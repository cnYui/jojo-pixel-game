# -*- coding: utf-8 -*-
r"""underwater —— 第2章第3战「暗蓝之月」的水下战场（2026-10-10 晚按体验版精度重画；第3章 sea_ch3 也用左边 320）。

承太郎被替身从游艇上拖进海里，在浅海的海底和鱼人一样的暗蓝之月打。侧视、地图 640 宽、不循环，两头是礁石墙。
水体偏青绿（暗蓝之月是宝蓝色的鱼人、承太郎是藏青的学生服，都要跳出来），沙地是浅色的。

地图：第2章 underwater_ch2 640 宽、可走带 y 158–178；第3章 sea_ch3 只用左边 320、可走带 y 150–176。
  ground 156（和原来一样）；沙地上沿 y 137–145，y 146 往下整张都是沙；y 150–178（x 8–632）只有平的东西
  （沙纹、贝壳、碎石、海星、锚链），石头 / 珊瑚 / 箱子 / 锚的底都在 y ≤ 148。

图层（从后往前）：
  water     static     水体渐变（上亮下暗）+ 左上角太阳那边略亮（屏幕固定）
  far       pano k .3  远处的礁丘 + 海带 / 海扇剪影 + 远处的沙（雾里，贴近水色）
  mid       pano k .55 中景礁石（有一座天然石拱）、珊瑚头、海扇、静止的海带 + 中景沙地
  ray0–6    strip k .6 斜照下来的光柱（亮度呼吸 + 底端轻轻摆；8 帧 @4 fps = 2 s）
  surface   strip k .5 从下往上看的水面波光：160 宽的周期图，同一张帧条放 x 0 / 160 / 320 三份接起来（24 帧 @12 fps）
  hull      pano k .5  游艇的船底剪影（层坐标 x 352–468；镜头往右才露出来，第3章 320 宽看不到）
  fish      wrap k .7  两小群鱼慢慢往左游（vx 6，周期 640）
  fish_solo clouds     两条单独的鱼（黄色刺尾鱼往右、条纹蝴蝶鱼往左）
  kelp0–4   strip k 1  海带（宽叶带，沿茎往上传的摆动 + 叶带扭转；根被近景沙脊挡住；12 帧 @6 fps）
  bed       pano k 1   近景海床：沙纹 / 颗粒 / 贝壳 / 碎石 / 海星 / 沙钱 / 锚链；后沿的石头（藤壶、珊瑚藻）、
                       脑珊瑚、鹿角珊瑚、桌珊瑚、管海绵、海扇、海胆、破木箱、半埋的旧锚、砗磲；两头的礁石墙
                       （岩层、板状珊瑚、海扇、海绵、藤壶，右墙洞里探出一条海鳝）
  caustic0/1 wrap k 1  沙地上的焦散光网：两层（vx +5 / −4）交叠处闪；只画 y 147 往下
  anemone0–2 strip k 1 海葵（触手摇；石头上那朵有两条小丑鱼绕着游）12 帧 @6 fps
  bubbles0/1 strip k 1 砗磲和墙缝里冒的零星小气泡（1 px，只升 20–30 px；16 帧 @8 fps）
战斗代码自己画的气泡柱（补气点：16 px 宽、从 y 16 到 178 的青色大气泡）背景里不放类似的东西。

锚点：surface（水面带下沿）、seabed（沙地上沿范围）、walk_ch2 / walk_ch3、walk_x、anchor、crate、clam、eel、hull、
      vortex（漩涡中心，战斗代码用 x 320）。
单独运行：python -B tools\bg_new\underwater.py → tools\bg_new\_preview\ch2\uw\layer_*.png（各图层）
"""
import sys
sys.dont_write_bytecode = True

import io  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from scipy import ndimage  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402

W, H = 320, 180
PW = 640
GROUND = 156
WALK = (150, 178)                 # 两张地图可走带的并集（第2章 158–178、第3章 150–176）
CH2_WALK, CH3_WALK = (158, 178), (150, 176)
WALK_X = (8, 632)                 # 地图两头的 obstacles 挡在 x < 8 / x > 632
SAND_SOLID = 146                  # 这一行往下整张都是沙（自检）
LOOP = 2.0                        # 所有帧条 2 s 闭合

FAR_K, MID_K, RAY_K, SURF_K, FISH_K = 0.3, 0.55, 0.6, 0.5, 0.7
FARW = W + int(math.ceil((PW - W) * FAR_K))       # 416
MIDW = W + int(math.ceil((PW - W) * MID_K))       # 496
RAYW = W + int(math.ceil((PW - W) * RAY_K))       # 512
SURFW = W + int(math.ceil((PW - W) * SURF_K))     # 480
SURF_TILE, SURF_H, SURF_N, SURF_FPS = 160, 26, 24, 12.0
RAY_N, RAY_FPS = 8, 4.0
SWAY_N, SWAY_FPS = 12, 6.0
BUB_N, BUB_FPS = 16, 8.0
CAUS_P, CAUS_Y = 160, 147
C = A._c4

# ============================================================ 调色
WATER = [(0, (186, 240, 224)), (18, (130, 214, 198)), (48, (94, 184, 172)), (88, (68, 154, 148)),
         (128, (52, 128, 126)), (180, (38, 102, 104))]


def water_at(y):
    y = max(0.0, min(float(H), float(y)))
    for (y0, c0), (y1, c1) in zip(WATER, WATER[1:]):
        if y <= y1:
            return mix(c0, c1, (y - y0) / float(y1 - y0))
    return WATER[-1][1]


WATER_ROWS = np.array([water_at(y) for y in range(H)], np.float32)


def haze(col, y, d):
    return mix(col, water_at(y), d)


SAND_HI = (230, 226, 184)
SAND_LT = (208, 204, 162)
SAND_MD = (186, 182, 144)
SAND_DK = (156, 154, 122)
SAND_DD = (124, 126, 102)
ROCK = [(34, 56, 62), (60, 88, 90), (88, 116, 110), (120, 146, 128), (160, 180, 154)]
WALLP = [(30, 48, 56), (54, 78, 82), (82, 106, 100), (112, 134, 116), (150, 166, 138)]
MIDP = [(40, 70, 78), (60, 94, 96), (84, 120, 114), (114, 148, 132), (150, 178, 154)]
INK = (20, 34, 40)
BARN = [(110, 106, 92), (164, 158, 136), (212, 206, 182), (242, 238, 216)]
CORALLINE = [(118, 74, 92), (156, 98, 116), (194, 130, 144), (226, 168, 174)]
TURF = [(48, 80, 50), (74, 112, 60), (106, 144, 74), (144, 176, 94)]
KELP_F = [(48, 82, 40), (78, 116, 50), (112, 148, 62), (150, 178, 82)]
KELP_B = [(40, 62, 36), (62, 86, 42), (88, 110, 52), (116, 136, 66)]
KELP_BF = [(60, 62, 34), (98, 98, 46), (136, 130, 62), (172, 164, 86)]       # 偏褐的（真正的海带色）
KELP_BB = [(46, 48, 30), (74, 74, 38), (102, 98, 48), (130, 124, 62)]


# ============================================================ 小工具
def arr(im):
    return np.array(im)


def img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def bayer(w, h):
    return A._bayer(w, h)


def shift(m, dy, dx):
    """m[y+dy, x+dx]（出界 = 0）。"""
    p = np.pad(m, 1)
    return p[1 + dy:1 + dy + m.shape[0], 1 + dx:1 + dx + m.shape[1]]


def comp(dst, src, x=0, y=0):
    """numpy RGBA 叠加（src over dst，dst 原地改；越界自动裁）。"""
    h, w = src.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    d = dst[y0:y1, x0:x1].astype(np.float32)
    sa = s[..., 3:4] / 255.0
    da = d[..., 3:4] / 255.0
    oa = sa + da * (1 - sa)
    rgb = (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    dst[y0:y1, x0:x1] = np.clip(np.round(np.concatenate([rgb, oa * 255.0], -1)), 0, 255).astype(dst.dtype)


def haze_arr(a, d, y0=0):
    """整块往水色里混 d（按每一行自己的水色）。"""
    h = a.shape[0]
    rows = WATER_ROWS[max(0, y0):max(0, y0) + h]
    if len(rows) < h:
        rows = np.concatenate([rows, np.repeat(rows[-1:], h - len(rows), 0)])
    f = a[..., :3].astype(np.float32) * (1 - d) + rows[:, None, :] * d
    a[..., :3] = np.clip(np.round(f), 0, 255).astype(np.uint8)
    return a


def draw_on(a, fn):
    """在 numpy 图上用 ImageDraw 画（fn(d, im)），画完写回。"""
    im = img(a)
    fn(ImageDraw.Draw(im), im)
    a[...] = arr(im)
    return a


def blob(w, h, balls, seed, noise=0.14, cell=6, base=None):
    """几个椭球的并（取最高）：返回 (遮罩, 高度)。balls = [(cx, cy, rx, ry)]，高度 = min(rx,ry)·sqrt(1 − d²)；
    边上加一点噪声，再开 / 闭运算去掉 1 px 的毛刺和小洞。"""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    f = np.full((h, w), -9.0, np.float32)
    z = np.zeros((h, w), np.float32)
    for (cx, cy, rx, ry) in balls:
        d2 = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        f = np.maximum(f, 1 - d2)
        z = np.maximum(z, np.sqrt(np.clip(1 - d2, 0, None)) * min(rx, ry))
    if noise:
        f = f + (A._fbm(w, h, cell, seed) - 0.5) * noise * 2
    m = f > 0
    m = ndimage.binary_opening(m, np.ones((2, 2), bool))
    m = ndimage.binary_closing(m, np.ones((2, 2), bool)) & (f > -0.3)
    if base is not None:
        m[int(base) + 1:] = False
    return m, z


def shade(mask, z, pal, seed, light=(-0.5, -0.8, 0.6), bump=0.5, bcell=5, facet=0.16, fcell=8, aspect=1.0,
          lo=-0.1, hi=1.0, dither=0.45, seam=0.45, speck=0.03, rim=True, outline=None, smooth=1.0, rim_top=True):
    """按高度场打光（左上来光）：逐像素 lambert + 噪声起伏 + Voronoi 切面的明暗偏移，分 len(pal) 级、只在级与级
    交界抖动；切面边界上，比上 / 左邻块暗的那块描暗一级的缝（seam 概率）——读起来是石面的转折，不是砌的砖。
    外轮廓：下 / 右描 outline，上沿亮边。返回 (H×W×4 uint8, 级数图；描边处 −1)。"""
    h, w = mask.shape
    out = np.zeros((h, w, 4), np.uint8)
    n = len(pal)
    if not mask.any():
        return out, np.full((h, w), -1, int)
    zz = z.astype(np.float32)
    if bump:
        zz = zz + (A._fbm(w, h, bcell, seed + 7) - 0.5) * bump * 4
    if smooth:
        zz = ndimage.gaussian_filter(zz, smooth)
    gy_, gx_ = np.gradient(zz)
    L = np.array(light, np.float32)
    L /= np.linalg.norm(L)
    lam = (-gx_ * L[0] - gy_ * L[1] + L[2]) / np.sqrt(gx_ * gx_ + gy_ * gy_ + 1)
    lab = None
    if facet:
        cw = max(2, int(round(fcell * aspect)))
        pts = np.array([(gx + hrange(0, cw, seed, gx, gy, 1), gy + hrange(0, fcell, seed, gx, gy, 2))
                        for gy in range(-fcell, h + fcell, fcell) for gx in range(-cw, w + cw, cw)], np.float32)
        yy, xx = np.mgrid[0:h, 0:w]
        _, lab = cKDTree(np.c_[pts[:, 0] / aspect, pts[:, 1]]).query(np.c_[xx.ravel() / aspect, yy.ravel()], k=1)
        lab = lab.reshape(h, w)
        off = np.array([(hash01(seed, i, 21) - 0.5) * 2 * facet for i in range(len(pts))], np.float32)
        lam = lam + off[lab]
    u = (lam - lo) / (hi - lo)
    q = np.floor(u * (n - 1) + 0.5 + (bayer(w, h) - 0.5) * dither)
    rng = np.random.default_rng(seed + 991)
    r = rng.random((h, w))
    q[r < speck / 2] -= 1
    q[r > 1 - speck / 2] += 1
    q = np.clip(q, 0, n - 1).astype(int)
    if lab is not None and seam:
        nl = int(lab.max()) + 1
        lm = lab[mask]
        mq = np.bincount(lm, weights=q[mask], minlength=nl) / np.maximum(1, np.bincount(lm, minlength=nl))
        keep = np.array([hash01(seed, i, 22) < seam for i in range(nl)])
        inner = mask & shift(mask, 0, 1) & shift(mask, 1, 0) & shift(mask, -1, 0) & shift(mask, 0, -1)
        q0 = q.copy()
        for dy, dx in ((-1, 0), (0, -1)):
            nb = shift(lab, dy, dx)
            s = inner & (lab != nb) & keep[lab] & (mq[nb] > mq[lab] + 0.25)
            q[s] = np.maximum(0, q0[s] - 1)
    top = mask & ~shift(mask, -1, 0)
    bot = mask & ~shift(mask, 1, 0)
    right = mask & ~shift(mask, 0, 1)
    if rim and rim_top:
        q[top] = np.maximum(q[top], n - 2)
        q[top & ~right & (r < 0.75)] = n - 1
    P = np.array(pal, np.uint8)
    out[..., :3] = P[q]
    out[..., 3] = np.where(mask, 255, 0)
    edge = (bot | right) & ~top & mask
    out[edge, :3] = np.array(outline or INK, np.uint8)
    q = np.where(mask, q, -1)
    q[edge] = -1
    return out, q


def encrust(a, q, mask, seed, pink=0.08, green=0.10, cell=8, n=5, dots=0.05):
    """石面上的附着物：成片的粉色珊瑚藻、绿色短藻（偏向朝上的亮面），按原来的明暗级数换成对应色阶。
    斑块要大（cell 大）、要少——碎点多了就成了花布。"""
    h, w = mask.shape
    ok = mask & (q >= 0)
    if ok.sum() < 8:
        return
    f1 = A._fbm(w, h, cell, seed + 31)
    f2 = A._fbm(w, h, cell + 2, seed + 32) + np.clip(q, 0, None) * 0.025
    t1 = np.quantile(f1[ok], 1 - pink) if pink else 9
    t2 = np.quantile(f2[ok], 1 - green) if green else 9
    for f, t, ramp in ((f1, t1, CORALLINE), (f2, t2, TURF)):
        m = ok & (f > t)
        m = ndimage.binary_opening(m, np.ones((2, 2), bool))
        idx = np.clip(np.round(q[m] / max(1, n - 1) * (len(ramp) - 1)), 0, len(ramp) - 1).astype(int)
        a[m, :3] = np.array(ramp, np.uint8)[idx]
    rng = np.random.default_rng(seed + 33)
    sp = ok & (f2 > t2) & (rng.random((h, w)) < dots)
    a[sp, :3] = TURF[3]
    sp = ok & (f1 > t1) & (rng.random((h, w)) < dots)
    a[sp, :3] = CORALLINE[3]


def barnacle(d, x, y, big=True):
    """藤壶：小火山口（下面一排亮 / 中 / 暗三格是壳，上面中间一格黑的是口）；小的只有两格。"""
    if big:
        d.point((x, y - 1), fill=C((40, 40, 40)))
        d.point((x - 1, y), fill=C(BARN[3]))
        d.point((x, y), fill=C(BARN[2]))
        d.point((x + 1, y), fill=C(BARN[0]))
    else:
        d.point((x, y), fill=C(BARN[2]))
        d.point((x + 1, y), fill=C(BARN[0]))


def barnacles(d, pts, seed):
    for i, (x, y) in enumerate(pts):
        barnacle(d, int(x), int(y), hash01(seed, i, 3) < 0.55)


def cluster_pts(mask, cx, cy, n, seed, spread=4.0):
    """一簇藤壶的位置：挤在一起成一片壳（彼此至少隔 2 格），只落在石面上。"""
    out = []
    for i in range(n * 4):
        x = int(round(cx + hrange(-spread, spread, seed, i, 1)))
        y = int(round(cy + hrange(-spread * 0.55, spread * 0.55, seed, i, 2)))
        if 1 <= y < mask.shape[0] - 1 and 1 <= x < mask.shape[1] - 1 and mask[y, x] and mask[y - 1, x] \
                and mask[y, x + 1] and all(abs(x - a) + abs(y - b) >= 2 for a, b in out):
            out.append((x, y))
        if len(out) >= n:
            break
    return out


def contact_shadow(a, cx, y, rx, ry=2.5, k=0.24):
    """物体落在沙上的接触阴影（往下压暗，带一点抖动）。"""
    h, w = a.shape[:2]
    for yy in range(int(y - ry), int(y + ry) + 1):
        for xx in range(int(cx - rx), int(cx + rx) + 1):
            if 0 <= yy < h and 0 <= xx < w and a[yy, xx, 3]:
                dd = ((xx - cx) / rx) ** 2 + ((yy - y) / ry) ** 2
                if dd < 1 and hash01(xx, yy, 77) < 0.9:
                    kk = k * (1 - dd) ** 0.6
                    a[yy, xx, :3] = (a[yy, xx, :3].astype(np.float32) * (1 - kk)).astype(np.uint8)


def crack(d, pts, dark, light=None):
    """一道裂缝：深色折线，下面一行亮一点（裂缝下沿受光）。"""
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if light is not None:
            d.line((xa, ya + 1, xb, yb + 1), fill=C(light))
        d.line((xa, ya, xb, yb), fill=C(dark))


# ============================================================ 水体（static）
@lru_cache(maxsize=1)
def water_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), [(y / float(H - 1), c) for y, c in WATER], bands=24)
    a = arr(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(1 - np.hypot((xx - 50) / 300.0, (yy + 20) / 160.0), 0, 1) ** 2 * 0.12   # 太阳在左上
    q = np.floor(g * 50 + bayer(W, H)) / 50.0
    a[..., :3] *= (1 + q[..., None])
    return img(a)


# ============================================================ 水面（strip，160 宽的周期图）
SURF_PAL = [(92, 186, 182), (118, 204, 196), (150, 222, 212), (190, 240, 230), (232, 254, 247)]


@lru_cache(maxsize=1)
def _surf_pts():
    """水面光网的特征点：x 方向 10 列（周期 160）、沿水面纵深 6 行；每个点在一个小椭圆上绕圈（2 s 一圈）。"""
    rng = np.random.default_rng(951)
    pts = []
    for j in range(6):
        for i in range(10):
            pts.append((i * 16 + rng.random() * 14, -8 + j * 14 + rng.random() * 12, 2.5 + rng.random() * 3,
                        1.5 + rng.random() * 2.5, rng.random() * 6.283, 1 if rng.random() < 0.5 else -1))
    return pts


def surface_tile(t):
    """从下往上看的水面：一张会动的光网（Worley：离两个最近特征点一样远的地方最亮），头顶（画面最上）格子大，
    越往下（越远、掠射）压得越扁、越暗；下沿一条波浪亮边 + 一行半透明过渡。
    特征点绕 2 s 一圈的小椭圆、x 方向 160 周期复制 → 横向 160 周期、2 s 严格闭合。"""
    t = t % LOOP
    tau = math.pi * t
    w, h = SURF_TILE, SURF_H
    K = 2 * math.pi / w
    xs = np.arange(w, dtype=np.float32)
    ys = np.arange(h, dtype=np.float32)
    edge = (15.0 + 1.6 * np.sin(K * 2 * xs - tau) + 1.0 * np.sin(K * 5 * xs + 2 * tau + 1.3)
            + 0.5 * np.sin(K * 9 * xs - 3 * tau + 0.4))
    v = ys * 2.0 + ys ** 2 * 0.15                                   # 屏幕行 → 水面上的纵深（越往下越压扁）
    P = []
    for (u0, v0, ru, rv, ph, sg) in _surf_pts():
        u = u0 + ru * math.cos(sg * tau + ph)
        vv = v0 + rv * math.sin(sg * tau + ph)
        for dx in (-w, 0, w):
            P.append((u + dx, vv))
    X, V = np.meshgrid(xs, v)
    dd, _ = cKDTree(np.array(P, np.float32)).query(np.c_[X.ravel(), V.ravel()], k=2)
    f = (dd[:, 1] - dd[:, 0]).reshape(h, w)
    f1 = dd[:, 0].reshape(h, w)
    yy = ys[:, None]
    base = 0.86 - 0.5 * np.clip(yy / 15.0, 0, 1)
    line = np.clip(1 - f / (2.6 - 1.2 * np.clip(yy / 15.0, 0, 1)), 0, 1)
    b = base + 0.42 * line - 0.05 * np.clip(f1 / 9.0, 0, 1)
    b[:2] += 0.12
    n = len(SURF_PAL)
    lv = np.clip(np.floor(b * (n - 1) + 0.5 + (bayer(w, h) - 0.5) * 0.35), 0, n - 1).astype(int)
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = np.array(SURF_PAL, np.uint8)[lv]
    a[..., 3] = 255
    E = np.round(edge).astype(int)
    for x in range(w):
        e = int(E[x])
        a[e + 1:, x, 3] = 0
        a[e, x, :3] = (236, 254, 248)
        a[e - 1, x, :3] = np.maximum(a[e - 1, x, :3], np.array(SURF_PAL[2], np.uint8))
        a[e + 1, x] = (140, 218, 206, 140)
        if e + 2 < h:
            a[e + 2, x] = (140, 218, 206, 56)
    return img(a)


def surface_frame(t):
    return surface_tile(t)


# ============================================================ 光柱（strip ×7，层坐标 k .6）
RAY_COL = (220, 255, 240)
RAY_Y0, RAY_Y1 = 10, 152
# x（层坐标顶端左边）、顶宽、斜移（底比顶往右）、底宽、顶 alpha、相位
RAYS = [(10, 10, 46, 20, 96, 0.0), (84, 16, 56, 30, 78, 1.9), (160, 8, 42, 16, 104, 3.3),
        (226, 13, 52, 24, 72, 4.6), (300, 11, 50, 22, 92, 2.4), (374, 17, 60, 30, 76, 5.4),
        (454, 9, 44, 18, 98, 0.8)]


def ray_box(i):
    x0, wt, dx, wb, a0, ph = RAYS[i]
    return (x0 - 2, RAY_Y0, int(math.ceil(x0 + dx + 2.6 + wb)) + 2, RAY_Y1)


def ray_frame(i, t):
    """一道光柱（层坐标，透明底）：顶端贴着水面不动，底端随 2 s 周期左右摆 2 px，亮度呼吸 ±18%。
    alpha 按 8 一级量化 + 有序抖动（像素画的光柱边）。"""
    x0, wt, dx, wb, a0, ph = RAYS[i]
    t = t % LOOP
    tau = math.pi * t
    amp = 0.82 + 0.18 * math.sin(tau + ph)
    sway = 2.2 * math.sin(tau + ph + 1.1)
    bx0, by0, bx1, by1 = ray_box(i)
    w, h = bx1 - bx0, by1 - by0
    ys = np.arange(h, dtype=np.float32)[:, None]
    xs = np.arange(w, dtype=np.float32)[None, :] + bx0
    v = ys / (h - 1)
    left = x0 + (dx + sway) * v
    width = wt + (wb - wt) * v
    s = (xs - left) / width
    inside = (s >= 0) & (s <= 1)
    edge = np.clip(1 - np.abs(2 * s - 1) ** 2.2, 0, 1)
    alpha = a0 * amp * (1 - v) ** 1.5 * edge * inside * np.clip(ys / 8.0, 0, 1)
    q = np.floor(alpha / 8.0 + bayer(w, h)) * 8.0
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = RAY_COL
    a[..., 3] = np.clip(q, 0, 255).astype(np.uint8)
    out = np.zeros((H, max(RAYW, bx1), 4), np.uint8)
    out[by0:by1, bx0:bx1] = a
    return img(out)


# ============================================================ 远景（pano k .3）
FARP = [(42, 86, 96), (58, 104, 110), (78, 124, 124)]


@lru_cache(maxsize=1)
def far_img():
    w = FARW
    a = np.zeros((H, w, 4), np.uint8)
    forms = [(22, 92, 30), (92, 106, 24), (160, 80, 30), (232, 108, 20), (294, 88, 36), (364, 100, 28), (412, 92, 22)]
    balls = []
    for i, (cx, top, rx) in enumerate(forms):
        hh = 128 - top
        balls.append((cx, 128, rx, hh))
        balls.append((cx + hrange(-rx * 0.6, rx * 0.6, i, 1), 128 - hh * 0.55, rx * 0.55, hh * 0.5))
        balls.append((cx + hrange(-rx * 0.8, rx * 0.8, i, 2), 128 - hh * 0.25, rx * 0.5, hh * 0.35))
    for x in range(-20, w + 40, 26):
        balls.append((x, 128, 20, 9 + 6 * hash01(x, 2)))
    m, z = blob(w, H, balls, 501, noise=0.12, cell=7, base=170)
    rgba, q = shade(m, z, FARP, 501, bump=0.4, facet=0.12, fcell=10, dither=0.4, seam=0.2, outline=(46, 96, 106),
                    speck=0.0)
    haze_arr(rgba, 0.5)
    comp(a, rgba)

    def deco(d, im):
        for i in range(16):                                     # 远处的海带剪影（细、弯）
            x0 = hrange(0, w, i, 510)
            hh = hrange(28, 60, i, 511)
            col = C(haze((40, 90, 72), 100, 0.5))
            prev = None
            for k in range(0, int(hh), 2):
                x = x0 + math.sin(k * 0.09 + i) * 2.5 + k * 0.1
                p = (round(x), round(128 - k))
                if prev:
                    d.line((prev, p), fill=col, width=2 if k < hh * 0.6 else 1)
                prev = p
        for i, (x, y) in enumerate(((52, 96), (190, 86), (330, 92), (396, 98))):   # 远处的海扇
            col = C(haze((150, 90, 110), y, 0.55))
            for k in range(8):
                ang = math.radians(-60 + k * 17)
                L = hrange(8, 12, i, k)
                d.line((x, y, round(x + math.sin(ang) * L), round(y - math.cos(ang) * L)), fill=col)
            d.arc((x - 7, y - 7, x + 7, y + 7), 210, 330, fill=col)
    draw_on(a, deco)
    ys_ = 121 + 1.5 * np.sin(np.arange(w) * 0.031 + 0.5) + 1.0 * np.sin(np.arange(w) * 0.083)
    for x in range(w):                                          # 远处的沙（雾里）
        y0 = int(round(ys_[x]))
        for y in range(y0, H):
            a[y, x, :3] = mix(SAND_MD, water_at(y), 0.6)
            a[y, x, 3] = 255
        a[y0, x, :3] = mix(SAND_HI, water_at(y0), 0.58)
    return img(a)


# ============================================================ 海带（宽叶带）
def ribbon(d, x0, y0, L, wmax, amp, ph, seed, t, lean=0.0, front=KELP_F, back=KELP_B):
    """一条海带：根部一小段细茎，往上是带波浪边的宽叶带，尖端收窄。摆动是沿叶带往上传的波（2 s 一周），
    叶带沿长度扭转（宽度按 |cos| 变窄，翻到背面换暗色）——读起来是在水里飘的带子，不是竹竿。"""
    t = t % LOOP
    tau = math.pi * t
    for k2 in range(0, int(L * 2) + 1):
        k = k2 / 2.0
        s = k / L
        y = int(round(y0 - k))
        sway = amp * s ** 1.3 * math.sin(tau + ph - 2.6 * s) + lean * s * L
        cx = x0 + sway
        if s < 0.12:
            hw = 0.5
        else:
            hw = wmax / 2.0 * math.sin(math.pi * min(1.0, (s - 0.12) / 0.88)) ** 0.55
            hw *= 1 + 0.2 * math.sin(k * 0.9 + seed * 1.7)
        tw = math.cos(1.6 * math.pi * s + seed + 0.6 * math.sin(tau + ph - 2.0 * s))
        hwe = max(0.5, hw * (0.3 + 0.7 * abs(tw)))
        pal = front if tw > 0 else back
        xl, xr = int(round(cx - hwe)), int(round(cx + hwe))
        d.line((xl, y, xr, y), fill=C(pal[1]))
        if xr - xl >= 2:
            d.point((xl, y), fill=C(pal[3] if tw > 0 else pal[2]))
            d.point((xr, y), fill=C(pal[0]))
            if xr - xl >= 4 and (k2 % 3):
                d.point((int(round(cx)) - (1 if tw > 0 else 0), y), fill=C(pal[2]))
        elif s >= 0.12:
            d.point((xr, y), fill=C(pal[0]))


# (根 x, 根 y, 长, 最宽, 摆幅, 相位, 种子, 斜)
KELP_GROUPS = [
    [(58, 142, 96, 6, 5.0, 0.0, 1, 0.04), (66, 143, 66, 5, 4.0, 1.2, 2, 0.08), (50, 143, 48, 4, 3.0, 2.6, 3, 0.02)],
    [(104, 141, 108, 7, 6.0, 0.7, 4, 0.05), (112, 142, 78, 5, 4.5, 2.1, 5, 0.1)],
    [(304, 141, 116, 7, 6.0, 1.6, 6, 0.04), (314, 142, 88, 6, 5.0, 0.2, 7, 0.07), (322, 143, 60, 5, 3.5, 3.0, 8, 0.1)],
    [(398, 142, 72, 6, 4.5, 2.4, 9, 0.06), (406, 143, 52, 5, 3.5, 0.9, 10, 0.1)],
    [(566, 142, 100, 7, 5.5, 1.1, 11, 0.03), (576, 143, 72, 5, 4.5, 2.9, 12, 0.08)],
]


def kelp_box(gi):
    g = KELP_GROUPS[gi]
    x0 = min(k[0] for k in g) - 12
    x1 = max(k[0] + k[7] * k[2] for k in g) + 14
    y0 = min(k[1] - k[2] for k in g) - 3
    y1 = max(k[1] for k in g) + 1
    return (int(x0), int(y0), int(math.ceil(x1)), int(y1))


def kelp_frame(gi, t):
    x0, y0, x1, y1 = kelp_box(gi)
    im = Image.new('RGBA', (x1, y1), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    g = sorted(KELP_GROUPS[gi], key=lambda k: -k[2])           # 长的在后面
    for (kx, ky, L, wm, amp, ph, seed, lean) in g:
        brown = seed % 3 == 0
        ribbon(d, kx, ky, L, wm, amp, ph, seed, t, lean, front=KELP_BF if brown else KELP_F,
               back=KELP_BB if brown else KELP_B)
    a = arr(im)
    haze_arr(a, 0.1)
    return img(a)


# ============================================================ 中景（pano k .55）
def mid_rock(a, balls, seed, d=0.4, w=None):
    h, ww = a.shape[:2]
    m, z = blob(ww, h, balls, seed, noise=0.14, cell=6, base=150)
    rgba, q = shade(m, z, MIDP, seed, bump=0.5, facet=0.14, fcell=9, dither=0.45, seam=0.35, outline=(34, 64, 72),
                    speck=0.02)
    encrust(rgba, q, m, seed, pink=0.05, green=0.07, n=len(MIDP), dots=0.0)
    haze_arr(rgba, d)
    comp(a, rgba)
    return m, q


@lru_cache(maxsize=1)
def mid_img():
    w = MIDW
    a = np.zeros((H, w, 4), np.uint8)
    sand_top = (132 + 1.6 * np.sin(np.arange(w) * 0.027 + 1.1) + 1.2 * np.sin(np.arange(w) * 0.071 + 0.3)).round().astype(int)
    # 静止的海带（中景，在礁石后面）
    def kelp_back(d, im):
        for i, (x0, L) in enumerate(((70, 70), (84, 52), (150, 60), (300, 84), (312, 62), (388, 70), (470, 76))):
            ribbon(d, x0, 140, L, 5, 3.0, i * 1.3, i + 30, 0.0, 0.03,
                   front=[haze(c, 100, 0.42) for c in KELP_F], back=[haze(c, 100, 0.42) for c in KELP_B])
    draw_on(a, kelp_back)
    mid_rock(a, [(30, 146, 30, 46), (52, 124, 18, 22), (12, 116, 14, 28), (40, 104, 12, 12)], 601)
    # 天然石拱：两根柱子 + 横梁，中间掏空
    yy, xx = np.mgrid[0:H, 0:w].astype(np.float32)
    hole = (((xx - 239) / 17.0) ** 2 + ((yy - 132) / 36.0) ** 2) < 1.0
    m, z = blob(w, H, [(206, 146, 19, 70), (272, 148, 19, 64), (238, 86, 42, 14), (218, 94, 18, 16),
                       (260, 90, 18, 16), (282, 120, 12, 24)], 602, noise=0.14, cell=6, base=150)
    m &= ~hole
    z = np.where(m, z, 0)
    rgba, q = shade(m, z, MIDP, 602, bump=0.5, facet=0.14, fcell=9, dither=0.45, seam=0.35, outline=(34, 64, 72),
                    speck=0.02)
    encrust(rgba, q, m, 602, pink=0.05, green=0.08, n=len(MIDP), dots=0.0)
    haze_arr(rgba, 0.4)
    comp(a, rgba)
    mid_rock(a, [(352, 146, 26, 44), (370, 122, 14, 18), (340, 126, 10, 14)], 603)
    mid_rock(a, [(432, 148, 34, 62), (414, 114, 16, 26), (452, 122, 14, 20)], 604)
    mid_rock(a, [(494, 146, 20, 34)], 605)
    mid_rock(a, [(120, 146, 16, 20), (144, 148, 12, 14), (318, 148, 14, 14), (162, 148, 8, 8)], 606)

    def corals(d, im):
        for (x, y, kind, col) in ((42, 100, 'fan', (182, 84, 112)), (226, 74, 'fan', (206, 118, 72)),
                                  (252, 76, 'heads', (176, 124, 154)), (420, 90, 'heads', (196, 156, 92)),
                                  (454, 104, 'fan', (160, 92, 156)), (364, 106, 'heads', (186, 112, 112)),
                                  (14, 90, 'heads', (166, 156, 104)), (120, 128, 'heads', (186, 150, 96))):
            cc = haze(col, y, 0.42)
            hi = mix(cc, (250, 246, 230), 0.3)
            if kind == 'fan':
                for k in range(9):
                    ang = math.radians(-70 + k * 17.5)
                    L = hrange(9, 14, x, k)
                    ex, ey = x + math.sin(ang) * L, y - math.cos(ang) * L
                    d.line((x, y, round(ex), round(ey)), fill=C(cc))
                for r in (5, 9):
                    d.arc((x - r, y - r, x + r, y + r), 200, 340, fill=C(cc))
                d.line((x, y, x, y + 4), fill=C(mix(cc, (30, 40, 40), 0.3)))
            else:
                for k in range(4):
                    bx = x - 6 + k * 4
                    d.ellipse((bx - 3, y - 4 - k % 2 * 2, bx + 3, y + 1), fill=C(cc))
                    d.point((bx - 1, y - 3 - k % 2 * 2), fill=C(hi))
    draw_on(a, corals)
    for x in range(w):                                          # 中景沙地（盖住礁石的底）
        y0 = sand_top[x]
        for y in range(y0, H):
            a[y, x, :3] = mix(SAND_MD, water_at(y), 0.4)
            a[y, x, 3] = 255
        a[y0, x, :3] = mix(SAND_HI, water_at(y0), 0.4)
        if hash01(x, 61) < 0.3:
            a[min(H - 1, y0 + 2 + int(hash01(x, 62) * 6)), x, :3] = mix(SAND_DK, water_at(y0), 0.4)
    return img(a)


# ============================================================ 鱼（wrap / clouds）
def sprite(rows, pal):
    a = np.zeros((len(rows), len(rows[0]), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.':
                a[y, x, :3] = pal[ch]
                a[y, x, 3] = 255
    return img(a)


def fish_sprite(kind='school'):
    if kind == 'school':                      # 6×3，朝左：银身、背上一道黄
        return sprite(['.yyy.t', 'ebbbtt', '.sss.t'],
                      {'y': (232, 214, 120), 'b': (196, 216, 204), 's': (130, 164, 156), 'e': (30, 40, 44),
                       't': (226, 196, 90)})
    if kind == 'tang':                        # 10×7，朝右：黄色刺尾鱼
        return sprite(['...yyy....', '.yyyyyy..t', 'yyyyyyyy.t', 'yyyyyyeyttt'[:10], 'yyyyyyyy.t', '.yyyyyy..t',
                       '...yyy....'], {'y': (246, 212, 72), 't': (226, 186, 58), 'e': (24, 24, 30)})
    return sprite(['....www.....', '..wbwwbww...', '.ewbwwbwwttt', 'wwwbwwbwwttt', '.wwbwwbww.t.', '...www.....'],
                  {'w': (238, 236, 222), 'b': (44, 44, 52), 'e': (20, 20, 26), 't': (240, 202, 72)})


FISH_Y0 = 30


@lru_cache(maxsize=1)
def fish_img():
    """一大一小两群鱼（640 周期，朝左游）。"""
    im = Image.new('RGBA', (PW, 74), (0, 0, 0, 0))
    sp = fish_sprite('school')
    for g, (gx, gy, n, rw, rh) in enumerate(((150, 30, 19, 70, 22), (470, 52, 8, 32, 12))):
        for i in range(n):
            u = hash01(g, i, 31)
            x = gx + (u - 0.5) * rw * (1 + 0.3 * math.sin(i))
            y = gy + (hash01(g, i, 32) - 0.5) * rh * (1 - abs(u - 0.5))
            im.alpha_composite(sp, (int(round(x)) % (PW - 6), int(round(y))))
    a = arr(im)
    haze_arr(a, 0.22, FISH_Y0)
    return img(a)


# ============================================================ 近景海床（pano k 1，640 宽）
def sand_top_x():
    xs = np.arange(PW, dtype=np.float32)
    n = A._fbm(PW, 1, 24, 701)[0] - 0.5
    y = 140.5 + 2.0 * np.sin(xs * 2 * math.pi * 3 / PW + 0.7) + 1.3 * np.sin(xs * 2 * math.pi * 7 / PW + 2.1) + n * 3
    return np.clip(np.round(y), 137, 145).astype(int)


def sand_col(y):
    """沙地在 y 行的底色（和 sand_layer 的底色级 + 水色一致；箱子 / 锚链埋进去的沙堆用）。"""
    u = float(np.clip((y - 150) / 22.0, 0, 1))
    return mix(mix(SAND_RAMP[3], SAND_RAMP[4], u), water_at(y), sand_haze(y))


SAND_RAMP = [(118, 122, 100), (144, 146, 116), (166, 166, 132), (186, 184, 146), (204, 200, 160), (220, 216, 174),
             (236, 232, 192)]


def sand_haze(y):
    """沙地离得越远（越往上）混越多水色。"""
    return 0.34 * float(np.clip((168 - y) / 30.0, 0, 1)) ** 1.2


def sand_layer():
    """沙地（不透明，从上沿铺到底）：色阶图 = 按远近分的底色级 + 大块明暗斑（±1 级、边上抖动）+ 沙纹（亮脊 + 暗槽）
    + 稀疏的颗粒，最后按行混水色（远处发青）。返回 (H×PW×4, 上沿数组)。"""
    top = sand_top_x()
    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(PW, dtype=np.float32)[None, :]
    b = bayer(PW, H)
    lev = 3.0 + np.clip((yy - 150) / 22.0, 0, 1) * 1.0 + np.zeros((1, PW), np.float32)
    big = A._fbm(PW, H, 28, 702)
    lev = lev + np.where(big > 0.6, 1.0, 0.0) * np.clip((big - 0.6) * 12, 0, 1) \
        - np.where(big < 0.4, 1.0, 0.0) * np.clip((0.4 - big) * 12, 0, 1)
    L = np.floor(lev + 0.5 + (b - 0.5) * 0.9).astype(int)
    # 沙纹：越往下越疏、越粗、越弯
    rows = [144, 147.5, 151.5, 156, 161, 166.5, 172.5, 179]
    for r, ry in enumerate(rows):
        lam = 34 + r * 7
        amp = 0.7 + r * 0.16
        ph = hash01(r, 704) * 6.28
        y = ry + amp * np.sin(2 * math.pi * xx[0] / lam + ph) + 0.5 * np.sin(2 * math.pi * xx[0] / (lam * 0.41) + ph * 2)
        gap = np.sin(xx[0] / (11.0 + r * 2) + r * 1.3) + np.sin(xx[0] / (27.0 + r) + r * 0.7)
        yi = np.round(y).astype(int)
        for x in range(PW):
            if gap[x] < -1.1 or yi[x] < top[x] + 2 or yi[x] >= H:
                continue
            L[yi[x], x] = L[yi[x], x] + 2
            if yi[x] + 1 < H:
                L[yi[x] + 1, x] = L[yi[x] + 1, x] - 1
            if r >= 3 and gap[x] > 0.5 and yi[x] + 2 < H:
                L[yi[x] + 2, x] = L[yi[x] + 2, x] - 1
    rng = np.random.default_rng(703)
    g = rng.random((H, PW))
    L[g < 0.012] -= 2
    L[g > 0.992] += 2
    L = np.clip(L, 0, len(SAND_RAMP) - 1)
    a = np.zeros((H, PW, 4), np.uint8)
    a[..., :3] = np.array(SAND_RAMP, np.uint8)[L]
    for y in range(H):
        dz = sand_haze(y)
        if dz > 0:
            a[y, :, :3] = np.clip(a[y, :, :3].astype(np.float32) * (1 - dz) + WATER_ROWS[y] * dz, 0, 255).astype(np.uint8)
    a[..., 3] = np.where(yy >= top[None, :], 255, 0).astype(np.uint8)
    on = a[..., 3] > 0
    col = rng.random((H, PW))
    for c, p in (((214, 168, 160), 0.0025), ((92, 110, 88), 0.002), ((242, 238, 220), 0.003)):
        m = on & (col < p) & (yy > 148)
        a[m, :3] = c
        col = np.where(m, 1.0, col - p)
    for x in range(PW):                                          # 上沿：沙脊顶一道亮边、下面一行略暗
        y0 = top[x]
        a[y0, x, :3] = mix(SAND_RAMP[5], water_at(y0), sand_haze(y0) * 0.8)
        a[y0 + 1, x, :3] = mix(tuple(int(v) for v in a[y0 + 1, x, :3]), SAND_RAMP[1], 0.3)
    return a, top


# ---------------------------------------------------------------- 两头的礁石墙
def wall_mask(prof, left, seed, amp=2.2):
    """prof = [(y, x)]：左墙 = 这一行 x < 边、右墙 = x > 边；墙脚在 y 146（再往下全是沙，人能走到墙跟前）。"""
    ys = np.arange(H, dtype=np.float32)
    yp = [p[0] for p in prof]
    xp = [p[1] for p in prof]
    edge = np.interp(ys, yp, xp) + (A._fbm(1, H, 10, seed)[:, 0] - 0.5) * 2 * amp
    xx = np.arange(PW)[None, :]
    if left:
        m = xx < edge[:, None]
    else:
        m = xx > edge[:, None]
    m[147:] = False
    return m, edge


def wall_shade(m, left, seed):
    """墙的光：高度 = 到边的距离（地图外、画面上方都算墙里面）+ 横向岩层（每层上沿亮、往下暗下去）。"""
    pm = np.pad(m, 1, constant_values=False)
    pm[0, :] = True                                  # 画面上方、地图外面都算墙里面（不在那里描边、不当成墙的边）
    if left:
        pm[:, 0] = True
    else:
        pm[:, -1] = True
    dist = ndimage.distance_transform_edt(pm)[1:-1, 1:-1]
    z = np.sqrt(dist) * 2.2
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    nn = A._fbm(PW, H, 8, seed + 3)
    band = (yy + nn * 10 + np.sin(xx * 0.05 + seed) * 2) / 13.0
    z = z - (band - np.floor(band)) * 3.2
    rgba, q = shade(m, z, WALLP, seed, bump=0.5, bcell=5, facet=0.14, fcell=10, aspect=1.8, dither=0.4, seam=0.4,
                    speck=0.03, smooth=0.9)
    encrust(rgba, q, m, seed, pink=0.06, green=0.08, cell=10, n=len(WALLP))
    return rgba, q


def plate_coral(d, x, y, w, col, right=True, seed=0):
    """板状珊瑚：从墙上长出来的一片薄盘（略俯视：看得到上面——一圈亮边、中间有生长纹；外沿起伏；
    盘底是暗色，再下面一条影子）。"""
    sg = 1 if right else -1
    xa, xb = sorted((x - sg * 3, x + sg * w))
    hi, md, dk, ink = (mix(col, (252, 248, 230), 0.4), col, mix(col, (30, 42, 44), 0.42),
                       mix(col, (14, 24, 28), 0.72))
    d.ellipse((xa, y - 3, xb, y + 2), fill=C(dk))
    d.ellipse((xa, y - 3, xb, y), fill=C(md))
    d.ellipse((xa + 2, y - 3, xb - 2, y - 2), fill=C(hi))
    for k in range(xa + 3, xb - 2, 3):                          # 生长纹
        d.point((k, y - 1 - (k // 3) % 2), fill=C(mix(col, (40, 50, 50), 0.18)))
    for k in range(xa + 1, xb):                                 # 外沿起伏：边上缺几个口、挂一点亮边
        if hash01(seed, k, 1) < 0.25:
            d.point((k, y + 1), fill=C(ink))
        elif hash01(seed, k, 2) < 0.2:
            d.point((k, y), fill=C(hi))
    d.line((xa + 2, y + 3, xb - 2, y + 3), fill=C(ink))


def sea_fan(d, x, y, r, col, seed, a0=-70, a1=70, lean=0.0):
    """海扇：从根往外放射的枝 + 横向的连枝（格子），深色根柄。"""
    dk = mix(col, (30, 30, 40), 0.35)
    hi = mix(col, (255, 230, 220), 0.3)
    n = 10
    tips = []
    for k in range(n):
        ang = math.radians(a0 + (a1 - a0) * k / (n - 1) + lean)
        L = r * hrange(0.75, 1.0, seed, k)
        pts = [(x, y)]
        for s in (0.35, 0.7, 1.0):
            pts.append((x + math.sin(ang) * L * s + hrange(-1, 1, seed, k, s), y - math.cos(ang) * L * s))
        for p, q in zip(pts, pts[1:]):
            d.line((round(p[0]), round(p[1]), round(q[0]), round(q[1])), fill=C(col))
        tips.append(pts)
    for s in (1, 2):
        for k in range(n - 1):
            if hash01(seed, k, s, 5) < 0.75:
                p, q = tips[k][s], tips[k + 1][s]
                d.line((round(p[0]), round(p[1]), round(q[0]), round(q[1])), fill=C(dk if s == 1 else col))
    for k in range(0, n, 2):
        p = tips[k][-1]
        d.point((round(p[0]), round(p[1])), fill=C(hi))
    d.line((x, y, x, y + 3), fill=C(dk))


def tube_sponges(d, x, base, hs, col, seed):
    """一丛管海绵：几根粗管（左亮右暗），管口是深色的洞 + 亮的口沿。"""
    hi, md, dk, ink = mix(col, (255, 245, 225), 0.3), col, mix(col, (30, 30, 40), 0.35), mix(col, (10, 16, 20), 0.7)
    for i, h in enumerate(hs):
        bx = x + i * 4 + int(hrange(-1, 1, seed, i))
        lean = hrange(-1.5, 1.5, seed, i, 2)
        for k in range(h):
            xx = round(bx + lean * k / h)
            yy = base - k
            d.line((xx, yy, xx + 2, yy), fill=C(md))
            d.point((xx, yy), fill=C(hi))
            d.point((xx + 2, yy), fill=C(dk))
        tx = round(bx + lean)
        ty = base - h
        d.line((tx, ty, tx + 2, ty), fill=C(hi))
        d.point((tx + 1, ty + 1), fill=C(ink))
        d.point((tx + 1, ty), fill=C(ink))


def urchin(d, x, y):
    """海胆：小小的深紫圆球 + 一圈短刺（上半圈）+ 一个亮点。"""
    body, spine, hi = (52, 36, 62), (84, 64, 98), (156, 136, 176)
    for ang in range(180, 361, 30):
        a = math.radians(ang)
        d.line((x, y - 1, round(x + math.cos(a) * 3.4), round(y - 1 + math.sin(a) * 2.8)), fill=C(spine))
    d.ellipse((x - 2, y - 2, x + 2, y + 1), fill=C(body))
    d.point((x - 1, y - 1), fill=C(hi))


def seagrass(d, x, y, n, hmax, seed, col=(92, 140, 66)):
    lt, dk = mix(col, (200, 220, 140), 0.35), mix(col, (30, 50, 30), 0.35)
    for i in range(n):
        bx = x + int(hrange(-n * 0.8, n * 0.8, seed, i))
        h = int(hrange(hmax * 0.4, hmax, seed, i, 2))
        lean = hrange(-0.5, 0.5, seed, i, 3)
        for k in range(h):
            d.point((round(bx + lean * k * k / max(1, h)), y - k), fill=C(lt if k > h * 0.6 else (col if i % 2 else dk)))


def brain_coral(a, x0, base, w, h, col, seed):
    """脑珊瑚：半球 + 弯弯曲曲的沟（深两级），按半球打光。"""
    bw, bh = w + 4, h + 3
    m, z = blob(bw, bh, [(bw / 2, bh - 1, w / 2, h)], seed, noise=0.08, cell=4, base=bh - 2)
    pal = [mix(col, (24, 36, 40), 0.6), mix(col, (24, 36, 40), 0.35), col, mix(col, (255, 248, 226), 0.3),
           mix(col, (255, 248, 226), 0.55)]
    rgba, q = shade(m, z, pal, seed, bump=0.2, facet=0, dither=0.4, speck=0.0)
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    nn = A._fbm(bw, bh, 3, seed + 4)
    g = np.sin(xx * 1.1 + nn * 7) * np.sin(yy * 1.3 + nn * 5 + xx * 0.3)
    groove = m & (np.abs(g) < 0.22) & (q > 0)
    P = np.array(pal, np.uint8)
    rgba[groove, :3] = P[np.clip(q[groove] - 2, 0, 4)]
    comp(a, rgba, int(x0), int(base - bh + 2))
    return m


def staghorn(d, x, y, h, pal, seed):
    """鹿角珊瑚：从根往上分叉（每段 2 px 宽，左亮右暗，枝尖亮）。"""
    def br(x, y, ang, L, depth, k):
        ex, ey = x + math.cos(ang) * L, y + math.sin(ang) * L
        d.line((round(x), round(y), round(ex), round(ey)), fill=C(pal[1]), width=2)
        d.line((round(x) - 1, round(y), round(ex) - 1, round(ey)), fill=C(pal[2]))
        if depth == 0:
            d.point((round(ex), round(ey) - 1), fill=C(pal[3]))
            d.point((round(ex) - 1, round(ey) - 1), fill=C(pal[3]))
            return
        for j, da in enumerate((-0.45, 0.45)):
            a2 = ang + da + hrange(-0.15, 0.15, seed, k, j)
            br(ex, ey, a2, L * hrange(0.62, 0.8, seed, k, j, 1), depth - 1, k * 2 + j + 1)
    br(x, y, -math.pi / 2 + hrange(-0.1, 0.1, seed), h * 0.38, 3, 1)
    d.point((x, y), fill=C(pal[0]))


def table_coral(d, x, base, w, yp, col, seed=0):
    """桌珊瑚：歪一点的粗柄 + 两层薄盘（上层大、下层小一点往右错开）；盘面看得到细密的珊瑚虫点和一圈浅色的生长边，
    盘底深色，盘沿起伏。"""
    hi, md, dk, ink = (mix(col, (255, 250, 230), 0.38), col, mix(col, (24, 36, 40), 0.4),
                       mix(col, (16, 26, 30), 0.72))
    cx = x + w // 2
    for k in range(base - yp - 2):                              # 柄：往下略粗、左亮右暗
        yy = base - k
        hw = 2 + (1 if k < 4 else 0)
        xx = cx + int(round(math.sin(k * 0.25) * 0.8))
        d.line((xx - hw, yy, xx + hw, yy), fill=C(dk))
        d.point((xx - hw, yy), fill=C(md))
    for (px, pw, py) in ((x + 6, w - 8, yp + 8), (x, w, yp)):    # 先画下层小盘，再画上层大盘
        d.ellipse((px, py - 3, px + pw, py + 3), fill=C(dk))
        d.ellipse((px, py - 3, px + pw, py + 1), fill=C(md))
        d.ellipse((px + 2, py - 3, px + pw - 2, py), fill=C(mix(col, (255, 250, 230), 0.15)))
        d.arc((px, py - 3, px + pw, py + 1), 180, 360, fill=C(hi))
        for k in range(px + 3, px + pw - 2, 2):                  # 珊瑚虫点
            d.point((k, py - 1 - (k // 2) % 2), fill=C(hi if hash01(seed, k, py) < 0.4 else md))
        for k in range(px + 1, px + pw):                         # 盘沿起伏
            if hash01(seed, k, py, 3) < 0.3:
                d.point((k, py + 2), fill=C(ink))
        d.line((px + 2, py + 3, px + pw - 2, py + 3), fill=C(ink))


def soft_coral(d, x, base, col, seed):
    """软珊瑚（皮革珊瑚）：短柄 + 起伏的伞盖。"""
    hi, md, dk = mix(col, (255, 250, 236), 0.35), col, mix(col, (30, 40, 44), 0.4)
    d.rectangle((x - 2, base - 6, x + 2, base), fill=C(dk))
    d.line((x - 2, base - 6, x - 2, base), fill=C(md))
    for k in range(-7, 8):
        hgt = 9 + int(2 * math.sin(k * 0.9 + seed))
        d.line((x + k, base - hgt, x + k, base - 6), fill=C(md))
        d.point((x + k, base - hgt), fill=C(hi))
        if k % 3 == 0:
            d.point((x + k, base - hgt + 2), fill=C(hi))
    d.line((x - 7, base - 6, x + 7, base - 6), fill=C(dk))


def starfish(d, x, y, col, rot=0.0, r=4):
    dk, hi = mix(col, (60, 20, 20), 0.4), mix(col, (255, 230, 200), 0.45)
    for k in range(5):
        a = rot + k * 2 * math.pi / 5 - math.pi / 2
        ex, ey = x + math.cos(a) * r, y + math.sin(a) * r * 0.55
        d.line((x, y, round(ex), round(ey)), fill=C(col))
        d.point((round(x + math.cos(a) * r * 0.5), round(y + math.sin(a) * r * 0.27) + 1), fill=C(dk))
    d.point((x, y), fill=C(hi))
    d.point((x - 1, y), fill=C(col))


def shell(d, x, y, kind, seed):
    if kind == 0:                                # 双壳（扇贝）
        c = [(236, 222, 204), (222, 176, 166), (240, 212, 150)][int(hash01(seed, 1) * 3)]
        d.line((x - 1, y, x + 1, y), fill=C(c))
        d.point((x, y - 1), fill=C(mix(c, (255, 255, 255), 0.4)))
        d.point((x, y + 1), fill=C(mix(c, (90, 80, 70), 0.4)))
    elif kind == 1:                              # 螺
        d.point((x, y), fill=C((226, 206, 170)))
        d.point((x + 1, y), fill=C((196, 160, 120)))
        d.point((x + 1, y - 1), fill=C((240, 226, 196)))
        d.point((x + 2, y), fill=C((150, 120, 90)))
    else:                                        # 沙钱
        d.ellipse((x - 2, y - 1, x + 2, y + 1), fill=C((226, 220, 196)))
        d.point((x, y), fill=C((180, 170, 146)))
        d.line((x - 1, y + 1, x + 1, y + 1), fill=C((196, 188, 160)))


def pebble(d, x, y, r, seed):
    c = [(126, 130, 118), (150, 148, 132), (110, 118, 112), (170, 164, 146)][int(hash01(seed, 1) * 4)]
    d.ellipse((x - r, y - r // 2 - 1, x + r, y + r // 2), fill=C(c))
    d.point((x - r + 1, y - r // 2), fill=C(mix(c, (255, 255, 240), 0.45)))
    d.line((x - r + 1, y + r // 2 + 1, x + r - 1, y + r // 2 + 1), fill=C(mix(c, (40, 50, 40), 0.5)))


def rubble(d, x, y, seed):
    c = (230, 226, 210)
    for k in range(3):
        a = hrange(0, 3.14, seed, k)
        d.line((x, y, round(x + math.cos(a) * 2), round(y + math.sin(a) * 1)), fill=C(c if k else (196, 190, 172)))


# ---------------------------------------------------------------- 旧锚 + 锚链、破木箱、砗磲
ANCHOR = dict(crown=(458, 148), tilt=-14.0, shank=50)
RUST = [(36, 30, 32), (70, 56, 50), (104, 78, 60), (140, 100, 70), (176, 126, 80)]


def _rot(cx, cy, ang):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def f(x, y):                                 # 局部坐标（x 右、y 上为负）→ 世界
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)
    return f


def anchor_parts():
    """旧锚（海军锚：环、锚杆、横杆、两只臂 + 锚爪）。crown 半埋在沙里，整体往左歪 14°。返回各部位的世界坐标。"""
    cx, cy = ANCHOR['crown']
    f = _rot(cx, cy, ANCHOR['tilt'])
    L = ANCHOR['shank']
    p = dict(f=f)
    p['shank'] = [f(-2, 0), f(2, 0), f(1.5, -L), f(-1.5, -L)]
    p['ring_c'] = f(0, -L - 4)
    p['stock'] = [f(-13, -L + 6), f(13, -L + 6), f(13, -L + 9), f(-13, -L + 9)]
    p['stock_ends'] = [f(-14, -L + 7.5), f(14, -L + 7.5)]
    arm = []
    for s in range(-1, 2, 2):
        pts = []
        for k in range(0, 11):
            a = math.radians(k * 9)
            pts.append(f(s * 16 * math.sin(a), -16 * (1 - math.cos(a)) * 0.9 - 1))
        arm.append(pts)
    p['arms'] = arm
    p['flukes'] = []
    for s, pts in zip((-1, 1), arm):
        p['flukes'].append([pts[-3], f(s * 20, -14), f(s * 13, -21)])
    return p


def draw_anchor(d):
    p = anchor_parts()
    f = p['f']
    o, dk, md, lt, hl = [C(c) for c in RUST]
    for pts in p['arms']:                                   # 臂（3 px 粗）
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            d.line((round(xa), round(ya), round(xb), round(yb)), fill=o, width=4)
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            d.line((round(xa), round(ya), round(xb), round(yb)), fill=md, width=2)
            d.point((round(xa), round(ya) - 1), fill=lt)
    for fl in p['flukes']:
        d.polygon([(round(x), round(y)) for x, y in fl], fill=md, outline=o)
        d.line((round(fl[0][0]), round(fl[0][1]), round(fl[2][0]), round(fl[2][1])), fill=lt)
    d.polygon([(round(x), round(y)) for x, y in p['shank']], fill=md, outline=o)    # 锚杆
    a0, a1 = f(-1, -2), f(-1, -ANCHOR['shank'] + 1)
    d.line((round(a0[0]), round(a0[1]), round(a1[0]), round(a1[1])), fill=lt)
    b0, b1 = f(1, -2), f(1, -ANCHOR['shank'] + 1)
    d.line((round(b0[0]), round(b0[1]), round(b1[0]), round(b1[1])), fill=dk)
    d.polygon([(round(x), round(y)) for x, y in p['stock']], fill=md, outline=o)    # 横杆
    s0, s1 = f(-12, -ANCHOR['shank'] + 7), f(12, -ANCHOR['shank'] + 7)
    d.line((round(s0[0]), round(s0[1]), round(s1[0]), round(s1[1])), fill=lt)
    for (ex, ey) in p['stock_ends']:
        d.ellipse((round(ex) - 2, round(ey) - 2, round(ex) + 2, round(ey) + 2), fill=md, outline=o)
        d.point((round(ex) - 1, round(ey) - 1), fill=hl)
    rx, ry = p['ring_c']                                    # 环
    d.ellipse((round(rx) - 4, round(ry) - 4, round(rx) + 4, round(ry) + 4), outline=o, width=3)
    d.ellipse((round(rx) - 4, round(ry) - 4, round(rx) + 4, round(ry) + 4), outline=md, width=1)
    d.arc((round(rx) - 4, round(ry) - 4, round(rx) + 4, round(ry) + 4), 180, 270, fill=lt)
    # 锈斑、藤壶、挂着的海草
    for k in range(18):
        s = hrange(4, ANCHOR['shank'] - 4, k, 801)
        x, y = f(hrange(-1, 1, k, 802), -s)
        d.point((round(x), round(y)), fill=C(RUST[4] if k % 3 else (120, 140, 90)))
    for k, s in enumerate((10, 13, 30, 33, 35)):
        x, y = f(1.5, -s)
        barnacle(d, round(x) + 1, round(y), k % 2 == 0)
    x, y = f(-10, -ANCHOR['shank'] + 9)
    for k in range(9):
        d.point((round(x + math.sin(k * 0.8) * 1.2), round(y + k)), fill=C(TURF[2] if k % 3 else TURF[1]))
    cx, cy = ANCHOR['crown']                                # 锚冠半埋：盖一个沙堆（底在 y 148，不进可走带）
    sc = sand_col(cy - 3)
    mound = [(cx - 15, cy), (cx - 9, cy - 2), (cx - 4, cy - 3), (cx + 3, cy - 4), (cx + 8, cy - 3), (cx + 13, cy - 1),
             (cx + 17, cy)]
    d.polygon(mound, fill=C(sc))
    d.line(mound[1:-1], fill=C(mix(sc, SAND_RAMP[6], 0.55)))
    d.line((cx - 13, cy, cx + 15, cy), fill=C(mix(sc, SAND_RAMP[1], 0.35)))
    for k in range(-10, 12, 4):
        d.point((cx + k, cy - 2 - (k // 4) % 2), fill=C(mix(sc, SAND_RAMP[1], 0.3)))
    return p


CHAIN_PATH = [(-1, 0), (430, 118), (424, 132), (421, 146), (425, 152), (438, 158), (458, 162), (482, 166), (504, 169),
              (520, 171)]


def chain_points():
    rx, ry = anchor_parts()['ring_c']
    pts = [(rx - 2, ry + 3)] + CHAIN_PATH[1:]
    out = []
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(xb - xa, yb - ya) / 3))
        for k in range(n):
            u = k / n
            out.append((xa + (xb - xa) * u, ya + (yb - ya) * u))
    out.append(pts[-1])
    return out


def draw_chain(d, flat, y_split=147):
    """锚链：正面的环（中间空）和侧面的环（一条横杠）交替；flat=True 只画躺在沙上的那段（y ≥ y_split），否则只画挂着的那段。"""
    o, dk, md, lt = C((40, 34, 32)), C((86, 66, 54)), C((120, 90, 66)), C((168, 124, 84))
    pts = chain_points()
    for i, (x, y) in enumerate(pts):
        if (y >= y_split) != flat:
            continue
        xi, yi = int(round(x)), int(round(y))
        if i % 2 == 0:
            d.rectangle((xi - 2, yi - 1, xi + 1, yi + 1), fill=md, outline=o)
            d.point((xi - 1, yi), fill=o)
            d.point((xi, yi), fill=dk)
            d.point((xi - 1, yi - 1), fill=lt)
        else:
            d.line((xi - 2, yi, xi + 1, yi), fill=md)
            d.point((xi - 2, yi), fill=lt)
            d.point((xi - 1, yi + 1), fill=o)
            d.point((xi, yi + 1), fill=o)
    if flat:                                                # 链尾埋进沙里：一小撮沙堆
        x, y = CHAIN_PATH[-1]
        d.ellipse((x - 3, y - 1, x + 4, y + 2), fill=C(sand_col(y)))
        d.line((x - 2, y - 1, x + 3, y - 1), fill=C(mix(sand_col(y), SAND_HI, 0.5)))


CRATE = (116, 146)          # 左下角 x、底 y（底下 4 px 埋在沙里）
WOOD = [(48, 38, 34), (82, 66, 52), (112, 92, 70), (144, 122, 92), (178, 156, 120)]


def draw_crate(d):
    """破木箱（3/4 视角）：正面四块横板、两头竖撑、生锈的角铁；顶面塌了一块，正面破了个洞，露出里面的玻璃瓶；
    长了藻、粘着藤壶。底下几 px 埋在沙里。"""
    x0, by = CRATE
    w, h, dep = 30, 18, 6
    o, dk, md, lt, hl = [C(c) for c in WOOD]
    top_y = by - h
    # 顶面（往右上斜）
    d.polygon([(x0, top_y), (x0 + w, top_y), (x0 + w + dep, top_y - dep // 2 - 1), (x0 + dep, top_y - dep // 2 - 1)],
              fill=lt, outline=o)
    for k in range(1, 3):
        yk = top_y - k * 2
        d.line((x0 + k * 2, yk, x0 + w + k * 2, yk), fill=md)
    d.polygon([(x0 + 12, top_y), (x0 + 22, top_y), (x0 + 25, top_y - 3), (x0 + 15, top_y - 3)], fill=C((26, 22, 24)))  # 顶上塌的洞
    # 侧面（右）
    d.polygon([(x0 + w, top_y), (x0 + w + dep, top_y - dep // 2 - 1), (x0 + w + dep, by - dep // 2 - 1), (x0 + w, by)],
              fill=dk, outline=o)
    for k in range(1, 4):
        yk = top_y + k * 4 + 1
        d.line((x0 + w + 1, yk, x0 + w + dep - 1, yk - dep // 2), fill=o)
    # 正面：四块横板
    d.rectangle((x0, top_y, x0 + w, by), fill=md, outline=o)
    for k in range(4):
        yk = top_y + 1 + k * 4
        d.line((x0 + 1, yk, x0 + w - 1, yk), fill=lt)
        d.line((x0 + 1, yk + 3, x0 + w - 1, yk + 3), fill=o)
        for q in range(3):                                     # 木纹
            gx = x0 + 4 + int(hrange(0, w - 8, k, q, 811))
            d.line((gx, yk + 1, gx + 3, yk + 1), fill=dk)
    d.rectangle((x0, top_y, x0 + 3, by), fill=lt, outline=o)                         # 两头竖撑
    d.rectangle((x0 + w - 3, top_y, x0 + w, by), fill=md, outline=o)
    d.line((x0 + 1, top_y + 1, x0 + 1, by - 1), fill=hl)
    for (ax, ay) in ((x0, top_y), (x0 + w - 3, top_y)):                              # 生锈的角铁
        d.rectangle((ax, ay, ax + 3, ay + 3), fill=C(RUST[3]), outline=C(RUST[0]))
        d.point((ax + 1, ay + 1), fill=C(RUST[4]))
    # 正面破洞（锯齿边）+ 里面的瓶子
    hole = [(x0 + 9, top_y + 5), (x0 + 13, top_y + 3), (x0 + 16, top_y + 6), (x0 + 20, top_y + 4), (x0 + 22, top_y + 9),
            (x0 + 19, top_y + 12), (x0 + 14, top_y + 11), (x0 + 10, top_y + 12)]
    d.polygon(hole, fill=C((22, 20, 24)), outline=C(WOOD[0]))
    for (bx, bc) in ((x0 + 13, (60, 140, 90)), (x0 + 17, (120, 90, 50))):
        d.rectangle((bx, top_y + 7, bx + 2, top_y + 11), fill=C(bc))
        d.line((bx + 1, top_y + 5, bx + 1, top_y + 6), fill=C(bc))
        d.point((bx, top_y + 8), fill=C(mix(bc, (255, 255, 255), 0.5)))
    for (sx, sy) in ((x0 + 9, top_y + 5), (x0 + 20, top_y + 4)):                     # 断板的木刺
        d.point((sx, sy - 1), fill=lt)
    # 藻、藤壶
    for k in range(x0 + dep, x0 + w + dep):                    # 顶面后沿长的短藻
        if hash01(k, 812) < 0.45:
            d.point((k, top_y - dep // 2 - 2), fill=C(TURF[2]))
            if hash01(k, 813) < 0.4:
                d.point((k, top_y - dep // 2 - 3), fill=C(TURF[3]))
    for k, (bx, byy) in enumerate(((x0 + 4, by - 5), (x0 + 6, by - 3), (x0 + 26, by - 6), (x0 + 24, by - 2),
                                   (x0 + 28, by - 3))):
        barnacle(d, bx, byy, k % 2 == 0)
    # 半埋：底下的沙堆盖住
    sc = sand_col(by)
    d.polygon([(x0 - 4, by + 2), (x0 + 2, by - 3), (x0 + 12, by - 2), (x0 + 24, by - 4), (x0 + w + dep + 2, by - 6),
               (x0 + w + dep + 6, by + 2)], fill=C(sc))
    d.line((x0 + 2, by - 3, x0 + 12, by - 2), fill=C(mix(sc, SAND_HI, 0.5)))
    d.line((x0 + 12, by - 2, x0 + 24, by - 4), fill=C(mix(sc, SAND_HI, 0.5)))


CLAM = (552, 147)


def draw_clam(d):
    """砗磲（侧面）：碗形的厚壳半埋在沙里，壳上 5 道放射状的粗棱、顶上是一排圆鼓鼓的扇形口沿；
    口沿上面翻出绿色带金斑的外套膜，中间一个出水孔。"""
    x0, by = CLAM
    w = 22
    o, dk, md, lt, hl = (66, 62, 54), (138, 132, 110), (186, 180, 154), (220, 214, 190), (244, 240, 222)
    cx = x0 + w / 2
    body = [(x0, by - 7), (x0 + 1, by - 3), (x0 + 4, by), (x0 + w - 4, by), (x0 + w - 1, by - 3), (x0 + w, by - 7)]
    d.polygon(body, fill=C(md))
    nrib = 5
    for i in range(nrib):                                       # 放射状的棱：每道左亮右暗，顶上鼓成一个扇形
        tx = x0 + 2 + (w - 4) * (i + 0.5) / nrib
        d.line((round(cx + (tx - cx) * 0.4), by + 1, round(tx) - 1, by - 7), fill=C(lt))
        d.line((round(cx + (tx - cx) * 0.4) + 2, by + 1, round(tx) + 2, by - 7), fill=C(dk))
        d.chord((round(tx) - 3, by - 10, round(tx) + 2, by - 5), 180, 360, fill=C(lt))
        d.arc((round(tx) - 3, by - 10, round(tx) + 2, by - 5), 200, 300, fill=C(hl))
        d.point((round(tx) + 2, by - 7), fill=C(o))
    mantle = [(64, 164, 126), (104, 200, 156), (40, 112, 92)]  # 外套膜：在扇形口沿上面翻出来
    for k in range(x0 + 2, x0 + w - 1):
        hgt = 2 + int(1.2 * (1 + math.sin(k * 1.3)))
        d.line((k, by - 10 - hgt, k, by - 10), fill=C(mantle[0]))
        d.point((k, by - 10 - hgt), fill=C(mantle[1]))
        if (k * 7) % 5 == 0:
            d.point((k, by - 11), fill=C((232, 206, 96)))
    d.line((x0 + 2, by - 9, x0 + w - 2, by - 9), fill=C(mantle[2]))
    d.ellipse((round(cx) - 2, by - 14, round(cx) + 1, by - 11), fill=C((22, 50, 44)))   # 出水孔
    d.point((round(cx) - 2, by - 14), fill=C(mantle[1]))
    d.line(body[:3], fill=C(o))
    d.line(body[3:], fill=C(o))
    d.line((x0 + 4, by, x0 + w - 4, by), fill=C(o))


# ---------------------------------------------------------------- 石头
def rock(dst, x0, base, w, h, seed, pal=ROCK, d=0.08, barn=(), extra=(), pink=0.07, green=0.09, fcell=8):
    """一块近景石头（底在 base 行）。extra = 额外的球（相对左下角）；barn = 藤壶簇中心（相对左下角）。返回 (遮罩, 左上角)。"""
    bw, bh = w + 10, h + 8
    ox, oy = int(x0 - 5), int(base - bh + 3)
    balls = [(bw / 2, bh - 3, w / 2, h)]
    for i in range(3):
        balls.append((bw / 2 + hrange(-w * 0.3, w * 0.3, seed, i, 1), bh - 3 - h * hrange(0.15, 0.5, seed, i, 2),
                      w * hrange(0.18, 0.32, seed, i, 3), h * hrange(0.35, 0.6, seed, i, 4)))
    for (ex, ey, rx, ry) in extra:
        balls.append((ex + 5, bh - 3 - ey, rx, ry))
    m, z = blob(bw, bh, balls, seed, noise=0.12, cell=6, base=bh - 3)
    rgba, q = shade(m, z, pal, seed, facet=0.16, fcell=fcell, lo=0.12, hi=1.0)
    encrust(rgba, q, m, seed, pink=pink, green=green, n=len(pal))

    def deco(dd, im):
        for i, (bx, by) in enumerate(barn):
            barnacles(dd, cluster_pts(m, bx + 5, bh - 3 - by, 9, seed + i, 4), seed + i)
        top = m & ~shift(m, -1, 0)
        rng = np.random.default_rng(seed + 5)
        for y, x in zip(*np.nonzero(top)):
            if rng.random() < 0.18:
                dd.point((x, y - 1), fill=C(TURF[2]))
                if rng.random() < 0.5:
                    dd.point((x, y - 2), fill=C(TURF[3]))
    draw_on(rgba, deco)
    if d:
        haze_arr(rgba, d, oy)
    comp(dst, rgba, ox, oy)
    out = np.zeros(dst.shape[:2], bool)
    ys, xs = np.nonzero(m)
    ok = (ys + oy >= 0) & (ys + oy < H) & (xs + ox >= 0) & (xs + ox < PW)
    out[ys[ok] + oy, xs[ok] + ox] = True
    return out


# ---------------------------------------------------------------- 组装
LEFT_WALL = [(0, 60), (8, 56), (16, 46), (24, 36), (36, 31), (48, 36), (60, 44), (66, 50), (70, 47), (84, 40),
             (100, 42), (112, 49), (122, 54), (132, 58), (140, 63), (146, 66)]
RIGHT_WALL = [(0, 598), (10, 606), (22, 600), (36, 590), (50, 593), (64, 602), (78, 598), (94, 588), (108, 584),
              (122, 586), (134, 580), (142, 576), (146, 574)]
EEL = (603, 112)


@lru_cache(maxsize=1)
def bed_parts():
    """近景海床的几块：sand（不透明沙地 + 平的小东西）、obj（后沿的石头 / 珊瑚 / 箱子 / 锚，底都在 y ≤ 148）、
    wall（两头礁石墙）。"""
    sand, top = sand_layer()
    obj = np.zeros((H, PW, 4), np.uint8)
    wall = np.zeros((H, PW, 4), np.uint8)
    # ---- 墙
    for prof, left, seed in ((LEFT_WALL, True, 851), (RIGHT_WALL, False, 852)):
        m, edge = wall_mask(prof, left, seed)
        rgba, q = wall_shade(m, left, seed)
        comp(wall, rgba)

    def wall_deco(d, im):
        # 左墙：岩缝、板状珊瑚、海扇、管海绵、藤壶
        crack(d, [(10, 30), (18, 33), (24, 40)], (24, 40, 46), (96, 118, 108))
        crack(d, [(4, 96), (14, 99), (22, 98), (30, 104)], (24, 40, 46), (96, 118, 108))
        d.ellipse((14, 116, 26, 124), fill=C((16, 32, 38)))                      # 墙缝（冒气泡的那个）
        d.arc((14, 116, 26, 124), 20, 160, fill=C((110, 134, 118)))
        plate_coral(d, 44, 66, 14, (196, 176, 120), seed=1)
        plate_coral(d, 50, 112, 12, (176, 160, 116), seed=2)
        plate_coral(d, 30, 24, 18, (190, 168, 114), seed=3)
        sea_fan(d, 46, 86, 13, (204, 84, 80), 31, a0=-10, a1=110)
        tube_sponges(d, 48, 132, (9, 13, 7), (170, 96, 176), 32)
        tube_sponges(d, 22, 64, (7, 10), (226, 184, 70), 33)
        for i, (bx, by) in enumerate(((30, 136), (54, 140), (12, 128), (40, 92), (20, 52))):
            barnacles(d, cluster_pts(wm, bx, by, 9, 860 + i, 4), 860 + i)
        # 右墙：洞里的海鳝、板状珊瑚、海扇、海绵、藤壶
        ex, ey = EEL
        d.ellipse((ex - 4, ey - 5, ex + 8, ey + 4), fill=C((14, 28, 34)))
        d.arc((ex - 4, ey - 5, ex + 8, ey + 4), 30, 150, fill=C((116, 140, 120)))
        eel = [(146, 140, 64), (98, 96, 44), (196, 188, 100), (30, 28, 20)]
        d.polygon([(ex + 4, ey - 3), (ex - 3, ey - 4), (ex - 7, ey - 2), (ex - 7, ey + 1), (ex - 3, ey + 2), (ex + 4, ey + 2)],
                  fill=C(eel[0]), outline=C(eel[3]))
        d.line((ex - 6, ey - 2, ex - 1, ey - 3), fill=C(eel[2]))
        d.line((ex - 7, ey, ex - 3, ey), fill=C((90, 30, 36)))                    # 张着的嘴
        d.point((ex - 4, ey - 2), fill=C((250, 250, 220)))
        d.point((ex - 4, ey - 1), fill=C((10, 10, 10)))
        for k in range(4):
            d.point((ex - 1 + k * 2, ey + (k % 2) - 1), fill=C(eel[1]))
        plate_coral(d, 592, 52, 14, (200, 180, 126), right=False, seed=4)
        plate_coral(d, 586, 92, 16, (184, 166, 118), right=False, seed=5)
        sea_fan(d, 592, 128, 14, (176, 86, 156), 41, a0=-110, a1=10)
        tube_sponges(d, 600, 70, (8, 11, 6), (234, 140, 70), 42)
        for i, (bx, by) in enumerate(((590, 138), (606, 142), (616, 100), (598, 30))):
            barnacles(d, cluster_pts(wm, bx, by, 9, 870 + i, 4), 870 + i)
    wm = wall[..., 3] > 0
    draw_on(wall, wall_deco)
    # ---- 后沿的石头
    rock(obj, 172, 145, 26, 14, 811, barn=((6, 4), (20, 6)))
    rock(obj, 232, 146, 62, 40, 812, barn=((8, 6), (24, 4), (44, 10), (54, 4), (34, 20)), fcell=10,
         extra=((14, 18, 12, 16), (48, 22, 14, 14)))
    rock(obj, 338, 146, 22, 10, 813, barn=((10, 3),))
    rock(obj, 356, 147, 14, 7, 814)
    rock(obj, 486, 146, 14, 9, 815)
    for (cx, y, rx) in ((185, 146, 16), (263, 147, 34), (349, 147, 14), (363, 148, 9), (493, 147, 10),
                        (134, 147, 24), (460, 148, 18), (518, 147, 18), (561, 148, 13), (84, 145, 18)):
        contact_shadow(sand, cx, y, rx)
    brain_coral(obj, 72, 144, 18, 11, (146, 172, 98), 821)
    brain_coral(obj, 524, 145, 16, 10, (196, 150, 170), 822)

    def obj_deco(d, im):
        staghorn(d, 98, 144, 22, [(110, 56, 90), (176, 98, 140), (206, 130, 168), (240, 184, 206)], 823)
        staghorn(d, 90, 144, 15, [(120, 90, 50), (200, 156, 84), (226, 190, 110), (250, 226, 160)], 824)
        tube_sponges(d, 104, 143, (8, 11, 6), (226, 188, 72), 825)
        table_coral(d, 498, 146, 26, 124, (172, 164, 104), 833)
        soft_coral(d, 546, 146, (222, 210, 172), 826)
        sea_fan(d, 262, 108, 14, (176, 70, 146), 827)
        sea_fan(d, 248, 112, 9, (214, 120, 70), 828, a0=-80, a1=40)
        urchin(d, 206, 147)
        urchin(d, 215, 148)
        urchin(d, 299, 147)
        seagrass(d, 386, 147, 9, 8, 829)
        seagrass(d, 410, 146, 6, 6, 830)
        seagrass(d, 150, 146, 5, 6, 831)
        seagrass(d, 476, 147, 5, 5, 832)
        draw_anchor(d)
        draw_chain(d, flat=False)
        draw_crate(d)
        draw_clam(d)
    draw_on(obj, obj_deco)
    haze_arr(obj, 0.0)
    # ---- 沙上平的东西（可走带里只放这些）
    flat = np.zeros((H, PW, 4), np.uint8)

    def flat_deco(d, im):
        rng = np.random.default_rng(840)
        for i in range(70):
            x = int(rng.integers(10, PW - 10))
            y = int(rng.integers(149, 179))
            k = rng.random()
            if k < 0.45:
                shell(d, x, y, 0 if k < 0.25 else 1, i)
            elif k < 0.75:
                pebble(d, x, y, 1 + int(rng.random() * 2), i)
            elif k < 0.9:
                rubble(d, x, y, i)
            else:
                shell(d, x, y, 2, i)
        for (x, y, col, rot) in ((214, 165, (226, 100, 66), 0.3), (372, 174, (232, 140, 60), 1.1),
                                 (122, 171, (208, 82, 92), 0.7), (590, 162, (226, 100, 66), 2.0)):
            starfish(d, x, y, col, rot)
        for (x, y) in ((60, 160), (282, 176), (530, 176), (412, 156)):          # 短海草丛（贴地）
            seagrass(d, x, y, 4, 3, x)
        draw_chain(d, flat=True)
        # 半埋的绿玻璃瓶
        bx, by = 162, 168
        d.rectangle((bx, by - 1, bx + 6, by + 1), fill=C((70, 140, 96)))
        d.line((bx + 7, by, bx + 9, by), fill=C((70, 140, 96)))
        d.line((bx + 1, by - 1, bx + 5, by - 1), fill=C((170, 230, 190)))
        d.line((bx - 1, by + 1, bx + 2, by + 2), fill=C(sand_col(by)))
    draw_on(flat, flat_deco)
    return sand, flat, obj, wall, top


@lru_cache(maxsize=1)
def bed_img():
    sand, flat, obj, wall, top = bed_parts()
    a = sand.copy()
    comp(a, flat)
    comp(a, obj)
    comp(a, wall)
    return img(a)


# ============================================================ 焦散（wrap ×2）
def caustic_img(seed, cell=13):
    """周期 160 的 Worley 光网（F2 − F1 小 = 亮线），按透视往远处压扁、变淡；只有 y ≥ CAUS_Y 的行。"""
    rows = H - CAUS_Y
    gx = CAUS_P // cell
    gh = 14
    rng = np.random.default_rng(seed)
    pts = []
    for j in range(gh):
        for i in range(gx):
            pts.append(((i + rng.random()) * cell, (j + rng.random()) * cell * 0.7))
    pts = np.array(pts, np.float32)
    allp = np.concatenate([pts + [dx, 0] for dx in (-CAUS_P, 0, CAUS_P)])
    tree = cKDTree(allp)
    ys = np.arange(rows, dtype=np.float32)
    v = (ys / (rows - 1))
    gyy = np.cumsum(3.0 - 1.6 * v) + 4                   # 越往上（越远）屏幕上一行代表的地面越多 → 光网压扁
    X, Y = np.meshgrid(np.arange(CAUS_P, dtype=np.float32), gyy)
    dd, _ = tree.query(np.c_[X.ravel(), Y.ravel()], k=2)
    f = (dd[:, 1] - dd[:, 0]).reshape(rows, CAUS_P)
    thr = 1.6 + 1.2 * v[:, None]                         # 近处的光线粗一点
    lit = np.clip(1 - f / thr, 0, 1) ** 1.1
    fade = np.clip(ys / 6.0, 0, 1)[:, None] * (0.5 + 0.5 * v[:, None])
    alpha = lit * fade * 118
    q = np.floor(alpha / 14 + bayer(CAUS_P, rows)) * 14
    a = np.zeros((rows, CAUS_P, 4), np.uint8)
    a[..., :3] = (236, 255, 236)
    a[..., 3] = np.clip(q, 0, 255).astype(np.uint8)
    return img(a)


# ============================================================ 海葵 + 小丑鱼、气泡（strip）
ANEMONES = [(186, 133, 7, (226, 120, 150), True), (276, 109, 6, (170, 210, 110), False),
            (40, 128, 5, (236, 170, 90), False)]


def anemone_box(i):
    x, y, r, col, fish = ANEMONES[i]
    return (x - r - (12 if fish else 4), y - r - (10 if fish else 3), x + r + (12 if fish else 4), y + 4)


def anemone_frame(i, t):
    x, y, r, col, fish = ANEMONES[i]
    bx0, by0, bx1, by1 = anemone_box(i)
    im = Image.new('RGBA', (bx1, by1), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    t = t % LOOP
    tau = math.pi * t
    dk, hi = mix(col, (40, 30, 40), 0.35), mix(col, (255, 250, 236), 0.4)
    d.rectangle((x - 2, y - 1, x + 2, y + 2), fill=C(dk))
    d.line((x - 2, y - 1, x + 2, y - 1), fill=C(col))
    nt = 9 + r
    for k in range(nt):
        u = (k + 0.5) / nt
        a0 = math.radians(-160 + 140 * u)
        L = r * (0.8 + 0.3 * math.sin(k * 1.7))
        pts = []
        for s in range(0, 5):
            ss = s / 4.0
            sw = math.sin(tau + k * 0.5 - ss * 2.0) * 0.45 * ss
            a = a0 + sw
            pts.append((x + math.cos(a) * L * ss, y - 1 + math.sin(a) * L * ss))
        for p, q in zip(pts, pts[1:]):
            d.line((round(p[0]), round(p[1]), round(q[0]), round(q[1])), fill=C(col if k % 2 else mix(col, hi, 0.4)))
        d.point((round(pts[-1][0]), round(pts[-1][1])), fill=C(hi))
    if fish:                                                    # 两条小丑鱼绕着海葵游（2 s 一圈）
        for j in range(2):
            ang = tau + j * math.pi
            fx = x + math.cos(ang) * (r + 6)
            fy = y - r * 0.6 + math.sin(ang) * 3
            right = math.sin(ang) < 0
            fx_, fy_ = int(round(fx)), int(round(fy))
            body = [(fx_ - 2, fy_), (fx_ + 2, fy_)]
            d.line(body, fill=C((240, 120, 40)))
            d.line((fx_ - 1, fy_ - 1, fx_ + 1, fy_ - 1), fill=C((246, 150, 60)))
            d.point((fx_, fy_), fill=C((250, 250, 250)))
            d.point((fx_, fy_ - 1), fill=C((250, 250, 250)))
            tail = fx_ - 3 if right else fx_ + 3
            d.point((tail, fy_), fill=C((220, 100, 30)))
            d.point((fx_ + 2 if right else fx_ - 2, fy_ - 1), fill=C((20, 20, 20)))
    a = arr(im)
    haze_arr(a, 0.06)
    return img(a)


BUBBLE_SRC = [(561, 137, 26), (20, 117, 22)]


def bubble_box(i):
    x, y, rise = BUBBLE_SRC[i]
    return (x - 4, y - rise - 2, x + 5, y + 1)


def bubble_frame(i, t):
    """零星小气泡：3 颗 1 px 的泡，错开相位往上升 rise px（左右晃 1 px），升到顶就没了，2 s 一轮。"""
    t = t % LOOP
    x, y, rise = BUBBLE_SRC[i]
    bx0, by0, bx1, by1 = bubble_box(i)
    im = Image.new('RGBA', (bx1, by1), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for j in range(3):
        u = ((t / LOOP) + j / 3.0) % 1.0
        yy = y - u * rise
        xx = x + math.sin(u * 6.28 * 2 + j) * 1.2
        c = (214, 246, 236, 220) if u < 0.8 else (214, 246, 236, 120)
        d.point((int(round(xx)), int(round(yy))), fill=c)
        if j == 0 and u > 0.35:
            d.point((int(round(xx)) + 1, int(round(yy))), fill=(180, 230, 220, 140))
    return im


# ============================================================ 船底（pano k .5）
HULL_X0, HULL_W = 330, 92            # 层坐标（k .5）：镜头 0 时在屏幕 x 330 以外，第3章 320 宽看不到


@lru_cache(maxsize=1)
def hull_img():
    """游艇的船底（从水下往上看，逆光）：船身下沿一条弧线（船尾平、船头翘），中间吊着鳍龙骨 + 底下的压载球，
    船尾一片舵、一个小螺旋桨；吃水线下一道白色水线条、一道暗红的防污漆；剪影的下沿透一圈亮边；
    船底下面一片淡淡的影子；吃水线上一串白色的小泡沫。"""
    w, h = HULL_W + 4, 76
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body, dk, rim, red, boot = (30, 64, 72), (20, 44, 52), (104, 182, 178), (92, 60, 66), (176, 214, 208)
    prof = [(0, 9), (7, 14), (22, 18), (42, 19), (60, 17), (74, 12), (85, 6), (92, 2)]
    xs = np.arange(0, HULL_W + 1)
    yb = np.interp(xs, [p[0] for p in prof], [p[1] for p in prof])
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))                   # 船底的影子（抖动的半透明暗色）
    sa = np.zeros((h, w), np.float32)
    for x in range(w):
        for y in range(14, h):
            u = (y - 14) / (h - 14)
            c0, c1 = 6 + 14 * u, 88 - 4 * u
            if c0 <= x <= c1:
                edge = min(x - c0, c1 - x) / 6.0
                sa[y, x] = 46 * (1 - u) ** 1.5 * min(1.0, edge)
    q = np.floor(sa / 10 + bayer(w, h)) * 10
    s = np.zeros((h, w, 4), np.uint8)
    s[..., :3] = (24, 70, 80)
    s[..., 3] = np.clip(q, 0, 255).astype(np.uint8)
    sh = img(s)
    hull = [(0, 2)] + [(int(x), int(round(y))) for x, y in zip(xs, yb)] + [(HULL_W, 2)]
    d.polygon(hull, fill=C(body))
    d.polygon([(38, 18), (54, 18), (51, 31), (44, 31)], fill=C(dk))          # 鳍龙骨（后掠）
    d.ellipse((39, 29, 57, 34), fill=C(dk))                                   # 压载球
    d.line((41, 34, 55, 34), fill=C(rim))
    d.line((39, 31, 44, 31), fill=C(rim))
    d.line((38, 18, 43, 30), fill=C(rim))
    d.polygon([(9, 13), (15, 14), (14, 26), (10, 25)], fill=C(dk))           # 舵
    d.line((10, 25, 14, 26), fill=C(rim))
    d.line((24, 17, 24, 21), fill=C(dk))                                      # 螺旋桨
    d.line((22, 21, 26, 23), fill=C(dk))
    d.line((26, 20, 22, 23), fill=C(dk))
    d.point((24, 22), fill=C(rim))
    for x in range(1, HULL_W):                                                # 下沿亮边、水线条、防污漆
        y = int(round(yb[x]))
        d.point((x, y), fill=C(rim))
        d.point((x, 3), fill=C(boot))
        if y > 6:
            d.point((x, 5), fill=C(red))
            d.point((x, 6), fill=C(mix(red, body, 0.5)))
    for x in range(-2, HULL_W + 4, 3):                                        # 吃水线的小泡沫
        if hash01(x, 931) < 0.6:
            d.point((x, 2 + (x // 3) % 2), fill=(236, 252, 246, 220))
    ha = arr(im)
    haze_arr(ha, 0.18)                                                        # 隔着一层水，不是死黑
    out = sh
    out.alpha_composite(img(ha))
    a = arr(out)
    a[:2, :, 3] = 0
    return img(a)


# ============================================================ 导出
def _png_bytes(im):
    bio = io.BytesIO()
    im.save(bio, 'PNG', optimize=True)
    return len(bio.getvalue())


def export(ex, BJ):
    strips = []

    def bake(name, box, n, fps, fn, k):
        L = ex.bake(name, box, n, fps, fn, screen=False, k=k)
        strips.append((name, box, n, fps, fn, k))
        return L
    layers = [dict(type='static', image=ex.img('water', water_img())),
              dict(type='pano', image=ex.img('far', far_img()), k=FAR_K, x=0, y=0),
              dict(type='pano', image=ex.img('mid', mid_img()), k=MID_K, x=0, y=0)]
    for i in range(len(RAYS)):
        layers.append(bake('ray%d' % i, ray_box(i), RAY_N, RAY_FPS, lambda t, i=i: ray_frame(i, t), RAY_K))
    Ls = bake('surface', (0, 0, SURF_TILE, SURF_H), SURF_N, SURF_FPS, surface_frame, SURF_K)
    for x in range(0, SURFW, SURF_TILE):
        layers.append(dict(Ls, x=x))
    hi_ = hull_img()
    layers.append(dict(type='pano', image=ex.img('hull', hi_), k=SURF_K, x=HULL_X0, y=0))
    layers.append(dict(type='wrap', image=ex.img('fish', fish_img()), period=PW, k=FISH_K, y=FISH_Y0, vx=6.0))
    tang, bfly = fish_sprite('tang'), fish_sprite('bfly')
    layers.append(dict(type='clouds', span=760, clouds=[
        dict(image=ex.img('fish_tang', img(haze_arr(arr(tang), 0.12, 96))), x0=40.0, y=96, vx=-7.0, k=0.85),
        dict(image=ex.img('fish_bfly', img(haze_arr(arr(bfly), 0.15, 70))), x0=520.0, y=70, vx=5.0, k=0.75)]))
    for gi in range(len(KELP_GROUPS)):
        layers.append(bake('kelp%d' % gi, kelp_box(gi), SWAY_N, SWAY_FPS, lambda t, gi=gi: kelp_frame(gi, t), 1.0))
    layers.append(dict(type='pano', image=ex.img('bed', bed_img()), k=1.0, x=0, y=0))
    for j, (seed, vx) in enumerate(((911, 5.0), (912, -4.0))):
        ci = caustic_img(seed)
        layers.append(dict(type='wrap', image=ex.img('caustic%d' % j, BJ.tile_to(ci, CAUS_P, CAUS_P + W)), period=CAUS_P,
                           k=1.0, y=CAUS_Y, vx=vx))
    for i in range(len(ANEMONES)):
        layers.append(bake('anemone%d' % i, anemone_box(i), SWAY_N, SWAY_FPS, lambda t, i=i: anemone_frame(i, t), 1.0))
    for i in range(len(BUBBLE_SRC)):
        layers.append(bake('bubbles%d' % i, bubble_box(i), BUB_N, BUB_FPS, lambda t, i=i: bubble_frame(i, t), 1.0))
    top = sand_top_x()
    ap = anchor_parts()
    anchors = dict(surface=15, seabed=[int(top.min()), int(top.max())], walk_ch2=list(CH2_WALK),
                   walk_ch3=list(CH3_WALK), walk_x=list(WALK_X), anchor=[int(ap['ring_c'][0]), int(ap['ring_c'][1])],
                   crate=[CRATE[0] + 15, CRATE[1]], clam=[CLAM[0] + 10, CLAM[1]], eel=list(EEL),
                   hull=[HULL_X0, HULL_X0 + HULL_W, SURF_K], vortex=[320, 166])
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, strips)
    return st


def direct(camX, t, strips):
    """不经导出：直接拿源图按同一套公式拼一帧（自检用，clouds 层不比）。"""
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(water_img())

    def pano(im, k, x=0, y=0):
        paste(out, im, x - math.floor(camX * k), y)

    def strip(name):
        for (nm, box, n, fps, fn, k) in strips:
            if nm == name:
                f = int(math.floor(t * fps)) % n
                fr = fn(f / fps).crop(box)
                xs = [box[0]] if name != 'surface' else list(range(0, SURFW, SURF_TILE))
                for x in xs:
                    pano(fr, k, x, box[1])
                return
        raise KeyError(name)

    def wrap(im, k, vx, y, period):
        o = int(math.floor(camX * k + t * vx)) % period
        big = Image.new('RGBA', (period + W, im.height), (0, 0, 0, 0))
        src = im.crop((0, 0, period, im.height))
        for x in range(0, period + W, period):
            big.paste(src, (x, 0))
        out.alpha_composite(big.crop((o, 0, o + W, im.height)), (0, y))
    pano(far_img(), FAR_K)
    pano(mid_img(), MID_K)
    for i in range(len(RAYS)):
        strip('ray%d' % i)
    strip('surface')
    pano(hull_img(), SURF_K, HULL_X0)
    wrap(fish_img(), FISH_K, 6.0, FISH_Y0, PW)
    for gi in range(len(KELP_GROUPS)):
        strip('kelp%d' % gi)
    pano(bed_img(), 1.0)
    for j, (seed, vx) in enumerate(((911, 5.0), (912, -4.0))):
        wrap(caustic_img(seed), 1.0, vx, CAUS_Y, CAUS_P)
    for i in range(len(ANEMONES)):
        strip('anemone%d' % i)
    for i in range(len(BUBBLE_SRC)):
        strip('bubbles%d' % i)
    return out


def _lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def _checks(ex, BJ, st, strips):
    # 1. 整屏不露黑
    bad = 0
    for camX in (0, 80, 160, 240, 320):
        for t in (0.0, 0.7, 1.35):
            im = np.array(BJ.ref_render(st, ex.images, camX, t).convert('RGB'))
            bad += int((im.sum(-1) == 0).sum())
    ex.checked('镜头 0…320 × 3 个时刻整屏都有画（不露黑）', bad)
    ex.checked('水体底图整张不透明', int((arr(water_img())[..., 3] != 255).sum()))
    # 2. 导出层重建 = 直接拼源图（验证裁框、视差偏移、三份水面接缝、wrap 周期）
    only = {'static', 'pano', 'strip', 'wrap'}
    diff = 0
    for camX in (0, 37, 160, 251, 320):
        for t in (0.0, 0.62, 1.33, 1.99):
            diff += BJ.ndiff(BJ.ref_render(st, ex.images, camX, t, only=only), direct(camX, t, strips))
    ex.checked('导出层按 §3.6 公式重建 = 直接用源图拼（5 镜头 × 4 时刻）', diff)
    # 3. 帧条：2 s 闭合、宽度不超 4096
    bad_close = 0
    for name, box, n, fps, fn, k in strips:
        if abs(n / fps - LOOP) > 1e-9:
            bad_close += 1
        bad_close += BJ.ndiff_rgba(fn(LOOP).crop(box), fn(0.0).crop(box))
    ex.checked('全部 %d 条帧条 n/fps = 2 s 且 t = 2 s 和第 0 帧逐像素相同' % len(strips), bad_close)
    wide = [L for L in st['layers'] if L['type'] == 'strip' and L['w'] * L['n'] > 4096]
    ex.checked('帧条宽度都 ≤ 4096（最宽 %d）' % max(L['w'] * L['n'] for L in st['layers'] if L['type'] == 'strip'),
               len(wide))
    # 4. 海床：y 146 往下整张是沙（沙层本身不透明，不靠别的层垫）；可走带（x 8–632、y 150–178）里没有石头 / 墙 /
    #    珊瑚 / 箱子 / 锚这些“立着的东西”，会动的东西（海带、海葵、气泡）也都在 y ≤ 148
    sand, flat, obj, wall, top = bed_parts()
    ex.checked('沙层 y %d–179 整张不透明（没有洞）' % SAND_SOLID, int((sand[SAND_SOLID:, :, 3] != 255).sum()))
    bed = arr(bed_img())
    ex.checked('近景海床层 y %d–179 整张不透明' % SAND_SOLID, int((bed[SAND_SOLID:, :, 3] != 255).sum()))
    x0, x1 = WALK_X
    y0, y1 = WALK
    blk = (obj[y0:y1 + 1, x0:x1 + 1, 3] > 0) | (wall[y0:y1 + 1, x0:x1 + 1, 3] > 0)
    ex.checked('可走带 x %d–%d、y %d–%d 里没有立着的东西（石头 / 墙 / 珊瑚 / 箱子 / 锚）' % (x0, x1, y0, y1),
               int(blk.sum()))
    low = [nm for (nm, box, n, fps, fn, k) in strips if k == 1.0 and box[3] > 149]
    ex.checked('会动的近景（海带 / 海葵 / 气泡）都在 y ≤ 149：%s' % (low or '全部'), len(low))
    # 5. 可走带是“地面的颜色”：浅色沙（亮度 ≥ 110 的像素 ≥ 96%），和承太郎的藏青（亮度约 50）拉得开
    wa = bed[y0:y1 + 1, x0:x1 + 1, :3].astype(np.float32)
    lum = _lum(wa)
    dark = int((lum < 110).sum())
    ex.checked('可走带亮度 ≥ 110 的像素占比 %.1f%%（中位亮度 %d）' % (100 - 100.0 * dark / lum.size, int(np.median(lum))),
               dark, limit=int(lum.size * 0.04))
    # 6. 第3章 sea_ch3 只用左边 320（镜头 0）：船底不出现
    hull_l = [L for L in st['layers'] if L.get('image', '').endswith('/hull')][0]
    ex.checked('船底在镜头 0 时完全在屏幕外（第3章看不到游艇）', 0 if hull_l['x'] - 0 >= W else 1)
    # 7. 大小
    tot = sum(_png_bytes(im) for k_, im in ex.images.items() if k_.startswith('bg/%s/' % ex.key))
    ex.checked('整张背景 PNG 合计 %.1f KB（≤ 700 KB）' % (tot / 1024.0), 0 if tot <= 700 * 1024 else 1)


if __name__ == '__main__':
    out = os.path.join(HERE, '_preview', 'ch2', 'uw')
    os.makedirs(out, exist_ok=True)
    for name, im in (('water', water_img()), ('far', far_img()), ('mid', mid_img()), ('bed', bed_img()),
                     ('surface', surface_tile(0.0)), ('fish', fish_img()), ('hull', hull_img())):
        im.save(os.path.join(out, 'layer_%s.png' % name))
    print('ok', out)
