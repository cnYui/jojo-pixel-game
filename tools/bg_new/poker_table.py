# -*- coding: utf-8 -*-
r"""poker_table —— 第10章「开罗」：扑克牌桌的俯视插画（全屏 320×180 静态，给剧情 T.show({ bg: 'poker_table' }) 用）。
2026-10-19 第三轮背景重画（interiors 组）新画。共用零件在 interior_parts.py。归包：bg_ch10（主代理登记）。

俯视的绿呢牌桌：四周一圈深红棕的皮包边（四角圆）、桌子外面露出一点暗地板；吊灯在正上方，桌面中间一大圈亮、往外一档档暗。
  上方（y 0–40）是达比那一侧：两只手 + 酒红袖子 + 白袖口（金袖扣），右手边三摞筹码（红 / 蓝 / 白），左手边一副扣着的牌（发牌用的牌堆）
  下方（y 150–180）是承太郎那一侧：深蓝校服袖子 + 金扣子，一只手搭在桌边
  桌面上印着的空牌位（剧情画牌）：上下各 5 个淡淡的方框（anchors.d_cards / j_cards，间距 16），中间一个下注圈（anchors.pot）
  右上一个金框的头像框（anchors.face = 框心；头像 32×32 放得下）+ 框左边三颗汗滴的位置（anchors.sweat）
  左边桌角一只铜烟灰缸（雪茄）、右下桌角一杯加冰的威士忌
剧情画在上面的（背景不画）：两边的 10 张牌（prop.card 11×14，pivot 中心）、底池里一枚枚叠上去的筹码（prop.chip / soul_chip 9×9）、
  达比的头像、0–3 颗汗滴。

图层：near  static（整张，不透明）。插画背景全静态（规格允许），没有会动的东西。
锚点：j_cards（承太郎 5 个牌位的中心）、d_cards（达比 5 个）、pot（下注圈中心）、face（头像框中心）、sweat（第一颗汗滴的位置）；
  另外多导出：face_box [270,22,303,55]（框里面 34×34）、face_foot [287,55]（按“脚点 / 底中”画头像时放这里）、
  sweat_list（三颗汗滴，从上往下）、pot_box（下注圈）、walk_x [0,320]。
单独运行：python -B tools/bg_new/poker_table.py → tools/bg_new/_preview/ch10/after/poker_table_solo.png
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import hash01, hrange, mix, paste  # noqa: E402


def _parts():
    key = 'bg_new_interior_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'interior_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect

W, H = 320, 180
PW = 320
GROUND = 156
WALK = (150, 176)             # 插画没有可走带，照通用合同给一个值
RAIL = (4, 10, 316, 172)      # 皮包边外沿
FELT_BOX = (14, 22, 306, 160) # 绿呢
SLOT_XS = [128, 144, 160, 176, 192]
D_Y, J_Y = 56, 126            # 达比 / 承太郎的牌位中心 y（顶上对白框盖到 y 46；底下对白框从 y ~134 起，牌位都在中间）
POT = (160, 96)             # 下注圈：往上叠 12 枚（每枚 2 px）也碰不到达比的牌位
FACE_BOX = (270, 22, 303, 55)
FACE = ((FACE_BOX[0] + FACE_BOX[2] + 1) // 2, (FACE_BOX[1] + FACE_BOX[3] + 1) // 2)
SWEAT = [(262, 26), (260, 34), (262, 42)]

INK = (18, 14, 14)
FELT = [(14, 52, 34), (20, 70, 46), (28, 88, 58), (36, 106, 70), (46, 124, 82), (58, 142, 94)]
LEATHER = [(40, 16, 14), (70, 28, 24), (98, 42, 34), (128, 64, 50)]
SLEEVE_D = [(62, 14, 26), (96, 24, 40), (128, 40, 56)]           # 达比的酒红西装
SLEEVE_J = [(20, 24, 50), (34, 40, 78), (52, 60, 104)]           # 承太郎的深蓝校服
SKIN = [(176, 120, 92), (214, 160, 124), (238, 196, 160)]
GOLD = [(120, 84, 30), (186, 140, 56), (236, 200, 110)]

ANCHORS = dict(j_cards=[[x, J_Y] for x in SLOT_XS], d_cards=[[x, D_Y] for x in SLOT_XS], pot=list(POT),
               face=list(FACE), sweat=list(SWEAT[0]), face_box=list(FACE_BOX), face_foot=[FACE[0], FACE_BOX[3]],
               sweat_list=[list(s) for s in SWEAT], pot_box=[POT[0] - 17, POT[1] - 12, POT[0] + 17, POT[1] + 12],
               walk_x=[0, 320])


def felt_base():
    """桌面：吊灯在正上方——以 (160, 92) 为心一圈圈往外暗（6 档，档的交界按 Bayer 抖一窄条）+ 绒面的细毛点。"""
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    dd = np.hypot((xx - 160) / 1.55, (yy - 92) / 1.0)
    lvl = np.clip(1.0 - dd / 120.0, 0, 1)
    q = P.quant(lvl, 5, P.bayer(PW, H), jitter=0.5)
    idx = np.clip((q * 5).round().astype(int), 0, 5)
    a = np.zeros((H, PW, 4), np.uint8)
    pal = np.array(FELT, np.uint8)
    a[..., :3] = pal[idx]
    a[..., 3] = 255
    noise = np.array([[hash01(x, y, 9) for x in range(PW)] for y in range(H)])
    dark = noise < 0.06
    a[dark, :3] = (a[dark, :3].astype(np.float32) * 0.86).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def rail_and_floor(im):
    """桌子外面一点暗木地板（四个角）+ 一圈皮包边（圆角、上亮下暗、一排包钉）+ 包边内侧一道木线。"""
    d = ImageDraw.Draw(im)
    a = np.array(im)
    x0, y0, x1, y1 = RAIL
    m_out = np.ones((H, PW), bool)
    mm = Image.new('L', (PW, H), 0)
    ImageDraw.Draw(mm).rounded_rectangle((x0, y0, x1, y1), radius=26, fill=255)
    m_out = np.array(mm) == 0
    for y in range(H):
        for x in range(PW):
            if m_out[y, x]:
                a[y, x, :3] = (46, 30, 24) if (x // 2 + y // 9) % 5 else (36, 24, 20)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    fx0, fy0, fx1, fy1 = FELT_BOX
    ring = Image.new('L', (PW, H), 0)
    rd = ImageDraw.Draw(ring)
    rd.rounded_rectangle((x0, y0, x1, y1), radius=26, fill=255)
    rd.rounded_rectangle((fx0, fy0, fx1, fy1), radius=16, fill=0)
    rm = np.array(ring) > 0
    a = np.array(im)
    yy, xx = np.mgrid[0:H, 0:PW]
    # 皮包边：鼓起来的一圈——靠外沿暗、中间亮、靠里沿再暗（光从上来，上半圈整体亮一档）
    dist_out = np.minimum.reduce([yy - y0, y1 - yy, xx - x0, x1 - xx]).astype(np.float32)
    w = np.where(yy < (y0 + y1) / 2, 1.0, 0.82)
    for y in range(H):
        for x in range(PW):
            if rm[y, x]:
                t = dist_out[y, x]
                c = LEATHER[1] if t < 2 else (LEATHER[3] if t < 5 else LEATHER[2])
                a[y, x, :3] = np.clip(np.array(c) * w[y, x], 0, 255)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((fx0 - 1, fy0 - 1, fx1 + 1, fy1 + 1), radius=17, outline=P.C((150, 104, 60)))   # 木线
    d.rounded_rectangle((fx0 - 2, fy0 - 2, fx1 + 2, fy1 + 2), radius=18, outline=P.C(INK))
    d.rounded_rectangle((x0, y0, x1, y1), radius=26, outline=P.C(INK))
    for x in range(40, 290, 12):                                                       # 包钉
        px(d, x, y0 + 3, GOLD[1])
        px(d, x + 6, y1 - 3, GOLD[0])
    for y in range(40, 150, 12):
        px(d, x0 + 3, y, GOLD[0])
        px(d, x1 - 3, y, GOLD[0])


def slots(d):
    """空牌位：上下各 5 个印在呢面上的细框（13×16，比牌大一圈）、下注圈（一圈细线 + 四个小菱形）。"""
    for y in (D_Y, J_Y):
        for x in SLOT_XS:
            rect(d, x - 6, y - 8, x + 6, y + 8, None, outline=(84, 160, 108))
            for (u, v) in ((x - 6, y - 8), (x + 6, y - 8), (x - 6, y + 8), (x + 6, y + 8)):
                px(d, u, v, (120, 190, 140))
    cx, cy = POT
    d.ellipse((cx - 17, cy - 12, cx + 17, cy + 12), outline=P.C((96, 176, 122)))
    d.ellipse((cx - 15, cy - 10, cx + 15, cy + 10), outline=P.C((60, 136, 90)))
    for (u, v) in ((0, -12), (17, 0), (0, 12), (-17, 0)):
        px(d, cx + u, cy + v, (190, 220, 160))


def chip_stack(d, x, y, n, col):
    """斜俯视的一摞筹码（圆柱）：侧面是筹码色的竖条（一枚 2 px，枚与枚之间一道暗缝、边上白色的边纹），
    顶上一枚椭圆（亮一点、一圈白点）；整摞外面一圈墨线。"""
    top = y - 2 * n
    rect(d, x - 4, top, x + 4, y, dk(col, 0.82))
    for k in range(n):
        yy = y - 2 * k
        hl(d, x - 4, x + 4, yy, dk(col, 0.6))
        for u in (-3, 0, 3):
            px(d, x + u, yy - 1, (238, 238, 232))
    vl(d, x - 4, top, y, lt(col, 0.2))
    d.ellipse((x - 4, top - 2, x + 4, top + 2), fill=P.C(lt(col, 0.15)))
    for (u, v) in ((-3, 0), (3, 0), (0, -2), (0, 2)):
        px(d, x + u, top + v, (246, 246, 240))
    px(d, x, top, lt(col, 0.4))
    vl(d, x - 5, top, y, INK)
    vl(d, x + 5, top, y, INK)
    hl(d, x - 4, x + 4, y + 1, INK)


def hand(d, hx, top, down, thumb_side, sk=SKIN):
    """一只手（俯视，手背朝上）：圆一点的手背 + 四根长短不一的手指（中间两根长、指节一个亮点）+ 大拇指在 thumb_side 那一边。
    down = 手指朝下（达比那一侧）/ 朝上（承太郎那一侧）。"""
    sgn = 1 if down else -1
    by0, by1 = (top, top + 7) if down else (top - 7, top)
    d.rounded_rectangle((hx - 7, by0, hx + 7, by1), radius=3, fill=P.C(sk[1]), outline=P.C(INK))
    hl(d, hx - 5, hx + 5, by0 + 1 if down else by1 - 1, sk[2])
    for k, L in enumerate((4, 6, 6, 4)):
        fx = hx - 6 + k * 3 + (1 if k > 1 else 0)
        y0 = by1 + 1 if down else by0 - L
        y1 = by1 + L if down else by0 - 1
        rect(d, fx, y0, fx + 1, y1, sk[1])
        vl(d, fx + 2, y0, y1, INK)
        px(d, fx, y1 if down else y0, sk[2])
        px(d, fx + 1, by1 if down else by0, sk[2])                                    # 指节
        hl(d, fx, fx + 1, y1 + 1 if down else y0 - 1, INK)
    tx = hx + 8 if thumb_side > 0 else hx - 10
    rect(d, tx, by0 + 2, tx + 2, by1 + (2 if down else -2), sk[1], outline=INK)
    px(d, tx + 1, by0 + 3, sk[2])


def darby_side(d):
    """上方：达比的两只手（指尖朝下伸到呢面上）、酒红袖子 + 白袖口 + 金袖扣；右手边三摞筹码、左手边一副扣着的牌。"""
    for (hx, mirror) in ((112, 1), (212, -1)):
        rect(d, hx - 9, 0, hx + 9, 20, SLEEVE_D[1], outline=INK)                    # 袖子（从画面外伸进来）
        vl(d, hx - 8, 1, 19, SLEEVE_D[2])
        vl(d, hx + 8, 1, 19, SLEEVE_D[0])
        for k in range(3):
            px(d, hx - 4 + k * 3, 6 + k * 4, SLEEVE_D[0])
        rect(d, hx - 8, 20, hx + 8, 24, (232, 232, 226), outline=INK)               # 白袖口
        hl(d, hx - 7, hx + 7, 21, (250, 250, 246))
        rect(d, hx + 4 * mirror - 1, 21, hx + 4 * mirror, 22, GOLD[2])               # 金袖扣
        hand(d, hx, 25, True, mirror)
    for i, (x, col, n) in enumerate(((240, (196, 40, 46), 6), (250, (40, 80, 180), 5), (245, (230, 228, 220), 4))):
        chip_stack(d, x, 40 + i * 3, n, col)
    for k in range(5):                                                                # 发牌用的牌堆（扣着，红色牌背）
        rect(d, 74 - k, 30 - k, 84 - k, 43 - k, (230, 226, 216), outline=INK)
    rect(d, 71, 27, 79, 38, (176, 30, 40))
    for y in range(28, 38, 2):
        for x in range(72 + (y // 2) % 2, 79, 2):
            px(d, x, y, (210, 70, 70))


def jotaro_side(d):
    """下方：承太郎的深蓝校服袖子 + 金扣子 + 一只手搭在桌边（手指往上）。"""
    hx = 222
    rect(d, hx - 10, 162, hx + 10, H - 1, SLEEVE_J[1], outline=INK)
    vl(d, hx - 9, 163, H - 1, SLEEVE_J[2])
    vl(d, hx + 9, 163, H - 1, SLEEVE_J[0])
    for bx in (hx - 5, hx + 1):
        px(d, bx, 168, GOLD[2])
        px(d, bx, 169, GOLD[0])
    hand(d, hx, 161, False, -1)


def props_(d):
    """左边桌角的铜烟灰缸（搁着一支雪茄，一缕灰）+ 右下桌角一杯加冰的威士忌（俯视：杯口一圈、琥珀色、两块冰）。"""
    cx, cy = 40, 116
    d.ellipse((cx - 9, cy - 7, cx + 9, cy + 7), fill=P.C(GOLD[1]), outline=P.C(INK))
    d.ellipse((cx - 6, cy - 4, cx + 6, cy + 4), fill=P.C((70, 60, 50)))
    hl(d, cx - 7, cx + 3, cy - 6, GOLD[2])
    rect(d, cx + 2, cy - 1, cx + 14, cy + 1, (110, 70, 40), outline=INK)
    hl(d, cx + 3, cx + 12, cy - 1, (150, 100, 60))
    rect(d, cx + 12, cy - 1, cx + 14, cy + 1, (190, 180, 170))
    px(d, cx + 15, cy, (250, 120, 50))
    gx, gy = 280, 140
    d.ellipse((gx - 8, gy - 8, gx + 8, gy + 8), fill=P.C((188, 196, 200)), outline=P.C(INK))
    d.ellipse((gx - 6, gy - 6, gx + 6, gy + 6), fill=P.C((196, 120, 40)))
    rect(d, gx - 3, gy - 3, gx, gy, (232, 236, 236))
    rect(d, gx + 1, gy, gx + 4, gy + 3, (214, 222, 226))
    px(d, gx - 5, gy - 4, (250, 250, 250))
    d.ellipse((gx - 9, gy + 7, gx + 9, gy + 11), outline=P.C(FELT[1]))          # 杯底在呢面上留的水圈


def face_frame(d):
    """右上的头像框：金色双线框（四角花饰），里面填暗绿呢（剧情把头像画进来）；框左边三颗汗滴的位置不画东西。"""
    x0, y0, x1, y1 = FACE_BOX
    rect(d, x0 - 3, y0 - 3, x1 + 3, y1 + 3, (30, 22, 18), outline=INK)
    P.gilt_frame(d, x0 - 3, y0 - 3, x1 + 3, y1 + 3, w=2)
    rect(d, x0, y0, x1, y1, (24, 40, 34))
    for (u, v) in ((x0 - 3, y0 - 3), (x1 + 3, y0 - 3), (x0 - 3, y1 + 3), (x1 + 3, y1 + 3)):
        rect(d, u - 1, v - 1, u + 1, v + 1, GOLD[2])
        px(d, u, v, GOLD[0])


def contact_shadows(im):
    """手 / 袖子 / 筹码 / 牌堆 / 杯子落在呢面上的影：往右下错 2 px，压暗一档。"""
    a = np.array(im).astype(np.float32)
    sh = np.zeros((H, PW), bool)
    for (x0, y0, x1, y1) in ((103, 25, 122, 39), (203, 25, 222, 39), (236, 33, 255, 47), (66, 26, 86, 45),
                             (31, 109, 56, 124), (272, 132, 290, 150), (212, 147, 231, 162)):
        sh[y0 + 2:y1 + 3, x0 + 2:x1 + 3] = True
    a[sh, :3] *= 0.8
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


@lru_cache(maxsize=2)
def table_img(bare=False):
    """bare=True：只有呢面 + 包边（自检“牌位 / 下注圈 / 头像框里是干净的”用）。"""
    im = felt_base()
    rail_and_floor(im)
    if bare:
        return im
    im = contact_shadows(im)
    d = ImageDraw.Draw(im)
    slots(d)
    darby_side(d)
    jotaro_side(d)
    props_(d)
    face_frame(d)
    return P.opaque(im)


def specs():
    return [dict(t='static', name='near', img=table_img())]


def export(ex, BJ):
    S = specs()
    layers, fg = P.export_layers(ex, BJ, S)
    st = ex.stage(PW, GROUND, WALK, layers, fg, {k: (list(v) if isinstance(v, (list, tuple)) else v)
                                                 for k, v in ANCHORS.items()})
    if ex.check_on:
        _checks(ex, BJ, st, S)
    return st


def _checks(ex, BJ, st, S):
    im = table_img()
    cfg = dict(name='牌桌插画', pw=PW, walk=WALK, states=[{}],
               opaque=[('整张不透明', im, (0, 0, PW, H))], binary=[('只有 0 / 255 两种透明度', im)],
               stand=[], inside=['j_cards', 'd_cards', 'pot', 'face', 'sweat', 'face_box', 'face_foot', 'sweat_list',
                                 'pot_box'])
    P.std_checks(ex, BJ, st, S, cfg)
    a = np.array(im)[..., :3].astype(int)
    b = np.array(table_img(True))[..., :3].astype(int)
    dirty = 0
    for y in (D_Y, J_Y):
        for x in SLOT_XS:
            dirty += int((np.abs(a[y - 7:y + 8, x - 5:x + 6] - b[y - 7:y + 8, x - 5:x + 6]).max(-1) > 0).sum())
    ex.checked('10 个牌位框里是干净的呢面（牌 11×14 放进去不压到别的东西）', dirty)
    ex.checked('牌位间距 ≥ 14（%d）' % (SLOT_XS[1] - SLOT_XS[0]), int(min(b_ - a_ for a_, b_ in zip(SLOT_XS, SLOT_XS[1:])) < 14))
    cx, cy = POT
    ring = P.new(PW, H)
    slots(ImageDraw.Draw(ring))                                   # 下注圈 / 牌位的细线本身不算“杂物”
    rm = np.array(ring)[..., 3] > 0
    col = (np.abs(a - b).max(-1) > 0) & ~rm
    ex.checked('下注圈往上叠 12 枚筹码的空间（x %d–%d、y %d–%d）干净、不碰达比的牌位' % (cx - 6, cx + 6, cy - 30, cy + 8),
               int(col[cy - 30:cy + 9, cx - 6:cx + 7].sum()) + int(cy - 30 <= D_Y + 8))
    x0, y0, x1, y1 = FACE_BOX
    inner = a[y0:y1 + 1, x0:x1 + 1]
    ex.checked('头像框里面 %d×%d ≥ 32×30、一色（头像放得下）' % (x1 - x0 + 1, y1 - y0 + 1),
               int((x1 - x0 + 1) < 32 or (y1 - y0 + 1) < 30) + int((inner != inner[0, 0]).any(-1).sum()))
    ex.checked('三颗汗滴的位置在头像框左边、是干净的呢面',
               sum(int((np.abs(a[sy - 2:sy + 3, sx - 2:sx + 3] - b[sy - 2:sy + 3, sx - 2:sx + 3]).max(-1) > 0).sum())
                   for (sx, sy) in SWEAT))
    ex.checked('牌位 / 下注圈都在上下对白框之间（y 48–132）', sum(1 for y in (D_Y - 8, J_Y + 8, cy - 30) if not 48 <= y <= 134))


if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch10', 'after')
    os.makedirs(od, exist_ok=True)
    table_img().convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'poker_table_solo.png'))
    print('ok')
