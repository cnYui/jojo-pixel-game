# -*- coding: utf-8 -*-
r"""karachi_street —— 第5章「卡拉奇」：下午热闹的集市街（地图 karachi_ch5：问路 + 第 11 战「恋人」线 B）。
2026-10-18 ch5-town 组按体验版精度重画（改前是 ch5_scenes.karachi()：一排平涂方块楼 + 三个色块棚子）。
殖民时期的拱廊楼（砂岩 / 粉砂岩、绿百叶、木阳台、铁阳台、宝瓶栏杆）和当地的水泥楼混在一起，墙上挂满乌尔都文招牌
（只画色块和像 Nastaliq 的笔画，读不出字），电线乱拉，远处一座清真寺的绿圆顶和宣礼塔，天上飘着风筝。
调色和零件：ch5_town_parts.py（窗 / 檐口 / 阳台 / 铺子里面 / 路人用 calcutta_street 的，第4章同一套画法）。

地图 640 宽、ground 160、可走带 y 148–176（被晒得发白的旧柏油路，压低了对比）；侧视平视，下午的太阳在左上（影子往右下）。
竖向：楼脚 / 拱廊地面 y 137；人行道水泥板 138–144、路缘石顶 145（亮）/ 侧面 146–147（暗）；148 起是马路。
摊子、车、路人都在 y ≤ 147（可走带后面）。
从左到右（世界坐标）：
  x 0–60     B1 砂岩拱廊楼：宝瓶栏杆女儿墙 + 瓶饰、三楼绿百叶拱窗、二楼一整条木阳台、一楼两个拱（杂货铺 / 铜器铺）
  x 60–126   B2 当地的青绿色水泥楼：屋顶水箱 + 电视天线、窗上的水泥遮阳板、铁栏杆阳台上晾着衣服、一楼卷帘门拉起一半 +
             红底招牌（芒果图标）；门口水果摊（anchors.fruit / fruit_vendor）：竹竿撑着条纹布篷（下摆 strip 飘）、
             篷下挂几串香蕉、木台上一堆芒果 / 一筐石榴 / 一杆秤、台前地上一堆西瓜（切开一个）
  x 126–206  B3 黄砂岩三拱拱廊楼（最高）：山花 + 刻字的小牌、三楼带三角楣的窗、二楼通长铁阳台、拱上一条绿底招牌
             （茶杯图标）；门口茶摊（anchors.tea）：木台上煤油炉 + 大铝壶（热气 strip）、一摞玻璃茶杯、一只大锅、
             铁皮饼干罐；三张矮木凳上坐着两个喝茶的人
  x 206–262  空地（anchors.dan / command：斯蒂利·丹站着问路的地方）：左边一面墙上画着手绘电影海报（大胡子男主角、
             女主角、一把枪、红色的标题笔画），右边一条往里退的小巷（尽头一户人家），巷口一棵老楝树（树干刷了白圈）、
             树下靠着一张绳床（charpai），人行道上一只英国时代留下来的红色邮筒
  x 262–340  B5 粉砂岩拱廊楼：屋角一座小亭（chhatri）、三楼四扇拱窗、二楼雕花木阳台、一楼三个拱，中间是手镯铺；
             门口手镯摊（anchors.bracelet 台面 / vendor 老板站的点）：布篷、五根竖杆上一串串玻璃手镯（五颜六色，
             strip 一闪一闪地反光）、台面上一盘盘手镯、旁边一张空着的小凳（老板在剧情里站着）
  x 340–400  B6 布店：二楼木阳台 + 蓝底招牌，一楼敞开的铺面（一卷卷布、挂着的几条布帘 strip 晃）、红白条纹布檐
             （anchors.girl：穿裙子的女孩站在布檐下）
  x 400–456  B7 奶白拱廊楼：两个拱（药房 / 裁缝），三楼窗 + 遮阳板；楼前路边一个排水口
  x 407–433  马路中间横着一条排水沟（anchors.bridge / bridge_box）：沟从路缘一直通到路的前沿，大部分盖着水泥盖板，
             中间 y 164–175 那一截盖板缺了——一条平平的暗缝（里面一点脏水反光 strip），人能走过去（承太郎趴下当桥）
  x 456–542  B8 汽车站售票处：楼上一块大红招牌（巴士图标）；楼前（x 452–540）停着一辆花纹巴士（anchors.bus，车头朝左：
             车头上的“王冠”木雕、镀铬保险杠、彩色镶片、车身上的花鸟图案、一排窗、车门、车顶行李架上堆着包袱 / 铁皮箱 /
             一辆自行车；保险杠下面一排链子流苏 strip 晃）
  x 542–640  B9 修车铺 + 一栋矮楼：敞着的车库（一摞轮胎、油桶、工具）、手绘招牌；路边一根蓝底白 P 的停车牌；
             右端路面上画着白线的停车位（anchors.jeep 停车位中心；吉普是剧情道具，底图不画车）
头顶：三根水泥电线杆（x 130 / 336 / 548，一根带变压器）和楼之间乱拉的电线；镜头前面头顶还有几根（fg）。
光：下午的太阳在左上：立面左沿亮、右沿暗，檐口 / 阳台 / 布篷下一道影，拱廊里很深的影；摊子的影子落在人行道上偏右。
可走带后面（y 108–147）往中间色收了 15 % 对比。

图层（从后往前）：
  sky       static           320×180 下午的天（上面偏蓝、往下发黄发白，一层薄薄的尘霾）+ 左上的太阳
  clouds    wrap   k 0.1  vx 1.0   扁扁的淡云（640 循环）
  far       pano   k 0.25          远景 400 宽：清真寺（绿圆顶 + 两根宣礼塔）、更远的圆顶、平顶楼、水塔、几棵椰子树（罩着尘霾）
  kites     strip  k 0.25          天上三只纸风筝（菱形 + 尾巴 + 线）在风里点头、摆（8 帧 @4 fps）
  mid       pano   k 0.55          中景 496 宽：一片屋顶（水箱、天线、晾衣绳、鸽子笼、广告牌的铁架背面、一座小清真寺的宣礼塔、树冠）
  pigeons   strip  k 0.55          屋顶上空绕圈的一群鸽子（8 帧 @4 fps）
  near      pano   k 1             整条街（640 宽，不透明）
  tarp      strip  k 1             水果摊布篷的下摆（8 帧 @4 fps）
  steam     strip  k 1             茶壶的热气（8 帧 @4 fps）
  bangles   strip  k 1             手镯一闪一闪的反光（8 帧 @4 fps）
  cloth     strip  k 1             布店门口挂着的布帘晃（8 帧 @4 fps）
  drain     strip  k 1             排水沟缺口里脏水的反光（8 帧 @4 fps）
  chains    strip  k 1             巴士保险杠下面的链子流苏（8 帧 @4 fps）
  fg: wires pano   k 1.2           镜头前面头顶的几根电线（只在 y < 30，不挡人）
锚点（规格要求的名字一个不少，值照规格）：
  arrive [40,163]、fruit [86,153]、fruit_vendor [100,160]、tea [170,155]、dan [232,162]、command [232,162]、bracelet [300,155]、
  vendor [318,160]、girl [356,164]、bridge [420,170]、bridge_box [407,166,433,174]、bus [496,150]、jeep [596,161]
  另外多导出：walk_x [8,632]、fruit_box、tea_box、bangle_box、poster_box、awning_box、drain_box [407,148,433,180]、
  bus_box、parking_box [558,149,636,173]、lane_back 145。
单独运行：python -B tools\bg_new\karachi_street.py → tools\bg_new\_preview\ch5\karachi_dev\*.png
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _parts():
    key = 'bg_new_ch5_town_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'ch5_town_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402

V, K = P.V, P.K
C = A._c4
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
mul_box, cast_shadow, mottle, opaque = P.mul_box, P.cast_shadow, P.mottle, P.opaque
SHADOW_MUL, SOFT_MUL = P.SHADOW_MUL, P.SOFT_MUL

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (148, 176)
CLOUD_K, CLOUD_VX = 0.1, 1.0
FAR_K, MID_K, FG_K = 0.25, 0.55, 1.2
FARW = P.layer_w(PW, FAR_K)       # 400
MIDW = P.layer_w(PW, MID_K)       # 496
FGW = P.layer_w(PW, FG_K)         # 704
BASE = 137                        # 楼脚 / 拱廊地面
SIDE = 138                        # 人行道 138–144
KERB = 145                        # 路缘石顶（亮），146–147 侧面（暗）
ROAD = 148
N_ANIM, FPS_ANIM = 8, 4.0

B1 = (0, 60)
B2 = (60, 126)
B3 = (126, 206)
OPEN = (206, 262)
B5 = (262, 340)
B6 = (340, 400)
B7 = (400, 456)
B8 = (456, 542)
B9 = (542, 640)
FRUIT = (62, 118)
TEA = (138, 198)
BANGLE = (278, 322)
DRAIN = (407, 433)
DRAIN_OPEN = (164, 175)
BUS = (452, 540)
PARK = (558, 636)
POLES = (130, 336, 548)

ANCHORS = dict(
    arrive=[40, 163], fruit=[86, 153], fruit_vendor=[100, 160], tea=[170, 155], dan=[232, 162], command=[232, 162],
    bracelet=[300, 155], vendor=[318, 160], girl=[356, 164], bridge=[420, 170], bridge_box=[407, 166, 433, 174],
    bus=[496, 150], jeep=[596, 161], walk_x=[8, 632],
)
STAND = ('arrive', 'fruit', 'fruit_vendor', 'tea', 'dan', 'command', 'bracelet', 'vendor', 'girl', 'bridge', 'jeep')

# ============================================================ 调色
INK = (40, 32, 30)
SKY_STOPS = [(104, 158, 200), (130, 176, 210), (166, 196, 214), (200, 210, 206), (222, 214, 190)]
HAZE = (222, 212, 190)
SAND = (208, 172, 122)            # 砂岩
SAND_HI = (228, 198, 152)
SAND_S = (184, 148, 104)
PINKST = (206, 146, 124)          # 粉砂岩
YELLOW = (220, 184, 112)
TURQ = (116, 170, 160)
CREAM = (230, 220, 196)
TRIM = (236, 228, 208)
SHUT = (64, 122, 96)
SHUT_B = (70, 112, 150)
WOOD = (122, 82, 54)
WOOD_D = (90, 60, 40)
WOOD_HI = (152, 108, 72)
IRON = (44, 44, 48)
DARK = (54, 44, 40)
WALKC = (174, 166, 150)           # 人行道水泥板
WALK_S = (164, 156, 141)
CURB_HI = (198, 192, 178)
CURB_D = (126, 118, 106)
ASPH = (152, 144, 130)            # 晒白了的旧柏油路
ASPH_S = (145, 137, 124)
ASPH_HI = (159, 151, 137)
PAINT = (222, 218, 206)           # 路面白线
CLOTH = [(214, 52, 74), (240, 196, 56), (64, 132, 196), (238, 120, 168), (90, 168, 96), (246, 140, 40),
         (150, 80, 170), (244, 238, 224)]
BANGLE_C = [(220, 40, 60), (40, 150, 90), (50, 90, 200), (240, 190, 60), (230, 90, 170), (140, 60, 190), (40, 170, 190),
            (250, 120, 40)]


# ============================================================ 天 / 云 / 远景 / 中景
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), SKY_STOPS, bands=12)
    A._glow(im, 44, 26, 46, 36, (255, 244, 214), 74, rings=5)
    d = ImageDraw.Draw(im)
    d.ellipse((38, 20, 50, 32), fill=C((255, 246, 220)))
    d.ellipse((40, 22, 48, 30), fill=C((255, 254, 244)))
    return im


@lru_cache(maxsize=1)
def clouds_img():
    im = A._new(640, 60)
    pal = ((255, 252, 244), (242, 238, 230), (220, 218, 214), (200, 198, 200))
    for i in range(4):
        w = hrange(50, 90, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.22, 0.3, i, 2), 1200 + i, pal)
        cx = (i + hrange(0.1, 0.9, i, 3)) * 640 / 4
        y = 60 - cl.height - int(hrange(4, 26, i, 4))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    return im


@lru_cache(maxsize=1)
def far_img():
    """远景：一片平顶楼、水塔、椰子树，正中一座清真寺（绿圆顶 + 两根宣礼塔），右边更远处一个白圆顶。"""
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    pal = [(214, 196, 168), (226, 214, 192), (204, 184, 158), (220, 206, 178), (200, 190, 176)]
    x, i = 0, 0
    while x < FARW:                                                # 后排的楼（高低错落，几栋 70 年代的方楼）
        w = int(hrange(10, 26, i, 1))
        top = int(hrange(62, 92, i, 2)) if hash01(i, 3) < 0.8 else int(hrange(44, 60, i, 4))
        V.far_block(d, x, w, top, 132, pal[i % 5], i)
        if hash01(i, 5) < 0.35:
            V.water_tank(d, x + 2, top - 6, 6, 5, (196, 192, 184))
        x += w
        i += 1
    cx = 216                                                       # 清真寺（镜头 0 时从空地 / 屋顶上露出来）
    rect(d, cx - 30, 78, cx + 30, 132, (232, 226, 210))
    for xx in range(cx - 28, cx + 29, 6):
        rect(d, xx, 92, xx + 2, 102, (200, 192, 178))
        hl(d, xx, xx + 2, 91, (210, 202, 188))
    hl(d, cx - 31, cx + 31, 78, (246, 242, 232))
    for (dx, r) in ((0, 15), (-21, 6), (21, 6)):                   # 绿圆顶（大）+ 两个小的
        d.ellipse((cx + dx - r, 78 - r * 1.6, cx + dx + r, 78 + 2), fill=C((76, 150, 110)))
        d.chord((cx + dx - r, 78 - r * 1.6, cx + dx + r, 78 + 2), 280, 80, fill=C((56, 120, 90)))
        d.chord((cx + dx - r, 78 - r * 1.6, cx + dx + r, 78 + 2), 200, 240, fill=C((120, 190, 140)))
        vl(d, cx + dx, int(78 - r * 1.6) - 4, int(78 - r * 1.6), (220, 190, 90))
    for tx in (cx - 38, cx + 38):                                  # 两根宣礼塔
        rect(d, tx - 2, 14, tx + 2, 132, (240, 236, 224))
        vl(d, tx + 2, 14, 132, (212, 204, 190))
        for yy in (34, 60):
            rect(d, tx - 4, yy, tx + 4, yy + 2, (226, 220, 206))
            hl(d, tx - 4, tx + 4, yy + 3, (190, 182, 168))
            for xx in range(tx - 3, tx + 4, 2):
                px(d, xx, yy - 1, (226, 220, 206))
        d.ellipse((tx - 3, 6, tx + 3, 16), fill=C((76, 150, 110)))
        px(d, tx - 1, 8, (120, 190, 140))
        vl(d, tx, 1, 6, (220, 190, 90))
    d.ellipse((318, 70, 340, 92), fill=C((236, 232, 222)))          # 远处一个白圆顶
    rect(d, 316, 82, 342, 132, (226, 220, 206))
    for (tx, ty) in ((60, 70), (120, 76), (268, 72), (370, 66)):    # 椰子树
        for k in range(ty, 132):
            px(d, tx + (k - ty) // 14, k, (126, 110, 90))
        for a in range(8):
            ang = a / 8 * math.tau
            for r in range(1, 9):
                px(d, round(tx + math.cos(ang) * r), round(ty + math.sin(ang) * r * 0.5 + (r * r) / 18), (96, 130, 90))
    ys = np.arange(H, dtype=np.float32)[:, None]
    return P.haze(im, np.clip(0.42 + (ys - 20) / 120 * 0.18, 0.42, 0.6), HAZE)


KITE_BOX = (40, 10, 330, 70)
KITES = [(90, 26, (226, 60, 70)), (196, 18, (250, 210, 60)), (300, 34, (60, 150, 220))]


def kites_frame(t):
    """三只纸风筝（远景坐标）：在风里点头、左右摆，尾巴飘，线一直斜着垂到屋顶后面去。"""
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    for j, (kx, ky, col) in enumerate(KITES):
        ph = math.tau * f / N_ANIM + j * 2.1
        x = kx + round(2 * math.sin(ph))
        y = ky + round(1.5 * math.cos(ph * 1.0 + 0.6))
        for k in range(1, 30):                                     # 线（往右下垂到屋顶后面）
            if k % 2 == 0:
                px(d, x + k // 3, y + 3 + k, (170, 170, 176))
        V.paper_kite(d, x, y, col, tail=6, lean=1 if math.sin(ph) > 0 else -1)
    return im


@lru_cache(maxsize=1)
def mid_img():
    """中景：一片屋顶（水箱、天线、晾衣绳、鸽子笼、广告牌的铁架背面、一座小清真寺的宣礼塔、树冠）。"""
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    pal = [(220, 196, 156), (204, 168, 150), (176, 200, 196), (232, 226, 210), (214, 196, 120), (196, 150, 120)]
    x, i = 0, 0
    while x < MIDW:
        w = int(hrange(22, 40, i, 21))
        top = int(hrange(36, 62, i, 22))
        V.roof_house(im, x, w, top, 132, pal[(i * 3) % len(pal)], 60 + i)
        x += w
        i += 1
    d = ImageDraw.Draw(im)
    mx = 300                                                       # 小清真寺的宣礼塔
    rect(d, mx - 2, 14, mx + 2, 70, (238, 232, 218))
    vl(d, mx + 2, 14, 70, (208, 200, 186))
    rect(d, mx - 4, 34, mx + 4, 36, (226, 218, 204))
    d.ellipse((mx - 3, 8, mx + 3, 16), fill=C((80, 150, 110)))
    vl(d, mx, 4, 8, (220, 190, 90))
    for (bx, by) in ((120, 30), (420, 26)):                         # 广告牌的铁架背面
        rect(d, bx, by, bx + 44, by + 18, (120, 114, 108))
        for xx in range(bx, bx + 45, 6):
            vl(d, xx, by, by + 30, (90, 86, 82))
        d.line((bx, by + 18, bx + 44, by + 30), fill=C((90, 86, 82)))
        d.line((bx + 44, by + 18, bx, by + 30), fill=C((90, 86, 82)))
    for (cx, cy) in ((60, 40), (232, 44), (380, 40)):               # 鸽子笼（屋顶上的木格子）
        rect(d, cx, cy, cx + 12, cy + 8, (150, 120, 86))
        for xx in range(cx + 1, cx + 12, 3):
            vl(d, xx, cy + 1, cy + 7, (90, 70, 52))
        hl(d, cx - 1, cx + 13, cy - 1, (176, 146, 106))
    for (tx, ty, rx, ry, sd) in ((180, 52, 16, 11, 1), (350, 56, 14, 10, 2), (470, 50, 18, 12, 3)):
        vl(d, tx, ty + 6, 132, (100, 84, 66))
        V._canopy(d, tx, ty, rx, ry, 640 + sd, pal=((60, 100, 62), (80, 128, 72), (106, 152, 86), (150, 186, 106)))
    rect(d, 0, 126, MIDW - 1, 140, (190, 176, 150))
    return P.haze(im, 0.18, HAZE)


PIGEON_BOX = (210, 0, 330, 40)


def pigeons_frame(t):
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    cx, cy = 270, 18
    for i in range(9):
        ph = math.tau * (f / N_ANIM + i / 9.0 * 0.6 + hash01(i, 81) * 0.05)
        x = round(cx + (44 + 6 * hash01(i, 82)) * math.cos(ph))
        y = round(cy + (11 + 4 * hash01(i, 83)) * math.sin(ph))
        col = (92, 94, 106) if math.sin(ph) > 0 else (124, 126, 138)
        px(d, x, y, col)
        if (f + i) % 2 == 0:
            px(d, x - 1, y - 1, col)
            px(d, x + 1, y - 1, col)
        else:
            px(d, x - 1, y, col)
            px(d, x + 1, y, col)
    return im


# ============================================================ 近景零件
def urdu_board(im, x0, y0, x1, y1, bg, fg, seed, rows=1, icon=None, border=None, fade=0.0):
    """乌尔都文招牌：铁皮框 + 底色 + 一两行像 Nastaliq 的笔画（从右往左），左边可以带一个小图标；板下落一道影。"""
    d = ImageDraw.Draw(im)
    rect(d, x0, y0, x1, y1, bg)
    rect(d, x0, y0, x1, y1, None, outline=border or dk(bg, 0.6))
    hl(d, x0 + 1, x1 - 1, y0 + 1, lt(bg, 0.22))
    ix = x0 + 2
    cy = (y0 + y1) // 2
    if icon == 'mango':
        d.ellipse((x0 + 2, cy - 3, x0 + 8, cy + 3), fill=C((246, 190, 50)))
        px(d, x0 + 7, cy - 4, (70, 140, 60))
        ix = x0 + 10
    elif icon == 'cup':
        rect(d, x0 + 3, cy - 2, x0 + 7, cy + 3, (240, 236, 224))
        px(d, x0 + 8, cy, (240, 236, 224))
        px(d, x0 + 4, cy - 4, (220, 220, 220))
        px(d, x0 + 6, cy - 5, (220, 220, 220))
        ix = x0 + 11
    elif icon == 'bus':
        rect(d, x0 + 3, cy - 3, x0 + 15, cy + 2, (250, 220, 80))
        for xx in range(x0 + 4, x0 + 14, 3):
            rect(d, xx, cy - 2, xx + 1, cy - 1, (60, 120, 180))
        for wx in (x0 + 5, x0 + 12):
            px(d, wx, cy + 3, (30, 30, 30))
        ix = x0 + 18
    elif icon == 'cross':
        rect(d, x0 + 4, cy - 3, x0 + 6, cy + 3, (60, 170, 90))
        rect(d, x0 + 2, cy - 1, x0 + 8, cy + 1, (60, 170, 90))
        ix = x0 + 11
    elif icon == 'tyre':
        d.ellipse((x0 + 2, cy - 4, x0 + 10, cy + 4), outline=C((40, 40, 44)), width=2)
        ix = x0 + 12
    elif icon == 'bangle':
        for k, c in enumerate(((220, 40, 60), (240, 190, 60), (40, 150, 90))):
            d.ellipse((x0 + 2 + k * 2, cy - 2, x0 + 7 + k * 2, cy + 2), outline=C(c))
        ix = x0 + 13
    hrow = (y1 - y0 - 2) / rows
    for r in range(rows):
        yb = int(y0 + 1 + hrow * (r + 1) - max(1, hrow * 0.25))
        P.urdu_line(d, x1 - 3, ix, yb, fg, seed=seed + r * 7, h=max(3, int(hrow * 0.7)))
    mul_box(im, (x0 + 1, y1 + 1, x1 + 1, y1 + 2), SHADOW_MUL)
    if fade:
        lay = np.array(im).astype(np.float32)
        lay[y0:y1 + 1, x0:x1 + 1, :3] = lay[y0:y1 + 1, x0:x1 + 1, :3] * (1 - fade) + np.array(HAZE) * fade
        im.paste(Image.fromarray(np.clip(lay, 0, 255).astype(np.uint8), 'RGBA'))


def arcade(im, x0, x1, top, col, trim, seed, bays, arch_r=None, sign=None):
    """一楼拱廊：一排半圆拱（拱石亮边、拱心石），拱和拱之间的墩子（墩础 / 墩头线脚），拱里面是很深的廊子影，
    廊子后墙是一间间铺子（calcutta_street.shop_img：先画亮的、再压暗）。bays = [(x, w, 铺子种类)]。"""
    d = ImageDraw.Draw(im)
    rect(d, x0, top, x1 - 1, BASE, col)
    mottle(im, (x0, top, x1 - 1, BASE), col, dk(col, 0.92), lt(col, 0.08), seed, cell=3)
    d = ImageDraw.Draw(im)
    for (bx, bw, kind) in bays:
        r = arch_r or bw // 2
        spring = top + r + 3
        shop = K.shop_img(kind, bw, BASE - top - 2, seed + bx)
        a = np.array(im)
        sa = np.array(shop)
        for xx in range(bw):
            u = (xx + 0.5 - bw / 2) / (bw / 2)
            atop = spring - int(round(r * math.sqrt(max(0.0, 1 - u * u))))
            for yy in range(atop, BASE + 1):
                sy = yy - top - 2
                c = sa[min(max(0, sy), sa.shape[0] - 1), xx, :3].astype(np.float32)
                k = 0.62 + 0.38 * min(1.0, max(0.0, (yy - atop) / max(1, BASE - atop)))   # 廊子里上暗下亮
                a[yy, bx + xx, :3] = (c * k).astype(np.uint8)
                a[yy, bx + xx, 3] = 255
            a[atop - 1, bx + xx, :3] = trim
            a[atop, bx + xx, :3] = (np.array(a[atop, bx + xx, :3], np.float32) * 0.55).astype(np.uint8)
        im.paste(Image.fromarray(a, 'RGBA'))
        d = ImageDraw.Draw(im)
        rect(d, bx + bw // 2 - 1, spring - r - 3, bx + bw // 2 + 1, spring - r, lt(trim, 0.1))   # 拱心石
        for (px0, px1) in ((bx - 3, bx - 1), (bx + bw, bx + bw + 2)):  # 墩头线脚
            rect(d, px0, spring - 1, px1, spring, trim)
        mul_box(im, (bx, spring - r, bx + 1, BASE), SHADOW_MUL)      # 拱洞左沿里的影
    hl(d, x0, x1 - 1, BASE, dk(col, 0.7))
    for x in range(x0, x1):                                         # 拱廊地面比人行道高一阶
        px(d, x, BASE - 1, dk(col, 0.84))
    if sign:
        urdu_board(im, *sign)


def balcony_laundry(d, x0, x1, y, seed):
    """阳台栏杆上搭着的衣服（一件件挂下来）。"""
    x = x0 + 2
    k = 0
    while x < x1 - 4:
        w = int(hrange(3, 7, seed, k, 1))
        h = int(hrange(4, 9, seed, k, 2))
        c = CLOTH[int(hash01(seed, k, 3) * len(CLOTH))]
        rect(d, x, y, x + w - 1, y + h, c)
        vl(d, x + w - 1, y, y + h, dk(c, 0.78))
        hl(d, x, x + w - 1, y, lt(c, 0.2))
        x += w + int(hrange(1, 4, seed, k, 4))
        k += 1


def bg_people(im, people):
    """背景里的路人 / 店里的人：比主角小一圈、颜色压灰（读起来是背景，不会当成能说话的人）。"""
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    for i, pp in enumerate(people):
        x, base, kind, face, h = pp[:5]
        ground = pp[5] if len(pp) > 5 else BASE
        K.person(d, x, base, kind, 900 + i, h=h, face=face, ground=ground)
    lay = A._grade(lay, sat=0.7, val=1.0)
    lay = P.haze(lay, 0.24, (200, 190, 172))
    im.alpha_composite(lay)


# ============================================================ 近景：地面
def draw_ground(im):
    d = ImageDraw.Draw(im)
    rect(d, 0, SIDE, PW - 1, KERB - 1, WALKC)                        # 人行道水泥板
    mottle(im, (0, SIDE, PW - 1, KERB - 1), WALKC, WALK_S, lt(WALKC, 0.05), 301, cell=4, lo=0.25, hi=0.75)
    d = ImageDraw.Draw(im)
    for x in range(0, PW, 12):
        vl(d, x, SIDE, KERB - 1, dk(WALKC, 0.86))
    hl(d, 0, PW - 1, SIDE, dk(WALKC, 0.82))
    hl(d, 0, PW - 1, KERB, CURB_HI)
    rect(d, 0, KERB + 1, PW - 1, ROAD - 1, CURB_D)
    for x in range(0, PW, 9):                                        # 路缘石刷的黑白漆（褪了）
        if (x // 9) % 2 == 0:
            rect(d, x, KERB + 1, x + 8, ROAD - 1, (150, 146, 136))
    rect(d, 0, ROAD, PW - 1, H - 1, ASPH)                            # 马路
    mottle(im, (0, ROAD, PW - 1, H - 1), ASPH, ASPH_S, ASPH_HI, 302, cell=6, lo=0.22, hi=0.78)
    d = ImageDraw.Draw(im)
    for (x, y, w, h) in ((30, 156, 28, 6), (180, 166, 34, 7), (300, 152, 22, 5), (480, 170, 26, 6)):   # 补过的补丁
        rect(d, x, y, x + w, y + h, (140, 133, 121))
        hl(d, x, x + w, y, (148, 141, 128))
    for i in range(36):                                              # 裂缝
        x, y = int(hrange(0, PW, i, 303)), int(hrange(ROAD + 2, H - 1, i, 304))
        for k in range(int(hrange(3, 8, i, 305))):
            px(d, x, y, (136, 129, 117))
            x += 1
            y += (1 if hash01(i, k, 306) < 0.3 else (-1 if hash01(i, k, 306) > 0.75 else 0))
            y = max(ROAD + 1, min(H - 1, y))
    for i in range(70):                                              # 尘土、纸屑、果皮、烟头
        x, y = int(hrange(0, PW, i, 307)), int(hrange(ROAD, H, i, 308))
        c = ((166, 156, 136), (190, 180, 150), (170, 150, 90), (200, 196, 186))[i % 4]
        px(d, x, y, mix(c, ASPH, 0.45))
    for x in range(0, PW, 3):                                        # 路缘下面一道细影
        px(d, x, ROAD, dk(ASPH, 0.92))


def draw_drain(im):
    """横在马路中间的排水沟：从路缘一直通到路的前沿（x 407–433），盖着几块水泥盖板，中间那一截（y 164–175）盖板缺了。"""
    d = ImageDraw.Draw(im)
    a, b = DRAIN
    y0, y1 = DRAIN_OPEN
    for (ya, yb) in ((ROAD, 155), (156, 163), (176, H - 1)):        # 盖板（比路面浅一点、四边一道缝）
        rect(d, a, ya, b - 1, yb, (160, 154, 142))
        hl(d, a, b - 1, ya, (170, 164, 152))
        hl(d, a, b - 1, yb, (130, 124, 114))
        vl(d, a, ya, yb, (130, 124, 114))
        vl(d, b - 1, ya, yb, (136, 130, 118))
        for i in range(6):
            px(d, int(hrange(a + 2, b - 2, ya, i, 311)), int(hrange(ya + 1, yb, ya, i, 312)), (146, 140, 128))
    hl(d, a, b - 1, y0 - 1, (120, 114, 104))                        # 缺口远的那边：沟壁（暗）
    for y in range(y0, y1 + 1):                                      # 缺口：一条平平的暗缝（脏水）
        u = (y - y0) / (y1 - y0)
        for x in range(a, b):
            c = mix((58, 54, 48), (72, 70, 62), u)
            if (x + y) % 7 == 0:
                c = (80, 78, 68)
            px(d, x, y, c)
    hl(d, a, b - 1, y1 + 1, (172, 166, 154))                        # 缺口近的那边：盖板的厚度（亮边）
    for (x, y) in ((a + 3, y0 + 2), (b - 6, y1 - 2), (a + 12, y0 + 5)):   # 沟里的垃圾
        px(d, x, y, (120, 110, 80))
        px(d, x + 1, y, (100, 96, 70))
    rect(d, a + 2, KERB + 1, b - 3, ROAD - 1, (50, 46, 42))          # 路缘上的进水口
    for x in range(a + 3, b - 3, 3):
        vl(d, x, KERB + 1, ROAD - 1, (90, 86, 80))


def draw_parking(im):
    """右端的停车位：路面上画的白线（靠路缘一道 + 两边两道往前斜一点）+ 一个褪了色的 P。"""
    d = ImageDraw.Draw(im)
    a, b = PARK
    hl(d, a, b, ROAD + 1, PAINT)
    for k in range(ROAD + 1, 173):                                   # 两边的线（透视：越近越往外）
        u = (k - ROAD) / 25
        px(d, round(a - u * 3), k, PAINT)
        px(d, round(b + u * 3), k, PAINT)
    for (x, y) in ((a + 30, 160), (a + 52, 166)):                    # 油渍
        for k in range(10):
            px(d, x + k, y + (k % 3 == 0), (128, 122, 112))
    P.text_px(d, b - 12, 163, 'P', (196, 194, 184), font=P.FONT5)
    a2 = np.array(im).astype(np.float32)                             # 白线被车轮磨掉一些（混回路面色）
    for y in range(ROAD, 174):
        for x in range(a - 4, min(PW, b + 5)):
            if hash01(x, y, 321) < 0.22 and abs(a2[y, x, 0] - PAINT[0]) < 4:
                a2[y, x, :3] = mix(PAINT, ASPH, 0.6)
    im.paste(Image.fromarray(np.clip(a2, 0, 255).astype(np.uint8), 'RGBA'))


# ============================================================ 近景：B1 / B2 + 水果摊
def draw_b1(im):
    x0, x1 = B1
    V.facade(im, x0, x1, 24, 95, SAND, 401, streaks=3)
    K.parapet(im, x0, x1 - 1, 14, 'baluster', TRIM, SAND)
    d = ImageDraw.Draw(im)
    K.urn(d, x0 + 2, 14, TRIM)
    K.urn(d, x1 - 3, 14, TRIM)
    for wx in (5, 23, 41):
        K.window(im, wx, 30, 11, 20, 'arch', SHUT, TRIM, state=('closed', 'half', 'open')[wx % 3], seed=wx, hood='flat')
    K.cornice(im, x0, x1 - 1, 56, TRIM, SAND, depth=2)
    for wx in (6, 24, 42):
        K.window(im, wx, 66, 10, 18, 'rect', SHUT, TRIM, state='closed' if wx != 24 else 'half', seed=wx + 1)
    K.wood_balcony(im, x0 + 2, x1 - 3, 72, 88, WOOD, seed=3)
    d = ImageDraw.Draw(im)
    balcony_laundry(d, x0 + 4, x1 - 6, 89, 11)
    K.cornice(im, x0, x1 - 1, 92, TRIM, SAND, depth=2, dentils=False)
    arcade(im, x0, x1, 96, SAND, TRIM, 402, [(4, 24, 'grocery'), (32, 24, 'brass')])
    urdu_board(im, 6, 98, 26, 104, (220, 200, 90), (120, 40, 40), 11, fade=0.0)
    d = ImageDraw.Draw(im)
    rect(d, 52, 60, 57, 82, (196, 48, 52))                           # 墩子上挂的竖招牌
    for k in range(4):
        P.urdu_line(d, 56, 53, 64 + k * 5, (250, 230, 150), seed=40 + k, h=2, dots=False)


def draw_b2(im):
    x0, x1 = B2
    V.facade(im, x0, x1, 34, BASE, TURQ, 411, streaks=4)
    d = ImageDraw.Draw(im)
    V.parapet(im, x0, x1 - 1, 32, TURQ, 'plain')
    d = ImageDraw.Draw(im)
    V.water_tank(d, x0 + 8, 22, 14, 10, (190, 186, 178))
    V.tv_antenna(d, x1 - 14, 12, 20)
    for (wy, bal) in ((42, True), (68, True)):
        for wx in (66, 86, 106):
            K.window(im, wx, wy, 11, 15, 'rect', SHUT_B if wx == 86 else SHUT, (226, 230, 222),
                     state=('closed', 'open', 'half')[(wx // 20 + wy) % 3], seed=wx + wy, hood='chajja')
        if bal:
            K.iron_balcony(im, x0 + 3, x1 - 4, wy + 20, rail_h=6, trim=(214, 220, 214))
            d = ImageDraw.Draw(im)
            balcony_laundry(d, x0 + 5, x1 - 6, wy + 21, 20 + wy)
    d = ImageDraw.Draw(im)
    urdu_board(im, x0 + 3, 90, x1 - 4, 99, (196, 44, 48), (250, 226, 130), 21, icon='mango')
    shop = K.shop_img('grocery', x1 - x0 - 8, BASE - 102, 22)
    paste(im, shop, x0 + 4, 102)
    d = ImageDraw.Draw(im)
    for yy in range(102, 116):                                       # 卷帘门拉起一半
        hl(d, x0 + 4, x1 - 5, yy, (150, 156, 150) if yy % 2 else (170, 176, 170))
    hl(d, x0 + 4, x1 - 5, 116, (90, 96, 92))
    vl(d, x0 + 3, 100, BASE, dk(TURQ, 0.7))
    vl(d, x1 - 4, 100, BASE, lt(TURQ, 0.2))


def draw_fruit_stall(im):
    """水果摊：两根竹竿撑一块条纹布篷（下摆在 strip），篷下横竿挂香蕉；木台上一堆芒果、一筐石榴、一杆秤；台前地上一堆西瓜。"""
    d = ImageDraw.Draw(im)
    a, b = FRUIT
    for xx in (a + 1, b - 1):                                        # 竹竿
        vl(d, xx, 92, BASE + 6, (200, 176, 116))
        vl(d, xx + 1, 92, BASE + 6, (154, 128, 80))
        for yy in range(96, BASE, 7):
            px(d, xx, yy, (232, 210, 154))
    for i in range(a - 2, b + 3):                                    # 篷（上半截，下摆在 strip）
        for yy in range(91, 97):
            c = (226, 120, 60) if ((i - a) // 5) % 2 else (240, 226, 200)
            if yy == 91:
                c = lt(c, 0.25)
            px(d, i, yy, c)
    mul_box(im, (a, 100, b, 104), SHADOW_MUL)
    d = ImageDraw.Draw(im)
    hl(d, a + 2, b - 2, 102, (150, 124, 78))                          # 挂香蕉的横竿
    for (bx, n) in ((a + 8, 4), (a + 20, 5), (b - 20, 4)):
        cx = bx + 2
        vl(d, cx, 102, 104 + n * 3, (110, 104, 56))
        for r in range(n):
            y = 105 + r * 3
            hw = 4 - r // 2
            for k in range(-hw, hw + 1):
                up = 1 if abs(k) >= hw - 1 else 0
                c = (246, 214, 76) if k < 0 else (226, 186, 52)
                if abs(k) == hw:
                    c = (176, 182, 70)
                px(d, cx + k, y - up, c)
                px(d, cx + k, y + 1 - up, (206, 164, 44) if abs(k) < hw else (150, 150, 60))
    cxs = b - 9                                                     # 一杆秤
    vl(d, cxs, 102, 108, (120, 100, 60))
    hl(d, cxs - 6, cxs + 6, 108, (196, 150, 70))
    for sx in (cxs - 6, cxs + 6):
        d.line((sx, 108, sx - 2, 112), fill=C((150, 120, 70)))
        d.line((sx, 108, sx + 2, 112), fill=C((150, 120, 70)))
        hl(d, sx - 3, sx + 3, 113, (220, 170, 70))
    ty = 124                                                        # 木台
    rect(d, a + 2, ty, b - 2, ty + 1, WOOD_HI)
    rect(d, a + 2, ty + 2, b - 2, ty + 3, WOOD_D)
    for lx in (a + 4, b - 5):
        rect(d, lx, ty + 4, lx + 1, BASE + 4, WOOD_D)
    for (cx0, cw, col) in ((a + 8, 14, (176, 132, 82)), (b - 26, 16, (184, 140, 88))):   # 台下的木箱
        rect(d, cx0, ty + 6, cx0 + cw, BASE + 2, col)
        hl(d, cx0, cx0 + cw, ty + 6, lt(col, 0.25))
        hl(d, cx0, cx0 + cw, ty + 10, dk(col, 0.75))
        vl(d, cx0 + cw, ty + 6, BASE + 2, dk(col, 0.65))
    bx0, bx1 = a + 4, a + 30                                         # 芒果一大堆
    d.ellipse((bx0, ty - 4, bx1, ty + 3), fill=C((170, 130, 70)))
    for i in range(40):
        x = int(hrange(bx0 + 2, bx1 - 3, i, 331))
        y = int(ty - 4 - hrange(0, 10, i, 332) * (1 - abs((x - (bx0 + bx1) / 2) / ((bx1 - bx0) / 2)) ** 2))
        c = ((246, 196, 60), (238, 150, 40), (180, 190, 70), (250, 214, 90))[i % 4]
        rect(d, x, y, x + 2, y + 1, c)
        px(d, x, y, lt(c, 0.3))
        px(d, x + 2, y + 1, dk(c, 0.75))
    gx0, gx1 = b - 24, b - 4                                         # 一筐石榴
    rect(d, gx0, ty - 2, gx1, ty + 3, (150, 108, 62))
    for xx in range(gx0, gx1 + 1, 2):
        vl(d, xx, ty - 1, ty + 3, (126, 90, 52))
    hl(d, gx0, gx1, ty - 2, (190, 146, 90))
    for i in range(14):
        x = gx0 + 1 + (i * 5) % 18 + (1 if (i // 4) % 2 else 0)
        y = ty - 4 - (i // 4) * 2 + (1 if i % 2 else 0)
        if x > gx1 - 2:
            continue
        d.ellipse((x, y - 1, x + 3, y + 2), fill=C((204, 36, 48)))
        px(d, x + 1, y - 1, (240, 96, 96))
        px(d, x + 3, y + 1, (140, 20, 36))
    for i in range(7):                                               # 台前地上一堆西瓜（切开一个）
        cx = a + 12 + (i % 4) * 9 + (i // 4) * 4
        cy = 141 - (i // 4) * 4
        d.ellipse((cx - 4, cy - 3, cx + 4, cy + 3), fill=C((60, 126, 60)))
        for k in (-2, 0, 2):
            vl(d, cx + k, cy - 2, cy + 2, (40, 92, 44))
        px(d, cx - 2, cy - 2, (120, 180, 100))
    cx, cy = a + 48, 141
    d.chord((cx - 5, cy - 4, cx + 5, cy + 4), 180, 360, fill=C((60, 126, 60)))
    d.chord((cx - 4, cy - 3, cx + 4, cy + 3), 180, 360, fill=C((222, 60, 64)))
    for k in (-2, 0, 2):
        px(d, cx + k, cy - 1, (40, 30, 30))
    P.ground_shadow(im, a + 8, b, KERB - 1, depth=2, slant=4)


# ============================================================ 近景：B3 + 茶摊
def draw_b3(im):
    x0, x1 = B3
    V.facade(im, x0, x1, 22, 95, YELLOW, 421, streaks=4)
    d = ImageDraw.Draw(im)
    cx = (x0 + x1) // 2                                              # 山花 + 刻字的小牌
    for k in range(18):
        px(d, cx - 18 + k, 14 - k // 3, TRIM)
        px(d, cx + 18 - k, 14 - k // 3, TRIM)
    hl(d, cx - 18, cx + 18, 15, TRIM)
    rect(d, cx - 8, 9, cx + 8, 14, lt(YELLOW, 0.1))
    P.urdu_line(d, cx + 6, cx - 6, 12, dk(YELLOW, 0.6), seed=51, h=2, dots=True)
    K.parapet(im, x0, x1 - 1, 15, 'baluster', TRIM, YELLOW)
    for wx in (132, 152, 172, 192):
        K.window(im, wx, 30, 10, 20, 'rect', SHUT, TRIM, state=('closed', 'open', 'closed', 'half')[(wx // 20) % 4],
                 seed=wx, hood='pedi')
    K.cornice(im, x0, x1 - 1, 56, TRIM, YELLOW, depth=2)
    for wx in (132, 152, 172, 192):
        K.window(im, wx, 64, 10, 20, 'arch', SHUT, TRIM, state=('half', 'closed', 'open', 'closed')[(wx // 20) % 4],
                 seed=wx + 3, fan_glass='color')
    K.iron_balcony(im, x0 + 2, x1 - 3, 86, rail_h=7, trim=TRIM)
    for px_ in (x0, x1 - 4):
        K.pilaster(im, px_, 24, 92, TRIM, w=4)
    arcade(im, x0, x1, 96, YELLOW, TRIM, 422, [(130, 24, 'sweets'), (157, 22, 'tailor'), (182, 22, 'pharmacy')])
    urdu_board(im, x0 + 2, 90, x1 - 3, 95, (50, 120, 80), (246, 236, 200), 23, icon='cup')


def draw_tea_stall(im):
    """茶摊：木台（takht）上煤油炉 + 大铝壶（热气在 strip）、一摞玻璃茶杯、一只大锅、铁皮饼干罐；三张矮凳。"""
    d = ImageDraw.Draw(im)
    a, b = TEA
    rect(d, a + 2, 124, a + 40, 126, WOOD_HI)                         # 木台
    rect(d, a + 2, 127, a + 40, 128, WOOD_D)
    for lx in (a + 3, a + 38):
        rect(d, lx, 129, lx + 1, BASE + 4, WOOD_D)
    rect(d, a + 6, 130, a + 34, BASE + 3, (98, 70, 48))               # 台下堆的煤 / 木柴
    for i in range(14):
        px(d, int(hrange(a + 7, a + 33, i, 341)), int(hrange(131, BASE + 2, i, 342)), (60, 50, 44))
    sx = a + 14                                                       # 煤油炉 + 大铝壶
    rect(d, sx - 5, 118, sx + 5, 123, (70, 70, 74))
    hl(d, sx - 5, sx + 5, 118, (110, 110, 116))
    for k in range(sx - 4, sx + 5, 2):
        px(d, k, 121, (240, 140, 50))
    d.ellipse((sx - 5, 109, sx + 5, 119), fill=C((188, 190, 194)))
    d.chord((sx - 5, 109, sx + 5, 119), 290, 70, fill=C((150, 152, 158)))
    d.chord((sx - 5, 109, sx + 5, 119), 190, 240, fill=C((226, 228, 230)))
    rect(d, sx - 2, 107, sx + 2, 109, (176, 178, 184))
    px(d, sx, 106, (120, 120, 126))
    d.line((sx + 4, 112, sx + 8, 109), fill=C((176, 178, 184)))       # 壶嘴
    d.arc((sx - 6, 104, sx + 6, 114), 200, 340, fill=C((90, 90, 96)))  # 提手
    for k in range(3):                                                # 一摞玻璃茶杯
        for j in range(4 - k):
            gx, gy = a + 24 + j * 3 + k, 122 - k * 3
            rect(d, gx, gy, gx + 1, gy + 2, (200, 120, 70) if k == 0 else (210, 220, 220))
    d.ellipse((a + 32, 115, a + 40, 123), fill=C((70, 66, 66)))       # 大锅
    hl(d, a + 32, a + 40, 115, (120, 116, 112))
    rect(d, a + 2, 116, a + 7, 123, (190, 60, 50))                    # 铁皮饼干罐
    hl(d, a + 2, a + 7, 116, (230, 200, 90))
    for (sx0, sy) in ((a + 44, 134), (a + 51, 135), (a + 57, 134)):   # 三张矮凳
        rect(d, sx0 - 3, sy, sx0 + 3, sy + 1, WOOD_HI)
        for lx in (sx0 - 2, sx0 + 2):
            vl(d, lx, sy + 2, KERB - 1, WOOD_D)
    P.ground_shadow(im, a + 2, a + 42, KERB - 1, depth=2, slant=4)


# ============================================================ 近景：空地（电影海报墙 + 小巷 + 楝树 + 邮筒）
def draw_open(im):
    a, b = OPEN
    d = ImageDraw.Draw(im)
    lane0, lane1 = a + 30, b                                          # 小巷（x 236–262）：往里退到尽头一户人家
    for y in range(84, BASE + 1):
        u = (y - 84) / (BASE - 84)
        hl(d, lane0, lane1 - 1, y, mix((214, 200, 170), (176, 160, 134), u))
    rect(d, lane0 + 6, 88, lane1 - 7, 120, (206, 188, 160))           # 巷子尽头那户
    rect(d, lane0 + 12, 104, lane0 + 17, 120, (110, 80, 60))
    rect(d, lane1 - 16, 94, lane1 - 12, 100, (90, 110, 120))
    hl(d, lane0 + 5, lane1 - 6, 87, (226, 214, 190))
    for y in range(120, BASE + 1):                                    # 巷子的地往前铺开
        u = (y - 120) / (BASE - 120)
        hl(d, lane0, lane1 - 1, y, mix((196, 182, 156), (172, 160, 140), u))
    for k in range(4):                                                # 巷子里的晾衣绳
        y = 92 + k * 6
        P.wire(d, lane0, y, lane1 - 1, y + 2, 2, (90, 84, 80))
        for j in range(3):
            c = CLOTH[(k * 3 + j) % len(CLOTH)]
            xx = lane0 + 4 + j * 8 + k
            rect(d, xx, y + 2, xx + 3, y + 6, mix(c, (206, 196, 176), 0.3))
    # 海报墙（x 206–236）：手绘电影海报
    rect(d, a, 58, lane0 - 1, BASE, (216, 204, 180))
    mottle(im, (a, 58, lane0 - 1, BASE), (216, 204, 180), (200, 188, 166), (228, 218, 198), 351, cell=3)
    d = ImageDraw.Draw(im)
    hl(d, a, lane0 - 1, 58, (236, 228, 210))
    pb = (a + 2, 62, lane0 - 3, 118)                                  # 海报
    lay = A._new(PW, H)
    ld = ImageDraw.Draw(lay)
    for y in range(pb[1], pb[3] + 1):
        u = (y - pb[1]) / (pb[3] - pb[1])
        hl(ld, pb[0], pb[2], y, mix((240, 160, 60), (150, 40, 60), u))
    hx, hy = pb[0] + 9, pb[1] + 14                                    # 男主角：大背头、浓眉、八字胡
    ld.ellipse((hx - 6, hy - 7, hx + 6, hy + 8), fill=C((196, 130, 90)))
    ld.chord((hx - 7, hy - 9, hx + 7, hy + 3), 180, 360, fill=C((30, 24, 24)))
    hl(ld, hx - 4, hx - 1, hy, (40, 30, 30))
    hl(ld, hx + 1, hx + 4, hy, (40, 30, 30))
    hl(ld, hx - 3, hx + 3, hy + 4, (40, 30, 30))
    rect(ld, hx - 8, hy + 9, hx + 8, hy + 20, (60, 60, 120))
    gx, gy = pb[0] + 22, pb[1] + 24                                   # 女主角
    ld.ellipse((gx - 4, gy - 5, gx + 4, gy + 5), fill=C((220, 170, 130)))
    ld.chord((gx - 5, gy - 7, gx + 5, gy + 2), 180, 360, fill=C((40, 26, 30)))
    vl(ld, gx - 5, gy - 2, gy + 8, (40, 26, 30))
    px(ld, gx, gy - 2, (200, 40, 50))
    rect(ld, gx - 5, gy + 6, gx + 5, gy + 12, (220, 60, 120))
    ld.line((pb[0] + 2, pb[1] + 40, pb[0] + 14, pb[1] + 36), fill=C((40, 40, 46)), width=2)   # 一把枪
    for k in range(5):                                                # 火光
        px(ld, pb[0] + 15 + k, pb[1] + 35 - (k % 2), (255, 230, 120))
    P.urdu_line(ld, pb[2] - 2, pb[0] + 2, pb[3] - 4, (250, 240, 120), seed=61, h=5, dots=True, dot_col=(255, 255, 220))
    P.urdu_line(ld, pb[2] - 6, pb[0] + 6, pb[3] - 11, (255, 255, 255), seed=62, h=3, dots=False)
    la = np.array(lay).astype(np.float32)                             # 晒褪了色、卷了角
    b2 = np.array(im).astype(np.float32)
    m = la[..., 3] > 0
    n = A._fbm(PW, H, 4, seed=63)
    fq = 0.18 + 0.25 * n[m]
    la[m, :3] = la[m, :3] * (1 - fq[:, None]) + b2[m, :3] * fq[:, None]
    for k in range(4):
        for j in range(4 - k):
            la[pb[3] - k, pb[2] - j, 3] = 0
    im.alpha_composite(Image.fromarray(np.clip(la, 0, 255).astype(np.uint8), 'RGBA'))
    d = ImageDraw.Draw(im)
    for (sx, sy) in ((a + 4, 124), (a + 17, 128)):                    # 墙上贴的小广告
        rect(d, sx, sy, sx + 7, sy + 5, (236, 230, 210))
        P.urdu_line(d, sx + 6, sx + 1, sy + 3, (60, 60, 120), seed=sx, h=2, dots=False)
    mul_box(im, (lane0, 84, lane0 + 2, BASE), SHADOW_MUL)            # 海报墙在巷子里落的影
    # 楝树（树干刷了白圈）+ 树下靠着的绳床
    tx = 248
    for y in range(70, BASE + 1):
        w = 5 if y < 120 else 6
        for k in range(w):
            c = (124, 104, 84) if k < 2 else ((100, 84, 70) if k < w - 1 else (78, 66, 56))
            if y >= 124:
                c = (236, 232, 222) if k < w - 1 else (200, 196, 186)
            px(d, tx - w // 2 + k, y, c)
    d.line((tx, 80, tx - 16, 56), fill=C((110, 92, 74)), width=2)
    d.line((tx + 1, 76, tx + 18, 50), fill=C((110, 92, 74)), width=2)
    for (cx, cy, rx, ry, sd) in ((tx - 8, 46, 22, 14, 1), (tx + 12, 40, 20, 13, 2), (tx, 58, 18, 10, 3)):
        V._canopy(d, cx, cy, rx, ry, 360 + sd, pal=((48, 92, 52), (70, 124, 62), (102, 158, 80), (150, 192, 104)))
    for k in range(18):                                               # 绳床（立着靠在树上）
        y = 112 + k
        hl(d, tx + 4, tx + 13, y, (196, 170, 120) if k % 2 else (170, 146, 100))
    for xx in (tx + 4, tx + 13):
        vl(d, xx, 110, BASE, WOOD_D)
    # 红邮筒
    mx = b - 6
    rect(d, mx - 3, 126, mx + 3, KERB - 1, (196, 40, 36))
    d.pieslice((mx - 4, 121, mx + 4, 130), 180, 360, fill=C((210, 50, 44)))
    hl(d, mx - 2, mx + 2, 129, (40, 30, 30))
    vl(d, mx - 3, 126, KERB - 1, (226, 80, 70))
    vl(d, mx + 3, 126, KERB - 1, (140, 26, 26))
    rect(d, mx - 4, KERB - 2, mx + 4, KERB - 1, (60, 40, 36))
    P.ground_shadow(im, mx - 3, mx + 4, KERB - 1, depth=2)


# ============================================================ 近景：B5 + 手镯摊
def draw_b5(im):
    x0, x1 = B5
    V.facade(im, x0, x1, 28, 95, PINKST, 431, streaks=3)
    K.parapet(im, x0, x1 - 1, 18, 'solid', TRIM, PINKST)
    V.chhatri(im, x1 - 10, 18, 16, 12)
    for wx in (268, 286, 304, 322):
        K.window(im, wx, 34, 10, 20, 'arch', SHUT, TRIM, state=('open', 'closed', 'half', 'closed')[(wx // 18) % 4],
                 seed=wx, fan_glass='color', hood=None)
    K.cornice(im, x0, x1 - 1, 58, TRIM, PINKST, depth=2)
    V.jharokha(im, 276, 62, 48, 22, WOOD, seed=5)
    for wx in (266, 328):
        K.window(im, wx, 66, 8, 16, 'rect', SHUT, TRIM, state='closed', seed=wx)
    K.cornice(im, x0, x1 - 1, 92, TRIM, PINKST, depth=2, dentils=False)
    arcade(im, x0, x1, 96, PINKST, TRIM, 432, [(265, 22, 'cycle'), (292, 22, 'photo'), (317, 20, 'brass')])
    urdu_board(im, 268, 98, 286, 104, (240, 236, 222), (60, 60, 140), 31, icon='bangle')


def draw_bangle_stall(im):
    """手镯摊：布篷、五根竖杆上一串串玻璃手镯（反光在 strip）、台面上一盘盘手镯、台下的柜子、旁边一张空着的小凳。"""
    d = ImageDraw.Draw(im)
    a, b = BANGLE
    for xx in (a + 1, b - 2):                                         # 撑篷的竹竿
        vl(d, xx, 90, KERB - 1, (196, 172, 116))
        vl(d, xx + 1, 90, KERB - 1, (150, 124, 80))
    for i in range(a - 2, b + 2):                                     # 篷（蓝白条）
        sag = int(round(1.2 * math.sin(math.pi * (i - a + 2) / (b - a + 4))))
        for yy in range(90, 96 + sag):
            c = (60, 110, 180) if ((i - a) // 4) % 2 else (236, 236, 230)
            if yy == 90:
                c = lt(c, 0.25)
            elif yy >= 95 + sag:
                c = dk(c, 0.8)
            px(d, i, yy, c)
    mul_box(im, (a, 97, b, 100), SHADOW_MUL)
    d = ImageDraw.Draw(im)
    for k, xx in enumerate(range(a + 6, b - 4, 8)):                    # 竖杆 + 一串串手镯
        vl(d, xx, 98, 127, (120, 96, 66))
        for j, yy in enumerate(range(100, 126, 2)):
            c = BANGLE_C[(k * 3 + j) % len(BANGLE_C)]
            hl(d, xx - 3, xx + 3, yy, c)
            px(d, xx - 3, yy, dk(c, 0.7))
            px(d, xx + 3, yy, dk(c, 0.7))
            px(d, xx - 1, yy, lt(c, 0.35))
            hl(d, xx - 2, xx + 2, yy + 1, dk(c, 0.62))
    rect(d, a, 128, b, 129, WOOD_HI)                                  # 台面 + 一盘盘手镯
    hl(d, a, b, 130, WOOD_D)
    for k, xx in enumerate(range(a + 2, b - 6, 8)):
        rect(d, xx, 126, xx + 6, 127, (200, 190, 170))
        for j in range(3):
            c = BANGLE_C[(k + j * 2) % len(BANGLE_C)]
            hl(d, xx + 1 + j * 2, xx + 2 + j * 2, 125, c)
    rect(d, a + 1, 131, b - 1, KERB - 1, (138, 94, 60))               # 柜子
    hl(d, a + 1, b - 1, 131, (166, 118, 78))
    for xx in range(a + 2, b - 1, 11):
        rect(d, xx, 133, xx + 8, KERB - 3, (124, 84, 54))
        px(d, xx + 4, 138, (210, 180, 90))
    rect(d, b + 2, 136, b + 8, 137, WOOD_HI)                           # 空着的小凳（老板在剧情里站着）
    for lx in (b + 3, b + 7):
        vl(d, lx, 138, KERB - 1, WOOD_D)
    P.ground_shadow(im, a, b + 8, KERB - 1, depth=2, slant=4)


# ============================================================ 近景：B6 布店 / B7
def draw_b6(im):
    x0, x1 = B6
    col = (226, 214, 180)
    V.facade(im, x0, x1, 40, BASE, col, 441, streaks=3)
    V.parapet(im, x0, x1 - 1, 38, col, 'post')
    d = ImageDraw.Draw(im)
    V.water_tank(d, x0 + 30, 28, 12, 9, (180, 176, 170))
    for wx in (346, 364, 382):
        K.window(im, wx, 48, 10, 16, 'rect', SHUT_B, (240, 236, 226), state=('closed', 'half', 'open')[(wx // 18) % 3],
                 seed=wx, hood='chajja')
    K.wood_balcony(im, x0 + 4, x1 - 5, 68, 84, WOOD, seed=7)
    urdu_board(im, x0 + 3, 87, x1 - 4, 95, (50, 80, 160), (250, 240, 200), 41, rows=1)
    shop = K.shop_img('saris', x1 - x0 - 8, BASE - 104, 42)
    paste(im, shop, x0 + 4, 104)
    d = ImageDraw.Draw(im)
    for k, xx in enumerate(range(x0 + 6, x1 - 6, 7)):                  # 架子上一卷卷布
        for j in range(3):
            c = CLOTH[(k + j * 3) % len(CLOTH)]
            rect(d, xx, 114 + j * 6, xx + 5, 117 + j * 6, dk(c, 0.82))
            hl(d, xx, xx + 5, 114 + j * 6, dk(c, 0.92))
    vl(d, x0 + 3, 102, BASE, dk(col, 0.7))
    vl(d, x1 - 4, 102, BASE, lt(col, 0.15))
    for i in range(x0 + 1, x1 - 1):                                   # 红白条纹布檐（女孩站在下面）
        for yy in range(97, 103):
            c = (210, 50, 50) if ((i - x0) // 5) % 2 else (240, 234, 222)
            if yy == 97:
                c = lt(c, 0.2)
            elif yy == 102:
                c = dk(c, 0.75)
            px(d, i, yy, c)
        if (i - x0) % 5 == 2:
            px(d, i, 103, (210, 50, 50))
    mul_box(im, (x0 + 2, 104, x1 - 1, 107), SHADOW_MUL)


def draw_b7(im):
    x0, x1 = B7
    col = (230, 224, 206)
    V.facade(im, x0, x1, 30, 95, col, 451, streaks=4)
    V.parapet(im, x0, x1 - 1, 28, col, 'arch')
    for wx in (406, 424, 442):
        K.window(im, wx, 38, 9, 16, 'seg', SHUT, TRIM, state=('closed', 'open', 'closed')[(wx // 18) % 3], seed=wx,
                 hood='chajja')
    for wx in (406, 424, 442):
        K.window(im, wx, 66, 9, 18, 'rect', SHUT, TRIM, state=('half', 'closed', 'open')[(wx // 18) % 3], seed=wx + 2)
    K.iron_balcony(im, x0 + 2, x1 - 3, 87, rail_h=6, trim=TRIM)
    d = ImageDraw.Draw(im)
    balcony_laundry(d, x0 + 4, x1 - 6, 88, 71)
    arcade(im, x0, x1, 96, col, TRIM, 452, [(404, 22, 'pharmacy'), (430, 22, 'tailor')])
    urdu_board(im, 405, 98, 425, 104, (236, 240, 236), (40, 120, 60), 43, icon='cross')


# ============================================================ 近景：B8 + 花纹巴士
def draw_b8(im):
    x0, x1 = B8
    col = (214, 196, 150)
    V.facade(im, x0, x1, 22, BASE, col, 461, streaks=5)
    V.parapet(im, x0, x1 - 1, 20, col, 'plain')
    d = ImageDraw.Draw(im)
    V.tv_antenna(d, x0 + 12, 8, 14)
    urdu_board(im, x0 + 4, 46, x1 - 5, 64, (200, 36, 40), (255, 226, 90), 51, rows=2, icon='bus')
    for wx in range(x0 + 6, x1 - 8, 16):
        K.window(im, wx, 26, 10, 14, 'rect', SHUT, TRIM, state='closed' if wx % 3 else 'open', seed=wx, hood='chajja')
        K.window(im, wx, 70, 10, 14, 'rect', SHUT, TRIM, state='half' if wx % 2 else 'closed', seed=wx + 1)
    shop = K.shop_img('bank', x1 - x0 - 8, BASE - 92, 52)              # 售票窗口（铁栅）
    paste(im, shop, x0 + 4, 92)


def bus_img():
    """花纹巴士（车头朝左，80 宽）：车身奶白底 + 红金花纹带、一排带铁栏的窗、车门、车头的“王冠”、镀铬保险杠、
    车身下半截绿底白菱形、两个轮子（彩漆轮毂）、车顶行李架上的包袱 / 铁皮箱 / 自行车。返回 (图, 左上角)。"""
    a, b = BUS
    w = b - a
    im = A._new(w + 2, 66)
    d = ImageDraw.Draw(im)
    oy = 147 - 66 + 1                                                 # 图的第 0 行 = 世界 y 82
    Y = lambda y: y - oy  # noqa: E731
    top, belt, skirt, bot = 98, 122, 131, 141
    body = (236, 226, 200)
    rect(d, 4, Y(top), w - 1, Y(bot), body)                           # 车身
    for x in range(4, w):                                             # 腰线以上：红金花纹带
        for y in range(Y(belt), Y(skirt)):
            c = (200, 40, 40) if ((x + y) // 3) % 2 else (230, 180, 60)
            if (x % 8 in (0, 1)) and y == Y(belt) + 3:
                c = (40, 120, 200)
            px(d, x, y, c)
    for x in range(4, w):                                             # 下半截：绿底白菱形 + 镜面小三角
        for y in range(Y(skirt), Y(bot) + 1):
            c = (40, 130, 80)
            if abs((x % 6) - 3) + abs((y - Y(skirt)) % 6 - 3) < 2:
                c = (240, 240, 230)
            px(d, x, y, c)
    hl(d, 4, w - 1, Y(skirt), (220, 210, 120))
    for k, x in enumerate(range(17, w - 6, 9)):                       # 一排窗（铁栏）+ 窗上的小檐
        rect(d, x, Y(top) + 5, x + 7, Y(top) + 15, (60, 74, 86))
        for xx in range(x + 1, x + 8, 2):
            vl(d, xx, Y(top) + 5, Y(top) + 15, (150, 154, 160))
        hl(d, x - 1, x + 8, Y(top) + 3, (220, 60, 60))
        hl(d, x, x + 7, Y(top) + 4, (200, 200, 206))
        hl(d, x - 1, x + 8, Y(top) + 16, (170, 170, 176))
        if k % 2 == 0:                                                # 窗下的花鸟（孔雀蓝 + 粉花）
            px(d, x + 3, Y(top) + 19, (230, 80, 150))
            px(d, x + 2, Y(top) + 20, (60, 160, 80))
            px(d, x + 4, Y(top) + 20, (60, 160, 80))
        else:
            hl(d, x + 1, x + 5, Y(top) + 19, (40, 120, 190))
            px(d, x + 6, Y(top) + 18, (40, 120, 190))
            px(d, x + 2, Y(top) + 20, (240, 200, 60))
    rect(d, 6, Y(top) + 5, 14, Y(bot) - 2, (70, 60, 56))              # 车门（前门，开着；门口挂着一串流苏）
    vl(d, 10, Y(top) + 7, Y(bot) - 3, (190, 190, 196))
    hl(d, 6, 14, Y(bot) - 2, (150, 150, 156))
    for k in range(5):
        px(d, 7 + k * 2, Y(top) + 6, ((230, 40, 50), (240, 200, 60), (40, 160, 90))[k % 3])
    d.polygon([(0, Y(top) + 8), (4, Y(top)), (4, Y(bot)), (0, Y(bot))], fill=C(body))   # 车头（斜一点）
    rect(d, 0, Y(top) + 8, 3, Y(top) + 18, (70, 90, 110))             # 挡风玻璃侧面
    rect(d, 0, Y(bot) - 7, 3, Y(bot) - 4, (250, 236, 170))            # 大灯
    for k in range(4):                                                # 车头上画的一只“眼睛”（truck art 的护身符）
        px(d, 1 + k % 2, Y(top) + 21 + k // 2, ((240, 240, 240), (40, 40, 40))[k % 2])
    for x in range(0, w, 3):                                          # 车顶边一排镜面小三角
        c = ((230, 40, 50), (240, 240, 240), (40, 170, 90))[(x // 3) % 3]
        px(d, x + 4 if x + 4 < w else w - 1, Y(top), c)
        px(d, min(w - 1, x + 5), Y(top) + 1, dk(c, 0.8))
    for k in range(13):                                               # 车头的“王冠”（彩色木雕板，往上翘）
        x = 1 + k
        hh = 9 - abs(k - 6)
        vl(d, x, Y(top) - hh, Y(top) - 1, ((220, 40, 60), (240, 190, 50), (40, 140, 200))[k % 3])
        if k % 2 == 0:
            px(d, x, Y(top) - hh - 1, (255, 236, 150))
    px(d, 7, Y(top) - 11, (255, 230, 120))
    rect(d, 0, Y(bot) + 1, w - 1, Y(bot) + 2, (210, 214, 220))        # 镀铬保险杠 / 底边
    hl(d, 0, w - 1, Y(bot) + 1, (240, 242, 246))
    for (wx) in (16, w - 16):                                          # 两个轮子
        d.ellipse((wx - 6, Y(bot) - 5, wx + 6, Y(bot) + 7), fill=C((30, 30, 32)))
        d.ellipse((wx - 3, Y(bot) - 2, wx + 3, Y(bot) + 4), fill=C((200, 60, 60)))
        d.ellipse((wx - 1, Y(bot), wx + 1, Y(bot) + 2), fill=C((230, 230, 236)))
        d.arc((wx - 8, Y(bot) - 7, wx + 8, Y(bot) + 9), 180, 360, fill=C((60, 60, 64)))   # 挡泥板
    rect(d, 6, Y(top) - 3, w - 2, Y(top) - 2, (110, 110, 116))       # 车顶行李架
    for x in range(6, w - 1, 4):
        vl(d, x, Y(top) - 6, Y(top) - 2, (110, 110, 116))
    rect(d, 16, Y(top) - 12, 32, Y(top) - 4, (180, 60, 60))            # 包袱（红布）、铁皮箱、捆着的草席、自行车、一只鸡笼
    hl(d, 16, 32, Y(top) - 12, (210, 90, 80))
    vl(d, 24, Y(top) - 12, Y(top) - 4, (120, 30, 30))
    rect(d, 34, Y(top) - 9, 48, Y(top) - 4, (60, 110, 160))
    hl(d, 34, 48, Y(top) - 9, (100, 150, 196))
    for x in (37, 45):
        vl(d, x, Y(top) - 9, Y(top) - 4, (200, 190, 120))
    rect(d, 50, Y(top) - 14, 60, Y(top) - 4, (220, 200, 150))
    for y in range(Y(top) - 14, Y(top) - 4, 2):
        hl(d, 50, 60, y, (190, 170, 120))
    for wx in (64, 74):
        d.ellipse((wx - 4, Y(top) - 12, wx + 4, Y(top) - 4), outline=C((40, 40, 44)))
    d.line((64, Y(top) - 8, 69, Y(top) - 13), fill=C((40, 40, 44)))
    d.line((69, Y(top) - 13, 74, Y(top) - 8), fill=C((40, 40, 44)))
    rect(d, 78, Y(top) - 8, 85, Y(top) - 4, (190, 160, 110))
    for x in range(79, 85, 2):
        vl(d, x, Y(top) - 8, Y(top) - 4, (120, 96, 66))
    P.ink(im, INK, sides='all')
    return im, (a, oy)


CHAIN_BOX = (BUS[0] - 1, 142, BUS[1] + 2, 148)


def draw_bus(im):
    bimg, (bx, by) = bus_img()
    im.alpha_composite(bimg, (bx, by))
    cast_shadow(im, [(BUS[0] + 4, KERB - 3), (BUS[1] + 2, KERB - 3), (BUS[1] + 8, KERB), (BUS[0] + 8, KERB)], mul=SOFT_MUL)


# ============================================================ 近景：B9 修车铺 + 停车牌
def draw_b9(im):
    x0, x1 = B9
    col = (200, 186, 160)
    V.facade(im, x0, x1, 60, BASE, col, 471, streaks=4)
    V.parapet(im, x0, x1 - 1, 58, col, 'plain')
    d = ImageDraw.Draw(im)
    V.water_tank(d, x0 + 60, 48, 16, 10, (176, 174, 168))
    V.tv_antenna(d, x0 + 30, 40, 18)
    for wx in (x0 + 8, x0 + 52, x0 + 76):
        K.window(im, wx, 68, 11, 16, 'rect', SHUT_B, TRIM, state='half' if wx % 2 else 'closed', seed=wx, hood='chajja')
    urdu_board(im, x0 + 6, 90, x0 + 50, 99, (240, 200, 60), (40, 40, 60), 61, icon='tyre')
    shop = K.shop_img('godown', 60, BASE - 102, 62)                   # 敞着的车库
    paste(im, shop, x0 + 4, 102)
    d = ImageDraw.Draw(im)
    for k in range(4):                                                # 一摞轮胎
        d.ellipse((x0 + 8, 128 - k * 5, x0 + 22, 134 - k * 5), fill=C((40, 40, 44)))
        d.ellipse((x0 + 12, 130 - k * 5, x0 + 18, 132 - k * 5), fill=C((90, 86, 80)))
    for (dx, c) in ((x0 + 44, (60, 90, 140)), (x0 + 52, (170, 60, 50))):   # 油桶
        rect(d, dx, 122, dx + 7, BASE - 1, c)
        hl(d, dx, dx + 7, 122, lt(c, 0.3))
        for yy in (126, 132):
            hl(d, dx, dx + 7, yy, dk(c, 0.7))
    for k in range(5):                                                # 墙上挂的工具
        vl(d, x0 + 28 + k * 3, 106, 112 + k % 2 * 2, (90, 90, 96))
    K.window(im, x0 + 72, 106, 14, 18, 'rect', SHUT, TRIM, state='closed', seed=99)
    px_ = PARK[0] - 4                                                  # 停车牌（蓝底白 P）
    vl(d, px_, 108, KERB - 1, (140, 144, 150))
    vl(d, px_ + 1, 108, KERB - 1, (100, 104, 110))
    rect(d, px_ - 5, 96, px_ + 6, 108, (40, 90, 170))
    rect(d, px_ - 5, 96, px_ + 6, 108, None, outline=(230, 230, 230))
    P.text_px(d, px_ - 2, 99, 'P', (240, 240, 240), font=P.FONT5)
    P.ground_shadow(im, px_, px_ + 2, KERB - 1, depth=2, slant=4)


# ============================================================ 近景：电线杆 / 电线
def draw_poles(im):
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    for i, x in enumerate(POLES):
        for y in range(18, KERB):
            u = (y - 18) / (KERB - 18)
            w = 2 if u < 0.5 else 3
            for k in range(w):
                c = (200, 196, 186) if k == 0 else ((164, 160, 152) if k < w - 1 else (126, 122, 116))
                px(d, x - 1 + k, y, c)
        for (yy, hw) in ((22, 9), (30, 6)):
            hl(d, x - hw, x + hw, yy, (110, 104, 100))
            for xx in (x - hw, x + hw):
                px(d, xx, yy - 1, (236, 236, 228))
        if i == 1:                                                    # 变压器
            rect(d, x + 2, 40, x + 10, 54, (110, 116, 112))
            hl(d, x + 2, x + 10, 40, (150, 156, 150))
            for yy in range(42, 54, 3):
                hl(d, x + 3, x + 9, yy, (90, 96, 92))
            for k in range(3):
                vl(d, x + 4 + k * 3, 36, 39, (70, 70, 74))
        rect(d, x + 2, 70, x + 5, 78, (176, 172, 160))                # 贴在杆上的小广告
        P.urdu_line(d, x + 5, x + 2, 74, (180, 40, 40), seed=x, h=2, dots=False)
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    WC = (44, 40, 44)
    p1, p2, p3 = POLES
    for (ya, yb, sag) in ((22, 22, 14), (22, 30, 18), (30, 30, 10)):
        P.wire(d, p1 - 9, ya, p2 - 9, yb, sag, WC)
        P.wire(d, p2 + 9, ya, p3 - 9, yb, sag + 2, WC)
    for (x0, y0, x1, y1, sag) in ((0, 30, p1 - 9, 22, 6), (p1 + 9, 22, 206, 50, 4), (p1 - 6, 30, 60, 30, 5),
                                  (p2 - 6, 30, 262, 40, 4), (p2 + 6, 30, 400, 34, 6), (p3 + 9, 22, PW, 18, 6),
                                  (p3 - 6, 30, 470, 30, 5), (p3 + 6, 30, 600, 60, 6), (p1 + 2, 60, 200, 64, 6),
                                  (p2 + 2, 64, 360, 92, 8)):
        P.wire(d, x0, y0, x1, y1, sag, WC)
    for x in POLES:
        P.ground_shadow(im, x - 1, x + 2, KERB - 1, depth=3, slant=5)


@lru_cache(maxsize=1)
def fg_img():
    im = A._new(FGW, 34)
    d = ImageDraw.Draw(im)
    WC = (34, 30, 32)
    for (x0, y0, x1, y1, sag) in ((-10, 2, 340, 8, 14), (260, 0, FGW + 10, 6, 18), (440, 12, FGW + 10, 0, 8)):
        P.wire(d, x0, y0, x1, y1, sag, WC)
    for (cx, cy) in ((160, 18), (590, 16)):
        for k in range(10):
            a = k * 0.7
            px(d, round(cx + 4 * math.cos(a)), round(cy + 2 * math.sin(a * 1.3)), WC)
    return opaque(im)


# ============================================================ 组装近景
PEOPLE = [  # (x, 脚 y, 样式, 朝向, 身高[, 地面 y])：背景里的路人 / 店里的人（压灰、比主角小一圈）
    (20, BASE, 'kurta', 1, 25), (46, BASE, 'shirt', -1, 24), (144, BASE - 1, 'kurta', 1, 24),
    (TEA[0] + 51, 134, 'sit', -1, 0, KERB - 1), (TEA[0] + 57, 133, 'sit', 1, 0, KERB - 1),
    (196, BASE, 'umbrella', -1, 25), (272, BASE, 'shirt', 1, 24), (330, BASE, 'kurta', -1, 25),
    (392, BASE - 1, 'squat', -1, 0), (446, BASE, 'porter', -1, 26), (604, BASE - 2, 'squat', 1, 0),
]


@lru_cache(maxsize=1)
def near_img():
    im = A._new(PW, H)
    draw_ground(im)
    draw_drain(im)
    draw_parking(im)
    draw_b1(im)
    draw_b2(im)
    draw_b3(im)
    draw_open(im)
    draw_b5(im)
    draw_b6(im)
    draw_b7(im)
    draw_b8(im)
    draw_b9(im)
    bg_people(im, PEOPLE)
    draw_fruit_stall(im)
    draw_tea_stall(im)
    draw_bangle_stall(im)
    draw_bus(im)
    draw_poles(im)
    P.compress_band(im, 108, ROAD - 1, 0.85, (176, 160, 136))
    im = A._grade(im, sat=0.96, val=1.0)
    return opaque(im)


# ============================================================ 会动的（strip）
TARP_BOX = (FRUIT[0] - 3, 96, FRUIT[1] + 4, 102)


def tarp_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    a, b = FRUIT
    for x in range(a - 2, b + 3):
        wv = math.sin(math.tau * f / N_ANIM - x * 0.4)
        hem = 98 + (1 if wv > 0.2 else 0) + (1 if wv > 0.8 else 0)
        for yy in range(97, hem + 1):
            c = (226, 120, 60) if ((x - a) // 5) % 2 else (240, 226, 200)
            if yy >= hem:
                c = dk(c, 0.78)
            px(d, x, yy, c)
    return im


STEAM_BOX = (TEA[0] + 10, 76, TEA[0] + 30, 108)


def steam_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    bay = A._bayer(PW, H)
    x0, y0 = TEA[0] + 16, 105
    for i in range(5):
        u = ((f / N_ANIM) + i / 5) % 1.0
        cx = x0 + u * 6 + 2 * math.sin(u * 5 + i)
        cy = y0 - u * 24
        r = 1.2 + u * 3
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                q = 1 - math.hypot(xx - cx, (yy - cy) * 1.2) / r
                if q > 0 and q * (1 - u * 0.8) > bay[yy, xx] * 0.7:
                    d.point((xx, yy), fill=(246, 246, 242, int(110 + 90 * (1 - u))))
    return im


BANGLE_BOX = (BANGLE[0] + 2, 98, BANGLE[1] - 2, 128)


def bangles_frame(t):
    """手镯反光：每根竖杆上一道亮点从上往下扫，台面上几只手镯轮流闪一下（玻璃 + 金粉）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    a, b = BANGLE
    for k, xx in enumerate(range(a + 6, b - 4, 8)):
        j = (f + k * 3) % N_ANIM
        yy = 100 + j * 3
        px(d, xx - 1, yy, (255, 255, 250))
        px(d, xx, yy, (255, 250, 220))
        px(d, xx - 2, yy + 1, (255, 240, 200))
        if (f + k) % 2 == 0:
            px(d, xx + 2, 100 + ((j + 4) % N_ANIM) * 3, (255, 255, 240))
    for k, xx in enumerate(range(a + 2, b - 6, 8)):
        if (f + k) % 3 == 0:
            px(d, xx + 3, 125, (255, 255, 240))
    return im


CLOTH_BOX = (B6[0] + 4, 103, B6[1] - 4, 132)


def cloth_frame(t):
    """布店门口挂着的几条布帘（上端钉在布檐下，越往下摆得越多）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    for k, (x, L, c) in enumerate(((346, 22, (220, 70, 120)), (354, 26, (240, 196, 56)), (378, 20, (64, 150, 200)),
                                   (387, 24, (150, 80, 170)))):
        ph = math.tau * f / N_ANIM + k * 1.4
        for r in range(L):
            u = r / (L - 1)
            dx = round(1.8 * u * math.sin(ph) + 0.6 * u)
            for cc in range(4):
                col = c if cc < 3 else dk(c, 0.75)
                if r % 6 == 5 and cc < 3:
                    col = lt(c, 0.25)                                  # 布上的花边
                px(d, x + cc + dx, 104 + r, col)
    return im


DRAIN_BOX = (DRAIN[0], DRAIN_OPEN[0], DRAIN[1], DRAIN_OPEN[1] + 1)


def drain_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    a, b = DRAIN
    for i in range(6):                                                 # 脏水上一道道往前流的反光
        y = DRAIN_OPEN[0] + 1 + (i * 2 + f) % (DRAIN_OPEN[1] - DRAIN_OPEN[0] - 1)
        x = a + 2 + int(hrange(0, b - a - 8, i, 361))
        L = 2 + i % 3
        hl(d, x, x + L, y, (120, 124, 116) if (i + f) % 2 else (100, 104, 98))
    return im


def chains_frame(t):
    """巴士保险杠下面一排链子流苏（末端一个小铃铛）：一根根轻轻前后荡。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    for k, x in enumerate(range(BUS[0] + 1, BUS[1], 3)):
        sw = round(1.0 * math.sin(math.tau * f / N_ANIM + k * 0.7))
        for r in range(4):
            px(d, x + (sw if r >= 2 else 0), 143 + r, (200, 200, 206) if r % 2 else (150, 150, 156))
        px(d, x + sw, 147, (230, 190, 60))
    return im


# ============================================================ 组装
@lru_cache(maxsize=1)
def build():
    cim, cy = BJ_crop(clouds_img())
    fg = fg_img()
    bb = fg.getbbox()
    layers = [
        P.L_static('sky', sky_img()),
        P.L_wrap('clouds', cim, 640, CLOUD_K, cy, CLOUD_VX),
        P.L_pano('far', far_img(), FAR_K),
        P.L_strip('kites', KITE_BOX, N_ANIM, FPS_ANIM, kites_frame, k=FAR_K),
        P.L_pano('mid', mid_img(), MID_K),
        P.L_strip('pigeons', PIGEON_BOX, N_ANIM, FPS_ANIM, pigeons_frame, k=MID_K),
        P.L_pano('near', near_img(), 1.0),
        P.L_strip('tarp', TARP_BOX, N_ANIM, FPS_ANIM, tarp_frame),
        P.L_strip('steam', STEAM_BOX, N_ANIM, FPS_ANIM, steam_frame),
        P.L_strip('bangles', BANGLE_BOX, N_ANIM, FPS_ANIM, bangles_frame),
        P.L_strip('cloth', CLOTH_BOX, N_ANIM, FPS_ANIM, cloth_frame),
        P.L_strip('drain', DRAIN_BOX, N_ANIM, FPS_ANIM, drain_frame),
        P.L_strip('chains', CHAIN_BOX, N_ANIM, FPS_ANIM, chains_frame),
    ]
    fgl = [P.L_pano('wires', fg.crop(bb), FG_K, x=bb[0], y=bb[1], crop=False)]
    return dict(layers=layers, fg=fgl, near=near_img())


def BJ_crop(im):
    bb = im.getchannel('A').getbbox()
    return (im.crop((0, bb[1], im.width, bb[3])), bb[1]) if bb else (im, 0)


def compose(camX, t=0.5, state=None, fg=True):
    R = build()
    return P.compose(R['layers'], R['fg'], camX, t, state, with_fg=fg)


def extra_anchors():
    return dict(
        lane_back=KERB, fruit_box=[FRUIT[0], 90, FRUIT[1] + 1, KERB], tea_box=[TEA[0], 104, TEA[1], KERB],
        bangle_box=[BANGLE[0], 90, BANGLE[1] + 9, KERB], poster_box=[OPEN[0] + 2, 62, OPEN[0] + 28, 119],
        awning_box=[B6[0], 97, B6[1], 104], drain_box=[DRAIN[0], ROAD, DRAIN[1], H], bus_box=[BUS[0], 82, BUS[1] + 2, 148],
        parking_box=[PARK[0], ROAD + 1, PARK[1], 173],
    )


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    anchors = dict(ANCHORS)
    anchors.update(extra_anchors())
    st = P.export_stage(ex, PW, GROUND, WALK, R['layers'], R['fg'], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    P.check_no_black(ex, BJ, st, PW, '卡拉奇集市', [{}])
    P.check_alpha01(ex, R['near'], '近景')
    P.check_opaque(ex, R['near'], (0, 100, PW, H), '近景 一楼往下 + 人行道 + 马路')
    P.check_opaque(ex, sky_img(), (0, 0, W, H), '天空底图')
    fa = np.array(R['fg'][0]['img'])
    ex.checked('前景电线只有 0 / 255 透明度、只在画面上沿（y < 34）',
               int(((fa[..., 3] > 0) & (fa[..., 3] < 255)).sum()) + int(R['fg'][0]['y'] + fa.shape[0] > 34))
    P.check_strips(ex, BJ, P.strips_of(R['layers'], R['fg']))
    P.check_wraps(ex, BJ, st)
    out = P.check_anchors(ex, st['anchors'], PW, WALK, STAND, ANCHORS['walk_x'])
    ex.checked('锚点都在地图里、站人的锚点在可走带 / walk_x 里（不满足的条数）', out)
    need = ('arrive', 'fruit', 'fruit_vendor', 'tea', 'dan', 'command', 'bracelet', 'vendor', 'girl', 'bridge', 'bridge_box',
            'bus', 'jeep')
    ex.checked('规格要求的 13 个锚点名都在', sum(k not in st['anchors'] for k in need))
    a = np.array(R['near']).astype(int)
    # 排水沟：bridge_box 那一截是暗缝（平的、比路面暗得多），沟宽 26
    bb = ANCHORS['bridge_box']
    slot = P.lum(a[DRAIN_OPEN[0]:DRAIN_OPEN[1] + 1, DRAIN[0]:DRAIN[1], :3].astype(np.float32))
    ex.checked('排水沟缺口（y 164–175）是一条暗缝（平均亮度 %.0f ≤ 90）' % slot.mean(), 0 if slot.mean() <= 90 else 1)
    ex.checked('bridge_box 落在排水沟缺口里（x 407–433，y 166–174）',
               0 if (DRAIN[0] <= bb[0] and bb[2] <= DRAIN[1] and DRAIN_OPEN[0] <= bb[1] and bb[3] <= DRAIN_OPEN[1] + 1) else 1)
    ex.checked('排水沟宽 26 px', abs((DRAIN[1] - DRAIN[0]) - 26))
    # 巴士在可走带后面（y ≤ 147），停车位的白线画在路上、车不画
    na = np.array(R['near'])
    bus_cols = na[ROAD:, BUS[0]:BUS[1] + 2, :3].astype(int)
    ex.checked('巴士没有压进可走带（y ≥ 148 那几行没有车身的颜色：红 / 绿 / 镀铬）',
               int(((bus_cols[..., 0] > 190) & (bus_cols[..., 1] < 80)).sum() + ((bus_cols[..., 1] > 120) & (bus_cols[..., 0] < 80)).sum()))
    pk = a[ROAD + 1, PARK[0]:PARK[1], :3]
    ex.checked('停车位靠路缘那道白线在（y 149 白像素 ≥ 50）', 0 if int((pk.min(-1) > 190).sum()) >= 50 else 1)
    bg = a[100:127, BANGLE[0] + 3:BANGLE[1] - 3, :3]
    sat = (bg.max(-1) - bg.min(-1))
    ex.checked('手镯摊上五颜六色（饱和的像素 ≥ 200，= %d）' % int((sat > 90).sum()), 0 if int((sat > 90).sum()) >= 200 else 1)
    mean, std = P.check_walk_flat(ex, R['near'], WALK, '卡拉奇集市',
                                  skip=((DRAIN[0], ROAD, DRAIN[1], H), (PARK[0] - 5, ROAD, PARK[1] + 6, 174)))
    ex.note('可走带 y148–176 亮度均值 %.0f 标准差 %.1f' % (mean, std))
    nm = P.lum(a[..., :3].astype(np.float32))
    ex.note('可走带后面 y108–147 亮度均值 %.0f 标准差 %.1f' % (nm[108:148].mean(), nm[108:148].std()))
    P.check_export_vs_compose(ex, BJ, st, R['layers'], R['fg'], '卡拉奇集市', (0, 160, 320), (0.0, 1.25, 9.0), [{}])


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch5', 'karachi_dev')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        compose(camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'solo_%d.png' % camX))
    world = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    world.alpha_composite(near_img())
    world.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'near.png'))
    print('ok')
