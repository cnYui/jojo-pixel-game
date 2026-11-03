# 第四部第1章（虹村家 / 弓与箭）的背景：4 张，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_ch1.json（build_p4.py 会把 _meta/bg_*.json 并进 bg.json）。
#   用法：python3 第四部/tools/art/p4_bg_ch1.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   图层 pack 一律 'ch1'（打包成 data/img_bg_ch1.js，进第1章时才加载）。
#   约定：高 180、ground 150、walk [142, 176]；平时对白框盖住 y 6–46，要指着说的东西放在 y 50 以下。
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import preview, save_layers  # noqa: E402

PACK = 'ch1'


# ============================================================ 共用零件
def poly(d, pts, col):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=C(col))


def kanji(im, x, y, text, col, vertical=False, size=12):
    """文泉驿点阵正黑 12 px（门牌用）；vertical = 竖排。返回 (宽, 高)"""
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


def comp(*ims):
    out = ims[0].copy()
    for im in ims[1:]:
        out.alpha_composite(im)
    return out


def add_glow(base, glow):
    """预览用：lighter 叠加"""
    pv = np.array(base).astype(int)
    g = np.array(glow).astype(int)
    pv[..., :3] = np.clip(pv[..., :3] + g[..., :3] * (g[..., 3:4] > 0), 0, 255)
    return Image.fromarray(pv.astype(np.uint8), 'RGBA')


def field_glow(f, col, levels=24):
    """强度场（0..1）→ lighter 叠加用的光图；分档硬过渡（像素画里的光柱）"""
    h, w = f.shape
    fq = np.round(np.clip(f, 0, 1) * levels) / levels
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * np.array(col, float), 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def shafts_field(W, polys, top, bottom, blur=2):
    """几块光柱多边形 → 强度场：从 top 往下先淡入、到 bottom 慢慢变淡"""
    m = Image.new('L', (W, 180), 0)
    md = ImageDraw.Draw(m)
    for p in polys:
        md.polygon([(int(round(x)), int(round(y))) for x, y in p], fill=255)
    sh = np.array(m.filter(ImageFilter.BoxBlur(blur))).astype(float) / 255 if blur else np.array(m).astype(float) / 255
    yy = np.mgrid[0:180, 0:W][0].astype(float)
    fall = np.clip(np.minimum((yy - top) / 24, 1) * (1 - .6 * np.clip((yy - top) / max(1, bottom - top), 0, 1)), 0, 1)
    return sh * fall, sh


def dust_strip(w, h, n=12, count=16, cols=('#fff2c8', '#ffd890'), region=None, seed=0):
    """光柱里浮着的灰尘：每粒沿一个小圈转、一圈正好 n 帧（首尾接得上）。region(x, y) → True 的位置才放"""
    rng = np.random.RandomState(seed)
    out = Image.new('RGBA', (w * n, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    motes = []
    tries = 0
    while len(motes) < count and tries < 6000:
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
            d.point((int(f * w + X), int(Y)), fill=C(cols[ci], 255 if b > .7 else 160))
    return out


def bullet_holes(im, n, box, seed, rim='#8a8070', dark='#120e0c', clusters=6, floor=False):
    """坏公司的小弹孔：一簇一簇的黑点 + 左上一像素亮边（墙皮崩开）+ 偶尔一道细裂纹。floor = 地板上的（扁一点）"""
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    x0, y0, x1, y1 = box
    centers = [(rng.uniform(x0, x1), rng.uniform(y0, y1)) for _ in range(clusters)]
    for i in range(n):
        cx, cy = centers[i % clusters]
        x = int(cx + rng.normal(0, 7))
        y = int(cy + rng.normal(0, 3 if floor else 6))
        if not (x0 <= x < x1 and y0 <= y < y1):
            continue
        px(d, x, y, dark)
        if rng.rand() < .6:
            px(d, x + 1, y, dark)
        px(d, x - 1, y - 1, rim)
        if not floor:
            px(d, x, y - 1, rim) if rng.rand() < .5 else None
        if rng.rand() < .25:
            dx, dy = rng.choice([-1, 1]), rng.choice([-1, 1])
            for k in range(2, 4):
                px(d, x + dx * k, y + dy * (k // 2), mix(dark, rim, .5))
    return im


def wood_floor(im, x0, x1, G, tones, seam, grain, hi, seed=5, dust=None):
    """木地板（同序章 liv_floor 的画法，颜色可换）：越往下木条越宽；接缝错开；dust = 灰尘色（零星的点）"""
    d = ImageDraw.Draw(im)
    y, h, row = G, 3.0, 0
    rng = np.random.RandomState(seed)
    while y < 180:
        yb = min(180, int(round(y + h)))
        rect(d, (x0, int(y), x1, yb - 1), tones[row % len(tones)])
        line(d, (x0, yb - 1, x1, yb - 1), seam)
        plank = int(40 + h * 6)
        off = rng.randint(0, plank)
        for x in range(x0 - off, x1, plank):
            if x > x0:
                line(d, (x, int(y), x, yb - 2), seam)
                px(d, x + 1, int(y), hi)
        for _ in range(int((x1 - x0) / 18)):
            gx = rng.randint(x0, x1 - 6)
            gy = rng.randint(int(y), max(int(y) + 1, yb - 1))
            line(d, (gx, gy, gx + rng.randint(2, 6), gy), grain if row % 2 else hi)
        y += h
        h = min(9.0, h * 1.18)
        row += 1
    if dust:
        noise_specks(im, (x0, G + 2, x1, 180), dust, int((x1 - x0) * (180 - G) / 90), seed + 3)
    return dither_fill(im, (x0, G, x1, G + 2), seam, tones[0], .5)


def debris(im, box, n, seed, cols=('#b4a88a', '#8a7e64', '#d8ccb0', '#6a5a46')):
    """墙皮碎块、纸屑：2–3 px 的小块"""
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rng.randint(x0, x1), rng.randint(y0, y1)
        c = cols[rng.randint(len(cols))]
        w, h = rng.randint(1, 4), rng.randint(1, 3)
        rect(d, (x, y, x + w - 1, y + h - 1), c)
        px(d, x, y + h, mix(c, '#000000', .45))
    return im


# ============================================================ 虹村家前院 nijimura_yard（640 宽，放学后的下午）
#   左：马路边的人行道 + 电线杆；后面一道红砖矮墙加生锈的铁栅栏，中间是铁门（门柱上竖着门牌「虹村」，能开关：pick 层 key 'gate'）。
#   墙在 x 200 附近塌了一截（碎砖堆：亿泰削墙角扔砖从这里来），往右就是满院杂草的前院：
#   花盆架（6 个花盆，砸掉几个：pick 层 key 'pots_gone'）→ 门廊和正门 → 枯树、油桶、后面的砖墙。
#   后面是两层的旧洋馆：剥落的米色护墙板、深色石板屋顶；二楼左边那扇窗挂着发黄的窗帘（形兆射箭的窗：key 'figure' 窗帘后人影）。
YD = dict(wall='#cdbf9e', wall2='#b6a684', wall3='#a29270', stain='#8e8062', trim='#5a4434', trim2='#7a5e46', trimhi='#94765a',
          roof=('#4e4248', '#3e343a', '#6a5c62', '#2a2228'), glass='#323c46', glass2='#4e5e6a', glass3='#7e8e96',
          brick=('#8e4c3a', '#a25c46', '#743e30', '#5e3226'), iron='#2e2624', rust='#7a4228', rust2='#a05a34',
          dirt='#7a7050', grass=('#56683a', '#6a7c42', '#80904c', '#9aa45a'), dry='#b0a466')


def yard_far():
    """远景（k 0.5，宽 480）：偏灰的下午天、几朵云、远处的山和一排树、零星屋顶"""
    W = 480
    im = new(W, 180, '#d8d6cc')
    im = grad(im, (0, 0, W, 112), ('#7ea2c8', '#98b6d0', '#b8cad8', '#d6d6cc'))
    rng = np.random.RandomState(3)
    for i in range(4):
        cloud(im, rng.randint(0, W - 50), rng.randint(14, 44), rng.randint(30, 60), seed=30 + i,
              cols=('#f4f2ea', '#dcdcd6', '#b6bcc6'))
    d = ImageDraw.Draw(im)
    for x in range(W):
        y = 88 + 8 * np.sin(x / 70 + 1) + 3 * np.sin(x / 19.0)
        line(d, (x, int(y), x, 130), '#8ea2ac')
        px(d, x, int(y), '#a6b8c0')
    for i in range(int(W / 12)):                                          # 远处一排树
        x = rng.randint(-8, W)
        r = rng.randint(6, 12)
        y = 104 + rng.randint(-4, 4)
        ellipse(d, (x - r, y - r, x + r, y + r + 20), ['#4e6a50', '#5a7656', '#46604a'][rng.randint(3)])
        ellipse(d, (x - r + 2, y - r + 1, x + r - 4, y), '#6a8662')
    for i in range(10):                                                   # 零星的屋顶
        x = rng.randint(0, W)
        bw, bh = rng.randint(12, 22), rng.randint(6, 12)
        y = 116 - bh
        rect(d, (x, y, x + bw, 130), ['#d8d0c4', '#e2dace', '#c8c0b2'][rng.randint(3)])
        rect(d, (x - 1, y - 3, x + bw + 1, y), ['#6a5a5a', '#5a6a7a', '#7a6a62'][rng.randint(3)])
    rect(d, (0, 122, W, 180), '#5e6e4a')
    return im


def slate_roof(im, pts, cols, seed=0):
    """石板屋顶：多边形里按 3 px 一行铺，错缝的竖短线，偶尔缺一块"""
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).polygon([(int(x), int(y)) for x, y in pts], fill=255)
    a = np.array(m) > 0
    out = np.array(im)
    rng = np.random.RandomState(seed)
    ys, xs = np.where(a)
    for y, x in zip(ys, xs):
        r = y // 3
        c = cols[0]
        if y % 3 == 2:
            c = cols[1]
        elif (x + (r % 2) * 4) % 8 == 0:
            c = cols[1]
        out[y, x] = (*c3(c), 255)
    img = Image.fromarray(out, 'RGBA')
    d = ImageDraw.Draw(img)
    for _ in range(int(a.sum() / 260)):                                   # 掉了的石板、青苔
        i = rng.randint(len(xs))
        x, y = xs[i], ys[i] // 3 * 3
        rect(d, (x, y, x + 3, y + 1), cols[3] if rng.rand() < .6 else '#5a6a44')
    return img


def sash_window(d, x0, y0, w, h, P, broken=False, boarded=False, shutter=None):
    """洋馆的上下推拉窗：深色窗框、脏玻璃、十字窗棂；broken = 碎了一块；boarded = 钉了木板；shutter = 'l' / 'r' 歪着的百叶"""
    x1, y1 = x0 + w, y0 + h
    rect(d, (x0 - 2, y0 - 3, x1 + 2, y0 - 1), P['trim'])                     # 窗楣
    line(d, (x0 - 2, y0 - 3, x1 + 2, y0 - 3), P['trimhi'])
    rect(d, (x0, y0, x1, y1), P['trim2'])
    rect(d, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), P['glass'])
    for i in range(0, w, 6):                                               # 脏玻璃上的反光
        line(d, (x0 + 2 + i, y0 + 2, min(x1 - 2, x0 + 5 + i), y0 + 5), P['glass2'])
    my = (y0 + y1) // 2
    rect(d, (x0, my - 1, x1, my), P['trim2'])
    line(d, ((x0 + x1) // 2, y0, (x0 + x1) // 2, y1), P['trim2'])
    if broken:
        bx, by = x0 + w // 4, my + 3
        poly(d, [(bx, by), (bx + 5, by - 1), (bx + 3, by + 4), (bx + 6, by + 8), (bx, by + 7)], '#0e0c0e')
        line(d, (bx + 5, by - 1, bx + 7, by - 3), P['glass3'])
    rect(d, (x0 - 3, y1 + 1, x1 + 3, y1 + 2), P['trim'])                    # 窗台
    line(d, (x0 - 3, y1 + 1, x1 + 3, y1 + 1), P['trimhi'])
    if boarded:
        for k, (a, b) in enumerate(((y0 + 4, y0 + 8), (my + 2, my - 4), (y1 - 7, y1 - 4))):
            poly(d, [(x0 - 3, a), (x1 + 3, b), (x1 + 3, b + 4), (x0 - 3, a + 4)], '#8a7658' if k % 2 else '#7a684e')
            line(d, (x0 - 3, a, x1 + 3, b), '#a08a68')
            px(d, x0 - 1, a + 2, '#3a3030')
            px(d, x1 + 1, b + 2, '#3a3030')
    if shutter:
        sx = x0 - 9 if shutter == 'l' else x1 + 3
        rect(d, (sx, y0 + 2, sx + 6, y1 + 3), '#5a6a5e')
        for y in range(y0 + 4, y1 + 2, 3):
            line(d, (sx + 1, y, sx + 5, y), '#46544a')
        line(d, (sx, y0 + 2, sx, y1 + 3), '#6e8072')


def nj_house(im, x0=150, x1=560, base=122):
    """虹村家（正面）：两层旧洋馆，护墙板 + 石板屋顶 + 中间一个山墙，右边门廊"""
    P = YD
    d = ImageDraw.Draw(im)
    top = 36
    rect(d, (x0, top, x1, base), P['wall'])
    for y in range(top + 3, base, 4):                                      # 护墙板
        line(d, (x0, y, x1, y), P['wall2'])
    rng = np.random.RandomState(11)
    for _ in range(46):                                                    # 剥落的漆、水渍往下流
        x = rng.randint(x0 + 4, x1 - 4)
        y = rng.randint(top + 2, base - 20)
        L = rng.randint(4, 18)
        c = P['stain'] if rng.rand() < .6 else P['wall3']
        for k in range(L):
            px(d, x + (k // 7), y + k, c)
    for _ in range(14):
        x, y = rng.randint(x0 + 6, x1 - 16), rng.randint(top + 6, base - 10)
        rect(d, (x, y, x + rng.randint(4, 10), y + rng.randint(2, 4)), P['wall3'])
    rect(d, (x0, top, x0 + 3, base), P['trim2'])                            # 转角板
    rect(d, (x1 - 3, top, x1, base), P['trim2'])
    rect(d, (x0, 78, x1, 81), P['trim'])                                    # 一二楼之间的腰线
    line(d, (x0, 78, x1, 78), P['trimhi'])
    rect(d, (x0, base - 6, x1, base), '#8a8478')                           # 石砌墙脚
    for x in range(x0, x1, 9):
        line(d, (x, base - 6, x, base), '#6e6a60')
    line(d, (x0, base - 6, x1, base - 6), '#a8a294')
    # 屋顶：檐口 + 四坡石板顶（上面出画）+ 中间山墙
    roof_pts = [(x0 - 10, top), (x0 + 30, -4), (x1 - 30, -4), (x1 + 10, top)]
    im2 = slate_roof(im, roof_pts, P['roof'], seed=12)
    im.paste(im2)
    d = ImageDraw.Draw(im)
    rect(d, (x0 - 10, top - 2, x1 + 10, top + 3), P['trim'])
    line(d, (x0 - 10, top - 2, x1 + 10, top - 2), P['trimhi'])
    for x in range(x0 - 8, x1 + 10, 8):                                   # 檐下托架
        rect(d, (x, top + 3, x + 2, top + 6), P['trim'])
    gx0, gx1 = 372, 470
    gm = (gx0 + gx1) // 2
    poly(d, [(gx0 - 6, top + 1), (gm, -10), (gx1 + 6, top + 1)], P['trim'])
    poly(d, [(gx0, top), (gm, -4), (gx1, top)], P['wall'])
    for y in range(-2, top, 4):
        hw = (y + 4) / (top + 4) * (gx1 - gx0) / 2
        line(d, (gm - hw + 1, y, gm + hw - 1, y), P['wall2'])
    ellipse(d, (gm - 7, 12, gm + 7, 26), P['trim'])                         # 山墙上的圆窗（被对白框盖住也无所谓）
    ellipse(d, (gm - 5, 14, gm + 5, 24), P['glass'])
    line(d, (gm, 14, gm, 24), P['trim'])
    # 烟囱
    rect(d, (196, -2, 210, 14), P['brick'][0])
    for y in range(0, 14, 3):
        line(d, (196, y, 210, y), P['brick'][2])
    rect(d, (194, -2, 212, 1), '#5a5250')
    # 二楼窗：225 = 形兆的窗（发黄的窗帘拉着）
    for cx, kw in ((225, dict()), (300, dict(shutter='r')), (378, dict()), (421, dict()), (464, dict()),
                   (510, dict(boarded=True))):
        sash_window(d, cx - 9, 48, 18, 24, P, **kw)
    wx0, wy0, wx1, wy1 = 216 + 2, 48 + 2, 234 - 2, 72 - 2
    rect(d, (wx0, wy0, wx1, wy1), '#c8b88e')                                 # 窗帘
    for x in range(wx0, wx1 + 1, 3):
        line(d, (x, wy0, x, wy1), '#b4a278')
    line(d, (225, wy0, 225, wy1), '#8a7a58')
    rect(d, (216, 59, 234, 60), P['trim2'])
    # 一楼窗
    for cx, kw in ((182, dict()), (262, dict(broken=True)), (320, dict(shutter='l')), (500, dict(broken=True)),
                   (536, dict(boarded=True))):
        sash_window(d, cx - 10, 88, 20, 26, P, **kw)
    # 门廊：两根柱子撑一个小坡顶，双开木门 + 半圆气窗，三级台阶
    rect(d, (398, 84, 444, 122), mix(P['wall'], '#000000', .3))              # 门廊里的阴影
    ellipse(d, (408, 84, 434, 100), P['trim'])
    ellipse(d, (410, 86, 432, 100), P['glass2'])
    for k in range(-2, 3):
        line(d, (421, 98, 421 + k * 5, 88), P['trim'])
    rect(d, (406, 92, 436, 122), P['trim'])
    rect(d, (408, 94, 420, 122), '#4a3226')
    rect(d, (422, 94, 434, 122), '#4a3226')
    for xx in (408, 422):
        bevel(d, (xx + 2, 97, xx + 10, 106), '#5e4232', '#2e1e16')
        bevel(d, (xx + 2, 109, xx + 10, 119), '#5e4232', '#2e1e16')
    px(d, 419, 108, '#c8a858')
    px(d, 423, 108, '#c8a858')
    poly(d, [(392, 84), (450, 84), (446, 76), (396, 76)], P['roof'][0])     # 门廊顶
    line(d, (396, 76, 446, 76), P['roof'][2])
    rect(d, (392, 84, 450, 86), P['trim'])
    for xx in (398, 442):
        rect(d, (xx - 2, 86, xx + 1, 122), '#d8ccb0')
        line(d, (xx - 2, 86, xx - 2, 122), '#ece2c8')
        line(d, (xx + 1, 86, xx + 1, 122), '#a89a7c')
    for i in range(3):                                                    # 台阶（往前、往下）
        y = 122 + i * 4
        rect(d, (396 - i * 3, y, 446 + i * 3, y + 3), '#a8a294' if i % 2 else '#9a9486')
        line(d, (396 - i * 3, y, 446 + i * 3, y), '#bcb6a8')
    # 爬山虎：墙根往上爬两片
    for cx, cy, n, s in ((352, 100, 60, 21), (552, 92, 70, 22), (160, 110, 30, 23)):
        r2 = np.random.RandomState(s)
        for _ in range(n):
            x = cx + r2.normal(0, 7)
            y = cy + abs(r2.normal(0, 14))
            if y > base:
                continue
            c = ['#3e5a34', '#4e6e3e', '#2e4628'][r2.randint(3)]
            rect(d, (x, y, x + 2, y + 1), c)
    return im


def weed_clumps(im, x0, x1, base, n, seed, hmin=4, hmax=14, cols=None):
    """一丛丛野草：竖着的细叶片，底下密、上面稀"""
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    cols = cols or YD['grass']
    for _ in range(n):
        x = rng.uniform(x0, x1)
        b = base + rng.uniform(-3, 3)
        for k in range(rng.randint(3, 7)):
            h = rng.uniform(hmin, hmax)
            lean = rng.uniform(-.35, .35)
            c = cols[rng.randint(len(cols))]
            for t in range(int(h)):
                px(d, x + k - 2 + lean * t, b - t, c)
            if rng.rand() < .15:
                px(d, x + k - 2 + lean * h, b - h, YD['dry'])
    return im


def foxtail_strip(W, x0, x1, y_base, n=4, count=40, seed=0):
    """狗尾草：高出草丛的几根穗子随风摆（n 帧，首尾接得上）"""
    rng = np.random.RandomState(seed)
    h = 30
    out = Image.new('RGBA', ((x1 - x0) * n, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    stalks = [(rng.uniform(4, x1 - x0 - 4), rng.uniform(10, 22), rng.uniform(0, 2 * np.pi), rng.uniform(-.2, .2))
              for _ in range(count)]
    for f in range(n):
        for sx, sh, ph, lean in stalks:
            sway = 1.6 * np.sin(2 * np.pi * f / n + ph)
            b = h - 1 - (y_base - y_base)
            prev = None
            for t in range(int(sh)):
                k = t / sh
                x = sx + (lean * t) + sway * k * k
                y = b - t
                d.point((int(f * (x1 - x0) + x), int(y)), fill=C('#7e8c4a' if t < sh - 4 else '#b8b070'))
            hx = sx + lean * sh + sway
            d.point((int(f * (x1 - x0) + hx), int(b - sh)), fill=C('#d0c888'))
    return out


def brick_wall(d, x0, x1, y0, y1, P, seed=0):
    B = P['brick']
    rect(d, (x0, y0, x1, y1), B[0])
    rng = np.random.RandomState(seed)
    for i, y in enumerate(range(y0, y1, 4)):
        line(d, (x0, y + 3, x1, y + 3), B[3])
        off = 0 if i % 2 else 4
        for x in range(x0 + off, x1, 8):
            line(d, (x, y, x, y + 2), B[3])
            if rng.rand() < .25:
                rect(d, (x + 1, y, x + 7, y + 2), B[rng.choice([1, 2])])


def iron_railing(d, x0, x1, y0, y1, P, skip=()):
    """生锈的铁栅栏：上下两道横档、竖杆顶上是矛尖"""
    for y in (y0 + 3, y1 - 3):
        line(d, (x0, y, x1, y), P['iron'])
    for x in range(x0 + 2, x1, 5):
        if any(a <= x <= b for a, b in skip):
            continue
        line(d, (x, y0 + 1, x, y1), P['iron'])
        px(d, x, y0, P['iron'])
        px(d, x - 1, y0 + 1, P['iron'])
        px(d, x + 1, y0 + 1, P['iron'])
        if (x * 7) % 3 == 0:
            px(d, x, y0 + 6 + (x % 9), P['rust'])
            px(d, x, y0 + 7 + (x % 9), P['rust2'])


def gate_closed(P):
    im = new(640, 180)
    d = ImageDraw.Draw(im)
    for gx0, gx1 in ((88, 109), (111, 132)):
        rect(d, (gx0, 86, gx0 + 1, 134), P['iron'])
        rect(d, (gx1 - 1, 86, gx1, 134), P['iron'])
        for y in (90, 108, 131):
            line(d, (gx0, y, gx1, y), P['iron'])
        for x in range(gx0 + 4, gx1 - 2, 4):
            line(d, (x, 86, x, 134), P['iron'])
            px(d, x, 85, P['iron'])
        for k in range(gx1 - gx0 - 4):                                     # 上面的卷草纹（一道弧）
            x = gx0 + 2 + k
            t = k / (gx1 - gx0 - 4)
            px(d, x, 96 - 4 * math.sin(math.pi * t), P['iron'])
        for y in range(92, 132, 7):
            px(d, gx0 + 3, y, P['rust2'])
            px(d, gx1 - 3, y + 3, P['rust'])
    rect(d, (108, 104, 112, 112), P['iron'])                                # 门闩
    px(d, 110, 108, P['rust2'])
    return im


def gate_open(P):
    """铁门往院子里开：两扇门板转成窄窄的斜边，贴着门柱"""
    im = new(640, 180)
    d = ImageDraw.Draw(im)
    for hx, s in ((88, 1), (132, -1)):
        x2 = hx + s * 9
        for t in range(0, 10):
            x = hx + s * t
            yt, yb = 86 - t * .5, 134 - t * 1.4
            line(d, (x, yt, x, yb), P['iron'] if t % 3 == 0 or t == 9 else P['iron'])
        line(d, (hx, 90, x2, 85), P['rust'])
        line(d, (hx, 108, x2, 101), P['iron'])
    return im


POTS = [(244, 136), (282, 136), (251, 126), (275, 126), (258, 116), (269, 116)]   # 6 个花盆（中心 x, 盆底 y）：下层 → 上层


def pot(d, cx, by, seed):
    rng = np.random.RandomState(seed)
    poly(d, [(cx - 4, by - 8), (cx + 4, by - 8), (cx + 3, by), (cx - 3, by)], '#ae6840')
    rect(d, (cx - 5, by - 9, cx + 5, by - 8), '#c88050')
    line(d, (cx + 2, by - 7, cx + 2, by - 1), '#8a4e30')
    line(d, (cx + 3, by - 7, cx + 3, by - 1), '#8a4e30')
    for k in range(rng.randint(2, 5)):                                    # 枯了的花茎
        x = cx - 3 + rng.randint(0, 7)
        h = rng.randint(3, 8)
        line(d, (x, by - 10, x + rng.randint(-1, 2), by - 10 - h), '#8a7a4a')
        if rng.rand() < .4:
            px(d, x, by - 10 - h, '#6a4a30')


def pots_layers():
    """花盆架上剩下的花盆：pots_gone = 0..6（砸掉几个），按 POTS 的顺序从下层先没"""
    out = []
    for gone in range(7):
        im = new(640, 180)
        d = ImageDraw.Draw(im)
        for i, (cx, by) in enumerate(POTS):
            if i >= gone:
                pot(d, cx, by, 40 + i)
        out.append(im)
    return out


def pot_rack(d):
    """三层的阶梯花架（木头晒白了）"""
    for (x0, x1, y) in ((236, 290, 136), (242, 284, 126), (250, 278, 116)):
        rect(d, (x0, y, x1, y + 2), '#9a8468')
        line(d, (x0, y, x1, y), '#b8a282')
        line(d, (x0, y + 3, x1, y + 3), '#5e4a38')
    for x, y0 in ((238, 136), (288, 136), (244, 126), (282, 126), (252, 116), (276, 116)):
        line(d, (x, y0 + 3, x, 142), '#6e5842')
    rect(d, (234, 142, 292, 143), '#4e4430')


def yard_near():
    W, P = 640, YD
    im = new(W, 180)
    d = ImageDraw.Draw(im)
    # 后面的砖墙（右边，院子的边界）+ 枯树
    brick_wall(d, 556, W, 100, 124, P, seed=4)
    rect(d, (556, 98, W, 100), '#a8a090')
    im = nj_house(im)
    d = ImageDraw.Draw(im)
    # 院子的地：土 + 草，从房子墙脚到画面底
    rect(d, (0, 122, W, 180), P['dirt'])
    im = dither_fill(im, (0, 122, W, 180), P['dirt'], P['grass'][0], .45)
    noise_specks(im, (0, 122, W, 180), list(P['grass']) + ['#6a6248', P['dry']], 4200, 5)
    d = ImageDraw.Draw(im)
    # 石板小路：门廊台阶 → 画面下边（往前变宽）
    rng = np.random.RandomState(8)
    y = 134
    while y < 180:
        hh = 3 + (y - 134) * .12
        k = (y - 134) / 46
        xa, xb = 394 - 22 * k, 448 + 22 * k
        x = xa + rng.uniform(0, 4)
        while x < xb - 4:
            sw = rng.uniform(8, 14) * (1 + k * .6)
            rect(d, (x, y, min(xb, x + sw - 2), y + hh - 1), ['#a8a49a', '#9a968c', '#b4b0a4'][rng.randint(3)])
            line(d, (x, y, min(xb, x + sw - 2), y), '#c4c0b4')
            x += sw
        y += hh + 1
    # 野草：墙脚一圈高的、满院零星的
    im = weed_clumps(im, 150, 560, 124, 150, 21, 6, 16)
    im = weed_clumps(im, 556, W, 126, 40, 22, 6, 18)
    im = weed_clumps(im, 0, W, 152, 120, 23, 3, 9)
    im = weed_clumps(im, 0, W, 172, 90, 24, 4, 11)
    d = ImageDraw.Draw(im)
    # 枯树
    tx, tb = 600, 132
    rect(d, (tx - 3, 60, tx + 3, tb), '#4a3c34')
    line(d, (tx - 3, 60, tx - 3, tb), '#5e4e44')
    line(d, (tx + 3, 60, tx + 3, tb), '#3a2e28')

    def branch(x, y, ang, L, w, depth):
        if depth == 0 or L < 3:
            return
        x2, y2 = x + L * math.cos(ang), y - L * math.sin(ang)
        line(d, (x, y, x2, y2), '#4a3c34', max(1, w))
        branch(x2, y2, ang + .45, L * .68, w - 1, depth - 1)
        branch(x2, y2, ang - .5, L * .62, w - 1, depth - 1)
    branch(tx, 62, math.pi / 2 + .25, 26, 3, 5)
    branch(tx, 74, math.pi / 2 - .6, 22, 2, 4)
    branch(tx, 86, math.pi / 2 + .9, 18, 2, 4)
    # 油桶（倒了的生锈铁桶）
    rect(d, (512, 118, 528, 134), '#5a4a3a')
    for y in (121, 128):
        line(d, (512, y, 528, y), '#3e3228')
    line(d, (512, 118, 528, 118), '#7a6450')
    rect(d, (513, 124, 516, 130), P['rust'])
    # 花盆架
    pot_rack(d)
    # 左边：人行道 + 红砖矮墙 + 铁栅栏 + 门柱，墙在 x 196 塌了
    for x in range(0, 214):
        pass
    brick_wall(d, 0, 196, 112, 134, P, seed=6)
    rect(d, (0, 110, 196, 112), '#a8a090')
    line(d, (0, 110, 196, 110), '#c4bcac')
    # 门洞（x 88–132）里看得见院子：先把墙抹掉
    a = np.array(im)
    ref = np.array(new(W, 180))
    im2 = new(W, 180)
    im2.alpha_composite(im)
    d = ImageDraw.Draw(im)
    rect(d, (88, 110, 132, 134), P['dirt'])
    im = dither_fill(im, (88, 112, 132, 134), P['dirt'], P['grass'][1], .5)
    im = weed_clumps(im, 88, 132, 133, 14, 25, 3, 12)
    d = ImageDraw.Draw(im)
    iron_railing(d, 0, 88, 86, 110, P)
    iron_railing(d, 132, 192, 86, 110, P, skip=((176, 180),))
    line(d, (182, 88, 186, 100), P['iron'])                                # 一根弯了的栏杆
    for gx in (74, 132):                                                  # 门柱（红砖 + 石帽 + 圆球）
        brick_wall(d, gx, gx + 14, 80, 134, P, seed=gx)
        line(d, (gx, 80, gx, 134), P['brick'][1])
        line(d, (gx + 14, 80, gx + 14, 134), P['brick'][3])
        rect(d, (gx - 2, 76, gx + 16, 80), '#a8a090')
        line(d, (gx - 2, 76, gx + 16, 76), '#c8c0b0')
        ellipse(d, (gx + 3, 68, gx + 11, 76), '#a8a090')
        px(d, gx + 5, 70, '#d0c8b8')
    # 门牌（左门柱）：石板竖写「虹村」
    rect(d, (75, 88, 87, 117), '#cfc8b2')
    bevel(d, (75, 88, 87, 117), '#e2dccc', '#8e8878')
    kanji(im, 75, 89, '虹村', '#2e2a26', vertical=True)
    d = ImageDraw.Draw(im)
    # 塌了的墙头：x 186–198 一级级往下掉，碎砖堆在墙脚
    for k, x in enumerate(range(186, 200, 3)):
        a = np.array(im)
        a[110:112 + k * 4, x:x + 3] = 0
        im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    for k, x in enumerate(range(186, 200, 3)):
        yy = 112 + k * 4
        rect(d, (x, yy, x + 2, yy + 1), P['brick'][1])
    rect(d, (199, 122, 214, 134), P['dirt'])                                # 塌口后面就是院子
    im = dither_fill(im, (199, 122, 214, 134), P['dirt'], P['grass'][1], .4)
    d = ImageDraw.Draw(im)
    poly(d, [(186, 140), (194, 128), (204, 124), (214, 130), (226, 140)], '#7a3e2e')
    rng = np.random.RandomState(31)
    for _ in range(26):
        x, y = rng.randint(186, 226), rng.randint(126, 141)
        rect(d, (x, y, x + 4, y + 2), P['brick'][rng.randint(3)])
        line(d, (x, y + 2, x + 4, y + 2), P['brick'][3])
    for x, y in ((232, 146), (214, 152), (246, 158)):                       # 滚远的几块
        rect(d, (x, y, x + 4, y + 2), P['brick'][1])
        line(d, (x, y + 2, x + 4, y + 2), P['brick'][3])
    # 人行道：x 0–200（右边斜着收进院子的草地里）
    pw = new(W, 180)
    pw = sidewalk(pw, 0, 240, 134, 180)
    pa = np.array(pw)
    for y in range(134, 180):
        edge = int(200 + (y - 134) * .35)
        pa[y, edge:] = 0
    pw = Image.fromarray(pa, 'RGBA')
    im.alpha_composite(pw)
    d = ImageDraw.Draw(im)
    for y in range(134, 180):
        px(d, int(200 + (y - 134) * .35), y, '#8a867c')
    im = weed_clumps(im, 196, 230, 160, 12, 26, 3, 8)
    im = weed_clumps(im, 0, 196, 136, 26, 27, 2, 6)                          # 墙脚缝里的草
    # 电线杆（人行道上）
    im = pole(im, 30, 140, 150)
    im = wires(im, [(30, -10 + 6), (330, 4)], sag=10)
    return im


def figure_layer():
    """二楼窗帘后面的人影（形兆）：深色剪影，透过窗帘只看得见轮廓"""
    im = new(640, 180)
    d = ImageDraw.Draw(im)
    sil = '#5a4a3a'
    ellipse(d, (222, 53, 229, 60), sil)                                     # 头
    rect(d, (219, 60, 232, 70), sil)                                        # 肩
    line(d, (219, 61, 215, 57), sil)                                        # 抬起的手（拿弓）
    line(d, (215, 52, 215, 64), '#4a3c30')                                  # 弓
    a = np.array(im)
    m = a[..., 3] > 0
    yy, xx = np.mgrid[0:180, 0:640]
    a[m & (((xx + yy) % 2) == 1)] = (*c3('#7a6a50'), 255)                   # 隔着窗帘：一半抖动
    return Image.fromarray(a, 'RGBA')


def nijimura_yard():
    W = 640
    far = yard_far()
    near = yard_near()
    fox = foxtail_strip(W, 206, 556, 124, n=4, count=36, seed=9)
    gc, go = gate_closed(YD), gate_open(YD)
    pots = pots_layers()
    fig = figure_layer()
    layers = {'far': far, 'near': near, 'foxtail': fox, 'gate_closed': gc, 'gate_open': go, 'figure': fig}
    for i, p in enumerate(pots):
        layers[f'pots_{i}'] = p
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(gate=[110, 146], gate_in=[110, 132], nameplate=[81, 102], window=[225, 60], street=[40, 150],
                             wall_corner=[204, 146], rubble=[206, 134], rack=[264, 146],
                             pot_1=[244, 128], pot_2=[282, 128], pot_3=[251, 118], pot_4=[275, 118], pot_5=[258, 108], pot_6=[269, 108],
                             door=[421, 146], porch=[421, 130], drum=[520, 146], tree=[600, 146], walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/nijimura_yard/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/nijimura_yard/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': 'bg/nijimura_yard/foxtail', 'n': 4, 'fps': 3, 'x': 206, 'y': 124 - 29, 'k': 1},
                        {'type': 'image', 'image': 'bg/nijimura_yard/figure', 'k': 1, 'x': 0, 'y': 0, 'key': 'figure'},
                        {'type': 'pick', 'images': ['bg/nijimura_yard/gate_closed', 'bg/nijimura_yard/gate_open'], 'key': 'gate',
                         'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pick', 'images': [f'bg/nijimura_yard/pots_{i}' for i in range(7)], 'values': list(range(7)),
                         'key': 'pots_gone', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv = comp(pv, near, gc, pots[0])
    pv.alpha_composite(fox.crop((0, 0, 350, 30)), (206, 95))
    preview('nijimura_yard', {'room': pv}, ['room'], W)
    pv2 = comp(far.resize((W, 180), Image.NEAREST), near, go, pots[3], fig)
    pv2.save(os.path.join(LIB.ASSETS, 'preview', 'bg_nijimura_yard_open.png'))
    save_layers('nijimura_yard', layers, meta)
    return meta


# ============================================================ 室内共用：墙纸、护墙板、地板
HD = dict(wp='#3c4a3e', wp2='#4a5a4a', wp3='#33403a', wpd='#28322c', plaster='#a29676', plaster2='#887c60', lath='#6a5440',
          ceil='#221e1c', trim='#3a2a22', trim2='#56402e', trimhi='#7a5e44',
          wain='#3e2c22', wain_in='#35251c', wain_hi='#5a4232', wain_lo='#22160e',
          floor=('#5a4232', '#523c2e', '#604634', '#4e3a2c'), seam='#30221a', grain='#46342a', fhi='#76583e',
          dust=('#7a6a58', '#6a5a4a'))


def nj_room(W, seed=0, top=0):
    """虹村家室内的墙：墨绿的花纹墙纸（一块块撕破、露出灰泥和板条）、天花板线脚、深色护墙板、木地板"""
    P = HD
    G = 134
    im = new(W, 180, P['wp'])
    d = ImageDraw.Draw(im)
    for y in range(top + 14, 98, 14):                                       # 花纹：小菱形 + 竖细条
        for x in range((y // 14) % 2 * 8, W, 16):
            px(d, x, y, P['wp2'])
            px(d, x - 1, y + 1, P['wp2'])
            px(d, x + 1, y + 1, P['wp2'])
            px(d, x, y + 2, P['wp2'])
    for x in range(4, W, 16):
        for y in range(top + 12, 98, 2):
            px(d, x, y, P['wp3'])
    im = grad(im, (0, top + 8, W, top + 34), (P['wpd'], P['wp3'], P['wp']))
    d = ImageDraw.Draw(im)
    for y in range(top + 14, 98, 14):
        for x in range((y // 14) % 2 * 8, W, 16):
            px(d, x, y + 1, P['wp2'])
    rect(d, (0, top, W, top + 8), P['ceil'])
    rect(d, (0, top + 8, W, top + 11), P['trim'])
    line(d, (0, top + 11, W, top + 11), P['trimhi'])
    # 水渍：从天花板往下流的深色竖条
    rng = np.random.RandomState(seed)
    for _ in range(int(W / 40)):
        x = rng.randint(0, W - 10)
        L = rng.randint(14, 50)
        for k in range(L):
            w = 1 + int(3 * (1 - k / L))
            line(d, (x + k // 12, top + 12 + k, x + k // 12 + w, top + 12 + k), P['wpd'])
    # 护墙板（y 98–134）
    WT = 98
    rect(d, (0, WT, W, G), P['wain'])
    rect(d, (0, WT, W, WT + 2), P['wain_hi'])
    line(d, (0, WT + 3, W, WT + 3), P['wain_lo'])
    for x in range(2, W, 26):
        rect(d, (x + 2, WT + 7, x + 22, G - 7), P['wain_in'])
        bevel(d, (x + 2, WT + 7, x + 22, G - 7), P['wain_lo'], P['wain_hi'])
    rect(d, (0, G - 4, W, G), P['trim'])
    line(d, (0, G - 4, W, G - 4), P['trimhi'])
    im = wood_floor(im, 0, W, G, P['floor'], P['seam'], P['grain'], P['fhi'], seed=seed + 5, dust=P['dust'])
    return im, G


def tear(im, cx, cy, w, h, seed, lath=False):
    """墙纸撕掉一块：不规则的洞露出灰泥（大的露出板条），边上卷起一条亮边"""
    P = HD
    rng = np.random.RandomState(seed)
    n = 9
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = .7 + .3 * rng.rand()
        pts.append((cx + math.cos(a) * w / 2 * r, cy + math.sin(a) * h / 2 * r))
    d = ImageDraw.Draw(im)
    poly(d, [(x + 1, y + 1) for x, y in pts], P['wpd'])
    poly(d, pts, P['plaster'])
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).polygon([(int(x), int(y)) for x, y in pts], fill=255)
    a = np.array(m) > 0
    ys, xs = np.where(a)
    arr = np.array(im)
    for y, x in zip(ys, xs):
        if lath and (y - int(cy - h / 2)) % 4 == 3 and abs(x - cx) < w * .3 and abs(y - cy) < h * .3:
            arr[y, x] = (*c3(P['lath']), 255)
        elif (x * 3 + y * 5) % 11 == 0:
            arr[y, x] = (*c3(P['plaster2']), 255)
    im2 = Image.fromarray(arr, 'RGBA')
    d = ImageDraw.Draw(im2)
    for i in range(n):                                                    # 卷起的墙纸边
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        if y0 < cy and y1 < cy:
            line(d, (x0, y0 - 1, x1, y1 - 1), P['wp2'])
    if h >= 12:                                                            # 一条往下耷拉的墙纸
        fx = cx + rng.uniform(-w * .2, w * .1)
        fy = cy + h * .3
        poly(d, [(fx - 3, fy), (fx + 4, fy), (fx + 2, fy + h * .55), (fx - 1, fy + h * .5)], P['wp2'])
        line(d, (fx + 4, fy, fx + 2, fy + h * .55), P['wpd'])
    if lath:
        x0 = int(cx - w * .3)
        for y in range(int(cy - h * .3), int(cy + h * .3), 4):
            line(d, (x0, y, int(cx + w * .3), y), P['lath'])
            line(d, (x0, y + 1, int(cx + w * .3), y + 1), '#4e3c2c')
    im.paste(im2)
    return im


def boarded_window(d, x0, y0, w, h, seed):
    """钉了木板的窗：深色窗框，玻璃后面亮（外面是下午），木板之间的缝透光。返回透光的缝（x0, y0, x1, y1）列表"""
    P = HD
    x1, y1 = x0 + w, y0 + h
    rect(d, (x0 - 4, y0 - 5, x1 + 4, y0 - 2), P['trim2'])
    line(d, (x0 - 4, y0 - 5, x1 + 4, y0 - 5), P['trimhi'])
    rect(d, (x0 - 2, y0 - 2, x1 + 2, y1 + 2), P['trim'])
    rect(d, (x0, y0, x1, y1), '#f0e2b8')
    rng = np.random.RandomState(seed)
    gaps = []
    y = y0 - 1
    k = 0
    while y < y1:
        bh = rng.randint(6, 10)
        tilt = rng.randint(-2, 3)
        poly(d, [(x0 - 4, y), (x1 + 4, y + tilt), (x1 + 4, y + tilt + bh), (x0 - 4, y + bh)], '#6a5a46' if k % 2 else '#5e4e3c')
        line(d, (x0 - 4, y, x1 + 4, y + tilt), '#86735a')
        px(d, x0 - 2, y + bh // 2, '#a8a090')
        px(d, x1 + 2, y + tilt + bh // 2, '#a8a090')
        gap = rng.randint(2, 4)
        if y + bh + gap < y1:
            gaps.append((x0, y + bh, x1, y + bh + gap))
        y += bh + gap
        k += 1
    rect(d, (x0 - 5, y1 + 2, x1 + 5, y1 + 4), P['trim2'])
    line(d, (x0 - 5, y1 + 2, x1 + 5, y1 + 2), P['trimhi'])
    return gaps


def slit_shafts(gaps, G, KD=0.55, SL=0.9):
    """木板缝透进来的光：往右下斜着落到地板上（太阳在左上）。返回 (光柱多边形, 地上光斑多边形)"""
    shafts, spots = [], []
    for x0, y0, x1, y1 in gaps:
        def proj(x, y):
            yf = G + (G - y) * KD
            return x + (yf - G) * SL, min(179.0, yf)
        q = [proj(x0, y1), proj(x1, y1), proj(x1, y0), proj(x0, y0)]
        spots.append(q)
        shafts.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)] + q)
    return shafts, spots


def hull(pts):
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


def light_layers(W, shafts, spots, top, col=(255, 214, 150), k_shaft=.16, k_spot=.32, extra=None):
    """光柱 + 地上的光斑 → glow 图；返回 (glow, 光柱强度场)"""
    f, sh = shafts_field(W, [hull(p) for p in shafts], top, 180)
    m = Image.new('L', (W, 180), 0)
    md = ImageDraw.Draw(m)
    for q in spots:
        md.polygon([(int(round(x)), int(round(y))) for x, y in q], fill=255)
    if extra:
        for q in extra:
            md.polygon([(int(round(x)), int(round(y))) for x, y in q], fill=255)
    sp = np.array(m).astype(float) / 255
    field = f * k_shaft + sp * k_spot
    return field_glow(field, col), sh


def holes_layer(W, seed, wall_box, floor_box, n_wall=110, n_floor=50):
    """打完坏公司之后多出来的弹孔（key 'holes'）"""
    im = new(W, 180)
    bullet_holes(im, n_wall, wall_box, seed, clusters=12)
    bullet_holes(im, n_floor, floor_box, seed + 1, rim='#7a6450', clusters=8, floor=True)
    return im


# ============================================================ 虹村家一楼走廊 nijimura_hall（640 宽）
#   左：开着的正门（外面是亮的院子，地上一块门形的光）→ 衣帽架 → 歪着的画 → 钉木板的窗（缝里透光）→
#   通黑屋子的门洞 → 边桌 + 裂了的椭圆镜子、地上碎花瓶 → 停了的落地钟 → 第二扇钉木板的窗 → 倒在墙根的画框 →
#   最右是通楼梯间的拱门。墙上、地板上已经有零星的小弹孔（伏笔）；key 'holes' = 打完之后更多。
def hall_room():
    W = 640
    im, G = nj_room(W, seed=3)
    P = HD
    for cx, cy, w, h, s, lath in ((140, 30, 30, 18, 1, False), (250, 108, 16, 10, 2, False), (318, 46, 40, 30, 3, True),
                                  (452, 34, 22, 16, 4, False), (566, 70, 26, 34, 5, True), (96, 110, 12, 8, 6, False)):
        im = tear(im, cx, cy, w, h, s, lath)
    d = ImageDraw.Draw(im)
    # ---- 正门（x 12–52）：门开着往里转，门洞里是亮的院子
    dx0, dx1, dy0 = 14, 50, 56
    rect(d, (dx0 - 5, dy0 - 12, dx1 + 5, G), P['trim'])
    line(d, (dx0 - 5, dy0 - 12, dx1 + 5, dy0 - 12), P['trimhi'])
    rect(d, (dx0, dy0 - 9, dx1, dy0 - 2), '#f4ead0')                          # 气窗
    for x in range(dx0 + 6, dx1, 7):
        line(d, (x, dy0 - 9, x, dy0 - 2), P['trim'])
    rect(d, (dx0, dy0, dx1, G - 1), '#ecebd2')                               # 外面：过曝的院子
    im = grad(im, (dx0, dy0, dx1 + 1, G - 14), ('#f6f2dc', '#e8e8cc', '#d4dab0'))
    d = ImageDraw.Draw(im)
    rect(d, (dx0, G - 22, dx1, G - 1), '#b8c08c')
    im = weed_clumps(im, dx0, dx1, G - 4, 10, 61, 4, 12, cols=('#8a9a62', '#a0ac72', '#7a8a56'))
    d = ImageDraw.Draw(im)
    rect(d, (dx0 + 14, dy0 + 20, dx1 - 2, G - 22), '#d8ccb0')                # 院子里的门柱、铁栏（很淡）
    for x in range(dx0 + 16, dx1 - 2, 3):
        line(d, (x, dy0 + 16, x, G - 22), '#9a9888')
    poly(d, [(dx0, dy0), (dx0 + 8, dy0 + 4), (dx0 + 8, G + 3), (dx0, G - 1)], '#4a3226')   # 门板（往里开）
    line(d, (dx0 + 8, dy0 + 4, dx0 + 8, G + 3), '#5e4232')
    px(d, dx0 + 6, dy0 + 42, '#c8a858')
    rect(d, (dx0 - 6, G - 1, dx1 + 6, G + 1), '#6a5a48')                     # 门槛
    # ---- 衣帽架（x 76–92）
    cx = 84
    rect(d, (cx - 1, 62, cx + 1, G - 2), '#2a1e18')
    for k in (-1, 1):
        line(d, (cx, 66, cx + k * 7, 60), '#2a1e18')
        line(d, (cx, 74, cx + k * 6, 70), '#2a1e18')
        line(d, (cx, G - 2, cx + k * 6, G + 1), '#2a1e18')
    ellipse(d, (cx - 8, 54, cx + 2, 60), '#3a3436')                          # 挂着的旧帽子
    rect(d, (cx - 10, 59, cx + 4, 60), '#2a2426')
    # ---- 歪着的画（x 112–162）
    pts = [(114, 56), (160, 52), (162, 86), (116, 90)]
    poly(d, [(x + 1, y + 2) for x, y in pts], '#1a1614')
    poly(d, pts, '#8a7040')
    poly(d, [(118, 59), (157, 56), (158, 83), (119, 86)], '#3e4a52')
    poly(d, [(119, 76), (132, 66), (144, 74), (158, 64), (158, 83), (119, 86)], '#2e3a2e')
    line(d, (119, 76, 158, 72), '#5a6a5a')
    line(d, (137, 40, 116, 56), '#1a1614')
    line(d, (137, 40, 160, 52), '#1a1614')
    # ---- 钉木板的窗 1（x 190–230）
    gaps1 = boarded_window(d, 192, 52, 36, 42, 7)
    # ---- 门洞（x 262–306）：通黑屋子
    rect(d, (258, 52, 310, G), P['trim'])
    line(d, (258, 52, 310, 52), P['trimhi'])
    rect(d, (262, 56, 306, G - 1), '#141210')
    poly(d, [(270, G - 1), (300, G - 1), (296, G - 10), (274, G - 10)], '#1c1814')
    rect(d, (284, 96, 296, 122), '#1e1a16')                                  # 黑屋子里一把椅子的影子
    rect(d, (284, 110, 300, 113), '#221e1a')
    line(d, (286, 113, 286, G - 10), '#221e1a')
    line(d, (298, 113, 298, G - 10), '#221e1a')
    # ---- 边桌 + 椭圆镜子（x 336–390）
    ellipse(d, (344, 50, 380, 98), '#7a6036')
    ellipse(d, (347, 53, 377, 95), '#5a6a70')
    ellipse(d, (350, 56, 368, 80), '#7a8a8e')
    for a, b in (((362, 60), (354, 88)), ((362, 60), (374, 82)), ((362, 60), (350, 64))):    # 镜面的裂纹
        line(d, (*a, *b), '#c8d4d6')
    rect(d, (336, 108, 390, 112), '#4a3226')
    line(d, (336, 108, 390, 108), '#6a4a34')
    for x in (339, 386):
        rect(d, (x, 112, x + 2, G - 2), '#3a2618')
    rect(d, (346, 112, 380, 118), '#3e2a1e')
    px(d, 363, 115, '#c8a858')
    rect(d, (350, 100, 356, 108), '#8a8e8a')                                 # 蜡烛台
    line(d, (353, 94, 353, 100), '#d8d0b8')
    # 地上的碎花瓶
    for x, y, c in ((352, 140, '#4a6a9a'), (358, 142, '#5a7aa8'), (364, 139, '#e8e4dc'), (370, 143, '#4a6a9a'), (347, 144, '#e8e4dc')):
        rect(d, (x, y, x + 3, y + 1), c)
    # ---- 落地钟（x 412–440）：停了，玻璃门裂了
    rect(d, (412, 56, 440, G - 1), '#4a2e20')
    poly(d, [(410, 56), (426, 46), (442, 56)], '#3a2418')
    ellipse(d, (416, 58, 436, 78), '#d8ccb0')
    ellipse(d, (418, 60, 434, 76), '#ece2c8')
    line(d, (426, 68, 426, 61), '#2a2420')
    line(d, (426, 68, 431, 71), '#2a2420')
    rect(d, (418, 84, 434, 122), '#2a1e16')
    line(d, (426, 84, 426, 112), '#8a7040')
    ellipse(d, (422, 110, 430, 118), '#b89848')
    line(d, (420, 88, 430, 100), '#8a9498')
    line(d, (430, 100, 424, 116), '#8a9498')
    bevel(d, (412, 56, 440, G - 1), '#6a4a34', '#2a1a10')
    # ---- 钉木板的窗 2（x 470–510）
    gaps2 = boarded_window(d, 472, 52, 36, 42, 9)
    # ---- 倒在墙根的画框（x 532–568）
    poly(d, [(532, G + 4), (540, 100), (572, 104), (566, G + 6)], '#7a6036')
    poly(d, [(536, G + 2), (542, 104), (568, 107), (563, G + 4)], '#2a2622')
    line(d, (540, 106, 560, 130), '#4a4642')
    # ---- 拱门（x 590–636）：里面是楼梯间，看得见最下面几级台阶
    ax0, ax1, ay0 = 592, 636, 48
    rect(d, (ax0 - 4, ay0 + 10, ax1 + 4, G), P['trim'])
    ellipse(d, (ax0 - 4, ay0 - 4, ax1 + 4, ay0 + 26), P['trim'])
    rect(d, (ax0, ay0 + 10, ax1, G - 1), '#2a2a24')
    ellipse(d, (ax0, ay0, ax1, ay0 + 22), '#2a2a24')
    for i in range(6):
        y = G - 1 - i * 5
        rect(d, (ax0 + 10 + i * 6, y - 4, ax1, y), '#3e2e22' if i % 2 else '#46342a')
        line(d, (ax0 + 10 + i * 6, y - 4, ax1, y - 4), '#5a4434')
    rect(d, (ax0 + 6, G - 34, ax0 + 9, G - 1), '#2e2018')                    # 楼梯扶手柱
    ellipse(d, (ax0 + 5, G - 38, ax0 + 10, G - 33), '#3a2a20')
    # ---- 地上的灰泥碎块、纸屑；已经有的小弹孔（伏笔）
    im = debris(im, (60, G + 2, 600, 176), 70, 41)
    im = bullet_holes(im, 26, (100, 52, 560, 128), 13, clusters=5)
    im = bullet_holes(im, 10, (120, G + 4, 540, 172), 14, rim='#7a6450', clusters=4, floor=True)
    return im, G, gaps1 + gaps2, (dx0, dy0, dx1)


def nijimura_hall():
    W = 640
    room, G, gaps, (dx0, dy0, dx1) = hall_room()
    shafts, spots = slit_shafts(gaps, G)
    # 正门的光：门洞落在地上的一块（往前、往右斜）
    door_spot = [(dx0 + 8, G + 1), (dx1, G + 1), (dx1 + 26, 179), (dx0 + 20, 179)]
    door_shaft = [(dx0 + 8, dy0), (dx1, dy0), (dx1, G), (dx0 + 8, G)] + door_spot
    glow, sh = light_layers(W, shafts + [door_shaft], spots + [door_spot], 50)
    holes = holes_layer(W, 77, (60, 50, 590, 130), (40, G + 4, 600, 176))
    ys, xs = np.where(sh > .5)
    ys, xs = ys[xs > dx1 + 30], xs[xs > dx1 + 30]                              # 浮尘只放在两扇窗的光柱里
    bx0, by0, bx1, by1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    region = lambda x, y: sh[min(179, int(y + by0)), min(W - 1, int(x + bx0))] > .6
    dust = dust_strip(bx1 - bx0, by1 - by0, n=12, count=40, region=region, seed=17)
    layers = {'room': room, 'glow': glow, 'dust': dust, 'holes': holes}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(entry=[32, 148], entry_in=[32, 138], koichi=[64, 156], coat=[84, 146], painting=[138, 70],
                             window_1=[210, 72], side_door=[284, 146], mirror=[362, 74], table=[363, 146], vase=[358, 142],
                             clock=[426, 146], window_2=[490, 72], frame=[552, 146], arch=[614, 146], walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/nijimura_hall/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/nijimura_hall/holes', 'k': 1, 'x': 0, 'y': 0, 'key': 'holes'},
                        {'type': 'glow', 'image': 'bg/nijimura_hall/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.05},
                        {'type': 'strip', 'image': 'bg/nijimura_hall/dust', 'n': 12, 'fps': 5, 'x': bx0, 'y': by0, 'k': 1}],
                fg=[])
    pv = add_glow(room, glow)
    pv.alpha_composite(dust.crop((0, 0, bx1 - bx0, by1 - by0)), (bx0, by0))
    preview('nijimura_hall', {'room': pv}, ['room'], W)
    comp(pv, holes).save(os.path.join(LIB.ASSETS, 'preview', 'bg_nijimura_hall_holes.png'))
    save_layers('nijimura_hall', layers, meta)
    return meta


# ============================================================ 虹村家楼梯 nijimura_stairs（480 宽）
#   左：一楼走廊的尽头（关着的门、坏壁灯）→ 楼梯从 x 110 往右上爬到 x 290 的二楼平台（y 80），楼梯底下是储物间的小门；
#   楼梯间墙上一扇高高的拱窗，光斜着落在台阶和地板上；二楼平台前面一排栏杆（打坏了几根），后面两扇房门，
#   最右是去阁楼的窄梯子（通到天花板上的活板门）。形兆站平台上（锚点 landing）。
STAIR = dict(x0=110, x1=290, top=80, n=12)


def stair_y(x):
    """楼梯上 x 处的踏面高度（地图坐标）"""
    S = STAIR
    if x <= S['x0']:
        return 134
    if x >= S['x1']:
        return S['top']
    run = (S['x1'] - S['x0']) / S['n']
    i = int((x - S['x0']) // run) + 1
    return 134 - i * (134 - S['top']) / S['n']


def stairs_room():
    W = 480
    im, G = nj_room(W, seed=9)
    P = HD
    S = STAIR
    for cx, cy, w, h, s, lath in ((60, 40, 28, 22, 11, True), (250, 36, 20, 14, 12, False), (226, 74, 14, 10, 13, False)):
        im = tear(im, cx, cy, w, h, s, lath)
    d = ImageDraw.Draw(im)
    # ---- 一楼的门（x 30–62）+ 坏壁灯
    rect(d, (26, 56, 66, G), P['trim'])
    line(d, (26, 56, 66, 56), P['trimhi'])
    rect(d, (30, 60, 62, G - 1), '#4a3226')
    for yy in (64, 98):
        bevel(d, (34, yy, 58, yy + 28), '#5e4232', '#2e1e16')
    px(d, 59, 100, '#c8a858')
    rect(d, (84, 72, 88, 80), '#8a7a50')                                     # 壁灯：铜座 + 歪了的玻璃罩（碎了一角）
    line(d, (86, 72, 90, 66), '#8a7a50')
    poly(d, [(86, 58), (96, 60), (95, 68), (87, 67)], '#c8c0a0')
    line(d, (86, 58, 96, 60), '#e0dcc4')
    poly(d, [(92, 64), (95, 61), (95, 68), (91, 68)], P['wp'])
    rect(d, (88, 66, 93, 68), '#8a7a50')
    # ---- 拱窗（楼梯间墙上，x 168–196）
    wx0, wx1, wy0, wy1 = 170, 194, 50, 96
    rect(d, (wx0 - 3, wy0 + 6, wx1 + 3, wy1 + 3), P['trim'])
    ellipse(d, (wx0 - 3, wy0 - 6, wx1 + 3, wy0 + 18), P['trim'])
    rect(d, (wx0, wy0 + 6, wx1, wy1), '#f0e2b8')
    ellipse(d, (wx0, wy0 - 3, wx1, wy0 + 15), '#f0e2b8')
    line(d, ((wx0 + wx1) // 2, wy0 - 3, (wx0 + wx1) // 2, wy1), P['trim'])
    for y in (wy0 + 16, wy0 + 30):
        line(d, (wx0, y, wx1, y), P['trim'])
    poly(d, [(wx0, wy0 + 30), (wx0 + 8, wy0 + 26), (wx0 + 4, wy1)], '#c8bc98')  # 一块玻璃脏了
    # ---- 二楼：平台后面的墙上两扇门 + 去阁楼的梯子
    for x0, ajar in ((320, False), (380, True)):
        rect(d, (x0 - 4, 32, x0 + 30, S['top']), P['trim'])
        line(d, (x0 - 4, 32, x0 + 30, 32), P['trimhi'])
        rect(d, (x0, 36, x0 + 26, S['top']), '#4a3226' if not ajar else '#121010')
        if ajar:
            poly(d, [(x0, 36), (x0 + 7, 39), (x0 + 7, S['top']), (x0, S['top'])], '#4a3226')
        else:
            bevel(d, (x0 + 4, 42, x0 + 22, 58), '#5e4232', '#2e1e16')
            px(d, x0 + 22, 62, '#c8a858')
    rect(d, (440, 0, 476, 8), '#141210')                                     # 天花板上的活板门（开着，黑洞）
    for x in (446, 468):                                                    # 梯子
        line(d, (x, 6, x + 4, S['top']), '#5a4434')
        line(d, (x + 1, 6, x + 5, S['top']), '#3a2a20')
    for y in range(12, S['top'], 8):
        t = (y - 6) / (S['top'] - 6)
        line(d, (446 + 4 * t, y, 468 + 4 * t, y), '#6a5240')
    # ---- 平台（x 290–480，y 80）+ 下面一楼的墙
    T = S['top']
    rect(d, (S['x1'] - 2, T, W, T + 8), P['trim'])
    line(d, (S['x1'] - 2, T, W, T), P['trimhi'])
    line(d, (S['x1'] - 2, T + 5, W, T + 5), P['wain_lo'])
    rect(d, (S['x1'] - 2, T + 9, W, T + 11), P['wpd'])                       # 平台底下的阴影
    rect(d, (388, 92, 418, G), P['trim'])                                    # 平台下面的门洞（通厨房，黑）
    rect(d, (392, 96, 414, G - 1), '#141210')
    # ---- 楼梯：侧面的斜梁 + 锯齿踏步 + 下面的储物间
    run = (S['x1'] - S['x0']) / S['n']
    rise = (G - T) / S['n']
    side = [(S['x0'], G)]
    for i in range(S['n']):
        xa = S['x0'] + i * run
        ya = G - (i + 1) * rise
        side += [(xa, ya), (xa + run, ya)]
    side += [(S['x1'], G)]
    poly(d, side, '#4a3426')
    poly(d, [(S['x0'] + 4, G), (S['x1'] - 2, T + 12), (S['x1'] - 2, G)], '#3e2c20')     # 储物间的墙板
    for x in range(S['x0'] + 12, S['x1'], 10):
        yy = G - (x - S['x0']) / (S['x1'] - S['x0']) * (G - T - 12)
        line(d, (x, yy + 2, x, G - 1), '#33241a')
    rect(d, (228, 106, 252, G - 1), '#2a1e16')                               # 储物间小门
    bevel(d, (228, 106, 252, G - 1), '#4e3828', '#1a120c')
    px(d, 248, 120, '#a88a48')
    for i in range(S['n']):                                                # 踏步：踏面 + 旧地毯边 + 竖板
        xa = S['x0'] + i * run
        ya = G - (i + 1) * rise
        rect(d, (xa, ya, xa + run, ya + 1), '#7a5e44')
        px(d, xa, ya, '#94765a')
        line(d, (xa + 2, ya + 2, xa + run, ya + 2), '#6a2a2a')
        line(d, (xa, ya + 2, xa, ya + rise), '#2e2018')
    # 斜梁上的一道线脚（和楼梯平行）
    line(d, (S['x0'] + 2, G - 4, S['x1'] - 2, T + 8), '#5e4432')
    line(d, (S['x0'] + 2, G - 3, S['x1'] - 2, T + 9), '#2e2018')
    # ---- 扶手：栏杆柱 + 斜扶手 + 两头的立柱
    rail = lambda x: stair_y(x) - 22
    for x in range(S['x0'] + 6, S['x1'], 7):
        if x in (S['x0'] + 6 + 7 * 9, S['x0'] + 6 + 7 * 10):              # 打断了两根
            line(d, (x, stair_y(x) - 6, x, stair_y(x) - 1), '#3a2a20')
            continue
        line(d, (x, rail(x), x, stair_y(x) - 1), '#3a2a20')
        px(d, x - 1, rail(x) + 4, '#5a4434')
    prev = None
    for x in range(S['x0'], S['x1'] + 1, 2):
        y = G - 22 - (x - S['x0']) / (S['x1'] - S['x0']) * (G - T)
        if prev:
            line(d, (*prev, x, y), '#5a3e2c', 2)
            line(d, (prev[0], prev[1] - 1, x, y - 1), '#7a5a40')
        prev = (x, y)
    for x, y0, y1 in ((S['x0'] - 4, G - 30, G), (S['x1'] - 2, T - 26, T + 8)):
        rect(d, (x - 2, y0, x + 3, y1), '#3a2618')
        line(d, (x - 2, y0, x - 2, y1), '#5a4030')
        ellipse(d, (x - 3, y0 - 5, x + 4, y0 + 1), '#4a3020')
        px(d, x - 1, y0 - 4, '#7a5a40')
    # ---- 平台的栏杆（y 58–80），打坏了几根
    rect(d, (S['x1'], T - 22, W, T - 20), '#5a3e2c')
    line(d, (S['x1'], T - 22, W, T - 22), '#7a5a40')
    for i, x in enumerate(range(S['x1'] + 6, W, 6)):
        if i in (5, 6, 14):
            line(d, (x, T - 4, x, T - 1), '#3a2a20')
            line(d, (x, T - 19, x, T - 16), '#3a2a20')
            continue
        line(d, (x, T - 19, x, T - 1), '#3a2a20')
        px(d, x - 1, T - 14, '#5a4434')
    # ---- 地上的碎屑、零星弹孔
    im = debris(im, (20, G + 2, 470, 176), 50, 51)
    im = bullet_holes(im, 22, (70, 40, 470, 128), 15, clusters=5)
    im = bullet_holes(im, 8, (60, G + 4, 460, 172), 16, rim='#7a6450', clusters=3, floor=True)
    return im, G, (wx0, wy0, wx1, wy1)


def nijimura_stairs():
    W = 480
    room, G, (wx0, wy0, wx1, wy1) = stairs_room()
    # 拱窗的光：太阳在右上，光往左下落在台阶、楼梯脚和地板上
    KD, SL = .5, -.9
    proj = lambda x, y: (x + (G + (G - y) * KD - G) * SL, min(179.0, G + (G - y) * KD))
    pane = (wx0, wy0, wx1, wy1)
    q = [proj(wx0, wy1), proj(wx1, wy1), proj(wx1, wy0), proj(wx0, wy0)]
    shaft = [(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)] + q
    glow, sh = light_layers(W, [shaft], [q], wy0, k_shaft=.14, k_spot=.28)
    holes = holes_layer(W, 88, (40, 30, 470, 130), (30, G + 4, 470, 176), n_wall=90, n_floor=40)
    ys, xs = np.where(sh > .5)
    bx0, by0, bx1, by1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    region = lambda x, y: sh[min(179, int(y + by0)), min(W - 1, int(x + bx0))] > .6 and not (
        wx0 <= x + bx0 <= wx1 and wy0 - 4 <= y + by0 <= wy1)
    dust = dust_strip(bx1 - bx0, by1 - by0, n=12, count=24, region=region, seed=19)
    S = STAIR
    layers = {'room': room, 'glow': glow, 'dust': dust, 'holes': holes}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(door_1f=[46, 146], foot=[104, 146], stair_bottom=[S['x0'], 134], stair_top=[S['x1'], S['top']],
                             stair_mid=[200, int(stair_y(200))], under_door=[240, 146], window=[182, 70],
                             landing=[400, S['top']], landing_l=[306, S['top']], landing_r=[440, S['top']],
                             door_2f=[333, S['top']], door_2f_open=[393, S['top']], ladder=[457, S['top']], hatch=[458, 4],
                             kitchen=[403, 146], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/nijimura_stairs/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/nijimura_stairs/holes', 'k': 1, 'x': 0, 'y': 0, 'key': 'holes'},
                        {'type': 'glow', 'image': 'bg/nijimura_stairs/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.04},
                        {'type': 'strip', 'image': 'bg/nijimura_stairs/dust', 'n': 12, 'fps': 5, 'x': bx0, 'y': by0, 'k': 1}],
                fg=[])
    pv = add_glow(room, glow)
    pv.alpha_composite(dust.crop((0, 0, bx1 - bx0, by1 - by0)), (bx0, by0))
    preview('nijimura_stairs', {'room': pv}, ['room'], W)
    comp(pv, holes).save(os.path.join(LIB.ASSETS, 'preview', 'bg_nijimura_stairs_holes.png'))
    save_layers('nijimura_stairs', layers, meta)
    return meta


# ============================================================ 虹村家阁楼 nijimura_attic（320 宽，一屏）
#   山墙一面（竖木板）+ 两边斜下来的屋顶底面（椽子）；山墙中间一扇小圆窗，光柱斜落在地板上。
#   左：地板上的活板门（梯子头露出来）→ 一摞纸箱和木箱 → 旧皮箱 → 父亲睡的破褥子 →
#   那只装碎纸的木箱（地上散着纸片，锚点 box）→ 一把坏椅子 → 山墙右下角的插座（锚点 outlet；key 'spark' = 插座冒电火花）。
AT = dict(board=('#5a4434', '#4e3a2c', '#664c3a', '#523e30'), gap='#2a1e16', roof='#3a2a20', roof2='#46342a', rafter='#2e2018',
          rafterhi='#5a4232', floor=('#6a523e', '#624a38', '#70583f', '#5e4836'), seam='#3a2a1e', grain='#56402e', fhi='#86684c')


def attic_room():
    W, G = 320, 134
    P = AT
    im = new(W, 180, P['board'][0])
    d = ImageDraw.Draw(im)
    for i, x in enumerate(range(0, W, 9)):                                   # 山墙：竖木板
        rect(d, (x, 0, x + 8, G), P['board'][i % 4])
        line(d, (x + 8, 0, x + 8, G), P['gap'])
        rng = np.random.RandomState(i)
        for _ in range(4):
            y = rng.randint(0, G - 4)
            line(d, (x + 2 + rng.randint(0, 4), y, x + 2 + rng.randint(0, 4), y + rng.randint(3, 9)), mix(P['board'][i % 4], '#000000', .2))
        if i % 3 == 0:
            px(d, x + 4, 20 + (i * 13) % 90, '#2a2420')                     # 钉子
    # 屋顶底面：左边从 (0,0)–(138,0)–(22,134)，右边对称
    for side in (-1, 1):
        def X(x):
            return x if side < 0 else W - x
        edge = lambda y: 138 - (138 - 22) * (y / G)
        pts = [(X(0), 0), (X(138), 0), (X(22), G), (X(0), G)]
        poly(d, pts, P['roof'])
        for k in range(1, 14):                                           # 望板：和斜边平行的线
            off = k * 9
            line(d, (X(138 - off), 0, X(22 - off), G), P['roof2'])
        for k in (0, 3, 7, 11):                                           # 椽子（粗一点）
            off = k * 9 + 2
            line(d, (X(138 - off), 0, X(22 - off), G), P['rafter'], 3)
        line(d, (X(138), 0, X(22), G), P['rafterhi'], 2)
        line(d, (X(137), 0, X(21), G), P['rafter'])
    # 系梁 + 中柱（被对白框盖住一部分也没关系）
    rect(d, (60, 32, 260, 38), P['rafter'])
    line(d, (60, 32, 260, 32), P['rafterhi'])
    rect(d, (156, 0, 164, 32), P['rafter'])
    line(d, (156, 0, 156, 32), P['rafterhi'])
    # 圆窗（中心 160, 70）
    cx, cy, r = 160, 72, 14
    ellipse(d, (cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), P['rafter'])
    ellipse(d, (cx - r, cy - r, cx + r, cy + r), '#f2e4bc')
    ellipse(d, (cx - r + 3, cy - r + 3, cx + 2, cy + 2), '#fff4d4')
    line(d, (cx, cy - r, cx, cy + r), P['rafter'], 2)
    line(d, (cx - r, cy, cx + r, cy), P['rafter'], 2)
    for k in range(10):                                                   # 蛛网
        a = k * .16
        line(d, (cx + r - 2, cy - r + 2, cx + r - 2 - 8 * math.cos(a), cy - r + 2 + 8 * math.sin(a)), '#8a8274')
    # 墙根踢脚
    rect(d, (0, G - 3, W, G), '#3a2a1e')
    im = wood_floor(im, 0, W, G, P['floor'], P['seam'], P['grain'], P['fhi'], seed=71, dust=('#8a7660', '#7a6650'))
    d = ImageDraw.Draw(im)
    # ---- 活板门（地板上，x 30–66）：盖板掀起来立在后面（两个铰链），前面是黑洞，梯子头露出来
    poly(d, [(30, 146), (66, 146), (64, 118), (32, 118)], '#4e3a2c')
    line(d, (32, 118, 64, 118), '#6a5040')
    for x in range(38, 64, 8):
        line(d, (x, 119, x - 1, 145), '#3e2e22')
    line(d, (31, 132, 65, 132), '#5e4836')
    for x in (36, 58):
        rect(d, (x, 143, x + 4, 146), '#8a8a86')
    poly(d, [(30, 146), (66, 146), (70, 156), (26, 156)], '#141010')
    line(d, (26, 156, 70, 156), '#8a6c50')
    line(d, (26, 157, 70, 157), '#4a3828')
    for x in (37, 57):
        rect(d, (x, 136, x + 2, 154), '#8a6c50')
        px(d, x, 136, '#a88a66')
    line(d, (37, 141, 59, 141), '#7a5e44')
    line(d, (37, 149, 59, 149), '#6a5040')
    # ---- 一摞箱子（x 70–120）
    for x0, y0, x1, y1, c, lab in ((70, 108, 98, G + 2, '#a07c54', True), (96, 116, 122, G + 2, '#8a6a48', False),
                                   (74, 88, 96, 108, '#b08a5e', True), (98, 100, 116, 116, '#7a5a3e', False)):
        rect(d, (x0, y0, x1, y1), c)
        line(d, (x0, y0, x1, y0), mix(c, '#ffffff', .25))
        line(d, (x1, y0, x1, y1), mix(c, '#000000', .3))
        line(d, (x0, (y0 + y1) // 2, x1, (y0 + y1) // 2), mix(c, '#000000', .15))
        if lab:
            rect(d, (x0 + 4, y0 + 4, x0 + 12, y0 + 8), '#e0d4b8')
    # ---- 旧皮箱（x 124–150）
    rect(d, (124, 116, 152, G + 3), '#5a3a2a')
    line(d, (124, 116, 152, 116), '#7a5440')
    for x in (130, 146):
        line(d, (x, 116, x, G + 3), '#a08a5a')
    rect(d, (136, 112, 140, 116), '#3a2a20')
    # ---- 破褥子（x 156–196，地上）
    poly(d, [(154, 140), (196, 138), (202, 148), (150, 150)], '#7a7464')
    poly(d, [(156, 141), (194, 139), (198, 145), (154, 147)], '#8e8674')
    for x, y in ((164, 143), (180, 141), (190, 145)):
        rect(d, (x, y, x + 3, y + 1), '#5e5a4c')
    # ---- 那只木箱（x 206–232）：盖子掀开靠着，里面、地上都是碎纸
    rect(d, (206, 120, 232, 140), '#7a5a3a')
    line(d, (206, 120, 232, 120), '#9a7650')
    line(d, (206, 130, 232, 130), '#5e4430')
    line(d, (232, 120, 232, 140), '#4a3424')
    rect(d, (208, 117, 230, 120), '#2a1e16')                                 # 箱口（里面黑）
    poly(d, [(206, 120), (232, 120), (236, 104), (210, 104)], '#86643e')     # 盖子
    line(d, (210, 104, 236, 104), '#a07a52')
    rng = np.random.RandomState(81)
    for _ in range(26):
        x = rng.randint(196, 250)
        y = rng.randint(140, 156) if rng.rand() < .7 else rng.randint(116, 120)
        rect(d, (x, y, x + rng.randint(1, 3), y), ['#e8e0cc', '#d4ccb4', '#f4ecd8', '#b8c4cc'][rng.randint(4)])
    # ---- 坏椅子（x 244–262）
    rect(d, (244, 116, 247, G + 4), '#4a3424')
    rect(d, (244, 124, 262, 127), '#5a4030')
    line(d, (260, 127, 266, G + 6), '#4a3424')
    line(d, (246, 104, 246, 116), '#4a3424')
    line(d, (252, 102, 252, 124), '#4a3424')
    line(d, (246, 104, 254, 101), '#4a3424')
    # ---- 插座（山墙右下，x 258–266, y 114–122）+ 一截电线
    ox, oy = 262, 118
    rect(d, (ox - 5, oy - 5, ox + 5, oy + 5), '#d8d0bc')
    bevel(d, (ox - 5, oy - 5, ox + 5, oy + 5), '#ece6d6', '#9a9480')
    for xx in (ox - 2, ox + 2):
        line(d, (xx, oy - 2, xx, oy), '#2a2620')
    px(d, ox, oy + 3, '#2a2620')
    line(d, (ox, oy + 5, ox + 1, G - 4), '#2a2a2a')
    line(d, (ox + 1, G - 4, 296, G - 4), '#2a2a2a')
    im = debris(im, (80, G + 6, 300, 176), 30, 61, cols=('#8a7660', '#a8946e', '#5e4a38'))
    return im, G, (cx, cy, r), (ox, oy)


def spark_strip(ox, oy, n=4, size=28, seed=0):
    """插座冒电火花：n 帧，黄白的折线往外窜"""
    rng = np.random.RandomState(seed)
    out = Image.new('RGBA', (size * n, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    c = size // 2
    for f in range(n):
        for k in range(3 + f % 2):
            a = rng.uniform(0, 2 * math.pi)
            L = rng.uniform(6, c - 1)
            x, y = c, c
            for s in range(4):
                t = (s + 1) / 4
                nx = c + math.cos(a) * L * t + rng.uniform(-2, 2)
                ny = c + math.sin(a) * L * t + rng.uniform(-2, 2)
                d.line([(f * size + x, y), (f * size + nx, ny)], fill=C('#fff8c0' if s < 2 else '#ffd040'))
                x, y = nx, ny
        d.point((f * size + c, c), fill=C('#ffffff'))
        d.point((f * size + c + 1, c), fill=C('#ffffff'))
    return out


def nijimura_attic():
    W = 320
    room, G, (cx, cy, r), (ox, oy) = attic_room()
    # 圆窗的光：往右下落在地上一个椭圆
    KD, SL = .7, .55
    ring = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
    proj = lambda x, y: (x + (G + (G - y) * KD - G) * SL, min(179.0, G + (G - y) * KD))
    spot = [proj(x, y) for x, y in ring]
    glow, sh = light_layers(W, [ring + spot], [spot], cy - r, k_shaft=.18, k_spot=.3)
    ys, xs = np.where(sh > .5)
    bx0, by0, bx1, by1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    region = lambda x, y: sh[min(179, int(y + by0)), min(W - 1, int(x + bx0))] > .6 and math.hypot(x + bx0 - cx, y + by0 - cy) > r + 3
    dust = dust_strip(bx1 - bx0, by1 - by0, n=12, count=26, region=region, seed=23)
    spark = spark_strip(ox, oy, n=4, size=28, seed=5)
    yy, xx = np.mgrid[0:180, 0:W]
    sg = np.clip(1 - np.hypot(xx - ox, (yy - oy) * 1.2) / 32, 0, 1) ** 1.8 * .5
    spark_glow = field_glow(sg, (255, 236, 140), levels=8)
    layers = {'room': room, 'glow': glow, 'dust': dust, 'spark': spark, 'spark_glow': spark_glow}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(hatch=[48, 150], hatch_up=[48, 140], boxes=[96, 146], trunk=[138, 146], futon=[176, 148],
                             box=[219, 146], box_inside=[219, 118], photo=[226, 150], chair=[254, 146], outlet=[ox, oy],
                             outlet_floor=[ox, 146], window=[cx, cy], sun=[int(np.mean([p[0] for p in spot])), 160],
                             walk_x=[24, 296]),
                layers=[{'type': 'pano', 'image': 'bg/nijimura_attic/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'glow', 'image': 'bg/nijimura_attic/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.04},
                        {'type': 'strip', 'image': 'bg/nijimura_attic/dust', 'n': 12, 'fps': 5, 'x': bx0, 'y': by0, 'k': 1},
                        {'type': 'glow', 'image': 'bg/nijimura_attic/spark_glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.6,
                         'key': 'spark'},
                        {'type': 'strip', 'image': 'bg/nijimura_attic/spark', 'n': 4, 'fps': 14, 'x': ox - 14, 'y': oy - 14,
                         'k': 1, 'key': 'spark'}],
                fg=[])
    pv = add_glow(room, glow)
    pv.alpha_composite(dust.crop((0, 0, bx1 - bx0, by1 - by0)), (bx0, by0))
    preview('nijimura_attic', {'room': pv}, ['room'], W)
    pv2 = add_glow(pv, spark_glow)
    pv2.alpha_composite(spark.crop((0, 0, 28, 28)), (ox - 14, oy - 14))
    pv2.save(os.path.join(LIB.ASSETS, 'preview', 'bg_nijimura_attic_spark.png'))
    save_layers('nijimura_attic', layers, meta)
    return meta


SCENES = {'nijimura_yard': nijimura_yard, 'nijimura_hall': nijimura_hall, 'nijimura_stairs': nijimura_stairs,
          'nijimura_attic': nijimura_attic}


def main(keys):
    path = os.path.join(LIB.META, 'bg_ch1.json')
    meta = LIB.load_json(path, {}) or {}
    for k in keys or SCENES:
        meta[k] = SCENES[k]()
        print('背景', k)
    LIB.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
