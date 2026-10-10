"""预览：python -B tools\\bg_new\\hongkong_night.py → _preview\\bg_hk\\hongkong_night_after*.png

第1章 香港夜街（游戏层重画，2026-10-10 bg-hk 代理）：1987 年九龙的夜市街（廟街一带）。
地图 960 宽、ground 154、可走 y 150–176、近景 640 循环，和原 exp_hongkong_night 的契约一样
（3 层 period 640 的 wrap + period 40 的路面黄线 wrap + neon + reflect；锚点 shopwindow 不变）。

  天空（static）：渐变 + 星星 + 弯月；路面底色同原片
  启德的飞机（clouds）：一架降落中的客机慢慢飞过楼顶
  远景（wrap k .25、vx −.5）：九龙群山的山脊 + 高楼，窗灯、天线红灯
  中景（wrap k .6）：唐楼，窗灯、冷气机、晾衫竹、天台水箱和天线、天台广告架
  近景（wrap k 1）：临街唐楼——铁窗花、冷气机、晾衫竹、雨水管、天台；地铺按原来的分段
       （橱窗那家还是 x 199–236，anchors.shopwindow 不变），每家店里面画货：烧腊、理发椅、涼茶铜壶、
       洋服橱窗（玻璃反光 + 假人）、上楼的红灯门口、药房货架、当铺遮羞板、电视墙、面档……；人行道砖、垃圾桶、消防栓
  街面（pano k 1，整条 960 不循环）：所有招牌的暗底、当铺的“蝠鼠吊金钱”押字牌、大牌档（帆布棚、灯泡、
       绿铁皮档口、炉火、挂着的叉烧）、菜单板（叉燒飯 / 雲吞麵 / 炒蜆）、报摊（杂志、报纸）、看相摊（八卦桌布、
       「睇相」布幡、灯笼）、挂风筝的「麻雀」招牌、路灯、「廟街」路牌、「碼頭」指路牌
  霓虹（neon，世界坐标，不再每 640 重复）：真字招牌——酒家 飛髮 涼茶 洋服 夜總會 藥房 當舖 旅館 大牌檔 粥麵
       茶餐廳 燒臘 理髮 藥材 麻雀 舞廳，部分会闪（JS 的 flick）
  会动的（strip k 1，世界坐标）：大牌档炉上的蒸汽（24 帧 @8 fps）、理发店的旋转灯柱（6 帧 @6 fps）
  倒影（reflect，源图改成 960 整条：近景 + 街面 + 亮着的霓虹，湿路面上看得见招牌的颜色）

剧情坐标对照（story\\ch01.js，一律不动剧情文件）：霓虹招牌 (400,60) = 「當舖」；橱窗倒影 (230,120) = 洋服橱窗
（anchors.shopwindow [205,112,230,146]）；菜单板 (520,120)；报摊电视 = 道具 tv (660,152) 放在报摊前；
招牌上的风筝 = 道具 kite (860,150) z 80 → 画在 y 62–70，正好挂在「麻雀」招牌上沿（y 68）；
大排档两张桌 (500 / 548, 164) 在帆布棚下、档口 (588–638) 在老板 (590 / 626) 身后；看相佬 (760,158) 在看相摊前。
"""
import sys
sys.dont_write_bytecode = True

import math
import os
from functools import lru_cache

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from engine import bg_asia as A
from engine.core import hash01, hrange, mix, gradient, paste

W, H = 320, 180
HK_W = 640
WORLD = 960
C = A._c4
GAPS = list(A._HK_GAPS)            # [(66,84),(236,254),(404,418),(556,572)]
FONT_PATH = r'C:\Windows\Fonts\simsun.ttc'

# 霓虹色
RED, PINK, CYAN, GREEN = (255, 64, 72), (255, 96, 196), (90, 230, 255), (100, 255, 150)
YEL, ORA, BLUE, VIO = (255, 222, 90), (255, 152, 56), (120, 150, 255), (196, 120, 255)

# (x, y, 字, 色, 字号, 竖排, 闪) —— x / y = 招牌板左上角（世界坐标，不含光晕）
SIGNS = [
    (16, 26, '酒家', RED, 16, True, False),
    (92, 78, '飛髮', CYAN, 12, False, False),
    (146, 40, '涼茶', GREEN, 12, True, False),
    (202, 80, '洋服', CYAN, 12, False, True),
    (264, 20, '夜總會', PINK, 16, True, True),
    (312, 76, '藥房', GREEN, 12, False, False),
    (390, 40, '當舖', RED, 16, True, False),        # 剧情「霓虹招牌」(400,60)
    (436, 28, '旅館', BLUE, 12, True, True),
    (478, 78, '大牌檔', YEL, 12, False, False),
    (538, 34, '粥麵', ORA, 12, True, False),
    (596, 24, '茶餐廳', CYAN, 12, True, True),
    (668, 30, '燒臘', ORA, 16, True, False),
    (728, 46, '理髮', VIO, 12, True, False),
    (788, 78, '藥材', YEL, 12, False, True),
    (846, 68, '麻雀', GREEN, 12, False, False),     # 风筝挂在这块的上沿
    (904, 22, '舞廳', PINK, 16, True, True),
]
SIGN_PAD = 7

# 剧情用到的几样东西（世界坐标的框，给自检和锚点用）
MENU_BOX = (500, 104, 540, 146)
STALL_BOX = (588, 108, 640, 151)
CANOPY = (470, 92, 638, 106)
NEWS_BOX = (624, 94, 702, 152)
FORTUNE_BOX = (742, 100, 796, 151)
PAWN_BAT = (388, 82, 414, 101)
LAMPS = (70, 416, 880)                 # 都立在巷口，灯杆不穿过招牌
HARBOR_SIGN = (920, 92, 956, 108)
STEAM_BOX = (596, 66, 628, 116)
POLE_BOX = (726, 112, 734, 138)
STEAM_N, STEAM_FPS = 24, 8.0
POLE_N, POLE_FPS = 6, 6.0


# ---------------------------------------------------------------- 小工具
def new(w, h, col=None):
    return Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0) if col is None else C(col))


def rect(d, box, fill, outline=None):
    d.rectangle(box, fill=C(fill) if fill is not None else None, outline=C(outline) if outline else None)


def line(d, pts, fill, width=1):
    d.line(pts, fill=C(fill), width=width)


def px(d, x, y, fill):
    d.point((x, y), fill=C(fill))


def dim(c, k):
    return tuple(int(v * k) for v in c)


@lru_cache(maxsize=4)
def font(sz):
    return ImageFont.truetype(FONT_PATH, sz)


@lru_cache(maxsize=256)
def glyph(ch, sz):
    """simsun 的点阵字（12 / 16 px 有内嵌点阵，fontmode '1' 不糊）→ sz×sz 的 L 图（255 = 笔画）。"""
    im = Image.new('L', (sz + 2, sz + 2), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.text((0, 0), ch, font=font(sz), fill=255)
    return im.crop((0, 0, sz, sz))


def text_size(s, sz, vertical, gap=1):
    n = len(s)
    return (sz, n * sz + (n - 1) * gap) if vertical else (n * sz + (n - 1) * gap, sz)


def put_text(img, x, y, s, sz, col, vertical=False, gap=1):
    lay = Image.new('RGBA', (sz, sz), C(col))
    for i, ch in enumerate(s):
        gx, gy = (x, y + i * (sz + gap)) if vertical else (x + i * (sz + gap), y)
        img.paste(lay, (int(gx), int(gy)), glyph(ch, sz))


def blend_ellipse(img, box, col, alpha):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse(box, fill=C(col, int(alpha)))
    img.alpha_composite(lay)


def glow(img, cx, cy, rx, ry, col, alpha, rings=4):
    A._glow(img, cx, cy, rx, ry, col, alpha, rings=rings)


def wrapped(fn, period=HK_W):
    """周期层：同一样东西在 x − 640 / x / x + 640 各画一次（跨接缝的自动接上）。"""
    for dx in (-period, 0, period):
        fn(dx)


def shopfronts():
    """和 bg_jojo._hk_shopfronts 同一算法（原片近景楼面的分段）→ [(x, w, k)]。"""
    edges = [0]
    for g0, g1 in GAPS:
        edges += [g0, g1]
    edges.append(HK_W)
    out, k = [], 0
    for seg in range(0, len(edges), 2):
        sx0, sx1 = edges[seg], edges[seg + 1]
        x = sx0
        while x < sx1:
            w = min(int(hrange(44, 70, k, 21)), sx1 - x)
            if sx1 - (x + w) < 20:
                w = sx1 - x
            out.append((x, w, k))
            x += w
            k += 1
    return out


# ---------------------------------------------------------------- 招牌
def sign_box(s):
    x, y, txt, col, sz, vert, fl = s
    n = len(txt)
    if vert:
        return x, y, x + sz + 6, y + n * (sz + 1) + 5
    return x, y, x + n * (sz + 1) + 5, y + sz + 6


@lru_cache(maxsize=64)
def neon_img(idx, lit):
    """招牌（含 SIGN_PAD 光晕边）。lit：亮版（光晕 + 白芯字）；否则暗底板（灯管和字都是暗的颜色）。"""
    x, y, txt, col, sz, vert, fl = SIGNS[idx]
    x0, y0, x1, y1 = sign_box(SIGNS[idx])
    bw, bh = x1 - x0, y1 - y0
    p = SIGN_PAD
    im = new(bw + 2 * p, bh + 2 * p)
    if lit:
        glow(im, p + bw / 2, p + bh / 2, bw / 2 + p, bh / 2 + p, col, 120)
    d = ImageDraw.Draw(im)
    back = (22, 12, 30)
    tube = col if lit else mix(col, back, 0.72)
    rect(d, (p, p, p + bw - 1, p + bh - 1), back, tube)
    rect(d, (p + 1, p + 1, p + bw - 2, p + bh - 2), None, mix(tube, back, 0.55))
    core = mix(col, (255, 255, 255), 0.6) if lit else mix(col, back, 0.6)
    tx, ty = p + 3, p + 3
    put_text(im, tx, ty, txt, sz, core, vertical=vert)
    if lit:                                              # 灯管颜色的描边（只描笔画两头，字不糊）
        a = np.array(im)
        m = np.zeros(a.shape[:2], bool)
        gm = np.zeros(a.shape[:2], bool)
        for i, ch in enumerate(txt):
            g = np.array(glyph(ch, sz)) > 0
            gx, gy = (tx, ty + i * (sz + 1)) if vert else (tx + i * (sz + 1), ty)
            gm[gy:gy + sz, gx:gx + sz] |= g
        m[:, 1:] |= gm[:, :-1]
        m[:, :-1] |= gm[:, 1:]
        edge = m & ~gm
        inner = np.zeros_like(gm)
        inner[p + 2:p + bh - 2, p + 2:p + bw - 2] = True
        edge &= inner
        a[edge, :3] = np.array(mix(col, back, 0.25), np.uint8)
        im = Image.fromarray(a, 'RGBA')
    return im


# ---------------------------------------------------------------- 天空 / 远景 / 中景
def sky_img():
    sky = new(W, H)
    gradient(sky, (0, 0, W, H), [(10, 8, 30), (26, 16, 54), (60, 26, 80), (120, 46, 100)], bands=8)
    A._stars(sky, (0, 0, W, 50), 30, 3)
    d = ImageDraw.Draw(sky)
    for i in range(10):                                  # 几颗亮星（十字）
        sx, sy = int(hrange(4, 316, i, 71)), int(hrange(3, 34, i, 72))
        px(d, sx, sy, (255, 250, 230))
        if i % 3 == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                px(d, sx + dx, sy + dy, (150, 140, 190))
    glow(sky, 274, 17, 16, 14, (220, 200, 255), 40)      # 弯月
    d = ImageDraw.Draw(sky)
    d.ellipse((268, 11, 280, 23), fill=C((250, 240, 200)))
    d.ellipse((271, 9, 283, 21), fill=C(mix((26, 16, 54), (10, 8, 30), 0.3)))
    px(d, 270, 15, (255, 255, 235))
    return sky


def far_img():
    im = new(HK_W, H)
    d = ImageDraw.Draw(im)
    # 九龙群山（狮子山一带）的山脊：两条正弦叠起来，0 和 640 接得上
    pts = [(0, H)]
    for x in range(0, HK_W + 1, 4):
        y = 60 + 9 * math.sin(2 * math.pi * x / HK_W * 2 + 0.4) + 5 * math.sin(2 * math.pi * x / HK_W * 5 + 1.3) \
            - 7 * max(0.0, math.sin(2 * math.pi * x / HK_W * 1 + 2.2)) ** 3
        pts.append((x, int(y)))
    pts.append((HK_W, H))
    d.polygon(pts, fill=C((28, 20, 50)))
    for (x0, y0), (x1, y1) in zip(pts[1:-2], pts[2:-1]):
        d.line((x0, y0, x1, y1), fill=C((46, 34, 74)))

    def draw(dx):
        for i in range(26):
            x = int(i * 24.6 + hrange(-5, 5, i, 1)) + dx
            w = int(hrange(12, 22, i, 2))
            top = int(hrange(34, 84, i, 3))
            col = (40 + i % 3 * 6, 32 + i % 2 * 4, 76)
            rect(d, (x, top, x + w, 130), col)
            line(d, (x, top, x + w, top), (72, 58, 112))
            line(d, (x + w, top + 1, x + w, 130), dim(col, 0.7))
            for wy in range(top + 3, 128, 4):
                for wx in range(x + 2, x + w - 1, 3):
                    if hash01(wx - dx, wy, 9) < 0.27:
                        px(d, wx, wy, (250, 210, 120) if hash01(wx - dx, wy, 4) < 0.6 else (140, 220, 255))
            if i % 4 == 0:                                   # 天线 + 红灯（wrap 层不能闪，常亮）
                line(d, (x + w // 2, top - 8, x + w // 2, top), (80, 70, 110))
                px(d, x + w // 2, top - 8, (255, 60, 60))
            if i % 5 == 2:                                   # 楼顶的广告灯箱（远，只是一条亮带）
                rect(d, (x + 1, top - 4, x + w - 1, top - 1), (60, 40, 80), (110, 70, 120))
    wrapped(draw)
    return im


def mid_img():
    im = new(HK_W, H)
    d = ImageDraw.Draw(im)
    blds = []
    x, k = 0, 0
    while x < HK_W:
        w = int(hrange(34, 56, k, 11))
        top = int(hrange(22, 50, k, 12))
        blds.append((x, w, top, k))
        x += w + int(hrange(0, 4, k, 16))
        k += 1
    span = x                                             # 原片同款：最后一栋跨过 640 的部分折回左边

    def draw(dx):
        for (x, w, top, k) in blds:
            x += dx
            col = [(56, 42, 76), (48, 40, 70), (62, 46, 70), (44, 44, 72)][k % 4]
            rect(d, (x, top, x + w, 140), col)
            line(d, (x, top, x + w, top), mix(col, (160, 140, 200), 0.3))
            line(d, (x + w, top, x + w, 140), dim(col, 0.7))
            for wy in range(top + 4, 132, 7):
                for wx in range(x + 3, x + w - 5, 7):
                    h = (wx - dx, wy)
                    lit = hash01(*h, 13) < 0.45
                    rect(d, (wx, wy, wx + 4, wy + 3), (236, 190, 110) if lit else (30, 24, 46))
                    if lit and hash01(*h, 14) < 0.3:
                        rect(d, (wx, wy, wx + 4, wy + 1), (120, 200, 230))
                    if lit and hash01(*h, 17) < 0.25:            # 窗帘
                        rect(d, (wx, wy, wx + 1, wy + 3), (170, 110, 90))
                    line(d, (wx - 1, wy + 4, wx + 5, wy + 4), dim(col, 0.6))
                    r = hash01(*h, 15)
                    if r < 0.18:
                        rect(d, (wx + 1, wy + 5, wx + 4, wy + 6), (150, 150, 160))      # 冷气机
                    elif r < 0.3:                                                     # 晾衫竹 + 衣服
                        line(d, (wx + 4, wy + 1, wx + 9, wy + 1), (120, 110, 90))
                        for q in range(2):
                            cc = [(200, 70, 70), (230, 230, 240), (80, 120, 200), (230, 200, 80)][int(hash01(*h, 18 + q) * 4)]
                            rect(d, (wx + 5 + q * 2, wy + 2, wx + 5 + q * 2, wy + 3), dim(cc, 0.75))
            # 天台：水箱 / 天线 / 小屋
            r = hash01(k, 19)
            if r < 0.4:
                tx = x + int(hrange(3, max(4, w - 10), k, 20))
                rect(d, (tx, top - 5, tx + 6, top - 1), (70, 64, 86), (40, 34, 52))
                line(d, (tx + 1, top - 1, tx + 1, top), (40, 34, 52))
                line(d, (tx + 5, top - 1, tx + 5, top), (40, 34, 52))
            elif r < 0.7:
                ax = x + int(hrange(4, max(5, w - 6), k, 21))
                line(d, (ax, top - 9, ax, top), (90, 80, 110))
                line(d, (ax - 3, top - 7, ax + 3, top - 7), (90, 80, 110))
                line(d, (ax - 2, top - 4, ax + 2, top - 4), (90, 80, 110))
            if k % 6 == 3:                                  # 天台广告架（没开灯的灯管）
                bx = x + 4
                rect(d, (bx, top - 12, bx + min(26, w - 8), top - 4), (38, 30, 52), (88, 66, 108))
                for q in range(bx + 3, bx + min(26, w - 8) - 2, 5):
                    rect(d, (q, top - 10, q + 2, top - 6), (70, 56, 92))
                line(d, (bx + 2, top - 4, bx + 2, top), (60, 50, 70))
                line(d, (bx + min(26, w - 8) - 2, top - 4, bx + min(26, w - 8) - 2, top), (60, 50, 70))
    assert span >= HK_W
    wrapped(draw)                                        # 最后一栋跨过 640 的部分在左边接上（原片是直接切掉）
    return A._grade(im, sat=0.9, val=0.88)


# ---------------------------------------------------------------- 近景（临街唐楼 + 地铺，640 循环）
FACADES = [(58, 48, 66), (46, 52, 62), (64, 46, 54), (50, 46, 62), (58, 54, 60)]
INNER = [(255, 208, 130), (230, 246, 255), (255, 186, 150), (200, 255, 220)]
AWN = [(200, 40, 50), (40, 120, 90), (220, 150, 40), (60, 70, 160), (150, 50, 120)]
# 每家店里卖什么（按原片分段的序号 k；+640 重复的那半条也一样）
SHOP_KIND = {0: 'roast', 1: 'barber', 2: 'herbal', 3: 'tailor', 4: 'stairs', 5: 'pharmacy', 6: 'pawn',
             7: 'tv', 8: 'kitchen', 9: 'noodle', 10: 'shutter'}


def _window(d, wx, wy, col, seed):
    lit = hash01(seed, 23) < 0.36
    wc = [(226, 170, 96), (150, 210, 240), (240, 120, 150)][int(hash01(seed, 25) * 3)]
    rect(d, (wx, wy, wx + 6, wy + 6), wc if lit else (22, 18, 34))
    if lit:
        if hash01(seed, 31) < 0.4:                                    # 窗帘
            rect(d, (wx, wy, wx + 2, wy + 6), mix(wc, (90, 40, 40), 0.45))
        if hash01(seed, 32) < 0.3:                                    # 里面的吊扇 / 人影
            line(d, (wx + 3, wy + 1, wx + 5, wy + 1), mix(wc, (40, 30, 30), 0.6))
            rect(d, (wx + 4, wy + 3, wx + 5, wy + 6), mix(wc, (40, 30, 30), 0.55))
    line(d, (wx + 3, wy, wx + 3, wy + 6), mix(col, (20, 16, 26), 0.4))   # 窗框
    line(d, (wx - 2, wy + 7, wx + 8, wy + 7), mix(col, (160, 150, 170), 0.35))
    line(d, (wx - 2, wy + 8, wx + 8, wy + 8), (24, 18, 30))
    r = hash01(seed, 26)
    if r < 0.34:                                                      # 铁窗花（往外凸的笼子）
        g = (96, 98, 108) if lit else (70, 70, 82)
        rect(d, (wx - 1, wy - 1, wx + 7, wy + 7), None, g)
        for q in range(wx + 1, wx + 7, 2):
            line(d, (q, wy, q, wy + 6), g)
        if hash01(seed, 27) < 0.5:                                    # 花盆
            px(d, wx + 1, wy + 6, (60, 140, 70))
            px(d, wx + 2, wy + 5, (80, 170, 80))
    r2 = hash01(seed, 28)
    if r2 < 0.24:                                                     # 冷气机 + 滴水印
        rect(d, (wx + 1, wy + 9, wx + 6, wy + 11), (118, 118, 130))
        line(d, (wx + 2, wy + 10, wx + 5, wy + 10), (80, 80, 92))
        line(d, (wx + 3, wy + 12, wx + 3, wy + 14), mix(col, (20, 20, 30), 0.3))
    elif r2 < 0.42:                                                   # 晾衫竹 + 衣服
        L = int(hrange(7, 12, seed, 29))
        line(d, (wx + 7, wy + 2, wx + 7 + L, wy + 2), (150, 130, 90))
        for q in range(int(L // 3)):
            cc = [(220, 80, 80), (240, 240, 245), (90, 130, 220), (240, 210, 90), (120, 200, 140)][int(hash01(seed, 30 + q) * 5)]
            hh = 3 + int(hash01(seed, 40 + q) * 2)
            rect(d, (wx + 8 + q * 3, wy + 3, wx + 9 + q * 3, wy + 2 + hh), dim(cc, 0.7))


def _interior(img, d, x, w, k, inner):
    kind = SHOP_KIND.get(k, 'goods')
    x0, x1 = x + 6, x + w - 6
    ink = mix(inner, (40, 20, 30), 0.7)
    mid_c = mix(inner, (120, 60, 40), 0.55)
    line(d, (x0 + 1, 113, x1 - 1, 113), mix(inner, (255, 255, 255), 0.6))        # 光管
    if kind == 'roast':                                       # 烧腊：玻璃柜里挂着烧鹅、叉烧
        line(d, (x0 + 2, 116, x1 - 2, 116), (120, 110, 100))
        for i, gx in enumerate(range(x0 + 4, x1 - 6, 7)):
            if i % 2 == 0:
                d.polygon([(gx, 118), (gx + 4, 118), (gx + 5, 124), (gx + 2, 128), (gx - 1, 124)], fill=C((150, 70, 30)))
                px(d, gx + 1, 120, (230, 150, 80))
            else:
                rect(d, (gx + 1, 118, gx + 3, 127), (170, 40, 30))
                px(d, gx + 2, 119, (230, 110, 80))
            line(d, (gx + 2, 116, gx + 2, 118), (80, 70, 70))
        rect(d, (x0, 133, x1, 146), (200, 200, 205))
        line(d, (x0, 133, x1, 133), (250, 250, 255))
        rect(d, (x0 + 3, 136, x0 + 9, 139), (140, 60, 40))   # 砧板
    elif kind == 'barber':                                    # 飞发铺：镜子 + 理发椅
        for gx in range(x0 + 2, x1 - 10, 14):
            rect(d, (gx, 116, gx + 9, 126), (170, 200, 220), (90, 90, 100))
            line(d, (gx + 1, 117, gx + 3, 119), (240, 250, 255))
            rect(d, (gx + 2, 130, gx + 7, 136), (150, 30, 40))
            rect(d, (gx + 1, 128, gx + 8, 130), (170, 40, 50))
            line(d, (gx + 4, 137, gx + 4, 144), (180, 180, 190))
            line(d, (gx + 2, 145, gx + 6, 145), (180, 180, 190))
    elif kind == 'herbal':                                    # 凉茶铺：两只铜壶 + 碗
        for gx in (x0 + 6, x0 + 24):
            d.ellipse((gx, 120, gx + 12, 134), fill=C((200, 140, 50)), outline=C((120, 70, 20)))
            rect(d, (gx + 4, 116, gx + 8, 120), (210, 150, 60))
            line(d, (gx + 3, 124, gx + 5, 122), (255, 220, 140))
            rect(d, (gx + 12, 128, gx + 14, 129), (230, 200, 140))
        rect(d, (x0, 136, x1, 146), (110, 60, 40))
        for q in range(x0 + 2, x1 - 2, 4):
            d.ellipse((q, 133, q + 2, 135), fill=C((240, 236, 225)))
    elif kind == 'tailor':                                    # 洋服橱窗：假人、布料，玻璃上的反光
        rect(d, (x0, 112, x1, 146), mix(inner, (40, 40, 60), 0.35))
        for i, gx in enumerate((x0 + 4, x0 + 15)):
            cc = [(60, 60, 90), (150, 120, 90)][i]
            d.ellipse((gx + 1, 117, gx + 5, 121), fill=C((210, 200, 190)))
            d.polygon([(gx - 1, 122), (gx + 7, 122), (gx + 6, 136), (gx, 136)], fill=C(cc))
            line(d, (gx + 3, 122, gx + 3, 130), (240, 240, 240))
            line(d, (gx + 3, 137, gx + 3, 145), (90, 80, 70))
        for q in range(4):
            rect(d, (x0 + 1 + q * 6, 140, x0 + 5 + q * 6, 145), [(120, 40, 50), (40, 70, 120), (180, 160, 120), (70, 70, 70)][q])
        for s in (0, 9, 15):                                   # 玻璃斜反光
            for j in range(10):
                xx, yy = x0 + 2 + s + j, 144 - j * 3
                if x0 <= xx <= x1 and 112 <= yy <= 146:
                    px(d, xx, yy, (250, 250, 255))
                    if yy + 1 <= 146:
                        px(d, xx, yy + 1, mix(inner, (255, 255, 255), 0.6))
        line(d, (x0, 112, x0, 146), (180, 170, 150))
        line(d, (x1, 112, x1, 146), (180, 170, 150))
        line(d, (x0, 129, x1, 129), (150, 140, 120))
    elif kind == 'stairs':                                    # 上楼的窄门口：红灯 + 楼梯
        rect(d, (x0, 112, x1, 146), (60, 20, 30))
        mx_ = (x0 + x1) // 2
        rect(d, (mx_ - 9, 114, mx_ + 9, 146), (120, 30, 40))
        for q in range(8):
            yy = 146 - q * 4
            rect(d, (mx_ - 8 + q, yy - 3, mx_ + 8 - q, yy), mix((200, 60, 70), (60, 20, 30), q / 9))
            line(d, (mx_ - 8 + q, yy - 3, mx_ + 8 - q, yy - 3), (240, 120, 120))
        glow(img, mx_, 116, 12, 6, (255, 60, 80), 90, rings=3)
    elif kind == 'pharmacy':                                  # 药房：货架 + 盒子
        for sy in (118, 126, 134):
            line(d, (x0 + 1, sy + 5, x1 - 1, sy + 5), (120, 110, 100))
            for q in range(x0 + 2, x1 - 3, 3):
                cc = [(230, 80, 80), (80, 160, 230), (240, 230, 220), (90, 200, 120), (240, 200, 70)][int(hash01(q, sy, 5) * 5)]
                hh = 2 + int(hash01(q, sy, 6) * 3)
                rect(d, (q, sy + 5 - hh, q + 1, sy + 4), cc)
        rect(d, (x0, 140, x1, 146), (200, 210, 205))
        line(d, (x0 + w // 2 - 8, 142, x0 + w // 2 - 4, 142), (40, 160, 80))
        line(d, (x0 + w // 2 - 6, 140, x0 + w // 2 - 6, 144), (40, 160, 80))
    elif kind == 'pawn':                                      # 当铺：门口的遮羞板 + 高柜台
        rect(d, (x0, 112, x1, 146), (90, 60, 40))
        for q in range(x0 + 3, x1 - 3, 5):
            rect(d, (q, 115, q + 3, 128), (60, 40, 30))
            line(d, (q, 115, q + 3, 115), (130, 90, 60))
        rect(d, (x0 + 4, 128, x1 - 14, 146), (70, 30, 24), (40, 20, 16))      # 遮羞板
        line(d, (x0 + 5, 129, x1 - 15, 129), (150, 60, 40))
        d.ellipse((x0 + 9, 133, x0 + 17, 141), outline=C((220, 180, 70)))
        rect(d, (x1 - 12, 131, x1 - 2, 146), (24, 16, 18))                     # 侧门
    elif kind == 'tv':                                        # 电器铺：一墙电视（蓝光）
        rect(d, (x0, 112, x1, 146), (40, 40, 56))
        for row, sy in enumerate((115, 125, 135)):
            for q in range(x0 + 2 + row % 2 * 3, x1 - 8, 9):
                rect(d, (q, sy, q + 7, sy + 7), (24, 24, 28))
                cc = [(90, 150, 230), (120, 200, 255), (220, 230, 255), (90, 200, 160)][int(hash01(q, sy, 8) * 4)]
                rect(d, (q + 1, sy + 1, q + 6, sy + 5), cc)
                line(d, (q + 1, sy + 3, q + 6, sy + 3), mix(cc, (255, 255, 255), 0.4))
        glow(img, (x0 + x1) // 2, 130, (x1 - x0) // 2, 14, (110, 170, 255), 40, rings=3)
    elif kind == 'kitchen':                                   # 大牌档背后的厨房：白瓷砖 + 锅具
        rect(d, (x0, 112, x1, 146), (210, 214, 206))
        for yy in range(116, 146, 4):
            line(d, (x0, yy, x1, yy), (170, 176, 170))
        for q in range(x0, x1, 4):
            line(d, (q, 112, q, 146), (180, 186, 180))
        for i, q in enumerate(range(x0 + 4, x1 - 6, 8)):
            d.ellipse((q, 117, q + 5, 122), outline=C((70, 70, 80)))
            line(d, (q + 2, 115, q + 2, 117), (70, 70, 80))
        rect(d, (x0, 134, x1, 146), (140, 140, 150))
    elif kind == 'noodle':                                    # 面档：玻璃柜（面饼、鱼蛋）
        rect(d, (x0, 112, x1, 146), mix(inner, (60, 40, 30), 0.25))
        rect(d, (x0 + 1, 126, x1 - 1, 138), (220, 230, 225), (150, 150, 140))
        for q in range(x0 + 3, x1 - 3, 4):
            d.ellipse((q, 131, q + 2, 133), fill=C((240, 210, 120)))
        for q in range(x0 + 2, x1 - 2, 5):
            line(d, (q, 117, q + 2, 121), (240, 220, 160))
        rect(d, (x0, 139, x1, 146), (150, 90, 60))
    elif kind == 'shutter':                                   # 拉闸了：铁闸（后面是大牌档档口）
        rect(d, (x0, 112, x1, 146), (96, 96, 108))
        for yy in range(113, 146, 2):
            line(d, (x0, yy, x1, yy), (78, 78, 90))
        line(d, (x0 + 3, 128, x1 - 3, 131), (160, 60, 70))                     # 喷漆
        line(d, (x0 + 6, 133, x0 + 16, 130), (200, 200, 90))
        rect(d, ((x0 + x1) // 2 - 2, 141, (x0 + x1) // 2 + 2, 144), (60, 60, 70))
    if kind in ('roast', 'herbal', 'pharmacy', 'noodle', 'pawn') and hash01(k, 27) < 0.75:   # 店员
        px_ = x + 10 + int(hrange(0, max(1, w - 24), k, 28))
        rect(d, (px_, 134, px_ + 5, 146), ink)
        d.ellipse((px_, 129, px_ + 5, 134), fill=C(ink))
    return mid_c


def near_img():
    im = new(HK_W, H)
    d = ImageDraw.Draw(im)
    fronts = shopfronts()
    for (x, w, k) in fronts:
        top = int(hrange(4, 40, k, 24))
        col = FACADES[k % len(FACADES)]
        rect(d, (x, top, x + w, 150), col)
        for yy in range(top + 2, 100, 3):                      # 墙面的旧痕（竖向深浅）
            if hash01(x, yy, 3) < 0.25:
                line(d, (x + 1, yy, x + 1 + int(hash01(x, yy, 4) * (w - 2)), yy), mix(col, (30, 26, 40), 0.18))
        line(d, (x, top, x + w, top), mix(col, (190, 150, 220), 0.35))
        line(d, (x, top + 1, x + w, top + 1), mix(col, (20, 16, 26), 0.3))
        line(d, (x, top, x, 150), mix(col, (0, 0, 0), 0.45))
        # 天台：女儿墙、水箱、天线、僭建铁皮屋
        r = hash01(k, 41)
        if r < 0.45:
            tx = x + int(hrange(4, max(5, w - 14), k, 42))
            rect(d, (tx, top - 7, tx + 9, top - 1), (84, 80, 96), (44, 40, 56))
            line(d, (tx + 1, top - 6, tx + 8, top - 6), (120, 116, 130))
            line(d, (tx + 2, top - 1, tx + 2, top), (44, 40, 56))
            line(d, (tx + 7, top - 1, tx + 7, top), (44, 40, 56))
        elif r < 0.75:
            tx = x + int(hrange(3, max(4, w - 18), k, 43))
            rect(d, (tx, top - 6, tx + 14, top - 1), (70, 76, 84))
            for q in range(tx, tx + 15, 2):
                px(d, q, top - 6, (110, 116, 120))
            rect(d, (tx + 3, top - 4, tx + 5, top - 1), (220, 190, 110))
        if top > 6:
            ax = x + w - 6
            line(d, (ax, top - 10, ax, top), (96, 90, 112))
            line(d, (ax - 4, top - 8, ax + 3, top - 8), (96, 90, 112))
            line(d, (ax - 3, top - 5, ax + 2, top - 5), (96, 90, 112))
        # 雨水管
        line(d, (x + w - 2, top + 2, x + w - 2, 100), mix(col, (130, 130, 140), 0.35))
        for yy in range(top + 6, 100, 14):
            px(d, x + w - 2, yy, (40, 36, 50))
        # 窗
        for wy in range(top + 6, 92, 13):
            for wx in range(x + 5, x + w - 9, 11):
                _window(d, wx, wy, col, wx * 131 + wy)
        # 地铺
        rect(d, (x + 2, 104, x + w - 2, 148), (30, 22, 34))
        inner = INNER[k % 4]
        rect(d, (x + 6, 112, x + w - 6, 146), mix(inner, (60, 40, 50), 0.22))
        _interior(im, d, x, w, k, inner)
        d = ImageDraw.Draw(im)
        rect(d, (x + 3, 108, x + w - 3, 111), (52, 50, 60))      # 铁闸卷筒
        line(d, (x + 3, 111, x + w - 3, 111), (24, 20, 28))
        line(d, (x + 5, 112, x + 5, 146), (60, 56, 70))          # 门框 / 闸轨
        line(d, (x + w - 5, 112, x + w - 5, 146), (60, 56, 70))
        aw = AWN[k % len(AWN)]
        for ax in range(x + 2, x + w - 2, 6):
            d.polygon([(ax, 100), (ax + 6, 100), (ax + 7, 108), (ax + 1, 108)],
                      fill=C(aw if (ax // 6) % 2 else mix(aw, (255, 255, 255), 0.45)))
        line(d, (x + 2, 100, x + w - 2, 100), mix(aw, (255, 255, 255), 0.3))
        for ax in range(x + 3, x + w - 3, 4):                    # 帆布垂边
            px(d, ax, 109, mix(aw, (20, 10, 20), 0.4))
        line(d, (x + 2, 108, x + w - 2, 108), (24, 16, 24))
    # 横街：往里走的暗巷、挂在半空的灯笼、巷尾的灯
    for g0, g1 in GAPS:                                          # 上面留空：从巷口看得见后面的楼和天空（同原片）
        rect(d, (g0, 64, g1, 150), (26, 20, 38))
        rect(d, (g0 + 4, 72, g1 - 4, 132), (36, 28, 52))
        line(d, (g0 + 4, 72, g1 - 4, 72), (60, 50, 76))
        for yy in range(76, 128, 9):
            if hash01(g0, yy, 5) < 0.6:
                rect(d, (g0 + 6, yy, g0 + 8, yy + 3), (240, 200, 120))
        glow(im, (g0 + g1) / 2, 128, (g1 - g0) / 2, 10, (255, 170, 90), 50, rings=3)
        d = ImageDraw.Draw(im)
        d.polygon([(g0, 150), (g1, 150), (g1 - 3, 132), (g0 + 3, 132)], fill=C((30, 24, 40)))
        line(d, (g0, 92, g1, 96), (60, 50, 60))                  # 横过巷口的电线
        for q in range(3):
            lx = g0 + 4 + q * ((g1 - g0 - 8) // 2)
            ly = 96 + q * 5
            line(d, (lx, ly - 5, lx, ly), (60, 50, 60))
            d.ellipse((lx - 2, ly, lx + 2, ly + 5), fill=C((250, 80, 70)))
            px(d, lx, ly + 1, (255, 200, 150))
        line(d, (g0 + 2, 120, g0 + 2, 150), (70, 60, 80))      # 巷口的水管
    # 人行道 + 路缘
    rect(d, (0, 146, HK_W, 152), (74, 66, 90))
    line(d, (0, 146, HK_W, 146), (120, 110, 140))
    for x in range(0, HK_W, 8):
        line(d, (x, 147, x, 151), (64, 56, 80))
    line(d, (0, 149, HK_W, 149), (68, 60, 84))
    line(d, (0, 152, HK_W, 152), (30, 24, 40))
    # 人行道上的东西（640 重复，挑重复了也不碍事的位置）
    for bx in (186,):                                            # 橙色垃圾桶
        rect(d, (bx, 138, bx + 6, 148), (220, 120, 40), (120, 60, 20))
        line(d, (bx + 1, 140, bx + 5, 140), (255, 170, 90))
        rect(d, (bx - 1, 137, bx + 7, 138), (90, 80, 70))
    for hx in (296,):                                            # 消防栓
        rect(d, (hx, 141, hx + 4, 148), (200, 40, 40))
        rect(d, (hx - 1, 143, hx + 5, 144), (200, 40, 40))
        rect(d, (hx + 1, 139, hx + 3, 140), (230, 70, 60))
    return im


# ---------------------------------------------------------------- 街面（960 整条，不循环）
def _lamp(img, d, x):
    line(d, (x, 60, x, 150), (60, 64, 70), width=2)
    line(d, (x + 1, 62, x + 1, 150), (100, 104, 112))
    d.arc((x, 54, x + 14, 66), 180, 270, fill=C((60, 64, 70)), width=2)
    line(d, (x + 7, 54, x + 14, 54), (60, 64, 70), width=2)
    rect(d, (x + 11, 55, x + 17, 57), (40, 40, 46))
    glow(img, x + 14, 60, 18, 14, (255, 170, 80), 70)
    d = ImageDraw.Draw(img)
    rect(d, (x + 12, 57, x + 16, 58), (255, 220, 150))
    rect(d, (x - 1, 146, x + 2, 150), (50, 54, 60))
    return d


def street_img():
    im = new(WORLD, H)
    d = ImageDraw.Draw(im)
    # 招牌暗底（亮版由 neon 层叠上去；flick 的那几块灭的时候露出这里）+ 挂架
    for i, s in enumerate(SIGNS):
        x0, y0, x1, y1 = sign_box(s)
        paste(im, neon_img(i, False), x0 - SIGN_PAD, y0 - SIGN_PAD)
        bx = x0 + (x1 - x0) // 2
        line(d, (bx - 3, y0 - 4, bx - 3, y0), (90, 90, 100))
        line(d, (bx + 3, y0 - 4, bx + 3, y0), (90, 90, 100))
        line(d, (x0 - 2, y0 - 4, x1 + 1, y0 - 4), (70, 70, 82))
    # 当铺：蝠鼠吊金钱（押）
    bx0, by0, bx1, by1 = PAWN_BAT
    cx = (bx0 + bx1) // 2
    line(d, (cx, 79, cx, by0 + 2), (110, 100, 80))
    d.polygon([(bx0, by0 + 3), (cx - 3, by0), (cx, by0 + 2), (cx + 3, by0), (bx1, by0 + 3), (bx1 - 3, by0 + 6),
               (cx + 2, by0 + 5), (cx - 2, by0 + 5), (bx0 + 3, by0 + 6)], fill=C((150, 30, 30)), outline=C((60, 10, 10)))
    d.ellipse((cx - 7, by0 + 5, cx + 7, by0 + 19), fill=C((236, 190, 70)), outline=C((120, 70, 20)))
    put_text(im, cx - 6, by0 + 6, '押', 12, (150, 20, 20))
    # 大牌档：帆布棚 + 灯泡 + 竹竿
    c0, cy0, c1, cy1 = CANOPY
    for q in (c0 + 2, 552, c1 - 2):
        line(d, (q, cy0 + 4, q, 150), (70, 60, 50))
    pts = [(c0, cy0 + 4)]
    for xx in range(c0, c1 + 1, 2):
        pts.append((xx, cy0 + 2 + int(2 * math.sin((xx - c0) / (c1 - c0) * math.pi * 3) ** 2)))
    for xx in range(c1, c0 - 1, -2):
        sc = ((xx - c0) // 8) % 2
        pts.append((xx, cy1 - 3 + sc * 2 + int(2 * math.sin((xx - c0) / (c1 - c0) * math.pi * 3) ** 2)))
    d.polygon(pts, fill=C((44, 112, 92)))
    for xx in range(c0, c1, 16):
        d.polygon([(xx, cy0 + 3), (xx + 8, cy0 + 3), (xx + 8, cy1 - 2), (xx, cy1 - 2)], fill=C((70, 146, 118)))
    line(d, (c0, cy0 + 3, c1, cy0 + 3), (120, 190, 160))
    for xx in range(c0, c1, 3):
        px(d, xx, cy1 - 1, (30, 70, 60))
    for bx in (490, 528, 566, 604):
        line(d, (bx, cy1 - 1, bx, cy1 + 2), (40, 40, 40))
        glow(im, bx, cy1 + 5, 15, 11, (255, 200, 120), 70)
        d = ImageDraw.Draw(im)
        d.ellipse((bx - 1, cy1 + 2, bx + 1, cy1 + 5), fill=C((255, 240, 190)))
    # 红胶凳叠在墙边
    for i in range(4):
        rect(d, (474, 132 - i * 3, 484, 134 - i * 3), (200, 50, 50))
        line(d, (474, 132 - i * 3, 484, 132 - i * 3), (240, 100, 90))
    line(d, (475, 135, 475, 147), (170, 40, 40))
    line(d, (483, 135, 483, 147), (170, 40, 40))
    # 菜单板（剧情「菜单板」(520,120)）
    mx0, my0, mx1, my1 = MENU_BOX
    rect(d, (mx0, my0, mx1, my1), (236, 222, 180), (70, 40, 24))
    rect(d, (mx0 + 1, my0 + 1, mx1 - 1, my1 - 1), None, (120, 80, 40))
    for i, s in enumerate(('叉燒飯', '雲吞麵', '炒蜆')):
        put_text(im, mx1 - 14 - i * 13, my0 + 2, s, 12, (40, 20, 16) if i != 2 else (170, 30, 24), vertical=True)
    line(d, (mx0 - 1, my0 - 3, mx0 + 3, my0), (90, 80, 70))
    line(d, (mx1 + 1, my0 - 3, mx1 - 3, my0), (90, 80, 70))
    # 档口：绿铁皮车 + 炉火 + 挂着的叉烧
    sx0, sy0, sx1, sy1 = STALL_BOX
    rect(d, (sx0, sy0, sx1, sy0 + 3), (50, 120, 80), (24, 60, 40))                # 顶棚
    line(d, (sx0 + 2, sy0 + 4, sx0 + 2, 122), (40, 90, 60))
    line(d, (sx1 - 2, sy0 + 4, sx1 - 2, 122), (40, 90, 60))
    line(d, (sx0 + 6, sy0 + 6, sx1 - 6, sy0 + 6), (150, 140, 120))                 # 挂钩横杆
    for q in range(sx1 - 20, sx1 - 4, 4):
        line(d, (q, sy0 + 6, q, sy0 + 8), (90, 80, 70))
        rect(d, (q - 1, sy0 + 8, q + 1, sy0 + 15), (170, 40, 30))
        px(d, q, sy0 + 9, (240, 120, 80))
    rect(d, (sx0, 122, sx1, sy1), (52, 128, 84), (22, 60, 38))                     # 车身
    line(d, (sx0, 122, sx1, 122), (140, 200, 150))
    for q in range(sx0 + 6, sx1 - 4, 10):
        rect(d, (q, 128, q + 6, 146), (44, 110, 72), (30, 80, 50))
    rect(d, (sx0 + 4, 131, sx0 + 18, 137), (240, 230, 200), (60, 40, 30))          # 牌照
    for q in range(sx0 + 6, sx0 + 17, 3):
        px(d, q, 134, (60, 40, 30))
    rect(d, (sx0 + 13, 116, sx0 + 27, 122), (60, 50, 50))                          # 炉 + 镬
    glow(im, sx0 + 20, 116, 10, 6, (255, 140, 40), 110, rings=3)
    d = ImageDraw.Draw(im)
    d.ellipse((sx0 + 13, 112, sx0 + 27, 118), fill=C((30, 30, 34)))
    line(d, (sx0 + 15, 117, sx0 + 25, 117), (255, 170, 60))
    line(d, (sx0 + 27, 114, sx0 + 32, 112), (90, 70, 50))
    for q in range(3):                                                              # 碗、酱油樽
        d.ellipse((sx0 + 34 + q * 4, 118, sx0 + 37 + q * 4, 121), fill=C((240, 236, 225)))
    rect(d, (sx1 - 8, 114, sx1 - 7, 121), (60, 30, 20))
    rect(d, (sx1 - 5, 115, sx1 - 4, 121), (180, 40, 30))
    for q in range(5):                                                             # 发泡胶箱
        rect(d, (sx1 - 14 + (q % 2) * 7, 141 - (q // 2) * 4, sx1 - 8 + (q % 2) * 7, 144 - (q // 2) * 4), (230, 230, 225), (160, 160, 150))
    # 报摊（剧情「报摊电视」：道具 tv 34×30 立在 (660,152)，x 643–677）
    nx0, ny0, nx1, ny1 = NEWS_BOX
    d.polygon([(nx0 - 2, ny0 + 6), (nx0 + 4, ny0), (nx1 - 4, ny0), (nx1 + 2, ny0 + 6)], fill=C((46, 110, 80)))
    line(d, (nx0 - 2, ny0 + 6, nx1 + 2, ny0 + 6), (24, 60, 40))
    rect(d, (nx0 + 1, ny0 + 7, nx1 - 1, 128), (70, 56, 46))
    for row, yy in enumerate((ny0 + 10, ny0 + 22)):
        line(d, (nx0 + 2, yy, nx1 - 2, yy), (160, 150, 130))
        for q in range(nx0 + 3 + row * 3, nx1 - 7, 8):
            cc = [(220, 60, 70), (70, 120, 220), (240, 220, 80), (240, 240, 240), (230, 120, 180), (90, 190, 130)][int(hash01(q, yy, 3) * 6)]
            rect(d, (q, yy + 1, q + 6, yy + 10), cc, (30, 26, 30))
            rect(d, (q + 1, yy + 2, q + 5, yy + 3), mix(cc, (255, 255, 255), 0.5))
            d.ellipse((q + 2, yy + 4, q + 5, yy + 8), fill=C(mix(cc, (240, 200, 170), 0.6)))
    rect(d, (nx0, 128, nx1, ny1), (52, 120, 84), (22, 60, 38))
    line(d, (nx0, 128, nx1, 128), (140, 200, 150))
    for q in range(nx0 + 2, nx1 - 6, 7):                                           # 一叠叠报纸
        rect(d, (q, 124, q + 5, 128), (220, 216, 206), (120, 116, 110))
        line(d, (q + 1, 125, q + 4, 125), (60, 60, 60))
    rect(d, (nx0 + 4, ny0 - 12, nx0 + 4 + 30, ny0 - 1), (240, 210, 70), (120, 60, 20))
    put_text(im, nx0 + 7, ny0 - 11, '書報', 12, (170, 30, 24))
    # 看相摊：八卦桌布 + 「睇相」布幡 + 灯笼
    fx0, fy0, fx1, fy1 = FORTUNE_BOX
    rect(d, (fx0 + 4, 136, fx0 + 30, 140), (150, 30, 40))
    d.polygon([(fx0 + 4, 140), (fx0 + 30, 140), (fx0 + 32, 150), (fx0 + 2, 150)], fill=C((180, 40, 50)))
    d.ellipse((fx0 + 12, 141, fx0 + 22, 149), outline=C((240, 200, 80)))
    line(d, (fx0 + 17, 141, fx0 + 17, 149), (240, 200, 80))
    for q in range(4):
        rect(d, (fx0 + 8 + q * 5, 133, fx0 + 10 + q * 5, 136), (240, 236, 220))   # 签筒、卦牌
    rect(d, (fx0 + 26, 128, fx0 + 29, 136), (150, 110, 60))
    line(d, (fx1 - 18, fy0, fx1 - 18, 150), (120, 90, 60))
    line(d, (fx1 - 18, fy0, fx1 - 4, fy0), (120, 90, 60))
    rect(d, (fx1 - 16, fy0 + 2, fx1 - 2, fy0 + 30), (236, 232, 220), (150, 140, 120))
    put_text(im, fx1 - 15, fy0 + 3, '睇相', 12, (30, 24, 30), vertical=True)
    glow(im, fx1 - 18, fy0 + 37, 10, 9, (255, 90, 70), 80, rings=3)
    d = ImageDraw.Draw(im)
    d.ellipse((fx1 - 22, fy0 + 32, fx1 - 14, fy0 + 42), fill=C((230, 60, 50)), outline=C((120, 20, 20)))
    line(d, (fx1 - 21, fy0 + 37, fx1 - 15, fy0 + 37), (255, 170, 120))
    # 路灯
    for lx in LAMPS:
        d = _lamp(im, d, lx)
    # 「廟街」路牌、「碼頭」指路牌
    rect(d, (256, 84, 285, 98), (240, 240, 236), (180, 40, 40))
    put_text(im, 258, 85, '廟街', 12, (20, 20, 24))
    hx0, hy0, hx1, hy1 = HARBOR_SIGN
    line(d, (hx1 - 8, hy1, hx1 - 8, 150), (90, 96, 100), width=2)
    rect(d, (hx0, hy0, hx1, hy1), (30, 110, 70), (230, 240, 230))
    put_text(im, hx0 + 2, hy0 + 2, '碼頭', 12, (240, 245, 240))
    d.polygon([(hx1 - 9, hy0 + 4), (hx1 - 3, hy0 + 8), (hx1 - 9, hy0 + 12)], fill=C((240, 245, 240)))
    return im


def steam_frame(t):
    """大牌档炉上的蒸汽（世界坐标整条图，透明底）：24 帧 @8 fps = 3 s 一周，严格闭合。"""
    im = new(WORLD, H)
    f = int(t * STEAM_FPS + 1e-6) % STEAM_N
    for i in range(3):
        u = ((f + i * 8) % STEAM_N) / STEAM_N
        cx = 608 + math.sin(u * math.pi * 2 + i * 2.1) * 3 + u * 5
        cy = 112 - u * 42
        r = 2 + u * 4
        a = int((1 - u) * 110)
        if a > 6:
            blend_ellipse(im, (round(cx - r), round(cy - r * 0.8), round(cx + r), round(cy + r * 0.8)), (230, 226, 236), a)
    return im


def pole_frame(t):
    """理发店的旋转灯柱：红 / 白 / 蓝斜纹往上走，6 帧 @6 fps = 1 s 一周。"""
    im = new(WORLD, H)
    d = ImageDraw.Draw(im)
    f = int(t * POLE_FPS + 1e-6) % POLE_N
    x0, y0, x1, y1 = POLE_BOX
    rect(d, (x0 + 1, y0, x1 - 1, y0 + 2), (200, 200, 210))
    rect(d, (x0 + 1, y1 - 3, x1 - 1, y1 - 1), (200, 200, 210))     # box 右下不含
    cols = [(230, 50, 50), (245, 245, 250), (60, 90, 220)]
    for yy in range(y0 + 3, y1 - 3):
        for xx in range(x0 + 2, x1 - 2):
            c = cols[((yy + (xx - x0) + f) // 2) % 3]
            px(d, xx, yy, c)
    line(d, (x0 + 2, y0 + 3, x0 + 2, y1 - 4), (255, 255, 255))
    return im


# ---------------------------------------------------------------- 启德的飞机（clouds 层）
def plane_img():
    im = new(28, 9)
    d = ImageDraw.Draw(im)
    line(d, (3, 5, 24, 5), (190, 190, 200))
    line(d, (4, 4, 22, 4), (150, 150, 165))
    d.polygon([(21, 4), (26, 1), (27, 1), (25, 5)], fill=C((150, 150, 165)))
    line(d, (10, 6, 16, 8), (120, 120, 135))
    px(d, 2, 5, (255, 250, 200))
    px(d, 16, 8, (255, 60, 60))
    px(d, 13, 3, (80, 255, 120))
    for q in range(6, 20, 2):
        px(d, q, 4, (255, 230, 150))
    return im


# ---------------------------------------------------------------- 导出
@lru_cache(maxsize=1)
def layers_raw():
    return dict(sky=sky_img(), far=far_img(), mid=mid_img(), near=near_img(), street=street_img())


def _tile(im, w):
    out = new(w, im.height)
    for x in range(0, w, im.width):
        out.paste(im, (x, 0))
    return out


def world_still(lit=True):
    """整条 960 的静止画面（镜头 0、视差层按 0 偏移；亮霓虹）——倒影源图和预览用。"""
    R = layers_raw()
    img = _tile(R['sky'], WORLD)
    for k in ('far', 'mid', 'near'):
        img.alpha_composite(_tile(R[k], WORLD))
    img.alpha_composite(R['street'])
    if lit:
        for i, s in enumerate(SIGNS):
            x0, y0, _, _ = sign_box(s)
            paste(img, neon_img(i, True), x0 - SIGN_PAD, y0 - SIGN_PAD)
    return img


def export(ex, BJ):
    R = layers_raw()
    rows = H - 153
    st_img = R['sky'].copy()
    a = np.array(st_img).astype(np.float32)
    yy = np.arange(rows, dtype=np.float32)
    street = np.zeros((rows, W, 3), np.float32)
    street[:] = np.array((22, 18, 34), np.float32)
    street += (yy / rows * 12)[:, None, None]
    street[(yy.astype(int) % 4 == 3)] *= 0.8
    a[153:, :, :3] = street
    st_img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    layers = [dict(type='static', image=ex.img('sky', st_img))]
    layers.append(dict(type='clouds', span=760, clouds=[dict(image=ex.img('plane', plane_img()), x0=520.0, y=15,
                                                              vx=-9.0, k=0.05)]))
    for name, k, vx in (('far', 0.25, -0.5), ('mid', 0.6, 0.0), ('near', 1.0, 0.0)):
        cim, y = BJ.crop_rows(R[name])
        L = dict(type='wrap', image=ex.img(name, cim), period=HK_W, k=k, y=y)
        if vx:
            L['vx'] = vx
        layers.append(L)
    sim, sy = BJ.crop_rows(R['street'])
    layers.append(dict(type='pano', image=ex.img('street', sim), x=0, y=sy, k=1.0))
    layers.append(ex.bake('steam', STEAM_BOX, STEAM_N, STEAM_FPS, steam_frame, screen=False, k=1.0))
    layers.append(ex.bake('barber_pole', POLE_BOX, POLE_N, POLE_FPS, pole_frame, screen=False, k=1.0))
    signs = []
    for i, s in enumerate(SIGNS):
        x0, y0, _, _ = sign_box(s)
        signs.append(dict(image=ex.img('neon%02d' % i, neon_img(i, True)), x=x0 - SIGN_PAD, y=y0 - SIGN_PAD,
                          flick=bool(s[6]), seed=i + 1))
    layers.append(dict(type='neon', signs=signs, k=1.0))
    # 倒影源图：整条 960（近景 + 街面 + 亮霓虹）减 30；period 960 = 世界坐标（镜头 0–640 时列号不越界）
    comp = world_still(True)
    ca = np.array(comp).astype(np.float32)
    ca[..., :3] = np.maximum(ca[..., :3] - 30, 0)
    ca[..., 3] = 255
    refl = Image.fromarray(ca.astype(np.uint8), 'RGBA').crop((0, 96, WORLD, 153))
    layers.append(dict(type='reflect', image=ex.img('reflect_src', refl), y=153, n=rows, a0=0.62, a1=0.27,
                       period=WORLD, k=1.0, blend='lighter', srcY=96, amp=1.8, rk=1.3, freq=6.0, wet=0.8))
    road = new(40, 1)
    ImageDraw.Draw(road).line((0, 0, 16, 0), fill=C((170, 150, 60)))
    layers.append(dict(type='wrap', image=ex.img('road', BJ.tile_to(road, 40, 40 + W)), period=40, k=1.0, y=170))
    shop = None
    for x, w, k in shopfronts():
        if x + 6 <= 230 <= x + w - 6:
            shop = [x + 6, 112, x + w - 6, 146]
    anchors = dict(curb=152, shopwindow=shop, alleys=[list(g) for g in GAPS],
                   alleys2=[[g0 + HK_W, g1 + HK_W] for g0, g1 in GAPS if g0 + HK_W < WORLD],
                   neon=[[sign_box(s)[0] + (sign_box(s)[2] - sign_box(s)[0]) // 2,
                          sign_box(s)[1] + (sign_box(s)[3] - sign_box(s)[1]) // 2] for s in SIGNS],
                   period=HK_W, walk_x=[0, WORLD], pawn_sign=list(sign_box(SIGNS[6])), menu=list(MENU_BOX),
                   stall=list(STALL_BOX), canopy=list(CANOPY), newsstand=list(NEWS_BOX), fortune=list(FORTUNE_BOX),
                   kite_sign=list(sign_box(SIGNS[14])), lamps=list(LAMPS), harbor_sign=list(HARBOR_SIGN))
    st = ex.stage(WORLD, 154, (150, 176), layers, anchors=anchors)
    if ex.check_on:
        ex.checked('香港 天空底图不透明', int((np.array(st_img)[..., 3] != 255).sum()))
        # 导出层 vs 直接用整幅原图拼（验证裁行 / 世界坐标 / 帧条位置），不比 clouds / reflect（公式同原片）
        only = ('static', 'wrap', 'pano', 'strip', 'neon')
        for camX in (0, 230, 400, 520, 640):
            for t in (0.0, 1.25):
                want = Image.new('RGBA', (W, H), (0, 0, 0, 255))
                want.alpha_composite(st_img)
                for name, k, vx in (('far', 0.25, -0.5), ('mid', 0.6, 0.0), ('near', 1.0, 0.0)):
                    o = int(math.floor(camX * k + t * vx)) % HK_W
                    want.alpha_composite(_tile(R[name], HK_W * 2).crop((o, 0, o + W, H)))
                want.alpha_composite(R['street'].crop((camX, 0, camX + W, H)))
                for fn in (steam_frame, pole_frame):
                    want.alpha_composite(fn(t).crop((camX, 0, camX + W, H)))
                for i, s in enumerate(SIGNS):
                    x0, y0, _, _ = sign_box(s)
                    paste(want, neon_img(i, True), x0 - SIGN_PAD - camX, y0 - SIGN_PAD)
                rd = ImageDraw.Draw(want)
                for x in range(-(camX % 40), W, 40):
                    rd.line((x, 170, x + 16, 170), fill=C((170, 150, 60)))
                got = BJ.ref_render(st, ex.images, camX, t, only=only)
                ex.checked('香港 camX=%d t=%.2f 导出 vs 整幅直接拼' % (camX, t), BJ.ndiff(got, want, box=(0, 0, W, 153))
                           + BJ.ndiff(got, want, box=(0, 170, W, 171)))
        # 剧情坐标对得上（ch01.js 不改）：每条不满足记 1
        bad = 0
        px0, py0, px1, py1 = sign_box(SIGNS[6])
        bad += not (px0 <= 400 <= px1 and py0 <= 60 <= py1)                      # 霓虹招牌 (400,60) = 當舖
        bad += not (shop == [205, 112, 230, 146])                               # 橱窗 anchors 没变
        bad += not (MENU_BOX[0] <= 520 <= MENU_BOX[2] and MENU_BOX[1] <= 120 <= MENU_BOX[3])
        bad += not (NEWS_BOX[0] <= 643 and 677 <= NEWS_BOX[2])                  # tv 道具 x 643–677 落在报摊前
        kx0, ky0, kx1, ky1 = sign_box(SIGNS[14])
        bad += not (kx0 <= 856 and 864 <= kx1 and 62 <= ky0 <= 70)             # kite 道具 y 62–70 挂在招牌上沿
        bad += not (CANOPY[0] <= 476 and 572 <= CANOPY[2])                      # 两张桌（476–572）在棚下
        bad += not (STALL_BOX[0] <= 590 and 626 <= STALL_BOX[2])                 # 老板 590 / 626 在档口前
        bad += not (FORTUNE_BOX[0] <= 760 <= FORTUNE_BOX[2])
        ex.checked('香港 剧情调查点 / 道具位置和画面对得上（不满足的条数）', int(bad))
    return st


# ---------------------------------------------------------------- 单独预览
def _prop(name):
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets', 'props', name + '.png')
    return Image.open(p).convert('RGBA') if os.path.exists(p) else None


def mock_props(img, camX=0):
    """预览用：把剧情放的道具（桌子、电视、风筝）按剧情坐标贴上去，看对不对位。"""
    for name, x, y, z, fw in (('hk_table', 500, 164, 0, 48), ('hk_table', 548, 164, 0, 48), ('tv', 660, 152, 0, 34),
                              ('kite', 860, 150, 80, 8)):
        im = _prop(name)
        if im is None:
            continue
        fr = im.crop((0, 0, fw, im.height))
        paste(img, fr, x - fw // 2 - camX, y - z - fr.height)
    return img


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_preview', 'bg_hk')
    os.makedirs(out, exist_ok=True)
    full = world_still(True)
    full.convert('RGB').save(os.path.join(out, 'hongkong_night_after_world.png'))
    mock_props(full.copy()).convert('RGB').resize((WORLD * 2, H * 2), Image.NEAREST).save(
        os.path.join(out, 'hongkong_night_after_world_props_x2.png'))
    print('ok', out)
