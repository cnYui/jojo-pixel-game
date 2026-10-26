# -*- coding: utf-8 -*-
r"""mountain_road —— 第5章：山口公路的路肩（地图 cliff_ch5，第 9 战段 2「命运之轮」+ 安妮告别）。中午，晴，干。
2026-10-18 ch5-road 组按体验版精度重画（改前是 ch5_scenes.cliff()：一块平涂的斜岩 + 一座三角山 + 一排白桩）。

地图 320 宽（单屏，镜头不动），ground 160、可走带 148–176（人和车都在路肩的碎石地上）。侧视平视，太阳在左上（中午，
偏高：影子短、几乎落在脚下）。
从左到右（世界坐标）：
  x 0–128    一面高高的砂岩崖壁：崖顶在 y 30 左右（顶上一溜干草、两丛灌木）；一层层的岩层（每层上沿受光、下面一道暗缝，
             颜色在土黄 / 锈红 / 米白之间换）、竖着的节理裂缝、几丛从缝里长出来的灌木；右边是往里退的侧面（背光，暗）。
             从崖顶 (70, 32) 到崖脚 (96, 146) 有一溜稍平、颜色浅一点的“车道”（命运之轮顺着它爬下来）：
             岩层在这里被磨平了，上面两道黑色的轮胎印。崖脚一坡碎石（车道落地的地方留空）。
  x 124–228  路肩后沿就是山谷的边：一块从崖上掉下来的大落石（x 128–156），一块“当心落石”的三角牌，
             一排刷了黑白道的护路石
  x 228–320  波形钢护栏（一根根立柱、两个反光片、x 300 那头一块黄底黑箭头的弯道牌）；护栏外是山谷：
             远处一道淡紫色的雪山、近一点的褐色山梁、山坡上一个小村子（平顶土房、小清真寺）、
             之字形下山的公路（路上一辆小卡车）、谷底一条青绿色的河（波光 strip）、河边的梯田和一排排白杨
  y 146–176  路肩：压实的碎石土（低对比），两道车辙、碎石子、几撮干草；崖脚一条中午的短影子
  y 177–179  柏油路的边（白色路缘线）
光：太阳在左上、偏高；岩层的上沿最亮，崖面越往右越暗（转到侧面），落石 / 护栏 / 路牌的影子短、往右下。

图层（从后往前）：
  sky      static             中午的天（上深下浅）+ 左上角的日晕
  clouds   wrap  640  vx 3    远山上的几朵积云
  far      static             山谷远景（雪山 / 山梁 / 村子 / 公路 / 河 / 梯田 / 白杨），y 46–147 不透明
  river    strip  8 帧 @4 fps  谷底河面的波光
  eagle    strip 16 帧 @8 fps  山谷上空盘旋的鹰
  near     static             崖壁 + 碎石坡 + 落石 + 路牌 + 护路石 + 护栏 + 路肩 + 路边（只有 0 / 255 透明度）
  sway     strip  8 帧 @4 fps  崖顶 / 岩缝里的灌木和护栏脚下的干草被风吹得晃（几个框共用一个帧函数）
  pebbles  strip 16 帧 @8 fps  崖面一道冲沟里不时滚下来的小石子（落到崖脚扬一点土）
  scorch   static  key        被火烧黑的一片地（中心 (206, 163)）
  embers   strip  key scorch  焦地上还没灭的火星 + 细烟（8 帧 @8 fps）
  oil      static  key        三摊汽油（puddles）+ 崖面上顺着车道淌下来的油痕
  sheen    strip  key oil     油面上的彩虹油光慢慢流动（8 帧 @4 fps）
  hole     static  key        tunnel 处挖开的洞：翻起的土块、往外裂的缝

锚点：cliff_top [70,32]、wheel [96,160]、party_car [282,168]、arrive [196,162]、tunnel [150,169]、
      puddles [[128,170],[178,172],[228,168]]、spw_car [140,166]、sign [300,131]（弯道牌的牌面中心；规格 138，护栏钢板挡住下半截，抬高 7 px）；
      另外导出：lane（车道中线从崖顶到崖脚的点列）、scorch [206,163]（焦地中心）、boulder [142,147]（落石脚）、
      rockfall_sign [176,131]、rail [228,320]（护栏的 x 范围，数字）、edge 146（路肩后沿的 y）。
key：oil、hole、scorch。
单独运行：python -B tools\bg_new\mountain_road.py → tools\bg_new\_preview\ch5\after\mountain_road_solo.png
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
from scipy import ndimage  # noqa: E402

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
ellipse, line = P.ellipse, P.line
frame_of = P.frame_of

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 320
GROUND = 160
WALK = (148, 176)
EDGE = 146                     # 路肩后沿（崖脚 / 山谷边）：这一行往下整条不透明
ROAD = 177                     # 前面柏油路的边（177–179）
RAIL = (228, 320)              # 护栏
SIGN_C = (300, 131)            # 弯道牌牌面中心（规格写 138；护栏钢板在 139–144，牌面整块抬到护栏上面才看得全）
ROCKSIGN_C = (176, 131)        # 当心落石牌
BOULDER = (128, 157)           # 落石 x 范围
SCORCH_C, SCORCH_R = (206, 163), (24, 7)
CLOUD_P, CLOUD_VX = 640, 3.0
N_RIV, FPS_RIV = 8, 4.0
N_EAGLE, FPS_EAGLE = 16, 8.0
N_SWAY, FPS_SWAY = 8, 4.0
N_PEB, FPS_PEB = 16, 8.0
N_OIL, FPS_OIL = 8, 4.0
N_EMB, FPS_EMB = 8, 8.0

ANCHORS = dict(
    cliff_top=[70, 32],          # 车从崖顶这里冒出来，顺着车道爬下来
    wheel=[96, 160],             # 车落地的崖脚下
    party_car=[282, 168],        # 众人的车被逼停在右边护栏旁
    arrive=[196, 162],
    tunnel=[150, 169],           # 承太郎挖地的点（两车中间）
    puddles=[[128, 170], [178, 172], [228, 168]],
    spw_car=[140, 166],          # SPW 的车从左边开来接安妮
    sign=list(SIGN_C),           # 右边护栏那头的弯道路牌（牌面中心）
)

# ============================================================ 调色
SKY_STOPS = [(46, 104, 186), (66, 126, 202), (98, 152, 214), (140, 182, 224), (184, 208, 228), (214, 224, 226)]
HAZE = (200, 212, 220)          # 山谷里的空气（偏蓝灰）
ROCK = [(96, 58, 46), (134, 86, 62), (170, 116, 80), (204, 152, 104), (232, 192, 140)]       # 土黄砂岩（暗→亮）
ROCK_R = [(92, 50, 42), (128, 72, 54), (164, 98, 70), (196, 132, 92), (224, 170, 124)]       # 锈红层
ROCK_W = [(110, 82, 66), (150, 118, 92), (190, 158, 122), (220, 192, 152), (240, 218, 180)]  # 米白层
ROCK_INK = (70, 40, 34)
GROUND_C = [(132, 116, 98), (152, 136, 114), (166, 150, 126), (178, 162, 136), (194, 178, 150)]
ASPH = (84, 82, 84)
STEEL = [(84, 88, 96), (126, 132, 140), (168, 174, 182), (212, 216, 222)]
LEAF = ((58, 78, 44), (86, 108, 54), (116, 136, 66), (156, 166, 92))


# ============================================================ 天 / 云
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), SKY_STOPS, bands=14)
    A._glow(im, 10, -6, 90, 60, (255, 248, 226), 64, rings=6)      # 太阳在画面外左上（中午偏高）
    A._glow(im, 10, -6, 34, 24, (255, 252, 240), 96, rings=3)
    return im


@lru_cache(maxsize=1)
def clouds_img():
    """640 循环：远山顶上的几朵平底积云（中午的对流云，底边齐、受光的上半亮）+ 高处两三朵小的。"""
    im = A._new(CLOUD_P, 100)
    pal = ((255, 255, 255), (238, 242, 248), (210, 222, 236), (186, 202, 222))
    for i in range(6):
        w = hrange(40, 84, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.34, 0.46, i, 2), 300 + i, pal)
        cx = (i + hrange(0.1, 0.9, i, 3)) * CLOUD_P / 6
        y = 96 - cl.height - int(hrange(0, 16, i, 4))
        for dx in (-CLOUD_P, 0, CLOUD_P):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    for i in range(4):
        w = hrange(16, 30, i, 11)
        cl = A._cloud_sprite(w, w * 0.34, 320 + i, pal)
        cx = (i + hrange(0.1, 0.9, i, 12)) * CLOUD_P / 4
        for dx in (-CLOUD_P, 0, CLOUD_P):
            paste(im, cl, int(cx + dx - cl.width / 2), int(hrange(4, 40, i, 13)))
    return im


# ============================================================ 山谷远景（static）
RIVER_PTS = [(104, 127), (132, 125), (160, 129), (184, 126), (208, 131), (234, 128), (262, 134), (290, 131),
             (314, 137), (330, 136)]


def river_y(x):
    xs = [p[0] for p in RIVER_PTS]
    ys = [p[1] for p in RIVER_PTS]
    return float(np.interp(x, xs, ys))


def river_hw(x):
    """河越往前（右下）越宽：远处 0.6、近处 2.6。"""
    return 0.6 + max(0.0, x - 104) / 226.0 * 2.0


@lru_cache(maxsize=1)
def river_mask():
    m = np.zeros((H, W), bool)
    for x in range(100, W):
        y = river_y(x)
        hw = river_hw(x)
        m[int(round(y - hw)):int(round(y + hw)) + 1, x] = True
    return m


def _poplar(d, x, base, h, haze_k):
    """白杨：细高的一根，左亮右暗。"""
    cd, cm, ch = (mix(c, HAZE, haze_k) for c in ((48, 82, 50), (74, 110, 60), (112, 144, 78)))
    for y in range(base - h, base):
        u = (y - (base - h)) / max(1, h - 1)
        hw = 0 if u < 0.15 else 1
        hl(d, x - hw, x + hw, y, cm)
        px(d, x - hw, y, ch)
        px(d, x + hw, y, cd)
    vl(d, x, base - 1, base, mix((90, 74, 60), HAZE, haze_k))


@lru_cache(maxsize=1)
def far_img():
    a = np.zeros((H, W, 4), np.uint8)
    # 最远的雪山（淡紫蓝）：几座尖峰（坡度 0.7–1.1 的三角形叠起来 + 一点锯齿），顶上三分之一积雪、朝左的坡雪多
    xs = np.arange(W, dtype=np.float32)
    hs = np.zeros(W, np.float32)
    for (pk, ph_, sl_) in ((136, 26, 0.8), (178, 40, 0.95), (214, 30, 0.75), (262, 46, 1.05), (306, 34, 0.85),
                           (338, 30, 0.8)):
        hs = np.maximum(hs, ph_ - np.abs(xs - pk) * sl_)
    hs = np.maximum(hs, 6) + (P.wnoise(W, 4, 4, 211)[1] - 0.5) * 3
    P.ridge(a, 112, hs, ((202, 204, 228), (178, 182, 212), (152, 158, 194), (228, 230, 242)), 211, HAZE, 0.3, 0.55,
            gully=0.0)
    for x in range(W):
        top = int(round(112 - hs[x]))
        snow_line = 112 - hs[x] * 0.62
        sl = hs[min(W - 1, x + 1)] - hs[max(0, x - 1)]
        for y in range(top, int(snow_line) + 1):
            if y > top + 1 and hash01(x // 2, y // 2, 212) < (y - top) / max(1.0, snow_line - top) * 0.55:
                continue                                              # 雪线参差（下沿一条条往下的雪槽）
            a[y, x, :3] = mix((246, 248, 252) if sl > 0 else (206, 214, 234), HAZE, 0.22)
    # 近一点的褐色山梁
    hm = P.hfield(W, 223, [(1, 10, 0.9), (3, 7, 2.6), (5, 4, 0.8), (9, 2, 1.7)], 5, 8) + 4
    hm = hm + np.clip((np.arange(W) - 180) / 140.0, 0, 1) * 14       # 右边的山梁抬高（对面山坡）
    P.ridge(a, 124, hm, ((190, 150, 118), (166, 128, 104), (138, 104, 92), (210, 176, 140)), 223, HAZE, 0.2, 0.42,
            gully=0.9)
    # 谷底（y 118–147）：从山脚往前铺满，偏黄绿；梯田、白杨、河
    nz = P.wnoise(W, H, 10, 231)
    b = P.bayer(W, H)
    for y in range(112, 148):                                       # 从雪山脚往下铺（两道山之间不能露天）
        for x in range(W):
            if a[y, x, 3] and y < 124:
                continue
            u = max(0.0, (y - 116) / 31.0)
            c = mix(mix((176, 162, 118), HAZE, 0.32), (168, 150, 104), u)
            n = nz[y, x]
            if n > 0.62 or (n > 0.57 and b[y, x] < 0.5):
                c = mix(c, (130, 146, 86), 0.55)                     # 一块块绿地
            elif n < 0.36:
                c = mix(c, (196, 182, 136), 0.4)
            a[y, x, :3] = c
            a[y, x, 3] = 255
    im = P.img(a)
    d = ImageDraw.Draw(im)
    # 梯田：一条条顺着坡的弧线（亮一行 + 暗一行）
    for i in range(14):
        y0 = 118 + int(hrange(0, 24, i, 232))
        x0 = int(hrange(110, 300, i, 233))
        L = int(hrange(16, 40, i, 234))
        for k in range(L):
            y = y0 + int(round(math.sin(k / L * math.pi) * -1.5))
            px(d, x0 + k, y, mix((150, 168, 96), HAZE, 0.25))
            px(d, x0 + k, y + 1, mix((116, 120, 76), HAZE, 0.25))
    # 河：青绿，两岸一道浅色砂石滩
    rm = river_mask()
    ar = np.array(im)
    for x in range(100, W):
        y = river_y(x)
        hw = river_hw(x)
        y0, y1 = int(round(y - hw)), int(round(y + hw))
        for yy in range(y0 - 1, y1 + 2):
            if 0 <= yy < H:
                ar[yy, x, :3] = mix((206, 200, 176), HAZE, 0.2)
        for yy in range(y0, y1 + 1):
            ar[yy, x, :3] = mix((84, 146, 152), HAZE, 0.22) if yy > y0 else mix((134, 186, 190), HAZE, 0.2)
    im = P.img(ar)
    d = ImageDraw.Draw(im)
    # 河边的白杨（一排排）
    for i in range(22):
        x = int(hrange(120, 318, i, 241))
        base = int(river_y(x) - river_hw(x) - 2 - hrange(0, 5, i, 242))
        _poplar(d, x, base, int(hrange(6, 11, i, 243)), 0.2)
    # 对面山坡上的小村子（平顶土房 + 小清真寺）+ 之字形下山的公路 + 路上一辆小卡车
    for k in range(9):
        hx = 246 + int(hrange(0, 40, k, 251))
        hy = 108 + int(hrange(0, 9, k, 252))
        w = int(hrange(3, 6, k, 253))
        col = mix([(214, 196, 160), (196, 172, 136), (226, 214, 190)][k % 3], HAZE, 0.25)
        rect(d, hx, hy - 2, hx + w, hy, col)
        hl(d, hx, hx + w, hy - 2, lt(col, 0.25))
        px(d, hx + w, hy - 1, dk(col, 0.8))
        px(d, hx + 1, hy - 1, dk(col, 0.6))
    ellipse(d, 272, 101, 276, 105, mix((236, 236, 228), HAZE, 0.2))
    rect(d, 271, 104, 277, 107, mix((236, 236, 228), HAZE, 0.2))
    vl(d, 279, 99, 107, mix((236, 236, 228), HAZE, 0.2))
    road = [(330, 112), (292, 113), (252, 116), (222, 117), (262, 121), (300, 124), (240, 126), (204, 127), (190, 129)]
    for (xa, ya), (xb, yb) in zip(road, road[1:]):
        line(d, [(xa, ya), (xb, yb)], mix((222, 214, 196), HAZE, 0.2))
    rect(d, 258, 119, 261, 120, mix((200, 70, 60), HAZE, 0.2))       # 小卡车
    px(d, 262, 120, mix((60, 60, 70), HAZE, 0.2))
    rect(d, 186, 130, 194, 130, mix((180, 176, 166), HAZE, 0.15))    # 小桥
    for x in (187, 193):
        px(d, x, 131, mix((120, 116, 110), HAZE, 0.15))
    im = P.haze(im, np.clip((np.arange(H, dtype=np.float32)[:, None] - 100) / 50.0 * 0.12, 0, 0.12), HAZE)
    return im


# ============================================================ 河面波光（strip）
RIV_BOX = (100, 124, W, 145)


@lru_cache(maxsize=None)
def _riv_f(f):
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    rm = river_mask()
    for i in range(60):
        x = int(hrange(110, W, i, 261))
        y = int(round(river_y(x) + hrange(-river_hw(x), river_hw(x), i, 262)))
        ph = (f / N_RIV + hash01(i, 263)) % 1.0
        if ph > 0.45 or not rm[y, x]:
            continue
        L = 1 + (1 if ph < 0.2 else 0) + int(river_hw(x) > 2.4)
        for k in range(L):
            if rm[y, min(W - 1, x + k)]:
                px(d, x + k, y, (236, 248, 246) if ph < 0.22 else (180, 222, 222))
    return im


def river_frame(t):
    return _riv_f(frame_of(t, N_RIV, FPS_RIV))


# ============================================================ 鹰（strip）
EAGLE_C, EAGLE_R = (232, 82), (26, 8)
EAGLE_BOX = (EAGLE_C[0] - EAGLE_R[0] - 7, EAGLE_C[1] - EAGLE_R[1] - 4, EAGLE_C[0] + EAGLE_R[0] + 7,
             EAGLE_C[1] + EAGLE_R[1] + 7)


@lru_cache(maxsize=None)
def _eagle_f(f):
    im = A._new(W, H)
    ang = math.tau * f / N_EAGLE
    x = EAGLE_C[0] - EAGLE_R[0] * math.cos(ang)
    y = EAGLE_C[1] + EAGLE_R[1] * math.sin(ang)
    c = math.cos(ang)
    pose = 'bank_l' if c > 0.6 else 'bank_r' if c < -0.6 else ('up' if f == N_EAGLE // 4 else 'glide')
    im.alpha_composite(P.eagle_img(pose), (int(round(x)) - 5, int(round(y)) - 2))
    return im


def eagle_frame(t):
    return _eagle_f(frame_of(t, N_EAGLE, FPS_EAGLE))


# ============================================================ 崖壁
WALL_OUTLINE = [(0, 25), (16, 23), (30, 27), (46, 26), (60, 30), (70, 31), (80, 30), (92, 33), (101, 37), (108, 44),
                (112, 56), (111, 68), (115, 80), (114, 93), (118, 106), (120, 118), (123, 130), (127, 141),
                (130, 147), (0, 147)]
LANE_TOP, LANE_BOT = (70, 31), (96, 146)
LANE_HW = 8


def lane_x(y):
    """车道中线：从崖顶 (70, 31) 往下先陡后缓地偏向右下，到崖脚 (96, 146)。"""
    u = (y - LANE_TOP[1]) / float(LANE_BOT[1] - LANE_TOP[1])
    u = min(1.0, max(0.0, u))
    return LANE_TOP[0] + (LANE_BOT[0] - LANE_TOP[0]) * (u ** 1.35) + 2.5 * math.sin(u * math.pi * 1.5)


@lru_cache(maxsize=1)
def wall_mask():
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon(WALL_OUTLINE, fill=255)
    m = np.array(m) > 0
    din = ndimage.distance_transform_edt(m)
    dout = ndimage.distance_transform_edt(~m)
    s = din - dout + (A._fbm(W, H, 5, 271) - 0.5) * 5.0
    m = s > 0
    m = ndimage.binary_opening(m, np.ones((2, 2), bool))
    m = ndimage.binary_closing(m, np.ones((2, 2), bool))
    m[EDGE + 1:, :] = False                                           # 崖脚往下是地面（另画）
    lab, n = ndimage.label(m)                                         # 只留最大那一块（不要飘着的小碎块）
    if n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = lab == (1 + int(np.argmax(sizes)))
    return m


@lru_cache(maxsize=1)
def lane_mask():
    yy, xx = np.mgrid[0:H, 0:W]
    lx = np.array([lane_x(y) for y in range(H)], np.float32)
    return (np.abs(xx - lx[:, None]) <= LANE_HW) & (yy >= LANE_TOP[1]) & wall_mask()


def _strata(yy, xx):
    """岩层的“层号”（连续值）：层厚 9–14 不等、略往右下倾、带一点起伏。"""
    nn = A._fbm(W, H, 10, 281)
    return (yy + nn * 9 + np.sin(xx * 0.045 + 0.7) * 2.2 + xx * 0.06) / 11.5


@lru_cache(maxsize=1)
def wall_rgba():
    """崖壁（numpy RGBA）：高度场 = 到崖边的距离开根号（崖面中间鼓、往右转进侧面）− 每层往下凹进去（层的上沿是受光的
    台阶）；车道那一溜把层磨平。按左上的光分 5 级 + Voronoi 切面，然后按层换颜色（土黄 / 锈红 / 米白），再画节理裂缝、
    层缝、车道上的轮胎印。可走带后面那段（y 108 往下）压一点对比。"""
    m = wall_mask()
    pm = np.pad(m, 1, constant_values=False)
    pm[:, 0] = True                                                   # 地图左边外面、崖脚下面都还是崖（不当成边描亮 / 暗）
    pm[-1, :] = True
    dist = ndimage.distance_transform_edt(pm)[1:-1, 1:-1]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    z = np.sqrt(dist) * 2.6
    band = _strata(yy, xx)
    frac = band - np.floor(band)
    lm = lane_mask()
    lane_soft = ndimage.gaussian_filter(lm.astype(np.float32), 2.0)
    z = z - frac * 3.4 * (1 - lane_soft * 0.85)
    rgba, q = P.shade(m, z, ROCK, 291, light=(-0.55, -0.8, 0.6), bump=0.45, bcell=5, facet=0.13, fcell=9, aspect=1.7,
                      dither=0.4, seam=0.35, speck=0.02, smooth=0.9, outline=ROCK_INK)
    # 按层换色：层号 hash → 三种岩色之一（同一层同一种），沿用 shade 算好的明暗级
    bi = np.floor(band).astype(int)
    kind = np.vectorize(lambda v: 0 if hash01(v, 292) < 0.5 else (1 if hash01(v, 293) < 0.55 else 2))(bi)
    pals = [np.array(ROCK, np.uint8), np.array(ROCK_R, np.uint8), np.array(ROCK_W, np.uint8)]
    ok = m & (q >= 0)
    for k in (1, 2):
        sel = ok & (kind == k)
        rgba[sel, :3] = pals[k][q[sel]]
    # 层缝：每层下沿一道暗线（断断续续），车道里没有
    edge_ = (frac > 0.9) & m & ~lm
    gap = A._fbm(W, H, 6, 294) > 0.62
    sel = edge_ & ~gap & ok
    rgba[sel, :3] = np.maximum(rgba[sel, :3].astype(int) - 38, 0).astype(np.uint8)
    # 车道：颜色往亮里提一点（被车轮磨过、岩粉）
    sel = lm & ok
    rgba[sel, :3] = np.clip(rgba[sel, :3].astype(np.float32) * 0.85 + np.array((236, 206, 160), np.float32) * 0.15,
                            0, 255).astype(np.uint8)
    im = P.img(rgba)
    d = ImageDraw.Draw(im)
    # 节理裂缝（竖的、折一折），右边一线受光
    for (x0, y0, L, sd) in ((22, 40, 70, 1), (48, 60, 50, 2), (34, 104, 38, 3), (106, 64, 40, 4), (10, 90, 44, 5),
                            (60, 112, 30, 6), (116, 104, 28, 7)):
        x = x0
        for y in range(y0, min(EDGE, y0 + L)):
            if hash01(sd, y, 295) < 0.25:
                x += 1 if hash01(sd, y, 296) < 0.5 else -1
            if not m[y, x] or lm[y, x]:
                continue
            px(d, x, y, ROCK_INK)
            if m[y, x + 1] and hash01(sd, y, 297) < 0.6:
                px(d, x + 1, y, ROCK[4])
    # 车道上的两道轮胎印（深色，断断续续）
    for y in range(LANE_TOP[1] + 2, EDGE - 1):
        cx = lane_x(y)
        for off in (-4, 4):
            x = int(round(cx + off))
            if m[y, x] and hash01(x, y, 298) < 0.82:
                px(d, x, y, (78, 58, 50))
    # 可走带后面那段压对比（人物上半身叠在这里）
    a = np.array(im).astype(np.float32)
    rows = slice(108, EDGE + 1)
    sub = a[rows]
    msk = sub[..., 3] > 0
    mean = np.array((176, 128, 92), np.float32)
    k = np.clip((np.arange(108, EDGE + 1) - 108) / 30.0, 0, 1)[:, None, None] * 0.22
    sub[..., :3] = np.where(msk[..., None], sub[..., :3] * (1 - k) + mean * k, sub[..., :3])
    a[rows] = sub
    return P.img(a)


# ============================================================ 植物 / 小物件
SHRUBS = [  # (x, 根的 y, 宽, 高, 种子)：崖顶、岩缝里的灌木（会晃，画在 sway strip 里）
    (18, 25, 12, 6, 1), (88, 32, 10, 5, 2), (30, 62, 9, 5, 3), (100, 88, 8, 4, 4), (14, 118, 10, 5, 5),
]
TUFTS_RAIL = [233, 247, 262, 281, 296, 311]                         # 护栏立柱脚下的干草（会晃）


def _shrub_sway(im, x, base, w, h, seed, f):
    """会晃的灌木：底下一半不动，上面一半随风往右偏 0 / 1 px（f 帧）。"""
    sway = int(round(math.sin(math.tau * f / N_SWAY + seed) * 1.0))
    lay = A._new(w + 8, h + 6)
    ld = ImageDraw.Draw(lay)
    P.shrub(ld, w // 2 + 4, h + 4, w, h, 400 + seed, pal=LEAF)
    top = lay.crop((0, 0, lay.width, (h + 6) // 2))
    bot = lay.crop((0, (h + 6) // 2, lay.width, h + 6))
    im.alpha_composite(bot, (x - w // 2 - 4, base - h - 4 + (h + 6) // 2))
    im.alpha_composite(top, (x - w // 2 - 4 + sway, base - h - 4))
    # 叶子翻过来的反光：每帧换两处（风吹叶面一闪一闪；也保证相邻两帧一定不一样）
    a = np.array(im)
    for k in range(2):
        gx = x + int(hrange(-w / 2 + 1, w / 2 - 1, seed, f, k, 401)) + sway
        gy = base - int(hrange(h * 0.45, h * 0.95, seed, f, k, 402))
        if 0 <= gx < W and 0 <= gy < H and a[gy, gx, 3]:
            a[gy, gx, :3] = LEAF[3]
            a[gy, gx, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))


@lru_cache(maxsize=None)
def _sway_f(f):
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for (x, base, w, h, sd) in SHRUBS:
        _shrub_sway(im, x, base, w, h, sd, f)
    for i, x in enumerate(TUFTS_RAIL):
        lean = math.sin(math.tau * f / N_SWAY + i * 0.8)
        for k in range(4):
            hh = 3 + (k % 2)
            for j in range(hh):
                xx = x + k - 2 + int(round(lean * j / hh * 1.6))
                px(d, xx, EDGE - j, (150, 136, 84) if j < hh - 1 else (200, 186, 120))
    return im


def sway_frame(t):
    return _sway_f(frame_of(t, N_SWAY, FPS_SWAY))


def _sway_boxes():
    out = []
    for i, (x, base, w, h, sd) in enumerate(SHRUBS):
        out.append(('sway%d' % i, (x - w // 2 - 4, base - h - 4, x + w // 2 + 6, base + 2)))
    out.append(('sway_rail', (RAIL[0] + 2, EDGE - 5, RAIL[1], EDGE + 1)))
    return out


SWAY_BOXES = _sway_boxes()

# 冲沟里滚下来的小石子：沿着一条折线（每段一个台阶）跳下来，落地扬一点土
GULLY = [(42, 58), (45, 72), (43, 84), (47, 98), (46, 112), (50, 126), (52, 140), (55, 146)]
PEB_BOX = (34, 52, 68, 148)


@lru_cache(maxsize=None)
def _peb_f(f):
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    T = N_PEB
    for i, ph0 in enumerate((0.0, 0.37, 0.7)):
        u = (f / T + ph0) % 1.0
        if u < 0.7:                                                   # 前 70% 的时间在往下滚
            s = u / 0.7 * (len(GULLY) - 1)
            k = min(len(GULLY) - 2, int(s))
            fr = s - k
            (xa, ya), (xb, yb) = GULLY[k], GULLY[k + 1]
            x = xa + (xb - xa) * fr
            y = ya + (yb - ya) * fr - math.sin(fr * math.pi) * 2.5        # 每段弹一下
            px(d, int(round(x)), int(round(y)), (120, 90, 70))
            if i != 1:
                px(d, int(round(x)) + 1, int(round(y)), (190, 150, 110))
        elif u < 0.85:                                                # 落地扬土（两三点，慢慢散开）
            v = (u - 0.7) / 0.15
            bx, by = GULLY[-1]
            for (ox, oy) in ((-1, -1), (1, -2), (2, -1), (-2, -2)):
                if hash01(i, ox, oy, int(v * 3), 299) < 0.8:
                    px(d, bx + int(ox * (1 + v * 2)), by + int(oy * (1 + v)), (210, 190, 156))
    return im


def pebbles_frame(t):
    return _peb_f(frame_of(t, N_PEB, FPS_PEB))


def rock_bits(d, x, y, r, seed, pal=ROCK):
    """一块碎石：椭圆，左上亮、右下暗，下沿描深色。"""
    rx, ry = r, max(1, int(r * hrange(0.55, 0.8, seed, 1)))
    ellipse(d, x - rx, y - 2 * ry, x + rx, y, pal[2])
    ellipse(d, x - rx, y - 2 * ry, x + rx - 1, y - 1, pal[3])
    if rx > 1:
        px(d, x - rx + 1, y - 2 * ry + 1, pal[4])
    hl(d, x - rx + 1, x + rx, y, ROCK_INK)
    px(d, x + rx, y - 1, pal[1])


def draw_talus(im):
    """崖脚的碎石坡：从崖脚往外一小坡（y 136–147），车道落地的那一段（x 84–110）留成平的。"""
    d = ImageDraw.Draw(im)
    for x in range(0, 136):
        if 84 <= x <= 110:
            top = EDGE - 1
        else:
            top = int(round(EDGE - 8 + 6 * (x / 136.0) ** 1.5 + math.sin(x * 0.3) * 1.2))
        for y in range(top, EDGE + 1):
            u = (y - top) / max(1, EDGE - top)
            c = GROUND_C[3] if u < 0.4 else GROUND_C[2]
            if hash01(x, y, 301) < 0.2:
                c = GROUND_C[1]
            px(d, x, y, c)
        px(d, x, top, GROUND_C[4])
    for i in range(46):
        x = int(hrange(2, 134, i, 302))
        if 84 <= x <= 110:
            continue
        y = int(hrange(EDGE - 6, EDGE + 1, i, 303))
        rock_bits(d, x, y, int(hrange(1, 4, i, 304)), 305 + i, pal=[ROCK, ROCK_R, ROCK_W][i % 3])


def draw_boulder(im):
    """从崖上掉下来的大落石：一块圆滚滚的砂岩（打光同崖壁），躺在路肩后沿，右下一片短影子。"""
    w, h = BOULDER[1] - BOULDER[0] + 8, 26
    m, z = P.blob(w, h, [(15, 17, 13, 9), (9, 14, 7, 6), (21, 12, 7, 6)], 311, noise=0.12, cell=5, base=h - 4)
    rgba, q = P.shade(m, z, ROCK, 311, light=(-0.55, -0.8, 0.6), bump=0.5, facet=0.16, fcell=6, dither=0.4, seam=0.4,
                      speck=0.03, outline=ROCK_INK)
    sel = m & (q >= 0) & (np.mgrid[0:h, 0:w][0] > 12)
    rgba[sel, :3] = np.array(ROCK_R, np.uint8)[q[sel]]                # 下半截是另一层（锈红）
    bim = P.img(rgba)
    ox, oy = BOULDER[0] - 2, EDGE + 1 - (h - 4) - 1
    P.cast_shadow(im, [(BOULDER[0] + 10, EDGE + 1), (BOULDER[1] + 8, EDGE + 1), (BOULDER[1] + 6, EDGE + 4),
                       (BOULDER[0] + 6, EDGE + 3)], level=0.85)
    im.alpha_composite(bim, (ox, oy))
    d = ImageDraw.Draw(im)
    line(d, [(ox + 12, oy + 8), (ox + 14, oy + 12), (ox + 13, oy + 16)], ROCK_INK)    # 一道裂纹
    px(d, ox + 15, oy + 12, ROCK[4])
    for k in range(5):                                                # 摔下来时碎的几块
        rock_bits(d, BOULDER[1] + 2 + k * 3, EDGE + (k % 2), 1 + k % 2, 320 + k)


def draw_rockfall_sign(d):
    """“当心落石”三角牌：红边白底、里面几块黑色落石 + 一道斜坡；灰色杆子。"""
    cx, cy = ROCKSIGN_C
    vl(d, cx, cy + 5, EDGE, (120, 124, 130))
    vl(d, cx + 1, cy + 5, EDGE, (86, 88, 94))
    for r in range(11):
        y = cy - 6 + r
        hw = r // 2 + 1
        hl(d, cx - hw, cx + hw + 1, y, (214, 52, 44))
        if 2 <= r <= 9:
            hl(d, cx - hw + 2, cx + hw - 1, y, (246, 244, 236))
    line(d, [(cx - 3, cy + 3), (cx + 3, cy - 1)], (40, 40, 44))
    for (ox, oy) in ((-1, 0), (1, 1), (0, 2)):
        px(d, cx + ox, cy + oy, (40, 40, 44))
    px(d, cx + 2, EDGE, (110, 96, 84))


def draw_guard_stones(d):
    """路肩后沿一排刷黑白道的护路石（山路上常见）。"""
    for x in range(160, RAIL[0] - 4, 14):
        if abs(x - ROCKSIGN_C[0]) < 4:
            continue
        rect(d, x, EDGE - 4, x + 4, EDGE, (236, 234, 226))
        rect(d, x, EDGE - 2, x + 4, EDGE - 1, (44, 42, 46))
        hl(d, x, x + 4, EDGE - 4, (250, 250, 246))
        vl(d, x + 4, EDGE - 4, EDGE, (180, 178, 172))
        px(d, x + 5, EDGE, (126, 112, 96))


def draw_guardrail(im):
    """波形钢护栏：立柱每 14 px（左亮右暗、顶上一点高光）、一条 W 形钢板（上亮 / 中暗 / 下亮三道 + 铆钉），
    左端往下弯进地里；两个反光片；x 268 附近被车撞过、凹进去一块（锈）。"""
    d = ImageDraw.Draw(im)
    x0, x1 = RAIL
    by = EDGE - 7                                                     # 钢板上沿
    for x in range(x0 + 4, x1, 14):
        vl(d, x, by - 1, EDGE, STEEL[2])
        vl(d, x + 1, by - 1, EDGE, STEEL[0])
        px(d, x, by - 2, STEEL[3])
        px(d, x + 2, EDGE, (120, 106, 90))                            # 影子
        px(d, x + 3, EDGE, (136, 122, 104))
    for x in range(x0, x1):
        dent = 1 if 266 <= x <= 272 else 0
        y = by + dent
        if x < x0 + 5:                                                # 左端往下弯进地里
            y = by + (x0 + 5 - x)
        hl(d, x, x, y, STEEL[3])
        px(d, x, y + 1, STEEL[2])
        px(d, x, y + 2, STEEL[0])
        px(d, x, y + 3, STEEL[1])
        px(d, x, y + 4, STEEL[2])
        px(d, x, y + 5, STEEL[0])
        if dent and hash01(x, 331) < 0.6:
            px(d, x, y + 2, (150, 92, 62))
    for x in range(x0 + 11, x1, 14):                                  # 铆钉
        px(d, x, by + 2, STEEL[3])
    for x in (x0 + 18, x0 + 60):                                      # 反光片
        rect(d, x, by + 1, x + 1, by + 3, (250, 196, 70))
    P.cast_shadow(im, [(x0, EDGE + 1), (x1, EDGE + 1), (x1, EDGE + 3), (x0 + 4, EDGE + 3)], level=0.6)


def draw_curve_sign(d):
    """弯道牌：黄底、两个黑色的大箭头（往右），黑边；两根细杆子立在护栏后面。"""
    cx, cy = SIGN_C
    x0, y0, x1, y1 = cx - 7, cy - 5, cx + 7, cy + 5
    for lx in (x0 + 2, x1 - 2):
        vl(d, lx, y1 + 1, EDGE - 1, (104, 106, 112))
    rect(d, x0, y0, x1, y1, (34, 34, 38))
    rect(d, x0 + 1, y0 + 1, x1 - 1, y1 - 1, (246, 206, 52))
    hl(d, x0 + 1, x1 - 1, y0 + 1, (252, 230, 120))
    for ox in (-4, 2):                                                # 两个 > 形箭头
        for k in range(4):
            px(d, cx + ox + k, cy - 3 + k, (34, 34, 38))
            px(d, cx + ox + k, cy + 3 - k, (34, 34, 38))
            px(d, cx + ox + k + 1, cy - 3 + k, (34, 34, 38))
            px(d, cx + ox + k + 1, cy + 3 - k, (34, 34, 38))


def draw_ground(im):
    """路肩（y 146–176）：压实的碎石土，低对比；两道车辙、碎石子、几撮矮干草；崖脚中午的一条短影子；
    最前面 177–179 是柏油路的边（白色路缘线）。"""
    a = np.array(im)
    nz = P.wnoise(W, H, 7, 341)
    big = P.wnoise(W, H, 40, 342)
    b = P.bayer(W, H)
    for y in range(EDGE + 1, ROAD):
        u = (y - EDGE) / float(ROAD - EDGE)
        lev = 2.6 - u * 0.5 + (nz[y] - 0.5) * 1.3 + (big[y] - 0.5) * 0.8
        for rut in (154, 158, 166, 171):                              # 车辙：压得更实（暗一级）
            if y == rut:
                lev -= 0.55
        L = np.clip(np.floor(lev + 0.5 + (b[y] - 0.5) * 0.9), 0, 4).astype(int)
        a[y, :, :3] = np.array(GROUND_C, np.uint8)[L]
        a[y, :, 3] = 255
    a[EDGE + 1, :, :3] = np.array(GROUND_C[1], np.uint8)              # 后沿一道暗（地面到边上往下折）
    for y in range(ROAD, H):
        a[y, :, :3] = np.array(ASPH, np.uint8)
        a[y, :, 3] = 255
    im.paste(P.img(a))
    d = ImageDraw.Draw(im)
    for x in range(W):
        px(d, x, ROAD, (226, 224, 214) if x % 23 else (196, 194, 186))
        if hash01(x, 343) < 0.15:
            px(d, x, ROAD + 2, (100, 98, 100))
    for i in range(170):                                              # 碎石子（1–2 px，颜色差一点）
        x = int(hrange(0, W, i, 344))
        y = int(hrange(EDGE + 2, ROAD - 1, i, 345))
        c = (GROUND_C[0], GROUND_C[4], (206, 192, 166), (150, 120, 96))[i % 4]
        px(d, x, y, c)
        if i % 5 == 0:
            px(d, x + 1, y, GROUND_C[1])
    for i in range(18):                                               # 矮干草（≤ 3 px）
        x = int(hrange(4, W - 4, i, 346))
        y = int(hrange(EDGE + 3, ROAD - 2, i, 347))
        P.grass_tuft(d, x, y, int(hrange(2, 4, i, 348)), 349 + i, col=(168, 150, 98), dark=(130, 112, 74),
                     light=(206, 190, 130))
    # 崖脚的短影子（中午，影子贴着崖脚）
    P.cast_shadow(im, [(0, EDGE + 1), (128, EDGE + 1), (122, EDGE + 5), (0, EDGE + 6)], level=0.75)


@lru_cache(maxsize=1)
def near_img():
    im = A._new(W, H)
    draw_ground(im)
    im.alpha_composite(wall_rgba())
    draw_talus(im)
    draw_boulder(im)
    d = ImageDraw.Draw(im)
    draw_rockfall_sign(d)
    draw_guard_stones(d)
    draw_curve_sign(d)
    draw_guardrail(im)
    im = A._grade(im, sat=0.96, val=1.0)
    return P.opaque(im)


# ============================================================ key：焦地 / 汽油 / 洞
@lru_cache(maxsize=1)
def scorch_img():
    """被火烧黑的一片地：中间炭黑、往外抖动成焦褐、最外一圈烤干发白的土；撒几点灰白的灰烬和几根烧剩的草梗。"""
    im = A._new(W, H)
    a = np.array(im)
    cx, cy = SCORCH_C
    rx, ry = SCORCH_R
    nz = A._fbm(W, H, 4, 351)
    b = P.bayer(W, H)
    for y in range(cy - ry - 2, cy + ry + 3):
        for x in range(cx - rx - 4, cx + rx + 5):
            dd = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + (nz[y, x] - 0.5) * 0.9
            if dd < 0.45:
                c = (40, 36, 38) if (nz[y, x] < 0.55 or b[y, x] < 0.5) else (58, 50, 48)
            elif dd < 0.8:
                c = (70, 58, 52) if b[y, x] < (0.8 - dd) * 3 else (100, 84, 70)
            elif dd < 1.15:
                c = (124, 104, 86) if b[y, x] < (1.15 - dd) * 2.5 else None
            else:
                c = None
            if c is not None:
                a[y, x, :3] = c
                a[y, x, 3] = 255
    im = P.img(a)
    d = ImageDraw.Draw(im)
    for i in range(26):
        x = int(cx + hrange(-rx * 0.8, rx * 0.8, i, 352))
        y = int(cy + hrange(-ry * 0.7, ry * 0.7, i, 353))
        px(d, x, y, (176, 170, 164) if i % 3 else (214, 210, 204))
    for i in range(5):
        x = int(cx + hrange(-rx * 0.6, rx * 0.6, i, 354))
        y = int(cy + hrange(-ry * 0.5, ry * 0.5, i, 355))
        line(d, [(x, y), (x + 1, y - 2)], (30, 26, 28))
    return im


EMB_BOX = (SCORCH_C[0] - SCORCH_R[0], SCORCH_C[1] - SCORCH_R[1] - 12, SCORCH_C[0] + SCORCH_R[0], SCORCH_C[1] + SCORCH_R[1])


@lru_cache(maxsize=None)
def _emb_f(f):
    """焦地上没灭的火星（一明一暗、橙 / 黄）+ 两缕往右上飘的细烟。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    cx, cy = SCORCH_C
    for i in range(9):
        x = int(cx + hrange(-14, 14, i, 361))
        y = int(cy + hrange(-4, 4, i, 362))
        v = 0.5 + 0.5 * math.sin(math.tau * f / N_EMB * (1 + i % 2) + hash01(i, 363) * 6)
        if v > 0.25:
            px(d, x, y, (255, 214, 96) if v > 0.75 else (236, 112, 40))
            if v > 0.85:
                px(d, x + 1, y, (200, 70, 30))
    for j, sx in enumerate((cx - 6, cx + 8)):
        for k in range(10):
            u = ((k + f * 0.75 + j * 3) % 10) / 10.0
            x = sx + int(round(u * 4 + math.sin(u * 6 + j) * 1.2))
            y = cy - 2 - int(u * 12)
            if hash01(j, k, f, 364) < 0.8 - u * 0.4:
                px(d, x, y, mix((150, 146, 146), (210, 210, 212), u))
    return im


def embers_frame(t):
    return _emb_f(frame_of(t, N_EMB, FPS_EMB))


PUDDLE_R = [(9, 3), (11, 3), (8, 2)]


@lru_cache(maxsize=1)
def oil_img():
    """三摊汽油：比地面暗一大截的油渍（边上一圈渗开的湿土色）+ 天光的一道亮边；
    崖面上顺着车道淌下来的油痕：几道深色发亮的竖条（亮边在左，跟着岩面往下流，碰到岩层台阶就积一点）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for (x, y), (rx, ry) in zip(ANCHORS['puddles'], PUDDLE_R):
        ellipse(d, x - rx - 2, y - ry - 1, x + rx + 2, y + ry + 1, (118, 98, 82))          # 渗开的湿土
        ellipse(d, x - rx, y - ry, x + rx, y + ry, (44, 38, 42))
        hl(d, x - rx + 2, x + rx - 3, y - ry, (126, 150, 176))                            # 远边反着天光
        px(d, x - rx + 1, y - ry + 1, (92, 104, 126))
    m = wall_mask()
    lm = lane_mask()
    na = np.array(near_img()).astype(np.float32)
    a = np.array(im)
    for (x0, y0, L, sd) in ((74, 44, 60, 1), (80, 70, 70, 2), (86, 52, 40, 3), (90, 96, 48, 4), (70, 100, 30, 5)):
        x = x0
        wide = 0
        for y in range(y0, min(EDGE, y0 + L)):
            if hash01(sd, y, 371) < 0.18:
                x += 1
            if not m[y, x]:
                continue
            wide = min(2, (y - y0) // 18)                                  # 越往下淌得越宽
            for xx in range(x - 1 - wide, x + 2 + wide):                   # 油浸湿的岩面：底下的岩色压暗（不是画黑线）
                if m[y, xx] and a[y, xx, 3] == 0:
                    a[y, xx, :3] = np.clip(na[y, xx, :3] * np.array((0.6, 0.56, 0.6)), 0, 255).astype(np.uint8)
                    a[y, xx, 3] = 255
            a[y, x, :3] = (46, 36, 34)                                     # 油线的芯
            a[y, x, 3] = 255
            if m[y, x - 1] and hash01(sd, y, 372) < 0.45:                  # 左边一线反光（光从左上）
                a[y, x - 1, :3] = (156, 134, 150) if hash01(sd, y, 374) < 0.5 else (120, 108, 120)
            if hash01(sd, y, 373) < 0.06 and lm[y, x]:                     # 碰到台阶积一小摊
                a[y + 1, x - 1:x + 2, :3] = (46, 36, 34)
                a[y + 1, x - 1:x + 2, 3] = 255
        yb = min(EDGE, y0 + L)
        if m[yb, x]:
            a[yb, x, :3] = (46, 36, 34)                                    # 末端一颗油滴 + 高光
            a[yb, x, 3] = 255
            a[yb - 1, x, :3] = (190, 176, 186)
    im = P.img(a)
    return im


SHEEN_BOXES = [('sheen%d' % i, (x - rx - 1, y - ry - 1, x + rx + 2, y + ry + 2))
               for i, ((x, y), (rx, ry)) in enumerate(zip(ANCHORS['puddles'], PUDDLE_R))]


@lru_cache(maxsize=None)
def _sheen_f(f):
    """油面上的彩虹油光：一道紫 / 绿 / 黄的弯带在油面上慢慢挪（8 帧一圈）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for i, ((x, y), (rx, ry)) in enumerate(zip(ANCHORS['puddles'], PUDDLE_R)):
        ph = (f / N_OIL + i * 0.3) % 1.0
        for k, col in enumerate(((170, 90, 170), (90, 170, 130), (210, 190, 90))):
            sx = int(round(x - rx + 2 + ((ph + k * 0.12) % 1.0) * (2 * rx - 4)))
            for j in range(3):
                yy = y - 1 + j
                xx = sx + (1 - j)
                if ((xx - x) / rx) ** 2 + ((yy - y) / ry) ** 2 < 0.8:
                    px(d, xx, yy, col)
    return im


def sheen_frame(t):
    return _sheen_f(frame_of(t, N_OIL, FPS_OIL))


@lru_cache(maxsize=1)
def hole_img():
    """tunnel 处挖开的洞：一个扁扁的黑洞（远边亮、近边暗），四周翻起来的土块（最高 5 px），往外裂开的几道缝。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    cx, cy = ANCHORS['tunnel']
    for (ang, L) in ((-0.3, 16), (0.4, 14), (2.8, 15), (3.5, 12), (1.6, 6), (4.7, 7)):     # 裂缝
        x, y = float(cx), float(cy)
        for k in range(L):
            x += math.cos(ang + hrange(-0.4, 0.4, k, 381))
            y += math.sin(ang + hrange(-0.4, 0.4, k, 382)) * 0.4
            px(d, int(round(x)), int(round(y)), (92, 78, 66))
    ellipse(d, cx - 12, cy - 4, cx + 12, cy + 4, (128, 104, 80))                          # 翻出来的湿土
    ellipse(d, cx - 9, cy - 3, cx + 9, cy + 3, (30, 24, 24))                               # 洞
    hl(d, cx - 6, cx + 6, cy - 3, (60, 48, 44))
    hl(d, cx - 7, cx + 7, cy + 3, (86, 68, 56))
    for i in range(10):                                                                    # 土块
        ang = hrange(0, math.tau, i, 383)
        x = int(round(cx + math.cos(ang) * hrange(11, 16, i, 384)))
        y = int(round(cy + math.sin(ang) * hrange(3.5, 5.5, i, 385)))
        r = int(hrange(1, 3, i, 386))
        ellipse(d, x - r, y - r - 1, x + r, y, (150, 124, 96))
        px(d, x - r + 1, y - r, (186, 160, 124))
        hl(d, x - r + 1, x + r, y, (96, 78, 62))
    return im


# ============================================================ 组装 / 导出
STRIPS = [('river', RIV_BOX, N_RIV, FPS_RIV, river_frame), ('eagle', EAGLE_BOX, N_EAGLE, FPS_EAGLE, eagle_frame)]
NEAR_STRIPS = [(n, b, N_SWAY, FPS_SWAY, sway_frame) for (n, b) in SWAY_BOXES] + \
              [('pebbles', PEB_BOX, N_PEB, FPS_PEB, pebbles_frame)]
KEY_STRIPS = [('embers', EMB_BOX, N_EMB, FPS_EMB, embers_frame, 'scorch')] + \
             [(n, b, N_OIL, FPS_OIL, sheen_frame, 'oil') for (n, b) in SHEEN_BOXES]


@lru_cache(maxsize=1)
def build():
    return dict(sky=sky_img(), clouds=clouds_img(), far=far_img(), near=near_img(), scorch=scorch_img(), oil=oil_img(),
                hole=hole_img())


def compose(t=0.5, state=None):
    st = state or {}
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    cl = R['clouds']
    bb = cl.getchannel('A').getbbox()
    cim, cy = cl.crop((0, bb[1], cl.width, bb[3])), bb[1]
    o = int(math.floor(t * CLOUD_VX)) % CLOUD_P
    big = Image.new('RGBA', (CLOUD_P * 2, cim.height))
    big.paste(cim, (0, 0))
    big.paste(cim, (CLOUD_P, 0))
    out.alpha_composite(big.crop((o, 0, o + W, cim.height)), (0, cy))
    out.alpha_composite(R['far'])
    for (n, box, nn, fps, fn) in STRIPS:
        paste(out, fn(t).crop(box), box[0], box[1])
    out.alpha_composite(R['near'])
    for (n, box, nn, fps, fn) in NEAR_STRIPS:
        paste(out, fn(t).crop(box), box[0], box[1])
    if st.get('scorch'):
        out.alpha_composite(R['scorch'])
        for (n, box, nn, fps, fn, key) in KEY_STRIPS[:1]:
            paste(out, fn(t).crop(box), box[0], box[1])
    if st.get('oil'):
        out.alpha_composite(R['oil'])
        for (n, box, nn, fps, fn, key) in KEY_STRIPS[1:]:
            paste(out, fn(t).crop(box), box[0], box[1])
    if st.get('hole'):
        out.alpha_composite(R['hole'])
    return out


def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0)]
    cim, cy = BJ.crop_rows(R['clouds'])
    layers.append(dict(type='wrap', image=ex.img('clouds', cim), period=CLOUD_P, k=0.0, y=cy, vx=CLOUD_VX))
    fim, fy = BJ.crop_rows(R['far'])
    layers.append(dict(type='static', image=ex.img('far', fim), x=0, y=fy))
    for (n, box, nn, fps, fn) in STRIPS:
        layers.append(ex.bake(n, box, nn, fps, fn, screen=False, k=1.0))
    nim, ny = BJ.crop_rows(R['near'])
    layers.append(dict(type='static', image=ex.img('near', nim), x=0, y=ny))
    for (n, box, nn, fps, fn) in NEAR_STRIPS:
        layers.append(ex.bake(n, box, nn, fps, fn, screen=False, k=1.0))
    sim, sy = BJ.crop_rows(R['scorch'])
    layers.append(dict(type='static', image=ex.img('scorch', sim), x=0, y=sy, key='scorch'))
    for (n, box, nn, fps, fn, key) in KEY_STRIPS[:1]:
        layers.append(ex.bake(n, box, nn, fps, fn, screen=False, k=1.0, key=key))
    oim, oy = BJ.crop_rows(R['oil'])
    layers.append(dict(type='static', image=ex.img('oil', oim), x=0, y=oy, key='oil'))
    for (n, box, nn, fps, fn, key) in KEY_STRIPS[1:]:
        layers.append(ex.bake(n, box, nn, fps, fn, screen=False, k=1.0, key=key))
    him, hy = BJ.crop_rows(R['hole'])
    layers.append(dict(type='static', image=ex.img('hole', him), x=0, y=hy, key='hole'))
    anchors = dict(ANCHORS)
    anchors.update(lane=[[int(round(lane_x(y))), y] for y in range(LANE_TOP[1], LANE_BOT[1] - 11, 23)] + [list(LANE_BOT)],
                   scorch=list(SCORCH_C), boulder=[(BOULDER[0] + BOULDER[1]) // 2, EDGE + 1],
                   rockfall_sign=list(ROCKSIGN_C), rail=dict(x0=RAIL[0], x1=RAIL[1]), edge=EDGE)
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    allkeys = {'oil': True, 'hole': True, 'scorch': True}
    P.check_no_black(ex, BJ, st, '山路 4 个时刻 × key 全关 / 全开 整屏都有画（没有露黑）', states=({}, allkeys))
    P.check_opaque(ex, '天空底图整张不透明', R['sky'], (0, 0, W, H))
    P.check_opaque(ex, '远景 y 124–147（谷底）整条不透明', R['far'], (0, 124, W, EDGE + 1))
    P.check_opaque(ex, '近景 路肩 + 路边（y 147–180）整条不透明', R['near'], (0, EDGE + 1, W, H))
    P.check_alpha_binary(ex, '近景只有 0 / 255 两种透明度', R['near'])
    na = np.array(R['near'])
    m = wall_mask()
    ex.checked('崖壁整块不透明（崖壁遮罩里的透明像素）', int((na[..., 3][m] != 255).sum()))
    for k in ('scorch', 'oil', 'hole'):
        P.check_alpha_binary(ex, 'key %s 只有 0 / 255 两种透明度' % k, R[k])
    P.check_strips(ex, BJ, STRIPS + NEAR_STRIPS + [s[:5] for s in KEY_STRIPS])
    P.check_wraps(ex, BJ, st)
    # 可走带平整：近景 y 150–176 里离地面均值太远的像素（碎石子 / 干草允许一点）
    lum = P.lum(na[..., :3].astype(np.float32))
    band = lum[150:ROAD]
    mu = float(np.median(band))
    ex.checked('可走带 y 150–176 平整（和地面中位数差 > 40 的像素）', int((np.abs(band - mu) > 40).sum()), limit=260)
    # key 的东西都是平的：洞 / 焦地 / 油摊在可走带里的高度不超过 14 px（人能踩过去，不和人物穿插）
    for k, c in (('hole', ANCHORS['tunnel']), ('scorch', SCORCH_C)):
        bb = R[k].getchannel('A').getbbox()
        ex.checked('key %s 的范围 %s 高 %d ≤ 16、包住中心点' % (k, list(bb), bb[3] - bb[1]),
                   int(bb[3] - bb[1] > 16) + int(not (bb[0] <= c[0] < bb[2] and bb[1] <= c[1] < bb[3])))
    oa = np.array(R['oil'])[..., 3] > 0
    ex.checked('key oil：三摊油都在 puddles 锚点上', sum(int(not oa[y, x]) for (x, y) in ANCHORS['puddles']))
    ex.checked('key oil：崖面上的油痕都在崖壁上（崖外的油痕像素）', int((oa[:EDGE - 1] & ~m[:EDGE - 1]).sum()))
    # 锚点
    out = 0
    for k in ('wheel', 'party_car', 'arrive', 'tunnel', 'spw_car'):
        x, y = ANCHORS[k]
        out += not (0 <= x < PW and WALK[0] <= y <= WALK[1])
    for (x, y) in ANCHORS['puddles']:
        out += not (0 <= x < PW and WALK[0] <= y <= WALK[1])
    x, y = ANCHORS['cliff_top']
    out += not (m[y + 2, x] and not m[max(0, y - 4), x])              # 崖顶点就在崖壁的上沿
    for y in range(LANE_TOP[1] + 2, EDGE):                            # 车道整条都在崖壁上
        out += int(not m[y, int(round(lane_x(y)))])
    x, y = SIGN_C                                                    # 弯道牌：中心周围 11×7 一半以上是黄色牌面
    sub = na[y - 3:y + 4, x - 5:x + 6]
    out += int(((sub[..., 0] > 200) & (sub[..., 2] < 120)).mean() < 0.5)
    out += int(not (RAIL[0] < SIGN_C[0] < RAIL[1]))
    ex.checked('锚点：站人的都在可走带里、cliff_top 在崖沿、车道在崖壁上、sign 在牌面上（不满足的条数）', out)
    for t in (0.0, 1.25, 3.4, 11.0):
        for s in ({}, allkeys, {'oil': True}, {'scorch': True, 'hole': True}):
            got = BJ.ref_render(st, ex.images, 0, t, s)
            ex.checked('山路 t=%.2f %s 导出 vs 直接拼' % (t, '+'.join(sorted(s)) or '-'), BJ.ndiff(got, compose(t, s)))
    ex.note('可走带亮度中位数 %.0f、标准差 %.1f；崖壁 y 108–146 标准差 %.1f' %
            (mu, float(band.std()), float(lum[108:EDGE][m[108:EDGE]].std())))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch5', 'after')
    os.makedirs(od, exist_ok=True)
    sheet = Image.new('RGB', (W * 2, H), (0, 0, 0))
    sheet.paste(compose(0.5).convert('RGB'), (0, 0))
    sheet.paste(compose(0.5, {'oil': True, 'hole': True, 'scorch': True}).convert('RGB'), (W, 0))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(os.path.join(od, 'mountain_road_solo.png'))
    print('ok')
