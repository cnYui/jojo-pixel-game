# -*- coding: utf-8 -*-
r"""cafe_interior —— 第10章「开罗」：开罗郊外的咖啡馆（地图 cafe_ch10），第 21 战「奥西里斯神」达比的赌局。
2026-10-19 第三轮背景重画（interiors 组）新画（改前是 later_stages 的占位：原工程 _cafe_static + 前景牌桌）。
共用零件在 interior_parts.py。

320 单屏，ground 156，可走带 y 150–172（花砖地，对比压低）；侧视平视，后墙 + 地面（地面从 y 145 起）。
下午的咖啡馆：屋里昏暗，三处光——牌桌上方的吊灯（暖黄）、左边拱窗透进来的日光（窗外是沙漠，远处是开罗）、吧台后面的灯。
竖向：天花板木板 0–9，几何花纹的檐口饰带 11–17，赭黄灰泥墙 18–101，腰线 102–104，护墙板 105–138，踢脚板 139–144，地面 145–179。
从左到右：
  x 2–24     入口木门（anchors.door = 门前站点）：上半截磨砂玻璃透着外面的日光、两块凹板、黄铜把手
  x 28–40    墙上挂着一块小黑板菜单（粉笔写的字，看不清）
  x 27–45    地上的猫窝（anchors.cat）：藤编篮子 + 格子布垫（猫是剧情摆的，篮子 8 px 高，不挡人）
  x 37–83    拱窗（anchors.window = 窗心）：窗外下午的沙漠、远处开罗的圆顶和宣礼塔、两棵椰枣树；两边红窗帘（strip 轻轻晃）；
             窗台上一盆罗勒；窗下一张小边桌（双陆棋盒、一杯红茶）；一道斜斜的日光落到地上（光柱里浮尘 strip）
  x 74–89    左座（anchors.seat_left）：圆木凳，凳面 y 142（坐姿 sit 的大腿正好压在凳面上）
  x 91–100   水烟壶（炭火一明一暗 strip）
  x 108–140  墙上的画（anchors.painting = 画心）：“奥西里斯的审判”——纸莎草色的底，中间一架天平，左盘一颗心脏、右盘一根羽毛
  x 100–220  牌桌（fg 前景，画在人物前面）：绿呢桌面 = anchors.table [104,118,216,132]，木框、正面一道厚边、中间一根立柱 + 十字脚；
             桌面中间被吊灯照亮；桌上空着（筹码 / 扑克是剧情摆的，anchors.chips）
  x 150–170  牌桌上方的吊灯：绿玻璃灯罩（strip：吊扇吹得轻轻晃 ±1 px）
  x 184–212  墙上的挂钟 + 一张金字塔的老照片
  x 224–252  右座（anchors.seat_right）：达比的高背红丝绒扶手椅（拉扣、铜钉边）；达比的 sit 帧自带一截小桌，椅子画在他身后
  x 236      天花板上的吊扇（strip 转）
  x 256–320  吧台（anchors.bar = 老板站的点）：后墙一面镜子 + 两层酒架（各色酒瓶、玻璃杯），上面一块写着阿拉伯字的绿招牌；
             台面上一台黄铜收银机、一个烟灰缸（烟 strip）、一只黄铜咖啡壶（热气 strip）；台面正面竖木板 + 黄铜踩脚杆
地面：米黄 / 浅玫瑰两色花砖（近大远小，缝往外斜），砖心一个小菱形；牌桌底下一圈淡影；anchors.meat 三个点附近是干净的地砖。

图层（从后往前）：
  near      pano  k 1          整张屋子（打好光：吊灯 / 窗 / 吧台三处暖光 + 偏冷的环境光，分档、只在档的交界抖）
  curtain   strip 8 帧 @4 fps   拱窗两边的窗帘下摆轻轻晃
  motes     strip 8 帧 @4 fps   日光光柱里的浮尘（绕小圈、一闪一闪）
  shisha    strip 8 帧 @4 fps   水烟壶的炭火一明一暗 + 一缕细烟
  steam     strip 8 帧 @4 fps   吧台咖啡壶冒的热气
  smoke     strip 8 帧 @4 fps   吧台烟灰缸里那支烟的细烟
  fan       strip 8 帧 @8 fps   吊扇转（四片桨叶，8 帧转 90°）
  lamp      strip 8 帧 @4 fps   吊灯被吊扇吹得轻轻晃（灯绳 + 灯罩 + 灯泡）
  fg: table      pano  k 1          前景牌桌（打好光，只有 0 / 255 透明度）
  fg: bar_front  pano  k 1  key bar（可选，规格之外加的）：吧台台面 + 正面那一截（和底图一模一样），画在人物前面——
                 剧情把老板放在 anchors.bar [280,146] 再打开它，台面就挡住老板的下半身（不开的时候老板像站在吧台前面）
锚点（素材总表定稿的名字一个不少）：table [104,118,216,132]、cafe_table [160,132]、seat_left [82,150]、seat_right [238,150]、
  dealer [160,127]（⚠ 从 [160,146] 往后挪了 19 px，原因见交付记录：小哥 26 px 高，脚在 146 时头顶 y 120，整个人被 y 115–137 的
  前景桌面盖住；脚在 127 时头 + 肩 y 101–114 露在桌面后沿上面、发牌的手正好在桌沿，下半身被牌桌挡住）、cat [36,164]、
  bar [280,146]、window [60,70]、chips [160,124]、painting [124,74]、door [12,160]、meat [[132,168],[160,168],[188,168]]；
  另外多导出：dealer_talk [160,152]（和小哥搭话时站的地面点）、lamp [160,86]、fan [236,13]、clock [198,58]、walk_x [8,312]。
⚠ 地图建议加 fgDepth: 148（engine/world.js 支持）：前景牌桌 / 吧台前沿按这条脚底线参与纵深排序——可走带里的人画在牌桌前面，
  站在 y < 148 的小哥 / 老板被挡；桌上的筹码 / 扑克道具要给 depth ≥ 149（或用 L.pixel 画），不然被前景牌桌盖住。
key：bar（可选：吧台前沿画到人物前面）。
单独运行：python -B tools/bg_new/cafe_interior.py → tools/bg_new/_preview/ch10/after/cafe_interior_solo.png
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
CEIL = 9                      # 天花板到这里
FRIEZE = (11, 17)             # 檐口饰带
RAIL = (102, 104)             # 腰线
WAINS = (105, 138)            # 护墙板
SKIRT = (139, 144)            # 踢脚板
FLOOR = 145                   # 地面从这里开始
DOOR = (2, 24, 100)           # 门 x0 x1 门顶
WIN = (44, 76, 46, 96)        # 拱窗玻璃（含拱顶）x0 x1 顶 底
WIN_C = (60, 62, 16)          # 拱顶圆心 + 半径
TABLE = (104, 118, 216, 132)  # 绿呢桌面
RIM = (100, 116, 220, 136)    # 木框外沿（正面那道厚边到 136）
PED = (155, 165)              # 立柱
LAMP_X, SHADE = 160, (78, 86)
STOOL = (74, 89, 142)         # 左座凳面 x0 x1 y
CHAIR = (224, 252)            # 达比的扶手椅
BAR_X0, BAR_TOP = 256, 132    # 吧台左沿 / 台面（老板脚在 146：台面 132 时露出头 + 肩）
FAN = (236, 13)
URN = (298, 311)              # 咖啡壶 x
ASH = (288, 130)              # 烟灰缸（烟从这里冒）
SHISHA = (96, 117)            # 水烟壶：中心 x / 烟碗顶 y
CLOCK = (198, 58)
MEAT = [(132, 168), (160, 168), (188, 168)]
BEAM = [(45, 92), (76, 92), (128, 160), (88, 160)]     # 日光光柱（窗下沿 → 地面）

INK = (40, 26, 24)
PLASTER = (204, 164, 116)
PLASTER_D = (190, 150, 104)
PLASTER_L = (214, 178, 130)
WOOD = [(52, 32, 22), (84, 54, 36), (104, 68, 44), (128, 86, 56)]            # 护墙板：缝 → 亮
WOOD_L = [(74, 46, 30), (112, 74, 46), (140, 96, 60), (170, 124, 80)]        # 家具（偏亮的胡桃木）
BRASS = [(96, 70, 30), (150, 114, 50), (200, 160, 74), (240, 210, 130)]
VELVET = [(70, 18, 24), (104, 26, 34), (140, 36, 44), (176, 64, 66)]
FELT = [(16, 58, 38), (28, 84, 54), (38, 104, 66), (52, 128, 80), (74, 152, 96)]
TILE_A = (196, 176, 142)      # 米黄花砖
TILE_B = (182, 150, 120)      # 浅玫瑰花砖
GROUT = (156, 130, 104)

ANCHORS = dict(table=[104, 118, 216, 132], cafe_table=[160, 132], seat_left=[82, 150], seat_right=[238, 150],
               dealer=[160, 127], cat=[36, 164], bar=[280, 146], window=[60, 70], chips=[160, 124],
               painting=[124, 74], door=[12, 160], meat=[list(m) for m in MEAT],
               dealer_talk=[160, 152], lamp=[160, 86], fan=list(FAN), clock=list(CLOCK), walk_x=[8, 312])


# ============================================================ 墙 / 地
def floor_tiles(d):
    """花砖地：行高近大远小（3 → 9 px），竖缝按“离画面中线越远越往外斜”画（一点透视）；米黄 / 浅玫瑰两色棋盘，
    米黄砖中间一个淡淡的小菱形。对比压低：两色亮度只差 ~16。"""
    ys = [FLOOR, 148, 152, 157, 163, 170, 178, 186]
    for r in range(len(ys) - 1):
        y0, y1 = ys[r], min(H - 1, ys[r + 1] - 1)
        if y0 > H - 1:
            break
        for y in range(y0, y1 + 1):
            s = 1 + (y - FLOOR) / 70.0
            for x in range(PW):
                u = (x - 160) / s / 15.0
                k = math.floor(u)
                c = TILE_A if (k + r) % 2 == 0 else TILE_B
                fu = u - k
                if fu < 1.0 / 15.0 * s * 0.9 or y == y1:
                    c = GROUT
                elif c == TILE_A:
                    cy = (y0 + y1) / 2.0
                    if abs(fu - 0.5) * 15 * s / max(1, (y1 - y0)) + abs(y - cy) / max(1, (y1 - y0) / 2.0) < 0.42:
                        c = (184, 160, 126)
                elif y == y0:
                    c = lt(c, 0.08)
                px(d, x, y, c)


def wall_base():
    im = P.new(PW, H, (0, 0, 0))
    a = np.array(im)
    a[...] = (*PLASTER, 255)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 天花板：深色木板 + 檐口线脚（下沿一条亮边、墙上一条影）
    rect(d, 0, 0, PW - 1, CEIL - 3, (70, 46, 32))
    for x in range(0, PW, 22):
        vl(d, x, 0, CEIL - 3, (54, 34, 24))
    hl(d, 0, PW - 1, CEIL - 2, (110, 74, 48))
    hl(d, 0, PW - 1, CEIL - 1, (138, 96, 62))
    hl(d, 0, PW - 1, CEIL, (90, 60, 40))
    # 檐口饰带：青绿底 + 赤陶 / 米色的小菱形（开罗老咖啡馆常见的模板花）
    y0, y1 = FRIEZE
    rect(d, 0, y0, PW - 1, y1, (62, 118, 112))
    hl(d, 0, PW - 1, y0, (40, 80, 76))
    hl(d, 0, PW - 1, y1, (40, 80, 76))
    for x in range(0, PW, 8):
        cx, cy = x + 4, (y0 + y1) // 2
        for (u, v, c) in ((0, -2, (214, 186, 140)), (-1, -1, (196, 102, 70)), (1, -1, (196, 102, 70)),
                          (-2, 0, (214, 186, 140)), (0, 0, (196, 102, 70)), (2, 0, (214, 186, 140)),
                          (-1, 1, (196, 102, 70)), (1, 1, (196, 102, 70)), (0, 2, (214, 186, 140))):
            px(d, cx + u, cy + v, c)
        px(d, x, y0 + 1, (96, 150, 142))
        px(d, x, y1 - 1, (96, 150, 142))
    hl(d, 0, PW - 1, y1 + 1, dk(PLASTER, 0.86))                 # 饰带下面一条影
    # 灰泥的斑驳 + 几道往下淌的水渍
    P.mottle(im, (0, y1 + 2, PW - 1, RAIL[0] - 1), PLASTER, PLASTER_D, PLASTER_L, seed=41, cell=6, lo=0.32, hi=0.68,
             streaks=5)
    # 腰线 + 护墙板 + 踢脚板
    rect(d, 0, RAIL[0], PW - 1, RAIL[1], WOOD_L[2])
    hl(d, 0, PW - 1, RAIL[0], WOOD_L[3])
    hl(d, 0, PW - 1, RAIL[1], WOOD_L[0])
    P.wood_boards_v(d, 0, WAINS[0], PW - 1, WAINS[1], WOOD, seed=7, bw=9)
    hl(d, 0, PW - 1, WAINS[0], dk(WOOD[1], 0.8))                 # 腰线压出来的影
    rect(d, 0, SKIRT[0], PW - 1, SKIRT[1], (70, 44, 30))
    hl(d, 0, PW - 1, SKIRT[0], (118, 80, 52))
    hl(d, 0, PW - 1, SKIRT[1], (48, 30, 22))
    floor_tiles(d)
    return im


# ============================================================ 家具 / 物件
def draw_door(d):
    x0, x1, top = DOOR
    rect(d, x0 - 1, top - 2, x1 + 1, SKIRT[1], WOOD_L[1], outline=INK)       # 门套
    hl(d, x0, x1, top - 1, WOOD_L[3])
    rect(d, x0 + 1, top + 1, x1 - 1, SKIRT[1], WOOD_L[2])                    # 门扇
    vl(d, x0 + 1, top + 1, SKIRT[1], WOOD_L[3])
    vl(d, x1 - 1, top + 1, SKIRT[1], WOOD_L[0])
    rect(d, x0 + 4, top + 4, x1 - 4, top + 21, (60, 44, 34), outline=INK)     # 玻璃框（玻璃本身打光以后再画）
    for (yy0, yy1) in ((top + 25, top + 33), (top + 36, SKIRT[1] - 3)):       # 两块凹板
        rect(d, x0 + 4, yy0, x1 - 4, yy1, WOOD_L[1])
        hl(d, x0 + 4, x1 - 4, yy0, WOOD_L[0])
        vl(d, x0 + 4, yy0, yy1, WOOD_L[0])
        hl(d, x0 + 5, x1 - 4, yy1, WOOD_L[3])
        vl(d, x1 - 4, yy0 + 1, yy1, WOOD_L[3])
    rect(d, x1 - 4, top + 23, x1 - 3, top + 24, BRASS[2])                     # 把手
    px(d, x1 - 4, top + 23, BRASS[3])
    px(d, x1 - 3, top + 25, INK)


def door_glass(d):
    """门上的磨砂玻璃：外面下午的日光，竖条纹的磨砂 + 中间一根窗棂（自己发光，打光以后画）。"""
    x0, x1, top = DOOR
    for y in range(top + 5, top + 21):
        for x in range(x0 + 5, x1 - 4):
            c = mix((250, 236, 200), (232, 206, 160), (y - top - 5) / 16)
            if (x + y // 3) % 4 == 0:
                c = dk(c, 0.94)
            px(d, x, y, c)
    vl(d, (x0 + x1) // 2, top + 5, top + 20, (96, 70, 50))
    hl(d, x0 + 5, x1 - 5, top + 12, (96, 70, 50))


def draw_menu(d):
    """小黑板菜单：木框、粉笔写的几行看不清的字（一行一行的小波浪）+ 一只咖啡杯的小画。"""
    x0, y0, x1, y1 = 28, 72, 40, 92
    vl(d, 34, 66, 71, (90, 80, 70))
    px(d, 34, 65, BRASS[1])
    hl(d, 30, 33, 71 - 2, (90, 80, 70))
    hl(d, 35, 38, 71 - 2, (90, 80, 70))
    rect(d, x0, y0, x1, y1, WOOD_L[2], outline=INK)
    rect(d, x0 + 2, y0 + 2, x1 - 2, y1 - 2, (46, 58, 52))
    for i, yy in enumerate(range(y0 + 4, y1 - 5, 3)):
        for x in range(x0 + 3, x1 - 3 - (i % 2) * 2):
            if hash01(x, yy, 3) < 0.62:
                px(d, x, yy - (1 if hash01(x, yy) < 0.3 else 0), (206, 210, 200))
    rect(d, x0 + 4, y1 - 5, x0 + 6, y1 - 3, (206, 210, 200))               # 咖啡杯
    px(d, x0 + 7, y1 - 4, (206, 210, 200))


def draw_window(d):
    """拱窗的木框 / 窗棂 / 窗台（玻璃里的景色打光以后画）。"""
    x0, x1, y0, y1 = WIN
    cx, cy, r = WIN_C
    d.pieslice((cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), 180, 360, fill=P.C(WOOD_L[1]), outline=P.C(INK))
    rect(d, x0 - 2, cy, x1 + 2, y1, WOOD_L[1], outline=INK)
    d.pieslice((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=P.C((70, 80, 90)))
    rect(d, x0, cy, x1, y1 - 1, (70, 80, 90))
    rect(d, x0 - 4, y1, x1 + 4, y1 + 3, WOOD_L[2], outline=INK)                   # 窗台
    hl(d, x0 - 3, x1 + 3, y1 + 1, WOOD_L[3])
    hl(d, x0 - 3, x1 + 3, y1 + 4, dk(PLASTER, 0.8))                              # 窗台下的影
    # 窗台上一盆罗勒（陶盆 + 一团叶子）
    rect(d, 68, y1 - 5, 73, y1 - 1, (172, 92, 58), outline=INK)
    hl(d, 68, 73, y1 - 5, (206, 126, 84))
    for (u, v) in ((69, y1 - 7), (70, y1 - 8), (71, y1 - 9), (72, y1 - 8), (73, y1 - 7), (70, y1 - 6), (72, y1 - 6),
                   (71, y1 - 7), (69, y1 - 6), (74, y1 - 8)):
        px(d, u, v, (70, 130, 64) if (u + v) % 2 else (100, 160, 80))


def window_view(im):
    """窗外：下午的天（上浅蓝 → 地平线暖米色）、远处开罗的天际线（圆顶、宣礼塔、方楼，罩一层暖雾）、
    近处的沙地和两棵椰枣树。自己发光，打光以后画；窗棂最后压上去。"""
    x0, x1, y0, y1 = WIN
    cx, cy, r = WIN_C
    lay = P.new(PW, H)
    d = ImageDraw.Draw(lay)
    hz = 82
    for y in range(y0, y1):
        u = (y - y0) / (hz - y0)
        c = mix((150, 188, 214), (246, 216, 164), min(1, max(0, u)) ** 1.3) if y < hz else \
            mix((226, 182, 124), (204, 156, 100), (y - hz) / (y1 - hz))
        hl(d, x0, x1, y, c)
    sky = (196, 170, 150)
    for (bx, bw, bh) in ((45, 5, 4), (50, 4, 6), (55, 6, 3), (62, 5, 5), (68, 7, 3), (74, 3, 4)):
        rect(d, bx, hz - bh, bx + bw - 1, hz - 1, sky)                          # 方楼
    for (dx, dy, rr) in ((53, 79, 3), (66, 78, 3), (59, 80, 2)):                 # 圆顶
        d.pieslice((dx - rr, dy - rr, dx + rr, dy + rr), 180, 360, fill=P.C((186, 160, 142)))
        px(d, dx, dy - rr - 1, (176, 150, 132))
    for (mx, mh) in ((49, 11), (58, 8), (71, 13)):                               # 宣礼塔（细长 + 尖顶 + 一圈阳台）
        vl(d, mx, hz - mh, hz - 1, (178, 152, 136))
        vl(d, mx + 1, hz - mh + 1, hz - 1, (190, 166, 148))
        px(d, mx, hz - mh - 1, (170, 144, 128))
        hl(d, mx - 1, mx + 2, hz - mh + 4, (170, 144, 128))
    for x in range(x0, x1 + 1):                                                  # 沙丘的亮脊
        yy = hz + 4 + int(2 * math.sin(x * 0.3) + hash01(x, 2) * 1.2)
        px(d, x, yy, (238, 204, 146))
    for (tx, ty, h) in ((48, 92, 11), (70, 91, 8)):                              # 椰枣树
        for k in range(h):
            px(d, tx + (1 if k > h * 0.6 else 0), ty - k, (110, 80, 54))
        top = ty - h
        for (u, v) in ((-3, 1), (-2, 0), (-1, -1), (1, -1), (2, 0), (3, 1), (-4, 2), (4, 2), (0, -2), (-1, 0), (1, 0)):
            px(d, tx + u, top + v, (64, 104, 60) if v < 1 else (52, 88, 52))
    # 只留在窗玻璃里（拱顶 + 方框）
    m = np.zeros((H, PW), bool)
    yy, xx = np.mgrid[0:H, 0:PW]
    m |= (((xx - cx) ** 2 + (yy - cy) ** 2) <= r * r) & (yy <= cy)
    m |= (xx >= x0) & (xx <= x1) & (yy >= cy) & (yy < y1)
    a = np.array(lay)
    a[~m, 3] = 0
    im.alpha_composite(Image.fromarray(a, 'RGBA'))
    d2 = ImageDraw.Draw(im)
    vl(d2, cx, y0 - 1, y1 - 1, WOOD_L[1])                                         # 窗棂（十字）
    vl(d2, cx + 1, y0, y1 - 1, WOOD_L[0])
    hl(d2, x0, x1, 72, WOOD_L[1])
    hl(d2, x0, x1, 73, WOOD_L[0])
    for (u, v) in ((cx - 9, 52), (cx - 10, 53), (cx + 5, 76), (cx + 6, 75)):    # 玻璃的反光
        px(d2, u, v, (252, 246, 232))


def draw_side_table(d):
    """窗下的小边桌：圆腿、台面上一只双陆棋盒（镶嵌花纹）+ 一杯红茶（玻璃杯）。"""
    rect(d, 46, 126, 72, 128, WOOD_L[2], outline=INK)
    hl(d, 47, 71, 126, WOOD_L[3])
    for x in (48, 69):
        rect(d, x, 129, x + 2, SKIRT[1] + 1, WOOD_L[1])
        vl(d, x, 129, SKIRT[1] + 1, WOOD_L[2])
        px(d, x + 1, 134, WOOD_L[3])
        hl(d, x - 1, x + 3, SKIRT[1] + 2, INK)
    hl(d, 50, 68, 140, WOOD_L[0])                                                  # 横撑
    rect(d, 49, 121, 61, 125, (120, 70, 40), outline=INK)                          # 双陆棋盒
    for x in range(50, 61, 2):
        px(d, x, 123, (226, 206, 160))
    hl(d, 50, 60, 122, (160, 100, 58))
    rect(d, 65, 121, 67, 125, (176, 70, 40), outline=(90, 70, 60))               # 红茶
    px(d, 65, 122, (230, 170, 120))


def draw_stool(d):
    """左座的圆木凳（凳面 y 142，坐姿 sit 的大腿压在这里）。"""
    x0, x1, y = STOOL
    rect(d, x0, y, x1, y + 2, WOOD_L[2], outline=INK)
    hl(d, x0 + 1, x1 - 1, y, WOOD_L[3])
    hl(d, x0 + 1, x1 - 1, y + 2, WOOD_L[0])
    for (xa, xb) in ((x0 + 2, x0 + 1), (x1 - 2, x1 - 1)):                          # 两条外撇的腿
        for k, yy in enumerate(range(y + 3, WALK[0] + 1)):
            xx = xa + (xb - xa) * k // max(1, WALK[0] - y - 3)
            px(d, xx, yy, WOOD_L[1])
            px(d, xx + (1 if xa > xb else -1) * 0, yy, WOOD_L[1])
        px(d, xb, WALK[0], INK)
    hl(d, x0 + 3, x1 - 3, y + 6, WOOD_L[1])                                        # 横撑


def draw_shisha(d):
    """水烟壶（烟碗里的炭火在 strip 里画）：绿玻璃壶身、铜杆、接灰盘、烟碗，管子绕在杆上垂下来。"""
    cx, top = SHISHA
    base = FLOOR + 1
    for k in range(10):                                                          # 玻璃壶身（上窄下宽的球）
        y = base - k
        w = int(round(4 * math.sin(math.pi * (k + 1) / 11) + 0.6))
        hl(d, cx - w, cx + w, y, (64, 120, 98))
        px(d, cx - w, y, (110, 170, 140))
        px(d, cx + w, y, (36, 74, 60))
    hl(d, cx - 2, cx + 2, base - 5, (150, 120, 70))                              # 壶里的水线
    rect(d, cx - 1, top + 2, cx + 1, base - 10, BRASS[1])
    vl(d, cx - 1, top + 2, base - 10, BRASS[3])
    hl(d, cx - 4, cx + 4, top + 8, BRASS[2])                                       # 接灰盘
    hl(d, cx - 3, cx + 3, top + 9, BRASS[0])
    rect(d, cx - 2, top, cx + 2, top + 2, (150, 84, 54), outline=INK)              # 烟碗
    for k in range(9):                                                             # 管子：从杆上往左垂成一个弧
        x = cx - 2 - int(4 * math.sin(math.pi * k / 9))
        px(d, x, top + 12 + k, (130, 40, 40) if k % 2 else (100, 30, 30))
    px(d, cx - 2, top + 21, BRASS[2])


def draw_painting(d):
    """“奥西里斯的审判”：纸莎草色的底（四边烧黄）、上下两排象形文字一样的小记号；中间一架天平，
    左盘一颗红心脏、右盘一根白羽毛（天平是平的：心和羽毛一样轻）。"""
    x0, y0, x1, y1 = 108, 62, 140, 86
    ix0, iy0, ix1, iy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 3
    for y in range(iy0, iy1 + 1):
        for x in range(ix0, ix1 + 1):
            e = min(x - ix0, ix1 - x, y - iy0, iy1 - y)
            c = (214, 188, 136) if e > 1 else (192, 160, 108)
            if hash01(x, y, 5) < 0.08:
                c = dk(c, 0.94)
            px(d, x, y, c)
    for yy in (iy0 + 1, iy1 - 2):                                                   # 两排“象形文字”
        x = ix0 + 2
        while x < ix1 - 2:
            k = int(hash01(x, yy) * 4)
            g = ((1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 0), (1, 1, 1, 0))[k]
            for i, v in enumerate(g):
                if v:
                    px(d, x + i % 2, yy + i // 2, (96, 70, 46))
            x += 3
    cx = 124
    rect(d, cx - 3, iy1 - 4, cx + 3, iy1 - 3, (120, 84, 40))                       # 底座
    vl(d, cx, iy0 + 5, iy1 - 4, (120, 84, 40))                                     # 立柱
    px(d, cx, iy0 + 4, (200, 150, 60))
    hl(d, cx - 8, cx + 8, iy0 + 6, (120, 84, 40))                                  # 横梁
    for sx in (cx - 8, cx + 8):
        vl(d, sx - 1, iy0 + 7, iy0 + 10, (150, 120, 80))
        vl(d, sx + 1, iy0 + 7, iy0 + 10, (150, 120, 80))
        hl(d, sx - 3, sx + 3, iy0 + 11, (150, 104, 44))                            # 秤盘
        hl(d, sx - 2, sx + 2, iy0 + 12, (120, 84, 40))
    hx = cx - 8                                                                     # 左盘：心脏
    rect(d, hx - 1, iy0 + 8, hx + 1, iy0 + 10, (176, 36, 40))
    px(d, hx - 1, iy0 + 8, (220, 90, 80))
    fx = cx + 8                                                                     # 右盘：羽毛（弯的白羽）
    for (u, v) in ((0, 10), (0, 9), (1, 8), (1, 7), (2, 6)):
        px(d, fx + u - 1, iy0 + v, (246, 242, 230))
    px(d, fx + 1, iy0 + 9, (210, 206, 196))
    P.gilt_frame(d, x0, y0, x1, y1)


def draw_clock_photo(d):
    """挂钟（木框、奶白钟面、四点四十的样子）+ 一张金字塔的旧照片（深木框、棕褐色调）。"""
    cx, cy = CLOCK
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=P.C(WOOD_L[1]), outline=P.C(INK))
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=P.C((236, 226, 200)))
    for (u, v) in ((0, -4), (4, 0), (0, 4), (-4, 0)):
        px(d, cx + u, cy + v, (90, 70, 60))
    for k in range(1, 4):                                                            # 时针（指 4 多一点）
        a = math.radians(-90 + 145)
        px(d, cx + int(round(k * 0.9 * math.cos(a))), cy + int(round(k * 0.9 * math.sin(a))), (40, 30, 30))
    for k in range(1, 5):                                                            # 分针（指 8）
        a = math.radians(-90 + 240)
        px(d, cx + int(round(k * math.cos(a))), cy + int(round(k * math.sin(a))), (40, 30, 30))
    px(d, cx, cy, (160, 40, 30))
    px(d, cx - 3, cy - 4, (252, 248, 236))
    x0, y0, x1, y1 = 186, 72, 210, 92
    rect(d, x0, y0, x1, y1, (66, 42, 30), outline=INK)
    hl(d, x0 + 1, x1 - 1, y0 + 1, (110, 74, 50))
    for y in range(y0 + 3, y1 - 2):
        u = (y - y0 - 3) / (y1 - y0 - 5)
        hl(d, x0 + 3, x1 - 3, y, mix((226, 206, 170), (196, 168, 128), u))
    for (bx, by, s) in ((193, 87, 6), (202, 87, 4)):                                # 两座金字塔
        for k in range(s):
            hl(d, bx - k, bx + k, by - s + k + 1, (150, 118, 82) if k < s - 1 else (130, 100, 70))
            px(d, bx + k, by - s + k + 1, (120, 92, 64))
    hl(d, x0 + 3, x1 - 3, 88, (176, 148, 108))


def draw_chair(d):
    """达比的高背扶手椅：红丝绒、拉扣（菱形排开的暗点 + 亮点）、铜钉边、两只翼、短木腿。
    达比的 sit 帧（28×25，脚在 seat_right）从 y 125 往下把椅子正面挡住，露出来的是椅背顶 + 两侧的翼。"""
    x0, x1 = CHAIR
    top = 116
    cx = (x0 + x1) // 2
    rect(d, x0 + 2, top + 4, x1 - 2, 142, VELVET[2])
    d.pieslice((x0 + 2, top, x1 - 2, top + 9), 180, 360, fill=P.C(VELVET[2]))
    for (u, v) in disc_edge(x0 + 2, top, x1 - 2, top + 9):
        px(d, u, v, VELVET[3])
    vl(d, x0 + 2, top + 5, 142, VELVET[3])
    vl(d, x1 - 2, top + 5, 142, VELVET[1])
    for r in range(4):                                                               # 拉扣
        for c in range(4):
            bx = x0 + 6 + c * 5 + (2 if r % 2 else 0)
            by = top + 7 + r * 5
            if bx < x1 - 4:
                px(d, bx, by, VELVET[0])
                px(d, bx - 1, by - 1, VELVET[3])
    for y in (top + 14, top + 26):                                                   # 两只翼（往外鼓 2 px）
        rect(d, x0, y, x0 + 2, y + 10, VELVET[1])
        rect(d, x1 - 2, y, x1, y + 10, VELVET[1])
        vl(d, x0, y, y + 10, VELVET[2])
    rect(d, x0, 136, x1, 143, VELVET[1])                                               # 座面前沿
    hl(d, x0, x1, 136, VELVET[3])
    for x in range(x0 + 1, x1, 3):                                                     # 铜钉边
        px(d, x, 143, BRASS[2])
    for x in (x0 + 2, x1 - 3):
        rect(d, x, 144, x + 1, WALK[0], WOOD_L[1])
        px(d, x, WALK[0], INK)
    d2 = d
    d2.line((x0 + 2, top + 4, x0 + 2, 142), fill=P.C(INK))
    d2.line((x1 - 2, top + 4, x1 - 2, 142), fill=P.C(INK))
    d2.arc((x0 + 2, top, x1 - 2, top + 9), 180, 360, fill=P.C(INK))
    px(d, cx, top - 1, BRASS[2])                                                       # 椅背顶上一颗铜扣


def disc_edge(x0, y0, x1, y1):
    """椭圆上半圈往里一格的点（椅背顶的亮边）。"""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2 - 1, (y1 - y0) / 2 - 1
    out = []
    for k in range(0, 181, 4):
        a = math.radians(180 + k)
        out.append((int(round(cx + rx * math.cos(a))), int(round(cy + ry * math.sin(a)))))
    return out


def draw_bar(d):
    """吧台：后墙一面镜子 + 两层酒架、上面一块绿底金字的招牌；台面上收银机 / 烟灰缸 / 咖啡壶；正面竖木板 + 黄铜踩脚杆。"""
    x0 = BAR_X0
    # 招牌（绿底、金色的假阿拉伯字：一条起伏的笔画 + 几个点）
    rect(d, 268, 44, 316, 54, (34, 82, 62), outline=INK)
    hl(d, 269, 315, 45, (60, 120, 92))
    pts = []
    for x in range(272, 313):
        y = 50 + int(round(1.6 * math.sin(x * 0.55) + (1 if x % 9 < 3 else 0)))
        pts.append((x, y))
    for (x, y) in pts:
        if hash01(x, 11) < 0.82:
            px(d, x, y, BRASS[3])
    for x in (276, 285, 293, 303, 309):
        px(d, x, 47, BRASS[3])
    vl(d, 266, 50, 58, (50, 40, 36))
    # 镜子 + 酒架
    rect(d, 264, 58, PW - 1, 100, (64, 44, 32), outline=INK)
    rect(d, 267, 60, PW - 1, 98, (132, 140, 142))
    for k in range(4):                                                                  # 镜面上斜的反光
        for u in range(10):
            xx, yy = 272 + k * 12 + u, 98 - u * 4 - 2
            if 60 <= yy <= 98 and xx < PW:
                px(d, xx, yy, (160, 168, 168))
    for y in (72, 88):
        rect(d, 263, y, PW - 1, y + 2, WOOD_L[2], outline=INK)
        hl(d, 264, PW - 1, y, WOOD_L[3])
        hl(d, 264, PW - 1, y + 3, dk((132, 140, 142), 0.7))
    cols = [(54, 110, 60), (150, 92, 36), (200, 196, 180), (130, 34, 40), (60, 80, 140), (196, 150, 60),
            (90, 130, 70), (170, 70, 40)]
    x = 266
    i = 0
    while x < PW - 4:
        P.bottle(d, x, 71, i % 3, cols[i % len(cols)])
        x += 4 + (1 if hash01(i, 4) < 0.5 else 0)
        i += 1
    x = 266
    i = 3
    while x < PW - 4:
        if i % 4 == 1:
            P.glass_cup(d, x, 87)
            x += 4
        else:
            P.bottle(d, x, 87, (i + 1) % 3, cols[(i * 3) % len(cols)])
            x += 5
        i += 1
    # 台面上：收银机 / 烟灰缸 / 咖啡壶（壶的热气、烟灰缸的烟在 strip）
    rect(d, 266, 120, 280, BAR_TOP - 1, (110, 104, 92), outline=INK)                   # 收银机
    rect(d, 267, 115, 276, 119, (90, 84, 76), outline=INK)
    rect(d, 268, 116, 275, 117, (220, 200, 140))                                         # 弹出来的价钱牌
    for yy in range(122, BAR_TOP - 2, 2):
        for xx in range(268, 279, 2):
            px(d, xx, yy, (200, 190, 170))
    hl(d, 267, 279, 121, (150, 144, 130))
    rect(d, 285, ASH[1] - 1, 291, ASH[1] + 1, (120, 120, 126), outline=INK)            # 烟灰缸 + 一支烟
    hl(d, 287, 292, ASH[1] - 2, (236, 230, 220))
    px(d, 292, ASH[1] - 2, (220, 90, 50))
    ux0, ux1 = URN                                                                       # 黄铜咖啡壶
    rect(d, ux0 + 2, 115, ux1 - 2, BAR_TOP - 4, BRASS[2], outline=INK)
    d.pieslice((ux0 + 2, 110, ux1 - 2, 120), 180, 360, fill=P.C(BRASS[2]), outline=P.C(INK))
    rect(d, (ux0 + ux1) // 2 - 1, 107, (ux0 + ux1) // 2 + 1, 110, BRASS[1], outline=INK)
    vl(d, ux0 + 3, 115, BAR_TOP - 5, BRASS[3])
    vl(d, ux1 - 3, 115, BAR_TOP - 5, BRASS[0])
    rect(d, ux0, BAR_TOP - 4, ux1, BAR_TOP - 1, BRASS[1], outline=INK)                   # 底座
    rect(d, ux0 - 3, 124, ux0 + 1, 125, BRASS[1])                                        # 龙头
    px(d, ux0 - 3, 126, BRASS[0])
    for xx in (313, 317):                                                                 # 两只倒扣的小杯
        rect(d, xx, BAR_TOP - 3, xx + 2, BAR_TOP - 1, (232, 226, 210), outline=(110, 100, 90))
    # 台面 + 正面
    rect(d, x0, BAR_TOP, PW - 1, BAR_TOP + 3, WOOD_L[2], outline=INK)
    hl(d, x0 + 1, PW - 1, BAR_TOP, WOOD_L[3])
    P.wood_boards_v(d, x0 + 2, BAR_TOP + 4, PW - 1, SKIRT[1] + 1, WOOD_L, seed=19, bw=8, ink=INK)
    vl(d, x0 + 1, BAR_TOP + 4, SKIRT[1] + 1, WOOD_L[0])
    vl(d, x0, BAR_TOP + 4, SKIRT[1] + 1, INK)
    hl(d, x0 + 2, PW - 1, BAR_TOP + 4, WOOD_L[0])                                         # 台面压出来的影
    for x in (x0 + 8, x0 + 34, x0 + 58):                                                   # 踩脚杆的支架
        vl(d, x, 141, 142, BRASS[0])
    hl(d, x0 + 3, PW - 1, 142, BRASS[2])
    hl(d, x0 + 3, PW - 1, 143, BRASS[0])
    hl(d, x0, PW - 1, SKIRT[1] + 2, INK)


def draw_basket(d):
    """猫窝：藤编篮子（侧面一条条编织纹）+ 格子布垫。8 px 高（y 158–165），猫是剧情摆的。"""
    cx, cy = 36, 164
    x0, x1 = cx - 9, cx + 9
    rect(d, x0 + 1, cy - 5, x1 - 1, cy, (176, 128, 70))
    d.ellipse((x0, cy - 7, x1, cy - 3), fill=P.C((150, 104, 56)), outline=P.C((96, 64, 36)))
    for x in range(x0 + 2, x1 - 1, 2):                                                    # 编织纹
        vl(d, x, cy - 4, cy, (150, 104, 56))
    for x in range(x0 + 3, x1 - 1, 4):
        px(d, x, cy - 2, (206, 160, 96))
    hl(d, x0 + 2, x1 - 2, cy + 1, (96, 64, 36))
    for x in range(x0 + 3, x1 - 2):                                                        # 格子布垫
        px(d, x, cy - 6, (196, 60, 56) if (x // 2) % 2 else (232, 220, 196))
    px(d, x0 + 1, cy - 5, (96, 64, 36))
    px(d, x1 - 1, cy - 5, (96, 64, 36))


def contact_shadows(im):
    """家具落在地上的影（光主要从上面来）：牌桌底下一圈淡影（不碰 meat 那一排）、凳子 / 椅子 / 边桌 / 水烟壶 / 吧台脚下一窄条。"""
    a = np.array(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:PW]
    m = (((xx - 160) / 62.0) ** 2 + ((yy - 149) / 4.0) ** 2) <= 1.0
    m2 = (((xx - 160) / 22.0) ** 2 + ((yy - 150) / 2.6) ** 2) <= 1.0
    bay = P.bayer(PW, H)
    a[m & (bay < 0.6), :3] *= 0.86
    a[m2, :3] *= 0.82
    im2 = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    for (x0, x1, y) in ((STOOL[0], STOOL[1], WALK[0] + 1), (CHAIR[0], CHAIR[1], WALK[0] + 1), (46, 73, FLOOR),
                        (90, 101, FLOOR + 1), (BAR_X0, PW - 1, FLOOR), (0, 26, FLOOR)):
        P.mul_box(im2, (x0, y, x1, y), (0.8, 0.8, 0.84))
        P.mul_box(im2, (x0 + 1, y + 1, x1 + 1, y + 1), (0.9, 0.9, 0.93))
    return im2


# ============================================================ 打光
def in_beam(x, y):
    return bool(P.poly_mask((PW, H), BEAM)[y, x]) if 0 <= x < PW and 0 <= y < H else False


@lru_cache(maxsize=1)
def beam_mask():
    return P.poly_mask((PW, H), BEAM)


@lru_cache(maxsize=1)
def light_mult():
    """环境光（偏冷、上暗下亮、左右两头更暗）+ 吊灯 / 拱窗 / 吧台三处暖光；日光光柱在地上 / 护墙板上亮一截（边上按 Bayer 抖）。"""
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    amb = 0.56 + 0.17 * np.clip((yy - 96) / 60.0, 0, 1) - 0.06 * np.clip((24 - yy) / 24.0, 0, 1)
    amb -= 0.05 * np.clip(np.abs(xx - 160) / 160.0, 0, 1) ** 2
    lights = [dict(x=LAMP_X, y=96, r=120, k=0.62, p=1.6, sy=1.25, col=(1.16, 0.99, 0.74)),
              dict(x=60, y=76, r=74, k=0.46, p=1.4, col=(1.10, 1.04, 0.92)),
              dict(x=292, y=86, r=62, k=0.36, p=1.4, col=(1.14, 0.97, 0.74)),
              dict(x=14, y=112, r=26, k=0.18, p=1.2, col=(1.08, 1.02, 0.9))]
    m = P.light_map(PW, H, amb, lights, n=10)
    bm = beam_mask()
    bay = P.bayer(PW, H)
    edge = np.zeros_like(bm)
    edge[:, 1:] |= bm[:, 1:] != bm[:, :-1]
    inner = bm & ~(edge & (bay < 0.5))
    m[inner] *= np.array((1.13, 1.09, 1.0), np.float32)
    return m


def albedo():
    im = wall_base()
    d = ImageDraw.Draw(im)
    draw_door(d)
    draw_menu(d)
    draw_window(d)
    draw_side_table(d)
    draw_painting(d)
    draw_clock_photo(d)
    draw_chair(d)
    draw_bar(d)
    draw_stool(d)
    draw_shisha(d)
    draw_basket(d)
    return contact_shadows(im)


@lru_cache(maxsize=1)
def floor_only():
    """只有墙 + 地（不画家具）的打好光的图：自检“meat 三个点附近是干净地砖”用。"""
    return P.apply_light(contact_shadows(wall_base()), light_mult())


@lru_cache(maxsize=1)
def near_img():
    im = P.apply_light(albedo(), light_mult())
    window_view(im)
    d = ImageDraw.Draw(im)
    door_glass(d)
    P.glow(im, LAMP_X, SHADE[1] + 2, 34, 22, (255, 214, 150), 34, rings=3)       # 吊灯下面一团暖光
    P.glow(im, 292, 66, 26, 14, (255, 220, 160), 22, rings=2)                       # 吧台镜子上的灯光
    return P.opaque(im)


# ============================================================ 前景牌桌
@lru_cache(maxsize=1)
def table_img():
    """绿呢牌桌（前景）：木框（上沿一条亮边、正面一道厚边）、绿呢桌面（吊灯照着的中间一团亮、四周暗）、
    中间一根车木立柱 + 十字脚。打光照底图同一张光图；只有 0 / 255 透明度。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = RIM
    tx0, ty0, tx1, ty1 = TABLE
    # 立柱 + 十字脚
    rect(d, PED[0], ty1 + 4, PED[1], 147, WOOD_L[1])
    vl(d, PED[0] + 1, ty1 + 4, 147, WOOD_L[3])
    vl(d, PED[1] - 1, ty1 + 4, 147, WOOD_L[0])
    for yy in (140, 144):
        hl(d, PED[0] - 1, PED[1] + 1, yy, WOOD_L[2])
    d.polygon([(136, 151), (PED[0], 146), (PED[1], 146), (184, 151)], fill=P.C(WOOD_L[1]))
    hl(d, 137, 183, 151, WOOD_L[0])
    hl(d, PED[0], PED[1], 146, WOOD_L[3])
    # 木框：一圈圆角 + 正面厚边
    d.rounded_rectangle((x0, y0, x1, y1), radius=6, fill=P.C(WOOD_L[2]))
    d.rounded_rectangle((x0, ty1 - 1, x1, y1), radius=3, fill=P.C(WOOD_L[1]))
    hl(d, x0 + 4, x1 - 4, ty1 + 1, WOOD_L[3])
    hl(d, x0 + 3, x1 - 3, y1 - 1, WOOD_L[0])
    for x in range(x0 + 6, x1 - 5, 14):                                               # 正面厚边上的木纹接缝
        vl(d, x, ty1 + 2, y1 - 2, WOOD_L[0])
    hl(d, x0 + 5, x1 - 5, y0, WOOD_L[3])
    # 绿呢：中间亮、四周暗（一圈一圈的椭圆）
    d.rounded_rectangle((tx0, ty0, tx1, ty1), radius=5, fill=P.C(FELT[1]))
    d.ellipse((tx0 + 6, ty0 + 1, tx1 - 6, ty1 - 1), fill=P.C(FELT[2]))
    d.ellipse((tx0 + 24, ty0 + 2, tx1 - 24, ty1 - 2), fill=P.C(FELT[3]))
    d.ellipse((tx0 + 40, ty0 + 3, tx1 - 40, ty1 - 3), fill=P.C(FELT[4]))
    hl(d, tx0 + 4, tx1 - 4, ty0, FELT[0])                                              # 后沿的阴影
    a = np.array(im)
    bay = P.bayer(PW, H)
    felt = (a[..., 3] > 0) & (np.abs(a[..., :3].astype(int) - np.array(FELT[2])).sum(-1) < 4)
    a[felt & (bay < 0.18), :3] = FELT[1]                                               # 绒面的毛
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 桌边一只铜烟灰缸 + 一盒火柴（只在桌角，牌位 / 筹码是剧情摆的，中间留空）
    rect(d, 204, 121, 209, 123, BRASS[1], outline=INK)
    hl(d, 205, 208, 121, BRASS[3])
    rect(d, 110, 126, 114, 128, (170, 40, 40), outline=INK)
    px(d, 111, 126, (240, 210, 120))
    im = P.outline(im, INK, sides=('l', 't', 'r', 'b'))
    m = light_mult().copy()
    m = np.maximum(m, 0.78)                                                             # 桌子在灯底下：不跟墙一起压那么暗
    return P.opaque(P.apply_light(im, m))


@lru_cache(maxsize=1)
def bar_front_img():
    """吧台台面 + 正面那一截（和底图一模一样），key bar 打开时画在人物前面。"""
    im = P.new(PW, H)
    paste(im, near_img().crop((BAR_X0, BAR_TOP, PW, SKIRT[1] + 3)), BAR_X0, BAR_TOP)
    return im


# ============================================================ 会动的（strip）
def curtain_frame(t):
    """拱窗两边的红窗帘：杆子上收成褶，中间用绑带束一下，下摆随风晃 ±1 px。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    rect(d, 36, 42, 84, 43, BRASS[1])
    hl(d, 36, 84, 42, BRASS[3])
    for (cx0, side) in ((38, -1), (76, 1)):
        for y in range(44, 101):
            k = (y - 44) / 56.0
            # 下摆的波从绑带往下传：相位随帧走一圈（8 帧），越往下摆得越开（±1.4 px），每一帧都不一样
            off = int(round(1.4 * math.sin(2 * math.pi * (f / 8.0) - (y - 86) * 0.35 + (0 if side < 0 else 1.7))
                            * (y - 86) / 14.0)) if y > 86 else 0
            pinch = 2 if 82 <= y <= 86 else 0
            x0 = cx0 + (pinch if side < 0 else 0) + off
            x1 = cx0 + 7 - (pinch if side > 0 else 0) + off
            for x in range(x0, x1 + 1):
                fold = (x - x0) % 3
                c = (160, 44, 48) if fold == 0 else ((128, 32, 38) if fold == 1 else (104, 26, 32))
                if side < 0 and x == x1:
                    c = (196, 84, 74)                                                   # 朝窗那边被日光照亮
                if side > 0 and x == x0:
                    c = (196, 84, 74)
                px(d, x, y, c)
            px(d, x0 - 1 if side < 0 else x1 + 1, y, (60, 20, 24))
        by = 84
        hl(d, cx0, cx0 + 7, by, (220, 180, 90))                                        # 绑带
    return im


def motes_frame(t):
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    bm = beam_mask()
    P.motes(d, (52, 98, 118, 156), t, 2.0, 10, (246, 226, 184), seed=5,
            ok=lambda x, y: 0 <= x < PW and 0 <= y < H and bool(bm[y, x]))
    return im


def shisha_frame(t):
    """水烟壶炭火一明一暗 + 一缕细烟（2 s 一圈）。"""
    a = np.zeros((H, PW, 4), np.uint8)
    cx, top = SHISHA
    P.wisp(a, cx, top - 2, t, 2.0, 18, 3, (214, 206, 196), alpha=120, seed=2)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    k = (1.0, 0.8, 0.6, 0.75, 0.95, 0.7, 0.55, 0.85)[fno(t)]
    px(d, cx - 1, top - 1, mix((90, 40, 30), (255, 150, 60), k))
    px(d, cx, top - 1, mix((90, 40, 30), (255, 210, 120), k))
    px(d, cx + 1, top - 1, mix((90, 40, 30), (255, 120, 50), k * 0.8))
    return im


def steam_frame(t):
    a = np.zeros((H, PW, 4), np.uint8)
    cx = (URN[0] + URN[1]) // 2
    P.wisp(a, cx, 105, t, 2.0, 22, -2, (236, 232, 226), alpha=110, seed=4, width=2)
    return Image.fromarray(a, 'RGBA')


def smoke_frame(t):
    a = np.zeros((H, PW, 4), np.uint8)
    P.wisp(a, ASH[0] + 4, ASH[1] - 3, t, 2.0, 26, 4, (200, 196, 190), alpha=130, seed=9)
    return Image.fromarray(a, 'RGBA')


def fan_frame(t):
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    vl(d, FAN[0], 0, FAN[1] - 3, (60, 46, 40))
    P.fan_frame(d, FAN[0], FAN[1], fno(t, 8, 8.0), R=18, pal=((70, 52, 42), (132, 98, 70), (176, 136, 96)))
    return im


def lamp_frame(t):
    """吊灯：灯绳从天花板垂下，灯罩跟着吊扇的风晃 ±1 px（8 帧一个来回）；绿玻璃灯罩 + 铜边 + 灯泡。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    dx = (0, 0, 1, 1, 0, 0, -1, -1)[f]
    kb = (1.0, 0.86, 0.95, 0.8, 1.0, 0.9, 0.82, 0.94)[f]          # 灯丝亮度：每帧都不一样（风吹灯晃 + 电压不稳）
    top, bot = SHADE
    d.line((LAMP_X, CEIL + 1, LAMP_X + dx, top - 2), fill=P.C((40, 30, 28)))
    rect(d, LAMP_X + dx - 1, top - 2, LAMP_X + dx + 1, top - 1, BRASS[1])
    cx = LAMP_X + dx
    for k, y in enumerate(range(top, bot + 1)):
        hw = 3 + k * 7 // (bot - top)
        hl(d, cx - hw, cx + hw, y, (40, 112, 72))
        px(d, cx - hw, y, (120, 196, 136))
        px(d, cx - hw + 1, y, (70, 150, 100))
        px(d, cx + hw, y, (24, 70, 46))
    hl(d, cx - 10, cx + 10, bot + 1, BRASS[2])
    hl(d, cx - 3, cx + 3, bot + 2, mix((200, 160, 100), (255, 240, 190), kb))
    px(d, cx - 4, bot + 2, (250, 200, 120))
    px(d, cx + 4, bot + 2, (250, 200, 120))
    return im


# ============================================================ 组装
@lru_cache(maxsize=1)
def specs():
    S = [dict(t='pano', name='near', img=near_img(), k=1.0),
         P.strip('curtain', curtain_frame, (30, 38, 92, 104)),
         P.strip('motes', motes_frame, (40, 90, 136, 164)),
         P.strip('shisha', shisha_frame, (84, 90, 108, 120)),
         P.strip('steam', steam_frame, (290, 70, 320, 106)),
         P.strip('smoke', smoke_frame, (280, 92, 308, 130)),
         P.strip('fan', fan_frame, (212, 0, 260, 24), n=8, fps=8.0),
         P.strip('lamp', lamp_frame, (146, CEIL, 176, SHADE[1] + 4)),
         dict(t='pano', name='table', img=table_img(), k=1.0, fg=True),
         dict(t='pano', name='bar_front', img=bar_front_img(), k=1.0, fg=True, key='bar')]
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
    tab = table_img()
    m0, s0 = P.walk_stats(near, WALK)
    cfg = dict(
        name='咖啡馆', pw=PW, walk=WALK, states=[{}, {'bar': True}],
        opaque=[('近景整张不透明（屋里没有天）', near, (0, 0, PW, H))],
        binary=[('近景只有 0 / 255 两种透明度', near), ('前景牌桌只有 0 / 255', tab), ('吧台前沿（key bar）只有 0 / 255', bar_front_img())],
        stand=['seat_left', 'seat_right', 'cat', 'door', 'meat', 'dealer_talk'],
        inside=['table', 'cafe_table', 'dealer', 'bar', 'window', 'chips', 'painting', 'lamp', 'fan', 'clock'],
        notes=['可走带亮度（y %d–%d）：均值 %.0f 标准差 %.1f' % (WALK[0], WALK[1], m0, s0)],
    )
    P.std_checks(ex, BJ, st, S, cfg)
    ta = np.array(tab)[..., 3]
    x0, y0, x1, y1 = TABLE
    ex.checked('前景牌桌盖满桌面框 table %s（没盖到的像素）' % (TABLE,), int((ta[y0:y1 + 1, x0:x1 + 1] != 255).sum()))
    # 发牌小哥：头 + 肩（脚点 y−26 … 桌面后沿上面）不被前景挡，下半身（桌面后沿 … 脚点）被挡
    dx, dy = ANCHORS['dealer']
    top = int(np.argmax(ta[:, dx] == 255))                       # 前景牌桌在小哥这一列最上面的一行（墨线）
    head = ta[dy - 26:top, dx - 6:dx + 7]
    body = ta[top:dy, dx - 6:dx + 7]
    ex.checked('发牌小哥 dealer：头肩（y %d–%d，%d 行）露在牌桌后沿上面（被挡的像素）' % (dy - 26, top - 1, top - dy + 26),
               int((head != 0).sum()) + max(0, 12 - (top - dy + 26)))
    ex.checked('发牌小哥 dealer：下半身（y %d–%d）被前景牌桌挡住（漏出来的像素）' % (top, dy - 1), int((body != 255).sum()))
    # 三块肉：附近（±6 × ±3）是干净地砖（和“只有墙 + 地”的图一样）、前景也不挡
    fo = np.array(floor_only())[..., :3].astype(int)
    na = np.array(near)[..., :3].astype(int)
    bad = 0
    for (mx, my) in MEAT:
        bad += int((np.abs(na[my - 3:my + 4, mx - 6:mx + 7] - fo[my - 3:my + 4, mx - 6:mx + 7]).max(-1) > 0).sum())
        bad += int((ta[my - 3:my + 4, mx - 6:mx + 7] != 0).sum())
    ex.checked('meat 三个点附近 13×7 是干净地砖（有东西的像素）', bad)
    # 两个座位：凳面 / 椅座前沿的高度和 sit 帧的大腿对得上（凳面 y 142；椅座前沿 y 136–143，达比的帧把它挡住）
    ex.checked('左座凳面在脚点上方 8 px（sit 帧的大腿 y 141–144）', abs((ANCHORS['seat_left'][1] - STOOL[2]) - 8))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch10', 'after')
    os.makedirs(od, exist_ok=True)
    P.direct(specs(), 0, 0.5, {'bar': True}).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
        os.path.join(od, 'cafe_interior_solo.png'))
    print('ok')
