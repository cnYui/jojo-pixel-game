"""序章牢房探索验收（2026-10-09 用户：抢漫画卡死；别那么快进荷莉来接的剧情，让玩家在牢房里好好探索）。

真实键盘：进序章 → 牢房自由走动 → 对每个调查点依次按 E / U / J（对白用 Enter 推进）→ 每样截一张图，
记“已调查”数和剧情报错 → 最后走到床前按 E（躺下）→ 确认荷莉来接的剧情开始（拍到小指特写为止）。
--quick：只按 E，不按 U / J。
用法：python -B tools\\dev\\full\\test_jail_explore.py --out tools\\_playtest\\jail_explore
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

PROBE = """() => { const W = G.world, p = W.player, S = G.S, st = W.stage;
  return { stage: st && st.id, free: !!W.free, busy: !!S.busy, insert: !!W.insert, x: p && p.x, y: p && p.y,
    seen: Object.keys(G.flags.jailSeen || {}), ready: !!G.flags.jailReady, grabbed: !!G.flags.grabbed,
    dlg: !!(G.ui && G.ui.dlg), mark: G.dbg && G.dbg.shot, ins: W.insert ? (W.insert.tag || null) : null,
    hots: st ? st.hotspots.map(h => [h.id, h.x, h.y, !!h.use, !!h.look, !!h.onStand]) : [],
    errs: (G.dbg && G.dbg.events ? G.dbg.events.filter(e => /error/.test(e.type)).map(e => e.type + ':' + (e.msg || e.name || '')) : []) }; }"""


class Explorer:
    def __init__(self, page, t, out):
        self.page, self.t, self.out = page, t, out

    def q(self):
        return self.page.evaluate(PROBE)

    def settle(self, limit=12.0):
        """推进对白 / 等剧情跑完，直到能自由走动。"""
        t0 = time.monotonic()
        while time.monotonic() - t0 < limit:
            q = self.q()
            if q['free'] and not q['busy'] and not q['dlg']:
                return q
            if q['ready'] and not q['busy']:
                return q                     # 已经要进荷莉来接的剧情：别替后面的剧情按 Enter
            if q['dlg']:
                if q['ready'] and q['seen'] and self.q().get('ins') is None and self._visitors_started():
                    return q
                self.t.pulse('Enter')
            self.page.wait_for_timeout(180)
        return self.q()

    def _visitors_started(self):
        return bool(self.page.evaluate("() => !!(G.world.stage && G.world.stage.find && G.world.stage.find('holly'))"))

    def walk_to(self, x, y, tol=3.0, limit=8.0):
        t0 = time.monotonic()
        while time.monotonic() - t0 < limit:
            q = self.q()
            dx, dy = x - q['x'], y - q['y']
            if abs(dx) <= tol and abs(dy) <= tol * 0.8:
                self.t.hold([])
                return True
            keys = []
            if abs(dx) > tol:
                keys.append('ArrowRight' if dx > 0 else 'ArrowLeft')
            if abs(dy) > tol * 0.8:
                keys.append('ArrowDown' if dy > 0 else 'ArrowUp')
            self.t.hold(keys)
            self.page.wait_for_timeout(40)
        self.t.hold([])
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=playtest.GAME / 'tools' / '_playtest' / 'jail_explore')
    ap.add_argument('--quick', action='store_true')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    targs = playtest.parser().parse_args(['prologue', '--timeout', '600'])
    from playwright.sync_api import sync_playwright
    errors, steps = [], []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        page = b.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
        t = playtest.Tester(page, targs, a.out)
        page.on('console', lambda m: errors.append({'console': m.type, 'text': m.text[:400]}) if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append({'pageerror': str(e)[:400]}))
        page.goto((playtest.GAME / 'index.html').as_uri() + '?autotest=1', wait_until='load')
        if not t.enter():
            print('enter failed')
            return 2
        ex = Explorer(page, t, a.out)
        t0 = time.monotonic()
        while time.monotonic() - t0 < 120:
            s = t.st()
            if s.get('stage') == 'jail_pro' and s.get('free') and not s.get('busy') and not s.get('dlg'):
                break
            if not t.advance(s):
                page.wait_for_timeout(100)
        q = ex.q()
        order = ['police_talk', 'pipe_look', 'tally', 'magazines', 'bulb', 'poster', 'bars', 'window', 'radio', 'cans']
        hot = {h[0]: h for h in q['hots']}
        for hid in order:
            h = hot.get(hid)
            if not h:
                steps.append({'id': hid, 'missing': True})
                continue
            for key in (['e'] if a.quick else ['e', 'u', 'j']):
                if key == 'e' and not h[3]:
                    continue
                if key == 'u' and not h[4]:
                    continue
                if key == 'j' and not h[5]:
                    continue
                ok = ex.walk_to(h[1], h[2])
                q0 = ex.q()
                if q0['ready']:
                    break
                t.pulse(key)
                page.wait_for_timeout(650)
                t.shot(f'{hid}_{key}')
                q1 = ex.settle()
                steps.append({'id': hid, 'key': key, 'arrived': ok, 'seen': len(q1['seen']), 'ready': q1['ready'], 'free_after': q1['free']})
                if q1['ready']:
                    break
            if ex.q()['ready']:
                break
        q = ex.q()
        before_bed = {'seen': q['seen'], 'ready': q['ready'], 'grabbed': q['grabbed']}
        if not q['ready']:
            bed = hot.get('bunk')
            ex.walk_to(bed[1], bed[2])
            t.pulse('e')
            page.wait_for_timeout(600)
            t.shot('bunk_e')
        # 荷莉来接：一直推进到小指特写（插入画面一出现就连拍三张：伸手 / 捏 / 小指落下）
        t1 = time.monotonic()
        pinky, trans, last = False, [], None
        while time.monotonic() - t1 < 90:
            q = ex.q()
            key = (q['insert'], q['mark'], q.get('ins'))
            if key != last:
                trans.append({'t': round(time.monotonic() - t1, 2), 'insert': q['insert'], 'mark': q['mark'], 'ins': q.get('ins')})
                last = key
            if q.get('ins') == 'pinky':
                pinky = True
                for i, ms in enumerate((200, 420, 420)):
                    page.wait_for_timeout(ms)
                    t.shot(f'pinky_insert_{i}')
                break
            if q['dlg']:
                t.pulse('Enter')
                page.wait_for_timeout(120)
            else:
                page.wait_for_timeout(50)
        steps.append({'visitor_transitions': trans})
        q = ex.q()
        res = {'ok': pinky and not errors and not q['errs'], 'pinky_reached': pinky, 'before_bed': before_bed, 'steps': steps,
               'script_errors': q['errs'], 'page_errors': errors, 'shots': t.shots}
        (a.out / 'result.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
        print(json.dumps({k: res[k] for k in ('ok', 'pinky_reached', 'before_bed', 'script_errors')}, ensure_ascii=False))
        print('page errors:', json.dumps(errors, ensure_ascii=False)[:800])
        b.close()
    return 0 if res['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
