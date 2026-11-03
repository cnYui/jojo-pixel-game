# 第四部第2章（葡萄丘高中 / 锁与表面）的背景：5 张，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_ch2.json（build_p4.py 会把 _meta/bg_*.json 并进 bg.json）。
#   用法：python3 第四部/tools/art/p4_bg_ch2.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   图层 pack 一律 'ch2'（打包成 data/img_bg_ch2.js，进第2章时才加载）。
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import liv_floor, preview, save_layers, sky_far  # noqa: E402

PACK = 'ch2'

# 3×5 的大写字母（招牌、门牌用；数字用 p4_bglib.DIG）
LET = {'A': ['010', '101', '111', '101', '101'], 'B': ['110', '101', '110', '101', '110'], 'C': ['011', '100', '100', '100', '011'],
       'D': ['110', '101', '101', '101', '110'], 'E': ['111', '100', '110', '100', '111'], 'F': ['111', '100', '110', '100', '100'],
       'G': ['011', '100', '101', '101', '011'], 'H': ['101', '101', '111', '101', '101'], 'I': ['111', '010', '010', '010', '111'],
       'K': ['101', '101', '110', '101', '101'], 'L': ['100', '100', '100', '100', '111'], 'M': ['10001', '11011', '10101', '10001', '10001'],
       'N': ['1001', '1101', '1011', '1001', '1001'], 'O': ['010', '101', '101', '101', '010'], 'P': ['110', '101', '110', '100', '100'],
       'R': ['110', '101', '110', '101', '101'], 'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'],
       'U': ['101', '101', '101', '101', '111'], 'V': ['101', '101', '101', '101', '010'], 'Y': ['101', '101', '010', '010', '010'],
       '-': ['000', '000', '111', '000', '000'], ' ': ['000'] * 5, '.': ['000', '000', '000', '000', '010']}


def letters(d, x, y, text, col, gap=1):
    """3×5 小字（M、N 宽一点）：字母 + 数字混排"""
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


def clock_face(d, cx, cy, r, hh, mm, rim='#7a5434', face='#f6f0e0', hand='#2a2a30', tick='#a8a090'):
    """挂钟：hh:mm（时针按分钟往前走一点）"""
    ellipse(d, (cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), rim)
    ellipse(d, (cx - r, cy - r, cx + r, cy + r), face)
    for i in range(12):
        a = i * math.pi / 6
        px(d, cx + (r - 1) * math.sin(a), cy - (r - 1) * math.cos(a), tick if i % 3 else hand)
    am = mm / 60 * 2 * math.pi
    ah = (hh % 12 + mm / 60) / 12 * 2 * math.pi
    line(d, (cx, cy, cx + (r - 2) * math.sin(am), cy - (r - 2) * math.cos(am)), hand)
    line(d, (cx, cy, cx + (r - 4) * math.sin(ah), cy - (r - 4) * math.cos(ah)), hand)
    px(d, cx, cy, '#c83a34')


def poly(d, pts, col):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=C(col))


def mask_dither(mask, soft=1.5, levels=3):
    """0/255 的硬蒙版 → 边缘按 4×4 Bayer 抖动的 0..1 场（光斑的半影）"""
    m = mask.filter(ImageFilter.BoxBlur(soft)) if soft else mask
    f = np.array(m).astype(float) / 255
    h, w = f.shape
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    return np.clip(np.floor(f * levels + bay) / levels, 0, 1)


def light_mix(base, lit, field):
    """field（0..1）处用 lit 替换 base；只看 0 / 1，半档已经抖动过"""
    a, b = np.array(base), np.array(lit)
    sel = field >= 0.5
    a[sel] = b[sel]
    return Image.fromarray(a, 'RGBA')


def glow_from_field(f, col, levels=6):
    """强度场 → lighter 叠加用的光晕图（颜色即亮度），同 p4_bg.lamp_glow 的抖动量化"""
    h, w = f.shape
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    fq = np.clip(np.floor(f * levels + bay) / levels, 0, 1)
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * np.array(col, float), 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def dust_strip(w, h, n=12, count=16, cols=('#fff2c8', '#ffd890'), region=None, seed=0):
    """光柱里浮着的灰尘：每粒沿一个小圈转、一圈正好 n 帧（首尾接得上），亮度跟着一闪一闪。
    region(x, y) → True 的位置才放（落在光柱里）"""
    rng = np.random.RandomState(seed)
    out = Image.new('RGBA', (w * n, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    motes = []
    tries = 0
    while len(motes) < count and tries < 5000:
        tries += 1
        x, y = rng.uniform(3, w - 3), rng.uniform(3, h - 3)
        if region and not region(x, y):
            continue
        motes.append((x, y, rng.uniform(1.2, 3.2), rng.uniform(0, 2 * np.pi), rng.choice([-1, 1]), rng.randint(len(cols)),
                      rng.uniform(0, 2 * np.pi)))
    for f in range(n):
        for x, y, r, ph, sgn, ci, tw in motes:
            a = ph + sgn * 2 * np.pi * f / n
            X, Y = x + r * np.cos(a), y + r * .6 * np.sin(a)
            b = .5 + .5 * np.sin(tw + 2 * np.pi * f / n * 2)
            if b < .25:
                continue
            d.point((int(f * w + X), int(Y)), fill=C(cols[ci], 255 if b > .7 else 170))
    return out


def flag_strip(w=16, h=11, n=6, cols=('#f4f0e6', '#d8d2c4', '#c83a34'), emblem=None, seed=0):
    """旗杆上飘的小旗：n 帧，正弦波沿旗面往后传；emblem(d, ox, oy, k) 在旗面中间画徽记"""
    out = Image.new('RGBA', (w * n, h + 4), (0, 0, 0, 0))
    a = np.array(out)
    for f in range(n):
        for x in range(w):
            amp = 1.6 * (x / w)
            dy = int(round(amp * np.sin(x / 3.2 - 2 * np.pi * f / n)))
            shade = np.cos(x / 3.2 - 2 * np.pi * f / n)
            base = c3(cols[1] if shade < -.35 else cols[0])
            for y in range(h):
                Y = y + 2 + dy
                if 0 <= Y < h + 4:
                    a[Y, f * w + x] = (*base, 255)
        if emblem:
            im = Image.fromarray(a, 'RGBA')
            emblem(ImageDraw.Draw(im), f * w, 2, f)
            a = np.array(im)
    return Image.fromarray(a, 'RGBA')


# ============================================================ 康一家客厅 hirose_living（320 宽，一屏，下午 4 点的斜阳）
#   左：通走廊的门（能开：image 层 key 'door'）→ 餐边柜 + 面包箱，上面挂钟停在 4:07 → 双人沙发（玉美给妈妈捶肩）→
#   书柜 → 右边的大窗：太阳从右上斜照进来，地板上两块窗格形的光斑，空气里有光柱和浮尘。
HL = dict(paper='#efe0c4', paper2='#e6d4b4', paper3='#dcc8a4', ceil='#d4c2a0', ceil2='#c0ac88',
          wd='#5e4030', wm='#7e5a40', wl='#9a7450', wh='#b88e64',
          wain='#8e7a5e', wain_in='#84704f', wain_hi='#a89272', wain_lo='#6a5a42')


def hl_room():
    W, G = 320, 134
    P = HL
    im = new(W, 180, P['paper'])
    d = ImageDraw.Draw(im)
    # 墙纸：细菱格小花
    for y in range(12, G, 10):
        for x in range((y // 10) % 2 * 5, W, 10):
            px(d, x, y, P['paper3'])
            px(d, x + 1, y + 1, P['paper2'])
            px(d, x - 1, y + 1, P['paper2'])
    im = grad(im, (0, 10, W, 30), (P['ceil'], P['paper2'], P['paper']))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 8), P['ceil2'])
    line(d, (0, 8, W, 8), P['wh'])
    line(d, (0, 9, W, 9), P['wl'])
    # 护墙板（y 106–134）
    WT = 106
    rect(d, (0, WT, W, G), P['wain'])
    rect(d, (0, WT, W, WT + 2), P['wh'])
    line(d, (0, WT + 3, W, WT + 3), P['wain_lo'])
    for x in range(2, W, 24):
        rect(d, (x + 2, WT + 7, x + 20, G - 7), P['wain_in'])
        bevel(d, (x + 2, WT + 7, x + 20, G - 7), P['wain_lo'], P['wain_hi'])
    rect(d, (0, G - 4, W, G), P['wd'])
    line(d, (0, G - 4, W, G - 4), P['wm'])

    # ---------------- 门（8–46）：木门 + 一条磨砂玻璃，门框，门把
    dx0, dx1, dy0 = 8, 46, G - 76
    rect(d, (dx0 - 4, dy0 - 4, dx1 + 4, G), P['wd'])
    line(d, (dx0 - 4, dy0 - 4, dx1 + 4, dy0 - 4), P['wl'])
    line(d, (dx0 - 4, dy0 - 4, dx0 - 4, G), P['wl'])
    rect(d, (dx0, dy0, dx1, G - 1), '#a07a52')
    bevel(d, (dx0, dy0, dx1, G - 1), '#b88e64', '#7e5a40')
    rect(d, (dx0 + 6, dy0 + 6, dx1 - 6, dy0 + 34), '#d8e0dc')          # 磨砂玻璃
    for yy in range(dy0 + 7, dy0 + 34, 3):
        line(d, (dx0 + 7, yy, dx1 - 7, yy), '#e8eee8')
    bevel(d, (dx0 + 6, dy0 + 6, dx1 - 6, dy0 + 34), '#7e5a40', '#c8a07a')
    rect(d, (dx0 + 6, dy0 + 40, dx1 - 6, G - 8), '#946e48')            # 下面的门板
    bevel(d, (dx0 + 6, dy0 + 40, dx1 - 6, G - 8), '#7e5a40', '#b08a60')
    rect(d, (dx1 - 7, dy0 + 36, dx1 - 3, dy0 + 38), '#d8c070')         # 门把
    px(d, dx1 - 7, dy0 + 39, '#a89040')
    # ---------------- 餐边柜（54–112）+ 面包箱 + 挂钟 4:07 + 日历
    sx0, sx1, st = 54, 112, G - 34
    rect(d, (sx0, st, sx1, G - 2), P['wm'])
    rect(d, (sx0 - 2, st - 3, sx1 + 2, st), P['wl'])
    line(d, (sx0 - 2, st - 3, sx1 + 2, st - 3), P['wh'])
    for k in range(2):
        x = sx0 + 3 + k * 28
        rect(d, (x, st + 3, x + 24, G - 6), '#8e6a48')
        bevel(d, (x, st + 3, x + 24, G - 6), '#a8805a', '#6a4a30')
        rect(d, (x + 10, st + 8, x + 14, st + 9), '#d8c070')
    rect(d, (sx0 + 2, G - 3, sx0 + 4, G), P['wd'])
    rect(d, (sx1 - 4, G - 3, sx1 - 2, G), P['wd'])
    bx0, bx1, by1 = 60, 88, st - 3                                     # 面包箱（奶油色，红边）
    rect(d, (bx0, by1 - 12, bx1, by1), '#f2e6c8')
    d.pieslice((bx0, by1 - 22, bx1, by1 - 2), 180, 360, fill=C('#f2e6c8'))
    d.arc((bx0, by1 - 22, bx1, by1 - 2), 180, 360, fill=C('#d84a3a'))
    line(d, (bx0, by1 - 12, bx0, by1), '#d84a3a')
    line(d, (bx1, by1 - 12, bx1, by1), '#d84a3a')
    line(d, (bx0, by1, bx1, by1), '#b83a2e')
    line(d, (bx0 + 2, by1 - 9, bx1 - 2, by1 - 9), '#e2d4b2')
    rect(d, (bx0 + 11, by1 - 7, bx0 + 17, by1 - 6), '#b83a2e')
    letters(d, bx0 + 7, by1 - 17, 'BREAD', '#b83a2e', gap=0)
    rect(d, (94, by1 - 8, 102, by1), '#6a8ac0')                       # 小花瓶
    rect(d, (95, by1 - 9, 101, by1 - 8), '#8aa8d8')
    for k, (fx, fy) in enumerate(((95, -14), (98, -17), (101, -13))):
        line(d, (98, by1 - 9, fx, by1 + fy + 2), '#4e8a52')
        ellipse(d, (fx - 2, by1 + fy - 1, fx + 2, by1 + fy + 3), ('#f2a0b4', '#f8e070', '#f2a0b4')[k])
    clock_face(d, 76, 60, 9, 4, 7)                                     # 挂钟停在 4:07（放在对白框下面：对白框盖住 y 6–46）
    rect(d, (75, 48, 77, 49), '#5e4030')
    rect(d, (96, 34, 110, 56), '#f6f2e8')                              # 日历（1999 年 4 月）
    rect(d, (96, 34, 110, 39), '#3a8a5a')
    for r in range(4):
        for c in range(4):
            px(d, 98 + c * 3, 42 + r * 3.5, '#6a6a70' if c else '#d84a3a')
    # ---------------- 沙发（122–206）：苔绿色双人沙发，上面挂一幅风景画
    fx0, fx1 = 126, 202
    rect(d, (fx0 + 6, 86, fx1 - 6, 112), '#5e7a4e')
    rect(d, (fx0 + 6, 86, fx1 - 6, 88), '#86a26e')
    for k in range(2):
        cx0 = fx0 + 8 + k * 31
        rect(d, (cx0, 90, cx0 + 29, 110), '#6a8858')
        line(d, (cx0, 90, cx0 + 29, 90), '#94b07a')
        line(d, (cx0 + 29, 90, cx0 + 29, 110), '#4e6640')
        for bx in (cx0 + 9, cx0 + 20):                                # 拉扣
            px(d, bx, 99, '#4e6640')
    rect(d, (fx0 + 6, 110, fx1 - 6, 120), '#769466')
    line(d, (fx0 + 6, 110, fx1 - 6, 110), '#94b07a')
    line(d, (fx0 + 37, 111, fx0 + 37, 119), '#4e6640')
    rect(d, (fx0 + 4, 120, fx1 - 4, 127), '#4e6640')
    for ax in (fx0, fx1 - 10):
        rect(d, (ax, 100, ax + 10, 127), '#5e7a4e')
        ellipse(d, (ax - 1, 96, ax + 11, 106), '#6a8858')
        line(d, (ax + 1, 98, ax + 9, 98), '#94b07a')
        line(d, (ax + 10, 102, ax + 10, 127), '#3e5432')
    for lx in (fx0 + 4, fx1 - 7):
        rect(d, (lx, 127, lx + 3, G - 1), P['wd'])
    rect(d, (fx0 + 40, 100, fx0 + 52, 110), '#f0d8a8')                 # 叠好的毛毯
    line(d, (fx0 + 40, 104, fx0 + 52, 104), '#d8b880')
    rect(d, (140, 34, 188, 66), '#6a4a30')                             # 风景画：杜王港
    rect(d, (142, 36, 186, 64), '#e8d6a8')
    im = grad(im, (144, 38, 185, 52), ('#9cc8e8', '#c4dcec'))
    d = ImageDraw.Draw(im)
    rect(d, (144, 52, 185, 62), '#4e88b8')
    for x in range(146, 184, 5):
        px(d, x, 55 + (x // 5) % 2 * 3, '#a8d0ec')
    poly(d, [(150, 52), (158, 45), (166, 52)], '#7a9a6a')
    poly(d, [(160, 52), (172, 42), (184, 52)], '#5e8058')
    rect(d, (170, 47, 172, 52), '#f4f0e6')
    line(d, (164, 30, 142, 34), '#5a5a5e')
    line(d, (164, 30, 186, 34), '#5a5a5e')
    # ---------------- 书柜（212–240）
    kx0, kx1 = 212, 240
    rect(d, (kx0, 46, kx1, G - 1), P['wm'])
    line(d, (kx0, 46, kx1, 46), P['wh'])
    line(d, (kx1, 46, kx1, G - 1), P['wd'])
    rng = np.random.RandomState(12)
    books = ['#c84a3a', '#3a6ac8', '#e0c040', '#4aa060', '#e8e0d0', '#8a5aa8', '#d88a3a', '#3a8a8a']
    for sy in (50, 72, 94):
        rect(d, (kx0 + 2, sy, kx1 - 2, sy + 19), '#4a3222')
        x = kx0 + 3
        while x < kx1 - 4:
            bw = rng.randint(2, 4)
            bh = rng.randint(12, 18)
            c = books[rng.randint(len(books))]
            rect(d, (x, sy + 19 - bh, x + bw - 1, sy + 18), c)
            px(d, x, sy + 19 - bh, mix(c, '#ffffff', .4))
            x += bw
        rect(d, (kx0 + 2, sy + 19, kx1 - 2, sy + 20), P['wl'])
    rect(d, (kx0 + 2, 116, kx1 - 2, G - 4), '#6a4a30')
    bevel(d, (kx0 + 3, 117, kx1 - 3, G - 5), '#8a6644', '#4e3622')
    rect(d, (kx0 + 6, 34, kx0 + 22, 46), '#c8a868')                    # 书柜顶上的相框（康一一家）
    rect(d, (kx0 + 7, 35, kx0 + 21, 45), '#d8e4ec')
    for k, (hx, hc) in enumerate(((kx0 + 10, '#5a4a40'), (kx0 + 14, '#c8a050'), (kx0 + 18, '#5a4a40'))):
        ellipse(d, (hx - 2, 38, hx + 1, 41), hc)
        rect(d, (hx - 2, 41, hx + 1, 45), ('#e88a8a', '#8aa8d8', '#f0c060')[k])
    # ---------------- 窗（250–312）：外面是斜阳下的邻居屋顶和电线杆
    wx0, wy0, wx1, wy1 = 250, 26, 312, 92
    rect(d, (wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4), '#f4ecd8')
    bevel(d, (wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4), '#fffaf0', '#cfc4ac')
    im = grad(im, (wx0, wy0, wx1, wy1), ('#f6b878', '#f8c88c', '#fad8a4', '#fce4bc'))
    d = ImageDraw.Draw(im)
    cloud(im, 256, 40, 30, seed=5, cols=('#fff2dc', '#fce0bc', '#f4c49a'))
    d = ImageDraw.Draw(im)
    poly(d, [(wx0, 70), (262, 62), (286, 62), (300, 70), (wx1, 70), (wx1, wy1), (wx0, wy1)], '#9a6a5a')
    for xx in range(wx0, wx1, 4):
        line(d, (xx, 62 + abs(xx - 280) // 4, xx + 2, 62 + abs(xx - 280) // 4), '#7a5048')
    rect(d, (wx0, 70, wx1, wy1), '#e8c49a')
    rect(d, (262, 74, 274, 84), '#f8e0a8')
    rect(d, (288, 74, 300, 84), '#c8a07a')
    rect(d, (wx0, 86, wx1, wy1), '#a87a5e')
    line(d, (wx0, 86, wx1, 86), '#c89a76')
    rect(d, (302, wy0, 304, wy1), '#6a5048')                           # 电线杆
    line(d, (wx0, 44, wx1, 50), '#6a5048')
    line(d, (wx0, 47, wx1, 53), '#6a5048')
    rect(d, (279, wy0, 281, wy1), '#f4ecd8')                           # 窗框十字
    line(d, (wx0, 58, wx1, 58), '#f4ecd8')
    rect(d, (wx0 - 8, wy1 + 4, wx1 + 6, wy1 + 8), '#e8dcc4')
    line(d, (wx0 - 8, wy1 + 4, wx1 + 6, wy1 + 4), '#fffaf0')
    line(d, (wx0 - 8, wy1 + 8, wx1 + 6, wy1 + 8), '#b8ac92')
    # 蕾丝窗帘（左边束起）+ 右边一层薄纱
    rect(d, (wx0 - 12, wy0 - 8, wx0 + 6, wy1 + 12), '#f4f0e6')
    for x in range(wx0 - 12, wx0 + 6, 3):
        line(d, (x, wy0 - 8, x, wy1 + 12), '#e2dccb')
    for y in range(wy1 + 4, wy1 + 12, 2):
        for x in range(wx0 - 12 + (y // 2) % 2, wx0 + 6, 2):
            px(d, x, y, '#d8d0bc')
    rect(d, (wx0 - 12, 68, wx0 + 6, 70), '#c8a07a')
    rect(d, (wx1 - 4, wy0 - 8, wx1 + 8, wy1 + 12), '#f4f0e6')
    for x in range(wx1 - 4, wx1 + 8, 3):
        line(d, (x, wy0 - 8, x, wy1 + 12), '#e2dccb')
    rect(d, (wx0 - 14, wy0 - 12, wx1 + 10, wy0 - 8), P['wm'])
    line(d, (wx0 - 14, wy0 - 12, wx1 + 10, wy0 - 12), P['wh'])
    # 窗台上的仙人掌和招财猫
    rect(d, (262, wy1 - 2, 270, wy1 + 4), '#c06a4a')
    rect(d, (264, wy1 - 12, 268, wy1 - 2), '#5a9a5a')
    rect(d, (261, wy1 - 9, 263, wy1 - 5), '#5a9a5a')
    px(d, 266, wy1 - 13, '#f2a0b4')
    rect(d, (290, wy1 - 6, 298, wy1 + 3), '#f8f4ec')
    ellipse(d, (289, wy1 - 12, 299, wy1 - 3), '#f8f4ec')
    px(d, 291, wy1 - 12, '#f8f4ec'); px(d, 297, wy1 - 12, '#f8f4ec')
    px(d, 292, wy1 - 8, '#2a2a30'); px(d, 296, wy1 - 8, '#2a2a30')
    rect(d, (299, wy1 - 9, 300, wy1 - 5), '#f8f4ec')
    rect(d, (291, wy1 - 3, 297, wy1 - 2), '#d84a3a')
    # ---------------- 墙角的落地灯（窗和书柜之间）
    rect(d, (244, 60, 246, G - 2), '#8a8a90')
    poly(d, [(238, 50), (252, 50), (256, 62), (234, 62)], '#f2e2c0')
    line(d, (234, 62, 256, 62), '#d8c49a')
    rect(d, (240, G - 3, 250, G - 1), '#6a6a70')
    # ---------------- 地板 + 地毯
    im = liv_floor(im, 0, W, G)
    d = ImageDraw.Draw(im)
    rx0, ry0, rx1, ry1 = 104, 146, 230, 170                            # 椭圆地毯
    ellipse(d, (rx0, ry0, rx1, ry1), '#c8a87a')
    ellipse(d, (rx0 + 3, ry0 + 2, rx1 - 3, ry1 - 2), '#5e8aa0')
    ellipse(d, (rx0 + 8, ry0 + 4, rx1 - 8, ry1 - 4), '#6e9ab0')
    ellipse(d, (rx0 + 24, ry0 + 8, rx1 - 24, ry1 - 8), '#c8a87a')
    ellipse(d, (rx0 + 26, ry0 + 9, rx1 - 26, ry1 - 9), '#6e9ab0')
    # 门口的拖鞋
    for k, sx in enumerate((14, 26)):
        ellipse(d, (sx, 140, sx + 9, 144), '#d86a7a' if k else '#6a8ac8')
        rect(d, (sx + 1, 140, sx + 5, 142), mix('#d86a7a' if k else '#6a8ac8', '#ffffff', .3))
    return im, G, (wx0, wy0, wx1, wy1, 279, 58)


def hl_door_open(G):
    """门开着的样子：门板转到左边成一条窄边，门洞里是走廊（冷一点、暗一点）"""
    im = new(320, 180)
    d = ImageDraw.Draw(im)
    dx0, dx1, dy0 = 8, 46, G - 76
    rect(d, (dx0, dy0, dx1, G - 1), '#8a8a7e')                       # 走廊墙
    rect(d, (dx0, dy0, dx1, dy0 + 6), '#6e6e66')
    rect(d, (dx0, G - 14, dx1, G - 1), '#7a6450')                    # 走廊地板（往里收）
    poly(d, [(dx0, G - 1), (dx1, G - 1), (dx1 - 6, G - 14), (dx0 + 6, G - 14)], '#8a7058')
    rect(d, (dx0 + 14, dy0 + 18, dx0 + 30, dy0 + 40), '#a8a89a')     # 对面的窗（暗）
    line(d, (dx0 + 22, dy0 + 18, dx0 + 22, dy0 + 40), '#8a8a7e')
    rect(d, (dx0 + 8, G - 26, dx0 + 14, G - 14), '#5a5a52')          # 鞋柜一角
    rect(d, (dx0, dy0, dx0 + 5, G - 1), '#a07a52')                   # 门板侧面
    line(d, (dx0 + 5, dy0, dx0 + 5, G - 1), '#7e5a40')
    rect(d, (dx0 + 4, dy0 + 36, dx0 + 7, dy0 + 38), '#d8c070')
    return im


def hirose_living():
    W = 320
    room, G, (wx0, wy0, wx1, wy1, mx, my) = hl_room()
    # 斜阳：太阳在右上，透过窗格落到地板上（越高的窗格落得越靠前、越往左）。
    #   窗格 → 地面：y_floor = G + (G − y)·KD，x 往左挪 (y_floor − G)·SL
    KD, SL = 0.42, 1.25
    panes = [(wx0 + 1, wy0 + 1, mx - 1, my - 1), (mx + 2, wy0 + 1, wx1 - 1, my - 1), (wx0 + 1, my + 1, mx - 1, wy1 - 1),
             (mx + 2, my + 1, wx1 - 1, wy1 - 1)]

    def proj(x, y):
        yf = G + (G - y) * KD
        return x - (yf - G) * SL, min(179.0, yf)

    floor_m = Image.new('L', (W, 180), 0)
    fd = ImageDraw.Draw(floor_m)
    shaft_polys = []
    for x0, y0, x1, y1 in panes:
        quad = [proj(x0, y1), proj(x1, y1), proj(x1, y0), proj(x0, y0)]
        fd.polygon([(int(round(a)), int(round(b))) for a, b in quad], fill=255)
        shaft_polys.append([(x0, y0), (x1, y0), (x1, y1), quad[1], quad[2], quad[3], quad[0], (x0, y1)])
    fm = mask_dither(floor_m, 1.2, 3)
    fm[:G + 1] = 0
    # 墙上的一小块反光（窗台下、书柜侧面被照到一点）
    wall_m = Image.new('L', (W, 180), 0)
    wd = ImageDraw.Draw(wall_m)
    wd.polygon([(241, 64), (249, 60), (249, 132), (241, 133)], fill=255)
    wm = mask_dither(wall_m, 1, 3)
    base = tint(room, (.9, .84, .84), (0, 0, 6))                      # 背光的一面偏暗、偏紫一点
    lit = tint(room, (1.12, 1.0, .78), (34, 18, 0))
    out = light_mix(base, lit, np.maximum(fm, wm * .6))
    # 窗里本来就是亮的，不压暗
    a, r = np.array(out), np.array(room)
    a[wy0:wy1 + 1, wx0:wx1 + 1] = r[wy0:wy1 + 1, wx0:wx1 + 1]
    out = Image.fromarray(a, 'RGBA')
    # 光柱：从窗格到光斑的体积，越往下越淡；lighter 叠加
    shaft = Image.new('L', (W, 180), 0)
    sd = ImageDraw.Draw(shaft)
    for pts in shaft_polys:
        hull = cv_hull(pts)
        sd.polygon([(int(round(a_)), int(round(b_))) for a_, b_ in hull], fill=255)
    sh = np.array(shaft.filter(ImageFilter.BoxBlur(2))).astype(float) / 255
    yy = np.mgrid[0:180, 0:W][0].astype(float)
    # 窗下一段淡入（贴着窗的地方不要一片白），到半空最亮，落到地板前再淡掉；不抖动、分 3 档硬过渡（像素画里常见的光柱）
    k = (yy - wy1) / (180 - wy1)
    fall = np.clip(np.minimum((yy - wy0) / 40, 1) * (1 - .55 * np.clip(k, 0, 1)), 0, 1)
    f = sh * .13 * fall
    f[wy0:wy1 + 1, wx0:wx1 + 1] = 0
    fq = np.round(f * 24) / 24
    glow = Image.fromarray(np.dstack([np.clip(fq[..., None] * np.array((255, 196, 120), float), 0, 255).astype(np.uint8),
                                      np.where(fq > 0, 255, 0).astype(np.uint8)[..., None]]).reshape(180, W, 4), 'RGBA')
    # 浮尘（光柱里）：帧条的范围 = 光柱外接框
    ys, xs = np.where(sh > .5)
    bx0, by0, bx1, by1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    region = lambda x, y: sh[min(179, int(y + by0)), min(W - 1, int(x + bx0))] > .6 and not (wx0 <= x + bx0 <= wx1 and wy0 <= y + by0 <= wy1)
    dust = dust_strip(bx1 - bx0, by1 - by0, n=12, count=22, region=region, seed=7)
    door = hl_door_open(G)
    layers = {'room': out, 'glow': glow, 'dust': dust, 'door_open': door}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(door=[27, 148], door_in=[27, 140], clock=[76, 60], breadbox=[74, 146], sofa=[164, 146],
                             shelf=[226, 146], window=[281, 60], sun=[200, 158], walk_x=[52, 312]),
                layers=[{'type': 'pano', 'image': 'bg/hirose_living/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/hirose_living/door_open', 'k': 1, 'x': 0, 'y': 0, 'key': 'door'},
                        {'type': 'glow', 'image': 'bg/hirose_living/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.04},
                        {'type': 'strip', 'image': 'bg/hirose_living/dust', 'n': 12, 'fps': 5, 'x': bx0, 'y': by0, 'k': 1},
                        {'type': 'tint', 'color': '#ff9a40', 'alpha': 0.06}],
                fg=[])
    prev = out.copy()
    prev.alpha_composite(door if False else new(W, 180))
    pv = np.array(prev).astype(int)
    g = np.array(glow).astype(int)
    pv[..., :3] = np.clip(pv[..., :3] + g[..., :3] * (g[..., 3:4] > 0), 0, 255)
    pv = Image.fromarray(pv.astype(np.uint8), 'RGBA')
    pv.alpha_composite(dust.crop((0, 0, bx1 - bx0, by1 - by0)), (bx0, by0))
    preview('hirose_living', {'room': pv}, ['room'], W)
    save_layers('hirose_living', layers, meta)
    return meta


def cv_hull(pts):
    """凸包（光柱的体积 = 窗格四角 + 光斑四角的凸包）"""
    pts = sorted(set((float(x), float(y)) for x, y in pts))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


# ============================================================ 葡萄丘高中走廊 budogaoka_hall（640 宽，早上）
#   左边教室 1-A：前门、一排储物柜（间田的柜子在中间偏右，能打开：image 层 key 'locker'）、后门、告示板；
#   中间的柱子上是消火栓箱；右边教室 3-A：腰窗里看得见课桌（间田的空座位靠窗）、后门；最右是楼梯口和绿色的安全出口灯。
#   身后那排窗户的阳光斜着落在墙上和地上（几块亮的窗形光斑）。第3章也会用这张图。
HALL = dict(ceil='#d6d2c6', ceil2='#bcb8ac', wall='#ece6d6', wall2='#e0d8c6', wall3='#d2c8b2',
            low='#8eb4a6', low2='#7aa292', low_hi='#a8c8ba', low_lo='#5e8476', rail='#4e7a6c',
            door='#b08a5e', door2='#946e48', door_hi='#c8a274', door_lo='#7a5636')


def hall_door(d, x, G, plate):
    """教室的拉门：上半两块玻璃（里面是教室的窗光），下半木板；门上伸出班牌"""
    P = HALL
    top = G - 70
    rect(d, (x - 3, top - 4, x + 35, G), P['rail'])
    rect(d, (x, top, x + 32, G - 1), P['door'])
    bevel(d, (x, top, x + 32, G - 1), P['door_hi'], P['door_lo'])
    line(d, (x + 16, top, x + 16, G - 1), P['door2'])
    for k in range(2):
        gx = x + 3 + k * 16
        rect(d, (gx, top + 5, gx + 10, top + 30), '#bcd6e2')
        line(d, (gx + 1, top + 6, gx + 4, top + 9), '#e2eef4')
        rect(d, (gx, top + 22, gx + 10, top + 30), '#a6c2d0')            # 里面课桌的影子
        bevel(d, (gx, top + 5, gx + 10, top + 30), P['door_lo'], P['door_hi'])
        rect(d, (gx + 1, top + 36, gx + 9, G - 6), P['door2'])
        bevel(d, (gx + 1, top + 36, gx + 9, G - 6), P['door_lo'], P['door_hi'])
    rect(d, (x + 13, top + 34, x + 14, top + 40), '#3a3a40')               # 拉手
    rect(d, (x + 18, top + 34, x + 19, top + 40), '#3a3a40')
    # 班牌：从门框上方伸出来的白牌子（侧着看是一条，正面的字往外）
    rect(d, (x + 8, top - 15, x + 26, top - 6), '#f6f4ee')
    bevel(d, (x + 8, top - 15, x + 26, top - 6), '#ffffff', '#c8c4b8')
    rect(d, (x + 16, top - 6, x + 17, top - 4), '#8a8a90')
    letters(d, x + 17 - text_w(plate) // 2, top - 13, plate, '#2a3a5a')


def locker_bank(d, x0, n, G, open_i=None, tags=True):
    """两层的钢制储物柜：每格 14 宽；open_i = 那一格画成开着（另做一层）"""
    top = G - 56
    rect(d, (x0 - 1, top - 3, x0 + n * 14 + 1, G), '#6e7a74')
    rect(d, (x0 - 2, top - 4, x0 + n * 14 + 2, top - 2), '#9aa69e')
    for i in range(n):
        x = x0 + i * 14
        for r, (y0, y1) in enumerate(((top, top + 25), (top + 27, G - 4))):
            rect(d, (x + 1, y0, x + 13, y1), '#a8b4ac')
            bevel(d, (x + 1, y0, x + 13, y1), '#c4d0c8', '#7e8a84')
            for vy in range(y0 + 3, y0 + 9, 2):                           # 通风口
                line(d, (x + 4, vy, x + 10, vy), '#7e8a84')
            rect(d, (x + 10, y0 + 12, x + 11, y0 + 15), '#5a625e')         # 把手
            if tags:
                rect(d, (x + 3, y0 + 11, x + 8, y0 + 13), '#f6f4ee')
                line(d, (x + 4, y0 + 12, x + 7, y0 + 12), '#9a9aa8')
    rect(d, (x0 - 1, G - 3, x0 + n * 14 + 1, G), '#4e5852')


def locker_open_layer(W, x, G):
    """间田的柜子（上层）开着：门转到左边成一条，里面黑，探出一截木偶的手（只是一截木头色的手臂，没脸）"""
    im = new(W, 180)
    d = ImageDraw.Draw(im)
    top = G - 56
    rect(d, (x + 1, top, x + 13, top + 25), '#2a2a30')
    rect(d, (x + 2, top + 1, x + 12, top + 3), '#3e3e46')
    rect(d, (x + 2, top + 18, x + 12, top + 19), '#5a5a62')                # 隔板
    rect(d, (x + 3, top + 12, x + 8, top + 17), '#3a4a8a')                 # 课本
    rect(d, (x - 3, top - 1, x + 1, top + 26), '#b8c4bc')                  # 门板（朝外开）
    line(d, (x - 3, top - 1, x - 3, top + 26), '#e0eae4')
    line(d, (x + 1, top - 1, x + 1, top + 26), '#7e8a84')
    for vy in range(top + 3, top + 9, 2):
        px(d, x - 2, vy, '#7e8a84')
    return im


def hall_room():
    W, G = 640, 136
    P = HALL
    im = new(W, 180, P['wall'])
    d = ImageDraw.Draw(im)
    # 天花板 + 日光灯
    rect(d, (0, 0, W, 10), P['ceil'])
    line(d, (0, 10, W, 10), P['ceil2'])
    line(d, (0, 11, W, 11), P['wall3'])
    for x in range(30, W, 96):
        rect(d, (x, 10, x + 40, 12), '#bab6aa')
        rect(d, (x + 2, 12, x + 38, 14), '#fffff4')
        line(d, (x + 2, 15, x + 38, 15), '#d8d6cc')
    im = grad(im, (0, 12, W, 30), (P['wall3'], P['wall2'], P['wall']))
    d = ImageDraw.Draw(im)
    # 腰壁（y 94–G）：薄荷绿，上沿一条深色扶手
    LT = 94
    rect(d, (0, LT, W, G), P['low'])
    rect(d, (0, LT - 3, W, LT), P['rail'])
    line(d, (0, LT - 3, W, LT - 3), P['low_hi'])
    line(d, (0, LT + 1, W, LT + 1), P['low_lo'])
    for x in range(0, W, 3):
        if (x // 3) % 7 == 0:
            line(d, (x, LT + 2, x, G - 4), P['low2'])
    rect(d, (0, G - 4, W, G), '#4e6a60')
    # 教室上方的欄間窗（y 20–40）：透过去看到教室那一侧的窗外天空
    for x0, x1 in ((0, 290), (338, 616)):
        rect(d, (x0, 18, x1, 42), P['rail'])
        for wx in range(x0 + 3, x1 - 3, 24):
            ww = min(21, x1 - 3 - wx)
            im = grad(im, (wx, 21, wx + ww, 39), ('#a8d0ee', '#c4e0f4', '#e2f0f8'))
            d = ImageDraw.Draw(im)
            rect(d, (wx, 33, wx + ww, 39), '#9cc48a')                          # 远处的树梢
            for tx in range(wx, wx + ww, 3):
                px(d, tx, 32 + (tx // 3) % 2, '#7aaa6a')
            line(d, (wx + 2, 22, wx + 6, 26), '#f4faff')
        line(d, (x0, 42, x1, 42), '#9aa69e')
    # ---------------- 教室 1-A（0–290）：前门、储物柜、后门、告示板
    hall_door(d, 14, G, '1-A')
    locker_bank(d, 56, 11, G)
    hall_door(d, 216, G, '1-A')
    # 告示板（254–288，y 54–90）
    bx0, by0, bx1, by1 = 252, 52, 290, 90
    rect(d, (bx0, by0, bx1, by1), '#7a5636')
    rect(d, (bx0 + 2, by0 + 2, bx1 - 2, by1 - 2), '#c89a62')
    rng = np.random.RandomState(3)
    for y in range(by0 + 3, by1 - 2, 2):
        for x in range(bx0 + 3 + (y // 2) % 2, bx1 - 2, 3):
            if rng.rand() < .4:
                px(d, x, y, '#b48650')
    posters = [(bx0 + 4, by0 + 4, 12, 15, '#f6f4ee', '#d84a3a'), (bx0 + 18, by0 + 5, 14, 11, '#fff2a8', '#3a6ac8'),
               (bx0 + 5, by0 + 22, 10, 13, '#c8e4f4', '#2a3a5a'), (bx0 + 18, by0 + 19, 15, 16, '#f6f4ee', '#4aa060')]
    for x, y, w, h, c, ink in posters:
        rect(d, (x, y, x + w, y + h), c)
        line(d, (x, y + h + 1, x + w, y + h + 1), '#8a6440')
        for ly in range(y + 3, y + h - 1, 2):
            line(d, (x + 2, ly, x + w - 2 - (ly % 3), ly), mix(c, ink, .55))
        rect(d, (x + 1, y + 1, x + w - 1, y + 2), ink)
        px(d, x + w // 2, y - 1, '#d84a3a')                                  # 图钉
    ellipse(d, (bx0 + 6, by0 + 26, bx0 + 12, by0 + 32), '#d84a3a')           # 红圈（“禁止”海报）
    ellipse(d, (bx0 + 7, by0 + 27, bx0 + 11, by0 + 31), '#c8e4f4')
    # ---------------- 柱子（290–338）：消火栓箱 + 红灯 + 校内广播喇叭
    rect(d, (290, 12, 338, G), '#e4ddca')
    line(d, (290, 12, 290, G), '#f4eee0')
    line(d, (338, 12, 338, G), '#c4bca8')
    rect(d, (290, LT - 3, 338, G), P['low'])
    rect(d, (290, LT - 3, 338, LT), P['rail'])
    rect(d, (290, G - 4, 338, G), '#4e6a60')
    rect(d, (300, 70, 328, 118), '#c83a34')                                  # 消火栓箱
    bevel(d, (300, 70, 328, 118), '#e86a5a', '#8a2420')
    rect(d, (303, 76, 325, 92), '#e8e4dc')
    letters(d, 306, 81, 'FIRE', '#c83a34')
    rect(d, (303, 96, 325, 114), '#a82e28')
    rect(d, (321, 104, 323, 107), '#e8c860')
    ellipse(d, (309, 58, 319, 68), '#8a2420')                                # 红灯
    ellipse(d, (310, 59, 318, 67), '#e84a3a')
    px(d, 312, 61, '#ffb0a0')
    rect(d, (306, 22, 322, 34), '#5a5a62')                                  # 广播喇叭
    rect(d, (308, 24, 320, 32), '#3a3a42')
    for yy in (25, 27, 29, 31):
        line(d, (309, yy, 319, yy), '#5a5a62')
    # ---------------- 教室 3-A（338–616）：前门、腰窗里的课桌、后门
    hall_door(d, 346, G, '3-A')
    # 腰窗（y 50–90）里看得见教室：黑板一角、课桌、靠窗那张是空的（间田的座位）
    wx0, wx1, wy0, wy1 = 388, 548, 50, 90
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), P['rail'])
    im = grad(im, (wx0, wy0, wx1, wy1), ('#e6e2d4', '#ddd8c8', '#d2ccba'))
    d = ImageDraw.Draw(im)
    rect(d, (wx0, wy0, wx1, wy0 + 14), '#cfe2ea')                            # 教室对面的窗
    for x in range(wx0 + 4, wx1, 22):
        rect(d, (x, wy0 + 1, x + 1, wy0 + 14), '#eaf2f4')
    rect(d, (wx0, wy0 + 14, wx1, wy0 + 15), '#b8b2a2')
    for row, (yy, sc) in enumerate(((wy0 + 22, 1.0), (wy0 + 30, 1.0))):
        for k, x in enumerate(range(wx0 + 6 + row * 7, wx1 - 10, 19)):
            empty = row == 0 and k == 6                                       # 空座位：没有书包、椅子推进去了
            rect(d, (x, yy, x + 12, yy + 2), '#c8a274')                       # 桌面
            rect(d, (x + 1, yy + 3, x + 2, yy + 8), '#8a8a90')
            rect(d, (x + 10, yy + 3, x + 11, yy + 8), '#8a8a90')
            if not empty:
                rect(d, (x + 3, yy - 3, x + 8, yy - 1), ['#3a3a48', '#5a4a3a', '#2a3a5a'][(k + row) % 3])
                rect(d, (x + 4, yy + 5, x + 10, yy + 7), '#b08a5e')            # 拉出来的椅子
            else:
                rect(d, (x + 3, yy + 2, x + 9, yy + 4), '#a07a50')
    for x in range(wx0 + 40, wx1, 40):                                       # 窗框
        rect(d, (x - 1, wy0, x, wy1), P['rail'])
    line(d, (wx0, wy0, wx0 + 6, wy0 + 6), '#ffffff')
    line(d, (wx0 + 40, wy0, wx0 + 46, wy0 + 6), '#ffffff')
    hall_door(d, 570, G, '3-A')
    # ---------------- 楼梯口（616–640）：往上的扶手 + 安全出口灯
    rect(d, (616, 12, W, G), '#d8d0bc')
    line(d, (616, 12, 616, G), '#c4bca8')
    for k in range(7):
        rect(d, (618 + k * 3, G - 6 - k * 9, W, G - k * 9), '#c8c0aa')
        line(d, (618 + k * 3, G - 6 - k * 9, W, G - 6 - k * 9), '#e4dcc8')
    line(d, (620, G - 18, W, G - 72), '#6a5a48')
    line(d, (620, G - 17, W, G - 71), '#8a7a62')
    rect(d, (620, 46, 638, 54), '#2a9a5a')                                  # 安全出口（绿底白人）
    rect(d, (621, 47, 637, 53), '#3ac06a')
    px(d, 627, 48, '#ffffff'); line(d, (627, 49, 625, 52), '#ffffff'); line(d, (627, 50, 629, 51), '#ffffff')
    rect(d, (632, 48, 635, 52), '#f4f4ec')
    # ---------------- 地板：打蜡的木地板，带一点倒影
    rect(d, (0, G, W, 180), '#b8946a')
    y, h, row = G, 3.0, 0
    rng = np.random.RandomState(9)
    while y < 180:
        yb = min(180, int(round(y + h)))
        rect(d, (0, int(y), W, yb - 1), ['#b8946a', '#ae8a60', '#c09c70', '#b28e64'][row % 4])
        line(d, (0, yb - 1, W, yb - 1), '#8e6c48')
        y += h
        h = min(9.0, h * 1.2)
        row += 1
    a = np.array(im)
    ref = a[G - 34:G][::-1].astype(float)                                   # 墙脚往下翻过来，混 18%
    fl = a[G:G + 34].astype(float)
    fade = np.linspace(.2, .04, 34)[:, None, None]
    fl[..., :3] = fl[..., :3] * (1 - fade) + ref[..., :3] * fade
    a[G:G + 34] = fl.astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    for x in range(0, W, 40):                                                # 日光灯的反光
        line(d, (x + 10, G + 6, x + 22, G + 6), '#d8bc94')
    line(d, (0, G, W, G), '#6e5236')
    return im, G


def budogaoka_hall():
    W = 640
    room, G = hall_room()
    # 身后（镜头这一侧）那排窗的阳光：在墙上和地上各落一串窗形光斑，右边来的光，往左斜
    wall_m = Image.new('L', (W, 180), 0)
    floor_m = Image.new('L', (W, 180), 0)
    wd, fd = ImageDraw.Draw(wall_m), ImageDraw.Draw(floor_m)
    for x in range(40, W, 112):
        for k in range(2):                                                   # 一扇窗两格
            xa = x + k * 30
            wd.polygon([(xa, 52), (xa + 26, 48), (xa + 26, 90), (xa, 94)], fill=255)
            fd.polygon([(xa - 14, 144), (xa + 12, 144), (xa - 6, 178), (xa - 34, 178)], fill=255)
    wm = mask_dither(wall_m, 1.2, 3)
    fm = mask_dither(floor_m, 1.2, 3)
    fm[:G + 2] = 0
    base = tint(room, (.95, .95, .97))
    lit = tint(room, (1.08, 1.05, .96), (18, 14, 4))
    out = light_mix(base, lit, np.maximum(wm, fm))
    lk = 56 + 6 * 14                                                        # 间田的柜子：左数第 7 格（上层）
    layers = {'room': out, 'locker_open': locker_open_layer(W, lk, G)}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(door_a1=[30, 146], door_a2=[232, 146], lockers=[133, 146], hazamada_locker=[lk + 7, 146],
                             board=[271, 146], hydrant=[314, 146], door_b1=[362, 146], window_b=[468, 146],
                             empty_seat=[507, 74], door_b2=[586, 146], stairs=[628, 146], walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/budogaoka_hall/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/budogaoka_hall/locker_open', 'k': 1, 'x': 0, 'y': 0, 'key': 'locker'}],
                fg=[])
    pv = out.copy()
    preview('budogaoka_hall', {'room': pv}, ['room'], W)
    save_layers('budogaoka_hall', layers, meta)
    return meta


# ============================================================ 商店街 morioh_shopping_street（960 宽，白天）
#   两层、三层的铺面房一字排开：书店、果蔬店、理发店（转灯）、老酒铺（杉玉、啤酒箱）、小巷、电器店（电视墙在播）、
#   蛋糕店、鞋店、拉面店。街灯上挂着竖幅（会飘），灯和灯之间拉着四月的塑料樱花串。往右走出画面就是铁路道口。
def kanji(im, x, y, text, col, vertical=False, size=12):
    """文泉驿点阵正黑 12 px 点阵字（招牌用）；vertical = 竖排。返回 (宽, 高)"""
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


def facade(im, x0, x1, top, G, wall, trim, seed=0, win='#9cc0d4', floors=2, sign_y=None):
    """铺面房的上半截：外墙（贴砖的横纹）、每层一排窗、楼顶的女儿墙。返回招牌带的 y"""
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    rect(d, (x0, top, x1, G), wall)
    for yy in range(top + 3, G, 3):
        line(d, (x0, yy, x1, yy), mix(wall, '#000000', .06))
    rect(d, (x0, top - 3, x1, top), trim)
    line(d, (x0, top - 3, x1, top - 3), mix(trim, '#ffffff', .3))
    line(d, (x0, top + 1, x1, top + 1), mix(wall, '#000000', .2))
    rect(d, (x1 - 2, top, x1, G), mix(wall, '#000000', .14))
    sy = sign_y or (G - 62)
    fh = (sy - top - 6) // max(1, floors - 1) if floors > 1 else 0
    for f in range(floors - 1):
        wy = top + 6 + f * fh
        n = max(1, (x1 - x0 - 10) // 30)
        gap = (x1 - x0 - n * 22) // (n + 1)
        for i in range(n):
            wx = x0 + gap + i * (22 + gap)
            curtain = ['#e8d8b0', '#c8d8e8', None, '#f0c8c8'][rng.randint(4)]
            window(d, (wx, wy, wx + 22, wy + min(18, fh - 8)), frame='#f4f2ec', glass=(win, mix(win, '#ffffff', .4)), curtain=curtain)
            if rng.rand() < .35:                                                 # 晾的毛巾 / 空调外机
                rect(d, (wx + 4, wy + min(18, fh - 8) + 3, wx + 18, wy + min(18, fh - 8) + 4), '#8a8a90')
            elif rng.rand() < .4:
                rect(d, (wx + 24, wy + 6, wx + 31, wy + 12), '#e4e4de')
                ellipse(d, (wx + 25, wy + 7, wx + 29, wy + 11), '#a4a4a8')
    return sy


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
    """遮阳篷：正面看是一条往外斜的条纹带 + 下摆的波浪边"""
    d = ImageDraw.Draw(im)
    for i in range(depth):
        for x in range(x0 - i // 3, x1 + i // 3 + 1):
            k = ((x - x0 + 200) // 6) % 2
            px(d, x, y + i, mix(cols[k], '#000000', .08 * (i / depth)))
    if scallop:
        for x in range(x0 - depth // 3, x1 + depth // 3, 6):
            ellipse(d, (x, y + depth - 2, x + 5, y + depth + 2), cols[((x - x0 + 200) // 6) % 2])
    line(d, (x0, y, x1, y), mix(cols[0], '#ffffff', .4))


def bike(d, x, g, frame='#3a6ac8'):
    """停着的自行车（侧面）"""
    for wx in (x, x + 14):
        d.ellipse((wx - 5, g - 10, wx + 5, g), outline=C('#2a2a30'))
        px(d, wx, g - 5, '#8a8a90')
    line(d, (x, g - 5, x + 6, g - 10), frame)
    line(d, (x + 6, g - 10, x + 14, g - 5), frame)
    line(d, (x + 6, g - 10, x + 7, g - 5), frame)
    line(d, (x + 7, g - 5, x, g - 5), frame)
    line(d, (x + 4, g - 12, x + 6, g - 10), frame)
    rect(d, (x + 2, g - 13, x + 6, g - 12), '#2a2a30')                        # 座
    line(d, (x + 13, g - 13, x + 14, g - 5), '#8a8a90')
    rect(d, (x + 11, g - 14, x + 16, g - 13), '#2a2a30')                       # 车把
    rect(d, (x + 14, g - 13, x + 19, g - 9), '#a8a8b0')                        # 车筐


def crate_stack(d, x, g, n, col='#e8c030', bottle='#6a3a1e'):
    """啤酒箱（塑料筐）一摞，每箱露出一排瓶颈"""
    for k in range(n):
        y = g - (k + 1) * 9
        rect(d, (x, y, x + 20, y + 8), col)
        rect(d, (x + 2, y + 3, x + 18, y + 6), mix(col, '#000000', .25))
        line(d, (x, y, x + 20, y), mix(col, '#ffffff', .35))
        for bx in range(x + 2, x + 19, 3):
            rect(d, (bx, y - 3, bx + 1, y), bottle)
            px(d, bx, y - 4, '#d8c070')


def fruit_display(d, x0, x1, g, seed=0):
    """果蔬店门口一层层的木箱：橙、苹果、香蕉、西瓜，插着价签"""
    rng = np.random.RandomState(seed)
    fruits = [('#f08a20', '#f8b050'), ('#d83a34', '#f06a5a'), ('#f0d040', '#f8e888'), ('#4a9a40', '#70c060'),
              ('#8a3a8a', '#b060b0'), ('#e8e0a0', '#f8f4d0')]
    for tier, (y, ix) in enumerate(((g - 8, 0), (g - 16, 6), (g - 24, 12))):
        for x in range(x0 + ix, x1 - ix - 14, 16):
            rect(d, (x, y, x + 14, y + 7), '#a87a4a')
            line(d, (x, y, x + 14, y), '#c89a62')
            line(d, (x, y + 4, x + 14, y + 4), '#8a6038')
            fc = fruits[rng.randint(len(fruits))]
            for fx in range(x + 1, x + 13, 3):
                ellipse(d, (fx, y - 3, fx + 3, y), fc[0])
                px(d, fx + 1, y - 3, fc[1])
            rect(d, (x + 5, y - 7, x + 10, y - 4), '#f6f4ee')                    # 价签
            line(d, (x + 6, y - 6, x + 9, y - 6), '#d83a34')
            line(d, (x + 7, y - 4, x + 7, y - 2), '#8a6038')


def tv_frames(n=8):
    """电器店橱窗里 2×3 台电视的画面（每台 12×9），n 帧：天气图、新闻主播、彩条、棒球场、动画、雪花"""
    rng = np.random.RandomState(4)
    frames = []
    progs = ['weather', 'news', 'bars', 'ball', 'toon', 'snow']
    for f in range(n):
        fr = []
        for t in range(6):
            im = new(12, 9, '#101418')
            d = ImageDraw.Draw(im)
            prog = progs[(t + f // 2) % len(progs)] if t != 2 else ('bars' if f % 4 < 2 else 'news')
            if prog == 'weather':
                rect(d, (0, 0, 11, 8), '#3a7ad8')
                poly(d, [(3, 1), (7, 2), (8, 6), (5, 8), (2, 5)], '#5ab05a')
                px(d, 5, 3 + f % 2, '#f8f8f8')
                px(d, 6, 5, '#f0c030')
            elif prog == 'news':
                rect(d, (0, 0, 11, 8), '#2a3a6a')
                ellipse(d, (4, 1, 7, 4), '#e8c4a0')
                rect(d, (3, 4, 8, 8), '#3a3a48')
                rect(d, (0, 7, 11, 8), '#d83a34')
                if f % 2:
                    px(d, 5, 3, '#a8604a')
            elif prog == 'bars':
                for i, c in enumerate(('#f0f0f0', '#f0e040', '#40e0e0', '#40e040', '#e040e0', '#e04040', '#4040e0')):
                    rect(d, (i * 12 // 7, 0, (i + 1) * 12 // 7, 8), c)
            elif prog == 'ball':
                rect(d, (0, 0, 11, 8), '#4aa040')
                poly(d, [(6, 2), (10, 5), (6, 8), (2, 5)], '#c89a62')
                px(d, 3 + f % 6, 3, '#f8f8f8')
            elif prog == 'toon':
                rect(d, (0, 0, 11, 8), '#f8d8a0')
                ellipse(d, (3, 2 + f % 2, 8, 7 + f % 2), '#f0a0b0')
                px(d, 4, 4 + f % 2, '#2a2a30'); px(d, 7, 4 + f % 2, '#2a2a30')
            else:
                for yy in range(9):
                    for xx in range(12):
                        if rng.rand() < .5:
                            px(d, xx, yy, '#c8c8c8' if rng.rand() < .6 else '#6a6a6a')
            fr.append(im)
        frames.append(fr)
    return frames


def barber_strip(n=8, w=6, h=22):
    """理发店的转灯：玻璃筒里红白蓝斜条往上走，n 帧一圈"""
    out = new(w * n, h + 6)
    d = ImageDraw.Draw(out)
    cols = ['#d83a34', '#f8f8f4', '#3a5ac8', '#f8f8f4']
    for f in range(n):
        ox = f * w
        rect(d, (ox, 0, ox + w - 1, 2), '#c8ccd4')
        rect(d, (ox, h + 3, ox + w - 1, h + 5), '#c8ccd4')
        for y in range(h):
            for x in range(1, w - 1):
                k = ((y + x * 2 + f * 16 // n) // 4) % 4
                c = cols[k]
                if x == 1:
                    c = mix(c, '#000000', .15)
                elif x == w - 2:
                    c = mix(c, '#ffffff', .25)
                px(d, ox + x, y + 3, c)
        line(d, (ox, 3, ox, h + 2), '#a8acb4')
        line(d, (ox + w - 1, 3, ox + w - 1, h + 2), '#a8acb4')
    return out


def banner_strip(n=4, w=10, h=28, cols=('#f4a0be', '#ffffff'), text='杜王'):
    """街灯上挂的竖幅：上端挂在横杆上，下摆左右轻轻飘"""
    out = new(w * n, h + 2)
    base = new(8, h, cols[0])
    bd = ImageDraw.Draw(base)
    rect(bd, (0, 0, 7, 1), mix(cols[0], '#000000', .2))
    for y in range(4, h - 2, 7):                                            # 樱花瓣的小点花纹
        px(bd, 2 + (y // 7) % 3, y, cols[1]); px(bd, 5, y + 3, cols[1])
    for f in range(n):
        sway = [0, 1, 1, 0][f % 4]
        sw2 = [0, 0, 1, 1][f % 4]
        for y in range(h):
            dx = int(round((sway if y > h * .6 else sw2 if y > h * .3 else 0)))
            row = base.crop((0, y, 8, y + 1))
            out.paste(row, (f * w + 1 + dx, y), row)
    return out


def lamp_post(im, x, g, h=88):
    """商店街的街灯：细杆、顶上的灯罩、往右伸出一根挂竖幅的横杆"""
    d = ImageDraw.Draw(im)
    top = g - h
    rect(d, (x - 1, top, x + 1, g), '#5a6a5e')
    line(d, (x - 1, top, x - 1, g), '#7a8a7e')
    rect(d, (x - 3, g - 4, x + 3, g), '#4a564e')
    rect(d, (x - 6, top - 6, x + 6, top - 1), '#4a564e')
    poly(d, [(x - 5, top - 1), (x + 5, top - 1), (x + 3, top + 6), (x - 3, top + 6)], '#f4f0dc')
    line(d, (x - 5, top - 1, x + 5, top - 1), '#3a443e')
    rect(d, (x - 1, top + 6, x + 1, top + 7), '#4a564e')
    rect(d, (x + 1, top + 14, x + 12, top + 15), '#5a6a5e')                  # 竖幅横杆
    return (x + 2, top + 16)


def sakura_garland(im, pts, sag=6, seed=0):
    """灯和灯之间的塑料樱花串：一根下垂的线，线上每隔几 px 一朵粉花"""
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        prev = None
        steps = int(abs(xb - xa))
        for i in range(steps + 1):
            t = i / max(1, steps)
            x = xa + (xb - xa) * t
            y = ya + (yb - ya) * t + sag * 4 * t * (1 - t)
            if prev:
                line(d, (prev[0], prev[1], x, y), '#6a7a6e')
            prev = (x, y)
            if i % 5 == 2:
                c = ['#f4a0be', '#ffd6e4', '#ec88ac'][rng.randint(3)]
                px(d, x, y + 1, c); px(d, x - 1, y + 1, c); px(d, x + 1, y + 1, c); px(d, x, y + 2, c)
                px(d, x, y, mix(c, '#ffffff', .5))
            elif i % 5 == 4 and rng.rand() < .5:
                px(d, x, y + 1, '#5a9a5a')


def paving(im, x0, x1, y0, y1):
    """商店街的地砖：米色砖错缝，每隔几排一道红砖带"""
    d = ImageDraw.Draw(im)
    rect(d, (x0, y0, x1, y1), '#cdbea6')
    row = 0
    y = y0
    h = 4
    while y < y1:
        red = row % 5 == 2
        col = '#b98c74' if red else '#cdbea6'
        rect(d, (x0, y, x1, min(y1, y + h)), col)
        line(d, (x0, y + h, x1, y + h), '#b0a08a' if not red else '#94705c')
        bw = 12 + h * 2
        for x in range(x0 - (row % 2) * bw // 2, x1, bw):
            line(d, (x, y, x, y + h - 1), '#b4a48e' if not red else '#9a7660')
        y += h + 1
        row += 1
        h = min(7, h + (1 if row % 2 else 0))
    noise_specks(im, (x0, y0, x1, y1), ['#bcac94', '#d8cab4'], int((x1 - x0) * (y1 - y0) / 20), y0 + 3)
    d = ImageDraw.Draw(im)
    line(d, (x0, y0, x1, y0), '#8e826e')


def shop_front(im, x0, x1, G, frame='#6a5a48', glass=('#a8c8d8', '#d0e4ec'), door_at=None, door_w=16):
    """一楼铺面：玻璃橱窗 + 玻璃门，返回橱窗的框"""
    d = ImageDraw.Draw(im)
    top = G - 46
    rect(d, (x0, top, x1, G), frame)
    rect(d, (x0 + 2, top + 2, x1 - 2, G - 6), glass[0])
    for i in range(x0 + 4, x1 - 4, 9):
        line(d, (i, top + 3, i + 5, top + 8), glass[1])
    rect(d, (x0, G - 6, x1, G), mix(frame, '#000000', .2))
    if door_at is not None:
        rect(d, (door_at - 1, top + 1, door_at + door_w + 1, G - 1), frame)
        rect(d, (door_at + 1, top + 4, door_at + door_w - 1, G - 2), mix(glass[0], '#000000', .15))
        line(d, (door_at + door_w // 2, top + 4, door_at + door_w // 2, G - 2), frame)
        rect(d, (door_at + door_w // 2 - 3, top + 22, door_at + door_w // 2 - 2, top + 28), '#d8d8dc')
        rect(d, (door_at + door_w // 2 + 2, top + 22, door_at + door_w // 2 + 3, top + 28), '#d8d8dc')
    return (x0 + 2, top + 2, x1 - 2, G - 6)


def shopping_near():
    W, G = 960, 138
    im = new(W, 180)
    d = ImageDraw.Draw(im)
    # ---------------- 1 书店（0–118）
    sy = facade(im, 0, 118, 44, G, '#d8cfc0', '#8a7a68', seed=1)
    signboard(im, 2, 116, sy, 14, '#2a4a7a', '#1a2a4a', '書店', '#f8f4e0')
    d = ImageDraw.Draw(im)
    top = G - 46
    rect(d, (0, top, 118, G), '#6a5040')                                        # 敞开的店面：里面一排排书架
    rect(d, (4, top + 3, 114, G - 2), '#e8dcc0')
    rng = np.random.RandomState(21)
    for sx in range(6, 112, 22):
        rect(d, (sx, top + 4, sx + 18, G - 4), '#8a6648')
        for yy in range(top + 6, G - 6, 8):
            x = sx + 1
            while x < sx + 17:
                bw = rng.randint(1, 3)
                c = ['#c84a3a', '#3a6ac8', '#e0c040', '#4aa060', '#f4f0e6', '#8a5aa8'][rng.randint(6)]
                rect(d, (x, yy, x + bw - 1, yy + 6), c)
                x += bw
            line(d, (sx + 1, yy + 7, sx + 17, yy + 7), '#5e4030')
    for rx in (10, 70):                                                          # 门口的杂志架
        rect(d, (rx, G - 24, rx + 30, G), '#9aa0a8')
        for k in range(3):
            y = G - 22 + k * 7
            line(d, (rx, y + 6, rx + 30, y + 6), '#6a7078')
            for mx in range(rx + 2, rx + 28, 7):
                c = ['#f06a5a', '#5aa0e0', '#f8e070', '#f4f0e6', '#e090c0'][(mx + k) % 5]
                rect(d, (mx, y, mx + 5, y + 5), c)
                line(d, (mx + 1, y + 1, mx + 4, y + 1), mix(c, '#ffffff', .5))
    bike(d, 50, G + 1, '#3a6ac8')
    # ---------------- 2 果蔬店（122–236）：绿篷
    sy = facade(im, 120, 238, 52, G, '#e6dcc8', '#6a8a5a', seed=2)
    signboard(im, 122, 236, sy, 14, '#f8f4e8', '#4a7a3a', '青果', '#3a7a3a')
    d = ImageDraw.Draw(im)
    rect(d, (120, G - 46, 238, G), '#5a4a3a')
    rect(d, (124, G - 44, 234, G - 2), '#3e342a')                               # 店里暗
    for k in range(4):
        rect(d, (130 + k * 26, G - 40, 150 + k * 26, G - 30), '#a87a4a')
    awning(im, 120, 238, G - 48, 10, ('#4a9a4a', '#f4f0e6'))
    d = ImageDraw.Draw(im)
    fruit_display(d, 124, 234, G, seed=4)
    # ---------------- 3 理发店（240–330）：三层，蓝白
    sy = facade(im, 240, 330, 34, G, '#e2e6ec', '#5a7aa8', seed=3, floors=3)
    signboard(im, 242, 328, sy, 14, '#3a5ac8', '#2a3a8a', '理容', '#ffffff')
    d = ImageDraw.Draw(im)
    fr = shop_front(im, 240, 330, G, frame='#e8ecf0', glass=('#b8d4e2', '#dcecf2'), door_at=292, door_w=18)
    d = ImageDraw.Draw(im)
    rect(d, (250, G - 34, 264, G - 8), '#c83a34')                                # 店里的理发椅
    rect(d, (248, G - 20, 266, G - 16), '#c83a34')
    rect(d, (256, G - 8, 258, G - 6), '#8a8a90')
    rect(d, (252, G - 44, 284, G - 38), '#f4f8fa')                               # 镜子
    line(d, (254, G - 42, 260, G - 42), '#ffffff')
    rect(d, (268, G - 30, 284, G - 8), '#d8e4ea')                                # 毛巾架
    for k in range(3):
        line(d, (270, G - 26 + k * 5, 282, G - 26 + k * 5), '#f8f8f4')
    # ---------------- 4 老酒铺（334–470）：木头门脸、瓦檐、杉玉、啤酒箱、自动售货机
    rect(d, (334, 48, 470, G), '#b89a74')
    for xx in range(334, 470, 6):
        line(d, (xx, 48, xx, G), '#a4865e')
    for wx in (344, 432):                                                        # 二楼的格子窗
        rect(d, (wx, 56, wx + 28, 74), '#6a4e34')
        for gx in range(wx + 2, wx + 27, 4):
            line(d, (gx, 57, gx, 73), '#d8c8a4')
        line(d, (wx, 65, wx + 28, 65), '#d8c8a4')
    rect(d, (380, 54, 424, 76), '#3a2a1e')                                       # 木招牌「地酒」
    rect(d, (382, 56, 422, 74), '#5a4030')
    bevel(d, (382, 56, 422, 74), '#7a5a40', '#2e2016')
    tw, th = kanji_size('地酒')
    kanji(im, 402 - tw // 2, 65 - th // 2, '地酒', '#f0e0b0')
    im = tiled_roof(im, 334, 470, 36, 48, ('#4a4e58', '#3a3e46', '#62666e', '#26282e'), overhang=3)
    im = tiled_roof(im, 336, 468, G - 60, G - 50, ('#4a4e58', '#3a3e46', '#62666e', '#26282e'), overhang=4)
    d = ImageDraw.Draw(im)
    rect(d, (334, G - 48, 470, G), '#4a3626')                                    # 店面（拉开的木门）
    rect(d, (338, G - 44, 430, G - 2), '#2e2218')
    for k in range(3):                                                           # 店里的酒架
        rect(d, (342 + k * 30, G - 40, 366 + k * 30, G - 6), '#5a4030')
        for yy in range(G - 38, G - 8, 6):
            for bx in range(344 + k * 30, 364 + k * 30, 3):
                rect(d, (bx, yy, bx + 1, yy + 4), ['#2a5a3a', '#6a3a1e', '#e8e0c8', '#3a2a6a'][(bx + yy) % 4])
    for gx in (432, 450):                                                        # 拉到一边的格子门
        rect(d, (gx, G - 44, gx + 16, G - 1), '#7a5a3a')
        for xx in range(gx + 2, gx + 15, 3):
            line(d, (xx, G - 42, xx, G - 3), '#c8b48a')
    line(d, (420, G - 49, 420, G - 44), '#3a2a1e')                               # 杉玉（挂在檐下）
    ellipse(d, (413, G - 44, 427, G - 30), '#5a6a3a')
    ellipse(d, (414, G - 43, 424, G - 35), '#7a8a4a')
    for k in range(10):
        a = k * 0.63
        px(d, 420 + 6 * math.cos(a), G - 37 + 6 * math.sin(a), '#4a5a2e')
    crate_stack(d, 342, G + 2, 3, '#e8c030')
    crate_stack(d, 364, G + 2, 2, '#d84a3a')
    crate_stack(d, 386, G + 2, 1, '#e8c030')
    im = vending(im, 444, G + 1, body='#3a6ac8', accent='#e8f0f8')
    d = ImageDraw.Draw(im)
    # ---------------- 5 小巷（470–494）
    rect(d, (470, 30, 494, G), '#6a6a70')
    rect(d, (474, 30, 490, G), '#4a4a52')
    for yy in range(40, G, 22):
        rect(d, (476, yy, 488, yy + 1), '#5a5a62')
    rect(d, (486, 40, 488, G - 2), '#7a7a80')                                    # 排水管
    rect(d, (476, G - 14, 486, G), '#4a6a5a')                                    # 垃圾桶
    rect(d, (475, G - 15, 487, G - 13), '#5a7a6a')
    # ---------------- 6 电器店（494–632）：现代楼、宽招牌、电视墙橱窗
    sy = facade(im, 494, 632, 30, G, '#eceae4', '#3a3a48', seed=6, floors=3, win='#8cb4d0')
    signboard(im, 496, 630, sy, 14, '#e8483c', '#a82a20', '電器', '#ffffff')
    d = ImageDraw.Draw(im)
    letters(d, 600, sy + 5, 'TV', '#ffe070')
    letters(d, 508, sy + 5, 'AV', '#ffe070')
    fr = shop_front(im, 494, 632, G, frame='#3a3a48', glass=('#9cbcd0', '#c8dce8'), door_at=600, door_w=20)
    d = ImageDraw.Draw(im)
    for r in range(2):                                                           # 2×3 电视（屏幕先画黑，动画帧条盖上去）
        for c in range(3):
            tx, ty = 504 + c * 30, G - 42 + r * 16
            rect(d, (tx, ty, tx + 18, ty + 13), '#3a3a42')
            rect(d, (tx + 2, ty + 2, tx + 13, ty + 10), '#101418')
            px(d, tx + 16, ty + 4, '#8a8a90'); px(d, tx + 16, ty + 7, '#8a8a90')
    rect(d, (500, G - 10, 592, G - 8), '#5a5a64')
    rect(d, (500, G - 22, 592, G - 21), '#5a5a64')
    rect(d, (540, G - 5, 560, G + 0), '#e4e4e0')                                 # 门口摆着的洗衣机
    ellipse(d, (544, G - 4, 548, G), '#8ab0d0')
    # ---------------- 7 蛋糕店（636–750）：粉白条纹篷、展示柜
    sy = facade(im, 634, 752, 50, G, '#f4e6e2', '#d87a94', seed=7)
    signboard(im, 640, 746, sy, 14, '#fff6f4', '#d87a94', None, '#d0507a', latin='CAKE SHOP')
    d = ImageDraw.Draw(im)
    fr = shop_front(im, 634, 752, G, frame='#f8f4f0', glass=('#f4e4e0', '#fff8f4'), door_at=716, door_w=18)
    d = ImageDraw.Draw(im)
    rect(d, (640, G - 22, 710, G - 6), '#e8f2f4')                                # 展示柜
    line(d, (640, G - 22, 710, G - 22), '#ffffff')
    for k, cx in enumerate(range(644, 706, 10)):
        c = ['#f8f0e0', '#f0a0b4', '#7a4a3a', '#f8e070', '#f8f0e0', '#c8e0a0', '#f0a0b4'][k % 7]
        rect(d, (cx, G - 15, cx + 6, G - 10), c)
        px(d, cx + 3, G - 16, '#d83a34')
    rect(d, (642, G - 40, 708, G - 26), '#fff4f0')                               # 柜后墙上的价目表
    for yy in range(G - 38, G - 28, 3):
        line(d, (646, yy, 700, yy), '#e0b8c0')
    awning(im, 634, 752, G - 50, 9, ('#f4a0be', '#ffffff'))
    d = ImageDraw.Draw(im)
    rect(d, (756 - 22, G - 16, 756 - 8, G), '#5a4030')                           # A 字黑板
    rect(d, (736, G - 14, 746, G - 6), '#2a3a2e')
    line(d, (738, G - 12, 744, G - 12), '#f4f0e6')
    line(d, (738, G - 9, 742, G - 9), '#f0a0b4')
    bike(d, 662, G + 1, '#e86a8a')
    # ---------------- 8 鞋店（754–858）
    sy = facade(im, 752, 860, 42, G, '#d6dee2', '#4a5a6a', seed=8)
    signboard(im, 756, 856, sy, 14, '#2a2a34', '#14141a', None, '#f8f4e0', latin='SHOES')
    d = ImageDraw.Draw(im)
    fr = shop_front(im, 752, 860, G, frame='#4a5a6a', glass=('#c4d4dc', '#e4eef2'), door_at=830, door_w=18)
    d = ImageDraw.Draw(im)
    for r in range(3):                                                           # 橱窗里的鞋架
        y = G - 38 + r * 11
        rect(d, (758, y + 7, 826, y + 8), '#8a9aa6')
        for k, sx in enumerate(range(760, 822, 12)):
            c = ['#3a2a22', '#f4f4f0', '#c83a34', '#3a5ac8', '#8a5a3a'][(k + r) % 5]
            rect(d, (sx, y + 3, sx + 8, y + 6), c)
            rect(d, (sx, y + 1, sx + 3, y + 3), c)
            px(d, sx + 6, y + 3, mix(c, '#ffffff', .4))
    rect(d, (790, G - 50, 822, G - 43), '#e8483c')                               # SALE 条
    letters(d, 806 - text_w('SALE') // 2, G - 49, 'SALE', '#ffffff')
    # ---------------- 9 拉面店（862–960）：红暖帘、红灯笼、木格门
    sy = facade(im, 860, 960, 54, G, '#cfc2ac', '#6a3a2a', seed=9)
    signboard(im, 864, 958, sy, 14, '#c83a2e', '#7a1e18', 'ラーメン', '#fff4d0')
    d = ImageDraw.Draw(im)
    rect(d, (860, G - 46, 960, G), '#6a4a34')
    rect(d, (866, G - 42, 954, G - 1), '#e8d8b0')                                # 格子门（里面亮）
    for xx in range(868, 954, 5):
        line(d, (xx, G - 42, xx, G - 1), '#8a6648')
    for yy in range(G - 40, G, 8):
        line(d, (866, yy, 954, yy), '#8a6648')
    for k in range(3):                                                           # 暖帘：三片
        nx = 878 + k * 22
        rect(d, (nx, G - 44, nx + 20, G - 24), '#c83a2e')
        line(d, (nx, G - 44, nx + 20, G - 44), '#e86a5a')
        line(d, (nx + 20, G - 44, nx + 20, G - 24), '#8a2418')
        ellipse(d, (nx + 6, G - 38, nx + 14, G - 30), '#fff4e0')
        ellipse(d, (nx + 8, G - 36, nx + 12, G - 32), '#c83a2e')
    rect(d, (874, G - 46, 946, G - 44), '#5a4030')
    line(d, (948, G - 46, 948, G - 40), '#3a2a1e')                               # 红灯笼
    ellipse(d, (942, G - 40, 954, G - 24), '#d83a2e')
    for yy in range(G - 37, G - 26, 3):
        line(d, (943, yy, 953, yy), '#a82a20')
    rect(d, (945, G - 41, 951, G - 39), '#2a2a2a')
    rect(d, (945, G - 25, 951, G - 23), '#2a2a2a')
    # ---------------- 地砖、街灯、樱花串
    paving(im, 0, W, G, 180)
    d = ImageDraw.Draw(im)
    im = dither_fill(im, (0, G + 1, W, G + 4), '#c2b49c', '#b2a48c', .5)          # 屋檐下的一条阴影
    lamps = []
    for x in (119, 331, 482, 753):
        lamps.append(lamp_post(im, x, G + 3, 90))
    sakura_garland(im, [(-10, 54)] + [(x, G + 3 - 90 - 2) for x in (119, 331, 482, 753)] + [(970, 52)], sag=7, seed=3)
    return im, G, lamps


def morioh_shopping_street():
    W = 960
    far = sky_far(640, seed=11, sea=False)
    near, G, lamps = shopping_near()
    tvs = tv_frames(8)
    # 电视墙帧条：只有 6 块屏幕不透明
    tvx, tvy, tvw, tvh = 504, G - 42, 80, 26
    tv_strip = new(tvw * 8, tvh)
    for f, fr in enumerate(tvs):
        for t, scr in enumerate(fr):
            r, c = divmod(t, 3)
            tv_strip.alpha_composite(scr.crop((0, 0, 12, 9)), (f * tvw + c * 30 + 2, r * 16 + 2))
    barber = barber_strip(8)
    banner = banner_strip(4)
    layers = {'far': far, 'near': near, 'tv': tv_strip, 'barber': barber, 'banner': banner}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(bookstore=[58, 146], grocer=[178, 146], barber=[300, 146], liquor=[400, 146], crates=[364, 146],
                             alley=[482, 146], electronics=[560, 146], tvwall=[548, 112], cake=[690, 146], shoes=[806, 146],
                             ramen=[910, 146], exit_x=948, walk_x=[8, 952]),
                layers=[{'type': 'pano', 'image': 'bg/morioh_shopping_street/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/morioh_shopping_street/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': 'bg/morioh_shopping_street/tv', 'n': 8, 'fps': 1.5, 'x': tvx, 'y': tvy, 'k': 1},
                        {'type': 'strip', 'image': 'bg/morioh_shopping_street/barber', 'n': 8, 'fps': 6, 'x': 322, 'y': G - 44, 'k': 1}]
                + [{'type': 'strip', 'image': 'bg/morioh_shopping_street/banner', 'n': 4, 'fps': 2.5, 'x': bx, 'y': by, 'k': 1}
                   for bx, by in lamps]
                + [{'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.14, 'key': 'pm'}],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    pv.alpha_composite(tv_strip.crop((0, 0, tvw, tvh)), (tvx, tvy))
    pv.alpha_composite(barber.crop((0, 0, 6, barber.height)), (322, G - 44))
    for bx, by in lamps:
        pv.alpha_composite(banner.crop((0, 0, 10, banner.height)), (bx, by))
    preview('morioh_shopping_street', {'room': pv}, ['room'], W)
    save_layers('morioh_shopping_street', layers, meta)
    return meta


# ============================================================ 铁路道口 rail_crossing（320 宽，一屏，下午）
#   人沿着马路左右走，铁轨从画面正中往远处延伸（灭点在地平线中间），道口两边各立一根警报器（X 牌 + 两盏红灯 + 喇叭），
#   栏杆平时竖着。会动的：key 'alarm' 时两盏红灯左右交替闪、方向箭头亮；pick 层 key 'gate'（0 竖着 / 1 放下）。
#   左边电线杆拉过来的电线横过画面上方（第2章结尾那个发光的影子可以蹲在电线上：锚点 wire）。
VPX, VPY = 160, 100           # 灭点
RX = 160 + 0                  # 铁轨中线


def persp(z):
    """世界深度 z（1 = 画面最下沿）→ 屏幕 y 和缩放"""
    y = VPY + 80 / z
    return y, (y - VPY) / 80


def crossing_far():
    W = 320
    im = new(W, 180, '#e8d8b8')
    im = grad(im, (0, 0, W, 104), ('#6aa0dc', '#86b6e6', '#a8cceb', '#d6dcd8', '#f2d8b0'))
    d = ImageDraw.Draw(im)
    cloud(im, 20, 30, 50, seed=21)
    cloud(im, 210, 22, 64, seed=22)
    cloud(im, 120, 52, 30, seed=23, cols=('#fff6e8', '#f6e4cc', '#e8ccb0'))
    d = ImageDraw.Draw(im)
    for layer, (base, amp, col, col2) in enumerate(((90, 7, '#9cb0bc', '#b0c2cc'), (96, 5, '#7c98a6', '#8eaab6'))):
        for x in range(W):
            y = base + amp * np.sin(x / (44 + layer * 21) + layer * 1.7) + 2 * np.sin(x / 11.0 + layer)
            line(d, (x, int(y), x, 104), col)
            px(d, x, int(y), col2)
    rng = np.random.RandomState(5)
    for i in range(30):                                                          # 远处的屋顶
        x = rng.randint(-10, W)
        if abs(x - VPX) < 14:
            continue
        bw, bh = rng.randint(8, 18), rng.randint(4, 9)
        y = 103 - bh
        rect(d, (x, y, x + bw, 104), ['#dcd2c4', '#e6dccc', '#cfc4b4'][rng.randint(3)])
        rect(d, (x - 1, y - 2, x + bw + 1, y), ['#8a7a78', '#6a7a8a', '#9a7e6e'][rng.randint(3)])
    rect(d, (0, 103, W, 180), '#9aae84')
    return im


def crossing_near():
    W, G = 320, 138
    im = new(W, 180)
    d = ImageDraw.Draw(im)
    # 地面：道口外是草坡，铁轨两边是碎石
    rect(d, (0, 101, W, G), '#8eaa72')
    im = grad(im, (0, 101, W, G), ('#a4b88a', '#94ae78', '#86a46a'))
    d = ImageDraw.Draw(im)
    noise_specks(im, (0, 104, W, G), ['#7a9a5e', '#a8c08c', '#6e8e54'], 700, 3)
    d = ImageDraw.Draw(im)
    # 碎石道床（梯形）+ 枕木 + 两条铁轨
    for y in range(101, 181):
        s = (y - VPY) / 80
        xa, xb = RX - 50 * s - 1, RX + 50 * s + 1
        line(d, (xa, y, xb, y), '#9a948a')
    noise_specks(im, (100, 101, 220, 180), ['#827c72', '#b0aa9e', '#6e6a62'], 900, 7)
    d = ImageDraw.Draw(im)
    for y in range(101, 181):                                                    # 道床边缘修一下（噪点不出界）
        s = (y - VPY) / 80
        xa, xb = int(RX - 50 * s - 1), int(RX + 50 * s + 1)
        a = np.array(im)
    a = np.array(im)
    for y in range(101, 180):
        s = (y - VPY) / 80
        xa, xb = int(RX - 50 * s - 2), int(RX + 50 * s + 2)
        for x in list(range(96, max(96, xa))) + list(range(min(224, xb + 1), 224)):
            if 0 <= x < W and tuple(a[y, x, :3]) in ((0x82, 0x7c, 0x72), (0xb0, 0xaa, 0x9e), (0x6e, 0x6a, 0x62)):
                a[y, x, :3] = a[y, x - 1 if x < RX else x + 1, :3] if 0 < x < W - 1 else a[y, x, :3]
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    z = 1.0
    while True:
        y, s = persp(z)
        if y < 102:
            break
        if not (G - 1 <= y <= 181):                                              # 道口那一段（马路）不画枕木
            th = max(1, int(round(3 * s)))
            rect(d, (RX - 34 * s, y - th, RX + 34 * s, y), '#6a5240')
            line(d, (RX - 34 * s, y - th, RX + 34 * s, y - th), '#86684e')
        z += 0.09 + 0.04 * z
    for side in (-1, 1):
        for y in range(101, 181):
            s = (y - VPY) / 80
            x = RX + side * 24 * s
            w = max(1, int(round(2.4 * s)))
            line(d, (x - w // 2, y, x + w // 2, y), '#6e6a68')
            px(d, x - w // 2, y, '#d8d8dc' if s > .15 else '#a8a8ac')
    # 架线柱（电气化：两边一根根往远处排，横臂跨过铁轨）
    for zz in (2.6, 3.6, 5.0, 7.0, 10.0, 15.0):
        y, s = persp(zz)
        h = 92 * s
        for side in (-1, 1):
            x = RX + side * 56 * s
            rect(d, (x - max(0, s * 1.5), y - h, x + max(0, s * 1.5), y), '#7a7a80')
        line(d, (RX - 56 * s, y - h + 3 * s, RX + 56 * s, y - h + 3 * s), '#6a6a70')
        line(d, (RX - 30 * s, y - h + 9 * s, RX + 30 * s, y - h + 9 * s), '#8a8a90')
    for k, (xs, ys) in enumerate(((-30, -.9), (30, -.9))):                       # 接触网（两根线往灭点收）
        pts = []
        for zz in np.linspace(1.6, 40, 40):
            y, s = persp(zz)
            pts.append((RX + xs * s * 0 + (k * 2 - 1) * 4 * s, y - 92 * s + 10 * s))
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            line(d, (xa, ya, xb, yb), '#5a5a62')
    # 铁轨两边的矮栅栏（马路外，往远处收）
    for side in (-1, 1):
        prev = None
        for zz in np.linspace(2.2, 30, 60):
            y, s = persp(zz)
            x = RX + side * 62 * s
            if prev:
                line(d, (prev[0], prev[1] - 7 * s, x, y - 7 * s), '#d8d4c8')
                line(d, (prev[0], prev[1] - 3 * s, x, y - 3 * s), '#c8c4b8')
            if int(zz * 3) % 2 == 0:
                line(d, (x, y, x, y - 8 * s), '#b8b4a8')
            prev = (x, y)
    # ---------------- 左边：民宅 + 围墙 + 电线杆 + 踏切注意的牌子
    im = house(im, -20, 112, 88, 58, wall='#e6dccb', wall2='#c8bca8', seed=41, roof=('#6a3e36', '#4e2c28', '#8a5246', '#341c1a'))
    im = block_wall(im, -4, 86, 116, G - 2)
    im = hedge(im, -4, 86, 108, 116, seed=42)
    im = pole(im, 38, G + 2, 132)
    d = ImageDraw.Draw(im)
    rect(d, (64, G - 34, 65, G), '#8a8a90')                                      # 踏切あり（黄底菱形）
    poly(d, [(64.5, G - 48), (73, G - 40), (64.5, G - 32), (56, G - 40)], '#f0c830')
    poly(d, [(64.5, G - 46), (71, G - 40), (64.5, G - 34), (58, G - 40)], '#f8d840')
    rect(d, (61, G - 42, 68, G - 39), '#2a2a30')                                 # 小火车
    px(d, 62, G - 38, '#2a2a30'); px(d, 66, G - 38, '#2a2a30')
    # ---------------- 右边：小卖部（关着卷帘）+ 自动售货机 + 树
    rx0 = 232
    rect(d, (rx0, 70, W, G - 2), '#d8ccb6')
    im = tiled_roof(im, rx0, W + 6, 58, 70, ('#3a5a52', '#2a4440', '#4e766a', '#1c2e2a'), overhang=3)
    d = ImageDraw.Draw(im)
    rect(d, (rx0 + 6, 96, W, G - 2), '#a8acb0')                                  # 卷帘门
    for yy in range(98, G - 2, 3):
        line(d, (rx0 + 6, yy, W, yy), '#8e9296')
    rect(d, (rx0 + 4, 78, W, 92), '#f4f0e6')
    kanji(im, rx0 + 10, 79, '駄菓子', '#c83a34')
    im = vending(im, 290, G - 1, body='#f0f0ec', accent='#c8dce8')
    d = ImageDraw.Draw(im)
    for k, bx in enumerate((262, 274)):                                          # 门口两盆花
        rect(d, (bx, G - 10, bx + 9, G - 2), '#b8643e')
        line(d, (bx, G - 10, bx + 9, G - 10), '#d88a5e')
        for j in range(4):
            ellipse(d, (bx - 1 + j * 3, G - 16 + (j % 2) * 2, bx + 3 + j * 3, G - 11 + (j % 2) * 2), '#5a9a5a' if j % 2 else '#4a8a4a')
        px(d, bx + 3, G - 15, '#f2a0b4' if k else '#f8e070'); px(d, bx + 7, G - 14, '#f2a0b4' if k else '#f8e070')
    # ---------------- 马路（G–180）：沥青横穿，道口那段铺橡胶板，两边停止线、黄黑边
    im = asphalt(im, 0, W, G, 180, dash=False)
    d = ImageDraw.Draw(im)
    for y in range(G + 3, 180):
        s = (y - VPY) / 80
        xa, xb = RX - 40 * s, RX + 40 * s
        line(d, (xa, y, xb, y), '#55555c')
        for side in (-1, 1):                                                     # 铁轨嵌在道口板里
            x = RX + side * 24 * s
            w = max(1, int(round(2.4 * s)))
            line(d, (x - w // 2, y, x + w // 2, y), '#2e2e34')
            px(d, x - w // 2 - 1, y, '#3a3a40')
    for y in range(G + 4, 180, 6):                                               # 道口板的横缝
        s = (y - VPY) / 80
        line(d, (RX - 40 * s, y, RX + 40 * s, y), '#4a4a50')
    for side in (-1, 1):                                                         # 黄黑相间的边 + 白色停止线
        for y in range(G + 3, 180):
            s = (y - VPY) / 80
            x = RX + side * 41 * s
            px(d, x, y, '#f0c830' if (y // 3) % 2 else '#2a2a30')
            px(d, x + side, y, '#f0c830' if (y // 3) % 2 else '#2a2a30')
            sx = RX + side * 66 * s
            line(d, (sx - 1, y, sx + 1, y), '#e8e4d8')
    return im, G


def crossing_signal(d, x, g, h=70):
    """警报器（远侧马路边）：黑白杆、X 牌、两盏灯（不亮）、方向箭头、喇叭；底下是栏杆的机箱"""
    top = g - h
    rect(d, (x - 1, top, x + 1, g), '#e8e8e4')
    for y in range(top + 30, g, 6):
        rect(d, (x - 1, y, x + 1, y + 2), '#2a2a30')
    ellipse(d, (x - 3, top - 7, x + 3, top - 1), '#3a3a42')                     # 喇叭
    ellipse(d, (x - 2, top - 6, x + 2, top - 2), '#6a6a72')
    for a, b in (((x - 9, top + 1), (x + 9, top + 11)), ((x - 9, top + 11), (x + 9, top + 1))):   # X 牌（黄黑）
        line(d, (a[0], a[1], b[0], b[1]), '#2a2a30', 3)
        line(d, (a[0], a[1], b[0], b[1]), '#f0c830', 1)
    rect(d, (x - 11, top + 15, x + 11, top + 23), '#1e1e24')                     # 灯的背板
    for lx in (x - 6, x + 6):
        ellipse(d, (lx - 4, top + 15, lx + 4, top + 23), '#2a2a30')
        ellipse(d, (lx - 3, top + 16, lx + 3, top + 22), '#6a2420')
        px(d, lx - 1, top + 17, '#8a3a34')
    rect(d, (x - 5, top + 25, x + 5, top + 29), '#1e1e24')                      # 方向指示器
    poly(d, [(x - 3, top + 27), (x, top + 25), (x, top + 29)], '#4a4a3a')
    poly(d, [(x + 3, top + 27), (x, top + 25), (x, top + 29)], '#4a4a3a')
    rect(d, (x + 3, g - 22, x + 9, g), '#2a2a30')                               # 栏杆机箱（黄黑斜条）
    for y in range(g - 22, g, 2):
        for xx in range(x + 3, x + 10):
            if ((xx + y) // 2) % 2:
                px(d, xx, y, '#f0c830')
    return (x, top)


def arm_layer(sigs, down):
    """栏杆：竖着（平时）/ 放下（横在马路远侧，挡住来车）"""
    im = new(320, 180)
    d = ImageDraw.Draw(im)
    for (x, top), side in sigs:
        hx, hy = x + 6, top + 50                                                  # 转轴
        if not down:
            for y in range(top + 2, hy):
                c = '#f0c830' if ((y - top) // 4) % 2 else '#2a2a30'
                line(d, (hx - 1, y, hx, y), c)
            rect(d, (hx - 2, top, hx + 1, top + 2), '#e8e8e4')
        else:
            L = 74
            for i in range(L):
                X = hx + side * i
                c = '#f0c830' if (i // 5) % 2 else '#2a2a30'
                line(d, (X, hy - 1, X, hy), c)
            for i in range(4, L, 9):                                              # 挂下来的流苏
                line(d, (hx + side * i, hy + 1, hx + side * i, hy + 3), '#2a2a30')
        ellipse(d, (hx - 2, hy - 2, hx + 2, hy + 2), '#4a4a50')
    return im


def alarm_strip(sigs):
    """警报：两帧，左右灯交替亮 + 灯周围一圈红晕 + 箭头亮"""
    n = 2
    out = new(320 * n, 180)
    d = ImageDraw.Draw(out)
    for f in range(n):
        ox = f * 320
        for (x, top), _ in sigs:
            for k, lx in enumerate((x - 6, x + 6)):
                if k != f:
                    continue
                cx, cy = ox + lx, top + 19
                for r, a in ((10, 60), (7, 110)):
                    for yy in range(cy - r, cy + r + 1):
                        for xx in range(cx - r, cx + r + 1):
                            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r and (xx + yy) % 2 == 0:
                                d.point((xx, yy), fill=(255, 80, 60, a))
                ellipse(d, (cx - 3, cy - 3, cx + 3, cy + 3), '#ff3a2a')
                ellipse(d, (cx - 2, cy - 2, cx + 1, cy + 1), '#ff9a80')
                px(d, cx - 1, cy - 1, '#ffffff')
            poly(d, [(ox + x - 3, top + 27), (ox + x, top + 25), (ox + x, top + 29)], '#7aff8a')
    return out


def rail_crossing():
    W = 320
    far = crossing_far()
    near, G = crossing_near()
    d = ImageDraw.Draw(near)
    sigs = [(crossing_signal(d, 112, G + 1, 74), -1), (crossing_signal(d, 208, G + 1, 74), 1)]
    # 电线：左边电线杆（38）的横担拉向右边出画；再从变压器那里拉一根低的到小卖部屋檐（发光的影子蹲在这根上，
    #   对白框盖住 y 6–46，所以放在低的那根：锚点 wire）
    near = wires(near, [(38, G + 2 - 132 + 7), (340, 40)], sag=12)
    dd = ImageDraw.Draw(near)
    (xa, ya), (xb, yb) = (42, 50), (234, 72)
    prev = None
    for i in range(61):
        t = i / 60
        x, y = xa + (xb - xa) * t, ya + (yb - ya) * t + 10 * 4 * t * (1 - t)
        if prev:
            line(dd, (prev[0], prev[1], x, y), '#2a2a30')
        prev = (x, y)
    wt = (150 - xa) / (xb - xa)
    wire_y = int(round(ya + (yb - ya) * wt + 10 * 4 * wt * (1 - wt)))
    up, down = arm_layer(sigs, False), arm_layer(sigs, True)
    alarm = alarm_strip(sigs)
    layers = {'far': far, 'near': near, 'arm_up': up, 'arm_down': down, 'alarm': alarm}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(signal_l=[112, 146], signal_r=[208, 146], lamp_l=[112, 84], lamp_r=[208, 84], tracks=[160, 158],
                             stop_l=[96, 156], stop_r=[224, 156], wire=[150, wire_y], kiosk=[270, 146], sign=[64, 146], walk_x=[8, 312]),
                layers=[{'type': 'pano', 'image': 'bg/rail_crossing/far', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/rail_crossing/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pick', 'images': ['bg/rail_crossing/arm_up', 'bg/rail_crossing/arm_down'], 'key': 'gate', 'k': 1,
                         'x': 0, 'y': 0},
                        {'type': 'strip', 'image': 'bg/rail_crossing/alarm', 'n': 2, 'fps': 2, 'w': 320, 'h': 180, 'x': 0, 'y': 0,
                         'k': 1, 'key': 'alarm'},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = far.copy()
    pv.alpha_composite(near)
    pv.alpha_composite(up)
    preview('rail_crossing', {'room': pv}, ['room'], W)
    pv2 = far.copy()
    pv2.alpha_composite(near)
    pv2.alpha_composite(down)
    pv2.alpha_composite(alarm.crop((0, 0, 320, 180)))
    pv2.save(os.path.join(LIB.ASSETS, 'preview', 'bg_rail_crossing_alarm.png'))
    save_layers('rail_crossing', layers, meta)
    return meta


# ============================================================ 杜王大酒店门口 + 街角咖啡馆 morioh_grand_hotel（480 宽，白天）
#   左：杜王大酒店（米色石材高楼，往上出画），金字雨棚、旋转门、红地毯、两盆修剪的灌木、三根旗杆（旗子会飘）、大堂酒廊的窗；
#   中间一棵榉树；右：红砖楼一楼的咖啡馆（绿白条纹篷、大橱窗、竖招牌），人行道上两张露天小圆桌。
#   之后各章找承太郎都来这里，所以留了一层 key 'pm' 的傍晚色。
def zelkova(im, cx, g, h=100, w=74, seed=0):
    pal = dict(d='#2e5e3a', m='#4a7c48', l='#6e9e5a', x='#a8cc7a', trunk='#5a4234', trunk2='#3e2c22')
    im = sakura(im, cx, g, h, w, seed=seed, pal=pal, petals=False)
    d = ImageDraw.Draw(im)
    rect(d, (cx - 9, g - 1, cx + 9, g + 2), '#6a6a70')                           # 树池铁箅子
    for x in range(cx - 8, cx + 9, 2):
        px(d, x, g, '#4a4a50')
    return im


def hotel_near():
    W, G = 480, 138
    im = new(W, 180)
    d = ImageDraw.Draw(im)
    # ---------------- 酒店主楼（0–298）：往上出画
    HX1 = 298
    rect(d, (0, 0, HX1, G), '#e6dac4')
    for y in range(0, G - 50, 22):                                               # 每层：石材横缝 + 一排窗
        line(d, (0, y + 21, HX1, y + 21), '#d2c4aa')
        for x in range(6, HX1 - 10, 24):
            rect(d, (x, y + 4, x + 14, y + 16), '#6e90ae')
            rect(d, (x + 1, y + 5, x + 13, y + 15), '#86a8c4')
            line(d, (x + 2, y + 6, x + 6, y + 10), '#c4dcec')
            line(d, (x, y + 17, x + 14, y + 17), '#c8baa0')
            if (x // 24 + y // 22) % 7 == 3:                                     # 拉着窗帘的几间
                rect(d, (x + 1, y + 5, x + 6, y + 15), '#e8dcc0')
    for x in range(0, HX1, 72):                                                  # 竖向的石柱带
        rect(d, (x, 0, x + 4, G - 50), '#d8caae')
        line(d, (x + 4, 0, x + 4, G - 50), '#c4b498')
    rect(d, (HX1 - 3, 0, HX1, G), '#c8b89c')
    # 一楼：深色花岗岩基座
    rect(d, (0, G - 52, HX1, G), '#7a6e66')
    rect(d, (0, G - 54, HX1, G - 52), '#a89a8a')
    for x in range(0, HX1, 18):
        line(d, (x, G - 50, x, G), '#6e625a')
    line(d, (0, G - 30, HX1, G - 30), '#6e625a')
    # 左边：大堂酒廊的窗（暖光、吊灯）
    for wx in (10, 214):
        ww = 70 if wx == 10 else 76
        rect(d, (wx, G - 46, wx + ww, G - 8), '#c8a050')
        im = grad(im, (wx + 2, G - 44, wx + ww - 2, G - 10), ('#f6dca0', '#eac888', '#d8b070'))
        d = ImageDraw.Draw(im)
        for cx in range(wx + 14, wx + ww - 6, 26):
            line(d, (cx, G - 44, cx, G - 38), '#a88440')
            poly(d, [(cx - 5, G - 34), (cx + 5, G - 34), (cx + 3, G - 38), (cx - 3, G - 38)], '#fff4c8')
            px(d, cx, G - 33, '#ffffff')
        for k in range(3):                                                       # 沙发椅的背
            sx = wx + 6 + k * (ww // 3)
            rect(d, (sx, G - 20, sx + 14, G - 10), '#8a3a34')
            line(d, (sx, G - 20, sx + 14, G - 20), '#a85a4a')
        line(d, (wx + ww // 2, G - 44, wx + ww // 2, G - 10), '#c8a050')
        line(d, (wx + 3, G - 43, wx + 9, G - 37), '#fffaf0')
    # 入口（96–206）：玻璃门 + 中间的旋转门
    ex0, ex1 = 96, 206
    rect(d, (ex0, G - 50, ex1, G), '#b89a50')
    rect(d, (ex0 + 3, G - 47, ex1 - 3, G - 1), '#4a5a6a')
    for gx in range(ex0 + 4, ex1 - 4, 14):
        rect(d, (gx, G - 46, gx + 12, G - 2), '#8eb0c6')
        line(d, (gx + 1, G - 45, gx + 5, G - 41), '#d4e6f0')
        line(d, (gx + 13, G - 46, gx + 13, G - 2), '#b89a50')
    rcx = (ex0 + ex1) // 2                                                       # 旋转门：圆筒 + 三片门叶
    rect(d, (rcx - 16, G - 48, rcx + 16, G - 1), '#b89a50')
    rect(d, (rcx - 14, G - 46, rcx + 14, G - 2), '#a6c4d6')
    for gx, c in ((rcx - 12, '#c4dae6'), (rcx - 1, '#7e9cb2'), (rcx + 8, '#bcd4e2')):
        rect(d, (gx, G - 45, gx + 2, G - 3), '#b89a50')
    rect(d, (rcx - 16, G - 50, rcx + 16, G - 47), '#d8bc6a')
    line(d, (rcx - 13, G - 44, rcx - 6, G - 37), '#eef6fa')
    # 红地毯（门口到人行道）
    poly(d, [(rcx - 14, G), (rcx + 14, G), (rcx + 20, G + 12), (rcx - 20, G + 12)], '#a8282a')
    line(d, (rcx - 14, G, rcx - 20, G + 12), '#d8bc6a')
    line(d, (rcx + 14, G, rcx + 20, G + 12), '#d8bc6a')
    # 雨棚（往外伸，金字店名）+ 两根细柱
    cx0, cx1, cy = ex0 - 6, ex1 + 6, G - 66
    rect(d, (cx0, cy, cx1, cy + 12), '#2a3446')
    line(d, (cx0, cy, cx1, cy), '#4a5a74')
    rect(d, (cx0, cy + 12, cx1, cy + 14), '#b89a50')
    rect(d, (cx0 - 2, cy - 3, cx1 + 2, cy), '#3a4458')
    name = 'MORIOH GRAND HOTEL'
    letters(d, (cx0 + cx1) // 2 - text_w(name) // 2, cy + 4, name, '#f0d070')
    for x in range(cx0 + 6, cx1 - 4, 12):                                        # 雨棚底下的筒灯
        px(d, x, cy + 15, '#fff4c8')
    for px_ in (cx0 + 2, cx1 - 3):
        rect(d, (px_, cy + 14, px_ + 1, G + 8), '#b89a50')
        rect(d, (px_ - 1, G + 7, px_ + 2, G + 9), '#8a7438')
    # 门边的壁灯 + 两盆修剪成球的灌木
    for lx in (ex0 - 10, ex1 + 6):
        rect(d, (lx, G - 40, lx + 4, G - 32), '#b89a50')
        rect(d, (lx + 1, G - 39, lx + 3, G - 34), '#fff0b8')
    for tx in (ex0 - 22, ex1 + 12):
        rect(d, (tx, G - 12, tx + 16, G + 2), '#c8bcac')
        line(d, (tx, G - 12, tx + 16, G - 12), '#e4dccc')
        rect(d, (tx + 7, G - 18, tx + 9, G - 12), '#5a4234')
        ellipse(d, (tx - 1, G - 36, tx + 17, G - 16), '#2e5e3a')
        ellipse(d, (tx + 1, G - 35, tx + 13, G - 22), '#4a7c48')
        ellipse(d, (tx + 3, G - 34, tx + 9, G - 28), '#6e9e5a')
    # 旗杆三根（旗子是动画帧条，这里只画杆）
    for fx in (236, 252, 268):
        rect(d, (fx, 50, fx + 1, G), '#c8ccd4')
        px(d, fx, 49, '#e8c860')
        px(d, fx + 1, 49, '#e8c860')
        rect(d, (fx - 2, G - 3, fx + 3, G), '#8a8a90')
    # ---------------- 咖啡馆（302–480）：红砖三层
    CX0 = 302
    rect(d, (CX0, 14, W, G), '#a8644c')
    for y in range(14, G, 4):                                                    # 砖缝
        line(d, (CX0, y, W, y), '#94543e')
        for x in range(CX0 + ((y // 4) % 2) * 5, W, 10):
            line(d, (x, y + 1, x, y + 3), '#94543e')
    rect(d, (CX0, 12, W, 16), '#d8ccb8')
    for y in (24, 58):                                                           # 楼上的窗 + 窗台花箱
        for x in range(CX0 + 12, W - 12, 34):
            rect(d, (x - 2, y - 2, x + 22, y + 22), '#e8dcc8')
            window(d, (x, y, x + 20, y + 20), frame='#f4f0e6', glass=('#7e9cb8', '#bcd4e6'), curtain='#f0e0c0' if (x // 34) % 2 else None)
            rect(d, (x - 2, y + 23, x + 22, y + 27), '#6a4a34')
            for fx in range(x, x + 21, 3):
                ellipse(d, (fx - 1, y + 20, fx + 2, y + 23), ['#e85a6a', '#f8e070', '#4a8a4a', '#f4f0f0'][(fx // 3) % 4])
    # 一楼：深绿门脸、大橱窗（里面暖）、门
    rect(d, (CX0, G - 54, W, G), '#2e5a46')
    rect(d, (CX0, G - 56, W, G - 54), '#d8ccb8')
    wx0, wx1, wy0, wy1 = CX0 + 8, 418, G - 46, G - 6
    rect(d, (wx0, wy0, wx1, wy1), '#c8a050')
    im = grad(im, (wx0 + 2, wy0 + 2, wx1 - 2, wy1 - 2), ('#f2d8a8', '#e4c088', '#cfa470'))
    d = ImageDraw.Draw(im)
    rect(d, (wx0 + 2, wy1 - 16, wx1 - 2, wy1 - 2), '#6a4a34')                    # 吧台
    line(d, (wx0 + 2, wy1 - 16, wx1 - 2, wy1 - 16), '#8a6648')
    rect(d, (wx0 + 10, wy1 - 26, wx0 + 24, wy1 - 16), '#b8bcc4')                  # 咖啡机
    rect(d, (wx0 + 12, wy1 - 24, wx0 + 22, wy1 - 20), '#2a2a30')
    for k, sx in enumerate(range(wx0 + 34, wx1 - 10, 14)):                       # 吧台上的杯子、蛋糕罩
        if k % 3 == 1:
            d.pieslice((sx - 2, wy1 - 26, sx + 10, wy1 - 14), 180, 360, fill=C('#e8f2f6'))
            rect(d, (sx + 1, wy1 - 20, sx + 7, wy1 - 17), '#f0a0b4')
        else:
            rect(d, (sx, wy1 - 20, sx + 4, wy1 - 17), '#f8f8f4')
    for lx in range(wx0 + 16, wx1 - 6, 24):                                      # 吊灯
        line(d, (lx, wy0 + 2, lx, wy0 + 10), '#5a4030')
        poly(d, [(lx - 4, wy0 + 14), (lx + 4, wy0 + 14), (lx + 2, wy0 + 10), (lx - 2, wy0 + 10)], '#3a6a52')
        px(d, lx, wy0 + 15, '#fff4c8')
    for x in range(wx0 + 36, wx1, 36):
        line(d, (x, wy0, x, wy1), '#c8a050')
    line(d, (wx0 + 4, wy0 + 4, wx0 + 12, wy0 + 12), '#fffaf0')
    line(d, (wx0 + 40, wy0 + 4, wx0 + 46, wy0 + 10), '#fffaf0')
    letters(d, wx0 + 40, wy1 - 11, 'COFFEE', '#f2ead8')                          # 吧台正面的字
    rect(d, (424, G - 48, 446, G - 1), '#c8a050')                                # 门
    rect(d, (426, G - 46, 444, G - 2), '#4a3a2a')
    rect(d, (428, G - 44, 442, G - 24), '#e2c48c')
    rect(d, (440, G - 22, 441, G - 18), '#e8d070')
    awning(im, CX0, W, G - 56, 10, ('#2e7a5a', '#f2ead8'))
    d = ImageDraw.Draw(im)
    rect(d, (454, 62, 456, 66), '#3a3a40')                                       # 竖招牌（喫茶）
    rect(d, (452, 66, 470, 98), '#1e3a2e')
    rect(d, (454, 68, 468, 96), '#2e5a46')
    kanji(im, 455, 69, '喫茶', '#f2ead8', vertical=True)
    d = ImageDraw.Draw(im)
    rect(d, (450, G - 18, 462, G), '#5a4030')                                    # 黑板
    rect(d, (452, G - 16, 460, G - 6), '#2a3a2e')
    line(d, (453, G - 14, 459, G - 14), '#f4f0e6')
    line(d, (453, G - 11, 457, G - 11), '#f8e070')
    # ---------------- 人行道 + 马路
    paving(im, 0, W, G, 168)
    d = ImageDraw.Draw(im)
    rect(d, (0, 166, W, 169), '#a8a49c')                                         # 路缘石
    line(d, (0, 166, W, 166), '#c8c4bc')
    im = asphalt(im, 0, W, 169, 180, dash=False)
    d = ImageDraw.Draw(im)
    # 红地毯盖在地砖上（再画一遍）
    poly(d, [(rcx - 14, G), (rcx + 14, G), (rcx + 20, G + 12), (rcx - 20, G + 12)], '#a8282a')
    line(d, (rcx - 14, G, rcx - 20, G + 12), '#d8bc6a')
    line(d, (rcx + 14, G, rcx + 20, G + 12), '#d8bc6a')
    for px_ in (cx0 + 2, cx1 - 3):
        rect(d, (px_, G, px_ + 1, G + 8), '#b89a50')
        rect(d, (px_ - 1, G + 7, px_ + 2, G + 9), '#8a7438')
    # 露天座：两张小圆桌（白）、每张两把绿椅子，矮花槽隔开
    tables = []
    for tx in (344, 398):
        ty = G + 12
        for side in (-1, 1):                                                     # 椅子：靠背 + 座 + 腿
            cx = tx + side * 13
            bx = cx + side * 3
            rect(d, (bx - 1, ty - 18, bx + 1, ty - 8), '#2e7a5a')
            line(d, (bx - 1, ty - 18, bx + 1, ty - 18), '#4a9a76')
            rect(d, (cx - 4, ty - 9, cx + 4, ty - 7), '#2e7a5a')
            line(d, (cx - 4, ty - 9, cx + 4, ty - 9), '#4a9a76')
            line(d, (cx - 3, ty - 6, cx - 3, ty), '#1e4a38')
            line(d, (cx + 3, ty - 6, cx + 3, ty), '#1e4a38')
        ellipse(d, (tx - 11, ty - 14, tx + 11, ty - 8), '#f4f0e6')               # 桌面
        line(d, (tx - 10, ty - 10, tx + 10, ty - 10), '#d8d2c4')
        line(d, (tx - 8, ty - 9, tx + 8, ty - 9), '#c8c2b4')
        rect(d, (tx - 1, ty - 8, tx + 1, ty - 1), '#5a5a62')
        rect(d, (tx - 5, ty - 1, tx + 5, ty), '#5a5a62')
        rect(d, (tx - 6, ty - 15, tx - 3, ty - 13), '#f8f8f4')                   # 咖啡杯 + 碟
        line(d, (tx - 7, ty - 12, tx - 2, ty - 12), '#e0dcd0')
        px(d, tx - 2, ty - 14, '#f8f8f4')
        tables.append([tx, ty])
    for x in range(CX0 + 4, 446, 10):                                            # 花槽
        rect(d, (x, G - 1, x + 8, G + 3), '#6a4a34')
    return im, G, (cx0, cy, cx1), tables, (wx0, wy0, wx1, wy1)


def hotel_far():
    im = sky_far(400, seed=13, sea=False)
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(14)
    for i in range(12):                                                          # 远处的楼（市中心）
        x = rng.randint(-10, 400)
        bw, bh = rng.randint(18, 34), rng.randint(30, 60)
        y = 120 - bh
        rect(d, (x, y, x + bw, 130), ['#c4ccd4', '#d4d0c8', '#b8c2cc'][rng.randint(3)])
        for wy in range(y + 4, 120, 6):
            for wx in range(x + 3, x + bw - 3, 5):
                px(d, wx, wy, '#8ea4b8')
                px(d, wx + 1, wy, '#8ea4b8')
    return im


def morioh_grand_hotel():
    W = 480
    far = hotel_far()
    near, G, (cx0, cy, cx1), tables, (wx0, wy0, wx1, wy1) = hotel_near()
    near = zelkova(near, 300, G + 2, 104, 70, seed=51)
    def emb_navy(d, ox, oy, f):
        poly(d, [(ox + 8, oy + 2), (ox + 11, oy + 5), (ox + 8, oy + 8), (ox + 5, oy + 5)], '#f0d070')
    def emb_sun(d, ox, oy, f):
        ellipse(d, (ox + 5, oy + 3, ox + 10, oy + 8), '#c8102e')
    flags = {'flag_navy': flag_strip(16, 11, 6, ('#2a3a6a', '#1e2a50', '#f0d070'), emb_navy),
             'flag_jp': flag_strip(16, 11, 6, ('#f8f8f4', '#dcdcd6', '#c8102e'), emb_sun),
             'flag_wine': flag_strip(16, 11, 6, ('#8a2a3a', '#6a1e2a', '#f0d070'),
                                     lambda d, ox, oy, f: rect(d, (ox + 4, oy + 4, ox + 11, oy + 6), '#f0d070'))}
    layers = {'far': far, 'near': near}
    layers.update(flags)
    fl = [{'type': 'strip', 'image': f'bg/morioh_grand_hotel/{k}', 'n': 6, 'fps': 7 + i, 'x': fx + 2, 'y': 49, 'k': 1}
          for i, (k, fx) in enumerate((('flag_navy', 236), ('flag_jp', 252), ('flag_wine', 268)))]
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(hotel_door=[151, 146], canopy=[151, cy + 6], lounge=[46, 146], flags=[254, 146],
                             tree=[300, 146], cafe_window=[(wx0 + wx1) // 2, 146], cafe_door=[435, 146],
                             table1=tables[0], table2=tables[1], sign=[461, 82], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/morioh_grand_hotel/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/morioh_grand_hotel/near', 'k': 1, 'x': 0, 'y': 0}] + fl
                + [{'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    for k, fx in (('flag_navy', 236), ('flag_jp', 252), ('flag_wine', 268)):
        pv.alpha_composite(flags[k].crop((0, 0, 16, flags[k].height)), (fx + 2, 49))
    preview('morioh_grand_hotel', {'room': pv}, ['room'], W)
    save_layers('morioh_grand_hotel', layers, meta)
    return meta


SCENES = {'hirose_living': hirose_living, 'budogaoka_hall': budogaoka_hall, 'morioh_shopping_street': morioh_shopping_street,
          'rail_crossing': rail_crossing, 'morioh_grand_hotel': morioh_grand_hotel}


def main(keys):
    path = os.path.join(LIB.META, 'bg_ch2.json')
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
