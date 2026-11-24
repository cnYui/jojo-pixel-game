# 第四部重画：背景部件库。所有部件按 第四部/docs/比例标准.md 的尺寸画（站姿高度 1 px = 6 cm，成年人 30 px）。
#   画风沿用原来的背景：大色块 + 1 px 高光 / 阴影线 + 少量抖动，不描黑边（黑边留给人物和道具，人才跳得出来）。
#   坐标是图像坐标；by = 物件落地的那一行（靠墙的家具 = 墙脚线，通常 138；户外 = 地面线 150 上下）。
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from px import Cv, mix, shade, rgba, ASSETS, META, ensure

CM = 6.0                     # 1 px = 6 cm（站姿高度）
FLOOR = 138                  # 室内墙脚线
CEIL = 44                    # 住宅层高 44 px ≈ 2.6 m；学校 / 医院 / 商店用 50
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
WQY = None
for _fp in (r'C:\Windows\Fonts\simsun.ttc', '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'):
    if os.path.exists(_fp):
        WQY = _fp
        break


def cm(v):
    return int(round(v / CM))


def rng(seed):
    return np.random.RandomState(seed)


# ------------------------------------------------------------------ 基本笔触
def vgrad(cv, x0, y0, x1, y1, cols, dither=True):
    """竖向分段渐变（色阶之间 4×4 抖动）"""
    n = len(cols) - 1
    H = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        t = (y - y0) / H * n
        k = int(min(n - 1, math.floor(t)))
        f = t - k
        ca, cb = rgba(cols[k]), rgba(cols[k + 1])
        for x in range(max(0, x0), min(cv.w, x1 + 1)):
            if 0 <= y < cv.h:
                cv.a[y, x] = cb if (dither and f > BAYER[y % 4, x % 4]) or (not dither and f >= .5) else ca


def dither(cv, x0, y0, x1, y1, c, k=0.5):
    """按比例 k 把 c 撒在这一块上（半透明感的阴影 / 高光）"""
    col = rgba(c)
    for y in range(max(0, y0), min(cv.h, y1 + 1)):
        for x in range(max(0, x0), min(cv.w, x1 + 1)):
            if k > BAYER[y % 4, x % 4]:
                cv.a[y, x] = col


def box(cv, x0, y0, x1, y1, c, hi=None, lo=None, left=None, right=None):
    """色块 + 上沿高光 + 下沿阴影（+ 左右边线）"""
    cv.rect(x0, y0, x1, y1, c)
    if hi:
        cv.hline(x0, x1, y0, hi)
    if lo:
        cv.hline(x0, x1, y1, lo)
    if left:
        cv.vline(x0, y0, y1, left)
    if right:
        cv.vline(x1, y0, y1, right)


def block3(cv, x0, y0, x1, y1, c, top=2):
    """立着的家具：正面 + 上面一条亮的顶面（俯视一点点，看得见台面）"""
    cv.rect(x0, y0, x1, y0 + top - 1, shade(c, 0.22))
    cv.rect(x0, y0 + top, x1, y1, c)
    cv.hline(x0, x1, y0 + top, shade(c, -0.18))
    cv.hline(x0, x1, y1, shade(c, -0.3))
    cv.vline(x0, y0 + top, y1, shade(c, -0.14))


def shadow(cv, x0, x1, y, k=0.5, c='#000000', h=2):
    """贴地的投影（抖动）"""
    for i in range(h):
        col = rgba(c)
        for x in range(max(0, x0 + i), min(cv.w, x1 - i + 1)):
            if 0 <= y + i < cv.h and k * (1 - i * 0.4) > BAYER[(y + i) % 4, x % 4]:
                px0 = cv.a[y + i, x]
                cv.a[y + i, x] = (int(px0[0] * 0.72), int(px0[1] * 0.72), int(px0[2] * 0.78), 255)


def darken(cv, x0, y0, x1, y1, k=0.8, tint=(1.0, 1.0, 1.06)):
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(cv.w - 1, x1), min(cv.h - 1, y1)
    sub = cv.a[y0:y1 + 1, x0:x1 + 1].astype(float)
    for i in range(3):
        sub[..., i] = np.clip(sub[..., i] * k * tint[i], 0, 255)
    cv.a[y0:y1 + 1, x0:x1 + 1] = sub.astype(np.uint8)


def text(cv, x, y, s, c, size=12, font=None, bold=False):
    """点阵小字（招牌、门牌）。SimSun 12 px 不抗锯齿"""
    f = ImageFont.truetype(font or WQY, size)
    w = int(sum(f.getlength(ch) for ch in s)) + 2
    m = Image.new('L', (w, size + 4), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = '1'
    d.text((0, 0), s, font=f, fill=255)
    a = np.array(m)
    col = rgba(c)
    for yy in range(a.shape[0]):
        for xx in range(a.shape[1]):
            if a[yy, xx] > 127:
                cv.put(x + xx, y + yy, col)
                if bold:
                    cv.put(x + xx + 1, y + yy, col)
    return w


# ------------------------------------------------------------------ 天空 / 远景
SKY_DAY = ('#6ea8ea', '#8cc0f0', '#b0d6f4', '#d6eaf8')
SKY_EVE = ('#5a6ab0', '#b07aa0', '#f0a070', '#ffd090')
SKY_NIGHT = ('#0c1030', '#141c48', '#1e2a5c', '#2c3a70')
SKY_RAIN = ('#5a6478', '#6e7a8e', '#8792a4', '#9ca6b6')


def sky(cv, x0, x1, y1, cols=SKY_DAY, y0=0):
    vgrad(cv, x0, y0, x1, y1, cols)


def cloud(cv, x, y, w, seed=0, cols=('#ffffff', '#e8f0fa', '#c4d4ea')):
    r = rng(seed)
    n = max(3, w // 8)
    puffs = [(x + (i + .5) * w / n + r.uniform(-1.5, 1.5), y - r.uniform(1, 4), r.uniform(3, 6) * (1.2 if 0 < i < n - 1 else .8)) for i in range(n)]
    for cx, cy, rr in puffs:
        cv.ellipse(cx, cy + 2, rr, rr, cols[2])
    for cx, cy, rr in puffs:
        cv.ellipse(cx, cy, rr, rr, cols[1])
    for cx, cy, rr in puffs:
        cv.ellipse(cx - rr * .15, cy - rr * .25, rr * .7, rr * .6, cols[0])
    cv.hline(int(x + 2), int(x + w - 2), y + 3, cols[2])


# ------------------------------------------------------------------ 室内：墙、地板、天花
def wall(cv, x0, x1, c, y0=FLOOR - CEIL, y1=FLOOR, stripes=None, wains=None, base='#7a5a3c', crown=None):
    """后墙。stripes = (间距, 颜色) 竖条壁纸；wains = (高, 颜色) 护墙板；base = 踢脚线色"""
    cv.rect(x0, y0, x1, y1, c)
    if stripes:
        step, sc = stripes
        for x in range(x0 + step // 2, x1, step):
            cv.vline(x, y0, y1, sc)
    if wains:
        h, wc = wains
        cv.rect(x0, y1 - h, x1, y1, wc)
        cv.hline(x0, x1, y1 - h, shade(wc, 0.25))
        cv.hline(x0, x1, y1 - h + 1, shade(wc, -0.2))
        for x in range(x0 + 6, x1, 12):
            cv.vline(x, y1 - h + 2, y1 - 2, shade(wc, -0.12))
    if base:
        cv.rect(x0, y1 - 1, x1, y1, base)
        cv.hline(x0, x1, y1 - 1, shade(base, 0.2))
    if crown:
        cv.hline(x0, x1, y0, crown)
        cv.hline(x0, x1, y0 + 1, shade(crown, -0.2))
    # 天花和墙交界往下一格的暗影，墙面才有“在屋里”的深度
    dither(cv, x0, y0 + (2 if crown else 0), x1, y0 + (3 if crown else 1), shade(c, -0.22), 0.5)


def floor_wood(cv, x0, x1, y0=FLOOR + 1, y1=179, c='#c49660', seed=3):
    """木地板：越靠下（靠镜头）板越宽，接缝错开"""
    cv.rect(x0, y0, x1, y1, c)
    r = rng(seed)
    y = y0
    h = 3
    row = 0
    while y <= y1:
        tone = shade(c, (-0.06, 0.05, 0.0, -0.1)[row % 4])
        cv.rect(x0, y, x1, min(y1, y + h - 1), tone)
        cv.hline(x0, x1, min(y1, y + h - 1), shade(c, -0.24))
        x = x0 + int(r.randint(8, 40))
        while x < x1:
            cv.vline(x, y, min(y1, y + h - 2), shade(c, -0.24))
            x += int(r.randint(34, 70))
        y += h
        h = min(9, h + 1)
        row += 1
    cv.hline(x0, x1, y0, shade(c, -0.34))
    dither(cv, x0, y0 + 1, x1, y0 + 2, shade(c, -0.3), 0.5)


def floor_tile(cv, x0, x1, y0=FLOOR + 1, y1=179, c1='#e6dfcf', c2='#cfc6b2', size=10):
    """方砖地：近大远小的棋盘格"""
    y = y0
    h = 3
    row = 0
    while y <= y1:
        w = size + row * 3
        off = (row % 2) * w
        for x in range(x0 - 2 * w, x1 + w, w):
            k = ((x - x0 + off) // w) % 2
            cv.rect(max(x0, x + (row * 2)), y, min(x1, x + w - 1 + (row * 2)), min(y1, y + h - 1), c1 if k else c2)
        y += h
        h = min(10, h + 2)
        row += 1
    cv.hline(x0, x1, y0, shade(c2, -0.3))


def floor_plain(cv, x0, x1, y0=FLOOR + 1, y1=179, c='#b8b4ac', line=None, seed=5, specks=0):
    cv.rect(x0, y0, x1, y1, c)
    cv.hline(x0, x1, y0, shade(c, -0.3))
    dither(cv, x0, y0 + 1, x1, y0 + 2, shade(c, -0.22), 0.5)
    if line:
        y = y0 + 6
        step = 6
        while y < y1:
            cv.hline(x0, x1, y, line)
            step += 3
            y += step
    if specks:
        r = rng(seed)
        for _ in range(specks):
            cv.put(r.randint(x0, x1 + 1), r.randint(y0 + 2, y1 + 1), shade(c, r.choice([-0.12, 0.1])))


def rug(cv, x0, x1, y0, y1, c='#a8485a', edge='#e0b060', motif='#e0b060'):
    cv.rect(x0, y0, x1, y1, c)
    cv.hline(x0, x1, y0, edge)
    cv.hline(x0, x1, y1, shade(edge, -0.2))
    cv.vline(x0, y0, y1, edge)
    cv.vline(x1, y0, y1, edge)
    cy = (y0 + y1) // 2
    for x in range(x0 + 6, x1 - 4, 10):
        for d in range(3):
            cv.hline(x - (2 - d), x + (2 - d), cy - d, motif)
            cv.hline(x - (2 - d), x + (2 - d), cy + d, motif)


def ceiling_slab(cv, x0, x1, y, h=4, c='#6a4e36'):
    """天花上面那层楼板的剖面（切开的梁）"""
    cv.rect(x0, y - h, x1, y - 1, c)
    cv.hline(x0, x1, y - 1, shade(c, -0.3))
    cv.hline(x0, x1, y - h, shade(c, 0.2))
    for x in range(x0 + 4, x1, 16):
        cv.rect(x, y - h + 1, x + 1, y - 2, shade(c, -0.25))


def cut_wall(cv, x, y0, y1, w=3, c='#5a4636'):
    """被剖开的墙（房间之间、房子两头）：一条竖的深色截面"""
    cv.rect(x, y0, x + w - 1, y1, c)
    cv.vline(x, y0, y1, shade(c, 0.25))
    cv.vline(x + w - 1, y0, y1, shade(c, -0.3))


def lintel(cv, x0, x1, y, h, c, post=3):
    """两间屋之间的垂壁（门洞上面那一截墙）+ 两边的柱"""
    cv.rect(x0, y, x1, y + h - 1, c)
    cv.hline(x0, x1, y + h - 1, shade(c, -0.3))
    cv.hline(x0, x1, y + h, shade(c, -0.45))


# ------------------------------------------------------------------ 门窗
def door(cv, cx, by=FLOOR, w=17, h=34, c='#9a6e44', frame='#5e4028', knob='#e8c860', side=1, panel=True, glass=None, step=0):
    """平开门：门洞净宽 w（Q 版头宽，所以比真实比例宽）、高 h = 204 cm。side = 把手在哪边"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    y0 = by - h + 1
    cv.rect(x0 - 2, y0 - 2, x1 + 2, by, frame)
    cv.hline(x0 - 2, x1 + 2, y0 - 2, shade(frame, 0.25))
    cv.rect(x0, y0, x1, by, c)
    cv.vline(x0, y0, by, shade(c, 0.2))
    cv.vline(x1, y0, by, shade(c, -0.2))
    if panel:
        for (py0, py1) in ((y0 + 3, y0 + 13), (y0 + 17, by - 4)):
            cv.rect(x0 + 3, py0, x1 - 3, py1, shade(c, -0.1))
            cv.hline(x0 + 3, x1 - 3, py0, shade(c, -0.28))
            cv.vline(x0 + 3, py0, py1, shade(c, -0.28))
            cv.hline(x0 + 3, x1 - 3, py1, shade(c, 0.18))
    if glass:
        cv.rect(x0 + 3, y0 + 3, x1 - 3, y0 + 13, glass)
        cv.line(x0 + 4, y0 + 11, x0 + 8, y0 + 4, shade(glass, 0.4))
    kx = x1 - 2 if side > 0 else x0 + 2
    cv.rect(kx - 1, by - 17, kx, by - 16, knob)
    cv.put(kx, by - 15, shade(knob, -0.4))
    if step:
        cv.rect(x0 - 3, by + 1, x1 + 3, by + step, shade(frame, 0.3))
    return x0, y0, x1, by


def sliding_door(cv, cx, by=FLOOR, w=34, h=33, c='#ecebe2', frame='#6a4e36', leaves=2, kind='shoji'):
    """推拉门：障子（shoji）/ 襖（fusuma）/ 玻璃（glass）。两扇共宽 w"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    y0 = by - h + 1
    cv.rect(x0 - 2, y0 - 2, x1 + 2, by, frame)
    lw = w // leaves
    for i in range(leaves):
        a, b = x0 + i * lw, x0 + (i + 1) * lw - 1
        cv.rect(a, y0, b, by, c)
        cv.vline(a, y0, by, frame)
        if kind == 'shoji':
            for xx in range(a + 4, b, 4):
                cv.vline(xx, y0 + 1, by - 8, shade(c, -0.22))
            for yy in range(y0 + 5, by - 8, 5):
                cv.hline(a + 1, b, yy, shade(c, -0.22))
            cv.rect(a + 1, by - 7, b, by, shade(frame, 0.35))
        elif kind == 'glass':
            cv.rect(a + 2, y0 + 2, b - 1, by - 3, '#a8cce0')
            cv.line(a + 3, y0 + 10, a + 8, y0 + 3, '#d8ecf6')
            cv.hline(a + 2, b - 1, by - 14, frame)
        else:
            cv.rect(a + 1, by - 16, a + 2, by - 14, shade(frame, -0.2))
    cv.vline(x1, y0, by, frame)
    return x0, y0, x1, by


def window(cv, x0, y0, x1, y1, frame='#f4f0e4', glass=('#a6cce4', '#d4eaf6'), nx=2, ny=1, sill=True, view=None, curtain=None,
           rod=None):
    """窗：frame 窗框、glass 两色（斜向反光）、nx × ny 格。view = 画窗外的函数 fn(cv, gx0, gy0, gx1, gy1)。
    curtain = 颜色（两侧束起）；rod = 窗帘杆颜色"""
    cv.rect(x0, y0, x1, y1, frame)
    gx0, gy0, gx1, gy1 = x0 + 1, y0 + 1, x1 - 1, y1 - 1
    cv.rect(gx0, gy0, gx1, gy1, glass[0])
    if view:
        view(cv, gx0, gy0, gx1, gy1)
    else:
        for i in range(0, (gx1 - gx0), 9):
            cv.line(gx0 + i, gy1, gx0 + i + (gy1 - gy0) // 2, gy0, glass[1])
    for i in range(1, nx):
        xx = x0 + (x1 - x0) * i // nx
        cv.vline(xx, y0, y1, frame)
    for j in range(1, ny):
        yy = y0 + (y1 - y0) * j // ny
        cv.hline(x0, x1, yy, frame)
    cv.hline(x0, x1, y0, shade(frame, -0.15))
    cv.vline(x0, y0, y1, shade(frame, -0.1))
    if sill:
        cv.rect(x0 - 1, y1 + 1, x1 + 1, y1 + 2, shade(frame, -0.08))
        cv.hline(x0 - 1, x1 + 1, y1 + 2, shade(frame, -0.35))
    if curtain:
        cw = max(4, (x1 - x0) // 6)
        for sgn, xa in ((1, x0 - 1), (-1, x1 + 1 - cw + 1)):
            cv.rect(xa, y0 - 2, xa + cw - 1, y1 + 3, curtain)
            for xx in range(xa + 1, xa + cw, 2):
                cv.vline(xx, y0 - 1, y1 + 3, shade(curtain, -0.16))
            ty = y0 + (y1 - y0) * 2 // 3
            cv.hline(xa, xa + cw - 1, ty, shade(curtain, -0.35))
    if rod:
        cv.hline(x0 - 4, x1 + 4, y0 - 3, rod)
        cv.put(x0 - 5, y0 - 3, shade(rod, -0.3))
        cv.put(x1 + 5, y0 - 3, shade(rod, -0.3))


# ------------------------------------------------------------------ 家具（高度见比例标准：椅面 5、桌面 11、柜台 14、冰箱 28、门 34）
def sofa(cv, cx, by=FLOOR, w=46, c='#7a6ab8', seat=5, back=13, arm=9, cushion=None, legs='#4a3626'):
    """三人沙发：座面 5 px（Q 版小腿长）、靠背顶 13 px、扶手 9 px"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    cv.rect(x0 + 2, by - 1, x0 + 3, by, legs)
    cv.rect(x1 - 3, by - 1, x1 - 2, by, legs)
    # 靠背
    cv.rect(x0 + 3, by - back, x1 - 3, by - seat, shade(c, -0.06))
    cv.hline(x0 + 3, x1 - 3, by - back, shade(c, 0.28))
    n = 3 if w >= 40 else 2
    for i in range(1, n):
        xx = x0 + 3 + (w - 6) * i // n
        cv.vline(xx, by - back + 1, by - seat, shade(c, -0.3))
    # 座垫
    cv.rect(x0 + 3, by - seat - 1, x1 - 3, by - seat, shade(c, 0.2))
    cv.rect(x0 + 3, by - seat + 1, x1 - 3, by - 2, c)
    cv.hline(x0 + 3, x1 - 3, by - 2, shade(c, -0.3))
    for i in range(1, n):
        xx = x0 + 3 + (w - 6) * i // n
        cv.vline(xx, by - seat - 1, by - 2, shade(c, -0.25))
    # 扶手
    for a in (x0, x1 - 3):
        cv.rect(a, by - arm, a + 3, by - 2, shade(c, 0.06))
        cv.hline(a, a + 3, by - arm, shade(c, 0.3))
        cv.vline(a if a == x0 else a + 3, by - arm + 1, by - 2, shade(c, -0.25))
    if cushion:
        cv.rect(x0 + 6, by - seat - 6, x0 + 11, by - seat - 1, cushion)
        cv.hline(x0 + 6, x0 + 11, by - seat - 6, shade(cushion, 0.3))
        cv.vline(x0 + 11, by - seat - 5, by - seat - 1, shade(cushion, -0.25))
    shadow(cv, x0, x1, by + 1)
    return x0, by - back, x1, by


def armchair(cv, cx, by=FLOOR, c='#8a5a3a', w=16, **kw):
    return sofa(cv, cx, by, w=w, c=c, **kw)


def chair(cv, cx, by=FLOOR, c='#8a6240', seat=5, back=13, w=9, face=1, cushion=None):
    """餐椅 / 课椅（侧面朝 face 方向）：座面 5、椅背顶 13"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    bx = x0 if face > 0 else x1
    cv.vline(bx, by - back, by, c)
    cv.vline(bx + (1 if face > 0 else -1), by - back, by - seat, shade(c, -0.2))
    cv.hline(bx, bx + (2 if face > 0 else -2), by - back, shade(c, 0.25))
    cv.rect(x0, by - seat, x1, by - seat + 1, cushion or shade(c, 0.15))
    cv.hline(x0, x1, by - seat + 1, shade(cushion or c, -0.3))
    fx = x1 if face > 0 else x0
    cv.vline(fx, by - seat + 2, by, shade(c, -0.15))
    cv.hline(x0 + 1, x1 - 1, by - 2, shade(c, -0.25))


def table(cv, cx, by=FLOOR, w=30, h=11, c='#a87a4a', top=2, cloth=None, legs=2):
    """桌子：餐桌 / 书桌面高 11；矮桌 h = 6"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    y0 = by - h
    cv.rect(x0, y0, x1, y0 + top - 1, shade(cloth or c, 0.25))
    cv.hline(x0, x1, y0 + top, shade(cloth or c, -0.2))
    if cloth:
        cv.rect(x0, y0 + top, x1, y0 + top + 2, cloth)
        cv.hline(x0, x1, y0 + top + 2, shade(cloth, -0.25))
    for lx in (x0 + 1, x1 - legs):
        cv.rect(lx, y0 + top + 1, lx + legs - 1, by, shade(c, -0.12))
        cv.vline(lx + legs - 1, y0 + top + 1, by, shade(c, -0.35))
    shadow(cv, x0 + 1, x1 - 1, by + 1, 0.4, h=1)
    return x0, y0, x1, by


def cabinet(cv, x0, x1, by=FLOOR, h=14, c='#b89060', doors=None, top=2, handles='#6a4e30', drawers=0):
    """矮柜 / 柜台（h = 14 是站着用的台面高度 85 cm）"""
    y0 = by - h
    block3(cv, x0, y0, x1, by, c, top)
    n = doors or max(1, (x1 - x0 + 1) // 14)
    w = (x1 - x0 + 1) / n
    for i in range(n):
        a, b = int(x0 + i * w) + 1, int(x0 + (i + 1) * w) - 1
        ya = y0 + top + 2
        if drawers:
            dh = (by - 2 - ya) // drawers
            for k in range(drawers):
                cv.rect(a, ya + k * dh, b, ya + (k + 1) * dh - 2, shade(c, 0.08))
                cv.hline(a, b, ya + (k + 1) * dh - 2, shade(c, -0.25))
                cv.hline((a + b) // 2 - 1, (a + b) // 2 + 1, ya + k * dh + dh // 2 - 1, handles)
        else:
            cv.rect(a, ya, b, by - 2, shade(c, 0.08))
            cv.hline(a, b, by - 2, shade(c, -0.25))
            cv.vline(b, ya, by - 2, shade(c, -0.2))
            cv.vline(b - 2 if i % 2 == 0 else a + 2, ya + 3, ya + 5, handles)
    return x0, y0, x1, by


def wall_cabinet(cv, x0, x1, y0, y1, c='#e8dcc0', n=None, handles='#8a7650'):
    """吊柜：下沿 140 cm（by − 23）、上沿到天花"""
    cv.rect(x0, y0, x1, y1, c)
    cv.hline(x0, x1, y1, shade(c, -0.35))
    cv.hline(x0, x1, y0, shade(c, 0.2))
    n = n or max(1, (x1 - x0 + 1) // 13)
    w = (x1 - x0 + 1) / n
    for i in range(n):
        a, b = int(x0 + i * w) + 1, int(x0 + (i + 1) * w) - 1
        cv.rect(a, y0 + 1, b, y1 - 2, shade(c, 0.1))
        cv.vline(b, y0 + 1, y1 - 2, shade(c, -0.2))
        cv.hline(a, b, y1 - 2, shade(c, -0.2))
        cv.vline(b - 2 if i % 2 == 0 else a + 2, y1 - 6, y1 - 4, handles)


def fridge(cv, x0, by=FLOOR, w=12, h=28, c='#f2efe6'):
    """冰箱：170 cm = 28 px"""
    x1 = x0 + w - 1
    y0 = by - h
    cv.rect(x0, y0, x1, by, c)
    cv.hline(x0, x1, y0, shade(c, 0.3))
    cv.vline(x1, y0, by, mix(c, '#8088a8', 0.3))
    cv.vline(x0, y0, by, mix(c, '#8088a8', 0.15))
    cv.hline(x0, x1, y0 + 9, mix(c, '#606880', 0.45))
    cv.vline(x0 + 2, y0 + 4, y0 + 7, '#9aa0b0')
    cv.vline(x0 + 2, y0 + 12, y0 + 18, '#9aa0b0')
    cv.hline(x0, x1, by, mix(c, '#404860', 0.5))
    shadow(cv, x0, x1, by + 1, 0.4, h=1)
    return x0, y0, x1, by


def tv_crt(cv, cx, by=FLOOR, stand_h=8, w=14, h=11, c='#3a3a44', screen='#1c2a3a', stand='#8a6240', antenna=True, on=None):
    """90 年代的显像管电视（25 英寸，约 66 × 60 cm）放在 48 cm 高的电视柜上；返回屏幕框 (x0, y0, x1, y1)"""
    sw = w + 8
    sx0 = cx - sw // 2
    cabinet(cv, sx0, sx0 + sw - 1, by, stand_h, stand, doors=2, top=1)
    x0 = cx - w // 2
    x1 = x0 + w - 1
    y1 = by - stand_h - 1
    y0 = y1 - h + 1
    cv.rect(x0, y0, x1, y1, c)
    cv.hline(x0, x1, y0, shade(c, 0.3))
    cv.vline(x1, y0, y1, shade(c, -0.3))
    s = (x0 + 1, y0 + 1, x1 - 3, y1 - 2)
    cv.rect(*s, on or screen)
    if not on:
        cv.line(s[0] + 1, s[3] - 1, s[0] + 4, s[1] + 1, shade(screen, 0.25))
    cv.put(x1 - 1, y0 + 2, '#c04040')
    cv.put(x1 - 1, y0 + 4, '#8a8a94')
    cv.put(x1 - 1, y0 + 6, '#8a8a94')
    if antenna:
        cv.line(cx, y0 - 1, cx - 4, y0 - 7, '#8a8a94')
        cv.line(cx, y0 - 1, cx + 4, y0 - 7, '#8a8a94')
    return s


def bookshelf(cv, x0, x1, by=FLOOR, h=30, c='#8a6240', seed=1, rows=None, empty=0.1):
    """书架：180 cm = 30 px"""
    y0 = by - h
    cv.rect(x0, y0, x1, by, c)
    cv.hline(x0, x1, y0, shade(c, 0.25))
    cv.vline(x0, y0, by, shade(c, 0.1))
    cv.vline(x1, y0, by, shade(c, -0.3))
    r = rng(seed)
    n = rows or max(2, h // 7)
    rh = (h - 2) / n
    cols = ['#b04a3a', '#3a6a9a', '#d0a840', '#4a8a5a', '#8a5a9a', '#d8d0c0', '#c0703a', '#5a5a6a']
    for i in range(n):
        ya, yb = int(y0 + 1 + i * rh), int(y0 + 1 + (i + 1) * rh) - 2
        cv.rect(x0 + 1, ya, x1 - 1, yb, shade(c, -0.4))
        x = x0 + 1
        while x < x1 - 1:
            if r.rand() < empty:
                x += int(r.randint(2, 4))
                continue
            bh = int(r.randint(max(2, (yb - ya) - 2), (yb - ya) + 1))
            bw = int(r.choice([1, 1, 2]))
            col = cols[int(r.randint(len(cols)))]
            cv.rect(x, yb - bh + 1, min(x1 - 1, x + bw - 1), yb, col)
            if bw == 2:
                cv.vline(x + 1, yb - bh + 1, yb, shade(col, -0.2))
            x += bw
        cv.hline(x0 + 1, x1 - 1, yb + 1, shade(c, 0.12))
    return x0, y0, x1, by


def picture(cv, cx, cy, w=10, h=8, frame='#6a4a2a', art=('#8ab0d0', '#6a9a6a', '#e8d8a0')):
    x0, y0 = cx - w // 2, cy - h // 2
    cv.rect(x0, y0, x0 + w - 1, y0 + h - 1, frame)
    cv.hline(x0, x0 + w - 1, y0, shade(frame, 0.3))
    cv.rect(x0 + 1, y0 + 1, x0 + w - 2, y0 + h - 2, art[0])
    cv.rect(x0 + 1, y0 + h - 4, x0 + w - 2, y0 + h - 2, art[1])
    cv.put(x0 + w - 4, y0 + 2, art[2])
    return x0, y0, x0 + w - 1, y0 + h - 1


def clock(cv, cx, cy, r=3, face='#f4f0e0', rim='#6a4a2a', hands='#2a2a30'):
    cv.ellipse(cx, cy, r + 1, r + 1, rim)
    cv.ellipse(cx, cy, r, r, face)
    cv.vline(cx, cy - r + 1, cy, hands)
    cv.hline(cx, cx + r - 2, cy, hands)


def calendar(cv, cx, cy, w=8, h=10):
    x0, y0 = cx - w // 2, cy - h // 2
    cv.rect(x0, y0, x0 + w - 1, y0 + h - 1, '#f4f0e8')
    cv.rect(x0, y0, x0 + w - 1, y0 + 2, '#d04040')
    for yy in range(y0 + 4, y0 + h - 1, 2):
        for xx in range(x0 + 1, x0 + w - 1, 2):
            cv.put(xx, yy, '#8a8a90')
    cv.hline(x0, x0 + w - 1, y0 + h - 1, '#c0bcb0')


def plant(cv, cx, by=FLOOR, h=12, pot='#b0603a', leaf=('#2e6a3a', '#4a8a4a', '#74b060'), seed=0):
    r = rng(seed)
    ph = max(3, h // 4)
    cv.rect(cx - 2, by - ph, cx + 2, by, pot)
    cv.hline(cx - 3, cx + 3, by - ph, shade(pot, 0.2))
    cv.vline(cx + 2, by - ph + 1, by, shade(pot, -0.3))
    top = by - h
    for i in range(h * 2):
        a = r.uniform(0, math.pi)
        rr = r.uniform(1, h * 0.45)
        x, y = cx + math.cos(a) * rr * 1.1, by - ph - 1 - math.sin(a) * (h - ph - 1) * r.uniform(0.3, 1)
        cv.put(int(round(x)), int(round(max(top, y))), leaf[int(r.randint(3))])
    cv.vline(cx, by - ph - 3, by - ph - 1, leaf[0])


def lamp_ceiling(cv, cx, y, c='#f8f0c8', w=10, cord=3, on=True):
    cv.vline(cx, y, y + cord, '#5a5a60')
    cv.rect(cx - w // 2, y + cord + 1, cx + w // 2, y + cord + 3, c if on else '#c8c4b4')
    cv.hline(cx - w // 2 + 1, cx + w // 2 - 1, y + cord, shade(c, -0.3))
    cv.hline(cx - w // 2, cx + w // 2, y + cord + 3, shade(c, -0.25))


def phone_stand(cv, cx, by=FLOOR, c='#8a6240', phone='#e8e4d8'):
    table(cv, cx, by, w=10, h=11, c=c, legs=1)
    cv.rect(cx - 3, by - 14, cx + 3, by - 12, phone)
    cv.hline(cx - 3, cx + 3, by - 15, shade(phone, -0.25))
    cv.put(cx - 4, by - 14, shade(phone, -0.3))
    cv.put(cx + 4, by - 14, shade(phone, -0.3))


def switch(cv, x, y):
    cv.rect(x - 1, y - 1, x + 1, y + 1, '#f0ece0')
    cv.put(x, y, '#b0aca0')


def kitchen_counter(cv, x0, x1, by=FLOOR, c='#e8dcc0', top='#c8ccd0', sink_x=None, stove_x=None, tiles=('#f0f0ea', '#d8d8d0')):
    """厨房台面（85 cm = 14 px）+ 后墙瓷砖一条；sink_x / stove_x = 水槽、炉子的中心"""
    y0 = by - 14
    # 台面后的瓷砖墙：台面到吊柜下沿（by − 23）
    for yy in range(by - 23, y0):
        for xx in range(x0, x1 + 1):
            cv.put(xx, yy, tiles[0] if ((xx - x0) % 4 and (yy - y0) % 3) else tiles[1])
    cabinet(cv, x0, x1, by, 14, c, top=2)
    cv.rect(x0, y0, x1, y0 + 1, top)
    cv.hline(x0, x1, y0, shade(top, 0.3))
    cv.hline(x0, x1, y0 + 2, shade(top, -0.35))
    if sink_x is not None:
        cv.rect(sink_x - 5, y0, sink_x + 5, y0 + 1, '#8a9098')
        cv.hline(sink_x - 4, sink_x + 4, y0 + 1, '#6a7078')
        cv.vline(sink_x, y0 - 4, y0 - 1, '#b8bcc4')
        cv.hline(sink_x, sink_x + 2, y0 - 4, '#b8bcc4')
        cv.put(sink_x + 2, y0 - 3, '#b8bcc4')
    if stove_x is not None:
        cv.rect(stove_x - 6, y0 - 1, stove_x + 6, y0 + 1, '#3a3a40')
        cv.hline(stove_x - 6, stove_x + 6, y0 - 1, '#5a5a62')
        cv.put(stove_x - 3, y0, '#8a8a90')
        cv.put(stove_x + 3, y0, '#8a8a90')
    return x0, y0, x1, by


def range_hood(cv, cx, y0, w=16, c='#c8ccd0'):
    cv.rect(cx - w // 2 + 2, y0, cx + w // 2 - 2, y0 + 2, shade(c, 0.1))
    cv.rect(cx - w // 2, y0 + 3, cx + w // 2, y0 + 5, c)
    cv.hline(cx - w // 2, cx + w // 2, y0 + 5, shade(c, -0.35))


def kettle(cv, cx, y, c='#d8dce0'):
    """水壶（放在炉子上，y = 壶底）"""
    cv.rect(cx - 2, y - 3, cx + 2, y, c)
    cv.hline(cx - 1, cx + 1, y - 4, shade(c, -0.2))
    cv.put(cx + 3, y - 2, c)
    cv.put(cx, y - 5, '#2a2a30')
    cv.vline(cx - 2, y - 3, y, shade(c, 0.3))
    cv.hline(cx - 2, cx + 2, y, shade(c, -0.35))


def stairs(cv, x0, by, n, rise=3, run=5, c='#9a7248', dir=1, rail='#5e4028'):
    """侧面看的楼梯：n 级，每级升 rise、进 run；dir = 1 往右上"""
    for i in range(n):
        xa = x0 + dir * i * run
        xb = xa + dir * (run - 1)
        ya = by - (i + 1) * rise + 1
        cv.rect(min(xa, xb), ya, max(xa, xb), by, c)
        cv.hline(min(xa, xb), max(xa, xb), ya, shade(c, 0.28))
        cv.vline(xa if dir < 0 else xa, ya + 1, by, shade(c, -0.12))
    if rail:
        cv.line(x0, by - rise - 13, x0 + dir * n * run, by - (n + 1) * rise - 12, rail)
        for i in range(0, n, 2):
            xa = x0 + dir * i * run + dir * 2
            cv.vline(xa, by - (i + 1) * rise - 12, by - (i + 1) * rise, rail)


# ------------------------------------------------------------------ 保存
def save_layers(key, layers):
    """layers = {名字: Cv 或 Image}，写到 assets/bg/<key>/<名字>.png"""
    out = {}
    for name, im in layers.items():
        fp = ensure(os.path.join(ASSETS, 'bg', key, name + '.png'))
        img = im.img() if isinstance(im, Cv) else im
        img.save(fp)
        out[name] = img
    return out


def people_check(scene_img, figures, k=3, ground=150):
    """比例核对图：把几个人物的待机帧贴到场景上（figures = [(Sheet, x, y)…]），放大 k 倍"""
    from rig import OX, OY
    im = scene_img.convert('RGBA').copy()
    for sh, x, y in figures:
        f = sh.rows[0][1][0].img()
        im.alpha_composite(f, (int(x - OX), int(y - OY - 1)))
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


# ------------------------------------------------------------------ 房子外立面（户外场景，以及室内剖面图上半截的二楼外墙和屋顶）
def siding(cv, x0, y0, x1, y1, c='#e6dccb', step=4, corner=None):
    """外墙板：横向压条"""
    cv.rect(x0, y0, x1, y1, c)
    for y in range(y0 + step - 1, y1, step):
        cv.hline(x0, x1, y, shade(c, -0.12))
    cv.vline(x0, y0, y1, corner or shade(c, 0.12))
    cv.vline(x1, y0, y1, corner or shade(c, -0.22))


def roof_hip(cv, x0, x1, y_eave, y_ridge, c='#3e4a5e', inset=None, over=4):
    """四坡 / 两坡屋顶的正面：檐口 x0–x1（已含出檐 over），屋脊缩进 inset"""
    inset = inset if inset is not None else (y_eave - y_ridge)
    H = y_eave - y_ridge
    for i in range(H + 1):
        y = y_ridge + i
        k = 1 - i / max(1, H)
        a, b = int(round(x0 + inset * k)), int(round(x1 - inset * k))
        cv.hline(a, b, y, shade(c, 0.1 if i % 3 == 0 else (-0.08 if i % 3 == 2 else 0)))
        cv.put(a, y, shade(c, 0.3))
        cv.put(b, y, shade(c, -0.3))
    cv.hline(x0 + inset, x1 - inset, y_ridge, shade(c, 0.35))
    cv.hline(x0, x1, y_eave, shade(c, -0.4))
    cv.hline(x0 + 1, x1 - 1, y_eave + 1, shade(c, -0.55))


def roof_shed(cv, x0, x1, y_low, y_high, c='#3e4a5e', high_side='left'):
    """单坡披檐（下屋）"""
    W = x1 - x0
    for x in range(x0, x1 + 1):
        t = (x - x0) / max(1, W)
        yt = y_high + (y_low - y_high) * (t if high_side == 'left' else 1 - t)
        yt = int(round(yt))
        cv.vline(x, yt, yt + 3, c)
        cv.put(x, yt, shade(c, 0.3))
        cv.put(x, yt + 3, shade(c, -0.4))


def window_ext(cv, x0, y0, x1, y1, frame='#f0ece0', glass='#5a7a98', lit=None, nx=2, shutter=None, rail=None):
    """从外面看的窗：白天玻璃偏暗蓝、亮灯时暖黄（lit）"""
    cv.rect(x0, y0, x1, y1, frame)
    g = lit or glass
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, g)
    if not lit:
        cv.line(x0 + 2, y1 - 2, x0 + 2 + (y1 - y0) // 2, y0 + 2, shade(glass, 0.3))
    else:
        cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 2, shade(lit, 0.3))
    for i in range(1, nx):
        cv.vline(x0 + (x1 - x0) * i // nx, y0, y1, frame)
    cv.hline(x0 - 1, x1 + 1, y1 + 1, shade(frame, -0.3))
    if shutter:
        cv.rect(x0 - 4, y0, x0 - 1, y1, shutter)
        cv.rect(x1 + 1, y0, x1 + 4, y1, shutter)
        for y in range(y0 + 1, y1, 2):
            cv.hline(x0 - 4, x0 - 1, y, shade(shutter, -0.25))
            cv.hline(x1 + 1, x1 + 4, y, shade(shutter, -0.25))
    if rail:
        cv.hline(x0 - 3, x1 + 3, y1 - 4, rail)
        for x in range(x0 - 3, x1 + 4, 3):
            cv.vline(x, y1 - 4, y1 + 1, rail)


# ------------------------------------------------------------------ 背景元数据
def update_meta(key, anchors=None, layers=None, fg=None, **top):
    """改 assets/_meta/bg*.json 里这张背景的条目：anchors 合并进去；layers / fg = {图名（不带路径）: {字段: 值}} 按图名找到那一层改字段；
    其余关键字（w、walk……）直接覆盖。图层顺序、类型、开关键都不动——剧情脚本是按这些键开关图层的。"""
    import glob
    import json
    for fp in sorted(glob.glob(os.path.join(META, 'bg*.json'))):
        with open(fp, encoding='utf-8') as fh:
            d = json.load(fh)
        if key not in d:
            continue
        e = d[key]
        if anchors:
            e.setdefault('anchors', {}).update(anchors)
        for sec, patch in (('layers', layers), ('fg', fg)):
            for name, fields in (patch or {}).items():
                hit = [L for L in _walk_layers(e.get(sec, [])) if (L.get('image') or '').split('/')[-1] == name]
                if not hit:
                    raise KeyError('%s 的 %s 里没有图层 %s' % (key, sec, name))
                for L in hit:
                    L.update(fields)
        e.update(top)
        with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        return e
    raise KeyError('元数据里没有背景 ' + key)


def _walk_layers(Ls):
    for L in Ls:
        yield L
        if L.get('layers'):
            for s in _walk_layers(L['layers']):
                yield s


def old_lib():
    """旧背景库里的动效零件（雨丝、水花、樱花……）还能用：它们没有比例问题"""
    import sys
    p = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art'))
    if p not in sys.path:
        sys.path.insert(0, p)
    import p4_bglib
    return p4_bglib
