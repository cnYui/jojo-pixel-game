"""连打循环音（ora_loop）孤儿回归：连打被防御 / 必杀 / 换队长 / 过场接管顶掉后，循环音必须停。

背景（2026-10-20 用户实机：第2章打完暗蓝之月后欧拉连打声一直响）：
a.rush.loop 只有 cancelRush / resetActor 会停，而 rushTick 只在 state==='rush' 且 updatePlayer 没提前 return 时才跑，
所以连打里按 L / U / Q 或被 cine 接管后，循环音没人管。修复是 combat.settleRush（world 每帧调）+ audio.stopLoops（reset 兜底）。

做法：借 G.DEV.ch2Darkmoon 开一场承太郎的战斗，冻住敌人、给玩家加血（只测连打，不测打架），用真实键盘进连打，
再各走一条“顶掉连打”的路径，等 1 秒断言 G.audio.loopCount() 回到基线、player.rush 为空。
--no-patch：把 settleRush 换成空函数，应当复现（用来证明这个测试真的抓得到 bug）。

用法：python -B tools\\dev\\full\\test_rush_loop.py [--no-patch] [--out tools\\_playtest\\rush_loop]
"""
from pathlib import Path
import argparse
import json
import sys
import time

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(GAME / 'tools'))
import playtest

SNAP = """() => { const p = G.world.player; return {
  combat: !!G.world.combat, cine: !!G.world.cine, state: p && p.state, rush: !!(p && p.rush), cid: p && p.cid,
  energy: p && p.energy, loops: G.audio.loopCount(), fight: G.world.fight ? G.world.fight.id : null }; }"""


class RushLoop(playtest.Tester):
    def snap(self):
        return self.page.evaluate(SNAP)

    def wait(self, ms):
        self.page.wait_for_timeout(ms)

    def to_combat(self):
        self.page.wait_for_function("() => G.booted && G.ui.menu && G.DEV && G.DEV.ch2Darkmoon", timeout=30000)
        self.page.evaluate("() => { G.CHAPTERS[2].run = G.DEV.ch2Darkmoon; }")
        if not (self.menu('选择章节') and self.menu('第2章')):
            return False
        t0 = time.monotonic()
        while time.monotonic() - t0 < 90:
            if self.snap()['combat']:
                break
            self.pulse('Enter')
            self.wait(400)
        else:
            return False
        # 只测连打：敌人冻住（stopT 每帧才减，给足）、玩家血量加大，免得被打断连打
        self.page.evaluate("""() => { G.world.enemies().forEach(e => { e.stopT = 9999; });
          const p = G.world.player; p.maxHp = p.hp = 99999; p.minHp = 1; }""")
        return True

    def enter_rush(self):
        """真实键盘：连点 J 走完三连，J3 之后继续按住 J 进连打。"""
        for _ in range(40):
            if self.snap()['rush']:
                return True
            self.pulse('j')
            self.wait(110)
        return self.snap()['rush']

    def calm(self):
        """把上一条路径留下的状态清掉：松开所有键、等动作结束、能量清零、连打冷却走完。"""
        self.hold()
        # 上一条路径若真的漏了（--no-patch 复现时），这里强行清掉，免得污染下一条的基线；每条用例的“漏没漏”在 case() 里量，不在这里
        self.page.evaluate("""() => { G.world.cine = null; G.audio.stopLoops(0.01);
          G.party.members.forEach(m => { if (m.rush) { m.rush = null; if (m.state === 'rush') m.state = 'idle'; } }); }""")
        self.wait(1800)

    def case(self, name, act):
        self.calm()
        base = self.snap()['loops']
        self.page.evaluate("() => { G.world.player.rushCdT = 0; G.world.player.energy = 100; }")
        if not self.enter_rush():
            self.check(False, 'cannot_enter_rush', case=name)
            return
        live = self.snap()
        # 测试自检：进连打时循环音必须登记上，否则后面的“回到基线”什么也证明不了
        self.check(live['loops'] == base + 1, 'loop_not_registered', case=name, base=base, live=live['loops'])
        act()
        self.wait(1000)
        end = self.snap()
        ok = end['loops'] == base and not end['rush'] and end['state'] != 'rush'
        self.check(ok, 'orphan_rush_loop', case=name, base=base, end=end)
        print(json.dumps({'case': name, 'ok': ok, 'base': base, 'live': live['loops'], 'end': end}, ensure_ascii=False), flush=True)

    def run(self):
        if not self.to_combat():
            self.check(False, 'cannot_reach_combat')
            return
        if self.args.no_patch:
            self.page.evaluate("() => { G.combat.settleRush = () => {}; }")

        # 对照：正常连打期间循环音在、松手后自己收尾（settleRush 不能误伤合法连打）
        self.calm()
        base = self.snap()['loops']
        self.page.evaluate("() => { G.world.player.rushCdT = 0; }")
        self.check(self.enter_rush(), 'cannot_enter_rush', case='normal')
        # 连打要靠不断按 J 续命（rushSustain 只有 12 帧），playwright 的 keydown 不会自动重复，所以每 100 ms 点一下
        for _ in range(6):
            self.pulse('j')
            self.wait(100)
        mid = self.snap()
        self.check(mid['rush'] and mid['loops'] == base + 1, 'normal_rush_killed', mid=mid)
        self.hold()
        self.wait(1500)
        end = self.snap()
        self.check(not end['rush'] and end['loops'] == base, 'normal_rush_not_ended', end=end)
        print(json.dumps({'case': 'normal', 'mid': mid, 'end': end}, ensure_ascii=False), flush=True)

        def guard():
            self.page.keyboard.down('l'); self.wait(350); self.page.keyboard.up('l')

        def special():
            self.page.evaluate("() => { G.world.player.energy = 100; }")
            self.pulse('u')
            # 必杀自己有切入 + 演出，等它走完再量
            t0 = time.monotonic()
            while time.monotonic() - t0 < 12:
                s = self.snap()
                if s['state'] != 'special' and not s['cine']:
                    break
                self.wait(200)

        def swap():
            # 战斗里队长键可能被 spec 锁住，直接走 party.setLeader（和 Q 键同一个入口，force 绕开锁）
            self.page.evaluate("() => { const o = G.party.members.find(m => m !== G.world.player && !m.mem.away); if (o) G.party.setLeader(o, { force: true, silent: true }); }")

        def cine():
            # boss 终结 / 阶段过场都会置 world.cine；0.6 秒后放开，等价于“过场结束回到自由”
            self.page.evaluate("() => { G.world.cine = { by: 'test' }; }")
            self.wait(400)
            # 过场期间就该静音，不能等过场结束（用户听到的是整段后续剧情里一直响）
            inside = self.snap()
            self.check(inside['loops'] == 0 and not inside['rush'], 'rush_loop_during_cine', inside=inside)
            self.wait(200)
            self.page.evaluate("() => { G.world.cine = null; }")

        self.case('guard', guard)
        self.case('special', special)
        self.case('swap', swap)
        self.page.evaluate("() => { const j = G.party.members.find(m => m.cid === 'jotaro'); if (j) G.party.setLeader(j, { force: true, silent: true }); }")
        self.case('cine', cine)

        # 回标题（reset 兜底）：此时不再有任何循环音
        self.page.evaluate("() => G.goTitle()")
        self.wait(800)
        t = self.snap()
        self.check(t['loops'] <= 0, 'loops_after_title', loops=t['loops'])
        print(json.dumps({'case': 'title', 'loops': t['loops']}, ensure_ascii=False), flush=True)

    def report(self):
        return {'errors': self.errors, 'notes': self.notes, 'seconds': self.elapsed()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--no-patch', action='store_true', help='关掉 settleRush，复现旧行为')
    ap.add_argument('--out', type=Path, default=GAME / 'tools' / '_playtest' / 'rush_loop')
    ap.add_argument('--shots-off', action='store_true', default=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
        t = RushLoop(page, args, args.out)
        page.on('pageerror', lambda e: t.errors.append({'kind': 'pageerror', 'text': str(e)}))
        try:
            page.goto((GAME / 'index.html').as_uri() + '?autotest=1', wait_until='load')
            t.run()
        except Exception as e:
            import traceback
            t.errors.append({'kind': 'tester_error', 'text': str(e), 'traceback': traceback.format_exc()})
        (args.out / ('result_nopatch.json' if args.no_patch else 'result.json')).write_text(
            json.dumps(t.report(), ensure_ascii=False, indent=2), encoding='utf-8')
        browser.close()
    print(json.dumps({'ok': not t.errors, 'errors': len(t.errors), 'no_patch': args.no_patch}, ensure_ascii=False))
    return 1 if t.errors else 0


if __name__ == '__main__':
    sys.exit(main())
