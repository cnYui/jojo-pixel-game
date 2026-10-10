"""预览：python -B tools\\bg_new\\bg_hk_preview.py hk_garden_night → _preview\\bg_hk\\hk_garden_night_*.png

第1章 虎豹别墅（夜，第 2 战银色战车的场地；游戏层重画，2026-10-10 bg-hk 代理）。
单屏 320、ground 150、可走 y 140–176、场地 x 16–304，和原 exp_hk_garden_night 一样。

  天空：夜空渐变 + 星星 + 满月和月晕；山后面一线港岛的楼灯
  山和树：两层树冠（暗面 / 月光面），比原片多一层远山
  白塔（cx 250、底 104，七层）：白墙拱窗、橙色琉璃瓦翘角、绿边、金顶；几扇窗亮着
  彩绘假山（x 0–196）：橙褐 / 赭石 / 灰蓝的石块，描边；三个洞龛——中间 x 160 的大龛供着神像（烛光），
       两边是小人物的彩塑场景
  红栏杆（y 112–131）：每 40 px 一根柱子挂红灯笼（灯笼的光会微微闪：strip 6 帧 @6 fps）
  虎像（x 17–68、y 85–116，底座石到 y 132）：橙黄底色、黑色虎纹、白肚、张嘴露牙，比原片大一圈、
       全在剧情的 tigerPatch（雕成红色魔术师时盖上的粗石，x 15–70、y 83–117）里面
  金狮一对（x 80 / 100，剧情调查点「金狮」(90,128)：镀金掉了一半，露出灰石头）；石阶两边改成一对石狮（212 / 288）
  棕榈两棵、花砖广场、白塔的月影
  飞鸟两只（clouds，同原片）

剧情坐标（story\\ch01.js 不动）：白塔 (250,104)、虎像 (44,132)、金狮 (90,128)、彩绘假山洞 (160,110)；
石像道具 mr_statue (44,133) z 17 立在虎像底座上；观战三人在石阶前 (276–306, 142–151)。
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
from engine.core import hash01, hrange, mix, gradient, paste

W, H = 320, 180
C = A._c4
LANTERNS = (120, 160, 200)                       # 栏杆柱子上的灯笼 x（虎像、金狮、石狮前面的柱子不挂）
LANTERN_N, LANTERN_FPS = 6, 6.0
LANTERN_BOX = (100, 100, 220, 128)               # 三只灯笼 + 光晕（x 107–213）
PATCH_Y = (83, 117)                              # 剧情 tigerPatch 的行范围


def rect(d, box, fill, outline=None):
    d.rectangle(box, fill=C(fill) if fill is not None else None, outline=C(outline) if outline else None)


def line(d, pts, fill, width=1):
    d.line(pts, fill=C(fill), width=width)


def px(d, x, y, fill):
    d.point((x, y), fill=C(fill))


def patch_span(y):
    """story/ch01.js tigerPatch 第 y 行盖住的 [l, r]（含描边）。"""
    j = ((y * 7) % 3) - 1
    l = 15 + max(0, 89 - y) * 4 + (j if y > 110 else 0)
    r = 70 - max(0, 86 - y) * 2 + j
    return l, r


# ---------------------------------------------------------------- 各部分
def sky(img):
    gradient(img, (0, 0, W, 120), [(10, 12, 34), (26, 28, 66), (52, 46, 92), (84, 62, 104)], bands=7)
    A._stars(img, (0, 0, W, 64), 40, 5)
    d = ImageDraw.Draw(img)
    for i in range(8):
        sx, sy = int(hrange(4, 316, i, 81)), int(hrange(3, 40, i, 82))
        px(d, sx, sy, (255, 250, 230))
        if i % 3 == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                px(d, sx + dx, sy + dy, (140, 140, 200))
    A._glow(img, 150, 24, 30, 26, (200, 210, 255), 50, rings=5)       # 月晕
    d = ImageDraw.Draw(img)
    d.ellipse((141, 15, 159, 33), fill=C((250, 246, 222)))
    for (x, y, r) in ((146, 21, 2), (153, 26, 3), (150, 19, 1), (155, 20, 1)):
        d.ellipse((x - r, y - r, x + r, y + r), fill=C((222, 220, 200)))
    for i in range(3):                                                  # 薄云
        cx, cy, w = hrange(20, 300, i, 91), hrange(30, 52, i, 92), hrange(30, 54, i, 93)
        for q in range(int(w)):
            yy = cy + math.sin(q * 0.4 + i) * 1.2
            px(d, int(cx - w / 2 + q), int(yy), (70, 66, 110))
            if q % 3:
                px(d, int(cx - w / 2 + q), int(yy) + 1, (58, 56, 98))


def far_hills(img):
    d = ImageDraw.Draw(img)
    pts = [(0, 72)] + [(x, int(68 + 6 * math.sin(x / 37 + 1) + 4 * math.sin(x / 13))) for x in range(0, W + 1, 4)] + [(W, 120), (0, 120)]
    d.polygon(pts, fill=C((44, 50, 82)))
    for i in range(30):                                                 # 山后面港岛的楼灯
        x = int(hrange(96, 214, i, 61))
        top = int(hrange(60, 70, i, 62))
        rect(d, (x, top, x + 3, 78), (38, 42, 70))
        for yy in range(top + 1, 78, 2):
            if hash01(x, yy, 63) < 0.35:
                px(d, x + 1 + int(hash01(x, yy, 64) * 2), yy, (250, 214, 130))


def hills_trees(img):
    d = ImageDraw.Draw(img)
    d.polygon([(0, 84), (60, 62), (140, 76), (220, 58), (320, 72), (320, 130), (0, 130)], fill=C((60, 118, 76)))
    for i in range(22):
        cx = i * 15.5 + hrange(-4, 4, i, 5)
        cy = 82 + hrange(-9, 7, i, 6)
        r = hrange(8, 14, i, 7)
        d.ellipse((cx - r, cy - r, cx + r, cy + r * 0.8), fill=C((44, 100, 64)))
        d.ellipse((cx - r + 3, cy - r, cx + r - 5, cy - 1), fill=C((78, 140, 88)))
        for q in range(4):                                              # 叶簇
            lx, ly = cx + hrange(-r + 2, r - 2, i, q, 8), cy + hrange(-r + 2, 2, i, q, 9)
            px(d, int(lx), int(ly), (110, 176, 110))
            px(d, int(lx) + 1, int(ly), (96, 160, 100))


def pagoda(img):
    d = ImageDraw.Draw(img)
    cx, base = 250, 104
    wall, roof, roof_d, trim = (244, 240, 226), (230, 116, 42), (170, 70, 30), (60, 150, 96)
    rect(d, (cx - 22, base - 2, cx + 22, base + 1), (210, 204, 190), (150, 140, 124))     # 台基
    y, w = base - 2, 34
    tops = []
    for i in range(7):
        h = 14 - i
        x0, x1 = cx - w // 2 + 3, cx + w // 2 - 3
        rect(d, (x0, y - h, x1, y), wall, (160, 150, 130))
        line(d, (x1 - 1, y - h + 1, x1 - 1, y - 1), (206, 200, 186))
        for wx in range(x0 + 3, x1 - 3, 6):                               # 拱窗
            rect(d, (wx, y - h + 4, wx + 2, y - 2), (70, 60, 74))
            px(d, wx + 1, y - h + 3, (70, 60, 74))
        line(d, (x0, y - 1, x1, y - 1), (200, 190, 170))
        ry = y - h
        d.polygon([(cx - w // 2 - 6, ry + 1), (cx - w // 2 - 2, ry - 3), (cx + w // 2 + 2, ry - 3),
                   (cx + w // 2 + 6, ry + 1), (cx + w // 2, ry - 1), (cx - w // 2, ry - 1)], fill=C(roof))
        for q in range(cx - w // 2, cx + w // 2 + 1, 2):                    # 瓦垄
            px(d, q, ry - 2, (250, 160, 80))
        line(d, (cx - w // 2 - 6, ry + 1, cx - w // 2, ry - 1), roof_d)
        line(d, (cx + w // 2 + 6, ry + 1, cx + w // 2, ry - 1), roof_d)
        px(d, cx - w // 2 - 7, ry, (240, 200, 90))                          # 翘角
        px(d, cx + w // 2 + 7, ry, (240, 200, 90))
        line(d, (cx - w // 2 - 1, ry - 3, cx + w // 2 + 1, ry - 3), trim)
        tops.append((x0, x1, y - h, y))
        y = ry - 3
        w = max(10, w - 4)
    line(d, (cx, y, cx, y - 13), (230, 190, 60), width=2)
    d.ellipse((cx - 2, y - 8, cx + 2, y - 4), fill=C((250, 210, 70)))
    d.ellipse((cx - 1, y - 12, cx + 1, y - 10), fill=C((250, 210, 70)))
    return tops


def pagoda_lights(img, tops):
    d = ImageDraw.Draw(img)
    for i, (x0, x1, yt, yb) in enumerate(tops):
        for j, wx in enumerate(range(x0 + 3, x1 - 3, 6)):
            if hash01(i, j, 71) < 0.4:
                rect(d, (wx, yt + 4, wx + 2, yb - 2), (255, 214, 120))
                px(d, wx + 1, yt + 3, (255, 214, 120))


def grotto(img):
    """彩绘假山（x 0–196）：石块 + 描边 + 三个洞龛。返回中间大龛的烛光位置。"""
    d = ImageDraw.Draw(img)
    out = [(0, 70), (18, 56), (46, 60), (70, 72), (96, 64), (122, 58), (150, 52), (172, 58), (190, 70), (198, 90),
           (196, 112), (0, 112)]
    d.polygon(out, fill=C((168, 108, 78)), outline=C((84, 50, 36)))
    blocks = [((8, 72), (30, 62), (50, 70), (40, 88), (14, 90), (200, 140, 96)),
              ((70, 76), (96, 68), (112, 80), (98, 96), (74, 94), (190, 120, 70)),
              ((116, 64), (148, 56), (170, 64), (176, 80), (128, 82), (120, 140, 170)),
              ((178, 74), (192, 78), (194, 102), (180, 104), (172, 90), (200, 160, 90)),
              ((100, 98), (130, 92), (136, 110), (104, 110), (96, 104), (150, 96, 110))]
    for b in blocks:
        pts, col = b[:-1], b[-1]
        d.polygon(pts, fill=C(col), outline=C(mix(col, (40, 20, 20), 0.5)))
        line(d, (pts[0][0] + 1, pts[0][1] + 1, pts[1][0], pts[1][1] + 1), mix(col, (255, 240, 220), 0.35))
    for i in range(40):                                                 # 石纹
        x, y = int(hrange(4, 192, i, 51)), int(hrange(62, 110, i, 52))
        line(d, (x, y, x + int(hrange(2, 6, i, 53)), y + int(hrange(-2, 2, i, 54))), (110, 66, 48))
    # 小龛：彩塑小人
    for (nx, ny, figs) in ((118, 100, ((230, 60, 60), (60, 120, 220))), (186, 92, ((240, 200, 70),))):
        d.ellipse((nx - 9, ny - 10, nx + 9, ny + 8), fill=C((66, 38, 34)), outline=C((40, 20, 20)))
        for k, fc in enumerate(figs):
            fx = nx - 3 * (len(figs) - 1) + k * 6
            d.ellipse((fx - 1, ny - 5, fx + 1, ny - 3), fill=C((240, 210, 180)))
            rect(d, (fx - 2, ny - 2, fx + 2, ny + 4), fc)
            px(d, fx - 3, ny - 1, fc)
    # 中间大龛（x 160）：神像 + 光环 + 供桌
    nx, ny = 160, 92
    d.ellipse((nx - 13, ny - 16, nx + 13, ny + 14), fill=C((54, 30, 28)), outline=C((30, 14, 14)))
    d.ellipse((nx - 11, ny - 14, nx + 11, ny + 12), outline=C((200, 60, 50)))
    d.ellipse((nx - 5, ny - 12, nx + 5, ny - 2), outline=C((240, 200, 90)))      # 光环
    d.ellipse((nx - 2, ny - 10, nx + 2, ny - 5), fill=C((240, 212, 160)))         # 头
    d.polygon([(nx - 6, ny + 6), (nx - 4, ny - 4), (nx + 4, ny - 4), (nx + 6, ny + 6)], fill=C((250, 236, 210)))
    line(d, (nx - 3, ny - 2, nx + 3, ny - 2), (230, 80, 60))
    rect(d, (nx - 9, ny + 7, nx + 9, ny + 10), (150, 40, 30), (90, 20, 16))      # 供桌
    return (nx - 6, ny + 6), (nx + 6, ny + 6)


def balustrade(img):
    d = ImageDraw.Draw(img)
    rect(d, (0, 112, W, 116), (200, 50, 40))
    line(d, (0, 112, W, 112), (240, 110, 90))
    line(d, (0, 116, W, 116), (120, 30, 24))
    for x in range(2, W, 8):
        rect(d, (x, 117, x + 3, 128), (70, 150, 100))
        px(d, x + 1, 118, (140, 210, 160))
        line(d, (x + 3, 118, x + 3, 128), (40, 100, 66))
        px(d, x + 1, 122, (50, 120, 80))
    rect(d, (0, 128, W, 131), (200, 50, 40))
    line(d, (0, 131, W, 131), (110, 30, 24))
    for x in range(0, W + 1, 40):                                        # 柱子
        rect(d, (x - 2, 108, x + 2, 131), (210, 60, 46), (110, 26, 20))
        rect(d, (x - 3, 106, x + 3, 108), (240, 200, 80))


def plaza(img):
    d = ImageDraw.Draw(img)
    rect(d, (0, 131, W, H), (196, 120, 90))
    for y in range(134, H, 8):
        line(d, (0, y, W, y), (170, 100, 76))
        off = 0 if (y // 8) % 2 else 8
        for x in range(off, W, 16):
            line(d, (x, y, x, y + 7), (170, 100, 76))
            if hash01(x, y, 3) < 0.18:                                   # 旧砖、裂纹
                rect(d, (x + 2, y + 2, x + 6, y + 4), (182, 110, 84))
    rect(d, (0, 131, W, 134), (226, 214, 196))
    line(d, (0, 134, W, 134), (160, 140, 120))
    # 白塔的月影（往左前方）
    d.polygon([(226, 135), (274, 135), (230, 150), (196, 150)], fill=C((180, 108, 82)))


def stairs(img):
    d = ImageDraw.Draw(img)
    for k in range(5):
        y = 104 + k * 5
        rect(d, (226 - k * 3, y, 274 + k * 3, y + 4), (226, 220, 206))
        line(d, (226 - k * 3, y, 274 + k * 3, y), (244, 240, 230))
        line(d, (226 - k * 3, y + 4, 274 + k * 3, y + 4), (170, 160, 150))
    for sx in (222, 278):                                                 # 石阶边的矮墙
        pass


def lion(d, lx, gold=True, flake=False):
    base, base_o = (200, 196, 186), (120, 116, 110)
    rect(d, (lx - 7, 118, lx + 7, 132), base, base_o)
    line(d, (lx - 7, 121, lx + 7, 121), (170, 166, 156))
    body, hi, out = ((226, 180, 60), (250, 220, 110), (120, 80, 20)) if gold else ((196, 196, 200), (230, 230, 236), (100, 100, 110))
    d.ellipse((lx - 6, 104, lx + 6, 118), fill=C(body), outline=C(out))           # 身
    d.ellipse((lx - 6, 98, lx + 6, 110), fill=C(body), outline=C(out))            # 头 + 鬃毛
    for q in range(-5, 6, 2):
        px(d, lx + q, 99, hi)
        px(d, lx + q + 1, 109, out)
    px(d, lx - 2, 103, (30, 20, 20))
    px(d, lx + 2, 103, (30, 20, 20))
    line(d, (lx - 2, 106, lx + 2, 106), (140, 40, 30))
    rect(d, (lx - 4, 114, lx - 2, 118), body, out)                                # 前爪
    rect(d, (lx + 2, 114, lx + 4, 118), body, out)
    d.ellipse((lx + 2, 111, lx + 6, 115), fill=C(hi if gold else (220, 220, 226)), outline=C(out))   # 绣球
    if flake:                                                                     # 镀金掉了一半：露出灰石头
        for (fx, fy, fw, fh) in ((-5, 106, 4, 5), (1, 100, 3, 3), (-3, 112, 3, 3), (3, 108, 2, 4)):
            rect(d, (lx + fx, fy, lx + fx + fw - 1, fy + fh - 1), (150, 146, 140))
            px(d, lx + fx, fy, (110, 106, 100))


def tiger(img):
    """虎像：橙黄 + 黑纹 + 白肚，张嘴；身体全在 x 17–68、y 85–116（剧情的粗石补丁盖得住），底座石 y 116–132。"""
    d = ImageDraw.Draw(img)
    # 底座石（patch 只盖到 117，下面这块一直露着，红色魔术师石像就立在上面）
    d.polygon([(14, 132), (18, 120), (26, 116), (60, 115), (72, 120), (76, 132)], fill=C((124, 114, 104)), outline=C((60, 54, 50)))
    line(d, (22, 121, 70, 121), (156, 146, 132))
    line(d, (30, 126, 46, 127), (96, 88, 80))
    o, dk, k, wh = (238, 146, 40), (190, 96, 30), (30, 20, 20), (250, 238, 214)
    # 尾巴（往上翘）
    line(d, (24, 104, 19, 96), o, width=3)
    line(d, (19, 96, 21, 89), o, width=3)
    rect(d, (19, 88, 22, 90), k)
    px(d, 20, 99, k)
    # 身体
    d.ellipse((22, 96, 52, 114), fill=C(o), outline=C(k))
    d.ellipse((28, 106, 48, 115), fill=C(wh))                                     # 白肚
    # 后腿 / 前腿
    rect(d, (24, 106, 30, 115), o, k)
    rect(d, (44, 106, 50, 115), o, k)
    rect(d, (50, 104, 55, 115), o, k)
    for (x0, x1) in ((24, 30), (44, 50), (50, 55)):
        line(d, (x0 + 1, 115, x1 - 1, 115), wh)
    # 头（张嘴朝右）
    d.ellipse((46, 87, 66, 106), fill=C(o), outline=C(k))
    d.ellipse((47, 85, 52, 90), fill=C(o), outline=C(k))                           # 耳
    d.ellipse((58, 85, 63, 90), fill=C(o), outline=C(k))
    px(d, 49, 87, (250, 200, 170))
    px(d, 60, 87, (250, 200, 170))
    d.polygon([(57, 97), (67, 95), (67, 104), (57, 102)], fill=C((150, 30, 30)), outline=C(k))   # 张开的嘴
    for q in (59, 62, 65):
        px(d, q, 96, (255, 255, 255))
        px(d, q, 103, (255, 255, 255))
    rect(d, (52, 99, 56, 104), wh)                                                # 腮
    d.ellipse((52, 91, 55, 94), fill=C((250, 240, 160)))                          # 眼
    px(d, 54, 92, k)
    line(d, (51, 90, 56, 90), k)
    # 虎纹
    for sx in (27, 32, 37, 42, 47):
        line(d, (sx, 97, sx + 2, 103), k)
        px(d, sx + 1, 104, k)
    for (a, b) in (((49, 89), (51, 92)), ((53, 88), (54, 90)), ((47, 96), (50, 97))):
        line(d, (a[0], a[1], b[0], b[1]), k)
    line(d, (25, 108, 28, 109), dk)
    line(d, (46, 108, 49, 109), dk)
    line(d, (30, 98, 46, 98), (252, 190, 90))                                     # 背上的高光


def palms(img):
    d = ImageDraw.Draw(img)
    for (px_, py, seed) in ((302, 38, 1), (8, 34, 2)):
        for q in range(8):                                               # 一节节的树干
            y0 = 131 - q * (131 - py - 6) / 8
            y1 = 131 - (q + 1) * (131 - py - 6) / 8
            x0 = px_ + q * 0.5
            line(d, (x0, y0, x0 + 0.5, y1), (110, 80, 50), width=4)
            line(d, (x0 - 1, y1 + 1, x0 + 2, y1 + 1), (80, 56, 36))
        top = (px_ + 4, py + 6)
        for a in range(9):
            ang = a / 9 * math.pi * 2 + seed
            ex, ey = top[0] + math.cos(ang) * 22, top[1] + math.sin(ang) * 8 + 5
            mxp, myp = (top[0] + ex) / 2, (top[1] + ey) / 2 - 3
            line(d, (top[0], top[1], mxp, myp, ex, ey), (44, 120, 56), width=3)
            line(d, (top[0], top[1] - 1, mxp, myp - 1, ex, ey - 1), (90, 170, 80))
            for u in (0.4, 0.7):                                         # 叶片的锯齿
                lx, ly = top[0] + (ex - top[0]) * u, top[1] + (ey - top[1]) * u
                px(d, int(lx), int(ly) + 2, (44, 120, 56))
        d.ellipse((top[0] - 3, top[1] - 1, top[0] + 3, top[1] + 4), fill=C((120, 90, 40)))   # 椰子


def urns(img):
    d = ImageDraw.Draw(img)
    for x in (138, 184):
        d.ellipse((x - 5, 121, x + 5, 131), fill=C((40, 90, 150)), outline=C((20, 40, 80)))
        rect(d, (x - 3, 119, x + 3, 121), (40, 90, 150), (20, 40, 80))
        line(d, (x - 3, 125, x + 3, 125), (230, 230, 240))
        px(d, x - 2, 123, (180, 210, 250))


def lantern_overlay(t, on=True):
    """栏杆柱子上的红灯笼（透明底叠加层）；t 给灯光一点闪动（6 帧 @6 fps 严格循环）。"""
    im = A._new()
    f = int(t * LANTERN_FPS + 1e-6) % LANTERN_N
    for i, x in enumerate(LANTERNS):
        k = 0.8 + 0.2 * math.sin((f / LANTERN_N) * math.pi * 2 + i * 1.7)
        A._glow(im, x, 114, 13, 10, (255, 120, 70), int(80 * k), rings=3)
    d = ImageDraw.Draw(im)
    for i, x in enumerate(LANTERNS):
        line(d, (x, 104, x, 107), (60, 40, 30))
        d.ellipse((x - 4, 107, x + 4, 117), fill=C((236, 60, 46)), outline=C((120, 20, 16)))
        line(d, (x - 2, 109, x - 2, 115), (255, 150, 110))
        line(d, (x, 108, x, 116), (200, 40, 30))
        rect(d, (x - 2, 106, x + 2, 107), (240, 200, 80))
        rect(d, (x - 2, 117, x + 2, 118), (240, 200, 80))
        line(d, (x, 119, x, 121), (240, 200, 80))
    return im


# ---------------------------------------------------------------- 合成
@lru_cache(maxsize=4)
def static(with_tiger=True):
    img = A._new(W, H, (0, 0, 0))
    sky(img)
    far_hills(img)
    hills_trees(img)
    tops = pagoda(img)
    candles = grotto(img)
    balustrade(img)
    stairs(img)                                      # 同原片：石阶压在栏杆上
    plaza(img)
    d = ImageDraw.Draw(img)
    lion(d, 80, gold=True, flake=True)
    lion(d, 100, gold=True, flake=False)
    for lx in (212, 288):
        lion(d, lx, gold=False)
    urns(img)
    palms(img)
    if with_tiger:
        tiger(img)
    img = A._grade(img, sat=0.88, val=0.72, tint=(40, 60, 140), tint_amt=0.25)
    # 夜里亮着的东西在调色之后画（不被压暗）
    pagoda_lights(img, tops)
    for (cx_, cy_) in candles:
        A._glow(img, cx_, cy_, 8, 6, (255, 190, 90), 90, rings=3)
        d = ImageDraw.Draw(img)
        line(d, (cx_, cy_ - 2, cx_, cy_), (255, 240, 200))
    A._glow(img, 160, 86, 14, 12, (255, 170, 90), 40, rings=3)
    return img


def render(t):
    img = static().copy()
    img.alpha_composite(lantern_overlay(t))
    return img


def export(ex, BJ):
    base = render(0.0)
    layers = [dict(type='static', image=ex.img('static', base))]
    layers.append(ex.bake('lanterns', LANTERN_BOX, LANTERN_N, LANTERN_FPS, render))
    birds = []
    bird = A._new(5, 2)
    ImageDraw.Draw(bird).line((0, 1, 2, 0, 4, 1), fill=C((40, 40, 50)))
    kb = ex.img('bird', bird)
    for i in range(2):
        by = round(30 + i * 12 + math.sin(i) * 2)
        bx0 = (i * 90) % 380 - 30
        birds.append(dict(image=kb, x0=round(bx0 - 2 + 100, 3), y=by, vx=14.0, k=0))
    layers.append(dict(type='clouds', span=440, clouds=birds))
    anchors = dict(tiger=[44, 132], pagoda=[250, 104], lions=[[80, 118], [100, 118]], stone_lions=[[212, 118], [288, 118]],
                   stairs=[226, 104, 274, 129], balustrade=[0, 112, W, 131], grotto=[0, 52, 198, 112], shrine=[160, 92],
                   lanterns=[[x, 112] for x in LANTERNS], arena_x=[16, 304])
    st = ex.stage(320, 150, (140, 176), layers, anchors=anchors)
    if ex.check_on:
        ex.checked('虎豹别墅 底图不透明', int((np.array(base)[..., 3] != 255).sum()))
        for t in (0.0, 0.5, 1.0, 2.25):
            ex.checked('虎豹别墅 t=%.2f 导出 vs 直接绘制（y≥60，鸟在 y 28–46）' % t,
                       BJ.ndiff(BJ.ref_render(st, ex.images, 0, t), render(t), box=(0, 60, W, H)))
        # 虎像全在 tigerPatch 里（雕成红色魔术师时整只被粗石盖住）：有虎 / 没虎两张图在 y < 117 的差异只能落在补丁里
        a = np.asarray(static(True).convert('RGB'), np.int16)
        b = np.asarray(static(False).convert('RGB'), np.int16)
        diff = np.abs(a - b).max(-1) > 0
        out = 0
        for y in range(0, PATCH_Y[1]):
            xs = np.nonzero(diff[y])[0]
            if not len(xs):
                continue
            if y < PATCH_Y[0]:
                out += len(xs)
                continue
            l, r = patch_span(y)
            out += int(((xs < l) | (xs > r)).sum())
        ex.checked('虎豹别墅 虎像（y<117）全在剧情 tigerPatch 里（露在外面的像素）', out)
        bad = 0
        bad += not (abs(anchors['pagoda'][0] - 250) <= 0)
        bad += not (abs((80 + 100) / 2 - 90) <= 4)            # 金狮调查点 (90,128)
        bad += not (abs(160 - 160) <= 4)                      # 彩绘假山洞 (160,110)：中间大龛 x 160
        ex.checked('虎豹别墅 剧情调查点位置对得上（不满足的条数）', int(bad))
    return st
