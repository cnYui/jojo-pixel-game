# -*- coding: utf-8 -*-
r"""kujo_bedroom_morning —— 终章 F-13：空条家荷莉的卧室，第 50 天的早上（地图 bedroom_fin，荷莉醒来）。
2026-10-19 cairo 组画。**和序章的 kujo_bedroom_dusk（tools/bg_new/kujo_bedroom_dusk.py）是同一间房**：天花板、栏间、
长押、土墙、左上的小相框、障子窗（118–300 × 38–112）、三根柱子（x 6 / 110 / 306）、金屏风（14–94）、架子和花瓶、
门槛、榻榻米、托盘、行灯的位置一个像素都没挪（几何照抄 dusk 的 static()，只换光和窗）——玩家一眼认得出。
换的东西：
  · 窗：中间两扇障子推开了（左边那扇推到最左、右边那扇推到最右，窗中间 163–254 敞开），窗外是早上的天、对面人家的
    瓦屋顶、白墙 + 瓦顶的院墙、一棵正开着的樱花（花瓣 strip 飘进屋里）；剩下两扇纸面被早上的太阳照得白里透金，
    映着樱花枝的影子（黄昏时是松枝的影子）
  · 光：从敞开的窗口斜照进来的一片晨光落在榻榻米上（正好照在 bed 那儿）、墙上一道亮；整间房用 _KJ['morning'] 调色
  · 行灯没点（白天）；最左边柱子外面是开着的门（door [30,156]：门外走廊暗一点）
荷莉（剧情摆 scene:s19_bed_ok / s19_holly_sit，自带被褥）躺在 bed [193,153]，被褥那一块榻榻米是空的。

地图 320 宽、ground 158、可走带 y 150–176（榻榻米）。
图层：static（整张底图）→ petals（樱花瓣：窗外飘落 + 几片飘进屋落到榻榻米上，8 帧 @4 fps）→ dust（光里的浮尘一闪一闪）
      → sparrow（窗外樱花枝上的麻雀，啄一下、跳一下）。
锚点：bed [193,153]、window [209,74]（窗的中心 = 敞开那一段的中心）、door [30,156]、arrive [60,164]（素材总表 §一.3）；
      另导出 window_box [118,38,300,112]、window_open [163,38,254,112]、sun_patch（地上那片光的四个角）、
      andon [305,144]、shelf、tray（和 dusk 一样）。
"""
import sys
sys.dont_write_bytecode = True

import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from engine import bg_asia as A  # noqa: E402
from engine.core import gradient, hrange, hash01, mix  # noqa: E402

W, H = 320, 180
C = A._c4
N, FPS = 8, 4.0
WX0, WY0, WX1, WY1 = 118, 38, 300, 112          # 障子窗（同 dusk）
OPEN = (163, 254)                               # 推开的那一段
ANCHORS = dict(bed=[193, 153], window=[209, 74], door=[30, 156], arrive=[60, 164])
STAND = ('bed', 'door', 'arrive')
SUN_PATCH = [(160, 143), (262, 143), (238, 176), (126, 176)]   # 地上那片晨光（左上、右上、右下、左下）


def R(d, box, col, outline=None):
    d.rectangle(box, fill=C(col), outline=C(outline) if outline else None)


def L(d, pts, col, width=1):
    d.line(pts, fill=C(col), width=width)


def P(d, x, y, col):
    d.point((round(x), round(y)), fill=C(col))


# ============================================================ 窗外（推开的那一段看出去）
def outside(d, img):
    x0, x1 = OPEN
    gradient(img, (x0, WY0, x1, WY1), [(150, 196, 236), (196, 222, 240), (246, 238, 222)], bands=8)
    lay = A._new(W, H)                                               # 右上：早上的太阳（在画面外）的光——只亮在窗口里
    A._glow(lay, 244, 44, 46, 30, (255, 250, 230), 90, rings=4)
    img.alpha_composite(lay.crop((x0, WY0, x1, WY1)), (x0, WY0))
    d = ImageDraw.Draw(img)
    # 对面人家的瓦屋顶（灰蓝的瓦一垄垄、屋脊）
    for x in range(x0, x1):
        top = 82 + int(round(2 * math.sin((x - x0) * 0.05)))
        if x > 228:
            top += (x - 228) // 3
        for y in range(top, 96):
            c = (110, 122, 140) if (x - x0) % 4 else (90, 100, 118)
            if y == top:
                c = (150, 160, 176)
            P(d, x, y, c)
    R(d, (x0, 80, x0 + 60, 81), (80, 90, 108))
    # 院墙：白灰墙 + 一溜瓦顶
    R(d, (x0, 98, x1, WY1), (236, 232, 222))
    R(d, (x0, 96, x1, 98), (96, 104, 120))
    L(d, (x0, 96, x1, 96), (140, 150, 166))
    for x in range(x0, x1, 3):
        P(d, x, 97, (70, 78, 92))
    for i in range(30):
        P(d, hrange(x0, x1, i, 61), hrange(100, WY1, i, 62), (220, 214, 200))
    # 樱花树：树干从右下斜着长上来，枝子伸满窗口上半
    trunk = (96, 70, 62)
    L(d, (240, WY1, 236, 92, 226, 74), trunk, 3)
    L(d, (226, 74, 206, 58, 182, 50), trunk, 2)
    L(d, (226, 74, 240, 56, 252, 50), trunk, 2)
    L(d, (206, 58, 196, 44), trunk)
    L(d, (214, 64, 172, 66), trunk)
    L(d, (236, 88, 254, 84), trunk)
    L(d, (238, 92, 237, 100), (130, 100, 90))
    pink = ((255, 226, 234), (248, 196, 212), (236, 166, 190), (214, 134, 164))
    for i, (cx, cy, r) in enumerate(((184, 48, 9), (198, 42, 8), (214, 52, 9), (232, 48, 10), (248, 44, 8), (172, 62, 7),
                                     (196, 60, 7), (250, 60, 7), (244, 78, 6), (220, 66, 6), (168, 44, 6))):
        for k in range(int(r * r * 2.2)):
            a_ = hrange(0, math.tau, i, k, 63)
            rr = r * math.sqrt(hash01(i, k, 64))
            x = cx + rr * math.cos(a_)
            y = cy + rr * 0.7 * math.sin(a_)
            if not (x0 <= x < x1 and WY0 <= y < WY1):
                continue
            u = (math.sin(a_) * 0.5 + 0.5) * 0.6 + rr / r * 0.4      # 下沿 / 外圈暗一点，上沿亮
            c = pink[min(3, int(u * 3.2))]
            P(d, x, y, c)
    for i in range(14):                                              # 几片已经飘在空中的花瓣（静的）
        P(d, hrange(x0, x1, i, 65), hrange(70, 110, i, 66), pink[1])


# ============================================================ 底图（几何照抄 kujo_bedroom_dusk.static，只换光和窗）
@lru_cache(maxsize=1)
def static():
    Pv = A._KJ['morning']
    img = A._new(col=(120, 90, 60))
    d = ImageDraw.Draw(img)
    # 天花板 + 栏间（竖格子）+ 长押（同 dusk）
    R(d, (0, 0, W, 10), (110, 76, 48))
    for x in range(0, W, 12):
        L(d, (x, 0, x, 10), (90, 60, 38))
        L(d, (x + 1, 0, x + 1, 10), (124, 88, 58))
    for i in range(24):
        y = int(hrange(2, 9, i, 3))
        xa = int(hrange(0, W, i, 4))
        L(d, (xa, y, xa + int(hrange(6, 20, i, 5)), y), (98, 66, 42))
    R(d, (0, 10, W, 26), (176, 156, 120))
    for x in range(2, W, 5):
        L(d, (x, 12, x, 25), (204, 184, 146))
        L(d, (x + 1, 12, x + 1, 25), (150, 120, 84))
    L(d, (0, 12, W, 12), (150, 112, 70))
    L(d, (0, 18, W, 18), (150, 112, 70))
    R(d, (0, 10, W, 11), (120, 86, 52))
    R(d, (0, 26, W, 30), (150, 108, 66))
    L(d, (0, 26, W, 26), (190, 150, 104))
    L(d, (0, 30, W, 30), (90, 62, 38))
    # 土墙（同 dusk）
    R(d, (0, 31, W, 140), (210, 192, 158))
    A._tex_noise(img, (0, 30, W, 140), 0.07, 21)
    d = ImageDraw.Draw(img)
    for i in range(260):
        P(d, hrange(0, W, i, 41), hrange(32, 136, i, 42), (194, 174, 140) if i % 2 else (224, 208, 176))
    A._blend_rect(img, (0, 31, W, 34), (80, 50, 30), 40)
    d = ImageDraw.Draw(img)
    # 小相框（荷莉和小时候的承太郎，同 dusk）
    R(d, (48, 38, 64, 52), (110, 76, 46))
    R(d, (50, 40, 62, 50), (226, 214, 190))
    R(d, (51, 41, 61, 45), (176, 200, 220))
    d.ellipse((52, 43, 55, 46), fill=C((240, 210, 120)))
    R(d, (52, 46, 55, 49), (230, 120, 140))
    d.ellipse((57, 45, 59, 47), fill=C((40, 36, 40)))
    R(d, (57, 47, 59, 49), (40, 50, 80))
    L(d, (56, 36, 52, 38), (90, 70, 50))
    L(d, (56, 36, 60, 38), (90, 70, 50))
    # 障子窗：外框、窗外（推开的那段）、剩下两扇纸面（被早上的太阳照得白里透金 + 樱花枝的影子）
    wx0, wy0, wx1, wy1 = WX0, WY0, WX1, WY1
    paper = (252, 246, 228)
    wood = (130, 92, 56)
    R(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), (120, 84, 50))
    L(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy0 - 3), (160, 118, 76))
    outside(d, img)
    d = ImageDraw.Draw(img)
    for (a_, b_) in ((wx0, OPEN[0]), (OPEN[1], wx1)):                # 两扇关着的障子（两扇叠在一起）
        A._shoji(d, a_, wy0, b_, wy1, paper=paper, wood=wood, cell=(13, 12))
        for cx in range(a_, b_ - 12, 13):
            for cy in range(wy0, wy1 - 18, 12):
                u = (cy - wy0) / float(wy1 - wy0)
                R(d, (cx + 1, cy + 1, cx + 12, cy + 11), mix(paper, (255, 236, 196), 0.35 * (1 - u)))
                L(d, (cx + 1, cy + 11, cx + 12, cy + 11), mix(paper, wood, 0.18))
        for x in range(a_, b_ + 1, 13):
            L(d, (x, wy0, x, wy1), wood)
        for y in range(wy0, wy1 + 1, 12):
            L(d, (a_, y, b_, y), wood)
        L(d, (a_, wy0, a_, wy1), (96, 66, 40))
        L(d, (b_, wy0, b_, wy1), (96, 66, 40))
        L(d, (b_ - 1 if a_ == wx0 else a_ + 1, wy0, b_ - 1 if a_ == wx0 else a_ + 1, wy1), (170, 130, 86))
    sh = mix(paper, (120, 120, 150), 0.22)                           # 右边那扇纸上映着樱花枝的影子
    L(d, (OPEN[1] + 2, wy0 + 20, wx1 - 6, wy0 + 10), sh)
    L(d, (OPEN[1] + 10, wy0 + 16, OPEN[1] + 18, wy0 + 30), sh)
    for (px_, py_, r) in ((OPEN[1] + 14, wy0 + 10, 7), (wx1 - 12, wy0 + 6, 6), (OPEN[1] + 22, wy0 + 28, 5)):
        for k in range(r * 5):
            P(d, px_ + hrange(-r, r, k, 67), py_ + hrange(-r * 0.6, r * 0.6, k, 68), sh)
    R(d, (wx0 - 5, wy1 + 3, wx1 + 5, wy1 + 6), (140, 98, 60))      # 窗台
    L(d, (wx0 - 5, wy1 + 3, wx1 + 5, wy1 + 3), (200, 156, 106))
    A._blend_rect(img, (wx0 - 3, wy1 + 7, wx1 + 3, wy1 + 9), (80, 50, 30), 40)
    d = ImageDraw.Draw(img)
    # 柱子（木纹，同 dusk）
    for x in (6, 110, 306):
        A._post(d, x, 26, 142)
        for i in range(4):
            xx = x + 1 + int(hrange(0, 4, x, i))
            ya = int(hrange(30, 100, x, i, 1))
            L(d, (xx, ya, xx, ya + int(hrange(10, 36, x, i, 2))), (126, 88, 52))
    # 最左边柱子外面：开着的门（门外走廊，暗一点）
    R(d, (0, 31, 5, 142), (150, 128, 96))
    R(d, (0, 120, 5, 142), (126, 92, 58))
    for y in range(122, 142, 4):
        L(d, (0, y, 5, y), (104, 74, 46))
    L(d, (5, 31, 5, 142), (96, 66, 40))
    # 金屏风（同 dusk）
    pw = 20
    for i in range(4):
        x0 = 14 + i * pw
        top = 62 if i % 2 == 0 else 60
        col = (206, 170, 90) if i % 2 == 0 else (186, 150, 76)
        R(d, (x0, top, x0 + pw, 146), col)
        for gy in range(top + 2, 144, 6):
            for gx in range(x0 + 2, x0 + pw - 1, 6):
                if hash01(gx, gy, 7) < 0.45:
                    R(d, (gx, gy, gx + 5, gy + 5), mix(col, (255, 226, 140), 0.18))
                L(d, (gx, gy, gx + 5, gy), mix(col, (120, 90, 40), 0.18))
        d.rectangle((x0, top, x0 + pw, 146), outline=C((40, 24, 18)))
        L(d, (x0 + 1, top + 1, x0 + pw - 1, top + 1), (90, 60, 30))
        if i:
            for hy in (top + 14, 128):
                R(d, (x0 - 1, hy, x0 + 1, hy + 2), (200, 170, 100))
    L(d, (14, 146, 94, 146), (60, 36, 24))
    L(d, (20, 120, 40, 98, 66, 90, 88, 76), (70, 50, 36), 2)
    L(d, (40, 98, 36, 86), (70, 50, 36))
    L(d, (66, 90, 70, 104, 80, 110), (70, 50, 36))
    L(d, (22, 140, 30, 128, 44, 124), (80, 58, 40))
    for (px_, py_) in ((40, 98), (52, 94), (66, 90), (76, 84), (88, 76), (30, 110), (58, 86), (36, 86), (72, 104),
                       (80, 110), (30, 128), (44, 124)):
        d.ellipse((px_ - 2, py_ - 2, px_ + 2, py_ + 2), fill=C((236, 120, 150)))
        P(d, px_, py_, (255, 220, 230))
        P(d, px_ - 1, py_ + 1, (200, 80, 110))
    for (px_, py_) in ((46, 96), (62, 88), (84, 79), (26, 134)):
        P(d, px_, py_, (220, 70, 100))
    # 架子：花瓶、小相框、首饰盒（同 dusk）
    R(d, (256, 124, 296, 130), (110, 70, 40))
    L(d, (256, 124, 296, 124), (150, 104, 66))
    R(d, (258, 130, 262, 142), (90, 56, 32))
    R(d, (290, 130, 294, 142), (90, 56, 32))
    R(d, (262, 136, 290, 137), (90, 56, 32))
    d.ellipse((270, 110, 280, 124), fill=C((200, 80, 70)), outline=C((100, 40, 36)))
    L(d, (272, 113, 272, 118), (236, 140, 120))
    L(d, (275, 110, 272, 100), (60, 110, 60))
    L(d, (274, 106, 278, 104), (60, 110, 60))
    d.ellipse((268, 96, 276, 102), fill=C((250, 240, 240)))
    P(d, 272, 99, (240, 200, 90))
    R(d, (259, 116, 266, 124), (70, 50, 36))
    R(d, (260, 117, 265, 122), (190, 200, 214))
    R(d, (283, 119, 293, 124), (140, 40, 50))
    L(d, (283, 119, 293, 119), (200, 90, 90))
    P(d, 288, 121, (240, 200, 100))
    # 门槛 + 榻榻米（同 dusk）
    R(d, (0, 136, W, 142), (150, 108, 66))
    L(d, (0, 136, W, 136), (196, 150, 100))
    L(d, (0, 139, W, 139), (126, 88, 52))
    A._tatami(d, img, 142, H, [[60, 150, 240], [20, 110, 200, 290]], seed=2)
    d = ImageDraw.Draw(img)
    for y in range(144, H, 2):
        for x in range((y // 2) % 3, W, 3):
            if hash01(x, y, 98) < 0.35:
                P(d, x, y, (196, 188, 120) if (x + y) % 2 else (170, 162, 98))
    for y in (142, 156):
        for x in range(1, W, 4):
            P(d, x, y + 1, (96, 112, 84))
    A._blend_rect(img, (0, 143, W, 145), (60, 40, 20), 50)
    d = ImageDraw.Draw(img)
    # 托盘：水盆、毛巾、水杯（同 dusk）
    A._blend_rect(img, (221, 164, 254, 166), (60, 40, 20), 60)
    d = ImageDraw.Draw(img)
    R(d, (222, 158, 252, 164), (120, 60, 40), (70, 34, 24))
    L(d, (223, 159, 251, 159), (150, 84, 56))
    d.ellipse((226, 152, 240, 160), fill=C((190, 196, 206)), outline=C((100, 106, 120)))
    d.ellipse((228, 153, 238, 157), fill=C((150, 200, 230)))
    L(d, (230, 154, 233, 154), (210, 236, 250))
    R(d, (242, 154, 250, 158), (250, 250, 250), (180, 180, 190))
    L(d, (243, 156, 249, 156), (210, 214, 226))
    R(d, (244, 150, 247, 154), (200, 220, 236), (140, 150, 170))
    # 门口一双拖鞋（同 dusk）
    for sx in (20, 28):
        d.rounded_rectangle((sx, 168, sx + 6, 171), radius=1, fill=C((150, 110, 160)), outline=C((90, 60, 100)))
        L(d, (sx + 1, 168, sx + 4, 168), (200, 170, 210))
    # 行灯：白天没点（纸是本色，没有光晕）
    R(d, (296, 132, 314, 158), (90, 56, 32))
    R(d, (298, 134, 312, 154), (226, 218, 196))
    L(d, (305, 134, 305, 154), (90, 56, 32))
    L(d, (298, 144, 312, 144), (90, 56, 32))
    R(d, (296, 158, 298, 161), (70, 42, 24))
    R(d, (312, 158, 314, 161), (70, 42, 24))
    L(d, (300, 129, 310, 129), (70, 42, 24))
    L(d, (300, 129, 300, 132), (70, 42, 24))
    L(d, (310, 129, 310, 132), (70, 42, 24))
    img = A._grade(img, sat=1.0, val=Pv['val'], tint=Pv['tint'], tint_amt=Pv['ta'])
    return sunlight(img)


def sunlight(img):
    """晨光：窗口斜照进来的一片光落在榻榻米上（梯形，边上 Bayer 抖开）+ 窗下墙上一道亮。只改颜色，不改透明度。"""
    a = np.array(img).astype(np.float32)
    bay = A._bayer(W, H)
    (x0, y0), (x1, _), (x2, y2), (x3, _) = SUN_PATCH
    for y in range(y0, H):
        u = (y - y0) / float(y2 - y0)
        l = x0 + (x3 - x0) * u
        r = x1 + (x2 - x1) * u
        for x in range(max(0, int(l) - 4), min(W, int(r) + 5)):
            edge = min(x - l, r - x)
            k = np.clip((edge + 4) / 8.0, 0, 1) * (0.85 + 0.15 * (1 - u))
            if k > bay[y, x] * 0.999:
                a[y, x, :3] = np.minimum(255, a[y, x, :3] * 1.12 + np.array((22, 18, 8), np.float32))
    for y in range(WY1 + 10, 136):                                   # 窗下墙上：从敞开处透下来的一道亮
        for x in range(OPEN[0], OPEN[1]):
            if bay[y, x] < 0.45 - (y - WY1 - 10) * 0.012:
                a[y, x, :3] = np.minimum(255, a[y, x, :3] * 1.06 + 10)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


# ============================================================ 动的小东西
PETALS_BOX = (150, WY0, 272, 168)


def frame_of(t):
    return int(math.floor(t * FPS + 1e-6)) % N


def petals_raw(f):
    """樱花瓣：窗外从树上飘下来（只在敞开那段里）、几片飘进屋里斜着落到榻榻米上（往左下）；8 帧一圈。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    cols = ((255, 214, 226), (244, 176, 198), (255, 236, 242))
    for i in range(12):                                              # 窗外
        u = ((f / N) + hash01(i, 71)) % 1.0
        x = hrange(OPEN[0] + 4, OPEN[1] - 4, i, 72) + 3 * math.sin(math.tau * u + i)
        y = WY0 + 6 + u * (WY1 - WY0 - 10)
        c = cols[i % 3]
        P(d, x, y, c)
        if (i + f) % 3 == 0:
            P(d, x + 1, y, c)
    for i in range(6):                                               # 飘进屋里
        u = ((f / N) + i / 6.0) % 1.0
        x = hrange(196, 248, i, 73) - u * 40 + 3 * math.sin(math.tau * u * 2 + i)
        y = WY1 - 6 + u * 58
        c = cols[(i + 1) % 3]
        P(d, x, y, c)
        if (i + f) % 2:
            P(d, x - 1, y + 1, c)
    return im


def dust_raw(f):
    """光里的浮尘：晨光斜照的那一片空气里，一颗颗亮点一闪一闪、慢慢往下沉。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for i in range(16):
        ph = (f + int(hash01(i, 81) * N)) % N
        if ph > 4:
            continue
        x = hrange(150, 250, i, 82) - (hrange(118, 140, i, 83) - 118) * 0.3
        y = hrange(118, 140, i, 83) + ph
        P(d, x, y, (255, 250, 220) if ph in (1, 2) else (240, 226, 190))
    return im


SPARROW = ((0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 2, 0), (0, 0, 1, 1), (0, 0, 0, 0), (1, -1, 0, 1), (1, 0, 0, 0),
           (0, 0, -1, 1))   # 每帧 (dx, dy, 低头几 px, 尾巴翘不翘)：站着 → 甩尾 → 啄 → 抬头 → 跳过去 → 落下 → 跳回来


def sparrow_raw(f):
    """窗外樱花枝上的一只麻雀：甩一下尾巴、低头啄一下、跳过去再跳回来（每一帧姿势都不一样）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    x, y = 188, 65
    dx, dy, peck, tail = SPARROW[f]
    body, head, belly = (140, 100, 70), (120, 80, 56), (226, 214, 190)
    R(d, (x + dx, y - 2 + dy, x + 3 + dx, y + dy), body)
    P(d, x + 1 + dx, y + dy, belly)
    P(d, x - 1 + dx, y - 1 - tail + dy, body)                        # 尾巴
    hx = x + 4 + dx
    hy = y - 3 + dy + peck                                           # 低头啄 / 抬头
    R(d, (hx - 1, hy, hx, hy + 1), head)
    P(d, hx + 1, hy + 1, (230, 190, 90))
    P(d, x + 1 + dx, y + 1, (90, 70, 50))
    P(d, x + 2 + dx, y + 1, (90, 70, 50))
    return im


def _cached(raw):
    cache = {}

    def fn(t):
        f = frame_of(t)
        if f not in cache:
            cache[f] = raw(f)
        return cache[f]
    return fn


STRIPS = (('petals', _cached(petals_raw)), ('dust', _cached(dust_raw)), ('sparrow', _cached(sparrow_raw)))


def _box(fn):
    bb = None
    for i in range(N):
        b = fn(i / FPS).getchannel('A').getbbox()
        if b:
            bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    return bb


def compose(t=0.0):
    img = static().copy()
    for (name, fn) in STRIPS:
        box = _box(fn)
        f = int(math.floor(t * FPS)) % N
        img.alpha_composite(fn(f / FPS).crop(box), box[:2])
    return img


def export(ex, BJ):
    base = static()
    layers = [dict(type='static', image=ex.img('static', base), x=0, y=0)]
    for (name, fn) in STRIPS:
        layers.append(ex.bake(name, _box(fn), N, FPS, fn))
    anchors = {k: list(v) for k, v in ANCHORS.items()}
    anchors.update(window_box=[WX0, WY0, WX1, WY1], window_open=[OPEN[0], WY0, OPEN[1], WY1],
                   sun_patch=[list(p) for p in SUN_PATCH], andon=[305, 144], shelf=[256, 124, 296, 142],
                   tray=[222, 152, 252, 164], walk_x=[12, 300])
    st = ex.stage(320, 158, (150, 176), layers, anchors=anchors)
    if ex.check_on:
        _checks(ex, BJ, st, base)
    return st


def _checks(ex, BJ, st, base):
    for t in (0.0, 0.75, 1.7, 3.3):
        ex.checked('卧室 t=%.2f 导出 vs 直接拼' % t, BJ.ndiff_rgba(BJ.ref_render(st, ex.images, 0, t), compose(t)))
    a = np.array(base)
    ex.checked('卧室底图整张不透明', int((a[..., 3] != 255).sum()))
    for (name, fn) in STRIPS:
        box = _box(fn)
        fr = [fn(i / FPS).crop(box) for i in range(N)]
        ex.checked('strip %s 闭合（t=0 vs t=%.1f）' % (name, N / FPS), BJ.ndiff_rgba(fn(0.0).crop(box), fn(N / FPS).crop(box)))
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % N]) > 0 for i in range(N))
        ex.checked('strip %s 每一帧都在动（%d / %d）' % (name, moving, N), N - moving)
        hard = sum(int(((np.array(q)[..., 3] > 0) & (np.array(q)[..., 3] < 255)).sum()) for q in fr)
        ex.checked('strip %s 只有 0 / 255 透明度' % name, hard)
    anc = st['anchors']
    miss = [k for k in ANCHORS if anc.get(k) != ANCHORS[k]]
    ex.checked('素材总表的锚点一个不少、值一致（不一致：%s）' % (miss or '无'), len(miss))
    out = [k for k in STAND if not (150 <= anc[k][1] <= 176 and 4 <= anc[k][0] <= 316)]
    ex.checked('站人的锚点在可走带 150–176 里（不满足：%s）' % (out or '无'), len(out))
    wx, wy = anc['window']
    ex.checked('window (%d,%d) 在推开的那一段窗口里（%d–%d）' % (wx, wy, OPEN[0], OPEN[1]),
               0 if OPEN[0] < wx < OPEN[1] and WY0 < wy < WY1 else 1)
    # 荷莉的被褥（scene:s19_bed_ok 36×15 / s19_holly_sit 38×29，pivot 底边中点）落在 bed：那一块榻榻米上没有别的东西
    bx, by = anc['bed']
    sub = a[max(144, by - 14):by + 1, bx - 19:bx + 20, :3].astype(np.float32)   # 143 以上是门槛和榻榻米后沿的布边
    lu = sub[..., 0] * 0.299 + sub[..., 1] * 0.587 + sub[..., 2] * 0.114
    heri = (np.abs(sub[..., 1] - sub[..., 0]) > 8) & (lu < 110)      # 榻榻米的布边（深绿）是地上的线，不算东西
    odd = int(((np.abs(lu - np.median(lu)) > 60) & ~heri).sum())
    ex.checked('bed (%d,%d) 被褥那一块（38×10）只有榻榻米和布边（别的东西的像素 %d）' % (bx, by, odd), odd)
    # 布局和序章的 dusk 一样：两张图在“没换的东西”上的轮廓一致（金屏风、柱子、架子、托盘、行灯框的位置）
    try:
        dusk = BJ.bg_new('kujo_bedroom_dusk').static()
        da = np.array(dusk).astype(np.float32)
        same = 0
        for (x0, y0, x1, y1) in ((14, 60, 95, 147), (6, 26, 12, 142), (110, 26, 116, 142), (256, 124, 297, 143),
                                 (222, 152, 253, 165), (296, 129, 315, 162)):
            ea = np.abs(np.diff(lum(a[y0:y1, x0:x1, :3].astype(np.float32)), axis=1)) > 18
            eb = np.abs(np.diff(lum(da[y0:y1, x0:x1, :3]), axis=1)) > 18
            same += int((ea != eb).sum())
        ex.checked('和序章 kujo_bedroom_dusk 同一个布局（金屏风 / 柱子 / 架子 / 托盘 / 行灯的轮廓不一致的像素 %d ≤ 400）'
                   % same, 0 if same <= 400 else same)
    except Exception as e:                                          # dusk 模块读不到时只记一笔
        ex.note('没能和 dusk 比布局：%s' % e)
    tot = sum(len(_png(im)) for k, im in ex.images.items() if k.startswith('bg/%s/' % ex.key))
    ex.checked('PNG 合计 %.1f KB ≤ 250 KB' % (tot / 1024.0), 0 if tot <= 250 * 1024 else 1)


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def _png(im):
    import io
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


if __name__ == '__main__':
    od = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_preview', 'final', 'after')
    os.makedirs(od, exist_ok=True)
    compose(0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'kujo_bedroom_morning_solo.png'))
    print('ok')
