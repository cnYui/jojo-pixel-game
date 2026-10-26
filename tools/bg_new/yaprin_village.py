# -*- coding: utf-8 -*-
r"""yaprin_village —— 第6章「亚普林村」：阿拉伯沙漠边上的小村（纳季德式土坯房、枣椰树、简易土跑道），下午。
2026-10-18 ch6-misc 组按体验版精度重画（改前是 later_stages.town(11, 640, 'village')：一排平涂的方块房 + 三角顶）。

地图 640 宽、ground 160、可走带 y 148–176（人走在压实的沙土路上，对比压得很低）；侧视平视，下午的太阳在左上，
影子往右下。墙脚 = 地面后沿 y 146，房子 / 摊子 / 井都画在 y ≤ 145（可走带里只有平地、脚印、车辙这类平的东西）。
从左到右（世界坐标）：
  x 0–26      村口：一截被风沙磨圆的矮泥墙 + 一口给路人喝水的陶罐（木架上），一棵枣椰树（树冠 strip 摆）
              （anchors.arrive）
  x 26–130    骆驼栏：棕榈叶搭的遮阳棚（三根木杆）、栏后一道棕榈叶编的篱笆（深色，骆驼才跳得出来）、木栅栏
              （立柱 + 两道横杆，绳子绑着）、栏里两头趴着的单峰骆驼（一头朝左一头朝右、一头驼峰上搭着红毯，strip 嚼草：
              下巴左右磨、偶尔抖耳朵、甩尾巴）、草料槽、立柱上挂的一卷绳子和皮水桶；栏后一棵枣椰树（anchors.camel_pen）
  x 130–196   杂货摊：草席棚（三根歪木杆撑着、席边挂着草须）、木柜台（阿拉伯咖啡壶 dallah、小杯、叠好的布、一筐椰枣、
              陶碗）、棚下挂着的布匹（strip 飘）和一盏马灯、柜台左边地上两口大水罐（zir）、靠墙一卷地毯；
              摊子后面是 H1 院墙（anchors.stall）
  x 196–246   H1 两层土坯房：屋顶一排三角垛 + 白石膏饰带、两排伸出墙的木梁头、二楼两扇蓝绿木百叶窗、一排三角通风孔、
              刷着三角花纹的蓝绿木门、带木格栅的小窗、两根木排水槽（下面一道水渍）；屋顶晾衣绳（strip）+ 电视天线
              （anchors.kids 在门前）
  x 246–304   H2：左边一截院墙 + 泥烤炉 tannur（炊烟 strip）+ 一捆柴 + 一小堆草料（山羊在啃：strip）；右边一层土坯房、
              蓝绿木门（anchors.mother 在门前）、窗洞、门边一串晒干的红辣椒、屋顶晒椰枣的草席 + 水罐
  x 304–336   H3 矮库房：木板门、靠墙的梯子（搭上屋顶）、扫帚；门前三只母鸡在啄食（strip）；房后一棵枣椰树（strip）
  x 336–380   井：石砌井台、两根木柱 + 横梁 + 滑轮、井绳吊着一只木桶；右边一个石头饮水槽；井边的地是湿的（anchors.well）
  x 380–448   小清真寺：土坯宣礼塔（往上收、几个窄窗、木挑台、顶上的小亭 + 尖顶 + 新月、两只喇叭）、礼拜堂（三角垛、
              木梁头、尖拱绿木门、两扇小拱窗、净身的水龙头 + 小水池、门口几双拖鞋）（anchors.mosque）
  x 448–546   卖飞机的商人的铁皮棚：瓦楞铁皮顶（锈斑）、三根木柱、铁皮后墙（几块颜色不一样的铁皮拼的）、
              棚里：一支靠墙的木螺旋桨、备用机轮、挂工具的木板、工作台 + 台钳、油壶；棚檐下挂一块手绘招牌（白底 + 红色小飞机）；
              棚右边三只汽油桶（红 / 蓝 + 横放在上面的黄桶）、漏斗；棚左一根电线杆（anchors.merchant、hangar）
  x 546–640   压平的土跑道：颜色更浅、更平，两道车辙，跑道前后沿一排刷白的石块；跑道起点一根风向袋杆（strip）；
              停机位（anchors.cessna，x 555–615）只有平地 + 两块油渍（塞斯纳是剧情道具）；右端出村（anchors.exit）
头顶：x 129 / 336 / 452 三根木电线杆之间拉着两根电线（y 30–46，在对白框后面也不要紧）。
光：太阳在左上（下午），墙左沿亮、右沿暗，木梁头 / 窗台 / 遮阳棚往右下投影；可走带后面 y 108–145 压了对比。

图层（从后往前）：
  sky       static           320×180 下午的天（上蓝、地平线发暖白）+ 左上的太阳
  clouds    wrap   k 0.1  vx 1.5   几缕高空的薄云（640 循环）
  far       pano   k 0.25          远景 400 宽：平顶的砂岩断崖（层理）、前面一道道沙丘（罩雾）
  mid       pano   k 0.55          中景 496 宽：村后的枣椰林、后排的土坯房、一座圆形泥瞭望塔、跑道外的大沙丘、一直铺到 y 150 的沙地
  birds     clouds                 两只在高处盘旋的鸢
  near      pano   k 1             整条村路（640 宽）
  camels    strip  k 1             骆驼栏：两头骆驼嚼草 + 栅栏（栅栏在骆驼前面，所以一起烘进帧里）（8 帧 @4 fps）
  palm_0…2  strip  k 1             三棵枣椰树的树冠（8 帧 @4 fps）
  cloths    strip  k 1             杂货摊棚下挂的布（8 帧 @4 fps）
  laundry   strip  k 1             H1 屋顶的晾衣绳（8 帧 @4 fps）
  smoke     strip  k 1             泥烤炉的炊烟（往右飘，和风向袋同一个风向）（8 帧 @4 fps）
  goat      strip  k 1             啃草的山羊（8 帧 @4 fps）
  hens      strip  k 1             H3 门前啄食的母鸡（8 帧 @4 fps）
  sock      strip  k 1             跑道起点的风向袋（8 帧 @4 fps）
锚点：arrive [40,164]、camel_pen [80,156]、stall [160,152]、kids [230,164]、mother [292,160]、well [350,154]、
      mosque [410,120]、merchant [470,160]、hangar [500,140]、cessna [585,162]、exit [626,162]（规格表）；另导出
      walk_x、runway [546,146,640,180]、parking [555,146,615,176]（停机位留空的框）、windsock [548,58]、oven [255,131]、
      camels [[55,141],[98,141]]（两头骆驼身子中心）、palms（三棵树冠中心）、doors（四扇门的框）、well_box、stall_box、
      shed_box、minaret（新月尖）、lane_back 146。
key：无（规格没有要求）。
单独运行：python -B tools\bg_new\yaprin_village.py → tools\bg_new\_preview\ch6\after\yaprin_village_solo_*.png
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
    """ch6 组共用的小工具 / 自检（tools\\bg_new\\ch6_parts.py，按路径加载，不改 sys.path 顺序）。"""
    key = 'bg_new_ch6_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'ch6_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
V = P.V
C = A._c4
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
mul_box, cast_shadow, mottle, haze, opaque = P.mul_box, P.cast_shadow, P.mottle, P.haze, P.opaque
SHADOW_MUL, SOFT_MUL = P.SHADOW_MUL, P.SOFT_MUL
fidx = P.fidx

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (148, 176)
LANE = 146                    # 墙脚 = 地面后沿（房子画到 145）
CLOUD_K, CLOUD_VX = 0.1, 1.5
FAR_K, MID_K = 0.25, 0.55
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 400
MIDW = W + int(math.ceil((PW - W) * MID_K))      # 496
N_ANIM, FPS_ANIM = 8, 4.0

PEN = (26, 130)
STALL = (130, 196)
H1 = (196, 246)
H2W = (246, 266)              # H2 的院墙段
H2 = (266, 304)
H3 = (304, 336)
WELL = (338, 362)
MOSQUE = (396, 448)
MINARET = (380, 398)
SHED = (454, 544)
RUNWAY = (546, 640)
POLES = (129, 336, 452)
SOCK = (547, 58)              # 风向袋杆顶（套环）：放在跑道起点，影子落不到停机位
OVEN = (255, 131)             # 泥烤炉炉口
PALMS = [(11, 146, 58, 3, 0, 23), (114, 146, 62, -4, 1, 21), (330, 104, 60, 2, 2, 22)]   # (树干 x, 树脚 y, 树冠 y, 弯, 种子, 叶长)
CAMEL_XY = [(26, 112, 1), (80, 112, -1)]          # 骆驼精灵左上角 (x, y, 朝向 1 = 朝左)
PARK = (555, 615)

ANCHORS = dict(
    arrive=[40, 164],          # 村口
    camel_pen=[80, 156],       # 骆驼栏前
    stall=[160, 152],          # 杂货摊前
    kids=[230, 164],           # H1 门前（小孩）
    mother=[292, 160],         # H2 门前（抱婴儿的妇人）
    well=[350, 154],           # 井前
    mosque=[410, 120],         # 清真寺（物件中心）
    merchant=[470, 160],       # 铁皮棚前（卖飞机的商人）
    hangar=[500, 140],         # 铁皮棚（物件中心偏下）
    cessna=[585, 162],         # 塞斯纳停机位中心（底图只有平地）
    exit=[626, 162],           # 右端出村
    walk_x=[8, 632],
)
STAND = ('arrive', 'camel_pen', 'stall', 'kids', 'mother', 'well', 'merchant', 'cessna', 'exit')

# ============================================================ 调色（下午、暖）
INK = (66, 44, 36)
SKY_STOPS = [(70, 126, 196), (98, 154, 212), (142, 184, 222), (192, 206, 212), (236, 220, 188)]
HAZE = (226, 212, 188)
ADOBE_HI = (230, 194, 142)
ADOBE = (208, 166, 116)       # 纳季德的赭色泥墙
ADOBE_S = (184, 142, 98)
ADOBE_D = (148, 108, 74)
ADOBE_K = (106, 76, 54)
ADOBE2 = (198, 150, 104)      # 偏红的泥
ADOBE3 = (218, 184, 136)      # 偏黄、掺沙多的泥
GYPSUM = (240, 232, 214)      # 白石膏饰带 / 门窗套
GYPSUM_S = (214, 204, 186)
TEAL_HI = (96, 176, 168)
TEAL = (54, 138, 138)         # 蓝绿木门
TEAL_D = (34, 94, 102)
WOOD_HI, WOOD, WOOD_D, WOOD_K = V.WOOD_HI, V.WOOD, V.WOOD_D, V.WOOD_K
DARK_IN = (62, 46, 42)
GRD = (220, 194, 152)         # 压实的沙土路
GRD_S = (210, 183, 141)
GRD_HI = (228, 204, 164)
RUN = (226, 206, 170)         # 跑道（压得更平、颜色更浅）
RUN_S = (216, 196, 160)
RUN_HI = (232, 214, 180)
STRAW = (222, 196, 120)
STRAW_D = (186, 154, 86)
TRUNK = (150, 112, 74)
TRUNK_HI = (182, 142, 98)
TRUNK_D = (104, 76, 52)
PALM_PAL = ((38, 92, 52), (66, 134, 64), (118, 178, 88), (176, 142, 80), (128, 98, 58), (196, 106, 40), (146, 70, 32))
CAMEL = ((234, 198, 148), (208, 162, 108), (172, 126, 82), (112, 80, 54))       # 亮 / 中 / 暗 / 描边
IRON = (150, 152, 150)
IRON_HI = (196, 198, 194)
IRON_D = (104, 106, 108)
RUST = (168, 96, 56)
RUST_D = (126, 70, 44)


# ============================================================ 天空 / 云
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), SKY_STOPS, bands=12)
    A._glow(im, 40, 26, 48, 40, (255, 240, 206), 70, rings=5)
    d = ImageDraw.Draw(im)
    d.ellipse((34, 20, 46, 32), fill=C((255, 244, 214)))
    d.ellipse((36, 22, 44, 30), fill=C((255, 252, 238)))
    return im


@lru_cache(maxsize=1)
def clouds_img():
    """640 循环：几缕高空的薄云（沙漠里云少，拉成长条）+ 两朵小积云。"""
    im = A._new(640, 64)
    d = ImageDraw.Draw(im)
    for i in range(7):                                             # 卷云：两头尖、中间厚的长条 + 一缕细丝
        cx = (i + hrange(0.1, 0.9, i, 1)) * 640 / 7
        y = int(hrange(6, 40, i, 2))
        L = int(hrange(34, 76, i, 3))
        tilt = hrange(-0.05, 0.05, i, 4)
        for k in range(L):
            u = k / (L - 1)
            th = int(round(2.6 * math.sin(math.pi * u) ** 0.7 * hrange(0.75, 1.0, i, k // 6, 5)))
            if th <= 0:
                continue
            yy = int(round(y + (k - L / 2) * tilt))
            for dx in (-640, 0, 640):
                x = int(cx - L / 2 + k + dx)
                if not 0 <= x < 640:
                    continue
                for r in range(th):
                    c = (250, 251, 252) if r == 0 else ((236, 242, 248) if r < th - 1 else (214, 226, 240))
                    px(d, x, yy + r, c)
                if 0.15 < u < 0.85 and hash01(i, k, 6) < 0.55:           # 细丝（淡）
                    px(d, x + 3, yy - 2, (222, 234, 246))
    pal = ((255, 255, 252), (240, 238, 234), (218, 218, 224), (198, 200, 212))
    for i in range(2):
        w = hrange(34, 52, i, 11)
        cl = A._cloud_sprite(w, w * 0.32, 700 + i, pal)
        cx = (i + 0.3) * 320
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), 64 - cl.height - int(hrange(2, 10, i, 12)))
    return im


BIRDS = [(34, -3.6, 0.3, 80), (48, -2.4, 0.22, 300)]          # (y, vx, k, x0)：两只鸢


# ============================================================ 远景（k 0.25，400 宽）
def _ridge(x, seed, lo, hi, scale):
    """一维山脊线：几层正弦叠起来（确定、平滑）。"""
    v = 0.0
    for k in range(4):
        f = (k + 1) * scale
        v += math.sin(x * f + hrange(0, 6.28, seed, k)) / (k + 1)
    return lo + (hi - lo) * (0.5 + 0.35 * v)


@lru_cache(maxsize=1)
def far_img():
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    # 平顶的砂岩断崖（图瓦伊克山那种）：一整道平顶、正面是一层层的层理和冲沟，左亮右暗
    top_c, face_c, face_d, band_c = (214, 170, 140), (190, 140, 116), (164, 118, 100), (176, 128, 106)
    for x in range(FARW):
        top = int(round(92 + 6 * math.sin(x * 0.011 + 1.3) + 3 * math.sin(x * 0.047) + (8 if 150 < x < 196 else 0)))
        if 150 < x < 196:                                           # 一处缺口（冲出来的峡谷）
            top = int(round(top + 6 * math.sin((x - 150) / 46 * math.pi)))
        hl(d, x, x, top, top_c)
        for y in range(top + 1, 126):
            c = face_c
            if (y - top) % 5 == 0:
                c = band_c
            if hash01(x // 3, y // 6, 3) < 0.18:
                c = face_d
            px(d, x, y, c)
        if (x * 7 + 3) % 23 < 2:                                    # 冲沟（竖的暗缝）
            for y in range(top + 2, 120):
                if hash01(x, y, 4) < 0.7:
                    px(d, x, y, face_d)
    # 前面一道道沙丘（亮面朝左、背光面朝右）
    for (base, amp, sc, sd, col, shd) in ((118, 8, 0.021, 1, (236, 202, 160), (214, 176, 138)),
                                          (124, 6, 0.033, 2, (232, 196, 152), (208, 168, 130))):
        for x in range(FARW):
            y0 = int(round(_ridge(x, sd, base - amp, base + 2, sc)))
            y1 = int(round(_ridge(x + 2, sd, base - amp, base + 2, sc)))
            for y in range(y0, 140):
                px(d, x, y, shd if y1 < y0 and y < y0 + 4 else col)
            px(d, x, y0, lt(col, 0.3))
    rect(d, 0, 132, FARW - 1, 150, (230, 200, 160))
    ys = np.arange(H, dtype=np.float32)[:, None]
    amt = np.clip(0.48 + (ys - 90) / 60 * 0.1, 0.44, 0.58)
    return haze(im, amt, HAZE)


# ============================================================ 枣椰树
def palm_trunk(d, x, base, top, lean, scale=1.0):
    """枣椰树树干：一节节的叶痕（每 3 行一圈暗）、左亮右暗，往上收细、往 lean 那边弯。返回树冠中心。"""
    n = max(1, base - top)
    for i in range(n + 1):
        s = i / n
        cx = x + lean * s * s
        y = base - i
        w = (2.8 - 1.1 * s) * scale
        x0, x1 = round(cx - w), round(cx + w - 1)
        hl(d, x0, x1, y, TRUNK)
        px(d, x0, y, TRUNK_HI)
        px(d, x1, y, TRUNK_D)
        if i % 3 == 0:
            hl(d, x0 + 1, x1, y, TRUNK_D)
        elif i % 3 == 1 and x1 - x0 > 2:
            px(d, x0 + 1, y, lt(TRUNK_HI, 0.15))
    return (round(x + lean), top)


def palm_crown(d, cx, cy, size, f, seed, pal=PALM_PAL, amp=3.0, dead=True):
    """枣椰树冠：9 片羽状叶（叶轴往外拱、叶尖往下垂，小叶往下挂、一明一暗），f 帧随风轻摆（风往右吹：右边几片摆得多）。
    底下一圈枯黄的老叶 + 两串橙褐色的椰枣。"""
    dkk, mid, hi, dead_c, dead_d, date_c, date_d = pal
    ph = math.tau * f / N_ANIM
    if dead:
        for k, deg in enumerate((-70, -100, -120, -55)):            # 枯叶：贴着树干往下垂
            a = math.radians(deg + 4 * math.sin(ph + k))
            L = size * 0.42
            for j in range(int(L)):
                u = j / L
                x = cx + math.cos(a) * L * u * 0.7
                y = cy + 2 + math.sin(-a) * L * u
                px(d, round(x), round(y), dead_c if j % 2 else dead_d)
        for (dx, sd) in ((-3, 1), (2, 2)):                             # 椰枣串
            for j in range(9):
                x = cx + dx + int(hrange(-2, 2, seed, sd, j))
                y = cy + 3 + j // 2 + int(hrange(0, 2, seed, sd, j, 1))
                px(d, x, y, date_c if hash01(seed, sd, j, 2) < 0.6 else date_d)
    fronds = [(168, 1.0), (140, 0.9), (112, 0.66), (84, 0.6), (56, 0.8), (24, 1.0), (196, 0.82), (-12, 0.86), (98, 0.42)]
    for k, (deg, lf) in enumerate(fronds):
        side = math.cos(math.radians(deg))
        sw = amp * (1.0 + 0.5 * max(0.0, side)) * math.sin(ph + k * 0.9 + seed)
        a = math.radians(deg - sw)
        L = size * lf * (0.9 + 0.2 * hash01(seed, k))
        droop = 0.62 + 0.16 * hash01(seed, k, 2)
        steps = max(4, int(L))
        pts = []
        for j in range(steps + 1):
            u = j / steps
            pts.append((cx + math.cos(a) * L * u, cy - math.sin(a) * L * u + droop * L * u * u))
        for j in range(2, steps + 1):                                   # 小叶（挂在叶轴下面，往回斜）
            u = j / steps
            x, y = pts[j]
            ln = 1 + round(3.4 * math.sin(math.pi * min(1.0, u * 1.08)))
            back = -1 if pts[j][0] > pts[j - 1][0] else 1
            col = dkk if j % 2 else mid
            d.line((round(x), round(y) + 1, round(x + back * ln * 0.6), round(y) + ln), fill=C(col))
        for j in range(1, len(pts)):
            d.line((round(pts[j - 1][0]), round(pts[j - 1][1]), round(pts[j][0]), round(pts[j][1])), fill=C(mid))
            if j % 2 == 0 and j < len(pts) - 2 and pts[j][1] < cy + 2:
                px(d, round(pts[j][0]), round(pts[j][1]) - 1, hi)
    d.ellipse((cx - 2, cy - 1, cx + 2, cy + 2), fill=C(dkk))
    px(d, cx - 1, cy - 1, mid)


@lru_cache(maxsize=None)
def palm_box(i):
    """树冠 strip 的框：把这棵树 8 帧都画一遍取并集（叶尖 / 小叶不会漏到框外）。"""
    (x, base, top, lean, sd, L) = PALMS[i]
    acc = None
    for f in range(N_ANIM):
        im = A._new(PW, H)
        palm_crown(ImageDraw.Draw(im), x + lean, top, L, f, sd)
        bb = im.getbbox()
        acc = bb if acc is None else (min(acc[0], bb[0]), min(acc[1], bb[1]), max(acc[2], bb[2]), max(acc[3], bb[3]))
    return acc


# ============================================================ 中景（k 0.55，496 宽）
def mini_house(im, x, w, top, base, col, seed):
    """后排的土坯房（远一点、小一点）：墙面斑驳、一排三角垛、几个暗窗洞、一排木梁头。"""
    d = ImageDraw.Draw(im)
    rect(d, x, top, x + w - 1, base, col)
    mottle(im, (x, top, x + w - 1, base), col, dk(col, 0.92), lt(col, 0.1), seed, cell=3)
    d = ImageDraw.Draw(im)
    vl(d, x, top, base, lt(col, 0.18))
    vl(d, x + w - 1, top, base, dk(col, 0.8))
    for xx in range(x + 1, x + w - 3, 4):
        px(d, xx + 1, top - 2, col)
        hl(d, xx, xx + 2, top - 1, col)
        px(d, xx, top - 1, lt(col, 0.15))
    hl(d, x, x + w - 1, top + 1, lt(GYPSUM, 0.0))
    for xx in range(x + 2, x + w - 2, 5):
        px(d, xx, top + 4, dk(col, 0.55))
    for yy in range(top + 8, base - 6, 11):
        for xx in range(x + 3, x + w - 4, 7):
            if hash01(seed, xx, yy) < 0.6:
                rect(d, xx, yy, xx + 2, yy + 3, dk(col, 0.5))


def tower(im, cx, top, base, col, seed):
    """圆形泥瞭望塔（burj）：往上收的圆柱，竖着的明暗（左亮右暗）、几道窄枪眼、顶上一圈三角垛。"""
    d = ImageDraw.Draw(im)
    for y in range(top, base + 1):
        u = (y - top) / max(1, base - top)
        hw = 5 + 3 * u
        for x in range(int(cx - hw), int(cx + hw) + 1):
            v = (x - (cx - hw)) / (2 * hw)
            c = lt(col, 0.16) if v < 0.25 else (col if v < 0.62 else (dk(col, 0.86) if v < 0.85 else dk(col, 0.74)))
            px(d, x, y, c)
    for xx in range(int(cx - 5), int(cx + 5), 3):
        hl(d, xx, xx + 1, top - 2, col)
        px(d, xx, top - 3, lt(col, 0.1))
    for (yy, xx) in ((top + 8, cx - 1), (top + 20, cx + 1), (top + 32, cx - 2)):
        vl(d, int(xx), yy, yy + 4, dk(col, 0.45))
    hl(d, int(cx - 6), int(cx + 6), top + 2, lt(col, 0.25))


@lru_cache(maxsize=1)
def mid_img():
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    # 一直铺到 y 150 的沙地（近景的路后沿在 146，跑道那段后面什么都没有，要接得上）
    gradient(im, (0, 118, MIDW, 152), [(230, 206, 168), (224, 198, 158), (220, 194, 152)], bands=4)
    d = ImageDraw.Draw(im)
    # 跑道外的大沙丘（中景 x 330 以后：镜头在最右时，跑道后面看到的就是这一段）
    for x in range(300, MIDW):
        u = (x - 300) / (MIDW - 300)
        y0 = int(round(118 - 20 * math.sin(min(1.0, u * 1.35) * math.pi) ** 1.3 - 4 * math.sin(x * 0.07)))
        y1 = int(round(118 - 20 * math.sin(min(1.0, (u + 0.004) * 1.35) * math.pi) ** 1.3 - 4 * math.sin((x + 1) * 0.07)))
        shade = y1 > y0
        for y in range(y0, 132):
            c = (226, 192, 148) if not shade else (206, 170, 132)
            if (y - y0) > 6:
                c = (228, 200, 158)
            px(d, x, y, c)
        px(d, x, y0, (244, 220, 180))
        if (x + 3) % 9 == 0:                                         # 风纹
            for k in range(3):
                px(d, x + k, y0 + 5 + (x % 5), (214, 182, 140))
    # 跑道外沙丘上半埋的旧飞机残骸（中景 x 420–452）：一截斜插在沙里的机翼、竖着的尾翼、几根露出来的肋条
    wx, wy = 420, 112
    d.polygon([(wx, wy + 8), (wx + 20, wy + 2), (wx + 22, wy + 4), (wx + 3, wy + 10)], fill=C((176, 172, 166)))
    hl(d, wx + 2, wx + 19, wy + 5, (200, 196, 190))
    d.polygon([(wx + 26, wy + 9), (wx + 30, wy - 4), (wx + 34, wy - 4), (wx + 33, wy + 9)], fill=C((162, 160, 156)))
    vl(d, wx + 31, wy - 3, wy + 6, (196, 80, 60))
    for k in range(4):
        vl(d, wx + 6 + k * 4, wy + 6 - k, wy + 9, (130, 110, 90))
    for x in range(wx - 2, wx + 38):                                # 埋着它的沙
        hl(d, x, x, wy + 9 + int(round(1.5 * math.sin(x * 0.3))), (230, 202, 160))
    # 后排的土坯房 + 瞭望塔（只在村子这段：中景 x 20–300）
    houses = [(20, 22, 104), (44, 18, 112), (64, 26, 98), (96, 20, 108), (118, 24, 102), (150, 18, 110),
              (226, 22, 104), (250, 28, 98), (282, 18, 108)]
    pal = [ADOBE, ADOBE3, ADOBE2, (212, 174, 126)]
    for i, (x, w, top) in enumerate(houses):
        mini_house(im, x, w, top, 134, pal[i % len(pal)], 70 + i)
    tower(im, 200, 70, 134, (204, 160, 112), 7)
    d = ImageDraw.Draw(im)
    # 村后的枣椰林（树干 + 树冠，静止；颜色淡一点）
    mp = ((56, 100, 62), (82, 136, 76), (126, 172, 98), (172, 146, 92), (130, 104, 70), (190, 116, 56), (150, 86, 46))
    for i in range(16):
        x = int(hrange(4, 340, i, 81))
        top = int(hrange(64, 92, i, 82))
        cx, cy = palm_trunk(d, x, 134, top, int(hrange(-5, 5, i, 83)), scale=0.8)
        palm_crown(d, cx, cy, int(hrange(13, 18, i, 84)), 0, 90 + i, pal=mp, dead=False)
    return haze(im, 0.24, HAZE)


# ============================================================ 近景：地面
def draw_ground(im):
    """压实的沙土路（146–179）：底色 + 很淡的斑驳；跑道那段（x 546 起）颜色更浅、更平，接缝处按 Bayer 抖开；
    脚印、骆驼蹄印、稻草屑、车辙、刷白的石块、停机位的油渍、井边的湿地。都压得很淡（可走带对比低）。"""
    d = ImageDraw.Draw(im)
    rect(d, 0, LANE, PW - 1, H - 1, GRD)
    a = np.array(im)
    bay = A._bayer(PW, H)
    for x in range(528, PW):
        u = min(1.0, max(0.0, (x - 530) / 18.0))
        col = a[LANE:, x]
        m = bay[LANE:, x] < u
        col[m, :3] = RUN
    im.paste(Image.fromarray(a, 'RGBA'))
    mottle(im, (0, LANE + 1, PW - 1, H - 1), GRD, GRD_S, GRD_HI, 61, cell=6, lo=0.24, hi=0.78)
    mottle(im, (0, LANE + 1, PW - 1, H - 1), RUN, RUN_S, RUN_HI, 62, cell=8, lo=0.2, hi=0.84)
    d = ImageDraw.Draw(im)
    # 墙脚线（后沿）：墙下一道暗、空地处淡
    for x in range(PW):
        c = im.getpixel((x, LANE))[:3]
        px(d, x, LANE, dk(c, 0.9))
    # 风吹出来的细沙纹（只在左端和跑道外沿，很淡）
    for (xa, xb) in ((0, 24), (600, 640)):
        for y in range(150, 178, 5):
            for x in range(xa, xb):
                if (x + y * 2) % 7 < 3 and hash01(x, y, 3) < 0.7:
                    c = im.getpixel((x, y))[:3]
                    px(d, x, y, dk(c, 0.96))
    # 脚印（成对的小暗点，沿着几条走出来的路）
    for i in range(70):
        x = int(hrange(30, 540, i, 11))
        y = int(hrange(150, 175, i, 12))
        c = im.getpixel((x, y))[:3]
        px(d, x, y, dk(c, 0.94))
        px(d, x + 3, y + 1, dk(c, 0.94))
    # 骆驼蹄印（宽的小椭圆，栏门口一片）
    for i in range(14):
        x = int(hrange(40, 128, i, 13))
        y = int(hrange(149, 162, i, 14))
        c = im.getpixel((x, y))[:3]
        hl(d, x, x + 2, y, dk(c, 0.93))
        px(d, x + 1, y + 1, dk(c, 0.95))
    # 稻草屑（栏前 / 摊前）
    for (xa, xb, n) in ((26, 136, 40), (130, 196, 18)):
        for i in range(n):
            x = int(hrange(xa, xb, i, xa, 15))
            y = int(hrange(147, 160, i, xa, 16))
            c = im.getpixel((x, y))[:3]
            px(d, x, y, mix(STRAW, c, 0.6))
            if hash01(i, xa, 17) < 0.4:
                px(d, x + 1, y, mix(STRAW_D, c, 0.62))
    # 井边的湿地（深一点的一片）
    for x in range(334, 382):
        for y in range(LANE, 152):
            u = abs(x - 356) / 26 + (y - LANE) / 7
            if u < 1 and hash01(x, y, 18) < 1.1 - u:
                c = im.getpixel((x, y))[:3]
                px(d, x, y, dk(c, 0.92))
    # 跑道：两道车辙、前后沿一排刷白的石块、停机位两块油渍
    for (y0, sd) in ((157, 1), (169, 2)):
        for x in range(536, PW):
            y = y0 + (1 if (x // 37 + sd) % 3 == 0 else 0)
            if hash01(x, sd, 19) < 0.62:
                c = im.getpixel((x, y))[:3]
                px(d, x, y, dk(c, 0.94))
            if hash01(x, sd, 20) < 0.3:
                c = im.getpixel((x, y + 1))[:3]
                px(d, x, y + 1, dk(c, 0.96))
    for x in range(RUNWAY[0] + 4, PW, 13):
        for (yy, hh) in ((LANE - 1, 2), (176, 2)):
            rect(d, x, yy, x + 2, yy + hh - 1, (246, 244, 236))
            px(d, x + 2, yy + hh - 1, (204, 200, 190))
            px(d, x, yy, (255, 255, 252))
    for (cx, cy, rx, ry) in ((574, 166, 6, 2), (598, 163, 4, 1)):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / max(1, ry)) ** 2 <= 1 and hash01(x, y, 21) < 0.8:
                    c = im.getpixel((x, y))[:3]
                    px(d, x, y, dk(c, 0.9))
    # 几颗小石子
    for i in range(30):
        x = int(hrange(0, PW, i, 22))
        y = int(hrange(150, 178, i, 23))
        if PARK[0] - 4 < x < PARK[1] + 4:
            continue
        c = im.getpixel((x, y))[:3]
        px(d, x, y, dk(c, 0.84))
        px(d, x, y - 1, lt(c, 0.2))


# ============================================================ 近景：泥墙零件
def mud_wall(im, x0, x1, top, base, col, seed, streaks=3, cell=4):
    """泥墙面：底色 + 斑驳 + 往下淌的雨水冲刷痕 + 麦秸 / 碎石点；左沿亮、右沿暗（太阳在左上）；墙脚溅上去的湿泥。x1 不含。"""
    d = ImageDraw.Draw(im)
    rect(d, x0, top, x1 - 1, base, col)
    mottle(im, (x0, top, x1 - 1, base), col, dk(col, 0.92), lt(col, 0.1), seed, cell=cell, streaks=streaks)
    d = ImageDraw.Draw(im)
    for i in range(int((x1 - x0) * (base - top) / 36)):
        x = int(hrange(x0 + 1, x1 - 1, seed, i, 1))
        y = int(hrange(top + 2, base, seed, i, 2))
        px(d, x, y, dk(col, 0.84) if hash01(seed, i, 3) < 0.6 else lt(col, 0.2))
    vl(d, x0, top, base, lt(col, 0.22))
    vl(d, x0 + 1, top, base, lt(col, 0.1))
    vl(d, x1 - 1, top, base, dk(col, 0.8))
    for x in range(x0, x1):
        for y in range(base - 4, base + 1):
            if hash01(seed, x, y, 4) < 0.25 + 0.17 * (y - base + 4):
                px(d, x, y, dk(col, 0.88))
    return d


def crenels(im, x0, x1, y, col, step=6):
    """屋顶女儿墙上一排三角垛（纳季德土房的 shurfa）：每个底宽 5、高 3，左亮右暗；下面一道白石膏饰带。y = 墙顶。"""
    d = ImageDraw.Draw(im)
    for x in range(x0 + 1, x1 - 4, step):
        for r in range(3):
            a, b = x + 2 - r, x + 2 + r
            yy = y - 3 + r
            hl(d, a, b, yy, col)
            px(d, a, yy, lt(col, 0.22))
            px(d, b, yy, dk(col, 0.82))
    hl(d, x0, x1 - 1, y, lt(col, 0.2))
    hl(d, x0, x1 - 1, y + 2, GYPSUM)
    hl(d, x0, x1 - 1, y + 3, GYPSUM_S)
    mul_box(im, (x0 + 1, y + 4, x1 - 1, y + 4), SHADOW_MUL, level=0.5)


def beam_ends(im, x0, x1, y, step=7, off=3):
    """伸出墙的木梁头（vigas）：一排 2×2 的圆木头，左上亮、右下暗，墙上往右下落一点影。"""
    d = ImageDraw.Draw(im)
    for x in range(x0 + off, x1 - 3, step):
        cast_shadow(im, [(x + 1, y + 2), (x + 3, y + 2), (x + 4, y + 4), (x + 2, y + 4)])
        d = ImageDraw.Draw(im)
        rect(d, x, y, x + 1, y + 1, WOOD)
        px(d, x, y, WOOD_HI)
        px(d, x + 1, y + 1, WOOD_K)
    return d


def spout(im, x, y, length=5):
    """木排水槽（从屋顶伸出来）：一截往右下斜的木槽，下面墙上一道深色水渍。"""
    d = ImageDraw.Draw(im)
    for k in range(length):
        px(d, x + k, y + k // 3, WOOD_D)
        px(d, x + k, y + k // 3 - 1, WOOD_HI if k < 3 else WOOD)
    for k in range(int(hrange(10, 22, x, y))):
        c = im.getpixel((x + length - 1, y + 2 + k))[:3]
        if hash01(x, k, 9) < 0.85 - k * 0.03:
            px(d, x + length - 1 - (k // 9), y + 2 + k, dk(c, 0.88))


def tri_vents(im, x0, x1, y, step=7):
    """一排三角通风孔（纳季德墙上的小三角洞）：暗洞 + 下沿亮。"""
    d = ImageDraw.Draw(im)
    for x in range(x0, x1 - 4, step):
        for r in range(3):
            hl(d, x + 2 - r, x + 2 + r, y + r, DARK_IN)
        hl(d, x, x + 4, y + 3, lt(ADOBE, 0.25))


def win_hole(im, x, y, w, h, wall, grille=False):
    """小窗洞：白石膏窗套、屋里暗、上沿 / 左沿一道更暗（洞有深度）、窗台亮、窗台下落影；grille = 木格栅。"""
    d = ImageDraw.Draw(im)
    rect(d, x - 1, y - 1, x + w, y + h, GYPSUM_S)
    hl(d, x - 1, x + w, y - 1, GYPSUM)
    rect(d, x, y, x + w - 1, y + h - 1, DARK_IN)
    hl(d, x, x + w - 1, y, dk(DARK_IN, 0.7))
    vl(d, x, y, y + h - 1, dk(DARK_IN, 0.7))
    if grille:
        for xx in range(x + 1, x + w - 1, 2):
            vl(d, xx, y + 1, y + h - 1, WOOD)
        hl(d, x, x + w - 1, y + h // 2, WOOD_HI)
    hl(d, x - 1, x + w, y + h, lt(GYPSUM, 0.3))
    mul_box(im, (x, y + h + 1, x + w, y + h + 1), SHADOW_MUL)


def najdi_door(im, x, y, w, h, col=TEAL, seed=0):
    """纳季德木门：白石膏门套 + 门楣；两扇门板（竖木板缝）、上半截刷着一排排三角花纹（红 / 黄 / 白）、铁门环、
    门下一道门槛石；门洞左沿 / 上沿的墙影。y = 门顶，h 含门槛。"""
    d = ImageDraw.Draw(im)
    rect(d, x - 2, y - 3, x + w + 1, y + h - 1, GYPSUM_S)          # 门套
    hl(d, x - 3, x + w + 2, y - 3, GYPSUM)
    hl(d, x - 3, x + w + 2, y - 4, lt(GYPSUM, 0.4))
    vl(d, x - 2, y - 2, y + h - 1, GYPSUM)
    rect(d, x, y, x + w - 1, y + h - 2, col)
    hw = w // 2
    for xx in range(x + 2, x + w - 1, 3):                           # 竖木板缝
        vl(d, xx, y + 1, y + h - 3, dk(col, 0.82))
    vl(d, x + hw - 1, y, y + h - 2, dk(col, 0.6))
    vl(d, x + hw, y, y + h - 2, lt(col, 0.18))
    vl(d, x, y, y + h - 2, lt(col, 0.28))
    vl(d, x + w - 1, y, y + h - 2, dk(col, 0.7))
    hl(d, x, x + w - 1, y, dk(col, 0.62))                           # 门楣下的影
    pal = ((206, 64, 50), (238, 196, 70), (246, 240, 228))
    for row, yy in enumerate((y + 4, y + 9, y + 14)):               # 三角花纹（三排、颜色错开）
        for k, xx in enumerate(range(x + 1, x + w - 3, 4)):
            c = pal[(k + row + seed) % 3]
            hl(d, xx, xx + 2, yy + 1, c)
            px(d, xx + 1, yy, c)
        hl(d, x + 1, x + w - 2, yy + 2, dk(col, 0.75))
    for yy in (y + h // 2 + 3, y + h - 8):                         # 门板横带 + 铁钉
        hl(d, x + 1, x + w - 2, yy, dk(col, 0.72))
        for xx in range(x + 2, x + w - 2, 3):
            px(d, xx, yy - 1, (196, 200, 196))
    for xx in (x + hw - 3, x + hw + 2):                             # 门环
        d.ellipse((xx - 1, y + h // 2 - 2, xx + 1, y + h // 2), outline=C((70, 66, 64)))
    hl(d, x - 2, x + w + 1, y + h - 1, (190, 176, 150))             # 门槛石
    hl(d, x - 2, x + w + 1, y + h - 2, (214, 202, 178))
    cast_shadow(im, [(x, y), (x + w - 1, y), (x + w - 1, y + 2), (x, y + 2)], mul=SOFT_MUL)


def bricks_patch(im, x, y, w, h, col, seed):
    """泥皮掉了一块，露出里面的土坯砖：砖一层 3 行、灰缝错开，边缘不规则。"""
    d = ImageDraw.Draw(im)
    for r in range(h):
        u = r / max(1, h - 1)
        sh = math.sin(math.pi * u)
        a = x + int(round((1 - sh) * w * 0.3 + hrange(-1, 1, seed, r, 1)))
        b = x + w - 1 - int(round((1 - sh) * w * 0.3 + hrange(-1, 1, seed, r, 2)))
        for xx in range(a, b + 1):
            c = dk(col, 0.86) if r % 3 else dk(col, 0.72)
            if r % 3 and (xx + (r // 3) * 4) % 8 == 0:
                c = dk(col, 0.72)
            px(d, xx, y + r, c)


# ============================================================ 近景：村口 / 骆驼栏
def draw_entrance(im):
    """村口：一截被风沙磨圆的矮泥墙、墙根堆的沙、木架上一口给路人喝水的陶罐（盖着木盖、挂着铜杯）。"""
    d = mud_wall(im, 0, 24, 124, LANE - 1, ADOBE3, 11, streaks=2)
    for x in range(0, 24):                                          # 墙顶磨圆、缺口
        cut = int(round(2 * math.sin(x * 0.4) + (4 if 14 < x < 19 else 0)))
        for y in range(124, 124 + max(0, cut)):
            im.putpixel((x, y), (0, 0, 0, 0))
        y = 124 + max(0, cut)
        px(d, x, y, lt(ADOBE3, 0.25))
    bricks_patch(im, 4, 132, 9, 7, ADOBE3, 12)
    d = ImageDraw.Draw(im)
    for x in range(0, 14):                                          # 墙根的沙堆
        hh = int(round(5 * (1 - x / 14) ** 1.5))
        for y in range(LANE - hh, LANE):
            px(d, x, y, GRD_HI if y == LANE - hh else GRD)
    # 陶罐（木架上）
    jx = 20
    for (xx, yy) in ((jx - 3, 140), (jx + 4, 140)):
        vl(d, xx, yy, LANE - 1, WOOD_D)
    hl(d, jx - 4, jx + 5, 139, WOOD)
    d.ellipse((jx - 4, 128, jx + 5, 139), fill=C((178, 104, 70)))
    d.chord((jx - 4, 128, jx + 5, 139), 300, 60, fill=C((150, 84, 58)))
    px(d, jx - 2, 131, (214, 148, 110))
    px(d, jx - 2, 132, (206, 136, 98))
    hl(d, jx - 2, jx + 3, 127, WOOD_HI)
    hl(d, jx - 2, jx + 3, 126, WOOD)
    px(d, jx + 6, 132, (210, 170, 70))                              # 挂着的铜杯
    px(d, jx + 6, 133, (176, 130, 50))
    cast_shadow(im, [(jx + 5, 139), (jx + 8, 139), (jx + 9, LANE + 2), (jx + 4, LANE + 2)], mul=SOFT_MUL)


PEN_FLOOR = 136


def draw_pen_back(im):
    """骆驼栏的底子：栏里的地（铺着草）、棕榈叶遮阳棚（三根木杆 + 一层干棕榈叶，下沿参差）、草料槽。"""
    d = ImageDraw.Draw(im)
    # 栏后的棕榈叶篱笆（barasti）：一根根竖的干叶柄、两道横绑的木杆、上沿参差
    for x in range(PEN[0] - 2, PEN[1] + 1):
        top = 109 + int(round(2 * hash01(x // 2, 38))) + (1 if x % 5 == 0 else 0)
        k = x % 3
        c = (118, 98, 62) if k == 0 else ((140, 118, 76) if k == 1 else (100, 82, 54))
        if hash01(x, 39) < 0.12:
            c = (108, 112, 66)
        vl(d, x, top, PEN_FLOOR - 1, c)
        px(d, x, top, (176, 150, 98))
    for y in (116, 129):
        hl(d, PEN[0] - 2, PEN[1], y, (150, 112, 70))
        hl(d, PEN[0] - 2, PEN[1], y + 1, (84, 64, 44))
    rect(d, PEN[0] - 2, PEN_FLOOR, PEN[1], LANE - 1, GRD_S)
    for i in range(110):
        x = int(hrange(PEN[0], PEN[1], i, 31))
        y = int(hrange(PEN_FLOOR + 1, LANE, i, 32))
        px(d, x, y, STRAW if hash01(i, 33) < 0.5 else STRAW_D)
    hl(d, PEN[0] - 2, PEN[1], PEN_FLOOR, dk(GRD_S, 0.9))
    # 遮阳棚（棚顶；三根木杆在骆驼前面，画在 draw_fence 里）
    for x in range(24, 87):
        top = 100 + (1 if (x // 5) % 3 == 0 else 0)
        bot = 105 + int(round(2 * hash01(x, 34))) + (1 if x % 4 == 0 else 0)
        for y in range(top, bot + 1):
            c = (172, 150, 96) if (x + y) % 3 else (142, 122, 76)
            if y == top:
                c = (204, 184, 122)
            if (x * 3 + y) % 11 == 0:
                c = (120, 132, 72)                                    # 还带一点绿的叶片
            px(d, x, y, c)
        if hash01(x, 35) < 0.3:
            vl(d, x, bot + 1, bot + 2 + int(hash01(x, 36) * 3), (150, 128, 80))
    cast_shadow(im, [(24, PEN_FLOOR), (88, PEN_FLOOR), (96, LANE - 1), (30, LANE - 1)], mul=SOFT_MUL)
    # 草料槽（两头骆驼中间）
    d = ImageDraw.Draw(im)
    rect(d, 70, 134, 80, 140, WOOD)
    hl(d, 70, 80, 134, WOOD_HI)
    hl(d, 70, 80, 140, WOOD_K)
    vl(d, 80, 134, 140, WOOD_D)
    for x in range(71, 80):
        for k in range(int(hrange(1, 5, x, 37))):
            px(d, x + (k % 2), 133 - k, STRAW if (x + k) % 2 else STRAW_D)


def draw_fence(d, im):
    """骆驼栏前面的木栅栏：歪歪的立柱（每 12 px，顶上削尖）、两道横杆（带节疤）、绳子绑着；栏左段搭着一副骆驼鞍
    （木架 + 红毯 + 黄流苏）。骆驼在栅栏后面——帧条里也会把这一段再画一遍盖在骆驼上。"""
    for x in (30, 56, 80):                                              # 遮阳棚的木杆
        vl(d, x, 104, LANE - 1, WOOD_D)
        vl(d, x + 1, 104, LANE - 1, WOOD)
        px(d, x, 112 + x % 7, WOOD_K)
    for i, x in enumerate(range(PEN[0], PEN[1] + 1, 12)):
        top = 125 + int(hrange(0, 3, i, 41))
        vl(d, x, top, LANE - 1, WOOD)
        vl(d, x + 1, top, LANE - 1, WOOD_D)
        px(d, x, top, WOOD_HI)
        px(d, x, top + 6, WOOD_K)
    for (y, sd) in ((129, 1), (137, 2)):
        for x in range(PEN[0] - 1, PEN[1] - 2):
            yy = y + (1 if (x // 23 + sd) % 2 == 0 and x % 23 > 18 else 0)
            px(d, x, yy, WOOD_HI)
            px(d, x, yy + 1, WOOD_D)
            if hash01(x, sd, 42) < 0.06:
                px(d, x, yy, WOOD_K)
        for x in range(PEN[0], PEN[1] + 1, 12):                         # 绑绳
            px(d, x, y - 1, (214, 196, 150))
            px(d, x + 1, y + 2, (190, 170, 124))
    # 一卷绳子挂在立柱上 + 一只皮水桶
    d.ellipse((96, 128, 102, 134), outline=C((206, 184, 132)))
    d.ellipse((97, 129, 101, 133), outline=C((176, 152, 104)))
    rect(d, 109, 130, 113, 135, (110, 72, 46))
    hl(d, 109, 113, 130, (150, 104, 66))
    d.line((109, 130, 111, 127), fill=C((90, 70, 50)))
    d.line((113, 130, 111, 127), fill=C((90, 70, 50)))


@lru_cache(maxsize=64)
def camel_img(bob, jaw, ear, tail, blanket):
    """趴着的单峰骆驼（48×30，朝左；肚子 / 折起来的腿贴地在最下一行）。bob 头上下 0/1、jaw 下巴左右磨 −1/0/1、
    ear 耳朵抖 0/1、tail 尾巴甩 0..2、blanket = 驼峰上搭不搭毯子。光从左上：上沿亮、下半截暗、右 / 下沿描深色边。"""
    w, h = 48, 30
    m = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(m)
    hy = bob
    md.ellipse((14, 15, 44, 33), fill=255)                             # 身子（下半截压在地上）
    md.ellipse((21, 7, 37, 23), fill=255)                              # 驼峰
    md.polygon([(15, 28), (19, 18), (13, 9 + hy), (8, 8 + hy), (6, 12 + hy), (11, 21), (12, 28)], fill=255)   # 脖子
    md.ellipse((2, 2 + hy, 12, 10 + hy), fill=255)                     # 头
    md.polygon([(0, 6 + hy), (4, 4 + hy), (5 + jaw, 10 + hy), (1 + jaw, 10 + hy)], fill=255)   # 嘴 / 下巴
    md.polygon([(9, 3 + hy - ear), (10, 0 + hy - ear), (12, 3 + hy)], fill=255)                # 耳朵
    md.ellipse((11, 24, 24, 31), fill=255)                             # 折起来的前腿（膝盖垫）
    md.ellipse((34, 21, 46, 31), fill=255)                             # 后腿 / 胯
    a = np.array(m) > 0
    im = Image.fromarray(np.dstack([np.zeros((h, w, 3), np.uint8), (a * 255).astype(np.uint8)]), 'RGBA')
    im = P.shade_sprite(im, CAMEL[0], CAMEL[1], CAMEL[2], CAMEL[3], lo_from=0.7)
    d = ImageDraw.Draw(im)
    # 驼峰顶上的毛（亮一点、毛茸茸）
    for x in range(23, 36):
        if x % 2 == 0:
            px(d, x, 8 + int(abs(x - 29) / 3), lt(CAMEL[0], 0.15))
    # 毯子（红底 + 黄条 + 流苏）
    if blanket:
        for x in range(22, 37):
            top = 10 + int(abs(x - 29) / 2.6)
            for y in range(top, top + 6):
                if a[y, x]:
                    px(d, x, y, (164, 52, 46) if (y - top) % 5 else (232, 186, 66))
            vl(d, x, top + 6, top + 7, (232, 186, 66) if x % 2 else (164, 52, 46))
    # 脸：眼睛、长睫毛、鼻孔、嘴线、缰绳（红）
    px(d, 5, 5 + hy, (40, 28, 24))
    px(d, 6, 4 + hy, (40, 28, 24))
    px(d, 1, 6 + hy, CAMEL[3])
    hl(d, 1 + jaw, 4 + jaw, 9 + hy, CAMEL[3])
    for (x, y) in ((3, 7), (6, 8), (9, 8), (11, 9)):
        px(d, x, y + hy, (190, 52, 46))
    px(d, 12, 13 + hy // 2, (190, 52, 46))
    # 膝盖上的老茧（深一点）、后腿折线
    hl(d, 13, 17, 28, CAMEL[3])
    for (x, y) in ((36, 24), (37, 25), (38, 26)):
        px(d, x, y, CAMEL[2])
    # 尾巴（从屁股往下垂，末端一撮深色毛）
    tx = [44, 45, 46][tail]
    for k in range(8):
        u = k / 7
        xx = 44 + round((tx - 44) * u * u)
        px(d, min(w - 1, xx), 16 + k, CAMEL[2] if k < 6 else (90, 64, 46))
    return P.outline(im, (76, 50, 34))


CAMEL_POSE = [  # (bob, jaw, ear, tail)：8 帧嚼草（下巴左右磨）、偶尔抖耳朵、甩尾巴
    (0, 0, 0, 0), (0, 1, 0, 1), (0, 0, 0, 2), (1, -1, 0, 1), (1, 0, 1, 0), (1, 1, 1, 0), (0, 0, 0, 0), (0, -1, 0, 0)]
CAMEL_BOX = (PEN[0] - 3, 104, PEN[1] + 2, LANE)


def camels_frame(t):
    """骆驼栏（strip）：两头骆驼（第二头朝右、驼峰上搭着毯子、动作错开 3 帧）+ 盖在骆驼前面的栅栏。"""
    im = A._new(PW, H)
    f = fidx(t, FPS_ANIM, N_ANIM)
    for i, (x, y, face) in enumerate(CAMEL_XY):
        bob, jaw, ear, tail = CAMEL_POSE[(f + 3 * i) % N_ANIM]
        sp = camel_img(bob, jaw, ear, tail, i == 1)
        if face < 0:
            sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
        paste(im, sp, x, y)
    d = ImageDraw.Draw(im)
    draw_fence(d, im)
    return finish(im)


# ============================================================ 近景：杂货摊
def draw_stall(im):
    """杂货摊：后面是 H1 的院墙；草席棚（三根歪木杆、席子织纹、席边挂草须）、木柜台（板缝、柜台下的暗）、
    柜台上的东西（两只铜咖啡壶 dallah + 小杯、叠好的布、一筐椰枣、陶碗、一摞草帽）、棚下一盏马灯 + 一捆干草药、
    柜台左边地上两口大水罐（zir）、靠墙一卷地毯。挂着的布在 strip 里。"""
    d = mud_wall(im, STALL[0] - 2, H1[0], 112, LANE - 1, ADOBE2, 51, streaks=2)
    crenels(im, STALL[0] - 2, H1[0], 112, ADOBE2, step=7)
    bricks_patch(im, 150, 116, 12, 6, ADOBE2, 52)
    d = ImageDraw.Draw(im)
    # 柜台
    cx0, cx1 = 140, 190
    rect(d, cx0, 127, cx1, LANE - 1, WOOD)
    for xx in range(cx0 + 4, cx1, 6):
        vl(d, xx, 128, LANE - 1, WOOD_D)
        vl(d, xx + 1, 128, LANE - 1, lt(WOOD, 0.08))
    hl(d, cx0 - 1, cx1 + 1, 125, WOOD_HI)
    hl(d, cx0 - 1, cx1 + 1, 126, WOOD)
    hl(d, cx0, cx1, 127, WOOD_K)
    vl(d, cx0, 127, LANE - 1, lt(WOOD, 0.2))
    vl(d, cx1, 127, LANE - 1, WOOD_K)
    for i in range(14):                                             # 木纹节疤
        px(d, int(hrange(cx0 + 2, cx1 - 2, i, 53)), int(hrange(130, 144, i, 54)), WOOD_K)
    cast_shadow(im, [(cx1 + 1, 127), (cx1 + 4, 129), (cx1 + 4, LANE + 1), (cx1 + 1, LANE + 1)])
    d = ImageDraw.Draw(im)
    for (kx, ky) in ((172, 127),):                                  # 基里姆毯（搭在柜台正面）
        for y in range(ky, ky + 13):
            for x in range(kx, kx + 17):
                r, q = (y - ky) // 3, (x - kx + (y - ky)) % 6
                c = (150, 40, 44) if r % 2 == 0 else ((40, 36, 44) if q < 3 else (236, 220, 180))
                if (y - ky) % 3 == 2 and (x - kx) % 4 == 0:
                    c = (230, 180, 60)
                px(d, x, y, c)
        for x in range(kx, kx + 17, 2):
            vl(d, x, ky + 13, ky + 15, (236, 220, 180))
    for (x, grain, gd) in ((149, (236, 224, 196), (206, 190, 160)), (160, (190, 84, 56), (150, 60, 40))):   # 麻袋
        rect(d, x, 137, x + 9, LANE - 1, (176, 148, 100))
        for yy in range(139, LANE - 1, 2):
            hl(d, x + 1, x + 8, yy, (160, 132, 88))
        hl(d, x - 1, x + 10, 136, (204, 178, 126))
        hl(d, x - 1, x + 10, 137, (150, 124, 82))
        for xx in range(x, x + 10):
            hh = int(round(2 * math.sin((xx - x + 0.5) / 10 * math.pi)))
            vl(d, xx, 135 - hh, 135, grain if (xx + hh) % 2 else gd)
        vl(d, x + 9, 137, LANE - 1, (130, 106, 70))
    # 柜台上的东西
    d = ImageDraw.Draw(im)
    for (x, c) in ((143, (214, 168, 70)), (151, (196, 150, 60))):   # 两只铜咖啡壶 dallah（尖盖、长嘴）
        d.polygon([(x, 124), (x + 5, 124), (x + 4, 119), (x + 3, 116), (x + 2, 116), (x + 1, 119)], fill=C(c))
        hl(d, x + 1, x + 4, 116, lt(c, 0.3))
        px(d, x + 2, 114, c)
        px(d, x + 2, 113, lt(c, 0.4))
        d.line((x + 5, 120, x + 8, 117), fill=C(c))                 # 壶嘴
        px(d, x + 8, 116, c)
        px(d, x + 1, 120, lt(c, 0.45))
        vl(d, x + 4, 119, 123, dk(c, 0.75))
    for x in (160, 163, 166):                                       # 小杯
        hl(d, x, x + 1, 124, (240, 236, 224))
        px(d, x, 123, (214, 206, 190))
    for k, col in enumerate(((60, 96, 160), (214, 60, 70), (240, 200, 70), (90, 150, 96))):   # 叠好的布
        rect(d, 170, 124 - 2 * k, 180, 125 - 2 * k, col)
        hl(d, 170, 180, 124 - 2 * k, lt(col, 0.25))
        px(d, 180, 125 - 2 * k, dk(col, 0.7))
    d.ellipse((181, 118, 190, 125), fill=C((176, 140, 80)))          # 一筐椰枣
    hl(d, 181, 190, 121, (150, 112, 60))
    for i in range(10):
        px(d, int(hrange(182, 189, i, 55)), int(hrange(116, 120, i, 56)), (150, 70, 40) if i % 2 else (190, 104, 50))
    # 马灯 + 干草药（挂在棚下）
    d.line((172, 101, 172, 104), fill=C((70, 66, 64)))
    rect(d, 170, 105, 174, 110, (60, 58, 60))
    rect(d, 171, 106, 173, 109, (250, 226, 150))
    hl(d, 169, 175, 104, (90, 86, 84))
    for k in range(5):
        vl(d, 157 + k, 101, 106 + k % 3, (126, 140, 80) if k % 2 else (150, 160, 96))
    # 大水罐（zir，地上）+ 小陶罐
    for (x, y0, r, c) in ((133, 126, 6, (182, 108, 72)), (137, 136, 4, (166, 96, 64))):
        d.ellipse((x - r, y0, x + r, y0 + 2 * r + 4), fill=C(c))
        d.chord((x - r, y0, x + r, y0 + 2 * r + 4), 290, 70, fill=C(dk(c, 0.82)))
        px(d, x - r + 2, y0 + 3, lt(c, 0.3))
        hl(d, x - 2, x + 2, y0 - 1, dk(c, 0.7))
        hl(d, x - 2, x + 2, y0, lt(c, 0.2))
    cast_shadow(im, [(139, 140), (142, 140), (144, LANE + 1), (140, LANE + 1)], mul=SOFT_MUL)
    # 靠墙一卷地毯（斜靠在柜台右边）
    d = ImageDraw.Draw(im)
    for k in range(26):
        y = LANE - 1 - k
        x = 192 + k // 6
        hl(d, x, x + 2, y, (150, 48, 52) if (k // 3) % 2 else (196, 150, 70))
        px(d, x + 2, y, (110, 34, 40))
    # 草席棚（三根歪木杆 + 织纹席子）
    for (x, lean) in ((131, 1), (163, 0), (195, -1)):
        d.line((x, LANE - 1, x + lean, 98), fill=C(WOOD_D))
        d.line((x + 1, LANE - 1, x + 1 + lean, 98), fill=C(WOOD))
    for x in range(126, 200):
        sag = int(round(2 * math.sin((x - 126) / 74 * math.pi)))
        top = 94 + sag
        for y in range(top, top + 6):
            c = (214, 186, 118) if ((x + y) // 2) % 2 else (190, 160, 96)
            if y == top:
                c = (236, 214, 150)
            if y == top + 5:
                c = (150, 122, 72)
            px(d, x, y, c)
        if hash01(x, 57) < 0.45:
            vl(d, x, top + 6, top + 6 + int(hrange(1, 4, x, 58)), (176, 146, 86))
    cast_shadow(im, [(127, 102), (200, 102), (200, 112), (127, 108)], mul=SOFT_MUL)
    cast_shadow(im, [(136, 112), (198, 112), (198, 124), (136, 118)], mul=SOFT_MUL, level=0.5)


CLOTHS = [(137, (196, 52, 60), 16), (147, (60, 112, 176), 13), (182, (236, 196, 70), 11)]   # (x, 颜色, 长)
CLOTH_BOX = (132, 99, 192, 120)


def cloths_frame(t):
    """草席棚下挂着的布匹（strip）：上端钉在席子上，下摆随风往右摆 0–2 px；布上一道花边。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    for i, (x, col, L) in enumerate(CLOTHS):
        ph = math.tau * f / N_ANIM + i * 1.7
        for r in range(L):
            u = r / L
            dx = round((1.2 + 0.8 * math.sin(ph)) * u * u)
            c = col if r % 6 != 4 else lt(col, 0.4)
            if r == L - 1:
                c = dk(col, 0.7)
            hl(d, x + dx, x + dx + 4, 101 + r, c)
            px(d, x + dx, 101 + r, lt(c, 0.2))
            px(d, x + dx + 4, 101 + r, dk(c, 0.72))
    return finish(im)


# ============================================================ 近景：房子
def draw_h1(im):
    """H1 两层土坯房：两排木梁头、三角垛、二楼两扇蓝绿百叶窗、一排三角通风孔、刷花纹的蓝绿木门、木格栅小窗、
    两根木排水槽、一块掉了泥皮露出砖的地方、屋顶的电视天线和晾衣杆。"""
    x0, x1 = H1
    top = 64
    mud_wall(im, x0, x1, top, LANE - 1, ADOBE, 61, streaks=3)
    crenels(im, x0, x1, top, ADOBE)
    beam_ends(im, x0, x1, 70)
    beam_ends(im, x0, x1, 98, off=5)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, 96, lt(ADOBE, 0.12))                          # 楼层分界的一道泥线
    hl(d, x0, x1 - 1, 97, dk(ADOBE, 0.9))
    for wx in (204, 230):
        V.win_shutter(im, wx, 78, 8, 12, ADOBE, TEAL, 'closed' if wx == 204 else 'half', frame=GYPSUM)
    tri_vents(im, x0 + 5, x1 - 4, 91)
    najdi_door(im, 207, 104, 16, 42, TEAL, seed=0)
    win_hole(im, 232, 112, 7, 8, ADOBE, grille=True)
    bricks_patch(im, 226, 126, 10, 7, ADOBE, 62)
    spout(im, x0 + 1, top + 4)
    spout(im, x1 - 7, top + 4)
    d = ImageDraw.Draw(im)
    V.tv_antenna(d, 238, 46, 16, (80, 78, 82))
    for x in (200, 242):                                             # 晾衣杆
        vl(d, x, 50, top - 1, WOOD_D)
        px(d, x, 50, WOOD_HI)
    # 门右边一条泥长凳（mastaba）+ 一块红垫子
    rect(d, 227, 139, 244, LANE - 1, ADOBE_S)
    hl(d, 227, 244, 139, ADOBE_HI)
    hl(d, 227, 244, 140, ADOBE)
    vl(d, 244, 139, LANE - 1, ADOBE_D)
    rect(d, 230, 137, 238, 138, (170, 50, 46))
    hl(d, 230, 238, 137, (206, 84, 66))
    cast_shadow(im, [(245, 140), (247, 141), (247, LANE + 1), (245, LANE + 1)], mul=SOFT_MUL)
    d = ImageDraw.Draw(im)
    cat, cat_d = (214, 140, 70), (170, 100, 50)                       # 凳子上蜷着睡的橘猫（尾巴绕到前面）
    d.ellipse((235, 133, 242, 139), fill=C(cat))
    d.ellipse((240, 132, 244, 136), fill=C(cat))
    for x in (236, 238):
        px(d, x, 134, cat_d)
    px(d, 241, 132, cat_d)
    px(d, 243, 131, cat_d)
    hl(d, 235, 240, 139, cat_d)
    px(d, 242, 134, (60, 40, 30))
    for (x, y) in ((206, 89), (232, 89)):                               # 二楼窗台上的罗勒盆栽
        rect(d, x, y, x + 3, y + 2, (176, 96, 60))
        hl(d, x, x + 3, y, (204, 126, 84))
        for (ox, oy) in ((0, -1), (1, -2), (2, -1), (3, -2), (1, -3)):
            px(d, x + ox, y + oy, (70, 140, 70) if (ox + oy) % 2 else (100, 170, 84))
    # 墙上一块挂着的小镜子和一个电表箱（生活气）
    rect(d, 226, 106, 229, 110, (120, 120, 126))
    px(d, 227, 107, (220, 230, 240))
    cast_shadow(im, [(230, 107), (231, 107), (231, 111), (230, 111)])


LAUNDRY = [(202, 4, 9, (246, 244, 236)), (208, 5, 7, (200, 56, 60)), (215, 3, 6, (60, 110, 170)),
           (220, 4, 11, (246, 244, 236)), (227, 3, 5, (240, 196, 70)), (232, 5, 8, (44, 40, 46))]
LAUNDRY_BOX = (198, 49, 245, 64)


def laundry_frame(t):
    """H1 屋顶的晾衣绳（strip）：白袍、红格头巾、蓝衣、黑袍……下摆往右飘，一件件错开相位。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    V.wire(d, 200, 51, 242, 52, 2, (100, 92, 88))
    for i, (x, w, L, col) in enumerate(LAUNDRY):
        ph = math.tau * f / N_ANIM + i * 1.3
        y0 = 52 + (1 if 210 < x < 232 else 0)
        for r in range(L):
            u = r / max(1, L - 1)
            dx = round((0.8 + 0.9 * math.sin(ph)) * u)
            c = col
            if col == (200, 56, 60) and (r + x) % 2:
                c = (240, 236, 228)                                      # 红格头巾
            hl(d, x + dx, x + dx + w - 1, y0 + r, c)
            px(d, x + dx + w - 1, y0 + r, dk(c, 0.78))
        hl(d, x, x + w - 1, y0, lt(col, 0.2))
        px(d, x, y0 - 1, (150, 120, 90))                                  # 衣夹
    return finish(im)


def draw_h2(im):
    """H2：左边一截院墙（矮、带三角垛）+ 泥烤炉 tannur（炉口一圈熏黑）+ 一捆柴 + 一小堆草料；右边一层土坯房：
    木梁头、三角垛、窗洞、蓝绿木门、门边一串红辣椒；屋顶晒椰枣的草席 + 一只水罐。"""
    x0, x1 = H2W
    mud_wall(im, x0, x1, 118, LANE - 1, ADOBE3, 71, streaks=1)
    crenels(im, x0, x1, 118, ADOBE3, step=7)
    x0, x1 = H2
    mud_wall(im, x0, x1, 94, LANE - 1, ADOBE2, 72, streaks=3)
    crenels(im, x0, x1, 94, ADOBE2)
    beam_ends(im, x0, x1, 100, off=4)
    win_hole(im, 271, 110, 7, 9, ADOBE2)
    najdi_door(im, 285, 104, 15, 42, (64, 128, 150), seed=1)
    spout(im, x1 - 7, 98)
    d = ImageDraw.Draw(im)
    for k in range(9):                                              # 门边一串红辣椒
        px(d, 302, 106 + k, (196, 40, 36) if k % 2 else (220, 70, 44))
        px(d, 303, 107 + k, (150, 30, 30))
    vl(d, 302, 104, 105, (120, 100, 70))
    # 屋顶：晒椰枣的草席 + 水罐
    hl(d, 276, 298, 93, (190, 160, 96))
    for i in range(18):
        px(d, int(hrange(277, 297, i, 73)), 92, (150, 70, 40) if i % 2 else (176, 96, 44))
    d.ellipse((268, 86, 274, 93), fill=C((180, 106, 70)))
    px(d, 269, 88, (214, 148, 110))
    hl(d, 270, 272, 85, (150, 84, 58))
    # 泥烤炉 tannur（院墙前）
    ox, oy = OVEN
    for y in range(oy, LANE):
        u = (y - oy) / (LANE - oy)
        hw = int(round(4 + 3 * math.sqrt(u)))
        for x in range(ox - hw, ox + hw + 1):
            v = (x - (ox - hw)) / max(1, 2 * hw)
            c = (194, 132, 88) if v < 0.3 else ((172, 112, 74) if v < 0.75 else (140, 90, 60))
            px(d, x, y, c)
    hl(d, ox - 3, ox + 3, oy, (60, 44, 40))                         # 炉口（熏黑）
    hl(d, ox - 4, ox + 4, oy + 1, (110, 76, 58))
    for (x, y) in ((ox - 2, oy + 2), (ox + 1, oy + 3), (ox + 3, oy + 2)):
        px(d, x, y, (90, 64, 50))
    px(d, ox - 1, LANE - 3, (250, 170, 70))                          # 炉门里的一点火光
    px(d, ox, LANE - 3, (240, 120, 50))
    hl(d, ox - 2, ox + 1, LANE - 2, (60, 40, 36))
    cast_shadow(im, [(ox + 7, oy + 4), (ox + 10, oy + 6), (ox + 11, LANE + 1), (ox + 7, LANE + 1)], mul=SOFT_MUL)
    # 一捆柴（靠在 H1 的墙角）
    d = ImageDraw.Draw(im)
    for k in range(5):
        d.line((239 + k, LANE - 1, 241 + k, 133 + (k % 2)), fill=C(WOOD if k % 2 else WOOD_D))
        px(d, 241 + k, 133 + (k % 2), WOOD_HI)
    # 草料堆（山羊啃的）
    for x in range(262, 269):
        hh = int(round(4 * math.sin((x - 261) / 8 * math.pi)))
        for y in range(LANE - 1 - hh, LANE):
            px(d, x, y, STRAW if (x + y) % 2 else STRAW_D)


def draw_h3(im):
    """H3 矮库房：木板门（旧、发灰）、通风孔、三角垛；靠墙的梯子（搭上屋顶）、一把扫帚；屋顶一只木箱。"""
    x0, x1 = H3
    mud_wall(im, x0, x1, 104, LANE - 1, ADOBE, 81, streaks=2)
    crenels(im, x0, x1, 104, ADOBE, step=7)
    beam_ends(im, x0, x1, 110, step=8, off=4)
    d = ImageDraw.Draw(im)
    dx0, dx1 = 318, 331
    rect(d, dx0 - 1, 116, dx1 + 1, LANE - 1, GYPSUM_S)
    plank = (150, 128, 100)
    rect(d, dx0, 118, dx1, LANE - 2, plank)
    for xx in range(dx0 + 2, dx1, 3):
        vl(d, xx, 119, LANE - 2, dk(plank, 0.78))
    hl(d, dx0, dx1, 118, dk(plank, 0.6))
    for yy in (123, 138):
        hl(d, dx0, dx1, yy, dk(plank, 0.7))
    px(d, dx1 - 2, 131, (70, 66, 64))
    tri_vents(im, x0 + 5, x0 + 14, 112, step=6)
    d = ImageDraw.Draw(im)
    # 梯子（底在地上 x 306，顶搭在屋顶 y 103）
    for (bx, tx) in ((306, 311), (311, 316)):
        d.line((bx, LANE - 1, tx, 100), fill=C(WOOD_D))
    for y in range(104, LANE - 1, 5):
        u = (LANE - 1 - y) / (LANE - 1 - 100)
        a = round(306 + 5 * u)
        hl(d, a, a + 5, y, WOOD_HI)
    cast_shadow(im, [(312, 102), (318, 102), (314, LANE - 1), (309, LANE - 1)], mul=SOFT_MUL, level=0.5)
    # 扫帚（靠在门右边）
    d = ImageDraw.Draw(im)
    d.line((334, 118, 333, 140), fill=C(WOOD))
    for k in range(5):
        d.line((333, 140, 331 + k, LANE - 1), fill=C(STRAW_D if k % 2 else STRAW))
    # 屋顶一只木箱 + 一个筐
    rect(d, 306, 97, 314, 103, WOOD)
    hl(d, 306, 314, 97, WOOD_HI)
    vl(d, 314, 97, 103, WOOD_K)
    d.ellipse((318, 99, 324, 104), fill=C((170, 136, 80)))


def draw_well(im):
    """井：石砌井台（圆石 + 灰缝，上沿一圈亮）、两根木柱 + 横梁 + 滑轮、井绳吊着一只木桶；右边一个石头饮水槽（有水）；
    井台上一只小陶罐。"""
    d = ImageDraw.Draw(im)
    x0, x1 = WELL
    top = 131
    stone = (176, 166, 150)
    for y in range(top, LANE):
        for x in range(x0, x1 + 1):
            u = (x - x0) / (x1 - x0)
            c = stone if 0.2 < u < 0.75 else (lt(stone, 0.12) if u <= 0.2 else dk(stone, 0.84))
            row = (y - top) // 4
            if (y - top) % 4 == 0 or (x + row * 3) % 7 == 0:
                c = dk(c, 0.78)
            px(d, x, y, c)
    hl(d, x0 - 1, x1 + 1, top - 1, lt(stone, 0.35))
    hl(d, x0 - 1, x1 + 1, top, lt(stone, 0.2))
    hl(d, x0 + 2, x1 - 2, top - 2, (70, 60, 56))                    # 井口（往里看是黑的）
    # 木架
    for x in (x0 + 1, x1 - 2):
        vl(d, x, 102, top - 2, WOOD)
        vl(d, x + 1, 102, top - 2, WOOD_D)
    hl(d, x0 - 2, x1 + 2, 101, WOOD_HI)
    hl(d, x0 - 2, x1 + 2, 102, WOOD)
    hl(d, x0 - 1, x1 + 1, 103, WOOD_K)
    cx = (x0 + x1) // 2
    d.ellipse((cx - 3, 102, cx + 3, 108), outline=C(WOOD_K), fill=C(WOOD))
    px(d, cx, 105, (60, 56, 56))
    vl(d, cx + 3, 105, 117, (200, 180, 130))                        # 井绳
    vl(d, cx - 3, 105, top - 3, (180, 160, 112))
    rect(d, cx + 1, 117, cx + 6, 123, (120, 84, 54))                # 木桶
    hl(d, cx + 1, cx + 6, 117, (160, 120, 80))
    hl(d, cx + 1, cx + 6, 120, (80, 76, 74))
    vl(d, cx + 6, 118, 123, (86, 60, 40))
    d.line((cx + 1, 117, cx + 3, 115), fill=C((90, 86, 84)))
    d.line((cx + 6, 117, cx + 3, 115), fill=C((90, 86, 84)))
    cast_shadow(im, [(x1 + 1, top + 1), (x1 + 4, top + 3), (x1 + 4, LANE + 1), (x1 + 1, LANE + 1)], mul=SOFT_MUL)
    # 井台上的小陶罐
    d = ImageDraw.Draw(im)
    d.ellipse((x0 + 2, top - 6, x0 + 7, top - 1), fill=C((178, 104, 70)))
    px(d, x0 + 3, top - 5, (214, 148, 110))
    # 饮水槽
    tx0, tx1 = 365, 378
    rect(d, tx0, 138, tx1, LANE - 1, (168, 158, 142))
    hl(d, tx0, tx1, 138, (204, 196, 182))
    hl(d, tx0 + 1, tx1 - 1, 139, (110, 150, 160))                   # 水面
    px(d, tx0 + 4, 139, (210, 230, 236))
    vl(d, tx1, 138, LANE - 1, (130, 120, 108))
    for x in range(tx0 + 3, tx1, 5):
        vl(d, x, 141, LANE - 2, (150, 140, 126))


def minaret_edges(y):
    """宣礼塔在 y 行的左右边（往上收：底宽 18、顶宽 12）。"""
    u = (LANE - 1 - y) / (LANE - 1 - 64)
    a = MINARET[0] + 3 * u
    b = MINARET[1] - 3 * u
    return int(round(a)), int(round(b))


def draw_mosque(im):
    """小清真寺：土坯宣礼塔（往上收、窄窗、木挑台、小亭、尖顶、新月、两只喇叭）+ 礼拜堂（三角垛、木梁头、尖拱绿木门、
    两扇小拱窗、净身的水龙头 + 小水池、门口几双拖鞋）。"""
    d = ImageDraw.Draw(im)
    # 礼拜堂
    x0, x1 = MOSQUE
    mud_wall(im, x0, x1, 94, LANE - 1, ADOBE3, 91, streaks=3)
    crenels(im, x0, x1, 94, ADOBE3)
    beam_ends(im, x0, x1, 100, off=3)
    d = ImageDraw.Draw(im)
    dx, dw = 414, 17
    for i in range(dw + 4):                                         # 尖拱门（门套白、门里绿木门）
        u = (i + 0.5) / (dw + 4) * 2 - 1
        rise = int(round(10 * (1 - abs(u)) ** 0.7))
        vl(d, dx - 2 + i, 106 - rise, LANE - 1, GYPSUM_S)
    for i in range(dw):
        u = (i + 0.5) / dw * 2 - 1
        rise = int(round(9 * (1 - abs(u)) ** 0.7))
        vl(d, dx + i, 108 - rise, LANE - 2, (70, 120, 84))
        if i % 3 == 0:
            vl(d, dx + i, 110 - rise, LANE - 2, (54, 98, 70))
    vl(d, dx + dw // 2, 100, LANE - 2, (40, 74, 54))
    for yy in range(112, LANE - 2, 6):
        for i in range(1, dw - 1, 3):
            px(d, dx + i, yy, (200, 196, 160))
    hl(d, dx - 2, dx + dw + 1, LANE - 1, (196, 182, 156))
    for wx in (402, 437):                                            # 小拱窗
        for i in range(6):
            rise = 2 if i in (2, 3) else (1 if i in (1, 4) else 0)
            vl(d, wx + i, 106 - rise, 115, DARK_IN)
        hl(d, wx - 1, wx + 6, 116, lt(GYPSUM, 0.2))
        vl(d, wx + 2, 106, 115, (90, 70, 54))
    d.line((422, 96, 422, 99), fill=C((90, 80, 60)))                    # 门上挂的铜灯
    rect(d, 420, 100, 424, 104, (196, 150, 60))
    rect(d, 421, 101, 423, 103, (250, 226, 150))
    hl(d, 419, 425, 99, (150, 110, 46))
    px(d, 422, 105, (150, 110, 46))
    # 净身的水龙头 + 小水池
    rect(d, 436, 137, 446, LANE - 1, (180, 170, 156))
    hl(d, 436, 446, 137, (214, 206, 192))
    hl(d, 437, 445, 138, (110, 150, 160))
    vl(d, 441, 128, 133, (120, 124, 130))
    hl(d, 441, 444, 128, (150, 154, 160))
    px(d, 441, 134, (190, 220, 236))
    for (x, c) in ((402, (60, 50, 46)), (406, (60, 90, 150)), (432, (150, 60, 50))):   # 拖鞋
        hl(d, x, x + 2, LANE - 1, c)
    # 宣礼塔
    for y in range(64, LANE):
        a, b = minaret_edges(y)
        for x in range(a, b + 1):
            v = (x - a) / max(1, b - a)
            c = lt(ADOBE, 0.12) if v < 0.25 else (ADOBE if v < 0.7 else ADOBE_S)
            if hash01(x, y, 92) < 0.08:
                c = dk(c, 0.92)
            px(d, x, y, c)
        px(d, a, y, lt(ADOBE, 0.24))
        px(d, b, y, ADOBE_D)
    for yy in (84, 104, 124):                                       # 窄窗 + 一道道泥线
        a, b = minaret_edges(yy)
        m = (a + b) // 2
        vl(d, m, yy, yy + 5, DARK_IN)
        vl(d, m + 1, yy, yy + 5, dk(DARK_IN, 0.8))
        hl(d, a, b, yy - 4, lt(ADOBE, 0.16))
        hl(d, a, b, yy - 3, dk(ADOBE, 0.9))
    # 木挑台（y 62–65）
    a, b = minaret_edges(64)
    for x in range(a - 3, b + 4, 2):
        px(d, x, 65, WOOD_K)
    hl(d, a - 3, b + 3, 63, WOOD)
    hl(d, a - 3, b + 3, 62, WOOD_HI)
    for x in range(a - 3, b + 4, 3):
        vl(d, x, 58, 61, WOOD_D)
    hl(d, a - 3, b + 3, 58, WOOD)
    # 小亭（y 48–57）+ 尖顶 + 新月
    cx = (MINARET[0] + MINARET[1]) // 2
    rect(d, cx - 5, 49, cx + 5, 57, ADOBE3)
    for xx in (cx - 3, cx + 1):
        rect(d, xx, 51, xx + 2, 57, DARK_IN)
        px(d, xx + 1, 50, DARK_IN)
    vl(d, cx - 5, 49, 57, lt(ADOBE3, 0.2))
    vl(d, cx + 5, 49, 57, ADOBE_S)
    hl(d, cx - 6, cx + 6, 48, GYPSUM)
    for r in range(6):
        hl(d, cx - 5 + r, cx + 5 - r, 47 - r, ADOBE3 if r < 5 else lt(ADOBE3, 0.2))
        px(d, cx + 5 - r, 47 - r, ADOBE_S)
    vl(d, cx, 37, 41, (200, 176, 90))
    for (x, y) in ((cx - 2, 35), (cx - 3, 34), (cx - 3, 33), (cx - 2, 32), (cx - 1, 33)):   # 新月
        px(d, x, y, (236, 210, 110))
    # 两只喇叭（80 年代的扩音器）
    for (x, sgn) in ((a - 1, -1), (b + 1, 1)):
        hl(d, min(x, x + 3 * sgn), max(x, x + 3 * sgn), 69, (150, 154, 160))
        vl(d, x + 3 * sgn, 68, 70, (196, 200, 206))
        px(d, x, 70, (90, 92, 98))
    cast_shadow(im, [(MINARET[1] + 1, 66), (MINARET[1] + 4, 70), (MINARET[1] + 4, 93), (MINARET[1] + 1, 93)])


# ============================================================ 近景：铁皮棚 / 汽油桶 / 风向袋
def corrugated(d, x0, x1, y0, y1, col, seed, vertical=True):
    """瓦楞铁皮：竖的亮 / 暗条（每 3 px 一道棱），零星锈斑。"""
    for x in range(x0, x1 + 1):
        k = (x - x0) % 3
        c = lt(col, 0.18) if k == 0 else (col if k == 1 else dk(col, 0.8))
        for y in range(y0, y1 + 1):
            cc = c
            if hash01(seed, x // 2, y // 3) < 0.07:
                cc = RUST if k != 2 else RUST_D
            px(d, x, y, cc)


def draw_shed(im):
    """卖飞机的商人的铁皮棚：铁皮后墙（灰、锈红、褪色的蓝三块拼的）、三根木柱、瓦楞铁皮顶（前沿一道道棱、锈斑、下面暗）；
    棚里：靠墙的木螺旋桨、挂工具的木板（扳手 / 锤子 / 锯）、工作台 + 台钳、备用机轮、油壶、一摞木箱；
    棚檐下挂一块手绘招牌（白底红色小飞机）；右边三只汽油桶 + 漏斗。"""
    d = ImageDraw.Draw(im)
    x0, x1 = SHED
    # 后墙（在棚子阴影里，偏暗）
    corrugated(d, x0 + 4, x0 + 30, 96, LANE - 1, (138, 140, 138), 1)
    corrugated(d, x0 + 31, x0 + 58, 96, LANE - 1, (150, 104, 74), 2)
    corrugated(d, x0 + 59, x1 - 4, 96, LANE - 1, (98, 128, 150), 3)
    mul_box(im, (x0 + 4, 96, x1 - 4, LANE - 1), np.array((0.72, 0.74, 0.82), np.float32))
    d = ImageDraw.Draw(im)
    # 靠墙的木螺旋桨（两叶，竖着，桨尖刷黄漆）
    pxx = x0 + 36
    for y in range(100, LANE - 1):
        u = abs((y - 122) / 22.0)
        hw = 1 if u > 0.85 else (2 if u > 0.15 else 3)
        hl(d, pxx - hw, pxx + hw - 1, y, (150, 102, 60))
        px(d, pxx - hw, y, (184, 136, 86))
    rect(d, pxx - 2, 120, pxx + 1, 124, (110, 112, 118))
    px(d, pxx - 1, 121, (170, 172, 178))
    for y in (101, 102, 142, 143):
        hl(d, pxx - 1, pxx, y, (230, 200, 60))
    # 挂工具的木板（扳手 / 锤子 / 锯）
    rect(d, x0 + 46, 104, x0 + 70, 118, (150, 118, 80))
    hl(d, x0 + 46, x0 + 70, 104, (176, 142, 100))
    for (tx, c) in ((x0 + 49, (80, 82, 90)), (x0 + 54, (110, 80, 50)), (x0 + 66, (80, 82, 90))):
        vl(d, tx, 106, 115, c)
        hl(d, tx - 1, tx + 1, 106, c)
    d.polygon([(x0 + 57, 107), (x0 + 63, 107), (x0 + 63, 110), (x0 + 57, 112)], fill=C((130, 132, 140)))
    # 工作台 + 台钳 + 两只油壶 + 台子底下一卷油布
    rect(d, x0 + 42, 126, x0 + 72, 128, WOOD_HI)
    hl(d, x0 + 42, x0 + 72, 129, WOOD_K)
    for lx in (x0 + 43, x0 + 70):
        vl(d, lx, 129, LANE - 1, WOOD_D)
    rect(d, x0 + 64, 122, x0 + 69, 125, (70, 90, 110))
    hl(d, x0 + 63, x0 + 70, 121, (110, 130, 150))
    for k, c in enumerate(((200, 60, 50), (60, 120, 70))):
        rect(d, x0 + 46 + k * 6, 121, x0 + 50 + k * 6, 125, c)
        px(d, x0 + 46 + k * 6, 120, (90, 90, 96))
    hl(d, x0 + 48, x0 + 60, 141, (70, 60, 56))
    hl(d, x0 + 47, x0 + 61, 142, (96, 84, 74))
    # 备用机轮（棚右端）
    d.ellipse((x0 + 75, 133, x0 + 87, LANE - 1), fill=C((40, 40, 44)))
    d.ellipse((x0 + 78, 136, x0 + 84, 142), fill=C((150, 152, 158)))
    px(d, x0 + 81, 139, (70, 70, 76))
    # 汽油桶（棚左前：红 / 蓝两只立着 + 一只黄桶横放在上面）+ 漏斗
    for (bx, col) in ((x0 + 4, (178, 54, 46)), (x0 + 15, (56, 92, 150))):
        rect(d, bx, 130, bx + 9, LANE - 1, col)
        vl(d, bx, 130, LANE - 1, lt(col, 0.25))
        vl(d, bx + 9, 130, LANE - 1, dk(col, 0.65))
        for yy in (134, 141):
            hl(d, bx, bx + 9, yy, dk(col, 0.7))
            hl(d, bx, bx + 9, yy - 1, lt(col, 0.2))
        hl(d, bx, bx + 9, 130, lt(col, 0.35))
    yb = (226, 186, 52)
    rect(d, x0 + 5, 122, x0 + 22, 129, yb)
    hl(d, x0 + 5, x0 + 22, 122, lt(yb, 0.3))
    hl(d, x0 + 5, x0 + 22, 129, dk(yb, 0.7))
    d.ellipse((x0 + 21, 122, x0 + 24, 129), fill=C(dk(yb, 0.8)))
    px(d, x0 + 22, 125, (90, 80, 50))
    for xx in (x0 + 9, x0 + 16):
        vl(d, xx, 123, 128, dk(yb, 0.75))
    d.polygon([(x0 + 8, 117), (x0 + 13, 117), (x0 + 11, 120), (x0 + 10, 120)], fill=C((160, 164, 170)))
    px(d, x0 + 10, 121, (120, 124, 130))
    cast_shadow(im, [(x0 + 25, 131), (x0 + 28, 133), (x0 + 30, LANE + 1), (x0 + 25, LANE + 1)], mul=SOFT_MUL)
    d = ImageDraw.Draw(im)
    # 木柱
    for x in (x0 + 2, x0 + 44, x1 - 4):
        vl(d, x, 92, LANE - 1, WOOD)
        vl(d, x + 1, 92, LANE - 1, WOOD_D)
        px(d, x, 100 + x % 5, WOOD_K)
    # 铁皮顶（前沿：左高右低一点）
    for x in range(x0 - 2, x1 + 3):
        y = 88 + int(round((x - x0) / (x1 - x0) * 3))
        k = (x - x0) % 3
        c = IRON_HI if k == 0 else (IRON if k == 1 else IRON_D)
        if hash01(x // 2, 93) < 0.12:
            c = RUST
        vl(d, x, y, y + 2, c)
        px(d, x, y + 3, (70, 70, 74))
        if hash01(x, 94) < 0.2:
            px(d, x, y + 4, RUST_D)                                  # 铁皮檐下淌的锈
    cast_shadow(im, [(x0, 92), (x1 + 2, 95), (x1 + 2, 104), (x0, 100)], mul=SOFT_MUL)
    # 招牌（棚檐下挂着：白底红飞机 + 一道蓝线）
    d = ImageDraw.Draw(im)
    sx0, sy0 = x0 + 8, 96
    for xx in (sx0 + 2, sx0 + 22):
        vl(d, xx, 92, sy0 - 1, (90, 86, 84))
    rect(d, sx0, sy0, sx0 + 24, sy0 + 10, (238, 232, 216))
    rect(d, sx0, sy0, sx0 + 24, sy0 + 10, None, outline=(150, 110, 70))
    red, ink = (200, 50, 46), (40, 60, 120)
    ax, ay = sx0 + 5, sy0 + 4                                        # 小飞机（朝左）：机身、高单翼、尾翼、螺旋桨、轮子
    hl(d, ax + 1, ax + 14, ay, red)
    hl(d, ax + 2, ax + 12, ay + 1, red)
    hl(d, ax + 4, ax + 11, ay - 2, red)
    px(d, ax + 6, ay - 1, red)
    vl(d, ax + 14, ay - 3, ay, red)
    px(d, ax + 13, ay - 2, red)
    px(d, ax + 3, ay, (150, 190, 220))                               # 风挡
    vl(d, ax, ay - 2, ay + 2, (110, 110, 118))
    px(d, ax + 4, ay + 2, (40, 40, 44))
    px(d, ax + 10, ay + 2, (40, 40, 44))
    for k, xx in enumerate(range(sx0 + 3, sx0 + 22, 4)):              # 一行“字”（只是笔画的样子）
        hl(d, xx, xx + 2, sy0 + 8, ink)
        px(d, xx + (k % 2) * 2, sy0 + 7, ink)
    px(d, sx0 + 21, sy0 + 6, ink)


def draw_runway_fence(im):
    """跑道后沿的一道铁丝网（隔开外面的沙漠）：每 20 px 一根歪木桩、两道铁丝（每 3 px 一个刺）；跑道尽头一只刷白、
    半埋在沙里的轮胎当标志。都在可走带后沿以外（y ≤ 146）。"""
    d = ImageDraw.Draw(im)
    for i, x in enumerate(range(RUNWAY[0] + 14, PW + 1, 20)):
        top = 135 + int(hrange(0, 3, i, 95))
        vl(d, x, top, LANE - 1, WOOD_D)
        px(d, x, top, WOOD_HI)
        px(d, x + 1, LANE - 1, WOOD_K)
    for y in (138, 142):
        for x in range(RUNWAY[0] + 14, PW):
            if (x - RUNWAY[0]) % 20 == 14:
                continue
            yy = y + (1 if 6 < (x - RUNWAY[0] - 14) % 20 < 14 else 0)
            px(d, x, yy, (126, 124, 122))
            if x % 3 == 0:
                px(d, x, yy - 1, (150, 148, 146))
    for x in range(627, 637):                                       # 半埋的白轮胎
        hh = int(round(4 * math.sin((x - 626.5) / 10.5 * math.pi)))
        for y in range(LANE - hh, LANE):
            px(d, x, y, (240, 238, 230) if (y - (LANE - hh)) < 2 or x in (627, 636) else (90, 86, 84))
        px(d, x, LANE - hh, (252, 252, 248))


def draw_sock_pole(im):
    """风向袋杆：细铁杆 + 底下一块水泥墩 + 杆顶的套环（袋子在 strip 里）。"""
    d = ImageDraw.Draw(im)
    x, y = SOCK
    vl(d, x, y, LANE - 2, (120, 122, 128))
    vl(d, x + 1, y + 2, LANE - 2, (80, 82, 88))
    rect(d, x - 2, LANE - 3, x + 3, LANE - 1, (180, 176, 168))
    hl(d, x - 2, x + 3, LANE - 3, (214, 210, 202))
    d.ellipse((x, y - 3, x + 2, y + 3), outline=C((90, 92, 98)))
    cast_shadow(im, [(x + 2, LANE - 1), (x + 4, LANE - 1), (x + 7, LANE + 1), (x + 5, LANE + 1)], mul=SOFT_MUL)


SOCK_BOX = (SOCK[0] + 1, SOCK[1] - 6, SOCK[0] + 24, SOCK[1] + 9)


def sock_frame(t):
    """风向袋（strip）：橙白相间 5 节，从套环往右伸（风往右吹），节节往下垂一点、像波浪一样一节节抖。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    x0, y0 = SOCK[0] + 2, SOCK[1]
    L = 20
    for k in range(L):
        u = k / (L - 1)
        hw = 2.6 - 1.6 * u
        yc = y0 + 2.0 * u * u + 1.2 * u * math.sin(math.tau * f / N_ANIM - u * 4.2)
        seg = int(u * 4.99)
        c = (236, 104, 40) if seg % 2 == 0 else (246, 244, 236)
        a, b = int(round(yc - hw)), int(round(yc + hw))
        for y in range(a, b + 1):
            cc = c if y < b else dk(c, 0.78)
            if y == a:
                cc = lt(c, 0.2)
            px(d, x0 + k, y, cc)
    return finish(im)


# ============================================================ 会动的小东西：炊烟 / 山羊 / 母鸡 / 树冠
SMOKE_BOX = (OVEN[0] - 6, 92, OVEN[0] + 26, OVEN[1] - 1)


def smoke_frame(t):
    """泥烤炉的炊烟（strip）：一团团从炉口冒出来，越往上越大、越淡（像素越稀），往右飘（和风向袋同一个风向）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    ox, oy = OVEN
    for i in range(6):
        u = ((f / N_ANIM) + i / 6.0) % 1.0
        y = oy - 2 - u * 36
        x = ox + u * u * 18 + 1.5 * math.sin(u * 6 + i)
        r = 1.0 + u * 3.2
        dens = 0.95 - u * 0.75
        for yy in range(int(y - r), int(y + r) + 1):
            for xx in range(int(x - r), int(x + r) + 1):
                if (xx - x) ** 2 + (yy - y) ** 2 <= r * r and hash01(xx, yy, i, 61) < dens:
                    if SMOKE_BOX[0] <= xx < SMOKE_BOX[2] and SMOKE_BOX[1] <= yy < SMOKE_BOX[3]:
                        px(d, xx, yy, (238, 234, 228) if yy < y else (210, 206, 202))
    return finish(im)


@lru_cache(maxsize=8)
def goat_img(pose, tail):
    """山羊（16×13，朝左）：黑褐身子、白脸 + 白肚、往后弯的短角、山羊胡；pose 0 = 低头啃草、1 = 抬头嚼、2 = 抬头看；
    tail 尾巴翘 0/1。"""
    im = A._new(16, 13)
    d = ImageDraw.Draw(im)
    body, body_hi, body_d = (78, 60, 50), (110, 88, 70), (52, 40, 34)
    white = (236, 230, 218)
    rect(d, 5, 4, 13, 8, body)                                       # 身子
    hl(d, 5, 13, 4, body_hi)
    hl(d, 6, 12, 8, white)                                           # 白肚
    for x in (6, 8, 11, 13):                                         # 腿
        vl(d, x, 9, 12, body_d if x in (8, 13) else body)
    px(d, 14, 4 - tail, body)                                        # 尾巴
    px(d, 14, 5, body)
    if pose == 0:                                                    # 低头：头在左下（啃草）
        hd = [(2, 8), (3, 8), (4, 8), (2, 9), (3, 9), (1, 10), (2, 10)]
        neck = [(4, 6), (4, 7), (5, 5)]
        horn = [(4, 6), (5, 5)]
        beard = (1, 11)
        eye = (3, 8)
    else:
        hd = [(1, 2), (2, 2), (3, 2), (1, 3), (2, 3), (3, 3), (0, 4), (1, 4), (2, 4)]
        neck = [(3, 4), (4, 4), (4, 5), (5, 5)]
        horn = [(3, 1), (4, 0)] if pose == 1 else [(3, 1), (4, 1)]
        beard = (1, 5)
        eye = (2, 3)
    for (x, y) in neck:
        px(d, x, y, body)
    for (x, y) in hd:
        px(d, x, y, white)
    for (x, y) in horn:
        px(d, x, y, (170, 150, 120))
    px(d, *beard, (200, 196, 186))
    px(d, *eye, (30, 24, 22))
    return P.outline(im, (40, 30, 26))


GOAT_XY = (268, 133)
GOAT_SEQ = [(0, 0), (0, 1), (0, 0), (1, 1), (1, 0), (2, 1), (2, 0), (1, 1)]
GOAT_BOX = (GOAT_XY[0] - 1, GOAT_XY[1] - 1, GOAT_XY[0] + 18, LANE)


def goat_frame(t):
    """啃草的山羊（strip）：低头啃两下 → 抬头嚼 → 抬头四下看 → 嚼，尾巴一直在抖。"""
    im = A._new(PW, H)
    f = fidx(t, FPS_ANIM, N_ANIM)
    pose, tail = GOAT_SEQ[f]
    paste(im, goat_img(pose, tail), GOAT_XY[0], GOAT_XY[1])
    return finish(im)


HEN_SPOTS = [(308, 144, 0), (316, 145, 1), (326, 143, 2)]
HEN_BOX = (304, 136, 334, LANE + 1)


def hen(d, x, y, pose, col):
    """一只母鸡（朝左，6×5）：身子 + 翘起的尾巴、红鸡冠；pose 0 = 站、1 = 低头啄、2 = 抬头。"""
    rect(d, x + 1, y - 3, x + 4, y - 1, col)
    px(d, x + 5, y - 4, dk(col, 0.8))
    px(d, x + 5, y - 3, col)
    hl(d, x + 2, x + 4, y - 2, dk(col, 0.86))                      # 翅膀
    if pose == 1:
        px(d, x, y - 1, col)
        px(d, x - 1, y, (220, 170, 60))
        px(d, x, y - 2, (210, 50, 44))
    elif pose == 2:
        px(d, x + 1, y - 5, col)
        px(d, x + 1, y - 4, col)
        px(d, x, y - 4, (220, 170, 60))
        px(d, x + 1, y - 6, (210, 50, 44))
    else:
        px(d, x, y - 3, col)
        px(d, x - 1, y - 3, (220, 170, 60))
        px(d, x, y - 4, (210, 50, 44))
    px(d, x + 2, y, (200, 150, 60))
    px(d, x + 3, y, (200, 150, 60))


def hens_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    seq = (0, 1, 1, 0, 2, 0, 1, 0)
    for i, (x, y, sd) in enumerate(HEN_SPOTS):
        hop = 1 if (i == 1 and f in (3, 4)) else 0
        hen(d, x - hop, y, seq[(f + i * 3) % N_ANIM], ((236, 230, 218), (176, 112, 62), (212, 196, 170))[i])
    return finish(im)


def palms_frame(t):
    """三棵枣椰树的树冠（strip，一棵一条）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    for (x, base, top, lean, sd, L) in PALMS:
        palm_crown(d, x + lean, top, L, f, sd)
    return finish(im)


# ============================================================ 电线杆 / 影子 / 组装
def draw_poles(im):
    """三根木电线杆（横担 + 两个白瓷瓶），杆和杆之间、杆到画面外拉两根电线（y 30–46，都在对白框高度）。"""
    d = ImageDraw.Draw(im)
    tops = {129: 26, 336: 28, 452: 30}
    for x, top in tops.items():
        vl(d, x, top, LANE - 1, (128, 100, 72))
        vl(d, x + 1, top, LANE - 1, (96, 74, 54))
        hl(d, x - 5, x + 6, top + 3, (110, 86, 62))
        for xx in (x - 4, x + 5):
            px(d, xx, top + 2, (236, 236, 230))
        for yy in range(top + 10, LANE - 2, 9):
            px(d, x + 1, yy, (70, 54, 40))
        cast_shadow(im, [(x + 2, LANE - 1), (x + 5, LANE - 1), (x + 10, LANE + 3), (x + 7, LANE + 3)], mul=SOFT_MUL)
        d = ImageDraw.Draw(im)
    for (dy, sag) in ((0, 9), (1, 10)):
        xs = [(-4, 30)] + [(x - 4 + dy * 9, tops[x] + 2) for x in (129, 336, 452)] + [(SHED[0] + 4, 90)]
        for (a, b) in zip(xs, xs[1:]):
            V.wire(d, a[0], a[1] + dy, b[0], b[1] + dy, sag if b[0] - a[0] > 60 else 3, (60, 54, 52))
    for (x0, x1, k) in ((150, 190, 3), (360, 400, 2)):                  # 停在下面那根电线上的麻雀（静的，几个点）
        for i in range(k):
            x = x0 + int((x1 - x0) * (i + 0.5) / k)
            y = None
            for yy in range(20, 60):
                if im.getpixel((x, yy))[3] > 0 and im.getpixel((x, yy))[:3] == C((60, 54, 52))[:3]:
                    y = yy
            if y is None:
                continue
            px(d, x, y - 1, (110, 90, 70))
            px(d, x + 1, y - 1, (90, 74, 60))
            px(d, x, y - 2, (130, 108, 84))
            px(d, x + 2, y - 1, (70, 60, 50))


def draw_front_shade(im):
    """画面最下沿（y 173–179）：镜头前面一棵椰树投下来的斑驳叶影（只压暗、不加东西；隔一段一片，可走带还是平的）。"""
    m = np.zeros((H, PW), bool)
    for i in range(16):
        cx = hrange(0, PW, i, 97)
        for k in range(7):
            ang = hrange(-0.6, 0.6, i, k, 98)
            L = hrange(8, 18, i, k, 99)
            for j in range(int(L)):
                x = int(round(cx + math.cos(ang) * j * (1 if k % 2 else -1)))
                y = int(round(179 - abs(math.sin(ang)) * j * 0.4 - (k % 3)))
                if 0 <= x < PW and 173 <= y < H:
                    m[y, x] = True
                    if j % 3 == 0 and y + 1 < H:
                        m[y + 1, x] = True
    P.mul_mask(im, m, SOFT_MUL)


def draw_shadows(im):
    """立着的东西往右下投在地上的淡影：房子的墙脚、摊子、井、清真寺、铁皮棚。"""
    for (a, b) in ((0, 24), (STALL[0], H1[0]), H1, (H2W[0], H2[1]), H3, MOSQUE, (SHED[0], SHED[1])):
        cast_shadow(im, [(a + 3, LANE), (b + 1, LANE), (b + 4, LANE + 2), (a + 5, LANE + 2)], mul=SOFT_MUL)


def finish(im):
    """近景和贴在近景上的 strip 用同一套调色 + 可走带后面压对比（不然 strip 框边上会有色差）。"""
    im = A._grade(im, sat=0.96, val=1.0)
    P.compress_band(im, 108, LANE, (196, 170, 132), k=0.14, ramp=10)
    return im


@lru_cache(maxsize=1)
def near_img():
    im = A._new(PW, H)
    draw_ground(im)
    d = ImageDraw.Draw(im)
    for i, (x, base, top, lean, sd, L) in enumerate(PALMS):
        palm_trunk(d, x, base, top, lean)
    draw_entrance(im)
    draw_pen_back(im)
    d = ImageDraw.Draw(im)
    draw_fence(d, im)
    draw_stall(im)
    draw_h1(im)
    draw_h2(im)
    draw_h3(im)
    draw_well(im)
    draw_mosque(im)
    draw_shed(im)
    draw_sock_pole(im)
    draw_runway_fence(im)
    draw_poles(im)
    draw_shadows(im)
    draw_front_shade(im)
    im = finish(im)
    return opaque(im)


STRIPS = [('camels', CAMEL_BOX, N_ANIM, FPS_ANIM, camels_frame)] + \
         [('palm_%d' % i, palm_box(i), N_ANIM, FPS_ANIM, palms_frame) for i in range(len(PALMS))] + \
         [('cloths', CLOTH_BOX, N_ANIM, FPS_ANIM, cloths_frame),
          ('laundry', LAUNDRY_BOX, N_ANIM, FPS_ANIM, laundry_frame),
          ('smoke', SMOKE_BOX, N_ANIM, FPS_ANIM, smoke_frame),
          ('goat', GOAT_BOX, N_ANIM, FPS_ANIM, goat_frame),
          ('hens', HEN_BOX, N_ANIM, FPS_ANIM, hens_frame),
          ('sock', SOCK_BOX, N_ANIM, FPS_ANIM, sock_frame)]


@lru_cache(maxsize=1)
def build():
    return dict(sky=sky_img(), clouds=clouds_img(), far=far_img(), mid=mid_img(), near=near_img())


def compose(camX, t=0.5):
    """直接拼一帧（不经导出），自检 / 预览用。"""
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    o = int(math.floor(camX * CLOUD_K + t * CLOUD_VX)) % 640
    cl = P.tile(R['clouds'], 1280)
    paste(out, cl.crop((o, 0, o + W, cl.height)), 0, 0)
    for key, k in (('far', FAR_K), ('mid', MID_K)):
        ox = math.floor(camX * k)
        out.alpha_composite(R[key].crop((ox, 0, ox + W, H)))
    bird = V.kite_bird_img()
    for (y, vx, k, x0) in BIRDS:
        x = (x0 + t * vx - camX * k) % 460 - 100
        paste(out, bird, math.floor(x), y)
    out.alpha_composite(R['near'].crop((camX, 0, camX + W, H)))
    for (name, box, n, fps, fn) in STRIPS:
        paste(out, fn(t).crop(box), box[0] - camX, box[1])
    return out


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0)]
    cim, cy = BJ.crop_rows(R['clouds'])
    layers.append(dict(type='wrap', image=ex.img('clouds', BJ.tile_to(cim, 640, 640 + W)), period=640, k=CLOUD_K, y=cy,
                       vx=CLOUD_VX))
    for key, k in (('far', FAR_K), ('mid', MID_K)):
        im, y = BJ.crop_rows(R[key])
        layers.append(dict(type='pano', image=ex.img(key, im), k=k, x=0, y=y))
    bk = ex.img('kite_bird', V.kite_bird_img())
    layers.append(dict(type='clouds', span=460, clouds=[dict(image=bk, x0=float(x0), y=y, vx=vx, k=k)
                                                       for (y, vx, k, x0) in BIRDS]))
    nim, ny = BJ.crop_rows(R['near'])
    layers.append(dict(type='pano', image=ex.img('near', nim), k=1.0, x=0, y=ny))
    for (name, box, n, fps, fn) in STRIPS:
        layers.append(ex.bake(name, box, n, fps, fn, screen=False, k=1.0))
    anchors = dict(ANCHORS)
    anchors.update(runway=[RUNWAY[0], LANE, PW, H], parking=[PARK[0], LANE, PARK[1], WALK[1]], windsock=[SOCK[0] + 1, SOCK[1]],
                   oven=list(OVEN), camels=[[x + (29 if face > 0 else 18), y + 29] for (x, y, face) in CAMEL_XY],
                   palms=[[x + lean, top] for (x, base, top, lean, sd, L) in PALMS],
                   doors=[[205, 101, 225, LANE], [283, 101, 302, LANE], [317, 116, 333, LANE], [412, 96, 433, LANE]],
                   well_box=[WELL[0] - 2, 101, WELL[1] + 3, LANE], stall_box=[STALL[0] - 4, 94, STALL[1] + 4, LANE],
                   shed_box=[SHED[0] - 2, 88, SHED[1] + 3, LANE], minaret=[(MINARET[0] + MINARET[1]) // 2, 33],
                   lane_back=LANE)
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    P.check_no_black(ex, BJ, st, list(range(0, PW - W + 1, 40)), (0.0, 0.75, 1.5), ({},), '亚普林村')
    ex.checked('天空底图整张不透明', int((np.array(R['sky'])[..., 3] != 255).sum()))
    a = np.array(R['near'])
    ex.checked('近景 地面（y 146–180）整条不透明', int((a[LANE:, :, 3] != 255).sum()))
    P.check_alpha01(ex, '近景', R['near'])
    ma = np.array(R['mid'])
    ex.checked('中景 沙地（y 120–150）整条不透明（跑道后面不会露天）', int((ma[120:151, :, 3] != 255).sum()))
    P.check_strips(ex, BJ, STRIPS)
    P.check_wraps(ex, BJ, st)
    P.check_anchor_inside(ex, st['anchors'], PW, WALK, STAND)
    # 停机位 / 站人的地方近景里只有平地（塞斯纳是剧情道具，底图那里只能是跑道的颜色）
    P.check_flat_spots(ex, R['near'], [(x, 176) for x in range(PARK[0] + 10, PARK[1] - 9, 20)], RUN, 26,
                       '停机位 x 555–615（y 147–175）只有跑道（离跑道色太远、又不是影子的像素）', half_w=10, up=29, down=0,
                       y_min=LANE + 1)
    spots = [tuple(ANCHORS[k]) for k in ('arrive', 'camel_pen', 'stall', 'kids', 'mother', 'well', 'merchant', 'exit')]
    P.check_flat_spots(ex, R['near'], spots, GRD, 34, '站人的锚点脚下（±8，往上 8 行）只有平地（离路面色太远、又不是影子的像素）',
                       half_w=8, up=8, down=4, y_min=LANE + 1)
    for camX in (0, 120, 200, 320):
        for t in (0.0, 1.25):
            got = BJ.ref_render(st, ex.images, camX, t, {})
            ex.checked('亚普林村 camX=%d t=%.2f 导出 vs 直接拼' % (camX, t), BJ.ndiff(got, compose(camX, t)))
    nm = P.lum(a[..., :3].astype(np.float32))
    ex.note('可走带亮度：y148–176 均值 %.0f 标准差 %.1f；后沿 y110–145 均值 %.0f 标准差 %.1f' %
            (nm[148:177].mean(), nm[148:177].std(), nm[110:146].mean(), nm[110:146].std()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch6', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        compose(camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'yaprin_village_solo_%d.png' % camX))
    print('ok')
