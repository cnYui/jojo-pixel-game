"""JoJo 游戏的新曲（包 1；技术约定 §5.9）。里程碑 1 不需要新曲：EXPORT 为空，build_audio 只导出原工程 10 首。

以后加新曲：写一个返回 `music.Song` 的构建函数，登记进 `music._BUILDERS` / `music.TRACKS`，名字放进 EXPORT。
下面的 `battle_egypt`（第8–10章九荣神战，规划 §2.4 / §7.3 的 P1）是调研报告 07 附录 B 的占位稿：
旋律只是验证记谱和渲染能跑通，没有经过作曲审听，**正式用之前要重写、给用户听**，所以现在不登记、不导出。
版权红线（源码 STYLE.md 第 10 行）：只写原创旋律，不抄动画原声和任何现成歌曲。
"""
import sys

sys.dont_write_bytecode = True

import os  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.normpath(os.path.join(_HERE, '..', '..', '源码'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from engine import music  # noqa: E402

EXPORT = []          # 要导出的新曲名字（M1：无）


def _t_battle_egypt():
    """占位稿（报告 07 附录 B）：E 弗里几亚 160 bpm 16 小节。未审听，不导出。"""
    from engine.music import (BRASS, CHIP, FMBASS, HARM, LEAD, PLUCK, TRIBASS, Song)
    S = Song('battle_egypt', bpm=160, bars=16, key='E', mode='phrygian', seed=123)
    S.chords('''E:16 | F:8 E:8 | Dm:16 | E:8 F:8 |
                E:16 | F:8 E:8 | G:8 F:8 | E:16 |
                Am:16 | G:16 | F:16 | E:16 |
                Am:8 G:8 | F:8 E:8 | Dm:8 F:8 | E:16 |''')
    A = '''E5:2 F5:2 G#5:2 A5:2 G#5:3 F5:1 E5:4 | F5:3 E5:1 D5:2 C5:2 B4:4 r:4 |
           D5:2 E5:2 F5:2 A5:2 G5:4 F5:2 E5:2 | G#5:4 F5:2 E5:2 D5:4 E5:4 |
           E5:2 F5:2 G#5:2 A5:2 B5:3 A5:1 G#5:4 | C6:3 B5:1 A5:2 G#5:2 F5:4 E5:4 |
           D5:4 G5:4 F5:2 E5:2 D5:2 F5:2 | E5:12 r:4 |'''
    B = '''A5:3 C6:1 E6:4 D6:2 C6:2 B5:4 | G5:3 B5:1 D6:4 C6:2 B5:2 A5:4 |
           F5:3 A5:1 C6:4 B5:2 A5:2 G#5:4 | E5:2 F5:2 G#5:2 B5:2 E6:8 |
           C6:4 B5:2 A5:2 B5:4 A5:2 G5:2 | A5:4 G#5:2 F5:2 E5:8 |
           D5:2 F5:2 A5:2 D6:2 C6:2 A5:2 F5:2 A5:2 | G#5:4 B5:4 E6:4 E5:4 |'''
    S.voice(S.parse(A + B), LEAD, pan=-0.08, dly=0.18, rev=0.08, name='lead', role='lead')
    S.voice(S.parse(B, bar0=8, tr=-12, vel=0.7), dict(BRASS, gain=0.26), pan=0.3, rev=0.1, name='brass')
    S.voice(S.harmonize(S.parse(A, vel=0.6), -2), HARM, pan=0.38, dly=0.1, rev=0.08, name='harm')
    S.voice(S.arp('0:1 1 2 1 0 1 2 3 0 1 2 1 0 1 2 3', 52, 71, bars=(8, 16), vel=0.7), PLUCK, pan=0.42,
            dly=0.2, rev=0.08, name='arp')
    S.voice(S.stabs('x--x--x-x--x--x-', 52, 69, 3, bars=(0, 8)), CHIP, pan=-0.3, rev=0.08, name='chip')
    bass = S.bass('R:2 R O R R O R O', lo=40)
    S.voice(bass, TRIBASS, name='tri')
    S.voice(bass, dict(FMBASS, gain=0.24), name='fm', pan=0.05)
    S.drums('c...k.t.k.k.t...' + 'k...k.t.k.k.t...' * 6 + 'k...k.t.T.m.t.tt'
            + 'c...s..kk.k.s...' + 'k...s..kk.k.s...' * 6 + 'k...s...T.m.t.sS')
    S.drums('h.h.h.h.h.h.h.h.' * 8 + 'hhHhhhHhhhHhhhHh' * 8, gain=0.8)
    S.drums('..z...z...z...z.' * 8 + '................' * 8, gain=0.7)
    S.rms_target = 0.2
    return S


def register_drafts():
    """手动试听占位稿时调用（不在构建里自动调用）。"""
    music._BUILDERS['battle_egypt'] = _t_battle_egypt
    music.TRACKS['battle_egypt'] = 'Egypt battle (DRAFT, not reviewed). E phrygian-dominant, 160 bpm, 16 bars.'
