# 第四部背景的绘制零件：抖动渐变天空、云、樱花树、日式民宅、电线杆、围墙、树篱、人行道、马路……
#   画风对齐第三部 2026-10-11 体验版的背景（tools/bg_new）：大色块 + 2×2/4×4 抖动 + 1 px 高光 / 阴影线，不描黑边。
#   第三部的背景脚本依赖原工程，云端用不了，这里重写一套同风格的零件。
import math

import numpy as np
from PIL import Image, ImageDraw

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def c3(c):
    if isinstance(c, str):
        c = c.lstrip('#')
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in c[:3])


def C(c, a=255):
    return c3(c) + (a,)


def mix(a, b, k):
    a, b = c3(a), c3(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))


def new(w, h, col=None):
    return Image.new('RGBA', (w, h), C(col) if col else (0, 0, 0, 0))


def grad(img, box, cols, dither=True, horizontal=False):
    """box 里画分段渐变（cols = 几个色阶），色阶交界用 4×4 抖动过渡"""
    x0, y0, x1, y1 = [int(v) for v in box]
    a = np.array(img)
    n = len(cols) - 1
    L = (x1 - x0) if horizontal else (y1 - y0)
    for i in range(max(1, L)):
        t = i / max(1, L - 1) * n
        k = int(min(n - 1, math.floor(t)))
        f = t - k
        ca, cb = c3(cols[k]), c3(cols[k + 1])
        if horizontal:
            xs = x0 + i
            for y in range(y0, y1):
                use = cb if (dither and f > BAYER[y % 4, xs % 4]) or (not dither and f >= .5) else ca
                a[y, xs] = (*use, 255)
        else:
            y = y0 + i
            row = a[y, x0:x1]
            thr = BAYER[y % 4, np.arange(x0, x1) % 4]
            sel = (f > thr) if dither else np.full(x1 - x0, f >= .5)
            row[:] = (*ca, 255)
            row[sel] = (*cb, 255)
    return Image.fromarray(a, 'RGBA')


def rect(d, box, col, outline=None):
    d.rectangle([int(v) for v in box], fill=C(col) if col else None, outline=C(outline) if outline else None)


def line(d, pts, col, w=1):
    d.line([int(round(v)) for v in pts], fill=C(col), width=w)


def px(d, x, y, col):
    d.point((int(round(x)), int(round(y))), fill=C(col))


def ellipse(d, box, col):
    d.ellipse([int(round(v)) for v in box], fill=C(col))


def dither_fill(img, box, ca, cb, k):
    """box 里用比例 k 的抖动把 ca / cb 混在一起（做“半色”）"""
    x0, y0, x1, y1 = [int(v) for v in box]
    a = np.array(img)
    for y in range(max(0, y0), min(a.shape[0], y1)):
        for x in range(max(0, x0), min(a.shape[1], x1)):
            a[y, x] = (*(c3(cb) if k > BAYER[y % 4, x % 4] else c3(ca)), 255)
    return Image.fromarray(a, 'RGBA')


def noise_specks(img, box, cols, n, seed=1):
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for _ in range(n):
        px(d, rng.randint(x0, x1), rng.randint(y0, y1), cols[rng.randint(len(cols))])
    return img


# ---------------------------------------------------------------- 云
def cloud(img, x, y, w, seed=0, cols=('#ffffff', '#e8f0fa', '#c4d4ea')):
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(img)
    puffs = []
    n = max(3, int(w / 9))
    for i in range(n):
        cx = x + (i + .5) * w / n + rng.uniform(-2, 2)
        r = rng.uniform(4, 7) * (1.2 if 0 < i < n - 1 else .8)
        puffs.append((cx, y - r * .6, r))
    for cx, cy, r in puffs:                                   # 底下的阴影
        ellipse(d, (cx - r, cy - r + 2, cx + r, cy + r + 2), cols[2])
    for cx, cy, r in puffs:
        ellipse(d, (cx - r, cy - r, cx + r, cy + r), cols[1])
    for cx, cy, r in puffs:
        ellipse(d, (cx - r * .8, cy - r, cx + r * .5, cy + r * .3), cols[0])
    rect(d, (x + 2, y + 1, x + w - 2, y + 2), cols[2])
    return img


# ---------------------------------------------------------------- 樱花树（第三部同款：一团团的粉色圆块 + 亮面 + 抖动）
SAKURA = dict(d='#c86a94', m='#ec98bc', l='#f8bcd4', x='#ffe0ec', trunk='#4a2e2a', trunk2='#2e1c1c')


def sakura(img, cx, ground, h=96, w=70, seed=0, pal=SAKURA, petals=True):
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(img)
    top = ground - h
    # 树干和分叉
    tw = max(3, int(w / 16))
    rect(d, (cx - tw // 2, top + h * .45, cx + tw // 2, ground), pal['trunk'])
    line(d, (cx - tw // 2, top + h * .45, cx - tw // 2, ground), pal['trunk2'])
    for s in (-1, 1):
        line(d, (cx, top + h * .5, cx + s * w * .22, top + h * .3), pal['trunk'], 2)
        line(d, (cx + s * w * .1, top + h * .42, cx + s * w * .32, top + h * .36), pal['trunk'], 1)
    # 树冠：一大团重叠的圆块（先整体暗色剪影，再每块往左上错开叠中间色、亮色），像第三部那样连成一片
    blobs = []
    ccx, ccy, rx, ry = cx, top + h * .3, w * .44, h * .25
    n = int(w / 3.2)
    for i in range(n):
        ang = rng.uniform(0, 2 * np.pi)
        rr = np.sqrt(rng.uniform(0, 1))
        bx = ccx + np.cos(ang) * rx * rr
        by = ccy + np.sin(ang) * ry * rr
        r = rng.uniform(w * .12, w * .19)
        blobs.append((bx, by, r))
    blobs.sort(key=lambda b: b[1])
    for bx, by, r in blobs:
        ellipse(d, (bx - r, by - r * .82, bx + r, by + r * .82), pal['d'])
    for bx, by, r in blobs:
        ellipse(d, (bx - r * .95, by - r * .86, bx + r * .7, by + r * .5), pal['m'])
    for bx, by, r in blobs:
        if by < ccy + ry * .3:
            ellipse(d, (bx - r * .75, by - r * .8, bx + r * .25, by - r * .1), pal['l'])
    for bx, by, r in blobs[: max(3, n // 4)]:
        ellipse(d, (bx - r * .5, by - r * .72, bx - r * .1, by - r * .45), pal['x'])
    # 树冠下沿漏出的几根枝（用暗粉，不用黑）
    for _ in range(3):
        bx = cx + rng.uniform(-w * .25, w * .25)
        by = ccy + ry * .8
        line(d, (bx, by, bx + rng.uniform(-2, 2), by + 5), pal['trunk'])
    # 抖动的花瓣点
    if petals:
        for _ in range(int(w * 1.2)):
            x = cx + rng.uniform(-w * .55, w * .55)
            y = top + rng.uniform(0, h * .7)
            if img.getpixel((int(x), int(y)) if 0 <= x < img.width and 0 <= y < img.height else (0, 0))[3] > 0:
                px(d, x, y, pal['x'] if rng.rand() < .5 else pal['d'])
    return img


def fallen_petals(img, box, n, seed=0, cols=('#f8bcd4', '#ec98bc', '#ffe0ec')):
    return noise_specks(img, box, cols, n, seed)


# ---------------------------------------------------------------- 树篱 / 灌木
def hedge(img, x0, x1, y_top, y_bot, seed=0, cols=('#2e5a3a', '#4a7c4a', '#6e9e5a', '#94c070')):
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(img)
    rect(d, (x0, y_top + 4, x1, y_bot), cols[0])
    x = x0
    while x < x1:
        r = rng.uniform(5, 8)
        ellipse(d, (x - 1, y_top, x + r * 2, y_top + r * 1.6), cols[1])
        ellipse(d, (x + 1, y_top + 1, x + r * 1.3, y_top + r * .9), cols[2])
        px(d, x + r * .6, y_top + 2, cols[3])
        x += r * 1.5
    noise_specks(img, (x0, y_top + 6, x1, y_bot), [cols[2], cols[0]], int((x1 - x0) * (y_bot - y_top) / 14), seed + 1)
    return img


# ---------------------------------------------------------------- 墙、地面
def block_wall(img, x0, x1, y_top, y_bot, cols=('#c8c2b4', '#aaa496', '#8e887c', '#e0dacc')):
    """水泥砌块围墙：砌块缝 + 顶上压顶"""
    d = ImageDraw.Draw(img)
    rect(d, (x0, y_top, x1, y_bot), cols[0])
    rect(d, (x0, y_top, x1, y_top + 2), cols[3])
    line(d, (x0, y_top + 3, x1, y_top + 3), cols[2])
    bh = 8
    for i, y in enumerate(range(y_top + 4, y_bot, bh)):
        line(d, (x0, y + bh - 1, x1, y + bh - 1), cols[1])
        off = 0 if i % 2 else 10
        for x in range(x0 + off, x1, 20):
            line(d, (x, y, x, y + bh - 2), cols[1])
    # 水渍
    rng = np.random.RandomState(x0 + y_top)
    for _ in range(int((x1 - x0) / 30)):
        x = rng.randint(x0, max(x0 + 1, x1 - 4))
        for k in range(rng.randint(3, 8)):
            px(d, x + rng.randint(0, 2), y_top + 4 + k, cols[1])
    return img


def sidewalk(img, x0, x1, y0, y1, cols=('#b8b4ac', '#a4a098', '#cccac2', '#94908a')):
    d = ImageDraw.Draw(img)
    rect(d, (x0, y0, x1, y1), cols[0])
    for y in range(y0 + 6, y1, 9):
        line(d, (x0, y, x1, y), cols[1])
    for i, y in enumerate(range(y0, y1, 9)):
        for x in range(x0 + (0 if i % 2 else 12), x1, 24):
            line(d, (x, y, x - 3, y + 8), cols[1])
    line(d, (x0, y0, x1, y0), cols[2])
    return noise_specks(img, (x0, y0, x1, y1), [cols[1], cols[2]], int((x1 - x0) * (y1 - y0) / 30), y0)


def asphalt(img, x0, x1, y0, y1, cols=('#4e4e54', '#44444a', '#5a5a62', '#6a6a72'), line_col='#e8e4d8', dash=True):
    d = ImageDraw.Draw(img)
    rect(d, (x0, y0, x1, y1), cols[0])
    rect(d, (x0, y0, x1, y0 + 1), '#8a8a8e')            # 路缘石
    rect(d, (x0, y0 + 2, x1, y0 + 2), cols[1])
    noise_specks(img, (x0, y0 + 3, x1, y1), [cols[1], cols[2], cols[3]], int((x1 - x0) * (y1 - y0) / 6), y0 + 7)
    if dash:
        my = (y0 + y1) // 2 + 2
        for x in range(x0 + 4, x1, 32):
            rect(d, (x, my, x + 14, my), line_col)
    return img


# ---------------------------------------------------------------- 房子
def tiled_roof(img, x0, x1, y_top, y_bot, cols=('#3e4a5e', '#2e3848', '#56647a', '#1e2632'), overhang=4):
    """瓦屋顶（侧面看的梯形）：一行行瓦楞线 + 屋脊"""
    d = ImageDraw.Draw(img)
    h = y_bot - y_top
    for i in range(h + 1):
        k = i / max(1, h)
        xa = x0 - overhang * k + (1 - k) * 6
        xb = x1 + overhang * k - (1 - k) * 6
        line(d, (xa, y_top + i, xb, y_top + i), cols[0] if i % 3 else cols[1])
    rect(d, (x0 + 4, y_top - 2, x1 - 4, y_top), cols[3])
    line(d, (x0 + 4, y_top - 2, x1 - 4, y_top - 2), cols[2])
    for x in range(int(x0), int(x1), 4):
        px(d, x, y_top + h - 1, cols[2])
    line(d, (x0 - overhang, y_bot + 1, x1 + overhang, y_bot + 1), cols[3])
    return img


def window(d, box, frame='#e8e4dc', glass=('#9cc4dc', '#c8e2ee'), curtain=None, lit=None, bars=True):
    x0, y0, x1, y1 = [int(v) for v in box]
    rect(d, (x0, y0, x1, y1), frame)
    gx0, gy0, gx1, gy1 = x0 + 1, y0 + 1, x1 - 1, y1 - 1
    if lit:
        rect(d, (gx0, gy0, gx1, gy1), lit)
    else:
        rect(d, (gx0, gy0, gx1, gy1), glass[0])
        for i in range(0, gx1 - gx0, 5):
            line(d, (gx0 + i, gy0, min(gx1, gx0 + i + 3), gy0 + 3), glass[1])
    if curtain:
        rect(d, (gx0, gy0, gx0 + (gx1 - gx0) // 3, gy1), curtain)
    if bars:
        mx = (x0 + x1) // 2
        line(d, (mx, y0, mx, y1), frame)
    line(d, (x0, y1 + 1, x1, y1 + 1), '#7a7670')


def house(img, x, ground, w=96, h=70, wall='#e6dccb', wall2='#c8bca8', roof=None, door='#7a5a40', seed=0, two_story=True,
          lit=None, curtain='#e8b4a8'):
    """二层民宅（正面）：墙、两层窗、瓦屋顶、门、门灯。lit = 夜里窗户的灯色"""
    d = ImageDraw.Draw(img)
    rng = np.random.RandomState(seed)
    top = ground - h
    rect(d, (x, top, x + w, ground), wall)
    for yy in range(top + 2, ground, 4):                      # 外墙横纹
        line(d, (x, yy, x + w, yy), mix(wall, wall2, .35))
    rect(d, (x, top, x + 2, ground), wall2)
    rect(d, (x + w - 3, top, x + w, ground), wall2)
    roof = roof or ('#3e4a5e', '#2e3848', '#56647a', '#1e2632')
    tiled_roof(img, x, x + w, top - 16, top, roof)
    if two_story:
        mid = top + h // 2 - 2
        tiled_roof(img, x + 2, x + w - 2, mid - 4, mid, roof, overhang=3)
        for i in range(2):
            wx = x + 10 + i * (w // 2)
            window(d, (wx, top + 8, wx + 22, top + 24), glass=('#8eb8d2', '#c0dcea'), curtain=curtain if i else None, lit=lit)
    # 一楼：门 + 窗
    dx = x + w - 30
    rect(d, (dx, ground - 34, dx + 18, ground), door)
    rect(d, (dx + 2, ground - 32, dx + 16, ground - 2), mix(door, '#000000', .25))
    line(d, (dx + 9, ground - 32, dx + 9, ground - 2), mix(door, '#ffffff', .2))
    px(d, dx + 7, ground - 16, '#e8c860')
    px(d, dx + 11, ground - 16, '#e8c860')
    rect(d, (dx - 2, ground - 37, dx + 20, ground - 35), roof[1])
    window(d, (x + 8, ground - 30, x + 40, ground - 10), glass=('#8eb8d2', '#c0dcea'), curtain='#d8c8a0', lit=lit)
    rect(d, (x + 6, ground - 9, x + 42, ground - 8), wall2)
    return img


def pole(img, x, ground, h=120, cols=('#9a9488', '#7a756c', '#b8b2a6')):
    d = ImageDraw.Draw(img)
    top = ground - h
    rect(d, (x - 2, top, x + 2, ground), cols[0])
    line(d, (x - 2, top, x - 2, ground), cols[1])
    line(d, (x + 1, top, x + 1, ground), cols[2])
    for y in (top + 6, top + 14):
        rect(d, (x - 9, y, x + 9, y + 1), '#6a655e')
        for k in (-7, -2, 3, 8):
            rect(d, (x + k - 1, y - 2, x + k, y - 1), '#e8e4dc')
    rect(d, (x - 4, top + 30, x + 4, top + 40), '#5a5a5e')       # 变压器
    line(d, (x - 4, top + 30, x + 4, top + 30), '#7a7a80')
    for y in range(top + 50, ground - 20, 7):                     # 脚钉
        px(d, x + (3 if (y // 7) % 2 else -3), y, '#5a5650')
    return img


def wires(img, pts, sag=6, col='#2a2a30'):
    """几根电线：pts = 电线杆顶的 x 列表；每两根之间画下垂的弧"""
    d = ImageDraw.Draw(img)
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        for k in range(3):
            prev = None
            for i in range(0, 41):
                t = i / 40
                x = xa + (xb - xa) * t
                y = ya + (yb - ya) * t + sag * 4 * t * (1 - t) + k * 3
                if prev:
                    line(d, (prev[0], prev[1], x, y), col)
                prev = (x, y)
    return img


def vending(img, x, ground, body='#d8303a', accent='#f4f0e8'):
    """自动售货机（第三部 school_stairs 同款的红色）"""
    d = ImageDraw.Draw(img)
    rect(d, (x, ground - 40, x + 22, ground), body)
    rect(d, (x + 2, ground - 37, x + 20, ground - 20), accent)
    cols = ['#3a7ad8', '#f0c030', '#40b060', '#e05050', '#a060d0', '#f08a30']
    for r in range(3):
        for c in range(5):
            rect(d, (x + 3 + c * 3 + (c > 1), ground - 36 + r * 6, x + 4 + c * 3 + (c > 1), ground - 33 + r * 6), cols[(r * 5 + c) % 6])
            px(d, x + 3 + c * 3 + (c > 1), ground - 32 + r * 6, '#e04040')
    rect(d, (x + 3, ground - 17, x + 19, ground - 13), '#2a2a30')
    rect(d, (x + 15, ground - 11, x + 19, ground - 6), '#2a2a30')
    rect(d, (x + 3, ground - 9, x + 12, ground - 4), mix(body, '#000000', .3))
    line(d, (x, ground - 40, x + 22, ground - 40), mix(body, '#ffffff', .3))
    line(d, (x + 22, ground - 40, x + 22, ground), mix(body, '#000000', .35))
    return img


def bus_stop(img, x, ground, roof_col='#5a7a9a'):
    """公交站：站牌（圆牌 + 时刻表）+ 带棚的长椅"""
    d = ImageDraw.Draw(img)
    # 站牌
    rect(d, (x, ground - 46, x + 1, ground), '#8a8a90')
    ellipse(d, (x - 6, ground - 56, x + 7, ground - 43), '#f0f0f0')
    ellipse(d, (x - 5, ground - 55, x + 6, ground - 44), '#3a8a5a')
    rect(d, (x - 3, ground - 51, x + 4, ground - 48), '#f0f0f0')
    rect(d, (x - 4, ground - 38, x + 5, ground - 26), '#f4f4f0')
    for y in range(ground - 36, ground - 27, 2):
        line(d, (x - 3, y, x + 4, y), '#6a6a70')
    # 棚
    sx = x + 16
    rect(d, (sx, ground - 44, sx + 56, ground - 41), roof_col)
    line(d, (sx, ground - 44, sx + 56, ground - 44), mix(roof_col, '#ffffff', .35))
    for k in (2, 52):
        rect(d, (sx + k, ground - 41, sx + k + 1, ground), '#7a7a80')
    rect(d, (sx + 4, ground - 40, sx + 52, ground - 22), '#b8d0dc')          # 背后的玻璃
    for i in range(0, 48, 6):
        line(d, (sx + 5 + i, ground - 39, sx + 9 + i, ground - 35), '#dceaf0')
    rect(d, (sx + 8, ground - 14, sx + 48, ground - 12), '#a0765a')         # 长椅
    rect(d, (sx + 10, ground - 12, sx + 11, ground - 6), '#5a5a5e')
    rect(d, (sx + 45, ground - 12, sx + 46, ground - 6), '#5a5a5e')
    return img


def flower_pot_window(img, x, ground, lit=None):
    """窗台：窗户 + 窗台板（花盆另做道具，摔碎 / 修好两种状态）"""
    d = ImageDraw.Draw(img)
    window(d, (x, ground - 52, x + 28, ground - 30), glass=('#8eb8d2', '#c0dcea'), curtain='#f0d8a0', lit=lit)
    rect(d, (x - 3, ground - 29, x + 31, ground - 27), '#c8bca8')
    return img


def street_lamp(img, x, ground, h=70, on=False):
    d = ImageDraw.Draw(img)
    top = ground - h
    rect(d, (x, top, x + 1, ground), '#6a6e78')
    line(d, (x, top, x + 8, top - 4), '#6a6e78')
    rect(d, (x + 6, top - 5, x + 12, top - 3), '#4a4e58')
    rect(d, (x + 7, top - 3, x + 11, top - 2), '#fff4c0' if on else '#c8ccd4')
    return img


def tint(img, mul=(1, 1, 1), add=(0, 0, 0), desat=0.0):
    a = np.array(img).astype(float)
    rgb = a[..., :3]
    if desat:
        g = rgb.mean(axis=2, keepdims=True)
        rgb = rgb * (1 - desat) + g * desat
    rgb = rgb * np.array(mul) + np.array(add)
    a[..., :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def quantize_like(img, n=48):
    """限制颜色数（tint 之后颜色会散开）：保持像素风的色块感"""
    a = img.convert('RGBA')
    alpha = a.getchannel('A')
    q = a.convert('RGB').quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGBA')
    q.putalpha(alpha)
    return q


def rain_ground(img, y0, y1, seed=0, col='#9aa8c0'):
    """湿地面：竖向的倒影条纹 + 积水的亮边"""
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(img)
    for _ in range(int(img.width / 6)):
        x = rng.randint(0, img.width)
        y = rng.randint(y0, y1 - 4)
        ln = rng.randint(2, 6)
        line(d, (x, y, x, y + ln), col)
    return img


def puddle(img, cx, cy, w, h=4, cols=('#5a6a88', '#8a9ab8', '#c0cce0')):
    d = ImageDraw.Draw(img)
    ellipse(d, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), cols[0])
    line(d, (cx - w / 2 + 3, cy - h / 2 + 1, cx + w / 4, cy - h / 2 + 1), cols[1])
    px(d, cx - w / 4, cy, cols[2])
    return img


# ---------------------------------------------------------------- 雨（烘成循环帧条，给 bg.js 的 strip 图层用；第三部 india_alley 同样做法）
def rain_strip(w, h, n=10, near=70, far=50, length=(7, 4), slant=-0.22, cols=('#c8d4e8', '#8e9cb8'), alpha=(200, 140), seed=0):
    """横向 n 帧、每帧 w×h 的落雨。每滴雨在一圈 n 帧里正好落整数个周期，所以首尾接得上。
    近层长、亮、快（一圈落 2 次），远层短、暗、慢（一圈 1 次）。slant = 每往下 1 px 往左右偏多少。"""
    rng = np.random.RandomState(seed)
    out = Image.new('RGBA', (w * n, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    drops = []
    for i in range(near + far):
        is_near = i < near
        L = length[0] if is_near else length[1]
        drops.append(dict(x=rng.uniform(0, w), y=rng.uniform(0, h + L), L=L + rng.randint(0, 2), m=2 if is_near else 1,
                          col=C(cols[0] if is_near else cols[1], alpha[0] if is_near else alpha[1])))
    for f in range(n):
        for dr in drops:
            span = h + dr['L']
            y = (dr['y'] + f * dr['m'] * span / n) % span - dr['L']
            x = (dr['x'] + slant * y) % w
            x1, y1 = x + slant * dr['L'], y + dr['L']
            if x1 < 0 or x1 >= w:          # 画到帧外的那一截不要跨进隔壁帧
                continue
            d.line([(int(f * w + x), int(y)), (int(f * w + x1), int(y1))], fill=dr['col'])
    return out


def splash_strip(w, h, n=6, count=18, col='#c8d4e8', seed=0):
    """地面溅起的小水花（每个只亮 2 帧）：横向 n 帧"""
    rng = np.random.RandomState(seed)
    out = Image.new('RGBA', (w * n, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    for f in range(n):
        for _ in range(count):
            x, y = rng.randint(2, w - 3), rng.randint(2, h - 2)
            big = rng.rand() < .4
            ox = f * w
            d.point((ox + x - 1, y - 1), fill=C(col, 220))
            d.point((ox + x + 1, y - 1), fill=C(col, 220))
            d.point((ox + x, y), fill=C(col, 150))
            if big:
                d.point((ox + x - 2, y - 2), fill=C(col, 160))
                d.point((ox + x + 2, y - 2), fill=C(col, 160))
    return out


# ---------------------------------------------------------------- 松树（海边路的行道树）
def pine(img, x, ground, h=90, seed=0, cols=('#1e3a2e', '#2e5440', '#46705a', '#6a9478'), trunk=('#5a4234', '#3e2c22', '#7a5c48')):
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(img)
    top = ground - h
    # 弯一点的树干
    lean = rng.uniform(-8, 8)
    for i in range(h):
        t = i / h
        cx = x + lean * (1 - t) ** 2 * (t * 4)
        w = 2 + (1 - t) * 2
        y = ground - i
        rect(d, (cx - w / 2, y, cx + w / 2, y), trunk[0])
        px(d, cx - w / 2, y, trunk[1])
        if i % 7 == 3:
            px(d, cx, y, trunk[2])
    # 一层层横着的松针团：每团先暗剪影，再亮面往左上
    tiers = [(top + h * .04, h * .34), (top + h * .2, h * .46), (top + h * .38, h * .52)]
    for k, (ty, tw) in enumerate(tiers):
        cx = x + lean * .2 + rng.uniform(-4, 4) + (k - 1) * rng.uniform(-6, 6)
        blobs = [(cx + rng.uniform(-tw * .5, tw * .5), ty + rng.uniform(-2, 3), rng.uniform(tw * .24, tw * .36)) for _ in range(6)]
        for bx, by, r in blobs:
            ellipse(d, (bx - r, by - r * .45, bx + r, by + r * .45), cols[0])
        for bx, by, r in blobs:
            ellipse(d, (bx - r * .9, by - r * .5, bx + r * .6, by + r * .2), cols[1])
        for bx, by, r in blobs:
            ellipse(d, (bx - r * .7, by - r * .5, bx + r * .1, by - r * .1), cols[2])
        for bx, by, r in blobs[:2]:
            line(d, (bx - r * .5, by - r * .42, bx - r * .1, by - r * .42), cols[3])
        # 伸出来的枝
        line(d, (x + lean * .1, ty + 4, cx, ty + 2), trunk[1])
    return img


def phone_booth(img, x, ground):
    """九十年代的绿色公用电话亭"""
    d = ImageDraw.Draw(img)
    w, h = 18, 50
    top = ground - h
    rect(d, (x, top, x + w, ground), '#c8d8dc')
    rect(d, (x + 2, top + 6, x + w - 2, ground - 4), '#a8c4cc')
    for i in range(0, w - 4, 4):
        line(d, (x + 3 + i, top + 7, x + 6 + i, top + 10), '#dcecf0')
    rect(d, (x - 1, top - 3, x + w + 1, top + 2), '#4a8a5a')
    rect(d, (x + 3, top - 2, x + w - 3, top), '#e8f0e8')
    rect(d, (x + 5, top + 18, x + 13, top + 30), '#3a8a4a')                 # 绿色电话机
    rect(d, (x + 6, top + 19, x + 12, top + 21), '#2a6a3a')
    px(d, x + 7, top + 24, '#e8e8e0')
    px(d, x + 10, top + 24, '#e8e8e0')
    rect(d, (x, ground - 4, x + w, ground), '#8a9498')
    line(d, (x + w, top, x + w, ground), '#7a8a90')
    return img


def bevel(d, box, hi, lo):
    """1 px 的高光（左上）+ 阴影（右下）"""
    x0, y0, x1, y1 = [int(v) for v in box]
    line(d, (x0, y0, x1, y0), hi)
    line(d, (x0, y0, x0, y1), hi)
    line(d, (x0, y1, x1, y1), lo)
    line(d, (x1, y0, x1, y1), lo)


DIG = {'0': ['111', '101', '101', '101', '111'], '1': ['010', '110', '010', '010', '111'], '2': ['111', '001', '111', '100', '111'],
       '3': ['111', '001', '111', '001', '111'], '4': ['101', '101', '111', '001', '001'], '5': ['111', '100', '111', '001', '111'],
       '6': ['111', '100', '111', '101', '111'], '7': ['111', '001', '010', '010', '010'], '8': ['111', '101', '111', '101', '111'],
       '9': ['111', '101', '111', '001', '111']}


def digits(d, x, y, text, col):
    """3×5 的小数字（路牌、日历）"""
    for i, ch in enumerate(text):
        for r, row in enumerate(DIG.get(ch, ['000'] * 5)):
            for c, v in enumerate(row):
                if v == '1':
                    px(d, x + i * 4 + c, y + r, col)
