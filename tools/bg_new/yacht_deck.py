# -*- coding: utf-8 -*-
r"""yacht_deck —— 第2章「南海」：SPW 安排的包船（中型游艇 / 包租船）甲板，晴天上午。2026-10-10 ch2 按体验版精度重画。

改前（later_stages.yacht()）是 320 单屏的简版（一块帆、一个舱、一个救生圈）。剧情这次改成 640 宽；侧视、
甲板高度平视（同第1章侧视客舱）：远侧舷墙 + 不锈钢栏杆，后面是海和天；近侧一道低栏杆做前景。
从左（船尾）到右（船头）：
  x 0–12      船尾外的海（尾流白浪 strip）
  x 12–118    船尾甲板：远侧栏杆上 3 根钓竿（钓竿架）、挂在栏杆上的救生圈、冷藏箱、饵桶、折叠椅、钓具箱
  x 120–211   救生艇（橙色艇身、白护舷条、扶手绳）坐在艇架上，两根吊艇柱 + 滑车 + 吊索；
              帆布单独做 pick（key 'tarp'）：0 = 盖着、绑着绳子、中间鼓起一块（安妮）；1 = 掀开搭在艇尾、艇里空了
  x 213–227   救生衣箱
  x 230–252   远侧栏杆的登船口（两根门柱 + 一条链子）—— 安妮翻过去跳海的地方（anchors.overboard）
  x 262–421   上层建筑。一层船舱：爬梯（上舱顶）、灭火器、舷窗、舱门（x 300）、扶手、无线电（x 350，
              防水箱 + 话筒 + 盘绕的电线）、去驾驶室的前门（圆窗）；舱顶后半是露天平台（救生筏筒 + 栏杆）。
              二层驾驶室：侧门、三扇侧窗、斜的前窗 + 雨刷、遮阳檐、绿舷灯、探照灯；
              顶上雷达拱架：雷达（strip 转）、GPS 罩、两根 VHF 天线、汽笛、桅杆 + 横桁 + 桅顶灯 + 蓝白旗（strip 飘）
  x 421–596   前甲板：双缆桩、平的货舱盖（挂锁）、盘好的缆绳、三个绑好的木箱、锚机 + 锚链
  x 596–640   船头：甲板收窄到船头尖、船头护栏、锚架上的锚、近侧船壳
光：上午的太阳在左上（天上画着），亮面朝左 / 朝上，影子落在物体右边的甲板上。
可走带后面（y 110–176）的白漆、柚木都压了对比，人物站上去是清楚的。

图层（从后往前）：
  sky     static  320×78        天空渐变 + 太阳（固定在屏幕）
  clouds  wrap    k 0.15 vx 1   云（640 循环，往左慢慢飘）
  far     pano    k 0.35        远岛、远处的货船 / 帆船、海面底色、海平线（432 宽，镜头 0–320 都盖满）
  sea0–5  wrap    k 0.36–0.9    海面上的浪花（6 条，越近越快、视差越大；船往右开，浪往左流；stage.state.speed 可调快慢 / 停）
  glitter strip   screen        太阳下的波光（8 帧 @4 fps，2 s 闭合）
  wake    strip   k 1           船尾尾流白浪（8 帧 @4 fps）
  gulls   clouds                两只海鸥滑翔
  near    pano    k 1           整条船（640 宽）
  radar   strip   k 1           雷达转（8 帧 @4 fps = 2 s 一圈）
  flag    strip   k 1           蓝白旗飘（8 帧 @4 fps）
  rods    strip   k 1           钓竿梢随船轻轻晃 + 钓线（8 帧 @4 fps）
  tarp    pick    k 1           key 'tarp'：0 盖着（鼓起一块）/ 1 掀开（艇里空了）；两张只在帆布框里不同
  fg: rail pano   k 1           近侧低栏杆（顶管 y 168–170，每 48 px 一根立柱）
单独运行：python -B tools\bg_new\yacht_deck.py → tools\bg_new\_preview\ch2\after\yacht_deck_solo*.png
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
PW = 640                      # 地图宽
GROUND = 156
WALK = (146, 172)             # 可走纵深带（脚底 y）
FAR_K = 0.35
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 432：镜头 0–320 时远景偏移 0–112
CLOUD_K, CLOUD_VX = 0.15, 1.0
HZ = 76                       # 海平线
DY0, DY1 = 141, 177           # 甲板：远侧边（舷墙脚）/ 近侧边（护舷条上沿）
RAIL_Y = 116                  # 远侧栏杆顶管（116–117）
MID_Y = 124                   # 远侧栏杆中间那道钢索
CAP_Y = 131                   # 远侧舷墙顶的柚木压条（131–132）
BW_Y = 133                    # 远侧舷墙内侧面（133–140）
XS = 12                       # 船尾甲板边
XB = 596                      # 船头从这里开始收窄
TIP = (640, 159.5)            # 船头尖（远近两条甲板边在这里会合）
SS0, SS1 = 262, 421           # 一层船舱 x
CAB_TOP = 96                  # 船舱墙顶（以上是檐口、舱顶）
WH0, WH1 = 318, 412           # 驾驶室 x（底边）
WH_TOP = 64                   # 驾驶室墙顶
LB0, LB1 = 120, 211           # 救生艇
GATE = (230, 252)             # 登船口两根门柱
N_ANIM, FPS_ANIM = 8, 4.0     # 所有 strip：8 帧 @4 fps = 2 s 闭合
# 海面浪花：(y0, y1, k, vx)——越靠近越快、视差越大
SEA_BANDS = [(77, 84, 0.36, 0.5), (84, 94, 0.42, 1.0), (94, 106, 0.5, 2.0),
             (106, 120, 0.6, 3.5), (120, 142, 0.72, 6.0), (142, 180, 0.9, 11.0)]
GLIT_BOX = (4, 78, 92, 142)            # 波光（屏幕坐标）
WAKE_BOX = (0, 120, 12, 180)           # 尾流（世界坐标）
RADAR_BOX = (346, 14, 382, 21)
FLAG_BOX = (326, 8, 348, 25)
RODS_BOX = (0, 34, 112, 133)
C = A._c4

ANCHORS = dict(
    rods=[96, 150],            # 钓竿（调查点：波鲁纳雷夫「钓鱼？我来！」）
    lifeboat=[160, 148],       # 救生艇（玩家站这里调查帆布）
    overboard=[241, 146],      # 登船口：安妮翻过远侧栏杆跳海的地方
    cabin_door=[300, 150],     # 一层舱门
    radio=[350, 150],          # 无线电（舱壁上的防水箱，驾驶室前门旁）
    captain=[420, 152],        # 船长平时站的位置（驾驶室前）
    cigarette=[440, 160],      # 烟头（不画进背景，剧情自己画）
    hatch=[470, 152],          # 平的货舱盖
    bow=[590, 152],            # 船头
    walk_x=[16, 594],
)

# ============================================================ 调色
INK = (44, 40, 56)
WHITE_HI = (252, 252, 248)
WHITE = (240, 241, 238)
WHITE_M = (226, 229, 230)
WHITE_S = (204, 211, 220)
WHITE_D = (170, 180, 196)
NAVY = (38, 66, 126)
NAVY_D = (26, 44, 88)
BLUE = (66, 112, 180)
SS_HI = (248, 251, 253)
SS_M = (194, 203, 213)
SS_D = (126, 138, 154)
SS_K = (88, 98, 114)
TEAK_HI = (214, 168, 114)
TEAK = (196, 148, 98)
TEAK_M = (184, 137, 88)
TEAK_S = (168, 122, 77)
TEAK_SEAM = (154, 110, 70)
GLASS_D = (30, 46, 70)
GLASS = (46, 72, 104)
GLASS_HI = (120, 162, 200)
ROPE_L = (232, 216, 172)
ROPE = (208, 186, 136)
ROPE_D = (160, 136, 96)
ORANGE_HI = (246, 140, 70)
ORANGE = (230, 112, 50)
ORANGE_M = (210, 92, 40)
ORANGE_D = (172, 70, 32)
ORANGE_K = (128, 50, 26)
CANVAS_HI = (132, 162, 192)
CANVAS_L = (100, 132, 166)
CANVAS = (70, 102, 138)
CANVAS_S = (52, 78, 110)
CANVAS_D = (38, 56, 84)
WOOD_HI = (224, 190, 132)
WOOD = (204, 166, 108)
WOOD_M = (184, 144, 90)
WOOD_S = (154, 116, 70)
WOOD_D = (116, 84, 52)
SHADOW_MUL = np.array((0.72, 0.76, 0.86), np.float32)     # 影子：偏冷的乘色


# ============================================================ 小工具
def dk(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


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
        d.rectangle((x0, y0, x1, y1), fill=C(c), outline=C(outline) if outline else None)


def shade_mask(img, mask, mul=SHADOW_MUL, level=1.0):
    """把 mask（H×W bool）里不透明的像素乘暗（原地改）；level < 1 时按 Bayer 抖动只压一部分（软边）。"""
    a = np.array(img).astype(np.float32)
    m = mask & (a[..., 3] > 0)
    if level < 1.0:
        m &= A._bayer(img.width, img.height) < level
    a[m, :3] *= mul
    img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def poly_mask(size, pts):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m) > 0


def cast_shadow(img, pts, level=1.0, mul=SHADOW_MUL):
    shade_mask(img, poly_mask(img.size, pts), mul=mul, level=level)


def y_far(x):
    """远侧甲板边（舷墙脚）的 y：x ≤ XB 是 141，船头收窄时往下弯到船头尖。"""
    if x <= XB:
        return float(DY0)
    u = min(1.0, (x - XB) / (TIP[0] - XB))
    return DY0 + (TIP[1] - DY0) * u ** 1.7


def y_near(x):
    if x <= XB:
        return float(DY1)
    u = min(1.0, (x - XB) / (TIP[0] - XB))
    return DY1 + (TIP[1] - DY1) * u ** 1.7


# ============================================================ 天空 / 云 / 远景
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, HZ + 2)
    gradient(im, (0, 0, W, HZ + 2), [(62, 126, 210), (92, 156, 230), (140, 192, 242), (196, 222, 246)], bands=11)
    A._glow(im, 40, 16, 34, 30, (255, 246, 210), 60, rings=5)
    d = ImageDraw.Draw(im)
    d.ellipse((34, 10, 46, 22), fill=C((255, 248, 222)))
    d.ellipse((36, 12, 44, 20), fill=C((255, 254, 244)))
    return im


@lru_cache(maxsize=1)
def clouds_img():
    """640 循环的云：海平线上一排积云（平底），上面几朵小的；画在远岛后面。"""
    im = A._new(640, HZ - 2)
    pal = ((255, 255, 255), (238, 244, 250), (208, 224, 240), (186, 206, 230))
    for i in range(7):
        w = hrange(44, 92, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.26, 0.34, i, 2), 300 + i, pal)
        cx = (i + hrange(0.15, 0.85, i, 3)) * 640 / 7
        y = HZ - 4 - cl.height + int(hrange(-3, 2, i, 4))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    pal2 = ((255, 255, 255), (232, 240, 250), (204, 220, 240), (180, 202, 230))
    for i in range(6):
        w = hrange(18, 36, i, 11)
        cl = A._cloud_sprite(w, w * 0.32, 400 + i, pal2)
        cx = (i + hrange(0.1, 0.9, i, 12)) * 640 / 6
        y = int(hrange(14, 42, i, 13))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    return im


def _island(a, x0, x1, peaks, seed, lit, base, shade, rim, haze):
    """远岛：几座山峰叠成的轮廓；朝左的坡亮、朝右的坡暗（抖动过渡），山脚往海平线方向发灰（空气透视）。"""
    xs = np.arange(x0, x1, dtype=np.float32)
    hgt = np.zeros_like(xs)
    for (pxx, ph, pw) in peaks:
        hgt += ph * np.exp(-((xs - pxx) / pw) ** 2)
    taper = np.minimum(1.0, np.minimum(xs - x0, x1 - 1 - xs) / 6.0)
    hgt *= np.clip(taper, 0, 1)
    bay = A._bayer(a.shape[1], a.shape[0])
    for i, x in enumerate(range(x0, x1)):
        top = int(round(HZ - hgt[i]))
        if top >= HZ:
            continue
        sl = (hgt[min(i + 1, len(xs) - 1)] - hgt[max(i - 1, 0)]) * 0.5
        for y in range(top, HZ):
            v = sl + hrange(-0.25, 0.25, seed, x, y // 3)
            if v > 0.45 or (v > 0.15 and bay[y, x] < 0.5):
                c = lit
            elif v < -0.45 or (v < -0.15 and bay[y, x] < 0.5):
                c = shade
            else:
                c = base
            depth = (y - top) / max(1.0, HZ - top)
            if depth > 0.55 and bay[y, x] < (depth - 0.55) * 1.6:
                c = haze
            a[y, x, :3] = c
            a[y, x, 3] = 255
        a[top, x, :3] = rim if sl >= -0.1 else base


@lru_cache(maxsize=1)
def far_img():
    im = A._new(FARW, H)
    gradient(im, (0, HZ, FARW, H), [(126, 182, 214), (90, 156, 204), (62, 128, 186), (46, 108, 172), (36, 92, 158)],
             bands=10)
    a = np.array(im)
    # 远岛：大岛（两座峰 + 山肩）、小岛、礁石
    _island(a, 150, 266, [(176, 18, 14), (204, 24, 12), (228, 13, 16), (250, 7, 10)], 3,
            (150, 182, 194), (126, 160, 178), (106, 140, 164), (172, 198, 208), (158, 190, 206))
    _island(a, 332, 378, [(344, 7, 9), (360, 9, 8), (370, 4, 6)], 5,
            (154, 186, 198), (134, 166, 184), (116, 150, 172), (176, 202, 212), (166, 196, 210))
    _island(a, 18, 32, [(24, 4, 4), (28, 3, 3)], 7,
            (150, 180, 192), (132, 162, 180), (116, 148, 168), (170, 196, 208), (160, 190, 206))
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 大岛山脚的白色小房子 + 灯塔
    for hx in (184, 189, 196, 241):
        px(d, hx, HZ - 2, (226, 232, 230))
        px(d, hx, HZ - 1, (186, 204, 210))
    vl(d, 258, HZ - 8, HZ - 1, (232, 236, 236))
    px(d, 258, HZ - 9, (220, 90, 80))
    # 远处的货船（剧情伏笔：第2章后面那艘无人货轮）：船身 + 尾部船楼 + 烟囱 + 吊杆
    sx = 288
    hl(d, sx, sx + 17, HZ - 1, (106, 126, 148))
    hl(d, sx + 1, sx + 17, HZ - 2, (118, 138, 158))
    rect(d, sx + 13, HZ - 6, sx + 16, HZ - 3, (128, 146, 164))
    rect(d, sx + 14, HZ - 8, sx + 15, HZ - 7, (100, 118, 140))
    vl(d, sx + 5, HZ - 6, HZ - 3, (120, 138, 158))
    vl(d, sx + 9, HZ - 5, HZ - 3, (120, 138, 158))
    # 小帆船
    bx = 106
    d.polygon([(bx, HZ - 9), (bx, HZ - 2), (bx + 5, HZ - 2)], fill=C((236, 240, 242)))
    d.polygon([(bx - 1, HZ - 7), (bx - 1, HZ - 2), (bx - 4, HZ - 2)], fill=C((214, 222, 228)))
    hl(d, bx - 4, bx + 5, HZ - 1, (98, 120, 146))
    # 海平线：一道亮的雾线 + 下面一行浅色
    hl(d, 0, FARW - 1, HZ, (214, 232, 242))
    hl(d, 0, FARW - 1, HZ + 1, (168, 206, 228))
    # 静态的长涌：几条很淡的深色长条（浪花另有会流动的 wrap 层）
    for i in range(40):
        y = HZ + 3 + int(hash01(i, 21) ** 1.3 * (H - HZ - 4))
        u = (y - HZ) / (H - HZ)
        x = int(hrange(-20, FARW, i, 22))
        L = int(hrange(10, 40, i, 23) * (0.6 + u))
        col = dk(np.array(im.getpixel((min(FARW - 1, max(0, x + 2)), y))[:3]), 0.93)
        hl(d, max(0, x), min(FARW - 1, x + L), y, col)
    return im


def _sea_color(y):
    """海面底色（和 far_img 的渐变同一组色标，给浪花取色用）。"""
    stops = [(126, 182, 214), (90, 156, 204), (62, 128, 186), (46, 108, 172), (36, 92, 158)]
    u = (y - HZ) / (H - HZ) * (len(stops) - 1)
    i = min(len(stops) - 2, max(0, int(u)))
    return mix(stops[i], stops[i + 1], u - i)


@lru_cache(maxsize=8)
def sea_band_img(i):
    """第 i 条海面浪花（透明底，640 循环）：远处是短亮线，近处是“亮弧 + 下面一道暗线”的小浪。"""
    y0, y1, k, vx = SEA_BANDS[i]
    im = A._new(640, y1 - y0)
    d = ImageDraw.Draw(im)

    def seg(x, y, L, col):
        for xx in range(x, x + L):
            d.point((xx % 640, y - y0), fill=C(col))
    for y in range(y0, y1):
        u = (y - HZ) / (H - HZ)
        sea = _sea_color(y)
        lite = mix(sea, (236, 246, 252), 0.42 + 0.1 * (1 - u))
        dark = dk(sea, 0.8)
        if (y - HZ) < 3:
            n = 34
        else:
            gap = 1 + int(u * 4)
            if (y - HZ) % (gap + 1):
                continue
            n = int(30 - 14 * u)
        for j in range(n):
            x = int(hrange(0, 640, y, j, 11))
            L = max(1, int(round((1 + u * 10) * hrange(0.5, 1.25, y, j, 12))))
            if hash01(y, j, 13) < 0.72:
                seg(x, y, L, lite)
                if u > 0.25 and y + 1 < y1:
                    seg(x + 1, y + 1, max(1, L - 1), dark)
                if u > 0.5 and L > 5 and y - 1 >= y0:
                    seg(x + 2, y - 1, L - 4, mix(lite, (255, 255, 255), 0.4))
            else:
                seg(x, y, L, dark)
    return im


def glitter_frame(t):
    """太阳下的波光（屏幕坐标，太阳 x 40）：点状闪光，2 s 一周严格闭合。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    for i in range(70):
        gy = HZ + 2 + int(hash01(i, 90) ** 1.35 * 62)
        spread = 3 + (gy - HZ) * 0.62
        gx = int(round(40 + hrange(-spread, spread, i, 91)))
        ph = (f / N_ANIM + hash01(i, 92)) % 1.0
        if ph < 0.38:
            c = (255, 255, 244) if ph < 0.15 else (214, 238, 252)
            px(d, gx, gy, c)
            if ph < 0.12 and gy > HZ + 18:
                px(d, gx - 1, gy, (200, 230, 250))
                px(d, gx + 1, gy, (200, 230, 250))
                if gy > HZ + 36:
                    px(d, gx, gy - 1, (220, 240, 252))
    return im


def wake_frame(t):
    """船尾外的尾流白浪（世界坐标）：翻滚的泡沫团，8 帧一周。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    for i in range(46):
        y = int(150 + hash01(i, 61) ** 0.8 * 30)
        x = int(hrange(0, 11, i, 62))
        ph = (f / N_ANIM + hash01(i, 63)) % 1.0
        dx = -int(ph * 3)
        r = 1 + int((1 - abs(ph - 0.4) * 2) * 2 * (0.5 + (y - 150) / 30))
        if ph < 0.85:
            col = (250, 252, 252) if ph < 0.5 else (196, 226, 240)
            d.ellipse((x + dx - r, y - max(0, r - 1), x + dx + r, y + max(0, r - 1)), fill=C(col))
    for i in range(14):                                           # 远一点的尾迹（细白线）
        y = int(hrange(128, 150, i, 64))
        x = int(hrange(0, 10, i, 65))
        ph = (f / N_ANIM + hash01(i, 66)) % 1.0
        if ph < 0.6:
            hl(d, x - 2, x + 1, y, (226, 242, 250))
    a = np.array(im)
    a[:, XS:, 3] = 0
    return Image.fromarray(a, 'RGBA')


# ============================================================ 船：远侧舷墙 + 栏杆
def draw_far_bulwark(im, d, x0, x1):
    """远侧舷墙（白漆内侧面 + 柚木压条 + 排水口）。x0..x1 不含 x1。"""
    rect(d, x0, CAP_Y, x1 - 1, CAP_Y, TEAK_HI)
    rect(d, x0, CAP_Y + 1, x1 - 1, CAP_Y + 1, TEAK_S)
    rect(d, x0, BW_Y, x1 - 1, DY0 - 1, WHITE_M)
    hl(d, x0, x1 - 1, BW_Y, WHITE_S)                       # 压条下面的一道影
    hl(d, x0, x1 - 1, DY0 - 2, WHITE_S)
    hl(d, x0, x1 - 1, DY0 - 1, WHITE_D)                    # 舷墙脚的暗角
    for x in range(x0 + 30, x1 - 6, 64):                   # 排水口
        rect(d, x, DY0 - 4, x + 4, DY0 - 2, (58, 96, 140))
        hl(d, x, x + 4, DY0 - 4, NAVY_D)
        px(d, x + 4, DY0 - 2, WHITE_S)
    for x in range(x0 + 62, x1 - 6, 64):                   # 舷墙脚的小甲板灯
        rect(d, x, BW_Y + 3, x + 2, BW_Y + 4, SS_M)
        px(d, x + 1, BW_Y + 4, (255, 250, 214))


def draw_far_rail(d, x0, x1, skip=()):
    """远侧栏杆：顶管 y 116–117、中间钢索 y 124、每 24 px 一根立柱（skip 里的 x 段不画立柱）。"""
    hl(d, x0, x1, RAIL_Y, SS_HI)
    hl(d, x0, x1, RAIL_Y + 1, SS_D)
    hl(d, x0, x1, MID_Y, SS_M)
    for x in range(x0 - x0 % 24 + 20, x1, 24):
        if x < x0 + 2 or any(a <= x <= b for a, b in skip):
            continue
        vl(d, x, RAIL_Y + 2, CAP_Y - 1, SS_HI)
        vl(d, x + 1, RAIL_Y + 2, CAP_Y - 1, SS_D)
        hl(d, x - 1, x + 2, CAP_Y - 1, SS_M)
        px(d, x, RAIL_Y + 1, SS_M)


# ============================================================ 船尾：钓竿、救生圈、冷藏箱……
# 竿尾插在压条上的钓竿架里（往船尾斜），(竿尾, 竿梢, 钓线入水点)
RODS = [((81, 126), (58, 62), (3, 118)), ((93, 126), (78, 57), (6, 122)), ((105, 126), (99, 64), (9, 126))]
GRIP = (64, 62, 70)
BLANK = (34, 42, 70)
BLANK_HI = (92, 108, 150)


def _rod_pts(butt, tip, bend):
    """钓竿：从竿尾到竿梢的一条略弯的线（梢往下、往后垂一点）。bend 越大越弯。"""
    pts = []
    n = 48
    for i in range(n + 1):
        u = i / n
        x = butt[0] + (tip[0] - butt[0]) * u - bend * (u ** 2.6) * 3
        y = butt[1] + (tip[1] - butt[1]) * u + bend * (u ** 2.4) * 7
        pts.append((x, y))
    return pts


def draw_rods(d, sway=0.0):
    """3 根钓竿（EVA 握把、绕线轮、深蓝碳素竿身 + 一道高光、导线环、竿梢）+ 钓线（虚线，很淡，垂进船尾外的海里）。
    sway 0..1：竿梢往下弯的量（strip 里随船轻轻晃）。"""
    for k, (butt, tip, wet) in enumerate(RODS):
        bend = 0.6 + 0.25 * k + sway * 0.9
        pts = _rod_pts(butt, tip, bend)
        tx, ty = pts[-1]
        n = int(max(abs(wet[0] - tx), abs(wet[1] - ty))) + 1
        for s in range(0, n + 1, 2):
            u = s / n
            lx = tx + (wet[0] - tx) * u
            ly = ty + (wet[1] - ty) * u - (5 + 2 * sway) * math.sin(math.pi * u) * (1 - u)
            px(d, round(lx), round(ly), (224, 232, 238))
        N = len(pts) - 1
        for i in range(N):
            x, y = pts[i]
            x2, y2 = pts[i + 1]
            u = i / N
            if u < 0.11:
                col = GRIP
            elif u < 0.15:
                col = SS_M
            else:
                col = BLANK_HI if (i % 4 == 0 and u < 0.8) else BLANK
            d.line((round(x), round(y), round(x2), round(y2)), fill=C(col))
            if u < 0.5:                                               # 下半截粗 2 px
                d.line((round(x) + 1, round(y), round(x2) + 1, round(y2)), fill=C(dk(col, 0.8) if u >= 0.15 else col))
        for u in (0.32, 0.47, 0.6, 0.72, 0.83, 0.92):                 # 导线环
            x, y = pts[int(u * N)]
            px(d, round(x) + 1, round(y) + 1, (220, 226, 234))
        px(d, round(tx), round(ty), (250, 250, 250))                  # 竿梢
        px(d, round(pts[N - 2][0]), round(pts[N - 2][1]), (220, 60, 60))
        # 绕线轮（挂在竿下侧）：金色线杯 + 黑色轮体 + 摇把
        x, y = pts[int(0.16 * N)]
        rx, ry = round(x) + 2, round(y) + 1
        rect(d, rx, ry, rx + 3, ry + 3, (44, 44, 52))
        rect(d, rx + 1, ry, rx + 2, ry + 2, (222, 186, 82))
        px(d, rx + 1, ry, (250, 222, 140))
        px(d, rx + 4, ry + 1, (150, 154, 166))
        px(d, rx + 5, ry + 2, (40, 40, 48))


def rods_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    draw_rods(d, sway=0.5 + 0.5 * math.sin(math.tau * f / N_ANIM))
    return im


def draw_rod_holders(d):
    """压条上斜插的不锈钢钓竿架（竿在 rods strip 里）。"""
    for (butt, tip, wet) in RODS:
        bx, by = butt
        d.line((bx + 1, CAP_Y, bx - 1, by - 1), fill=C(SS_M), width=2)
        px(d, bx - 1, by - 1, SS_HI)
        px(d, bx, by, SS_HI)
        rect(d, bx, CAP_Y - 1, bx + 3, CAP_Y, SS_D)                      # 夹在压条上的卡箍
        px(d, bx + 1, CAP_Y - 1, SS_HI)


def draw_life_ring(d, cx, cy, r=7):
    """救生圈：红白四段 + 反光带 + 外圈的绳子，挂在远侧栏杆顶管上。"""
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            dd = math.hypot(xx - cx, yy - cy)
            if dd > r + 0.3 or dd < 3.2:
                continue
            ang = math.atan2(yy - cy, xx - cx)
            q = int(((ang + math.pi / 4) % math.tau) / (math.pi / 2))
            base = (222, 70, 46) if q % 2 == 0 else (244, 242, 236)
            lit = -(xx - cx) - (yy - cy)
            if lit > 3:
                base = mix(base, (255, 255, 255), 0.25)
            elif lit < -4:
                base = dk(base, 0.78)
            if dd > r - 0.7:
                base = dk(base, 0.7)
            px(d, xx, yy, base)
    for a in range(0, 360, 30):                                  # 外圈的绳
        rad = math.radians(a)
        px(d, round(cx + math.cos(rad) * (r + 0.6)), round(cy + math.sin(rad) * (r + 0.6)), ROPE)
    for a in (40, 130, 220, 310):                                # 反光带
        rad = math.radians(a)
        px(d, round(cx + math.cos(rad) * (r - 2)), round(cy + math.sin(rad) * (r - 2)), (196, 200, 206))
    rect(d, cx - 1, cy - r - 2, cx + 1, cy - r, SS_D)            # 挂钩


def draw_cooler(im, d, x0, y1):
    """冷藏箱：白箱身 + 蓝盖 + 提手 + 扣。y1 = 箱底。"""
    x1 = x0 + 20
    y0 = y1 - 15
    rect(d, x0, y0 + 3, x1, y1, WHITE)
    vl(d, x0, y0 + 3, y1, WHITE_HI)
    vl(d, x1, y0 + 3, y1, WHITE_S)
    vl(d, x1 - 1, y0 + 4, y1, WHITE_M)
    hl(d, x0, x1, y1, WHITE_D)
    rect(d, x0 - 1, y0, x1 + 1, y0 + 3, BLUE)
    hl(d, x0 - 1, x1 + 1, y0, (124, 170, 226))
    hl(d, x0 - 1, x1 + 1, y0 + 3, NAVY)
    hl(d, x0 + 4, x1 - 4, y0 - 1, SS_D)                          # 盖上的提手
    px(d, x0 + 4, y0, SS_D)
    px(d, x1 - 4, y0, SS_D)
    rect(d, x0 + 9, y0 + 4, x0 + 11, y0 + 6, SS_D)               # 扣
    px(d, x0 + 9, y0 + 4, SS_HI)
    for xx in range(x0 + 3, x1 - 2, 4):                          # 侧面的凹槽
        px(d, xx, y1 - 3, WHITE_S)
    px(d, x0 + 2, y1 - 1, (110, 116, 130))                       # 放水塞


def draw_bucket(d, x0, y1):
    rect(d, x0, y1 - 7, x0 + 7, y1, WHITE)
    vl(d, x0, y1 - 7, y1, WHITE_HI)
    vl(d, x0 + 7, y1 - 7, y1, WHITE_S)
    hl(d, x0, x0 + 7, y1 - 4, BLUE)
    hl(d, x0 + 1, x0 + 6, y1 - 7, (40, 80, 120))                # 桶里的水
    hl(d, x0 + 1, x0 + 6, y1 - 8, WHITE_M)
    d.arc((x0, y1 - 12, x0 + 7, y1 - 4), 180, 360, fill=C(SS_D))


def draw_chair(d, x0, y1):
    """折叠导演椅（柚木架 + 藏青帆布），侧面看朝右：后腿斜撑到靠背顶、前腿直立到扶手、座下交叉撑。"""
    d.line((x0 + 2, y1 - 9, x0 + 12, y1), fill=C(WOOD_S))         # 交叉撑（远的那根暗）
    d.line((x0 + 2, y1, x0 + 12, y1 - 9), fill=C(WOOD_M))
    vl(d, x0 + 12, y1 - 14, y1, WOOD)                            # 前腿
    px(d, x0 + 12, y1, WOOD_S)
    d.line((x0 + 2, y1, x0, y1 - 22), fill=C(WOOD))              # 后腿 → 靠背杆
    px(d, x0, y1 - 22, WOOD_HI)
    rect(d, x0 + 1, y1 - 21, x0 + 3, y1 - 15, NAVY)              # 靠背帆布
    vl(d, x0 + 1, y1 - 21, y1 - 15, BLUE)
    hl(d, x0 + 2, x0 + 12, y1 - 10, NAVY)                        # 坐面帆布（略往下垂）
    hl(d, x0 + 4, x0 + 10, y1 - 9, NAVY_D)
    hl(d, x0 + 2, x0 + 12, y1 - 11, BLUE)
    hl(d, x0 + 1, x0 + 13, y1 - 14, WOOD_HI)                     # 扶手
    hl(d, x0 + 1, x0 + 13, y1 - 13, WOOD_S)


def draw_landing_net(d, x, y1):
    """靠在舷墙上的抄网（铝杆 + 网兜）。"""
    d.line((x, y1, x + 6, y1 - 26), fill=C(SS_M))
    d.line((x + 1, y1, x + 7, y1 - 26), fill=C(SS_D))
    d.ellipse((x + 3, y1 - 36, x + 13, y1 - 26), outline=C((60, 64, 74)))
    for yy in range(y1 - 34, y1 - 26, 2):
        for xx in range(x + 5, x + 12, 2):
            px(d, xx + (yy // 2) % 2, yy, (120, 126, 140))


def draw_tackle_box(d, x0, y1):
    rect(d, x0, y1 - 6, x0 + 9, y1, (62, 128, 86), outline=(34, 74, 50))
    hl(d, x0 + 1, x0 + 8, y1 - 5, (106, 170, 120))
    hl(d, x0, x0 + 9, y1 - 3, (40, 92, 60))
    rect(d, x0 + 3, y1 - 8, x0 + 6, y1 - 7, (40, 92, 60))        # 提手
    px(d, x0 + 4, y1 - 3, (226, 210, 120))


def draw_lifejacket_box(d, x0, y1):
    """救生衣箱（白色甲板箱 + 橙色横条 + 盖子 + 扣）。"""
    x1, y0 = x0 + 14, y1 - 16
    rect(d, x0, y0, x1, y1, WHITE)
    rect(d, x0 - 1, y0 - 2, x1 + 1, y0, WHITE_M)
    hl(d, x0 - 1, x1 + 1, y0 - 2, WHITE_HI)
    hl(d, x0 - 1, x1 + 1, y0, WHITE_S)
    vl(d, x0, y0 + 1, y1, WHITE_HI)
    vl(d, x1, y0 + 1, y1, WHITE_S)
    rect(d, x0 + 1, y0 + 6, x1 - 1, y0 + 8, ORANGE)
    hl(d, x0 + 1, x1 - 1, y0 + 8, ORANGE_D)
    rect(d, x0 + 6, y0 + 2, x0 + 8, y0 + 3, SS_D)
    hl(d, x0, x1, y1, WHITE_D)


# ============================================================ 救生艇
def lb_sheer(x):
    """近侧船舷（护舷条上沿）的 y：船头翘、船尾略翘。"""
    u = min(1.0, max(0.0, (x - LB0) / (LB1 - LB0)))
    return 114 - 7.5 * u ** 2.6 + 1.6 * (1 - u) ** 6


def lb_hull_poly():
    top = [(x, lb_sheer(x)) for x in range(LB0 + 1, LB1 - 2)]
    bow = [(LB1 - 2, lb_sheer(LB1 - 2)), (LB1, 105.5), (LB1 - 1, 110), (LB1 - 4, 118), (LB1 - 10, 126),
           (LB1 - 18, 131), (LB1 - 28, 133)]
    keel = [(LB0 + 14, 133), (LB0 + 7, 132), (LB0 + 3, 129), (LB0 + 1, lb_sheer(LB0 + 1) + 2)]
    return top + bow + keel


DAVIT_C = (226, 230, 234)


def draw_davit(d, x, toward):
    """吊艇柱（立在远侧舷墙后面，比艇身远）：2 px 的灰白钢柱，柱头弯一点挂滑车，吊索从滑车垂到艇的吊环。
    toward = +1 柱头往右弯 / −1 往左弯。返回滑车的 x。"""
    top = 82
    vl(d, x, top + 3, CAP_Y - 1, DAVIT_C)
    vl(d, x + 1, top + 3, CAP_Y - 1, WHITE_D)
    arm = [(x, top + 3), (x, top + 1), (x + toward, top - 1), (x + 3 * toward, top - 2), (x + 5 * toward, top - 1),
           (x + 6 * toward, top + 1)]
    d.line(arm, fill=C(DAVIT_C), width=2)
    d.line(arm[1:4], fill=C(WHITE_HI))
    bx = x + 6 * toward
    rect(d, bx - 1, top + 2, bx + 1, top + 5, SS_K)              # 滑车
    px(d, bx - 1, top + 2, SS_M)
    px(d, bx, top + 6, SS_D)
    hl(d, x - 1, x + 2, CAP_Y - 1, SS_D)                         # 柱脚卡在压条上
    return bx


def tarp_top(x):
    """帆布顶的 y：中间拱起（艇里横着一根撑杆）+ x 164 那里鼓起一块（安妮缩在下面）。"""
    u = min(1.0, max(0.0, (x - LB0) / (LB1 - LB0)))
    dome = 6.0 * math.sin(math.pi * u) ** 0.55
    bulge = 6.0 * math.exp(-((x - 164) / 7.0) ** 2)
    sag = 0.0
    for (a, b) in ((134, 156), (174, 197)):                    # 帆布在吊索 / 鼓包之间往下塌一点
        if a < x < b:
            sag += 1.6 * math.sin(math.pi * (x - a) / (b - a))
    return lb_sheer(x) - 1 - dome - bulge + sag


def draw_lifeboat_base(im, d):
    """吊艇柱、艇架、艇身（不含帆布 / 艇内）。"""
    falls = [draw_davit(d, 128, +1), draw_davit(d, 203, -1)]
    for cx in (138, 184):                                       # 艇架（两块深色木托 + 橡胶垫）
        rect(d, cx - 5, 131, cx + 5, 143, (70, 82, 104))
        hl(d, cx - 5, cx + 5, 131, (30, 30, 36))
        vl(d, cx - 5, 132, 143, (96, 110, 134))
        vl(d, cx + 5, 132, 143, (52, 60, 78))
        hl(d, cx - 6, cx + 6, 143, (52, 60, 78))
    poly = lb_hull_poly()
    m = poly_mask(im.size, poly)
    a = np.array(im)
    ys, xs = np.nonzero(m)
    bay = A._bayer(im.width, im.height)
    for y, x in zip(ys, xs):
        top = lb_sheer(x)
        v = (y - top) / max(1.0, 133 - top)
        if v < 0.5:
            c = ORANGE_HI if v < 0.12 else ORANGE
        elif v < 0.78:
            c = ORANGE if bay[y, x] < (0.78 - v) * 3 else ORANGE_M
        else:
            c = ORANGE_M if bay[y, x] < (1.0 - v) * 3 else ORANGE_D
        a[y, x, :3] = c
        a[y, x, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    d.line([(LB1 - 1, 106), (LB1 - 1, 110), (LB1 - 4, 118), (LB1 - 10, 126), (LB1 - 18, 131), (LB1 - 28, 133)],
           fill=C(ORANGE_K))                                     # 船头轮廓
    hl(d, LB0 + 14, LB1 - 28, 133, ORANGE_K)
    d.line([(LB0 + 14, 133), (LB0 + 7, 132), (LB0 + 3, 129), (LB0 + 1, lb_sheer(LB0 + 1) + 2)], fill=C(ORANGE_K))
    # 白护舷条（船舷上沿 2 px）+ 下面一道影
    for x in range(LB0 + 1, LB1 - 1):
        y = int(round(lb_sheer(x)))
        px(d, x, y, (246, 244, 236))
        px(d, x, y + 1, (196, 198, 204))
        px(d, x, y + 2, ORANGE_D)
    # 扶手绳（沿船舷垂成一串弧）+ 卡子
    clips = list(range(LB0 + 8, LB1 - 10, 13))
    for xa, xb in zip(clips, clips[1:]):
        for x in range(xa, xb + 1):
            u = (x - xa) / (xb - xa)
            y = lb_sheer(x) + 6 + 3.2 * math.sin(math.pi * u)
            px(d, x, round(y), ROPE_L if (x % 2) else ROPE)
            px(d, x, round(y) + 1, ORANGE_D)
    for xa in clips:
        y = round(lb_sheer(xa) + 6)
        rect(d, xa, y - 1, xa, y, (246, 244, 236))
    # 船头的号码牌（看不清的字）+ 船尾的排水塞
    rect(d, LB1 - 22, 116, LB1 - 14, 120, (246, 244, 236))
    for xx in (LB1 - 21, LB1 - 19, LB1 - 16):
        vl(d, xx, 117, 119, (60, 70, 96))
    px(d, LB0 + 6, 128, (60, 40, 30))
    return falls


TIE_XS = [127, 139, 151, 177, 189, 201]        # 帆布下摆系到艇身挂钩的位置
STRAP_XS = [143, 186]                          # 两道跨过帆布顶的绑带


def _shade_region(im, poly, fn):
    """在多边形里逐像素上色：fn(x, y) → 颜色或 None（不改）。"""
    m = poly_mask(im.size, poly)
    a = np.array(im)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        c = fn(x, y)
        if c is not None:
            a[y, x, :3] = c
            a[y, x, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))


def draw_tarp_on(im, d, falls):
    """状态 0：帆布盖着（中间撑起成拱、x 164 鼓起一块），下摆压在护舷条上、每 12 px 系一根短绳到艇身的挂钩，
    两道绑带跨过顶；吊索从滑车穿进帆布。外轮廓一圈深色描边、顶上一道高光（和后面的海分得开）。"""
    poly = [(x, tarp_top(x)) for x in range(LB0, LB1 + 1)] + \
           [(x, lb_sheer(x) + 2.4) for x in range(LB1, LB0 - 1, -1)]
    bay = A._bayer(im.width, im.height)

    def col(x, y):
        top = tarp_top(x)
        bot = lb_sheer(x) + 2.4
        v = (y - top) / max(1.0, bot - top)
        sl = tarp_top(x + 1.5) - tarp_top(x - 1.5)          # < 0：往右升（朝左上的坡，亮）
        if y - top < 1.0:
            return CANVAS_D                                  # 轮廓
        if y - top < 2.0:
            return CANVAS_HI if sl < 0.9 else CANVAS_L
        if v < 0.4:
            if sl < -0.5:
                return CANVAS_L
            if sl > 1.2:
                return CANVAS_S
            return CANVAS_L if bay[y, x] < 0.35 else CANVAS
        if v < 0.82:
            return CANVAS if sl < 1.0 else CANVAS_S
        return CANVAS_S if bay[y, x] < 0.55 else CANVAS_D
    _shade_region(im, poly, col)
    d = ImageDraw.Draw(im)
    # 鼓起来那一块：左上亮边、右下影，两道被撑开的 V 形褶通到下摆
    for x in range(156, 173):
        y = round(tarp_top(x))
        if x <= 162:
            px(d, x, y + 1, (156, 184, 210))
        if x >= 167:
            px(d, x, y + 2, CANVAS_S)
            px(d, x, y + 3, CANVAS_D if x > 169 else CANVAS_S)
    for (xa, xb) in ((159, 153), (169, 177)):
        ya = round(tarp_top(xa)) + 3
        yb = round(lb_sheer(xb)) + 1
        d.line((xa, ya, xb, yb), fill=C(CANVAS_S))
        d.line((xa - 1, ya, xb - 1, yb), fill=C(CANVAS_L))
    # 撑杆两头被吊索顶起的小尖
    for bx in falls:
        y = round(tarp_top(bx))
        px(d, bx, y, CANVAS_D)
        px(d, bx, y + 1, CANVAS_HI)
        d.line((bx, y + 2, bx - 3, round(lb_sheer(bx - 3))), fill=C(CANVAS_S))
    # 下摆（压在护舷条上，一圈深色）+ 扣眼 + 系到挂钩的短绳
    for x in range(LB0 + 1, LB1 - 1):
        y = round(lb_sheer(x) + 2.4)
        px(d, x, y, CANVAS_D)
    for x in TIE_XS:
        y = round(lb_sheer(x) + 2.4)
        px(d, x, y - 1, (214, 218, 220))
        px(d, x, y + 1, ROPE_L)
        px(d, x + 1, y + 2, ROPE)
        px(d, x + 1, y + 3, (60, 60, 66))                       # 挂钩
    # 两道绑带跨过帆布顶（米色织带，顶上亮、往下暗）
    for x in STRAP_XS:
        y0 = round(tarp_top(x))
        y1 = round(lb_sheer(x) + 2.4)
        for y in range(y0 + 1, y1 + 1):
            v = (y - y0) / max(1, y1 - y0)
            px(d, x, y, (200, 180, 132) if v < 0.35 else ((172, 152, 108) if v < 0.8 else (140, 122, 88)))
            px(d, x + 1, y, (172, 152, 108) if v < 0.35 else (140, 122, 88))
        px(d, x, y0, CANVAS_D)
        rect(d, x, y1 + 1, x + 1, y1 + 2, SS_D)                  # 带扣
    # 吊索：从滑车垂下来，穿进帆布
    for bx in falls:
        vl(d, bx, 88, round(tarp_top(bx)) - 1, ROPE_D)
        px(d, bx, 88, ROPE)


def draw_tarp_off(im, d, falls):
    """状态 1：帆布被掀开，一大团皱着堆在艇尾、一片顺着船尾和近侧船舷垂下来；艇里空了：
    看得见远侧舷的白色内壁、三块横座板、两支桨、橙色救生衣、水壶；松开的系绳和绑带垂在船舷外。"""
    far_gw = lambda x: lb_sheer(x) - 6.0
    for x in range(LB0 + 3, LB1 - 2):
        y0, y1 = round(far_gw(x)), round(lb_sheer(x)) - 1
        for y in range(y0, y1 + 1):
            v = (y - y0) / max(1, y1 - y0)
            c = (236, 232, 220) if v < 0.3 else ((216, 212, 200) if v < 0.7 else (178, 172, 162))
            px(d, x, y, c)
        px(d, x, y0, (248, 246, 238))                             # 远侧舷的护舷条（白）
        px(d, x, y0 - 1, (150, 156, 170))
    d.polygon([(LB1 - 3, round(far_gw(LB1 - 3))), (LB1, 105), (LB1 - 1, 110), (LB1 - 4, 112)], fill=C((216, 212, 200)))
    for x in range(150, 200, 16):                                 # 内壁上的肋骨缝
        vl(d, x, round(far_gw(x)) + 2, round(lb_sheer(x)) - 2, (200, 196, 186))
    # 横座板（柚木）露出来的一截 + 两支桨 + 救生衣 + 水壶
    for (xa, xb) in ((147, 157), (170, 181), (191, 199)):
        y = round(lb_sheer((xa + xb) / 2)) - 2
        rect(d, xa, y, xb, y + 1, TEAK)
        hl(d, xa, xb, y, TEAK_HI)
    for (x0, x1, off, blade) in ((130, 198, 0, 197), (136, 202, 1, 133)):
        for x in range(x0, x1):
            yy = round(lb_sheer(x)) - 3 - off
            px(d, x, yy, WOOD_HI if x % 5 else WOOD)
        yb = round(lb_sheer(blade)) - 4 - off
        rect(d, blade - 3, yb, blade + 3, yb + 1, WOOD)
        hl(d, blade - 3, blade + 3, yb, WOOD_HI)
    yj = round(lb_sheer(186))
    rect(d, 182, yj - 5, 189, yj - 1, ORANGE)
    hl(d, 182, 189, yj - 5, ORANGE_HI)
    hl(d, 183, 188, yj - 3, (240, 224, 190))
    yw = round(lb_sheer(162))
    rect(d, 160, yw - 6, 164, yw - 1, (236, 240, 244))
    vl(d, 160, yw - 6, yw - 1, (255, 255, 255))
    rect(d, 161, yw - 7, 162, yw - 7, (56, 104, 196))
    # 近侧护舷条再压一遍（座板 / 桨在它后面）
    for x in range(LB0 + 1, LB1 - 1):
        y = int(round(lb_sheer(x)))
        px(d, x, y, (246, 244, 236))
        px(d, x, y + 1, (196, 198, 204))
    # 掀开的帆布：在艇尾堆成一团（几道横的皱褶，上亮下暗），一片从船尾板垂下去（两道竖褶），
    # 一角搭在近侧船舷外（短短一截，下沿起伏）
    bay = A._bayer(im.width, im.height)
    sx = LB0
    heap = [(sx - 1, lb_sheer(sx) - 1), (sx + 1, 106), (sx + 4, 103), (sx + 8, 101), (sx + 12, 102), (sx + 15, 100),
            (sx + 19, 101), (sx + 23, 103), (sx + 27, 105), (sx + 31, 108), (sx + 34, lb_sheer(sx + 34) - 1),
            (sx + 34, lb_sheer(sx + 34) + 1), (sx - 1, lb_sheer(sx) + 1)]
    wr = [(sx + 2, 105, 0.5), (sx + 6, 108, 0.35), (sx + 16, 104, 0.45), (sx + 22, 108, 0.3), (sx + 12, 110, 0.4)]

    def heap_col(x, y):
        # 皱褶：几条斜的“脊”（亮）和它下面的“沟”（暗）
        for (cx, cy, s) in wr:
            r = (y - cy) - (x - cx) * s
            if 0 <= x - cx <= 9 and -0.5 <= r < 0.5:
                return CANVAS_HI if y < 106 else CANVAS_L
            if 0 <= x - cx <= 9 and 0.5 <= r < 1.5:
                return CANVAS_S
        top = 100 + abs(x - sx - 15) * 0.4
        v = (y - top) / 12.0
        if v < 0.25:
            return CANVAS_L
        if v < 0.7:
            return CANVAS
        return CANVAS_S if bay[y, x] < 0.6 else CANVAS_D
    _shade_region(im, heap, heap_col)
    drape = [(sx - 1, 109), (sx + 2, 112), (sx + 2, 120), (sx + 1, 127), (sx - 2, 129), (sx - 4, 126), (sx - 4, 118),
             (sx - 3, 111)]

    def drape_col(x, y):
        if x in (sx - 2, sx + 1):
            return CANVAS_D
        if x == sx - 1:
            return CANVAS_L
        return CANVAS if y < 120 else CANVAS_S
    _shade_region(im, drape, drape_col)
    flap = [(sx + 6, lb_sheer(sx + 6) + 1), (sx + 22, lb_sheer(sx + 22) + 1), (sx + 21, lb_sheer(sx + 21) + 5),
            (sx + 17, lb_sheer(sx + 17) + 7), (sx + 13, lb_sheer(sx + 13) + 5), (sx + 9, lb_sheer(sx + 9) + 7),
            (sx + 6, lb_sheer(sx + 6) + 4)]

    def flap_col(x, y):
        if (x - sx) % 7 == 3:
            return CANVAS_S
        if (x - sx) % 7 == 2:
            return CANVAS_L
        return CANVAS
    _shade_region(im, flap, flap_col)
    d = ImageDraw.Draw(im)
    d.line([(sx - 3, 112), (sx + 1, 106), (sx + 4, 103), (sx + 8, 101), (sx + 12, 102), (sx + 15, 100),
            (sx + 19, 101), (sx + 23, 103), (sx + 27, 105), (sx + 31, 108), (sx + 34, round(lb_sheer(sx + 34)) - 1)],
           fill=C(CANVAS_D))
    d.line([(sx - 4, 118), (sx - 4, 126), (sx - 2, 129), (sx + 1, 127)], fill=C(CANVAS_D))
    for gx in (sx + 9, sx + 18):                                     # 扣眼
        px(d, gx, round(lb_sheer(gx)) + 5, (214, 218, 220))
    # 松开的系绳 / 绑带垂在船舷外
    for xa in (151, 177, 189):
        y = round(lb_sheer(xa)) + 2
        d.line((xa, y, xa + 1, y + 4, xa, y + 7), fill=C(ROPE))
        px(d, xa, y + 8, ROPE_D)
    for x in STRAP_XS[1:]:
        y = round(lb_sheer(x)) + 2
        vl(d, x, y, y + 9, ROPE)
        vl(d, x + 1, y, y + 9, ROPE_D)
        rect(d, x, y + 10, x + 1, y + 11, SS_D)
    # 吊索垂进艇里，挂在吊环上
    for bx in falls:
        yb = round(far_gw(bx)) + 3
        if bx < LB0 + 30:
            yb = 99                                                # 艇尾那根被帆布堆挡住
        vl(d, bx, 88, yb, ROPE_D)
        px(d, bx, 88, ROPE)


# ============================================================ 上层建筑
def cab_rake(y):
    """船舱前端（斜的）在第 y 行的 x。"""
    return SS1 - 1 - (143 - y) * 6.0 / 47.0


def wh_rake(y):
    return WH1 - 1 - (88 - y) * 8.0 / 24.0


def porthole(d, cx, cy, r=4):
    d.ellipse((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), fill=C(SS_M))
    d.arc((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), 160, 290, fill=C(SS_HI))
    d.arc((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), 340, 100, fill=C(SS_D))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C(GLASS))
    d.ellipse((cx - r + 1, cy - r + 2, cx + r - 1, cy + r), fill=C(GLASS_D))
    d.line((cx - r + 1, cy, cx, cy - r + 1), fill=C(GLASS_HI))       # 天空的倒影
    d.line((cx - r + 2, cy + 1, cx + 1, cy - r + 2), fill=C((86, 120, 160)))
    px(d, cx + 1, cy - 2, (236, 246, 252))


def door(d, x0, x1, y0, round_win=False):
    """舱门：门框（门洞略凹，左边和上边落影）+ 门板 + 窗 + 把手 + 百叶 + 门槛。"""
    rect(d, x0 - 1, y0 - 1, x1 + 1, 142, WHITE_S)
    rect(d, x0, y0, x1, 142, WHITE)
    vl(d, x0, y0, 142, WHITE_D)
    hl(d, x0, x1, y0, WHITE_D)
    vl(d, x1, y0 + 1, 142, WHITE_M)
    if round_win:
        cx, cy = (x0 + x1) // 2, y0 + 10
        porthole(d, cx, cy, 4)
    else:
        rect(d, x0 + 3, y0 + 4, x1 - 3, y0 + 16, SS_M)
        rect(d, x0 + 4, y0 + 5, x1 - 4, y0 + 15, GLASS_D)
        d.line((x0 + 4, y0 + 12, x0 + 9, y0 + 5), fill=C(GLASS_HI))
        d.line((x0 + 4, y0 + 14, x0 + 11, y0 + 6), fill=C((70, 104, 142)))
        hl(d, x0 + 4, x1 - 4, y0 + 5, GLASS)
    hy = y0 + 23
    rect(d, x1 - 3, hy, x1 - 1, hy, SS_HI)                           # 把手
    px(d, x1 - 1, hy + 1, SS_D)
    px(d, x1 - 2, hy + 3, INK)                                       # 锁眼
    for yy in (136, 138):                                            # 百叶通风口
        hl(d, x0 + 3, x1 - 3, yy, WHITE_S)
        hl(d, x0 + 3, x1 - 3, yy + 1, WHITE_HI)
    rect(d, x0 - 2, 141, x1 + 2, 143, TEAK_M)                        # 门槛
    hl(d, x0 - 2, x1 + 2, 141, TEAK_HI)
    for hy2 in (y0 + 5, 132):                                        # 合页
        px(d, x0 + 1, hy2, SS_D)
        px(d, x0 + 1, hy2 + 1, SS_D)


def draw_radio(d):
    """无线电：舱壁上的灰色防水箱（绿屏、旋钮、喇叭网）+ 挂在侧面的话筒 + 盘绕的电线 + 往上走的天线馈线。"""
    x0, y0, x1, y1 = 341, 111, 357, 126
    vl(d, 354, 97, y0 - 1, (84, 90, 104))                            # 天线馈线（沿舱壁往上，夹子固定）
    for yy in range(99, y0, 5):
        px(d, 353, yy, SS_D)
        px(d, 355, yy, SS_D)
    rect(d, x0 - 1, y1 + 1, x1 + 1, y1 + 2, SS_D)                    # 托架
    px(d, x0, y1 + 3, SS_K)
    px(d, x1, y1 + 3, SS_K)
    rect(d, x0, y0, x1, y1, (90, 98, 112), outline=(52, 56, 68))
    hl(d, x0 + 1, x1 - 1, y0 + 1, (132, 140, 154))
    vl(d, x0 + 1, y0 + 1, y1 - 1, (118, 126, 140))
    rect(d, x0 + 2, y0 + 3, x0 + 9, y0 + 6, (110, 200, 140))         # 绿屏
    for xx in (x0 + 3, x0 + 5, x0 + 6, x0 + 8):
        px(d, xx, y0 + 4, (50, 110, 70))
    px(d, x0 + 4, y0 + 5, (50, 110, 70))
    for kx in (x0 + 3, x0 + 7):                                      # 旋钮
        rect(d, kx - 1, y0 + 9, kx + 1, y0 + 11, (200, 206, 214))
        px(d, kx, y0 + 10, (60, 64, 74))
    px(d, x0 + 3, y0 + 13, (240, 70, 60))                            # 电源灯
    for yy in range(y0 + 3, y1 - 1, 2):                              # 喇叭网
        for xx in range(x0 + 11, x1 - 1, 2):
            px(d, xx, yy, (58, 62, 74))
    rect(d, x1 + 1, y0 + 2, x1 + 3, y0 + 11, (34, 34, 40))           # 话筒（挂在右侧）
    vl(d, x1 + 1, y0 + 3, y0 + 10, (86, 88, 100))
    px(d, x1 + 2, y0 + 2, (70, 72, 84))
    pts = []                                                         # 盘绕的电线
    for i in range(23):
        u = i / 22
        x = x1 + 2 - u * 6 + math.sin(u * math.pi * 6) * 1.6
        y = y0 + 12 + math.sin(u * math.pi) * 9
        pts.append((round(x), round(y)))
    for i, p in enumerate(pts):
        px(d, p[0], p[1], (40, 40, 48) if i % 2 else (96, 98, 110))


def draw_extinguisher(d, x, y):
    rect(d, x - 1, y + 4, x + 5, y + 5, SS_D)                        # 卡箍
    rect(d, x, y, x + 4, y + 14, (204, 44, 40))
    vl(d, x, y + 1, y + 14, (240, 104, 92))
    vl(d, x + 4, y + 1, y + 14, (140, 26, 26))
    hl(d, x, x + 4, y + 14, (120, 22, 22))
    rect(d, x + 1, y - 3, x + 3, y - 1, (40, 40, 46))                # 阀
    px(d, x + 2, y - 4, (70, 70, 80))
    d.line((x + 4, y - 2, x + 6, y, x + 6, y + 8), fill=C((34, 34, 40)))   # 喷管
    rect(d, x + 1, y + 7, x + 3, y + 9, (240, 240, 236))             # 标签
    px(d, x + 2, y + 8, (60, 60, 70))


def draw_ladder(d, x0, x1, ytop, ybot):
    """固定在舱壁上的不锈钢爬梯（两根立管 + 横档；在墙上落一道影）；立管伸出舱顶弯成扶手。"""
    for x in (x0, x1):
        vl(d, x + 1, ytop + 2, ybot, WHITE_S)                        # 墙上的影
    for y in range(ybot - 3, ytop + 6, -6):
        hl(d, x0 + 1, x1 - 1, y + 1, WHITE_S)
        hl(d, x0, x1, y, SS_M)
        px(d, x0 + 1, y, SS_HI)
    for x in (x0, x1):
        vl(d, x, ytop + 2, ybot, SS_M)
        px(d, x, ybot, SS_D)
    vl(d, x0, ytop + 2, ybot, SS_HI)
    d.arc((x0 - 1, ytop - 2, x0 + 3, ytop + 4), 180, 300, fill=C(SS_M))
    d.arc((x1 - 3, ytop - 2, x1 + 1, ytop + 4), 240, 360, fill=C(SS_M))
    for y in (ybot - 6, (ytop + ybot) // 2, ytop + 12):              # 固定座
        px(d, x0 - 1, y, SS_D)
        px(d, x1 + 1, y, SS_D)


def draw_superstructure(im, d):
    # ---------- 一层船舱
    for y in range(CAB_TOP, 144):
        xr = int(cab_rake(y))
        if y <= CAB_TOP + 1:
            c = WHITE_S                                              # 檐口下的影
        elif y in (137, 138):
            c = NAVY if y == 137 else NAVY_D                         # 踢脚蓝线
        elif y >= 142:
            c = WHITE_S if y == 142 else (150, 156, 168)
        elif y >= 139:
            c = WHITE_M
        elif y >= 127:
            c = (238, 235, 228) if y < 132 else (234, 230, 221)       # 墙脚被柚木甲板反上来的一点暖光
        else:
            c = WHITE if y > CAB_TOP + 3 else WHITE_M
        hl(d, SS0, xr, y, c)
        if 127 <= y < 139 and y % 2 == 0:                              # 冷暖交界抖一下
            for x in range(SS0 + (y // 2) % 2, xr, 2):
                if y in (127, 128):
                    px(d, x, y, WHITE)
        px(d, xr, y, WHITE_S if y < 137 else c)
        px(d, xr - 1, y, mix(c, WHITE_S, 0.5) if y < 137 else c)
    vl(d, SS0, CAB_TOP + 2, 141, WHITE_HI)                           # 船舱后端的亮边
    # 檐口（舱顶边缘：顶面 89–91 + 立面 92–95，前后各伸出 2 px）
    xr0 = int(cab_rake(CAB_TOP)) + 2
    rect(d, SS0 - 2, 89, xr0, 89, WHITE_M)
    rect(d, SS0 - 2, 90, xr0, 91, WHITE_HI)
    rect(d, SS0 - 2, 92, xr0, 94, WHITE)
    hl(d, SS0 - 2, xr0, 92, WHITE_HI)
    hl(d, SS0 - 2, xr0, 94, NAVY)
    hl(d, SS0 - 2, xr0, 95, WHITE_D)
    vl(d, xr0, 89, 95, WHITE_S)
    # 舷窗
    for cx in (322, 336, 392, 405):
        porthole(d, cx, 108)
    porthole(d, 284, 106, 3)
    # 舱门（x 292–308）、去驾驶室的前门（x 362–378，圆窗 + 小牌子）
    door(d, 293, 307, 103)
    rect(d, 298, 98, 302, 99, SS_M)                                  # 门顶灯
    hl(d, 299, 301, 100, (255, 250, 220))
    door(d, 363, 377, 103, round_win=True)
    rect(d, 366, 98, 374, 100, NAVY)
    hl(d, 367, 373, 99, (180, 196, 220))
    # 扶手（沿舱壁的一道不锈钢管 + 支脚）
    for (xa, xb) in ((312, 339), (380, 412)):
        hl(d, xa, xb, 118, SS_M)
        hl(d, xa, xb, 117, SS_HI)
        hl(d, xa, xb, 119, WHITE_S)
        for xx in range(xa + 2, xb, 9):
            px(d, xx, 120, SS_D)
    draw_extinguisher(d, 280, 121)
    draw_radio(d)
    draw_ladder(d, 266, 273, 80, 142)
    # 船钟（黄铜，挂在舱门右上）
    rect(d, 312, 99, 317, 100, SS_D)
    vl(d, 314, 100, 101, SS_D)
    d.polygon([(312, 102), (316, 102), (317, 107), (311, 107)], fill=C((210, 168, 66)))
    vl(d, 312, 103, 106, (246, 214, 124))
    vl(d, 316, 103, 106, (150, 110, 40))
    hl(d, 311, 317, 107, (150, 110, 40))
    vl(d, 314, 108, 111, ROPE)
    px(d, 314, 112, ROPE_D)
    # 绕在墙上的水管卷盘（绿色）
    d.ellipse((384, 123, 396, 135), fill=C((46, 112, 70)), outline=C((26, 66, 42)))
    d.ellipse((387, 126, 393, 132), outline=C((84, 158, 104)))
    d.arc((384, 123, 396, 135), 200, 290, fill=C((110, 186, 128)))
    rect(d, 389, 128, 391, 130, SS_D)
    d.line((395, 133, 399, 140, 404, 142), fill=C((46, 112, 70)))
    rect(d, 403, 141, 406, 142, SS_M)
    # 舱顶后半的露天平台：救生筏筒 + 栏杆
    rect(d, 276, 84, 302, 88, SS_D)                                  # 筏架
    d.rounded_rectangle((277, 79, 301, 87), radius=4, fill=C(WHITE), outline=C(WHITE_D))
    hl(d, 280, 298, 80, WHITE_HI)
    hl(d, 279, 299, 86, WHITE_S)
    rect(d, 288, 79, 289, 87, (230, 120, 50))                        # 橙色绑带
    px(d, 288, 83, SS_D)
    rect(d, 281, 82, 284, 84, (70, 120, 190))                        # 标签
    for x in (264, 290, 314):
        vl(d, x, 79, 88, SS_M)
        px(d, x + 1, 80, SS_D)
    hl(d, 262, 316, 78, SS_HI)
    hl(d, 262, 316, 79, SS_D)
    hl(d, 262, 316, 84, SS_M)
    # ---------- 二层驾驶室
    for y in range(WH_TOP, 89):
        xr = int(wh_rake(y))
        c = WHITE_S if y <= WH_TOP + 1 else WHITE
        hl(d, WH0, xr, y, c)
        px(d, xr, y, WHITE_S)
    vl(d, WH0, WH_TOP + 2, 88, WHITE_HI)
    hl(d, WH0, int(wh_rake(88)), 88, WHITE_S)
    rect(d, WH0 - 1, 89, int(wh_rake(88)) + 1, 89, (150, 156, 168))  # 和舱顶的接缝
    # 侧窗（三扇，深色玻璃 + 斜的天空倒影）
    for (xa, xb) in ((334, 352), (356, 374), (378, 394)):
        rect(d, xa - 1, 67, xb + 1, 84, WHITE_S)
        rect(d, xa, 68, xb, 83, GLASS_D)
        hl(d, xa, xb, 68, GLASS)
        for k, off in enumerate((2, 9)):
            for s in range(0, 16):
                x = xa + off + s
                y = 83 - s
                if xa <= x <= xb and 68 <= y <= 83:
                    px(d, x, y, GLASS_HI if k == 0 else (78, 112, 150))
                    if x + 1 <= xb and k == 0:
                        px(d, x + 1, y, (92, 128, 168))
        hl(d, xa, xb, 84, WHITE_HI)
    # 斜的前窗（露出一窄条）+ 雨刷
    for y in range(67, 85):
        xr = int(wh_rake(y))
        for x in range(xr - 8, xr - 1):
            px(d, x, y, GLASS if (x + y) % 7 else (70, 100, 136))
        px(d, xr - 9, y, WHITE_S)
    for y in range(67, 85, 1):
        xr = int(wh_rake(y))
        if (y - 67) < 9:
            px(d, xr - 6 + (y - 67) // 3, y, GLASS_HI)
    d.line((int(wh_rake(83)) - 5, 83, int(wh_rake(70)) - 7, 70), fill=C((34, 36, 44)))     # 雨刷（竖着的那根）
    d.line((int(wh_rake(83)) - 4, 83, int(wh_rake(71)) - 6, 71), fill=C((70, 74, 86)))
    hl(d, int(wh_rake(84)) - 8, int(wh_rake(84)) - 3, 84, (34, 36, 44))                   # 停着的那根
    px(d, int(wh_rake(84)) - 5, 85, SS_D)
    # 驾驶室侧门
    rect(d, 320, 66, 331, 88, WHITE_S)
    rect(d, 321, 67, 330, 88, WHITE)
    vl(d, 321, 67, 88, WHITE_D)
    rect(d, 323, 69, 328, 77, GLASS_D)
    d.line((323, 75, 327, 69), fill=C(GLASS_HI))
    px(d, 329, 80, SS_HI)
    # 绿舷灯（右舷那一侧对着我们）
    rect(d, 396, 85, 401, 88, (30, 32, 38))
    rect(d, 398, 86, 401, 87, (80, 220, 130))
    px(d, 400, 86, (200, 255, 220))
    # 遮阳檐 + 顶（在视线上方：看得见檐下）
    xr_top = int(wh_rake(WH_TOP)) + 6
    rect(d, WH0 - 2, 58, xr_top, 61, WHITE)
    hl(d, WH0 - 2, xr_top, 58, WHITE_HI)
    hl(d, WH0 - 2, xr_top, 61, NAVY)
    rect(d, WH0 - 1, 62, xr_top - 1, 63, WHITE_D)                    # 檐下的阴影
    vl(d, xr_top, 58, 61, WHITE_S)
    # 探照灯（顶前端，朝前）
    rect(d, 400, 55, 401, 57, SS_D)
    rect(d, 397, 50, 405, 55, (66, 72, 86), outline=(40, 44, 54))
    hl(d, 398, 404, 51, (110, 118, 134))
    vl(d, 406, 50, 55, SS_HI)
    vl(d, 407, 51, 54, (250, 246, 220))
    # 顶上的栏杆（前后两小段）
    for (xa, xb) in ((320, 335), (392, 404)):
        hl(d, xa, xb, 50, SS_HI)
        hl(d, xa, xb, 51, SS_D)
        for x in range(xa + 1, xb, 7):
            vl(d, x, 52, 57, SS_M)
    # ---------- 雷达拱架
    arch_l = [(338, 58), (348, 58), (346, 30), (341, 30)]
    arch_r = [(380, 58), (390, 58), (388, 30), (383, 30)]
    for poly in (arch_l, arch_r):
        d.polygon(poly, fill=C(WHITE))
        d.line((poly[0], poly[3]), fill=C(WHITE_HI))
        d.line((poly[1], poly[2]), fill=C(WHITE_S))
        d.line(((poly[0][0] + poly[1][0]) // 2, 56, (poly[2][0] + poly[3][0]) // 2, 32), fill=C(NAVY))
    rect(d, 339, 26, 389, 30, WHITE)
    hl(d, 339, 389, 26, WHITE_HI)
    hl(d, 347, 382, 30, WHITE_D)                                     # 横梁底面（在视线上方）
    hl(d, 341, 387, 28, NAVY)
    px(d, 339, 30, WHITE_S)
    px(d, 389, 30, WHITE_S)
    # 雷达底座（天线在 radar strip 里转）、GPS 罩
    rect(d, 360, 21, 367, 25, (80, 88, 102), outline=(46, 50, 62))
    hl(d, 361, 366, 22, (124, 132, 148))
    rect(d, 362, 19, 365, 20, (60, 66, 78))
    d.ellipse((371, 20, 378, 27), fill=C(WHITE), outline=C(WHITE_D))
    d.arc((371, 20, 378, 27), 180, 260, fill=C(WHITE_HI))
    rect(d, 371, 25, 378, 25, WHITE_D)
    # 桅杆 + 横桁 + 桅顶灯（旗挂在横桁后端，在 flag strip 里）
    vl(d, 350, 6, 25, SS_HI)
    vl(d, 351, 6, 25, SS_D)
    hl(d, 345, 356, 12, SS_M)
    hl(d, 345, 356, 13, SS_D)
    rect(d, 349, 3, 352, 5, (60, 64, 76))
    px(d, 350, 3, (255, 252, 226))
    px(d, 351, 3, (255, 240, 190))
    d.line((356, 13, 360, 19), fill=C((200, 206, 214)))              # 支索
    # VHF 天线（两根细白杆，在拱架前端）
    vl(d, 383, 3, 25, (214, 218, 226))
    rect(d, 382, 23, 384, 25, (60, 64, 76))
    vl(d, 387, 9, 25, (214, 218, 226))
    rect(d, 386, 23, 388, 25, (60, 64, 76))
    # 汽笛（装在拱架前腿上，喇叭口朝前）
    rect(d, 389, 39, 391, 41, SS_D)
    d.polygon([(391, 39), (395, 37), (396, 37), (396, 43), (395, 43), (391, 41)], fill=C(SS_M))
    vl(d, 396, 37, 43, SS_HI)
    hl(d, 392, 395, 39, SS_HI)
    px(d, 397, 40, (70, 74, 86))


# ============================================================ 前甲板
def crate(d, x0, y0, x1, y1, top=3, seed=0):
    """木箱：正面横板（有缝、有钉）+ 两边竖框 + 顶面（视线下方，看得见一条）+ 右边一列暗。"""
    rect(d, x0, y0 - top, x1, y0 - 1, WOOD_HI)
    hl(d, x0 + 1, x1 - 1, y0 - top, (236, 206, 152))
    for x in range(x0 + 4, x1, 6):
        vl(d, x, y0 - top + 1, y0 - 1, WOOD)
    rect(d, x0, y0, x1, y1, WOOD)
    for y in range(y0 + 4, y1, 5):
        hl(d, x0, x1, y, WOOD_S)
        hl(d, x0, x1, y - 1, WOOD_M) if hash01(seed, y) < 0.3 else None
    for y in range(y0 + 1, y1, 3):
        if hash01(seed, y, 2) < 0.35:
            hl(d, x0 + 3 + int(hrange(0, 6, seed, y)), x0 + 6 + int(hrange(0, 8, seed, y, 3)), y, WOOD_M)
    rect(d, x0, y0, x0 + 2, y1, WOOD_HI)
    rect(d, x1 - 2, y0, x1, y1, WOOD_M)
    vl(d, x1, y0, y1, WOOD_S)
    hl(d, x0, x1, y0, (236, 206, 152))
    hl(d, x0, x1, y1, WOOD_D)
    for y in range(y0 + 2, y1, 5):
        px(d, x0 + 1, y, WOOD_D)
        px(d, x1 - 1, y, WOOD_D)
    d.line((x0 + 3, y1 - 2, x1 - 3, y0 + 2), fill=C(WOOD_M))           # 斜撑
    d.line((x0 + 3, y1 - 1, x1 - 3, y0 + 3), fill=C(WOOD_S))


def draw_crates(im, d):
    crate(d, 516, 117, 540, 142, top=3, seed=1)
    crate(d, 541, 125, 561, 142, top=3, seed=2)
    crate(d, 520, 102, 537, 116, top=3, seed=3)
    # 印的记号（向上箭头、易碎玻璃杯、色块）——不写字
    for (x, y) in ((524, 122),):
        vl(d, x, y, y + 5, (90, 60, 40))
        d.line((x - 2, y + 2, x, y, x + 2, y + 2), fill=C((90, 60, 40)))
        vl(d, x + 5, y, y + 5, (90, 60, 40))
        d.line((x + 3, y + 2, x + 5, y, x + 7, y + 2), fill=C((90, 60, 40)))
    d.polygon([(546, 129), (551, 129), (550, 132), (549, 133), (549, 135), (551, 135), (546, 135), (548, 135),
               (548, 133), (547, 132)], outline=C((150, 40, 40)))
    rect(d, 526, 106, 532, 109, (60, 90, 140))
    # 绑绳：两道从甲板眼环上来压过箱子
    for x in (523, 533):
        for y in range(114, 143):
            px(d, x, y, ROPE_L if y % 3 else ROPE)
            px(d, x + 1, y, ROPE_D if y % 3 == 1 else WOOD_S)
        for y in range(99, 114):
            if x < 537:
                px(d, x, y, ROPE_L if y % 3 else ROPE)
    d.line((542, 124, 560, 141), fill=C(ROPE))
    d.line((542, 125, 560, 142), fill=C(ROPE_D))
    for x in (523, 533, 560):
        rect(d, x - 1, 142, x + 1, 143, SS_D)
    # 黄色紧固带（上面那个箱子）
    rect(d, 528, 99, 530, 116, (232, 196, 58))
    vl(d, 530, 100, 116, (184, 148, 36))
    rect(d, 527, 108, 531, 111, SS_M)
    px(d, 528, 109, SS_HI)


def draw_bitts(d, x):
    for bx in (x, x + 7):
        rect(d, bx, 133, bx + 3, DY0 - 1, SS_M)
        vl(d, bx, 133, DY0 - 1, SS_HI)
        vl(d, bx + 3, 133, DY0 - 1, SS_D)
        rect(d, bx - 1, 131, bx + 4, 132, SS_HI)
        hl(d, bx - 1, bx + 4, 132, SS_M)
    hl(d, x + 4, x + 6, 136, SS_D)
    rect(d, x - 2, DY0 - 1, x + 12, DY0 + 1, SS_D)
    hl(d, x - 2, x + 12, DY0 - 1, SS_M)


def draw_rope_coil(d, cx, cy):
    """盘好的缆绳（扁椭圆一圈套一圈）+ 一截绳头搭到缆桩。"""
    rect_e = lambda rx, ry: (cx - rx, cy - ry, cx + rx, cy + ry)
    d.ellipse(rect_e(10, 4), fill=C(ROPE_D))
    for i, (rx, ry) in enumerate(((10, 4), (8, 3), (6, 2), (4, 1))):
        d.ellipse(rect_e(rx, ry), outline=C(ROPE_L if i % 2 == 0 else ROPE))
    d.ellipse(rect_e(2, 1), fill=C(ROPE_D))
    for x in range(cx - 9, cx + 10, 2):
        y = cy - 4 + (1 if abs(x - cx) > 7 else 0)
        px(d, x, y, ROPE)
    d.line((cx - 10, cy, cx - 16, cy - 2, cx - 20, cy - 4), fill=C(ROPE))


def draw_windlass(d):
    """锚机：底板 + 机身 + 左边卷缆鼓 + 右边链轮（锚链从这里绕出去）+ 刹车柄。"""
    rect(d, 561, 140, 593, 144, (66, 72, 84))
    hl(d, 561, 593, 140, (110, 118, 132))
    for xx in (563, 591):
        px(d, xx, 142, SS_HI)
    rect(d, 569, 128, 583, 140, (92, 104, 122), outline=(52, 58, 72))
    hl(d, 570, 582, 129, (132, 144, 162))
    vl(d, 570, 129, 139, (120, 132, 150))
    for xx in (572, 580):
        px(d, xx, 131, (60, 66, 80))
        px(d, xx, 137, (60, 66, 80))
    rect(d, 562, 131, 568, 138, SS_M)                                # 卷缆鼓
    hl(d, 562, 568, 131, SS_HI)
    hl(d, 562, 568, 138, SS_D)
    for yy in (133, 135):
        hl(d, 563, 567, yy, SS_D)
    d.ellipse((583, 129, 592, 139), fill=C((60, 64, 76)), outline=C((36, 38, 48)))     # 链轮
    for a in range(0, 360, 45):
        r = math.radians(a)
        px(d, round(587.5 + math.cos(r) * 4), round(134 + math.sin(r) * 4), (130, 136, 150))
    rect(d, 586, 132, 589, 136, SS_D)
    vl(d, 576, 119, 128, (40, 42, 50))                               # 刹车柄
    rect(d, 575, 117, 577, 119, (210, 50, 44))


def draw_chain(d, x0, y0, x1, y1):
    n = int(math.hypot(x1 - x0, y1 - y0))
    for s in range(n + 1):
        u = s / n
        x = round(x0 + (x1 - x0) * u)
        y = round(y0 + (y1 - y0) * u + 1.5 * math.sin(math.pi * u))
        col = (150, 156, 168) if s % 3 == 0 else ((80, 84, 96) if s % 3 == 1 else (112, 118, 130))
        px(d, x, y, col)
        if s % 3 == 0:
            px(d, x, y - 1, (60, 64, 74))


HATCH = (451, 147, 489, 156)                     # 平的货舱盖（甲板面上的框，含围板）


def draw_hatch(im, d):
    """平的货舱盖（平躺在甲板上，在可走带里）：一圈窄的不锈钢包边（远边亮）、柚木拼条的盖板（和甲板同色系、
    颜色压低）、远边两个合页、中间一个凹进去的拉手、近边右侧的搭扣 + 黄铜挂锁（“舱盖锁着”）。"""
    x0, y0, x1, y1 = HATCH
    rect(d, x0, y0, x1, y1, SS_D)
    hl(d, x0, x1, y0, SS_HI)
    hl(d, x0 + 1, x1 - 1, y1, (110, 98, 86))                          # 近边：包边的一线暗
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            k = (y - y0 - 1) // 2
            c = TEAK_HI if k % 2 == 0 else TEAK
            if x in (x0 + 13, x0 + 26) or y == y1 - 1:
                c = TEAK_M
            px(d, x, y, c)
    for x in range(x0 + 1, x1):
        px(d, x, y0 + 1, mix(TEAK_HI, (255, 236, 200), 0.3))
    rect(d, 466, 151, 474, 152, (122, 88, 56))                       # 凹拉手
    hl(d, 467, 473, 151, SS_K)
    hl(d, 467, 473, 153, mix(TEAK_HI, (255, 236, 200), 0.4))
    for hx in (457, 480):                                            # 合页（远边）
        rect(d, hx, y0, hx + 4, y0 + 1, SS_M)
        px(d, hx + 2, y0 + 1, SS_K)
    rect(d, x1 - 6, y1 - 2, x1 - 4, y1 + 1, SS_M)                    # 搭扣 + 挂锁
    px(d, x1 - 5, y1 - 2, SS_HI)
    rect(d, x1 - 7, y1 + 2, x1 - 3, y1 + 5, (206, 168, 62))
    hl(d, x1 - 7, x1 - 3, y1 + 2, (240, 214, 120))
    px(d, x1 - 5, y1 + 4, (110, 84, 30))
    vl(d, x1 - 3, y1 + 3, y1 + 5, (160, 124, 40))


def draw_bow(im, d):
    """船头：远侧舷墙 / 栏杆顺着收窄的甲板边往下弯到船头尖；船头护栏；锚架 + 锚；近侧船壳。"""
    for x in range(XB, PW):
        yf = y_far(x)
        yn = y_near(x)
        ybw = int(round(yf)) - 8
        # 远侧舷墙
        for y in range(ybw, int(round(yf))):
            v = (y - ybw) / 8.0
            px(d, x, y, WHITE_M if v < 0.75 else WHITE_D)
        px(d, x, ybw - 2, TEAK_HI)
        px(d, x, ybw - 1, TEAK_S)
        # 近侧船壳（甲板边下面，白漆 + 蓝饰线），一直到底
        for y in range(int(round(yn)) + 3, H):
            v = (y - yn) / max(1.0, H - yn)
            c = WHITE if v < 0.35 else (WHITE_M if v < 0.6 else WHITE_S)
            if abs(y - (yn + 9 + (x - XB) * 0.12)) < 1.0:
                c = NAVY
            px(d, x, y, c)
    # 船头护栏（顶管顺着往下弯，到船头尖立一根前柱）+ 立柱
    prev = None
    for x in range(XB - 1, 637):
        y = round(y_far(x) - 25 + 4 * ((x - XB) / 40.0) ** 2) if x > XB else RAIL_Y
        if prev is not None:
            d.line((prev[0], prev[1], x, y), fill=C(SS_HI))
            d.line((prev[0], prev[1] + 1, x, y + 1), fill=C(SS_D))
        prev = (x, y)
    vl(d, 636, prev[1], round(y_far(636)) - 2, SS_M)
    vl(d, 637, prev[1] + 1, round(y_far(636)) - 2, SS_D)
    for x in (610, 624):
        yt = round(y_far(x) - 25 + 4 * ((x - XB) / 40.0) ** 2) + 2
        vl(d, x, yt, round(y_far(x)) - 9, SS_HI)
        vl(d, x + 1, yt, round(y_far(x)) - 9, SS_D)
    # 近侧的船头护栏（从近侧栏杆尽头扬起来，接到船头尖的前柱）
    prev = None
    for x in range(XB, 637):
        u = (x - XB) / (636 - XB)
        y = round(168 + ((y_far(636) - 25 + 4 * (40 / 40.0) ** 2) - 168) * u ** 1.4)
        if prev is not None:
            d.line((prev[0], prev[1], x, y), fill=C(SS_HI))
            d.line((prev[0], prev[1] + 1, x, y + 1), fill=C(SS_D))
        prev = (x, y)
    for x in (612,):
        u = (x - XB) / (636 - XB)
        yt = round(168 + ((y_far(636) - 21) - 168) * u ** 1.4) + 2
        vl(d, x, yt, round(y_near(x)) - 1, SS_M)
    # 锚架 + 锚（船头尖）
    rect(d, 622, 151, 639, 154, SS_M)
    hl(d, 622, 639, 151, SS_HI)
    hl(d, 622, 639, 154, SS_D)
    d.ellipse((634, 150, 639, 155), fill=C(SS_D), outline=C(SS_K))
    d.line((626, 152, 638, 156), fill=C(SS_HI), width=2)              # 锚杆
    d.polygon([(635, 155), (639, 154), (639, 162), (636, 160)], fill=C(SS_M))
    d.line((635, 155, 636, 160), fill=C(SS_HI))
    px(d, 638, 161, SS_D)


# ============================================================ 甲板（柚木）
PLANK_SEAMS = [143, 146, 149, 152, 155, 159, 163, 167, 171, 175]


def draw_deck(im):
    """柚木甲板：远侧边 141–142（暗角 + 边板）、10 条板（越近越宽，缝颜色只比板暗一点）、错开的接缝和木塞、
    木纹；近侧 175–176 边板、177–179 柚木护舷条。船头那段板缝往船头尖收拢。"""
    a = np.array(im)
    bay = A._bayer(PW, H)
    rows = [141, 143] + PLANK_SEAMS[1:] + [175]
    for x in range(XS, PW):
        yf, yn = y_far(x), y_near(x)
        if yn - yf < 1:
            continue
        for y in range(int(math.floor(yf)), min(H, int(math.ceil(yn)) + 3)):
            if y < yf - 0.01:
                continue
            # 把这一列的 y 映射回“直甲板”的 y（船头收拢）
            yy = DY0 + (y - yf) / max(0.5, yn - yf) * (DY1 - DY0)
            if yy >= DY1:
                # 近侧护舷条（柚木）
                k = int(yy - DY1)
                c = TEAK_HI if k == 0 else (TEAK_M if k == 1 else TEAK_S)
            elif yy < DY0 + 1:
                c = (150, 112, 74)                                     # 舷墙脚的暗角
            elif yy < 143:
                c = TEAK_M
            else:
                seam = any(abs(yy - s) < 0.5 for s in PLANK_SEAMS)
                if seam:
                    c = TEAK_SEAM
                else:
                    pi = sum(1 for s in PLANK_SEAMS if s <= yy)
                    v = hash01(pi, x // 53, 7)
                    c = mix(TEAK, TEAK_M if v < 0.5 else TEAK_HI, abs(v - 0.5) * 0.7)
                    g = hash01(pi, x // 5, int(yy), 9)
                    if g < 0.06:
                        c = TEAK_M
                    elif g > 0.95:
                        c = mix(TEAK, TEAK_HI, 0.6)
            a[y, x, :3] = c
            a[y, x, 3] = 255
    # 接缝（每条板错开）+ 两个木塞
    for i in range(len(PLANK_SEAMS) - 1):
        ya, yb = PLANK_SEAMS[i] + 1, PLANK_SEAMS[i + 1] - 1
        x = XS + int(hrange(4, 60, i, 31))
        while x < XB - 4:
            for y in range(ya, yb + 1):
                a[y, x, :3] = TEAK_SEAM
            ym = (ya + yb) // 2
            for dx in (-2, 2):
                a[ym, x + dx, :3] = mix(TEAK, TEAK_HI, 0.75)
            x += int(hrange(46, 88, i, x, 32))
    im.paste(Image.fromarray(a, 'RGBA'))


# ============================================================ 整条船
def deck_shadows(im):
    """太阳在左上、略偏前：朝我们的面是亮的，影子落在物体右边、略往远侧（贴着舷墙脚的那几行甲板 + 舷墙面）。"""
    def wedge(xr, yb, length, hgt=3):
        return [(xr + 1, yb - hgt), (xr + length, yb - hgt), (xr + length - 3, yb), (xr + 1, yb)]
    for (xr, yb, ln, hg) in ((41, 142, 7, 4), (54, 142, 3, 3), (72, 142, 6, 3), (120, 142, 5, 3), (144, 143, 6, 3),
                             (190, 143, 6, 3), (212, 140, 8, 6), (229, 142, 4, 4), (445, 142, 5, 3), (562, 142, 7, 4),
                             (593, 144, 5, 4)):
        cast_shadow(im, wedge(xr, yb, ln, hg), level=1.0)
    # 船舱：墙脚一道暗角 + 前端右边甲板上一块渐淡的影（两层实色，不抖动）
    cast_shadow(im, [(SS0, 144), (SS1, 144), (SS1, 144), (SS0, 144)], level=1.0, mul=np.array((0.84, 0.86, 0.92)))
    cast_shadow(im, [(SS1, 141), (SS1 + 26, 141), (SS1 + 16, 146), (SS1, 146)], level=1.0,
                mul=np.array((0.86, 0.88, 0.94), np.float32))
    cast_shadow(im, [(SS1, 141), (SS1 + 14, 141), (SS1 + 8, 145), (SS1, 145)], level=1.0,
                mul=np.array((0.9, 0.91, 0.95), np.float32))


@lru_cache(maxsize=2)
def near_full(tarp):
    """整条船（640×180，天和海透明）。tarp：0 = 帆布盖着，1 = 掀开。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    # 远侧舷墙 + 栏杆
    draw_far_bulwark(im, d, XS - 4, XB)
    draw_far_rail(d, XS - 4, XB - 1, skip=[(GATE[0] - 3, GATE[1] + 3)])
    # 登船口：两根门柱（顶上一个球）+ 一条垂着的链子；门口没有顶管
    rect(d, GATE[0] + 1, RAIL_Y - 1, GATE[1] - 1, MID_Y, (0, 0, 0))
    a = np.array(im)
    a[RAIL_Y - 1:MID_Y + 1, GATE[0] + 1:GATE[1], 3] = 0
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for gx in GATE:
        rect(d, gx - 1, RAIL_Y, gx + 1, CAP_Y - 1, SS_M)
        vl(d, gx - 1, RAIL_Y, CAP_Y - 1, SS_HI)
        vl(d, gx + 1, RAIL_Y, CAP_Y - 1, SS_D)
        d.ellipse((gx - 2, RAIL_Y - 4, gx + 2, RAIL_Y), fill=C(SS_M))
        px(d, gx - 1, RAIL_Y - 3, SS_HI)
    for x in range(GATE[0] + 2, GATE[1] - 1):
        u = (x - GATE[0] - 2) / (GATE[1] - GATE[0] - 4)
        y = round(RAIL_Y + 4 + 5 * math.sin(math.pi * u))
        px(d, x, y, (150, 156, 168) if x % 2 else (90, 96, 108))
    # 船尾的东西
    draw_rod_holders(d)
    draw_life_ring(d, 46, 121)
    draw_cooler(im, d, 18, DY0 + 1)
    draw_bucket(d, 43, DY0 + 1)
    draw_landing_net(d, 53, DY0 + 1)
    draw_chair(d, 64, DY0 + 1)
    draw_tackle_box(d, 110, DY0 + 1)
    draw_lifejacket_box(d, 214, DY0 + 1)
    # 救生艇
    falls = draw_lifeboat_base(im, d)
    d = ImageDraw.Draw(im)
    if tarp:
        draw_tarp_off(im, d, falls)
    else:
        draw_tarp_on(im, d, falls)
    d = ImageDraw.Draw(im)
    # 上层建筑
    draw_superstructure(im, d)
    # 前甲板
    draw_bitts(d, 434)
    draw_crates(im, d)
    draw_windlass(d)
    draw_bow(im, d)
    # 甲板（画在最后，只填甲板面；上面的东西都在 y ≤ 143）
    deck = A._new(PW, H)
    draw_deck(deck)
    deck.alpha_composite(im)
    im = deck
    d = ImageDraw.Draw(im)
    # 甲板上的东西（画在甲板面上）
    draw_hatch(im, d)
    draw_rope_coil(d, 506, 141)
    draw_chain(d, 591, 139, 628, 152)
    # 船尾：横跨船尾的矮舷墙（侧着看是一条竖带：柚木压条 + 白漆 + 暗边）+ 船尾栏杆（一根竖管，远侧顶管接到近侧顶管）
    for y in range(CAP_Y, H):
        px(d, XS - 4, y, TEAK_HI if y < DY1 else TEAK_M)
        px(d, XS - 3, y, WHITE_M)
        px(d, XS - 2, y, WHITE_S)
        px(d, XS - 1, y, WHITE_D)
    for y in range(RAIL_Y, 169):
        px(d, XS - 4, y, SS_HI)
        px(d, XS - 3, y, SS_D)
    for y in (RAIL_Y + 8, 142, 156):
        rect(d, XS - 5, y, XS - 2, y + 1, SS_M)
        px(d, XS - 5, y, SS_HI)
    # 影子
    deck_shadows(im)
    im = A._grade(im, sat=0.94, val=1.0)
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    return Image.fromarray(a, 'RGBA')


def radar_frame(t):
    """雷达开放式天线：侧面看是一根横条，转一圈 2 s（8 帧），转到正对 / 背对时最长，侧过来只剩一个小方块。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    th = math.tau * f / N_ANIM
    half = 15 * abs(math.cos(th))
    cx = 363.5
    x0, x1 = round(cx - max(2, half)), round(cx + max(2, half))
    front = math.cos(th) >= 0
    rect(d, x0, 16, x1, 18, (236, 238, 240) if front else (200, 206, 214))
    hl(d, x0, x1, 16, (252, 252, 252))
    hl(d, x0, x1, 18, (150, 158, 172))
    if half > 4 and front:
        hl(d, x0 + 2, x1 - 2, 17, (60, 66, 80))
    px(d, x0, 17, (120, 128, 142))
    px(d, x1, 17, (120, 128, 142))
    return im


def flag_frame(t):
    """蓝白旗（上白下蓝），挂在横桁的后端，往船尾飘（船往右开，风从右来）。8 帧一周。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    hx, hy = 344, 14
    vl(d, hx + 1, hy - 2, hy + 9, (90, 96, 110))                       # 旗绳
    L, Hh = 15, 8
    for c in range(L):
        x = hx - c
        ph = math.tau * f / N_ANIM - c * 0.6
        dy = 1.6 * math.sin(ph) * (c / (L - 1)) ** 0.9
        slope = math.cos(ph)
        h = Hh - (1 if c > 10 and math.sin(ph) > 0.5 else 0)
        for r in range(h):
            y = round(hy + r + dy)
            col = (244, 246, 248) if r < h // 2 else (42, 88, 172)
            if slope < -0.35:
                col = dk(col, 0.8)
            elif slope > 0.6:
                col = mix(col, (255, 255, 255), 0.15)
            px(d, x, y, col)
    return im


def _mask_tarp():
    """帆布框：两种状态逐像素不同的范围（外扩 1 px）；船层里这一块里“只在一种状态不透明”的像素抠掉，交给 pick。"""
    a0 = np.array(near_full(0))
    a1 = np.array(near_full(1))
    diff = (a0 != a1).any(-1)
    ys, xs = np.nonzero(diff)
    box = (int(xs.min()) - 1, int(ys.min()) - 1, int(xs.max()) + 2, int(ys.max()) + 2)
    both = (a0[..., 3] == 255) & (a1[..., 3] == 255)
    near = a0.copy()
    x0, y0, x1, y1 = box
    sub = near[y0:y1, x0:x1]
    sub[~both[y0:y1, x0:x1], 3] = 0
    sub[~both[y0:y1, x0:x1], :3] = 0
    return Image.fromarray(near, 'RGBA'), box


@lru_cache(maxsize=1)
def build():
    near, box = _mask_tarp()
    tarps = [near_full(s).crop(box) for s in (0, 1)]
    return dict(sky=sky_img(), clouds=clouds_img(), far=far_img(), sea=[sea_band_img(i) for i in range(len(SEA_BANDS))],
                near=near, tarp_box=box, tarps=tarps, rail=fg_rail())


@lru_cache(maxsize=1)
def fg_rail():
    """近侧低栏杆（画在人前面）：顶管 y 168–170（亮 / 中 / 暗）、每 48 px 一根立柱到护舷条，船尾一根角柱。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    hl(d, XS - 1, XB, 168, SS_HI)
    hl(d, XS - 1, XB, 169, SS_M)
    hl(d, XS - 1, XB, 170, SS_D)
    posts = list(range(XS + 20, XB - 8, 48)) + [XB]
    for x in posts:
        vl(d, x, 171, 177, SS_M)
        vl(d, x, 171, 175, SS_HI)
        vl(d, x + 1, 171, 177, SS_D)
        hl(d, x - 1, x + 2, 178, SS_K)
        px(d, x, 178, SS_M)
    vl(d, XS - 1, 168, 178, SS_HI)
    vl(d, XS, 168, 178, SS_D)
    return im


GULLS = [(30, -7.0, 0.3, 40), (40, -4.5, 0.25, 260)]


def gull_img():
    g = A._new(7, 3)
    d = ImageDraw.Draw(g)
    for (x, y) in ((0, 1), (1, 0), (2, 0), (4, 0), (5, 0), (6, 1)):
        px(d, x, y, (250, 250, 250))
    px(d, 3, 1, (210, 214, 222))
    px(d, 0, 2, (120, 126, 140))
    px(d, 6, 2, (120, 126, 140))
    return g


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0)]
    cim, cy = BJ.crop_rows(R['clouds'])
    layers.append(dict(type='wrap', image=ex.img('clouds', cim), period=640, k=CLOUD_K, y=cy, vx=CLOUD_VX))
    fim, fy = BJ.crop_rows(R['far'])
    layers.append(dict(type='pano', image=ex.img('far', fim), k=FAR_K, x=0, y=fy))
    for i, (y0, y1, k, vx) in enumerate(SEA_BANDS):
        layers.append(dict(type='wrap', image=ex.img('sea%d' % i, R['sea'][i]), period=640, k=k, y=y0, vx=vx))
    layers.append(ex.bake('glitter', GLIT_BOX, N_ANIM, FPS_ANIM, glitter_frame))
    layers.append(ex.bake('wake', WAKE_BOX, N_ANIM, FPS_ANIM, wake_frame, screen=False, k=1.0))
    gk = ex.img('gull', gull_img())
    layers.append(dict(type='clouds', span=460, clouds=[dict(image=gk, x0=float(x0), y=y, vx=vx, k=k)
                                                       for (y, vx, k, x0) in GULLS]))
    nim, ny = BJ.crop_rows(R['near'])
    layers.append(dict(type='pano', image=ex.img('near', nim), k=1.0, x=0, y=ny))
    layers.append(ex.bake('radar', RADAR_BOX, N_ANIM, FPS_ANIM, radar_frame, screen=False, k=1.0))
    layers.append(ex.bake('flag', FLAG_BOX, N_ANIM, FPS_ANIM, flag_frame, screen=False, k=1.0))
    layers.append(ex.bake('rods', RODS_BOX, N_ANIM, FPS_ANIM, rods_frame, screen=False, k=1.0))
    box = R['tarp_box']
    tk = [ex.img('tarp%d' % i, im) for i, im in enumerate(R['tarps'])]
    layers.append(dict(type='pick', images=tk, key='tarp', values=[0, 1], x=box[0], y=box[1], k=1.0))
    rim, ry = BJ.crop_rows(R['rail'])
    fg = [dict(type='pano', image=ex.img('rail', rim), k=1.0, x=0, y=ry)]
    anchors = dict(ANCHORS)
    anchors['lifeboat_box'] = list(box)
    anchors.update(horizon=HZ, deck=[DY0, DY1], rail_y=RAIL_Y, gate=list(GATE), superstructure=[SS0, SS1],
                   ladder=[270, 150], windlass=[577, 150], crates=[540, 150], life_ring=[46, 150],
                   cooler=[28, 150], stern_x=XS)
    st = ex.stage(PW, GROUND, WALK, layers, fg, anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    cams = (0, 80, 160, 240, 320)
    bad = 0
    for camX in cams:
        for t in (0.0, 0.75, 1.5):
            for s in (0, 1):
                im = np.array(BJ.ref_render(st, ex.images, camX, t, dict(tarp=s)).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('游艇 镜头 0–320 × t × 帆布两态 整屏都有画（没有露黑）', bad)
    a = np.array(R['near'])
    hole = 0
    for x in range(XS + 2, XB):
        hole += int((a[DY0:H, x, 3] < 255).sum())
    ex.checked('甲板 / 近侧船壳（y 141–180，x 14–596）整块不透明', hole)
    ex.checked('船层只有 0 / 255 两种透明度', int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum()))
    # 帆布 pick：船层 + pick(s) 合成 = 直接画的那一态（逐像素，含透明度）
    box = R['tarp_box']
    for s in (0, 1):
        comp = R['near'].copy()
        comp.alpha_composite(R['tarps'][s], (box[0], box[1]))
        ex.checked('帆布 tarp=%d：船层 + pick 合成 = 直接画（RGBA 逐像素）' % s, BJ.ndiff_rgba(comp, near_full(s)))
    ex.checked('帆布 pick 两张尺寸一致', 0 if R['tarps'][0].size == R['tarps'][1].size else 1)
    diff_out = 0
    diff_in = 0
    for camX in (0, 60, 120):
        g0 = BJ.ref_render(st, ex.images, camX, 0.5, dict(tarp=0))
        g1 = BJ.ref_render(st, ex.images, camX, 0.5, dict(tarp=1))
        dm = (np.abs(np.asarray(g0.convert('RGB'), np.int16) - np.asarray(g1.convert('RGB'), np.int16)).max(-1) > 0)
        inb = np.zeros_like(dm)
        inb[box[1]:box[3], max(0, box[0] - camX):max(0, box[2] - camX)] = True
        diff_out += int((dm & ~inb).sum())
        diff_in += int((dm & inb).sum())
    ex.checked('帆布两态只在 lifeboat_box 里不同（框外差异像素）', diff_out, extra='框内差 %d px' % diff_in)
    ex.checked('帆布两态在框内确实不同', 0 if diff_in > 200 else 1)
    # strip 2 s 闭合
    for name, box_, fn in (('glitter', GLIT_BOX, glitter_frame), ('wake', WAKE_BOX, wake_frame),
                           ('radar', RADAR_BOX, radar_frame), ('flag', FLAG_BOX, flag_frame),
                           ('rods', RODS_BOX, rods_frame)):
        ex.checked('strip %s 2 s 闭合（t=0 vs t=2）' % name, BJ.ndiff_rgba(fn(0.0).crop(box_), fn(2.0).crop(box_)))
        ex.checked('strip %s 帧条宽 ≤ 4096' % name, 0 if (box_[2] - box_[0]) * N_ANIM <= 4096 else 1)
    # 锚点在地图里
    out = 0
    for k, v in ANCHORS.items():
        if k == 'walk_x':
            out += not (0 <= v[0] < v[1] <= PW)
        else:
            out += not (0 <= v[0] <= PW and 0 <= v[1] <= H)
    out += not (0 <= box[0] < box[2] <= PW and 0 <= box[1] < box[3] <= H)
    ex.checked('锚点都在地图里（不满足的条数）', out)
    # 导出层（pano / wrap / strip / pick / static）vs 直接拼
    for camX in (0, 160, 320):
        for t in (0.0, 1.25):
            want = Image.new('RGBA', (W, H), (0, 0, 0, 255))
            want.alpha_composite(R['sky'])
            o = int(math.floor(camX * CLOUD_K + t * CLOUD_VX)) % 640
            cl = R['clouds']
            want.alpha_composite(_tile(cl, 1280).crop((o, 0, o + W, cl.height)), (0, 0))
            want.alpha_composite(R['far'].crop((math.floor(camX * FAR_K), 0, math.floor(camX * FAR_K) + W, H)))
            for i, (y0, y1, k, vx) in enumerate(SEA_BANDS):
                o = int(math.floor(camX * k + t * vx)) % 640
                want.alpha_composite(_tile(R['sea'][i], 1280).crop((o, 0, o + W, y1 - y0)), (0, y0))
            want.alpha_composite(glitter_frame(t).crop((0, 0, W, H)))
            want.alpha_composite(wake_frame(t).crop((camX, 0, camX + W, H)))
            want.alpha_composite(near_full(0).crop((camX, 0, camX + W, H)))
            for fn in (radar_frame, flag_frame, rods_frame):
                want.alpha_composite(fn(t).crop((camX, 0, camX + W, H)))
            got = BJ.ref_render(st, ex.images, camX, t, dict(tarp=0), fg=False,
                                only={'static', 'wrap', 'pano', 'strip', 'pick'})
            m = np.ones((H, W), bool)
            ex.checked('游艇 camX=%d t=%.2f 导出 vs 直接拼（不含海鸥 / 前景）' % (camX, t),
                       _diff_strips(got, want, st, camX, t))
    ex.note('帆布框 lifeboat_box = %s' % list(box))


def _diff_strips(got, want, st, camX, t):
    """strip 在导出时按 box 裁过（box 外的像素本来就不进帧条），这里只要求 box 内一致 + 其他地方一致。"""
    return int((np.abs(np.asarray(got.convert('RGB'), np.int16) - np.asarray(want.convert('RGB'), np.int16)).max(-1) > 0).sum())


def _tile(im, w):
    out = A._new(w, im.height)
    for x in range(0, w, im.width):
        out.paste(im, (x, 0))
    return out


# ============================================================ 单独预览
def preview(camX, t=0.5, tarp=0):
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    o = int(math.floor(camX * CLOUD_K + t * CLOUD_VX)) % 640
    out.alpha_composite(_tile(R['clouds'], 1280).crop((o, 0, o + W, R['clouds'].height)))
    out.alpha_composite(R['far'].crop((math.floor(camX * FAR_K), 0, math.floor(camX * FAR_K) + W, H)))
    for i, (y0, y1, k, vx) in enumerate(SEA_BANDS):
        o = int(math.floor(camX * k + t * vx)) % 640
        out.alpha_composite(_tile(R['sea'][i], 1280).crop((o, 0, o + W, y1 - y0)), (0, y0))
    out.alpha_composite(glitter_frame(t))
    out.alpha_composite(wake_frame(t).crop((camX, 0, camX + W, H)))
    out.alpha_composite(near_full(tarp).crop((camX, 0, camX + W, H)))
    for fn in (radar_frame, flag_frame, rods_frame):
        out.alpha_composite(fn(t).crop((camX, 0, camX + W, H)))
    out.alpha_composite(R['rail'].crop((camX, 0, camX + W, H)))
    return out


if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch2', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        for tarp in (0, 1):
            preview(camX, 0.5, tarp).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
                os.path.join(od, 'yacht_deck_solo_%d_t%d.png' % (camX, tarp)))
    print('ok', build()['tarp_box'])
