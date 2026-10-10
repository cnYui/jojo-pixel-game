"""预览：python -B tools\\bg_new\\bgpro_preview.py kujo_house_day kujo_house_night kujo_house_morning

空条家和室（游戏层加细节，2026-10-10 bg-pro）：同一间屋三种光（day / night / morning），布局、锚点、
动画和原导出 bg_jojo.exp_kujo 一样（风铃 12 s 真循环、两片落叶、早晨两道斜光呼吸），只把底图画细：

  天花板：竿缘天井的木纹；栏间：格子后面压暗 + 高光；长押上的钉隐（金色小饰）
  壁龛：聚乐土墙的砂粒；挂轴 = 富士山（雪顶、红日、云带、松林、落款红印、轴头），挂轴的挂钩和吊绳；
        床板木纹、左边小香炉、花瓶下的薄板；床柱的天然木纹和节疤
  隔扇：黑漆边框、金云带的描边、下半部淡墨远山 + 松枝、拉手的铜圈
  庭院：天上两朵小云（夜里换成月亮 + 星星）、远树两层、院墙瓦檐的瓦当、粉墙的柱子和水渍；
        池塘石岸、三条锦鲤、睡莲叶；踏脚石 + 脱鞋石上一双木屐；苔藓斑；松树的支柱；
        风铃后面的柱子上趴着一只壁虎（阿布德尔的台词）
  廊下：木板接缝、檐下一只蚊香猪；拉门：纸的旧色、樱花形补丁
  榻榻米：席面织纹、榻榻米边的花纹；矮桌：木纹、茶壶侧把、两杯绿茶、一碟仙贝；坐垫：中间的线结、四角穗子
  夜：月亮、星星、石灯笼点亮（调色之后另画，免得被压暗）
"""
import sys
sys.dont_write_bytecode = True

import math
import os
from functools import lru_cache

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np
from PIL import Image, ImageDraw
from engine import bg_asia as A
from engine.core import gradient, hrange, hash01, mix

W, H = 320, 180
C = A._c4


def R(d, box, col, outline=None):
    d.rectangle(box, fill=C(col), outline=C(outline) if outline else None)


def L(d, pts, col, width=1):
    d.line(pts, fill=C(col), width=width)


def P(d, x, y, col):
    d.point((round(x), round(y)), fill=C(col))


def grain(d, box, base, seed, n=6, dark=0.18, vertical=True):
    """木纹：在 box 里画几条断续的深 / 浅细线。"""
    x0, y0, x1, y1 = box
    for i in range(n):
        if vertical:
            x = x0 + hrange(0, max(1, x1 - x0), seed, i)
            ya = y0 + hrange(0, (y1 - y0) * 0.5, seed, i, 1)
            yb = ya + hrange((y1 - y0) * 0.3, (y1 - y0), seed, i, 2)
            L(d, (round(x), round(ya), round(x), round(min(y1, yb))), mix(base, (0, 0, 0) if i % 3 else (255, 230, 190), dark))
        else:
            y = y0 + hrange(0, max(1, y1 - y0), seed, i)
            xa = x0 + hrange(0, (x1 - x0) * 0.6, seed, i, 1)
            xb = xa + hrange((x1 - x0) * 0.2, (x1 - x0) * 0.7, seed, i, 2)
            L(d, (round(xa), round(y), round(min(x1, xb)), round(y)), mix(base, (0, 0, 0) if i % 3 else (255, 230, 190), dark))


def speckle(d, box, cols, n, seed):
    x0, y0, x1, y1 = box
    for i in range(n):
        P(d, hrange(x0, x1, seed, i), hrange(y0, y1, seed, i, 1), cols[i % len(cols)])


# ---------------------------------------------------------------- 庭院
def garden(img, sky, variant):
    d = ImageDraw.Draw(img)
    gx0, gx1, gy0, gy1 = 206, 318, 34, 134
    gradient(img, (gx0, gy0, gx1, 100), sky, bands=6)
    d = ImageDraw.Draw(img)
    if variant != 'night':                                   # 两朵小云（夜里换月亮）
        for cx, cy, w in ((226, 44, 14), (262, 52, 10)):
            d.ellipse((cx - w, cy - 3, cx + w, cy + 3), fill=C((236, 244, 252)))
            d.ellipse((cx - w // 2, cy - 6, cx + w // 2 + 2, cy + 1), fill=C((250, 252, 255)))
            L(d, (cx - w + 2, cy + 3, cx + w - 2, cy + 3), (206, 222, 240))
    # 远树两层
    for i in range(8):
        cx = gx0 - 4 + i * 16 + hrange(-4, 4, i, 15)
        r = hrange(9, 13, i, 16)
        d.ellipse((cx - r, 64 - r * 0.8, cx + r, 64 + r), fill=C((78, 116, 92)))
    for i in range(7):
        cx = gx0 + i * 18 + hrange(-4, 4, i, 5)
        r = hrange(10, 16, i, 6)
        d.ellipse((cx - r, 70 - r * 0.8, cx + r, 70 + r), fill=C((58, 96, 70)))
        d.ellipse((cx - r * 0.6, 70 - r * 0.8 + 1, cx + r * 0.2, 70 - r * 0.2), fill=C((76, 118, 82)))
        speckle(d, (cx - r + 2, 70 - r * 0.6, cx + r - 2, 72), [(46, 80, 58), (92, 134, 92)], 10, 50 + i)
    # 院墙：瓦檐（瓦当一排）+ 粉墙（柱子、水渍）+ 腰板
    R(d, (gx0, 76, gx1, 100), (226, 220, 204))
    for x in range(gx0 + 10, gx1, 28):
        R(d, (x, 78, x + 2, 96), (196, 188, 170))
        L(d, (x + 3, 78, x + 3, 96), (236, 232, 220))
    for i in range(5):
        sx = gx0 + hrange(4, 104, i, 61)
        L(d, (round(sx), 78, round(sx), round(78 + hrange(4, 12, i, 62))), (210, 204, 188))
    R(d, (gx0, 72, gx1, 77), (60, 64, 74))
    L(d, (gx0, 71, gx1, 71), (100, 106, 120))
    for x in range(gx0, gx1, 4):
        L(d, (x, 72, x, 76), (90, 96, 110))
        P(d, x + 1, 77, (120, 126, 140))
        P(d, x + 2, 77, (70, 74, 86))
    L(d, (gx0, 78, gx1, 78), (40, 42, 50))
    R(d, (gx0, 96, gx1, 100), (150, 140, 120))
    for x in range(gx0, gx1, 6):
        L(d, (x, 96, x, 100), (132, 122, 104))
    # 地面：苔 + 耙过的白砂
    R(d, (gx0, 100, gx1, gy1), (178, 172, 150))
    for y in range(102, gy1, 3):
        L(d, (gx0, y, gx1, y), (160, 154, 134))
    for (cx, cy, rx, ry) in ((242, 110, 26, 9), (286, 108, 18, 6)):     # 绕石头的耙纹
        for k in (0, 4):
            d.arc((cx - rx - k, cy - ry - k // 2, cx + rx + k, cy + ry + k // 2), 0, 360, fill=C((162, 156, 136)))
    for i in range(14):                                                  # 苔藓斑
        mx, my = hrange(gx0, gx1, i, 71), hrange(100, 120, i, 72)
        rr = hrange(2, 5, i, 73)
        d.ellipse((mx - rr, my - rr * 0.4, mx + rr, my + rr * 0.4), fill=C((112, 140, 86) if i % 2 else (96, 128, 76)))
    # 池塘：石岸、水面、波纹、锦鲤、睡莲叶
    d.ellipse((220, 103, 264, 117), fill=C((120, 116, 104)))
    d.ellipse((222, 104, 262, 116), fill=C((86, 130, 170)))
    d.ellipse((226, 106, 256, 113), fill=C((120, 170, 206)))
    for i in range(9):
        a = i / 9 * math.pi * 2
        P(d, 242 + math.cos(a) * 21, 110 + math.sin(a) * 6.5, (150, 146, 132))
    L(d, (230, 108, 236, 108), (176, 212, 236))
    L(d, (244, 112, 252, 112), (176, 212, 236))
    for (kx, ky, col) in ((232, 110, (240, 110, 40)), (245, 108, (250, 250, 244)), (251, 111, (236, 96, 36))):
        L(d, (kx, ky, kx + 2, ky), col)
        P(d, kx + 3, ky, mix(col, (86, 130, 170), 0.5))
    P(d, 246, 108, (230, 70, 40))
    d.ellipse((235, 112, 239, 114), fill=C((70, 130, 70)))
    P(d, 237, 113, (90, 160, 86))
    # 灌木
    for (bx, by, r) in ((210, 104, 10), (286, 106, 12), (300, 100, 9), (268, 112, 7)):
        d.ellipse((bx - r, by - r * 0.7, bx + r, by + r * 0.6), fill=C((50, 100, 60)))
        d.ellipse((bx - r + 2, by - r * 0.7, bx + r - 3, by), fill=C((80, 136, 80)))
        speckle(d, (bx - r + 2, by - r * 0.6, bx + r - 2, by + 2), [(110, 160, 96), (40, 84, 52)], 8, int(bx))
    # 石灯笼（加苔、火袋）
    A._lantern(d, 250, 104)
    P(d, 246, 80, (96, 130, 80))
    P(d, 253, 80, (96, 130, 80))
    L(d, (243, 101, 245, 101), (96, 130, 80))
    # 松 + 支柱
    A._pine(d, 290, 52, 1.1)
    L(d, (275, 68, 275, 100), (110, 80, 52))                                 # 松枝的支柱
    L(d, (272, 68, 278, 68), (110, 80, 52))
    for (px_, py_) in ((286, 50), (300, 60), (276, 64), (294, 44), (306, 68)):
        P(d, px_, py_, (120, 168, 104))
        P(d, px_ + 1, py_, (100, 150, 90))
    L(d, (286, 80, 284, 90), (100, 70, 48))
    # 踏脚石 + 脱鞋石 + 木屐
    for (sx, sy, rw) in ((218, 120, 6), (232, 118, 5), (300, 120, 6), (290, 116, 4)):
        d.ellipse((sx - rw, sy - 2, sx + rw, sy + 2), fill=C((136, 132, 122)))
        L(d, (sx - rw + 2, sy - 2, sx + rw - 2, sy - 2), (176, 172, 160))
    R(d, (262, 119, 284, 124), (128, 124, 116))
    L(d, (263, 119, 283, 119), (170, 166, 156))
    for gx in (266, 274):
        R(d, (gx, 117, gx + 5, 119), (176, 130, 80))
        L(d, (gx + 1, 116, gx + 4, 116), (60, 40, 30))
    # 廊下（木板 + 接缝）+ 蚊香猪
    R(d, (gx0, 124, gx1, 140), (170, 122, 74))
    for y in range(124, 140, 3):
        L(d, (gx0, y, gx1, y), (146, 102, 60))
    for r_, y in enumerate(range(125, 140, 3)):
        for x in range(gx0 + (r_ * 23) % 40, gx1, 40):
            L(d, (x, y, x, y + 1), (130, 90, 52))
    L(d, (gx0, 124, gx1, 124), (206, 160, 110))
    d.ellipse((226, 127, 234, 132), fill=C((176, 96, 62)))
    d.ellipse((232, 128, 236, 131), fill=C((160, 84, 54)))
    P(d, 237, 129, (60, 36, 30))
    L(d, (227, 132, 228, 133), (120, 64, 44))
    L(d, (232, 132, 233, 133), (120, 64, 44))
    P(d, 236, 128, (250, 120, 60))
    # 收在右边的拉门：纸的旧色 + 樱花补丁
    A._shoji(d, 300, 34, 318, 138)
    for (cx, cy) in ((304, 52), (312, 94)):
        R(d, (cx, cy, cx + 3, cy + 4), (226, 216, 190))
    d.ellipse((305, 70, 309, 74), fill=C((246, 206, 214)))
    P(d, 307, 72, (230, 160, 176))


def gecko(d):
    """风铃后面的柱子上（x 270 附近，长押下沿）趴着的壁虎。"""
    col, dk = (128, 132, 96), (80, 84, 60)
    L(d, (268, 37, 272, 37), col)
    P(d, 273, 37, dk)
    P(d, 267, 38, col)
    P(d, 266, 39, col)
    for (x, y) in ((269, 36), (271, 36), (269, 38), (271, 38)):
        P(d, x, y, dk)


# ---------------------------------------------------------------- 屋内
def room(img):
    d = ImageDraw.Draw(img)
    # 天花板：竿缘 + 木纹
    R(d, (0, 0, W, 10), (110, 76, 48))
    for x in range(0, W, 12):
        L(d, (x, 0, x, 10), (90, 60, 38))
        L(d, (x + 1, 0, x + 1, 10), (124, 88, 58))
    grain(d, (0, 1, W, 9), (110, 76, 48), 3, n=26, dark=0.14, vertical=False)
    # 栏间：格子后面压暗
    R(d, (0, 10, W, 30), (172, 150, 112))
    for x in range(0, W, 8):
        L(d, (x, 12, x + 8, 28), (130, 96, 60))
        L(d, (x + 8, 12, x, 28), (130, 96, 60))
        L(d, (x + 1, 12, x + 9, 28), (204, 182, 142))
    for x in (8, 84, 147, 200, 312):
        R(d, (x, 11, x + 3, 29), (140, 100, 62))
    R(d, (0, 10, W, 11), (120, 86, 52))
    L(d, (0, 28, W, 28), (150, 112, 70))
    # 长押 + 钉隐
    R(d, (0, 29, W, 34), (150, 108, 66))
    L(d, (0, 29, W, 29), (190, 150, 104))
    L(d, (0, 34, W, 34), (80, 54, 34))
    grain(d, (0, 30, W, 33), (150, 108, 66), 4, n=10, dark=0.15, vertical=False)
    for x in (10, 86, 202, 314):
        R(d, (x, 30, x + 2, 32), (214, 180, 96))
        P(d, x + 1, 31, (250, 230, 160))


def tokonoma(img):
    d = ImageDraw.Draw(img)
    R(d, (14, 35, 86, 128), (176, 156, 118))
    A._tex_noise(img, (14, 35, 87, 128), 0.08, 11)
    d = ImageDraw.Draw(img)
    speckle(d, (15, 39, 85, 123), [(160, 140, 104), (192, 174, 136), (150, 128, 96)], 120, 81)
    L(d, (15, 39, 15, 123), (150, 130, 96))                                  # 墙角阴影
    R(d, (14, 35, 86, 38), (130, 96, 60))
    L(d, (14, 38, 86, 38), (96, 70, 44))
    # 挂钩 + 吊绳
    P(d, 50, 39, (210, 180, 100))
    L(d, (50, 39, 44, 41), (230, 220, 200))
    L(d, (50, 39, 56, 41), (230, 220, 200))
    # 挂轴：裱（上下一文字金条）+ 画心富士山
    R(d, (38, 41, 62, 116), (70, 104, 110))
    for y in (45, 109):
        L(d, (41, y, 59, y), (214, 186, 110))
    R(d, (41, 46, 59, 108), (236, 228, 206))
    R(d, (41, 46, 59, 64), (226, 224, 214))
    d.ellipse((50, 52, 55, 57), fill=C((206, 60, 50)))                       # 红日
    d.polygon([(41, 98), (48, 72), (52, 69), (56, 72), (59, 82), (59, 98)], fill=C((104, 120, 150)))
    L(d, (52, 69, 59, 82), (78, 92, 120))                                    # 右坡暗面
    d.polygon([(47, 76), (48, 72), (52, 69), (56, 72), (57, 76), (56, 78), (55, 75), (53, 79), (52, 75),
               (50, 78), (49, 75)], fill=C((250, 250, 248)))
    L(d, (41, 88, 59, 88), (232, 226, 212))                                  # 云带
    L(d, (44, 89, 56, 89), (220, 212, 196))
    for i, x in enumerate(range(41, 60, 2)):                                  # 山脚松林（矮）
        h = 1 + (i * 7) % 3
        L(d, (x, 104, x, 104 - h), (70, 92, 74))
    L(d, (41, 105, 59, 105), (110, 124, 100))
    for k in range(5):                                                        # 落款 + 红印
        P(d, 57, 90 + k * 2, (60, 56, 52))
    R(d, (56, 101, 57, 102), (200, 50, 44))
    # 轴头 + 上轴
    L(d, (37, 116, 63, 116), (60, 40, 26), 2)
    R(d, (35, 115, 36, 117), (226, 214, 186))
    R(d, (64, 115, 65, 117), (226, 214, 186))
    L(d, (36, 40, 64, 40), (60, 40, 26), 2)
    # 床板（木纹）
    R(d, (14, 124, 86, 131), (96, 62, 38))
    L(d, (14, 124, 86, 124), (160, 116, 76))
    grain(d, (15, 126, 85, 130), (96, 62, 38), 21, n=8, dark=0.2, vertical=False)
    # 小香炉
    d.ellipse((22, 118, 31, 124), fill=C((96, 88, 70)), outline=C((60, 54, 44)))
    R(d, (24, 116, 29, 118), (120, 110, 86))
    P(d, 26, 115, (150, 140, 110))
    L(d, (23, 120, 30, 120), (160, 140, 96))
    # 花瓶（薄板、高光）+ 枝
    R(d, (63, 123, 79, 124), (70, 44, 28))
    d.ellipse((66, 110, 76, 124), fill=C((60, 90, 150)), outline=C((30, 40, 70)))
    L(d, (68, 113, 68, 118), (120, 150, 210))
    L(d, (71, 110, 64, 96, 58, 90), (70, 50, 30))
    L(d, (71, 110, 78, 98), (70, 50, 30))
    for (px_, py_) in ((64, 96), (58, 90), (78, 98), (61, 93), (75, 101)):
        P(d, px_, py_, (250, 170, 190))
        P(d, px_ + 1, py_, (250, 200, 210))
    # 床柱：天然木纹 + 节疤
    A._post(d, 84, 35, 132, 5, col=(120, 90, 60))
    for i, y in enumerate(range(40, 130, 9)):
        P(d, 85 + i % 3, y, (98, 70, 44))
        P(d, 85 + (i + 1) % 3, y + 3, (140, 108, 74))
    d.ellipse((85, 98, 87, 101), fill=C((90, 62, 38)))


def fusuma(img):
    d = ImageDraw.Draw(img)
    for i, x0 in enumerate((90, 148)):
        R(d, (x0, 35, x0 + 56, 134), (214, 204, 176), (90, 62, 40))
        R(d, (x0 + 1, 35, x0 + 55, 50), (200, 176, 116))
        for k in range(4):
            cxc = x0 + 8 + k * 14 + (i * 5)
            d.ellipse((cxc - 8, 44, cxc + 8, 54), fill=C((206, 184, 124)))
            d.arc((cxc - 8, 44, cxc + 8, 54), 20, 160, fill=C((176, 150, 90)))
        # 淡墨远山 + 地平
        ink = (180, 172, 150)
        base = 118
        pts = [(x0 + 1, base)]
        for k in range(8):
            pts.append((x0 + 1 + k * 8, base - hrange(6, 20, i, k, 91)))
        pts.append((x0 + 55, base))
        d.polygon(pts, fill=C(mix((214, 204, 176), ink, 0.45)))
        L(d, (x0 + 1, base, x0 + 55, base), mix((214, 204, 176), ink, 0.6))
    # 右扇的松枝
    br = (150, 140, 116)
    L(d, (204, 70, 186, 78, 172, 76, 160, 82), br, 2)
    L(d, (186, 78, 180, 90), br)
    for (cx, cy, r) in ((172, 74, 6), (160, 80, 5), (184, 88, 5), (196, 70, 6)):
        d.ellipse((cx - r, cy - 2, cx + r, cy + 2), fill=C((170, 172, 140)))
        L(d, (cx - r + 1, cy - 2, cx + r - 1, cy - 2), (190, 192, 160))
    A._tex_noise(img, (90, 35, 205, 134), 0.05, 12)
    d = ImageDraw.Draw(img)
    for x0 in (90, 148):                                                     # 黑漆边框
        L(d, (x0, 35, x0, 134), (54, 36, 26))
        L(d, (x0 + 56, 35, x0 + 56, 134), (54, 36, 26))
        L(d, (x0, 133, x0 + 56, 133), (54, 36, 26))
        L(d, (x0 + 1, 36, x0 + 1, 132), (120, 90, 64))
    L(d, (147, 35, 147, 134), (90, 62, 40))
    for (hx, hy) in ((138, 84), (152, 84)):                                  # 拉手：铜圈
        d.ellipse((hx - 1, hy - 1, hx + 5, hy + 7), fill=C((170, 130, 70)))
        d.ellipse((hx, hy, hx + 4, hy + 6), fill=C((110, 80, 50)))
        P(d, hx + 1, hy + 1, (210, 176, 110))


def posts_floor(img):
    d = ImageDraw.Draw(img)
    for x in (8, 200, 312):
        A._post(d, x, 30, 140)
        grain(d, (x + 1, 32, x + 4, 138), (150, 106, 64), x, n=4, dark=0.18)
    R(d, (0, 134, 206, 140), (150, 108, 66))
    L(d, (0, 134, 206, 134), (196, 150, 100))
    L(d, (0, 137, 206, 137), (126, 88, 52))
    L(d, (0, 140, W, 140), (96, 70, 40))
    # 榻榻米 + 织纹 + 边的花纹
    A._tatami(d, img, 140, H, [[40, 120, 200, 280], [80, 160, 240]], seed=1)
    d = ImageDraw.Draw(img)
    for y in range(142, H, 2):
        for x in range((y // 2) % 3, W, 3):
            if hash01(x, y, 97) < 0.35:
                P(d, x, y, (196, 188, 120) if (x + y) % 2 else (170, 162, 98))
    for y in (140, 155):
        for x in range(1, W, 4):
            P(d, x, y + 1, (96, 112, 84))
    # 暗角：长押下 / 门槛下
    A._blend_rect(img, (0, 141, 206, 143), (60, 40, 20), 50)


def table(img):
    d = ImageDraw.Draw(img)
    A._blend_poly(img, [(12, 160), (86, 160), (90, 168), (8, 168)], (60, 40, 20), 70)     # 桌下阴影
    d = ImageDraw.Draw(img)
    d.ellipse((14, 150, 82, 162), fill=C((80, 40, 30)))
    d.ellipse((14, 148, 82, 159), fill=C((122, 56, 40)))
    d.ellipse((20, 149, 60, 154), fill=C((150, 76, 54)))
    d.arc((17, 149, 79, 158), 200, 340, fill=C((170, 96, 66)))
    for (xa, xb, y) in ((26, 44, 152), (50, 72, 155), (30, 52, 156)):
        L(d, (xa, y, xb, y), (108, 48, 34))
    R(d, (22, 159, 25, 170), (70, 36, 26))
    R(d, (70, 159, 73, 170), (70, 36, 26))
    L(d, (22, 159, 22, 170), (100, 56, 40))
    # 一碟仙贝
    d.ellipse((22, 151, 33, 155), fill=C((236, 232, 222)), outline=C((150, 140, 128)))
    d.ellipse((24, 151, 28, 153), fill=C((196, 140, 70)))
    d.ellipse((28, 152, 32, 154), fill=C((180, 120, 56)))
    # 茶壶（侧把）
    d.ellipse((36, 146, 46, 153), fill=C((70, 110, 90)), outline=C((30, 50, 40)))
    L(d, (46, 148, 50, 146), (30, 50, 40))
    L(d, (36, 149, 32, 147), (40, 30, 24), 2)
    R(d, (40, 145, 42, 146), (40, 70, 56))
    P(d, 39, 148, (120, 160, 136))
    # 两杯绿茶
    for cx in (56, 64):
        R(d, (cx, 149, cx + 4, 153), (230, 226, 214), (120, 110, 100))
        L(d, (cx + 1, 149, cx + 3, 149), (140, 170, 90))
    # 坐垫：线结 + 穗子
    d.rounded_rectangle((86, 164, 112, 172), radius=2, fill=C((120, 60, 110)), outline=C((70, 30, 60)))
    L(d, (88, 165, 110, 165), (150, 90, 140))
    R(d, (98, 167, 100, 168), (220, 190, 120))
    for (tx, ty) in ((85, 163), (112, 163), (85, 172), (112, 172)):
        P(d, tx, ty, (220, 190, 120))


@lru_cache(maxsize=4)
def static(variant):
    Pv = A._KJ.get(variant, A._KJ['day'])
    img = A._new(col=(120, 90, 60))
    garden(img, tuple(map(tuple, Pv['sky'])), variant)
    sky = A._new()
    gradient(sky, (206, 34, 318, 100), Pv['sky'], bands=6)
    room(img)
    d = ImageDraw.Draw(img)
    gecko(d)
    tokonoma(img)
    fusuma(img)
    posts_floor(img)
    table(img)
    a_pre = np.array(img)
    skymask = np.all(a_pre[:, :, :3] == np.array(sky)[:, :, :3], axis=2)
    skymask[:, :206] = False
    skymask[:, 299:] = False
    skymask[100:] = False
    if Pv['ta'] > 0 or Pv['val'] != 1.0:
        img = A._grade(img, sat=0.95, val=Pv['val'], tint=Pv['tint'], tint_amt=Pv['ta'])
    if variant == 'night':
        d = ImageDraw.Draw(img)
        a = np.array(img)
        for i in range(22):                                                  # 星星（只落在天空上）
            x, y = int(hrange(208, 298, i, 101)), int(hrange(36, 66, i, 102))
            if skymask[y, x]:
                a[y, x, :3] = (200, 210, 255) if i % 3 else (255, 255, 230)
        img = Image.fromarray(a, 'RGBA')
        d = ImageDraw.Draw(img)
        A._glow(img, 224, 46, 12, 10, (200, 210, 255), 40, rings=3)          # 月亮
        d = ImageDraw.Draw(img)
        d.ellipse((220, 42, 228, 50), fill=C((236, 236, 214)))
        d.ellipse((223, 42, 230, 49), fill=C(tuple(int(v) for v in np.array(img)[44, 231, :3])))
        A._glow(img, 250, 84, 16, 12, (255, 200, 120), 60, rings=3)          # 石灯笼点亮
        d = ImageDraw.Draw(img)
        R(d, (248, 82, 252, 85), (255, 226, 150))
        A._blend_poly(img, [(240, 104), (262, 104), (268, 110), (236, 110)], (255, 190, 110), 30)
    return img


def export(ex, BJ, variant=None):
    variant = variant or ex.key.rsplit('_', 1)[-1]
    Pv = A._KJ[variant]
    base = static(variant).copy()
    if variant == 'day':
        A._blend_poly(base, [(206, 134), (206, 140), (150, 180), (110, 180)], Pv['light'], 30)
    layers = [dict(type='static', image=ex.img('static', base))]
    parts = []

    if variant in ('morning', 'dusk'):
        def beams(t):
            img = BJ.blank()
            a = int(Pv['la'] * (0.85 + 0.15 * math.sin(t * 0.8)))
            A._blend_poly(img, [(206, 60), (206, 134), (120, 180), (60, 180)], Pv['light'], a)
            A._blend_poly(img, [(206, 36), (206, 58), (40, 180), (10, 180)], Pv['light'], a // 2)
            return img
        parts.append(beams)
        layers.append(ex.bake('beams', (10, 36, 207, 180), BJ.BEAM_N, BJ.BEAM_N * 0.8 / (2 * math.pi), beams))

    def furin(t):
        f = BJ.FakeFr(t)
        BJ._furin_loop(f, 262, 40, t)
        return f.img
    parts.append(furin)
    layers.append(ex.bake('furin', (255, 33, 270, 62), int(BJ.FURIN_L * BJ.FURIN_FPS), BJ.FURIN_FPS, furin))
    leaf_col = (110, 150, 70) if variant == 'day' else (250, 190, 200)

    def leaves(t):
        f = BJ.FakeFr(t)
        for i in range(2):
            u = ((t * 0.12 + i * 0.5) % 1.0)
            lx = 300 - u * 80 + math.sin(t * BJ.LEAF_W + i) * 4
            ly = 50 + u * 80
            f.d.point((round(lx), round(ly)), fill=A._c4(leaf_col))
        return f.img
    parts.append(leaves)
    layers.append(ex.bake('leaves', (214, 49, 306, 131), int(round(BJ.LEAF_L * BJ.LEAF_FPS)), BJ.LEAF_FPS, leaves))
    anchors = dict(garden=[206, 34, 318, 134], table=[48, 154], table_box=[14, 146, 82, 170], walk_x=[90, 300],
                   furin=[262, 40], alcove=[14, 35, 86, 128], fusuma=[90, 35, 204, 134])
    st = ex.stage(320, 160, (148, 176), layers, anchors=anchors)
    if ex.check_on:
        boxes = {'beams': (10, 36, 207, 180), 'furin': (255, 33, 270, 62), 'leaves': (214, 49, 306, 131)}
        names = (['beams'] if variant in ('morning', 'dusk') else []) + ['furin', 'leaves']

        strips = {L_['image'].split('/')[-1]: L_ for L_ in layers if L_['type'] == 'strip'}

        def direct(t):
            img = base.copy()
            for nm, fn in zip(names, parts):
                x0, y0, x1, y1 = boxes[nm]
                S_ = strips[nm]
                f = int(math.floor(t * S_['fps'])) % S_['n']           # 帧条按帧取（和 §3.6 一样）
                img.alpha_composite(fn(f / S_['fps']).crop(boxes[nm]), (x0, y0))
            return img
        for t in (0.0, 2.5, 7.3):
            ex.checked('空条家(%s) t=%.1f 导出 vs 直接绘制' % (variant, t),
                       BJ.ndiff_rgba(BJ.ref_render(st, ex.images, 0, t), direct(t)))
        ex.checked('空条家(%s) 底图不透明' % variant, int((np.array(base)[:, :, 3] != 255).sum()))
    return st
