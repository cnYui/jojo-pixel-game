# 第四部第10章（送电铁塔 / 铁塔与谜）的背景：4 张新图，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   transmission_tower 送电铁塔（竖向：320 宽、往上卷 360，图高 540）、miyamoto_house 宫本的屋子（480）、
#   paper_world 纸里的世界（480）、library 杜王町图书馆一角（320）。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_ch10.json（build_p4.py 会把 _meta/bg_*.json 并进背景表）。
#   用法：python3 第四部/tools/art/p4_bg_ch10.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   图层 pack 一律 'ch10'（打包成 data/img_bg_ch10.js，进第10章时才加载）。
#   本章别的场景沿用别章的图：morioh_map、higashikata_living（序章）、crop_field、hospital（第9章）、morioh_avenue（第7章）。
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import liv_floor, preview, save_layers  # noqa: E402

PACK = 'ch10'
_rect = rect


def rect(d, box, col, outline=None):  # noqa: F811
    """同 p4_bglib.rect，坐标先排好序（倒着写的框也能画）"""
    x0, y0, x1, y1 = box
    _rect(d, (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), col, outline)


def poly(d, pts, col):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=C(col))


def kanji(im, x, y, text, col, vertical=False, size=12):
    """文泉驿点阵正黑 12 px 点阵字（告示、招牌用）；vertical = 竖排。返回 (宽, 高)"""
    if vertical:
        cy, w = y, 0
        for ch in text:
            m = LIB.text_mask(ch, LIB.WQY, size, index=1)
            im.paste(C(col), (int(x + (size - m.width) // 2), int(cy)), m)
            cy += m.height + 1
            w = max(w, m.width)
        return w, cy - y - 1
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    im.paste(C(col), (int(x), int(y)), m)
    return m.width, m.height


def kanji_w(text, size=12):
    return LIB.text_mask(text, LIB.WQY, size, index=1).width


def sag_pts(a, b, sag, n=40):
    (xa, ya), (xb, yb) = a, b
    return [(xa + (xb - xa) * i / n, ya + (yb - ya) * i / n + sag * 4 * (i / n) * (1 - i / n)) for i in range(n + 1)]


def polyline(d, pts, col, w=1):
    for p, q in zip(pts, pts[1:]):
        line(d, (p[0], p[1], q[0], q[1]), col, w)


# ============================================================ 送电铁塔 transmission_tower（320 × 540，竖向）
#   世界坐标和平常一样：地面 y 150，画面高 180；往上卷时 stage.camY 从 0 到 −360（图的第 0 行 = 世界 y −360）。
#   郊外荒草地里一座废弃的送电铁塔：四条腿往上收，三层横担（往两边伸出去，挂着绝缘子），塔顶避雷线支架。
#   能站的横梁：塔身里的三道水平梁 + 三层横担 + 塔顶小平台；两道之间是交叉斜梁（能爬）。
#   丰大的家：中间那道梁上一顶蓝色防水布帐篷、睡袋、炉子、水壶；上一层挂着晾衣绳和晨衣；塔顶横担头上一架自制小风车（会转）；
#   一根水桶滑轮绳从中层垂到地面。塔脚围着倒了一半的铁丝网，柱子上的告示「私人住宅 请勿靠近」。
#   断掉的电线：右边横担的线一路往右下方拉出画面（伸向远处，丰大沿着它往外走），左边的几根断头垂下来。
TY0 = -360                       # 图第 0 行的世界 y
TH = 540
STEEL = ('#5e646c', '#7e848c', '#a4aab0', '#3e434a')     # 中、亮、高光、暗
RUST = ('#8a5a3a', '#a46a42')


def Yr(y):
    return y - TY0


def tower_hw(y):
    """塔身半宽（世界 y）：地面 92 → 塔顶（y −300）22"""
    return 22 + (y + 300) / 450 * 70


TOWER_CX = 160
PLAT = [96, 42, -12]                           # 塔身里的水平梁（世界 y）
ARMS = [(-66, 112), (-150, 104), (-234, 96)]   # 横担（世界 y，从中心往两边伸多少）
TOP = -300


def steel_line(d, x0, y0, x1, y1, w=1, col=None):
    line(d, (x0, Yr(y0), x1, Yr(y1)), col or STEEL[0], w)


def beam(d, x0, x1, y, h=3):
    """水平梁：上面一条亮边、中间、底下一条暗边；每隔一段一颗螺栓"""
    r = Yr(y)
    rect(d, (x0, r, x1, r + h - 1), STEEL[1])
    line(d, (x0, r, x1, r), STEEL[2])
    line(d, (x0, r + h - 1, x1, r + h - 1), STEEL[3])
    for x in range(int(x0) + 3, int(x1), 9):
        px(d, x, r + 1, STEEL[3])


def cross_arm(d, y, reach):
    """横担：上下两根弦 + 之字腹杆，伸到头收成尖；两头各吊一串绝缘子。返回两个挂线点（世界坐标）"""
    hw = tower_hw(y)
    ends = []
    for s in (-1, 1):
        xa = TOWER_CX + s * hw
        xb = TOWER_CX + s * reach
        # 上弦（能站：3 px 厚）
        x0, x1 = sorted((xa, xb))
        beam(d, x0, x1, y, 3)
        # 下弦：从塔身往下 12 px 斜到头
        steel_line(d, xa, y + 14, xb, y + 3, 2)
        line(d, (xa, Yr(y + 14) - 1, xb, Yr(y + 3) - 1), STEEL[1])
        # 腹杆
        n = max(2, int(abs(xb - xa) / 12))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            xx0, xx1 = xa + (xb - xa) * t0, xa + (xb - xa) * t1
            yb0 = y + 14 + (3 - 14) * t0
            yb1 = y + 14 + (3 - 14) * t1
            if i % 2 == 0:
                steel_line(d, xx0, yb0, xx1, y + 2)
            else:
                steel_line(d, xx0, y + 2, xx1, yb1)
        # 绝缘子串
        ix = xb - s * 4
        for k in range(5):
            yy = Yr(y + 5 + k * 3)
            rect(d, (ix - 2, yy, ix + 2, yy + 1), '#c8d2d8' if k % 2 == 0 else '#9aa8b2')
            px(d, ix - 2, yy, '#e8f0f4')
        rect(d, (ix - 1, Yr(y + 20), ix + 1, Yr(y + 21)), STEEL[3])
        ends.append((ix, y + 21))
    return ends


def tower_near():
    W = 320
    im = new(W, TH)
    d = ImageDraw.Draw(im)
    G = 150
    # ---------------- 远一点的草地（地平线以下）——塔是近景，这里只画脚下这一块
    r_g = Yr(G)
    rect(d, (0, Yr(118), W, TH), '#7a9a52')
    im = grad(im, (0, Yr(118), W, Yr(140)), ('#9cb878', '#88a862', '#7a9a52'))
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(101)
    for x in range(0, W):                                                       # 远处草梢起伏
        y = Yr(118) + int(2 * math.sin(x / 9.0) + 1.5 * math.sin(x / 3.7 + 1))
        line(d, (x, y, x, Yr(119)), '#9cb878')
    # 土路（从左下斜进来，到塔脚）
    poly(d, [(0, Yr(168)), (0, Yr(180)), (130, Yr(180)), (176, Yr(150)), (150, Yr(150))], '#b8a27a')
    for _ in range(140):
        x, y = rng.randint(0, 170), rng.randint(Yr(150), TH)
        if im.getpixel((x, y))[:3] == c3('#b8a27a'):
            px(d, x, y, '#a48e66' if rng.rand() < .6 else '#ccb890')
    # 草丛：一簇簇往上翘的草叶
    for _ in range(420):
        x, y = rng.randint(-4, W + 4), rng.randint(Yr(126), TH)
        if im.getpixel((min(W - 1, max(0, x)), y))[:3] == c3('#b8a27a') and rng.rand() < .8:
            continue
        hgt = 2 + int((y - Yr(126)) / 14) + rng.randint(0, 3)
        col = ['#5e8040', '#6e9048', '#8cae5a', '#a6c46a'][rng.randint(4)]
        line(d, (x, y, x + rng.randint(-1, 2), y - hgt), col)
    # ---------------- 塔脚的水泥基础
    for s in (-1, 1):
        x = TOWER_CX + s * tower_hw(G)
        rect(d, (x - 7, Yr(G) - 3, x + 7, Yr(G) + 4), '#a8a49a')
        line(d, (x - 7, Yr(G) - 3, x + 7, Yr(G) - 3), '#c8c4ba')
        rect(d, (x - 7, Yr(G) + 4, x + 7, Yr(G) + 5), '#7e7a72')
    # ---------------- 塔身：四条腿（前后两对，后面那对细一点、颜色暗一点，错开 6 px）
    for back in (True, False):
        off = 6 if back else 0
        col = STEEL[3] if back else STEEL[0]
        for s in (-1, 1):
            xa = TOWER_CX + s * (tower_hw(G) - off)
            xb = TOWER_CX + s * (tower_hw(TOP) - off * .3)
            steel_line(d, xa, G, xb, TOP, 2 if back else 3, col)
            if not back:
                line(d, (xa - s, Yr(G), xb - s, Yr(TOP)), STEEL[2])
    # 腿上的脚钉（左腿，往上一路）
    for y in range(G - 10, TOP, -8):
        x = TOWER_CX - tower_hw(y)
        px(d, x - 2, Yr(y), STEEL[2])
        px(d, x - 3, Yr(y), STEEL[3])
    # ---------------- 交叉斜梁（能爬）：水平梁之间
    levels = [G] + PLAT + [a[0] for a in ARMS] + [TOP]
    for ya, yb in zip(levels, levels[1:]):
        xla, xra = TOWER_CX - tower_hw(ya), TOWER_CX + tower_hw(ya)
        xlb, xrb = TOWER_CX - tower_hw(yb), TOWER_CX + tower_hw(yb)
        steel_line(d, xla + 2, ya - 2, xrb - 2, yb + 3, 2, STEEL[0])
        steel_line(d, xra - 2, ya - 2, xlb + 2, yb + 3, 2, STEEL[0])
        line(d, (xla + 2, Yr(ya - 2) - 1, xrb - 2, Yr(yb + 3) - 1), STEEL[1])
        # 中间交点一块节点板
        mx, my = TOWER_CX, (ya + yb) / 2
        rect(d, (mx - 2, Yr(my) - 2, mx + 2, Yr(my) + 2), STEEL[1])
        px(d, mx, Yr(my), STEEL[3])
    # 水平梁 + 横担 + 塔顶小平台
    for y in PLAT:
        hw = tower_hw(y)
        beam(d, TOWER_CX - hw - 2, TOWER_CX + hw + 2, y)
    arm_ends = []
    for y, reach in ARMS:
        arm_ends.append(cross_arm(d, y, reach))
    beam(d, TOWER_CX - tower_hw(TOP) - 4, TOWER_CX + tower_hw(TOP) + 4, TOP)
    # 塔顶避雷线支架（尖顶）
    for s in (-1, 1):
        steel_line(d, TOWER_CX + s * tower_hw(TOP), TOP, TOWER_CX + s * 4, -344, 2)
    steel_line(d, TOWER_CX - 4, -330, TOWER_CX + 4, -330)
    steel_line(d, TOWER_CX - 10, -318, TOWER_CX + 10, -318)
    rect(d, (TOWER_CX - 1, Yr(-350), TOWER_CX + 1, Yr(-344)), STEEL[0])
    px(d, TOWER_CX, Yr(-351), '#d84a3a')
    # 锈迹：随机几处
    for _ in range(90):
        y = rng.randint(TOP, G)
        s = rng.choice([-1, 1])
        x = TOWER_CX + s * tower_hw(y) + rng.randint(-1, 2)
        px(d, x, Yr(y), RUST[rng.randint(2)])
    # 号牌（塔腿上：黄底黑字的编号牌）
    plx = int(TOWER_CX + tower_hw(112)) - 4
    rect(d, (plx, Yr(118), plx + 11, Yr(108)), '#e8c838')
    line(d, (plx, Yr(108), plx + 11, Yr(108)), '#8a7420')
    digits(d, plx + 2, Yr(116), '42', '#2a2a24')
    # ---------------- 断掉的电线
    #   右边三根：从右边三个挂线点往右下方一路拉出画面（伸向远处的下一座塔，丰大沿着它往外走）
    wires_out = []
    for i, ((lx, ly), (rx, ry)) in enumerate(arm_ends):
        end = (W + 30, ry + 70 + i * 26)
        pts = sag_pts((rx, Yr(ry)), (end[0], Yr(end[1])), 6 + i * 2)
        polyline(d, pts, '#2a2a30')
        wires_out.append([[round(rx), ry], [W, round(ry + (end[1] - ry) * (W - rx) / (end[0] - rx))]])
    #   左边：断头垂下来，打着卷
    for i, (lx, ly) in enumerate(e[0] for e in arm_ends):
        L_ = 28 + i * 12
        pts = [(lx - 3 * math.sin(k / 6.0) - k * .15, Yr(ly) + k) for k in range(L_)]
        polyline(d, pts, '#2a2a30')
        ex, ey = pts[-1]
        px(d, ex + 1, ey + 1, '#2a2a30')
        px(d, ex + 2, ey, '#2a2a30')
    # ---------------- 丰大的家
    # 中层（PLAT[1] = 42）：蓝色防水布帐篷 + 睡袋 + 炉子水壶 + 木箱 + 收音机
    y = PLAT[1]
    hw = tower_hw(y)
    tx0, tx1 = TOWER_CX - hw + 6, TOWER_CX - 10
    ry = Yr(y)
    poly(d, [(tx0, ry), (tx1, ry), ((tx0 + tx1) / 2 + 6, ry - 24)], '#3a74b8')
    poly(d, [((tx0 + tx1) / 2 + 6, ry - 24), (tx1, ry), (tx1 - 6, ry)], '#2a5a96')
    line(d, (tx0, ry, (tx0 + tx1) / 2 + 6, ry - 24), '#5a94d4')
    poly(d, [((tx0 + tx1) / 2 - 2, ry), ((tx0 + tx1) / 2 + 10, ry), ((tx0 + tx1) / 2 + 5, ry - 14)], '#1e3a5e')   # 门口
    line(d, ((tx0 + tx1) / 2 + 6, ry - 24, TOWER_CX - hw + 2, ry - 30), '#c8b890')                          # 拉绳
    rect(d, (TOWER_CX - 6, ry - 6, TOWER_CX + 12, ry - 1), '#d86a3a')                                        # 睡袋（卷起来）
    line(d, (TOWER_CX - 6, ry - 6, TOWER_CX + 12, ry - 6), '#f08a5a')
    for x in (TOWER_CX - 1, TOWER_CX + 6):
        line(d, (x, ry - 6, x, ry - 1), '#a84a2a')
    rect(d, (TOWER_CX + 18, ry - 4, TOWER_CX + 26, ry - 1), '#3a3a40')                                       # 小炉子 + 水壶
    rect(d, (TOWER_CX + 19, ry - 9, TOWER_CX + 25, ry - 5), '#c8ccd0')
    line(d, (TOWER_CX + 19, ry - 9, TOWER_CX + 25, ry - 9), '#e8ecf0')
    line(d, (TOWER_CX + 25, ry - 8, TOWER_CX + 28, ry - 10), '#c8ccd0')
    rect(d, (TOWER_CX + 30, ry - 8, TOWER_CX + 42, ry - 1), '#a07848')                                       # 木箱
    line(d, (TOWER_CX + 30, ry - 8, TOWER_CX + 42, ry - 8), '#c09868')
    line(d, (TOWER_CX + 30, ry - 4, TOWER_CX + 42, ry - 4), '#806038')
    rect(d, (TOWER_CX + 33, ry - 13, TOWER_CX + 40, ry - 9), '#2a2a30')                                      # 收音机
    rect(d, (TOWER_CX + 34, ry - 12, TOWER_CX + 36, ry - 10), '#8a8a90')
    line(d, (TOWER_CX + 40, ry - 13, TOWER_CX + 44, ry - 19), '#c8ccd0')
    # 上一层（PLAT[2] = −12）：蓝色塑料水箱 + 滑轮（绳子一路垂到地面，挂着水桶）
    y = PLAT[2]
    ry = Yr(y)
    hw = tower_hw(y)
    rect(d, (TOWER_CX + 8, ry - 16, TOWER_CX + 26, ry - 1), '#2a6ab0')
    rect(d, (TOWER_CX + 8, ry - 16, TOWER_CX + 26, ry - 15), '#4a8ad0')
    line(d, (TOWER_CX + 10, ry - 13, TOWER_CX + 10, ry - 3), '#5a9ade')
    rect(d, (TOWER_CX + 14, ry - 19, TOWER_CX + 20, ry - 17), '#1e4a80')
    pu = (TOWER_CX - hw - 8, ry + 2)
    rect(d, (TOWER_CX - hw - 8, ry, TOWER_CX - hw, ry + 2), STEEL[0])                                         # 伸出去的吊杆
    ellipse(d, (pu[0] - 2, pu[1], pu[0] + 2, pu[1] + 4), '#8a8a90')
    line(d, (pu[0], pu[1] + 4, pu[0], Yr(120)), '#c8b890')
    rect(d, (pu[0] - 3, Yr(120), pu[0] + 3, Yr(127)), '#c8ccd0')                                             # 水桶
    line(d, (pu[0] - 3, Yr(120), pu[0] + 3, Yr(120)), '#e8ecf0')
    rect(d, (pu[0] - 3, Yr(124), pu[0] + 3, Yr(124)), '#9aa0a6')
    # 晾衣绳：从下层横担（−66）左边拉到塔身，挂着酒红色晨衣、毛巾、一只袜子
    ya = ARMS[0][0]
    a0 = (TOWER_CX - 86, Yr(ya) + 2)
    a1 = (TOWER_CX - tower_hw(PLAT[2]) + 2, Yr(PLAT[2]) - 22)
    pts = sag_pts(a0, a1, 5, 30)
    polyline(d, pts, '#e8e0cc')
    robe_x = TOWER_CX - 64
    k = (robe_x - a0[0]) / (a1[0] - a0[0])
    by = int(a0[1] + (a1[1] - a0[1]) * k + 5 * 4 * k * (1 - k))
    poly(d, [(robe_x - 8, by), (robe_x + 8, by), (robe_x + 10, by + 6), (robe_x + 7, by + 24), (robe_x - 7, by + 24), (robe_x - 10, by + 6)],
         '#8a2a3a')
    poly(d, [(robe_x - 2, by), (robe_x + 2, by), (robe_x, by + 10)], '#5a1a24')                              # 领口
    line(d, (robe_x - 7, by + 14, robe_x + 7, by + 14), '#c8a050')                                           # 腰带
    line(d, (robe_x - 9, by + 6, robe_x - 6, by + 22), '#a84a5a')
    line(d, (robe_x, by + 15, robe_x - 1, by + 23), '#6a1e2a')
    towel_x = robe_x + 22
    k = (towel_x - a0[0]) / (a1[0] - a0[0])
    ty = int(a0[1] + (a1[1] - a0[1]) * k + 5 * 4 * k * (1 - k))
    rect(d, (towel_x - 4, ty, towel_x + 4, ty + 12), '#f0ece0')
    line(d, (towel_x - 4, ty + 9, towel_x + 4, ty + 9), '#6a9ad0')
    sx = robe_x - 18
    k = (sx - a0[0]) / (a1[0] - a0[0])
    sy = int(a0[1] + (a1[1] - a0[1]) * k + 5 * 4 * k * (1 - k))
    rect(d, (sx - 1, sy, sx + 1, sy + 6), '#e8e4d8')
    rect(d, (sx - 1, sy + 5, sx + 3, sy + 7), '#e8e4d8')
    # 塔顶横担（−234）右头：自制风车的立杆（叶片是动画帧条），一根线连回帐篷那层
    mx = TOWER_CX + 70
    ytop = ARMS[2][0]
    rect(d, (mx - 1, Yr(ytop) - 22, mx, Yr(ytop) - 1), '#b8bcc0')
    rect(d, (mx - 3, Yr(ytop) - 24, mx + 4, Yr(ytop) - 20), '#d84a3a')                                       # 发电机壳
    line(d, (mx + 4, Yr(ytop) - 22, mx + 9, Yr(ytop) - 22), '#b8bcc0')                                       # 尾翼
    poly(d, [(mx + 8, Yr(ytop) - 26), (mx + 12, Yr(ytop) - 22), (mx + 8, Yr(ytop) - 20)], '#e8e4d8')
    polyline(d, sag_pts((mx, Yr(ytop) + 2), (TOWER_CX + 20, Yr(PLAT[1]) - 14), 10, 40), '#3a3a40')
    windmill = (mx - 3, ytop - 24)
    # ---------------- 塔脚：倒了一半的铁丝网 + 告示
    fy = Yr(158)
    posts = [-6, 40, 86, 234, 280, 326]
    for i, x in enumerate(posts):
        lean = 0 if i not in (1, 4) else (5 if i == 1 else -6)
        line(d, (x, fy, x + lean, fy - 28), '#6a5a48', 2)
        px(d, x + lean, fy - 29, '#8a7a64')
    for (xa, xb, down) in ((-6, 40, False), (40, 86, True), (234, 280, True), (280, 326, False)):
        for yy in range(0, 26, 4):
            if down:
                line(d, (xa, fy - yy, xb, fy - max(0, yy - 14)), '#9aa0a0')
            else:
                line(d, (xa, fy - yy, xb, fy - yy), '#9aa0a0')
        for xx in range(xa, xb, 4):
            line(d, (xx, fy - (26 if not down else 12), xx + 2, fy), '#8a9090')
    # 告示：钉在左边塔脚旁的木桩上
    bx0, by0 = 22, Yr(106)
    rect(d, (bx0 + 24, by0 + 26, bx0 + 27, Yr(156)), '#7a5a3a')
    rect(d, (bx0, by0, bx0 + 52, by0 + 30), '#5a4a38')
    rect(d, (bx0 + 1, by0 + 1, bx0 + 51, by0 + 29), '#f0ece0')
    line(d, (bx0 + 1, by0 + 28, bx0 + 51, by0 + 28), '#c8c2b0')
    kanji(im, bx0 + 2, by0 + 2, '私人住宅', '#c8282a')
    kanji(im, bx0 + 2, by0 + 15, '请勿靠近', '#2a2a30')
    d = ImageDraw.Draw(im)
    px(d, bx0 + 3, by0 + 1, '#8a8a90')
    px(d, bx0 + 49, by0 + 1, '#8a8a90')
    return im, arm_ends, wires_out, windmill


def tower_far():
    """天空 + 远景：320 × 324，画在世界 y −144，ky 0.4（镜头往上卷 360，远景只卷 144）"""
    W, H = 320, 324
    im = new(W, H, '#d8eaf6')
    im = grad(im, (0, 0, W, 250), ('#3a78c8', '#5a94dc', '#78b0ec', '#9cc8f0', '#c4def4', '#e2eef6'))
    rng = np.random.RandomState(7)
    for i in range(7):                                                          # 夏天的积云（越高越小）
        cy = rng.randint(20, 210)
        cloud(im, rng.randint(-10, W - 30), cy, rng.randint(24, 40 + cy // 4), seed=70 + i)
    d = ImageDraw.Draw(im)
    HZ = 246                                                                    # 地平线（世界 y 102）
    for layer, (base, amp, col, col2) in enumerate(((HZ - 14, 9, '#9cb8c4', '#b4ccd4'), (HZ - 6, 6, '#7c9eac', '#90b0bc'))):
        for x in range(W):
            y = base + amp * math.sin(x / (50 + layer * 20) + layer * 2) + 3 * math.sin(x / 13.0 + layer)
            line(d, (x, int(y), x, HZ + 4), col)
            px(d, x, int(y), col2)
    # 远处的杜王町（左边一小片屋顶）+ 海
    rect(d, (180, HZ - 2, W, HZ + 2), '#5c98cc')
    for x in range(182, W, 7):
        px(d, x + (x // 7) % 3, HZ, '#9cc8ec')
    for i in range(26):
        x = rng.randint(0, 170)
        w_ = rng.randint(6, 12)
        h_ = rng.randint(3, 7)
        rect(d, (x, HZ - h_, x + w_, HZ + 2), ['#c8ccd0', '#d8d0c4', '#b8c0c8', '#a8b4c0'][rng.randint(4)])
        line(d, (x, HZ - h_, x + w_, HZ - h_), ['#8a6a5a', '#5a6a7a', '#7a5a4a'][rng.randint(3)])
    # 远处一排送电铁塔（电线一路连过来）
    tops = []
    for i, (x, h) in enumerate(((236, 34), (276, 24), (304, 17))):
        bot = HZ + 4
        for s in (-1, 1):
            line(d, (x + s * h * .28, bot, x + s * 2, bot - h), '#8a96a2')
        for k in range(1, 4):
            yy = bot - h * k / 4
            hw = h * .28 * (1 - k / 4) + 2
            line(d, (x - hw, yy, x + hw, yy), '#8a96a2')
        line(d, (x - h * .3, bot - h * .7, x + h * .3, bot - h * .7), '#8a96a2')
        tops.append((x, bot - h * .7))
    for a, b in zip(tops, tops[1:]):
        polyline(d, sag_pts(a, b, 3, 16), '#7a8692')
    # 近处的草地
    rect(d, (0, HZ + 4, W, H), '#9cb878')
    im = grad(im, (0, HZ + 4, W, H), ('#a8c484', '#9cb878', '#8cac68'))
    return im


def windmill_strip(n=4):
    """三叶小风车：n 帧转一圈的 1/3（三叶对称，首尾接得上）"""
    S = 17
    out = Image.new('RGBA', (S * n, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    for f in range(n):
        cx, cy = f * S + 8, 8
        for b in range(3):
            a = (f / n + b) * 2 * math.pi / 3
            ex, ey = cx + 7 * math.cos(a), cy + 7 * math.sin(a)
            nx, ny = -math.sin(a), math.cos(a)
            poly(d, [(cx, cy), (ex, ey), (ex + nx * 2, ey + ny * 2), (cx + nx * 1, cy + ny * 1)], '#f0ece0')
            line(d, (cx, cy, ex, ey), '#c8c2b0')
        rect(d, (cx - 1, cy - 1, cx + 1, cy + 1), '#d84a3a')
    return out


def transmission_tower():
    W = 320
    near, arm_ends, wires_out, (wx, wy) = tower_near()
    far = tower_far()
    mill = windmill_strip(4)
    layers = {'far': far, 'near': near, 'windmill': mill}
    beams = [[round(TOWER_CX - tower_hw(y) - 2), round(TOWER_CX + tower_hw(y) + 2), y] for y in PLAT]
    arms = [[TOWER_CX - r, TOWER_CX + r, y] for y, r in ARMS]
    top = [round(TOWER_CX - tower_hw(TOP) - 4), round(TOWER_CX + tower_hw(TOP) + 4), TOP]
    meta = dict(pack=PACK, w=W, h=TH, y0=TY0, camY=[TY0, 0], ground=150, walk=[142, 176],
                anchors=dict(tower=[TOWER_CX, 146], sign=[48, 146], path=[60, 166], bucket=[TOWER_CX - round(tower_hw(PLAT[2])) - 8, 146],
                             tent=[TOWER_CX - 30, PLAT[1]], stove=[TOWER_CX + 22, PLAT[1]], robe=[TOWER_CX - 64, ARMS[0][0] + 4],
                             tank=[TOWER_CX + 17, PLAT[2]], windmill=[wx + 8, wy + 8], top=[TOWER_CX, TOP],
                             wire_out=[[round(e[1][0]), e[1][1]] for e in arm_ends], wire_end=[w[1] for w in wires_out],
                             leg_l=[round(TOWER_CX - tower_hw(150)), 150], leg_r=[round(TOWER_CX + tower_hw(150)), 150],
                             beams=beams, arms=arms, top_deck=top, walk_x=[8, 312]),
                layers=[{'type': 'tall', 'ky': 0.4, 'layers': [{'type': 'pano', 'image': 'bg/transmission_tower/far', 'k': 0, 'x': 0, 'y': -144}]},
                        {'type': 'tall', 'ky': 1, 'layers': [
                            {'type': 'pano', 'image': 'bg/transmission_tower/near', 'k': 1, 'x': 0, 'y': TY0},
                            {'type': 'strip', 'image': 'bg/transmission_tower/windmill', 'n': 4, 'fps': 10, 'w': 17, 'h': 17,
                             'x': wx - 5, 'y': wy - 5, 'k': 1}]},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    # 预览：整座塔（竖长图）+ 镜头在底 / 中 / 顶三张拼一排
    full = Image.new('RGBA', (W, TH), (0, 0, 0, 255))
    full.alpha_composite(far.resize((W, TH), Image.NEAREST))
    full.alpha_composite(near)
    full.alpha_composite(mill.crop((0, 0, 17, 17)), (wx - 5, wy - 5 - TY0))
    os.makedirs(os.path.join(LIB.ASSETS, 'preview'), exist_ok=True)
    full.save(os.path.join(LIB.ASSETS, 'preview', 'bg_transmission_tower_full.png'))
    shots = Image.new('RGBA', (W * 3 + 8, 180), (0, 0, 0, 255))
    for i, cam in enumerate((0, -180, -360)):
        can = Image.new('RGBA', (W, 180), (0, 0, 0, 255))
        can.alpha_composite(far, (0, int(-144 - round(cam * .4))))
        can.alpha_composite(near, (0, int(TY0 - cam)))
        can.alpha_composite(mill.crop((0, 0, 17, 17)), (wx - 5, int(wy - 5 - cam)))
        shots.alpha_composite(can, (i * (W + 4), 0))
    preview('transmission_tower', {'room': shots}, ['room'], W * 3 + 8)
    save_layers('transmission_tower', layers, meta)
    return meta


# ============================================================ 宫本的屋子 miyamoto_house（480 宽，傍晚前的室内）
#   老式日本民宅的一间大屋：左边拉门（障子）透进走廊的光，中间矮桌、书桌台灯、书架；
#   满屋子折好的纸：桌上一摞摞、墙上图钉钉着、地上散着；右边一台大型工业碎纸机（进纸台、投入口、指示灯、底下纸屑箱）。
#   碎纸机开着的那一层是动画（key 'shred'：刀辊转、纸条往下掉、绿灯亮）。
def folded_note(d, x, y, w=8, h=6, col='#f4f0e4', edge='#c8c2b0'):
    """一张折好的纸：长方形 + 一条斜折痕 + 一角翻起"""
    rect(d, (x, y, x + w, y + h), col)
    line(d, (x, y + h, x + w, y + h), edge)
    line(d, (x + w, y, x + w, y + h), edge)
    line(d, (x + 1, y + 1, x + w - 2, y + h - 1), '#e0dacc')
    px(d, x + w - 1, y + 1, '#ffffff')


def shoji(d, x0, x1, top, G, lit=True):
    rect(d, (x0, top, x1, G), '#6a4a30')
    rect(d, (x0 + 2, top + 2, x1 - 2, G - 6), '#f4ecd4' if lit else '#d8ccb0')
    for x in range(x0 + 2, x1 - 2, 10):
        line(d, (x, top + 2, x, G - 6), '#8a6a48')
    for y in range(top + 2, G - 6, 13):
        line(d, (x0 + 2, y, x1 - 2, y), '#8a6a48')
    rect(d, (x0 + 2, G - 6, x1 - 2, G - 1), '#7a5a3a')                            # 腰板


def shredder(d, x0, G, run=False, frame=0):
    """工业碎纸机：x0 起 76 宽、到 G 为止。run = 开着（绿灯，刀辊花纹按 frame 错开）"""
    x1 = x0 + 76
    top = G - 64
    # 机身
    rect(d, (x0, top, x1, G - 2), '#7a8288')
    rect(d, (x0, top, x1, top + 2), '#a8b0b6')
    line(d, (x1, top, x1, G - 2), '#5a6268')
    rect(d, (x0 + 2, G - 2, x1 - 2, G), '#3a3e42')
    # 进纸台：从左上斜进投入口
    poly(d, [(x0 - 22, top - 14), (x0 + 8, top - 2), (x0 + 8, top + 1), (x0 - 22, top - 11)], '#c8ccd0')
    line(d, (x0 - 22, top - 14, x0 + 8, top - 2), '#e8ecf0')
    line(d, (x0 - 20, top - 11, x0 - 20, G - 2), '#5a6268')                       # 台子的腿
    # 投入口：黑色的长缝 + 黄黑警示条
    rect(d, (x0 + 8, top - 4, x1 - 8, top), '#3a3e42')
    rect(d, (x0 + 10, top - 3, x1 - 10, top - 1), '#141418')
    for x in range(x0 + 8, x1 - 8, 6):
        poly(d, [(x, top + 4), (x + 3, top + 4), (x + 6, top + 7), (x + 3, top + 7)], '#2a2a2a')
    rect(d, (x0 + 8, top + 3, x1 - 8, top + 3), '#e8c030')
    rect(d, (x0 + 8, top + 8, x1 - 8, top + 8), '#e8c030')
    if run:                                                                     # 刀辊：缝里一排亮齿，按帧错开
        for x in range(x0 + 11 + frame % 3, x1 - 10, 3):
            px(d, x, top - 2, '#c8ccd0')
    # 面板：铭牌、两盏灯、开关
    rect(d, (x0 + 8, top + 14, x0 + 40, top + 26), '#5a6268')
    rect(d, (x0 + 9, top + 15, x0 + 39, top + 25), '#2a2e32')
    letters_small(d, x0 + 11, top + 18, 'SHRED', '#c8ccd0')
    for i, (c_on, c_off) in enumerate((('#58e870', '#2a5a34'), ('#ff5a4a', '#5a2a28'))):
        on = (i == 0) == run
        ellipse(d, (x0 + 48 + i * 10, top + 16, x0 + 54 + i * 10, top + 22), c_on if on else c_off)
        if on:
            px(d, x0 + 50 + i * 10, top + 17, '#ffffff')
    rect(d, (x0 + 66, top + 15, x0 + 70, top + 23), '#d84a3a')
    # 底下的纸屑箱（透明窗里塞满纸条）
    rect(d, (x0 + 6, top + 32, x1 - 6, G - 6), '#4a5056')
    rect(d, (x0 + 9, top + 35, x1 - 9, G - 9), '#d8dcd8')
    rng = np.random.RandomState(9 + (frame if run else 0))
    for _ in range(60):
        x = rng.randint(x0 + 9, x1 - 9)
        y = rng.randint(top + 38, G - 9)
        line(d, (x, y, x + rng.randint(-2, 3), y + 3), ['#f4f0e4', '#c8c2b0', '#e8e2d0', '#a8b8d0'][rng.randint(4)])
    line(d, (x0 + 10, top + 36, x0 + 18, top + 36), '#ffffff')
    rect(d, (x0 + 32, G - 14, x1 - 32, G - 12), '#2a2e32')                         # 把手


LET_S = {'S': ['011', '100', '010', '001', '110'], 'H': ['101', '101', '111', '101', '101'], 'R': ['110', '101', '110', '101', '101'],
         'E': ['111', '100', '110', '100', '111'], 'D': ['110', '101', '101', '101', '110'], 'T': ['111', '010', '010', '010', '010'],
         'O': ['010', '101', '101', '101', '010'], 'K': ['101', '101', '110', '101', '101'], 'N': ['1001', '1101', '1011', '1001', '1001'],
         'I': ['111', '010', '010', '010', '111'], 'G': ['011', '100', '101', '101', '011'], 'M': ['10001', '11011', '10101', '10001', '10001'],
         'A': ['010', '101', '111', '101', '101'], ' ': ['000'] * 5}


def letters_small(d, x, y, text, col):
    cx = x
    for ch in text:
        g = LET_S.get(ch, ['000'] * 5)
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == '1':
                    px(d, cx + c, y + r, col)
        cx += len(g[0]) + 1


def miyamoto_room():
    W, G = 480, 140
    im = new(W, 180)
    d = ImageDraw.Draw(im)
    # 天花板（木板）+ 墙（土墙米色）+ 柱子 + 长押
    rect(d, (0, 0, W, 14), '#8a6a48')
    for x in range(0, W, 16):
        line(d, (x, 0, x, 13), '#7a5a3a')
    line(d, (0, 13, W, 13), '#5a4028')
    im = grad(im, (0, 14, W, G), ('#d8c8a4', '#e2d4b2', '#d4c4a0'))
    d = ImageDraw.Draw(im)
    noise_specks(im, (0, 16, W, G), ['#cebe9a', '#e8dcc0'], 900, 5)
    d = ImageDraw.Draw(im)
    rect(d, (0, 38, W, 42), '#7a5a3a')                                          # 长押
    line(d, (0, 38, W, 38), '#9a7a58')
    for x in (0, 112, 224, 336, 470):
        rect(d, (x, 14, x + 9, G), '#8a6440')
        line(d, (x + 1, 14, x + 1, G), '#a88058')
        line(d, (x + 9, 14, x + 9, G), '#6a4a30')
    # 左：两扇拉门（障子）透着走廊的光
    shoji(d, 12, 58, 44, G)
    shoji(d, 58, 108, 44, G)
    rect(d, (56, 44, 60, G), '#6a4a30')
    # 拉门上面的欄間（透雕的格子）
    for x in range(12, 108, 6):
        line(d, (x, 18, x + 3, 36), '#7a5a3a')
    # 中：窗（傍晚前，外面一棵树影）+ 窗下书桌 + 台灯 + 书架
    wx0, wx1, wy0, wy1 = 132, 214, 50, 104
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), '#6a4a30')
    im = grad(im, (wx0, wy0, wx1, wy1), ('#f4d8a4', '#f0c890', '#e8b880'))
    d = ImageDraw.Draw(im)
    for k in range(5):                                                          # 外面的树影
        cx, cy = wx0 + 10 + k * 17, wy0 + 6 + (k % 2) * 8
        ellipse(d, (cx - 9, cy - 6, cx + 9, cy + 8), '#c8a070')
    for x in range(wx0, wx1, 20):
        line(d, (x, wy0, x, wy1), '#6a4a30')
    line(d, (wx0, (wy0 + wy1) // 2, wx1, (wy0 + wy1) // 2), '#6a4a30')
    rect(d, (wx0 - 6, wy1 + 3, wx1 + 6, wy1 + 6), '#7a5a3a')                      # 窗台
    # 书桌
    dx0, dx1 = 228, 300
    rect(d, (dx0, 108, dx1, 112), '#7a5434')
    line(d, (dx0, 108, dx1, 108), '#9a7450')
    rect(d, (dx0 + 2, 112, dx0 + 22, G - 1), '#6a4a2e')
    for y in (118, 127):
        line(d, (dx0 + 4, y, dx0 + 20, y), '#4e3420')
        px(d, dx0 + 12, y - 3, '#c8a050')
    line(d, (dx1 - 3, 112, dx1 - 3, G - 1), '#5a3e26')
    rect(d, (dx0 + 52, 116, dx0 + 64, 130), '#3a5a8a')                            # 椅子靠背
    rect(d, (dx0 + 50, 130, dx0 + 66, 132), '#2a4a72')
    line(d, (dx0 + 52, 132, dx0 + 52, G - 1), '#2a2a30')
    line(d, (dx0 + 64, 132, dx0 + 64, G - 1), '#2a2a30')
    line(d, (dx0 + 60, 92, dx0 + 64, 107), '#3a3a40')                              # 台灯
    line(d, (dx0 + 60, 92, dx0 + 52, 96), '#3a3a40')
    poly(d, [(dx0 + 48, 94), (dx0 + 56, 94), (dx0 + 54, 100), (dx0 + 50, 100)], '#2a6a4a')
    rect(d, (dx0 + 60, 106, dx0 + 68, 107), '#3a3a40')
    for i in range(4):                                                          # 桌上一摞摞折好的纸
        for k in range(3 + i % 2):
            folded_note(d, dx0 + 6 + i * 10, 104 - k * 3, 8, 3)
    # 书架
    bx0, bx1 = 304, 334
    rect(d, (bx0, 52, bx1, G - 1), '#6a4a2e')
    rng = np.random.RandomState(31)
    for sy in (56, 76, 96, 116):
        rect(d, (bx0 + 2, sy, bx1 - 2, sy + 17), '#3e2a1a')
        x = bx0 + 3
        while x < bx1 - 4:
            w_ = rng.randint(2, 4)
            h_ = rng.randint(11, 17)
            rect(d, (x, sy + 17 - h_, x + w_ - 1, sy + 16), ['#8a3a34', '#3a5a8a', '#e8e0cc', '#4a7a4a', '#c8a050', '#5a4a6a'][rng.randint(6)])
            x += w_ + (1 if rng.rand() < .2 else 0)
        rect(d, (bx0 + 2, sy + 17, bx1 - 2, sy + 19), '#7a5636')
    # 墙上图钉钉着的折纸（中间那面墙一大片）
    for i in range(18):
        x = 116 + (i * 37) % 100 + rng.randint(0, 4)
        y = 16 + (i * 13) % 20
        if 132 - 6 < x < 214 + 6 and y > 44:
            continue
        folded_note(d, x, y, 7, 5)
        px(d, x + 3, y, '#d84a3a')
    for i in range(10):
        x = 340 + rng.randint(0, 24)
        y = 48 + i * 8
        folded_note(d, x, y, 7, 5)
        px(d, x + 3, y, '#d84a3a')
    # ---------------- 地板
    im = liv_floor(im, 0, W, G)
    d = ImageDraw.Draw(im)
    # 矮桌（左中）+ 坐垫
    rect(d, (70, G + 6, 118, G + 9), '#5a3a22')
    line(d, (70, G + 6, 118, G + 6), '#7a5434')
    for x in (73, 114):
        rect(d, (x, G + 9, x + 2, G + 18), '#4a2e1a')
    for k in range(4):
        folded_note(d, 76 + k * 9, G + 3 - (k % 2) * 3, 8, 3)
    rect(d, (58, G + 20, 76, G + 24), '#8a3a4a')
    line(d, (58, G + 20, 76, G + 20), '#a85a6a')
    # 地上散的折纸
    for i in range(16):
        x = rng.randint(10, W - 100)
        y = rng.randint(G + 12, 176)
        folded_note(d, x, y, 6, 4)
    return im, G


def shred_strip(n=4):
    """碎纸机开着：只画机身那一块（76+22 宽 × 72 高），刀辊花纹错开、纸条往下掉、绿灯亮"""
    W_, H_ = 104, 76
    out = Image.new('RGBA', (W_ * n, H_), (0, 0, 0, 0))
    for f in range(n):
        fr = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        d = ImageDraw.Draw(fr)
        shredder(d, 24, H_ - 2, run=True, frame=f)
        # 从投入口往下掉的纸条（在机身前面飘几根）
        top = H_ - 2 - 64
        for k in range(5):
            x = 34 + k * 11 + (f * 3 + k * 5) % 7
            y = top + 2 + ((f * 4 + k * 7) % 12)
            line(ImageDraw.Draw(fr), (x, y, x + 1, y + 4), '#f4f0e4')
        out.alpha_composite(fr, (f * W_, 0))
    return out


def miyamoto_house():
    W = 480
    room, G = miyamoto_room()
    d = ImageDraw.Draw(room)
    sx0 = 386
    shredder(d, sx0, G + 6)
    # 碎纸机脚下的纸屑
    rng = np.random.RandomState(44)
    for _ in range(70):
        x = rng.randint(sx0 - 30, W - 4)
        y = rng.randint(G + 6, 172)
        line(d, (x, y, x + rng.randint(-2, 3), y + 2), ['#f4f0e4', '#d8d2c0', '#e8e2d0'][rng.randint(3)])
    strip = shred_strip(4)
    layers = {'room': room, 'shred': strip}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(shoji=[58, 148], window=[173, 76], desk=[264, 148], shelf=[319, 148], table=[94, 150],
                             shredder=[sx0 + 38, 150], slot=[sx0 + 38, G + 6 - 66], feed=[sx0 - 8, G + 6 - 74],
                             bin=[sx0 + 38, G - 18], walk_x=[8, 380]),
                layers=[{'type': 'pano', 'image': 'bg/miyamoto_house/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': 'bg/miyamoto_house/shred', 'n': 4, 'fps': 12, 'w': 104, 'h': 76,
                         'x': sx0 - 24, 'y': G + 6 - 74, 'k': 1, 'key': 'shred'},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.12, 'key': 'pm'}],
                fg=[])
    pv = room.copy()
    preview('miyamoto_house', {'room': pv}, ['room'], W)
    pv2 = room.copy()
    pv2.alpha_composite(strip.crop((0, 0, 104, 76)), (sx0 - 24, G + 6 - 74))
    pv2.save(os.path.join(LIB.ASSETS, 'preview', 'bg_miyamoto_house_shred.png'))
    save_layers('miyamoto_house', layers, meta)
    return meta


# ============================================================ 纸里的世界 paper_world（480 宽）
#   一张摊开的大纸：米白纸面、折痕（横竖几道，一边亮一边暗），上面是钢笔线条画的“世界”——
#   街道的轮廓、房子、电线杆、一棵树，都只有线条和排线阴影；地面是一条墨线。
#   空中飘着几张折好的小纸（动画），仗助和康一的那两张由剧情摆道具（锚点 paper_a / paper_b）。
INK = '#2a2a34'
INK2 = '#6a6a78'


def hatch(d, box, step=3, col=INK2, slope=1):
    x0, y0, x1, y1 = box
    for k in range(int(x0 - (y1 - y0)), int(x1), step):
        pts = []
        for t in range(0, int(y1 - y0) + 1):
            x = k + t * slope
            if x0 <= x <= x1:
                pts.append((x, y1 - t))
        if len(pts) > 1:
            line(d, (pts[0][0], pts[0][1], pts[-1][0], pts[-1][1]), col)


def ink_house(d, x, G, w, h, roof=14, door=True):
    rect(d, (x, G - h, x + w, G), None, INK)
    poly_o(d, [(x - 4, G - h), (x + w // 2, G - h - roof), (x + w + 4, G - h)])
    for k in range(2):
        wx = x + 6 + k * (w // 2)
        rect(d, (wx, G - h + 8, wx + 10, G - h + 18), None, INK)
        line(d, (wx + 5, G - h + 8, wx + 5, G - h + 18), INK)
    if door:
        rect(d, (x + w - 16, G - 22, x + w - 6, G), None, INK)
    hatch(d, (x + 1, G - h + 1, x + 5, G - 1), 3)


def poly_o(d, pts):
    d.line([(int(round(x)), int(round(y))) for x, y in pts], fill=C(INK), width=1)


def paper_base(W):
    im = new(W, 180, '#f4f0e4')
    rng = np.random.RandomState(3)
    a = np.array(im)
    nz = rng.rand(180, W)
    a[nz < .04] = (*c3('#ebe6d6'), 255)
    a[nz > .985] = (*c3('#fbf8f0'), 255)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 折痕：竖的每 120、横的 60 / 120（一边暗一边亮）
    for x in range(120, W, 120):
        line(d, (x, 0, x, 179), '#d8d2c0')
        line(d, (x + 1, 0, x + 1, 179), '#fffdf6')
    for y in (60, 120):
        line(d, (0, y, W, y), '#ddd6c4')
        line(d, (0, y + 1, W, y + 1), '#fffdf6')
    # 纸边：上下两头的阴影（这是一张纸，四边稍暗）
    im = dither_fill(im, (0, 0, W, 3), '#e2dccb', '#f4f0e4', .5)
    im = dither_fill(im, (0, 176, W, 180), '#e2dccb', '#f4f0e4', .5)
    return im


def paper_world_img():
    W, G = 480, 146
    im = paper_base(W)
    d = ImageDraw.Draw(im)
    # 地面墨线 + 往前的透视线（路）
    line(d, (0, G, W, G), INK)
    for k, x in enumerate(range(-200, W + 200, 60)):
        line(d, (W // 2 + (x - W // 2) * .35, G, x, 180), '#9a9aa6')
    for y in (156, 168):
        line(d, (0, y, W, y), '#b8b8c2')
    # 房子、电线杆、树
    ink_house(d, 16, G, 70, 40)
    ink_house(d, 150, G, 56, 50, roof=10, door=False)
    ink_house(d, 330, G, 80, 36, roof=16)
    for px_ in (110, 270, 440):                                                 # 电线杆
        line(d, (px_, G, px_, 50), INK)
        line(d, (px_ - 8, 58, px_ + 8, 58), INK)
        line(d, (px_ - 6, 64, px_ + 6, 64), INK)
    for a, b in ((110, 270), (270, 440)):
        polyline(d, sag_pts((a - 8, 58), (b - 8, 58), 8, 30), INK2)
        polyline(d, sag_pts((a + 6, 64), (b + 6, 64), 9, 30), INK2)
    # 树（只有轮廓 + 几笔叶子）
    tx = 236
    line(d, (tx, G, tx, G - 30), INK)
    line(d, (tx + 4, G, tx + 3, G - 30), INK)
    d.arc((tx - 24, G - 70, tx + 26, G - 24), 150, 30, fill=C(INK))
    d.arc((tx - 18, G - 76, tx + 18, G - 46), 180, 0, fill=C(INK))
    for k in range(10):
        a = k * .6
        x, y = tx + 14 * math.cos(a), G - 50 + 10 * math.sin(a)
        line(d, (x, y, x + 3, y + 2), INK2)
    # 一只画出来的猫（喜剧点缀）
    cx = 300
    d.arc((cx, G - 8, cx + 12, G + 2), 180, 360, fill=C(INK))
    line(d, (cx + 1, G - 4, cx + 1, G - 9), INK)
    line(d, (cx + 1, G - 9, cx + 3, G - 6), INK)
    line(d, (cx + 12, G - 3, cx + 16, G - 9), INK)
    # 远处的山：一笔带过
    pts = [(x, 92 + 8 * math.sin(x / 40.0) + 4 * math.sin(x / 13.0)) for x in range(0, W, 4)]
    polyline(d, pts, '#a8a8b4')
    # 太阳：一个圆圈 + 几道线
    d.ellipse((396, 18, 414, 36), outline=C(INK2))
    for k in range(8):
        a = k * math.pi / 4
        line(d, (405 + 12 * math.cos(a), 27 + 12 * math.sin(a), 405 + 15 * math.cos(a), 27 + 15 * math.sin(a)), INK2)
    return im, G


def float_notes_strip(W=480, n=8, seed=5):
    """空中飘的折纸：每张上下浮 2 px、首尾接得上（整宽帧条，n 帧）"""
    rng = np.random.RandomState(seed)
    notes = [(rng.randint(10, W - 20), rng.randint(46, 110), rng.uniform(0, 2 * math.pi), rng.randint(6, 10)) for _ in range(9)]
    out = Image.new('RGBA', (W * n, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    for f in range(n):
        for x, y, ph, w in notes:
            yy = y + round(2 * math.sin(ph + 2 * math.pi * f / n))
            X = f * W + x
            rect(d, (X, yy, X + w, yy + w * 2 // 3), '#fbf8f0')
            rect(d, (X, yy, X + w, yy + w * 2 // 3), None, INK)
            line(d, (X, yy, X + w, yy + w * 2 // 3), INK2)
            line(d, (X + 1, yy + w * 2 // 3 + 2, X + w + 1, yy + w * 2 // 3 + 2), '#d8d2c0')
    return out


def paper_world():
    W = 480
    im, G = paper_world_img()
    notes = float_notes_strip(W, 8)
    layers = {'paper': im, 'notes': notes}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(paper_a=[160, 120], paper_b=[320, 120], house_l=[50, 146], tree=[236, 146], house_r=[370, 146],
                             crease_x=[120, 240, 360], crease_y=[60, 120], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/paper_world/paper', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': 'bg/paper_world/notes', 'n': 8, 'fps': 4, 'w': W, 'h': 180, 'x': 0, 'y': 0, 'k': 1}],
                fg=[])
    pv = im.copy()
    pv.alpha_composite(notes.crop((0, 0, W, 180)))
    preview('paper_world', {'room': pv}, ['room'], W)
    save_layers('paper_world', layers, meta)
    return meta


# ============================================================ 杜王町图书馆一角 library（320 宽，白天）
#   高书架两排（深色木、彩色书脊）、中间一扇高窗透进光柱，前面一张长阅览桌 + 绿罩台灯 + 椅子；
#   右边一张推荐书展台，立着「推荐图书」的牌子（key 'book' = 展台上放着《谜》：紫封面，隐约一张脸，和安杰罗岩同一种隐约画法）。
def bookshelf(d, x0, x1, top, G, seed=0):
    rng = np.random.RandomState(seed)
    rect(d, (x0, top, x1, G), '#5a3a24')
    line(d, (x0, top, x1, top), '#7a5636')
    rect(d, (x0 - 2, top - 4, x1 + 2, top), '#6a4630')
    for sy in range(top + 4, G - 18, 20):
        rect(d, (x0 + 3, sy, x1 - 3, sy + 16), '#2e1e12')
        x = x0 + 4
        while x < x1 - 5:
            w_ = rng.randint(2, 5)
            h_ = rng.randint(10, 16)
            col = ['#8a3a34', '#3a5a8a', '#e8e0cc', '#4a7a4a', '#c8a050', '#5a4a6a', '#a86a3a', '#2e4a5e'][rng.randint(8)]
            if rng.rand() < .06:                                                 # 斜靠着的一本
                poly(d, [(x, sy + 16), (x + 3, sy + 16), (x + 7, sy + 16 - h_), (x + 4, sy + 16 - h_)], col)
                x += 7
                continue
            rect(d, (x, sy + 16 - h_, x + w_ - 1, sy + 15), col)
            if w_ >= 3:
                px(d, x + 1, sy + 18 - h_, '#f0d070' if rng.rand() < .5 else '#ffffff')
            x += w_
        rect(d, (x0 + 3, sy + 16, x1 - 3, sy + 19), '#6a4630')
        line(d, (x0 + 3, sy + 16, x1 - 3, sy + 16), '#8a6644')
    rect(d, (x0 + 3, G - 14, x1 - 3, G), '#4a2e1c')                               # 底下的柜门
    for x in range(x0 + 3, x1 - 3, 20):
        line(d, (x, G - 14, x, G), '#3a2414')
    line(d, (x1, top, x1, G), '#3e2818')


def library():
    W, G = 320, 140
    im = new(W, 180)
    im = grad(im, (0, 0, W, G), ('#e4dcc8', '#ece4d2', '#e0d6c0'))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 8), '#c8bca4')
    line(d, (0, 8, W, 8), '#a89c84')
    for x in range(20, W, 64):                                                  # 天花板的日光灯
        rect(d, (x, 2, x + 28, 5), '#f8f8f0')
        line(d, (x, 6, x + 28, 6), '#d8d4c8')
    # 中间高窗 + 光柱
    wx0, wx1 = 124, 182
    rect(d, (wx0 - 3, 14, wx1 + 3, 104), '#8a7458')
    im = grad(im, (wx0, 17, wx1, 101), ('#bcdcf0', '#d8ecf6', '#eef6fa'))
    d = ImageDraw.Draw(im)
    for k in range(3):                                                          # 窗外的树梢
        ellipse(d, (wx0 + 4 + k * 18, 80 - k % 2 * 6, wx0 + 22 + k * 18, 104), '#9cc488')
    line(d, ((wx0 + wx1) // 2, 17, (wx0 + wx1) // 2, 101), '#8a7458')
    for y in (45, 73):
        line(d, (wx0, y, wx1, y), '#8a7458')
    line(d, (wx0 + 2, 19, wx0 + 10, 27), '#ffffff')
    # 光柱（斜着打到地板上：用抖动淡黄盖一层）
    sh = Image.new('RGBA', (W, 180), (0, 0, 0, 0))
    a = np.array(sh)
    for y in range(101, 176):
        t = (y - 101) / 75
        xa = wx0 + 18 * t + 6
        xb = wx1 + 34 * t
        for x in range(int(xa), int(xb)):
            if (x + y) % 2 == 0 and BAYER[y % 4, x % 4] < .32 - .22 * t:
                a[y, x] = (*c3('#fff4d0'), 255)
    sh = Image.fromarray(a, 'RGBA')
    # 两排书架
    bookshelf(d, 6, 116, 20, G, seed=1)
    bookshelf(d, 190, 244, 20, G, seed=2)
    # 书架侧面的分类牌
    for x, t in ((60, 'A'), (216, 'K')):
        rect(d, (x - 6, 12, x + 6, 19), '#2e4a5e')
        letters_small(d, x - 1, 13, t, '#f4f0e6')
    # 右：推荐书展台 + 牌子
    sx0 = 252
    rect(d, (sx0, 108, sx0 + 56, 112), '#7a5434')
    line(d, (sx0, 108, sx0 + 56, 108), '#9a7450')
    rect(d, (sx0 + 4, 112, sx0 + 52, G - 1), '#6a4a2e')
    line(d, (sx0 + 4, 124, sx0 + 52, 124), '#5a3e26')
    for k, col in enumerate(('#3a5a8a', '#c8a050', '#8a3a34')):                 # 平放的几本 + 立着的两本
        if k == 1:
            continue
        x = sx0 + 6 + k * 18
        poly(d, [(x, 107), (x + 12, 107), (x + 10, 96), (x + 2, 96)], col)
        line(d, (x + 2, 96, x + 10, 96), '#f4f0e6')
        line(d, (x + 5, 104, x + 9, 104), '#7a6a5a')
    rect(d, (sx0 + 22, 104, sx0 + 34, 107), '#e8e0cc')                            # 中间空出来的书架（放《谜》的地方）
    line(d, (sx0 + 22, 104, sx0 + 34, 104), '#c8c2b0')
    rect(d, (sx0 + 12, 64, sx0 + 44, 88), '#f4f0e6')                              # 牌子
    rect(d, (sx0 + 12, 64, sx0 + 44, 88), None, '#8a6a48')
    kanji(im, sx0 + 13, 66, '推荐', '#c8282a')
    kanji(im, sx0 + 13, 76, '图书', '#2a2a30')
    d = ImageDraw.Draw(im)
    for x in (sx0 + 16, sx0 + 40):
        line(d, (x, 88, x, 95), '#8a6a48')
    # 地板（灰绿地毯）
    rect(d, (0, G, W, 180), '#7a8a7a')
    im = grad(im, (0, G, W, 180), ('#6e7e6e', '#7a8a7a', '#869686'))
    d = ImageDraw.Draw(im)
    noise_specks(im, (0, G, W, 180), ['#6a7a6a', '#8a9a8a'], 500, 11)
    d = ImageDraw.Draw(im)
    line(d, (0, G, W, G), '#5a6a5a')
    im.alpha_composite(sh)
    d = ImageDraw.Draw(im)
    # 阅览长桌 + 台灯 + 椅子（靠墙，桌面 y 134；人走在桌子前面）
    tx0, tx1, ty = 40, 200, 140
    for cx in (64, 112, 160):                                                   # 后排椅子（桌子后面露出椅背）
        rect(d, (cx - 7, ty - 18, cx + 7, ty - 6), '#8a5a3a')
        line(d, (cx - 7, ty - 18, cx + 7, ty - 18), '#a87a54')
    rect(d, (tx0, ty - 6, tx1, ty - 2), '#9a6e46')
    line(d, (tx0, ty - 6, tx1, ty - 6), '#c09468')
    rect(d, (tx0, ty - 2, tx1, ty), '#6a4a2e')
    for x in (tx0 + 4, tx1 - 7):
        rect(d, (x, ty, x + 3, ty + 7), '#5a3e26')
    for cx in (80, 160):                                                        # 绿罩台灯
        rect(d, (cx - 1, ty - 14, cx, ty - 7), '#c8a050')
        poly(d, [(cx - 8, ty - 14), (cx + 7, ty - 14), (cx + 5, ty - 19), (cx - 6, ty - 19)], '#2e7a5a')
        line(d, (cx - 6, ty - 19, cx + 5, ty - 19), '#4a9a76')
        rect(d, (cx - 4, ty - 7, cx + 3, ty - 6), '#c8a050')
    for x in (100, 128):                                                        # 桌上摊开的书
        poly(d, [(x, ty - 7), (x + 8, ty - 8), (x + 16, ty - 7), (x + 16, ty - 6), (x, ty - 6)], '#f4f0e6')
        line(d, (x + 8, ty - 8, x + 8, ty - 6), '#c8c2b0')
    # 《谜》（key 'book'）：立在展台中间
    book = new(W, 180)
    bd = ImageDraw.Draw(book)
    bx, by = sx0 + 22, 90
    rect(bd, (bx, by, bx + 12, by + 16), '#4a2a5a')
    rect(bd, (bx, by, bx + 1, by + 16), '#2e1a3a')
    line(bd, (bx + 2, by + 1, bx + 12, by + 1), '#6a4a7a')
    px(bd, bx + 5, by + 6, '#5e3e6e')                                            # 隐约的一张脸：两只眼一张嘴，只比底色亮一点
    px(bd, bx + 9, by + 6, '#5e3e6e')
    line(bd, (bx + 6, by + 10, bx + 8, by + 10), '#5e3e6e')
    line(bd, (bx + 4, by + 13, bx + 10, by + 13), '#c8a050')
    layers = {'room': im, 'book': book}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(window=[153, 60], sun=[170, 160], table=[120, 146], display=[280, 148], book=[sx0 + 28, by + 8],
                             sign=[sx0 + 28, 76], shelf_l=[60, 146], shelf_r=[216, 146], walk_x=[8, 312]),
                layers=[{'type': 'pano', 'image': 'bg/library/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/library/book', 'k': 1, 'x': 0, 'y': 0, 'key': 'book'}],
                fg=[])
    pv = im.copy()
    pv.alpha_composite(book)
    preview('library', {'room': pv}, ['room'], W)
    save_layers('library', layers, meta)
    return meta


SCENES = {'transmission_tower': transmission_tower, 'miyamoto_house': miyamoto_house, 'paper_world': paper_world, 'library': library}


def main(keys):
    path = os.path.join(LIB.META, 'bg_ch10.json')
    meta = LIB.load_json(path, {}) or {}
    for k in keys or SCENES:
        meta[k] = SCENES[k]()
        print('背景', k)
    LIB.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
