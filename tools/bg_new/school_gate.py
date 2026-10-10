"""预览：python -B tools\\bg_new\\bgpro_preview.py school_gate

春天的校门（游戏层加细节，2026-10-10 bg-pro）：两层 pano（远层 400 宽 k 0.5、近层 480 宽 k 1）和
petals 花瓣层的参数都和原导出 bg_jojo.exp_school_gate 一样；门柱 x 194–204 / 296–306、铁门 x 264–294、
校名牌 x 196–202 不动（剧情的调查点 gate_plaque 200、gate 282、走进校门的触发区 x 212–258 照旧）。

  远层：校舍屋顶栏杆、每层楼板线、窗框中挺、几扇窗拉着窗帘；挂一条竖幅；钟楼的刻度和校徽；
        玄关玻璃门里看得见鞋柜；右边体育馆的拱顶（远层 y 96 以下被近层围墙挡住，只有门口那一段看得见）；旗杆；远处楼的窗
  近层：围墙的混凝土分块、水渍、顶上压顶的高光；门柱花岗岩斑点 + 顶上门灯；校名牌加边框；
        铁门底下的轮子和地上的轨道；围墙边两辆自行车；告示板（贴着海报）；人行道的井盖和排水篦子；
        树下落花更密
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
from PIL import ImageDraw
from engine import bg_asia as A
from engine.core import gradient, hrange, paste, mix, H

C = A._c4
SG_W = 480


def R(d, box, col, outline=None):
    d.rectangle(box, fill=C(col), outline=C(outline) if outline else None)


def L(d, pts, col, width=1):
    d.line(pts, fill=C(col), width=width)


def P(d, x, y, col):
    d.point((round(x), round(y)), fill=C(col))


def bicycle(d, x, y, frame=(70, 90, 130), s=1.0):
    """侧面自行车，后轮着地点 (x, y)。"""
    r = 5 * s
    for wx in (x, x + 14 * s):
        d.ellipse((wx - r, y - 2 * r, wx + r, y), outline=C((50, 50, 56)))
        P(d, wx, y - r, (150, 150, 160))
    L(d, (x, y - r, x + 6 * s, y - r - 6 * s, x + 12 * s, y - r - 6 * s, x + 14 * s, y - r), frame)
    L(d, (x + 6 * s, y - r - 6 * s, x + 7 * s, y - r), frame)
    L(d, (x + 7 * s, y - r, x + 14 * s, y - r), frame)
    L(d, (x + 5 * s, y - r - 8 * s, x + 7 * s, y - r - 8 * s), (40, 40, 44))         # 车座
    L(d, (x + 12 * s, y - r - 6 * s, x + 12 * s, y - r - 9 * s), frame)
    L(d, (x + 11 * s, y - r - 9 * s, x + 14 * s, y - r - 9 * s), (40, 40, 44))      # 车把
    R(d, (x + 13 * s, y - r - 9 * s, x + 17 * s, y - r - 6 * s), (176, 176, 180), (110, 110, 116))   # 车筐


@lru_cache(maxsize=1)
def layers():
    # ------------------------------------------------ 远层（400 宽，k 0.5）
    far = A._new(400, H)
    gradient(far, (0, 0, 400, 110), [(108, 170, 236), (164, 206, 244), (236, 232, 222), (252, 226, 200)], bands=7)
    d = ImageDraw.Draw(far)
    for i in range(4):
        cl = A._cloud_sprite(hrange(30, 60, i, 3), hrange(9, 14, i, 4), 70 + i)
        paste(far, cl, int(hrange(0, 380, i, 5)), int(hrange(6, 40, i, 6)))
    for i in range(14):                                                        # 远处的楼 + 窗
        x = i * 30 + hrange(-6, 6, i, 7)
        h = hrange(10, 26, i, 8)
        bw = hrange(14, 26, i, 9)
        R(d, (x, 100 - h, x + bw, 104), (170, 186, 206))
        for wy in range(int(100 - h) + 3, 100, 4):
            for wx in range(int(x) + 2, int(x + bw) - 1, 4):
                P(d, wx, wy, (196, 208, 224))
    # 右边体育馆（拱顶）
    R(d, (344, 66, 398, 104), (210, 206, 196))
    d.chord((340, 52, 402, 82), 180, 360, fill=C((120, 140, 150)))
    L(d, (340, 67, 402, 67), (100, 116, 126))
    for x in range(348, 396, 8):
        R(d, (x, 76, x + 4, 90), (150, 180, 206))
    # 校舍
    bx0, bx1 = 70, 350
    R(d, (bx0, 38, bx1, 104), (226, 222, 210))
    R(d, (bx0, 36, bx1, 39), (180, 176, 168))
    for x in range(bx0, bx1 + 1, 6):                                            # 屋顶栏杆
        L(d, (x, 31, x, 36), (150, 156, 160))
    L(d, (bx0, 31, bx1, 31), (150, 156, 160))
    for fl in range(3):
        y = 46 + fl * 19
        L(d, (bx0, y - 3, bx1, y - 3), (200, 196, 186))
        L(d, (bx0, y - 2, bx1, y - 2), (236, 234, 226))
        for k, x in enumerate(range(bx0 + 6, bx1 - 10, 14)):
            if 184 <= x <= 226:
                continue
            R(d, (x, y, x + 9, y + 10), (120, 160, 196))
            L(d, (x, y, x + 9, y), (90, 110, 130))
            L(d, (x + 4, y + 1, x + 4, y + 10), (190, 196, 200))              # 中挺
            P(d, x + 2, y + 2, (210, 230, 246))
            if (k * 7 + fl * 3) % 5 == 0:                                       # 拉着窗帘
                R(d, (x + 5, y + 1, x + 9, y + 10), (236, 230, 206))
            if (k * 5 + fl) % 7 == 0:
                R(d, (x + 1, y + 1, x + 3, y + 10), (226, 220, 200))
            L(d, (x - 1, y + 11, x + 10, y + 11), (196, 192, 182))             # 窗台
    # 竖幅
    R(d, (126, 40, 133, 92), (250, 250, 246), (180, 176, 168))
    for k in range(6):
        L(d, (128, 44 + k * 8, 131, 44 + k * 8), (200, 50, 50) if k < 2 else (40, 40, 50))
        L(d, (129, 45 + k * 8, 130, 47 + k * 8), (200, 50, 50) if k < 2 else (40, 40, 50))
    # 钟楼：刻度、校徽
    R(d, (186, 14, 224, 104), (236, 232, 222))
    R(d, (184, 12, 226, 16), (180, 176, 168))
    L(d, (187, 17, 187, 103), (250, 248, 240))
    L(d, (223, 17, 223, 103), (206, 202, 192))
    d.ellipse((196, 20, 214, 38), fill=C((250, 250, 244)), outline=C((70, 70, 80)))
    for k in range(12):
        a = k / 12 * math.pi * 2
        P(d, 205 + math.cos(a) * 7, 29 + math.sin(a) * 7, (110, 110, 120))
    L(d, (205, 29, 205, 23), (30, 30, 40))
    L(d, (205, 29, 209, 31), (30, 30, 40))
    d.polygon([(205, 60), (210, 64), (208, 70), (202, 70), (200, 64)], fill=C((200, 170, 70)), outline=C((140, 110, 40)))
    P(d, 205, 65, (250, 236, 170))
    for fl in range(3):                                                         # 楼梯间的小窗
        R(d, (202, 44 + fl * 6, 208, 47 + fl * 6), (140, 176, 206))
    # 玄关：雨棚 + 玻璃门里的鞋柜
    R(d, (192, 76, 218, 79), (170, 166, 158))
    L(d, (192, 79, 218, 79), (120, 118, 112))
    R(d, (196, 80, 214, 104), (150, 176, 196))
    for yy in range(83, 102, 4):
        L(d, (197, yy, 213, yy), (180, 160, 120))
    for xx in range(198, 214, 4):
        L(d, (xx, 82, xx, 101), (150, 130, 96))
    L(d, (205, 80, 205, 104), (60, 70, 90))
    d.rectangle((196, 80, 214, 104), outline=C((80, 90, 110)))
    P(d, 199, 84, (220, 236, 246))
    P(d, 209, 84, (220, 236, 246))
    for k in range(6):                                                          # 台阶
        y = 104 + k * 3
        R(d, (180 - k * 6, y, 230 + k * 6, y + 2), (200, 196, 188))
        L(d, (180 - k * 6, y + 2, 230 + k * 6, y + 2), (150, 146, 140))
    R(d, (0, 104, 400, H), (196, 176, 140))                                    # 操场
    for i in range(30):
        x0 = hrange(0, 400, i, 81)
        L(d, (round(x0), round(hrange(108, 178, i, 82)), round(x0 + hrange(3, 10, i, 83)), round(hrange(108, 178, i, 82))), (186, 166, 132))
    R(d, (150, 104, 260, H), (186, 180, 168))
    for y in range(110, H, 6):
        L(d, (150, y, 260, y), (170, 164, 154))
    # 旗杆
    L(d, (262, 44, 262, 104), (200, 200, 206))
    P(d, 262, 43, (230, 200, 90))
    R(d, (263, 46, 271, 51), (250, 250, 250))
    d.ellipse((265, 47, 268, 50), fill=C((210, 50, 50)))
    for i in range(6):
        bx = 84 + i * 26 if i < 3 else 280 + (i - 3) * 30            # 左边三丛让给自行车棚，往右挪
        d.ellipse((bx - 9, 100, bx + 9, 112), fill=C((90, 140, 90)))
        d.ellipse((bx - 7, 100, bx + 5, 106), fill=C((120, 170, 110)))
    far = A._grade(far, sat=0.8, val=0.97)

    # ------------------------------------------------ 近层（480 宽，k 1）
    near = A._new(SG_W, H)
    d = ImageDraw.Draw(near)
    gx0, gx1 = 206, 294
    for (x0, x1) in ((0, gx0 - 10), (gx1 + 10, SG_W)):
        R(d, (x0, 100, x1, 132), (196, 192, 182))
        R(d, (x0, 96, x1, 101), (140, 138, 132))
        L(d, (x0, 96, x1, 96), (210, 208, 200))
        L(d, (x0, 101, x1, 101), (120, 118, 112))
        for x in range(x0 + 20, x1, 40):
            L(d, (x, 101, x, 132), (176, 172, 162))
            L(d, (x + 1, 102, x + 1, 132), (208, 204, 196))
        for y in (112, 122):
            L(d, (x0, y, x1, y), (186, 182, 172))
        for i in range(int((x1 - x0) / 14)):                                   # 水渍
            sx = x0 + hrange(2, x1 - x0 - 2, x0, i, 91)
            L(d, (round(sx), 102, round(sx), round(102 + hrange(3, 14, x0, i, 92))), (182, 178, 168))
        for i in range(int((x1 - x0) / 3)):
            P(d, x0 + hrange(0, x1 - x0, x0, i, 93), hrange(102, 131, x0, i, 94), (184, 180, 170) if i % 2 else (206, 202, 192))
        L(d, (x0, 132, x1, 132), (120, 118, 112))
    # 告示板（右边围墙）
    R(d, (366, 104, 400, 124), (120, 96, 70), (80, 60, 40))
    R(d, (368, 106, 398, 122), (200, 190, 160))
    for (bx, by, bw, bh, col) in ((370, 107, 8, 10, (250, 250, 240)), (380, 108, 7, 8, (250, 220, 140)),
                                  (389, 107, 8, 11, (190, 220, 246))):
        R(d, (bx, by, bx + bw, by + bh), col)
        for k in range(2, bh - 1, 2):
            L(d, (bx + 1, by + k, bx + bw - 2, by + k), (120, 120, 130))
    L(d, (366, 103, 400, 103), (90, 70, 50))
    # 围墙边两辆自行车（门柱左边）
    bicycle(d, 160, 134, (60, 70, 120))
    bicycle(d, 176, 134, (150, 50, 50))
    # 门柱（花岗岩 + 门灯）+ 校名牌
    for x in (gx0 - 12, gx1 + 2):
        R(d, (x, 80, x + 10, 134), (178, 172, 160), (90, 86, 80))
        R(d, (x - 1, 78, x + 11, 82), (150, 146, 136), (90, 86, 80))
        L(d, (x + 1, 83, x + 1, 133), (210, 206, 196))
        for i in range(26):
            P(d, x + 2 + hrange(0, 8, x, i, 95), hrange(84, 132, x, i, 96), (150, 144, 134) if i % 2 else (200, 196, 186))
        R(d, (x + 3, 74, x + 7, 77), (120, 120, 126))
        d.ellipse((x + 2, 67, x + 8, 74), fill=C((246, 244, 230)), outline=C((150, 146, 136)))
        P(d, x + 4, 69, (255, 255, 255))
    px = gx0 - 10
    R(d, (px - 1, 87, px + 7, 125), (90, 70, 50))
    R(d, (px, 88, px + 6, 124), (226, 214, 186), (80, 60, 40))
    for k in range(5):
        y = 91 + k * 7
        L(d, (px + 2, y, px + 4, y), (30, 30, 30))
        L(d, (px + 3, y, px + 3, y + 4), (30, 30, 30))
        L(d, (px + 2, y + 4, px + 4, y + 3), (30, 30, 30))
    # 铁门（半开）：轮子 + 轨道
    d.rectangle((gx1 - 30, 104, gx1, 132), outline=C((60, 64, 72)))
    for x in range(gx1 - 30, gx1, 4):
        L(d, (x, 104, x, 132), (70, 74, 84))
        P(d, x, 103, (90, 94, 104))
    L(d, (gx1 - 30, 118, gx1, 118), (70, 74, 84))
    L(d, (gx1 - 30, 110, gx1, 110), (90, 94, 104))
    # 人行道
    R(d, (0, 132, SG_W, H), (172, 168, 160))
    for y in (140, 152, 168):
        L(d, (0, y, SG_W, y), (150, 146, 140))
    for i, y0 in enumerate((132, 140, 152, 168)):
        step = 16 + i * 8
        for x in range((i * 7) % step, SG_W, step):
            L(d, (x, y0, x + (x - 240) * 0.05, min(H, y0 + 12 + i * 4)), (154, 150, 144))
    R(d, (0, 132, SG_W, 134), (200, 196, 188))
    L(d, (gx0 - 10, 134, gx1 + 4, 134), (130, 130, 136))                      # 门口的轨道
    for x in (gx1 - 28, gx1 - 4):
        d.ellipse((x - 2, 130, x + 2, 134), fill=C((60, 64, 72)))
    d.ellipse((92, 158, 112, 164), fill=C((120, 118, 114)), outline=C((96, 94, 90)))   # 井盖
    for k in range(-8, 9, 3):
        P(d, 102 + k, 161, (100, 98, 94))
    R(d, (410, 146, 424, 149), (110, 108, 104))                               # 排水篦子
    for x in range(411, 424, 2):
        L(d, (x, 146, x, 149), (80, 78, 76))
    for (cx, cy, r, sd) in ((40, 62, 46, 1), (150, 54, 40, 2), (350, 58, 44, 3), (446, 66, 40, 4)):
        A._sakura(d, cx, cy, r, sd)
    for i in range(160):
        x = hrange(0, SG_W, i, 21)
        y = hrange(134, H, i, 22)
        P(d, x, y, (246, 186, 206) if i % 3 else (255, 220, 230))
    for (cx, n) in ((38, 40), (148, 34), (348, 40), (444, 30)):              # 树下落花更密
        for i in range(n):
            x = cx + hrange(-30, 30, cx, i, 23)
            y = hrange(134, 150, cx, i, 24)
            P(d, x, y, (246, 186, 206) if i % 3 else (255, 220, 230))
    near = A._grade(near, sat=0.9, val=0.98)
    return far, near


def export(ex, BJ):
    far, near = layers()
    W = BJ.W
    petals = dict(type='petals', n=26, colors=['#f4a0be', '#ffd6e4'], seed=31, y0=-6, y1=184,
                  vx=-12.7, vy=34.5, per=[4.0, 7.0], x0=[-20, W + 60], drift=70, sway=6, swayW=2.3,
                  k=0.2, wrapX=40)
    lay = [dict(type='pano', image=ex.img('far', far), k=0.5, x=0, y=0),
           dict(type='pano', image=ex.img('near', near), k=1.0, x=0, y=0),
           petals]
    anchors = dict(gate=[206, 294], walk_x=[16, 464], clock=[205, 29], building_door=[205, 104],
                   trees=[[40, 62], [150, 54], [350, 58], [446, 66]])
    st = ex.stage(480, 150, (140, 176), lay, anchors=anchors)
    if ex.check_on:
        for camX in (0, 40, 80, 120, 160):
            want = BJ.Image.new('RGBA', (W, BJ.H), (0, 0, 0, 255))
            paste(want, far, -math.floor(camX * 0.5), 0)
            paste(want, near, -math.floor(camX), 0)
            ex.checked('校门 camX=%d 两层 pano vs 直接贴图' % camX,
                       BJ.ndiff_rgba(BJ.ref_render(st, ex.images, camX, 0, only={'pano'}), want))
        ex.checked('校门 远层不透明', int((np.array(far)[:, :, 3] != 255).sum()))
        ex.checked('校门 近层地面不透明（y ≥ 132）', int((np.array(near)[132:, :, 3] != 255).sum()))
    return st
