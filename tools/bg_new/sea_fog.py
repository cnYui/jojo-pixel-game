# -*- coding: utf-8 -*-
r"""sea_fog —— 第2章 漂流：救生艇在雾里过夜，天快亮时一艘巨大的货轮从雾里出现（新 key，2026-10-11 ch2）。

320 单屏，ground 160，可走带 y 150–170（人坐在救生艇里，几乎不走动；救生艇是剧情的道具，放在 anchors.boat）。
镜头贴着水面：海平线 y 104，天快亮前的深蓝灰，海平线一带一点黎明的灰白；月亮躲在雾后面只剩一圈光晕。

图层（从后往前）：
  sky         static            天空渐变 + 雾后的月晕 + 几颗暗星 + 海面底色 + 黎明在海面上的一点反光
  fog_far     wrap  vx 2        远处的雾墙（贴着海平线，320 循环，往左慢慢飘）
  swell_far   strip screen      远一半的海面（y 105–148）：反着天光的细浪起伏（12 帧 @6 fps，2 s 闭合）
  ship        pick  key 'ship'  values [0, 0.5, 1]：0 = 没有船（全透明）；0.5 = 雾里一个淡淡的巨大船影（半透明）；
                                1 = 生锈的暗色货轮船身占画面右边（x 150–320，只看得到船头和一段船身；
                                    船头锚链孔 + 锚、舷窗、焊缝、锈迹、吃水标记、水线的红漆、船舷栏杆、
                                    雾里的前桅和吊杆；x 250 一道绳梯一直垂到水面；水里有船身的倒影）
  swell_near  strip screen      近一半的海面（y 148–180），画在船的倒影上面
  fog_near    wrap  vx 5        飘过船身前面的雾带（很淡）
  night       tint  key 'night' 数字 0–1 = 夜色浓淡（颜色 #0a0e22，alpha 0.55 × night；0 / 不设 = 天快亮）
  fg: mist    wrap  vx 7        贴着水面的一层薄雾（y 166–180，很淡，盖到救生艇的下沿）
锚点：boat [110,162]（剧情把救生艇道具放这里，人坐在艇后面）、ladder [250,150]（绳梯底，人从这里爬上去）、
      ladder_top [250,18]、ship_x [150,320]、waterline 148、horizon 104、moon [70,30]、walk_x [40,300]。
单独运行：python -B tools\bg_new\sea_fog.py → tools\bg_new\_preview\ch2\after\sea_fog_solo_*.png
"""
import sys
sys.dont_write_bytecode = True

import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import gradient, hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402

W, H = 320, 180
GROUND = 160
WALK = (150, 170)
HZ = 104                       # 海平线
WL = 148                       # 货轮水线
SHIP_X0 = 140                  # ship pick 图从这一列开始（宽 180）
LADDER_X = 250
N_SW, FPS_SW = 12, 6.0         # 海面 strip：12 帧 @6 fps = 2 s
FOG_FAR_VX, FOG_NEAR_VX, MIST_VX = 2.0, 5.0, 7.0
SWELL_FAR = (0, HZ + 1, W, WL)
SWELL_NEAR = (0, WL, W, H)
NIGHT = ('#0a0e22', 0.55)
C = A._c4

ANCHORS = dict(boat=[110, 162], ladder=[LADDER_X, 150], ladder_top=[LADDER_X, 18], ship_x=[150, 320],
               waterline=WL, horizon=HZ, moon=[70, 30], walk_x=[40, 300])

# 船身
HULL = (40, 45, 51)
HULL_A = (37, 42, 48)
HULL_B = (43, 48, 54)
HULL_HI = (66, 72, 80)
HULL_SEAM_HI = (52, 58, 64)
HULL_SEAM_D = (30, 34, 40)
RUST_L = (108, 68, 46)
RUST = (94, 58, 42)
RUST_D = (70, 46, 38)
BOOT = (72, 36, 34)
GRIME = (34, 44, 42)
ROPE = (164, 154, 130)
ROPE_D = (116, 108, 92)
RUNG = (128, 98, 66)
RUNG_HI = (168, 136, 92)
FOG_C = (120, 128, 142)


def dk(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


def hl(d, x0, x1, y, c):
    if x1 >= x0:
        d.line((x0, y, x1, y), fill=C(c))


def vl(d, x, y0, y1, c):
    if y1 >= y0:
        d.line((x, y0, x, y1), fill=C(c))


def px(d, x, y, c):
    d.point((x, y), fill=C(c))


def rect(d, x0, y0, x1, y1, c):
    if x1 >= x0 and y1 >= y0:
        d.rectangle((x0, y0, x1, y1), fill=C(c))


# ============================================================ 天 + 海底色
SKY = [(14, 18, 36), (22, 28, 50), (40, 48, 70), (78, 84, 100), (122, 122, 130)]
SEA = [(96, 100, 112), (62, 70, 86), (38, 46, 62), (24, 32, 46), (16, 22, 34)]


def sea_color(y):
    u = max(0.0, min(1.0, (y - HZ) / (H - HZ))) * (len(SEA) - 1)
    i = min(len(SEA) - 2, int(u))
    return mix(SEA[i], SEA[i + 1], u - i)


@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, HZ), SKY, bands=12)
    A._glow(im, 64, HZ, 130, 26, (176, 156, 146), 42, rings=5)          # 黎明：左边海平线上一点暖灰
    A._glow(im, 70, 30, 26, 22, (196, 204, 222), 46, rings=5)           # 雾后的月亮
    d = ImageDraw.Draw(im)
    d.ellipse((66, 26, 74, 34), fill=C((150, 158, 178)))
    d.ellipse((67, 27, 73, 33), fill=C((172, 178, 196)))
    for i in range(16):                                                 # 几颗暗星（雾里只剩上面这几颗）
        x, y = int(hrange(4, 316, i, 31)), int(hrange(3, 44, i, 32))
        if abs(x - 70) < 24 and y < 50:
            continue
        px(d, x, y, (84, 92, 120) if i % 3 else (120, 128, 156))
    gradient(im, (0, HZ, W, H), SEA, bands=10)
    d = ImageDraw.Draw(im)
    hl(d, 0, W - 1, HZ, (138, 136, 142))
    hl(d, 0, W - 1, HZ + 1, (110, 112, 122))
    for i in range(70):                                                 # 海面上的长涌（静止的暗条）
        y = HZ + 3 + int(hash01(i, 41) ** 1.2 * (H - HZ - 4))
        u = (y - HZ) / (H - HZ)
        x = int(hrange(-30, W, i, 42))
        L = int(hrange(14, 50, i, 43) * (0.5 + u))
        hl(d, max(0, x), min(W - 1, x + L), y, dk(sea_color(y), 0.86))
    for i in range(46):                                                 # 黎明的反光（左边海平线下面一片竖着的亮碎片）
        y = HZ + 2 + int(hash01(i, 44) ** 1.6 * 40)
        x = int(64 + hrange(-30, 30, i, 45) * (0.4 + (y - HZ) / 40))
        L = int(hrange(2, 7, i, 46))
        hl(d, x, x + L, y, mix(sea_color(y), (168, 156, 152), 0.5 - (y - HZ) / 120))
    return im


# ============================================================ 雾
def _fog(w, h, seed, center, half, amax, cell=32, stretch=4, levels=(0, 34, 62, 92, 122, 150), col=(146, 152, 164)):
    """循环（w 宽首尾接得上）的雾带：横着拉长的噪声 × 纵向的钟形，透明度量化成几档再用 Bayer 抖动过渡（像素风）。"""
    n = A._fbm_wrap(w, h * stretch, cell, seed=seed, octaves=3)[::stretch][:h]
    yy = np.arange(h, dtype=np.float32)[:, None]
    prof = np.clip(1 - ((yy - center) / half) ** 2, 0, 1)
    a = np.clip((n - 0.32) / 0.5, 0, 1) * prof * amax
    lv = np.array(levels, np.float32)
    idx = np.searchsorted(lv, a) - 1
    idx = np.clip(idx, 0, len(lv) - 2)
    lo, hi = lv[idx], lv[idx + 1]
    frac = (a - lo) / np.maximum(1, hi - lo)
    bay = A._bayer(w, h)
    out_a = np.where(frac > bay, hi, lo)
    out_a[a <= 1] = 0
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., :3] = col
    arr[..., 3] = np.clip(out_a, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


@lru_cache(maxsize=1)
def fog_far_img():
    """远处的雾墙：中心在海平线（y 104），上下各 30 px，最浓 150。返回 (图, y0)。"""
    y0 = HZ - 30
    return _fog(W, 62, 51, 30, 30, 170, cell=40, col=(140, 146, 160)), y0


@lru_cache(maxsize=1)
def fog_near_img():
    y0 = 112
    return _fog(W, 50, 57, 26, 24, 96, cell=32, stretch=5, levels=(0, 30, 56, 84), col=(156, 162, 174)), y0


@lru_cache(maxsize=1)
def mist_img():
    y0 = 164
    return _fog(W, 16, 63, 12, 10, 80, cell=20, stretch=3, levels=(0, 26, 50, 72), col=(150, 158, 172)), y0


# ============================================================ 海面起伏（strip）
def swell_frame(t):
    """整片海面的细浪（透明底）：每道浪花按 x 有相位（一道一道往右传），上下起伏 1 px、长短一呼一吸；
    远处是短亮线，近处是“亮线 + 下面一道暗线”的小涌。12 帧 2 s 严格闭合。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_SW + 1e-6)) % N_SW
    ph0 = math.tau * f / N_SW
    for i in range(330):
        y = HZ + 2 + int(hash01(i, 1) ** 1.45 * (H - HZ - 3))
        u = (y - HZ) / (H - HZ)
        x = int(hrange(-8, W, i, 2))
        L0 = (2 + 12 * u) * hrange(0.6, 1.3, i, 3)
        ph = ph0 + x * 0.04 + hash01(i, 4) * 1.4
        dy = int(round((0.4 + 1.3 * u) * math.sin(ph)))
        L = int(round(L0 * (0.5 + 0.5 * math.cos(ph))))
        if L <= 0:
            continue
        sea = sea_color(y + dy)
        dawn = max(0.0, 1 - abs(x - 64) / 90) * max(0.0, 1 - u * 2.2)
        lite = mix(mix(sea, (150, 156, 170), 0.55 - 0.25 * u), (190, 172, 160), dawn * 0.6)
        if hash01(i, 5) < 0.72:
            hl(d, x, x + L, y + dy, lite)
            if u > 0.45:
                hl(d, x + 1, x + L - 1, y + dy + 1, dk(sea, 0.72))
        else:
            hl(d, x, x + L, y + dy, dk(sea, 0.74))
    return im


# ============================================================ 货轮
def hull_top(x):
    """船舷顶（舷墙上沿）的 y：往船头翘。"""
    return 19 - 4 * max(0.0, (205 - x) / 55.0) ** 1.4


def stem_x(y):
    """船头柱（斜的）在第 y 行的 x：上面伸得更靠左。"""
    u = max(0.0, min(1.0, (y - 15) / (WL - 15)))
    return 150 + 37 * u ** 1.5


def hull_mask():
    m = np.zeros((H, W), bool)
    for y in range(0, WL + 1):
        xs = stem_x(y)
        for x in range(int(math.ceil(xs)), W):
            if y >= hull_top(x):
                m[y, x] = True
    return m


def structures(d, col, col_hi=None):
    """船舷上的栏杆 + 雾里的前桅、吊杆、船楼的轮廓（画在 hull_top 以上）。"""
    for x in range(156, W, 11):                                         # 栏杆立柱
        yt = round(hull_top(x))
        vl(d, x, yt - 7, yt - 1, col)
    prev = None
    for x in range(152, W):
        y = round(hull_top(x)) - 8
        if prev:
            d.line((prev[0], prev[1], x, y), fill=C(col))
        prev = (x, y)
    for x in range(154, W):
        px(d, x, round(hull_top(x)) - 4, col)
    # 前桅（桅杆 + 横桁 + 灯架）
    vl(d, 204, 0, round(hull_top(204)) - 1, col)
    vl(d, 205, 0, round(hull_top(205)) - 1, col)
    hl(d, 196, 213, 4, col)
    d.line((205, 2, 224, 13), fill=C(col))
    # 吊杆柱 + 斜伸的吊杆 + 钢索
    rect(d, 286, 0, 290, round(hull_top(288)) - 1, col)
    d.line((288, 8, 238, 0), fill=C(col), width=2)
    d.line((288, 3, 252, 0), fill=C(col))
    d.line((246, 1, 246, 12), fill=C(col))
    rect(d, 244, 12, 248, 14, col)
    # 船首楼甲板上的绞缆机 / 通风筒的轮廓
    for (x0, x1, h) in ((168, 176, 5), (222, 228, 7), (262, 268, 5)):
        yt = round(hull_top(x0)) - 1
        rect(d, x0, yt - h, x1, yt, col)
    d.ellipse((222, round(hull_top(225)) - 11, 228, round(hull_top(225)) - 6), fill=C(col))
    if col_hi:
        for x in range(152, W, 2):
            px(d, x, round(hull_top(x)) - 8, col_hi)


@lru_cache(maxsize=1)
def ship_clear():
    """状态 1：清楚的货轮（W×H，透明底；只在 x ≥ 140 有东西）。"""
    im = A._new(W, H)
    m = hull_mask()
    a = np.array(im)
    bay = A._bayer(W, H)
    rows = list(range(22, WL, 16))
    for y in range(H):
        for x in range(W):
            if not m[y, x]:
                continue
            band = sum(1 for r in rows if r <= y)
            colk = (x + band * 13) // 30
            c = HULL_A if (colk + band) % 2 == 0 else HULL_B
            if hash01(colk, band, 3) < 0.25:
                c = HULL
            a[y, x, :3] = c
            a[y, x, 3] = 255
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 焊缝：横缝（上亮下暗）+ 错开的竖缝 + 铆钉
    for r in rows:
        for x in range(int(stem_x(r)) + 1, W):
            px(d, x, r, HULL_SEAM_HI)
            px(d, x, r + 1, HULL_SEAM_D)
            if x % 5 == 0:
                px(d, x, r - 1, (56, 62, 68))
    for bi, r in enumerate([16] + rows):
        r2 = rows[bi] if bi < len(rows) else WL
        x = 156 + int(hrange(0, 40, bi, 17))
        while x < W:
            for y in range(max(r + 2, int(hull_top(x)) + 4), r2):
                if x > stem_x(y) + 1:
                    px(d, x, y, HULL_SEAM_D)
            x += int(hrange(34, 52, bi, x, 18))
    # 舷墙上沿（亮一条）+ 船舷顶的一道暗线
    for x in range(int(stem_x(16)), W):
        yt = int(math.ceil(hull_top(x)))
        if yt <= WL:
            px(d, x, yt, HULL_HI)
            px(d, x, yt + 1, (60, 66, 72))
            px(d, x, yt + 4, HULL_SEAM_D)
    # 船头柱：迎着黎明那边的一道亮边（两格）
    for y in range(16, WL + 1):
        xs = int(math.ceil(stem_x(y)))
        if y >= hull_top(xs):
            px(d, xs, y, (84, 92, 98))
            px(d, xs + 1, y, (64, 70, 76))
    # 锚链孔 + 收着的锚
    d.ellipse((166, 34, 180, 42), fill=C((20, 22, 26)), outline=C((80, 86, 90)))
    d.arc((166, 34, 180, 42), 200, 330, fill=C((96, 102, 106)))
    hl(d, 169, 177, 40, (34, 36, 40))
    rect(d, 172, 41, 174, 58, (58, 60, 64))
    vl(d, 172, 41, 58, (82, 84, 88))
    d.polygon([(165, 56), (181, 56), (183, 61), (176, 60), (173, 66), (170, 60), (163, 61)], fill=C((54, 56, 60)))
    hl(d, 165, 181, 56, (88, 90, 94))
    px(d, 163, 61, (110, 76, 52))
    px(d, 183, 61, (110, 76, 52))
    # 舷窗（一排暗的，没有灯——船上没人）
    for x in (216, 232, 268, 284, 300, 316):
        y = 31
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=C((78, 84, 90)))
        d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=C((12, 14, 18)))
        px(d, x - 1, y - 1, (60, 70, 86))
    # 船名被漆盖掉了（一块颜色不一样的长方形，底下隐约几道看不清的笔画）+ 船首楼的导缆孔
    rect(d, 186, 25, 214, 29, (50, 55, 61))
    for xx in range(188, 212, 4):
        if hash01(xx, 91) < 0.7:
            vl(d, xx, 26, 28, (58, 63, 68))
            px(d, xx + 1, 26, (58, 63, 68))
    d.ellipse((157, 22, 163, 26), fill=C((18, 20, 24)), outline=C((74, 80, 86)))
    d.line((160, 27, 160, 36), fill=C(RUST_D))
    # 吃水标记（白色刻度 + 看不清的小号码）
    for k, y in enumerate(range(112, WL - 1, 6)):
        x0 = int(stem_x(y)) + 9
        hl(d, x0, x0 + 3, y, (176, 172, 162))
        if k % 2 == 0:
            rect(d, x0 + 5, y - 2, x0 + 6, y, (150, 146, 138))
            px(d, x0 + 7, y - 1, (150, 146, 138))
    # 锈：锚链孔、排水口、舷窗、绳梯挂点往下淌的锈水 + 水线附近的大片锈斑
    srcs = [(172, 44, 9, 70), (173, 64, 6, 40), (196, 24, 4, 50), (226, 24, 4, 60), (258, 24, 4, 46),
            (296, 24, 4, 64), (232, 34, 3, 30), (284, 34, 3, 26), (LADDER_X, 22, 3, 40), (312, 24, 3, 36)]
    for si, (sx, sy, n, ln) in enumerate(srcs):
        for k in range(n):
            x = int(sx + hrange(-3, 3, si, k, 1))
            L = int(ln * hrange(0.4, 1.0, si, k, 2))
            for j in range(L):
                y = sy + j
                if y > WL or not m[y, min(W - 1, max(0, x))]:
                    continue
                v = j / max(1, L)
                if hash01(si, k, j, 3) < 0.92 - v * 0.7:
                    px(d, x, y, RUST_L if v < 0.25 else (RUST if v < 0.6 else RUST_D))
    n = A._vnoise(W, H, 6, 61)
    n2 = A._vnoise(W, H, 3, 62)
    a = np.array(im)
    yy = np.arange(H)[:, None] * np.ones((1, W))
    lo = np.clip((yy - 70) / 70.0, 0, 1)                               # 越往水线锈得越多
    # 锈斑只长在焊缝下沿（一道道往下渗）和水线上面一截，不在钢板中间乱长
    seam_near = np.zeros((H, W), bool)
    for r in rows:
        seam_near[r + 2:r + 5] = True
    v = n + 0.12 * lo + 0.15 * (n2 - 0.5)
    zone = seam_near | (yy > WL - 22)
    patch = m & zone & (v > 0.66) & ((n2 > 0.45) | (yy > WL - 22))
    a[patch, :3] = np.array(RUST_D)
    patch2 = m & zone & (v > 0.78) & (bay < 0.6)
    a[patch2, :3] = np.array(RUST)
    # 水线：褪色的暗红漆带（上沿参差）+ 一层发绿的污垢
    for x in range(W):
        top = WL - 9 + int(round(1.5 * math.sin(x * 0.3) + hrange(-1, 1, x, 71)))
        for y in range(top, WL + 1):
            if m[y, x]:
                a[y, x, :3] = BOOT if (y < WL - 2 or bay[y, x] < 0.5) else GRIME
                if y == top:
                    a[y, x, :3] = (86, 44, 40)
    # 光：迎着左边黎明的船头弧面亮一点；贴着水面的雾把船身下半截罩得发灰（两档抖动）
    f = a[..., :3].astype(np.float32)
    for y in range(H):
        for x in range(W):
            if not m[y, x]:
                continue
            k = max(0.0, 1 - (x - stem_x(y)) / 26.0)
            if k > 0 and bay[y, x] < k:
                f[y, x] *= 1.12
            hz = 0.06 + 0.34 * min(1.0, max(0.0, (y - 50) / 95.0)) ** 1.4
            q = hz + (0.06 if bay[y, x] < 0.5 else 0.0)
            f[y, x] = f[y, x] * (1 - q) + np.array(FOG_C) * q
    a[..., :3] = np.clip(f, 0, 255).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 船舷栏杆 + 雾里的上层轮廓（比船身远、偏雾色）
    structures(d, (70, 78, 92), (88, 96, 110))
    # 绳梯：两根绳 + 每 6 px 一根木踏板，顶上两个挂钩，最下面一截泡在水里；绳梯在船身上落一道影
    xl, xr = LADDER_X - 3, LADDER_X + 3
    ytop = round(hull_top(LADDER_X)) - 3
    for y in range(ytop + 2, WL + 4):
        px(d, xr + 1, y, (30, 34, 40))
    for y in range(ytop + 6, WL + 4, 6):
        hl(d, xl + 1, xr - 1, y + 1, (30, 34, 40))
    for y in range(ytop, WL + 4):
        px(d, xl, y, ROPE if y % 3 else ROPE_D)
        px(d, xr, y, ROPE if (y + 1) % 3 else ROPE_D)
    for y in range(ytop + 6, WL + 4, 6):
        hl(d, xl, xr, y, RUNG)
        hl(d, xl + 1, xr - 1, y - 1, RUNG_HI)
    for x in (xl, xr):
        rect(d, x - 1, ytop - 2, x + 1, ytop, (150, 154, 160))
    # 水线一道拍岸的浅色 + 船身倒影（断断续续的暗条，越远越碎）+ 绳梯的倒影
    a = np.array(im)
    xs0 = int(math.ceil(stem_x(WL)))
    for x in range(xs0, W):                                            # 拍在船身上的水（亮、断续）
        if hash01(x // 3, 81) < 0.75:
            a[WL, x, :3] = (104, 114, 128)
        if hash01(x // 2, 82) < 0.35:
            a[WL - 1, x, :3] = (90, 100, 114)
    for r in range(1, 28):
        y = WL + r
        for x in range(xs0 + r // 3, W):
            k = ((x + r * 7) // (5 + r // 6)) % 4
            if r % 3 == 2 or k == 0:
                continue
            if hash01(x, r, 83) > 1.05 - r / 30.0 and r > 6:
                continue
            c = mix((56, 60, 72) if r < 10 else (44, 48, 60), sea_color(y), min(0.8, r / 30.0))
            a[y, x, :3] = c
            a[y, x, 3] = 255
        if r % 3 != 2:
            xx = LADDER_X + int(round(1.5 * math.sin(r * 0.9)))
            if hash01(r, 84) < 0.75:
                for x in (xx - 1, xx):
                    a[y, x, :3] = mix((150, 134, 104), sea_color(y), min(0.8, r / 30.0))
                    a[y, x, 3] = 255
    return Image.fromarray(a, 'RGBA')


@lru_cache(maxsize=1)
def ship_ghost():
    """状态 0.5：雾里淡淡的巨大船影——同一个轮廓（船身 + 上面的桅杆吊杆），半透明的暗色，没有细节；
    下半截（水线一带）抖动着淡进雾里，看不见水线。"""
    m = hull_mask()
    st = A._new(W, H)
    structures(ImageDraw.Draw(st), (255, 255, 255))
    sm = np.array(st)[..., 3] > 0
    bay = A._bayer(W, H)
    a = np.zeros((H, W, 4), np.uint8)
    a[..., :3] = (24, 28, 40)
    yy = np.arange(H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32)
    fade = np.clip((WL - yy) / 34.0, 0, 1)                             # 水线往上 34 px 慢慢淡掉
    alpha = np.where(m, np.where(bay < fade, 116, np.where(bay < fade + 0.35, 64, 0)), 0)
    a[sm & ~m, :3] = (66, 72, 88)                                       # 雾里透出来的桅杆 / 吊杆（比夜空亮一点）
    alpha = np.where(sm & ~m, np.where(bay < 0.6, 104, 70), alpha)
    rim = np.zeros_like(m)                                              # 船舷上沿被雾映亮的一道边
    for x in range(int(stem_x(16)), W):
        yt = int(math.ceil(hull_top(x)))
        rim[yt, x] = True
    a[rim, :3] = (78, 84, 100)
    alpha = np.where(rim, 96, alpha)
    a[..., 3] = alpha.astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


@lru_cache(maxsize=1)
def build():
    sx = SHIP_X0
    ships = [A._new(W - sx, H), ship_ghost().crop((sx, 0, W, H)), ship_clear().crop((sx, 0, W, H))]
    return dict(sky=sky_img(), fog_far=fog_far_img(), fog_near=fog_near_img(), mist=mist_img(), ships=ships)


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    ff, ffy = R['fog_far']
    fn, fny = R['fog_near']
    mi, miy = R['mist']
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0),
              dict(type='wrap', image=ex.img('fog_far', ff), period=W, k=0.0, y=ffy, vx=FOG_FAR_VX),
              ex.bake('swell_far', SWELL_FAR, N_SW, FPS_SW, swell_frame),
              dict(type='pick', key='ship', values=[0, 0.5, 1], images=[ex.img('ship%d' % i, im) for i, im in
                                                                        enumerate(R['ships'])],
                   x=SHIP_X0, y=0, k=0),
              ex.bake('swell_near', SWELL_NEAR, N_SW, FPS_SW, swell_frame),
              dict(type='wrap', image=ex.img('fog_near', fn), period=W, k=0.0, y=fny, vx=FOG_NEAR_VX),
              dict(type='tint', color=NIGHT[0], alpha=NIGHT[1], key='night')]
    fg = [dict(type='wrap', image=ex.img('mist', mi), period=W, k=0.0, y=miy, vx=MIST_VX)]
    st = ex.stage(W, GROUND, WALK, layers, fg, dict(ANCHORS))
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def compose(t, ship=0.0, night=0.0, fg=True):
    """直接拼一帧（不经导出），自检和预览用。night 按 JS 的公式乘 alpha。"""
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])

    def wrap(img_y, vx):
        im, y = img_y
        o = int(math.floor(t * vx)) % W
        two = Image.new('RGBA', (W * 2, im.height))
        two.paste(im, (0, 0))
        two.paste(im, (W, 0))
        out.alpha_composite(two.crop((o, 0, o + W, im.height)), (0, y))
    wrap(R['fog_far'], FOG_FAR_VX)
    out.alpha_composite(swell_frame(t).crop(SWELL_FAR), SWELL_FAR[:2])
    i = min(range(3), key=lambda j: abs((0, 0.5, 1)[j] - ship))
    out.alpha_composite(R['ships'][i], (SHIP_X0, 0))
    out.alpha_composite(swell_frame(t).crop(SWELL_NEAR), SWELL_NEAR[:2])
    wrap(R['fog_near'], FOG_NEAR_VX)
    if night:
        col = tuple(int(NIGHT[0][i:i + 2], 16) for i in (1, 3, 5))
        out.alpha_composite(Image.new('RGBA', (W, H), col + (int(255 * NIGHT[1] * night),)))
    if fg:
        wrap(R['mist'], MIST_VX)
    return out


def _checks(ex, BJ, st, R):
    bad = 0
    for s in (0, 0.5, 1):
        for t in (0.0, 0.5, 1.25, 7.0):
            im = np.array(BJ.ref_render(st, ex.images, 0, t, dict(ship=s)).convert('RGB'))
            bad += int((im.sum(-1) == 0).sum())
    ex.checked('海雾 船 0 / 0.5 / 1 × t 整屏都有画（没有露黑）', bad)
    ex.checked('天空底图整张不透明', int((np.array(R['sky'])[..., 3] != 255).sum()))
    ex.checked('ship pick 三张尺寸一致', 0 if len({im.size for im in R['ships']}) == 1 else 1)
    ex.checked('ship 0 是全透明（没有船）', int((np.array(R['ships'][0])[..., 3] > 0).sum()))
    ex.checked('ship 0.5 是半透明的影子（没有不透明像素）', int((np.array(R['ships'][1])[..., 3] == 255).sum()))
    sc = np.array(R['ships'][2])[..., 3]
    ex.checked('ship 1 船身不透明（x 190–320，y 30–140 抽查）', int((sc[30:140, 190 - SHIP_X0:] < 255).sum()))
    for name, box in (('swell_far', SWELL_FAR), ('swell_near', SWELL_NEAR)):
        ex.checked('strip %s 2 s 闭合（t=0 vs t=2）' % name, BJ.ndiff_rgba(swell_frame(0).crop(box), swell_frame(2.0).crop(box)))
        ex.checked('strip %s 帧条宽 ≤ 4096' % name, 0 if (box[2] - box[0]) * N_SW <= 4096 else 1)
    # 雾带首尾接得上：首尾两列的透明度差不超过图里相邻两列的最大差
    for name in ('fog_far', 'fog_near', 'mist'):
        al = np.array(R[name][0])[..., 3].astype(int)
        inner = int(np.abs(np.diff(al, axis=1)).max())
        seam = int(np.abs(al[:, -1] - al[:, 0]).max())
        ex.checked('wrap %s 首尾接缝（首尾两列差 ≤ 相邻列最大差 %d）' % (name, inner), max(0, seam - inner))
    out = 0
    for k, v in ANCHORS.items():
        if isinstance(v, list):
            if k in ('walk_x', 'ship_x'):
                out += not (0 <= v[0] < v[1] <= W)
            else:
                out += not (0 <= v[0] <= W and 0 <= v[1] <= H)
    ex.checked('锚点都在地图里（不满足的条数）', out)
    # 绳梯：底在水面（锚点 y 150 附近有踏板 / 绳）、顶挂在船舷上
    a = np.array(ship_clear())
    ex.checked('绳梯从船舷一直垂到水面（x 247/253，y 20–150 都是绳）',
               int((a[20:151, LADDER_X - 3, 3] < 255).sum() + (a[20:151, LADDER_X + 3, 3] < 255).sum()))
    # 导出 vs 直接拼（夜色 tint 只比 night=0；ref_render 的 tint 不乘数字）
    for s in (0, 0.5, 1):
        for t in (0.0, 1.25, 9.5):
            got = BJ.ref_render(st, ex.images, 0, t, dict(ship=s))
            ex.checked('海雾 ship=%.1f t=%.2f 导出 vs 直接拼' % (s, t), BJ.ndiff(got, compose(t, s)))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch2', 'after')
    os.makedirs(od, exist_ok=True)
    tiles = []
    for (s, night, t) in ((0, 1.0, 0.0), (0.5, 0.6, 0.5), (1, 0.0, 1.0), (1, 1.0, 1.5)):
        tiles.append(compose(t, s, night).convert('RGB'))
    sheet = Image.new('RGB', (W * 2 + 4, H * 2 + 4), (16, 16, 20))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(os.path.join(od, 'sea_fog_solo_states.png'))
    compose(1.0, 1, 0).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'sea_fog_solo_ship1.png'))
    compose(1.0, 0.5, 0).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'sea_fog_solo_ship05.png'))
    print('ok')
