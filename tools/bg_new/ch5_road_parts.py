# -*- coding: utf-8 -*-
r"""ch5_road_parts —— 第5章「ch5-road」组（desert_highway / mountain_road / brain_inside）共用零件（2026-10-18 第二轮）。
不是背景 key（文件名不和任何 key 重名），三张图的模块加载时用 importlib 按路径引用它（同 ganges_ghat 引 varanasi_street）。

放在这里的东西：
  · 像素小工具：直接借 varanasi_street.py 的 dk / lt / hl / vl / px / rect / mul_box / mul_mask / poly_mask /
    cast_shadow / mottle / haze / opaque（第4章同一套，画法和描边习惯一致）
  · 有机体打光：借 underwater.py 的 blob / shade（高度场 lambert + Voronoi 切面 + 下 / 右描边）——岩壁、落石、脑回都用它
  · 帧号、可横向循环的噪声、wrap 层“跨接缝左右各画一份”的小工具
  · 两张户外图共用的活物 / 植物：鹰（盘旋时按倾角换翅膀）、乌鸦、金合欢（伞状树冠）、刺灌木、草丛
  · 自检公用件：整屏不露黑、strip 闭合 / 帧条宽 / 每帧在动 / 框外没画、wrap 一圈闭合、导出 vs 直接拼
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

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402,F401
from engine import bg_asia as A  # noqa: E402


def load(name):
    """tools\\bg_new\\<name>.py，模块名和 bg_jojo.bg_new(name) 一样（'bg_new_<name>'），已经加载过就直接复用。"""
    key = 'bg_new_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


V = load('varanasi_street')      # 第4章的像素小工具（描边 / 斑驳 / 投影 / 空气透视）
U = load('underwater')           # 第2章的有机体打光（blob / shade）

C = A._c4
W, H = 320, 180
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, cast_shadow, mottle, haze, opaque = (V.mul_box, V.mul_mask, V.poly_mask, V.cast_shadow,
                                                                  V.mottle, V.haze, V.opaque)
SHADOW_MUL, SOFT_MUL = V.SHADOW_MUL, V.SOFT_MUL
blob, shade, shift = U.blob, U.shade, U.shift


# ============================================================ 小工具
def frame_of(t, n, fps):
    """t 秒是第几帧（和引擎 strip 一样：floor(t·fps + 1e-6) mod n）。"""
    return int(math.floor(t * fps + 1e-6)) % n


def wnoise(w, h, cell, seed, octaves=3):
    """横向可循环的 fbm（w 的整数倍周期）：wrap 层的地面纹理用，接缝看不出来。"""
    return A._fbm_wrap(w, h, cell, seed, octaves)


def arr(im):
    return np.array(im)


def img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def comp(dst, src, x=0, y=0):
    """numpy RGBA 叠加（src over dst，越界自动裁）。"""
    U.comp(dst, src, x, y)


def bayer(w, h):
    return A._bayer(w, h)


def ellipse(d, x0, y0, x1, y1, c, outline=None):
    if x1 >= x0 and y1 >= y0:
        d.ellipse((x0, y0, x1, y1), fill=C(c) if c is not None else None, outline=C(outline) if outline else None)


def line(d, pts, c, width=1):
    d.line([(int(round(x)), int(round(y))) for (x, y) in pts], fill=C(c), width=width)


def wrap_x(fn, x, period, margin=120):
    """wrap 层（周期 period）里画一个横向跨度不超过 margin 的东西：离接缝近就在 x ± period 再画一份，接缝处不断。"""
    fn(x)
    if x < margin:
        fn(x + period)
    if x > period - margin:
        fn(x - period)


def catenary(x0, y0, x1, y1, sag):
    """两根杆子之间下垂的电线：抛物线近似，返回整数点列。"""
    n = max(2, int(abs(x1 - x0)))
    pts = []
    for i in range(n + 1):
        u = i / n
        pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + sag * 4 * u * (1 - u)))
    return pts


# ============================================================ 鸟
def eagle_img(pose='glide', col=(74, 56, 46)):
    """鹰（从下往上看，翅膀张开）：pose glide = 平展、bank_l / bank_r = 往左 / 右倾（一边翅膀抬高、短一截）、
    up = 翅膀上扬（一下扇动）。头和尾巴颜色浅一点。11×5。"""
    g = A._new(11, 6)
    d = ImageDraw.Draw(g)
    hi = (196, 176, 150)
    if pose == 'glide':
        pts = ((0, 2), (1, 1), (2, 1), (3, 1), (4, 2), (6, 2), (7, 1), (8, 1), (9, 1), (10, 2))
    elif pose == 'bank_l':
        pts = ((1, 0), (2, 1), (3, 1), (4, 2), (6, 2), (7, 2), (8, 3), (9, 3), (10, 4))
    elif pose == 'bank_r':
        pts = ((0, 4), (1, 3), (2, 3), (3, 2), (4, 2), (6, 2), (7, 1), (8, 1), (9, 0))
    else:
        pts = ((1, 0), (2, 0), (3, 1), (4, 2), (6, 2), (7, 1), (8, 0), (9, 0))
    for (x, y) in pts:
        px(d, x, y, col)
        if 1 <= x <= 9 and x not in (4, 6):
            px(d, x, y + 1, dk(col, 0.82))                         # 翅膀下沿（羽毛的暗边）
    px(d, 5, 1, hi)                                               # 头（白头的）
    vl(d, 5, 2, 3, col)
    px(d, 5, 4, mix(col, hi, 0.5))                                # 尾
    return g


def crow_img(up=False, col=(48, 42, 46)):
    """远处的乌鸦（7×3）：up = 翅膀上扬。"""
    g = A._new(7, 3)
    d = ImageDraw.Draw(g)
    pts = ((0, 0), (1, 0), (2, 1), (4, 1), (5, 0), (6, 0)) if up else ((0, 1), (1, 1), (2, 1), (4, 1), (5, 1), (6, 2))
    for (x, y) in pts:
        px(d, x, y, col)
    px(d, 3, 1, col)
    px(d, 3, 2, dk(col, 0.8))
    return g


# ============================================================ 植物
def acacia(d, x, base, h, w, seed, leaf=((60, 82, 46), (84, 108, 56), (112, 134, 70), (146, 160, 90)),
           trunk=((72, 54, 44), (104, 80, 60)), shadow=None):
    """金合欢（kikar，旁遮普 / 信德平原路边最常见的树）：弯弯的黑褐色树干在半截分成两三股，
    顶上一片扁扁的伞状树冠（下沿平、上沿起伏），树冠左上亮、下沿一圈暗、里面漏几个天光的洞。
    x = 树干脚，base = 地面 y，h = 树高，w = 树冠宽。"""
    crown_y = base - h
    cw = w // 2
    # 树干：从脚往上歪一点，到 0.55 h 处分叉
    split = base - int(h * 0.5)
    lean = hrange(-2, 2, seed, 1)
    tx = x
    for y in range(base, split, -1):
        u = (base - y) / max(1, base - split)
        xx = int(round(tx + lean * u))
        vl(d, xx, y, y, trunk[0])
        px(d, xx - 1, y, trunk[1])                                   # 树干左边受光
        if y > base - 3:
            px(d, xx + 1, y, trunk[0])                               # 根部粗一点
    top_x = int(round(tx + lean))
    for k, (ang, L) in enumerate(((-0.9, 0.9), (0.15, 1.0), (0.8, 0.85))):
        ex = top_x + int(round(math.sin(ang) * cw * 0.7 * L))
        ey = crown_y + 3 + int(hrange(0, 2, seed, k, 2))
        line(d, [(top_x, split), ((top_x + ex) / 2, (split + ey) / 2 + 1), (ex, ey)], trunk[0])
    # 树冠：几块扁椭圆叠起来（先暗后亮）
    blobs = []
    n = max(4, w // 7)
    for i in range(n):
        u = (i + 0.5) / n
        bx = x + lean + (u - 0.5) * w * 0.92
        by = crown_y + 2 + abs(u - 0.5) * 3 + hrange(-1, 1, seed, i, 3)
        br = hrange(0.55, 0.8, seed, i, 4) * w / n * 1.3
        blobs.append((bx, by, br))
    for (bx, by, br) in blobs:
        d.ellipse((bx - br, by - br * 0.45 + 1, bx + br, by + br * 0.45 + 2), fill=C(leaf[0]))
    for (bx, by, br) in blobs:
        d.ellipse((bx - br, by - br * 0.45, bx + br, by + br * 0.4), fill=C(leaf[1]))
    for (bx, by, br) in blobs:
        rr = br * 0.6
        d.ellipse((bx - rr - br * 0.3, by - br * 0.45, bx + rr - br * 0.3, by - br * 0.45 + rr * 0.55), fill=C(leaf[2]))
    for i, (bx, by, br) in enumerate(blobs):
        if hash01(seed, i, 5) < 0.6:
            px(d, int(bx - br * 0.5), int(by - br * 0.4), leaf[3])
            px(d, int(bx - br * 0.5) + 1, int(by - br * 0.4), leaf[3])
    for i in range(max(2, w // 10)):                                 # 树冠里漏天光的小洞 + 下沿零碎的叶簇
        hx = int(x + lean + hrange(-w * 0.35, w * 0.35, seed, i, 6))
        hy = int(crown_y + 2 + hrange(-1, 1, seed, i, 7))
        px(d, hx, hy + 1, leaf[0])
        px(d, hx + 1, hy + 2, leaf[0])
    if shadow is not None:
        shadow(x, base, w)


def shrub(d, x, base, w, h, seed, pal=((92, 96, 58), (124, 124, 70), (158, 150, 88), (186, 174, 110))):
    """路边的刺灌木（干旱区的矮丛）：一团疙瘩，左上亮、右下暗，底下几根枯枝露出来。"""
    for i in range(max(3, w // 3)):
        bx = x + hrange(-w / 2, w / 2, seed, i, 1)
        by = base - hrange(h * 0.3, h * 0.8, seed, i, 2)
        r = hrange(1.5, 2.8, seed, i, 3) * max(1.0, h / 5)
        d.ellipse((bx - r, by - r * 0.8 + 1, bx + r, by + r * 0.8 + 1), fill=C(pal[0]))
    for i in range(max(3, w // 3)):
        bx = x + hrange(-w / 2, w / 2, seed, i, 1)
        by = base - hrange(h * 0.3, h * 0.8, seed, i, 2)
        r = hrange(1.5, 2.8, seed, i, 3) * max(1.0, h / 5)
        d.ellipse((bx - r, by - r * 0.8, bx + r - 1, by + r * 0.6), fill=C(pal[1]))
        px(d, int(bx - r * 0.4), int(by - r * 0.5), pal[2])
        if hash01(seed, i, 4) < 0.4:
            px(d, int(bx - r * 0.4) + 1, int(by - r * 0.5), pal[3])
    for k in range(3):                                               # 底下露出来的枯枝
        sx = int(x + hrange(-w / 3, w / 3, seed, k, 5))
        line(d, [(sx, base), (sx + hrange(-2, 2, seed, k, 6), base - 2)], dk(pal[0], 0.7))


def grass_tuft(d, x, base, h, seed, col=(176, 156, 96), dark=(132, 112, 70), light=(214, 196, 132)):
    """一撮干草：三五根往两边岔开的草叶，中间深、外面浅，叶尖亮。"""
    n = 3 + int(hash01(seed, 1) * 3)
    for k in range(n):
        u = (k + 0.5) / n - 0.5
        hh = max(1, int(round(h * (1 - abs(u) * 0.8) * hrange(0.7, 1.1, seed, k, 2))))
        lean = u * 2.4 + hrange(-0.6, 0.6, seed, k, 3)
        for j in range(hh):
            xx = int(round(x + lean * j / max(1, hh - 1)))
            c = dark if j < hh // 3 else col
            if j == hh - 1:
                c = light
            px(d, xx, base - j, c)


# ============================================================ 山脉（两张户外图共用）
def hfield(P_, seed, terms, noise_amp, cell):
    xs = np.arange(P_, dtype=np.float32)
    h = np.zeros(P_, np.float32)
    for (cyc, amp, ph) in terms:
        h += amp * (0.5 + 0.5 * np.sin(xs * 2 * math.pi * cyc / P_ + ph))
    n = wnoise(P_, 4, cell, seed)[1] - 0.5
    return h + n * noise_amp


def ridge(a, base, h, pal, seed, haze_col, haze_top, haze_bot, gully=0.5):
    """一道山脉画进 a（numpy，宽 = 周期）：每列从 base − h 到 base；朝左的坡亮（太阳在左）、朝右的坡暗，
    按列的坡度 + 可循环噪声分亮 / 中 / 暗三级，竖着的冲沟（细长噪声）压暗一级；山脊一道亮边；
    越往山脚越往 haze_col 混（haze_top → haze_bot）。"""
    P_ = a.shape[1]
    hh, ww = a.shape[:2]
    lit, mid, shd, rim = pal
    nz = wnoise(P_, hh, 4, seed + 5)
    gl = wnoise(P_, hh, 8, seed + 9)
    b = bayer(P_, hh)
    for x in range(P_):
        top = int(round(base - h[x]))
        if top >= base:
            continue
        sl = (h[(x + 1) % P_] - h[(x - 1) % P_]) * 0.5
        for y in range(max(0, top), base + 1):
            v = sl + (nz[y, x] - 0.5) * 0.9
            if v > 0.35 or (v > 0.1 and b[y, x] < 0.5):
                c = lit
            elif v < -0.35 or (v < -0.1 and b[y, x] < 0.5):
                c = shd
            else:
                c = mid
            # 冲沟：顺着坡往下的细长暗纹（只在有坡的地方）
            if abs(sl) > 0.15 and gl[y, (x + int((y - top) * 0.4 * np.sign(sl))) % P_] > 1 - gully * 0.35:
                c = shd if c != shd else dk(shd, 0.9)
            depth = (y - top) / max(1.0, base - top)
            hz = haze_top + (haze_bot - haze_top) * depth
            a[y, x, :3] = mix(c, haze_col, hz)
            a[y, x, 3] = 255
        a[top, x, :3] = mix(rim if sl >= -0.05 else mid, haze_col, haze_top)


# ============================================================ 自检公用件
def check_no_black(ex, BJ, st, label, cams=(0,), times=(0.0, 0.75, 1.5, 7.0), states=({},)):
    bad = 0
    for s in states:
        for camX in cams:
            for t in times:
                im = np.array(BJ.ref_render(st, ex.images, camX, t, s).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked(label, bad)


def check_strips(ex, BJ, strips):
    """strips = [(名字, 框, 帧数, fps, 帧函数)]：闭合、帧条宽、每帧在动；同一个帧函数的几条合起来查“画的东西都在框里”。"""
    for (name, box, n, fps, fn) in strips:
        T = n / fps
        ex.checked('strip %s %.2f s 闭合（t=0 vs t=%.2f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
    groups = {}
    for (name, box, n, fps, fn) in strips:
        groups.setdefault(fn, []).append((name, box, n, fps))
    for fn, items in groups.items():
        lost = 0
        n, fps = items[0][2], items[0][3]
        for i in range(n):
            m = np.array(fn(i / fps))[..., 3] > 0
            for (_, box, _, _) in items:
                m[box[1]:box[3], box[0]:box[2]] = False
            lost += int(m.sum())
        ex.checked('strip %s 每帧画的东西都在框里（框外的像素）' % '+'.join(it[0] for it in items), lost)


def check_wraps(ex, BJ, st, t0=0.0123):
    """wrap 层一圈（t = period/|vx|）闭合；t0 取个零碎数，免得 floor 正好卡在整数边上。"""
    for L in [L for L in st['layers'] + st.get('fg', []) if L['type'] == 'wrap' and L.get('vx')]:
        T = L['period'] / abs(L['vx'])
        one = dict(st, layers=[L], fg=[])
        g0 = BJ.ref_render(one, ex.images, 0, t0, {})
        g1 = BJ.ref_render(one, ex.images, 0, t0 + T, {})
        ex.checked('wrap %s 一圈 %.2f s 闭合' % (L['image'].split('/')[-1], T), BJ.ndiff(g0, g1))


def check_alpha_binary(ex, label, im):
    a = np.array(im)[..., 3]
    ex.checked(label, int(((a > 0) & (a < 255)).sum()))


def check_opaque(ex, label, im, box):
    """box（右下不含）里整块不透明。"""
    a = np.array(im)[..., 3]
    x0, y0, x1, y1 = box
    ex.checked(label, int((a[y0:y1, x0:x1] != 255).sum()))


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
