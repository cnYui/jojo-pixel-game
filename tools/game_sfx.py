"""JoJo 游戏的新合成音效（包 1）。

只用原工程 `源码/engine/sfx.py` 的辅助函数，运行时用 `sfx._reg` 登记新名字（源码一个字不改）。
起点是调研报告 07 附录 A 的原型（照搬后改了几处响度），再补上技术约定 §3.14 G / 规划 §7.3 要的其余新音效。

    import game_sfx            # 登记新名字到 engine.sfx
    from engine import sfx
    sfx.make('ora_loop')

规则（报告 07 §7）：
  * 循环音效（名字以 _loop / _hum 结尾）**不吃 dur**：sfx._build 只要收到 dur 就会 _fit，把最后 30 ms 淡出，接缝就坏了。
    它们用 `loop`（秒）参数，最后用 _fin_loop（只减均值 + 归一，不切尾、不淡入淡出）。
  * 循环里的滤波用 FFT 圆周滤波 _cband、持续音的频率吸附成循环内整数周期（_per），首尾才接得上。
  * 原工程那些 dur 型的环境音（fire / crowd / wind / plane_engine）要循环时，用 _xfade_loop：
    多生成一段，跳过开头的淡入，再把尾巴等功率交叉淡化到开头。
  * 新音效同时登记感知响度目标 sfx._LA（和必要时的 sfx._PUSH_MAX），否则响度和老音效对不齐。
"""
import sys

sys.dont_write_bytecode = True

import os  # noqa: E402

import numpy as np  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.normpath(os.path.join(_HERE, '..', '..', '源码'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from engine import sfx  # noqa: E402
from engine.sfx import (SR, _TAU, _chirp, _clicks, _cymbal, _dsig, _fin, _formant, _hit, _kick,  # noqa: E402
                        _metal, _n, _pan, _ping, _place, _reg, _rng, _seq, _st, _t, _warp, bp, delay,
                        env_exp, env_pts, fade, hp, lp, nf, noise, norm, osc, sat, snh, sweep, verb)

GAME = {}            # 新名字 -> 说明（只有本文件登记的）
LOOP = {}            # 循环音效 -> 循环秒数


def reg(name, desc, la=None, push=None, loop=None, hit=None):
    """登记一个新音效：sfx._reg + 响度目标 + 同步点。"""
    def deco(f):
        _reg(name, desc)(f)
        GAME[name] = desc
        if la is not None:
            sfx._LA[name] = la
        if push is not None:
            sfx._PUSH_MAX[name] = push
        if loop:
            LOOP[name] = loop
        if hit is not None:
            sfx.HIT[name] = hit
        return f
    return deco


# ============================================================ 循环（圆周）工具
def _fold(x, L):
    """把超过 L 个样本的尾巴折回开头（循环的余音）。"""
    y = x[:L].copy()
    r = x[L:]
    while len(r):
        m = min(L, len(r))
        y[:m] += r[:m]
        r = r[m:]
    return y


def _cband(x, lo=None, hi=None):
    """FFT 圆周滤波（Butterworth 幅度响应），循环不留接缝。"""
    L = len(x)
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(L, 1 / SR)
    f[0] = 1e-6
    H = np.ones_like(f)
    if lo:
        H /= np.sqrt(1 + (lo / f) ** 4)
    if hi:
        H /= np.sqrt(1 + (f / hi) ** 4)
    H[0] = 0
    return np.fft.irfft(X * (H[:, None] if x.ndim == 2 else H), L, axis=0)


def _fin_loop(x, peak):
    """循环收尾：精确去直流（减均值）+ 峰值归一；不切尾、不淡入淡出。"""
    x = np.asarray(x, np.float64)
    x = x - x.mean(axis=0)
    return norm(x, peak)


def _per(f, L):
    """把频率吸附到“L 个样本里正好整数个周期”。"""
    return max(1, round(f * L / SR)) * SR / L


def _xfade_loop(x, L, X, lead):
    """把一段长的、首尾有淡入淡出的录音做成 L 个样本的无缝循环。
    取 x[lead : lead+L+X]，最后 X 个样本等功率交叉淡化到开头。"""
    raw = np.asarray(x[lead:lead + L + X], np.float64)
    out = raw[:L].copy()
    u = np.linspace(0, 1, X, endpoint=False)
    w_in, w_out = np.sin(0.5 * np.pi * u), np.cos(0.5 * np.pi * u)
    if raw.ndim == 2:
        w_in, w_out = w_in[:, None], w_out[:, None]
    out[:X] = raw[:X] * w_in + raw[L:L + X] * w_out
    return out - out.mean(axis=0)


def _amb_loop(src, loop, peak=None, **kw):
    """原工程 dur 型环境音 -> 无缝循环（保留原来的响度）。"""
    L, X, lead, pad = _n(loop), _n(0.4), _n(0.6), _n(0.7)
    x = sfx.make(src, dur=(L + X + lead + pad) / SR, **kw)
    y = _xfade_loop(x, L, X, lead)
    return norm(y, peak) if peak else y


# ============================================================ 连打（循环）
def _barrage_loop(name, loop, rate, dark, seed):
    rng = _rng(name, seed)
    L = _n(loop)
    k = max(2, int(round(loop * rate)))
    k += k % 2                                   # 偶数拳：左右交替跨接缝不乱
    per = L / k
    if dark:
        base = dict(f0=175, f1=58, drop=0.03, tau=0.05, bright=1700, smack=0.6, slap=1.7,
                    slap_lp=1900, slap_tau=0.028, drive=3.4, tri=0.4, knock=1.2)
    else:
        base = dict(f0=260, f1=75, drop=0.022, tau=0.042, bright=5200, smack=0.9, slap=1.2,
                    slap_lp=3200, slap_tau=0.022, drive=2.6, tri=0.2, knock=0.8)
    temps = []
    for _ in range(8):
        v = rng.uniform(0.86, 1.14)
        temps.append(_hit(dur=0.16, rng=rng, **dict(base, f0=base['f0'] * v, f1=base['f1'] * v)))
    out = np.zeros((L + _n(0.3), 2))
    for i in range(k):
        at = int(i * per + rng.uniform(-0.12, 0.12) * per)
        pan = (0.35 if i % 2 else -0.35) + rng.uniform(-0.12, 0.12)
        _place(out, _pan(temps[rng.integers(8)], pan), max(0, at), rng.uniform(0.82, 1.0))
    out = _fold(out, L)
    t = _t(L)
    fr = k / (L / SR)                                        # 底噪每个循环正好起伏 k 次
    bed = _cband(noise(L, rng), 150, 900) if dark else _cband(noise(L, rng), 500, 3200)
    bed *= 0.55 + 0.45 * np.sin(np.pi * fr * t) ** 2
    out += _st(bed) * (0.18 if dark else 0.14)
    if dark:
        dr = osc(_per(41.2, L), L, 'saw') + osc(_per(43.7, L), L, 'saw')
        out += _st(_cband(dr, None, 260)) * 0.07
    return _fin_loop(out, 0.88)


@reg('ora_loop', 'ORA barrage, seamless loop while J is mashed (loop=1.0 s, 16 hits/s, stereo)', loop=1.0)
def _ora_loop(loop=1.0, rate=16.0, seed=0):
    return _barrage_loop('ora_loop', float(loop), float(rate), False, seed)


@reg('muda_loop', 'MUDA barrage loop (DIO / dark enemies), seamless (loop=1.0 s, stereo)', loop=1.0)
def _muda_loop(loop=1.0, rate=16.0, seed=0):
    return _barrage_loop('muda_loop', float(loop), float(rate), True, seed)


@reg('rapier_loop', 'Silver Chariot thrust barrage: swish + tink 18/s, seamless (loop=1.0 s, stereo)', loop=1.0)
def _rapier_loop(loop=1.0, rate=18.0, seed=0):
    rng = _rng('rapier_loop', seed)
    L = _n(loop)
    k = int(round(loop * rate))
    k += k % 2
    per = L / k
    out = np.zeros((L + _n(0.3), 2))
    for i in range(k):
        sn = _n(0.035)
        sw = sweep(noise(sn, rng), _dsig(sn, 2000, 7500), 'bp', q=1.6) * np.sin(np.pi * np.linspace(0, 1, sn)) ** 2
        tk = _metal(_n(0.12), np.array([3200, 4700, 6100]) * rng.uniform(0.94, 1.06), [0.03, 0.022, 0.015],
                    [1, .6, .4], rng, 0.004)
        one = np.zeros(_n(0.16))
        _place(one, sw, 0, 0.9)
        _place(one, tk, _n(0.03), 0.45)
        at = int(i * per + rng.uniform(-0.1, 0.1) * per)
        _place(out, _pan(one, (0.3 if i % 2 else -0.3) + rng.uniform(-0.1, 0.1)), max(0, at), rng.uniform(0.8, 1))
    return _fin_loop(_fold(out, L), 0.8)


# ============================================================ 时停
@reg('timestop_hum', 'Stopped-time drone "嗡": frozen gong partials + sub + airy shimmer, seamless (loop=4 s, stereo)',
     loop=4.0)
def _timestop_hum(loop=4.0, seed=0):
    rng = _rng('timestop_hum', seed)
    L = _n(loop)
    t = _t(L)
    f = 73.4
    x = np.zeros(L)
    for r, a in zip([1.0, 2.0, 2.41, 2.98, 4.07], [1.0, 0.55, 0.4, 0.3, 0.18]):
        for d in (0.997, 1.003):                   # 慢拍频，吸附成整数周期
            x += a * osc(_per(f * r * d, L), L, ph0=rng.uniform())
    x *= 0.8 + 0.2 * np.sin(_TAU * (2 / (L / SR)) * t)            # 每个循环起伏 2 次
    sub = osc(_per(36.7, L), L) * 0.8
    air = _cband(noise(L, rng), 2500, 6000) * (0.5 + 0.5 * np.sin(_TAU * (1 / (L / SR)) * t) ** 2) * 0.25
    left = x + sub + air
    right = np.roll(x, L // 3) + sub + np.roll(air, L // 2)
    return _fin_loop(np.stack([left, right], -1), 0.5)


# ============================================================ 其他循环（低血、灰塔、环境）
@reg('heartbeat_loop', 'Low-HP heartbeat, 110 bpm lub-dub, seamless (loop = 2 beats ≈ 1.09 s)', loop=120 / 110)
def _heartbeat_loop(seed=0):
    per = 60.0 / 110.0
    L = _n(2 * per)
    one = sfx.make('heartbeat', n=1, bpm=110, seed=seed)
    out = np.zeros(L + len(one) + _n(per))
    _place(out, one, 0)
    _place(out, one, _n(per), 0.92)
    return _fin_loop(_fold(out, L), 0.9)


@reg('insect_buzz_loop', 'Tower of Gray stag-beetle buzz: FM square + 30 Hz wing AM, seamless (loop=2 s)', loop=2.0)
def _insect_buzz_loop(loop=2.0, seed=0):
    rng = _rng('insect_buzz_loop', seed)
    L = _n(loop)
    t = _t(L)
    Ls = L / SR
    out = np.zeros(L)
    for f0, g, duty in ((220.0, 1.0, 0.3), (331.0, 0.45, 0.22)):
        # 周期性的频率摆动（几条整数周期的正弦）——相位积分在一个循环里正好整数圈
        m = np.zeros(L)
        for nk in (3, 7, 13):
            m += rng.uniform(0.3, 1.0) * np.sin(_TAU * nk / Ls * t + rng.uniform(0, _TAU))
        m /= np.abs(m).max() + 1e-9
        fc = _per(f0, L)
        ph = np.cumsum(fc * (1 + 0.05 * m)) / SR
        ph *= round(ph[-1]) / ph[-1]
        p = ph % 1.0
        out += g * (np.where(p < duty, 1.0, -1.0) - (2 * duty - 1))
    am = 0.6 + 0.4 * np.sin(_TAU * _per(30.0, L) * t)
    am2 = 0.85 + 0.15 * np.sin(_TAU * (2 / Ls) * t)
    x = _cband(out * am * am2, 400, 3000)
    x += 0.12 * _cband(noise(L, rng), 2500, 7000) * am
    return _fin_loop(x, 0.5)


@reg('fire_loop', 'Flame roar with crackles, seamless loop of the original `fire` (loop=3 s)', loop=3.0)
def _fire_loop(loop=3.0, seed=0):
    return _amb_loop('fire', float(loop), seed=seed)


@reg('crowd_loop', 'Street crowd murmur, seamless loop of the original `crowd` (loop=6 s, stereo)', loop=6.0)
def _crowd_loop(loop=6.0, seed=0):
    return _amb_loop('crowd', float(loop), seed=seed)


@reg('wind_loop', 'Gusting wind, seamless loop of the original `wind` (loop=6 s, stereo)', loop=6.0)
def _wind_loop(loop=6.0, seed=0):
    return _amb_loop('wind', float(loop), seed=seed)


@reg('plane_engine_loop', 'Airliner cabin drone, seamless loop of the original `plane_engine` (loop=6 s, stereo)',
     loop=6.0)
def _plane_engine_loop(loop=6.0, seed=0):
    return _amb_loop('plane_engine', float(loop), seed=seed)


# ============================================================ 命中 / 防守 / 移动
@reg('dodge', 'Dodge dash: tight swish + afterimage echoes (0.35 s)', la=-16)
def _dodge(seed=0):
    rng = _rng('dodge', seed)
    n = _n(0.22)
    u = np.linspace(0, 1, n)
    c = 700 * (6000 / 700) ** (np.sin(np.pi * np.clip(u / 0.8, 0, 1)) ** 1.2)
    x = sweep(noise(n, rng), c, 'bp', q=1.5) * np.sin(np.pi * u) ** 1.6
    m = _n(0.04)
    x[:m] += 0.25 * _chirp(m, 1800, 900, 0.015, 'square', 0.25, 0.001)
    x = delay(x, 0.045, fb=0.45, taps=3, lpf=5000)                   # 残影回声
    return _fin(x, 0.6, 0.002, 0.03)


@reg('dodge_perfect', 'Perfect dodge -> bullet time: dodge + reverse cymbal rising into a low whump at +0.3 s',
     la=-15, hit=0.3)
def _dodge_perfect(seed=0):
    rng = _rng('dodge_perfect', seed)
    hit = 0.3
    n = _n(1.2)
    x = np.zeros((n, 2))
    _place(x, _st(sfx.make('dodge')), 0, 0.8)
    cn = _n(0.4)
    cy = _cymbal(cn, rng, 0.3, 3000)[::-1]
    tt = _t(cn)
    cy = cy * np.exp((tt - tt[-1]) / 0.1)
    _place(x, _st(cy), _n(hit) - cn, 0.55)
    m = n - _n(hit)
    boom = osc(_dsig(m, 90, 40), m) * env_exp(m, 0.2, 0.002) * 0.6
    boom += 0.35 * _ping(m, nf('E6'), 0.25, 0.001, ((1, 1), (2.0, 0.3)))
    _place(x, _st(boom), _n(hit))
    x = verb(x, wet=0.3, sec=0.9, tau=0.25, lpf=6000, seed=27)
    return _fin(x, 0.8, 0.002, 0.12)


@reg('guard', 'Stand guard: dull metallic clank + short ring (0.5 s)', la=-15, push=8)
def _guard(seed=0):
    rng = _rng('guard', seed)
    n = _n(0.45)
    x = _hit(320, 140, 0.01, 0.03, 0.45, rng, bright=5000, smack=0.9, slap=0.6, slap_lp=2500,
             slap_tau=0.015, drive=3.0, knock=0.5)
    ring = _metal(n, [520, 1180, 1730, 2650], [0.12, 0.09, 0.07, 0.05], [1, .8, .6, .4], rng, 0.006)
    x = x + 0.6 * ring + 0.4 * bp(noise(n, rng), 2000, 6000) * env_exp(n, 0.01, 0.0003)
    x = verb(x, wet=0.12, sec=0.4, tau=0.08, lpf=6000, seed=21)
    return _fin(x, 0.85, 0.0005, 0.04)


@reg('parry', 'Perfect guard "KIIN": bright long metal ring + snap (0.9 s)', la=-14)
def _parry(seed=0):
    rng = _rng('parry', seed)
    n = _n(0.9)
    ring = _metal(n, [2093, 3140, 4400, 5870], [0.45, 0.3, 0.2, 0.12], [1, .7, .5, .3], rng, 0.002)
    ring *= np.minimum(_t(n) / 0.001, 1)
    x = 0.8 * ring + 0.35 * _ping(n, 4186, 0.25, 0.001, ((1, 1), (1.5, 0.3)))
    x += 0.7 * hp(noise(n, rng), 3000) * env_exp(n, 0.006, 0.0002)
    x += 0.5 * osc(_dsig(n, 160, 70), n) * env_exp(n, 0.04, 0.001)
    x = verb(x, wet=0.2, sec=0.8, tau=0.2, lpf=9000, seed=22)
    return _fin(x, 0.8, 0.0005, 0.1)


@reg('guard_break', 'Guard broken: lowered glass shatter + thud + low metal (0.9 s, stereo)', la=-13)
def _guard_break(seed=0):
    rng = _rng('guard_break', seed)
    n = _n(1.0)
    x = np.zeros((n, 2))
    _place(x, _st(sfx.make('glass_break', pitch=0.8)), 0, 0.8)
    _place(x, _st(sfx.make('thud')), 0, 0.9)
    m = _n(0.8)
    _place(x, _st(_metal(m, [300, 700, 1100], [0.3, 0.2, 0.15], [1, .8, .6], rng, 0.005)), 0, 0.5)
    return _fin(sat(x, 1.3), 0.9, 0.0005, 0.12)


@reg('crit', 'Critical hit: heavy body + glassy crack + ring (0.9 s, stereo)', la=-11, push=8)
def _crit(seed=0):
    rng = _rng('crit', seed)
    n = _n(0.6)
    x = _hit(210, 46, 0.045, 0.14, 0.6, rng, bright=4500, smack=1.1, slap=1.7, slap_lp=3000,
             slap_tau=0.05, drive=3.8, sub=0.3, knock=1.1)
    x += 0.6 * hp(noise(n, rng), 3000) * env_exp(n, 0.006, 0.0002)
    x += 0.35 * _metal(n, [1900, 2870, 4100], [0.2, 0.15, 0.1], [1, .7, .5], rng, 0.004)
    x += 0.5 * bp(snh(n, 6000, rng), 300, 5000) * env_exp(n, 0.04, 0.0005)
    x = verb(sat(x, 1.8), wet=0.2, sec=0.7, tau=0.15, lpf=5000, seed=23)
    return _fin(x, 0.92, 0.0005, 0.08)


@reg('ko_hit', 'KO finisher: huge punch + gong + boom, slow-motion warped tail (2.6 s, stereo)', la=-11, push=7)
def _ko_hit(seed=0):
    rng = _rng('ko_hit', seed)
    n = _n(2.2)
    x = _hit(150, 32, 0.07, 0.35, 2.2, rng, bright=3500, smack=1.2, slap=2.0, slap_lp=2800,
             slap_tau=0.08, drive=4.0, sub=0.6, knock=1.2)
    x += 0.6 * bp(snh(n, 5500, rng), 300, 5000) * env_exp(n, 0.06, 0.0005)
    g = _metal(n, [73.4 * r for r in (1.0, 2.0, 2.41, 2.98, 4.07)], [1.2, 0.8, 0.7, 0.5, 0.4],
               [1.0, .7, .55, .5, .4], rng, 0.0025)
    x += 0.5 * g * np.minimum(_t(n) / 0.004, 1)
    spd = np.interp(np.linspace(0, 1, n), [0, 0.15, 1], [1.0, 1.0, 0.45])     # 慢动作下沉
    x = fade(_warp(sat(x, 1.5), spd), 0.0, 0.5)          # 先淡出再进混响（不然 2.2 s 处硬切）
    x = verb(x, wet=0.3, sec=1.6, tau=0.45, lpf=3500, seed=24)
    return _fin(x, 0.92, 0.0005, 0.3)


@reg('wall_slam', 'Knocked into a wall / slammed to the ground: deep hit + rubble + short rumble (0.7 s)', la=-12)
def _wall_slam(seed=0):
    rng = _rng('wall_slam', seed)
    n = _n(0.7)
    x = np.zeros(n)
    _place(x, _hit(120, 40, 0.05, 0.2, 0.6, rng, bright=3500, smack=1.0, slap=1.4, slap_lp=2400,
                   slap_tau=0.05, drive=3.0, sub=0.5, knock=0.8), 0)
    x += 0.8 * _clicks(n, 60, rng, (1, 5), 900, env_exp(n, 0.3))
    _place(x, sfx.make('rumble', dur=0.6) * 0.4, 0)
    return _fin(x, 0.9, 0.0005, 0.08)


@reg('skid', 'Knocked back, skidding along the ground: falling band-passed scrape + grit (0.4 s)', la=-19)
def _skid(dur=0.4, seed=0):
    rng = _rng('skid', seed)
    n = _n(dur)
    x = sweep(noise(n, rng), _dsig(n, 2500, 700), 'bp', q=2.0) * env_pts(n, [(0, 0), (0.02, 1), (dur, 0)])
    x += 0.6 * _clicks(n, 40, rng, (0.5, 2.5), 1200, env_pts(n, [(0, 1), (dur, 0.2)]))
    return _fin(x, 0.6, 0.002, 0.05)


# ============================================================ 替身 / 能量 / 必杀
_SUMMON = {   # 和弦（锯齿）, 配色层
    'star': (('E2', 'B2', 'E3', 'G#3', 'B3'), 'punch'),
    'hiero': (('G3', 'D4', 'G4', 'B4', 'D5'), 'chime'),
    'chariot': (('A2', 'E3', 'A3', 'C#4', 'E4'), 'shing'),
    'red': (('D2', 'A2', 'D3', 'F#3', 'A3'), 'fire'),
    'purple': (('C3', 'G3', 'C4', 'E4', 'G4'), 'vine'),
    'fool': (('F2', 'C3', 'F3', 'A3', 'C4'), 'sand'),
    'world': (('C2', 'G2', 'C3', 'Eb3', 'G3'), 'gong'),
}


@reg('stand_summon', 'Stand appears: rising swish + glide -> chord stab + colour layer at +0.25 s (kind=star..world)',
     la=-14, push=8, hit=0.25)
def _stand_summon(kind='star', seed=0):
    rng = _rng('stand_summon_' + str(kind), seed)
    notes, colour = _SUMMON.get(kind, _SUMMON['star'])
    hit = 0.25
    n = _n(1.4)
    x = np.zeros(n)
    pn = _n(hit)
    u = np.linspace(0, 1, pn)
    sw = sweep(noise(pn, rng), 400 * (6000 / 400) ** u, 'bp', q=1.3) * u ** 2
    gl = sum(osc(nf(s) * 0.5 * 2 ** u, pn, 'saw') for s in notes[:3]) * u ** 2 * 0.25
    _place(x, sw + lp(gl, 3000), 0)
    m = n - pn
    ch = sum(osc(nf(s) * rng.uniform(0.998, 1.002), m, 'saw') for s in notes) * 0.3
    ch = sweep(ch, 700 + 5000 * np.exp(-_t(m) / 0.15), 'lp', q=1.0) * env_exp(m, 0.4, 0.003)
    _place(x, ch, pn, 0.9)
    _place(x, _kick(0.4, 140, 40, 0.13), pn, 1.0)
    if colour == 'punch':
        _place(x, _hit(230, 62, 0.03, 0.07, 0.3, rng, knock=0.8, slap=1.2), pn, 0.6)
    elif colour == 'chime':
        _place(x, _metal(m, [3136, 3951, 4699, 6272], [.3, .25, .2, .15], [1, .8, .6, .4], rng, 0.002), pn, 0.4)
    elif colour == 'shing':
        _place(x, _metal(m, [2210, 3470, 5130, 7020], [.25, .18, .12, .08], [1, .7, .5, .35], rng, 0.004), pn, 0.45)
    elif colour == 'fire':
        _place(x, sfx.make('fire_burst')[:, 0] * 0.6, pn - _n(0.05))
    elif colour == 'vine':
        _place(x, sfx.make('vine', dur=0.6) * 0.6, pn)
    elif colour == 'sand':
        _place(x, sfx.make('sand', dur=0.8) * 0.7, pn)
    elif colour == 'gong':
        _place(x, _metal(m, [73.4 * r for r in (1, 2, 2.41, 2.98)], [1.2, .8, .7, .5], [1, .7, .5, .4], rng), pn, 0.5)
    _place(x, _cymbal(m, rng, 0.5, 4500), pn, 0.25)
    x = verb(x, wet=0.22, sec=0.9, tau=0.2, lpf=6000, seed=25)
    return _fin(x, 0.9, 0.001, 0.15)


@reg('stand_recall', 'Stand withdraws: falling swish + chord glide down + soft pop (0.4 s)', la=-18)
def _stand_recall(seed=0):
    rng = _rng('stand_recall', seed)
    n = _n(0.4)
    u = np.linspace(0, 1, n)
    x = sweep(noise(n, rng), 6000 * (400 / 6000) ** u, 'bp', q=1.3) * np.sin(np.pi * np.clip(u * 1.2, 0, 1)) ** 1.5
    gl = sum(osc(nf(s) * 2 ** (-u), n, 'saw') for s in ('E4', 'B4', 'E5')) * (1 - u) ** 1.5 * 0.2
    x = x + lp(gl, 3500)
    _place(x, sfx.make('pop') * 0.5, n - _n(0.12))
    return _fin(x, 0.5, 0.002, 0.04)


@reg('meter_tick', 'Stand energy +1 notch: high blip (1320 Hz); runtime rate rises with the meter', la=None)
def _meter_tick():
    return sfx.make('blip', freq=1320)


@reg('meter_full', 'Stand energy full: quick chip arpeggio + shimmer ping (0.8 s)', la=-17)
def _meter_full(seed=0):
    seq = [(k * 0.03, 0.028, nf(s), 0.8) for k, s in enumerate(['E6', 'G#6', 'B6', 'E7'])]
    x = _seq(seq, 0.8, 'square', 0.125, a=0.001, d=0.04, s=0.6, r=0.02)
    pn = _n(0.6)
    pg = _ping(pn, nf('E7'), 0.22, 0.001, ((1, 1.0), (2.0, 0.25)))
    pg *= 1 + 0.4 * np.sin(_TAU * 24 * _t(pn))
    _place(x, pg, _n(0.12), 0.5)
    sn = _n(0.15)
    _place(x, _chirp(sn, 1200, 2400, 0.08, 'sine', attack=0.01), 0, 0.25)
    return _fin(delay(x, 0.06, 0.3, 2), 0.5, 0.0005, 0.08)


@reg('super_start', 'Super move start: flash snap + rising cut-in swish -> minor stab at +0.5 s (1.8 s, stereo)',
     la=-13, hit=0.5)
def _super_start(seed=0):
    rng = _rng('super_start', seed)
    hit = 0.5
    n = _n(1.6)
    x = np.zeros(n)
    fn = _n(0.4)
    snap = hp(noise(fn, rng), 3000) * env_exp(fn, 0.04, 0.0005) * 0.7 + osc(_dsig(fn, 110, 45), fn) * env_exp(fn, 0.15)
    _place(x, snap, 0)
    rn = _n(hit)
    u = np.linspace(0, 1, rn)
    rise = sweep(noise(rn, rng), 300 * (8000 / 300) ** u, 'bp', q=1.6) * u ** 2
    rise += lp(osc(150 * (1200 / 150) ** u, rn, 'saw'), 4000) * 0.2 * u ** 2
    _place(x, rise, 0, 0.9)
    m = n - rn
    st = sum(osc(nf(s), m, 'saw') for s in ('A2', 'E3', 'A3', 'C4', 'E4')) * 0.35
    st = sweep(st, 800 + 5000 * np.exp(-_t(m) / 0.12), 'lp', q=1.0) * env_exp(m, 0.35, 0.003)
    _place(x, st, rn)
    _place(x, _kick(0.4, 150, 40, 0.14), rn)
    _place(x, _cymbal(m, rng, 0.45, 4000), rn, 0.3)
    x = verb(x, wet=0.2, sec=0.9, tau=0.2, lpf=6000, seed=26)
    return _fin(x, 0.85, 0.001, 0.15)


@reg('game_over_jingle', 'Defeat jingle before retrying: falling square melody + triangle bass, echo (2.5 s)', la=-17)
def _game_over_jingle(seed=0):
    rng = _rng('game_over_jingle', seed)
    total = 2.6
    mel = [(0.10, 0.17, nf('E5'), 0.9), (0.28, 0.17, nf('D5'), 0.9), (0.46, 0.17, nf('C5'), 0.9),
           (0.64, 0.17, nf('B4'), 0.9)]
    x = _seq(mel, total, 'square', 0.25, a=0.002, d=0.06, s=0.65, r=0.04)
    x += 0.95 * _seq([(0.82, 1.0, nf('A4'), 1.0)], total, 'square', 0.25, a=0.002, d=0.2, s=0.75, r=0.3,
                     vib=0.012, vib_rate=5.0, vib_delay=0.15)
    bass = [(0.10, 0.34, nf('A2'), 1.0), (0.46, 0.34, nf('E2'), 1.0), (0.82, 1.1, nf('A1'), 1.0)]
    x += 0.7 * _seq(bass, total, 'tri', 0.5, a=0.004, d=0.2, s=0.8, r=0.2)
    _place(x, sfx.make('thud') * 0.6, 0)
    x = delay(x, 0.15, 0.25, 2)
    x = verb(x, wet=0.2, sec=1.0, tau=0.3, lpf=6000, seed=28)
    _ = rng
    return _fin(x, 0.55, 0.001, 0.25)


# ============================================================ 主角招式 / 敌人
@reg('emerald_shot', 'Single Emerald Splash gem shot: crystalline chip "pew" + faint chime (0.3 s)', la=-17)
def _emerald_shot(seed=0):
    rng = _rng('emerald_shot', seed)
    n = _n(0.3)
    x = np.zeros(n)
    m = _n(0.11)
    f0 = rng.uniform(2000, 2800)
    pew = lp(_chirp(m, f0, f0 * 0.3, 0.04, 'square', 0.25, 0.001), 9000)
    _place(x, pew, 0)
    cn = _n(0.25)
    ch = _metal(cn, [3136, 4699, 6272], [0.08, 0.06, 0.05], [1, .7, .5], rng, 0.002)
    _place(x, ch, _n(0.01), 0.2)
    return _fin(x, 0.6, 0.0005, 0.03)


@reg('hiero_tentacle', 'Hierophant tentacle lash / bind: vine whip + wet formant squelch (0.5 s)', la=-18)
def _hiero_tentacle(seed=0):
    x = sfx.make('vine', dur=0.5, seed=seed) * 0.9
    wet = sfx.make('rero', dur=0.5, seed=seed) * 0.6
    y = np.zeros(max(len(x), len(wet)))
    _place(y, x, 0)
    _place(y, wet, _n(0.04))
    return _fin(y, 0.6, 0.002, 0.04)


@reg('crossfire', "Crossfire Hurricane: fire burst + whirling roar panning L->R + blast at +0.6 s (stereo)",
     la=-12, push=6)
def _crossfire(seed=0):
    rng = _rng('crossfire', seed)
    n = _n(3.6)
    x = np.zeros((n, 2))
    _place(x, sfx.make('fire_burst'), 0, 0.9)
    m = _n(0.6)
    u = np.linspace(0, 1, m)
    roar = sweep(noise(m, rng), 400 * (3000 / 400) ** u, 'bp', q=0.9) * np.sin(np.pi * np.clip(u * 1.1, 0, 1)) ** 1.2
    blk = 512
    sw = np.zeros((m, 2))
    for i in range(0, m, blk):
        seg = roar[i:i + blk]
        sw[i:i + len(seg)] = _pan(seg, -0.8 + 1.6 * (i / m))
    _place(x, sw, _n(0.05), 0.9)
    ex = sfx.make('explosion')
    _place(x, ex, _n(0.6), 0.5)
    return _fin(sat(x, 1.2), 0.92, 0.002, 0.3)


@reg('armor_off', 'Silver Chariot sheds its armour: plates clatter to the floor + whoosh + final shing (1.0 s)',
     la=-15)
def _armor_off(seed=0):
    rng = _rng('armor_off', seed)
    n = _n(1.2)
    x = np.zeros((n, 2))
    _place(x, _st(sfx.make('whoosh')), 0, 0.7)
    for i in range(7):
        st = 0.05 + i * 0.065 + rng.uniform(0, 0.03)
        m = _n(0.35)
        fs = rng.uniform(400, 1200) * np.array([1.0, rng.uniform(1.4, 1.9), rng.uniform(2.3, 3.1)])
        clank = _metal(m, fs, [rng.uniform(0.1, 0.2)] * 3, [1, .7, .5], rng, 0.006)
        clank += 0.5 * bp(noise(m, rng), 1500, 6000) * env_exp(m, 0.006, 0.0003)
        _place(x, _pan(clank, rng.uniform(-0.6, 0.6)), _n(st), rng.uniform(0.6, 1.0))
    sl = sfx.make('slash', seed=1)
    _place(x, _st(sl), _n(0.62), 0.8)
    return _fin(x, 0.85, 0.001, 0.1)


# ============================================================ UI
def _ui_notes(notes, step, kind='square', duty=0.25):
    seq = [(k * step, step * 0.9, nf(s), 1.0) for k, s in enumerate(notes)]
    return _seq(seq, step * len(notes) + 0.06, kind, duty, a=0.001, d=0.03, s=0.7, r=0.015)


@reg('menu_move', 'Menu cursor move: 25 ms chip tick (A5)', la=-24)
def _menu_move():
    return _fin(_ui_notes(['A5'], 0.025, 'chip', 0.25), 0.25, 0.0005, 0.004, dc=False)


@reg('menu_confirm', 'Menu confirm: E6 -> B6 two-note chip (0.12 s)', la=-21)
def _menu_confirm():
    return _fin(delay(_ui_notes(['E6', 'B6'], 0.045), 0.05, 0.25, 1), 0.3, 0.0005, 0.01, dc=False)


@reg('menu_cancel', 'Menu cancel / back: B5 -> E5 descending (0.12 s)', la=-22)
def _menu_cancel():
    return _fin(_ui_notes(['B5', 'E5'], 0.045), 0.28, 0.0005, 0.01, dc=False)


@reg('menu_error', 'Not allowed buzz: detuned low square (0.16 s)', la=-22)
def _menu_error():
    n = _n(0.16)
    x = (osc(110, n, 'chip', 0.5) + osc(116.5, n, 'chip', 0.5)) * env_pts(n, [(0, 0), (0.005, 1), (0.13, 0.8), (0.16, 0)])
    return _fin(lp(x, 3000, 1), 0.3, 0.0005, 0.01, dc=False)


# ============================================================ 人声（没有配音，全部共振峰合成；设置“喊声”默认关）
_VOICE = {   # f0 起, f0 止, 共振峰缩放, 噪声（沙哑）, drive
    'jotaro': (110, 82, 0.92, 0.25, 2.2), 'kakyoin': (150, 112, 1.0, 0.2, 2.0),
    'polnareff': (140, 100, 1.0, 0.3, 2.2), 'avdol': (95, 72, 0.9, 0.3, 2.4),
    'joseph': (135, 95, 1.0, 0.5, 2.0), 'enemy': (100, 70, 0.88, 0.45, 2.8), 'dio': (115, 80, 0.95, 0.4, 3.0),
}


@reg('grunt', 'Hurt grunt "UGH" by formant synthesis (voice=jotaro/kakyoin/polnareff/avdol/joseph/enemy/dio, 0.3 s)',
     la=-16)
def _grunt(voice='jotaro', seed=0):
    rng = _rng('grunt_' + str(voice), seed)
    f0a, f0b, fs, rasp, drive = _VOICE.get(voice, _VOICE['jotaro'])
    n = _n(0.3)
    t = _t(n)
    f0 = np.interp(t, [0, 0.03, 0.3], [f0a * 1.15, f0a, f0b]) * (1 + 0.02 * np.sin(_TAU * 30 * t))
    src = osc(f0, n, 'saw') + 0.5 * osc(f0 * 0.5, n, 'square', 0.4) * rasp + rasp * noise(n, rng)
    src *= np.interp(t, [0, 0.012, 0.08, 0.22, 0.3], [0, 1, 0.85, 0.25, 0])
    F1 = np.interp(t, [0, 0.05, 0.3], [380, 680, 560]) * fs
    F2 = np.interp(t, [0, 0.05, 0.3], [900, 1150, 1050]) * fs
    y = _formant(src, [(F1, 5, 1.0), (F2, 6, 0.7), (2500 * fs, 7, 0.25)])
    return _fin(sat(y * 3, drive), 0.6, 0.002, 0.03)


def _chant(name, n, rate, f0, v1, v2, breath, seed):
    """n 个“X-RA”音节（每个 1/rate 秒）：前 40 % 元音 v1、45 % 处幅度掉到 .25 当“r”闪音、之后元音 v2。
    v1 / v2 = (F1, F2)；breath > 0 时每个音节前面加一点气声（HO-RA 的 h）。"""
    rng = _rng(name, seed)
    k = max(1, int(n))
    per = 1.0 / float(rate)
    out = np.zeros(_n(per * k + 0.1))
    m = _n(per)
    t = _t(m)
    for i in range(k):
        f = float(f0) * rng.uniform(0.97, 1.05) * np.interp(t, [0, per * 0.4, per], [1.0, 1.08, 0.95])
        src = osc(f, m, 'saw') + 0.4 * osc(f * 0.5, m, 'square', 0.4) + 0.2 * noise(m, rng)
        a = np.interp(t, [0, 0.01, per * 0.38, per * 0.45, per * 0.52, per * 0.85, per], [0, 1, 0.9, 0.25, 1, 0.7, 0])
        F1 = np.interp(t, [0, per * 0.4, per * 0.5, per], [v1[0], v1[0], v2[0], v2[0] * 0.97])
        F2 = np.interp(t, [0, per * 0.4, per * 0.5, per], [v1[1], v1[1], v2[1], v2[1] * 0.96])
        y = _formant(src * a, [(F1, 5, 1.0), (F2, 6, 0.7), (2600, 7, 0.2)])
        y = sat(y * 3, 2.0)
        if breath:
            bn = _n(0.035)
            h = bp(noise(bn, rng), 900, 4000) * np.sin(np.pi * np.linspace(0, 1, bn)) ** 2 * breath
            y[:bn] += h
        _place(out, y, _n(i * per), 1.0 if i % 2 == 0 else 0.85)
    return _fin(out, 0.65, 0.002, 0.03)


@reg('ora_voice', 'Synthetic "O-RA!" chant syllables (n syllables at ~7/s; formant o->a; experimental)', la=-15)
def _ora_voice(n=1, rate=7.0, f0=165.0, seed=0):
    return _chant('ora_voice', n, rate, f0, (450, 800), (800, 1250), 0.0, seed)


@reg('muda_voice', 'Synthetic "MU-DA!" chant syllables (DIO; formant u->a, lower; experimental)', la=-15)
def _muda_voice(n=1, rate=7.0, f0=130.0, seed=0):
    return _chant('muda_voice', n, rate, f0, (300, 800), (800, 1250), 0.0, seed)


@reg('hora_voice', 'Synthetic "HO-RA!" chant syllables (Polnareff; breathy h + o->a; experimental)', la=-15)
def _hora_voice(n=1, rate=7.5, f0=150.0, seed=0):
    return _chant('hora_voice', n, rate, f0, (480, 860), (820, 1300), 0.8, seed)


def _mix_parts(duration, parts):
    out = np.zeros(_n(duration))
    for name, at, gain in parts:
        y = sfx.make(name)
        if y.ndim == 2:
            y = y.mean(axis=1)
        _place(out, y, _n(at), gain)
    return _fin(out, .72, .002, .06)


@reg('metal_scrape', '金属伪装转移：短促刮擦和高频共振', la=-19)
def _metal_scrape(seed=0):
    n = _n(.5)
    rng = _rng('metal_scrape', seed)
    t = _t(n)
    x = bp(noise(n, rng), 1800, 7000) * (.3 + .7 * np.sin(t * 130) ** 2)
    x += _metal(n, [740, 1240, 2230], [.12, .08, .06], [.4, .3, .2], rng)
    return _fin(x * env_exp(n, .14, .008), .65, .002, .06)


@reg('metal_crunch', '义手被咬碎的金属断裂声', la=-16)
def _metal_crunch():
    return _mix_parts(.9, [('crash', 0, .4), ('punch_heavy', .05, .7), ('armor_off', .08, .45)])


@reg('water_splash', '跃出水面的连续水花', la=-18)
def _water_splash():
    return _mix_parts(1.6, [('splash', 0, .9), ('water_gush', .2, .45)])


@reg('teeth_crunch', '牙齿碎裂：钝击后接清脆碎片', la=-16)
def _teeth_crunch():
    return _mix_parts(.8, [('punch_heavy', 0, .8), ('crash', .025, .3), ('glass_break', .06, .25)])


@reg('clay_crumble', '泥偶崩散：落地钝响和沙粒', la=-19)
def _clay_crumble():
    return _mix_parts(1.2, [('thud', 0, .7), ('sand', .03, .8)])


@reg('lalala', '死神13的三音节合成笑声', la=-20)
def _lalala():
    return _chant('lalala', 3, 3.5, 225, (680, 1200), (800, 1450), .05, 0)


@reg('water_jet', '盖布急速水柱：喷射和水面冲击', la=-17)
def _water_jet():
    return _mix_parts(1.2, [('water_gush', 0, .8), ('whoosh', 0, .35), ('splash', .12, .5)])


@reg('sand_storm', '愚者拍翼：砂砾擦过风声', la=-21)
def _sand_storm():
    return _mix_parts(1.5, [('sand', 0, .8), ('wind', 0, .35), ('whoosh', .08, .25)])


@reg('magnet_clack', '金属受磁力吸附的两次撞击', la=-18)
def _magnet_clack(seed=0):
    rng = _rng('magnet_clack', seed)
    n = _n(.65)
    out = _metal(n, [460, 930, 1670], [.12, .08, .07], [1, .65, .35], rng)
    _place(out, _metal(_n(.35), [610, 1210], [.08, .05], [.7, .4], rng), _n(.12), .8)
    return _fin(out, .72, .001, .06)


@reg('train_horn', '远处列车的低沉双音汽笛', la=-20)
def _train_horn():
    n = _n(1.8)
    x = osc(185, n, 'saw') + .6 * osc(233, n, 'saw') + .3 * osc(370, n, 'sine')
    return _fin(lp(x, 2200, 2), .65, .12, .28)


@reg('axe_chop', '斧头挥落：风声后接木质钝击', la=-17)
def _axe_chop():
    return _mix_parts(.85, [('whoosh', 0, .6), ('thud', .09, .9), ('punch_heavy', .09, .35)])


@reg('sub_alarm', '潜艇漏水警报：两次方波蜂鸣', la=-22)
def _sub_alarm():
    n = _n(1.2)
    t = _t(n)
    gate = ((t < .4) | ((t > .6) & (t < 1))).astype(float)
    return _fin(lp(osc(660, n, 'square') * gate, 2500, 1), .45, .005, .05)


@reg('genie_appear', '灯神现形：闪光和上升的音阶', la=-18)
def _genie_appear():
    n = _n(1.3)
    t = _t(n)
    x = osc(360 * (4 ** np.minimum(t, 1)), n, 'sine') * np.sin(np.pi * np.minimum(t / 1.3, 1))
    for name, at in [('sparkle', 0), ('ding', .55)]:
        y = sfx.make(name)
        _place(x, y.mean(axis=1) if y.ndim == 2 else y, _n(at), .5)
    return _fin(x, .65, .008, .1)


@reg('roadroller', '压路机坠落：柴油机轰鸣、重击和金属散落', la=-15, push=5)
def _roadroller():
    return _mix_parts(3.2, [('car_engine', 0, .55), ('rumble', .05, .7), ('crash', .4, .75), ('explosion', .4, .6), ('armor_off', .5, .5)])


@reg('drip', '大厅中单颗水滴的空旷回响', la=-24)
def _drip():
    n = _n(.7)
    t = _t(n)
    x = osc(1700 * np.exp(-t * 8) + 420, n, 'sine') * env_exp(n, .055, .001)
    return _fin(delay(x, .11, .35, 3), .4, .001, .08)


@reg('baseball_hit', '球棒击中球：木质脆响和短促掠空', la=-18)
def _baseball_hit():
    return _mix_parts(.5, [('thud', 0, .5), ('punch_heavy', .005, .55), ('whoosh', .025, .25)])


@reg('sax_melody', '幻觉走廊的四音短句，颤音提示循环机关', la=-22)
def _sax_melody():
    out = np.zeros(_n(2.1))
    for i, hz in enumerate([293.66, 349.23, 329.63, 261.63]):
        n = _n(.48)
        t = _t(n)
        f = hz * (1 + .012 * np.sin(t * 2 * np.pi * 5.2))
        note = lp(osc(f, n, 'square') + .18 * osc(f * 2, n, 'sine'), 2100, 2)
        _place(out, note * np.sin(np.pi * t / .48) ** .5, _n(i * .46), .22)
    return _fin(out, .5, .012, .14)


@reg('void_eat', '奶油吞噬：低频漩涡吸力收进一声闷响', la=-19)
def _void_eat():
    n = _n(1.1)
    t = _t(n)
    rng = _rng('void_eat', 0)
    x = lp(noise(n, rng), 900, 2) * (.2 + .8 * t / 1.1)
    x += osc(180 * np.exp(-t * 3) + 35, n, 'sine') * .35
    y = sfx.make('thud')
    _place(x, y.mean(axis=1) if y.ndim == 2 else y, _n(.65), .45)
    return _fin(x, .65, .04, .18)


@reg('knife_freeze', '飞刀凝固：高频金属泛音骤然冻结', la=-20)
def _knife_freeze():
    n = _n(1.1)
    x = _metal(n, [1400, 2100, 3200, 4800], [.4, .6, .35, .2], [.3, .25, .2, .12], _rng('knife_freeze', 0))
    y = sfx.make('freeze')
    _place(x, y.mean(axis=1) if y.ndim == 2 else y, 0, .45)
    return _fin(x, .55, .002, .14)


@reg('knife_volley', '飞刀阵恢复：八次错开的金属破空', la=-17)
def _knife_volley():
    return _mix_parts(1.3, [('knife_throw', i * .065, .34) for i in range(8)] + [('whoosh', .08, .3)])


@reg('flatline', '停止心跳：心电监测的平稳长鸣', la=-24)
def _flatline():
    return _fin(osc(880, _n(1.4), 'sine'), .3, .018, .16)


@reg('clang', '刀刃撞上金属：明亮撞击和短共振', la=-18)
def _clang():
    n = _n(.65)
    return _fin(_metal(n, [830, 1420, 2260, 3400], [.1, .13, .08, .05], [1, .65, .4, .25], _rng('clang', 0)), .7, .001, .08)


if __name__ == '__main__':
    # 自检：把本文件登记的全部新音效各渲一次，打印时长 / 声道 / 峰值 / 感知响度
    for nm in sorted(GAME):
        kw = {}
        if nm == 'stand_summon':
            kw = {'kind': 'star'}
        y = sfx.make(nm, **kw)
        print(f'{nm:18s} {len(y) / SR:6.3f}s ch={1 if y.ndim == 1 else 2} peak={np.abs(y).max():.2f} '
              f'LA={sfx.loudness(y):6.1f}')
