# -*- coding: utf-8 -*-
r"""包 2 联系表的用例（Python 参考 ref.py 和 JS 版 fx_sheet.html 共用；python cases.py 生成 _out\cases.js）。

每个用例：
  id     行标签
  bg     背景（make_stub_data.py 的 BGS）
  calls  依次调用：{fn, pos, kw, py, py_pos, py_kw}
         fn = G.FX 的函数名；pos = JS 位置参数（P 之后、kw 之前）；kw = 关键字参数（键名照 Python）
         py = None → 源码 engine.fx 同名函数；'adapter:<名>' → ref.py 里的适配函数；'-' → 原工程没有（只画 JS）
         py_pos / py_kw：Python 那边参数不同时覆盖
  times  4 个时刻（相对 T0 的秒数），或 cols：4 列各自的 {t, a, i, kw, py_kw}
  t1     '$t1' = T0 + t1（rush / emerald_splash / vines / clash_sparks 的绝对结束时刻）
令牌：'$t' 当前时刻、'$t0' = T0、'$t1'、'$a'（列的 a）、'$i'（列的 i）。
"""
import sys
sys.dont_write_bytecode = True

import json  # noqa: E402
import os  # noqa: E402

T0 = 2.0
P0 = 'P0'
P1 = 'P1'
EX = '后面章节'


def C(id_, fn, pos, kw=None, bg='hkn', times=(0.05, 0.1, 0.2, 0.4), cols=None, t1=None, py=None, py_pos=None, py_kw=None,
      pre=(), post=(), pri=P0):
    call = dict(fn=fn, pos=list(pos), kw=dict(kw or {}), py=py)
    if py_pos is not None:
        call['py_pos'] = list(py_pos)
    if py_kw is not None:
        call['py_kw'] = dict(py_kw)
    c = dict(id=id_, bg=bg, calls=list(pre) + [call] + list(post), pri=pri)
    if cols:
        c['cols'] = cols
    else:
        c['times'] = list(times)
    if t1 is not None:
        c['t1'] = t1
    return c


def S(name, x, y, **kw):
    """先画 / 后画一个精灵（Python 用 fr.spr；JS 用 G.FX.sprite）。"""
    return dict(fn='sprite', pos=[name, x, y], kw=kw, py='adapter:sprite')


TS = (0, 0.09, 0.17, 0.25)          # 12 fps 抽帧的效果：看相邻两步
CREW = [S('jotaro.idle', 120, 150), S('starplat.idle', 112, 140, alpha=0.92), S('kakyoin.idle', 220, 150, flip=True)]

CASES = [
    # ---- 拳击与冲击
    C('speedlines radial', 'speedlines', ['$t'], dict(cx=160, cy=90, n=48, inner=40), times=TS),
    C('speedlines ORA α.45', 'speedlines', ['$t'], dict(cx=200, cy=100, n=40, inner=26, alpha=0.45, colour='#d8c8ff'), times=TS),
    C('speedlines horizontal', 'speedlines', ['$t'], dict(style='horizontal', n=30, inner=8, alpha=0.8, cy=110), times=TS),
    C('impact_frame', 'impact_frame', [], {}, pre=CREW,
      cols=[dict(kw=dict(style='invert')), dict(kw=dict(style='purple')), dict(kw=dict(style='bw3')), dict(kw=dict(style='blue'))]),
    C('hit_spark 18', 'hit_spark', [160, 100, '$t', '$t0'], dict(size=18), times=(0.02, 0.07, 0.12, 0.17)),
    C('hit_spark 22 终结', 'hit_spark', [160, 100, '$t', '$t0'], dict(size=22, accent='#c080ff', dur=0.3), times=(0.03, 0.1, 0.18, 0.25)),
    C('shockwave 60', 'shockwave', [160, 100, '$t', '$t0'], dict(r_max=60, width=3), times=(0.05, 0.1, 0.2, 0.3)),
    C('shockwave 地面', 'shockwave', [160, 150, '$t', '$t0'], dict(r_max=120, squash=0.3, colour='#fff0c0', width=3), times=(0.05, 0.1, 0.2, 0.3)),
    C('shockwave 盾 1.6', 'shockwave', [160, 100, '$t', '$t0'], dict(r_max=18, squash=1.6, dur=0.2), times=(0.02, 0.06, 0.1, 0.15)),
    C('rush ORA', 'rush', [170, 105, '$t', '$t0', '$t1'], dict(direction=1, fist='starplat.fist', spread=36, rate=40, reach=30, life=0.3),
      t1=1.0, times=(0.1, 0.2, 0.4, 0.8), pre=[S('starplat.rush', 140, 150)]),
    C('rush ORA 游戏版 big.3', 'rush', [170, 105, '$t', '$t0', '$t1'], dict(direction=1, fist='starplat.fist', spread=36, rate=40, reach=30, life=0.3, big=0.3),
      py_kw=dict(direction=1, fist='starplat.fist', spread=36, rate=40, reach=30, life=0.3), t1=1.0, times=(0.1, 0.2, 0.4, 0.8), pre=[S('starplat.rush', 140, 150)]),
    C('rush MUDA ←', 'rush', [150, 100, '$t', '$t0', '$t1'], dict(direction=-1, fist='theworld.fist', spread=26, rate=34, reach=30), t1=1.0,
      times=(0.1, 0.2, 0.4, 0.8)),
    C('clash_sparks', 'clash_sparks', ['$t', '$t0', '$t1', 160, 100], dict(seed=3), t1=1.0, times=(0.1, 0.3, 0.5, 0.7),
      py='adapter:clash_sparks'),
    C('afterimage', 'afterimage', ['chariot.thrust', [[90, 150, 0], [115, 150, 1], [140, 150, 2], [165, 150, 2]]], {},
      cols=[dict(kw=dict(colour='#c8d8ff')), dict(kw=dict()), dict(kw=dict(colour='#e8c070')), dict(kw=dict(colour='#8090ff', alpha0=0.2, alpha1=0.55))]),
    # ---- 粒子
    C('burst', 'burst', [160, 110, '$t', '$t0'], dict(n=40, speed=120, life=0.8, colours=['#ffd83c', '#ffffff', '#ff9820'], gravity=120, size=2),
      times=(0.05, 0.15, 0.3, 0.6)),
    C('dust', 'dust', [160, 150, '$t', '$t0'], dict(n=10, size=1.2), times=(0.05, 0.15, 0.3, 0.5)),
    C('explosion 40', 'explosion', [160, 110, '$t', '$t0'], dict(size=40), times=(0.04, 0.2, 0.6, 1.2)),
    C('smoke', 'smoke', [160, 140, '$t', '$t0'], dict(n=8, size=6, rise=40), times=(0.2, 0.5, 0.9, 1.4)),
    # ---- 火
    C('fire 16×24', 'fire', [160, 150, '$t'], dict(w=16, h=24), times=TS),
    C('fire 34×60 blue', 'fire', [160, 160, '$t'], dict(w=34, h=60, palette='blue'), times=TS),
    C('fire_ankh 40', 'fire_ankh', [160, 90, '$t', '$t0'], dict(size=40), times=(0.05, 0.15, 0.3, 0.6)),
    C('fireball', 'fireball', [160, 90, 8], {}, py='adapter:fireball',
      cols=[dict(kw=dict(heat=1.0)), dict(kw=dict(heat=0.6)), dict(kw=dict(heat=0.3)), dict(kw=dict(heat=0.5, lift=1))]),
    C('fire_jet', 'fire_jet', [70, 250, 100, '$t'], dict(thick=1.0), py='adapter:fire_jet', times=(0, 0.07, 0.14, 0.21)),
    C('fire_chunks', 'fire_chunks', [160, 100, '$t', '$t0'], {}, py='adapter:fire_chunks', times=(0.05, 0.15, 0.3, 0.45)),
    # ---- 闪光、魔法
    C('sparkles', 'sparkles', [160, 90, '$t'], dict(n=8, radius=20), times=(0, 0.2, 0.4, 0.6)),
    C('glint', 'glint', [160, 90, '$t', '$t0'], dict(size=8), times=(0.05, 0.15, 0.25, 0.4)),
    C('glow', 'glow', [160, 90, 40, '#ff8a30'], {},
      cols=[dict(kw=dict(alpha=0.6)), dict(kw=dict(alpha=0.9)), dict(kw=dict(alpha=0.6, add=True)), dict(kw=dict(alpha=0.5, levels=4))]),
    C('hamon', 'hamon', [100, 100, 220, 110, '$t'], dict(strands=2), times=(0, 0.06, 0.12, 0.3)),
    C('lightning', 'lightning', [60, 20, 260, 160, '$t'], {}, times=(0, 0.09, 0.17, 0.25), pri=P1),
    # ---- 替身能力
    C('emerald_splash', 'emerald_splash', [80, 100, 260, 90, '$t', '$t0', '$t1'], dict(n=24, spread=20, speed=320), t1=0.4,
      times=(0.1, 0.25, 0.45, 0.7)),
    C('tendrils', 'tendrils', [[[40, 60], [160, 100], [280, 70]], '$t'], dict(colour='#50e890', wiggle=2.0), times=(0, 0.3, 0.6, 0.9)),
    C('vines purple', 'vines', [60, 150, 260, 60, '$t', '$t0', '$t1'], dict(colour='purple'), t1=0.4, times=(0.1, 0.25, 0.5, 1.0)),
    C('vines 火绳 thorns ×', 'vines', [60, 150, 260, 60, '$t', '$t0', '$t1'], dict(colour=['#5a0c1c', '#e8501a', '#ffd840', '#ff9820'], thorns=False),
      t1=0.4, times=(0.1, 0.25, 0.5, 1.0)),
    C('water_gush', 'water_gush', [92, 110, '$t', '$t0'], dict(direction=1, strength=1.0, ground=150), bg='jail', times=(0.1, 0.3, 0.6, 1.0)),
    C('water_splash', 'water_splash', [160, 140, '$t', '$t0'], {}, times=(0.05, 0.2, 0.4, 0.7), pri=P1),
    C('knives', 'knives', [[[100, 90, 0], [140, 100, 30], [180, 110, -20]], '$t'], {}, pri=P1,
      cols=[dict(kw=dict()), dict(kw=dict(frozen=True)), dict(kw=dict(streak=24)), dict(kw=dict(frozen=True), t=0.33)]),
    # ---- 时停
    C('timestop yellow', 'timestop', ['$t', '$t0', 160, 90], dict(dur=0.6, tint='yellow'), pre=CREW, times=(0.1, 0.3, 0.45, 0.8)),
    C('timestop blue', 'timestop', ['$t', '$t0', 160, 90], dict(dur=0.7, tint='blue'), pre=CREW, times=(0.12, 0.35, 0.5, 0.9)),
    C('time_resume', 'time_resume', ['$t', '$t0', 160, 90], dict(dur=0.6), pre=CREW, times=(0.1, 0.25, 0.4, 0.55)),
    C('timestop_world', 'timestop_world', [], {}, pre=CREW,
      cols=[dict(kw=dict(amount=0.35, tint='yellow')), dict(kw=dict(tint='yellow')), dict(kw=dict(tint='blue')), dict(kw=dict(tint='gray'))]),
    # ---- 滤镜、转场、背景
    C('vignette', 'vignette', [], {}, cols=[dict(kw=dict(amount=0.3)), dict(kw=dict(amount=0.6)), dict(kw=dict(amount=0.9)),
                                             dict(kw=dict(amount=0.5, colour='#5a0010'))]),
    C('sepia', 'sepia', [], {}, pre=CREW, cols=[dict(kw=dict(amount=a)) for a in (0.25, 0.5, 0.75, 1.0)]),
    C('dim_bg', 'dim_bg', ['$a'], {}, py='adapter:dim_bg', cols=[dict(a=a) for a in (0.2, 0.45, 0.7, 0.9)]),
    C('slash_wipe', 'slash_wipe', ['$a'], dict(angle=22), cols=[dict(a=a) for a in (0.2, 0.45, 0.7, 0.9)]),
    C('iris', 'iris', ['$a'], {}, cols=[dict(a=a) for a in (0.2, 0.5, 0.8, 0.95)], pri=P1),
    C('diamond_wipe', 'diamond_wipe', ['$a'], {}, cols=[dict(a=a) for a in (0.2, 0.4, 0.6, 0.8)], pri=P1),
    C('menace_bg', 'menace_bg', ['$t'], dict(colours=['#402060', '#200830', '#5a2490']), times=(0, 0.09, 0.5, 1.0)),
    C('radial_burst_bg', 'radial_burst_bg', ['$t'], dict(colours=['#5a2aa0', '#34146a', '#46208a'], n=22, spin=0.35), times=(0, 0.1, 0.3, 0.6)),
    C('ora_bg', 'ora_bg', ['$t', 170, 104], {}, py='adapter:ora_bg', times=(0, 0.06, 0.12, 0.3)),
    # ---- 替身
    C('stand_summon', 'stand_summon', ['starplat', 'idle', 160, 150, '$t', '$t0'], dict(aura_colour='#b090ff'),
      py_pos=['starplat.idle', 160, 150, '$t', '$t0'], times=(0.05, 0.15, 0.3, 0.5)),
    C('stand_out', 'stand_out', ['starplat', 'idle', 160, 150, '$t', '$t0'], {}, py='adapter:stand_out', times=(0, 0.06, 0.12, 0.2)),
    C('aura_flame', 'aura_flame', ['jotaro.pose', 160, 160, '$t'], dict(colour='#c8a0ff', intensity=1.0, scale=2, height=10, grow=2),
      post=[S('jotaro.pose', 160, 160, scale=2)], times=TS),
    C('shatter', 'shatter', ['starplat.idle', 160, 150, '$t', '$t0'], dict(pieces=30, dur=0.9, tint_to='#fff4c0'), times=(0.03, 0.15, 0.4, 0.7)),
    C('crack', 'crack', [160, 90, '$t', '$t0'], dict(size=30, hi='#ffffff'), times=(0.05, 0.12, 0.2, 0.4)),
    C('slash_arc', 'slash_arc', [160, 100, '$t', '$t0'], dict(size=15), py='adapter:slash_arc', times=(0.01, 0.03, 0.06, 0.09)),
    C('blade_ext + coins', 'blade_ext', [210, 150], {}, py='adapter:blade_ext', pre=[S('chariot.thrust', 210, 150, frame=1, flip=True)],
      post=[dict(fn='coin_on_blade', pos=[210, 150, i], kw={}, py='adapter:coin_on_blade') for i in range(5)], times=(0, 0, 0, 0)),
    C('cap_shadow', 'cap_shadow', [160, 176, '$t', '$t0'], dict(scale=3), py='adapter:cap_shadow', bg='gray',
      pre=[S('jotaro.pose', 160, 176, frame=1, scale=3)], times=(-0.1, 0.12, 0.2, 0.3)),
    # ---- 场景氛围（M1 用到 petals / smoke；其余后面章节）
    C('petals', 'petals', ['$t'], {}, bg='gray', times=(0, 0.5, 1.0, 1.5)),
    C('draw_route 东京→香港', 'draw_route', [['东京', '香港'], '$t', '$t0', '$t1'], dict(vehicle='plane'), py='adapter:draw_route',
      bg='map', t1=1.35, times=(0.2, 0.6, 1.0, 1.5)),
    C('rain', 'rain', ['$t'], dict(ground=150), times=(0, 0.1, 0.2, 0.3), pri=EX),
    C('sand_wind', 'sand_wind', ['$t'], {}, bg='gray', times=(0, 0.2, 0.4, 0.6), pri=EX),
    C('fog', 'fog', ['$t'], dict(density=0.65), times=(0, 1, 2, 3), pri=EX),
    C('stars', 'stars', ['$t'], {}, bg='gray', times=(0, 0.3, 0.6, 0.9), pri=EX),
    C('bubbles', 'bubbles', ['$t', 100, 40, 220, 170], {}, times=(0, 0.5, 1.0, 1.5), pri=EX),
    C('void_sphere', 'void_sphere', [160, 100, 18, '$t'], {}, times=(0, 0.25, 0.5, 0.75), pri=EX),
    C('bats', 'bats', ['$t', '$t0', 160, 110], {}, times=(0.1, 0.4, 0.8, 1.4), pri=EX),
    C('clock', 'clock', [160, 90, 30, 3, 40], {}, cols=[dict(kw=dict()), dict(kw=dict(cracked=0.3)), dict(kw=dict(cracked=0.7)),
                                                     dict(kw=dict(cracked=1.0))], pri=EX),
    C('heat_haze', 'heat_haze', ['$t', 60, 180], dict(amp=2), times=TS, pri=EX),
    C('shooting_star', 'shooting_star', ['$t', '$t0', 40, 20, 280, 90], {}, times=(0.1, 0.3, 0.5, 0.7), pri=EX),
    C('light_beam', 'light_beam', [100, 160, 0, 180, '$t'], {}, times=(0, 0.5, 1.0, 1.5), pri=P1),
    # ---- 新增（原片没有）
    C('zone_warn rect', 'zone_warn', [120, 140, 200, 170, '$t', '$t0'], dict(dur=0.67), py='-', times=(0.05, 0.2, 0.4, 0.6)),
    C('zone_warn ellipse', 'zone_warn', [130, 140, 190, 160, '$t', '$t0'], dict(dur=0.67, shape='ellipse', colour='#ff6020'), py='-',
      times=(0.03, 0.2, 0.4, 0.6)),
    C('warn_line bezier', 'warn_line', [[[40, 120], [160, 30], [280, 130]], '$t', '$t0'], dict(grow=0.15, dur=0.6), py='-',
      times=(0.03, 0.08, 0.2, 0.5)),
    C('flame_pointer 30°', 'flame_pointer', [160, 120, '$t', '$t0'], dict(angle=30), py='-', pre=[S('avdol.idle', 160, 150)],
      times=(0.2, 0.5, 0.8, 1.05)),
    C('scent_line', 'scent_line', [[[60, 160], [120, 150], [200, 165], [280, 140]], '$t', '$t0'], {}, py='-', times=(0.2, 0.6, 1.5, 2.6)),
    C('firerope (wrap)', 'firerope', [160, 150, '$t', '$t0'], {}, py='-', pre=[S('jotaro.idle', 160, 150)], times=(0.03, 0.08, 0.3, 0.6)),
    C('wrap vine / tendril', 'wrap', [160, 150, '$t', '$t0'], {}, py='-', pre=[S('kakyoin.idle', 160, 150)],
      cols=[dict(t=0.05, kw=dict(kind='vine')), dict(t=0.4, kw=dict(kind='vine')), dict(t=0.05, kw=dict(kind='tendril')),
            dict(t=0.4, kw=dict(kind='tendril'))]),
    C('gem / summon_lines', 'gem', [160, 90], {}, py='-',
      cols=[dict(kw=dict(kind='emerald', size=2)), dict(kw=dict(kind='ice', size=2, vx=-300, vy=0)), dict(kw=dict(kind='ruby', size=1, vx=200, vy=-100)),
            dict(kw=dict(kind='emerald', size=0))],
      post=[dict(fn='summon_lines', pos=[160, 150, '$t', '$t0'], kw=dict(colour='#70ffb0'), py='-')]),
    C('inhale_stream', 'inhale_stream', [110, 130, '$t', '$t0'], dict(cx=245, cy=60), py='-', times=(.05,.2,.6,1.05)),
    C('fire_burst', 'fire_burst', [160, 125, '$t', '$t0'], dict(size=24), py='-', times=(.03,.15,.35,.6)),
]


def dump_js(path):
    js = 'window.P2_T0 = %r;\nwindow.P2_CASES = %s;\n' % (T0, json.dumps(CASES, ensure_ascii=False, indent=0))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(js)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, '_out'), exist_ok=True)
    dump_js(os.path.join(here, '_out', 'cases.js'))
    print(len(CASES), 'cases →', os.path.join(here, '_out', 'cases.js'))
