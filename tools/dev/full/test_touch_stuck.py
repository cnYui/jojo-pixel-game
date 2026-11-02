r"""触屏方向盘“卡在一个方向”回归（2026-11-02）。

    python -B tools\dev\full\test_touch_stuck.py [--out tools\_playtest\touch_stuck]

真机上手指的抬起事件可能丢（iOS 边缘手势、通知 / 控制中心、来电、切应用、微信等内置浏览器），
以前方向盘的 padId 会一直留着、方向一直按着，之后的触摸全被忽略。这里用 CDP Input.dispatchTouchEvent
发真实触摸（?touch=1 + hasTouch），在标题画面上按方向盘，逐项模拟“抬起丢失”：
  A. 第一根手指不抬起，第二根手指按方向盘向左 → 右松开、左按下（新手指不再被忽略）
  B. 按住向右时窗口 blur → 右松开、方向盘复位；之后新手指向左能用
  C. 按住向右时 visibilitychange(hidden) → 同上
  D. 按住向右时 G.input.clear() → 触屏层也复位（.on / 箭头高亮 / 摇杆位置）
  E. 按住 J 时 blur → attack 松开、按钮 .on 去掉；再按 J 能重新算一次按下
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

GAME = Path(__file__).resolve().parents[3]
UA = ('Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/126.0.0.0 Mobile Safari/537.36')

STATE_JS = '''() => {
  const pad = document.getElementById('tc-pad'), knob = document.getElementById('tc-knob');
  const arr = [...pad.querySelectorAll('.arr.on')].map(n => n.dataset.d);
  const j = document.querySelector('#tc .tc-e');
  const d = G.input.down;
  return { right: !!d.right, left: !!d.left, up: !!d.up, down: !!d.down, attack: !!d.ok,
           padOn: pad.classList.contains('on'), knob: knob.style.transform || '', arrows: arr,
           jOn: !!(j && j.classList.contains('on')), touch: !!(G.touch && G.touch.on) };
}'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(GAME / 'tools' / '_playtest' / 'touch_stuck'))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    url = (GAME / 'index.html').as_uri() + '?autotest=1&touch=1'
    errors, checks = [], []

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        ctx = browser.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, is_mobile=True,
                                  has_touch=True, user_agent=UA)
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append({'kind': 'pageerror', 'text': str(e)}))
        page.on('console', lambda m: errors.append({'kind': 'console_error', 'text': m.text}) if m.type == 'error' else None)
        cdp = ctx.new_cdp_session(page)

        page.goto(url, wait_until='load')
        page.wait_for_function('() => G.booted && G.ui.menu && G.touch && G.touch.on', timeout=60000)
        page.wait_for_timeout(800)
        box = page.locator('#tc-pad').bounding_box()
        cx, cy, R = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2, box['width'] / 2
        RIGHT = (cx + R * 0.8, cy)
        LEFT = (cx - R * 0.8, cy)
        jb = page.locator('#tc .tc-e').bounding_box()
        J = (jb['x'] + jb['width'] / 2, jb['y'] + jb['height'] / 2)

        def touch(kind, pts):
            # CDP 的 touchPoints 是“当前所有按着的点”；和上一次相比多出来的点算按下，少了的算抬起
            cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [
                {'x': x, 'y': y, 'id': i, 'radiusX': 4, 'radiusY': 4, 'force': 1} for i, (x, y) in pts]})
            page.wait_for_timeout(200)          # 等几个逻辑步，让 pending 落进 G.input.down

        def st():
            return page.evaluate(STATE_JS)

        def check(name, cond, s):
            checks.append({'name': name, 'ok': bool(cond), 'state': s})
            print(('PASS ' if cond else 'FAIL ') + name, json.dumps(s, ensure_ascii=False))

        def released(s):
            return not (s['right'] or s['left'] or s['up'] or s['down']) and not s['padOn'] and not s['arrows'] and s['knob'] in ('', 'none')

        # A. 第一根手指的抬起丢了（不发），第二根手指按方向盘：应接管，不再被忽略
        touch('touchStart', [(1, RIGHT)])
        s = st(); check('A1 按住右：down.right', s['right'] and s['padOn'], s)
        touch('touchStart', [(1, RIGHT), (2, LEFT)])
        s = st(); check('A2 新手指向左：right 松开、left 按下', (not s['right']) and s['left'], s)
        touch('touchEnd', [])
        s = st(); check('A3 全部抬起：方向盘复位', released(s), s)

        # B. 按住时窗口 blur（切应用 / 来电）
        touch('touchStart', [(1, RIGHT)])
        s = st(); check('B1 按住右', s['right'], s)
        page.evaluate('() => window.dispatchEvent(new Event("blur"))')
        page.wait_for_timeout(200)
        s = st(); check('B2 blur 后：down.right 变 false、方向盘复位', released(s), s)
        touch('touchEnd', [])
        touch('touchStart', [(3, LEFT)])
        s = st(); check('B3 新手指向左：down.left 为 true', s['left'] and not s['right'], s)
        touch('touchEnd', [])

        # C. 按住时页面变 hidden（锁屏 / 控制中心 / 切后台）
        touch('touchStart', [(1, RIGHT)])
        page.evaluate('''() => {
          Object.defineProperty(document, 'hidden', { configurable: true, get: () => true });
          document.dispatchEvent(new Event('visibilitychange'));
          delete document.hidden;           // 恢复原型上的只读属性
        }''')
        page.wait_for_timeout(200)
        s = st(); check('C1 visibilitychange(hidden) 后：方向盘复位', released(s), s)
        touch('touchEnd', [])
        touch('touchStart', [(4, LEFT)])
        s = st(); check('C2 新手指向左：down.left 为 true', s['left'], s)
        touch('touchEnd', [])

        # D. 按住时 G.input.clear()：触屏层也要复位，不再和 input.js 不一致
        touch('touchStart', [(1, RIGHT)])
        s = st(); check('D1 按住右', s['right'] and s['padOn'], s)
        page.evaluate('() => G.input.clear()')
        page.wait_for_timeout(200)
        s = st(); check('D2 clear 后：down 清空、padOn / 箭头 / 摇杆复位', released(s), s)
        touch('touchEnd', [])
        touch('touchStart', [(5, LEFT)])
        s = st(); check('D3 新手指向左：down.left 为 true', s['left'], s)
        touch('touchEnd', [])

        # E. 按钮（标题画面 J 是藏着的，用 E；按钮逻辑同一份）：按住时 blur → 松开；再按仍然算新的一下
        # 先锁住确认：否则 E 会选中“从序章开始”，开新游戏时 main.js 调 G.input.clear() 把按钮一并复位，测不到 blur
        page.evaluate('() => G.input.lockOk(60)')
        touch('touchStart', [(6, J)])
        s = st(); check('E1 按住 E：down.ok', s['attack'] and s['jOn'], s)
        page.evaluate('() => window.dispatchEvent(new Event("blur"))')
        page.wait_for_timeout(200)
        s = st(); check('E2 blur 后：ok 松开、E 的 .on 去掉', (not s['attack']) and not s['jOn'], s)
        touch('touchEnd', [])
        touch('touchStart', [(7, J)])
        s = st(); check('E3 再按 E：down.ok', s['attack'] and s['jOn'], s)
        touch('touchEnd', [])
        s = st(); check('E4 抬起 E', (not s['attack']) and not s['jOn'], s)

        page.screenshot(path=str(out / 'final.png'))
        browser.close()

    fails = [c['name'] for c in checks if not c['ok']]
    res = {'url': url, 'checks': checks, 'errors': errors}
    (out / 'result.json').write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'pass': len(checks) - len(fails), 'total': len(checks), 'fails': fails, 'errors': len(errors)}, ensure_ascii=False))
    return 0 if not fails and not errors else 1


if __name__ == '__main__':
    sys.exit(main())
