"""开发调参用：直接从虎豹别墅开打第1章银色战车（G.DEV.ch1Chariot，战斗走正式剧情的同一个 chariot()），
看一场要打多久、各阶段多久、输几次、关键画面。键盘打法和 test_ch1.py 的 Ch1Tester.chariot 相同。

只用来调数值，不是通关证据：验收一律跑整章 python -B tools\\dev\\full\\test_ch1.py ch1（--lose）。
用法：python -B tools\\dev\\full\\dev_chariot.py ch1 --out tools\\_playtest\\early_dev_chariot_1 [--lose]
"""
from pathlib import Path
import json
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import playtest
import test_ch1


class DevChariot(test_ch1.Ch1Tester):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.phase_at, self.cur_phase, self.fight_t0, self.hp_log = {}, None, None, []

    def enter(self):
        self.page.wait_for_function("() => G.booted && G.ui.menu && G.DEV && G.DEV.ch1Chariot", timeout=30000)
        self.page.evaluate("() => { G.CHAPTERS[1].run = G.DEV.ch1Chariot; }")
        if not self.menu("选择章节"):
            return False
        return self.menu("第1章")

    def st(self):
        s = super().st()
        if s.get('fightId') == 'b02_chariot' and s.get('combat'):
            if self.fight_t0 is None:
                self.fight_t0 = self.elapsed()
            h = s.get('fightHint') or {}
            ph = (self.loses.get('b02_chariot', 0), h.get('phase'))
            if ph != self.cur_phase:
                self.cur_phase = ph
                self.phase_at[f'try{ph[0]}_phase{ph[1]}'] = round(self.elapsed() - self.fight_t0, 1)
                self.shot(f'chariot_try{ph[0]}_phase{ph[1]}')
            if h.get('stance') and 'stance' not in self.special:
                self.special['stance'] = True
                self.shot('chariot_stance_arc')
            if h.get('open') and 'open' not in self.special:
                self.special['open'] = True
                self.shot('chariot_open')
            boss = next((e for e in s.get('enemies') or [] if e[13]), None)
            ft = round(self.elapsed() - self.fight_t0, 1)
            if boss and (not self.hp_log or ft - self.hp_log[-1][0] >= 5):
                self.hp_log.append([ft, boss[4], s.get('hp'), s.get('energy'), h.get('phase'), self.loses.get('b02_chariot', 0)])
            if h.get('statueUsed') and 'statue_hit' not in self.special:
                self.special['statue_hit'] = True
                self.shot('chariot_statue_stuck')
        return s

    def explore(self, s):
        # 虎豹别墅：直接和波鲁纳雷夫搭话开打
        npc = next((n for n in s.get('npcs') or [] if '波鲁纳雷夫' in (n[0] or '')), None)
        if npc:
            if self.move(s, npc[1] - 20, npc[2], 6):
                self.hold()
                self.pulse('e')
            return
        return super().explore(s)

    def validate(self):
        s = self.st()
        self.check(any(n['kind'] == 'route_complete' for n in self.notes), 'chapter_not_completed')
        for name in ('missingImg', 'missingSfx', 'missingGlyph', 'missingHead'):
            self.check(not s.get(name), name, items=s.get(name))
        evs = s.get('evTotals') or {}
        for name in ('fx_unknown', 'fx_error', 'script_error'):
            self.check(not evs.get(name), name, count=evs.get(name))

    def report(self):
        last = self.fights.get('b02_chariot') or {}
        return {**super().report(), 'phase_at': self.phase_at, 'hp_log': self.hp_log, 'last_hint': last.get('fightHint'),
                'fight_seconds': round(self.elapsed() - (self.fight_t0 or 0), 1)}


if __name__ == '__main__':
    playtest.Tester = DevChariot
    raise SystemExit(playtest.main())
