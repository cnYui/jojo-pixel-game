# -*- coding: utf-8 -*-
r"""luxor_town —— 第9章「卢克索的街」：浅土黄的楼、木格窗、遮阳棚，远处卢克索神庙的柱廊和方尖碑，下午。
（第 19 战段 1 玛丽亚 / 巴斯特女神的街道，9-16 阿莱西的影子，9-19 阿莱西被打出门外。）
2026-10-19 egypt-town 组按体验版精度重画（改前是 later_stages.town(21)：一排平涂方块房）。零件在 egypt_town_parts.py。

地图 960 宽、ground 160、可走带 y 148–176（晒褪了色的旧柏油路，补丁、裂缝都压得很淡）；墙脚 = 地面后沿 y 146
（146–147 一道水泥路沿），房子 / 摊子 / 咖啡馆的桌椅都画在 y ≤ 145，可走带里只有平的东西。
**光从右上来**（下午的太阳在西边）：剧情 9-16 里擦窗工人“背对着阳光，影子往左拉得很长”，所以这张图的墙右沿亮、
左沿暗，挑出来的东西往左下落影，和剧情画的长影子同一个方向。零件都是按“太阳在左”写的，所以近景 / 中景先在画布上
按镜像的坐标画（画布 x = 959 − 世界 x，函数 MX / MR），最后整张左右翻过来；远景直接按右边的光画。
从左到右（世界坐标）：
  x 0–40      街口：两层的转角楼（木格窗、百叶窗、路牌）
  x 40–78     一截矮墙 + 一棵海枣树（strip）：墙头上看得见远处神庙的柱子（anchors.arrive）
  x 78–160    两层的杂货铺：条纹遮阳棚（波浪边 strip）、门口一筐筐蔬菜、挂着的扫帚 / 水桶、二楼的晾衣绳
  x 160–236   一面很旧的墙：大块抹灰掉了露出土坯砖、墙脚一道褪色的青绿漆、一扇砖封死的拱窗、一张撕剩一半的旧海报、
              几道裂缝和水渍；墙脚上一只**崭新雪白的插座**（anchors.socket [210,140]，没有电线接它，偶尔闪一下 strip），
              插座前的站人点 anchors.socket_stand
  x 236–330   两层楼（挑出的木格窗）+ 楼前卖插座 / 杂货的小摊：红白条纹太阳伞（伞边 strip）、木桌上一排排插头、插座、
              灯泡、电池、一卷卷电线，后面一块挂满东西的洞洞板（anchors.mariah 站摊前）
  x 330–488   露天咖啡馆（ahwa）：二楼小阳台、绿白条纹遮阳棚（波浪边 strip）、绿底白字招牌；敞开的店面里有柜台、铜咖啡壶、
              一排水烟壶、墙角支架上的电视（屏幕 strip 闪）、吊扇（strip 转）；门外靠墙两张小圆桌 + 椅子、
              两个抽水烟的老人（背景人，压灰，烟 strip）、x 434 那张桌子底下有地方给伊奇钻（anchors.cafe、cafe_owner）
  x 488–620   三层的公寓楼 + 楼前搭的木脚手架（三根立杆、三层木板、麻绳绑的斜撑、一架靠着的梯子），
              最上层挂着水桶和抹布（strip 晃）；anchors.scaffold [560,120] 是脚手架中间，擦窗工人站 anchors.washer
  x 620–688   两层民宅：木门（anchors.house_door：小孩波鲁纳雷夫跑进去的那扇）、门边长凳、窗台的花
  x 688–714   窄巷（anchors.alley）：两边的墙往里收、头顶晾的衣服（strip），巷子台阶上一筐刚出炉的大饼
  x 714–790   面包房：敞开的窑口（火光 strip）、一排排晾在棕榈叶托盘上的大饼、烟囱的烟（strip）
  x 790–880   两层楼：铁栏杆阳台 + 晾的地毯、绿百叶窗、一楼关着的蓝铁门
  x 880–960   去火车站的路：一棵海枣树（strip）、铁路道口的红白栏杆（抬着）+ 叉形警示牌、蓝色路牌（火车 + 箭头）
              （anchors.station_road）
头顶：几根木电线杆之间拉着电线（y 20–60）。
远景（k 0.3）：西岸的底比斯山（库尔恩峰）、卢克索神庙——塔门、门前的方尖碑和坐像、一长排纸莎草柱头的大柱廊、
塔门上的阿布·哈贾吉清真寺（宣礼塔 + 穹顶）、几片海枣林；中景（k 0.6）：后排的房顶、水箱、天线、一座宣礼塔、右边的火车站。

图层（从后往前）：
  sky       static           320×180 下午的天 + 右上的太阳
  clouds    wrap   k 0.08 vx 1.0   小积云 + 云丝（640 循环）
  far       pano   k 0.3           远景 512 宽：底比斯山、神庙（罩雾）
  mid       pano   k 0.6           中景 704 宽：后排房顶
  birds     clouds k 0.15          两只鸢
  near      pano   k 1             整条街（960 宽）
  palm_0…2  strip  k 1             海枣树冠
  valance_0/1 strip k 1            杂货铺、咖啡馆遮阳棚的波浪边
  umbrella  strip  k 1             小摊太阳伞的伞边
  smoke_0…2 strip  k 1             两个老人的水烟、面包房烟囱
  tv / fan  strip  k 1             咖啡馆的电视、吊扇
  oven      strip  k 1             面包房窑口的火
  laundry   strip  k 1             窄巷 + 杂货铺二楼的晾衣绳
  bucket    strip  k 1             脚手架上的水桶和抹布
  socket    strip  k 1             插座偶尔闪一下（崭新的塑料反光）
锚点：arrive [40,164]、socket [210,140]、socket_stand [212,162]、mariah [260,160]、cafe [400,152]、cafe_owner [420,158]、
      scaffold [560,120]、washer [560,162]、alley [700,156]、station_road [930,162]（素材总表 §一.3）；
      另导出 house_door [640,146]（小孩波鲁纳雷夫跑进去的门）、sugar [434,152]（伊奇钻桌子底下叼方糖的地方）、
      stall_box、cafe_tables、scaffold_box、socket_box、sun_dir -1（太阳在右边：影子往左）、lane_back 146。
key：无（素材总表没有要求）。
单独运行：python -B tools\bg_new\luxor_town.py → tools\bg_new\_preview\ch9\after\luxor_town_solo.png
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

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _parts():
    """egypt-town 组的零件（tools\\bg_new\\egypt_town_parts.py，按路径加载，模块名同 bg_jojo.bg_new，不改 sys.path 顺序）。"""
    key = 'bg_new_egypt_town_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'egypt_town_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
V = P.V
C = P.C
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
mul_box, mul_mask, poly_mask, cast_shadow, mottle, haze, opaque = (P.mul_box, P.mul_mask, P.poly_mask, P.cast_shadow,
                                                                  P.mottle, P.haze, P.opaque)
SHADOW_MUL, SOFT_MUL = P.SHADOW_MUL, P.SOFT_MUL
INK = P.INK
WOOD_HI, WOOD, WOOD_D, WOOD_K = P.WOOD_HI, P.WOOD, P.WOOD_D, P.WOOD_K
IRON, IRON_HI, BRASS = P.IRON, P.IRON_HI, P.BRASS
DARK_IN = P.DARK_IN
soft_shadow, put_inside, picto, leafy = P.soft_shadow, P.put_inside, P.picto, P.leafy
cached = P.cached_frames

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 960
GROUND = 160
WALK = (148, 176)
LANE = 146
N, FPS = P.N_ANIM, P.FPS_ANIM
CLOUD_P, CLOUD_K, CLOUD_VX = 640, 0.08, 1.0
FAR_K, MID_K, BIRD_K = 0.3, 0.6, 0.15
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 512
MIDW = W + int(math.ceil((PW - W) * MID_K))      # 704


def MX(x):
    """世界 x → 画布 x（近景 / 中景先在画布上按“太阳在左”画，最后整张左右翻：太阳就到了右边）。"""
    return PW - 1 - x


def MR(a, b):
    """世界 [a, b) → 画布 [PW − b, PW − a)。"""
    return PW - b, PW - a


# 世界坐标的分段
B0 = (0, 40)
GAP0 = (40, 78)
B1 = (78, 160)
OLDWALL = (160, 236)
B3 = (236, 330)
STALL = (238, 288)
CAFE = (330, 488)
SCAF_B = (488, 620)
SCAF = (520, 602)              # 脚手架（三根立杆在世界 x 522 / 560 / 598）
HOUSE = (620, 688)
ALLEY = (688, 714)
BAKERY = (714, 790)
B8 = (790, 880)
ROAD = (880, 960)
SOCKET = (210, 140)
HOUSE_DOOR = (632, 648)        # 世界 x 范围
CAFE_TABLES = [(352, 1), (434, -1)]   # 门外两张小圆桌（世界 x，椅子摆向）

ANCHORS = dict(arrive=[40, 164], socket=[210, 140], socket_stand=[212, 162], mariah=[260, 160], cafe=[400, 152],
               cafe_owner=[420, 158], scaffold=[560, 120], washer=[560, 162], alley=[700, 156], station_road=[930, 162])
STAND = ('arrive', 'socket_stand', 'mariah', 'cafe', 'cafe_owner', 'washer', 'alley', 'station_road')
REQUIRED = tuple(ANCHORS)

# ============================================================ 调色
SKY_STOPS = [(62, 112, 190), (92, 140, 206), (138, 174, 216), (198, 204, 206), (240, 214, 170)]
HAZE = (232, 212, 182)
ASPH = (176, 166, 150)         # 晒褪了色的旧柏油路
ASPH_S = (166, 156, 140)
ASPH_HI = (186, 176, 160)
CURB = (206, 198, 182)
SANDY, SANDY_D = P.SANDY, P.SANDY_D
OCHRE_P = (222, 184, 132)      # 浅赭
PINK_P = (226, 182, 160)       # 褪色的粉
OFFW = (232, 222, 200)         # 米白
GRAYB = (200, 196, 184)        # 灰白（公寓楼的水泥）
OLD = (196, 176, 140)          # 旧墙的抹灰
OLD_PAINT = (150, 182, 168)    # 旧墙脚的青绿漆
SHUT_G, SHUT_B = (70, 120, 96), (90, 120, 150)
LEAF_D, LEAF, LEAF_M, LEAF_HI = P.LEAF_D, P.LEAF, P.LEAF_M, P.LEAF_HI


def fidx(t):
    return P.frame_of(t, N, FPS)


# ============================================================ 天 / 远景 / 中景
def sky_img():
    """下午的天：上蓝、地平线发暖；太阳在右上（光晕分档）。"""
    return P.sun_sky(SKY_STOPS, (276, 26), sun_r=6, glow=(255, 236, 196), glow_a=80)


def clouds_img():
    return P.wisps_img(period=CLOUD_P, hgt=56, seed=47)


def theban_ridge(x):
    """西岸底比斯山的脊线（远景层 x）：一长条台地，x 330 一座金字塔形的库尔恩峰。"""
    return (74 + 4 * math.sin(x * 0.018 + 1.1) + 2.2 * math.sin(x * 0.07 + 0.3) + 1.2 * math.sin(x * 0.19)
            - 16 * max(0.0, 1 - abs(x - 330) / 46.0))


TEMPLE_Y = 112                 # 神庙地面（远景层 y）
COLS_X = list(range(130, 300, 17))   # 大柱廊的柱子（远景层 x）


def pap_column(d, x, top, base, w=7):
    """纸莎草柱（开花式柱头）：柱身右亮左暗（太阳在右），顶上一个往外撇的柱头 + 一块方垫石。"""
    lit, mid, sh = (236, 206, 160), (214, 182, 138), (176, 146, 110)
    for yy in range(top + 6, base + 1):
        for k in range(w):
            c = mid
            if k >= w - 2:
                c = lit
            elif k == 0:
                c = sh
            if (yy - top) % 9 == 0:
                c = dk(c, 0.92)                                    # 柱身的一道道刻纹 / 石块缝
            px(d, x + k, yy, c)
    for r in range(5):                                             # 柱头：越往上越宽
        hw = w // 2 + 1 + r // 2
        cx = x + w // 2
        hl(d, cx - hw, cx + hw, top + 5 - r, lit if r < 3 else mid)
        px(d, cx - hw, top + 5 - r, sh)
    rect(d, x - 1, top - 2, x + w, top, mid)                        # 垫石
    hl(d, x - 1, x + w, top - 2, lit)


@lru_cache(maxsize=1)
def far_img():
    """远景（512 宽，k 0.3）：底比斯山 + 卢克索神庙。直接按“太阳在右”画（不翻）。"""
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    # 底比斯山（偏红的土黄，右坡受光）
    for x in range(FARW):
        top = int(round(theban_ridge(x)))
        slope = theban_ridge(x + 1.5) - theban_ridge(x - 1.5)
        for y in range(top, TEMPLE_Y + 1):
            c = (214, 170, 128) if slope > 0.4 else ((198, 154, 116) if slope > -0.4 else (180, 138, 106))
            if (y + int(x * 0.4)) % 7 == 0:
                c = dk(c, 0.95)
            px(d, x, y, c)
        px(d, x, top, lt((214, 170, 128), 0.25) if slope > 0 else (198, 154, 116))
    # 山脚的绿带（西岸的田）+ 一道河（远处一条亮线）
    for x in range(FARW):
        for y in range(98, 104):
            px(d, x, y, (150, 160, 110) if (x + y) % 4 else (136, 150, 100))
        px(d, x, 104, (190, 210, 214))
        px(d, x, 105, (170, 196, 204))
    for y in range(106, H):                                        # 东岸的地（神庙脚下），铺到底
        hl(d, 0, FARW - 1, y, (214, 192, 152) if y % 3 else (206, 184, 144))
    # 海枣林（神庙两边）
    for i, x in enumerate(list(range(4, 100, 9)) + list(range(330, 500, 11))):
        h = int(hrange(14, 24, i, 401))
        yb = TEMPLE_Y
        vl(d, x, yb - h, yb, (140, 112, 84))
        for k in range(-5, 6):
            yy = yb - h + abs(k) // 2 + (1 if abs(k) > 3 else 0)
            px(d, x + k, yy, (84, 120, 70))
            if abs(k) > 1:
                px(d, x + k, yy + 1, (70, 104, 60))
    # 塔门（梯形，两座塔楼 + 中间的门洞），门前的方尖碑和两尊坐像
    pa, pb = 66, 124
    for y in range(66, TEMPLE_Y + 1):
        u = (y - 66) / float(TEMPLE_Y - 66)
        inset = int(round((1 - u) * 5))
        for x in range(pa + inset, pb - inset):
            c = (222, 190, 146) if x > (pa + pb) // 2 else (200, 166, 126)
            if (y - 66) % 6 == 0:
                c = dk(c, 0.94)
            px(d, x, y, c)
    rect(d, 90, 88, 99, TEMPLE_Y, (120, 96, 80))                    # 门洞
    hl(d, pa + 5, pb - 6, 66, (240, 214, 170))
    for x in range(pa + 8, pb - 8, 5):                             # 塔门上的浮雕（几道竖刻的人形）
        for y in range(74, 86, 4):
            vl(d, x, y, y + 2, (186, 152, 112))
    ox = 58                                                        # 方尖碑（左边那根）
    for y in range(48, TEMPLE_Y + 1):
        u = (y - 48) / float(TEMPLE_Y - 48)
        hw = 1 + int(round(u * 1.6))
        hl(d, ox - hw, ox + hw, y, (210, 176, 136))
        px(d, ox + hw, y, (236, 206, 160))
        px(d, ox - hw, y, (178, 144, 108))
    px(d, ox, 46, (240, 214, 170))
    hl(d, ox - 1, ox + 1, 47, (226, 196, 150))
    for y in range(56, 104, 6):                                    # 方尖碑上的象形文字（一点点）
        px(d, ox, y, (170, 136, 100))
    for sx in (74, 112):                                           # 坐像
        rect(d, sx - 3, 98, sx + 3, TEMPLE_Y, (204, 170, 130))
        rect(d, sx - 2, 92, sx + 1, 97, (214, 180, 138))
        rect(d, sx - 2, 89, sx + 1, 91, (190, 160, 120))
        px(d, sx + 3, 100, (232, 202, 156))
    # 塔门顶上的阿布·哈贾吉清真寺（小穹顶 + 宣礼塔），在神庙的残墙上
    rect(d, 126, 84, 146, 96, (232, 224, 206))
    d.pieslice((130, 77, 142, 89), 180, 360, fill=C((236, 230, 214)))
    vl(d, 150, 62, 96, (236, 230, 214))
    vl(d, 151, 62, 96, (214, 206, 190))
    rect(d, 149, 70, 152, 71, (224, 216, 200))
    px(d, 150, 60, (226, 196, 90))
    # 大柱廊：一长排纸莎草柱 + 上面的额枋
    for i, cx in enumerate(COLS_X):
        pap_column(d, cx, 58 + (i % 2), TEMPLE_Y)
    for i in range(len(COLS_X) - 1):
        a, b = COLS_X[i] - 1, COLS_X[i + 1] + 7
        if i % 3 != 2:                                             # 有几段额枋塌了
            rect(d, a, 54 + (i % 2), b, 57 + (i % 2), (220, 188, 144))
            hl(d, a, b, 54 + (i % 2), (240, 214, 170))
    # 右边：第二进庭院的一排矮柱 + 残墙
    for i, cx in enumerate(range(312, 400, 12)):
        pap_column(d, cx, 80 + (i % 3) * 2, TEMPLE_Y, w=5)
    rect(d, 300, 100, 410, TEMPLE_Y, (206, 174, 132))
    hl(d, 300, 410, 100, (226, 196, 152))
    # 罩雾（越往上越远）
    amt = np.zeros((H, 1), np.float32)
    for y in range(H):
        amt[y, 0] = 0.5 if y < 96 else 0.36
    im = haze(im, amt, HAZE)
    return opaque(im)


def mid_house(im, x0, x1, top, col, seed, roof=None):
    """中景的一栋房（画布坐标 = 镜像，太阳在左；整层最后会翻）：抹灰 + 小窗洞 + 屋顶的东西。"""
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = P.wall_pal(col)
    rect(d, x0, top, x1 - 1, H - 1, md)
    vl(d, x0, top, H - 1, hi)
    vl(d, x1 - 1, top, H - 1, sh)
    hl(d, x0, x1 - 1, top, hi)
    for i in range(max(1, (x1 - x0) // 8)):
        wx = x0 + 3 + i * 8
        if wx + 3 > x1 - 2:
            break
        for wy in range(top + 5, 132, 12):
            if hash01(seed, i, wy, 1) < 0.7:
                rect(d, wx, wy, wx + 2, wy + 4, dk(md, 0.55))
                if hash01(seed, i, wy, 2) < 0.4:
                    rect(d, wx, wy, wx + 2, wy + 4, (70, 110, 90))  # 关着的绿百叶
                hl(d, wx - 1, wx + 3, wy + 5, hi)
    if roof == 'tank':
        rect(d, x0 + 3, top - 6, x0 + 10, top - 1, (178, 178, 180))
        hl(d, x0 + 3, x0 + 10, top - 6, (214, 214, 214))
    elif roof == 'antenna':
        ax = x1 - 6
        vl(d, ax, top - 12, top, (96, 96, 100))
        for k, w in ((0, 4), (3, 3), (6, 2)):
            hl(d, ax - w, ax + w, top - 12 + k, (96, 96, 100))
    elif roof == 'laundry':
        V.wire(d, x0 + 1, top - 6, x1 - 2, top - 6, 2, (90, 86, 84))
        for k in range(4):
            cx = x0 + 4 + k * ((x1 - x0 - 8) // 4)
            c = P.CLOTH[int(hash01(seed, k, 3) * len(P.CLOTH))]
            rect(d, cx, top - 5, cx + 2, top - 2, c)
    elif roof == 'dome':
        P.dome(im, (x0 + x1) // 2, top, max(5, (x1 - x0) // 3), col, drum=1)
    elif roof == 'parapet':
        rect(d, x0, top - 3, x1 - 1, top - 1, lt(md, 0.06))
        for x in range(x0 + 2, x1 - 2, 4):
            px(d, x, top - 2, dk(md, 0.7))


@lru_cache(maxsize=1)
def mid_img():
    """中景（704 宽，k 0.6）：后排的房顶（画布镜像画，最后翻）。世界左端（画布右端）矮一点，看得见远处的神庙。"""
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    for x in range(MIDW):
        yb = 120 + int(round(2 * math.sin(x * 0.05)))
        for y in range(yb, H):
            px(d, x, y, (204, 184, 148) if (x + y) % 5 else (196, 176, 140))
    houses = [(70, 104, 86, OFFW, 'laundry'),
              (104, 128, 104, PINK_P, None), (128, 166, 90, SANDY_D, 'antenna'), (166, 196, 98, OFFW, 'parapet'),
              (196, 236, 84, SANDY, 'tank'), (236, 262, 102, OCHRE_P, 'dome'), (262, 300, 94, GRAYB, 'laundry'),
              (300, 336, 88, SANDY_D, 'antenna'), (336, 372, 100, OFFW, 'tank'), (372, 400, 92, PINK_P, 'parapet'),
              (420, 452, 98, SANDY, 'laundry'), (452, 486, 90, GRAYB, 'antenna'), (486, 516, 104, OCHRE_P, None),
              (516, 548, 96, OFFW, 'tank'), (548, 572, 108, SANDY_D, 'parapet')]
    for i, (x0, x1, top, col, roof) in enumerate(houses):
        mid_house(im, x0, x1, top, col, 860 + i, roof)
    P.minaret(im, 410, 122, 40, 8, (236, 228, 210), speakers=True)
    # 画布左端（= 世界右端，去车站的路那头）：火车站的站房（两层、拱窗、中间一座钟楼）+ 水塔
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = P.wall_pal((226, 196, 150))
    rect(d, 0, 92, 68, H - 1, md)
    hl(d, 0, 68, 92, hi)
    vl(d, 0, 92, H - 1, hi)
    vl(d, 68, 92, H - 1, sh)
    for wx in range(4, 64, 9):
        rect(d, wx, 100, wx + 4, 108, dk(md, 0.55))
        d.pieslice((wx, 97, wx + 4, 103), 180, 360, fill=C(dk(md, 0.55)))
        rect(d, wx, 114, wx + 4, 121, dk(md, 0.6))
    hl(d, 0, 68, 110, sh)
    tx = 28
    rect(d, tx, 70, tx + 12, 92, md)
    vl(d, tx, 70, 92, hi)
    vl(d, tx + 12, 70, 92, sh)
    d.ellipse((tx + 3, 74, tx + 9, 80), fill=C((244, 240, 228)))
    px(d, tx + 6, 77, (40, 40, 40))
    px(d, tx + 6, 76, (40, 40, 40))
    px(d, tx + 7, 77, (40, 40, 40))
    for k in range(4):
        hl(d, tx - 1 + k, tx + 13 - k, 69 - k, sh if k % 2 else md)
    wtx = 52                                                       # 水塔（铁架 + 圆罐）
    for lx in (wtx - 5, wtx + 5):
        vl(d, lx, 70, 92, (110, 110, 116))
    d.line((wtx - 5, 76, wtx + 5, 90), fill=C((110, 110, 116)))
    d.line((wtx + 5, 76, wtx - 5, 90), fill=C((110, 110, 116)))
    rect(d, wtx - 7, 58, wtx + 7, 70, (150, 150, 156))
    hl(d, wtx - 7, wtx + 7, 58, (190, 190, 196))
    vl(d, wtx - 7, 58, 70, (176, 176, 182))
    for i, (x, top) in enumerate(((60, 80), (180, 84), (290, 78), (412, 86), (534, 82), (600, 90), (640, 86))):
        vl(d, x, top, 122, (140, 110, 80))
        vl(d, x + 1, top, 122, (116, 88, 64))
        for k in range(11):
            ang = math.radians(-20 + k * 22)
            L = 9 if 2 < k < 9 else 7
            for j in range(1, L):
                xx = x + int(round(math.cos(ang) * j))
                yy = top - int(round(math.sin(ang) * j * 0.55)) + j * j // 10
                px(d, xx, yy, (62, 112, 60) if j % 2 else (90, 140, 72))
    im = haze(im, 0.28, HAZE)
    im = A._grade(im, sat=0.86, val=1.0)
    return opaque(im.transpose(Image.FLIP_LEFT_RIGHT))


def birds_img():
    return V.kite_bird_img()


BIRDS = [(16, -2.6, BIRD_K, 120), (26, 2.0, BIRD_K, 360)]


# ============================================================ 近景：地面（画布坐标，最后跟近景一起翻）
def draw_ground(im):
    d = ImageDraw.Draw(im)
    rect(d, 0, LANE, PW - 1, H - 1, ASPH)
    mottle(im, (0, WALK[0], PW - 1, H - 1), ASPH, ASPH_S, ASPH_HI, 911, cell=7, lo=0.24, hi=0.78)
    d = ImageDraw.Draw(im)
    rect(d, 0, LANE, PW - 1, LANE + 1, CURB)                        # 水泥路沿（上面一行亮）
    hl(d, 0, PW - 1, LANE + 1, dk(CURB, 0.9))
    for x in range(0, PW, 11):
        px(d, x, LANE, dk(CURB, 0.92))
        px(d, x, LANE + 1, dk(CURB, 0.84))
    # 补过的柏油补丁（颜色深一点点）、裂缝、油渍、尘土（都压得很淡）
    for i in range(14):
        x, y = int(hrange(0, PW - 30, i, 912)), int(hrange(150, 170, i, 913))
        w, h = int(hrange(14, 30, i, 914)), int(hrange(4, 7, i, 915))
        rect(d, x, y, x + w, y + h, (170, 160, 144))
        hl(d, x, x + w, y, (174, 164, 148))
    for i in range(40):
        x, y = int(hrange(0, PW, i, 916)), int(hrange(WALK[0] + 1, H - 1, i, 917))
        for k in range(int(hrange(3, 9, i, 918))):
            px(d, x, y, (164, 154, 138))
            x += 1
            y += (1 if hash01(i, k, 919) < 0.3 else (-1 if hash01(i, k, 919) > 0.75 else 0))
            y = max(WALK[0] + 1, min(H - 1, y))
    for i in range(90):
        x, y = int(hrange(0, PW, i, 920)), int(hrange(WALK[0], H, i, 921))
        c = ((186, 176, 158), (166, 158, 144), (190, 182, 160), (172, 160, 140))[i % 4]
        px(d, x, y, c)
    for x in range(PW):                                            # 路沿下面一道细影
        if x % 2 == 0:
            px(d, x, WALK[0], dk(ASPH, 0.95))
    # 车轮压出来的两道深一点的带（断断续续）+ 几块油渍 + 一个井盖（都是平的，压得很淡）
    for (ya, yb) in ((157, 159), (168, 170)):
        for x in range(PW):
            if hash01(x // 17, ya, 922) < 0.7:
                for y in range(ya, yb + 1):
                    if hash01(x, y, 923) < 0.6:
                        px(d, x, y, dk(im.getpixel((x, y))[:3], 0.95))
    for i in range(9):
        cx, cy = int(hrange(20, PW - 20, i, 924)), int(hrange(152, 172, i, 925))
        rx, ry = int(hrange(3, 7, i, 926)), int(hrange(1, 3, i, 927))
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / float(rx)) ** 2 + ((y - cy) / float(ry)) ** 2 <= 1.0 and hash01(x, y, 928) < 0.8:
                    px(d, x, y, dk(im.getpixel((x, y))[:3], 0.9))
    mx, my = MX(600), 166                                          # 井盖（铸铁，一圈亮边 + 格纹）
    d.ellipse((mx - 7, my - 2, mx + 7, my + 2), fill=C((150, 144, 134)))
    d.ellipse((mx - 7, my - 2, mx + 7, my + 2), outline=C((136, 130, 120)))
    for x in range(mx - 5, mx + 6, 2):
        px(d, x, my, (160, 154, 144))
    hl(d, mx - 5, mx + 5, my - 2, (172, 166, 154))


def ground_shade(im):
    """墙脚（路沿那两行）压一道暗。"""
    a = np.array(im)
    for x in range(PW):
        if a[LANE - 1, x, 3] > 0:
            a[LANE, x, :3] = (a[LANE, x, :3] * np.array((0.88, 0.88, 0.92))).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))


# ============================================================ 近景：街口 + 杂货铺
def draw_b0(im):
    x0, x1 = MR(*B0)
    top = 56
    P.plaster(im, x0, x1, top, LANE - 1, SANDY, 1101, streaks=2)
    d = ImageDraw.Draw(im)
    rect(d, x0, top - 3, x1 - 1, top - 1, lt(SANDY, 0.1))           # 平顶的压檐
    hl(d, x0, x1 - 1, top - 3, lt(SANDY, 0.3))
    P.mashrabiya(im, x0 + 12, 66, 16, 22, seed=2)
    P.grille_window(im, x0 + 14, 104, 12, 16, SANDY, frame=OFFW, kind='shutter', shutter=SHUT_G, state='closed', seed=1)
    d = ImageDraw.Draw(im)
    rect(d, x0 + 2, 128, x0 + 10, 133, (36, 72, 140), outline=(230, 230, 230))   # 蓝色路牌
    P.sign_ar(d, x0 + 3, 129, x0 + 9, 132, None, (240, 240, 236), seed=3, dots=False)
    P.spout(im, x0 + 2, top + 4, L=5, wall=SANDY, stain_len=14)


def draw_gap0(im):
    x0, x1 = MR(*GAP0)
    P.palm_trunk(im, x0 + 20, 132, 66, lean=-3, seed=4)            # 墙后一棵海枣（树冠 strip）
    P.plaster(im, x0, x1, 122, LANE - 1, OFFW, 1102, streaks=1, cracks=2)
    d = ImageDraw.Draw(im)
    rect(d, x0, 119, x1 - 1, 121, lt(OFFW, 0.1))
    hl(d, x0, x1 - 1, 119, lt(OFFW, 0.35))
    P.brick_patch(im, x0 + 10, 134, 5, 3, 1103)
    d = ImageDraw.Draw(im)
    for k, col in enumerate(((190, 60, 60), (240, 200, 60))):      # 墙头上两盆花
        fx = x0 + 6 + k * 18
        rect(d, fx, 116, fx + 3, 118, (176, 96, 64))
        rect(d, fx - 1, 113, fx + 4, 115, LEAF)
        px(d, fx, 113, col)
        px(d, fx + 3, 114, col)


def draw_b1(im):
    x0, x1 = MR(*B1)
    top = 60
    P.plaster(im, x0, x1, top, LANE - 1, OCHRE_P, 1111, streaks=3)
    d = ImageDraw.Draw(im)
    rect(d, x0, top - 3, x1 - 1, top - 1, lt(OCHRE_P, 0.12))
    hl(d, x0, x1 - 1, top - 3, lt(OCHRE_P, 0.35))
    for wx in (x0 + 8, x0 + 34, x0 + 60):                           # 二楼三扇百叶窗
        P.grille_window(im, wx, 70, 11, 16, OCHRE_P, frame=OFFW, kind='shutter', shutter=SHUT_B,
                        state=('half', 'closed', 'open')[(wx - x0) // 26 % 3], seed=wx)
    d = ImageDraw.Draw(im)
    V.wire(d, x0 + 4, 90, x1 - 6, 90, 3, (90, 86, 84))             # 二楼窗外的晾衣绳（衣服在 strip）
    hl(d, x0, x1 - 1, 96, lt(OCHRE_P, 0.3))
    hl(d, x0, x1 - 1, 97, dk(OCHRE_P, 0.8))
    # 招牌（红底黄字）+ 店面
    rect(d, x0 + 4, 99, x1 - 5, 106, (176, 48, 44), outline=(120, 30, 30))
    hl(d, x0 + 5, x1 - 6, 100, (210, 90, 80))
    P.sign_ar(d, x0 + 6, 99, x1 - 7, 106, None, (250, 220, 110), seed=5)
    a, b = x0 + 6, x1 - 6
    rect(d, a, 110, b - 1, LANE - 1, (96, 76, 60))
    for sy in (118, 126, 134):                                     # 店里的架子：罐头、油瓶、米袋
        hl(d, a + 1, b - 2, sy, (150, 110, 72))
        for k in range((b - a - 4) // 4):
            col = ((200, 60, 50), (230, 200, 70), (70, 120, 170), (236, 232, 222), (90, 150, 80))[int(hash01(sy, k, 1112) * 5)]
            rect(d, a + 2 + k * 4, sy - 3, a + 4 + k * 4, sy - 1, col)
            px(d, a + 2 + k * 4, sy - 3, lt(col, 0.3))
    vl(d, a, 110, LANE - 1, (70, 56, 46))
    mul_box(im, (a, 110, b - 1, 113), SHADOW_MUL)
    d = ImageDraw.Draw(im)
    P.awning(im, a - 3, b + 2, 107, 4, (60, 140, 90), (240, 236, 220), stripe=4, scallop=False, shadow=0)
    d = ImageDraw.Draw(im)
    # 门口：三筐菜（番茄、土豆、青椒）、一只扫帚、一只挂着的塑料水桶
    for k, (col, col2) in enumerate((((210, 50, 40), (240, 100, 80)), ((196, 160, 100), (220, 190, 130)),
                                     ((70, 150, 60), (120, 190, 90)))):
        bx = a + 4 + k * 12
        P.basket(d, bx, LANE - 1, 10, 6, (190, 150, 92))
        for j in range(5):
            px(d, bx + 1 + j * 2, LANE - 8, col)
            px(d, bx + 2 + j * 2, LANE - 8, col2)
            px(d, bx + 2 + j * 2, LANE - 9, col)
    vl(d, b - 4, 120, LANE - 1, (180, 150, 90))
    for k in range(5):
        px(d, b - 6 + k, LANE - 1 - (k % 2), (200, 170, 100))
    rect(d, b - 12, 114, b - 8, 119, (60, 120, 190))
    hl(d, b - 12, b - 8, 113, (150, 150, 156))
    soft_shadow(im, a, b, LANE, depth=1, slant=3)


# ============================================================ 近景：旧墙 + 插座
def draw_oldwall(im):
    x0, x1 = MR(*OLDWALL)
    top = 94
    d = ImageDraw.Draw(im)
    # 墙头残缺不齐（塌掉的地方露出后面的天）
    for x in range(x0, x1):
        tt = top + int(round(3 * math.sin(x * 0.21) + 2 * hash01(x // 3, 1121)))
        if 18 < x - x0 < 30:
            tt += 7                                                # 一大块塌下去的缺口
        rect(d, x, tt, x, LANE - 1, OLD)
    mottle(im, (x0, top - 4, x1 - 1, LANE - 1), OLD, dk(OLD, 0.9), lt(OLD, 0.08), 1122, cell=4, streaks=4)
    d = ImageDraw.Draw(im)
    # 墙脚一道褪色的青绿漆（一块块掉了）
    for y in range(126, LANE):
        for x in range(x0, x1):
            if hash01(x // 2, y // 2, 1123) < 0.78 - (126 - y) * 0.0:
                c = OLD_PAINT if (x + y) % 9 else dk(OLD_PAINT, 0.92)
                if hash01(x, y, 1124) < 0.06:
                    c = OLD
                px(d, x, y, c)
    hl(d, x0, x1 - 1, 126, dk(OLD_PAINT, 0.8))
    # 大块掉了抹灰露出土坯砖
    for (cx, cy, rx, ry, sd) in ((x0 + 14, 110, 8, 5, 1125), (x0 + 52, 104, 6, 4, 1126), (x0 + 60, 134, 5, 3, 1127)):
        P.brick_patch(im, cx, cy, rx, ry, sd)
    d = ImageDraw.Draw(im)
    # 一扇用砖封死的拱窗
    wx, wy = x0 + 34, 102
    d.pieslice((wx - 1, wy - 6, wx + 13, wy + 8), 180, 360, fill=C(dk(OLD, 0.86)))
    rect(d, wx, wy, wx + 12, wy + 14, dk(OLD, 0.86))
    for yy in range(wy - 3, wy + 15, 3):
        hl(d, wx + 1, wx + 11, yy, dk(OLD, 0.74))
        for xx in range(wx + 1 + (yy // 3 % 2) * 2, wx + 12, 4):
            px(d, xx, yy + 1, dk(OLD, 0.74))
    hl(d, wx - 2, wx + 14, wy + 15, lt(OLD, 0.2))
    # 撕剩一半的旧海报（褪色的红 / 黄，边上卷起来）
    rect(d, x0 + 54, 116, x0 + 64, 124, (214, 180, 140))
    rect(d, x0 + 55, 117, x0 + 63, 119, (190, 110, 90))
    P.sign_ar(d, x0 + 55, 119, x0 + 63, 124, None, (120, 80, 70), seed=7, dots=False)
    for k in range(4):
        px(d, x0 + 64 - k, 124 - k // 2, OLD)
    # 裂缝、水渍
    for i in range(5):
        P.crack(d, x0 + 6 + i * 13, 98 + (i % 3) * 6, 10 + i % 4, 1128 + i, dk(OLD, 0.7))
    # 插座（崭新的白塑料：一块方面板 + 两个圆孔 + 中间接地片，一圈细影）—— 整张图最“干净”的一处。
    # 周围一圈旧墙更脏（手摸、雨水溅上来的灰），新面板才更跳
    sx = MX(SOCKET[0])
    sy = SOCKET[1]
    for y in range(sy - 9, LANE):
        for x in range(sx - 11, sx + 12):
            r = math.hypot((x - sx) / 11.0, (y - sy) / 9.0)
            if r < 1.0 and hash01(x, y, 1129) < (1.0 - r) * 1.1:
                px(d, x, y, dk(im.getpixel((x, y))[:3], 0.84))
    rect(d, sx - 3, sy - 3, sx + 3, sy + 3, (250, 250, 246))
    hl(d, sx - 3, sx + 3, sy - 3, (255, 255, 255))
    vl(d, sx - 3, sy - 3, sy + 3, (255, 255, 255))
    vl(d, sx + 3, sy - 2, sy + 3, (206, 206, 200))
    hl(d, sx - 2, sx + 3, sy + 3, (206, 206, 200))
    d.ellipse((sx - 2, sy - 2, sx + 2, sy + 2), outline=C((222, 222, 216)))
    px(d, sx - 1, sy, (40, 40, 40))
    px(d, sx + 1, sy, (40, 40, 40))
    px(d, sx, sy - 2, (180, 180, 176))
    mul_box(im, (sx - 2, sy + 4, sx + 4, sy + 4), SHADOW_MUL)        # 面板下沿一道影（太阳在左上）
    mul_box(im, (sx + 4, sy - 2, sx + 4, sy + 4), SHADOW_MUL)
    soft_shadow(im, x0, x1, LANE, depth=1, slant=3)


# ============================================================ 近景：小摊楼 + 卖插座的小摊
def draw_b3(im):
    x0, x1 = MR(*B3)
    top = 52
    P.plaster(im, x0, x1, top, LANE - 1, OFFW, 1131, streaks=3)
    d = ImageDraw.Draw(im)
    rect(d, x0, top - 3, x1 - 1, top - 1, lt(OFFW, 0.1))
    hl(d, x0, x1 - 1, top - 3, lt(OFFW, 0.35))
    for k in range(x0 + 2, x1 - 2, 6):                              # 屋顶女儿墙上的小孔
        px(d, k, top - 2, dk(OFFW, 0.7))
    P.mashrabiya(im, x0 + 36, 62, 24, 28, seed=6)
    for wx in (x0 + 8, x1 - 20):
        P.grille_window(im, wx, 66, 11, 16, OFFW, frame=lt(OFFW, 0.3), kind='shutter', shutter=SHUT_G,
                        state='closed' if wx == x0 + 8 else 'half', seed=wx)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, 100, lt(OFFW, 0.3))
    hl(d, x0, x1 - 1, 101, dk(OFFW, 0.84))
    # 一楼：一扇关着的绿铁门（小摊就摆在门前）+ 门边一块小招牌
    P.door(im, x1 - 30, LANE - 1, 18, 36, (80, 120, 100), frame=lt(OFFW, 0.2), arch=False, studs=True, seed=8)
    P.grille_window(im, x0 + 10, 110, 12, 12, OFFW, frame=lt(OFFW, 0.3), kind='bars')
    P.spout(im, x0 + 3, top + 2, L=5, wall=OFFW, stain_len=14)


STALL_UMB = (MX(262), 102)     # 太阳伞的伞顶（画布坐标）


def draw_stall(im):
    """卖插座 / 杂货的小摊：木桌 + 桌上一排排插头、插座、灯泡、电池、电线卷；后面一块洞洞板挂满东西；
    一把红白条纹的太阳伞（伞边在 strip）。"""
    a, b = MR(*STALL)
    d = ImageDraw.Draw(im)
    # 洞洞板（靠墙，挂着电线、插头、手电筒）
    ba, bb = a + 6, b - 6
    rect(d, ba, 108, bb, 126, (196, 170, 130))
    for y in range(110, 126, 3):
        for x in range(ba + 2, bb, 3):
            px(d, x, y, (150, 124, 90))
    hl(d, ba, bb, 108, (220, 196, 156))
    vl(d, bb, 108, 126, (150, 124, 90))
    for k in range(7):                                             # 挂着的东西
        hx = ba + 3 + k * 6
        col = ((240, 240, 236), (40, 40, 44), (230, 200, 70), (200, 60, 50), (60, 110, 180), (240, 240, 236),
               (90, 90, 96))[k]
        vl(d, hx, 110, 112, IRON_HI)
        if k % 3 == 0:                                             # 一圈电线
            d.ellipse((hx - 2, 112, hx + 2, 117), outline=C(col))
        elif k % 3 == 1:                                           # 插头（方块 + 两根脚）
            rect(d, hx - 1, 113, hx + 1, 115, col)
            px(d, hx - 1, 116, (190, 190, 190))
            px(d, hx + 1, 116, (190, 190, 190))
        else:                                                      # 手电筒 / 灯泡盒
            rect(d, hx - 1, 113, hx + 1, 119, col)
            px(d, hx, 113, lt(col, 0.4))
    # 木桌（台面 + 前面一块布帘）
    ty = 128
    rect(d, a + 2, ty, b - 3, ty + 1, WOOD_HI)
    hl(d, a + 2, b - 3, ty + 2, WOOD_D)
    for x in range(a + 2, b - 2):
        for y in range(ty + 3, LANE - 1):
            c = (196, 60, 70) if ((x - a) // 4) % 2 else (230, 214, 190)
            if y == ty + 3:
                c = dk(c, 0.8)
            px(d, x, y, c)
    hl(d, a + 2, b - 3, LANE - 1, (110, 60, 60))
    # 台面上的货：一排白插座面板、插头、一个个灯泡（亮白 + 金色螺口）、一板电池、电线卷
    for k in range(4):
        rect(d, a + 4 + k * 5, ty - 4, a + 7 + k * 5, ty - 1, (244, 244, 240))
        px(d, a + 5 + k * 5, ty - 3, (60, 60, 60))
        px(d, a + 6 + k * 5, ty - 3, (60, 60, 60))
    for k in range(4):
        bx = a + 26 + k * 4
        d.ellipse((bx, ty - 6, bx + 3, ty - 3), fill=C((246, 244, 230)))
        px(d, bx + 1, ty - 5, (255, 255, 255))
        rect(d, bx + 1, ty - 2, bx + 2, ty - 1, (200, 170, 80))
    rect(d, b - 14, ty - 3, b - 6, ty - 1, (40, 40, 44))             # 一板电池
    for k in range(4):
        px(d, b - 13 + k * 2, ty - 3, (220, 180, 60))
    d.ellipse((b - 22, ty - 5, b - 16, ty - 1), outline=C((40, 40, 44)))   # 电线卷
    d.ellipse((b - 21, ty - 4, b - 17, ty - 2), outline=C((60, 60, 66)))
    # 太阳伞：一根杆 + 伞面（红白条，上亮下暗；伞边在 strip）
    ux, uy = STALL_UMB
    vl(d, ux, uy, LANE - 1, (200, 200, 204))
    vl(d, ux + 1, uy + 4, LANE - 1, (150, 150, 156))
    for r in range(8):
        hw = 6 + r * 3
        for x in range(ux - hw, ux + hw + 1):
            k = int((math.atan2(r + 2, x - ux) / math.pi) * 8)
            c = (210, 50, 50) if k % 2 else (244, 240, 230)
            if r == 0:
                c = lt(c, 0.3)
            elif r >= 6:
                c = dk(c, 0.86)
            px(d, x, uy + r, c)
    px(d, ux, uy - 1, (200, 200, 204))
    mul_box(im, (ux - 26, uy + 11, ux + 30, uy + 14), SOFT_MUL)       # 伞下洞洞板上的一道影（整块乘，不用 Bayer 点）
    soft_shadow(im, a + 2, b - 3, LANE, depth=1, slant=3)


# ============================================================ 近景：咖啡馆
CAFE_OPEN = (344, 476)         # 敞开的店面（世界 x）
CAFE_TV = (112, 1)             # 电视框左上（店里的局部坐标 = 画布坐标减店面左沿、减 y 112）


def cafe_interior(w, h):
    """店里（画布坐标，宽 w、高 h，从起拱线往上 rise 那一行算起）：后墙的镜子和架子、柜台 + 铜咖啡壶、一排水烟壶、
    墙角支架上的电视（屏幕在 strip）、墙上挂的老照片。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    wall, wall_d = (132, 104, 82), (110, 86, 68)
    rect(d, 0, 0, w - 1, h - 1, wall)
    for y in range(0, h, 2):
        for x in range(w):
            if hash01(x, y, 1141) < 0.16:
                px(d, x, y, wall_d)
    rect(d, 0, h - 6, w - 1, h - 1, (110, 92, 76))                  # 地（黑白格的水磨石，压暗）
    for x in range(0, w, 2):
        for y in range(h - 6, h):
            if (x // 2 + y) % 2 == 0:
                px(d, x, y, (130, 112, 94))
    # 两面镜子（ahwa 后墙都挂镜子）
    for mx in (52, 76):
        rect(d, mx, 4, mx + 14, 16, (150, 170, 176))
        rect(d, mx - 1, 3, mx + 15, 17, None, outline=(196, 160, 80))
        for k in range(3):
            px(d, mx + 3 + k, 6 + k, (210, 226, 230))
    # 老照片两张
    for (fx, col) in ((100, (60, 50, 50)), (34, (70, 60, 52))):
        rect(d, fx, 5, fx + 6, 12, (180, 150, 80))
        rect(d, fx + 1, 6, fx + 5, 11, col)
        px(d, fx + 3, 8, (170, 140, 110))
    # 柜台（左边）+ 铜咖啡壶 + 一摞小杯 + 糖罐
    cy = h - 18
    rect(d, 2, cy, 44, h - 1, (124, 84, 52))
    hl(d, 1, 45, cy, (176, 132, 84))
    hl(d, 1, 45, cy + 1, (150, 104, 66))
    for x in range(6, 44, 6):
        vl(d, x, cy + 3, h - 2, (104, 70, 44))
    kx = 12
    rect(d, kx - 2, cy - 6, kx + 2, cy - 1, BRASS[1])
    hl(d, kx - 3, kx + 3, cy - 7, BRASS[2])
    px(d, kx - 2, cy - 5, BRASS[3])
    hl(d, kx + 3, kx + 6, cy - 6, BRASS[0])                        # 长柄
    for k in range(3):
        rect(d, 22 + k * 3, cy - 3, 23 + k * 3, cy - 1, (236, 236, 230))
    rect(d, 34, cy - 4, 38, cy - 1, (220, 220, 214))
    hl(d, 34, 38, cy - 5, (180, 60, 50))
    # 一排水烟壶（镜子前面的地上）
    for i, g in enumerate(((110, 160, 150), (160, 90, 120), (90, 130, 170), (120, 170, 110))):
        P.shisha(d, 56 + i * 8, h - 6, glass=g)
    # 墙角支架上的电视（屏幕先画暗的，strip 画闪的）
    tx, ty = CAFE_TV
    rect(d, tx, ty, tx + 14, ty + 10, (60, 56, 58))
    rect(d, tx + 2, ty + 2, tx + 10, ty + 8, (70, 90, 96))
    rect(d, tx + 12, ty + 2, tx + 13, ty + 8, (110, 106, 100))
    vl(d, tx + 7, ty + 11, ty + 14, (90, 90, 96))
    hl(d, tx + 2, tx + 12, ty + 14, (90, 90, 96))
    return im


def draw_cafe(im):
    x0, x1 = MR(*CAFE)
    top = 58
    P.plaster(im, x0, x1, top, LANE - 1, SANDY, 1151, streaks=3)
    d = ImageDraw.Draw(im)
    rect(d, x0, top - 3, x1 - 1, top - 1, lt(SANDY, 0.1))
    hl(d, x0, x1 - 1, top - 3, lt(SANDY, 0.35))
    # 二楼：三扇百叶窗 + 中间一个铁栏杆小阳台（门开着，晾着一件衣服）
    for wx in (x0 + 10, x0 + 44, x1 - 56, x1 - 22):
        P.grille_window(im, wx, 68, 11, 16, SANDY, frame=OFFW, kind='shutter', shutter=SHUT_G,
                        state=('closed', 'half', 'open', 'closed')[(wx - x0) // 30 % 4], seed=wx)
    d = ImageDraw.Draw(im)
    cxm = (x0 + x1) // 2
    rect(d, cxm - 10, 64, cxm + 10, 86, DARK_IN)
    vl(d, cxm, 64, 86, (90, 70, 60))
    rect(d, cxm - 14, 86, cxm + 14, 87, (200, 196, 190))
    hl(d, cxm - 14, cxm + 14, 88, (120, 110, 104))
    for x in range(cxm - 13, cxm + 14, 3):
        vl(d, x, 79, 85, IRON)
    hl(d, cxm - 14, cxm + 14, 78, IRON_HI)
    mul_box(im, (cxm - 12, 89, cxm + 16, 92), SHADOW_MUL, level=0.7)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, 94, lt(SANDY, 0.3))
    hl(d, x0, x1 - 1, 95, dk(SANDY, 0.82))
    # 招牌：绿底白字 + 左边一杯咖啡（土耳其咖啡小杯）
    sa, sb = x0 + 8, x1 - 9
    rect(d, sa, 97, sb, 105, (40, 108, 72), outline=(26, 70, 48))
    hl(d, sa + 1, sb - 1, 98, (70, 140, 100))
    P.sign_ar(d, sa + 14, 97, sb - 2, 105, None, (244, 240, 226), seed=15)
    rect(d, sa + 4, 100, sa + 8, 103, (240, 240, 232))
    hl(d, sa + 3, sa + 9, 104, (240, 240, 232))
    px(d, sa + 9, 101, (240, 240, 232))
    # 敞开的店面（卷帘门收在上面）+ 里面
    a, b = MR(*CAFE_OPEN)
    inner = cafe_interior(b - a, LANE - 1 - 112 + 1)
    paste(im, inner, a, 112)
    d = ImageDraw.Draw(im)
    for yy in range(108, 112):
        hl(d, a, b - 1, yy, (160, 164, 160) if yy % 2 else (186, 190, 184))
    vl(d, a, 108, LANE - 1, (90, 70, 56))
    vl(d, a + 1, 112, LANE - 1, (110, 88, 70))
    mul_box(im, (a, 112, b - 1, 115), SHADOW_MUL)
    for xx in (a + (b - a) // 3, a + 2 * (b - a) // 3):              # 两根铁柱子
        vl(d, xx, 108, LANE - 1, (90, 90, 96))
        vl(d, xx + 1, 108, LANE - 1, (140, 140, 146))
    P.awning(im, a - 3, b + 2, 106, 4, (52, 130, 80), (240, 236, 222), stripe=4, scallop=False, shadow=0)
    d = ImageDraw.Draw(im)
    # 门外两张小圆桌 + 椅子 + 两只水烟壶（老人在 people 层）。都按世界坐标说：椅子在桌子 −8·face、人朝 face 坐，
    # 水烟壶在桌子另一边 +8·face；画布里 x 用 MX 换、朝向取反
    for (wx, face) in CAFE_TABLES:
        cx = MX(wx)
        P.round_table(d, cx, LANE - 1, 136, r=5, col=(170, 176, 180))
        P.tea_glass(d, cx - 2, 135)
        P.chair(d, MX(wx - 8 * face), LANE - 1, face=-face, col=(150, 104, 62), seat_y=LANE - 8)
        P.shisha(d, MX(wx + 8 * face), LANE - 1, glass=(120, 170, 150) if face > 0 else (160, 100, 120))
    soft_shadow(im, a, b, LANE, depth=1, slant=3)


# ============================================================ 近景：公寓楼 + 脚手架
def draw_scaf_building(im):
    x0, x1 = MR(*SCAF_B)
    top = 30
    P.plaster(im, x0, x1, top, LANE - 1, GRAYB, 1161, streaks=5, cell=5)
    d = ImageDraw.Draw(im)
    rect(d, x0, top - 3, x1 - 1, top - 1, lt(GRAYB, 0.1))
    hl(d, x0, x1 - 1, top - 3, lt(GRAYB, 0.35))
    for k in range(x0 + 4, x1 - 4, 7):
        rect(d, k, top - 6, k + 1, top - 4, (150, 150, 150))       # 屋顶伸出来的钢筋头（没盖完的楼）
    for (fy, rows) in ((40, 0), (72, 1), (104, 2)):
        for i, wx in enumerate(range(x0 + 8, x1 - 12, 22)):
            st = ('closed', 'open', 'half')[(i + rows) % 3]
            P.grille_window(im, wx, fy, 12, 18, GRAYB, frame=lt(GRAYB, 0.3), kind='shutter',
                            shutter=SHUT_B if (i + rows) % 2 else SHUT_G, state=st, seed=wx + fy)
        d = ImageDraw.Draw(im)
        hl(d, x0, x1 - 1, fy + 26, lt(GRAYB, 0.25))
        hl(d, x0, x1 - 1, fy + 27, dk(GRAYB, 0.84))
    d = ImageDraw.Draw(im)
    # 一楼：楼门（深色铁门，门上一块门牌）
    P.door(im, x0 + 52, LANE - 1, 16, 34, (70, 74, 86), frame=lt(GRAYB, 0.2), arch=False, studs=False, seed=9)
    d = ImageDraw.Draw(im)
    rect(d, x0 + 56, 104, x0 + 64, 108, (40, 90, 160))
    px(d, x0 + 60, 106, (240, 240, 240))


SCAF_POLES = [522, 560, 598]   # 世界 x
SCAF_PLANKS = [70, 98, 126]


def draw_scaffold(im):
    """木脚手架（埃及老式的：圆木杆 + 麻绳绑、木板搭的三层平台、斜撑、一架靠着的梯子）。画布坐标，最后跟着翻。"""
    d = ImageDraw.Draw(im)
    poles = [MX(x) for x in SCAF_POLES]
    lo, hi_ = min(poles), max(poles)
    wood, wood_hi, wood_sh = (150, 112, 70), (186, 146, 96), (104, 76, 48)
    # 杆子在墙上的影（太阳在左上：影子往右下落在墙上）
    for x in poles:
        cast_shadow(im, [(x + 2, 40), (x + 4, 40), (x + 6, LANE - 1), (x + 4, LANE - 1)], mul=SOFT_MUL)
    for y in SCAF_PLANKS:
        cast_shadow(im, [(lo - 2, y + 3), (hi_ + 3, y + 3), (hi_ + 6, y + 6), (lo + 1, y + 6)], mul=SOFT_MUL)
    d = ImageDraw.Draw(im)
    # 斜撑（两道交叉）+ 横杆
    for (xa, xb) in ((poles[0], poles[1]), (poles[1], poles[2])):
        for (ya, yb) in ((SCAF_PLANKS[0] + 2, SCAF_PLANKS[1]), (SCAF_PLANKS[1] + 2, SCAF_PLANKS[2])):
            d.line((xa, ya, xb, yb), fill=C(wood_sh))
            d.line((xa, yb, xb, ya), fill=C(wood_sh))
    # 立杆
    for x in poles:
        vl(d, x - 1, 40, LANE - 1, wood_hi)
        vl(d, x, 40, LANE - 1, wood)
        vl(d, x + 1, 40, LANE - 1, wood_sh)
        px(d, x, 39, wood_hi)
        for y in SCAF_PLANKS:                                      # 绑绳
            for k in range(3):
                px(d, x - 1 + k, y - 1, (220, 200, 150))
                px(d, x - 1 + k, y + 2, (200, 180, 130))
    # 木板平台
    for y in SCAF_PLANKS:
        hl(d, lo - 4, hi_ + 4, y, wood_hi)
        hl(d, lo - 4, hi_ + 4, y + 1, wood)
        hl(d, lo - 4, hi_ + 4, y + 2, wood_sh)
        for x in range(lo - 4, hi_ + 4, 9):
            px(d, x, y + 1, wood_sh)
    # 梯子（靠在最左那根杆上，从地面到第三层）
    la, lb = poles[2] + 6, poles[2] + 12
    for y in range(SCAF_PLANKS[2] - 2, LANE):
        u = (y - (SCAF_PLANKS[2] - 2)) / float(LANE - (SCAF_PLANKS[2] - 2))
        px(d, la + int(round(u * 4)), y, wood_hi)
        px(d, lb + int(round(u * 4)), y, wood_sh)
        if (y - SCAF_PLANKS[2]) % 4 == 0:
            hl(d, la + int(round(u * 4)), lb + int(round(u * 4)), y, wood)
    # 第二层平台上：一桶水泥灰浆 + 一卷麻绳；最上层的东西（水桶、抹布）在 strip
    rect(d, poles[1] + 6, SCAF_PLANKS[1] - 5, poles[1] + 11, SCAF_PLANKS[1] - 1, (160, 160, 164))
    hl(d, poles[1] + 6, poles[1] + 11, SCAF_PLANKS[1] - 5, (200, 200, 204))
    d.ellipse((poles[0] - 10, SCAF_PLANKS[1] - 5, poles[0] - 4, SCAF_PLANKS[1] - 1), outline=C((210, 190, 140)))
    # 地上：一只倒扣的铁皮桶、一把扫帚、湿的一片（擦窗的水滴下来）
    rect(d, poles[1] - 14, LANE - 6, poles[1] - 8, LANE - 1, (150, 150, 156))
    hl(d, poles[1] - 15, poles[1] - 7, LANE - 6, (190, 190, 196))
    soft_shadow(im, lo - 4, hi_ + 4, LANE, depth=1, slant=3)


# ============================================================ 近景：民宅 + 窄巷 + 面包房
def draw_house(im):
    x0, x1 = MR(*HOUSE)
    top = 56
    P.plaster(im, x0, x1, top, LANE - 1, PINK_P, 1171, streaks=3)
    d = ImageDraw.Draw(im)
    rect(d, x0, top - 3, x1 - 1, top - 1, lt(PINK_P, 0.1))
    hl(d, x0, x1 - 1, top - 3, lt(PINK_P, 0.35))
    P.mashrabiya(im, x0 + 34, 64, 18, 24, seed=11)
    P.grille_window(im, x0 + 8, 68, 11, 16, PINK_P, frame=OFFW, kind='shutter', shutter=SHUT_G, state='open', seed=12)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, 98, lt(PINK_P, 0.3))
    hl(d, x0, x1 - 1, 99, dk(PINK_P, 0.82))
    # 木门（小孩波鲁纳雷夫跑进去的那扇；门半开，里面暗）
    da, db = MR(*HOUSE_DOOR)
    P.door(im, da, LANE - 1, db - da, 38, (140, 92, 54), frame=OFFW, arch=True, studs=True, seed=13, open_leaf=True)
    P.grille_window(im, x0 + 8, 112, 10, 12, PINK_P, frame=OFFW, kind='lattice')
    d = ImageDraw.Draw(im)
    for (fx, col) in ((x0 + 8, (210, 60, 70)), (x0 + 13, (240, 200, 60))):   # 窗台的花
        rect(d, fx, 126, fx + 3, 128, (170, 90, 60))
        px(d, fx + 1, 125, LEAF)
        px(d, fx, 124, col)
        px(d, fx + 2, 124, LEAF_M)
    P.bench(d, x0 + 4, x0 + 24, 138, LANE - 1, wood=(150, 104, 64))  # 门边长凳
    P.spout(im, x0 + 2, top + 4, L=5, wall=PINK_P, stain_len=12)
    soft_shadow(im, x0 + 4, x0 + 24, LANE, depth=1, slant=3)


def draw_alley(im):
    """窄巷（画布坐标）：两边的墙往里收、巷底一面墙 + 小门、台阶上一筐刚出炉的大饼；整条巷子罩在影子里。"""
    a, b = MR(*ALLEY)
    ia, ib = a + 6, b - 6
    back = 126
    d = ImageDraw.Draw(im)
    wall = (210, 184, 150)
    rect(d, ia, 64, ib - 1, back, wall)
    mottle(im, (ia, 64, ib - 1, back), wall, dk(wall, 0.92), lt(wall, 0.08), 1181, cell=3)
    d = ImageDraw.Draw(im)
    rect(d, ia + 4, 102, ia + 10, back - 3, (120, 70, 50))
    px(d, ia + 9, 114, BRASS[2])
    hl(d, ia + 2, ib - 3, back - 2, (180, 168, 150))
    hl(d, ia + 1, ib - 2, back - 1, (160, 148, 130))
    for x in range(a, ia):                                         # 画布左墙（背阴）
        u = (x - a) / float(ia - a)
        t = int(round(56 + u * 8))
        yb = int(round(LANE - 1 - u * (LANE - 1 - back)))
        for y in range(t, yb + 1):
            px(d, x, y, (150, 120, 92) if (x + y) % 5 else (138, 110, 84))
    for x in range(ib, b):                                         # 画布右墙（上半截受光）
        u = (b - 1 - x) / float(b - 1 - ib)
        t = int(round(54 + u * 10))
        yb = int(round(LANE - 1 - u * (LANE - 1 - back)))
        for y in range(t, yb + 1):
            c = (222, 208, 186) if y < 92 else (190, 178, 160)
            if (x * 3 + y) % 7 == 0:
                c = dk(c, 0.93)
            px(d, x, y, c)
    for y in range(back, LANE):                                    # 地面（往里上坡）
        u = (y - back) / float(LANE - 1 - back)
        xa = int(round(ia - u * (ia - a)))
        xb = int(round(ib - 1 + u * (b - ib)))
        for x in range(xa, xb + 1):
            px(d, x, y, (176, 160, 134) if (y % 4) else (160, 146, 122))
    # 台阶上一筐大饼（棕榈叶筐 + 一张张圆饼，伊奇叼出来的就是这个）
    P.basket(d, ia + 1, back + 8, 10, 4, (186, 150, 90))
    for k in range(3):
        d.ellipse((ia + 1 + k * 3, back + 1 - k % 2, ia + 6 + k * 3, back + 4 - k % 2), fill=C((214, 170, 110)))
        px(d, ia + 3 + k * 3, back + 2 - k % 2, (232, 196, 140))
    m = np.zeros((H, PW), bool)
    for y in range(50, LANE):
        for x in range(a, b):
            if not (x >= ib and y < 92):
                m[y, x] = True
    mul_mask(im, m, SHADOW_MUL)
    m2 = np.zeros((H, PW), bool)
    m2[64:back + 1, ia:ib] = True
    mul_mask(im, m2, np.array((0.88, 0.87, 0.9), np.float32))
    d = ImageDraw.Draw(im)
    for (y0, y1) in ((78, 80), (92, 93)):
        px(d, a + 1, y0, IRON)
        px(d, b - 2, y1, IRON)


def draw_bakery(im):
    x0, x1 = MR(*BAKERY)
    top = 76
    P.plaster(im, x0, x1, top, LANE - 1, SANDY_D, 1191, streaks=4)
    d = ImageDraw.Draw(im)
    rect(d, x0, top - 3, x1 - 1, top - 1, lt(SANDY_D, 0.1))
    hl(d, x0, x1 - 1, top - 3, lt(SANDY_D, 0.35))
    # 烟囱（砖砌，顶上冒烟在 strip）+ 墙上被烟熏黑的一道
    cx = x0 + 12
    rect(d, cx, top - 22, cx + 6, top - 3, (176, 120, 90))
    for y in range(top - 22, top - 3, 3):
        hl(d, cx, cx + 6, y, (150, 100, 76))
    hl(d, cx - 1, cx + 7, top - 23, (200, 150, 110))
    for y in range(top, top + 18):
        for x in range(cx - 1, cx + 8):
            if hash01(x, y, 1192) < 0.5 - (y - top) * 0.025:
                px(d, x, y, dk(im.getpixel((x, y))[:3], 0.8))
    # 招牌（白底蓝字）
    rect(d, x0 + 6, 84, x1 - 7, 91, (236, 232, 222), outline=(160, 150, 130))
    P.sign_ar(d, x0 + 7, 84, x1 - 8, 91, None, (40, 80, 150), seed=19)
    # 敞开的门面：里面暗，后墙一个圆拱窑口（火在 strip），前面一排排晾在棕榈叶托盘上的大饼
    a, b = x0 + 6, x1 - 6
    rect(d, a, 96, b - 1, LANE - 1, (86, 66, 56))
    vl(d, a, 96, LANE - 1, (60, 46, 40))
    mul_box(im, (a, 96, b - 1, 99), SHADOW_MUL)
    d = ImageDraw.Draw(im)
    ox = (a + b) // 2 + 6
    rect(d, ox - 12, 100, ox + 12, 124, (120, 84, 64))              # 窑（砖）
    for y in range(100, 124, 3):
        hl(d, ox - 12, ox + 12, y, (104, 72, 56))
    d.pieslice((ox - 6, 106, ox + 6, 118), 180, 360, fill=C((40, 26, 24)))
    rect(d, ox - 6, 112, ox + 6, 118, (40, 26, 24))
    for (ty, n) in ((128, 4), (134, 5), (140, 5)):                  # 托盘上的饼（在架子上，一层层）
        hl(d, a + 2, b - 3, ty + 2, (170, 140, 90))
        hl(d, a + 2, b - 3, ty + 3, (120, 96, 64))
        for k in range(n):
            fx = a + 4 + k * 10 + (ty // 6) % 2 * 3
            if fx + 6 > b - 3:
                break
            d.ellipse((fx, ty - 1, fx + 7, ty + 2), fill=C((214, 170, 110)))
            hl(d, fx + 2, fx + 5, ty - 1, (236, 200, 146))
            px(d, fx + 6, ty + 1, (180, 136, 86))
    soft_shadow(im, a, b, LANE, depth=1, slant=3)


def draw_b8(im):
    x0, x1 = MR(*B8)
    top = 48
    P.plaster(im, x0, x1, top, LANE - 1, OCHRE_P, 1201, streaks=4)
    d = ImageDraw.Draw(im)
    rect(d, x0, top - 3, x1 - 1, top - 1, lt(OCHRE_P, 0.1))
    hl(d, x0, x1 - 1, top - 3, lt(OCHRE_P, 0.35))
    for wx in (x0 + 10, x0 + 38, x0 + 66):
        P.grille_window(im, wx, 58, 11, 16, OCHRE_P, frame=OFFW, kind='shutter', shutter=SHUT_G,
                        state=('open', 'closed', 'half')[(wx - x0) // 28 % 3], seed=wx)
    d = ImageDraw.Draw(im)
    # 二楼铁栏杆长阳台 + 搭在栏杆上晾的花地毯
    rect(d, x0 + 6, 100, x1 - 7, 101, (200, 196, 190))
    hl(d, x0 + 6, x1 - 7, 102, (120, 110, 104))
    for x in range(x0 + 7, x1 - 7, 3):
        vl(d, x, 92, 99, IRON)
    hl(d, x0 + 6, x1 - 7, 91, IRON_HI)
    ca, cb = x0 + 30, x0 + 58
    for y in range(90, 112):
        for x in range(ca, cb):
            c = (170, 40, 50)
            if y in (90, 111) or x in (ca, cb - 1):
                c = (230, 190, 90)
            elif (abs(x - (ca + cb) // 2) + abs(y - 101)) % 6 == 0:
                c = (40, 60, 120)
            px(d, x, y, c)
    for x in range(ca, cb, 2):                                     # 地毯的穗
        px(d, x, 112, (230, 210, 170))
    mul_box(im, (x0 + 8, 103, x1 - 5, 106), SHADOW_MUL, level=0.7)
    d = ImageDraw.Draw(im)
    P.grille_window(im, x0 + 10, 72, 11, 14, OCHRE_P, frame=OFFW, kind='bars')
    hl(d, x0, x1 - 1, 116, lt(OCHRE_P, 0.3))
    hl(d, x0, x1 - 1, 117, dk(OCHRE_P, 0.82))
    # 一楼：关着的蓝铁门 + 一扇带铁栏的窗 + 墙上一块蓝牌
    P.door(im, x1 - 30, LANE - 1, 18, 26, (60, 90, 140), frame=lt(OCHRE_P, 0.2), arch=False, studs=False, seed=14)
    P.grille_window(im, x0 + 12, 124, 14, 10, OCHRE_P, frame=OFFW, kind='bars')
    d = ImageDraw.Draw(im)
    rect(d, x0 + 34, 124, x0 + 44, 129, (40, 90, 160), outline=(230, 230, 230))
    P.sign_ar(d, x0 + 35, 125, x0 + 43, 128, None, (240, 240, 236), seed=21, dots=False)


PICTO_CROSS = '''
X.......X
.X.....X.
..X...X..
...X.X...
....X....
...X.X...
..X...X..
.X.....X.
X.......X
'''


def draw_road(im):
    """去火车站的路（画布 x 0–79 = 世界 880–960）：海枣树、铁路道口的红白栏杆（抬起来的）+ 叉形牌、蓝色路牌（箭头朝世界右边
    = 画布左边）。"""
    x0, x1 = MR(*ROAD)
    P.palm_trunk(im, x0 + 66, LANE - 1, 84, lean=4, seed=15)
    d = ImageDraw.Draw(im)
    # 道口：栏杆的立柱 + 抬起来的红白横杆（斜着往上）
    bx = x0 + 22
    rect(d, bx - 2, 126, bx + 2, LANE - 1, (90, 90, 96))
    hl(d, bx - 2, bx + 2, 126, (140, 140, 146))
    for k in range(34):
        x = bx + int(round(k * 0.35))
        y = 126 - k
        c = (210, 40, 40) if (k // 4) % 2 else (240, 240, 236)
        px(d, x, y, c)
        px(d, x + 1, y, dk(c, 0.8))
    vl(d, x0 + 8, 108, LANE - 1, (120, 120, 126))                   # 叉形警示牌（白底红边）
    picto(im, PICTO_CROSS, x0 + 4, 100, (236, 236, 232))
    d = ImageDraw.Draw(im)
    for (xx, yy) in ((x0 + 4, 100), (x0 + 12, 100), (x0 + 8, 104), (x0 + 4, 108), (x0 + 12, 108)):
        px(d, xx, yy, (200, 40, 40))
    # 蓝色路牌：白色火车 + 箭头（画布里朝左，翻过来朝右）
    vl(d, x0 + 36, 108, LANE - 1, (120, 120, 126))
    vl(d, x0 + 37, 108, LANE - 1, (86, 86, 92))
    rect(d, x0 + 24, 100, x0 + 52, 110, (40, 86, 164), outline=(236, 236, 236))
    picto(im, '''
...XX.......
...XX...XXXX
.XXXXXX.X..X
XXXXXXXXXXXX
XXXXXXXXXXXX
..X.X...X.X.
''', x0 + 38, 103)
    d = ImageDraw.Draw(im)
    hl(d, x0 + 27, x0 + 35, 105, (246, 246, 246))
    px(d, x0 + 28, 104, (246, 246, 246))
    px(d, x0 + 28, 106, (246, 246, 246))
    px(d, x0 + 29, 103, (246, 246, 246))
    px(d, x0 + 29, 107, (246, 246, 246))
    soft_shadow(im, bx - 2, bx + 2, LANE, depth=1, slant=3)


POLES = [150, 486, 690, 880]   # 世界 x


def draw_poles(im):
    d = ImageDraw.Draw(im)
    tops = {150: 26, 486: 22, 690: 30, 880: 26}
    pins = {}
    for x in POLES:
        pins[x] = P.power_pole(d, MX(x), tops[x], LANE - 1)
    for (xa, xb, sag) in ((150, 486, 10), (486, 690, 8), (690, 880, 9)):
        for k in (0, 3):
            pa, pb = pins[xa][k], pins[xb][k]
            V.wire(d, pb[0], pb[1], pa[0], pa[1], sag + k, (52, 46, 46))
    V.wire(d, pins[150][0][0], pins[150][0][1], PW - 1, 46, 5, (52, 46, 46))
    V.wire(d, 0, 40, pins[880][3][0], pins[880][3][1], 4, (52, 46, 46))
    for x in POLES:
        soft_shadow(im, MX(x) - 1, MX(x) + 1, LANE, depth=1, slant=3)


PEOPLE = [  # 世界 x、凳面 y、样式、朝向（世界的朝向）、seed、身高、地面 y、衣服：咖啡馆门外抽水烟的两个老人
    (CAFE_TABLES[0][0] - 8, LANE - 8, 'smoke', 1, 21, 27, LANE - 1, (236, 232, 222)),
    (CAFE_TABLES[1][0] + 8, LANE - 8, 'tea', -1, 23, 27, LANE - 1, (150, 114, 84)),
]


def finish(im):
    """近景和贴在近景上的 strip 用同一套调色 + 可走带后面 y 106–145 压对比。"""
    im = A._grade(im, sat=0.95, val=1.0)
    P.compress_band(im, 106, LANE, (198, 184, 160), amt=0.14, ramp=10)
    return im


def flip(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


@lru_cache(maxsize=1)
def near_img():
    im = A._new(PW, H)
    draw_ground(im)
    draw_b0(im)
    draw_gap0(im)
    draw_b1(im)
    draw_oldwall(im)
    draw_b3(im)
    draw_cafe(im)
    draw_scaf_building(im)
    draw_house(im)
    draw_alley(im)
    draw_bakery(im)
    draw_b8(im)
    draw_road(im)
    im = P.outer_rim(im, INK, y1=LANE)
    draw_stall(im)
    draw_scaffold(im)
    draw_poles(im)
    crowd = [(MX(x), base, kind, -face, seed, h, ground, robe) for (x, base, kind, face, seed, h, ground, robe) in PEOPLE]
    im.alpha_composite(P.people_layer((PW, H), crowd, sat=0.7, amt=0.26, col=(214, 200, 178)))
    ground_shade(im)
    im = flip(im)
    box = (SOCKET[0] - 3, SOCKET[1] - 3, SOCKET[0] + 4, SOCKET[1] + 4)
    plate = im.crop(box)                                           # 插座面板不进“压对比”：崭新的白要比旧墙跳出来
    im = finish(im)
    im.paste(plate, box[:2])
    return opaque(im)


# ============================================================ strip（画在画布坐标的透明整张上，翻过来再调色）
PALMS = [(GAP0, 4), (ROAD, 15)]


def palm_tops():
    """两棵近景海枣的树冠中心（画布坐标）。"""
    g0 = MR(*GAP0)
    r0 = MR(*ROAD)
    return [(g0[0] + 20 - 3, 132 - 66, 17, 4), (r0[0] + 66 + 4, LANE - 1 - 84, 19, 15)]


def palms_raw(f):
    im = A._new(PW, H)
    for (cx, cy, R, sd) in palm_tops():
        P.palm_crown(im, cx, cy, R, seed=sd, f=f, n=N)
    return finish(flip(im))


def valance_raw(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    b1 = MR(*B1)
    a, b = b1[0] + 6, b1[1] - 6
    P.valance(d, a - 3, b + 2, 111, (60, 140, 90), (240, 236, 220), f, stripe=4, n=N, seed=0.4)
    ca, cb = MR(*CAFE_OPEN)
    P.valance(d, ca - 3, cb + 2, 110, (52, 130, 80), (240, 236, 222), f, stripe=4, n=N, seed=1.9)
    return finish(flip(im))


def umbrella_raw(f):
    """太阳伞的伞边：一圈红白小垂片，被风一阵阵掀起来。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    ux, uy = STALL_UMB
    y = uy + 8
    hw = 6 + 7 * 3
    for k, x in enumerate(range(ux - hw, ux + hw + 1, 3)):
        lift = 1 if math.sin(math.tau * f / N + k * 0.8) > 0.4 else 0
        c = (210, 50, 50) if k % 2 else (244, 240, 230)
        for r in range(3 - lift):
            hl(d, x, x + 2 - (1 if r == 2 - lift else 0), y + r, dk(c, 0.84) if r == 2 - lift else c)
    return finish(flip(im))


def smoke_raw(f):
    """两个老人吐的水烟（往左上飘：风从右边来）、面包房烟囱的烟：硬边白点，按 Bayer 抖开浓淡。"""
    a = np.zeros((H, PW, 4), np.float32)
    wx, face = CAFE_TABLES[0]                                      # 抽水烟老人的嘴（画布里他朝 −face）
    srcs = [(MX(wx - 8 * face) - 3 * face, LANE - 8 - 16, 9, 0.8, (240, 238, 232))]
    wx, face = CAFE_TABLES[1]                                      # 另一张桌子边上那只水烟壶的炭
    srcs.append((MX(wx + 8 * face), LANE - 1 - 20, 7, 0.7, (236, 234, 228)))
    bk = MR(*BAKERY)
    srcs.append((bk[0] + 15, 76 - 23, 22, 1.0, (210, 206, 200)))     # 烟囱口
    for si, (x0, y0, hgt, dens, col) in enumerate(srcs):
        for j in range(3):
            for k in range(hgt):
                u = k / float(hgt)
                ph = (f / float(N) + j / 3.0 + u * 0.5) % 1.0
                x = x0 + int(round(math.sin(math.tau * (u * 1.1 + f / float(N) + j * 0.33 + si)) * (1 + u * 2) + u * hgt * 0.35))
                y = y0 - k
                al = dens * (1.0 - u) * (0.55 + 0.45 * math.sin(math.tau * ph))
                if 0 <= y < H and 0 <= x < PW:
                    a[y, x, :3] = col
                    a[y, x, 3] = max(a[y, x, 3], al * 255)
                    if hgt > 12 and u > 0.3 and x + 1 < PW:
                        a[y, x + 1, :3] = col
                        a[y, x + 1, 3] = max(a[y, x + 1, 3], al * 200)
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    return finish(flip(P.hard_alpha(im)))


def cafe_tv_xy():
    a, b = MR(*CAFE_OPEN)
    return a + CAFE_TV[0], 112 + CAFE_TV[1]                        # 电视框左上（画布坐标）


def tv_raw(f):
    """咖啡馆里的电视：屏幕上的画面一帧帧换（球赛的绿 + 跑来跑去的小点），亮度跟着闪。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    tx, ty = cafe_tv_xy()
    k = (f * 3) % 7
    rect(d, tx + 2, ty + 2, tx + 10, ty + 8, (80, 150, 90) if f % 4 else (100, 170, 110))
    hl(d, tx + 2, tx + 10, ty + 2, (150, 190, 210))
    px(d, tx + 3 + k, ty + 5, (240, 240, 240))
    px(d, tx + 9 - k // 2, ty + 6, (200, 40, 40))
    px(d, tx + 4 + (k * 2) % 6, ty + 4, (40, 40, 160))
    return finish(flip(im))


def fan_raw(f):
    """咖啡馆天花板的吊扇：三片扇叶转（8 帧转 120°，正好闭合）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    a, b = MR(*CAFE_OPEN)
    cx, cy = a + 56, 116
    vl(d, cx, 112, cy - 1, (70, 70, 74))
    rect(d, cx - 1, cy - 1, cx + 1, cy, (110, 110, 116))
    ang0 = math.tau / 3 * f / N
    for k in range(3):
        ang = ang0 + k * math.tau / 3
        L = 9
        for j in range(2, L):
            x = cx + int(round(math.cos(ang) * j))
            y = cy + int(round(math.sin(ang) * j * 0.25))
            px(d, x, y, (150, 120, 90) if j < L - 1 else (120, 96, 72))
    return finish(flip(im))


def oven_raw(f):
    """面包房窑口里的火：几簇火苗上下跳、颜色一闪一闪。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x0, x1 = MR(*BAKERY)
    ox = (x0 + 6 + x1 - 6) // 2 + 6
    for k in range(5):
        h = 2 + int(2 * (0.5 + 0.5 * math.sin(math.tau * f / N * 2 + k * 1.3)))
        x = ox - 4 + k * 2
        for j in range(h):
            c = (250, 220, 120) if j == 0 else ((240, 150, 50) if j < h - 1 else (200, 80, 30))
            px(d, x, 117 - j, c)
    for k in range(4):
        px(d, ox - 5 + ((k * 3 + f) % 11), 118, (250, 200, 90) if (k + f) % 2 else (230, 120, 40))
    return finish(flip(im))


def laundry_raw(f):
    """两处晾衣绳：窄巷头顶（在影子里，压暗）+ 杂货铺二楼窗外。衣服的下摆跟着风摆。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    items = [((214, 214, 206), 6, 7), ((200, 70, 70), 4, 9), ((70, 110, 170), 5, 6), ((230, 200, 80), 4, 8),
             ((150, 170, 150), 6, 7), ((236, 160, 180), 5, 6)]
    al = MR(*ALLEY)
    b1 = MR(*B1)
    lines = [(al[0] + 1, 78, al[1] - 2, 80, 2, 3, True), (al[0] + 1, 92, al[1] - 2, 93, 2, 2, True),
             (b1[0] + 4, 90, b1[1] - 6, 90, 3, 5, False)]
    shade = np.zeros((H, PW), bool)
    for li, (x0, y0, x1, y1, sag, n, dark) in enumerate(lines):
        pts = V.garland_pts(x0, y0, x1, y1, sag)
        if dark:
            d.line([(round(x), round(y)) for (x, y) in pts], fill=C((90, 86, 84)))
        for j in range(n):
            col, w, L = items[(li * 3 + j) % len(items)]
            xa = x0 + 3 + j * ((x1 - x0 - 6) // n)
            ya = int(round(pts[min(len(pts) - 1, xa - x0)][1])) + 1
            sw = math.sin(math.tau * f / N + j * 1.7 + li)
            for r in range(L):
                dx = int(round(sw * 1.2 * (r / float(L))))
                for k in range(w):
                    c = col if k > 0 else lt(col, 0.2)
                    if k == w - 1:
                        c = dk(col, 0.75)
                    px(d, xa + k + dx, ya + r, c)
                    if dark:
                        shade[ya + r, xa + k + dx] = True
            px(d, xa, ya - 1, (200, 190, 170))
            px(d, xa + w - 1, ya - 1, (200, 190, 170))
    a = np.array(im).astype(np.float32)
    a[shade, :3] *= SHADOW_MUL
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    return finish(flip(im))


def bucket_raw(f):
    """脚手架最上层：麻绳吊着的水桶轻轻晃、搭在木板上的两块抹布被风掀动。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    poles = [MX(x) for x in SCAF_POLES]
    y = SCAF_PLANKS[0]
    hx = poles[1] - 9
    sw = math.sin(math.tau * f / N)
    bx = hx + int(round(sw * 1.5))
    d.line((hx, y + 3, bx, y + 12), fill=C((210, 190, 140)))
    rect(d, bx - 3, y + 12, bx + 3, y + 17, (90, 120, 170))
    hl(d, bx - 3, bx + 3, y + 12, (140, 170, 210))
    vl(d, bx + 3, y + 12, y + 17, (60, 84, 120))
    d.arc((bx - 3, y + 10, bx + 3, y + 14), 180, 360, fill=C((150, 150, 156)))
    for k, (rx, col) in enumerate(((poles[0] - 10, (236, 220, 190)), (poles[2] + 6, (200, 80, 70)))):
        lift = math.sin(math.tau * f / N + k * 2.0)
        for r in range(6):
            dx = int(round(lift * r * 0.35))
            hl(d, rx + dx, rx + dx + 4, y + 3 + r, col if r < 5 else dk(col, 0.8))
    return finish(flip(im))


def socket_raw(f):
    """插座的反光：一个小十字星从面板右上角亮一下（8 帧里亮 2 帧，其余帧只留面板上一个亮点）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    sx, sy = MX(SOCKET[0]), SOCKET[1]
    gx, gy = sx - 2, sy - 3
    if f in (0, 1):
        r = 2 if f == 0 else 1
        hl(d, gx - r, gx + r, gy, (255, 255, 255))
        vl(d, gx, gy - r, gy + r, (255, 255, 255))
    elif f in (2, 6):
        px(d, gx, gy, (255, 255, 250))
    else:
        px(d, gx + (f % 2), gy, (250, 250, 246))
    return finish(flip(im))


palms_frame = cached(palms_raw)
valance_frame = cached(valance_raw)
umbrella_frame = cached(umbrella_raw)
smoke_frame = cached(smoke_raw)
tv_frame = cached(tv_raw)
fan_frame = cached(fan_raw)
oven_frame = cached(oven_raw)
laundry_frame = cached(laundry_raw)
bucket_frame = cached(bucket_raw)
socket_frame = cached(socket_raw)


def _boxes_of(fn, groups):
    return [P.auto_box(fn, N, FPS, limit=(xa, 0, xb, H)) for (xa, xb) in groups]


@lru_cache(maxsize=1)
def strips():
    """(name, box, fn) 列表（k 1，世界坐标）。框都从画出来的东西算。"""
    out = []
    for i, bx in enumerate(_boxes_of(palms_frame, [(20, 110), (840, 960)])):
        out.append(('palm_%d' % i, bx, palms_frame))
    for i, bx in enumerate(_boxes_of(valance_frame, [B1, CAFE])):
        out.append(('valance_%d' % i, bx, valance_frame))
    out.append(('umbrella', P.auto_box(umbrella_frame, N, FPS), umbrella_frame))
    for i, bx in enumerate(_boxes_of(smoke_frame, [(330, 400), (400, 488), BAKERY])):
        out.append(('smoke_%d' % i, bx, smoke_frame))
    out.append(('tv', P.auto_box(tv_frame, N, FPS), tv_frame))
    out.append(('fan', P.auto_box(fan_frame, N, FPS), fan_frame))
    out.append(('oven', P.auto_box(oven_frame, N, FPS), oven_frame))
    for i, bx in enumerate(_boxes_of(laundry_frame, [ALLEY, B1])):
        out.append(('laundry_%d' % i, bx, laundry_frame))
    out.append(('bucket', P.auto_box(bucket_frame, N, FPS), bucket_frame))
    out.append(('socket', P.auto_box(socket_frame, N, FPS), socket_frame))
    return out


@lru_cache(maxsize=1)
def table():
    tb = [('static', 'sky', sky_img(), 0, 0),
          ('wrap', 'clouds', clouds_img(), CLOUD_P, CLOUD_K, 4, CLOUD_VX)]
    fim, fy = P.crop_pano(far_img())
    tb.append(('pano', 'far', fim, FAR_K, 0, fy))
    mim, my = P.crop_pano(mid_img())
    tb.append(('pano', 'mid', mim, MID_K, 0, my))
    bird = birds_img()
    tb.append(('clouds', 'birds', 460, [('bird%d' % i, bird, x0, y, vx, k) for i, (y, vx, k, x0) in enumerate(BIRDS)]))
    nim, ny = P.crop_pano(near_img())
    tb.append(('pano', 'near', nim, 1.0, 0, ny))
    for (name, box, fn) in strips():
        tb.append(('strip', name, box, N, FPS, fn, 1.0))
    return tuple(tb)


def compose(camX, t=0.5, state=None):
    return P.compose(table(), camX, t, state)


def anchors():
    anc = {k: list(v) for k, v in ANCHORS.items()}
    anc.update(
        house_door=[(HOUSE_DOOR[0] + HOUSE_DOOR[1]) // 2, LANE],
        sugar=[434, 152],
        stall_box=[STALL[0], 100, STALL[1], LANE],
        cafe_tables=[[x, LANE] for (x, face) in CAFE_TABLES],
        scaffold_box=[SCAF[0] - 4, 38, SCAF[1] + 4, LANE],
        socket_box=[SOCKET[0] - 4, SOCKET[1] - 4, SOCKET[0] + 5, SOCKET[1] + 5],
        sun_dir=-1,
        lane_back=LANE)
    return anc


# ============================================================ 导出
def export(ex, BJ):
    tb = table()
    layers = P.export_layers(ex, BJ, tb)
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors())
    if ex.check_on:
        _checks(ex, BJ, st, tb)
    return st


def _checks(ex, BJ, st, tb):
    cfg = dict(title='卢克索', PW=PW, walk=WALK, near=near_img(), opaque_rows=(LANE, H), sky=sky_img(),
               states=[{}], stand=STAND, required=REQUIRED, size_limit=350 * 1024, cams_step=40,
               flat=(0, PW, WALK[0], WALK[1] + 1, 22, 0.012), flat_skip=[])
    P.common_checks(ex, BJ, st, tb, cfg)
    # 插座要“突兀”：面板比周围的旧墙亮得多（面板均值 − 周围一圈均值）
    a = np.array(near_img()).astype(np.float32)
    lum = P._lum(a[..., :3])
    sx, sy = SOCKET
    panel = lum[sy - 2:sy + 3, sx - 2:sx + 3].mean()
    # 周围 = 插座上方和左右两边的墙（下方 y 146 起是路沿，不算）
    ring = np.concatenate([lum[sy - 9:sy - 5, sx - 9:sx + 10].ravel(), lum[sy - 3:sy + 4, sx - 10:sx - 5].ravel(),
                           lum[sy - 3:sy + 4, sx + 6:sx + 11].ravel()]).mean()
    ex.checked('插座面板比旧墙亮（面板 %.0f − 周围 %.0f ≥ 40）' % (panel, ring), 0 if panel - ring >= 40 else 1)
    # 光从右边来：一扇百叶窗 / 楼的右沿比左沿亮（翻过来以后）
    ex.note('光从右上来（近景 / 中景是镜像画再翻的），剧情的长影子往左，和墙上的影子同向')


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch9', 'after')
    os.makedirs(od, exist_ok=True)
    full = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    for cx in (0, 320, 640):
        full.paste(compose(cx, 0.5), (cx, 0))
    full.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'luxor_town_solo.png'))
    print('ok')
