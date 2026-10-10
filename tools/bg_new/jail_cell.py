"""【草稿，还没接进 bg_jojo.py、没跑构建自检、没进游戏】预览：python -B tools\\bg_new\\jail_cell.py → _preview\\jail_cell_solo.png

序章拘留所（游戏层重画，2026-10-10 主代理）：房间透视、所有物品的位置和原工程 A.jail_cell 一样
（调查点、伸手坐标、铁栏 6 张 pick、fgDepth 144 都不用改），每样东西画细：

  墙：水泥砌块缝、水渍、裂缝、墙脚污垢、右侧墙上的《留置须知》；「正」字划了三个半（台词：住了十七天）
  床：钢管床架、厚床垫、条纹毛毯的褶子和垂边、枕头；床底下一双鞋、一只哑铃
  左：漫画 / 杂志两堆（书脊带白色书名条，最上面一本是这周的新刊）、靠墙两本精装书，地上摊开一本
  右：木箱换成一张两层小木桌——上层放收音机（喇叭网、磁带仓、调频刻度、指示灯位置不变），下层放书和磁带盒
  罐子：三个啤酒罐（一个压扁倒着），底下压着一张纸条（台词：『求你别再拿了』）
  海报：摇滚海报 + 胶带 + 卷起的角 + 左下角一个拳印（台词：这个是我）
  地面：水泥地裂纹、排水口；走廊地面分块、接缝、栏杆影子
动画和原导出一样：灯泡闪（50 帧 @12 fps）、收音机指示灯（2 帧 @2 fps）。
"""
import sys
sys.dont_write_bytecode = True

import math
import os
from functools import lru_cache

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np
from PIL import Image, ImageDraw
from engine import bg_asia as A

W, H = 320, 180
C = A._c4
JBW = (64, 30, 256, 114)        # 后墙框（和原工程 _JBW 一样）
VP = (160, 70)                   # 消失点
CX = 182                         # 铁栏掰开的中心（规划 §5.1 jail_bars cx=182）
BULB_N = 50                      # 12 fps × 50 帧
BULB_BOX = (129, 14, 192, 68)
LED_BOX = (224, 109, 225, 110)


def jp(x, y, s):
    return (VP[0] + (x - VP[0]) * s, VP[1] + (y - VP[1]) * s)


def rect(d, box, fill, outline=None):
    d.rectangle(box, fill=C(fill), outline=C(outline) if outline else None)


def line(d, pts, fill, width=1):
    d.line(pts, fill=C(fill), width=width)


def px(d, x, y, fill):
    d.point((x, y), fill=C(fill))


# ---------------------------------------------------------------- 房间
def room(img):
    d = ImageDraw.Draw(img)
    bx0, by0, bx1, by1 = JBW
    dado, fy = 80, 143
    d.polygon([(0, 0), (W, 0), (bx1, by0), (bx0, by0)], fill=C((84, 82, 78)))
    for k in range(1, 5):
        y = jp(0, by0, 1 + k * 0.45)[1]
        if y > 0:
            line(d, (0, y, W, y), (74, 72, 68))
    # 天花板：沿墙的水管（带两个管卡）+ 通风口
    line(d, (0, 9, bx0 + 20, by0 + 3), (110, 106, 100), 2)
    line(d, (0, 8, bx0 + 20, by0 + 2), (138, 134, 126))
    for t in (0.35, 0.7):
        x, y = round(bx0 * t * 1.2), round(9 + (by0 + 3 - 9) * t * 1.2)
        rect(d, (x - 1, y - 2, x + 1, y + 2), (70, 68, 64))
    vx0, vy0 = 186, 16
    d.polygon([(vx0, vy0), (vx0 + 22, vy0), (vx0 + 20, vy0 + 7), (vx0 + 2, vy0 + 7)], fill=C((60, 60, 58)), outline=C((44, 44, 44)))
    for i in range(4):
        line(d, (vx0 + 3, vy0 + 2 + i * 1.5, vx0 + 19, vy0 + 2 + i * 1.5), (96, 94, 90))
    # 侧墙：上米黄、下墙裙绿（透视）
    ldy = VP[1] + (dado - VP[1]) * (VP[0] / (VP[0] - bx0))
    d.polygon([(0, 0), (bx0, by0), (bx0, dado), (0, ldy)], fill=C((168, 160, 138)))
    d.polygon([(0, ldy), (bx0, dado), (bx0, by1), (0, fy)], fill=C((74, 94, 84)))
    d.polygon([(W, 0), (bx1, by0), (bx1, dado), (W, ldy)], fill=C((178, 170, 148)))
    d.polygon([(W, ldy), (bx1, dado), (bx1, by1), (W, fy)], fill=C((80, 100, 90)))
    line(d, (0, ldy, bx0, dado), (56, 70, 62))
    line(d, (W, ldy, bx1, dado), (56, 70, 62))
    line(d, (0, ldy + 1, bx0, dado + 1), (110, 128, 114))
    line(d, (W, ldy + 1, bx1, dado + 1), (116, 134, 120))
    # 后墙
    rect(d, (bx0, by0, bx1, dado), (196, 188, 164))
    rect(d, (bx0, dado, bx1, by1), (92, 114, 102))
    line(d, (bx0, dado, bx1, dado), (62, 78, 70))
    line(d, (bx0, dado + 1, bx1, dado + 1), (120, 140, 126))
    # 水泥砌块缝（很淡，错缝）
    for r, y in enumerate(range(by0 + 7, dado - 1, 8)):
        line(d, (bx0 + 1, y, bx1 - 1, y), (186, 178, 154))
        for x in range(bx0 + (8 if r % 2 else 0), bx1, 16):
            if x > bx0:
                line(d, (x, y - 7, x, y - 1), (186, 178, 154))
    for x in (bx0, bx1):
        line(d, (x, by0, x, by1), (60, 62, 60))
    # 地面（水泥）
    d.polygon([(bx0, by1), (bx1, by1), (W, fy), (0, fy)], fill=C((112, 110, 108)))
    for k in range(1, 6):
        y = by1 + (fy - by1) * (k / 6) ** 1.3
        line(d, (0, y, W, y), (100, 98, 96))
    for x in range(bx0 + 24, bx1, 32):
        line(d, (x, by1, jp(x, by1, 1.66)[0], fy), (100, 98, 96))
    line(d, (bx0, by1, bx1, by1), (70, 70, 70))
    A._tex_noise(img, (0, 0, W, 146), 0.10, 5)
    d = ImageDraw.Draw(img)
    A._dither_rect(img, (bx0, by1 - 4, bx1 + 1, by1), (86, 104, 94), (70, 86, 78), 0.5)
    d = ImageDraw.Draw(img)
    # 水渍（左上角往下流）、裂缝（右上）
    for i, (x, y0, y1) in enumerate(((70, 31, 58), (72, 31, 66), (74, 31, 50), (78, 31, 44))):
        A._dither_rect(img, (x, y0, x + 2, y1), (196, 188, 164), (170, 156, 124), 0.55 - i * 0.08)
    d = ImageDraw.Draw(img)
    line(d, [(244, 31), (246, 36), (243, 40), (247, 46), (245, 52)], (150, 142, 122))
    line(d, [(246, 36), (250, 38)], (150, 142, 122))
    # 墙裙上的刮痕
    for x0, y0, n in ((96, 88, 9), (120, 96, 6), (232, 90, 8), (70, 102, 5)):
        line(d, (x0, y0, x0 + n, y0 - 1), (78, 98, 88))
    return d


def wall_items(img):
    d = ImageDraw.Draw(img)
    # 高窗：窗框有厚度、窗台、四根铁条、窗外天空
    wx0, wy0, wx1, wy1 = 206, 38, 236, 56
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), (120, 116, 104))
    line(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy0 - 3), (150, 146, 132))
    A.gradient(img, (wx0, wy0, wx1 + 1, wy1 + 1), [(150, 200, 240), (210, 234, 250)], bands=3)
    d = ImageDraw.Draw(img)
    line(d, (wx0 + 3, wy0 + 4, wx0 + 9, wy0 + 4), (240, 248, 252))      # 一小朵云
    line(d, (wx0 + 4, wy0 + 3, wx0 + 7, wy0 + 3), (240, 248, 252))
    for x in range(wx0 + 4, wx1, 6):
        line(d, (x, wy0, x, wy1), (50, 52, 60), 2)
        line(d, (x, wy0, x, wy1), (86, 90, 100))
    rect(d, (wx0 - 4, wy1 + 2, wx1 + 4, wy1 + 4), (140, 134, 120), (90, 88, 80))
    # 「正」字：三个半（17 划）
    c = (120, 112, 96)
    for k in range(3):
        tx0, ty0 = 76 + k * 9, 44
        line(d, (tx0, ty0, tx0 + 6, ty0), c)
        line(d, (tx0 + 3, ty0, tx0 + 3, ty0 + 8), c)
        line(d, (tx0 + 3, ty0 + 4, tx0 + 6, ty0 + 4), c)
        line(d, (tx0 + 1, ty0 + 3, tx0 + 1, ty0 + 8), c)
        line(d, (tx0 - 1, ty0 + 8, tx0 + 7, ty0 + 8), c)
    line(d, (103, 44, 109, 44), c)
    line(d, (106, 44, 106, 52), c)
    # 摇滚海报：胶带、卷角、闪电、乐队剪影、红色标题条、左下角拳印
    rect(d, (168, 36, 194, 70), (30, 28, 40), (20, 18, 26))
    A.gradient(img, (169, 37, 194, 70), [(44, 34, 58), (26, 24, 36)], bands=4)
    d = ImageDraw.Draw(img)
    rect(d, (171, 39, 191, 41), (220, 60, 70))
    for x in range(172, 191, 3):
        px(d, x, 40, (255, 210, 210))
    d.polygon([(178, 44), (186, 44), (181, 53), (188, 53), (174, 66), (178, 56), (172, 56)], fill=C((236, 200, 60)))
    line(d, [(178, 44), (186, 44)], (255, 236, 140))
    line(d, [(174, 66), (178, 56)], (180, 140, 30))
    for x, h in ((171, 5), (174, 6), (189, 6), (192, 4)):                # 乐队剪影
        rect(d, (x, 69 - h, x + 1, 68), (14, 12, 20))
        px(d, x, 68 - h - 1, (14, 12, 20))
    line(d, (176, 67, 187, 67), (210, 200, 220))                       # 小字
    d.polygon([(194, 64), (194, 70), (188, 70)], fill=C((176, 168, 146)))   # 右下角卷起
    line(d, [(188, 70), (194, 64)], (120, 112, 96))
    for (x, y) in ((167, 35), (192, 35), (167, 68)):                    # 胶带
        rect(d, (x, y, x + 3, y + 2), (214, 210, 190))
    # 拳印：左下角纸被打得凹进去——一圈不规则的暗坑（四个指节的小凹点）+ 上沿受光的皱褶 + 往外放射的折痕
    for (x, y) in ((171, 61), (172, 60), (173, 60), (174, 60), (175, 60), (176, 61), (176, 62), (175, 63), (172, 63), (171, 62)):
        px(d, x, y, (14, 12, 20))
    for x in (172, 174, 176):
        px(d, x, 61, (6, 4, 10))
    for (x, y) in ((171, 59), (173, 59), (175, 59), (177, 60)):
        px(d, x, y, (110, 100, 130))
    for pts in (((177, 61), (181, 59)), ((176, 63), (179, 66)), ((171, 63), (170, 66)), ((173, 59), (173, 56)), ((170, 60), (169, 58))):
        line(d, pts, (74, 68, 92))
    # 床头上方的木搁板：一排书（书脊 + 书名条）、一个搪瓷杯、一盒磁带
    rect(d, (98, 72, 138, 74), (138, 98, 58), (82, 56, 32))
    line(d, (99, 72, 137, 72), (176, 134, 84))
    for x in (102, 134):                                                 # 三角托架
        d.polygon([(x, 75), (x + 2, 75), (x + 2, 80)], fill=C((96, 80, 64)))
    x = 100
    for i, (w_, h, col) in enumerate(((3, 9, (180, 50, 50)), (2, 8, (230, 200, 90)), (3, 10, (60, 90, 150)), (2, 7, (240, 236, 220)),
                                       (3, 9, (70, 140, 90)), (2, 8, (150, 90, 190)), (3, 10, (40, 40, 50)))):
        rect(d, (x, 71 - h, x + w_, 71), col, (34, 30, 34))
        px(d, x + 1, 71 - h + 2, (250, 240, 200) if sum(col) < 500 else (60, 50, 60))
        x += w_ + 1
    d.polygon([(x, 71), (x + 6, 66), (x + 8, 68), (x + 2, 71)], fill=C((200, 120, 60)), outline=C((90, 50, 30)))   # 斜靠的一本
    rect(d, (124, 66, 128, 71), (230, 232, 236), (120, 124, 132))       # 搪瓷杯
    line(d, (129, 67, 130, 69), (120, 124, 132))
    line(d, (124, 67, 128, 67), (60, 110, 180))
    rect(d, (131, 68, 136, 71), (40, 40, 48), (16, 16, 20))             # 磁带盒
    line(d, (132, 69, 135, 69), (220, 200, 90))
    A._dither_rect(img, (99, 75, 138, 77), (196, 188, 164), (150, 140, 116), 0.5)   # 搁板的影子
    d = ImageDraw.Draw(img)
    # 右侧墙《留置须知》（透视纸）
    d.polygon([(264, 38), (281, 34), (281, 60), (264, 61)], fill=C((228, 222, 204)), outline=C((150, 144, 126)))
    line(d, (266, 40, 279, 37), (150, 60, 60))
    for i in range(6):
        y0 = 44 + i * 2.8
        line(d, (266, round(y0), 278 - (i % 3) * 2, round(y0 - 3 + i * 0.1)), (120, 116, 104))
    for (x, y) in ((265, 38), (280, 35)):
        px(d, x, y, (200, 60, 60))
    return d


# ---------------------------------------------------------------- 床
def bunk(img):
    d = ImageDraw.Draw(img)
    by1 = JBW[3]
    seat_b, seat_f = 94, 1.16
    bl, br = 92, 200
    fl_, fr_ = jp(bl, seat_b, seat_f)[0], jp(br, seat_b, seat_f)[0]
    fyb = jp(0, seat_b, seat_f)[1]
    floor_f = jp(0, by1, seat_f)[1]
    frame = (96, 110, 128)
    for x in (bl + 3, br - 3):                                          # 后腿
        line(d, (x, seat_b, x, by1), (60, 70, 84), 2)
    line(d, (bl, seat_b - 1, br, seat_b - 1), (70, 80, 96))            # 后横杆
    # 床底下：一双鞋、一只哑铃（在床的影子里）
    sh_y = round(floor_f) - 1
    for x0 in (118, 127):
        d.polygon([(x0, sh_y), (x0 + 7, sh_y), (x0 + 8, sh_y - 2), (x0 + 2, sh_y - 3), (x0, sh_y - 2)], fill=C((40, 32, 30)))
        line(d, (x0 + 1, sh_y - 2, x0 + 5, sh_y - 2), (86, 70, 60))
    line(d, (156, sh_y - 2, 166, sh_y - 2), (110, 110, 118))
    for x in (154, 166):
        rect(d, (x, sh_y - 4, x + 2, sh_y), (44, 44, 50), (24, 24, 28))
    # 床垫顶面 + 车线
    d.polygon([(bl, seat_b - 3), (br, seat_b - 3), (fr_, fyb - 3), (fl_, fyb - 3)], fill=C((206, 204, 190)))
    line(d, (bl + 2, seat_b - 2, br - 2, seat_b - 2), (190, 188, 172))
    # 条纹毛毯：皱在右边三分之二，褶子 + 垂边
    bxl = 128
    d.polygon([(bxl, seat_b - 5), (br, seat_b - 4), (fr_ + 1, fyb - 3), (bxl - 6, fyb - 2)], fill=C((96, 64, 60)))
    for k in range(4):
        x = bxl + 8 + k * 16
        line(d, (x, seat_b - 5, x - 3 + k, fyb - 2), (170, 150, 90), 2)
    for x in (bxl + 16, bxl + 40, bxl + 58):                            # 褶子的暗线 + 高光
        line(d, (x, seat_b - 4, x - 2, fyb - 3), (70, 44, 42))
        line(d, (x + 1, seat_b - 4, x - 1, fyb - 3), (122, 84, 76))
    for (x, y) in ((bxl + 26, seat_b - 4), (bxl + 50, seat_b - 3), (bxl + 66, seat_b - 4)):   # 毯子鼓起的几块
        d.ellipse((x - 4, y - 2, x + 4, y + 1), fill=C((110, 74, 68)))
        line(d, (x - 3, y - 2, x + 2, y - 2), (138, 98, 88))
    line(d, (bxl, seat_b - 5, br, seat_b - 4), (126, 88, 80))
    line(d, (bxl - 6, fyb - 2, fr_ + 1, fyb - 3), (70, 44, 40))
    rect(d, (bxl - 6, fyb - 2, fr_ + 1, fyb + 3), (84, 56, 52))
    for i, x in enumerate(range(round(bxl - 6), round(fr_), 7)):        # 垂边波浪
        px(d, x, round(fyb) + 4, (84, 56, 52))
        px(d, x + 1, round(fyb) + 4 + (i % 2), (84, 56, 52))
        line(d, (x + 3, fyb - 1, x + 3, fyb + 3), (150, 130, 80))
    line(d, (bxl - 6, fyb + 3, fr_ + 1, fyb + 3), (56, 36, 34))
    # 枕头（中间凹一道）
    d.rounded_rectangle((bl + 2, seat_b - 8, bl + 22, seat_b - 2), radius=2, fill=C((226, 224, 214)), outline=C((150, 148, 140)))
    line(d, (bl + 12, seat_b - 7, bl + 11, seat_b - 3), (196, 194, 184))
    line(d, (bl + 4, seat_b - 7, bl + 9, seat_b - 7), (246, 244, 236))
    # 床垫正面 + 钢管床架
    rect(d, (fl_, fyb - 3, fr_, fyb), (178, 176, 162))
    for x in range(round(fl_) + 4, round(bxl - 6), 6):
        px(d, x, round(fyb) - 2, (150, 148, 136))
    rect(d, (fl_, fyb + 1, fr_, fyb + 3), frame)
    line(d, (fl_, fyb + 1, fr_, fyb + 1), (150, 162, 180))
    line(d, (fl_, fyb + 4, fr_, fyb + 4), (50, 58, 70))
    for x in (fl_ + 2, fr_ - 2):
        line(d, (x, fyb + 4, x, floor_f), frame, 2)
        px(d, x + 1, fyb + 5, (150, 162, 180))
        rect(d, (x - 1, floor_f - 1, x + 2, floor_f), (50, 58, 70))
    A._dither_rect(img, (fl_ + 4, floor_f - 1, fr_ - 3, floor_f + 1), (112, 110, 108), (70, 70, 72), 0.6)


# ---------------------------------------------------------------- 书、杂志、桌子、收音机、罐子
SPINES = [(220, 70, 70), (240, 200, 70), (70, 120, 210), (240, 240, 230), (100, 180, 110),
          (230, 120, 170), (60, 60, 70), (250, 160, 60), (150, 90, 200)]


def magazine(d, x, y, w, col, title=True):
    """侧面看一本杂志：3 px 厚，书脊色 + 白色书名条 + 下面一道暗线。"""
    rect(d, (x, y - 2, x + w, y), col)
    if title:
        line(d, (x + 3, y - 1, x + 3 + w // 3, y - 1), tuple(min(255, c + 70) for c in col) if sum(col) < 600 else (90, 80, 90))
    px(d, x + w, y - 2, tuple(max(0, c - 50) for c in col))
    line(d, (x, y, x + w, y), (40, 36, 40))


def contact_shadows(img):
    """书堆、桌子、罐子底下的接地阴影（先画，东西压在上面）。"""
    for box in ((63, 123, 92, 126), (90, 127, 112, 130), (203, 123, 246, 127), (240, 130, 258, 134), (60, 110, 71, 112)):
        A._dither_rect(img, box, (112, 110, 108), (64, 62, 62), 0.55)


def books(img):
    contact_shadows(img)
    d = ImageDraw.Draw(img)
    # 靠墙两本精装书（竖着，书脊朝外）
    for x, col, h in ((62, (120, 40, 40), 15), (66, (40, 70, 110), 13)):
        rect(d, (x, 111 - h, x + 3, 111), col, (30, 26, 30))
        line(d, (x + 1, 113 - h, x + 1, 109 - h + 6), (220, 196, 120))
    # 左边一大堆（9 本）：每本错开一点
    y = 124
    for i in range(9):
        w_ = 22 - (i % 3)
        x = 66 + (i % 2) + (1 if i in (3, 6) else 0)
        magazine(d, x, y, w_, SPINES[i % len(SPINES)])
        y -= 3
    # 最上面一本：封面朝上的新刊（白底红标、斜放）
    d.polygon([(66, y - 1), (88, y - 2), (89, y + 1), (67, y + 2)], fill=C((246, 244, 236)), outline=C((60, 56, 60)))
    line(d, (68, y - 1, 76, y - 1), (220, 50, 60))
    line(d, (79, y, 86, y), (60, 110, 200))
    # 右边一小堆（5 本）
    y = 128
    for i in range(5):
        x = 92 + (i % 2) * 2
        magazine(d, x, y, 16, SPINES[(i + 3) % len(SPINES)])
        y -= 3
    # 地上摊开的一本：左右两页 + 小格子漫画
    d.polygon([(110, 134), (124, 132), (126, 137), (112, 139)], fill=C((236, 232, 214)))
    d.polygon([(124, 132), (138, 133), (138, 138), (126, 137)], fill=C((226, 220, 200)))
    line(d, [(124, 132), (126, 137)], (170, 164, 150))
    for (x0, y0, x1, y1) in ((113, 134, 117, 136), (118, 134, 122, 135), (114, 137, 122, 137), (127, 134, 131, 136), (132, 134, 136, 135)):
        line(d, (x0, y0, x1, y1), (90, 90, 110))
    rect(d, (128, 136, 134, 137), (220, 90, 90))


def table_and_radio(img):
    d = ImageDraw.Draw(img)
    # 两层小木桌（原来是木箱）：桌面 y 111–113，下层板 y 119，四条腿
    wood, dark, hi = (138, 98, 58), (82, 56, 32), (176, 134, 84)
    rect(d, (204, 111, 244, 113), wood, dark)
    line(d, (205, 111, 243, 111), hi)
    for x in (206, 241):
        rect(d, (x, 114, x + 2, 125), (110, 78, 44), dark)
    rect(d, (206, 119, 243, 120), (118, 84, 48), dark)
    # 下层：两本书 + 一盒磁带
    magazine(d, 209, 118, 13, (60, 110, 160))
    magazine(d, 210, 116, 11, (190, 150, 60), title=False)
    rect(d, (226, 115, 233, 118), (40, 40, 48), (16, 16, 20))
    rect(d, (227, 116, 232, 117), (210, 90, 80))
    # 收音机（双卡录音机）：位置和原来一样，指示灯 (224,109)
    rx0, ry0 = 208, 98
    rect(d, (rx0, ry0, rx0 + 32, ry0 + 13), (40, 40, 46), (16, 16, 20))
    line(d, (rx0 + 1, ry0 + 1, rx0 + 31, ry0 + 1), (88, 88, 98))
    line(d, (rx0 + 6, ry0 - 3, rx0 + 26, ry0 - 3), (140, 140, 150))            # 提手
    line(d, (rx0 + 6, ry0 - 3, rx0 + 6, ry0), (140, 140, 150))
    line(d, (rx0 + 26, ry0 - 3, rx0 + 26, ry0), (140, 140, 150))
    line(d, (rx0 + 29, ry0, rx0 + 38, ry0 - 12), (170, 170, 180))             # 天线
    px(d, rx0 + 38, ry0 - 12, (230, 230, 240))
    for bx in range(rx0 + 10, rx0 + 22, 3):                                   # 顶上按键
        rect(d, (bx, ry0 - 1, bx + 1, ry0), (170, 170, 176))
    for sx in (rx0 + 6, rx0 + 26):                                            # 两个喇叭：网 + 盆
        d.ellipse((sx - 5, ry0 + 2, sx + 5, ry0 + 12), fill=C((110, 110, 120)), outline=C((16, 16, 20)))
        d.ellipse((sx - 3, ry0 + 4, sx + 3, ry0 + 10), fill=C((70, 70, 80)))
        d.ellipse((sx - 1, ry0 + 6, sx + 1, ry0 + 8), fill=C((30, 30, 36)))
        for (dx, dy) in ((-4, 7), (4, 7), (0, 3), (0, 11)):
            px(d, sx + dx, ry0 + dy, (150, 150, 160))
    rect(d, (rx0 + 12, ry0 + 3, rx0 + 20, ry0 + 8), (150, 180, 200), (20, 24, 30))     # 磁带仓
    for cx in (rx0 + 14, rx0 + 18):
        px(d, cx, ry0 + 5, (40, 44, 54))
        px(d, cx, ry0 + 6, (40, 44, 54))
    line(d, (rx0 + 12, ry0 + 10, rx0 + 20, ry0 + 10), (200, 160, 70))         # 调频刻度
    px(d, rx0 + 15, ry0 + 10, (255, 90, 80))
    px(d, rx0 + 16, ry0 + 11, (120, 30, 30))                                  # 指示灯（灭）
    # 啤酒罐：两个立着、一个压扁倒在地上；底下压着纸条
    d.polygon([(241, 127), (255, 126), (256, 131), (242, 132)], fill=C((236, 232, 220)), outline=C((160, 154, 140)))
    for (x0, y0, x1) in ((243, 128, 251), (243, 130, 249)):
        line(d, (x0, y0, x1, y0), (110, 100, 110))
    for i, cx in enumerate((244, 250)):
        cy = 126
        col = (200, 200, 210) if i == 0 else (200, 60, 60)
        rect(d, (cx, cy - 6, cx + 3, cy), col, (60, 60, 70))
        line(d, (cx + 1, cy - 5, cx + 1, cy - 1), tuple(min(255, c + 40) for c in col))
        line(d, (cx, cy - 3, cx + 3, cy - 3), (230, 200, 80) if i == 0 else (240, 240, 240))
        line(d, (cx, cy - 6, cx + 3, cy - 6), (150, 150, 160))
    d.polygon([(245, 133), (252, 131), (253, 133), (246, 135)], fill=C((196, 196, 206)), outline=C((60, 60, 70)))
    line(d, (247, 133, 251, 132), (120, 160, 220))


def floor_details(img):
    d = ImageDraw.Draw(img)
    # 牢里地面：排水口、两道裂纹、一块污渍
    d.ellipse((186, 131, 194, 134), fill=C((80, 80, 82)), outline=C((60, 60, 62)))
    for x in (188, 190, 192):
        px(d, x, 132, (40, 40, 42))
    line(d, [(150, 128), (156, 130), (160, 129), (166, 132)], (92, 90, 88))
    line(d, [(212, 136), (218, 134), (222, 137)], (92, 90, 88))
    A._dither_rect(img, (138, 136, 150, 139), (112, 110, 108), (98, 96, 92), 0.45)


def lighting(img):
    a = np.array(img).astype(np.float32)
    yy, xx = np.mgrid[0:146, 0:W].astype(np.float32)
    dist = np.hypot(xx - 160, (yy - 44) * 1.4)
    li = np.clip(1.08 - dist / 230.0, 0.55, 1.08)
    q = np.floor(li * 8 + A._bayer(W, 146)) / 8.0
    a[:146, :, :3] *= q[..., None]
    a[:146, :, :3] = a[:146, :, :3] * np.array((1.0, 0.97, 0.9), np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def corridor(img):
    A.gradient(img, (0, 146, W, H), [(118, 112, 102), (140, 134, 122), (128, 122, 112)], bands=5)
    d = ImageDraw.Draw(img)
    rect(d, (0, 142, W, 147), (96, 94, 90))
    line(d, (0, 142, W, 142), (150, 146, 138))
    line(d, (0, 147, W, 147), (60, 58, 56))
    for x in range(0, W, 4):                                           # 栏杆脚下的排水槽格栅
        px(d, x, 145, (70, 68, 64))
    for y in (156, 168):
        line(d, (0, y, W, y), (110, 104, 96))
    for i, x in enumerate(range(-20, W + 40, 48)):                     # 分块的竖缝（透视）
        line(d, (x + 10, 148, x + 10 + (x - 160) * 0.22, H), (116, 110, 100))
    for x in range(8, W, 14):                                          # 铁栏投下的影子
        d.polygon([(x, 148), (x + 3, 148), (x + 3 + (x - 160) * 0.22, H), (x + (x - 160) * 0.22, H)], fill=C((104, 98, 90)))
    A._tex_noise(img, (0, 148, W, H), 0.05, 41)
    d = ImageDraw.Draw(img)
    for (x0, y0, n) in ((40, 160, 10), (230, 172, 14), (130, 150, 8)):  # 鞋印擦痕
        line(d, (x0, y0, x0 + n, y0), (122, 116, 106))
    line(d, (0, 176, W, 176), (196, 170, 70))
    line(d, (0, 177, W, 177), (150, 130, 60))


@lru_cache(maxsize=1)
def static():
    img = A._new(W, H, (50, 50, 54))
    room(img)
    wall_items(img)
    bunk(img)
    books(img)
    table_and_radio(img)
    floor_details(img)
    img = lighting(img)
    corridor(img)
    return img


def render(t, bulb=1.0):
    """和原工程 jail_cell(fr) 一样的动画：窗口光束、灯泡（k = int(t·12)，hash01(k,77) < 0.04 的帧暗下去）、收音机指示灯。"""
    img = static().copy()
    A._blend_poly(img, [(206, 56), (236, 56), (206 - 30, 124), (176 - 34, 124)], (255, 244, 200), 30)
    d = ImageDraw.Draw(img)
    fl = bulb
    k = int(t * 12 + 1e-9)
    if A.hash01(k % BULB_N, 77) < 0.04:
        fl *= 0.55
    line(d, (160, 8, 160, 34), (40, 38, 36))
    rect(d, (158, 34, 162, 37), (90, 86, 80))
    if fl > 0.05:
        A._glow(img, 160, 41, 30, 26, (255, 226, 150), int(70 * fl), rings=4)
        d = ImageDraw.Draw(img)
    d.ellipse((157, 37, 163, 45), fill=C(A.mix((120, 110, 90), (255, 250, 220), fl)))
    px(d, 159, 39, (255, 255, 255))
    if int(t * 2 + 1e-9) % 2:
        px(d, 224, 109, (80, 255, 120))
    return img


def bars(bq):
    return A._bars_layer(bq, 6, 314, CX, 0, 146).crop((0, 0, W, 147))


def export(ex, BJ):
    layers = [dict(type='static', image=ex.img('static', render(0.0)))]
    layers.append(ex.bake('bulb', BULB_BOX, BULB_N, 12.0, render))
    layers.append(ex.bake('led', LED_BOX, 2, 2.0, render))
    imgs = [ex.img('bars%d' % i, bars(bq)) for i, bq in enumerate((0, 10, 20, 30, 40, 50))]
    fg = [dict(type='pick', images=imgs, key='bend', x=0, y=0, k=0)]
    anchors = dict(cell_ground=130, cell_walk=[122, 138], cell_x=[96, 236], corridor_walk=[150, 176],
                   bunk=[148, 97], bunk_feet=[148, 124], bars=[6, 314, 0, 145], bars_cx=CX,
                   window=[206, 38, 236, 56], radio=[208, 98], bulb=[160, 41])
    st = ex.stage(320, 166, (122, 138), layers, fg, anchors)
    if ex.check_on:
        for k_ in (0, 10, 13, 30, 47):
            t = k_ / 12.0
            ex.checked('牢房 t=%.3f(k=%d) 导出 vs 直接绘制' % (t, k_), BJ.ndiff_rgba(BJ.ref_render(st, ex.images, 0, t), render(t)))
        a = np.array(render(0))
        ex.checked('牢房底图不透明', int((a[:, :, 3] != 255).sum()))
    return st


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '_preview')
    os.makedirs(out, exist_ok=True)
    im = render(0).copy()
    im.alpha_composite(bars(0).crop((0, 0, W, 147)), (0, 0))
    im.resize((W * 4, H * 4), Image.Resampling.NEAREST).save(os.path.join(out, 'jail_cell_solo.png'))
    old = os.path.join(out, 'jail_cell_solo.png')
    print(old)
