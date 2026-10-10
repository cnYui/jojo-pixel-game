"""用真实入口核验返回标题后的等待取消和资源释放。"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / '_out'

PREP = """async () => {
  await G.goTitle(); G.cancelRun(); G.ui.reset();
  G.input.clear(); G.flags = {};
  window.__oldResult = 'pending'; window.__oldUntil = false;
  window.__oldVideo = null;
  G.dbg.missingHead.clear(); G.dbg.missingGlyph.clear();
}"""

CASES = {
    'wait_world': "S.wait(30)",
    'wait_ui': "S.wait(30, 'ui')",
    'until': "S.until(() => window.__oldUntil)",
    'say': "S.say('jotaro', '这一段对白应在返回标题时取消。')",
    'narrate': "S.narrate('这一段旁白应在返回标题时取消。')",
    'choice': "S.choice(['继续旧剧情', '离开旧剧情'], '取消回归')",
    'notice': "S.notice({ title: '取消回归', text: '这一段系统框应取消。' })",
    'menu': "G.ui.openMenu('旧菜单', ['继续', '返回'])",
    'qte': "S.mash({ need: 999, time: 120 })",
    'fade': "S.fadeOut(30)",
    'animate': "S.animate(30, () => {})",
    'zoom': "S.zoom(3, 140, 100, 30)",
    'video': "S.video('op', { skip: false })",
}


def main():
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    errors, rows = [], []
    started = time.monotonic()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        page.on('console', lambda m: errors.append({'type': m.type, 'text': m.text}) if m.type in ('warning', 'error') else None)
        page.on('pageerror', lambda e: errors.append({'type': 'pageerror', 'text': str(e)}))
        page.goto((GAME / 'index.html').as_uri() + '?autotest=1&touch=0')
        page.wait_for_function('G.booted && G.ui.menu', timeout=30000)
        page.evaluate(PREP)
        r = page.evaluate("""async () => {
          let cleanup = 0;
          const value = await G.runPromise(resolve => { resolve('settled'); return () => cleanup++; });
          G.cancelRun(); G.cancelRun();
          return { value, cleanup };
        }""")
        rows.append({'name': '同步 resolve 后 cleanup 恰好一次', 'ok': r == {'value': 'settled', 'cleanup': 1}, 'detail': r})
        r = page.evaluate("""async () => {
          let cleanup = 0;
          const promise = G.runPromise(() => () => cleanup++).catch(e => e.name);
          G.cancelRun(); G.cancelRun();
          return { result: await promise, cleanup };
        }""")
        rows.append({'name': '连续取消 cleanup 恰好一次', 'ok': r == {'result': 'RunCancelled', 'cleanup': 1}, 'detail': r})
        for name, expression in CASES.items():
            page.evaluate(PREP)
            page.evaluate("""(expression) => {
              const create = document.createElement.bind(document);
              document.createElement = (...args) => {
                const element = create(...args);
                if (String(args[0]).toLowerCase() === 'video') window.__oldVideo = element;
                return element;
              };
              const start = new Function('S', 'return ' + expression);
              G.S.run(async S => { await start(S); G.flags.oldChain = true; })
                .then(() => window.__oldResult = 'resolved', e => window.__oldResult = e.name);
              document.createElement = create;
            }""", expression)
            page.wait_for_timeout(80)
            pending = page.evaluate("() => window.__oldResult === 'pending'")
            page.evaluate("""async () => {
              await G.goTitle();
              G.flags.newScene = true; window.__oldUntil = true;
            }""")
            page.wait_for_timeout(130)
            r = page.evaluate("""() => ({ result: window.__oldResult, scene: G.scene.name,
              flags: G.flags, busy: G.S.busy, dlg: !!G.ui.dlg, choice: !!G.ui.choiceBox,
              narr: !!G.ui.narr, qte: !!G.ui.qte, notice: !!G.ui.noticeBox,
              fade: G.fadeA, zoom: G.cam.zoom, an: G.world.anims.length,
              video: window.__oldVideo && { paused: window.__oldVideo.paused,
                src: window.__oldVideo.getAttribute('src') } })""")
            ok = pending and r['result'] == 'RunCancelled' and r['scene'] == 'title' and r['flags'] == {'newScene': True}
            ok = ok and not any(r[k] for k in ('busy', 'dlg', 'choice', 'narr', 'qte', 'notice', 'fade', 'zoom', 'an'))
            if name == 'video':
                ok = ok and r['video'] == {'paused': True, 'src': None}
            rows.append({'name': name + ' 返回标题取消旧 await 链', 'ok': bool(ok), 'detail': {'pending': pending, **r}})
            print(('通过 ' if ok else '失败 ') + rows[-1]['name'], flush=True)
        page.evaluate(PREP)
        page.evaluate("""() => {
          G.defer(.22, () => G.flags.oldDefer = true, 'ui');
          G.defer(.22, () => G.flags.oldWorldDefer = true);
        }""")
        page.wait_for_timeout(60)
        page.evaluate("async () => { await G.goTitle(); G.flags.newScene = true; }")
        page.wait_for_timeout(350)
        r = page.evaluate('() => ({ scene: G.scene.name, flags: G.flags })')
        rows.append({'name': '旧 defer 不落入新场景', 'ok': r == {'scene': 'title', 'flags': {'newScene': True}}, 'detail': r})
        page.screenshot(path=str(OUT / 'cancel_title.png'))
        missing = page.evaluate("() => ({ image: [...G.dbg.missingImg], head: [...G.dbg.missingHead], glyph: [...G.dbg.missingGlyph] })")
        rows.append({'name': '取消测试资源完整', 'ok': not any(missing.values()), 'detail': missing})
        rows.append({'name': '控制台 warning/error/pageerror 为零', 'ok': not errors, 'detail': errors})
        browser.close()
    result = {'ok': all(row['ok'] for row in rows), 'checks': len(rows), 'results': rows,
              'console': errors, 'seconds': round(time.monotonic() - started, 2)}
    (OUT / 'test_cancel.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': result['ok'], 'checks': len(rows), 'failed': [r['name'] for r in rows if not r['ok']], 'seconds': result['seconds']}, ensure_ascii=False))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
