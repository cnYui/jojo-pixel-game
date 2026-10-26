# -*- coding: utf-8 -*-
r"""interior_parts —— interiors 组（第三轮，2026-10-19）共用的零件：
cafe_interior、cairo_sewer（第10章）、game_room（第11章）、airport（终章）四张室内背景 +
poker_table、cairo_map（第10章）、crt_baseball（第11章）三张全屏插画背景。
这个文件不是背景 key（名字不和任何 key 重名），各 key 模块按路径加载它（同 sea_parts.py 的写法）。

内容：
  · 图层表框架直接引用 sea_parts.py（已验收的第7章零件，只读不改）：export_layers / direct / std_checks /
    auto_box / walk_stats / outline / frame_no——图层表写法、通用自检和第7章完全一样，验收的人不用重新看一套。
  · 小工具引用 varanasi_street.py：dk / lt / hl / vl / px / rect / mul_box / mul_mask / poly_mask / mottle / opaque。
  · 室内用的新零件：分档打光（light_map：几盏灯 + 环境光，只在档的交界抖一窄条，像手画的光）、
    木纹护墙板 / 木地板 / 地砖 / 砖墙、画框、酒瓶、吊扇帧、细烟 / 热气帧、光柱里的浮尘、3×5 点阵字。
所有颜色都避开纯黑 (0,0,0)：通用自检用“RGB 全 0”判断露黑。
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


def _load(name):
    """按路径加载 tools/bg_new/<name>.py（模块名和 bg_jojo.bg_new() 一致，已经加载过就直接复用）。"""
    key = 'bg_new_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


SP = _load('sea_parts')
V = SP.V
W, H = 320, 180
C = A._c4
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, mottle, opaque = V.mul_box, V.mul_mask, V.poly_mask, V.mottle, V.opaque
export_layers, direct, std_checks, auto_box, walk_stats = SP.export_layers, SP.direct, SP.std_checks, SP.auto_box, SP.walk_stats
outline, frame_no, hexc = SP.outline, SP.frame_no, SP.hexc
N_ANIM, FPS_ANIM = SP.N_ANIM, SP.FPS_ANIM          # 默认 strip：8 帧 @4 fps = 2 s 一圈
new = A._new
bayer = A._bayer


def strip(name, fn, region, n=N_ANIM, fps=FPS_ANIM, key=None, fg=False, k=1.0):
    """图层表里的一条 strip：框按 n 帧实际画到的范围自动算（不切东西、不带空白）。"""
    L = dict(t='strip', name=name, box=auto_box(fn, n, fps, region), n=n, fps=fps, fn=fn, k=k)
    if key:
        L['key'] = key
    if fg:
        L['fg'] = True
    return L


# ============================================================ 打光
def quant(L, n, bay, jitter=0.28):
    """光照分 n 档；只在档和档的交界抖一窄条（大片是平的，像手画的光）。"""
    return np.floor(L * n + 0.5 + (bay - 0.5) * jitter) / n


def light_map(w, h, amb, lights, n=10, cool=(0.86, 0.92, 1.06), gain=1.0):
    """分档打光的乘数图（h×w×3）。
    amb：环境光（标量或 h×w）；lights：[dict(x, y, r, k=1, p=1.5, sx=1, sy=1, col=(暖色乘数))]——
    每盏灯一个椭圆光圈（sx / sy 压扁），亮度 (1 − d/r)^p·k。环境光偏冷、灯光带自己的颜色。"""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    s = np.zeros((h, w), np.float32)
    acc = np.zeros((h, w, 3), np.float32)
    for L in lights:
        dd = np.hypot((xx - L['x']) * L.get('sx', 1.0), (yy - L['y']) * L.get('sy', 1.0))
        v = np.clip(1 - dd / L['r'], 0, 1) ** L.get('p', 1.5) * L.get('k', 1.0)
        s += v
        acc += v[..., None] * np.array(L.get('col', (1.12, 0.98, 0.76)), np.float32)
    sn = np.clip(s, 0, 1)
    lc = acc / np.maximum(s, 1e-4)[..., None]
    tint = np.array(cool, np.float32)[None, None, :] * (1 - sn[..., None]) + lc * sn[..., None]
    q = quant(np.asarray(amb, np.float32) + gain * s, n, bayer(w, h))
    return q[..., None] * tint


def apply_light(im, m, lo=8):
    """RGB 乘打光图（下限 lo：不会压成纯黑，自检靠“全 0”找露黑）。"""
    a = np.array(im).astype(np.float32)
    a[..., :3] = np.clip(a[..., :3] * m, lo, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def glow(im, cx, cy, rx, ry, col, alpha, rings=3):
    """一圈一圈的柔光（真 alpha 混合，画在已经打好光的图上：灯罩、屏幕这些自己发光的东西）。"""
    A._glow(im, cx, cy, rx, ry, col, alpha, rings=rings)


def overlay(w, h):
    """透明叠加层（strip 帧、key 叠层用）。"""
    return new(w, h)


# ============================================================ 材质
def wood_boards_v(d, x0, y0, x1, y1, pal, seed, bw=7, ink=None):
    """竖拼的木板（护墙板 / 吧台正面）：每块一个底色、左亮边、右暗缝，木纹是几道断续的竖线 + 偶尔一个节疤。
    pal = (暗缝, 暗, 中, 亮)。"""
    x = x0
    i = 0
    while x <= x1:
        w = min(bw, x1 - x + 1)
        base = pal[2] if hash01(seed, i) > 0.35 else mix(pal[1], pal[2], 0.55)
        rect(d, x, y0, x + w - 1, y1, base)
        vl(d, x, y0, y1, pal[3])
        vl(d, x + w - 1, y0, y1, pal[0] if ink is None else ink)
        for g in range(2):
            gx = x + 2 + int(hash01(seed, i, g) * max(1, w - 4))
            ga = y0 + int(hash01(seed, i, g, 3) * (y1 - y0) * 0.5)
            gb = min(y1, ga + 4 + int(hash01(seed, i, g, 4) * (y1 - y0) * 0.6))
            vl(d, gx, ga, gb, pal[1])
        if hash01(seed, i, 9) < 0.25 and w > 4:
            kx, ky = x + w // 2, y0 + int(hash01(seed, i, 8) * (y1 - y0 - 4)) + 2
            px(d, kx, ky, pal[0])
            px(d, kx, ky + 1, pal[1])
        x += w
        i += 1


def planks_h(d, x0, y0, x1, y1, pal, seed, ph=4, plen=(28, 60)):
    """横铺的木地板（错缝）：每行一个底色，行缝一条暗线、接缝一条短竖线，木纹短横线。pal = (缝, 暗, 中, 亮)。"""
    y = y0
    r = 0
    while y <= y1:
        h = min(ph, y1 - y + 1)
        x = x0 - int(hash01(seed, r) * plen[1])
        j = 0
        while x <= x1:
            L = int(hrange(plen[0], plen[1], seed, r, j))
            base = (pal[2], mix(pal[1], pal[2], 0.6), mix(pal[2], pal[3], 0.3))[int(hash01(seed, r, j, 1) * 3)]
            rect(d, max(x0, x), y, min(x1, x + L - 1), y + h - 1, base)
            if x0 <= x <= x1:
                vl(d, x, y, y + h - 2, pal[0])
            for g in range(2):
                gx = x + 3 + int(hash01(seed, r, j, g) * max(1, L - 10))
                gy = y + 1 + int(hash01(seed, r, j, g, 5) * max(1, h - 2))
                hl(d, max(x0, gx), min(x1, gx + 3 + int(hash01(seed, r, j, g, 6) * 6)), gy, pal[1])
            x += L
            j += 1
        hl(d, x0, x1, y + h - 1, pal[0])
        y += h
        r += 1


def bricks(a, x0, y0, x1, y1, pal, seed, bw=8, bh=4, mortar=None, jit=0.5):
    """砖墙（numpy，直接写进 a[h, w, 3]）：错缝，每块砖一个底色（pal 里随机挑，带一点明暗抖动），
    砖的上沿亮一行、下沿暗一行（光从上来）；mortar = 灰缝颜色。"""
    mortar = mortar if mortar is not None else dk(pal[0], 0.7)
    for y in range(y0, y1 + 1):
        r = (y - y0) // bh
        yy = (y - y0) % bh
        off = (bw // 2) * (r % 2)
        for x in range(x0, x1 + 1):
            c = (x - x0 + off) // bw
            xx = (x - x0 + off) % bw
            if yy == bh - 1 or xx == bw - 1:
                a[y, x, :3] = mortar
                continue
            h = hash01(seed, r, c)
            base = np.array(pal[int(h * len(pal)) % len(pal)], np.float32)
            base = base * (1 + (hash01(seed, r, c, 7) - 0.5) * 0.12 * jit * 2)
            if yy == 0:
                base = base * 1.1
            elif yy == bh - 2:
                base = base * 0.9
            a[y, x, :3] = np.clip(base, 0, 255)


def tiles(d, x0, y0, x1, y1, tw, th, cols, grout, seed, bevel=True):
    """方地砖 / 墙砖：cols 里交替（棋盘），每块上 / 左一条亮边、下 / 右一条暗边（bevel），grout 是砖缝。"""
    j = 0
    y = y0
    while y <= y1:
        i = 0
        x = x0
        while x <= x1:
            c = cols[(i + j) % len(cols)]
            if hash01(seed, i, j) < 0.12:
                c = dk(c, 0.95)
            rect(d, x, y, min(x1, x + tw - 2), min(y1, y + th - 2), c)
            if bevel:
                hl(d, x, min(x1, x + tw - 2), y, lt(c, 0.12))
                vl(d, min(x1, x + tw - 2), y, min(y1, y + th - 2), dk(c, 0.9))
            vl(d, min(x1, x + tw - 1), y, min(y1, y + th - 1), grout)
            hl(d, x, min(x1, x + tw - 1), min(y1, y + th - 1), grout)
            x += tw
            i += 1
        y += th
        j += 1


def gilt_frame(d, x0, y0, x1, y1, pal=((92, 64, 26), (150, 112, 46), (200, 160, 74), (236, 206, 120)), w=2,
               ink=(40, 28, 22)):
    """金色画框（宽 w）：外圈墨线、上 / 左亮、下 / 右暗，四角一个亮点。里面不填。"""
    rect(d, x0, y0, x1, y1, None, outline=ink)
    for k in range(1, w + 1):
        hl(d, x0 + k, x1 - k, y0 + k, pal[3] if k == 1 else pal[2])
        vl(d, x0 + k, y0 + k, y1 - k, pal[2])
        hl(d, x0 + k, x1 - k, y1 - k, pal[1] if k == 1 else pal[0])
        vl(d, x1 - k, y0 + k, y1 - k, pal[1])
    for (u, v) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1)):
        px(d, u, v, pal[3])
    rect(d, x0 + w + 1, y0 + w + 1, x1 - w - 1, y1 - w - 1, None, outline=pal[0])


def bottle(d, x, base, kind, col, ink=(34, 26, 30)):
    """吧台酒架上的瓶子（底在 base）：kind 0 = 葡萄酒瓶（细高）、1 = 方肩烈酒瓶、2 = 矮胖瓶；
    左边一列高光、右边一列暗色、一块小标签。宽 3–4 px、高 8–11 px。"""
    if kind == 0:
        rect(d, x, base - 8, x + 2, base - 1, col)
        vl(d, x + 1, base - 11, base - 9, col)
        px(d, x + 1, base - 12, dk(col, 0.7))
        vl(d, x, base - 7, base - 2, lt(col, 0.35))
        vl(d, x + 2, base - 8, base - 1, dk(col, 0.7))
        rect(d, x, base - 5, x + 2, base - 4, (226, 214, 180))
    elif kind == 1:
        rect(d, x, base - 7, x + 3, base - 1, col)
        rect(d, x + 1, base - 9, x + 2, base - 8, col)
        hl(d, x + 1, x + 2, base - 10, dk(col, 0.6))
        vl(d, x, base - 7, base - 2, lt(col, 0.35))
        vl(d, x + 3, base - 7, base - 1, dk(col, 0.7))
        rect(d, x + 1, base - 5, x + 2, base - 3, (236, 222, 190))
    else:
        rect(d, x, base - 5, x + 3, base - 1, col)
        rect(d, x + 1, base - 7, x + 2, base - 6, dk(col, 0.85))
        vl(d, x, base - 5, base - 2, lt(col, 0.35))
        vl(d, x + 3, base - 5, base - 1, dk(col, 0.7))
    px(d, x + 1, base, ink)


def glass_cup(d, x, base, col=(200, 214, 220)):
    """小玻璃杯（3×4）：透明的就画边 + 一点高光。"""
    vl(d, x, base - 3, base, dk(col, 0.8))
    vl(d, x + 2, base - 3, base, dk(col, 0.7))
    hl(d, x, x + 2, base, dk(col, 0.75))
    px(d, x + 1, base - 2, col)


# ============================================================ 会动的小东西
def fan_frame(d, cx, cy, f, n=8, R=13, pal=((60, 46, 40), (110, 84, 62), (150, 116, 84)), ink=(36, 28, 28)):
    """吊扇（侧面略俯视）：四片桨叶绕轴转，侧视时桨叶投成一条横向的扁椭圆——每片的 x 偏移 = R·cos(θ)、
    y 偏移 = 0.22·R·sin(θ)；8 帧转 90°（四片对称 → 首尾闭合）。马达壳画在桨叶前面。"""
    base = f / n * (math.pi / 2)
    blades = []
    for b in range(4):
        th = base + b * math.pi / 2
        blades.append((math.sin(th), th))
    for (sv, th) in sorted(blades):                      # 后面的桨叶先画
        ex, ey = math.cos(th) * R, math.sin(th) * R * 0.22
        n_ = max(abs(ex), 1.0)
        c = pal[2] if sv > 0 else pal[1]
        for k in range(1, 101):
            u = k / 100.0
            x = cx + ex * u
            y = cy + 1 + ey * u
            if u > 0.18:
                px(d, int(round(x)), int(round(y)), c)
                if abs(ex) > R * 0.5:                   # 横着的时候桨叶有 2 px 厚
                    px(d, int(round(x)), int(round(y)) + 1, dk(c, 0.75))
        px(d, int(round(cx + ex)), int(round(cy + 1 + ey)), ink if n_ > 2 else c)
    rect(d, cx - 3, cy - 2, cx + 3, cy + 2, pal[1], outline=ink)
    hl(d, cx - 2, cx + 2, cy - 1, pal[2])
    px(d, cx, cy + 3, ink)


def wisp(a, x0, y0, t, period, length, drift, col, alpha=150, seed=0, width=1, sway=1.6):
    """一缕往上飘的细烟 / 热气（numpy 叠加层 a[h, w, 4]）：沿一条正弦线往上，越高越淡、越歪；
    相位按 t / period 走一圈（period 秒正好闭合）。"""
    ph = (t / period) % 1.0
    for k in range(length):
        y = y0 - k
        if y < 0:
            break
        u = k / length
        x = x0 + drift * u + sway * math.sin(2 * math.pi * (ph * 2 - u * 1.6) + seed) * (0.3 + u)
        al = alpha * (1 - u) ** 1.2 * (0.55 + 0.45 * math.sin(2 * math.pi * (ph - u * 2.0) + seed * 1.7) ** 2)
        for wv in range(width):
            xi = int(round(x)) + wv
            if 0 <= xi < a.shape[1] and al > 18:
                a[y, xi, :3] = col
                a[y, xi, 3] = max(a[y, xi, 3], int(al))


def motes(d, box, t, period, n, col, seed, amp=(2.0, 3.0), ok=None):
    """光柱里飘的浮尘：n 个点各绕自己的位置画小椭圆（amp 是 x / y 半径），一明一暗。
    用绕圈而不是直线漂：period 秒正好转一圈，帧条首尾不会“跳回原位”。ok(x, y) 给了就只画在光柱里。"""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    for i in range(n):
        u = (t / period + hash01(seed, i)) % 1.0
        bx = x0 + hash01(seed, i, 1) * w
        by = y0 + hash01(seed, i, 2) * h
        x = int(round(bx + amp[0] * math.sin(2 * math.pi * u)))
        y = int(round(by + amp[1] * math.cos(2 * math.pi * u)))
        if ok is not None and not ok(x, y):
            continue
        if int(u * 8 + i) % 4 != 0:                     # 转到某一段时“暗下去”：浮尘一闪一闪
            px(d, x, y, col)


# ============================================================ 3×5 点阵字（牌子 / 翻牌用）
FONT35 = {
    'A': ('010', '101', '111', '101', '101'), 'B': ('110', '101', '110', '101', '110'),
    'C': ('011', '100', '100', '100', '011'), 'D': ('110', '101', '101', '101', '110'),
    'E': ('111', '100', '110', '100', '111'), 'F': ('111', '100', '110', '100', '100'),
    'G': ('011', '100', '101', '101', '011'), 'H': ('101', '101', '111', '101', '101'),
    'I': ('111', '010', '010', '010', '111'), 'J': ('001', '001', '001', '101', '010'),
    'K': ('101', '110', '100', '110', '101'), 'L': ('100', '100', '100', '100', '111'),
    'M': ('101', '111', '111', '101', '101'), 'N': ('110', '101', '101', '101', '101'),
    'O': ('010', '101', '101', '101', '010'), 'P': ('110', '101', '110', '100', '100'),
    'Q': ('010', '101', '101', '110', '011'), 'R': ('110', '101', '110', '101', '101'),
    'S': ('011', '100', '010', '001', '110'), 'T': ('111', '010', '010', '010', '010'),
    'U': ('101', '101', '101', '101', '111'), 'V': ('101', '101', '101', '101', '010'),
    'W': ('101', '101', '111', '111', '101'), 'X': ('101', '101', '010', '101', '101'),
    'Y': ('101', '101', '010', '010', '010'), 'Z': ('111', '001', '010', '100', '111'),
    '0': ('111', '101', '101', '101', '111'), '1': ('010', '110', '010', '010', '111'),
    '2': ('110', '001', '010', '100', '111'), '3': ('110', '001', '010', '001', '110'),
    '4': ('101', '101', '111', '001', '001'), '5': ('111', '100', '110', '001', '110'),
    '6': ('011', '100', '111', '101', '111'), '7': ('111', '001', '010', '010', '010'),
    '8': ('111', '101', '111', '101', '111'), '9': ('111', '101', '111', '001', '110'),
    ':': ('0', '1', '0', '1', '0'), '-': ('000', '000', '111', '000', '000'), ' ': ('00', '00', '00', '00', '00'),
    '.': ('0', '0', '0', '0', '1'), '/': ('001', '001', '010', '100', '100'),
}


def text35(d, x, y, s, col, gap=1):
    """3×5 点阵字，返回写完的 x。"""
    for ch in s:
        g = FONT35.get(ch, FONT35[' '])
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == '1':
                    px(d, x + c, y + r, col)
        x += len(g[0]) + gap
    return x


def text35_w(s, gap=1):
    return sum(len(FONT35.get(ch, FONT35[' '])[0]) + gap for ch in s) - gap


# ============================================================ 插画背景的自检（没有可走带、单屏）
def ill_checks(ex, BJ, st, S, cfg):
    """全屏插画背景：通用自检（整屏不露黑、底图整张不透明、strip / pick）+ 锚点在画面里 + 每个“剧情要写字 / 摆东西”
    的框里底色够干净（clear：和基准色差 > 容差的像素数）。cfg 同 std_checks，另加 inside 全部锚点名。"""
    std_checks(ex, BJ, st, S, cfg)
