# 第四部第11章（川尻家 / 败者食尘）的背景，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）和第2章（p4_bg_ch2.py）。
#   本章新画 3 张：
#     morning_corner   640  住宅区的街口，7 月早上的光（邮筒、电线杆、路边大钟、カーブミラー、往里走的小巷）。第 18 战。
#                          钟的指针是 pick 层，key 'clock' = 当天的分钟数（7:00 = 420 … 8:30 = 510，每 5 分钟一张）。
#     street_crossing  960  商店街到大马路的十字路口（第 17 战段 A）：左边一排铺面，中间横穿的大路 + 斑马线 + 两组红绿灯，
#                          右边写字楼、长围墙、邮局、去杜王大酒店的路牌。红绿灯是 pick 层，key 'signal'：0 行人红灯 / 1 行人绿灯。
#   本章直接沿用、不复制的背景：morioh_map（序章）、kawajiri_house（第8章，早 / 夜用它自己的开关层）、ghost_alley（第6章）。
#     rohan_house_scaffold 480  第5章露伴宅（p4_bg_ch5.rohan_house_layers）+ 修缮用的脚手架、防护网、“工事中”牌。
#                          第5章分支没合进来时跳过这张；要重画就 PYTHONPATH 指到有 p4_bg_ch5.py 的目录。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_ch11.json（build_p4.py 会把 _meta/bg_*.json 并进 bg）。
#   用法：python3 第四部/tools/art/p4_bg_ch11.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   终章要的“街口雨天版”可以 import 本文件的 corner_near(var='rain')。
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import preview, save_layers, sky_far  # noqa: E402

PACK = 'ch11'

# ------------------------------------------------------------ 下面这些小零件抄自 p4_bg_ch2.py（第2章分支还没合，不能 import）

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



# ============================================================ 共用
def shade_poly(im, pts, mul=(.78, .8, .9)):
    """多边形里的像素按 mul 压暗（地上的影子，偏一点蓝）；只压不透明的像素"""
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=255)
    a = np.array(im).astype(float)
    sel = (np.array(m) > 0) & (a[..., 3] > 0)
    a[sel, :3] *= np.array(mul)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def warm_side(im, box, mul=(1.06, 1.0, .9)):
    """box 里的像素按 mul 调（朝东的墙面被早上的太阳照到）"""
    a = np.array(im).astype(float)
    x0, y0, x1, y1 = [int(v) for v in box]
    sub = a[y0:y1, x0:x1]
    sel = sub[..., 3] > 0
    sub[sel, :3] *= np.array(mul)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def round_tree(im, cx, g, h=70, w=56, seed=0, cols=('#2e5a36', '#467a44', '#68a056', '#9cc87a'), trunk='#5a4234'):
    """夏天的阔叶树：几团叶子叠起来，左上受光"""
    d = ImageDraw.Draw(im)
    rect(d, (cx - 2, g - h * .45, cx + 2, g), trunk)
    line(d, (cx - 2, g - h * .45, cx - 2, g), mix(trunk, '#ffffff', .2))
    rng = np.random.RandomState(seed)
    blobs = []
    for i in range(9):
        bx = cx + rng.uniform(-w * .38, w * .38)
        by = g - h * .62 + rng.uniform(-h * .28, h * .16)
        r = rng.uniform(w * .2, w * .32)
        blobs.append((bx, by, r))
    for bx, by, r in blobs:
        ellipse(d, (bx - r, by - r * .85, bx + r, by + r * .85), cols[0])
    for bx, by, r in blobs:
        ellipse(d, (bx - r + 2, by - r * .85 + 1, bx + r - 3, by + r * .85 - 3), cols[1])
    for bx, by, r in blobs:
        ellipse(d, (bx - r * .7 - 2, by - r * .7, bx + r * .2, by), cols[2])
    for _ in range(int(w * h / 40)):
        x, y = cx + rng.uniform(-w * .5, w * .3), g - h + rng.uniform(4, h * .6)
        if im.getpixel((int(x), int(y)))[3] and im.getpixel((int(x), int(y)))[:3] == c3(cols[2]):
            px(d, x, y, cols[3])
    return im


def morning_glory(im, x0, x1, y0, y1, seed=0):
    """牵牛花（7 月）：围墙上爬的藤 + 心形叶子 + 紫蓝色的花"""
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    for _ in range(int((x1 - x0) / 7)):
        x = rng.randint(x0, x1)
        y = y1
        while y > y0:
            nx = x + rng.choice([-1, 0, 1])
            line(d, (x, y, nx, y - 2), '#4a7a3a')
            x, y = nx, y - 2
            if rng.rand() < .35:
                ellipse(d, (x - 2, y - 1, x + 1, y + 2), '#5a9a48')
                px(d, x - 1, y, '#7ab85a')
            if rng.rand() < .08:
                c = ['#6a5ad0', '#8a6ae0', '#d070b8', '#4a7ae0'][rng.randint(4)]
                ellipse(d, (x - 2, y - 2, x + 2, y + 2), c)
                px(d, x, y, '#f8f4ff')


def postbox(d, x, g):
    """老式圆筒邮筒（红色，顶上圆帽，正面投信口）"""
    rect(d, (x, g - 34, x + 14, g - 2), '#d42a2a')
    line(d, (x, g - 34, x, g - 2), '#a81e1e')
    line(d, (x + 14, g - 34, x + 14, g - 2), '#a81e1e')
    line(d, (x + 3, g - 34, x + 3, g - 3), '#ec5a4a')
    ellipse(d, (x - 2, g - 40, x + 16, g - 30), '#c82424')
    ellipse(d, (x, g - 40, x + 12, g - 34), '#e44a40')
    rect(d, (x + 3, g - 27, x + 11, g - 25), '#3a1414')                         # 投信口
    rect(d, (x + 4, g - 21, x + 10, g - 15), '#f4f0e6')                         # 收信时间的小牌
    for y in (g - 20, g - 18, g - 16):
        line(d, (x + 5, y, x + 9, y), '#8a8a90')
    rect(d, (x - 1, g - 3, x + 15, g), '#4a4a50')                               # 底座


def curve_mirror(d, x, g, h=78):
    """カーブミラー：橙色的杆、圆镜（镜面里映一点天和路）"""
    top = g - h
    rect(d, (x - 1, top, x + 1, g), '#e8742a')
    line(d, (x - 1, top, x - 1, g), '#f49a52')
    for y in range(top + 20, g - 10, 8):
        line(d, (x - 1, y, x + 1, y), '#c85a1e')
    ellipse(d, (x - 11, top - 20, x + 11, top + 2), '#e8742a')
    ellipse(d, (x - 9, top - 18, x + 9, top), '#b8d4e4')
    ellipse(d, (x - 9, top - 9, x + 9, top), '#8a8e94')                          # 镜子里的路
    ellipse(d, (x - 6, top - 16, x - 1, top - 12), '#e8f4fa')
    rect(d, (x - 2, top + 2, x + 2, top + 5), '#7a7a80')


def street_clock_body(im, x, g, h=104, r=11):
    """路边的大钟：一根两节的柱子，顶上一个双面圆钟（钟面不带针，针是 pick 层），钟下面挂町名的牌子。返回钟心"""
    d = ImageDraw.Draw(im)
    top = g - h
    rect(d, (x - 3, top + r, x + 3, g), '#5a6a70')
    line(d, (x - 3, top + r, x - 3, g), '#7a8a90')
    line(d, (x + 2, top + r, x + 2, g), '#46545a')
    rect(d, (x - 5, g - 8, x + 5, g), '#46545a')
    line(d, (x - 5, g - 8, x + 5, g - 8), '#7a8a90')
    rect(d, (x - 4, top + r + 30, x + 4, top + r + 33), '#46545a')
    cy = top
    ellipse(d, (x - r - 3, cy - r - 3, x + r + 3, cy + r + 3), '#3e4a50')
    ellipse(d, (x - r - 2, cy - r - 2, x + r + 2, cy + r + 2), '#6a7a80')
    ellipse(d, (x - r, cy - r, x + r, cy + r), '#f8f4e8')
    for i in range(12):
        a = i * math.pi / 6
        rr = r - 1 if i % 3 else r - 2
        px(d, x + (r - 1) * math.sin(a), cy - (r - 1) * math.cos(a), '#8a8a80' if i % 3 else '#2a2a30')
        if not i % 3:
            px(d, x + rr * math.sin(a), cy - rr * math.cos(a), '#2a2a30')
    rect(d, (x - 1, cy - r - 6, x + 1, cy - r - 3), '#3e4a50')                  # 顶上的小尖
    px(d, x, cy - r - 7, '#d8c060')
    # 町名牌（竖）
    rect(d, (x + 4, cy + r + 8, x + 16, cy + r + 44), '#2e5a8a')
    rect(d, (x + 5, cy + r + 9, x + 15, cy + r + 43), '#3a6aa0')
    kanji(im, x + 5, cy + r + 10, '杜王町', '#f4f4f0', vertical=True, size=10)
    return (x, cy)


def clock_hands(r, hh, mm, hand='#2a2a30'):
    """一张 (2r+1)² 的透明图：时针 + 分针 + 红色中心"""
    S = 2 * r + 1
    im = new(S, S)
    d = ImageDraw.Draw(im)
    c = r
    am = mm / 60 * 2 * math.pi
    ah = (hh % 12 + mm / 60) / 12 * 2 * math.pi
    line(d, (c, c, c + (r - 2) * math.sin(am), c - (r - 2) * math.cos(am)), hand)
    line(d, (c, c, c + (r - 5) * math.sin(ah), c - (r - 5) * math.cos(ah)), hand)
    line(d, (c + 1, c, c + 1 + (r - 5) * math.sin(ah), c - (r - 5) * math.cos(ah)), hand)
    px(d, c, c, '#c83a34')
    return im


def tobacco_shop(im, x0, x1, G):
    """街角的烟草 / 杂货小店：一层半的木造，蓝瓦，'たばこ' 红招牌，玻璃柜台窗口，门口贴着海报"""
    d = ImageDraw.Draw(im)
    top = G - 70
    rect(d, (x0, top, x1, G), '#e2d6c0')
    for yy in range(top + 2, G, 4):
        line(d, (x0, yy, x1, yy), '#d4c8b0')
    im = tiled_roof(im, x0, x1, top - 14, top, ('#3e5a7a', '#2e4660', '#56769a', '#1e3048'), overhang=4)
    d = ImageDraw.Draw(im)
    window(d, (x0 + 8, top + 6, x0 + 30, top + 20), glass=('#8eb8d2', '#c0dcea'), curtain='#e8d8b0')
    window(d, (x1 - 32, top + 6, x1 - 10, top + 20), glass=('#8eb8d2', '#c0dcea'))
    rect(d, (x0 - 2, top + 26, x1 + 2, top + 28), '#2e4660')                       # 一楼的小屋檐
    rect(d, (x0 + 4, top + 30, x0 + 50, top + 42), '#c8262a')                      # たばこ 招牌
    rect(d, (x0 + 5, top + 31, x0 + 49, top + 41), '#e0383a')
    tw, th = kanji_size('たばこ', 10)
    kanji(im, x0 + 27 - tw // 2, top + 31, 'たばこ', '#ffffff', size=10)
    d = ImageDraw.Draw(im)
    # 柜台窗口（玻璃柜里摆着烟盒）
    rect(d, (x0 + 4, G - 26, x0 + 50, G - 4), '#8a6a48')
    rect(d, (x0 + 6, G - 24, x0 + 48, G - 12), '#b8d4e0')
    cols = ['#e8e4dc', '#d83a34', '#3a6ac8', '#f0c030', '#40a060', '#2a2a30']
    for i, bx in enumerate(range(x0 + 8, x0 + 46, 4)):
        rect(d, (bx, G - 17, bx + 2, G - 13), cols[i % len(cols)])
    line(d, (x0 + 6, G - 24, x0 + 48, G - 24), '#e8f4fa')
    rect(d, (x0 + 6, G - 11, x0 + 48, G - 5), '#6a5038')
    # 门（拉门）+ 海报
    rect(d, (x0 + 56, G - 40, x1 - 6, G), '#7a5a40')
    rect(d, (x0 + 58, G - 38, x1 - 8, G - 2), '#a8c4d0')
    line(d, ((x0 + 56 + x1 - 6) // 2, G - 38, (x0 + 56 + x1 - 6) // 2, G - 2), '#7a5a40')
    for k in range(3):
        line(d, (x0 + 58, G - 30 + k * 9, x1 - 8, G - 30 + k * 9), '#7a5a40')
    rect(d, (x1 - 4, G - 56, x1 + 6, G - 40), '#f4f0e6')                          # 墙上的海报（夏祭）
    rect(d, (x1 - 3, G - 55, x1 + 5, G - 47), '#2a3a7a')
    ellipse(d, (x1 - 1, G - 54, x1 + 4, G - 49), '#f0a040')
    line(d, (x1 - 3, G - 44, x1 + 5, G - 44), '#c83a34')
    return im


# ============================================================ 住宅区街口 morning_corner（640 宽，7 月早上 7:00–8:30）
#   镜头从左往右：民宅 A（围墙 + 牵牛花）→ 电线杆 → 往里去的小路（街口，仗助他们从里面走出来；路面写着“止まれ”）
#   → カーブミラー → 街角烟草店 + 邮筒 → 路边大钟（锚点 clock）→ 民宅 B + 夏天的树 → 电线杆 + 售货机 → 公寓。
#   太阳在左边（东）低处：东向墙面暖一点，影子往右拖得很长。
CVPX, CVPY = 206, 96                     # 小路的灭点


def corner_far(var='am'):
    if var == 'rain':
        im = sky_far(480, seed=31, cols=('#7a8494', '#8a94a2', '#a0a8b2', '#b4bac0'), sea=False)
        return im
    im = sky_far(480, seed=31, cols=('#7eb4e6', '#a2cceb', '#cfe2ee', '#f4e4c8'), sea=False)
    d = ImageDraw.Draw(im)
    # 东边低处的太阳（被对白框盖住一半也没关系，主要是那一圈暖光）
    sx, sy = 40, 62
    for r, col in ((22, '#f8ecd0'), (15, '#fcf2dc'), (9, '#fff8e8'), (6, '#ffffff')):
        for yy in range(sy - r, sy + r + 1):
            for xx in range(sx - r, sx + r + 1):
                if (xx - sx) ** 2 + (yy - sy) ** 2 <= r * r and (r < 10 or (xx + yy) % 2 == 0) and 0 <= xx < im.width:
                    px(d, xx, yy, col)
    return im


def side_street(im, G, var='am'):
    """往画面里去的小路：路面梯形收向灭点，两边围墙 + 房子跟着收，尽头一栋房子"""
    d = ImageDraw.Draw(im)
    x0, x1 = 150, 262                                       # 小路在 G 处的宽度
    hw0 = (x1 - x0) / 2
    def at(y):                                              # y 处路面的左右边
        s = (y - CVPY) / (G - CVPY)
        return CVPX - hw0 * s, CVPX + hw0 * s, s
    yend = 112                                              # 小路尽头（再远就被尽头的房子挡住）
    # 尽头的房子（正面，小）
    _, _, s_end = at(yend)
    ex0, ex1 = CVPX - 34 * s_end * 2.2, CVPX + 34 * s_end * 2.2
    rect(d, (ex0, yend - 36, ex1, yend), '#e4dccc')
    im = tiled_roof(im, ex0, ex1, yend - 44, yend - 36, ('#6a3e36', '#4e2c28', '#8a5246', '#341c1a'), overhang=2)
    d = ImageDraw.Draw(im)
    window(d, (ex0 + 4, yend - 32, ex0 + 14, yend - 24), glass=('#8eb8d2', '#c0dcea'))
    window(d, (ex1 - 14, yend - 32, ex1 - 4, yend - 24), glass=('#8eb8d2', '#c0dcea'))
    rect(d, (ex0 - 2, yend - 10, ex1 + 2, yend), '#c8c2b4')
    line(d, (ex0 - 2, yend - 10, ex1 + 2, yend - 10), '#e0dacc')
    # 两边：围墙（顶边、底边都收向灭点）+ 墙后面的房子
    for side in (-1, 1):
        xa0, xb0, sa = at(yend)
        xa1, xb1, sb = at(G)
        ea, eb = (xa0, xa1) if side < 0 else (xb0, xb1)
        poly(d, [(ea, yend), (eb, G), (eb, G - 20 * sb), (ea, yend - 20 * sa)], '#c8c2b4' if side < 0 else '#b4aea0')
        for k in range(1, 6):                                               # 砌块缝（横）
            f = k / 6
            line(d, (ea, yend - 20 * sa * f, eb, G - 20 * sb * f), '#aaa496' if side < 0 else '#a09a8c')
        line(d, (ea, yend - 20 * sa, eb, G - 20 * sb), '#e0dacc')
    # 墙后的房子（侧墙在透视里：上沿也收向灭点）
    for side, (za, zb, wall, roof) in ((-1, (0.28, 0.62, '#e8e0d2', '#3e4a5e')), (1, (0.3, 0.7, '#ecdcc4', '#3a5a52')),
                                      (-1, (0.66, 0.98, '#dfe2e6', '#6a3e36')), (1, (0.74, 1.0, '#e6dccb', '#3e4a5e'))):
        ya, yb = CVPY + (G - CVPY) * za, CVPY + (G - CVPY) * zb
        pts = []
        for y in (ya, yb):
            xl, xr, s = at(y)
            xe = (xl if side < 0 else xr) + side * 6 * s
            pts.append((xe, y - 20 * s, xe, y - 62 * s))
        (xa, ga, _, ta), (xb, gb, _, tb) = pts
        poly(d, [(xa, ga), (xb, gb), (xb, tb), (xa, ta)], wall)
        poly(d, [(xa, ta), (xb, tb), (xb, tb - 8 * (yb - CVPY) / (G - CVPY)), (xa, ta - 8 * (ya - CVPY) / (G - CVPY))], roof)
        # 一扇窗
        mx = (xa + xb) / 2
        my = (ta + ga) / 2 - 4
        sm = ((ya + yb) / 2 - CVPY) / (G - CVPY)
        rect(d, (mx - 5 * sm, my - 4 * sm, mx + 5 * sm, my + 3 * sm), '#9cc4dc')
        line(d, (mx, my - 4 * sm, mx, my + 3 * sm), '#e8e4dc')
    # 路面
    for y in range(yend, G + 1):
        xl, xr, s = at(y)
        line(d, (xl, y, xr, y), '#56565c' if var != 'rain' else '#4a4e58')
    rng = np.random.RandomState(9)                                           # 路面颗粒（只撒在梯形里）
    for y in range(yend, G + 1):
        xl, xr, s = at(y)
        for _ in range(int((xr - xl) / 5)):
            px(d, rng.uniform(xl + 1, xr - 1), y, ['#4a4a50', '#62626a'][rng.randint(2)])
    # 路边白线（两条收向灭点）
    for side in (-1, 1):
        for y in range(yend, G + 1):
            xl, xr, s = at(y)
            xe = (xl if side < 0 else xr) - side * 5 * s
            px(d, xe, y, '#d8d4c8')
    return im


def corner_near(var='am'):
    W, G = 640, 136
    im = new(W, 180)
    im = sidewalk(im, 0, W, G, 166)
    im = asphalt(im, 0, W, 166, 180)
    # 小路（覆盖人行道那一段：路口降下来的路面 + 斑马线前的停止线 + “止まれ”）
    im = side_street(im, G, var)
    d = ImageDraw.Draw(im)
    rect(d, (150, G, 262, 166), '#56565c')
    noise_specks(im, (150, G + 1, 262, 166), ['#4a4a50', '#62626a', '#6a6a72'], 520, 13)
    d = ImageDraw.Draw(im)
    line(d, (150, G, 262, G), '#6a6a70')
    rect(d, (152, G + 6, 260, G + 7), '#e8e4d8')                                 # 停止线
    m = LIB.text_mask('止まれ', LIB.WQY, 12, index=1)                            # 路面字：横着压扁
    im.paste(C('#e8e4d8'), (206 - m.width // 2, G + 12), m)
    d = ImageDraw.Draw(im)
    for x in (149, 263):                                                        # 路口两边的路缘石
        rect(d, (x - 1, G, x + 1, 166), '#94908a')
    # ---- 民宅 A（0–118）
    im = house(im, -6, G - 10, 112, 74, wall='#ece2d0', wall2='#cfc2aa', seed=51, roof=('#3e4a5e', '#2e3848', '#56647a', '#1e2632'))
    im = hedge(im, -4, 118, G - 28, G - 20, seed=52)
    im = block_wall(im, -4, 118, G - 20, G)
    d = ImageDraw.Draw(im)
    rect(d, (60, G - 26, 82, G), '#5a5a60')                                     # 门（铁栅门）
    for gx in range(62, 82, 3):
        line(d, (gx, G - 24, gx, G - 1), '#8a8a92')
    line(d, (60, G - 26, 82, G - 26), '#a8a8b0')
    rect(d, (86, G - 16, 98, G - 8), '#f4f0e6')                                 # 门牌
    kanji(im, 87, G - 16, '田中', '#2a2a30', size=10)
    morning_glory(im, 4, 56, G - 24, G - 2, seed=3)
    morning_glory(im, 88, 116, G - 24, G - 2, seed=4)
    # ---- 电线杆 1
    im = pole(im, 132, G + 2, 130)
    # ---- カーブミラー（路口右角）
    d = ImageDraw.Draw(im)
    curve_mirror(d, 270, G + 2, 82)
    # ---- 街角烟草店 + 邮筒（276–372）
    im = tobacco_shop(im, 276, 372, G)
    d = ImageDraw.Draw(im)
    postbox(d, 352, G + 4)
    # ---- 路边大钟（锚点 clock）
    clock = street_clock_body(im, 398, G + 4, 86, 11)
    # ---- 民宅 B（420–560）：围墙 + 院子里的树
    im = round_tree(im, 452, G - 14, 84, 66, seed=7)
    im = house(im, 470, G - 10, 92, 70, wall='#e6dccb', wall2='#c8bca8', seed=53, roof=('#6a3e36', '#4e2c28', '#8a5246', '#341c1a'))
    im = block_wall(im, 418, 566, G - 20, G)
    morning_glory(im, 424, 470, G - 24, G - 2, seed=5)
    d = ImageDraw.Draw(im)
    rect(d, (520, G - 24, 540, G), '#7a5a40')                                   # 木门
    rect(d, (522, G - 22, 538, G - 1), '#9a7656')
    line(d, (530, G - 22, 530, G - 1), '#7a5a40')
    # ---- 电线杆 2 + 售货机
    im = pole(im, 572, G + 2, 130)
    im = vending(im, 578, G + 2, body='#2a6ac0', accent='#e8eef4')
    # ---- 公寓（604–640+）：两层，外楼梯
    d = ImageDraw.Draw(im)
    rect(d, (604, G - 82, W, G), '#d8d0c4')
    for yy in range(G - 80, G, 4):
        line(d, (604, yy, W, yy), '#ccc4b6')
    rect(d, (602, G - 86, W, G - 82), '#6a6a72')
    rect(d, (604, G - 44, W, G - 41), '#a8a49c')                                  # 二楼的走廊板
    for x in range(606, W, 4):
        line(d, (x, G - 54, x, G - 44), '#8a8a92')
    line(d, (604, G - 54, W, G - 54), '#a8a8b0')
    for k, dx in enumerate((612, 630)):
        rect(d, (dx, G - 78, dx + 12, G - 56), '#7a8a9a')                          # 二楼的门
        rect(d, (dx, G - 36, dx + 12, G - 2), '#8a7a6a')                           # 一楼的门
        px(d, dx + 9, G - 18, '#e8c860')
    for i in range(10):                                                          # 外楼梯（往右上）
        y = G - 2 - i * 4
        rect(d, (606 + i * 0, y - 1, 610, y), '#6a6a72')
    # ---- 电线
    im = wires(im, [(-40, 20), (132, G + 2 - 130 + 7), (572, G + 2 - 130 + 7), (700, 30)], sag=10)
    # ---- 早上的光：东向（左边）的竖边暖一点，地上拖长影子（往右）
    if var != 'rain':
        for x0, x1, top in ((0, 118, G - 90), (276, 372, G - 86), (470, 562, G - 86), (604, 640, G - 86)):
            im = warm_side(im, (x0, max(0, top), min(W, x0 + 14), G), (1.05, 1.0, .93))
        L = 1.2                                                                   # 影长 / 物高 的水平分量
        for x, h, w in ((132, 130, 4), (270, 82, 3), (398, 86, 6), (572, 130, 4)):
            im = shade_poly(im, [(x - w // 2, G + 1), (x + w // 2 + 1, G + 1), (x + w // 2 + 1 + h * .55, G + 20), (x - w // 2 + h * .55, G + 20)])
        im = shade_poly(im, [(352, G + 2), (366, G + 2), (384, G + 10), (370, G + 10)])          # 邮筒
        im = shade_poly(im, [(578, G + 2), (600, G + 2), (626, G + 12), (604, G + 12)])          # 售货机
        for x0, x1 in ((0, 118), (418, 566)):                                   # 围墙脚下一条窄影
            im = shade_poly(im, [(x0, G + 1), (x1, G + 1), (x1 + 8, G + 4), (x0 + 8, G + 4)])
    else:
        im = tint(im, (.78, .82, .9), (0, 0, 6), desat=.25)
    return im, G, clock


def morning_corner():
    W = 640
    far = corner_far()
    near, G, (cx, cy) = corner_near()
    layers = {'far': far, 'near': near}
    r = 11
    times = [(h, m) for h in (7, 8) for m in range(0, 60, 5) if h * 60 + m <= 510]
    os.makedirs(os.path.join(LIB.ASSETS, 'bg', 'morning_corner'), exist_ok=True)
    imgs, vals = [], []
    for h, m in times:
        name = f'clock_{h:02d}{m:02d}'
        layers[name] = clock_hands(r, h, m)
        imgs.append('bg/morning_corner/' + name)
        vals.append(h * 60 + m)
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(clock=[cx, cy], clock_base=[cx, 146], postbox=[359, 146], shop=[300, 146], shop_window=[303, 128],
                             mirror=[270, 146], alley=[206, 146], alley_far=[206, 116], gate_a=[71, 146], gate_b=[530, 146],
                             vending=[589, 146], apartment=[618, 146], pole_l=[132, 146], pole_r=[572, 146], walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/morning_corner/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/morning_corner/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pick', 'images': imgs, 'values': vals, 'key': 'clock', 'k': 1, 'x': cx - r, 'y': cy - r},
                        {'type': 'tint', 'color': '#ffb060', 'alpha': 0.10, 'key': 'dawn'},
                        {'type': 'tint', 'color': '#1a2040', 'alpha': 0.35, 'key': 'dark'}],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    pv.alpha_composite(layers['clock_0829' if 'clock_0829' in layers else 'clock_0830'], (cx - r, cy - r))
    preview('morning_corner', {'room': pv}, ['room'], W)
    save_layers('morning_corner', layers, meta)
    return meta


# ============================================================ 十字路口 street_crossing（960 宽，白天）
#   第 17 战段 A：露伴背着 Cheap Trick 从商店街走到大马路口、过斑马线、贴着写字楼的墙往杜王大酒店去。
#   0–400 铺面一排（药店、照相馆、花店、银行转角）→ 400–580 横穿的大路（往画面里收向灭点）+ 斑马线 + 两组红绿灯
#   → 580–960 写字楼（玻璃门）、没有窗的长墙（立体停车场，贴墙走的地方）、邮局、电话亭、去大酒店的蓝路牌。
XVPX, XVPY = 490, 90                     # 大路的灭点
XR0, XR1 = 404, 576                      # 大路在人行道那一行（G）的左右边


def crossing_far2():
    im = sky_far(640, seed=41, cols=('#6aa4e2', '#86b8ea', '#acd0f0', '#d8e8f2'), sea=False)
    return im


def crossroad(im, G):
    """横穿的大路：路面梯形、中线、两边的人行道和楼（侧墙在透视里），尽头一排远楼"""
    d = ImageDraw.Draw(im)
    hw = (XR1 - XR0) / 2
    def at(y, k=1.0):
        s = (y - XVPY) / (G - XVPY)
        return XVPX - hw * k * s, XVPX + hw * k * s, s
    yend = 104
    # 尽头的远楼（几栋不同高的楼，正面）
    rng = np.random.RandomState(12)
    x = XVPX - 70
    while x < XVPX + 70:
        bw = rng.randint(14, 26)
        bh = rng.randint(22, 50)
        col = ['#d8d4cc', '#c8ccd2', '#e2d8c8', '#b8c0c8'][rng.randint(4)]
        rect(d, (x, yend - bh, x + bw, yend), col)
        for wy in range(yend - bh + 3, yend - 3, 5):
            for wx in range(x + 2, x + bw - 2, 4):
                px(d, wx, wy, '#8eaac0')
                px(d, wx + 1, wy, '#8eaac0')
        line(d, (x + bw, yend - bh, x + bw, yend), mix(col, '#000000', .15))
        x += bw
    # 两侧人行道（外扩 1.35 倍那条线到路边）+ 沿街的楼
    for side in (-1, 1):
        for (za, zb), col, hgt in (((0.0, 0.45), '#d6cfc2', 70), ((0.45, 0.78), '#c4ccd4', 96), ((0.78, 1.0), '#e0d6c6', 60)):
            ya, yb = yend + (G - yend) * za, yend + (G - yend) * zb
            _, _, sa = at(ya)
            _, _, sb = at(yb)
            xa = XVPX + side * hw * 1.4 * sa
            xb = XVPX + side * hw * 1.4 * sb
            poly(d, [(xa, ya), (xb, yb), (xb, yb - hgt * sb), (xa, ya - hgt * sa)], col if side < 0 else mix(col, '#000000', .1))
            # 一层层的窗带
            for f in range(1, int(hgt / 12)):
                k = f * 12 / hgt
                line(d, (xa, ya - hgt * sa * k, xb, yb - hgt * sb * k), mix(col, '#5a7890', .55))
            line(d, (xa, ya - hgt * sa, xb, yb - hgt * sb), mix(col, '#ffffff', .3))
            line(d, (xb, yb, xb, yb - hgt * sb), mix(col, '#000000', .25))
        # 人行道面
        pts = []
        for y in (yend, G):
            xl, xr, s = at(y)
            e = xl if side < 0 else xr
            o = XVPX + side * hw * 1.4 * s
            pts.append((e, o, y))
        (ea, oa, ya), (eb, ob, yb) = pts
        poly(d, [(ea, ya), (eb, yb), (ob, yb), (oa, ya)], '#b8b4ac')
    # 路面
    for y in range(yend, G + 1):
        xl, xr, s = at(y)
        line(d, (xl, y, xr, y), '#505058')
    rng = np.random.RandomState(13)
    for y in range(yend, G + 1):
        xl, xr, s = at(y)
        for _ in range(int((xr - xl) / 5)):
            px(d, rng.uniform(xl + 1, xr - 1), y, ['#46464c', '#5e5e66'][rng.randint(2)])
    # 中线（黄）+ 车道虚线（白）
    for y in range(yend, G + 1):
        xl, xr, s = at(y)
        px(d, XVPX, y, '#e8c040')
        if (int(math.log(max(1, y - XVPY)) * 14)) % 2:
            for k in (-.5, .5):
                px(d, XVPX + hw * k * s, y, '#d8d4c8')
    # 路缘石
    for side in (-1, 1):
        for y in range(yend, G + 1):
            xl, xr, s = at(y)
            px(d, xl if side < 0 else xr, y, '#8a8a8e')
    return im


def ped_signal(im, x, G, state):
    """行人信号灯（上红人 / 下绿人）+ 车辆信号灯（横的 青黄红，朝大马路）。state: 'red' = 行人红、车绿；'green' 反过来；None = 都不亮（底图）"""
    d = ImageDraw.Draw(im)
    top = G - 96
    if state is None:
        rect(d, (x - 2, top, x + 2, G), '#7a7e86')
        line(d, (x - 2, top, x - 2, G), '#9a9ea6')
        line(d, (x + 1, top, x + 1, G), '#5a5e66')
        rect(d, (x - 4, G - 6, x + 4, G), '#5a5e66')
        rect(d, (x - 1, top + 2, x + 1, top + 4), '#5a5e66')
        # 车辆灯：横臂往路中间伸
        side = 1 if x < XVPX else -1
        line(d, (x, top + 6, x + side * 26, top + 6), '#7a7e86', 2)
        bx = x + side * 26 - (34 if side < 0 else 0)
        rect(d, (bx, top, bx + 34, top + 12), '#3a3e46')
        rect(d, (bx, top - 2, bx + 34, top), '#2a2e36')                             # 遮阳檐
        for i in range(3):
            ellipse(d, (bx + 2 + i * 11, top + 2, bx + 10 + i * 11, top + 10), '#1e2228')
        # 行人灯箱
        rect(d, (x + 3, top + 18, x + 15, top + 44), '#3a3e46')
        rect(d, (x + 4, top + 19, x + 14, top + 30), '#1e2228')
        rect(d, (x + 4, top + 32, x + 14, top + 43), '#1e2228')
        # 按钮盒（押しボタン）
        rect(d, (x - 8, G - 52, x - 2, G - 40), '#e8c030')
        rect(d, (x - 7, G - 49, x - 3, G - 45), '#c83a34')
        return
    side = 1 if x < XVPX else -1
    bx = x + side * 26 - (34 if side < 0 else 0)
    car = 0 if state == 'red' else 2                                      # 0 青 1 黄 2 红（日本的灯从左到右）
    cols = ('#38d0a0', '#f0c030', '#f04030')
    i = car
    cx, cy = bx + 6 + i * 11, top + 6
    ellipse(d, (cx - 4, cy - 4, cx + 4, cy + 4), cols[i])
    px(d, cx - 1, cy - 2, '#ffffff')
    # 行人灯：亮的那一格画小人
    if state == 'red':
        bx0, by0, c = x + 4, top + 19, '#f04030'
        rect(d, (bx0, by0, bx0 + 10, by0 + 11), '#3a1410')
        ellipse(d, (bx0 + 4, by0 + 1, bx0 + 6, by0 + 3), c)
        rect(d, (bx0 + 3, by0 + 4, bx0 + 7, by0 + 8), c)
        line(d, (bx0 + 4, by0 + 8, bx0 + 4, by0 + 10), c)
        line(d, (bx0 + 6, by0 + 8, bx0 + 6, by0 + 10), c)
    else:
        bx0, by0, c = x + 4, top + 32, '#40e0a0'
        rect(d, (bx0, by0, bx0 + 10, by0 + 11), '#0e3020')
        ellipse(d, (bx0 + 4, by0 + 1, bx0 + 6, by0 + 3), c)
        line(d, (bx0 + 5, by0 + 4, bx0 + 4, by0 + 7), c)
        line(d, (bx0 + 6, by0 + 4, bx0 + 5, by0 + 7), c)
        line(d, (bx0 + 4, by0 + 5, bx0 + 2, by0 + 7), c)
        line(d, (bx0 + 6, by0 + 5, bx0 + 8, by0 + 6), c)
        line(d, (bx0 + 4, by0 + 7, bx0 + 2, by0 + 10), c)
        line(d, (bx0 + 5, by0 + 7, bx0 + 7, by0 + 10), c)


def phone_box(im, x, G):
    """绿色公用电话亭（玻璃 + 绿顶）"""
    return phone_booth(im, x, G)


def crossing_near2():
    W, G = 960, 136
    im = new(W, 180)
    im = sidewalk(im, 0, W, G, 166)
    im = asphalt(im, 0, W, 166, 180)
    im = crossroad(im, G)
    d = ImageDraw.Draw(im)
    # 大路穿过人行道那一段：路面 + 斑马线（白色横条，人沿着条走）+ 两边的盲道砖
    rect(d, (XR0, G, XR1, 166), '#505058')
    rng = np.random.RandomState(14)
    for y in range(G, 166):
        for _ in range(30):
            px(d, rng.randint(XR0, XR1), y, ['#46464c', '#5e5e66'][rng.randint(2)])
    for y in range(G + 3, 165, 6):
        rect(d, (XR0 + 6, y, XR1 - 6, y + 2), '#ece8dc')
        line(d, (XR0 + 6, y + 2, XR1 - 6, y + 2), '#c8c4b8')
    for x0 in (XR0 - 10, XR1 + 2):
        rect(d, (x0, G + 2, x0 + 7, 164), '#e8c030')
        for yy in range(G + 3, 164, 3):
            for xx in range(x0 + 1, x0 + 7, 3):
                px(d, xx, yy, '#c8a020')
    for x in (XR0, XR1):
        rect(d, (x - 1, G, x, 166), '#94908a')
    # ---------------- 左：铺面一排（0–400）
    # 药店（0–96）
    sy = facade(im, -4, 96, G - 100, G, '#e8e4dc', '#4a8a5a', seed=61, floors=2)
    signboard(im, -4, 96, sy, 13, '#2e8a4a', '#1e5a32', text='くすり', col='#ffffff')
    shop_front(im, 0, 94, G, frame='#6a7a6a', door_at=58)
    d = ImageDraw.Draw(im)
    rect(d, (8, G - 38, 22, G - 24), '#f4f4f0')                                 # 绿十字
    rect(d, (13, G - 36, 17, G - 26), '#2e9a4a')
    rect(d, (10, G - 33, 20, G - 29), '#2e9a4a')
    for i, bx in enumerate(range(26, 54, 6)):                                   # 货架上的药盒
        rect(d, (bx, G - 22, bx + 4, G - 14), ['#f0c030', '#e05a4a', '#4a90d8', '#f4f0e6', '#58b068'][i % 5])
    # 照相馆（96–200）：露伴的照片在这里冲洗——橱窗里一排相片
    sy = facade(im, 96, 200, G - 92, G, '#d8dce4', '#3a4a6a', seed=62, floors=2)
    signboard(im, 96, 200, sy, 13, '#f4f0e6', '#3a4a6a', text='カメラ', col='#2a3a6a', latin=None)
    d = ImageDraw.Draw(im)
    letters(d, 172, sy + 4, 'DPE', '#c83a34')
    win = shop_front(im, 100, 196, G, frame='#3a4a6a', door_at=168)
    d = ImageDraw.Draw(im)
    for i, (px0, py0) in enumerate([(106, G - 40), (124, G - 40), (142, G - 40), (106, G - 26), (124, G - 26), (142, G - 26)]):
        rect(d, (px0, py0, px0 + 14, py0 + 11), '#f8f8f4')
        rect(d, (px0 + 1, py0 + 1, px0 + 13, py0 + 9), ['#7aa8d0', '#d8a878', '#88b878', '#c8a0c0', '#a0a8b8', '#e8c890'][i])
        ellipse(d, (px0 + 5, py0 + 3, px0 + 8, py0 + 6), '#e8c4a0')
    # 花店（200–300）：门口一排水桶，夏天的向日葵
    sy = facade(im, 200, 300, G - 96, G, '#f0ece2', '#d86a8a', seed=63, floors=2)
    signboard(im, 200, 300, sy, 13, '#f4a0be', '#c85a7a', text='花', col='#ffffff')
    awning(im, 202, 298, G - 48, 8, ('#f4f0e6', '#d86a8a'))
    shop_front(im, 204, 296, G, frame='#8a6a5a', door_at=272)
    d = ImageDraw.Draw(im)
    for i, bx in enumerate(range(206, 268, 10)):
        rect(d, (bx, G - 10, bx + 8, G - 1), '#8a8e96')
        line(d, (bx, G - 10, bx + 8, G - 10), '#b8bcc4')
        fl = [('#f0c030', '#8a5a1e'), ('#e05a7a', '#f8a0b8'), ('#f8f4f0', '#f0d060'), ('#a070d0', '#c8a0e8'), ('#f08a3a', '#f8c070'),
              ('#d83a34', '#f06a5a'), ('#f0c030', '#8a5a1e')][i % 7]
        for k in range(3):
            fx = bx + 1 + k * 3
            line(d, (fx + 1, G - 10, fx + 1, G - 17 - (k % 2) * 3), '#4a8a3a')
            ellipse(d, (fx - 1, G - 21 - (k % 2) * 3, fx + 3, G - 17 - (k % 2) * 3), fl[0])
            px(d, fx + 1, G - 19 - (k % 2) * 3, fl[1])
    # 银行转角（300–404）：灰色石材，自动门，ATM
    d = ImageDraw.Draw(im)
    rect(d, (300, G - 104, 404, G), '#c4c2bc')
    for yy in range(G - 100, G, 8):
        line(d, (300, yy, 404, yy), '#b0aea8')
        for xx in range(300 + (yy // 8 % 2) * 12, 404, 24):
            line(d, (xx, yy, xx, yy + 7), '#b0aea8')
    rect(d, (298, G - 108, 406, G - 104), '#8a8884')
    for wx in range(306, 400, 24):
        window(d, (wx, G - 96, wx + 18, G - 78), frame='#9a9894', glass=('#8aa8c0', '#b8d0e0'), bars=False)
    rect(d, (300, G - 66, 404, G - 52), '#1e4a8a')
    tw, th = kanji_size('杜王銀行')
    kanji(im, 352 - tw // 2, G - 65, '杜王銀行', '#ffffff')
    d = ImageDraw.Draw(im)
    rect(d, (310, G - 46, 360, G), '#4a4a50')                                   # 自动门
    rect(d, (312, G - 44, 334, G - 1), '#9ab8cc')
    rect(d, (336, G - 44, 358, G - 1), '#9ab8cc')
    line(d, (314, G - 42, 320, G - 36), '#d0e4ee')
    line(d, (338, G - 42, 344, G - 36), '#d0e4ee')
    rect(d, (366, G - 40, 398, G), '#8a8884')                                   # ATM 角
    rect(d, (368, G - 38, 396, G - 26), '#2e5a9a')
    letters(d, 372, G - 34, 'ATM', '#ffffff')
    rect(d, (372, G - 22, 392, G - 2), '#d8d6d0')
    # 街灯
    for x in (96, 296):
        lamp_post(im, x, G + 2, 92)
    # ---------------- 右：写字楼 / 长墙 / 邮局（580–960）
    d = ImageDraw.Draw(im)
    # 写字楼（580–720）：往上出画，玻璃门厅
    rect(d, (580, 0, 720, G), '#d4d8de')
    for yy in range(0, G - 50, 16):
        rect(d, (584, yy + 4, 716, yy + 13), '#7a9ab4')
        for xx in range(584, 716, 12):
            line(d, (xx, yy + 4, xx, yy + 13), '#c4cad2')
        line(d, (584, yy + 4, 716, yy + 4), '#a8c0d4')
    rect(d, (580, G - 48, 720, G - 44), '#8a8e96')
    rect(d, (600, G - 42, 680, G), '#4a5058')
    for xx in range(602, 680, 13):
        rect(d, (xx, G - 40, xx + 11, G - 1), '#8cb0c8')
        line(d, (xx + 1, G - 38, xx + 5, G - 32), '#c0d8e6')
    tw, th = kanji_size('杜王ビル', 10)
    rect(d, (699 - tw // 2 - 3, G - 31, 699 + tw // 2 + 3, G - 31 + th + 2), '#f4f4f0')
    kanji(im, 699 - tw // 2, G - 30, '杜王ビル', '#3a3e46', size=10)
    d = ImageDraw.Draw(im)
    # 立体停车场（720–830）：没窗的长墙（贴墙走），上面一排通风格栅
    rect(d, (720, G - 110, 830, G), '#b8b4aa')
    for yy in (G - 104, G - 76, G - 48):
        rect(d, (720, yy, 830, yy + 10), '#8a8a90')
        for xx in range(722, 830, 4):
            line(d, (xx, yy + 1, xx, yy + 9), '#6a6a72')
    rect(d, (720, G - 36, 830, G), '#c8c4ba')
    for xx in range(720, 830, 22):
        line(d, (xx, G - 36, xx, G), '#b0aca2')
    line(d, (720, G - 36, 830, G - 36), '#d8d4ca')
    rect(d, (796, G - 66, 826, G - 52), '#2e5a9a')                              # P 牌
    letters(d, 800, G - 62, 'P', '#ffffff')
    d = ImageDraw.Draw(im)
    letters(d, 806, G - 62, '24H', '#f0e060')
    # 邮局（830–960）
    sy = facade(im, 830, 964, G - 90, G, '#f0ece4', '#c83a34', seed=64, floors=2)
    signboard(im, 830, 964, sy, 13, '#f4f0e6', '#c83a34', text='杜王郵便局', col='#c83a34')
    shop_front(im, 836, 960, G, frame='#8a8a90', door_at=880, door_w=20)
    d = ImageDraw.Draw(im)
    rect(d, (842, G - 40, 860, G - 24), '#c83a34')                             # 〒
    line(d, (845, G - 37, 857, G - 37), '#ffffff')
    line(d, (845, G - 34, 857, G - 34), '#ffffff')
    line(d, (851, G - 34, 851, G - 27), '#ffffff')
    postbox(d, 916, G + 4)
    # 电话亭（在长墙前，挡住一段墙）
    im = phone_box(im, 742, G + 2)
    # 去大酒店的蓝路牌（立在路口右角）
    d = ImageDraw.Draw(im)
    rect(d, (630, G - 62, 631, G + 2), '#8a8a90')
    tw, th = kanji_size('杜王グランドホテル', 10)
    sx0, sx1 = 631 - tw // 2 - 4, 631 + tw // 2 + 4
    rect(d, (sx0, G - 78, sx1, G - 58), '#2a6ab0')
    rect(d, (sx0 + 1, G - 77, sx1 - 1, G - 59), '#3a7ac8')
    kanji(im, 631 - tw // 2, G - 77, '杜王グランドホテル', '#f0f0f0', size=10)
    d = ImageDraw.Draw(im)
    line(d, (sx0 + 6, G - 62, sx1 - 6, G - 62), '#f0f0f0')
    line(d, (sx1 - 6, G - 62, sx1 - 10, G - 65), '#f0f0f0')
    line(d, (sx1 - 6, G - 62, sx1 - 10, G - 59), '#f0f0f0')
    # 街灯
    for x in (700, 860):
        lamp_post(im, x, G + 2, 92)
    # 信号灯底图（两个路角）
    ped_signal(im, XR0 - 4, G + 2, None)
    ped_signal(im, XR1 + 4, G + 2, None)
    # 电线（商店街这边有电线杆）
    im = pole(im, 36, G + 2, 132)
    im = wires(im, [(-40, 20), (36, G + 2 - 132 + 7), (400, 4)], sag=10)
    # 影子（中午偏下午：短，往左下）
    for x, h in ((XR0 - 4, 96), (XR1 + 4, 96), (96, 92), (296, 92), (700, 92), (860, 92), (630, 62)):
        im = shade_poly(im, [(x - 2, G + 1), (x + 2, G + 1), (x + 2 - h * .12, G + 8), (x - 2 - h * .12, G + 8)])
    return im, G


def street_crossing():
    W = 960
    far = crossing_far2()
    near, G = crossing_near2()
    red, green = new(W, 180), new(W, 180)
    for x in (XR0 - 4, XR1 + 4):
        ped_signal(red, x, G + 2, 'red')
        ped_signal(green, x, G + 2, 'green')
    layers = {'far': far, 'near': near, 'sig_red': red.crop((XR0 - 60, 0, XR1 + 60, 120)),
              'sig_green': green.crop((XR0 - 60, 0, XR1 + 60, 120))}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(pharmacy=[50, 146], camera_shop=[148, 146], camera_window=[130, 112], flower=[250, 146],
                             bank=[352, 146], atm=[382, 146], signal_l=[XR0 - 4, 146], signal_r=[XR1 + 4, 146],
                             crosswalk=[XR0, XR1], road_far=[XVPX, 104], office=[640, 146], office_door=[640, 146],
                             wall=[720, 830], phone=[752, 146], hotel_sign=[637, 146], post=[896, 146], postbox=[923, 146],
                             exit_x=944, walk_x=[8, 952]),
                layers=[{'type': 'pano', 'image': 'bg/street_crossing/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/street_crossing/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pick', 'images': ['bg/street_crossing/sig_red', 'bg/street_crossing/sig_green'], 'key': 'signal',
                         'k': 1, 'x': XR0 - 60, 'y': 0},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    pv.alpha_composite(layers['sig_red'], (XR0 - 60, 0))
    preview('street_crossing', {'room': pv}, ['room'], W)
    pv2 = pv.copy()
    pv2.alpha_composite(near.crop((XR0 - 60, 0, XR1 + 60, 120)), (XR0 - 60, 0))
    pv2.alpha_composite(layers['sig_green'], (XR0 - 60, 0))
    pv2.save(os.path.join(LIB.ASSETS, 'preview', 'bg_street_crossing_green.png'))
    save_layers('street_crossing', layers, meta)
    return meta


# ============================================================ 露伴宅修缮版 rohan_house_scaffold（480 宽，第5章 rohan_house + 脚手架）
#   乙雅三来看第9章那场火之后的修缮：右翼（二楼工作室凸窗到右端）搭着钢管脚手架，最右一跨挂着防护网，
#   梯子靠在左边那根立杆上，院墙上挂“工事中”的牌子。脚手架在院墙栏杆后面（栏杆重新盖一遍）。
#   底图从第5章的 p4_bg_ch5.rohan_house_layers() 来；第5章分支没合进来时跳过这张（保留已经生成的文件）。
SCAF_X = (278, 356, 412)                 # 三根立杆
SCAF_Y = (32, 92, 118)                   # 横杆（避开凸窗 RH_STUDY 的 y 38–89）


def scaffold_layer(W=480):
    im = new(W, 180)
    d = ImageDraw.Draw(im)
    x0, x1 = SCAF_X[0], SCAF_X[-1]
    top, base = SCAF_Y[0] - 4, 128
    # 防护网（最右一跨）：抖动的灰蓝网，墙面透出来一半
    for y in range(SCAF_Y[0], 120):
        for x in range(SCAF_X[1] + 2, SCAF_X[2] - 1):
            if (x + y) % 2 == 0:
                px(d, x, y, '#6a8aa0' if (y // 6) % 2 else '#5e7e94')
    for y in range(SCAF_Y[0], 120, 12):                                       # 网的绑绳
        line(d, (SCAF_X[1] + 2, y, SCAF_X[2] - 2, y), '#4a6478')
    # 斜撑（右跨里一根，左跨下半一根）
    line(d, (SCAF_X[1], SCAF_Y[1], SCAF_X[2], SCAF_Y[0]), '#8a9098')
    line(d, (SCAF_X[0], SCAF_Y[2], SCAF_X[1], SCAF_Y[1]), '#8a9098')
    # 立杆
    for x in SCAF_X:
        rect(d, (x - 1, top, x, base), '#9aa0a8')
        line(d, (x - 1, top, x - 1, base), '#c4c8ce')
        rect(d, (x - 3, base - 2, x + 2, base), '#6a6e74')                    # 底座
    # 横杆 + 踏板（钢踏板，带一排孔）；右跨中间多一道横杆
    for y in SCAF_Y:
        line(d, (x0 - 4, y, x1 + 4, y), '#8a9098')
        rect(d, (x0 - 2, y - 3, x1 + 2, y - 1), '#a8a69c')
        line(d, (x0 - 2, y - 3, x1 + 2, y - 3), '#c8c6bc')
        for x in range(x0, x1, 4):
            px(d, x, y - 2, '#7a786e')
    line(d, (SCAF_X[1], 62, SCAF_X[2] + 4, 62), '#8a9098')
    rect(d, (SCAF_X[1], 59, SCAF_X[2] + 2, 61), '#a8a69c')
    for y in SCAF_Y + (62,):                                                  # 扣件
        for x in SCAF_X:
            if y == 62 and x == SCAF_X[0]:
                continue
            rect(d, (x - 2, y - 1, x + 1, y + 1), '#5a5e66')
    # 顶上的扶手栏杆
    line(d, (x0 - 2, SCAF_Y[0] - 10, x1 + 2, SCAF_Y[0] - 10), '#8a9098')
    for x in SCAF_X:
        rect(d, (x - 1, SCAF_Y[0] - 10, x, SCAF_Y[0]), '#9aa0a8')
    # 梯子（靠在左立杆，从下层踏板到地）
    lx = SCAF_X[0] + 6
    for xx in (lx, lx + 7):
        line(d, (xx, SCAF_Y[1] - 2, xx + 3, base - 1), '#c8a050')
    for y in range(SCAF_Y[1] + 2, base - 1, 5):
        k = (y - SCAF_Y[1]) / (base - SCAF_Y[1])
        line(d, (lx + 3 * k, y, lx + 7 + 3 * k, y), '#a88038')
    # 院子里堆着的钢管 + 一袋水泥
    for i in range(4):
        line(d, (300, 126 - i * 2, 346, 124 - i * 2), '#9aa0a8')
        px(d, 300, 126 - i * 2, '#5a5e66')
    rect(d, (384, 120, 396, 127), '#d8d0bc')
    line(d, (384, 120, 396, 120), '#ece4d0')
    return im


def koji_sign(im, x, y):
    """院墙栏杆上挂的“工事中”牌：黄底，黑红字，两角绑着铁丝"""
    d = ImageDraw.Draw(im)
    tw, th = kanji_size('工事中', 10)
    w = tw + 6
    rect(d, (x, y, x + w, y + th + 6), '#2a2a30')
    rect(d, (x + 1, y + 1, x + w - 1, y + th + 5), '#f4d040')
    kanji(im, x + 3, y + 3, '工事中', '#c82a2a', size=10)
    d = ImageDraw.Draw(im)
    for xx in (x + 1, x + w - 1):
        px(d, xx, y - 1, '#6a6a70')
    return (x + w // 2, y + th + 6)


def rohan_house_scaffold():
    try:
        from p4_bg_ch5 import RH_STUDY, rh_fence, rohan_house_layers
    except ImportError:
        print('  跳过 rohan_house_scaffold：第5章的 p4_bg_ch5.py 还没合进来')
        return None
    W = 480
    far, near, _win, _ = rohan_house_layers()
    near.alpha_composite(scaffold_layer(W))
    fence = rh_fence(new(W, 180))                                               # 栏杆盖回脚手架前面
    near.alpha_composite(fence)
    koji_sign(near, 366, 110)
    layers = {'far': far, 'near': near}
    sx, sy = (RH_STUDY[0] + RH_STUDY[2]) // 2, (RH_STUDY[1] + RH_STUDY[3]) // 2
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(gate=[240, 148], gate_in=[240, 140], porch=[240, 128], nameplate=[202, 117], mailbox=[280, 115],
                             study_window=[sx, sy], study_window_box=list(RH_STUDY), house_box=[64, 8, 416, 128],
                             scaffold_box=[SCAF_X[0] - 4, SCAF_Y[0] - 10, SCAF_X[2] + 4, 128], scaffold_deck=[317, SCAF_Y[1] - 3],
                             ladder=[SCAF_X[0] + 10, 128], koji_sign=[380, 110], pole=[132, 148], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/rohan_house_scaffold/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/rohan_house_scaffold/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    preview('rohan_house_scaffold', {'room': pv}, ['room'], W)
    save_layers('rohan_house_scaffold', layers, meta)
    return meta


SCENES = {'morning_corner': morning_corner, 'street_crossing': street_crossing, 'rohan_house_scaffold': rohan_house_scaffold}


def main(keys):
    path = os.path.join(LIB.META, 'bg_ch11.json')
    allm = LIB.load_json(path, {}) or {}
    for k in (keys or list(SCENES)):
        m = SCENES[k]()
        if m is None:                       # 依赖别章脚本、那一章还没合进来：保留已生成的
            continue
        allm[k] = m
        print('背景', k)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(allm, fh, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main(sys.argv[1:])
