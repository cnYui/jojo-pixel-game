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


# ============================================================ 第2章（南海）：猩猩、雾中货轮、暗蓝之月、海面
def _cnoise(L, rng, tilt=0.0, lo=None, hi=None):
    """圆周彩色噪声：白噪声在频域乘 f^(-tilt/2)（tilt 1 = 粉、2 = 褐）再过 _cband；首尾天然接得上，std 归一。"""
    X = np.fft.rfft(rng.standard_normal(L))
    f = np.fft.rfftfreq(L, 1 / SR)
    f[0] = 1.0
    y = _cband(np.fft.irfft(X * f ** (-tilt / 2), L), lo, hi)
    return y / (np.std(y) + 1e-9)


def _cmod(L, rng, ks):
    """循环内整数周期的慢起伏：几条正弦（每循环 k 次，随机相位 / 幅度）叠加，归一到 [-1, 1]。"""
    t = _t(L)
    Ls = L / SR
    m = np.zeros(L)
    for k in ks:
        m += rng.uniform(.4, 1.0) * np.sin(_TAU * k / Ls * t + rng.uniform(0, _TAU))
    return m / (np.abs(m).max() + 1e-9)


@reg('ape_screech', '猩猩（力量的本体）尖叫“呜——喔！”：带喉音的低“呜”往上扬，接高亢沙哑的“喔！”'
                    '（锯齿 + 次谐波喉音过四条共振峰，0.85 s；“喔！”在 +0.335 s）', la=-15, hit=0.335)
def _ape_screech(seed=0):
    rng = _rng('ape_screech', seed)
    n = _n(.8)
    t = _t(n)
    f0 = np.interp(t, [0, .08, .22, .27, .31, .36, .5, .66, .8], [300, 360, 520, 560, 940, 1180, 1060, 820, 640])
    scream = np.clip((t - .29) / .05, 0, 1)                         # 0 = “呜”，1 = “喔！”
    f0 = f0 * (1 + .025 * sfx.lfo_noise(n, 45, rng) + .03 * scream * np.sin(_TAU * 13 * t)
               + .02 * scream * sfx.lfo_noise(n, 140, rng))         # 嘶叫段多一层快抖（声带乱颤）
    rasp = .25 + .5 * scream * np.interp(t, [0, .36, .55, .8], [1, 1, .7, 1])
    growl = 1 + .45 * np.sin(_TAU * np.cumsum(f0 * .5) / SR) * (.8 - .5 * scream)    # 半频调幅 = 喉音
    src = osc(f0, n, 'saw') + .55 * osc(f0 * .5, n, 'square', .35) * rasp + rasp * noise(n, rng)
    src = src * growl
    F1 = np.interp(t, [0, .28, .34, .5, .8], [430, 470, 980, 1050, 800])
    F2 = np.interp(t, [0, .28, .34, .5, .8], [900, 950, 1550, 1700, 1400])
    F3 = np.interp(t, [0, .3, .4, .8], [2500, 2600, 3000, 2800])
    y = _formant(src, [(F1, 5, 1.0), (F2, 6, .75), (F3, 7, .45), (4100, 6, .2 * scream + .05)])
    y = sat(y * 3, 2.4)
    e = env_pts(n, [(0, 0), (.04, .35), (.2, .5), (.27, .42), (.3, .15), (.335, 1), (.52, .85), (.68, .5), (.8, 0)])
    y = bp(y * e, 220, 6500)
    y = verb(y, wet=.12, sec=.45, tau=.09, lpf=5000, seed=33).mean(axis=1)[:_n(.86)]
    return _fin(y, .65, .003, .07)


@reg('ship_horn', '雾里巨大货轮的汽笛：两个低音（≈73 / 88 Hz，各自微失谐出拍频）的簧片号角，号筒共鸣把中频顶起来，'
                  '尾音在长混响里慢慢散开（2.5 s，立体声）', la=-18, push=4)
def _ship_horn(seed=0):
    rng = _rng('ship_horn', seed)
    T, on = 2.5, 1.62                     # 总长；号角吹 1.62 s，后面是雾里的混响尾巴
    n, m = _n(T), _n(on)
    t = _t(m)
    bend = (1 - .055 * np.exp(-t / .07)) * (1 - .035 * np.clip((t - 1.25) / .37, 0, 1) ** 1.5)   # 起音压力上来、收尾气压掉
    wob = 1 + .004 * sfx.lfo_noise(m, 3, rng)
    tone = np.zeros(m)
    fund = np.zeros(m)
    for f, beat, g in ((73.0, 1.1, 1.0), (88.3, 1.4, .85)):
        for d, w in ((-.5, 1.0), (.5, .55)):                       # 一对微失谐、不等幅：拍频“哇——哇——”但不会拍到零
            ff = (f + d * beat) * bend * wob
            p0 = rng.uniform()
            tone += g * w * osc(ff, m, 'square', .14, ph0=p0)      # 窄脉冲 = 簧片 / 膜片的“嗡”，谐波一路铺到 2 kHz
            fund += g * w * osc(ff, m, ph0=p0)                     # 基频再垫一层：两条低频线稳、厚
    body = .5 * lp(tone, 1900, 2) + 1.3 * bp(tone, 230, 480) + .8 * bp(tone, 600, 1000) + .3 * fund    # 号筒共鸣
    body = sat(body * 1.6, 3.0)                                    # 大号角本来就“吹爆”：压扁波形，嗡得更满
    air = bp(noise(m, rng), 500, 2600) * (.04 + .22 * np.exp(-t / .08))
    x = (body + air) * env_pts(m, [(0, 0), (.04, .45), (.2, 1), (1.2, .93), (1.45, .4), (on, 0)])
    x = np.concatenate([x, np.zeros(n - m)])
    x = verb(lp(x, 2400), wet=.34, sec=2.6, tau=.8, lpf=1600, seed=31, pre=.035)[:n]
    x = sfx._limit(norm(x, 1.0), 5.0)                              # 峰值主要来自混响的噪声样湿声：混响后再前瞻限幅
    return _fin(x, .9, .01, .55)


@reg('whirlpool', '暗蓝之月在水下造漩涡：越转越快的涌流（中心频率和声像都跟着绕圈）+ 低沉气泡 + 一点低频涡鸣，'
                  '整体压在 1.4 kHz 以下的水下闷声（1.5 s，立体声）', la=-18, push=6)
def _whirlpool(seed=0):
    rng = _rng('whirlpool', seed)
    T = 1.5
    n = _n(T)
    t = _t(n)
    u = t / T
    spin = 1.4 + 3.2 * np.clip(u / .75, 0, 1) ** 1.4               # 圈 / 秒：1.4 → 4.6
    ph = _TAU * np.cumsum(spin) / SR
    s = np.sin(ph)
    c = 300 * (900 / 300) ** (.5 + .5 * s) * (1 + .25 * u)          # 涌流“呼——呼——”：中心频率每圈摆一次
    flow = sweep(noise(n, rng), c, 'bp', q=1.8) + .5 * sweep(noise(n, rng), c * 1.8, 'bp', q=3.0)
    hum = osc(48 * (1 + .5 * u), n, 'tri') * (.6 + .4 * np.sin(ph + 1.3))
    rum = lp(noise(n, rng, 'brown'), 150) * (.65 + .35 * (.5 + .5 * s))
    suck = osc(_dsig(n, 160, 50), n) * env_exp(n, .2, .03)          # 开头水被抽走的一下“呜”
    env = env_pts(n, [(0, 0), (.25, 1), (1.1, .95), (T, 0)])
    core = (flow + .25 * hum + .25 * rum) * env + .35 * suck
    bub = sfx._bubble_train(n, 40, rng, 200, 650, amp_env=np.clip(.25 + u * 1.2, 0, 1)) * env
    x = _pan(core, .7 * s) + _pan(bub, -.6 * s)
    x = lp(sat(x * 1.3, 1.6), 1400)
    x = sfx._limit(norm(verb(x, wet=.2, sec=.6, tau=.15, lpf=1400, seed=32)[:n], 1.0), 3.5)
    return _fin(x, .85, .01, .25)


def _lap(rng):
    """一下浪拍船身：软起音的“噗啦”水声（带通往下扫）+ 船壳的空闷“咚”+ 几滴水珠。"""
    m = _n(.45)
    x = sweep(noise(m, rng), _dsig(m, 900, 220), 'bp', q=1.2) * env_pts(m, [(0, 0), (.02, 1), (.07, .5), (.3, .08), (.45, 0)])
    x += .3 * bp(noise(m, rng), 700, 3000) * env_pts(m, [(0, 0), (.008, 1), (.04, .15), (.12, 0)])
    x += .5 * osc(_dsig(m, 140, 85), m) * env_exp(m, .07, .01)
    for _ in range(int(rng.integers(2, 5))):
        dn = _n(rng.uniform(.015, .035))
        f0 = rng.uniform(700, 1600)
        _place(x, _chirp(dn, f0, f0 * rng.uniform(1.4, 2.0), dn / SR / 3, attack=.002), _n(rng.uniform(.06, .3)),
               rng.uniform(.05, .15))
    return x


def _spray(rng):
    """一点小水花：白沫的沙声 + 水声 + 一串水珠。"""
    m = _n(.6)
    x = .4 * hp(noise(m, rng), 2200) * env_pts(m, [(0, 0), (.03, 1), (.12, .4), (.6, 0)])
    x += .6 * bp(noise(m, rng), 500, 2000) * env_pts(m, [(0, 0), (.02, 1), (.15, .2), (.5, 0)])
    for _ in range(9):
        dn = _n(rng.uniform(.012, .03))
        f0 = rng.uniform(1200, 3000)
        _place(x, _chirp(dn, f0, f0 * rng.uniform(1.3, 1.9), dn / SR / 3, attack=.001), _n(rng.uniform(.03, .45)),
               rng.uniform(.05, .2))
    return x


@reg('sea_loop', '甲板 / 救生艇上的海浪环境音：约 2 s 一涌的海水沙沙（浪峰才带高频白沫）+ 浪拍船身 + 偶尔一点水花，'
                 '安静不抢台词（loop=6 s，立体声，无缝）', la=-28, push=0, loop=6.0)
def _sea_loop(loop=6.0, seed=0):
    rng = _rng('sea_loop', seed)
    L = _n(loop)
    sw = .65 * _cmod(L, rng, (3,)) + .35 * _cmod(L, rng, (2, 5))    # 一个循环约 3 涌，不完全等距
    sw /= np.abs(sw).max()
    chans = []
    for _ in range(2):
        lvl = np.clip(.5 + .5 * sw + .12 * _cmod(L, rng, (4, 7, 11)), 0, 1)
        low = _cnoise(L, rng, 1.0, 80, 650) * (.45 + .55 * lvl)              # 一直在的低沉海水
        mid = _cnoise(L, rng, .5, 500, 2600) * lvl ** 2.2 * .8              # 涌上来才有的“沙——”
        foam = _cnoise(L, rng, 0.0, 2600, 8000) * lvl ** 4 * .22            # 浪峰的白沫
        deep = _cnoise(L, rng, 2.0, 30, 150) * .45
        chans.append(low + mid + foam + deep)
    out = np.stack(chans, -1)
    ev = np.zeros((L + _n(1.0), 2))
    pk = [i for i in range(1, L - 1) if sw[i] >= sw[i - 1] and sw[i] > sw[i + 1] and sw[i] > .2]
    for p in pk:                                                   # 每涌拍一下船身（浪快到顶时），一半带个小回拍
        at = (p - _n(rng.uniform(.12, .3))) % L
        pan = rng.uniform(-.45, .45)
        _place(ev, _pan(_lap(rng), pan), at, rng.uniform(.75, 1.0))
        if rng.uniform() < .5:
            _place(ev, _pan(_lap(rng), pan + rng.uniform(-.15, .15)), at + _n(rng.uniform(.2, .32)), rng.uniform(.3, .5))
    for _ in range(2):                                             # 涌与涌之间零星的小拍
        _place(ev, _pan(_lap(rng), rng.uniform(-.6, .6)), int(rng.uniform(0, 1) * L), rng.uniform(.25, .4))
    big = max(pk, key=lambda i: sw[i]) if pk else L // 2
    _place(ev, _pan(_spray(rng), rng.uniform(-.6, .6)), (big + _n(.05)) % L, .55)
    out = .45 * out + _fold(ev, L) * 1.1
    return _fin_loop(out, .34)


def _gull_call(rng, fs=1.0, dur=.3):
    """一声海鸥“kee-OW”：80 ms 挑上去、再慢慢落下的鼻音（锯齿 + 窄脉冲过 2.2 / 3.6 kHz 共振峰）+ “k” 起音。"""
    m = _n(dur + .04)
    t = _t(m)
    f0 = np.interp(t, [0, .07, .11, dur * .75, dur], [880, 1600, 1560, 1000, 820]) * fs
    f0 = f0 * (1 + .015 * np.sin(_TAU * 28 * t) + .008 * sfx.lfo_noise(m, 90, rng))
    src = osc(f0, m, 'saw') + .5 * osc(f0, m, 'square', .25) + .15 * noise(m, rng)
    y = sat(_formant(src, [(2200 * fs, 3, 1.0), (3600 * fs, 4, .55)]) * 2.5, 1.8)
    y = y * env_pts(m, [(0, 0), (.015, .7), (.07, 1), (dur * .6, .8), (dur, 0), (dur + .04, 0)])
    return y + .25 * hp(noise(m, rng), 2000) * env_exp(m, .005, .0005)


@reg('gulls', '远处的海鸥：一只“kee-OW”两声，再远一点另一只答一声；高频被距离吃掉，带一点水面回声（1.5 s，立体声）',
     la=-22)
def _gulls(seed=0):
    rng = _rng('gulls', seed)
    n = _n(1.5)
    x = np.zeros((_n(1.3), 2))
    for st, fs, d, pan, g, cut in ((.03, 1.0, .3, -.45, 1.0, 3800), (.42, .95, .27, -.4, .8, 3800),
                                   (.92, 1.13, .22, .55, .5, 2600)):
        _place(x, _pan(lp(_gull_call(rng, fs, d), cut, 2), pan), _n(st), g)
    x = delay(x, .23, .2, 1, lpf=2000)                            # 水面 / 船壳弹回来的远处回声
    x = verb(x, wet=.1, sec=.7, tau=.14, lpf=3000, seed=34)[:n]
    return _fin(x, .55, .003, .25)


@reg('creak', '钢板船体被拧的低沉吱嘎“吱——嘎——”：不规则的黏滑摩擦脉冲（30–75 次 / 秒）激励一组慢慢漂移的钢板模态'
              '（63 Hz–2.1 kHz，低的响得久），在空船舱里回响（0.8 s）', la=-17)
def _creak(seed=0):
    rng = _rng('creak', seed)
    n, cn = _n(.8), _n(.72)
    ct = _t(cn)
    rate = np.interp(ct, [0, .1, .3, .36, .42, .6, .72], [34, 52, 74, 60, 66, 44, 30]) * (1 + .18 * sfx.lfo_noise(cn, 30, rng))
    ph = np.cumsum(rate) / SR
    imp = np.diff(np.floor(ph), prepend=0.0) * rng.uniform(.35, 1.0, cn)
    imp *= env_pts(cn, [(0, 0), (.05, .7), (.3, 1), (.36, .3), (.42, 1), (.62, .8), (.72, 0)])     # “吱——”松一下“嘎——”
    imp = np.concatenate([imp, np.zeros(n - cn)])
    drift = 1 + .03 * sfx.lfo_noise(n, 2.5, rng)                   # 受力变化 → 模态整体漂移
    x = np.zeros(n)
    for f, q, a in ((63, 14, .5), (131, 26, 1.0), (227, 28, .95), (348, 26, .85), (509, 24, .7), (733, 22, .55),
                    (1046, 20, .38), (1480, 18, .22), (2110, 16, .12)):
        x += a * q / f * sweep(imp, f * drift * rng.uniform(.98, 1.02), 'bp', q=q, block=128)    # q / f：按带宽补回能量
    grit = bp(noise(n, rng), 1200, 4500) * norm(lp(np.abs(imp), 90, 1), 1.0)
    x = sat(norm(x, 1.0) * 1.6 + .15 * grit, 2.2)
    x = verb(x, wet=.2, sec=1.2, tau=.32, lpf=2400, seed=35).mean(axis=1)[:n]
    x = sfx._limit(norm(x, 1.0), 3.5)                              # 黏滑脉冲峰均比高：限幅压一点，响度才对得上老音效
    return _fin(x, .85, .005, .08)


@reg('lighter', '冒牌船长的 Zippo：开盖的亮金属“叮”+ 擦火轮“嚓”+ 一小下火苗“噗”（0.3 s）', la=-20)
def _lighter(seed=0):
    rng = _rng('lighter', seed)
    n = _n(.32)
    x = np.zeros(n)
    m = _n(.2)                                                     # 1. 开盖：铰链咔 + 盖子“叮”
    lid = _metal(m, [3150, 4620, 6240, 8100], [.07, .05, .035, .02], [1, .75, .5, .3], rng, .002)
    lid = lid * np.minimum(_t(m) / .0005, 1) + .6 * hp(noise(m, rng), 3000) * env_exp(m, .002, .0002)
    lid += .25 * bp(noise(m, rng), 800, 2500) * env_exp(m, .006, .0003)
    _place(x, lid, 0)
    m = _n(.06)                                                    # 2. 擦火轮：密集砂砾 + “嚓”
    wheel = _clicks(m, 1500, rng, (.08, .5), 2500, np.interp(_t(m), [0, .005, .045, .06], [0, 1, .3, 0]))
    wheel += .5 * bp(noise(m, rng), 2500, 8000) * env_pts(m, [(0, 0), (.004, 1), (.035, .25), (.06, 0)])
    _place(x, wheel, _n(.115), .9)
    m = _n(.17)                                                    # 3. 火苗：小“噗”+ 一点呼呼声
    tt = _t(m)
    puff = bp(noise(m, rng), 300, 1600) * env_pts(m, [(0, 0), (.01, 1), (.05, .35), (.17, 0)])
    puff += .35 * osc(_dsig(m, 140, 70), m) * env_exp(m, .03, .004)
    puff += .2 * lp(noise(m, rng), 900) * (1 + .5 * np.sin(_TAU * 14 * tt)) * env_pts(m, [(0, 0), (.03, 1), (.17, 0)])
    _place(x, puff, _n(.15), .7)
    return _fin(x, .6, .0005, .03)


# ============================================================ 第3章（新加坡）：黑檀木恶魔、黄色节制、酒店 / 街道 / 缆车 / 火车
def _cres(x, f0, q):
    """FFT 圆周共振带通（二阶带通的幅度响应，峰值 0 dB）：循环里要窄带（风哨）时用，首尾不留接缝。"""
    L = len(x)
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(L, 1 / SR)
    f[0] = 1e-6
    H = 1 / np.sqrt(1 + (q * (f / f0 - f0 / f)) ** 2)
    H[0] = 0
    return np.fft.irfft(X * (H[:, None] if x.ndim == 2 else H), L, axis=0)


def _rms1(x):
    """按 RMS 归一（混层前先把各层拉到同一尺度，增益才好读）。"""
    return x / (np.sqrt(np.mean(np.asarray(x) ** 2)) + 1e-12)


@reg('razor', '迪波 / 黑檀木恶魔挥剃刀：极短的细刃划空“咻”（3→10 kHz 窄带上扫）+ 刃口一下“嚓”+ 细高的金属铮鸣'
              '（4.3–10.5 kHz，比 slash 更细、更高、更短；0.25 s，刃口在 +0.05 s）', la=-17, hit=.05)
def _razor(seed=0):
    rng = _rng('razor', seed)
    n = _n(.25)
    x = np.zeros(n)
    sn = _n(.07)                                                   # 1. 细刃划空：窄带（q 2.6）一路往上扫
    u = np.linspace(0, 1, sn)
    sw = sweep(noise(sn, rng), _dsig(sn, 3000, 10000), 'bp', q=2.6) * np.sin(np.pi * u) ** 1.5 * np.sqrt(u)
    sw += .3 * hp(noise(sn, rng), 7000) * np.sin(np.pi * u) ** 4
    _place(x, norm(sw, 1.0), 0, .8)
    at = _n(.05)
    m = n - at                                                     # 2. 刃口：细高的铮鸣（短衰减）+ “嚓”
    v = rng.uniform(.97, 1.03)
    ring = _metal(m, np.array([4310, 6120, 8240, 10530]) * v, [.09, .06, .04, .025], [1, .7, .45, .3], rng, .003)
    ring *= np.minimum(_t(m) / .0006, 1)
    _place(x, norm(ring, 1.0), at, .6)
    k = _n(.014)
    edge = hp(noise(k, rng), 5000) * env_exp(k, .0018, .0002) + .6 * bp(noise(k, rng), 2000, 5000) * env_exp(k, .004, .0003)
    _place(x, norm(edge, 1.0), at, .45)
    return _fin(x, .75, .001, .04)


@reg('doll_voice', '黑檀木恶魔（玩偶）的怪笑：尖细的“咯咯咯”越笑越快（约 10 → 22 个 / 秒，音高从 540 Hz 往上爬），'
                   '最后一声拖长的尖“吱——”；小身体的共振峰（约 ×1.5）+ 一层越来越密的发条齿轮“嗒嗒”，不成词（0.6 s）', la=-17)
def _doll_voice(seed=0):
    rng = _rng('doll_voice', seed)
    T = .6
    out = np.zeros(_n(T + .1))
    ons = []                                                       # 音节起点：间隔每次 ×0.86（越笑越快）
    st, per = .015, .1
    while st < T - .14:
        ons.append((st, per))
        st += per
        per = max(.044, per * .86)
    ons.append((st, None))                                         # 最后一声拖长的“吱——”
    K = len(ons)
    for i, (st, per) in enumerate(ons):
        last = per is None
        d = (T - st - .01) if last else per * .7
        m = _n(d)
        tt = _t(m)
        u = tt / d
        fa = (540 + 300 * i / (K - 1)) * rng.uniform(.96, 1.05)
        if last:
            f0 = fa * np.interp(u, [0, .15, .6, 1], [1.05, 1.32, 1.25, .95])
            F1 = np.interp(u, [0, .3, 1], [700, 520, 480])        # “i”
            F2 = np.interp(u, [0, .3, 1], [3000, 3400, 3300])
            e = env_pts(m, [(0, 0), (.006, 1), (d * .5, .8), (d, 0)])
        else:
            f0 = fa * np.interp(u, [0, .12, 1], [1.15, 1.0, .84])  # 每个“咯”往下掉
            F1 = np.interp(u, [0, .3, 1], [950, 800, 700])        # “e”（小身体：共振峰整体抬高）
            F2 = np.interp(u, [0, .3, 1], [2500, 2900, 3000])
            e = env_pts(m, [(0, 0), (.003, 1), (d * .4, .65), (d, 0)])
        f0 = f0 * (1 + .025 * np.sin(_TAU * 34 * tt))             # 发条的抖
        src = osc(f0, m, 'saw') + .45 * osc(f0, m, 'chip', .3) + .12 * noise(m, rng)
        y = _formant(src, [(F1, 4, 1.0), (F2, 6, .8), (4400, 7, .35)])
        y = sat(norm(y, 1.0) * e * 2.5, 1.8)
        a = _n(st)
        kn = _n(.007)
        _place(out, bp(noise(kn, rng), 2800, 8000) * env_exp(kn, .0015, .0002), a, .5)     # “k”
        _place(out, y, a + _n(.005), (1.0 if i % 2 == 0 else .8) * (1.15 if last else 1.0))
    tk = np.zeros_like(out)                                        # 发条齿轮：一路“嗒嗒嗒”，越来越密
    st, per = 0.0, .04
    while st < T - .02:
        m = _n(.02)
        c = _metal(m, np.array([2900, 4650, 6800]) * rng.uniform(.97, 1.03), [.004, .003, .002], [1, .6, .4], rng, .002)
        _place(tk, c + .4 * hp(noise(m, rng), 4000) * env_exp(m, .0008, .0001), _n(st), rng.uniform(.6, 1.0))
        st += per
        per = max(.025, per * .95)
    x = bp(out + .22 * tk, 380, 9000)
    return _fin(x, .6, .002, .04)


@reg('doll_scurry', '玩偶在家具底下窜：木地板上细碎的小脚步（约 22 步 / 秒的“嗒嗒嗒”，带一点木头共鸣，左右脚略不同）'
                    '+ 布料摩擦的沙沙声；轻、近、干，不加混响（0.4 s；藏身预警）', la=-21)
def _doll_scurry(seed=0):
    rng = _rng('doll_scurry', seed)
    T = .4
    n = _n(T)
    x = np.zeros(n + _n(.06))
    rus = np.zeros_like(x)
    gain = lambda s: float(np.interp(s, [0, .07, .3, T], [.55, 1.0, .9, .5]))   # noqa: E731  跑近又跑开
    st, i = .012, 0
    while st < T - .035:
        m = _n(.04)
        v = rng.uniform(.92, 1.1) * (1.0 if i % 2 == 0 else 1.08)  # 左右脚略有不同
        exc = noise(m, rng) * env_exp(m, .0012, .0001)
        body = np.zeros(m)
        for f, q, a in ((380, 6, .5), (870, 9, 1.0), (1650, 10, .8), (2900, 12, .45)):
            body += a * sweep(exc, f * v, 'bp', q=q)
        tap = .8 * norm(body, 1.0) + .5 * norm(hp(exc, 2500), 1.0)  # 木头的“嗒”+ 脚尖的“嗒”
        _place(x, tap, _n(st), gain(st) * (1.0 if i % 2 == 0 else .78) * rng.uniform(.85, 1.0))
        k = _n(.035)                                               # 每步带一下衣料“沙”
        sw = bp(noise(k, rng), 1500, 6500) * np.sin(np.pi * np.linspace(0, 1, k)) ** 2
        _place(rus, sw, _n(st) - _n(.006), gain(st) * rng.uniform(.6, 1.0))
        st += rng.uniform(.04, .051)
        i += 1
    drag = bp(noise(len(x), rng), 900, 4500) * np.clip(.6 + .6 * sfx.lfo_noise(len(x), 30, rng), 0, 1.2)
    drag *= env_pts(len(x), [(0, 0), (.04, 1), (.32, .8), (T, 0), (T + .06, 0)])
    x = x + .35 * rus + .12 * drag
    return _fin(lp(x, 9000), .6, .001, .03)


@reg('fridge', '冰箱门自己打开：封条先黏一下、“啵”地脱开（低频“啵”+ 橡胶撕开的“噗”）+ 一点冷气 + 门轴一小段轻吱'
               '+ 继电器“咔”+ 压缩机 100 Hz 的嗡（带 50 / 200 / 300 Hz，起动时音高往上爬）一小段尾巴（0.7 s，“啵”在 +0.03 s）',
     la=-20, hit=.03)
def _fridge(seed=0):
    rng = _rng('fridge', seed)
    T = .7
    n = _n(T)
    x = np.zeros(n)
    m = _n(.03)                                                    # 0. 封条被吸着：几下细小的黏滑
    _place(x, _clicks(m, 300, rng, (.3, 1.2), 800, np.linspace(.3, 1, m)), 0, .25)
    at = _n(.03)
    m = _n(.16)                                                    # 1. “啵”：低频“啵”+ 封条撕开的“噗”+ 门板空腔的“嘭”
    pop = .7 * osc(_dsig(m, 280, 120), m) * env_exp(m, .03, .0012)
    pop += .3 * osc(_dsig(m, 560, 240), m, 'tri') * env_exp(m, .02, .001)
    pop += .6 * sweep(noise(m, rng), _dsig(m, 1500, 380), 'bp', q=2.0) * env_exp(m, .03, .0008)
    pop += .6 * bp(noise(m, rng), 380, 1200) * env_exp(m, .04, .002)
    pop += .08 * bp(noise(m, rng), 2500, 7000) * env_exp(m, .004, .0004)
    _place(x, norm(sat(pop * 1.5, 1.4), 1.0), at)
    m = _n(.35)                                                    # 2. 冷气轻轻涌出来
    _place(x, bp(noise(m, rng), 300, 1800) * env_pts(m, [(0, 0), (.06, 1), (.35, 0)]), _n(.05), .08)
    cn = _n(.26)                                                   # 3. 门轴：轻、短的黏滑吱声
    ct = _t(cn)
    rate = np.interp(ct, [0, .08, .26], [70, 120, 85]) * (1 + .12 * sfx.lfo_noise(cn, 25, rng))
    imp = np.diff(np.floor(np.cumsum(rate) / SR), prepend=0.0) * rng.uniform(.5, 1.0, cn)
    imp *= env_pts(cn, [(0, 0), (.04, 1), (.18, .8), (.26, 0)])
    cr = sweep(imp, np.interp(ct, [0, .26], [1050, 1250]), 'bp', q=14) + .6 * sweep(imp, 2300, 'bp', q=16)
    cr += .3 * sweep(imp, 3650, 'bp', q=16)
    _place(x, norm(cr, 1.0), _n(.1), .35)
    rl = _n(.33)                                                   # 4. 继电器“咔”+ 压缩机起动的嗡
    m = _n(.012)
    _place(x, hp(noise(m, rng), 1500) * env_exp(m, .002, .0002) + .5 * _metal(m, [1800, 3100], [.004, .003], [1, .6], rng),
           rl, .25)
    m = n - rl - _n(.005)
    f = 100 * (1 - .12 * np.exp(-_t(m) / .05))                     # 电机转起来：音高往上爬
    hum = .25 * osc(f * .5, m) + osc(f, m) + .6 * osc(f * 2, m) + .4 * osc(f * 3, m) + .15 * osc(f * 4, m)
    hum += .1 * osc(f, m, 'square', .2)                            # 一点电磁“滋”
    hum = norm(lp(hum, 1000), 1.0) * env_pts(m, [(0, 0), (.04, 1), (m / SR, .8)])
    _place(x, hum, rl + _n(.005), .2)
    return _fin(x, .75, .001, .12)


@reg('slime', '黄色节制的黏液蠕动 / 甩出：先一团厚的低“咕”（60–90 Hz 喉音过低共振峰 + 三个 120–300 Hz 的厚气泡 + 次低频），'
              '接湿黏的“啾”（高 Q 共振往上又往下扫、40–80 次 / 秒的黏滑抖动 + 一个上挑的湿泡）+ 拉丝慢慢扯长、最后两下细小的断开；'
              '整体压在 2.2 kHz 以下：比 drain 更厚（一整团、不是细细的吸溜）、比 rero 低得多（0.5 s）', la=-18)
def _slime(seed=0):
    rng = _rng('slime', seed)
    T = .5
    n = _n(T)
    x = np.zeros(n + _n(.05))
    m = _n(.24)                                                    # 1. “咕”：厚、低的一团
    tt = _t(m)
    f0 = np.interp(tt, [0, .07, .24], [90, 70, 60]) * (1 + .08 * sfx.lfo_noise(m, 30, rng))
    src = osc(f0, m, 'saw') + .5 * lp(noise(m, rng), 1000)
    F1 = np.interp(tt, [0, .05, .16, .24], [200, 400, 300, 230])
    F2 = np.interp(tt, [0, .05, .16, .24], [520, 850, 700, 560])
    gu = norm(_formant(src, [(F1, 4, 1.0), (F2, 5, .5)]), 1.0) * env_pts(m, [(0, 0), (.012, 1), (.1, .7), (.24, 0)])
    gu += .5 * osc(_dsig(m, 125, 55), m) * env_exp(m, .07, .005)
    for st, f, d in ((.01, 125, .06), (.055, 170, .05), (.1, 140, .07)):     # 厚气泡：慢、低、往上挑
        k = _n(d)
        _place(gu, _chirp(k, f, f * 2.1, d / 2.2, attack=.004), _n(st), .45)
    _place(x, gu, 0)
    at = _n(.14)                                                   # 2. “啾”
    m = _n(.24)
    tt = _t(m)
    fc = np.interp(tt, [0, .05, .12, .24], [350, 900, 640, 430])
    sq = sweep(noise(m, rng), fc, 'bp', q=8.0, block=64)            # 高 Q：湿、带音高的“啾”
    sq *= (.5 + .5 * np.clip(sfx.lfo_noise(m, 60, rng) * 2.0, -1, 1)) * env_pts(m, [(0, 0), (.015, 1), (.09, .65), (.24, 0)])
    vo = _formant(osc(np.interp(tt, [0, .24], [80, 62]), m, 'saw'), [(fc * .8, 5, 1.0), (fc * 1.9, 6, .4)])
    vo *= env_pts(m, [(0, 0), (.02, .8), (.14, .3), (.24, 0)])
    wet = _chirp(_n(.06), 300, 720, .03, attack=.003)              # 一个上挑的湿泡（“啾”的尾音）
    y = norm(sq, 1.0) + .6 * norm(vo, 1.0)
    _place(y, wet, _n(.035), .55)
    _place(x, y, at, .8)
    m = _n(.17)                                                    # 3. 拉丝：细丝慢慢扯长（窄带往下滑 + 颤），最后两下断开
    tt = _t(m)
    st = sweep(noise(m, rng), np.interp(tt, [0, .17], [950, 420]), 'bp', q=14, block=64)
    st *= (.6 + .4 * np.sin(_TAU * 27 * tt)) * env_pts(m, [(0, 0), (.03, 1), (.14, .6), (.17, 0)])
    _place(x, norm(st, 1.0), _n(.29), .22)
    for s0, f in ((.43, 820), (.455, 600)):
        k = _n(.018)
        _place(x, _chirp(k, f, f * .55, .006, attack=.0008), _n(s0), .25)
    x = lp(x, 2200, 2)
    return _fin(sat(x * 1.3, 1.5), .7, .003, .04)


@reg('slime_absorb', '拳头打在黄色节制上被吸收：闷的湿“噗”——软起音（约 8 ms，没有高频瞬态）的低频下坠 + 泥样低通噪声'
                     '+ 往里吞的“咕嘟”共振峰 + 一个厚气泡；1.5 kHz 以上几乎没有，一听就是“没打进去”（0.3 s）', la=-18, push=6)
def _slime_absorb(seed=0):
    rng = _rng('slime_absorb', seed)
    T = .3
    n = _n(T)
    t = _t(n)
    body = osc(_dsig(n, 150, 46), n) * env_pts(n, [(0, 0), (.008, 1), (.05, .55), (.15, .12), (T, 0)])
    mud = lp(noise(n, rng), 700, 2) * env_pts(n, [(0, 0), (.007, 1), (.04, .45), (.14, 0)])
    src = osc(np.interp(t, [0, .14], [105, 70]), n, 'saw') + .6 * lp(noise(n, rng), 1200)
    F1 = np.interp(t, [0, .03, .14, T], [600, 500, 250, 220])      # “咕嘟”：共振峰往下吞（中频让小喇叭也听得到）
    F2 = np.interp(t, [0, .03, .14, T], [1150, 1000, 620, 600])
    gulp = _formant(src, [(F1, 3, 1.0), (F2, 4, .45)]) * env_pts(n, [(0, 0), (.012, .6), (.06, 1), (.15, .3), (.22, 0)])
    x = body + .9 * norm(mud, 1.0) + .9 * norm(gulp, 1.0)
    _place(x, _chirp(_n(.08), 160, 320, .025, attack=.006), _n(.11), .35)       # 吞进去的一个厚气泡
    x = lp(sat(x * 1.3, 1.5), 1500, 2)
    return _fin(x, .85, .004, .06)


@reg('fan_loop', '酒店房间的吊扇：电机 100 Hz 低嗡（50 Hz 电网，带 50 / 200 / 300 Hz，每圈一点不平衡的起伏）+ 三片扇叶'
                 '每圈 3 下的轻“呼——呼——”（2.25 下 / 秒，左右声道错一点相位，三片轻重略不同）+ 每圈一下极轻的松动“嗒”；'
                 '安静不抢台词（loop=4 s，立体声，无缝）', la=-29, push=0, loop=4.0)
def _fan_loop(loop=4.0, seed=0):
    rng = _rng('fan_loop', seed)
    L = _n(loop)
    t = _t(L)
    rot = 3 / (L / SR)                                             # 每循环正好 3 圈（4 s → 0.75 圈 / 秒）
    bps = 3 * rot                                                  # 叶片通过：每循环正好 9 下
    chans = []
    for c in range(2):
        q = t * bps + c * .1                                       # 右声道晚 1/10 片：扇叶从头顶扫过
        blade = np.floor(q).astype(int) % 3
        pulse = np.sin(np.pi * (q % 1.0)) ** 3 * np.array([1.0, .8, .9])[blade]   # 两片之间包络为零，轻重切换没有跳变
        lo = _cnoise(L, rng, 1.0, 120, 700)
        hi = _cnoise(L, rng, .5, 600, 2400)
        chans.append(lo * (.3 + .7 * pulse) + .5 * hi * (.08 + .92 * pulse ** 1.6))
    air = np.stack(chans, -1)
    hum = (.5 * osc(_per(50, L), L) + osc(_per(100, L), L, ph0=.13) + .35 * osc(_per(200, L), L, ph0=.41)
           + .2 * osc(_per(300, L), L, ph0=.77) + .06 * osc(_per(400, L), L, ph0=.2))
    hum = _rms1(hum * (1 + .08 * np.sin(_TAU * rot * t)))
    room = _cnoise(L, rng, 2.0, 30, 250)
    ev = np.zeros(L + _n(.1))
    for k in range(3):                                             # 每圈一下极轻的松动“嗒”
        m = _n(.03)
        tick = .6 * bp(noise(m, rng), 1200, 5000) * env_exp(m, .0015, .0002)
        tick += _metal(m, [1650, 2780], [.008, .005], [1, .6], rng)
        _place(ev, tick, int((k + .62) * L / 3), rng.uniform(.8, 1.0))
    ev = _rms1(_fold(ev, L))
    out = .5 * _rms1(air) + _st(.28 * hum + .2 * room + .022 * ev)
    return _fin_loop(out, .34)


def _passby(rng, T, f_lo, f_hi, d=1, bus=False):
    """远处一辆车开过：宽带的轮胎 / 风噪“呼——”（中心频率随多普勒略降），声像从一边移到另一边，包络两头为零；
    bus=True 再加低沉的柴油机谐波（31 Hz 一族）。返回 (m, 2)，放进循环后 _fold。"""
    m = _n(T)
    u = np.linspace(0, 1, m)
    e = np.sin(np.pi * u) ** 2.5
    dop = np.interp(u, [0, .45, .55, 1], [1.08, 1.05, .94, .9])
    x = sweep(noise(m, rng, 'pink'), np.sqrt(f_lo * f_hi) * dop, 'bp', q=.7, block=512)
    x = _rms1(x) * e
    if bus:
        f = 31 * dop
        eng = sum(a * osc(f * h, m, ph0=rng.uniform()) for h, a in ((1, .6), (2, 1.0), (3, .7), (4, .5), (6, .3)))
        x = x + .7 * _rms1(lp(eng, 380)) * e ** 1.3
    p = np.interp(u, [0, 1], [-.85, .85]) * d
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], -1) * 1.4142


def _bike_bell(rng):
    """自行车铃“叮铃铃”：拇指拨的小铃，5 下约 22 次 / 秒的快敲 + 余振。"""
    m = _n(.75)
    x = np.zeros(m)
    fs = np.array([2390, 3480, 5120, 6890]) * rng.uniform(.98, 1.02)
    for i in range(5):
        k = _n(.5)
        r = _metal(k, fs, [.22, .15, .09, .06], [1, .6, .4, .25], rng, .004) * np.minimum(_t(k) / .0005, 1)
        r += .3 * hp(noise(k, rng), 4000) * env_exp(k, .001, .0001)
        _place(x, r, _n(i * .045), .9 if i % 2 == 0 else .7)
    return x


def _street_bird(rng):
    """一只街边的鸟（鹎 / 八哥那种）“啾啾——啾”：2.2–3.9 kHz 的快速滑音 + 一点颤。"""
    m = _n(.5)
    x = np.zeros(m)
    for st, f0, f1, d in ((0, 2300, 3600, .07), (.11, 2500, 3900, .06), (.3, 3400, 2200, .12)):
        k = _n(d)
        tt = _t(k)
        f = np.interp(tt, [0, d * .6, d], [f0, f1, f1 * .92]) * (1 + .03 * np.sin(_TAU * 60 * tt))
        y = (osc(f, k) + .12 * osc(2 * f, k)) * np.sin(np.pi * tt / d) ** 1.5
        _place(x, y, _n(st))
    return x


@reg('city_loop', '新加坡街道环境音：远处车流的低频底（每循环慢慢起伏）+ 三辆车从远处开过（其中一辆公交带柴油机低音，'
                  '声像从一边移到另一边）+ 远处听不清的人声嘈杂（原工程 crowd 换 seed、再圆周低通）+ 一声自行车铃、一只鸟，'
                  '带一点骑楼墙面的回声；比 crowd_loop 更“街道”、更开阔（loop=6 s，立体声，无缝）', la=-27, push=0, loop=6.0)
def _city_loop(loop=6.0, seed=0):
    rng = _rng('city_loop', seed)
    L = _n(loop)
    chans = []
    for _ in range(2):                                             # 1. 远处车流的底（两声道各自独立 → 开阔）
        sw = .7 + .3 * _cmod(L, rng, (1, 2, 3))
        chans.append((.9 * _cnoise(L, rng, 2.0, 35, 300) + .6 * _cnoise(L, rng, 1.0, 150, 1200)) * sw
                     + .05 * _cnoise(L, rng, .3, 1800, 7000))
    bed = _rms1(np.stack(chans, -1))
    bab = _rms1(_cband(_amb_loop('crowd', float(loop), seed=seed + 5), 180, 1700))    # 2. 远处人声：听不清
    cars = np.zeros((L + _n(4.0), 2))                               # 3. 开过去的车
    for at, T, lo, hi, d, bus, g in ((.3, 2.6, 300, 2400, 1, False, .8), (2.5, 3.2, 200, 1600, -1, True, 1.0),
                                     (4.6, 2.2, 400, 3000, 1, False, .55)):
        _place(cars, _passby(rng, T, lo, hi, d, bus), _n(at), g)
    cars = _fold(cars, L)
    ev = np.zeros((L + _n(1.5), 2))                                 # 4. 一声车铃、一只鸟（远、带墙面回声）
    _place(ev, _pan(lp(_bike_bell(rng), 5000), .55), _n(1.9), 1.0)
    _place(ev, _pan(lp(_street_bird(rng), 6000), -.5), _n(4.1), .9)
    ev = _fold(delay(ev, .11, .25, 2, lpf=3000), L)
    out = .55 * bed + .35 * _rms1(cars) + .45 * bab + 1.3 * ev / (np.abs(ev).max() + 1e-9)
    return _fin_loop(out, .31)


def _cabin_creak(rng):
    """缆车车厢挂架的一下轻吱嘎：比 creak 短、轻、高（小钢件 / 铝件），0.4 s。"""
    cn, n = _n(.22), _n(.4)
    ct = _t(cn)
    rate = np.interp(ct, [0, .06, .22], [45, 80, 50]) * (1 + .15 * sfx.lfo_noise(cn, 25, rng))
    imp = np.diff(np.floor(np.cumsum(rate) / SR), prepend=0.0) * rng.uniform(.4, 1.0, cn)
    imp *= env_pts(cn, [(0, 0), (.04, 1), (.14, .8), (.22, 0)])
    imp = np.concatenate([imp, np.zeros(n - cn)])
    x = np.zeros(n)
    for f, q, a in ((330, 18, .45), (560, 22, 1.0), (910, 22, .85), (1420, 20, .55), (2150, 18, .3)):
        x += a * q / f * sweep(imp, f * rng.uniform(.98, 1.02), 'bp', q=q, block=128)
    return sat(norm(x, 1.0) * 1.4, 1.8)


@reg('cable_loop', '缆车车厢里：钢缆过滑轮的低嗡（52 Hz 一族谐波，每组一对差 0.5 Hz 的拍频 + 滚轮“呜噜”起伏，慢慢摇）'
                   '+ 窗外的风（两声道独立的阵风，大风时缝隙里带 1.4 / 2.2 kHz 的细风哨）+ 两下轻轻的车厢吱嘎；'
                   '没有地面的隆隆、风很宽 → 悬在高空的空旷感（loop=6 s，立体声，无缝）', la=-28, push=0, loop=6.0)
def _cable_loop(loop=6.0, seed=0):
    rng = _rng('cable_loop', seed)
    L = _n(loop)
    t = _t(L)
    Ls = L / SR
    roll = .5 + .5 * np.sin(_TAU * _per(6.5, L) * t)                # 滑轮滚过的“呜噜”
    sway = .8 + .2 * np.sin(_TAU * (2 / Ls) * t + 1.0)              # 车厢慢慢摇：每循环 2 次
    hum = np.zeros(L)
    for h, a in ((1, 1.0), (2, .7), (3, .45), (4, .3), (6, .15)):
        f = _per(52 * h, L)
        hum += a * (osc(f, L, ph0=rng.uniform()) + .7 * osc(f + 3 / Ls, L, ph0=rng.uniform()))    # 差 0.5 Hz：每循环 3 拍
    hum = _rms1(.6 * _rms1(hum) + .5 * _cnoise(L, rng, 1.5, 60, 400) * (.55 + .45 * roll)) * sway
    gust = _cmod(L, rng, (1, 2, 3))
    chans = []
    for c in range(2):
        g = np.clip(.55 + .45 * (.7 * gust + .3 * _cmod(L, rng, (2, 5, 7))), 0, 1)
        lo = _cnoise(L, rng, 1.0, 150, 900) * (.5 + .5 * g)
        hi = _cnoise(L, rng, .3, 900, 4000) * (.15 + .85 * g ** 2)
        wh = _rms1(_cres(rng.standard_normal(L), (1380, 1460)[c], 40)) * g ** 3
        wh2 = _rms1(_cres(rng.standard_normal(L), 2210, 50)) * g ** 4
        chans.append(lo + .45 * hi + .22 * wh + .1 * wh2)
    wind = _rms1(np.stack(chans, -1))
    ev = np.zeros((L + _n(1.5), 2))
    for at, pan in ((1.7, -.35), (4.5, .4)):
        _place(ev, _pan(_cabin_creak(rng), pan), _n(at), rng.uniform(.8, 1.0))
    ev = _fold(verb(ev, wet=.15, sec=.5, tau=.08, lpf=4000, seed=36), L)
    out = .55 * wind + _st(.45 * hum) + 2.0 * ev / (np.abs(ev).max() + 1e-9)
    return _fin_loop(out, .38)


def _rail_clack(rng):
    """一下车轮过钢轨接缝（在车厢里听）：车体低频“咚”+ 中频“哐”+ 一点钢轨 / 车轮的金属泛音，低通 2.8 kHz。"""
    m = _n(.3)
    v = rng.uniform(.93, 1.07)
    x = .8 * osc(_dsig(m, 110 * v, 52 * v), m) * env_exp(m, .05, .0008)
    x += 1.1 * bp(noise(m, rng), 300, 1800) * env_exp(m, .018, .0004)
    x += .5 * bp(noise(m, rng), 150, 600) * env_exp(m, .04, .001)
    x += .35 * _metal(m, np.array([640, 1150, 1890, 2710]) * v, [.07, .05, .035, .02], [1, .7, .5, .3], rng, .004)
    return lp(sat(x * 1.5, 1.7), 2800)


@reg('train_loop', '火车车厢里：车轮过钢轨接缝的“哐当—哐当”（每秒一组：近处转向架两下 + 半秒后远处转向架两下、更轻更闷；'
                   '严格按格子排，循环里节奏接得上）+ 车厢的低频隆隆（随车轮转一点起伏）+ 一点钢轨嘶声（loop=4 s，立体声，无缝）',
     la=-27, push=0, loop=4.0)
def _train_loop(loop=4.0, seed=0):
    rng = _rng('train_loop', seed)
    L = _n(loop)
    t = _t(L)
    groups = max(1, int(round(loop)))                              # 每秒一组
    per = L / groups
    temps = [_rail_clack(rng) for _ in range(6)]
    ev = np.zeros((L + _n(1.0), 2))
    ph = .3                                                        # 整组往后挪 0.3 s：接缝落在远处那对之后的安静处，不切在“哐”上
    for i in range(groups):
        for off, g, pan, far in ((0, 1.0, -.25, False), (.14, .8, -.2, False), (.5, .7, .3, True), (.64, .6, .35, True)):
            y = temps[int(rng.integers(6))]
            if far:
                y = lp(y, 1400)
            at = int(round(i * per + (ph + off + rng.uniform(-.002, .002)) * SR))
            _place(ev, _pan(y, pan), at, g * rng.uniform(.9, 1.0))
    ev = _fold(ev, L)
    wheel = .5 + .5 * np.sin(_TAU * _per(5.6, L) * t)              # 车轮每圈一点起伏
    chans = []
    for _ in range(2):
        rum = .8 * _rms1(_cnoise(L, rng, 2.0, 25, 180)) + _rms1(_cnoise(L, rng, 1.0, 120, 900)) * (.8 + .2 * wheel)
        rum += .15 * _cnoise(L, rng, .5, 900, 3000) + .05 * _cnoise(L, rng, 0.0, 2500, 6000)
        chans.append(rum)
    sway = .9 + .1 * np.sin(_TAU * (1 / (L / SR)) * t)
    out = .16 * _rms1(np.stack(chans, -1)) * sway[:, None] + ev / (np.abs(ev).max() + 1e-9)
    return _fin_loop(out, .42)


if __name__ == '__main__':
    # 自检：把本文件登记的全部新音效各渲一次，打印时长 / 声道 / 峰值 / 感知响度
    for nm in sorted(GAME):
        kw = {}
        if nm == 'stand_summon':
            kw = {'kind': 'star'}
        y = sfx.make(nm, **kw)
        print(f'{nm:18s} {len(y) / SR:6.3f}s ch={1 if y.ndim == 1 else 2} peak={np.abs(y).max():.2f} '
              f'LA={sfx.loudness(y):6.1f}')
