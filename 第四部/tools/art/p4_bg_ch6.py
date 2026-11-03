# 第四部第6章（幽灵小路 / 丰收与纽扣）的背景：6 张，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   ghost_alley      幽灵小路：两栋楼中间多出来的窄巷（640），第11章和终章还要用；“不能回头”的暗角、影子手是开关层
#   morioh_blocks    杜王町 9 块街区的俯视图（320），捡硬币小游戏的底图（morioh_map 的放大版）
#   budogaoka_bank   葡萄丘银行大厅（320）：兑彩票
#   rooftops         第 9 战：左一屏大楼外墙（爬墙），右一屏楼顶，两栋楼之间架着两根水管（640）；水管断开是开关层
#   st_gentleman     三明治店门口 + 公园长椅（480）：拿错纸袋
#   middle_school    重清的初中：操场一角、体育仓库、走廊（640）：第 10 战
#   用法：python3 第四部/tools/art/p4_bg_ch6.py [key ...]   元数据写 第四部/assets/_meta/bg_ch6.json（build_p4.py 会合并进 bg）
#         预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import preview, save_layers, sky_far  # noqa: E402

PACK = 'ch6'
META = os.path.join(LIB.META, 'bg_ch6.json')

# 3×5 的大写字母（招牌用；数字用 p4_bglib.DIG）
LET = {'A': ['010', '101', '111', '101', '101'], 'B': ['110', '101', '110', '101', '110'], 'C': ['011', '100', '100', '100', '011'],
       'D': ['110', '101', '101', '101', '110'], 'E': ['111', '100', '110', '100', '111'], 'F': ['111', '100', '110', '100', '100'],
       'G': ['011', '100', '101', '101', '011'], 'H': ['101', '101', '111', '101', '101'], 'I': ['111', '010', '010', '010', '111'],
       'K': ['101', '101', '110', '101', '101'], 'L': ['100', '100', '100', '100', '111'], 'M': ['10001', '11011', '10101', '10001', '10001'],
       'N': ['1001', '1101', '1011', '1001', '1001'], 'O': ['010', '101', '101', '101', '010'], 'P': ['110', '101', '110', '100', '100'],
       'R': ['110', '101', '110', '101', '101'], 'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'],
       'U': ['101', '101', '101', '101', '111'], 'W': ['10001', '10001', '10101', '11011', '10001'], 'Y': ['101', '101', '010', '010', '010'],
       '-': ['000', '000', '111', '000', '000'], ' ': ['00'] * 5, '.': ['0', '0', '0', '0', '1'], "'": ['1', '1', '0', '0', '0']}


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


def kanji(im, x, y, text, col, size=12):
    """文泉驿点阵正黑 12 px（招牌用）。返回 (宽, 高)"""
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    im.paste(C(col), (int(x), int(y)), m)
    return m.width, m.height


def kanji_size(text, size=12):
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    return m.width, m.height


def poly(d, pts, col):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=C(col))


def glow_from_field(f, col, levels=6):
    """强度场（0..1）→ lighter 叠加用的光晕图，按 4×4 Bayer 抖动量化"""
    h, w = f.shape
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    fq = np.clip(np.floor(f * levels + bay) / levels, 0, 1)
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * np.array(c3(col), float), 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def shade_x(im, xs, ks, box=None, cool=(1.0, 1.0, 1.0)):
    """按 x 插值的明暗系数（ks 在 xs 处的值）整列乘上去；cool 再按暗的程度往冷色偏"""
    a = np.array(im).astype(float)
    h, w = a.shape[:2]
    k = np.interp(np.arange(w), xs, ks)
    x0, y0, x1, y1 = box or (0, 0, w, h)
    sub = a[y0:y1, x0:x1, :3]
    kk = k[x0:x1][None, :, None]
    dark = 1 - kk
    sub *= kk
    sub *= (1 - dark * (1 - np.array(cool)))
    a[y0:y1, x0:x1, :3] = sub
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def bayer_mask(field):
    """0..1 场 → 0/1 抖动蒙版"""
    h, w = field.shape
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    return field > bay


def paving(im, x0, x1, y0, y1, cols, seed=0, crack='#5a5660'):
    """旧水泥地面：一块块方砖（越往下越宽）、裂缝、苔点"""
    d = ImageDraw.Draw(im)
    rect(d, (x0, y0, x1, y1), cols[0])
    rng = np.random.RandomState(seed)
    y, h = y0, 4.0
    row = 0
    while y < y1:
        yb = min(y1, int(round(y + h)))
        line(d, (x0, yb, x1, yb), cols[1])
        step = int(14 + h * 4)
        off = (row * 11) % step
        for x in range(x0 - off, x1, step):
            line(d, (x, int(y), x - int(h * .4), yb), cols[1])
            if rng.rand() < .35:
                rect(d, (x + 2, int(y) + 1, x + step - 3, yb - 1), cols[2])
        y += h + 1
        h *= 1.32
        row += 1
    for _ in range(int((x1 - x0) / 40)):
        x, yy = rng.randint(x0, x1), rng.randint(y0 + 4, y1 - 2)
        for k in range(rng.randint(4, 10)):
            x += rng.choice([-1, 0, 1, 1])
            yy += rng.choice([0, 1]) if k % 2 else 0
            px(d, x, yy, crack)
    return noise_specks(im, (x0, y0, x1, y1), [cols[1], cols[3]], int((x1 - x0) * (y1 - y0) / 40), seed + 3)


def weeds(im, x0, x1, ground, seed=0, cols=('#4a6a3a', '#6a8a4a', '#8aa860'), n=None):
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(seed)
    for _ in range(n or int((x1 - x0) / 4)):
        x = rng.randint(x0, x1)
        h = rng.randint(2, 7)
        c = cols[rng.randint(len(cols))]
        line(d, (x, ground, x + rng.choice([-1, 0, 1]), ground - h), c)
        if h > 4:
            px(d, x + rng.choice([-1, 1]), ground - h + 2, c)
    return im


def drainpipe(im, x, y0, y1, col='#8a8a84', hi='#b0b0a8', lo='#5e5e5a'):
    d = ImageDraw.Draw(im)
    rect(d, (x, y0, x + 3, y1), col)
    line(d, (x + 1, y0, x + 1, y1), hi)
    line(d, (x + 3, y0, x + 3, y1), lo)
    for y in range(y0 + 10, y1 - 4, 22):
        rect(d, (x - 1, y, x + 4, y + 1), lo)
    rect(d, (x - 1, y1 - 3, x + 6, y1), col)
    return im


def ac_unit(im, x, y, w=24, h=16, body='#d8d8d0', dark='#9a9a94'):
    """空调外机（正面）：格栅 + 风扇圆"""
    d = ImageDraw.Draw(im)
    rect(d, (x, y, x + w, y + h), body)
    line(d, (x, y, x + w, y), mix(body, '#ffffff', .4))
    line(d, (x + w, y, x + w, y + h), dark)
    line(d, (x, y + h, x + w, y + h), dark)
    r = h // 2 - 2
    cx, cy = x + w // 2 - 3, y + h // 2
    ellipse(d, (cx - r, cy - r, cx + r, cy + r), dark)
    ellipse(d, (cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1), mix(dark, '#000000', .25))
    for k in range(-r + 1, r, 2):
        line(d, (cx - r + 1, cy + k, cx + r - 1, cy + k), dark)
    for k in range(3):
        line(d, (x + w - 6, y + 3 + k * 3, x + w - 2, y + 3 + k * 3), dark)
    return im


def chainlink(im, x0, x1, y0, y1, col='#7a8a82', post='#5a6a64', step=4):
    """铁丝网：斜格子 + 立柱（格子之间留空，能看见后面）"""
    net = Image.new('RGBA', im.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(net)
    for x in range(x0 - (y1 - y0), x1, step):
        line(nd, (x, y1, x + (y1 - y0), y0), col)
        line(nd, (x, y0, x + (y1 - y0), y1), col)
    im2 = im.copy()
    im2.alpha_composite(net.crop((x0, 0, x1, im.height)), (x0, 0))
    d = ImageDraw.Draw(im2)
    for x in range(x0, x1 + 1, 40):
        rect(d, (x, y0 - 2, x + 1, y1), post)
    rect(d, (x0, y0 - 2, x1, y0 - 1), post)
    rect(d, (x0, y1 - 1, x1, y1), post)
    return im2


def clip_band(dst, src, x0, x1):
    """把 src 的 [x0, x1) 列贴回 dst（用来把超出范围的斜线裁掉）"""
    dst.paste(src.crop((x0, 0, x1, src.height)), (x0, 0))
    return dst


# ============================================================ 幽灵小路 ghost_alley（640 宽，白天但巷子里阴）
#   左：从大街拐进来的巷口（亮）→ 楼 A 的背面（铁栅小窗、排水管、空调外机、电表、铁后门）→ 老木板墙和老房子的二楼（雨户关着）
#   → 水泥砌块墙和后面的楼（盆栽、自行车）→ 楼 C 的生锈铁楼梯 → 右边出口（白光）。
#   越往中间越暗、越冷；地上一层薄雾慢慢飘。开关层：dark（0..1 画面四边压暗，“不能回头”的诱惑），hands（左边缘伸进来的影子手）
GA = dict(sky=('#c8c4d8', '#d4d0e0', '#e2dee8'), sil='#9a94ac', sil2='#aaa4ba')


def ghost_alley():
    W, G = 640, 140
    # 远景：一线灰紫的天 + 远处屋顶的剪影
    FW = (W - 320) // 2 + 320
    far = new(FW, 180, GA['sky'][-1])
    far = grad(far, (0, 0, FW, 70), GA['sky'])
    d = ImageDraw.Draw(far)
    rng = np.random.RandomState(61)
    x = 0
    while x < FW:
        w = rng.randint(18, 46)
        top = rng.randint(22, 44)
        rect(d, (x, top, x + w, 180), GA['sil'] if rng.rand() < .6 else GA['sil2'])
        if rng.rand() < .4:
            rect(d, (x + 4, top - 6, x + 6, top), GA['sil'])
        x += w
    near = new(W, 180)
    d = ImageDraw.Draw(near)
    # ---- 地面：巷口一段是大街的人行道（亮），往里是旧水泥地，中间一道排水沟盖板
    near = paving(near, 0, W, G, 180, ('#8a8692', '#76727e', '#94909c', '#a6a2ac'), seed=7)
    d = ImageDraw.Draw(near)
    for x in range(64, 584, 12):                                   # 排水沟的格栅盖（沿墙根）
        rect(d, (x, G + 1, x + 10, G + 4), '#5a5662')
        for k in range(1, 10, 2):
            line(d, (x + k, G + 1, x + k, G + 4), '#3e3a46')
    line(d, (64, G, 584, G), '#4e4a56')
    near = sidewalk(near, 0, 62, G - 2, 180, ('#d8d2c4', '#c4beb0', '#e8e2d6', '#b4ae9e'))
    near = sidewalk(near, 586, W, G - 2, 180, ('#d8d2c4', '#c4beb0', '#e8e2d6', '#b4ae9e'))
    d = ImageDraw.Draw(near)
    # ---- 巷口（0–64）：大街对面的店面一角 + 电线杆
    rect(d, (0, 30, 40, G - 2), '#e6dccb')
    for yy in range(32, G - 2, 4):
        line(d, (0, yy, 40, yy), '#d8ccb8')
    window(d, (6, 52, 30, 72), glass=('#8eb8d2', '#c0dcea'), curtain='#e8b4a8')
    rect(d, (0, 92, 42, 98), '#c84a3a')                            # 店的遮雨棚
    for x in range(0, 42, 6):
        rect(d, (x, 92, x + 2, 98), '#f0e8dc')
    rect(d, (4, 100, 34, G - 2), '#b8c8d0')
    line(d, (19, 100, 19, G - 2), '#8a9aa4')
    near = pole(near, 48, G + 6, 140)
    d = ImageDraw.Draw(near)
    # ---- 楼 A 背面（64–204）：抹灰墙
    A0, A1, Atop = 64, 204, 18
    rect(d, (A0, Atop, A1, G), '#a29a90')
    near = noise_specks(near, (A0, Atop, A1, G), ['#968e84', '#aca49a'], 900, 3)
    d = ImageDraw.Draw(near)
    rect(d, (A0, Atop - 3, A1, Atop), '#8a827a')
    rect(d, (A0, Atop, A0 + 3, G), '#c4bcb0')                       # 楼角（受光）
    for y in (56, 96):                                             # 楼层线
        line(d, (A0, y, A1, y), '#8e867c')
    for wx, wy in ((80, 30), (140, 30), (80, 68), (176, 68)):      # 铁栅小窗
        rect(d, (wx, wy, wx + 16, wy + 14), '#4a4650')
        rect(d, (wx + 1, wy + 1, wx + 15, wy + 6), '#5e5a68')
        for k in range(2, 16, 3):
            line(d, (wx + k, wy, wx + k, wy + 14), '#7a7480')
        line(d, (wx - 1, wy + 15, wx + 17, wy + 15), '#c4bcb0')
    near = drainpipe(near, 122, Atop - 2, G)
    near = ac_unit(near, 150, 104, 26, 18, body='#c8c8c0', dark='#8a8a84')
    d = ImageDraw.Draw(near)
    rect(d, (150, 122, 151, 128), '#6a6a66')
    rect(d, (174, 122, 175, 128), '#6a6a66')
    rect(d, (90, 104, 104, 118), '#c8c4b8')                         # 电表箱
    rect(d, (92, 106, 102, 112), '#e8e4d8')
    ellipse(d, (95, 107, 99, 111), '#4a4650')
    line(d, (97, 118, 97, G - 6), '#3a3a40')
    rect(d, (182, 96, 202, G), '#6a6e74')                           # 铁后门
    rect(d, (184, 98, 200, G), '#7e8288')
    line(d, (192, 98, 192, G), '#5a5e64')
    px(d, 190, 120, '#c8c8c0')
    rect(d, (180, 94, 204, 95), '#8a8e94')
    # ---- 老木板墙 + 老房子（204–332）
    B0, B1 = 204, 332
    tiled_roof(near, B0 + 6, B1 - 6, 30, 44, ('#4a4a54', '#383842', '#5e5e6a', '#26262e'), overhang=6)
    d = ImageDraw.Draw(near)
    rect(d, (B0 + 8, 45, B1 - 8, 72), '#c8b89a')
    rect(d, (B0 + 30, 50, B1 - 30, 70), '#6a4e3a')                   # 二楼的雨户（关着）
    for x in range(B0 + 30, B1 - 30, 5):
        line(d, (x, 50, x, 70), '#5a4030')
    line(d, (B0 + 30, 50, B1 - 30, 50), '#8a6a50')
    rect(d, (B0, 72, B1, G), '#3e3430')                             # 黑木板墙
    for x in range(B0, B1, 6):
        line(d, (x, 72, x, G), '#2e2624')
        line(d, (x + 1, 72, x + 1, G), '#4a3e38')
    rect(d, (B0 - 1, 70, B1 + 1, 73), '#2a2422')
    line(d, (B0 - 1, 70, B1 + 1, 70), '#5a4a42')
    for y in (90, 124):
        rect(d, (B0, y, B1, y + 2), '#4e423c')
    near = weeds(near, B0, B1, G, seed=11, n=40)
    d = ImageDraw.Draw(near)
    # 靠墙的旧自行车
    bx = 262
    for cx in (bx, bx + 22):
        ellipse(d, (cx - 7, G - 13, cx + 7, G + 1), '#2a2a30')
        ellipse(d, (cx - 6, G - 12, cx + 6, G), '#3e3430')
        px(d, cx, G - 6, '#9a9a9a')
    line(d, (bx, G - 6, bx + 10, G - 16), '#8a3a34')
    line(d, (bx + 10, G - 16, bx + 22, G - 6), '#8a3a34')
    line(d, (bx + 10, G - 16, bx + 19, G - 16), '#8a3a34')
    line(d, (bx + 4, G - 18, bx + 12, G - 18), '#2a2a30')
    line(d, (bx + 19, G - 16, bx + 21, G - 22), '#9a9a9a')
    line(d, (bx + 18, G - 22, bx + 24, G - 22), '#2a2a30')
    # 一小块木牌（字已经褪了）
    rect(d, (226, 98, 244, 112), '#8a7a62')
    rect(d, (227, 99, 243, 111), '#a8987a')
    for k in range(3):
        line(d, (229, 102 + k * 3, 241 - k * 2, 102 + k * 3), '#7a6a52')
    # ---- 水泥砌块墙 + 后面的楼（332–480）
    C0, C1 = 332, 480
    rect(d, (C0, 14, C1, 96), '#8e8a98')
    near = noise_specks(near, (C0, 14, C1, 96), ['#84808e', '#9894a2'], 500, 5)
    d = ImageDraw.Draw(near)
    for wx in range(C0 + 10, C1 - 16, 30):
        for wy in (22, 52):
            rect(d, (wx, wy, wx + 18, wy + 20), '#5a5668')
            rect(d, (wx + 1, wy + 1, wx + 17, wy + 19), '#6e6a80')
            line(d, (wx + 9, wy, wx + 9, wy + 20), '#5a5668')
            line(d, (wx + 2, wy + 2, wx + 6, wy + 2), '#8a86a0')
            line(d, (wx - 1, wy + 21, wx + 19, wy + 21), '#a6a2b0')
    near = block_wall(near, C0, C1, 96, G, cols=('#a8a4a6', '#8e8a8e', '#787478', '#c0bcbc'))
    d = ImageDraw.Draw(near)
    # 墙根一排盆栽 + 水桶
    for i, x in enumerate(range(C0 + 8, C1 - 10, 17)):
        if i == 4:
            rect(d, (x, G - 12, x + 10, G), '#5a7a9a')              # 蓝色塑料桶
            rect(d, (x - 1, G - 13, x + 11, G - 12), '#7a9aba')
            continue
        rect(d, (x + 1, G - 8, x + 9, G), '#a85a3a')
        rect(d, (x, G - 9, x + 10, G - 8), '#c06a46')
        rr = 4 + (i * 7) % 4
        ellipse(d, (x + 5 - rr, G - 9 - rr * 2, x + 5 + rr, G - 9), ['#4a6a3a', '#5a7a44', '#3e5e34'][i % 3])
        px(d, x + 4, G - 9 - rr, '#8aa860')
        if i % 3 == 1:                                             # 紫阳花
            for k in range(3):
                ellipse(d, (x + 1 + k * 3, G - 15 - rr - k % 2 * 2, x + 4 + k * 3, G - 12 - rr - k % 2 * 2), '#8a82c8')
    # 晾衣竿（楼上窗外）
    line(d, (C0 + 40, 46, C0 + 120, 46), '#b8b8b0')
    for x, c in ((C0 + 52, '#d8d4e0'), (C0 + 70, '#b8c8d8'), (C0 + 98, '#e0d0c0')):
        rect(d, (x, 47, x + 10, 60), c)
        line(d, (x, 47, x + 10, 47), '#8a8a8a')
    # ---- 楼 C（480–586）：旧砖墙 + 生锈的铁楼梯
    D0, D1 = 480, 586
    rect(d, (D0, 24, D1, G), '#8a6e62')
    for i, y in enumerate(range(24, G, 4)):
        line(d, (D0, y, D1, y), '#76594e')
        for x in range(D0 + (0 if i % 2 else 6), D1, 12):
            line(d, (x, y, x, y + 3), '#76594e')
    near = noise_specks(near, (D0, 24, D1, G), ['#9a7a6c', '#6e5248'], 600, 9)
    d = ImageDraw.Draw(near)
    rect(d, (D0, 21, D1, 24), '#5e4a42')
    rect(d, (500, 34, 516, 52), '#3e3440')                          # 楼梯口的门
    rect(d, (548, 34, 572, 52), '#4a4250')
    line(d, (560, 34, 560, 52), '#3a3240')
    # 铁楼梯：一跑斜梯 + 中间平台
    rust, rust2 = '#6a4a3a', '#8a5e44'
    rect(d, (496, 54, 576, 56), rust)
    line(d, (496, 53, 576, 53), rust2)
    for x in range(498, 576, 8):
        line(d, (x, 44, x, 53), rust)
    line(d, (496, 44, 576, 44), rust2)
    for i in range(14):
        x0, y0 = 520 + i * 4, 56 + i * 6
        rect(d, (x0, y0, x0 + 6, y0 + 1), rust2)
    line(d, (518, 56, 576, G - 2), rust)
    line(d, (518, 46, 576, G - 12), rust2)
    for x in range(522, 576, 9):
        yy = 46 + (x - 518) * (G - 58) / 58
        line(d, (x, yy, x, yy + 10), rust)
    rect(d, (577, 56, 579, G), rust)
    rect(d, (498, 56, 500, G), rust)
    # 一盏没开的灯
    rect(d, (528, 28, 536, 31), '#5a5a5e')
    rect(d, (530, 31, 534, 34), '#c8c8c0')
    near = weeds(near, D0, D1, G, seed=13, n=30)
    d = ImageDraw.Draw(near)
    # ---- 出口（586–640）：对面亮亮的大街
    rect(d, (586, 26, W, G - 2), '#f0ecdc')
    for yy in range(28, G - 2, 4):
        line(d, (586, yy, W, yy), '#e2dccb')
    window(d, (600, 44, 626, 66), glass=('#a8cce0', '#d4ecf4'))
    rect(d, (596, 92, W, 98), '#3a7a5a')
    for x in range(596, W, 6):
        rect(d, (x, 92, x + 2, 98), '#f0e8dc')
    rect(d, (604, 100, 632, G - 2), '#c8d8e0')
    # ---- 头顶横过巷子的电线
    near = wires(near, [(48, 22), (330, 30), (640, 18)], sag=10, col='#3a3644')
    # ---- 光：巷口和出口亮，往中间越来越暗、越冷
    xs = [0, 60, 110, 250, 380, 470, 560, 600, 640]
    ks = [1.0, .98, .80, .70, .62, .66, .78, .98, 1.0]
    near = shade_x(near, xs, ks, cool=(.92, .96, 1.06))
    # 墙根的阴影带（巷子窄，地面靠墙一半在影子里）
    a = np.array(near).astype(float)
    for y in range(G, G + 12):
        k = .78 + .22 * (y - G) / 12
        a[y, 64:586, :3] *= k
    near = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    # 巷口 / 出口的光晕
    yy, xx = np.mgrid[0:180, 0:W]
    f = np.clip(1 - np.abs(xx - 30) / 70, 0, 1) * np.clip((yy - 40) / 120, 0, 1) * .5
    f += np.clip(1 - np.abs(xx - 616) / 70, 0, 1) * np.clip((yy - 30) / 120, 0, 1) * .7
    glow = glow_from_field(np.clip(f, 0, 1), '#5a5040', levels=5)
    # 雾：地面上方一条，横向循环（320 宽）
    mist = new(320, 40)
    yy, xx = np.mgrid[0:40, 0:320]
    fm = (.5 + .25 * np.sin(xx / 320 * 2 * np.pi * 3 + 1) + .2 * np.sin(xx / 320 * 2 * np.pi * 7)) * np.sin(np.pi * yy / 40) ** 2.5 * .32
    mk = bayer_mask(fm)
    ma = np.zeros((40, 320, 4), np.uint8)
    ma[mk] = (*c3('#c8c4dc'), 255)
    mist = Image.fromarray(ma, 'RGBA')
    # 开关层 dark：画面四边压暗（屏幕坐标，三档）
    vigs = {'vig0': new(1, 1)}
    yy, xx = np.mgrid[0:180, 0:320]
    e = np.minimum(np.minimum(xx, 319 - xx) / 160, np.minimum(yy, 179 - yy) / 90)
    for i, lvl in enumerate((.25, .45, .7), 1):
        fv = np.clip((lvl - e) / lvl, 0, 1) ** 1.4
        m = bayer_mask(fv * .95)
        va = np.zeros((180, 320, 4), np.uint8)
        va[m] = (*c3('#120e1c'), 255)
        vigs[f'vig{i}'] = Image.fromarray(va, 'RGBA')
    # 开关层 hands：从画面左边伸进来的影子手（4 帧，抖动的半透明暗紫）
    HW, n = 120, 4
    hands = new(HW * n, 180)
    for fr in range(n):
        hm = Image.new('L', (HW, 180), 0)
        hd = ImageDraw.Draw(hm)
        reach = 40 + fr * 16
        for j, (hy, ang) in enumerate(((60, -.25), (92, .05), (126, .2), (150, -.1))):
            L = reach * (1 - .12 * ((j + fr) % 3))
            ex, ey = L, hy + L * ang
            hd.line((0, hy, ex, ey), fill=255, width=7)
            hd.ellipse((ex - 7, ey - 6, ex + 7, ey + 6), fill=255)
            for k in range(4):                                     # 手指（一张一合）
                spread = .5 + .5 * math.sin(fr * math.pi / 2 + j)
                fa = ang + (-.6 + k * .4) * (.6 + spread * .6)
                hd.line((ex, ey, ex + 13 * math.cos(fa), ey + 13 * math.sin(fa)), fill=255, width=3)
        hm = hm.filter(ImageFilter.BoxBlur(2))
        fh = np.array(hm).astype(float) / 255
        xg = np.arange(HW)[None, :]
        fh *= np.clip(1.15 - xg / HW, 0, 1)
        m = bayer_mask(np.clip(fh * 1.1, 0, 1))
        ha = np.zeros((180, HW, 4), np.uint8)
        ha[m] = (*c3('#1a1228'), 255)
        hands.paste(Image.fromarray(ha, 'RGBA'), (fr * HW, 0))
    layers = dict(far=far, near=near, glow=glow, mist=mist, hands=hands, **vigs)
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(entrance=[30, 150], back_door=[192, 146], ac=[163, 112], bicycle=[273, 146], reimi=[300, 152],
                             arnold=[318, 156], plants=[400, 146], stairs=[540, 146], exit=[616, 150], exit_x=600, walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/ghost_alley/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/ghost_alley/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'glow', 'image': 'bg/ghost_alley/glow', 'k': 1, 'x': 0, 'y': 0, 'flicker': 0.05},
                        {'type': 'wrap', 'image': 'bg/ghost_alley/mist', 'k': 1.15, 'vx': -6, 'y': 128}],
                fg=[{'type': 'pick', 'images': ['bg/ghost_alley/vig0', 'bg/ghost_alley/vig1', 'bg/ghost_alley/vig2',
                                                 'bg/ghost_alley/vig3'], 'key': 'dark', 'k': 0, 'x': 0, 'y': 0},
                    {'type': 'strip', 'image': 'bg/ghost_alley/hands', 'n': 4, 'fps': 5, 'w': HW, 'h': 180, 'x': 0, 'y': 0,
                     'screen': True, 'key': 'hands'}])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    preview('ghost_alley', {'all': pv}, ['all'], W)
    return save_layers('ghost_alley', layers, meta)


# ============================================================ 杜王町 9 块街区 morioh_blocks（320×180，俯视，捡硬币）
#   morioh_map 同一种旧纸，放大成 3×3 街区。左上角起按行编号 b0..b8；派出所（b4）、河边的狗（b5）、工地下水道口（b6）是“小心”的街区。
BLOCKS = [('住宅区', 0), ('商店街', 0), ('公园', 0), ('车站前', 0), ('派出所', 1), ('河边', 1), ('工地', 1), ('便利店', 0), ('银行', 0)]


def morioh_blocks():
    W, H = 320, 180
    paper = '#efe4c8'
    im = new(W, H, paper)
    d = ImageDraw.Draw(im)
    xs = [(16, 106), (115, 205), (214, 304)]
    ys = [(28, 74), (82, 128), (136, 172)]
    # 路（街区之间）
    rect(d, (8, 20, W - 9, H - 4), '#fffaf0')
    for (x0, x1) in xs[:-1]:
        for y in range(22, H - 6, 6):
            px(d, x1 + 4, y, '#d8c8a0')
            px(d, x1 + 4, y + 1, '#d8c8a0')
    for (y0, y1) in ys[:-1]:
        for x in range(10, W - 10, 6):
            px(d, x, y1 + 4, '#d8c8a0')
            px(d, x + 1, y1 + 4, '#d8c8a0')
    rects = []
    rng = np.random.RandomState(23)
    for i, (name, danger) in enumerate(BLOCKS):
        x0, x1 = xs[i % 3]
        y0, y1 = ys[i // 3]
        rects.append([x0, y0, x1, y1, name, danger])
        rect(d, (x0, y0, x1, y1), '#e2d4b4')
        rect(d, (x0, y0, x1, y1), None, '#c8b890')
    # b0 住宅区：一排排小屋顶 + 院子
    x0, y0, x1, y1 = rects[0][:4]
    for r in range(3):
        for c in range(6):
            hx, hy = x0 + 4 + c * 14, y0 + 16 + r * 10
            if hy + 8 > y1:
                continue
            rect(d, (hx - 1, hy - 1, hx + 11, hy + 8), '#b8cc96')
            roof = ['#5a6a8a', '#8a4e44', '#4e7a6a'][(r + c) % 3]
            rect(d, (hx, hy, hx + 9, hy + 6), roof)
            line(d, (hx, hy + 3, hx + 9, hy + 3), mix(roof, '#000000', .3))
            line(d, (hx, hy, hx + 9, hy), mix(roof, '#ffffff', .25))
    # b1 商店街：中间一条步行街，两边铺面 + 条纹遮阳棚
    x0, y0, x1, y1 = rects[1][:4]
    rect(d, (x0 + 2, y0 + 24, x1 - 2, y0 + 30), '#f4ead6')
    for side, yy in ((0, y0 + 14), (1, y0 + 32)):
        for c in range(7):
            sx = x0 + 4 + c * 12
            rect(d, (sx, yy, sx + 10, yy + 9), ['#e6dccb', '#dcd0bc', '#ece2d0'][c % 3])
            ac = ['#c84a3a', '#3a7a5a', '#e0a030', '#3a6ab0'][c % 4]
            ay = yy + 9 if side == 0 else yy - 2
            for k in range(0, 10, 2):
                rect(d, (sx + k, ay, sx + k, ay + 1), ac)
    # b2 公园：草地、树、池塘、沙坑
    x0, y0, x1, y1 = rects[2][:4]
    rect(d, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), '#b8d090')
    ellipse(d, (x0 + 40, y0 + 18, x0 + 72, y0 + 38), '#7ab0d8')
    ellipse(d, (x0 + 44, y0 + 20, x0 + 60, y0 + 26), '#a8cce8')
    rect(d, (x0 + 10, y0 + 30, x0 + 26, y0 + 40), '#f0e0b0')
    for tx, ty in ((x0 + 10, y0 + 18), (x0 + 22, y0 + 20), (x0 + 80, y0 + 18), (x0 + 82, y0 + 36), (x0 + 30, y0 + 42), (x0 + 70, y0 + 42)):
        ellipse(d, (tx - 4, ty - 4, tx + 4, ty + 3), '#6a9a5a')
        px(d, tx - 1, ty - 2, '#a8cc88')
    line(d, (x0 + 2, y0 + 28, x1 - 2, y0 + 30), '#f4ead6')
    # b3 车站前：铁路横过去 + 红顶车站 + 公交站 + 出租车
    x0, y0, x1, y1 = rects[3][:4]
    line(d, (x0 + 1, y0 + 16, x1 - 1, y0 + 16), '#4a4a50', 2)
    for x in range(x0 + 2, x1, 5):
        px(d, x, y0 + 16, '#f0f0f0')
    rect(d, (x0 + 30, y0 + 20, x0 + 62, y0 + 32), '#f4f0e6')
    rect(d, (x0 + 28, y0 + 18, x0 + 64, y0 + 21), '#c84a3a')
    rect(d, (x0 + 40, y0 + 34, x0 + 52, y0 + 44), '#d8d0c0')         # 站前广场
    rect(d, (x0 + 70, y0 + 36, x0 + 78, y0 + 40), '#f0c030')         # 出租车
    rect(d, (x0 + 10, y0 + 36, x0 + 12, y0 + 42), '#3a8a5a')         # 公交站牌
    # b4 派出所：小房子 + 红灯 + 警车 / 自行车（小心）
    x0, y0, x1, y1 = rects[4][:4]
    for c in range(3):
        hx = x0 + 8 + c * 28
        rect(d, (hx, y0 + 30, hx + 14, y0 + 40), '#5a6a8a' if c != 1 else '#e8e4dc')
    rect(d, (x0 + 34, y0 + 14, x0 + 58, y0 + 30), '#e8e4dc')
    rect(d, (x0 + 33, y0 + 13, x0 + 59, y0 + 15), '#3a3e4a')
    ellipse(d, (x0 + 44, y0 + 18, x0 + 48, y0 + 22), '#e83a34')
    px(d, x0 + 45, y0 + 19, '#ffd0c8')
    rect(d, (x0 + 64, y0 + 18, x0 + 76, y0 + 24), '#f4f4f0')        # 警车（黑白）
    rect(d, (x0 + 64, y0 + 21, x0 + 76, y0 + 24), '#2a2a30')
    px(d, x0 + 70, y0 + 17, '#e83a34')
    # b5 河边：一道河 + 桥 + 狗屋和狗（小心）
    x0, y0, x1, y1 = rects[5][:4]
    rect(d, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), '#c8d8a0')
    poly(d, [(x0 + 30, y0 + 1), (x0 + 46, y0 + 1), (x0 + 58, y1 - 1), (x0 + 42, y1 - 1)], '#7ab0d8')
    for k in range(6):
        px(d, x0 + 38 + k * 2, y0 + 6 + k * 6, '#a8cce8')
    rect(d, (x0 + 30, y0 + 20, x0 + 60, y0 + 25), '#fffaf0')
    line(d, (x0 + 30, y0 + 19, x0 + 60, y0 + 19), '#a89870')
    line(d, (x0 + 30, y0 + 26, x0 + 60, y0 + 26), '#a89870')
    rect(d, (x0 + 68, y0 + 30, x0 + 78, y0 + 38), '#a85a3a')         # 狗屋
    poly(d, [(x0 + 66, y0 + 30), (x0 + 73, y0 + 25), (x0 + 80, y0 + 30)], '#7a3a2a')
    rect(d, (x0 + 71, y0 + 34, x0 + 74, y0 + 38), '#2a2020')
    ellipse(d, (x0 + 80, y0 + 34, x0 + 86, y0 + 39), '#c89a5a')      # 狗
    ellipse(d, (x0 + 84, y0 + 32, x0 + 88, y0 + 36), '#c89a5a')
    px(d, x0 + 87, y0 + 33, '#2a2020')
    # b6 工地：围挡、锥桶、下水道口（小心）
    x0, y0, x1, y1 = rects[6][:4]
    rect(d, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), '#d8c8a8')
    for x in range(x0 + 4, x1 - 4, 8):
        rect(d, (x, y0 + 14, x + 3, y0 + 15), '#e8c030')
        rect(d, (x + 4, y0 + 14, x + 7, y0 + 15), '#2a2a30')
    for mx_, my_ in ((x0 + 24, y0 + 28), (x0 + 60, y0 + 34)):
        ellipse(d, (mx_ - 5, my_ - 4, mx_ + 5, my_ + 4), '#5a5a62')
        ellipse(d, (mx_ - 4, my_ - 3, mx_ + 4, my_ + 3), '#3a3a42')
        for k in range(-3, 4, 2):
            line(d, (mx_ - 3, my_ + k * .7, mx_ + 3, my_ + k * .7), '#6a6a72')
    for cx in (x0 + 40, x0 + 46, x0 + 78):
        poly(d, [(cx - 2, y0 + 40), (cx, y0 + 34), (cx + 2, y0 + 40)], '#f07030')
        px(d, cx, y0 + 37, '#f4f0e8')
    rect(d, (x0 + 70, y0 + 20, x0 + 84, y0 + 28), '#e8c030')        # 小挖掘机
    rect(d, (x0 + 72, y0 + 18, x0 + 78, y0 + 21), '#2a2a30')
    # b7 便利店 + 一排自动售货机
    x0, y0, x1, y1 = rects[7][:4]
    rect(d, (x0 + 10, y0 + 12, x0 + 54, y0 + 28), '#f4f4f0')
    rect(d, (x0 + 10, y0 + 12, x0 + 54, y0 + 15), '#3a7ad8')
    rect(d, (x0 + 10, y0 + 16, x0 + 54, y0 + 17), '#f08a30')
    rect(d, (x0 + 8, y0 + 30, x0 + 56, y0 + 40), '#d0ccc4')          # 停车场
    for x in range(x0 + 12, x0 + 56, 8):
        line(d, (x, y0 + 31, x, y0 + 39), '#f4f4f0')
    for k, col in enumerate(('#d8303a', '#3a7ad8', '#f0f0f0', '#d8303a', '#40b060')):
        rect(d, (x0 + 62 + k * 5, y0 + 18, x0 + 65 + k * 5, y0 + 24), col)
    # b8 银行 + 彩票摊
    x0, y0, x1, y1 = rects[8][:4]
    rect(d, (x0 + 8, y0 + 12, x0 + 56, y0 + 30), '#e4e0d8')
    rect(d, (x0 + 8, y0 + 12, x0 + 56, y0 + 15), '#2e6a52')
    for k in range(5):
        ellipse(d, (x0 + 28 + (k % 3) * 3, y0 + 18 + (k // 3) * 3, x0 + 31 + (k % 3) * 3, y0 + 21 + (k // 3) * 3), '#7a4a9a')
    rect(d, (x0 + 66, y0 + 24, x0 + 80, y0 + 32), '#c84a3a')        # 彩票摊（红白棚）
    for k in range(0, 14, 3):
        rect(d, (x0 + 66 + k, y0 + 22, x0 + 67 + k, y0 + 24), '#f4f0e8')
    rect(d, (x0 + 30, y0 + 32, x0 + 34, y0 + 36), '#c8c4b8')
    # 街区名牌（左上角的小白签）+ 小心街区的红框
    for x0, y0, x1, y1, name, danger in rects:
        tw, th = kanji_size(name)
        rect(d, (x0 + 1, y0 + 1, x0 + tw + 4, y0 + th + 1), '#fffaf0')
        line(d, (x0 + 1, y0 + th + 2, x0 + tw + 4, y0 + th + 2), '#c8b890')
        kanji(im, x0 + 3, y0 + 1, name, '#c84a3a' if danger else '#5a4a34')
        d = ImageDraw.Draw(im)
        if danger:
            for k in range(x0, x1, 4):
                px(d, k, y0, '#c84a3a')
                px(d, k, y1, '#c84a3a')
            for k in range(y0, y1, 4):
                px(d, x0, k, '#c84a3a')
                px(d, x1, k, '#c84a3a')
    # 顶上的标题带：杜王町 · 1999年6月（左），留出右边给小游戏的计时 / 金额
    kanji(im, 10, 4, '杜王町', '#5a4a34')
    d = ImageDraw.Draw(im)
    letters(d, 50, 8, '1999.6', '#8a7a5a')
    # 纸边、折痕、旧纸噪点、四角压暗（同 morioh_map）
    rect(d, (0, 0, W - 1, H - 1), None, '#9a8a64')
    rect(d, (3, 3, W - 4, H - 4), None, '#c8b890')
    im = noise_specks(im, (0, 0, W, H), ['#e6dabe', '#f4ead2'], 500, 19)
    a = np.array(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    k = np.clip((v - 1.1) * .25, 0, .18)
    a[..., :3] *= (1 - k[..., None] * np.array([1, 1.15, 1.6]))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    anchors = {f'b{i}': [(r[0] + r[2]) // 2, (r[1] + r[3]) // 2] for i, r in enumerate(rects)}
    anchors['hud'] = [240, 10]
    meta = dict(pack=PACK, w=W, ground=170, walk=[160, 170], anchors=anchors,
                blocks=[r[:4] + [r[4], bool(r[5])] for r in rects],
                layers=[{'type': 'static', 'image': 'bg/morioh_blocks/map'}], fg=[])
    preview('morioh_blocks', {'map': im}, ['map'], W)
    return save_layers('morioh_blocks', {'map': im}, meta)


# ============================================================ 葡萄丘银行大厅 budogaoka_bank（320 宽，一屏）
#   左：自动玻璃门（外面是亮亮的街）→ 取号机 → 候客沙发 + 盆栽 → 右边三个柜台窗口（玻璃隔断，后面是办公桌、CRT、文件柜、挂钟）。
#   柜台上方深绿色的行名牌「葡萄丘银行」+ 一串葡萄的行徽。
def budogaoka_bank():
    W, G = 320, 136
    im = new(W, 180, '#ece4d4')
    d = ImageDraw.Draw(im)
    # 天花板 + 灯带
    rect(d, (0, 0, W, 12), '#d8d0c0')
    line(d, (0, 12, W, 12), '#b8b0a0')
    for x in range(14, W, 64):
        rect(d, (x, 4, x + 40, 6), '#fffaf0')
        line(d, (x, 7, x + 40, 7), '#c8c0b0')
    # 墙：上半米白、下半木护墙板
    im = grad(im, (0, 13, W, 100), ('#f2ecdf', '#ece4d4', '#e2d8c6'))
    d = ImageDraw.Draw(im)
    rect(d, (0, 100, W, G), '#9a7454')
    for x in range(0, W, 16):
        line(d, (x, 102, x, G - 2), '#8a6646')
    rect(d, (0, 100, W, 101), '#b88e64')
    rect(d, (0, G - 2, W, G), '#6a4a34')
    # 地：米色大理石 + 拼缝，近处的块大
    rect(d, (0, G, W, 180), '#e4dccb')
    y, h, row = G, 5.0, 0
    while y < 180:
        yb = min(180, int(round(y + h)))
        step = int(h * 4.2)
        for i, x in enumerate(range(-(row % 2) * step // 2, W, step)):
            if (i + row) % 2:
                rect(d, (x, int(y), x + step - 1, yb - 1), '#d4cab6')
        line(d, (0, yb, W, yb), '#c4b8a2')
        y += h + 1
        h *= 1.3
        row += 1
    # ---- 左：自动玻璃门
    rect(d, (6, 34, 56, G), '#8a8e94')
    rect(d, (8, 36, 54, G), '#f4f0e0')                              # 外面的街（亮）
    rect(d, (8, 100, 54, G), '#d8d2c4')
    rect(d, (8, 70, 54, 100), '#e6dccb')
    rect(d, (20, 74, 34, 90), '#9cc4dc')
    for x in range(8, 55, 6):                                      # 玻璃反光斜线
        line(d, (x, 40, x + 8, 32 + 16), '#ffffff')
    line(d, (31, 36, 31, G), '#8a8e94')
    rect(d, (6, 30, 56, 34), '#5a5e64')
    rect(d, (18, 31, 44, 33), '#2a2a30')
    for k in range(3):
        px(d, 24 + k * 6, 32, '#e04040')
    rect(d, (10, G, 52, G + 6), '#5a5a62')                          # 门口的地垫
    rect(d, (12, G + 1, 50, G + 5), '#6a6a74')
    # ---- 取号机
    rect(d, (64, 84, 78, G), '#e8e8e2')
    rect(d, (64, 84, 78, 86), '#2e6a52')
    rect(d, (66, 90, 76, 98), '#2a2a30')
    digits(d, 67, 92, '42', '#e04040')
    rect(d, (68, 102, 74, 104), '#c84a3a')
    rect(d, (69, 106, 73, 110), '#f4f4f0')
    line(d, (78, 84, 78, G), '#b8b8b2')
    # ---- 候客沙发两张（侧面对着我们）+ 盆栽
    for sx in (86, 118):
        rect(d, (sx, 112, sx + 28, 128), '#2e6a52')
        rect(d, (sx, 112, sx + 28, 114), '#4a8a6e')
        rect(d, (sx - 1, 124, sx + 29, 132), '#3a7a5e')
        rect(d, (sx - 1, 124, sx + 29, 125), '#5a9a7e')
        rect(d, (sx + 1, 132, sx + 2, G + 2), '#5a5a5e')
        rect(d, (sx + 26, 132, sx + 27, G + 2), '#5a5a5e')
    rect(d, (150, 120, 160, G), '#b8a080')
    rect(d, (149, 119, 161, 121), '#c8b090')
    for k, (dx, dy, r) in enumerate(((155, 104, 9), (150, 110, 6), (160, 108, 7), (155, 96, 5))):
        ellipse(d, (dx - r, dy - r, dx + r, dy + r), ['#3e6e3a', '#4e8048', '#5a8e50', '#6aa05a'][k])
    # 墙上的海报（定期存款）
    rect(d, (94, 50, 136, 82), '#fffaf0')
    rect(d, (96, 52, 134, 66), '#7ab0d8')
    ellipse(d, (100, 55, 110, 65), '#f0c030')
    kanji(im, 98, 68, '定期', '#c84a3a')
    d = ImageDraw.Draw(im)
    letters(d, 124, 72, '3.5', '#c84a3a')
    # ---- 柜台（168–320）
    K0 = 168
    # 后面的办公区
    rect(d, (K0, 52, W, 112), '#e2dccf')
    rect(d, (K0, 52, W, 54), '#cfc6b4')
    for fx in range(K0 + 6, W, 50):                                 # 文件柜
        rect(d, (fx, 60, fx + 14, 104), '#a8acb2')
        for fy in range(62, 104, 10):
            rect(d, (fx + 1, fy, fx + 13, fy + 8), '#b8bcc2')
            rect(d, (fx + 5, fy + 3, fx + 9, fy + 4), '#6a6e74')
    for dx_ in (K0 + 26, K0 + 76, K0 + 124):                       # 办公桌 + CRT
        rect(d, (dx_, 92, dx_ + 22, 95), '#8a7458')
        rect(d, (dx_ + 4, 78, dx_ + 16, 91), '#d8d4c8')
        rect(d, (dx_ + 6, 80, dx_ + 14, 88), '#3a5a6a')
        line(d, (dx_ + 7, 81, dx_ + 10, 81), '#6a9aaa')
        rect(d, (dx_ + 2, 95, dx_ + 4, 104), '#6a5a44')
        rect(d, (dx_ + 18, 95, dx_ + 20, 104), '#6a5a44')
    # 挂钟（下午 2:50，银行 3 点关门）
    cx, cy, r = 296, 64, 6
    ellipse(d, (cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), '#5a5e64')
    ellipse(d, (cx - r, cy - r, cx + r, cy + r), '#f6f0e0')
    line(d, (cx, cy, cx + 5 * math.sin(50 / 60 * 2 * math.pi), cy - 5 * math.cos(50 / 60 * 2 * math.pi)), '#2a2a30')
    line(d, (cx, cy, cx + 3 * math.sin((2 + 50 / 60) / 12 * 2 * math.pi), cy - 3 * math.cos((2 + 50 / 60) / 12 * 2 * math.pi)),
         '#2a2a30')
    # 柜台本体
    rect(d, (K0, 112, W, G), '#7a5a40')
    for x in range(K0, W, 50):
        rect(d, (x + 2, 116, x + 47, G - 4), '#8a6a4e')
        line(d, (x + 2, 116, x + 47, 116), '#a2805e')
    rect(d, (K0 - 2, 108, W, 112), '#e8e2d6')                       # 台面（大理石）
    line(d, (K0 - 2, 108, W, 108), '#fffaf0')
    line(d, (K0 - 2, 112, W, 112), '#a89e8c')
    # 玻璃隔断 + 三个窗口
    wins = []
    for i in range(3):
        x0 = K0 + 2 + i * 50
        x1 = x0 + 46
        wins.append((x0 + x1) // 2)
        rect(d, (x0, 70, x0 + 1, 108), '#9a9ea4')
        rect(d, (x1, 70, x1 + 1, 108), '#9a9ea4')
        for k in range(0, 40, 9):                                   # 玻璃上的反光
            line(d, (x0 + 4 + k, 72, x0 + 10 + k, 66 + 12), '#f8f8f4')
        rect(d, (x0 + 14, 102, x1 - 14, 104), '#6a6e74')             # 递钱的小槽
        rect(d, (x0 + 16, 74, x1 - 16, 82), '#2a2a30')               # 叫号牌
        digits(d, x0 + 19, 76, str(i + 1), '#f0c030')
        digits(d, x0 + 25, 76, '0' + str(39 + i), '#e04040')
    rect(d, (K0, 68, W, 70), '#8a8e94')
    # 行名牌：深绿底 + 金字 + 葡萄行徽
    name = '葡萄丘银行'
    tw, th = kanji_size(name)
    nx = K0 + (W - K0 - tw) // 2 + 6
    rect(d, (K0 + 8, 20, W - 4, 40), '#2e6a52')
    rect(d, (K0 + 8, 20, W - 4, 21), '#4a8a6e')
    rect(d, (K0 + 8, 39, W - 4, 40), '#1e4a3a')
    kanji(im, nx, 24, name, '#f0d070')
    d = ImageDraw.Draw(im)
    gx, gy = nx - 14, 24
    for k, (ox, oy) in enumerate(((0, 0), (4, 0), (8, 0), (2, 4), (6, 4), (4, 8))):
        ellipse(d, (gx + ox, gy + oy, gx + ox + 4, gy + oy + 4), '#8a5aaa')
        px(d, gx + ox + 1, gy + oy + 1, '#c8a0e0')
    line(d, (gx + 6, gy - 2, gx + 8, gy), '#5a8a4a')
    # 门口方向打来的光（地上一块亮）
    yy, xx = np.mgrid[0:180, 0:W]
    f = np.clip(1 - np.hypot((xx - 32) / 70, (yy - 150) / 26), 0, 1) * .6
    glow = glow_from_field(f, '#3a3428', levels=4)
    layers = {'room': im, 'glow': glow}
    meta = dict(pack=PACK, w=W, ground=150, walk=[140, 176],
                anchors=dict(door=[31, 146], ticket=[71, 146], sofa=[116, 146], plant=[155, 146], poster=[115, 66],
                             window1=[wins[0], 146], window2=[wins[1], 146], window3=[wins[2], 146], counter=[wins[1], 108],
                             clock=[cx, cy], sign=[nx + tw // 2, 30], walk_x=[8, 312]),
                layers=[{'type': 'pano', 'image': 'bg/budogaoka_bank/room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'glow', 'image': 'bg/budogaoka_bank/glow', 'k': 1, 'x': 0, 'y': 0}],
                fg=[])
    preview('budogaoka_bank', {'room': im}, ['room'], W)
    return save_layers('budogaoka_bank', layers, meta)


# ============================================================ 楼外墙 + 楼顶 rooftops（640 宽 = 两屏，第 9 战）
#   左一屏（0–320）：大楼正面，从下往上是人行道（y150）、二楼窗台的檐（y112）、三楼的檐（y74）、楼顶女儿墙（y36）—— 爬墙那段用。
#   右一屏（320–640）：楼顶（地面 y150）：水箱、楼梯间、铁丝网；中间两栋楼的空当（450–530）架着两根水管：下面那根走人（y150），
#   上面那根扶手（y128）。开关层 brk1..brk4：下面那根水管从左到右的第 1..4 段断开（剧情设 state.brkN = 1，修好设回 0）。
#   两屏不在同一个高度，舞台请用 x0/x1 把镜头卡在其中一屏。
def rooftops():
    W = 640
    FW = (W - 320) // 2 + 320
    far = sky_far(FW, seed=9)
    near = new(W, 180)
    d = ImageDraw.Draw(near)
    # ================= 左屏：大楼正面
    B0, B1, TOP = 8, 296, 36
    wall, wall2 = '#d8ccb4', '#c4b69c'
    rect(d, (B0, TOP, B1, 150), wall)
    for y in range(TOP + 2, 150, 3):                               # 贴面砖的横纹
        line(d, (B0, y, B1, y), wall2 if y % 6 == 0 else mix(wall, wall2, .4))
    rect(d, (B0, TOP - 8, B1, TOP), '#c8bca4')                      # 女儿墙
    rect(d, (B0 - 2, TOP - 10, B1 + 2, TOP - 8), '#e8e0cc')
    line(d, (B0, TOP, B1, TOP), '#9a8e78')
    rect(d, (B1 - 3, TOP - 8, B1, 150), '#a89c84')                   # 楼的右边角（背光）
    rect(d, (B0, TOP - 8, B0 + 2, 150), '#ece2cc')
    # 两层檐（能站人）：上面是走得上去的平台，下面一道阴影
    for ly in (112, 74):
        rect(d, (B0 - 4, ly - 2, B1 + 4, ly + 3), '#e8e0cc')
        line(d, (B0 - 4, ly - 2, B1 + 4, ly - 2), '#fffaf0')
        rect(d, (B0 - 4, ly + 4, B1 + 4, ly + 5), '#8a7e68')
        for x in range(B0, B1, 3):
            px(d, x, ly + 6, '#a89c84')
    # 每层的窗（铝框 + 天空的反光）、空调外机、广告招牌
    for fy0, fy1 in ((TOP + 6, 70), (80, 108)):
        for i, wx in enumerate(range(B0 + 18, B1 - 30, 46)):
            window(d, (wx, fy0 + 4, wx + 30, fy1 - 6), frame='#c8ccd0', glass=('#88b4d4', '#c4def0'),
                   curtain='#e8d8b8' if (i + fy0) % 3 == 0 else None)
    near = ac_unit(near, 120, 58, 20, 13)
    near = ac_unit(near, 214, 96, 20, 13)
    d = ImageDraw.Draw(near)
    near = drainpipe(near, 34, TOP - 8, 150)
    d = ImageDraw.Draw(near)
    # 一楼：店面（卷帘半拉 + 玻璃门）
    rect(d, (B0 + 6, 118, B1 - 6, 150), '#a8b4bc')
    for x in range(B0 + 8, 150, 1):
        pass
    rect(d, (B0 + 40, 118, 150, 134), '#b8bcc0')                     # 卷帘
    for y in range(119, 134, 2):
        line(d, (B0 + 40, y, 150, y), '#9a9ea4')
    rect(d, (B0 + 40, 134, 150, 150), '#5a6a78')
    rect(d, (170, 118, 230, 150), '#9cc4dc')
    for x in range(172, 230, 7):
        line(d, (x, 120, x + 5, 126), '#d4ecf4')
    line(d, (200, 118, 200, 150), '#8a9aa4')
    rect(d, (B0 + 6, 116, B1 - 6, 117), '#8a7e68')
    # 竖招牌（右上角，红底白字的 “BLDG”）
    rect(d, (268, 40, 284, 104), '#c84a3a')
    rect(d, (269, 41, 283, 103), '#d85a48')
    for i, ch in enumerate('MORIOH'):
        letters(d, 274, 46 + i * 9, ch, '#fffaf0')
    rect(d, (284, 50, 296, 51), '#6a6a66')
    rect(d, (284, 90, 296, 91), '#6a6a66')
    # 人行道（爬墙的起点）
    near = sidewalk(near, 0, 320, 150, 180)
    d = ImageDraw.Draw(near)
    line(d, (0, 150, 320, 150), '#7a766e')
    # 楼右边的空当：远处另一栋楼的侧面（灰，暗）
    rect(d, (304, 60, 320, 150), '#a8a49c')
    for y in range(66, 150, 10):
        rect(d, (307, y, 316, y + 5), '#8a8680')
    # ================= 右屏：楼顶
    R = 320
    GR = 140                                                       # 楼顶后面女儿墙的墙脚
    # 楼 A 的楼顶（320–452）
    A1 = 452
    rect(d, (R, GR - 10, A1, GR), '#c8c0ac')                         # 女儿墙
    rect(d, (R, GR - 12, A1, GR - 10), '#e0d8c4')
    rect(d, (R, GR, A1, 180), '#b4ac9c')                             # 楼顶地面（防水砖）
    for y in range(GR + 6, 180, 8):
        line(d, (R, y, A1, y), '#a29a8a')
    for x in range(R, A1, 12):
        line(d, (x, GR, x - 4, 180), '#a29a8a')
    near = noise_specks(near, (R, GR, A1, 180), ['#a8a090', '#c0b8a8'], 300, 31)
    d = ImageDraw.Draw(near)
    near = chainlink(near, R, A1, 92, GR - 12, col='#6a8a7a', post='#4a6a5e')
    d = ImageDraw.Draw(near)
    # 水箱（架子上）
    for lx in (334, 368):
        rect(d, (lx, 82, lx + 2, GR + 6), '#6a6e74')
    line(d, (334, 110, 370, 96), '#6a6e74')
    line(d, (334, 96, 370, 110), '#6a6e74')
    rect(d, (328, 56, 376, 82), '#e0e2e4')
    ellipse(d, (328, 52, 376, 62), '#eceef0')
    rect(d, (328, 66, 376, 67), '#c4c8cc')
    rect(d, (370, 58, 376, 82), '#b8bcc0')
    # 楼梯间（塔屋）+ 铁门
    rect(d, (388, 70, 440, GR + 4), '#d0c8b4')
    rect(d, (386, 66, 442, 70), '#b8b0a0')
    rect(d, (402, 96, 424, GR + 4), '#7a8a96')
    rect(d, (404, 98, 422, GR + 4), '#8a9aa6')
    px(d, 419, 120, '#e0e0d8')
    line(d, (388, 70, 388, GR + 4), '#e4dccb')
    line(d, (440, 70, 440, GR + 4), '#a49c88')
    near = ac_unit(near, 340, 126, 22, 14)
    d = ImageDraw.Draw(near)
    # 楼 A 的楼边（前沿：断口，往下是空的）
    rect(d, (A1 - 2, GR - 12, A1, 180), '#8a8272')
    # ---- 两栋楼中间的空当（452–530）：往下看是窄窄的缝，越往下越暗
    G0, G1 = A1, 530
    for y in range(GR - 12, 180):
        k = (y - (GR - 12)) / (180 - GR + 12)
        col = mix('#8a8494', '#2a2632', k ** .7)
        line(d, (G0, y, G1, y), col)
    rect(d, (G0, GR - 12, G0 + 6, 180), '#6e6678')                    # 两边楼的侧墙
    rect(d, (G1 - 6, GR - 12, G1, 180), '#5e5868')
    for y in range(GR - 6, 180, 7):
        rect(d, (G0 + 1, y, G0 + 4, y + 3), '#4e4858')
        rect(d, (G1 - 5, y + 3, G1 - 2, y + 6), '#423c4c')
    # 缝底：远远的一条巷子（垃圾桶两个小点）
    rect(d, (G0 + 30, 176, G0 + 33, 179), '#5a7a6a')
    rect(d, (G0 + 40, 177, G0 + 42, 179), '#7a6a5a')
    # 楼 B 的楼顶（530–640）
    rect(d, (G1, GR - 10, W, GR), '#bcc0c4')
    rect(d, (G1, GR - 12, W, GR - 10), '#d8dcdf')
    rect(d, (G1, GR, W, 180), '#a8acb0')
    for y in range(GR + 6, 180, 8):
        line(d, (G1, y, W, y), '#989ca0')
    for x in range(G1, W, 12):
        line(d, (x, GR, x + 4, 180), '#989ca0')
    near = noise_specks(near, (G1, GR, W, 180), ['#9ca0a4', '#b8bcc0'], 240, 33)
    d = ImageDraw.Draw(near)
    rect(d, (G1, GR - 12, G1 + 2, 180), '#8a8e92')
    # 楼 B：广告牌的铁架子背面 + 天线
    for lx in range(560, 640, 20):
        rect(d, (lx, 60, lx + 1, GR - 12), '#6a6e74')
    for y in (70, 96, 120):
        line(d, (556, y, 640, y), '#6a6e74')
    for x in range(560, 620, 20):
        line(d, (x, 70, x + 20, 96), '#7a7e84')
        line(d, (x + 20, 70, x, 96), '#7a7e84')
    rect(d, (552, 34, 640, 60), '#e4e6e8')                           # 广告牌的背面（白铁皮）
    for x in range(556, 640, 8):
        line(d, (x, 34, x, 60), '#ccd0d4')
    line(d, (604, 34, 604, 14), '#5a5e64')                           # 天线
    for k in range(4):
        line(d, (598 + k, 18 + k * 4, 610 - k, 18 + k * 4), '#5a5e64')
    near = ac_unit(near, 544, 125, 24, 15)
    d = ImageDraw.Draw(near)
    # ---- 两根水管（先画一份没有水管的，断口层从里面裁）
    nopipe = near.copy()
    P0, P1 = A1 - 6, G1 + 6
    PY, PY2 = 148, 126

    def pipe(dd, x0, x1, y, th=3):
        rect(dd, (x0, y, x1, y + th), '#9a9ea4')
        line(dd, (x0, y, x1, y), '#d4d8dc')
        line(dd, (x0, y + th, x1, y + th), '#5a5e64')
        for x in range(x0 + 10, x1 - 4, 18):
            rect(dd, (x, y - 1, x + 2, y + th + 1), '#7a7e84')

    pipe(d, P0, P1, PY, 4)
    pipe(d, P0, P1, PY2, 2)
    for x in (P0 + 2, P1 - 4):                                      # 两头的固定卡子
        rect(d, (x - 2, PY2 - 2, x + 3, PY + 6), '#6a6e74')
        rect(d, (x - 1, PY2 - 1, x + 2, PY + 5), '#8a8e94')
    # 断口层：每段 = 没有水管的底子 + 两头参差的断茬 + 滴下来的水
    segs = []
    sx0, sx1 = A1 + 2, G1 - 2
    sw = (sx1 - sx0) // 4
    brks = {}
    for i in range(4):
        a0 = sx0 + i * sw
        a1 = a0 + sw
        piece = nopipe.crop((a0, PY - 2, a1, PY + 8)).copy()
        pd = ImageDraw.Draw(piece)
        for side, xx in ((0, 0), (1, sw - 1)):
            for yy in range(2, 7):
                L = 1 + (yy * 3 + side * 2 + i) % 3
                xs_ = range(0, L) if side == 0 else range(sw - L, sw)
                for x in xs_:
                    px(pd, x, yy, '#9a9ea4' if yy > 2 else '#d4d8dc')
            px(pd, xx, 7, '#5a5e64')
        for k in (3, 6):
            px(pd, (sw // 2 + k * (i + 1)) % sw, 8, '#a8d0f0')
        brks[f'brk{i + 1}'] = piece
        segs.append([a0, a1])
    layers = dict(far=far, near=near, **brks)
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(street=[160, 150], ledge1=[150, 112], ledge2=[150, 74], roof_edge=[150, 34], ledges_y=[150, 112, 74, 34],
                             climb_x=[16, 292], screen1=[0, 320], screen2=[320, 640], tank=[352, 146], stairs_door=[413, 146],
                             pipe_l=[P0, PY], pipe_r=[P1, PY], pipe_rail_y=PY2, gap=[G0, G1], roof_b=[590, 146],
                             pipe_segs=segs, walk_x_roof=[330, 632]),
                layers=[{'type': 'pano', 'image': 'bg/rooftops/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/rooftops/near', 'k': 1, 'x': 0, 'y': 0}]
                + [{'type': 'image', 'image': f'bg/rooftops/brk{i + 1}', 'k': 1, 'x': segs[i][0], 'y': PY - 2, 'key': f'brk{i + 1}'}
                   for i in range(4)],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    preview('rooftops', {'all': pv}, ['all'], W)
    return save_layers('rooftops', layers, meta)


# ============================================================ 三明治店门口 + 公园 st_gentleman（480 宽，六月的中午）
#   左：砖楼一角 → 三明治店（深绿门脸、绿白条纹遮阳棚、橱窗里的三明治、玻璃门、黑板菜单）→ 路灯 + 垃圾桶 →
#   公园：树篱和紫阳花、两张长椅（左边那张就是拿错纸袋的地方）、饮水台、大树。
def st_gentleman():
    W, G = 480, 136
    FW = (W - 320) // 2 + 320
    far = sky_far(FW, seed=21, sea=False)
    near = new(W, 180)
    near = sidewalk(near, 0, 232, G, 166)
    near = asphalt(near, 0, W, 166, 180)
    d = ImageDraw.Draw(near)
    # 公园的地：碎石小路
    rect(d, (232, G, W, 166), '#d8c8a4')
    near = noise_specks(near, (232, G, W, 166), ['#c4b490', '#e4d6b6', '#b0a080'], 700, 41)
    d = ImageDraw.Draw(near)
    line(d, (232, G, W, G), '#b8a884')
    # ---- 左：砖楼一角
    rect(d, (0, 40, 40, G), '#a8644a')
    for i, y in enumerate(range(40, G, 4)):
        line(d, (0, y, 40, y), '#8e523c')
        for x in range(0 if i % 2 else 5, 40, 10):
            line(d, (x, y, x, y + 3), '#8e523c')
    window(d, (8, 52, 30, 72), glass=('#8eb8d2', '#c0dcea'))
    window(d, (8, 92, 30, 112), glass=('#8eb8d2', '#c0dcea'), curtain='#e8d8b8')
    rect(d, (38, 40, 40, G), '#7a3e2c')
    # ---- 三明治店（40–212）
    S0, S1 = 40, 212
    rect(d, (S0, 30, S1, G), '#f0e8d6')                              # 二楼外墙
    for y in range(32, 72, 4):
        line(d, (S0, y, S1, y), '#e4dac4')
    rect(d, (S0, 26, S1, 30), '#2e5a44')
    for wx in (56, 106, 156):
        window(d, (wx, 38, wx + 30, 60), frame='#2e5a44', glass=('#8eb8d2', '#c0dcea'), curtain='#f0d8a0')
        rect(d, (wx - 2, 61, wx + 32, 66), '#7a5a40')                # 花箱
        for k in range(0, 34, 4):
            ellipse(d, (wx - 2 + k, 57, wx + 2 + k, 62), ['#e84a5a', '#f0c030', '#e86aa0'][k // 4 % 3])
            px(d, wx + k, 61, '#4a7a4a')
    # 招牌带：深绿 + 金色 ST.GENTLEMAN + 小字 SANDWICH
    rect(d, (S0, 70, S1, 90), '#2e5a44')
    rect(d, (S0, 70, S1, 71), '#4a7a60')
    rect(d, (S0, 89, S1, 90), '#1e3a2c')
    t1, t2 = 'ST. GENTLEMAN', 'SANDWICH SHOP'
    letters(d, (S0 + S1 - text_w(t1, 2)) // 2, 74, t1, '#f0d070', gap=2)
    letters(d, (S0 + S1 - text_w(t2)) // 2, 82, t2, '#e8e0cc')
    # 条纹遮阳棚（下沿是波浪边）
    for y in range(91, 104):
        k = (y - 91) / 13
        xa, xb = S0 - k * 4, S1 + k * 4
        for x in range(int(xa), int(xb) + 1):
            col = '#3a7a5a' if ((x - S0) // 8) % 2 == 0 else '#f4f0e4'
            if y == 91:
                col = mix(col, '#000000', .2)
            px(d, x, y, col)
    for x in range(S0 - 4, S1 + 5, 8):
        ellipse(d, (x, 101, x + 7, 107), '#3a7a5a' if ((x - S0 + 4) // 8) % 2 == 0 else '#f4f0e4')
    for x in range(S0 - 4, S1 + 4):                                 # 棚下面的阴影
        px(d, x, 108, '#c8bca4')
    # 店面：橱窗（三明治摆在架子上）+ 玻璃门
    rect(d, (S0, 108, S1, G), '#2e5a44')
    rect(d, (S0 + 6, 110, S0 + 96, G - 6), '#cfe2ea')
    for y in (118, 126):
        rect(d, (S0 + 8, y, S0 + 94, y + 1), '#a8a090')
        for k, x in enumerate(range(S0 + 10, S0 + 92, 10)):
            poly(d, [(x, y), (x + 8, y), (x + 8, y - 6)], '#f0dca0')     # 三角三明治
            line(d, (x + 1, y - 1, x + 8, y - 1), ['#6ab04a', '#e84a3a', '#f0c030'][k % 3])
            line(d, (x + 8, y - 6, x + 8, y), '#c8a870')
    for x in range(S0 + 8, S0 + 96, 9):
        line(d, (x, 110, x + 5, 115), '#ffffff')
    rect(d, (S0 + 6, G - 6, S0 + 96, G), '#1e3a2c')
    DX = S0 + 108
    rect(d, (DX, 110, DX + 24, G), '#1e3a2c')
    rect(d, (DX + 2, 112, DX + 22, G), '#bcd4de')
    line(d, (DX + 12, 112, DX + 12, G), '#1e3a2c')
    rect(d, (DX + 8, 122, DX + 10, 126), '#c8a050')
    rect(d, (DX + 14, 122, DX + 16, 126), '#c8a050')
    rect(d, (DX + 5, 114, DX + 19, 119), '#fffaf0')                  # 门上的 OPEN 牌
    letters(d, DX + 6, 114, 'OPEN', '#c84a3a')
    rect(d, (S1 - 30, 112, S1 - 6, G - 6), '#cfe2ea')                 # 右边的小窗（外卖口）
    line(d, (S1 - 18, 112, S1 - 18, G - 6), '#2e5a44')
    # 黑板菜单（A 字架）
    MX = 222
    line(d, (MX - 8, G + 10, MX - 2, G - 20), '#7a5a40')
    line(d, (MX + 8, G + 10, MX + 2, G - 20), '#7a5a40')
    rect(d, (MX - 9, G - 18, MX + 9, G + 2), '#2e3a34')
    rect(d, (MX - 10, G - 19, MX + 10, G - 18), '#7a5a40')
    for k in range(4):
        line(d, (MX - 6, G - 14 + k * 4, MX + 2 + (k % 2) * 4, G - 14 + k * 4), '#e8e4dc')
    # 路灯 + 垃圾桶（店和公园中间）
    near = street_lamp(near, 236, G + 4, 96)
    d = ImageDraw.Draw(near)
    rect(d, (244, G - 12, 254, G + 2), '#4a6a5a')
    rect(d, (243, G - 14, 255, G - 12), '#5a7a6a')
    # ---- 公园（232–480）
    # 树篱 + 紫阳花
    near = hedge(near, 258, W, G - 22, G, seed=43)
    d = ImageDraw.Draw(near)
    rng = np.random.RandomState(45)
    for _ in range(26):
        hx, hy = rng.randint(262, W - 4), rng.randint(G - 22, G - 8)
        c = ['#7a8ad8', '#9a7ac8', '#6aa0d8', '#c08ad0'][rng.randint(4)]
        ellipse(d, (hx - 3, hy - 3, hx + 3, hy + 2), c)
        px(d, hx - 1, hy - 2, mix(c, '#ffffff', .4))
    # 大树（六月，满树绿）
    for tx, th, tw, s in ((300, 120, 70, 1), (398, 132, 84, 2), (470, 116, 64, 3)):
        trng = np.random.RandomState(s + 50)
        rect(d, (tx - 4, G - 50, tx + 4, G - 18), '#5a4234')
        line(d, (tx - 4, G - 50, tx - 4, G - 18), '#3e2c22')
        line(d, (tx + 3, G - 50, tx + 3, G - 18), '#7a5c48')
        top = G - th
        for k in range(14):
            cx_ = tx + trng.uniform(-tw / 2 + 10, tw / 2 - 10)
            cy_ = top + 20 + trng.uniform(0, th * .45)
            r = trng.uniform(10, 17)
            ellipse(d, (cx_ - r, cy_ - r * .8, cx_ + r, cy_ + r * .8), '#2e5a3a')
        for k in range(12):
            cx_ = tx + trng.uniform(-tw / 2 + 12, tw / 2 - 12)
            cy_ = top + 16 + trng.uniform(0, th * .4)
            r = trng.uniform(8, 13)
            ellipse(d, (cx_ - r, cy_ - r * .8, cx_ + r * .7, cy_ + r * .5), '#4a7c4a')
        for k in range(8):
            cx_ = tx + trng.uniform(-tw / 2 + 14, tw / 2 - 18)
            cy_ = top + 14 + trng.uniform(0, th * .3)
            r = trng.uniform(5, 8)
            ellipse(d, (cx_ - r, cy_ - r * .7, cx_ + r * .5, cy_ + r * .3), '#6e9e5a')
            px(d, cx_ - 2, cy_ - 2, '#94c070')
    # 长椅两张（木条 + 铸铁腿）
    benches = []
    for bx in (316, 420):
        benches.append(bx + 20)
        for lx in (bx + 3, bx + 35):                                   # 铸铁侧架：靠背立柱 + 扶手 + 腿
            line(d, (lx, G - 20, lx + 1, G - 2), '#3a3a40')
            line(d, (lx - 2, G - 9, lx + 3, G - 9), '#3a3a40')
            line(d, (lx - 1, G - 2, lx - 3, G + 8), '#3a3a40')
            line(d, (lx + 2, G - 2, lx + 4, G + 8), '#3a3a40')
        for y in (G - 20, G - 15):                                      # 靠背两条木
            rect(d, (bx, y, bx + 40, y + 2), '#a0765a')
            line(d, (bx, y, bx + 40, y), '#c0966a')
        rect(d, (bx - 2, G - 3, bx + 42, G - 1), '#b0866a')            # 座面
        line(d, (bx - 2, G - 3, bx + 42, G - 3), '#d0a67a')
        line(d, (bx - 2, G, bx + 42, G), '#7a5640')
    # 饮水台
    FX = 380
    rect(d, (FX, G - 10, FX + 8, G + 6), '#b8b4ac')
    rect(d, (FX - 2, G - 13, FX + 10, G - 10), '#d8d4cc')
    rect(d, (FX + 3, G - 15, FX + 5, G - 13), '#8a8e94')
    # 公园入口的牌子
    pw, ph = kanji_size('杜王公园')
    psx = 266 - pw // 2
    rect(d, (265, G - 36, 267, G + 4), '#6a5a44')
    rect(d, (psx - 3, G - 52, psx + pw + 2, G - 36), '#f4ecd8')
    rect(d, (psx - 3, G - 52, psx + pw + 2, G - 51), '#4a7a4a')
    line(d, (psx - 3, G - 36, psx + pw + 2, G - 36), '#b8a884')
    kanji(near, psx, G - 51, '杜王公园', '#3e5e3a')
    d = ImageDraw.Draw(near)
    # 鸽子两只
    for gx_ in (364, 396):
        ellipse(d, (gx_, G + 12, gx_ + 6, G + 16), '#8a8e9a')
        ellipse(d, (gx_ + 4, G + 10, gx_ + 8, G + 13), '#9a9eaa')
        px(d, gx_ + 8, G + 11, '#e0a040')
    layers = {'far': far, 'near': near}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(shop_window=[S0 + 50, 146], shop_door=[DX + 12, 146], takeout=[S1 - 18, 146], menu=[MX, 146],
                             lamp=[240, 146], trash=[249, 146], park_sign=[266, 146], bench=[benches[0], 146],
                             bench_seat=[benches[0], G - 4], bench2=[benches[1], 146], fountain=[FX + 4, 146], pigeons=[380, 150],
                             walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/st_gentleman/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/st_gentleman/near', 'k': 1, 'x': 0, 'y': 0}],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    preview('st_gentleman', {'all': pv}, ['all'], W)
    return save_layers('st_gentleman', layers, meta)


# ============================================================ 重清的初中 middle_school（640 宽：操场一角 / 体育仓库 / 走廊）
#   左（0–228）操场一角：铁丝网（看得见外面的街）、球门、半埋的轮胎、一棵树。
#   中（228–392）体育仓库（剖开前墙）：跳箱、垫子、球筐、跨栏、墙上的挂钩和一只铁丝衣架、高窗。
#   右（392–640）教学楼走廊：大窗、公告栏、消防栓箱、教室的拉门；最右是楼梯口（第 10 战爬到这里能看见仗助）。
#   开关层 pm：傍晚的橙色罩（放学后、第 10 战）。
def middle_school():
    W = 640
    FW = (W - 320) // 2 + 320
    far = sky_far(FW, seed=27)
    near = new(W, 180)
    d = ImageDraw.Draw(near)
    # ================= 操场一角（0–228）
    O1, GO = 228, 132
    rect(d, (0, GO, O1, 180), '#d8c09a')
    near = noise_specks(near, (0, GO, O1, 180), ['#c8b08a', '#e4d0ac', '#b89e78'], 900, 51)
    d = ImageDraw.Draw(near)
    line(d, (0, 168, O1, 160), '#f4f0e6')                          # 白线
    line(d, (0, 169, O1, 161), '#e8e2d6')
    # 铁丝网后面的矮墙 + 树
    near = block_wall(near, 0, O1, GO - 12, GO)
    d = ImageDraw.Draw(near)
    near = chainlink(near, 0, O1, 50, GO - 12)
    d = ImageDraw.Draw(near)
    # 球门（侧面：门柱 + 网）
    gx0, gx1 = 26, 92
    for x in (gx0, gx1):
        rect(d, (x, GO - 26, x + 2, GO + 18), '#f4f4f0')
    rect(d, (gx0, GO - 28, gx1 + 2, GO - 26), '#f4f4f0')
    for x in range(gx0 + 4, gx1, 5):
        line(d, (x, GO - 25, x + 4, GO + 16), '#d8d8d4')
    for y in range(GO - 22, GO + 16, 5):
        line(d, (gx0 + 3, y, gx1 - 1, y + 2), '#d8d8d4')
    # 半埋的轮胎（彩色）
    for k, tx in enumerate(range(116, 190, 14)):
        col = ['#e84a3a', '#f0c030', '#3a8ad8', '#40b060', '#e86aa0', '#f08a30'][k % 6]
        ellipse(d, (tx, GO + 6, tx + 12, GO + 20), '#2a2a30')
        ellipse(d, (tx + 2, GO + 8, tx + 10, GO + 18), col)
        ellipse(d, (tx + 4, GO + 10, tx + 8, GO + 16), '#2a2a30')
        rect(d, (tx - 1, GO + 15, tx + 13, GO + 21), '#d8c09a')
    # 树（梅雨季的绿）
    tx = 206
    rect(d, (tx - 3, GO - 50, tx + 3, GO + 2), '#5a4234')
    trng = np.random.RandomState(53)
    for k in range(16):
        cx_ = tx + trng.uniform(-26, 22)
        cy_ = GO - 70 + trng.uniform(-18, 22)
        r = trng.uniform(9, 15)
        ellipse(d, (cx_ - r, cy_ - r * .8, cx_ + r, cy_ + r * .8), ['#2e5a3a', '#4a7c4a', '#6e9e5a'][k % 3])
    # ================= 体育仓库（228–392）：剖开的前墙
    K0, K1, GK = 228, 392, 136
    rect(d, (K0, 40, K1, GK), '#8e8a84')                              # 里墙（暗）
    near = noise_specks(near, (K0, 40, K1, GK), ['#86827c', '#96928c'], 500, 55)
    d = ImageDraw.Draw(near)
    for y in range(56, GK, 20):
        line(d, (K0, y, K1, y), '#7e7a74')
    rect(d, (K0, GK, K1, 180), '#a8a49c')                             # 水泥地
    for y in range(GK + 8, 180, 10):
        line(d, (K0, y, K1, y), '#9a968e')
    near = noise_specks(near, (K0, GK, K1, 180), ['#9a968e', '#b4b0a8'], 300, 57)
    d = ImageDraw.Draw(near)
    rect(d, (K0 - 4, 30, K1 + 4, 40), '#c8c4bc')                       # 屋顶板
    line(d, (K0 - 4, 30, K1 + 4, 30), '#e0dcd4')
    rect(d, (K0 - 4, 40, K1 + 4, 42), '#6a6660')
    rect(d, (K0, 42, K0 + 6, 180), '#c0bcb4')                          # 左右墙的断面
    rect(d, (K1 - 6, 42, K1, 180), '#c0bcb4')
    line(d, (K0 + 6, 42, K0 + 6, 180), '#8a8680')
    line(d, (K1 - 6, 42, K1 - 6, 180), '#8a8680')
    # 高窗（透进来一束光）
    rect(d, (296, 50, 336, 64), '#c8dce8')
    line(d, (316, 50, 316, 64), '#6a6660')
    for k in (0, 1):
        line(d, (296 + k * 20 + 3, 52, 296 + k * 20 + 8, 57), '#f0f8fc')
    # 铁架子（球、绳子、标志锥）
    rect(d, (240, 64, 282, 66), '#6a6e74')
    rect(d, (240, 92, 282, 94), '#6a6e74')
    for x in (240, 281):
        rect(d, (x, 60, x + 1, GK), '#6a6e74')
    for k, bx in enumerate(range(243, 279, 9)):
        ellipse(d, (bx, 84, bx + 8, 92), ['#f4f4f0', '#e8c030', '#3a8ad8', '#e84a3a'][k % 4])
    for k, cx_ in enumerate(range(246, 280, 10)):
        poly(d, [(cx_ - 3, 64), (cx_, 54), (cx_ + 3, 64)], '#f07030')
    ellipse(d, (250, 100, 270, 112), '#c8a870')                       # 一卷跳绳 / 拔河绳
    ellipse(d, (254, 103, 266, 109), '#8e8a84')
    # 跳箱（五段 + 白色顶）
    jx = 248
    for i in range(5):
        y0 = GK - 6 - (i + 1) * 7
        inset = i
        rect(d, (jx + inset, y0, jx + 40 - inset, y0 + 7), '#c8a070' if i % 2 else '#b88e60')
        line(d, (jx + inset, y0, jx + 40 - inset, y0), '#d8b484')
        rect(d, (jx + 14, y0 + 2, jx + 26, y0 + 4), '#7a5a3a')
    rect(d, (jx + 4, GK - 48, jx + 36, GK - 41), '#f4f0e6')
    line(d, (jx + 4, GK - 41, jx + 36, GK - 41), '#c8c4b8')
    # 垫子（蓝、绿两摞，卷起来的一卷）
    mx = 300
    for i, col in enumerate(('#3a6ab0', '#3a6ab0', '#4a8a5a', '#4a8a5a', '#3a6ab0')):
        y0 = GK + 4 - (i + 1) * 6
        rect(d, (mx, y0, mx + 44, y0 + 5), col)
        line(d, (mx, y0, mx + 44, y0), mix(col, '#ffffff', .3))
    ellipse(d, (mx + 8, GK - 52, mx + 30, GK - 30), '#4a8a5a')
    ellipse(d, (mx + 13, GK - 47, mx + 25, GK - 35), '#2e5a3a')
    # 球筐（推车）
    bx = 352
    rect(d, (bx, GK - 26, bx + 26, GK - 4), '#8a8e94')
    for x in range(bx, bx + 27, 4):
        line(d, (x, GK - 26, x, GK - 4), '#6a6e74')
    for k, (ox, oy) in enumerate(((2, -32), (10, -33), (18, -32), (6, -38), (14, -38))):
        ellipse(d, (bx + ox, GK + oy, bx + ox + 8, GK + oy + 8), ['#f4f4f0', '#e8e4dc'][k % 2])
        line(d, (bx + ox + 2, GK + oy + 2, bx + ox + 6, GK + oy + 6), '#2a2a30')
    for wx in (bx + 3, bx + 22):
        ellipse(d, (wx - 2, GK - 4, wx + 2, GK), '#2a2a30')
    # 墙上的挂钩一排 + 一只铁丝衣架（吉良用它钩回纸袋）
    for hx in range(344, 386, 10):
        rect(d, (hx, 72, hx + 1, 76), '#5a5e64')
    hx, hy = 374, 76
    line(d, (hx, hy, hx, hy + 3), '#b8bcc4')
    line(d, (hx, hy + 3, hx - 7, hy + 9), '#b8bcc4')
    line(d, (hx, hy + 3, hx + 7, hy + 9), '#b8bcc4')
    line(d, (hx - 7, hy + 9, hx + 7, hy + 9), '#b8bcc4')
    # 门口的拉门（拉开在右墙外侧）
    rect(d, (K1, 52, K1 + 6, GK + 4), '#6a7a8a')
    line(d, (K1 + 3, 52, K1 + 3, GK + 4), '#5a6a7a')
    # ================= 走廊（392–640）
    C0 = 398
    GC = 134
    rect(d, (K1, 0, W, 30), '#e4e0d4')                                 # 走廊天花板 + 日光灯
    line(d, (K1, 29, W, 29), '#c4beb0')
    for x in range(C0 + 20, W - 40, 70):
        rect(d, (x, 10, x + 36, 13), '#fffaf0')
        line(d, (x, 14, x + 36, 14), '#b8b2a4')
    rect(d, (C0, 30, W, GC), '#f0ece0')
    rect(d, (C0, 30, W, 64), '#f0ece0')                                # 上墙
    rect(d, (C0, 30, W, 34), '#d8d2c4')
    rect(d, (C0, 104, W, GC), '#9ab0a4')                               # 腰墙（灰绿）
    line(d, (C0, 104, W, 104), '#b8ccc0')
    rect(d, (C0, GC - 4, W, GC), '#6a8478')
    # 大窗（外面是中庭的天和树）
    for wx in range(C0 + 6, W - 40, 56):
        rect(d, (wx, 64, wx + 48, 104), '#c8ccd0')
        rect(d, (wx + 2, 66, wx + 46, 102), '#9cc8e8')
        rect(d, (wx + 2, 88, wx + 46, 102), '#6e9e6a')
        for k in range(4):
            ellipse(d, (wx + 2 + k * 12, 82, wx + 14 + k * 12, 94), '#4e7e4a')
        line(d, (wx + 24, 64, wx + 24, 104), '#c8ccd0')
        for k in range(0, 44, 9):
            line(d, (wx + 4 + k, 68, wx + 8 + k, 72), '#e0f0fa')
        line(d, (wx, 105, wx + 48, 105), '#7a948a')
    rect(d, (C0, 62, W, 64), '#c8ccd0')
    # 公告栏 + 消防栓箱 + 班牌
    rect(d, (C0 + 4, 36, C0 + 50, 58), '#8a6a4a')
    rect(d, (C0 + 6, 38, C0 + 48, 56), '#c8a878')
    for k, (ox, oy, w_, h_) in enumerate(((2, 2, 12, 9), (16, 1, 10, 13), (28, 3, 12, 8), (6, 12, 14, 5))):
        rect(d, (C0 + 6 + ox, 38 + oy, C0 + 6 + ox + w_, 38 + oy + h_), ['#fffaf0', '#f4e8c8', '#e8f0f8', '#fff0f0'][k])
        px(d, C0 + 6 + ox + w_ // 2, 38 + oy, '#e84a3a')
    rect(d, (C0 + 112, 106, C0 + 128, 126), '#d8303a')
    rect(d, (C0 + 114, 108, C0 + 126, 124), '#e84a4a')
    ellipse(d, (C0 + 117, 111, C0 + 123, 117), '#f4f0e8')
    rect(d, (C0 + 112, 102, C0 + 128, 104), '#f0c030')
    # 教室的拉门 + 门上的班牌 “2-B”
    for dx_ in (C0 + 150,):
        rect(d, (dx_, 66, dx_ + 34, GC), '#b8946a')
        rect(d, (dx_ + 2, 68, dx_ + 16, GC), '#c8a47a')
        rect(d, (dx_ + 18, 68, dx_ + 32, GC), '#c8a47a')
        rect(d, (dx_ + 4, 72, dx_ + 14, 86), '#9cc8e8')
        rect(d, (dx_ + 20, 72, dx_ + 30, 86), '#9cc8e8')
        rect(d, (dx_ + 6, 38, dx_ + 28, 46), '#f4f4f0')
        rect(d, (dx_ + 6, 38, dx_ + 28, 39), '#6a8478')
        letters(d, dx_ + 12, 40, '2-B', '#2a2a30')
    # 最右：楼梯口（暗一点，墙往里退）
    rect(d, (W - 40, 30, W, GC + 2), '#cfc8b8')
    for i in range(8):
        y0 = GC - i * 10
        rect(d, (W - 36 + i * 4, y0 - 2, W, y0), '#e4ded0')
        line(d, (W - 36 + i * 4, y0, W, y0), '#a8a090')
    rect(d, (W - 40, 30, W - 38, GC + 2), '#a8a090')
    # 走廊地板：亮漆的灰绿地胶，窗户的倒影
    rect(d, (C0 - 6, GC, W, 180), '#b8c4b8')
    for y in range(GC + 6, 180, 9):
        line(d, (C0 - 6, y, W, y), '#a8b4a8')
    for wx in range(C0 + 6, W - 40, 56):
        for y in range(GC + 3, 158, 2):
            line(d, (wx + 6 + (y - GC) // 3, y, wx + 40 - (y - GC) // 4, y), '#cad6cc')
    line(d, (C0 - 6, GC, W, GC), '#8aa094')
    # 仓库和走廊之间：楼的外墙 + 入口（玻璃门）
    rect(d, (K1 + 6, 30, C0, GC + 2), '#ece6da')
    # 地上的接缝（仓库 → 走廊）
    line(d, (K1, GK, K1, 180), '#7a7670')
    line(d, (O1, GO, O1, 180), '#8a7a60')
    # 窗户投到走廊地上的光块
    yy, xx = np.mgrid[0:180, 0:W]
    f = np.zeros((180, W))
    for wx in range(C0 + 6, W - 40, 56):
        dx = (xx - (wx + 34)) / 26
        dy = (yy - 150) / 12
        f = np.maximum(f, np.clip(1 - np.hypot(dx, dy), 0, 1) * .55)
    f = np.maximum(f, np.clip(1 - np.hypot((xx - 316) / 30, (yy - 150) / 14), 0, 1) * .5)   # 仓库高窗那一束
    glow = glow_from_field(f, '#3a3828', levels=4)
    layers = {'far': far, 'near': near, 'glow': glow}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(goal=[58, 150], tires=[150, 152], tree=[206, 146], shed_door=[K0 + 4, 150], vault_box=[jx + 20, 146],
                             mats=[mx + 22, 146], sit=[mx + 22, GK - 26], ball_cart=[bx + 13, 146], hanger=[hx, hy + 6],
                             shed_window=[316, 57], corridor_in=[C0 + 6, 150], board=[C0 + 27, 47], hydrant=[C0 + 120, 146],
                             door_2b=[C0 + 167, 146], stairs=[W - 20, 146], josuke_window=[W - 112, 84],
                             zones=dict(playground=[0, O1], shed=[K0, K1], corridor=[K1, W]), walk_x=[8, 628]),
                layers=[{'type': 'pano', 'image': 'bg/middle_school/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/middle_school/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'glow', 'image': 'bg/middle_school/glow', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.18, 'key': 'pm'}],
                fg=[])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    preview('middle_school', {'all': pv}, ['all'], W)
    return save_layers('middle_school', layers, meta)


SCENES = {'ghost_alley': ghost_alley, 'morioh_blocks': morioh_blocks, 'budogaoka_bank': budogaoka_bank, 'rooftops': rooftops,
          'st_gentleman': st_gentleman, 'middle_school': middle_school}


def main(keys):
    meta = LIB.load_json(META, {}) or {}
    for k in keys or SCENES:
        meta[k] = SCENES[k]()
        print('背景', k)
    LIB.save_json(META, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
