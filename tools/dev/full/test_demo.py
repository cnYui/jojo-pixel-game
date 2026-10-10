r"""体验版（demo）开关的快速检查：标题曲、章节菜单只到第1章、打完第1章出「体验版到此结束」、回标题能「继续」。

    python -B tools\dev\full\test_demo.py                          # 开发目录，网址加 ?demo=1
    python -B tools\dev\full\test_demo.py --root <发布包文件夹>       # 打好的发布包（index.html 里已有 JOJO_DEMO）

菜单全用真实键盘；只有“打完第1章”这一步用开发钩子把第1章的剧情换成空函数（只测章末的体验版流程，不算通关证据——
整章路线另跑 test_ch1.py）。截图和结果在 tools\_playtest\demo_check\（或 --out）。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

GAME = Path(__file__).resolve().parents[3]
SNAP = "() => { const s = G.dbg.snapshot(); return { scene: s.scene, menu: s.menu, menuItems: s.menuItems, notice: s.notice," \
       " music: G.audio.name, demo: G.DEMO, max: G.progress.max, cur: G.curChapter }; }"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', help='发布包文件夹（不给 = 开发目录 + ?demo=1）')
    ap.add_argument('--out', default=str(GAME / 'tools' / '_playtest' / 'demo_check'))
    a = ap.parse_args()
    root = Path(a.root) if a.root else GAME
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    url = (root / 'index.html').as_uri() + ('?autotest=1' if a.root else '?autotest=1&demo=1')
    errors, checks, shots = [], [], []

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
        page.on('console', lambda m: errors.append({'kind': 'console_' + m.type, 'text': m.text}) if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e: errors.append({'kind': 'pageerror', 'text': str(e)}))

        def st():
            return page.evaluate(SNAP)

        def check(ok, what, **kw):
            checks.append({'ok': bool(ok), 'what': what, **kw})
            print(('ok  ' if ok else 'BAD ') + what + ('  ' + json.dumps(kw, ensure_ascii=False) if kw and not ok else ''), flush=True)

        def shot(name):
            p = out / f'{len(shots) + 1:02d}_{name}.png'
            page.screenshot(path=str(p))
            shots.append(str(p))

        def key(k, wait=90):
            page.keyboard.down(k); page.wait_for_timeout(40); page.keyboard.up(k); page.wait_for_timeout(wait)

        def dismiss_notice():
            # 提示框 0.6 s 以后才认确认键：等它能关再按，按完等它真的关掉
            page.wait_for_function('() => G.ui.noticeBox && G.ui.noticeBox.t >= 0.7', timeout=10000)
            key('Enter', 120)
            page.wait_for_function('() => !G.ui.noticeBox', timeout=10000)

        def pick(label):
            page.wait_for_timeout(150)
            s = st()
            items = s.get('menuItems') or []
            hit = [i for i, v in enumerate(items) if label in (v or '')]
            if not hit:
                check(False, 'menu_item_missing', label=label, items=items)
                return False
            idx = page.evaluate('() => G.ui.menu ? G.ui.menu.idx : 0') or 0
            for _ in range(abs(hit[0] - idx)):
                key('ArrowDown' if hit[0] > idx else 'ArrowUp', 70)
            key('Enter', 220)
            return True

        page.goto(url, wait_until='load')
        page.evaluate('() => { try { localStorage.removeItem("jojo-progress"); } catch (e) {} }')
        page.reload(wait_until='load')
        page.wait_for_function('() => G.booted && G.ui.menu', timeout=60000)
        page.wait_for_timeout(600)
        s = st()
        shot('title')
        check(s['demo'] and s['demo'].get('last') == 1, 'G.DEMO = { last: 1 }', demo=s['demo'])
        check(s['music'] == 'title', '标题曲是原工程的 title（不是 STAND PROUD）', music=s['music'])
        check('继续' not in (s['menuItems'] or []), '新存档没有「继续」', items=s['menuItems'])

        pick('操作说明')
        page.wait_for_timeout(500)
        s = st()
        shot('controls')
        check('操作说明' in (s['notice'] or ''), '操作说明能打开', notice=s['notice'])
        dismiss_notice()

        pick('选择章节')
        s = st()
        shot('chapter_menu')
        check((s['menuItems'] or []) == ['序章　东京', '第1章　香港', '返回'], '章节菜单只有序章 + 第1章', items=s['menuItems'])
        pick('返回')

        # 打完第1章：开发钩子把第1章剧情换成空函数，只看章末流程
        page.evaluate('() => { G.CHAPTERS[1].run = async () => {}; }')
        pick('选择章节')
        pick('第1章')
        page.wait_for_function('() => { const s = G.dbg.snapshot(); return !!s.notice; }', timeout=20000)
        page.wait_for_timeout(400)
        s = st()
        shot('demo_end')
        check('体验版到此结束' in (s['notice'] or ''), '第1章打完出「体验版到此结束」', notice=s['notice'])
        dismiss_notice()
        page.wait_for_function('() => G.scene && G.scene.name === "title" && G.ui.menu', timeout=20000)
        page.wait_for_timeout(500)
        s = st()
        shot('back_title')
        check(s['max'] == 1, '进度封顶在第1章', max=s['max'])
        check((s['menuItems'] or [])[:1] == ['继续'], '回标题有「继续」', items=s['menuItems'])
        r = page.evaluate('async () => { await G.playFrom(2); return G.scene.name; }')
        check(r == 'title', '体验版里进不了第2章', scene=r)
        browser.close()

    bad = [c for c in checks if not c['ok']]
    res = {'ok': not bad and not errors, 'url': url, 'checks': checks, 'errors': errors, 'shots': shots}
    (out / 'result.json').write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': res['ok'], 'bad': len(bad), 'errors': len(errors), 'out': str(out)}, ensure_ascii=False))
    return 0 if res['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
