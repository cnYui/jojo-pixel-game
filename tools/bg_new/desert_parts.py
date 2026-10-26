# -*- coding: utf-8 -*-
r"""desert_parts —— 第6章 / 第8章三张沙漠背景共用的零件（2026-10-18 第二轮分工，desert 组）。

不是背景 key（文件名不和任何 key 重名）：desert_noon.py（阿拉伯沙漠正午）、desert_night.py（坠机夜营）、
desert_day.py（埃及东部石漠白天）在模块加载时按路径引用这里（照 ganges_ghat.py 引用 varanasi_street.py 的写法，
模块名 bg_new_desert_parts，不改 sys.path 顺序）。

放在这里的东西（三张图都用、或者至少两张用）：
  像素小工具   借 varanasi_street 的 dk / lt / hl / vl / px / rect / mul_box / cast_shadow / haze / opaque
               （同一套墨线 / 投影手感，和第4章一致）
  噪声         1D fbm（山脊、地面起伏，可首尾循环）、各向异性的 2D 值噪声（岩石纹理、冲沟）、Bayer 抖动分档
  天           分档渐变 + 太阳光晕、卷云（wrap 用，首尾循环）、积云
  岩山         一道道岩脊：冲沟明暗（左坡向阳、右坡背光，冲沟顺着坡往下斜）、层理、空气透视
  沙丘         一座座沙丘（迎风坡亮、风纹；背风的滑落面是一块月牙形的阴影、上面有崩落的竖纹；脊线一道亮边 / 背风侧墨线），
               从远到近画，后画的盖前面
  地面         可走带的沙地（底色 + 很淡的风纹，越往下越疏 = 近大远小；可走带对比压低）、碎石、干草、灌木、枯树
  岩石         砂岩露头：多边形拼形状 → 遮罩着色（左沿 / 顶面亮、正面中间调、右侧背光、层理、裂缝、风蚀洞、
               沙漆往下淌的暗纹、右下墨线、脚下的沙堆）+ 往右前方投到可走带上的影子（剧情用影子判“在阴影里”）
  骨头         牛头骨（半埋）、散骨、骆驼骨架
  会动的       热浪（某一层的几行按行横移 = 扭曲，加海市蜃楼的“水光”）、盘旋的秃鹫、尘卷风、沙脊扬沙
  图层表       场景模块把图层写成一张表（static / wrap / pano / strip / clouds / pick / tint，可带 key），
               export_layers 导出成 stage、compose 用内存里的原图直接拼（自检对照导出）、std_checks 公用自检
注意：bg_jojo.ref_render（预览 / 自检的 Python 版拼图公式）不认识 glow / stars 图层（singapore_hotel.py 踩过），
所以篝火光、星星闪都烘进底图 + strip，不用这两种图层；图层也不用 alpha / blend 字段（ref_render 不处理，JS 和预览会不一样）。
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _load(name):
    """按路径加载 tools\\bg_new\\<name>.py（模块名同 bg_jojo.bg_new 的约定，已经加载过就直接复用）。"""
    key = 'bg_new_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


V = _load('varanasi_street')
C = A._c4
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, cast_shadow, haze, opaque = (V.mul_box, V.mul_mask, V.poly_mask, V.cast_shadow,
                                                           V.haze, V.opaque)
SHADOW_MUL, SOFT_MUL = V.SHADOW_MUL, V.SOFT_MUL

W, H = 320, 180
PW = 640
N_ANIM, FPS_ANIM = 8, 4.0


def layer_w(k, pw=PW):
    """视差 k 的全景层要多宽（镜头从 0 走到 pw − 320 时这一层露出来的范围）。"""
    return W + int(math.ceil((pw - W) * k))


def frame_of(t, n, fps):
    return int(math.floor(t * fps + 1e-6)) % n


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def smooth(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


# ============================================================ 噪声 / 抖动
def fbm1(n, cell, seed, octaves=4, period=None):
    """1D 值噪声 fbm，值域约 [-1, 1]，长度 n。period 给了就以 period 首尾循环（wrap 层的地面起伏要接得上）。"""
    xs = np.arange(n, dtype=np.float64)
    out = np.zeros(n)
    amp, tot, c = 1.0, 0.0, float(cell)
    for o in range(octaves):
        if period:
            m = max(1, int(round(period / c)))
            c = period / m
        else:
            m = int(math.ceil(n / c)) + 2
        g = np.array([hash01(seed, o, i) for i in range(m + 2)]) * 2 - 1
        u = xs / c
        i0 = np.floor(u).astype(int)
        f = u - i0
        f = f * f * (3 - 2 * f)
        if period:
            a, b = g[i0 % m], g[(i0 + 1) % m]
        else:
            a, b = g[np.clip(i0, 0, m + 1)], g[np.clip(i0 + 1, 0, m + 1)]
        out += (a + (b - a) * f) * amp
        tot += amp
        amp *= 0.5
        c = max(1.0, c / 2)
    return out / tot


def vnoise2(w, h, cx, cy, seed, period=None):
    """各向异性的 2D 值噪声（cx / cy = 横 / 竖方向的格子大小），[0, 1]。岩石的层理纹要横着拉长，冲沟要竖着拉长。
    period（= w）给了就横向首尾循环（第三轮加：滑翔段 wrap 层的岩山纹理在接缝处要接得上）。"""
    rng = np.random.default_rng(seed)
    if period:
        m = max(1, int(round(period / cx)))
        cx = period / m
        gw, gh = m + 3, int(h / cy) + 3
    else:
        gw, gh = int(w / cx) + 3, int(h / cy) + 3
    g = rng.random((gh, gw))
    if period:
        g[:, m:] = g[:, :gw - m]
    ys = np.arange(h, dtype=np.float64) / cy
    xs = np.arange(w, dtype=np.float64) / cx
    y0 = np.floor(ys).astype(int)
    x0 = np.floor(xs).astype(int)
    if period:
        x0 = x0 % m
    fy = smooth(ys - y0)
    fx = smooth(xs - np.floor(xs))
    a = g[y0][:, x0]
    b = g[y0][:, x0 + 1]
    c = g[y0 + 1][:, x0]
    d = g[y0 + 1][:, x0 + 1]
    top = a + (b - a) * fx[None, :]
    bot = c + (d - c) * fx[None, :]
    return top + (bot - top) * fy[:, None]


def fbm2(w, h, cx, cy, seed, octaves=3, period=None):
    out = np.zeros((h, w))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        out += vnoise2(w, h, max(1.0, cx / 2 ** o), max(1.0, cy / 2 ** o), seed + 31 * o, period=period) * amp
        tot += amp
        amp *= 0.5
    return out / tot


@lru_cache(maxsize=8)
def bayer(w, h):
    return A._bayer(w, h)


def dq(v, levels, bay):
    """连续的档位 v（0 … levels−1）→ 整数档；小数部分按 Bayer 阈值抖动（像素画的渐变过渡）。"""
    b = np.floor(v)
    return np.clip(b + ((v - b) > bay), 0, levels - 1).astype(int)


def run_lengths(m):
    """遮罩里每个像素到左 / 右 / 上 / 下边界的距离（含自己，= 1 就是贴边的那一圈）。岩石按它判断哪是左沿、哪是顶面。"""
    hh, ww = m.shape
    dl = np.zeros(m.shape, np.int32)
    dr = np.zeros(m.shape, np.int32)
    dt = np.zeros(m.shape, np.int32)
    db = np.zeros(m.shape, np.int32)
    acc = np.zeros(hh, np.int32)
    for x in range(ww):
        acc = np.where(m[:, x], acc + 1, 0)
        dl[:, x] = acc
    acc = np.zeros(hh, np.int32)
    for x in range(ww - 1, -1, -1):
        acc = np.where(m[:, x], acc + 1, 0)
        dr[:, x] = acc
    acc = np.zeros(ww, np.int32)
    for y in range(hh):
        acc = np.where(m[y], acc + 1, 0)
        dt[y] = acc
    acc = np.zeros(ww, np.int32)
    for y in range(hh - 1, -1, -1):
        acc = np.where(m[y], acc + 1, 0)
        db[y] = acc
    return dl, dr, dt, db


def edge_masks(m):
    """遮罩的四条边：右边 / 下边（画墨线）、左边 / 上边（画亮边）。"""
    def sh(dx, dy):
        o = np.zeros_like(m)
        hh, ww = m.shape
        ys0, ys1 = max(0, dy), hh + min(0, dy)
        xs0, xs1 = max(0, dx), ww + min(0, dx)
        o[ys0:ys1, xs0:xs1] = m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
        return o
    right = m & ~sh(-1, 0)
    left = m & ~sh(1, 0)
    bottom = m & ~sh(0, -1)
    top = m & ~sh(0, 1)
    return left, right, top, bottom


def regrade(im, ramp, keep=0.25, mul=(1.0, 1.0, 1.0)):
    """换时段的调色（梯度映射）：按亮度从 ramp（[(亮度 0–1, 颜色), ...]）取颜色，再混回一点原色（keep，留住材质的色相差），
    透明度不变。傍晚 / 黎明的 pick 层用它从白天的图层直接算出来（形状、像素位置和原图一模一样，盖上去严丝合缝）。"""
    a = np.array(im).astype(np.float64)
    l = lum(a) / 255.0
    pos = np.array([p_ for p_, _ in ramp])
    cols = np.array([c for _, c in ramp], np.float64)
    rc = np.stack([np.interp(l, pos, cols[:, k]) for k in range(3)], -1)
    out = rc * (1 - keep) + a[..., :3] * np.array(mul) * keep
    a[..., :3] = np.clip(out, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def crop_alpha_rows(im):
    """上下裁掉全透明的行：返回 (图, y0)（pick 层自己带 y，省 KB）。"""
    bb = im.getchannel('A').getbbox()
    if not bb:
        return im, 0
    return im.crop((0, bb[1], im.width, bb[3])), bb[1]


def time_pick(name, key, img, k, ramp, keep=0.25, mul=(1.0, 1.0, 1.0)):
    """某一层的“换时段”版本做成 pick（values [0, 1]：0 = 1×1 透明，1 = 梯度映射后的整层，同一个视差 k）。"""
    g, y = crop_alpha_rows(regrade(img, ramp, keep, mul))
    return dict(type='pick', name=name, key=key, values=[0, 1], imgs=[blank1(), g], k=k, x=0, y=y)


# ============================================================ 天
def sky_base(stops, bands=14, h=H, w=W):
    im = A._new(w, h)
    gradient(im, (0, 0, w, h), stops, bands=bands)
    return im


def sun(im, cx, cy, r, core, rim, glow, glow_r, glow_a, rings=6):
    """太阳：几圈台阶状的光晕（真半透明叠在天上，天是整张不透明的，叠完还是不透明）+ 亮边 + 白芯。"""
    A._glow(im, cx, cy, glow_r, glow_r * 0.92, glow, glow_a, rings=rings)
    d = ImageDraw.Draw(im)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C(rim))
    d.ellipse((cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1), fill=C(core))


def cirrus_img(period, h, n, seed, col, col2, slope=0.07, strands=(2, 4)):
    """卷云（period 宽、首尾循环）：一缕缕往右上扬的细丝（马尾云）。每缕是几根挨着的弯丝，丝中间厚（2–3 px）、
    两头细，用 Bayer 抖动出“半透明”（其实只是比天亮一两档的不透明像素），丝尾往下勾一下。
    col 是丝芯的亮色、col2 是丝边更淡的一档。只为了天不是一整片平色，所以压得很淡。"""
    a = np.zeros((h, period, 4), np.uint8)
    bay = bayer(period, h)
    for i in range(n):
        x0 = hrange(0, period, seed, i, 1)
        y0 = hrange(8, h - 8, seed, i, 2)
        L = hrange(46, 120, seed, i, 3)
        ns = int(hrange(strands[0], strands[1] + 1, seed, i, 4))
        for s_ in range(ns):
            sx = x0 + hrange(-8, 14, seed, i, s_, 5)
            sy = y0 + s_ * hrange(2.5, 4.5, seed, i, s_, 6)
            sl = L * hrange(0.55, 1.0, seed, i, s_, 7)
            th = hrange(0.8, 1.9, seed, i, s_, 8)
            curl = hrange(-3, 3, seed, i, s_, 9)
            for k in range(int(sl)):
                u = k / sl
                hook = 3.5 * max(0.0, (u - 0.86) / 0.14) ** 2         # 丝尾往下勾
                yc = sy - k * slope + curl * math.sin(u * math.pi) + 0.7 * math.sin(k * 0.11 + i) + hook
                tt = th * math.sin(math.pi * min(1.0, u * 1.1)) ** 0.6
                xx = int(round(sx + k)) % period
                for dy in range(-2, 3):
                    v = 1 - abs(dy - (yc - math.floor(yc))) / (tt + 0.6)
                    if v <= 0:
                        continue
                    yy = int(math.floor(yc)) + dy
                    if 0 <= yy < h and bay[yy, xx] < v * 0.85:
                        a[yy, xx, :3] = col if v > 0.5 else col2
                        a[yy, xx, 3] = 255
    return Image.fromarray(a, 'RGBA')


def cumulus_row(period, h, specs, pal, seed):
    """一排积云（period 宽、首尾循环）：specs = [(中心 x, 底 y, 宽, 高比), ...]。"""
    im = A._new(period, h)
    for i, (cx, by, w, hr) in enumerate(specs):
        cl = A._cloud_sprite(w, w * hr, seed + i, pal)
        for dx in (-period, 0, period):
            paste(im, cl, int(cx + dx - cl.width / 2), int(by - cl.height))
    return im


# ============================================================ 岩山（远景）
def paint_ridge(im, x0, x1, base, hts, pal, seed, strata=6, shear=0.8, bottom=None, light='left', period=None):
    """一道岩山：hts = 每列的山高（numpy，长度 x1−x0，像素）；从山脊画到 bottom（默认 base）。
    明暗：山脊往右升的坡朝左上（向阳，亮）、往右降的坡背光（暗）；坡面上是顺着坡往下斜的冲沟（左坡往左下、
    右坡往右下），冲沟一侧亮一侧暗；越往山脚越接近正面的中间调。再加几道横的层理（阿拉伯的山是沉积岩）、
    向阳的山脊线一道亮边。pal = (deep, shade, mid, lit, hi)。
    period（= x1 − x0）给了就整层横向首尾循环：冲沟 / 斑驳 / 层理的噪声都按 period 循环（滑翔段的 wrap 层用）。"""
    bottom = base if bottom is None else bottom
    w = x1 - x0
    a = np.array(im)
    hts = np.asarray(hts, np.float64)
    top = base - hts
    ts = np.convolve(np.pad(top, 3, mode='edge'), np.ones(7) / 7, mode='valid')
    slope = np.gradient(ts)                                   # dtop/dx：< 0 = 往右升 = 朝左的坡
    geo = np.tanh(-slope * 1.6)                                # +1 朝左的坡 / −1 朝右的坡
    face = -geo if light == 'right' else geo                   # +1 向光；夜里月亮在右上，朝右的坡亮
    Y = np.arange(H, dtype=np.float64)[:, None]
    X = np.arange(w, dtype=np.float64)[None, :]
    depth = Y - top[None, :]
    inside = (depth >= 0) & (Y <= bottom)
    s = shear * np.sign(geo)[None, :]                          # 冲沟顺着坡往下斜（只看坡朝哪边，和光无关）
    xg = X + s * depth                                         # 同一条冲沟上 xg 不变
    if period:
        g = fbm1(w, 7.0, seed, octaves=4, period=w)
        gi = np.mod(xg, w)
        i0 = np.floor(gi).astype(int) % w
        fr = gi - np.floor(gi)
        gv = g[i0] * (1 - fr) + g[(i0 + 1) % w] * fr
        dg = np.roll(gv, -1, axis=1) - np.roll(gv, 1, axis=1)
    else:
        span = int(w + shear * H * 2 + 40)
        g = fbm1(span, 7.0, seed, octaves=4)
        gi = np.clip(xg + shear * H + 20, 0, span - 1.001)
        i0 = np.floor(gi).astype(int)
        fr = gi - i0
        gv = g[i0] * (1 - fr) + g[np.minimum(i0 + 1, span - 1)] * fr
        dg = np.zeros_like(gv)
        dg[:, 1:-1] = (gv[:, 2:] - gv[:, :-2])
    nz = fbm2(w, H, 5, 3, seed + 7, period=w if period else None)
    fade = np.exp(-np.clip(depth, 0, None) / 30.0)
    lev = 2.0 + 1.05 * face[None, :] * (0.35 + 0.65 * fade) + 5.0 * dg + 0.5 * (nz - 0.5)
    for k in range(strata):                                    # 层理：一道道略暗的横线（断断续续）
        fq = (2 * math.pi / w * max(1, round(w / (13.0 * 2 * math.pi)))) if period else 1 / 13.0   # 循环时波长取整
        yy = base - (k + 1) * (hts.max() / (strata + 1)) + 1.5 * np.sin(X * fq + k)
        m = (np.abs(Y - yy) < 0.6) & (vnoise2(w, H, 6, 50, seed + k, period=w if period else None)[..., :] > 0.35)
        lev = np.where(m, lev - 0.7, lev)
    bay = bayer(w, H)
    li = dq(lev, len(pal), bay)
    cols = np.array(pal, np.uint8)
    sub = a[:, x0:x1]
    sub[inside, :3] = cols[li][inside]
    sub[inside, 3] = 255
    # 山脊线：向阳的坡一道亮边，背光的坡一道暗边（让一层层山脊分得开）
    for x in range(w):
        y = int(math.ceil(top[x]))
        if 0 <= y < H and y <= bottom:
            sub[y, x, :3] = pal[-1] if face[x] > -0.2 else pal[1]
            sub[y, x, 3] = 255
    a[:, x0:x1] = sub
    im.paste(Image.fromarray(a, 'RGBA'))


def ridge_heights(w, peaks, seed, jag=0.22, cell=9.0, period=None):
    """山高：几座山峰（(x, 高, 半宽, 偏斜)，三角形略带弧）取最大，再乘一层锯齿噪声（岩山的嶙峋山脊）。"""
    xs = np.arange(w, dtype=np.float64)
    h = np.zeros(w)
    for (cx, ph, hw, sk) in peaks:
        for dx in ((-period, 0, period) if period else (0,)):
            u = (xs - cx - dx) / hw
            uu = np.where(u < 0, -u / (1 + sk), u / max(0.2, 1 - sk))
            prof = np.clip(1 - uu, 0, None) ** 1.25
            h = np.maximum(h, ph * prof)
    n = fbm1(w, cell, seed, octaves=4, period=period)
    return np.clip(h * (1 + jag * n) + 1.5 * n, 0, None)


def mesa_heights(w, mesas, seed, jag=0.06, period=None):
    """平顶山（阿拉伯的砂岩台地 / 孤山）：mesas = [(x, 高, 顶半宽, 坡宽), ...]：顶上一段平（带一点缺口和台阶），
    两边先是陡崖、往下变成缓的碎石坡（凹的）。比尖山更像沙漠里的岩山，也不会和金字塔混。"""
    xs = np.arange(w, dtype=np.float64)
    h = np.zeros(w)
    for i, (cx, ph, ht, side) in enumerate(mesas):
        for dx in ((-period, 0, period) if period else (0,)):
            d = np.abs(xs - cx - dx) - ht
            cliff = np.clip(1 - np.clip(d, 0, None) / side, 0, 1) ** 0.55
            prof = np.where(d <= 0, 1.0, cliff)
            step = np.where((d > side * 0.18) & (d < side * 0.3), 0.06, 0.0)        # 崖下一级小台阶
            h = np.maximum(h, ph * np.clip(prof - step, 0, 1))
    n = fbm1(w, 5.0, seed, octaves=3, period=period)
    notch = np.where(fbm1(w, 11.0, seed + 1, octaves=2, period=period) > 0.45, -1.5, 0.0)
    return np.clip(h * (1 + jag * n) + notch * (h > 4), 0, None)


# ============================================================ 沙丘
def dune_y(x, cx, top, base, wl, wr, p=1.0, q=1.6):
    """沙丘在 x 处的顶面 y：左边迎风坡（S 形：坡脚缓、中段陡一点、近顶圆）、右边背风的滑落面（陡、到坡脚变缓）。
    q ≤ 0（第三轮加）：右边也用余弦坡 = 圆顶的缓丘（没有尖脊）。desert_day 的远 / 中景用：一排尖脊的小沙丘
    在埃及的天底下远看就是一排小金字塔。"""
    if x <= cx:
        u = max(0.0, min(1.0, (x - (cx - wl)) / wl))
        return base - (base - top) * ((1 - math.cos(math.pi * u)) / 2) ** p
    v = max(0.0, min(1.0, (x - cx) / wr))
    if q <= 0:
        return top + (base - top) * (1 - math.cos(math.pi * v)) / 2
    return top + (base - top) * (1 - (1 - v) ** q)


def crest_pts(cx, top, base, bl, wob, seed, n=18):
    """脊线（迎风坡和滑落面的分界）：从脊顶往左下扫到坡脚——先往下多、后往左多（月牙的“角”贴着坡脚伸出去），
    中段带一点 S 形的扭。直线的脊会让沙丘像金字塔，所以一定要弯。"""
    pts = []
    for j in range(n + 1):
        s = j / n
        y = top + (base - top) * (1 - (1 - s) ** 1.35)
        x = cx - bl * s ** 1.9 + wob * math.sin(math.pi * s * 1.4 + seed) * s * (1 - s) * 3
        pts.append((x, y))
    return pts


def dune_row(x0, x1, base, hmin, hmax, seed, ratio=(2.6, 3.6), slip=(0.38, 0.55), bl=(0.3, 0.5), overlap=(0.15, 0.5),
             base_jit=2.0, big=None, sweep='lee'):
    """一排连在一起的新月形沙丘（像一道波浪形的沙脊：⌒⌒⌒，每个弧的右边挂一块月牙影）：
    从 x0 往右一座接一座，下一座的迎风坡从上一座的滑落面里起来（互相压着，不会有孤零零的三角形 = 金字塔）。
    big = [(第几座, 高)]：把某几座加高成大沙丘。返回 paint_dunes 用的 dict 列表（从左到右）。
    sweep：脊线（亮面 / 影子的分界）从脊顶往哪边扫到坡脚。
      'lee'（默认，2026-10-19 第三轮改）：往右下扫，影子是贴着右边滑落面的一弯月牙——看起来像一道道沙浪；
      'wind'（第二轮的画法）：往左下扫 bl × 迎风坡长，影子在脊顶下面摊成一个三角，远看像金字塔，所以不再默认用。"""
    out = []
    x, i = x0, 0
    bigd = dict(big or [])
    while x < x1:
        h = bigd.get(i, hrange(hmin, hmax, seed, i, 1))
        wl = h * hrange(ratio[0], ratio[1], seed, i, 2)
        wr = max(6.0, h * 1.6 * hrange(slip[0], slip[1], seed, i, 3) / 0.45)
        cx = x + wl
        b = base + hrange(-base_jit, base_jit, seed, i, 6)
        sw = (-wr * hrange(0.45, 0.62, seed, i, 4)) if sweep == 'lee' else wl * hrange(bl[0], bl[1], seed, i, 4)
        out.append(dict(cx=cx, top=b - h, base=b, wl=wl, wr=wr, bl=sw, q=1.3,
                        wob=hrange(-3, 3, seed, i, 5)))
        x = cx + wr * hrange(overlap[0], overlap[1], seed, i, 7)
        i += 1
    return out


def _poly_np(ww, hh, pts):
    m = Image.new('L', (ww, hh), 0)
    ImageDraw.Draw(m).polygon([(round(x), round(y)) for (x, y) in pts], fill=255)
    return np.array(m) > 0


def paint_dunes(im, dunes, pal, seed, ripples=True, rip_gap=4.0, streaks=True, period=None):
    """一排沙丘（从远到近画，后画的盖前面）。dunes = [dict(cx, top, base, wl, wr, bl, kind, ...), ...]：
      cx 脊顶 x、top 脊顶 y、base 坡脚 y、wl 迎风坡长、wr 滑落面长、bl 脊线往左下扫多远；
      kind 'crescent'（默认，月牙：脊线右边是背光的滑落面）/ 'whale'（鲸背丘：没有滑落面，只是往右慢慢暗下去）/
           'star'（星状丘：滑落面里再伸出一条往右下的“臂”，臂的左侧一溜亮）；
      可选 p / q（迎风坡 / 滑落面的形状指数）、wob（脊线扭多少）、arm = (va, ext, wb)（星状丘的臂）。
    pal（dict）：hi 脊线亮边、lit 迎风坡上段、lit2 迎风坡下段、toe 坡脚、rip / rip_hi 风纹的暗线 / 亮线、
                 sh 滑落面、sh_d 滑落面靠脊的深色、sh_l 滑落面坡脚的反光、ink 背风侧轮廓。
    period 给了就按 period 首尾循环（wrap 层用）。"""
    a = np.array(im)
    hh, ww = a.shape[:2]
    bay = bayer(ww, hh)
    lit_cols = np.array([pal['toe'], pal['lit2'], pal['lit'], pal['hi']], np.uint8)
    sh_cols = np.array([pal['sh_d'], pal['sh'], pal['sh_l']], np.uint8)
    reps = (-period, 0, period) if period else (0,)
    Yf = np.arange(hh, dtype=np.float64)[:, None]
    for di, D in enumerate(dunes):
        cx0, top, base, wl, wr = D['cx'], D['top'], int(round(D['base'])), D['wl'], D['wr']
        bl = D.get('bl', wl * 0.3)
        kind = D.get('kind', 'crescent')
        p, q, wob = D.get('p', 1.0), D.get('q', 1.6), D.get('wob', 2.0)
        for rep in reps:
            cx = cx0 + rep
            xa, xb = int(math.floor(cx - wl)), int(math.ceil(cx + wr))
            if xb < 0 or xa >= ww:
                continue
            xs = np.arange(max(0, xa), min(ww, xb + 1))
            prof = np.array([dune_y(x, cx, top, base, wl, wr, p, q) for x in xs])
            ytop = np.ceil(prof - 0.3).astype(int)
            body = (Yf >= ytop[None, :]) & (Yf <= base)
            hfrac = np.clip((Yf - prof[None, :]) / max(1.0, base - top), 0, 1)
            cp = crest_pts(cx, top, base, bl, wob, seed + di)
            if kind == 'whale':
                # 鲸背丘：脊顶右边按离脊顶的距离慢慢转暗（宽的抖动过渡）
                gx = (xs - cx) / max(1.0, wr)
                shade_amt = np.clip(gx * 1.2 - 0.1, 0, 1)[None, :] * (0.4 + 0.6 * (1 - hfrac))
                slip = body & (shade_amt > bay[:, xs] * 0.9 + 0.05)
            else:
                pts = cp + [(cx + wr, base + 1)] + [(x, dune_y(x, cx, top, base, wl, wr, p, q))
                                                     for x in range(int(cx + wr), int(cx), -1)]
                slip = _poly_np(ww, hh, pts)[:, xs] & body
            lit = body & ~slip
            # 迎风坡：近脊亮、往坡脚暗；紧贴脊线左边 4 px 再亮一档（锐利的沙脊迎着光）
            xc_row = np.interp(np.arange(hh), [q_[1] for q_ in cp], [q_[0] for q_ in cp])
            near_crest = (xc_row[:, None] - xs[None, :] >= 0) & (xc_row[:, None] - xs[None, :] < 4) & \
                (Yf > top + 1) & (Yf < base - 2)
            lv = 3.15 - 2.7 * hfrac ** 0.8 + np.where(near_crest, 0.7, 0.0)
            li = dq(lv, 4, bay[:, xs])
            sv = 0.25 + 2.1 * hfrac ** 0.9                         # 滑落面：靠脊深、坡脚有反光
            si = dq(sv, 3, bay[:, xs])
            sub = a[:, xs]
            sub[lit, :3] = lit_cols[li][lit]
            sub[slip, :3] = sh_cols[si][slip]
            sub[body, 3] = 255
            # 星状丘的臂：滑落面里一条往右下的脊，左侧一溜亮
            if kind == 'star' and D.get('arm'):
                va, ext, wb = D['arm']
                ax = cx + wr * va
                ay = dune_y(ax, cx, top, base, wl, wr, p, q)
                bx = cx + wr + ext
                mx_ = (ax + bx) / 2 - 3
                my_ = (ay + base) / 2 + 2
                wedge = _poly_np(ww, hh, [(ax, ay), (mx_, my_), (bx, base), (bx - wb, base), (mx_ - wb * 0.5, my_)])
                wedge = wedge[:, xs] & body
                wl_ = dq(2.6 - 1.8 * hfrac, 4, bay[:, xs])
                sub[wedge, :3] = lit_cols[wl_][wedge]
                arm_edge = wedge & ~np.roll(wedge, -1, axis=1)
                arm_edge[:, -1] = False
                sub[arm_edge, :3] = pal['hi']
                lit = lit | wedge
                slip = slip & ~wedge
            # 风纹：一道道细波纹（暗线 + 上面一行亮线），近脊处顺着坡顶弯、往下变成横的；只在亮的坡面上，碰到滑落面就断
            if ripples:
                nrip = int((base - top) / rip_gap) + 2
                for j in range(1, nrip):
                    y0 = top + j * rip_gap + hrange(-0.8, 0.8, seed, di, j, 1)
                    for ix, x in enumerate(xs):
                        if hash01(seed, di, j, (x - int(cx)) // 6) < 0.2:
                            continue
                        yy = max(y0, prof[ix] + 1.6 + j * 0.35) + 0.9 * math.sin(x * 0.19 + j * 1.7) \
                            + 0.6 * math.sin(x * 0.051 + j)
                        y = int(round(yy))
                        if y >= base - 1 or y <= ytop[ix]:
                            continue
                        if lit[y, ix] and lit[min(hh - 1, y + 1), ix]:
                            sub[y, ix, :3] = pal['rip']
                            if lit[y - 1, ix] and y - 1 > ytop[ix]:
                                sub[y - 1, ix, :3] = pal['rip_hi']
            # 滑落面上崩落的竖纹（沙子一道道往下流的痕迹）
            if streaks and kind != 'whale':
                for j in range(int(wr / 3.5)):
                    sx = cx + hrange(-bl * 0.5, wr * 0.85, seed, di, j, 21)
                    ix = int(round(sx)) - xs[0]
                    if not (0 <= ix < len(xs)):
                        continue
                    col = pal['sh_d'] if hash01(seed, di, j, 22) < 0.55 else pal['sh_l']
                    ys = np.nonzero(slip[:, ix])[0]
                    if not len(ys):
                        continue
                    L = int(hrange(3, max(4, len(ys) * 0.7), seed, di, j, 23))
                    y0 = ys[0] + int(hrange(1, 4, seed, di, j, 24))
                    for k in range(L):
                        y = y0 + k
                        xx = ix + k // 6
                        if 0 <= xx < len(xs) and y < hh and slip[y, xx]:
                            sub[y, xx, :3] = col
            # 轮廓：迎风坡的脊线亮边、背风坡轮廓一道深色、脊线（亮的那一侧）一道亮边 = 锐利的沙脊；坡脚一线暗
            for ix, x in enumerate(xs):
                y = ytop[ix]
                if 0 <= y < hh and y <= base:
                    sub[y, ix, :3] = pal['hi'] if (lit[y, ix] and x <= cx + 1) else pal['ink']
                if 0 <= base < hh and body[base, ix]:
                    sub[base, ix, :3] = pal['toe'] if lit[base, ix] else pal['sh_d']
            edge = lit & np.roll(slip, -1, axis=1)
            edge[:, -1] = False
            sub[edge, :3] = pal['hi']
            a[:, xs] = sub
    im.paste(Image.fromarray(a, 'RGBA'))


# ============================================================ 地面
def paint_floor(im, x0, x1, top, bottom, pal, seed, gap0=3.0, gap1=8.0, dash=0.25, contrast=1.0, period=None):
    """沙地（top 是每列的后沿 y，numpy，长度 x1−x0）：底色 + 一道道很淡的横向风纹（暗线 + 上面一行亮线，波浪形、
    断断续续；越往下（越近）越疏）+ 后沿一道亮边。pal = dict(base, rip, rip_hi, lip)。可走带上不画别的。"""
    d = ImageDraw.Draw(im)
    for i, x in enumerate(range(x0, x1)):
        vl(d, x, int(top[i]), bottom, pal['base'])
    a = np.array(im)
    y = float(np.min(top)) + 2
    j = 0
    rows = []
    while y < bottom:
        rows.append((y, j))
        u = (y - np.min(top)) / max(1.0, bottom - np.min(top))
        y += gap0 + (gap1 - gap0) * u + hrange(-0.6, 0.6, seed, j, 1)
        j += 1
    for (yb, j) in rows:
        for i, x in enumerate(range(x0, x1)):
            xx = x % period if period else x
            if hash01(seed, j, xx // int(hrange(5, 14, seed, j, 2))) < dash:
                continue
            yy = int(round(yb + 1.1 * math.sin(xx * 0.11 + j * 1.9) + 0.7 * math.sin(xx * 0.037 + j)))
            if yy <= top[i] + 1 or yy >= bottom:
                continue
            a[yy, x, :3] = pal['rip']
            if yy - 1 > top[i]:
                a[yy - 1, x, :3] = pal['rip_hi']
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for i, x in enumerate(range(x0, x1)):
        px(d, x, int(top[i]), pal['lip'])


def pebble(d, x, y, col, hi, sh, w=2, h=1):
    """一颗小石子：亮的上沿 + 暗的下沿 / 右沿（光从左上来）。"""
    rect(d, x, y - h + 1, x + w - 1, y, col)
    hl(d, x, x + w - 2, y - h + 1, hi)
    hl(d, x + 1, x + w, y + 1, sh)
    px(d, x + w - 1, y, sh)


def tuft(d, x, y, h, col, col2, seed, lean=0):
    """一撮干草：几根 1 px 的草叶从一点往上张开（光从左上，左边的叶子亮一点）。"""
    n = int(hrange(3, 6, seed, 1))
    for k in range(n):
        u = (k / max(1, n - 1)) * 2 - 1
        L = int(round(h * hrange(0.6, 1.0, seed, k, 2)))
        c = col if u < 0.2 else col2
        for r in range(L):
            xx = x + int(round(u * r * 0.55 + lean * r / max(1, L)))
            px(d, xx, y - r, c)


def shrub(im, x, y, w, h, seed, pal):
    """沙漠里的矮灌木（骆驼刺 / 盐木）：从根部分出几根弯枝，枝上一团团灰绿的小叶（左上亮、右下暗），根部一圈影子。
    pal = (枝, 叶暗, 叶, 叶亮)。"""
    d = ImageDraw.Draw(im)
    br, ld, lm, lh = pal
    n = int(hrange(4, 7, seed, 1))
    tips = []
    for k in range(n):
        ang = math.pi * (0.15 + 0.7 * (k + hrange(-0.3, 0.3, seed, k, 2)) / max(1, n - 1))
        L = h * hrange(0.65, 1.0, seed, k, 3)
        ex = x + math.cos(ang) * w * 0.55 * (L / h)
        ey = y - math.sin(ang) * L
        mx_, my_ = (x + ex) / 2 + hrange(-1, 1, seed, k, 4), (y + ey) / 2 - 1
        d.line([(x, y), (round(mx_), round(my_)), (round(ex), round(ey))], fill=C(br))
        tips.append((ex, ey))
    for k, (ex, ey) in enumerate(tips):
        for j in range(int(hrange(2, 4, seed, k, 5))):
            bx = ex + hrange(-2.0, 2.0, seed, k, j, 6)
            by = ey + hrange(-1.0, 2.0, seed, k, j, 7)
            r = hrange(0.6, 1.3, seed, k, j, 8)
            d.ellipse((bx - r, by - r * 0.8 + 1, bx + r, by + r * 0.8 + 1), fill=C(ld))
            d.ellipse((bx - r, by - r * 0.8, bx + r, by + r * 0.8), fill=C(lm))
            if by < y - h * 0.5 and bx < x + w * 0.2:
                px(d, int(bx - 0.5), int(by - 0.5), lh)


def dead_tree(im, x, y, h, seed, col, hi, sh):
    """一棵枯死的金合欢 / 柽柳：主干往上分两三次叉，枝梢细；左边一线亮（光从左上）、右边暗。"""
    d = ImageDraw.Draw(im)

    def branch(x0, y0, ang, L, wdt, lvl):
        x1 = x0 + math.cos(ang) * L
        y1 = y0 - math.sin(ang) * L
        steps = max(2, int(L))
        for s in range(steps + 1):
            u = s / steps
            xx = x0 + (x1 - x0) * u
            yy = y0 + (y1 - y0) * u
            ww_ = max(0, int(round(wdt * (1 - 0.6 * u))))
            for k in range(-ww_ // 2, ww_ - ww_ // 2 + 1):
                c = hi if k == -ww_ // 2 and ww_ > 0 else (sh if k == ww_ - ww_ // 2 and ww_ > 0 else col)
                px(d, int(round(xx)) + k, int(round(yy)), c)
        if lvl < 3:
            nb = 2 if lvl else 3
            for j in range(nb):
                da = hrange(-0.75, 0.75, seed, lvl, j, int(x0), 1)
                branch(x1, y1, ang + da, L * hrange(0.5, 0.75, seed, lvl, j, 2), max(0, wdt - 1), lvl + 1)
    branch(x, y, math.pi / 2 + hrange(-0.15, 0.15, seed, 3), h * 0.42, 2, 0)


def caravan(d, x, y, n, col, col2, seed=0, riders=(1, 3), facing=1):
    """远处地平线上的一支驼队剪影（每峰骆驼 9×6：驼峰、长脖子、四条腿两两错开），有的背上坐着人，最前面一个牵骆驼的人。
    x, y = 第一峰骆驼的左脚、地平线；facing = 1 朝右走。"""
    camel = ["......xx.", "..xx...x.", ".xxxxxxx.", ".xxxxx...", ".x.x.x...", ".x..x.x.."]
    for i in range(n):
        cx = x + i * 11 * facing
        for r, row in enumerate(camel):
            for c, ch in enumerate(row):
                if ch == 'x':
                    cc = c if facing > 0 else 8 - c
                    px(d, cx + cc, y - 5 + r, col if r < 4 else col2)
        if i in riders:
            hx = cx + (3 if facing > 0 else 5)
            vl(d, hx, y - 7, y - 5, col)
            px(d, hx, y - 8, col2)
    lx = x + (n * 11 + 1) * facing if facing > 0 else x - 13
    vl(d, lx, y - 4, y - 1, col)                                   # 牵骆驼的人
    px(d, lx, y - 5, col2)
    px(d, lx + facing, y, col2)
    px(d, lx - facing, y, col2)


def boulder(d, x, y, w, h, pal):
    """一块落石 / 碎岩（底在 y）：上沿一线亮、右边和下沿墨线、中间一点暗斑。pal = dict(ink, sh, mid, lit, hi)。"""
    for r in range(h):
        u = r / max(1, h - 1)
        inset = int(round((1 - math.sin(math.pi * (0.5 + 0.5 * u))) * w * 0.25)) if r < h * 0.5 else 0
        hl(d, x + inset, x + w - 1 - inset // 2, y - h + 1 + r, pal['mid'] if r else pal['hi'])
    vl(d, x + w - 1, y - h + 2, y, pal['sh'])
    hl(d, x + 1, x + w - 1, y, pal['ink'])
    vl(d, x + w, y - h + 3, y, pal['ink'])
    px(d, x + 1, y - h + 2, pal['lit'])


def colocynth(d, x, y, w, seed, vine=(108, 128, 66), leaf=(132, 154, 78), fruit=(226, 204, 92), stripe=(120, 150, 70)):
    """药西瓜（阿拉伯沙漠里贴地长的苦瓜藤）：几根贴着沙面的藤、一些小叶子、两三个带绿条纹的小黄瓜。"""
    for k in range(3):
        y0 = y + int(hrange(-1, 1, seed, k, 1))
        for i in range(w):
            yy = y0 + int(round(math.sin(i * 0.5 + k * 2 + seed) * 0.8))
            if hash01(seed, k, i, 2) < 0.75:
                px(d, x + i, yy, vine)
            if hash01(seed, k, i, 3) < 0.25:
                px(d, x + i, yy - 1, leaf)
    for k in range(int(hrange(2, 4, seed, 4))):
        fx = x + int(hrange(1, w - 3, seed, k, 5))
        fy = y + int(hrange(-1, 2, seed, k, 6))
        hl(d, fx, fx + 2, fy, fruit)
        hl(d, fx, fx + 2, fy - 1, fruit)
        px(d, fx + 1, fy - 1, stripe)
        px(d, fx, fy, lt(fruit, 0.3))


# ============================================================ 岩石
def rough_poly(pts, seed, amp=1.0, step=3.0):
    """多边形每条边按 step 细分、往法向随机抖 ±amp（岩石的轮廓不那么规整）。"""
    out = []
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0)
        k = max(1, int(L / step))
        nx, ny = (y1 - y0) / max(L, 1e-6), -(x1 - x0) / max(L, 1e-6)
        for j in range(k):
            u = j / k
            o = hrange(-amp, amp, seed, i, j) if j else 0.0
            out.append((x0 + (x1 - x0) * u + nx * o, y0 + (y1 - y0) * u + ny * o))
    return out


def poly_m(size, polys):
    m = Image.new('L', size, 0)
    dd = ImageDraw.Draw(m)
    for p in polys:
        dd.polygon([(round(x), round(y)) for (x, y) in p], fill=255)
    return np.array(m) > 0


ROCK_KEYS = ('ink', 'deep', 'sh', 'mid', 'lit', 'hi')


def shade_rock(im, mask, pal, seed, bands=None, cracks=6, holes=4, varnish=5, top_hi=True, face_bias=0.0,
               light='left', outline=True, grain=0.55, faces=None):
    """砂岩着色（遮罩 mask 是和 im 同大小的 bool）：
      · 左沿（光从左上）亮、正面中间调、右侧背光；顶面（每列最上面两三行）高光；越往下越暗一点（脚下有沙子挡光）
      · bands：层理 [(厚度, 色偏 dict 或 None), ...]：每层换一套亮度 / 色相，层与层之间一道断续的暗线
      · cracks 条竖裂缝（暗线 + 左边一线亮）、holes 个风蚀洞（暗芯 + 下沿亮）、varnish 道沙漆（从顶往下淌的暗纹）
      · 右边 / 下边一圈墨线（ink），左 / 上边留亮
    light='right' 时左右反过来（夜里月亮在右上）。pal = dict(ink, deep, sh, mid, lit, hi)，可以带 'red' / 'pale' 两套层色。"""
    a = np.array(im)
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    m = mask[y0:y1 + 1, x0:x1 + 1]
    hh, ww = m.shape
    dl, dr, dt, db = run_lengths(m)
    if light == 'right':
        dl, dr = dr, dl
    wid = (dl + dr - 1).astype(np.float64)
    u = (dl - 0.5) / np.maximum(1.0, wid)                        # 0 = 向光那一沿，1 = 背光那一沿
    nz = fbm2(ww, hh, 4, 3, seed)
    # 基础档位：向光一沿 lit、正面 mid、背光一侧 sh → deep（档位尽量落在整数上：像素画的岩面是一块块平色，
    # 只在交界处抖动；整片都在两档之间会变成满屏噪点，第一版就是那样“毛”的）
    uu = u + 0.1 * (fbm2(ww, hh, 3, 6, seed + 9) - 0.5) * 2        # 明暗交界线抖一下（不是笔直的）
    lev = 4.0 - smooth((uu - 0.1) / 0.07) - smooth((uu - 0.58) / 0.08) - 0.9 * smooth((uu - 0.85) / 0.06) + face_bias
    if faces:
        # 方岩：按给定的面（左侧面 / 正面 / 右侧面……）定基础档位，比按左右距离算的“圆柱”更像一块块平的岩面
        for (fm, fl) in faces:
            sel = fm[y0:y1 + 1, x0:x1 + 1] & m
            lev = np.where(sel, fl + face_bias, lev)
    # 斑驳：噪声高的地方亮一档、低的地方暗一档（成片的，不是逐点噪）
    lev = lev + np.where(nz > 0.66, grain, 0.0) - np.where(nz < 0.32, grain, 0.0)
    lev = np.where(dl <= 1, lev + 0.9, lev)                        # 向光的边一线亮
    if top_hi:
        lev = np.where(dt <= 1, lev + 1.5, np.where(dt <= 3, lev + 0.6, lev))
    yy = np.arange(hh)[:, None].astype(np.float64)
    lev = lev - 0.6 * smooth((yy - hh * 0.75) / (hh * 0.25))       # 脚下暗一点（沙子挡光）
    # 层理：每层自己的亮度偏移 + 色相（红层 / 白层），层间一道断续暗线
    band_id = np.zeros(m.shape, np.int32)
    tint = np.zeros(m.shape, np.int32)                             # 0 = 本色，1 = 红层，2 = 白层
    if bands:
        X = np.arange(ww)[None, :]
        yb = yy + 0.06 * X + 1.2 * np.sin(X / 9.0 + seed) + 0.8 * (fbm2(ww, hh, 9, 30, seed + 3) - 0.5) * 3
        acc = 0.0
        edges = []
        for bi, (th, kind) in enumerate(bands):
            acc += th
            edges.append((acc, bi, kind))
        for (lim, bi, kind) in reversed(edges):
            sel = yb < lim
            band_id = np.where(sel, bi, band_id)
            tint = np.where(sel, {'red': 1, 'pale': 2}.get(kind, 0), tint)
            if kind == 'red':
                pass
        for (lim, bi, kind) in edges[:-1]:
            line = (np.abs(yb - lim) < 0.55) & (fbm2(ww, hh, 5, 40, seed + bi) > 0.32)
            lev = np.where(line, lev - 0.9, lev)
        boff = np.array([hrange(-0.35, 0.35, seed, bi, 41) for bi in range(len(bands))])
        lev = lev + boff[band_id]
    bay = bayer(ww, hh)
    li = np.floor(lev + 0.5 + 0.38 * (bay - 0.5)).astype(int)     # 只在离两档中线很近的地方抖动
    li = np.clip(li, 1, 5)                                         # 0 档（ink）只留给墨线 / 裂缝
    pals = [np.array([pal[k] for k in ROCK_KEYS], np.uint8)]
    for key in ('red', 'pale'):
        if key in pal:
            pals.append(np.array([pal[key][k] if k in pal[key] else pal[k] for k in ROCK_KEYS], np.uint8))
        else:
            pals.append(pals[0])
    out = np.zeros((hh, ww, 3), np.uint8)
    for ti in range(3):
        sel = tint == ti
        out[sel] = pals[ti][li][sel]
    # 裂缝
    for c in range(cracks):
        cx = int(hrange(ww * 0.12, ww * 0.88, seed, c, 51))
        col_y = np.nonzero(m[:, cx])[0]
        if not len(col_y):
            continue
        cy = col_y[0] + int(hrange(0, max(1, len(col_y) * 0.5), seed, c, 52))
        L = int(hrange(5, max(6, len(col_y) * 0.7), seed, c, 53))
        x = cx
        for k in range(L):
            y = cy + k
            if y >= hh or not m[y, x]:
                break
            out[y, x] = pals[0][1]
            if x - 1 >= 0 and m[y, x - 1] and light != 'right':
                out[y, x - 1] = pals[tint[y, x - 1]][min(5, li[y, x - 1] + 1)]
            elif x + 1 < ww and m[y, x + 1] and light == 'right':
                out[y, x + 1] = pals[tint[y, x + 1]][min(5, li[y, x + 1] + 1)]
            r = hash01(seed, c, k, 54)
            if r < 0.18:
                x -= 1
            elif r > 0.82:
                x += 1
            x = max(0, min(ww - 1, x))
    # 风蚀洞（tafoni）：暗芯 + 下沿一线亮
    for k in range(holes):
        hx = int(hrange(ww * 0.15, ww * 0.85, seed, k, 61))
        hy = int(hrange(hh * 0.15, hh * 0.7, seed, k, 62))
        rw = int(hrange(1, 3, seed, k, 63))
        rh = max(1, rw - 1)
        if not m[max(0, hy - rh - 1):hy + rh + 2, max(0, hx - rw - 1):hx + rw + 2].all():
            continue
        for y in range(hy - rh, hy + rh + 1):
            for x in range(hx - rw, hx + rw + 1):
                if ((x - hx) / (rw + 0.5)) ** 2 + ((y - hy) / (rh + 0.5)) ** 2 <= 1:
                    out[y, x] = pals[0][1] if y < hy + rh else pals[0][2]
        for x in range(hx - rw + 1, hx + rw):
            out[hy + rh + 1, x] = pals[tint[hy + rh + 1, x]][5]
    # 沙漆：从顶面往下淌的暗纹（隔一个像素压暗一档）
    for k in range(varnish):
        vx = int(hrange(ww * 0.1, ww * 0.95, seed, k, 71))
        col_y = np.nonzero(m[:, vx])[0]
        if not len(col_y):
            continue
        L = int(hrange(4, max(5, len(col_y) * 0.55), seed, k, 72))
        for j in range(L):
            y = col_y[0] + 1 + j
            if y < hh and m[y, vx] and (j % 2 == 0 or j < 3):
                out[y, vx] = pals[tint[y, vx]][max(1, li[y, vx] - 1)]
    # 墨线：背光的一侧 + 下沿；向光一侧的边缘用亮色收（选择性描边）
    if outline:
        left, right, top, bottom = edge_masks(m)
        if light == 'right':
            left, right = right, left
        out[right | bottom] = pal['ink']
        lt_edge = (left | top) & ~(right | bottom)
        out[lt_edge & (li >= 3)] = pal['hi']
    sub = a[y0:y1 + 1, x0:x1 + 1]
    sub[m, :3] = out[m]
    sub[m, 3] = 255
    a[y0:y1 + 1, x0:x1 + 1] = sub
    im.paste(Image.fromarray(a, 'RGBA'))


def rock_shadow(mask, base_y, sx, sy, ground_top=None, dilate=1):
    """岩石往右前方投在地上的影子：遮罩里每个点（离地高 h = base_y − y）落到地上 (x + h·sx, base_y + h·sy)；
    投出来的点补洞、扩一圈，返回和 mask 同大小的 bool。光从左上后方来（太阳在画面里的天上），所以影子往人这边、往右落。"""
    hh, ww = mask.shape
    out = np.zeros_like(mask)
    ys, xs = np.nonzero(mask)
    for (y, x) in zip(ys, xs):
        h = base_y - y
        if h < -1:
            continue
        h = max(0, h)
        gx = x + h * sx
        gy = base_y + h * sy
        for (ax, ay) in ((gx, gy), (gx + 0.5, gy + 0.5), (gx - 0.5, gy + 0.5)):
            ix, iy = int(round(ax)), int(round(ay))
            if 0 <= ix < ww and 0 <= iy < hh:
                out[iy, ix] = True
    # 补洞：每一行最左到最右之间填满（投影是实心的）
    for y in range(hh):
        r = np.nonzero(out[y])[0]
        if len(r) > 1:
            gaps = np.diff(r)
            for i in np.nonzero(gaps <= 4)[0]:
                out[y, r[i]:r[i + 1] + 1] = True
    for _ in range(dilate):
        o2 = out.copy()
        o2[1:] |= out[:-1]
        o2[:, 1:] |= out[:, :-1]
        out = o2
    if ground_top is not None:
        out &= np.arange(hh)[:, None] >= ground_top
    return out & ~mask


def apply_shadow(im, m, mul=SHADOW_MUL):
    mul_mask(im, m, mul)


def sand_drift(im, x0, x1, base_y, peak_x, h, pal, seed):
    """堆在岩石脚下的沙堆（迎风一侧高）：一道往两边低下去的沙坡，顶边一线亮、和岩石交界处一线暗，坡上两三道风纹。"""
    d = ImageDraw.Draw(im)
    for x in range(x0, x1 + 1):
        if x <= peak_x:
            u = (x - x0) / max(1, peak_x - x0)
        else:
            u = 1 - (x - peak_x) / max(1, x1 - peak_x)
        hy = int(round(h * math.sin(max(0.0, min(1.0, u)) * math.pi / 2) ** 1.4))
        if hy <= 0:
            continue
        for y in range(base_y - hy, base_y + 1):
            px(d, x, y, pal['base'])
        px(d, x, base_y - hy, pal['lip'])
        if hy > 3 and hash01(seed, x // 3, 1) < 0.7:
            px(d, x, base_y - hy + 2 + (x // 5) % 2, pal['rip'])
        if hy > 1:
            px(d, x, base_y - hy - 1, pal.get('edge', pal['rip']))


# ============================================================ 骨头
def ox_skull(im, x, y, pal, flip=False):
    """半埋在沙里的牛头骨（13×8，朝左）：一对往上弯的角、额骨、两个黑眼窝、鼻骨往下收，下巴埋在沙里；
    光从左上：左上亮、右下一线暗。x, y = 骨头底（沙面）的中心。pal = dict(bone, hi, sh, dark, sand)。"""
    g = [
        "h..........h.",
        "hh........hh.",
        ".hb......bh..",
        "..bbbbbbbbs..",
        "..bkkbbkkbs..",
        "..bkkbbkkbs..",
        "...bbbbbbs...",
        "....bssbs....",
        "....sbbs.....",
    ]
    cm = {'h': pal['hi'], 'b': pal['bone'], 's': pal['sh'], 'k': pal['dark']}
    d = ImageDraw.Draw(im)
    w = len(g[0])
    for r, row in enumerate(g):
        for c, ch in enumerate(row):
            if ch == '.':
                continue
            cc = (w - 1 - c) if flip else c
            px(d, x - w // 2 + cc, y - len(g) + 1 + r, cm[ch])
    # 下巴那截埋在沙里：沙面压上来一点（两侧堆起的沙）
    for k in range(-5, 6):
        if abs(k) > 2:
            px(d, x + k, y, pal['sand'])
    px(d, x - 6, y, pal['sand_hi'])
    px(d, x + 6, y + 1, pal['sand_sh'])


def bone(d, x, y, L, pal, ang=0.0):
    """一根散落的骨头（两头粗的棒）。"""
    for k in range(L):
        xx = int(round(x + k * math.cos(ang)))
        yy = int(round(y + k * math.sin(ang)))
        px(d, xx, yy, pal['bone'] if k % 4 else pal['hi'])
    px(d, x - 1, y, pal['hi'])
    px(d, int(round(x + L * math.cos(ang))), int(round(y + L * math.sin(ang))), pal['sh'])


def camel_skeleton(im, x, y, pal, seed=0):
    """一副骆驼骨架（朝左倒在地上，40×14）：长脖子的颈椎一节节、头骨（长嘴）、脊椎一串、肋骨一根根往下弯、
    骨盆、折着的腿骨；有几根被沙埋了一半。x, y = 骨架最左（头）和地面。"""
    d = ImageDraw.Draw(im)
    b, hi, sh, dkc = pal['bone'], pal['hi'], pal['sh'], pal['dark']
    # 头骨（长嘴，眼窝）
    rect(d, x, y - 3, x + 6, y - 2, b)
    hl(d, x + 1, x + 6, y - 4, hi)
    rect(d, x + 5, y - 5, x + 8, y - 2, b)
    px(d, x + 6, y - 4, dkc)
    hl(d, x, x + 4, y - 1, sh)
    # 颈椎：一节一节往右上（脖子仰着）
    for k in range(7):
        cx = x + 9 + k * 2
        cy = y - 4 - int(round(4 * math.sin(k / 6 * math.pi * 0.8)))
        rect(d, cx, cy, cx + 1, cy + 1, b)
        px(d, cx, cy, hi)
        px(d, cx + 1, cy + 2, sh)
    # 脊椎 + 肋骨
    sx0 = x + 23
    for k in range(9):
        cx = sx0 + k * 2
        cy = y - 8 + int(round(1.5 * math.sin(k / 8 * math.pi)))
        rect(d, cx, cy, cx + 1, cy + 1, b)
        px(d, cx, cy, hi)
        if 1 <= k <= 7:                                           # 肋骨往下弯
            L = 6 - abs(k - 4) // 2
            for j in range(L):
                rx = cx + (1 if j > L // 2 else 0)
                ry = cy + 2 + j
                if hash01(seed, k, j, 1) < 0.85:
                    px(d, rx, ry, b if j < L - 1 else sh)
            if k % 2:
                px(d, cx + 1, cy + 2 + L, pal['sand'])               # 肋骨尖埋进沙里
    # 骨盆 + 腿骨
    px_ = sx0 + 18
    rect(d, px_, y - 8, px_ + 3, y - 5, b)
    hl(d, px_, px_ + 3, y - 8, hi)
    px(d, px_ + 1, y - 6, dkc)
    for (lx, ly, L, ang) in ((px_ + 2, y - 4, 7, 0.35), (px_ - 4, y - 3, 6, 0.2), (sx0 + 2, y - 2, 6, -0.25)):
        for k in range(L):
            px(d, int(round(lx + k * math.cos(ang))), int(round(ly + k * math.sin(ang))), b if k % 3 else hi)
    for k in range(-1, 44):                                        # 和沙地的接触：一线暗
        if hash01(seed, k, 2) < 0.55:
            px(d, x + k, y + 1, pal['sand_sh'])


# ============================================================ 会动的
def shimmer_rows(src, y0, y1, f, n, amp, seed, mirage=None):
    """热浪：src（某一层的整张图，RGBA）的 y0..y1 行按行横移（正弦，n 帧一圈严格闭合；带的上下沿振幅收到 0，
    和没扭的图接得上）；边缘按最边上的像素延伸（不会把另一头的东西卷过来）。
    mirage = (y_a, y_b, sky_col, sky_col2)：地平线下 y_a..y_b 这几行再撒一些天色的横段（“水光”，海市蜃楼），一帧一变。
    返回和 src 同大小的 RGBA（只有这几行有东西）。"""
    s = np.array(src)
    hh, ww = s.shape[:2]
    out = np.zeros_like(s)
    for y in range(y0, y1):
        u = (y - y0 + 0.5) / max(1, y1 - y0)
        taper = math.sin(math.pi * u)
        ph = math.tau * f / n + y * 0.9 + hash01(seed, y) * 0.8
        sh_ = int(round(amp * taper * math.sin(ph) * (0.6 + 0.4 * math.sin(math.tau * f / n * 2 + y * 0.37))))
        idx = np.clip(np.arange(ww) - sh_, 0, ww - 1)
        out[y] = s[y, idx]
    if mirage:
        ya, yb, c1, c2 = mirage
        rng = []
        for i in range(int(ww / 3)):
            x = int(hrange(0, ww, seed, i, 81))
            y = int(hrange(ya, yb, seed, i, 82))
            ph = (f / n + hash01(seed, i, 83)) % 1.0
            if ph > 0.55 or out[y, x, 3] == 0:
                continue
            L = int(hrange(2, 7, seed, i, 84) * (0.4 + ph))
            dx = int(round(2 * math.sin(math.tau * ph)))
            rng.append((x + dx, y, L, c1 if ph < 0.3 else c2))
        for (x, y, L, c) in rng:
            for xx in range(max(0, x), min(ww, x + L)):
                if out[y, xx, 3]:
                    out[y, xx, :3] = c
    return Image.fromarray(out, 'RGBA')


def vulture(d, x, y, pose, col, col2):
    """秃鹫（在高处盘旋，从下往上看）：宽翅膀、翼尖分叉的“手指”、短尾；pose 0 = 平展、1 = 翼尖上扬、2 = 侧倾。"""
    if pose == 0:
        pts = [(-5, 0), (-4, 0), (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
               (-5, -1), (5, -1), (0, 1), (-1, 1), (1, 1)]
    elif pose == 1:
        pts = [(-5, -2), (-4, -1), (-3, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, -1), (4, -1), (5, -2),
               (-6, -2), (6, -2), (0, 1), (0, 2)]
    else:
        pts = [(-4, -1), (-3, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 1), (3, 1), (4, 2),
               (-5, -1), (0, 1), (-1, 1)]
    for (dx, dy) in pts:
        px(d, x + dx, y + dy, col)
    px(d, x, y, col2)


def circling(d, f, n, cx, cy, rx, ry, birds, col, col2, seed):
    """几只秃鹫绕一个扁椭圆盘旋（n 帧转一圈，各自错开相位）；在椭圆下半圈（离镜头近）翅膀平展、上半圈侧倾。"""
    for i in range(birds):
        ph = math.tau * (f / n + i / birds + hash01(seed, i) * 0.07)
        x = round(cx + rx * (0.85 + 0.15 * hash01(seed, i, 2)) * math.cos(ph))
        y = round(cy + ry * math.sin(ph))
        pose = 0 if math.sin(ph) > 0.3 else (2 if math.cos(ph) > 0 else 1)
        vulture(d, x, y, pose, col, col2)


def dust_devil(d, x, ybase, h, f, n, pal, seed, lean=4.0):
    """尘卷风：下细上粗的一根尘柱，往上一圈圈旋转的尘带（每帧往上挪）、顶上散开；整根轻轻左右摆。
    用抖动的不透明像素表示半透明（近景层规矩：只有 0 / 255）。pal = (亮尘, 尘, 暗尘)。"""
    ph = math.tau * f / n
    sway = math.sin(ph) * 1.5
    for r in range(h):
        u = r / max(1, h - 1)
        y = ybase - r
        cx = x + sway * u + lean * u * u
        hw = 0.8 + 5.5 * u ** 1.4
        dens = 0.85 - 0.55 * u
        for xx in range(int(math.floor(cx - hw)), int(math.ceil(cx + hw)) + 1):
            v = (xx - cx) / max(0.5, hw)
            if abs(v) > 1:
                continue
            band = math.sin(ph * 2 - r * 0.75 + v * 2.2)
            if hash01(seed, xx - int(x), r, f % 2) > dens * (0.65 + 0.35 * band):
                continue
            c = pal[0] if v < -0.3 else (pal[2] if v > 0.45 else pal[1])
            px(d, xx, y, c)


def spindrift(d, pts, f, n, col, col2, seed, reach=10):
    """沙脊扬沙：从脊线上的几点被风吹出去的一缕缕细沙（往右、略往下，越远越稀），每帧往外挪。"""
    for i, (x0, y0) in enumerate(pts):
        for k in range(10):
            u = ((f / n) + k / 10.0 + hash01(seed, i, k) * 0.1) % 1.0
            x = x0 + u * reach * hrange(0.7, 1.2, seed, i, k, 1)
            y = y0 + u * u * 3 + math.sin(u * 7 + i) * 0.6
            if hash01(seed, i, k, 2) < 0.7 - u * 0.5:
                px(d, int(round(x)), int(round(y)), col if u < 0.5 else col2)


# ============================================================ 第三轮（10-19）加的零件：积云、圆石堆、换时段的帧条孪生
def cumulus_sprite(w, h, seed, pal, light=(-0.5, -0.72, 0.48)):
    """一朵积云（宽 w、高 h，底是平的）：几团球拼出花椰菜一样的顶。每个像素取“最靠前”的那团球、按球面法线算明暗
    （光从左上来：左上沿最亮；球和球交界的地方法线一拐，自然出一道浅折痕），下面 45% 压一条偏蓝灰的阴影带，底沿一行最暗。
    pal = (最亮, 亮, 中, 影)。第三轮看图改的：引擎 _cloud_sprite 的锯齿底在滑翔段的大片天上像一排牙。"""
    w, h = max(8, int(round(w))), max(5, int(round(h)))
    base = h - 1
    puffs = []
    # 花椰菜的轮廓：中间偏一边一团最大的顶到上沿，两边各一团中等的、低一截，底下一串小的——大小高低都要错开
    # （两团一样大的并排，远看像两个屁股蛋，第三轮看图改的）
    rb = min(h * hrange(0.56, 0.66, seed, 1), w * 0.3)
    cxb = w * hrange(0.4, 0.58, seed, 2)
    puffs.append((cxb, rb + hrange(0.0, 1.0, seed, 3), rb, -0.2 * rb))
    for j, side in enumerate((-1, 1)):                    # 两边的中等团，一边高一点、一边低一点
        r = min(h * hrange(0.34, 0.46, seed, j, 4), w * 0.22)
        cx = cxb + side * (rb * hrange(0.75, 1.0, seed, j, 5) + r * 0.5)
        cx = min(max(cx, r + 0.5), w - r - 0.5)
        cy = base - r * hrange(0.55, 0.95, seed, j, 6)
        puffs.append((cx, cy, r, -0.1 * r))
    if w > h * 3.2:                                       # 很宽的云：再加一团中等的，接在长的那一边
        side = 1 if cxb < w * 0.5 else -1
        r = min(h * hrange(0.3, 0.4, seed, 7), w * 0.16)
        cx = min(max(cxb + side * (rb + r * 1.6), r + 0.5), w - r - 0.5)
        puffs.append((cx, base - r * 0.8, r, -0.1 * r))
    n0 = max(2, int(round(w / (h * 0.8))))
    for i in range(n0):                                   # 底排：一串小球沿底排开（底被压平，只露上半）
        u = (i + 0.5) / n0
        r = h * hrange(0.22, 0.32, seed, i, 8)
        cx = r + (w - 2 * r) * u + hrange(-1.5, 1.5, seed, i, 9)
        puffs.append((cx, base - r * hrange(0.1, 0.4, seed, i, 10), r, 0.0))
    Y, X = np.mgrid[0:h, 0:w].astype(np.float64)
    best = np.full((h, w), -1e9)
    nx, ny, nz = np.zeros((h, w)), np.zeros((h, w)), np.zeros((h, w))
    for (cx, cy, r, z0) in puffs:
        dx, dy = X + 0.5 - cx, Y + 0.5 - cy
        d2 = dx * dx + dy * dy
        zz = np.sqrt(np.maximum(0.0, r * r - d2))
        sel = (d2 < r * r) & (z0 + zz > best)
        best = np.where(sel, z0 + zz, best)
        nx, ny, nz = np.where(sel, dx / r, nx), np.where(sel, dy / r, ny), np.where(sel, zz / r, nz)
    m = (best > -1e8) & (Y <= base)
    L = np.array(light, np.float64)
    L /= np.linalg.norm(L)
    lam = nx * L[0] + ny * L[1] + nz * L[2]
    lev = 1.2 + 2.2 * lam - 1.1 * smooth((Y - h * 0.55) / (h * 0.45))
    li = np.clip(np.floor(lev + 0.5 + 0.35 * (bayer(w, h) - 0.5)), 0, 3).astype(int)
    cols = np.array([pal[3], pal[2], pal[1], pal[0]], np.uint8)
    out = np.zeros((h, w, 4), np.uint8)
    out[m, :3] = cols[li][m]
    out[m, 3] = 255
    row = out[base]
    row[m[base], :3] = pal[3]
    return Image.fromarray(out, 'RGBA')


def cumulus_row2(period, h, specs, pal, seed):
    """一排积云（period 宽、首尾循环），云用上面的 cumulus_sprite：specs = [(中心 x, 底 y, 宽, 高比), ...]。"""
    im = A._new(period, h)
    for i, (cx, by, w, hr) in enumerate(specs):
        cl = cumulus_sprite(w, w * hr, seed + i, pal)
        for dx in (-period, 0, period):
            paste(im, cl, int(cx + dx - cl.width / 2), int(by - cl.height))
    return im


def boulder_parts(specs, size):
    """一堆圆石（从后往前）的几何：specs = [dict(cx, base, w, h, p=2.4, seed, wob=0.07, bury=0.18, rnd=2.2), ...]。
    每块是一个超椭圆（p 越大越方：2 = 椭圆，3 以上像方岩），底埋进地里（露出地面的正好是 h），
    轮廓按角度抖一点（几个 sin 叠的周期函数，不会裂口）。法线 = 超椭圆梯度的方向 + 越靠边越往外倒（rnd 越大中间越平），
    所以每块石头都是“鼓”的：左上沿迎光、右下背光，石头和石头之间自然分得开。
    第三轮看图改：原来用抖过轮廓的多边形拼形状、再按左右距离着色，一摞摞圆石看着像趴着的骆驼 / 刺猬（轮廓上一圈毛刺）。
    可选：
      rot=弧度        整块歪一点（斜躺的石板 / 歪着的石块，乱石脊不再是一排一样的圆包）；
      cut=(x, 斜率, 'L' 或 'R')   只留一条近乎竖直的线的一侧（劈开的石头：两半各写一条，法线还是整块的，
                      所以两半合起来明暗是连着的；线 x = x + 斜率 × (base − y)，带一点锯齿）；
      facets=n        把石面分成 n 块平面（在石头里撒 n 个点，每个像素取最近那个点的法线 = 一块块平的岩面、
                      面和面之间一道折线）：棱角分明的乱石用，圆石不用（不分面的圆石成堆摆、轮廓又圆又黑的话
                      远看像一窝趴着的动物，第三轮看图发现的）。
    返回 [dict(box, m, nx, ny, nz, base, top), ...]（数组都是 box 里的局部坐标）。"""
    ww, hh = size
    out = []
    for s in specs:
        cx, base, w, h = float(s['cx']), float(s['base']), float(s['w']), float(s['h'])
        p, bury, wob, sd = s.get('p', 2.4), s.get('bury', 0.18), s.get('wob', 0.07), s.get('seed', 0)
        rot = s.get('rot', 0.0)
        a = w / 2.0
        b = h / (2.0 * (1.0 - bury))
        cy = base - h + b
        # 框留够轮廓抖动（三个 sin 的振幅加起来 1.2 × wob）和歪斜的余量
        ex_ = (max(a, b) if rot else a) * (1 + 1.25 * wob) + 1
        ey_ = (max(a, b) * (1 + 1.25 * wob) + 1) if rot else (h * (1 + wob) + 1)
        x0 = max(0, int(math.floor(cx - ex_)))
        x1 = min(ww - 1, int(math.ceil(cx + ex_)))
        y0 = max(0, int(math.floor((cy - ey_) if rot else (base - ey_))))
        y1 = min(hh - 1, int(base))
        if x1 < x0 or y1 < y0:
            continue
        xs = np.arange(x0, x1 + 1, dtype=np.float64) + 0.5
        ys = np.arange(y0, y1 + 1, dtype=np.float64) + 0.5
        dx, dy = xs[None, :] - cx, ys[:, None] - cy
        cr, sr = math.cos(rot), math.sin(rot)
        U = (dx * cr + dy * sr) / a                     # 转到石头自己的坐标系里
        Vv = (-dx * sr + dy * cr) / b
        th = np.arctan2(Vv, U)
        rs = 1 + wob * (0.6 * np.sin(2 * th + hrange(0, 6.28, sd, 1)) + 0.35 * np.sin(3 * th + hrange(0, 6.28, sd, 2)) +
                        0.25 * np.sin(5 * th + hrange(0, 6.28, sd, 3)))
        F = (np.abs(U) ** p + np.abs(Vv) ** p) ** (1.0 / p) / rs
        m = (F <= 1.0) & (ys[:, None] <= base + 0.5)
        if s.get('cut'):
            xc_, slope, side = s['cut']
            xl = xc_ + slope * (base - ys[:, None]) + 0.6 * np.sin(ys[:, None] * 0.9 + sd)
            m &= (xs[None, :] < xl) if side == 'L' else (xs[None, :] >= xl)
        gu = np.sign(U) * np.abs(U) ** (p - 1) / a
        gv = np.sign(Vv) * np.abs(Vv) ** (p - 1) / b
        gx, gy = gu * cr - gv * sr, gu * sr + gv * cr          # 梯度转回图的坐标系
        gn = np.hypot(gx, gy) + 1e-9
        tilt = (math.pi / 2) * np.clip(F, 0, 1) ** s.get('rnd', 2.2)
        nx, ny, nz = gx / gn * np.sin(tilt), gy / gn * np.sin(tilt), np.cos(tilt)
        nf = s.get('facets', 0)
        if nf and m.sum() > nf * 3:
            # 在石头里撒 nf 个点（按 seed 挑像素），每个像素取最近那个点的法线 → 一块块平的岩面
            iy, ix = np.nonzero(m)
            pick = [int(hrange(0, len(iy) - 1e-6, sd, k, 81)) for k in range(nf)]
            py_, px_ = iy[pick].astype(np.float64), ix[pick].astype(np.float64)
            YY, XX = np.mgrid[0:m.shape[0], 0:m.shape[1]].astype(np.float64)
            dist = (XX[None] - px_[:, None, None]) ** 2 + ((YY[None] - py_[:, None, None]) * 1.3) ** 2
            near_ = np.argmin(dist, axis=0)
            # 每块平面的法线取这块里所有像素法线的平均（取撒点那一个像素的话，点落在边上的那块会整块发黑，像一片鳍）
            fx, fy, fz = np.zeros(nf), np.zeros(nf), np.ones(nf)
            for k in range(nf):
                sel = m & (near_ == k)
                if sel.any():
                    vx_, vy_, vz_ = nx[sel].mean(), ny[sel].mean(), nz[sel].mean()
                    ln = math.sqrt(vx_ * vx_ + vy_ * vy_ + vz_ * vz_) + 1e-9
                    fx[k], fy[k], fz[k] = vx_ / ln, vy_ / ln, vz_ / ln
            nx, ny, nz = fx[near_], fy[near_], fz[near_]
        out.append(dict(box=(x0, y0, x1, y1), m=m, nx=nx, ny=ny, nz=nz, base=int(base),
                        top=int(round(base - h)), seed=sd))
    return out


def boulder_union(parts, size):
    """几块圆石合起来的遮罩（整张图大小）：算投影、找石头顶用。"""
    ww, hh = size
    u = np.zeros((hh, ww), bool)
    for q in parts:
        x0, y0, x1, y1 = q['box']
        u[y0:y1 + 1, x0:x1 + 1] |= q['m']
    return u


def paint_boulders(im, parts, pal, seed, light='left', speck=0.05, grain=0.45, cracks=1, varnish=1, outline=True):
    """按 boulder_parts 的几何从后往前画圆石：
      · 明暗 = 法线 · 光（光从左上前方来；light='right' 时从右上，夕阳用），五档 deep / sh / mid / lit / hi，只在档位交界处抖动
      · 花岗岩的斑驳：成片的亮一档 / 暗一档 + 零星的暗点、亮点；脚下两三行暗一点（沙子挡光）
      · 每块 cracks 道裂缝（暗线 + 向光一侧一线亮）、varnish 道沙漆（从顶往下淌的暗纹，隔一个像素压暗一档）
      · 墨线：背光一侧 + 下沿一圈 ink；向光一侧压在后面石头上的那一圈用 deep（两块石头之间一道缝），
        贴着天 / 地的那一圈留亮（选择性描边，和第4章一样）。pal = dict(ink, deep, sh, mid, lit, hi)。"""
    a = np.array(im)
    hh, ww = a.shape[:2]
    occ = np.zeros((hh, ww), bool)                       # 已经画过的（后面的）石头：判断向光一侧的边压在石头上还是天上
    Lv = np.array([-0.55 if light == 'left' else 0.55, -0.62, 0.56])
    Lv /= np.linalg.norm(Lv)
    pals = np.array([pal[k] for k in ROCK_KEYS], np.uint8)
    for bi, q in enumerate(parts):
        x0, y0, x1, y1 = q['box']
        m = q['m']
        if not m.any():
            continue
        bh, bw = m.shape
        sd = seed * 97 + bi * 13 + q.get('seed', 0)
        lam = q['nx'] * Lv[0] + q['ny'] * Lv[1] + q['nz'] * Lv[2]
        # 正对着人的面 = mid、左上 45° 的面 = hi、右边 / 下沿 = deep（光大致从左上前方来，法线 · 光 ∈ [−1, 1]）
        lev = 3.0 + 3.0 * (lam - 0.45)
        yy = np.arange(y0, y1 + 1, dtype=np.float64)[:, None]
        lev = lev - 0.8 * smooth((yy - (q['base'] - 3)) / 3.0)
        nzs = fbm2(bw, bh, 3, 3, sd)
        lev = lev + np.where(nzs > 0.68, grain, 0.0) - np.where(nzs < 0.3, grain, 0.0)
        li = np.clip(np.floor(lev + 0.5 + 0.4 * (bayer(bw, bh) - 0.5)), 1, 5).astype(int)
        li0 = li.copy()                                   # 撒斑点之前的档位：向光的边按它决定要不要描亮边（不然亮边断断续续）
        r = np.random.default_rng(sd).random(m.shape)
        li = np.where(r < speck, np.maximum(1, li - 1), li)
        li = np.where((r > 1 - speck * 0.6) & (li >= 3), np.minimum(5, li + 1), li)
        col = pals[li]
        # 裂缝：从顶面往下的一道随机走的暗线（向光一侧一线亮）
        for c in range(cracks):
            cxl = int(hrange(bw * 0.25, bw * 0.75, sd, c, 51))
            cyl = np.nonzero(m[:, cxl])[0]
            if len(cyl) < 6:
                continue
            x = cxl
            L_ = int(hrange(len(cyl) * 0.35, len(cyl) * 0.75, sd, c, 53))
            for k in range(L_):
                y = cyl[0] + 1 + k
                if y >= bh or not m[y, x]:
                    break
                col[y, x] = pals[1]
                xl = x - 1 if light == 'left' else x + 1
                if 0 <= xl < bw and m[y, xl]:
                    col[y, xl] = pals[min(5, li[y, xl] + 1)]
                rr = hash01(sd, c, k, 54)
                x = max(0, min(bw - 1, x + (-1 if rr < 0.2 else (1 if rr > 0.8 else 0))))
        # 沙漆：顶上往下淌的暗纹
        for k in range(varnish):
            vx = int(hrange(bw * 0.2, bw * 0.9, sd, k, 71))
            cyl = np.nonzero(m[:, vx])[0]
            if len(cyl) < 5:
                continue
            for j in range(int(hrange(3, len(cyl) * 0.6, sd, k, 72))):
                y = cyl[0] + 1 + j
                if y < bh and m[y, vx] and j % 2 == 0:
                    col[y, vx] = pals[max(1, li[y, vx] - 1)]
        if outline:
            left, right, top, bottom = edge_masks(m)
            if light == 'right':
                left, right = right, left
            back = occ[y0:y1 + 1, x0:x1 + 1]
            # 向光一侧的边：外面一格是后面的石头 → 一道缝（deep）；外面是天 / 地 → 亮边（只在本来就不暗的地方）
            def nb(mm, dx, dy):
                o = np.zeros_like(mm)
                o[max(0, dy):bh + min(0, dy), max(0, dx):bw + min(0, dx)] = \
                    mm[max(0, -dy):bh + min(0, -dy), max(0, -dx):bw + min(0, -dx)]
                return o
            dxl = -1 if light == 'left' else 1
            on_rock = (left & nb(back, -dxl, 0)) | (top & nb(back, 0, 1))
            lit_rim = (left | top) & ~on_rock & ~(right | bottom)
            col[lit_rim & (li0 >= 3)] = pals[5]
            col[on_rock] = pals[1]
            col[right | bottom] = pals[0]
        sub = a[y0:y1 + 1, x0:x1 + 1]
        sub[m, :3] = col[m]
        sub[m, 3] = 255
        a[y0:y1 + 1, x0:x1 + 1] = sub
        occ[y0:y1 + 1, x0:x1 + 1] |= m
    im.paste(Image.fromarray(a, 'RGBA'))
    return occ


def regraded_render(render, ramp, keep=0.25):
    """帧条的“换时段”孪生：每帧按 regrade 换色（透明度、像素位置一个不变）。配同一个框、同一个 n / fps、带 key 的 strip，
    排在原帧条（和那一层的换时段 pick）后面：同一时刻两条取同一帧，换色版正好把原版整个盖住。
    为什么要它：引擎的 key 只有“开了才画”，没有“开了就不画”——傍晚 / 夕阳时白天颜色的小动画（尘卷风、扬沙、蜥蜴）
    露在换了色的画面上很扎眼（第三轮看图发现的）。"""
    cache = {}

    def r(t):
        f = frame_of(t, render.n, render.fps)
        if f not in cache:
            cache[f] = regrade(render(t), ramp, keep)
        return cache[f]
    r.n, r.fps = render.n, render.fps
    return r


# ============================================================ 图层表 → 导出 / 直接拼 / 自检
def cache_frames(fn_f, n, fps):
    """fn_f(f) → 整帧图（世界坐标），按帧号缓存；返回 render(t)（ex.bake / 自检按时间调用）。"""
    cache = {}

    def render(t):
        f = frame_of(t, n, fps)
        if f not in cache:
            cache[f] = fn_f(f)
        return cache[f]
    render.n, render.fps = n, fps
    return render


@lru_cache(maxsize=4)
def blank1():
    return A._new(1, 1)


def export_layers(ex, BJ, spec):
    """图层表 → stage 的 layers（顺序不变）。pano / wrap 先裁掉上下全透明的行（省 KB），y 跟着挪。"""
    out = []
    for L in spec:
        typ = L['type']
        if typ == 'static':
            d = dict(type='static', image=ex.img(L['name'], L['img']), x=L.get('x', 0), y=L.get('y', 0))
        elif typ == 'wrap':
            im, y = BJ.crop_rows(L['img'])
            d = dict(type='wrap', image=ex.img(L['name'], BJ.tile_to(im, L['period'], L['period'] + W)),
                     period=L['period'], k=L['k'], y=L.get('y', 0) + y, vx=L['vx'])
        elif typ == 'pano':
            im, y = BJ.crop_rows(L['img'])
            d = dict(type='pano', image=ex.img(L['name'], im), k=L['k'], x=L.get('x', 0), y=L.get('y', 0) + y)
        elif typ == 'strip':
            d = ex.bake(L['name'], L['box'], L['n'], L['fps'], L['fn'], screen=bool(L.get('screen')),
                        key=L.get('key'), k=None if L.get('screen') else L['k'])
        elif typ == 'clouds':
            d = dict(type='clouds', span=L['span'],
                     clouds=[dict(image=ex.img(c['name'], c['img']), x0=float(c['x0']), y=c['y'], vx=c['vx'], k=c['k'])
                             for c in L['clouds']])
        elif typ == 'pick':
            d = dict(type='pick', key=L['key'], values=list(L['values']),
                     images=[ex.img('%s%d' % (L['name'], i), im) for i, im in enumerate(L['imgs'])],
                     x=L.get('x', 0), y=L.get('y', 0), k=L.get('k', 0.0))
        elif typ == 'tint':
            d = dict(type='tint', color=L['color'], alpha=L['alpha'])
        else:
            raise ValueError(typ)
        if L.get('key') and typ != 'pick':
            d['key'] = L['key']
        out.append(d)
    return out


def _hexc(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def compose(spec, camX, t=0.5, state=None):
    """不经导出、直接用内存里的原图按 §3.6 的公式拼一帧（黑底）：自检拿它对照导出的图层。"""
    st = state or {}
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for L in spec:
        typ = L['type']
        key = L.get('key')
        if key and typ != 'pick' and not st.get(key):
            continue
        if typ == 'static':
            paste(out, L['img'], L.get('x', 0), L.get('y', 0))
        elif typ == 'wrap':
            P = L['period']
            o = int(math.floor(camX * L['k'] + t * L['vx'])) % P
            big = V._tile(L['img'], P * 3)
            paste(out, big.crop((o, 0, o + W, big.height)), 0, L.get('y', 0))
        elif typ == 'pano':
            paste(out, L['img'], L.get('x', 0) - math.floor(camX * L['k']), L.get('y', 0))
        elif typ == 'strip':
            box = L['box']
            fr = L['fn'](t).crop(box)
            x = box[0] if L.get('screen') else box[0] - math.floor(camX * L['k'])
            paste(out, fr, x, box[1])
        elif typ == 'clouds':
            for c in L['clouds']:
                x = (c['x0'] + t * c['vx'] - camX * c['k']) % L['span'] - 100
                paste(out, c['img'], math.floor(x), c['y'])
        elif typ == 'pick':
            v = st.get(key, 0) or 0
            v = float(v)
            vals = L['values']
            i = min(range(len(vals)), key=lambda j: abs(vals[j] - v))
            paste(out, L['imgs'][i], L.get('x', 0) - math.floor(camX * L.get('k', 0.0)), L.get('y', 0))
        elif typ == 'tint':
            lay = Image.new('RGBA', (W, H), _hexc(L['color']) + (int(255 * L['alpha']),))
            out.alpha_composite(lay)
    return out


def keys_of(spec):
    return sorted({L['key'] for L in spec if L.get('key')})


def std_checks(ex, BJ, st, spec, fg_spec, name, pw, walk, near, sky, anchors, stand=(), boxes=(), opaque_bands=(),
               kb_limit=250):
    """三张沙漠图共用的自检（照 ganges_ghat._checks）：
      不露黑（镜头 0 … pw−320 每 40 × 4 个时刻 × key 全关 / 全开）、天整张不透明、近景可走带整条不透明、近景只有 0 / 255、
      指定的层在指定的带里不透明、strip 闭合 / 帧条 ≤ 4096 / 每帧在动 / 画的东西都在框里、wrap 一圈闭合、
      每个 key 打开以后画面真的变了、锚点都在地图里 / 站人的锚点在可走带里、导出 vs 直接拼逐像素一致、PNG 合计 ≤ kb_limit KB。"""
    imgs = ex.images
    allk = keys_of(spec + fg_spec)
    on = {k: 1 for k in allk}
    full = spec + fg_spec
    bad = 0
    for camX in range(0, pw - W + 1, 40):
        for t in (0.0, 0.75, 1.5, 7.0):
            for state in ({}, on):
                im = np.array(BJ.ref_render(st, imgs, camX, t, state).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('%s 镜头 0–%d（每 40）× 4 个时刻 × key 全关 / 全开 整屏都有画（没有露黑）' % (name, pw - W), bad)
    ex.checked('天空底图整张不透明', int((np.array(sky)[..., 3] != 255).sum()))
    a = np.array(near)
    ex.checked('近景 可走带（y %d–%d）整条不透明' % (walk[0], H - 1), int((a[walk[0]:, :, 3] != 255).sum()))
    ex.checked('近景只有 0 / 255 两种透明度', int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum()))
    for (label, img, box) in opaque_bands:
        b = np.array(img)[box[1]:box[3], box[0]:box[2], 3]
        ex.checked(label, int((b != 255).sum()))
    strips = [L for L in full if L['type'] == 'strip']
    for L in strips:
        fn, box, n, fps = L['fn'], L['box'], L['n'], L['fps']
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (L['name'], T, T),
                   BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (L['name'], (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (L['name'], moving, n), n - moving)
    groups = {}
    for L in strips:
        groups.setdefault(id(L['fn']), []).append(L)
    for items in groups.values():
        fn, n, fps = items[0]['fn'], items[0]['n'], items[0]['fps']
        lost = 0
        for i in range(n):
            m = np.array(fn(i / fps))[..., 3] > 0
            for L in items:
                b = L['box']
                m[b[1]:b[3], b[0]:b[2]] = False
            lost += int(m.sum())
        ex.checked('strip %s 每帧画的东西都在框里（框外的像素）' % '+'.join(L['name'] for L in items), lost)
    for L in [L for L in st['layers'] + st['fg'] if L['type'] == 'wrap']:
        T = L['period'] / abs(L['vx'])
        one = dict(st, layers=[dict(L, key=None)], fg=[])
        g0 = BJ.ref_render(one, imgs, 0, 0.1, {})
        g1 = BJ.ref_render(one, imgs, 0, 0.1 + T, {})
        ex.checked('wrap %s 一圈 %.1f s 闭合' % (L['image'].split('/')[-1], T), BJ.ndiff(g0, g1))
    for k in allk:
        moved = 0
        for camX in sorted({0, (pw - W) // 2, pw - W}):
            moved += BJ.ndiff(BJ.ref_render(st, imgs, camX, 1.0, {}), BJ.ref_render(st, imgs, camX, 1.0, {k: 1}))
        ex.checked('key %s 打开以后画面变了（变化的像素 %d > 0）' % (k, moved), 0 if moved > 0 else 1)
    out = 0
    for k, v in anchors.items():
        if isinstance(v, (int, float)):
            continue
        if k == 'walk_x':                                          # [x0, x1]：可走的横向范围，不是点
            out += not (0 <= v[0] < v[1] <= pw)
            continue
        pts = v if (v and isinstance(v[0], (list, tuple))) else [v]
        for p in pts:
            if len(p) == 2:
                out += not (0 <= p[0] <= pw and 0 <= p[1] <= H)
                if k in stand:
                    out += not (walk[0] <= p[1] <= walk[1])
            elif len(p) == 4:
                out += not (0 <= p[0] < p[2] <= pw and 0 <= p[1] < p[3] <= H)
    for (k, b) in boxes:
        out += not (0 <= b[0] < b[2] <= pw and 0 <= b[1] < b[3] <= H)
    ex.checked('锚点都在地图里、站人的锚点在可走带 %d–%d 里（不满足的条数）' % tuple(walk), out)
    for camX in sorted({0, 120, (pw - W) // 2, pw - W}):
        for t in (0.0, 1.25, 9.0):
            for state in ({}, on):
                got = BJ.ref_render(st, imgs, camX, t, state)
                ex.checked('%s camX=%d t=%.2f %s 导出 vs 直接拼' % (name, camX, t, 'key 全开' if state else 'key 全关'),
                           BJ.ndiff(got, compose(full, camX, t, state)))
    idx = ex.c.get('index') if isinstance(ex.c, dict) else None
    if idx:
        tot = sum(v['bytes'] for k, v in idx.items() if k.startswith('bg/%s/' % ex.key))
        ex.checked('PNG 合计 %.1f KB ≤ %d KB' % (tot / 1024, kb_limit), 0 if tot <= kb_limit * 1024 else int(tot / 1024))
