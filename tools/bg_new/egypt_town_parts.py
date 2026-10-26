# -*- coding: utf-8 -*-
r"""egypt_town_parts —— egypt-town 组（aswan_town / luxor_town / luxor_house）共用的零件。不是背景 key，本身不导出。
2026-10-18 第二轮背景重画（分工 20261018-164346-背景重画分工_第二轮.md）。

为什么单独一个文件：三张图在同一片地方（上埃及的阿斯旺 / 卢克索），墙的抹灰、木门、木格窗、遮阳棚、棕榈、背景路人、
阿拉伯文招牌的“样子”这些零件是一样的；放一处，三张图的光照方向（太阳一律在左上，影子往右下）和墨线粗细也就一致。
最底层的小工具（dk / lt / hl / vl / px / rect / mul_box / cast_shadow / mottle / haze / opaque / wire / _canopy …）直接借
varanasi_street.py（第4章，同一套像素画法），用和 bg_jojo.bg_new 一样的模块名加载，不改 sys.path 顺序。

里面有：
  调色                SKY / HAZE / 刷色墙（努比亚的蓝、黄、粉、青绿，卢克索的浅土黄）、木头、铁、布、棕榈、人的肤色和衣服
  墙                  plaster（抹灰 + 斑驳 + 水渍 + 墙脚返潮 + 裂缝）、brick_patch（掉了灰露出的土坯砖）、frieze（努比亚几何花纹带）、
                      lattice_parapet（三角孔的镂空女儿墙，孔是透明的）、crenels（三角 / 阶梯垛口）、spout（屋顶出水口 + 下面的水渍）
  屋顶                dome（土坯穹顶，左上亮）、vault（努比亚筒拱，端面看）
  门窗                door（木门：门套花纹、铁钉、门环、拱顶气窗）、crocodile（门楣上的鳄鱼标本）、plate（嵌在墙上的瓷盘）、
                      grille_window（小方窗 + 木格栅）、mashrabiya（挑出来的木格窗）、awning / valance（条纹布遮阳棚 + 会飘的波浪边）
  树                  palm_trunk / palm_crown（海枣树：菱形叶柄的树干、一圈下垂的羽状叶、枯叶、海枣串；crown 有 8 帧摆动）
  清真寺              minaret（方座 → 八角柱 → 阳台 + 栏杆 + 喇叭 → 圆柱 → 球顶 + 新月）
  小物件              lantern（铜灯笼）、jar / zir_stand（陶水罐 + 木架）、crate（木箱 / 椰枣枝箱）、sack、basket、bench、
                      round_table / chair / shisha / tea_glass（茶馆）、lamp_post、sign_ar（阿拉伯文招牌的样子，读不出字）
  动的                egypt_flag（埃及国旗，飘）、pigeon、felucca_img（尼罗河三角帆船）
  人                  person（背景路人：长袍 galabiya、黑长裙的妇女、头顶筐、小孩、坐着喝茶 / 抽水烟、蹲着）—— 事后整体压灰
  地面 / 光           sand_ground（压实的沙土路）、compress_band（可走带后面压对比）、ink_rim（剪影外沿 1 px 墨线）
  组装 / 自检         图层表 → compose（直接拼）/ export_layers（导出）走同一张表；common_checks（各张图共用的自检）
2026-10-19 第三轮补的（三张图都在用）：
  frame_of / auto_box / cached_frames   strip 的帧号、从画出来的东西算框、每帧只画一次的缓存
  hard_alpha                            烟、蒸汽这类软的东西 → 只有 0 / 255（Bayer 抖开）
  outer_rim                             只描和天连着的外轮廓（ink_rim 会把镂空女儿墙的小孔描黑填满）
  power_pole                            木电线杆（返回瓷瓶坐标拉电线）
  picto / leafy / bird_cage / bicycle    路牌白图标、给平涂树冠加叶子碎、墙上的鸟笼、靠墙的自行车
  soft_shadow / arch_mask / put_inside  地上的淡影、拱洞形状、把画好的“店里”按拱洞的形状贴进墙
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import io  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _load(name):
    """tools\\bg_new\\<name>.py，模块名和 bg_jojo.bg_new 一样（'bg_new_' + name），已经加载过就直接复用。"""
    key = 'bg_new_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


V = _load('varanasi_street')
C = A._c4
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, cast_shadow, mottle, haze, opaque = (V.mul_box, V.mul_mask, V.poly_mask, V.cast_shadow,
                                                                  V.mottle, V.haze, V.opaque)
wire, garland_pts, canopy, tile = V.wire, V.garland_pts, V._canopy, V._tile
SHADOW_MUL, SOFT_MUL = V.SHADOW_MUL, V.SOFT_MUL

W, H = 320, 180
N_ANIM, FPS_ANIM = 8, 4.0

# ============================================================ 调色
INK = (62, 42, 38)                 # 墨线：深棕（纯黑在白天的土坯墙边上太跳）
SKY_STOPS = [(56, 112, 192), (78, 138, 208), (116, 168, 220), (172, 198, 218), (234, 220, 190)]
HAZE = (228, 214, 188)             # 下午偏暖的空气色
DARK_IN = (56, 42, 42)             # 门洞 / 窗洞里
WOOD_HI, WOOD, WOOD_D, WOOD_K = (176, 124, 78), (134, 90, 56), (98, 64, 40), (66, 44, 30)
IRON, IRON_HI = (50, 48, 54), (98, 96, 104)
BRASS = ((120, 84, 36), (176, 132, 56), (222, 182, 90), (250, 226, 150))
# 刷色墙的底色（亮面 / 暗面在 wall_pal 里按底色推出来，所有墙同一个规则）
NUB_BLUE = (112, 166, 210)
NUB_SKY = (146, 192, 222)
NUB_YELLOW = (230, 190, 96)
NUB_OCHRE = (214, 160, 92)
NUB_PINK = (226, 160, 148)
NUB_TURQ = (96, 176, 168)
LIME = (236, 230, 214)             # 刷白
MUD = (202, 164, 118)              # 没刷色的土坯抹灰
SANDY = (226, 202, 156)            # 卢克索的浅土黄
SANDY_D = (206, 176, 128)
TERRA = (196, 118, 84)
DOOR_GREEN = (64, 134, 110)
DOOR_BLUE = (62, 116, 170)
DOOR_TEAL = (54, 140, 150)
DOOR_RED = (166, 70, 54)
PAINT_RED = (196, 64, 52)
PAINT_WHITE = (246, 242, 232)
PAINT_BLUE = (52, 104, 168)
ORANGE_C = ((255, 186, 70), (244, 140, 34), (206, 98, 22), (150, 66, 18))     # 橘子：高光 / 中 / 暗 / 深
CLOTH = [(206, 52, 64), (240, 190, 50), (52, 120, 190), (236, 120, 160), (78, 160, 96), (244, 132, 40),
         (140, 76, 168), (244, 238, 222), (30, 140, 150), (180, 40, 90)]
LEAF_D, LEAF, LEAF_M, LEAF_HI = (40, 82, 46), (60, 116, 56), (92, 150, 68), (146, 190, 92)
PALM_PAL = dict(trunk=((176, 136, 96), (144, 106, 72), (110, 80, 56), (76, 56, 42)),
                frond=((44, 92, 50), (62, 122, 58), (96, 156, 70), (150, 196, 96)),
                dry=((150, 116, 66), (120, 90, 54)), dates=((226, 140, 40), (180, 92, 32), (250, 190, 80)))
SKIN = ((150, 104, 76), (124, 84, 60), (100, 68, 50), (170, 124, 92))
HAIR = (36, 30, 32)
ROBES = [(236, 232, 222), (176, 198, 214), (172, 170, 162), (150, 114, 84), (90, 104, 140), (214, 204, 180),
         (120, 140, 120)]


def wall_pal(c):
    """刷色墙的四档：亮面（左沿、受光的线脚）、中（墙面）、暗面（右沿、檐下）、深（缝、洞口边）。"""
    return (lt(c, 0.24), tuple(c), dk(c, 0.82), dk(c, 0.62))


# ============================================================ 小工具
def ink_rim(im, col=INK, y1=H, only_up=True):
    """剪影外沿 1 px 墨线（照第4章：近景的屋顶 / 树冠 / 杆子对着天空那一圈描深色）：
    透明、但上 / 左 / 右有不透明像素的点涂成 col（only_up 时不往下描——下沿都是墙脚，贴着地）。"""
    a = np.array(im)
    op = a[..., 3] > 0
    nb = np.zeros_like(op)
    nb[:-1] |= op[1:]                                              # 下面一行不透明 → 这一点在剪影上沿
    nb[:, 1:] |= op[:, :-1]
    nb[:, :-1] |= op[:, 1:]
    if not only_up:
        nb[1:] |= op[:-1]
    m = nb & ~op
    m[y1:] = False
    a[m, :3] = col
    a[m, 3] = 255
    return Image.fromarray(a, 'RGBA')


def crack(d, x, y, n, seed, col):
    """一道细裂缝：往下走、左右随机拐。"""
    for k in range(n):
        px(d, x, y, col)
        y += 1
        r = hash01(seed, k, 5)
        x += -1 if r < 0.28 else (1 if r > 0.72 else 0)


def plaster(im, x0, x1, top, base, col, seed, streaks=2, cell=4, damp=5, cracks=2, edges=True):
    """土坯墙抹灰刷色（x1 不含）：底色 + fbm 斑驳 + 往下淌的水渍 + 墙脚返潮的暗带（damp 行，越往下越暗、上沿 Bayer 抖开）
    + 几道细裂缝；左沿亮、右沿暗（太阳在左上）。返回 ImageDraw。"""
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = wall_pal(col)
    rect(d, x0, top, x1 - 1, base, md)
    mottle(im, (x0, top, x1 - 1, base), md, dk(md, 0.93), lt(md, 0.09), seed, cell=cell, streaks=streaks)
    for k in range(damp):                                          # 返潮 + 溅上的泥
        lev = 1.0 - k / max(1, damp)
        mul_box(im, (x0, base - k, x1 - 1, base - k), (0.9, 0.87, 0.84), level=0.35 + 0.65 * lev)
    d = ImageDraw.Draw(im)
    for i in range(cracks):
        cx = int(hrange(x0 + 3, x1 - 4, seed, i, 31))
        cy = int(hrange(top + 4, base - 16, seed, i, 32))
        crack(d, cx, cy, int(hrange(4, 11, seed, i, 33)), seed + i, dk(md, 0.76))
    if edges:
        vl(d, x0, top, base, hi)
        vl(d, x1 - 1, top, base, sh)
    return d


def brick_patch(im, cx, cy, rx, ry, seed, brick=(170, 126, 88), mortar=(130, 96, 68)):
    """灰掉了一块露出里面的土坯砖：砖 2 行 + 1 行灰缝、竖缝错开，边缘不规则；断口左上一圈亮（抹灰的厚度）、右下暗。"""
    d = ImageDraw.Draw(im)
    rows = {}
    for yy in range(cy - ry, cy + ry + 1):
        v = (yy - cy) / max(1, ry)
        hw = rx * math.sqrt(max(0.0, 1 - v * v)) * hrange(0.75, 1.1, seed, yy, 1)
        a, b = int(round(cx - hw)), int(round(cx + hw * hrange(0.8, 1.05, seed, yy, 2)))
        if b < a:
            continue
        rows[yy] = (a, b)
        r = yy - (cy - ry)
        for xx in range(a, b + 1):
            c = brick
            if r % 3 == 2:
                c = mortar
            elif (xx + (r // 3) * 4) % 8 == 0:
                c = mortar
            elif hash01(seed, xx, yy, 3) < 0.16:
                c = dk(brick, 0.88)
            elif hash01(seed, xx, yy, 4) < 0.1:
                c = lt(brick, 0.1)
            px(d, xx, yy, c)
    for yy, (a, b) in rows.items():
        if yy - 1 not in rows:
            hl(d, a, b, yy - 1, lt(mortar, 0.55))
        px(d, a - 1, yy, lt(mortar, 0.5))
        px(d, b + 1, yy, dk(mortar, 0.8))
    if rows:
        yb = max(rows)
        a, b = rows[yb]
        hl(d, a, b + 1, yb + 1, dk(mortar, 0.82))


def frieze(d, x0, x1, y, h, kind, c1, c2=None, seed=0):
    """努比亚的几何花纹带（x0..x1 含，y..y+h−1）：tri 锯齿三角、zig 折线、diamond 菱形串、check 棋盘格、
    steps 阶梯金字塔、dots 点、chev 人字。c2 = 第二色（花纹里的点 / 描边）。"""
    if kind == 'tri':
        p = max(2, h) * 2
        for x in range(x0, x1 + 1):
            u = (x - x0) % p
            hh = u if u <= h else p - u
            for k in range(min(h, hh)):
                px(d, x, y + h - 1 - k, c1)
            if c2 is not None and u == h // 2 + h:
                px(d, x, y + 1, c2)
    elif kind == 'zig':
        p = max(2, h - 1) * 2
        for x in range(x0, x1 + 1):
            u = (x - x0) % p
            yy = y + (u if u < p // 2 else p - u)
            px(d, x, min(y + h - 1, yy), c1)
            if c2 is not None:
                px(d, x, min(y + h - 1, yy + 1), c2)
    elif kind == 'diamond':
        p = h + 1
        for x in range(x0, x1 + 1):
            u = (x - x0) % p
            r = abs(u - h // 2)
            for yy in range(y, y + h):
                v = abs(yy - (y + h // 2))
                if r + v == h // 2:
                    px(d, x, yy, c1)
                elif c2 is not None and r + v == 0:
                    px(d, x, yy, c2)
    elif kind == 'check':
        for x in range(x0, x1 + 1):
            for yy in range(y, y + h):
                if ((x - x0) // 2 + (yy - y) // 2) % 2 == 0:
                    px(d, x, yy, c1)
                elif c2 is not None:
                    px(d, x, yy, c2)
    elif kind == 'steps':
        p = h * 2 + 2
        for x in range(x0, x1 + 1):
            u = (x - x0) % p
            hh = min(u + 1, p - u - 1, h)
            hh = (hh + 1) // 2 * 2 if hh < h else h
            for k in range(max(0, hh)):
                px(d, x, y + h - 1 - k, c1)
    elif kind == 'dots':
        for x in range(x0 + 1, x1, 3):
            px(d, x, y + h // 2, c1)
            if c2 is not None:
                px(d, x + 1, y + h // 2, c2)
    elif kind == 'chev':
        p = h * 2
        for x in range(x0, x1 + 1):
            u = (x - x0) % p
            for yy in range(y, y + h):
                if (u + (yy - y)) % p == 0 or (u - (yy - y)) % p == 0:
                    px(d, x, yy, c1)
    if kind != 'dots' and c2 is not None and kind in ('tri', 'steps'):
        hl(d, x0, x1, y + h, c2)


def lattice_parapet(im, x0, x1, y, col, hole=4, period=6, coping=2):
    """努比亚镂空女儿墙：压顶 coping 行 → 一排三角孔（孔透明，看得到后面的天；孔上沿一道深影、下沿亮）→ 下面 2 行实墙。
    x0..x1 含；返回下沿 y。"""
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = wall_pal(col)
    yb = y + coping + hole + 2
    rect(d, x0, y, x1, yb - 1, md)
    hl(d, x0 - 1, x1 + 1, y, hi)
    hl(d, x0 - 1, x1 + 1, y + 1, md)
    hl(d, x0, x1, y + coping, sh)
    a = np.array(im)
    for x in range(x0 + 2, x1 - period + 2, period):
        for r in range(hole):
            yy = y + coping + 1 + r
            hw = r // 2 + (1 if r >= 1 else 0)
            cx = x + period // 2 - 1
            if (x // period) % 2:                                  # 一正一倒的三角
                hw = (hole - 1 - r) // 2 + (1 if r < hole - 1 else 0)
            for xx in range(cx - hw, cx + hw + 1):
                if x0 < xx < x1:
                    a[yy, xx, 3] = 0
    im.paste(Image.fromarray(a, 'RGBA'))
    a = np.array(im)
    holes = a[..., 3] == 0
    d = ImageDraw.Draw(im)
    for yy in range(y + coping, yb):
        for xx in range(x0 + 1, x1):
            if not holes[yy, xx]:
                if yy + 1 < im.height and holes[yy + 1, xx]:
                    px(d, xx, yy, kk)                              # 孔上沿：深
                elif holes[yy - 1, xx]:
                    px(d, xx, yy, hi)                              # 孔下沿：亮
                elif holes[yy, xx - 1]:
                    px(d, xx, yy, sh)
    hl(d, x0, x1, yb - 1, sh)
    vl(d, x0, y, yb - 1, hi)
    vl(d, x1, y, yb - 1, sh)
    return yb


def crenels(im, x0, x1, y, col, kind='tri', size=4, gap=2):
    """垛口：tri 三角（努比亚）/ step 阶梯（马穆鲁克清真寺的那种）/ round 圆头；y = 垛口底（站在墙顶上）。x0..x1 含。"""
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = wall_pal(col)
    p = size * 2 + gap
    for x in range(x0, x1 - size * 2 + 2, p):
        if kind == 'tri':
            for r in range(size):
                a, b = x + r, x + size * 2 - 2 - r
                hl(d, a, b, y - 1 - r, md)
                px(d, a, y - 1 - r, hi)
                px(d, b, y - 1 - r, sh)
        elif kind == 'step':
            w = size * 2 - 1
            for r in range(size + 2):
                inset = (r // 2) * (1 if r >= 2 else 0)
                a, b = x + inset, x + w - 1 - inset
                if b < a:
                    break
                hl(d, a, b, y - 1 - r, md)
                px(d, a, y - 1 - r, hi)
                px(d, b, y - 1 - r, sh)
        else:
            w = size * 2 - 1
            rect(d, x, y - size, x + w - 1, y - 1, md)
            d.pieslice((x, y - size - w // 2 - 1, x + w - 1, y - size + w // 2), 180, 360, fill=C(md))
            vl(d, x, y - size, y - 1, hi)
            vl(d, x + w - 1, y - size, y - 1, sh)


def spout(im, x, y, L=5, wood=(120, 86, 56), stain_len=14, wall=None):
    """屋顶出水口（一截木槽 / 陶管从墙顶伸出来，朝右）+ 下面墙上一道往下淌的深色水渍。"""
    d = ImageDraw.Draw(im)
    if wall is not None and stain_len:
        for k in range(stain_len):
            if hash01(x, y, k, 7) < 1.0 - k / stain_len * 0.75:
                px(d, x + L - 1 + (1 if k > stain_len // 2 else 0), y + 2 + k, dk(wall, 0.8))
    hl(d, x, x + L, y, lt(wood, 0.2))
    hl(d, x, x + L, y + 1, dk(wood, 0.75))
    px(d, x + L, y + 1, dk(wood, 0.5))


# ============================================================ 屋顶
def dome(im, cx, base, r, col, seed=0, hgt=None, vents=0, finial=None, courses=True, drum=2):
    """土坯穹顶（侧视：半个椭圆，宽 2r+1、高 hgt）：法线和左上的光点乘分 4 档；每 3 行一道浅浅的砌层；下沿一圈鼓座（drum 行）；
    vents = 顶上开的小通风孔（个数）；finial = 顶上一个小尖（颜色）。返回顶点 y。"""
    d = ImageDraw.Draw(im)
    hgt = hgt or int(round(r * 0.92))
    hi, md, sh, kk = wall_pal(col)
    L = np.array((-0.62, -0.55, 0.56))
    L /= np.linalg.norm(L)
    top = base - drum - hgt
    for yy in range(top, base - drum + 1):
        v = (base - drum - yy) / max(1, hgt)
        hw = r * math.sqrt(max(0.0, 1 - v * v))
        a, b = int(round(cx - hw)), int(round(cx + hw))
        for xx in range(a, b + 1):
            nx = (xx - cx) / max(1.0, r)
            ny = -v
            nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
            s = nx * L[0] + ny * L[1] + nz * L[2]
            c = hi if s > 0.78 else (md if s > 0.45 else (sh if s > 0.12 else kk))
            if courses and (base - drum - yy) % 3 == 2 and 0.12 < s <= 0.78:
                c = dk(c, 0.94)
            px(d, xx, yy, c)
        px(d, b, yy, kk if yy > top + 1 else sh)
    for k in range(drum):
        hl(d, cx - r - 1, cx + r + 1, base - drum + 1 + k, md if k == 0 else sh)
    hl(d, cx - r - 1, cx - r + 2, base - drum + 1, hi)
    for i in range(vents):                                         # 通风孔（顶上一圈，暗）
        ang = math.pi * (0.25 + 0.5 * (i + 0.5) / vents)
        vx = cx + int(round(math.cos(ang) * r * 0.55)) * (1 if i % 2 else -1)
        vy = base - drum - int(round(math.sin(ang) * hgt * 0.62))
        px(d, vx, vy, DARK_IN)
        px(d, vx, vy + 1, kk)
    if finial is not None:
        vl(d, cx, top - 3, top - 1, finial)
        px(d, cx, top - 4, lt(finial, 0.3))
        return top - 4
    return top


def vault(im, x0, x1, base, col, seed=0, rings=True):
    """努比亚筒拱（端面朝镜头）：半圆的端墙（x0..x1 含，拱顶高 = 半宽），一圈圈斜着砌的拱砖（同心弧，2 px 一圈），
    右上沿暗；拱脚下一道影。返回顶点 y。"""
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = wall_pal(col)
    cx = (x0 + x1) / 2.0
    r = (x1 - x0) / 2.0
    for xx in range(x0, x1 + 1):
        u = (xx - cx) / max(1.0, r)
        top = base - int(round(r * math.sqrt(max(0.0, 1 - u * u))))
        for yy in range(top, base + 1):
            dd = math.hypot(xx - cx, (yy - base) * 1.0)
            c = md
            if rings and int(r - dd) % 3 == 0 and dd < r - 1:
                c = dk(md, 0.9)
            if u < -0.6:
                c = lt(c, 0.12)
            px(d, xx, yy, c)
        px(d, xx, top, hi if u < 0.15 else sh)
        if u > 0.5:
            px(d, xx, top + 1, sh)
    return base - int(round(r))


# ============================================================ 门窗
def door(im, x, base, w, h, wood, frame=None, arch=False, studs=True, pattern=None, pcol=None, knocker=True,
         seed=0, open_leaf=False, sill=True):
    """木门（两扇，x..x+w−1，门洞底 = base）：门洞上沿 / 左沿暗；竖板 + 中缝；铁钉；门环；门槛石。
    arch = 门顶半圆（里面一块扇形的格子气窗）；frame = 门套刷的颜色带（3 px），pattern = 门套上的花纹（frieze 的 kind）；
    open_leaf = 右边那扇开着（里面暗）。返回门顶 y。"""
    d = ImageDraw.Draw(im)
    top = base - h
    if frame is not None:
        fhi, fmd, fsh, fkk = wall_pal(frame)
        rr = (w + 6) // 2
        if arch:
            d.pieslice((x - 3, top - 3 - (w + 6) // 2 + rr // 3, x + w + 2, top - 3 + rr + rr // 3), 180, 360, fill=C(fmd))
        rect(d, x - 3, top - 3, x + w + 2, base, fmd)
        if pattern:
            frieze(d, x - 3, x + w + 2, top - 3, 3, pattern, pcol or fsh)
            for yy in range(top, base - 2, 4):
                px(d, x - 2, yy, pcol or fsh)
                px(d, x + w + 1, yy, pcol or fsh)
        vl(d, x - 3, top - 3, base, fhi)
        vl(d, x + w + 2, top - 3, base, fsh)
    whi, wmd, wsh, wkk = lt(wood, 0.18), wood, dk(wood, 0.8), dk(wood, 0.58)
    r = w // 2
    arch_top = top - (r if arch else 0)
    if arch:
        rows = V.arch_mask_rows(w, r, pointed=False)
        for i in range(w):
            t = top - int(round(rows[i]))
            for yy in range(t, top):
                ang = math.atan2(top - yy, (i + 0.5) - w / 2.0)
                spoke = abs(((math.degrees(ang) + 180) % 30) - 15) > 12 or yy == top - 1
                px(d, x + i, yy, wmd if spoke else (DARK_IN if (i + yy) % 2 else (90, 110, 130)))
            px(d, x + i, t, wsh)
    for i in range(w):
        for yy in range(top, base):
            c = wmd
            if open_leaf and i >= r:
                c = DARK_IN if yy > top + 2 else wkk
            elif i % 3 == 2:
                c = wsh
            elif i % 3 == 0:
                c = lt(wmd, 0.06)
            px(d, x + i, yy, c)
    if not open_leaf:
        vl(d, x + r - 1, top, base - 1, wkk)
        vl(d, x + r, top, base - 1, whi)
    else:
        rect(d, x + w, top, x + w + 1, base - 1, wsh)              # 开着的那扇（往外推开，侧面露 2 px）
    for yy in (top + h // 4, base - h // 4):                       # 横档
        hl(d, x, x + (r - 1 if open_leaf else w - 1), yy, wsh)
        hl(d, x, x + (r - 1 if open_leaf else w - 1), yy - 1, whi)
    if studs:
        for yy in range(top + 3, base - 2, 5):
            for xx in (x + 1, x + r - 3, x + r + 2, x + w - 2):
                if open_leaf and xx >= x + r:
                    continue
                px(d, xx, yy, IRON_HI)
    if knocker:
        for xx in ((x + r - 3,) if open_leaf else (x + r - 3, x + r + 2)):
            px(d, xx, base - h // 2, BRASS[2])
            px(d, xx, base - h // 2 + 1, BRASS[1])
            px(d, xx - 1, base - h // 2 + 1, BRASS[0])
    vl(d, x, arch_top, base - 1, wkk)                              # 门洞左沿 / 上沿的阴影（凹进去）
    hl(d, x, x + w - 1, top, wkk)
    if sill:
        hl(d, x - 2, x + w + 1, base, (196, 186, 166))
        hl(d, x - 2, x + w + 1, base + 1, (150, 140, 124))
    return arch_top


def crocodile(d, x, y, L=22, col=(118, 110, 84)):
    """门楣上挂的鳄鱼标本（努比亚房子的习俗，辟邪）：吻朝左，(x, y) = 吻尖、背脊那一行；身子 4 行厚，背上一排棱鳞，
    四条短腿往两边摊开，尾巴往右收尖；左上亮、肚子一道浅边、下沿描深。"""
    hi, md, sh, kk = lt(col, 0.2), col, dk(col, 0.74), dk(col, 0.5)
    belly = mix(col, (214, 200, 150), 0.45)
    for i in range(L):
        u = i / (L - 1)
        if u < 0.16:
            th = 1 + int(round(u / 0.16 * 1.4))
        elif u < 0.62:
            th = 4
        else:
            th = max(1, int(round(4 * (1 - (u - 0.62) / 0.38) + 0.4)))
        y0 = y + (4 - th) // 2 + (1 if u > 0.85 else 0)
        for k in range(th):
            c = md
            if k == 0:
                c = hi if u < 0.62 else md
            if k == th - 1 and th > 1:
                c = belly if u < 0.6 else sh
            px(d, x + i, y0 + k, c)
        px(d, x + i, y0 + th, kk if th > 1 else sh)
        if 0.24 < u < 0.82 and i % 2 == 0:                         # 背上的棱鳞
            px(d, x + i, y0 - 1, sh)
    for (lx, sgn) in ((x + 6, -1), (x + 8, 1), (x + 13, -1), (x + 15, 1)):   # 腿（前后各一对，往上下摊开）
        yy = y + (-1 if sgn < 0 else 4)
        px(d, lx, yy, md)
        px(d, lx + (1 if sgn > 0 else -1), yy + sgn, sh)
    px(d, x + 3, y + 1, (40, 34, 28))                             # 眼
    px(d, x + 1, y + 2, lt(col, 0.4))                             # 牙
    px(d, x + 3, y + 3, lt(col, 0.4))
    for nx in (x + 5, x + L - 6):                                  # 挂它的两根钉子
        px(d, nx, y - 2, IRON)


def plate(d, cx, cy, r=2, col=(60, 100, 170), rim=(244, 242, 236)):
    """嵌在墙上的瓷盘：白边 + 蓝花心 + 左上一点高光 + 右下一圈影。"""
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C(rim))
    if r >= 2:
        d.ellipse((cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1), fill=C(col))
        px(d, cx, cy, rim)
    px(d, cx - r + 1, cy - r + 1, (255, 255, 255))
    px(d, cx + r, cy + 1, dk(rim, 0.7))
    px(d, cx + 1, cy + r, dk(rim, 0.7))


def grille_window(im, x, y, w, h, wall, frame=None, wood=WOOD, kind='lattice', shutter=None, state='open', seed=0):
    """小方窗（努比亚房子的窗都小、开得高）：窗套（frame 色）+ 窗洞里暗；kind：lattice 木格栅（斜格）/ bars 铁栏 /
    shutter 两扇百叶（state closed / open / half）。窗台一道亮、下面一道影。"""
    d = ImageDraw.Draw(im)
    fr = frame or lt(wall, 0.32)
    rect(d, x - 2, y - 2, x + w + 1, y + h + 1, fr)
    hl(d, x - 2, x + w + 1, y - 2, lt(fr, 0.25))
    vl(d, x + w + 1, y - 2, y + h + 1, dk(fr, 0.82))
    rect(d, x, y, x + w - 1, y + h - 1, DARK_IN)
    if kind == 'lattice':
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if (xx + yy) % 3 == 0 or (xx - yy) % 3 == 0:
                    px(d, xx, yy, wood if (xx + yy) % 2 else lt(wood, 0.15))
    elif kind == 'bars':
        for xx in range(x + 1, x + w, 2):
            vl(d, xx, y, y + h - 1, IRON_HI)
        hl(d, x, x + w - 1, y + h // 2, IRON_HI)
    if kind == 'shutter':
        V.win_shutter(im, x, y, w, h, wall, shutter or DOOR_GREEN, state, seed=seed, frame=fr)
        d = ImageDraw.Draw(im)
    else:
        hl(d, x, x + w - 1, y, dk(DARK_IN, 0.7))
        vl(d, x, y, y + h - 1, dk(DARK_IN, 0.7))
    hl(d, x - 3, x + w + 2, y + h + 2, lt(fr, 0.35))               # 窗台
    mul_box(im, (x - 2, y + h + 3, x + w + 3, y + h + 4), SHADOW_MUL, level=0.6)


def mashrabiya(im, x, y, w, h, wood=WOOD, seed=0, hood=True):
    """挑出来的木格窗（mashrabiya）：顶上一道平檐 + 小檐托、正面密的车木格子（亮暗点交错 = 一颗颗车出来的木珠），
    中间一扇能推开的小窗、左侧面一窄条（受光）、底下一排逐级收进去的托架；墙上往右下落影。(x, y) = 正面左上。"""
    cast_shadow(im, [(x + w, y + 2), (x + w + 4, y + 5), (x + w + 4, y + h + 6), (x + w, y + h + 2)])
    cast_shadow(im, [(x + 1, y + h + 4), (x + w, y + h + 4), (x + w + 4, y + h + 10), (x + 5, y + h + 10)])
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = lt(wood, 0.2), wood, dk(wood, 0.76), dk(wood, 0.52)
    if hood:
        hl(d, x - 2, x + w + 1, y - 2, hi)
        hl(d, x - 2, x + w + 1, y - 1, md)
        hl(d, x - 1, x + w, y, kk)
        for xx in range(x - 1, x + w + 1, 3):
            px(d, xx, y + 1, sh)
    rect(d, x, y + 1, x + w - 1, y + h - 1, kk)
    for yy in range(y + 2, y + h - 1):                             # 车木格子
        for xx in range(x + 1, x + w - 1):
            if (xx + yy) % 2 == 0:
                px(d, xx, yy, md if (yy // 2 + xx // 2) % 2 else hi)
    for yy in range(y + 2, y + h - 1, 5):                          # 横撑
        hl(d, x + 1, x + w - 2, yy, sh)
    wx, ww = x + w // 2 - 3, 6                                     # 中间的小窗（半开，里面暗）
    rect(d, wx, y + h // 3, wx + ww - 1, y + h // 3 + 6, DARK_IN)
    rect(d, wx - 1, y + h // 3 - 1, wx + ww, y + h // 3 - 1, hi)
    vl(d, x, y + 1, y + h - 1, hi)                                 # 左侧面（受光）
    vl(d, x + w - 1, y + 1, y + h - 1, kk)
    hl(d, x, x + w - 1, y + h - 1, hi)                             # 底板
    hl(d, x, x + w - 1, y + h, md)
    hl(d, x + 1, x + w - 2, y + h + 1, sh)
    for r in range(4):                                             # 逐级收进去的托架
        hl(d, x + 2 + r * 2, x + w - 3 - r * 2, y + h + 2 + r, md if r % 2 == 0 else sh)


def awning(im, x0, x1, y, depth, c1, c2, stripe=4, scallop=True, shadow=7):
    """条纹布遮阳棚（侧视：贴墙的上沿 y 往前往下斜，看见的是一条 depth 行的布面）：条纹 c1 / c2，最上一行亮、下半截暗一点；
    下沿的波浪边由 valance 画（strip 里会飘）；棚下墙上落一道影（shadow 行，往右错 2）。x0..x1 含。"""
    d = ImageDraw.Draw(im)
    for xx in range(x0, x1 + 1):
        c = c1 if ((xx - x0) // stripe) % 2 == 0 else c2
        for k in range(depth):
            cc = c
            if k == 0:
                cc = lt(c, 0.25)
            elif k >= depth - 2:
                cc = dk(c, 0.84)
            px(d, xx, y + k, cc)
    hl(d, x0, x1, y - 1, dk(c1, 0.6))                              # 钉在墙上的木条
    if shadow:
        mul_box(im, (x0 + 2, y + depth + (3 if scallop else 0), x1 + 2, y + depth + 2 + shadow), SHADOW_MUL)
        mul_box(im, (x0 + 3, y + depth + 3 + shadow, x1 + 2, y + depth + 4 + shadow), SHADOW_MUL, level=0.5)
    if scallop:
        valance(d, x0, x1, y + depth, c1, c2, 0, stripe=stripe)


def valance(d, x0, x1, y, c1, c2, f, stripe=4, n=N_ANIM, amp=1.0, seed=0):
    """遮阳棚下沿的波浪边（每 stripe 一个半圆小垂片），f 帧：垂片轻轻往后翻（下沿 0 / 1 px 起伏 + 偶尔一片翘起来）。"""
    for k, xx in enumerate(range(x0, x1 + 1, stripe)):
        c = c1 if k % 2 == 0 else c2
        ph = math.tau * f / n + k * 0.9 + seed
        lift = 1 if math.sin(ph) * amp > 0.55 else 0
        L = 3 - lift
        for r in range(L):
            hw = (stripe - 1) // 2 - (1 if r == L - 1 else 0)
            for i in range(-hw, hw + 1):
                cx = xx + stripe // 2
                if x0 <= cx + i <= x1:
                    px(d, cx + i, y + r, dk(c, 0.82) if r == L - 1 else c)


# ============================================================ 海枣树
def palm_trunk(im, x, base, h, lean=0, seed=0, pal=PALM_PAL, w0=4):
    """海枣树干（x = 脚、base = 脚底）：往上略细（w0 → w0−1）、按 lean 往一边弯；树皮是一层层叶柄留下的菱形鳞（每 3 行错开半格），
    左亮右暗、右沿描深；脚下一圈根和淡影。返回树冠中心 (cx, cy)。"""
    d = ImageDraw.Draw(im)
    tr = pal['trunk']
    for i in range(h + 1):
        s = i / max(1, h)
        cx = x + lean * s * s
        yy = base - i
        w = w0 - (1 if s > 0.55 else 0)
        a = int(round(cx - w / 2.0))
        for k in range(w):
            c = tr[0] if k == 0 else (tr[1] if k < w - 1 else tr[2])
            if ((i // 3) + (k + (i // 3) % 2)) % 2 == 0 and i % 3 == 0:
                c = tr[3] if k > 0 else tr[2]                      # 叶柄鳞的下沿
            elif i % 3 == 1 and k == (1 + (i // 3) % 2) % w:
                c = lt(c, 0.12)
            px(d, a + k, yy, c)
        px(d, a + w, yy, tr[3])
    hl(d, x - 3, x + 3, base, tr[2])
    px(d, x - 3, base - 1, tr[1])
    px(d, x + 3, base - 1, tr[2])
    return (x + lean, base - h)


def palm_crown(im, cx, cy, R, seed=0, f=0, n=N_ANIM, pal=PALM_PAL, dry=True, dates=True, amp=1.0, fronds=13):
    """海枣树冠：fronds 片羽状叶从树冠中心放射出去（上面的翘、两边的平伸往下垂、下面的垂到底），每片 = 一根叶轴 +
    两侧往下挂的小叶（2–4 px 的短笔）；左上的叶子亮、右下的暗；下面一圈枯叶（棕）、几串海枣（橙）。
    f 帧：每片叶子按自己的相位轻轻摆（叶尖 ±1–2 px），n 帧闭合。"""
    d = ImageDraw.Draw(im)
    fr = pal['frond']
    sway = math.tau * f / n
    items = []
    for k in range(fronds):
        # 每片叶子的朝向（度，0 = 朝右、90 = 朝上）：两边平伸的多、上面几片翘、最外两片往下垂
        base_ang = [168, 146, 122, 96, 70, 44, 18, -6, 190, 206, -26, 132, 58][k % 13]
        ang = math.radians(base_ang + amp * 4.0 * math.sin(sway + k * 1.7 + seed))
        Lk = R * hrange(0.8, 1.05, seed, k, 1)
        droop = hrange(0.45, 0.7, seed, k, 2) + 0.05 * amp * math.sin(sway + k)
        if base_ang > 170 or base_ang < -2:
            droop += 0.25
        items.append((math.sin(ang), ang, Lk, droop, k))
    items.sort(key=lambda it: it[0])                               # 往下垂的先画（在后面），往上翘的后画（盖在上面）
    if dry:
        for j in range(7):                                         # 枯叶：从树冠下面垂下来的一圈
            a = math.radians(200 + j * 20 + 2 * math.sin(sway + j))
            Lj = R * 0.55
            for u in np.linspace(0, 1, int(Lj) + 1):
                xx = cx + math.cos(a) * Lj * u * 0.6
                yy = cy + 2 + Lj * u * 0.9
                c = pal['dry'][int(u * 3) % 2]
                px(d, round(xx), round(yy), c)
                if u > 0.3:
                    px(d, round(xx) + (1 if j % 2 else -1), round(yy) + 1, pal['dry'][1])
    for (_, ang, Lk, droop, k) in items:
        steps = max(6, int(Lk * 1.3))
        pts = []
        for j in range(steps + 1):
            u = j / steps
            pts.append((cx + math.cos(ang) * Lk * u, cy - math.sin(ang) * Lk * u + droop * Lk * u * u))
        lit = math.cos(ang) < 0.2 and math.sin(ang) > -0.3
        dark_side = math.cos(ang) > 0.5
        for j in range(2, steps + 1):                              # 小叶（往下挂，往叶根方向斜）
            u = j / steps
            x0, y0 = pts[j]
            ln = 1 + int(round(3.2 * math.sin(math.pi * min(1.0, u * 1.05))))
            back = -1 if pts[j][0] > pts[j - 1][0] else 1
            c = fr[1] if j % 2 else fr[0]
            if lit and j % 3 == 0:
                c = fr[2]
            if dark_side:
                c = dk(c, 0.86)
            for q in range(1, ln + 1):
                px(d, round(x0 + back * q * 0.45), round(y0) + q, c)
            if j % 2 == 0 and ln > 1:
                px(d, round(x0 - back * 0.6), round(y0) + 1, fr[0])
        for j in range(1, len(pts)):                               # 叶轴
            xa, ya = pts[j - 1]
            xb, yb = pts[j]
            d.line((round(xa), round(ya), round(xb), round(yb)), fill=C(fr[2] if lit else fr[1]))
            if lit and j % 3 == 1:
                px(d, round(xb), round(yb) - 1, fr[3])
    if dates:
        for (ox, L) in ((-3, 5), (1, 6), (4, 4)):                  # 海枣串（树冠下面挂着）
            for q in range(L):
                c = pal['dates'][(q + ox) % 2]
                px(d, cx + ox + (q // 3), cy + 3 + q, c)
                if q % 2 == 0:
                    px(d, cx + ox + 1 + (q // 3), cy + 3 + q, pal['dates'][2] if q < 2 else pal['dates'][1])
    d.ellipse((cx - 2, cy - 1, cx + 2, cy + 2), fill=C(fr[0]))
    px(d, cx - 1, cy - 1, fr[2])


# ============================================================ 清真寺
def minaret(im, cx, base, top, w, col, seed=0, speakers=True, crescent=(226, 190, 90)):
    """埃及的宣礼塔（马穆鲁克 / 奥斯曼混的样子，简化）：方形基座（宽 w）→ 八角柱身（宽 w−2，竖着两道棱线）→
    第一层阳台（托架 + 栏杆 + 两只铁皮喇叭，80 年代都装了）→ 圆柱身（宽 w−4）→ 第二层小阳台 → 球形尖顶 + 新月。
    左亮右暗。返回新月顶 y。"""
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = wall_pal(col)
    tot = base - top
    y_sq = base - int(tot * 0.38)                                  # 方座顶
    y_b1 = base - int(tot * 0.66)                                  # 第一层阳台
    y_b2 = base - int(tot * 0.84)                                  # 第二层阳台
    y_bulb = base - int(tot * 0.9)

    def shaft(y0, y1, ww, ridges=0):
        a = cx - ww // 2
        rect(d, a, y0, a + ww - 1, y1, md)
        vl(d, a, y0, y1, hi)
        vl(d, a + 1, y0, y1, lt(md, 0.1))
        vl(d, a + ww - 1, y0, y1, kk)
        vl(d, a + ww - 2, y0, y1, sh)
        for r in range(ridges):
            vl(d, a + (r + 1) * ww // (ridges + 1), y0, y1, sh)

    shaft(y_sq, base, w)
    for yy in range(y_sq + 6, base - 4, 12):                       # 方座上的小尖拱窗
        rect(d, cx - 1, yy, cx, yy + 4, DARK_IN)
        px(d, cx, yy - 1, DARK_IN)
        hl(d, cx - 2, cx + 1, yy + 5, hi)
    hl(d, cx - w // 2 - 1, cx + w // 2, y_sq, hi)                  # 方座顶的线脚
    hl(d, cx - w // 2 - 1, cx + w // 2, y_sq + 1, sh)
    shaft(y_b1 + 3, y_sq - 1, w - 2, ridges=2)
    for yy in range(y_b1 + 8, y_sq - 4, 9):
        rect(d, cx - 1, yy, cx, yy + 3, DARK_IN)
    for k in range(3):                                             # 阳台托架（一层层挑出去）
        hl(d, cx - w // 2 - k, cx + w // 2 - 1 + k, y_b1 + 2 - k, md if k % 2 else sh)
    rect(d, cx - w // 2 - 3, y_b1 - 4, cx + w // 2 + 2, y_b1 - 1, md)   # 栏杆
    for xx in range(cx - w // 2 - 2, cx + w // 2 + 2, 2):
        vl(d, xx, y_b1 - 3, y_b1 - 2, kk)
    hl(d, cx - w // 2 - 3, cx + w // 2 + 2, y_b1 - 4, hi)
    hl(d, cx - w // 2 - 3, cx + w // 2 + 2, y_b1 - 1, sh)
    shaft(y_b2 + 2, y_b1 - 5, max(3, w - 4))
    if speakers:                                                   # 两只喇叭（朝左右）
        for sgn in (-1, 1):
            bx = cx + sgn * (w // 2 - 1)
            for k in range(3):
                vl(d, bx + sgn * k, y_b1 - 9 - k // 2, y_b1 - 7 + k // 2, (196, 196, 200) if k < 2 else (130, 130, 136))
    for k in range(2):
        hl(d, cx - w // 2 + 1 - k, cx + w // 2 - 2 + k, y_b2 + 1 - k, sh if k else md)
    rect(d, cx - w // 2, y_b2 - 3, cx + w // 2 - 1, y_b2 - 1, md)
    hl(d, cx - w // 2, cx + w // 2 - 1, y_b2 - 3, hi)
    shaft(y_bulb + 2, y_b2 - 4, max(3, w - 6))
    r = max(2, (w - 4) // 2)                                       # 球顶（洋葱尖）
    for yy in range(y_bulb - r * 2, y_bulb + 2):
        v = (yy - (y_bulb - r)) / max(1, r)
        hw = r * math.sqrt(max(0.0, 1 - min(1.0, abs(v)) ** 2)) if v > -0.2 else max(0.0, r * (1 + v) * 0.9)
        a, b = int(round(cx - hw)), int(round(cx + hw))
        for xx in range(a, b + 1):
            c = hi if xx < cx - hw * 0.3 else (md if xx < cx + hw * 0.4 else sh)
            px(d, xx, yy, c)
    tip = y_bulb - r * 2
    vl(d, cx, tip - 4, tip - 1, BRASS[2])                          # 新月
    px(d, cx - 1, tip - 5, crescent)
    px(d, cx + 1, tip - 5, crescent)
    px(d, cx - 1, tip - 6, crescent)
    px(d, cx + 1, tip - 7, lt(crescent, 0.3))
    return tip - 7


# ============================================================ 小物件
def lantern(d, x, y, glass=((214, 70, 60), (70, 150, 90), (240, 196, 70)), chain=3):
    """铜灯笼（fanous）：从 (x, y) 往下：链子 chain 行 → 尖顶帽 → 六角灯身（三色玻璃）→ 底座小尖。宽 5、高 ~chain+9。"""
    for k in range(chain):
        px(d, x, y + k, IRON_HI if k % 2 else IRON)
    y += chain
    px(d, x, y, BRASS[2])
    hl(d, x - 1, x + 1, y + 1, BRASS[1])
    hl(d, x - 2, x + 2, y + 2, BRASS[2])
    for k in range(4):
        yy = y + 3 + k
        px(d, x - 2, yy, BRASS[1])
        px(d, x - 1, yy, glass[0])
        px(d, x, yy, lt(glass[2], 0.2) if k < 2 else glass[2])
        px(d, x + 1, yy, glass[1])
        px(d, x + 2, yy, BRASS[0])
    hl(d, x - 2, x + 2, y + 7, BRASS[1])
    hl(d, x - 1, x + 1, y + 8, BRASS[0])
    px(d, x, y + 9, BRASS[0])


def jar(d, x, base, h=9, col=(182, 104, 66), neck=True):
    """陶水罐（zir / ballas）：鼓肚子、窄脖子、外翻的口；左上亮、右下暗、下沿深；罐身一圈湿的深色（渗水）。"""
    hi, md, sh, kk = lt(col, 0.2), col, dk(col, 0.78), dk(col, 0.56)
    r = max(2, h // 2 - 1)
    cy = base - r - 1
    d.ellipse((x - r, cy - r, x + r, cy + r), fill=C(md))
    for yy in range(cy - r, cy + r + 1):
        v = (yy - cy) / r
        hw = r * math.sqrt(max(0.0, 1 - v * v))
        px(d, round(x + hw), yy, sh)
        if v > 0.3:
            px(d, round(x + hw) - 1, yy, sh)
    px(d, x - r + 1, cy - 1, hi)
    px(d, x - r + 1, cy, hi)
    px(d, x - r + 2, cy - 2, hi)
    hl(d, x - r + 1, x + r - 1, cy + r, kk)
    for xx in range(x - r + 1, x + r, 2):                          # 渗水的那圈
        px(d, xx, cy + r // 2 + 1, dk(md, 0.88))
    if neck:
        top = cy - r - 2
        rect(d, x - 1, top, x + 1, cy - r, md)
        hl(d, x - 2, x + 2, top - 1, hi)
        px(d, x + 2, top - 1, sh)
        px(d, x + 1, top, sh)


def zir_stand(d, x, base, col=(182, 104, 66)):
    """路边给过路人喝水的陶罐（sabil）：木架上两只大罐、罐口盖着木板、链子拴一只铁皮杯。x = 左腿。"""
    for lx in (x, x + 15):
        rect(d, lx, base - 10, lx + 1, base, WOOD_D)
        px(d, lx, base - 10, WOOD_HI)
    hl(d, x, x + 16, base - 10, WOOD_HI)
    hl(d, x, x + 16, base - 9, WOOD)
    hl(d, x + 1, x + 15, base - 3, WOOD)
    for (cx, h) in ((x + 5, 12), (x + 12, 11)):
        jar(d, cx, base - 9, h, col)
        hl(d, cx - 3, cx + 3, base - 9 - h - 1, WOOD_HI)          # 盖板
    vl(d, x + 16, base - 9, base - 6, IRON_HI)
    rect(d, x + 16, base - 6, x + 17, base - 5, (176, 180, 186))


def crate(d, x0, base, w, h, col=(176, 136, 88), kind='plank', seed=0):
    """木箱：plank 木板箱（两道横板缝、四角钉）/ jarid 椰枣枝编的箱子（一格格的细格子，埃及装菜装水果用的那种）。
    左上亮、右沿暗、下沿深。x0..x0+w−1、base−h+1..base。"""
    hi, md, sh, kk = lt(col, 0.2), col, dk(col, 0.78), dk(col, 0.55)
    top = base - h + 1
    rect(d, x0, top, x0 + w - 1, base, md)
    if kind == 'plank':
        for yy in range(top + h // 3, base, max(2, h // 3)):
            hl(d, x0, x0 + w - 1, yy, sh)
            hl(d, x0, x0 + w - 1, yy - 1, lt(md, 0.08))
        for (xx, yy) in ((x0 + 1, top + 1), (x0 + w - 2, top + 1), (x0 + 1, base - 1), (x0 + w - 2, base - 1)):
            px(d, xx, yy, IRON)
        for k in range(2):
            px(d, x0 + int(hrange(2, w - 3, seed, k)), top + int(hrange(1, h - 2, seed, k, 2)), dk(md, 0.86))
    else:
        for yy in range(top + 1, base):
            for xx in range(x0 + 1, x0 + w - 1):
                if (xx - x0) % 3 == 0 or (yy - top) % 3 == 0:
                    px(d, xx, yy, sh)
                elif hash01(seed, xx, yy) < 0.12:
                    px(d, xx, yy, lt(md, 0.1))
    hl(d, x0, x0 + w - 1, top, hi)
    vl(d, x0, top, base, hi)
    vl(d, x0 + w - 1, top, base, kk)
    hl(d, x0, x0 + w - 1, base, kk)


def sack(d, x, base, w=7, h=8, col=(196, 170, 120), rolled=True):
    """麻袋：下宽上窄一点、口卷起来一圈（rolled）；麻布的横纹；左亮右暗。"""
    hi, md, sh, kk = lt(col, 0.18), col, dk(col, 0.8), dk(col, 0.6)
    for k in range(h):
        yy = base - k
        u = k / max(1, h - 1)
        hw = w / 2.0 - (0.6 if u > 0.75 else 0) + (0.4 if u < 0.25 else 0)
        a, b = int(round(x - hw)), int(round(x + hw))
        hl(d, a, b, yy, md if k % 3 else dk(md, 0.93))
        px(d, a, yy, hi)
        px(d, b, yy, sh)
    if rolled:
        hl(d, x - w // 2, x + w // 2, base - h, lt(md, 0.25))
        hl(d, x - w // 2, x + w // 2, base - h + 1, sh)
    hl(d, x - w // 2, x + w // 2, base, kk)


def basket(d, x0, base, w, h, col=(196, 156, 94)):
    """编的筐（棕榈叶）：斜纹编法（隔点亮暗）、口沿一道亮、两只小提耳。"""
    hi, md, sh, kk = lt(col, 0.2), col, dk(col, 0.78), dk(col, 0.58)
    for yy in range(base - h + 1, base + 1):
        for xx in range(x0, x0 + w):
            c = md if (xx + yy) % 2 else sh
            if xx == x0:
                c = hi
            elif xx == x0 + w - 1:
                c = kk
            px(d, xx, yy, c)
    hl(d, x0 - 1, x0 + w, base - h, hi)
    px(d, x0 - 1, base - h - 1, sh)
    px(d, x0 + w, base - h - 1, sh)


def bench(d, x0, x1, seat_y, base, wood=WOOD, back=False):
    """长木凳：凳面 2 行（上亮）、两头 + 中间的凳腿、腿间一根横撑；back = 靠背（几根竖条）。"""
    hl(d, x0, x1, seat_y, lt(wood, 0.22))
    hl(d, x0, x1, seat_y + 1, wood)
    hl(d, x0, x1, seat_y + 2, dk(wood, 0.62))
    for lx in (x0 + 1, (x0 + x1) // 2, x1 - 2):
        rect(d, lx, seat_y + 3, lx + 1, base, dk(wood, 0.72))
        px(d, lx, seat_y + 3, wood)
    hl(d, x0 + 2, x1 - 2, base - 3, dk(wood, 0.78))
    if back:
        hl(d, x0, x1, seat_y - 9, lt(wood, 0.15))
        hl(d, x0, x1, seat_y - 8, dk(wood, 0.7))
        for xx in range(x0 + 1, x1, 4):
            vl(d, xx, seat_y - 7, seat_y - 1, wood)


def round_table(d, cx, base, top_y, r=6, col=(150, 156, 160), cloth=None):
    """茶馆的小圆铁桌：桌面是压扁的椭圆（3 行：亮沿 / 面 / 暗沿）、一根桌腿、三只脚往外撇；cloth = 铺一块小方布。"""
    hi, md, sh, kk = lt(col, 0.3), col, dk(col, 0.72), dk(col, 0.5)
    hl(d, cx - r + 1, cx + r - 1, top_y, hi)
    hl(d, cx - r, cx + r, top_y + 1, md)
    hl(d, cx - r + 1, cx + r - 1, top_y + 2, sh)
    if cloth is not None:
        hl(d, cx - r + 2, cx + r - 2, top_y + 1, cloth)
        vl(d, cx - r + 2, top_y + 2, top_y + 4, dk(cloth, 0.86))
        vl(d, cx + r - 2, top_y + 2, top_y + 4, dk(cloth, 0.7))
    vl(d, cx, top_y + 3, base - 2, kk)
    vl(d, cx - 1, top_y + 3, base - 2, sh)
    px(d, cx - 3, base, kk)
    px(d, cx - 2, base - 1, kk)
    px(d, cx + 3, base, kk)
    px(d, cx + 2, base - 1, kk)
    px(d, cx, base, kk)


def chair(d, x, base, face=1, col=WOOD, seat_y=None):
    """木头小椅子（侧面，face = 椅背在哪边的反方向：1 = 人朝右坐，椅背在左）：靠背、凳面、两条腿。"""
    seat_y = seat_y or base - 6
    hi, md, sh = lt(col, 0.2), col, dk(col, 0.7)
    bx = x - 3 * face
    hl(d, min(bx, x + 3 * face), max(bx, x + 3 * face), seat_y, hi)
    hl(d, min(bx, x + 3 * face), max(bx, x + 3 * face), seat_y + 1, sh)
    vl(d, bx, seat_y - 8, base, md)
    px(d, bx, seat_y - 8, hi)
    for yy in (seat_y - 6, seat_y - 3):
        px(d, bx + face, yy, md)
    vl(d, x + 3 * face, seat_y + 2, base, sh)
    vl(d, bx + face, seat_y + 2, base, sh)


def shisha(d, x, base, glass=(110, 160, 150), col=BRASS):
    """水烟壶：玻璃底瓶（圆、半透明的绿，里面一道水线）→ 铜杆 + 一只托盘 → 顶上的烟碗 + 炭（红点）；一根软管垂下来往右拖。
    x = 中线、base = 瓶底。高 ~18。"""
    d.ellipse((x - 3, base - 6, x + 3, base), fill=C(glass))
    hl(d, x - 2, x + 2, base - 3, lt(glass, 0.3))                  # 水线
    px(d, x - 2, base - 5, (230, 240, 236))
    px(d, x + 3, base - 2, dk(glass, 0.7))
    hl(d, x - 2, x + 2, base, dk(glass, 0.6))
    vl(d, x, base - 15, base - 7, col[1])
    vl(d, x + 1, base - 15, base - 7, col[0])
    hl(d, x - 3, x + 3, base - 10, col[2])                         # 托盘
    hl(d, x - 2, x + 2, base - 9, col[0])
    rect(d, x - 1, base - 18, x + 1, base - 16, (150, 80, 50))     # 烟碗
    px(d, x, base - 19, (240, 90, 40))                             # 炭
    px(d, x - 1, base - 19, (120, 50, 40))
    for k in range(8):                                             # 软管
        px(d, x + 2 + k, base - 12 + int(round(5 * math.sin(k / 7.0 * math.pi * 0.9))), (70, 60, 80) if k % 2 else (110, 80, 120))


def tea_glass(d, x, y, tea=(178, 52, 30)):
    """玻璃杯红茶（放在碟子上）：杯 2×3、上面一行亮（玻璃口）、碟子一道。(x, y) = 杯底左。"""
    px(d, x, y - 3, (236, 236, 230))
    px(d, x + 1, y - 3, (210, 214, 214))
    px(d, x, y - 2, tea)
    px(d, x + 1, y - 2, dk(tea, 0.8))
    px(d, x, y - 1, tea)
    px(d, x + 1, y - 1, dk(tea, 0.8))
    hl(d, x - 1, x + 2, y, (226, 226, 222))


def lamp_post(d, x, base, top, col=(56, 76, 70), head='lantern'):
    """铸铁路灯（刷墨绿）：底座（一圈线脚）→ 柱身（左亮右暗）→ 顶上弯出去一根臂 + 灯罩（lantern 老式四方灯 / bulb 新的伞形灯罩）。"""
    hi, md, sh = lt(col, 0.3), col, dk(col, 0.7)
    rect(d, x - 2, base - 5, x + 2, base, md)
    hl(d, x - 2, x + 2, base - 5, hi)
    hl(d, x - 3, x + 3, base, sh)
    for yy in range(top + 4, base - 5):
        px(d, x - 1, yy, hi)
        px(d, x, yy, md)
        px(d, x + 1, yy, sh)
    hl(d, x - 2, x + 2, top + 10, md)
    if head == 'lantern':
        rect(d, x - 3, top - 4, x + 3, top + 3, md)
        rect(d, x - 2, top - 3, x + 2, top + 2, (250, 238, 200))
        vl(d, x, top - 3, top + 2, md)
        hl(d, x - 4, x + 4, top - 5, sh)
        px(d, x, top - 7, md)
        hl(d, x - 1, x + 1, top - 6, md)
        px(d, x + 2, top + 2, (226, 212, 170))
    else:
        d.line((x, top + 4, x + 8, top), fill=C(md))
        hl(d, x + 5, x + 11, top, sh)
        hl(d, x + 6, x + 10, top + 1, (246, 236, 200))


def sign_ar(d, x0, y0, x1, y1, bg, fg, seed=0, border=None, rows=1, dots=True):
    """阿拉伯文招牌的“样子”（从右往左写的连笔）：底色 + 边框；每行一条基线，按词分段（中间空 2–3 px），
    基线上冒几根竖笔（alif / lam）、几处往下的碗（nun / ya）、词尾往左下的尾巴、上下几个点。只是形状，读不出字。"""
    if bg is not None:
        rect(d, x0, y0, x1, y1, bg, outline=border or dk(bg, 0.7))
        hl(d, x0 + 1, x1 - 1, y0 + 1, lt(bg, 0.22))
    ih = (y1 - y0 - 1) / rows
    for r in range(rows):
        yb = int(round(y0 + 1 + ih * (r + 0.66)))
        x = x1 - 3
        k = 0
        while x > x0 + 3:
            wl = int(hrange(4, 11, seed, r, k, 1))
            a = max(x0 + 3, x - wl + 1)
            if x - a < 2:
                break
            hl(d, a, x, yb, fg)
            for xx in range(a, x + 1):
                q = hash01(seed, r, k, xx, 2)
                if q < 0.22 and yb - 3 > y0 + 1:                   # 竖笔
                    vl(d, xx, max(y0 + 2, yb - (3 if ih > 6 else 2)), yb, fg)
                elif q < 0.34 and yb + 2 < y1:                     # 碗
                    px(d, xx, yb + 1, fg)
                    px(d, xx + 1, yb + 1, fg)
                elif dots and q > 0.9:
                    yy = yb - 2 if hash01(seed, xx, 3) < 0.6 else yb + 2
                    if y0 + 1 < yy < y1:
                        px(d, xx, yy, fg)
            if yb + 1 < y1:                                        # 词尾往左下的尾巴
                px(d, a - 1, yb + 1, fg)
            x = a - int(hrange(2, 4, seed, r, k, 4))
            k += 1


def egypt_flag(d, x, y, f, n=N_ANIM, L=11, hgt=6):
    """埃及国旗（1984 年以后：红白黑三条 + 中间金色的萨拉丁鹰，像素小只画一个金点）：旗杆在 x，旗往右飘、一波一波，n 帧闭合。"""
    for i in range(L):
        u = i / max(1, L - 1)
        wav = 1.2 * math.sin(math.tau * f / n - u * 3.6) * u
        y0 = round(y + wav + u * 0.8)
        for r in range(hgt):
            band = r * 3 // hgt
            c = ((206, 32, 44), (244, 242, 236), (36, 34, 40))[band]
            if wav > 0.6 and band == 1:
                c = (226, 224, 220)
            if wav < -0.6:
                c = dk(c, 0.86)
            px(d, x + 1 + i, y0 + r, c)
        if i == L // 2:
            px(d, x + 1 + i, y0 + hgt // 2, (214, 170, 60))


def pigeon(d, x, y, pose, col=(124, 128, 142)):
    """一只鸽子（侧面朝左，5×4）：pose 0 站着、1 低头啄、2 抬头、3 扑翅（翅膀往上）。(x, y) = 脚。"""
    hd = dk(col, 0.82)
    rect(d, x, y - 3, x + 3, y - 1, col)
    px(d, x + 4, y - 2, dk(col, 0.78))
    hl(d, x + 1, x + 2, y - 2, lt(col, 0.2))
    px(d, x + 1, y - 3, (140, 110, 156))
    if pose == 1:
        px(d, x - 1, y - 1, hd)
        px(d, x - 2, y - 1, (226, 150, 120))
    elif pose == 2:
        px(d, x, y - 5, hd)
        px(d, x, y - 4, hd)
        px(d, x - 1, y - 5, (226, 150, 120))
    elif pose == 3:
        px(d, x, y - 4, hd)
        px(d, x - 1, y - 4, (226, 150, 120))
        px(d, x + 1, y - 5, lt(col, 0.3))
        px(d, x + 2, y - 6, lt(col, 0.3))
        px(d, x + 3, y - 5, col)
    else:
        px(d, x, y - 4, hd)
        px(d, x - 1, y - 4, (226, 150, 120))
    px(d, x + 1, y, (206, 110, 96))


def felucca_img(L, sail_h, seed=0, sail=(246, 244, 236), hull=(98, 72, 54), band=None, face=1):
    """尼罗河三角帆船 felucca（侧面、远景）：船身两头翘、一道彩色船舷；一根斜挂的长横桁（低的一头在船头、高的一头远远翘在船尾上方），
    三角帆（白，背光的一半暗一点、一道接缝）；船尾一个人影。face = 1 船头朝右。返回 RGBA 小图。"""
    band = band or [(60, 140, 160), (200, 70, 60), (230, 190, 70)][seed % 3]
    wd, ht = L + 6, sail_h + 6
    g = A._new(wd, ht)
    d = ImageDraw.Draw(g)
    deck = ht - 3
    for i in range(L):                                             # 船身
        u = i / max(1, L - 1)
        lift = int(round(2 * abs(u - 0.5) * 2) ** 2) if abs(u - 0.5) > 0.3 else 0
        xx = 3 + i
        vl(d, xx, deck - lift, deck + 1, hull)
        px(d, xx, deck - lift, band)
        px(d, xx, deck + 1, dk(hull, 0.7))
    bow = 3 + L - 1 if face > 0 else 3
    stern = 3 if face > 0 else 3 + L - 1
    mx = 3 + int(L * (0.62 if face > 0 else 0.38))                  # 桅杆
    vl(d, mx, deck - int(sail_h * 0.55), deck - 1, (110, 90, 70))
    ya, yb = (bow + 2 * face, deck - 3), (stern - 2 * face, deck - sail_h)   # 横桁：船头低、船尾高
    pts = [(ya[0], ya[1]), (yb[0], yb[1]), (stern + face, deck - 2)]
    m = Image.new('L', g.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    ma = np.array(m) > 0
    a = np.array(g)
    for yy, xx in zip(*np.nonzero(ma)):
        c = sail
        if (xx - stern) * face < L * 0.35:
            c = dk(sail, 0.9)                                      # 靠船尾那半边背光
        if (xx + yy) % 7 == 0:
            c = dk(c, 0.94)                                        # 帆布的接缝
        a[yy, xx, :3] = c
        a[yy, xx, 3] = 255
    g = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(g)
    d.line((ya[0], ya[1], yb[0], yb[1]), fill=C((120, 96, 70)))
    px(d, stern + face * 2, deck - 3, (60, 50, 50))                # 船尾掌舵的人
    px(d, stern + face * 2, deck - 4, (60, 50, 50))
    return g


# ============================================================ 背景里的人（比主角矮一点，事后整体压灰）
def person(d, x, base, kind, seed, h=27, face=1, ground=None, robe=None):
    """背景路人（x = 中线、base = 脚底；sit / tea / smoke / shop 时 base = 凳面 y、ground = 地面 y）。光从左边来：左亮右暗。
    kind：galabiya 长袍 + 白头巾 / 小白帽（男）、woman 黑长裙 + 头巾、basket 头顶筐的妇女、kid 小孩（条纹衫短裤）、
          sit 坐着（长袍）、tea 坐着端茶杯、smoke 坐着叼水烟管、shop 坐在门口小凳上的店主、squat 蹲着。"""
    R = lambda *k: hash01(seed, *k)  # noqa: E731
    sk = SKIN[int(R(1) * len(SKIN))]
    skd = dk(sk, 0.78)
    fem = kind in ('woman', 'basket')
    rb = robe or (ROBES[int(R(2) * len(ROBES))] if not fem else
                  ((40, 36, 44), (52, 44, 60), (70, 40, 56), (36, 50, 70))[int(R(3) * 4)])
    rhi, rsh, rkk = lt(rb, 0.14), dk(rb, 0.82), dk(rb, 0.64)
    hx = x - 2

    def head(y, turban=True):
        rect(d, hx, y, hx + 3, y + 4, sk)
        vl(d, hx + 3, y + 1, y + 4, skd)
        px(d, hx + (2 if face > 0 else 1), y + 2, dk(sk, 0.5))     # 眼
        if fem:                                                    # 头巾（裹到下巴、垂到肩）
            sc = ((40, 36, 44), (150, 40, 70), (40, 80, 130), (200, 170, 70))[int(R(4) * 4)]
            hl(d, hx - 1, hx + 4, y - 1, sc)
            vl(d, hx - 1 if face > 0 else hx + 4, y, y + 6, sc)
            hl(d, hx, hx + 3, y, sc)
            px(d, hx + (0 if face > 0 else 3), y + 1, sc)
        elif turban and R(5) < 0.6:                                # 白头巾（缠得鼓鼓的）
            tc = (244, 240, 230) if R(6) < 0.7 else (214, 196, 160)
            hl(d, hx - 1, hx + 4, y - 1, tc)
            hl(d, hx - 1, hx + 4, y, dk(tc, 0.88))
            px(d, hx + 4, y - 1, dk(tc, 0.8))
            hl(d, hx, hx + 3, y - 2, tc)
        else:                                                      # 小白帽 / 短发
            hl(d, hx, hx + 3, y, (240, 238, 230) if R(7) < 0.6 else HAIR)
            hl(d, hx, hx + 3, y - 1, (240, 238, 230) if R(7) < 0.6 else HAIR)

    if kind in ('sit', 'tea', 'smoke', 'shop'):
        g = ground if ground is not None else base + 7
        head(base - 17)
        rect(d, x - 3, base - 12, x + 2, base - 1, rb)              # 上身
        vl(d, x - 3, base - 12, base - 1, rhi)
        vl(d, x + 2, base - 12, base - 1, rsh)
        for k in range(6):                                         # 大腿往前平伸（长袍盖住）
            xx = x - 2 + k * face if face > 0 else x + 1 - k
            hl(d, xx, xx, base - 2, rb)
            px(d, xx, base - 1, rsh)
        sx = x + 4 * face
        for yy in range(base, g):                                  # 小腿：长袍垂到脚踝
            px(d, sx, yy, rb if yy < g - 2 else sk)
            px(d, sx - face, yy, rsh if yy < g - 2 else skd)
        px(d, sx, g, (70, 54, 44))
        px(d, sx + face, g, (70, 54, 44))
        if kind == 'tea':                                          # 端着茶杯举到胸前
            px(d, x + 3 * face, base - 8, sk)
            px(d, x + 4 * face, base - 9, (236, 236, 230))
            px(d, x + 4 * face, base - 8, (178, 52, 30))
        elif kind == 'smoke':                                      # 叼着水烟管（管子往外拖）
            for k in range(5):
                px(d, x + (2 + k) * face, base - 14 + k, (90, 70, 100))
        return
    if kind == 'squat':
        head(base - 15)
        rect(d, x - 3, base - 10, x + 3, base - 1, rb)
        vl(d, x + 3, base - 10, base - 1, rsh)
        px(d, x - 3, base, (70, 54, 44))
        px(d, x + 3, base, (70, 54, 44))
        return
    if kind == 'kid':
        h = 19
        top = base - h
        head(top, turban=False)
        sh_ = CLOTH[int(R(8) * len(CLOTH))]
        for yy in range(top + 5, top + 12):                        # 条纹衫
            hl(d, x - 2, x + 1, yy, sh_ if yy % 2 else (240, 236, 226))
        px(d, x - 3, top + 6, sk)
        px(d, x + 2, top + 6, skd)
        rect(d, x - 2, top + 12, x + 1, top + 14, (70, 80, 110))
        for xx in (x - 2, x + 1):
            vl(d, xx, top + 15, base - 1, sk)
            px(d, xx, base, (60, 50, 44))
        return
    top = base - h
    head(top + 1)
    for yy in range(top + 6, base - 1):                            # 长袍：肩窄、往下摆开
        u = (yy - top - 6) / max(1, base - top - 8)
        half = 3 + int(round(u * 1.4))
        hl(d, x - half, x + half - 1, yy, rb)
        px(d, x - half, yy, rhi)
        px(d, x + half - 1, yy, rsh)
        if (yy - top) % 3 == 0 and u > 0.3:
            px(d, x + face, yy, rsh)                               # 一道褶
    for yy in range(top + 7, top + 15):                            # 胳膊（垂着，袖子到手腕）
        px(d, x - 4, yy, rb if yy < top + 14 else sk)
        px(d, x + 3, yy, rsh if yy < top + 14 else skd)
    hl(d, x - 3, x + 2, top + 6, rhi)
    if not fem and R(9) < 0.5:                                     # 领口一道
        px(d, x - (0 if face > 0 else 1), top + 7, rkk)
    hl(d, x - 3, x - 2, base - 1, (70, 54, 44))                    # 鞋 / 脚
    hl(d, x + 1, x + 2, base - 1, (70, 54, 44))
    px(d, x - 1, base - 1, sk)
    if kind == 'basket':                                           # 头顶一只筐（橘子 / 面包）
        d.ellipse((x - 5, top - 5, x + 4, top), fill=C((186, 150, 90)))
        hl(d, x - 4, x + 3, top - 5, (214, 180, 116))
        for k in range(4):
            px(d, x - 3 + k * 2, top - 6, ORANGE_C[1] if k % 2 else ORANGE_C[0])
        vl(d, x + 3, top, top + 6, skd)                            # 扶筐的手


def people_layer(size, crowd, sat=0.74, amt=0.24, col=(214, 200, 178)):
    """把一群背景路人画在单独一层上再整体压灰（往空气色混 amt、降饱和）：读起来是背景，不会被当成能说话的 NPC。
    crowd = [(x, base, kind, face, seed, h, ground, robe)]。"""
    lay = A._new(*size)
    d = ImageDraw.Draw(lay)
    for (x, base, kind, face, seed, h, ground, robe) in crowd:
        person(d, x, base, kind, seed, h=h, face=face, ground=ground, robe=robe)
    lay = A._grade(lay, sat=sat, val=1.0)
    return haze(lay, amt, col)


# ============================================================ 地面 / 光
def sand_ground(im, x0, x1, y0, y1, base, dark, light, seed, ruts=(), pebbles=60):
    """压实的沙土路：底色 + 低对比的斑驳（fbm，大块）+ 几道车辙（ruts = y 列表，淡淡的两行）+ 碎石子（亮点 + 下面一个暗点）。"""
    d = ImageDraw.Draw(im)
    rect(d, x0, y0, x1, y1, base)
    mottle(im, (x0, y0, x1, y1), base, dark, light, seed, cell=7, lo=0.24, hi=0.78)
    d = ImageDraw.Draw(im)
    for ry in ruts:
        for x in range(x0, x1 + 1):
            if hash01(seed, x // 13, ry, 3) < 0.72:
                yy = ry + int(round(math.sin(x * 0.021 + ry) * 0.8))
                px(d, x, yy, mix(base, dark, 0.7))
                if hash01(seed, x, ry, 4) < 0.4:
                    px(d, x, yy + 1, mix(base, dark, 0.45))
    for i in range(pebbles):
        x = int(hrange(x0, x1, seed, i, 5))
        y = int(hrange(y0 + 1, y1 - 1, seed, i, 6))
        px(d, x, y, mix(base, light, 0.9))
        px(d, x + 1, y + 1, mix(base, dark, 0.8))


def compress_band(im, y0, y1, mid, amt=0.16, ramp=8):
    """可走带后面（y0..y1−1）压对比：往 mid 收 amt（从 y0 起 ramp 行渐变），人物站上去看得清。"""
    a = np.array(im).astype(np.float32)
    m_ = np.array(mid, np.float32)
    for y in range(y0, y1):
        k = 1.0 - amt * min(1.0, (y - y0 + 1) / float(ramp))
        m = a[y, :, 3] > 0
        a[y, m, :3] = m_ + (a[y, m, :3] - m_) * k
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def sun_sky(stops, sun_xy, sun_r=6, glow=(255, 240, 206), glow_a=70):
    """320×180 的天：渐变 + 左上的太阳（光晕分档）。"""
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), stops, bands=12)
    sx, sy = sun_xy
    A._glow(im, sx, sy, 46, 38, glow, glow_a, rings=5)
    d = ImageDraw.Draw(im)
    d.ellipse((sx - sun_r, sy - sun_r, sx + sun_r, sy + sun_r), fill=C((255, 244, 214)))
    d.ellipse((sx - sun_r + 2, sy - sun_r + 2, sx + sun_r - 2, sy + sun_r - 2), fill=C((255, 253, 242)))
    return im


def wisps_img(period=640, hgt=60, seed=0, pal=((255, 252, 246), (240, 236, 230), (222, 220, 222), (204, 204, 212))):
    """干热天的云：几朵扁的小积云 + 长长的薄云丝（period 循环，左右接得上）。"""
    im = A._new(period, hgt)
    for i in range(4):
        w = hrange(30, 64, seed, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.26, 0.36, seed, i, 2), 700 + seed + i, pal)
        cx = (i + hrange(0.1, 0.9, seed, i, 3)) * period / 4
        y = hgt - cl.height - int(hrange(0, hgt * 0.45, seed, i, 4))
        for dx in (-period, 0, period):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    d = ImageDraw.Draw(im)
    for i in range(6):                                             # 云丝
        x0 = hrange(0, period, seed, i, 11)
        y = int(hrange(4, hgt * 0.6, seed, i, 12))
        L = int(hrange(30, 80, seed, i, 13))
        for k in range(L):
            if hash01(seed, i, k, 14) < 0.82:
                xx = int(x0 + k) % period
                c = pal[1] if k % 5 else pal[0]
                px(d, xx, y + (1 if k > L * 0.6 else 0), c)
                if hash01(seed, i, k, 15) < 0.3:
                    px(d, (xx + 2) % period, y + 1, pal[2])
    return im


# ============================================================ 图层表 → 直接拼 / 导出
# 每一项：
#   ('static', name, img, x, y)
#   ('wrap',   name, img, period, k, y, vx)          img 宽 = period（导出时 tile 到 period + 320）
#   ('pano',   name, img, k, x, y)
#   ('strip',  name, box, n, fps, fn, k)              fn(t) → 层坐标的整张 RGBA（只裁 box）
#   ('clouds', name, span, [(sub, img, x0, y, vx, k)])
#   ('pick',   key,  [img, …], values, x, y, k)
#   ('tint',   key,  '#rrggbb', alpha)
def compose(table, camX, t=0.0, state=None, fg_table=()):
    """照 bg_jojo.ref_render 的取整，把图层表直接拼成一帧（不经导出）：自检拿它和导出的层比。"""
    st = state or {}
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for L in list(table) + list(fg_table):
        typ = L[0]
        if typ == 'static':
            paste(out, L[2], L[3], L[4])
        elif typ == 'wrap':
            _, name, im, P, k, y, vx = L
            o = int(math.floor(camX * k + t * vx)) % P
            big = tile(im, P * (2 + W // P))
            paste(out, big.crop((o, 0, o + W, im.height)), 0, y)
        elif typ == 'pano':
            _, name, im, k, x, y = L
            paste(out, im, x - math.floor(camX * k), y)
        elif typ == 'strip':
            _, name, box, n, fps, fn, k = L[:7]
            if len(L) > 7 and L[7] and not st.get(L[7]):                 # 带 key 的 strip：状态没开就不画（同 bg.js）
                continue
            f = int(math.floor(t * round(fps, 6))) % n
            fr = fn(f / fps).crop(box)
            paste(out, fr, box[0] - math.floor(camX * k), box[1])
        elif typ == 'clouds':
            _, name, span, items = L
            for (sub, im, x0, y, vx, k) in items:
                x = (x0 + t * vx - camX * k) % span - 100
                paste(out, im, math.floor(x), y)
        elif typ == 'pick':
            _, key, ims, values, x, y, k = L
            v = st.get(key, 0) or 0
            i = min(range(len(values)), key=lambda j: abs(values[j] - v))
            paste(out, ims[i], x - math.floor(camX * k), y)
        elif typ == 'tint':
            _, key, col, alpha = L
            if not st.get(key):
                continue
            lay = Image.new('RGBA', (W, H), V._hex(col) + (int(255 * alpha),))
            out.alpha_composite(lay)
    return out


def export_layers(ex, BJ, table):
    """图层表 → stage 的 layers（ex.img / ex.bake 存图）。"""
    layers = []
    for L in table:
        typ = L[0]
        if typ == 'static':
            _, name, im, x, y = L
            layers.append(dict(type='static', image=ex.img(name, im), x=x, y=y))
        elif typ == 'wrap':
            _, name, im, P, k, y, vx = L
            layers.append(dict(type='wrap', image=ex.img(name, BJ.tile_to(im, P, P + W)), period=P, k=k, y=y, vx=vx))
        elif typ == 'pano':
            _, name, im, k, x, y = L
            layers.append(dict(type='pano', image=ex.img(name, im), k=k, x=x, y=y))
        elif typ == 'strip':
            _, name, box, n, fps, fn, k = L[:7]
            layers.append(ex.bake(name, box, n, fps, fn, screen=False, k=k, key=L[7] if len(L) > 7 else None))
        elif typ == 'clouds':
            _, name, span, items = L
            cl = [dict(image=ex.img(sub, im), x0=float(x0), y=y, vx=vx, k=k) for (sub, im, x0, y, vx, k) in items]
            layers.append(dict(type='clouds', span=span, clouds=cl))
        elif typ == 'pick':
            _, key, ims, values, x, y, k = L
            names = [ex.img('%s%d' % (key, i), im) for i, im in enumerate(ims)]
            layers.append(dict(type='pick', key=key, values=list(values), images=names, x=x, y=y, k=k))
        elif typ == 'tint':
            _, key, col, alpha = L
            layers.append(dict(type='tint', key=key, color=col, alpha=alpha))
    return layers


def crop_pano(im):
    """pano 层上下裁到不透明的行：返回 (图, y0)。"""
    bb = im.getchannel('A').getbbox()
    if not bb:
        return im, 0
    return im.crop((0, bb[1], im.width, bb[3])), bb[1]


def png_bytes(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.tell()


def _lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def common_checks(ex, BJ, st, table, cfg):
    """三张图共用的自检（照 ganges_ghat._checks）：cfg = dict(
        title, PW, walk, near（近景整张）, opaque_rows（近景必须整条不透明的行 (y0, y1)）, sky,
        states（要测的状态列表）, stand（站人的锚点名）, required（规格要求的锚点名）, anchors,
        size_limit（字节）, flat=(x0, x1, y0, y1, tol, frac)（可走带平整度）, cams_step）。"""
    imgs = ex.images
    PW = cfg['PW']
    title = cfg['title']
    cams = list(range(0, max(1, PW - W + 1), cfg.get('cams_step', 40)))
    if cams[-1] != PW - W and PW > W:
        cams.append(PW - W)
    states = cfg.get('states') or [{}]
    bad = 0
    for camX in cams:
        for tt in (0.0, 0.75, 1.5, 7.0):
            for s in states:
                im = np.array(BJ.ref_render(st, imgs, camX, tt, s).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('%s 镜头 0–%d（每 %d）× 4 个时刻 × %d 种状态 整屏都有画（没有露黑）' %
               (title, PW - W, cfg.get('cams_step', 40), len(states)), bad)
    ex.checked('天空 / 底图整张不透明', int((np.array(cfg['sky'])[..., 3] != 255).sum()))
    a = np.array(cfg['near'])
    y0, y1 = cfg['opaque_rows']
    ex.checked('近景 y %d–%d（地面 + 可走带）整条不透明' % (y0, y1 - 1), int((a[y0:y1, :, 3] != 255).sum()))
    ex.checked('近景只有 0 / 255 两种透明度', int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum()))
    for L in table:                                                # pano / pick 只有 0 / 255（pick 的图要和近景一样硬边）
        if L[0] == 'pick':
            for i, im in enumerate(L[2]):
                pa = np.array(im)
                ex.checked('pick %s 第 %d 张只有 0 / 255 透明度' % (L[1], i), int(((pa[..., 3] > 0) & (pa[..., 3] < 255)).sum()))
    # strip：闭合 / 帧条宽 / 每帧在动 / 画的东西都在框里（同一个帧函数的几个 strip 合起来算）
    strips = [L[:7] for L in list(table) + list(cfg.get('fg_table', ())) if L[0] == 'strip']
    for (_, name, box, n, fps, fn, k) in strips:
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
        hard = sum(int(((np.array(f)[..., 3] > 0) & (np.array(f)[..., 3] < 255)).sum()) for f in fr)
        ex.checked('strip %s 只有 0 / 255 透明度' % name, hard)
    fns = {}
    for (_, name, box, n, fps, fn, k) in strips:
        fns.setdefault(fn, []).append((name, box, n, fps))
    for fn, items in fns.items():
        lost = 0
        n, fps = items[0][2], items[0][3]
        for i in range(n):
            m = np.array(fn(i / fps))[..., 3] > 0
            for (_, box, _, _) in items:
                m[box[1]:box[3], box[0]:box[2]] = False
            lost += int(m.sum())
        ex.checked('strip %s 每帧画的东西都在框里（框外的像素）' % '+'.join(it[0] for it in items), lost)
    for L in [L for L in st['layers'] if L['type'] == 'wrap']:
        T = L['period'] / abs(L['vx']) if L.get('vx') else 0
        if not T:
            continue
        one = dict(st, layers=[L], fg=[])
        g0 = BJ.ref_render(one, imgs, 0, 0.1, {})
        g1 = BJ.ref_render(one, imgs, 0, 0.1 + T, {})
        ex.checked('wrap %s 一圈 %.1f s 闭合' % (L['image'].split('/')[-1], T), BJ.ndiff(g0, g1))
    # 锚点：规格要求的名字一个不少；都在地图里；站人的点在可走带里
    anc = st['anchors']
    miss = [k for k in cfg['required'] if k not in anc]
    ex.checked('规格要求的锚点一个不少（缺：%s）' % (','.join(miss) or '无'), len(miss))
    out = []
    wk = cfg['walk']

    def inside(v):
        if isinstance(v, (list, tuple)) and len(v) in (2, 4) and all(isinstance(q, (int, float)) for q in v):
            if len(v) == 2:
                return 0 <= v[0] <= PW and 0 <= v[1] <= H
            return 0 <= v[0] < v[2] <= PW and 0 <= v[1] < v[3] <= H
        if isinstance(v, (list, tuple)):
            return all(inside(q) for q in v)
        if isinstance(v, dict):
            return all(inside(q) for q in v.values())
        return True
    for k, v in anc.items():
        if not inside(v):
            out.append(k)
    for k in cfg['stand']:
        v = anc.get(k)
        if v is None or not (wk[0] <= v[1] <= wk[1] and 4 <= v[0] <= PW - 4):
            out.append(k + '(站点)')
    ex.checked('锚点都在地图里、站人的点在可走带里（不满足：%s）' % (','.join(out) or '无'), len(out))
    # 可走带平整：可走带里和该行中位亮度差太多的像素（画在地上的平东西除外）占比
    if cfg.get('flat'):
        # flat_skip = 要排除的框（剧情要坐 / 要站上去的矮东西：茶桌、喷泉池沿……它们本来就该和地面不一样）
        x0, x1, fy0, fy1, tol, frac = cfg['flat']
        lum = _lum(a[..., :3].astype(np.float32))
        m = np.zeros(lum.shape, bool)
        m[fy0:fy1, x0:x1] = True
        for (sx0, sy0, sx1, sy1) in cfg.get('flat_skip', ()):
            m[sy0:sy1, sx0:sx1] = False
        n_bad, tot = 0, int(m.sum())
        for y in range(fy0, fy1):
            row = lum[y][m[y]]
            if row.size:
                n_bad += int((np.abs(row - np.median(row)) > tol).sum())
        ex.checked('可走带 y %d–%d 只有平整地面（和行中位亮度差 > %d 的像素 %.2f %% ≤ %.1f %%，排除 %d 个框）' %
                   (fy0, fy1 - 1, tol, 100.0 * n_bad / max(1, tot), frac * 100, len(cfg.get('flat_skip', ()))),
                   0 if n_bad <= frac * tot else n_bad)
    # 导出 vs 直接拼
    for camX in sorted(set([0, PW // 2 - W // 2, PW - W] if PW > W else [0])):
        for tt in (0.0, 1.25, 9.0):
            for s in states:
                got = BJ.ref_render(st, imgs, camX, tt, s)
                want = compose(table, camX, tt, s, cfg.get('fg_table', ()))
                ex.checked('%s camX=%d t=%.2f %s 导出 vs 直接拼' % (title, camX, tt, s or '默认'), BJ.ndiff(got, want))
    # 体积
    tot = 0
    for k, im in imgs.items():
        if k.startswith('bg/%s/' % ex.key):
            tot += png_bytes(im)
    lim = cfg.get('size_limit', 250 * 1024)
    ex.checked('PNG 合计 %.1f KB ≤ %d KB' % (tot / 1024.0, lim // 1024), 0 if tot <= lim else int((tot - lim) // 1024) + 1)
    nm = _lum(a[..., :3].astype(np.float32))
    ex.note('亮度：可走带 y%d–%d 均值 %.0f 标准差 %.1f；后沿 y%d–%d 均值 %.0f 标准差 %.1f' %
            (wk[0], wk[1], nm[wk[0]:wk[1] + 1].mean(), nm[wk[0]:wk[1] + 1].std(),
             wk[0] - 40, wk[0] - 1, nm[wk[0] - 40:wk[0]].mean(), nm[wk[0] - 40:wk[0]].std()))


# ============================================================ 2026-10-19 第三轮补的通用工具
def frame_of(t, n=N_ANIM, fps=FPS_ANIM):
    """t 秒 → 第几帧（和 bg.js 的 floor(t·fps) mod n 一样；+1e-6 免得 i/fps 乘回来差一点掉到上一帧）。"""
    return int(math.floor(t * fps + 1e-6)) % n


def auto_box(fn, n=N_ANIM, fps=FPS_ANIM, pad=0, limit=None):
    """strip 的框 = n 帧画到的像素的外接框（+pad）：框是从画出来的东西算的，“每帧画的东西都在框里”天然成立，
    改动画时也不用手调框。limit = (x0, y0, x1, y1) 夹在这个范围里。"""
    bb = None
    for i in range(n):
        b = fn(i / fps).getchannel('A').getbbox()
        if not b:
            continue
        bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    if bb is None:
        raise ValueError('strip 每一帧都是空的')
    x0, y0, x1, y1 = bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad
    if limit:
        x0, y0, x1, y1 = max(x0, limit[0]), max(y0, limit[1]), min(x1, limit[2]), min(y1, limit[3])
    return (x0, y0, x1, y1)


def hard_alpha(im, bay_off=0):
    """半透明（烟、蒸汽、光斑）→ 只有 0 / 255：alpha 和 Bayer 阈值比，留下的点不透明（颜色不变）。
    near / strip 都要求硬边，所以软的东西一律走这里抖开。"""
    a = np.array(im)
    al = a[..., 3].astype(np.float32) / 255.0
    bay = A._bayer(im.width + bay_off, im.height)[:, bay_off:bay_off + im.width]
    keep = al > bay * 0.999 + 1e-3
    a[..., 3] = np.where(keep & (a[..., 3] > 0), 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def outer_rim(im, col=INK, y1=H, max_iter=600):
    """只描“外轮廓”的 1 px 墨线：和画面上沿连通的透明区（= 天）里、挨着不透明像素（上 / 左 / 右）的点涂成 col。
    为什么不用 ink_rim：镂空女儿墙的三角孔、拱洞、树冠缝这类封闭的透明小孔，ink_rim 会把孔沿一圈描黑、小孔直接填满；
    这里只认从顶上连下来的天，孔还是透明的（看得见后面的天）。连通用 numpy 一步步往外扩（不靠 scipy）。"""
    a = np.array(im)
    op = a[..., 3] > 0
    free = ~op
    sky = np.zeros_like(op)
    sky[0] = free[0]
    for _ in range(max_iter):
        grow = sky.copy()
        grow[1:] |= sky[:-1]
        grow[:-1] |= sky[1:]
        grow[:, 1:] |= sky[:, :-1]
        grow[:, :-1] |= sky[:, 1:]
        grow &= free
        if (grow == sky).all():
            break
        sky = grow
    nb = np.zeros_like(op)
    nb[:-1] |= op[1:]
    nb[:, 1:] |= op[:, :-1]
    nb[:, :-1] |= op[:, 1:]
    m = nb & sky
    m[y1:] = False
    a[m, :3] = col
    a[m, 3] = 255
    return Image.fromarray(a, 'RGBA')


def power_pole(d, x, top, base, col=(120, 92, 66), arm=True, lean=0):
    """木头电线杆（80 年代埃及街上的那种）：杆身 3 px（左亮右暗）、顶上一根横担 + 白瓷瓶、半腰一个铁箍和一块小牌。
    lean = 杆顶往一边歪的像素。返回横担两头的瓷瓶坐标（拉电线用）。"""
    for yy in range(top, base + 1):
        u = (base - yy) / max(1, base - top)
        xx = x + int(round(lean * u))
        px(d, xx - 1, yy, lt(col, 0.18))
        px(d, xx, yy, col)
        px(d, xx + 1, yy, dk(col, 0.7))
    xt = x + lean
    pins = []
    if arm:
        hl(d, xt - 7, xt + 7, top + 3, dk(col, 0.85))
        hl(d, xt - 7, xt + 7, top + 4, dk(col, 0.62))
        for k in (-6, -2, 2, 6):
            px(d, xt + k, top + 2, (236, 236, 228))
            px(d, xt + k, top + 1, (200, 204, 200))
            pins.append((xt + k, top + 1))
    yb = top + (base - top) // 2
    hl(d, x - 1, x + 1, yb, IRON_HI)
    rect(d, x - 1, yb + 3, x + 1, yb + 6, (226, 214, 120))       # 杆号小牌（黄）
    px(d, x, yb + 4, (60, 50, 40))
    return pins


# ---- 2026-10-19 egypt-town：三张图都要用的近景小工具（从 aswan_town 挪过来）
def picto(im, s, x, y, col=(246, 246, 246)):
    paste(im, A._grid(s, {'X': col}), x, y)


def leafy(im, box, pal, seed, nib=0.22, sprout=0.12):
    """给一团平涂的树冠加叶子的碎：树冠里随机点亮 / 压暗一些像素（一簇簇叶子），边上啃掉一些、往外冒一些单片叶子。
    box = 树冠所在的框；pal = (深, 中, 亮, 高光)。只动 box 里和 pal 颜色一样的像素。"""
    x0, y0, x1, y1 = box
    a = np.array(im)
    cols = [np.array(c, np.uint8) for c in pal]
    sub = a[y0:y1, x0:x1]
    leaf = np.zeros(sub.shape[:2], bool)
    for c in cols:
        leaf |= (sub[..., :3] == c).all(-1) & (sub[..., 3] > 0)
    out = sub.copy()
    hgt, wid = leaf.shape
    for yy in range(hgt):
        for xx in range(wid):
            if not leaf[yy, xx]:
                continue
            edge = (xx == 0 or not leaf[yy, xx - 1] or xx == wid - 1 or not leaf[yy, xx + 1] or
                    yy == 0 or not leaf[yy - 1, xx])
            r = hash01(seed, x0 + xx, y0 + yy)
            if edge and r < nib:
                out[yy, xx, 3] = 0                                 # 边上啃掉一点
                continue
            if r > 0.86:
                out[yy, xx, :3] = cols[min(3, int(hash01(seed, xx, yy, 2) * 2) + 2)]
            elif r > 0.74:
                out[yy, xx, :3] = cols[0]
            if edge and yy > 0 and r > 1.0 - sprout:               # 往外冒一片叶子（左上方向多一点）
                ty, tx = yy - 1, xx + (-1 if hash01(seed, xx, yy, 3) < 0.6 else 1)
                if 0 <= tx < wid and not leaf[ty, tx]:
                    out[ty, tx, :3] = cols[1] if yy < hgt // 2 else cols[0]
                    out[ty, tx, 3] = 255
    a[y0:y1, x0:x1] = out
    im.paste(Image.fromarray(a, 'RGBA'))


def bird_cage(d, x, y):
    """挂在墙上的鸟笼（铁丝圆顶 + 一只黄雀）：(x, y) = 挂钩。"""
    px(d, x, y, IRON)
    vl(d, x, y + 1, y + 2, IRON_HI)
    d.arc((x - 4, y + 3, x + 4, y + 9), 180, 360, fill=C((200, 196, 186)))
    for k in (-4, -2, 0, 2, 4):
        vl(d, x + k, y + 6 - (1 if abs(k) == 2 else (0 if abs(k) == 4 else 3)), y + 11, (200, 196, 186))
    hl(d, x - 4, x + 4, y + 11, (150, 140, 120))
    hl(d, x - 4, x + 4, y + 12, (110, 100, 86))
    px(d, x - 1, y + 8, (240, 210, 60))
    px(d, x, y + 8, (240, 210, 60))
    px(d, x - 1, y + 7, (240, 210, 60))
    px(d, x - 2, y + 7, (230, 120, 40))


def bicycle(d, x, base):
    """靠墙的旧自行车（侧面，车头朝右）：两个轮子（圆圈 + 轮毂）、斜梁、车座、车把；x = 后轮中心。"""
    fr = (60, 90, 130)
    for cx in (x, x + 14):
        d.ellipse((cx - 5, base - 10, cx + 5, base), outline=C((40, 38, 40)))
        px(d, cx, base - 5, (150, 150, 156))
    d.line((x, base - 5, x + 6, base - 5), fill=C(fr))
    d.line((x + 6, base - 5, x + 4, base - 11), fill=C(fr))
    d.line((x + 4, base - 11, x + 12, base - 11), fill=C(fr))
    d.line((x + 6, base - 5, x + 12, base - 11), fill=C(fr))
    d.line((x + 12, base - 11, x + 14, base - 5), fill=C(fr))
    hl(d, x + 2, x + 5, base - 12, (40, 34, 30))                    # 车座
    vl(d, x + 12, base - 14, base - 11, (150, 150, 156))           # 车把
    hl(d, x + 11, x + 14, base - 14, (150, 150, 156))


def soft_shadow(im, x0, x1, y, depth=2, slant=3, mul=None):
    """立着的东西往右下落在地上的淡影（x0..x1 的脚，往下 depth 行、往右 slant）。"""
    cast_shadow(im, [(x0 + 2, y), (x1 + 1, y), (x1 + 1 + slant, y + depth), (x0 + 2 + slant, y + depth)],
                mul=mul if mul is not None else SOFT_MUL)


def arch_mask(w, rise, pointed=True):
    """宽 w 的拱：返回每一列拱洞顶相对起拱线往上的高度（int）。"""
    return [int(round(r)) for r in V.arch_mask_rows(w, rise, pointed=pointed)]


def put_inside(im, inner, x0, spring, rise, pointed=True):
    """把 inner（宽 w、高 = rise + 起拱线以下的高）按拱洞的形状贴进 im：x0 = 洞左沿、spring = 起拱线 y。
    洞口一圈：拱券左上亮、右上暗；洞里左沿 / 拱腹下一道深影（墙的厚度，太阳在左上）。"""
    w, h = inner.size
    rows = arch_mask(w, rise, pointed)
    top0 = spring - rise
    a = np.array(im)
    b = np.array(inner)
    tops = [top0 + rise - rows[i] for i in range(w)]               # 每一列洞口的上沿 y
    for i in range(w):
        for yy in range(tops[i], top0 + h):
            if b[yy - top0, i, 3] > 0:
                a[yy, x0 + i] = b[yy - top0, i]
    # 拱券一圈：左半亮、右半暗（太阳在左上）
    for i in range(w):
        y = tops[i] - 1
        c = a[y, x0 + i, :3].astype(np.float32)
        a[y, x0 + i, :3] = (c + (255 - c) * 0.3) if i < w // 2 else c * 0.8
    im.paste(Image.fromarray(a, 'RGBA'))
    # 洞里：左沿两列、上沿两行压暗（墙的厚度挡住的光）
    mask = np.zeros((H, im.width), bool)
    for i in range(w):
        mask[tops[i]:tops[i] + 2, x0 + i] = True
        if i < 2:
            mask[tops[i]:top0 + h, x0 + i] = True
    mul_mask(im, mask, SHADOW_MUL)


def cached_frames(raw):
    """raw(f) → 第 f 帧的整张图；包成 fn(t)（按 t 算帧号、每帧只画一次）。自检会把同一帧要很多次。"""
    cache = {}

    def fn(t):
        f = frame_of(t, N_ANIM, FPS_ANIM)
        if f not in cache:
            cache[f] = raw(f)
        return cache[f]
    fn.raw = raw
    return fn
