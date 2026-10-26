# -*- coding: utf-8 -*-
r"""game_room —— 第11章「DIO 的馆」：泰伦斯的游戏室（地图 game_ch11），第 24 战「阿图姆神」（F-MEGA 赛车 / 棒球）。
2026-10-19 第三轮背景重画（interiors 组）新画（改前是 later_stages 的占位：原工程 _game_static）。共用零件在 interior_parts.py。

320 单屏，ground 156，可走带 y 150–172（深色木地板 + 一大块旧波斯地毯，压低了对比）；侧视平视，后墙 + 左边一小截侧墙。
馆里的一间老房间被改成了游戏室：哥特式的暗紫大马士革墙纸、桃花心木护墙板、烛台——中间却是 1980 年代的大电视和街机。
竖向：天花板（格子梁）0–8，檐口 9–12，墙纸 13–100，腰线 101–103，护墙板 104–138，踢脚板 139–144，地面 145–179。
从左到右：
  x 0–14     左边一截侧墙（透视），墙上一扇往走廊去的门（anchors.door = 门前站点 [12,160]）
  x 16–46    街机柜 1（anchors.arcade [30,150]）：蓝色机身、顶上灯箱写着 F-MEGA、屏幕在放赛车的演示画面（strip）、摇杆和按钮
  x 50–108   玩具架：三层木搁板——铁皮机器人（眼睛一闪一闪 strip）、小汽车、陀螺、魔方、一架飞机模型、一排游戏卡带、玩具兵
  x 112–206  大 CRT 电视（anchors.tv [160,120]；屏幕 anchors.screen [122,58,196,110]）：胡桃木外壳、银边、兔耳天线、
             屏幕下面一条喇叭网 + 旋钮；平时屏幕是暗的（墨绿灰 + 一道弧形反光）；下面一个矮电视柜：游戏机（红色电源灯一闪一闪）、
             一排卡带、两根手柄线一直拖到两把游戏椅那里
  x 76–102 / 226–252  两把矮的游戏椅（紫丝绒坐垫 + 矮靠背，贴着可走带后沿；anchors.player [89,156] / opponent [239,156] 站在椅子前）
  x 212–242  街机柜 2：红色机身、灯箱写着 UFO、屏幕里星星往下飞（strip）
  x 246–258  墙上的三头烛台（火苗 strip）
  x 262–312  玻璃柜（anchors.dolls_box [262,70,312,124]、dolls [282,96]）：深色木框、玻璃上斜的反光、暗红丝绒的背板；
             中间那层搁板（y 96）上三个空着的人偶座（小铜托 + 名牌：anchors.doll_slots），上层、下层空着——人偶是剧情摆的
  x 282–320  key hole：墙被打穿（anchors.wall_hole [300,120]）：玻璃柜后面的墙上一个大洞（碎砖、撕开的墙纸、
             另一边是空房间），玻璃柜的玻璃也碎了（裂纹、缺块），地上一堆碎砖和玻璃渣
地毯中间是对着电视打游戏的地方；手柄线贴着地毯走（不高过 1 px）。

图层（从后往前）：
  near      pano  k 1           整间屋子（打好光：烛台、两台街机屏幕的彩光、偏紫的暗环境光；电视是关着的）
  hole      pano  k 1  key hole  墙被打穿的那一块（重画了墙 + 玻璃柜 + 碎砖，和底图同一套打光）
  crt_light pano  k 1  key crt   电视亮着：屏幕照亮周围（半透明的冷蓝光，分 5 档抖开）
  crt       strip 8 帧 @8 fps key crt   屏幕：雪花 + 扫描线 + 一道往下滚的亮带 + 屏幕四周的辉光
  arcade1   strip 8 帧 @4 fps   街机 1 的赛车演示（路往近处滚、两辆车左右换道）+ 灯箱一明一暗
  arcade2   strip 8 帧 @4 fps   街机 2 的星星往下飞 + 小飞碟左右晃
  candle    strip 8 帧 @4 fps   三头烛台的火苗
  toys      strip 8 帧 @4 fps   玩具机器人的眼睛一闪一闪 + 游戏机的电源灯
锚点（素材总表定稿的名字一个不少，值照总表）：screen [122,58,196,110]、tv [160,120]、player [89,156]、opponent [239,156]、
  dolls [282,96]、dolls_box [262,70,312,124]、arcade [30,150]、wall_hole [300,120]、door [12,160]；
  另外多导出：doll_slots [[270,96],[282,96],[294,96]]（三个人偶座：人偶道具 pivot 底中，脚放在这里正好站在搁板上）、
  console [160,140]（游戏机）、candles [252,76]、arcade2 [227,150]、walk_x [8,312]。
key：crt（电视亮）、hole（墙被打穿）。
单独运行：python -B tools/bg_new/game_room.py → tools/bg_new/_preview/ch11/after/game_room_solo.png
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import hash01, hrange, mix, paste  # noqa: E402


def _parts():
    key = 'bg_new_interior_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'interior_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
fno = P.frame_no

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 320
GROUND = 156
WALK = (150, 172)
CEIL = 8
CORN = (9, 12)
RAIL = (101, 103)
WAINS = (104, 138)
SKIRT = (139, 144)
FLOOR = 145
SIDE = 14                      # 左边侧墙到这里（和后墙的交线）
SCREEN = (122, 58, 196, 110)
TV = (112, 48, 206, 122)       # 电视外壳
STAND = (118, 122, 200, 144)   # 电视柜
AR1 = (16, 88, 46, 146)        # 街机 1
AR2 = (212, 92, 242, 146)      # 街机 2
SHELF_X = (50, 108)
CHAIRS = [89, 239]
BOX = (262, 70, 312, 124)      # 玻璃柜（玻璃部分）
SLOTS = [(270, 96), (282, 96), (294, 96)]
CAND = (252, 76)
HOLE_C = (300, 120)

INK = (22, 16, 26)
PAPER = (64, 40, 66)           # 墙纸底（暗紫）
PAPER_P = (82, 54, 84)         # 大马士革花纹
PAPER_D = (56, 34, 58)
WOOD = [(40, 22, 22), (66, 38, 32), (86, 50, 40), (110, 66, 50)]       # 桃花心木护墙板
WALNUT = [(58, 36, 26), (92, 60, 40), (120, 82, 54), (152, 108, 72)]  # 电视外壳 / 柜子
FLOORW = [(74, 50, 38), (116, 80, 56), (132, 92, 64), (150, 106, 74)]   # 地板比墙亮：人站上去要看得清
RUG = [(136, 56, 56), (152, 70, 64), (84, 68, 114), (200, 164, 108)]    # 旧红 / 团花的红 / 藏青 / 金（压低对比）
VELVET = [(60, 30, 70), (88, 48, 104), (116, 70, 136)]
BRASS = [(96, 70, 30), (150, 114, 50), (200, 160, 74), (240, 210, 130)]
CHROME = [(70, 74, 80), (130, 136, 144), (190, 196, 204), (236, 240, 244)]

ANCHORS = dict(screen=list(SCREEN), tv=[160, 120], player=[89, 156], opponent=[239, 156], dolls=[282, 96],
               dolls_box=list(BOX), arcade=[30, 150], wall_hole=list(HOLE_C), door=[12, 160],
               doll_slots=[list(s) for s in SLOTS], console=[160, 140], candles=list(CAND), arcade2=[227, 150],
               walk_x=[8, 312])


# ============================================================ 墙 / 地
def damask(d, x0, y0, x1, y1):
    """大马士革墙纸：竖条底纹 + 每 16×14 一朵对称的花（菱形花心 + 四片叶）。"""
    rect(d, x0, y0, x1, y1, PAPER)
    for x in range(x0, x1 + 1, 4):
        vl(d, x, y0, y1, PAPER_D)
    for j, y in enumerate(range(y0 + 3, y1 - 4, 14)):
        for i, x in enumerate(range(x0 + 4 + (8 if j % 2 else 0), x1 - 4, 16)):
            for (u, v) in ((0, -3), (-1, -2), (1, -2), (-2, -1), (2, -1), (-3, 0), (3, 0), (-2, 1), (2, 1), (-1, 2),
                           (1, 2), (0, 3), (0, 0), (0, 5), (-1, 4), (1, 4)):
                px(d, x + u, y + v, PAPER_P)
            px(d, x, y, (104, 70, 100))


def wall_base():
    im = P.new(PW, H, (0, 0, 0))
    d = ImageDraw.Draw(im)
    rect(d, 0, 0, PW - 1, CEIL, (44, 28, 30))                                      # 格子梁天花板
    for x in range(0, PW, 26):
        rect(d, x, 0, x + 2, CEIL, (66, 42, 40))
    hl(d, 0, PW - 1, CEIL, (30, 20, 22))
    rect(d, 0, CORN[0], PW - 1, CORN[1], WOOD[2])                                  # 檐口
    hl(d, 0, PW - 1, CORN[0], WOOD[3])
    for x in range(0, PW, 6):
        px(d, x, CORN[0] + 2, WOOD[1])
    hl(d, 0, PW - 1, CORN[1], WOOD[0])
    damask(d, 0, CORN[1] + 1, PW - 1, RAIL[0] - 1)
    hl(d, 0, PW - 1, CORN[1] + 1, dk(PAPER, 0.7))
    rect(d, 0, RAIL[0], PW - 1, RAIL[1], WOOD[2])
    hl(d, 0, PW - 1, RAIL[0], WOOD[3])
    hl(d, 0, PW - 1, RAIL[1], WOOD[0])
    # 护墙板：一块块凹板（亮边在上 / 左，暗边在下 / 右）
    rect(d, 0, WAINS[0], PW - 1, WAINS[1], WOOD[2])
    for x in range(2, PW, 22):
        rect(d, x, WAINS[0] + 4, x + 17, WAINS[1] - 4, WOOD[1])
        hl(d, x, x + 17, WAINS[0] + 4, WOOD[0])
        vl(d, x, WAINS[0] + 4, WAINS[1] - 4, WOOD[0])
        hl(d, x + 1, x + 17, WAINS[1] - 4, WOOD[3])
        vl(d, x + 17, WAINS[0] + 5, WAINS[1] - 4, WOOD[3])
    rect(d, 0, SKIRT[0], PW - 1, SKIRT[1], WOOD[0])
    hl(d, 0, PW - 1, SKIRT[0], WOOD[2])
    # 地板 + 地毯
    P.planks_h(d, 0, FLOOR, PW - 1, H - 1, FLOORW, seed=23, ph=4, plen=(30, 70))
    rug(d)
    side_wall(d)
    return im


def rug(d):
    """一大块旧波斯地毯（y 149–176）：藏青外框 + 金色细边 + 暗红底、中间一个大菱形团花；颜色都压暗、对比低。"""
    x0, y0, x1, y1 = 56, 149, 274, 176
    rect(d, x0, y0, x1, y1, RUG[2])
    rect(d, x0 + 3, y0 + 2, x1 - 3, y1 - 2, RUG[0])
    rect(d, x0 + 3, y0 + 2, x1 - 3, y1 - 2, None, outline=dk(RUG[3], 0.7))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for y in range(y0 + 4, y1 - 3):
        half = int((1 - abs(y - cy) / ((y1 - y0) / 2 - 3)) * 46)
        if half > 0:
            hl(d, cx - half, cx + half, y, RUG[1])
            px(d, cx - half, y, dk(RUG[3], 0.6))
            px(d, cx + half, y, dk(RUG[3], 0.6))
    for x in range(x0 + 6, x1 - 5, 6):                                                    # 外框上的小花
        px(d, x, y0 + 1, dk(RUG[3], 0.7))
        px(d, x + 3, y1 - 1, dk(RUG[3], 0.7))
    for x in range(x0, x1 + 1, 2):                                                        # 流苏
        px(d, x, y1 + 1, (150, 130, 100))
    hl(d, x0, x1, y0 - 1, FLOORW[0])


def side_wall(d):
    """左边一截侧墙（透视：和后墙的交线在 x 14，往左越来越近）+ 墙上一扇门（平行四边形）。"""
    for x in range(0, SIDE + 1):
        k = (SIDE - x) / SIDE
        top = int(CORN[1] - k * 10)
        bot = int(SKIRT[1] + k * 16)
        vl(d, x, 0, top, (36, 22, 26))
        vl(d, x, top + 1, bot, dk(PAPER, 0.78))
        if x % 4 == 0:
            vl(d, x, top + 1, bot, dk(PAPER_D, 0.8))
    vl(d, SIDE, CORN[1], SKIRT[1], (30, 20, 26))                                          # 墙角的暗线
    # 门（透视的平行四边形）
    for x in range(2, 13):
        k = (SIDE - x) / SIDE
        top = int(96 - k * 8)
        bot = int(SKIRT[1] + k * 16)
        vl(d, x, top, bot, WALNUT[1] if x not in (2, 12) else WALNUT[0])
        if x in (5, 9):
            vl(d, x, top + 4, bot - 4, WALNUT[0])
    for x in range(1, 14):
        k = (SIDE - x) / SIDE
        px(d, x, int(96 - k * 8) - 1, WALNUT[3])
    px(d, 10, 126, BRASS[2])
    px(d, 10, 127, BRASS[1])


# ============================================================ 家具
def draw_arcade(d, box, body, marquee_txt, mq_col):
    """街机柜：侧板（亮边 + 暗边）、顶上的灯箱（写字）、屏幕框（屏幕本身在 strip 里画）、斜的操作台（摇杆 + 三个按钮）、
    投币口（两个发红光的小口）、底座。"""
    x0, y0, x1, y1 = box
    bd = [dk(body, 0.55), dk(body, 0.8), body, lt(body, 0.25)]
    rect(d, x0, y0 + 8, x1, y1, bd[2], outline=INK)                                       # 机身
    rect(d, x0 + 2, y0, x1 - 2, y0 + 9, (30, 26, 34), outline=INK)                        # 灯箱
    rect(d, x0 + 3, y0 + 1, x1 - 3, y0 + 8, mq_col)
    tw = P.text35_w(marquee_txt)
    P.text35(d, (x0 + x1 + 1) // 2 - tw // 2, y0 + 2, marquee_txt, (40, 20, 30))
    vl(d, x0 + 1, y0 + 9, y1 - 1, bd[3])
    vl(d, x1 - 1, y0 + 9, y1 - 1, bd[0])
    for k in range(3):                                                                     # 侧板的彩条
        vl(d, x0 + 3 + k, y0 + 30, y1 - 4, lt(body, 0.1 * k) if k != 1 else (230, 200, 60))
    rect(d, x0 + 4, y0 + 12, x1 - 4, y0 + 30, (18, 18, 24), outline=INK)                   # 屏幕框
    d.polygon([(x0 + 1, y0 + 33), (x1 - 1, y0 + 33), (x1 + 1, y0 + 40), (x0 - 1, y0 + 40)], fill=P.C(bd[1]),
              outline=P.C(INK))                                                            # 操作台
    vl(d, x0 + 8, y0 + 33, y0 + 36, (30, 30, 30))
    rect(d, x0 + 7, y0 + 32, x0 + 9, y0 + 33, (200, 40, 40))                               # 摇杆
    for i, c in enumerate(((220, 60, 60), (240, 200, 60), (60, 170, 230))):
        px(d, x0 + 15 + i * 4, y0 + 36, c)
        px(d, x0 + 15 + i * 4, y0 + 37, dk(c, 0.6))
    for i in range(2):                                                                      # 投币口
        rect(d, x0 + 10 + i * 8, y0 + 44, x0 + 13 + i * 8, y0 + 48, (40, 34, 40), outline=INK)
        vl(d, x0 + 11 + i * 8, y0 + 45, y0 + 47, (230, 70, 40))
    hl(d, x0, x1, y1 - 2, bd[0])


def draw_shelves(d):
    """玩具架：三层搁板（托架 + 板），上面一样样玩具。"""
    x0, x1 = SHELF_X
    for y in (66, 84, 102):
        rect(d, x0, y, x1, y + 2, WALNUT[2], outline=INK)
        hl(d, x0 + 1, x1 - 1, y, WALNUT[3])
        for bx in (x0 + 4, x1 - 6):
            d.polygon([(bx, y + 3), (bx + 2, y + 3), (bx + 2, y + 7)], fill=P.C(WALNUT[1]))
        hl(d, x0, x1, y + 3, dk(PAPER, 0.7))
    # 上层：铁皮机器人（眼睛在 strip 里闪）、陀螺、飞机模型
    rect(d, 54, 56, 61, 65, (150, 156, 166), outline=INK)                                   # 机器人
    rect(d, 55, 52, 60, 56, (170, 176, 186), outline=INK)
    vl(d, 57, 49, 51, (200, 60, 60))
    px(d, 57, 48, (240, 200, 60))
    rect(d, 52, 58, 53, 62, (130, 136, 146))
    rect(d, 62, 58, 63, 62, (130, 136, 146))
    rect(d, 56, 59, 59, 61, (230, 180, 60))                                                  # 胸口的灯
    d.polygon([(68, 65), (74, 59), (80, 65)], fill=P.C((200, 60, 60)), outline=P.C(INK))   # 陀螺
    hl(d, 70, 78, 62, (240, 220, 120))
    vl(d, 74, 56, 58, (90, 60, 40))
    hl(d, 84, 104, 60, (220, 220, 210))                                                       # 飞机模型
    hl(d, 90, 96, 58, (200, 200, 190))
    hl(d, 90, 96, 62, (200, 200, 190))
    px(d, 103, 58, (200, 60, 60))
    px(d, 84, 61, (90, 90, 90))
    vl(d, 94, 63, 65, (90, 90, 90))
    # 中层：一排游戏卡带（各色标签）+ 魔方
    x = 53
    for i in range(10):
        c = [(200, 60, 60), (60, 120, 200), (230, 200, 60), (80, 170, 90), (180, 90, 180)][i % 5]
        rect(d, x, 76, x + 3, 83, (70, 70, 76), outline=INK)
        rect(d, x + 1, 78, x + 2, 81, c)
        x += 4
    for (u, v, c) in ((96, 79, (220, 40, 40)), (99, 79, (240, 240, 240)), (96, 81, (60, 160, 70)),
                      (99, 81, (240, 200, 40)), (97, 80, (50, 90, 210)), (98, 82, (250, 140, 40))):
        rect(d, u, v, u + 1, v + 1, c)
    rect(d, 95, 78, 101, 83, None, outline=INK)
    # 下层：小汽车、玩具兵、一只发条老鼠
    rect(d, 54, 97, 66, 100, (200, 40, 40), outline=INK)
    rect(d, 57, 94, 63, 97, (220, 60, 60), outline=INK)
    rect(d, 58, 95, 62, 96, (150, 200, 230))
    for wx in (57, 63):
        rect(d, wx - 1, 100, wx + 1, 101, (30, 30, 30))
    for i, sx in enumerate((72, 77, 82)):
        vl(d, sx, 93, 101, (40, 60, 120))
        px(d, sx, 92, (230, 190, 150))
        px(d, sx, 91, (200, 30, 30))
        px(d, sx + 1, 95, (220, 200, 160))
    rect(d, 90, 97, 99, 101, (150, 150, 156), outline=INK)
    px(d, 100, 99, (230, 160, 160))
    vl(d, 89, 95, 98, (200, 170, 60))


def draw_tv(d):
    """大 CRT 电视：胡桃木外壳（圆角）、银色内框、暗着的屏幕（墨绿灰 + 弧形反光）、下面一条喇叭网 + 两个旋钮、兔耳天线；
    下面一个矮电视柜：游戏机（电源灯在 strip）、一排卡带、两根手柄线。"""
    x0, y0, x1, y1 = TV
    sx0, sy0, sx1, sy1 = SCREEN
    d.line((150, y0, 136, 30), fill=P.C(CHROME[2]))                                         # 兔耳天线
    d.line((168, y0, 186, 28), fill=P.C(CHROME[2]))
    px(d, 136, 29, CHROME[3])
    px(d, 186, 27, CHROME[3])
    rect(d, 152, y0 - 3, 166, y0, (40, 36, 40), outline=INK)
    d.rounded_rectangle((x0, y0, x1, y1), radius=5, fill=P.C(WALNUT[2]), outline=P.C(INK))
    hl(d, x0 + 4, x1 - 4, y0 + 1, WALNUT[3])
    vl(d, x0 + 1, y0 + 4, y1 - 4, WALNUT[3])
    vl(d, x1 - 1, y0 + 4, y1 - 4, WALNUT[0])
    hl(d, x0 + 4, x1 - 4, y1 - 1, WALNUT[0])
    for y in range(y0 + 3, y1 - 2, 3):                                                       # 木纹
        if hash01(y, 3) < 0.5:
            hl(d, x0 + 3, x0 + 8, y, WALNUT[1])
            hl(d, x1 - 8, x1 - 3, y + 1, WALNUT[1])
    d.rounded_rectangle((sx0 - 4, sy0 - 4, sx1 + 4, sy1 + 4), radius=4, fill=P.C(CHROME[1]), outline=P.C(INK))
    hl(d, sx0 - 2, sx1 + 2, sy0 - 3, CHROME[3])
    hl(d, sx0 - 2, sx1 + 2, sy1 + 3, CHROME[0])
    d.rounded_rectangle((sx0 - 1, sy0 - 1, sx1 + 1, sy1 + 1), radius=6, fill=P.C((22, 26, 28)))
    rect(d, x0 + 10, sy1 + 6, x1 - 30, y1 - 4, (40, 32, 28))                                 # 喇叭网
    for x in range(x0 + 11, x1 - 30, 2):
        vl(d, x, sy1 + 7, y1 - 5, (70, 58, 48))
    for i, kx in enumerate((x1 - 24, x1 - 14)):                                              # 旋钮
        d.ellipse((kx - 3, sy1 + 5, kx + 3, sy1 + 11), fill=P.C(CHROME[2]), outline=P.C(INK))
        px(d, kx, sy1 + 6, CHROME[3])
        px(d, kx + (1 if i else -1), sy1 + 8, INK)
    # 电视柜
    ax0, ay0, ax1, ay1 = STAND
    rect(d, ax0, ay0, ax1, ay1, WALNUT[1], outline=INK)
    hl(d, ax0 + 1, ax1 - 1, ay0 + 1, WALNUT[3])
    rect(d, ax0 + 4, ay0 + 5, ax1 - 4, ay1 - 3, (34, 24, 22))                                # 柜子里（开格）
    hl(d, ax0 + 4, ax1 - 4, ay0 + 13, WALNUT[2])                                               # 中间一块隔板
    rect(d, 146, 131, 174, 137, (180, 176, 168), outline=INK)                                # 游戏机
    rect(d, 150, 131, 170, 133, (200, 40, 40))
    rect(d, 156, 129, 164, 131, (70, 70, 74), outline=INK)                                    # 插着的卡带
    for (cx_, cy_) in ((150, 136), (154, 136)):
        px(d, cx_, cy_, (60, 60, 64))
    x = ax0 + 6
    for i in range(8):                                                                         # 一排卡带（下层）
        c = [(200, 60, 60), (60, 120, 200), (230, 200, 60), (80, 170, 90)][i % 4]
        rect(d, x, 133, x + 3, 141, (70, 70, 76), outline=INK)
        rect(d, x + 1, 135, x + 2, 138, c)
        x += 4
    rect(d, ax1 - 26, 125, ax1 - 8, 133, (50, 46, 50), outline=INK)                           # 上层：录像带
    hl(d, ax1 - 25, ax1 - 9, 129, (200, 190, 160))
    # 两根手柄线：从游戏机拖到两把椅子（贴着地毯，1 px）
    for (tx, sgn) in ((CHAIRS[0] + 6, -1), (CHAIRS[1] - 6, 1)):
        pts = []
        for k in range(41):
            u = k / 40
            x = 160 + sgn * 12 + (tx - 160 - sgn * 12) * u
            y = 145 + 6 * math.sin(math.pi * u) + u * 2
            pts.append((int(round(x)), int(round(y))))
        for (u, v) in pts:
            px(d, u, v, (24, 22, 26))


def draw_chairs(d):
    """两把矮游戏椅：紫丝绒坐垫（y 145–150）+ 矮靠背（到 y 136），贴着可走带后沿；坐垫上一只手柄。"""
    for cx in CHAIRS:
        x0, x1 = cx - 13, cx + 13
        rect(d, x0 + 2, 135, x1 - 2, 146, VELVET[1], outline=INK)                               # 靠背
        hl(d, x0 + 3, x1 - 3, 136, VELVET[2])
        for bx in range(x0 + 6, x1 - 4, 6):
            px(d, bx, 141, VELVET[0])
        rect(d, x0, 145, x1, 150, VELVET[1], outline=INK)                                      # 坐垫
        hl(d, x0 + 1, x1 - 1, 145, VELVET[2])
        hl(d, x0 + 1, x1 - 1, 149, VELVET[0])
        rect(d, cx - 3, 143, cx + 3, 145, (60, 60, 66), outline=INK)                           # 手柄
        px(d, cx - 2, 144, (220, 60, 60))
        px(d, cx + 2, 144, (60, 120, 220))


def draw_candles(d):
    """三头烛台（铜）：墙上的托 + 三根白蜡烛（火苗在 strip）。"""
    cx, cy = CAND
    rect(d, cx - 1, cy + 4, cx + 1, cy + 14, BRASS[1], outline=INK)
    hl(d, cx - 7, cx + 7, cy + 6, BRASS[2])
    for u in (-6, 0, 6):
        rect(d, cx + u - 1, cy - 3 + (2 if u else 0), cx + u + 1, cy + 5, (236, 230, 210), outline=(120, 110, 100))
        hl(d, cx + u - 2, cx + u + 2, cy + 5, BRASS[2])
    rect(d, cx - 2, cy + 14, cx + 2, cy + 16, BRASS[0])


def draw_vitrine_back(d):
    """玻璃柜的暗红丝绒背板（key hole 时洞从这里打穿）。"""
    x0, y0, x1, y1 = BOX
    rect(d, x0 - 1, y0, x1 + 1, y1, (70, 22, 30))
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if (x + y) % 7 == 0:
                px(d, x, y, (84, 28, 36))


def draw_vitrine(d, broken=False):
    """玻璃柜：深色木框 + 柜脚、暗红丝绒背板、三层（上层 / 中层 y 96 / 底）；中层三个空的人偶座（小铜托 + 名牌）。
    玻璃：在丝绒上叠一层偏冷的反光（斜条）。broken：玻璃碎了（裂纹从右下角放射出去、右下一块缺掉）。"""
    x0, y0, x1, y1 = BOX
    rect(d, x0 - 2, y0 - 4, x1 + 2, y0 - 1, WALNUT[1], outline=INK)                            # 顶
    hl(d, x0 - 1, x1 + 1, y0 - 3, WALNUT[3])
    for sy in (83, SLOTS[0][1]):                                                                  # 两层玻璃搁板
        hl(d, x0, x1, sy, (170, 190, 196))
        hl(d, x0, x1, sy + 1, (96, 110, 116))
    for (sx, sy) in SLOTS:                                                                        # 人偶座 + 名牌
        hl(d, sx - 2, sx + 2, sy - 1, BRASS[2])
        px(d, sx, sy - 2, BRASS[1])
        rect(d, sx - 3, sy + 3, sx + 3, sy + 5, BRASS[1])
        hl(d, sx - 2, sx + 2, sy + 4, BRASS[3])
    if not broken:
        rect(d, x0, y1 - 6, x1, y1, (90, 30, 40))                                                # 底层的丝绒垫
        hl(d, x0, x1, y1 - 6, (120, 44, 54))
    # 木框：四边 + 中间一根竖档（玻璃门的门框）
    for (u0, u1) in ((x0 - 2, x0 - 1), (x1 + 1, x1 + 2), ((x0 + x1) // 2, (x0 + x1) // 2 + 1)):
        rect(d, u0, y0 - 1, u1, y1 + 1, WALNUT[1])
        vl(d, u0, y0 - 1, y1 + 1, WALNUT[3])
    rect(d, x0 - 2, y1, x1 + 2, y1 + 3, WALNUT[1], outline=INK)
    hl(d, x0 - 1, x1 + 1, y1 + 1, WALNUT[3])
    rect(d, x0 - 3, y1 + 4, x1 + 3, y1 + 8, WALNUT[2], outline=INK)                             # 柜子下半截（抽屉）
    hl(d, x0 + 4, x0 + 10, y1 + 6, BRASS[2])
    hl(d, x1 - 10, x1 - 4, y1 + 6, BRASS[2])
    for lx in (x0 - 1, x1 - 1):                                                                   # 柜脚（细长、弯）
        vl(d, lx, y1 + 9, SKIRT[1] + 1, WALNUT[1])
        vl(d, lx + 1, y1 + 9, SKIRT[1] + 1, WALNUT[0])
        px(d, lx - 1 if lx < x1 else lx + 2, SKIRT[1] + 1, WALNUT[1])
    rect(d, x0 - 2, y0 - 1, x1 + 2, y1 + 3, None, outline=INK)


def glass_over(im, broken=False):
    """玻璃的反光（打光以后叠）：左上往右下的几道斜亮条；碎了的时候换成放射的裂纹 + 缺一块（露出后面的洞）。"""
    a = np.array(im).astype(np.float32)
    x0, y0, x1, y1 = BOX
    gone = hole_shape() if broken else None                     # 碎了：洞前面那块玻璃整块掉了，直接看得到洞
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if x in ((x0 + x1) // 2, (x0 + x1) // 2 + 1):
                continue
            if gone is not None and gone[y, x]:
                continue
            s = (x - x0) + (y - y0) * 0.6
            band = (s % 26) < 3 or (s % 26) in (7,)
            k = 0.32 if band else 0.1
            a[y, x, :3] = a[y, x, :3] * (1 - k) + np.array((190, 210, 220)) * k
    im2 = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    if broken:
        d = ImageDraw.Draw(im2)
        hx, hy = HOLE_C
        for k in range(11):                                                   # 裂纹：从缺口边上往外放射
            ang = math.radians(120 + k * 22)
            r0 = 17 * abs(math.cos(ang)) + 23 * abs(math.sin(ang))
            L = 6 + int(hash01(k, 3) * 14)
            for q in range(L):
                rr = r0 * 0.75 + q
                u = int(round(hx + rr * math.cos(ang) * 0.75))
                v = int(round(hy + rr * math.sin(ang)))
                if x0 <= u <= x1 and y0 <= v <= y1 and not gone[v, u]:
                    px(d, u, v, (230, 240, 244) if q % 5 else (150, 170, 180))
    return im2


def hole_shape():
    """墙上的洞：中心 (300,120) 的不规则椭圆（宽 ~34、高 ~46），边缘用 hash 抖成碎口。返回 bool 图。"""
    yy, xx = np.mgrid[0:H, 0:PW]
    cx, cy = HOLE_C
    ang = np.arctan2(yy - cy, xx - cx)
    r = 1 + 0.12 * np.sin(ang * 5 + 1.3) + 0.08 * np.sin(ang * 9)
    m = (((xx - cx) / (17.0 * r)) ** 2 + ((yy - cy) / (23.0 * r)) ** 2) <= 1.0
    m &= yy <= SKIRT[1]
    return m


def draw_hole(im):
    """墙被打穿：洞口外一圈碎灰泥（亮）、一圈红砖断面、里圈一道暗影；洞里是另一边的空房间
    （暗墙、墙角线、地板线、远处一扇窗透一点光）；地上一堆碎砖和玻璃渣。"""
    m = hole_shape()
    a = np.array(im)

    def grow(mm, r):
        out = mm.copy()
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    out |= np.roll(np.roll(mm, dy, 0), dx, 1)
        return out
    g1, g3, g4 = grow(m, 1), grow(m, 3), grow(m, 4)
    bay = P.bayer(PW, H)
    yy, xx = np.mgrid[0:H, 0:PW]
    plaster = g4 & ~g3 & (bay < 0.6) & (yy <= SKIRT[1])
    brick = g3 & ~g1 & (yy <= SKIRT[1])
    a[plaster, :3] = (150, 132, 140)
    bk = brick & (((xx // 3) + (yy // 2)) % 3 != 0)
    a[brick, :3] = (96, 84, 80)
    a[bk, :3] = (164, 82, 62)
    a[g1 & ~m & (yy <= SKIRT[1]), :3] = (40, 24, 28)
    inner = m.copy()
    a[inner, :3] = (70, 62, 84)                                                                # 另一边的空房间（有窗，比这边亮一点）
    a[inner & (yy >= 130), :3] = (92, 78, 76)                                                  # 另一边的地板
    a[inner & (yy == 129), :3] = (44, 36, 48)
    a[inner & (xx == 306), :3] = (54, 46, 64)                                                  # 墙角线
    win = inner & (xx >= 289) & (xx <= 297) & (yy >= 106) & (yy <= 118)
    a[win, :3] = (170, 172, 200)
    a[win & ((xx == 293) | (yy == 112)), :3] = (70, 64, 84)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for i in range(22):                                                                           # 地上的碎砖 + 玻璃渣
        bx = 266 + int(hash01(i, 21) * 52)
        by = 145 + int(hash01(i, 22) * 6)
        if i % 3 == 0:
            px(d, bx, by, (220, 236, 240))
        else:
            rect(d, bx, by, bx + 1 + i % 2, by + 1, (164, 82, 62) if i % 2 else (120, 108, 104))


def contact_shadows(im):
    for (x0, x1, y) in ((AR1[0], AR1[2], FLOOR), (AR2[0], AR2[2], FLOOR), (STAND[0], STAND[2], FLOOR),
                        (BOX[0] - 3, BOX[2] + 3, FLOOR), (CHAIRS[0] - 13, CHAIRS[0] + 13, 151),
                        (CHAIRS[1] - 13, CHAIRS[1] + 13, 151)):
        P.mul_box(im, (x0, y, x1, y), (0.7, 0.7, 0.76))
        P.mul_box(im, (x0 + 1, y + 1, x1 + 1, y + 1), (0.86, 0.86, 0.9))


# ============================================================ 打光
@lru_cache(maxsize=2)
def light_mult(crt=False):
    """偏紫的暗环境光；烛台（暖）、两台街机屏幕（冷蓝 / 洋红）各打一团光；crt=True 时电视屏幕再打一大团冷白光。"""
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    amb = 0.5 + 0.26 * np.clip((yy - 100) / 50.0, 0, 1)       # 地面这一截亮：可走带上的人要看得清
    lights = [dict(x=CAND[0], y=CAND[1], r=58, k=0.5, p=1.5, col=(1.18, 0.98, 0.72)),
              dict(x=31, y=110, r=40, k=0.34, p=1.4, col=(0.86, 1.0, 1.2)),
              dict(x=227, y=114, r=38, k=0.3, p=1.4, col=(1.16, 0.86, 1.1)),
              dict(x=160, y=150, r=110, k=0.16, p=1.2, sy=2.2, col=(1.0, 0.96, 1.0))]
    if crt:
        lights.append(dict(x=160, y=96, r=150, k=0.72, p=1.35, sy=1.1, col=(0.9, 1.04, 1.24)))
    return P.light_map(PW, H, amb, lights, n=10, cool=(0.92, 0.88, 1.06))


def albedo(hole=False):
    im = wall_base()
    d = ImageDraw.Draw(im)
    draw_arcade(d, AR1, (44, 70, 160), 'F-MEGA', (250, 210, 70))
    draw_arcade(d, AR2, (150, 36, 56), 'UFO', (120, 220, 240))
    draw_shelves(d)
    draw_tv(d)
    draw_candles(d)
    draw_vitrine_back(d)
    if hole:
        draw_hole(im)                                                                            # 打穿墙 + 柜子的背板
        d = ImageDraw.Draw(im)
    draw_vitrine(d, broken=hole)
    draw_chairs(d)
    contact_shadows(im)
    return im


def lit_room(hole=False, crt=False):
    im = P.apply_light(albedo(hole), light_mult(crt))
    im = glass_over(im, broken=hole)
    d = ImageDraw.Draw(im)
    # 自己发光：两台街机的灯箱底色、投币口、烛台的蜡烛头、电视暗屏的弧形反光
    for (box, col) in ((AR1, (250, 210, 70)), (AR2, (120, 220, 240))):
        x0, y0, x1, y1 = box
        a = np.array(im)
        sub = a[y0 + 1:y0 + 9, x0 + 3:x1 - 2, :3].astype(np.float32)
        a[y0 + 1:y0 + 9, x0 + 3:x1 - 2, :3] = np.clip(sub * 1.5, 0, 255).astype(np.uint8)
        im.paste(Image.fromarray(a, 'RGBA'))
        P.glow(im, (x0 + x1) // 2, y0 + 20, 22, 18, col, 26, rings=3)
    sx0, sy0, sx1, sy1 = SCREEN
    d = ImageDraw.Draw(im)
    for k in range(18):                                                                          # 暗屏上的弧形反光
        u = sx0 + 6 + k
        v = sy0 + 5 + int(0.04 * (k - 9) ** 2)
        px(d, u, v, (64, 74, 76))
    px(d, sx1 - 6, sy1 - 5, (52, 60, 62))
    return im


@lru_cache(maxsize=1)
def near_img():
    return P.opaque(lit_room(False))


HOLE_BOX = (256, 62, PW, 156)


@lru_cache(maxsize=1)
def hole_img():
    """key hole：重画整间屋子（墙上打穿 + 玻璃碎了 + 碎砖），只裁出右边那一块当 pano。
    按“电视亮着”打光：脚本里墙被打穿（11-07）以后电视一直亮着（11-05 开 crt，后面没关），这一块画在 crt_room 上面。"""
    full = P.opaque(lit_room(True, True))
    out = P.new(PW, H)
    x0, y0, x1, y1 = HOLE_BOX
    paste(out, full.crop(HOLE_BOX), x0, y0)
    return out


@lru_cache(maxsize=1)
def crt_room_img():
    """key crt：电视亮着时的整间屋子（同一套底色，多一盏“屏幕”冷白光重新打光；不透明，比半透明叠一层蓝更像光）。
    屏幕本身在 crt strip 里画。"""
    im = lit_room(False, True)
    sx0, sy0, sx1, sy1 = SCREEN
    P.glow(im, (sx0 + sx1) // 2, (sy0 + sy1) // 2, 60, 44, (190, 214, 255), 26, rings=3)       # 屏幕四周的辉光
    return P.opaque(im)


# ============================================================ 会动的
def crt_frame(t):
    """电视屏幕（8 帧 @8 fps）：蓝白雪花（每帧换一批点）+ 隔行扫描线 + 一道往下滚的亮带 + 四角暗、四边一圈辉光。"""
    im = P.new(PW, H)
    a = np.zeros((H, PW, 4), np.uint8)
    f = fno(t, 8, 8.0)
    sx0, sy0, sx1, sy1 = SCREEN
    band = sy0 + (f * (sy1 - sy0)) // 8
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            n = hash01(x, y, f, 7)
            c = 150 + n * 90
            if (y - sy0) % 2:
                c *= 0.78
            if abs(y - band) <= 2:
                c += 26
            ex = min(x - sx0, sx1 - x, y - sy0, sy1 - y)
            if ex < 3:
                c *= 0.7 + 0.1 * ex
            a[y, x, :3] = np.clip((c * 0.82, c * 0.92, c * 1.08), 0, 255)
            a[y, x, 3] = 255
    # 圆角：四个角各挖掉一点（和外框的圆角一致）
    for (cx, cy) in ((sx0, sy0), (sx1, sy0), (sx0, sy1), (sx1, sy1)):
        for (u, v) in ((0, 0), (1, 0), (0, 1)):
            a[cy + (v if cy == sy0 else -v), cx + (u if cx == sx0 else -u), 3] = 0
    return Image.fromarray(a, 'RGBA')


def arcade1_frame(t):
    """街机 1 的 F-MEGA 演示：伪 3D 赛道（路往近处滚的横线、两辆车左右换道）+ 灯箱一明一暗。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    x0, y0, x1, y1 = AR1
    sx0, sy0, sx1, sy1 = x0 + 5, y0 + 13, x1 - 5, y0 + 29
    rect(d, sx0, sy0, sx1, sy0 + 5, (40, 70, 150))                                               # 天
    rect(d, sx0, sy0 + 6, sx1, sy1, (40, 120, 60))                                               # 草地
    cx = (sx0 + sx1) // 2
    for y in range(sy0 + 6, sy1 + 1):                                                            # 路面梯形
        hw = 1 + (y - sy0 - 6) * 9 // (sy1 - sy0 - 6)
        hl(d, cx - hw, cx + hw, y, (90, 90, 96))
        if (y * 2 - f * 3) % 6 < 2:
            px(d, cx - hw, y, (230, 230, 230))
            px(d, cx + hw, y, (230, 230, 230))
    px(d, cx + (1 if f < 4 else -1), sy0 + 9, (220, 60, 60))                                       # 远处的车
    lane = (-3, -3, -2, 0, 2, 3, 3, 1)[f]
    rect(d, cx + lane - 1, sy1 - 3, cx + lane + 1, sy1 - 1, (60, 200, 90))                        # 自己的车
    px(d, cx + lane, sy1 - 4, (200, 255, 210))
    k = (1.0, 0.9, 0.8, 0.9, 1.0, 0.85, 0.75, 0.9)[f]
    rect(d, x0 + 3, y0 + 1, x0 + 3, y0 + 8, mix((120, 90, 30), (255, 230, 120), k))                # 灯箱左右两条灯
    rect(d, x1 - 3, y0 + 1, x1 - 3, y0 + 8, mix((120, 90, 30), (255, 230, 120), k))
    return im


def arcade2_frame(t):
    """街机 2：星星往下飞（8 帧走 16 px，正好一圈）+ 小飞碟左右晃。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    x0, y0, x1, y1 = AR2
    sx0, sy0, sx1, sy1 = x0 + 5, y0 + 13, x1 - 5, y0 + 29
    rect(d, sx0, sy0, sx1, sy1, (10, 10, 30))
    for i in range(12):
        x = sx0 + int(hash01(i, 5) * (sx1 - sx0 + 1))
        y = sy0 + (int(hash01(i, 6) * 16) + f * 2) % 17
        px(d, x, y, (220, 220, 255) if i % 3 else (120, 120, 200))
    ux = (sx0 + sx1) // 2 + (-3, -2, 0, 2, 3, 2, 0, -2)[f]
    hl(d, ux - 2, ux + 2, sy0 + 4, (120, 230, 240))
    px(d, ux, sy0 + 3, (240, 240, 120))
    px(d, (sx0 + sx1) // 2, sy1 - 1, (240, 80, 80))
    px(d, (sx0 + sx1) // 2 - 1, sy1, (240, 80, 80))
    px(d, (sx0 + sx1) // 2 + 1, sy1, (240, 80, 80))
    return im


def candle_frame(t):
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    cx, cy = CAND
    for i, u in enumerate((-6, 0, 6)):
        top = cy - 4 + (2 if u else 0)
        h = 2 + ((f + i * 3) % 4 == 0)
        sway = (0, 0, 1, 0, 0, -1, 0, 0)[(f + i * 2) % 8]
        for k in range(h + 1):
            px(d, cx + u + (sway if k == h else 0), top - k, (255, 236, 150) if k < h else (255, 160, 60))
        px(d, cx + u, top + 1, (255, 250, 220))
    return im


def toys_frame(t):
    """玩具机器人的眼睛（亮 / 暗交替，偶尔眨一下）+ 游戏机的红色电源灯（一明一暗）。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    on = (1, 1, 0, 1, 1, 1, 0, 0)[f]
    k = (1.0, 0.8, 0.6, 0.4, 0.3, 0.45, 0.65, 0.85)[f]
    for x in (56, 59):
        px(d, x, 54, (255, 60, 40) if on else (90, 30, 30))
    px(d, 167, 134, mix((80, 20, 20), (255, 60, 50), k))
    return im


# ============================================================ 组装
@lru_cache(maxsize=1)
def specs():
    sx0, sy0, sx1, sy1 = SCREEN
    S = [dict(t='pano', name='near', img=near_img(), k=1.0),
         dict(t='pano', name='crt_room', img=crt_room_img(), k=1.0, key='crt'),
         dict(t='pano', name='hole', img=hole_img(), k=1.0, key='hole'),
         P.strip('crt', crt_frame, (sx0, sy0, sx1 + 1, sy1 + 1), n=8, fps=8.0, key='crt'),
         P.strip('arcade1', arcade1_frame, (AR1[0], AR1[1], AR1[2] + 1, AR1[1] + 31)),
         P.strip('arcade2', arcade2_frame, (AR2[0], AR2[1] + 12, AR2[2] + 1, AR2[1] + 31)),
         P.strip('candle', candle_frame, (CAND[0] - 9, CAND[1] - 10, CAND[0] + 10, CAND[1] + 2)),
         P.strip('toys', toys_frame, (50, 50, 172, 138))]
    return S


def anchors():
    return {k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in ANCHORS.items()}


def export(ex, BJ):
    S = specs()
    layers, fg = P.export_layers(ex, BJ, S)
    st = ex.stage(PW, GROUND, WALK, layers, fg, anchors())
    if ex.check_on:
        _checks(ex, BJ, st, S)
    return st


def _checks(ex, BJ, st, S):
    near = near_img()
    m0, s0 = P.walk_stats(near, WALK)
    cfg = dict(
        name='游戏室', pw=PW, walk=WALK,
        states=[{}, {'crt': True}, {'hole': True}, {'crt': True, 'hole': True}],
        opaque=[('近景整张不透明', near, (0, 0, PW, H)), ('key crt 整间屋子不透明', crt_room_img(), (0, 0, PW, H)),
                ('key hole 那一块整片不透明', hole_img(), HOLE_BOX)],
        binary=[('近景只有 0 / 255 两种透明度', near), ('key crt 只有 0 / 255', crt_room_img()),
                ('key hole 只有 0 / 255', hole_img())],
        stand=['player', 'opponent', 'door'],
        inside=['screen', 'tv', 'dolls', 'dolls_box', 'arcade', 'wall_hole', 'doll_slots', 'console', 'candles', 'arcade2'],
        notes=['可走带亮度（y %d–%d）：均值 %.0f 标准差 %.1f' % (WALK[0], WALK[1], m0, s0)],
    )
    P.std_checks(ex, BJ, st, S, cfg)
    # 人偶座：三个都在玻璃柜框里、彼此间距 ≥ 10（人偶 8 px 宽）、10 px 高的人偶站上去不顶到上一层搁板（y 83）
    x0, y0, x1, y1 = BOX
    bad = sum(1 for (sx, sy) in SLOTS if not (x0 + 4 <= sx <= x1 - 4 and y0 + 12 <= sy <= y1))
    bad += sum(1 for a, b in zip(SLOTS, SLOTS[1:]) if b[0] - a[0] < 10)
    bad += sum(1 for (sx, sy) in SLOTS if sy - 10 <= 84)
    ex.checked('三个人偶座在玻璃柜里、间距 ≥ 10、人偶站上去不顶到上一层（不满足的条数）', bad)
    # 平时屏幕是暗的；key crt 时屏幕整块亮
    sx0, sy0, sx1, sy1 = SCREEN
    lum0 = np.array(near)[sy0 + 3:sy1 - 2, sx0 + 3:sx1 - 2, :3].mean()
    lum1 = np.array(crt_frame(0.0))[sy0 + 3:sy1 - 2, sx0 + 3:sx1 - 2, :3].mean()
    ex.checked('屏幕平时是暗的（均值 %.0f ≤ 40）、key crt 亮（均值 %.0f ≥ 140）' % (lum0, lum1),
               int(lum0 > 40) + int(lum1 < 140))
    # 墙洞：洞心在 key hole 那块里，和底图不一样
    hx, hy = HOLE_C
    diff = (np.abs(np.array(hole_img())[hy - 4:hy + 5, hx - 4:hx + 5, :3].astype(int)
                   - np.array(crt_room_img())[hy - 4:hy + 5, hx - 4:hx + 5, :3].astype(int)).max(-1) > 0).sum()
    ex.checked('key hole：wall_hole 周围 9×9 和平时不一样（不一样的像素 %d ≥ 60）' % diff, int(diff < 60))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch11', 'after')
    os.makedirs(od, exist_ok=True)
    P.direct(specs(), 0, 0.5, {'crt': True}).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
        os.path.join(od, 'game_room_solo.png'))
    print('ok')
