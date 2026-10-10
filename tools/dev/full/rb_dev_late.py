"""开发调参用（routes-b）：直接开打后段的某一段，看要打多久、输几次、关键画面。
战斗用的是正式剧情的同一份函数（G.LATE.final.dioFight 等），打法用 test_late_routes.py 的 LateTester（真实键盘、只读快照）。
**只用来调数值、看画面，不是通关证据**：验收一律从「选择章节」跑整章（test_late_routes.py）。

用法（游戏目录）：
    python -B tools\\dev\\full\\rb_dev_late.py final --entry dio2 --out tools\\_playtest\\rb_dev_dio2 [--lose]
入口见 ENTRIES（章节参数要和入口对上：借「选择章节」里那一章的位置和背景包）。
"""
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import playtest  # noqa: E402
import test_late_routes  # noqa: E402

# 入口：页面里 eval 的 async 函数源码（dev 才写旗标：第2、3段要“已经觉醒”，正式流程由第1段设）
ENTRIES = {
    'dio1': "async S => { await G.LATE.final.dioFight(1); }",
    'dio2': "async S => { G.flags.dioGrowth = true; await G.LATE.final.dioFight(2); }",
    'dio3': "async S => { G.flags.dioGrowth = true; await G.LATE.final.dioFight(3); }",
    'roof': "async S => { await G.LATE.final.roofWeb(); }",
    'birds': "async S => { S.party(['iggy'], { leader: 'iggy' }); const r = await G.LATE.ch10.birdFight(S, 'cairo_day_ch10', 1500, true);"
             " if (r > 0) await G.LATE.ch10.birdFight(S, 'sewer_ch10', r, false); }",
    'prophecy': "async S => { S.party(['iggy', 'polnareff'], { leader: 'iggy' }); await S.setStage('cairo_day_ch10', { x: 360, y: 160 });"
                " for (let n = 0; n < 3; n++) await G.LATE.ch10.prophecy(S, n); }",
    'cream': "async S => { S.party(['polnareff', 'iggy'], { leader: 'polnareff' }); await S.setStage('hall_ch11');"
             " await G.LATE.ch11.creamHidden(); await G.LATE.ch11.creamSun(); }",
}
ENTRY = None


class DevLate(test_late_routes.LateTester):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.hp_log = []

    def enter(self):
        self.page.wait_for_function("() => G.booted && G.ui.menu && G.LATE && G.LATE.final", timeout=30000)
        idx = playtest.chapter_index(self.args.chapter)
        self.page.evaluate("([i, src]) => { G.CHAPTERS[i].run = eval(src); }", [idx, ENTRIES[ENTRY]])
        if not self.menu("选择章节"):
            return False
        for _ in range(idx // 5):
            if not self.menu("下一页"):
                return False
        return self.menu("第" + str(idx) + "章" if idx != 12 else "终章")

    def st(self):
        s = super().st()
        fid = s.get('fightId')
        if fid and s.get('combat'):
            boss = next((e for e in s.get('enemies') or [] if e[13]), None)
            ft = s.get('fightT') or 0
            last = self.hp_log[-1] if self.hp_log else None
            if boss and (not last or last[1] != fid or ft - last[2] >= 3 or ft < last[2]):
                self.hp_log.append([self.elapsed(), fid, round(ft, 1), boss[4], s.get('hp'), s.get('energy'), self.loses.get(fid, 0)])
                print(json.dumps({'hp': self.hp_log[-1]}, ensure_ascii=False), flush=True)
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
        return {**super().report(), 'hp_log': self.hp_log, 'entry': ENTRY, 'note': '开发调参：直接开打，不是通关证据'}


if __name__ == '__main__':
    if '--entry' in sys.argv:
        i = sys.argv.index('--entry')
        ENTRY = sys.argv[i + 1]
        del sys.argv[i:i + 2]
    if ENTRY not in ENTRIES:
        raise SystemExit('需要 --entry，可选：' + ' '.join(ENTRIES))
    playtest.Tester = DevLate
    raise SystemExit(playtest.main())
