# -*- coding: utf-8 -*-
r"""nile_parts —— nile 组（egypt_temple / nile_bank / egypt_rail，第9章「尼罗河」）共用的零件。不是背景 key，本身不导出。
2026-10-19 第三轮背景重画（分工 docs/ai/context/20261019-095108-背景重画分工_第三轮.md）。

为什么单独一个文件：三张图是同一段尼罗河边（科翁坡神殿 → 河边小镇 → 卢克索外的铁路），远景的对岸（台地状的沙山、
一条海枣林的绿带、河面和倒影）、砂岩方石、海枣树、三角帆船、天和云是同一套；放在一处，三张图的调色、光照方向
（太阳一律在左上，影子往右下）和墨线粗细才一致。
最底层的小工具（dk / lt / hl / vl / px / rect / mul_box / cast_shadow / mottle / haze …）借 varanasi_street.py；
图层表 → 直接拼 / 导出 / 通用自检（compose / export_layers / common_checks）、海枣树、三角帆船、帧缓存借 egypt_town_parts.py
（同在上埃及，已验收的 aswan_town 用的就是这一套）。两个都按 bg_jojo.bg_new 的模块名加载、只读不改，不改 sys.path 顺序。

里面有：
  调色        砂岩七档色阶 SST_LADDER（深缝 → 高光）和它的阴影版、浮雕残留的颜料 PAINT、尼罗河的水、对岸的绿带和台地
  天 / 云     sky_img（P.sun_sky）、clouds_img（P.wisps_img）、kites（两只盘旋的黑鸢）
  对岸        ridge（台地状的沙山：平顶 + 一级级台阶 + 冲沟；不画尖顶，一排光滑三角在埃及会被看成金字塔）、
              greenbelt（贴水的一条绿带：灌木 / 田、远处的海枣、土坯房、宣礼塔）
  河          water_body（分档的水色 + 对岸倒影 + 长亮纹）、ripples_img（会流的短水纹，wrap 用）、glint_raw（波光闪点）、
              felucca_refl（三角帆船 + 水里的倒影，clouds 层用）
  石头        ashlar（方石砌的墙：错缝、上沿受光、灰缝、崩角、风化小坑，色阶取整、不出连续色）、block（散落的方石块）
  柱子        column（开放纸莎草柱头 / 断柱；圆柱的明暗分档、柱身的浮雕带、柱头下褪色的彩带、圆柱础、方顶板）
  浮雕        relief_god（阿努比斯 / 荷鲁斯 / 索贝克：豺狼头 / 鹰头 / 鳄鱼头的阴刻立像，残留颜料）、glyph_column（象形文字竖行）
  植物        reeds_raw（芦苇 / 纸莎草丛，strip 帧函数）
  会动的      swallows_raw（绕圈飞的小燕子）、motes_raw（光柱里飘的灰尘）
  小字        tiny_text（3×5 像素字：站牌 / 景点牌）
  自检        anchor_values（锚点名字和值都要和《素材总表》一致）、state_checks（每个 key 单独开着拍一遍没露黑）
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
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
    """tools/bg_new/<name>.py，模块名和 bg_jojo.bg_new 一样（'bg_new_' + name），已经加载过就直接复用。"""
    key = 'bg_new_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


V = _load('varanasi_street')
P = _load('egypt_town_parts')
C = A._c4
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, cast_shadow, mottle, haze, opaque = (V.mul_box, V.mul_mask, V.poly_mask, V.cast_shadow,
                                                                  V.mottle, V.haze, V.opaque)
tile = V._tile
SHADOW_MUL, SOFT_MUL = V.SHADOW_MUL, V.SOFT_MUL
compose, export_layers, common_checks, crop_pano = P.compose, P.export_layers, P.common_checks, P.crop_pano
frame_of, auto_box, hard_alpha, outer_rim, ink_rim = P.frame_of, P.auto_box, P.hard_alpha, P.outer_rim, P.ink_rim
cached_frames, soft_shadow, compress_band, sand_ground = P.cached_frames, P.soft_shadow, P.compress_band, P.sand_ground
palm_trunk, palm_crown, PALM_PAL, person = P.palm_trunk, P.palm_crown, P.PALM_PAL, P.person
_lum = P._lum

W, H = 320, 180
N, FPS = P.N_ANIM, P.FPS_ANIM
INK = P.INK
WOOD_HI, WOOD, WOOD_D, WOOD_K = P.WOOD_HI, P.WOOD, P.WOOD_D, P.WOOD_K
IRON, IRON_HI = P.IRON, P.IRON_HI
DARK_IN = P.DARK_IN

# ============================================================ 调色
# 砂岩（科翁坡 / 卢克索的神庙都是努比亚砂岩：偏黄的米褐）。七档：0 深缝 1 暗 2 背光 3 中暗 4 墙面 5 受光 6 高光。
# 为什么用色阶不用连续色：像素画只该有有限的几档，PNG 也小；所有石头零件都在这七档里取色。
SST_LADDER = [(104, 74, 56), (140, 104, 74), (172, 132, 92), (198, 160, 112), (214, 178, 128), (230, 198, 150),
              (244, 220, 176)]


def shade_ladder(lad, mul=SHADOW_MUL):
    """色阶整体压进阴影（偏冷一点，和 varanasi / aswan 的影子同一个乘子）。"""
    return [tuple(int(round(c[i] * mul[i])) for i in range(3)) for c in lad]


SST_SHADE = shade_ladder(SST_LADDER)
GRANITE = [(30, 28, 34), (48, 46, 54), (66, 64, 72), (86, 84, 92), (112, 110, 118), (146, 144, 150)]   # 黑花岗岩雕像
MUDBRICK = [(96, 66, 50), (128, 90, 64), (156, 114, 80), (178, 136, 98), (198, 158, 118), (216, 182, 140)]

# 浮雕残留的颜料（褪色，比原色灰）：大写 = 正色、小写 = 暗一档
PAINT = {'K': (46, 42, 48), 'k': (92, 88, 96), 'G': (84, 140, 102), 'g': (58, 106, 80), 'B': (70, 116, 162),
         'b': (48, 82, 124), 'N': (140, 98, 64), 'n': (104, 72, 50), 'S': (186, 102, 68), 's': (152, 80, 54),
         'W': (240, 232, 212), 'w': (210, 200, 178), 'Y': (232, 184, 74), 'y': (186, 138, 50), 'R': (194, 70, 52),
         'E': (248, 240, 218), 'Z': (246, 242, 230), 'T': (82, 62, 48)}

# 尼罗河（正午 / 上午）：远处映着天、偏亮偏蓝 → 这边偏绿褐、暗
NILE_FAR = (140, 180, 186)
NILE_MID = (106, 152, 154)
NILE_NEAR = (80, 126, 124)
NILE_DEEP = (60, 100, 98)
NILE_HI = (210, 230, 228)
GLINT = (255, 252, 236)

# 对岸：台地（亮顶面 → 中 → 背光 → 冲沟）、绿带（深 → 亮）、土坯房
RIDGE = [(240, 214, 170), (224, 192, 146), (206, 170, 124), (182, 144, 104), (154, 118, 88)]
GREEN = [(38, 72, 50), (54, 96, 60), (76, 120, 68), (108, 148, 82), (150, 178, 100)]
MUDHOUSE = [(230, 210, 174), (204, 178, 140), (164, 136, 106), (98, 80, 70)]

SKY_MORNING = [(62, 120, 196), (86, 144, 210), (126, 174, 222), (180, 204, 222), (236, 222, 196)]
SKY_NOON = [(56, 116, 198), (80, 142, 214), (118, 172, 226), (168, 202, 228), (226, 224, 206)]
SKY_AFTERNOON = [(60, 112, 188), (88, 138, 202), (132, 170, 214), (190, 200, 206), (240, 214, 176)]


# ============================================================ 天 / 云 / 鸟
def sky_img(stops, sun_xy, sun_r=6):
    return P.sun_sky(stops, sun_xy, sun_r=sun_r)


def clouds_img(seed, period=640, hgt=60):
    return P.wisps_img(period, hgt, seed)


def kites():
    """两只在高处盘旋的黑鸢（跟第4章窄街共用一张图）：返回 (图, [(y, vx, k, x0)])。"""
    return V.kite_bird_img(), list(V.KITES)


# ============================================================ 对岸
def ridge(im, x0, x1, top, base, seed, pal=RIDGE):
    """对岸的沙山（台地）：平顶 + 一级级台阶，台阶之间的坡分成三小级（风化的样子，不是一条光滑斜线）；顶面一行最亮、
    朝左的坡亮、朝右的坡暗；岩层每 5 行深浅交替；竖着几道冲沟（左沿亮、沟里暗）；脚下 4 行是淡色的沙坡。
    为什么不画尖顶：一排光滑的三角在埃及会被看成金字塔。"""
    w = x1 - x0
    ys = np.zeros(w, np.float32)
    x, i = 0, 0
    lvl = top + (base - top) * hrange(0.1, 0.45, seed, 0, 0)
    while x < w:
        L = int(hrange(26, 74, seed, i, 1))
        nxt = top + (base - top) * hrange(0.0, 0.6, seed, i, 2)
        ramp = int(hrange(5, 12, seed, i, 3))
        for k in range(L):
            if x + k >= w:
                break
            if k < ramp:
                u = round((k + 1) / ramp * 3) / 3.0
                ys[x + k] = lvl + (nxt - lvl) * u
            else:
                ys[x + k] = nxt
        x += L
        lvl = nxt
        i += 1
    yi = np.round(ys).astype(int)
    for xx in range(w):
        if hash01(seed, xx // 3, 5) < 0.16:
            yi[xx] += 1                                              # 顶沿一点点崩缺
    gul = set()
    for g in range(w // 24 + 1):
        gx = int(hrange(0, w, seed, g, 9))
        for q in range(int(hrange(1, 3, seed, g, 10))):
            gul.add(gx + q)
    d = ImageDraw.Draw(im)
    for xx in range(w):
        t = int(yi[xx])
        prev = int(yi[xx - 1]) if xx > 0 else t
        nx_ = int(yi[xx + 1]) if xx < w - 1 else t
        slope = nx_ - prev
        for y in range(t, base + 1):
            r = y - t
            if r == 0:
                c = pal[0]
            elif base - y < 4:
                c = pal[1] if (xx + y) % 2 else pal[0]               # 脚下的沙坡
            elif slope < 0 and r < 7:
                c = pal[1]
            elif slope > 0 and r < 9:
                c = pal[3]
            else:
                band = ((y + int(2 * math.sin(xx * 0.07 + seed))) // 5) % 2
                c = pal[2] if band else pal[1]
            if xx in gul and r > 2 and base - y >= 4:
                c = pal[4] if (xx + 1) in gul or (xx - 1) not in gul else pal[3]
                if (xx - 1) not in gul:
                    c = pal[1]                                       # 冲沟左沿受光
            px(d, x0 + xx, y, c)
    return yi


def greenbelt(im, x0, x1, top, water, seed, pal=GREEN, houses=(), minaret=None, palms=1.0):
    """对岸贴着水的一条绿带：最底下几行是灌木 / 甘蔗田（上沿起伏、亮点）、上面一排远处的海枣（1 px 的干 + 星形小树冠，
    高矮不一、有的成丛）；houses = [(x, w, h)] 土坯房（左亮右暗、平顶、黑窗点），minaret = (x, h) 白色宣礼塔。"""
    d = ImageDraw.Draw(im)
    for (hx, hw, hh) in houses:                                    # 房子在树后面（先画）
        rect(d, hx, water - hh, hx + hw - 1, water - 1, MUDHOUSE[1])
        vl(d, hx, water - hh, water - 1, MUDHOUSE[0])
        vl(d, hx + hw - 1, water - hh, water - 1, MUDHOUSE[2])
        hl(d, hx, hx + hw - 1, water - hh, MUDHOUSE[0])
        for k in range(1, hw - 2, 3):
            if hash01(seed, hx, k, 3) < 0.6:
                px(d, hx + k, water - hh + 2, MUDHOUSE[3])
    if minaret:
        mx, mh = minaret
        rect(d, mx, water - mh, mx + 1, water - 1, (238, 232, 218))
        vl(d, mx + 1, water - mh, water - 1, (206, 198, 186))
        hl(d, mx - 1, mx + 2, water - int(mh * 0.62), (226, 220, 206))
        px(d, mx, water - mh - 1, (226, 220, 206))
        px(d, mx, water - mh - 2, (214, 178, 90))
    xx = x0
    i = 0
    while xx < x1:                                                 # 海枣
        if hash01(seed, i, 1) < 0.85 * palms:
            hgt = int(hrange(5, 12, seed, i, 2))
            lean = 1 if hash01(seed, i, 3) < 0.3 else 0
            cy = water - 3 - hgt
            for k in range(hgt):
                px(d, xx + (lean if k > hgt // 2 else 0), water - 3 - k, (104, 92, 72))
            cx = xx + lean
            for (dx, dy, c) in ((-3, 1, pal[1]), (-2, 0, pal[2]), (-1, 0, pal[2]), (0, -1, pal[3]), (1, 0, pal[1]),
                                (2, 0, pal[1]), (3, 1, pal[0]), (-1, 1, pal[1]), (1, 1, pal[0]), (0, 0, pal[2])):
                px(d, cx + dx, cy + dy, c)
        xx += int(hrange(3, 9, seed, i, 4))
        i += 1
    for x in range(x0, x1):                                        # 灌木 / 甘蔗田
        hh = 2 + int(2.2 * (0.5 + 0.5 * math.sin(x * 0.19 + seed) * math.sin(x * 0.051 + seed * 2)))
        hh += 1 if hash01(seed, x, 6) < 0.25 else 0
        for k in range(hh + 1):
            y = water - 1 - k
            c = pal[1] if k < hh else pal[3]
            if k < hh and (x + y) % 3 == 0:
                c = pal[0]
            if k == hh and hash01(seed, x, 7) < 0.35:
                c = pal[4]
            px(d, x, y, c)


# ============================================================ 河
def water_body(im, x0, x1, y0, y1, seed, stops=(NILE_FAR, NILE_MID, NILE_NEAR), refl=8, refl_k=0.6, streaks=1.0):
    """河面（y0..y1 含）：从对岸（y0，亮、映着天）到这边（y1，暗、绿褐）分档的水色（Bayer 抖开，像素画的过渡）；
    对岸的倒影：把 y0 上面 refl 行（绿带 / 房子）上下翻过来往水色里混、每行左右错一点（水在动）、越往下越淡（抖开）；
    再撒几道长长的亮水纹（远处细、近处长）。"""
    gradient(im, (x0, y0, x1, y1 + 1), list(stops), bands=7)
    a = np.array(im)
    for r in range(refl):
        sy, ty = y0 - 1 - r, y0 + r
        if sy < 0 or ty > y1:
            break
        k = refl_k * (1 - r / float(refl))
        sh = int(round(math.sin(r * 1.9 + seed) * (0.4 + r * 0.3)))
        src = np.roll(a[sy, x0:x1, :3].astype(np.float32), sh, axis=0)
        sa = np.roll(a[sy, x0:x1, 3], sh)
        dst = a[ty, x0:x1, :3].astype(np.float32)
        bay = A._bayer(x1, ty + 1)[ty, x0:x1]
        m = (sa > 0) & (bay < k * 1.5)
        mixc = dst * 0.5 + src * 0.5 * np.array([0.82, 0.92, 0.96], np.float32)
        dst[m] = mixc[m]
        a[ty, x0:x1, :3] = np.clip(dst, 0, 255).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    n = int((x1 - x0) * (y1 - y0) / 260 * streaks)
    for i in range(n):
        y = int(hrange(y0 + refl // 2, y1, seed, i, 1))
        u = (y - y0) / max(1.0, float(y1 - y0))
        x = int(hrange(x0, x1, seed, i, 2))
        L = int(hrange(3, 10, seed, i, 3) * (0.5 + u))
        c = mix(NILE_HI, stops[1], 0.25 + u * 0.5) if hash01(seed, i, 4) < 0.7 else mix(NILE_DEEP, stops[2], 0.4)
        hl(d, x, min(x1 - 1, x + L), y, c)


def ripples_img(period, hgt, seed, dens=0.03, light=NILE_HI, dark=NILE_DEEP, far=NILE_FAR, near=NILE_NEAR):
    """会流的水纹（wrap 层，横向 period 循环、左右接得上）：一道道 2–7 px 的短横线，亮的（映天的浪尖）和暗的（浪的背光面）
    交替；越靠这边（行越往下）越密越长、颜色越实；其余透明（下面是远景层画好的水）。"""
    im = A._new(period, hgt)
    d = ImageDraw.Draw(im)
    for y in range(hgt):
        u = y / max(1.0, float(hgt - 1))
        n = int(period * dens * (0.3 + u * 1.4))
        for i in range(n):
            x = int(hrange(0, period, seed, y, i, 1))
            L = int(hrange(2, 3 + 5 * u, seed, y, i, 2))
            if hash01(seed, y, i, 3) < 0.55:
                c = mix(light, far, (1 - u) * 0.55)
            else:
                c = mix(dark, near, (1 - u) * 0.6)
            for k in range(L):
                px(d, (x + k) % period, y, c)
    return im


def glint_raw(size, box, seed, n_pts, cols=(GLINT, NILE_HI), center=None, spread=40):
    """波光：box 里 n_pts 个闪点，每个按自己的相位在 8 帧里亮 3 帧（一个点 → 3 px 的横线（大的是小十字）→ 一个点）；
    center 给了就往这一竖条聚（正午太阳的倒影）。返回 raw(f) → size 大小的整张 RGBA（只在 box 里画，帧号取模闭合）。"""
    sw, sh = size
    x0, y0, x1, y1 = box
    pts = []
    for i in range(n_pts):
        if center is not None:
            u = (hash01(seed, i, 1) + hash01(seed, i, 2) + hash01(seed, i, 3)) / 3.0
            x = int(center + (u - 0.5) * 2 * spread)
        else:
            x = int(hrange(x0, x1, seed, i, 1))
        y = int(hrange(y0, y1, seed, i, 4))
        x = max(x0 + 2, min(x1 - 3, x))
        y = max(y0 + 1, min(y1 - 2, y))
        pts.append((x, y, int(hrange(0, N, seed, i, 5)), hash01(seed, i, 6) < 0.25))

    def raw(f):
        im = A._new(sw, sh)
        d = ImageDraw.Draw(im)
        for (x, y, ph, big) in pts:
            s = (f - ph) % N
            if s == 0 or s == 2:
                px(d, x, y, cols[1])
            elif s == 1:
                if big:
                    hl(d, x - 2, x + 2, y, cols[1])
                    px(d, x, y - 1, cols[1])
                    px(d, x, y + 1, cols[1])
                else:
                    hl(d, x - 1, x + 1, y, cols[1])
                px(d, x, y, cols[0])
        return im
    return raw


def felucca_refl(L, sail_h, seed=0, face=1, water=NILE_MID, band=None, sail=(246, 244, 236)):
    """三角帆船 + 水里的倒影（clouds 层整张一起漂）：船借 P.felucca_img；倒影 = 上下翻过来、往水色混（帆的倒影亮、船身暗）、
    隔行左右错 1 px、越往下越稀（Bayer 抖开），长度取帆高的一半多一点。"""
    g = P.felucca_img(L, sail_h, seed, sail=sail, band=band, face=face)
    w, h = g.size
    rl = int(sail_h * 0.6) + 2
    out = A._new(w, h + rl)
    out.alpha_composite(g, (0, 0))
    src = np.array(g.transpose(Image.FLIP_TOP_BOTTOM)).astype(np.float32)
    a = np.array(out).astype(np.float32)
    wat = np.array(water, np.float32)
    for j in range(1, rl + 1):
        if j >= h:
            break
        ty = h - 2 + j
        if ty >= out.height:
            break
        row = src[j]
        sh = 1 if j % 2 else 0
        row = np.roll(row, sh, axis=0)
        k = 1.0 - j / float(rl + 1)
        bay = A._bayer(w + 8, ty + 1)[ty, :w]
        m = (row[:, 3] > 0) & (bay < 0.35 + 0.6 * k) & (a[ty, :, 3] == 0)
        c = wat * 0.55 + row[:, :3] * 0.45
        a[ty, m, :3] = c[m]
        a[ty, m, 3] = 255
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


# ============================================================ 石头
def ashlar(im, box, seed, lad=SST_LADDER, base_i=4, course=7, blen=(12, 26), var=1, pits=0.018, chips=0.3,
           mott=True, offset=0, joint_i=1, top_hi=True):
    """方石砌的墙面（box 含右下）：一层层（course 行高）错缝的长方石块；每块在色阶里上下差 var 档、上沿一行受光（+1 档）、
    下沿 / 竖缝一道灰缝（joint_i 档）、缝左边那一列暗一档（石块右沿背光）、角上崩掉直角的小缺口（不是毛刺）、
    风化小坑（单像素暗点）、整面再按 fbm 斑驳 ±1 档。只用色阶里的颜色（像素画、PNG 小）。返回块 id 图（给浮雕挑位置用）。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if w <= 0 or h <= 0:
        return None
    ys = np.arange(h)
    rr = (ys + offset) // course
    qq = (ys + offset) % course
    tone = np.full((h, w), base_i, np.int32)
    joint = np.zeros((h, w), bool)
    edge = np.zeros((h, w), bool)
    bid = np.zeros((h, w), np.int64)
    for r in np.unique(rr):
        rows = np.nonzero(rr == r)[0]
        pos = -int(hrange(0, blen[1], seed, int(r), 1))
        edges = []
        k = 0
        while pos < w:
            pos += int(hrange(blen[0], blen[1], seed, int(r), k, 2))
            edges.append(pos)
            k += 1
        cid = np.searchsorted(np.array(edges), np.arange(w), side='right')
        for c_ in np.unique(cid):
            cols = np.nonzero(cid == c_)[0]
            dv = int(round(hrange(-var, var, seed, int(r), int(c_), 3)))
            tone[np.ix_(rows, cols)] += dv
            bid[np.ix_(rows, cols)] = int(r) * 1000 + int(c_)
            if hash01(seed, int(r), int(c_), 4) < chips and len(rows) > 2 and len(cols) > 4:
                # 崩角：块的左上或右上角少一个 2×2 / 3×1 的直角
                cx = cols[0] if hash01(seed, int(r), int(c_), 5) < 0.5 else cols[-1] - 1
                rw = 2 if hash01(seed, int(r), int(c_), 6) < 0.5 else 3
                for yy in rows[:2 if rw == 2 else 1]:
                    for xx in range(cx, min(w, cx + rw)):
                        tone[yy, xx] = base_i - 2
        for e in edges:
            if 0 <= e < w:
                joint[rows, e] = True
                if e - 1 >= 0:
                    edge[rows, e - 1] = True
    if top_hi:
        tone[qq == 0] += 1
    joint[qq == course - 1] = True
    if mott:
        nz = A._fbm(w + 8, h + 8, 6, seed=seed % 997)[4:4 + h, 4:4 + w]
        bay = A._bayer(x1 + 1, y1 + 1)[y0:y1 + 1, x0:x1 + 1]
        tone[(nz > 0.66) & (bay < 0.6)] -= 1
        tone[(nz < 0.32) & (bay < 0.6)] += 1
    tone[edge] -= 1
    rng = np.random.default_rng(seed % 100003)
    tone[rng.random((h, w)) < pits] -= 2
    tone = np.clip(tone, 0, len(lad) - 1)
    tone[joint] = joint_i
    lut = np.array(lad, np.uint8)
    a = np.array(im)
    a[y0:y1 + 1, x0:x1 + 1, :3] = lut[tone]
    a[y0:y1 + 1, x0:x1 + 1, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    return bid


def behind(im, draw):
    """在 im 已经画好的东西“后面”补画（draw(layer) 画进一张空层，再把 im 盖上去）：墙先画、坍完顶，
    再补墙后的树干 / 远处的东西，坍掉的地方就露出它们（broken_top 会把墙顶上面整列清空，先画的会被清掉）。"""
    lay = A._new(im.width, im.height)
    draw(lay)
    lay.alpha_composite(im)
    im.paste(lay)


def broken_top(im, x0, x1, y_lo, y_hi, seed, step=(3, 9), lad=SST_LADDER):
    """把墙顶 (x0..x1) 弄成坍塌的样子：每隔 3–9 px 一级，高度在 y_lo..y_hi 之间（成块地缺，不是锯齿）；
    缺掉的地方透明，新的顶沿一行亮（受光的断面）。返回每列顶 y。"""
    a = np.array(im)
    tops = []
    x = x0
    i = 0
    while x <= x1:
        L = int(hrange(step[0], step[1], seed, i, 1))
        y = int(hrange(y_lo, y_hi, seed, i, 2))
        for k in range(L):
            if x + k > x1:
                break
            tops.append(y)
        x += L
        i += 1
    for k, y in enumerate(tops):
        xx = x0 + k
        a[:y, xx, 3] = 0
        if a[y, xx, 3]:
            a[y, xx, :3] = lad[6] if (k + y) % 4 else lad[5]
            if y + 1 < H and a[y + 1, xx, 3]:
                a[y + 1, xx, :3] = lad[5]
    im.paste(Image.fromarray(a, 'RGBA'))
    return tops


def block(im, x, base, w, h, seed, lad=SST_LADDER, top_h=2, shadow=True):
    """一块散落的方石（x = 左沿、base = 底行）：顶面 top_h 行最亮（受光）、正面一层方石的颜色 + 两三个风化坑、右侧 2 px 背光、
    崩掉一个角（直角小缺口——毛刺一窝远看像动物），1 px 墨线描外沿；右下落一道淡影。"""
    d = ImageDraw.Draw(im)
    if shadow:
        soft_shadow(im, x, x + w, base + 1, depth=1, slant=3)
        d = ImageDraw.Draw(im)
    top = base - h + 1
    rect(d, x, top, x + w - 1, base, lad[4])
    rect(d, x, top, x + w - 1, top + top_h - 1, lad[6])
    hl(d, x, x + w - 1, top + top_h, lad[5])
    rect(d, x + w - 2, top + top_h, x + w - 1, base, lad[2])
    for k in range(int(w * h / 30) + 1):
        px(d, x + 1 + int(hrange(0, w - 4, seed, k, 1)), top + top_h + 1 + int(hrange(0, max(1, h - top_h - 2), seed, k, 2)),
           lad[3])
    chip = None
    if hash01(seed, 3) < 0.6 and w > 6:                              # 崩角：左上或右上少一个 3×2 的直角
        chip = x if hash01(seed, 4) < 0.5 else x + w - 3
    # 墨线：块是叠在墙前 / 地上的，背后可能已经有东西，所以按“块自己的形状”描上沿和左右，不看底下的透明度
    a2 = np.array(im)
    for xx in range(x, x + w):
        notch = chip is not None and chip <= xx < chip + 3
        if notch:                                                  # 缺口里露出块后面的东西（取块上面那一行的颜色）
            a2[top:top + 2, xx] = a2[top - 2, xx]
        yy = top + 2 if notch else top
        a2[yy - 1, xx, :3] = INK
        a2[yy - 1, xx, 3] = 255
    for yy in range(top, base + 1):
        for xx in (x - 1, x + w):
            a2[yy, xx, :3] = INK
            a2[yy, xx, 3] = 255
    im.paste(Image.fromarray(a2, 'RGBA'))


# ============================================================ 柱子
def _cyl_tone(u):
    """圆柱横截面的明暗（太阳在左上）：左沿中、偏左高光、往右一档档暗下去。u = 0..1（左 → 右）。"""
    if u < 0.1:
        return 4
    if u < 0.34:
        return 6
    if u < 0.5:
        return 5
    if u < 0.68:
        return 4
    if u < 0.84:
        return 3
    return 2


def column(im, cx, base, top, w, seed, lad=SST_LADDER, cap='open', cap_h=12, abacus_h=4, flare=5, reliefs=True,
           paint=True, broken=None):
    """一根砂岩圆柱（cx = 中线、base = 柱础底行、top = 顶板上沿）：
      柱础   宽 w+4、3 行的扁圆盘（上沿亮）
      柱身   宽 w，按 _cyl_tone 分档的圆柱明暗；每隔 ~16 行一道阴刻的横线（浮雕分栏），栏里是压在圆柱上的小浮雕记号
            （靠两边的被“转”走，只画中间那 70 %）；柱头下面一圈褪色的彩带（蓝 / 红 / 绿）
      柱头   cap='open'：开放的纸莎草（钟形往上张开 flare px，竖着的花瓣线、下半截绿 / 蓝相间的残色）；
            cap='broken'：没有柱头，柱身到 broken 行就断了（断口是两三级直角的台阶、上面一行受光）
      顶板   宽 w−2、abacus_h 行的方块（左亮右暗）
    两边 1 px 墨线。返回 (柱身左沿, 柱身右沿, 柱头顶 y)。"""
    d = ImageDraw.Draw(im)
    xl = cx - w // 2
    xr = xl + w - 1
    rect(d, xl - 2, base - 2, xr + 2, base, lad[3])
    hl(d, xl - 2, xr + 2, base - 2, lad[5])
    hl(d, xl - 1, xl + w // 3, base - 1, lad[4])
    vl(d, xr + 2, base - 2, base, lad[1])
    prof = [0] * w                                                 # 断柱的断口：每列往下缺几行（成段的直角台阶）
    if cap == 'broken':
        shaft_top = broken
        x, i, k = 0, 0, 0
        while k < w:
            L = int(hrange(2, 5, seed, i, 21))
            dy = int(hrange(0, 4, seed, i, 22))
            for q in range(L):
                if k < w:
                    prof[k] = dy
                    k += 1
            i += 1
    else:
        shaft_top = top + abacus_h + cap_h
    for x in range(xl, xr + 1):
        u = (x - xl + 0.5) / w
        vl(d, x, shaft_top + prof[x - xl], base - 3, lad[_cyl_tone(u)])
    if reliefs:                                                    # 浮雕分栏 + 栏里的小记号（圆柱的弧度：只画中间）
        y = base - 10
        k = 0
        while y > shaft_top + 6:
            for x in range(xl + 1, xr):
                u = (x - xl + 0.5) / w
                t = _cyl_tone(u)
                px(d, x, y, lad[max(0, t - 2)])
                px(d, x, y + 1, lad[min(6, t + 1)])
            for j in range(int(w * 0.9)):
                xx = xl + 2 + int(hrange(0, w * 0.72, seed, k, j, 1))
                yy = y - 3 - int(hrange(0, 10, seed, k, j, 2))
                if yy <= shaft_top + 2:
                    continue
                u = (xx - xl + 0.5) / w
                t = _cyl_tone(u)
                if hash01(seed, k, j, 3) < 0.7:
                    px(d, xx, yy, lad[max(0, t - 2)])
                    if hash01(seed, k, j, 4) < 0.5:
                        px(d, xx, yy + 1, lad[max(0, t - 2)])
                    px(d, xx + 1, yy + 1, lad[min(6, t + 1)])
            y -= int(hrange(15, 19, seed, k, 9))
            k += 1
    if paint and cap != 'broken':                                  # 柱头下的彩带（褪色、掉了一半）
        bands = [PAINT['B'], PAINT['R'], PAINT['W'], PAINT['G']]
        for i, c in enumerate(bands):
            yy = shaft_top + 1 + i
            for x in range(xl, xr + 1):
                if hash01(seed, x, yy, 7) < 0.72:
                    u = (x - xl + 0.5) / w
                    px(d, x, yy, dk(c, 0.82) if u > 0.66 else c)
    if cap == 'open':
        for r in range(cap_h):                                     # r = 0 在柱头最下面（颈）
            yy = shaft_top - 1 - r
            s = r / max(1.0, cap_h - 1.0)
            half = w / 2.0 + flare * (s ** 1.6)
            a_ = int(round(cx - half))
            b_ = int(round(cx + half)) - (1 if w % 2 == 0 else 0)
            for x in range(a_, b_ + 1):
                u = (x - a_ + 0.5) / (b_ - a_ + 1)
                t = _cyl_tone(u)
                c = lad[t]
                petal = ((x - cx) % 3 == 0)
                if petal:
                    c = lad[max(0, t - 1)]
                if paint and r < cap_h * 0.6 and hash01(seed, x, yy, 11) < 0.55:
                    pc = PAINT['G'] if ((x - cx) // 3) % 2 else PAINT['B']
                    c = pc if t >= 4 else dk(pc, 0.8)
                px(d, x, yy, c)
            px(d, a_ - 1, yy, INK)
            px(d, b_ + 1, yy, INK)
        ytop = shaft_top - cap_h
        hl(d, int(cx - w / 2.0 - flare), int(cx + w / 2.0 + flare) - 1, ytop, lad[6])
        rect(d, xl + 1, top, xr - 1, top + abacus_h - 1, lad[4])
        hl(d, xl + 1, xr - 1, top, lad[6])
        vl(d, xl + 1, top, top + abacus_h - 1, lad[5])
        vl(d, xr - 1, top, top + abacus_h - 1, lad[2])
        vl(d, xl, top, top + abacus_h - 1, INK)
        vl(d, xr, top, top + abacus_h - 1, INK)
    elif cap == 'broken':
        for k_, x in enumerate(range(xl, xr + 1)):                 # 断面：最上一行受光、下一行次亮，上面描墨线
            yy = shaft_top + prof[k_]
            px(d, x, yy, lad[6])
            px(d, x, yy + 1, lad[5])
            px(d, x, yy - 1, INK)
            if k_ > 0 and prof[k_ - 1] < prof[k_]:
                vl(d, x, shaft_top + prof[k_ - 1], yy - 1, INK)
            if k_ < w - 1 and prof[k_ + 1] < prof[k_]:
                vl(d, x, shaft_top + prof[k_ + 1], yy - 1, INK)
    for yy in range(shaft_top + prof[0], base - 2):
        px(d, xl - 1, yy, INK)
    for yy in range(shaft_top + prof[-1], base - 2):
        px(d, xr + 1, yy, INK)
    return xl, xr, shaft_top - (cap_h if cap == 'open' else 0)


# ============================================================ 浮雕
# 三个神的立像（朝右，18×42，最下面一行是脚）：头部各不相同（豺狼 / 鹰 / 鳄鱼），身体一样——假发垂片、宽领、
# 前手握权杖（was，顶上斜着一个兽头）、后手提生命符（ankh）、白色短裙、迈步的腿。字符见 PAINT；'.' = 墙面。
_BODY = [
    '.....bB.SS.....T..',
    '....bBYYYYY....T..',
    '...SSBRRRRRS...T..',
    '...SS.BBBBBSS..T..',
    '...SS.SSSSSS.S.T..',
    '...SS.SSSSSs..SSs.',
    '...SS..SSSSs...T..',
    '...SS..SSSSs...T..',
    '...SS..SSSSs...T..',
    '...SS..SSSSs...T..',
    '...SS.YYYYYY...T..',
    '...SS.WWWwWW...T..',
    '...SS.WWWwWW...T..',
    '...SS.WWWwWWW..T..',
    '..Y.Y.WWWwWWWW.T..',
    '..YYY.WWWwWWWW.T..',
    '...Y..wwwwwwww.T..',
    '...Y..SS..SS...T..',
    '......SS..SS...T..',
    '......SS...SS..T..',
    '......SS...SS..T..',
    '......SS...SS..T..',
    '......SS....SS.T..',
    '......SS....SS.T..',
    '......SS....SS.T..',
    '......SS.....SST..',
    '......SS.....SST..',
    '.....SSSS....SST..',
    '..............T.T.',
]
_HEADS = {
    # 阿努比斯：黑色豺狼头，一只竖得很高的尖耳朵、细长的嘴、金色的眼睛
    'anubis': [
        '........K.........',
        '........KK........',
        '.......KKK........',
        '.......KkK......TT',
        '.......KkK.....T..',
        '......KKKKK....T..',
        '......KKKKKKK..T..',
        '.....KKYKKKKKK.T..',
        '.....KKKKKKKKK.T..',
        '.....bKKKKKK...T..',
        '.....bBKKK.....T..',
        '.....bBKSS.....T..',
        '.....bB.SS.....T..',
    ],
    # 荷鲁斯：鹰头（圆脑袋、白脸颊上一道黑的“泪纹”、短而带钩的喙），戴上下埃及双冠（白冠套在红冠里）
    'horus': [
        '.......WW.........',
        '......WWWW........',
        '.....RWWWW.R......',
        '.....RWWWWRR....TT',
        '.....RRRRRR....T..',
        '......NNNNN....T..',
        '.....NNNWEWN...T..',
        '.....NNNWKWYK..T..',
        '.....NNNNKNKK..T..',
        '.....bNNNNN.K..T..',
        '.....bBNNN.....T..',
        '.....bBNSS.....T..',
        '.....bB.SS.....T..',
    ],
    # 索贝克：绿色鳄鱼头（长长的扁嘴、一排白牙、眼睛鼓在头顶），头上两根羽毛 + 红日盘 + 一对横着的角
    'sobek': [
        '.....Y..Y.........',
        '.....W..W.........',
        '....RWRRWR........',
        '....RRRRRR........',
        '..YYRRRRRRYY......',
        '.YY..GGG...YY...TT',
        '.....GGGG......T..',
        '.....GYGGGGGGGGT..',
        '.....GGGGGGGGGGT..',
        '.....GGZGZGZGZ.T..',
        '.....bGGGGGGGG.T..',
        '.....bBGSS.....T..',
        '.....bB.SS.....T..',
    ],
}


def relief_god(kind):
    """返回 (颜色图 RGBA 18×42, 掩码 bool)：头 13 行 + 身体 29 行（身体第 0 行和头的最后一行重叠，取头的）。"""
    rows = _HEADS[kind][:12] + [_HEADS[kind][12]] + _BODY[1:]
    hh = len(rows)
    ww = max(len(r) for r in rows)
    a = np.zeros((hh, ww, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == '.':
                continue
            a[y, x, :3] = PAINT[ch]
            a[y, x, 3] = 255
    return Image.fromarray(a, 'RGBA'), a[..., 3] > 0


def place_relief(im, img, x, y, seed, lad=SST_LADDER, wear=0.22, keep_head=13):
    """把浮雕贴进墙（阴刻）：图形外面一圈——左 / 上那一侧是刻槽的阴影（深）、右 / 下那一侧是刻槽受光的边（亮）；
    颜料按 fbm 掉一部分（露出刻进去的石面：比墙面暗一档），头部（前 keep_head 行）掉得少，免得认不出是哪个神。"""
    a = np.array(im)
    g = np.array(img)
    m = g[..., 3] > 0
    hh, ww = m.shape
    nz = A._fbm(ww + 6, hh + 6, 3, seed=seed % 997)[3:3 + hh, 3:3 + ww]
    for yy in range(hh):
        for xx in range(ww):
            if not m[yy, xx]:
                continue
            c = g[yy, xx, :3]
            lim = wear * (0.35 if yy < keep_head else 1.0)
            if nz[yy, xx] < lim:
                c = lad[3]
            a[y + yy, x + xx, :3] = c
    pad = np.zeros((hh + 2, ww + 2), bool)
    pad[1:-1, 1:-1] = m
    for yy in range(-1, hh + 1):
        for xx in range(-1, ww + 1):
            if pad[yy + 1, xx + 1]:
                continue
            right_or_below = pad[yy + 1, xx + 2] if xx + 2 < ww + 2 else False
            right_or_below = right_or_below or (pad[yy + 2, xx + 1] if yy + 2 < hh + 2 else False)
            left_or_above = pad[yy + 1, xx] or pad[yy, xx + 1]
            X, Y = x + xx, y + yy
            if not (0 <= X < im.width and 0 <= Y < im.height):
                continue
            if right_or_below:
                a[Y, X, :3] = lad[1]                               # 图形左 / 上外侧：刻槽里的影
            elif left_or_above:
                a[Y, X, :3] = lad[6]                               # 图形右 / 下外侧：刻槽受光的斜面
    im.paste(Image.fromarray(a, 'RGBA'))


_GLYPHS = [
    ['x.', 'xx', 'x.', 'x.'],                  # 芦苇叶 i
    ['x.x.x', '.x.x.'],                         # 水 n
    ['.xxx.', 'xx.xx'],                         # 嘴 r
    ['.x.', 'xxx'],                             # 面包 t
    ['xxx', 'x.x', 'xxx'],                      # 日轮 ra
    ['.x.', 'x.x', '.x.', 'xxx', '.x.'],        # 生命符 ankh
    ['.xx.', 'xxx.', '.xxx', '.x.x'],           # 鸟
    ['.xxx.', 'xx.xx', '..x.x'],                # 荷鲁斯之眼
    ['.x', 'xx', 'x.', 'x.'],                   # 羽毛 maat
    ['..xx', 'xx.x', '.x..'],                   # 角蝰 f
    ['xxxx', '.xx.'],                           # 篮子 k
    ['x...', 'xxxx'],                           # 脚 b
    ['xxx', 'x.x', 'x.x'],                      # 房子 pr
    ['.x.', 'x.x', '.x.', '.x.'],               # 亚麻绳 h
    ['.x', 'xx', '.x', 'xx'],                   # 坐着的人
]


def glyph_column(im, x, y0, y1, seed, lad=SST_LADDER, colw=5, paint=0.25):
    """一竖行象形文字（x = 左沿、宽 colw、y0..y1）：符号一个个往下排（中间 1 行空），阴刻：笔画是刻槽的深色、
    右下多一个受光的亮点；有的符号里还剩一点颜料（蓝 / 红 / 绿）；偶尔一个椭圆的王名圈（cartouche）。右边一道竖分隔线。"""
    d = ImageDraw.Draw(im)
    y = y0
    k = 0
    while y < y1 - 2:
        if hash01(seed, k, 1) < 0.08 and y1 - y > 16:              # 王名圈
            ch = int(hrange(10, 16, seed, k, 2))
            rect(d, x, y, x + colw - 2, y + ch, None, outline=lad[1])
            px(d, x, y, lad[4])
            px(d, x + colw - 2, y, lad[4])
            px(d, x, y + ch, lad[4])
            px(d, x + colw - 2, y + ch, lad[4])
            for q in range(y + 2, y + ch - 1, 3):
                hl(d, x + 1, x + colw - 3, q, lad[2])
            hl(d, x, x + colw - 2, y + ch + 1, lad[6])
            y += ch + 3
            k += 1
            continue
        gl = _GLYPHS[int(hrange(0, len(_GLYPHS), seed, k, 3))]
        gh, gw = len(gl), max(len(r) for r in gl)
        if y + gh > y1:
            break
        ox = x + max(0, (colw - 1 - gw) // 2)
        pc = None
        if hash01(seed, k, 4) < paint:
            pc = [PAINT['B'], PAINT['R'], PAINT['G'], PAINT['Y']][int(hrange(0, 4, seed, k, 5))]
        for gy, row in enumerate(gl):
            for gx, chh in enumerate(row):
                if chh != 'x':
                    continue
                px(d, ox + gx, y + gy, pc if pc else lad[1])
        for gy, row in enumerate(gl):
            for gx, chh in enumerate(row):
                if chh == 'x':
                    nxp = row[gx + 1] if gx + 1 < len(row) else '.'
                    below = gl[gy + 1][gx] if gy + 1 < gh and gx < len(gl[gy + 1]) else '.'
                    if nxp != 'x' and below != 'x':
                        px(d, ox + gx + 1, y + gy + 1, lad[6])
        y += gh + 2
        k += 1
    vl(d, x + colw - 1, y0, y1, lad[2])


# ============================================================ 植物
def reeds_raw(size, x0, x1, base, top, seed, n=40, amp=1.6, kind='reed', pal=None):
    """芦苇 / 纸莎草丛（strip 帧函数 raw(f) → size 大小的整张 RGBA）：n 根细秆从 base 往上（高度在 top..base 之间不一），
    微微弯；秆是三档绿（后排暗、前排亮）、顶上是浅褐的穗（kind='reed'）或一小把伞状的花（kind='papyrus'）；
    每根按自己的相位左右摆，越往上摆得越多（高的摆 amp px），8 帧闭合。"""
    pal = pal or dict(st=((52, 92, 56), (78, 124, 66), (118, 158, 84)), tip=((214, 190, 140), (178, 150, 104)),
                      pap=((96, 146, 70), (140, 180, 90)))
    stalks = []
    for i in range(n):
        x = hrange(x0, x1, seed, i, 1)
        hgt = hrange(0.35, 1.0, seed, i, 2) ** 0.7 * (base - top)
        lean = hrange(-0.12, 0.12, seed, i, 3)
        ph = hrange(0, math.tau, seed, i, 4)
        row = int(hrange(0, 3, seed, i, 5))
        stalks.append((row, x, hgt, lean, ph, i))
    stalks.sort()

    def raw(f):
        im = A._new(*size)
        d = ImageDraw.Draw(im)
        sw = math.tau * f / N
        for (row, x, hgt, lean, ph, i) in stalks:
            c = pal['st'][row]
            L = int(hgt)
            prev = None
            for k in range(L + 1):
                u = k / max(1.0, float(L))
                dx = lean * k + amp * math.sin(sw + ph) * u * u
                xx = int(round(x + dx))
                yy = base - k
                if prev and abs(xx - prev[0]) > 1:
                    px(d, (xx + prev[0]) // 2, yy, c)
                px(d, xx, yy, c)
                prev = (xx, yy)
            tx, ty = prev
            if kind == 'papyrus' and hash01(seed, i, 6) < 0.7:
                for (ddx, ddy) in ((-2, 0), (-1, -1), (0, -1), (1, -1), (2, 0), (0, 0), (-1, 0), (1, 0)):
                    px(d, tx + ddx, ty + ddy, pal['pap'][1] if ddy < 0 else pal['pap'][0])
            elif hash01(seed, i, 7) < 0.75:
                for q in range(int(hrange(2, 5, seed, i, 8))):
                    px(d, tx + (1 if q % 2 else 0), ty - q, pal['tip'][q % 2])
            if row == 2 and L > 6 and hash01(seed, i, 9) < 0.6:        # 前排的秆上一片斜出的叶子
                ky = base - int(L * 0.45)
                kx = int(round(x + lean * L * 0.45 + amp * math.sin(sw + ph) * 0.2))
                s = 1 if hash01(seed, i, 10) < 0.5 else -1
                for q in range(1, 5):
                    px(d, kx + s * q, ky - q // 2 + (1 if q > 3 else 0), pal['st'][1])
        return im
    return raw


# ============================================================ 会动的小东西
def swallows_raw(size, box, seed, n=3):
    """几只小燕子绕着椭圆圈飞（strip 帧函数）：每只 3×2（翅膀一帧上一帧下），8 帧一圈，闭合。"""
    sw, sh = size
    x0, y0, x1, y1 = box
    birds = []
    for i in range(n):
        cx = hrange(x0 + 10, x1 - 10, seed, i, 1)
        cy = hrange(y0 + 6, y1 - 6, seed, i, 2)
        rx = hrange(8, (x1 - x0) / 2.6, seed, i, 3)
        ry = hrange(3, (y1 - y0) / 3.0, seed, i, 4)
        birds.append((cx, cy, rx, ry, hrange(0, math.tau, seed, i, 5), 1 if i % 2 else -1))

    def raw(f):
        im = A._new(sw, sh)
        d = ImageDraw.Draw(im)
        for (cx, cy, rx, ry, ph, dr) in birds:
            a_ = ph + dr * math.tau * f / N
            x = int(round(cx + rx * math.cos(a_)))
            y = int(round(cy + ry * math.sin(a_)))
            x = max(x0 + 1, min(x1 - 3, x))
            y = max(y0 + 1, min(y1 - 2, y))
            col = (40, 40, 56)
            if f % 2:
                px(d, x - 1, y - 1, col)
                px(d, x + 1, y - 1, col)
                px(d, x, y, col)
            else:
                hl(d, x - 1, x + 1, y, col)
                px(d, x, y - 1, (230, 226, 220))
        return im
    return raw


def motes_raw(size, box, seed, n=14, col=(255, 244, 214)):
    """光柱里飘的灰尘（strip 帧函数）：n 个 1 px 的亮点沿各自的小椭圆慢慢飘、隔帧一明一暗，8 帧闭合。"""
    sw, sh = size
    x0, y0, x1, y1 = box
    pts = [(hrange(x0 + 2, x1 - 2, seed, i, 1), hrange(y0 + 2, y1 - 2, seed, i, 2), hrange(0, math.tau, seed, i, 3))
           for i in range(n)]

    def raw(f):
        im = A._new(sw, sh)
        d = ImageDraw.Draw(im)
        for i, (x, y, ph) in enumerate(pts):
            a_ = ph + math.tau * f / N
            xx = int(round(x + 1.5 * math.cos(a_)))
            yy = int(round(y + 2.0 * math.sin(a_)))
            if (f + i) % 3 != 2:
                px(d, xx, yy, col)
        return im
    return raw


# ============================================================ 小字
_FONT = {
    'A': ['.x.', 'x.x', 'xxx', 'x.x', 'x.x'], 'B': ['xx.', 'x.x', 'xx.', 'x.x', 'xx.'],
    'E': ['xxx', 'x..', 'xx.', 'x..', 'xxx'], 'K': ['x.x', 'x.x', 'xx.', 'x.x', 'x.x'],
    'L': ['x..', 'x..', 'x..', 'x..', 'xxx'], 'M': ['x...x', 'xx.xx', 'x.x.x', 'x...x', 'x...x'],
    'N': ['x..x', 'xx.x', 'x.xx', 'x..x', 'x..x'], 'O': ['xxx', 'x.x', 'x.x', 'x.x', 'xxx'],
    'R': ['xx.', 'x.x', 'xx.', 'x.x', 'x.x'], 'S': ['xxx', 'x..', 'xxx', '..x', 'xxx'],
    'T': ['xxx', '.x.', '.x.', '.x.', '.x.'], 'U': ['x.x', 'x.x', 'x.x', 'x.x', 'xxx'],
    'X': ['x.x', 'x.x', '.x.', 'x.x', 'x.x'], 'I': ['x', 'x', 'x', 'x', 'x'], 'P': ['xx.', 'x.x', 'xx.', 'x..', 'x..'],
    ' ': ['..', '..', '..', '..', '..'],
}


def text_width(s):
    return sum(len(_FONT[ch][0]) + 1 for ch in s) - 1


def tiny_text(d, x, y, s, col):
    """3×5 的像素字（只有站牌 / 景点牌要用的几个字母）。"""
    for ch in s:
        g = _FONT[ch]
        for gy, row in enumerate(g):
            for gx, c in enumerate(row):
                if c == 'x':
                    px(d, x + gx, y + gy, col)
        x += len(g[0]) + 1


# ============================================================ 自检（各张图共用的补充项）
def anchor_values(ex, anc, expect):
    """《素材总表》定稿的锚点：名字一个不少、值一个不改。"""
    bad = [k for k, v in expect.items() if list(anc.get(k, [])) != list(v)]
    ex.checked('素材总表的锚点名字和值都对（不一致：%s）' % (','.join(bad) or '无'), len(bad))


def state_checks(ex, BJ, st, keys, cams, title):
    """每个 key 单独开着拍一遍（_state.png 是全开，盖层会互相挡）：各镜头 × 两个时刻不露黑。"""
    for key in keys:
        bad = 0
        for camX in cams:
            for tt in (0.0, 1.25):
                im = np.array(BJ.ref_render(st, ex.images, camX, tt, {key: 1}).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
        ex.checked('%s 只开 %s：各镜头不露黑' % (title, key), bad)
