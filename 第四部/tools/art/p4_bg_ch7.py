# 第四部第7章（商店街 / 灰姑娘与枯萎穿心攻击）的背景：3 张，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   cinderella_salon 灰姑娘美容院（480）、tailor_shop 裁缝店里面（480）、morioh_avenue 裁缝店外的马路（960）。
#   约会那段直接用第2章的 morioh_grand_hotel（街角咖啡馆露天座，pack ch2），地图用序章的 morioh_map，不在这里重画。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_ch7.json（build_p4.py 会把 _meta/bg_*.json 并进 bg.json）。
#   用法：python3 第四部/tools/art/p4_bg_ch7.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   图层 pack 一律 'ch7'（打包成 data/img_bg_ch7.js，进第7章时才加载）。
#   招牌小字、地砖、遮阳篷这些零件和第2章（p4_bg_ch2.py）同一套画法；为了两条分支互不依赖，这里各抄了一份。
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import preview, save_layers, sky_far  # noqa: E402

PACK = 'ch7'

# ---------------------------------------------------------------- 小零件（同第2章）
LET = {'A': ['010', '101', '111', '101', '101'], 'B': ['110', '101', '110', '101', '110'], 'C': ['011', '100', '100', '100', '011'],
       'D': ['110', '101', '101', '101', '110'], 'E': ['111', '100', '110', '100', '111'], 'F': ['111', '100', '110', '100', '100'],
       'G': ['011', '100', '101', '101', '011'], 'H': ['101', '101', '111', '101', '101'], 'I': ['111', '010', '010', '010', '111'],
       'K': ['101', '101', '110', '101', '101'], 'L': ['100', '100', '100', '100', '111'], 'M': ['10001', '11011', '10101', '10001', '10001'],
       'N': ['1001', '1101', '1011', '1001', '1001'], 'O': ['010', '101', '101', '101', '010'], 'P': ['110', '101', '110', '100', '100'],
       'R': ['110', '101', '110', '101', '101'], 'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'],
       'U': ['101', '101', '101', '101', '111'], 'V': ['101', '101', '101', '101', '010'], 'Y': ['101', '101', '010', '010', '010'],
       'W': ['10001', '10001', '10101', '11011', '10001'],
       '-': ['000', '000', '111', '000', '000'], ' ': ['000'] * 5, '.': ['000', '000', '000', '000', '010'],
       '¥': ['101', '010', '111', '010', '010']}


def letters(d, x, y, text, col, gap=1):
    cx = x
    for ch in text:
        g = LET.get(ch) or DIG.get(ch) or ['000'] * 5
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == '1':
                    px(d, cx + c, y + r, col)
        cx += len(g[0]) + gap
    return cx - x - gap


def text_w(text, gap=1):
    return sum(len((LET.get(ch) or DIG.get(ch) or ['000'])[0]) + gap for ch in text) - gap


def poly(d, pts, col):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=C(col))


def kanji(im, x, y, text, col, vertical=False, size=12):
    """文泉驿点阵正黑 12 px 点阵字（招牌用）；vertical = 竖排"""
    if vertical:
        cy, w = y, 0
        for ch in text:
            m = LIB.text_mask(ch, LIB.WQY, size, index=1)
            im.paste(C(col), (int(x + (size - m.width) // 2), int(cy)), m)
            cy += m.height + 1
            w = max(w, m.width)
        return w, cy - y - 1
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    im.paste(C(col), (int(x), int(y)), m)
    return m.width, m.height


def kanji_size(text, size=12):
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    return m.width, m.height


def signboard(im, x0, x1, y, h, bg, edge, text=None, col='#ffffff', latin=None):
    d = ImageDraw.Draw(im)
    rect(d, (x0, y, x1, y + h), edge)
    rect(d, (x0 + 1, y + 1, x1 - 1, y + h - 1), bg)
    line(d, (x0 + 1, y + 1, x1 - 1, y + 1), mix(bg, '#ffffff', .3))
    if text:
        tw, th = kanji_size(text)
        kanji(im, (x0 + x1) // 2 - tw // 2, y + (h - th) // 2 + 1, text, col)
    if latin:
        letters(d, (x0 + x1) // 2 - text_w(latin) // 2, y + (h - 5) // 2 + 1, latin, col)


def awning(im, x0, x1, y, depth, cols, scallop=True):
    d = ImageDraw.Draw(im)
    for i in range(depth):
        for x in range(x0 - i // 3, x1 + i // 3 + 1):
            k = ((x - x0 + 200) // 6) % 2
            px(d, x, y + i, mix(cols[k], '#000000', .08 * (i / depth)))
    if scallop:
        for x in range(x0 - depth // 3, x1 + depth // 3, 6):
            ellipse(d, (x, y + depth - 2, x + 5, y + depth + 2), cols[((x - x0 + 200) // 6) % 2])
    line(d, (x0, y, x1, y), mix(cols[0], '#ffffff', .4))


def window_row(im, x0, x1, y, h, G_, wall, seed=0, win='#9cc0d4', step=30):
    """楼上一排窗（窗帘、晾的毛巾、空调外机随机）"""
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    n = max(1, (x1 - x0 - 10) // step)
    gap = (x1 - x0 - n * 22) // (n + 1)
    for i in range(n):
        wx = x0 + gap + i * (22 + gap)
        curtain = ['#e8d8b0', '#c8d8e8', None, '#f0c8c8'][rng.randint(4)]
        window(d, (wx, y, wx + 22, y + h), frame='#f4f2ec', glass=(win, mix(win, '#ffffff', .4)), curtain=curtain)
        if rng.rand() < .4:
            rect(d, (wx + 24, y + 6, wx + 31, y + 12), '#e4e4de')
            ellipse(d, (wx + 25, y + 7, wx + 29, y + 11), '#a4a4a8')


def floor_tiles(im, x0, x1, G, cols=('#f4f0ec', '#2e2a34'), grout='#8a8490', seed=0):
    """黑白格地砖（美容院）：越往下格子越大，像往镜头这边铺过来"""
    d = ImageDraw.Draw(im)
    y, h, row = float(G), 4.0, 0
    while y < 180:
        yb = min(180, int(round(y + h)))
        tw = int(round(h * 2.2))
        off = 0 if row % 2 == 0 else 0
        for i, x in enumerate(range(x0 - off, x1, tw)):
            c = cols[(i + row) % 2]
            rect(d, (max(x0, x), int(y), min(x1, x + tw - 1), yb - 1), c)
            line(d, (max(x0, x), int(y), min(x1, x + tw - 1), int(y)), mix(c, '#ffffff', .25))
        line(d, (x0, yb - 1, x1, yb - 1), grout)
        y += h
        h = min(12.0, h * 1.22)
        row += 1
    return im


def wood_floor(im, x0, x1, G, tones=('#9a7048', '#8e6640', '#a47a50', '#946a44'), seam='#6a4a30', seed=5):
    d = ImageDraw.Draw(im)
    y, h, row = float(G), 3.0, 0
    rng = np.random.RandomState(seed)
    while y < 180:
        yb = min(180, int(round(y + h)))
        rect(d, (x0, int(y), x1, yb - 1), tones[row % 4])
        line(d, (x0, yb - 1, x1, yb - 1), seam)
        plank = int(40 + h * 6)
        off = rng.randint(0, plank)
        for x in range(x0 - off, x1, plank):
            if x > x0:
                line(d, (x, int(y), x, yb - 2), mix(seam, tones[0], .5))
        for _ in range(int((x1 - x0) / 18)):
            gx = rng.randint(x0, x1 - 6)
            gy = rng.randint(int(y), max(int(y) + 1, yb - 1))
            line(d, (gx, gy, gx + rng.randint(2, 6), gy), mix(tones[row % 4], '#000000', .1))
        y += h
        h = min(9.0, h * 1.18)
        row += 1
    return dither_fill(im, (x0, G, x1, G + 2), seam, tones[1], .5)


def shimmer_strip(w, h, n=6, cols=('#ffb060', '#ffe0a0'), seed=0, density=.2):
    """热源上方的热气：一列列往上飘的抖动小点（半透明），n 帧一圈"""
    rng = np.random.RandomState(seed)
    out = new(w * n, h)
    d = ImageDraw.Draw(out)
    cols_x = [(x, rng.uniform(0, 2 * np.pi), rng.uniform(.6, 1.4)) for x in range(0, w, 2)]
    for f in range(n):
        for x, ph, sp in cols_x:
            for y in range(h):
                k = 1 - y / h                                                  # 越往下（离热源越近）越密
                a = math.sin(ph + y * .45 * sp - 2 * math.pi * f / n)
                if a > .82 and rng.rand() < density * 4 * (1 - k * .4):
                    dx = int(round(math.sin(y * .3 + ph + 2 * math.pi * f / n)))
                    d.point((f * w + x + dx, y), fill=C(cols[(x + y) % 2], int(130 + 100 * (y / h))))
    return out


def smoke_strip(w=10, h=28, n=8, col='#c8c8cc', seed=0):
    """一缕细烟：从底部中间往上飘、左右摆、越高越淡"""
    out = new(w * n, h)
    d = ImageDraw.Draw(out)
    for f in range(n):
        for k in range(3):
            for i in range(h):
                y = h - 1 - i
                t = (i + (f * h / n) + k * h / 3) % h
                if t > h - 2:
                    continue
                x = w / 2 + math.sin(t * .28 + k * 2.1) * (1 + t / h * (w / 2 - 2))
                a = int(230 * (1 - t / h))
                if a > 40:
                    X, Y = f * w + int(round(x)), int(h - 1 - t)
                    d.point((X, Y), fill=C(col, a))
                    if t > h * .35 and (i + k) % 2 == 0:
                        d.point((X + 1, Y), fill=C(col, a // 2))
    return out


# ============================================================ 灰姑娘美容院 cinderella_salon（480 宽，室内）
#   左：玻璃门（门外是马路）、前台（玫瑰、收银机）、墙上的价目表；中：两组镜台（金框椭圆镜、化妆台、粉色丝绒美容椅），
#   第二组化妆台上放着那支红口红；右：酒红丝绒墙上挂着一排 6 张“脸”（解谜用），下面是辻彩的工作台和一张躺椅，最右是通里间的帘子。
#   吊灯两盏（glow 层微微闪）；镜面上一道反光扫过（strip）。key 'night'：打烊后的暗蓝罩色（吉良逼辻彩那段）。
SAL = dict(wall='#eadcea', wall2='#dccbdc', wall3='#f4eaf2', ceil='#d2c0d4', ceil2='#b8a4bc', wain='#f8f4f6', wain2='#e4dce4',
           gold='#d8b05a', gold2='#a8823a', gold3='#f4dc90', velvet='#6a1e3a', velvet2='#4e1428', velvet3='#8a3050',
           pink='#e88aa8', pink2='#c0607e', pink3='#f6b4c8')

# 6 张脸：(眉形, 眼角, 嘴角, 刘海)；第 4 张（index 3）是由花子原来的脸：平直细长、尾巴微微上挑的眉，眼角上挑，嘴角平，齐刘海
FACES = [dict(brow='arch', eye='down', mouth='up', bang='side', skin='#f6e2d4'),
         dict(brow='thick', eye='round', mouth='wide', bang='curl', skin='#f2dccc'),
         dict(brow='down', eye='down', mouth='down', bang='part', skin='#f8e6da'),
         dict(brow='sharp', eye='up', mouth='flat', bang='hime', skin='#f6e0d2'),
         dict(brow='thin', eye='up', mouth='up', bang='part', skin='#f4ded0'),
         dict(brow='sharp', eye='round', mouth='flat', bang='short', skin='#f8e4d6')]
YUKAKO_FACE = 3


def face_mask(d, x, y, spec, hair='#2a2230', hair2='#3e3448'):
    """一张 18×24 的“脸”：瓷白的脸 + 额前的头发，挂在金钩上。只画五官差别：眉形、眼角、嘴角、刘海"""
    sk = spec['skin']
    ellipse(d, (x + 1, y + 2, x + 17, y + 24), mix(sk, '#000000', .18))       # 脸的轮廓（下巴阴影）
    ellipse(d, (x + 1, y + 1, x + 17, y + 23), sk)
    line(d, (x + 3, y + 17, x + 5, y + 20), mix(sk, '#000000', .08))
    # 刘海
    b = spec['bang']
    if b == 'hime':                                                          # 齐刘海：一刀切平
        rect(d, (x + 1, y, x + 17, y + 7), hair)
        line(d, (x + 2, y + 1, x + 16, y + 1), hair2)
        for k in range(x + 3, x + 16, 3):
            px(d, k, y + 7, hair2)
        rect(d, (x, y + 3, x + 1, y + 20), hair)                               # 两边垂下来的头发
        rect(d, (x + 17, y + 3, x + 18, y + 20), hair)
    elif b == 'side':                                                        # 斜刘海：从左往右斜下
        poly(d, [(x + 1, y), (x + 17, y), (x + 17, y + 9), (x + 6, y + 4), (x + 1, y + 6)], hair)
        line(d, (x + 4, y + 2, x + 15, y + 6), hair2)
    elif b == 'part':                                                        # 中分
        poly(d, [(x + 1, y + 8), (x + 1, y + 1), (x + 17, y + 1), (x + 17, y + 8), (x + 13, y + 3), (x + 9, y + 1), (x + 5, y + 3)], hair)
        px(d, x + 9, y + 1, sk)
    elif b == 'curl':                                                        # 卷卷的刘海
        rect(d, (x + 1, y, x + 17, y + 3), hair)
        for k in range(x + 2, x + 17, 4):
            ellipse(d, (k - 1, y + 2, k + 3, y + 6), hair)
            px(d, k + 1, y + 3, hair2)
    elif b == 'short':                                                       # 碎短刘海
        rect(d, (x + 2, y, x + 16, y + 3), hair)
        for k in range(x + 2, x + 16, 2):
            px(d, k, y + 4 + (k % 3 == 0), hair)
    # 眉
    br = spec['brow']
    for side in (0, 1):
        ex = x + 4 if side == 0 else x + 11
        by = y + 9
        if br == 'arch':
            px(d, ex, by + 1, hair); px(d, ex + 1, by, hair); px(d, ex + 2, by, hair); px(d, ex + 3, by + 1, hair)
        elif br == 'thick':
            rect(d, (ex, by, ex + 3, by + 1), hair)
        elif br == 'down':                                                   # 八字眉（内高外低）
            if side == 0:
                px(d, ex, by + 1, hair); px(d, ex + 1, by + 1, hair); px(d, ex + 2, by, hair); px(d, ex + 3, by, hair)
            else:
                px(d, ex, by, hair); px(d, ex + 1, by, hair); px(d, ex + 2, by + 1, hair); px(d, ex + 3, by + 1, hair)
        elif br == 'sharp':                                                  # 平直细长，尾巴上挑
            if side == 0:
                px(d, ex - 1, by, hair); px(d, ex, by + 1, hair); px(d, ex + 1, by + 1, hair); px(d, ex + 2, by + 1, hair); px(d, ex + 3, by + 1, hair)
            else:
                px(d, ex, by + 1, hair); px(d, ex + 1, by + 1, hair); px(d, ex + 2, by + 1, hair); px(d, ex + 3, by + 1, hair); px(d, ex + 4, by, hair)
        elif br == 'thin':
            line(d, (ex, by + 1, ex + 3, by + 1), mix(hair, sk, .4))
    # 眼（闭着的，像面具）：一条线 + 眼角
    ey = y + 13
    e = spec['eye']
    for side in (0, 1):
        ex = x + 4 if side == 0 else x + 11
        line(d, (ex, ey, ex + 3, ey), '#3a2a2e')
        outer = ex if side == 0 else ex + 3
        if e == 'up':
            px(d, outer + (-1 if side == 0 else 1), ey - 1, '#3a2a2e')
        elif e == 'down':
            px(d, outer + (-1 if side == 0 else 1), ey + 1, '#3a2a2e')
        elif e == 'round':
            px(d, ex + 1, ey - 1, '#3a2a2e'); px(d, ex + 2, ey - 1, '#3a2a2e')
        px(d, ex + 1, ey + 2, mix(sk, '#e88a8a', .25))                         # 腮红一点
    # 鼻
    px(d, x + 9, y + 16, mix(sk, '#000000', .15))
    # 嘴
    my = y + 19
    m = spec['mouth']
    lip = '#c8505a'
    if m == 'up':
        line(d, (x + 7, my, x + 11, my), lip); px(d, x + 6, my - 1, lip); px(d, x + 12, my - 1, lip)
    elif m == 'down':
        line(d, (x + 7, my, x + 11, my), lip); px(d, x + 6, my + 1, lip); px(d, x + 12, my + 1, lip)
    elif m == 'wide':
        line(d, (x + 5, my, x + 13, my), lip); line(d, (x + 7, my + 1, x + 11, my + 1), mix(lip, '#000000', .2))
    else:
        line(d, (x + 7, my, x + 11, my), lip)


def salon_room():
    W, G = 480, 134
    P = SAL
    im = new(W, 180, P['wall'])
    d = ImageDraw.Draw(im)
    # 墙：淡紫底 + 小菱形暗纹
    for y in range(14, G, 8):
        for x in range((y // 8) % 2 * 6, W, 12):
            px(d, x, y, P['wall2'])
            px(d, x - 1, y + 1, P['wall3'])
            px(d, x + 1, y + 1, P['wall3'])
            px(d, x, y + 2, P['wall2'])
    im = grad(im, (0, 10, W, 26), (P['ceil'], P['wall2'], P['wall']))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 9), P['ceil2'])
    rect(d, (0, 9, W, 11), P['gold'])                                          # 顶角线（金）
    line(d, (0, 9, W, 9), P['gold3'])
    line(d, (0, 12, W, 12), P['wall2'])
    # 护墙板（白漆 + 金线）
    WT = 108
    rect(d, (0, WT, W, G), P['wain'])
    line(d, (0, WT, W, WT), P['gold'])
    line(d, (0, WT + 1, W, WT + 1), P['gold2'])
    for x in range(4, W, 26):
        rect(d, (x + 2, WT + 6, x + 22, G - 6), P['wain'])
        bevel(d, (x + 2, WT + 6, x + 22, G - 6), P['wain2'], '#ffffff')
    rect(d, (0, G - 3, W, G), P['wain2'])
    # ---------------- 入口（6–56）：金框玻璃双开门，门外是白天的马路
    dx0, dx1, dy0 = 8, 54, G - 82
    rect(d, (dx0 - 3, dy0 - 3, dx1 + 3, G), P['gold2'])
    rect(d, (dx0 - 2, dy0 - 2, dx1 + 2, G), P['gold'])
    im = grad(im, (dx0, dy0, dx1, G - 1), ('#a8d0ec', '#c8e0f0', '#d8d4c8'))
    d = ImageDraw.Draw(im)
    rect(d, (dx0, G - 22, dx1, G - 1), '#8a8a90')                              # 门外：人行道、对面的楼
    rect(d, (dx0, G - 50, dx0 + 20, G - 22), '#d8cfc0')
    rect(d, (dx0 + 24, G - 58, dx1, G - 22), '#c4ccd4')
    for wy in range(G - 54, G - 26, 8):
        rect(d, (dx0 + 28, wy, dx0 + 34, wy + 4), '#7e9cb8'); rect(d, (dx0 + 38, wy, dx0 + 44, wy + 4), '#7e9cb8')
    rect(d, (dx0 + 4, G - 46, dx0 + 14, G - 38), '#7e9cb8')
    line(d, ((dx0 + dx1) // 2, dy0, (dx0 + dx1) // 2, G - 1), P['gold'])       # 两扇门的中缝 + 门框
    for x in (dx0, dx1):
        line(d, (x, dy0, x, G - 1), P['gold2'])
    for k in range(3):                                                         # 玻璃反光
        line(d, (dx0 + 3 + k * 4, dy0 + 4, dx0 + 9 + k * 4, dy0 + 10), '#eef6fa')
        line(d, ((dx0 + dx1) // 2 + 3 + k * 4, dy0 + 6, (dx0 + dx1) // 2 + 8 + k * 4, dy0 + 11), '#eef6fa')
    for hx in ((dx0 + dx1) // 2 - 4, (dx0 + dx1) // 2 + 3):                  # 门把（金色竖条）
        rect(d, (hx, G - 50, hx + 1, G - 34), P['gold3'])
    letters(d, (dx0 + dx1) // 2 - text_w('SALON') // 2, dy0 + 18, 'SALON', '#f8f0f4')  # 门玻璃上的字
    line(d, ((dx0 + dx1) // 2 - 12, dy0 + 25, (dx0 + dx1) // 2 + 12, dy0 + 25), P['gold'])
    rect(d, (dx1 - 6, dy0 - 10, dx1 - 2, dy0 - 4), P['gold'])                  # 门铃
    ellipse(d, (dx1 - 7, dy0 - 5, dx1 - 1, dy0 + 1), P['gold3'])
    px(d, dx1 - 4, dy0 + 1, P['gold2'])
    # ---------------- 前台（66–124）+ 墙上的价目表
    cx0, cx1, ct = 66, 124, G - 30
    rect(d, (cx0, ct, cx1, G + 4), '#f8f4f6')
    rect(d, (cx0 - 2, ct - 3, cx1 + 2, ct), P['pink2'])
    line(d, (cx0 - 2, ct - 3, cx1 + 2, ct - 3), P['pink3'])
    for x in range(cx0 + 4, cx1 - 4, 14):
        rect(d, (x, ct + 4, x + 10, G), '#efe6ec')
        bevel(d, (x, ct + 4, x + 10, G), '#ddd0d8', '#ffffff')
    line(d, (cx0, G + 4, cx1, G + 4), P['gold2'])
    rect(d, (cx0 + 6, ct - 12, cx0 + 22, ct - 3), '#4a4450')                   # 收银机
    rect(d, (cx0 + 8, ct - 16, cx0 + 18, ct - 12), '#6a6470')
    rect(d, (cx0 + 9, ct - 15, cx0 + 17, ct - 13), '#9ae0a0')
    for k in range(3):
        px(d, cx0 + 9 + k * 3, ct - 8, '#c8c4cc')
    vx = cx1 - 16                                                              # 玻璃花瓶 + 一束红玫瑰
    rect(d, (vx, ct - 12, vx + 6, ct - 3), '#c8e4ec')
    line(d, (vx + 1, ct - 11, vx + 1, ct - 4), '#eef8fa')
    for k, (rx, ry) in enumerate(((-3, -20), (1, -23), (5, -21), (9, -18), (-1, -16), (7, -15), (3, -18))):
        line(d, (vx + 3, ct - 12, vx + 3 + rx // 2, ct + ry + 3), '#3a7a3a')
        ellipse(d, (vx + rx, ct + ry, vx + rx + 3, ct + ry + 3), '#c8203a')
        px(d, vx + rx + 1, ct + ry + 1, '#e85a6a')
    # 价目表：金框里一块深紫板，白字
    mx0, my0, mx1, my1 = 70, 52, 120, 96
    rect(d, (mx0 - 2, my0 - 2, mx1 + 2, my1 + 2), P['gold2'])
    rect(d, (mx0 - 1, my0 - 1, mx1 + 1, my1 + 1), P['gold'])
    rect(d, (mx0, my0, mx1, my1), '#3a2a44')
    tw, th = kanji_size('価格表')
    kanji(im, (mx0 + mx1) // 2 - tw // 2, my0 + 2, '価格表', P['gold3'])
    d = ImageDraw.Draw(im)
    for k, (name, price) in enumerate((('CUT', '3000'), ('MAKE', '5000'), ('ESTE', '8000'), ('VIP', '-----'))):
        y = my0 + 18 + k * 7
        letters(d, mx0 + 3, y, name, '#f4eaf2')
        letters(d, mx1 - 3 - text_w('¥' + price), y, '¥' + price, '#f4eaf2' if k < 3 else P['pink3'])
    # ---------------- 两组镜台（134–222、230–318）
    stations = []
    for i, sx in enumerate((134, 230)):
        cxm = sx + 44
        # 椭圆镜（金框），镜面里映着对面淡粉的墙，左上一道高光
        ellipse(d, (cxm - 24, 44, cxm + 24, 104), P['gold2'])
        ellipse(d, (cxm - 23, 45, cxm + 23, 103), P['gold'])
        ellipse(d, (cxm - 21, 47, cxm + 21, 101), P['gold3'])
        ellipse(d, (cxm - 20, 48, cxm + 20, 100), '#c8d4dc')
        im = grad(im, (cxm - 18, 50, cxm + 18, 98), ('#dce6ec', '#c8d4de', '#b4c2ce'))
        d = ImageDraw.Draw(im)
        # 把镜面以外 grad 涂到的角落补回金框
        for yy in range(50, 99):
            half = int(20 * math.sqrt(max(0, 1 - ((yy - 74) / 26) ** 2)))
            for xx in range(cxm - 18, cxm + 19):
                if abs(xx - cxm) > half:
                    px(d, xx, yy, P['gold3'] if abs(xx - cxm) <= half + 1 else P['gold'] if abs(xx - cxm) <= half + 2 else P['wall'])
        ellipse(d, (cxm - 12, 66, cxm + 12, 100), '#d8c4d4')                    # 镜子里：对面墙上一块粉
        rect(d, (cxm - 14, 92, cxm + 14, 100), '#b8aab8')
        line(d, (cxm - 14, 58, cxm - 8, 52), '#f4f8fa')
        line(d, (cxm - 15, 62, cxm - 7, 54), '#f4f8fa')
        line(d, (cxm - 13, 68, cxm - 10, 65), '#f4f8fa')
        px(d, cxm, 43, P['gold3']); rect(d, (cxm - 2, 40, cxm + 2, 43), P['gold'])  # 顶上的金花饰
        # 化妆台（白 + 金脚）
        t0, t1, ty = sx + 14, sx + 74, G - 26
        rect(d, (t0, ty, t1, ty + 3), '#ffffff')
        line(d, (t0, ty + 3, t1, ty + 3), '#d8ccd4')
        rect(d, (t0 + 2, ty + 4, t1 - 2, ty + 12), '#f4eef2')
        bevel(d, (t0 + 2, ty + 4, t1 - 2, ty + 12), '#e0d4dc', '#ffffff')
        rect(d, (t0 + 26, ty + 7, t0 + 34, ty + 8), P['gold'])
        for lx in (t0 + 3, t1 - 4):
            rect(d, (lx, ty + 13, lx + 1, G + 2), P['gold2'])
        # 台上：瓶瓶罐罐、梳子、吹风机
        rng = np.random.RandomState(70 + i)
        for k, bx in enumerate(range(t0 + 4, t0 + 24, 5)):
            c = ['#f0a0c0', '#a8d8e8', '#f8e4a0', '#c8a8e8'][(k + i) % 4]
            h = 4 + rng.randint(0, 4)
            rect(d, (bx, ty - h, bx + 3, ty - 1), c)
            px(d, bx + 1, ty - h - 1, '#ffffff')
            line(d, (bx, ty - h, bx, ty - 1), mix(c, '#ffffff', .4))
        line(d, (t1 - 20, ty - 1, t1 - 8, ty - 1), '#2a2a30')                   # 梳子
        for k in range(t1 - 20, t1 - 8, 2):
            px(d, k, ty - 2, '#2a2a30')
        if i == 0:                                                             # 吹风机
            rect(d, (t1 - 6, ty - 6, t1 - 1, ty - 3), '#f4f4f0')
            rect(d, (t1 - 5, ty - 3, t1 - 4, ty - 1), '#f4f4f0')
        stations.append((cxm, ty))
        # 美容椅：粉色丝绒 + 镀铬底座
        ch = cxm - 2
        rect(d, (ch - 10, G - 8, ch + 10, G + 8), P['pink2'])                   # 椅背
        rect(d, (ch - 9, G - 7, ch + 9, G + 7), P['pink'])
        for k in range(ch - 7, ch + 8, 4):
            px(d, k, G - 3, P['pink2']); px(d, k + 2, G + 2, P['pink2'])
        line(d, (ch - 9, G - 7, ch + 9, G - 7), P['pink3'])
        rect(d, (ch - 4, G - 12, ch + 4, G - 8), P['pink2'])                    # 头枕
        rect(d, (ch - 3, G - 12, ch + 3, G - 9), P['pink'])
        rect(d, (ch - 13, G + 4, ch + 13, G + 10), P['pink2'])                  # 座 + 扶手
        rect(d, (ch - 12, G + 4, ch + 12, G + 7), P['pink'])
        rect(d, (ch - 14, G + 2, ch - 11, G + 9), '#d8dce4')
        rect(d, (ch + 11, G + 2, ch + 14, G + 9), '#d8dce4')
        rect(d, (ch - 2, G + 11, ch + 2, G + 18), '#c8ccd4')                    # 液压杆
        line(d, (ch - 2, G + 11, ch - 2, G + 18), '#eef0f4')
        ellipse(d, (ch - 12, G + 17, ch + 12, G + 22), '#a8acb8')               # 圆底座
        ellipse(d, (ch - 11, G + 17, ch + 11, G + 20), '#d8dce4')
    # 第二组化妆台上：那支红口红（金管）放在一块小丝绒托盘上
    lcx, lty = stations[1][0] + 18, stations[1][1]
    rect(d, (lcx - 5, lty - 2, lcx + 7, lty - 1), P['velvet'])
    rect(d, (lcx, lty - 8, lcx + 2, lty - 3), P['gold'])
    rect(d, (lcx, lty - 11, lcx + 2, lty - 8), '#d0102a')
    px(d, lcx + 2, lty - 11, '#ff4a5a')
    px(d, lcx, lty - 8, P['gold3'])
    lipstick = [lcx + 1, lty - 6]
    # ---------------- 右：丝绒墙 + 一排 6 张脸（328–472）
    vx0, vx1 = 328, 472
    rect(d, (vx0, 14, vx1, WT - 1), P['velvet'])
    for x in range(vx0 + 3, vx1, 6):                                           # 丝绒的竖褶
        line(d, (x, 14, x, WT - 1), P['velvet2'])
        line(d, (x + 1, 14, x + 1, WT - 1), P['velvet3'] if (x // 6) % 3 == 0 else P['velvet'])
    rect(d, (vx0 - 3, 13, vx0, WT), P['gold'])
    rect(d, (vx1, 13, vx1 + 3, WT), P['gold'])
    line(d, (vx0 - 3, 13, vx0 - 3, WT), P['gold3'])
    rect(d, (vx0, 14, vx1, 18), P['gold2'])                                    # 上沿的金色帷幔边
    for x in range(vx0, vx1, 8):
        ellipse(d, (x, 15, x + 8, 22), P['gold'])
        px(d, x + 4, 22, P['gold3'])
    tw, th = kanji_size('シンデレラ')                                           # 丝绒墙上方的店名牌
    rect(d, ((vx0 + vx1) // 2 - tw // 2 - 5, 25, (vx0 + vx1) // 2 + tw // 2 + 5, 25 + th + 4), P['gold2'])
    rect(d, ((vx0 + vx1) // 2 - tw // 2 - 4, 26, (vx0 + vx1) // 2 + tw // 2 + 4, 25 + th + 3), '#2a1420')
    kanji(im, (vx0 + vx1) // 2 - tw // 2, 28, 'シンデレラ', P['gold3'])
    d = ImageDraw.Draw(im)
    faces = []
    fy = 58
    for k, spec in enumerate(FACES):
        fx = vx0 + 6 + k * 23
        line(d, (fx + 9, fy - 6, fx + 9, fy - 1), P['gold'])                   # 挂钩 + 一条金链
        px(d, fx + 8, fy - 7, P['gold3']); px(d, fx + 10, fy - 7, P['gold3'])
        ellipse(d, (fx - 1, fy - 1, fx + 19, fy + 26), P['gold2'])              # 椭圆小金托
        ellipse(d, (fx, fy, fx + 18, fy + 25), P['velvet2'])
        face_mask(d, fx, fy, spec)
        rect(d, (fx + 6, fy + 29, fx + 12, fy + 33), P['gold2'])                # 下面的小铜牌（号码）
        rect(d, (fx + 7, fy + 30, fx + 11, fy + 32), P['gold3'])
        faces.append([fx + 9, fy + 12])
    # 辻彩的工作台：长桌，桌上有刷子、小剪子、一卷软尺、一碟粉
    t0, t1, ty = 336, 420, G - 24
    rect(d, (t0, ty, t1, ty + 3), '#4a2a1e')
    line(d, (t0, ty, t1, ty), '#7a4a34')
    rect(d, (t0 + 2, ty + 4, t1 - 2, ty + 10), '#5a3426')
    bevel(d, (t0 + 2, ty + 4, t1 - 2, ty + 10), '#3a1e16', '#7a4a34')
    for lx in (t0 + 3, t1 - 5):
        rect(d, (lx, ty + 11, lx + 2, G + 3), '#3a1e16')
    for k in range(4):                                                         # 化妆刷
        bx = t0 + 6 + k * 4
        line(d, (bx, ty - 1, bx + 1, ty - 8), '#2a2a30')
        rect(d, (bx, ty - 11, bx + 2, ty - 8), ['#f0d8c8', '#e8a8b8', '#8a6a5a', '#f8f0e8'][k])
    line(d, (t0 + 26, ty - 2, t0 + 31, ty - 5), '#c8ccd4'); line(d, (t0 + 26, ty - 5, t0 + 31, ty - 2), '#c8ccd4')  # 剪子
    ellipse(d, (t0 + 25, ty - 3, t0 + 27, ty - 1), P['gold']); ellipse(d, (t0 + 25, ty - 6, t0 + 27, ty - 4), P['gold'])
    ellipse(d, (t0 + 38, ty - 5, t0 + 46, ty - 1), '#f4e04a')                   # 软尺一卷
    ellipse(d, (t0 + 40, ty - 4, t0 + 44, ty - 2), '#c8b030')
    ellipse(d, (t0 + 52, ty - 3, t0 + 64, ty), '#f8f4f0')                      # 粉碟 + 粉扑
    ellipse(d, (t0 + 54, ty - 4, t0 + 62, ty - 1), '#f4d8c8')
    ellipse(d, (t0 + 66, ty - 6, t0 + 74, ty - 1), '#f8e4ec')
    rect(d, (t0 + 76, ty - 14, t0 + 80, ty - 1), '#c8ccd4')                    # 台灯
    poly(d, [(t0 + 72, ty - 14), (t0 + 84, ty - 14), (t0 + 82, ty - 20), (t0 + 74, ty - 20)], P['pink2'])
    # 躺椅（美容床）：右边，白色皮面
    bx0, bx1 = 424, 466
    rect(d, (bx0, G - 2, bx1, G + 4), '#f4f0f2')
    line(d, (bx0, G - 2, bx1, G - 2), '#ffffff')
    poly(d, [(bx0, G - 2), (bx0 + 4, G - 2), (bx0 - 4, G - 14), (bx0 - 8, G - 14)], '#f4f0f2')
    line(d, (bx0 - 8, G - 14, bx0, G - 2), '#d8d0d6')
    rect(d, (bx0 + 2, G + 5, bx0 + 4, G + 14), '#c8ccd4'); rect(d, (bx1 - 4, G + 5, bx1 - 2, G + 14), '#c8ccd4')
    rect(d, (bx0 - 2, G + 14, bx1 + 2, G + 16), '#a8acb8')
    rect(d, (bx1 - 10, G - 6, bx1 - 1, G - 2), '#fbeaf0')                      # 叠好的毛巾
    line(d, (bx1 - 10, G - 4, bx1 - 1, G - 4), P['pink3'])
    # 最右：通里间的帘子（丝绒 + 金色绑带），在丝绒墙外面
    rect(d, (vx1 + 3, 14, W, G), P['velvet2'])
    for x in range(vx1 + 4, W, 3):
        line(d, (x, 14, x, G), P['velvet'] if x % 2 else P['velvet3'])
    rect(d, (vx1 + 3, 70, W, 73), P['gold'])
    # ---------------- 地板：黑白格（护墙板脚下压一条阴影）
    im = floor_tiles(im, 0, W, G + 1, cols=('#f4eef2', '#3a2e3e'), grout='#8a7a8a')
    im = dither_fill(im, (0, G + 1, W, G + 3), '#6a5a6a', '#9a8a9a', .5)
    # 地板上椅子、前台、桌子的影子 + 再画一遍压在地板上的椅子底座 / 桌腿（地板后画会盖掉）
    d = ImageDraw.Draw(im)
    for cxm, _ in stations:
        ch = cxm - 2
        im = dither_fill(im, (ch - 14, G + 18, ch + 14, G + 23), '#5a4a5a', '#2a2030', .5)
        d = ImageDraw.Draw(im)
        rect(d, (ch - 2, G + 1, ch + 2, G + 18), '#c8ccd4')
        line(d, (ch - 2, G + 1, ch - 2, G + 18), '#eef0f4')
        ellipse(d, (ch - 12, G + 16, ch + 12, G + 21), '#a8acb8')
        ellipse(d, (ch - 11, G + 16, ch + 11, G + 19), '#d8dce4')
        rect(d, (ch - 13, G + 1, ch + 13, G + 10), P['pink2'])
        rect(d, (ch - 12, G + 1, ch + 12, G + 7), P['pink'])
        rect(d, (ch - 14, G + 1, ch - 11, G + 9), '#d8dce4')
        rect(d, (ch + 11, G + 1, ch + 14, G + 9), '#d8dce4')
        rect(d, (ch - 9, G - 7, ch + 9, G + 3), P['pink'])
    rect(d, (cx0, G, cx1, G + 4), '#f8f4f6')
    line(d, (cx0, G + 4, cx1, G + 4), P['gold2'])
    rect(d, (bx0 - 2, G + 1, bx1 + 2, G + 4), '#f4f0f2')
    rect(d, (bx0 + 2, G + 5, bx0 + 4, G + 14), '#c8ccd4'); rect(d, (bx1 - 4, G + 5, bx1 - 2, G + 14), '#c8ccd4')
    rect(d, (bx0 - 2, G + 14, bx1 + 2, G + 16), '#a8acb8')
    for lx in (t0 + 3, t1 - 5):
        rect(d, (lx, G, lx + 2, G + 3), '#3a1e16')
    # 门口的地垫
    rect(d, (dx0 - 2, G + 2, dx1 + 2, G + 7), P['velvet'])
    line(d, (dx0 - 2, G + 2, dx1 + 2, G + 2), P['velvet3'])
    return im, G, dict(stations=stations, faces=faces, lipstick=lipstick, menu=[(mx0 + mx1) // 2, (my0 + my1) // 2],
                       door=(dx0, dx1), counter=(cx0, cx1), table=(t0, t1), bed=(bx0, bx1))


def chandelier(d, cx, top, P=SAL):
    line(d, (cx, top, cx, top + 8), P['gold2'])
    rect(d, (cx - 1, top + 8, cx + 1, top + 12), P['gold'])
    line(d, (cx - 12, top + 14, cx + 12, top + 14), P['gold'])
    for k in (-12, -6, 0, 6, 12):
        line(d, (cx + k, top + 14, cx + k, top + 12), P['gold'])
        rect(d, (cx + k - 1, top + 9, cx + k + 1, top + 11), '#fff8e0')
        px(d, cx + k, top + 8, '#fff4b0')
    for k in (-9, -3, 3, 9):                                                    # 垂下的水晶
        px(d, cx + k, top + 16, '#e8f4fa'); px(d, cx + k, top + 18, '#c8e4f0')
    ellipse(d, (cx - 2, top + 16, cx + 2, top + 20), '#e8f4fa')


def salon_glow(W, lamps):
    yy, xx = np.mgrid[0:180, 0:W].astype(float)
    f = np.zeros((180, W))
    for cx, cy in lamps:
        r = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.3) ** 2)
        f = np.maximum(f, np.clip(1 - r / 44, 0, 1) ** 1.6 * .22)
    h, w = f.shape
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    fq = np.clip(np.floor(f * 6 + bay) / 6, 0, 1)
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * np.array((255, 214, 150), float), 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def mirror_glint(n=10, w=40, h=52):
    """镜面上一道斜着扫过去的反光：n 帧里只有前 4 帧在扫，其余空着（隔一会儿闪一次）"""
    out = new(w * n, h)
    d = ImageDraw.Draw(out)
    for f in range(4):
        x0 = -10 + f * 14
        for y in range(h):
            xx = x0 + (h - y) * .5
            for k in range(3):
                X = int(xx + k)
                # 只画在椭圆镜面里
                cx, cy = w / 2, h / 2
                if ((X - cx) / (w / 2 - 1)) ** 2 + ((y - cy) / (h / 2 - 1)) ** 2 < 1:
                    d.point((f * w + X, y), fill=C('#ffffff', 150 if k == 1 else 90))
    return out


def cinderella_salon():
    W = 480
    room, G, info = salon_room()
    d = ImageDraw.Draw(room)
    lamps = []
    for cx in (160, 306):
        chandelier(d, cx, 12)
        lamps.append((cx, 34))
    glow = salon_glow(W, lamps)
    glint = mirror_glint(10, 40, 52)
    layers = {'room': room, 'glow': glow, 'glint': glint}
    st = info['stations']
    faces = info['faces']
    anchors = dict(door=[31, 148], counter=[95, 146], menu=info['menu'], mirror1=[st[0][0], 74], mirror2=[st[1][0], 74],
                   chair1=[st[0][0] - 2, 148], chair2=[st[1][0] - 2, 148], lipstick=info['lipstick'],
                   face_wall=[400, 146], table=[378, 146], bed=[445, 148], curtain=[476, 146], walk_x=[12, 468])
    for k, f in enumerate(faces):
        anchors[f'face{k + 1}'] = f
    anchors['yukako_face'] = faces[YUKAKO_FACE]
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176], anchors=anchors,
                layers=[{'type': 'pano', 'image': 'bg/cinderella_salon/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': 'bg/cinderella_salon/glint', 'n': 10, 'fps': 6, 'x': st[0][0] - 20, 'y': 48, 'k': 1},
                        {'type': 'strip', 'image': 'bg/cinderella_salon/glint', 'n': 10, 'fps': 5, 'x': st[1][0] - 20, 'y': 48, 'k': 1},
                        {'type': 'glow', 'image': 'bg/cinderella_salon/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.05},
                        {'type': 'tint', 'color': '#1a2048', 'alpha': 0.5, 'key': 'night'}],
                fg=[])
    pv = room.copy()
    pa = np.array(pv).astype(int)
    g = np.array(glow).astype(int)
    pa[..., :3] = np.clip(pa[..., :3] + g[..., :3] * (g[..., 3:4] > 0), 0, 255)
    pv = Image.fromarray(pa.astype(np.uint8), 'RGBA')
    pv.alpha_composite(glint.crop((40, 0, 80, 52)), (st[0][0] - 20, 48))
    preview('cinderella_salon', {'room': pv}, ['room'], W)
    save_layers('cinderella_salon', layers, meta)
    return meta


# ============================================================ 裁缝店 tailor_shop（480 宽，室内，白天）
#   老式的洋服店：左边玻璃门和橱窗（门外是马路，坦克从这里滚进来），挂着待取的西装的衣架，中间长柜台（登记簿、算盘、
#   剪刀、划粉），柜台后墙上一格格的布料卷，右边窗下一台老缝纫机（台灯），一个穿着半成品西装的人台，试衣间的帘子。
#   key 'after'：白光之后——橱窗玻璃碎了、布卷和纸散了一地、地上一圈焦黑、柜台上的登记簿不见了（只剩翻开的空位），一缕烟。
TL = dict(wall='#e8dcc4', wall2='#d8caae', wall3='#f2e8d4', ceil='#c8b898', wood='#7a5234', wood2='#5a3a24', wood3='#9a6e48',
          wood4='#3e2618')


def bolt(d, x, y, w, h, col):
    """架上平放的一卷布：侧面看是一个椭圆头 + 长条"""
    rect(d, (x, y, x + w, y + h), col)
    line(d, (x, y, x + w, y), mix(col, '#ffffff', .35))
    line(d, (x, y + h, x + w, y + h), mix(col, '#000000', .3))
    ellipse(d, (x + w - 3, y, x + w + 1, y + h), mix(col, '#000000', .15))
    px(d, x + w - 1, y + h // 2, mix(col, '#000000', .45))


def suit_on_hanger(d, x, top, col, shirt='#f4f2ec', tag=True, sleeve=True):
    """挂在横杆上的一件西装外套（正面）：衣架、肩、翻领、两排扣"""
    line(d, (x, top, x, top + 3), '#a8acb4')
    poly(d, [(x - 7, top + 6), (x, top + 3), (x + 7, top + 6)], '#8a6a4a')
    poly(d, [(x - 8, top + 6), (x + 8, top + 6), (x + 9, top + 34), (x - 9, top + 34)], col)
    poly(d, [(x - 3, top + 6), (x + 3, top + 6), (x, top + 18)], shirt)
    line(d, (x - 3, top + 6, x - 1, top + 22), mix(col, '#000000', .3))
    line(d, (x + 3, top + 6, x + 1, top + 22), mix(col, '#000000', .3))
    for k in range(2):
        px(d, x - 2, top + 22 + k * 5, mix(col, '#ffffff', .35))
        px(d, x + 2, top + 22 + k * 5, mix(col, '#ffffff', .35))
    line(d, (x - 8, top + 6, x - 9, top + 34), mix(col, '#ffffff', .15))
    line(d, (x + 9, top + 7, x + 9, top + 34), mix(col, '#000000', .25))
    if tag:
        rect(d, (x + 4, top + 9, x + 8, top + 14), '#f8f4e0')
        line(d, (x + 5, top + 11, x + 7, top + 11), '#c83a34')


def mannequin(d, x, g, col):
    """人台：一截躯干（套着只缝了一半的西装马甲）+ 木杆 + 三脚架"""
    ellipse(d, (x - 9, g - 70, x + 9, g - 64), '#e8d8c0')
    poly(d, [(x - 10, g - 66), (x + 10, g - 66), (x + 8, g - 44), (x + 9, g - 34), (x - 9, g - 34), (x - 8, g - 44)], '#e8d8c0')
    poly(d, [(x - 10, g - 64), (x + 10, g - 64), (x + 8, g - 44), (x + 9, g - 36), (x - 9, g - 36), (x - 8, g - 44)], col)
    poly(d, [(x - 3, g - 64), (x + 3, g - 64), (x, g - 52)], '#e8d8c0')
    for k in range(3):
        px(d, x, g - 50 + k * 5, '#d8c8a0')
    for k in range(-8, 9, 3):                                                  # 别着的珠针
        px(d, x + k, g - 44, '#e8e8f0')
    line(d, (x + 9, g - 60, x + 9, g - 40), '#f4f4f0')                         # 粉笔线
    rect(d, (x - 1, g - 34, x + 1, g - 6), '#6a4a34')
    line(d, (x, g - 6, x - 10, g), '#5a3a24'); line(d, (x, g - 6, x + 10, g), '#5a3a24'); line(d, (x, g - 6, x, g + 2), '#5a3a24')
    ellipse(d, (x - 2, g - 73, x + 2, g - 70), '#6a4a34')


def sewing_machine(d, x, g):
    """老式脚踏缝纫机：铸铁镂空架 + 木台面 + 黑色机头（金字）"""
    rect(d, (x, g - 30, x + 44, g - 27), '#7a5234')
    line(d, (x, g - 30, x + 44, g - 30), '#9a6e48')
    for lx in (x + 3, x + 37):                                                 # 铸铁腿（镂空）
        rect(d, (lx, g - 26, lx + 4, g), '#2a2a30')
        rect(d, (lx + 1, g - 22, lx + 3, g - 8), '#7a6a58')
        rect(d, (lx - 2, g - 1, lx + 6, g), '#2a2a30')
    line(d, (x + 7, g - 6, x + 37, g - 6), '#2a2a30')
    rect(d, (x + 14, g - 8, x + 30, g - 5), '#2a2a30')                         # 脚踏板
    for k in range(x + 15, x + 30, 2):
        px(d, k, g - 7, '#4a4a52')
    ellipse(d, (x + 34, g - 24, x + 44, g - 14), '#2a2a30')                     # 大飞轮
    ellipse(d, (x + 36, g - 22, x + 42, g - 16), '#7a6a58')
    # 机头
    rect(d, (x + 6, g - 44, x + 34, g - 40), '#1e1e24')
    rect(d, (x + 26, g - 44, x + 34, g - 31), '#1e1e24')
    rect(d, (x + 6, g - 44, x + 10, g - 33), '#1e1e24')
    line(d, (x + 6, g - 44, x + 34, g - 44), '#4a4a58')
    rect(d, (x + 7, g - 33, x + 9, g - 31), '#c8ccd4')                          # 针
    line(d, (x + 8, g - 31, x + 8, g - 30), '#e8e8f0')
    letters(d, x + 12, g - 43, 'SINGER'[:0] or 'MRT', '#d8b05a')               # 机头上的金字（自造牌子）
    for k in range(x + 12, x + 25, 3):
        px(d, k, g - 38, '#d8b05a')
    ellipse(d, (x + 33, g - 42, x + 37, g - 38), '#4a4a58')                     # 小飞轮
    rect(d, (x + 20, g - 48, x + 22, g - 44), '#e8e0c8')                        # 线轴
    px(d, x + 21, g - 49, '#c83a34')


def tailor_room(after=False):
    W, G = 480, 134
    P = TL
    im = new(W, 180, P['wall'])
    d = ImageDraw.Draw(im)
    for y in range(16, G, 6):                                                  # 旧墙纸：细竖条
        for x in range((y // 6) % 2 * 4, W, 8):
            px(d, x, y, P['wall2'])
    im = grad(im, (0, 10, W, 24), (P['ceil'], P['wall2'], P['wall']))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 10), '#a89878')
    rect(d, (0, 10, W, 12), P['wood'])
    line(d, (0, 10, W, 10), P['wood3'])
    WT = 110                                                                   # 腰线以下：木护墙
    rect(d, (0, WT, W, G), P['wood'])
    line(d, (0, WT, W, WT), P['wood3'])
    for x in range(0, W, 12):
        line(d, (x, WT + 2, x, G), P['wood2'])
    rect(d, (0, G - 3, W, G), P['wood4'])
    # ---------------- 左：玻璃门 + 橱窗（门外的马路），门上挂铃，窗玻璃上的店名
    dx0, dx1, dy0 = 10, 40, G - 78
    rect(d, (dx0 - 3, dy0 - 3, dx1 + 3, G), P['wood2'])
    im = grad(im, (dx0, dy0, dx1, G - 1), ('#b0d4ee', '#cce2f2', '#d8d4c8'))
    d = ImageDraw.Draw(im)
    rect(d, (dx0, G - 18, dx1, G - 1), '#8a8a90')
    rect(d, (dx0, G - 26, dx1, G - 18), '#3a3a42')                             # 门外停着的车（一截）
    rect(d, (dx0 + 4, G - 32, dx1 - 2, G - 26), '#c8ccd4')
    rect(d, (dx0, dy0 + 30, dx1, dy0 + 32), P['wood2'])                        # 门的横档
    line(d, (dx0 + 2, dy0 + 3, dx0 + 8, dy0 + 9), '#eef6fa')
    rect(d, (dx1 - 6, G - 44, dx1 - 4, G - 36), '#d8c070')
    rect(d, (dx1 - 6, dy0 - 9, dx1 - 3, dy0 - 4), '#d8b05a')                   # 门铃
    ellipse(d, (dx1 - 7, dy0 - 5, dx1 - 2, dy0), '#e8c870')
    wx0, wx1, wy0 = 48, 112, G - 76                                            # 橱窗
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, G - 18), P['wood2'])
    im = grad(im, (wx0, wy0, wx1, G - 21), ('#b0d4ee', '#cce2f2', '#e0dccc'))
    d = ImageDraw.Draw(im)
    rect(d, (wx0, G - 34, wx1, G - 21), '#8a8a90')
    rect(d, (wx0 + 10, wy0 + 6, wx0 + 30, G - 34), '#d8cfc0')                  # 对面的楼
    rect(d, (wx0 + 34, wy0 + 2, wx1, G - 34), '#c4b8a8')
    for yy in range(wy0 + 8, G - 38, 9):
        rect(d, (wx0 + 14, yy, wx0 + 20, yy + 4), '#7e9cb8'); rect(d, (wx0 + 40, yy, wx0 + 46, yy + 4), '#7e9cb8')
        rect(d, (wx0 + 52, yy, wx0 + 58, yy + 4), '#7e9cb8')
    line(d, ((wx0 + wx1) // 2, wy0, (wx0 + wx1) // 2, G - 21), P['wood2'])
    for k in range(3):
        line(d, (wx0 + 3 + k * 5, wy0 + 3, wx0 + 10 + k * 5, wy0 + 10), '#eef6fa')
    rect(d, (wx0 - 3, G - 20, wx1 + 3, G), P['wood'])                           # 橱窗下的木台
    line(d, (wx0 - 3, G - 20, wx1 + 3, G - 20), P['wood3'])
    letters(d, wx0 + 8, wy0 + 4, 'TAILOR', '#f4ead0')                          # 窗玻璃上的白字（店里看是反的，像素小字只写正的）
    # 窗台上：一块折好的布 + 一个小镜子
    rect(d, (wx0 + 4, G - 24, wx0 + 18, G - 21), '#3a4a6a')
    rect(d, (wx0 + 20, G - 24, wx0 + 32, G - 21), '#8a7a5a')
    # 窗前的一排待取西装：衣架横杆
    rail_y = 34
    rect(d, (120, rail_y, 196, rail_y + 1), '#a8acb4')
    for x in (120, 196):
        rect(d, (x, rail_y, x + 1, G + 6), '#a8acb4')
        rect(d, (x - 4, G + 5, x + 5, G + 7), '#6a6e78')
    for k, (x, col) in enumerate(((130, '#3a3e52'), (145, '#5a4a3a'), (160, '#2a2a30'), (175, '#6a6e78'), (188, '#4a3a5a'))):
        suit_on_hanger(d, x, rail_y + 1, col)
    # ---------------- 中：长柜台（210–330）+ 后墙的布料格架
    sx0, sx1, sy0 = 206, 338, 22
    rect(d, (sx0 - 2, sy0 - 2, sx1 + 2, WT - 4), P['wood4'])
    rect(d, (sx0, sy0, sx1, WT - 6), P['wood2'])
    rng = np.random.RandomState(77)
    cols = ['#3a4a6a', '#2a2a30', '#6a6e78', '#8a7a5a', '#4a5a4a', '#7a3a3a', '#c8bca0', '#2e3a5a', '#5a4a3a', '#a89a80', '#4a3a5a',
            '#d8d0c0']
    rows = 5
    rh = (WT - 6 - sy0) // rows
    for r in range(rows):
        y = sy0 + r * rh
        rect(d, (sx0, y + rh - 2, sx1, y + rh), P['wood3'])
        for c in range(4):
            cx = sx0 + 3 + c * 33
            for k in range(2 if r % 2 else 3):
                h = (rh - 5) // (2 if r % 2 else 3)
                bolt(d, cx, y + 2 + k * (h + 1), 28, h - 1, cols[rng.randint(len(cols))])
        for c in range(1, 4):
            rect(d, (sx0 + c * 33, y, sx0 + c * 33 + 1, y + rh - 2), P['wood4'])
    # 柜台
    ct, c0, c1 = G - 30, 210, 334
    rect(d, (c0, ct, c1, G + 6), P['wood'])
    rect(d, (c0 - 3, ct - 4, c1 + 3, ct), P['wood3'])
    line(d, (c0 - 3, ct - 4, c1 + 3, ct - 4), '#b88a5e')
    line(d, (c0 - 3, ct, c1 + 3, ct), P['wood4'])
    for x in range(c0 + 4, c1 - 6, 20):
        rect(d, (x, ct + 4, x + 16, G + 2), P['wood2'])
        bevel(d, (x, ct + 4, x + 16, G + 2), P['wood4'], P['wood3'])
    # 台面上：登记簿（翻开）、算盘、大剪刀、划粉、软尺
    ledger = [c0 + 30, ct - 6]
    if not after:
        rect(d, (c0 + 20, ct - 7, c0 + 40, ct - 5), '#f4ecd8')
        line(d, (c0 + 30, ct - 7, c0 + 30, ct - 5), '#c8b898')
        rect(d, (c0 + 19, ct - 5, c0 + 41, ct - 4), '#5a2a2a')
        for k in range(c0 + 21, c0 + 29, 2):
            px(d, k, ct - 6, '#6a6a7a')
        for k in range(c0 + 32, c0 + 40, 2):
            px(d, k, ct - 6, '#6a6a7a')
    else:
        rect(d, (c0 + 19, ct - 5, c0 + 41, ct - 4), mix('#5a2a2a', '#000000', .3))  # 登记簿被翻乱：只剩深色封皮一角
        px(d, c0 + 22, ct - 6, '#f4ecd8'); px(d, c0 + 26, ct - 6, '#f4ecd8')
    rect(d, (c0 + 50, ct - 8, c0 + 72, ct - 4), '#6a4a2a')                     # 算盘
    for k in range(c0 + 51, c0 + 72, 2):
        px(d, k, ct - 7, '#2a1a10'); px(d, k, ct - 5, '#2a1a10')
    line(d, (c0 + 50, ct - 6, c0 + 72, ct - 6), '#c8b898')
    line(d, (c0 + 82, ct - 5, c0 + 94, ct - 7), '#c8ccd4')                     # 大剪刀
    line(d, (c0 + 82, ct - 7, c0 + 94, ct - 5), '#a8acb4')
    ellipse(d, (c0 + 78, ct - 8, c0 + 82, ct - 5), '#2a2a30')
    rect(d, (c0 + 100, ct - 6, c0 + 104, ct - 4), '#f4f4f0')                   # 划粉
    poly(d, [(c0 + 106, ct - 4), (c0 + 120, ct - 4), (c0 + 118, ct - 6), (c0 + 108, ct - 6)], '#f4e04a')  # 软尺
    # 柜台后墙上：挂钟（3:10）+ 营业执照的小框
    ccx, ccy = 360, 34
    ellipse(d, (ccx - 9, ccy - 9, ccx + 9, ccy + 9), P['wood2'])
    ellipse(d, (ccx - 7, ccy - 7, ccx + 7, ccy + 7), '#f6f0e0')
    line(d, (ccx, ccy, ccx, ccy - 6), '#2a2a30')
    line(d, (ccx, ccy, ccx + 3, ccy + 1), '#2a2a30')
    px(d, ccx, ccy, '#c83a34')
    # ---------------- 右：人台、窗下的缝纫机、试衣间
    mannequin(d, 360, G + 4, '#3a3e52')
    wx0, wx1, wy0, wy1 = 384, 440, 30, 80                                      # 侧窗（磨砂）
    rect(d, (wx0 - 2, wy0 - 2, wx1 + 2, wy1 + 2), P['wood2'])
    rect(d, (wx0, wy0, wx1, wy1), '#e8eee8')
    for yy in range(wy0 + 1, wy1, 3):
        line(d, (wx0, yy, wx1, yy), '#f4f8f4')
    line(d, ((wx0 + wx1) // 2, wy0, (wx0 + wx1) // 2, wy1), P['wood2'])
    line(d, (wx0, (wy0 + wy1) // 2, wx1, (wy0 + wy1) // 2), P['wood2'])
    sewing_machine(d, 390, G + 2)
    rect(d, (420, G - 44, 423, G - 30), '#4a5a4a')                             # 缝纫灯
    poly(d, [(416, G - 50), (428, G - 50), (426, G - 44), (418, G - 44)], '#4a6a5a')
    rect(d, (448, 20, W, G + 4), P['wood2'])                                   # 试衣间（帘子）
    rect(d, (450, 22, W, 24), '#a8acb4')
    for x in range(451, W, 4):
        line(d, (x, 25, x + (x % 3) - 1, G + 2), '#8a2a34')
        line(d, (x + 1, 25, x + 1, G + 2), '#a83a44')
        line(d, (x + 2, 25, x + 2, G + 2), '#a83a44')
    # ---------------- 地板
    im = wood_floor(im, 0, W, G + 1)
    d = ImageDraw.Draw(im)
    rect(d, (c0, G, c1, G + 6), P['wood'])                                     # 柜台底座压在地板上
    line(d, (c0, G + 6, c1, G + 6), P['wood4'])
    im = dither_fill(im, (c0 - 4, G + 7, c1 + 4, G + 10), '#5a3a24', '#7a5234', .5)
    d = ImageDraw.Draw(im)
    for x in (120, 196):
        rect(d, (x, G, x + 1, G + 6), '#a8acb4')
        rect(d, (x - 4, G + 5, x + 5, G + 7), '#6a6e78')
    mannequin(d, 360, G + 4, '#3a3e52')
    sewing_machine(d, 390, G + 2)
    rect(d, (dx0 - 3, G + 1, dx1 + 3, G + 6), '#6a5a48')                       # 门口的擦鞋垫
    line(d, (dx0 - 3, G + 1, dx1 + 3, G + 1), '#8a7a62')
    return im, G, dict(door=(dx0, dx1), window=(48, 112), ledger=ledger, counter=(c0, c1), rail=(120, 196), sewing=[412, 146],
                       mannequin=[360, 146], fitting=[462, 146], clock=[ccx, ccy])


def tailor_after_layer(clean):
    """白光之后：把干净的图和乱了的图比较，只留下有变化的像素（橱窗碎了、地上散的布和纸、焦黑一圈），作为 key 'after' 的覆盖层"""
    W, G = 480, 134
    messy, _, info = tailor_room(after=True)
    d = ImageDraw.Draw(messy)
    rng = np.random.RandomState(91)
    # 橱窗玻璃：碎成几块，中间露出外面（更亮），窗框上挂着碎片
    wx0, wx1 = info['window']
    wy0 = G - 76
    for k in range(10):
        x = rng.randint(wx0 + 2, wx1 - 4)
        y = rng.randint(wy0 + 2, G - 26)
        poly(d, [(x, y), (x + rng.randint(3, 9), y + rng.randint(-3, 4)), (x + rng.randint(1, 6), y + rng.randint(4, 10))],
             '#f4fafc')
    for k in range(6):
        cxk, cyk = (wx0 + wx1) // 2 + rng.randint(-20, 20), (wy0 + G - 26) // 2 + rng.randint(-14, 14)
        line(d, ((wx0 + wx1) // 2, (wy0 + G - 26) // 2, cxk + rng.randint(-14, 14), cyk + rng.randint(-14, 14)), '#5a6a78')
    # 地上：焦黑一圈（柜台前），用两档抖动
    cx, cy = 250, G + 20
    yy, xx = np.mgrid[0:180, 0:W].astype(float)
    r = np.sqrt(((xx - cx) / 34) ** 2 + ((yy - cy) / 8) ** 2)
    bay = np.tile(BAYER, (180 // 4 + 1, W // 4 + 1))[:180, :W]
    a = np.array(messy)
    burn1 = (r < 1.0) & (bay < np.clip(1.25 - r, 0, 1)) & (yy > G)
    burn2 = (r < .55) & (yy > G)
    a[burn1] = np.array([*c3('#3a2a22'), 255])
    a[burn2 & (bay < .6)] = np.array([*c3('#1e1612'), 255])
    messy = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(messy)
    # 散落的布卷、纸片、衣架、碎玻璃
    cols = ['#3a4a6a', '#6a6e78', '#8a7a5a', '#7a3a3a', '#c8bca0', '#4a3a5a']
    for k in range(7):
        x = rng.randint(130, 420)
        y = rng.randint(G + 6, 172)
        if abs(x - cx) < 30 and abs(y - cy) < 6:
            continue
        w = rng.randint(14, 26)
        c = cols[rng.randint(len(cols))]
        if rng.rand() < .5:
            bolt(d, x, y, w, 3, c)
        else:                                                                  # 摊开的一截布
            poly(d, [(x, y), (x + w, y - 2), (x + w + 4, y + 4), (x + 3, y + 5)], c)
            line(d, (x, y, x + w, y - 2), mix(c, '#ffffff', .3))
    for k in range(18):
        x, y = rng.randint(60, 440), rng.randint(G + 4, 176)
        rect(d, (x, y, x + 3, y + 2), '#f4ecd8')
        px(d, x + 1, y + 1, '#a8a090')
    for k in range(20):
        x, y = rng.randint(40, 140), rng.randint(G + 3, 170)
        px(d, x, y, '#e8f4fa'); px(d, x + 1, y, '#a8c4d4')
    poly(d, [(150, G + 10), (158, G + 7), (166, G + 10)], '#8a6a4a')           # 掉在地上的衣架
    # 衣架上的西装：歪了一件（盖一块墙色再斜着画）
    out = np.array(messy)
    cl = np.array(clean)
    diff = np.any(out != cl, axis=2)
    lay = np.zeros_like(out)
    lay[diff] = out[diff]
    return Image.fromarray(lay, 'RGBA')


def tailor_shop():
    W = 480
    room, G, info = tailor_room()
    after = tailor_after_layer(room)
    smoke = smoke_strip(16, 40, 8, '#b8b4b0', seed=3)
    layers = {'room': room, 'after': after, 'smoke': smoke}
    c0, c1 = info['counter']
    anchors = dict(door=[25, 148], door_in=[25, 140], window=[80, 146], rail=[158, 146], counter=[(c0 + c1) // 2, 146],
                   counter_front=[(c0 + c1) // 2, 160], ledger=info['ledger'], shelves=[272, 60], clock=info['clock'],
                   mannequin=info['mannequin'], sewing=info['sewing'], fitting=info['fitting'], blast=[250, 154], walk_x=[12, 440])
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176], anchors=anchors,
                layers=[{'type': 'pano', 'image': 'bg/tailor_shop/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/tailor_shop/after', 'k': 1, 'x': 0, 'y': 0, 'key': 'after'},
                        {'type': 'strip', 'image': 'bg/tailor_shop/smoke', 'n': 8, 'fps': 6, 'x': 242, 'y': 116, 'k': 1, 'key': 'after'},
                        {'type': 'tint', 'color': '#ffb060', 'alpha': 0.05}],
                fg=[])
    preview('tailor_shop', {'room': room}, ['room'], W)
    pv = room.copy()
    pv.alpha_composite(after)
    pv.alpha_composite(smoke.crop((0, 0, 16, 40)), (242, 116))
    preview('tailor_shop_after', {'room': pv}, ['room'], W)
    save_layers('tailor_shop', layers, meta)
    return meta


# ============================================================ 裁缝店外的马路 morioh_avenue（960 宽，夏天的白天）
#   后面一排店：烟店（たばこ）、裁缝店门面（TAILOR 洋服）、小巷、米店门口的两台自动售货机、住家的砖墙和院子、公交站、
#   最右是灰姑娘美容院的门面。前面是人行道 + 马路（第 11 战在马路上打），路边停着两辆车；电线杆四根拉着电线。
#   热源（段 A/B 引坦克）：两辆车的引擎盖、售货机背后、马路上的烟头；每处一层 key 'heat_*' 的热气（默认不画）。
#   key 'after'：裁缝店的橱窗碎了、门口冒烟；key 'closed'：美容院拉下百叶、挂“本日休業”（第二天没开门）；key 'pm' 傍晚色。
def car_side(d, x, g, body='#f4f4f0', dark='#c8ccd4', glass='#5a7a98', kind='sedan'):
    """停在路边的车（侧面，车头朝右）：返回 (引擎盖中点, 车宽)"""
    if kind == 'sedan':
        L = 76
        poly(d, [(x, g - 10), (x + 2, g - 17), (x + 16, g - 19), (x + 24, g - 29), (x + 50, g - 29), (x + 58, g - 19),
                 (x + 74, g - 17), (x + L, g - 10), (x + L, g - 5), (x, g - 5)], body)
        poly(d, [(x + 26, g - 27), (x + 37, g - 27), (x + 37, g - 19), (x + 20, g - 19)], glass)
        poly(d, [(x + 39, g - 27), (x + 49, g - 27), (x + 55, g - 19), (x + 39, g - 19)], glass)
        line(d, (x + 28, g - 26, x + 33, g - 21), mix(glass, '#ffffff', .5))
        line(d, (x + 2, g - 13, x + L - 2, g - 13), dark)
        line(d, (x + 38, g - 19, x + 38, g - 6), dark)
        line(d, (x + 20, g - 19, x + 20, g - 6), dark)
        rect(d, (x + 30, g - 15, x + 33, g - 14), '#8a8a90'); rect(d, (x + 44, g - 15, x + 47, g - 14), '#8a8a90')
        rect(d, (x + L - 3, g - 15, x + L, g - 12), '#f8e8a0')                   # 前灯
        rect(d, (x, g - 15, x + 2, g - 12), '#d83a34')                          # 尾灯
        rect(d, (x - 1, g - 7, x + L + 1, g - 5), '#8a8a90')                     # 保险杠
        hood = [x + 66, g - 18]
        wheels = (x + 14, x + 62)
    else:                                                                      # 小货车（軽トラ）
        L = 64
        rect(d, (x, g - 18, x + 42, g - 6), body)                              # 车斗
        line(d, (x, g - 18, x + 42, g - 18), mix(body, '#ffffff', .3))
        for k in range(x + 4, x + 40, 8):
            line(d, (k, g - 17, k, g - 7), dark)
        poly(d, [(x + 42, g - 6), (x + 42, g - 30), (x + 56, g - 30), (x + L, g - 18), (x + L, g - 6)], body)
        poly(d, [(x + 45, g - 28), (x + 55, g - 28), (x + 61, g - 19), (x + 45, g - 19)], glass)
        line(d, (x + 47, g - 27, x + 51, g - 22), mix(glass, '#ffffff', .5))
        rect(d, (x + L - 3, g - 15, x + L, g - 12), '#f8e8a0')
        rect(d, (x - 1, g - 7, x + L + 1, g - 5), '#8a8a90')
        hood = [x + 58, g - 20]
        wheels = (x + 12, x + 52)
    for wx in wheels:
        ellipse(d, (wx - 6, g - 11, wx + 6, g + 1), '#1e1e24')
        ellipse(d, (wx - 3, g - 8, wx + 3, g - 2), '#a8acb4')
        px(d, wx, g - 5, '#5a5a62')
    return hood, L


def avenue_near(after=False, closed=False):
    W, G = 960, 128
    im = new(W, 180)
    d = ImageDraw.Draw(im)
    # ---------------- 1 烟店（0–104）：两层木造，一楼一个小窗口柜台，红色「たばこ」招牌、门口的立式烟灰缸
    rect(d, (0, 38, 104, G), '#c8b49a')
    for xx in range(0, 104, 5):
        line(d, (xx, 38, xx, G), '#b8a488')
    im = tiled_roof(im, -4, 108, 26, 38, ('#4a4e58', '#3a3e46', '#62666e', '#26282e'), overhang=3)
    d = ImageDraw.Draw(im)
    for wx in (12, 62):
        window(d, (wx, 46, wx + 26, 66), frame='#f0ece0', glass=('#8cb0c8', '#c0d8e6'), curtain='#e8d8b0')
    im = tiled_roof(im, 0, 104, G - 58, G - 50, ('#4a4e58', '#3a3e46', '#62666e', '#26282e'), overhang=3)
    d = ImageDraw.Draw(im)
    rect(d, (0, G - 50, 104, G), '#8a6a4a')
    rect(d, (6, G - 46, 58, G - 18), '#e8dcc4')                                # 小窗口：玻璃柜里一排排烟盒
    rect(d, (8, G - 44, 56, G - 20), '#a8c4d4')
    for r in range(3):
        for k, sx in enumerate(range(10, 54, 5)):
            c = ['#f4f4f0', '#3a6ac8', '#d83a34', '#f0c030', '#4a9a4a', '#2a2a30'][(k + r * 2) % 6]
            rect(d, (sx, G - 42 + r * 8, sx + 3, G - 37 + r * 8), c)
            px(d, sx + 1, G - 42 + r * 8, '#ffffff')
    rect(d, (4, G - 18, 60, G - 14), '#6a4a34')                                # 窗口的小台
    line(d, (4, G - 18, 60, G - 18), '#9a7a5a')
    rect(d, (8, G - 14, 56, G), '#7a5a3e')
    rect(d, (6, G - 62, 98, G - 50), '#d82a2a')                                # 招牌
    rect(d, (7, G - 61, 97, G - 51), '#e83a34')
    tw, th = kanji_size('たばこ')
    kanji(im, 52 - tw // 2, G - 62 + (12 - th) // 2 + 1, 'たばこ', '#ffffff')
    d = ImageDraw.Draw(im)
    rect(d, (64, G - 46, 100, G), '#5a4030')                                   # 拉门
    for xx in range(66, 100, 4):
        line(d, (xx, G - 44, xx, G - 1), '#c8b48a')
    im = vending(im, 72, G + 1, body='#e8e4dc', accent='#c83a34')              # 香烟售货机（白）
    d = ImageDraw.Draw(im)
    # ---------------- 2 裁缝店门面（112–296）：两层浅米色洋楼，绿框橱窗（人台穿西装）、玻璃门、TAILOR 招牌
    rect(d, (112, 30, 296, G), '#ece2cc')
    for yy in range(33, G, 3):
        line(d, (112, yy, 296, yy), '#e2d6be')
    rect(d, (110, 27, 298, 30), '#3a5a4a')
    line(d, (110, 27, 298, 27), '#5a7a6a')
    window_row(im, 112, 296, 38, 18, G, '#ece2cc', seed=12)
    d = ImageDraw.Draw(im)
    signboard(im, 114, 294, G - 64, 14, '#2e4a3e', '#1a2e26', None, '#f4ead0', latin='TAILOR')
    d = ImageDraw.Draw(im)
    tw, th = kanji_size('洋服')
    kanji(im, 128, G - 64 + 2, '洋服', '#f4ead0')
    kanji(im, 280 - tw, G - 64 + 2, '仕立', '#f4ead0')
    d = ImageDraw.Draw(im)
    rect(d, (112, G - 48, 296, G), '#3a5a4a')                                  # 一楼门脸（深绿框）
    swx0, swx1 = 120, 232                                                       # 橱窗
    rect(d, (swx0, G - 44, swx1, G - 8), '#2a3e34')
    im = grad(im, (swx0 + 2, G - 42, swx1 - 2, G - 10), ('#d8e4ea', '#c4d4dc', '#b0c0c8'))
    d = ImageDraw.Draw(im)
    for mx, col in ((140, '#2a2a30'), (176, '#3a3e52'), (212, '#6a5a48')):      # 橱窗里三个人台
        ellipse(d, (mx - 5, G - 40, mx + 5, G - 36), '#e8d8c0')
        poly(d, [(mx - 7, G - 37), (mx + 7, G - 37), (mx + 6, G - 20), (mx - 6, G - 20)], col)
        poly(d, [(mx - 2, G - 37), (mx + 2, G - 37), (mx, G - 28)], '#f4f2ec')
        rect(d, (mx, G - 20, mx + 1, G - 12), '#6a4a34')
        rect(d, (mx - 4, G - 12, mx + 5, G - 10), '#6a4a34')
    for k in range(3):
        line(d, (swx0 + 4 + k * 6, G - 42, swx0 + 12 + k * 6, G - 34), '#eef6fa')
    line(d, ((swx0 + swx1) // 2, G - 44, (swx0 + swx1) // 2, G - 8), '#2a3e34')
    rect(d, (swx0 - 2, G - 8, swx1 + 2, G), '#2a3e34')
    dx0, dx1 = 246, 284                                                        # 玻璃门
    rect(d, (dx0 - 2, G - 46, dx1 + 2, G), '#2a3e34')
    im = grad(im, (dx0, G - 44, dx1, G - 1), ('#b8ccd6', '#a4bcc8', '#8ea4b0'))
    d = ImageDraw.Draw(im)
    line(d, ((dx0 + dx1) // 2, G - 44, (dx0 + dx1) // 2, G - 1), '#2a3e34')
    rect(d, ((dx0 + dx1) // 2 - 3, G - 26, (dx0 + dx1) // 2 - 2, G - 18), '#d8c070')
    rect(d, ((dx0 + dx1) // 2 + 2, G - 26, (dx0 + dx1) // 2 + 3, G - 18), '#d8c070')
    rect(d, (dx0 + 2, G - 41, dx0 + 20, G - 33), '#f4ead0')                    # 门上的“营业中”小牌
    letters(d, dx0 + 3, G - 39, 'OPEN', '#c83a34')
    awning(im, 112, 296, G - 52, 6, ('#3a5a4a', '#e8e0c8'), scallop=False)
    d = ImageDraw.Draw(im)
    # ---------------- 3 小巷（296–318）
    rect(d, (296, 24, 318, G), '#6a6a70')
    rect(d, (300, 24, 314, G), '#4a4a52')
    rect(d, (310, 36, 312, G - 2), '#7a7a80')
    rect(d, (301, G - 16, 309, G), '#4a6a5a')
    # ---------------- 4 米店（318–444）：门口两台自动售货机（红、蓝），售货机后面是热源
    rect(d, (318, 44, 444, G), '#d8d0c0')
    im = tiled_roof(im, 314, 448, 32, 44, ('#5a4a42', '#4a3a34', '#7a665c', '#2e2420'), overhang=4)
    d = ImageDraw.Draw(im)
    window_row(im, 318, 444, 50, 16, G, '#d8d0c0', seed=13, step=34)
    d = ImageDraw.Draw(im)
    signboard(im, 322, 440, G - 60, 14, '#f4f0e0', '#6a5040', '米', '#3a2a1e')
    d = ImageDraw.Draw(im)
    letters(d, 336, G - 55, 'RICE', '#6a5040')
    rect(d, (318, G - 46, 444, G), '#5a4a3a')
    rect(d, (322, G - 42, 388, G - 1), '#3a3028')                              # 店里（暗）：米袋一摞摞
    for r in range(3):
        for k in range(4):
            x = 326 + k * 15 + (r % 2) * 6
            y = G - 10 - r * 8
            rect(d, (x, y, x + 12, y + 7), '#e8e0c8')
            line(d, (x + 2, y + 3, x + 10, y + 3), '#c83a34')
    vx1_, vx2_ = 396, 420
    im = vending(im, vx1_, G + 1, body='#d8303a', accent='#f4f0e8')
    im = vending(im, vx2_, G + 1, body='#2a5ac8', accent='#e8f0f8')
    d = ImageDraw.Draw(im)
    rect(d, (vx2_ + 24, G - 10, vx2_ + 26, G), '#8a8a90')                      # 空罐回收箱
    rect(d, (vx2_ + 23, G - 12, vx2_ + 27, G - 10), '#4a7a4a')
    vend = [vx1_ + 23, G - 20]
    # ---------------- 5 住家（444–640）：砖墙 + 院子里的树 + 二层小楼，墙外是公交站
    im = house(im, 470, G - 8, w=110, h=68, wall='#e6dccb', wall2='#c8bca8', seed=5)
    im = block_wall(im, 444, 640, G - 26, G)
    im = hedge(im, 448, 520, G - 40, G - 24, seed=3)
    im = hedge(im, 590, 640, G - 38, G - 24, seed=4)
    im = sakura(im, 612, G - 20, 64, 46, seed=8, pal=dict(d='#2e5e3a', m='#4a7c48', l='#6e9e5a', x='#a8cc7a', trunk='#5a4234',
                                                          trunk2='#3e2c22'), petals=False)
    # ---------------- 6 公交站 + 第二户（640–806）
    im = house(im, 660, G - 2, w=120, h=78, wall='#dcd6e0', wall2='#bcb4c4', seed=9)
    im = block_wall(im, 640, 806, G - 22, G, cols=('#d4ccbc', '#b8b0a0', '#9a9284', '#e8e0d0'))
    im = bus_stop(im, 724, G + 2)
    # ---------------- 7 灰姑娘美容院（806–960）：淡粉灰泥洋楼，拱窗（蕾丝窗帘）、金字招牌、玻璃鞋徽、两盆修剪的灌木
    S = SAL
    d = ImageDraw.Draw(im)
    rect(d, (806, 18, 960, G), '#f0dce4')
    for yy in range(22, G, 4):
        for xx in range(806 + (yy // 4) % 2 * 3, 960, 6):
            px(d, xx, yy, '#e8d0da')
    rect(d, (804, 14, 960, 18), '#ffffff')
    line(d, (804, 14, 960, 14), S['gold'])
    for ax in (818, 884):                                                       # 二楼拱窗
        d.pieslice((ax, 26, ax + 26, 52), 180, 360, fill=C('#ffffff'))
        rect(d, (ax, 39, ax + 26, 62), '#ffffff')
        d.pieslice((ax + 2, 28, ax + 24, 50), 180, 360, fill=C('#8cb0c8'))
        rect(d, (ax + 2, 39, ax + 24, 60), '#8cb0c8')
        for k in range(ax + 3, ax + 24, 3):                                     # 蕾丝窗帘
            line(d, (k, 34, k, 60), '#f4eef2')
        line(d, (ax + 13, 28, ax + 13, 60), '#ffffff')
        rect(d, (ax - 2, 62, ax + 28, 65), S['wain2'])
        for fx in range(ax, ax + 27, 3):
            ellipse(d, (fx - 1, 59, fx + 2, 62), ['#e85a8a', '#f8f0f4', '#c8a8e8'][(fx // 3) % 3])
    rect(d, (938, 26, 960, 62), '#ffffff')                                      # 最右一扇（被画框切掉一半）
    rect(d, (940, 28, 960, 60), '#8cb0c8')
    # 招牌：深紫底、金框、白字 Cinderella（拉丁小字）+ 片假名，左边一只玻璃鞋
    sx0, sx1, sy = 814, 952, G - 64
    rect(d, (sx0, sy, sx1, sy + 16), S['gold2'])
    rect(d, (sx0 + 1, sy + 1, sx1 - 1, sy + 15), '#3a2a44')
    line(d, (sx0 + 1, sy + 1, sx1 - 1, sy + 1), '#5a4a64')
    tw, th = kanji_size('シンデレラ')
    kanji(im, (sx0 + sx1) // 2 - tw // 2 + 8, sy + 2, 'シンデレラ', S['gold3'])
    d = ImageDraw.Draw(im)
    gx, gy = sx0 + 8, sy + 4                                                    # 玻璃鞋
    poly(d, [(gx, gy + 8), (gx + 2, gy + 3), (gx + 6, gy + 6), (gx + 12, gy + 6), (gx + 13, gy + 9), (gx + 1, gy + 9)], '#c8e4f4')
    line(d, (gx + 2, gy + 3, gx + 6, gy + 6), '#ffffff')
    line(d, (gx + 1, gy + 9, gx + 1, gy + 11), '#c8e4f4')
    # 一楼：大玻璃窗（店里的镜台、吊灯）+ 白色木门
    rect(d, (806, G - 46, 960, G), '#ffffff')
    rect(d, (806, G - 48, 960, G - 46), S['gold'])
    mwx0, mwx1 = 814, 890
    rect(d, (mwx0, G - 42, mwx1, G - 8), S['gold2'])
    im = grad(im, (mwx0 + 1, G - 41, mwx1 - 1, G - 9), ('#f6e8f0', '#ecd8e4', '#dcc4d4'))
    d = ImageDraw.Draw(im)
    for mx in (832, 870):                                                       # 窗里：椭圆镜 + 粉椅
        ellipse(d, (mx - 8, G - 38, mx + 8, G - 20), S['gold'])
        ellipse(d, (mx - 6, G - 36, mx + 6, G - 22), '#d4dee6')
        rect(d, (mx - 5, G - 18, mx + 5, G - 10), S['pink'])
    line(d, (852, G - 41, 852, G - 34), S['gold2'])
    rect(d, (848, G - 34, 856, G - 32), '#fff4c8')
    for k in range(3):
        line(d, (mwx0 + 3 + k * 6, G - 40, mwx0 + 10 + k * 6, G - 33), '#ffffff')
    sdx0, sdx1 = 904, 934                                                      # 门
    rect(d, (sdx0 - 2, G - 46, sdx1 + 2, G), S['gold2'])
    rect(d, (sdx0, G - 44, sdx1, G - 1), '#f8f4f6')
    bevel(d, (sdx0 + 3, G - 41, sdx1 - 3, G - 24), '#d8ccd4', '#ffffff')
    rect(d, (sdx0 + 5, G - 39, sdx1 - 5, G - 26), '#c8dcea')                    # 门上的小窗
    bevel(d, (sdx0 + 3, G - 21, sdx1 - 3, G - 4), '#d8ccd4', '#ffffff')
    rect(d, (sdx1 - 7, G - 24, sdx1 - 5, G - 20), S['gold3'])
    for tx in (894, 940):                                                      # 修剪成球的灌木（白盆）
        rect(d, (tx, G - 10, tx + 10, G), '#f8f4f0')
        line(d, (tx, G - 10, tx + 10, G - 10), '#ffffff')
        rect(d, (tx + 4, G - 14, tx + 6, G - 10), '#5a4234')
        ellipse(d, (tx - 1, G - 28, tx + 11, G - 13), '#2e5e3a')
        ellipse(d, (tx + 1, G - 27, tx + 8, G - 19), '#4a7c48')
        px(d, tx + 3, G - 25, '#6e9e5a')
    awning(im, 806, 960, G - 52, 6, ('#3a2a44', '#f0dce4'), scallop=True)
    d = ImageDraw.Draw(im)
    # ---------------- 人行道 + 路缘 + 马路
    im = sidewalk(im, 0, W, G, 146)
    d = ImageDraw.Draw(im)
    im = dither_fill(im, (0, G, W, G + 2), '#8a867e', '#a4a098', .5)           # 檐下阴影
    im = asphalt(im, 0, W, 146, 180, dash=False)
    d = ImageDraw.Draw(im)
    for x in range(8, W, 36):                                                  # 中线（虚线，靠下）
        rect(d, (x, 170, x + 16, 171), '#e8e4d8')
    for x in range(0, W):                                                      # 路边的白实线
        px(d, x, 150, '#d8d4c8')
    for gx in (186, 520, 880):                                                 # 排水沟铁箅子（路缘）
        rect(d, (gx, 147, gx + 14, 149), '#3a3a40')
        for k in range(gx + 1, gx + 14, 2):
            px(d, k, 148, '#6a6a72')
    # ---------------- 电线杆 + 电线
    poles = [108, 452, 702, 958]
    for x in poles:
        im = pole(im, x, G + 4, 118)
    im = wires(im, [(-10, 12)] + [(x, G + 4 - 118 + 7) for x in poles] + [(980, 14)], sag=7)
    d = ImageDraw.Draw(im)
    # ---------------- 停着的车（路边，车身底在 y 158，人站在车前面）
    hood1, _ = car_side(d, 516, 158, body='#f4f4f0', dark='#c8ccd4', glass='#5a7a98', kind='sedan')
    hood2, _ = car_side(d, 742, 158, body='#e8e0d0', dark='#b8b0a0', glass='#5a7a98', kind='truck')
    im = dither_fill(im, (514, 158, 594, 160), '#3a3a40', '#4e4e54', .5)
    im = dither_fill(im, (740, 158, 808, 160), '#3a3a40', '#4e4e54', .5)
    d = ImageDraw.Draw(im)
    # 烟头：马路上，裁缝店门口斜前方
    butt = [214, 166]
    rect(d, (butt[0] - 2, butt[1], butt[0] + 2, butt[1]), '#f4f0e6')
    px(d, butt[0] - 3, butt[1], '#d89a5a')
    px(d, butt[0] + 3, butt[1], '#ff6a2a')
    # 裁缝店 'after'：橱窗碎了（另做覆盖层，这里只返回位置）
    info = dict(tailor_window=(swx0, swx1), tailor_door=(dx0, dx1), vend=vend, hood_car=hood1, hood_truck=hood2, butt=butt,
                salon_door=(sdx0, sdx1), salon_window=(mwx0, mwx1), poles=poles)
    if after:
        d = ImageDraw.Draw(im)
        rng = np.random.RandomState(31)
        rect(d, (swx0 + 2, G - 42, swx1 - 2, G - 10), '#2a2a2e')               # 橱窗只剩黑洞 + 挂着的碎玻璃
        for k in range(12):
            x = rng.randint(swx0 + 2, swx1 - 6)
            top = rng.random() < .5
            y = G - 42 if top else G - 10
            poly(d, [(x, y), (x + rng.randint(3, 8), y), (x + rng.randint(1, 5), y + (rng.randint(4, 10) if top else -rng.randint(4, 10)))],
                 '#b8ccd6')
        for mx in (140, 212):                                                  # 人台倒了：只剩杆
            rect(d, (mx, G - 20, mx + 1, G - 12), '#6a4a34')
        for k in range(26):                                                    # 人行道上的碎玻璃
            x, y = rng.randint(swx0 - 10, swx1 + 30), rng.randint(G + 2, 146)
            px(d, x, y, '#e8f4fa')
            if rng.rand() < .5:
                px(d, x + 1, y, '#a8c4d4')
        im = dither_fill(im, (swx0, G - 50, swx1, G - 44), '#4a4a4e', '#2a2a2e', .4)  # 窗上沿熏黑
    if closed:
        d = ImageDraw.Draw(im)
        rect(d, (mwx0 + 1, G - 41, mwx1 - 1, G - 9), '#d8d0d8')                # 橱窗：百叶拉下
        for yy in range(G - 41, G - 9, 3):
            line(d, (mwx0 + 1, yy, mwx1 - 1, yy), '#b8acb8')
        rect(d, (sdx0 + 5, G - 39, sdx1 - 5, G - 26), '#c8bcc8')                # 门窗也拉了帘
        line(d, (sdx0 + 10, G - 46, (sdx0 + sdx1) // 2, G - 52), '#8a6a4a')    # 门上挂的木牌「本日休業」
        line(d, (sdx1 - 10, G - 46, (sdx0 + sdx1) // 2, G - 52), '#8a6a4a')
        rect(d, (sdx0 - 2, G - 42, sdx1 + 2, G - 25), '#7a5234')
        rect(d, (sdx0 - 1, G - 41, sdx1 + 1, G - 26), '#f4ecd8')
        tw, th = kanji_size('休業')
        kanji(im, (sdx0 + sdx1) // 2 - tw // 2, G - 41 + (15 - th) // 2, '休業', '#c83a34')
    return im, G, info


def overlay_diff(base, changed):
    a, b = np.array(base), np.array(changed)
    diff = np.any(a != b, axis=2)
    lay = np.zeros_like(b)
    lay[diff] = b[diff]
    return Image.fromarray(lay, 'RGBA')


def avenue_far():
    im = sky_far(640, seed=21, sea=False, cols=('#5a9ee8', '#78b4f0', '#a0ccf4', '#cce4f6'))
    d = ImageDraw.Draw(im)
    # 夏天的积雨云（远处一大朵）
    for k, (cx, cy, r) in enumerate(((150, 70, 26), (176, 58, 30), (204, 66, 24), (228, 78, 18), (126, 82, 18), (190, 84, 26))):
        ellipse(d, (cx - r, cy - r, cx + r, cy + r), '#f4f8fc')
        ellipse(d, (cx - r + 4, cy - r + 2, cx + r - 6, cy + r - 8), '#ffffff')
    rect(d, (100, 84, 260, 100), '#f4f8fc')
    line(d, (104, 100, 256, 100), '#c8d8ea')
    for x in range(108, 256, 6):
        px(d, x, 99, '#dce6f2')
    rng = np.random.RandomState(22)
    for i in range(14):                                                        # 远处的楼和山
        x = rng.randint(-10, 640)
        bw, bh = rng.randint(18, 40), rng.randint(20, 50)
        y = 118 - bh
        rect(d, (x, y, x + bw, 130), ['#c4ccd4', '#d4d0c8', '#b8c2cc'][rng.randint(3)])
        for wy in range(y + 4, 116, 6):
            for wx in range(x + 3, x + bw - 3, 5):
                px(d, wx, wy, '#8ea4b8')
    return im


def morioh_avenue():
    W = 960
    far = avenue_far()
    near, G, info = avenue_near()
    after_full, _, _ = avenue_near(after=True)
    closed_full, _, _ = avenue_near(closed=True)
    after = overlay_diff(near, after_full)
    closed = overlay_diff(near, closed_full)
    smoke = smoke_strip(16, 44, 8, '#9a9894', seed=5)
    heat = shimmer_strip(24, 22, 6, seed=1)
    heat_big = shimmer_strip(30, 26, 6, seed=2)
    butt_smoke = smoke_strip(8, 16, 8, '#d8d8dc', seed=7)
    layers = {'far': far, 'near': near, 'after': after, 'closed': closed, 'smoke': smoke, 'heat': heat, 'heat_big': heat_big,
              'butt_smoke': butt_smoke}
    tx0, tx1 = info['tailor_window']
    td0, td1 = info['tailor_door']
    sd0, sd1 = info['salon_door']
    h1, h2, vend, butt = info['hood_car'], info['hood_truck'], info['vend'], info['butt']
    anchors = dict(tobacco=[40, 146], tailor_window=[(tx0 + tx1) // 2, 146], tailor_door=[(td0 + td1) // 2, 146],
                   alley=[307, 146], vending=[vend[0] - 12, 146], vending_back=vend, car=[554, 166], car_hood=h1,
                   truck=[774, 166], truck_hood=h2, butt=butt, bus_stop=[740, 146], road_mid=[480, 164], jotaro_down=[620, 168],
                   salon_window=[852, 146], salon_door=[(sd0 + sd1) // 2, 146], walk_x=[8, 952])
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176], anchors=anchors,
                layers=[{'type': 'pano', 'image': 'bg/morioh_avenue/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/morioh_avenue/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/morioh_avenue/after', 'k': 1, 'x': 0, 'y': 0, 'key': 'after'},
                        {'type': 'strip', 'image': 'bg/morioh_avenue/smoke', 'n': 8, 'fps': 6, 'x': (tx0 + tx1) // 2 - 8,
                         'y': G - 86, 'k': 1, 'key': 'after'},
                        {'type': 'image', 'image': 'bg/morioh_avenue/closed', 'k': 1, 'x': 0, 'y': 0, 'key': 'closed'},
                        {'type': 'strip', 'image': 'bg/morioh_avenue/butt_smoke', 'n': 8, 'fps': 5, 'x': butt[0] - 1, 'y': butt[1] - 16,
                         'k': 1},
                        {'type': 'strip', 'image': 'bg/morioh_avenue/heat_big', 'n': 6, 'fps': 8, 'x': h1[0] - 26, 'y': h1[1] - 24,
                         'k': 1, 'key': 'heat_car'},
                        {'type': 'strip', 'image': 'bg/morioh_avenue/heat', 'n': 6, 'fps': 8, 'x': h2[0] - 12, 'y': h2[1] - 20,
                         'k': 1, 'key': 'heat_truck'},
                        {'type': 'strip', 'image': 'bg/morioh_avenue/heat', 'n': 6, 'fps': 8, 'x': vend[0] - 12, 'y': vend[1] - 24,
                         'k': 1, 'key': 'heat_vend'},
                        {'type': 'strip', 'image': 'bg/morioh_avenue/heat', 'n': 6, 'fps': 8, 'x': butt[0] - 12, 'y': butt[1] - 22,
                         'k': 1, 'key': 'heat_butt'},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    pv.alpha_composite(butt_smoke.crop((0, 0, 8, 16)), (butt[0] - 1, butt[1] - 16))
    preview('morioh_avenue', {'room': pv}, ['room'], W)
    pv2 = pv.copy()
    pv2.alpha_composite(after)
    pv2.alpha_composite(smoke.crop((0, 0, 16, 44)), ((tx0 + tx1) // 2 - 8, G - 86))
    pv2.alpha_composite(closed)
    for (x, y, im_, w) in ((h1[0] - 26, h1[1] - 24, heat_big, 30), (h2[0] - 12, h2[1] - 20, heat, 24), (vend[0] - 12, vend[1] - 24, heat, 24),
                           (butt[0] - 12, butt[1] - 22, heat, 24)):
        pv2.alpha_composite(im_.crop((0, 0, w, im_.height)), (x, y))
    preview('morioh_avenue_toggles', {'room': pv2}, ['room'], W)
    save_layers('morioh_avenue', layers, meta)
    return meta


SCENES = {'cinderella_salon': cinderella_salon, 'tailor_shop': tailor_shop, 'morioh_avenue': morioh_avenue}


def main(keys):
    path = os.path.join(LIB.META, 'bg_ch7.json')
    meta = LIB.load_json(path, {}) or {}
    for k in keys or SCENES:
        meta[k] = SCENES[k]()
        print('背景', k)
    LIB.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
