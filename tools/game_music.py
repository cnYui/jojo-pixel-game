"""JoJo 游戏的新曲（包 1；技术约定 §5.9）。

加新曲：写一个返回 `music.Song` 的构建函数，登记进 `music._BUILDERS` / `music.TRACKS`，名字放进 EXPORT；
build_audio 渲染 `list(music.TRACKS) + EXPORT`，每章用哪几首在 `tools\\registry\\packs.json` 的 music 里登记。
版权红线（源码 STYLE.md 第 10 行）：只写原创旋律，不抄动画原声和任何现成歌曲。

2026-10-19（第5章到终章游玩脚本 + 素材总表 §五）：
  battle_egypt  第8–10章的战斗（九荣神）。重写了报告 07 附录 B 的占位稿：E 为中心、A 和声小调的音（= E 弗里几亚属调式
                E F G# A B C D，“埃及味”来自 F–E 的半音和 G#），150 bpm，24 小节：2 小节手鼓前奏 → A 段压低的主题 →
                B 段往上冲 → 4 小节“弄蛇人”装饰音的桥 → 2 小节回前奏。
  comedy        第8章托特神的三个预言、第10章（选用）。F 大调 112 bpm 摇摆，跳音主旋律 + 木琴（FM 铃）+ 嘣嚓低音 + 木鱼。
  dream         第6章死神13 的梦（梦一、梦二开场）。C 大调 3/4 拍 96 bpm 八音盒华尔兹，和声里插了两处半音外的和弦
                （Ab、Db），音盒音轻微走调（颤音 + 低八度错音分），听起来甜、但不对劲。
"""
import sys

sys.dont_write_bytecode = True

import os  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.normpath(os.path.join(_HERE, '..', '..', '源码'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from engine import music  # noqa: E402
from engine.music import (BELL, BRASS, CHIP, FMBASS, HARM, LEAD, LEAD50, PAD, PLUCK, STAB, TRIBASS,  # noqa: E402
                          Song)

EXPORT = ['battle_egypt', 'comedy', 'dream']


def _t_battle_egypt():
    # 和声用 A 和声小调的音阶（A B C D E F G#），和弦以 E 为中心：harmonize 出来的三度下行音不会跑出这套“埃及”音阶
    S = Song('battle_egypt', bpm=150, bars=24, key='A', mode='hminor', seed=123)
    S.chords('''E:16 | F:8 E:8 |
                E:16 | F:16 | E:16 | Dm:8 E:8 | E:16 | F:16 | Am:8 Dm:8 | E:16 |
                Am:16 | G:16 | F:16 | E:16 | Am:8 G:8 | F:8 E:8 | Dm:8 F:8 | E:16 |
                E:16 | E:8 F:8 | E:16 | Dm:8 E:8 |
                F:16 | E:16 |''')
    intro = 'r:16 | r:8 B4:2 C5:2 B4:2 G#4:2 |'
    A = '''E5:3 F5:1 E5:2 D5:2 C5:2 B4:2 G#4:2 B4:2 | C5:3 D5:1 C5:2 B4:2 A4:4 F4:4 |
           G#4:2 A4:2 B4:2 C5:2 B4:3 A4:1 G#4:4 | F4:2 A4:2 D5:4 C5:2 B4:2 G#4:4 |
           E5:3 F5:1 G#5:2 A5:2 B5:3 A5:1 G#5:4 | A5:3 G#5:1 F5:2 E5:2 F5:4 C5:4 |
           C5:2 E5:2 A5:4 F5:2 A5:2 D5:4 | G#4:4 B4:4 E5:6 r:2 |'''
    B = '''A5:6 C6:2 B5:2 A5:2 G#5:4 | G5:6 B5:2 A5:2 G5:2 F5:4 |
           F5:3 G5:1 A5:2 C6:2 B5:2 A5:2 G#5:4 | E5:2 G#5:2 B5:2 E6:2 D6:4 B5:4 |
           C6:3 B5:1 A5:2 E5:2 D6:3 C6:1 B5:2 G5:2 | A5:3 G5:1 F5:2 C5:2 B5:3 C6:1 G#5:4 |
           D6:4 C6:2 A5:2 C6:4 F6:4 | E6:8 B5:2 G#5:2 E5:4 |'''
    # “弄蛇人”：围着 E / G# / B 绕的装饰音，压在 E 的长音上
    brg = '''E5:1 F5:1 E5:1 D5:1 E5:4 r:2 B4:1 C5:1 B4:1 A4:1 B4:2 |
             G#4:1 A4:1 G#4:1 F4:1 G#4:4 A4:2 B4:2 C5:2 D5:2 |
             E5:1 F5:1 G#5:1 A5:1 B5:4 A5:1 G#5:1 F5:1 E5:1 F5:4 |
             D5:2 F5:2 A5:2 F5:2 G#5:2 B5:2 D6:2 E6:2 |'''
    turn = 'F5:2 r:2 F5:2 r:2 E5:2 r:2 E5:2 r:2 | F5:4 E5:4 D5:4 B4:4 |'
    S.voice(S.parse(intro + A + B + brg + turn), LEAD, pan=-0.08, dly=0.18, rev=0.08, name='lead', role='lead')
    S.voice(S.harmonize(S.parse(B, bar0=10, vel=0.6), -2), HARM, pan=0.38, dly=0.1, rev=0.08,
            name='harm', role='harm')
    S.voice(S.parse(B, bar0=10, tr=-12, vel=0.62), dict(BRASS, gain=0.2), pan=0.28, rev=0.1, name='brass')
    S.voice(S.stabs('x--x--x-x--x--x-', 52, 69, 3, bars=(2, 10)), CHIP, pan=-0.3, rev=0.08, name='chip')
    S.voice(S.arp('0:1 1 2 1 0 1 2 3 0 1 2 1 0 1 2 3', 52, 71, bars=(18, 22), vel=0.7), PLUCK, pan=0.42,
            dly=0.2, rev=0.08, name='arp')
    # 前奏的低音 riff：E 上一个 F 的半音邻音，像手鼓前的弦乐拨奏
    riff = S.parse('E2:2 E2:2 F2:2 E2:2 E2:2 E2:2 F2:2 G#2:2 | E2:2 E2:2 F2:2 E2:2 D2:2 E2:2 F2:2 E2:2 |', vel=0.95)
    bass = (riff + S.bass('R:2 R O R R O R O', lo=38, bars=(2, 10))
            + S.bass('R:2 R O R F O R A', lo=38, bars=(10, 18))
            + S.bass('R:3 R:3 R:2 R:3 R:3 O:2', lo=38, bars=(18, 22))
            + S.bass('R:2 R O R R O R O', lo=38, bars=(22, 24)))
    S.voice(bass, TRIBASS, name='tri')
    S.voice(bass, dict(FMBASS, gain=0.24), name='fm', pan=0.05)
    S.drums('c..t.tm.k.t.m.T.' + 'k..t.tm.k.t.m.TT'
            + 'k..t.tk.s..t.tk.' * 7 + 'k..t.tk.s.TTmmtt'
            + 'c...s..kk.k.s...' + 'k...s..kk.k.s...' * 6 + 'k...s..kk.s.sSSS'
            + 'k..b..b.k.b.b...' * 3 + 'k..b..b.k.b.TTmm'
            + 'K...K...K...K...' + 'k.k.s.s.T.m.t.SS')
    S.drums('z.z.z.z.z.z.z.z.' * 2 + 'h.h.h.h.h.h.h.h.' * 8 + 'hhHhhhHhhhHhhhHh' * 8
            + 'z.zzz.zzz.zzz.zz' * 4 + 'h.h.h.h.h.h.h.h.' * 2, gain=0.8)
    S.rms_target = 0.2
    return S


def _t_comedy():
    S = Song('comedy', bpm=112, bars=16, key='F', mode='major', swing=0.58, seed=211)
    S.chords('''F:16 | Bb:8 C7:8 | F:8 D7:8 | Gm:8 C7:8 | F:16 | Bb:8 Bdim7:8 | F/C:8 D7:8 | G7:8 C7:8 |
                Dm:16 | A7:16 | Dm:8 G7:8 | C7:16 | F:16 | Bb:8 Bdim7:8 | F/C:8 C7:8 | F:8 C7:8 |''')
    lead = '''C5:1 r:1 F5:1 r:1 A5:2 G5:1 F5:1 E5:2 F5:2 r:4 | D5:1 r:1 F5:1 r:1 Bb5:2 A5:2 G5:1 r:1 E5:1 r:1 C5:4 |
              A4:1 r:1 C5:1 r:1 F5:2 A5:2 F#5:2 A5:2 C6:4 | Bb5:2 A5:1 G5:1 D5:2 E5:2 G5:2 Bb5:2 A5:2 G5:2 |
              C5:1 r:1 F5:1 r:1 A5:2 G5:1 F5:1 E5:2 F5:2 r:4 | D5:1 r:1 F5:1 r:1 Bb5:4 B5:1 r:1 D6:1 r:1 F6:4 |
              C6:2 A5:2 F5:2 C5:2 F#5:2 A5:2 D6:2 C6:2 | B5:2 G5:2 F5:2 D5:2 E5:2 G5:2 Bb5:2 E5:2 |
              D5:2 F5:1 A5:1 D6:4 C#6:1 D6:1 E6:1 D6:1 A5:4 | C#6:2 A5:1 E5:1 G5:4 F5:1 E5:1 D5:1 C#5:1 E5:4 |
              D5:1 r:1 F5:1 r:1 A5:2 D6:2 B5:2 G5:2 F5:2 D5:2 | E5:2 G5:2 Bb5:2 C6:2 Bb5:1 A5:1 G5:1 F5:1 E5:2 D5:2 |
              C5:1 r:1 F5:1 r:1 A5:2 G5:1 F5:1 E5:2 F5:2 r:4 | D5:1 r:1 F5:1 r:1 Bb5:4 Ab5:1 r:1 B5:1 r:1 D6:4 |
              C6:2 A5:2 F5:2 A5:2 G5:2 E5:2 C5:2 E5:2 | F5:2 r:2 C5:1 r:1 F4:2 r:4 E5:1 F5:1 G5:2 |'''
    # 跳音：gate 压短；起音带一点往上滑（滑稽的“哟”）
    S.voice(S.parse(lead), dict(LEAD50, gate=0.5, bend=(-0.8, 0.02), vib=(0.1, 6.0, 0.25), gain=0.34),
            pan=-0.1, dly=0.12, rev=0.08, name='lead', role='lead')
    # 木琴：B 段（第 8–15 小节）高八度轻轻跟一遍
    S.voice(_bars(S.parse(lead, tr=12, vel=0.4), 8, 16), dict(BELL, gain=0.16, d=0.25, r=0.15), pan=0.35,
            rev=0.12, name='xylo')
    S.voice(S.stabs('..x-..x-..x-..x-', 57, 74, 3), dict(STAB, gate=0.5), pan=0.3, rev=0.08, name='stabs')
    S.voice(S.bass('R:4 F:4 R:4 F:4', lo=36), dict(TRIBASS, gate=0.55, gain=0.6), name='tri')
    S.drums('k.......k.......' * 15 + 'k.......k...k.k.')
    S.drums('....p.......p...' * 7 + '....p.......p.pp' + '....p.......p...' * 7 + '....p.....p.p.p.', gain=0.6)
    S.drums('b...b.b.b...b.b.' * 8 + 'b.B.b.B.b.B.b.B.' * 8, gain=0.55)
    S.rms_target = 0.17
    return S


def _t_dream():
    S = Song('dream', bpm=96, bars=16, beats=3, key='C', mode='major', seed=313)
    S.chords('''C:12 | G7:12 | C:12 | Ab:12 | F:12 | Fm:12 | C:12 | G7:12 |
                Am:12 | E:12 | F:12 | Db:12 | C:12 | Ab7:12 | G7:12 | C:12 |''')
    box = '''E6:4 G6:2 C7:2 G6:2 E6:2 | D6:4 F6:2 B6:2 G6:2 F6:2 | E6:4 G6:2 C7:4 E7:2 | Eb7:4 C7:2 Ab6:2 Eb6:2 C6:2 |
             A6:4 C7:2 F7:2 C7:2 A6:2 | Ab6:4 C7:2 F7:2 C7:2 Ab6:2 | G6:6 E6:2 C6:2 E6:2 | D6:6 B5:2 D6:2 F6:2 |
             E6:4 A6:2 C7:2 B6:2 A6:2 | G#6:6 B6:2 E7:2 D7:2 | C7:4 A6:2 F6:2 A6:2 C7:2 | Db7:4 Ab6:2 F6:2 Db6:4 |
             E6:4 G6:2 C7:2 G6:2 E6:2 | Eb7:4 Gb6:2 C7:2 Ab6:2 Eb6:2 | D6:3 F6:1 B6:2 D7:2 F7:2 G7:2 | C7:6 r:6 |'''
    # 八音盒：FM 铃 + 一点颤音（走调的感觉）；再叠一层低八度、音分偏 14 的弱音盒，两层互相“拍”出不稳
    S.voice(S.parse(box), dict(BELL, gain=0.26, vib=(0.12, 4.5, 0.0)), pan=-0.15, dly=0.2, rev=0.4,
            name='musicbox', role='lead')
    S.voice(S.parse(box, tr=-12, vel=0.35), dict(BELL, gain=0.16, detune=14), pan=0.3, dly=0.25, rev=0.45,
            name='box_warp')
    S.voice(S.pad(55, 72, 3), dict(PAD, detune=-5, gain=0.1), pan=-0.4, rev=0.45, name='padL')
    S.voice(S.pad(55, 72, 3), dict(PAD, detune=5, duty=0.4, gain=0.1), pan=0.4, rev=0.45, name='padR')
    S.voice(S.bass('R:4 F:4 F:4', lo=36, vel=0.6), dict(TRIBASS, gate=0.5, gain=0.45), name='tri')
    S.drums('i...j...j...' * 16, gain=0.45)
    S.delay = (0.3125, 0.47, 0.3)
    S.reverb = 2.6
    S.rms_target = 0.15
    return S


def _bars(ev, b0, b1, bs=16):
    return [e for e in ev if b0 * bs <= e[0] < b1 * bs]


music._BUILDERS.update({'battle_egypt': _t_battle_egypt, 'comedy': _t_comedy, 'dream': _t_dream})
music.TRACKS.update({
    'battle_egypt': 'Egyptian Nine Gods battle. E-centred A harmonic minor (E phrygian dominant), 150 bpm, 24 bars: '
                    'hand-drum intro riff, low menacing A theme, rising B theme, snake-charmer bridge.',
    'comedy': 'Comic caper. F major swing, 112 bpm, 16 bars: staccato lead with scoops, xylophone answer, '
              'oom-pah bass, woodblocks.',
    'dream': "Death 13's dream carnival. C major 3/4 waltz, 96 bpm, 16 bars: detuned music box, chromatic "
             'Ab / Db chords, clock ticks.',
})


def register_drafts():
    """兼容旧的手动试听入口（现在 import 就已经登记）。"""
    return list(EXPORT)
