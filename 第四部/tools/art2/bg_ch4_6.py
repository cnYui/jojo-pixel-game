# 第四部重画：第 4–6 章的室内（房间内景）+ 港口集装箱。
#   画法同 bg_ch1_3.py：镜头在房间里（天花、后墙、地板），家具和门窗按 第四部/docs/比例标准.md。
#   地面上的东西 x 不动（剧情和战斗里写死了坐标），只改高度；改了高度的锚点在各 build_* 里一起更新。
#   用法：python bg_ch4_6.py <核对图输出目录> [背景键…]
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from px import Cv, mix, shade, rgba  # noqa: E402
import bgkit as K  # noqa: E402
import bgout as O  # noqa: E402
import bgin2 as I  # noqa: E402
import bgroom as R  # noqa: E402
import bg_pro as P  # noqa: E402
from bgkit import FLOOR  # noqa: E402
from bgout import GROUND  # noqa: E402
from pfont import ptext  # noqa: E402
from bg_pro import night_tint  # noqa: E402

F = FLOOR


def edit_meta(key, fn):
    """直接改一张背景的元数据条目（K.update_meta 管不到的：pick 图层的位置、加前景层）"""
    for fp in sorted(glob.glob(os.path.join(K.META, 'bg*.json'))):
        with open(fp, encoding='utf-8') as fh:
            d = json.load(fh)
        if key not in d:
            continue
        fn(d[key])
        with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        return
    raise KeyError(key)


def clip(fn):
    """窗外景画在小画布上再贴回去：椭圆之类不会画出窗框"""
    def view(cv, x0, y0, x1, y1):
        t = Cv(x1 - x0 + 1, y1 - y0 + 1)
        fn(t, 0, 0, x1 - x0, y1 - y0)
        cv.blit(t, x0, y0)
    return view


def tube_lights(cv, W, C, step=90, x0=30):
    """天花上的日光灯（近的一排宽、远的一排窄）"""
    for x in range(x0, W, step):
        cv.rect(x, C - 10, x + 30, C - 9, '#ffffff')
        cv.hline(x, x + 30, C - 8, '#d0ccbc')
        cv.rect(x - 8, C - 36, x + 40, C - 34, '#ffffff')
        cv.hline(x - 8, x + 40, C - 33, '#d0ccbc')


# ================================================================ 东方家夜里的客厅 higashikata_tvnight（480）
def tv_frames():
    """电视里的横版游戏（4 帧，12 × 10）和没信号的雪花（6 帧）"""
    w, h = 12, 10
    scr = Cv(w * 4, h)
    for f in range(4):
        ox = f * w
        scr.rect(ox, 0, ox + w - 1, 6, '#5a9ae8')
        scr.rect(ox, 7, ox + w - 1, 7, '#4aa04a')
        scr.rect(ox, 8, ox + w - 1, 9, '#b8703a')
        scr.rect(ox + 8, 2, ox + 9, 3, '#f0c040')
        scr.hline(ox + 1 + f % 2, ox + 3 + f % 2, 1, '#ffffff')
        px_ = ox + 2 + f * 2
        jy = (0, 1, 2, 1)[f]
        scr.rect(px_, 5 - jy, px_ + 1, 6 - jy, '#e03a3a')
        scr.put(px_, 4 - jy, '#f8d0a0')
    snow = Cv(w * 6, h)
    r = K.rng(31)
    for f in range(6):
        for y in range(h):
            for x in range(w):
                v = int(r.choice([36, 84, 140, 200, 246]))
                snow.a[y, f * w + x] = (v, v, min(255, v + 6), 255)
    return scr, snow


def build_higashikata_tvnight():
    lit, s = P.higashikata_living('night', ret_screen=True)
    # 电视前地上的游戏机和手柄
    lit.rect(300, 146, 309, 148, '#c8c8d0')
    lit.hline(300, 309, 146, '#ececf2')
    lit.hline(302, 305, 147, '#5a5a66')
    lit.put(308, 147, '#d04040')
    lit.line(309, 146, 315, 140, '#3a3a44')
    lit.line(300, 148, 296, 155, '#3a3a44')
    lit.rect(291, 156, 296, 158, '#b8b8c4')
    lit.put(292, 157, '#3a3a44')
    lit.put(295, 157, '#d04040')
    lit.rect(s[0], s[1], s[2], s[3], '#0a0c14')
    room = lit.copy()
    night_tint(room, 0.42, tint=(0.72, 0.82, 1.32))
    glow = I.shafts(480, spots=[(323, 123, 30, 22, 0.42), (316, 152, 54, 12, 0.2)], col='#8ab4ff', k=0.3)
    scr, snow = tv_frames()
    K.save_layers('higashikata_tvnight', dict(room=room, glow=glow, lit=lit, screen=scr, snow=snow))
    box = dict(x=s[0], y=s[1], w=12, h=10)
    K.update_meta('higashikata_tvnight',
                  anchors=dict(tv=[323, 122], socket=[289, F - 5], photo=[229, F - 28], window=[98, F - 19], switch=[146, F - 21],
                               console=[304, 147], pad=[293, 157]),
                  layers={'screen': box, 'snow': box})
    return room


# ================================================================ 露伴的工作室 rohan_studio（480）
def hills_view(cv, x0, y0, x1, y1):
    K.vgrad(cv, x0, y0, x1, y1, ['#7ab4ee', '#a8d2f4', '#d4eaf8'])
    for cx_, w_ in ((x0 + 16, 7), (x0 + 58, 9), (x1 - 22, 8)):
        cv.ellipse(cx_, y0 + 6, w_, 2.5, '#ffffff')
        cv.ellipse(cx_ + 4, y0 + 4, w_ * 0.6, 2.5, '#ffffff')
    for i, x in enumerate(range(x0 - 6, x1 + 10, 17)):
        cv.ellipse(x + 6, y1 - 1, 12, 6 + (i % 3) * 2, ('#5a9a5a', '#4a8a4e', '#6aa862')[i % 3])
    cv.rect(x0, y1 - 2, x1, y1, '#3e7a44')


def manga_page(cv, x, y, w=7, h=9):
    """一页原稿：白纸 + 几格分镜"""
    cv.rect(x, y, x + w - 1, y + h - 1, '#f8f6ee')
    cv.rect(x + 1, y + 1, x + w - 2, y + h // 2 - 1, '#f8f6ee')
    for (a, b, c, d) in ((1, 1, w - 2, h // 2 - 1), (1, h // 2 + 1, w // 2 - 1, h - 2), (w // 2 + 1, h // 2 + 1, w - 2, h - 2)):
        cv.hline(x + a, x + c, y + b, '#3a3a44')
        cv.hline(x + a, x + c, y + d, '#3a3a44')
        cv.vline(x + a, y + b, y + d, '#3a3a44')
        cv.vline(x + c, y + b, y + d, '#3a3a44')


def rohan_studio():
    W = 480
    cv = Cv(W, 180)
    R.ceiling(cv, 0, W - 1, c='#efe8d8', beam='#4a3020')
    R.back_wall(cv, 0, W - 1, '#f2ead8', wains=(13, '#5a3c28'), base='#3a2618', rail_c='#4a3020', upper='#ece2cc')
    K.floor_wood(cv, 0, W - 1, c='#b88850')
    R.side_wall(cv, 0, 7, '#f2ead8', left=True)
    R.side_wall(cv, 472, W - 1, '#f2ead8', left=False)
    K.door(cv, 26, F, c='#6a4028', frame='#3a2618')
    # 两架顶到挂镜线下面的书
    K.bookshelf(cv, 50, 96, F, 40, '#5a3a24', seed=5)
    K.bookshelf(cv, 100, 146, F, 40, '#5a3a24', seed=9)
    # 一排大窗（窗台 84 cm）
    K.window(cv, 170, F - 42, 294, F - 14, frame='#f4f0e4', nx=4, view=clip(hills_view), curtain='#2e5a44', rod='#4a3020')
    # 画桌：桌面 11，斜的画板、台灯、墨水
    K.table(cv, 234, F, w=62, h=11, c='#b08450')
    cv.rect(248, F - 8, 262, F - 1, '#9a7040')                       # 抽屉
    cv.hline(248, 262, F - 5, '#6a4a28')
    cv.rect(254, F - 7, 256, F - 7, '#e8c860')
    cv.rect(254, F - 3, 256, F - 3, '#e8c860')
    for i in range(11):                                              # 斜画板
        cv.hline(220 + i // 3, 250 - i // 3, F - 12 - i, '#f4f0e4' if i < 10 else '#c8c0a8')
    cv.hline(220, 250, F - 12, '#8a6a44')
    manga_page(cv, 226, F - 21, 8, 8)
    manga_page(cv, 237, F - 21, 8, 8)
    cv.rect(198, F - 13, 203, F - 12, '#2a3a30')                     # 台灯
    cv.line(200, F - 13, 204, F - 21, '#2a3a30')
    cv.line(204, F - 21, 210, F - 24, '#2a3a30')
    cv.rect(208, F - 25, 214, F - 23, '#2e6a4a')
    cv.hline(209, 213, F - 22, '#fff4c0')
    for x, col in ((256, '#1a1a20'), (260, '#1a1a20')):              # 墨水瓶
        cv.rect(x, F - 15, x + 2, F - 12, col)
        cv.put(x + 1, F - 16, '#8a8a90')
    cv.rect(266, F - 16, 269, F - 12, '#8a3a2a')                     # 笔筒
    cv.vline(266, F - 19, F - 17, '#e8e0c0')
    cv.vline(268, F - 20, F - 17, '#3a3a44')
    # 转椅（坐面 5）
    cv.rect(230, 132, 242, 141, '#3a3a44')
    cv.hline(230, 242, 132, '#5a5a66')
    cv.vline(242, 132, 141, '#2a2a30')
    cv.rect(229, 142, 243, 143, '#4a4a54')
    cv.hline(229, 243, 144, '#2a2a30')
    cv.vline(236, 145, 147, '#8a8e96')
    cv.hline(231, 241, 148, '#6a6e76')
    cv.put(231, 149, '#2a2a30')
    cv.put(241, 149, '#2a2a30')
    cv.put(236, 149, '#2a2a30')
    # 软木板上钉着的原稿
    cv.rect(314, F - 43, 358, F - 18, '#8a5a34')
    cv.rect(316, F - 41, 356, F - 20, '#c8a06a')
    K.dither(cv, 316, F - 41, 356, F - 20, '#b8905a', 0.3)
    for (x, y) in ((318, F - 40), (328, F - 39), (338, F - 40), (348, F - 39), (320, F - 30), (332, F - 29), (344, F - 30)):
        manga_page(cv, x, y, 7, 9)
        cv.put(x + 3, y, '#d04040')
    # 放原稿的抽屉柜 + 成摞的稿纸
    K.cabinet(cv, 374, 418, F, 15, '#6a4a2c', drawers=3, handles='#e8c860')
    for x, n in ((377, 3), (391, 4), (405, 2)):
        for j in range(n):
            cv.rect(x, F - 17 - j, x + 10, F - 17 - j, '#f8f6ee' if j % 2 == 0 else '#d8d4c8')
    # 石膏像 + 上面的风景画
    cv.rect(442, F - 16, 454, F, '#e8e4dc')
    cv.vline(454, F - 16, F, '#b8b4a8')
    cv.hline(441, 455, F - 16, '#f8f6f0')
    cv.rect(444, F - 20, 452, F - 17, '#f0ece4')
    cv.ellipse(448, F - 24, 3.4, 3.8, '#f4f0e8')
    cv.vline(451, F - 26, F - 21, '#c8c4b8')
    K.picture(cv, 449, F - 37, 22, 12, '#b8923a', ('#a8cce8', '#5a8a5a', '#e8e0c0'))
    R.pendant(cv, 120, drop=16, w=10, c='#f8f0c8')
    R.pendant(cv, 340, drop=16, w=10, c='#f8f0c8')
    return cv


def studio_hole():
    """墙上被打穿的洞（柜子上面）+ 地上的碎块"""
    cv = Cv(480, 180)
    r = K.rng(7)
    cx, cy = 398, F - 32
    for i in range(14):                                              # 裂缝
        ang = i * 0.45 + r.uniform(-0.1, 0.1)
        ln = r.uniform(11, 16)
        cv.line(cx + np.cos(ang) * 7, cy + np.sin(ang) * 5, cx + np.cos(ang) * ln, cy + np.sin(ang) * ln * 0.75, '#8a7a60')
    cv.ellipse(cx, cy, 10, 7.5, '#d8ccb0')
    for i in range(10):
        ang = i * 0.63
        cv.ellipse(cx + np.cos(ang) * 8, cy + np.sin(ang) * 6, 2.6, 2.2, '#d8ccb0')
    cv.ellipse(cx, cy, 8.4, 6, '#241814')
    for i in range(9):
        ang = i * 0.7 + 0.3
        cv.ellipse(cx + np.cos(ang) * 7, cy + np.sin(ang) * 5, 2, 1.6, '#241814')
    for x in (cx - 5, cx - 1, cx + 4):                               # 露出来的木板条
        cv.vline(x, cy - 5, cy + 4, '#6a4a30')
    cv.hline(cx - 6, cx + 6, cy + 1, '#4a3220')
    for _ in range(26):                                              # 碎块
        x, y = int(r.uniform(382, 418)), int(r.uniform(140, 147))
        c = r.choice(['#d8ccb0', '#b8a888', '#f2ead8'])
        cv.rect(x, y, x + int(r.randint(0, 3)), y + int(r.randint(0, 2)), c)
    for _ in range(8):
        cv.put(int(r.uniform(376, 424)), int(r.uniform(146, 152)), '#c8bc9c')
    return cv


def studio_pages():
    """被翻出来撒了一地的原稿"""
    cv = Cv(480, 180)
    r = K.rng(12)
    for _ in range(34):
        x, y = int(r.uniform(84, 462)), int(r.uniform(142, 174))
        w = 6 + (y - 140) // 14
        sk = int(r.choice([-2, -1, 1, 2]))
        for j in range(3):
            cv.hline(x + sk * j // 2, x + w + sk * j // 2, y + j, '#f8f6ee')
        cv.hline(x + sk, x + w + sk, y + 3, '#c8c4b4')
        cv.hline(x + 1, x + w // 2, y + 1, '#3a3a44')
        cv.put(x + w - 1, y + 1, '#3a3a44')
    return cv


def build_rohan_studio():
    cv = rohan_studio()
    glow = I.shafts(480, [[(176, F + 1), (290, F + 1), (336, 178), (200, 178)]], col='#fff0c8', k=0.09)
    K.save_layers('rohan_studio', dict(room=cv, hole=studio_hole(), glow=glow, pages=studio_pages()))
    K.update_meta('rohan_studio',
                  anchors=dict(door=[26, 148], door_in=[26, 140], window_l=[201, F - 28], window_r=[263, F - 28], chair=[236, 148],
                               lamp=[205, F - 22], board=[336, F - 30], manuscripts=[396, F - 18], painting=[449, F - 37],
                               hole=[398, F - 32], rubble=[400, 142]))
    return cv


# ================================================================ 牧场的屋里 farmhouse（480）
def field_view(cv, x0, y0, x1, y1):
    K.vgrad(cv, x0, y0, x1, y1, ['#8cc0f0', '#c4e0f6'])
    cv.rect(x0, y1 - 7, x1, y1, '#8ab860')
    cv.ellipse(x1 - 12, y1 - 8, 9, 4, '#5a9a4a')
    cv.vline(x1 - 12, y1 - 6, y1 - 3, '#5a4030')
    for x in range(x0 + 2, x1, 6):
        cv.vline(x, y1 - 9, y1 - 6, '#c8b890')
    cv.hline(x0, x1, y1 - 8, '#c8b890')


def farmhouse():
    W = 480
    cv = Cv(W, 180)
    C = R.CL
    R.ceiling(cv, 0, W - 1, c='#9a7a54', beam='#5a4028')
    wc = '#b08a60'
    cv.rect(0, C + 2, W - 1, F, wc)                                  # 竖木板墙
    for i, x in enumerate(range(3, W, 7)):
        cv.vline(x, C + 2, F, shade(wc, -0.18))
        if i % 3 == 0:
            cv.vline(x + 1, C + 2, F, shade(wc, 0.08))
    r = K.rng(4)
    for _ in range(46):
        x, y = int(r.uniform(4, W - 4)), int(r.uniform(C + 6, F - 4))
        cv.put(x, y, shade(wc, -0.3))
        cv.put(x, y + 1, shade(wc, -0.14))
    cv.rect(0, R.RAIL, W - 1, R.RAIL + 1, '#6a4a2c')                 # 横梁
    cv.hline(0, W - 1, R.RAIL, '#8a6a44')
    cv.hline(0, W - 1, R.RAIL + 2, shade(wc, -0.3))
    cv.rect(0, F - 1, W - 1, F, '#5a4028')
    K.dither(cv, 0, C + 2, W - 1, C + 4, shade(wc, -0.35), 0.5)
    K.floor_wood(cv, 0, W - 1, c='#a8845a', seed=8)
    R.side_wall(cv, 0, 7, wc, left=True)
    R.side_wall(cv, 472, W - 1, wc, left=False)
    # 后门（上半是玻璃格）
    K.door(cv, 26, F, c='#9a6e44', frame='#5a4028', glass='#c8e0d0')
    cv.vline(26, F - 30, F - 21, '#9a6e44')
    cv.hline(21, 31, F - 26, '#9a6e44')
    # 水槽上面的窗 + 红白格的窗幔
    K.window(cv, 56, F - 39, 104, F - 19, frame='#f0e8d8', nx=2, view=clip(field_view))
    for i, x in enumerate(range(55, 106, 3)):
        cv.rect(x, F - 41, min(105, x + 2), F - 37, '#d04a40' if i % 2 == 0 else '#f4f0e8')
    cv.hline(55, 105, F - 42, '#7a5a3c')
    for x, col in ((62, '#6aa87a'), (70, '#c8a050'), (92, '#e8e4d8')):   # 窗台上的瓶子
        cv.rect(x, F - 23, x + 2, F - 20, col)
        cv.put(x + 1, F - 24, shade(col, -0.2))
    K.wall_cabinet(cv, 112, 146, F - 42, F - 26, '#b89468')
    K.kitchen_counter(cv, 46, 150, F, '#d8ccb0', sink_x=78)
    cv.rect(124, F - 18, 132, F - 15, '#7a8a9a')                     # 台面上的锅
    cv.hline(123, 133, F - 18, '#9aaaba')
    # 煤气灶（灶面 14）+ 烟罩
    cv.rect(154, F - 14, 188, F, '#f0f0ec')
    cv.rect(154, F - 15, 188, F - 14, '#3a3a44')
    cv.vline(188, F - 13, F, '#c8c8c0')
    cv.rect(158, F - 10, 184, F - 3, '#2a2a30')
    cv.rect(160, F - 8, 182, F - 5, '#4a4a54')
    cv.hline(160, 182, F - 11, '#b8bcc4')
    for x in (158, 164, 178, 184):
        cv.put(x, F - 13, '#3a3a44')
    cv.rect(160, F - 37, 182, F - 34, '#c8ccd0')
    cv.rect(156, F - 34, 186, F - 31, '#b0b4b8')
    cv.hline(156, 186, F - 31, '#7a7e86')
    # 碗柜（上半玻璃门，里面摞着盘子）
    cv.rect(196, F - 36, 230, F, '#8a6240')
    cv.hline(196, 230, F - 36, '#aa8260')
    cv.vline(230, F - 36, F, '#6a4a2c')
    for a, b in ((198, 212), (214, 228)):
        cv.rect(a, F - 34, b, F - 17, '#d8e4e0')
        for yy in (F - 29, F - 23, F - 18):
            cv.hline(a, b, yy, '#8a6240')
            for x in range(a + 2, b - 2, 4):
                cv.rect(x, yy - 3, x + 2, yy - 1, '#f8f8f4')
        cv.rect(a, F - 14, b, F - 2, shade('#8a6240', -0.1))
        cv.hline(a, b, F - 14, '#6a4a2c')
    cv.put(211, F - 8, '#e8c860')
    cv.put(215, F - 8, '#e8c860')
    # 老式圆角冰箱（174 cm）
    cv.rect(249, F - 29, 267, F, '#f0ead8')
    cv.put(249, F - 29, wc)
    cv.put(267, F - 29, wc)
    cv.hline(250, 266, F - 29, '#fffcf0')
    cv.vline(267, F - 28, F, '#c8c0a8')
    cv.hline(249, 267, F - 19, '#b8b0a0')
    cv.vline(251, F - 26, F - 22, '#8a8a90')
    cv.vline(251, F - 16, F - 10, '#8a8a90')
    cv.rect(257, F - 15, 261, F - 11, '#f8f8f0')
    cv.rect(249, F - 1, 267, F, '#3a3a40')                           # 冰箱底下的缝
    # 墙上：日历、钟、草帽、黄雨衣
    K.calendar(cv, 286, F - 32)
    K.clock(cv, 318, F - 36, 3)
    cv.ellipse(398, F - 31, 7, 2, '#e8c878')
    cv.ellipse(398, F - 33, 4, 2.6, '#e8c878')
    cv.hline(395, 401, F - 32, '#c04030')
    cv.put(398, F - 37, '#5a4028')
    cv.put(440, F - 41, '#5a4028')                                   # 挂钩上的雨衣
    for i in range(22):
        w_ = 3 + i // 4
        cv.hline(440 - w_, 440 + w_, F - 40 + i, '#e8c020')
    cv.vline(440, F - 38, F - 19, '#c8a010')
    cv.rect(437, F - 41, 443, F - 38, '#d8b018')
    # 柴箱
    cv.rect(426, F - 9, 464, F, '#7a5434')
    cv.hline(426, 464, F - 9, '#9a7450')
    cv.vline(464, F - 9, F, '#5a3c24')
    for x in range(430, 462, 7):
        cv.ellipse(x, F - 12, 3, 2.6, '#c8a070')
        cv.ellipse(x, F - 12, 1.4, 1.2, '#a88050')
    # 桌子上面的吊灯
    R.pendant(cv, 340, drop=30, w=10, c='#2e6a4a')
    # 餐桌（落在可走带上，y = 150）、椅子、倒下的椅子
    K.chair(cv, 299, 152, c='#6a4a2c', face=1)
    K.chair(cv, 381, 152, c='#6a4a2c', face=-1)
    I.dining_table(cv, 340, 150, w=60)
    cv.rect(332, 136, 336, 138, '#f8f8f4')                           # 杯子、盘子
    cv.hline(346, 354, 138, '#e8e8e0')
    cv.hline(402, 416, 157, '#6a4a2c')                               # 倒下的椅子
    cv.hline(402, 416, 158, '#4a3220')
    cv.vline(403, 152, 157, '#6a4a2c')
    cv.vline(410, 152, 157, '#6a4a2c')
    cv.line(416, 157, 422, 153, '#6a4a2c')
    cv.line(416, 158, 423, 158, '#7a5a38')
    return cv


def build_farmhouse():
    cv = farmhouse()
    pan = Cv(18, 5)
    pan.rect(0, 2, 9, 4, '#2a2a30')
    pan.hline(0, 9, 1, '#4a4a54')
    pan.hline(10, 17, 2, '#2a2a30')
    pan.put(17, 2, '#8a6a44')
    glow = I.shafts(480, [[(58, F + 1), (102, F + 1), (150, 178), (60, 178)]], col='#ffe0a0', k=0.09)
    K.save_layers('farmhouse', dict(room=cv, pan=pan, pan_none=Cv(18, 5), glow=glow))

    def fix(e):
        for L in e['layers']:
            if L.get('key') == 'pan':
                L.update(x=162, y=F - 20)
    edit_meta('farmhouse', fix)
    K.update_meta('farmhouse',
                  anchors=dict(back_door=[26, 148], window=[80, F - 29], sink=[78, 146], pan=[168, F - 18], under_fridge=[258, F - 1],
                               under_table=[340, 146], chair_l=[299, 152], chair_r=[381, 152], raincoat=[440, F - 30]))
    return cv


# ================================================================ 葡萄丘银行 budogaoka_bank（320）
BANK_F = 136                              # 这张图可走带从 140 起
BANK_C = 62


def budogaoka_bank():
    W = 320
    cv = Cv(W, 180)
    Fb, C = BANK_F, BANK_C
    R.ceiling(cv, 0, W - 1, cl=C, c='#f2f0e8', boards=False)
    tube_lights(cv, W, C, step=96, x0=26)
    R.back_wall(cv, 0, W - 1, '#f0ece0', cl=C, rail=Fb - 47, upper='#ece8dc', rail_c='#c8c4b4', base='#a8a498', floor=Fb,
                wains=(13, '#b89468'))
    # 行招：绿底 + 葡萄
    cv.rect(178, C + 6, 312, C + 21, '#1f6a4a')
    cv.hline(178, 312, C + 6, '#3a8a66')
    cv.hline(178, 312, C + 21, '#0f4a32')
    for (dx, dy) in ((0, 0), (3, 0), (6, 0), (1, 3), (4, 3), (3, 6)):
        cv.rect(186 + dx, C + 10 + dy, 187 + dx, C + 11 + dy, '#a070d0')
    cv.put(190, C + 8, '#6ab060')
    K.text(cv, 200, C + 7, '葡萄丘银行', '#f4f0d8', 12)
    K.floor_tile(cv, 0, W - 1, y0=Fb + 1, c1='#e8e2d2', c2='#d8d0bc', size=14)
    R.side_wall(cv, 0, 7, '#f0ece0', cl=C, left=True, floor=Fb)
    R.side_wall(cv, W - 8, W - 1, '#f0ece0', cl=C, left=False, floor=Fb)
    # 自动玻璃门
    K.sliding_door(cv, 31, Fb, w=34, h=34, c='#cfe2ea', frame='#8a8e96', kind='glass')
    cv.rect(13, Fb - 39, 49, Fb - 37, '#5a5e66')
    cv.rect(26, Fb - 39, 36, Fb - 38, '#3a3a44')
    # 取号机（1.3 m）
    cv.rect(65, Fb - 22, 77, Fb, '#e8e4d8')
    cv.hline(65, 77, Fb - 22, '#1f6a4a')
    cv.hline(65, 77, Fb - 21, '#1f6a4a')
    cv.vline(77, Fb - 20, Fb, '#b8b4a8')
    cv.rect(67, Fb - 18, 75, Fb - 13, '#2a1a1a')
    ptext(cv, 68, Fb - 18, '42', '#ff4a3a')
    cv.rect(68, Fb - 10, 74, Fb - 9, '#3a3a44')
    cv.put(71, Fb - 8, '#f8f8f0')
    # 海报、长沙发、盆栽
    cv.rect(100, Fb - 45, 130, Fb - 25, '#f8f6ee')
    cv.rect(101, Fb - 44, 129, Fb - 36, '#7ab8e8')
    cv.ellipse(108, Fb - 40, 3, 3, '#f8c838')
    cv.rect(101, Fb - 36, 129, Fb - 35, '#f0b040')
    K.text(cv, 102, Fb - 36, '定期', '#d03a2a', 10)
    ptext(cv, 121, Fb - 31, '35', '#d03a2a')
    K.sofa(cv, 116, Fb, w=46, c='#3a8a5a')
    K.plant(cv, 155, Fb, 16, pot='#c8c0b0', seed=6)
    K.clock(cv, 160, C + 13, 3)
    # 柜台后面的办公区：文件柜 + 办公桌
    for wx in (193, 243, 293):
        cv.rect(wx - 22, Fb - 24, wx - 11, Fb, '#a8b0b8')
        cv.hline(wx - 22, wx - 11, Fb - 24, '#c8d0d8')
        for yy in range(Fb - 18, Fb, 6):
            cv.hline(wx - 22, wx - 11, yy, '#7a828a')
            cv.hline(wx - 18, wx - 15, yy - 3, '#5a626a')
        K.table(cv, wx + 10, Fb, w=22, h=11, c='#9a7a54')
        cv.rect(wx + 3, Fb - 16, wx + 9, Fb - 12, '#d8d4c8')           # 桌上的文件和显示器
        cv.rect(wx + 12, Fb - 19, wx + 19, Fb - 13, '#3a3a44')
        cv.rect(wx + 13, Fb - 18, wx + 18, Fb - 14, '#6a9a8a')
    return cv


def bank_counter():
    """柜台 + 玻璃隔断单独一层（前景，按纵深排在柜员前面、顾客后面）：台面 1.02 m = 17 px，台脚落在 y = 140"""
    cv = Cv(320, 180)
    by = 140
    top = by - 17
    I.counter(cv, 172, 319, by, 17, '#8a5a34', top='#e8dcc0')
    # 玻璃隔断（台面上 17 px）：三个窗口
    gy = top - 17
    g = rgba('#c8e4ee')
    cv.a[gy + 2:top, 173:320] = (g[0], g[1], g[2], 70)
    for i in range(0, 14, 5):                                        # 反光
        for wx in (193, 243, 293):
            cv.line(wx - 14 + i, top - 2, wx - 6 + i, gy + 3, (255, 255, 255, 90))
    cv.rect(172, gy, 319, gy + 1, '#8a8e96')
    cv.hline(172, 319, gy, '#b8bcc4')
    for x in (172, 218, 268, 318):
        cv.rect(x, gy, x + 1, top - 1, '#8a8e96')
    for n, wx in enumerate((193, 243, 293)):
        cv.a[top - 3:top, wx - 5:wx + 6] = 0                         # 递东西的口
        cv.rect(wx - 9, gy - 7, wx + 9, gy - 1, '#1a1a20')           # 窗口号牌
        ptext(cv, wx - 7, gy - 6, str(n + 1), '#f0b040')
        ptext(cv, wx - 1, gy - 6, ('039', '040', '041')[n], '#ff4a3a')
    return cv


def build_budogaoka_bank():
    cv = budogaoka_bank()
    Fb, C = BANK_F, BANK_C
    glow = I.shafts(320, [[(15, Fb + 1), (48, Fb + 1), (104, 176), (10, 176)]], col='#fff4d0', k=0.09)
    K.save_layers('budogaoka_bank', dict(room=cv, glow=glow, counter=bank_counter()))

    def fix(e):
        e['fg'] = [{'type': 'pano', 'image': 'bg/budogaoka_bank/counter', 'k': 1, 'x': 0, 'y': 0}]
    edit_meta('budogaoka_bank', fix)
    K.update_meta('budogaoka_bank', anchors=dict(poster=[115, Fb - 35], counter=[243, 123], clock=[160, C + 13], sign=[244, C + 13]))
    return cv


# ================================================================ 中学：操场 + 体育器材棚 + 教学楼外廊 middle_school（640）
def classroom_view(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1, y1, '#e8e0c8')
    cv.rect(x0, y0, x1, y0 + 2, '#c8dce8')
    for x in range(x0 + 3, x1 - 6, 12):
        cv.rect(x, y1 - 6, x + 7, y1 - 5, '#c8a878')
        cv.vline(x + 1, y1 - 4, y1, '#8a8e96')
        cv.vline(x + 6, y1 - 4, y1, '#8a8e96')


def middle_school():
    W = 640
    cv = Cv(W, 180)
    G = GROUND
    r = K.rng(3)
    # ---------------- 操场（0–227）：上面留空，露出远景层的天
    sand = '#d8b888'
    cv.rect(0, G + 1, 227, 179, sand)
    cv.hline(0, 227, G + 1, shade(sand, -0.2))
    for _ in range(220):
        cv.put(int(r.uniform(0, 228)), int(r.uniform(G + 3, 180)), shade(sand, float(r.choice([-0.1, 0.08, -0.05]))))
    for x in range(0, 228, 14):                                      # 石灰线
        cv.hline(x, x + 8, 171, '#f4ecd8')
    # 挡球网：5 m 高的铁丝网 + 矮墙
    net = rgba('#8a98a8')
    for y in range(52, G - 6):
        for x in range(0, 228):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                cv.a[y, x] = (net[0], net[1], net[2], 120)
    for x in range(0, 228, 38):
        cv.rect(x, 50, x + 1, G - 6, '#7a8088')
    cv.rect(0, 50, 227, 51, '#8a9098')
    cv.rect(0, G - 6, 227, G, '#c8c4b8')
    cv.hline(0, 227, G - 6, '#e0dcd0')
    cv.hline(0, 227, G, '#9a968a')
    # 足球门（2 m 高）：前框 + 往后收的网
    gx0, gx1, gt, gb = 28, 88, 117, 150
    wn = (244, 244, 244, 130)
    for y in range(gt + 1, gb):
        for x in range(gx0 - 8, gx1):
            if (x + y) % 3 == 0 and (x >= gx0 or y >= gt + (gx0 - x)):
                cv.a[y, x] = wn
    cv.line(gx0, gt, gx0 - 8, gt + 8, '#e8e8e8')
    cv.vline(gx0 - 8, gt + 8, gb - 4, '#d8d8d8')
    cv.line(gx0 - 8, gb - 4, gx0, gb, '#d8d8d8')
    for x in (gx0, gx1):
        cv.rect(x, gt, x + 1, gb, '#f8f8f8')
        cv.vline(x + 1, gt, gb, '#c8c8c8')
    cv.rect(gx0, gt, gx1 + 1, gt + 1, '#f8f8f8')
    cv.hline(gx0, gx1 + 1, gt + 2, '#c8c8c8')
    K.shadow(cv, gx0 - 6, gx1 + 2, gb + 1, 0.3, h=1)
    # 半埋的彩色轮胎
    for i, col in enumerate(('#d04040', '#e8a030', '#40a060', '#3a7ad0', '#d05a9a', '#e8c838')):
        tx = 122 + i * 12
        cv.ellipse(tx, 152, 5.2, 5.2, col)
        cv.ellipse(tx, 152, 2.6, 2.6, shade(sand, -0.1))
        cv.rect(tx - 6, 153, tx + 6, 158, sand)
        cv.hline(tx - 5, tx + 5, 153, shade(sand, -0.18))
    # ---------------- 体育器材棚（228–391）：敞口的铁皮棚
    ry = G - 50                                                      # 檐口底
    cv.rect(228, ry + 1, 391, G, '#b4b0a4')
    for y in range(ry + 4, G, 5):
        cv.hline(228, 391, y, '#a4a094')
    K.dither(cv, 228, ry + 1, 391, ry + 9, '#6a6860', 0.5)           # 檐下的暗
    K.dither(cv, 228, ry + 10, 391, ry + 16, '#8a887c', 0.3)
    cv.rect(228, G - 1, 391, G, '#7a786c')
    cv.rect(228, G + 1, 391, 179, '#b0aca0')                         # 水泥地
    cv.hline(228, 391, G + 1, '#8a877c')
    K.dither(cv, 228, G + 2, 391, G + 6, '#8a877c', 0.4)
    for y in (G + 12, G + 26):
        cv.hline(228, 391, y, '#9c988c')
    for x in range(250, 392, 46):
        cv.vline(x, G + 2, 179, '#9c988c')
    cv.rect(304, G - 45, 328, G - 37, '#6a6e76')                     # 高处的小窗
    cv.rect(305, G - 44, 327, G - 38, '#b8d8ea')
    cv.vline(316, G - 45, G - 37, '#6a6e76')
    # 铁架：上层雪糕筒，下层球
    cv.rect(234, G - 30, 235, G, '#5a5e66')
    cv.rect(256, G - 30, 257, G, '#5a5e66')
    for yy in (G - 30, G - 16):
        cv.rect(234, yy, 257, yy + 1, '#7a7e86')
    for x in (238, 243, 248, 253):
        cv.rect(x, G - 32, x + 2, G - 31, '#f06a20')
        cv.put(x + 1, G - 33, '#f06a20')
        cv.put(x + 1, G - 34, '#f06a20')
        cv.put(x + 1, G - 35, '#f8f8f0')
    for x, col in ((239, '#f0c030'), (245, '#3a7ad0'), (251, '#d04040')):
        cv.ellipse(x + 1, G - 19, 2.6, 2.6, col)
    cv.rect(237, G - 9, 254, G, '#c8a878')
    cv.hline(237, 254, G - 9, '#e0c090')
    # 跳箱（5 层，1.1 m）
    for i in range(5):                                               # i = 0 最上面一层
        w_ = 14 + i * 2
        ya = G - 16 + i * 3
        cv.rect(272 - w_ // 2, ya, 272 + w_ // 2, ya + 2, '#c89858')
        cv.hline(272 - w_ // 2, 272 + w_ // 2, ya + 2, '#8a6030')
        cv.hline(271, 273, ya + 1, '#6a4a28')
    cv.hline(261, 283, G, '#8a6030')
    cv.rect(265, G - 19, 279, G - 17, '#f4f0e0')
    cv.hline(265, 279, G - 17, '#c8c4b0')
    # 墙上的呼啦圈
    for col, rr_ in (('#40a060', 6), ('#e8a030', 4.4)):
        for a in np.arange(0, 6.3, 0.12):
            cv.put(int(round(292 + np.cos(a) * rr_)), int(round(G - 26 + np.sin(a) * rr_)), col)
    # 一摞体操垫
    for i, col in enumerate(('#3a6ab0', '#4a7ac0', '#3a6ab0')):
        ya = G - 4 - i * 4
        cv.rect(304, ya, 340, ya + 3, col)
        cv.hline(304, 340, ya, shade(col, 0.3))
        cv.hline(304, 340, ya + 3, shade(col, -0.3))
        cv.vline(322, ya, ya + 3, shade(col, -0.2))
    # 球车
    for x in (359, 363, 367, 371):
        for dy in (0, 4):
            cv.ellipse(x + (dy // 4) * 2 - 1, G - 9 - dy, 2.6, 2.6, '#f4f4f0')
            cv.put(x + (dy // 4) * 2 - 1, G - 9 - dy, '#c8c8c8')
    for x in range(356, 376, 3):
        cv.vline(x, G - 13, G - 3, '#6a6e76')
    cv.rect(355, G - 14, 375, G - 13, '#8a8e96')
    cv.hline(355, 375, G - 3, '#6a6e76')
    cv.put(357, G - 1, '#2a2a30')
    cv.put(373, G - 1, '#2a2a30')
    cv.vline(357, G - 2, G - 2, '#6a6e76')
    cv.vline(373, G - 2, G - 2, '#6a6e76')
    # 墙上的挂钩和铁丝衣架
    cv.hline(360, 386, G - 33, '#5a5e66')
    for x in (366, 374, 382):
        cv.put(x, G - 32, '#5a5e66')
        cv.line(x, G - 31, x - 3, G - 28, '#c8ccd4')
        cv.line(x, G - 31, x + 3, G - 28, '#c8ccd4')
        cv.hline(x - 3, x + 3, G - 28, '#c8ccd4')
    # 棚的侧柱和铁皮檐口
    for x in (228, 389):
        cv.rect(x, ry + 1, x + 2, G, '#6a6e76')
        cv.vline(x, ry + 1, G, '#8a8e96')
    cv.rect(224, ry - 6, 395, ry, '#7a8088')
    for x in range(224, 396, 3):
        cv.vline(x, ry - 6, ry - 1, '#9aa0a8')
    cv.hline(224, 395, ry - 6, '#b4bac2')
    cv.hline(224, 395, ry, '#4a4e56')
    cv.rect(226, ry - 9, 393, ry - 7, '#8a9098')
    cv.hline(226, 393, ry - 9, '#a8aeb6')
    # 棚边的树
    O.tree(cv, 204, G + 8, h=86, w=52, seed=3)
    # ---------------- 教学楼（392–639）：一楼是敞开的外廊，上面是二、三楼外墙
    sl = G - 52                                                      # 外廊顶板底
    wallc = '#ece6da'
    cv.rect(392, 0, W - 1, sl - 6, wallc)
    cv.hline(392, W - 1, 24, '#d0cabc')                              # 三楼楼板线
    for x in range(404, 636, 40):
        K.window_ext(cv, x, 40, x + 30, 62, frame='#f4f0e4', glass='#7a9ab8', nx=3)
        K.window_ext(cv, x, 0, x + 30, 9, frame='#f4f0e4', glass='#7a9ab8', nx=3)
        cv.rect(x - 1, 63, x + 31, 64, '#d0cabc')
    cv.rect(392, sl - 6, W - 1, sl - 1, '#d8d2c4')                   # 外廊顶板
    cv.hline(392, W - 1, sl - 6, '#f0ece0')
    cv.hline(392, W - 1, sl, '#7a766a')
    cv.rect(392, sl + 1, W - 1, G, '#f0ead8')                        # 外廊里的墙
    K.dither(cv, 392, sl + 1, W - 1, sl + 8, '#a8a290', 0.5)
    K.dither(cv, 392, sl + 9, W - 1, sl + 14, '#c8c2b0', 0.3)
    cv.rect(392, G - 14, W - 1, G, '#9ab8a8')
    cv.hline(392, W - 1, G - 14, '#7a9888')
    cv.rect(392, G - 1, W - 1, G, '#6a8878')
    for x in (392, 540):                                             # 壁柱
        cv.rect(x, sl + 1, x + 4, G, '#dcd6c8')
        cv.vline(x + 4, sl + 1, G, '#b8b2a4')
    cv.rect(392, 0, 395, sl - 6, '#dcd6c8')
    cv.vline(395, 0, sl - 6, '#b8b2a4')
    # 公告栏、朝外廊的教室窗、消火栓、2-B 的门
    cv.rect(410, G - 41, 440, G - 20, '#8a6a44')
    cv.rect(411, G - 40, 439, G - 21, '#c8a868')
    for (a, b, col) in ((413, G - 38, '#f4f4f0'), (423, G - 38, '#f0d8d8'), (431, G - 37, '#d8e8f0'), (414, G - 29, '#f4f0c8'), (426, G - 28, '#f4f4f0')):
        cv.rect(a, b, a + 6, b + 5, col)
        cv.hline(a + 1, a + 4, b + 2, '#8a8a90')
    K.window(cv, 452, G - 36, 500, G - 15, frame='#5a7a6a', nx=3, view=clip(classroom_view))
    cv.rect(510, G - 22, 526, G, '#d03a3a')
    cv.hline(510, 526, G - 22, '#e86a6a')
    cv.rect(513, G - 18, 523, G - 12, '#f4f0e0')
    cv.ellipse(518, G - 26, 2.4, 2.4, '#e03030')
    I.class_door(cv, 565, G, sign='2-B')
    # 楼梯口
    cv.rect(600, sl + 1, W - 1, G, '#c8c4b4')
    cv.vline(600, sl + 1, G, '#8a8678')
    for i in range(7):
        cv.rect(604 + i * 5, G - 5 - i * 5, W - 1, G - i * 5, '#b4b0a0')
        cv.hline(604 + i * 5, W - 1, G - 5 - i * 5, '#dcd8c8')
    cv.line(602, G - 18, 638, G - 54, '#6a6a70')
    # 外廊的地
    cv.rect(392, G + 1, W - 1, 179, '#c8c8bc')
    cv.hline(392, W - 1, G + 1, '#98988c')
    K.dither(cv, 392, G + 2, W - 1, G + 7, '#98988c', 0.4)
    for y in (G + 12, G + 26):
        cv.hline(392, W - 1, y, '#b4b4a8')
    for x in range(410, W, 44):
        cv.vline(x, G + 2, 179, '#b4b4a8')
    cv.vline(391, G + 1, 179, '#8a877c')
    cv.vline(227, G + 1, 179, shade(sand, -0.25))
    return cv


def build_middle_school():
    cv = middle_school()
    G = GROUND
    glow = I.shafts(640)                                             # 户外白天不加光晕，图层留着（元数据里有）
    K.save_layers('middle_school', dict(near=cv, glow=glow))
    K.update_meta('middle_school',
                  anchors=dict(vault_box=[272, 146], sit=[322, G - 12], hanger=[374, G - 30], shed_window=[316, G - 41], board=[425, G - 30],
                               josuke_window=[539, 51]))
    return cv


# ================================================================ 港口的集装箱 morioh_harbor / morioh_harbor_late（只换集装箱那一块）
def container(cv, x0, by, c, w=100, h=43, label=None, seed=0):
    """20 英尺集装箱侧面：6.06 × 2.59 m = 101 × 43 px"""
    y0 = by - h + 1
    x1 = x0 + w - 1
    cv.rect(x0, y0, x1, by, c)
    for x in range(x0 + 3, x1 - 2, 3):
        cv.vline(x, y0 + 3, by - 3, shade(c, -0.16))
        cv.vline(x + 1, y0 + 3, by - 3, shade(c, 0.14))
    cv.rect(x0, y0, x1, y0 + 2, shade(c, -0.22))
    cv.hline(x0, x1, y0, shade(c, 0.25))
    cv.rect(x0, by - 2, x1, by, shade(c, -0.42))
    for x in (x0, x0 + 1, x1 - 1, x1):
        cv.vline(x, y0, by, shade(c, -0.36))
    for (a, b) in ((x0, y0), (x1 - 2, y0), (x0, by - 2), (x1 - 2, by - 2)):
        cv.rect(a, b, a + 2, b + 2, shade(c, -0.6))
    r = K.rng(seed)
    for _ in range(w // 5):
        x = int(r.uniform(x0 + 4, x1 - 4))
        hh = int(r.randint(1, 5))
        cv.vline(x, by - 3 - hh, by - 3, '#8a4a2a')
    if label:
        lw = len(label) * 4 + 5
        cv.rect(x0 + 8, y0 + 8, x0 + 8 + lw, y0 + 16, '#f0ece0')
        ptext(cv, x0 + 11, y0 + 10, label, shade(c, -0.5))


def wheel(cv, cx, cy, r):
    cv.ellipse(cx, cy, r, r, '#1a1a20')
    cv.ellipse(cx, cy, r - 2.2, r - 2.2, '#8a8e98')
    cv.put(cx, cy, '#3a3a44')


def forklift(cv):
    """电瓶叉车：护顶架 2.2 m = 37 px、车身 1.1 m、轮子 60 cm；落地 y = 150。前轮不画（在 tyre0 / tyre1 两张可切换的小图里）"""
    Y, Yd, Yl, D, Dd, M, Ml = '#e8a820', '#c08818', '#f8c848', '#3a3a44', '#2a2a30', '#5a5e68', '#7a7e88'
    cv.rect(606, 108, 607, 148, M)                                   # 门架
    cv.rect(608, 108, 609, 148, Ml)
    cv.hline(606, 609, 108, '#9a9ea8')
    cv.rect(594, 148, 607, 149, Ml)                                  # 货叉
    cv.hline(594, 607, 150, M)
    cv.rect(604, 138, 605, 148, M)
    cv.rect(612, 113, 646, 114, D)                                   # 护顶架
    for x in range(615, 645, 4):
        cv.put(x, 113, '#6a6a76')
    cv.rect(614, 115, 615, 131, D)
    cv.rect(642, 115, 643, 129, D)
    cv.rect(611, 132, 648, 146, Y)                                   # 车身
    cv.hline(611, 648, 132, Yl)
    cv.rect(611, 145, 648, 146, Yd)
    cv.rect(636, 130, 648, 144, D)                                   # 配重
    cv.hline(636, 648, 130, M)
    cv.rect(615, 135, 632, 142, Yd)
    ptext(cv, 617, 136, 'BATT', '#5a3a08')
    cv.rect(630, 125, 635, 131, Dd)                                  # 座椅、方向盘
    cv.line(621, 131, 624, 124, Dd)
    cv.hline(622, 626, 124, Dd)
    cv.rect(646, 126, 647, 129, '#e03a2a')                           # 警示灯
    wheel(cv, 640, 146, 4.4)
    cv.ellipse(618, 145, 6.4, 6.4, Dd)                               # 前轮的轮拱


def tyres():
    """叉车前轮的两张小图（14 × 13，贴在 611, 139）：好的 / 被打爆的"""
    t0 = Cv(14, 13)
    wheel(t0, 7, 6, 5.4)
    t1 = Cv(14, 13)
    t1.ellipse(7, 8, 6, 3.6, '#1a1a20')
    t1.rect(5, 5, 9, 8, '#8a8e98')
    t1.put(7, 6, '#3a3a44')
    for (a, b, c, d) in ((2, 6, 0, 3), (12, 6, 13, 2), (4, 4, 3, 1), (10, 5, 11, 1)):
        t1.line(a, b, c, d, '#2a2a30')
    t1.hline(1, 12, 12, '#1a1a20')
    return t0, t1


def harbor_new():
    """新画的东西（透明底的整张 960 图）：两层集装箱（下 SPW 红 + 蓝，上 TOHO 黄 + MRH 绿）和叉车"""
    cv = Cv(960, 180)
    by = 127
    container(cv, 252, by, '#c8483c', label='SPW', seed=1)
    container(cv, 353, by, '#3a6a9a', seed=2)
    container(cv, 262, by - 43, '#d89a30', label='TOHO', seed=3)
    container(cv, 364, by - 43, '#4a8a5a', label='MRH', seed=4)
    forklift(cv)
    return cv


HARBOR_REV = 'd7f8a53'                    # 集装箱和叉车还没改的那个提交


def harbor_orig(key):
    import io
    import subprocess
    root = os.path.normpath(os.path.join(K.ASSETS, '..', '..'))
    rel = '第四部/assets/bg/%s/near.png' % key
    raw = subprocess.run(['git', 'show', '%s:%s' % (HARBOR_REV, rel)], cwd=root, capture_output=True, check=True).stdout
    return np.array(Image.open(io.BytesIO(raw)).convert('RGBA'))


def build_harbor(key):
    def fn():
        a = harbor_orig(key)
        M = None
        if key != 'morioh_harbor':
            # 傍晚版是白天版整体偏色出来的：用两张旧图配一个颜色矩阵，套到新画的东西上
            base = harbor_orig('morioh_harbor')
            m = (base[..., 3] > 0) & (a[..., 3] > 0)
            X = np.c_[base[m][:, :3].astype(float), np.ones(m.sum())]
            M, *_ = np.linalg.lstsq(X, a[m][:, :3].astype(float), rcond=None)

        def tone(arr):
            arr = arr.copy()
            if M is not None:
                op = arr[..., 3] > 0
                v = np.c_[arr[op][:, :3].astype(float), np.ones(op.sum())] @ M
                arr[op, :3] = np.clip(np.round(v), 0, 255).astype(np.uint8)
            return arr
        out = a.copy()
        out[42:128, 250:452] = 0                                     # 擦掉旧集装箱
        out[88:124, 584:655] = 0                                     # 擦掉旧叉车：码头面以上清空，码头面用旁边干净的一段补上
        for x in range(584, 655):
            out[124:154, x] = a[124:154, 500 + (x - 584) % 40]
        new = tone(harbor_new().a)
        op = new[..., 3] > 0
        out[op] = new[op]
        # 集装箱前面那根路灯（x = 411）补回来：拿后面没东西的那根（x = 901）当模板
        lamp = a[40:128, 893:925, 3] > 0
        lamp[10:, :4] = False
        lamp[10:, 13:] = False
        lamp[80:, :7] = False
        lamp[80:, 10:] = False
        seg = out[40:128, 403:435]
        seg[lamp] = a[40:128, 403:435][lamp]
        img = Image.fromarray(out, 'RGBA')
        img.save(os.path.join(K.ASSETS, 'bg', key, 'near.png'))
        t0, t1 = tyres()
        K.save_layers(key, dict(tyre0=Image.fromarray(tone(t0.a), 'RGBA'), tyre1=Image.fromarray(tone(t1.a), 'RGBA')))

        def fix(e):
            for L in e['layers']:
                if L.get('key') == 'tyre':
                    L.update(x=611, y=139)
        edit_meta(key, fix)
        K.update_meta(key, anchors=dict(forklift_batt=[622, 138], tyre=[618, 145]))
        return Cv.of(img)
    return fn


BUILD = {
    'higashikata_tvnight': build_higashikata_tvnight, 'rohan_studio': build_rohan_studio, 'farmhouse': build_farmhouse,
    'budogaoka_bank': build_budogaoka_bank, 'middle_school': build_middle_school,
    'morioh_harbor': build_harbor('morioh_harbor'), 'morioh_harbor_late': build_harbor('morioh_harbor_late'),
}


def check(key, out, ids=None, ys=(148, 156, 164)):
    """比例核对图：当前 assets 里这张背景的常开图层 + 前景层，贴几个人物，放大 3 倍"""
    import cast_pro
    from rig import OX, OY
    spec = {}
    for fp in glob.glob(os.path.join(K.META, 'bg*.json')):
        spec.update(json.load(open(fp, encoding='utf-8')))
    spec = spec[key]
    w = spec.get('w', 320)
    im = Image.new('RGBA', (w, 180), (20, 20, 30, 255))

    def comp(L):
        nonlocal im
        t = L['type']
        name = L.get('image') or (L.get('images') or [None])[0]
        if t not in ('pano', 'static', 'image', 'glow', 'pick', 'strip') or not name or (L.get('key') and t not in ('pick',)):
            return
        a = Image.open(os.path.join(K.ASSETS, name + '.png')).convert('RGBA')
        k = L.get('k', 1)
        if t == 'glow':
            b = np.array(im).astype(int)
            g = np.array(a).astype(int)
            x, y = L.get('x', 0), L.get('y', 0)
            hh, ww = min(b.shape[0] - y, g.shape[0]), min(b.shape[1] - x, g.shape[1])
            b[y:y + hh, x:x + ww, :3] = np.clip(b[y:y + hh, x:x + ww, :3] + g[:hh, :ww, :3], 0, 255)
            im = Image.fromarray(b.astype('uint8'), 'RGBA')
        elif t == 'strip':
            fw = L.get('w') or a.width // (L.get('n') or 1)
            im.alpha_composite(a.crop((0, 0, fw, L.get('h') or a.height)), (L.get('x', 0), L.get('y', 0)))
        elif k not in (1, None) and t == 'pano':
            for sx in range(0, w, 320):
                cam = min(sx, w - 320)
                off = int(cam * k)
                im.alpha_composite(a.crop((off, 0, min(a.width, off + 320), 180)), (cam, 0))
        else:
            im.alpha_composite(a, (L.get('x', 0), L.get('y', 0)))
    for L in spec['layers']:
        comp(L)
    for L in spec.get('fg') or []:
        if not L.get('screen') and not L.get('key'):
            comp(L)
    n = max(4, w // 110)
    ids = ids or ['josuke', 'jotaro4', 'koichi', 'tomoko', 'kid', 'ryohei', 'fan_a', 'thug_a', 'clerk']
    for i in range(n):
        f = cast_pro.build(ids[i % len(ids)]).rows[0][1][0].img()
        x = int((i + 0.5) * w / n)
        im.alpha_composite(f, (x - OX, ys[i % len(ys)] - OY - 1))
    k = 3 if w <= 640 else 2
    im.resize((w * k, 180 * k), Image.NEAREST).save('%s/bg_%s.png' % (out, key))


if __name__ == '__main__':
    out = sys.argv[1]
    for key in (sys.argv[2:] or list(BUILD)):
        cv = BUILD[key]()
        check(key, out)
        print(key, cv.w)
