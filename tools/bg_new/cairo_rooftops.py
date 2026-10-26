# -*- coding: utf-8 -*-
r"""cairo_rooftops —— 终章 28B / 28C：开罗夜里连成一片的平屋顶（地图 roof_fin：花京院布触须网、钟楼、水塔、烟囱）。
2026-10-19 cairo 组按体验版精度重画（改前是 later_stages 里的平涂方块）。零件和图层表 / 自检借 cairo_parts.py。

地图 640 宽、ground 156、可走带 y 145–176（屋顶的水泥面：方砖 + 沥青缝，对比压得很低）；侧视平视，夜里，月亮在天上
偏左（画面坐标 (200, 36)，镜头在哪都一样），月光从左上来。屋顶后沿一道矮墙（y 136–144），东西都立在后沿（脚 y 144）。
从左到右（世界坐标）：
  x   0–32   楼梯间小屋（arrive 40：从这里上来）：门开着、里面亮、门顶一盏灯泡（飞虫 strip）
  x  34–100  晾衣绳（两根木杆 x 58 / 96，衣服 strip）；绳下一把塑料椅、几盆花
  x 102–130  鸽舍（木条塔 + 网，鸽子睡了）、顶上一根挂破布的竹竿（节点 2 在竿顶）
  x 141–169  钟楼（clock [155,105]、clock_face [155,105,7]）：方柱身、钟面只画表盘 + 时针（分针剧情画，会跳一格），
             尖顶 + 小旗杆；key clock_broken：钟面碎了（裂纹、掉了几块、露出里面的黑）
  x 172–236  一只架在角钢上的小水箱（节点 3 在箱盖把手）、靠墙堆的木箱、破沙发
  x 240–292  高高的电视天线杆（三根拉线，节点 4 在杆顶，杆顶一盏一闪一闪的红灯 strip）、天窗小盒子
  x 292–360  空着的一段屋顶（DIO 悬在 dio_air [320,90]，背后只有天和远处的城）；一根弯头通风管（节点 5 在管口）
  x 370–390  砖烟囱（chimney [380,118] = 烟囱帽的顶，节点 6 在烟囱口）；key chimney_broken：上半截被打断、砖块撒了一地
  x 404–466  又一根晾衣绳（木杆 x 414 / 452，节点 7 在 452 的杆顶，衣服 strip）
  x 472–512  水塔（tank [492,146] = 塔脚；铁皮圆罐 + 铆钉 + 爬梯 + 四根角钢腿）；key tank_burst：罐身被打穿一个洞、
             水从洞里涌出来浇到屋顶（strip，key 同名）、地上一摊水
  x 522–574  第二间楼梯小屋（窗里亮着、门关着）、屋顶的天线（节点 8 在天线顶）、一只蹲在水箱上的猫（尾巴 strip）
  x 576–626  花盆、一摞砖、铁栏杆；edge [620,150] = 屋顶右边的边（再往右是楼缝）
  x 627–640  楼缝：往下看是对面楼的亮窗、最下面是街上的暖光
远景：满城的夜（远处的楼、宣礼塔的绿灯、电视塔）；中景：邻家的屋顶（水箱、天线、晾衣、一座近一点的宣礼塔）。
key red_sky：乔瑟夫倒下时的血红天空（天换成血红的那张，月亮也变红）。

图层（从后往前）：
  sky        pick  key red_sky（0 夜空 / 1 血红）  320×180，k 0
  clouds     wrap  k 0.05 vx 0.6     夜里的薄云
  far        pano  k 0.3             远处的城（cairo_parts.far_img('night') 裁 416 宽）
  mid        pano  k 0.6             邻家的屋顶（512 宽）
  near       pano  k 1               屋顶（640 宽）
  clock_broken / tank_burst / chimney_broken   pick k 1（和底图逐像素比出来的框）
  laundry_l / laundry_r / beacon / bulb / cat  strip k 1
  water      strip k 1  key tank_burst          水塔洞里涌出来的水
锚点：arrive [40,160]、nodes（8 个，见 NODES）、clock [155,105]、clock_face [155,105,7]、chimney [380,118]、tank [492,146]、
      edge [620,150]、dio_air [320,90]（素材总表 §一.3）；另导出 node_objs（每个节点落在什么东西上）、tank_hole、
      chimney_box、clock_box、roof_back 144、moon_screen（月亮的画面坐标，镜头不动它也不动）。
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _parts():
    key = 'bg_new_cairo_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'cairo_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


CP = _parts()
P, A = CP.P, CP.A
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from engine.core import gradient, hash01, hrange, mix  # noqa: E402

C = A._c4
dk, lt, hl, vl, px, rect = CP.dk, CP.lt, CP.hl, CP.vl, CP.px, CP.rect
W, H, N, FPS = CP.W, CP.H, CP.N, CP.FPS

PW = 640
GROUND = 156
WALK = (145, 176)
BACK = 144               # 屋顶后沿（东西的脚）
PARA = (136, 144)        # 后沿矮墙
EDGE_X = 626             # 屋顶右边的边（再往右是楼缝）
MOON = (200, 36, 14)     # 月亮（画面坐标，天是 k 0）
FAR_K, MID_K = 0.3, 0.6
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 416
MIDW = W + int(math.ceil((PW - W) * MID_K))      # 512
CLOCK = (155, 105, 7)
CHIM = (380, 118)
TANK = (492, 146)
TANK_BODY = (474, 96, 510, 128)                   # 水塔罐身（x0, y0, x1, y1）
TANK_HOLE = (490, 113)
NODES = [[58, 117], [118, 92], [204, 111], [262, 88], [334, 133], [380, 116], [452, 120], [560, 100]]
NODE_OBJS = ['左边晾衣杆顶', '鸽舍竹竿顶', '小水箱的盖把手', '电视天线杆顶', '弯头通风管口', '烟囱口', '右边晾衣杆顶',
             '第二间小屋的天线顶']
ANCHORS = dict(arrive=[40, 160], nodes=[list(n) for n in NODES], clock=[155, 105], clock_face=[155, 105, 7],
               chimney=[380, 118], tank=[492, 146], edge=[620, 150], dio_air=[320, 90])
STAND = ('arrive', 'tank', 'edge')

ROOF_C, ROOF_D, ROOF_HI = (178, 170, 158), (164, 156, 144), (190, 184, 172)
PARA_C = (196, 184, 160)
BRICK = (206, 118, 84)                 # 砖色调亮一点：夜里压暗以后烟囱还认得出是红砖


# ============================================================ 天
@lru_cache(maxsize=2)
def sky(red=False):
    im = A._new(W, H)
    if not red:
        gradient(im, (0, 0, W, H), CP.NIGHT_SKY, bands=10)
        A._stars(im, (0, 0, W, 130), 110, 501)
        A._stars(im, (0, 0, W, 100), 30, 502, cols=((255, 240, 200), (200, 220, 255)))
        CP.moon(im, MOON[0], MOON[1], MOON[2])
    else:
        gradient(im, (0, 0, W, H), [(40, 4, 10), (96, 10, 18), (160, 24, 24), (210, 50, 30), (236, 96, 44)], bands=10)
        A._glow(im, MOON[0], MOON[1], MOON[2] * 3, MOON[2] * 3, (255, 60, 40), 60, rings=4)
        d = ImageDraw.Draw(im)
        r = MOON[2]
        d.ellipse((MOON[0] - r, MOON[1] - r, MOON[0] + r, MOON[1] + r), fill=C((120, 16, 20)))
        d.ellipse((MOON[0] - r + 2, MOON[1] - r + 1, MOON[0] + r - 2, MOON[1] + r - 3), fill=C((150, 24, 26)))
        for i in range(50):                                          # 几道往下拖的暗云
            x = int(hrange(0, W, 503, i))
            y = int(hrange(10, 110, 504, i))
            hl(d, x, x + int(hrange(10, 40, 505, i)), y, (70, 8, 16))
    return im


# ============================================================ 中景：邻家的屋顶
@lru_cache(maxsize=1)
def mid_albedo():
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    base = 150
    x = 0
    k = 0
    while x < MIDW:
        w = int(hrange(26, 52, k, 510))
        top = int(hrange(104, 128, k, 511))
        c = mix((196, 176, 140), (222, 206, 172), hash01(k, 512))
        rect(d, x, top, min(MIDW - 1, x + w - 1), base, c)
        hl(d, x, x + w - 1, top, CP.lt(c, 0.25))
        hl(d, x, x + w - 1, top + 1, dk(c, 0.85))
        for yy in range(top + 6, base - 4, 10):
            for xx in range(x + 4, x + w - 4, 8):
                rect(d, xx, yy, xx + 2, yy + 4, (70, 110, 90) if hash01(xx, yy, 513) < 0.5 else dk(c, 0.62))
        q = hash01(k, 514)
        if q < 0.4:
            CP.water_tank(im, x + 4, top, w=10, h=7, legs=3)
        elif q < 0.7:
            CP.antenna(ImageDraw.Draw(im), x + w - 6, top, 12, seed=k)
        else:
            d2 = ImageDraw.Draw(im)
            vl(d2, x + 3, top - 9, top, (120, 96, 70))
            vl(d2, x + w - 3, top - 9, top, (120, 96, 70))
            CP.laundry(d2, x + 3, x + w - 3, top - 9, 0, 515 + k, sag=2)
        d = ImageDraw.Draw(im)
        x += w
        k += 1
    P.minaret(im, 300, 112, 30, 8, (226, 214, 186), seed=9)          # 近一点的宣礼塔
    d = ImageDraw.Draw(im)
    d.ellipse((316, 96, 344, 124), fill=C((214, 200, 170)))          # 旁边的穹顶
    vl(d, 330, 88, 96, (200, 170, 90))
    return im


def mid_img(red=False):
    im = mid_albedo()
    a = np.array(im)
    g = CP.grade(im, 'night')
    d = ImageDraw.Draw(g)
    win = (a[..., 3] > 0) & (a[..., 0] == 70) & (a[..., 1] == 110) & (a[..., 2] == 90)
    ys, xs = np.nonzero(win)
    for (y, x) in zip(ys, xs):
        if hash01(int(x) // 3, int(y) // 5, 516) < 0.45:
            px(d, int(x), int(y), (240, 196, 120))
    for yy in (56, 72):                                              # 宣礼塔阳台的绿灯
        hl(d, 296, 304, yy, (90, 230, 140))
    return CP.haze(g, 0.1, (30, 36, 70))


# ============================================================ 近景：屋顶
def roof_hut(im, reg, x0, x1, top, col, seed, door='open', window=False):
    """楼梯间小屋：抹灰方盒 + 檐 + 门（open = 开着、里面亮）+ 小窗。"""
    d = P.plaster(im, x0, x1, top, BACK, col, seed, streaks=2, cell=3, damp=3, cracks=2)
    CP.cornice(im, x0, x1, top, col, depth=2)
    d = ImageDraw.Draw(im)
    dx = x0 + 6
    if door == 'open':
        rect(d, dx, BACK - 20, dx + 8, BACK, (40, 34, 36))
        rect(d, dx + 1, BACK - 19, dx + 7, BACK, (150, 120, 90))         # 里面（夜里点亮）
        vl(d, dx + 2, BACK - 18, BACK - 2, (120, 92, 66))
        hl(d, dx + 1, dx + 7, BACK - 6, (110, 86, 60))                  # 楼梯的一级
        rect(d, dx + 9, BACK - 20, dx + 10, BACK, (96, 104, 112))       # 推开的铁门
        reg['shop'].append((dx + 1, BACK - 19, dx + 7, BACK, True))
    else:
        rect(d, dx, BACK - 20, dx + 8, BACK, (90, 98, 106))
        vl(d, dx, BACK - 20, BACK, (130, 138, 146))
        px(d, dx + 6, BACK - 10, (200, 190, 120))
    if window:
        wx = x1 - 16
        CP.window(im, reg, wx, top + 8, 8, 9, col, 'o', CP.SHUT['green'], seed + 3)


def clothes_pole(d, x, top, col=(150, 116, 76)):
    vl(d, x, top, BACK, col)
    vl(d, x + 1, top + 1, BACK, dk(col, 0.7))
    hl(d, x - 2, x + 2, top + 1, dk(col, 0.85))                       # 顶上的横档（拴绳子）
    px(d, x, top - 1, dk(col, 0.6))


def pigeon_loft(im, x0, x1, top):
    d = ImageDraw.Draw(im)
    for xx in (x0, x1):
        vl(d, xx, top + 6, BACK, (120, 90, 60))
    vl(d, x0 + 1, top + 6, BACK, (150, 116, 78))
    for y in range(top + 10, BACK - 4, 6):
        hl(d, x0, x1, y, (140, 104, 66))
        hl(d, x0, x1, y + 1, (100, 72, 46))
    rect(d, x0 + 2, top + 12, x1 - 2, BACK - 6, (110, 90, 70))
    for y in range(top + 12, BACK - 6, 2):
        for xx in range(x0 + 2 + (y // 2) % 2, x1 - 1, 2):
            px(d, xx, y, (150, 130, 100))
    d.polygon([(x0 - 2, top + 7), ((x0 + x1) // 2, top), (x1 + 2, top + 7)], fill=C((150, 100, 64)))
    hl(d, x0 - 2, x1 + 2, top + 7, (100, 68, 44))
    for i, (px_, py_) in enumerate(((x0 + 5, top + 9), (x0 + 11, top + 9), (x0 + 8, top + 15))):   # 睡着的鸽子
        CP.pigeon_px(d, px_, py_, 0, (150, 150, 162) if i % 2 else (126, 128, 144))


def tank_stand(im, x0, x1, body_top, body_bot, burst=False):
    """水塔：铁皮圆罐（竖着的圆柱侧影：左亮右暗、几道箍、一排排铆钉、顶上锥形盖 + 人孔）+ 四根角钢腿 + 交叉撑 + 爬梯。
    burst = 罐身被打穿：一个参差的洞（里面黑）、洞边铁皮往外翻、下面一道道水痕、屋顶上一摊水。"""
    d = ImageDraw.Draw(im)
    col = (150, 158, 166)
    w = x1 - x0
    for i in range(w):
        u = i / max(1, w - 1)
        c = lt(col, 0.3) if u < 0.18 else (dk(col, 0.62) if u > 0.78 else (col if u < 0.55 else dk(col, 0.84)))
        vl(d, x0 + i, body_top, body_bot, c)
    for y in (body_top + 1, body_top + 11, body_top + 22, body_bot - 1):
        hl(d, x0, x1 - 1, y, dk(col, 0.7))
        for xx in range(x0 + 2, x1 - 1, 3):
            px(d, xx, y - 1, lt(col, 0.2) if xx < x0 + w * 0.5 else dk(col, 0.75))
    d.polygon([(x0, body_top), ((x0 + x1) // 2, body_top - 7), (x1 - 1, body_top)], fill=C(dk(col, 0.9)))
    d.line((x0, body_top, (x0 + x1) // 2, body_top - 7), fill=C(lt(col, 0.3)))
    rect(d, (x0 + x1) // 2 - 2, body_top - 9, (x0 + x1) // 2 + 2, body_top - 7, dk(col, 0.7))
    for k in range(4):                                               # 锈迹往下淌
        sx = x0 + 4 + int(hash01(k, 520) * (w - 8))
        vl(d, sx, body_top + 3, body_top + 3 + int(hrange(4, 20, k, 521)), (150, 100, 70))
    legs = (x0 + 2, x0 + 12, x1 - 13, x1 - 3)
    for xx in legs:
        vl(d, xx, body_bot + 1, BACK, (60, 62, 68))
        vl(d, xx + 1, body_bot + 1, BACK, (40, 42, 46))
    for (a_, b_) in ((legs[0], legs[1]), (legs[2], legs[3])):
        d.line((a_, body_bot + 2, b_, BACK - 1), fill=C((60, 62, 68)))
        d.line((b_, body_bot + 2, a_, BACK - 1), fill=C((60, 62, 68)))
    hl(d, legs[0], legs[3], body_bot + 8, (60, 62, 68))
    for y in range(body_top + 2, BACK, 3):                            # 爬梯（右边）
        hl(d, x1, x1 + 3, y, (70, 72, 78))
    vl(d, x1, body_top + 2, BACK, (70, 72, 78))
    vl(d, x1 + 3, body_top + 2, BACK, (50, 52, 56))
    if burst:
        hx, hy = TANK_HOLE
        for i in range(-5, 6):
            hh = int(round(4.5 * math.sqrt(max(0.0, 1 - (i / 5.5) ** 2)) + hash01(i, 522) * 1.5))
            vl(d, hx + i, hy - hh, hy + hh, (14, 14, 18))
        for i in range(10):                                          # 洞边翻出来的铁皮
            a_ = i / 10 * math.tau
            px(d, int(round(hx + 6.5 * math.cos(a_))), int(round(hy + 5.5 * math.sin(a_))), lt(col, 0.4))
        for k in range(8):                                           # 往下一道道水痕
            sx = hx - 6 + int(hash01(k, 523) * 14)
            vl(d, sx, hy + 5, body_bot, (110, 130, 150))
        d.ellipse((hx - 6, BACK - 1, hx + 36, BACK + 9), fill=C((120, 140, 160)))     # 屋顶上的一摊水
        d.ellipse((hx - 2, BACK + 1, hx + 30, BACK + 7), fill=C((140, 164, 186)))
        for k in range(6):
            px(d, hx + int(hrange(0, 28, k, 524)), BACK + 2 + int(hrange(0, 5, k, 525)), (210, 226, 236))


def chimney(im, broken=False):
    """砖烟囱：一层层红砖（灰缝错开）、左亮右暗、顶上一块水泥帽（chimney.y = 帽顶）、烟囱口黑。
    broken = 上半截被打断：断口参差、砖块撒在屋顶上。"""
    d = ImageDraw.Draw(im)
    cx, top = CHIM
    x0, x1 = cx - 8, cx + 8
    cut = top + 13 if broken else top
    for y in range(cut + 2, BACK + 1):
        for x in range(x0, x1 + 1):
            c = BRICK
            if (y - top) % 3 == 0:
                c = (176, 160, 146)                                  # 灰缝（浅）
            elif (x + ((y - top) // 3) * 3) % 6 == 0:
                c = (176, 160, 146)
            if x == x0:
                c = lt(c, 0.2)
            elif x >= x1 - 1:
                c = dk(c, 0.7)
            px(d, x, y, c)
    if not broken:
        rect(d, x0 - 2, top, x1 + 2, top + 2, (170, 166, 156))       # 水泥帽
        hl(d, x0 - 2, x1 + 2, top, (200, 196, 186))
        hl(d, x0 - 2, x1 + 2, top + 2, (120, 116, 110))
        rect(d, cx - 3, top - 2, cx + 3, top - 1, (90, 86, 82))       # 烟囱口（一截短管）
        hl(d, cx - 3, cx + 3, top - 2, (120, 116, 110))
        px(d, cx, top - 2, (20, 18, 20))
        px(d, cx + 1, top - 2, (20, 18, 20))
    else:
        for x in range(x0, x1 + 1):                                  # 参差的断口
            jag = int(hrange(0, 5, x, 530))
            vl(d, x, cut + 2 - jag, cut + 2, BRICK if jag % 2 else (130, 110, 100))
            px(d, x, cut + 2 - jag, lt(BRICK, 0.25))
        rect(d, cx - 2, cut + 1, cx + 2, cut + 3, (20, 18, 20))
        for i in range(30):                                          # 撒了一地的砖块（平的）
            x = int(hrange(cx - 40, cx + 46, 531, i))
            y = int(hrange(BACK + 1, 160, 532, i))
            rect(d, x, y, x + 2, y + 1, BRICK if i % 3 else (170, 166, 156))
            hl(d, x, x + 2, y, lt(BRICK, 0.3) if i % 3 else (200, 196, 186))
        for i in range(40):
            px(d, int(hrange(cx - 30, cx + 36, 533, i)), int(hrange(BACK - 2, 156, 534, i)), (150, 120, 100))
        rect(d, x0 - 5, BACK - 3, x0 - 1, BACK, BRICK)               # 脚下一堆碎砖
        rect(d, x1 + 1, BACK - 2, x1 + 6, BACK, (150, 90, 70))


def vent_pipe(d, x, top):
    """弯头通风管：一根铁管从屋顶冒出来、顶上弯成一个钩（管口朝下）。"""
    col = (120, 124, 130)
    vl(d, x, top + 3, BACK, col)
    vl(d, x + 1, top + 3, BACK, dk(col, 0.7))
    hl(d, x, x + 3, top + 1, col)
    hl(d, x, x + 3, top, lt(col, 0.3))
    vl(d, x + 3, top + 1, top + 4, dk(col, 0.8))
    px(d, x + 4, top + 4, (40, 40, 44))
    hl(d, x - 1, x + 2, BACK, dk(col, 0.6))


def roof_surface(im):
    d = ImageDraw.Draw(im)
    rect(d, 0, BACK + 1, EDGE_X, H - 1, ROOF_C)
    P.mottle(im, (0, BACK + 1, EDGE_X, H - 1), ROOF_C, ROOF_D, ROOF_HI, 540, cell=8, lo=0.28, hi=0.72)
    d = ImageDraw.Draw(im)
    for y in range(BACK + 5, H, 6):                                  # 方砖的沥青缝（横）
        hl(d, 0, EDGE_X, y, CP.mix(ROOF_C, (110, 104, 96), 0.35))
    for band, y0 in enumerate(range(BACK + 1, H, 6)):
        for x in range((band % 2) * 6, EDGE_X, 12):
            vl(d, x, y0, min(H - 1, y0 + 3), CP.mix(ROOF_C, (110, 104, 96), 0.3))
    hl(d, 0, EDGE_X, BACK + 1, CP.mix(ROOF_C, (80, 72, 70), 0.4))    # 矮墙脚的影
    for i in range(16):                                              # 补过的沥青块
        x = int(hrange(0, EDGE_X - 20, 541, i))
        y = int(hrange(BACK + 6, H - 3, 542, i))
        for yy in range(y, y + 2):
            hl(d, x, x + int(hrange(6, 18, 543, i)), yy, CP.mix(ROOF_C, (120, 112, 104), 0.35))


def parapet(im):
    """后沿矮墙（y 136–144）：抹灰 + 一道水泥压顶；有几段换成铁栏杆。"""
    d = ImageDraw.Draw(im)
    for (a_, b_) in ((0, 236), (292, 470), (512, EDGE_X)):
        rect(d, a_, PARA[0], b_, PARA[1], PARA_C)
        P.mottle(im, (a_, PARA[0], b_, PARA[1]), PARA_C, dk(PARA_C, 0.92), lt(PARA_C, 0.1), 545 + a_, cell=3)
        d = ImageDraw.Draw(im)
        hl(d, a_, b_, PARA[0], lt(PARA_C, 0.35))
        hl(d, a_, b_, PARA[0] + 1, dk(PARA_C, 0.86))
    for (a_, b_) in ((236, 292), (470, 512)):                        # 铁栏杆段
        hl(d, a_, b_, PARA[0] + 1, CP.IRON)
        hl(d, a_, b_, PARA[0] + 5, CP.IRON)
        for x in range(a_, b_ + 1, 3):
            vl(d, x, PARA[0] + 1, PARA[1], CP.IRON)


def drop_gap(im):
    """右边楼缝（x 627–639）：往下看——对面楼的墙和亮窗、最下面街上的暖光。"""
    d = ImageDraw.Draw(im)
    for y in range(0, H):
        u = y / (H - 1.0)
        hl(d, EDGE_X + 1, PW - 1, y, CP.mix((30, 30, 44), (70, 56, 50), u ** 2))
    for (x, y) in ((630, 60), (634, 92), (630, 120), (635, 150)):
        rect(d, x, y, x + 2, y + 4, (230, 190, 120))
    for y in range(H - 10, H):
        hl(d, EDGE_X + 1, PW - 1, y, CP.mix((120, 90, 60), (200, 150, 90), (y - (H - 10)) / 10.0))
    vl(d, EDGE_X, BACK - 8, H - 1, (210, 200, 182))                   # 屋顶边的压顶石
    vl(d, EDGE_X + 1, BACK - 8, H - 1, (140, 130, 120))
    for y in range(BACK - 8, BACK, 2):                                # 边上的铁栏杆
        px(d, EDGE_X - 2, y, CP.IRON)
    vl(d, EDGE_X - 2, BACK - 9, BACK, CP.IRON)


@lru_cache(maxsize=8)
def roof_albedo(dmg=()):
    reg = dict(win=[], lamp=[], shop=[], ground_shadow=[])
    im = A._new(PW, H)
    roof_surface(im)
    parapet(im)
    d = ImageDraw.Draw(im)
    # 楼梯间小屋（左）+ 门顶的灯泡
    roof_hut(im, reg, 2, 32, 112, CP.WALL['sand'], 551, door='open')
    d = ImageDraw.Draw(im)
    CP.bulb(d, reg, 13, 118)
    # 晾衣绳（左）：两根杆；衣服在 strip
    clothes_pole(d, 58, NODES[0][1])
    clothes_pole(d, 96, 121)
    rect(d, 70, BACK - 6, 76, BACK, (60, 110, 160))                  # 塑料椅
    hl(d, 70, 76, BACK - 6, (90, 140, 190))
    vl(d, 76, BACK - 12, BACK - 6, (60, 110, 160))
    for (fx, c) in ((82, (196, 92, 70)), (88, (170, 110, 70))):      # 花盆
        rect(d, fx, BACK - 4, fx + 3, BACK, c)
        px(d, fx + 1, BACK - 5, (60, 120, 60))
        px(d, fx + 2, BACK - 6, (80, 150, 70))
        px(d, fx + 1, BACK - 7, (230, 90, 120))
    # 鸽舍 + 竹竿（节点 2）
    pigeon_loft(im, 104, 128, 106)
    d = ImageDraw.Draw(im)
    vl(d, 118, NODES[1][1], 106, (176, 150, 96))
    rect(d, 119, NODES[1][1] + 1, 123, NODES[1][1] + 3, (200, 60, 60))
    px(d, 118, NODES[1][1] - 1, (120, 100, 70))
    # 钟楼
    CP.clock_tower(im, CLOCK[0], BACK, 0, CLOCK[1], CLOCK[2], state='broken' if 'clock' in dmg else 'ok',
                   tod='night', hands='hour')
    # 小水箱（节点 3：盖把手）+ 木箱 + 破沙发
    CP.water_tank(im, 196, BACK, w=16, h=10, legs=22)
    d = ImageDraw.Draw(im)
    rect(d, 202, NODES[2][1] + 1, 205, NODES[2][1] + 1, CP.IRON)
    px(d, 204, NODES[2][1], CP.IRON_HI)
    for (cx, w_, h_) in ((176, 10, 8), (186, 8, 6), (180, 7, 5)):
        y = BACK - h_ + (0 if cx != 180 else -8)
        rect(d, cx, y, cx + w_, y + h_, (170, 130, 80))
        hl(d, cx, cx + w_, y, (206, 170, 120))
        vl(d, cx + w_, y, y + h_, (120, 90, 56))
    rect(d, 218, BACK - 7, 234, BACK, (120, 60, 50))                  # 破沙发
    rect(d, 218, BACK - 11, 221, BACK - 7, (120, 60, 50))
    hl(d, 218, 234, BACK - 7, (160, 90, 70))
    px(d, 226, BACK - 5, (220, 200, 160))
    # 天线杆（节点 4）+ 拉线 + 天窗盒
    ax, ay = NODES[3]
    vl(d, ax, ay, BACK, (110, 110, 118))
    for (yy, L) in ((ay + 4, 5), (ay + 8, 4), (ay + 12, 3), (ay + 16, 2)):
        hl(d, ax - L, ax + L, yy, (110, 110, 118))
    for gx in (244, 286):
        P.wire(d, ax, ay + 14, gx, PARA[0], 2, col=(90, 90, 96))
    rect(d, 268, BACK - 7, 284, BACK, (150, 156, 160))
    rect(d, 270, BACK - 6, 282, BACK - 3, (90, 110, 130))
    hl(d, 270, 282, BACK - 6, (160, 180, 196))
    # 弯头通风管（节点 5）
    vent_pipe(d, NODES[4][0], NODES[4][1])
    # 烟囱
    chimney(im, broken='chimney' in dmg)
    d = ImageDraw.Draw(im)
    # 晾衣绳（右）
    clothes_pole(d, 414, 122)
    clothes_pole(d, 452, NODES[6][1])
    # 水塔
    tank_stand(im, TANK_BODY[0], TANK_BODY[2], TANK_BODY[1], TANK_BODY[3], burst='tank' in dmg)
    d = ImageDraw.Draw(im)
    # 第二间小屋 + 天线（节点 8）+ 小水箱（猫蹲在上面，猫在 strip）
    roof_hut(im, reg, 524, 574, 108, CP.WALL['cream'], 552, door='closed', window=True)
    d = ImageDraw.Draw(im)
    CP.antenna(d, NODES[7][0], 108, 108 - NODES[7][1] - 1, seed=553)
    CP.water_tank(im, 532, 108, w=12, h=8, legs=2)
    d = ImageDraw.Draw(im)
    for (fx, c) in ((580, (196, 92, 70)), (586, (160, 100, 70)), (592, (196, 92, 70))):
        rect(d, fx, BACK - 4, fx + 3, BACK, c)
        px(d, fx + 1, BACK - 5, (60, 120, 60))
        px(d, fx + 2, BACK - 7, (80, 150, 70))
        px(d, fx, BACK - 6, (60, 120, 60))
    for k in range(4):                                               # 一摞砖
        rect(d, 600, BACK - 2 - k * 2, 610, BACK - 1 - k * 2, BRICK)
        hl(d, 600, 610, BACK - 2 - k * 2, lt(BRICK, 0.2))
    drop_gap(im)
    im = P.outer_rim(im, CP.INK, y1=BACK + 1)
    return im, reg


def near_img(dmg=()):
    im, reg = roof_albedo(tuple(sorted(dmg)))
    g = CP.grade(im.copy(), 'night')
    out = CP.light_night(g, im, reg, 'night', 0.7)
    # 月光（月亮在左上）：东西朝天 / 朝左的那一圈边（紧挨着墨线的像素）亮一档冷色，暗下来的砖烟囱、水塔、钟楼才有轮廓
    al_ = np.array(im)
    ink = np.all(al_[..., :3] == np.array(CP.INK, np.uint8), axis=-1) & (al_[..., 3] > 0)
    op = (al_[..., 3] > 0) & ~ink
    edge = np.zeros_like(op)
    edge[1:] |= ink[:-1]
    edge[:, 1:] |= ink[:, :-1]
    edge &= op
    edge[BACK - 6:] = False
    o = np.array(out).astype(np.float32)
    o[edge, :3] += np.array((34, 40, 62), np.float32)
    out = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8), 'RGBA')
    # 钟面是亮着的（夜里的钟楼钟面有灯）：花京院最后一发要瞄它，表盘要从夜色里跳出来；时针 / 碎掉的黑洞还是暗的
    a = np.array(out).astype(np.float32)
    al = np.array(im).astype(np.float32)
    cx, cy, r = CLOCK
    yy, xx = np.mgrid[0:H, 0:PW]
    m = ((xx - cx) ** 2 + (yy - cy) ** 2) <= r * r
    a[m, :3] = al[m, :3] * np.array((1.0, 0.94, 0.8), np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


# ============================================================ 动的小东西
def _graded(raw):
    def f(i):
        return CP.grade(raw(i), 'night')
    return f


def raw_laundry_l(f):
    im = A._new(PW, H)
    CP.laundry(ImageDraw.Draw(im), 58, 96, NODES[0][1] + 2, f, 561, sag=3)
    return im


def raw_laundry_r(f):
    im = A._new(PW, H)
    CP.laundry(ImageDraw.Draw(im), 414, 452, 123, f, 562, sag=3)
    return im


def raw_beacon(f):
    """天线杆顶的红灯：一闪一闪（亮两帧、暗、再亮）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    ax, ay = NODES[3]
    lv = (1.0, 0.7, 0.25, 0.1, 0.25, 0.7, 1.0, 0.85)[f]
    c = mix((80, 20, 24), (255, 70, 60), lv)
    px(d, ax, ay - 1, c)
    if lv > 0.6:
        for (dx, dy) in ((-1, -1), (1, -1), (0, -2)):
            px(d, ax + dx, ay - 1 + dy, mix((60, 20, 30), (200, 50, 50), lv - 0.4))
    else:
        px(d, ax, ay - 2, (50, 30, 40) if f % 2 else (60, 34, 44))
    return im


def raw_moths(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    lx, ly = 13, 118
    for i in range(3):
        a_ = math.tau * (f / N) * (1 if i % 2 else -1) + i * 2.1
        px(d, int(round(lx + (5 + i * 2) * math.cos(a_))), int(round(ly + 2 + (3 + i) * math.sin(a_ + i))),
           (255, 240, 200) if i % 2 else (230, 220, 190))
    return im


def raw_cat(f):
    """蹲在第二间小屋水箱上的猫（剪影），尾巴慢慢甩。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y = 538, 89
    col = (34, 30, 40)
    rect(d, x, y - 4, x + 4, y, col)
    rect(d, x + 3, y - 7, x + 5, y - 4, col)
    px(d, x + 3, y - 8, col)
    px(d, x + 5, y - 8, col)
    px(d, x + 4, y - 6, (200, 220, 120))
    ph = math.sin(math.tau * f / N)
    tx = x - 1
    for k in range(5):
        px(d, tx - (k if ph > -0.3 else max(0, k - 1)), y - int(round(k * (0.6 + 0.6 * ph))), col)
    return im


def raw_water(f):
    """水塔洞里涌出来的水：一道往右下弯的水柱浇到屋顶、溅起来的水花（hard_alpha）。"""
    im = A._new(PW, H)
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    hx, hy = TANK_HOLE
    for k in range(40):
        u = k / 39.0
        x = hx + 3 + u * 16 + math.sin(f * 0.8 + u * 6) * 0.8
        y = hy + u * u * (BACK - hy)
        c = mix((200, 226, 244), (120, 160, 200), u)
        r = 1.6 + u * 1.4
        d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(c) + (230,))
    for i in range(6):                                               # 水花
        u = ((f / N) + i / 6.0) % 1.0
        x = hx + 19 + (i - 2.5) * 3 * u * 2
        y = BACK - 2 - 6 * math.sin(math.pi * u)
        d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(220, 236, 250, 220))
    lay = P.hard_alpha(lay, bay_off=f)
    im.alpha_composite(lay)
    return im


# ============================================================ 图层表 / 导出
@lru_cache(maxsize=1)
def spec():
    L = [dict(type='pick', name='sky', key='red_sky', values=[0, 1], imgs=[sky(False), sky(True)], x=0, y=0, k=0.0),
         dict(type='wrap', name='clouds', img=CP.clouds_img('night'), period=640, k=0.05, y=16, vx=0.6)]
    far = CP.far_img('night').crop((0, 0, FARW, H))
    fim, fy = CP.crop_rows(far)
    L.append(dict(type='pano', name='far', img=fim, k=FAR_K, x=0, y=fy))
    mim, my = CP.crop_rows(mid_img())
    L.append(dict(type='pano', name='mid', img=mim, k=MID_K, x=0, y=my))
    near = near_img()
    nim, ny = CP.crop_rows(near)
    L.append(dict(type='pano', name='near', img=nim, k=1.0, x=0, y=ny))
    for (name, key, dmg) in (('clockbroken', 'clock_broken', ('clock',)), ('tankburst', 'tank_burst', ('tank',)),
                             ('chimneybroken', 'chimney_broken', ('chimney',))):
        pk, box = CP.diff_pick(name, key, near, near_img(dmg))
        L.append(pk)
    for (name, raw) in (('laundry_l', raw_laundry_l), ('laundry_r', raw_laundry_r)):
        L.append(CP.strip(name, CP.cached(_graded(raw)), k=1.0))
    L.append(CP.strip('beacon', CP.cached(raw_beacon), k=1.0))
    L.append(CP.strip('moths', CP.cached(raw_moths), k=1.0))
    L.append(CP.strip('cat', CP.cached(raw_cat), k=1.0))
    L.append(CP.strip('water', CP.cached(raw_water), k=1.0, key='tank_burst'))
    return tuple(L)


def compose(camX, t=0.5, state=None):
    return CP.compose(spec(), camX, t, state)


def anchors():
    anc = {k: (list(v) if not isinstance(v[0], list) else [list(q) for q in v]) for k, v in ANCHORS.items()}
    anc.update(node_objs=list(NODE_OBJS),
               tank_hole=list(TANK_HOLE), tank_body=list(TANK_BODY),
               chimney_box=[CHIM[0] - 10, CHIM[1] - 3, CHIM[0] + 11, BACK + 1],
               clock_box=[CLOCK[0] - 12, 70, CLOCK[0] + 13, BACK + 1],
               roof_back=BACK, roof_edge_x=EDGE_X, moon_screen=[MOON[0], MOON[1]])
    return anc


def export(ex, BJ):
    sp = spec()
    layers = CP.export_layers(ex, BJ, sp)
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors())
    if ex.check_on:
        _checks(ex, BJ, st, sp)
    return st


def _checks(ex, BJ, st, sp):
    near = near_img()
    flat = near
    cfg = dict(title='开罗屋顶', PW=PW, walk=WALK, near=near, opaque_rows=(BACK + 1, H),
               skies=[('夜空', sky(False)), ('血红的天', sky(True))],
               states=[{}, {'red_sky': 1, 'clock_broken': 1, 'tank_burst': 1, 'chimney_broken': 1}],
               stand=STAND, required=tuple(ANCHORS), values={k: v for k, v in ANCHORS.items() if k != 'nodes'},
               size_limit=250 * 1024, cams_step=40, flat=(0, EDGE_X - 4, WALK[0] + 1, WALK[1] + 1, 24, 0.015),
               flatnear=flat)
    CP.std_checks(ex, BJ, st, sp, cfg)
    a = np.array(near)
    # 8 个节点：每个都落在不透明的东西上（节点那一点或它下面 2 px 内有实的像素），x 都在 20–620（花京院走得到）
    bad = []
    for i, (x, y) in enumerate(NODES):
        hit = any(a[yy, x, 3] > 0 for yy in range(y, min(H, y + 3)))
        if not hit or not (20 <= x <= 620):
            bad.append(i)
    ex.checked('8 个触须节点都落在看得见的东西上（%s），x 在 20–620（不满足：%s）' % ('、'.join(NODE_OBJS), bad or '无'),
               len(bad))
    xs = sorted(x for (x, y) in NODES)
    gaps = [b - a_ for a_, b in zip(xs, xs[1:])]
    ex.checked('节点之间横向至少隔 40 px（布网时一个一个走过去，最小间隔 %d）' % min(gaps), 0 if min(gaps) >= 40 else 1)
    # 钟面：中心 (155,105) 半径 7 的圆里是表盘（亮），圆外一圈是框（暗）
    cx, cy, r = CLOCK
    yy, xx = np.mgrid[0:H, 0:PW]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    lu = CP.lum(a[..., :3].astype(np.float32))
    face = lu[(dist <= r - 2)]
    ring = lu[(dist > r) & (dist <= r + 1.2)]
    ex.checked('clock_face (155,105,7)：表盘亮（中位 %.0f）、外框暗（中位 %.0f）' % (np.median(face), np.median(ring)),
               0 if np.median(face) > np.median(ring) + 80 else 1)
    # 分针由剧情画：表盘上只有时针（中心往上那一条竖线上没有指针色）
    up = [tuple(a[cy - k, cx, :3]) for k in range(2, r - 1)]
    ex.checked('钟面只有时针（12 点方向那条线上没有分针）', sum(1 for c in up if sum(int(v) for v in c) < 200))
    # DIO 悬在 dio_air：精灵（42×42，pivot 17,40）占的框里近景是透明的（背后只有天和远景，不压钟楼 / 烟囱）
    dx, dy = ANCHORS['dio_air']
    box = a[dy - 40:dy + 2, dx - 17:dx + 25, 3]
    ex.checked('dio_air (%d,%d) DIO 的身子那一块（%d×%d）近景是空的（不压钟楼 / 烟囱 / 天线）' % (dx, dy, 42, 42),
               int((box > 0).sum()))
    # 水塔脚 / 屋顶边
    tx, ty = ANCHORS['tank']
    ex.checked('tank (%d,%d) 在水塔脚下（罐身 x %d–%d）' % (tx, ty, TANK_BODY[0], TANK_BODY[2]),
               0 if TANK_BODY[0] <= tx <= TANK_BODY[2] and abs(ty - BACK) <= 2 else 1)
    ex.checked('edge (620,150) 在屋顶右边的边以内 6 px', 0 if 0 <= EDGE_X - 620 <= 6 else 1)
    chx, chy = ANCHORS['chimney']
    ex.checked('chimney (%d,%d) 是烟囱帽的顶（这一点实、上面隔一行墨线是空的）' % (chx, chy),
               0 if a[chy, chx - 6, 3] == 255 and a[chy - 2, chx - 6, 3] == 0 else 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'final', 'after')
    os.makedirs(od, exist_ok=True)
    full = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    for cx in (0, 320):
        full.paste(compose(cx, 0.5), (cx, 0))
    full.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'cairo_rooftops_solo.png'))
    print('ok')
