# 第四部重画：更多室内部件（老洋房、学校、餐厅、医院、店铺用的）+ 光柱 / 光晕 / 弹孔这些叠加层。
#   尺寸照 第四部/docs/比例标准.md；by = 物件落地的那一行。
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from px import Cv, mix, shade, rgba
from bgkit import BAYER, FLOOR, rng, dither, shadow, block3, cabinet, old_lib


# ------------------------------------------------------------------ 叠加层
def shafts(w, polys=(), spots=(), col='#ffd696', k=0.34, blur=2, h=180, levels=7):
    """光柱 / 光斑的光晕层（lighter 混合）。polys = [[(x, y)…]…] 光柱多边形；spots = [(cx, cy, rx, ry, 强度)] 地上 / 灯下的光斑"""
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        d.polygon([(int(round(x)), int(round(y))) for x, y in p], fill=255)
    f = np.array(m.filter(ImageFilter.BoxBlur(blur))).astype(float) / 255 * k
    yy, xx = np.mgrid[0:h, 0:w]
    for (cx, cy, rx, ry, kk) in spots:
        dd = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        f += np.clip(1 - dd, 0, 1) ** 1.5 * kk
    q = np.clip(np.floor(f * levels + BAYER[yy % 4, xx % 4] * 0.9) / levels, 0, 1)
    cv = Cv(w, h)
    r, g, b, _ = rgba(col)
    for i, v in enumerate((r, g, b)):
        cv.a[..., i] = (q * v).astype(np.uint8)
    cv.a[..., 3] = np.where(q > 0, 255, 0).astype(np.uint8)
    return cv


def dust(w, h, n=12, count=16, seed=0):
    """光柱里的浮尘（n 帧循环的横条，w × h 一帧）：沿用旧库的画法"""
    import sys
    import os
    old_lib()
    import p4_bg_ch1 as B1
    return B1.dust_strip(w, h, n=n, count=count, seed=seed)


def bullet_holes(w, boxes, seed=0, h=180):
    """坏公司打出来的弹孔层：boxes = [(x0, y0, x1, y1, 个数, 是否地板)]"""
    old_lib()
    import p4_bg_ch1 as B1
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for i, (x0, y0, x1, y1, n, fl) in enumerate(boxes):
        B1.bullet_holes(im, n, (x0, y0, x1, y1), seed + i, floor=fl)
    return im


# ------------------------------------------------------------------ 老洋房
def grandfather_clock(cv, cx, by=FLOOR, c='#5a3a28', face='#e8dcc0'):
    """落地钟：2 m = 33 px"""
    cv.rect(cx - 4, by - 33, cx + 4, by, c)
    cv.vline(cx - 4, by - 33, by, shade(c, 0.2))
    cv.vline(cx + 4, by - 33, by, shade(c, -0.3))
    cv.rect(cx - 5, by - 35, cx + 5, by - 33, shade(c, 0.1))
    cv.put(cx, by - 36, shade(c, 0.1))
    cv.ellipse(cx, by - 28, 3, 3, face)
    cv.vline(cx, by - 30, by - 28, '#2a2a30')
    cv.hline(cx, cx + 1, by - 28, '#2a2a30')
    cv.rect(cx - 2, by - 22, cx + 2, by - 6, shade(c, -0.45))
    cv.vline(cx, by - 22, by - 12, '#c8a850')
    cv.ellipse(cx, by - 10, 1.4, 1.4, '#c8a850')
    cv.rect(cx - 5, by - 2, cx + 5, by, shade(c, -0.2))


def coat_rack(cv, cx, by=FLOOR, c='#4a3428', hat='#2a2a34'):
    cv.vline(cx, by - 30, by, c)
    cv.hline(cx - 3, cx + 3, by, c)
    cv.hline(cx - 3, cx + 3, by - 28, c)
    cv.put(cx - 3, by - 29, c)
    cv.put(cx + 3, by - 29, c)
    if hat:
        cv.rect(cx - 5, by - 31, cx - 1, by - 30, hat)
        cv.rect(cx - 4, by - 33, cx - 2, by - 32, hat)


def oval_mirror(cv, cx, cy, rx=4, ry=6, frame='#8a6a3a', glass='#9ab0c0', crack=True):
    cv.ellipse(cx, cy, rx + 1, ry + 1, frame)
    cv.ellipse(cx, cy, rx, ry, glass)
    cv.line(cx - 2, cy + 2, cx + 1, cy - 4, shade(glass, 0.35))
    if crack:
        cv.line(cx, cy - ry + 1, cx + 1, cy, '#2a3038')
        cv.line(cx + 1, cy, cx - 2, cy + ry - 2, '#2a3038')


def boarded_window(cv, x0, y0, x1, y1, frame='#4a3428', glass='#2a3038', board='#8a7050', light='#fff0c0', seed=0):
    """钉了木板的窗：板缝里漏光；返回漏光的缝 [(x0, y, x1)…]"""
    cv.rect(x0, y0, x1, y1, frame)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, glass)
    r = rng(seed)
    gaps = []
    y = y0 + 2
    while y < y1 - 2:
        hh = int(r.randint(3, 5))
        cv.rect(x0 - 1, y, x1 + 1, min(y1 - 1, y + hh - 1), shade(board, r.uniform(-0.15, 0.1)))
        cv.hline(x0 - 1, x1 + 1, y, shade(board, 0.2))
        y += hh
        if y < y1 - 2:
            cv.hline(x0 + 1, x1 - 1, y, light)
            gaps.append((x0 + 1, y, x1 - 1))
            y += 1
    return gaps


def arch(cv, cx, by=FLOOR, w=22, h=36, frame='#4a3428', inside='#18141a'):
    """拱形门洞（通另一间屋，里面是暗的）"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    cv.rect(x0 - 2, by - h + w // 2, x1 + 2, by, frame)
    cv.ellipse(cx - 0.5, by - h + w // 2, w / 2 + 2, w / 2 + 2, frame)
    cv.rect(x0, by - h + w // 2, x1, by, inside)
    cv.ellipse(cx - 0.5, by - h + w // 2, w / 2, w / 2, inside)
    return x0, by - h, x1, by


def doorway(cv, cx, by=FLOOR, w=17, h=34, frame='#4a3428', inside='#120e12'):
    """没有门扇的门洞（里面黑）"""
    x0 = cx - w // 2
    cv.rect(x0 - 2, by - h - 1, x0 + w + 1, by, frame)
    cv.rect(x0, by - h + 1, x0 + w - 1, by, inside)
    return x0, by - h + 1, x0 + w - 1, by


def balustrade(cv, x0, x1, y, h=14, c='#5a3a28', step=4):
    """栏杆（90 cm = 14–15 px），y = 立在哪一行"""
    cv.hline(x0, x1, y - h, shade(c, 0.2))
    cv.hline(x0, x1, y - h + 1, c)
    for x in range(x0 + 1, x1, step):
        cv.vline(x, y - h + 2, y, shade(c, -0.1))
    for x in (x0, x1):
        cv.rect(x - 1, y - h - 2, x + 1, y, c)
        cv.put(x, y - h - 3, shade(c, 0.2))


def ladder(cv, x, y0, y1, w=8, c='#7a5a3a'):
    cv.vline(x, y0, y1, c)
    cv.vline(x + w, y0, y1, shade(c, -0.2))
    for y in range(y0 + 2, y1, 4):
        cv.hline(x, x + w, y, shade(c, 0.1))


def stain(cv, cx, cy, w, h, c, seed=0, k=0.5):
    """墙上的霉斑 / 剥落：一团抖动的不规则色块"""
    r = rng(seed)
    for y in range(int(cy - h / 2), int(cy + h / 2) + 1):
        for x in range(int(cx - w / 2), int(cx + w / 2) + 1):
            d = ((x - cx) / (w / 2)) ** 2 + ((y - cy) / (h / 2)) ** 2
            if d < 1 and cv.inb(x, y) and r.rand() > d * 0.8 and k > BAYER[y % 4, x % 4] * (0.6 + d):
                cv.put(x, y, c)


# ------------------------------------------------------------------ 学校
def class_door(cv, cx, by=FLOOR, w=30, h=33, c='#a8845a', frame='#5a7a6a', glass='#b8d4e0', sign=None):
    """教室的双开推拉门（门上有玻璃）+ 门上的班牌"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    y0 = by - h + 1
    cv.rect(x0 - 2, y0 - 2, x1 + 2, by, frame)
    for a, b in ((x0, cx - 1), (cx, x1)):
        cv.rect(a, y0, b, by, c)
        cv.vline(a, y0, by, shade(c, 0.2))
        cv.rect(a + 3, y0 + 3, b - 3, y0 + 14, glass)
        cv.line(a + 4, y0 + 12, a + 7, y0 + 4, shade(glass, 0.3))
        cv.hline(a + 2, b - 2, by - 3, shade(c, -0.25))
    cv.vline(cx - 1, y0, by, shade(c, -0.35))
    cv.rect(cx - 3, by - 17, cx - 2, by - 14, '#3a3a40')
    cv.rect(cx + 1, by - 17, cx + 2, by - 14, '#3a3a40')
    if sign:
        from pfont import ptext
        cv.rect(cx - 9, y0 - 12, cx + 9, y0 - 5, '#f4f2ea')
        cv.hline(cx - 9, cx + 9, y0 - 5, '#a8a498')
        ptext(cv, cx - 7, y0 - 11, sign, '#2a2a30')
    return x0, y0, x1, by


def lockers(cv, x0, x1, by=FLOOR, h=30, c='#9aa8ac', cols=None, rows=2):
    """学校的铁皮储物柜（1.8 m）"""
    y0 = by - h
    cv.rect(x0, y0, x1, by, c)
    cv.hline(x0, x1, y0, shade(c, 0.3))
    n = cols or max(1, (x1 - x0 + 1) // 9)
    w = (x1 - x0 + 1) / n
    rh = (h - 1) / rows
    for i in range(n):
        a, b = int(x0 + i * w), int(x0 + (i + 1) * w) - 1
        cv.vline(b, y0, by, shade(c, -0.3))
        for j in range(rows):
            ya = int(y0 + 1 + j * rh)
            cv.hline(a, b, ya + int(rh) - 1, shade(c, -0.3))
            cv.hline(a + 2, b - 2, ya + 2, shade(c, -0.18))
            cv.hline(a + 2, b - 2, ya + 4, shade(c, -0.18))
            cv.put(b - 2, ya + int(rh / 2) + 1, '#3a3a44')
    cv.hline(x0, x1, by, shade(c, -0.45))
    shadow(cv, x0, x1, by + 1, 0.4, h=1)


def blackboard(cv, x0, x1, by=FLOOR, c='#2e5a48', frame='#8a6a44'):
    """黑板：下沿离地 14、上沿 34"""
    y0, y1 = by - 34, by - 14
    cv.rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1, frame)
    cv.rect(x0, y0, x1, y1, c)
    cv.rect(x0 - 1, y1 + 2, x1 + 1, y1 + 2, shade(frame, 0.2))
    r = rng(x0)
    for yy in (y0 + 3, y0 + 7, y0 + 11):
        x = x0 + 4
        while x < x1 - 14:
            ln = int(r.randint(3, 9))
            cv.hline(x, x + ln, yy, '#d8e8dc')
            x += ln + int(r.randint(2, 5))
    cv.rect(x0 + 4, y1 + 1, x0 + 7, y1 + 1, '#f4f4f0')
    cv.rect(x1 - 8, y1 + 1, x1 - 5, y1 + 1, '#e8c060')
    return x0, y0, x1, y1


def school_desk(cv, cx, by=FLOOR, c='#c8a878', leg='#8a8e96', chair=True, face=1, bag=None):
    """课桌（桌面 11）+ 课椅（椅面 5、椅背 13）"""
    if chair:
        hx = cx - face * 8
        cv.vline(hx - face * 3, by - 13, by, leg)
        cv.rect(min(hx - face * 3, hx - face * 1), by - 13, max(hx - face * 3, hx - face * 1), by - 10, shade(c, -0.1))
        cv.rect(hx - 3, by - 6, hx + 3, by - 5, shade(c, -0.05))
        cv.vline(hx + face * 3, by - 4, by, leg)
    cv.rect(cx - 6, by - 12, cx + 6, by - 11, shade(c, 0.18))
    cv.hline(cx - 6, cx + 6, by - 10, shade(c, -0.3))
    cv.rect(cx - 5, by - 9, cx + 5, by - 7, shade(c, -0.12))
    cv.vline(cx - 5, by - 9, by, leg)
    cv.vline(cx + 5, by - 9, by, leg)
    if bag:
        cv.rect(cx + 6, by - 7, cx + 8, by - 2, bag)


def podium(cv, cx, by=FLOOR, c='#a87a4a'):
    """讲台（1 m = 17 px）"""
    block3(cv, cx - 9, by - 17, cx + 9, by, c, 2)
    cv.rect(cx - 6, by - 12, cx + 6, by - 3, shade(c, -0.1))


# ------------------------------------------------------------------ 餐厅 / 厨房
def dining_table(cv, cx, by, w=30, cloth=('#f4f0e8', '#d04040'), leg='#5a3a28', h=11):
    """餐桌（桌面 11）铺格子桌布；返回桌面那一行 y"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    y0 = by - h
    cv.rect(x0, y0, x1, y0 + 1, cloth[0])
    for x in range(x0, x1 + 1):
        for y in range(y0 + 2, y0 + 5):
            cv.put(x, y, cloth[1] if ((x - x0) // 2 + (y - y0)) % 2 == 0 else cloth[0])
    cv.hline(x0, x1, y0 + 5, shade(cloth[0], -0.3))
    cv.rect(cx - 1, y0 + 6, cx, by, leg)
    cv.hline(cx - 4, cx + 3, by, leg)
    shadow(cv, x0 + 2, x1 - 2, by + 1, 0.4, h=1)
    return y0


def bistro_chair(cv, cx, by, face=1, c='#5a3a28', seat='#8a5a3a'):
    """餐椅侧面：椅面 5、椅背顶 13；face = 人坐上去面朝哪边"""
    bx = cx - face * 4
    cv.vline(bx, by - 13, by, c)
    cv.vline(bx + face, by - 13, by - 6, shade(c, 0.15))
    cv.hline(min(bx, bx + face * 2), max(bx, bx + face * 2), by - 13, shade(c, 0.2))
    cv.rect(cx - 4, by - 5, cx + 4, by - 4, seat)
    cv.hline(cx - 4, cx + 4, by - 3, shade(seat, -0.3))
    cv.vline(cx + face * 4, by - 3, by, c)


def wine_rack(cv, x0, x1, by=FLOOR, h=30, c='#5a3a28'):
    y0 = by - h
    cv.rect(x0, y0, x1, by, c)
    cv.hline(x0, x1, y0, shade(c, 0.25))
    for y in range(y0 + 2, by - 2, 5):
        for x in range(x0 + 2, x1 - 2, 5):
            cv.rect(x, y, x + 3, y + 3, shade(c, -0.45))
            cv.ellipse(x + 1.5, y + 1.5, 1.4, 1.4, ('#3a6a3a', '#6a2a3a', '#2a2a30')[(x + y) % 3])
            cv.put(x + 1, y + 1, '#c8d8c0')


def swing_door(cv, cx, by=FLOOR, w=22, h=34, c='#8a5a34', frame='#5a3a22'):
    """厨房的双开弹簧门（圆窗）"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    cv.rect(x0 - 2, by - h - 1, x1 + 2, by, frame)
    for a, b in ((x0, cx - 1), (cx, x1)):
        cv.rect(a, by - h + 1, b, by, c)
        cv.vline(a, by - h + 1, by, shade(c, 0.2))
        cv.ellipse((a + b) / 2, by - h + 9, 2.6, 2.6, '#e8e0c8')
        cv.rect(a + 2, by - 16, b - 2, by - 15, '#c8a850')
    cv.vline(cx - 1, by - h + 1, by, shade(c, -0.4))


def brick_oven(cv, cx, by=FLOOR, w=44, h=40, c='#a8583a', fire=True):
    """砖砌的烤炉；返回炉口 (x0, y0, x1, y1)"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    cv.rect(x0, by - h, x1, by, c)
    for j, y in enumerate(range(by - h, by, 3)):
        cv.hline(x0, x1, y, shade(c, -0.25))
        for x in range(x0 + (j % 2) * 4, x1, 8):
            cv.vline(x, y, y + 2, shade(c, -0.25))
    mx0, mx1, my0, my1 = cx - 9, cx + 9, by - 22, by - 9
    cv.rect(mx0, my0 + 4, mx1, my1, '#1a0e0c')
    cv.ellipse(cx, my0 + 5, 9.5, 6, '#1a0e0c')
    if fire:
        for i, x in enumerate(range(mx0 + 2, mx1 - 1, 3)):
            hh = 3 + (i * 7) % 4
            cv.vline(x, my1 - hh, my1, '#f08a30')
            cv.vline(x + 1, my1 - hh + 1, my1, '#ffd060')
    cv.rect(x0 - 1, by - 8, x1 + 1, by - 7, shade(c, 0.2))
    return mx0, my0, mx1, my1


def stove_range(cv, x0, x1, by=FLOOR, c='#3a3a44'):
    """商用炉灶（台面 14）"""
    block3(cv, x0, by - 14, x1, by, c, 2)
    for x in range(x0 + 4, x1 - 3, 9):
        cv.ellipse(x + 2, by - 7, 2, 2, '#c8ccd4')
        cv.put(x + 2, by - 7, '#6a6a74')
    cv.rect(x0 + 3, by - 4, x1 - 3, by - 3, '#8a8e98')
    for x in range(x0 + 3, x1 - 4, 10):
        cv.hline(x, x + 5, by - 15, '#1a1a20')


def pot(cv, cx, y, w=10, h=7, c='#b8bcc4'):
    """汤锅（y = 锅底）"""
    cv.rect(cx - w // 2, y - h, cx + w // 2, y, c)
    cv.hline(cx - w // 2 - 1, cx + w // 2 + 1, y - h, shade(c, 0.3))
    cv.vline(cx + w // 2, y - h + 1, y, shade(c, -0.3))
    cv.hline(cx - w // 2 + 1, cx + w // 2 - 1, y - h + 1, '#c8703a')
    cv.put(cx - w // 2 - 2, y - h + 2, c)
    cv.put(cx + w // 2 + 2, y - h + 2, c)


def jar_shelf(cv, x0, x1, y, c='#8a6a44', seed=0):
    cv.rect(x0, y, x1, y + 1, c)
    cv.hline(x0, x1, y + 1, shade(c, -0.3))
    cols = ['#d04040', '#e8c860', '#6a9a4a', '#f0e8d0', '#c8703a']
    for i, x in enumerate(range(x0 + 2, x1 - 3, 6)):
        col = cols[(i + seed) % len(cols)]
        cv.rect(x, y - 6, x + 3, y - 1, col)
        cv.hline(x, x + 3, y - 7, '#c8c8c0')
        cv.put(x, y - 5, shade(col, 0.35))


# ------------------------------------------------------------------ 医院 / 店铺
def bed(cv, x0, by, w=40, c='#f0f0ec', frame='#b8bcc4', blanket='#a8c8e0', head='left', h=5):
    """床：床面 5（加被子 7–8）、长 40；head = 床头在哪边"""
    x1 = x0 + w - 1
    cv.rect(x0, by - h - 2, x1, by - h, c)
    cv.rect(x0, by - h + 1, x1, by - 2, shade(frame, 0.1))
    cv.hline(x0, x1, by - 2, shade(frame, -0.3))
    hx = x0 if head == 'left' else x1
    cv.rect(hx - (0 if head == 'left' else 1), by - h - 9, hx + (1 if head == 'left' else 0), by, frame)
    fx = x1 if head == 'left' else x0
    cv.rect(fx - (1 if head == 'left' else 0), by - h - 5, fx + (0 if head == 'left' else 1), by, frame)
    px0 = x0 + 3 if head == 'left' else x1 - 10
    cv.rect(px0, by - h - 4, px0 + 7, by - h - 2, '#ffffff')
    bx0, bx1 = (x0 + 13, x1 - 2) if head == 'left' else (x0 + 2, x1 - 13)
    cv.rect(bx0, by - h - 3, bx1, by - h - 1, blanket)
    cv.hline(bx0, bx1, by - h - 3, shade(blanket, 0.25))
    for x in (x0 + 2, x1 - 2):
        cv.vline(x, by - 1, by, shade(frame, -0.35))
    shadow(cv, x0, x1, by + 1, 0.4, h=1)
    return x0, by - h - 3, x1, by


def bench(cv, x0, x1, by, c='#b08a5a', leg='#5a5a62', back=True):
    """长椅：椅面 5、靠背 13"""
    cv.rect(x0, by - 6, x1, by - 5, c)
    cv.hline(x0, x1, by - 4, shade(c, -0.3))
    if back:
        cv.rect(x0, by - 13, x1, by - 11, c)
        cv.hline(x0, x1, by - 10, shade(c, -0.3))
    for x in (x0 + 2, x1 - 2):
        cv.vline(x, by - (13 if back else 4), by, leg)


def counter(cv, x0, x1, by=FLOOR, h=15, c='#c8b088', top='#e8dcc0', panels=True):
    """柜台 / 服务台（90 cm = 15 px）"""
    block3(cv, x0, by - h, x1, by, c, 2)
    cv.rect(x0 - 1, by - h, x1 + 1, by - h + 1, top)
    cv.hline(x0 - 1, x1 + 1, by - h + 2, shade(top, -0.35))
    if panels:
        for x in range(x0 + 3, x1 - 8, 12):
            cv.rect(x, by - h + 5, x + 8, by - 3, shade(c, -0.08))
            cv.hline(x, x + 8, by - 3, shade(c, -0.25))
    shadow(cv, x0, x1, by + 1, 0.4, h=1)


def salon_chair(cv, cx, by, c='#c84a6a', base='#b8bcc4', face=1):
    """理发 / 美容椅：椅面 6、靠背顶 16"""
    cv.rect(cx - 1, by - 3, cx + 1, by, base)
    cv.hline(cx - 4, cx + 4, by, shade(base, -0.3))
    cv.rect(cx - 5, by - 7, cx + 5, by - 4, c)
    cv.hline(cx - 5, cx + 5, by - 7, shade(c, 0.25))
    bx = cx - face * 5
    cv.rect(min(bx, bx + face * 2), by - 16, max(bx, bx + face * 2), by - 7, c)
    cv.rect(min(bx, bx + face * 2), by - 19, max(bx, bx + face * 2), by - 17, shade(c, 0.15))
    cv.hline(cx - 5 if face < 0 else cx, cx + 5 if face > 0 else cx, by - 10, base)


def sewing_machine(cv, cx, by, c='#2a2a30'):
    """缝纫机 + 小桌（桌面 11）"""
    cv.rect(cx - 9, by - 12, cx + 9, by - 11, '#a87a4a')
    cv.hline(cx - 9, cx + 9, by - 10, '#6a4a2a')
    for x in (cx - 8, cx + 8):
        cv.vline(x, by - 10, by, '#5a5a62')
    cv.rect(cx - 6, by - 14, cx + 6, by - 13, c)
    cv.rect(cx + 3, by - 19, cx + 6, by - 14, c)
    cv.rect(cx - 6, by - 19, cx + 6, by - 18, c)
    cv.vline(cx - 5, by - 18, by - 15, '#c8ccd4')
    cv.put(cx + 5, by - 20, '#d04040')


def mannequin(cv, cx, by, c='#e8dcc8', dress='#7a4ab0'):
    """人台（1.6 m）"""
    cv.vline(cx, by - 8, by, '#5a5a62')
    cv.hline(cx - 3, cx + 3, by, '#5a5a62')
    cv.rect(cx - 3, by - 22, cx + 3, by - 8, dress)
    cv.rect(cx - 4, by - 20, cx + 4, by - 16, dress)
    cv.vline(cx - 3, by - 22, by - 8, shade(dress, -0.3))
    cv.rect(cx - 1, by - 25, cx + 1, by - 23, c)
    cv.put(cx, by - 26, '#8a6a44')


def clothes_rail(cv, x0, x1, by, seed=0):
    """挂衣杆（1.5 m）+ 一排衣服"""
    cv.hline(x0, x1, by - 25, '#8a8e96')
    for x in (x0, x1):
        cv.vline(x, by - 25, by, '#8a8e96')
        cv.hline(x - 2, x + 2, by, '#6a6e76')
    r = rng(seed)
    cols = ['#3a4a7a', '#7a4a3a', '#5a5a66', '#c8c0a8', '#2a2a34', '#6a7a5a', '#a84a5a']
    for x in range(x0 + 2, x1 - 4, 5):
        col = cols[int(r.randint(len(cols)))]
        hh = int(r.randint(12, 18))
        cv.rect(x, by - 24, x + 3, by - 24 + hh, col)
        cv.vline(x, by - 24, by - 24 + hh, shade(col, 0.2))
        cv.put(x + 1, by - 25, '#c8ccd4')


def tatami(cv, x0, x1, y0=FLOOR + 1, y1=179, c='#c8c088', edge='#4a5a3a'):
    """榻榻米地面"""
    cv.rect(x0, y0, x1, y1, c)
    cv.hline(x0, x1, y0, shade(c, -0.3))
    for y in range(y0 + 2, y1, 3):
        for x in range(x0 + (y % 2), x1, 2):
            cv.put(x, y, shade(c, -0.07))
    y = y0 + 12
    while y < y1:
        cv.hline(x0, x1, y, edge)
        y += 16
    for x in range(x0 + 30, x1, 70):
        cv.vline(x, y0, y1, edge)


def tokonoma(cv, x0, x1, by=FLOOR, top=None, wall_c='#d8cca8', post='#5a4028'):
    """和室的壁龛：一幅挂轴 + 花瓶"""
    top = top if top is not None else by - 40
    cv.rect(x0, top, x1, by, shade(wall_c, -0.12))
    cv.rect(x0, by - 3, x1, by, post)
    cv.vline(x0, top, by, post)
    cv.vline(x1, top, by, post)
    cx = (x0 + x1) // 2
    cv.rect(cx - 4, top + 5, cx + 4, by - 10, '#f0ead8')
    cv.rect(cx - 4, top + 5, cx + 4, top + 6, '#7a5a8a')
    cv.rect(cx - 4, by - 11, cx + 4, by - 10, '#7a5a8a')
    for yy in range(top + 10, by - 14, 4):
        cv.vline(cx, yy, yy + 2, '#3a3a40')
    cv.rect(x1 - 7, by - 9, x1 - 4, by - 4, '#3a5a6a')
    cv.put(x1 - 6, by - 11, '#d04a5a')
    cv.put(x1 - 5, by - 12, '#4a8a4a')
