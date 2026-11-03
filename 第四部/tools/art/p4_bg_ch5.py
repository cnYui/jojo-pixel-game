# 第四部第5章（露伴宅 / 漫画家与猎鼠）的背景：6 张，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_ch5.json（build_p4.py 会把 _meta/bg_*.json 并进 bg.json）。
#   用法：python3 第四部/tools/art/p4_bg_ch5.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   图层 pack 一律 'ch5'（打包成 data/img_bg_ch5.js，进第5章时才加载）。
#   画面约定：高 180、ground 150、可走带 walk [142, 176]；平时对白框盖住 y 6–46，要指着说的东西放在 y 50 以下。
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import liv_floor, preview, save_layers, sky_far  # noqa: E402

PACK = 'ch5'
H = 180


# ============================================================ 通用零件
def poly(d, pts, col):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=C(col))


def kanji(im, x, y, text, col, size=12):
    """文泉驿点阵正黑 12 px（招牌、门牌）"""
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    im.paste(C(col), (int(x), int(y)), m)
    return m.width, m.height


def compose(*layers, w):
    """合成一张整图（预览用；比地图窄的远层横向拉到整宽，只是看个大概）"""
    can = Image.new('RGBA', (w, H), (0, 0, 0, 255))
    for im in layers:
        if im is None:
            continue
        can.alpha_composite(im.crop((0, 0, w, H)) if im.width >= w else im.resize((w, H), Image.NEAREST), (0, 0))
    return can


def grass_band(im, x0, x1, y0, y1, cols=('#5e8a3e', '#6e9a48', '#86b058', '#4a7232'), seed=0, density=6):
    """草地：底色 + 一簇簇短竖线（越往下越密、越亮）"""
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(im)
    rect(d, (x0, y0, x1, y1), cols[0])
    n = int((x1 - x0) * (y1 - y0) / density)
    for _ in range(n):
        x = rng.randint(x0, x1)
        y = rng.randint(y0, y1 + 1)
        k = (y - y0) / max(1, y1 - y0)
        L = 1 + int(k * 3 * rng.rand())
        c = cols[1] if rng.rand() < .55 else (cols[2] if rng.rand() < .5 + .3 * k else cols[3])
        line(d, (x, y, x, y - L), c)
    return im


def tuft(d, x, y, h=6, cols=('#3e6a2e', '#5e8a3e', '#86b058'), seed=0):
    """一丛高草：几根往两边弯的草叶"""
    rng = np.random.RandomState(seed)
    for i in range(7):
        lean = rng.uniform(-.6, .6)
        hh = h * rng.uniform(.6, 1)
        c = cols[i % 3]
        for k in range(int(hh)):
            px(d, x + i - 3 + lean * k * k / hh, y - k, c)


def rock(d, x, y, w, h, cols=('#7a7468', '#948e80', '#b0aa98', '#5a554c'), seed=0):
    """岩石：底下扁圆的暗面 + 左上亮面 + 几道裂缝"""
    rng = np.random.RandomState(seed)
    ellipse(d, (x - w / 2, y - h, x + w / 2, y + h * .25), cols[3])
    ellipse(d, (x - w / 2 + 1, y - h, x + w / 2 - 2, y), cols[0])
    ellipse(d, (x - w / 2 + 2, y - h + 1, x + w * .15, y - h * .35), cols[1])
    ellipse(d, (x - w / 2 + 4, y - h + 2, x - w * .1, y - h * .6), cols[2])
    for _ in range(max(1, int(w / 14))):
        cx = x + rng.uniform(-w * .3, w * .3)
        cy = y - h * rng.uniform(.2, .7)
        line(d, (cx, cy, cx + rng.uniform(-3, 3), cy + rng.uniform(2, 5)), cols[3])
    line(d, (x - w / 2 + 2, y, x + w / 2 - 2, y), cols[3])


def wood_wall(im, x0, x1, y0, y1, cols=('#8a6444', '#7a573a', '#9c7450', '#5e422c'), plank=7, seed=0):
    """竖板木墙：板缝、钉子、零星节疤"""
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(im)
    rect(d, (x0, y0, x1, y1), cols[0])
    for i, x in enumerate(range(x0, x1, plank)):
        if i % 3 == 1:
            rect(d, (x + 1, y0, x + plank - 1, y1), cols[1])
        line(d, (x, y0, x, y1), cols[3])
        px(d, x + 2, y0 + 3, cols[3])
        px(d, x + 2, y1 - 4, cols[3])
        line(d, (x + 1, y0, x + 1, y1), cols[2])
        for _ in range(rng.randint(0, 2)):
            ky = rng.randint(y0 + 6, max(y0 + 7, y1 - 6))
            ellipse(d, (x + 2, ky, x + 4, ky + 2), cols[3])
    return im


def bookshelf(d, x0, x1, top, base, wood=('#4a3020', '#6a4630', '#86603e'), seed=0, rows=None):
    """书架：深色木框、几层隔板、书脊颜色随机（偶尔一本斜靠、一段空位放小物）"""
    rng = np.random.RandomState(seed)
    rect(d, (x0, top, x1, base), wood[0])
    rect(d, (x0, top, x1, top + 2), wood[2])
    rows = rows or max(2, (base - top - 6) // 18)
    sh = (base - top - 6) / rows
    spines = ['#8a2a2a', '#2a4a7a', '#c8a050', '#3a6a4a', '#e8e0d0', '#5a3a6a', '#b85a3a', '#2a2a30', '#7a8a9a', '#d8c8a0']
    for r in range(rows):
        y_bot = int(top + 3 + (r + 1) * sh)
        y_top = int(top + 3 + r * sh) + 1
        rect(d, (x0 + 2, y_top, x1 - 2, y_bot - 2), mix(wood[0], '#000000', .35))
        x = x0 + 3
        while x < x1 - 4:
            if rng.rand() < .06 and x < x1 - 14:     # 空位：放个小摆件
                rect(d, (x + 2, y_bot - 6, x + 6, y_bot - 2), ['#e8e4d8', '#4a6a8a', '#c8a050'][rng.randint(3)])
                x += 10
                continue
            bw = rng.randint(2, 5)
            bh = int(sh - 3 - rng.randint(0, 5))
            c = spines[rng.randint(len(spines))]
            rect(d, (x, y_bot - 1 - bh, x + bw - 1, y_bot - 2), c)
            px(d, x, y_bot - 1 - bh, mix(c, '#ffffff', .35))
            if bh > 8 and rng.rand() < .4:
                line(d, (x, y_bot - bh + 3, x + bw - 1, y_bot - bh + 3), mix(c, '#ffffff', .45))
            x += bw
        rect(d, (x0 + 1, y_bot - 1, x1 - 1, y_bot), wood[1])
        line(d, (x0 + 1, y_bot - 1, x1 - 1, y_bot - 1), wood[2])
    line(d, (x0, top, x0, base), wood[2])
    line(d, (x1, top, x1, base), mix(wood[0], '#000000', .3))


def sky_layer(w, seed, cols=('#6aa8e8', '#8cbcf0', '#b0d4f4', '#d8eaf6'), hills=True):
    """远层：天空 + 远山 + 远处的屋顶（序章 sky_far，不要海）"""
    return sky_far(w, seed=seed, cols=cols, sea=False, hills=hills)


def far_w(W, k=.5):
    return int(math.ceil((W - 320) * k)) + 320


def manuscript(d, x, y, w=9, h=12, seed=0, tilt=0):
    """一张漫画原稿：白纸 + 几格分镜框 + 涂黑的地方"""
    rng = np.random.RandomState(seed)
    rect(d, (x, y, x + w, y + h), '#f6f2e6')
    line(d, (x, y + h + 1, x + w, y + h + 1), '#b8b0a0')
    line(d, (x + 1, y + 1, x + w - 1, y + 1), '#4a4a50')
    line(d, (x + 1, y + h - 1, x + w - 1, y + h - 1), '#4a4a50')
    line(d, (x + 1, y + 1, x + 1, y + h - 1), '#4a4a50')
    line(d, (x + w - 1, y + 1, x + w - 1, y + h - 1), '#4a4a50')
    sy = y + 2 + rng.randint(2, max(3, h - 5))
    line(d, (x + 1, sy, x + w - 1, sy), '#4a4a50')
    if w > 6:
        sx = x + 2 + rng.randint(1, w - 4)
        line(d, (sx, y + 1, sx, sy), '#4a4a50')
    for _ in range(2):
        px(d, x + rng.randint(2, w - 1), y + rng.randint(2, h - 1), '#2a2a30')


# ============================================================ 露伴宅外观 rohan_house（480 宽，白天）
#   左：邻家的树 → 院墙（石砌矮墙 + 铁栏杆）后面是两层洋馆：石板灰蓝屋顶、中间山墙（圆窗）、
#   一楼左边凸窗、正中带两根柱子的门廊和双开门、右边一扇推拉窗（亿泰翻进去的那扇，能开：key 'window'）；
#   二楼一排窗，右边是工作室的大凸窗（第11章修缮版在这张上加脚手架）。院墙正中是铁门 + 门柱 + 门牌「岸辺」+ 信箱。
#   人站在院墙外的人行道 / 马路上。
RH = dict(wall='#ece4d0', wall2='#d6ccb4', wall3='#c4b89e', trim='#4a5a54', trim2='#32403c', roof='#3c4658', roof2='#2c3444',
          roof3='#56627a', roof4='#1e2430', stone='#a8a090', stone2='#8e8676', stone3='#c4bcaa', iron='#2a2c30', iron2='#4a4e56')
RH_WIN = (304, 92, 330, 118)       # 一楼右边那扇推拉窗（亿泰翻窗）的框
RH_STUDY = (290, 46, 346, 80)      # 二楼工作室凸窗的框（第11章脚手架对这里）


def rh_window(d, box, glass=('#86aac4', '#b8d2e2'), curtain='#f2ecdc', arch=False, open_=False):
    """洋馆的窗：白框 + 十字窗棂 + 窗台；open_ = 下半扇推上去，里面黑、窗帘往外飘"""
    P = RH
    x0, y0, x1, y1 = box
    rect(d, (x0 - 2, y0 - 2, x1 + 2, y1 + 1), P['trim'])
    rect(d, (x0, y0, x1, y1), '#f4f0e6')
    gx0, gy0, gx1, gy1 = x0 + 2, y0 + 2, x1 - 2, y1 - 2
    if open_:
        my = (gy0 + gy1) // 2
        rect(d, (gx0, gy0, gx1, my - 1), glass[0])                      # 上半扇（推上去的那扇叠在这里）
        line(d, (gx0, my - 1, gx1, my - 1), '#f4f0e6')
        line(d, (gx0, my - 2, gx1, my - 2), '#d8d2c4')
        rect(d, (gx0, my, gx1, gy1), '#2a2226')                          # 屋里黑
        rect(d, (gx0, my, gx0 + 3, gy1), '#3a3036')
        for k in range(gy1 - my):                                         # 窗帘从窗口飘出来一角
            px(d, gx1 - 3 - int(2 * math.sin(k / 3)), my + k, curtain)
            px(d, gx1 - 2 - int(2 * math.sin(k / 3)), my + k, curtain)
        line(d, (gx0, gy1, gx1, gy1), '#4a4046')
    else:
        rect(d, (gx0, gy0, gx1, gy1), glass[0])
        for i in range(0, gx1 - gx0, 6):
            line(d, (gx0 + i, gy0, min(gx1, gx0 + i + 4), gy0 + 4), glass[1])
        rect(d, (gx0, gy0, gx0 + 3, gy1), curtain)
        rect(d, (gx1 - 3, gy0, gx1, gy1), curtain)
        line(d, ((x0 + x1) // 2, y0, (x0 + x1) // 2, y1), '#f4f0e6')
        line(d, (x0, (y0 + y1) // 2, x1, (y0 + y1) // 2), '#f4f0e6')
    rect(d, (x0 - 3, y1 + 1, x1 + 3, y1 + 3), P['wall3'])                 # 窗台
    line(d, (x0 - 3, y1 + 1, x1 + 3, y1 + 1), '#f4f0e6')
    if arch:
        d.pieslice((x0 - 2, y0 - 9, x1 + 2, y0 + 7), 180, 360, fill=C(P['trim']))
        d.pieslice((x0, y0 - 7, x1, y0 + 5), 180, 360, fill=C('#f4f0e6'))
        d.pieslice((x0 + 2, y0 - 5, x1 - 2, y0 + 3), 180, 360, fill=C(glass[0]))


def rh_shutters(d, box):
    x0, y0, x1, y1 = box
    for sx in (x0 - 9, x1 + 3):
        rect(d, (sx, y0 - 1, sx + 5, y1), RH['trim'])
        for yy in range(y0 + 1, y1, 3):
            line(d, (sx + 1, yy, sx + 4, yy), RH['trim2'])


def rh_roof(im, x0, x1, top, base, overhang=6):
    P = RH
    d = ImageDraw.Draw(im)
    h = base - top
    for i in range(h + 1):
        k = i / max(1, h)
        xa, xb = x0 - overhang * k + (1 - k) * 18, x1 + overhang * k - (1 - k) * 18
        line(d, (xa, top + i, xb, top + i), P['roof'] if i % 4 else P['roof2'])
        if i % 4 == 2:                                                    # 石板瓦的错缝
            for x in range(int(xa) + (i // 4 % 2) * 4, int(xb), 8):
                px(d, x, top + i, P['roof2'])
    line(d, (x0 + 18, top, x1 - 18, top), P['roof3'])
    rect(d, (x0 - overhang, base + 1, x1 + overhang, base + 3), P['trim2'])
    line(d, (x0 - overhang, base + 1, x1 + overhang, base + 1), P['trim'])


def rh_house(im):
    P = RH
    d = ImageDraw.Draw(im)
    X0, X1, B = 64, 416, 128                 # 房子左右、墙脚
    F2 = 84                                  # 二楼楼板线
    # 烟囱（屋顶后面）
    rect(d, (352, 10, 366, 30), '#8a5a48')
    rect(d, (350, 8, 368, 11), '#6a4434')
    for yy in range(13, 30, 4):
        line(d, (352, yy, 366, yy), '#7a4e3e')
    rh_roof(im, X0, X1, 18, 40)
    d = ImageDraw.Draw(im)
    # 墙：横向护墙板（细横线）
    rect(d, (X0, 41, X1, B), P['wall'])
    for yy in range(44, B, 3):
        line(d, (X0, yy, X1, yy), P['wall2'] if yy % 6 else mix(P['wall'], P['wall2'], .5))
    rect(d, (X0, 41, X0 + 3, B), P['trim'])
    rect(d, (X1 - 3, 41, X1, B), P['trim'])
    rect(d, (X0, F2, X1, F2 + 2), P['trim'])
    line(d, (X0, F2 + 3, X1, F2 + 3), P['wall3'])
    rect(d, (X0 - 2, B - 6, X1 + 2, B), P['stone'])                      # 石砌墙基
    for x in range(X0, X1, 9):
        line(d, (x, B - 6, x, B), P['stone2'])
    line(d, (X0 - 2, B - 6, X1 + 2, B - 6), P['stone3'])
    # 正中山墙（比主屋顶高一截）+ 圆窗
    cx = 240
    for i in range(34):
        line(d, (cx - 4 - i * 1.5, 12 + i, cx + 4 + i * 1.5, 12 + i), P['roof'] if i % 4 else P['roof2'])
    for i in range(26):
        line(d, (cx - i * 1.5 + 2, 20 + i, cx + i * 1.5 - 2, 20 + i), P['wall'])
    line(d, (cx - 51, 46, cx + 51, 46), P['trim2'])
    ellipse(d, (cx - 7, 28, cx + 7, 42), P['trim'])
    ellipse(d, (cx - 5, 30, cx + 5, 40), '#f4f0e6')
    ellipse(d, (cx - 4, 31, cx + 4, 39), '#86aac4')
    line(d, (cx, 30, cx, 40), '#f4f0e6')
    line(d, (cx - 5, 35, cx + 5, 35), '#f4f0e6')
    # 二楼的窗
    for x in (96, 150, 196, 254):
        if x in (196, 254):
            x += 0
        rh_window(d, (x, 52, x + 18, 76))
    rh_shutters(d, (96, 52, 114, 76))
    rh_shutters(d, (150, 52, 168, 76))
    # 工作室凸窗（二楼右）：往外凸的箱子 + 三扇窗 + 小屋顶
    sx0, sy0, sx1, sy1 = RH_STUDY
    rect(d, (sx0 - 4, sy0 - 2, sx1 + 4, sy1 + 4), P['wall2'])
    for i in range(6):
        line(d, (sx0 - 6 + i, sy0 - 8 + i, sx1 + 6 - i, sy0 - 8 + i), P['roof'] if i % 3 else P['roof2'])
    line(d, (sx0 - 6, sy0 - 8, sx1 + 6, sy0 - 8), P['roof3'])
    for k in range(3):
        wx0 = sx0 + 1 + k * 19
        rh_window(d, (wx0, sy0 + 2, wx0 + 16, sy1 - 2), curtain='#e4dcc8')
    rect(d, (sx0 - 4, sy1 + 1, sx1 + 4, sy1 + 4), P['trim'])
    for x in range(sx0, sx1 + 1, 8):                                       # 凸窗下的托架
        poly(d, [(x, sy1 + 4), (x + 4, sy1 + 4), (x + 2, sy1 + 9)], P['trim2'])
    rh_window(d, (372, 52, 390, 76))
    rh_shutters(d, (372, 52, 390, 76))
    # 一楼：左凸窗、门廊、右窗
    bx0, bx1 = 92, 168
    rect(d, (bx0 - 4, 92, bx1 + 4, B - 6), P['wall2'])
    for i in range(5):
        line(d, (bx0 - 6 + i, 86 + i, bx1 + 6 - i, 86 + i), P['roof'] if i % 3 else P['roof2'])
    for k in range(3):
        wx0 = bx0 + k * 26
        rh_window(d, (wx0, 96, wx0 + 22, 118), curtain='#e8d8c0')
    # 门廊：台阶、两根白柱、小三角檐、双开门
    px0, px1 = 214, 266
    poly(d, [(px0 - 8, 90), (cx, 76), (px1 + 8, 90)], P['roof'])
    poly(d, [(px0 - 2, 89), (cx, 80), (px1 + 2, 89)], P['wall'])
    line(d, (px0 - 8, 90, px1 + 8, 90), P['trim2'])
    rect(d, (px0 - 6, 91, px1 + 6, 93), P['trim'])
    for colx in (px0, px1 - 5):
        rect(d, (colx, 93, colx + 5, B - 6), '#f4f0e6')
        line(d, (colx + 4, 93, colx + 4, B - 6), '#d8d2c4')
        rect(d, (colx - 1, 93, colx + 6, 95), '#e0dace')
        rect(d, (colx - 1, B - 9, colx + 6, B - 6), '#e0dace')
    rect(d, (226, 96, 254, B - 6), P['trim2'])
    rect(d, (228, 98, 239, B - 6), '#6a4a34')
    rect(d, (241, 98, 252, B - 6), '#6a4a34')
    for dx in (228, 241):
        rect(d, (dx + 2, 101, dx + 9, 110), '#7e5a40')
        bevel(d, (dx + 2, 101, dx + 9, 110), '#8e6a4c', '#4e3424')
        rect(d, (dx + 2, 113, dx + 9, B - 9), '#7e5a40')
        bevel(d, (dx + 2, 113, dx + 9, B - 9), '#8e6a4c', '#4e3424')
    px(d, 238, 112, '#e8c860')
    px(d, 242, 112, '#e8c860')
    rect(d, (236, 92, 244, 95), '#f8e8a8')                                # 门灯
    for k in range(3):                                                    # 台阶
        rect(d, (px0 - 2 - k * 3, B - 6 + k * 2, px1 + 2 + k * 3, B - 4 + k * 2), ['#d4ccba', '#c4bcaa', '#b4ac9a'][k])
    rh_window(d, RH_WIN)
    rh_shutters(d, RH_WIN)
    rh_window(d, (372, 96, 390, 118))
    rh_shutters(d, (372, 96, 390, 118))
    # 墙上的爬山虎（左下角）
    rng = np.random.RandomState(7)
    for _ in range(140):
        x = X0 + 2 + int(abs(rng.normal(0, 12)))
        y = B - 6 - int(abs(rng.normal(0, 30)))
        if y > 41:
            px(d, x, y, ['#4a7a3e', '#5e8e48', '#3a6a32'][rng.randint(3)])
    return im


def rh_fence(im, gx0=212, gx1=268):
    """院墙：石砌矮墙 + 黑铁栏杆（尖头），中间门柱 + 铁门、门牌、信箱"""
    P = RH
    d = ImageDraw.Draw(im)
    W = im.width
    T, B = 128, 146
    for x0, x1 in ((0, gx0 - 18), (gx1 + 18, W)):
        rect(d, (x0, T + 4, x1, B), P['stone'])
        rect(d, (x0, T + 2, x1, T + 4), P['stone3'])
        line(d, (x0, T + 5, x1, T + 5), P['stone2'])
        for i, y in enumerate(range(T + 6, B, 5)):
            line(d, (x0, y + 4, x1, y + 4), P['stone2'])
            for x in range(x0 + (i % 2) * 6, x1, 12):
                line(d, (x, y, x, y + 4), P['stone2'])
        # 铁栏杆
        line(d, (x0, 112, x1, 112), P['iron'])
        line(d, (x0, 124, x1, 124), P['iron'])
        for x in range(x0 + 2, x1, 5):
            line(d, (x, 108, x, T + 1), P['iron'])
            px(d, x, 107, P['iron2'])
            px(d, x - 1, 109, P['iron'])
            px(d, x + 1, 109, P['iron'])
        for x in range(x0 + 4, x1, 20):                                    # 栏杆中段的小花饰
            ellipse(d, (x - 2, 116, x + 2, 120), P['iron2'])
            ellipse(d, (x - 1, 117, x + 1, 119), P['stone3'])
    # 门柱
    for x0 in (gx0 - 18, gx1 + 2):
        rect(d, (x0, 100, x0 + 16, B), P['stone3'])
        for y in range(104, B, 6):
            line(d, (x0, y, x0 + 16, y), P['stone'])
        rect(d, (x0 - 1, 97, x0 + 17, 100), P['stone2'])
        ellipse(d, (x0 + 4, 89, x0 + 12, 97), '#f4f0e0')                  # 门柱灯
        line(d, (x0 + 6, 90, x0 + 10, 90), '#ffffff')
        line(d, (x0 + 16, 100, x0 + 16, B), P['stone2'])
    # 门牌（左门柱，竖写「岸辺」）+ 信箱（右门柱）
    rect(d, (gx0 - 16, 103, gx0 - 3, 131), '#ece4d0')
    bevel(d, (gx0 - 16, 103, gx0 - 3, 131), '#fbf8ee', '#a8a090')
    for i, ch in enumerate('岸辺'):
        kanji(im, gx0 - 16, 104 + i * 13, ch, '#2a2a30')
    d = ImageDraw.Draw(im)
    rect(d, (gx1 + 5, 110, gx1 + 15, 120), '#7a2a24')
    line(d, (gx1 + 6, 113, gx1 + 14, 113), '#2a1a18')
    line(d, (gx1 + 5, 110, gx1 + 15, 110), '#9a3a30')
    # 铁门（两扇，关着）
    for x in range(gx0 - 2, gx1 + 2, 4):
        top = 104 + int(6 * abs(math.sin((x - gx0) / (gx1 - gx0) * math.pi)) * -1 + 6)
        line(d, (x, top, x, B - 2), P['iron'])
        px(d, x, top - 1, P['iron2'])
    for y in (112, 126, 140):
        line(d, (gx0 - 2, y, gx1 + 2, y), P['iron'])
    line(d, ((gx0 + gx1) // 2, 104, (gx0 + gx1) // 2, B - 2), P['iron2'])
    for x in range(gx0 + 4, gx1 - 2, 8):                                 # 门上沿的一排小尖
        px(d, x, 103, P['iron2'])
    return im


def rh_open_window():
    """亿泰翻窗：一楼右窗开着（只是那一块）"""
    x0, y0, x1, y1 = RH_WIN
    im = new(x1 - x0 + 7, y1 - y0 + 8)
    d = ImageDraw.Draw(im)
    rh_window(d, (3, 2, 3 + x1 - x0, 2 + y1 - y0), open_=True)
    return im, x0 - 3, y0 - 2


def rohan_house_layers():
    """露伴宅外观的各层（不存盘）：返回 (far, near, window_open, (wx, wy))。
    别章的变体（第11章修缮版加脚手架）import 这个函数，叠上自己的东西另存成自己 pack 的新 key"""
    W = 480
    fw = far_w(W)
    far = sky_layer(fw, seed=51)
    near = new(W, H)
    d = ImageDraw.Draw(near)
    # 院子里的草和树篱（房子和院墙中间）
    rect(d, (0, 120, W, 132), '#5e8a3e')
    hedge(near, 0, 64, 92, 132, seed=52)
    hedge(near, 416, W, 96, 132, seed=53)
    # 左右两棵树（邻家的，挡住房子边）
    pal = dict(d='#2e5e3a', m='#4a7c48', l='#6e9e5a', x='#a8cc7a', trunk='#5a4234', trunk2='#3e2c22')
    near = sakura(near, 28, 132, 118, 72, seed=54, pal=pal, petals=False)
    near = rh_house(near)
    near = sakura(near, 452, 132, 112, 66, seed=55, pal=pal, petals=False)
    d = ImageDraw.Draw(near)
    hedge(near, 170, 206, 116, 130, seed=56)
    hedge(near, 274, 300, 118, 130, seed=57)
    # 门口的石板小路（门廊台阶 → 铁门）
    for i, y in enumerate(range(130, 146, 4)):
        rect(d, (224 - i, y, 256 + i, y + 2), '#c8c0ae')
        line(d, (240, y, 240, y + 2), '#a8a090')
    near = rh_fence(near)
    d = ImageDraw.Draw(near)
    # 人行道 + 马路
    near = sidewalk(near, 0, W, 146, 164)
    near = asphalt(near, 0, W, 164, H, dash=False)
    d = ImageDraw.Draw(near)
    pole(near, 132, 160, 150)
    d = ImageDraw.Draw(near)
    wires(near, [(132, 14), (480, 22)], sag=6)
    wires(near, [(0, 26), (132, 18)], sag=4)
    win, wx, wy = rh_open_window()
    return far, near, win, (wx, wy)


def rohan_house():
    W = 480
    far, near, win, (wx, wy) = rohan_house_layers()
    layers = {'far': far, 'near': near, 'window_open': win}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(gate=[240, 148], gate_in=[240, 140], porch=[240, 128], nameplate=[202, 117], mailbox=[280, 115],
                             climb_window=[(RH_WIN[0] + RH_WIN[2]) // 2, 146], climb_window_box=list(RH_WIN),
                             study_window=[(RH_STUDY[0] + RH_STUDY[2]) // 2, (RH_STUDY[1] + RH_STUDY[3]) // 2],
                             study_window_box=list(RH_STUDY), house_box=[64, 8, 416, 128], pole=[132, 148], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/rohan_house/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/rohan_house/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/rohan_house/window_open', 'k': 1, 'x': wx, 'y': wy, 'key': 'window'},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    preview('rohan_house', {'a': compose(far, near, w=W)}, ['a'], W)
    pv = compose(far, near, w=W)
    pv.alpha_composite(win, (wx, wy))
    preview('rohan_house_window', {'a': pv}, ['a'], W)
    save_layers('rohan_house', layers, meta)
    return meta



# ============================================================ 露伴的工作室 rohan_studio（480 宽，白天，第 7 战）
#   左：通走廊的门 → 两架画集书架 → 正中两扇高窗，窗下是画桌（斜放的画板、台灯、笔筒、墨水瓶、网点纸）和转椅 →
#   软木板上钉着原稿和分镜 → 原稿柜（上面一摞摞原稿）→ 石膏像 + 挂画。木地板，窗光斜照在地上。
#   开关层：'pages' = 地上撒满原稿（撒原稿那一招 / 打完以后）；'hole' = 右墙被打穿一个洞、地上有碎块（打完以后）。
RS = dict(wall='#efe9dc', wall2='#e2dacb', wall3='#d4cbb8', beam='#4e3626', beam2='#6a4a34', wain='#5e4230', wain_in='#54392a',
          wain_hi='#7a5840', wain_lo='#3e2a1e')


def rs_room():
    W, G = 480, 134
    P = RS
    im = new(W, H, P['wall'])
    d = ImageDraw.Draw(im)
    # 灰泥墙：零星的斑点 + 顶上一圈阴影 + 天花板的木梁
    noise_specks(im, (0, 10, W, G), [P['wall2'], P['wall3']], 900, seed=61)
    im = grad(im, (0, 10, W, 28), (P['wall3'], P['wall2'], P['wall']))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 9), P['beam'])
    line(d, (0, 9, W, 9), P['beam2'])
    for x in range(0, W, 96):
        rect(d, (x, 0, x + 6, 12), P['beam'])
        line(d, (x, 12, x + 6, 12), P['beam2'])
    # 护墙板（y 108–134）
    WT = 108
    rect(d, (0, WT, W, G), P['wain'])
    rect(d, (0, WT, W, WT + 2), P['wain_hi'])
    line(d, (0, WT + 3, W, WT + 3), P['wain_lo'])
    for x in range(2, W, 24):
        rect(d, (x + 2, WT + 7, x + 20, G - 7), P['wain_in'])
        bevel(d, (x + 2, WT + 7, x + 20, G - 7), P['wain_lo'], P['wain_hi'])
    rect(d, (0, G - 4, W, G), P['beam'])
    line(d, (0, G - 4, W, G - 4), P['beam2'])
    # ---------------- 门（6–40）
    dx0, dx1, dy0 = 8, 40, G - 80
    rect(d, (dx0 - 4, dy0 - 4, dx1 + 4, G), P['beam'])
    line(d, (dx0 - 4, dy0 - 4, dx1 + 4, dy0 - 4), P['beam2'])
    rect(d, (dx0, dy0, dx1, G - 1), '#6e4a32')
    for yy in (dy0 + 4, dy0 + 40):
        rect(d, (dx0 + 4, yy, dx1 - 4, yy + 32), '#5e3e2a')
        bevel(d, (dx0 + 4, yy, dx1 - 4, yy + 32), '#82583c', '#3e2a1e')
    rect(d, (dx1 - 6, dy0 + 38, dx1 - 3, dy0 + 40), '#d8c070')
    # ---------------- 两架画集书架（48–150）
    for x0 in (48, 100):
        bookshelf(d, x0, x0 + 48, 22, G - 1, seed=x0)
    # ---------------- 正中两扇高窗（168–296）+ 窗帘
    for wx0 in (170, 238):
        wx1 = wx0 + 56
        rect(d, (wx0 - 3, 24, wx1 + 3, 104), P['beam2'])
        im = grad(im, (wx0, 27, wx1, 101), ('#7ab4e4', '#a8d0f0', '#d4e8f6'))
        d = ImageDraw.Draw(im)
        for k in range(3):                                                # 窗外的树梢
            ellipse(d, (wx0 + k * 20 - 4, 74 - k * 6, wx0 + k * 20 + 22, 104), ['#5e8e48', '#6e9e58', '#4a7a3e'][k])
        cloud(im, wx0 + 8, 44, 30, seed=wx0)
        d = ImageDraw.Draw(im)
        rect(d, (wx0, 101, wx1, 104), P['beam2'])
        line(d, ((wx0 + wx1) // 2, 27, (wx0 + wx1) // 2, 101), '#f4f0e6')
        for yy in (50, 76):
            line(d, (wx0, yy, wx1, yy), '#f4f0e6')
        for k in range(0, wx1 - wx0, 7):
            line(d, (wx0 + k, 27, min(wx1, wx0 + k + 5), 32), '#e4f0fa')
        for cx, sgn in ((wx0 - 6, 1), (wx1 - 2, -1)):                    # 窗帘（收在两边，墨绿）
            rect(d, (cx, 22, cx + 8, 106), '#3a5a4a')
            for yy in range(24, 106, 4):
                px(d, cx + 2, yy, '#2a4a3a')
                px(d, cx + 6, yy + 2, '#4a6e5a')
    rect(d, (160, 18, 306, 21), P['beam2'])                               # 窗帘杆
    # ---------------- 画桌（184–284）：斜画板、台灯、笔筒、墨水瓶、原稿
    tx0, tx1, ty = 182, 286, 112
    rect(d, (tx0, ty, tx1, ty + 3), '#7a5434')
    line(d, (tx0, ty, tx1, ty), '#9a7048')
    rect(d, (tx0 + 2, ty + 4, tx0 + 6, G + 8), '#5a3e28')
    rect(d, (tx1 - 6, ty + 4, tx1 - 2, G + 8), '#5a3e28')
    rect(d, (tx1 - 34, ty + 4, tx1 - 7, ty + 26), '#6a4a30')              # 抽屉
    for yy in (ty + 6, ty + 16):
        bevel(d, (tx1 - 32, yy, tx1 - 9, yy + 8), '#82603e', '#4a3220')
        rect(d, (tx1 - 23, yy + 4, tx1 - 18, yy + 5), '#d8c070')
    poly(d, [(206, ty), (262, ty), (256, ty - 22), (212, ty - 22)], '#d8d0bc')   # 斜画板
    poly(d, [(208, ty - 1), (260, ty - 1), (255, ty - 20), (213, ty - 20)], '#f8f4ea')
    manuscript(d, 220, ty - 18, 13, 15, seed=3)
    manuscript(d, 236, ty - 17, 13, 15, seed=4)
    line(d, (206, ty, 262, ty), '#8a7a5a')
    line(d, (244, ty - 12, 252, ty - 4), '#2a2a30')                       # 笔
    # 台灯（左边，弯臂）
    rect(d, (190, ty - 3, 198, ty - 1), '#2e3a34')
    line(d, (194, ty - 3, 190, ty - 22), '#2e3a34')
    line(d, (190, ty - 22, 202, ty - 32), '#2e3a34')
    poly(d, [(200, ty - 36), (210, ty - 30), (206, ty - 26), (198, ty - 31)], '#2e5a46')
    px(d, 206, ty - 27, '#fff4c8')
    # 笔筒、墨水瓶、网点纸
    rect(d, (268, ty - 9, 274, ty - 1), '#8a3a2e')
    for k, c in enumerate(('#2a2a30', '#c8a050', '#2a4a7a', '#2a2a30')):
        line(d, (269 + k, ty - 9, 268 + k * 2 - 1, ty - 15 + k % 2), c)
    for k, (bx, c) in enumerate(((278, '#1e1e24'), (190 - 6, '#1e1e24'))):
        rect(d, (bx, ty - 5, bx + 4, ty - 1), c)
        rect(d, (bx + 1, ty - 7, bx + 3, ty - 5), '#5a4a3a')
        px(d, bx + 1, ty - 4, '#5a5a66')
    rect(d, (264, ty - 2, 276, ty - 1), '#bcbcc4')
    # 转椅（画桌前，背对镜头一点）
    rect(d, (226, 104, 246, 128), '#3a3a42')
    rect(d, (228, 106, 244, 126), '#4a4a54')
    line(d, (228, 106, 244, 106), '#5e5e6a')
    rect(d, (222, 128, 250, 132), '#3a3a42')
    rect(d, (234, 132, 238, 140), '#5a5a62')
    for fx in (222, 236, 250):
        line(d, (236, 140, fx, 144), '#3a3a42')
        px(d, fx, 145, '#2a2a30')
    # ---------------- 软木板（306–366）：钉着原稿、分镜、照片
    rect(d, (304, 44, 368, 96), P['beam2'])
    rect(d, (306, 46, 366, 94), '#c49a64')
    noise_specks(im, (306, 46, 366, 94), ['#b08654', '#d4aa74'], 160, seed=62)
    d = ImageDraw.Draw(im)
    for k, (mx, my) in enumerate(((310, 50), (324, 52), (338, 49), (352, 51), (312, 72), (328, 73), (346, 70))):
        manuscript(d, mx, my, 11, 15, seed=10 + k)
        px(d, mx + 5, my + 1, ['#e83a3a', '#3a6ae8', '#e8c83a'][k % 3])
    rect(d, (356, 76, 364, 86), '#d8e0e8')                                # 照片
    rect(d, (357, 77, 363, 82), '#6a8aa8')
    px(d, 360, 76, '#e83a3a')
    # ---------------- 原稿柜（372–420）+ 上面一摞摞原稿
    cx0, cx1, ct = 372, 420, 98
    rect(d, (cx0, ct, cx1, G - 1), '#6a4a30')
    rect(d, (cx0 - 2, ct - 3, cx1 + 2, ct), '#86603e')
    for k in range(4):
        yy = ct + 3 + k * 8
        bevel(d, (cx0 + 3, yy, cx1 - 3, yy + 6), '#86603e', '#4a3220')
        rect(d, (cx0 + 22, yy + 3, cx0 + 26, yy + 3), '#d8c070')
    for k, sx in enumerate((cx0 + 2, cx0 + 18, cx0 + 33)):
        hh = [10, 6, 14][k]
        for j in range(hh):
            line(d, (sx, ct - 4 - j, sx + 12, ct - 4 - j), '#f4f0e6' if j % 3 else '#d8d2c4')
    # ---------------- 石膏像（台座上）+ 挂画（424–476）
    rect(d, (436, 104, 460, G - 1), '#d8d2c4')
    rect(d, (434, 102, 462, 105), '#ece6da')
    line(d, (459, 105, 459, G - 1), '#b8b2a4')
    ellipse(d, (440, 70, 456, 90), '#f2eee4')                             # 头
    rect(d, (444, 88, 452, 96), '#e6e0d4')
    poly(d, [(436, 102), (460, 102), (456, 94), (440, 94)], '#ece8dc')
    ellipse(d, (448, 72, 456, 88), '#d8d2c4')
    px(d, 445, 78, '#b8b2a4')
    rect(d, (428, 30, 470, 62), '#8a6a3a')                                # 挂画（远山）
    rect(d, (431, 33, 467, 59), '#a8c4d4')
    poly(d, [(431, 59), (444, 42), (456, 52), (467, 44), (467, 59)], '#6a8a6a')
    poly(d, [(431, 59), (450, 50), (467, 59)], '#4e6e52')
    bevel(d, (428, 30, 470, 62), '#b08a50', '#5a4228')
    return im, G


def rs_glow(G):
    """窗光：从两扇窗斜照到地板上的两块光（lighter 叠加）"""
    W = 480
    f = np.zeros((H, W))
    for wx0 in (170, 238):
        for y in range(G + 2, H):
            k = (y - G) / (H - G)
            xa = wx0 + 24 + k * 34
            xb = wx0 + 56 + 10 + k * 46
            f[y, int(xa):int(min(W, xb))] = .55 - .25 * k
    bay = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
    fq = np.clip(np.floor(f * 4 + bay) / 4, 0, 1)
    a = np.zeros((H, W, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * np.array((110, 86, 40), float), 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def rs_pages(G):
    """地上撒满原稿（开关层 'pages'）"""
    W = 480
    im = new(W, H)
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(63)
    for k in range(46):
        y = rng.randint(G + 4, H - 6)
        x = rng.randint(30, W - 20)
        k2 = (y - G) / (H - G)
        w, h = int(9 + 6 * k2), int(4 + 3 * k2)                           # 平躺在地上：扁
        x1 = x + w
        sk = rng.randint(-2, 3)
        poly(d, [(x, y), (x1, y + sk), (x1 + 2, y + h + sk), (x + 2, y + h)], '#f6f2e6')
        line(d, (x + 2, y + h + 1, x1 + 2, y + h + sk + 1), '#b8ac94')
        line(d, (x + 2, y + 1, x1 - 1, y + 1 + sk), '#5a5a62')
        if rng.rand() < .7:
            line(d, (x + 3, y + h // 2 + 1, x1 - 2, y + h // 2 + 1 + sk), '#7a7a82')
        if rng.rand() < .5:
            rect(d, (x + 4, y + 2, x + 6, y + 3), '#2a2a30')
    return im


def rs_hole(G):
    """右墙被打穿：参差的洞口、露出的木骨架和隔壁的暗处，地上一堆灰泥碎块（开关层 'hole'）"""
    W = 480
    im = new(W, H)
    d = ImageDraw.Draw(im)
    cx, cy = 398, 66
    rng = np.random.RandomState(64)
    pts = []
    for i in range(18):
        a = i / 18 * 2 * math.pi
        r = 16 + rng.uniform(-4, 5)
        pts.append((cx + r * 1.05 * math.cos(a), cy + r * .95 * math.sin(a)))
    poly(d, [(x + 3 * math.cos(i), y + 3 * math.sin(i)) for i, (x, y) in enumerate(pts)], '#c4bba8')   # 墙皮剥落的一圈
    poly(d, pts, '#2a2026')
    for x in range(cx - 14, cx + 15, 9):                                  # 墙里的木龙骨
        line(d, (x, cy - 14, x, cy + 14), '#6a4a30')
        line(d, (x + 1, cy - 14, x + 1, cy + 14), '#4a3220')
    poly(d, [(cx - 8, cy - 6), (cx + 6, cy - 10), (cx + 12, cy + 4), (cx - 2, cy + 10)], '#3a2e34')
    for i, (x, y) in enumerate(pts):                                      # 裂纹往外伸
        if i % 3 == 0:
            a = math.atan2(y - cy, x - cx)
            line(d, (x, y, x + 10 * math.cos(a) + rng.uniform(-3, 3), y + 10 * math.sin(a) + rng.uniform(-3, 3)), '#a8a090')
    for _ in range(26):                                                   # 地上的碎块
        x = cx + rng.normal(0, 18)
        y = G + 3 + abs(rng.normal(0, 4))
        s = rng.randint(1, 4)
        rect(d, (x, y, x + s, y + s - 1), ['#d8d0bc', '#bcb2a0', '#efe9dc'][rng.randint(3)])
    for _ in range(40):
        px(d, cx + rng.normal(0, 26), G + 2 + abs(rng.normal(0, 6)), '#c8c0ac')
    return im


def rohan_studio():
    W = 480
    room, G = rs_room()
    room = liv_floor(room, 0, W, G)
    d = ImageDraw.Draw(room)
    # 画桌、椅子的腿压在地板上（地板画完再补一遍阴影）
    room = dither_fill(room, (180, G, 290, G + 8), '#7e5a3a', '#94704a', .5)
    d = ImageDraw.Draw(room)
    rect(d, (184, G, 188, G + 8), '#5a3e28')
    rect(d, (280, G, 284, G + 8), '#5a3e28')
    for fx in (222, 236, 250):
        line(d, (236, 140, fx, 144), '#3a3a42')
    rect(d, (234, 132, 238, 140), '#5a5a62')
    for fx in (222, 236, 250):
        px(d, fx, 145, '#2a2a30')
    glow = rs_glow(G)
    pages = rs_pages(G)
    hole = rs_hole(G)
    layers = {'room': room, 'glow': glow, 'pages': pages, 'hole': hole}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(door=[24, 148], door_in=[24, 140], shelves=[98, 146], window_l=[198, 64], window_r=[266, 64],
                             desk=[234, 146], chair=[236, 146], lamp=[200, 80], board=[336, 70], cabinet=[396, 146],
                             manuscripts=[396, 92], bust=[448, 146], painting=[449, 46], hole=[398, 66], rubble=[400, 140],
                             walk_x=[44, 472]),
                layers=[{'type': 'pano', 'image': 'bg/rohan_studio/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/rohan_studio/hole', 'k': 1, 'x': 0, 'y': 0, 'key': 'hole'},
                        {'type': 'glow', 'image': 'bg/rohan_studio/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.03},
                        {'type': 'image', 'image': 'bg/rohan_studio/pages', 'k': 1, 'x': 0, 'y': 0, 'key': 'pages'},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.14, 'key': 'pm'}],
                fg=[])
    pv = room.copy()
    pv = Image.fromarray(np.clip(np.array(pv).astype(int) + np.array(glow).astype(int) * (np.array(glow)[..., 3:] > 0), 0, 255).astype(np.uint8))
    pv.putalpha(255)
    preview('rohan_studio', {'a': pv}, ['a'], W)
    pv2 = pv.copy()
    pv2.alpha_composite(hole)
    pv2.alpha_composite(pages)
    preview('rohan_studio_after', {'a': pv2}, ['a'], W)
    save_layers('rohan_studio', layers, meta)
    return meta



# ============================================================ 田间水渠 irrigation_ditch（640 宽，白天，追踪）
#   远：天空、远山、一片片水田、农舍和电线杆。近：后岸的草 → 水泥水渠（水在流）→ 人走的土路 → 前面的草。
#   左边一座小水闸（手轮），中间一块水泥板小桥，右边后岸的挡土墙上开着排水口（圆管，往渠里淌水）。
#   土路上有老鼠的小脚印（从桥一直到排水口）、承太郎放的捕鼠笼和三脚架上的摄像机。
ID_TOP, ID_WATER, ID_BOT = 120, 128, 138       # 渠的后沿、水面、前沿


def id_far(w):
    im = sky_layer(w, seed=71, hills=True)
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(72)
    # 水田：一格格的，田埂浅色，远处的格子扁
    rect(d, (0, 112, w, 180), '#6e9a4e')
    for row, (y0, y1) in enumerate(((112, 117), (117, 124), (124, 134), (134, 180))):
        x = -rng.randint(0, 30)
        while x < w:
            cw = rng.randint(40, 90)
            c = ['#6e9a4e', '#7ea85a', '#86b062', '#78a056'][rng.randint(4)]
            rect(d, (x, y0, x + cw, y1), c)
            if row > 0:
                for yy in range(y0 + 1, y1, 2):
                    for xx in range(x + 1, x + cw, 3):
                        px(d, xx, yy, mix(c, '#4a7232', .4))
            line(d, (x, y0, x, y1), '#a8a070')
            x += cw
        line(d, (0, y0, w, y0), '#b0a878')
    # 杂木林、农舍、电线杆
    for i in range(int(w / 26)):
        x = rng.randint(-10, w)
        r = rng.randint(6, 12)
        ellipse(d, (x - r, 112 - r * 1.4, x + r, 114), ['#3e6a3e', '#4a7848', '#36603a'][rng.randint(3)])
    for x in (60, 210, 340):
        rect(d, (x, 100, x + 22, 113), '#e4dccc')
        poly(d, [(x - 3, 101), (x + 11, 93), (x + 25, 101)], '#5a5e6a')
        rect(d, (x + 4, 104, x + 8, 108), '#8aa0b4')
        rect(d, (x + 14, 104, x + 18, 108), '#8aa0b4')
    for x in range(30, w, 90):
        line(d, (x, 84, x, 116), '#6a665e')
        line(d, (x - 3, 86, x + 3, 86), '#6a665e')
    for x in range(30, w - 90, 90):
        for k in range(90):
            px(d, x + k, 86 + int(3 * math.sin(k / 90 * math.pi)), '#5a5a5e')
    return im


def id_water_strip(W, n=6):
    """渠里的水：一道道亮纹往右流（n 帧一圈，首尾接得上）"""
    h = ID_BOT - ID_WATER
    out = new(W * 1, h * n)          # 竖着排 n 帧，再转成横条，省得一张图宽过 4096
    rng = np.random.RandomState(73)
    streaks = [(rng.uniform(0, W), rng.randint(1, h - 1), rng.randint(3, 9), rng.rand() < .4) for _ in range(int(W / 7))]
    d = ImageDraw.Draw(out)
    for f in range(n):
        for x, y, L, bright in streaks:
            X = (x + f * 12 / n * (1 + y / h)) % W
            for k in range(L):
                px(d, (X + k) % W, f * h + y, '#cfe6f2' if bright else '#9cc8e0')
    return out, h


def irrigation_ditch():
    W = 640
    fw = far_w(W)
    far = id_far(fw)
    near = new(W, H)
    d = ImageDraw.Draw(near)
    # 后岸：草坡
    near = grass_band(near, 0, W, 104, ID_TOP, seed=74)
    d = ImageDraw.Draw(near)
    line(d, (0, 104, W, 104), '#86b058')
    for x in range(6, W, 23):
        tuft(d, x + (x * 7) % 11, 106, 7 + (x % 3) * 2, seed=x)
    # 渠：后壁（水泥，带水痕）、水、前沿
    rect(d, (0, ID_TOP, W, ID_WATER), '#a4a296')
    line(d, (0, ID_TOP, W, ID_TOP), '#c8c6b8')
    for x in range(0, W, 30):
        line(d, (x, ID_TOP + 1, x, ID_WATER - 1), '#8e8c80')
    near = dither_fill(near, (0, ID_WATER - 3, W, ID_WATER), '#a4a296', '#6e7a6a', .5)
    d = ImageDraw.Draw(near)
    near = grad(near, (0, ID_WATER, W, ID_BOT), ('#4a7a94', '#3e6a84', '#355e76'))
    d = ImageDraw.Draw(near)
    rect(d, (0, ID_BOT, W, ID_BOT + 3), '#b4b2a4')
    line(d, (0, ID_BOT, W, ID_BOT), '#d4d2c4')
    line(d, (0, ID_BOT + 3, W, ID_BOT + 3), '#8e8c80')
    # 土路
    rect(d, (0, ID_BOT + 4, W, 168), '#a88e68')
    near = dither_fill(near, (0, ID_BOT + 4, W, ID_BOT + 7), '#8e7656', '#a88e68', .5)
    noise_specks(near, (0, ID_BOT + 6, W, 168), ['#96805e', '#b89c74', '#8a7254'], 1400, seed=75)
    d = ImageDraw.Draw(near)
    for y in (150, 160):                                                  # 车辙
        for x in range(0, W, 3):
            if (x // 40) % 4 != 3:
                px(d, x, y + int(1.2 * math.sin(x / 37)), '#8a7254')
    rng = np.random.RandomState(76)
    for _ in range(40):                                                   # 小石子
        x, y = rng.randint(0, W), rng.randint(ID_BOT + 8, 166)
        px(d, x, y, '#d4c8b0')
        px(d, x + 1, y, '#7a6a50')
    # 前面的草
    near = grass_band(near, 0, W, 168, H, seed=77, density=4)
    d = ImageDraw.Draw(near)
    line(d, (0, 168, W, 168), '#6e9a48')
    # ---------------- 小水闸（x 96–144）：水泥门柱 + 闸板 + 手轮
    gx = 120
    for x0 in (gx - 22, gx + 16):
        rect(d, (x0, 84, x0 + 6, ID_BOT), '#b8b6aa')
        line(d, (x0, 84, x0, ID_BOT), '#d4d2c4')
        line(d, (x0 + 6, 84, x0 + 6, ID_BOT), '#8e8c80')
    rect(d, (gx - 24, 80, gx + 24, 84), '#a4a296')
    line(d, (gx - 24, 80, gx + 24, 80), '#c8c6b8')
    rect(d, (gx - 16, 100, gx + 16, ID_WATER + 2), '#6a5a4a')             # 闸板（锈铁）
    for yy in range(102, ID_WATER, 5):
        line(d, (gx - 16, yy, gx + 16, yy), '#7e4e36')
    rect(d, (gx - 1, 70, gx + 1, 100), '#4a4a50')
    d.ellipse((gx - 9, 62, gx + 9, 76), outline=C('#2e5a8a'))
    d.ellipse((gx - 8, 63, gx + 8, 75), outline=C('#3e6a9a'))
    line(d, (gx - 8, 69, gx + 8, 69), '#2e5a8a')
    line(d, (gx, 62, gx, 76), '#2e5a8a')
    # ---------------- 水泥板小桥（x 236–270）
    bx0, bx1 = 236, 272
    rect(d, (bx0, ID_TOP - 2, bx1, ID_BOT + 3), '#bcbaae')
    for yy in range(ID_TOP, ID_BOT + 3, 4):
        line(d, (bx0, yy, bx1, yy), '#a8a69a')
    line(d, (bx0, ID_TOP - 2, bx1, ID_TOP - 2), '#d8d6ca')
    line(d, (bx0, ID_BOT + 4, bx1, ID_BOT + 4), '#6e6c62')
    rect(d, (bx0 + 2, ID_BOT + 4, bx1 - 2, ID_BOT + 6), '#2a3a44')       # 板下的阴影
    # ---------------- 排水口（后岸挡土墙 x 440–508）
    rx0, rx1 = 440, 508
    rect(d, (rx0, 84, rx1, ID_TOP), '#b4b2a4')
    for yy in range(88, ID_TOP, 9):
        line(d, (rx0, yy, rx1, yy), '#9a988c')
        for x in range(rx0 + ((yy // 9) % 2) * 8, rx1, 16):
            line(d, (x, yy - 8, x, yy), '#9a988c')
    line(d, (rx0, 84, rx1, 84), '#d4d2c4')
    rect(d, (rx0 - 1, 82, rx1 + 1, 84), '#c8c6b8')
    pcx, pcy = 474, 106
    ellipse(d, (pcx - 12, pcy - 11, pcx + 12, pcy + 11), '#8e8c80')
    ellipse(d, (pcx - 10, pcy - 9, pcx + 10, pcy + 9), '#5a5a56')
    ellipse(d, (pcx - 8, pcy - 7, pcx + 8, pcy + 7), '#1e2024')
    ellipse(d, (pcx - 6, pcy - 4, pcx + 6, pcy + 6), '#121416')
    for k in range(5):                                                    # 管口的水苔
        px(d, pcx - 8 + k * 4, pcy + 9, '#4a6a3a')
    rect(d, (pcx - 4, pcy + 7, pcx + 4, ID_WATER), '#7ab0cc')              # 管口淌下的水（底图；亮纹在 strip 里）
    for x in (rx0 - 6, rx1 + 2):                                          # 挡土墙两边的杂草
        tuft(d, x + 3, ID_TOP - 1, 10, seed=x)
    # ---------------- 土路上的东西：老鼠脚印（桥 → 排水口）、捕鼠笼、三脚架摄像机
    for i, x in enumerate(range(286, 446, 8)):
        y = ID_BOT + 8 + int(2 * math.sin(i * .9)) + (2 if i % 2 else 0)
        rect(d, (x, y, x + 1, y + 1), '#5e4836')                          # 掌心
        for tx_, ty_ in ((-1, -1), (1, -2), (3, -1)):                     # 三个趾头
            px(d, x + tx_, y + ty_, '#5e4836')
    tx, ty = 362, 152                                                     # 捕鼠笼（铁丝，门开着）
    rect(d, (tx - 12, ty - 9, tx + 12, ty), '#6a6a70')
    rect(d, (tx - 11, ty - 8, tx + 11, ty - 1), '#a88e68')
    for x in range(tx - 11, tx + 12, 3):
        line(d, (x, ty - 8, x, ty - 1), '#8a8a92')
    for y in range(ty - 7, ty, 3):
        line(d, (tx - 11, y, tx + 11, y), '#8a8a92')
    line(d, (tx - 12, ty - 9, tx + 12, ty - 9), '#b4b4bc')
    line(d, (tx + 12, ty - 9, tx + 17, ty - 13), '#8a8a92')               # 掀起的门
    rect(d, (tx - 2, ty - 3, tx + 1, ty - 1), '#e8c860')                  # 诱饵（奶酪）
    cx, cy = 528, 152                                                     # 三脚架 + 摄像机（对着渠）
    for fx in (-7, 0, 7):
        line(d, (cx, cy - 18, cx + fx, cy), '#3a3a42')
    rect(d, (cx - 7, cy - 26, cx + 5, cy - 18), '#2a2a30')
    rect(d, (cx - 11, cy - 25, cx - 7, cy - 20), '#3e3e48')
    px(d, cx - 10, cy - 23, '#8ab4e8')
    px(d, cx + 3, cy - 25, '#e83a3a')
    line(d, (cx - 7, cy - 26, cx + 5, cy - 26), '#4a4a54')
    # 电线杆（近）
    pole(near, 196, 166, 158)
    pole(near, 590, 166, 158)
    wires(near, [(0, 18), (196, 10), (590, 14), (640, 18)], sag=8)
    d = ImageDraw.Draw(near)
    for x, sd in ((20, 1), (70, 2), (330, 3), (414, 4), (612, 5)):        # 前面的高草丛
        tuft(d, x, 178, 12, seed=sd)
    wat, wh = id_water_strip(W)
    wat_h = Image.new('RGBA', (W * 6, wh), (0, 0, 0, 0))
    for f in range(6):
        wat_h.paste(wat.crop((0, f * wh, W, (f + 1) * wh)), (f * W, 0))
    # strip 太宽（3840）：切成 2 段 320 宽各自循环
    layers = {'far': far, 'near': near}
    strips = []
    for k in range(2):
        seg = Image.new('RGBA', (320 * 6, wh), (0, 0, 0, 0))
        for f in range(6):
            seg.paste(wat_h.crop((f * W + k * 320, 0, f * W + k * 320 + 320, wh)), (f * 320, 0))
        layers[f'water{k}'] = seg
        strips.append({'type': 'strip', 'image': f'bg/irrigation_ditch/water{k}', 'n': 6, 'fps': 6, 'w': 320, 'h': wh,
                       'x': k * 320, 'y': ID_WATER, 'k': 1})
    # 排水口淌水（4 帧）
    drip = new(9 * 4, ID_WATER - pcy - 6)
    dd = ImageDraw.Draw(drip)
    for f in range(4):
        for y in range(drip.height):
            if (y + f * 2) % 5 < 2:
                px(dd, f * 9 + 2 + (y % 3 == 0), y, '#d4ecf6')
                px(dd, f * 9 + 6, y + 1, '#b8dcee')
    layers['drip'] = drip
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(sluice=[120, 146], sluice_wheel=[120, 69], bridge=[254, 146], tracks_start=[286, 146],
                             tracks_end=[440, 146], trap=[362, 150], camera=[528, 150], drain=[474, 146], drain_pipe=[474, 106],
                             ditch_y=[ID_TOP, ID_BOT], walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/irrigation_ditch/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/irrigation_ditch/near', 'k': 1, 'x': 0, 'y': 0}] + strips
                + [{'type': 'strip', 'image': 'bg/irrigation_ditch/drip', 'n': 4, 'fps': 8, 'w': 9, 'x': pcx - 4, 'y': pcy + 7, 'k': 1},
                   {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = compose(far, near, w=W)
    pv.alpha_composite(wat_h.crop((0, 0, W, wh)), (0, ID_WATER))
    preview('irrigation_ditch', {'a': pv}, ['a'], W)
    save_layers('irrigation_ditch', layers, meta)
    return meta



# ============================================================ 牧场屋内 farmhouse（480 宽，下午，第 8 战段 1）
#   木板墙的农家厨房，屋里没人：左边后门 → 窗（外面是牧草地）→ 水槽和料理台 → 煤气灶（上面一只平底锅，能拿走：pick 'pan'）→
#   碗柜 → 老式双门冰箱 → 正中一张铺格子桌布的餐桌和四把椅子（一把倒在地上）、吊灯 → 右边挂着草帽和雨衣、柴火箱。
#   老鼠能躲的地方：桌子底下、椅子后面、冰箱底下（都写在 anchors 里）。
FH = dict(wall=('#8a6a4a', '#7a5c3e', '#9c7a56', '#5e4630'), floor=('#7e6448', '#74593e', '#8a6e50', '#5e4630'))


def fh_floor(im, x0, x1, G):
    """旧木地板：比工作室的暗、木条宽"""
    d = ImageDraw.Draw(im)
    y, h, row = G, 3.5, 0
    tones = ['#86684a', '#7a5e42', '#8e7050', '#806246']
    rng = np.random.RandomState(81)
    while y < H:
        yb = min(H, int(round(y + h)))
        rect(d, (x0, int(y), x1, yb - 1), tones[row % 4])
        line(d, (x0, yb - 1, x1, yb - 1), '#5a4430')
        plank = int(50 + h * 7)
        off = rng.randint(0, plank)
        for x in range(x0 - off, x1, plank):
            if x > x0:
                line(d, (x, int(y), x, yb - 2), '#62492f')
        for _ in range(int((x1 - x0) / 14)):
            gx, gy = rng.randint(x0, x1 - 6), rng.randint(int(y), max(int(y) + 1, yb - 1))
            line(d, (gx, gy, gx + rng.randint(2, 7), gy), '#6e5438' if row % 2 else '#96785a')
        y += h
        h = min(10.0, h * 1.18)
        row += 1
    return dither_fill(im, (x0, G, x1, G + 2), '#4e3a28', '#6a5038', .5)


def fh_chair(d, x, base, facing=1, col='#b08458', col2='#c89a68'):
    """木椅（侧面）：靠背在 facing 的反方向"""
    bx = x - facing * 7
    rect(d, (bx - 1, base - 26, bx + 1, base), col)
    for yy in (base - 24, base - 19):
        line(d, (bx - 1, yy, bx + 1, yy), col2)
    rect(d, (x - 8, base - 12, x + 8, base - 10), col2)
    line(d, (x - 8, base - 12, x + 8, base - 12), mix(col2, '#ffffff', .25))
    line(d, (x + facing * 7, base - 10, x + facing * 7, base), col)
    line(d, (x - facing * 6, base - 10, x - facing * 6, base), col)


def fh_room():
    W, G = 480, 132
    im = new(W, H)
    im = wood_wall(im, 0, W, 0, G, cols=FH['wall'], plank=8, seed=82)
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 8), '#4a3626')                                       # 天花板横梁
    line(d, (0, 8, W, 8), '#6a4e36')
    rect(d, (0, G - 5, W, G), '#4a3626')
    line(d, (0, G - 5, W, G - 5), '#6a4e36')
    # ---------------- 后门（8–40）：木门 + 上半截玻璃，门缝里透光
    dx0, dx1, dy0 = 8, 40, G - 78
    rect(d, (dx0 - 3, dy0 - 3, dx1 + 3, G), '#4a3626')
    rect(d, (dx0, dy0, dx1, G - 1), '#a07a52')
    rect(d, (dx0 + 4, dy0 + 4, dx1 - 4, dy0 + 30), '#d8ead0')
    line(d, ((dx0 + dx1) // 2, dy0 + 4, (dx0 + dx1) // 2, dy0 + 30), '#a07a52')
    line(d, (dx0 + 4, dy0 + 17, dx1 - 4, dy0 + 17), '#a07a52')
    rect(d, (dx0 + 4, dy0 + 36, dx1 - 4, G - 6), '#8e6a46')
    bevel(d, (dx0 + 4, dy0 + 36, dx1 - 4, G - 6), '#b08a5e', '#6a4a30')
    rect(d, (dx1 - 7, dy0 + 32, dx1 - 4, dy0 + 34), '#c8c0a0')
    line(d, (dx1 + 1, dy0, dx1 + 1, G - 1), '#f8e8b0')                    # 门缝透光
    # ---------------- 窗（54–108）：外面是牧草地和蓝天
    wx0, wx1, wy0, wy1 = 54, 108, 30, 74
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), '#4a3626')
    im = grad(im, (wx0, wy0, wx1, wy1 - 16), ('#8cc0ec', '#b8daf4'))
    d = ImageDraw.Draw(im)
    rect(d, (wx0, wy1 - 16, wx1, wy1), '#8ab060')
    for x in range(wx0, wx1, 3):
        px(d, x, wy1 - 16 + (x % 5), '#a8c878')
    ellipse(d, (wx0 + 30, wy1 - 26, wx1 + 6, wy1 - 12), '#5e8e48')
    line(d, ((wx0 + wx1) // 2, wy0, (wx0 + wx1) // 2, wy1), '#e8e0cc')
    line(d, (wx0, (wy0 + wy1) // 2, wx1, (wy0 + wy1) // 2), '#e8e0cc')
    rect(d, (wx0 - 4, wy1 + 3, wx1 + 4, wy1 + 6), '#6a4e36')
    rect(d, (wx0 - 2, wy0 - 6, wx1 + 2, wy0 - 1), '#e8c0a0')              # 小窗帘（褪色的红格）
    for x in range(wx0 - 2, wx1 + 2, 4):
        rect(d, (x, wy0 - 6, x + 1, wy0 - 1), '#c87060')
    for k, x in enumerate((wx0 + 6, wx0 + 18, wx1 - 10)):                 # 窗台上的瓶瓶罐罐
        rect(d, (x, wy1 - 1 - [6, 9, 5][k], x + 4, wy1 + 2), ['#7ab07a', '#c8a050', '#e8e0cc'][k])
    # ---------------- 料理台 + 水槽（50–150）
    kx0, kx1, kt = 50, 150, 100
    rect(d, (kx0, kt, kx1, G - 1), '#c8bca4')
    rect(d, (kx0 - 2, kt - 3, kx1 + 2, kt), '#8a8c90')
    line(d, (kx0 - 2, kt - 3, kx1 + 2, kt - 3), '#b4b8bc')
    rect(d, (kx0 + 8, kt - 3, kx0 + 40, kt - 1), '#5a5e66')               # 水槽
    rect(d, (kx0 + 22, kt - 14, kx0 + 24, kt - 3), '#9a9ea4')              # 水龙头
    line(d, (kx0 + 22, kt - 14, kx0 + 30, kt - 14), '#9a9ea4')
    px(d, kx0 + 30, kt - 13, '#9a9ea4')
    for k in range(3):                                                    # 柜门
        x = kx0 + 3 + k * 33
        rect(d, (x, kt + 4, x + 29, G - 4), '#b8ac92')
        bevel(d, (x, kt + 4, x + 29, G - 4), '#d8ccb2', '#8e8270')
        rect(d, (x + 13, kt + 8, x + 16, kt + 9), '#6a6e74')
    for k, x in enumerate((kx0 + 52, kx0 + 62, kx0 + 74)):                # 台面上的锅碗、砧板
        if k == 0:
            rect(d, (x, kt - 6, x + 6, kt - 3), '#f4f0e6')
        elif k == 1:
            rect(d, (x, kt - 4, x + 9, kt - 3), '#d8b07a')
        else:
            rect(d, (x, kt - 9, x + 10, kt - 3), '#5a6a7a')
            line(d, (x, kt - 9, x + 10, kt - 9), '#7a8a9a')
    # 吊柜
    rect(d, (kx0 + 64, 26, kx1, 56), '#9c7a56')
    for k in range(2):
        x = kx0 + 66 + k * 18
        bevel(d, (x, 28, x + 15, 54), '#b8946c', '#6a4e36')
        rect(d, (x + 7, 50, x + 8, 51), '#d8c070')
    # ---------------- 煤气灶（154–186）
    sx0, sx1 = 154, 188
    rect(d, (sx0, kt + 2, sx1, G - 1), '#e8e4da')
    bevel(d, (sx0, kt + 2, sx1, G - 1), '#f8f6f0', '#a8a49a')
    rect(d, (sx0 + 4, kt + 10, sx1 - 4, G - 6), '#3a3a40')                 # 烤箱门的玻璃
    line(d, (sx0 + 4, kt + 8, sx1 - 4, kt + 8), '#8a8a90')
    for k in range(3):
        px(d, sx0 + 8 + k * 9, kt + 5, '#2a2a30')
    rect(d, (sx0 - 1, kt - 2, sx1 + 1, kt + 1), '#5a5a62')
    for bx in (sx0 + 9, sx1 - 9):
        d.ellipse((bx - 5, kt - 4, bx + 5, kt), outline=C('#2a2a30'))
    rect(d, (sx0 + 2, 50, sx1 - 2, 54), '#9a9ea4')                         # 抽油烟罩
    poly(d, [(sx0 - 2, 62), (sx1 + 2, 62), (sx1 - 2, 54), (sx0 + 2, 54)], '#b4b8bc')
    line(d, (sx0 - 2, 62, sx1 + 2, 62), '#7a7e84')
    # ---------------- 碗柜（192–232）：玻璃门里一摞摞盘子
    cx0, cx1 = 194, 232
    rect(d, (cx0, 40, cx1, G - 1), '#7a5a3a')
    rect(d, (cx0 - 2, 37, cx1 + 2, 40), '#9c7a56')
    for k in range(2):
        gx = cx0 + 3 + k * 18
        rect(d, (gx, 44, gx + 15, 88), '#c8d4d4')
        for yy in (56, 70, 84):
            line(d, (gx, yy, gx + 15, yy), '#6a4e36')
            for pxx in range(gx + 2, gx + 14, 4):
                ellipse(d, (pxx - 2, yy - 6, pxx + 2, yy), '#f4f0e6')
                px(d, pxx, yy - 3, '#7aa0c8')
        bevel(d, (gx, 44, gx + 15, 88), '#9c7a56', '#5a3e28')
    for k in range(2):
        gx = cx0 + 3 + k * 18
        rect(d, (gx, 94, gx + 15, G - 5), '#86643e')
        bevel(d, (gx, 94, gx + 15, G - 5), '#a07a52', '#5a3e28')
    # ---------------- 老式双门冰箱（240–276），底下一条黑缝
    fx0, fx1, ft = 240, 276, 52
    rect(d, (fx0, ft, fx1, G - 2), '#e8e0c8')
    ellipse(d, (fx0, ft - 3, fx1, ft + 5), '#e8e0c8')
    line(d, (fx0, ft + 26, fx1, ft + 26), '#a8a088')
    line(d, (fx1 - 1, ft, fx1 - 1, G - 2), '#c4bca4')
    line(d, (fx0 + 1, ft, fx0 + 1, G - 2), '#f8f4e8')
    rect(d, (fx0 + 4, ft + 14, fx0 + 5, ft + 22), '#9a9ea4')
    rect(d, (fx0 + 4, ft + 30, fx0 + 5, ft + 44), '#9a9ea4')
    rect(d, (fx0 + 10, ft + 4, fx0 + 26, ft + 8), '#c8c0a8')               # 牌子
    rect(d, (fx0 + 20, ft + 36, fx0 + 28, ft + 46), '#f4f0e6')             # 贴着的便条
    px(d, fx0 + 24, ft + 36, '#e83a3a')
    rect(d, (fx0 + 1, G - 2, fx1 - 1, G), '#1e1a18')                      # 冰箱底下的缝
    # ---------------- 墙上的日历、挂钟；右边挂着的草帽和雨衣、柴火箱
    rect(d, (300, 30, 318, 54), '#f4f0e6')
    rect(d, (300, 30, 318, 36), '#c83a34')
    for r in range(4):
        for c in range(5):
            px(d, 302 + c * 3, 39 + r * 4, '#5a5a62')
    ellipse(d, (364, 26, 380, 42), '#5a4030')
    ellipse(d, (366, 28, 378, 40), '#f4f0e6')
    line(d, (372, 34, 372, 29), '#2a2a30')
    line(d, (372, 34, 376, 36), '#2a2a30')
    for hx in (408, 440):
        rect(d, (hx, 44, hx + 2, 46), '#3a2a1e')
    ellipse(d, (396, 46, 420, 56), '#e0c070')                             # 草帽
    ellipse(d, (402, 42, 414, 52), '#d4b060')
    line(d, (402, 50, 414, 50), '#c83a34')
    poly(d, [(434, 46), (446, 46), (452, 96), (428, 96)], '#e8c030')        # 雨衣
    line(d, (440, 46, 440, 96), '#c8a020')
    rect(d, (436, 46, 444, 52), '#d8b028')
    rect(d, (420, 104, 470, G - 1), '#6a4a30')                             # 柴火箱
    for k in range(6):
        ellipse(d, (424 + k * 7, 96, 432 + k * 7, 106), ['#b08a5e', '#a07a52', '#c49a6c'][k % 3])
        px(d, 428 + k * 7, 101, '#6a4a30')
    for yy in range(108, G, 6):
        line(d, (420, yy, 470, yy), '#5a3e28')
    return im, G


def fh_table(im, G):
    """餐桌（格子桌布）+ 椅子，一把倒在地上；桌子底下一片阴影（地板画完以后再画）"""
    d = ImageDraw.Draw(im)
    tx0, tx1, tt = 300, 380, 120
    im = dither_fill(im, (tx0 + 2, tt + 18, tx1 - 2, 150), '#3e2e20', '#5a4430', .35)
    d = ImageDraw.Draw(im)
    fh_chair(d, tx0 - 8, 146, facing=1)
    for x in (tx0 + 6, tx1 - 8):                                          # 桌腿
        rect(d, (x, tt + 4, x + 3, 150), '#5a3e28')
    rect(d, (tx0 + 10, tt + 4, tx0 + 12, 144), '#4a3220')
    rect(d, (tx1 - 16, tt + 4, tx1 - 14, 144), '#4a3220')
    rect(d, (tx0, tt - 2, tx1, tt + 2), '#6a4a30')
    for x in range(tx0 - 2, tx1 + 3):                                     # 桌布：红白格子，垂下来一截
        for y in range(tt - 3, tt + 12):
            if y > tt + 3 and (x < tx0 or x > tx1):
                continue
            k = ((x // 4) + (y // 3)) % 2
            c = '#d84a3e' if k else '#f4ece0'
            if y >= tt:
                c = mix(c, '#000000', .12)
            px(d, x, y, c)
    for x in range(tx0 - 2, tx1 + 3, 3):
        px(d, x, tt + 12, '#b8382e')
    rect(d, (tx0 + 14, tt - 7, tx0 + 20, tt - 3), '#f4f0e6')              # 桌上的杯子、报纸
    rect(d, (tx1 - 34, tt - 4, tx1 - 16, tt - 3), '#e0dccc')
    line(d, (tx1 - 33, tt - 4, tx1 - 18, tt - 4), '#8a8a90')
    fh_chair(d, tx1 + 8, 146, facing=-1)
    # 倒在地上的椅子（右前）
    cx, cy = 410, 160
    ellipse(d, (cx - 18, cy - 1, cx + 18, cy + 3), '#4a3626')            # 影子
    rect(d, (cx - 14, cy - 3, cx + 14, cy - 1), '#c89a68')               # 椅面（侧躺）
    line(d, (cx - 14, cy - 3, cx + 14, cy - 3), '#dcb07c')
    for k in (-10, 10):                                                   # 两条腿翘起来
        line(d, (cx + k, cy - 3, cx + k + 5, cy - 14), '#b08458')
    rect(d, (cx - 26, cy - 2, cx - 14, cy), '#b08458')                    # 靠背平躺在地上
    line(d, (cx - 22, cy - 2, cx - 22, cy), '#8a6444')
    # 吊灯
    line(d, (340, 8, 340, 70), '#2a2a30')
    poly(d, [(330, 78), (350, 78), (344, 70), (336, 70)], '#2e5a46')
    line(d, (330, 78, 350, 78), '#4a7a62')
    px(d, 340, 79, '#fff4c8')
    return im


def fh_pan():
    """平底锅（煤气灶上）；拿走以后换空图"""
    im = new(24, 8)
    d = ImageDraw.Draw(im)
    ellipse(d, (0, 2, 14, 7), '#2a2a30')
    line(d, (1, 3, 13, 3), '#4a4a54')
    rect(d, (14, 3, 23, 4), '#3a2a20')
    px(d, 23, 3, '#5a4030')
    return im


def fh_glow(G):
    W = 480
    f = np.zeros((H, W))
    for y in range(G + 2, H):
        k = (y - G) / (H - G)
        xa, xb = 60 + k * 40, 110 + k * 64
        f[y, int(xa):int(xb)] = .5 - .25 * k
    for y in range(G - 40, H):                                            # 门缝的一道光
        if y > G:
            f[y, 42 + int((y - G) * .6):46 + int((y - G) * .9)] = .45
    bay = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
    fq = np.clip(np.floor(f * 4 + bay) / 4, 0, 1)
    a = np.zeros((H, W, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * np.array((120, 96, 52), float), 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def farmhouse():
    W = 480
    room, G = fh_room()
    room = fh_floor(room, 0, W, G)
    room = fh_table(room, G)
    d = ImageDraw.Draw(room)
    rect(d, (8, G, 40, G + 1), '#4a3626')                                 # 门槛
    pan = fh_pan()
    empty = new(24, 8)
    glow = fh_glow(G)
    dust = None
    layers = {'room': room, 'glow': glow, 'pan': pan, 'pan_none': empty}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(back_door=[24, 148], window=[81, 52], sink=[74, 146], stove=[171, 146], pan=[164, 96],
                             cupboard=[213, 146], fridge=[258, 146], under_fridge=[258, 134], table=[340, 150],
                             under_table=[340, 140], chair_l=[292, 146], chair_r=[388, 146], fallen_chair=[410, 158],
                             woodbox=[445, 146], raincoat=[440, 70], walk_x=[44, 472]),
                layers=[{'type': 'pano', 'image': 'bg/farmhouse/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pick', 'images': ['bg/farmhouse/pan', 'bg/farmhouse/pan_none'], 'key': 'pan', 'k': 1,
                         'x': 156, 'y': 93},
                        {'type': 'glow', 'image': 'bg/farmhouse/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.03},
                        {'type': 'tint', 'color': '#ff9a40', 'alpha': 0.08}],
                fg=[])
    pv = room.copy()
    pv.alpha_composite(pan, (156, 93))
    pv = Image.fromarray(np.clip(np.array(pv).astype(int) + np.array(glow).astype(int) * (np.array(glow)[..., 3:] > 0), 0, 255).astype(np.uint8))
    pv.putalpha(255)
    preview('farmhouse', {'a': pv}, ['a'], W)
    save_layers('farmhouse', layers, meta)
    return meta



# ============================================================ 牧场外景 farm_out（480 宽，白天）
#   左：农舍（木墙、铁皮屋顶、门廊和门）→ 晾衣绳上一排没收的衣服 → 空狗屋（链子拖在地上、空碗）→
#   右：红色谷仓和小筒仓。谷仓前面一段木篱笆，横杆上摆着一排空罐（承太郎教弹钢珠：pick 'cans'，0 立着 / 1 打穿倒下）。
#   后面是牧草地和牧场的横杆围栏，远处是山。
FO_CANS = [(318, 118), (334, 118), (350, 118), (366, 118), (382, 118), (398, 118)]   # 每只罐子底部中心


def fo_farmhouse(im):
    d = ImageDraw.Draw(im)
    x0, x1, top, B = 22, 186, 62, 138
    rect(d, (x0, top, x1, B), '#c8b48e')
    for x in range(x0, x1, 6):                                            # 竖板墙
        line(d, (x, top, x, B), '#b09c78')
        line(d, (x + 1, top, x + 1, B), '#d8c49e')
    for i in range(22):                                                   # 铁皮屋顶（波浪板，红褐）
        k = i / 21
        xa, xb = x0 - 6 * k - (1 - k) * -10, x1 + 6 * k + (1 - k) * -10
        line(d, (xa, top - 22 + i, xb, top - 22 + i), '#8e4a36' if i % 3 else '#7a3e2c')
    for x in range(x0 + 8, x1 - 6, 4):
        line(d, (x, top - 19, x - 1, top), '#a65a42')
    line(d, (x0 + 10, top - 22, x1 - 10, top - 22), '#b8705a')
    rect(d, (x0 - 6, top, x1 + 6, top + 2), '#5a2e22')
    rect(d, (60, top - 34, 70, top - 18), '#8a8a8e')                       # 铁皮烟囱
    rect(d, (58, top - 36, 72, top - 34), '#6a6a70')
    # 窗
    for wx in (34, 140):
        window(d, (wx, top + 12, wx + 24, top + 34), frame='#f0e8d4', glass=('#7e9cb4', '#b4cce0'), curtain='#e8d8b8')
    # 门廊：小屋檐、两根柱、门、台阶
    dx = 92
    for i in range(6):
        line(d, (dx - 22 + i, top + 14 + i, dx + 46 - i, top + 14 + i), '#8e4a36' if i % 2 else '#7a3e2c')
    for cx in (dx - 18, dx + 40):
        rect(d, (cx, top + 20, cx + 3, B), '#e8dcc4')
    rect(d, (dx, top + 28, dx + 22, B), '#6a4a30')
    rect(d, (dx + 2, top + 30, dx + 20, B - 1), '#7e5a3c')
    rect(d, (dx + 5, top + 33, dx + 17, top + 46), '#a8c0cc')
    line(d, (dx + 11, top + 33, dx + 11, top + 46), '#7e5a3c')
    px(d, dx + 18, top + 56, '#d8c070')
    for k in range(2):
        rect(d, (dx - 24 + k * 2, B - 2 + k * 2, dx + 48 - k * 2, B + k * 2), ['#b4a888', '#9e9274'][k])
    rect(d, (x0, B - 4, x1, B), '#8e7a5c')                                 # 墙脚
    # 门廊上的木凳、水桶
    rect(d, (dx + 26, B - 12, dx + 38, B - 10), '#8a6444')
    line(d, (dx + 27, B - 10, dx + 27, B - 3), '#6a4a30')
    line(d, (dx + 37, B - 10, dx + 37, B - 3), '#6a4a30')
    rect(d, (dx - 14, B - 10, dx - 6, B - 2), '#8a9aa4')
    line(d, (dx - 14, B - 10, dx - 6, B - 10), '#b4c4cc')
    return im


def fo_barn(im):
    d = ImageDraw.Draw(im)
    x0, x1, top, B = 330, 456, 54, 138
    # 筒仓（后面）
    rect(d, (440, 34, 470, B), '#b8bcc0')
    for yy in range(38, B, 6):
        line(d, (440, yy, 470, yy), '#9ea2a8')
    ellipse(d, (440, 26, 470, 42), '#9ea2a8')
    line(d, (468, 34, 468, B), '#8a8e94')
    # 谷仓：山形屋顶
    cx = (x0 + x1) // 2
    for i in range(30):
        w2 = 8 + i * 2.3
        line(d, (cx - w2, top - 26 + i, cx + w2, top - 26 + i), '#5a5e66' if i % 3 else '#4a4e56')
    rect(d, (x0, top + 4, x1, B), '#a83a2e')
    for x in range(x0, x1, 5):
        line(d, (x, top + 4, x, B), '#943226')
    poly(d, [(x0 + 4, top + 4), (cx, top - 22), (x1 - 4, top + 4)], '#a83a2e')
    line(d, (x0 + 4, top + 4, cx, top - 22), '#f4ece0')
    line(d, (cx, top - 22, x1 - 4, top + 4), '#f4ece0')
    rect(d, (cx - 8, top - 12, cx + 8, top), '#f4ece0')                   # 干草窗
    rect(d, (cx - 6, top - 10, cx + 6, top - 2), '#3a2a20')
    rect(d, (cx - 5, top - 5, cx + 5, top - 2), '#d8b860')
    # 大门（白框打 X）
    gx0, gx1 = cx - 26, cx + 26
    rect(d, (gx0, top + 26, gx1, B), '#8e2e24')
    rect(d, (gx0, top + 26, gx1, top + 28), '#f4ece0')
    rect(d, (gx0, top + 26, gx0 + 2, B), '#f4ece0')
    rect(d, (gx1 - 2, top + 26, gx1, B), '#f4ece0')
    line(d, (cx, top + 26, cx, B), '#f4ece0')
    for a0, a1 in ((gx0, cx), (cx, gx1)):
        line(d, (a0, top + 28, a1, B), '#f4ece0')
        line(d, (a1, top + 28, a0, B), '#f4ece0')
    rect(d, (x0, B - 3, x1, B), '#6a2a20')
    return im


def fo_fence(d, x0, x1, top, B, posts=16):
    """木篱笆：桩 + 两道横杆"""
    for y in (top + 6, top + 16):
        rect(d, (x0, y, x1, y + 2), '#a07a52')
        line(d, (x0, y, x1, y), '#c49a6c')
        line(d, (x0, y + 3, x1, y + 3), '#6a4a30')
    for x in range(x0, x1 + 1, posts):
        rect(d, (x - 1, top, x + 2, B), '#8a6444')
        line(d, (x - 1, top, x - 1, B), '#b08458')
        px(d, x, top, '#c49a6c')


def fo_cans(shot):
    """篱笆横杆上的一排空罐；shot = 都被打穿：倒下、滚到地上、罐身上有洞"""
    im = new(480, H)
    d = ImageDraw.Draw(im)
    cols = [('#c83a34', '#e86a5e'), ('#3a6ab0', '#6a9ad8'), ('#d8c040', '#f0e080'), ('#3a8a4a', '#6ab07a'),
            ('#c83a34', '#e86a5e'), ('#d8d8d8', '#ffffff')]
    rng = np.random.RandomState(91)
    for k, (cx, by) in enumerate(FO_CANS):
        c, hi = cols[k]
        if not shot:
            rect(d, (cx - 3, by - 8, cx + 3, by - 1), c)
            line(d, (cx - 3, by - 8, cx + 3, by - 8), '#c8c8cc')
            line(d, (cx - 2, by - 7, cx - 2, by - 2), hi)
            line(d, (cx - 3, by - 5, cx + 3, by - 5), '#f4f0e6')
        else:
            gx = cx + rng.randint(-6, 7)
            gy = 140 + rng.randint(0, 4)
            rect(d, (gx - 4, gy - 4, gx + 4, gy), c)                       # 躺在地上
            line(d, (gx - 4, gy - 4, gx + 4, gy - 4), hi)
            ellipse(d, (gx + 3, gy - 4, gx + 5, gy), '#c8c8cc')
            px(d, gx - 1, gy - 2, '#1e1e24')                               # 弹孔
            px(d, gx, gy - 2, '#1e1e24')
    return im


def fo_laundry(d):
    """晾衣绳：两根杆子 + 一排衣服（衬衫、毛巾、工作裤）"""
    x0, x1, y = 204, 300, 72
    for x in (x0, x1):
        rect(d, (x - 1, y - 6, x + 1, 138), '#8a8a8e')
        line(d, (x - 6, y - 4, x + 6, y - 4), '#8a8a8e')
    for k in range(x1 - x0):
        px(d, x0 + k, y + int(4 * math.sin(k / (x1 - x0) * math.pi)), '#e8e4dc')
    items = [(214, 'shirt', '#e8e4dc'), (232, 'towel', '#7ab0d8'), (246, 'towel', '#f0d070'),
             (262, 'pants', '#4a5a7a'), (282, 'shirt', '#d87060')]
    for x, kind, col in items:
        yy = y + int(4 * math.sin((x - x0) / (x1 - x0) * math.pi)) + 1
        if kind == 'shirt':
            poly(d, [(x - 8, yy), (x + 8, yy), (x + 11, yy + 6), (x + 6, yy + 7), (x + 6, yy + 20), (x - 6, yy + 20),
                     (x - 6, yy + 7), (x - 11, yy + 6)], col)
            line(d, (x, yy + 1, x, yy + 19), mix(col, '#000000', .15))
        elif kind == 'towel':
            rect(d, (x - 5, yy, x + 5, yy + 16), col)
            line(d, (x - 5, yy + 13, x + 5, yy + 13), mix(col, '#ffffff', .4))
        else:
            rect(d, (x - 6, yy, x + 6, yy + 4), col)
            rect(d, (x - 6, yy + 4, x - 1, yy + 24), col)
            rect(d, (x + 1, yy + 4, x + 6, yy + 24), col)
        px(d, x - 4, yy - 1, '#c8a050')
        px(d, x + 4, yy - 1, '#c8a050')


def fo_doghouse(d, x, B):
    """空狗屋：红屋顶的木屋、黑洞洞的门、链子拖在地上、翻倒的空碗"""
    rect(d, (x, B - 20, x + 26, B), '#b08a5e')
    for xx in range(x, x + 26, 4):
        line(d, (xx, B - 20, xx, B), '#9a7650')
    poly(d, [(x - 3, B - 19), (x + 13, B - 32), (x + 29, B - 19)], '#a83a2e')
    line(d, (x - 3, B - 19, x + 13, B - 32), '#c85a4a')
    ellipse(d, (x + 7, B - 15, x + 19, B - 1), '#1e1814')
    rect(d, (x + 7, B - 8, x + 19, B), '#1e1814')
    for k in range(10):                                                   # 链子
        px(d, x + 22 + k * 2, B + 2 + (k % 2), '#8a8a92')
        px(d, x + 23 + k * 2, B + 2 + ((k + 1) % 2), '#5a5a62')
    ellipse(d, (x + 44, B + 1, x + 54, B + 5), '#3a6ab0')                 # 空碗
    ellipse(d, (x + 46, B + 1, x + 52, B + 3), '#2a4a80')


def farm_out():
    W = 480
    fw = far_w(W)
    far = sky_layer(fw, seed=92)
    near = new(W, H)
    d = ImageDraw.Draw(near)
    near = grass_band(near, 0, W, 108, 140, seed=93)
    d = ImageDraw.Draw(near)
    line(d, (0, 108, W, 108), '#86b058')
    fo_fence(d, 0, W, 96, 116, posts=24)                                  # 牧场后面的围栏（远一点、细一点）
    near = fo_farmhouse(near)
    near = fo_barn(near)
    d = ImageDraw.Draw(near)
    fo_laundry(d)
    fo_doghouse(d, 226, 138)
    # 院子：土地、车辙、草皮
    rect(d, (0, 138, W, H), '#a88e68')
    near = dither_fill(near, (0, 138, W, 141), '#8e7656', '#a88e68', .5)
    noise_specks(near, (0, 140, W, H), ['#96805e', '#b89c74', '#8a7254'], 1100, seed=94)
    d = ImageDraw.Draw(near)
    for y in (156, 168):
        for x in range(0, W, 2):
            px(d, x, y + int(1.5 * math.sin(x / 41)), '#8a7254')
    rng = np.random.RandomState(95)
    for _ in range(14):                                                   # 一块块草皮
        gx, gy = rng.randint(0, W), rng.randint(146, 176)
        for k in range(rng.randint(6, 16)):
            line(d, (gx + k, gy, gx + k, gy - rng.randint(1, 4)), ['#6e9a48', '#86b058', '#5e8a3e'][rng.randint(3)])
    fo_doghouse(d, 226, 138)
    # 教学用的篱笆（谷仓前）：横杆上摆空罐
    fo_fence(d, 306, 410, 110, 140, posts=26)
    for x in (300, 420):
        tuft(d, x, 140, 9, seed=x)
    # 门口的牛奶罐、干草捆
    for k, x in enumerate((196, 206)):
        rect(d, (x, 126, x + 7, 138), '#c8ccd0')
        rect(d, (x + 1, 123, x + 6, 126), '#a8acb0')
        line(d, (x + 1, 128, x + 1, 137), '#e8ecf0')
    for x in (420, 440):
        rect(d, (x, 126, x + 18, 140), '#d8b860')
        for yy in range(128, 140, 3):
            line(d, (x, yy, x + 18, yy), '#c4a24c')
        line(d, (x + 5, 126, x + 5, 140), '#8a6a3a')
        line(d, (x + 13, 126, x + 13, 140), '#8a6a3a')
    up, shot = fo_cans(False), fo_cans(True)
    layers = {'far': far, 'near': near, 'cans_up': up, 'cans_shot': shot}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(house_door=[103, 146], porch=[103, 140], window_l=[46, 86], laundry=[252, 146],
                             laundry_line=[252, 80], doghouse=[239, 146], dog_bowl=[275, 141], milk_cans=[204, 146],
                             barn=[393, 146], barn_door=[393, 120], silo=[455, 80], fence=[358, 146],
                             cans=[list(c) for c in FO_CANS], hay=[438, 146], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/farm_out/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/farm_out/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pick', 'images': ['bg/farm_out/cans_up', 'bg/farm_out/cans_shot'], 'key': 'cans', 'k': 1,
                         'x': 0, 'y': 0},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = compose(far, near, up, w=W)
    preview('farm_out', {'a': pv}, ['a'], W)
    preview('farm_out_shot', {'a': compose(far, near, shot, w=W)}, ['a'], W)
    save_layers('farm_out', layers, meta)
    return meta


# ============================================================ 山坡 hillside（960 宽，白天，第 8 战段 2）
#   左边低处是池塘（芦苇、睡莲叶，水面闪光）：脚印在池塘边断掉。往右地势抬高，后面一整面长满草的山坡，
#   坡上散着大大小小的岩石和草丛；坡顶几棵松树。地面是草地 + 一条踩出来的土路，前景有几丛高草（fg）。
#   狙击段用 anchors 里的岩石坐标：reflect_rock 是飞镖跳弹的那块（会闪一下的反光点），rat_hide 是老鼠真正趴着的草丛。
def HS_SLOPE(x):
    """山坡的轮廓线 y(x)"""
    t = max(0, x - 280)
    return 132 - t * 0.105 - 6 * math.sin(t / 70)


HS_ROCKS = [(352, 'r1', 18, 10), (430, 'r2', 26, 14), (512, 'r3', 14, 8), (590, 'r4', 34, 20), (668, 'reflect_rock', 30, 18),
            (744, 'r6', 16, 9), (812, 'r7', 40, 22), (900, 'r8', 20, 11)]


def hs_far(w):
    im = sky_layer(w, seed=101, hills=True)
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(102)
    for x in range(w):                                                    # 近一层的绿山
        y = 96 + 10 * math.sin(x / 90 + 1) + 5 * math.sin(x / 23)
        line(d, (x, int(y), x, 180), '#5a8a5a')
        px(d, x, int(y), '#7aa676')
    for i in range(int(w / 9)):
        x = rng.randint(0, w)
        y = 96 + 10 * math.sin(x / 90 + 1) + 5 * math.sin(x / 23)
        ellipse(d, (x - 4, y - 4, x + 4, y + 5), ['#3e6a42', '#4a7a4a', '#36603a'][rng.randint(3)])
    return im


def hs_slope(im):
    W = im.width
    a = np.array(im)
    rng = np.random.RandomState(103)
    for x in range(W):
        top = int(HS_SLOPE(x))
        for y in range(top, 142):
            k = (y - top) / max(1, 142 - top)
            b = BAYER[y % 4, x % 4]
            c = '#7aa652' if k + .25 * b < .2 else ('#6a9a48' if k + .2 * b < .6 else '#5e8e40')
            a[y, x] = (*c3(c), 255)
        if top < 142:
            a[top, x] = (*c3('#96c068'), 255)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    for _ in range(int(W * 1.6)):                                         # 坡上的草纹（顺着坡往下的短斜线）
        x = rng.randint(280, W)
        top = HS_SLOPE(x)
        y = rng.uniform(top + 2, 140)
        line(d, (x, y, x - 1, y + 2), ['#86b25c', '#527e38'][rng.randint(2)])
    return im


def hs_pond(im, x0=24, x1=262, y0=118, y1=142):
    d = ImageDraw.Draw(im)
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    ellipse(d, (x0 - 4, y0 - 3, x1 + 4, y1 + 3), '#8a7a58')               # 泥岸
    ellipse(d, (x0, y0, x1, y1), '#3e6a80')
    water = grad(new(im.width, H), (x0, y0, x1, y1 + 1), ('#6aa0bc', '#4a7e98', '#3e6a80'))
    mask = new(im.width, H)
    ImageDraw.Draw(mask).ellipse((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=(255, 255, 255, 255))
    im.paste(water, (0, 0), mask.getchannel('A'))
    d = ImageDraw.Draw(im)
    for x in range(int(x0 + 30), int(x1 - 30), 3):                        # 倒影里的山坡色
        px(d, x, y0 + 3 + (x % 2), '#7aa6b8')
    for lx, ly in ((70, 130), (96, 134), (180, 128), (204, 133)):         # 睡莲叶
        ellipse(d, (lx - 5, ly - 2, lx + 5, ly + 2), '#4a7a3e')
        line(d, (lx, ly, lx + 4, ly - 1), '#3e6a80')
    px(d, 98, 133, '#f4c0d0')
    px(d, 99, 133, '#f8e0e8')
    for rx_, h_ in ((x0 + 6, 18), (x0 + 12, 14), (x1 - 14, 16), (x1 - 8, 20), (x1 - 3, 12)):   # 芦苇
        for k in range(h_):
            px(d, rx_ + (k * k) / 120, y1 - k, '#6a8a3e' if k % 3 else '#86a24e')
        ellipse(d, (rx_ - 1 + h_ * h_ / 120, y1 - h_ - 4, rx_ + 1 + h_ * h_ / 120, y1 - h_), '#7a5a34')
    return im, (cx, cy, rx, ry)


def hs_fg(W):
    """前景：几丛高草（挡在人前面，画面最下沿）"""
    im = new(W, H)
    d = ImageDraw.Draw(im)
    for x, sd in ((14, 1), (150, 2), (318, 3), (486, 4), (620, 5), (774, 6), (930, 7)):
        for j in range(3):
            tuft(d, x + j * 6, 182, 16 + j * 3, cols=('#2e5a26', '#3e6a2e', '#5e8a3e'), seed=sd * 10 + j)
    return im


def hillside():
    W = 960
    fw = far_w(W)
    far = hs_far(fw)
    near = new(W, H)
    near = hs_slope(near)
    for x, h_, sd in ((560, 54, 1), (604, 42, 2), (820, 60, 3), (872, 48, 4), (930, 66, 5)):   # 坡顶的松树
        near = pine(near, x, int(HS_SLOPE(x)) + 4, h_, seed=sd + 100)
    d = ImageDraw.Draw(near)
    rng = np.random.RandomState(104)
    for _ in range(36):                                                   # 坡上的草丛
        x = rng.randint(300, W)
        top = HS_SLOPE(x)
        y = rng.uniform(top + 6, 136)
        tuft(d, x, y, rng.randint(5, 10), cols=('#3e6a2e', '#5e8a3e', '#7aa652'), seed=rng.randint(9999))
    rocks = {}
    for x, name, w_, h_ in HS_ROCKS:                                      # 岩石
        top = HS_SLOPE(x)
        y = int(min(138, top + 10 + (142 - top) * .35))
        rock(d, x, y, w_, h_, seed=x)
        rocks[name] = [x, y - h_ // 2]
        tuft(d, x - w_ // 2, y + 1, 6, seed=x + 1)
        tuft(d, x + w_ // 2 - 2, y + 1, 7, seed=x + 2)
    hide_x = 778                                                          # 老鼠藏身的那丛（r6 和 r7 之间）
    hide_y = int(HS_SLOPE(hide_x) + 14)
    for j in range(4):
        tuft(d, hide_x - 6 + j * 4, hide_y + 2, 12, cols=('#2e5a26', '#4a7a32', '#6a9a48'), seed=900 + j)
    # 平地：草 + 踩出来的土路
    near = grass_band(near, 0, W, 140, H, seed=105, density=5)
    d = ImageDraw.Draw(near)
    line(d, (0, 140, W, 140), '#86b058')
    near, (pcx, pcy, prx, pry) = hs_pond(near)
    d = ImageDraw.Draw(near)
    for x in range(0, W):                                                 # 土路
        y = 157 + 5 * math.sin(x / 160)
        for k in range(-5, 6):
            if abs(k) < 4 or (x + k) % 3:
                px(d, x, y + k, '#a88e68' if abs(k) < 4 else '#96805e')
    noise_specks(near, (0, 150, W, 164), ['#8a7254', '#b89c74'], 500, seed=106)
    d = ImageDraw.Draw(near)
    for i, x in enumerate(range(300, 262, -8)):                           # 脚印一路到池塘边断掉
        y = 148 + (2 if i % 2 else 0)
        rect(d, (x, y, x + 1, y + 1), '#5e4836')
        for tx_, ty_ in ((-1, -1), (1, -2), (3, -1)):
            px(d, x + tx_, y + ty_, '#5e4836')
    fg = hs_fg(W)
    # 池塘水面的闪光（6 帧）
    pw = int(prx * 2) - 40
    sh = new(pw * 6, 16)
    sd = ImageDraw.Draw(sh)
    rng = np.random.RandomState(107)
    glints = [(rng.uniform(4, pw - 8), rng.randint(3, 13), rng.randint(2, 6)) for _ in range(22)]
    for f in range(6):
        for gx, gy, L in glints:
            ph = (gx * 0.37 + gy) % 6
            if (f - ph) % 6 < 3:
                rel = abs(gx - pw / 2) / (pw / 2)                          # 椭圆外的不画
                if rel > .9 - abs(gy - 8) / 16:
                    continue
                X = (gx + f * 1.5) % (pw - L)
                line(sd, (f * pw + X, gy, f * pw + X + L, gy), '#cfe6f2')
    layers = {'far': far, 'near': near, 'fg': fg, 'pond': sh}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(pond=[int(pcx), 146], pond_edge=[262, 148], pond_water=[int(pcx), int(pcy)], tracks_end=[266, 150],
                             tracks_start=[300, 150], slope_foot=[300, 146], rat_hide=[hide_x, hide_y - 4],
                             walk_x=[8, 952], **rocks),
                layers=[{'type': 'pano', 'image': 'bg/hillside/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/hillside/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': 'bg/hillside/pond', 'n': 6, 'fps': 4, 'w': pw, 'h': 16,
                         'x': int(pcx - pw / 2), 'y': int(pcy - 8), 'k': 1},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[{'type': 'pano', 'image': 'bg/hillside/fg', 'k': 1, 'x': 0, 'y': 0}])
    pv = compose(far, near, w=W)
    pv.alpha_composite(sh.crop((0, 0, pw, 16)), (int(pcx - pw / 2), int(pcy - 8)))
    pv.alpha_composite(fg)
    preview('hillside', {'a': pv}, ['a'], W)
    save_layers('hillside', layers, meta)
    return meta


SCENES = {'rohan_house': rohan_house, 'rohan_studio': rohan_studio, 'irrigation_ditch': irrigation_ditch, 'farmhouse': farmhouse, 'farm_out': farm_out, 'hillside': hillside}


def main(keys):
    path = os.path.join(LIB.META, 'bg_ch5.json')
    meta = LIB.load_json(path, {}) or {}
    for k in keys or SCENES:
        meta[k] = SCENES[k]()
        print('背景', k)
    LIB.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
