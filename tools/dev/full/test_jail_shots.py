"""序章拘留所改版验收（2026-10-09：开打前掰铁栏出来、教学战在走廊打、铁栏有前后景、连打拳影挂在替身身前）。

在 test_prologue.py 的真实键盘路线上，多截几张关键画面（只读状态，不改游戏）：
- jail_visitors_layer：荷莉 / 乔瑟夫在走廊、承太郎在牢里（铁栏只挡承太郎）
- jail_walked_out：掰开铁栏、承太郎站到走廊上
- jail_step3_jet / jail_step3_jet_guard：火柱烧着（看得见火）、按住 L 挡
- jail_rush_fists：第 5 步欧拉连打（紫色拳影在白金之星身前）
- jail_finale_ora：第 6 步 U 的收尾
用法：python -B tools\\dev\\full\\test_jail_shots.py prologue --out tools\\_playtest\\jail_corridor
"""
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import playtest
import test_prologue

PROBE_JS = """() => {
  const W = G.world, p = W.player, st = W.stage;
  const holly = st && st.find ? st.find('holly') : null;
  return {
    stage: st && st.id, combat: !!W.combat, bend: st && st.state ? st.state.bend || 0 : 0,
    py: p ? p.y : null, pstate: p ? p.state : null, rush: !!(p && p.rush),
    jet: !!(W.hazards || []).some(h => h.tag === 'flame_jet' && h.phase === 'active' && !h.dead),
    special: !!(W.cine && W.cine.by === 'special-run'),
    holly: holly && holly.visible !== false ? [holly.x, holly.y] : null,
  };
}"""


class JailTester(test_prologue.ProTester):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.since = {}
        self.probe = {}

    def _after(self, key, cond, delay, name):
        now = time.monotonic()
        if not cond:
            self.since.pop(key, None)
            return
        if now - self.since.setdefault(key, now) >= delay:
            self.shot_once(name)

    def st(self):
        s = super().st()
        if s.get('stage') != 'jail_pro':
            return s
        try:
            q = self.page.evaluate(PROBE_JS)
        except Exception:
            return s
        self.probe = q
        hy = (q.get('holly') or [0, 0])[1]
        self._after('vis', q['bend'] == 0 and not q['combat'] and hy >= 160, 1.2, 'jail_visitors_layer')
        self._after('out', q['bend'] >= 1 and not q['combat'] and (q['py'] or 0) >= 150, 0.6, 'jail_walked_out')
        self._after('jet', q['jet'], 0.25, 'jail_step3_jet')
        self._after('jetg', q['jet'] and q['pstate'] == 'guard', 0.4, 'jail_step3_jet_guard')
        self._after('rush', q['rush'], 0.3, 'jail_rush_fists')
        self._after('sp', q['special'], 0.9, 'jail_finale_ora')
        return s


if __name__ == '__main__':
    playtest.Tester = JailTester
    raise SystemExit(playtest.main())
