"""开发调参用：直接开打第2、3章的某一战（G.DEV.<入口>，战斗配置和正式剧情是同一份），看要打多久、输几次、关键画面。
打法用 test_mid_early.py 的 EarlyTester（键盘输入、只读快照）。只用来调数值，不是通关证据：验收一律跑整章。

用法：python -B tools\\dev\\full\\dev_fight.py ch2 --entry ch2Strength --out tools\\_playtest\\early_dev_strength [--lose]
入口：ch2Darkmoon ch2Strength ch3Devo ch3Yellow（章节参数要和入口对上，用来借「选择章节」里那一章的位置）
"""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import playtest
import test_mid_early

ENTRY = None


class DevFight(test_mid_early.EarlyTester):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.hp_log, self.fid = [], None

    def enter(self):
        self.page.wait_for_function("e => G.booted && G.ui.menu && G.DEV && G.DEV[e]", arg=ENTRY, timeout=30000)
        idx = playtest.chapter_index(self.args.chapter)
        self.page.evaluate("([i, e]) => { G.CHAPTERS[i].run = G.DEV[e]; }", [idx, ENTRY])
        if not self.menu("选择章节"):
            return False
        return self.menu("第" + str(idx) + "章")

    def st(self):
        s = super().st()
        fid = s.get('fightId')
        if fid and s.get('combat'):
            self.fid = fid
            boss = next((e for e in s.get('enemies') or [] if e[13]), None)
            ft = self.fight_secs.get(fid, 0)
            if boss and (not self.hp_log or ft - self.hp_log[-1][0] >= 5):
                self.hp_log.append([ft, boss[4], s.get('hp'), s.get('energy'), self.loses.get(fid, 0), s.get('fightHint')])
        return s

    def validate(self):
        s = self.st()
        self.check(any(n['kind'] == 'route_complete' for n in self.notes), 'chapter_not_completed')
        for name in ('missingImg', 'missingSfx', 'missingGlyph', 'missingHead'):
            self.check(not s.get(name), name, items=s.get(name))
        evs = s.get('evTotals') or {}
        for name in ('fx_unknown', 'fx_error', 'script_error'):
            self.check(not evs.get(name), name, count=evs.get(name))

    def report(self):
        return {**super().report(), 'hp_log': self.hp_log, 'entry': ENTRY}


if __name__ == '__main__':
    if '--entry' in sys.argv:
        i = sys.argv.index('--entry')
        ENTRY = sys.argv[i + 1]
        del sys.argv[i:i + 2]
    playtest.Tester = DevFight
    raise SystemExit(playtest.main())
