# -*- coding: utf-8 -*-
r"""cable_view —— 第3章 新加坡：缆车外景（过场用，新 key，2026-10-11 ch3）。一节缆车车厢挂在高高的缆绳上，下面是海。

320 单屏，ground 160，可走带 y 150–170（没人走动，只是给剧情摆人用）。白天，太阳在左上。
画面：
  天      渐变 + 左上的太阳光晕；云在海平线上一排、上面几朵小的（慢慢往左飘）
  远景    海平线 y 104：左边远处的花柏山（绿山 + 山顶白墙红顶的缆车站）、旁边港口的城市天际线 + 集装箱吊机；
          右边远处的圣淘沙（绿岛 + 沙滩 + 红屋顶 + 灯塔）
  海      y 104–180 大片的海（底色渐变 + 一层波光 strip：细浪一道道往右传、闪烁，2 s 闭合）+ 港口里慢慢开的船（wrap）
  缆绳    从左上斜到右下（y = 26 + (x − 170)·0.2，2 px 粗）+ 后面一根回程缆绳（往上 6 px，细、淡）
  缆车塔  x 288：钢桁架、顶上横担托着两根缆绳（托索轮组）、红白航空警示带，脚下一座混凝土墩子立在海里
  车厢    中心 (170, 70)，车身 60×40（x 140–199，y 50–89），吊臂 21 px 挂在缆绳上（挂钩两个轮子骑在索上）；
          配色和 cable_car 车里一样（红窗框 / 红车顶 / 奶油色车身 / 镀铬腰线 / 深红裙边 / 编号牌 17），
          透过 4 扇侧窗看得到对面的窗和一排青绿色椅背；第 3、4 扇窗里两个人影的剪影
图层（从后往前）：
  sky      static            天空渐变 + 太阳
  clouds   wrap  vx 3        云（640 循环）
  far      static            远山 / 城市 / 圣淘沙 / 海平线 / 海面底色（海平线以下不透明）
  sea      strip 12 帧 @6fps 波光（screen，2 s 闭合）
  boats    wrap  vx 3        港口里的船（640 循环，透明底）
  rig      static            回程缆绳 + 缆绳 + 缆车塔 + 塔墩
  car      static            车厢（完好）
  win      pick  key 'win'   0 = 完好（两个人影）；1 = 最右那扇窗被撞碎（玻璃没了、看得穿到车里，窗框一圈锯齿碎玻璃，
                             人影只剩中间那扇窗里一个）——两张只在那扇窗附近不同
  shards   strip key 'win'   12 帧 @6fps：碎玻璃从破窗往下掉、一闪一闪、落进海里（state.win 为真才画；2 s 一圈接着掉）
  gulls    clouds            两只海鸥
锚点：car [170,70]（车厢中心）、car_win（被撞碎那扇窗的中心）、splash（车窗正下方的海面落水点）、
      tower [288,50]、cable [[0,y0],[320,y1]]、horizon 104。
单独运行：python -B tools\bg_new\cable_view.py → tools\bg_new\_preview\ch3\after\cable_view_solo*.png
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


def _cable_car_mod():
    """车厢外观 / 调色 / 船 / 远山跟 cable_car.py 共用（同一个模块名，bg_jojo.bg_new('cable_car') 会直接复用）。"""
    key = 'bg_new_cable_car'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'cable_car.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


CC = _cable_car_mod()
C = A._c4
dk, hl, vl, px, rect = CC.dk, CC.hl, CC.vl, CC.px, CC.rect

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
GROUND = 160
WALK = (150, 170)
HZ = 104
CAR_W, CAR_H, HANGER = 60, 40, 21
CAR_C = (170, 70)
CABLE_K = 0.2
CABLE_Y0 = 26                    # 缆绳（上沿）在 x 170 处的 y
RET_DY = -6                      # 回程缆绳往上偏多少
TOWER_X = 288
N_SEA, FPS_SEA = 12, 6.0         # 波光 2 s
N_SH, FPS_SH = 12, 6.0           # 碎玻璃 2 s
SEA_BOX = (0, HZ + 1, W, H)
BROKEN = 3                       # 撞碎的是最右那扇窗


def cable_y(x):
    return CABLE_Y0 + (x - CAR_C[0]) * CABLE_K


def sea_color(y):
    u = max(0.0, min(1.0, (y - HZ) / (H - HZ))) * (len(CC.SEA) - 1)
    i = min(len(CC.SEA) - 2, int(u))
    return mix(CC.SEA[i], CC.SEA[i + 1], u - i)


def frame_of(t, n, fps):
    return int(math.floor(t * fps + 1e-6)) % n


# ============================================================ 天 / 云
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, HZ + 2), [(58, 120, 196), (78, 142, 212), (110, 170, 226), (156, 200, 234), (204, 226, 236)],
             bands=12)
    gradient(im, (0, HZ + 2, W, H), CC.SEA, bands=8)
    A._glow(im, 46, 22, 40, 34, (255, 246, 214), 56, rings=5)
    d = ImageDraw.Draw(im)
    d.ellipse((39, 15, 53, 29), fill=C((255, 248, 224)))
    d.ellipse((41, 17, 51, 27), fill=C((255, 254, 246)))
    return im


@lru_cache(maxsize=1)
def clouds_img():
    """640 循环：海平线上一排平底积云（被远山挡住下半截）+ 天上几朵小的。返回 (图, y0)。"""
    y0, y1 = 6, HZ - 2
    im = A._new(640, y1 - y0)
    pal = ((255, 255, 255), (238, 244, 250), (208, 224, 240), (186, 206, 230))
    for i in range(7):
        w = hrange(46, 96, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.26, 0.34, i, 2), 800 + i, pal)
        cx = (i + hrange(0.15, 0.85, i, 3)) * 640 / 7
        y = (y1 - y0) - 4 - cl.height + int(hrange(-4, 2, i, 4))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    pal2 = ((255, 255, 255), (232, 240, 250), (204, 220, 240), (182, 202, 230))
    for i in range(6):
        w = hrange(18, 40, i, 11)
        cl = A._cloud_sprite(w, w * 0.32, 900 + i, pal2)
        cx = (i + hrange(0.1, 0.9, i, 12)) * 640 / 6
        y = int(hrange(4, 46, i, 13))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    return im, y0


# ============================================================ 远景（static）
@lru_cache(maxsize=1)
def far_img():
    im = A._new(W, H)
    gradient(im, (0, HZ, W, H), CC.SEA, bands=12)
    d = ImageDraw.Draw(im)
    # 港口天际线（花柏山后面 / 右边）+ 吊机 + 码头
    CC._skyline(d, 84, 196, 23, hz=HZ)
    for (cx_, h_) in ((126, 11), (135, 12), (201, 10)):              # 吊机避开车厢正下方（不然像车底挂着东西）
        CC._crane(d, cx_, h_, hz=HZ)
    for x in list(range(122, 146)) + list(range(196, 214)):
        col = [(176, 132, 120), (140, 160, 176), (190, 176, 140), (150, 170, 150)][int(hash01(x // 3, 61) * 4)]
        if hash01(x // 3, 62) < 0.8:
            px(d, x, HZ - 2, mix(col, CC.HAZE, 0.35))
        px(d, x, HZ - 1, (150, 160, 168))
    a = np.array(im)
    # 花柏山（左，远处的绿山）
    CC._hills(a, 0, 124, HZ, [(14, 22, 20), (48, 32, 22), (86, 16, 16), (110, 7, 10)], 13,
              (128, 172, 128), (108, 154, 116), (90, 134, 106), (156, 194, 150), (164, 194, 186))
    # 圣淘沙（右）
    CC._hills(a, 212, 320, HZ, [(232, 9, 10), (258, 17, 14), (288, 13, 14), (312, 8, 10)], 17,
              (112, 162, 112), (90, 140, 98), (70, 116, 86), (140, 186, 132), (150, 184, 170))
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 花柏山顶的缆车站：白墙、红屋顶、黑洞洞的出索口，往右下伸出一截（缆绳就从这里出来）
    sx, sy = 44, HZ - 32
    rect(d, sx - 7, sy - 4, sx + 8, sy + 1, (232, 230, 220))
    hl(d, sx - 8, sx + 9, sy - 5, (196, 92, 76))
    hl(d, sx - 7, sx + 8, sy - 6, (176, 80, 66))
    rect(d, sx + 4, sy - 3, sx + 7, sy, (60, 62, 72))
    for k in range(sx - 5, sx + 3, 3):
        px(d, k, sy - 2, (120, 140, 160))
    vl(d, sx - 4, sy + 2, sy + 6, (200, 200, 196))                  # 山上的白色小塔
    # 山上零星的白房子
    for (hx, hy) in ((20, HZ - 12), (28, HZ - 8), (70, HZ - 14), (96, HZ - 6), (104, HZ - 4)):
        rect(d, hx, hy, hx + 2, hy + 1, (226, 226, 216))
        hl(d, hx, hx + 2, hy - 1, (186, 104, 90))
    # 圣淘沙：沙滩、红屋顶、灯塔、椰树
    for x in range(216, 320):
        if hash01(x // 4, 71) < 0.82:
            px(d, x, HZ - 1, (236, 222, 180))
        if hash01(x // 5, 72) < 0.35:
            px(d, x, HZ - 2, (226, 214, 176))
    for (hx, hy) in ((226, HZ - 4), (231, HZ - 4), (250, HZ - 6), (276, HZ - 5), (281, HZ - 4), (300, HZ - 4)):
        rect(d, hx, hy, hx + 2, hy + 1, (232, 230, 220))
        hl(d, hx, hx + 2, hy - 1, (196, 104, 86))
    vl(d, 260, HZ - 23, HZ - 16, (236, 236, 230))
    px(d, 261, HZ - 21, (200, 200, 196))
    px(d, 260, HZ - 24, (214, 92, 70))
    for (tx, ty) in ((220, HZ - 3), (243, HZ - 3), (268, HZ - 3), (292, HZ - 3), (311, HZ - 3)):
        vl(d, tx, ty - 3, ty, (96, 112, 90))
        hl(d, tx - 1, tx + 1, ty - 4, (80, 128, 86))
        px(d, tx - 2, ty - 3, (80, 128, 86))
        px(d, tx + 2, ty - 3, (80, 128, 86))
    for (sx_, L) in ((200, 7), (126, 5)):                            # 海平线上远远的船
        hl(d, sx_, sx_ + L, HZ - 1, (120, 138, 150))
        rect(d, sx_ + L - 2, HZ - 3, sx_ + L - 1, HZ - 2, (150, 164, 172))
    hl(d, 0, W - 1, HZ, (214, 232, 230))
    hl(d, 0, W - 1, HZ + 1, (184, 212, 210))
    # 静止的长涌（很淡的深色长条；会动的波光另有 strip）
    for i in range(60):
        y = HZ + 3 + int(hash01(i, 81) ** 1.25 * (H - HZ - 4))
        u = (y - HZ) / (H - HZ)
        x = int(hrange(-30, W, i, 82))
        L = int(hrange(12, 44, i, 83) * (0.5 + u))
        hl(d, max(0, x), min(W - 1, x + L), y, dk(sea_color(y), 0.92))
    # 太阳在海面上的一条反光带（左边）
    for i in range(40):
        y = HZ + 2 + int(hash01(i, 84) ** 1.5 * 50)
        x = int(46 + hrange(-10, 10, i, 85) * (0.4 + (y - HZ) / 30))
        L = int(hrange(2, 6, i, 86))
        hl(d, x, x + L, y, mix(sea_color(y), (236, 244, 236), 0.45 - (y - HZ) / 160))
    return im


# ============================================================ 海：波光（strip）+ 船（wrap）
def sea_frame(t):
    """整片海面的细浪：每道浪花按 x 有相位（一道一道往右传），上下起伏 1 px、长短一呼一吸；近处“亮线 + 下面一道暗线”。
    太阳那边（左）的浪花偏亮。12 帧 2 s 严格闭合。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = frame_of(t, N_SEA, FPS_SEA)
    ph0 = math.tau * f / N_SEA
    for i in range(300):
        y = HZ + 2 + int(hash01(i, 1, 5) ** 1.4 * (H - HZ - 3))
        u = (y - HZ) / (H - HZ)
        x = int(hrange(-8, W, i, 2, 5))
        L0 = (2 + 11 * u) * hrange(0.6, 1.3, i, 3, 5)
        ph = ph0 + x * 0.045 + hash01(i, 4, 5) * 1.4
        dy = int(round((0.3 + 1.2 * u) * math.sin(ph)))
        L = int(round(L0 * (0.5 + 0.5 * math.cos(ph))))
        if L <= 0:
            continue
        sea = sea_color(y + dy)
        sun = max(0.0, 1 - abs(x - 46) / 70) * max(0.0, 1 - u * 1.6)
        lite = mix(mix(sea, (232, 246, 244), 0.4 - 0.12 * u), (255, 250, 230), sun * 0.5)
        if hash01(i, 5, 5) < 0.7:
            hl(d, x, x + L, y + dy, lite)
            if u > 0.35:
                hl(d, x + 1, x + L - 1, y + dy + 1, dk(sea, 0.84))
        else:
            hl(d, x, x + L, y + dy, dk(sea, 0.86))
    return im


BOATS = [  # (kind, x, waterline, haze, 尾迹)
    ('cargo', 380, 112, 0.35, 0), ('box', 560, 108, 0.5, 0), ('bumboat', 90, 126, 0.15, 10),
    ('tug', 250, 144, 0.04, 20), ('ferry', 470, 160, 0.0, 26), ('sampan', 30, 168, 0.0, 6),
]
BOAT_P, BOAT_VX, BOAT_Y0 = 640, 3.0, HZ + 1


@lru_cache(maxsize=1)
def boats_img():
    im = A._new(BOAT_P, H - BOAT_Y0)
    d = ImageDraw.Draw(im)
    for (kind, x, wy, hz, wk) in BOATS:
        if wk:
            CC._wake(d, x + {'tug': 12, 'ferry': 20, 'bumboat': 16, 'sampan': 9}.get(kind, 10), wy, wk, 1, BOAT_Y0,
                     mix((246, 252, 250), sea_color(wy), 0.15), sea_color(wy))
        CC._ship(d, kind, x, wy, BOAT_Y0, hz)
    return im


# ============================================================ 缆绳 + 缆车塔（static）
ST_C = (104, 112, 124)
ST_HI = (156, 164, 176)
ST_D = (72, 78, 90)


@lru_cache(maxsize=1)
def rig_img():
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    # 回程缆绳（远，细、淡）
    for x in range(W):
        y = int(round(cable_y(x) + RET_DY))
        if 0 <= y < H:
            px(d, x, y, (96, 104, 120))
    # 缆车塔：钢桁架、顶上横担托着两根缆绳、红白警示带；脚下混凝土墩子立在海里
    cx = TOWER_X
    top = int(round(cable_y(cx))) + 4                                # 横担在缆绳下面
    bot = 150

    def leg_x(y, side):
        u = (y - top) / (bot - top)
        return cx + side * (6 + 11 * u)
    for side in (-1, 1):
        for y in range(top, bot + 1):
            x = int(round(leg_x(y, side)))
            px(d, x, y, ST_HI if side < 0 else ST_D)
            px(d, x + side, y, ST_C)
    yy, k = top + 3, 0
    while yy < bot - 2:
        y2 = min(bot, yy + 9 + k * 2)
        d.line((leg_x(yy, -1), yy, leg_x(y2, 1), y2), fill=C(ST_C))
        d.line((leg_x(yy, 1), yy, leg_x(y2, -1), y2), fill=C(ST_D))
        hl(d, int(leg_x(y2, -1)), int(leg_x(y2, 1)), y2, ST_C)
        yy, k = y2, k + 1
    for y in range(top, top + 10):                                    # 红白航空警示带
        for side in (-1, 1):
            x = int(round(leg_x(y, side)))
            c = (214, 70, 56) if (y // 3) % 2 == 0 else (236, 234, 228)
            px(d, x, y, c)
            px(d, x + side, y, dk(c, 0.85))
    ya = top - 1                                                     # 横担（托两根缆绳）
    rect(d, cx - 14, ya, cx + 14, ya + 2, ST_C)
    hl(d, cx - 14, cx + 14, ya, ST_HI)
    hl(d, cx - 14, cx + 14, ya + 2, ST_D)
    for (off, dy) in ((-7, RET_DY), (6, 0)):                          # 两组托索轮（在各自的缆绳下面）
        xs = cx + off
        yc = int(round(cable_y(xs) + dy)) + 2
        rect(d, xs - 5, yc + 2, xs + 5, yc + 2, ST_D)
        vl(d, xs, yc + 3, ya - 1, ST_D)
        for wx in range(xs - 4, xs + 5, 4):
            d.ellipse((wx - 1, yc, wx + 1, yc + 2), fill=C((60, 64, 74)), outline=C(ST_HI))
    vl(d, cx, top + 2, bot - 2, ST_HI)                                # 检修梯
    for y in range(top + 4, bot - 2, 3):
        px(d, cx + 1, y, ST_C)
    # 混凝土墩子（立在海里）+ 拍在墩子上的浪
    d.polygon([(cx - 21, bot), (cx + 21, bot), (cx + 23, bot + 9), (cx - 23, bot + 9)], fill=C((178, 172, 160)))
    hl(d, cx - 21, cx + 21, bot, (214, 208, 196))
    for x in range(cx - 22, cx + 23):
        px(d, x, bot + 6, (130, 126, 118))
        px(d, x, bot + 7, (112, 120, 112))
        px(d, x, bot + 8, (90, 110, 110))
    vl(d, cx - 21, bot, bot + 8, (220, 214, 202))
    for x in range(cx - 25, cx + 26):
        if hash01(x, 91) < 0.7:
            px(d, x, bot + 9, (232, 244, 242))
        if hash01(x, 92) < 0.35:
            px(d, x, bot + 10, (200, 228, 228))
    # 缆绳（近，2 px，上沿一排反光点）
    for x in range(W):
        y = int(round(cable_y(x)))
        if 0 <= y < H - 1:
            px(d, x, y, (56, 60, 70) if x % 3 else (128, 136, 150))
            px(d, x, y + 1, (40, 42, 52))
    return im


# ============================================================ 车厢
@lru_cache(maxsize=2)
def car_img(state):
    """返回 (车厢 sprite, 左上角的屏幕坐标, 车身框, 各窗框)。"""
    people = (2, 3) if state == 0 else (2,)
    im, (gx, gy), body, panes = CC.gondola(CAR_W, CAR_H, HANGER, panes=4, people=people,
                                          broken=(BROKEN if state else None), slope=CABLE_K, num='17')
    ox = CAR_C[0] - gx
    oy = int(round(cable_y(CAR_C[0]))) - gy
    return im, (ox, oy), body, panes


def car_layer(state):
    im, (ox, oy), _, _ = car_img(state)
    out = A._new(W, H)
    paste(out, im, ox, oy)
    return out


def _pick_box():
    a0 = np.array(car_layer(0))
    a1 = np.array(car_layer(1))
    diff = (a0 != a1).any(-1)
    ys, xs = np.nonzero(diff)
    return (int(xs.min()) - 1, int(ys.min()) - 1, int(xs.max()) + 2, int(ys.max()) + 2)


def car_win():
    _, (ox, oy), _, panes = car_img(1)
    x0, y0, x1, y1 = panes[BROKEN]
    return [ox + (x0 + x1) // 2, oy + (y0 + y1) // 2]


def splash_pt():
    cw = car_win()
    return [cw[0], 150]


# ============================================================ 碎玻璃往下掉（strip，key 'win'）
def shard_box():
    cw = car_win()
    return (cw[0] - 22, cw[1] + 2, cw[0] + 30, 154)


def shards_frame(t):
    """碎玻璃从破窗往下掉：10 片错开相位，带一点往外的初速度、加速往下，一闪一闪（亮 / 青交替），掉到海面溅一个小白点。
    12 帧 2 s 一圈（state.win 为真时一直在掉）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = frame_of(t, N_SH, FPS_SH)
    cw = car_win()
    sx0, sy0 = cw[0], cw[1] + 6
    sea_y = splash_pt()[1]
    T = N_SH / FPS_SH
    for i in range(12):
        ph = (f / N_SH + hash01(i, 101)) % 1.0
        tau = ph * T
        vx = hrange(-4, 12, i, 102)
        g = hrange(70, 95, i, 103)
        x = sx0 + hrange(-5, 5, i, 104) + vx * tau
        y = sy0 + hrange(-2, 3, i, 105) + 0.5 * g * tau * tau
        if y >= sea_y:
            if y < sea_y + 14:                                        # 落水：溅一个小白点
                px(d, round(x), sea_y, (240, 250, 250))
                px(d, round(x) - 1, sea_y + 1, (200, 232, 232))
                px(d, round(x) + 1, sea_y + 1, (200, 232, 232))
            continue
        xi, yi = int(round(x)), int(round(y))
        glint = (f + i) % 3 == 0
        big = hash01(i, 106) < 0.55
        col = (255, 255, 255) if glint else (190, 230, 244)
        edge = (54, 100, 132)
        if not big:
            px(d, xi, yi, col)
            px(d, xi + 1, yi, edge)
            px(d, xi, yi + 1, edge)
        else:                                                         # 三角碎片翻着往下掉（两种朝向交替）
            pts = [(xi, yi), (xi + 2, yi - 1), (xi + 1, yi + 2)] if (f + i) % 2 else [(xi, yi - 1), (xi + 2, yi + 1), (xi - 1, yi + 1)]
            d.polygon(pts, fill=C(col), outline=C(edge))
            px(d, pts[0][0], pts[0][1], (255, 255, 255) if glint else col)
    return im


# ============================================================ 海鸥
GULLS = [(40, 5.0, 40.0), (97, 3.5, 260.0)]      # (y, vx, x0)：一只在高处，一只贴着海平线上面（都避开车厢）


def gull_img(dark=False):
    g = A._new(7, 3)
    d = ImageDraw.Draw(g)
    c = (250, 250, 250) if not dark else (90, 96, 110)
    for (x, y) in ((0, 1), (1, 0), (2, 0), (4, 0), (5, 0), (6, 1)):
        px(d, x, y, c)
    px(d, 3, 1, (210, 214, 222))
    px(d, 0, 2, (120, 126, 140))
    px(d, 6, 2, (120, 126, 140))
    return g


# ============================================================ 导出
@lru_cache(maxsize=1)
def build():
    box = _pick_box()
    picks = [car_layer(s).crop(box) for s in (0, 1)]
    return dict(sky=sky_img(), clouds=clouds_img(), far=far_img(), boats=boats_img(), rig=rig_img(),
                car=car_layer(0), pick_box=box, picks=picks)


def export(ex, BJ):
    R = build()
    ci, cy = R['clouds']
    gk = ex.img('gull', gull_img())
    fim, fy = BJ.crop_rows(R['far'])
    rim, ry = BJ.crop_rows(R['rig'])
    cim, cyy = BJ.crop_rows(R['car'])
    box = R['pick_box']
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0),
              dict(type='wrap', image=ex.img('clouds', ci), period=640, k=0.0, y=cy, vx=3.0),
              dict(type='static', image=ex.img('far', fim), x=0, y=fy),
              ex.bake('sea', SEA_BOX, N_SEA, FPS_SEA, sea_frame),
              dict(type='wrap', image=ex.img('boats', R['boats']), period=BOAT_P, k=0.0, y=BOAT_Y0, vx=BOAT_VX),
              dict(type='static', image=ex.img('rig', rim), x=0, y=ry),
              dict(type='static', image=ex.img('car', cim), x=0, y=cyy),
              dict(type='pick', images=[ex.img('win%d' % i, im) for i, im in enumerate(R['picks'])], key='win',
                   values=[0, 1], x=box[0], y=box[1], k=0.0),
              ex.bake('shards', shard_box(), N_SH, FPS_SH, shards_frame, key='win'),
              dict(type='clouds', span=W + 200, clouds=[dict(image=gk, x0=x0, y=y, vx=vx, k=0.0) for (y, vx, x0) in GULLS])]
    _, (ox, oy), body, _ = car_img(0)
    anchors = dict(car=list(CAR_C), car_win=car_win(), splash=splash_pt(),
                   car_box=[ox + body[0], oy + body[1], ox + body[2] + 1, oy + body[3] + 1], win_box=list(box),
                   tower=[TOWER_X, int(round(cable_y(TOWER_X)))],
                   cable=[[0, round(cable_y(0), 1)], [W, round(cable_y(W), 1)]], horizon=HZ, walk_x=[40, 280])
    st = ex.stage(W, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R, anchors)
    return st


def compose(t, win=0, gulls=True):
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    ci, cy = R['clouds']
    o = int(math.floor(t * 3.0)) % 640
    out.alpha_composite(CC._tile(ci, 1280).crop((o, 0, o + W, ci.height)), (0, cy))
    out.alpha_composite(R['far'])
    out.alpha_composite(sea_frame(t).crop(SEA_BOX), SEA_BOX[:2])
    o = int(math.floor(t * BOAT_VX)) % BOAT_P
    out.alpha_composite(CC._tile(R['boats'], BOAT_P * 2).crop((o, 0, o + W, R['boats'].height)), (0, BOAT_Y0))
    out.alpha_composite(R['rig'])
    out.alpha_composite(R['car'])
    box = R['pick_box']
    out.alpha_composite(R['picks'][1 if win else 0], box[:2])
    if win:
        sb = shard_box()
        out.alpha_composite(shards_frame(t).crop(sb), sb[:2])
    if gulls:
        g = gull_img()
        for (y, vx, x0) in GULLS:
            x = (x0 + t * vx) % (W + 200) - 100
            paste(out, g, math.floor(x), y)
    return out


def _checks(ex, BJ, st, R, anchors):
    bad = 0
    for t in (0.0, 0.5, 1.25, 7.0):
        for s in (0, 1):
            im = np.array(BJ.ref_render(st, ex.images, 0, t, dict(win=s)).convert('RGB'))
            bad += int((im.sum(-1) == 0).sum())
    ex.checked('缆车外景 t × win 0/1 整屏都有画（没有露黑）', bad)
    ex.checked('天空底图整张不透明', int((np.array(R['sky'])[..., 3] != 255).sum()))
    box = R['pick_box']
    ex.checked('win pick 两张尺寸一致', 0 if R['picks'][0].size == R['picks'][1].size else 1)
    ex.checked('win pick 两张都整块不透明（盖得住下面的车厢）', int((np.array(R['picks'][0])[..., 3] < 255).sum() +
                                                  (np.array(R['picks'][1])[..., 3] < 255).sum()))
    _, (ox, oy), _, panes = car_img(1)
    px0, py0, px1, py1 = panes[BROKEN]
    near = (ox + px0 - 4, oy + py0 - 4, ox + px1 + 5, oy + py1 + 5)
    ex.checked('win 两态的差异都在那扇窗附近（pick 框 %s ⊂ 窗框外扩 4 px %s）' % (list(box), list(near)),
               0 if (box[0] >= near[0] and box[1] >= near[1] and box[2] <= near[2] and box[3] <= near[3]) else 1)
    g0 = BJ.ref_render(st, ex.images, 0, 1.0, dict(win=0), only={'static', 'wrap', 'pick'})
    g1 = BJ.ref_render(st, ex.images, 0, 1.0, dict(win=1), only={'static', 'wrap', 'pick'})
    dm = (np.abs(np.asarray(g0.convert('RGB'), np.int16) - np.asarray(g1.convert('RGB'), np.int16)).max(-1) > 0)
    inb = np.zeros_like(dm)
    inb[box[1]:box[3], box[0]:box[2]] = True
    ex.checked('win 两态（不算碎玻璃 strip）只在框里不同（框外差异像素）', int((dm & ~inb).sum()),
               extra='框内差 %d px' % int((dm & inb).sum()))
    ex.checked('win 两态在框内确实不同', 0 if int((dm & inb).sum()) > 60 else 1)
    for name, bx, fn, n, fps in (('sea', SEA_BOX, sea_frame, N_SEA, FPS_SEA), ('shards', shard_box(), shards_frame, N_SH, FPS_SH)):
        ex.checked('strip %s 闭合（t=0 vs t=%g）' % (name, n / fps), BJ.ndiff_rgba(fn(0.0).crop(bx), fn(n / fps).crop(bx)))
        ex.checked('strip %s 帧条宽 ≤ 4096' % name, 0 if (bx[2] - bx[0]) * n <= 4096 else 1)
    ex.checked('wrap 图宽 = period（云 640 / 船 640）', int(R['clouds'][0].width != 640) + int(R['boats'].width != BOAT_P))
    out = 0
    for k in ('car', 'car_win', 'splash', 'tower'):
        v = anchors[k]
        out += not (0 <= v[0] <= W and 0 <= v[1] <= H)
    ex.checked('锚点都在地图里（不满足的条数）', out)
    cw, sp = anchors['car_win'], anchors['splash']
    ex.checked('splash 在破窗正下方、在海面上（y > 海平线）', 0 if (sp[0] == cw[0] and sp[1] > HZ + 10) else 1)
    # 车挂在缆绳上：挂钩那一列的缆绳就在 sprite 的挂钩位置
    im, (ox_, oy_), _, _ = car_img(0)
    ex.checked('车厢中心 ≈ (170, 70)（车身框中心偏差 px）',
               abs((anchors['car_box'][0] + anchors['car_box'][2]) / 2 - CAR_C[0]) +
               abs((anchors['car_box'][1] + anchors['car_box'][3]) / 2 - CAR_C[1]), limit=1)
    for s in (0, 1):
        for t in (0.0, 1.25, 3.4, 11.0):
            got = BJ.ref_render(st, ex.images, 0, t, dict(win=s))
            ex.checked('缆车外景 win=%d t=%.2f 导出 vs 直接拼' % (s, t), BJ.ndiff(got, compose(t, s)))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch3', 'after')
    os.makedirs(od, exist_ok=True)
    compose(1.0, 0).convert('RGB').resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(od, 'cable_view_solo.png'))
    compose(1.0, 1).convert('RGB').resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(od, 'cable_view_solo_broken.png'))
    print('ok', car_win(), splash_pt(), _pick_box())
