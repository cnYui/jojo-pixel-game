# 第四部第9章（国道隧道 / 宇宙人、公路之星与猫草）的背景：6 张，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_ch9.json（build_p4.py 会把 _meta/bg_*.json 并进 bg.json）。
#   用法：python3 第四部/tools/art/p4_bg_ch9.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   图层 pack 一律 'ch9'（打包成 data/img_bg_ch9.js，进第9章时才加载）。
#   露伴宅外观沿用第5章的 rohan_house，这里不重画。
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import liv_floor, preview, save_layers, sky_far  # noqa: E402

PACK = 'ch9'
H = 180

# 3×5 的大写字母（招牌、门牌用；数字用 p4_bglib.DIG）
LET = {'A': ['010', '101', '111', '101', '101'], 'B': ['110', '101', '110', '101', '110'], 'C': ['011', '100', '100', '100', '011'],
       'D': ['110', '101', '101', '101', '110'], 'E': ['111', '100', '110', '100', '111'], 'F': ['111', '100', '110', '100', '100'],
       'G': ['011', '100', '101', '101', '011'], 'H': ['101', '101', '111', '101', '101'], 'I': ['111', '010', '010', '010', '111'],
       'K': ['101', '101', '110', '101', '101'], 'L': ['100', '100', '100', '100', '111'], 'M': ['10001', '11011', '10101', '10001', '10001'],
       'N': ['1001', '1101', '1011', '1001', '1001'], 'O': ['010', '101', '101', '101', '010'], 'P': ['110', '101', '110', '100', '100'],
       'R': ['110', '101', '110', '101', '101'], 'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'],
       'U': ['101', '101', '101', '101', '111'], 'V': ['101', '101', '101', '101', '010'], 'W': ['10001', '10001', '10101', '11011', '10001'],
       'X': ['101', '101', '010', '101', '101'], 'Y': ['101', '101', '010', '010', '010'],
       '-': ['000', '000', '111', '000', '000'], ' ': ['000'] * 5, '.': ['000', '000', '000', '000', '010']}


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
    """文泉驿点阵正黑 12 px（招牌用）；vertical = 竖排。返回 (宽, 高)"""
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


def qfield(f, col, levels=6):
    """强度场 0..1 → lighter 叠加用的光晕图（颜色即亮度），4×4 Bayer 抖动分档"""
    h, w = f.shape
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    fq = np.clip(np.floor(f * levels + bay) / levels, 0, 1)
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * np.array(col, float), 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def blob(w, cx, cy, rx, ry, power=1.4):
    yy, xx = np.mgrid[0:H, 0:w].astype(float)
    r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(1 - r, 0, 1) ** power


def add_glow(base, glow):
    """预览用：把 lighter 光晕加到底图上"""
    pv = np.array(base).astype(int)
    g = np.array(glow).astype(int)
    pv[..., :3] = np.clip(pv[..., :3] + g[..., :3] * (g[..., 3:4] > 0), 0, 255)
    return Image.fromarray(pv.astype(np.uint8), 'RGBA')


def mask_dither(mask, soft=1.5, levels=3):
    m = mask.filter(ImageFilter.BoxBlur(soft)) if soft else mask
    f = np.array(m).astype(float) / 255
    h, w = f.shape
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    return np.clip(np.floor(f * levels + bay) / levels, 0, 1)


def light_mix(base, lit, field):
    a, b = np.array(base), np.array(lit)
    sel = field >= 0.5
    a[sel] = b[sel]
    return Image.fromarray(a, 'RGBA')


def dust_strip(w, h, n=12, count=16, cols=('#fff2c8', '#ffd890'), region=None, seed=0):
    """光柱里浮着的灰尘：每粒沿小圈转、一圈正好 n 帧，亮度一闪一闪"""
    rng = np.random.RandomState(seed)
    out = Image.new('RGBA', (w * n, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    motes, tries = [], 0
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


def flame_strip(w, h, n=8, base=None, seed=0, cols=('#8a1e10', '#d8401a', '#f08a28', '#f8c848', '#fff2b0')):
    """一排火苗的循环帧条：每列一个火舌高度（base(x) 给包络），按两三个正弦叠出来的相位上下窜；
    从外到里五个色带（暗红 → 白芯），顶上偶尔脱出一颗火星。n 帧首尾接得上"""
    rng = np.random.RandomState(seed)
    out = np.zeros((h, w * n, 4), np.uint8)
    ph = rng.uniform(0, 2 * np.pi, (3, w))
    fr = [1, 2, 3]
    env = np.array([base(x) if base else 1.0 for x in range(w)])
    tongue = rng.uniform(.55, 1.0, w)
    # 火舌：相邻几列共用一个尖（看起来一簇一簇）
    for f in range(n):
        t = 2 * np.pi * f / n
        hh = np.zeros(w)
        for x in range(w):
            s = sum(np.sin(fr[i] * t + ph[i, x // 3 * 3 % w] + x * .35 * (i + 1)) / (i + 1) for i in range(3))
            hh[x] = env[x] * h * (.62 + .22 * s) * tongue[x // 4 * 4 % w]
        hh = np.convolve(hh, [.25, .5, .25], 'same')
        for x in range(w):
            top = h - hh[x]
            for y in range(max(0, int(top)), h):
                k = (y - top) / max(1, hh[x])             # 0 顶 → 1 底
                core = abs(x - w / 2) / (w / 2)
                lvl = 0 if k < .14 else 1 if k < .34 else 2 if k < .58 else 3 if k < .82 - .2 * core else 4
                if BAYER[y % 4, x % 4] < .3 and lvl > 0 and k < .9:
                    lvl -= 1
                out[y, f * w + x] = (*c3(cols[lvl]), 255)
        for _ in range(3):                                # 火星
            sx = rng.randint(0, w)
            sy = int(h - hh[sx] - 4 - rng.randint(0, 10))
            if 0 <= sy < h:
                out[sy, f * w + sx] = (*c3(cols[3]), 255)
    return Image.fromarray(out, 'RGBA')


def smoke_strip(w, h, n=10, count=10, cols=('#3a3434', '#4e4646', '#2a2626'), seed=0):
    """往上翻滚的黑烟：一团团圆从下往上走一圈（n 帧回到原处），边缘用抖动"""
    rng = np.random.RandomState(seed)
    out = Image.new('RGBA', (w * n, h), (0, 0, 0, 0))
    puffs = [(rng.uniform(0, w), rng.uniform(0, 1), rng.uniform(9, 17), rng.randint(len(cols))) for _ in range(count)]
    for f in range(n):
        fr = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(fr)
        for x, ph, r, ci in puffs:
            u = (ph + f / n) % 1
            cy = h + r - u * (h + 2 * r)
            cx = x + 5 * np.sin(u * 6 + x)
            rr = r * (.7 + .6 * u)
            ellipse(d, (cx - rr, cy - rr, cx + rr, cy + rr), cols[ci])
        a = np.array(fr)
        bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
        yy = np.mgrid[0:h, 0:w][0]
        keep = (yy / h * 1.3 + .1) > bay              # 越往上越稀
        a[..., 3] = np.where(keep & (a[..., 3] > 0), 255, 0)
        out.paste(Image.fromarray(a, 'RGBA'), (f * w, 0))
    return out


def damask(im, box, base, pat, pat2, step=14, seed=0):
    """洋馆墙纸：菱格里一朵小花纹"""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(im)
    rect(d, box, base)
    for j, y in enumerate(range(y0 + 4, y1, step)):
        for x in range(x0 + (j % 2) * step // 2, x1, step):
            px(d, x, y - 3, pat)
            px(d, x - 1, y - 2, pat); px(d, x + 1, y - 2, pat)
            px(d, x - 2, y, pat2); px(d, x + 2, y, pat2)
            px(d, x, y, pat)
            px(d, x - 1, y + 2, pat); px(d, x + 1, y + 2, pat)
            px(d, x, y + 3, pat)
    return im


# ============================================================ 露伴宅客厅 rohan_parlor（480 宽，白天）
#   左：通门厅的双开门 → 拱顶落地窗（酒红窗帘，外面是院子）→ 壁炉（上面挂露伴的彩稿）→ 茶几和两把扶手椅（骰子小游戏）
#   → 长沙发 → 一整面书柜（少年 JUMP 和自己的单行本）+ 落地钟。顶上一盏水晶吊灯。
#   开关：fire = 1 起火（左边窗帘和门那一头烧起来、黑烟、整屏橙色），数字 = 罩色浓度倍数。
RP = dict(wall='#3e5a4c', wall_p='#4e6c5a', wall_p2='#46624f', ceil='#e8e0cc', ceil2='#cfc4aa', trim='#f0e8d4', trim2='#c8bc9e',
          wain='#e6dcc4', wain_in='#dcd0b4', wain_hi='#f6f0e0', wain_lo='#b4a684', wd='#4a2e22', wm='#6a4430', wl='#8a5e40')


def rp_room():
    W, G = 480, 134
    P = RP
    im = new(W, H, P['wall'])
    im = damask(im, (0, 14, W, 104), P['wall'], P['wall_p'], P['wall_p2'])
    d = ImageDraw.Draw(im)
    # 天花板 + 檐口（两道线脚 + 一排齿饰）
    rect(d, (0, 0, W, 9), P['ceil'])
    rect(d, (0, 9, W, 14), P['trim'])
    line(d, (0, 9, W, 9), '#fffaf0')
    for x in range(0, W, 4):
        rect(d, (x, 12, x + 1, 13), P['trim2'])
    line(d, (0, 14, W, 14), P['trim2'])
    line(d, (0, 15, W, 15), '#2e4438')
    # 墙腰线 + 白护墙板（y 104–134）
    WT = 104
    rect(d, (0, WT, W, G), P['wain'])
    rect(d, (0, WT, W, WT + 2), P['trim'])
    line(d, (0, WT, W, WT), '#fffaf0')
    line(d, (0, WT + 3, W, WT + 3), P['wain_lo'])
    for x in range(3, W, 22):
        rect(d, (x + 2, WT + 7, x + 18, G - 7), P['wain_in'])
        bevel(d, (x + 2, WT + 7, x + 18, G - 7), P['wain_lo'], P['wain_hi'])
    rect(d, (0, G - 4, W, G), P['wd'])
    line(d, (0, G - 4, W, G - 4), P['wl'])

    # ---------------- 双开门（10–56）：深色实木、上半两块玻璃格，门楣三角
    dx0, dx1, dy0 = 10, 56, G - 82
    poly(d, [(dx0 - 6, dy0 - 6), (dx1 + 6, dy0 - 6), ((dx0 + dx1) / 2, dy0 - 16)], P['trim'])
    poly(d, [(dx0 - 2, dy0 - 7), (dx1 + 2, dy0 - 7), ((dx0 + dx1) / 2, dy0 - 13)], P['trim2'])
    rect(d, (dx0 - 6, dy0 - 6, dx1 + 6, G), P['trim'])
    line(d, (dx0 - 6, dy0 - 6, dx0 - 6, G), '#fffaf0')
    line(d, (dx1 + 6, dy0 - 6, dx1 + 6, G), P['trim2'])
    rect(d, (dx0, dy0, dx1, G - 1), P['wm'])
    mx = (dx0 + dx1) // 2
    for a, b in ((dx0, mx), (mx + 1, dx1)):
        bevel(d, (a, dy0, b, G - 1), P['wl'], P['wd'])
        for r in range(3):
            gy = dy0 + 5 + r * 11
            rect(d, (a + 4, gy, b - 4, gy + 8), '#a8c4b8')
            line(d, (a + 5, gy + 1, a + 8, gy + 1), '#d4e6dc')
            bevel(d, (a + 4, gy, b - 4, gy + 8), P['wd'], P['wl'])
        rect(d, (a + 4, dy0 + 42, b - 4, G - 8), '#5a3a28')
        bevel(d, (a + 4, dy0 + 42, b - 4, G - 8), P['wd'], P['wl'])
    rect(d, (mx - 3, dy0 + 40, mx - 2, dy0 + 44), '#d8b858')
    rect(d, (mx + 3, dy0 + 40, mx + 4, dy0 + 44), '#d8b858')

    # ---------------- 拱顶落地窗（76–160），外面是院子
    wx0, wy0, wx1, wy1 = 80, 30, 156, 128
    rect(d, (wx0 - 5, wy0 + 10, wx1 + 5, wy1 + 2), P['trim'])
    d.pieslice((wx0 - 5, wy0 - 10, wx1 + 5, wy0 + 30), 180, 360, fill=C(P['trim']))
    sky = new(W, H)
    sky = grad(sky, (wx0, wy0 - 6, wx1, wy1), ('#7cb4e8', '#a4cdf0', '#cce4f6', '#e4f0f8'))
    sd = ImageDraw.Draw(sky)
    cloud(sky, 92, 40, 30, seed=3)
    sd = ImageDraw.Draw(sky)
    for k, (tx, ty, r, c) in enumerate(((90, 84, 16, '#3e6a44'), (118, 78, 20, '#4a7c4a'), (148, 88, 15, '#3e6a44'),
                                       (104, 96, 14, '#5e8e52'), (138, 98, 13, '#5e8e52'))):
        ellipse(sd, (tx - r, ty - r, tx + r, ty + r), c)
        ellipse(sd, (tx - r + 3, ty - r + 2, tx + r - 6, ty + r - 8), mix(c, '#c8e08a', .35))
    rect(sd, (wx0, 104, wx1, wy1), '#86ae64')                            # 草坪
    for x in range(wx0, wx1, 3):
        px(sd, x, 104 + (x * 7) % 5, '#a4c87a')
    rect(sd, (wx0, 112, wx1, 116), '#d8ccb0')                            # 院子里的石板小路
    for x in range(wx0, wx1, 8):
        line(sd, (x, 112, x - 2, 116), '#b8ac90')
    rect(sd, (wx0 + 40, 92, wx0 + 41, 112), '#4a4a4e')                   # 院灯
    rect(sd, (wx0 + 38, 88, wx0 + 43, 92), '#2a2a30')
    msk = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(msk)
    md.rectangle((wx0, wy0 + 10, wx1, wy1), fill=255)
    md.pieslice((wx0, wy0 - 6, wx1, wy0 + 26), 180, 360, fill=255)
    im.paste(sky, (0, 0), msk)
    d = ImageDraw.Draw(im)
    for x in (wx0 + 25, wx0 + 51):                                       # 窗棂
        line(d, (x, wy0 - 2, x, wy1), P['trim'])
    for y in (wy0 + 22, wy0 + 52, wy0 + 78):
        line(d, (wx0, y, wx1, y), P['trim'])
    d.arc((wx0 + 18, wy0 - 2, wx1 - 18, wy0 + 30), 180, 360, fill=C(P['trim']))
    rect(d, (wx0 - 8, wy1 + 1, wx1 + 8, wy1 + 4), P['trim'])
    line(d, (wx0 - 8, wy1 + 4, wx1 + 8, wy1 + 4), P['trim2'])
    # 酒红丝绒窗帘（两边束起）+ 帘头
    for side in (-1, 1):
        cx = wx0 - 4 if side < 0 else wx1 + 4
        pts = [(cx - 12 * (side < 0), 22), (cx + 12 * (side > 0), 22), (cx + 12 * (side > 0) - 3 * side, 74),
               (cx + 4 * side, 82), (cx + 14 * side, G - 2), (cx - 2 * side if side > 0 else cx - 14, G - 2)]
        x_a, x_b = (cx - 14, cx + 8) if side < 0 else (cx - 8, cx + 14)
        rect(d, (x_a, 22, x_b, G - 2), '#8a1e2e')
        for x in range(x_a, x_b, 4):
            line(d, (x, 22, x, G - 2), '#6e1624')
            line(d, (x + 1, 22, x + 1, G - 2), '#a8323e')
        rect(d, (x_a - 1, 74, x_b + 1, 77), '#d8b858')                   # 束帘带
        px(d, (x_a + x_b) // 2, 78, '#d8b858')
        rect(d, (x_a, G - 3, x_b, G - 2), '#5a1018')
    rect(d, (wx0 - 22, 16, wx1 + 22, 24), '#8a1e2e')                     # 帘头（波浪边）
    for x in range(wx0 - 22, wx1 + 22, 8):
        d.pieslice((x, 20, x + 8, 28), 0, 180, fill=C('#8a1e2e'))
        px(d, x + 4, 27, '#d8b858')
    line(d, (wx0 - 22, 16, wx1 + 22, 16), '#d8b858')
    line(d, (wx0 - 22, 18, wx1 + 22, 18), '#a8323e')

    # ---------------- 壁炉（190–262）+ 上面露伴的彩稿
    fx0, fx1 = 190, 262
    rect(d, (fx0, 88, fx1, G), '#e2d8c2')                                # 大理石炉身
    rect(d, (fx0 - 6, 84, fx1 + 6, 89), '#f0e8d8')                       # 炉台
    line(d, (fx0 - 6, 84, fx1 + 6, 84), '#ffffff')
    line(d, (fx0 - 6, 89, fx1 + 6, 89), '#b8ac94')
    for x in (fx0 + 2, fx1 - 8):                                         # 两边的柱
        rect(d, (x, 90, x + 6, G), '#ece4d2')
        line(d, (x + 6, 90, x + 6, G), '#b8ac94')
        for yy in range(94, G - 2, 6):
            px(d, x + 3, yy, '#c8bca4')
    rect(d, (fx0 + 16, 98, fx1 - 16, G), '#2a1e1a')                      # 炉口
    d.pieslice((fx0 + 16, 92, fx1 - 16, 106), 180, 360, fill=C('#2a1e1a'))
    rect(d, (fx0 + 20, 120, fx1 - 20, 124), '#4a4448')                   # 柴架 + 几根没点的柴
    for k in range(3):
        rect(d, (fx0 + 24 + k * 8, 116 - k % 2 * 2, fx0 + 30 + k * 8 + 6, 119 - k % 2 * 2), ('#6a4430', '#7a5038', '#5a3a28')[k])
    rect(d, (fx0 + 14, G - 3, fx1 - 14, G), '#8a8078')                   # 炉前石
    for ox, c in ((fx0 + 4, '#d8b858'), (fx1 - 14, '#d8b858')):          # 炉台上的烛台
        rect(d, (ox + 4, 76, ox + 6, 84), c)
        rect(d, (ox + 2, 82, ox + 8, 84), c)
        rect(d, (ox + 4, 70, ox + 6, 75), '#f6f0e0')
        px(d, ox + 5, 69, '#f8c848')
    rect(d, (fx0 + 26, 78, fx0 + 46, 84), '#6a4430')                     # 座钟
    rect(d, (fx0 + 30, 72, fx0 + 42, 78), '#6a4430')
    ellipse(d, (fx0 + 32, 73, fx0 + 40, 80), '#f6f0e0')
    px(d, fx0 + 36, 75, '#2a2a30'); px(d, fx0 + 36, 76, '#2a2a30'); px(d, fx0 + 37, 76, '#2a2a30')
    # 彩稿（金框）：紫粉色调、一个戴头巾的少年剪影 + 粉色的书名（不写真名，只是露伴的画风）
    ax0, ay0, ax1, ay1 = 200, 30, 252, 68
    rect(d, (ax0 - 3, ay0 - 3, ax1 + 3, ay1 + 3), '#b8902e')
    bevel(d, (ax0 - 3, ay0 - 3, ax1 + 3, ay1 + 3), '#e8c860', '#7a5e1e')
    rect(d, (ax0 - 1, ay0 - 1, ax1 + 1, ay1 + 1), '#e8c860')
    im = grad(im, (ax0, ay0, ax1, ay1), ('#3a2a5a', '#7a3a7a', '#d86a8a', '#f4b0a0'))
    d = ImageDraw.Draw(im)
    ellipse(d, (ax0 + 30, ay0 + 6, ax0 + 46, ay0 + 22), '#f8e8b0')       # 月
    poly(d, [(ax0 + 12, ay1), (ax0 + 16, ay0 + 24), (ax0 + 22, ay0 + 16), (ax0 + 28, ay0 + 22), (ax0 + 30, ay1)], '#1e1428')
    ellipse(d, (ax0 + 15, ay0 + 10, ax0 + 27, ay0 + 22), '#1e1428')
    line(d, (ax0 + 14, ay0 + 13, ax0 + 30, ay0 + 11), '#f0e060')       # 头巾
    line(d, (ax0 + 30, ay0 + 11, ax0 + 36, ay0 + 14), '#f0e060')
    for k in range(5):
        px(d, ax0 + 6 + k * 9, ay1 - 4 - (k % 2) * 3, '#f8e8b0')
    rect(d, (ax0 + 33, ay1 - 9, ax1 - 3, ay1 - 3), '#f070a0')
    line(d, (ax0 + 35, ay1 - 6, ax1 - 5, ay1 - 6), '#ffd0e0')
    line(d, (226, 18, ax0 - 2, ay0 - 3), '#b8902e')
    line(d, (226, 18, ax1 + 2, ay0 - 3), '#b8902e')
    px(d, 226, 17, '#e8c860')

    # ---------------- 沙发（330–420，靠墙）
    sx0, sx1 = 332, 418
    rect(d, (sx0 + 4, 92, sx1 - 4, 114), '#7a2a34')
    d.pieslice((sx0 + 4, 84, sx1 - 4, 104), 180, 360, fill=C('#7a2a34'))
    for x in range(sx0 + 12, sx1 - 8, 10):                               # 拉扣
        px(d, x, 98, '#5a1a24'); px(d, x + 5, 104, '#5a1a24')
    line(d, (sx0 + 10, 90, sx1 - 10, 90), '#9a3a44')
    rect(d, (sx0 + 4, 112, sx1 - 4, 122), '#8a3440')
    line(d, (sx0 + 4, 112, sx1 - 4, 112), '#aa4a54')
    line(d, (sx0 + 47, 113, sx0 + 47, 121), '#6a2430')
    for ax in (sx0 - 2, sx1 - 10):
        rect(d, (ax, 102, ax + 12, 124), '#7a2a34')
        ellipse(d, (ax - 1, 98, ax + 13, 108), '#8a3440')
        line(d, (ax + 12, 104, ax + 12, 124), '#5a1a24')
    rect(d, (sx0, 124, sx1, 128), '#4a2e22')
    for lx in (sx0 + 2, sx1 - 5):
        rect(d, (lx, 128, lx + 2, G - 1), '#d8b858')
    rect(d, (sx0 + 16, 104, sx0 + 30, 113), '#d8b858')                   # 靠垫
    rect(d, (sx1 - 32, 104, sx1 - 18, 113), '#2e5a4a')
    # 沙发上方：一排四幅小画（露伴的速写）
    for k in range(4):
        x = 338 + k * 20
        rect(d, (x, 52, x + 14, 70), '#2a1e1a')
        rect(d, (x + 2, 54, x + 12, 68), '#f4ecd8')
        for r in range(3):
            line(d, (x + 4, 57 + r * 4, x + 9 + (k + r) % 3, 57 + r * 4 + (k % 2)), '#6a6070')

    # ---------------- 书柜（428–480）+ 落地钟（422 前）
    bx0, bx1 = 430, 480
    rect(d, (bx0, 24, bx1, G - 1), P['wd'])
    line(d, (bx0, 24, bx1, 24), P['wl'])
    rect(d, (bx0 - 2, 20, bx1, 24), P['wm'])
    rng = np.random.RandomState(9)
    books = ['#e8e0d0', '#c8a040', '#3a5aa8', '#a83a3a', '#e85a7a', '#5a8a5a', '#f4f0e6', '#6a4a8a']
    for sy in (28, 50, 72, 94):
        rect(d, (bx0 + 2, sy, bx1 - 1, sy + 19), '#2a1a12')
        x = bx0 + 3
        jump = sy == 50                                                  # 这一层是成排的单行本（同一套，书脊一样高）
        while x < bx1 - 2:
            bw = 2 if jump else rng.randint(2, 4)
            bh = 14 if jump else rng.randint(11, 18)
            c = ('#f070a0' if (x // 2) % 2 else '#f4f0e6') if jump else books[rng.randint(len(books))]
            rect(d, (x, sy + 19 - bh, x + bw - 1, sy + 18), c)
            px(d, x, sy + 19 - bh + 2, '#2a1a12' if jump else mix(c, '#ffffff', .4))
            x += bw
        rect(d, (bx0 + 2, sy + 19, bx1 - 1, sy + 20), P['wl'])
    rect(d, (bx0 + 2, 116, bx1 - 1, G - 3), P['wm'])
    bevel(d, (bx0 + 3, 117, bx1 - 2, G - 4), P['wl'], P['wd'])
    # 落地钟
    cx0 = 420
    rect(d, (cx0 - 7, 46, cx0 + 7, G - 1), '#5a3424')
    d.pieslice((cx0 - 7, 40, cx0 + 7, 54), 180, 360, fill=C('#5a3424'))
    ellipse(d, (cx0 - 5, 50, cx0 + 5, 60), '#f6f0e0')
    line(d, (cx0, 55, cx0, 51), '#2a2a30'); line(d, (cx0, 55, cx0 + 3, 55), '#2a2a30')
    rect(d, (cx0 - 4, 66, cx0 + 4, 110), '#3a2018')
    rect(d, (cx0 - 3, 67, cx0 + 3, 109), '#a8c4b8')
    line(d, (cx0, 67, cx0, 98), '#c8a040')
    ellipse(d, (cx0 - 3, 96, cx0 + 3, 102), '#e8c860')
    line(d, (cx0 + 7, 46, cx0 + 7, G - 1), '#3a2018')

    # ---------------- 地板：人字拼木地板 + 波斯地毯
    im = parquet(im, 0, W, G)
    d = ImageDraw.Draw(im)
    rug(im, 176, 142, 392, 172)
    d = ImageDraw.Draw(im)
    # ---------------- 茶几 + 两把扶手椅（骰子在茶几上：大碗由道具画，这里只放桌子）
    tx = 280
    for side in (-1, 1):                                                 # 扶手椅（侧面，面向茶几）
        cx = tx + side * 38
        back = cx + side * 10
        rect(d, (back - 4, 112, back + 4, 146), '#2e5a4a')
        d.pieslice((back - 4, 106, back + 4, 118), 180, 360, fill=C('#2e5a4a'))
        line(d, (back - 4 if side > 0 else back + 4, 112, back - 4 if side > 0 else back + 4, 146), '#3e7260')
        rect(d, (cx - 12, 132, cx + 10 * side + 2 * (side < 0), 144), '#3e7260')
        rect(d, (min(cx - 12, cx + 12 * side), 132, max(cx - 12, cx + 12 * side), 144), '#3e7260')
        line(d, (cx - 12, 132, cx + 12, 132), '#5a8c78')
        rect(d, (cx - 12, 124, cx - 9, 138), '#2e5a4a')                  # 扶手
        rect(d, (cx + 9, 124, cx + 12, 138), '#2e5a4a')
        line(d, (cx - 12, 124, cx - 9, 124), '#5a8c78'); line(d, (cx + 9, 124, cx + 12, 124), '#5a8c78')
        rect(d, (cx - 12, 144, cx + 12, 146), '#1e3a30')
        for lx in (cx - 11, cx + 10):
            rect(d, (lx, 146, lx + 1, 150), '#4a2e22')
    ellipse(d, (tx - 22, 128, tx + 22, 138), '#4a2e22')                  # 圆茶几
    ellipse(d, (tx - 22, 126, tx + 22, 136), '#7a5038')
    ellipse(d, (tx - 19, 127, tx + 19, 134), '#8a5e40')
    line(d, (tx - 14, 128, tx + 6, 128), '#a87a54')
    rect(d, (tx - 2, 136, tx + 2, 146), '#4a2e22')
    poly(d, [(tx - 12, 150), (tx + 12, 150), (tx + 4, 145), (tx - 4, 145)], '#3a2218')
    # 门口的伞架、窗下的盆栽
    rect(d, (62, 112, 72, G + 4), '#6a6a72')
    line(d, (62, 112, 72, 112), '#9a9aa2')
    for k, c in enumerate(('#2a2a30', '#8a1e2e')):
        line(d, (64 + k * 4, 112, 63 + k * 6, 92), c)
        px(d, 63 + k * 6, 91, '#d8b858')
    rect(d, (166, 120, 178, 136), '#b8784a')
    line(d, (166, 120, 178, 120), '#d89a6a')
    for k, (lx, ly) in enumerate(((160, 98), (172, 92), (182, 100), (168, 106), (178, 108))):
        poly(d, [(172, 120), (lx, ly), (lx + 6, ly + 4)], ('#3e7a44', '#5a9a52', '#3e7a44', '#4a8a4a', '#2e6a3a')[k])
    return im, G, (wx0, wy0, wx1, wy1)


def parquet(im, x0, x1, G):
    """人字拼木地板：每行一排斜放的短板，越往下行越高"""
    d = ImageDraw.Draw(im)
    tones = ['#9a6a44', '#8a5c3a', '#a8784e', '#94643e']
    y, h, row = G, 4.0, 0
    while y < H:
        yb = min(H, int(round(y + h)))
        bw = int(h * 2.2)
        for i, x in enumerate(range(x0 - bw, x1 + bw, bw)):
            c = tones[(i + row) % 4]
            if (i + row) % 2:
                poly(d, [(x, int(y)), (x + bw, int(y)), (x + bw - 2, yb), (x - 2, yb)], c)
            else:
                poly(d, [(x, int(y)), (x + bw, int(y)), (x + bw + 2, yb), (x + 2, yb)], c)
            line(d, (x, int(y), x - 2 + 4 * ((i + row) % 2 == 0), yb - 1), '#6e4a2e')
        line(d, (x0, yb - 1, x1, yb - 1), '#6e4a2e')
        y += h
        h = min(10.0, h * 1.2)
        row += 1
    im = dither_fill(im, (x0, G, x1, G + 2), '#4a2e22', '#6e4a2e', .5)
    return im


def rug(im, x0, y0, x1, y1):
    """波斯地毯（透视压扁的矩形）：深红底、藏青边、米色流苏、中间一个菱形纹章"""
    d = ImageDraw.Draw(im)
    poly(d, [(x0 + 8, y0), (x1 - 8, y0), (x1, y1), (x0, y1)], '#e8dcc0')        # 流苏底
    poly(d, [(x0 + 9, y0 + 1), (x1 - 9, y0 + 1), (x1 - 2, y1 - 1), (x0 + 2, y1 - 1)], '#2a3a6a')
    poly(d, [(x0 + 13, y0 + 3), (x1 - 13, y0 + 3), (x1 - 7, y1 - 3), (x0 + 7, y1 - 3)], '#9a2a2a')
    poly(d, [(x0 + 16, y0 + 5), (x1 - 16, y0 + 5), (x1 - 11, y1 - 5), (x0 + 11, y1 - 5)], '#8a2026')
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    poly(d, [(cx - 34, cy), (cx, y0 + 6), (cx + 34, cy), (cx, y1 - 6)], '#2a3a6a')
    poly(d, [(cx - 26, cy), (cx, y0 + 9), (cx + 26, cy), (cx, y1 - 9)], '#c8a050')
    poly(d, [(cx - 18, cy), (cx, y0 + 11), (cx + 18, cy), (cx, y1 - 11)], '#9a2a2a')
    ellipse(d, (cx - 4, cy - 2, cx + 4, cy + 2), '#e8dcc0')
    for k in range(-3, 4):                                                       # 边框上的小花
        if k:
            px(d, cx + k * 26, y0 + 2, '#c8a050')
            px(d, cx + k * 30, y1 - 2, '#c8a050')
    for x in range(int(x0), int(x1), 2):                                         # 前后流苏
        px(d, x, y1, '#f4ecd8')
    return im


def rohan_parlor():
    W = 480
    room, G, (wx0, wy0, wx1, wy1) = rp_room()
    # 窗外的阳光：落在地板上的一块（往右下斜），lighter 叠加
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    win = np.zeros((H, W))
    fl = Image.new('L', (W, H), 0)
    fd = ImageDraw.Draw(fl)
    fd.polygon([(wx0 + 6, G + 2), (wx1 - 6, G + 2), (wx1 + 40, 176), (wx0 + 24, 176)], fill=255)
    fm = mask_dither(fl, 1.5, 3)
    lit = tint(room, (1.12, 1.04, .86), (26, 18, 0))
    out = light_mix(room, lit, fm)
    # 吊灯（270, 16–36）：画进前景不合适（会盖住对白框），画在墙上的层里
    d = ImageDraw.Draw(out)
    cx = 300
    line(d, (cx, 0, cx, 12), '#b8902e')
    poly(d, [(cx - 16, 22), (cx + 16, 22), (cx + 10, 28), (cx - 10, 28)], '#d8b858')
    line(d, (cx - 16, 22, cx + 16, 22), '#f0d878')
    for k in range(-2, 3):
        x = cx + k * 7
        rect(d, (x - 1, 15, x, 21), '#f6f0e0')
        px(d, x, 14, '#fff2b0')
        for j in range(3):
            px(d, x + (j % 2), 29 + j * 2, '#d8eef8' if j % 2 else '#ffffff')
    line(d, (cx - 4, 12, cx - 14, 20), '#b8902e'); line(d, (cx + 4, 12, cx + 14, 20), '#b8902e')
    glow = qfield(np.maximum(blob(W, cx, 22, 30, 16) * .55, blob(W, (wx0 + wx1) / 2, 78, 50, 60, 2) * .18), (255, 220, 150))
    # 起火（fire）：门和左边窗帘烧起来，地板沿墙一溜小火，黑烟顶在天花板下
    fire_big = flame_strip(40, 74, 8, base=lambda x: .55 + .45 * math.sin(math.pi * x / 40), seed=3)
    fire_low = flame_strip(150, 26, 8, base=lambda x: .5 + .5 * abs(math.sin(x / 9.0)), seed=4)
    fire_cur = flame_strip(24, 96, 8, base=lambda x: .7 + .3 * math.sin(math.pi * x / 24), seed=5)
    smoke = smoke_strip(200, 44, 10, 30, seed=6)
    fire_glow = qfield(np.clip(blob(W, 60, 120, 120, 70, 1.2) * .7 + blob(W, wx0 - 6, 80, 40, 70) * .5, 0, 1), (255, 120, 40))
    # 烧焦的门（起火时换上）：门板发黑、玻璃碎掉
    scorch = new(W, H)
    sc = ImageDraw.Draw(scorch)
    for y in range(G - 82, G):
        for x in range(4, 62):
            if BAYER[y % 4, x % 4] < .45 + .4 * (y - (G - 82)) / 82:
                px(sc, x, y, '#1e1210')
    layers = {'room': out, 'glow': glow, 'fire_big': fire_big, 'fire_low': fire_low, 'fire_cur': fire_cur, 'smoke': smoke,
              'fire_glow': fire_glow, 'scorch': scorch}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(door=[33, 148], window=[118, 146], curtain=[72, 100], fireplace=[226, 146], painting=[226, 50],
                             mantel_clock=[226, 76], table=[280, 150], dice_bowl=[280, 128], chair_l=[242, 148], chair_r=[318, 148],
                             sofa=[375, 146], bookshelf=[455, 146], clock=[420, 146], chandelier=[300, 24], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/rohan_parlor/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'glow', 'image': 'bg/rohan_parlor/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.03},
                        {'type': 'image', 'image': 'bg/rohan_parlor/scorch', 'k': 1, 'x': 0, 'y': 0, 'key': 'fire'},
                        {'type': 'strip', 'image': 'bg/rohan_parlor/fire_cur', 'n': 8, 'fps': 10, 'x': wx0 - 18, 'y': G - 96, 'key': 'fire'},
                        {'type': 'strip', 'image': 'bg/rohan_parlor/fire_big', 'n': 8, 'fps': 11, 'x': 13, 'y': G - 74, 'key': 'fire'},
                        {'type': 'strip', 'image': 'bg/rohan_parlor/fire_low', 'n': 8, 'fps': 9, 'x': 0, 'y': G - 22, 'key': 'fire'},
                        {'type': 'strip', 'image': 'bg/rohan_parlor/smoke', 'n': 10, 'fps': 6, 'x': 0, 'y': 4, 'key': 'fire'},
                        {'type': 'glow', 'image': 'bg/rohan_parlor/fire_glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.25, 'key': 'fire'},
                        {'type': 'tint', 'color': '#ff6a20', 'alpha': 0.14, 'key': 'fire'}],
                fg=[])
    pv = add_glow(out, glow)
    preview('rohan_parlor', {'room': pv}, ['room'], W)
    pf = pv.copy()
    pf.alpha_composite(scorch)
    pf.alpha_composite(fire_cur.crop((0, 0, 24, 96)), (wx0 - 18, G - 96))
    pf.alpha_composite(fire_big.crop((0, 0, 40, 74)), (13, G - 74))
    pf.alpha_composite(fire_low.crop((0, 0, 150, 26)), (0, G - 22))
    pf.alpha_composite(smoke.crop((0, 0, 200, 44)), (0, 4))
    pf = add_glow(pf, fire_glow)
    preview('rohan_parlor_fire', {'room': pf}, ['room'], W)
    save_layers('rohan_parlor', layers, meta)
    return meta


# ============================================================ 国道隧道 route_tunnel（960 宽，傍晚，钠灯）
#   侧面看隧道：上面是拱顶的弧（越往上越暗），中间一排米色瓷砖墙、橙色钠灯一盏一盏，墙脚是检修步道 + 白色路缘，
#   下面两车道（中间橙色实线）。墙上：隧道名牌、距离牌、紧急电话箱、消火栓箱、避难口指示。右端 x 912 起是出口外面（傍晚天空）。
#   开关：room = 1 墙上开出公路之星的“房间”（亮着灯的门洞，门牌 ROOM）。
TN = dict(arch0='#1a1614', arch1='#2a2420', arch2='#3e3630', tile='#c8b08a', tile2='#b89e78', tile3='#d8c49e', grime='#8a7458',
          walk='#7a6e62', walk2='#948678', curb='#e8dcc4', road='#3a3330', road2='#332d2a', road3='#463e38')


def tunnel_near():
    W, G = 960, 128
    P = TN
    EX = 912                                                           # 出口
    im = new(W, H, P['arch0'])
    im = grad(im, (0, 0, W, 34), (P['arch0'], P['arch1'], P['arch2']))
    d = ImageDraw.Draw(im)
    # 拱顶的混凝土环缝（每 64 px 一道，竖向）+ 拱脚的弧线
    for x in range(20, EX, 64):
        line(d, (x, 0, x, 33), '#14100e')
        line(d, (x + 1, 0, x + 1, 33), P['arch2'])
    rect(d, (0, 33, EX, 36), '#4e443c')
    line(d, (0, 36, EX, 36), '#2a2420')
    # 射流风机（两台，挂在拱顶）
    for fx in (220, 640):
        rect(d, (fx - 26, 10, fx + 26, 24), '#6a6a6e')
        ellipse(d, (fx - 30, 10, fx - 22, 24), '#7a7a7e')
        ellipse(d, (fx + 22, 10, fx + 30, 24), '#4a4a4e')
        ellipse(d, (fx + 24, 12, fx + 28, 22), '#2a2a2e')
        line(d, (fx - 26, 11, fx + 26, 11), '#9a9a9e')
        for k in (-14, 14):
            line(d, (fx + k, 2, fx + k, 10), '#4a4a4e')
    # 瓷砖墙（36–G）：4×3 小砖，下半截一层黑灰（车开过熏的），每 64 px 一道伸缩缝
    WT = 38
    rect(d, (0, WT - 2, EX, G), P['tile'])
    for y in range(WT, G, 4):
        line(d, (0, y, EX, y), P['tile2'])
        for x in range((y // 4) % 2 * 3, EX, 6):
            px(d, x, y + 1, P['tile3'])
            px(d, x + 3, y + 2, P['tile2'])
    for x in range(20, EX, 64):
        line(d, (x, WT - 2, x, G), '#8a7458')
    # 熏黑的一截（下 30 px，抖动往上淡出）
    a = np.array(im)
    for y in range(G - 34, G):
        k = (y - (G - 34)) / 34
        for x in range(EX):
            if k > BAYER[y % 4, x % 4] * .9:
                a[y, x, :3] = (np.array(a[y, x, :3], float) * .62).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 一条蓝色反光带 + 一条白线（墙上的视线诱导标）
    rect(d, (0, G - 40, EX, G - 38), '#3a5a8a')
    line(d, (0, G - 40, EX, G - 40), '#5a7aaa')
    # 钠灯（每 48 px 一盏，y 46）
    lamps = []
    for x in range(36, EX - 10, 48):
        rect(d, (x - 9, 44, x + 9, 50), '#4a4440')
        rect(d, (x - 8, 45, x + 8, 48), '#ffd27a')
        line(d, (x - 7, 45, x + 7, 45), '#fff2c0')
        line(d, (x - 9, 50, x + 9, 50), '#2a2420')
        lamps.append(x)
    # 隧道名牌（左端）
    rect(d, (60, 60, 132, 80), '#e8e4dc')
    rect(d, (62, 62, 130, 78), '#1e3a6a')
    kanji(im, 72, 64, '杜王隧道', '#f4f0e6')
    d = ImageDraw.Draw(im)
    letters(d, 74, 82, 'MORIOH TUNNEL', '#5a5048')
    # 距离牌（白底黑字：出口还有多少米）
    for x, m in ((300, '600M'), (560, '300M'), (820, '50M')):
        rect(d, (x, 60, x + 20, 72), '#f4f0e6')
        bevel(d, (x, 60, x + 20, 72), '#ffffff', '#a8a092')
        letters(d, x + 3 + (14 - text_w(m)) // 2, 64, m, '#2a2a30')
    # 紧急电话箱 + 消火栓箱（绿底白字的避难口指示在电话箱上面）
    def phone_box(x):
        rect(d, (x, 76, x + 28, 112), '#d8d2c4')
        bevel(d, (x, 76, x + 28, 112), '#f4f0e6', '#8a8478')
        rect(d, (x + 2, 78, x + 26, 92), '#d83a2e')
        kanji(im, x + 2, 79, '非常', '#f4f0e6')
        rect(d, (x + 8, 95, x + 20, 108), '#4a4a50')
        rect(d, (x + 10, 97, x + 18, 101), '#2a2a30')
        px(d, x + 14, 105, '#e8e070')
        rect(d, (x + 4, 62, x + 24, 70), '#2e8a4e')
        rect(d, (x + 7, 64, x + 9, 68), '#f4f0e6')
        line(d, (x + 11, 66, x + 21, 66), '#f4f0e6')
        px(d, x + 20, 65, '#f4f0e6'); px(d, x + 20, 67, '#f4f0e6')
    def hydrant_box(x):
        rect(d, (x, 82, x + 20, 114), '#c8302a')
        bevel(d, (x, 82, x + 20, 114), '#e85a4a', '#7a1a14')
        rect(d, (x + 2, 85, x + 18, 92), '#f4f0e6')
        letters(d, x + 3, 86, 'FIRE', '#c8302a')
        ellipse(d, (x + 6, 96, x + 14, 104), '#f4e070')
        ellipse(d, (x + 8, 98, x + 12, 102), '#c8302a')
    phone_box(176)
    hydrant_box(212)
    phone_box(696)
    hydrant_box(732)
    # 墙脚：检修步道（G–G+10）+ 白路缘
    rect(d, (0, G, EX, G + 10), P['walk'])
    line(d, (0, G, EX, G), P['walk2'])
    for x in range(0, EX, 16):
        line(d, (x, G + 1, x, G + 9), '#6a5e54')
    rect(d, (0, G + 10, EX, G + 13), P['curb'])
    for x in range(0, EX, 8):
        rect(d, (x + 4, G + 10, x + 7, G + 13), '#2a2a30')            # 黑白相间
    line(d, (0, G + 14, EX, G + 14), '#1e1a18')
    # 路面（G+14 – 180）：两车道，中线橙色实线
    im = asphalt(im, 0, W, G + 15, H, cols=(P['road'], P['road2'], P['road3'], '#524a42'), dash=False)
    d = ImageDraw.Draw(im)
    rect(d, (0, 160, W, 161), '#e8902a')
    rect(d, (0, 163, W, 164), '#e8902a')
    rect(d, (0, 177, W, 178), '#e8e4d8')
    # ---------------- 出口外面（x ≥ EX）：傍晚的天空、山、护栏，路接着往外
    out = new(W, H)
    out = grad(out, (EX, 0, W, 130), ('#4a5a8a', '#a87a8a', '#f0a070', '#f8c888'))
    od = ImageDraw.Draw(out)
    for x in range(EX, W):
        y = 108 + 6 * math.sin(x / 13.0)
        line(od, (x, int(y), x, 130), '#5a5a6a')
    rect(od, (EX, 124, W, G + 14), '#6a6a5a')
    for x in range(EX, W, 10):                                         # 护栏
        rect(od, (x, 118, x + 1, G + 12), '#d8d4cc')
    rect(od, (EX, 118, W, 120), '#f0ece4')
    a, b = np.array(im), np.array(out)
    a[:G + 14, EX:] = b[:G + 14, EX:]
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 洞口（混凝土端墙，厚 10 px）+ 名牌
    rect(d, (EX - 10, 0, EX, G + 14), '#8a8478')
    line(d, (EX - 10, 0, EX - 10, G + 14), '#6a6458')
    line(d, (EX - 1, 0, EX - 1, G + 14), '#aaa498')
    for y in range(0, G + 14, 8):
        line(d, (EX - 9, y, EX - 2, y), '#7a7468')
    return im, G, lamps, EX


def tunnel_room(G):
    """公路之星的“房间”：墙上开出一个亮着暖灯的门洞，门牌 ROOM，里面看得到床头灯和床脚（x 470–520）"""
    im = new(960, H)
    d = ImageDraw.Draw(im)
    x0, x1, y0 = 474, 514, G - 66
    rect(d, (x0 - 4, y0 - 4, x1 + 4, G), '#6a4a34')
    bevel(d, (x0 - 4, y0 - 4, x1 + 4, G), '#8a6448', '#3a2418')
    im = grad(im, (x0, y0, x1, G), ('#f8d89a', '#f0c07a', '#c8905a'))
    d = ImageDraw.Draw(im)
    rect(d, (x0, G - 12, x1, G), '#8a3a3a')                             # 里面的红地毯
    rect(d, (x0 + 4, G - 26, x0 + 26, G - 14), '#f4ecdc')               # 床脚
    line(d, (x0 + 4, G - 26, x0 + 26, G - 26), '#ffffff')
    rect(d, (x0 + 4, G - 14, x0 + 26, G - 12), '#6a4a34')
    rect(d, (x1 - 10, G - 40, x1 - 4, G - 14), '#6a4a34')               # 床头柜 + 台灯
    poly(d, [(x1 - 12, G - 48), (x1 - 2, G - 48), (x1 - 4, G - 42), (x1 - 10, G - 42)], '#fff2c0')
    line(d, (x1 - 7, G - 42, x1 - 7, G - 40), '#6a4a34')
    rect(d, (x0 + 10, y0 + 8, x0 + 22, y0 + 22), '#a8c4b8')             # 墙上的小画
    bevel(d, (x0 + 10, y0 + 8, x0 + 22, y0 + 22), '#d8b858', '#8a6a2a')
    rect(d, (x0 + 2, y0 - 14, x1 - 2, y0 - 6), '#f4ecdc')               # 门牌 ROOM
    bevel(d, (x0 + 2, y0 - 14, x1 - 2, y0 - 6), '#ffffff', '#a8a092')
    letters(d, (x0 + x1) // 2 - text_w('ROOM') // 2, y0 - 12, 'ROOM', '#8a1e2e')
    for y in range(y0, G, 6):                                           # 门框上的砖（和隧道瓷砖接不上：一看就不对劲）
        line(d, (x0 - 4, y, x0 - 1, y), '#4a2e22')
    return im


def tunnel_far(W=480):
    """几乎看不见的远层：隧道里没有远景，用来在镜头卷动时给拱顶加一点景深（环缝慢一拍）"""
    im = new(W, H)
    d = ImageDraw.Draw(im)
    for x in range(10, W, 40):
        line(d, (x, 0, x + 6, 8), '#221c1a')
    return im


def route_tunnel():
    W = 960
    near, G, lamps, EX = tunnel_near()
    # 钠灯的光：每盏一圈晕 + 往墙上、往路面落的一块
    f = np.zeros((H, W))
    for x in lamps:
        f = np.maximum(f, blob(W, x, 48, 22, 12, 1.4) * .9)
        f = np.maximum(f, blob(W, x, 96, 26, 50, 2.0) * .30)
        f = np.maximum(f, blob(W, x + 6, 168, 30, 10, 1.4) * .32)
    f[:, EX - 10:] = 0
    glow = qfield(f, (190, 120, 40))
    exit_f = blob(W, W + 10, 120, 90, 90, 1.2) * .65                     # 出口的天光往洞里透一截
    exit_glow = qfield(exit_f, (255, 200, 140))
    room = tunnel_room(G)
    room_glow = qfield(blob(W, 494, G - 20, 50, 40, 1.5) * .45, (255, 190, 110))
    layers = {'near': near, 'glow': glow, 'exit': exit_glow, 'room': room, 'room_glow': room_glow}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(sign=[96, 70], phone1=[190, 146], hydrant1=[222, 146], phone2=[710, 146], hydrant2=[742, 146],
                             fan1=[220, 17], fan2=[640, 17], room_door=[494, 146], room_in=[494, 138], km600=[310, 66],
                             km300=[570, 66], km50=[830, 66], exit=[930, 150], lane_far=[0, 150], lane_near=[0, 170],
                             walk_x=[8, 952]),
                layers=[{'type': 'pano', 'image': 'bg/route_tunnel/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/route_tunnel/room', 'k': 1, 'x': 0, 'y': 0, 'key': 'room'},
                        {'type': 'glow', 'image': 'bg/route_tunnel/room_glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.1, 'key': 'room'},
                        {'type': 'glow', 'image': 'bg/route_tunnel/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.05},
                        {'type': 'glow', 'image': 'bg/route_tunnel/exit', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'tint', 'color': '#ff9a30', 'alpha': 0.07}],
                fg=[])
    pv = add_glow(add_glow(near, glow), exit_glow)
    preview('route_tunnel', {'room': pv}, ['room'], W)
    pr = pv.copy()
    pr.alpha_composite(room)
    preview('route_tunnel_room', {'room': add_glow(pr, room_glow)}, ['room'], W)
    save_layers('route_tunnel', layers, meta)
    return meta


# ============================================================ 国道 national_road（960 宽，下午，追车用：每层横向循环、自己会卷）
#   远：天空和云（慢）→ 海和对岸的岬角 → 中：海边的岩石和黑松 → 近：护栏、电线杆、反光柱、蓝色路牌、三车道（y 136–179）。
#   全部 wrap 层，vx = 每秒卷多少 px；stage.state.speed 乘在 vx 上（0 = 停住，1 = 追车，2 = 飙车）。
#   车道：上 136–151（中心 y 144）、中 151–165（158）、下 165–179（172），车道线白色虚线。
def tiled(P, base, objs):
    """横向无缝循环的一层：base(im, W3) 画铺满的底，objs(im, ox) 在 ox = 0, P, 2P 各画一遍，取中间那一段"""
    im = new(3 * P, H)
    if base:
        im = base(im, 3 * P) or im
    for ox in (0, P, 2 * P):
        im = objs(im, ox) or im
    return im.crop((P, 0, 2 * P, H))


def road_sky(P=480):
    def base(im, W3):
        im = grad(im, (0, 0, W3, 100), ('#5e9ade', '#7cb0e6', '#a2c8ee', '#cfe2f4'))
        return im
    def objs(im, ox):
        rng = np.random.RandomState(31)
        for i in range(4):
            cloud(im, ox + rng.randint(0, P - 60), rng.randint(16, 60), rng.randint(36, 70), seed=40 + i)
        return im
    return tiled(P, base, objs)


def road_sea(P=640):
    def base(im, W3):
        d = ImageDraw.Draw(im)
        rect(d, (0, 86, W3, H), '#3a7ab8')
        im = grad(im, (0, 86, W3, 126), ('#6aa4d4', '#4a8cc4', '#3a7ab8', '#2e6aa8'))
        d = ImageDraw.Draw(im)
        rng = np.random.RandomState(5)
        for _ in range(W3 // 3):                                       # 浪花的亮点
            x, y = rng.randint(0, W3), rng.randint(92, 126)
            line(d, (x, y, x + 1 + (y - 86) // 12, y), '#a8d0f0')
        line(d, (0, 86, W3, 86), '#9ac4e8')
        return im
    def objs(im, ox):
        d = ImageDraw.Draw(im)
        for cx, w, h in ((120, 150, 22), (470, 90, 14)):                # 对岸的岬角
            for x in range(-w // 2, w // 2):
                y = 86 - h * (1 - (2 * x / w) ** 2) ** .7 - 2 * math.sin(x / 5.0)
                line(d, (ox + cx + x, int(y), ox + cx + x, 86), '#6a8a7a')
                px(d, ox + cx + x, int(y), '#8aa494')
        rect(d, (ox + 130, 70, ox + 133, 76), '#f4f0e6')                # 灯塔
        rect(d, (ox + 130, 68, ox + 133, 69), '#c83a34')
        return im
    return tiled(P, base, objs)


def road_shore(P=720):
    """海边的一排礁石、防波块和黑松（y 100–132），下沿是路基的草坡"""
    def base(im, W3):
        d = ImageDraw.Draw(im)
        for x in range(W3):
            y = 120 + 3 * math.sin(x / 11.0) + 2 * math.sin(x / 4.3)
            line(d, (x, int(y), x, 134), '#6a8a4a')
            px(d, x, int(y), '#8aaa5a')
        noise_specks(im, (0, 122, W3, 134), ['#5a7a3e', '#7a9a52'], W3 // 2, 3)
        return im
    def objs(im, ox):
        d = ImageDraw.Draw(im)
        rng = np.random.RandomState(8)
        for k in range(9):                                             # 礁石
            x, w = ox + rng.randint(0, P), rng.randint(14, 30)
            y = 118 + rng.randint(-2, 3)
            poly(d, [(x, y + 6), (x + w * .3, y - 6), (x + w * .7, y - 4), (x + w, y + 6)], '#5a5450')
            poly(d, [(x + w * .3, y - 6), (x + w * .5, y - 5), (x + w * .45, y + 2)], '#7a7470')
        for k in range(6):                                             # 消波块（四脚的）
            x = ox + 300 + k * 13
            poly(d, [(x, 120), (x + 6, 110), (x + 12, 120)], '#a8a49c')
            rect(d, (x + 4, 112, x + 8, 122), '#c8c4bc')
        for x, h, sd in ((80, 70, 1), (190, 58, 2), (520, 76, 3), (640, 52, 4)):
            im = pine(im, ox + x, 128, h=h, seed=sd)
        return im
    return tiled(P, base, objs)


def road_near(P=960):
    G = 136
    def base(im, W3):
        d = ImageDraw.Draw(im)
        rect(d, (0, 124, W3, G), '#7a8a5a')                             # 护栏外的路肩草
        noise_specks(im, (0, 124, W3, G), ['#6a7a4a', '#94a46a'], W3, 9)
        im = asphalt(im, 0, W3, G - 2, H, cols=('#55555c', '#4c4c52', '#606068', '#6e6e76'), dash=False)
        d = ImageDraw.Draw(im)
        rect(d, (0, G, W3, G + 1), '#f0ece4')                           # 外侧线
        rect(d, (0, 178, W3, 179), '#f0ece4')
        for y in (151, 165):                                           # 车道虚线
            for x in range(0, W3, 40):
                rect(d, (x, y, x + 19, y), '#f0ece4')
        for y in range(G + 3, H, 3):                                   # 车辙（两道略深的带）
            pass
        for yb in (146, 160, 174):
            for x in range(0, W3, 2):
                if (x // 2 + yb) % 3 == 0:
                    px(d, x, yb, '#48484e')
        # 护栏：白色波形板（y 120–126），每 16 px 一根柱
        rect(d, (0, 120, W3, 126), '#e8e4dc')
        line(d, (0, 120, W3, 120), '#ffffff')
        line(d, (0, 123, W3, 123), '#c8c4bc')
        line(d, (0, 126, W3, 126), '#a8a49c')
        for x in range(4, W3, 16):
            rect(d, (x, 118, x + 2, 134), '#d8d4cc')
            line(d, (x + 2, 118, x + 2, 134), '#a8a49c')
        return im
    def objs(im, ox):
        d = ImageDraw.Draw(im)
        poles = [ox + x for x in (140, 460, 780)]
        for x in poles:                                                # 电线杆（种在护栏外）
            im = pole(im, x, 124, h=112)
        d = ImageDraw.Draw(im)
        tops = [(x, 124 - 112 + 6) for x in [poles[-1] - P] + poles + [poles[0] + P]]
        im = wires(im, tops, sag=22)
        d = ImageDraw.Draw(im)
        for x in range(ox + 60, ox + P, 80):                           # 反光柱（橙色）
            rect(d, (x, 110, x + 1, 120), '#f4f0e6')
            rect(d, (x, 110, x + 1, 113), '#f08a28')
        # 蓝色路牌（悬臂式）：杜王町 ← → S市
        sx = ox + 600
        rect(d, (sx, 40, sx + 3, 124), '#9a9ea4')
        line(d, (sx + 3, 40, sx + 3, 124), '#6a6e74')
        rect(d, (sx - 2, 44, sx + 64, 46), '#9a9ea4')
        rect(d, (sx + 8, 48, sx + 62, 80), '#f4f0e6')
        rect(d, (sx + 9, 49, sx + 61, 79), '#1e4a9a')
        kanji(im, sx + 12, 51, '杜王町', '#f4f0e6')
        kanji(im, sx + 12, 65, 'S 市', '#f4f0e6')
        d = ImageDraw.Draw(im)
        poly(d, [(sx + 52, 54), (sx + 58, 57), (sx + 52, 60)], '#f4f0e6')
        poly(d, [(sx + 58, 68), (sx + 52, 71), (sx + 58, 74)], '#f4f0e6')
        # 国道号牌（倒三角盾）
        gx = ox + 300
        rect(d, (gx + 7, 90, gx + 8, 124), '#9a9ea4')
        poly(d, [(gx, 76), (gx + 16, 76), (gx + 16, 84), (gx + 8, 92), (gx, 84)], '#f4f0e6')
        poly(d, [(gx + 1, 77), (gx + 15, 77), (gx + 15, 83), (gx + 8, 90), (gx + 1, 83)], '#1e4a9a')
        digits(d, gx + 3, 79, '45', '#f4f0e6')
        # 限速牌（红圈 50）
        lx = ox + 870
        rect(d, (lx + 6, 96, lx + 7, 124), '#9a9ea4')
        ellipse(d, (lx, 84, lx + 13, 97), '#d83a2e')
        ellipse(d, (lx + 2, 86, lx + 11, 95), '#f4f0e6')
        digits(d, lx + 3, 88, '50', '#2a4a8a')
        return im
    return tiled(P, base, objs)


def national_road():
    W = 960
    sky, sea, shore, near = road_sky(), road_sea(), road_shore(), road_near()
    layers = {'sky': sky, 'sea': sea, 'shore': shore, 'near': near}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(lane_top=[0, 144], lane_mid=[0, 158], lane_bot=[0, 172], lane_lines=[151, 165], guardrail=[0, 122],
                             walk_x=[8, 952]),
                layers=[{'type': 'wrap', 'image': 'bg/national_road/sky', 'k': 0.05, 'vx': 6, 'y': 0},
                        {'type': 'wrap', 'image': 'bg/national_road/sea', 'k': 0.2, 'vx': 36, 'y': 0},
                        {'type': 'wrap', 'image': 'bg/national_road/shore', 'k': 0.55, 'vx': 120, 'y': 0},
                        {'type': 'wrap', 'image': 'bg/national_road/near', 'k': 1, 'vx': 260, 'y': 0},
                        {'type': 'tint', 'color': '#ff9040', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = new(W, H)
    for im in (sky, sea, shore, near):
        t = Image.new('RGBA', (W, H))
        for x in range(0, W, im.width):
            t.paste(im, (x, 0))
        pv.alpha_composite(t)
    preview('national_road', {'room': pv}, ['room'], W)
    save_layers('national_road', layers, meta)
    return meta


# ============================================================ 医院走廊 hospital_corridor（640 宽，白天）
#   杜王町综合医院三楼：日光灯、米白墙 + 浅绿墙裙和木扶手、五间病房的推拉门（301–305，304 门口的名牌写着“噴上”），
#   中间一扇大窗，右端护士站。地上是会反光的浅绿胶地板。
HC = dict(wall='#eeeadc', wall2='#e2dccb', ceil='#f4f2ea', ceil2='#d8d4c8', wain='#a8cbb8', wain2='#94b8a4', rail='#b88e64',
          door='#d8c4a0', door2='#c4ac84', floor='#b8c8bc', floor2='#a8bcb0', floor3='#cad8cc')


def hc_near():
    W, G = 640, 134
    P = HC
    im = new(W, H, P['wall'])
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 12), P['ceil'])
    for x in range(0, W, 32):
        line(d, (x, 0, x, 12), P['ceil2'])
    line(d, (0, 12, W, 12), P['ceil2'])
    line(d, (0, 13, W, 13), '#c8c4b8')
    lights = []
    for x in range(40, W, 80):                                          # 日光灯
        rect(d, (x - 14, 3, x + 14, 8), '#c8c8c4')
        rect(d, (x - 12, 4, x + 12, 7), '#f8fcff')
        lights.append(x)
    # 墙裙（y 100–G）+ 扶手（y 96）
    rect(d, (0, 100, W, G), P['wain'])
    line(d, (0, 100, W, 100), '#c4e0d0')
    for x in range(0, W, 12):
        line(d, (x, 101, x, G), P['wain2'])
    rect(d, (0, G - 4, W, G), '#7a9a88')
    rect(d, (0, 94, W, 97), P['rail'])
    line(d, (0, 94, W, 94), '#d8ae84')
    line(d, (0, 97, W, 97), '#8a6444')
    for x in range(10, W, 60):
        rect(d, (x, 97, x + 2, 101), '#a8a8a8')
    doors = {}
    # 病房推拉门：宽 34，门上一条竖窗，门把手，右边门牌（房号 + 名牌）
    for x, no in ((30, '301'), (130, '302'), (300, '303'), (400, '304'), (500, '305')):
        rect(d, (x - 3, G - 72, x + 37, G), '#c8c2b0')
        rect(d, (x, G - 69, x + 34, G - 1), P['door'])
        bevel(d, (x, G - 69, x + 34, G - 1), '#e8d8b8', P['door2'])
        rect(d, (x + 6, G - 62, x + 10, G - 34), '#a8c8d8')
        line(d, (x + 7, G - 61, x + 7, G - 50), '#d0e4ee')
        rect(d, (x + 26, G - 40, x + 28, G - 26), '#9a9a9a')
        rect(d, (x + 29, G - 69, x + 34, G - 1), P['door2'])          # 推开的另半扇（叠在后面）
        rect(d, (x - 3, G - 76, x + 37, G - 72), '#b8b2a0')
        # 门牌
        rect(d, (x + 40, 52, x + 66, 82), '#f8f8f4')
        bevel(d, (x + 40, 52, x + 66, 82), '#ffffff', '#b8b8b0')
        rect(d, (x + 40, 52, x + 66, 59), '#4a8a6a')
        digits(d, x + 47, 53, no, '#f8f8f4')
        if no == '304':
            kanji(im, x + 41, 62, '噴上', '#2a2a30')
            d = ImageDraw.Draw(im)
            rect(d, (x + 43, 76, x + 63, 77), '#c8c8c0')
        else:
            for r in range(3):
                line(d, (x + 44, 63 + r * 6, x + 58 - (r * 4 + int(no)) % 7, 63 + r * 6), '#9a9a9a')
        doors[no] = x + 17
    # 大窗（206–286）：外面是杜王町的屋顶和远山
    wx0, wy0, wx1, wy1 = 200, 26, 284, 90
    rect(d, (wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4), '#d8d8d0')
    im = grad(im, (wx0, wy0, wx1, wy1), ('#7ab4e8', '#a0ccf0', '#cce4f6'))
    d = ImageDraw.Draw(im)
    cloud(im, wx0 + 10, wy0 + 16, 34, seed=21)
    d = ImageDraw.Draw(im)
    for x in range(wx0, wx1 + 1):
        y = 66 + 4 * math.sin(x / 12.0)
        line(d, (x, int(y), x, wy1), '#8aa8b8')
    rng = np.random.RandomState(4)
    for i in range(10):
        x = wx0 + rng.randint(-6, wx1 - wx0)
        bw, bh = rng.randint(8, 16), rng.randint(6, 16)
        rect(d, (max(wx0, x), wy1 - bh, min(wx1, x + bw), wy1), ['#e8e0d4', '#d8d0c4', '#c8c2b8'][i % 3])
        rect(d, (max(wx0, x - 1), wy1 - bh - 3, min(wx1, x + bw + 1), wy1 - bh), ['#6a7a90', '#8a6a68', '#5a6a7a'][i % 3])
    for x in (wx0 + 28, wx0 + 56):
        line(d, (x, wy0, x, wy1), '#d8d8d0')
    line(d, (wx0, 58, wx1, 58), '#d8d8d0')
    rect(d, (wx0 - 6, wy1 + 4, wx1 + 6, wy1 + 7), '#e8e8e0')
    # 窗下的长椅
    rect(d, (210, 112, 274, 116), '#4a7a9a')
    line(d, (210, 112, 274, 112), '#6a9aba')
    rect(d, (210, 102, 274, 110), '#4a7a9a')
    for lx in (214, 270):
        rect(d, (lx, 116, lx + 2, G + 2), '#8a8a8a')
    # 灭火器、轮椅
    rect(d, (100, 108, 108, 128), '#d83a2e')
    rect(d, (102, 104, 106, 108), '#2a2a30')
    line(d, (106, 106, 110, 112), '#2a2a30')
    rect(d, (96, 86, 114, 95), '#d83a2e')
    letters(d, 98, 88, 'FIRE', '#f8f8f4')
    ellipse(d, (360, 114, 380, G + 2), '#5a5a62')
    ellipse(d, (363, 117, 377, G - 1), '#eeeadc')
    rect(d, (366, 104, 386, 108), '#4a6aa0')
    rect(d, (382, 92, 386, 110), '#4a6aa0')
    line(d, (382, 92, 390, 92), '#8a8a8a')
    line(d, (366, 108, 362, G + 2), '#8a8a8a')
    # ---------------- 护士站（570–640）
    nx = 570
    rect(d, (nx, 30, W, G), '#e6e2d4')
    rect(d, (nx, 30, W, 36), '#4a8a6a')
    letters(d, nx + 6, 31, 'NURSE STATION', '#f8f8f4')
    rect(d, (nx + 4, 44, W, 84), '#c8dce4')                             # 里面的玻璃
    for x in range(nx + 8, W, 14):
        rect(d, (x, 60, x + 8, 76), '#f4f4ec')                          # 病历夹
        rect(d, (x, 60, x + 8, 62), ('#d83a2e', '#4a7aca', '#e8b030')[(x // 14) % 3])
    rect(d, (nx, 84, W, 104), '#d8c4a0')                                # 柜台
    line(d, (nx, 84, W, 84), '#f0dcb8')
    rect(d, (nx, 104, W, G), '#c4ac84')
    for x in range(nx + 6, W, 20):
        bevel(d, (x, 108, x + 16, G - 4), '#d8c4a0', '#a8946c')
    rect(d, (nx + 18, 78, nx + 26, 84), '#f8f8f4')                      # 柜台上的小花
    for k in range(3):
        ellipse(d, (nx + 17 + k * 3, 73, nx + 20 + k * 3, 76), ('#f2a0b4', '#f8e070', '#f2a0b4')[k])
    # ---------------- 地板：浅绿胶地板，越往下越亮，日光灯在地上的倒影
    im = grad(im, (0, G, W, H), (P['floor2'], P['floor'], P['floor3']))
    d = ImageDraw.Draw(im)
    for y in (G + 12, G + 28):
        line(d, (0, y, W, y), '#a0b4a8')
    for x in lights:
        for k, (y, w_) in enumerate(((G + 6, 10), (G + 18, 16), (G + 34, 24))):
            rect(d, (x - w_, y, x + w_, y + 1 + k), '#dce8e0')
    rect(d, (0, G, W, G + 1), '#7a9a88')
    return im, G, lights, doors, (wx0, wy0, wx1, wy1)


def hospital_corridor():
    W = 640
    near, G, lights, doors, (wx0, wy0, wx1, wy1) = hc_near()
    f = np.zeros((H, W))
    for x in lights:
        f = np.maximum(f, blob(W, x, 8, 26, 10, 1.4) * .6)
    f = np.maximum(f, blob(W, (wx0 + wx1) / 2 + 10, 158, 56, 12, 1.4) * .22)
    glow = qfield(f, (200, 220, 230))
    layers = {'near': near, 'glow': glow}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(**{f'door_{k}': [v, 146] for k, v in doors.items()}, plate_304=[454, 66], window=[242, 146],
                             bench=[242, 146], extinguisher=[104, 146], wheelchair=[374, 146], nurse_station=[605, 146],
                             walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/hospital_corridor/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'glow', 'image': 'bg/hospital_corridor/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.02},
                        {'type': 'tint', 'color': '#ff9040', 'alpha': 0.14, 'key': 'pm'}],
                fg=[])
    preview('hospital_corridor', {'room': add_glow(near, glow)}, ['room'], W)
    save_layers('hospital_corridor', layers, meta)
    return meta


# ============================================================ 病房 hospital_room（320 宽，傍晚）
#   单人病房：左边推拉门 → 床头柜（小电视、花瓶）→ 病床（床头朝左，床尾挂病历）→ 点滴架 → 右边的窗（傍晚的天）+ 陪护椅。
#   天花板上有隔帘的轨道，帘子收在床头那边。
def hospital_room():
    W, G = 320, 134
    im = new(W, H, '#efe8d8')
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 10), '#f6f2e8')
    line(d, (0, 10, W, 10), '#d8d2c2')
    rect(d, (0, 106, W, G), '#d8cdb4')
    line(d, (0, 106, W, 106), '#e8dfc8')
    rect(d, (0, G - 3, W, G), '#a89a80')
    rect(d, (0, 76, W, 78), '#c8c0aa')                                  # 墙上的设备带（氧气、呼叫铃）
    # 推拉门
    rect(d, (10, G - 74, 50, G), '#c8c2b0')
    rect(d, (13, G - 71, 47, G - 1), '#d8c4a0')
    bevel(d, (13, G - 71, 47, G - 1), '#e8d8b8', '#c4ac84')
    rect(d, (19, G - 64, 23, G - 36), '#a8c8d8')
    rect(d, (39, G - 42, 41, G - 28), '#9a9a9a')
    # 隔帘轨道 + 收起的帘子（淡绿）
    line(d, (60, 14, 230, 14), '#b8b8b0')
    for x in range(62, 82, 3):
        line(d, (x, 15, x + (x % 2), 100), '#b8d4c4')
        line(d, (x + 1, 15, x + 1, 100), '#cce4d6')
    rect(d, (62, 98, 82, 102), '#a8c4b4')
    # 床头墙上的设备板（呼叫铃、氧气接口）
    rect(d, (92, 66, 140, 82), '#e6e2d6')
    bevel(d, (92, 66, 140, 82), '#f6f4ec', '#b8b4a8')
    ellipse(d, (96, 70, 102, 76), '#4a8a6a')
    ellipse(d, (106, 70, 112, 76), '#e8e4dc')
    rect(d, (118, 70, 124, 78), '#d83a2e')
    line(d, (121, 78, 126, 102), '#f4f0e6')
    # 床头柜 + 小电视 + 花瓶
    rect(d, (86, 92, 96, 92), '#000000')
    rect(d, (88, 102, 112, G + 2), '#d8c4a0')
    bevel(d, (88, 102, 112, G + 2), '#e8d8b8', '#a8946c')
    line(d, (88, 116, 112, 116), '#a8946c')
    rect(d, (98, 108, 102, 109), '#9a9a9a')
    rect(d, (90, 86, 106, 100), '#3a3a40')
    rect(d, (92, 88, 104, 97), '#6a8aa8')
    line(d, (93, 89, 96, 89), '#9ab8d0')
    rect(d, (106, 92, 111, 101), '#e8f2f6')
    for k, (fx, fy) in enumerate(((106, 86), (109, 83), (112, 87))):
        line(d, (108, 92, fx, fy + 2), '#4e8a52')
        ellipse(d, (fx - 2, fy - 1, fx + 2, fy + 3), ('#f8e070', '#f08a4a', '#f8e070')[k])
    # 病床（床头 116，床尾 214）
    bx0, bx1 = 116, 214
    rect(d, (bx0, 96, bx0 + 4, G + 6), '#c8ccd4')                       # 床头板
    d.pieslice((bx0 - 2, 90, bx0 + 6, 102), 180, 360, fill=C('#c8ccd4'))
    rect(d, (bx1 - 4, 108, bx1, G + 6), '#c8ccd4')                      # 床尾板
    rect(d, (bx1 + 1, 112, bx1 + 9, 124), '#f4f4ec')                    # 病历夹
    rect(d, (bx1 + 1, 112, bx1 + 9, 114), '#4a7aca')
    rect(d, (bx0 + 4, 116, bx1 - 4, 124), '#9aa4b4')                    # 床架
    line(d, (bx0 + 4, 124, bx1 - 4, 124), '#6a7484')
    rect(d, (bx0 + 4, 106, bx1 - 4, 116), '#f8f8f4')                    # 床垫 + 被子
    poly(d, [(bx0 + 30, 104), (bx1 - 4, 104), (bx1 - 2, 118), (bx0 + 28, 118)], '#e8eef4')
    line(d, (bx0 + 30, 104, bx1 - 4, 104), '#ffffff')
    for x in range(bx0 + 40, bx1 - 6, 14):
        line(d, (x, 106, x + 2, 117), '#d0d8e2')
    ellipse(d, (bx0 + 6, 98, bx0 + 28, 108), '#ffffff')                 # 枕头
    line(d, (bx0 + 8, 106, bx0 + 26, 106), '#dcdcd8')
    for lx in (bx0 + 8, bx1 - 10):                                      # 床脚 + 轮子
        rect(d, (lx, 124, lx + 2, G + 8), '#8a8e98')
        ellipse(d, (lx - 2, G + 6, lx + 4, G + 11), '#3a3a40')
    # 点滴架
    ix = 226
    line(d, (ix, 46, ix, G + 6), '#b8bcc4')
    line(d, (ix - 6, 48, ix + 6, 48), '#b8bcc4')
    rect(d, (ix - 9, 50, ix - 3, 62), '#e8f4f8')
    rect(d, (ix - 9, 56, ix - 3, 62), '#c8e4ec')
    line(d, (ix - 6, 62, ix - 14, 100), '#d8e8ee')
    for k in (-6, 0, 6):
        line(d, (ix, G + 4, ix + k, G + 8), '#8a8e98')
    # 窗（240–312）：傍晚
    wx0, wy0, wx1, wy1 = 244, 24, 310, 92
    rect(d, (wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4), '#e8e4d8')
    im = grad(im, (wx0, wy0, wx1, wy1), ('#6a6a9a', '#c88a8a', '#f4a870', '#f8d090'))
    d = ImageDraw.Draw(im)
    for x in range(wx0, wx1 + 1):
        y = 74 + 3 * math.sin(x / 9.0)
        line(d, (x, int(y), x, wy1), '#6a5a6a')
    for x in range(wx0 + 4, wx1, 12):
        rect(d, (x, 80, x + 7, wy1), '#4e4a5a')
        px(d, x + 3, 84, '#f8d890')
    ellipse(d, (wx0 + 40, 60, wx0 + 52, 72), '#fff0c0')
    line(d, ((wx0 + wx1) // 2, wy0, (wx0 + wx1) // 2, wy1), '#e8e4d8')
    rect(d, (wx0 - 8, wy1 + 4, wx1 + 6, wy1 + 7), '#f4f0e6')
    for side_x in (wx0 - 10, wx1 - 2):                                  # 窗帘（米色，拉开）
        rect(d, (side_x, wy0 - 8, side_x + 10, wy1 + 10), '#e8dcc0')
        for x in range(side_x, side_x + 10, 3):
            line(d, (x, wy0 - 8, x, wy1 + 10), '#d8caa8')
    # 陪护椅
    rect(d, (270, 112, 296, 116), '#6a8aaa')
    rect(d, (292, 96, 296, 116), '#6a8aaa')
    for lx in (272, 294):
        rect(d, (lx, 116, lx + 1, G + 6), '#8a8a8a')
    # 地板
    im = grad(im, (0, G, W, H), ('#c8c0b0', '#d4ccbc', '#ded8ca'))
    d = ImageDraw.Draw(im)
    for x in range(0, W, 24):
        line(d, (x, G + 1, x - 6, H), '#c0b8a6')
    for y in (G + 14, G + 30):
        line(d, (0, y, W, y), '#c0b8a6')
    rect(d, (0, G, W, G + 1), '#a89a80')
    # 夕照：窗投到地上的一块（往左拉长的平行四边形，抖动边）+ 窗边一圈暖光
    fl = Image.new('L', (W, H), 0)
    ImageDraw.Draw(fl).polygon([(wx0 - 6, G + 4), (wx1 - 6, G + 4), (wx1 - 70, G + 36), (wx0 - 70, G + 36)], fill=255)
    fm = mask_dither(fl, 1.5, 3)
    im = light_mix(im, tint(im, (1.1, 1.0, .82), (30, 12, 0)), fm)
    f = blob(W, (wx0 + wx1) / 2, 60, 46, 40, 2) * .2
    glow = qfield(np.clip(f, 0, 1), (255, 170, 90))
    layers = {'room': im, 'glow': glow}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(door=[30, 148], bed=[165, 150], bed_pillow=[128, 102], chart=[219, 118], drip=[226, 146],
                             tv=[98, 92], flowers=[109, 88], call_button=[121, 74], window=[277, 146], chair=[283, 148],
                             curtain=[72, 146], walk_x=[54, 312]),
                layers=[{'type': 'pano', 'image': 'bg/hospital_room/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'glow', 'image': 'bg/hospital_room/glow', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'tint', 'color': '#ff8a40', 'alpha': 0.08}],
                fg=[])
    preview('hospital_room', {'room': add_glow(im, glow)}, ['room'], W)
    save_layers('hospital_room', layers, meta)
    return meta


# ============================================================ 川尻家阁楼 kawajiri_attic（320 宽，白天，只有山墙小窗透光）
#   人字屋顶的斜椽从两边压下来，正中山墙一扇小格窗，光柱斜落到地板上、灰尘在里面飘。
#   两边堆着纸箱、旧行李箱、电风扇、圣诞装饰盒、卷起来的地毯；窗下空出一块晒得到太阳的地方（猫草待的位置，由道具画）。
#   开关：lamp = 1 拉亮梁上的灯泡（暖黄光晕，阁楼整体亮一点）。
def at_room():
    W, G = 320, 136
    im = new(W, H, '#3a2a20')
    d = ImageDraw.Draw(im)
    cx = 160
    # 山墙（中间竖的木板墙，三角形）
    poly(d, [(cx - 150, G), (cx, 6), (cx + 150, G)], '#6a4a34')
    for x in range(cx - 150, cx + 151, 10):
        top = 6 + abs(x - cx) * (G - 6) / 150
        line(d, (x, top, x, G), '#5a3e2c')
        line(d, (x + 1, top, x + 1, G), '#7a5640')
    # 两边斜屋面的底面（椽子 + 望板），越靠外越暗
    for side in (-1, 1):
        pts = [(cx, 6), (cx + side * 150, G), (cx + side * 170, G), (cx + side * 170, 0), (cx, 0)]
        poly(d, pts, '#2e2018')
        for k in range(8):                                              # 椽子（往山墙收拢的斜线）
            x_top = cx + side * (6 + k * 3)
            x_bot = cx + side * (40 + k * 18)
            line(d, (x_top, 0, x_bot + side * 120, G + 40), '#4a3424')
    im = Image.fromarray(np.array(im), 'RGBA')
    d = ImageDraw.Draw(im)
    # 山墙边上的两根斜梁 + 一根横梁（y 40）+ 中间短柱
    for side in (-1, 1):
        line(d, (cx, 4, cx + side * 156, G + 2), '#8a6448', 4)
        line(d, (cx, 2, cx + side * 156, G), '#a87a54')
    rect(d, (cx - 100, 52, cx + 100, 57), '#7a5640')
    line(d, (cx - 100, 52, cx + 100, 52), '#a87a54')
    line(d, (cx - 100, 57, cx + 100, 57), '#4a3424')
    rect(d, (cx - 3, 10, cx + 3, 52), '#7a5640')
    # 小格窗（四格）
    wx0, wy0, wx1, wy1 = cx - 18, 64, cx + 18, 96
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), '#8a6448')
    im = grad(im, (wx0, wy0, wx1, wy1), ('#bcdcf4', '#e4f0f8', '#f8f8f0'))
    d = ImageDraw.Draw(im)
    for x in range(wx0, wx1 + 1):                                       # 窗外邻居的屋顶
        if x < cx + 6:
            y = 86 + (x - wx0) * .3
            line(d, (x, int(y), x, wy1), '#5a6a80')
    line(d, (cx, wy0, cx, wy1), '#8a6448')
    line(d, (wx0, (wy0 + wy1) // 2, wx1, (wy0 + wy1) // 2), '#8a6448')
    rect(d, (wx0 - 5, wy1 + 3, wx1 + 5, wy1 + 5), '#a87a54')
    # 地板（粗木板，往近处变宽）
    y, h, row = G, 3.0, 0
    rng = np.random.RandomState(3)
    while y < H:
        yb = min(H, int(round(y + h)))
        rect(d, (0, int(y), W, yb - 1), ('#7a5a40', '#6e5038', '#84624a')[row % 3])
        line(d, (0, yb - 1, W, yb - 1), '#4a3424')
        off = rng.randint(0, 60)
        for x in range(-off, W, 70):
            line(d, (x, int(y), x, yb - 2), '#5a4030')
        y += h
        h = min(9.0, h * 1.22)
        row += 1
    # 杂物：左边
    def box(x, y1, w, h, col='#c8a070', tape='#d8c49a', label=None):
        rect(d, (x, y1 - h, x + w, y1), col)
        line(d, (x, y1 - h, x + w, y1 - h), mix(col, '#ffffff', .25))
        line(d, (x + w, y1 - h, x + w, y1), mix(col, '#000000', .3))
        rect(d, (x + w // 2 - 2, y1 - h, x + w // 2 + 2, y1 - h + 6), tape)
        line(d, (x, y1 - h // 2, x + w, y1 - h // 2), mix(col, '#000000', .12))
        if label:
            letters(d, x + 3, y1 - h + 8, label, '#4a3424')
    box(8, G + 4, 34, 26)
    box(12, G - 22, 28, 18, '#b89060', label='XMAS')
    box(44, G + 6, 26, 20, '#c8a070')
    rect(d, (74, G - 16, 104, G + 6), '#5a3a4a')                         # 旧行李箱
    bevel(d, (74, G - 16, 104, G + 6), '#7a5a6a', '#3a2232')
    rect(d, (86, G - 20, 92, G - 16), '#2a1a20')
    for x in (78, 100):
        rect(d, (x, G - 16, x + 1, G + 6), '#c8a050')
    # 电风扇（左边纸箱上）
    fx = 57
    ellipse(d, (fx - 10, G - 44, fx + 10, G - 24), '#8aa8c0')
    ellipse(d, (fx - 7, G - 41, fx + 7, G - 27), '#c8dce8')
    ellipse(d, (fx - 2, G - 36, fx + 2, G - 32), '#4a5a6a')
    rect(d, (fx - 1, G - 24, fx + 1, G - 14), '#d8d4cc')
    # 右边：卷起的地毯（斜靠）、一摞旧杂志、木头三屉柜、鸟笼
    poly(d, [(250, G + 6), (258, G + 6), (296, 70), (290, 66)], '#8a2a34')
    ellipse(d, (288, 64, 298, 72), '#a84a4a')
    ellipse(d, (291, 66, 295, 70), '#5a1a24')
    rect(d, (214, G - 26, 246, G + 6), '#8a6448')
    for k in range(3):
        y0 = G - 24 + k * 10
        rect(d, (216, y0, 244, y0 + 8), '#9a7454')
        bevel(d, (216, y0, 244, y0 + 8), '#b08a64', '#6a4a34')
        rect(d, (228, y0 + 3, 232, y0 + 4), '#d8c070')
    for k in range(5):
        rect(d, (300, G + 6 - k * 3 - 3, 318 - (k % 2) * 2, G + 6 - k * 3), ('#e8e0d0', '#d8483c', '#f4f0e6', '#4a7aca', '#e8e0d0')[k])
    rect(d, (222, G - 44, 238, G - 26), '#00000000')
    d.arc((222, G - 50, 238, G - 34), 180, 360, fill=C('#c8a050'))
    for x in range(222, 239, 3):
        line(d, (x, G - 42, x, G - 26), '#c8a050')
    line(d, (222, G - 26, 238, G - 26), '#c8a050')
    # 灯泡（梁上吊下来）
    line(d, (cx + 40, 57, cx + 40, 70), '#2a2a30')
    rect(d, (cx + 38, 70, cx + 42, 73), '#6a6a6a')
    ellipse(d, (cx + 37, 72, cx + 43, 79), '#e8e0c0')
    # 地板上一层灰（窗下的光斑里能看到猫草待过的一圈干净的地方：道具自己画，这里留空）
    return im, G, (wx0, wy0, wx1, wy1), cx


def kawajiri_attic():
    W = 320
    room, G, (wx0, wy0, wx1, wy1), cx = at_room()
    # 光：小窗往右下斜落到地板（太阳在左上），地上一块平行四边形光斑
    KD, SL = .9, -.5
    def proj(x, y):
        yf = G + (wy1 + 40 - y) * KD * .55
        return x - (yf - G) * SL, min(179.0, yf)
    quad = [proj(wx0, wy1), proj(wx1, wy1), proj(wx1, wy0), proj(wx0, wy0)]
    fl = Image.new('L', (W, H), 0)
    ImageDraw.Draw(fl).polygon([(int(a), int(b)) for a, b in quad], fill=255)
    fm = mask_dither(fl, 1.2, 3)
    fm[:G + 1] = 0
    base = tint(room, (.82, .78, .80), (0, 0, 4))
    lit = tint(room, (1.25, 1.12, .9), (30, 20, 4))
    out = light_mix(base, lit, fm)
    a, r = np.array(out), np.array(room)
    a[wy0:wy1 + 1, wx0:wx1 + 1] = r[wy0:wy1 + 1, wx0:wx1 + 1]
    out = Image.fromarray(a, 'RGBA')
    shaft = Image.new('L', (W, H), 0)
    pts = [(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)] + quad
    xs = [p[0] for p in pts]
    hull = [(wx0, wy0), (wx1, wy0), quad[1], quad[0]] if quad[0][0] > wx0 else [(wx0, wy0), (wx1, wy0), quad[1], quad[0]]
    ImageDraw.Draw(shaft).polygon([(int(a_), int(b_)) for a_, b_ in hull], fill=255)
    sh = np.array(shaft.filter(ImageFilter.BoxBlur(2))).astype(float) / 255
    yy = np.mgrid[0:H, 0:W][0].astype(float)
    fall = np.clip((yy - wy0) / 30, 0, 1) * (1 - .5 * np.clip((yy - wy1) / (H - wy1), 0, 1))
    f = sh * .16 * fall
    f[wy0:wy1 + 1, wx0:wx1 + 1] = 0
    fq = np.round(f * 24) / 24
    glow = Image.fromarray(np.dstack([np.clip(fq[..., None] * np.array((255, 220, 160), float), 0, 255).astype(np.uint8),
                                      np.where(fq > 0, 255, 0).astype(np.uint8)[..., None]]).reshape(H, W, 4), 'RGBA')
    ys, xs_ = np.where(sh > .5)
    bx0, by0, bx1, by1 = int(xs_.min()), int(ys.min()), int(xs_.max()) + 1, int(ys.max()) + 1
    region = lambda x, y: sh[min(H - 1, int(y + by0)), min(W - 1, int(x + bx0))] > .6 and not (wx0 <= x + bx0 <= wx1 and wy0 <= y + by0 <= wy1)
    dust = dust_strip(bx1 - bx0, by1 - by0, n=12, count=20, region=region, seed=17)
    lamp = qfield(np.clip(blob(W, cx + 40, 76, 70, 60, 1.6) * .55 + blob(W, cx + 40, 158, 70, 14, 1.2) * .3, 0, 1), (200, 150, 70))
    bulb = new(W, H)
    bd = ImageDraw.Draw(bulb)
    ellipse(bd, (cx + 37, 72, cx + 43, 79), '#fff6c8')
    px(bd, cx + 39, 74, '#ffffff')
    sun = (quad[0][0] + quad[1][0]) / 2
    layers = {'room': out, 'glow': glow, 'dust': dust, 'lamp': lamp, 'bulb': bulb}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(window=[cx, 80], sunspot=[int(sun), 156], hatch=[60, 160], boxes=[30, 146], suitcase=[89, 146],
                             fan=[57, 110], chest=[230, 146], birdcage=[230, 100], rug_roll=[274, 146], bulb=[cx + 40, 76],
                             beam=[cx, 54], walk_x=[16, 304]),
                layers=[{'type': 'pano', 'image': 'bg/kawajiri_attic/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/kawajiri_attic/bulb', 'k': 1, 'x': 0, 'y': 0, 'key': 'lamp'},
                        {'type': 'glow', 'image': 'bg/kawajiri_attic/lamp', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.06, 'key': 'lamp'},
                        {'type': 'glow', 'image': 'bg/kawajiri_attic/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.03},
                        {'type': 'strip', 'image': 'bg/kawajiri_attic/dust', 'n': 12, 'fps': 4, 'x': bx0, 'y': by0, 'k': 1},
                        {'type': 'tint', 'color': '#2a1a3a', 'alpha': 0.12}],
                fg=[])
    pv = add_glow(out, glow)
    pv.alpha_composite(dust.crop((0, 0, bx1 - bx0, by1 - by0)), (bx0, by0))
    preview('kawajiri_attic', {'room': pv}, ['room'], W)
    pl = pv.copy()
    pl.alpha_composite(bulb)
    preview('kawajiri_attic_lamp', {'room': add_glow(pl, lamp)}, ['room'], W)
    save_layers('kawajiri_attic', layers, meta)
    return meta


SCENES = {'hospital_corridor': hospital_corridor, 'hospital_room': hospital_room, 'kawajiri_attic': kawajiri_attic, 'national_road': national_road, 'rohan_parlor': rohan_parlor, 'route_tunnel': route_tunnel}


def main(keys):
    path = os.path.join(LIB.META, 'bg_ch9.json')
    meta = LIB.load_json(path, {}) or {}
    for k in keys or SCENES:
        meta[k] = SCENES[k]()
        print('背景', k)
    LIB.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
