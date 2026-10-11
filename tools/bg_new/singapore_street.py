# -*- coding: utf-8 -*-
r"""singapore_street —— 第3章「新加坡」：1980 年代末殖民时期的骑楼街（shophouse + 五脚基），晴天下午。
2026-10-11 ch3 按体验版精度重画（改前是 later_stages.city_street()：一排一模一样的彩色楼、平涂、没有纵深）。

地图 960 宽、ground 154、可走带 y 150–176（人走在五脚基外面的人行道上）；侧视平视，下午的太阳在左上。
从左到右（世界坐标）：
  x 0–48      港口：海（y 118–146）、驳船（tongkang，船头画眼睛）、铁柱 + 铁链的码头栏杆、系缆桩、一棵椰子树
  x 48–118    码头 / 海关楼：奶油色殖民式两层楼，正中一个大拱门（看得见里面的栈桥、拱形桁架、尽头的海），
              拱上一条名牌（色块）、山花里一个钟；一行人从拱门里走出来（anchors.arrive）
  x 118–176   横街路口：往里退的小街（斑马线、两边的侧墙，尽头是中景层的楼），一棵雨树的大树冠，
              交警岗亭（蓝白小亭子 + 顶灯）、红绿灯 + 行人灯（anchors.police）
  x 176–232   S1 黄色早期骑楼：绿百叶窗、晾衣竿（strip）；一层杂货铺（米袋、罐头、竹篮）
  x 232–302   装饰艺术风（Art Deco）旅行社：竖鳍、遮阳檐、钢窗；一层平墙上贴着鱼尾狮旅游海报（anchors.merlion_*）
  x 302–358   S2 粉色「海峡折中风」：拱窗、娘惹瓷砖、灰塑花饰、圆拱五脚基；一层药材行（百子柜、红灯笼、吊扇）
  x 358–414   S3 薄荷绿过渡式：三扇扇形气窗的长窗、浮雕牌匾；一层布庄（布匹）、晾衣竿
  x 414–468   S4 天蓝色：铸铁小阳台；一层咖啡店（kopitiam：大理石圆桌、鸟笼、吊扇）
  x 468–516   S5 蜜桃色三层：女儿墙 + 花砖通风墙；一层五金店；晾衣竿
  x 372–446   水果推车（绿白遮阳伞），推车左前方一筐醒目的红樱桃（anchors.cherry_stall / vendor）
  x 470–506   停在路边的三轮车（trishaw，侧边车 + 折叠篷）
  x 516–708   酒店：白色殖民式三层（红瓦四坡顶、绿百叶窗、拱形外廊），正中门廊（双柱、雨篷、阳台栏杆、
              名牌色块）、玻璃门、门口三级台阶、两盆棕榈（strip）、外廊里的藤椅 / 吊扇（anchors.hotel_door / doorman）
  x 708–770   S6 淡紫：拱窗 + 拱心石、圆形通风孔；一层理发店（转灯柱、理发椅、镜子）、吊扇
  x 770–836   S7 青绿：三扇长窗 + 橙色百叶、横楣花格；一层书店；门前公车站（雨棚、长椅、线路牌、站牌，anchors.tourist）
  x 836–960   缆车站入口：小站房（售票窗、青绿色檐带）+ 缆索机房（缆绳从这里出来），门口一块画缆车车厢图标的指示牌，
              一道往右上爬的石阶（扶手、毛石挡土墙）、山坡（九重葛、灌木、棕榈）、钢架塔；
              缆绳从机房斜着拉过塔顶、拉出画面右上，挂着一个小缆车车厢（strip 轻轻晃）（anchors.cable_station）
街上：三盏铸铁路灯（x 176 / 358 / 712）、几家五脚基口卷起来的竹帘、台阶上几盆花草；人行道是一块块水泥板
    （每块明暗差 ±3 %、细裂缝、树下落叶、沙井盖），路缘石 y 176–177，最下面两行是马路。
光：下午的太阳在左上（天上画着）；立面朝我们的一面亮，凸出来的东西影子落在右下，凹进去的窗洞上沿 / 左沿暗；
    五脚基里面暗（偏冷的阴影 + 下半截一点地面反光），外面亮。可走带后面（y 110–176）压了对比，人物站上去是清楚的。

图层（从后往前）：
  sky       pick    key 'morning'  values [0, 1]：0 = 下午的天（深一点的热带蓝 + 左上的太阳）；
                                   1 = 清晨的天（淡蓝、地平线发白微暖、不画太阳）；320×180，固定在屏幕（k 0）
  clouds    wrap    k 0.1 vx 1.2   积云（640 循环）
  far       pano    k 0.25         远景 480 宽：港口的海平线 + 小岛 + 货船、80 年代的高楼（CBD）、
                                   右边一座绿色的山（山顶缆车塔 + 细缆绳 + 小车厢 + 白房子）
  mid       pano    k 0.55         中景 672 宽：横街尽头的骑楼、组屋（HDB）板楼、教堂尖塔、钟楼、雨树、山脚的黑白洋房
  birds     clouds                 两只远处的鸟
  near      pano    k 1            整条街（960 宽）
  sea       strip   k 1            港口海面的波光（8 帧 @4 fps，只画在露出来的水面上）
  palms     strip   k 1 ×3         椰子树 / 酒店门口两盆棕榈 / 山坡上的棕榈：叶子摇（8 帧 @4 fps）
  laundry   strip   k 1            三处晾衣竿上的衣服飘（8 帧 @4 fps）
  fans      strip   k 1            五脚基 / 外廊里的吊扇转（4 帧 @8 fps）
  cabin     strip   k 1            缆车车厢轻轻晃（4 帧 @2 fps）
  morning   tint    key 'morning'  第二天清晨：偏冷偏淡的晨光（#9db4d8，alpha 0.30 × morning；0 / 不设 = 下午原样）
  fg: fg    pick    k 1.3          近处的东西（偶尔遮一点画面边缘）：地图左头码头那棵雨树（树干 + 只占画面上沿的树冠，
                                   镜头 0–40 才看得见）、一根细路灯柱（3 px，镜头约 150–400 时从画面里扫过去）；
                                   key 'morning' values [0, 1]：1 = 同一张图预先罩了晨光色（和 tint 同色同 alpha），
                                   人物夹在背景和前景中间，自己不被罩
单独运行：python -B tools\bg_new\singapore_street.py → tools\bg_new\_preview\ch3\after\singapore_street_solo_*.png
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

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 960                      # 地图宽
GROUND = 154
WALK = (150, 176)             # 可走纵深带（脚底 y）
CLOUD_K, CLOUD_VX = 0.1, 1.2
FAR_K, MID_K, FG_K = 0.25, 0.55, 1.3
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 480
MIDW = W + int(math.ceil((PW - W) * MID_K))      # 672
FG_X0 = -48                                      # 前景图的世界 x 起点（左边那棵树的树冠伸出地图左沿）
FGW = W + int(math.ceil((PW - W) * FG_K)) - FG_X0 + 48
HZ = 116                      # 海平线（港口那头，近景 / 远景同一行；也是横街 / 栈桥的消失点高度）
# 竖向（近景）
ROAD_Y = 178                  # 马路（最下面两行）
KERB_Y = 176                  # 路缘石顶（亮）/ 177 侧面
WALK_TOP = 148                # 人行道从这一行开始
STEP_Y = 146                  # 五脚基前沿的台阶：146 顶面、147 侧面
FLOOR_Y = 140                 # 五脚基地砖（140–145）
ARC_Y = 94                    # 五脚基开口顶
ARC_H = STEP_Y - ARC_Y        # 52 行（94–145）
BEAM_Y = 86                   # 一层檐口 / 招牌带（86–93）
UP_Y = 44                     # 二层墙面（44–85）
EAVE_Y = 40                   # 屋檐封檐板（40–43）
ROOF_Y = 30                   # 瓦（30–39）

# 各栋楼的 x 范围（右边不含）
PIER = (48, 118)
GAP = (118, 176)
S1 = (176, 232)
DECO = (232, 302)
S2 = (302, 358)
S3 = (358, 414)
S4 = (414, 468)
S5 = (468, 516)
HOTEL = (516, 708)
S6 = (708, 770)
S7 = (770, 836)
STATION = (836, 960)
HC = 612                      # 酒店中轴（门的中线）
POSTER = (268, 101, 294, 137)  # 鱼尾狮海报（含边框，右下不含）
CART = (378, 438)             # 水果推车车身 x
UMB = (408, 92)               # 遮阳伞顶（伞杆 x 408）
CHERRY = (380, 401)           # 樱桃筐 x
TRISHAW_X = 470
BUS = (744, 816)              # 公车站雨棚
STAIR0 = (900, 146)           # 石阶起点（第一级踏面左端）
STAIR_RUN, STAIR_RISE = 4, 3
PYLON_X = 928
CABLE = [(884, 66), (PYLON_X, 34), (968, 6)]     # 缆绳经过的点（机房出口 → 塔顶滑轮 → 画面外）
CAB_X = 948                   # 缆车车厢挂在这里

LAMPS = (176, 358, 712)       # 铸铁路灯（立在台阶边上）：横街转角、S2|S3 之间、酒店|S6 之间
N_ANIM, FPS_ANIM = 8, 4.0
N_FAN, FPS_FAN = 4, 8.0
N_CAB, FPS_CAB = 4, 2.0         # 缆车车厢：4 帧 @2 fps（0 / 右 / 0 / 左）
C = A._c4

ANCHORS = dict(
    arrive=[70, 164],          # 一行人从码头拱门出来的起点
    police=[150, 164],         # 交警岗亭前
    merlion_poster=[281, 150],  # 站这里看鱼尾狮海报
    cherry_stall=[414, 160],   # 水果推车前（樱桃筐在推车左前方 x 383–399，人站右边一点不挡住）
    vendor=[446, 152],         # 小贩站在推车右边
    hotel_door=[612, 152],     # 酒店门口（台阶下）
    doorman=[660, 156],        # 门童（门廊右边）
    tourist=[780, 164],        # 公车站前的游客
    cable_station=[890, 152],  # 缆车站入口（指示牌 / 石阶脚下）
    walk_x=[14, 946],
)

# ============================================================ 调色
INK = (40, 36, 48)
SKY_STOPS = [(54, 116, 204), (80, 146, 222), (120, 180, 236), (166, 208, 242), (198, 226, 244)]
HAZE = (196, 218, 236)
PAVE = (204, 197, 184)
PAVE_S = (193, 186, 173)
PAVE_HI = (212, 206, 194)
KERB_HI = (224, 220, 212)
KERB_F = (150, 146, 142)
ROAD = (98, 100, 108)
ROAD_D = (86, 88, 96)
GRANITE = (214, 210, 202)
GRANITE_F = (150, 146, 140)
TILE_A = (170, 104, 80)
TILE_B = (204, 186, 156)
TILE_C = (74, 120, 128)
ROOF = (186, 96, 64)
ROOF_HI = (212, 126, 86)
ROOF_D = (146, 70, 48)
ROOF_K = (104, 50, 38)
GLASS = (54, 70, 92)
GLASS_HI = (150, 176, 198)
DARK_IN = (52, 46, 50)        # 窗洞里（屋里暗）
LEAF_D = (30, 84, 46)
LEAF = (50, 124, 58)
LEAF_M = (78, 152, 70)
LEAF_HI = (132, 190, 90)
BARK = (110, 92, 74)
BARK_D = (76, 62, 52)
BARK_HI = (150, 132, 108)
IRON = (44, 74, 60)           # 铸铁（墨绿）
IRON_HI = (84, 124, 100)
SHADOW_MUL = np.array((0.74, 0.76, 0.86), np.float32)
SOFT_MUL = np.array((0.86, 0.87, 0.93), np.float32)     # 人行道上小东西的淡影（实色，不抖动）
MORNING = ('#9db4d8', 0.30)   # 晨光：偏冷偏淡（颜色、alpha；JS 里 alpha × morning）
SKY_MORNING = [(118, 158, 212), (150, 186, 226), (186, 210, 234), (214, 226, 236), (234, 228, 224)]


# ============================================================ 小工具
def dk(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


def lt(c, k):
    return mix(c, (255, 255, 255), k)


def hl(d, x0, x1, y, c):
    if x1 >= x0:
        d.line((x0, y, x1, y), fill=C(c))


def vl(d, x, y0, y1, c):
    if y1 >= y0:
        d.line((x, y0, x, y1), fill=C(c))


def px(d, x, y, c):
    d.point((x, y), fill=C(c))


def rect(d, x0, y0, x1, y1, c, outline=None):
    if x1 >= x0 and y1 >= y0:
        d.rectangle((x0, y0, x1, y1), fill=C(c) if c is not None else None, outline=C(outline) if outline else None)


def mul_box(im, box, mul, level=1.0):
    """box（右下含）里不透明的像素乘 mul；level < 1 时按 Bayer 只压一部分。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(im.width - 1, x1), min(im.height - 1, y1)
    if x1 < x0 or y1 < y0:
        return
    a = np.array(im.crop((x0, y0, x1 + 1, y1 + 1))).astype(np.float32)
    m = a[..., 3] > 0
    if level < 1.0:
        m &= A._bayer(im.width, im.height)[y0:y1 + 1, x0:x1 + 1] < level
    a[m, :3] *= np.asarray(mul, np.float32)
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'), (x0, y0))


def mul_mask(im, mask, mul, level=1.0):
    a = np.array(im).astype(np.float32)
    m = mask & (a[..., 3] > 0)
    if level < 1.0:
        m &= A._bayer(im.width, im.height) < level
    a[m, :3] *= np.asarray(mul, np.float32)
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def poly_mask(size, pts):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m) > 0


def cast_shadow(im, pts, level=1.0, mul=SHADOW_MUL):
    mul_mask(im, poly_mask(im.size, pts), mul, level)


def mottle(im, box, base, dark, light, seed, cell=4, lo=0.3, hi=0.7, streaks=0):
    """灰泥墙的斑驳：box 里颜色正好是 base 的像素，按 fbm 噪声换成 dark / light（边缘 Bayer 抖动）；
    streaks > 0 时再加几道往下淌的水渍（从上沿往下，越往下越稀）。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if w <= 0 or h <= 0:
        return
    a = np.array(im)
    sub = a[y0:y1 + 1, x0:x1 + 1]
    is_base = (sub[..., 0] == base[0]) & (sub[..., 1] == base[1]) & (sub[..., 2] == base[2]) & (sub[..., 3] > 0)
    n = A._fbm(w + 8, h + 8, cell, seed=seed % 997)[4:4 + h, 4:4 + w]
    bay = A._bayer(x1 + 1, y1 + 1)[y0:y1 + 1, x0:x1 + 1]
    dm = is_base & ((n > hi + 0.05) | ((n > hi) & (bay < 0.5)))
    lm = is_base & ((n < lo - 0.05) | ((n < lo) & (bay < 0.5)))
    sub[dm, :3] = dark
    sub[lm, :3] = light
    for i in range(streaks):
        sx = int(hrange(0, w - 1, seed, i, 7))
        L = int(hrange(h * 0.2, h * 0.7, seed, i, 8))
        for yy in range(L):
            if hash01(seed, i, yy, 9) < 1.0 - yy / max(1, L) * 0.8 and is_base[yy, sx] | ((sub[yy, sx, :3] == light).all()):
                sub[yy, sx, :3] = dark
    a[y0:y1 + 1, x0:x1 + 1] = sub
    im.paste(Image.fromarray(a, 'RGBA'))


def _tile(im, w):
    out = A._new(w, im.height)
    for x in range(0, w, im.width):
        out.paste(im, (x, 0))
    return out


# ============================================================ 天空 / 云
@lru_cache(maxsize=2)
def sky_img(morning=False):
    """下午：深一点的热带蓝 + 左上的太阳；清晨（morning）：淡蓝、地平线一带发白微暖，太阳还在楼后面（不画）。"""
    im = A._new(W, H)
    if morning:
        gradient(im, (0, 0, W, H), SKY_MORNING, bands=12)
        A._glow(im, 40, 120, 120, 50, (250, 236, 220), 40, rings=4)
        return im
    gradient(im, (0, 0, W, H), SKY_STOPS, bands=12)
    A._glow(im, 38, 18, 40, 34, (255, 246, 214), 70, rings=5)
    d = ImageDraw.Draw(im)
    d.ellipse((32, 12, 44, 24), fill=C((255, 248, 222)))
    d.ellipse((34, 14, 42, 22), fill=C((255, 254, 244)))
    return im


@lru_cache(maxsize=1)
def clouds_img():
    """640 循环：海平线一带的热带积云（高、底平，下午的光从左上照，右下暗）+ 上面几朵小云。"""
    im = A._new(640, 112)
    pal = ((255, 255, 255), (240, 244, 250), (212, 224, 240), (184, 200, 226))
    for i in range(6):
        w = hrange(60, 110, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.42, 0.6, i, 2), 600 + i, pal)
        cx = (i + hrange(0.1, 0.9, i, 3)) * 640 / 6
        y = 112 - cl.height - int(hrange(0, 14, i, 4))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    pal2 = ((255, 255, 255), (236, 242, 250), (210, 224, 242), (188, 206, 232))
    for i in range(7):
        w = hrange(16, 40, i, 11)
        cl = A._cloud_sprite(w, w * 0.34, 700 + i, pal2)
        cx = (i + hrange(0.1, 0.9, i, 12)) * 640 / 7
        y = int(hrange(4, 40, i, 13))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    return im


def bird_img():
    g = A._new(5, 3)
    d = ImageDraw.Draw(g)
    for (x, y) in ((0, 0), (1, 1), (3, 1), (4, 0)):
        px(d, x, y, (60, 64, 80))
    px(d, 2, 2, (60, 64, 80))
    return g


BIRDS = [(22, -5.0, 0.35, 120), (30, -3.6, 0.3, 300)]


# ============================================================ 远景：海平线 / 高楼 / 山
def hill_top(x):
    """远山（Mount Faber 那种）的山脊 y：主峰在 x 412，左边缓坡、右边一个山肩。"""
    h = 64 * math.exp(-((x - 412) / 52.0) ** 2) + 30 * math.exp(-((x - 470) / 40.0) ** 2) \
        + 14 * math.exp(-((x - 340) / 30.0) ** 2)
    return 104 - h


TOWERS = [  # (x, w, top, 立面色, 样式)
    (108, 16, 52, (214, 208, 196), 'band'),
    (126, 12, 34, (176, 190, 204), 'grid'),
    (140, 20, 20, (226, 222, 212), 'step'),
    (162, 14, 40, (150, 168, 186), 'glass'),
    (178, 18, 28, (204, 196, 182), 'band'),
    (198, 12, 46, (232, 228, 218), 'grid'),
    (212, 22, 12, (184, 196, 208), 'round'),
    (236, 14, 36, (220, 214, 200), 'step'),
    (252, 18, 24, (160, 176, 194), 'glass'),
    (272, 12, 50, (226, 220, 206), 'band'),
    (286, 16, 42, (196, 202, 210), 'grid'),
    (304, 12, 58, (214, 206, 190), 'band'),
]


def _tower(d, x, w, top, face, style, seed):
    base = 120
    side = max(2, w // 5)
    fd = dk(face, 0.82)
    sd = dk(face, 0.68)
    rect(d, x, top, x + w - 1, base, face)
    rect(d, x + w, top + 2, x + w + side - 1, base, sd)           # 右侧面（背光）
    vl(d, x, top, base, lt(face, 0.25))
    if style == 'band':
        for y in range(top + 3, base, 3):
            hl(d, x + 1, x + w - 1, y, fd)
            hl(d, x + w, x + w + side - 1, y, dk(sd, 0.85))
    elif style == 'grid':
        for y in range(top + 2, base, 3):
            for xx in range(x + 2, x + w - 1, 3):
                px(d, xx, y, fd)
                px(d, xx, y + 1, fd)
    elif style == 'glass':
        for xx in range(x + 2, x + w - 1, 3):
            vl(d, xx, top + 2, base, fd)
        for y in range(top + 1, base, 6):
            hl(d, x, x + w - 1, y, lt(face, 0.2))
    elif style == 'step':
        rect(d, x + 3, top - 6, x + w - 4, top - 1, face)
        rect(d, x + w - 3, top - 4, x + w - 2, top - 1, sd)
        rect(d, x + 6, top - 10, x + w - 7, top - 7, face)
        vl(d, x + w // 2, top - 16, top - 11, dk(face, 0.6))       # 天线
        for y in range(top + 2, base, 4):
            hl(d, x + 1, x + w - 1, y, fd)
    elif style == 'round':
        # 圆柱楼：横向明暗（左亮右暗），一圈圈窗带
        for xx in range(x, x + w + side):
            u = (xx - x) / (w + side - 1)
            c = mix(lt(face, 0.2), dk(face, 0.62), u ** 1.2)
            vl(d, xx, top + int(2 * (1 - math.sin(math.pi * u))), base, c)
        for y in range(top + 4, base, 3):
            for xx in range(x, x + w + side):
                u = (xx - x) / (w + side - 1)
                px(d, xx, y, mix(dk(face, 0.8), dk(face, 0.5), u))
        hl(d, x + 2, x + w + side - 3, top, lt(face, 0.4))
    # 屋顶的机房 / 水箱
    if style in ('band', 'grid', 'glass'):
        rect(d, x + 2 + int(hrange(0, w / 3, seed, 1)), top - 3, x + 6 + int(hrange(0, w / 3, seed, 1)), top - 1, fd)


@lru_cache(maxsize=1)
def far_img():
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    # 港口那头：海（海平线以下）+ 小岛 + 船
    gradient(im, (0, HZ, 140, H), [(150, 196, 222), (104, 164, 206), (76, 138, 192)], bands=6)
    for (x0, x1, ht) in ((0, 34, 7), (40, 70, 4), (84, 120, 9)):
        pts = [(x0, HZ)]
        for x in range(x0, x1 + 1):
            u = (x - x0) / max(1, x1 - x0)
            pts.append((x, HZ - ht * math.sin(math.pi * u) ** 0.7 - 1.5 * math.sin(x * 0.7)))
        pts.append((x1, HZ))
        d.polygon(pts, fill=C((132, 168, 170)))
        for x in range(x0, x1):
            u = (x - x0) / max(1, x1 - x0)
            y = int(HZ - ht * math.sin(math.pi * u) ** 0.7 - 1.5 * math.sin(x * 0.7))
            px(d, x, y, (150, 184, 182) if u < 0.5 else (122, 156, 160))
    # 远处的货船（集装箱船 + 油轮）
    for (sx, L, col) in ((18, 22, (120, 132, 150)), (60, 14, (140, 150, 164))):
        hl(d, sx, sx + L, HZ - 1, dk(col, 0.8))
        hl(d, sx + 1, sx + L - 1, HZ - 2, col)
        rect(d, sx + L - 5, HZ - 6, sx + L - 2, HZ - 3, lt(col, 0.3))
        for i in range(0, L - 7, 3):
            rect(d, sx + 2 + i, HZ - 4, sx + 3 + i, HZ - 3, ((176, 110, 96), (96, 130, 160), (190, 176, 120))[(i // 3) % 3])
    hl(d, 0, 139, HZ, (214, 232, 242))
    # 山（主峰 x 412）：先填山体，再按坡向上色、树冠疙瘩的山脊线
    a = np.array(im)
    bay = A._bayer(FARW, H)
    for x in range(300, FARW):
        top = int(round(hill_top(x)))
        sl = hill_top(x + 2) - hill_top(x - 2)                     # > 0：往右下（朝左上的坡，亮）
        for y in range(max(0, top), 140):
            v = sl + hrange(-0.4, 0.4, x // 2, y // 2, 5)
            if v > 0.9 or (v > 0.3 and bay[y, x] < 0.5):
                c = (110, 160, 104)
            elif v < -0.9 or (v < -0.3 and bay[y, x] < 0.5):
                c = (66, 112, 82)
            else:
                c = (86, 136, 92)
            nn = hash01(x // 3, y // 3, 6)
            if nn < 0.12:
                c = dk(c, 0.88)
            elif nn > 0.92:
                c = lt(c, 0.12)
            a[y, x, :3] = c
            a[y, x, 3] = 255
        # 山脊：一圈树冠的疙瘩
        if 0 <= top - 1 and hash01(x, 7) < 0.55:
            a[top - 1, x, :3] = (96, 146, 96)
            a[top - 1, x, 3] = 255
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 山顶：白房子 + 缆车塔（细钢架）+ 往左下拉的缆绳 + 一个小车厢
    tx = 404
    ty = int(hill_top(tx))
    rect(d, 416, int(hill_top(416)) - 4, 424, int(hill_top(416)) + 1, (236, 236, 228))
    hl(d, 415, 425, int(hill_top(416)) - 5, (176, 92, 70))
    for yy in range(ty - 14, ty + 1):
        u = (yy - (ty - 14)) / 14
        half = int(round(1 + 2 * u))
        px(d, tx - half, yy, (84, 92, 104))
        px(d, tx + half, yy, (84, 92, 104))
        if yy % 3 == 0:
            hl(d, tx - half, tx + half, yy, (110, 118, 128))
    hl(d, tx - 4, tx + 4, ty - 15, (70, 78, 90))
    for k, off in enumerate((0, 2)):
        x0, y0, x1, y1 = tx - 3, ty - 14 + off, 236, 86 + off
        for x in range(x1, x0 + 1):
            u = (x0 - x) / (x0 - x1)
            y = y0 + (y1 - y0) * u + 6 * math.sin(math.pi * u)
            if x % 2 == 0 or k == 0:
                px(d, x, round(y), (92, 102, 116))
    # 小车厢
    cx = 330
    u = (tx - 3 - cx) / (tx - 3 - 236)
    cy = round(ty - 14 + (86 - ty + 14) * u + 6 * math.sin(math.pi * u))
    vl(d, cx, cy + 1, cy + 3, (80, 88, 100))
    rect(d, cx - 2, cy + 4, cx + 2, cy + 7, (232, 186, 70))
    hl(d, cx - 2, cx + 2, cy + 5, (90, 110, 140))
    # 高楼（CBD）
    for i, (x, w, top, face, style) in enumerate(TOWERS):
        _tower(d, x, w, top, face, style, i)
    # 空气透视：越往下越发灰（远处的楼底被热气蒸得白白的）
    a = np.array(im).astype(np.float32)
    ys = np.arange(H, dtype=np.float32)[:, None]
    amt = np.clip(0.30 + (ys - 20) / 100 * 0.35, 0.3, 0.7)
    m = a[..., 3] > 0
    hz = np.array(HAZE, np.float32)
    a[..., :3] = np.where(m[..., None], a[..., :3] * (1 - amt[..., None]) + hz * amt[..., None], a[..., :3])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


# ============================================================ 中景：横街尽头的楼 / 组屋 / 尖塔 / 山脚
def _mid_shophouse(d, x, w, base, col, seed):
    """小一号的骑楼（中景，横街尽头）：两层，五脚基暗口、两扇窗、瓦檐。"""
    top = base - 50
    rect(d, x, top + 6, x + w - 1, base, col)
    rect(d, x - 1, top + 2, x + w, top + 5, ROOF)
    hl(d, x - 1, x + w, top + 2, ROOF_HI)
    hl(d, x, x + w - 1, top + 6, dk(col, 0.8))
    for i in range(2):
        wx = x + 3 + i * (w - 9) // 1 if w < 14 else x + 3 + i * ((w - 9) // 2 + 2)
        rect(d, wx, top + 12, wx + 3, top + 22, dk(col, 0.55))
        hl(d, wx, wx + 3, top + 12, dk(col, 0.7))
    hl(d, x, x + w - 1, top + 26, lt(col, 0.3))
    rect(d, x + 1, top + 29, x + w - 2, base - 1, mix(dk(col, 0.55), (70, 80, 110), 0.2))  # 五脚基（暗）
    vl(d, x, top + 26, base, lt(col, 0.15))
    rect(d, x + 3, top + 34, x + w - 4, base - 3, mix(dk(col, 0.4), (60, 50, 50), 0.3))
    hl(d, x, x + w - 1, base, (176, 170, 160))


def _hdb(d, x, w, top, base, col):
    """组屋板楼：长条走廊 + 一排排窗 + 屋顶水箱；走廊外伸出晾衣竿。"""
    rect(d, x, top, x + w - 1, base, col)
    rect(d, x + w, top + 2, x + w + 2, base, dk(col, 0.7))
    for y in range(top + 3, base, 5):
        hl(d, x, x + w - 1, y, dk(col, 0.72))                      # 走廊的影
        hl(d, x, x + w - 1, y + 1, lt(col, 0.2))                   # 走廊栏板
        for xx in range(x + 2, x + w - 2, 4):
            px(d, xx, y + 2, dk(col, 0.58))
        if hash01(x, y, 3) < 0.5:
            xx = x + int(hrange(2, w - 4, x, y, 4))
            hl(d, xx, xx + 2, y + 3, (230, 140, 120) if hash01(x, y, 5) < 0.5 else (120, 160, 210))
    rect(d, x + 3, top - 4, x + 9, top - 1, dk(col, 0.82))          # 屋顶水箱
    vl(d, x + w - 4, top - 7, top - 1, (90, 96, 106))              # 天线


def _canopy(d, cx, cy, rx, ry, seed, pal=(LEAF_D, LEAF, LEAF_M, LEAF_HI)):
    """雨树 / 大树的树冠：一堆椭圆疙瘩，左上亮、右下暗、底下一圈深色。"""
    blobs = []
    n = max(5, int(rx * ry / 40))
    for i in range(n):
        ang = hrange(0, math.tau, seed, i, 1)
        r = hrange(0.1, 0.85, seed, i, 2)
        bx = cx + math.cos(ang) * rx * r
        by = cy + math.sin(ang) * ry * r * 0.8
        br = hrange(0.28, 0.45, seed, i, 3) * min(rx, ry * 1.6)
        blobs.append((bx, by, br))
    for (bx, by, br) in blobs:
        d.ellipse((bx - br, by - br * 0.75 + 1, bx + br, by + br * 0.75 + 1), fill=C(pal[0]))
    for (bx, by, br) in blobs:
        d.ellipse((bx - br, by - br * 0.75, bx + br, by + br * 0.75), fill=C(pal[1]))
    for (bx, by, br) in blobs:
        rr = br * 0.62
        d.ellipse((bx - rr - br * 0.25, by - br * 0.7, bx + rr - br * 0.25, by - br * 0.7 + rr * 1.0), fill=C(pal[2]))
    for (bx, by, br) in blobs:
        if by < cy:
            rr = br * 0.3
            d.ellipse((bx - rr - br * 0.4, by - br * 0.62, bx + rr - br * 0.4, by - br * 0.62 + rr * 0.9), fill=C(pal[3]))


@lru_cache(maxsize=1)
def mid_img():
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    # 组屋板楼 / 办公楼（高的，露在骑楼屋顶上面）
    _hdb(d, 204, 46, 22, 132, (226, 218, 196))
    _hdb(d, 268, 30, 34, 132, (214, 222, 214))
    _hdb(d, 438, 40, 28, 132, (230, 214, 190))
    _hdb(d, 486, 26, 40, 132, (208, 216, 226))
    # 教堂尖塔（白）
    sx = 352
    rect(d, sx, 40, sx + 12, 132, (236, 234, 226))
    rect(d, sx + 13, 42, sx + 14, 132, (196, 196, 196))
    d.polygon([(sx - 1, 40), (sx + 6, 6), (sx + 13, 40)], fill=C((232, 230, 222)))
    d.polygon([(sx + 6, 6), (sx + 13, 40), (sx + 10, 40)], fill=C((196, 196, 196)))
    vl(d, sx + 6, 1, 5, (150, 150, 156))
    hl(d, sx + 5, sx + 7, 3, (150, 150, 156))
    for y in (50, 70):
        rect(d, sx + 4, y, sx + 8, y + 8, (90, 96, 112))
        d.ellipse((sx + 4, y - 2, sx + 8, y + 2), fill=C((90, 96, 112)))
    # 钟楼（米黄 + 绿顶）
    cx = 396
    rect(d, cx, 30, cx + 14, 132, (232, 214, 170))
    rect(d, cx + 15, 32, cx + 16, 132, (196, 176, 134))
    d.polygon([(cx - 1, 30), (cx + 7, 18), (cx + 15, 30)], fill=C((92, 150, 120)))
    d.ellipse((cx + 3, 36, cx + 11, 44), fill=C((246, 244, 236)))
    px(d, cx + 7, 38, INK)
    px(d, cx + 7, 39, INK)
    px(d, cx + 8, 40, INK)
    for y in range(50, 130, 10):
        rect(d, cx + 4, y, cx + 10, y + 5, (176, 150, 110))
    # 横街尽头：一排小骑楼（从近景的路口缝里看得见）+ 一棵树
    base = 128
    x = 52
    i = 0
    while x < 210:
        w = int(hrange(18, 26, i, 31))
        col = ((236, 204, 150), (214, 178, 186), (170, 206, 192), (196, 196, 222), (238, 186, 150))[i % 5]
        _mid_shophouse(d, x, w, base, col, i)
        x += w
        i += 1
    # 雨树（横街里）+ 中间几棵行道树
    for (tx, ty, rx, ry, sd) in ((84, 70, 26, 16, 41), (178, 66, 24, 16, 43), (322, 92, 20, 14, 45),
                                 (540, 78, 30, 18, 47)):
        vl(d, tx, ty + 6, base, BARK_D)
        vl(d, tx + 1, ty + 6, base, BARK)
        _canopy(d, tx, ty, rx, ry, sd)
    # 山脚（右边）：一片树林往右升，林子里一栋黑白洋房
    for x in range(520, MIDW):
        top = int(110 - 46 * (1 - math.exp(-((x - 520) / 70.0))) - 6 * math.sin(x * 0.11))
        vl(d, x, top, 140, (64, 116, 72))
    for i in range(22):
        tx = 520 + int(hrange(0, MIDW - 520, i, 51))
        top = int(110 - 46 * (1 - math.exp(-((tx - 520) / 70.0))))
        _canopy(d, tx, top + 2, hrange(10, 18, i, 52), hrange(7, 11, i, 53), 60 + i,
                pal=((40, 92, 56), (58, 118, 66), (82, 144, 78), (120, 176, 96)))
    bx, by = 596, 74
    rect(d, bx, by, bx + 24, by + 14, (244, 242, 234))                     # 黑白洋房：白墙 + 黑木构
    for xx in range(bx, bx + 25, 6):
        vl(d, xx, by, by + 14, (52, 48, 46))
    hl(d, bx, bx + 24, by + 6, (52, 48, 46))
    d.polygon([(bx - 3, by), (bx + 12, by - 8), (bx + 27, by)], fill=C((150, 76, 56)))
    hl(d, bx - 3, bx + 27, by, (110, 56, 44))
    # 地平（横街尽头的路面）
    rect(d, 0, base + 1, MIDW - 1, 140, (168, 162, 154))
    # 空气透视（比远景淡得多）
    a = np.array(im).astype(np.float32)
    m = a[..., 3] > 0
    hz = np.array(HAZE, np.float32)
    a[m, :3] = a[m, :3] * 0.8 + hz * 0.2
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


# ============================================================ 近景：地面
def draw_ground(im):
    """人行道（148–175）+ 路缘石（176 顶 / 177 侧）+ 马路（178–179）。人行道的接缝、污渍都压得很淡。"""
    d = ImageDraw.Draw(im)
    rect(d, 0, WALK_TOP, PW - 1, KERB_Y - 1, PAVE)
    mottle(im, (0, WALK_TOP, PW - 1, KERB_Y - 1), PAVE, PAVE_S, PAVE_HI, 31, cell=6, lo=0.22, hi=0.8)
    d = ImageDraw.Draw(im)
    bands = [(WALK_TOP, 154), (154, 161), (161, 169), (169, KERB_Y)]
    for bi, (ya, yb) in enumerate(bands):
        if bi:
            for x in range(0, PW, 2):
                px(d, x, ya, PAVE_S)
            for x in range(1, PW, 2):
                px(d, x, ya, mix(PAVE, PAVE_S, 0.5))
        step = 28 + bi * 4
        off = (bi * 17) % step
        for x in range(off, PW, step):
            vl(d, x, ya + 1, yb - 1, mix(PAVE, PAVE_S, 0.7))
    a = np.array(im).astype(np.float32)                          # 每块板子亮一点 / 暗一点（±3 %）
    for bi, (ya, yb) in enumerate(bands):
        step = 28 + bi * 4
        off = (bi * 17) % step
        xs = [0] + list(range(off, PW, step)) + [PW]
        for xa, xb in zip(xs, xs[1:]):
            f = hrange(0.97, 1.03, bi, xa, 33)
            a[ya + 1:yb, xa + 1:xb, :3] *= f
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))
    d = ImageDraw.Draw(im)
    for i in range(26):                                           # 细裂缝
        x, y = int(hrange(0, PW, i, 34)), int(hrange(150, 173, i, 35))
        for k in range(int(hrange(3, 8, i, 36))):
            px(d, x, y, mix(PAVE, PAVE_S, 0.9))
            x += 1
            y += (1 if hash01(i, k, 37) < 0.3 else (-1 if hash01(i, k, 37) > 0.8 else 0))
            y = max(149, min(174, y))
    for i in range(60):                                           # 口香糖印 / 小污点
        x, y = int(hrange(0, PW, i, 38)), int(hrange(150, 174, i, 39))
        px(d, x, y, mix(PAVE, (150, 146, 140), 0.35))
    for (xa, xb) in ((112, 190), (872, 960), (8, 60)):            # 树下的落叶
        for i in range(int((xb - xa) / 3)):
            x, y = int(hrange(xa, xb, i, xa, 40)), int(hrange(149, 174, i, xa, 41) ** 1.0)
            if hash01(i, xa, 42) < 0.5:
                px(d, x, y, ((150, 160, 80), (176, 140, 70), (120, 140, 70))[i % 3])
    hl(d, 0, PW - 1, WALK_TOP, dk(PAVE, 0.86))                  # 台阶脚下一道暗缝
    hl(d, 0, PW - 1, KERB_Y, KERB_HI)
    hl(d, 0, PW - 1, KERB_Y + 1, KERB_F)
    rect(d, 0, ROAD_Y, PW - 1, H - 1, ROAD)
    for x in range(0, PW, 3):
        if hash01(x, 81) < 0.4:
            px(d, x, ROAD_Y + (x // 3) % 2, ROAD_D)
    for x in range(0, PW, 37):                                    # 路缘石的接缝
        px(d, x, KERB_Y, KERB_F)
    for x in (206, 444, 690, 868):                                # 人行道上的沙井盖
        d.ellipse((x - 6, 163, x + 6, 167), fill=C(mix(PAVE, (120, 116, 110), 0.28)))
        hl(d, x - 4, x + 4, 165, mix(PAVE, (120, 116, 110), 0.4))


def draw_arcade_floor(im, x0, x1):
    """五脚基地砖（140–145，娘惹花砖：米色底 + 赭红菱形 + 青绿点）+ 前沿花岗岩台阶（146 顶 / 147 侧）。"""
    d = ImageDraw.Draw(im)
    for y in range(FLOOR_Y, STEP_Y):
        for x in range(x0, x1):
            u, v = x % 6, (y - FLOOR_Y) % 6
            c = TILE_B
            if abs(u - 2.5) + abs(v - 2.5) < 2.2:
                c = TILE_A
            if u == 0 or v == 0:
                c = mix(TILE_B, TILE_A, 0.3)
            if (u, v) in ((3, 3),):
                c = TILE_C
            px(d, x, y, c)
    hl(d, x0, x1 - 1, STEP_Y, GRANITE)
    hl(d, x0, x1 - 1, STEP_Y + 1, GRANITE_F)


# ============================================================ 近景：港口
def draw_harbour(im):
    """x 0–48：海（HZ–145）、驳船、码头栏杆（铁柱 + 铁链）、系缆桩。返回只有海的那一张（给波光 strip 找水面）。"""
    sea = A._new(PW, H)
    gradient(sea, (0, HZ, 49, STEP_Y), [(176, 210, 230), (112, 170, 208), (70, 132, 186), (54, 112, 168)], bands=7)
    sd = ImageDraw.Draw(sea)
    hl(sd, 0, 48, HZ, (214, 232, 242))
    for i in range(36):                                          # 静止的小浪（深一点的短横）
        y = HZ + 2 + int(hash01(i, 21) ** 1.2 * (STEP_Y - HZ - 3))
        x = int(hrange(-6, 48, i, 22))
        L = 2 + int((y - HZ) / 7)
        c = dk(sea.getpixel((max(0, min(48, x + 1)), y))[:3], 0.9)
        hl(sd, max(0, x), min(48, x + L), y, c)
    im.alpha_composite(sea)
    d = ImageDraw.Draw(im)
    # 驳船（tongkang）：木船身、船头画着眼睛、蓝色篷顶，系在码头上
    bx0, bx1, wl = 4, 44, 136
    hull = [(bx0, wl - 7), (bx1 - 6, wl - 7), (bx1, wl - 10), (bx1 - 2, wl - 4), (bx1 - 8, wl), (bx0 + 3, wl), (bx0, wl - 4)]
    d.polygon(hull, fill=C((136, 92, 60)))
    hl(d, bx0, bx1 - 6, wl - 7, (176, 128, 84))
    hl(d, bx0 + 1, bx1 - 4, wl - 6, (210, 74, 52))              # 船舷上的红漆条
    hl(d, bx0 + 2, bx1 - 5, wl - 3, (112, 74, 50))
    hl(d, bx0 + 3, bx1 - 8, wl - 1, (90, 60, 42))
    d.ellipse((bx1 - 9, wl - 7, bx1 - 5, wl - 4), fill=C((244, 240, 228)))  # 船眼
    px(d, bx1 - 7, wl - 6, INK)
    px(d, bx1 - 6, wl - 6, INK)
    rect(d, bx0 + 6, wl - 15, bx0 + 26, wl - 8, (64, 104, 150))  # 篷
    hl(d, bx0 + 5, bx0 + 27, wl - 16, (96, 138, 184))
    hl(d, bx0 + 6, bx0 + 26, wl - 9, (44, 74, 112))
    for xx in (bx0 + 7, bx0 + 25):
        vl(d, xx, wl - 14, wl - 8, (90, 66, 48))
    rect(d, bx0 + 10, wl - 13, bx0 + 22, wl - 9, (40, 40, 52))   # 篷底下暗
    hl(d, bx0, bx1 - 2, wl + 1, (60, 104, 150))                  # 水线的影
    # 码头边（花岗岩）+ 栏杆
    hl(d, 0, PIER[0] - 1, STEP_Y, GRANITE)
    hl(d, 0, PIER[0] - 1, STEP_Y + 1, GRANITE_F)
    posts = [3, 16, 29, 42]
    for i, x in enumerate(posts):
        rect(d, x, 128, x + 1, STEP_Y - 1, IRON)
        vl(d, x, 128, STEP_Y - 1, IRON_HI)
        rect(d, x - 1, 126, x + 2, 127, IRON)
        px(d, x, 126, IRON_HI)
        if i + 1 < len(posts):
            xb = posts[i + 1]
            for yy0 in (130, 138):
                for xx in range(x + 2, xb):
                    u = (xx - x - 2) / max(1, xb - x - 3)
                    y = round(yy0 + 3 * math.sin(math.pi * u))
                    px(d, xx, y, (70, 76, 84) if xx % 2 else (40, 44, 52))
    # 系缆桩 + 缆绳拉到船头
    rect(d, 34, 140, 38, STEP_Y - 1, (52, 52, 60))
    rect(d, 33, 139, 39, 140, (72, 72, 82))
    px(d, 34, 141, (110, 110, 122))
    for xx in range(39, 46):
        px(d, xx, 140 + (xx - 39) // 3, (196, 176, 130))
    return sea


# ============================================================ 近景：横街路口（交警岗亭）
VP = (147, 116)
GAP_U = 0.4                   # 横街尽头的深度（0 = 街口，1 = 消失点）


def _toward_vp(x, y, u=GAP_U):
    return x + (VP[0] - x) * u, y + (VP[1] - y) * u


def draw_side_street(im):
    """横街：往里退的路面 + 斑马线 + 两边的侧墙（左边码头楼的侧墙背光，右边 S1 的侧墙向阳）+ 雨树。"""
    d = ImageDraw.Draw(im)
    gx0, gx1 = GAP
    # 路面：前沿 y 147，尽头 y 131
    fl, fr = (gx0, STEP_Y + 1), (gx1, STEP_Y + 1)
    bl, br = _toward_vp(*fl), _toward_vp(*fr)
    d.polygon([fl, fr, br, bl], fill=C((120, 120, 126)))
    for y in range(int(bl[1]), STEP_Y + 2):
        u = (STEP_Y + 1 - y) / (STEP_Y + 1 - bl[1])
        xa = gx0 + (bl[0] - gx0) * u
        xb = gx1 + (br[0] - gx1) * u
        hl(d, round(xa), round(xa) + max(1, round(4 * (1 - u))), y, (178, 172, 160))     # 两边窄人行道
        hl(d, round(xb) - max(1, round(4 * (1 - u))), round(xb), y, (190, 184, 172))
        if y % 3 == 0:
            for xx in range(round(xa) + 5, round(xb) - 5, 5):
                if hash01(xx, y, 11) < 0.25:
                    px(d, xx, y, (110, 110, 118))
    for k in range(6):                                            # 斑马线（往消失点收）
        xa = gx0 + 9 + k * 8
        for y in range(139, STEP_Y + 1):
            u = (STEP_Y + 1 - y) / (STEP_Y + 1 - bl[1])
            xx = xa + (VP[0] - xa) * u * 0.95
            hl(d, round(xx), round(xx) + 3, y, (226, 224, 216))
    # 侧墙
    lt0, lb0 = (gx0, 36), (gx0, STEP_Y + 1)
    lt1, lb1 = _toward_vp(*lt0), _toward_vp(*lb0)
    d.polygon([lt0, lt1, lb1, lb0], fill=C((168, 160, 146)))      # 码头楼侧墙（背光）
    for k in range(3):
        u0, u1 = 0.05 + k * 0.12, 0.1 + k * 0.12
        xa, ya = _toward_vp(gx0, 58, u0)
        xb, yb = _toward_vp(gx0, 58, u1)
        _, ya2 = _toward_vp(gx0, 80, u0)
        _, yb2 = _toward_vp(gx0, 80, u1)
        d.polygon([(xa, ya), (xb, yb), (xb, yb2), (xa, ya2)], fill=C((92, 88, 92)))
    rt0, rb0 = (gx1 - 1, ROOF_Y), (gx1 - 1, STEP_Y + 1)
    rt1, rb1 = _toward_vp(*rt0), _toward_vp(*rb0)
    d.polygon([rt0, rt1, rb1, rb0], fill=C((236, 210, 140)))      # S1 侧墙（向阳，同 S1 的黄）
    for (yy0, yy1) in ((52, 80), (100, 136)):
        for k in range(2):
            u0, u1 = 0.06 + k * 0.16, 0.13 + k * 0.16
            xa, ya = _toward_vp(gx1 - 1, yy0, u0)
            xb, yb = _toward_vp(gx1 - 1, yy0, u1)
            _, ya2 = _toward_vp(gx1 - 1, yy1, u0)
            _, yb2 = _toward_vp(gx1 - 1, yy1, u1)
            d.polygon([(xa, ya), (xb, yb), (xb, yb2), (xa, ya2)], fill=C((62, 112, 88)))
            d.line([(xa, ya2), (xb, yb2)], fill=C((250, 236, 190)))
    d.line([rt0, rt1], fill=C(ROOF_D))
    d.line([(rt0[0], rt0[1] + 1), (rt1[0], rt1[1] + 1)], fill=C(ROOF))
    # 雨树：树干立在横街里（被岗亭挡住下半截），树冠又宽又平，伸到两边楼顶上
    tx = 148
    for y in range(52, 122):
        w = 2 if y > 80 else 3
        rect(d, tx - w // 2, y, tx + (w - 1) // 2 + 1, y, BARK)
        px(d, tx - w // 2, y, BARK_HI)
        px(d, tx + (w - 1) // 2 + 1, y, BARK_D)
    for (ax, ay, bx, by) in ((tx, 70, tx - 16, 50), (tx + 1, 66, tx + 18, 46), (tx, 60, tx - 6, 40)):
        d.line((ax, ay, bx, by), fill=C(BARK), width=2)
    _canopy(d, tx, 40, 46, 22, 77)
    _canopy(d, tx - 26, 50, 22, 10, 78)
    _canopy(d, tx + 28, 46, 22, 11, 79)


def draw_police_box(im):
    """交警岗亭（蓝白小亭子：四面玻璃窗、檐、顶灯）+ 红绿灯 + 过街标志。"""
    d = ImageDraw.Draw(im)
    x0, x1, base = 137, 160, STEP_Y + 1
    BL, BLD, WH = (40, 86, 160), (28, 60, 116), (240, 242, 240)
    rect(d, x0, 113, x1, base, WH)
    vl(d, x0, 113, base, (252, 252, 250))
    vl(d, x1, 113, base, (200, 204, 212))
    rect(d, x0, 138, x1, base, BL)                                # 下半截蓝
    hl(d, x0, x1, 138, (86, 132, 204))
    hl(d, x0, x1, base, BLD)
    rect(d, x0 + 2, 117, x1 - 2, 131, (60, 78, 100))              # 玻璃窗
    for xx in (x0 + 2 + (x1 - x0 - 4) // 2,):
        vl(d, xx, 117, 131, WH)
    d.line((x0 + 3, 130, x0 + 8, 118), fill=C((132, 160, 186)))  # 反光
    d.line((x0 + 13, 130, x0 + 17, 121), fill=C((112, 140, 168)))
    rect(d, x0 + 4, 125, x0 + 8, 131, (226, 214, 176))            # 窗里看得见的帽子 / 本子
    hl(d, x0 + 1, x1 - 1, 132, (220, 222, 224))                   # 窗台
    hl(d, x0 + 1, x1 - 1, 133, (176, 180, 190))
    rect(d, x0 + 4, 134, x1 - 4, 136, BL)                         # 警徽（只画一块色块）
    px(d, (x0 + x1) // 2, 135, (236, 210, 90))
    rect(d, x0 - 3, 108, x1 + 3, 112, BL)                         # 檐
    hl(d, x0 - 3, x1 + 3, 108, (96, 140, 210))
    hl(d, x0 - 3, x1 + 3, 112, BLD)
    hl(d, x0 - 2, x1 + 2, 113, (180, 184, 196))
    d.polygon([(x0 + 1, 108), (x1 - 1, 108), (x1 - 5, 104), (x0 + 5, 104)], fill=C(WH))
    hl(d, x0 + 5, x1 - 5, 104, (252, 252, 250))
    rect(d, (x0 + x1) // 2 - 2, 99, (x0 + x1) // 2 + 2, 103, (226, 70, 60))   # 顶灯
    px(d, (x0 + x1) // 2 - 1, 100, (255, 170, 160))
    hl(d, (x0 + x1) // 2 - 2, (x0 + x1) // 2 + 2, 103, (150, 40, 40))
    # 红绿灯（灰杆 + 黑白条的底座、三个灯，绿灯亮）+ 行人灯
    lx = 124
    for y in range(84, base + 1):
        px(d, lx, y, (150, 156, 164))
        px(d, lx + 1, y, (104, 110, 120))
    for y in range(134, base, 4):
        rect(d, lx, y, lx + 1, y + 1, (40, 40, 46))
    rect(d, lx - 3, 76, lx + 4, 96, (36, 38, 44))
    vl(d, lx - 3, 76, 96, (70, 74, 82))
    for i, (on, off) in enumerate((((236, 70, 60), (96, 40, 40)), ((240, 190, 60), (100, 84, 40)),
                                   ((90, 230, 140), (40, 90, 60)))):
        cy = 79 + i * 6
        c = on if i == 2 else off
        d.ellipse((lx - 1, cy, lx + 2, cy + 3), fill=C(c))
        if i == 2:
            px(d, lx, cy, (200, 255, 220))
    rect(d, lx + 3, 99, lx + 9, 109, (36, 38, 44))                # 行人灯（绿色走路小人）
    for (gx_, gy_) in ((6, 101), (5, 102), (6, 102), (7, 103), (4, 103), (6, 103), (6, 104), (5, 105), (7, 105),
                       (4, 106), (8, 106), (4, 107)):
        px(d, lx + gx_, gy_, (90, 230, 140))


# ============================================================ 近景：码头 / 海关楼
def draw_pier_building(im):
    """奶油色殖民式两层楼：四坡瓦顶、山花 + 钟、正中大拱门（看得见里面的栈桥和尽头的海）、两边拱窗、石基。"""
    d = ImageDraw.Draw(im)
    x0, x1 = PIER
    xr = x1 - 1
    cx = (x0 + x1) // 2                                          # 83
    WALL, WALL_S, WALL_HI = (238, 228, 204), (212, 198, 170), (248, 242, 224)
    STONE, STONE_S = (206, 198, 184), (176, 168, 156)
    rect(d, x0, 40, xr, STEP_Y - 1, WALL)
    mottle(im, (x0, 40, xr, STEP_Y - 1), WALL, mix(WALL, WALL_S, 0.5), WALL_HI, 91, cell=5, streaks=6)
    d = ImageDraw.Draw(im)
    # 石基（112–145）：横缝 + 错缝
    rect(d, x0, 112, xr, STEP_Y - 1, STONE)
    for y in range(112, STEP_Y, 6):
        hl(d, x0, xr, y, STONE_S)
        off = 0 if (y // 6) % 2 else 6
        for x in range(x0 + off, x1, 12):
            vl(d, x, y + 1, min(STEP_Y - 1, y + 5), STONE_S)
    hl(d, x0, xr, 111, WALL_HI)
    # 四坡瓦顶 + 檐口
    d.polygon([(x0 - 2, 40), (x1 + 1, 40), (x1 - 8, 31), (x0 + 7, 31)], fill=C(ROOF))
    for x in range(x0, x1, 3):
        d.line((x, 39, x + (cx - x) * 0.12, 32), fill=C(ROOF_D))
    hl(d, x0 + 7, x1 - 8, 31, ROOF_K)
    hl(d, x0 - 2, x1 + 1, 40, ROOF_K)
    rect(d, x0 - 2, 41, x1 + 1, 43, WALL_HI)                     # 檐口线脚 + 齿饰
    for x in range(x0 - 1, x1 + 1, 3):
        px(d, x, 43, WALL_S)
    hl(d, x0, xr, 44, dk(WALL, 0.82))
    # 中间的山花（三角楣）+ 钟
    d.polygon([(cx - 19, 41), (cx + 19, 41), (cx, 25)], fill=C(WALL_HI))
    d.line([(cx - 19, 41), (cx, 25), (cx + 19, 41)], fill=C(WALL_S))
    d.line([(cx - 17, 40), (cx, 26)], fill=C((255, 252, 240)))
    d.ellipse((cx - 5, 30, cx + 5, 40), fill=C((70, 60, 54)))
    d.ellipse((cx - 4, 31, cx + 4, 39), fill=C((246, 242, 228)))
    vl(d, cx, 32, 35, INK)
    hl(d, cx, cx + 2, 35, INK)
    # 壁柱（亮左边、右边一道影）
    for px0 in (x0, x0 + 16, x1 - 21, x1 - 5):
        rect(d, px0, 44, px0 + 4, 111, WALL_HI)
        vl(d, px0 + 4, 44, 111, WALL_S)
        px(d, px0 + 5, 46, dk(WALL, 0.9))
        rect(d, px0 - 1, 44, px0 + 5, 46, (252, 248, 236))
        hl(d, px0 - 1, px0 + 5, 47, WALL_S)
    # 两边的拱窗（上层）+ 小方窗（下层）
    for wx in (x0 + 7, x1 - 14):
        rect(d, wx - 1, 52, wx + 7, 76, (252, 248, 236))
        rect(d, wx, 56, wx + 6, 75, DARK_IN)
        d.pieslice((wx, 52, wx + 6, 60), 180, 360, fill=C(DARK_IN))
        vl(d, wx + 3, 54, 75, (120, 110, 100))
        hl(d, wx, wx + 6, 64, (120, 110, 100))
        hl(d, wx, wx + 6, 57, (90, 84, 82))
        vl(d, wx, 56, 75, (34, 30, 34))                           # 窗洞左沿的影
        rect(d, wx - 2, 77, wx + 8, 78, (252, 248, 236))
        hl(d, wx - 2, wx + 8, 79, WALL_S)
        rect(d, wx, 88, wx + 6, 102, DARK_IN)
        rect(d, wx - 1, 87, wx + 7, 87, (252, 248, 236))
        for yy in range(90, 102, 3):
            hl(d, wx, wx + 6, yy, (110, 104, 98))
    # 大拱门：拱顶 y 62、半径 14
    ax0, ax1, atop = cx - 14, cx + 14, 62
    ins = pier_interior(ax1 - ax0 + 1, STEP_Y - atop)
    m = np.zeros((STEP_Y - atop, ax1 - ax0 + 1), bool)
    r = (ax1 - ax0) / 2
    for yy in range(STEP_Y - atop):
        for xx in range(ax1 - ax0 + 1):
            y = yy + atop
            if y >= atop + r or (xx - r) ** 2 + (y - (atop + r)) ** 2 <= r * r:
                m[yy, xx] = True
    a = np.array(ins)
    a[~m, 3] = 0
    im.alpha_composite(Image.fromarray(a, 'RGBA'), (ax0, atop))
    d = ImageDraw.Draw(im)
    for ang in range(180, 361, 3):                               # 拱券（一圈石块）
        rad = math.radians(ang)
        for rr in (r + 1, r + 2):
            px(d, round(cx + math.cos(rad) * rr), round(atop + r + math.sin(rad) * rr),
               (252, 248, 236) if rr == r + 1 else WALL_S)
    rect(d, cx - 2, atop - 3, cx + 2, atop + 2, (252, 248, 236))  # 拱心石
    vl(d, cx + 2, atop - 3, atop + 2, WALL_S)
    rect(d, cx - 12, 46, cx + 12, 52, (44, 92, 96))              # 名牌（只是色块）
    hl(d, cx - 12, cx + 12, 46, (80, 130, 132))
    for i in range(7):
        rect(d, cx - 10 + i * 3, 48, cx - 9 + i * 3, 50, (226, 200, 120))
    # 门洞两边的门框
    for xx in (ax0 - 1, ax1 + 1):
        vl(d, xx, atop + int(r), STEP_Y - 1, (252, 248, 236))
    vl(d, ax1 + 2, atop + int(r), STEP_Y - 1, WALL_S)
    # 台阶
    hl(d, x0, xr, STEP_Y, GRANITE)
    hl(d, x0, xr, STEP_Y + 1, GRANITE_F)


def pier_interior(w, h):
    """拱门里的栈桥：木板地往消失点收、拱形桁架、两盏吊灯，尽头一个亮口（天 + 海 + 一艘小船）。已上好阴影。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    vx, vy = w // 2, VP[1] - 62                                   # 消失点（局部坐标）
    rect(d, 0, 0, w - 1, h - 1, (112, 104, 100))
    # 尽头的亮口
    ox0, ox1, oy0, oy1 = vx - 6, vx + 6, vy - 16, vy + 8
    rect(d, ox0, oy0, ox1, oy1, (196, 224, 240))
    rect(d, ox0, vy, ox1, oy1, (96, 156, 204))
    hl(d, ox0, ox1, vy, (220, 236, 244))
    rect(d, ox0 + 2, vy - 3, ox0 + 6, vy - 1, (240, 240, 236))    # 远处的小船
    hl(d, ox0 + 1, ox0 + 7, vy, (70, 80, 96))
    # 地板（木板往消失点收）
    for xb in range(-30, w + 31, 5):
        d.line((xb, h - 1, vx + (xb - vx) * 0.25, oy1 + 1), fill=C((128, 104, 82)))
    d.polygon([(0, h - 1), (w - 1, h - 1), (ox1, oy1 + 1), (ox0, oy1 + 1)], outline=None)
    for y in range(oy1 + 1, h):
        u = (y - oy1) / (h - oy1)
        xa = ox0 + (0 - ox0) * u
        xb = ox1 + (w - 1 - ox1) * u
        for x in range(int(xa), int(xb) + 1):
            if 0 <= x < w:
                c = (150, 122, 92) if (x - vx) * 2 // max(1, int(1 + 6 * u)) % 2 else (138, 112, 86)
                px(d, x, y, c)
    # 两边的墙 + 立柱
    for side in (0, 1):
        for k in range(4):
            u = 1 - k * 0.22
            xx = round(vx + ((0 if side == 0 else w - 1) - vx) * u)
            ytop = round(vy + (0 - vy) * u)
            ybot = round(oy1 + (h - 1 - oy1) * u)
            vl(d, xx, max(0, ytop + 6), ybot, (150, 140, 128))
    # 拱形桁架（一圈圈往里收）
    for k in range(5):
        u = 1 - k * 0.18
        rx = (w / 2) * u
        cy = vy + (14 - vy) * u
        d.arc((vx - rx, cy - rx, vx + rx, cy + rx), 180, 360, fill=C((78, 70, 68)))
    # 吊灯
    for (lx, ly) in ((vx - 6, 22), (vx + 5, 30)):
        vl(d, lx, 0, ly, (70, 64, 62))
        rect(d, lx - 1, ly, lx + 1, ly + 2, (236, 220, 170))
    shade_interior(im, top_k=0.5, bot_k=0.72)
    # 亮口不压暗：重新画回去（它是外面的天光）
    d = ImageDraw.Draw(im)
    rect(d, ox0, oy0, ox1, vy - 1, (196, 224, 240))
    rect(d, ox0, vy + 1, ox1, oy1, (96, 156, 204))
    hl(d, ox0, ox1, vy, (220, 236, 244))
    rect(d, ox0 + 2, vy - 3, ox0 + 6, vy - 1, (240, 240, 236))
    hl(d, ox0 + 1, ox0 + 7, vy, (70, 80, 96))
    return im


# ============================================================ 近景：骑楼（shophouse）
# 每栋：wall / sh（暗）/ hi（亮）/ trim（线脚）/ shutter（百叶）/ fascia（封檐板）/ win（窗数）/ wtype（窗型）/
#       arcade（五脚基开口：flat 平梁、seg 弧拱、round 圆拱）/ shop（铺子）/ sign（招牌底色、字块色）/ deco（装饰）
SHOPS = [
    dict(x=S1, wall=(240, 212, 136), sh=(212, 178, 106), hi=(250, 230, 172), trim=(250, 244, 226),
         shutter=(58, 120, 90), fascia=(96, 64, 44), win=2, wtype='rect', arcade='flat', shop='provisions',
         sign=((36, 30, 28), (220, 182, 92)), deco=('vents',), seed=1),
    dict(x=S2, wall=(236, 168, 166), sh=(204, 132, 136), hi=(246, 196, 192), trim=(252, 238, 228),
         shutter=(66, 108, 156), fascia=(40, 84, 90), win=2, wtype='arch', arcade='round', shop='medicine',
         sign=((30, 26, 26), (226, 190, 96)), deco=('tiles', 'swag', 'lanterns'), seed=2),
    dict(x=S3, wall=(162, 212, 186), sh=(122, 176, 152), hi=(196, 230, 210), trim=(246, 246, 236),
         shutter=(150, 94, 62), fascia=(110, 72, 52), win=3, wtype='fan', arcade='seg', shop='textile',
         sign=((44, 70, 60), (240, 236, 214)), deco=('cartouche',), seed=3),
    dict(x=S4, wall=(152, 194, 224), sh=(116, 156, 194), hi=(190, 218, 238), trim=(250, 248, 240),
         shutter=(56, 92, 68), fascia=(60, 60, 70), win=2, wtype='rect', arcade='flat', shop='kopitiam',
         sign=((150, 40, 36), (250, 226, 150)), deco=('balcony', 'birdcage'), seed=4),
    dict(x=S5, wall=(244, 186, 142), sh=(210, 148, 108), hi=(252, 212, 178), trim=(255, 242, 222),
         shutter=(58, 108, 118), fascia=(96, 64, 44), win=2, wtype='rect', arcade='flat', shop='hardware',
         sign=((40, 60, 96), (240, 240, 240)), deco=('third',), seed=5),
    dict(x=S6, wall=(196, 178, 220), sh=(160, 140, 188), hi=(220, 206, 236), trim=(250, 244, 236),
         shutter=(112, 72, 58), fascia=(70, 54, 80), win=2, wtype='key', arcade='seg', shop='barber',
         sign=((30, 30, 40), (200, 220, 240)), deco=('vent_round',), seed=6),
    dict(x=S7, wall=(122, 196, 194), sh=(88, 158, 160), hi=(166, 220, 216), trim=(248, 248, 240),
         shutter=(212, 124, 60), fascia=(48, 64, 70), win=3, wtype='transom', arcade='flat', shop='books',
         sign=((236, 230, 210), (60, 80, 120)), deco=('tiles',), seed=7),
]
PIER_XS = [S1[0], S1[1], S2[0], S3[0], S4[0], S5[0], S5[1], S6[0], S7[0], S7[1]]
FAN_POS = [(330, 98, ARC_Y), (441, 98, ARC_Y), (550, 105, ARC_Y + 4), (674, 105, ARC_Y + 4), (739, 101, ARC_Y + 1)]   # (x, 扇叶 y, 杆顶 y)
LAUNDRY = [(208, 229, 61), (390, 411, 63), (482, 507, 25)]   # (x0, x1, 竿的 y)


def _win_mask(w, h, kind):
    """窗洞形状（局部坐标）：kind 里带拱的上面是半圆。"""
    m = np.ones((h, w), bool)
    if kind in ('arch', 'fan', 'key'):
        r = (w - 1) / 2
        for yy in range(int(math.ceil(r)) + 1):
            for xx in range(w):
                if (xx - r) ** 2 + (yy - r) ** 2 > (r + 0.35) ** 2:
                    m[yy, xx] = False
    return m


def draw_window(im, x, y0, y1, w, s, kind, open_leaf=None):
    """一扇长窗（x..x+w−1，y0..y1）：线脚框 + 百叶（两扇）+ 气窗 / 拱；窗洞上沿、左沿暗（凹进去），窗台下一道影。
    open_leaf = 'l' / 'r'：那一扇百叶开着（看得见屋里暗 + 窗帘）。"""
    h = y1 - y0 + 1
    m = _win_mask(w, h, kind)
    d = ImageDraw.Draw(im)
    trim, shut = s['trim'], s['shutter']
    shut_d, shut_hi = dk(shut, 0.72), lt(shut, 0.22)
    # 框（外扩 1 px 的线脚）
    mm = np.zeros((h + 2, w + 2), bool)
    mm[1:-1, 1:-1] = m
    grow = mm.copy()
    grow[:-1] |= mm[1:]
    grow[1:] |= mm[:-1]
    grow[:, :-1] |= mm[:, 1:]
    grow[:, 1:] |= mm[:, :-1]
    for yy, xx in zip(*np.nonzero(grow & ~mm)):
        px(d, x - 1 + xx, y0 - 1 + yy, trim)
    r = (w - 1) / 2
    fan_h = int(math.ceil(r)) + 1 if kind in ('arch', 'fan', 'key') else (5 if kind == 'transom' else 0)
    mid = x + w // 2
    for yy, xx in zip(*np.nonzero(m)):
        X, Y = x + xx, y0 + yy
        if yy < fan_h and kind in ('fan', 'key', 'transom'):
            c = GLASS if (xx + yy) % 3 else GLASS_HI
            if kind == 'transom':
                c = GLASS if (xx % 3 and yy % 2) else trim
            elif kind in ('fan', 'key'):
                ang = math.degrees(math.atan2(r + 1 - yy, xx - r))
                if abs(((ang + 180) % 30) - 15) > 12 or yy == fan_h - 1:
                    c = trim
            px(d, X, Y, c)
            continue
        leaf = 'l' if X < mid else 'r'
        if open_leaf == leaf:
            c = DARK_IN
            if (leaf == 'l' and xx in (1, 2)) or (leaf == 'r' and xx in (w - 3, w - 2)):
                c = (226, 214, 188) if yy % 4 else (204, 190, 164)    # 窗帘
            px(d, X, Y, c)
            continue
        c = shut if (yy % 2 == 0) else shut_d
        if X in (x, mid) or X == x + w - 1 or X == mid - 1:
            c = shut_hi if X in (x, mid) else shut_d
        if yy == fan_h or yy == h - 1:
            c = shut_hi
        px(d, X, Y, c)
    if kind in ('arch',):
        for yy in range(fan_h):
            for xx in range(w):
                if m[yy, xx]:
                    px(d, x + xx, y0 + yy, shut if (yy % 2 == 0) else shut_d)
    # 凹进去的影：上沿一行 + 左沿一列
    a = np.array(im)
    for yy, xx in zip(*np.nonzero(m)):
        top = yy == 0 or not m[yy - 1, xx]
        left = xx == 0 or not m[yy, xx - 1]
        if top or left or (yy == fan_h and fan_h):
            a[y0 + yy, x + xx, :3] = (a[y0 + yy, x + xx, :3] * 0.72).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    # 窗台
    rect(d, x - 2, y1 + 1, x + w + 1, y1 + 2, trim)
    hl(d, x - 2, x + w + 1, y1 + 3, s['sh'])
    if kind == 'key':
        rect(d, mid - 1, y0 - 3, mid + 1, y0 + 1, trim)
        vl(d, mid + 1, y0 - 3, y0 + 1, s['sh'])


def shop_interior(kind, w, seed):
    """五脚基里看得见的铺面（局部坐标，w × 46 行 = y 94–139），先画亮色，最后统一压阴影。"""
    h = FLOOR_Y - ARC_Y
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    R = lambda *k: hrange(0, 1, seed, *k)  # noqa: E731
    backs = dict(provisions=(204, 184, 150), medicine=(150, 98, 74), textile=(214, 200, 176), kopitiam=(224, 216, 196),
                 hardware=(168, 166, 156), barber=(206, 214, 216), books=(178, 146, 108))
    back = backs[kind]
    rect(d, 0, 0, w - 1, h - 1, back)
    hl(d, 0, w - 1, 0, dk(back, 0.6))
    hl(d, 0, w - 1, 1, dk(back, 0.75))
    # 铺面的门洞（暗）+ 门楣上的招牌（黑底金字块）
    dx0, dx1 = 4, w - 5
    inside = dk(back, 0.48)
    if kind in ('medicine', 'barber'):
        dx0, dx1 = w // 2 - 8, w // 2 + 7
    rect(d, dx0, 10, dx1, h - 1, inside)
    bx0, bx1 = w // 2 - min(16, w // 2 - 4), w // 2 + min(16, w // 2 - 4)
    rect(d, bx0, 3, bx1, 8, (34, 28, 26))
    hl(d, bx0, bx1, 3, (70, 60, 54))
    for i, xx in enumerate(range(bx0 + 3, bx1 - 2, 5)):
        rect(d, xx, 5, xx + 2, 6, (214, 176, 90))
    for xx in (dx0 - 1, dx1 + 1):                                 # 门框
        vl(d, xx, 9, h - 1, dk(back, 0.7))
    if kind == 'provisions':
        for row, yy in enumerate((16, 24, 32)):                  # 货架 + 罐头 / 瓶子
            hl(d, dx0, dx1, yy, (150, 112, 72))
            for xx in range(dx0 + 1, dx1, 3):
                c = ((200, 60, 50), (230, 190, 70), (70, 130, 80), (70, 100, 170), (230, 230, 220))[int(R(row, xx) * 5)]
                rect(d, xx, yy - 4 + int(R(row, xx, 1) * 2), xx + 1, yy - 1, c)
        for xx in range(dx0 + 2, dx1 - 2, 6):                    # 挂着的竹篮
            d.arc((xx, 9, xx + 5, 14), 0, 180, fill=C((176, 140, 90)))
        for xx in range(1, w - 6, 7):                             # 门口一排米袋
            rect(d, xx, 37, xx + 6, h - 1, (222, 204, 164))
            hl(d, xx + 1, xx + 5, 36, (204, 186, 146))
            hl(d, xx + 2, xx + 4, 35, (190, 170, 130))
            vl(d, xx + 6, 37, h - 1, (186, 166, 128))
            hl(d, xx + 1, xx + 5, 40, (190, 80, 70) if xx % 2 else (70, 110, 170))
    elif kind == 'medicine':
        for side in (0, 1):                                       # 两边的百子柜
            x0 = 2 if side == 0 else dx1 + 3
            x1 = dx0 - 3 if side == 0 else w - 3
            rect(d, x0, 12, x1, 36, (126, 80, 52))
            for yy in range(13, 36, 4):
                for xx in range(x0 + 1, x1, 4):
                    rect(d, xx, yy, xx + 2, yy + 2, (156, 104, 66))
                    px(d, xx + 1, yy + 1, (226, 196, 110))
            rect(d, x0, 37, x1, h - 1, (110, 70, 46))
            for xx in range(x0 + 2, x1 - 2, 6):                   # 青花瓷罐
                d.ellipse((xx, 30, xx + 4, 36), fill=C((226, 230, 236)))
                hl(d, xx + 1, xx + 3, 33, (60, 90, 170))
        rect(d, dx0 + 2, 30, dx1 - 2, h - 1, (120, 76, 50))       # 柜台
        hl(d, dx0 + 2, dx1 - 2, 30, (170, 120, 80))
        rect(d, dx0 + 5, 14, dx1 - 5, 22, (190, 60, 50))          # 后面的红纸神龛
        rect(d, dx0 + 8, 16, dx1 - 8, 20, (226, 196, 110))
    elif kind == 'textile':
        for row, yy in enumerate((14, 23, 32)):
            hl(d, dx0, dx1, yy + 8, (140, 104, 70))
            for xx in range(dx0 + 1, dx1 - 2, 4):
                c = ((60, 90, 170), (200, 70, 130), (230, 196, 70), (70, 150, 110), (236, 236, 226), (150, 70, 160),
                     (230, 120, 60))[int(R(row, xx) * 7)]
                rect(d, xx, yy, xx + 2, yy + 7, c)
                vl(d, xx + 2, yy, yy + 7, dk(c, 0.78))
                if R(row, xx, 2) < 0.4:
                    for k in range(yy + 1, yy + 7, 2):
                        px(d, xx + 1, k, lt(c, 0.4))
        for i in range(3):                                        # 挂在门口的布（斜纹）
            xx = 3 + i * (w - 10) // 2
            c = ((210, 90, 60), (60, 110, 160), (220, 180, 70))[i]
            rect(d, xx, 10, xx + 5, 30, c)
            for k in range(10, 31, 3):
                hl(d, xx, xx + 5, k, dk(c, 0.8))
            vl(d, xx + 5, 10, 30, dk(c, 0.7))
        rect(d, dx0 + 6, 36, dx1 - 6, h - 1, (140, 104, 70))      # 量布的长台
        hl(d, dx0 + 6, dx1 - 6, 36, (180, 140, 96))
    elif kind == 'kopitiam':
        rect(d, 0, 28, w - 1, h - 1, (120, 170, 150))             # 墙裙绿瓷砖
        for yy in range(28, h, 3):
            hl(d, 0, w - 1, yy, (100, 150, 132))
        for xx in range(0, w, 3):
            vl(d, xx, 28, h - 1, (100, 150, 132))
        rect(d, 3, 12, 15, 26, (40, 40, 44))                      # 饮料档：玻璃柜 + 杯子
        rect(d, 4, 13, 14, 20, (120, 150, 170))
        for xx in range(5, 14, 2):
            px(d, xx, 18, (236, 236, 236))
        rect(d, 3, 27, 15, h - 1, (110, 76, 52))
        hl(d, 3, 15, 27, (170, 130, 90))
        rect(d, w - 18, 12, w - 6, 22, (176, 196, 210))           # 镜子（色块字）
        rect(d, w - 18, 12, w - 6, 12, (150, 112, 70))
        for xx in range(w - 16, w - 7, 3):
            px(d, xx, 16, (180, 50, 50))
        for (tx, ty) in ((22, 34), (w - 12, 35)):                 # 大理石圆桌 + 木椅
            rect(d, tx - 4, ty, tx + 4, ty + 1, (240, 240, 236))
            hl(d, tx - 4, tx + 4, ty + 1, (200, 200, 200))
            vl(d, tx, ty + 2, h - 2, (60, 56, 56))
            hl(d, tx - 2, tx + 2, h - 1, (60, 56, 56))
            for cx in (tx - 7, tx + 7):
                vl(d, cx, ty - 6, h - 1, (110, 70, 44))
                hl(d, cx - 1, cx + 1, ty + 3, (130, 86, 54))
                vl(d, cx - 1 if cx < tx else cx + 1, ty + 3, h - 1, (110, 70, 44))
            px(d, tx - 2, ty - 1, (250, 250, 250))                # 杯子
            px(d, tx + 1, ty - 1, (200, 140, 80))
    elif kind == 'hardware':
        for xx in range(dx0 + 2, dx1 - 4, 7):                     # 挂着的铁桶
            d.polygon([(xx, 12), (xx + 5, 12), (xx + 4, 18), (xx + 1, 18)], fill=C((190, 196, 204)))
            hl(d, xx, xx + 5, 12, (230, 234, 238))
            d.arc((xx, 9, xx + 5, 14), 180, 360, fill=C((120, 124, 130)))
        for xx in range(dx0 + 1, dx1 - 3, 9):                     # 盘好的绳子
            d.ellipse((xx, 21, xx + 6, 27), outline=C((200, 170, 110)))
            d.ellipse((xx + 1, 22, xx + 5, 26), outline=C((176, 146, 92)))
        for k in range(4):                                        # 靠墙的扫帚 / 竹梯
            xx = 2 + k * 3
            d.line((xx, h - 1, xx + 3, 14), fill=C((196, 160, 100)))
        for yy in range(16, h, 4):
            hl(d, w - 9, w - 4, yy, (176, 140, 90))
        vl(d, w - 9, 14, h - 1, (176, 140, 90))
        vl(d, w - 4, 14, h - 1, (176, 140, 90))
        for xx in range(dx0 + 4, dx1 - 10, 5):                    # 油漆罐
            rect(d, xx, 38, xx + 3, h - 1, ((200, 70, 60), (70, 120, 190), (230, 200, 70))[(xx // 5) % 3])
            hl(d, xx, xx + 3, 38, (210, 210, 214))
    elif kind == 'barber':
        rect(d, 2, 12, dx0 - 3, 28, (180, 206, 220))              # 大镜子
        hl(d, 2, dx0 - 3, 12, (220, 236, 244))
        d.line((4, 26, 10, 14), fill=C((230, 242, 250)))
        rect(d, 2, 29, dx0 - 3, 31, (220, 220, 224))
        cx = (dx0 + dx1) // 2                                     # 理发椅
        rect(d, cx - 4, 22, cx + 3, 33, (110, 56, 50))
        rect(d, cx - 5, 33, cx + 4, 35, (110, 56, 50))
        hl(d, cx - 4, cx + 3, 22, (150, 86, 76))
        vl(d, cx, 36, h - 3, (200, 204, 212))
        hl(d, cx - 3, cx + 3, h - 2, (200, 204, 212))
        rect(d, dx1 + 3, 14, w - 3, 30, (236, 236, 230))          # 价目牌（色块）
        for yy in range(16, 29, 3):
            hl(d, dx1 + 5, w - 5, yy, (90, 110, 150))
    elif kind == 'books':
        for row, yy in enumerate((12, 20, 28)):
            hl(d, dx0, dx1, yy + 7, (120, 86, 56))
            xx = dx0 + 1
            while xx < dx1 - 1:
                bw = 1 + int(R(row, xx) * 2)
                c = ((180, 60, 50), (60, 90, 160), (230, 210, 150), (70, 130, 90), (200, 160, 60), (240, 240, 232),
                     (120, 70, 130))[int(R(row, xx, 1) * 7)]
                hh = 5 + int(R(row, xx, 2) * 2)
                rect(d, xx, yy + 7 - hh, xx + bw - 1, yy + 6, c)
                xx += bw
        rect(d, 2, 36, w - 3, h - 1, (110, 80, 54))               # 门口的杂志架
        for xx in range(4, w - 6, 5):
            c = ((230, 90, 80), (90, 160, 210), (240, 220, 90), (130, 200, 120))[(xx // 5) % 4]
            rect(d, xx, 33, xx + 3, 39, c)
            hl(d, xx, xx + 3, 33, lt(c, 0.4))
    shade_interior(im, top_k=0.5, bot_k=0.74)
    return im


def _arcade_mask(w, kind):
    h = FLOOR_Y - ARC_Y
    m = np.ones((h, w), bool)
    if kind == 'round':
        r = (w - 1) / 2
        for yy in range(h):
            for xx in range(w):
                if yy < r and (xx - r) ** 2 + (yy - r) ** 2 > r * r:
                    m[yy, xx] = False
    elif kind == 'seg':
        for xx in range(w):
            u = (xx - (w - 1) / 2) / ((w - 1) / 2)
            top = int(round(6 * u * u))
            m[:top, xx] = False
    return m


def draw_shophouse(im, s):
    x0, x1 = s['x']
    xr = x1 - 1
    wall, sh, hi, trim = s['wall'], s['sh'], s['hi'], s['trim']
    third = 'third' in s['deco']
    top = 6 if third else EAVE_Y
    d = ImageDraw.Draw(im)
    rect(d, x0, top, xr, STEP_Y - 1, wall)
    mottle(im, (x0, top, xr, STEP_Y - 1), wall, mix(wall, sh, 0.45), mix(wall, hi, 0.55), 100 + s['seed'],
           cell=4, streaks=7)
    d = ImageDraw.Draw(im)
    ix0, ix1 = x0 + 3, x1 - 4                                     # 两边壁柱之间
    # ---------------- 屋顶
    if not third:
        # 筒瓦（每 3 px 一垄：亮 / 中 / 沟），每 3 行一道瓦缝；老一点的楼瓦色发灰、零星几块发黑的旧瓦
        age = hrange(0.0, 0.35, s['seed'], 71)
        pal = [mix(c, (150, 120, 104), age) for c in (ROOF_HI, ROOF, ROOF_D, ROOF_K)]
        for y in range(ROOF_Y, EAVE_Y):
            for x in range(x0 - 1, x1 + 1):
                k = (x + (1 if (y - ROOF_Y) % 6 >= 3 else 0)) % 3
                c = pal[k]
                if y == ROOF_Y:
                    c = pal[3]
                elif y == ROOF_Y + 1:
                    c = mix(pal[0], (240, 210, 180), 0.3)
                elif (y - ROOF_Y) % 3 == 0:
                    c = dk(c, 0.88)
                elif y < ROOF_Y + 4:
                    c = mix(c, (236, 196, 170), 0.2)
                if hash01(x // 3, (y - ROOF_Y) // 3, s['seed'], 72) < 0.06:
                    c = dk(c, 0.8)
                if y == EAVE_Y - 1:
                    c = (pal[0] if k == 0 else dk(pal[2], 0.8))           # 檐口一排瓦当
                px(d, x, y, c)
        rect(d, x0 - 1, EAVE_Y, x1, EAVE_Y + 2, s['fascia'])      # 封檐板 + 花边
        hl(d, x0 - 1, x1, EAVE_Y, lt(s['fascia'], 0.25))
        for x in range(x0 - 1, x1 + 1, 2):
            px(d, x, EAVE_Y + 3, s['fascia'])
        hl(d, x0, xr, EAVE_Y + 4, dk(wall, 0.8))                  # 檐下的影
        for x in range(x0, x1, 2):
            px(d, x, EAVE_Y + 5, dk(wall, 0.9))
    else:
        # 三层：女儿墙 + 宝瓶栏杆，三楼一排小窗 + 花砖通风墙
        rect(d, x0 - 1, 2, x1, 5, trim)
        hl(d, x0 - 1, x1, 2, (255, 255, 250))
        hl(d, x0 - 1, x1, 6, sh)
        for x in range(ix0 + 2, ix1 - 1, 3):
            rect(d, x, 7, x + 1, 11, trim)
            px(d, x + 1, 11, sh)
            rect(d, x - 1, 7, x - 1, 11, dk(wall, 0.7))
        rect(d, x0, 12, xr, 13, trim)
        hl(d, x0, xr, 14, sh)
        for i in range(3):
            wx = ix0 + 4 + i * ((ix1 - ix0 - 8) // 3 + 1)
            draw_window(im, wx, 19, 33, 7, s, 'rect', open_leaf='l' if i == 1 else None)
        d = ImageDraw.Draw(im)
        for x in range(ix0 + 2, ix1 - 1):                         # 花砖通风墙（breeze blocks）
            for y in (37, 38, 39):
                if (x + y) % 2 == 0:
                    px(d, x, y, trim)
                else:
                    px(d, x, y, dk(wall, 0.6))
        rect(d, x0 - 1, 40, x1, 42, trim)                         # 二三楼之间的线脚
        hl(d, x0 - 1, x1, 40, (255, 255, 250))
        hl(d, x0, xr, 43, sh)
    # ---------------- 二楼的窗
    n = s['win']
    ww = 10 if n == 2 else 8
    span = ix1 - ix0 + 1
    gap = (span - n * ww) / (n + 1)
    wx_list = [int(round(ix0 + gap * (i + 1) + ww * i)) for i in range(n)]
    for i, wx in enumerate(wx_list):
        ol = None
        if hash01(s['seed'], i, 5) < 0.4:
            ol = 'l' if hash01(s['seed'], i, 6) < 0.5 else 'r'
        draw_window(im, wx, 52, 80, ww, s, s['wtype'], open_leaf=ol)
    d = ImageDraw.Draw(im)
    if 'tiles' in s['deco']:                                      # 窗下的娘惹瓷砖
        for wx in wx_list:
            for x in range(wx - 1, wx + ww + 1):
                for y in (83, 84):
                    c = ((70, 140, 170), (240, 236, 220), (220, 110, 120), (110, 170, 110))[(x // 2 + y) % 4]
                    px(d, x, y, c)
            hl(d, wx - 1, wx + ww, 85, dk(wall, 0.8))
        if len(wx_list) > 1:                                      # 两窗之间一块方瓷砖
            mx = (wx_list[0] + ww + wx_list[1]) // 2
            for y in range(60, 72):
                for x in range(mx - 3, mx + 3):
                    u, v = x - (mx - 3), y - 60
                    c = (70, 140, 170) if (u + v) % 4 == 0 else ((240, 236, 220) if (u * v) % 3 else (220, 110, 120))
                    px(d, x, y, c)
            hl(d, mx - 3, mx + 2, 72, dk(wall, 0.78))
            vl(d, mx + 3, 60, 72, dk(wall, 0.85))
    if 'swag' in s['deco']:                                       # 窗上的灰塑花饰
        for wx in wx_list:
            for k in range(ww + 2):
                y = 48 + int(1.5 * math.sin(math.pi * k / (ww + 1)))
                px(d, wx - 1 + k, y, hi)
                px(d, wx - 1 + k, y + 1, sh)
            px(d, wx + ww // 2, 46, hi)
            px(d, wx + ww // 2 - 1, 47, (220, 110, 120))
            px(d, wx + ww // 2 + 1, 47, (110, 170, 110))
    if 'cartouche' in s['deco']:                                  # 檐下的浮雕牌匾
        cx = (x0 + x1) // 2
        d.ellipse((cx - 7, 45, cx + 7, 50), fill=C(trim))
        d.ellipse((cx - 5, 46, cx + 5, 49), fill=C(hi))
        hl(d, cx - 6, cx + 6, 51, sh)
    if 'vents' in s['deco']:
        for wx in wx_list:
            for x in range(wx + 1, wx + ww - 1, 2):
                px(d, x, 47, dk(wall, 0.6))
                px(d, x, 48, dk(wall, 0.75))
    if 'vent_round' in s['deco']:
        cx = (x0 + x1) // 2
        d.ellipse((cx - 3, 45, cx + 3, 50), fill=C(trim))
        d.ellipse((cx - 2, 46, cx + 2, 49), fill=C(dk(wall, 0.55)))
        vl(d, cx, 46, 49, trim)
    if 'balcony' in s['deco']:                                    # 铸铁小阳台（凸出来，影落在右下）
        bx0, bx1 = wx_list[0] - 3, wx_list[-1] + ww + 2
        rect(d, bx0, 81, bx1, 82, trim)
        hl(d, bx0, bx1, 83, sh)
        hl(d, bx0 + 1, bx1 + 1, 84, dk(wall, 0.84))
        hl(d, bx0, bx1, 70, IRON)
        hl(d, bx0, bx1, 71, IRON_HI)
        for x in range(bx0, bx1 + 1, 2):
            vl(d, x, 72, 80, IRON)
        for x in range(bx0 + 1, bx1, 4):
            d.ellipse((x, 74, x + 2, 77), outline=C(IRON))
        for x in (bx0 + 2, bx1 - 2):                              # 两盆花
            rect(d, x - 1, 66, x + 1, 69, (176, 90, 60))
            d.ellipse((x - 3, 61, x + 3, 67), fill=C(LEAF))
            px(d, x - 1, 62, (230, 80, 140))
            px(d, x + 1, 63, (240, 120, 170))
    # ---------------- 一楼檐口 + 招牌带（86–93）
    rect(d, x0, BEAM_Y - 1, xr, BEAM_Y, trim)
    hl(d, x0, xr, BEAM_Y - 2, lt(trim, 0.5))
    hl(d, x0, xr, BEAM_Y + 1, dk(wall, 0.74))
    sb0, sb1 = ix0 + 4, ix1 - 4
    bg, fgc = s['sign']
    rect(d, sb0, BEAM_Y + 2, sb1, ARC_Y - 1, bg)
    hl(d, sb0, sb1, BEAM_Y + 2, lt(bg, 0.25))
    vl(d, sb1 + 1, BEAM_Y + 3, ARC_Y - 1, dk(wall, 0.8))
    for x in range(sb0 + 3, sb1 - 2, 6):
        rect(d, x, BEAM_Y + 4, x + 3, ARC_Y - 3, fgc)
    # ---------------- 五脚基（开口 + 铺面）
    ow = ix1 - ix0 + 1
    ins = shop_interior(s['shop'], ow, s['seed'])
    a = np.array(ins)
    a[~_arcade_mask(ow, s['arcade']), 3] = 0
    im.alpha_composite(Image.fromarray(a, 'RGBA'), (ix0, ARC_Y))
    d = ImageDraw.Draw(im)
    if s['arcade'] == 'round':                                    # 拱的线脚
        r = (ow - 1) / 2
        for ang in range(180, 361, 2):
            rad = math.radians(ang)
            px(d, round(ix0 + r + math.cos(rad) * (r + 1)), round(ARC_Y + r + math.sin(rad) * (r + 1)), trim)
    elif s['arcade'] == 'seg':
        for xx in range(ow):
            u = (xx - (ow - 1) / 2) / ((ow - 1) / 2)
            px(d, ix0 + xx, ARC_Y - 1 + int(round(6 * u * u)), trim)
    else:
        hl(d, ix0, ix1, ARC_Y, dk(wall, 0.55))
    if 'lanterns' in s['deco']:
        for lx in (ix0 + 8, ix1 - 8):
            vl(d, lx, ARC_Y + 1, ARC_Y + 3, (60, 50, 40))
            d.ellipse((lx - 3, ARC_Y + 4, lx + 3, ARC_Y + 11), fill=C((206, 50, 44)))
            vl(d, lx - 2, ARC_Y + 6, ARC_Y + 9, (236, 110, 90))
            hl(d, lx - 1, lx + 1, ARC_Y + 4, (220, 180, 80))
            hl(d, lx - 1, lx + 1, ARC_Y + 11, (220, 180, 80))
            vl(d, lx, ARC_Y + 12, ARC_Y + 15, (220, 180, 80))
    if 'birdcage' in s['deco']:
        cx, cy = ix0 + 10, ARC_Y + 6
        vl(d, cx, ARC_Y + 1, cy, (60, 50, 40))
        d.ellipse((cx - 4, cy, cx + 4, cy + 10), outline=C((196, 168, 112)))
        for xx in range(cx - 2, cx + 3, 2):
            vl(d, xx, cy + 1, cy + 9, (176, 146, 96))
        hl(d, cx - 4, cx + 4, cy + 9, (150, 116, 70))
        px(d, cx, cy + 5, (240, 220, 70))                         # 小黄鸟
        px(d, cx + 1, cy + 5, (220, 190, 60))
    draw_arcade_floor(im, ix0, ix1 + 1)
    mul_box(im, (ix0, FLOOR_Y, ix1, STEP_Y - 1), (0.7, 0.72, 0.8))


def draw_piers(im):
    """每两栋骑楼之间的壁柱 / 五脚基的方柱（6 px 宽，左亮右暗、柱头柱础、右边一道投影），屋顶上一截封火山墙。"""
    walls = {s['x'][0]: s for s in SHOPS}
    for xb in PIER_XS:
        left = next((s for s in SHOPS if s['x'][1] == xb), None)
        right = walls.get(xb)
        s = left or right
        col = mix(s['wall'], s['trim'], 0.45)
        sh = s['sh']
        x0, x1 = xb - 3, xb + 2
        top_l = (6 if 'third' in left['deco'] else EAVE_Y) if left else None
        top_r = (6 if 'third' in right['deco'] else EAVE_Y) if right else None
        top = max(t for t in (top_l, top_r) if t is not None) + 4      # 到矮的那一栋的檐下
        d = ImageDraw.Draw(im)
        rect(d, x0, top, x1, STEP_Y - 1, col)
        vl(d, x0, top, STEP_Y - 1, lt(col, 0.4))
        vl(d, x1, top, STEP_Y - 1, mix(col, sh, 0.7))
        if right:
            vl(d, x1 + 1, top, ARC_Y - 1, dk(right['wall'], 0.86))       # 投在右边墙上的一道影
        # 柱头 / 柱础 / 中间的线脚
        for (y, w) in ((BEAM_Y - 3, 1), (ARC_Y, 1)):
            rect(d, x0 - w, y, x1 + w, y + 1, lt(col, 0.35))
            hl(d, x0 - w, x1 + w, y + 2, mix(col, sh, 0.8))
        rect(d, x0 - 1, 138, x1 + 1, STEP_Y - 1, mix(col, (150, 146, 140), 0.4))
        hl(d, x0 - 1, x1 + 1, 138, lt(col, 0.3))
        vl(d, x1 + 1, 139, STEP_Y - 1, mix(col, sh, 0.9))
        # 封火山墙：两栋之间高出屋顶的一截墙（墙帽深灰、左亮右暗），墙脚压着瓦
        if left and right and top_l == EAVE_Y and top_r == EAVE_Y:
            rect(d, xb - 3, ROOF_Y - 5, xb + 2, EAVE_Y - 1, col)
            vl(d, xb - 3, ROOF_Y - 4, EAVE_Y - 1, lt(col, 0.4))
            vl(d, xb + 2, ROOF_Y - 4, EAVE_Y - 1, mix(col, sh, 0.8))
            rect(d, xb - 4, ROOF_Y - 7, xb + 3, ROOF_Y - 6, (120, 116, 112))
            hl(d, xb - 4, xb + 3, ROOF_Y - 7, (176, 172, 166))
            px(d, xb + 3, ROOF_Y - 6, (90, 86, 84))
            hl(d, xb - 2, xb + 1, ROOF_Y - 5, mix(col, sh, 0.5))
            for y in range(ROOF_Y, EAVE_Y, 2):
                px(d, xb + 3, y, dk(ROOF, 0.7))                       # 墙右边瓦上的一道影


# ============================================================ 近景：装饰艺术风旅行社 + 鱼尾狮海报
MERLION = [          # 鱼尾狮剪影（朝右，嘴里喷水）：# 白、s 阴影、e 眼、m 嘴
    "...ss#....",
    "..s####...",
    ".s######..",
    ".s####e#..",
    "ss#######m",
    ".s#####m..",
    "..s###....",
    "..s###....",
    "..s####...",
    ".s#####...",
    "ss######..",
    "s..s####..",
    "s...s####.",
    "ss...s###.",
    ".s...s####",
]


def draw_poster(im, box):
    """旅游海报（box = x0, y0, x1, y1，右下不含）：白边 + 细框；上面一条红标题条（白色字块，读不出来），
    青绿天空 + 橙太阳，鱼尾狮站在台座上往右喷一道水，下面海浪；最下面一条深蓝字块条。边角有胶带。"""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(im)
    rect(d, x0, y0, x1 - 1, y1 - 1, (250, 248, 240))               # 白边
    rect(d, x0 - 1, y0 - 1, x1, y1, None, outline=(150, 140, 120))
    ix0, iy0, ix1, iy1 = x0 + 2, y0 + 2, x1 - 3, y1 - 3
    sub = A._new(ix1 - ix0 + 1, iy1 - iy0 + 1)
    gradient(sub, (0, 0, sub.width, sub.height), [(86, 186, 206), (140, 214, 222), (206, 236, 226)], bands=5)
    im.alpha_composite(sub, (ix0, iy0))
    d = ImageDraw.Draw(im)
    d.ellipse((ix1 - 9, iy0 + 7, ix1 - 2, iy0 + 14), fill=C((250, 170, 70)))     # 太阳
    d.ellipse((ix1 - 7, iy0 + 9, ix1 - 4, iy0 + 12), fill=C((255, 214, 120)))
    rect(d, ix0, iy0, ix1, iy0 + 5, (204, 58, 48))                 # 标题条
    for xx in range(ix0 + 2, ix1 - 1, 3):
        rect(d, xx, iy0 + 2, xx + 1, iy0 + 3, (252, 246, 236))
    # 海 + 浪
    sea_y = iy1 - 8
    rect(d, ix0, sea_y, ix1, iy1, (40, 110, 176))
    for yy in range(sea_y + 1, iy1 - 3, 2):
        for xx in range(ix0 + (yy % 4), ix1, 4):
            hl(d, xx, xx + 1, yy, (150, 206, 236))
    # 鱼尾狮 + 台座
    mx, my = ix0 + 3, iy0 + 8
    for r, row in enumerate(MERLION):
        for c, ch in enumerate(row):
            col = {'#': (250, 250, 244), 's': (190, 198, 206), 'e': (40, 50, 70), 'm': (90, 120, 150)}.get(ch)
            if col:
                px(d, mx + c, my + r, col)
    rect(d, mx + 3, my + 15, mx + 11, sea_y, (176, 170, 160))      # 台座
    hl(d, mx + 3, mx + 11, my + 15, (220, 214, 202))
    vl(d, mx + 11, my + 16, sea_y, (130, 124, 116))
    # 嘴里喷出来的水（一道弧，越往下越散）
    sx, sy = mx + 10, my + 4
    for k in range(0, 15):
        u = k / 14
        xx = sx + 1 + round(11 * u)
        yy = sy - round(3 * math.sin(math.pi * u * 0.6)) + round(12 * u * u)
        if xx <= ix1 and yy < sea_y:
            px(d, xx, yy, (250, 252, 255) if k % 3 else (190, 230, 250))
            if k > 8:
                px(d, xx + 1, yy + 1, (200, 236, 250))
    for (xx, yy) in ((sx + 9, sea_y - 2), (sx + 12, sea_y - 1), (sx + 7, sea_y - 1)):
        if xx <= ix1:
            px(d, xx, yy, (230, 246, 252))
    rect(d, ix0, iy1 - 2, ix1, iy1, (26, 52, 104))                 # 下面的字块条
    for xx in range(ix0 + 2, ix1 - 3, 4):
        hl(d, xx, xx + 2, iy1 - 1, (236, 236, 240))
    for (cx, cy) in ((x0, y0), (x1 - 1, y0)):                      # 胶带
        rect(d, cx - 1, cy - 1, cx + 1, cy + 1, (236, 230, 196))
    # 太阳晒得有点褪色：整张往白里提一点
    mul_box(im, (x0, y0, x1 - 1, y1 - 1), (1.0, 1.0, 1.0))


def draw_deco(im):
    """装饰艺术风的两层旅行社（1930 年代）：平顶女儿墙、正中竖鳍塔、钢窗 + 遮阳檐、流线横纹；
    一楼没有拱廊：左边凹进去的玻璃门（门楣上一块招牌 + 小飞机图标），右边平墙上贴着鱼尾狮海报。"""
    x0, x1 = DECO
    xr = x1 - 1
    cx = (x0 + x1) // 2
    CREAM, CREAM_S, CREAM_HI = (238, 230, 206), (208, 198, 172), (250, 244, 228)
    MINT, TEAL = (118, 190, 170), (46, 108, 106)
    d = ImageDraw.Draw(im)
    rect(d, x0, 28, xr, STEP_Y - 1, CREAM)
    mottle(im, (x0, 28, xr, STEP_Y - 1), CREAM, mix(CREAM, CREAM_S, 0.5), CREAM_HI, 141, cell=5, streaks=8)
    d = ImageDraw.Draw(im)
    # 女儿墙 + 流线横纹
    hl(d, x0, xr, 28, CREAM_HI)
    for y in (31, 34):
        hl(d, x0 + 2, xr - 2, y, CREAM_S)
        hl(d, x0 + 2, xr - 2, y + 1, CREAM_HI)
    hl(d, x0, xr, 37, CREAM_S)
    # 正中竖鳍塔（高出屋顶，阶梯形）
    tx0, tx1 = cx - 10, cx + 10
    rect(d, tx0, 14, tx1, 40, CREAM)
    rect(d, tx0 + 3, 9, tx1 - 3, 14, CREAM)
    rect(d, tx0 + 6, 5, tx1 - 6, 9, CREAM)
    for (a, b, y) in ((tx0, tx1, 14), (tx0 + 3, tx1 - 3, 9), (tx0 + 6, tx1 - 6, 5)):
        hl(d, a, b, y, CREAM_HI)
        vl(d, b, y, y + 4, CREAM_S)
    vl(d, cx, 0, 4, (120, 120, 128))                               # 旗杆
    for fx in (tx0 + 3, cx, tx1 - 3):                               # 三道竖鳍（凸出来：左亮右影）
        rect(d, fx - 1, 16, fx, 84, CREAM_HI)
        vl(d, fx + 1, 16, 84, CREAM_S)
        vl(d, fx + 2, 18, 84, dk(CREAM, 0.88))
    for xx in (tx0 + 1, tx0 + 2, cx - 3, cx - 2, cx + 3, cx + 4, tx1 - 1):      # 竖鳍之间的薄荷绿面板
        vl(d, xx, 20, 82, MINT)
    rect(d, cx - 6, 24, cx - 3, 30, TEAL)                          # 塔上的圆窗
    rect(d, cx + 4, 24, cx + 7, 30, TEAL)
    # 两边的钢窗 + 遮阳檐
    for (wx0, wx1) in ((x0 + 5, tx0 - 4), (tx1 + 5, xr - 4)):
        for y in range(56, 77):
            for x in range(wx0, wx1 + 1):
                c = (128, 158, 178) if (x - wx0) % 4 and (y - 56) % 4 else (60, 72, 78)
                px(d, x, y, c)
        d.line((wx0 + 2, 74, wx0 + 8, 58), fill=C((180, 206, 222)))
        d.line((wx1 - 6, 74, wx1 - 2, 66), fill=C((170, 196, 214)))
        for x in range(wx0, wx1 + 1):                               # 窗洞上沿的影
            px(d, x, 56, dk(px_get(im, x, 56), 0.75))
        rect(d, wx0 - 2, 51, wx1 + 2, 52, CREAM_HI)                 # 遮阳檐
        hl(d, wx0 - 2, wx1 + 2, 53, (120, 116, 108))
        hl(d, wx0 - 1, wx1 + 3, 54, dk(CREAM, 0.82))
        hl(d, wx0, wx1 + 3, 55, dk(CREAM, 0.9))
        rect(d, wx0 - 1, 77, wx1 + 1, 78, CREAM_HI)                 # 窗台
        hl(d, wx0 - 1, wx1 + 1, 79, CREAM_S)
        for y in (82, 84):                                          # 流线横纹
            hl(d, wx0 - 2, wx1 + 2, y, CREAM_S)
    # 一楼雨篷（混凝土薄檐，底下一道影）
    rect(d, x0, 87, xr, 89, CREAM_HI)
    hl(d, x0, xr, 89, CREAM_S)
    hl(d, x0, xr, 90, (110, 106, 100))
    hl(d, x0, xr, 91, dk(CREAM, 0.76))
    hl(d, x0, xr, 92, dk(CREAM, 0.86))
    for x in range(x0, x1, 2):
        px(d, x, 93, dk(CREAM, 0.92))
    # 左边：凹进去的玻璃门 + 门楣招牌 + 小飞机图标
    ex0, ex1 = x0 + 6, x0 + 28
    rect(d, ex0, 96, ex1, STEP_Y - 1, (150, 140, 124))
    shade = A._new(ex1 - ex0 + 1, STEP_Y - 96)
    sd = ImageDraw.Draw(shade)
    rect(sd, 0, 0, shade.width - 1, shade.height - 1, (196, 186, 166))
    rect(sd, 2, 0, shade.width - 3, 5, TEAL)                       # 招牌（色块 + 飞机）
    for xx in range(4, shade.width - 10, 3):
        px(sd, xx, 2, (240, 220, 140))
        px(sd, xx, 3, (240, 220, 140))
    ax = shade.width - 7
    hl(sd, ax, ax + 4, 2, (250, 250, 250))
    px(sd, ax + 2, 1, (250, 250, 250))
    px(sd, ax + 2, 3, (250, 250, 250))
    px(sd, ax, 1, (250, 250, 250))
    rect(sd, 3, 8, shade.width - 4, shade.height - 1, (70, 64, 60))  # 门框
    rect(sd, 4, 9, shade.width // 2 - 1, shade.height - 1, (96, 120, 140))
    rect(sd, shade.width // 2 + 1, 9, shade.width - 5, shade.height - 1, (96, 120, 140))
    sd.line((6, 40, 10, 14), fill=C((170, 196, 214)))
    sd.line((shade.width // 2 + 3, 44, shade.width // 2 + 7, 20), fill=C((150, 178, 200)))
    for xx in (shade.width // 2 - 3, shade.width // 2 + 2):         # 门把
        vl(sd, xx, 28, 32, (220, 190, 110))
    rect(sd, 5, 24, shade.width // 2 - 2, 32, (236, 232, 220))     # 玻璃门上贴的航线图（色块）
    for k in range(3):
        px(sd, 7 + k * 2, 27 + k, (200, 60, 50))
    shade_interior(shade, top_k=0.62, bot_k=0.8)
    im.alpha_composite(shade, (ex0, 96))
    d = ImageDraw.Draw(im)
    vl(d, ex0 - 1, 94, STEP_Y - 1, CREAM_HI)
    vl(d, ex1 + 1, 94, STEP_Y - 1, CREAM_S)
    # 右边：平墙 + 鱼尾狮海报 + 墙裙瓷砖
    rect(d, ex1 + 2, 138, xr, STEP_Y - 1, TEAL)
    hl(d, ex1 + 2, xr, 138, MINT)
    for x in range(ex1 + 2, x1, 3):
        vl(d, x, 139, STEP_Y - 1, dk(TEAL, 0.8))
    draw_poster(im, POSTER)
    d = ImageDraw.Draw(im)
    rect(d, POSTER[2] + 3, 112, POSTER[2] + 6, 126, (226, 220, 200))  # 旁边一张小告示（褪色）
    for yy in range(114, 125, 2):
        hl(d, POSTER[2] + 4, POSTER[2] + 5, yy, (170, 160, 140))
    draw_arcade_floor_plain(im, x0, x1)
    # 两边的竖向线脚（楼的边）
    for (xx, c) in ((x0, CREAM_HI), (x0 + 1, CREAM), (xr, CREAM_S)):
        vl(d, xx, 28, STEP_Y - 1, c)


def px_get(im, x, y):
    return im.getpixel((x, y))[:3]


def draw_arcade_floor_plain(im, x0, x1):
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, STEP_Y, GRANITE)
    hl(d, x0, x1 - 1, STEP_Y + 1, GRANITE_F)


# ============================================================ 近景：酒店
HW, HW_S, HW_D, HW_HI = (242, 240, 230), (212, 210, 204), (182, 184, 192), (252, 252, 246)
H_SHUT = (52, 98, 76)
H_GREEN = (36, 84, 66)
H_GOLD = (222, 186, 98)
HOTEL_ARCH = [(520, 535), (542, 557), (564, 579), (644, 659), (666, 681), (688, 703)]
HOTEL_WIN = [528, 548, 568, 648, 668, 688]      # 二、三楼窗（8 宽）；以 611.5 左右对称
PORTICO = (586, 637)
COLS = [(588, 591), (596, 599), (624, 627), (632, 635)]
POTS = [578, 645]


def hotel_mirror(x0, x1):
    return 1223 - x1, 1223 - x0


def draw_hotel(im):
    """白色殖民式三层酒店（以 x 611.5 左右对称）：红瓦四坡顶 + 两个老虎窗、山花 + 徽章、三层檐口；
    二三楼绿百叶长窗；一楼拱形外廊（藤椅、蕨类、吊灯、吊扇）；正中门廊：四根柱子、檐部名牌（金色字块）、
    顶上阳台栏杆，里面是玻璃大门 + 扇形气窗 + 两盏壁灯；门口三级台阶、两盆棕榈（叶子在 strip 里）。"""
    x0, x1 = HOTEL
    xr = x1 - 1
    d = ImageDraw.Draw(im)
    rect(d, x0, 14, xr, STEP_Y - 1, HW)
    mottle(im, (x0, 14, xr, STEP_Y - 1), HW, mix(HW, HW_S, 0.5), HW_HI, 171, cell=5, lo=0.25, hi=0.72, streaks=10)
    d = ImageDraw.Draw(im)
    # 四坡瓦顶 + 老虎窗
    d.polygon([(x0 - 2, 14), (x1 + 1, 14), (x1 - 12, 3), (x0 + 11, 3)], fill=C(ROOF))
    for x in range(x0 + 2, x1, 3):
        d.line((x, 13, x + (HC - x) * 0.06, 4), fill=C(ROOF_D))
    for y in (6, 9, 12):
        hl(d, x0 + 4, x1 - 5, y, mix(ROOF, ROOF_HI, 0.6))
    hl(d, x0 + 11, x1 - 12, 3, ROOF_K)
    d.line((x0 - 2, 14, x0 + 11, 3), fill=C(ROOF_HI))
    d.line((x1 + 1, 14, x1 - 12, 3), fill=C(ROOF_K))
    for dxm in (556, 662):
        rect(d, dxm - 4, 7, dxm + 4, 13, HW)
        d.polygon([(dxm - 6, 7), (dxm + 6, 7), (dxm, 2)], fill=C(ROOF))
        d.line((dxm - 6, 7, dxm, 2), fill=C(ROOF_HI))
        rect(d, dxm - 2, 8, dxm + 2, 13, DARK_IN)
        vl(d, dxm, 8, 13, HW_S)
    # 主檐口（齿饰）+ 影
    rect(d, x0 - 2, 14, x1 + 1, 17, HW_HI)
    hl(d, x0 - 2, x1 + 1, 16, HW_S)
    for x in range(x0 - 1, x1 + 1, 3):
        px(d, x, 17, HW_D)
    hl(d, x0, xr, 18, dk(HW, 0.78))
    hl(d, x0, xr, 19, dk(HW, 0.9))
    # 层间腰线（50–53）+ 二楼檐口（88–93）
    rect(d, x0 - 1, 50, x1, 52, HW_HI)
    hl(d, x0 - 1, x1, 53, HW_S)
    hl(d, x0, xr, 54, dk(HW, 0.86))
    rect(d, x0 - 1, 89, x1, 92, HW_HI)
    hl(d, x0 - 1, x1, 92, HW_S)
    hl(d, x0, xr, 93, dk(HW, 0.8))
    # 两端的隅石（角上的石块）+ 中间凸出那一跨的壁柱
    for xx, side in ((x0, 0), (xr - 3, 1)):
        for y in range(20, STEP_Y - 1, 6):
            w = 4 if (y // 6) % 2 else 2
            xa = xx if side == 0 else xx + 4 - w
            rect(d, xa, y, xa + w - 1, y + 4, HW_HI if side == 0 else HW_S)
            hl(d, xa, xa + w - 1, y + 5, HW_S if side == 0 else HW_D)
    for (pa, pb) in ((PORTICO[0], PORTICO[0] + 3), (PORTICO[1] - 3, PORTICO[1])):
        rect(d, pa, 18, pb, 88, HW_HI)
        vl(d, pb, 18, 88, HW_S)
        vl(d, pb + 1, 20, 88, dk(HW, 0.9))
    # 窗：三楼拱窗、二楼长窗（绿百叶）
    s = dict(trim=HW_HI, shutter=H_SHUT, sh=HW_S)
    for i, wx in enumerate(HOTEL_WIN):
        draw_window(im, wx, 24, 45, 8, s, 'arch', open_leaf='r' if i == 4 else None)
        draw_window(im, wx, 60, 84, 8, s, 'transom', open_leaf='l' if i == 1 else None)
        d = ImageDraw.Draw(im)
        hl(d, wx - 2, wx + 9, 58, HW_HI)                           # 窗楣
        hl(d, wx - 1, wx + 10, 59, HW_S)
    for wx in (598, 621):                                           # 中间那一跨：两扇窄拱窗 + 圆窗
        draw_window(im, wx, 26, 45, 5, s, 'arch')
    d = ImageDraw.Draw(im)
    d.ellipse((HC - 4, 27, HC + 4, 35), fill=C(HW_HI))
    d.ellipse((HC - 3, 28, HC + 3, 34), fill=C(GLASS))
    hl(d, HC - 3, HC + 3, 31, HW_HI)
    vl(d, HC, 28, 34, HW_HI)
    draw_window(im, 603, 62, 88, 18, s, 'fan')                      # 通向阳台的落地长窗
    d = ImageDraw.Draw(im)
    # 山花（三角楣）+ 徽章
    d.polygon([(PORTICO[0] + 2, 18), (PORTICO[1] - 2, 18), (HC, 4)], fill=C(HW_HI))
    d.line([(PORTICO[0] + 2, 18), (HC, 4), (PORTICO[1] - 2, 18)], fill=C(HW_S))
    d.line([(PORTICO[0] + 5, 17), (HC, 6)], fill=C((255, 255, 252)))
    hl(d, PORTICO[0] + 2, PORTICO[1] - 2, 18, HW_S)
    d.ellipse((HC - 5, 9, HC + 5, 16), fill=C(H_GREEN))
    d.ellipse((HC - 3, 10, HC + 3, 15), fill=C(H_GOLD))
    px(d, HC, 12, H_GREEN)
    px(d, HC - 1, 13, H_GREEN)
    px(d, HC + 1, 13, H_GREEN)
    # 一楼外廊：圆拱开口 + 里面（阴影里的藤椅、蕨类、吊灯）
    for (a, b) in HOTEL_ARCH:
        w = b - a + 1
        ins = A._new(w, FLOOR_Y - ARC_Y)
        sd = ImageDraw.Draw(ins)
        rect(sd, 0, 0, w - 1, ins.height - 1, (226, 220, 204))
        rect(sd, 3, 12, w - 4, ins.height - 1, (66, 104, 84))       # 里面的绿百叶门
        for yy in range(13, ins.height, 2):
            hl(sd, 4, w - 5, yy, (50, 84, 66))
        vl(sd, w // 2, 12, ins.height - 1, (40, 70, 56))
        rect(sd, 1, 31, 6, 41, (196, 160, 104))                     # 藤椅
        hl(sd, 1, 6, 35, (220, 186, 128))
        for yy in range(31, 35):
            px(sd, 1, yy, (176, 140, 88))
        vl(sd, 1, 41, 45, (150, 116, 70))
        vl(sd, 6, 41, 45, (150, 116, 70))
        rect(sd, w - 7, 38, w - 3, 45, (176, 96, 64))               # 蕨类盆栽
        sd.ellipse((w - 10, 28, w - 1, 39), fill=C((70, 140, 80)))
        sd.point((w - 7, 30), fill=C((120, 180, 100)))
        if (a, b) not in ((542, 557), (666, 681)):
            vl(sd, w // 2, 0, 6, (90, 80, 70))                       # 吊灯
            sd.ellipse((w // 2 - 2, 7, w // 2 + 2, 11), fill=C((250, 240, 210)))
        shade_interior(ins, top_k=0.55, bot_k=0.76)
        a_ = np.array(ins)
        r = (w - 1) / 2
        for yy in range(int(r) + 1):
            for xx in range(w):
                if (xx - r) ** 2 + (yy - r) ** 2 > (r + 0.3) ** 2:
                    a_[yy, xx, 3] = 0
        oy = ARC_Y + 4
        a_ = a_[: FLOOR_Y - oy]
        im.alpha_composite(Image.fromarray(a_, 'RGBA'), (a, oy))
        d = ImageDraw.Draw(im)
        for ang in range(180, 361, 4):
            rad = math.radians(ang)
            px(d, round(a + r + math.cos(rad) * (r + 1)), round(oy + r + math.sin(rad) * (r + 1)), HW_HI)
        rect(d, round(a + r) - 1, oy - 3, round(a + r) + 1, oy - 1, HW_HI)   # 拱心石
        draw_arcade_floor(im, a, b + 1)
        mul_box(im, (a, FLOOR_Y, b, STEP_Y - 1), (0.72, 0.74, 0.82))
    for (a, b) in ((516, 519), (536, 541), (558, 563), (580, 585), (638, 643), (660, 665), (682, 687), (704, 707)):
        d = ImageDraw.Draw(im)
        vl(d, a, ARC_Y, STEP_Y - 1, HW_HI)
        vl(d, b, ARC_Y + 6, STEP_Y - 1, HW_S)
        rect(d, a, 136, b, STEP_Y - 1, HW_S)
        hl(d, a, b, 136, HW_HI)
    # 门廊后面的入口墙（在门廊的影里）：玻璃大门 + 扇形气窗 + 侧窗 + 壁灯
    ew = A._new(PORTICO[1] - PORTICO[0] - 3, FLOOR_Y + 2 - ARC_Y)
    ed = ImageDraw.Draw(ew)
    ox = PORTICO[0] + 2
    rect(ed, 0, 0, ew.width - 1, ew.height - 1, (232, 228, 216))
    dx0, dx1 = 603 - ox, 620 - ox
    r = (dx1 - dx0) / 2
    for yy in range(9, 18):                                         # 扇形气窗
        for xx in range(dx0, dx1 + 1):
            if (xx - dx0 - r) ** 2 + (yy - 17) ** 2 <= r * r:
                ang = math.degrees(math.atan2(17 - yy, xx - dx0 - r))
                c = (130, 156, 176) if abs(((ang + 180) % 22.5) - 11) < 8 else (226, 200, 120)
                ed.point((xx, yy), fill=C(c))
    rect(ed, dx0 - 1, 18, dx1 + 1, ew.height - 1, (150, 120, 70))  # 黄铜门框
    for (a, b) in ((dx0, dx0 + 7), (dx1 - 7, dx1)):
        rect(ed, a, 19, b, ew.height - 1, (70, 92, 112))
        rect(ed, a + 1, 20, b - 1, ew.height - 2, (96, 124, 148))
        ed.line((a + 2, ew.height - 6, a + 5, 24), fill=C((176, 200, 218)))
        vl(ed, b - 1 if a == dx0 else a + 1, 30, 36, (230, 200, 110))
    for sx in (dx0 - 6, dx1 + 3):                                   # 侧窗
        rect(ed, sx, 20, sx + 3, 40, (96, 124, 148))
        rect(ed, sx - 1, 19, sx + 4, 19, (150, 120, 70))
    for sx in (dx0 - 9, dx1 + 8):                                   # 壁灯
        vl(ed, sx, 18, 20, (150, 120, 70))
        rect(ed, sx - 1, 14, sx + 1, 17, (250, 234, 180))
        px(ed, sx, 13, (150, 120, 70))
    rect(ed, 0, ew.height - 3, ew.width - 1, ew.height - 1, (190, 180, 160))  # 门口地面
    shade_interior(ew, top_k=0.6, bot_k=0.8)
    im.alpha_composite(ew, (ox, ARC_Y))
    d = ImageDraw.Draw(im)
    # 门廊：檐部（名牌）+ 阳台栏杆 + 四根柱子
    rect(d, PORTICO[0] - 1, 78, PORTICO[1] + 1, 79, HW_HI)          # 栏杆扶手
    hl(d, PORTICO[0] - 1, PORTICO[1] + 1, 80, HW_S)
    for x in range(PORTICO[0] + 1, PORTICO[1], 3):
        rect(d, x, 81, x + 1, 86, HW_HI)
        px(d, x + 1, 83, HW_S)
        px(d, x, 84, HW_S)
    for x in (PORTICO[0], HC - 1, HC, PORTICO[1]):
        rect(d, x - 1, 78, x + 1, 87, HW_HI)
    rect(d, PORTICO[0] - 2, 87, PORTICO[1] + 2, 89, HW_HI)          # 檐口
    hl(d, PORTICO[0] - 2, PORTICO[1] + 2, 89, HW_S)
    rect(d, PORTICO[0], 90, PORTICO[1], 96, HW)                    # 檐壁 + 名牌
    rect(d, PORTICO[0] + 7, 91, PORTICO[1] - 7, 95, H_GREEN)
    hl(d, PORTICO[0] + 7, PORTICO[1] - 7, 91, (70, 120, 96))
    for x in range(PORTICO[0] + 10, PORTICO[1] - 9, 4):
        rect(d, x, 93, x + 2, 94, H_GOLD)
    hl(d, PORTICO[0], PORTICO[1], 97, HW_S)
    hl(d, PORTICO[0], PORTICO[1], 98, (120, 120, 126))             # 檐下一道深影
    for (a, b) in COLS:
        rect(d, a, 99, b, 139, HW_HI)
        vl(d, b, 99, 139, HW_S)
        vl(d, a + 1, 101, 137, (255, 255, 252))
        rect(d, a - 1, 97, b + 1, 98, HW_HI)                        # 柱头
        hl(d, a - 1, b + 1, 99, HW_S)
        rect(d, a - 1, 138, b + 1, 141, HW_HI)                      # 柱础
        hl(d, a - 1, b + 1, 141, HW_S)
    # 台阶（三级，越往下越宽）
    for k, (y, a, b) in enumerate(((141, 588, 635), (143, 586, 637), (STEP_Y, 584, 639))):
        rect(d, a, y, b, y, GRANITE)
        rect(d, a, y + 1, b, y + 1, GRANITE_F)
    # 两盆棕榈的盆（青花大瓷缸）+ 茎（叶子在 strip）
    for cx in POTS:
        d.polygon([(cx - 5, 137), (cx + 5, 137), (cx + 4, STEP_Y + 1), (cx - 4, STEP_Y + 1)], fill=C((236, 240, 244)))
        hl(d, cx - 6, cx + 6, 136, (250, 250, 252))
        hl(d, cx - 4, cx + 4, 140, (60, 96, 170))
        for xx in range(cx - 3, cx + 4, 2):
            px(d, xx, 142, (80, 120, 190))
        hl(d, cx - 4, cx + 4, 144, (60, 96, 170))
        vl(d, cx + 4, 137, STEP_Y, (196, 204, 216))
        for (dx, top) in ((-2, 118), (0, 114), (2, 120)):
            for y in range(top, 137):
                px(d, cx + dx + (1 if y < top + 6 and dx > 0 else 0), y, (120, 100, 64) if y % 3 else (150, 128, 84))
    # 门廊和柱子在台阶 / 人行道上的影（往右下）
    for (a, b) in COLS:
        cast_shadow(im, [(b + 1, 139), (b + 5, 139), (b + 6, STEP_Y + 1), (b + 2, STEP_Y + 1)], level=1.0, mul=SOFT_MUL)


# ============================================================ 近景：公车站
def draw_bus_stop(im):
    """80 年代的公车站：平顶雨棚（绿檐）、两根柱、后面一块穿孔铁板 + 一张广告（色块）、长椅、线路牌、
    站牌（圆牌 + 公车图标）、垃圾桶。"""
    d = ImageDraw.Draw(im)
    x0, x1 = BUS
    base = STEP_Y + 1
    # 后板（半透明感：竖条纹的穿孔铁板）+ 广告
    rect(d, x0 + 4, 118, x1 - 4, 139, (176, 186, 190))
    for x in range(x0 + 4, x1 - 3, 2):
        vl(d, x, 118, 139, (156, 166, 172))
    rect(d, x0 + 30, 120, x0 + 50, 137, (250, 246, 236))           # 广告（色块）
    rect(d, x0 + 31, 121, x0 + 49, 128, (240, 160, 60))
    d.ellipse((x0 + 34, 122, x0 + 41, 128), fill=C((250, 220, 120)))
    rect(d, x0 + 31, 130, x0 + 49, 131, (60, 90, 150))
    rect(d, x0 + 31, 133, x0 + 42, 134, (60, 90, 150))
    hl(d, x0 + 4, x1 - 4, 140, (120, 126, 132))
    # 长椅
    rect(d, x0 + 8, 133, x0 + 26, 135, (190, 140, 80))
    hl(d, x0 + 8, x0 + 26, 133, (220, 176, 110))
    for xx in (x0 + 10, x0 + 24):
        vl(d, xx, 136, base - 1, (80, 84, 92))
    rect(d, x0 + 54, 133, x1 - 8, 135, (190, 140, 80))
    hl(d, x0 + 54, x1 - 8, 133, (220, 176, 110))
    for xx in (x0 + 56, x1 - 10):
        vl(d, xx, 136, base - 1, (80, 84, 92))
    # 柱子 + 顶棚
    for xx in (x0 + 2, x1 - 3):
        rect(d, xx, 112, xx + 1, base - 1, (120, 128, 136))
        vl(d, xx, 112, base - 1, (180, 186, 194))
    rect(d, x0 - 2, 107, x1 + 2, 111, (226, 228, 224))
    hl(d, x0 - 2, x1 + 2, 107, (246, 248, 244))
    rect(d, x0 - 2, 109, x1 + 2, 111, (56, 128, 92))
    hl(d, x0 - 2, x1 + 2, 111, (36, 92, 64))
    hl(d, x0, x1, 112, (110, 114, 118))
    # 线路牌（白板 + 几行色块）
    rect(d, x1 - 12, 114, x1 - 4, 130, (246, 246, 242))
    rect(d, x1 - 12, 114, x1 - 4, 115, (56, 128, 92))
    for k, yy in enumerate(range(118, 129, 3)):
        hl(d, x1 - 10, x1 - 6, yy, ((200, 60, 50), (60, 90, 160), (70, 140, 80), (200, 150, 50))[k % 4])
    # 站牌（杆 + 圆牌 + 公车图标）
    sx = x0 - 8
    for y in range(102, base):
        px(d, sx, y, (150, 156, 164))
        px(d, sx + 1, y, (110, 116, 126))
    d.ellipse((sx - 5, 92, sx + 6, 103), fill=C((246, 246, 242)))
    d.ellipse((sx - 5, 92, sx + 6, 103), outline=C((40, 96, 170)))
    rect(d, sx - 3, 95, sx + 4, 99, (40, 96, 170))
    hl(d, sx - 2, sx + 3, 96, (200, 226, 250))
    px(d, sx - 2, 100, INK)
    px(d, sx + 3, 100, INK)
    # 垃圾桶
    bx = x1 + 6
    rect(d, bx, 136, bx + 6, base - 1, (60, 120, 90))
    hl(d, bx, bx + 6, 136, (100, 160, 120))
    rect(d, bx - 1, 134, bx + 7, 135, (40, 90, 66))
    vl(d, bx + 6, 137, base - 1, (40, 90, 66))


# ============================================================ 近景：缆车站入口
def stair_y(x):
    """石阶踏面的 y（x ≥ STAIR0[0]）：每 4 px 一级、每级 3 px。"""
    i = (x - STAIR0[0]) // STAIR_RUN
    return STAIR0[1] - STAIR_RISE * (i + 1)


def hill_y(x):
    """缆车站后面山坡（近景）的上沿。"""
    return 122 - (x - 872) * 0.95 - 5 * math.sin(x * 0.21)


def cable_y(x, k=0):
    """缆绳（两根，k = 0 / 1 下面那根）：机房出口 → 塔顶滑轮（中间略垂）→ 画面右上外。"""
    (ax, ay), (bx, by), (cx, cy) = CABLE
    if x <= bx:
        u = (x - ax) / (bx - ax)
        y = ay + (by - ay) * u + 3.0 * math.sin(math.pi * u)
    else:
        u = (x - bx) / (cx - bx)
        y = by + (cy - by) * u + 1.5 * math.sin(math.pi * u)
    return y + 2 * k


def draw_station(im):
    """缆车站：S7 右边一段矮墙 + 花池；小站房（售票窗、入口、青绿檐带）+ 上面的缆索机房（缆绳从右侧口里出来）；
    往右上爬的石阶（踏面 + 踢面、扶手、毛石挡土墙）、山坡上的灌木 / 九重葛、钢架塔、缆绳；门口一块缆车图标指示牌。"""
    d = ImageDraw.Draw(im)
    x0 = STATION[0]
    base = STEP_Y + 1
    # 山坡（最后面）：一片绿，往右上升
    for x in range(872, PW):
        top = int(round(hill_y(x)))
        vl(d, x, top, base, (70, 124, 70))
    for i in range(30):
        tx = 872 + int(hrange(0, PW - 872, i, 61))
        ty = int(hill_y(tx)) + int(hrange(-2, 10, i, 62))
        _canopy(d, tx, ty, hrange(5, 11, i, 63), hrange(4, 7, i, 64), 300 + i)
    for i in range(46):                                           # 九重葛（洋红 / 粉）
        tx = 880 + int(hrange(0, PW - 880, i, 65))
        ty = int(hill_y(tx)) + int(hrange(1, 18, i, 66))
        c = ((214, 50, 140), (236, 100, 170), (250, 160, 200))[i % 3]
        d.ellipse((tx - 1, ty - 1, tx + 1 + (i % 2), ty + 1), fill=C(c))
    # 钢架塔（两条腿往下张开、X 形斜撑、顶上横担 + 两个滑轮，灰白漆）
    pt, pb = 34, int(hill_y(PYLON_X)) + 8
    LEG, LEG_D, BR = (200, 206, 212), (120, 128, 140), (160, 168, 178)
    prev = None
    for y in range(pt, pb + 1):
        u = (y - pt) / (pb - pt)
        half = 2 + int(round(6 * u))
        px(d, PYLON_X - half, y, LEG)
        px(d, PYLON_X - half + 1, y, LEG_D)
        px(d, PYLON_X + half, y, LEG_D)
        px(d, PYLON_X + half - 1, y, LEG)
        if (y - pt) % 8 == 0:
            hl(d, PYLON_X - half, PYLON_X + half, y, BR)
            if prev is not None:
                d.line((PYLON_X - prev[1], prev[0], PYLON_X + half, y), fill=C(BR))
                d.line((PYLON_X + prev[1], prev[0], PYLON_X - half, y), fill=C(LEG_D))
            prev = (y, half)
    rect(d, PYLON_X - 9, pt - 2, PYLON_X + 9, pt, (110, 118, 130))  # 横担 + 滑轮
    hl(d, PYLON_X - 9, PYLON_X + 9, pt - 2, (220, 224, 230))
    for sx in (PYLON_X - 6, PYLON_X + 6):
        d.ellipse((sx - 2, pt - 5, sx + 2, pt - 1), fill=C((60, 66, 78)))
        px(d, sx, pt - 3, (150, 156, 166))
    px(d, PYLON_X, pt - 6, (220, 60, 50))                           # 航空障碍灯
    # 挡土墙 + 石阶
    for x in range(STAIR0[0], PW):
        ty = stair_y(x)
        for y in range(ty + 3, base + 1):                          # 毛石侧墙
            u, v = (x + (y // 5) * 3) % 7, y % 5
            c = (176, 168, 156) if u and v else (138, 132, 124)
            if hash01(x // 7, y // 5, 3) < 0.25 and u and v:
                c = (160, 154, 144)
            px(d, x, y, c)
        px(d, x, ty, GRANITE)                                       # 踏面
        px(d, x, ty + 1, (198, 194, 186))
        px(d, x, ty + 2, GRANITE_F)                                 # 踢面
    for i in range((PW - STAIR0[0]) // STAIR_RUN + 1):
        x = STAIR0[0] + i * STAIR_RUN
        ty = stair_y(x)
        vl(d, x, ty, ty + 3, GRANITE_F)
        px(d, x, ty, (236, 232, 224))
    # 扶手（绿铁管 + 立柱）
    for x in range(STAIR0[0] + 2, PW):
        y = STAIR0[1] - 12 - (x - STAIR0[0]) * STAIR_RISE / STAIR_RUN
        px(d, x, round(y), IRON_HI)
        px(d, x, round(y) + 1, IRON)
    for x in range(STAIR0[0] + 3, PW, 12):
        y = STAIR0[1] - 12 - (x - STAIR0[0]) * STAIR_RISE / STAIR_RUN
        vl(d, x, round(y), stair_y(x) - 1, IRON)
    # 矮墙 + 花池（S7 和站房之间）
    rect(d, x0, 128, x0 + 9, base - 1, (214, 206, 190))
    hl(d, x0, x0 + 9, 128, (236, 230, 216))
    vl(d, x0 + 9, 129, base - 1, (176, 168, 152))
    _canopy(d, x0 + 5, 122, 7, 6, 351)
    for k in range(5):
        px(d, x0 + 2 + k * 2, 119 + (k % 2) * 3, (236, 100, 170))
    # 缆索机房（站房上面那一截）：清水混凝土、竖向分格、顶上青绿檐 + 栏杆；右边一个大开口，
    # 看得见里面的大转轮和一个停着的车厢（缆绳从这里出去）；左边一排小方窗
    mx0, mx1 = 850, 888
    CON, CON_S, CON_HI = (196, 200, 204), (160, 166, 174), (224, 228, 230)
    rect(d, mx0, 64, mx1, 104, CON)
    mottle(im, (mx0, 64, mx1, 104), CON, (182, 188, 194), (206, 210, 214), 371, cell=3, streaks=5)
    d = ImageDraw.Draw(im)
    for x in range(mx0 + 6, mx1 - 14, 7):
        vl(d, x, 68, 104, CON_S)
    vl(d, mx0, 64, 104, CON_HI)
    vl(d, mx1, 64, 104, CON_S)
    rect(d, mx0 - 2, 58, mx1 + 2, 63, (64, 160, 158))
    hl(d, mx0 - 2, mx1 + 2, 58, (120, 200, 196))
    hl(d, mx0 - 2, mx1 + 2, 63, (40, 116, 116))
    hl(d, mx0, mx1, 64, dk(CON, 0.8))
    hl(d, mx0 - 1, mx1 + 1, 53, IRON_HI)                            # 屋顶栏杆
    for x in range(mx0 - 1, mx1 + 2, 4):
        vl(d, x, 54, 57, IRON)
    vl(d, mx0 + 6, 44, 57, (120, 124, 132))                         # 天线
    hl(d, mx0 + 4, mx0 + 8, 46, (120, 124, 132))
    for x in range(mx0 + 3, mx0 + 22, 6):                           # 小方窗
        rect(d, x, 72, x + 3, 76, (60, 72, 88))
        px(d, x, 72, (140, 160, 180))
        hl(d, x - 1, x + 4, 77, CON_HI)
    ox0, ox1, oy0, oy1 = mx1 - 16, mx1 - 1, 66, 92                  # 大开口
    rect(d, ox0, oy0, ox1, oy1, (44, 48, 58))
    d.ellipse((ox0 + 1, oy0 + 1, ox0 + 13, oy0 + 13), outline=C((110, 116, 128)))   # 大转轮
    d.ellipse((ox0 + 5, oy0 + 5, ox0 + 9, oy0 + 9), fill=C((90, 96, 108)))
    d.line((ox0 + 2, oy0 + 7, ox0 + 12, oy0 + 7), fill=C((80, 86, 98)))
    rect(d, ox0 + 3, oy1 - 9, ox0 + 11, oy1 - 2, (200, 156, 56))    # 停着的车厢（在暗处）
    rect(d, ox0 + 4, oy1 - 7, ox0 + 6, oy1 - 5, (60, 72, 90))
    rect(d, ox0 + 8, oy1 - 7, ox0 + 10, oy1 - 5, (60, 72, 90))
    vl(d, ox0 + 7, oy0 + 14, oy1 - 10, (90, 96, 108))
    vl(d, ox0 - 1, oy0, oy1, CON_HI)
    hl(d, ox0 - 1, ox1, oy1 + 1, CON_HI)
    hl(d, ox0, ox1, oy0, (30, 32, 40))
    # 站房（售票窗 + 入口 + 青绿檐带）
    sx0, sx1 = 846, 898
    rect(d, sx0, 104, sx1, base - 1, (232, 226, 212))
    mottle(im, (sx0, 104, sx1, base - 1), (232, 226, 212), (216, 208, 192), (242, 238, 228), 361, cell=4, streaks=4)
    d = ImageDraw.Draw(im)
    rect(d, sx0 - 2, 102, sx1 + 2, 109, (64, 160, 158))
    hl(d, sx0 - 2, sx1 + 2, 102, (120, 200, 196))
    hl(d, sx0 - 2, sx1 + 2, 109, (40, 116, 116))
    hl(d, sx0, sx1, 110, dk((232, 226, 212), 0.8))
    for x in range(sx0 + 3, sx1 - 2, 5):                            # 檐带上的色块（读不出来）
        rect(d, x, 104, x + 2, 106, (236, 246, 240))
    tw = A._new(18, 14)                                             # 售票窗（里面暗 + 柜台）
    td = ImageDraw.Draw(tw)
    rect(td, 0, 0, 17, 13, (70, 70, 76))
    rect(td, 2, 2, 15, 9, (130, 150, 166))
    td.line((4, 8, 8, 3), fill=C((190, 210, 224)))
    rect(td, 4, 5, 8, 9, (226, 210, 180))                           # 售票员的身影（色块）
    rect(td, 0, 10, 17, 13, (150, 110, 70))
    im.alpha_composite(tw, (sx0 + 4, 116))
    d = ImageDraw.Draw(im)
    rect(d, sx0 + 3, 130, sx0 + 22, 131, (210, 204, 190))
    hl(d, sx0 + 3, sx0 + 22, 132, (170, 162, 150))
    ent = A._new(18, base - 114)                                    # 入口（暗，看得见里面的闸口和往上的楼梯）
    ed = ImageDraw.Draw(ent)
    rect(ed, 0, 0, 17, ent.height - 1, (140, 134, 126))
    for k in range(6):
        hl(ed, 6 + k * 2, 17, 8 + k * 3, (176, 170, 160))
    rect(ed, 2, 20, 5, ent.height - 1, (200, 200, 206))             # 闸口
    hl(ed, 2, 9, 24, (200, 200, 206))
    shade_interior(ent, top_k=0.45, bot_k=0.7)
    im.alpha_composite(ent, (sx0 + 30, 114))
    d = ImageDraw.Draw(im)
    vl(d, sx0 + 29, 112, base - 1, (246, 242, 232))
    vl(d, sx0 + 48, 112, base - 1, (190, 182, 168))
    hl(d, sx0 + 29, sx0 + 48, 112, (246, 242, 232))
    hl(d, sx0, sx1, STEP_Y, GRANITE)
    hl(d, sx0, sx1, STEP_Y + 1, GRANITE_F)
    # 缆绳（在塔上面画，挂过滑轮）
    for k in (0, 1):
        for x in range(mx1 - 1, PW):
            y = cable_y(x, k)
            px(d, x, round(y), (54, 58, 70) if k == 0 else (90, 96, 108))
    # 指示牌（门口：蓝牌白边，一根斜缆绳 + 挂着的车厢图标 + 往右上的黄箭头；不写字）
    gx = 901
    for y in range(117, base):
        px(d, gx, y, (176, 180, 188))
        px(d, gx + 1, y, (120, 126, 136))
    SB, SW = (32, 86, 166), (240, 244, 248)
    rect(d, gx - 11, 98, gx + 12, 116, SB)
    rect(d, gx - 11, 98, gx + 12, 116, None, outline=SW)
    hl(d, gx - 10, gx + 11, 117, (20, 50, 100))
    d.line((gx - 9, 106, gx + 10, 100), fill=C(SW))                 # 缆绳
    hx = gx - 3
    hy = 106 - round((hx - (gx - 9)) * 6 / 19)
    vl(d, hx, hy + 1, hy + 2, SW)                                   # 吊杆
    rect(d, hx - 4, hy + 3, hx + 4, hy + 9, SW)                     # 车厢
    hl(d, hx - 5, hx + 5, hy + 3, SW)
    rect(d, hx - 3, hy + 5, hx - 1, hy + 6, SB)
    rect(d, hx + 1, hy + 5, hx + 3, hy + 6, SB)
    AR = (250, 214, 80)
    d.line((gx + 5, 113, gx + 9, 109), fill=C(AR))                  # 箭头（往右上）
    hl(d, gx + 7, gx + 9, 108, AR)
    vl(d, gx + 9, 108, 110, AR)


# ============================================================ 近景：街上的东西
def draw_lamp(im, x, base=STEP_Y + 1):
    """铸铁路灯（墨绿）：底座、细杆、一圈花饰、弯臂挂一盏灯笼形灯头。"""
    d = ImageDraw.Draw(im)
    rect(d, x - 2, base - 7, x + 2, base - 1, IRON)
    hl(d, x - 2, x + 2, base - 7, IRON_HI)
    vl(d, x - 2, base - 6, base - 1, IRON_HI)
    for y in range(66, base - 7):
        px(d, x, y, IRON_HI)
        px(d, x + 1, y, IRON)
    rect(d, x - 1, 100, x + 2, 101, IRON)
    d.arc((x - 7, 63, x + 1, 71), 270, 360, fill=C(IRON))
    d.arc((x, 63, x + 8, 71), 180, 270, fill=C(IRON))
    for lx in (x - 6, x + 7):
        rect(d, lx - 2, 69, lx + 2, 70, IRON)
        rect(d, lx - 1, 71, lx + 1, 75, (236, 230, 206))
        vl(d, lx + 1, 71, 75, (200, 192, 170))
        hl(d, lx - 2, lx + 2, 76, IRON)
    px(d, x, 62, IRON)


def draw_fruit_cart(im):
    """水果推车：木车身（绿漆框）、一个大辐条轮、支脚、往左伸的车把；车面上左边一筐醒目的红樱桃（插着价钱牌），
    然后山竹、菠萝、木瓜 / 橙子；绿白条遮阳伞，伞边挂一串香蕉，伞杆上挂着秤；车左边地上两箱榴莲。"""
    d = ImageDraw.Draw(im)
    x0, x1 = CART
    base = STEP_Y + 1
    # 榴莲箱（地上）
    for (bx, by) in ((362, base - 9), (366, base - 17)):
        rect(d, bx, by, bx + 13, by + 8, (176, 136, 86))
        for yy in range(by + 2, by + 8, 3):
            hl(d, bx, bx + 13, yy, (150, 112, 70))
        vl(d, bx + 13, by, by + 8, (130, 96, 60))
        for k in range(3):
            cx = bx + 3 + k * 4
            d.ellipse((cx - 2, by - 3, cx + 2, by + 1), fill=C((126, 140, 60)))
            for (dx, dy) in ((-1, -3), (1, -2), (-2, -1), (2, 0)):
                px(d, cx + dx, by + dy, (160, 170, 80))
    # 车身
    rect(d, x0, 125, x1, 137, (166, 122, 74))
    for y in range(127, 137, 3):
        hl(d, x0 + 1, x1 - 1, y, (146, 104, 62))
    rect(d, x0, 125, x1, 137, None, outline=(52, 110, 80))
    hl(d, x0, x1, 124, (90, 156, 110))
    hl(d, x0 + 1, x1 + 1, 138, (110, 100, 90))
    d.line((x0, 129, x0 - 12, 127), fill=C((130, 94, 60)), width=2)  # 车把
    vl(d, x0 + 4, 138, base - 1, (110, 80, 52))                    # 支脚
    wx, wy, wr = x1 - 12, 139, 7                                    # 大轮
    d.ellipse((wx - wr, wy - wr, wx + wr, wy + wr), outline=C((50, 46, 46)))
    d.ellipse((wx - wr + 1, wy - wr + 1, wx + wr - 1, wy + wr - 1), outline=C((80, 76, 74)))
    for ang in range(0, 180, 30):
        rad = math.radians(ang)
        d.line((wx - math.cos(rad) * (wr - 1), wy - math.sin(rad) * (wr - 1),
                wx + math.cos(rad) * (wr - 1), wy + math.sin(rad) * (wr - 1)), fill=C((150, 150, 156)))
    px(d, wx, wy, (60, 60, 64))
    # 车面上的水果
    # 樱桃筐（编织筐 + 堆得冒尖的红樱桃）
    cx0, cx1 = CHERRY
    rect(d, cx0, 116, cx1, 125, (196, 152, 92))
    for y in range(118, 126, 2):
        for x in range(cx0, cx1 + 1):
            if (x + y // 2) % 2 == 0:
                px(d, x, y, (170, 126, 74))
    hl(d, cx0 - 1, cx1 + 1, 117, (222, 184, 122))
    vl(d, cx1, 117, 125, (150, 110, 64))
    CH, CH_HI, CH_D, CH_K = (214, 20, 38), (255, 150, 150), (150, 8, 26), (110, 4, 20)
    berries = []
    for row in range(5):                                            # 从下往上一层层堆
        y = 115 - row * 2
        half = (cx1 - cx0) / 2 - row * 1.9
        mid = (cx0 + cx1) / 2
        x = mid - half + (row % 2)
        while x <= mid + half - 1:
            berries.append((int(x), y + int(hash01(int(x), row, 41) < 0.3)))
            x += 2.4 - 0.4 * hash01(int(x), row, 42)
    for (x, y) in berries:
        rect(d, x, y, x + 1, y + 1, CH)
        px(d, x + 1, y + 1, CH_D)
        px(d, x, y + 2, CH_K)
    for (x, y) in berries:
        px(d, x, y, CH_HI if hash01(x, y, 43) < 0.6 else (240, 70, 80))
    for k, (x, y) in enumerate(berries[-7:]):                       # 顶上几根果柄
        if k % 2 == 0:
            px(d, x + 1, y - 1, (90, 120, 50))
            px(d, x + 2, y - 2, (90, 120, 50))
    hl(d, cx0 - 1, cx1 + 1, 117, (222, 184, 122))                   # 筐沿压在樱桃前面
    hl(d, cx0 - 1, cx1 + 1, 118, (186, 142, 86))
    for x in range(cx0 + 2, cx1 - 1, 5):                            # 筐身上的竹篾横箍
        px(d, x, 121, (226, 190, 130))
    rect(d, cx1 + 1, 103, cx1 + 6, 107, (250, 250, 244))            # 价钱牌（色块），插在筐边
    hl(d, cx1 + 2, cx1 + 5, 105, (60, 60, 70))
    vl(d, cx1 + 2, 108, 116, (150, 120, 80))
    # 山竹
    for i in range(16):
        x = 402 + (i % 5) * 2 + (i // 5) % 2
        y = 123 - (i // 5) * 2
        d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=C((86, 36, 66)))
        px(d, x - 1, y - 1, (140, 80, 110))
        px(d, x, y - 2, (80, 120, 50))
    # 菠萝（立着，叶冠）
    for x in (414, 419):
        d.ellipse((x - 2, 115, x + 2, 124), fill=C((214, 160, 60)))
        for y in range(116, 124, 2):
            px(d, x - 1, y, (170, 116, 40))
            px(d, x + 1, y + 1, (170, 116, 40))
        for (dx, dy) in ((0, -1), (-1, -2), (1, -2), (-2, -3), (0, -4), (2, -3)):
            px(d, x + dx, 115 + dy, (60, 130, 70))
    # 木瓜 + 橙子
    for (x, y) in ((425, 121), (430, 122)):
        d.ellipse((x - 3, y - 2, x + 3, y + 2), fill=C((236, 150, 50)))
        hl(d, x - 2, x, y - 2, (250, 190, 100))
    for i in range(8):
        x = 426 + (i % 4) * 3
        y = 118 - (i // 4) * 2
        d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=C((240, 160, 40)))
        px(d, x - 1, y - 1, (255, 210, 120))
    hl(d, x0 + 1, x1 - 1, 125, (60, 120, 86))
    # 遮阳伞：杆 + 秤 + 伞面（绿白条）+ 香蕉
    ux, uy = UMB
    vl(d, ux, uy + 2, 124, (200, 200, 206))
    vl(d, ux + 1, uy + 2, 124, (150, 150, 158))
    vl(d, ux - 1, 104, 106, (60, 60, 60))                           # 秤
    d.ellipse((ux - 4, 106, ux + 1, 111), fill=C((236, 236, 230)))
    d.ellipse((ux - 4, 106, ux + 1, 111), outline=C((150, 40, 40)))
    px(d, ux - 2, 108, INK)
    R = 33
    for x in range(ux - R, ux + R + 1):
        u = (x - ux) / R
        top = uy + int(round(7 * u * u))
        bot = uy + 9 + int(round(2 * u * u))
        seg = int((math.asin(max(-1, min(1, u))) / math.pi + 0.5) * 8)
        c = (66, 150, 96) if seg % 2 == 0 else (244, 244, 236)
        for y in range(top, bot + 1):
            cc = c
            if y == top:
                cc = lt(c, 0.25)
            elif y > bot - 2:
                cc = dk(c, 0.8)
            if u > 0.3:
                cc = dk(cc, 0.9)
            px(d, x, y, cc)
        if (x - ux) % 6 == 3:
            px(d, x, bot + 1, c)                                    # 伞边的扇形花边
    px(d, ux, uy - 1, (200, 200, 206))
    for (bx, by) in ((ux + 26, 102),):                              # 香蕉
        vl(d, bx, by - 2, by, (110, 90, 50))
        for k in range(5):
            d.arc((bx - 4 + k, by + k, bx + 1 + k, by + 6 + k), 20, 160, fill=C((240, 210, 70)))
        px(d, bx - 1, by + 9, (90, 120, 40))
    # 影（往右下）
    cast_shadow(im, [(x1 + 1, 138), (x1 + 8, 138), (x1 + 10, base + 1), (x1 + 2, base + 1)], level=1.0, mul=SOFT_MUL)


def draw_trishaw(im):
    """三轮车（trishaw）：自行车在后、侧边车在前（深青漆、红色坐垫、折叠起来的条纹篷），车头朝左，停在人行道里沿。"""
    d = ImageDraw.Draw(im)
    x = TRISHAW_X
    base = STEP_Y + 1
    def wheel(cx, cy, r):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=C((44, 44, 50)))
        d.ellipse((cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1), outline=C((70, 70, 76)))
        for ang in range(0, 180, 36):
            rad = math.radians(ang)
            d.line((cx - math.cos(rad) * (r - 1), cy - math.sin(rad) * (r - 1),
                    cx + math.cos(rad) * (r - 1), cy + math.sin(rad) * (r - 1)), fill=C((160, 162, 170)))
        px(d, cx, cy, (190, 190, 196))
    # 自行车（后面）
    wheel(x + 6, base - 7, 6)
    wheel(x + 31, base - 7, 6)
    FR = (84, 94, 108)
    d.line((x + 6, base - 7, x + 14, base - 21), fill=C(FR))        # 前叉
    d.line((x + 14, base - 21, x + 30, base - 19), fill=C(FR))      # 横梁
    d.line((x + 31, base - 7, x + 28, base - 19), fill=C(FR))
    d.line((x + 20, base - 8, x + 28, base - 19), fill=C(FR))
    hl(d, x + 10, x + 15, base - 23, (60, 60, 66))                  # 车把
    rect(d, x + 27, base - 22, x + 31, base - 21, (50, 40, 36))     # 车座
    # 侧边车（前面）
    TEAL_, TEAL_D = (44, 112, 122), (30, 80, 90)
    d.polygon([(x + 3, base - 18), (x + 26, base - 18), (x + 27, base - 9), (x + 22, base - 6), (x + 4, base - 6),
               (x + 1, base - 12)], fill=C(TEAL_))
    hl(d, x + 3, x + 26, base - 18, (90, 160, 166))
    hl(d, x + 4, x + 22, base - 7, TEAL_D)
    hl(d, x + 6, x + 22, base - 13, (226, 200, 120))                # 金色描线
    rect(d, x + 7, base - 22, x + 19, base - 19, (176, 54, 50))     # 坐垫 + 靠背
    hl(d, x + 7, x + 19, base - 22, (210, 90, 80))
    rect(d, x + 17, base - 29, x + 20, base - 19, (176, 54, 50))
    vl(d, x + 17, base - 29, base - 20, (210, 90, 80))
    # 折叠篷：往后折起来的一整块帆布（蓝白条），篷骨架露在外面
    hood = []
    hc = (x + 30, base - 19)
    for k in range(0, 91, 6):
        a = math.radians(180 + k)
        hood.append((hc[0] + 9 * math.cos(a), hc[1] + 11 * math.sin(a)))
    hood += [hc, (hc[0] - 2, hc[1])]
    d.polygon(hood, fill=C((236, 236, 228)))
    for k in range(0, 90, 15):
        a0, a1 = math.radians(180 + k), math.radians(180 + k + 7)
        d.polygon([hc, (hc[0] + 9 * math.cos(a0), hc[1] + 11 * math.sin(a0)),
                   (hc[0] + 9 * math.cos(a1), hc[1] + 11 * math.sin(a1))], fill=C((60, 104, 170)))
    d.arc((hc[0] - 9, hc[1] - 11, hc[0] + 9, hc[1] + 11), 180, 270, fill=C((40, 64, 110)))
    wheel(x + 18, base - 6, 5)                                      # 侧边车的轮
    # 影
    cast_shadow(im, [(x + 2, base - 1), (x + 40, base - 1), (x + 42, base + 1), (x + 4, base + 1)], level=1.0, mul=SOFT_MUL)


BLINDS = [(S1[0] + 3, S1[1] - 4), (S3[0] + 3, S3[1] - 4), (S6[0] + 3, S6[1] - 4)]
PLANTS = [(S2[0] + 8, 'fern'), (S4[1] - 6, 'palm'), (S6[0] + 18, 'fern'), (DECO[0] + 32, 'pot')]


def draw_arcade_life(im):
    """五脚基口上的卷起来的竹帘（挂在檐梁下）+ 台阶上几盆花草。"""
    d = ImageDraw.Draw(im)
    for (a, b) in BLINDS:
        y0 = ARC_Y + 1
        for x in range(a, b + 1):
            for k, c in enumerate(((176, 140, 86), (214, 180, 118), (196, 160, 102), (150, 116, 70))):
                px(d, x, y0 + k, c if x % 4 else dk(c, 0.85))
        for x in (a + 6, b - 6):                                    # 两根吊绳
            vl(d, x, ARC_Y, y0 + 4, (110, 90, 60))
            px(d, x, y0 + 5, (150, 120, 80))
    for (x, kind) in PLANTS:
        y1 = STEP_Y - 1
        if kind == 'pot':
            rect(d, x - 3, y1 - 5, x + 3, y1, (186, 96, 64))
            hl(d, x - 4, x + 4, y1 - 6, (210, 120, 84))
            vl(d, x + 3, y1 - 5, y1, (150, 72, 50))
            _canopy(d, x, y1 - 10, 5, 4, 700 + x)
            for k in range(3):
                px(d, x - 2 + k * 2, y1 - 12 + (k % 2), (240, 120, 170))
        elif kind == 'fern':
            rect(d, x - 3, y1 - 4, x + 3, y1, (90, 130, 160))
            hl(d, x - 3, x + 3, y1 - 4, (130, 170, 200))
            for k in range(-5, 6, 2):
                d.line((x, y1 - 5, x + k, y1 - 9 - (3 - abs(k) // 2)), fill=C(LEAF_M))
                d.line((x, y1 - 5, x + k + 1, y1 - 7 - (3 - abs(k) // 2)), fill=C(LEAF))
        else:
            rect(d, x - 3, y1 - 5, x + 3, y1, (220, 214, 200))
            hl(d, x - 3, x + 3, y1 - 5, (240, 236, 226))
            vl(d, x, y1 - 12, y1 - 6, BARK)
            for k in (-1, 1):
                for j in range(5):
                    px(d, x + k * (j + 1), y1 - 12 + j // 2, LEAF_M if j < 3 else LEAF)
                    px(d, x + k * (j + 1), y1 - 11 + j // 2, LEAF_D)


def draw_fan_mounts(im):
    """吊扇的杆 + 电机（扇叶在 strip）。"""
    d = ImageDraw.Draw(im)
    for (fx, fy, top) in FAN_POS:
        vl(d, fx, top, fy - 2, (60, 56, 56))
        rect(d, fx - 1, fy - 1, fx + 1, fy, (96, 90, 86))
        px(d, fx - 1, fy - 1, (130, 124, 118))


def draw_laundry_poles(im):
    d = ImageDraw.Draw(im)
    for (a, b, y) in LAUNDRY:
        hl(d, a, b, y, (214, 190, 128))
        hl(d, a, b, y + 1, (168, 140, 86))
        for x in range(a + 3, b, 7):
            px(d, x, y, (190, 166, 104))                            # 竹节
        rect(d, b, y - 1, b + 1, y + 3, (60, 60, 64))               # 竿头的铁托
        vl(d, b + 1, y + 3, y + 6, (60, 60, 64))


def draw_shadows(im):
    """立在人行道 / 台阶上的东西投在右下的影（压在台阶和人行道最上面几行，很淡）。"""
    for x in (124, BUS[0] - 8, 901) + LAMPS:
        cast_shadow(im, [(x + 2, STEP_Y), (x + 6, STEP_Y), (x + 8, WALK_TOP + 2), (x + 3, WALK_TOP + 2)], level=1.0, mul=SOFT_MUL)
    cast_shadow(im, [(161, 140), (166, 140), (170, WALK_TOP + 2), (161, WALK_TOP + 2)], level=1.0, mul=SOFT_MUL)   # 岗亭
    cast_shadow(im, [(BUS[1] - 1, 140), (BUS[1] + 4, 140), (BUS[1] + 6, WALK_TOP + 2), (BUS[1], WALK_TOP + 2)],
                level=1.0, mul=SOFT_MUL)


# ============================================================ 近景：整条街
@lru_cache(maxsize=1)
def near_parts():
    """返回 (整条街, 只有海的那一张)。"""
    im = A._new(PW, H)
    draw_ground(im)
    d = ImageDraw.Draw(im)
    hl(d, PIER[0], PW - 1, STEP_Y, GRANITE)                      # 五脚基前沿的台阶（整条，楼和壁柱都站在上面）
    hl(d, PIER[0], PW - 1, STEP_Y + 1, GRANITE_F)
    sea = draw_harbour(im)
    draw_side_street(im)
    draw_police_box(im)
    draw_pier_building(im)
    for s in SHOPS:
        draw_shophouse(im, s)
    draw_deco(im)
    draw_hotel(im)
    draw_piers(im)
    draw_bus_stop(im)
    draw_station(im)
    draw_fan_mounts(im)
    draw_arcade_life(im)
    draw_laundry_poles(im)
    for x in LAMPS:
        draw_lamp(im, x)
    draw_fruit_cart(im)
    draw_trishaw(im)
    draw_palm_trunks(im)
    draw_shadows(im)
    im = A._grade(im, sat=0.96, val=1.0)
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    return Image.fromarray(a, 'RGBA'), sea


def near_img():
    return near_parts()[0]


@lru_cache(maxsize=1)
def water_mask():
    """近景里露出来的水面（画波光用）：近景的像素和“只有海”那张一样的地方。"""
    near, sea = near_parts()
    a = np.array(near).astype(np.int16)
    b = np.array(A._grade(sea, sat=0.96, val=1.0)).astype(np.int16)
    m = (np.abs(a[..., :3] - b[..., :3]).max(-1) <= 1) & (b[..., 3] > 0)
    m[:HZ + 2] = False
    return m


def shade_interior(im, top_k=0.5, bot_k=0.7, cool=(0.94, 0.97, 1.1)):
    """五脚基 / 门洞里的阴影：上暗下亮（下半截有人行道的反光），偏冷。原地改。"""
    a = np.array(im).astype(np.float32)
    h = a.shape[0]
    u = np.arange(h, dtype=np.float32)[:, None] / max(1, h - 1)
    k = top_k + (bot_k - top_k) * u ** 0.9
    mul = np.stack([k * cool[0], k * cool[1], k * cool[2]], -1)
    a[..., :3] = a[..., :3] * np.minimum(mul, 1.0)
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


# ============================================================ 会动的（strip，世界坐标，k 1）
PALMS = [  # (名字, 树冠中心, 叶长, 种子, strip 框)
    ('palm_quay', (31, 76), 20, 1, (6, 52, 58, 102)),
    ('palms_hotel', (578, 116), 13, 2, None),
    ('palms_hotel', (645, 116), 13, 3, None),
    ('palm_hill', (945, 46), 12, 4, (928, 30, 960, 66)),
]
PALM_BOXES = [('palm_quay', (6, 52, 58, 102)), ('palms_hotel', (560, 100, 664, 136)), ('palm_hill', (928, 30, 960, 66))]
SEA_BOX = (0, HZ + 1, 48, STEP_Y)
LAUNDRY_BOX = (204, 22, 512, 80)
FAN_BOX = (322, 95, 746, 108)
CAB_BOX = (936, 14, 960, 42)


def draw_palm_trunks(im):
    """棕榈 / 椰子树的树干（静止，画在近景里）：码头那棵往左弯、山坡上一棵短的。"""
    d = ImageDraw.Draw(im)
    for (x0, y0, x1, y1, bend, w) in ((43, STEP_Y + 1, 31, 78, 7, 3), (947, 64, 945, 48, 1, 2)):
        n = int(abs(y0 - y1))
        for i in range(n + 1):
            u = i / n
            x = x0 + (x1 - x0) * u - bend * math.sin(math.pi * u * 0.9)
            y = y0 + (y1 - y0) * u
            for k in range(w):
                c = BARK_HI if k == 0 else (BARK if k < w - 1 else BARK_D)
                if i % 3 == 0:
                    c = dk(c, 0.82)
                px(d, round(x) + k - w // 2, round(y), c)


def palm_crown(d, cx, cy, L, sway, seed):
    """椰子 / 棕榈树冠：十来片羽状叶从中心放射出去、往下垂；上面的叶子亮、下面的暗；中间几个椰子。
    sway −1..1：风从左边来，叶子整体往右偏、右边的叶子垂得多一点。"""
    fr = [(12, 1.0), (34, 0.95), (58, 0.85), (82, 0.75), (104, 0.8), (128, 0.9), (152, 1.0), (176, 0.95),
          (200, 0.8), (-16, 0.85), (230, 0.6), (-48, 0.6)]
    order = sorted(range(len(fr)), key=lambda i: -math.sin(math.radians(fr[i][0])))
    for i in order[::-1] if False else order:
        phi0, lk = fr[i]
        phi = math.radians(phi0 + 7 * sway + hrange(-6, 6, seed, i))
        Li = L * lk * hrange(0.85, 1.1, seed, i, 2)
        droop = 0.55 + 0.25 * (1 - math.sin(phi)) + 0.12 * sway * math.cos(phi)
        up = math.sin(phi) > 0.35
        rach = LEAF_M if up else LEAF
        leaf_c = (LEAF_HI if up else LEAF_M, LEAF if up else LEAF_D)
        n = max(4, int(Li))
        pts = []
        for k in range(n + 1):
            s = k / n
            x = cx + math.cos(phi) * Li * s
            y = cy - math.sin(phi) * Li * s + droop * Li * s * s
            pts.append((x, y))
        for k in range(1, n + 1):
            x, y = pts[k]
            s = k / n
            ll = max(1, round((1 - abs(s - 0.45) * 1.6) * L * 0.18))
            dx, dy = pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]
            nrm = math.hypot(dx, dy) or 1
            for side in (-1, 1):
                ox = -dy / nrm * side
                oy = dx / nrm * side
                if oy < 0:
                    oy = -oy * 0.5 + 0.6
                ex = x + ox * ll + dx / nrm * ll * 0.6
                ey = y + oy * ll + 0.8 * ll
                d.line((round(x), round(y), round(ex), round(ey)), fill=C(leaf_c[0] if side < 0 else leaf_c[1]))
        d.line([(round(x), round(y)) for (x, y) in pts], fill=C(rach))
    for (dx, dy) in ((-1, 1), (1, 1), (0, 2)):
        d.ellipse((cx + dx - 1, cy + dy - 1, cx + dx + 1, cy + dy + 1), fill=C((110, 120, 50)))
    px(d, cx, cy, (70, 90, 40))


def palms_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    for (name, (cx, cy), L, seed, box) in PALMS:
        sway = math.sin(math.tau * f / N_ANIM + seed * 0.9)
        palm_crown(d, cx, cy, L, sway, seed)
    return im


def sea_frame(t):
    """港口海面的波光：只在露出来的水面上（被驳船、栏杆、树干挡住的地方不画）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    wm = water_mask()
    for i in range(60):
        y = HZ + 2 + int(hash01(i, 501) ** 1.15 * (STEP_Y - HZ - 3))
        x = int(hrange(0, 48, i, 502))
        ph = (f / N_ANIM + hash01(i, 503)) % 1.0
        if ph > 0.5:
            continue
        L = 1 + int((y - HZ) / 9) + (1 if ph < 0.2 else 0)
        c = (236, 246, 252) if ph < 0.22 else (176, 214, 236)
        for xx in range(x, x + L):
            if 0 <= xx < PW and wm[y, xx]:
                px(d, xx, y, c)
    return im


CLOTHES = [  # (竿 i, x 偏移, 宽, 长, 色, 样式)
    (0, 1, 5, 7, (246, 246, 240), 'shirt'), (0, 8, 3, 9, (120, 170, 220), 'towel'), (0, 13, 5, 8, (236, 200, 90), 'shirt'),
    (1, 1, 4, 10, (220, 120, 70), 'batik'), (1, 7, 5, 7, (250, 250, 246), 'shirt'), (1, 14, 4, 9, (110, 170, 120), 'pants'),
    (2, 2, 5, 7, (230, 150, 180), 'shirt'), (2, 9, 3, 8, (246, 246, 240), 'towel'), (2, 14, 5, 10, (70, 110, 170), 'batik'),
    (2, 21, 3, 6, (240, 220, 120), 'towel'),
]


def laundry_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    for k, (pi, ox, w, h, col, sty) in enumerate(CLOTHES):
        a, b, y = LAUNDRY[pi]
        x0 = a + ox
        ph = math.tau * f / N_ANIM + k * 0.9
        for r in range(h):
            u = r / max(1, h - 1)
            dx = round(1.6 * u * math.sin(ph) + 0.4 * u)
            y_ = y + 2 + r
            for c in range(w):
                cc = col
                if sty == 'batik' and (c + r) % 3 == 0:
                    cc = dk(col, 0.72)
                if sty == 'pants' and c == w // 2 and r > 2:
                    continue
                if sty == 'shirt' and r < 2 and c in (0, w - 1) and False:
                    continue
                if c == w - 1:
                    cc = dk(cc, 0.86)
                if r == 0:
                    cc = lt(cc, 0.2)
                px(d, x0 + c + dx, y_, cc)
            if sty == 'shirt' and r == 1:                               # 袖子
                px(d, x0 - 1 + dx, y_, col)
                px(d, x0 + w + dx, y_, dk(col, 0.86))
        px(d, x0 + 1, y + 1, (200, 200, 200))                            # 夹子
    return im


def fans_frame(t):
    """吊扇：四片扇叶，侧面看是一根横条，长短随转角变（4 帧 = 转 1/4 圈）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_FAN + 1e-6)) % N_FAN
    for (fx, fy, top) in FAN_POS:
        th = (math.pi / 2) * f / N_FAN + fx * 0.01
        for k in range(4):
            a = th + k * math.pi / 2
            ex = round(fx + 6 * math.cos(a))
            front = math.sin(a) > 0
            y = fy + 1 if front else fy
            d.line((fx, y, ex, y), fill=C((150, 128, 100) if front else (96, 84, 70)))
    return im


def cabin_frame(t):
    """缆车车厢：挂在缆绳上，吊杆 + 车厢（黄色、两扇窗）轻轻前后晃。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_CAB + 1e-6)) % N_CAB
    sw = (0, 1, 0, -1)[f]
    hx, hy = CAB_X, round(cable_y(CAB_X))
    rect(d, hx - 2, hy - 1, hx + 2, hy, (60, 64, 76))                     # 滑轮架
    d.line((hx, hy + 1, hx + sw, hy + 6), fill=C((70, 74, 86)))
    cx, cy = hx + sw, hy + 7
    rect(d, cx - 5, cy, cx + 5, cy + 9, (236, 184, 62))
    hl(d, cx - 5, cx + 5, cy, (250, 214, 110))
    rect(d, cx - 6, cy - 1, cx + 6, cy - 1, (80, 84, 96))                 # 车顶
    for wx in (cx - 4, cx + 1):
        rect(d, wx, cy + 2, wx + 2, cy + 5, (70, 96, 124))
        px(d, wx, cy + 2, (170, 200, 220))
    vl(d, cx + 5, cy + 1, cy + 9, (190, 140, 40))
    hl(d, cx - 5, cx + 5, cy + 9, (170, 120, 36))
    return im


# ============================================================ 前景（人前面，k 1.3）
FG_TREES = [(6, 40, 52, 24)]     # (树干 x, 树冠中心 y, rx, ry)：地图左头（码头）那一棵
FG_LAMP = 520


@lru_cache(maxsize=1)
def fg_img():
    """近处（比人行道更靠近镜头）的两棵雨树树干 + 树冠（只占画面上沿）、一根路灯柱。坐标 = 前景世界 x − FG_X0。"""
    im = A._new(FGW, H)
    d = ImageDraw.Draw(im)
    pal = ((22, 58, 36), (34, 84, 48), (52, 112, 58), (90, 150, 76))
    for (tx, cy, rx, ry) in FG_TREES:
        X = tx - FG_X0
        for y in range(cy, H):
            w = 7 if y > cy + 30 else 6
            for k in range(w):
                c = (96, 82, 68) if k < 2 else ((76, 64, 54) if k < w - 1 else (54, 46, 40))
                if (y // 3 + k) % 5 == 0:
                    c = dk(c, 0.82)
                px(d, X - w // 2 + k, y, c)
        for (bx, by, ex_, ey) in ((X, cy + 14, X - 18, cy - 2), (X + 1, cy + 10, X + 20, cy - 4)):
            d.line((bx, by, ex_, ey), fill=C((76, 64, 54)), width=3)
        _canopy(d, X, cy - 6, rx, ry, 900 + tx, pal=pal)
        _canopy(d, X - rx * 0.6, cy - 12, rx * 0.5, ry * 0.6, 950 + tx, pal=pal)
        _canopy(d, X + rx * 0.6, cy - 10, rx * 0.5, ry * 0.6, 980 + tx, pal=pal)
    # 路灯柱（只有一根细杆 + 顶上的灯头）
    X = FG_LAMP - FG_X0
    for y in range(20, H):
        px(d, X, y, (70, 116, 92))
        px(d, X + 1, y, (40, 70, 56))
        px(d, X + 2, y, (30, 54, 44))
    for y in (120, 121, 150):
        hl(d, X - 1, X + 3, y, (40, 70, 56))
    d.arc((X - 1, 10, X + 13, 30), 180, 270, fill=C((40, 70, 56)), width=2)
    rect(d, X + 9, 10, X + 15, 11, (40, 70, 56))
    rect(d, X + 10, 12, X + 14, 17, (236, 230, 206))
    vl(d, X + 14, 12, 17, (196, 188, 168))
    hl(d, X + 9, X + 15, 18, (40, 70, 56))
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    return Image.fromarray(a, 'RGBA')


def morning_tinted(im):
    """把 tint 层（晨光色、alpha）预先罩在不透明的像素上（前景用：人物夹在背景和前景中间，前景要自己罩）。"""
    col = np.array(_hex(MORNING[0]), np.float32)
    al = int(255 * MORNING[1]) / 255.0
    a = np.array(im).astype(np.float32)
    m = a[..., 3] > 0
    a[m, :3] = a[m, :3] * (1 - al) + col * al
    return Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA')


def _hex(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


# ============================================================ 组装
@lru_cache(maxsize=1)
def build():
    near, _ = near_parts()
    fg = fg_img()
    bb = fg.getbbox()
    fg0 = fg.crop(bb)
    return dict(sky=[sky_img(False), sky_img(True)], clouds=clouds_img(), far=far_img(), mid=mid_img(), near=near,
                fg=[fg0, morning_tinted(fg0)], fg_xy=(FG_X0 + bb[0], bb[1]))


def compose(camX, t=0.5, morning=0.0, fg=True):
    """直接拼一帧（不经导出），自检 / 预览用。morning 按 JS 的公式乘 alpha。"""
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'][1 if morning > 0.5 else 0])
    o = int(math.floor(camX * CLOUD_K + t * CLOUD_VX)) % 640
    out.alpha_composite(_tile(R['clouds'], 1280).crop((o, 0, o + W, R['clouds'].height)))
    for key, k in (('far', FAR_K), ('mid', MID_K)):
        ox = math.floor(camX * k)
        out.alpha_composite(R[key].crop((ox, 0, ox + W, H)))
    bird = bird_img()
    for (y, vx, k, x0) in BIRDS:
        x = (x0 + t * vx - camX * k) % 460 - 100
        paste(out, bird, math.floor(x), y)
    out.alpha_composite(R['near'].crop((camX, 0, camX + W, H)))
    for fn in (sea_frame, palms_frame, laundry_frame, fans_frame, cabin_frame):
        out.alpha_composite(fn(t).crop((camX, 0, camX + W, H)))
    if morning:
        col = _hex(MORNING[0])
        out.alpha_composite(Image.new('RGBA', (W, H), col + (int(255 * MORNING[1] * morning),)))
    if fg:
        im = R['fg'][1 if morning > 0.5 else 0]
        fx, fy = R['fg_xy']
        paste(out, im, fx - math.floor(camX * FG_K), fy)
    return out


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    sk = [ex.img('sky%d' % i, im) for i, im in enumerate(R['sky'])]
    layers = [dict(type='pick', key='morning', values=[0, 1], images=sk, x=0, y=0, k=0)]
    cim, cy = BJ.crop_rows(R['clouds'])
    layers.append(dict(type='wrap', image=ex.img('clouds', cim), period=640, k=CLOUD_K, y=cy, vx=CLOUD_VX))
    for key, k in (('far', FAR_K), ('mid', MID_K)):
        im, y = BJ.crop_rows(R[key])
        layers.append(dict(type='pano', image=ex.img(key, im), k=k, x=0, y=y))
    bk = ex.img('bird', bird_img())
    layers.append(dict(type='clouds', span=460, clouds=[dict(image=bk, x0=float(x0), y=y, vx=vx, k=k)
                                                       for (y, vx, k, x0) in BIRDS]))
    nim, ny = BJ.crop_rows(R['near'])
    layers.append(dict(type='pano', image=ex.img('near', nim), k=1.0, x=0, y=ny))
    layers.append(ex.bake('sea', SEA_BOX, N_ANIM, FPS_ANIM, sea_frame, screen=False, k=1.0))
    for name, box in PALM_BOXES:
        layers.append(ex.bake(name, box, N_ANIM, FPS_ANIM, palms_frame, screen=False, k=1.0))
    layers.append(ex.bake('laundry', LAUNDRY_BOX, N_ANIM, FPS_ANIM, laundry_frame, screen=False, k=1.0))
    layers.append(ex.bake('fans', FAN_BOX, N_FAN, FPS_FAN, fans_frame, screen=False, k=1.0))
    layers.append(ex.bake('cabin', CAB_BOX, N_CAB, FPS_CAB, cabin_frame, screen=False, k=1.0))
    layers.append(dict(type='tint', color=MORNING[0], alpha=MORNING[1], key='morning'))
    fx, fy = R['fg_xy']
    fk = [ex.img('fg%d' % i, im) for i, im in enumerate(R['fg'])]
    fg = [dict(type='pick', key='morning', values=[0, 1], images=fk, x=fx, y=fy, k=FG_K)]
    anchors = dict(ANCHORS)
    anchors.update(merlion_box=[POSTER[0], POSTER[1], POSTER[2], POSTER[3]],
                   cherry_box=[CHERRY[0] - 1, 104, CHERRY[1] + 2, 126],
                   hotel_box=[HOTEL[0], 2, HOTEL[1], STEP_Y + 2],
                   hotel_doors=[603, 112, 621, 144],
                   pier_arch=[69, 62, 98, STEP_Y],
                   trishaw=[TRISHAW_X + 20, 150],
                   bus_stop=[BUS[0], 107, BUS[1], STEP_Y + 1],
                   station_sign=[901, 108],
                   cable_cabin=[CAB_X, round(cable_y(CAB_X)) + 12],
                   stairs=dict(x0=STAIR0[0], y0=STAIR0[1], run=STAIR_RUN, rise=STAIR_RISE),
                   horizon=HZ, arcade_step=STEP_Y)
    st = ex.stage(PW, GROUND, WALK, layers, fg, anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


STRIPS = [('sea', SEA_BOX, N_ANIM, FPS_ANIM, sea_frame)] + \
         [(n, b, N_ANIM, FPS_ANIM, palms_frame) for (n, b) in PALM_BOXES] + \
         [('laundry', LAUNDRY_BOX, N_ANIM, FPS_ANIM, laundry_frame), ('fans', FAN_BOX, N_FAN, FPS_FAN, fans_frame),
          ('cabin', CAB_BOX, N_CAB, FPS_CAB, cabin_frame)]


def _lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def _checks(ex, BJ, st, R):
    imgs = ex.images
    cams = list(range(0, PW - W + 1, 80))
    # 1 各镜头整屏不露黑
    bad = 0
    for camX in cams:
        for t in (0.0, 0.75, 1.5):
            for m in (0, 1):
                im = np.array(BJ.ref_render(st, imgs, camX, t, dict(morning=m)).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('新加坡街 镜头 0–640（每 80）× 3 个时刻 × 晨光开关 整屏都有画（没有露黑）', bad)
    ex.checked('天空底图（下午 / 清晨两张）整张不透明', int(sum((np.array(im)[..., 3] != 255).sum() for im in R['sky'])))
    a = np.array(R['near'])
    ex.checked('近景 人行道 / 路缘 / 马路（y 146–180）整条不透明', int((a[STEP_Y:, :, 3] != 255).sum()))
    ex.checked('近景只有 0 / 255 两种透明度', int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum()))
    ex.checked('前景只有 0 / 255 两种透明度', int(sum(((np.array(f)[..., 3] > 0) & (np.array(f)[..., 3] < 255)).sum()
                                               for f in R['fg'])))
    # 2 strip 闭合 + 帧条宽
    for (name, box, n, fps, fn) in STRIPS:
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
    # 3 锚点在地图里；站人的锚点在可走带 / walk_x 里
    out = 0
    wx = ANCHORS['walk_x']
    for k, v in ANCHORS.items():
        if k == 'walk_x':
            out += not (0 <= v[0] < v[1] <= PW)
        else:
            out += not (0 <= v[0] <= PW and 0 <= v[1] <= H)
            if k in ('arrive', 'police', 'merlion_poster', 'cherry_stall', 'vendor', 'hotel_door', 'doorman', 'tourist',
                     'cable_station'):
                out += not (WALK[0] <= v[1] <= WALK[1] and wx[0] <= v[0] <= wx[1])
    for k in ('merlion_box', 'cherry_box', 'hotel_box', 'hotel_doors', 'pier_arch', 'bus_stop'):
        b = st['anchors'][k]
        out += not (0 <= b[0] < b[2] <= PW and 0 <= b[1] < b[3] <= H)
    ex.checked('锚点都在地图里、站人的锚点在可走带 / walk_x 里（不满足的条数）', out)
    # 海报框里确实是海报（颜色多、和墙不同）；樱桃筐里红的够多
    pb = np.array(R['near'].crop(POSTER))[..., :3].reshape(-1, 3)
    ncol = len({tuple(c) for c in pb})
    ex.checked('鱼尾狮海报框里颜色 ≥ 12 种（= %d）' % ncol, 0 if ncol >= 12 else 1)
    cb = np.array(R['near'].crop(st['anchors']['cherry_box'])).astype(int)
    red = int(((cb[..., 0] > 120) & (cb[..., 0] > 2.5 * cb[..., 1]) & (cb[..., 0] > 2 * cb[..., 2])).sum())
    ex.checked('樱桃筐里红色像素（R > 120、R > 2.5G、R > 2B）≥ 60（= %d）' % red, 0 if red >= 60 else 1)
    # 酒店比两边的骑楼高
    top_of = lambda x0, x1: int(min(np.nonzero(a[:, x, 3] > 0)[0].min() for x in range(x0 + 8, x1 - 8)))  # noqa: E731
    ex.checked('酒店顶（y %d）比两边骑楼（y %d / %d）高' % (top_of(*HOTEL), top_of(*S4), top_of(*S6)),
               0 if top_of(*HOTEL) + 20 < min(top_of(*S4), top_of(*S6)) else 1)
    # 4 晨光 tint：每个像素都变了、整体更冷（B − R 变大）、更淡（亮度方差变小）；前景两张 = 原图 + 同一层晨光
    dch, cool, flat = 0, 0, 0
    for camX in (0, 320, 640):
        g0 = np.asarray(BJ.ref_render(st, imgs, camX, 0.5, dict(morning=0), fg=False).convert('RGB'), np.float32)
        g1 = np.asarray(BJ.ref_render(st, imgs, camX, 0.5, dict(morning=1), fg=False).convert('RGB'), np.float32)
        dch += int((np.abs(g0 - g1).max(-1) == 0).sum())
        cool += int(((g1[..., 2] - g1[..., 0]).mean() <= (g0[..., 2] - g0[..., 0]).mean()))
        flat += int(_lum(g1).std() >= _lum(g0).std())
    ex.checked('晨光 morning=1：每个像素都变了（没变的像素）', dch)
    ex.checked('晨光 morning=1：更冷（B−R 没变大的镜头数）', cool)
    ex.checked('晨光 morning=1：更淡（亮度方差没变小的镜头数）', flat)
    ex.checked('前景 pick 两张尺寸一致', 0 if R['fg'][0].size == R['fg'][1].size else 1)
    ex.checked('前景 morning 那张 = 原图罩同一层晨光（逐像素）', BJ.ndiff_rgba(R['fg'][1], morning_tinted(R['fg'][0])))
    # 5 导出 vs 直接拼（含前景；鸟用 clouds 层同一公式）
    for camX in (0, 160, 320, 480, 640):
        for t in (0.0, 1.25):
            for m in (0, 1):
                got = BJ.ref_render(st, imgs, camX, t, dict(morning=m))
                ex.checked('新加坡街 camX=%d t=%.2f morning=%d 导出 vs 直接拼' % (camX, t, m), BJ.ndiff(got, compose(camX, t, m)))
    # 6 可走带后面的对比度（人行道 y 150–176 / 五脚基 y 110–145）
    nm = _lum(np.array(R['near'])[..., :3].astype(np.float32))
    ex.note('可走带后面的亮度：人行道 y150–176 均值 %.0f 标准差 %.1f；五脚基 y110–145 均值 %.0f 标准差 %.1f' %
            (nm[150:177].mean(), nm[150:177].std(), nm[110:146, 176:836].mean(), nm[110:146, 176:836].std()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch3', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320, 480, 640):
        compose(camX, 0.5, 0).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'singapore_street_solo_%d.png' % camX))
    compose(320, 0.5, 1).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
        os.path.join(od, 'singapore_street_solo_morning.png'))
    world = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    world.alpha_composite(build()['near'])
    world.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'singapore_street_near.png'))
    print('ok')
