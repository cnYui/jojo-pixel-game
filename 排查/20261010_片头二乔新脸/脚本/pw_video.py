"""In-game check: index.html?autotest=1 -> 从序章开始 -> op video scene plays (webm) -> screenshot Joseph moments -> coffin -> story."""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
GAME = Path(r'D:\大疆\游戏素材\JoJo\游戏')
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
SNAP = "() => { const s = G.dbg.snapshot(); return { scene: G.scene && G.scene.name, menuItems: s.menuItems }; }"
HOOK = """
window.__vids = [];
const _ce = document.createElement.bind(document);
document.createElement = function (tag, ...r) { const el = _ce(tag, ...r); if (String(tag).toLowerCase() === 'video') window.__vids.push(el); return el; };
"""
from playwright.sync_api import sync_playwright
errors, log = [], []
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
    page = browser.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
    page.add_init_script(HOOK)
    page.on('console', lambda m: errors.append({'kind': 'console_' + m.type, 'text': m.text}) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: errors.append({'kind': 'pageerror', 'text': str(e)}))

    def key(k, wait=90):
        page.keyboard.down(k); page.wait_for_timeout(40); page.keyboard.up(k); page.wait_for_timeout(wait)

    page.goto((GAME / 'index.html').as_uri() + '?autotest=1', wait_until='load')
    page.evaluate('() => { try { localStorage.removeItem("jojo-progress"); } catch (e) {} }')
    page.reload(wait_until='load')
    page.wait_for_function('() => G.booted && G.ui.menu', timeout=60000)
    page.wait_for_timeout(600)
    items = page.evaluate(SNAP)['menuItems']
    log.append(('menu', items))
    hit = [i for i, v in enumerate(items) if '从序章开始' in (v or '')][0]
    idx = page.evaluate('() => G.ui.menu ? G.ui.menu.idx : 0') or 0
    for _ in range(abs(hit - idx)):
        key('ArrowDown' if hit > idx else 'ArrowUp', 70)
    key('Enter', 200)
    page.wait_for_function('() => G.scene && G.scene.name === "video" && window.__vids.length >= 1', timeout=30000)
    info = page.evaluate('() => { const v = window.__vids[0]; return { src: v.currentSrc || v.src, dur: v.duration, rs: v.readyState }; }')
    log.append(('op', info))

    def grab(vi, t, name):
        page.wait_for_function(f'() => window.__vids[{vi}] && window.__vids[{vi}].currentTime >= {t}', timeout=30000, polling=10)
        page.evaluate(f'() => window.__vids[{vi}].pause()')
        page.wait_for_timeout(250)
        ct = page.evaluate(f'() => window.__vids[{vi}].currentTime')
        p = OUT / f'{name}_t{ct:.2f}.png'
        page.screenshot(path=str(p))
        page.evaluate(f'() => window.__vids[{vi}].play()')
        log.append((name, round(ct, 3), str(p), page.evaluate(SNAP)['scene']))

    grab(0, 5.20, 'op_joseph_card')
    grab(0, 12.05, 'op_finale')
    page.wait_for_function('() => window.__vids.length >= 2 && G.scene && G.scene.name === "video"', timeout=30000)
    info2 = page.evaluate('() => { const v = window.__vids[1]; return { src: v.currentSrc || v.src, dur: v.duration }; }')
    log.append(('coffin', info2))
    grab(1, 5.0, 'coffin_mid')
    page.wait_for_function('() => G.scene && G.scene.name !== "video"', timeout=30000)
    page.wait_for_timeout(1500)
    log.append(('after_videos', page.evaluate(SNAP)['scene']))
    page.screenshot(path=str(OUT / 'after_videos.png'))
    browser.close()
for l in log:
    print(l)
print('errors:', json.dumps(errors, ensure_ascii=False)[:2000])
