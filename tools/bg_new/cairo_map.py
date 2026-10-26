# -*- coding: utf-8 -*-
r"""cairo_map —— 第10章「开罗」：找馆推理用的开罗旧地图插画（全屏 320×180 静态，给剧情 T.show({ bg: 'cairo_map' }) 用）。
2026-10-19 第三轮背景重画（interiors 组）新画。共用零件在 interior_parts.py。归包：bg_ch10（主代理登记）。

一张摊在木桌上的旧地图（x 8–244）：发黄的纸、四边磨毛 / 缺角、对折两次的折痕（竖一道 x 126、横两道 y 66 / 122）、两个咖啡渍的圈。
  尼罗河从下往上穿过（偏左，蜿蜒，中间一个沙洲岛 + 两座桥），河西是西岸（田地的格子 + 左下角三座小金字塔），
  河东从上到下分成城北 / 老城 / 城南三块（街道网、几个清真寺的小圆顶），几块之间一道虚线的区界。
  ⚠ 不写字：剧情用字库在 north / south / old_town / west_bank 四个锚点写两个字的区名——每个锚点周围留了 26×12 的干净浅色纸面；
  推理答对时剧情在 north 画红圈（椭圆描边）：north 周围 44×24 里没有深色杂物。左上一个只有箭头和星的指北针（不写 N）、左下一段比例尺。
  右边（x 248–316）是木桌：三张线索小卡的位置（anchors.cards = 卡片中心）——背景只画一颗图钉 + 一块淡淡的影（卡是剧情画的）。
图层：near  static（整张，不透明）；全静态。
锚点：north [176,34]、south [176,148]、old_town [190,96]、west_bank [52,96]（四块的中心 = 写区名的地方）、
  cards [[282,36],[282,88],[282,140]]（三张卡的中心）；另外多导出：card_boxes（三张卡的框 52×44）、label_boxes（四块写字的干净框）、
  nile（河的中线，从下往上 7 个点）、walk_x [0,320]。
单独运行：python -B tools/bg_new/cairo_map.py → tools/bg_new/_preview/ch10/after/cairo_map_solo.png
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
WALK = (150, 176)
PAPER_BOX = (8, 8, 244, 172)
NORTH, SOUTH, OLD, WEST = (176, 34), (176, 148), (190, 96), (52, 96)
LABEL = (13, 6)                     # 写字的干净框半宽 / 半高（26×12）
CIRCLE = (22, 12)                   # 红圈的半宽 / 半高（north 周围不放深色东西）
CARDS = [(282, 36), (282, 88), (282, 140)]
CARD_HALF = (26, 22)
NILE = [(104, 172), (98, 150), (106, 126), (100, 100), (108, 74), (102, 46), (110, 8)]   # 河中线（下 → 上）

INK = (60, 40, 30)
PAPER = (226, 208, 166)
PAPER_D = (210, 188, 144)
PAPER_L = (236, 222, 186)
LINE = (150, 120, 84)               # 街道 / 区界的墨线（褪色的棕）
WATER = (120, 160, 170)
WATER_D = (90, 130, 146)
FIELD = (190, 186, 132)
WOOD = [(70, 44, 30), (98, 64, 42), (120, 82, 54), (146, 104, 70)]

ANCHORS = dict(north=list(NORTH), south=list(SOUTH), old_town=list(OLD), west_bank=list(WEST),
               cards=[list(c) for c in CARDS],
               card_boxes=[[x - CARD_HALF[0], y - CARD_HALF[1], x + CARD_HALF[0] - 1, y + CARD_HALF[1] - 1] for (x, y) in CARDS],
               label_boxes={k: [x - LABEL[0], y - LABEL[1], x + LABEL[0], y + LABEL[1]]
                            for k, (x, y) in (('north', NORTH), ('south', SOUTH), ('old_town', OLD), ('west_bank', WEST))},
               nile=[list(p) for p in NILE], walk_x=[0, 320])


def nile_x(y):
    """河中线在 y 处的 x（NILE 折线插值，再加一点平滑的弯）。"""
    pts = NILE
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if y1 <= y <= y0:
            u = (y0 - y) / max(1, (y0 - y1))
            u = u * u * (3 - 2 * u)
            return x0 + (x1 - x0) * u
    return pts[-1][0]


def keep_clear(x, y):
    """写字框 / 红圈范围：街道、图标都不画进来。"""
    for (cx, cy) in (SOUTH, OLD, WEST):
        if abs(x - cx) <= LABEL[0] + 1 and abs(y - cy) <= LABEL[1] + 1:
            return True
    cx, cy = NORTH
    return ((x - cx) / (CIRCLE[0] + 2)) ** 2 + ((y - cy) / (CIRCLE[1] + 2)) ** 2 <= 1.0


def table_and_paper():
    """木桌（横纹木板）+ 地图纸（发黄、四边磨毛、右上缺一角）。"""
    im = P.new(PW, H, WOOD[2])
    d = ImageDraw.Draw(im)
    P.planks_h(d, 0, 0, PW - 1, H - 1, WOOD, seed=5, ph=9, plen=(60, 140))
    a = np.array(im)
    x0, y0, x1, y1 = PAPER_BOX
    yy, xx = np.mgrid[0:H, 0:PW]
    edge = np.minimum.reduce([xx - x0, x1 - xx, yy - y0, y1 - yy]).astype(np.float32)
    rough = np.array([[hash01(x, y, 4) for x in range(PW)] for y in range(H)])
    paper = (edge >= 0) & ~((edge < 2) & (rough < 0.35))
    paper &= ~((xx > x1 - 12) & (yy < y0 + 12) & ((xx - (x1 - 12)) > (yy - y0)))   # 右上缺一个小三角
    shadow = np.zeros_like(paper)
    shadow[2:, 2:] = paper[:-2, :-2]
    a[shadow & ~paper, :3] = (a[shadow & ~paper, :3] * 0.62).astype(np.uint8)       # 纸落在桌上的影
    n = P.A._fbm(PW, H, 18, seed=3)
    for y in range(H):
        for x in range(PW):
            if paper[y, x]:
                c = PAPER
                if n[y, x] > 0.62:
                    c = PAPER_D
                elif n[y, x] < 0.36:
                    c = PAPER_L
                if edge[y, x] < 3:
                    c = dk(c, 0.9)
                a[y, x, :3] = c
    im = Image.fromarray(a, 'RGBA')
    return im, paper


def draw_map(im, paper):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = PAPER_BOX
    # 西岸：田地的格子（淡绿黄）+ 灌溉渠
    for y in range(y0 + 4, y1 - 4):
        nx = int(nile_x(y))
        for x in range(x0 + 4, nx - 7):
            if keep_clear(x, y):
                continue
            if ((x // 9) + (y // 7)) % 2 == 0 and hash01(x // 9, y // 7, 2) < 0.45:
                px(d, x, y, mix(PAPER, FIELD, 0.7))                                      # 田块（淡）
            if (x % 9 == 0 or y % 7 == 0) and hash01(x, y, 6) < 0.6:
                px(d, x, y, mix(PAPER_D, LINE, 0.35))                                    # 田埂 / 渠
    for (bx, by, s) in ((26, 150, 5), (36, 152, 4), (20, 154, 3)):                     # 左下：三座小金字塔
        for k in range(s):
            hl(d, bx - k, bx + k, by - s + k, (196, 160, 104) if k < s - 1 else (170, 136, 86))
            px(d, bx + k, by - s + k, (150, 116, 70))
    # 尼罗河：浅蓝的河面（宽 9）、两岸一道深一点的线；中间一个沙洲岛；两座桥
    for y in range(y0, y1 + 1):
        nx = nile_x(y)
        hw = 4 + (1 if 80 < y < 112 else 0)
        for x in range(int(nx - hw), int(nx + hw) + 1):
            px(d, x, y, WATER)
        px(d, int(nx - hw) - 1, y, WATER_D)
        px(d, int(nx + hw) + 1, y, WATER_D)
        if y % 6 == 0:
            px(d, int(nx) - 1, y, (170, 200, 204))
    for y in range(86, 106):                                                            # 沙洲岛
        nx = nile_x(y)
        w = int(2 * math.sin(math.pi * (y - 86) / 20) + 0.5)
        hl(d, int(nx) - w, int(nx) + w, y, (196, 186, 134))
    for by in (60, 116):                                                                # 两座桥
        nx = int(nile_x(by))
        hl(d, nx - 7, nx + 7, by, (110, 84, 60))
        hl(d, nx - 7, nx + 7, by + 1, (180, 150, 110))
    # 河东：街道网（城北疏、老城密、城南中等）+ 几个清真寺圆顶
    for y in range(y0 + 4, y1 - 4):
        nx = int(nile_x(y))
        for x in range(nx + 8, x1 - 4):
            if keep_clear(x, y):
                continue
            grid = 12 if y < 66 else (5 if y < 122 else 8)
            off = (y // 23) * 3
            if (x + off) % grid == 0 or (y % grid == 0 and hash01(x // grid, y, 7) < 0.85):
                if hash01(x, y, 11) < 0.92:
                    px(d, x, y, LINE)
    # 老城里的几条弯巷子
    for k in range(5):
        sx, sy = 140 + k * 18, 74 + int(hash01(k, 3) * 40)
        for q in range(14):
            u, v = sx + q, sy + int(2 * math.sin(q * 0.6 + k))
            if not keep_clear(u, v) and u < x1 - 4:
                px(d, u, v, dk(LINE, 0.85))
    for (mx, my) in ((150, 84), (212, 110), (226, 80), (140, 140), (210, 52), (230, 160)):     # 清真寺小圆顶
        if keep_clear(mx, my):
            continue
        d.pieslice((mx - 3, my - 3, mx + 3, my + 3), 180, 360, fill=P.C((170, 140, 100)), outline=P.C(INK))
        hl(d, mx - 3, mx + 3, my, INK)
        vl(d, mx + 4, my - 6, my, INK)
        px(d, mx + 4, my - 7, (170, 140, 100))
    # 区界：虚线（河东：y 66 / 122 两道横的；河本身就是西岸的界）
    for by in (68, 124):
        for x in range(int(nile_x(by)) + 7, x1 - 4):
            if (x // 3) % 2 == 0 and not keep_clear(x, by):
                px(d, x, by, (140, 70, 60))
                px(d, x, by + 1, (180, 120, 100))
    # 写字的地方：一块干净的浅色纸面（比周围亮一点、四角圆），让字读得清
    for (cx, cy) in (NORTH, SOUTH, OLD, WEST):
        d.rounded_rectangle((cx - LABEL[0], cy - LABEL[1], cx + LABEL[0], cy + LABEL[1]), radius=3,
                            fill=P.C(PAPER_L))
    # 折痕：竖一道、横两道（一条暗线 + 一条亮线，像纸被折过又摊开）
    a = np.array(im)
    for x in (126,):
        for y in range(H):
            if paper[y, x]:
                a[y, x, :3] = (a[y, x, :3] * 0.86).astype(np.uint8)
                a[y, x + 1, :3] = np.minimum(255, a[y, x + 1, :3].astype(int) + 14).astype(np.uint8)
    for y in (66, 122):
        for x in range(PW):
            if paper[y, x]:
                a[y, x, :3] = (a[y, x, :3] * 0.86).astype(np.uint8)
                a[y + 1, x, :3] = np.minimum(255, a[y + 1, x, :3].astype(int) + 14).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    # 咖啡渍：两个不完整的圈（一深一浅）
    for (cx, cy, r) in ((214, 150, 11), (70, 36, 8)):
        for k in range(0, 360, 4):
            if hash01(cx, k, 9) < 0.82:
                ang = math.radians(k)
                u, v = int(round(cx + r * math.cos(ang))), int(round(cy + r * 0.8 * math.sin(ang)))
                if not keep_clear(u, v):
                    px(d, u, v, (176, 130, 84))
                    if k % 12 == 0:
                        px(d, u, v + 1, (196, 156, 104))
    # 指北针（只有箭头 + 一颗星，不写 N）
    cx, cy = 24, 26
    d.polygon([(cx, cy - 9), (cx + 3, cy), (cx, cy - 2), (cx - 3, cy)], fill=P.C((150, 50, 40)), outline=P.C(INK))
    d.polygon([(cx, cy + 7), (cx + 3, cy), (cx, cy + 2), (cx - 3, cy)], fill=P.C((210, 190, 150)), outline=P.C(INK))
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), outline=P.C(LINE))
    # 比例尺
    for k in range(4):
        rect(d, 16 + k * 8, 164, 23 + k * 8, 166, INK if k % 2 == 0 else PAPER_L)
    rect(d, 16, 164, 47, 166, None, outline=INK)


def card_spots(d):
    """右边木桌上三张线索小卡的位置：四个黑色的相角（L 形，卡片插进去的地方）+ 顶上一颗红头图钉。"""
    for (cx, cy) in CARDS:
        hw, hh = CARD_HALF
        x0, y0, x1, y1 = cx - hw, cy - hh, cx + hw - 1, cy + hh - 1
        for (u, v, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            for k in range(5):
                px(d, u + sx * k, v, (40, 30, 26))
                px(d, u, v + sy * k, (40, 30, 26))
            px(d, u + sx, v + sy, (40, 30, 26))
        d.ellipse((cx - 3, cy - hh - 3, cx + 3, cy - hh + 3), fill=P.C((196, 40, 40)), outline=P.C(INK))
        px(d, cx - 1, cy - hh - 1, (250, 150, 140))
        vl(d, cx, cy - hh + 3, cy - hh + 5, (200, 200, 200))


@lru_cache(maxsize=1)
def map_img():
    im, paper = table_and_paper()
    table = np.array(im)
    draw_map(im, paper)
    a = np.array(im)                                                    # 画出纸边的街道 / 河：纸外面还原成桌面
    a[~paper] = table[~paper]
    im = Image.fromarray(a, 'RGBA')
    card_spots(ImageDraw.Draw(im))
    return P.opaque(im)


def specs():
    return [dict(t='static', name='near', img=map_img())]


def export(ex, BJ):
    S = specs()
    layers, fg = P.export_layers(ex, BJ, S)
    st = ex.stage(PW, GROUND, WALK, layers, fg, {k: (list(v) if isinstance(v, (list, tuple)) else v)
                                                 for k, v in ANCHORS.items()})
    if ex.check_on:
        _checks(ex, BJ, st, S)
    return st


def _checks(ex, BJ, st, S):
    im = map_img()
    cfg = dict(name='开罗地图插画', pw=PW, walk=WALK, states=[{}],
               opaque=[('整张不透明', im, (0, 0, PW, H))], binary=[('只有 0 / 255 两种透明度', im)],
               stand=[], inside=['north', 'south', 'old_town', 'west_bank', 'cards', 'card_boxes'])
    P.std_checks(ex, BJ, st, S, cfg)
    a = np.array(im)[..., :3].astype(int)
    bad = 0
    for (cx, cy) in (NORTH, SOUTH, OLD, WEST):
        sub = a[cy - LABEL[1] + 1:cy + LABEL[1], cx - LABEL[0] + 1:cx + LABEL[0]]
        bad += int((np.abs(sub - np.array(PAPER_L)).max(-1) > 0).sum())
    ex.checked('四个区名锚点周围 %d×%d 是干净的浅色纸面（不是纸色的像素）' % (LABEL[0] * 2 - 1, LABEL[1] * 2 - 1), bad)
    lum = a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11
    cx, cy = NORTH
    yy, xx = np.mgrid[0:H, 0:PW]
    ring = (((xx - cx) / CIRCLE[0]) ** 2 + ((yy - cy) / CIRCLE[1]) ** 2 <= 1.0)
    ex.checked('north 红圈范围（%d×%d 椭圆）里没有深色杂物（亮度 < 150 的像素）' % (CIRCLE[0] * 2, CIRCLE[1] * 2),
               int((ring & (lum < 150)).sum()))
    ex.checked('四块区域：west_bank 在河西、另外三块在河东（不对的块数）',
               int(WEST[0] >= nile_x(WEST[1]) - 6) + sum(int(x <= nile_x(y) + 6) for (x, y) in (NORTH, SOUTH, OLD)))
    ex.checked('三张卡的框在纸外的木桌上、不出画面', sum(int(not (PAPER_BOX[2] < x - CARD_HALF[0] and x + CARD_HALF[0] <= PW
                                                           and 0 <= y - CARD_HALF[1] - 4 and y + CARD_HALF[1] <= H))
                                                 for (x, y) in CARDS))


if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch10', 'after')
    os.makedirs(od, exist_ok=True)
    map_img().convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'cairo_map_solo.png'))
    print('ok')
