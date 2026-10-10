"""复现 / 回归：序章牢房里抢狱警的漫画（用户 2026-10-09：抢完突然卡死、什么也做不了）。

真实键盘：进序章 → 牢房自由走动 → 走到左边、面朝狱警按 J（或 --via bars：对铁栏按 E 调查）
→ 之后 12 s 每 0.25 s 记一次 busy / free / 对白 / 剧情报错；能移动就算没卡死。
用法：python -B tools\\dev\\full\\repro_jail_grab.py [--via j|bars|stand] --out tools\\_playtest\\repro_grab
"""
from pathlib import Path
import argparse
import json
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
import playtest

PROBE = """() => { const W = G.world, p = W.player, S = G.S;
  return { stage: W.stage && W.stage.id, free: !!W.free, busy: !!S.busy, x: p && Math.round(p.x), y: p && Math.round(p.y),
    facing: p && p.facing, standMode: p && p.stand ? p.stand.mode : null, standPose: p && p.stand ? p.stand.pose : null,
    dlg: G.ui && G.ui.dlg ? String(G.ui.dlg.text || '').slice(0, 30) : null, grabbed: !!G.flags.grabbed,
    errs: (G.dbg && G.dbg.events ? G.dbg.events.filter(e => /error/.test(e.type)).slice(-5) : []) }; }"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--via', default='j', choices=['j', 'bars', 'stand'])
    ap.add_argument('--out', type=Path, default=playtest.GAME / 'tools' / '_playtest' / 'repro_grab')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    targs = playtest.parser().parse_args(['prologue', '--timeout', '400'])
    from playwright.sync_api import sync_playwright
    log = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        page = b.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
        t = playtest.Tester(page, targs, a.out)
        page.on('console', lambda m: log.append({'console': m.type, 'text': m.text}) if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e: log.append({'pageerror': str(e), 'stack': getattr(e, 'stack', None)}))
        page.goto((playtest.GAME / 'index.html').as_uri() + '?autotest=1', wait_until='load')
        if not t.enter():
            print('enter failed'); return 2
        t0 = time.monotonic()
        while time.monotonic() - t0 < 120:                 # 跳过开场到牢房能走动
            s = t.st()
            if s.get('stage') == 'jail_pro' and s.get('free') and not s.get('busy') and not s.get('dlg'):
                break
            if not t.advance(s):
                page.wait_for_timeout(100)
        q = page.evaluate(PROBE)
        log.append({'free_in_jail': q})
        # 走到左边铁栏前（x 110 附近），面朝左
        t0 = time.monotonic()
        while time.monotonic() - t0 < 8:
            q = page.evaluate(PROBE)
            if q['x'] <= 112:
                break
            t.hold(['ArrowLeft'])
            page.wait_for_timeout(60)
        t.hold([])
        page.wait_for_timeout(200)
        t.shot('before_grab')
        if a.via == 'j':
            t.pulse('j')
        elif a.via == 'bars':
            t.hold(['ArrowRight']); page.wait_for_timeout(500); t.hold([])      # 铁栏调查点在 x 182 附近
            for _ in range(40):
                q = page.evaluate(PROBE)
                if q['x'] >= 176:
                    break
                t.hold(['ArrowRight']); page.wait_for_timeout(60)
            t.hold(['ArrowDown']); page.wait_for_timeout(400); t.hold([])
            t.pulse('e')
        else:
            t.pulse('j'); page.wait_for_timeout(120); t.pulse('j')
        stuck_since = None
        for i in range(48):
            page.wait_for_timeout(250)
            q = page.evaluate(PROBE)
            log.append({'t': round(i * 0.25, 2), **q})
            if q['dlg']:
                t.pulse('Enter')                            # 对白用 E / Enter 推进（J 不推进）
            if i == 8:
                t.shot('during_grab')
        t.shot('after_grab')
        q = page.evaluate(PROBE)
        x0 = q['x']
        t.hold(['ArrowRight']); page.wait_for_timeout(700); t.hold([])
        q2 = page.evaluate(PROBE)
        moved = q2['x'] != x0
        res = {'via': a.via, 'moved_after': moved, 'final': q2, 'grabbed': q2['grabbed'],
               'errors': [e for e in log if 'pageerror' in e or e.get('console') == 'error'], 'log': log}
        (a.out / 'repro.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
        print(json.dumps({k: res[k] for k in ('via', 'moved_after', 'grabbed', 'final')}, ensure_ascii=False))
        print('errors:', json.dumps(res['errors'], ensure_ascii=False)[:1500])
        b.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
