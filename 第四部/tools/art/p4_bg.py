# 第四部序章的背景：7 张（含变体），全部程序绘制。输出 第四部/assets/bg/<key>/<层>.png + _meta/bg.json。
#   用法：python3 第四部/tools/art/p4_bg.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402

OUT = os.path.join(LIB.ASSETS, 'bg')
PREV = os.path.join(LIB.ASSETS, 'preview')
PETALS = {'type': 'petals', 'n': 24, 'colors': ['#f4a0be', '#ffd6e4'], 'seed': 41, 'y0': -6, 'y1': 184, 'vx': -12.7, 'vy': 34.5,
          'per': [4, 7], 'x0': [-20, 380], 'drift': 70, 'sway': 6, 'swayW': 2.3, 'k': 0.2, 'wrapX': 40}


def save_layers(key, layers, meta):
    os.makedirs(os.path.join(OUT, key), exist_ok=True)
    for name, im in layers.items():
        im.save(os.path.join(OUT, key, name + '.png'))
    return meta


def preview(key, layers, order, w, k=None):
    """按视差合成一张整图（镜头在最左）方便看"""
    os.makedirs(PREV, exist_ok=True)
    can = Image.new('RGBA', (w, 180), (0, 0, 0, 255))
    for name in order:
        im = layers[name]
        if im.width < w:      # 远层：按 k 拉回整宽来看
            im = im.resize((w, 180), Image.NEAREST) if k else im
        can.alpha_composite(im.crop((0, 0, w, 180)))
    can.save(os.path.join(PREV, f'bg_{key}.png'))


# ============================================================ 上学路 morioh_road（960 宽，早上 / 下午）
def sky_far(w, seed=1, cols=('#78b0ec', '#96c4f0', '#b6d8f4', '#d8eaf6'), sea=True, hills=True, night=False):
    im = new(w, 180, cols[-1])
    im = grad(im, (0, 0, w, 116), cols)
    rng = np.random.RandomState(seed)
    if not night:
        for i in range(int(w / 110)):
            cloud(im, rng.randint(0, w - 40), rng.randint(14, 58), rng.randint(26, 58), seed=seed * 10 + i)
    d = ImageDraw.Draw(im)
    if hills:
        # 远山两层（山脊用正弦叠出来）
        for layer, (base, amp, col, col2) in enumerate(((92, 10, '#9cb8c4', '#b4ccd4'), (100, 8, '#7c9eac', '#90b0bc'))):
            for x in range(w):
                y = base + amp * np.sin(x / (60 + layer * 25) + layer) + 4 * np.sin(x / 17.0 + layer * 2)
                line(d, (x, int(y), x, 130), col)
                px(d, x, int(y), col2)
    if sea:
        rect(d, (0, 106, w, 112), '#5c98cc')
        for x in range(0, w, 7):
            px(d, x + (x // 7) % 3, 108, '#9cc8ec')
        line(d, (0, 106, w, 106), '#88b8e0')
    # 远处的屋顶
    for i in range(int(w / 14)):
        x = rng.randint(-10, w)
        bw, bh = rng.randint(10, 22), rng.randint(6, 14)
        y = 118 - bh + rng.randint(-2, 4)
        roof = ['#7a8aa0', '#8a7a78', '#6a7a8a', '#9a8e86'][rng.randint(4)]
        rect(d, (x, y, x + bw, 130), ['#dcd6cc', '#e8e0d4', '#cfc8bc'][rng.randint(3)])
        rect(d, (x - 1, y - 3, x + bw + 1, y), roof)
        for wx in range(x + 2, x + bw - 2, 5):
            px(d, wx, y + 3, '#8ea8bc')
    rect(d, (0, 124, w, 180), '#a8b49c')
    return im


def morioh_road():
    W, G = 960, 136               # G = 房子 / 围墙的地脚线；人行道从这里开始
    far = sky_far(640, seed=3)
    near = new(W, 180)
    d = ImageDraw.Draw(near)
    # 人行道 + 马路
    near = sidewalk(near, 0, W, G, 166)
    near = asphalt(near, 0, W, 166, 180)
    d = ImageDraw.Draw(near)
    # 房子和围墙（从左到右）
    houses = [(8, 96, 74, 1, '#e6dccb'), (150, 88, 70, 2, '#dfe2e6'), (300, 92, 72, 3, '#efe2cc'), (560, 100, 76, 4, '#e2d6c6'),
              (690, 84, 66, 5, '#e8e4d8')]
    for x, w, h, s, wall in houses:
        near = house(near, x, G - 10, w, h, wall=wall, wall2=mix(wall, '#000000', .18), seed=s,
                     roof=[('#3e4a5e', '#2e3848', '#56647a', '#1e2632'), ('#6a3e36', '#4e2c28', '#8a5246', '#341c1a'),
                           ('#3a5a52', '#2a4440', '#4e766a', '#1c2e2a')][s % 3])
    d = ImageDraw.Draw(near)
    # 围墙 + 树篱（房子前面）
    for x0, x1 in ((0, 120), (140, 262), (290, 400), (548, 680), (686, 790)):
        near = hedge(near, x0, x1, G - 26, G - 18, seed=x0)
        near = block_wall(near, x0, x1, G - 18, G)
    d = ImageDraw.Draw(near)
    # 老奶奶家的窗台（花盆从这里掉下来）：窗在围墙上方
    near = flower_pot_window(near, 318, G - 34)
    d = ImageDraw.Draw(near)
    # 樱花
    for cx, h, w, s in ((128, 104, 74, 7), (278, 96, 66, 8), (530, 108, 80, 9), (808, 112, 84, 10), (900, 98, 70, 11)):
        near = sakura(near, cx, G - 2, h, w, seed=s)
    # 公园那一段（790–960）：矮栅栏 + 草地
    d = ImageDraw.Draw(near)
    rect(d, (790, G - 10, W, G), '#7aa85a')
    for x in range(792, W, 6):
        rect(d, (x, G - 14, x + 1, G - 2), '#e8e2d6')
    line(d, (790, G - 12, W, G - 12), '#e8e2d6')
    line(d, (790, G - 6, W, G - 6), '#e8e2d6')
    near = noise_specks(near, (790, G - 10, W, G), ['#94c070', '#5a8a4a'], 120, 5)
    # 电线杆 + 电线
    poles = [60, 268, 470, 680, 880]
    for x in poles:
        near = pole(near, x, G + 2, 128)
    near = wires(near, [(x, G + 2 - 128 + 7) for x in poles], sag=8)
    # 公交站、自动售货机
    near = bus_stop(near, 404, G + 4)
    near = vending(near, 520, G + 2)
    d = ImageDraw.Draw(near)
    # 去学校的路牌（右端）
    rect(d, (936, G - 50, 937, G + 2), '#8a8a90')
    rect(d, (920, G - 58, 954, G - 46), '#2a6ab0')
    rect(d, (921, G - 57, 953, G - 47), '#3a7ac8')
    line(d, (924, G - 52, 946, G - 52), '#f0f0f0')
    line(d, (946, G - 52, 943, G - 55), '#f0f0f0')
    line(d, (946, G - 52, 943, G - 49), '#f0f0f0')
    # 地上的落花
    near = fallen_petals(near, (0, G + 1, W, 166), 260, 3)
    near = fallen_petals(near, (100, G + 1, 160, 150), 40, 4)
    near = fallen_petals(near, (500, G + 1, 560, 150), 40, 5)
    layers = {'far': far, 'near': near}
    meta = dict(pack='prologue', w=W, ground=150, walk=[142, 172],
                anchors=dict(pot=[332, 148], window=[332, 104], vending=[531, 148], busstop=[408, 146], sakura=[808, 140],
                             fans=[600, 152], thug=[430, 156], exit_x=930, walk_x=[8, 952]),
                layers=[{'type': 'pano', 'image': 'bg/morioh_road/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/morioh_road/near', 'k': 1, 'x': 0, 'y': 0},
                        dict(PETALS, seed=41),
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    preview('morioh_road', {'far': far.resize((W, 180), Image.NEAREST), 'near': near}, ['far', 'near'], W)
    return save_layers('morioh_road', layers, meta)


# ============================================================ 葡萄丘高中校门 budou_gate（640 宽）
def school_building(im, x0, x1, top, base, wall='#ece6da', wall2='#d4ccbc', trim='#5a9a8a', glass=('#8cb4cc', '#bcd8e8')):
    d = ImageDraw.Draw(im)
    rect(d, (x0, top, x1, base), wall)
    rect(d, (x0, top, x1, top + 4), trim)
    line(d, (x0, top + 5, x1, top + 5), mix(trim, '#000000', .3))
    for fl, y in enumerate(range(top + 12, base - 18, 24)):
        line(d, (x0, y + 19, x1, y + 19), wall2)
        for wx in range(x0 + 8, x1 - 16, 22):
            window(d, (wx, y, wx + 16, y + 14), frame='#f4f0e8', glass=glass, curtain='#e8e0c8' if (wx // 22 + fl) % 5 == 0 else None)
    for x in range(x0, x1, 66):
        rect(d, (x, top + 6, x + 2, base), wall2)
    rect(d, (x0, base - 4, x1, base), wall2)
    return im


def budou_gate():
    W, G = 640, 140
    far = sky_far(480, seed=5, sea=False)
    near = new(W, 180)
    d = ImageDraw.Draw(near)
    # 校舍（门后面）：主楼 + 右边一截体育馆
    near = school_building(near, 120, 520, 30, G - 8)
    d = ImageDraw.Draw(near)
    # 主楼中间的钟塔
    rect(d, (296, 6, 344, 34), '#ece6da')
    rect(d, (296, 6, 344, 9), '#5a9a8a')
    ellipse(d, (310, 13, 330, 33), '#f8f6f0')
    ellipse(d, (311, 14, 329, 32), '#ffffff')
    line(d, (320, 23, 320, 16), '#2a2a30')
    line(d, (320, 23, 325, 23), '#2a2a30')
    for i in range(12):
        import math as _m
        px(d, 320 + 8 * _m.cos(i * _m.pi / 6), 23 + 8 * _m.sin(i * _m.pi / 6), '#6a6a70')
    rect(d, (520, 62, 640, G - 8), '#d8d0c0')
    for x in range(524, 640, 14):
        rect(d, (x, 70, x + 8, 92), '#9cbcd0')
    d.pieslice((516, 40, 644, 84), 180, 360, fill=C('#6a8aa8'))
    # 门里看得见的：玄关（玻璃门 + 雨棚）和往里收的步道（围墙挡住了楼的下半截，只有门洞里露出来）
    rect(d, (284, 96, 356, 124), '#e2dccf')
    rect(d, (298, 100, 342, 124), '#6a7a8a')
    for k in range(4):
        rect(d, (300 + k * 10, 102, 308 + k * 10, 124), '#a8c8dc')
        line(d, (301 + k * 10, 103, 304 + k * 10, 106), '#dcecf4')
        line(d, (308 + k * 10, 102, 308 + k * 10, 124), '#5a6a7a')
    rect(d, (292, 94, 348, 98), '#5a9a8a')
    line(d, (292, 98, 348, 98), '#3e7a6a')
    line(d, (292, 94, 348, 94), '#8acaba')
    for lx in (295, 345):
        rect(d, (lx, 98, lx + 1, 124), '#9a9488')
    near = grad(near, (284, 124, 356, G), ('#c8bc9c', '#d4c8aa', '#ded4ba'))
    d = ImageDraw.Draw(near)
    d.polygon([(312, 124), (328, 124), (346, G), (294, G)], fill=C('#e8e0ce'))
    line(d, (312, 124, 294, G), '#c4b694')
    line(d, (328, 124, 346, G), '#c4b694')
    for yy in (128, 133, 138):                                   # 步道的砖缝
        t = (yy - 124) / (G - 124)
        line(d, (312 - 18 * t, yy, 328 + 18 * t, yy), '#d6ccb4')
    for hx in (288, 350):                                        # 两边的小灌木
        ellipse(d, (hx - 5, 118, hx + 5, 128), '#4a7c4a')
        ellipse(d, (hx - 4, 118, hx + 3, 124), '#6e9e5a')
    # 围墙 + 门柱 + 校名牌
    near = block_wall(near, 0, 270, G - 30, G, cols=('#d6d0c4', '#bab4a8', '#9a9488', '#ece8de'))
    near = block_wall(near, 370, W, G - 30, G, cols=('#d6d0c4', '#bab4a8', '#9a9488', '#ece8de'))
    d = ImageDraw.Draw(near)
    for gx in (268, 356):
        rect(d, (gx, G - 50, gx + 16, G), '#b4aca0')
        rect(d, (gx - 1, G - 54, gx + 17, G - 49), '#ccc4b8')
        line(d, (gx + 15, G - 48, gx + 15, G), '#948c80')
        near = noise_specks(near, (gx, G - 48, gx + 15, G), ['#9a9286', '#c8c0b4'], 30, gx)
        d = ImageDraw.Draw(near)
        rect(d, (gx + 5, G - 60, gx + 11, G - 54), '#e8e4d8')
        rect(d, (gx + 6, G - 59, gx + 10, G - 55), '#fff8d0')
    rect(d, (271, G - 44, 281, G - 8), '#f4f0e6')                # 校名牌（竖）
    rect(d, (272, G - 43, 280, G - 9), '#fbf8f0')
    for y in range(G - 40, G - 12, 5):
        rect(d, (274, y, 278, y + 2), '#3a3a40')
    # 打开的铁门（推到右柱后面）
    for x in range(372, 404, 4):
        rect(d, (x, G - 36, x + 1, G - 2), '#5a5e66')
    line(d, (372, G - 36, 404, G - 36), '#5a5e66')
    line(d, (372, G - 20, 404, G - 20), '#5a5e66')
    # 自行车、告示板
    import p4_bglib as BL
    rect(d, (470, G - 36, 520, G - 12), '#7a5a40')
    rect(d, (472, G - 34, 518, G - 14), '#efe8d8')
    for i, c in enumerate(('#e8a0a0', '#a0c0e8', '#f0d080')):
        rect(d, (476 + i * 14, G - 31, 486 + i * 14, G - 17), c)
    # 樱花
    for cx, h, w, sd in ((54, 112, 84, 21), (196, 104, 76, 22), (452, 110, 80, 23), (600, 104, 74, 24)):
        near = sakura(near, cx, G - 2, h, w, seed=sd)
    near = sidewalk(near, 0, W, G, 170)
    near = asphalt(near, 0, W, 170, 180, dash=False)
    near = fallen_petals(near, (0, G + 1, W, 170), 300, 7)
    d = ImageDraw.Draw(near)
    rect(d, (286, G, 354, G + 2), '#c8c0b0')
    layers = {'far': far, 'near': near}
    meta = dict(pack='prologue', w=W, ground=150, walk=[142, 174],
                anchors=dict(gate=[286, 354], plaque=[276, 120], lean=[262, 150], door_x=320, walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/budou_gate/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/budou_gate/near', 'k': 1, 'x': 0, 'y': 0}, dict(PETALS, seed=43)], fg=[])
    preview('budou_gate', {'far': far.resize((W, 180), Image.NEAREST), 'near': near}, ['far', 'near'], W)
    return save_layers('budou_gate', layers, meta)


# ============================================================ 超市 supermarket（640 宽，室内）
PRODUCT = ['#e05a4a', '#f0c040', '#4a90d8', '#58b068', '#f08a3a', '#a070d0', '#f4f0e6', '#d84a8a', '#3ab0b0', '#c89a60']


def shelf(im, x0, x1, top, base, seed=0, label='#e8483c'):
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(im)
    rect(d, (x0, top, x1, base), '#8a8e96')
    rect(d, (x0 + 2, top + 2, x1 - 2, base), '#e4e6ea')
    rect(d, (x0, top - 8, x1, top), label)
    for k in range(3):
        rect(d, (x0 + 6 + k * (x1 - x0) // 3, top - 6, x0 + 12 + k * (x1 - x0) // 3 + 14, top - 3), '#ffffff')
    for y in range(top + 4, base - 4, 14):
        rect(d, (x0 + 2, y + 10, x1 - 2, y + 11), '#9a9ea6')
        x = x0 + 4
        while x < x1 - 6:
            w = rng.randint(3, 7)
            h = rng.randint(5, 9)
            c = PRODUCT[rng.randint(len(PRODUCT))]
            rect(d, (x, y + 10 - h, x + w - 1, y + 9), c)
            line(d, (x, y + 10 - h, x + w - 1, y + 10 - h), mix(c, '#ffffff', .35))
            px(d, x + w // 2, y + 10 - h + 2, mix(c, '#ffffff', .6))
            x += w + 1
        rect(d, (x0 + 2, y + 12, x1 - 2, y + 13), '#f8f8f0')
        for px_ in range(x0 + 6, x1 - 8, 18):
            rect(d, (px_, y + 12, px_ + 6, y + 13), '#f0c830')
    return im


def supermarket():
    W, G = 640, 132
    im = new(W, 180, '#f2ecdc')
    d = ImageDraw.Draw(im)
    im = grad(im, (0, 0, W, G), ('#f4eedf', '#ece4d0', '#e2d8c2'))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 10), '#d8d2c4')
    for x in range(20, W, 80):                                   # 日光灯
        rect(d, (x, 3, x + 44, 5), '#fffef4')
        line(d, (x, 6, x + 44, 6), '#c8c2b4')
    for x, c, t in ((40, '#e8483c', 6), (200, '#f0a020', 5), (360, '#3a8ad8', 6), (520, '#4aa868', 4)):   # 吊着的促销牌
        line(d, (x + 14, 10, x + 14, 18), '#8a8a8a')
        rect(d, (x, 18, x + 30, 30), c)
        rect(d, (x + 2, 20, x + 28, 28), '#fffaf0')
        for k in range(t):
            rect(d, (x + 4 + k * 4, 22, x + 6 + k * 4, 26), c)
    rect(d, (0, G - 26, W, G), '#d8ccb4')                         # 踢脚线那一段
    line(d, (0, G - 26, W, G - 26), '#c4b8a0')
    # 入口自动门（左）
    rect(d, (6, 40, 58, G), '#8a8e96')
    for k in range(2):
        rect(d, (9 + k * 25, 43, 31 + k * 25, G), '#b8d4e4')
        for i in range(0, 20, 6):
            line(d, (11 + k * 25 + i, 46, 15 + k * 25 + i, 52), '#e0eef6')
    rect(d, (6, 36, 58, 40), '#3a8ad8')
    # 货架：调味料 / 零食 / 日用品
    im = shelf(im, 76, 206, 54, G - 2, 1, '#e8483c')
    im = shelf(im, 222, 352, 54, G - 2, 2, '#f0a020')
    im = shelf(im, 368, 420, 54, G - 2, 3, '#a070d0')
    d = ImageDraw.Draw(im)
    # 冷柜（玻璃门、里面亮）+ 旁边的水槽
    rect(d, (430, 46, 516, G), '#c4c8d0')
    rect(d, (432, 38, 514, 46), '#3a8ad8')
    rect(d, (440, 40, 506, 44), '#ffffff')
    for k in range(3):
        x0 = 434 + k * 27
        rect(d, (x0, 48, x0 + 25, G - 4), '#dcecf6')
        for y in range(54, G - 8, 14):
            rect(d, (x0 + 1, y + 10, x0 + 24, y + 10), '#a8b8c8')
            for j in range(5):
                rect(d, (x0 + 2 + j * 5, y + 4, x0 + 5 + j * 5, y + 9), ['#f4f4ec', '#f8f0d8', '#e8f0f8', '#f0e0c8'][(j + k + y) % 4])
        line(d, (x0 + 22, 52, x0 + 22, G - 8), '#ffffff')
    rect(d, (522, 98, 548, 112), '#c8ccd4')                        # 水槽
    rect(d, (524, 100, 546, 106), '#7a8a9a')
    rect(d, (533, 84, 535, 98), '#a8acb4')
    rect(d, (533, 84, 540, 86), '#a8acb4')
    rect(d, (539, 86, 540, 88), '#a8acb4')
    rect(d, (528, 112, 542, G), '#b0b4bc')
    # 收银台（右）
    rect(d, (566, 96, 634, G + 6), '#c8a07a')
    rect(d, (566, 96, 634, 100), '#e0c09a')
    rect(d, (590, 78, 618, 96), '#4a4e58')
    rect(d, (593, 80, 615, 88), '#a8d8b8')
    rect(d, (596, 89, 612, 94), '#6a6e78')
    rect(d, (624, 70, 626, 96), '#8a8a8a')
    rect(d, (618, 62, 632, 70), '#e8483c')
    # 地板（白灰格子）
    for y in range(G, 180, 8):
        for x in range(0, W, 16):
            c = '#e8e6e0' if ((x // 16) + (y // 8)) % 2 else '#d6d4cc'
            rect(d, (x, y, x + 15, y + 7), c)
    line(d, (0, G, W, G), '#b8b0a0')
    for x in range(0, W, 40):                                     # 地板反光
        line(d, (x + 6, G + 4, x + 14, G + 4), '#f8f8f4')
    meta = dict(pack='prologue', w=W, ground=150, walk=[140, 176],
                anchors=dict(soy=[130, 150], snacks=[288, 150], detergent=[394, 150], tofu=[474, 150], sink=[535, 146],
                             register=[600, 150], entrance=[32, 150], walk_x=[12, 628]),
                layers=[{'type': 'pano', 'image': 'bg/supermarket/room', 'k': 1, 'x': 0, 'y': 0}], fg=[])
    preview('supermarket', {'room': im}, ['room'], W)
    return save_layers('supermarket', {'room': im}, meta)


# ============================================================ 东方家外面 higashikata_eve / _night / _rain（640 宽）
def higashikata_near(var):
    W, G = 640, 138
    lit = '#ffe2a0' if var == 'night' else None
    near = new(W, 180)
    # 邻居
    near = house(near, -10, G - 8, 110, 74, wall='#dcd4c8', wall2='#bcb4a6', seed=31, lit=lit,
                 roof=('#4a5a50', '#36443c', '#62766a', '#222c26'))
    near = house(near, 500, G - 8, 120, 80, wall='#e2dccf', wall2='#c4bcae', seed=32, lit=lit,
                 roof=('#5a4a44', '#423632', '#76625a', '#2a2220'))
    d = ImageDraw.Draw(near)
    # 东方家：两层，米白墙、红褐屋顶、一楼大窗（客厅）
    x0, x1, top = 160, 440, 40
    rect(d, (x0, top, x1, G - 6), '#efe6d6')
    for yy in range(top + 2, G - 6, 4):
        line(d, (x0, yy, x1, yy), '#e2d8c6')
    rect(d, (x0, top, x0 + 2, G - 6), '#d0c4b0')
    rect(d, (x1 - 3, top, x1, G - 6), '#d0c4b0')
    near = tiled_roof(near, x0, x1, top - 20, top, ('#8a4a3a', '#6a362a', '#a8604e', '#40201a'))
    near = tiled_roof(near, x0 + 2, x1 - 2, top + 40, top + 46, ('#8a4a3a', '#6a362a', '#a8604e', '#40201a'), overhang=3)
    d = ImageDraw.Draw(near)
    for wx in (180, 250, 330, 390):
        window(d, (wx, top + 10, wx + 26, top + 30), glass=('#8eb8d2', '#c0dcea'), curtain='#e8b8a8' if wx == 250 else None,
               lit=lit)
    # 客厅大窗
    window(d, (176, G - 52, 262, G - 16), glass=('#8eb8d2', '#c0dcea'), curtain='#e8d0a0', lit=lit)
    line(d, (219, G - 52, 219, G - 16), '#e8e4dc')
    rect(d, (174, G - 15, 264, G - 13), '#d0c4b0')
    # 玄关：门 + 门灯 + 伞架
    rect(d, (360, G - 48, 392, G - 6), '#6a4a34')
    rect(d, (363, G - 45, 389, G - 8), '#7e5a40')
    line(d, (376, G - 45, 376, G - 8), '#8e6a4e')
    px(d, 372, G - 26, '#e8c860')
    rect(d, (356, G - 52, 396, G - 49), '#6a362a')
    rect(d, (398, G - 46, 403, G - 40), '#fff0b0' if var == 'night' else '#e8e0c8')
    rect(d, (396, G - 22, 404, G - 6), '#4a5a6a')               # 伞架
    line(d, (397, G - 30, 398, G - 22), '#2a3a5a')
    line(d, (401, G - 32, 401, G - 22), '#5a2a2a')
    # 门前的矮墙 + 门柱 + 邮箱
    near = block_wall(near, 100, 300, G - 20, G, cols=('#d0c8ba', '#b4ac9e', '#968e82', '#e6e0d4'))
    near = block_wall(near, 340, 500, G - 20, G, cols=('#d0c8ba', '#b4ac9e', '#968e82', '#e6e0d4'))
    near = hedge(near, 100, 300, G - 30, G - 20, seed=33)
    near = hedge(near, 412, 500, G - 30, G - 20, seed=34)
    d = ImageDraw.Draw(near)
    for gx in (300, 334):
        rect(d, (gx, G - 30, gx + 6, G), '#a8a094')
        rect(d, (gx - 1, G - 32, gx + 7, G - 30), '#c4bcae')
    rect(d, (286, G - 30, 298, G - 20), '#c83a34')                # 邮箱
    rect(d, (287, G - 28, 297, G - 26), '#2a2a2a')
    rect(d, (291, G - 20, 293, G - 8), '#5a5a5e')
    rect(d, (302, G - 26, 304, G - 18), '#f0ece0')                 # 门牌「东方」
    # 路灯
    near = street_lamp(near, 470, G + 2, 76, on=(var == 'night'))
    near = pole(near, 120, G + 2, 124)
    near = wires(near, [(120, G - 115), (640, G - 120)], sag=10)
    near = sidewalk(near, 0, W, G, 162)
    near = asphalt(near, 0, W, 162, 180)
    return near


def lamp_glow(w, bulb, ground):
    """路灯光晕（引擎用 lighter 叠加，颜色本身就是亮度）：灯泡一圈晕、往下一道淡淡的光锥、地上一摊光。
    强度场分 6 档、用 4×4 Bayer 抖动过渡：一整块实心圆叠上去会像个肥皂泡，抖动出来的渐变才像光"""
    bx, by = bulb
    yy, xx = np.mgrid[0:180, 0:w].astype(float)
    # 灯泡周围：横 22、竖 18 的椭圆，往外衰减
    r = np.sqrt(((xx - bx) / 22) ** 2 + ((yy - by) / 18) ** 2)
    f = np.clip(1 - r, 0, 1) ** 1.6
    # 光锥：灯泡到地面，越往下越宽、越淡，两边 6 px 羽化
    t = np.clip((yy - by) / max(1, ground - by), 0, 1)
    half = 5 + 30 * t
    edge = np.clip((half - np.abs(xx - bx)) / 6, 0, 1)
    cone = np.where((yy > by) & (yy <= ground + 2), 0.22 * (1 - 0.35 * t) * edge, 0)
    # 地上的光斑
    d = np.sqrt(((xx - bx) / 36) ** 2 + ((yy - ground) / 8) ** 2)
    pool = 0.45 * np.clip(1 - d, 0, 1) ** 1.2
    f = np.clip(f + cone + pool, 0, 1)
    levels = 6
    bay = np.tile(BAYER, (180 // 4 + 1, w // 4 + 1))[:180, :w]
    fq = np.floor(f * levels + bay) / levels
    fq = np.clip(fq, 0, 1)
    col = np.array([160, 136, 68], float)
    a = np.zeros((180, w, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * col, 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def higashikata_variant(var):
    W = 640
    if var == 'eve':
        far = sky_far(480, seed=9, cols=('#f0a070', '#f4b480', '#f8c89a', '#fadab4'), sea=False)
        far = tint(far, (1.0, .9, .82))
        near = tint(higashikata_near('eve'), (1.0, .9, .8), (10, 0, 0))
        extra = [{'type': 'tint', 'color': '#ff8040', 'alpha': 0.12}]
    elif var == 'night':
        far = sky_far(480, seed=9, cols=('#0e1430', '#16204a', '#202c5a', '#2a3866'), sea=False, night=True)
        far = tint(far, (.55, .6, .85))
        near = higashikata_near('night')
        a = np.array(near).astype(float)
        lit = (a[..., 0] > 240) & (a[..., 1] > 200) & (a[..., 2] < 200) & (a[..., 3] > 0)
        a[..., :3] = a[..., :3] * np.array([.32, .36, .55])
        near2 = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
        b = np.array(near2)
        b[lit] = (255, 226, 150, 255)
        near = Image.fromarray(b, 'RGBA')
        glow = new(W, 180)
        gd = ImageDraw.Draw(glow)
        for r, al in ((26, 40), (18, 60), (10, 90)):
            ellipse(gd, (478 - r, 62 - r * .5 + 40, 478 + r, 62 + r + 40), (90, 80, 40, al))
        extra = []
    else:   # rain
        far = sky_far(480, seed=9, cols=('#6a7484', '#7c8696', '#8e98a6', '#a0a8b4'), sea=False, night=True)
        near = tint(higashikata_near('rain'), (.62, .66, .76), (0, 4, 14), desat=.35)
        near = rain_ground(near, 140, 180, 3, '#8a96ae')
        for cx, cy, w in ((90, 166, 30), (250, 172, 40), (520, 168, 36), (600, 175, 24)):
            near = puddle(near, cx, cy, w)
        extra = [{'type': 'tint', 'color': '#203050', 'alpha': 0.12}]
    key = 'higashikata_' + var
    fg = []
    if var == 'rain':
        fg = [{'type': 'strip', 'image': f'bg/{key}/rain', 'n': 10, 'fps': 14, 'screen': True, 'x': 0, 'y': 0, 'w': 320, 'h': 180,
               'alpha': 0.8, 'key': 'rain'},
              {'type': 'strip', 'image': f'bg/{key}/splash', 'n': 6, 'fps': 12, 'screen': True, 'x': 0, 'y': 142, 'w': 320, 'h': 34,
               'key': 'rain'}]
    meta = dict(pack='prologue', w=W, ground=150, walk=[144, 174],
                anchors=dict(door=[376, 146], mailbox=[292, 148], umbrella=[400, 148], window=[219, 104], puddle=[250, 168],
                             lamp=[474, 140], crossroad=[600, 152], gate=[317, 148], walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': f'bg/{key}/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': f'bg/{key}/near', 'k': 1, 'x': 0, 'y': 0}] + extra, fg=fg)
    layers = {'far': far, 'near': near}
    if var == 'rain':
        layers['rain'] = rain_strip(320, 180, n=10, near=60, far=44, length=(8, 4), slant=-0.2, cols=('#c8d4e8', '#8e9cb8'),
                                    alpha=(190, 130), seed=33)
        layers['splash'] = splash_strip(320, 34, n=6, count=14, col='#c8d4e8', seed=34)
    if var == 'night':
        layers['glow'] = lamp_glow(W, (479, 62), 153)
        meta['layers'].append({'type': 'glow', 'image': f'bg/{key}/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.08})
        stars = [[int(x), int(y), 1 + (i % 3) * .6, i * .7, i % 7 == 0, '#ffffff'] for i, (x, y) in
                 enumerate(zip(np.random.RandomState(4).randint(0, 320, 40), np.random.RandomState(5).randint(4, 70, 40)))]
        meta['layers'].insert(1, {'type': 'stars', 'list': stars, 'k': 0})
    preview(key, {'far': far.resize((W, 180), Image.NEAREST), 'near': near}, ['far', 'near'], W)
    save_layers(key, layers, meta)
    return meta


def higashikata():
    return {('higashikata_' + v): higashikata_variant(v) for v in ('eve', 'night', 'rain')}


# ============================================================ 东方家客厅 higashikata_living（480 宽）
#   左：电话桌 + 日历（加湿器道具站在它前面）；窗（外面下雨，窗里另有一条动的雨帧）；一段空墙（打墙放汽的地方）；
#   沙发 + 外公的遗照（黑缎带）+ 挂钟；电视柜；隔断柱；右边是厨房：吊柜、瓷砖、水槽、炉子上的水壶、冰箱。
LIV = dict(paper='#eadfc6', paper2='#e1d4b8', paper3='#d6c8a8', ceil='#cbbb9a', ceil2='#b8a684',
           wd='#6a4a30', wm='#8a6644', wl='#a8805a', wh='#c49a6c',
           wain='#a07c56', wain_in='#946f4a', wain_hi='#bc9670', wain_lo='#7a5a3c')


def liv_floor(im, x0, x1, G):
    """木地板：越往下（离镜头越近）木条越宽；接缝错开；窗下有一块淡淡的反光"""
    d = ImageDraw.Draw(im)
    y, h, row = G, 3.0, 0
    tones = ['#b08458', '#a47a50', '#ba8e60', '#a98052']
    rng = np.random.RandomState(5)
    while y < 180:
        yb = min(180, int(round(y + h)))
        rect(d, (x0, int(y), x1, yb - 1), tones[row % 4])
        line(d, (x0, yb - 1, x1, yb - 1), '#7e5a3a')
        plank = int(40 + h * 6)
        off = rng.randint(0, plank)
        for x in range(x0 - off, x1, plank):
            if x > x0:
                line(d, (x, int(y), x, yb - 2), '#86603e')
                px(d, x + 1, int(y), '#c8a074')
        # 木纹：零星的短横线
        for _ in range(int((x1 - x0) / 18)):
            gx = rng.randint(x0, x1 - 6)
            gy = rng.randint(int(y), max(int(y) + 1, yb - 1))
            line(d, (gx, gy, gx + rng.randint(2, 6), gy), '#9a7048' if row % 2 else '#b88c5e')
        y += h
        h = min(9.0, h * 1.18)
        row += 1
    # 护墙板脚下的阴影
    im = dither_fill(im, (x0, G, x1, G + 2), '#7e5a3a', '#94704a', .5)
    return im


def liv_kitchen_floor(im, x0, x1, G):
    d = ImageDraw.Draw(im)
    y, h, row = G, 4.0, 0
    while y < 180:
        yb = min(180, int(round(y + h)))
        tw = int(8 + h * 1.6)
        for i, x in enumerate(range(x0 - (row % 2) * tw // 2, x1, tw)):
            rect(d, (max(x0, x), int(y), min(x1, x + tw - 1), yb - 1), '#e6e0d0' if (i + row) % 2 else '#cfc6b2')
        line(d, (x0, yb - 1, x1, yb - 1), '#b8ae98')
        y += h
        h = min(10.0, h * 1.2)
        row += 1
    return im


def higashikata_living():
    W, G = 480, 134
    P = LIV
    im = new(W, 180, P['paper'])
    # ---------------- 墙纸：竖条纹 + 顶上一圈阴影
    d = ImageDraw.Draw(im)
    for x in range(0, W, 8):
        line(d, (x, 10, x, G), P['paper2'])
        for y in range(14 + (x // 8) % 2 * 6, G, 12):
            px(d, x + 4, y, P['paper3'])
    im = grad(im, (0, 10, W, 26), (P['ceil'], P['paper2'], P['paper']))
    d = ImageDraw.Draw(im)
    # 天花板 + 线脚
    rect(d, (0, 0, W, 8), P['ceil2'])
    line(d, (0, 8, W, 8), P['wh'])
    line(d, (0, 9, W, 9), P['wl'])
    line(d, (0, 10, W, 10), P['ceil'])
    # ---------------- 护墙板（y 108–134）
    WT = 108
    rect(d, (0, WT, W, G), P['wain'])
    rect(d, (0, WT, W, WT + 2), P['wh'])
    line(d, (0, WT + 3, W, WT + 3), P['wain_lo'])
    for x in range(2, W, 30):
        rect(d, (x + 2, WT + 7, x + 26, G - 7), P['wain_in'])
        bevel(d, (x + 2, WT + 7, x + 26, G - 7), P['wain_lo'], P['wain_hi'])
    rect(d, (0, G - 4, W, G), P['wd'])
    line(d, (0, G - 4, W, G - 4), P['wm'])
    # ---------------- 左边：电话桌 + 日历
    rect(d, (14, 40, 36, 70), '#f6f2e8')                         # 日历（1999 年 4 月）
    rect(d, (14, 40, 36, 47), '#d84a3a')
    line(d, (16, 43, 30, 43), '#f6f2e8')
    for r in range(4):
        for c in range(6):
            px(d, 16 + c * 3.4, 50 + r * 4.5, '#6a6a70' if c else '#d84a3a')
    ellipse(d, (24, 57, 30, 62), '#e05a4a')
    ellipse(d, (25, 58, 29, 61), '#f6f2e8')
    px(d, 27, 59, '#6a6a70')
    rect(d, (24, 37, 26, 40), '#8a8a90')
    rect(d, (6, 104, 42, 108), P['wm'])                           # 电话桌
    line(d, (6, 104, 42, 104), P['wh'])
    rect(d, (8, 108, 10, G), P['wd'])
    rect(d, (38, 108, 40, G), P['wd'])
    rect(d, (8, 122, 40, 124), P['wm'])
    rect(d, (14, 96, 32, 104), '#e8e0c8')                          # 按键电话
    rect(d, (13, 93, 33, 97), '#d8ceb2')
    line(d, (13, 93, 33, 93), '#f4eedc')
    for r in range(2):
        for c in range(3):
            px(d, 20 + c * 3, 99 + r * 2, '#8a8270')
    line(d, (33, 96, 36, 104), '#6a6458')
    rect(d, (34, 100, 40, 104), '#f4f0e0')                          # 便条
    line(d, (35, 101, 39, 101), '#8a8aa0')
    # ---------------- 窗（56–140），外面雨天
    wx0, wy0, wx1, wy1 = 58, 26, 138, 94
    rect(d, (wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4), '#f2ead8')
    bevel(d, (wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4), '#fffaf0', '#cfc4ac')
    im = grad(im, (wx0, wy0, wx1, wy1), ('#5e6878', '#727c8c', '#86909e', '#98a2ae'))
    d = ImageDraw.Draw(im)
    # 窗外：对面人家的屋顶和墙（雨里发灰）
    d.polygon([(wx0, 66), (78, 58), (104, 58), (122, 66), (wx1, 66), (wx1, wy1), (wx0, wy1)], fill=C('#5a6272'))
    rect(d, (wx0, 66, wx1, wy1), '#7a8290')
    for xx in range(wx0, wx1, 4):
        line(d, (xx, 58 + abs(xx - 91) // 4, xx + 2, 58 + abs(xx - 91) // 4), '#4a5262')
    rect(d, (88, 72, 102, 84), '#a6aeba')
    line(d, (95, 72, 95, 84), '#7a8290')
    rect(d, (wx0, 86, wx1, wy1), '#4e5866')                        # 外面的围墙顶
    line(d, (wx0, 86, wx1, 86), '#6a7482')
    # 窗框十字 + 窗台
    rect(d, (97, wy0, 99, wy1), '#f2ead8')
    line(d, (wx0, 60, wx1, 60), '#f2ead8')
    rect(d, (wx0 - 8, wy1 + 4, wx1 + 8, wy1 + 8), '#e4dac4')
    line(d, (wx0 - 8, wy1 + 4, wx1 + 8, wy1 + 4), '#fffaf0')
    line(d, (wx0 - 8, wy1 + 8, wx1 + 8, wy1 + 8), '#b8ac92')
    # 窗台上的小盆栽
    rect(d, (118, wy1 - 2, 128, wy1 + 4), '#c06a4a')
    line(d, (118, wy1 - 2, 128, wy1 - 2), '#d88a68')
    for k, (dx, dy) in enumerate(((-3, -6), (0, -9), (3, -7), (5, -4), (-5, -3))):
        ellipse(d, (123 + dx - 3, wy1 - 2 + dy - 2, 123 + dx + 3, wy1 - 2 + dy + 2), '#4e8a52' if k % 2 else '#6aa66a')
    # 窗帘：两边束起来，三色褶
    for cx0, cx1, side in ((wx0 - 14, wx0 + 6, -1), (wx1 - 6, wx1 + 14, 1)):
        rect(d, (cx0, wy0 - 8, cx1, wy1 + 14), '#d68a7a')
        for i, x in enumerate(range(cx0, cx1, 4)):
            line(d, (x, wy0 - 8, x, wy1 + 14), '#b86a5c')
            line(d, (x + 1, wy0 - 8, x + 1, wy1 + 14), '#eaa898')
        # 束带
        rect(d, (cx0, 70, cx1, 72), '#a85648')
        # 下摆往里收
        d.polygon([(cx0, wy1 + 14), (cx1, wy1 + 14), (cx1 + side * 2, wy1 + 18), (cx0 + side * 2, wy1 + 18)], fill=C('#c47868'))
    rect(d, (wx0 - 16, wy0 - 12, wx1 + 16, wy0 - 8), P['wm'])        # 窗帘杆
    line(d, (wx0 - 16, wy0 - 12, wx1 + 16, wy0 - 12), P['wh'])
    ellipse(d, (wx0 - 19, wy0 - 13, wx0 - 14, wy0 - 7), P['wd'])
    ellipse(d, (wx1 + 14, wy0 - 13, wx1 + 19, wy0 - 7), P['wd'])
    # ---------------- 空墙 + 开关（打墙放汽在这一段）
    rect(d, (156, 80, 162, 88), '#f4f0e6')
    bevel(d, (156, 80, 162, 88), '#ffffff', '#c8c0ae')
    px(d, 159, 83, '#a8a090')
    # ---------------- 沙发（172–288）
    sx0, sx1 = 174, 288
    rect(d, (sx0 + 6, 84, sx1 - 6, 112), '#6c5e8c')                 # 靠背
    rect(d, (sx0 + 6, 84, sx1 - 6, 86), '#9488b4')
    for k in range(3):
        cx0 = sx0 + 8 + k * 34
        rect(d, (cx0, 88, cx0 + 31, 110), '#7a6c9a')                 # 靠垫
        line(d, (cx0, 88, cx0 + 31, 88), '#aca2c8')
        line(d, (cx0 + 31, 88, cx0 + 31, 110), '#5e527c')
        line(d, (cx0 + 2, 98, cx0 + 29, 98), '#6c5e8c')
    rect(d, (sx0 + 6, 110, sx1 - 6, 120), '#8478a6')                 # 坐垫
    line(d, (sx0 + 6, 110, sx1 - 6, 110), '#aca2c8')
    for k in (1, 2):
        line(d, (sx0 + 6 + k * 34, 111, sx0 + 6 + k * 34, 119), '#5e527c')
    rect(d, (sx0 + 4, 120, sx1 - 4, 128), '#5e527c')                 # 底座
    line(d, (sx0 + 4, 120, sx1 - 4, 120), '#6c5e8c')
    for ax in (sx0, sx1 - 10):                                       # 扶手
        rect(d, (ax, 98, ax + 10, 128), '#6c5e8c')
        ellipse(d, (ax - 1, 94, ax + 11, 104), '#7a6c9a')
        line(d, (ax + 1, 96, ax + 9, 96), '#aca2c8')
        line(d, (ax + 10, 100, ax + 10, 128), '#4a4064')
    for lx in (sx0 + 4, sx1 - 7):
        rect(d, (lx, 128, lx + 3, G - 1), P['wd'])
    # 抱枕（粉色，斜靠在左边）
    d.polygon([(sx0 + 12, 96), (sx0 + 26, 92), (sx0 + 30, 106), (sx0 + 15, 110)], fill=C('#e09ab0'))
    line(d, (sx0 + 12, 96, sx0 + 26, 92), '#f4c0d0')
    line(d, (sx0 + 15, 110, sx0 + 30, 106), '#c07890')
    # ---------------- 外公的遗照（黑缎带）+ 挂钟
    fx0, fy0 = 216, 30
    rect(d, (fx0, fy0, fx0 + 26, fy0 + 32), '#3a2a20')
    rect(d, (fx0 + 2, fy0 + 2, fx0 + 24, fy0 + 30), '#d8d2c2')
    rect(d, (fx0 + 3, fy0 + 3, fx0 + 23, fy0 + 29), '#b8bcc4')
    ellipse(d, (fx0 + 8, fy0 + 9, fx0 + 18, fy0 + 20), '#e8c4a0')    # 脸
    rect(d, (fx0 + 7, fy0 + 6, fx0 + 19, fy0 + 10), '#2a3a5a')       # 警帽
    rect(d, (fx0 + 6, fy0 + 10, fx0 + 20, fy0 + 11), '#1a2440')
    px(d, fx0 + 13, fy0 + 7, '#e8c860')
    line(d, (fx0 + 10, fy0 + 17, fx0 + 16, fy0 + 17), '#a8a8b0')     # 小胡子（灰）
    rect(d, (fx0 + 5, fy0 + 21, fx0 + 21, fy0 + 29), '#2a3a5a')      # 制服
    line(d, (fx0 + 13, fy0 + 21, fx0 + 13, fy0 + 29), '#e8e0d0')
    d.polygon([(fx0, fy0), (fx0 + 7, fy0), (fx0, fy0 + 7)], fill=C('#141014'))    # 黑缎带（两个上角）
    d.polygon([(fx0 + 26, fy0), (fx0 + 19, fy0), (fx0 + 26, fy0 + 7)], fill=C('#141014'))
    line(d, (fx0 + 13, fy0 - 4, fx0 + 2, fy0), '#5a5a5e')
    line(d, (fx0 + 13, fy0 - 4, fx0 + 24, fy0), '#5a5a5e')
    ellipse(d, (268, 30, 284, 46), '#7a5434')                         # 挂钟
    ellipse(d, (270, 32, 282, 44), '#f6f0e0')
    line(d, (276, 38, 276, 34), '#2a2a30')
    line(d, (276, 38, 279, 39), '#2a2a30')
    px(d, 276, 33, '#a8a090'); px(d, 281, 38, '#a8a090'); px(d, 276, 43, '#a8a090'); px(d, 271, 38, '#a8a090')
    # ---------------- 电视柜 + 显像管电视
    rect(d, (298, 102, 358, G - 1), P['wm'])
    line(d, (298, 102, 358, 102), P['wh'])
    rect(d, (302, 108, 326, 128), P['wd'])
    rect(d, (330, 108, 354, 128), P['wd'])
    rect(d, (304, 110, 324, 115), '#3a3a40')                          # 录像机
    line(d, (306, 112, 314, 112), '#1a1a1e')
    px(d, 321, 112, '#6ae070')
    for k in range(4):
        rect(d, (332 + k * 5, 112, 335 + k * 5, 126), ['#c84a3a', '#3a6ac8', '#e0c040', '#4aa060'][k])   # 录像带
    rect(d, (304, 66, 352, 102), '#4a4a50')                           # 电视
    rect(d, (306, 68, 350, 100), '#3a3a40')
    rect(d, (309, 71, 341, 97), '#26303a')
    rect(d, (310, 72, 340, 96), '#2e3c48')
    line(d, (312, 74, 322, 74), '#4a5e6e')
    line(d, (312, 75, 316, 75), '#4a5e6e')
    for yy in (76, 80, 84):
        px(d, 346, yy, '#8a8a90')
    rect(d, (344, 90, 348, 92), '#2a2a30')
    line(d, (328, 66, 318, 52), '#6a6a70')                             # 天线
    line(d, (330, 66, 340, 50), '#6a6a70')
    ellipse(d, (325, 63, 333, 67), '#3a3a40')
    # ---------------- 隔断柱（客厅 | 厨房）
    rect(d, (362, 0, 368, G), P['wd'])
    line(d, (363, 0, 363, G), P['wm'])
    line(d, (368, 0, 368, G), '#4e3622')
    # ---------------- 厨房（369–480）
    KX = 369
    rect(d, (KX, 10, W, WT), '#efe9da')
    for y in range(62, 98, 6):                                         # 瓷砖
        for x in range(KX + ((y // 6) % 2) * 3, W, 6):
            rect(d, (x, y, x + 5, y + 5), '#f4f2ec')
            line(d, (x, y + 5, x + 5, y + 5), '#d6d2c8')
            line(d, (x + 5, y, x + 5, y + 5), '#d6d2c8')
    rect(d, (KX, 14, 448, 48), '#d8c8a4')                              # 吊柜
    for x in range(KX + 2, 446, 26):
        rect(d, (x, 16, x + 23, 46), '#e4d6b4')
        bevel(d, (x, 16, x + 23, 46), '#f2e8cc', '#bcaa86')
        rect(d, (x + 19, 38, x + 20, 42), '#8a7a5a')
    rect(d, (KX, 48, 448, 50), '#bcaa86')
    rect(d, (420, 50, 448, 60), '#c8ccd2')                             # 抽油烟机
    line(d, (420, 60, 448, 60), '#a4a8b0')
    d.polygon([(420, 60), (448, 60), (444, 64), (424, 64)], fill=C('#b0b4bc'))
    # 挂勺子的横杆
    line(d, (KX + 6, 66, 414, 66), '#a4a8b0')
    for k, x in enumerate((376, 384, 392, 404)):
        line(d, (x, 66, x, 76 + k % 2 * 3), '#8a8e96')
        ellipse(d, (x - 2, 76 + k % 2 * 3, x + 2, 80 + k % 2 * 3), '#a4a8b0' if k != 2 else '#c89a6a')
    # 台面 + 地柜
    rect(d, (KX, 98, 450, 102), '#c8ccd2')
    line(d, (KX, 98, 450, 98), '#e8ecf0')
    line(d, (KX, 102, 450, 102), '#a4a8b0')
    rect(d, (KX, 103, 450, G - 1), '#d8c8a4')
    for x in range(KX + 2, 448, 27):
        rect(d, (x, 106, x + 24, G - 6), '#e4d6b4')
        bevel(d, (x, 106, x + 24, G - 6), '#f2e8cc', '#bcaa86')
        rect(d, (x + 11, 109, x + 14, 110), '#8a7a5a')
    rect(d, (KX, G - 5, 450, G - 1), '#8a7a5a')
    # 水槽（嵌在台面里）+ 水龙头 + 滴水
    rect(d, (382, 97, 416, 99), '#7a7e86')
    line(d, (382, 97, 416, 97), '#5a5e66')
    rect(d, (397, 82, 399, 97), '#b8bcc4')
    rect(d, (397, 80, 407, 82), '#b8bcc4')
    line(d, (397, 80, 407, 80), '#e0e4ea')
    rect(d, (406, 82, 407, 84), '#9a9ea6')
    px(d, 406, 88, '#9ac8f0')
    rect(d, (392, 88, 395, 90), '#c8ccd2')                             # 把手
    # 炉子 + 水壶
    rect(d, (420, 94, 448, 98), '#3a3a40')
    line(d, (420, 94, 448, 94), '#5a5a60')
    for bx in (426, 440):
        line(d, (bx - 3, 93, bx + 3, 93), '#2a2a30')
    rect(d, (424, 82, 438, 93), '#d8d8dc')                             # 水壶
    ellipse(d, (423, 80, 439, 86), '#e8e8ec')
    line(d, (425, 84, 425, 92), '#f4f4f6')
    line(d, (437, 84, 437, 92), '#a8a8b0')
    rect(d, (429, 77, 433, 80), '#2a2a30')
    line(d, (438, 86, 443, 81), '#c8c8cc')
    line(d, (443, 81, 444, 80), '#2a2a30')
    # 冰箱（450–480）
    rect(d, (450, 34, W - 1, G - 1), '#ece6d4')
    line(d, (450, 34, W - 1, 34), '#fffaee')
    line(d, (450, 34, 450, G - 1), '#d4ccb6')
    line(d, (450, 70, W - 1, 70), '#c8c0aa')
    rect(d, (453, 44, 454, 62), '#a8a294')
    rect(d, (453, 74, 454, 96), '#a8a294')
    rect(d, (462, 44, 470, 54), '#f8f4c8')                             # 冰箱贴 + 便条
    px(d, 466, 44, '#d84a3a')
    line(d, (463, 48, 469, 48), '#8a8aa0')
    line(d, (463, 51, 468, 51), '#8a8aa0')
    ellipse(d, (470, 80, 474, 84), '#4a8ad8')
    rect(d, (450, G - 4, W - 1, G - 1), '#a8a294')
    # ---------------- 地板：客厅木地板、厨房地砖
    im = liv_floor(im, 0, 365, G)
    im = liv_kitchen_floor(im, 366, W, G)
    d = ImageDraw.Draw(im)
    line(d, (365, G, 365, 180), '#6a4a30')
    # 地毯（沙发前）
    rx0, ry0, rx1, ry1 = 182, 146, 292, 168
    rect(d, (rx0, ry0, rx1, ry1), '#c89a62')
    rect(d, (rx0 + 2, ry0 + 2, rx1 - 2, ry1 - 2), '#8a4a4e')
    rect(d, (rx0 + 4, ry0 + 4, rx1 - 4, ry1 - 4), '#9a5458')
    for x in range(rx0 + 10, rx1 - 6, 12):
        cy = (ry0 + ry1) // 2
        d.polygon([(x, cy - 4), (x + 4, cy), (x, cy + 4), (x - 4, cy)], fill=C('#c89a62'))
        px(d, x, cy, '#8a4a4e')
    line(d, (rx0, ry1 + 1, rx1, ry1 + 1), '#7a5434')
    for x in range(rx0, rx1 + 1, 3):                                   # 流苏
        px(d, x, ry0 - 1, '#e0c08a')
        px(d, x, ry1 + 2, '#e0c08a')
    # 家具在地板上的影子
    im = dither_fill(im, (sx0 + 2, G, sx1 - 2, G + 3), '#86603e', '#9a7048', .5)
    im = dither_fill(im, (296, G, 360, G + 3), '#86603e', '#9a7048', .5)
    im = noise_specks(im, (0, G + 4, 365, 180), ['#c09468', '#9a7048'], 260, 9)
    # ---------------- 窗里的雨（动的，烘成 8 帧）
    winrain = rain_strip(wx1 - wx0, wy1 - wy0 - 8, n=8, near=16, far=12, length=(5, 3), slant=-0.18,
                         cols=('#c8d2e0', '#9aa6b8'), alpha=(200, 150), seed=21)
    meta = dict(pack='prologue', w=W, ground=150, walk=[142, 174],
                anchors=dict(humidifier=[26, 150], sink=[400, 146], kettle=[431, 84], wall=[159, 146], wallhole=[159, 104],
                             window=[98, 60], glovebox=[374, 98], glove=[380, 146], sofa=[231, 140], photo=[229, 46],
                             walk_x=[10, 470]),
                layers=[{'type': 'pano', 'image': 'bg/higashikata_living/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': 'bg/higashikata_living/winrain', 'n': 8, 'fps': 12, 'k': 1, 'x': wx0, 'y': wy0,
                         'w': wx1 - wx0, 'h': wy1 - wy0 - 8},
                        {'type': 'tint', 'color': '#f4f8fc', 'alpha': 0.62, 'key': 'fog'}], fg=[])
    prev = im.copy()
    prev.alpha_composite(winrain.crop((0, 0, wx1 - wx0, wy1 - wy0 - 8)), (wx0, wy0))
    preview('higashikata_living', {'room': prev}, ['room'], W)
    return save_layers('higashikata_living', {'room': im, 'winrain': winrain}, meta)


# ============================================================ 河堤边的雨路 angelo_road（1280 宽，下雨 / 雨停）
def angelo_near(after):
    W, G = 1280, 132
    near = new(W, 180)
    d = ImageDraw.Draw(near)
    # 河（护栏后面）+ 对岸
    rect(d, (0, 92, W, G - 12), '#6a7e92')
    for x in range(0, W, 9):
        line(d, (x, 100 + (x // 9) % 5 * 4, x + 5, 100 + (x // 9) % 5 * 4), '#8ea2b6')
    rect(d, (0, 84, W, 92), '#5a7258')
    near = noise_specks(near, (0, 84, W, 92), ['#6e8a6a', '#4a6048'], 400, 11)
    d = ImageDraw.Draw(near)
    # 对岸的小船、栈桥
    for bx in (250, 690, 1110):
        d.polygon([(bx, 96), (bx + 16, 96), (bx + 13, 99), (bx + 3, 99)], fill=C('#e8e4dc'))
        line(d, (bx + 3, 99, bx + 13, 99), '#8a8e96')
        rect(d, (bx + 6, 92, bx + 10, 96), '#c84a3a')
    rect(d, (430, 92, 470, 94), '#7a6a5a')
    for k in range(430, 471, 8):
        line(d, (k, 94, k, 100), '#5a4a3a')
    # 松树（种在河堤上，护栏后面）
    for x, h, sd in ((330, 92, 1), (372, 70, 2), (1150, 96, 3), (1190, 74, 4), (760, 82, 5)):
        near = pine(near, x, G - 2, h, seed=sd)
    d = ImageDraw.Draw(near)
    # 护栏
    rect(d, (0, G - 22, W, G - 19), '#c8ccd2')
    line(d, (0, G - 22, W, G - 22), '#e8ecf0')
    for x in range(0, W, 24):
        rect(d, (x, G - 22, x + 2, G - 4), '#a8acb4')
    rect(d, (0, G - 12, W, G - 10), '#b8bcc4')
    # 电线杆 + 电线
    for x in (60, 700, 1240):
        near = pole(near, x, G + 2, 118)
    near = wires(near, [(60, G - 110), (700, G - 112), (1240, G - 110)], sag=14)
    # 公交站（右段）+ 售货机 + 电话亭 + 限速牌 + 路灯
    near = bus_stop(near, 960, G + 2, roof_col='#6a7a8a')
    near = vending(near, 926, G + 2, body='#3a6ab8', accent='#eef2f8')
    near = phone_booth(near, 590, G + 2)
    d = ImageDraw.Draw(near)
    rect(d, (810, G - 36, 811, G + 2), '#8a8a90')                     # 限速 40
    ellipse(d, (803, G - 50, 818, G - 35), '#d83a34')
    ellipse(d, (805, G - 48, 816, G - 37), '#f4f4f0')
    digits(d, 807, G - 45, '40', '#2a3a8a')
    for x in (180, 520, 860, 1200):
        near = street_lamp(near, x, G + 2, 80)
    d = ImageDraw.Draw(near)
    # 河堤上的草
    rect(d, (0, G - 4, W, G), '#5a7a4a')
    near = noise_specks(near, (0, G - 4, W, G), ['#6e8e5a', '#4a6a3a'], 300, 12)
    near = sidewalk(near, 0, W, G, 150, cols=('#a8a6a2', '#94928e', '#bcbab4', '#84827e'))
    near = asphalt(near, 0, W, 150, 180)
    return near


def far_lighthouse(far, x, base):
    d = ImageDraw.Draw(far)
    d.polygon([(x - 40, base + 2), (x - 10, base - 8), (x + 16, base - 9), (x + 50, base + 2)], fill=C('#6e8a8e'))
    rect(d, (x, base - 26, x + 4, base - 8), '#f0ece4')
    rect(d, (x, base - 20, x + 4, base - 17), '#c84a3a')
    rect(d, (x - 1, base - 29, x + 5, base - 26), '#4a4e58')
    rect(d, (x + 1, base - 28, x + 3, base - 27), '#fff4c0')
    return far


def angelo_road():
    out = {}
    rain = rain_strip(320, 180, n=10, near=64, far=48, length=(8, 4), slant=-0.2, cols=('#c8d4e8', '#8e9cb8'), alpha=(190, 130), seed=31)
    splash = splash_strip(320, 34, n=6, count=16, col='#c8d4e8', seed=32)
    for var in ('rain', 'after'):
        W = 1280
        if var == 'rain':
            far = sky_far(800, seed=13, cols=('#5e6878', '#6e7888', '#7e8898', '#8e98a6'), sea=False, night=True)
            far = far_lighthouse(far, 430, 92)
            near = tint(angelo_near(False), (.6, .64, .74), (0, 4, 12), desat=.3)
            near = rain_ground(near, 134, 180, 5, '#8a96ae')
            extra = [{'type': 'tint', 'color': '#203050', 'alpha': 0.14}]
            fg = [{'type': 'strip', 'image': 'bg/angelo_rain/rain', 'n': 10, 'fps': 14, 'screen': True, 'x': 0, 'y': 0, 'w': 320, 'h': 180,
                   'alpha': 0.85, 'key': 'rain'},
                  {'type': 'strip', 'image': 'bg/angelo_rain/splash', 'n': 6, 'fps': 12, 'screen': True, 'x': 0, 'y': 142, 'w': 320, 'h': 34,
                   'key': 'rain'}]
        else:
            far = sky_far(800, seed=13, cols=('#9aaac0', '#b4c2d4', '#cad6e2', '#dde4ec'), sea=False)
            far = far_lighthouse(far, 430, 92)
            near = tint(angelo_near(True), (.86, .88, .94), desat=.1)
            extra = []
            fg = []
        for cx, cy, w in ((140, 168, 36), (420, 174, 46), (700, 166, 30), (1010, 172, 40), (1180, 166, 30)):
            near = puddle(near, cx, cy, w, cols=('#4e5e7a', '#8a9ab8', '#c8d4e8') if var == 'rain' else ('#7a8aa8', '#b0c0d8', '#e8f0f8'))
        key = 'angelo_' + var
        meta = dict(pack='prologue', w=W, ground=150, walk=[144, 176],
                    anchors=dict(rock=[1068, 150], stop=[990, 146], puddle=[420, 172], start=[60, 160], end=[1240, 160], walk_x=[8, 1272],
                                 booth=[599, 146], vending=[937, 148]),
                    layers=[{'type': 'pano', 'image': f'bg/{key}/far', 'k': 0.4, 'x': 0, 'y': 0},
                            {'type': 'pano', 'image': f'bg/{key}/near', 'k': 1, 'x': 0, 'y': 0}] + extra, fg=fg)
        layers = {'far': far, 'near': near}
        if var == 'rain':
            layers.update(rain=rain, splash=splash)
        pv = near.copy()
        if var == 'rain':
            for i in range(4):
                pv.alpha_composite(rain.crop((0, 0, 320, 180)), (i * 320, 0))
        preview(key, {'far': far.resize((W, 180), Image.NEAREST), 'near': pv}, ['far', 'near'], W)
        save_layers(key, layers, meta)
        out[key] = meta
    return out


# ============================================================ 杜王町地图 morioh_map（320×180，日历地图的底图）
def morioh_map():
    W, H = 320, 180
    im = new(W, H, '#efe4c8')
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(17)
    # 海（右下）+ 海岸线
    pts = [(W, 40), (282, 52), (270, 78), (258, 100), (240, 124), (222, 150), (208, H), (W, H)]
    d.polygon(pts, fill=C('#7ab0d8'))
    for i in range(60):
        x, y = rng.randint(220, W), rng.randint(50, H)
        if im.getpixel((x, y))[:3] == c3('#7ab0d8'):
            line(d, (x, y, x + 3, y), '#a8cce8')
    d.line(pts[:-2], fill=C('#5a8ab8'), width=1)
    # 山（左上）
    for cx, cy, r in ((40, 30, 34), (86, 18, 28), (20, 70, 22)):
        ellipse(d, (cx - r, cy - r * .7, cx + r, cy + r * .7), '#a8c48a')
        ellipse(d, (cx - r * .7, cy - r * .6, cx + r * .4, cy + r * .2), '#c0d8a0')
    # 河（从山里流到海）
    river = [(96, 0), (110, 30), (124, 58), (150, 84), (176, 110), (200, 136), (214, 158), (226, H)]
    d.line(river, fill=C('#7ab0d8'), width=5)
    d.line(river, fill=C('#a8cce8'), width=1)
    # 街区
    for _ in range(90):
        x, y = rng.randint(30, 250), rng.randint(40, 172)
        w, h = rng.randint(6, 14), rng.randint(5, 10)
        if im.getpixel((x, y))[:3] == c3('#efe4c8') and im.getpixel((min(W - 1, x + w), min(H - 1, y + h)))[:3] == c3('#efe4c8'):
            rect(d, (x, y, x + w, y + h), ['#e2d4b4', '#dccca8', '#e8dcc0'][rng.randint(3)])
    # 主干道 + 铁路
    ROADS = ([(0, 120), (100, 116), (180, 104), (250, 84), (290, 60)], [(60, 180), (90, 130), (130, 90), (170, 46), (200, 0)],
             [(0, 150), (120, 146), (210, 140)])
    for pts_ in ROADS:
        d.line(pts_, fill=C('#fffaf0'), width=3)
        d.line(pts_, fill=C('#d8c8a0'), width=1)
    rail = [(0, 92), (80, 88), (160, 76), (250, 62), (320, 50)]
    d.line(rail, fill=C('#4a4a50'), width=2)
    for i in range(0, 320, 6):
        t = i / 320
        x = i
        y = int(np.interp(x, [p[0] for p in rail], [p[1] for p in rail]))
        px(d, x, y, '#f0f0f0')
    # 沙滩（海岸线内侧一条浅黄）
    d.line([(p[0] - 3, p[1]) for p in pts[:-2]], fill=C('#f4e4b0'), width=2)
    # 桥：路跨过河的地方（求两条折线的交点）
    def cross(a, b):
        for (x1, y1), (x2, y2) in zip(a, a[1:]):
            for (x3, y3), (x4, y4) in zip(b, b[1:]):
                den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                if den == 0:
                    continue
                t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
                u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
                if 0 <= t <= 1 and 0 <= u <= 1:
                    return x1 + t * (x2 - x1), y1 + t * (y2 - y1)
        return None
    for road in ROADS:
        c = cross(road, river)
        if c:
            bx, by = int(round(c[0])), int(round(c[1]))
            rect(d, (bx - 4, by - 2, bx + 4, by + 2), '#fffaf0')
            line(d, (bx - 4, by - 2, bx + 4, by - 2), '#a89870')
            line(d, (bx - 4, by + 2, bx + 4, by + 2), '#a89870')
    # 车站（铁路上的红顶小房子）
    rect(d, (196, 60, 210, 66), '#f4f0e6')
    rect(d, (195, 57, 211, 60), '#c84a3a')
    line(d, (195, 66, 211, 66), '#8a7a5a')
    # 公园里的树
    for tx, ty in ((40, 34), (52, 40), (30, 44), (94, 22), (84, 28), (22, 74), (14, 66)):
        ellipse(d, (tx - 3, ty - 3, tx + 3, ty + 2), '#86a86a')
        px(d, tx - 1, ty - 2, '#c8dca8')
    # 指北针（左下）
    cx, cy = 24, 152
    ellipse(d, (cx - 11, cy - 11, cx + 11, cy + 11), '#e8dcc0')
    ellipse(d, (cx - 10, cy - 10, cx + 10, cy + 10), '#f4ead2')
    d.polygon([(cx, cy - 10), (cx + 3, cy), (cx, cy + 2), (cx - 3, cy)], fill=C('#c84a3a'))
    d.polygon([(cx, cy + 10), (cx + 3, cy), (cx, cy - 2), (cx - 3, cy)], fill=C('#5a5a64'))
    line(d, (cx - 10, cy, cx + 10, cy), '#b8a880')
    for r, row in enumerate(('1001', '1101', '1011', '1001')):         # 一个小小的 N
        for c_, v_ in enumerate(row):
            if v_ == '1':
                px(d, cx - 2 + c_, cy - 18 + r, '#5a4a34')
    # 纸张的边（双线）和折痕
    rect(d, (0, 0, W - 1, H - 1), None, '#9a8a64')
    rect(d, (3, 3, W - 4, H - 4), None, '#c8b890')
    line(d, (160, 4, 160, H - 5), '#e2d6b8')
    line(d, (4, 90, W - 5, 90), '#e2d6b8')
    im = noise_specks(im, (0, 0, W, H), ['#e6dabe', '#f4ead2'], 900, 18)
    # 四个角压暗一点（旧纸）
    a = np.array(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    k = np.clip((v - 1.1) * .25, 0, .18)
    a[..., :3] *= (1 - k[..., None] * np.array([1, 1.15, 1.6]))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    meta = dict(pack='prologue', w=W, ground=170, walk=[160, 170],
                anchors=dict(school=[170, 70], home=[118, 126], station=[203, 62], sea=[280, 140], gate=[170, 70], market=[96, 112], rock=[236, 120]),
                layers=[{'type': 'static', 'image': 'bg/morioh_map/map'}], fg=[])
    preview('morioh_map', {'map': im}, ['map'], W)
    return save_layers('morioh_map', {'map': im}, meta)


# ============================================================ 标题画面 title_morioh（320 宽：傍晚的杜王町，海、坡上的学校、樱花）
def title_morioh():
    W = 320
    far = sky_far(320, seed=21, cols=('#3a2a6a', '#8a4a8a', '#e8789a', '#ffb08a', '#ffd8a0'), sea=True, hills=True)
    far = tint(far, (1.0, .9, .92), (8, 0, 6))
    d = ImageDraw.Draw(far)
    # 落日
    ellipse(d, (104, 84, 136, 116), '#ffe8b0')
    ellipse(d, (108, 88, 132, 112), '#fff6d8')
    rect(d, (0, 106, W, 112), '#e88a7a')
    for x in range(70, 170, 3):
        px(d, x, 108 + (x // 3) % 2 * 2, '#ffe0a8')
    near = new(W, 180)
    d = ImageDraw.Draw(near)
    sil, sil2 = '#2a1430', '#3a1c40'
    rect(d, (0, 138, W, 180), sil)
    # 坡上的葡萄丘高中（剪影 + 亮着的窗）
    d.polygon([(150, 128), (190, 104), (250, 100), (300, 118), (320, 126), (320, 180), (150, 180)], fill=C(sil2))
    rect(d, (196, 86, 262, 104), sil)
    rect(d, (222, 74, 236, 86), sil)
    for x in range(200, 260, 7):
        rect(d, (x, 92, x + 3, 95), '#ffcf8a')
    # 近处的房子剪影 + 电线杆 + 电线
    xs = [0, 34, 70, 104, 136, 170, 210, 250, 286]
    for i, x in enumerate(xs):
        h = 22 + (i * 7) % 14
        w = 30 + (i * 5) % 10
        rect(d, (x, 150 - h, x + w, 180), sil)
        d.polygon([(x - 3, 150 - h), (x + w // 2, 150 - h - 9), (x + w + 3, 150 - h)], fill=C(sil))
        if i % 2 == 0:
            rect(d, (x + 6, 150 - h + 8, x + 11, 150 - h + 12), '#ffcf8a')
    for x in (60, 196):
        rect(d, (x, 60, x + 2, 180), sil)
        rect(d, (x - 8, 66, x + 10, 67), sil)
    near = wires(near, [(-10, 64), (61, 66), (197, 66), (330, 70)], sag=10, col=sil)
    # 两边的樱花（暗面偏紫，被夕阳照的一侧偏橙）
    pal = dict(d='#3e1638', m='#7a3460', l='#b8607e', x='#f09a98', trunk='#2a1430', trunk2='#1a0a20')
    near = sakura(near, 18, 182, 110, 90, seed=31, pal=pal, petals=False)
    near = sakura(near, 304, 184, 104, 84, seed=32, pal=pal, petals=False)
    d = ImageDraw.Draw(near)
    rect(d, (0, 168, W, 180), '#1e0e22')
    meta = dict(pack='title', w=W, ground=170, walk=[160, 176], anchors={},
                layers=[{'type': 'static', 'image': 'bg/title_morioh/far'},
                        {'type': 'clouds', 'clouds': [], 'span': 520},
                        {'type': 'static', 'image': 'bg/title_morioh/near'},
                        dict(PETALS, seed=45, n=30, k=0, colors=['#f0a0a8', '#ffd0b8'])], fg=[])
    preview('title_morioh', {'far': far, 'near': near}, ['far', 'near'], W)
    return save_layers('title_morioh', {'far': far, 'near': near}, meta)


SCENES = {'morioh_road': morioh_road, 'budou_gate': budou_gate, 'supermarket': supermarket, 'higashikata': higashikata,
          'higashikata_living': higashikata_living, 'angelo_road': angelo_road, 'morioh_map': morioh_map,
          'title_morioh': title_morioh}



def main(keys):
    path = os.path.join(LIB.META, 'bg.json')
    meta = LIB.load_json(path, {}) or {}
    for k in keys or SCENES:
        r = SCENES[k]()
        if isinstance(r, dict) and 'layers' in r:
            meta[k] = r
        else:
            meta.update(r)
        print('背景', k)
    LIB.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
