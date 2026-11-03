# 第四部第4章（杜王港 / 辣妹与透明宝宝）的背景：5 张，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_ch4.json（build_p4.py 会把 _meta/bg_*.json 并进 bg.json）。
#   用法：python3 第四部/tools/art/p4_bg_ch4.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   图层 pack 一律 'ch4'（打包成 data/img_bg_ch4.js，进第4章时才加载）。
#   morioh_map、morioh_road 沿用序章；客厅夜景是序章 higashikata_living 的变体，做成本章的新 key higashikata_tvnight。
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
import p4_bg as BG  # noqa: E402
from p4_bg import far_lighthouse, preview, save_layers  # noqa: E402

PACK = 'ch4'
H = 180

# 3×5 的大写字母（船名、集装箱、标牌）
LET = {'A': ['010', '101', '111', '101', '101'], 'B': ['110', '101', '110', '101', '110'], 'F': ['111', '100', '110', '100', '100'], 'C': ['011', '100', '100', '100', '011'], 'D': ['110', '101', '101', '101', '110'],
       'E': ['111', '100', '110', '100', '111'], 'G': ['011', '100', '101', '101', '011'], 'H': ['101', '101', '111', '101', '101'],
       'I': ['111', '010', '010', '010', '111'], 'K': ['101', '101', '110', '101', '101'], 'L': ['100', '100', '100', '100', '111'],
       'M': ['10001', '11011', '10101', '10001', '10001'], 'N': ['1001', '1101', '1011', '1001', '1001'],
       'O': ['010', '101', '101', '101', '010'], 'P': ['110', '101', '110', '100', '100'], 'R': ['110', '101', '110', '101', '101'],
       'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'], 'U': ['101', '101', '101', '101', '111'],
       'W': ['10001', '10001', '10101', '11011', '10001'], 'Y': ['101', '101', '010', '010', '010'],
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


def field_q(f, levels=6):
    h, w = f.shape
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    return np.clip(np.floor(f * levels + bay) / levels, 0, 1)


def glow_from_field(f, col, levels=6):
    """强度场 → lighter 叠加用的光晕图（颜色即亮度），抖动量化同 p4_bg.lamp_glow"""
    fq = field_q(f, levels)
    h, w = f.shape
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * np.array(col, float), 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def ell_field(w, h, cx, cy, rx, ry, p=1.4):
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(1 - r, 0, 1) ** p


def sky(w, cols, y1=120, seed=1, clouds=True, cl=('#ffffff', '#e8f0fa', '#c4d4ea')):
    im = new(w, H, cols[-1])
    im = grad(im, (0, 0, w, y1), cols)
    if clouds:
        rng = np.random.RandomState(seed)
        for i in range(max(1, int(w / 120))):
            cloud(im, rng.randint(0, w - 50), rng.randint(14, 54), rng.randint(28, 62), seed=seed * 10 + i, cols=cl)
    return im


def sea(im, y0, y1, cols=('#4a88c0', '#3c78b0', '#2e6496', '#245478'), glint='#a8d0f0', seed=3):
    """海面：上浅下深的渐变 + 横向短亮线"""
    x1 = im.width
    im = grad(im, (0, y0, x1, y1), cols)
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    line(d, (0, y0, x1, y0), mix(cols[0], '#ffffff', .35))
    for _ in range(int(x1 * (y1 - y0) / 90)):
        y = rng.randint(y0 + 1, y1)
        x = rng.randint(0, x1)
        L = 1 + int(3 * (y - y0) / max(1, y1 - y0)) + rng.randint(0, 3)
        line(d, (x, y, x + L, y), glint if rng.rand() < .6 else mix(glint, cols[1], .5))
    return im


def wave_tile(w, h, n=1, cols=('#cfe6f8', '#8ec0e8'), seed=5, density=60):
    """海面闪光的循环图块（wrap 层用 vx 慢慢平移）"""
    im = new(w, h)
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    for _ in range(int(w * h / density)):
        y = rng.randint(0, h)
        x = rng.randint(0, w)
        L = 1 + int(4 * y / max(1, h)) + rng.randint(0, 2)
        for k in range(L):
            px(d, (x + k) % w, y, cols[0] if k == 0 or rng.rand() < .5 else cols[1])
    return im


def round_tree(img, x, ground, h=70, r=26, seed=0, cols=('#2a5a34', '#3e7a40', '#5a9a4e', '#86bc64'),
               trunk=('#5a4234', '#3e2c22', '#7a5c48')):
    """阔叶树（公园、空地边）：树干 + 一团团圆冠，暗面在右下"""
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(img)
    top = ground - h
    rect(d, (x - 2, top + r, x + 2, ground), trunk[0])
    line(d, (x - 2, top + r, x - 2, ground), trunk[2])
    line(d, (x + 2, top + r, x + 2, ground), trunk[1])
    line(d, (x, top + r + 8, x - 8, top + r - 2), trunk[0])
    line(d, (x + 1, top + r + 4, x + 9, top + r - 4), trunk[0])
    cy = top + r * .9
    blobs = [(x + rng.uniform(-r * .7, r * .7), cy + rng.uniform(-r * .55, r * .4), rng.uniform(r * .42, r * .62)) for _ in range(9)]
    for bx, by, br in blobs:
        ellipse(d, (bx - br, by - br * .85, bx + br, by + br * .85), cols[0])
    for bx, by, br in blobs:
        ellipse(d, (bx - br * .9, by - br * .85, bx + br * .55, by + br * .4), cols[1])
    for bx, by, br in blobs:
        ellipse(d, (bx - br * .7, by - br * .8, bx + br * .1, by - br * .15), cols[2])
    for bx, by, br in blobs[:4]:
        line(d, (bx - br * .5, by - br * .7, bx - br * .1, by - br * .7), cols[3])
    for bx, by, br in blobs[3:]:                     # 冠里零星的暗点（只点在叶团里面）
        for _ in range(4):
            a_, rr = rng.uniform(0, 2 * np.pi), rng.uniform(0, br * .6)
            px(d, bx + rr * np.cos(a_), by + rr * .7 * np.sin(a_), cols[0] if rng.rand() < .6 else cols[2])
    return img


def grass_ground(img, x0, x1, y0, y1, seed=0, cols=('#6a9a4a', '#5a8a40', '#7eac56', '#94c068', '#4a7a36')):
    """草地：越往下（近）草叶越长越稀"""
    d = ImageDraw.Draw(img)
    rect(d, (x0, y0, x1, y1), cols[0])
    rng = np.random.RandomState(seed)
    for _ in range(int((x1 - x0) * (y1 - y0) / 5)):
        x = rng.randint(x0, x1)
        y = rng.randint(y0, y1)
        k = (y - y0) / max(1, y1 - y0)
        L = 1 + int(k * 3 * rng.rand())
        c = cols[rng.choice([1, 2, 3, 4], p=[.35, .3, .15, .2])]
        line(d, (x, y, x + rng.randint(-1, 2) * (k > .5), y - L), c)
    return img


def dirt(img, box, seed=0, cols=('#b49a72', '#a48a64', '#c4ac84', '#8e7656')):
    """泥土地（空地裸露的地方）：椭圆斑块 + 碎石点"""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    rng = np.random.RandomState(seed)
    w_, h_ = x1 - x0, y1 - y0
    m = np.zeros((img.height, img.width))
    yy, xx = np.mgrid[0:img.height, 0:img.width].astype(float)
    for _ in range(6):                               # 几个椭圆叠成不规则的一块，边缘抖动着溶进草里
        cx, cy = x0 + rng.uniform(.25, .75) * w_, y0 + rng.uniform(.35, .65) * h_
        rx, ry = rng.uniform(.22, .4) * w_, rng.uniform(.3, .5) * h_
        m = np.maximum(m, np.clip(1 - np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2), 0, 1))
    q = field_q(np.clip(m * 2.2, 0, 1), 3)
    a = np.array(img)
    a[q >= .34] = (*c3(cols[1]), 255)
    a[q >= .67] = (*c3(cols[0]), 255)
    a[(q >= 1) & ((xx + yy * 3) % 7 == 0)] = (*c3(cols[2]), 255)
    img.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(img)
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    rx, ry = rx * .7, ry * .7
    for _ in range(int(rx * ry / 4)):
        a, rr = rng.uniform(0, 2 * np.pi), np.sqrt(rng.rand()) * .95
        px(d, cx + rr * rx * np.cos(a), cy + rr * ry * np.sin(a), cols[rng.choice([1, 2, 3])])
    return img


# ============================================================ 东方家客厅夜景 higashikata_tvnight（480 宽）
#   序章客厅（p4_bg.higashikata_living）同一张图转成夜里：只开着电视，屏幕的蓝白光照到沙发和地板；窗外是夜里的邻居家。
#   电视前地上加一台游戏机和手柄（仗助在打游戏），电视柜左边护墙板上一个插座（发光的手钻进去的地方）。
#   层：room（夜景底）→ glow（电视光，闪）→ lit（key 'lamp'：妈妈开灯，整屋换成暖光版，盖掉电视光）
#      → screen（游戏画面 4 帧）→ snow（key 'snow'：雪花屏 6 帧，手伸出来的时候）
TVX0, TVY0, TVX1, TVY1 = 310, 72, 340, 96


def tvnight_base():
    got = {}
    old_s, old_p = BG.save_layers, BG.preview
    BG.save_layers = lambda key, layers, meta: got.update(layers=layers, meta=meta) or meta
    BG.preview = lambda *a, **k: None
    try:
        BG.higashikata_living()
    finally:
        BG.save_layers, BG.preview = old_s, old_p
    return got['layers']['room'].copy()


def higashikata_tvnight():
    W, G = 480, 134
    im = tvnight_base()
    d = ImageDraw.Draw(im)
    # ---- 电视前的游戏机 + 手柄线（画在转夜景之前，跟着一起变暗）
    rect(d, (316, 140, 334, 145), '#5a5a62')
    line(d, (316, 140, 334, 140), '#8a8a92')
    rect(d, (318, 142, 322, 143), '#2a2a30')
    px(d, 331, 142, '#e04040')
    rect(d, (316, 146, 334, 146), '#3a3a40')
    pts = [(318, 145), (312, 150), (304, 154), (296, 156)]
    for a, b in zip(pts, pts[1:]):
        line(d, (*a, *b), '#2a2a30')
    rect(d, (288, 155, 298, 159), '#6a6a72')
    px(d, 290, 157, '#2a2a30'); px(d, 296, 156, '#d04040'); px(d, 295, 158, '#4060d0')
    # 插座（电视柜左边的护墙板上）+ 电视插头的线
    rect(d, (285, 120, 292, 128), '#ece6d6')
    bevel(d, (285, 120, 292, 128), '#fffaf0', '#b8b09e')
    for yy in (122, 125):
        px(d, 287, yy, '#3a3a3a'); px(d, 290, yy, '#3a3a3a')
    line(d, (292, 125, 298, 128), '#2a2a30')
    # ---- 窗外改夜里：深蓝天、邻居家的剪影、一扇亮着的窗
    wx0, wy0, wx1, wy1 = 58, 26, 138, 94
    im = grad(im, (wx0, wy0, wx1, wy1), ('#101830', '#16203e', '#1e2a4c', '#243258'))
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(8)
    for _ in range(14):
        px(d, rng.randint(wx0, wx1), rng.randint(wy0, 56), '#c8d0f0' if rng.rand() < .5 else '#8a96c0')
    d.polygon([(wx0, 66), (78, 58), (104, 58), (122, 66), (wx1, 66), (wx1, wy1), (wx0, wy1)], fill=C('#0c1020'))
    rect(d, (wx0, 66, wx1, wy1), '#141a2c')
    rect(d, (88, 72, 102, 84), '#ffd890')
    line(d, (95, 72, 95, 84), '#8a6a3a')
    rect(d, (88, 82, 102, 84), '#e8b868')
    rect(d, (wx0, 86, wx1, wy1), '#0a0e1a')
    line(d, (wx0, 86, wx1, 86), '#1e2638')
    rect(d, (97, wy0, 99, wy1), '#f2ead8')
    line(d, (wx0, 60, wx1, 60), '#f2ead8')
    # 开灯以后的样子（key 'lamp'）：原来的颜色偏暖一点，窗外还是夜里
    lit_room = quantize_like(tint(im.copy(), (1.0, .9, .74), (8, 3, 0)), 64)
    # ---- 整屋转夜里：压暗偏蓝，窗外那扇亮窗和电视屏幕之后另外补
    a = np.array(im).astype(float)
    win = np.zeros(a.shape[:2], bool)
    win[wy0:wy1, wx0:wx1] = True
    lum = a[..., :3].mean(axis=2, keepdims=True)
    night = a[..., :3] * .5 + lum * .5
    night = night * np.array([.26, .29, .46]) + np.array([6, 8, 18])
    keep = win & (a[..., 0] > 200) & (a[..., 2] < 170)          # 邻居亮着的窗
    sky_px = win & (a[..., :3].max(axis=2) < 60)               # 窗外的夜空本来就暗
    a[..., :3] = np.where((keep | sky_px)[..., None], a[..., :3], night)
    im = quantize_like(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'), 64)
    d = ImageDraw.Draw(im)
    # 电视屏幕本身（屏幕层盖在这上面，这里是底色）
    rect(d, (TVX0, TVY0, TVX1, TVY1), '#a8c8f0')
    # 电视对面的东西被照亮的一圈：沙发右扶手、地毯右半、电视柜顶的边
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    f = np.clip(1 - np.sqrt(((xx - 325) / 120) ** 2 + ((yy - 120) / 70) ** 2), 0, 1) ** 1.3
    front = ((xx < 300) | (yy > 130)) & (xx < 364)                            # 只照电视前面（电视柜后面的墙另算一点点）
    f = f * np.where(front, 1, .45)
    f[TVY0 - 6:TVY1 + 6, TVX0 - 8:TVX1 + 14] *= .3
    room_f = field_q(f, 4)
    b = np.array(im).astype(float)
    lit = b[..., :3] * (1 + room_f[..., None] * np.array([.9, 1.1, 1.3])) + room_f[..., None] * np.array([8, 14, 26])
    b[..., :3] = np.clip(lit, 0, 255)
    im = Image.fromarray(b.astype(np.uint8), 'RGBA')
    # ---- 屏幕：游戏画面 4 帧（横版小人跑、地面往左卷）
    sw, sh = TVX1 - TVX0 + 1, TVY1 - TVY0 + 1
    n = 4
    screen = new(sw * n, sh)
    sd = ImageDraw.Draw(screen)
    for k in range(n):
        o = k * sw
        rect(sd, (o, 0, o + sw - 1, sh - 1), '#6aa8f0')
        rect(sd, (o, 0, o + sw - 1, 6), '#4a88e0')
        for cxk in (6, 22):
            cx = o + (cxk - k * 2) % sw
            rect(sd, (cx, 4, cx + 5, 6), '#f4f8ff')
        rect(sd, (o, sh - 7, o + sw - 1, sh - 1), '#c07838')
        rect(sd, (o, sh - 7, o + sw - 1, sh - 6), '#58c048')
        for bx in range(-8, sw + 8, 8):
            x = o + bx - (k * 2) % 8
            if o <= x < o + sw - 2:
                px(sd, x, sh - 4, '#8a5428'); px(sd, x + 1, sh - 3, '#8a5428')
        # 小人
        hx, hy = o + 9, sh - 13 - (2 if k % 2 else 0)
        rect(sd, (hx, hy, hx + 3, hy + 2), '#e03028')
        rect(sd, (hx, hy + 3, hx + 3, hy + 5), '#2848c8')
        px(sd, hx + (k % 2) * 3, hy + 6, '#6a3818')
        # 敌人 + 问号砖
        ex = o + (sw - 2 - k * 3) % sw
        if ex < o + sw - 4:
            rect(sd, (ex, sh - 10, ex + 3, sh - 8), '#8a4a20')
        rect(sd, (o + 20, 9, o + 23, 12), '#f0b030')
        px(sd, o + 21, 10, '#8a5010')
    # 雪花屏 6 帧（手伸出来）
    sn = 6
    snow = new(sw * sn, sh)
    sa = np.array(snow)
    rng = np.random.RandomState(12)
    for k in range(sn):
        v = rng.randint(0, 4, (sh, sw))
        pal = np.array([[34, 40, 54, 255], [110, 120, 140, 255], [190, 200, 220, 255], [240, 244, 255, 255]], np.uint8)
        sa[:, k * sw:(k + 1) * sw] = pal[v]
        r = rng.randint(0, sh)
        sa[r, k * sw:(k + 1) * sw] = (250, 252, 255, 255)
    snow = Image.fromarray(sa, 'RGBA')
    # 电视光：屏幕一圈 + 往前的光锥 + 地上一摊（lighter）
    g = ell_field(W, H, 325, 84, 30, 22, 1.5) * .9
    t = np.clip((yy - 84) / 80, 0, 1)
    half = 18 + 70 * t
    cone = np.where((yy > 84) & (xx < 345), .14 * (1 - .5 * t) * np.clip((half - np.abs(xx - 315)) / 14, 0, 1), 0)
    pool = .32 * ell_field(W, H, 316, 156, 56, 12, 1.2)
    glow = glow_from_field(np.clip(g + cone + pool, 0, 1), (70, 96, 150))
    # 开灯：暖色罩
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 174],
                anchors=dict(tv=[325, 84], tv_front=[322, 148], console=[325, 143], pad=[293, 157], socket=[289, 124],
                             sofa=[231, 140], photo=[229, 46], window=[98, 60], kitchen=[410, 146], switch=[159, 84],
                             walk_x=[10, 470]),
                layers=[{'type': 'pano', 'image': 'bg/higashikata_tvnight/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'glow', 'image': 'bg/higashikata_tvnight/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.18},
                        {'type': 'pano', 'image': 'bg/higashikata_tvnight/lit', 'k': 1, 'x': 0, 'y': 0, 'key': 'lamp'},
                        {'type': 'strip', 'image': 'bg/higashikata_tvnight/screen', 'n': n, 'fps': 5, 'k': 1, 'x': TVX0, 'y': TVY0,
                         'w': sw, 'h': sh},
                        {'type': 'strip', 'image': 'bg/higashikata_tvnight/snow', 'n': sn, 'fps': 15, 'k': 1, 'x': TVX0, 'y': TVY0,
                         'w': sw, 'h': sh, 'key': 'snow'}], fg=[])
    prev = im.copy()
    prev.alpha_composite(screen.crop((0, 0, sw, sh)), (TVX0, TVY0))
    pa = np.array(prev).astype(int)
    pa[..., :3] = np.clip(pa[..., :3] + np.array(glow)[..., :3], 0, 255)
    preview('higashikata_tvnight', {'p': Image.fromarray(pa.astype(np.uint8), 'RGBA')}, ['p'], W)
    return save_layers('higashikata_tvnight', {'room': im, 'lit': lit_room, 'screen': screen, 'snow': snow, 'glow': glow}, meta)


# ============================================================ 远离电线的空地 open_field（640 宽，下午）
#   一大片长草的空地，远处一排电线杆（离得远，是故意挑的地方）。左边一堆水泥管（土管），中间几块裸土，
#   右边一块旧告示牌、油桶、碎石堆。地底下埋着电缆：key 'cable' 打开 = 亿泰削掉地面露出来的沟和电缆（带电光）。
CABLE = (400, 148, 500, 170)


def field_far(w):
    far = sky(w, ('#6aa4e4', '#86b8ec', '#a8ccf0', '#cce2f4'), 112, seed=41)
    d = ImageDraw.Draw(far)
    for layer, (base, amp, col, col2) in enumerate(((96, 9, '#98b4c0', '#b0c8d0'), (104, 6, '#7c9aa6', '#8eacb6'))):
        for x in range(w):
            y = base + amp * np.sin(x / (55 + layer * 30) + layer * 2) + 3 * np.sin(x / 13.0 + layer)
            line(d, (x, int(y), x, 130), col)
            px(d, x, int(y), col2)
    # 远处的屋顶（很小、很淡）
    rng = np.random.RandomState(42)
    for i in range(int(w / 12)):
        x = rng.randint(-10, w)
        bw, bh = rng.randint(8, 18), rng.randint(5, 10)
        y = 116 - bh + rng.randint(-1, 3)
        rect(d, (x, y, x + bw, 124), ['#d4d0c8', '#dcd6cc', '#c8c4bc'][rng.randint(3)])
        rect(d, (x - 1, y - 2, x + bw + 1, y), ['#7a8aa0', '#8a7a78', '#6a7a8a'][rng.randint(3)])
    # 远处一排电线杆 + 电线（小，偏灰蓝）
    xs = list(range(14, w, 54))
    for x in xs:
        rect(d, (x, 78, x + 1, 120), '#6e7a86')
        line(d, (x - 4, 81, x + 5, 81), '#6e7a86')
        line(d, (x - 3, 85, x + 4, 85), '#6e7a86')
    for xa, xb in zip(xs, xs[1:]):
        for k, yb in enumerate((81, 85)):
            prev = None
            for i in range(21):
                t = i / 20
                x = xa + (xb - xa) * t
                y = yb + 3 * 4 * t * (1 - t)
                if prev:
                    line(d, (*prev, x, y), '#7e8a96')
                prev = (x, y)
    rect(d, (0, 120, w, H), '#8aa878')
    return far


def open_field():
    W, G = 640, 130
    far = field_far(320 + (W - 320) // 2)
    near = new(W, H)
    # 后边缘一溜高草 + 灌木
    near = grass_ground(near, 0, W, G, H, seed=43)
    d = ImageDraw.Draw(near)
    rng = np.random.RandomState(44)
    for x in range(0, W, 2):
        h = 6 + int(5 * (0.5 + 0.5 * np.sin(x / 9.0)) + rng.randint(0, 4))
        line(d, (x, G, x + rng.randint(-1, 2), G - h), ['#5a8a40', '#4a7a36', '#7eac56'][rng.randint(3)])
        if rng.rand() < .08:
            px(d, x, G - h - 1, '#e8e0a0' if rng.rand() < .5 else '#f0f0f0')          # 狗尾草 / 白花
    for cx, wd, sd in ((210, 60, 1), (560, 70, 2)):
        near = hedge(near, cx, cx + wd, G - 16, G + 2, seed=45 + sd, cols=('#2e5a34', '#3e7040', '#5a8a48', '#7aa858'))
    near = round_tree(near, 600, G + 2, 86, 30, seed=46)
    d = ImageDraw.Draw(near)
    # 裸土斑块
    for box, sd in (((150, 140, 290, 168), 1), ((330, 152, 430, 176), 2), ((470, 138, 560, 156), 3)):
        near = dirt(near, box, seed=50 + sd)
    d = ImageDraw.Draw(near)
    # 水泥管（土管）三根：两根并排在下、一根叠在上（侧面看是圆口）
    def pipe(cx, cy, r):
        ellipse(d, (cx - r, cy - r, cx + r, cy + r), '#a8a49a')
        ellipse(d, (cx - r, cy - r, cx + r - 2, cy + r - 2), '#c4c0b6')
        ellipse(d, (cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), '#5a5650')
        ellipse(d, (cx - r + 5, cy - r + 6, cx + r - 4, cy + r - 4), '#3e3a36')
        line(d, (cx - r + 3, cy - 3, cx - r + 3, cy + 3), '#e0dcd2')
    pipe(66, G + 10, 17)
    pipe(104, G + 10, 17)
    pipe(85, G - 18, 17)
    near = dither_fill(near, (46, G + 26, 126, G + 29), '#4a7a36', '#5a8a40', .5)
    d = ImageDraw.Draw(near)
    # 旧告示牌（褪色，字看不清）+ 油桶 + 碎石堆
    rect(d, (470, G - 30, 472, G + 6), '#6a5240')
    rect(d, (500, G - 30, 502, G + 6), '#6a5240')
    rect(d, (464, G - 46, 508, G - 22), '#e8e2d2')
    bevel(d, (464, G - 46, 508, G - 22), '#f6f2e8', '#b8b0a0')
    rect(d, (464, G - 46, 508, G - 40), '#c8483c')
    letters(d, 470, G - 45, 'KEEP OUT', '#f4ece0')
    for k in range(3):
        line(d, (468, G - 36 + k * 4, 468 + 30 - k * 6, G - 36 + k * 4), '#8a8478')
    px(d, 503, G - 28, '#a8603a'); px(d, 466, G - 24, '#a8603a')
    rect(d, (526, G - 6, 540, G + 14), '#3e6a8a')
    line(d, (526, G - 6, 540, G - 6), '#6a92b0')
    line(d, (526, G + 1, 540, G + 1), '#2e5068')
    line(d, (526, G + 8, 540, G + 8), '#2e5068')
    rect(d, (534, G - 2, 536, G + 12), '#8a5a3a')
    rng = np.random.RandomState(47)
    for _ in range(60):
        x, y = 548 + rng.randint(0, 34), G + 12 - int(abs(rng.normal(0, 4)))
        r = rng.randint(1, 3)
        ellipse(d, (x - r, y - r, x + r, y), ['#a8a49a', '#8e8a80', '#c4c0b6'][rng.randint(3)])
    # 散落的小石头
    for _ in range(40):
        x, y = rng.randint(0, W), rng.randint(G + 6, H)
        px(d, x, y, '#c8c0aa'); px(d, x + 1, y, '#9a9282')
    # ---- 电缆沟（key 'cable'）：削掉的一条沟，切面有土层，沟底两根粗电缆
    x0, y0, x1, y1 = CABLE
    cw, ch = x1 - x0, y1 - y0
    cab = new(cw + 8, ch + 6)
    cd = ImageDraw.Draw(cab)
    ox, oy = 4, 2
    poly(cd, [(ox, oy + 3), (ox + 6, oy), (ox + cw - 6, oy), (ox + cw, oy + 3), (ox + cw - 3, oy + ch), (ox + 3, oy + ch)], '#5a4632')
    poly(cd, [(ox + 3, oy + 5), (ox + cw - 3, oy + 5), (ox + cw - 6, oy + ch - 2), (ox + 6, oy + ch - 2)], '#3e2e20')
    for k in range(ox, ox + cw, 3):                                   # 被削出来的整齐切口（削，不是挖）
        px(cd, k, oy + 1 + (k // 3) % 2, '#7a6248')
    line(cd, (ox + 6, oy, ox + cw - 6, oy), '#9a8262')
    line(cd, (ox + 4, oy + 8, ox + cw - 4, oy + 8), '#4a382a')
    for yy_, col in ((oy + 12, '#1e1e24'), (oy + 16, '#26262e')):
        rect(cd, (ox + 4, yy_, ox + cw - 4, yy_ + 3), col)
        line(cd, (ox + 4, yy_, ox + cw - 4, yy_), '#4a4a56')
    rect(cd, (ox + 40, oy + 11, ox + 46, oy + 20), '#6a6a72')         # 接线盒
    line(cd, (ox + 40, oy + 11, ox + 46, oy + 11), '#9a9aa2')
    for _ in range(30):
        px(cd, ox + 2 + rng.randint(0, cw - 4), oy - 1 + rng.randint(0, 3), '#7a6248')   # 翻出来的土渣
    spark = ell_field(cw + 40, ch + 40, (cw + 40) / 2, 32, (cw + 30) / 2, 18, 1.3)
    sg = glow_from_field(spark * .9, (60, 140, 230))
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(pipes=[85, 146], meet=[220, 148], bike=[300, 150], cable=[450, 160], cable_box=[447, 162],
                             sign=[486, 146], drum=[533, 146], gravel=[565, 146], tree=[600, 146], poles_far=[0, 84],
                             walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/open_field/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/open_field/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'image', 'image': 'bg/open_field/cable', 'k': 1, 'x': x0 - ox, 'y': y0 - oy, 'key': 'cable'},
                        {'type': 'glow', 'image': 'bg/open_field/spark', 'k': 1, 'x': x0 - 20, 'y': y0 - 20, 'flicker': 0.5,
                         'key': 'cable'}], fg=[])
    layers = {'far': far, 'near': near, 'cable': cab, 'spark': sg}
    pv = near.copy()
    pv.alpha_composite(cab, (x0 - ox, y0 - oy))
    return _save_field(layers, meta, far, pv, W)


def _save_field(layers, meta, far, pv, W):
    prev = far.resize((W, H), Image.NEAREST)
    prev.alpha_composite(pv)
    preview('open_field', {'p': prev}, ['p'], W)
    return save_layers('open_field', layers, meta)


# ============================================================ 杜王港码头 morioh_harbor（960 宽，白天）
#   左半：仓库 + 摞起来的集装箱 + 龙门吊；右半：开阔的码头边，后面是海。地面是水泥地，有接缝、黄色安全线、
#   6 块铁格栅（辣妹钻出来的地方）和 4 根路灯。叉车停在中间偏右：key 'forklift' = 电瓶充电发光，
#   pick 'tyre'（0 好的 / 1 前轮被打出裂口）。key 'ship' = SPW 的船靠在最右边，舷梯放到码头上（和乔瑟夫见面）。
GRATES = [(96, 158), (232, 168), (372, 154), (520, 166), (688, 156), (836, 168)]
LAMPS = [150, 410, 700, 900]
FLX = 600           # 叉车左边 x


def harbor_far(w):
    far = sky(w, ('#5c9ee6', '#7ab2ec', '#9cc6f0', '#c4ddf4'), 96, seed=61)
    far = sea(far, 96, 132, seed=62)
    d = ImageDraw.Draw(far)
    # 对岸的岬角 + 灯塔（杜王町的海岸线）
    for x in range(0, 200):
        y = 96 - 14 * np.sin(np.pi * x / 200) ** .8 - 2 * np.sin(x / 7)
        line(d, (x + 380, int(y), x + 380, 96), '#7a96a0')
        px(d, x + 380, int(y), '#94acb4')
    far = far_lighthouse(far, 552, 96)
    d = ImageDraw.Draw(far)
    # 远处的船
    for sx, sw_, col in ((140, 30, '#e8e4dc'), (300, 18, '#c8483c')):
        poly(d, [(sx, 92), (sx + sw_, 92), (sx + sw_ - 4, 96), (sx + 3, 96)], col)
        rect(d, (sx + sw_ // 3, 87, sx + sw_ // 3 + 8, 92), '#f0ece4')
    rect(d, (0, 132, w, H), '#4e6270')
    return far


def corrugated(img, box, cols):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    rect(d, box, cols[0])
    for x in range(x0, x1, 3):
        line(d, (x, y0, x, y1), cols[1])
        line(d, (x + 1, y0, x + 1, y1), cols[2])
    return img


def container(img, x, y, w, h, col, label=None, seed=0):
    """侧面看的集装箱：瓦楞竖纹、上下边梁、右端的门锁杆"""
    base = c3(col)
    dk, lt = mix(col, '#000000', .28), mix(col, '#ffffff', .18)
    img = corrugated(img, (x, y, x + w, y + h), (base, dk, lt))
    d = ImageDraw.Draw(img)
    rect(d, (x, y, x + w, y + 1), mix(col, '#ffffff', .3))
    rect(d, (x, y + h - 2, x + w, y + h), mix(col, '#000000', .45))
    rect(d, (x, y, x + 1, y + h), mix(col, '#000000', .4))
    rect(d, (x + w - 1, y, x + w, y + h), mix(col, '#000000', .4))
    if label:
        tw = text_w(label)
        rect(d, (x + 6, y + 5, x + 10 + tw, y + 13), mix(col, '#ffffff', .75))
        letters(d, x + 8, y + 7, label, mix(col, '#000000', .5))
    rng = np.random.RandomState(seed)
    for _ in range(int(w / 6)):
        xx = rng.randint(x + 2, x + w - 2)
        for k in range(rng.randint(2, 6)):
            px(d, xx, y + h - 3 - k, '#8a5a3a')                         # 锈迹
    return img


def grate_img():
    g = new(20, 8)
    d = ImageDraw.Draw(g)
    rect(d, (0, 0, 19, 7), '#3a3a40')
    rect(d, (1, 1, 18, 6), '#1a1a20')
    for x in range(2, 18, 3):
        line(d, (x, 1, x, 6), '#5a5a62')
    line(d, (0, 0, 19, 0), '#7a7a80')
    return g


def forklift(img, x, ground, tyre_cut=False, only_tyre=False):
    """叉车（侧面，叉子朝左）：橙黄车身、护顶架、门架 + 货叉、黑色实心胎"""
    d = ImageDraw.Draw(img)
    if not only_tyre:
        Y = ground
        # 门架 + 货叉
        rect(d, (x + 2, Y - 46, x + 5, Y - 4), '#4a4a52')
        rect(d, (x + 7, Y - 46, x + 9, Y - 4), '#5a5a62')
        line(d, (x + 2, Y - 46, x + 9, Y - 46), '#7a7a82')
        rect(d, (x - 14, Y - 6, x + 4, Y - 4), '#6a6a72')
        line(d, (x - 14, Y - 6, x + 4, Y - 6), '#9a9aa2')
        rect(d, (x + 1, Y - 18, x + 3, Y - 4), '#6a6a72')
        # 车身
        poly(d, [(x + 10, Y - 26), (x + 44, Y - 26), (x + 50, Y - 18), (x + 50, Y - 6), (x + 10, Y - 6)], '#e8a020')
        line(d, (x + 10, Y - 26, x + 44, Y - 26), '#f8c860')
        rect(d, (x + 10, Y - 9, x + 50, Y - 6), '#b87810')
        rect(d, (x + 36, Y - 24, x + 49, Y - 10), '#3a3a42')               # 配重
        line(d, (x + 36, Y - 24, x + 49, Y - 24), '#5a5a62')
        rect(d, (x + 14, Y - 22, x + 30, Y - 12), '#c88418')               # 电瓶盖
        line(d, (x + 14, Y - 22, x + 30, Y - 22), '#f0b848')
        letters(d, x + 16, Y - 20, 'BATT', '#5a3a08')
        # 座椅 + 方向盘 + 护顶架
        rect(d, (x + 30, Y - 34, x + 36, Y - 26), '#2a2a30')
        line(d, (x + 30, Y - 34, x + 30, Y - 26), '#4a4a52')
        line(d, (x + 20, Y - 26, x + 23, Y - 34), '#2a2a30')
        line(d, (x + 20, Y - 35, x + 26, Y - 33), '#2a2a30')
        for px_ in (x + 13, x + 41):
            rect(d, (px_, Y - 56, px_ + 1, Y - 26), '#3a3a42')
        rect(d, (x + 11, Y - 58, x + 44, Y - 56), '#3a3a42')
        for k in range(x + 14, x + 42, 4):
            px(d, k, Y - 57, '#6a6a72')
        rect(d, (x + 46, Y - 30, x + 48, Y - 26), '#e04030')               # 尾灯
    # 轮胎：前轮大（x+18）、后轮小（x+42）
    for cx, r, front in ((x + 18, 7, True), (x + 42, 5, False)):
        if only_tyre and not front:
            continue
        cy = ground - r
        ellipse(d, (cx - r, cy - r, cx + r, cy + r), '#1e1e22')
        ellipse(d, (cx - r + 1, cy - r + 1, cx + r - 2, cy + r - 2), '#2e2e34')
        ellipse(d, (cx - 3, cy - 3, cx + 3, cy + 3), '#8a8a92')
        px(d, cx, cy, '#2e2e34')
        if front and tyre_cut:
            # 被打出一道裂口：胎面往外翻、露出里面的空腔
            poly(d, [(cx - 6, cy - 4), (cx - 1, cy - 8), (cx + 5, cy - 6), (cx + 2, cy - 1), (cx - 4, cy)], '#0a0a0c')
            line(d, (cx - 6, cy - 4, cx - 9, cy - 7), '#3e3e46')
            line(d, (cx + 5, cy - 6, cx + 8, cy - 9), '#3e3e46')
            px(d, cx - 1, cy - 9, '#4a4a52')
    return img


def morioh_harbor():
    W, G = 960, 128
    far = harbor_far(320 + (W - 320) // 2)
    near = new(W, H)
    d = ImageDraw.Draw(near)
    # ---- 仓库（0–250）：灰蓝瓦楞墙、大卷帘门、编号
    near = corrugated(near, (0, 34, 250, G), ('#8a9aa8', '#76869a', '#a0b0be'))
    d = ImageDraw.Draw(near)
    poly(d, [(-4, 34), (125, 18), (254, 34)], '#5a6a7a')
    line(d, (-4, 34, 125, 18), '#7a8a9a'); line(d, (125, 18, 254, 34), '#4a5a6a')
    rect(d, (0, 34, 250, 37), '#4e5e6e')
    for dx0 in (24, 134):
        rect(d, (dx0, 62, dx0 + 92, G), '#6a7684')
        for y in range(64, G, 3):
            line(d, (dx0 + 1, y, dx0 + 91, y), '#7c8896')
        rect(d, (dx0 - 3, 58, dx0 + 95, 62), '#3e4a58')
        rect(d, (dx0 + 2, G - 30, dx0 + 90, G - 1), '#2a323c')          # 半开的卷帘门：里面暗
        for y in range(G - 30, G, 4):
            line(d, (dx0 + 2, y, dx0 + 90, y), '#323a46')
        rect(d, (dx0, G - 32, dx0 + 92, G - 30), '#5a6674')
    rect(d, (106, 40, 144, 52), '#e8e4dc')
    letters(d, 110, 44, 'MORIOH', '#2a4a7a')
    rect(d, (52, 40, 70, 54), '#d8b040')
    letters(d, 55, 44, '03', '#2a2a30')
    rect(d, (180, 40, 198, 54), '#d8b040')
    letters(d, 183, 44, '04', '#2a2a30')
    # ---- 集装箱堆（250–470）+ 龙门吊
    stacks = [((252, G - 26, 64, 26), '#c8483c', 'SPW', 1), ((318, G - 26, 64, 26), '#3a72a8', None, 2),
              ((384, G - 26, 64, 26), '#4a8a5a', 'MRH', 3), ((262, G - 52, 64, 26), '#e0a030', None, 4),
              ((328, G - 52, 64, 26), '#c8483c', None, 5), ((300, G - 78, 64, 26), '#3a72a8', 'TOHO', 6)]
    for (x, y, w, h), col, lab, sd in stacks:
        near = container(near, x, y, w, h, col, lab, sd)
    d = ImageDraw.Draw(near)
    # 龙门吊（橙白，横梁伸向海）
    for lx in (470, 520, 700, 744):
        rect(d, (lx, 22, lx + 4, G), '#e07a30')
        line(d, (lx, 22, lx, G), '#f0a060')
        for y in range(30, G - 6, 12):
            line(d, (lx, y, lx + 4, y + 10), '#b85a20')
    rect(d, (440, 16, 760, 22), '#e07a30')
    line(d, (440, 16, 760, 16), '#f0a060')
    for x in range(444, 756, 8):
        line(d, (x, 17, x + 4, 21), '#b85a20')
    rect(d, (500, 6, 530, 16), '#f0ece4')
    rect(d, (504, 9, 512, 13), '#5a8ab8')
    rect(d, (626, 22, 638, 28), '#4a4a52')
    line(d, (630, 28, 630, 58), '#2a2a30'); line(d, (634, 28, 634, 58), '#2a2a30')
    rect(d, (624, 58, 640, 62), '#d8b040')
    # ---- 码头边（470 以右）：岸壁 + 系船柱 + 轮胎护舷
    rect(d, (474, G - 4, W, G), '#8a8a86')
    line(d, (474, G - 4, W, G - 4), '#b4b4ae')
    for bx in (560, 680, 800, 930):
        rect(d, (bx - 4, G - 10, bx + 4, G - 4), '#3a3a42')
        ellipse(d, (bx - 6, G - 14, bx + 6, G - 8), '#4a4a52')
        line(d, (bx - 5, G - 13, bx + 3, G - 13), '#6a6a72')
    for bx in (520, 620, 740, 860):
        ellipse(d, (bx - 6, G - 2, bx + 6, G + 8), '#1e1e22')
        ellipse(d, (bx - 3, G + 1, bx + 3, G + 5), '#4e6270')
    # ---- 地面：水泥大板，越近越宽的接缝 + 黄色安全线 + 油渍
    rect(d, (0, G, W, H), '#a8a49c')
    near = grad(near, (0, G, W, G + 14), ('#9a968e', '#a8a49c', '#b0aca4'))
    d = ImageDraw.Draw(near)
    for y in (G + 14, G + 30, G + 50):
        line(d, (0, y, W, y), '#8e8a82')
    for x in range(0, W, 64):
        line(d, (x, G, x - 6, H), '#8e8a82')
    for x in range(0, W, 48):
        rect(d, (x, G + 6, x + 26, G + 7), '#e0b830')
    noise_specks(near, (0, G, W, H), ['#9a968e', '#b8b4ac', '#8a867e'], 2400, 63)
    rng = np.random.RandomState(64)
    for _ in range(8):
        cx, cy = rng.randint(20, W - 20), rng.randint(G + 16, H - 4)
        ellipse(d, (cx - 9, cy - 2, cx + 9, cy + 2), '#8e8a84')
        ellipse(d, (cx - 5, cy - 1, cx + 4, cy + 1), '#7e7a76')
    # 格栅（6 块）
    gi = grate_img()
    for gx, gy in GRATES:
        near.alpha_composite(gi, (gx - 10, gy - 4))
    d = ImageDraw.Draw(near)
    # 路灯（码头的高杆灯）
    for lx in LAMPS:
        rect(d, (lx, 50, lx + 2, G + 4), '#5a6270')
        line(d, (lx, 50, lx, G + 4), '#7a8290')
        line(d, (lx + 1, 50, lx + 12, 46), '#5a6270')
        rect(d, (lx + 8, 44, lx + 18, 47), '#3e4652')
        rect(d, (lx + 9, 47, lx + 17, 48), '#e8ecf0')
        rect(d, (lx - 2, G, lx + 4, G + 4), '#4a5260')
        rect(d, (lx - 1, 100, lx + 3, 108), '#4a5260')                      # 灯杆上的电箱
        px(d, lx + 1, 103, '#e0b830')
    # 鱼箱、缆绳卷、渔民的桶（码头杂物）
    for k, (x, col) in enumerate(((760, '#3a72c8'), (772, '#3a72c8'), (766, '#d84a3a'))):
        y = G - 10 if k < 2 else G - 20
        rect(d, (x, y, x + 11, y + 9), col)
        line(d, (x, y, x + 11, y), mix(col, '#ffffff', .4))
    ellipse(d, (880, G - 6, 902, G + 2), '#c8a060')
    ellipse(d, (884, G - 4, 898, G), '#a8803e')
    ellipse(d, (889, G - 3, 893, G - 1), '#6a5030')
    # ---- 叉车
    near = forklift(near, FLX, G + 22)
    # 叉车层：tyre pick（两张前轮小图）、电瓶发光
    tyre0 = forklift(new(20, 18), -8, 16, False, True)
    tyre1 = forklift(new(20, 18), -8, 16, True, True)
    tyre_x, tyre_y = FLX + 18 - 10, G + 22 - 16
    fl = ell_field(80, 60, 40, 30, 36, 24, 1.2)
    fglow = glow_from_field(fl, (230, 200, 90))
    # ---- 海面闪光（远层的 wrap，跟远层同视差）
    waves = wave_tile(320, 34, seed=65)
    # ---- SPW 的船（key 'ship'）：白船身、蓝条、船名，舷梯斜放到码头上
    ship = new(200, 110)
    sd = ImageDraw.Draw(ship)
    poly(sd, [(0, 60), (196, 60), (186, 96), (14, 96)], '#f0ece4')
    rect(sd, (6, 80, 192, 86), '#2a5a9a')
    line(sd, (0, 60, 196, 60), '#ffffff')
    poly(sd, [(14, 96), (186, 96), (184, 100), (16, 100)], '#c8483c')
    for x in range(30, 180, 14):
        ellipse(sd, (x, 66, x + 5, 71), '#5a7a9a')
        px(sd, x + 1, 67, '#c8e0f0')
    letters(sd, 140, 73, 'SPW', '#2a5a9a')
    rect(sd, (40, 30, 150, 60), '#f6f2ea')
    line(sd, (40, 30, 150, 30), '#ffffff')
    for x in range(46, 146, 12):
        rect(sd, (x, 36, x + 8, 44), '#4a6a8a')
        line(sd, (x, 36, x + 8, 36), '#8ab0d0')
    rect(sd, (70, 14, 120, 30), '#f6f2ea')
    rect(sd, (74, 18, 116, 24), '#3a5a7a')
    rect(sd, (94, 0, 96, 14), '#6a6a72')
    line(sd, (86, 4, 104, 4), '#6a6a72')
    rect(sd, (124, 18, 134, 30), '#2a5a9a')
    rect(sd, (124, 16, 134, 18), '#1e1e22')
    for x in range(42, 150, 6):
        line(sd, (x, 54, x, 60), '#c8c4bc')
    line(sd, (40, 54, 150, 54), '#c8c4bc')
    poly(sd, [(30, 60), (34, 60), (6, 104), (0, 104)], '#a8a49c')          # 舷梯
    for k in range(8):
        line(sd, (30 - k * 3.4, 62 + k * 5.5, 34 - k * 3.4, 62 + k * 5.5), '#6a6a72')
    line(sd, (30, 54, 0, 98), '#6a6a72')
    SX, SY = 760, G - 100
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(warehouse=[70, 146], shutter=[180, 146], containers=[340, 146], crane=[495, 146],
                             forklift=[FLX + 28, 150], forklift_batt=[FLX + 22, G + 5], tyre=[FLX + 18, G + 15],
                             grates=[list(p) for p in GRATES], lamps=[[x + 13, 48] for x in LAMPS],
                             lamp_feet=[[x + 1, 148] for x in LAMPS], quay_edge=[700, 128], fish_boxes=[770, 146],
                             ship_gangway=[SX + 4, 150], ship=[SX + 100, 70], sea=[700, 110], walk_x=[8, 952]),
                layers=[{'type': 'pano', 'image': 'bg/morioh_harbor/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'wrap', 'image': 'bg/morioh_harbor/waves', 'k': 0.5, 'vx': 4, 'y': 98},
                        {'type': 'image', 'image': 'bg/morioh_harbor/ship', 'k': 1, 'x': SX, 'y': SY, 'key': 'ship'},
                        {'type': 'pano', 'image': 'bg/morioh_harbor/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pick', 'key': 'tyre', 'images': ['bg/morioh_harbor/tyre0', 'bg/morioh_harbor/tyre1'],
                         'k': 1, 'x': tyre_x, 'y': tyre_y},
                        {'type': 'glow', 'image': 'bg/morioh_harbor/fglow', 'k': 1, 'x': FLX - 12, 'y': G - 16, 'flicker': 0.4,
                         'key': 'forklift'}], fg=[])
    layers = {'far': far, 'near': near, 'waves': waves, 'ship': ship, 'tyre0': tyre0, 'tyre1': tyre1, 'fglow': fglow}
    prev = far.resize((W, H), Image.NEAREST)
    prev.alpha_composite(near)
    preview('morioh_harbor', {'p': prev}, ['p'], W)
    p2 = far.resize((W, H), Image.NEAREST)
    p2.alpha_composite(ship, (SX, SY))
    p2.alpha_composite(near)
    p2.alpha_composite(tyre1, (tyre_x, tyre_y))
    preview('morioh_harbor_ship', {'p': p2}, ['p'], W)
    return save_layers('morioh_harbor', layers, meta)


# ============================================================ SPW 的船 spw_ship（640 宽，海上，下午）
#   船尾甲板（左）→ 发电机（key 'gen' = 充电时发光、电表闪）→ 缆绳卷、木箱、救生圈 → 船舱（驾驶室在上，门在下）→ 船头。
#   甲板后面一道栏杆，栏杆外是海和远处的杜王町海岸线。
def ship_far(w):
    far = sky(w, ('#5c9ee6', '#7ab2ec', '#a0c8f0', '#cce2f4'), 92, seed=71)
    far = sea(far, 92, H, cols=('#4a88c0', '#3a76ae', '#2c6496', '#225480'), seed=72)
    d = ImageDraw.Draw(far)
    # 远处的杜王町：一条低低的海岸线 + 小房子 + 山
    for x in range(w):
        y = 84 + 4 * np.sin(x / 40) + 2 * np.sin(x / 11)
        line(d, (x, int(y), x, 92), '#8aa4ae')
    rng = np.random.RandomState(73)
    for _ in range(int(w / 10)):
        x = rng.randint(0, w)
        rect(d, (x, 88, x + rng.randint(3, 7), 91), ['#d8d4cc', '#c4c0b8', '#e4e0d8'][rng.randint(3)])
    far = far_lighthouse(far, 260, 92)
    return far


def spw_ship():
    W, G = 640, 134
    far = ship_far(320 + int((W - 320) * .4))
    near = new(W, H)
    d = ImageDraw.Draw(near)
    # ---- 甲板后沿：白色船舷墙 + 栏杆
    rect(d, (0, G - 14, W, G), '#e8e4dc')
    line(d, (0, G - 14, W, G - 14), '#ffffff')
    line(d, (0, G - 1, W, G - 1), '#b8b4ac')
    for x in range(0, W, 40):
        line(d, (x, G - 13, x, G - 2), '#d0ccc4')
    rect(d, (0, G - 34, W, G - 33), '#d8d8d4')
    line(d, (0, G - 24, W, G - 24), '#c8c8c4')
    for x in range(4, W, 16):
        rect(d, (x, G - 34, x + 1, G - 14), '#c8c8c4')
    # 船名牌（栏杆上）
    rect(d, (60, G - 12, 106, G - 4), '#2a5a9a')
    letters(d, 64, G - 10, 'SPW-02', '#f0ece4')
    # ---- 甲板：绿色防滑漆钢板，越近越宽的接缝
    rect(d, (0, G, W, H), '#5e8a6e')
    near = grad(near, (0, G, W, G + 10), ('#4e7a5e', '#5e8a6e', '#6a967a'))
    d = ImageDraw.Draw(near)
    y, h = G + 10, 6.0
    while y < H:
        line(d, (0, int(y), W, int(y)), '#4e7a5e')
        y += h
        h *= 1.35
    for x in range(0, W, 80):
        line(d, (x, G, x - 8, H), '#527e62')
    noise_specks(near, (0, G, W, H), ['#6a967a', '#527e62', '#74a084'], 1600, 74)
    rect(d, (0, G + 40, W, G + 41), '#e0c040')                              # 甲板边黄线（靠镜头）
    for x in range(0, W, 12):
        rect(d, (x, G + 40, x + 5, G + 41), '#2a2a30')
    # ---- 船尾（0–90）：系缆桩、缆绳卷、旗杆
    for bx in (20, 70):
        rect(d, (bx - 3, G - 6, bx + 3, G + 4), '#3a3a42')
        ellipse(d, (bx - 5, G - 9, bx + 5, G - 4), '#4a4a52')
    ellipse(d, (34, G - 4, 58, G + 6), '#c8a060')
    ellipse(d, (38, G - 2, 54, G + 4), '#a8803e')
    ellipse(d, (43, G - 1, 49, G + 2), '#6a5030')
    rect(d, (8, 40, 9, G - 14), '#8a8a92')
    flag = new(18, 12)
    fd = ImageDraw.Draw(flag)
    rect(fd, (0, 0, 17, 11), '#2a5a9a')
    letters(fd, 2, 3, 'SPW', '#f0ece4')
    near.alpha_composite(flag, (10, 40))
    d = ImageDraw.Draw(near)
    # ---- 发电机（150–230）：灰绿机箱、散热鳍片、电表、警告牌、电缆
    gx0, gx1, gy0 = 150, 230, G - 40
    rect(d, (gx0, gy0, gx1, G + 2), '#6a7a72')
    rect(d, (gx0, gy0, gx1, gy0 + 3), '#8a9a92')
    line(d, (gx1, gy0, gx1, G + 2), '#4a5a52')
    for x in range(gx0 + 6, gx0 + 44, 3):
        line(d, (x, gy0 + 8, x, G - 6), '#4e5e56')
    rect(d, (gx0 + 50, gy0 + 8, gx0 + 74, gy0 + 24), '#2a2a30')              # 电表
    rect(d, (gx0 + 52, gy0 + 10, gx0 + 72, gy0 + 18), '#d8e0c8')
    line(d, (gx0 + 54, gy0 + 17, gx0 + 66, gy0 + 12), '#c83a34')
    px(d, gx0 + 54, gy0 + 21, '#6ae070'); px(d, gx0 + 60, gy0 + 21, '#e0c040'); px(d, gx0 + 66, gy0 + 21, '#e04040')
    poly(d, [(gx0 + 62, gy0 + 28), (gx0 + 56, gy0 + 38), (gx0 + 68, gy0 + 38)], '#f0c020')     # 高压警告
    line(d, (gx0 + 62, gy0 + 31, gx0 + 62, gy0 + 35), '#2a2a30')
    rect(d, (gx0 + 4, gy0 - 8, gx0 + 10, gy0), '#4a4a52')                    # 排气管
    rect(d, (gx0 + 3, gy0 - 10, gx0 + 11, gy0 - 8), '#3a3a42')
    cable_pts = [(gx1, G - 4), (gx1 + 14, G + 6), (gx1 + 50, G + 8), (gx1 + 110, G + 2), (380, G - 10)]
    for a_, b_ in zip(cable_pts, cable_pts[1:]):
        line(d, (*a_, *b_), '#1e1e24', 2)
    # ---- 木箱 + 救生圈（240–360）
    for x, y, w, h in ((270, G - 22, 24, 22), (296, G - 18, 20, 18), (280, G - 38, 20, 16)):
        rect(d, (x, y, x + w, y + h), '#b08a5a')
        bevel(d, (x, y, x + w, y + h), '#ccaa78', '#8a6a42')
        line(d, (x + 1, y + 1, x + w - 1, y + h - 1), '#9a7648')
        line(d, (x + w - 1, y + 1, x + 1, y + h - 1), '#9a7648')
    for cx in (340, ):
        ellipse(d, (cx - 9, G - 32, cx + 9, G - 14), '#e86a30')
        ellipse(d, (cx - 5, G - 28, cx + 5, G - 18), '#e8e4dc')
        for a_ in (0, 1, 2, 3):
            ang = a_ * np.pi / 2 + np.pi / 4
            ellipse(d, (cx + 7 * np.cos(ang) - 2, G - 23 + 7 * np.sin(ang) - 2, cx + 7 * np.cos(ang) + 2, G - 23 + 7 * np.sin(ang) + 2),
                    '#f4f0e8')
    # ---- 船舱（380–560）：下层客舱（门 + 舷窗），上层驾驶室（一排斜窗），桅杆 + 雷达
    cx0, cx1 = 380, 560
    rect(d, (cx0, 60, cx1, G), '#f2eee6')
    line(d, (cx0, 60, cx1, 60), '#ffffff')
    line(d, (cx1, 60, cx1, G), '#c8c4bc')
    rect(d, (cx0, G - 22, cx1, G - 18), '#2a5a9a')
    for x in range(cx0 + 16, cx1 - 10, 24):
        if 448 <= x <= 488:
            continue
        ellipse(d, (x, 78, x + 10, 88), '#a8a49c')
        ellipse(d, (x + 1, 79, x + 9, 87), '#4a6a8a')
        px(d, x + 3, 81, '#c8e0f0')
    rect(d, (452, 70, 480, G - 1), '#c8c4bc')                                 # 舱门
    rect(d, (454, 72, 478, G - 1), '#a8a49c')
    rect(d, (456, 74, 476, 120), '#b8b4ac')
    ellipse(d, (460, 78, 472, 90), '#4a6a8a')
    rect(d, (474, 100, 476, 104), '#6a6a72')
    rect(d, (448, 68, 484, 70), '#2a5a9a')
    letters(d, cx0 + 10, 64, 'SPW FOUNDATION', '#2a5a9a')
    # 上层驾驶室
    rect(d, (410, 24, 540, 60), '#f6f2ea')
    line(d, (410, 24, 540, 24), '#ffffff')
    poly(d, [(410, 24), (400, 24), (406, 60), (410, 60)], '#e4e0d8')
    rect(d, (404, 20, 546, 24), '#2a5a9a')
    for x in range(418, 534, 14):
        poly(d, [(x, 32), (x + 11, 32), (x + 10, 46), (x - 1, 46)], '#3a5a7a')
        line(d, (x, 32, x + 11, 32), '#8ab0d0')
        px(d, x + 2, 35, '#c8e0f0')
    for x in range(408, 548, 6):                                              # 驾驶室外的小栏杆
        line(d, (x, 54, x, 60), '#c8c4bc')
    line(d, (404, 54, 548, 54), '#c8c4bc')
    rect(d, (474, 0, 476, 20), '#8a8a92')                                     # 桅杆 + 雷达 + 灯
    rect(d, (464, 6, 486, 8), '#6a6a72')
    rect(d, (474, 0, 477, 2), '#e04030')
    line(d, (476, 8, 440, 24), '#8a8a92')
    line(d, (476, 8, 520, 24), '#8a8a92')
    # 舱壁上的救生圈 + 灭火器
    ellipse(d, (cx0 + 6, 96, cx0 + 22, 112), '#e86a30')
    ellipse(d, (cx0 + 10, 100, cx0 + 18, 108), '#f2eee6')
    rect(d, (cx1 - 16, 96, cx1 - 10, 112), '#d84030')
    rect(d, (cx1 - 15, 94, cx1 - 11, 96), '#2a2a30')
    # ---- 船头（560–640）：锚机 + 收窄的船舷
    rect(d, (582, G - 12, 610, G + 4), '#4a4a52')
    ellipse(d, (586, G - 16, 606, G - 4), '#5a5a62')
    ellipse(d, (591, G - 12, 601, G - 8), '#3a3a42')
    for k in range(5):
        ellipse(d, (612 + k * 5, G - 2 + k, 616 + k * 5, G + 2 + k), '#6a6a72')
    near = noise_specks(near, (0, G + 42, W, H), ['#527e62'], 200, 75)
    # ---- 发电机发光（key 'gen'）
    gf = ell_field(120, 90, 60, 45, 56, 40, 1.4)
    gglow = glow_from_field(gf, (90, 150, 230))
    waves = wave_tile(320, 40, seed=76, density=40)
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(stern=[46, 146], flag=[19, 46], generator=[190, 146], gen_meter=[212, 102], gen_top=[190, 94],
                             cable=[300, 142], crates=[288, 146], buoy=[340, 146], cabin=[470, 146], cabin_door=[466, 146],
                             bridge=[476, 40], bow=[600, 146], winch=[596, 140], joseph=[520, 148], crew=[[250, 146], [360, 146], [420, 146]],
                             captain=[530, 146], walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/spw_ship/far', 'k': 0.4, 'x': 0, 'y': 0},
                        {'type': 'wrap', 'image': 'bg/spw_ship/waves', 'k': 0.4, 'vx': 10, 'y': 96},
                        {'type': 'pano', 'image': 'bg/spw_ship/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'glow', 'image': 'bg/spw_ship/gglow', 'k': 1, 'x': 130, 'y': G - 64, 'flicker': 0.45,
                         'key': 'gen'}], fg=[])
    prev = far.resize((W, H), Image.NEAREST)
    prev.alpha_composite(near)
    preview('spw_ship', {'p': prev}, ['p'], W)
    return save_layers('spw_ship', {'far': far, 'near': near, 'waves': waves, 'gglow': gglow}, meta)


# ============================================================ 公园池塘 park_pond（480 宽，初夏下午）
#   左：公园入口 + 长椅 + 路灯；中右：池塘（石砌池边、睡莲、芦苇），池塘在小路后面；小路上落叶和两个水洼。
#   strip 'pond'：水面波光一直在动；key 'ring'：扑通一圈涟漪（6 帧，循环）；key 'red'：水里散开的一圈淡红（克制）。
PCX, PCY, PRX, PRY = 322, 124, 124, 14          # 池塘水面（椭圆）
PX0, PX1, PY0, PY1 = PCX - PRX, PCX + PRX, PCY - PRY, PCY + PRY


def park_pond():
    W, G = 480, 140
    far = sky(320 + (W - 320) // 2, ('#6aa6e6', '#88baee', '#aacef2', '#d0e4f4'), 110, seed=81)
    fd = ImageDraw.Draw(far)
    rng = np.random.RandomState(82)
    for i in range(int(far.width / 9)):                                        # 远处树林
        x = rng.randint(-10, far.width)
        r = rng.randint(10, 18)
        ellipse(fd, (x - r, 92 - r, x + r, 112 + r), ['#5a8a6a', '#6a9a76', '#4e7e60'][rng.randint(3)])
    for x0 in (40, 180):
        rect(fd, (x0, 66, x0 + 30, 100), '#dcd8d0')
        for y in range(70, 98, 6):
            for x in range(x0 + 3, x0 + 28, 6):
                rect(fd, (x, y, x + 3, y + 3), '#8ea8bc')
    rect(fd, (0, 104, far.width, H), '#6e9e68')
    near = new(W, H)
    d = ImageDraw.Draw(near)
    # 后面的草坪 + 树 + 灌木
    near = grass_ground(near, 0, W, 104, G, seed=83, cols=('#6a9e52', '#5a8e46', '#7eb05e', '#94c46e', '#4e7e3c'))
    for x, h, r, sd in ((30, 96, 34, 1), (150, 86, 30, 2), (300, 100, 36, 3), (440, 92, 32, 4)):
        near = round_tree(near, x, 110, h, r, seed=84 + sd)
    near = hedge(near, 0, 120, 98, 112, seed=89)
    near = hedge(near, 450, W, 98, 112, seed=90)
    d = ImageDraw.Draw(near)
    # 池塘：椭圆水面（透视压扁），石块沿着前半圈摆一圈，后沿是一条湿土边；倒影里的树影、睡莲、芦苇
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    pr = np.sqrt(((xx - PCX) / PRX) ** 2 + ((yy - PCY) / PRY) ** 2)
    pr = pr * (1 + .03 * np.sin(xx / 9) + .02 * np.sin(xx / 4.3))          # 边不要太圆
    a_ = np.array(near)
    a_[(pr < 1.12)] = (*c3('#6a6a52'), 255)                                  # 湿土边
    water = pr < 1
    depth = np.clip(1 - pr, 0, 1)
    cols = [c3(c) for c in ('#5e8e98', '#4e7e8a', '#42707e', '#386472')]
    bay = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
    lvl = np.clip(np.floor(depth * 3.2 + bay * .9), 0, 3).astype(int)
    for i, c in enumerate(cols):
        a_[water & (lvl == i)] = (*c, 255)
    near = Image.fromarray(a_, 'RGBA')
    d = ImageDraw.Draw(near)
    for x0_, x1_ in ((236, 300), (340, 404)):                              # 树影
        for x in range(x0_, x1_):
            hgt = int(5 + 4 * np.sin((x - x0_) / (x1_ - x0_) * np.pi))
            for y in range(PCY - PRY + 3, PCY - PRY + 3 + hgt):
                if water[y, x] and (x + y) % 2 == 0:
                    px(d, x, y, '#365e5a')
    for k, (x, y) in enumerate(((240, 128), (266, 133), (382, 122), (408, 130), (304, 134))):
        ellipse(d, (x - 5, y - 2, x + 5, y + 2), '#4e8a4a')
        line(d, (x - 4, y - 1, x - 1, y - 1), '#6aa65a')
        px(d, x + 1, y, '#386472')
        if k in (0, 2):
            px(d, x - 1, y - 2, '#f4b8cc'); px(d, x, y - 3, '#f8d0dc')
    for i in range(46):                                                       # 前半圈的石块
        t = np.pi * (i / 45)
        x = PCX + PRX * 1.04 * np.cos(t)
        y = PCY + PRY * 1.08 * np.sin(t)
        if y < PCY - 2:
            continue
        w_ = 5 + (i * 7) % 4
        ellipse(d, (x - w_, y - 2, x + w_, y + 3), '#a8a498' if i % 3 else '#9a968a')
        line(d, (x - w_ + 2, y - 1, x + w_ - 3, y - 1), '#c8c4b8')
    for x in (PCX - PRX - 2, PCX + PRX - 10):                                 # 芦苇
        for k in range(7):
            xx_ = x + k * 2
            top = PCY - 22 + (k * 5) % 9
            line(d, (xx_, PCY + 4, xx_ + (k % 3) - 1, top), '#5a8a40' if k % 2 else '#7aa850')
            if k % 2 == 0:
                rect(d, (xx_ + (k % 3) - 2, top, xx_ + (k % 3) - 1, top + 5), '#8a6a3e')
    # 池边的告示牌（禁止游泳）
    rect(d, (176, 112, 178, 140), '#6a5240')
    rect(d, (166, 104, 188, 116), '#f0ece0')
    bevel(d, (166, 104, 188, 116), '#ffffff', '#b8b0a0')
    ellipse(d, (172, 106, 182, 114), '#d84a3a')
    ellipse(d, (174, 108, 180, 112), '#f0ece0')
    line(d, (174, 112, 180, 108), '#d84a3a')
    # 长椅 + 路灯 + 垃圾桶（左边）
    bx = 60
    rect(d, (bx, 118, bx + 44, 121), '#9a6a40')
    rect(d, (bx, 112, bx + 44, 114), '#9a6a40')
    line(d, (bx, 112, bx + 44, 112), '#c08a58')
    line(d, (bx, 118, bx + 44, 118), '#c08a58')
    for lx in (bx + 3, bx + 39):
        rect(d, (lx, 112, lx + 2, G), '#3a3a42')
    near = street_lamp(near, 120, G, 74)
    d = ImageDraw.Draw(near)
    rect(d, (130, 124, 140, G), '#4a7a5a')
    line(d, (130, 124, 140, 124), '#6a9a7a')
    for y in range(127, G, 3):
        line(d, (131, y, 139, y), '#3e6a4e')
    # 小路（碎石铺装 + 两边的路缘），落叶、两个水洼
    rect(d, (0, G, W, H), '#c8b896')
    near = grad(near, (0, G, W, G + 6), ('#b4a482', '#c8b896'))
    d = ImageDraw.Draw(near)
    rect(d, (0, G - 2, W, G), '#a8a498')
    line(d, (0, G - 2, W, G - 2), '#c8c4b8')
    noise_specks(near, (0, G + 2, W, H), ['#b4a482', '#d8caa8', '#a89878', '#e0d4b4'], 2200, 91)
    rng = np.random.RandomState(92)
    for _ in range(34):
        x, y = rng.randint(0, W), rng.randint(G + 4, H - 2)
        col = ['#a8783a', '#c89a48', '#8a6a3a', '#6a8a3e'][rng.randint(4)]
        px(d, x, y, col); px(d, x + 1, y, col); px(d, x + 1, y - 1, mix(col, '#ffffff', .2))
    puddles = ((150, 164, 26), (330, 170, 30))
    for cx, cy, w in puddles:
        near = puddle(near, cx, cy, w, 4, cols=('#7a8a8e', '#9ab4c4', '#c8dce8'))
    d = ImageDraw.Draw(near)
    # 前景：路边的一溜矮草（站人的前面那条，不挡脚）
    for x in range(0, W, 3):
        if (x // 30) % 3 == 1:
            continue
        line(d, (x, H - 1, x + 1, H - 4 - (x * 7) % 3), '#6a9a4a')
    # ---- 水面的波光（4 帧）
    pw, ph = PX1 - PX0, PY1 - PY0
    n = 4
    pond = new(pw * n, ph)
    pd = ImageDraw.Draw(pond)
    rng = np.random.RandomState(93)
    marks = [(rng.randint(2, pw - 8), rng.randint(2, ph - 2), rng.randint(2, 6)) for _ in range(40)]
    for k in range(n):
        for i, (x, y, L) in enumerate(marks):
            if (i + k) % 4 == 0:
                continue
            xx = x + int(2 * np.sin(2 * np.pi * (k / n) + i))
            line(pd, (k * pw + xx, y, k * pw + xx + L, y), '#8ec0c8' if (i + k) % 3 else '#c8e4e8')
    pa_ = np.array(pond)
    my, mx = np.mgrid[0:ph, 0:pw * n].astype(float)
    pa_[np.sqrt((((mx % pw) + PX0 - PCX) / (PRX - 4)) ** 2 + ((my + PY0 - PCY) / (PRY - 2)) ** 2) >= 1] = 0
    pond = Image.fromarray(pa_, 'RGBA')
    # ---- 涟漪（key 'ring'）6 帧，扩散一圈
    rw, rh, rn = 60, 16, 6
    ring = new(rw * rn, rh)
    rd = ImageDraw.Draw(ring)
    for k in range(rn):
        for j, lag in enumerate((0, 2)):
            t = (k - lag) / (rn - 1)
            if t <= 0:
                continue
            ax, ay = 4 + 24 * t, 1.5 + 5.5 * t
            col = '#e0f0f4' if t < .6 else '#9ac8d0'
            d0 = ImageDraw.Draw(ring)
            d0.ellipse([k * rw + 30 - ax, 8 - ay, k * rw + 30 + ax, 8 + ay], outline=C(col))
        if k < 2:
            for dx, dy in ((-2, -3), (1, -4), (3, -2)):
                px(rd, k * rw + 30 + dx, 6 + dy - k, '#e0f0f4')
    # ---- 一圈淡红（key 'red'）：水面上一小团散开的淡红晕，不画别的
    red = glow_from_field(ell_field(56, 18, 28, 9, 26, 8, 1.6) * .8, (96, 16, 20), levels=4)
    RX, RY = PCX - 30, PCY - 8
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(entrance=[16, 146], bench=[82, 146], lamp=[124, 146], bin=[135, 146], sign=[177, 146],
                             pond_edge=[[230, 146], [320, 146], [410, 146]], pond=[320, 126], splash=[RX + 30, RY + 8],
                             lily=[[236, 128], [380, 124]], leaves=[[60, 160], [220, 158], [270, 166], [400, 162]],
                             puddles=[[cx, cy] for cx, cy, _ in puddles], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/park_pond/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/park_pond/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': 'bg/park_pond/pond', 'n': n, 'fps': 3, 'k': 1, 'x': PX0, 'y': PY0, 'w': pw, 'h': ph},
                        {'type': 'glow', 'image': 'bg/park_pond/red', 'k': 1, 'x': RX + 2, 'y': RY, 'key': 'red'},
                        {'type': 'strip', 'image': 'bg/park_pond/ring', 'n': rn, 'fps': 8, 'k': 1, 'x': RX, 'y': RY, 'w': rw, 'h': rh,
                         'key': 'ring'}], fg=[])
    prev = far.resize((W, H), Image.NEAREST)
    prev.alpha_composite(near)
    prev.alpha_composite(pond.crop((0, 0, pw, ph)), (PX0, PY0))
    preview('park_pond', {'p': prev}, ['p'], W)
    return save_layers('park_pond', {'far': far, 'near': near, 'pond': pond, 'ring': ring, 'red': red}, meta)


SCENES = {'higashikata_tvnight': higashikata_tvnight, 'open_field': open_field, 'morioh_harbor': morioh_harbor,
          'spw_ship': spw_ship, 'park_pond': park_pond}


def main(keys):
    path = os.path.join(LIB.META, 'bg_ch4.json')
    meta = LIB.load_json(path, {}) or {}
    for k in keys or SCENES:
        meta[k] = SCENES[k]()
        print('背景', k)
    LIB.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
