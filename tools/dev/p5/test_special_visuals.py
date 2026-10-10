"""正式入口的键盘、触屏大招与画布验收，固定时钟便于复核特效。"""
import argparse
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
GAME = HERE.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)

PIXELS = """() => {
  const data = G.wg.getImageData(0, 0, G.W, G.H).data;
  let visible = 0, changed = 0;
  const colours = new Set(), prev = window.__visualPixels;
  for (let i = 0; i < data.length; i += 4) {
    if (data[i] + data[i + 1] + data[i + 2] > 24 && data[i + 3]) visible++;
    colours.add((data[i] << 16) | (data[i + 1] << 8) | data[i + 2]);
    if (prev && (prev[i] !== data[i] || prev[i + 1] !== data[i + 1] || prev[i + 2] !== data[i + 2])) changed++;
  }
  window.__visualPixels = Array.from(data);
  return { visible, colours: colours.size, changed };
}"""


def step(page, frames=1):
    page.evaluate('(n) => Specials.step(n)', frames)


def wait_frames(page, condition, limit=180):
    for _ in range(limit):
        if page.evaluate(condition):
            return
        step(page)
    raise AssertionError('等待大招阶段超时：' + condition)


def capture(page, prefix, label):
    page.evaluate('G.render()')
    pixels = page.evaluate(PIXELS)
    page.screenshot(path=str(args.out / (prefix + '_' + label + '.png')))
    return pixels


results, errors = [], []
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for mode, options in [
        ('desktop', {'viewport': {'width': 1280, 'height': 720}}),
        ('mobile', {'viewport': {'width': 844, 'height': 390},
                    'device_scale_factor': 3, 'is_mobile': True, 'has_touch': True}),
    ]:
        context = browser.new_context(**options)
        page = context.new_page()
        # pageerror 存完整调用栈（以前只存消息，“reading 'draw'”查不到是哪个文件抛的）
        page.on('pageerror', lambda e, m=mode: errors.append({'mode': m, 'msg': str(e), 'stack': getattr(e, 'stack', None)}))
        page.on('console', lambda m, md=mode: errors.append({'mode': md, 'msg': m.text}) if m.type in ('warning', 'error') else None)
        page.goto((GAME / 'index.html').as_uri() + ('?touch=1' if mode == 'mobile' else '?touch=0'))
        page.wait_for_function('window.G && G.booted')
        page.evaluate('G.dbg.hold = true; G.cancelRun(); G.ui.reset(); G.world.insert = null')
        page.add_script_tag(path=str(HERE / 'specials.js'))
        page.evaluate('Specials.init()')
        page.evaluate("G.res.loadPack('bg_ch1')")
        page.evaluate("""G.setScene({
          name: 'world',
          update(dt, advancing, wdt) { G.ui.update(dt); if (advancing) G.world.update(wdt); },
          drawWorld: g => G.world.draw(g), drawUI: g => G.ui.draw(g), drawTop: g => G.ui.drawTop(g),
          hasPixel: () => G.world.hasPixel(), drawPixel: (P, layer) => G.world.drawPixel(P, layer),
          hasOver: () => G.world.hasOver(), drawOver: g => G.world.drawOver(g)
        })""")
        for cid, frames in [('jotaro', 38), ('kakyoin', 10), ('avdol', 0),
                            ('polnareff', 18), ('joseph', 8), ('iggy', 26)]:
            page.evaluate("""cid => {
              G.ui.reset(); G.world.insert = null;
              Specials.reset(cid, { dx: cid === 'iggy' ? 70 : 100, dy: -12, facing: -1 });
              G.world.player.energy = 100; G.hud.on = true;
              window.__visualPixels = null;
            }""", cid)
            if mode == 'mobile':
                page.wait_for_function("G.touch.ctx === 'combat' && document.querySelector('.tc-u').classList.contains('ready')")
                button = page.locator('.tc-u').bounding_box()
                page.touchscreen.tap(button['x'] + button['width'] / 2, button['y'] + button['height'] / 2)
            else:
                page.keyboard.press('u')
            step(page)
            wait_frames(page, "G.world.cine && G.world.cine.by === 'special-run'")
            if cid == 'avdol':
                wait_frames(page, "G.world.shots.some(s => s.kind === 'ankh' && !s.dead)")
                frames = 6
            step(page, frames)
            prefix = mode + '_' + cid
            first = capture(page, prefix, 'active')
            step(page, 8)
            second = capture(page, prefix, 'active2')
            explosion = None
            if cid == 'avdol':
                wait_frames(page, "G.fx.list.some(e => e.name === 'fire_burst' && !G.fx.expired(e))")
                step(page, 34)
                explosion = capture(page, prefix, 'explosion')
            step(page, 360)
            result = page.evaluate("""() => ({
              damage: Specials.snap().damage, energy: G.world.player.energy,
              idle: G.world.player.state === 'idle', cine: !!G.world.cine,
              shots: G.world.shots.length,
              missing: [...G.dbg.missingImg],
              errors: G.dbg.events.filter(e => /error|unknown/.test(e.type)),
              canvas: (() => { const r = G.screen.getBoundingClientRect();
                return { x: r.x, y: r.y, w: r.width, h: r.height,
                  fits: r.left >= -1 && r.top >= -1 && r.right <= innerWidth + 1 && r.bottom <= innerHeight + 1 }; })()
            })""")
            result.update(mode=mode, cid=cid, first=first, second=second, explosion=explosion)
            result['ok'] = (result['damage'] > 0 and result['energy'] == 0 and result['idle']
                            and not result['cine'] and not result['shots'] and not result['missing']
                            and not result['errors'] and result['canvas']['fits']
                            and first['visible'] > 5000 and first['colours'] > 20
                            and second['changed'] > 5)
            results.append(result)
            # 终端只打摘要（同一条错误每帧都记，整段 JSON 会刷几百 KB）；完整内容在 report.json
            uniq = sorted({(e.get('where'), e.get('msg')) for e in result['errors']}, key=str)
            brief = dict(damage=result['damage'], energy=result['energy'], idle=result['idle'], cine=result['cine'],
                         shots=result['shots'], missing=result['missing'], errors=[f'{w}: {m} ×{sum(1 for e in result["errors"] if (e.get("where"), e.get("msg")) == (w, m))}' for w, m in uniq],
                         fits=result['canvas']['fits'], visible=first['visible'], colours=first['colours'], changed=second['changed'])
            print(mode, cid, '通过' if result['ok'] else '失败 ' + json.dumps(brief, ensure_ascii=False), flush=True)
        context.close()
    browser.close()

report = {'ok': all(r['ok'] for r in results) and not errors, 'results': results, 'errors': errors}
(args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
for e in errors[:3]:
    print('页面错误', e.get('mode'), e.get('msg'))
    if e.get('stack'):
        print(e['stack'][:1200])
print(f"{sum(r['ok'] for r in results)}/{len(results)} 通过；页面错误 {len(errors)}", flush=True)
sys.exit(0 if report['ok'] else 1)
