# -*- coding: utf-8 -*-
r"""cockpit —— 客机驾驶舱（第1章 1-7 / 1-8，侧视、机头朝右）。scenes-early 2026-10-10 按人的比例重画。

用户 2026-10-09 晚：“驾驶舱的场景也需要你重新构建，这个飞机的控制台、椅子的大小完全不对。”原片 s06 的
_cockpit_bg() 只有一张比人还高的椅子、一个悬在半空的操纵杆和一排孤零零的表。重画（320 单屏，地板 y 172）：
  左    驾驶舱门（开着，看得见客舱的暖光）+ 隔板；舱壁上的随机工程师面板（表、开关、断路器）、灭火瓶、
        折叠的观察员座椅、挂着的外套
  中    两张按人比例的驾驶座（近侧机长座空着，远侧副驾驶歪倒在座位上，没有血）：头枕顶 y 128 / 122，
        羊皮椅套、扶手、座椅底座和滑轨；两根操纵杆（羊角盘）在座椅前面，近侧那根是 pick 层（key 'yoke'：
        0 = 原位，1 = 乔瑟夫拉到底）；两座之间的中央操纵台（四根油门杆、无线电面板）
  右    遮光板 + 自动驾驶面板、主仪表板（姿态仪 / 航向 / 空速 / 高度 / 发动机表 / 警告灯）、方向舵踏板；
        斜的挡风玻璃 + 侧窗（外面是往下冲的海和天：strip 24 帧 @12 fps）
  上    往机头压低的天花板 + 头顶开关面板
  警报  key 'alarm'：主警告灯 2 Hz 闪、天花板红色警灯光晕（strip）
锚点：floor 172、walk [164,176]、door [6,34]、seat_near / seat_far、yoke_near（乔瑟夫抓的位置）、
      pilot_floor（倒在地上的机长）、cap、crew_at（三人站在门口的位置）、panel、windshield。
单独运行：python -B tools\bg_new\cockpit.py → tools\bg_new\_preview\cockpit_solo.png
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
FLOOR = 172
WALK = (164, 176)
N_WS, FPS_WS = 24, 12.0                  # 窗外 2 s 一圈
WS_BOX = (172, 22, 320, 104)             # 窗外动画裁出来的那一块（侧窗 + 挡风玻璃）
WS_POLY = [(236, 34), (320, 25), (320, 98), (246, 98)]          # 挡风玻璃（透明区）
SIDE_POLY = [(178, 40), (228, 33), (234, 84), (184, 86)]        # 侧窗
YOKE_BOX = (226, 124, 252, 173)
NEAR_SEAT = 186                          # 近侧机长座椅背中心 x
FAR_DX, FAR_DY = 18, -6                  # 远侧座椅相对近侧的偏移（错开一点才看得出是两张椅子）
C = A._c4

PANEL = (66, 76, 80)                     # 驾驶舱“波音灰”
PANEL_D = (44, 52, 56)
PANEL_L = (96, 108, 112)
INK = (16, 18, 22)


def _poly_mask(poly, size=(W, H)):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    return m


def _gauge(d, cx, cy, r, kind='w', ang=None, seed=0):
    """圆表：黑表盘 + 白刻度 + 指针；kind 'adi' 姿态仪（上蓝下棕）。"""
    d.ellipse((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), fill=C((30, 34, 38)))
    if kind == 'adi':
        d.pieslice((cx - r, cy - r, cx + r, cy + r), 180 - 14, 360 - 14, fill=C((70, 130, 210)))
        d.pieslice((cx - r, cy - r, cx + r, cy + r), -14, 180 - 14, fill=C((150, 96, 52)))
        d.line((cx - r, cy + 1, cx + r, cy - 2), fill=C((240, 240, 240)))
        d.line((cx - 2, cy, cx + 2, cy), fill=C((255, 210, 60)))
        return
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C((14, 16, 20)))
    for k in range(8):
        a = k / 8 * math.tau
        d.point((round(cx + math.cos(a) * (r - 1)), round(cy + math.sin(a) * (r - 1))), fill=C((200, 204, 210)))
    a = ang if ang is not None else hrange(0, math.tau, seed, 1)
    col = (255, 255, 255) if kind == 'w' else (255, 210, 70)
    d.line((cx, cy, round(cx + math.cos(a) * (r - 1)), round(cy + math.sin(a) * (r - 1))), fill=C(col))


def _switches(d, x0, y0, x1, y1, seed, pitch=3):
    """一排排小开关 / 指示灯（头顶面板、工程师面板）。"""
    for y in range(y0, y1, pitch + 1):
        for x in range(x0, x1, pitch):
            r = hash01(seed, x, y)
            if r < 0.45:
                d.point((x, y), fill=C((200, 204, 210)))
                d.point((x, y + 1), fill=C((90, 96, 100)))
            elif r < 0.55:
                d.point((x, y), fill=C((255, 190, 60)))
            elif r < 0.6:
                d.point((x, y), fill=C((120, 230, 140)))
            elif r < 0.7:
                d.rectangle((x, y, x + 1, y + 1), fill=C((30, 32, 36)))


def _seat(d, cx, floor, dim=1.0, sheep=True):
    """驾驶座（侧视、朝右）：头枕 + 高靠背（羊皮椅套）+ 坐垫 + 扶手 + 底座 + 滑轨。cx = 椅背中心。"""
    def k(c):
        return tuple(int(v * dim) for v in c)
    leather, leather_d, leather_h = (120, 92, 66), (84, 62, 44), (156, 124, 92)
    fleece, fleece_d = (222, 212, 190), (184, 172, 150)
    top = floor - 44
    # 底座 + 滑轨
    d.rectangle((cx - 2, floor - 14, cx + 16, floor - 2), fill=C(k((54, 56, 62))))
    d.line((cx - 2, floor - 14, cx + 16, floor - 14), fill=C(k((96, 100, 108))))
    d.rectangle((cx - 8, floor - 2, cx + 22, floor), fill=C(k((80, 84, 92))))
    d.line((cx - 8, floor - 2, cx + 22, floor - 2), fill=C(k((130, 134, 142))))
    # 坐垫
    d.rounded_rectangle((cx - 2, floor - 22, cx + 24, floor - 13), radius=3, fill=C(k(leather)), outline=C(k(INK)))
    d.line((cx, floor - 21, cx + 22, floor - 21), fill=C(k(leather_h)))
    if sheep:
        d.rounded_rectangle((cx - 1, floor - 23, cx + 20, floor - 19), radius=2, fill=C(k(fleece)))
    # 靠背（往后仰一点）+ 头枕
    back = [(cx - 7, top + 7), (cx + 5, top + 6), (cx + 8, floor - 18), (cx - 4, floor - 16)]
    d.polygon(back, fill=C(k(leather)), outline=C(k(INK)))
    d.line((cx - 5, top + 9, cx - 3, floor - 18), fill=C(k(leather_h)))
    if sheep:
        d.polygon([(cx - 4, top + 9), (cx + 5, top + 8), (cx + 7, floor - 20), (cx - 2, floor - 19)], fill=C(k(fleece)))
        for yy in range(top + 11, floor - 20, 3):
            d.point((cx + int(hrange(-2, 4, cx, yy, 1)), yy), fill=C(k(fleece_d)))
    d.rounded_rectangle((cx - 8, top - 1, cx + 5, top + 7), radius=3, fill=C(k(leather_d)), outline=C(k(INK)))
    d.line((cx - 6, top, cx + 3, top), fill=C(k(leather_h)))
    # 扶手（近侧这一边，盖在坐垫上）
    d.rounded_rectangle((cx + 1, floor - 27, cx + 21, floor - 24), radius=1, fill=C(k((70, 72, 80))), outline=C(k(INK)))
    d.line((cx + 2, floor - 27, cx + 20, floor - 27), fill=C(k((130, 134, 144))))
    d.line((cx + 4, floor - 24, cx + 4, floor - 21), fill=C(k((50, 52, 58))))


def _yoke(d, base_x, floor, pull=0.0, dim=1.0):
    """操纵杆：从地板升起的杆子 + 羊角盘（侧视是一根竖着的握把）。pull 0..1 往驾驶员这边拉。"""
    def k(c):
        return tuple(int(v * dim) for v in c)
    top_x = base_x - 4 - round(6 * pull)
    top_y = floor - 36 + round(2 * pull)
    d.line((base_x, floor - 1, top_x + 1, top_y + 4), fill=C(k((40, 42, 48))), width=3)
    d.line((base_x - 1, floor - 2, top_x, top_y + 4), fill=C(k((96, 100, 110))))
    d.rectangle((base_x - 4, floor - 4, base_x + 4, floor), fill=C(k((50, 52, 58))))         # 底座套筒
    d.rectangle((top_x - 3, top_y - 1, top_x + 3, top_y + 5), fill=C(k((30, 32, 36))))        # 盘心
    d.rectangle((top_x - 2, top_y - 8, top_x + 1, top_y + 12), fill=C(k((26, 26, 30))))       # 羊角盘握把（侧面）
    d.line((top_x - 1, top_y - 7, top_x - 1, top_y + 11), fill=C(k((92, 94, 102))))
    d.point((top_x, top_y - 8), fill=C(k((200, 60, 60))))                                     # 握把上的按钮
    d.rectangle((top_x - 1, top_y + 1, top_x + 1, top_y + 2), fill=C(k((230, 230, 236))))     # 盘心标牌
    return top_x, top_y


def _pilot_slumped(d, sx, floor):
    """远侧副驾驶：歪倒在座位上（头垂到胸前、手臂垂下），深蓝制服 + 金色袖线；没有血。sx = 远侧椅背中心。"""
    navy, navy_d, gold = (40, 52, 104), (26, 34, 70), (230, 190, 70)
    skin, skin_d, hair = (240, 196, 160), (206, 150, 118), (92, 60, 40)
    seat_y = floor - 22
    # 腿：往右伸到方向舵踏板
    d.polygon([(sx + 8, seat_y - 2), (sx + 22, seat_y - 3), (sx + 34, seat_y + 8), (sx + 30, seat_y + 11),
               (sx + 18, seat_y + 4), (sx + 8, seat_y + 4)], fill=C(navy_d), outline=C(INK))
    d.rectangle((sx + 31, seat_y + 9, sx + 37, seat_y + 12), fill=C((20, 20, 24)))          # 鞋
    # 上身：往后靠、往左歪
    d.polygon([(sx + 2, seat_y - 22), (sx + 12, seat_y - 24), (sx + 15, seat_y - 2), (sx + 4, seat_y)],
              fill=C(navy), outline=C(INK))
    d.line((sx + 8, seat_y - 22, sx + 9, seat_y - 4), fill=C((236, 236, 240)))               # 衬衫领口
    d.point((sx + 9, seat_y - 18), fill=C((180, 40, 40)))                                     # 领带
    d.point((sx + 9, seat_y - 17), fill=C((180, 40, 40)))
    # 手臂垂在扶手外
    d.line((sx + 12, seat_y - 20, sx + 16, seat_y - 8), fill=C(navy_d), width=3)
    d.line((sx + 15, seat_y - 9, sx + 17, seat_y - 6), fill=C(gold))
    d.rectangle((sx + 16, seat_y - 6, sx + 18, seat_y - 3), fill=C(skin))
    # 头：垂到右肩前面，眼睛闭着；戴着耳机（头箍 + 耳罩 + 话筒杆）
    hx, hy = sx + 13, seat_y - 30
    d.ellipse((hx - 6, hy - 6, hx + 6, hy + 6), fill=C(skin), outline=C(INK))
    d.chord((hx - 6, hy - 7, hx + 6, hy + 3), 180, 360, fill=C(hair))
    d.line((hx - 6, hy - 2, hx - 3, hy - 4), fill=C(hair))
    d.line((hx - 3, hy - 5, hx + 2, hy - 6), fill=C((128, 90, 60)))                           # 头发高光
    d.arc((hx - 7, hy - 8, hx + 5, hy + 4), 200, 330, fill=C((40, 42, 48)))                   # 耳机头箍
    d.rectangle((hx - 4, hy - 1, hx - 1, hy + 3), fill=C((40, 42, 48)))                       # 耳罩
    d.line((hx - 1, hy + 3, hx + 4, hy + 6), fill=C((60, 62, 70)))                            # 话筒杆
    d.point((hx + 4, hy + 6), fill=C((20, 20, 24)))
    d.line((hx + 1, hy + 1, hx + 4, hy + 1), fill=C(INK))                                     # 闭着的眼睛
    d.line((hx + 1, hy - 1, hx + 4, hy - 2), fill=C(hair))                                    # 眉毛
    d.point((hx + 6, hy + 2), fill=C(skin_d))                                                 # 鼻子
    d.line((hx + 2, hy + 4, hx + 3, hy + 4), fill=C(skin_d))


@lru_cache(maxsize=1)
def base():
    """不会动的部分（窗户是黑的，窗外另烘 strip 叠上去）。"""
    im = A._new(W, H, PANEL)
    d = ImageDraw.Draw(im)
    # ---------- 天花板（往机头压低）+ 头顶开关面板
    d.polygon([(0, 0), (W, 0), (W, 25), (236, 34), (178, 40), (40, 30), (0, 28)], fill=C((58, 66, 70)))
    for i in range(5):
        y = 4 + i * 5
        d.line((0, y, 172, y + 4), fill=C((50, 58, 62)))
    d.polygon([(150, 4), (300, 4), (300, 16), (236, 26), (176, 30), (150, 26)], fill=C((40, 46, 50)), outline=C(INK))
    _switches(d, 154, 7, 296, 15, 3)
    _switches(d, 158, 17, 232, 25, 4)
    for x in range(160, 290, 22):                                    # 面板分格
        d.line((x, 5, x - 1, 26), fill=C((30, 34, 38)))
    # ---------- 左边：隔板 + 开着的门（门外是客舱的暖光）
    d.rectangle((0, 26, 40, FLOOR), fill=C((88, 98, 100)))
    d.rectangle((6, 54, 34, FLOOR), fill=C((214, 196, 158)))         # 门洞里：客舱
    gradient(im, (7, 55, 34, FLOOR), [(226, 214, 182), (204, 186, 150), (150, 128, 100)], bands=5)
    d = ImageDraw.Draw(im)
    for x in (12, 22):                                               # 门外客舱里的座椅背影
        d.rounded_rectangle((x, 132, x + 9, 158), radius=2, fill=C((50, 72, 136)), outline=C((26, 36, 70)))
        d.rectangle((x + 1, 133, x + 7, 136), fill=C((232, 232, 236)))
    d.rectangle((6, 54, 34, 56), fill=C((60, 66, 70)))
    d.rectangle((4, 52, 6, FLOOR), fill=C((54, 60, 64)))
    d.rectangle((34, 52, 37, FLOOR), fill=C((54, 60, 64)))
    d.polygon([(37, 56), (44, 60), (44, FLOOR - 4), (37, FLOOR)], fill=C((120, 128, 130)), outline=C(INK))   # 开着的门板
    d.point((42, 112), fill=C((200, 200, 206)))
    # ---------- 左侧舱壁：随机工程师面板、断路器、灭火瓶、折叠座椅、挂着的外套
    d.rectangle((44, 30, 176, FLOOR), fill=C(PANEL))
    gradient(im, (44, 30, 176, FLOOR), [mix(PANEL, (90, 100, 104), 0.4), PANEL, PANEL_D], bands=5)
    d = ImageDraw.Draw(im)
    d.rectangle((52, 40, 150, 70), fill=C((36, 40, 44)), outline=C(INK))                 # 断路器面板
    for y in range(43, 68, 4):
        for x in range(55, 148, 3):
            if hash01(x, y, 21) < 0.9:
                d.point((x, y), fill=C((150, 154, 160)))
                d.point((x, y + 1), fill=C((70, 74, 80)))
    d.rectangle((86, 78, 170, 132), fill=C((48, 56, 60)), outline=C(INK))                # 工程师面板
    for i, (gx, gy) in enumerate([(94, 88), (106, 88), (118, 88), (130, 88), (94, 102), (106, 102), (118, 102),
                                   (130, 102), (146, 92), (158, 92)]):
        _gauge(d, gx, gy, 4, 'w' if i % 3 else 'y', seed=i)
    _switches(d, 90, 112, 168, 130, 5, 3)
    d.rectangle((140, 104, 166, 110), fill=C((24, 28, 30)))
    for x in range(142, 165, 4):
        d.point((x, 107), fill=C((255, 180, 60) if hash01(x, 22) < 0.5 else (90, 230, 120)))
    d.rectangle((58, 104, 74, 112), fill=C((90, 98, 102)), outline=C(INK))               # 折叠观察员座椅
    d.rectangle((60, 112, 72, 146), fill=C((70, 78, 82)), outline=C(INK))
    d.line((61, 113, 61, 145), fill=C((110, 118, 122)))
    d.rectangle((50, 120, 54, 124), fill=C((150, 150, 156)))                             # 衣钩 + 外套
    d.polygon([(48, 124), (56, 124), (58, 152), (46, 152)], fill=C((36, 40, 72)), outline=C(INK))
    d.line((52, 125, 52, 150), fill=C((24, 26, 50)))
    d.line((47, 140, 57, 140), fill=C((220, 180, 70)))
    d.rounded_rectangle((152, 140, 160, 166), radius=3, fill=C((200, 40, 40)), outline=C(INK))   # 灭火瓶
    d.rectangle((154, 136, 158, 140), fill=C((40, 40, 44)))
    d.line((153, 142, 153, 164), fill=C((240, 110, 110)))
    d.rectangle((150, 150, 162, 152), fill=C((90, 96, 100)))
    d.rectangle((96, 140, 130, 160), fill=C((54, 62, 66)), outline=C(INK))               # 文件包 / 航图箱
    d.line((98, 142, 128, 142), fill=C((90, 98, 102)))
    d.rectangle((100, 145, 126, 150), fill=C((214, 206, 180)))
    # ---------- 侧窗 + 挡风玻璃的窗框（窗里先黑着）
    d.polygon(SIDE_POLY, fill=C((10, 12, 16)))
    d.line([SIDE_POLY[0], SIDE_POLY[1], SIDE_POLY[2], SIDE_POLY[3], SIDE_POLY[0]], fill=C((24, 28, 32)), width=3)
    d.polygon(WS_POLY, fill=C((10, 12, 16)))
    d.line([WS_POLY[0], WS_POLY[1], (320, 25)], fill=C((24, 28, 32)), width=4)
    d.line([(236, 34), (246, 98)], fill=C((24, 28, 32)), width=5)                       # 挡风玻璃和侧窗之间的立柱
    d.line([(286, 30), (290, 98)], fill=C((24, 28, 32)), width=3)                        # 两块挡风玻璃之间
    # ---------- 遮光板 + 自动驾驶面板
    d.polygon([(240, 96), (320, 94), (320, 106), (250, 108)], fill=C((22, 24, 28)), outline=C(INK))
    d.line((242, 96, 320, 94), fill=C((70, 76, 82)))
    d.rectangle((262, 99, 316, 104), fill=C((44, 48, 54)))
    for x in range(265, 314, 6):
        d.point((x, 101), fill=C((200, 204, 210)))
        d.point((x + 2, 102), fill=C((255, 170, 60) if hash01(x, 31) < 0.4 else (150, 154, 160)))
    d.rectangle((250, 100, 258, 104), fill=C((90, 20, 20)))          # 主警告灯（不亮）
    # ---------- 主仪表板
    d.polygon([(250, 108), (320, 106), (320, 154), (256, 156)], fill=C(PANEL_D), outline=C(INK))
    for i, (gx, gy, kind) in enumerate([(264, 118, 'adi'), (264, 136, 'w'), (278, 116, 'w'), (278, 130, 'y'),
                                         (278, 144, 'w'), (294, 118, 'w'), (306, 118, 'w'), (294, 132, 'y'),
                                         (306, 132, 'w'), (300, 146, 'w')]):
        _gauge(d, gx, gy, 5 if kind == 'adi' else 4, kind, seed=i + 40)
    d.rectangle((286, 108, 316, 111), fill=C((26, 28, 32)))
    for x in range(288, 315, 3):
        d.point((x, 109), fill=C((255, 190, 60) if hash01(x, 33) < 0.3 else (60, 66, 70)))
    # 下半：膝盖挡板 + 方向舵踏板
    d.polygon([(256, 156), (320, 154), (320, FLOOR), (262, FLOOR)], fill=C((34, 40, 44)))
    d.line((256, 156, 320, 154), fill=C((80, 88, 92)))
    for px_ in (270, 282):
        d.line((px_, 158, px_ - 4, 168), fill=C((60, 64, 70)), width=2)
        d.rectangle((px_ - 8, 166, px_ - 2, 170), fill=C((26, 28, 32)))
    # ---------- 中央操纵台（两座之间）：斜面 + 四根油门杆 + 无线电面板
    d.polygon([(226, 146), (252, 140), (258, FLOOR), (230, FLOOR)], fill=C((40, 46, 50)), outline=C(INK))
    d.line((227, 146, 252, 140), fill=C((96, 104, 108)))
    for k in range(4):
        tx = 234 + k * 4
        d.line((tx, 144 - k, tx - 3, 132 - k), fill=C((150, 154, 162)), width=1)
        d.rectangle((tx - 5, 130 - k, tx - 2, 132 - k), fill=C((230, 230, 236)))
    _switches(d, 234, 152, 252, 168, 6, 3)
    # ---------- 地板
    d.rectangle((0, FLOOR, W, H), fill=C((40, 44, 50)))
    d.line((0, FLOOR, W, FLOOR), fill=C((90, 96, 104)))
    for x in range(0, W, 12):
        d.line((x, FLOOR + 3, x + 6, FLOOR + 3), fill=C((52, 56, 62)))
    gradient(im, (0, FLOOR + 1, W, H), [(46, 50, 56), (30, 32, 38)], bands=3)
    d = ImageDraw.Draw(im)
    for x in range(4, W, 16):
        d.line((x, FLOOR + 6, x + 8, FLOOR + 6), fill=C((56, 60, 68)))
    # ---------- 远侧（副驾驶）座椅 + 歪倒的副驾驶 + 远侧操纵杆
    fx = NEAR_SEAT + FAR_DX
    _yoke(d, 252, FLOOR + FAR_DY, 0.0, dim=0.7)
    _seat(d, fx, FLOOR + FAR_DY, dim=0.78)
    _pilot_slumped(d, fx, FLOOR + FAR_DY)
    # ---------- 近侧（机长）座椅：空着
    _seat(d, NEAR_SEAT, FLOOR, dim=1.0)
    # 驾驶舱里的光：窗外日光照亮遮光板边、座椅头枕；角落压暗
    A._tex_noise(im, (0, 0, W, FLOOR), 0.05, 61)
    a = np.array(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.hypot(xx - 290, (yy - 60) * 1.2)
    li = np.clip(1.12 - dist / 360.0, 0.72, 1.1)
    q = np.floor(li * 8 + A._bayer(W, H)) / 8.0
    a[..., :3] *= q[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    return im


def _view(t):
    """窗外：飞机往下冲、往右歪（海占了一大半），云和浪往上、往外冲。返回 W×H（只有窗户里有东西）。"""
    vw, vh = 200, 140
    v = Image.new('RGBA', (vw, vh), (0, 0, 0, 255))
    d = ImageDraw.Draw(v)
    hy = 34
    bank = -13.0 + 2.0 * math.sin(t * math.tau / 2.0)
    gradient(v, (0, 0, vw, hy), [(122, 176, 240), (206, 230, 252)], bands=4)
    gradient(v, (0, hy, vw, vh), [(96, 164, 226), (48, 112, 196), (30, 76, 160)], bands=6)
    d.line((0, hy, vw, hy), fill=(236, 246, 255, 255))
    d.polygon([(130, hy), (140, hy - 4), (150, hy - 3), (160, hy)], fill=(90, 116, 140, 255))   # 远处的岛（香港）
    for i in range(40):                                   # 浪：往下（往我们这边）冲
        z = (hash01(i, 5) + t * 0.5 * 2) % 1.0
        yy = hy + 2 + (vh - hy - 2) * z * z
        xx = (hash01(i, 6) - 0.5) * vw * (0.6 + 1.4 * z) + vw / 2
        L = 2 + 16 * z
        col = (255, 255, 255) if hash01(i, 7) < 0.5 else (170, 214, 255)
        d.line((round(xx - L / 2), round(yy), round(xx + L / 2), round(yy)), fill=col + (255,))
    for i in range(4):                                    # 云絮：从下往上掠过
        u = (hash01(i, 9) + t * 0.5 * 3) % 1.0
        cx = vw * hash01(i, 10)
        cy = vh * (1.2 - 1.6 * u)
        d.ellipse((cx - 16, cy - 5, cx + 16, cy + 5), fill=(236, 244, 255, 255))
        d.ellipse((cx - 8, cy - 7, cx + 10, cy + 2), fill=(250, 252, 255, 255))
    v = v.rotate(bank, resample=Image.NEAREST)
    full = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    full.paste(v, (WS_BOX[0] + 60 - vw // 2 + 40, 64 - vh // 2))
    m = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(m)
    md.polygon(WS_POLY, fill=255)
    md.polygon(SIDE_POLY, fill=255)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.paste(full, (0, 0), m)
    # 玻璃反光（两道斜线）+ 窗框再压一遍
    od = ImageDraw.Draw(out)
    for (x0, y0, x1, y1) in ((250, 40, 262, 92), (296, 30, 306, 90), (186, 44, 196, 82)):
        od.line((x0, y0, x1, y1), fill=(255, 255, 255, 60))
    return out


def ws_frame(t):
    im = base().copy()
    im.alpha_composite(_view(t))
    d = ImageDraw.Draw(im)
    d.line([SIDE_POLY[0], SIDE_POLY[1], SIDE_POLY[2], SIDE_POLY[3], SIDE_POLY[0]], fill=C((24, 28, 32)), width=3)
    d.line([WS_POLY[0], WS_POLY[1]], fill=C((24, 28, 32)), width=4)
    d.line([(236, 34), (246, 98)], fill=C((24, 28, 32)), width=5)
    d.line([(286, 30), (290, 98)], fill=C((24, 28, 32)), width=3)
    return im


def alarm_frame(t):
    """警报：主警告灯 2 Hz 闪、头顶红色警灯光晕 + 仪表板上几颗红灯。"""
    im = base().copy()
    d = ImageDraw.Draw(im)
    on = int(t * 4) % 2 == 0
    if on:
        A._glow(im, 254, 102, 10, 6, (255, 60, 40), 70, rings=3)
        d = ImageDraw.Draw(im)
        d.rectangle((250, 100, 258, 104), fill=C((255, 70, 50)))
        d.line((252, 101, 256, 101), fill=C((255, 220, 200)))
    for i in range(5):
        lit = int(t * 6 + i * 0.5) % 2 == 0
        d.point((289 + i * 6, 109), fill=C((255, 50, 40) if lit else (90, 20, 20)))
    pulse = 0.5 + 0.5 * math.cos(t * math.tau * 2.0)
    A._glow(im, 120, 8, 26 + 10 * pulse, 10, (255, 40, 40), int(40 + 50 * pulse), rings=4)
    d = ImageDraw.Draw(im)
    d.rectangle((116, 4, 124, 8), fill=C((255, 70, 60) if pulse > 0.5 else (170, 30, 40)))
    return im


def yoke_img(pull):
    """操纵杆那一块（连同底下的背景，不透明）：pick 换图时整块盖住底图里原位的操纵杆。"""
    im = base().copy()
    d = ImageDraw.Draw(im)
    _yoke(d, 244, FLOOR, pull)
    return im.crop(YOKE_BOX)


def export(ex, BJ):
    b = base().copy()
    d = ImageDraw.Draw(b)
    _yoke(d, 244, FLOOR, 0.0)
    layers = [dict(type='static', image=ex.img('static', b))]
    layers.append(ex.bake('windshield', WS_BOX, N_WS, FPS_WS, ws_frame))
    layers.append(ex.bake('alarm_light', (238, 92, 320, 112), N_WS, FPS_WS, alarm_frame, key='alarm'))
    layers.append(ex.bake('alarm_beacon', (84, 0, 158, 20), N_WS, FPS_WS, alarm_frame, key='alarm'))
    yk = [ex.img('yoke%d' % i, yoke_img(p)) for i, p in enumerate((0.0, 1.0))]
    layers.append(dict(type='pick', images=yk, key='yoke', x=YOKE_BOX[0], y=YOKE_BOX[1], k=0))
    anchors = dict(floor=FLOOR, walk=list(WALK), door=[6, 34], seat_near=[NEAR_SEAT, FLOOR], seat_far=[NEAR_SEAT + FAR_DX, FLOOR + FAR_DY],
                   yoke_near=[238, 140], joseph_at=[228, 172], pilot_floor=[132, 174], cap=[166, 175],
                   crew_at=[[52, 172], [72, 168], [92, 175]], panel=[250, 106, 320, 156], windshield=[list(p) for p in WS_POLY],
                   walk_x=[44, 236])
    st = ex.stage(W, 170, WALK, layers, anchors=anchors)
    if ex.check_on:
        # 导出层（static + 窗外 strip + 操纵杆 pick 0）重建 = 直接画（ws_frame + 操纵杆）
        for t in (0.0, 0.5, 1.25):
            ref = ws_frame(t)
            dd = ImageDraw.Draw(ref)
            _yoke(dd, 244, FLOOR, 0.0)
            got = BJ.ref_render(st, ex.images, 0, t, dict(yoke=0))
            ex.checked('驾驶舱 t=%.2f 导出与直接绘制一致（窗外 + 操纵杆）' % t,
                       BJ.ndiff(got, ref, mask=BJ.rect_mask([WS_BOX, YOKE_BOX], keep=True)))
        a = np.array(b)
        ex.checked('驾驶舱整幅不透明', int((a[..., 3] != 255).sum()))
        ex.checked('窗外 2 s 严格闭合', BJ.ndiff_rgba(ws_frame(0).crop(WS_BOX), ws_frame(2.0).crop(WS_BOX)))
    return st


if __name__ == '__main__':
    im = ws_frame(0.3)
    im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 0)))
    os.makedirs(os.path.join(HERE, '_preview'), exist_ok=True)
    im.convert('RGB').resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(HERE, '_preview', 'cockpit_solo.png'))
    print('ok')
