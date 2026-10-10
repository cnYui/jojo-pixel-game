r"""触屏布局快速看一眼（手机横屏模拟，不是真机）：标题、片头跳过、牢房自由走动时的虚拟按键，再拍一张竖屏提示。

    python -B tools\dev\full\test_touch_layout.py [--demo] [--out tools\_playtest\touch_check]

Playwright 的 Chromium 模拟 844×390 横屏、触屏、移动端；操作全用点虚拟按键 / 点屏幕。
只看布局（按键有没有挡住对白框、提示、血条），真机的手感和声音还是要用户拿手机试。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

GAME = Path(__file__).resolve().parents[3]
UA = ('Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/126.0.0.0 Mobile Safari/537.36')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--demo', action='store_true', help='网址加 ?demo=1')
    ap.add_argument('--out', default=str(GAME / 'tools' / '_playtest' / 'touch_check'))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    url = (GAME / 'index.html').as_uri() + '?autotest=1' + ('&demo=1' if a.demo else '')
    errors, shots, notes = [], [], {}

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        ctx = browser.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, is_mobile=True,
                                  has_touch=True, user_agent=UA)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append({'kind': 'console_' + m.type, 'text': m.text}) if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e: errors.append({'kind': 'pageerror', 'text': str(e)}))

        def shot(name):
            p = out / f'{len(shots) + 1:02d}_{name}.png'
            page.screenshot(path=str(p))
            shots.append(str(p))

        def snap():
            return page.evaluate('() => { const s = G.dbg.snapshot(); return { scene: s.scene, stage: s.stage, free: s.free, dlg: s.dlg, menu: s.menu, touch: !!(G.touch && G.touch.on) }; }')

        def tap_btn(sel, wait=250):
            # 过场（视频、篇章卡）时虚拟按键是藏着的：看得见就点按键，看不见就点屏幕中间（等于确认）
            loc = page.locator(sel)
            box = loc.bounding_box() if loc.count() and loc.is_visible() else None
            if box:
                page.touchscreen.tap(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
            else:
                page.touchscreen.tap(422, 195)
            page.wait_for_timeout(wait)

        page.goto(url, wait_until='load')
        page.evaluate('() => { try { localStorage.removeItem("jojo-progress"); } catch (e) {} }')
        page.reload(wait_until='load')
        page.wait_for_function('() => G.booted && G.ui.menu', timeout=60000)
        page.wait_for_timeout(800)
        s = snap()
        notes['title'] = s
        shot('title')
        # 标题菜单第一项「从序章开始」：点 E（确认）
        tap_btn('.tc-e', 600)
        # 片头 op、序幕 coffin：点屏幕跳过（0.6 s 后才认）
        for name in ('op', 'coffin'):
            page.wait_for_function('() => G.scene && G.scene.name === "video"', timeout=20000)
            page.wait_for_timeout(1500)
            if name == 'op':
                shot('video_op')
            page.touchscreen.tap(422, 195)
            page.wait_for_function('() => !(G.scene && G.scene.name === "video") || true', timeout=5000)
            page.wait_for_timeout(700)
        # 篇章卡、开场对白：一直点 E，直到能自由走动（最多 60 s）
        for _ in range(240):
            s = snap()
            if s.get('free') and s.get('stage') == 'jail_pro' and not s.get('dlg'):
                break
            if s.get('dlg') and not notes.get('dlg_shot'):
                notes['dlg_shot'] = True
                shot('dialog')
            tap_btn('.tc-e', 250)
        s = snap()
        notes['jail'] = s
        page.wait_for_timeout(600)
        shot('jail_free')
        notes['pad_box'] = page.locator('#tc-pad').bounding_box()
        notes['btns_box'] = page.locator('#tc-btns').bounding_box()
        page.set_viewport_size({'width': 390, 'height': 844})
        page.wait_for_timeout(800)
        shot('portrait_rotate_hint')
        browser.close()

    res = {'url': url, 'notes': notes, 'errors': errors, 'shots': shots}
    (out / 'result.json').write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'errors': len(errors), 'touch_on': notes.get('title', {}).get('touch'), 'jail_free': notes.get('jail', {}).get('free'),
                      'out': str(out)}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
