# -*- coding: utf-8 -*-
r"""school_stairs —— 上学路上的长石阶（序-8 / 序-8b，用户 2026-10-09 晚：“在动漫里确实是在一个下楼梯的场景触发的”）。

侧视、640 宽、不循环（游戏层新画，scenes-early 2026-10-10）。从马路对面看过去：左边是一块高台（石垣墙面），
台上是上学的小路；小路尽头一条 20 级的石阶往右下走到马路边的人行道；远处是东京的街景和学校。

人物在石阶上的高度用 z 表示（地图可走带固定 y 150–160，z = 台阶面离人行道多高）：
  x < X0（184）：z = TOP（80，坡顶小路）
  X0 ≤ x < X1（404）：第 i 级（i = (x − X0) // RUN）z = TOP − RISE·(i + 1)
  x ≥ X1：z = 0（人行道）
剧情（story\prologue.js）照 anchors.stairs 的同一组数算 z，背景和人物脚底永远对得上。

图层：
  far    天空 + 云 + 远处街景 + 远处的学校（pano k 0.35，448 宽）
  near   坡顶小路（围墙、房子、樱花、路灯）、石垣、石阶（踏面 + 侧面）、马路、人行道边的围墙 / 电线杆 /
         转角镜 / 自动售货机（pano k 1，640 宽）
  petals 飘落的樱花瓣（同 school_gate）
  fg     近侧扶手：坡顶小路的栏杆 + 顺着石阶往下的钢管扶手（画在人前面，挡住小腿）
锚点：stairs {x0, run, rise, n, top, band}、trip_x（摔倒的那一级）、bottom（摔下来落地）、kakyoin（花京院走过来站的位置）、
      sakura / view / mirror / vending（调查点）、exit_x（往右走去学校）。
单独运行：python -B tools\bg_new\school_stairs.py → tools\bg_new\_preview\school_stairs_solo.png
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
PW = 640                     # 地图宽
FARW = 448                   # 远景宽（k 0.35：镜头 0…320 → 偏移 0…112）
FAR_K = 0.35
BAND = (150, 160)            # 可走纵深带（脚底 y）
GROUND = 156
X0, RUN, RISE, N = 184, 11, 4, 20
TOP = RISE * N               # 80
X1 = X0 + RUN * N            # 404
TRIP_I = 7                   # 第 8 级踩空（x 261–272）
TRIP_X = X0 + RUN * TRIP_I + 4
BOTTOM = (418, 156)          # 滚下来落在人行道上
KAK_AT = (446, 155)
EXIT_X = 612
ROAD_Y = 162                 # 马路（近处）从这一行开始
C = A._c4


def height(x):
    """台阶面离人行道的高度（= 人物的 z）。和 story\\prologue.js 的 stairZ 一个算法。"""
    if x < X0:
        return TOP
    if x >= X1:
        return 0
    i = int((x - X0) // RUN)
    return TOP - RISE * (i + 1)


def nose_line(x):
    """踏面近侧边线（前缘）连成的斜线高度：扶手顺着它走（线性，不取整）。"""
    if x <= X0:
        return TOP
    if x >= X1:
        return 0
    return TOP - (x - X0) / (X1 - X0) * TOP


# ============================================================ 小工具
def _arr(im):
    return np.array(im).astype(np.int16)


def _img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def _put(a, x, y, col, alpha=255):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]:
        if alpha >= 255:
            a[y, x, :3] = col
            a[y, x, 3] = 255
        else:
            k = alpha / 255.0
            a[y, x, :3] = a[y, x, :3] * (1 - k) + np.array(col) * k
            a[y, x, 3] = max(int(a[y, x, 3]), alpha)


def stone_wall(w, h, seed, base=(150, 144, 132), hi=(184, 178, 164), lo=(110, 104, 96), mortar=(84, 80, 74),
               moss=(98, 126, 78), row_h=(5, 7), stone_w=(8, 15)):
    """石垣：错缝的石块（左上亮、右下暗、灰缝深色），偶尔有深色石、青苔。返回 h×w×4 int16。"""
    a = np.zeros((h, w, 4), np.int16)
    a[..., :3] = mortar
    a[..., 3] = 255
    y = 0
    r = 0
    while y < h:
        rh = int(hrange(row_h[0], row_h[1] + 0.99, seed, r, 1))
        x = -int(hrange(0, stone_w[1], seed, r, 2))
        k = 0
        while x < w:
            sw = int(hrange(stone_w[0], stone_w[1] + 0.99, seed, r, k, 3))
            dk = hash01(seed, r, k, 4)
            col = np.array(base, np.float32) * (0.86 + 0.22 * hash01(seed, r, k, 5))
            if dk < 0.12:
                col = col * 0.78
            elif dk > 0.9:
                col = col * 1.08
            x0, x1 = max(0, x + 1), min(w, x + sw)
            y0, y1 = y + 1, min(h, y + rh)
            if x1 > x0 and y1 > y0:
                a[y0:y1, x0:x1, :3] = col
                # 立体：上沿、左沿亮，下沿、右沿暗
                a[y0, x0:x1, :3] = np.minimum(255, col * 0.55 + np.array(hi) * 0.45)
                a[y0:y1, x0, :3] = np.minimum(255, col * 0.7 + np.array(hi) * 0.3)
                a[y1 - 1, x0:x1, :3] = col * 0.62 + np.array(lo) * 0.38
                a[y0:y1, x1 - 1, :3] = col * 0.7 + np.array(lo) * 0.3
                # 石面上的斑点
                for q in range(int((x1 - x0) * (y1 - y0) / 18)):
                    px = x0 + int(hrange(0, x1 - x0, seed, r, k, q, 6))
                    py = y0 + int(hrange(0, y1 - y0, seed, r, k, q, 7))
                    if px < w and py < h:
                        a[py, px, :3] = col * (0.84 if hash01(seed, r, k, q, 8) < 0.5 else 1.1)
            x += sw
            k += 1
        y += rh
        r += 1
    # 青苔：石缝里一小簇一小簇（越靠下越多）
    for q in range(int(w * h / 60)):
        px = int(hrange(0, w, seed, q, 9))
        py = int(hrange(0, h, seed, q, 10) ** 1.0)
        if hash01(seed, q, 11) < 0.25 + 0.5 * (py / max(1, h)):
            if tuple(a[py, px, :3]) == mortar or hash01(seed, q, 12) < 0.3:
                a[py, px, :3] = moss if hash01(seed, q, 13) < 0.6 else (122, 150, 92)
    return a


# ============================================================ 远景
@lru_cache(maxsize=1)
def far_layer():
    im = A._new(FARW, H)
    gradient(im, (0, 0, FARW, 128), [(104, 166, 234), (150, 198, 244), (214, 228, 240), (246, 230, 206)], bands=8)
    d = ImageDraw.Draw(im)
    for i in range(6):
        cl = A._cloud_sprite(int(hrange(26, 58, i, 3)), int(hrange(8, 13, i, 4)), 120 + i)
        im.alpha_composite(cl, (int(hrange(0, FARW - 40, i, 5)), int(hrange(6, 46, i, 6))))
    d = ImageDraw.Draw(im)
    # 远山（淡）
    pts = [(0, 104)]
    for x in range(0, FARW + 8, 8):
        pts.append((x, 98 - 8 * math.sin(x * 0.013 + 1.1) - 4 * math.sin(x * 0.041)))
    pts += [(FARW, 128), (0, 128)]
    d.polygon(pts, fill=C((176, 196, 214)))
    # 远处街景：两排楼，后排更淡
    for row, (base, col, hmin, hmax) in enumerate(((112, (184, 198, 214), 8, 22), (122, (160, 176, 196), 6, 18))):
        x = -4
        i = 0
        while x < FARW:
            w = int(hrange(10, 24, row, i, 1))
            hh = int(hrange(hmin, hmax, row, i, 2))
            d.rectangle((x, base - hh, x + w, 128), fill=C(col))
            d.line((x, base - hh, x + w, base - hh), fill=C(mix(col, (240, 244, 250), 0.4)))
            if hash01(row, i, 3) < 0.7:
                for wy in range(base - hh + 3, base, 4):
                    for wx in range(x + 2, x + w - 1, 4):
                        if hash01(row, i, wx, wy, 4) < 0.55:
                            d.point((wx, wy), fill=C(mix(col, (110, 128, 160), 0.45)))
            if hash01(row, i, 5) < 0.18:                 # 屋顶上的水塔 / 天线
                d.rectangle((x + 3, base - hh - 4, x + 6, base - hh), fill=C(mix(col, (120, 130, 150), 0.3)))
            x += w + int(hrange(0, 4, row, i, 6))
            i += 1
    # 远处的学校（白色校舍 + 钟楼），在镜头往右走时露在人行道围墙上面
    sx0, sx1 = 286, 402
    d.rectangle((sx0, 92, sx1, 128), fill=C((222, 220, 210)))
    d.rectangle((sx0, 90, sx1, 92), fill=C((176, 174, 166)))
    for fl in range(3):
        y = 96 + fl * 9
        for x in range(sx0 + 3, sx1 - 4, 6):
            if 336 <= x <= 352:
                continue
            d.rectangle((x, y, x + 3, y + 4), fill=C((128, 160, 192)))
    d.rectangle((336, 76, 354, 128), fill=C((232, 230, 220)))
    d.rectangle((335, 74, 355, 77), fill=C((176, 174, 166)))
    d.ellipse((340, 79, 350, 89), fill=C((250, 250, 244)), outline=C((90, 92, 100)))
    d.line((345, 84, 345, 81), fill=C((40, 40, 50)))
    d.line((345, 84, 347, 85), fill=C((40, 40, 50)))
    d.rectangle((0, 124, FARW, H), fill=C((168, 184, 196)))                     # 远处街道的地面（一直铺到底，近景的缝里不露黑）
    for y in range(128, H, 5):
        d.line((0, y, FARW, y), fill=C((160, 176, 190)))
    d.rectangle((sx0 - 30, 118, sx1 + 30, 128), fill=C((150, 176, 136)))       # 操场边的树
    for i in range(16):
        bx = sx0 - 30 + i * 11 + int(hrange(-2, 2, i, 7))
        d.ellipse((bx - 6, 112, bx + 6, 122), fill=C((128, 160, 118)))
        if i % 3 == 1:
            d.ellipse((bx - 5, 110, bx + 5, 119), fill=C((236, 180, 200)))   # 校园里的樱花
    im = A._grade(im, sat=0.82, val=0.98)
    return im


# ============================================================ 近景
def _house(d, x0, y0, x1, ybase, wall, roof, seed):
    """坡顶小路后面的民宅：瓦屋顶 + 墙 + 窗。"""
    d.rectangle((x0, y0 + 10, x1, ybase), fill=C(wall))
    d.line((x0, y0 + 10, x1, y0 + 10), fill=C(mix(wall, (255, 255, 255), 0.3)))
    d.polygon([(x0 - 5, y0 + 11), (x0 + 6, y0), (x1 - 6, y0), (x1 + 5, y0 + 11)], fill=C(roof))
    for xx in range(x0 - 3, x1 + 4, 3):                       # 瓦楞
        d.line((xx, y0 + 2, xx, y0 + 10), fill=C(mix(roof, (0, 0, 0), 0.2)))
    d.line((x0 - 5, y0 + 11, x1 + 5, y0 + 11), fill=C(mix(roof, (0, 0, 0), 0.4)))
    d.line((x0 + 6, y0, x1 - 6, y0), fill=C(mix(roof, (255, 255, 255), 0.25)))
    wx = x0 + 6
    while wx + 10 < x1:
        d.rectangle((wx, y0 + 15, wx + 9, y0 + 23), fill=C((96, 116, 132)), outline=C(mix(wall, (0, 0, 0), 0.4)))
        d.line((wx + 4, y0 + 15, wx + 4, y0 + 23), fill=C(mix(wall, (0, 0, 0), 0.3)))
        d.point((wx + 2, y0 + 17), fill=C((200, 220, 236)))
        wx += int(hrange(16, 24, seed, wx))


def _fence(d, x0, x1, ytop, ybase, seed):
    """板塀（深色木板围墙 + 顶上一条横木）。"""
    d.rectangle((x0, ytop, x1, ybase), fill=C((92, 70, 54)))
    for x in range(x0, x1, 3):
        c = (104, 80, 62) if (x // 3) % 2 else (86, 64, 48)
        d.line((x, ytop + 2, x, ybase), fill=C(c))
    d.rectangle((x0 - 1, ytop - 2, x1 + 1, ytop + 1), fill=C((70, 52, 40)))
    d.line((x0 - 1, ytop - 2, x1 + 1, ytop - 2), fill=C((128, 100, 78)))


def _lamp(d, x, ybase, h=44):
    """路灯：灰色杆 + 弯臂 + 灯罩。"""
    d.rectangle((x, ybase - h, x + 1, ybase), fill=C((120, 124, 132)))
    d.line((x + 2, ybase - h, x + 2, ybase), fill=C((88, 92, 100)))
    d.line((x + 1, ybase - h, x + 7, ybase - h - 3), fill=C((120, 124, 132)))
    d.rectangle((x + 6, ybase - h - 3, x + 11, ybase - h - 1), fill=C((90, 94, 104)))
    d.line((x + 6, ybase - h, x + 11, ybase - h), fill=C((250, 244, 214)))


def _pole(d, x, ytop, ybase):
    """电线杆（水泥杆 + 横担 + 变压器 + 广告牌）。"""
    d.rectangle((x, ytop, x + 4, ybase), fill=C((168, 164, 156)))
    d.line((x, ytop, x, ybase), fill=C((196, 192, 184)))
    d.line((x + 4, ytop, x + 4, ybase), fill=C((128, 124, 118)))
    for k in range(ytop + 16, ybase - 10, 7):                 # 脚钉
        d.point((x - 1 if (k // 7) % 2 else x + 5, k), fill=C((90, 90, 96)))
    d.rectangle((x - 10, ytop + 6, x + 14, ytop + 8), fill=C((110, 110, 116)))
    d.rectangle((x - 8, ytop + 16, x + 12, ytop + 17), fill=C((110, 110, 116)))
    for xx in (x - 9, x - 3, x + 7, x + 13):
        d.rectangle((xx, ytop + 3, xx + 1, ytop + 6), fill=C((236, 236, 240)))
    d.rectangle((x + 6, ytop + 22, x + 13, ytop + 34), fill=C((140, 146, 150)), outline=C((96, 100, 104)))
    d.rectangle((x - 3, ybase - 58, x + 7, ybase - 40), fill=C((240, 210, 60)), outline=C((80, 70, 30)))
    for k in range(3):
        d.line((x - 1, ybase - 55 + k * 5, x + 5, ybase - 55 + k * 5), fill=C((60, 50, 30)))


def _mirror(d, x, ybase):
    """转角镜（橙色杆 + 圆镜）。"""
    d.rectangle((x, ybase - 46, x + 1, ybase), fill=C((236, 128, 48)))
    d.line((x + 2, ybase - 46, x + 2, ybase), fill=C((176, 88, 32)))
    d.ellipse((x - 8, ybase - 62, x + 10, ybase - 44), fill=C((236, 128, 48)))
    d.ellipse((x - 6, ybase - 60, x + 8, ybase - 46), fill=C((176, 206, 226)))
    d.arc((x - 5, ybase - 59, x + 6, ybase - 48), 200, 260, fill=C((240, 250, 255)))
    d.point((x + 3, ybase - 50), fill=C((120, 150, 176)))


def _vending(d, x0, ybase):
    """自动售货机（红白，两排饮料样品 + 投币口 + 取物口）。"""
    x1, y0 = x0 + 22, ybase - 42
    d.rectangle((x0, y0, x1, ybase), fill=C((212, 44, 48)), outline=C((96, 20, 24)))
    d.rectangle((x0 + 2, y0 + 2, x1 - 2, y0 + 20), fill=C((236, 240, 244)))
    for r in range(2):
        for k in range(5):
            cx = x0 + 3 + k * 4
            cy = y0 + 4 + r * 8
            col = ((60, 90, 200), (240, 200, 40), (60, 170, 80), (220, 90, 40), (140, 60, 160))[(k + r * 2) % 5]
            d.rectangle((cx, cy, cx + 2, cy + 5), fill=C(col))
            d.point((cx + 1, cy), fill=C((250, 250, 250)))
        d.line((x0 + 3, y0 + 10 + r * 8, x1 - 3, y0 + 10 + r * 8), fill=C((150, 154, 160)))
    d.rectangle((x0 + 3, y0 + 23, x0 + 9, y0 + 27), fill=C((40, 40, 46)))
    d.rectangle((x1 - 7, y0 + 23, x1 - 3, y0 + 30), fill=C((180, 184, 190)))
    d.rectangle((x0 + 3, ybase - 9, x1 - 3, ybase - 4), fill=C((30, 30, 34)))
    d.line((x0 + 1, y0 + 1, x0 + 1, ybase - 1), fill=C((240, 100, 100)))


def tree(d, cx, base_y, r, seed):
    """樱花树：树干从 base_y（树根所在的地面）往上，树冠照 bg_asia._sakura 的画法（它的树干默认长 1.9r）。"""
    A._sakura(d, cx, base_y - r * 1.9, r, seed)


def _block_wall(d, x0, x1, ytop, ybase):
    """人行道后面的水泥砖墙（ブロック塀）+ 一排镂空砖。"""
    d.rectangle((x0, ytop, x1, ybase), fill=C((188, 184, 174)))
    for y in range(ytop + 6, ybase, 6):
        d.line((x0, y, x1, y), fill=C((160, 156, 148)))
        off = 0 if ((y - ytop) // 6) % 2 else 8
        for x in range(x0 + off, x1, 16):
            d.line((x, y - 6, x, y), fill=C((160, 156, 148)))
    yy = ytop + 7
    for x in range(x0 + 4, x1 - 8, 16):                      # 镂空花砖
        d.rectangle((x, yy, x + 8, yy + 4), fill=C((150, 146, 138)))
        d.ellipse((x + 1, yy, x + 7, yy + 4), fill=C((110, 118, 104)))
    d.rectangle((x0, ytop - 2, x1, ytop), fill=C((206, 202, 194)))
    d.line((x0, ybase, x1, ybase), fill=C((132, 128, 120)))


@lru_cache(maxsize=1)
def near_layer():
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    top_far = BAND[0] - TOP          # 70：坡顶小路的远边
    top_near = BAND[1] - TOP + 1     # 81：坡顶小路的近边（石垣从这里开始）
    # ---------------- 坡顶小路后面：房子、板塀、树篱
    _house(d, -6, 18, 58, top_far - 4, (214, 204, 186), (82, 92, 112), 1)
    _house(d, 70, 26, 148, top_far - 4, (226, 220, 204), (128, 74, 60), 2)
    _fence(d, -2, 172, top_far - 22, top_far, 3)
    for i in range(18):                                       # 板塀上面探出来的树篱
        bx = 4 + i * 10 + int(hrange(-2, 2, i, 41))
        d.ellipse((bx - 7, top_far - 30, bx + 7, top_far - 18), fill=C((70, 112, 74)))
        d.ellipse((bx - 5, top_far - 31, bx + 4, top_far - 24), fill=C((96, 140, 90)))
    d.rectangle((120, top_far - 22, 136, top_far), fill=C((122, 96, 70)))     # 板塀上的小木门
    d.rectangle((121, top_far - 20, 135, top_far), fill=C((140, 112, 84)))
    d.line((128, top_far - 20, 128, top_far), fill=C((98, 76, 56)))
    d.point((126, top_far - 10), fill=C((210, 190, 120)))
    d.point((130, top_far - 10), fill=C((210, 190, 120)))
    _lamp(d, 160, top_far, 46)
    tree(d, 92, top_far, 30, 12)                              # 坡顶的大樱花树（树干落在小路远边）
    # ---------------- 坡顶小路的路面（踏面带 y 70–80）：方砖
    d.rectangle((0, top_far, X0 - 1, top_near - 1), fill=C((178, 172, 160)))
    for y in (top_far + 3, top_far + 7):
        d.line((0, y, X0 - 1, y), fill=C((160, 154, 144)))
    for i, (ya, yb) in enumerate(((top_far, top_far + 3), (top_far + 3, top_far + 7), (top_far + 7, top_near - 1))):
        for x in range((i * 5) % 12, X0, 12):
            d.line((x, ya, x, yb), fill=C((160, 154, 144)))
    d.line((0, top_far, X0 - 1, top_far), fill=C((140, 134, 126)))
    d.line((0, top_near - 1, X0, top_near - 1), fill=C((206, 200, 188)))     # 近边路缘石
    tree(d, 238, 84, 24, 13)                                  # 石阶后面的一棵（树干被矮石墙挡住）
    tree(d, 330, 120, 22, 14)
    # ---------------- 石阶后侧的矮石墙（斜顶，跟着台阶往下）
    for x in range(X0 - 2, X1 + 6):
        hh = nose_line(x)
        ytop = int(round(BAND[0] - hh - 9))
        yb = int(BAND[0] - height(min(x, X1 - 1) if x < X1 else x))
        if x >= X1:
            yb = BAND[0]
        d.line((x, ytop, x, yb), fill=C((150, 146, 136)))
        d.point((x, ytop), fill=C((200, 196, 186)))
        d.point((x, ytop + 1), fill=C((176, 172, 162)))
        if (x - X0) % 9 == 0:
            d.line((x, ytop + 2, x, yb), fill=C((128, 124, 116)))
    # ---------------- 石垣（高台的墙面）+ 石阶侧面：先铺满整块石墙，再按台阶轮廓裁
    wall = stone_wall(X1 + 8, ROAD_Y - top_near + 2, 7)
    wa = _arr(im)
    hill_h = wall.shape[0]
    for x in range(0, X1):
        top_y = BAND[1] - height(x) + 1                  # 这一列墙面从哪一行开始（踏面近边下面一行）
        for y in range(top_y, ROAD_Y):
            wy = y - top_near
            if 0 <= wy < hill_h:
                wa[y, x] = wall[wy, x]
    # 石阶侧面（踏面下面这一截）用平整一点的混凝土，每级一块
    for i in range(N):
        xa, xb = X0 + i * RUN, X0 + (i + 1) * RUN
        hz = TOP - RISE * (i + 1)
        ya = BAND[1] - hz + 1
        for x in range(xa, xb):
            for y in range(ya, min(ROAD_Y, ya + RISE + 2)):
                k = 0.95 if (x - xa) in (0,) else 1.0
                wa[y, x, :3] = np.array((150, 146, 138)) * k
                wa[y, x, 3] = 255
            wa[ya, x, :3] = (176, 172, 164)
            wa[min(ROAD_Y - 1, ya + RISE + 1), x, :3] = (118, 114, 108)
    im = _img(wa)
    d = ImageDraw.Draw(im)
    # 石垣上的细节：天端石（顶上一排长条石）、排水孔 + 水渍、常春藤、杂草
    for x in range(0, X0, 13):
        d.rectangle((x, top_near, x + 12, top_near + 3), fill=C((176, 170, 158)))
        d.line((x, top_near, x + 12, top_near), fill=C((206, 200, 188)))
        d.line((x, top_near + 3, x + 12, top_near + 3), fill=C((112, 106, 98)))
        d.line((x + 12, top_near, x + 12, top_near + 3), fill=C((96, 92, 86)))
    for (hx, hy) in ((40, 120), (112, 132), (168, 110)):
        for k in range(3, 26):                                # 排水孔下面的水渍（越往下越淡）
            if hash01(hx, k, 55) < 0.8 - k * 0.025:
                d.point((hx + int(hrange(-2, 2, hx, k, 56)), hy + k), fill=C((112, 110, 104)))
        d.ellipse((hx - 3, hy - 2, hx + 3, hy + 2), fill=C((50, 46, 44)))
        d.point((hx - 1, hy - 1), fill=C((90, 86, 80)))
        d.line((hx - 1, hy + 2, hx - 1, hy + 9), fill=C((92, 100, 96)))
        d.line((hx, hy + 2, hx, hy + 12), fill=C((80, 88, 84)))
    for i in range(46):                                       # 常春藤从坡顶垂下来
        vx = 8 + i * 3.6 + hrange(-1, 1, i, 51)
        if 60 < vx < 92:
            continue
        L = int(hrange(4, 26, i, 52))
        for k in range(L):
            yy = top_near + k
            xx = int(round(vx + math.sin(k * 0.5 + i) * 1.2))
            if xx < X0 and yy < ROAD_Y:
                d.point((xx, yy), fill=C((64, 110, 64) if k % 3 else (98, 150, 84)))
                if k % 4 == 1:
                    d.point((xx + 1, yy), fill=C((120, 168, 96)))
    for i in range(30):                                       # 墙脚的杂草
        gx = int(hrange(0, X1 - 4, i, 53))
        if gx > 404:
            continue
        gh = int(hrange(2, 5, i, 54))
        for k in range(gh):
            d.point((gx + (k % 2), ROAD_Y - 1 - k), fill=C((88, 140, 70)))
    # ---------------- 石阶踏面（每级 11 px 宽、一条 10 px 的纵深带），落着樱花瓣
    for i in range(N):
        xa, xb = X0 + i * RUN, X0 + (i + 1) * RUN - 1
        hz = TOP - RISE * (i + 1)
        y0, y1 = BAND[0] - hz, BAND[1] - hz
        d.rectangle((xa, y0, xb, y1), fill=C((196, 190, 178)))
        d.line((xa, y0, xb, y0), fill=C((164, 158, 148)))               # 远边（靠矮墙，暗）
        d.line((xa, y1, xb, y1), fill=C((222, 216, 204)))               # 近边（踏面前缘，亮）
        d.line((xa, y0, xa, y1), fill=C((150, 144, 134)))               # 和上一级的分界（立面看成一条线）
        for q in range(5):                                              # 石面斑点
            px = xa + 1 + int(hrange(0, RUN - 2, i, q, 61))
            py = y0 + 1 + int(hrange(0, 9, i, q, 62))
            d.point((px, py), fill=C((178, 172, 160) if q % 2 else (210, 204, 192)))
        if i % 4 == 2:                                                  # 有几级缺了一角
            d.point((xb, y1), fill=C((150, 144, 134)))
            d.point((xb - 1, y1), fill=C((176, 170, 158)))
    # 上一级的立面露出来的一截（每级比上一级低 4 px：上一级前缘下面那 4 px 是台阶的竖面）
    for i in range(1, N):
        xa = X0 + i * RUN
        hz_prev = TOP - RISE * i
        y0 = BAND[0] - hz_prev
        d.line((xa, y0, xa, y0 + RISE), fill=C((132, 126, 118)))
    # ---------------- 人行道（台阶下面，纵深带 y 150–160）+ 后面的砖墙、电线杆、转角镜、售货机
    d.rectangle((X1, BAND[0], PW, BAND[1]), fill=C((186, 180, 170)))
    for y in (BAND[0] + 3, BAND[0] + 7):
        d.line((X1, y, PW, y), fill=C((168, 162, 152)))
    for i, (ya, yb) in enumerate(((BAND[0], BAND[0] + 3), (BAND[0] + 3, BAND[0] + 7), (BAND[0] + 7, BAND[1]))):
        for x in range(X1 + (i * 6) % 14, PW, 14):
            d.line((x, ya, x, yb), fill=C((168, 162, 152)))
    d.line((X1, BAND[1], PW, BAND[1]), fill=C((210, 206, 196)))
    d.line((X1, BAND[1] + 1, PW, BAND[1] + 1), fill=C((150, 146, 138)))
    tree(d, 474, 112, 28, 11)                                 # 砖墙后面院子里的樱花
    _block_wall(d, X1 + 6, PW, 112, BAND[0] - 1)
    for i in range(10):                                        # 砖墙上探出来的庭院树
        bx = 452 + i * 19 + int(hrange(-3, 3, i, 71))
        if 500 < bx < 520:
            continue
        d.ellipse((bx - 10, 96, bx + 10, 114), fill=C((74, 118, 76)))
        d.ellipse((bx - 7, 95, bx + 6, 106), fill=C((104, 148, 92)))
    _pole(d, 520, 20, BAND[0])
    _mirror(d, 432, BAND[0] + 1)
    _vending(d, 588, BAND[0])
    # 电线（从电线杆往两边）
    for (ya, yb, sag) in ((26, 30, 6), (29, 34, 7)):
        prev = None
        for s in np.linspace(0, 1, 40):
            xx = 0 + (520 - 0) * s
            yy = ya - 18 + (yb - ya + 18) * s + sag * 4 * s * (1 - s)
            if prev:
                d.line((prev[0], prev[1], round(xx), round(yy)), fill=C((40, 40, 48)))
            prev = (round(xx), round(yy))
        prev = None
        for s in np.linspace(0, 1, 30):
            xx = 524 + (PW + 10 - 524) * s
            yy = yb + 2 + sag * 3 * s * (1 - s)
            if prev:
                d.line((prev[0], prev[1], round(xx), round(yy)), fill=C((40, 40, 48)))
            prev = (round(xx), round(yy))
    # 樱花树下的石柱牌（「石阶」的路标）
    d.rectangle((174, top_far - 20, 179, top_far + 1), fill=C((170, 166, 156)), outline=C((96, 92, 86)))
    d.line((175, top_far - 19, 175, top_far), fill=C((206, 202, 192)))
    for k in range(3):
        d.line((176, top_far - 16 + k * 5, 178, top_far - 16 + k * 5), fill=C((70, 66, 60)))
    # ---------------- 近处的马路（y 162–180，整张都有）
    d.rectangle((0, ROAD_Y, PW, H), fill=C((98, 98, 106)))
    d.line((0, ROAD_Y, PW, ROAD_Y), fill=C((150, 146, 140)))
    d.line((0, ROAD_Y + 1, PW, ROAD_Y + 1), fill=C((120, 120, 126)))
    for x in range(0, PW, 1):
        if hash01(x, 81) < 0.35:
            d.point((x, ROAD_Y + 2 + int(hrange(0, H - ROAD_Y - 3, x, 82))), fill=C((112, 112, 120)))
        if hash01(x, 83) < 0.15:
            d.point((x, ROAD_Y + 2 + int(hrange(0, H - ROAD_Y - 3, x, 84))), fill=C((84, 84, 92)))
    d.line((0, ROAD_Y + 4, PW, ROAD_Y + 4), fill=C((226, 226, 222)))          # 路边白线
    d.ellipse((290, 170, 310, 176), fill=C((84, 84, 92)), outline=C((70, 70, 78)))   # 井盖
    for k in range(3):
        d.line((294 + k * 5, 172, 296 + k * 5, 174), fill=C((106, 106, 112)))
    # 地上 / 台阶上的落花
    for i in range(220):
        x = int(hrange(0, PW, i, 91))
        hz = height(x)
        y0 = BAND[0] - hz
        if i % 3 == 0:
            y = int(hrange(ROAD_Y + 2, H, i, 92))
        else:
            y = int(hrange(y0 + 1, y0 + 10, i, 93))
        d.point((x, y), fill=C((246, 186, 206) if i % 4 else (255, 222, 232)))
    im = A._grade(im, sat=0.9, val=0.99)
    return im


@lru_cache(maxsize=1)
def fg_layer():
    """近侧扶手（画在人前面）：坡顶小路近边的铁栏杆 + 顺着石阶往下的钢管扶手。只到台阶最下一级。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    rail_h = 13
    dark, mid, hi = (54, 58, 68), (92, 98, 110), (168, 174, 186)
    top_near = BAND[1] - TOP + 1
    # 坡顶栏杆（横杆两道 + 立柱）
    y_top = top_near - rail_h
    for x in range(-4, X0 + 1, 16):
        d.rectangle((x, y_top, x + 1, top_near), fill=C(mid))
        d.point((x, y_top), fill=C(hi))
    d.line((-4, y_top, X0, y_top), fill=C(mid))
    d.line((-4, y_top - 1, X0, y_top - 1), fill=C(hi))
    d.line((-4, y_top + 6, X0, y_top + 6), fill=C(dark))
    # 石阶扶手：立柱每 3 级一根，钢管顺着前缘斜线
    posts = [X0 + RUN * k + 5 for k in range(0, N, 3)] + [X1 - 6]
    for px in posts:
        base = BAND[1] - height(px) + 1
        top = int(round(BAND[1] - nose_line(px) + 1 - rail_h))
        d.rectangle((px, top, px + 1, base), fill=C(mid))
        d.point((px + 1, top + 2), fill=C(dark))
    prev = None
    for x in range(X0, X1 - 5):
        y = int(round(BAND[1] - nose_line(x) + 1 - rail_h))
        if prev is not None:
            d.line((prev[0], prev[1] - 1, x, y - 1), fill=C(hi))
            d.line((prev[0], prev[1], x, y), fill=C(mid))
            d.line((prev[0], prev[1] + 1, x, y + 1), fill=C(dark))
        prev = (x, y)
    # 坡顶栏杆和石阶扶手接上（拐角）
    d.line((X0 - 2, y_top - 1, X0 + 2, y_top - 1), fill=C(hi))
    return im


def build():
    return far_layer(), near_layer(), fg_layer()


def export(ex, BJ):
    far, near, fg = build()
    petals = dict(type='petals', n=24, colors=['#f4a0be', '#ffd6e4'], seed=37, y0=-6, y1=184,
                  vx=-12.7, vy=34.5, per=[4.0, 7.0], x0=[-20, W + 60], drift=70, sway=6, swayW=2.3, k=0.2, wrapX=40)
    layers = [dict(type='pano', image=ex.img('far', far), k=FAR_K, x=0, y=0),
              dict(type='pano', image=ex.img('near', near), k=1.0, x=0, y=0),
              petals]
    fcrop_box = fg.getbbox()
    fy0 = fcrop_box[1] if fcrop_box else 0
    fgc = fg.crop((0, fy0, PW, fcrop_box[3] if fcrop_box else H))
    fgl = [dict(type='pano', image=ex.img('rail', fgc), k=1.0, x=0, y=fy0)]
    anchors = dict(stairs=dict(x0=X0, run=RUN, rise=RISE, n=N, top=TOP, x1=X1, band=list(BAND)),
                   trip_x=TRIP_X, bottom=list(BOTTOM), kakyoin=list(KAK_AT), exit_x=EXIT_X,
                   sakura=[96, 74], view=[176, 70], mirror=[432, 104], vending=[599, 130], walk_x=[12, 628])
    st = ex.stage(PW, GROUND, BAND, layers, fgl, anchors)
    if ex.check_on:
        a = np.array(near)[..., 3]
        ex.checked('近景层整张不透明（没有露出远景的洞，天空除外）', int((a[ROAD_Y:, :] < 255).sum()))
        bad = 0
        for camX in (0, 100, 200, 320):
            im = np.array(BJ.ref_render(st, ex.images, camX, 0.0, fg=True, only={'pano'}).convert('RGB'))
            bad += int((im.sum(-1) == 0).sum())
        ex.checked('camX 0…320 整屏都有画（没有露黑）', bad)
        # 台阶踏面和 height() 对得上：每级踏面中点那一列，纵深带上沿 y = 150 − z 是踏面颜色
        miss = 0
        na = np.array(near.convert('RGB')).astype(int)
        for i in range(N):
            x = X0 + i * RUN + RUN // 2
            y = BAND[0] - height(x) + 4
            if abs(int(na[y, x].sum()) - sum(near.getpixel((X0 + RUN // 2, BAND[0] - height(X0 + RUN // 2) + 4))[:3])) > 120:
                miss += 1
        ex.checked('20 级踏面都在 height(x) 算出来的高度上', miss)
    return st


if __name__ == '__main__':
    far, near, fg = build()
    for camX in (0, 160, 320):
        out = Image.new('RGBA', (W, H))
        out.alpha_composite(far.crop((int(camX * FAR_K), 0, int(camX * FAR_K) + W, H)))
        out.alpha_composite(near.crop((camX, 0, camX + W, H)))
        out.alpha_composite(fg.crop((camX, 0, camX + W, H)))
        os.makedirs(os.path.join(HERE, '_preview'), exist_ok=True)
        out.convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(HERE, '_preview', 'school_stairs_solo_%d.png' % camX))
    print('ok')
