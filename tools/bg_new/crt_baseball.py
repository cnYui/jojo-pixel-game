# -*- coding: utf-8 -*-
r"""crt_baseball —— 第11章「DIO 的馆」：泰伦斯的电视里的 8 位棒球游戏画面（全屏 320×180 静态，给剧情 T.show({ bg }) 用）。
2026-10-19 第三轮背景重画（interiors 组）新画。共用零件在 interior_parts.py。归包：bg_ch11（主代理登记）。

⚠ 剧情会在最上层盖 prop.crt_bezel（320×180 的电视外框；屏幕区只有 [40,18]–[252,162]，暗角和扫描线已经在框里）：
  所有内容和四个锚点都在屏幕区里；屏幕区外画纯深色（电视机外面的暗房间，外框盖不到的边上也不突兀）。
从本垒后面看过去的 8 位棒球场（少色、平涂、硬边）：
  y 18–44  看台：深色底 + 一排排彩色的观众点（两种亮度错开）+ 顶上几面小旗；右上一块深色的比分牌（anchors.score = 牌子中心，
           约 120×10，剧情在上面写一行字；牌子上不画字）
  外野围栏：一道弧（中外野最高 y 44，两边的界外杆 y ~80），绿墙 + 黄色顶边；两根黄色界外杆
  外野草地：横的割草条纹（深浅两种绿）
  内野：透视的菱形——本垒 (146,148)、一垒 (214,108)、二垒 (146,68)、三垒 (78,108)；土色的跑垒道 + 中间一块内野草地；
        投手丘（anchors.mound [146,102]）：土色的椭圆 + 白色投手板；本垒（anchors.plate [146,148]）：土色圆 + 白色五角形本垒板 +
        两边的打击区白框；两条白色的边线从本垒经一 / 三垒一直到围栏
  球的轨迹：读中时从本垒飞向 anchors.outfield [100,56]（左中外野、围栏前面）——这条线上只有草地 / 土，不压投手（投手在 x 138–154）
剧情画在上面的（背景不画）：投手 / 打者 / 球（prop.bb_sprites 16×22，pivot 底中，站在 mound / plate）、比分牌上的字、
  委托藤蔓后左下的紫色藤蔓、YES / NO 气泡、最上层的电视外框。
图层：near  static（整张，不透明）；全静态。
锚点：mound [146,102]、plate [146,148]、outfield [100,56]、score [188,26]；另外多导出：screen [40,18,252,162]（屏幕区）、
  score_box [128,21,248,31]、bases（一 / 二 / 三垒）、walk_x [40,252]。
单独运行：python -B tools/bg_new/crt_baseball.py → tools/bg_new/_preview/ch11/after/crt_baseball_solo.png
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

W, H = 320, 180
PW = 320
GROUND = 156
WALK = (150, 176)
SCREEN = (40, 18, 252, 162)
MOUND, PLATE, OUTFIELD, SCORE = (146, 102), (146, 148), (100, 56), (188, 26)
SCORE_BOX = (128, 21, 248, 31)
B1, B2, B3 = (214, 108), (146, 68), (78, 108)
FENCE_C, FENCE_R = (146, 110), (120, 66)       # 围栏的弧：椭圆上半圈

OUT = (16, 14, 20)                              # 屏幕区外（电视机外面的暗房间）
SKYC = (24, 30, 64)
STAND = (40, 44, 70)
GRASS = [(48, 140, 56), (64, 168, 68)]          # 割草条纹的深 / 浅
INGRASS = (72, 176, 76)
DIRT = (188, 124, 64)
DIRT_D = (160, 100, 52)
WHITE = (246, 246, 240)
FENCEC = (32, 96, 60)
YEL = (246, 210, 60)

ANCHORS = dict(mound=list(MOUND), plate=list(PLATE), outfield=list(OUTFIELD), score=list(SCORE),
               screen=list(SCREEN), score_box=list(SCORE_BOX), bases=[list(B1), list(B2), list(B3)], walk_x=[40, 252])


def fence_y(x):
    cx, cy = FENCE_C
    rx, ry = FENCE_R
    u = (x - cx) / rx
    return cy - ry * math.sqrt(max(0.0, 1 - u * u))


@lru_cache(maxsize=1)
def field_img():
    im = P.new(PW, H, OUT)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = SCREEN
    rect(d, x0, y0, x1, y1, SKYC)
    # 看台：围栏上面一整片，观众是两种亮度错开的彩点（8 位游戏常见的“人海”花纹）
    crowd = [(220, 70, 70), (240, 200, 80), (90, 150, 230), (240, 240, 240), (120, 200, 120), (230, 130, 190)]
    for y in range(y0 + 2, 60):
        for x in range(x0, x1 + 1):
            if y >= fence_y(x) - 4:
                continue
            c = STAND
            if (x + (y // 3) % 2) % 2 == 0 and y % 3 != 2:
                c = crowd[int(hash01(x // 2, y // 3, 4) * len(crowd))]
                if (y // 3) % 2:
                    c = dk(c, 0.75)
            px(d, x, y, c)
    for fx in (60, 92, 200, 232):                                                    # 看台顶上的小旗
        vl(d, fx, y0, y0 + 5, (200, 200, 200))
        rect(d, fx + 1, y0, fx + 4, y0 + 2, (230, 60, 60) if fx < 146 else (60, 120, 230))
    # 外野草地（割草条纹）
    for y in range(40, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < fence_y(x):
                continue
            px(d, x, y, GRASS[(y // 6) % 2])
    # 围栏：绿墙 4 px + 黄色顶边；两根界外杆
    for x in range(x0, x1 + 1):
        fy = int(round(fence_y(x)))
        if fy <= y1:
            vl(d, x, fy - 4, fy - 1, FENCEC)
            px(d, x, fy - 5, YEL)
            px(d, x, fy, dk(GRASS[0], 0.8))
    for x in (44, 248):
        fy = int(round(fence_y(x)))
        vl(d, x, fy - 18, fy, YEL)
    # 内野：土色的大菱形（跑垒道 + 内野土）→ 里面一块内野草地 → 投手丘 → 本垒的土圈
    d.polygon([(B2[0], B2[1] - 10), (B1[0] + 14, B1[1]), (PLATE[0], PLATE[1] + 10), (B3[0] - 14, B3[1])], fill=P.C(DIRT))
    d.polygon([(B2[0], B2[1] + 8), (B1[0] - 18, B1[1]), (PLATE[0], PLATE[1] - 12), (B3[0] + 18, B3[1])], fill=P.C(INGRASS))
    for y in range(B2[1] + 8, PLATE[1] - 11):                                           # 内野草地也有条纹
        for x in range(B3[0] + 18, B1[0] - 17):
            if im.getpixel((x, y))[:3] == INGRASS and (y // 5) % 2:
                px(d, x, y, GRASS[1])
    mx, my = MOUND
    d.ellipse((mx - 11, my - 5, mx + 11, my + 4), fill=P.C(DIRT), outline=P.C(DIRT_D))
    rect(d, mx - 3, my - 1, mx + 3, my, WHITE)                                         # 投手板
    px_, py_ = PLATE
    d.ellipse((px_ - 18, py_ - 8, px_ + 18, py_ + 8), fill=P.C(DIRT), outline=P.C(DIRT_D))
    # 边线：本垒 → 一垒 / 三垒 → 围栏
    for (bx, by) in (B1, B3):
        dx, dy = bx - px_, by - py_
        for k in range(0, 400):
            u = k / 100.0
            x = int(round(px_ + dx * u))
            y = int(round(py_ + dy * u))
            if not (x0 <= x <= x1) or y < fence_y(x):
                break
            px(d, x, y, WHITE)
    for (bx, by) in (B1, B2, B3):                                                        # 垒包
        rect(d, bx - 2, by - 1, bx + 2, by + 1, WHITE)
        hl(d, bx - 2, bx + 2, by + 2, DIRT_D)
    d.polygon([(px_ - 3, py_ - 1), (px_ + 3, py_ - 1), (px_ + 3, py_), (px_, py_ + 2), (px_ - 3, py_)], fill=P.C(WHITE))
    for sx in (-1, 1):                                                                   # 打击区
        bx0 = px_ + sx * 6 if sx > 0 else px_ - 13
        rect(d, bx0, py_ - 6, bx0 + 7, py_ + 5, None, outline=WHITE)
    # 比分牌：深色横牌 + 亮边（剧情在上面写字）
    sx0, sy0, sx1, sy1 = SCORE_BOX
    rect(d, sx0 - 1, sy0 - 1, sx1 + 1, sy1 + 1, (190, 190, 200))
    rect(d, sx0, sy0, sx1, sy1, (14, 16, 30))
    hl(d, sx0, sx1, sy1 + 2, (10, 10, 16))
    return P.opaque(im)


def specs():
    return [dict(t='static', name='near', img=field_img())]


def export(ex, BJ):
    S = specs()
    layers, fg = P.export_layers(ex, BJ, S)
    st = ex.stage(PW, GROUND, WALK, layers, fg, {k: (list(v) if isinstance(v, (list, tuple)) else v)
                                                 for k, v in ANCHORS.items()})
    if ex.check_on:
        _checks(ex, BJ, st, S)
    return st


def _checks(ex, BJ, st, S):
    im = field_img()
    cfg = dict(name='棒球插画', pw=PW, walk=WALK, states=[{}],
               opaque=[('整张不透明', im, (0, 0, PW, H))], binary=[('只有 0 / 255 两种透明度', im)],
               stand=[], inside=['mound', 'plate', 'outfield', 'score', 'screen', 'score_box', 'bases'])
    P.std_checks(ex, BJ, st, S, cfg)
    x0, y0, x1, y1 = SCREEN
    bad = 0
    for (x, y) in (MOUND, PLATE, OUTFIELD, SCORE):
        bad += int(not (x0 <= x <= x1 and y0 <= y <= y1))
    for (x, y) in (MOUND, PLATE):                                                     # 16×22 的小人站上去也在屏幕区里
        bad += int(not (x0 <= x - 8 and x + 8 <= x1 and y0 <= y - 22 and y <= y1))
    sx0, sy0, sx1, sy1 = SCORE_BOX
    bad += int(not (x0 <= sx0 and sx1 <= x1 and y0 <= sy0 and sy1 <= y1))
    ex.checked('四个锚点 / 两个小人 / 比分牌都在电视的屏幕区 %s 里（不满足的条数）' % (SCREEN,), bad)
    a = np.array(im)[..., :3]
    out = np.ones((H, PW), bool)
    out[y0:y1 + 1, x0:x1 + 1] = False
    ex.checked('屏幕区外是一色的深色（不是 %s 的像素）' % (OUT,), int((np.abs(a[out].astype(int) - np.array(OUT)).max(-1) > 0).sum()))
    ok = {GRASS[0], GRASS[1], INGRASS, DIRT, DIRT_D, WHITE, dk(GRASS[0], 0.8)}
    blocked = 0
    for k in range(101):
        u = k / 100.0
        x = int(round(PLATE[0] + (OUTFIELD[0] - PLATE[0]) * u))
        y = int(round(PLATE[1] - 8 + (OUTFIELD[1] - PLATE[1] + 8) * u))
        blocked += int(tuple(int(v) for v in a[y, x]) not in ok)
        blocked += int(abs(x - MOUND[0]) <= 8 and MOUND[1] - 22 <= y <= MOUND[1])
    ex.checked('本垒 → outfield 的球路上只有草地 / 土 / 白线、不穿过投手（挡住的点）', blocked)
    ex.checked('比分牌 120×10 左右（%d×%d）、score 是牌子中心' % (sx1 - sx0 + 1, sy1 - sy0 + 1),
               int(abs(sx1 - sx0 + 1 - 121) > 6 or abs(sy1 - sy0 + 1 - 11) > 2)
               + int(SCORE != ((sx0 + sx1) // 2, (sy0 + sy1) // 2)))


if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch11', 'after')
    os.makedirs(od, exist_ok=True)
    field_img().convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'crt_baseball_solo.png'))
    print('ok')
