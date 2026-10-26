# -*- coding: utf-8 -*-
r"""desert_highway —— 第5章：印巴边境的公路（地图 road_ch5，第 9 战段 1「命运之轮」追车）。上午，干热，尘土里的大平原。
2026-10-18 ch5-road 组按体验版精度重画（改前是 ch5_scenes.highway()：三座三角山 + 平涂沙地 + 两排虚线）。

地图 320 宽（镜头不动，整张图自己往左卷：所有横卷层都是 wrap + vx，引擎让 wrap 的速度乘 stage.state.speed，
state.speed = 0 时整张图停下；strip / clouds 层不乘，所以“会动的小东西”只放在不跟着地面走的地方：天上、热浪、扬尘）。
ground 160、可走带 152–168 = 三条车道（车轮着地的 y 152 / 160 / 168，每条道 7 行，正好在两条线中间）。
侧视平视，车往右开（往西开向巴基斯坦），所以画面左边是东：上午的太阳在左上，影子落在右下。
从远到近（屏幕 y）：
  y 0–98     上午的天（偏暖的蓝、地平线一层发白的尘霾）、左上的太阳；高处几缕卷云
  y 56–98    远山：两道褐紫色的山脉（后面一道更淡更紫），朝左的坡受光，山脚罩着热霾
  y 88–124   远处的平原：一片片干地 / 收过的田、土埂、几簇树、土坯村子、一座白墙绿顶的小清真寺、砖窑的高烟囱、
             水塔；地平线上一层海市蜃楼的“水面”在晃（heat strip）
  y 60–142   中景（wrap vx 160，960 循环）：干裂的平原、金合欢、刺灌木、四根水泥电线杆 + 下垂的电线；
             路边茶棚 dhaba（草顶、竹柱、泥墙、灶上的大铁壶、泥炉 tandoor、三张绳床 charpai——一张立着靠墙、
             一张上坐着喝茶的人、门口挂的零食串、招牌、水罐）、茶棚右边停着一辆刷满花纹的巴基斯坦货车
             （truck art：车头上高高的木雕“王冠”、彩色镶片、反光贴、三块画板、篷布、保险杠下一排链条铃铛流苏）；
             再往后：骆驼拉的平板车、一块褪色的手绘广告牌、白墙绿顶的路边小圣祠（绿旗、红旗）、一堆砖、几只山羊
  y 136–180  近景三车道（wrap vx 360，640 循环）：远侧碎石路肩（白色反光桩每 80 px 一根、一块白身黄顶的里程碑、
             干草、碎石、半截旧轮胎），柏油路面（骨料颗粒、补丁、沥青灌缝、裂缝、车辙油渍、路边吹上来的沙），
             两条实线路缘 + 两条白虚线（车道线一定清楚），虚线空档里的反光道钉；近侧碎石路肩
光：太阳在左上；物件左面亮、右面暗，影子往右下；远处一层层罩热霾，近处描 1 px 深色边。

图层（从后往前）：
  sky       static           320×180 上午的天 + 太阳 + 地平线尘霾
  clouds    wrap  640  vx 2    k 0      高处的卷云
  crows     clouds                     一小群乌鸦慢慢往左飞
  mountains wrap  640  vx 5    k 0.02   远山
  plain     wrap  640  vx 36   k 0.1    远处的平原 + 村子
  heat      strip 8 帧 @4 fps（screen）  地平线上的海市蜃楼 + 热浪
  eagle     strip 16 帧 @8 fps（screen） 远处平原上空盘旋的一只鹰
  mid       wrap  960  vx 160  k 0.45   中景（茶棚、货车、树、电线杆……）
  road      wrap  640  vx 360  k 1      三车道
  fg: dust  strip 8 帧 @8 fps（screen，key 'dust'）路面扬起的一层沙尘（半透明）

锚点：party_car [80,160]、lanes [152,160,168]、wheel_start [140,160]；
      另外导出：horizon 98、road_vx 360（近景路面的速度，剧情里的落石之类按它走就“贴”在路上）、
      lane_lines {far 148, mid1 156, mid2 164, near 172}（四条线的 y）。
key：dust（扬尘）；state.speed（引擎乘到所有 wrap 层上）。
单独运行：python -B tools\bg_new\desert_highway.py → tools\bg_new\_preview\ch5\after\desert_highway_solo.png
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
    key = 'bg_new_ch5_road_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'ch5_road_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
C = A._c4
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
ellipse, line, wrap_x, catenary = P.ellipse, P.line, P.wrap_x, P.catenary
haze, opaque, mottle = P.haze, P.opaque, P.mottle
frame_of = P.frame_of

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 320
GROUND = 160
WALK = (152, 168)
LANES = (152, 160, 168)
HZ = 98                         # 地平线
CLOUD_P, CLOUD_VX, CLOUD_K = 640, 2.0, 0.0
MTN_P, MTN_VX, MTN_K = 640, 5.0, 0.02
PLAIN_P, PLAIN_VX, PLAIN_K = 640, 36.0, 0.1
MID_P, MID_VX, MID_K = 960, 160.0, 0.45
ROAD_P, ROAD_VX = 640, 360.0
SHOULDER = 138                  # 远侧路肩上沿（近景层从这里往下不透明）
EDGE_FAR = 148                  # 远侧路缘线（147 淡、148 实）
DIVS = (156, 164)               # 两条白虚线
EDGE_NEAR = 172                 # 近侧路缘线（172–173）
ASPH = (147, 175)               # 柏油（含路缘线）
NEAR_SH = 176                   # 近侧路肩 176–179
DASH_P, DASH_L = 40, 18         # 虚线：每 40 px 一段，长 18
POST_P = 80                     # 反光桩间距
MID_BASE = 134                  # 中景物件大致的地面线
N_HEAT, FPS_HEAT = 8, 4.0
N_EAGLE, FPS_EAGLE = 16, 8.0
N_DUST, FPS_DUST = 8, 8.0

ANCHORS = dict(
    party_car=[80, 160],         # 众人的车（中间车道）
    lanes=list(LANES),           # 三条车道车轮着地的 y
    wheel_start=[140, 160],      # 命运之轮出现的位置
)

# ============================================================ 调色
SKY_STOPS = [(80, 136, 198), (104, 158, 210), (140, 182, 218), (180, 202, 216), (214, 214, 204), (234, 224, 200)]
HAZE = (230, 218, 196)          # 地平线的尘霾
SUN = (255, 246, 218)
INK = (58, 44, 40)
EARTH_HI = (230, 204, 152)
EARTH = (212, 180, 128)
EARTH_S = (190, 156, 108)
EARTH_D = (160, 124, 86)
EARTH_K = (124, 94, 66)
GRAVEL = [(120, 108, 96), (148, 134, 116), (170, 154, 130), (192, 176, 148), (214, 198, 168)]
ASPHALT = [(70, 68, 70), (84, 81, 82), (96, 92, 92), (108, 104, 102), (122, 117, 113)]
TAR = (62, 60, 64)                # 沥青灌缝：比路面暗一截但不发黑（车道里要平整）
PAINT = (240, 238, 226)
PAINT_D = (206, 204, 194)
STUD = (246, 196, 76)
WOOD_HI, WOOD, WOOD_D = (170, 122, 78), (128, 88, 56), (88, 60, 40)
LEAF = ((60, 82, 46), (84, 108, 56), (112, 134, 70), (146, 160, 90))


# ============================================================ 天空 / 卷云
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, HZ + 6), SKY_STOPS, bands=14)
    rect(ImageDraw.Draw(im), 0, HZ + 6, W - 1, H - 1, HAZE)
    A._glow(im, 44, 36, 58, 46, (255, 240, 206), 70, rings=6)
    A._glow(im, 44, 36, 20, 17, (255, 248, 226), 110, rings=3)
    d = ImageDraw.Draw(im)
    ellipse(d, 38, 30, 50, 42, SUN)
    ellipse(d, 40, 32, 48, 40, (255, 254, 244))
    # 地平线上一层尘霾：越往下越白（Bayer 抖动，不是平滑渐变）
    a = np.array(im).astype(np.float32)
    b = P.bayer(W, H)
    for y in range(HZ - 30, HZ + 6):
        u = (y - (HZ - 30)) / 36.0
        m = b[y] < u * 0.85
        a[y, m, :3] = a[y, m, :3] * 0.55 + np.array(HAZE, np.float32) * 0.45
    return P.img(a)


@lru_cache(maxsize=1)
def clouds_img():
    """640 循环：高处几缕被风拉长的卷云（1–2 px 的亮条，两头细、中间断开几处）+ 地平线上两朵热天的小积云（被山挡住下半）。"""
    im = A._new(CLOUD_P, 92)
    d = ImageDraw.Draw(im)
    for i in range(9):
        x0 = hrange(0, CLOUD_P, i, 11)
        y0 = hrange(10, 60, i, 12)
        L = int(hrange(40, 110, i, 13))
        slope = hrange(-0.06, 0.02, i, 14)
        for k in range(L):
            u = k / L
            th = math.sin(math.pi * u)
            if hash01(i, k // 5, 15) < 0.18:
                continue
            x = int(x0 + k) % CLOUD_P
            y = int(round(y0 + k * slope))
            c = mix((214, 228, 238), (248, 250, 250), th)
            px(d, x, y, c)
            if th > 0.55 and hash01(i, k, 16) < 0.7:
                px(d, x, y + 1, mix((196, 214, 230), (226, 236, 242), th))
            if th > 0.8 and hash01(i, k, 17) < 0.35:
                px(d, (x + 3) % CLOUD_P, y - 1, (236, 242, 246))
    pal = ((255, 252, 246), (240, 236, 228), (218, 214, 210), (200, 196, 198))
    for i, (cx, w) in enumerate(((150, 48), (470, 36))):
        cl = A._cloud_sprite(w, w * 0.4, 70 + i, pal)
        for dx in (-CLOUD_P, 0, CLOUD_P):
            paste(im, cl, int(cx + dx - cl.width / 2), 92 - cl.height)
    return im


CROWS = [(66, -7.0, 120.0), (58, -6.0, 300.0)]      # (y, vx, x0)：两小群乌鸦


@lru_cache(maxsize=1)
def crows_img():
    """一小群乌鸦（4 只，翅膀一上一下，错开一点）。"""
    g = A._new(26, 9)
    for i, (x, y, up) in enumerate(((0, 4, False), (7, 1, True), (13, 5, True), (19, 2, False))):
        g.alpha_composite(P.crow_img(up), (x, y))
    return g


# ============================================================ 远山（wrap 640）
@lru_cache(maxsize=1)
def mountains_img():
    a = np.zeros((H, MTN_P, 4), np.uint8)
    hb = P.hfield(MTN_P, 31, [(2, 16, 0.4), (3, 9, 1.9), (5, 6, 0.7), (9, 3, 2.2)], 7, 16) + 6
    P.ridge(a, HZ, hb, ((210, 184, 182), (188, 164, 172), (166, 146, 164), (228, 204, 198)), 31, HAZE, 0.42, 0.7)
    hf = P.hfield(MTN_P, 47, [(3, 10, 2.6), (4, 6, 0.3), (7, 5, 1.1), (13, 3, 0.2)], 6, 10) - 2
    P.ridge(a, HZ, hf, ((198, 160, 134), (172, 136, 122), (146, 114, 112), (216, 182, 150)), 47, HAZE, 0.22, 0.55,
           gully=0.8)
    im = P.img(a)
    return im


# ============================================================ 远处的平原 + 村子（wrap 640）
def _village(d, x, seed):
    """远处一个土坯村子：几间平顶泥房（矮、左面亮）、一两棵树、偶尔一个院墙。宽约 30。"""
    xx = x
    for k in range(int(hrange(4, 7, seed, 1))):
        w = int(hrange(4, 8, seed, k, 2))
        h = int(hrange(2, 5, seed, k, 3))
        col = mix([(206, 176, 140), (194, 162, 128), (214, 190, 156), (186, 150, 120)][k % 4], HAZE, 0.42)
        rect(d, xx, HZ - h, xx + w - 1, HZ, col)
        vl(d, xx, HZ - h, HZ, lt(col, 0.18))
        vl(d, xx + w - 1, HZ - h, HZ, dk(col, 0.86))
        hl(d, xx, xx + w - 1, HZ - h, lt(col, 0.25))
        if w > 5 and h > 2:
            px(d, xx + 2, HZ - h + 2, dk(col, 0.6))                  # 门 / 窗
        xx += w + int(hrange(0, 3, seed, k, 4))
        if hash01(seed, k, 5) < 0.4:                                   # 房子之间一棵树
            tx = xx + 1
            ty = HZ - int(hrange(5, 8, seed, k, 6))
            for (dx_, dy_, r) in ((0, 0, 3), (-2, 1, 2), (2, 1, 2)):
                ellipse(d, tx + dx_ - r, ty + dy_ - r + 1, tx + dx_ + r, ty + dy_ + r - 1, mix((92, 110, 72), HAZE, 0.4))
            px(d, tx - 1, ty - 1, mix((126, 140, 90), HAZE, 0.4))
            vl(d, tx, ty + 2, HZ, mix((96, 80, 64), HAZE, 0.4))
            xx += 4
    return xx


@lru_cache(maxsize=1)
def plain_img():
    a = np.zeros((H, PLAIN_P, 4), np.uint8)
    # 地面：从地平线（远、发白）到 y 128（近、偏黄），按行渐变 + 一条条横着的田块（透视压扁）
    nz = P.wnoise(PLAIN_P, H, 16, 61)
    fn = P.wnoise(PLAIN_P, H, 40, 62)
    b = P.bayer(PLAIN_P, H)
    stops = [(HZ, mix(EARTH_HI, HAZE, 0.62)), (HZ + 8, mix(EARTH, HAZE, 0.46)), (HZ + 18, mix(EARTH, HAZE, 0.32)),
             (HZ + 30, mix(EARTH_S, HAZE, 0.22))]
    for y in range(HZ, 132):
        for i in range(len(stops) - 1):
            if stops[i][0] <= y <= stops[i + 1][0]:
                base = mix(stops[i][1], stops[i + 1][1], (y - stops[i][0]) / max(1, stops[i + 1][0] - stops[i][0]))
                break
        else:
            base = stops[-1][1]
        dz = 0.5 * max(0.0, 1 - (y - HZ) / 30.0)
        for x in range(PLAIN_P):
            c = base
            f = fn[y, x]
            if f > 0.62:                                              # 收过的田（偏黄的茬地）
                c = mix((222, 200, 140), HAZE, 0.3 + dz)
            elif f < 0.3:                                             # 灌过水的地（偏灰绿）
                c = mix((176, 174, 124), HAZE, 0.3 + dz)
            n = nz[y, x]
            if n > 0.66 or (n > 0.6 and b[y, x] < 0.5):
                c = dk(c, 0.94)
            elif n < 0.32 or (n < 0.38 and b[y, x] < 0.5):
                c = lt(c, 0.06)
            a[y, x, :3] = c
            a[y, x, 3] = 255
    im = P.img(a)
    d = ImageDraw.Draw(im)
    # 土埂（田与田之间的一道道细线，越近越长）
    for i in range(70):
        y = HZ + 2 + int(hash01(i, 63) ** 1.4 * 28)
        x = int(hrange(0, PLAIN_P, i, 64))
        L = int(hrange(10, 40, i, 65) * (0.4 + (y - HZ) / 30))
        c = mix(EARTH_D, HAZE, 0.5 * max(0.0, 1 - (y - HZ) / 30.0) + 0.15)
        for k in range(L):
            px(d, (x + k) % PLAIN_P, y, c)
    # 一簇簇树（地平线上、田边）
    for i in range(16):
        x = int(hrange(0, PLAIN_P, i, 66))
        y = HZ + int(hrange(0, 10, i, 67))
        r = 2 + (y - HZ) // 4
        u = max(0.0, 1 - (y - HZ) / 24.0)
        cd, cm, ch = (mix(c, HAZE, 0.25 + 0.4 * u) for c in ((70, 86, 58), (96, 112, 70), (128, 140, 88)))
        def tree(xx, y=y, r=r, cd=cd, cm=cm, ch=ch, i=i):
            for k in range(3):
                ox = int(hrange(-r, r, i, k, 68))
                ellipse(d, xx + ox - r, y - 2 * r, xx + ox + r, y, cd)
                ellipse(d, xx + ox - r, y - 2 * r, xx + ox + r - 1, y - 1, cm)
                px(d, xx + ox - r // 2, y - 2 * r + 1, ch)
            vl(d, xx, y - 1, y, dk(cd, 0.8))
        wrap_x(tree, x, PLAIN_P, 20)
    # 村子（地平线上）
    for (x, sd) in ((20, 1), (150, 2), (300, 3), (520, 4)):
        _village(d, x, sd)
    # 小清真寺：白墙、绿圆顶、一根宣礼塔
    mx = 252
    wcol, gcol = mix((236, 232, 220), HAZE, 0.35), mix((92, 150, 110), HAZE, 0.35)
    rect(d, mx - 6, HZ - 5, mx + 6, HZ, wcol)
    vl(d, mx + 6, HZ - 5, HZ, dk(wcol, 0.85))
    ellipse(d, mx - 4, HZ - 10, mx + 4, HZ - 3, gcol)
    px(d, mx - 2, HZ - 9, lt(gcol, 0.3))
    vl(d, mx, HZ - 12, HZ - 11, mix((200, 180, 110), HAZE, 0.3))
    for k in range(-4, 5, 3):
        px(d, mx + k, HZ - 2, dk(wcol, 0.7))
    vl(d, mx + 9, HZ - 15, HZ, wcol)                                  # 宣礼塔
    vl(d, mx + 10, HZ - 15, HZ, dk(wcol, 0.86))
    hl(d, mx + 8, mx + 11, HZ - 11, dk(wcol, 0.9))
    px(d, mx + 9, HZ - 16, gcol)
    px(d, mx + 10, HZ - 16, gcol)
    px(d, mx + 9, HZ - 17, mix((200, 180, 110), HAZE, 0.3))
    # 砖窑：一圈矮墙 + 高烟囱 + 往右飘的淡烟
    kx = 412
    kcol = mix((168, 104, 84), HAZE, 0.4)
    rect(d, kx - 10, HZ - 3, kx + 10, HZ, kcol)
    hl(d, kx - 10, kx + 10, HZ - 3, lt(kcol, 0.2))
    for k in range(-9, 10, 3):
        px(d, kx + k, HZ - 1, dk(kcol, 0.8))
    rect(d, kx - 1, HZ - 24, kx + 1, HZ - 3, kcol)
    vl(d, kx - 1, HZ - 24, HZ - 3, lt(kcol, 0.2))
    vl(d, kx + 1, HZ - 24, HZ - 3, dk(kcol, 0.82))
    hl(d, kx - 2, kx + 2, HZ - 25, dk(kcol, 0.8))
    for k in range(40):                                               # 烟：一条往右上飘、越来越宽越来越淡的带
        u = k / 40.0
        sx = kx + 2 + k
        sy = HZ - 26 - int(u * 9 + math.sin(u * 7) * 1.5)
        th = 1 + int(u * 3)
        for j in range(th):
            if hash01(k, j, 69) < 0.85 - u * 0.5:
                px(d, sx % PLAIN_P, sy + j, mix((150, 140, 138), HAZE, 0.35 + u * 0.4))
    # 水塔（高脚、圆罐）
    tx = 586
    tcol = mix((206, 204, 198), HAZE, 0.35)
    for lx in (tx - 3, tx + 3):
        vl(d, lx, HZ - 12, HZ, dk(tcol, 0.8))
    for k in range(HZ - 11, HZ, 3):
        line(d, [(tx - 3, k), (tx + 3, k + 2)], dk(tcol, 0.85))
    ellipse(d, tx - 5, HZ - 18, tx + 5, HZ - 11, tcol)
    hl(d, tx - 4, tx + 4, HZ - 17, lt(tcol, 0.3))
    vl(d, tx + 4, HZ - 16, HZ - 13, dk(tcol, 0.82))
    # 高压线的铁塔（很远，两座）+ 线
    for bx in (96, 466):
        pc = mix((120, 116, 120), HAZE, 0.5)
        for yy in range(HZ - 16, HZ + 1):
            hw = 1 + (yy - (HZ - 16)) // 6
            px(d, bx - hw, yy, pc)
            px(d, bx + hw, yy, pc)
        hl(d, bx - 4, bx + 4, HZ - 14, pc)
        hl(d, bx - 3, bx + 3, HZ - 10, pc)
    for x in range(PLAIN_P):                                          # 两座塔之间的线（跨接缝）
        u = ((x - 96) % PLAIN_P) / 370.0
        if u <= 1.0:
            y = HZ - 14 + int(round(5 * 4 * u * (1 - u)))
            if x % 2 == 0:
                px(d, x, y, mix((110, 106, 112), HAZE, 0.5))
    return im


# ============================================================ 地平线的热浪 / 海市蜃楼（strip，screen）
HEAT_BOX = (0, HZ - 6, W, HZ + 12)
MIRAGES = [(48, 20, HZ + 3), (132, 26, HZ + 2), (214, 16, HZ + 4), (286, 22, HZ + 2)]     # (中心 x, 半宽, y)


@lru_cache(maxsize=None)
def _heat_f(f):
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    ph = math.tau * f / N_HEAT
    for i, (cx, hw, y0) in enumerate(MIRAGES):
        # 海市蜃楼：地面上一片晃动的“水”（反着天的颜色），上下三行，边上参差，宽度一呼一吸
        breathe = 0.78 + 0.22 * math.sin(ph + i * 1.7)
        for r in range(3):
            w = hw * breathe * (1 - r * 0.28)
            jit = math.sin(ph * 2 + i + r * 2.1) * 2
            x0 = int(round(cx - w + jit))
            x1 = int(round(cx + w + jit * 0.5))
            col = (206, 218, 224) if r == 1 else (196, 210, 220)
            for x in range(x0, x1 + 1):
                if hash01(i, r, x // 3, f, 71) < 0.86:
                    px(d, x, y0 + r, col)
            # 一条亮线 + 远处东西的倒影（几点深色，跟着晃）
            if r == 1:
                for x in range(x0 + 2, x1 - 1, 4):
                    if hash01(i, x, 72) < 0.5:
                        px(d, x + int(jit), y0 + r, (232, 236, 236))
            if r == 2:
                for k in range(3):
                    tx = int(cx + hrange(-hw * 0.6, hw * 0.6, i, k, 73) + jit)
                    px(d, tx, y0 + r, (150, 150, 140))
    # 热浪：地平线上方几道 1 px 的亮纹，左右扭动、时有时无
    for i in range(26):
        y = HZ - 1 - int(hash01(i, 74) * 5)
        x = int(hrange(0, W, i, 75))
        L = int(hrange(3, 9, i, 76))
        if (f + i) % 4 == 0:
            continue
        dx = int(round(2 * math.sin(ph + i * 0.9)))
        for k in range(L):
            if (k + f + i) % 3:
                px(d, x + dx + k, y, (236, 230, 214))
    return im


def heat_frame(t):
    return _heat_f(frame_of(t, N_HEAT, FPS_HEAT))


# ============================================================ 鹰（strip，screen）
EAGLE_C, EAGLE_R = (228, 64), (24, 7)
EAGLE_BOX = (EAGLE_C[0] - EAGLE_R[0] - 7, EAGLE_C[1] - EAGLE_R[1] - 4, EAGLE_C[0] + EAGLE_R[0] + 7,
             EAGLE_C[1] + EAGLE_R[1] + 7)


@lru_cache(maxsize=None)
def _eagle_f(f):
    """鹰顺时针绕一个扁椭圆盘旋（近大远小不画，太远了）：在圈的左右两头翅膀倾过来，绕到上面那段扇一下翅膀。"""
    im = A._new(W, H)
    ang = math.tau * f / N_EAGLE
    x = EAGLE_C[0] + EAGLE_R[0] * math.cos(ang)
    y = EAGLE_C[1] + EAGLE_R[1] * math.sin(ang)
    c = math.cos(ang)
    if c > 0.6:
        pose = 'bank_r'
    elif c < -0.6:
        pose = 'bank_l'
    elif f == N_EAGLE * 3 // 4:
        pose = 'up'
    else:
        pose = 'glide'
    im.alpha_composite(P.eagle_img(pose), (int(round(x)) - 5, int(round(y)) - 2))
    return im


def eagle_frame(t):
    return _eagle_f(frame_of(t, N_EAGLE, FPS_EAGLE))


# ============================================================ 中景（wrap 960）
def _mid_top():
    """中景地面上沿（起伏的矮土坡），可循环。"""
    xs = np.arange(MID_P, dtype=np.float32)
    y = 115 + 1.6 * np.sin(xs * 2 * math.pi * 3 / MID_P + 0.6) + 1.1 * np.sin(xs * 2 * math.pi * 11 / MID_P + 1.9) + \
        (P.wnoise(MID_P, 4, 24, 81)[1] - 0.5) * 4
    return np.round(y).astype(int)


def _mid_ground(a):
    """中景地面：后沿发白（远）、往前渐黄；大块的明暗斑只差一级（抖动只在斑块边上），不做满地的棋盘点——
    人物的上半身正好叠在这一带，地面要静。"""
    top = _mid_top()
    nz = P.wnoise(MID_P, H, 12, 82)
    big = P.wnoise(MID_P, H, 48, 83)
    b = P.bayer(MID_P, H)
    for x in range(MID_P):
        y0 = top[x]
        for y in range(y0, 144):
            u = (y - y0) / max(1.0, 143 - y0)
            base = mix(mix(EARTH_HI, HAZE, 0.3), EARTH, min(1.0, u * 1.6))
            n = nz[y, x] * 0.6 + big[y, x] * 0.4
            if n > 0.64 or (n > 0.6 and b[y, x] < 0.5):
                c = mix(base, EARTH_S, 0.55)
            elif n < 0.34 or (n < 0.38 and b[y, x] < 0.5):
                c = mix(base, EARTH_HI, 0.5)
            else:
                c = base
            a[y, x, :3] = c
            a[y, x, 3] = 255
        a[y0, x, :3] = mix(EARTH_HI, HAZE, 0.25)
    return top


def _cracks(d, x0, y0, w, h, seed):
    """一片干裂的泥地：不规则的多边形裂纹（深色细线），裂块中间亮一点。"""
    for i in range(int(w * h / 18)):
        x = x0 + hrange(0, w, seed, i, 1)
        y = y0 + hrange(0, h, seed, i, 2)
        L = hrange(2, 5, seed, i, 3)
        ang = hrange(0, math.pi, seed, i, 4)
        line(d, [(x, y), (x + math.cos(ang) * L, y + math.sin(ang) * L * 0.4)], EARTH_D)
    for i in range(int(w * h / 30)):
        px(d, int(x0 + hrange(0, w, seed, i, 5)), int(y0 + hrange(0, h, seed, i, 6)), EARTH_HI)


def _cast(im, pts, k=1.0):
    P.cast_shadow(im, pts, level=k)


def _pole(d, im, x, base, top):
    """水泥电线杆：上细下粗，左面亮；顶上一根横担 + 三个白瓷瓶；杆脚一小片影子。"""
    for y in range(top, base + 1):
        u = (y - top) / (base - top)
        w = 1 + (1 if u > 0.45 else 0)
        px(d, x, y, (196, 192, 184))
        px(d, x + 1, y, (150, 146, 140))
        if w > 1:
            px(d, x + 2, y, (128, 124, 120))
    rect(d, x - 6, top + 3, x + 8, top + 4, (104, 100, 98))
    hl(d, x - 6, x + 8, top + 3, (150, 146, 142))
    for ix in (x - 5, x + 1, x + 7):
        vl(d, ix, top + 1, top + 2, (236, 236, 230))
        px(d, ix, top, (210, 210, 204))
    line(d, [(x - 3, top + 5), (x, top + 9)], (110, 106, 102))       # 斜撑
    line(d, [(x + 5, top + 5), (x + 1, top + 9)], (110, 106, 102))
    for k in range(4):                                                # 杆上贴的小告示 / 编号
        px(d, x, top + 30 + k, (226, 214, 120) if k < 2 else (200, 60, 50))
    _cast(im, [(x + 2, base), (x + 18, base + 2), (x + 18, base + 3), (x, base + 1)], 0.7)


POLES = [60, 300, 540, 780]
POLE_TOP, POLE_BASE = 64, 136


def _wires(d):
    """两根电线：每两根杆子之间往下垂（最后一段跨接缝接到下一圈的第一根）。颜色往天色里混了一点——
    中景的线太黑会像一道横切画面的墨线；两根错开 3 px，不会糊成一根粗线。线上停着几只小鸟。"""
    xs = POLES + [POLES[0] + MID_P]
    for (ox, oy, sag, col) in ((-5, 0, 9, (92, 88, 94)), (7, 2, 11, (104, 100, 106))):
        for j, (a_, b_) in enumerate(zip(xs, xs[1:])):
            pts = catenary(a_ + ox, POLE_TOP + oy, b_ + ox, POLE_TOP + oy, sag)
            for (x, y) in pts:
                xx = int(round(x)) % MID_P
                px(d, xx, int(round(y)), col)
            if ox < 0 and j in (0, 2):                                 # 停在线上的小鸟（一排三五只）
                for k in range(3 + j):
                    u = 0.3 + k * 0.07
                    bx, by = pts[int(u * (len(pts) - 1))]
                    bx = int(round(bx)) % MID_P
                    by = int(round(by))
                    px(d, bx, by - 1, (56, 50, 54))
                    px(d, bx, by - 2, (56, 50, 54))
                    px(d, bx - 1, by - 2, (70, 64, 66))


def _charpai(d, x, y, L, seat=None, upright=False):
    """绳床 charpai：木框（深色）、四条矮腿、上面一层编的麻绳（浅色交叉纹）；upright = 竖着靠墙（看得见整张网）。"""
    if upright:
        rect(d, x, y - L, x + 5, y, WOOD_D)
        for yy in range(y - L + 1, y):
            for xx in range(x + 1, x + 5):
                px(d, xx, yy, (222, 196, 140) if (xx + yy) % 2 else (190, 160, 110))
        vl(d, x, y - L, y, WOOD)
        return
    rect(d, x, y - 4, x + L, y - 3, (214, 186, 130))                  # 绳面（略俯视，两行）
    for xx in range(x, x + L + 1):
        if (xx // 2) % 2:
            px(d, xx, y - 4, (190, 158, 104))
    hl(d, x, x + L, y - 2, WOOD)                                      # 侧框
    hl(d, x, x + L, y - 5, WOOD_HI)
    for lx in (x, x + L):
        vl(d, lx, y - 2, y, WOOD_D)
    if seat:
        seat(d)


def _man_sitting(d, x, y, shirt=(236, 232, 220)):
    """坐在绳床上喝茶的人（白色长衫 shalwar kameez、小圆帽），侧身朝左，手里一个小茶杯。9 px 高。"""
    rect(d, x, y - 7, x + 2, y - 2, shirt)                            # 身子
    vl(d, x + 2, y - 7, y - 2, dk(shirt, 0.82))
    hl(d, x - 2, x + 1, y - 2, dk(shirt, 0.9))                        # 盘着的腿
    hl(d, x - 2, x + 2, y - 1, dk(shirt, 0.78))
    rect(d, x, y - 10, x + 1, y - 8, (150, 104, 76))                  # 头
    px(d, x - 1, y - 9, (150, 104, 76))
    hl(d, x, x + 1, y - 11, (240, 240, 236))                          # 小圆帽
    px(d, x + 1, y - 8, (60, 50, 46))                                 # 胡子
    px(d, x - 1, y - 5, (150, 104, 76))                               # 手
    px(d, x - 2, y - 6, (236, 236, 228))                              # 茶杯


def _kettle_steam(d, x, y):
    """灶上的大铁壶冒的热气（静止的几缕，中景跟着地面卷，不能做 strip）。"""
    for k in range(9):
        u = k / 8.0
        sx = x + int(round(math.sin(u * 4 + 0.5) * 1.5 + u * 2))
        px(d, sx, y - k, mix((244, 240, 232), HAZE, u * 0.6))
        if k % 3 == 0:
            px(d, sx + 1, y - k, mix((230, 228, 222), HAZE, u * 0.6))


def draw_dhaba(im, x0):
    """路边茶棚（x0 = 左沿；地面 y 134）：草顶 + 竹柱 + 半截泥墙 + 灶 / 铁壶 / 泥炉 + 三张绳床 + 招牌 + 水罐。"""
    d = ImageDraw.Draw(im)
    base = 134
    # 后墙（泥抹的半截墙）+ 墙上的手绘字（色块）
    wall = (204, 168, 124)
    rect(d, x0 + 6, 117, x0 + 78, base, wall)
    mottle(im, (x0 + 6, 117, x0 + 78, base), wall, dk(wall, 0.92), lt(wall, 0.1), 901, cell=3, streaks=2)
    d = ImageDraw.Draw(im)
    hl(d, x0 + 6, x0 + 78, 117, lt(wall, 0.2))
    vl(d, x0 + 78, 117, base, dk(wall, 0.8))
    rect(d, x0 + 12, 121, x0 + 30, 126, (236, 232, 214))              # 墙上刷白的一块 + 红绿字
    for k in range(5):
        hl(d, x0 + 13 + k * 3, x0 + 14 + k * 3, 122 + (k % 2), (196, 52, 44))
        px(d, x0 + 14 + k * 3, 124, (52, 128, 70))
    hl(d, x0 + 13, x0 + 29, 125, (52, 128, 70))
    # 门洞（暗）+ 里面的货架
    rect(d, x0 + 54, 119, x0 + 66, base - 1, (62, 46, 40))
    for yy in (122, 126):
        hl(d, x0 + 55, x0 + 65, yy, (104, 80, 60))
        for xx in range(x0 + 55, x0 + 65, 2):
            px(d, xx, yy - 1, ((200, 70, 60), (230, 190, 70), (70, 120, 180), (230, 230, 220))[(xx + yy) % 4])
    # 草顶下面的阴影（墙上半截暗）
    P.mul_box(im, (x0 + 6, 117, x0 + 78, 120), P.SHADOW_MUL)
    d = ImageDraw.Draw(im)
    # 竹柱
    for cx in (x0 + 4, x0 + 30, x0 + 56, x0 + 80):
        vl(d, cx, 110, base, (190, 160, 104))
        vl(d, cx + 1, 110, base, (136, 108, 70))
        for yy in range(113, base, 6):                                # 竹节
            px(d, cx, yy, (150, 120, 76))
    # 草顶：一块略斜的厚草垫，上沿亮、下沿参差的草穗；底面暗
    roof_t = lambda x: 104 + (x - x0) * 0.03
    for x in range(x0 - 4, x0 + 88):
        yt = int(round(roof_t(x)))
        fringe = 112 + int(hash01(x, 902) * 3)
        for y in range(yt, fringe + 1):
            u = (y - yt) / max(1, fringe - yt)
            if y == yt:
                c = (232, 206, 140)
            elif u < 0.35:
                c = (210, 180, 112) if (x + y // 2) % 3 else (226, 198, 130)
            elif u < 0.8:
                c = (184, 152, 92) if (x + y) % 4 else (162, 130, 78)
            else:
                c = (140, 108, 64)
            px(d, x, y, c)
        if hash01(x, 903) < 0.3:                                      # 垂下来的长草穗
            px(d, x, fringe + 1, (150, 118, 70))
    for x in range(x0 - 2, x0 + 86, 5):                               # 草垫上一道道捆扎的绳
        vl(d, x, int(roof_t(x)) + 1, int(roof_t(x)) + 4, (150, 118, 72))
    # 门口挂的零食串（彩色小方块）+ 一盏马灯
    for i, hx in enumerate((x0 + 36, x0 + 42, x0 + 48)):
        for k in range(5):
            px(d, hx, 113 + k, ((220, 60, 70), (240, 200, 60), (70, 150, 210), (240, 120, 40))[(i + k) % 4])
    vl(d, x0 + 70, 113, 114, (60, 56, 56))
    rect(d, x0 + 69, 115, x0 + 71, 117, (240, 214, 120))
    px(d, x0 + 70, 116, (255, 246, 200))
    # 泥灶 + 大铁壶（左）、泥炉 tandoor（右）
    rect(d, x0 + 10, 129, x0 + 20, base, (176, 120, 88))
    hl(d, x0 + 10, x0 + 20, 129, (204, 150, 112))
    rect(d, x0 + 13, 131, x0 + 16, base, (70, 40, 36))                # 灶口
    px(d, x0 + 14, 132, (240, 150, 60))                               # 火
    px(d, x0 + 15, 133, (250, 200, 90))
    ellipse(d, x0 + 11, 123, x0 + 19, 129, (60, 58, 62))              # 铁壶
    hl(d, x0 + 13, x0 + 16, 124, (110, 108, 112))
    px(d, x0 + 12, 125, (96, 94, 98))
    line(d, [(x0 + 19, 125), (x0 + 22, 123)], (60, 58, 62))           # 壶嘴
    vl(d, x0 + 15, 121, 122, (60, 58, 62))
    _kettle_steam(d, x0 + 22, 121)
    rect(d, x0 + 68, 125, x0 + 75, base, (184, 120, 82))              # tandoor
    hl(d, x0 + 68, x0 + 75, 125, (214, 156, 112))
    vl(d, x0 + 75, 125, base, (150, 96, 66))
    hl(d, x0 + 69, x0 + 74, 126, (90, 54, 40))
    # 绳床：一张立着靠墙、一张上坐着人、一张空的在门口
    _charpai(d, x0 + 80, base, 16, upright=True)
    _charpai(d, x0 + 24, base, 16, seat=lambda dd: _man_sitting(dd, x0 + 31, base - 4))
    _charpai(d, x0 + 44, base, 14)
    rect(d, x0 + 48, base - 6, x0 + 49, base - 5, (236, 236, 230))     # 空床上两只茶杯
    rect(d, x0 + 52, base - 6, x0 + 53, base - 5, (236, 236, 230))
    # 水罐（三只陶罐放在架子上）
    for k, hx in enumerate((x0 - 6, x0 - 1)):
        ellipse(d, hx - 2, base - 7, hx + 2, base - 3, (176, 96, 66))
        px(d, hx - 1, base - 6, (214, 140, 100))
        hl(d, hx - 1, hx + 1, base - 8, (130, 70, 52))
    rect(d, x0 - 9, base - 3, x0 + 2, base - 2, WOOD)
    vl(d, x0 - 8, base - 2, base, WOOD_D)
    vl(d, x0 + 1, base - 2, base, WOOD_D)
    # 招牌（两根竹竿上一块绿底白字、红边的牌子，立在茶棚左前方）
    sx = x0 - 30
    for lx in (sx + 1, sx + 20):
        vl(d, lx, 108, base + 1, (180, 150, 96))
        vl(d, lx + 1, 108, base + 1, (130, 104, 66))
    rect(d, sx - 1, 104, sx + 23, 115, (196, 52, 44))
    rect(d, sx, 105, sx + 22, 114, (48, 120, 72))
    for k in range(6):
        y = 107 + (k % 2) * 3
        hl(d, sx + 2 + k * 3, sx + 3 + k * 3, y, (240, 240, 230))
        px(d, sx + 3 + k * 3, y + 1, (240, 240, 230))
    hl(d, sx + 3, sx + 19, 112, (240, 220, 120))
    px(d, sx + 20, 106, (240, 220, 120))
    # 地上：影子（往右下）+ 一条进茶棚的土路（浅色、两道车辙）
    _cast(im, [(x0 + 78, 117), (x0 + 92, 120), (x0 + 96, base + 2), (x0 + 78, base + 1)], 0.8)
    _cast(im, [(x0 + 88, 112), (x0 + 100, 114), (x0 + 100, 118), (x0 + 88, 116)], 0.6)
    d = ImageDraw.Draw(im)
    for x in range(x0 - 40, x0 + 100):
        if hash01(x, 904) < 0.55:
            px(d, x, base + 3, mix(EARTH_HI, EARTH, 0.4))
        if hash01(x, 905) < 0.4:
            px(d, x, base + 6, EARTH_S)


def truck_img():
    """巴基斯坦花车（truck art，朝右）：76×38。车头上高高的木雕“王冠”（taj，画着一只眼睛、镶小镜片）、
    彩绘车门、货厢三块画板（孔雀 / 雪山湖 / 玫瑰）、上下两道反光贴（菱形色块）、篷布盖着货（绳子交叉捆）、
    保险杠下一排链条 + 铃铛流苏、三个红轮毂、挡泥板上画着花。光从左上。"""
    w, h = 78, 40
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    gy = h - 2                                                       # 车轮着地
    # 车底的影子
    ellipse(d, 2, gy - 1, 76, gy + 1, (120, 92, 66))
    # 底盘
    hl(d, 4, 70, gy - 9, (44, 40, 44))
    hl(d, 4, 70, gy - 8, (32, 30, 34))
    # 油箱
    rect(d, 34, gy - 9, 42, gy - 5, (150, 150, 156))
    hl(d, 34, 42, gy - 9, (210, 210, 214))
    hl(d, 34, 42, gy - 5, (96, 96, 102))
    # 货厢
    x0, x1, yt, yb = 2, 46, 12, gy - 10
    rect(d, x0, yt, x1, yb, (196, 40, 52))
    hl(d, x0, x1, yt, (240, 200, 70))                                # 顶上雕花木条（金）
    hl(d, x0, x1, yt + 1, (200, 150, 50))
    for x in range(x0 + 1, x1, 2):                                    # 一排小镜片
        px(d, x, yt, (255, 255, 236) if x % 4 == 1 else (240, 200, 70))
    for x in range(x0, x1 + 1):                                       # 上沿一道花边（红底白点）
        px(d, x, yt + 2, (196, 40, 52))
        if x % 3 == 0:
            px(d, x, yt + 2, (250, 240, 230))
    pals = [((40, 110, 180), (60, 160, 120), (240, 200, 60)), ((120, 190, 230), (250, 250, 250), (70, 140, 70)),
            ((250, 230, 210), (220, 60, 90), (60, 130, 70))]
    for k in range(3):                                                # 三块画板
        bx0 = x0 + 2 + k * 15
        bx1 = bx0 + 12
        by0, by1 = yt + 4, yb - 4
        rect(d, bx0 - 1, by0 - 1, bx1 + 1, by1 + 1, (250, 180, 40))
        rect(d, bx0, by0, bx1, by1, pals[k][0])
        if k == 0:                                                    # 孔雀：蓝身子 + 开屏的尾羽点
            for j in range(5):
                px(d, bx0 + 3 + j * 2, by0 + 1 + (j % 2), (60, 170, 120))
                px(d, bx0 + 3 + j * 2, by0 + 2 + (j % 2), (240, 200, 60))
            rect(d, bx0 + 5, by0 + 4, bx0 + 7, by1 - 1, (30, 70, 160))
            px(d, bx0 + 6, by0 + 3, (30, 70, 160))
        elif k == 1:                                                  # 雪山 + 湖
            for j in range(6):
                hl(d, bx0 + 6 - j, bx0 + 6 + j, by0 + 1 + j, (236, 240, 244) if j < 2 else (110, 130, 150))
            hl(d, bx0, bx1, by1 - 1, (60, 140, 190))
            hl(d, bx0, bx1, by1, (70, 140, 70))
        else:                                                         # 一束玫瑰
            for (rx, ry) in ((3, 2), (6, 1), (9, 2), (4, 4), (8, 4)):
                px(d, bx0 + rx, by0 + ry, (220, 50, 80))
                px(d, bx0 + rx + 1, by0 + ry, (250, 120, 140))
            vl(d, bx0 + 6, by0 + 5, by1, (60, 130, 70))
            px(d, bx0 + 5, by1 - 1, (60, 130, 70))
            px(d, bx0 + 7, by1 - 2, (60, 130, 70))
    for x in range(x0, x1 + 1):                                       # 下面一道反光贴（菱形色块）
        c = ((240, 60, 60), (60, 200, 120), (60, 140, 240), (240, 230, 120), (230, 230, 240))[(x // 3) % 5]
        px(d, x, yb - 2, c)
        if x % 3 == 1:
            px(d, x, yb - 1, c)
            px(d, x, yb - 3, c)
    hl(d, x0, x1, yb, (110, 30, 36))                                  # 货厢底边（暗）
    vl(d, x0, yt, yb, (230, 90, 96))                                  # 左沿受光
    vl(d, x1, yt, yb, (130, 26, 34))
    # 篷布（蓝，鼓起来）+ 交叉的绳子
    for x in range(x0 + 1, x1):
        top = yt - 2 - int(round(5 * math.sin(math.pi * (x - x0) / (x1 - x0)) ** 0.6)) - (1 if hash01(x // 4, 906) < 0.3 else 0)
        for y in range(top, yt):
            c = (66, 104, 164) if (x + y) % 7 else (52, 86, 140)
            if y == top:
                c = (110, 150, 206)
            px(d, x, y, c)
    for k in range(5):
        cx = x0 + 4 + k * 9
        line(d, [(cx - 4, yt - 1), (cx + 4, yt - 6)], (222, 204, 160))
        line(d, [(cx - 4, yt - 6), (cx + 4, yt - 1)], (196, 178, 136))
    # 驾驶室
    c0, c1 = 48, 62
    rect(d, c0, 15, c1, yb + 1, (40, 120, 90))                        # 车门（绿底）
    vl(d, c0, 15, yb + 1, (90, 170, 130))
    rect(d, c0 + 2, 16, c1 - 3, 21, (36, 54, 84))                     # 侧窗
    hl(d, c0 + 2, c1 - 3, 16, (120, 160, 200))
    px(d, c0 + 3, 17, (200, 220, 240))
    for (fx, fy, fc) in ((c0 + 4, 24, (250, 210, 60)), (c0 + 8, 25, (230, 70, 80)), (c0 + 11, 23, (250, 250, 250))):
        px(d, fx, fy, fc)                                             # 车门上的花
        px(d, fx + 1, fy, fc)
        px(d, fx, fy + 1, dk(fc, 0.8))
    hl(d, c0 + 2, c1 - 2, yb - 2, (240, 200, 70))                     # 金色腰线
    # 车鼻子（贝德福德的短车头）+ 格栅 + 大灯
    rect(d, c1 + 1, 21, c1 + 8, yb + 1, (230, 190, 50))
    hl(d, c1 + 1, c1 + 7, 21, (250, 230, 120))
    vl(d, c1 + 8, 22, yb + 1, (170, 130, 30))
    for yy in range(23, yb, 2):
        hl(d, c1 + 5, c1 + 7, yy, (200, 200, 206))
    px(d, c1 + 7, 22, (255, 250, 210))
    px(d, c1 + 8, 23, (255, 250, 210))
    # 车头上的“王冠”：拱形木板（深红底、金边、中间一只眼睛、镶小镜片）
    for y in range(1, 15):
        u = (y - 1) / 13.0
        hw = int(round(4 + 6 * min(1.0, u * 1.8)))
        cx = 56
        hl(d, cx - hw, cx + hw, y, (150, 30, 60))
        px(d, cx - hw, y, (250, 200, 70))
        px(d, cx + hw, y, (190, 140, 40))
    px(d, 56, 0, (250, 220, 90))
    for (ex, ey) in ((53, 7), (59, 7)):
        pass
    hl(d, 53, 59, 7, (250, 250, 240))                                 # 眼睛
    px(d, 56, 7, (30, 30, 40))
    px(d, 55, 7, (60, 140, 200))
    hl(d, 54, 58, 6, (250, 200, 70))
    hl(d, 54, 58, 8, (250, 200, 70))
    for (mx, my) in ((50, 11), (62, 11), (56, 3), (52, 13), (60, 13), (56, 11)):
        px(d, mx, my, (255, 255, 240))                                # 小镜片
    hl(d, 47, 65, 14, (240, 200, 70))
    # 后视镜
    vl(d, 66, 16, 19, (60, 60, 64))
    rect(d, 67, 15, 68, 18, (200, 210, 220))
    # 保险杠 + 链条铃铛流苏
    hl(d, c1 - 2, c1 + 10, yb + 2, (210, 210, 216))
    hl(d, c1 - 2, c1 + 10, yb + 3, (140, 140, 146))
    for k, x in enumerate(range(c1 - 1, c1 + 10, 2)):
        L = 2 + (k % 3)
        vl(d, x, yb + 4, yb + 3 + L, (180, 160, 120))
        px(d, x, yb + 4 + L, (250, 220, 90) if k % 2 else (230, 230, 236))
    # 挡泥板（画着花）
    for (mx, mc) in ((5, (200, 40, 50)), (28, (40, 110, 180))):
        rect(d, mx, gy - 8, mx + 2, gy - 1, mc)
        px(d, mx + 1, gy - 6, (250, 240, 200))
        px(d, mx + 1, gy - 3, (250, 220, 80))
    # 车轮（两个后轮、一个前轮）
    for wx in (14, 22, 60):
        ellipse(d, wx - 4, gy - 8, wx + 4, gy, (38, 34, 38))
        ellipse(d, wx - 2, gy - 6, wx + 2, gy - 2, (200, 50, 50))
        px(d, wx - 1, gy - 5, (250, 140, 120))
        px(d, wx, gy - 4, (240, 220, 120))
        hl(d, wx - 3, wx + 1, gy - 8, (70, 66, 70))
    return im


def camel_cart(d, im, x, base):
    """骆驼拉的平板车（朝左歇着）：骆驼站着低头、脖子上挂彩色流苏；木板车两个大轮子，车上一捆干草，车夫坐在草上。"""
    cc = (196, 156, 110)
    cd_ = (160, 120, 82)
    # 骆驼身子（驼峰）
    ellipse(d, x + 4, base - 16, x + 18, base - 9, cc)
    ellipse(d, x + 8, base - 19, x + 14, base - 13, cc)               # 驼峰
    hl(d, x + 9, x + 12, base - 19, lt(cc, 0.2))
    hl(d, x + 5, x + 17, base - 9, cd_)
    # 脖子 + 头（往左前低着）
    line(d, [(x + 5, base - 13), (x + 1, base - 15), (x - 1, base - 18)], cc, 2)
    rect(d, x - 5, base - 19, x - 1, base - 17, cc)
    px(d, x - 5, base - 17, cd_)
    px(d, x - 3, base - 19, (60, 46, 40))                             # 眼
    for k in range(3):                                                # 脖子上的流苏
        px(d, x + 2 + k, base - 13 + k % 2, ((220, 60, 60), (240, 200, 60), (60, 140, 220))[k])
    # 腿
    for lx in (x + 6, x + 8, x + 15, x + 17):
        vl(d, lx, base - 9, base, cd_ if lx % 2 else cc)
    # 车辕 + 平板车 + 大轮子
    line(d, [(x + 12, base - 12), (x + 22, base - 8)], WOOD_D)
    rect(d, x + 20, base - 9, x + 40, base - 7, WOOD)
    hl(d, x + 20, x + 40, base - 9, WOOD_HI)
    ellipse(d, x + 26, base - 9, x + 34, base - 1, (90, 66, 46))
    ellipse(d, x + 28, base - 7, x + 32, base - 3, (150, 116, 80))
    px(d, x + 30, base - 5, (70, 50, 36))
    for (sx, sy) in ((30, -8), (30, -2), (27, -5), (33, -5)):
        px(d, x + sx, base + sy, (110, 80, 56))
    # 干草堆 + 车夫
    for xx in range(x + 21, x + 40):
        top = base - 13 - int(round(3 * math.sin(math.pi * (xx - x - 21) / 19)))
        for yy in range(top, base - 9):
            px(d, xx, yy, (226, 196, 120) if (xx + yy) % 3 else (196, 164, 96))
        px(d, xx, top, (240, 216, 150))
    rect(d, x + 30, base - 21, x + 32, base - 15, (226, 222, 210))   # 车夫（白衣）
    rect(d, x + 30, base - 24, x + 31, base - 22, (140, 98, 72))
    hl(d, x + 29, x + 32, base - 25, (200, 70, 60))                   # 头巾
    _cast(im, [(x + 18, base - 1), (x + 46, base), (x + 48, base + 2), (x + 16, base + 1)], 0.7)


def billboard(d, im, x, base):
    """一块褪色的手绘广告牌（两条铁腿、木框；画面：一个笑脸 + 一瓶食用油 + 一行字的色块；左上角掉漆、底下锈迹）。"""
    for lx in (x + 4, x + 26):
        vl(d, lx, base - 22, base, (90, 86, 90))
        vl(d, lx + 1, base - 22, base, (60, 58, 62))
    rect(d, x, base - 38, x + 31, base - 22, (224, 214, 188))
    rect(d, x + 1, base - 37, x + 30, base - 23, (232, 196, 120))
    ellipse(d, x + 3, base - 36, x + 12, base - 27, (220, 170, 130))  # 笑脸
    px(d, x + 6, base - 33, (60, 40, 40))
    px(d, x + 9, base - 33, (60, 40, 40))
    hl(d, x + 6, x + 9, base - 30, (180, 70, 60))
    hl(d, x + 3, x + 12, base - 36, (60, 40, 40))                     # 头发
    rect(d, x + 22, base - 36, x + 26, base - 27, (220, 200, 80))     # 油瓶
    rect(d, x + 23, base - 38, x + 25, base - 37, (200, 60, 50))
    hl(d, x + 22, x + 26, base - 32, (60, 140, 80))
    for k in range(5):                                                # 一行字
        hl(d, x + 3 + k * 5, x + 6 + k * 5, base - 25, (170, 50, 46))
    for k in range(6):                                                # 掉漆 / 锈
        px(d, x + 1 + k, base - 37 + k // 2, (224, 214, 188))
        vl(d, x + 8 + k * 4, base - 23, base - 22 + (k % 3), (150, 96, 70))
    hl(d, x, x + 31, base - 38, (246, 238, 214))
    vl(d, x + 31, base - 38, base - 22, (150, 140, 120))
    _cast(im, [(x + 32, base - 30), (x + 40, base - 28), (x + 40, base - 26), (x + 32, base - 24)], 0.5)


def shrine(d, im, x, base):
    """路边的小圣祠（mazar）：刷白的小方屋、绿色小圆顶、门上一道绿边；旁边竹竿上挑着绿旗、红旗（静止的飘带形）。"""
    wcol = (238, 234, 222)
    rect(d, x, base - 10, x + 11, base, wcol)
    vl(d, x + 11, base - 10, base, dk(wcol, 0.82))
    hl(d, x, x + 11, base - 10, (250, 248, 240))
    rect(d, x + 4, base - 6, x + 7, base, (60, 90, 70))
    hl(d, x + 3, x + 8, base - 7, (70, 150, 100))
    ellipse(d, x + 2, base - 16, x + 9, base - 9, (70, 150, 100))
    px(d, x + 4, base - 15, (130, 200, 150))
    vl(d, x + 5, base - 19, base - 16, (220, 190, 90))
    for (fx, fc, top) in ((x - 4, (60, 150, 90), base - 26), (x + 15, (200, 50, 50), base - 22)):
        vl(d, fx, top, base, (180, 150, 100))
        for k in range(6):                                            # 旗面（三角飘带，往右）
            vl(d, fx + 1 + k, top + k // 3, top + 4 - k // 2, fc)
        px(d, fx + 1, top, lt(fc, 0.3))
    _cast(im, [(x + 11, base - 10), (x + 18, base - 8), (x + 18, base + 1), (x + 11, base)], 0.7)


def goat(d, x, y, col, facing=-1):
    """小山羊（6×4）。"""
    rect(d, x, y - 3, x + 3, y - 2, col)
    px(d, x + (-1 if facing < 0 else 4), y - 4, col)
    px(d, x + (-1 if facing < 0 else 4), y - 3, dk(col, 0.8))
    for lx in (x, x + 3):
        vl(d, lx, y - 1, y, dk(col, 0.7))
    px(d, x + (4 if facing < 0 else -1), y - 3, dk(col, 0.85))


def tyre_stall(d, im, x, base):
    """补胎摊（puncture）：两根木杆撑一块生锈的铁皮棚、棚边吊着一只旧轮胎当招牌、地上摞着几只旧胎、
    一台小气泵（红漆）、一个蹲着补胎的人。"""
    for lx in (x + 2, x + 24):
        vl(d, lx, base - 18, base, WOOD_D)
        vl(d, lx - 1, base - 18, base, WOOD)
    for xx in range(x - 1, x + 28):                                   # 铁皮棚（波纹 + 锈）
        y = base - 19 - (xx - x) // 12
        c = (150, 146, 140) if xx % 2 else (124, 120, 118)
        if hash01(xx, 951) < 0.3:
            c = (166, 104, 70)
        px(d, xx, y, c)
        px(d, xx, y + 1, dk(c, 0.75))
    ellipse(d, x + 26, base - 16, x + 32, base - 10, (40, 38, 42))    # 吊着的旧轮胎
    ellipse(d, x + 28, base - 14, x + 30, base - 12, mix(EARTH, HAZE, 0.2))
    vl(d, x + 29, base - 18, base - 16, (60, 58, 60))
    for k in range(4):                                                # 摞着的旧胎
        ellipse(d, x + 5, base - 3 - k * 2, x + 13, base - k * 2, (44, 42, 46))
        hl(d, x + 7, x + 11, base - 3 - k * 2, (78, 76, 80))
    rect(d, x + 15, base - 5, x + 20, base, (196, 52, 44))            # 气泵
    hl(d, x + 15, x + 20, base - 5, (230, 96, 80))
    px(d, x + 19, base - 4, (230, 230, 220))
    line(d, [(x + 20, base - 2), (x + 23, base - 1), (x + 25, base - 2)], (40, 40, 44))
    rect(d, x + 24, base - 5, x + 26, base - 1, (90, 110, 150))       # 蹲着的人（蓝衣）
    rect(d, x + 24, base - 8, x + 25, base - 6, (150, 104, 76))
    hl(d, x + 23, x + 26, base - 9, (226, 222, 210))
    P.cast_shadow(im, [(x + 28, base - 18), (x + 40, base - 16), (x + 40, base + 1), (x + 26, base)], level=0.7)


def shepherd(d, x, base):
    """放羊的人：头巾、长衫、肩上一根长棍（11 px 高）。"""
    rect(d, x, base - 8, x + 2, base - 2, (196, 178, 150))
    vl(d, x + 2, base - 8, base - 2, (160, 144, 120))
    vl(d, x, base - 1, base, (96, 74, 60))
    vl(d, x + 2, base - 1, base, (96, 74, 60))
    rect(d, x, base - 11, x + 1, base - 9, (150, 104, 76))
    hl(d, x - 1, x + 2, base - 12, (236, 232, 222))
    line(d, [(x - 2, base + 0), (x + 4, base - 13)], (120, 90, 60))


def bricks(d, x, base):
    """一堆码起来的红砖（窑里出来的）。"""
    for r in range(4):
        for k in range(6 - r):
            bx = x + r + k * 3
            by = base - 1 - r * 2
            hl(d, bx, bx + 2, by, (178, 86, 64) if (k + r) % 2 else (196, 104, 76))
            px(d, bx + 2, by, (140, 64, 50))
            hl(d, bx, bx + 2, by - 1, (210, 128, 96))


@lru_cache(maxsize=1)
def mid_img():
    a = np.zeros((H, MID_P, 4), np.uint8)
    top = _mid_ground(a)
    im = P.img(a)
    d = ImageDraw.Draw(im)
    # 干裂的泥地（几片）、小石子、干草
    for (cx, cy, w, h, sd) in ((40, 124, 50, 8, 1), (380, 126, 60, 7, 2), (610, 122, 44, 8, 3), (860, 125, 50, 7, 4)):
        _cracks(d, cx, cy, w, h, 910 + sd)
    for i in range(160):
        x = int(hrange(0, MID_P, i, 911))
        y = int(hrange(top[x] + 3, 141, i, 912))
        c = (EARTH_D, EARTH_K, EARTH_HI)[i % 3]
        px(d, x, y, c)
        if i % 3 == 0:
            px(d, (x + 1) % MID_P, y, EARTH_HI)
    for i in range(70):
        x = int(hrange(0, MID_P, i, 913))
        y = int(hrange(top[x] + 6, 140, i, 914))
        P.grass_tuft(d, x, y, int(hrange(2, 5, i, 915)), 916 + i)
    # 远一点的刺灌木（在中景地面的后沿，淡）
    for i in range(14):
        x = int(hrange(0, MID_P, i, 917))
        sw = int(hrange(6, 12, i, 918))
        wrap_x(lambda xx, i=i, sw=sw: P.shrub(d, xx, top[xx % MID_P] + 4, sw, 5, 920 + i,
                                              pal=tuple(mix(c, HAZE, 0.3) for c in
                                                        ((92, 96, 58), (124, 124, 70), (158, 150, 88), (186, 174, 110)))),
               x, MID_P, 20)
    # 金合欢（几棵大小不一）+ 影子
    def tree_shadow(xx, base, w):
        P.cast_shadow(im, [(xx, base), (xx + w * 0.9, base + 1), (xx + w * 0.8, base + 3), (xx - 2, base + 2)], level=0.7)
    for (tx, base, th, tw, sd) in ((140, 128, 40, 46, 1), (430, 124, 30, 34, 2), (650, 131, 46, 56, 3),
                                   (900, 122, 26, 28, 4), (560, 120, 20, 22, 5)):
        wrap_x(lambda xx, base=base, th=th, tw=tw, sd=sd: P.acacia(d, xx, base, th, tw, 930 + sd, leaf=LEAF,
                                                                  shadow=tree_shadow), tx, MID_P, 40)
        d = ImageDraw.Draw(im)
    # 近一点的灌木
    for i, (x, w, h) in enumerate(((20, 14, 7), (250, 10, 5), (500, 12, 6), (720, 16, 7), (930, 10, 5))):
        wrap_x(lambda xx, w=w, h=h, i=i: P.shrub(d, xx, 138, w, h, 940 + i), x, MID_P, 20)
    # 茶棚 + 货车
    draw_dhaba(im, 196)
    d = ImageDraw.Draw(im)
    tr = truck_img()
    paste(im, tr, 286, 137 - tr.height + 1)
    P.cast_shadow(im, [(332, 120), (372, 126), (370, 137), (330, 136)], level=0.6)
    d = ImageDraw.Draw(im)
    # 骆驼车、广告牌、小圣祠、砖堆、山羊
    camel_cart(d, im, 470, 134)
    d = ImageDraw.Draw(im)
    billboard(d, im, 586, 132)
    d = ImageDraw.Draw(im)
    shrine(d, im, 740, 130)
    d = ImageDraw.Draw(im)
    tyre_stall(d, im, 362, 135)
    d = ImageDraw.Draw(im)
    bricks(d, 846, 136)
    for (gx, gy, gc, fc) in ((770, 133, (236, 230, 220), -1), (782, 135, (90, 70, 60), 1), (796, 132, (200, 170, 130), -1),
                             (790, 129, (236, 230, 220), 1)):
        goat(d, gx, gy, gc, fc)
    shepherd(d, 808, 134)
    # 电线杆 + 电线（最后画，在所有东西前面）
    for x in POLES:
        _pole(d, im, x, POLE_BASE, POLE_TOP)
        d = ImageDraw.Draw(im)
    _wires(d)
    # 中景的里程碑（小）
    for mx in (110, 590 + 60):
        rect(d, mx, 131, mx + 3, 136, (236, 234, 226))
        hl(d, mx, mx + 3, 130, (236, 196, 60))
        px(d, mx + 1, 133, (60, 60, 60))
        vl(d, mx + 3, 131, 136, (196, 194, 186))
    # 整层罩一点热霾（0.1）+ 越往后越多：中景正好在车 / 人物的上半身后面，压低对比、让人物跳出来
    im = haze(im, np.clip(0.1 + (140 - np.arange(H, dtype=np.float32)[:, None]) / 120.0 * 0.2, 0.1, 0.3), HAZE)
    return opaque(im)


# ============================================================ 近景：三车道（wrap 640）
def _asphalt():
    """柏油底色（色阶图）：远的几行亮一点（发灰）、每条道中间一行车辙油渍暗一级，噪声 ±1 级 + 稀疏的骨料颗粒。"""
    nz = P.wnoise(ROAD_P, H, 8, 101)
    big = P.wnoise(ROAD_P, H, 64, 102)
    b = P.bayer(ROAD_P, H)
    rng = np.random.default_rng(103)
    g = rng.random((H, ROAD_P))
    L = np.zeros((H, ROAD_P), int)
    for y in range(ASPH[0], ASPH[1] + 1):
        lev = 2.0 + (0.6 if y < 152 else 0.0) - (0.4 if y > 170 else 0.0)
        for lc in LANES:                                              # 车辙中间那一行（油渍）
            if y == lc:
                lev -= 0.7
            if y in (lc - 2, lc + 2):                                # 轮迹磨亮
                lev += 0.35
        row = lev + (nz[y] - 0.5) * 1.2 + (big[y] - 0.5) * 0.8
        L[y] = np.floor(row + 0.5 + (b[y] - 0.5) * 0.8).astype(int)
    L[g < 0.03] -= 1
    L[g > 0.975] += 2                                                 # 骨料里的白石子
    return np.clip(L, 0, len(ASPHALT) - 1)


@lru_cache(maxsize=1)
def road_img():
    a = np.zeros((H, ROAD_P, 4), np.uint8)
    # 远侧碎石路肩（138–146）：上沿起伏的干草边，往下渐暗
    gz = P.wnoise(ROAD_P, H, 6, 104)
    b = P.bayer(ROAD_P, H)
    edge = (SHOULDER + (P.wnoise(ROAD_P, 4, 10, 105)[1] - 0.5) * 3).round().astype(int)
    for x in range(ROAD_P):
        for y in range(edge[x], ASPH[0]):
            u = (y - edge[x]) / max(1, ASPH[0] - edge[x])
            lev = 3 - u * 1.2 + (gz[y, x] - 0.5) * 2.4
            a[y, x, :3] = GRAVEL[int(np.clip(np.floor(lev + 0.5 + (b[y, x] - 0.5) * 0.9), 0, 4))]
            a[y, x, 3] = 255
        a[edge[x], x, :3] = GRAVEL[4]
    # 柏油
    L = _asphalt()
    pal = np.array(ASPHALT, np.uint8)
    a[ASPH[0]:ASPH[1] + 1, :, :3] = pal[L[ASPH[0]:ASPH[1] + 1]]
    a[ASPH[0]:ASPH[1] + 1, :, 3] = 255
    # 近侧碎石路肩（176–179）
    for x in range(ROAD_P):
        for y in range(NEAR_SH, H):
            lev = 2 + (gz[y, x] - 0.5) * 2.6 - (y - NEAR_SH) * 0.3
            a[y, x, :3] = GRAVEL[int(np.clip(np.floor(lev + 0.5 + (b[y, x] - 0.5) * 0.9), 0, 4))]
            a[y, x, 3] = 255
        a[NEAR_SH, x, :3] = GRAVEL[1]                                  # 柏油边上一道暗（路面比路肩高一点）
    im = P.img(a)
    d = ImageDraw.Draw(im)
    # 补丁（新补的沥青：更黑、更平，边上一圈亮线）
    for (x0, y0, w, h) in ((60, 157, 46, 7), (300, 149, 30, 6), (470, 165, 60, 6), (560, 157, 22, 7)):
        rect(d, x0, y0, x0 + w, y0 + h - 1, (78, 76, 78))
        for k in range(int(w * h / 6)):
            px(d, x0 + int(hrange(0, w, x0, k, 1)), y0 + int(hrange(0, h, x0, k, 2)), (88, 86, 88))
        hl(d, x0, x0 + w, y0, (104, 100, 98))
        vl(d, x0 + w, y0, y0 + h - 1, (66, 64, 68))
    # 沥青灌缝（黑色弯弯的“沥青蛇”）+ 裂缝
    for (x0, y0, L_, sd) in ((20, 151, 70, 1), (210, 169, 90, 2), (380, 159, 50, 3), (520, 150, 80, 4), (150, 166, 40, 5)):
        y = y0
        for k in range(L_):
            if hash01(sd, k, 106) < 0.12:
                y += 1 if hash01(sd, k, 107) < 0.5 else -1
                y = max(ASPH[0] + 1, min(ASPH[1] - 1, y))
            if y in DIVS or y == EDGE_NEAR or y == EDGE_FAR:
                continue
            px(d, (x0 + k) % ROAD_P, y, TAR)
    for (x0, y0, sd) in ((120, 157, 1), (250, 149, 2), (440, 165, 3), (600, 157, 4), (330, 165, 5)):
        x = x0
        for y in range(y0, y0 + 6):                                   # 横向的短裂缝（斜一点）
            if y in DIVS:
                continue
            px(d, x % ROAD_P, y, ASPHALT[0])
            x += 1 if hash01(sd, y, 108) < 0.4 else 0
    # 路边吹上来的沙（远侧 147–150、近侧 173–175 的抖动沙色）
    sz = P.wnoise(ROAD_P, H, 20, 109)
    for x in range(ROAD_P):
        for y in (149, 150, 151, 174, 175):
            v = sz[y, x] + (0.15 if y in (149, 175) else 0.0)
            if v > 0.62 and b[y, x] < (v - 0.55) * 2.2:
                px(d, x, y, (176, 156, 124) if y < 160 else (164, 146, 118))
    # 路缘实线 + 虚线
    for x in range(ROAD_P):
        px(d, x, EDGE_FAR - 1, mix(PAINT_D, ASPHALT[3], 0.35))
        px(d, x, EDGE_FAR, PAINT)
        px(d, x, EDGE_NEAR, PAINT)
        px(d, x, EDGE_NEAR + 1, PAINT_D)
        for yd in DIVS:
            if x % DASH_P < DASH_L:
                px(d, x, yd, PAINT)
                if x % DASH_P in (0, DASH_L - 1):
                    px(d, x, yd, PAINT_D)                             # 两头稍暗（漆边磨掉了）
        if hash01(x, 110) < 0.06:                                     # 实线上偶尔掉漆的点
            px(d, x, EDGE_FAR, PAINT_D)
            px(d, x, EDGE_NEAR, PAINT_D)
    # 反光道钉：虚线空档的中间（白）+ 两条路缘线上（黄）
    for x in range(DASH_L + (DASH_P - DASH_L) // 2, ROAD_P, DASH_P):
        for yd in DIVS:
            px(d, x, yd, (250, 250, 240))
            px(d, x + 1, yd, (120, 120, 126))
    for x in range(10, ROAD_P, DASH_P * 2):
        px(d, x, EDGE_FAR - 1, STUD)
        px(d, x + 1, EDGE_FAR - 1, (110, 96, 70))
        px(d, x + 20, EDGE_NEAR + 1, STUD)
        px(d, x + 21, EDGE_NEAR + 1, (110, 96, 70))
    # 刹车印（两道，跨车道斜着）
    for k in range(34):
        x = 420 + k
        y = 161 + k // 12
        if y not in DIVS:
            px(d, x, y, (62, 60, 64))
            px(d, x, y + 3, (62, 60, 64))
    # 远侧路肩上的东西：反光桩、里程碑、干草、碎石、半截旧轮胎、塑料瓶
    for i in range(160):
        x = int(hrange(0, ROAD_P, i, 111))
        y = int(hrange(SHOULDER + 2, ASPH[0] - 1, i, 112))
        px(d, x, y, (GRAVEL[0], GRAVEL[4], (204, 186, 150))[i % 3])
    for i in range(40):
        x = int(hrange(0, ROAD_P, i, 113))
        P.grass_tuft(d, x, edge[x] + 1, int(hrange(2, 5, i, 114)), 115 + i)
    for x in range(30, ROAD_P, POST_P):                               # 白色反光桩（每 80 px）
        base = ASPH[0] - 1
        top = base - 10
        vl(d, x, top, base, (246, 244, 236))
        vl(d, x + 1, top, base, (198, 196, 190))
        hl(d, x, x + 1, top, (250, 250, 246))
        hl(d, x, x + 1, top + 2, (36, 34, 38))                         # 黑带
        hl(d, x, x + 1, top + 3, (36, 34, 38))
        px(d, x, top + 5, STUD)                                       # 反光片
        px(d, x + 1, top + 5, (210, 150, 50))
        px(d, x + 2, base, GRAVEL[0])                                 # 影子（往右下）
        px(d, x + 3, base, GRAVEL[1])
    mx = 470                                                         # 里程碑：白身、黄顶、一行黑字
    base = ASPH[0] - 1
    rect(d, mx, base - 8, mx + 7, base, (236, 234, 226))
    ellipse(d, mx, base - 12, mx + 7, base - 6, (236, 196, 64))
    hl(d, mx + 1, mx + 6, base - 12, (250, 220, 110))
    vl(d, mx + 7, base - 9, base, (186, 184, 176))
    hl(d, mx + 1, mx + 5, base - 5, (50, 50, 54))
    hl(d, mx + 2, mx + 4, base - 3, (50, 50, 54))
    px(d, mx + 8, base, GRAVEL[0])
    px(d, mx + 9, base, GRAVEL[1])
    tx = 250                                                         # 半截旧轮胎（躺着）
    base = ASPH[0] - 2
    ellipse(d, tx, base - 3, tx + 9, base, (44, 42, 46))
    hl(d, tx + 2, tx + 7, base - 3, (80, 78, 82))
    ellipse(d, tx + 3, base - 2, tx + 6, base - 1, GRAVEL[2])
    for (bx, by) in ((372, ASPH[0] - 3), (590, ASPH[0] - 4)):         # 塑料瓶（反光一点）
        hl(d, bx, bx + 2, by, (150, 200, 220))
        px(d, bx + 3, by, (60, 120, 70))
        px(d, bx + 1, by, (230, 246, 250))
    # 近侧路肩：小石头、碎玻璃闪光、几根干草（都很矮）
    for i in range(70):
        x = int(hrange(0, ROAD_P, i, 116))
        y = int(hrange(NEAR_SH + 1, H, i, 117))
        px(d, x, y, (GRAVEL[0], GRAVEL[4], (210, 196, 166), (230, 236, 236))[i % 4])
    return opaque(im)


# ============================================================ 扬尘（fg strip，key 'dust'，半透明）
DUST_BOX = (0, 126, W, H)
DUST_C = [(222, 200, 160), (206, 182, 142), (236, 220, 188)]


@lru_cache(maxsize=None)
def _dust_f(f):
    """路面扬起的沙尘：贴着路面一层薄薄的黄尘（透明度 40）+ 一团团往左飘（车往右开）、边飘边升、越来越大越淡的
    尘团 + 几道被风拉长的尘线。透明度只有 40 / 70 / 100 / 120 四档（硬边像素，不做平滑渐变），最浓也透得出车道线。"""
    al = np.zeros((H, W), np.float32)
    col = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # 底下一层：从 y 146 往下越来越浓，上沿按列起伏（像一层慢慢翻滚的尘）
    ph = math.tau * f / N_DUST
    top = 150 + 3 * np.sin(xx[0] * 0.05 + ph) + 2 * np.sin(xx[0] * 0.13 - ph * 2)
    base_m = yy >= top[None, :]
    al = np.where(base_m, 40.0, 0.0)
    col[...] = DUST_C[0]
    for i in range(28):
        p = (f / N_DUST + hash01(i, 121)) % 1.0
        y0 = hrange(148, 178, i, 122) - p * hrange(6, 14, i, 125)
        x = (hrange(0, W + 80, i, 123) - p * 90) % (W + 80) - 40
        r = 4 + p * hrange(6, 14, i, 124)
        a = 120 * (1 - p) ** 0.7
        for k in range(3):
            ox = hrange(-r * 0.8, r * 0.8, i, k, 126)
            oy = hrange(-r * 0.3, r * 0.2, i, k, 127)
            rr = r * hrange(0.55, 0.9, i, k, 128)
            m = ((xx - x - ox) / rr) ** 2 + ((yy - y0 - oy) / (rr * 0.55)) ** 2 < 1
            al = np.where(m, np.maximum(al, a * (0.75 if k else 1.0)), al)
            col[m] = DUST_C[(i + k) % 3]
    for i in range(10):                                               # 尘线
        y = int(hrange(150, 178, i, 129))
        x0 = int((hrange(0, W + 80, i, 130) - (f / N_DUST + hash01(i, 131)) % 1.0 * 120) % (W + 80)) - 40
        L = int(hrange(10, 26, i, 132))
        al[y, max(0, x0):max(0, min(W, x0 + L))] = np.maximum(al[y, max(0, x0):max(0, min(W, x0 + L))], 70)
    q = np.where(al >= 110, 120, np.where(al >= 85, 100, np.where(al >= 55, 70, np.where(al >= 30, 40, 0))))
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = col.astype(np.uint8)
    out[..., 3] = q.astype(np.uint8)
    out[:DUST_BOX[1]] = 0
    return Image.fromarray(out, 'RGBA')


def dust_frame(t):
    return _dust_f(frame_of(t, N_DUST, FPS_DUST))


# ============================================================ 组装 / 导出
STRIPS = [('heat', HEAT_BOX, N_HEAT, FPS_HEAT, heat_frame),
          ('eagle', EAGLE_BOX, N_EAGLE, FPS_EAGLE, eagle_frame)]
FG_STRIPS = [('dust', DUST_BOX, N_DUST, FPS_DUST, dust_frame)]


@lru_cache(maxsize=1)
def build():
    return dict(sky=sky_img(), clouds=clouds_img(), mountains=mountains_img(), plain=plain_img(), mid=mid_img(),
                road=road_img(), crows=crows_img())


def _wrap_crop(im, o, y, out):
    """直接拼时的 wrap：从周期图第 o 列取 320 宽（不够就从头接）。"""
    P_ = im.width
    o %= P_
    if o + W <= P_:
        out.alpha_composite(im.crop((o, 0, o + W, im.height)), (0, y))
    else:
        w1 = P_ - o
        out.alpha_composite(im.crop((o, 0, P_, im.height)), (0, y))
        out.alpha_composite(im.crop((0, 0, W - w1, im.height)), (w1, y))


def compose(t=0.5, dust=False):
    """直接拼一帧（不经导出），自检 / 预览用（镜头不动 camX = 0，speed = 1）。"""
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    for key, P_, vx in (('clouds', CLOUD_P, CLOUD_VX), ('mountains', MTN_P, MTN_VX), ('plain', PLAIN_P, PLAIN_VX)):
        cim, cy = _rows(R[key])
        _wrap_crop(cim, int(math.floor(t * vx)), cy, out)
        if key == 'clouds':
            for (y, vx_, x0) in CROWS:
                x = (x0 + t * vx_) % (W + 200) - 100
                paste(out, R['crows'], math.floor(x), y)
    for (name, box, n, fps, fn) in STRIPS[:1]:
        paste(out, fn(t).crop(box), box[0], box[1])
    for (name, box, n, fps, fn) in STRIPS[1:]:
        paste(out, fn(t).crop(box), box[0], box[1])
    for key, vx in (('mid', MID_VX), ('road', ROAD_VX)):
        cim, cy = _rows(R[key])
        _wrap_crop(cim, int(math.floor(t * vx)), cy, out)
    if dust:
        for (name, box, n, fps, fn) in FG_STRIPS:
            paste(out, fn(t).crop(box), box[0], box[1])
    return out


def _rows(im):
    bb = im.getchannel('A').getbbox()
    return (im.crop((0, bb[1], im.width, bb[3])), bb[1]) if bb else (im, 0)


def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0)]
    cim, cy = BJ.crop_rows(R['clouds'])
    layers.append(dict(type='wrap', image=ex.img('clouds', cim), period=CLOUD_P, k=CLOUD_K, y=cy, vx=CLOUD_VX))
    layers.append(dict(type='clouds', span=W + 200, clouds=[dict(image=ex.img('crows', R['crows']), x0=x0, y=y, vx=vx,
                                                                 k=0.0) for (y, vx, x0) in CROWS]))
    mim, my = BJ.crop_rows(R['mountains'])
    layers.append(dict(type='wrap', image=ex.img('mountains', mim), period=MTN_P, k=MTN_K, y=my, vx=MTN_VX))
    pim, py = BJ.crop_rows(R['plain'])
    layers.append(dict(type='wrap', image=ex.img('plain', pim), period=PLAIN_P, k=PLAIN_K, y=py, vx=PLAIN_VX))
    for (name, box, n, fps, fn) in STRIPS:
        layers.append(ex.bake(name, box, n, fps, fn, screen=True))
    dim, dy = BJ.crop_rows(R['mid'])
    layers.append(dict(type='wrap', image=ex.img('mid', dim), period=MID_P, k=MID_K, y=dy, vx=MID_VX))
    rim, ry = BJ.crop_rows(R['road'])
    layers.append(dict(type='wrap', image=ex.img('road', rim), period=ROAD_P, k=1.0, y=ry, vx=ROAD_VX))
    fg = [ex.bake(name, box, n, fps, fn, screen=True, key='dust') for (name, box, n, fps, fn) in FG_STRIPS]
    anchors = dict(ANCHORS)
    anchors.update(horizon=HZ, road_vx=ROAD_VX,
                   lane_lines=dict(far=EDGE_FAR, mid1=DIVS[0], mid2=DIVS[1], near=EDGE_NEAR))
    st = ex.stage(PW, GROUND, WALK, layers, fg, anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    P.check_no_black(ex, BJ, st, '公路 4 个时刻 × dust 开 / 关 整屏都有画（没有露黑）',
                     times=(0.0, 0.75, 1.5, 7.0), states=({}, {'dust': True}))
    P.check_opaque(ex, '天空底图整张不透明', R['sky'], (0, 0, W, H))
    P.check_opaque(ex, '近景 路肩 + 柏油 + 近路肩（y 141–180）整条不透明', R['road'], (0, 141, ROAD_P, H))
    P.check_alpha_binary(ex, '近景（路）只有 0 / 255 两种透明度', R['road'])
    P.check_alpha_binary(ex, '中景只有 0 / 255 两种透明度', R['mid'])
    P.check_opaque(ex, '中景 地面（y 119–144）整条不透明（远景不会从下面漏出来）', R['mid'], (0, 119, MID_P, 144))
    P.check_opaque(ex, '远平原 地平线以下（y 98–132）整条不透明', R['plain'], (0, HZ, PLAIN_P, 132))
    widths = dict(clouds=CLOUD_P, mountains=MTN_P, plain=PLAIN_P, mid=MID_P, road=ROAD_P)
    ex.checked('wrap 图宽 = period（%s）' % ', '.join('%s %d' % kv for kv in widths.items()),
               sum(int(R[k].width != v) for k, v in widths.items()))
    P.check_strips(ex, BJ, STRIPS + FG_STRIPS)
    P.check_wraps(ex, BJ, st)
    # 扬尘：半透明，最多 120/255（盖住路面不超过一半，车道线还看得见）
    da = max(int(np.array(dust_frame(i / FPS_DUST))[..., 3].max()) for i in range(N_DUST))
    ex.checked('扬尘最浓的像素透明度 %d ≤ 120（车道线透得出来）' % da, max(0, da - 120))
    # 车道线：四条线（实 / 虚）在每一列都是漆色（实线）或按 40 px 周期出现（虚线），和柏油的亮度差够大
    ra = np.array(R['road'])[..., :3].astype(np.float32)
    lum = P.lum(ra)
    asph = lum[ASPH[0] + 3:ASPH[1] - 1].mean()
    paint = min(lum[EDGE_FAR].mean(), lum[EDGE_NEAR].mean(), max(lum[DIVS[0]]), max(lum[DIVS[1]]))
    ex.checked('车道线比柏油亮 ≥ 90（漆 %.0f vs 路面 %.0f）' % (paint, asph), 0 if paint - asph >= 90 else 1)
    dash = sum(int((lum[yd] > asph + 90).sum()) for yd in DIVS)
    ex.checked('两条虚线的亮段占 %.0f%%（每 40 px 18 px 左右）' % (dash / (2 * ROAD_P) * 100),
               0 if 0.35 < dash / (2 * ROAD_P) < 0.6 else 1)
    # 车道：每条道（两线之间）里面没有比柏油亮很多的东西（除了道钉 / 白石子），车停上去看得清
    noisy = 0
    for (y0, y1) in ((EDGE_FAR + 1, DIVS[0]), (DIVS[0] + 1, DIVS[1]), (DIVS[1] + 1, EDGE_NEAR)):
        noisy += int((np.abs(lum[y0:y1] - asph) > 60).sum())
    ex.checked('三条车道里面平整（和路面均值差 > 60 的像素）', noisy, limit=ROAD_P * 3 // 40)
    # 锚点
    out = 0
    for k in ('party_car', 'wheel_start'):
        v = ANCHORS[k]
        out += not (0 <= v[0] < PW and WALK[0] <= v[1] <= WALK[1])
    out += int(list(ANCHORS['lanes']) != [152, 160, 168])
    for lc in LANES:                                                  # 车轮着地的行在两条线正中间
        ys = sorted([EDGE_FAR] + list(DIVS) + [EDGE_NEAR])
        lo = max(y for y in ys if y < lc)
        hi = min(y for y in ys if y > lc)
        out += int(abs((lo + hi) / 2 - lc) > 0.5)
    ex.checked('锚点在可走带里、三条车道的 y = 152 / 160 / 168 且都在两条线正中间（不满足的条数）', out)
    for t in (0.0, 1.25, 3.4, 11.0):
        for dz in (False, True):
            got = BJ.ref_render(st, ex.images, 0, t, {'dust': True} if dz else {})
            ex.checked('公路 t=%.2f dust=%d 导出 vs 直接拼' % (t, dz), BJ.ndiff(got, compose(t, dz)))
    ex.note('路面亮度：柏油均值 %.0f，车道线 %.0f；中景地面均值 %.0f' %
            (asph, paint, P.lum(np.array(R['mid'])[120:140, :, :3].astype(np.float32)).mean()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch5', 'after')
    os.makedirs(od, exist_ok=True)
    sheet = Image.new('RGB', (W * 3, H * 2), (0, 0, 0))
    for i, t in enumerate((0.0, 1.0, 2.5)):
        sheet.paste(compose(t).convert('RGB'), (i * W, 0))
        sheet.paste(compose(t, True).convert('RGB'), (i * W, H))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(os.path.join(od, 'desert_highway_solo.png'))
    mid = Image.new('RGBA', (MID_P, H), (150, 190, 220, 255))
    mid.alpha_composite(build()['mid'])
    mid.convert('RGB').resize((MID_P * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'desert_highway_mid.png'))
    print('ok')
