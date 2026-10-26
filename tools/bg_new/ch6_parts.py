# -*- coding: utf-8 -*-
r"""ch6_parts —— 第6章 ch6-misc 组（yaprin_village / cessna_cabin / dream_carnival）共用的小工具和自检。
2026-10-18 第二轮背景重画新建（文件名按分工表，不和任何 key 重名）。

为什么单独一个模块：三张图的画法各不相同，但都要同一套像素小工具（照 varanasi_street.py 的 dk / lt / hl / vl /
rect / mul_box / cast_shadow / mottle / haze / opaque）和同一套自检（整屏不露黑、近景只有 0 / 255 透明度、strip 闭合 /
每帧在动 / 帧条宽、帧画在框里、导出 vs 直接拼）。小工具直接复用 varanasi_street.py（同一个模块名，bg_jojo 也会复用
这个实例），这里只补三张图都要的：描边、帧号、可走带后面压对比、自检函数。
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _street_mod():
    """调色 / 像素小工具跟 varanasi_street.py 共用（模块名和 ganges_ghat.py 一样，只加载一次）。"""
    key = 'bg_new_varanasi_street'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'varanasi_street.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


V = _street_mod()
C = A._c4
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, cast_shadow, mottle, haze, opaque = (V.mul_box, V.mul_mask, V.poly_mask, V.cast_shadow,
                                                                  V.mottle, V.haze, V.opaque)
wire, tile = V.wire, V._tile
SHADOW_MUL, SOFT_MUL = V.SHADOW_MUL, V.SOFT_MUL
W, H = 320, 180


def fidx(t, fps, n):
    """第几帧：和 engine/bg.js 的 strip 同一个取整（floor(t·fps + 1e-6) mod n）。"""
    return int(math.floor(t * fps + 1e-6)) % n


def outline(im, col, diag=False):
    """不透明形状外面描一圈 1 px 墨线（小精灵：骆驼、山羊、木马……；同第4章近景的 1 px 深色描边）。"""
    a = np.array(im)
    m = a[..., 3] > 0
    g = m.copy()
    g[1:] |= m[:-1]
    g[:-1] |= m[1:]
    g[:, 1:] |= m[:, :-1]
    g[:, :-1] |= m[:, 1:]
    if diag:
        g[1:, 1:] |= m[:-1, :-1]
        g[1:, :-1] |= m[:-1, 1:]
        g[:-1, 1:] |= m[1:, :-1]
        g[:-1, :-1] |= m[1:, 1:]
    ring = g & ~m
    a[ring] = C(col)
    return Image.fromarray(a, 'RGBA')


def shade_sprite(im, hi, mid, lo, edge, light_from_left=True, lo_from=0.66):
    """单色剪影 → 有体积的小精灵：上沿一行亮、下半截暗、背光一侧描深色边（光从左上）。im 里所有不透明像素重新上色。"""
    a = np.array(im)
    m = a[..., 3] > 0
    h, w = m.shape
    ys = np.arange(h)[:, None].repeat(w, 1)
    top = np.zeros_like(m)
    top[1:] = m[:-1]
    left = np.zeros_like(m)
    left[:, 1:] = m[:, :-1]
    right = np.zeros_like(m)
    right[:, :-1] = m[:, 1:]
    down = np.zeros_like(m)
    down[:-1] = m[1:]
    rows = np.where(m.any(1))[0]
    y0, y1 = (rows[0], rows[-1]) if len(rows) else (0, h - 1)
    u = (ys - y0) / max(1, (y1 - y0))
    a[m, :3] = mid
    a[m & (u > lo_from), :3] = lo
    lit_edge = m & ~top
    lit_edge |= m & (~left if light_from_left else ~right) & (u < 0.5)
    a[lit_edge, :3] = hi
    dark_edge = m & (~down | (~right if light_from_left else ~left)) & (u > 0.25)
    a[dark_edge, :3] = edge
    return Image.fromarray(a, 'RGBA')


def compress_band(im, y0, y1, mid, k=0.18, ramp=8):
    """可走带后面那一条压对比：往 mid 收 k（从 y0 起 ramp 行渐变），人物站上去是清楚的（照 calcutta_street）。"""
    a = np.array(im).astype(np.float32)
    mm = np.array(mid, np.float32)
    for y in range(y0, y1):
        kk = 1.0 - k * min(1.0, (y - y0 + 1) / ramp)
        m = a[y, :, 3] > 0
        a[y, m, :3] = mm + (a[y, m, :3] - mm) * kk
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def dither_fill(d, pts_or_box, c1, c2, level, seed=0, box=True):
    """在 box 里按 Bayer 阈值交错 c1 / c2（level 0 → 全 c1，1 → 全 c2）：像素画里的“半透明”。"""
    x0, y0, x1, y1 = pts_or_box
    bay = A._bayer(x1 + 2, y1 + 2)
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            d.point((x, y), fill=C(c2 if bay[y, x] < level else c1))


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


# ============================================================ 自检（三张图共用）
def check_no_black(ex, BJ, st, cams, times, states, label):
    """各镜头 × 几个时刻 × 几种 key 组合：整屏没有露黑（ref_render 黑底，RGB 全 0 = 没画到）。"""
    bad = 0
    for state in states:
        for camX in cams:
            for t in times:
                im = np.array(BJ.ref_render(st, ex.images, camX, t, state).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('%s 镜头 %s × %d 个时刻 × %d 种状态 整屏都有画（没有露黑）' % (label, cams if len(cams) < 4 else
                                                              '%d–%d' % (cams[0], cams[-1]), len(times), len(states)), bad)


def check_alpha01(ex, label, im):
    a = np.array(im)
    ex.checked('%s只有 0 / 255 两种透明度' % label, int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum()))


def check_strips(ex, BJ, strips):
    """strips = [(name, box, n, fps, fn)]：闭合 / 帧条宽 / 每帧在动；同一个帧函数的几条合起来查“画的东西都在框里”。"""
    for (name, box, n, fps, fn) in strips:
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
    fns = {}
    for (name, box, n, fps, fn) in strips:
        fns.setdefault(fn, []).append((name, box, n, fps))
    for fn, items in fns.items():
        lost = 0
        n, fps = items[0][2], items[0][3]
        for i in range(n):
            m = np.array(fn(i / fps))[..., 3] > 0
            for (_, box, _, _) in items:
                m[box[1]:box[3], box[0]:box[2]] = False
            lost += int(m.sum())
        ex.checked('strip %s 每帧画的东西都在框里（框外的像素）' % '+'.join(it[0] for it in items), lost)


def check_wraps(ex, BJ, st):
    """wrap 层（云、窗外的天）转一圈闭合：t = period / |vx| 时和 t = 0 一样。"""
    for L in [L for L in st['layers'] if L['type'] == 'wrap' and L.get('vx')]:
        T = L['period'] / abs(L['vx'])
        one = dict(st, layers=[L], fg=[])
        g0 = BJ.ref_render(one, ex.images, 0, 0.1, {})
        g1 = BJ.ref_render(one, ex.images, 0, 0.1 + T, {})
        ex.checked('wrap %s 一圈 %.1f s 闭合' % (L['image'].split('/')[-1], T), BJ.ndiff(g0, g1))


def check_anchor_inside(ex, anchors, pw, walk, stand_keys, label='锚点'):
    """锚点都在地图里（点 / 框 / 点列表）、站人的锚点在可走带里。返回不满足的条数并记一条自检。"""
    out = 0

    def pt_ok(v):
        return 0 <= v[0] <= pw and 0 <= v[1] <= H

    for k, v in anchors.items():
        if isinstance(v, (int, float)) or isinstance(v, dict) or isinstance(v, str):
            continue
        if k == 'walk_x':                                   # [x0, x1]：可走的横向范围，不是点
            out += not (0 <= v[0] < v[1] <= pw)
            continue
        if len(v) == 2 and all(isinstance(q, (int, float)) for q in v):
            out += not pt_ok(v)
            if k in stand_keys:
                out += not (walk[0] <= v[1] <= walk[1])
        elif len(v) == 4 and all(isinstance(q, (int, float)) for q in v):
            out += not (0 <= v[0] < v[2] <= pw and 0 <= v[1] < v[3] <= H)
        else:
            for q in v:
                if isinstance(q, (list, tuple)) and len(q) == 2:
                    out += not pt_ok(q)
                    if k in stand_keys:
                        out += not (walk[0] <= q[1] <= walk[1])
                elif isinstance(q, (list, tuple)) and len(q) == 4:
                    out += not (0 <= q[0] < q[2] <= pw and 0 <= q[1] < q[3] <= H)
    ex.checked('%s都在地图里、站人的锚点在可走带 %d–%d 里（不满足的条数）' % (label, walk[0], walk[1]), out)
    return out


def check_flat_spots(ex, im, spots, base, tol, label, half_w=10, up=18, down=4, y_min=None):
    """站人 / 放道具的地方（spots 的脚点 ±half_w，往上 up 行、往下 down 行）近景里只有平地：
    离 base 太远（最大通道差 > tol）、又不是“同一个颜色压暗 / 提亮”（影子、湿地、石子高光：各通道比值差 < 0.12、
    平均比值 0.68–1.1）的像素数——也就是那里画了别的东西。y_min 以上（墙脚线等）不算。"""
    a = np.array(im)[..., :3].astype(np.float32)
    b = np.array(base, np.float32)
    busy = 0
    for (x, y) in spots:
        y0 = max(y_min if y_min is not None else 0, y - up)
        sub = a[y0:y + down, max(0, x - half_w):x + half_w + 1]
        far = np.abs(sub - b).max(-1) > tol
        r = sub / np.maximum(b, 1)
        same_hue = (r.max(-1) - r.min(-1) < 0.12) & (r.mean(-1) > 0.68) & (r.mean(-1) < 1.1)
        busy += int((far & ~same_hue).sum())
    ex.checked(label, busy)
    return busy
