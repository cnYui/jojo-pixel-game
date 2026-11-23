# 序章背景（重画）：东方家客厅、上学路、校门、超市、东方家门口（傍晚 / 夜 / 雨）、海边路（雨 / 雨后）。
#   每张图的宽度、可走带、地面落点的锚点和旧图一样（剧情脚本按这些坐标走位）；
#   家具、门窗、房子按 第四部/docs/比例标准.md 重新定尺寸；室内画成剖面：一楼切开，上面是二楼外墙、屋顶和天空。
#   远景层（天空、海、远山，视差 0.4–0.5）没有比例问题，沿用旧图。俯视的杜王町地图和标题画面也不动。
#   用法：python 第四部/tools/art2/bg_pro.py 检查图输出目录 [背景 key …]
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from px import Cv, mix, shade, rgba  # noqa: E402
import bgkit as K  # noqa: E402
import bgout as O  # noqa: E402
from pfont import ptext  # noqa: E402
from bgkit import FLOOR, CEIL  # noqa: E402
from bgout import GROUND  # noqa: E402


def rain_view(cols=('#5a6478', '#77839a')):
    def fn(cv, x0, y0, x1, y1):
        K.vgrad(cv, x0, y0, x1, y1, [cols[0], cols[1]])
        cv.rect(x0, y1 - 6, x1, y1, '#3a5a4a')                 # 院子里的树篱
        K.dither(cv, x0, y1 - 8, x1, y1 - 7, '#3a5a4a', 0.5)
        cv.rect(x0 + (x1 - x0) // 2, y0 + 8, x1, y0 + 12, '#4a5468')     # 邻家屋顶的影子
    return fn


# ================================================================ 东方家客厅（480）
def higashikata_living():
    W, H = 480, 180
    cv = Cv(W, H)
    F, C = FLOOR, FLOOR - CEIL          # 墙脚线 138、天花线 94
    # ---- 上半截：雨天的天空、二楼外墙、屋顶
    K.sky(cv, 0, W - 1, C - 4, K.SKY_RAIN)
    K.roof_hip(cv, 36, 380, C - 44, C - 70, '#3c4658', inset=40)
    K.siding(cv, 42, C - 42, 374, C - 5, '#d8cdb8')
    for wx in (86, 196, 306):
        K.window_ext(cv, wx - 12, C - 33, wx + 12, C - 15, lit='#f6d98a' if wx == 196 else None, nx=2,
                     rail='#8a8478' if wx == 196 else None)
    K.roof_shed(cv, 374, 479, C - 8, C - 22, '#3c4658', 'left')      # 厨房的披檐
    K.roof_shed(cv, 0, 42, C - 8, C - 20, '#3c4658', 'right')        # 玄关的披檐
    K.darken(cv, 0, 0, W - 1, C - 5, 0.86)
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#6a4e36')
    # ---- 一楼：后墙、地板
    K.wall(cv, 11, 361, '#f0e4c8', stripes=(8, '#e8dab8'), wains=(13, '#b89060'), crown='#8a6a44')
    K.wall(cv, 365, 469, '#f4eede', base='#b0a890', crown='#8a6a44')
    K.floor_wood(cv, 0, 363, c='#c49660')
    K.floor_tile(cv, 364, W - 1)
    for x in (8, 470):                                               # 两头剖开的外墙 + 屋外
        K.cut_wall(cv, x, C, 179, 3)
    cv.rect(0, C, 7, 179, '#4a5a58')
    cv.rect(473, C, W - 1, 179, '#4a5a58')
    K.dither(cv, 0, F - 10, 7, 179, '#3a4a44', 0.5)
    K.dither(cv, 473, F - 10, W - 1, 179, '#3a4a44', 0.5)
    # ---- 客厅
    K.calendar(cv, 22, F - 27)
    K.phone_stand(cv, 22, F)
    K.door(cv, 48, F, c='#a87a4c', frame='#6a4a2c', side=-1)        # 通走廊的门（204 cm）
    K.window(cv, 68, F - 34, 128, F - 1, frame='#e8dcc4', nx=2, ny=1, sill=False, view=rain_view(), curtain='#d8847a', rod='#7a5a3c')
    K.switch(cv, 146, F - 21)
    K.bookshelf(cv, 174, 198, F, 30, '#8a6240', seed=7)
    K.sofa(cv, 231, F, w=48, c='#7a6ab8', cushion='#e8a0b8')
    x0, y0, x1, y1 = K.picture(cv, 229, F - 28, 9, 11, '#3a2a1e', ('#b8c8d8', '#2a3660', '#f0c8a0'))    # 良平的照片
    cv.rect(x0 + 3, y0 + 2, x0 + 5, y0 + 3, '#2a3660')
    cv.rect(x0 + 3, y0 + 4, x0 + 5, y0 + 5, '#f0c8a0')
    K.clock(cv, 262, F - 33, 3)
    K.cabinet(cv, 268, 296, F, 12, '#9a7248', doors=2)
    K.plant(cv, 276, F - 12, 9, seed=4)
    cv.rect(286, F - 15, 291, F - 13, '#e8e4d8')
    K.plant(cv, 304, F, 16, pot='#8a8a94', seed=9)
    K.tv_crt(cv, 325, F, stand_h=8)
    K.picture(cv, 325, F - 31, 14, 9, '#6a4a2a')
    K.bookshelf(cv, 343, 358, F, 30, '#9a7248', seed=11, empty=0.4)
    K.lamp_ceiling(cv, 200, C + 2, w=12)
    cv.rect(362, C + 2, 364, F, '#8a6a44')                           # 客厅和厨房之间的柱
    cv.vline(362, C + 2, F, shade('#8a6a44', 0.25))
    # ---- 厨房
    K.wall_cabinet(cv, 372, 446, C + 3, F - 24, '#e8dcc0')
    K.kitchen_counter(cv, 372, 446, F, '#e8dcc0', sink_x=400, stove_x=431)
    K.range_hood(cv, 431, F - 29, 16)
    K.kettle(cv, 431, F - 16)
    cv.rect(368, F - 23, 380, F - 22, '#b89060')                     # 放手套盒的小搁板
    K.fridge(cv, 450, F, 13, 28)
    K.rug(cv, 180, 290, 152, 166)
    K.lamp_ceiling(cv, 416, C + 2, w=8)
    return cv


def build_higashikata_living():
    cv = higashikata_living()
    F = FLOOR
    OB = K.old_lib()
    # 窗里的雨（8 帧循环）：落地窗玻璃 59 × 32
    winrain = OB.rain_strip(59, 32, n=8, near=12, far=9, length=(5, 3), slant=-0.18, cols=('#c8d2e0', '#9aa6b8'), alpha=(200, 150), seed=21)
    K.save_layers('higashikata_living', {'room': cv, 'winrain': winrain})
    K.update_meta('higashikata_living',
                  anchors=dict(kettle=[431, F - 18], wallhole=[159, 116], window=[98, F - 17], glovebox=[374, F - 23],
                               photo=[229, F - 28], tv=[325, F - 14]),
                  layers={'winrain': dict(x=69, y=F - 33, w=59, h=32)})
    return cv


# ================================================================ 户外通用：一条住宅街的近景
def ground_street(cv, w, sidewalk_c='#b9b5ad', road_c='#4c4c54'):
    O.sidewalk(cv, 0, w - 1, c=sidewalk_c)
    O.asphalt(cv, 0, w - 1, c=road_c)


def lot(cv, x0, x1, door_x=None, s=0.88, wall_c='#e6dccb', roof_c='#3e4a5e', hedge_seed=0, fence_h=13, hedge_h=7, gate=True,
        lit=None, **kw):
    """一户人家：房子（退在后面）+ 矮墙 + 树篱 + 正对着门的门柱和敞开的铁门"""
    O.house(cv, x0 + 6, x1 - 6, GROUND - 2, s=s, wall_c=wall_c, roof_c=roof_c, door_x=door_x, lit=lit, **kw)
    gaps = []
    if door_x is not None and gate:
        gaps.append((door_x - 15, door_x + 15))
    xa = x0
    for ga, gb in gaps + [(x1 + 1, x1 + 1)]:
        if ga - 1 > xa:
            O.hedge(cv, xa + 1, ga - 2, GROUND - fence_h, hedge_h, seed=hedge_seed + xa)
            O.block_wall(cv, xa, ga - 1, GROUND, fence_h)
        xa = gb + 1
    for ga, gb in gaps:
        O.gate_post(cv, ga + 2, GROUND, 23)
        O.gate_post(cv, gb - 2, GROUND, 23)
        O.gate_iron(cv, ga + 5, gb - 5, GROUND, 17, open_=True)
        cv.rect(ga + 5, GROUND - 1, gb - 5, GROUND, '#a8a296')


# ================================================================ 上学路 morioh_road（960）
def morioh_road():
    W = 960
    cv = Cv(W, 180)
    # 远处的空地（樱花树后面）：一条草坡，免得树干悬空
    cv.rect(0, GROUND - 6, W - 1, GROUND, '#8fa87a')
    K.dither(cv, 0, GROUND - 8, W - 1, GROUND - 7, '#8fa87a', 0.5)
    # 樱花树（房子之间、空地上）
    for x, h, w_, sd in ((132, 104, 66, 1), (276, 96, 58, 2), (446, 100, 64, 3), (548, 92, 56, 4), (700, 98, 60, 5), (808, 112, 78, 6),
                         (896, 96, 60, 7)):
        O.sakura(cv, x, GROUND - 2, h, w_, seed=sd)
    # 五户人家
    lot(cv, 4, 118, door_x=44, wall_c='#e6dccb', roof_c='#6a3a30', win1=[84], win2=[36, 84], hedge_seed=1)
    lot(cv, 146, 262, door_x=226, wall_c='#dfe4e2', roof_c='#2e4a44', win1=[178], win2=[178, 226], hedge_seed=2)
    lot(cv, 290, 378, door_x=None, wall_c='#e8dcc0', roof_c='#34405a', win1=[332], win2=[314, 354], hedge_seed=3)
    lot(cv, 566, 684, door_x=646, wall_c='#e6dccb', roof_c='#6a3a30', win1=[598], win2=[598, 646], hedge_seed=4)
    lot(cv, 708, 790, door_x=None, wall_c='#e2e0d2', roof_c='#2e4a44', win1=[730, 768], win2=[730, 768], hedge_seed=5)
    # 公交站那一段：矮墙 + 候车亭 + 站牌
    O.block_wall(cv, 379, 565, GROUND, 13)
    O.hedge(cv, 480, 564, GROUND - 13, 7, seed=9)
    O.bus_stop(cv, 408, GROUND, 46, 38)
    O.sign_post(cv, 452, GROUND, 40, 'bus')
    O.vending(cv, 531, GROUND, '#d8303a', seed=3)
    # 右头：白栅栏的空地 + 指路牌（往学校）
    cv.rect(791, GROUND - 3, W - 1, GROUND, '#8fa87a')
    for x in range(792, W, 4):
        cv.vline(x, GROUND - 12, GROUND, '#f4f2ea')
        cv.put(x, GROUND - 13, '#f4f2ea')
    cv.hline(791, W - 1, GROUND - 9, '#f4f2ea')
    cv.hline(791, W - 1, GROUND - 4, '#e0ded4')
    O.sign_post(cv, 930, GROUND, 46, 'arrow')
    # 电线杆和电线
    xs = [62, 270, 474, 690, 884]
    pts = [O.pole(cv, x, GROUND) for x in xs]
    for a, b in zip(pts[:-1], pts[1:]):
        O.wires(cv, a, b, sag=6)
    O.wires(cv, [(-40, 14), (-40, 24)], [pts[0][0], pts[0][4]], sag=4)
    O.wires(cv, [pts[-1][3], pts[-1][5]], [(W + 40, 14), (W + 40, 24)], sag=4)
    ground_street(cv, W)
    # 落在人行道上的花瓣
    r = K.rng(31)
    for _ in range(260):
        cv.put(int(r.randint(0, W)), int(r.randint(GROUND + 2, 164)), ('#f8bcd4', '#ec98bc', '#ffe0ec')[int(r.randint(3))])
    return cv


def build_morioh_road():
    cv = morioh_road()
    K.save_layers('morioh_road', {'near': cv})
    K.update_meta('morioh_road', anchors=dict(window=[332, 108], busstop=[408, GROUND], vending=[531, GROUND]))
    return cv


# ================================================================ 葡萄丘高中校门 budou_gate（640）
def school_block(cv, x0, x1, by, floors=3, s=0.7, wall_c='#ece6da', trim='#5a9a8a', glass='#8cb4cc', entrance_x=None, clock_x=None):
    """教学楼（退在操场后面，按 s 缩）：每层 50 px × s，横向长窗"""
    fh = int(round(50 * s))
    top = by - fh * floors
    cv.rect(x0, top, x1, by, wall_c)
    for f in range(floors):
        y1 = by - f * fh
        y0 = y1 - fh
        cv.hline(x0, x1, y1, shade(wall_c, -0.2))
        wy0, wy1 = y0 + int(fh * .28), y0 + int(fh * .68)
        for x in range(x0 + 8, x1 - 20, 30):
            if f == 0 and entrance_x is not None and abs(x + 11 - entrance_x) < 30:
                continue
            cv.rect(x, wy0, x + 22, wy1, '#f4f0e6')
            cv.rect(x + 1, wy0 + 1, x + 21, wy1 - 1, glass)
            cv.vline(x + 8, wy0, wy1, '#f4f0e6')
            cv.vline(x + 15, wy0, wy1, '#f4f0e6')
            cv.line(x + 2, wy1 - 2, x + 6, wy0 + 2, shade(glass, 0.35))
            cv.hline(x - 1, x + 23, wy1 + 1, shade(wall_c, -0.3))
    for x in range(x0 + 2, x1, 60):
        cv.vline(x, top, by, shade(wall_c, -0.1))
    cv.rect(x0 - 2, top - 4, x1 + 2, top - 1, trim)
    cv.hline(x0 - 2, x1 + 2, top - 4, shade(trim, 0.3))
    cv.hline(x0 - 2, x1 + 2, top, shade(wall_c, -0.3))
    if entrance_x is not None:
        ew, eh = 46, int(34 * s) + 2
        cv.rect(entrance_x - ew // 2 - 4, by - eh - 6, entrance_x + ew // 2 + 4, by - eh - 2, trim)
        cv.hline(entrance_x - ew // 2 - 4, entrance_x + ew // 2 + 4, by - eh - 1, shade(trim, -0.4))
        cv.rect(entrance_x - ew // 2, by - eh, entrance_x + ew // 2, by, '#6a8aa4')
        for x in range(entrance_x - ew // 2, entrance_x + ew // 2 + 1, ew // 4):
            cv.vline(x, by - eh, by, '#f0ece0')
        cv.line(entrance_x - ew // 2 + 2, by - 3, entrance_x - ew // 2 + 9, by - eh + 2, '#a8c8dc')
    if clock_x is not None:
        cv.rect(clock_x - 22, top - 26, clock_x + 22, top - 5, wall_c)
        cv.rect(clock_x - 24, top - 30, clock_x + 24, top - 27, trim)
        cv.hline(clock_x - 24, clock_x + 24, top - 30, shade(trim, 0.3))
        cv.ellipse(clock_x, top - 15, 8, 8, '#3a3a44')
        cv.ellipse(clock_x, top - 15, 7, 7, '#f8f6ee')
        cv.vline(clock_x, top - 20, top - 15, '#2a2a30')
        cv.hline(clock_x, clock_x + 4, top - 15, '#2a2a30')
    return top


def budou_gate():
    W = 640
    cv = Cv(W, 180)
    G_ = GROUND
    # 教学楼（操场对面，0.7 倍）
    school_block(cv, 20, 620, G_ - 6, floors=3, s=0.7, entrance_x=320, clock_x=320)
    cv.rect(0, G_ - 8, W - 1, G_, '#c8bc9c')                   # 操场的土地
    cv.rect(296, G_ - 8, 344, G_, '#d8d0bc')                   # 通往大门的路
    # 校内的樱花树
    for x, h, w_, sd in ((60, 108, 72, 1), (176, 100, 64, 2), (452, 104, 70, 3), (566, 98, 62, 4)):
        O.sakura(cv, x, G_ - 2, h, w_, seed=sd)
    # 围墙（1.45 m）+ 校门（门洞 286–354）
    O.block_wall(cv, 0, 276, G_, 24, '#d0cabc')
    O.block_wall(cv, 364, W - 1, G_, 24, '#d0cabc')
    for cx in (281, 359):                                       # 校门柱 2 m
        cv.rect(cx - 5, G_ - 33, cx + 5, G_, '#b4ac9c')
        cv.vline(cx - 5, G_ - 33, G_, '#ccc4b4')
        cv.vline(cx + 5, G_ - 33, G_, '#8c8474')
        cv.rect(cx - 6, G_ - 36, cx + 6, G_ - 34, '#8c8474')
        cv.rect(cx - 2, G_ - 40, cx + 2, G_ - 37, '#f4ecc0')    # 门灯
    cv.rect(277, G_ - 30, 284, G_ - 10, '#2a2a30')              # 校名牌（竖排）
    for yy in range(G_ - 28, G_ - 11, 4):
        cv.rect(279, yy, 282, yy + 1, '#e8e4d8')
    # 推到一边的铁栅门
    for x in range(366, 392, 2):
        cv.vline(x, G_ - 22, G_, '#4a4a54')
    cv.hline(366, 392, G_ - 22, '#4a4a54')
    cv.hline(366, 392, G_ - 3, '#4a4a54')
    ground_street(cv, W)
    r = K.rng(43)
    for _ in range(220):
        cv.put(int(r.randint(0, W)), int(r.randint(G_ + 2, 164)), ('#f8bcd4', '#ec98bc', '#ffe0ec')[int(r.randint(3))])
    return cv


def build_budou_gate():
    cv = budou_gate()
    K.save_layers('budou_gate', {'near': cv})
    K.update_meta('budou_gate', anchors=dict(plaque=[281, GROUND - 20]))
    return cv


# ================================================================ 便利店 supermarket（640）
def shelf_goods(cv, x0, x1, by, h=28, seed=0, c='#e8e4da', label='#e8483c'):
    """货架（1.7 m）：四层货，最上面一条价签"""
    y0 = by - h
    cv.rect(x0, y0, x1, by, c)
    cv.vline(x0, y0, by, shade(c, 0.15))
    cv.vline(x1, y0, by, shade(c, -0.3))
    cv.rect(x0, y0, x1, y0 + 2, label)
    cv.hline(x0, x1, y0, shade(label, 0.3))
    r = K.rng(seed)
    cols = ['#e04a3a', '#3a7ad0', '#f0b030', '#40a060', '#f08a30', '#8a50c0', '#f4f0e0', '#d04a8a', '#3ab0b0']
    for i in range(4):
        ya = y0 + 4 + i * 6
        cv.rect(x0 + 1, ya, x1 - 1, ya + 4, shade(c, -0.35))
        x = x0 + 1
        while x < x1 - 1:
            w_ = int(r.choice([1, 2, 2, 3]))
            hh = int(r.randint(3, 6))
            col = cols[int(r.randint(len(cols)))]
            cv.rect(x, ya + 5 - hh, min(x1 - 1, x + w_ - 1), ya + 4, col)
            if w_ >= 2:
                cv.put(x, ya + 5 - hh, shade(col, 0.35))
            x += w_ + (1 if r.rand() < 0.25 else 0)
        cv.hline(x0 + 1, x1 - 1, ya + 5, '#f4f2ea')
    K.shadow(cv, x0, x1, by + 1, 0.4, h=1)


def supermarket():
    W = 640
    cv = Cv(W, 180)
    F = 136                               # 这张图可走带从 140 起，墙脚线 136
    C = F - 50                            # 商店层高 3 m
    # ---- 上半截：天空、平屋顶、招牌
    K.sky(cv, 0, W - 1, C - 5, K.SKY_DAY)
    K.cloud(cv, 60, 30, 46, 1)
    K.cloud(cv, 410, 22, 60, 2)
    K.cloud(cv, 250, 44, 34, 3)
    for bx0, bx1, bh, col in ((70, 190, 60, '#c8ccd4'), (250, 330, 44, '#d8d0c4'), (430, 590, 70, '#bcc4cc')):
        cv.rect(bx0, C - 26 - bh, bx1, C - 26, col)        # 后面的公寓楼（远，颜色淡）
        cv.hline(bx0, bx1, C - 26 - bh, shade(col, 0.2))
        for yy in range(C - 26 - bh + 6, C - 30, 9):
            for xx in range(bx0 + 5, bx1 - 6, 10):
                cv.rect(xx, yy, xx + 5, yy + 4, shade(col, -0.25))
    for ax in (120, 470):                                   # 屋顶的空调外机
        cv.rect(ax, C - 34, ax + 12, C - 27, '#d8dce0')
        cv.ellipse(ax + 6, C - 31, 3, 3, '#8a9098')
    cv.rect(300, C - 60, 340, C - 30, '#2f8a5a')            # 屋顶的大立牌
    cv.rect(302, C - 58, 338, C - 32, '#f4f0e0')
    ptext(cv, 305, C - 55, 'OWSON', '#2f8a5a', 2, gap=1)
    cv.rect(318, C - 30, 321, C - 26, '#6a6a70')
    cv.rect(8, C - 26, W - 9, C - 5, '#f0ece0')                 # 女儿墙
    cv.hline(8, W - 9, C - 26, '#ffffff')
    cv.rect(8, C - 20, W - 9, C - 11, '#2f8a5a')                # 绿色招牌带
    cv.hline(8, W - 9, C - 20, '#44a070')
    cv.hline(8, W - 9, C - 11, '#1c5a3a')
    for sx in (40, 200, 360, 520):
        ptext(cv, sx, C - 18, 'OWSON', '#ffffff', 1, gap=1)
        cv.rect(sx - 8, C - 18, sx - 4, C - 14, '#f0c040')
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#8a8a90')
    # ---- 店内
    K.wall(cv, 11, W - 12, '#f2efe4', y0=C, y1=F, base='#a8a498')
    cv.rect(11, C + 1, W - 12, C + 4, '#fbfaf2')                # 天花灯槽
    for x in range(40, W - 20, 64):
        cv.rect(x, C + 2, x + 30, C + 3, '#ffffff')
        cv.hline(x, x + 30, C + 4, '#d8d8cc')
    K.floor_tile(cv, 0, W - 1, y0=F + 1, c1='#e9e6dc', c2='#d6d2c6', size=12)
    for x in (8, W - 11):
        K.cut_wall(cv, x, C, 179, 3, '#6a6a70')
    cv.rect(0, C, 7, 179, '#a8b0a0')
    cv.rect(W - 8, C, W - 1, 179, '#a8b0a0')
    # 入口：自动玻璃门（门洞 34 高）
    K.sliding_door(cv, 32, F, w=34, h=34, c='#cfe2ea', frame='#8a8e96', kind='glass')
    cv.rect(14, F - 40, 50, F - 37, '#2f8a5a')
    # 墙上的海报和价目
    for px_, col in ((78, '#e8a030'), (212, '#d04a4a'), (344, '#3a7ad0'), (432, '#40a060')):
        cv.rect(px_, F - 46, px_ + 12, F - 36, col)
        cv.rect(px_ + 2, F - 44, px_ + 10, F - 41, '#f8f4e4')
        cv.hline(px_ + 2, px_ + 10, F - 38, shade(col, -0.3))
    # 货架三组 + 冷柜
    shelf_goods(cv, 102, 158, F, 28, seed=1, label='#e8483c')            # 酱油
    shelf_goods(cv, 176, 232, F, 28, seed=5, label='#3a7ad0')
    shelf_goods(cv, 260, 316, F, 28, seed=2, label='#f0a030')            # 零食
    shelf_goods(cv, 366, 422, F, 28, seed=3, label='#40a060')            # 洗洁精
    # 冷柜（1.9 m 的敞口冷藏柜）：豆腐
    cv.rect(446, F - 32, 502, F, '#e4eaee')
    cv.hline(446, 502, F - 32, '#ffffff')
    cv.rect(446, F - 32, 502, F - 29, '#4aa0c8')
    for i in range(4):
        ya = F - 27 + i * 6
        cv.rect(448, ya, 500, ya + 4, '#b8d8e8')
        for x in range(449, 500, 4):
            cv.rect(x, ya + 1, x + 2, ya + 4, ('#f8f8f0', '#f4e8c0', '#e8f0f8')[(x + i) % 3])
        cv.hline(448, 500, ya + 5, '#f4f8fa')
    cv.rect(446, F - 3, 502, F, '#9aa4ac')
    # 洗手池
    K.cabinet(cv, 526, 544, F, 14, '#d8d4c8', doors=1)
    cv.rect(529, F - 15, 541, F - 14, '#8a9098')
    cv.vline(535, F - 19, F - 16, '#b8bcc4')
    cv.hline(535, 537, F - 19, '#b8bcc4')
    # 收银台（90 cm）+ 收银机 + 后面的烟柜
    K.bookshelf(cv, 590, 622, F, 34, '#b8b0a0', seed=21, rows=5)
    K.cabinet(cv, 572, 626, F, 15, '#d8c8a8', doors=3)
    cv.rect(594, F - 22, 606, F - 16, '#3a3a44')
    cv.rect(595, F - 21, 601, F - 18, '#9ad0a0')
    cv.rect(596, F - 25, 604, F - 23, '#5a5a66')
    # 购物篮
    for i in range(3):
        cv.rect(62, F - 4 - i * 3, 74, F - 2 - i * 3, '#d04040')
        cv.hline(62, 74, F - 4 - i * 3, '#e86a6a')
    return cv


def build_supermarket():
    cv = supermarket()
    K.save_layers('supermarket', {'room': cv})
    K.update_meta('supermarket', anchors=dict(sink=[535, 136]))
    return cv


# ================================================================ 东方家门口 higashikata_eve / _night / _rain（640）
def higashikata_out(var='eve'):
    W = 640
    cv = Cv(W, 180)
    G_ = GROUND
    pal = dict(eve=('#f0dcc0', '#8a4638'), night=('#e6dccb', '#7a4034'), rain=('#dcd6ca', '#6e4238'))[var]
    lit = {219, 300} if var == 'night' else set()
    # 左右的邻居
    O.house(cv, -60, 96, G_ - 2, s=0.88, wall_c=shade(pal[0], -0.05), roof_c='#3a4a44', door_x=60, win1=[14], win2=[14, 60],
            lit={14} if var == 'night' else None)
    O.house(cv, 536, 700, G_ - 2, s=0.88, wall_c=shade(pal[0], -0.03), roof_c='#4a3a34', door_x=None, win1=[604], win2=[566, 620],
            lit={620} if var == 'night' else None)
    # 东方家：大一号的两层（0.92 倍），门 376、客厅落地窗 219
    O.house(cv, 150, 470, G_ - 2, s=0.92, wall_c=pal[0], roof_c=pal[1], door_x=376, door_c='#8a5a3a', big1=[219], win1=[300, 440],
            win2=[186, 252, 318, 384, 440], lit=lit)
    # 院墙、树篱；门正对玄关
    for xa, xb, sd in ((0, 100, 1), (128, 357, 2), (395, 496, 3), (524, 585, 4)):
        if var != 'x':
            O.hedge(cv, xa + 1, xb - 1, G_ - 13, 7, seed=sd)
        O.block_wall(cv, xa, xb, G_, 13, '#cbbfa8' if var == 'eve' else '#c4c0b4')
    O.gate_post(cv, 360, G_, 23, plate='#2a2a30')
    O.gate_post(cv, 392, G_, 23)
    O.gate_iron(cv, 363, 389, G_, 17, open_=True)
    cv.rect(363, G_ - 1, 389, G_, '#a8a296')
    O.mailbox(cv, 292, G_)
    # 伞架（门柱右边）
    cv.rect(398, G_ - 6, 403, G_, '#5a5a62')
    cv.vline(399, G_ - 15, G_ - 6, '#2a3660')
    cv.vline(402, G_ - 13, G_ - 6, '#8a2a2a')
    cv.put(399, G_ - 16, '#c8a060')
    # 巷口（路口 600）：左右两段墙之间留出一条往里的小路
    cv.rect(586, G_ - 40, 640, G_, mix(pal[0], '#7a8088', 0.6))
    K.dither(cv, 586, G_ - 44, 640, G_ - 41, mix(pal[0], '#7a8088', 0.6), 0.5)
    cv.rect(586, G_ - 6, 640, G_, '#8a8a8e')
    O.block_wall(cv, 622, 640, G_, 13, '#c4c0b4')
    O.sign_post(cv, 610, G_, 40, 'stop')
    # 电线杆、路灯
    p1 = O.pole(cv, 116, G_)
    p2 = O.pole(cv, 510, G_)
    O.wires(cv, p1, p2, sag=7)
    O.wires(cv, [(-40, 12), (-40, 22)], [p1[0], p1[4]], sag=4)
    O.wires(cv, [p2[3], p2[5]], [(W + 40, 12), (W + 40, 22)], sag=4)
    lamp = O.street_lamp(cv, 474, G_, 76, on=(var == 'night'), side=1)
    c1, c2 = dict(eve=('#c8b8a4', '#5c4c50'), night=('#b9b5ad', '#4c4c54'), rain=('#a8a8a8', '#44464e'))[var]
    ground_street(cv, W, c1, c2)
    if var == 'rain':
        r = K.rng(8)
        for (px_, py_, pw) in ((250, 168, 30), (120, 158, 14), (450, 172, 18), (560, 160, 12)):
            cv.ellipse(px_, py_, pw / 2, 3, '#6a7890')
            cv.hline(int(px_ - pw / 2 + 3), int(px_ + pw / 2 - 5), py_ - 1, '#9aa8c0')
        for _ in range(140):
            x, y = int(r.randint(0, W)), int(r.randint(G_ + 2, 179))
            cv.put(x, y, '#c0c8d8')
    if var == 'night':
        night_tint(cv, 0.42, keep=('#f6d98a', shade('#f6d98a', 0.3), '#fff2b0'))
    elif var == 'rain':
        night_tint(cv, 0.78, tint=(0.92, 0.96, 1.04))
    elif var == 'eve':
        night_tint(cv, 0.96, tint=(1.06, 0.96, 0.9))
    return cv, lamp


def night_tint(cv, k, tint=(0.8, 0.86, 1.2), keep=()):
    """整张压暗 / 偏色；keep 里的颜色（亮着的窗、灯）不动"""
    a = cv.a
    op = a[..., 3] > 0
    mask = op.copy()
    for c in keep:
        r, g, b, _ = rgba(c)
        mask &= ~((a[..., 0] == r) & (a[..., 1] == g) & (a[..., 2] == b))
    f = a[..., :3].astype(float)
    for i in range(3):
        f[..., i] = np.clip(f[..., i] * k * tint[i], 0, 255)
    a[..., :3][mask] = f[mask].astype(np.uint8)


def glow_layer(w, spots, h=180):
    """夜景的光晕（lighter 混合）：spots = [(x, y, 半径, 颜色, 强度)]，由里到外抖动衰减"""
    cv = Cv(w, h)
    acc = np.zeros((h, w), float)
    col0 = None
    yy, xx = np.mgrid[0:h, 0:w]
    for (x, y, rad, col, k) in spots:
        d = np.sqrt((xx - x) ** 2 + ((yy - y) * 1.15) ** 2) / rad
        f = np.clip(1 - d, 0, 1) ** 1.6 * k
        acc += f
        col0 = col0 or col
    # 量化成 6 档，带一点抖动，免得出现平滑渐变（像素风）
    lv = 7
    q = np.clip(np.floor(acc * lv + K.BAYER[yy % 4, xx % 4] * 0.9) / lv, 0, 1)
    r, g, b, _ = rgba(col0 or '#ffe9a0')
    for i, v in enumerate((r, g, b)):
        cv.a[..., i] = (q * v).astype(np.uint8)
    cv.a[..., 3] = np.where(q > 0, 255, 0).astype(np.uint8)
    return cv


def build_higashikata(var):
    def fn():
        cv, lamp = higashikata_out(var)
        layers = {'near': cv}
        if var == 'night':
            S_ = 0.92
            layers['glow'] = glow_layer(640, [(lamp[0], lamp[1] + 4, 40, '#ffe9a0', 0.5), (lamp[0], 152, 56, '#ffe9a0', 0.3),
                                              (219, GROUND - 22, 30, '#f6d98a', 0.3), (300, GROUND - 28, 18, '#f6d98a', 0.22)])
        key = 'higashikata_' + var
        K.save_layers(key, layers)
        K.update_meta(key, anchors=dict(door=[376, 146], window=[219, GROUND - 22], lamp=[lamp[0], lamp[1]], gate=[376, 148]))
        return cv
    return fn


# ================================================================ 海边的路 angelo_rain / angelo_after（1280）
def pine(cv, x, by, h=90, seed=0):
    """海边的松树（旧部件，按新高度调用）"""
    OB = K.old_lib()
    im = OB.pine(cv.img(), x, by, h=h, seed=seed)
    cv.a = np.array(im)


def angelo_road(after=False):
    W = 1280
    cv = Cv(W, 180)
    G_ = GROUND
    sea = ('#5a86b0', '#7aa6cc') if after else ('#5a6e84', '#7688a0')
    # 海（护栏后面）
    cv.rect(0, G_ - 30, W - 1, G_, sea[0])
    for x in range(0, W, 9):
        y = G_ - 26 + (x // 9) % 5 * 5
        cv.hline(x, x + 5, y, sea[1])
    # 松树
    for x, h, sd in ((150, 104, 1), (470, 96, 2), (760, 108, 3), (1180, 100, 4)):
        pine(cv, x, G_ - 1, h, sd)
    # 防波堤矮墙（60 cm）+ 护栏（1.1 m）
    cv.rect(0, G_ - 9, W - 1, G_, '#b0aca4' if after else '#8e8e92')
    cv.hline(0, W - 1, G_ - 9, '#d0ccc4' if after else '#a8a8ac')
    cv.hline(0, W - 1, G_, '#6e6a66')
    rc = '#e8e8ec' if after else '#b8bcc4'
    cv.hline(0, W - 1, G_ - 18, rc)
    cv.hline(0, W - 1, G_ - 14, shade(rc, -0.15))
    for x in range(6, W, 16):
        cv.vline(x, G_ - 18, G_ - 9, rc)
    # 电线杆 + 路灯
    xs = [90, 380, 690, 1010, 1250]
    pts = [O.pole(cv, x, G_) for x in xs]
    for a, b in zip(pts[:-1], pts[1:]):
        O.wires(cv, a, b, sag=8)
    for x in (240, 560, 860):
        O.street_lamp(cv, x, G_, 76, side=1)
    # 电话亭（2.2 m）
    bx = 599
    cv.rect(bx - 8, G_ - 37, bx + 8, G_, '#d8dce0')
    cv.rect(bx - 9, G_ - 39, bx + 9, G_ - 37, '#3a8a5a')
    cv.rect(bx - 6, G_ - 34, bx + 6, G_ - 6, '#a8ccdc')
    cv.line(bx - 5, G_ - 10, bx + 2, G_ - 33, '#d0e6f0')
    cv.rect(bx - 2, G_ - 24, bx + 3, G_ - 16, '#4a8a5a')        # 绿色公用电话
    cv.vline(bx - 8, G_ - 37, G_, '#f0f2f4')
    cv.vline(bx + 8, G_ - 37, G_, '#9aa0a8')
    cv.vline(bx, G_ - 34, G_ - 6, '#d8dce0')
    # 售货机、停车让行牌、公交站牌
    O.vending(cv, 937, G_, '#3a6ab8', seed=5)
    O.sign_post(cv, 990, G_, 40, 'stop')
    O.sign_post(cv, 318, G_, 40, 'bus')
    # 长椅
    cv.rect(700, G_ - 6, 730, G_ - 5, '#b08a5a')
    cv.hline(700, 730, G_ - 4, '#7a5a38')
    cv.rect(700, G_ - 13, 730, G_ - 11, '#b08a5a')
    for x in (703, 727):
        cv.vline(x, G_ - 13, G_, '#5a5a62')
    c1, c2 = ('#b9b5ad', '#4c4c54') if after else ('#9a9a9e', '#3e4048')
    ground_street(cv, W, c1, c2)
    r = K.rng(12)
    puddles = ((420, 172, 34), (180, 160, 14), (640, 158, 18), (880, 170, 22), (1120, 162, 16))
    for (px_, py_, pw) in puddles if not after else puddles[:3]:
        cv.ellipse(px_, py_, pw / 2, 3, '#7a94b8' if after else '#5c6c84')
        cv.hline(int(px_ - pw / 2 + 3), int(px_ + pw / 2 - 5), py_ - 1, '#c8dcf0' if after else '#8a98b0')
    if not after:
        for _ in range(300):
            cv.put(int(r.randint(0, W)), int(r.randint(G_ + 2, 179)), '#b8c0d0')
        night_tint(cv, 0.8, tint=(0.92, 0.96, 1.04))
    return cv


def build_angelo(after):
    def fn():
        cv = angelo_road(after)
        key = 'angelo_after' if after else 'angelo_rain'
        K.save_layers(key, {'near': cv})
        K.update_meta(key, anchors=dict(booth=[599, GROUND], vending=[937, GROUND], stop=[990, GROUND]))
        return cv
    return fn


BUILD = {
    'higashikata_living': build_higashikata_living,
    'morioh_road': build_morioh_road,
    'budou_gate': build_budou_gate,
    'supermarket': build_supermarket,
    'higashikata_eve': build_higashikata('eve'),
    'higashikata_night': build_higashikata('night'),
    'higashikata_rain': build_higashikata('rain'),
    'angelo_rain': build_angelo(False),
    'angelo_after': build_angelo(True),
}


def check_image(key, cv, out):
    """比例核对图：新近景叠在旧远景上，再贴几个人物"""
    from PIL import Image
    import json
    import glob
    import cast_pro
    from rig import OX, OY
    spec = {}
    for fp in glob.glob(os.path.join(K.META, 'bg*.json')):
        spec.update(json.load(open(fp, encoding='utf-8')))
    spec = spec[key]
    w = spec.get('w', cv.w)
    im = Image.new('RGBA', (w, 180), (20, 20, 30, 255))
    for L in spec['layers']:
        if L['type'] not in ('pano', 'static', 'image', 'glow') or not L.get('image') or L.get('key'):
            continue
        a = Image.open(os.path.join(K.ASSETS, L['image'] + '.png')).convert('RGBA')
        k = L.get('k', 1)
        if L['type'] == 'glow':
            import numpy as _np
            b = _np.array(im).astype(int)
            g = _np.array(a).astype(int)
            hh, ww = min(b.shape[0], g.shape[0]), min(b.shape[1], g.shape[1])
            b[:hh, :ww, :3] = _np.clip(b[:hh, :ww, :3] + g[:hh, :ww, :3], 0, 255)
            im = Image.fromarray(b.astype('uint8'), 'RGBA')
        elif k != 1:
            for sx in range(0, w, 320):
                cam = min(sx, w - 320)
                off = int(cam * k)
                im.alpha_composite(a.crop((off, 0, min(a.width, off + 320), 180)), (cam, 0))
        else:
            im.alpha_composite(a, (L.get('x', 0), L.get('y', 0)))
    n = max(5, w // 110)
    ids = ['josuke', 'jotaro4', 'koichi', 'tomoko', 'kid', 'ryohei', 'fan_a', 'thug_a', 'angelo', 'clerk', 'robber', 'flirt']
    for i in range(n):
        f = cast_pro.build(ids[i % len(ids)]).rows[0][1][0].img()
        x = int((i + 0.5) * w / n)
        y = 148 + (i % 3) * 8
        im.alpha_composite(f, (x - OX, y - OY - 1))
    k = 3 if w <= 640 else 2
    im.resize((w * k, 180 * k), Image.NEAREST).save('%s/bg_%s.png' % (out, key))


if __name__ == '__main__':
    out = sys.argv[1]
    for key in (sys.argv[2:] or list(BUILD)):
        cv = BUILD[key]()
        check_image(key, cv, out)
        print(key, cv.w)
