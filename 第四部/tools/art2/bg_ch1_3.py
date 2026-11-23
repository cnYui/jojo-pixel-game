# 第1–3章背景（重画）。比例普查的结论：户外的虹村家前院、商店街、铁道口、酒店门口、海角本来就接近正确，保留；
#   室内全部偏大（门有 75 px，人只有 30 px），重画：虹村家走廊、虹村家楼梯间、康一家客厅、学校走廊、教室、海边别墅屋里、餐厅、厨房；
#   海边别墅门外的房子偏小（门只有 22 px），也重画。虹村家的阁楼比例尚可，保留。
#   用法：python 第四部/tools/art2/bg_ch1_3.py 检查图输出目录 [背景 key …]
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from px import Cv, mix, shade, rgba  # noqa: E402
import bgkit as K  # noqa: E402
import bgout as O  # noqa: E402
import bgin2 as I  # noqa: E402
from bgkit import FLOOR  # noqa: E402
from bgout import GROUND  # noqa: E402
from pfont import ptext  # noqa: E402
from bg_pro import night_tint, check_image, ground_street, lot, school_block  # noqa: E402

F = FLOOR


def empty(w, h=180):
    return Cv(w, h)


# ================================================================ 虹村家走廊 nijimura_hall（640）：荒废的老洋房，层高 3 m
NJ = dict(wall='#3e5a50', wall2='#36504a', wains='#4a3428', floor='#6a4a34', frame='#3a281e', ext='#cfc6a0', roof='#3a2e3a')


def nj_top(cv, W, C, sky=('#8a8ea0', '#a4a8b4', '#c0c2c8', '#d8d8d8')):
    """虹村家上半截：阴天、二楼外墙（发黄的木板墙、几扇窗钉着板）、破屋顶"""
    K.sky(cv, 0, W - 1, C - 4, sky)
    K.roof_hip(cv, -10, W + 10, C - 46, C - 74, NJ['roof'], inset=44)
    K.siding(cv, 0, C - 45, W - 1, C - 5, NJ['ext'])
    r = K.rng(5)
    for wx in range(46, W - 20, 96):
        if r.rand() < 0.4:
            I.boarded_window(cv, wx - 9, C - 36, wx + 9, C - 14, frame='#6a5a44', light='#2a3038', seed=wx)
        else:
            K.window_ext(cv, wx - 9, C - 36, wx + 9, C - 14, frame='#b8b094', glass='#3a4450', nx=2)
    for _ in range(26):                                   # 墙板上的裂缝和青苔
        x, y = int(r.randint(4, W - 4)), int(r.randint(C - 44, C - 8))
        cv.vline(x, y, y + int(r.randint(2, 6)), shade(NJ['ext'], -0.3))
    K.darken(cv, 0, 0, W - 1, C - 5, 0.8)
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#3a2a20')


def nj_wall(cv, x0, x1, C, seed=0):
    K.wall(cv, x0, x1, NJ['wall'], y0=C, y1=F, stripes=(10, NJ['wall2']), wains=(14, NJ['wains']), base='#2e2018', crown='#2e2018')
    r = K.rng(seed)
    for _ in range(max(2, (x1 - x0) // 70)):              # 发霉、墙纸剥落
        I.stain(cv, r.randint(x0 + 10, x1 - 10), r.randint(C + 8, F - 20), r.randint(8, 16), r.randint(6, 12), shade(NJ['wall'], -0.35), seed=int(r.randint(999)))
    for _ in range(max(1, (x1 - x0) // 160)):
        cx, cy = int(r.randint(x0 + 14, x1 - 14)), int(r.randint(C + 8, F - 24))
        I.stain(cv, cx, cy, 10, 7, '#a89878', seed=int(r.randint(999)), k=0.9)
        for yy in range(cy - 2, cy + 3, 2):
            cv.hline(cx - 3, cx + 3, yy, '#7a6a50')
    for x in range(x0 + 20, x1, 37):                      # 天花往下淌的水渍
        cv.vline(x, C + 2, C + 2 + int(r.randint(3, 12)), shade(NJ['wall'], -0.28))


def nijimura_hall():
    W = 640
    cv = Cv(W, 180)
    C = F - 50
    nj_top(cv, W, C)
    nj_wall(cv, 0, W - 1, C, seed=3)
    K.floor_wood(cv, 0, W - 1, c=NJ['floor'], seed=7)
    # 开着的正门（外面是亮的院子）
    cv.rect(21, F - 37, 43, F, NJ['frame'])
    cv.rect(23, F - 35, 41, F, '#f4eccc')
    cv.rect(23, F - 12, 41, F, '#a8c088')
    cv.rect(23, F - 35, 41, F - 30, '#d8e8f0')
    cv.rect(38, F - 35, 41, F, '#5a3a28')                  # 推开的门扇侧边
    I.coat_rack(cv, 84, F)
    x0, y0, x1, y1 = K.picture(cv, 138, F - 28, 14, 10, '#8a6a3a', ('#4a5a6a', '#3a4a3a', '#c8c0a0'))
    cv.line(x0, y0 - 2, x1, y0 - 4, '#2a2018')           # 歪着的挂绳
    g1 = I.boarded_window(cv, 200, F - 38, 220, F - 15, seed=1)
    I.doorway(cv, 284, F, 18, 34, NJ['frame'])
    K.table(cv, 363, F, w=20, h=11, c='#5a3a28')
    I.oval_mirror(cv, 362, F - 26, 4, 6)
    for dx, dy in ((-6, 0), (-3, 1), (-8, 2), (-4, 3)):   # 地上的碎花瓶
        cv.put(358 + dx, F + 3 + dy, '#c8d0d8')
    I.grandfather_clock(cv, 426, F)
    g2 = I.boarded_window(cv, 480, F - 38, 500, F - 15, seed=2)
    cv.line(545, F, 552, F - 12, '#8a6a3a')               # 倒在墙根的画框
    cv.line(552, F - 12, 561, F - 10, '#8a6a3a')
    cv.line(561, F - 10, 556, F, '#8a6a3a')
    cv.hline(545, 556, F, '#8a6a3a')
    I.arch(cv, 614, F, 24, 38, NJ['frame'])
    for i in range(4):                                     # 拱门里隐约的楼梯
        cv.hline(606 + i * 3, 625, F - 2 - i * 4, '#3a2a22')
    old = I.bullet_holes(W, [(60, C + 6, 600, F - 4, 14, False), (60, F + 6, 600, 176, 8, True)], seed=11)
    cv.a = np.array(_over(cv.img(), old))
    night_tint(cv, 0.82, tint=(0.96, 0.98, 1.02), keep=('#f4eccc', '#fff0c0', '#d8e8f0', '#a8c088'))
    polys = [[(23, F - 35), (41, F - 35), (86, 176), (30, 176)]]
    for gaps in (g1, g2):
        for (xa, y, xb) in gaps:
            polys.append([(xa, y), (xb, y), (xb - 26, 174), (xa - 40, 174)])
    glow = I.shafts(W, polys, spots=[(56, 160, 40, 12, 0.3)], k=0.22)
    holes = I.bullet_holes(W, [(40, C + 6, 620, F - 4, 110, False), (40, F + 6, 620, 177, 50, True)], seed=21)
    dust = I.dust(160, 78, n=12, count=18, seed=3)
    return cv, dict(holes=holes, glow=glow, dust=dust)


def _over(base, top):
    b = base.convert('RGBA')
    b.alpha_composite(top)
    return b


def build_nijimura_hall():
    cv, L = nijimura_hall()
    K.save_layers('nijimura_hall', dict(room=cv, **L))
    K.update_meta('nijimura_hall',
                  anchors=dict(painting=[138, F - 28], window_1=[210, F - 26], window_2=[490, F - 26], mirror=[362, F - 26]),
                  layers={'dust': dict(x=150, y=96, w=160, h=78, n=12)})
    return cv


# ================================================================ 虹村家楼梯间 nijimura_stairs（480）
#   二楼平台是玩法上的高度（形兆站在 y = 80），不动：一楼层高 58 px（老洋房的大楼梯厅），二楼 50 px
def stair_y(x):
    """楼梯斜线（和旧图、脚本一致）：x 110 → 290，y 134 → 80"""
    t = (x - 110) / 180.0
    return 134 - 54 * max(0.0, min(1.0, t))


def nijimura_stairs():
    W = 480
    cv = Cv(W, 180)
    L2 = 80                               # 二楼地面
    C2 = L2 - 50                          # 二楼天花
    # 最上面：阁楼的暗影（梁）
    cv.rect(0, 0, W - 1, C2 - 4, '#1c1614')
    for x in range(20, W, 60):
        cv.line(x, C2 - 5, x + 30, 0, '#2a201a')
    K.ceiling_slab(cv, 0, W - 1, C2, 4, '#3a2a20')
    # 二楼的墙（只有平台那一段有地面，左边是挑空）
    K.wall(cv, 0, W - 1, NJ['wall'], y0=C2, y1=L2, stripes=(10, NJ['wall2']), wains=None, base=None, crown='#2e2018')
    nj_wall(cv, 0, W - 1, L2 + 4, seed=9)
    K.wall(cv, 0, 289, NJ['wall'], y0=C2, y1=L2 + 8, stripes=(10, NJ['wall2']), base=None, crown='#2e2018')   # 挑空的那一段墙连下来
    r = K.rng(4)
    for _ in range(5):
        I.stain(cv, r.randint(20, 280), r.randint(C2 + 8, L2), r.randint(8, 16), r.randint(6, 12), shade(NJ['wall'], -0.35), seed=int(r.randint(99)))
    K.floor_wood(cv, 0, W - 1, c=NJ['floor'], seed=8)
    # 拱窗（光往左下落）
    cv.rect(173, 92, 191, 124, NJ['frame'])
    cv.ellipse(182, 93, 10, 8, NJ['frame'])
    cv.rect(175, 93, 189, 122, '#f4eccc')
    cv.ellipse(182, 94, 8, 6, '#f4eccc')
    cv.vline(182, 86, 122, NJ['frame'])
    cv.hline(175, 189, 106, NJ['frame'])
    # 一楼的门、楼梯下的小门、平台下的黑门洞
    K.door(cv, 46, F, c='#5a3a28', frame=NJ['frame'], knob='#c8a850')
    I.doorway(cv, 403, F, 18, 34, NJ['frame'])
    # 二楼平台：楼板 + 两扇门（右边那扇开着）+ 梯子 + 活板门
    cv.rect(290, L2 + 1, W - 1, L2 + 4, '#3a2a20')
    cv.hline(290, W - 1, L2 + 1, '#6a4a34')
    K.door(cv, 333, L2, c='#5a3a28', frame=NJ['frame'], knob='#c8a850')
    I.doorway(cv, 393, L2, 18, 34, NJ['frame'])
    cv.rect(400, L2 - 33, 403, L2, '#5a3a28')
    I.ladder(cv, 453, C2 + 2, L2, 8)
    cv.rect(449, C2 - 1, 467, C2 + 1, '#120e0c')
    # 楼梯：12 级，侧板一直落到地面；扶手
    for i in range(12):
        xa = 110 + i * 15
        ya = int(round(134 - (i + 1) * 4.5))
        cv.rect(xa, ya, xa + 14, F, '#4a3226')
        cv.hline(xa, xa + 14, ya, '#7a5640')
        cv.hline(xa, xa + 14, ya + 1, '#5a3e2e')
    for x in range(110, 291):                              # 侧板下沿（楼梯下面是储物间的斜墙）
        pass
    K.door(cv, 240, F, w=13, h=24, c='#4a3226', frame=NJ['frame'], knob='#c8a850', panel=False)
    for i in range(0, 13):                                 # 扶手栏杆
        xa = 110 + i * 15
        ya = int(round(134 - i * 4.5))
        cv.vline(xa, ya - 14, ya, '#5a3a28')
    cv.line(110, 134 - 14, 290, 80 - 14, '#6a4630')
    cv.line(110, 134 - 15, 290, 80 - 15, '#7a5640')
    cv.rect(108, 134 - 18, 111, F, '#5a3a28')
    cv.rect(288, L2 - 18, 291, L2 + 4, '#5a3a28')
    # 平台的栏杆（人站上去腿在栏杆后面：栏杆单独存一层前景也行，这里直接画在近处）
    I.balustrade(cv, 292, W - 2, L2, 14)
    old = I.bullet_holes(W, [(30, 96, 460, F - 4, 8, False), (30, F + 6, 460, 176, 5, True)], seed=13)
    cv.a = np.array(_over(cv.img(), old))
    night_tint(cv, 0.82, tint=(0.96, 0.98, 1.02), keep=('#f4eccc',))
    glow = I.shafts(W, [[(175, 93), (189, 93), (150, 176), (96, 176)]], spots=[(124, 164, 34, 10, 0.3)], k=0.24)
    holes = I.bullet_holes(W, [(20, 40, 470, F - 4, 110, False), (20, F + 6, 470, 177, 50, True)], seed=23)
    dust = I.dust(62, 80, n=12, count=14, seed=5)
    return cv, dict(holes=holes, glow=glow, dust=dust)


def build_nijimura_stairs():
    cv, L = nijimura_stairs()
    K.save_layers('nijimura_stairs', dict(room=cv, **L))
    K.update_meta('nijimura_stairs', anchors=dict(window=[182, 106], hatch=[458, 30]),
                  layers={'dust': dict(x=110, y=94, w=62, h=80, n=12)})
    return cv


# ================================================================ 康一家客厅 hirose_living（320）
def sunset_view(cv, x0, y0, x1, y1):
    K.vgrad(cv, x0, y0, x1, y1, ['#f6a060', '#f8c078', '#fbe0a0'])
    cv.ellipse(x1 - 6, y0 + 8, 3, 3, '#fff4c8')
    cv.rect(x0, y1 - 5, x1, y1, '#6a8a5a')
    cv.rect(x0 + 2, y1 - 9, x0 + 12, y1 - 5, '#b08a6a')
    cv.rect(x0 + 1, y1 - 11, x0 + 13, y1 - 9, '#7a4a3a')


def hirose_living(door_open=False):
    W = 320
    cv = Cv(W, 180)
    C = F - K.CEIL
    K.sky(cv, 0, W - 1, C - 4, K.SKY_EVE)
    K.cloud(cv, 40, 30, 40, 2, ('#ffe0c0', '#f8c0a0', '#d89a90'))
    K.roof_hip(cv, 10, 310, C - 44, C - 70, '#4a3a44', inset=40)
    K.siding(cv, 18, C - 42, 302, C - 5, '#e8d8c0')
    for wx in (70, 160, 250):
        K.window_ext(cv, wx - 12, C - 33, wx + 12, C - 15, lit='#f6d98a' if wx == 160 else None, nx=2)
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#6a4e36')
    K.wall(cv, 8, 311, '#f0dcc8', stripes=(8, '#e8d0b8'), wains=(13, '#b08a60'), crown='#8a6a44')
    K.floor_wood(cv, 0, W - 1, c='#c08a58')
    for x in (5, 312):
        K.cut_wall(cv, x, C, 179, 3)
    cv.rect(0, C, 4, 179, '#8a6a5a')
    cv.rect(315, C, W - 1, 179, '#8a6a5a')
    # 门（左边，state.door = 1 时开着）
    if door_open:
        I.doorway(cv, 27, F, 17, 34, '#6a4a2c', inside='#3a2a22')
        cv.rect(34, F - 33, 37, F, '#a87a4c')
    else:
        K.door(cv, 27, F, c='#a87a4c', frame='#6a4a2c', glass='#d8e0e0')
    K.cabinet(cv, 56, 92, F, 13, '#9a7248', doors=2)
    cv.rect(66, F - 19, 82, F - 14, '#e8e0d0')             # 面包箱
    cv.hline(66, 82, F - 19, '#c84a4a')
    cv.put(86, F - 16, '#d04a8a')
    cv.vline(86, F - 15, F - 14, '#4a8a4a')
    K.clock(cv, 76, F - 32, 3)
    K.calendar(cv, 104, F - 30)
    K.sofa(cv, 164, F, w=46, c='#5a8a5a', cushion='#c8b888')
    K.picture(cv, 164, F - 28, 18, 11, '#8a6a3a', ('#8ac0e0', '#3a7a9a', '#f4f4f0'))
    K.bookshelf(cv, 214, 238, F, 30, '#8a6240', seed=3)
    K.window(cv, 256, F - 35, 304, F - 14, frame='#f4ece0', nx=2, view=sunset_view, curtain='#f0e0d0', rod='#8a6a44')
    K.plant(cv, 266, F - 14, 7, pot='#c86a4a', seed=2)
    cv.rect(288, F - 19, 292, F - 15, '#f8f8f4')            # 窗台上的招财猫
    cv.put(289, F - 20, '#f8f8f4')
    cv.put(291, F - 20, '#f8f8f4')
    cv.put(290, F - 17, '#d04a4a')
    K.rug(cv, 110, 230, 152, 168, '#4a6a9a', '#c8b888', '#c8b888')
    K.lamp_ceiling(cv, 160, C + 2, w=12)
    return cv


def build_hirose_living():
    cv = hirose_living(False)
    op = hirose_living(True)
    # 开着的门单独存一层：只留门那一块
    d = Cv(320, 180)
    d.a[F - 38:F + 1, 14:42] = op.a[F - 38:F + 1, 14:42]
    glow = I.shafts(320, [[(258, F - 34), (302, F - 34), (236, 172), (150, 172)]], spots=[(196, 160, 46, 10, 0.3)], col='#ffc880', k=0.2)
    dust = I.dust(100, 70, n=12, count=14, seed=7)
    K.save_layers('hirose_living', dict(room=cv, door_open=d, glow=glow, dust=dust))
    K.update_meta('hirose_living', anchors=dict(clock=[76, F - 32], window=[280, F - 24]), layers={'dust': dict(x=170, y=100, w=100, h=70, n=12)})
    return cv


# ================================================================ 葡萄丘高中走廊 budogaoka_hall（640）
def classroom_view(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1, y1, '#f0e8d0')
    cv.rect(x0, y0, x1, y0 + 3, '#c8dce8')
    for x in range(x0 + 5, x1 - 6, 14):
        cv.rect(x, y1 - 7, x + 8, y1 - 6, '#c8a878')
        cv.vline(x + 1, y1 - 5, y1, '#8a8e96')
        cv.vline(x + 7, y1 - 5, y1, '#8a8e96')
        cv.rect(x + 2, y1 - 11, x + 6, y1 - 8, '#5a6a8a')


def budogaoka_hall(locker_open=False):
    W = 640
    cv = Cv(W, 180)
    C = F - 50
    K.sky(cv, 0, W - 1, C - 4, K.SKY_DAY)
    K.cloud(cv, 120, 16, 50, 3)
    K.cloud(cv, 470, 22, 40, 4)
    # 楼上一层的外墙（一排长窗）+ 楼顶
    cv.rect(0, C - 56, W - 1, C - 5, '#ece6da')
    cv.rect(0, C - 60, W - 1, C - 57, '#5a9a8a')
    cv.hline(0, W - 1, C - 60, '#7ab8a8')
    for x in range(10, W - 20, 30):
        cv.rect(x, C - 42, x + 22, C - 20, '#f4f0e6')
        cv.rect(x + 1, C - 41, x + 21, C - 21, '#8cb4cc')
        cv.vline(x + 8, C - 42, C - 20, '#f4f0e6')
        cv.vline(x + 15, C - 42, C - 20, '#f4f0e6')
        cv.line(x + 2, C - 23, x + 6, C - 39, '#b8d4e4')
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#8a8a86')
    # 走廊：上白下绿的墙
    K.wall(cv, 0, W - 1, '#f2eee0', y0=C, y1=F, base='#5a7a6a', crown='#c8c4b4')
    cv.rect(0, F - 16, W - 1, F - 2, '#8ab0a0')
    cv.hline(0, W - 1, F - 16, '#6a9484')
    K.floor_plain(cv, 0, W - 1, c='#c8b48a', line='#b8a47a')
    for x in range(40, W, 110):                            # 地上的窗光
        K.dither(cv, x, F + 6, x + 40, 178, '#e8d8a8', 0.5)
    for x in range(30, W, 70):                             # 天花的日光灯
        cv.rect(x, C + 2, x + 24, C + 3, '#ffffff')
    # 门上面一直到天花的气窗
    for x in range(8, W - 30, 26):
        cv.rect(x, C + 6, x + 22, C + 13, '#f4f0e6')
        cv.rect(x + 1, C + 7, x + 21, C + 12, '#b8d8e8')
    I.class_door(cv, 30, F, sign='1-A')
    I.lockers(cv, 78, 188, F, 30)
    if locker_open:
        cv.rect(144, F - 29, 151, F - 16, '#1a1a20')
        cv.rect(152, F - 29, 154, F - 16, '#7a888c')
    I.class_door(cv, 232, F, sign='1-B')
    cv.rect(258, F - 34, 284, F - 16, '#8a6a44')            # 公告栏
    cv.rect(259, F - 33, 283, F - 17, '#c8a868')
    for (a, b, col) in ((261, F - 31, '#f4f4f0'), (270, F - 31, '#f0d8d8'), (261, F - 23, '#d8e8f0'), (272, F - 24, '#f4f0c8')):
        cv.rect(a, b, a + 7, b + 5, col)
        cv.hline(a + 1, a + 5, b + 2, '#8a8a90')
    cv.rect(306, F - 22, 322, F, '#d03a3a')                 # 消火栓箱
    cv.hline(306, 322, F - 22, '#e86a6a')
    cv.rect(309, F - 18, 319, F - 12, '#f4f0e0')
    cv.ellipse(314, F - 26, 2.5, 2.5, '#e03030')
    cv.rect(334, F - 21, 342, F - 12, '#5a9a6a')            # 墙上的绿色公用电话
    cv.rect(336, F - 19, 340, F - 16, '#2a2a30')
    I.class_door(cv, 362, F, sign='3-A')
    K.window(cv, 404, F - 34, 540, F - 15, frame='#5a7a6a', nx=4, view=classroom_view)
    I.class_door(cv, 586, F, sign='3-B')
    # 楼梯口
    cv.rect(614, C + 2, W - 1, F, '#d8d4c4')
    for i in range(6):
        cv.rect(614 + i * 4, F - 5 - i * 5, W - 1, F - i * 5, '#b8b4a4')
        cv.hline(614 + i * 4, W - 1, F - 5 - i * 5, '#e0dccc')
    cv.line(614, F - 20, 638, F - 50, '#6a6a70')
    cv.rect(606, C + 8, 622, C + 13, '#3aa05a')              # 安全出口灯
    return cv


def build_budogaoka_hall():
    cv = budogaoka_hall(False)
    op = budogaoka_hall(True)
    d = Cv(640, 180)
    d.a[F - 31:F - 14, 142:156] = op.a[F - 31:F - 14, 142:156]
    K.save_layers('budogaoka_hall', dict(room=cv, locker_open=d))
    K.update_meta('budogaoka_hall', anchors=dict(empty_seat=[507, F - 22]))
    return cv


# ================================================================ 教室 budogaoka_classroom（320）
def yard_view(cv, x0, y0, x1, y1):
    K.vgrad(cv, x0, y0, x1, y1, ['#f6a060', '#f8c078', '#fbe0a0'])
    cv.ellipse(x1 - 10, y0 + 9, 4, 4, '#fff4c8')
    for x in range(x0, x1, 9):
        cv.ellipse(x + 4, y1 - 2, 6, 5, '#5a7a4a')
    cv.rect(x0, y1 - 2, x1, y1, '#4a6a3e')


def budogaoka_classroom():
    W = 320
    cv = Cv(W, 180)
    C = F - 50
    K.sky(cv, 0, W - 1, C - 4, K.SKY_EVE)
    cv.rect(0, C - 56, W - 1, C - 5, '#ece6da')
    cv.rect(0, C - 60, W - 1, C - 57, '#5a9a8a')
    for x in range(10, W - 20, 30):
        cv.rect(x, C - 42, x + 22, C - 20, '#f4f0e6')
        cv.rect(x + 1, C - 41, x + 21, C - 21, '#d8a878')
        cv.vline(x + 11, C - 42, C - 20, '#f4f0e6')
    K.darken(cv, 0, C - 60, W - 1, C - 5, 0.92, (1.04, 0.98, 0.92))
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#8a8a86')
    K.wall(cv, 0, W - 1, '#f4ecd8', y0=C, y1=F, wains=(12, '#c8a878'), base='#8a6a44', crown='#c8c4b4')
    K.floor_wood(cv, 0, W - 1, c='#c8a068')
    for x in range(30, W, 90):
        cv.rect(x, C + 2, x + 24, C + 3, '#ffffff')
    # 门（最左边，侧墙上的推拉门只露一条边）
    cv.rect(0, F - 34, 6, F, '#a8845a')
    cv.vline(6, F - 34, F, '#5a7a6a')
    I.blackboard(cv, 22, 106, F)
    cv.rect(108, F - 34, 118, F - 22, '#f4f0e0')            # 课程表
    for yy in range(F - 32, F - 23, 2):
        cv.hline(109, 117, yy, '#a8a8a0')
    K.clock(cv, 64, F - 40, 3)
    I.podium(cv, 62, F)
    # 靠窗的一面：两扇大窗 + 窗下的矮柜
    K.window(cv, 136, F - 36, 216, F - 15, frame='#f4ece0', nx=3, view=yard_view, curtain='#f4e4c0')
    K.window(cv, 232, F - 36, 312, F - 15, frame='#f4ece0', nx=3, view=yard_view, curtain='#f4e4c0')
    K.cabinet(cv, 130, 318, F, 12, '#b89060', doors=12)
    for x, col in ((150, '#3a4a7a'), (176, '#7a3a3a'), (236, '#3a6a4a'), (270, '#3a4a7a'), (300, '#8a6a3a')):   # 柜上的书包
        cv.rect(x, F - 18, x + 8, F - 13, col)
        cv.hline(x, x + 8, F - 18, shade(col, 0.3))
    # 课桌（靠前一排，落在 y = 146 一带，人从前面走）
    for i, x in enumerate((141, 165, 189, 213, 237, 261, 285)):
        I.school_desk(cv, x, 146, face=-1, bag=('#3a4a7a', None, '#7a3a3a', None)[i % 4])
    return cv


def build_budogaoka_classroom():
    cv = budogaoka_classroom()
    sun = I.shafts(320, [[(136, F - 36), (216, F - 36), (150, 178), (40, 178)], [(232, F - 36), (312, F - 36), (250, 178), (140, 178)]],
                   col='#ffb870', k=0.16)
    K.save_layers('budogaoka_classroom', dict(room=cv, sun=sun))
    K.update_meta('budogaoka_classroom', anchors=dict(bento=[189, 146 - 13]))
    return cv


# ================================================================ 海边别墅门外 seaside_villa_out（640）
def seaside_villa_out():
    W = 640
    cv = Cv(W, 180)
    G_ = GROUND
    # 路对面是海：栏杆后面一条海面（远景层里还有一层海和天）
    cv.rect(392, G_ - 20, 486, G_, '#3a86c0')
    for x in range(392, 486, 8):
        cv.hline(x, x + 4, G_ - 16 + (x // 8) % 4 * 4, '#7ab8e0')
    OB = K.old_lib()
    im = cv.img()
    for x, h, sd in ((20, 100, 1), (430, 104, 2), (540, 96, 3)):
        im = OB.pine(im, x, G_ - 1, h=h, seed=sd)
    cv.a = np.array(im)
    # 由花子的别墅：白色洋房、蓝屋顶；二楼左边那扇挂粉色窗帘（康一被关的房间）
    O.house(cv, 60, 250, G_ - 2, s=0.9, wall_c='#f4f0e6', roof_c='#3a5a78', door_x=176, door_c='#7a4a34', win1=[103, 226],
            win2=[103, 176, 226], trim='#ffffff')
    cv.rect(94, G_ - 2 - 74, 112, G_ - 2 - 60, '#f4a8c0')     # 粉色窗帘
    for x in range(95, 112, 3):
        cv.vline(x, G_ - 76, G_ - 62, '#e088a4')
    O.house(cv, 296, 384, G_ - 2, s=0.86, wall_c='#f0e4b8', roof_c='#a8483a', door_x=None, win1=[322, 360], win2=[322, 360])
    O.house(cv, 560, 660, G_ - 2, s=0.88, wall_c='#f0ece0', roof_c='#3a5a44', door_x=610, win1=[580], win2=[580, 630])
    # 围墙、树篱、门柱
    for xa, xb, sd in ((0, 157, 1), (195, 391, 2), (544, 591, 3), (629, W - 1, 4)):
        O.hedge(cv, xa + 1, xb - 1, G_ - 13, 7, seed=sd)
        O.block_wall(cv, xa, xb, G_, 13, '#d0cabc')
    O.gate_post(cv, 160, G_, 23, plate='#2a2a30')
    O.gate_post(cv, 192, G_, 23)
    O.gate_iron(cv, 163, 189, G_, 17, open_=True)
    O.mailbox(cv, 135, G_)
    # 海边的栏杆
    cv.hline(392, 486, G_ - 18, '#e8e8ec')
    cv.hline(392, 486, G_ - 12, '#d0d0d8')
    for x in range(394, 486, 12):
        cv.vline(x, G_ - 18, G_, '#e8e8ec')
    cv.rect(392, G_ - 3, 486, G_, '#b0aca4')
    O.sign_post(cv, 489, G_, 44, 'arrow')
    # 电话亭（2.2 m）
    bx = 513
    cv.rect(bx - 8, G_ - 37, bx + 8, G_, '#d8dce0')
    cv.rect(bx - 9, G_ - 39, bx + 9, G_ - 37, '#3a8a5a')
    cv.rect(bx - 6, G_ - 34, bx + 6, G_ - 6, '#a8ccdc')
    cv.line(bx - 5, G_ - 10, bx + 2, G_ - 33, '#d0e6f0')
    cv.rect(bx - 2, G_ - 24, bx + 3, G_ - 16, '#4a8a5a')
    cv.vline(bx, G_ - 34, G_ - 6, '#d8dce0')
    p1 = O.pole(cv, 270, G_)
    p2 = O.pole(cv, 530, G_)
    O.wires(cv, p1, p2, sag=7)
    O.wires(cv, [(-40, 12), (-40, 22)], [p1[0], p1[4]], sag=5)
    O.wires(cv, [p2[3], p2[5]], [(W + 40, 12), (W + 40, 22)], sag=4)
    O.street_lamp(cv, 420, G_, 76, side=-1)
    ground_street(cv, W)
    return cv


def build_seaside_villa_out():
    cv = seaside_villa_out()
    K.save_layers('seaside_villa_out', {'near': cv})
    K.update_meta('seaside_villa_out', anchors=dict(villa_window=[103, GROUND - 69], booth=[513, GROUND], sign=[489, GROUND]))
    return cv


# ================================================================ 海边别墅屋里 seaside_villa（640）
VILLA_STAIR = (150, 232)                 # 楼梯：x 150 → 232，从地面升到天花的开口


def sea_view(cv, x0, y0, x1, y1):
    K.vgrad(cv, x0, y0, x1, (y0 + y1) // 2, ['#8cc0f0', '#c8e4f8'])
    cv.rect(x0, (y0 + y1) // 2, x1, y1, '#3a86c0')
    for y in range((y0 + y1) // 2 + 1, y1, 3):
        for x in range(x0 + (y % 5), x1, 6):
            cv.hline(x, min(x1, x + 2), y, '#7ab8e0')


def seaside_villa():
    W = 640
    cv = Cv(W, 180)
    C = F - 46
    K.sky(cv, 0, W - 1, C - 4, K.SKY_DAY)
    K.cloud(cv, 90, 24, 50, 5)
    K.cloud(cv, 480, 18, 44, 6)
    K.roof_hip(cv, 4, 636, C - 44, C - 72, '#3a5a78', inset=42)
    K.siding(cv, 12, C - 42, 628, C - 5, '#f4f0e6')
    for wx in (60, 150, 240, 330, 420, 510, 590):
        K.window_ext(cv, wx - 11, C - 33, wx + 11, C - 15, frame='#ffffff', nx=2, shutter='#3a5a78')
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#6a4e36')
    # 玄关（0–124）铺石砖，屋里铺木地板
    K.wall(cv, 8, 631, '#f2ecdc', y0=C, y1=F, wains=(13, '#8aa4b8'), base='#5a6a7a', crown='#7a5a3c')
    K.floor_tile(cv, 0, 124, c1='#d8d4c8', c2='#c0bcb0', size=11)
    K.floor_wood(cv, 125, W - 1, c='#8a5a3a')
    for x in (5, 632):
        K.cut_wall(cv, x, C, 179, 3)
    cv.rect(0, C, 4, 179, '#7a9ab0')
    cv.rect(635, C, W - 1, 179, '#7a9ab0')
    cv.rect(124, F, 126, 179, '#5a3a28')                    # 玄关和屋里之间的门槛
    # 玄关：伞架、大门（双开，彩色玻璃气窗）、椭圆镜、鞋柜的位置（鞋柜是单独的一层）
    cv.rect(11, F - 7, 17, F, '#5a5a62')
    cv.vline(13, F - 15, F - 7, '#c84a4a')
    cv.vline(16, F - 13, F - 7, '#2a2a34')
    x0, y0, x1, y1 = K.door(cv, 57, F, w=24, h=36, c='#6a4030', frame='#4a2c20', knob='#e8c860')
    cv.vline(57, y0, F, '#4a2c20')
    cv.rect(x0, y0 - 7, x1, y0 - 3, '#4a2c20')
    for i, col in enumerate(('#d04a4a', '#e8c040', '#3a7ad0', '#e8c040', '#d04a4a')):
        cv.rect(x0 + 1 + i * 5, y0 - 6, x0 + 4 + i * 5, y0 - 4, col)
    I.oval_mirror(cv, 109, F - 27, 4, 6, frame='#c8a850', glass='#b8d0e0', crack=False)
    # 楼梯（上二楼）：10 级，楼梯下一个壁橱
    n = 10
    run = (VILLA_STAIR[1] - VILLA_STAIR[0]) / n
    rise = (F - C) / n
    for i in range(n):
        xa = int(round(VILLA_STAIR[0] + i * run))
        ya = int(round(F - (i + 1) * rise))
        cv.rect(xa, ya, VILLA_STAIR[1] + 8, F, '#e8e0d0')
        cv.rect(xa, ya, int(round(xa + run)), ya + 1, '#8a5a3a')
        cv.hline(xa, int(round(xa + run)), ya, '#a8744a')
    cv.rect(VILLA_STAIR[1] + 9, C, VILLA_STAIR[1] + 11, F, '#7a5a3c')
    for i in range(0, n + 1, 1):                            # 扶手
        xa = int(round(VILLA_STAIR[0] + i * run))
        ya = int(round(F - i * rise))
        cv.vline(xa, ya - 13, ya, '#5a3a28')
    cv.line(VILLA_STAIR[0], F - 14, VILLA_STAIR[1], C - 13, '#6a4630')
    K.door(cv, 213, F, w=13, h=22, c='#c8b8a0', frame='#8a7a66', panel=False)     # 楼梯下的壁橱
    K.picture(cv, 172, F - 40, 12, 8, '#c8a850', ('#8cc0f0', '#f4f4f0', '#ffffff'))
    cv.rect(244, C + 2, 246, F, '#7a5a3c')                   # 柱
    # 餐厅：朝海的窗、吊灯、餐桌（另画在可走带上）、餐边柜 + 照片
    K.window(cv, 296, F - 36, 344, F - 15, frame='#ffffff', nx=2, view=sea_view, curtain='#f4f0e6', rod='#7a5a3c')
    K.lamp_ceiling(cv, 348, C + 2, c='#e8c060', w=10, cord=8)
    K.cabinet(cv, 372, 408, F, 14, '#7a5030', doors=2, drawers=2)
    cv.rect(398, F - 20, 405, F - 15, '#c8a850')
    cv.rect(399, F - 19, 404, F - 16, '#d8e0e8')
    cv.rect(378, F - 21, 381, F - 15, '#f4f0e6')             # 花瓶 + 红花
    cv.put(379, F - 23, '#d03a4a')
    cv.put(381, F - 24, '#d03a4a')
    cv.put(378, F - 24, '#d03a4a')
    cv.rect(428, C + 2, 430, F, '#7a5a3c')
    K.bookshelf(cv, 446, 480, F, 32, '#6a4630', seed=5)
    # 书房：墙上的日程表、书桌（电椅是单独的一层）、落地窗
    cv.rect(505, F - 40, 553, F - 22, '#f4f0e6')
    cv.rect(505, F - 40, 553, F - 37, '#f08aa8')
    for yy in range(F - 34, F - 23, 3):
        for xx in range(508, 551, 6):
            cv.hline(xx, xx + 3, yy, '#a8a8a0')
    cv.rect(544, F - 35, 550, F - 28, '#e8c8b0')              # 贴着康一的照片
    cv.rect(546, F - 34, 548, F - 32, '#b8bcc8')
    K.table(cv, 535, F, w=44, h=11, c='#7a5030')
    cv.rect(520, F - 15, 524, F - 12, '#3a8a5a')              # 台灯
    cv.vline(522, F - 12, F - 11, '#2a2a30')
    for i, col in enumerate(('#d04a4a', '#e8c040', '#3a7ad0')):
        cv.hline(538, 550, F - 12 - i, col)
    K.window(cv, 586, F - 37, 628, F - 2, frame='#ffffff', nx=2, ny=2, sill=False, view=sea_view, curtain='#f4f0e6')
    # 可走带上的餐桌（桌布 + 四把椅子的靠背）
    I.bistro_chair(cv, 322, 150, face=1)
    I.bistro_chair(cv, 374, 150, face=-1)
    I.dining_table(cv, 348, 150, w=40, cloth=('#f8f6f0', '#e8e4d8'))
    for x, col in ((338, '#e8c060'), (348, '#c85a3a'), (358, '#f4f4f0')):     # 桌上的菜
        cv.rect(x - 2, 137, x + 2, 138, col)
    return cv


def hair_mass(cv, x0, y0, x1, y1, seed=0, density=1.0):
    """由花子的头发：一缕一缕黑紫色的发丝从上往下垂、互相缠着"""
    r = K.rng(seed)
    cols = ['#1a1424', '#2a2438', '#3a3450', '#120e1a']
    n = int((x1 - x0) / 2.2 * density)
    for _ in range(n):
        x = r.uniform(x0, x1)
        y = y0
        ln = r.uniform((y1 - y0) * 0.5, (y1 - y0))
        ph = r.uniform(0, 6.28)
        col = cols[int(r.randint(len(cols)))]
        for i in range(int(ln)):
            xx = x + 2.2 * np.sin(i * 0.22 + ph)
            cv.put(int(round(xx)), int(y + i), col)
            if r.rand() < 0.3:
                cv.put(int(round(xx)) + 1, int(y + i), col)


def build_seaside_villa():
    cv = seaside_villa()
    C = F - 46
    L = dict(room=cv)
    # 鞋柜（单独一层，被头发拖走时关掉）：1.1 m 高
    sb = Cv(34, 26)
    K.cabinet(sb, 2, 31, 25, 18, '#8a6240', doors=3)
    for x in (6, 16, 24):
        sb.rect(x, 4, x + 4, 6, ('#3a3a44', '#8a4a3a', '#f4f4f0')[x % 3])
    L['shoebox'] = sb
    # 电椅（单独一层）：一把高背木椅，扶手和椅背上缠着电线
    ch = Cv(34, 44)
    by = 43
    ch.rect(10, by - 22, 12, by, '#6a4630')
    ch.rect(10, by - 22, 22, by - 20, '#7a5640')
    ch.rect(12, by - 20, 21, by - 8, '#5a3a28')
    ch.rect(10, by - 7, 24, by - 5, '#7a5640')
    ch.vline(24, by - 5, by, '#6a4630')
    ch.hline(12, 24, by - 11, '#6a4630')
    for y in range(by - 20, by - 6, 3):
        ch.hline(10, 23, y, '#e8c040')
    ch.put(9, by - 23, '#fff0a0')
    L['chair'] = ch
    # 头发四层
    hw = Cv(640, 70)
    hair_mass(hw, 8, 0, 632, 30, seed=1, density=0.8)
    L['hair_walls'] = hw
    hd = Cv(76, 110)
    hair_mass(hd, 4, 0, 72, 108, seed=2, density=1.6)
    L['hair_door'] = hd
    hs = Cv(140, 120)
    hair_mass(hs, 6, 0, 134, 118, seed=3, density=1.3)
    L['hair_stairs'] = hs
    hwi = Cv(66, 124)
    hair_mass(hwi, 4, 0, 62, 122, seed=4, density=1.6)
    L['hair_window'] = hwi
    K.save_layers('seaside_villa', L)
    K.update_meta('seaside_villa',
                  anchors=dict(knob=[57, F - 17], mirror=[109, F - 27], stairs_top=[232, C + 2], handrail=[190, F - 36],
                               painting=[172, F - 40], dinner=[348, 138], window_dining=[320, F - 26], photo=[402, F - 18],
                               schedule=[529, F - 31]),
                  layers={'shoebox': dict(x=90, y=F - 25), 'chair': dict(x=518, y=F - 43), 'hair_walls': dict(x=0, y=C),
                          'hair_door': dict(x=20, y=C - 2), 'hair_stairs': dict(x=132, y=C - 4), 'hair_window': dict(x=574, y=C - 4)})
    return cv


# ================================================================ 意大利餐厅 trattoria（480）
def street_view(cv, x0, y0, x1, y1):
    K.vgrad(cv, x0, y0, x1, y1, ['#f8c078', '#fbe0a0'])
    for x in range(x0 + 2, x1 - 6, 12):
        cv.rect(x, y1 - 12, x + 8, y1, '#c8a078')
        cv.rect(x + 2, y1 - 9, x + 5, y1 - 5, '#8a9ab0')


def trattoria():
    W = 480
    cv = Cv(W, 180)
    C = F - 48
    K.sky(cv, 0, W - 1, C - 4, K.SKY_EVE)
    K.roof_hip(cv, 4, 476, C - 20, C - 44, '#a8583a', inset=30)
    cv.rect(10, C - 20, 470, C - 5, '#f0e0b8')                # 檐下的外墙 + 店招
    cv.rect(150, C - 18, 330, C - 8, '#3a6a3a')
    ptext(cv, 176, C - 16, 'TRATTORIA TRUSSARDI', '#f4f0d8', 1, gap=1)
    for x, col in ((132, '#3a8a4a'), (138, '#f4f4f0'), (144, '#d03a3a')):
        cv.rect(x, C - 18, x + 5, C - 8, col)
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#5a3a28')
    K.wall(cv, 8, 471, '#f0d8a0', y0=C, y1=F, wains=(13, '#3a5a44'), base='#2a3a2e', crown='#5a3a28')
    for x in range(40, W, 80):                                # 天花的木梁
        cv.rect(x, C + 2, x + 5, C + 5, '#5a3a28')
    K.floor_tile(cv, 0, W - 1, c1='#b8603e', c2='#a8523a', size=12)
    for x in (5, 472):
        K.cut_wall(cv, x, C, 179, 3)
    cv.rect(0, C, 4, 179, '#c8a078')
    cv.rect(475, C, W - 1, 179, '#c8a078')
    # 入口门（玻璃门 + 意大利小旗）、临街的窗、盆栽
    K.door(cv, 32, F, w=17, h=34, c='#7a4a30', frame='#4a2c20', glass='#f8d8a0')
    for i, col in enumerate(('#3a8a4a', '#f4f4f0', '#d03a3a')):
        cv.rect(24 + i * 5, F - 43, 28 + i * 5, F - 40, col)
    K.window(cv, 68, F - 35, 116, F - 15, frame='#f4ece0', nx=2, view=street_view, curtain='#f8f0d8', rod='#5a3a28')
    K.plant(cv, 124, F, 14, pot='#b0603a', seed=3)
    # 菜单黑板、挂画、成串的蒜和辣椒
    cv.rect(156, F - 40, 180, F - 18, '#5a3a28')
    cv.rect(157, F - 39, 179, F - 19, '#2a3a34')
    for yy in range(F - 36, F - 21, 3):
        cv.hline(159, 159 + (yy * 7) % 14 + 5, yy, '#e8e8e0')
    K.picture(cv, 228, F - 32, 16, 10, '#c8a850', ('#a8d0e8', '#6a9a4a', '#f4e8b0'))
    for x, col in ((200, '#f4f0e0'), (262, '#d03a3a')):
        for yy in range(C + 6, C + 22, 3):
            cv.ellipse(x, yy, 1.6, 1.6, col)
    I.wine_rack(cv, 312, 344, F, 32)
    # 出菜口 + 吧台、厨房的弹簧门
    cv.rect(368, F - 34, 406, F - 16, '#5a3a28')
    cv.rect(370, F - 32, 404, F - 18, '#f8f4e8')
    cv.rect(380, F - 20, 392, F - 18, '#e8e8e8')
    cv.put(386, F - 21, '#d0703a')
    I.counter(cv, 362, 412, F, 15, '#7a5030', top='#c8a878')
    I.swing_door(cv, 443, F)
    # 吊灯
    for x in (118, 228, 318):
        K.lamp_ceiling(cv, x, C + 2, c='#3a6a4a', w=8, cord=10)
        cv.hline(x - 2, x + 2, C + 16, '#fff0b0')
    # 三张桌子（落在可走带上，y = 150）和椅子
    for tx in (118, 228, 318):
        I.bistro_chair(cv, tx - 30, 152, face=1)
        I.bistro_chair(cv, tx + 40 if tx == 228 else tx + 30, 152, face=-1)
        I.dining_table(cv, tx + (5 if tx == 228 else 0), 150, w=34)
        cv.rect(tx + 2, 135, tx + 3, 138, '#3a6a3a')           # 酒瓶
        cv.put(tx - 6, 138, '#f4f4f0')
    return cv


def build_trattoria():
    cv = trattoria()
    C = F - 48
    glow = I.shafts(480, spots=[(118, 142, 30, 16, 0.26), (228, 142, 30, 16, 0.26), (318, 142, 30, 16, 0.26)], col='#ffd890')
    K.save_layers('trattoria', dict(room=cv, glow=glow))
    K.update_meta('trattoria', anchors=dict(window=[92, F - 25], menu=[168, F - 29], pass_window=[387, F - 25]))
    return cv


# ================================================================ 餐厅厨房 trattoria_kitchen（480）
def trattoria_kitchen():
    W = 480
    cv = Cv(W, 180)
    C = F - 48
    K.sky(cv, 0, W - 1, C - 4, K.SKY_EVE)
    K.roof_hip(cv, 4, 476, C - 20, C - 44, '#a8583a', inset=30)
    cv.rect(10, C - 20, 470, C - 5, '#f0e0b8')
    cv.rect(372, C - 60, 384, C - 20, '#a8583a')               # 烤炉的烟囱
    cv.rect(370, C - 62, 386, C - 59, '#8a4630')
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#8a8a86')
    # 白瓷砖墙
    cv.rect(8, C, 471, F, '#f2f0e8')
    for y in range(C + 3, F, 4):
        cv.hline(8, 471, y, '#dcd8cc')
    for j, y in enumerate(range(C, F, 4)):
        for x in range(8 + (j % 2) * 4, 471, 8):
            cv.vline(x, y, min(F, y + 3), '#dcd8cc')
    cv.hline(8, 471, F - 24, '#3a8a5a')
    cv.rect(8, F - 1, 471, F, '#a8a498')
    K.floor_tile(cv, 0, W - 1, c1='#b8603e', c2='#a8523a', size=12)
    for x in (5, 472):
        K.cut_wall(cv, x, C, 179, 3, '#6a6a70')
    cv.rect(0, C, 4, 179, '#c8a078')
    cv.rect(475, C, W - 1, 179, '#c8a078')
    for x in range(60, W, 120):
        cv.rect(x, C + 2, x + 30, C + 3, '#ffffff')
    I.swing_door(cv, 24, F)
    # 水槽（台面 14）+ 墙上的洗手告示
    K.cabinet(cv, 58, 104, F, 14, '#c8ccd0', doors=3, handles='#6a6e76')
    cv.rect(66, F - 15, 96, F - 14, '#8a9098')
    cv.vline(84, F - 21, F - 16, '#b8bcc4')
    cv.hline(84, 87, F - 21, '#b8bcc4')
    cv.rect(70, F - 38, 92, F - 28, '#f4f0e0')
    cv.ellipse(76, F - 33, 2.5, 2.5, '#e8b090')
    cv.hline(81, 90, F - 35, '#3a8a5a')
    cv.hline(81, 88, F - 32, '#8a8a90')
    # 备料台 + 墙上的罐子架、挂着的锅
    K.cabinet(cv, 126, 232, F, 14, '#c8ccd0', doors=5, handles='#6a6e76')
    cv.rect(140, F - 16, 156, F - 15, '#c8a878')                # 砧板
    for x, col in ((144, '#d03a3a'), (148, '#d03a3a'), (152, '#4a9a4a')):
        cv.put(x, F - 17, col)
    cv.rect(190, F - 19, 193, F - 15, '#e8e0a0')                # 油瓶
    I.jar_shelf(cv, 130, 226, F - 32, seed=1)
    for x in (136, 152, 168, 184):
        cv.vline(x, F - 28, F - 25, '#6a6e76')
        cv.ellipse(x, F - 22, 3, 2.5, '#c8703a')
    # 炉灶 + 汤锅 + 烟罩
    I.stove_range(cv, 262, 332, F)
    I.pot(cv, 281, F - 15, 12, 8)
    cv.rect(310, F - 19, 322, F - 16, '#3a3a44')                # 平底锅
    cv.hline(322, 328, F - 17, '#3a3a44')
    cv.rect(258, F - 42, 336, F - 37, '#c8ccd0')
    cv.rect(266, C + 2, 328, F - 43, '#d8dce0')
    cv.hline(258, 336, F - 37, '#8a9098')
    # 砖烤炉
    I.brick_oven(cv, 375, F, 46, 42, fire=False)
    cv.line(404, F - 30, 414, F - 16, '#8a6a44')                 # 靠着的披萨铲
    cv.rect(412, F - 18, 418, F - 12, '#c8a878')
    # 大冰箱（1.9 m）
    cv.rect(438, F - 32, 468, F, '#d8dce0')
    cv.hline(438, 468, F - 32, '#f4f6f8')
    cv.vline(453, F - 32, F, '#8a9098')
    cv.vline(450, F - 22, F - 12, '#6a6e76')
    cv.vline(456, F - 22, F - 12, '#6a6e76')
    cv.rect(442, F - 28, 448, F - 24, '#f4f0c8')
    cv.hline(438, 468, F, '#6a6e76')
    return cv


def fire_strip(w=20, h=14, n=4, seed=0):
    """炉口里的火（n 帧横条）"""
    cv = Cv(w * n, h)
    r = K.rng(seed)
    for f in range(n):
        for x in range(1, w - 1):
            hh = int(3 + 5 * abs(np.sin(x * 0.9 + f * 1.7)) + r.randint(0, 3))
            for y in range(hh):
                c = '#fff0a0' if y < hh * 0.35 else ('#ffb040' if y < hh * 0.7 else '#e8602a')
                cv.put(f * w + x, h - 1 - y, c)
    return cv


def steam_strip(w=20, h=30, n=8, seed=0):
    """锅上的热气（n 帧横条）"""
    cv = Cv(w * n, h)
    r = K.rng(seed)
    wisps = [(r.uniform(4, w - 4), r.uniform(0, 1), r.uniform(0, 6.28)) for _ in range(4)]
    for f in range(n):
        for (x0, ph0, sw) in wisps:
            u = (ph0 + f / n) % 1.0
            y = h - 2 - u * (h - 4)
            x = x0 + 2.5 * np.sin(sw + u * 6.28)
            a = int(200 * (1 - u))
            for dx, dy in ((0, 0), (1, 0), (0, -1)):
                xx, yy = int(f * w + x + dx), int(y + dy)
                if 0 <= xx < w * n and 0 <= yy < h and xx // w == f:
                    cv.a[yy, xx] = (240, 240, 244, a)
    return cv


def build_trattoria_kitchen():
    cv = trattoria_kitchen()
    glow = I.shafts(480, spots=[(375, F - 14, 26, 18, 0.34), (375, 150, 30, 8, 0.16)], col='#ffb060')
    K.save_layers('trattoria_kitchen', dict(room=cv, fire=fire_strip(20, 14, 4, 3), glow=glow, steam=steam_strip(20, 30, 8, 5)))
    K.update_meta('trattoria_kitchen',
                  anchors=dict(faucet=[84, F - 21], sign=[80, F - 33], board=[148, F - 16], pot=[281, F - 24], oven_mouth=[375, F - 14]),
                  layers={'fire': dict(x=365, y=F - 23, w=20, h=14, n=4), 'steam': dict(x=271, y=F - 54, w=20, h=30, n=8)})
    return cv


BUILD = {
    'nijimura_hall': build_nijimura_hall, 'nijimura_stairs': build_nijimura_stairs,
    'hirose_living': build_hirose_living, 'budogaoka_hall': build_budogaoka_hall,
    'budogaoka_classroom': build_budogaoka_classroom, 'seaside_villa_out': build_seaside_villa_out,
    'seaside_villa': build_seaside_villa, 'trattoria': build_trattoria, 'trattoria_kitchen': build_trattoria_kitchen,
}

if __name__ == '__main__':
    out = sys.argv[1]
    for key in (sys.argv[2:] or list(BUILD)):
        cv = BUILD[key]()
        check_image(key, cv, out)
        print(key, cv.w)
