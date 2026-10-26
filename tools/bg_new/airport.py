# -*- coding: utf-8 -*-
r"""airport —— 终章：开罗机场的候机厅（地图 airport_fin），第 50 天早上三人告别（承太郎 / 乔瑟夫 → 东京，波鲁纳雷夫 → 巴黎）。
2026-10-19 第三轮背景重画（interiors 组）新画（改前是 later_stages 的占位）。共用零件在 interior_parts.py。

320 单屏，ground 156，可走带 y 150–176（米白水磨石地面，对比压低）；侧视平视，后墙中间一整面大玻璃窗。
早上：太阳刚升起来（窗外的天下面橙、上面淡蓝），日光从大窗斜着照进来，在地上落成几块亮斑；天花板一排日光灯。
竖向：天花板 0–15（吊顶板 + 日光灯管），墙 16–139（米白墙 + 一条浅灰绿的腰带），踢脚 140–145，地面 146–179。
从左到右：
  x 4–44     往巴黎的登机口（anchors.gate_paris = 门前站点 [24,156]）：门洞里是去登机桥的走廊（偏蓝的光）、
             门上的灯箱：GATE 2 + 法国三色旗 + PARIS（不写台词，只是标识）
  x 48–66    一盆棕榈（叶子被空调吹得轻轻晃 strip）
  x 70–118   航班显示牌（anchors.board [96,84] 在牌子上）：黑底黄字的翻牌——DEPARTURES、四行航班（TOKYO / PARIS / ROME /
             LONDON + 时间 + 登机口）；东京那一行的状态栏在翻牌（strip），翻完亮出 BOARD
  x 122–242  大玻璃窗（anchors.window [180,80]）：铝框、竖挺；窗外早上的天、远处的跑道和管制塔（雷达天线在转）、
             一架小飞机在远处的滑行道上转弯（strip）；近处停着一架客机（机头朝左，舱门 = anchors.plane_door [238,112]），
             舱门口靠着一辆登机梯车，地上一辆行李拖车
  x 124–216  窗前两排候机长椅（橙色塑料座椅 + 金属横梁，贴着可走带后沿；anchors.benches 是椅子前面的站点）
  x 246–254  一根方柱 + 墙上的挂钟（秒针 strip）
  x 256–300  往东京的登机口（anchors.gate = 门前站点 [276,156]）：同上，灯箱 GATE 5 + 日本国旗 + TOKYO，
             旁边一块小牌子 BOARDING（绿灯一闪一闪 strip）
  x 302–318  登机口的柜台（检票台）+ 一盆棕榈
地面：水磨石（米白底 + 彩色碎石点 + 大方格的铜嵌条），窗光在地上落成三块斜的亮斑（只亮一档）。

图层（从后往前）：
  near      pano  k 1            整个候机厅（打好光：窗外进来的晨光 + 天花板日光灯的冷白光）
  apron     strip 16 帧 @4 fps   窗外：远处一架小飞机沿滑行道转弯、开走（4 s 一架）+ 管制塔顶的雷达天线在转
  board     strip 8 帧 @4 fps    航班牌东京那一行的状态栏翻牌 → BOARD 一明一暗
  gate_lamp strip 8 帧 @4 fps    东京登机口 BOARDING 小牌子的绿灯一闪一闪
  tube      strip 8 帧 @8 fps    天花板一根日光灯管接触不好（偶尔一闪）
  palm      strip 8 帧 @4 fps    两盆棕榈的叶子轻轻晃
  clock     strip 8 帧 @4 fps    挂钟的秒针
锚点（素材总表定稿的名字一个不少，值照总表）：arrive [40,164]、board [96,84]、benches [[140,162],[200,162]]、window [180,80]、
  plane_door [238,112]、gate [276,156]（东京）、gate_paris [24,156]（巴黎）；
  另外多导出：walk_x [8,312]、clock [250,64]、counter [310,150]（检票台）。
  长椅上不画登机牌：那是纪念品（fin_boarding_pass），拿走以后背景上还留着会穿帮。
key：无。
单独运行：python -B tools/bg_new/airport.py → tools/bg_new/_preview/final/after/airport_solo.png
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
WALK = (150, 176)
CEIL = 15
BAND = (96, 102)              # 墙上的腰带
SKIRT = (140, 145)
FLOOR = 146
WIN = (122, 28, 242, 134)     # 大玻璃窗（玻璃 + 框）
MULL = [152, 182, 212]        # 竖挺
HZ = 96                       # 窗外地平线
BOARD = (70, 68, 118, 102)
GP = (4, 44)                  # 巴黎登机口
GT = (256, 300)               # 东京登机口
DOOR_TOP = 100
PLANE_DOOR = (238, 112)
CLOCK = (250, 64)
TUBES = [34, 92, 150, 208, 266]
FLICK = 3                     # TUBES[3] 接触不好
BENCH_X = [(124, 160), (182, 218)]
PALMS = [(57, FLOOR - 1), (311, FLOOR - 1)]

INK = (40, 42, 48)
WALL = (222, 214, 198)
WALL_D = (206, 198, 182)
WALL_L = (232, 226, 212)
BANDC = (150, 170, 160)
ALU = [(70, 76, 86), (120, 128, 138), (170, 178, 186), (214, 220, 226)]
TERR = (210, 202, 186)        # 水磨石底
SEAT = [(150, 66, 30), (196, 96, 44), (226, 130, 66)]
FLAGBLUE, FLAGRED = (40, 70, 160), (206, 40, 46)

ANCHORS = dict(arrive=[40, 164], board=[96, 84], benches=[[140, 162], [200, 162]], window=[180, 80],
               plane_door=list(PLANE_DOOR), gate=[276, 156], gate_paris=[24, 156],
               walk_x=[8, 312], clock=list(CLOCK), counter=[310, 150])


# ============================================================ 墙 / 地 / 天花板
def terrazzo(d):
    """水磨石地面：米白底、彩色碎石点（稀、淡）、每 40 px 一道铜嵌条（竖条按一点透视往外斜），近处的格子大一点。"""
    for y in range(FLOOR, H):
        s = 1 + (y - FLOOR) / 60.0
        for x in range(PW):
            c = TERR
            h = hash01(x, y, 3)
            if h < 0.05:
                c = (176, 168, 156)
            elif h < 0.08:
                c = (196, 150, 120)
            elif h < 0.1:
                c = (150, 160, 150)
            u = (x - 160) / s / 40.0
            if abs(u - round(u)) * 40 * s < 0.6:
                c = (176, 150, 104)
            px(d, x, y, c)
    for y in (FLOOR + 3, FLOOR + 10, FLOOR + 21):                                      # 横的嵌条（远疏近密的反过来：近处间距大）
        hl(d, 0, PW - 1, y, (184, 160, 116))
    hl(d, 0, PW - 1, FLOOR, (150, 140, 124))


def wall_base():
    im = P.new(PW, H, WALL)
    d = ImageDraw.Draw(im)
    rect(d, 0, 0, PW - 1, CEIL, (226, 226, 222))                                        # 吊顶板
    for x in range(0, PW, 24):
        vl(d, x, 0, CEIL, (196, 196, 194))
    hl(d, 0, PW - 1, 6, (200, 200, 198))
    for tx in TUBES:                                                                     # 日光灯格栅（灯管本身打光后画）
        rect(d, tx - 12, 9, tx + 12, 12, (180, 182, 184), outline=(150, 152, 156))
    hl(d, 0, PW - 1, CEIL, (170, 168, 162))
    hl(d, 0, PW - 1, CEIL + 1, (190, 184, 170))
    for x in range(20, PW, 40):                                                          # 墙面的板缝（干净的现代墙，不做斑驳）
        vl(d, x, CEIL + 2, BAND[0] - 1, WALL_D)
        vl(d, x + 1, CEIL + 2, BAND[0] - 1, WALL_L)
    for x in range(20, PW, 40):
        vl(d, x, BAND[1] + 1, SKIRT[0] - 1, WALL_D)
    rect(d, 0, BAND[0], PW - 1, BAND[1], BANDC)
    hl(d, 0, PW - 1, BAND[0], lt(BANDC, 0.3))
    hl(d, 0, PW - 1, BAND[1], dk(BANDC, 0.8))
    rect(d, 0, SKIRT[0], PW - 1, SKIRT[1], (120, 124, 120))
    hl(d, 0, PW - 1, SKIRT[0], (160, 164, 158))
    terrazzo(d)
    return im


def gate(d, x0, x1, num, city, flag):
    """登机口：门洞（里面是去登机桥的走廊：偏蓝的地、两边的墙往里收）、铝门框、门上的灯箱（GATE n + 国旗 + 城市名）。"""
    top = DOOR_TOP
    rect(d, x0 - 2, top - 2, x1 + 2, SKIRT[1], ALU[1], outline=INK)
    rect(d, x0, top, x1, SKIRT[1], (120, 140, 164))
    cx = (x0 + x1) // 2
    for y in range(top, SKIRT[1] + 1):                                                    # 走廊：透视往里收
        k = (y - top) / (SKIRT[1] - top)
        hw = int(6 + k * ((x1 - x0) // 2 - 6))
        if y > top + 20:
            hl(d, cx - hw, cx + hw, y, mix((150, 166, 186), (176, 186, 198), k))
        px(d, cx - hw, y, (90, 104, 126))
        px(d, cx + hw, y, (90, 104, 126))
    rect(d, cx - 5, top + 6, cx + 5, top + 20, (226, 236, 244))                           # 走廊尽头的亮光（机舱门）
    hl(d, x0, x1, top + 1, (150, 166, 190))
    vl(d, x0 - 1, top - 1, SKIRT[1], ALU[3])
    # 灯箱
    by0, by1 = top - 22, top - 6
    rect(d, x0 - 2, by0, x1 + 2, by1, (34, 38, 48), outline=INK)
    rect(d, x0, by0 + 2, x1, by1 - 2, (40, 46, 60))
    P.text35(d, x0 + 2, by0 + 3, 'GATE ' + num, (250, 214, 90))
    fx0 = x1 - 12
    if flag == 'fr':
        rect(d, fx0, by0 + 3, fx0 + 2, by0 + 7, FLAGBLUE)
        rect(d, fx0 + 3, by0 + 3, fx0 + 5, by0 + 7, (246, 246, 246))
        rect(d, fx0 + 6, by0 + 3, fx0 + 8, by0 + 7, FLAGRED)
    else:
        rect(d, fx0, by0 + 3, fx0 + 8, by0 + 7, (246, 246, 246))
        rect(d, fx0 + 3, by0 + 4, fx0 + 5, by0 + 6, FLAGRED)
        px(d, fx0 + 4, by0 + 3, FLAGRED)
        px(d, fx0 + 4, by0 + 7, FLAGRED)
    tw = P.text35_w(city)
    P.text35(d, (x0 + x1) // 2 - tw // 2, by0 + 9, city, (236, 240, 244))
    vl(d, x0 + 6, by0 - 6, by0, ALU[0])                                                    # 吊杆
    vl(d, x1 - 6, by0 - 6, by0, ALU[0])


def draw_board(d):
    """航班显示牌：黑底、铝边、DEPARTURES 标题、四行航班（城市 + 时间 + 登机口）。东京那一行的状态栏在 strip 里翻。"""
    x0, y0, x1, y1 = BOARD
    rect(d, x0 - 2, y0 - 2, x1 + 2, y1 + 2, ALU[1], outline=INK)
    rect(d, x0, y0, x1, y1, (26, 28, 32))
    hl(d, x0 - 1, x1 + 1, y0 - 1, ALU[3])
    P.text35(d, x0 + 3, y0 + 2, 'DEPARTURES', (230, 232, 236))
    hl(d, x0 + 2, x1 - 2, y0 + 8, (70, 74, 80))
    # 四行：城市（≤ 5 个字母）+ 登机口 + 状态栏（别的航班显示时间；东京那一行的状态栏在 strip 里翻）
    rows = [('TOKYO', '5', ''), ('PARIS', '2', '0945'), ('ROME', '3', '1010'), ('DUBAI', '4', '1040')]
    for i, (city, g, stat) in enumerate(rows):
        y = y0 + 10 + i * 6
        for k in range(11):                                                                  # 翻牌的格子底
            if k != 5:
                rect(d, x0 + 2 + k * 4, y - 1, x0 + 4 + k * 4, y + 5, (40, 42, 48))
        P.text35(d, x0 + 3, y, city, (250, 214, 90))
        P.text35(d, x0 + 24, y, g, (250, 214, 90))
        if stat:
            P.text35(d, x0 + 30, y, stat, (250, 214, 90))
        hl(d, x0 + 2, x1 - 2, y + 5, (34, 36, 40))
    vl(d, (x0 + x1) // 2 - 8, y0 - 12, y0 - 3, ALU[0])                                       # 吊杆
    vl(d, (x0 + x1) // 2 + 8, y0 - 12, y0 - 3, ALU[0])


def draw_window_frame(d):
    """大玻璃窗的铝框 + 竖挺 + 中间一道横挺（窗外的景色打光以后画）；窗台。"""
    x0, y0, x1, y1 = WIN
    rect(d, x0 - 3, y0 - 3, x1 + 3, y1 + 3, ALU[1], outline=INK)
    hl(d, x0 - 2, x1 + 2, y0 - 2, ALU[3])
    rect(d, x0, y0, x1, y1, (150, 170, 190))
    rect(d, x0 - 4, y1 + 3, x1 + 4, y1 + 5, ALU[2], outline=INK)


def window_view(im):
    """窗外：早上的天（下面橙、上面淡蓝）、刚升起来的太阳（左边窗角，一团光）、远处的跑道 + 管制塔（雷达天线在 strip）、
    近处的停机坪（灰、黄色引导线）、停着的客机（机头朝左、蓝色腰线、一排舷窗、舱门 = plane_door，门口一辆登机梯车）、
    一辆行李拖车。自己发光的部分打光以后画；竖挺 / 横挺最后压上去。"""
    x0, y0, x1, y1 = WIN
    lay = P.new(PW, H)
    d = ImageDraw.Draw(lay)
    for y in range(y0, HZ + 1):
        u = (y - y0) / (HZ - y0)
        hl(d, x0, x1, y, mix((168, 200, 226), (252, 206, 150), u ** 1.6))
    P.glow(lay, x0 + 14, HZ - 10, 26, 18, (255, 236, 190), 70, rings=4)                    # 太阳
    d = ImageDraw.Draw(lay)
    d.ellipse((x0 + 9, HZ - 15, x0 + 19, HZ - 5), fill=P.C((255, 246, 214)))
    for (cx, cy, w) in ((x0 + 60, y0 + 12, 22), (x0 + 96, y0 + 22, 16)):                   # 两朵淡淡的云
        hl(d, cx - w // 2, cx + w // 2, cy, (240, 232, 228))
        hl(d, cx - w // 3, cx + w // 3, cy - 1, (248, 242, 238))
    rect(d, x0, HZ - 3, x1, HZ, (204, 176, 150))                                            # 远处的沙地 / 城
    for (bx, bw, bh) in ((x0 + 30, 8, 3), (x0 + 44, 5, 4), (x0 + 74, 10, 2), (x0 + 100, 6, 3)):
        rect(d, bx, HZ - 3 - bh, bx + bw, HZ - 3, (186, 166, 150))
    tx = x0 + 18                                                                             # 管制塔（雷达在 strip）
    rect(d, tx - 2, HZ - 30, tx + 2, HZ, (196, 186, 170))
    vl(d, tx + 2, HZ - 30, HZ, (170, 160, 146))
    rect(d, tx - 5, HZ - 36, tx + 5, HZ - 31, (110, 140, 160), outline=(150, 140, 126))
    hl(d, tx - 5, tx + 5, HZ - 37, (200, 190, 176))
    vl(d, tx, HZ - 41, HZ - 38, (150, 140, 126))
    for y in range(HZ + 1, y1 + 1):                                                          # 停机坪 / 跑道
        u = (y - HZ) / (y1 - HZ)
        hl(d, x0, x1, y, mix((176, 170, 162), (150, 146, 140), u))
    hl(d, x0, x1, HZ + 3, (210, 206, 196))                                                   # 跑道边线
    for x in range(x0, x1, 8):
        hl(d, x, x + 3, HZ + 5, (236, 234, 226))
    d.line((x0, y1 - 2, x0 + 60, y1 - 18), fill=P.C((230, 190, 60)))                          # 黄色引导线
    # 停着的客机（机头朝左；机身 y 100–122；舱门在 plane_door）
    px0, px1, py0, py1 = 150, x1 + 1, 101, 121
    rect(d, px0 + 10, py0, px1, py1, (232, 234, 236))
    d.pieslice((px0, py0, px0 + 22, py1), 90, 270, fill=P.C((232, 234, 236)))              # 圆机头
    hl(d, px0 + 6, px1, py0 + 10, (40, 90, 170))                                              # 蓝色腰线
    hl(d, px0 + 6, px1, py0 + 11, (40, 90, 170))
    hl(d, px0 + 10, px1, py1 - 1, (196, 198, 202))
    hl(d, px0 + 10, px1, py1, (150, 152, 158))
    for k in range(4):                                                                        # 驾驶舱窗
        px(d, px0 + 5 + k, py0 + 6 - (1 if k > 1 else 0), (40, 56, 80))
    for x in range(px0 + 20, px1, 4):                                                        # 舷窗
        if abs(x - PLANE_DOOR[0]) > 4:
            px(d, x, py0 + 6, (60, 80, 110))
    dx, dy = PLANE_DOOR                                                                       # 舱门（开着，里面暗）
    rect(d, dx - 3, dy - 8, dx + 2, dy + 6, (180, 184, 190))
    rect(d, dx - 2, dy - 7, dx + 1, dy + 5, (60, 64, 76))
    px(d, dx - 2, dy - 7, (90, 96, 110))
    for k in range(13):                                                                       # 登机梯车：从舱门斜下到地面
        yy = dy + 6 + k
        xx = dx - 3 - k
        hl(d, xx - 2, xx + 1, yy, (226, 226, 220) if k % 2 else (200, 200, 196))
        px(d, xx + 2, yy, (120, 120, 120))
    rect(d, dx - 24, y1 - 6, dx - 6, y1 - 2, (230, 200, 60), outline=(120, 100, 40))          # 梯车的底盘
    for wx in (dx - 21, dx - 9):
        rect(d, wx - 1, y1 - 2, wx + 1, y1, (40, 40, 44))
    vl(d, dx + 1, dy + 6, y1 - 2, (120, 120, 120))
    for k, (bx, by) in enumerate(((x0 + 8, y1 - 8), (x0 + 16, y1 - 8))):                     # 行李拖车（两节）
        rect(d, bx, by, bx + 6, by + 4, (200, 120, 50), outline=(90, 60, 30))
        rect(d, bx + 1, by - 2, bx + 5, by, (150, 110, 80))
        px(d, bx + 1, by + 5, (40, 40, 44))
        px(d, bx + 5, by + 5, (40, 40, 44))
    im.alpha_composite(lay)
    d2 = ImageDraw.Draw(im)
    window_bars(d2)


def window_bars(d):
    x0, y0, x1, y1 = WIN
    for mx in MULL:
        vl(d, mx, y0, y1, ALU[1])
        vl(d, mx + 1, y0, y1, ALU[0])
    hl(d, x0, x1, 62, ALU[1])
    hl(d, x0, x1, 63, ALU[0])
    for (u, v) in ((x0 + 40, y0 + 4), (x0 + 41, y0 + 3), (x0 + 100, y0 + 40), (x0 + 101, y0 + 39)):  # 玻璃反光
        px(d, u, v, (252, 252, 250))


def is_bar(x, y):
    x0, y0, x1, y1 = WIN
    return x in MULL or (x - 1) in MULL or y in (62, 63) or not (x0 <= x <= x1 and y0 <= y <= y1)


def draw_benches(d):
    """候机长椅：一排四个橙色塑料座（靠背 + 座面）装在一根金属横梁上，两头两条腿；贴着可走带后沿（脚在 y 149）。"""
    for (x0, x1) in BENCH_X:
        hl(d, x0, x1, 144, ALU[1])                                                           # 横梁
        hl(d, x0, x1, 145, ALU[0])
        for lx in (x0 + 3, x1 - 3):
            vl(d, lx, 145, 149, ALU[1])
            hl(d, lx - 2, lx + 2, 149, ALU[0])
        n = 4
        w = (x1 - x0 + 1) // n
        for i in range(n):
            sx0 = x0 + i * w + 1
            sx1 = sx0 + w - 3
            rect(d, sx0, 131, sx1, 140, SEAT[1], outline=INK)                               # 靠背
            hl(d, sx0 + 1, sx1 - 1, 132, SEAT[2])
            vl(d, sx1 - 1, 133, 139, SEAT[0])
            rect(d, sx0 - 1, 140, sx1 + 1, 143, SEAT[1], outline=INK)                         # 座面
            hl(d, sx0, sx1, 140, SEAT[2])


def draw_pillar_clock(d):
    """一根方柱（混凝土，左亮右暗）+ 柱子上的挂钟（钟面打光以后不用再画，秒针在 strip）。"""
    x0, x1 = 244, 254
    rect(d, x0, CEIL + 1, x1, SKIRT[1], (200, 196, 186))
    vl(d, x0, CEIL + 1, SKIRT[1], (226, 222, 212))
    vl(d, x1, CEIL + 1, SKIRT[1], (160, 156, 148))
    vl(d, x1 + 1, CEIL + 1, SKIRT[1], (190, 182, 166))
    cx, cy = CLOCK
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=P.C((246, 246, 242)), outline=P.C(INK))
    for k in range(12):
        a = math.radians(k * 30)
        px(d, cx + int(round(5 * math.cos(a))), cy + int(round(5 * math.sin(a))), (120, 120, 124))
    for k in range(1, 4):                                                                     # 时针（7 点半）
        a = math.radians(-90 + 225)
        px(d, cx + int(round(k * math.cos(a))), cy + int(round(k * math.sin(a))), (30, 30, 34))
    for k in range(1, 5):                                                                     # 分针（30 分）
        px(d, cx, cy + k, (30, 30, 34))
    px(d, cx, cy, (200, 40, 40))


def draw_counter(d):
    """东京登机口旁的检票台：浅木台面 + 深色正面、上面一台小电脑终端（绿屏）、一个小牌子位置（灯在 strip）。"""
    x0, x1 = 302, 319
    rect(d, x0, 128, x1, SKIRT[1] + 2, (90, 96, 110), outline=INK)
    rect(d, x0 - 1, 126, x1, 128, (200, 170, 120), outline=INK)
    hl(d, x0, x1, 126, (226, 200, 150))
    rect(d, x0 + 5, 118, x0 + 13, 125, (210, 206, 196), outline=INK)
    rect(d, x0 + 6, 119, x0 + 12, 123, (40, 90, 60))
    hl(d, x0 + 7, x0 + 10, 120, (120, 230, 140))
    hl(d, x0 + 7, x0 + 9, 122, (120, 230, 140))
    # BOARDING 小牌子（东京登机口左边的墙上）
    rect(d, 258, 104, 272, 110, (34, 38, 48), outline=INK)


def palm(d, x, base, sway, seed, pot=True, leaves=True):
    """盆栽棕榈：方陶盆 + 一束往四周弯的长叶（sway = 叶尖左右偏）。底图只画盆和干（pot），叶子在 strip 里每帧画（leaves），
    免得底图的叶子在 strip 底下露出“重影”。"""
    if pot:
        rect(d, x - 4, base - 7, x + 4, base, (170, 104, 66), outline=INK)
        hl(d, x - 3, x + 3, base - 6, (206, 140, 96))
        hl(d, x - 3, x + 3, base - 7, (90, 60, 40))
        vl(d, x, base - 16, base - 8, (110, 80, 50))
    if not leaves:
        return
    for k, (ang, L) in enumerate(((-150, 10), (-120, 9), (-95, 11), (-70, 9), (-35, 10), (-165, 8), (-15, 8))):
        a = math.radians(ang)
        for q in range(L):
            u = q / L
            xx = x + q * math.cos(a) + (sway * u * u if q > L // 2 else 0)
            yy = base - 16 + q * math.sin(a) + u * u * 6
            px(d, int(round(xx)), int(round(yy)), (60, 120, 60) if q % 3 else (90, 150, 70))
            if q > 1 and q % 2 == 0:
                px(d, int(round(xx)), int(round(yy)) + 1, (44, 96, 50))


def contact_shadows(im):
    for (x0, x1, y) in ((BENCH_X[0][0], BENCH_X[0][1], 150), (BENCH_X[1][0], BENCH_X[1][1], 150), (302, 319, FLOOR + 2),
                        (52, 62, FLOOR), (306, 316, FLOOR), (244, 256, FLOOR)):
        P.mul_box(im, (x0, y, x1, y), (0.84, 0.84, 0.88))
        P.mul_box(im, (x0 + 1, y + 1, x1 + 1, y + 1), (0.92, 0.92, 0.95))


# ============================================================ 打光
def sun_polys():
    """窗光落在地上的三块亮斑（窗子的三格，往右下斜）。"""
    out = []
    for (a, b) in ((124, 150), (154, 180), (184, 210), (214, 240)):
        out.append([(a + 18, FLOOR + 2), (b + 18, FLOOR + 2), (b + 44, H - 1), (a + 44, H - 1)])
    return out


@lru_cache(maxsize=1)
def sun_mask():
    m = np.zeros((H, PW), bool)
    for poly in sun_polys():
        m |= P.poly_mask((PW, H), poly)
    return m


@lru_cache(maxsize=1)
def light_mult():
    """亮堂的候机厅：环境光高（日光灯），窗那一片暖一点；地上的窗光亮斑只亮一档（边上按 Bayer 抖），不抢人物。"""
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    amb = 0.8 + 0.06 * np.clip((yy - 100) / 60.0, 0, 1)
    lights = [dict(x=182, y=110, r=130, k=0.26, p=1.3, sy=1.4, col=(1.12, 1.04, 0.92))]
    lights += [dict(x=tx, y=14, r=60, k=0.12, p=1.2, sy=1.5, col=(1.0, 1.02, 1.06)) for tx in TUBES]
    m = P.light_map(PW, H, amb, lights, n=12, cool=(0.98, 0.99, 1.02))
    sm = sun_mask()
    bay = P.bayer(PW, H)
    edge = np.zeros_like(sm)
    edge[:, 1:] |= sm[:, 1:] != sm[:, :-1]
    inner = sm & ~(edge & (bay < 0.5))
    m[inner] *= np.array((1.08, 1.05, 0.98), np.float32)
    return m


@lru_cache(maxsize=1)
def near_img():
    im = wall_base()
    d = ImageDraw.Draw(im)
    gate(d, GP[0], GP[1], '2', 'PARIS', 'fr')
    gate(d, GT[0], GT[1], '5', 'TOKYO', 'jp')
    draw_board(d)
    draw_window_frame(d)
    draw_benches(d)
    draw_pillar_clock(d)
    draw_counter(d)
    for i, (x, b) in enumerate(PALMS):
        palm(d, x, b, 0, i, leaves=False)
    contact_shadows(im)
    im = P.apply_light(im, light_mult())
    window_view(im)
    d = ImageDraw.Draw(im)
    for tx in TUBES:                                                                         # 日光灯管（自己发光）
        rect(d, tx - 10, 10, tx + 10, 11, (250, 252, 255))
    return P.opaque(im)


# ============================================================ 会动的
def apron_frame(t):
    """窗外（16 帧 @4 fps = 4 s）：远处一架小飞机从右边的滑行道转上跑道、往左开走（侧影随转弯变）+ 管制塔的雷达转。
    竖挺 / 横挺上不画（飞机在窗外，被窗框挡住）。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t, 16, 4.0)
    x0, y0, x1, y1 = WIN
    # 飞机：0–5 帧从右边斜着开过来（越来越大一点）、6–9 帧转弯（机头从对着我们转到朝左）、10–15 帧往左开走
    path = [(232, 99), (224, 99), (216, 98), (208, 98), (200, 98), (193, 98), (187, 98), (181, 98), (175, 98),
            (167, 98), (157, 98), (147, 98), (137, 98), (128, 98), (119, 98), (110, 98)]
    pose = [2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]       # 2 = 机头对着我们 / 1 = 斜 / 0 = 机头朝左
    x, y = path[f]
    pts = []
    if pose[f] == 0:
        pts += [(x + k, y) for k in range(-4, 7)] + [(x + 5, y - 1), (x + 6, y - 2), (x + 6, y - 3), (x + 1, y + 1),
                                                      (x + 2, y + 1), (x, y - 1)]
    elif pose[f] == 1:
        pts += [(x + k, y) for k in range(-3, 5)] + [(x - 4, y + 1), (x + 4, y - 1), (x + 3, y - 2), (x + 1, y + 1),
                                                      (x - 1, y - 1)]
    else:
        pts += [(x + k, y) for k in range(-5, 6)] + [(x, y - 1), (x, y - 2), (x - 1, y + 1), (x + 1, y + 1)]
    for (u, v) in pts:
        if not is_bar(u, v):
            px(d, u, v, (240, 240, 244) if v <= y else (190, 192, 198))
    if not is_bar(x - 2, y):
        px(d, x - 2 if pose[f] != 2 else x, y, (220, 60, 50))                                   # 航行灯
    # 雷达：天线（横条）绕竖轴转：宽度 5 → 1 → 5 变
    tx, ty = x0 + 18, HZ - 42
    wv = [3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 2][f]
    hl(d, tx - wv, tx + wv, ty, (230, 230, 226))
    px(d, tx, ty + 1, (150, 140, 126))
    return im


ROWS_Y = BOARD[1] + 10


def board_frame(t):
    """东京那一行的状态栏（x 101–115）：0–3 帧翻牌（字母乱跳），4–7 帧亮出 BOARD（一明一暗）。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    x0, y0, x1, y1 = BOARD
    sx = x0 + 29
    y = ROWS_Y
    rect(d, sx - 1, y - 1, sx + 19, y + 5, (40, 42, 48))
    if f < 4:
        letters = 'ABCDEFGHKLMNOPRSTUVWXYZ'
        for k in range(5):
            ch = letters[int(hash01(f, k, 5) * len(letters))]
            P.text35(d, sx + k * 4, y, ch, (250, 214, 90))
            hl(d, sx + k * 4, sx + k * 4 + 2, y + 2, (20, 22, 26))                                  # 翻牌中间的缝
    else:
        P.text35(d, sx, y, 'BOARD', (120, 255, 150) if f % 2 == 0 else (60, 150, 80))
    return im


def gate_lamp_frame(t):
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    k = (1.0, 0.85, 0.3, 1.0, 0.75, 0.3, 0.95, 0.6)[f]
    c = mix((30, 70, 40), (120, 255, 150), k)
    rect(d, 260, 106, 262, 108, c)
    P.text35(d, 264, 105, 'GO', mix((90, 90, 90), (236, 240, 244), 0.6 + 0.4 * k))
    return im


def tube_frame(t):
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    tx = TUBES[FLICK]
    k = (1.0, 1.0, 0.35, 1.0, 0.95, 1.0, 0.25, 0.9)[fno(t, 8, 8.0)]
    rect(d, tx - 10, 10, tx + 10, 11, mix((150, 152, 156), (250, 252, 255), k))
    px(d, tx - 10 + int(hash01(fno(t, 8, 8.0), 3) * 20), 10, (240, 244, 255))
    return im


def palm_frame(t):
    """两盆棕榈的叶子被空调吹得轻轻晃：每帧只重画叶子（盆和干在底图）。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    for i, (x, b) in enumerate(PALMS):
        sw = (0, 1, 2, 3, 2, 1, 0, -1)[(f + i * 3) % 8]
        palm(d, x, b, sw, i, pot=False)
    return im


def clock_frame(t):
    """挂钟的秒针（8 帧走一圈 = 加速的“秒针”，2 s 一圈：每帧 45°）。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    cx, cy = CLOCK
    a = math.radians(-90 + fno(t) * 45)
    for k in range(1, 6):
        px(d, cx + int(round(k * math.cos(a))), cy + int(round(k * math.sin(a))), (210, 40, 40))
    return im


# ============================================================ 组装
@lru_cache(maxsize=1)
def specs():
    x0, y0, x1, y1 = WIN
    S = [dict(t='pano', name='near', img=near_img(), k=1.0),
         P.strip('apron', apron_frame, (x0, y0, x1 + 1, HZ + 6), n=16, fps=4.0),
         P.strip('board', board_frame, (BOARD[0], BOARD[1], BOARD[2] + 1, BOARD[3] + 1)),
         P.strip('gate_lamp', gate_lamp_frame, (256, 100, 280, 112)),
         P.strip('tube', tube_frame, (TUBES[FLICK] - 12, 8, TUBES[FLICK] + 12, 13), n=8, fps=8.0),
         P.strip('palm0', palm_frame, (PALMS[0][0] - 16, 110, PALMS[0][0] + 17, FLOOR)),
         P.strip('palm1', palm_frame, (PALMS[1][0] - 16, 110, PW, FLOOR)),
         P.strip('clock', clock_frame, (CLOCK[0] - 7, CLOCK[1] - 7, CLOCK[0] + 8, CLOCK[1] + 8))]
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
        name='机场', pw=PW, walk=WALK, states=[{}],
        opaque=[('近景整张不透明', near, (0, 0, PW, H))],
        binary=[('近景只有 0 / 255 两种透明度', near)],
        stand=['arrive', 'benches', 'gate', 'gate_paris'],
        inside=['board', 'window', 'plane_door', 'clock', 'counter'],
        notes=['可走带亮度（y %d–%d）：均值 %.0f 标准差 %.1f' % (WALK[0], WALK[1], m0, s0)],
    )
    P.std_checks(ex, BJ, st, S, cfg)
    x0, y0, x1, y1 = WIN
    dx, dy = PLANE_DOOR
    ex.checked('舱门 plane_door 在大玻璃窗里（看得见）', int(not (x0 < dx < x1 and y0 < dy < y1)))
    bx0, by0, bx1, by1 = BOARD
    ex.checked('board 锚点在航班牌上', int(not (bx0 <= 96 <= bx1 and by0 <= 84 <= by1)))
    ok = sum(1 for (gx, (a, b)) in ((276, GT), (24, GP)) if a <= gx <= b)
    ex.checked('gate / gate_paris 锚点正对各自的门洞', 2 - ok)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'final', 'after')
    os.makedirs(od, exist_ok=True)
    P.direct(specs(), 0, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'airport_solo.png'))
    print('ok')
