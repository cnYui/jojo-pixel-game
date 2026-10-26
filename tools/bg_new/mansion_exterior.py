# -*- coding: utf-8 -*-
r"""mansion_exterior —— 第11章「DIO 的馆」馆门口（地图 mansion_ext_ch11；第10章章末的馆剪影插入也用这张）。
2026-10-19 mansion 组按体验版精度从头画（旧稿是 later_stages 里的一块平涂）。零件和场景框架在 mansion_parts.py。

地图 320 宽、ground 156、可走带 y 150–172（街面：压实的土路，对比压得很低）；侧视平视。
**光**：下午，太阳在左后方（逆光）——馆的正面整片落在阴影里，只有左边的棱、屋脊、尖顶描一道亮边；天是被尘土染黄的
亮天，所以馆的剪影黑压压地立在亮天前面（“阳光照着但整栋楼还是阴沉”）。key night：日落后，深蓝夜空 + 左上一轮月亮，
馆再压暗一档，窗帘后面透出暗红的光（玫瑰窗像一只眼睛），蝙蝠绕着尖塔飞。
从左到右（世界坐标）：
  x 0–36     街面 + 远处开罗老城（宣礼塔、圆顶、平顶房，罩着尘雾）；x 22 一根没点的煤气路灯；
             SPW 的吉普由剧情摆在 anchors.spw_car [24,166]，这一段地面只留平地
  x 30–37    围栏左端的石柱
  x 41–59    左边的圆塔楼（尖锥顶 + 铁尖、两道窄窗）
  x 59–129   左翼：三开间，楼上三扇尖拱窗拉着黑帘（中间那扇 = anchors.windows[0] [100,90]），楼下三扇被木板钉死；
             陡屋顶上一个老虎窗（玻璃碎了，一角黑帘被风吹得往外飘：strip）、一根烟囱；枯死的爬山虎爬在墙上
  x 129–191  中间的门楼：尖拱大门（三层拱券 + 门上三角山花，anchors.door [160,138]）、门上一扇玫瑰窗、两角尖塔、
             上面方塔（百叶拱窗）+ 高尖顶（顶上铁风向标：strip 慢慢转）；门前四级石阶（缝里长着枯草，两侧石栏墙 + 石球）
  x 191–253  右翼：同左翼（楼上中间那扇 = anchors.windows[1] [220,90]），屋顶右端是斜脊，矮一些——
             让出右上角的天空给枯树和乌鸦当背景（乌鸦的剪影才看得清）
  x 254–290  枯树（anchors.tree [262,160]：树干在围栏后面）：一根往左上伸的枝上停着乌鸦（anchors.crow [240,60]，strip
             偶尔歪一下头）；树根旁的黑羽毛由剧情摆
  x 134–186  铁栅大门（两扇，拱形顶 + 中间一块铁纹章；门柱上两只石雕滴水兽），anchors.gate [160,160] 在门前地面
  x 36–320   围栏：石基座 + 尖头铁栏（基座下一道影子），x 296–303 再一根石柱
  y 150–180  街面（土路，几颗小石子、浅浅的车辙，对比很低）
anchors.steps [200,162]：石阶的调查点在右边地面上（石阶最下一级 x 133–187）。

图层（从后往前）：
  day         static            白天整张（天 + 远景 + 馆 + 围栏 + 树 + 地面；不透明）
  crows_far   strip  k 1        两只乌鸦绕尖塔慢慢盘旋（只在白天：夜里被 night 盖住）
  curtain     strip  k 1        老虎窗里飘出来的黑帘（白天版）
  leaves      strip  k 1        围栏脚下被风卷着走的几片枯叶（白天）
  night       static key night  夜里整张（同一套固有色 × 夜光 + 发光的窗）
  curtain_n   strip  key night  黑帘（夜里版）
  glow_n      strip  key night  三扇窗 + 玫瑰窗里的红光慢慢一明一暗
  bats_n      strip  key night  四只蝙蝠绕着塔楼飞
  vane        strip  k 1        尖顶的铁风向标（蝙蝠形，转一圈；剪影，白天夜里同色）
  crow        strip  k 1        树枝上的乌鸦（呼吸、尾巴一翘、偶尔歪头 + 眨眼；黑色剪影，白天夜里同一套）
锚点（素材总表定稿）：arrive [60,164]、gate [160,160]、door [160,138]、windows [[100,90],[220,90]]、tree [262,160]、
      crow [240,60]、steps [200,162]、spw_car [24,166]；另导出 fence_y 147（围栏脚）、door_box [143,101,177,139]（门洞 + 门套）、
      steps_box [133,139,187,147]（石阶）。
单独运行：python -B tools\bg_new\mansion_exterior.py → tools\bg_new\_preview\ch11\after\mansion_exterior_solo.png
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

from engine.core import gradient, hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _parts():
    """mansion_parts（同 ganges_ghat 引 varanasi_street 的写法：importlib 按路径加载，不改 sys.path 顺序）。"""
    key = 'bg_new_mansion_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'mansion_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


M = _parts()
dk, lt, hl, vl, px, rect = M.dk, M.lt, M.hl, M.vl, M.px, M.rect
C = M.C
W, H = M.W, M.H
PW = 320
GROUND = 156
WALK = (150, 172)
N8 = M.N8
FPS = M.FPS_SLOW

ANCHORS = {
    'arrive': [60, 164], 'gate': [160, 160], 'door': [160, 138], 'windows': [[100, 90], [220, 90]],
    'tree': [262, 160], 'crow': [240, 60], 'steps': [200, 162], 'spw_car': [24, 166],
}
REQUIRED = ('arrive', 'gate', 'door', 'windows', 'tree', 'crow', 'steps', 'spw_car')
STAND = ('arrive', 'gate', 'tree', 'steps', 'spw_car')

BASE_Y = 140                    # 馆的墙脚（院子地面）
FENCE_Y = 147                   # 围栏基座的底（= 街面后沿）
INK = M.INK
BLK = dict(hi=(88, 84, 100), lt=(64, 60, 76), md=(48, 45, 60), dk=(34, 31, 44), dd=(20, 18, 28))   # 外墙黑石（逆光里更暗一档）
STN = M.STONE
SLATE = dict(hi=(104, 112, 134), lt=(82, 88, 110), md=(62, 66, 86), dk=(44, 46, 62), dd=(28, 28, 40))
TRIM = dict(hi=(150, 140, 150), lt=(118, 110, 124), md=(92, 86, 102), dk=(66, 60, 78), dd=(40, 36, 50))
IRON = M.IRON
BARK = dict(hi=(150, 132, 112), lt=(116, 100, 86), md=(86, 74, 66), dk=(60, 50, 46), dd=(36, 30, 30))
BARK_N = dict(rim=(170, 146, 118), lt=(96, 82, 76), md=(58, 48, 50), dk=(42, 34, 38), dd=(26, 20, 26))   # 逆光的枯树
DIRT = dict(base=(170, 146, 112), lt=(184, 160, 124), dk=(150, 128, 98), dd=(124, 104, 80), peb=(196, 178, 146))
RIM = (236, 214, 170)           # 逆光描边（太阳在左后方）
CURTAIN = M.BLACKCLOTH
OLDWOOD = dict(lt=(110, 98, 88), md=(92, 82, 74), dk=(66, 58, 54), dd=(36, 30, 32))   # 发灰的旧木板
GLOW = ((88, 10, 18), (132, 22, 26), (176, 40, 34), (220, 76, 52))     # 夜里窗帘后透出来的红光（暗 → 亮）

# 窗（楼上：中心 x、宽；anchors.windows 两扇是宽 14 的那两扇）
UP_WIN = [(78, 10), (100, 14), (120, 10), (200, 10), (220, 14), (240, 10)]
UP_Y0, UP_Y1 = 76, 104
LOW_Y0, LOW_Y1 = 114, 133
ROSE = (160, 78, 9)
DOOR = (150, 108, 21, 31)       # 门洞 x0、尖拱顶点 y、宽、高（门底 = 138）
DORMER = (88, 46, 13, 16)       # 老虎窗 x0, y0, w, h（窗洞在里面）
TREE_X = 262
CROW_FOOT = (240, 60)
MOON = (26, 30, 11)


# ============================================================ 天 / 远景
def sky_day():
    """下午被尘土染黄的亮天：上面灰蓝、往下越来越黄白；左上太阳藏在薄云后（一团光晕）；几条压低的长云，
    尖塔上空一团更暗的云（不祥），云底被太阳照亮一道。"""
    im = A._new(PW, H)
    gradient(im, (0, 0, PW, H), [(0, (92, 104, 132)), (0.32, (140, 140, 152)), (0.62, (204, 186, 156)),
                                  (0.8, (226, 206, 168)), (1, (232, 214, 178))], bands=14)
    a = np.array(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    # 太阳的光晕（左上，被云挡着：没有日轮，只有一团亮）
    r = np.hypot(xx - 30, (yy - 20) * 1.15)
    g = np.clip(1 - r / 90.0, 0, 1) ** 1.8
    bay = A._bayer(PW, H)
    q = np.floor(g * 6 + bay * 0.9) / 6
    a[..., :3] = a[..., :3] * (1 - 0.55 * q[..., None]) + np.array((255, 240, 206), np.float32) * 0.55 * q[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    # 长云（扁、几层；上沿亮、下沿暗；离太阳近的那头亮）
    clouds = [(58, 30, 70, 5, 0), (150, 14, 120, 7, 1), (236, 40, 90, 5, 2), (8, 56, 60, 4, 3), (276, 22, 60, 4, 4),
              (100, 48, 46, 3, 5)]
    for (cx, cy, L, th, s) in clouds:
        for i in range(L):
            x = cx - L // 2 + i
            u = i / max(1, L - 1)
            hgt = max(1, int(round(th * math.sin(math.pi * u) ** 0.6 + hrange(-1, 1, s, i))))
            dark = (122, 112, 128) if s != 1 else (96, 84, 102)
            lit = (214, 196, 176) if s != 1 else (182, 160, 150)
            for k in range(hgt):
                c = lit if k == 0 else (mix(dark, lit, 0.35) if k == 1 else dark)
                px(d, x, cy - hgt + 1 + k, c)
    # 压在头顶的一层暗云（整条，下沿参差、被太阳照亮一道边）：让亮天只剩中间一条，馆更阴沉
    nz = A._fbm(PW + 8, 48, 12, seed=23)[4:44, 4:4 + PW]
    a = np.array(im)
    for x in range(PW):
        u = x / (PW - 1)
        bot = 7 + 9 * math.sin(math.pi * min(1.0, max(0.0, (u - 0.12) / 0.8))) + 10 * (nz[20, x] - 0.5) * 2
        bot += 4 * math.exp(-((x - 160) / 50.0) ** 2)                 # 尖塔正上方那团最低最厚
        bot = int(round(bot))
        for y in range(0, max(0, bot) + 1):
            k = nz[min(39, y), x]
            if y == bot:
                c = (176, 150, 140) if x > 40 else (214, 186, 160)
            elif y == bot - 1:
                c = (112, 98, 112)
            else:
                c = (70, 62, 82) if k < 0.55 else (82, 74, 94)
            a[y, x, :3] = c
        if bot >= 0 and hash01(29, x) < 0.25 and bot + 1 < H:          # 下沿挂下来的几缕
            a[bot + 1, x, :3] = (150, 132, 132)
    im = Image.fromarray(a, 'RGBA')
    return im


def sky_night():
    """日落后：深蓝紫的夜空 + 星 + 左上一轮满月（和白天的太阳同一个方向，馆上的亮边才说得通）。"""
    im = M.night_sky(PW, H, seed=11, stops=[(10, 10, 30), (20, 22, 56), (40, 40, 84), (66, 52, 92)], stars=110, star_y=120)
    M.moon(im, MOON[0], MOON[1], MOON[2], strength=0.36)
    d = ImageDraw.Draw(im)
    # 夜里的薄云（月光照亮上沿）
    for (cx, cy, L) in ((70, 34, 60), (190, 20, 80), (280, 46, 50)):
        for i in range(L):
            x = cx - L // 2 + i
            u = i / max(1, L - 1)
            hgt = max(1, int(round(3 * math.sin(math.pi * u) ** 0.6)))
            for k in range(hgt):
                px(d, x, cy - hgt + 1 + k, (92, 96, 140) if k == 0 else (44, 44, 80))
    return im


def skyline(day=True):
    """远处的开罗老城（尘雾里的平顶房、圆顶、宣礼塔）：只露在馆的两边和树后。固有色已经罩好雾。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    far = (190, 170, 144)
    mid = (170, 150, 126)
    win = (150, 128, 106)
    # 远排（更淡）
    x = 0
    s = 0
    while x < PW:
        w = int(hrange(10, 24, 3, s))
        top = int(hrange(110, 124, 3, s, 1))
        rect(d, x, top, x + w - 1, 142, far)
        hl(d, x, x + w - 1, top, lt(far, 0.12))
        x += w
        s += 1
    # 宣礼塔（左）、两个圆顶
    for (mx, top) in ((14, 66), (300, 78)):
        rect(d, mx - 2, top + 8, mx + 2, 130, mid)
        rect(d, mx - 3, top + 18, mx + 3, top + 19, dk(mid, 0.9))
        rect(d, mx - 3, top + 34, mx + 3, top + 35, dk(mid, 0.9))
        rect(d, mx - 1, top + 2, mx + 1, top + 7, mid)
        px(d, mx, top, mid)
        px(d, mx, top + 1, mid)
        vl(d, mx - 2, top + 8, 130, lt(mid, 0.14))
    for (cx, cy, r) in ((34, 112, 8), (286, 116, 10)):
        d.pieslice((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=C(mid))
        rect(d, cx - r, cy, cx + r, 140, mid)
        px(d, cx, cy - r - 1, mid)
        px(d, cx, cy - r - 2, mid)
        for k in range(-r + 2, r - 1, 4):
            px(d, cx + k, cy + 5, win)
    # 近一排平顶房（左右两头）
    for (x0, x1, top) in ((0, 30, 104), (276, 320, 112), (300, 320, 98)):
        rect(d, x0, top, x1 - 1, 142, mid)
        hl(d, x0, x1 - 1, top, lt(mid, 0.18))
        for wx in range(x0 + 3, x1 - 3, 7):
            for wy in range(top + 6, 136, 11):
                rect(d, wx, wy, wx + 2, wy + 3, win)
    if not day:
        a = np.array(im).astype(np.float32)
        m = a[..., 3] > 0
        a[m, :3] = a[m, :3] * np.array((0.22, 0.24, 0.42), np.float32)
        # 远处几扇亮着的窗（开罗的夜）
        for i in range(24):
            wx = int(hrange(0, PW, 5, i))
            wy = int(hrange(108, 138, 5, i, 1))
            if a[wy, wx, 3] > 0 and (wx < 44 or wx > 270):
                a[wy, wx, :3] = (226, 186, 110)
                if wx + 1 < PW:
                    a[wy, wx + 1, :3] = (190, 150, 90)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    return im


# ============================================================ 馆
def shade_cols(d, x0, x1, y0, y1, pal, round_=False):
    """竖向一块墙面：逆光（太阳在左后方）→ 左沿一道亮边，往右越来越暗；round_ = 圆塔（中间略亮、两边压暗）。"""
    w = x1 - x0 + 1
    for i in range(w):
        u = i / max(1, w - 1)
        if round_:
            c = pal['hi'] if i == 0 else (pal['lt'] if u < 0.22 else (pal['md'] if u < 0.6 else (pal['dk'] if u < 0.88 else pal['dd'])))
        else:
            c = pal['lt'] if i == 0 else pal['md']
        vl(d, x0 + i, y0, y1, c)


def stone_courses(im, box, pal, bh=5, bw=12, seed=0, mortar=None):
    """在已经铺好底色的墙面上刻石缝（错缝）+ 每块石头一点色差：只改 box 里颜色 = pal['md'] / pal['lt'] 的像素，
    窗、门、亮边不动。"""
    x0, y0, x1, y1 = box
    a = np.array(im)
    mortar = mortar or pal['dk']
    for yy in range(y0, y1 + 1):
        row = (yy - y0) // bh
        off = (row % 2) * (bw // 2)
        for xx in range(x0, x1 + 1):
            c = tuple(a[yy, xx, :3])
            if c not in (pal['md'], pal['lt']):
                continue
            if (yy - y0) % bh == 0 or (xx - x0 + off) % bw == 0:
                if c == pal['md']:
                    a[yy, xx, :3] = mortar
            else:
                k = int((xx - x0 + off) // bw)
                f = hrange(0.92, 1.07, seed, row, k)
                if c == pal['md']:
                    a[yy, xx, :3] = np.clip(np.array(c, np.float32) * f, 0, 255).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))


def roof_scales(im, poly, pal, seed=0, rim_left=True):
    """陡屋顶（多边形）：鱼鳞石板瓦——一行行错开的小圆弧，上半行亮、下沿暗；靠左的边描一道逆光亮边。"""
    m = M.poly_mask(im.size, poly)
    a = np.array(im)
    ys, xs = np.nonzero(m)
    for (y, x) in zip(ys, xs):
        row = y // 3
        u = (x + (row % 2) * 2) % 4
        c = pal['md']
        if y % 3 == 2:
            c = pal['dk'] if u in (0, 3) else pal['md']
        elif y % 3 == 0 and u in (1, 2):
            c = pal['lt']
        if hash01(seed, x, y) < 0.04:
            c = pal['dd']
        a[y, x, :3] = c
        a[y, x, 3] = 255
    # 左沿亮边（逆光）+ 外圈墨线
    if rim_left:
        for y in np.unique(ys):
            row_x = xs[ys == y]
            x0 = row_x.min()
            a[y, x0, :3] = lt(pal['hi'], 0.25)
    im.paste(Image.fromarray(a, 'RGBA'))
    return m


def lancet(cv, cx, y0, y1, w, kind='curtain', seed=0, frame=TRIM, glow_mask=None):
    """尖拱窗：石窗套（外扩 2，左亮右暗）+ 滴水檐 + 窗台；里面 kind = 'curtain'（中梃分两格，玻璃后黑帘，竖褶）/
    'boards'（钉死的木板）/ 'slit'（窄窗，黑）。glow_mask：夜里会透红光的像素记在这里（帘缝、褶子的亮边）。"""
    d = cv.d
    x0 = cx - w // 2
    x1 = x0 + w - 1
    rise = w // 2 + 2
    top = M.arch_rows(w, rise, pointed=True)
    # 窗套
    for i in range(-2, w + 2):
        j = min(max(i, 0), w - 1)
        yt = y0 + rise - int(round(top[j])) - 2
        c = frame['lt'] if i < 0 else (frame['dk'] if i >= w else frame['md'])
        vl(d, x0 + i, yt, y1 + 1, c)
    hl(d, x0 - 3, x1 + 3, y1 + 2, frame['hi'])                         # 窗台
    hl(d, x0 - 3, x1 + 3, y1 + 3, frame['dk'])
    hl(d, x0 - 2, x1 + 2, y1 + 4, INK)
    # 滴水檐（拱外一圈 + 两端下垂的小尾巴）
    for i in range(-3, w + 3):
        j = min(max(i, 0), w - 1)
        yt = y0 + rise - int(round(top[j])) - 3
        px(d, x0 + i, yt, frame['hi'] if i < w // 2 else frame['lt'])
        px(d, x0 + i, yt - 1, INK)
    for sx in (x0 - 3, x1 + 3):
        vl(d, sx, y0 + rise - 2, y0 + rise + 1, frame['lt'])
    # 窗洞
    for i in range(w):
        yt = y0 + rise - int(round(top[i]))
        if kind == 'boards':
            vl(d, x0 + i, yt, y1, (30, 22, 24))
        else:
            ph = (i + seed) % 4
            c = CURTAIN['md'] if ph in (0, 1) else (CURTAIN['lt'] if ph == 2 else CURTAIN['dk'])
            if kind == 'slit':
                c = (18, 14, 22)
            vl(d, x0 + i, yt, y1, c)
            if glow_mask is not None and kind == 'curtain' and ph == 2:
                for yy in range(yt + 2, y1 + 1):
                    if hash01(seed, i, yy) < 0.55:
                        glow_mask[yy, x0 + i] = 1 + (yy > y1 - 6)
        px(d, x0 + i, yt, INK)
    if kind == 'curtain':
        # 中梃 + 一道横档；玻璃上一道斜的天光反光（逆光：反的是亮天）
        mx = x0 + w // 2
        vl(d, mx, y0 + 3, y1, frame['md'])
        vl(d, mx - 1 if w > 10 else mx, y0 + 4, y1, frame['dk'] if w > 10 else frame['md'])
        hl(d, x0, x1, y0 + rise + 4, frame['md'])
        for k in range(min(w, 8)):
            x, y = x0 + 1 + k, y1 - 4 - k * 2
            if y > y0 + rise and x != mx:
                px(d, x, y, (96, 92, 110))
        if glow_mask is not None:                                     # 帘子中缝和下沿：夜里最亮的一道
            for yy in range(y0 + rise, y1 + 1):
                glow_mask[yy, mx + 1 if w > 10 else mx + 1] = 3
            for xx in range(x0, x1 + 1):
                glow_mask[y1, xx] = max(glow_mask[y1, xx], 2)
    elif kind == 'boards':
        for k, by in enumerate(range(y0 + rise - 1, y1, 4)):
            c = OLDWOOD['md'] if k % 2 else OLDWOOD['lt']
            hl(d, x0, x1, by, c)
            hl(d, x0, x1, by + 1, OLDWOOD['dk'])
            hl(d, x0, x1, by + 2, OLDWOOD['dd'])
            px(d, x0 + 1, by, IRON['hi'])
            px(d, x1 - 1, by, IRON['hi'])
        d.line((x0, y0 + rise + 2, x1, y1 - 2), fill=C(OLDWOOD['dk']))
    return (x0, y0, x1, y1)


def rose_window(cv, cx, cy, r, glow_mask=None):
    """门上的玫瑰窗：石圈（左上亮右下暗）+ 8 根辐条 + 中间小圆；玻璃深红黑。夜里整片透红光（像一只眼睛）。"""
    d = cv.d
    d.ellipse((cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), fill=C(TRIM['md']), outline=C(INK))
    d.ellipse((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), outline=C(TRIM['lt']))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C((34, 14, 22)))
    for k in range(8):
        a = k * math.pi / 4
        for s in range(2, r + 1):
            px(d, round(cx + s * math.cos(a)), round(cy + s * math.sin(a)), TRIM['md'])
    d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=C((50, 18, 26)), outline=C(TRIM['lt']))
    px(d, cx, cy, TRIM['dk'])
    for k in range(8):                                                 # 每瓣一点反光
        a = k * math.pi / 4 + math.pi / 8
        px(d, round(cx + (r - 3) * math.cos(a)), round(cy + (r - 3) * math.sin(a)), (70, 26, 34))
    if glow_mask is not None:
        yy, xx = np.mgrid[0:H, 0:PW]
        rr = np.hypot(xx - cx, yy - cy)
        a = np.array(cv.im)
        dark = (a[..., 0] < 80) & (rr <= r)
        glow_mask[dark & (rr <= r)] = np.maximum(glow_mask[dark & (rr <= r)], 1)
        glow_mask[dark & (rr <= 3.5)] = 3
        glow_mask[dark & (rr > 3.5) & (rr <= r - 2)] = np.maximum(glow_mask[dark & (rr > 3.5) & (rr <= r - 2)], 2)


def portal(cv):
    """尖拱大门：三层拱券（一层层往里收，左亮右暗）+ 两边小柱 + 上面三角山花（尖顶一个十字花饰）；门扇两扇深色木门、
    铁合页、中间一个铁环门环；门洞上沿一道深影。"""
    d = cv.d
    x0, apex, w, h = DOOR
    x1 = x0 + w - 1
    y1 = apex + h - 1                                                  # 138
    # 山花（三角形）
    for i in range(0, 25):
        yy = 86 + i
        hw = int(i * 0.95)
        hl(d, 160 - hw, 160 + hw, yy, TRIM['md'] if i > 1 else TRIM['lt'])
        px(d, 160 - hw, yy, TRIM['hi'])
        px(d, 160 + hw, yy, TRIM['dd'])
    d.line((160, 86, 136, 111), fill=C(INK))
    d.line((160, 86, 184, 111), fill=C(INK))
    # 山花里的三叶窗洞（暗）
    d.ellipse((157, 97, 163, 103), fill=C((36, 26, 36)), outline=C(TRIM['dk']))
    px(d, 160, 100, TRIM['dk'])
    # 十字花饰
    vl(d, 160, 80, 86, TRIM['lt'])
    hl(d, 158, 162, 82, TRIM['lt'])
    px(d, 160, 79, TRIM['hi'])
    # 三层拱券
    for k, (ex_, col) in enumerate(((9, TRIM), (6, STN), (3, TRIM))):
        ww = w + ex_ * 2
        rise = ww // 2 + 1
        top = M.arch_rows(ww, rise, pointed=True)
        for i in range(ww):
            yt = apex - ex_ + rise - int(round(top[i])) - (rise - (w // 2 + 1))
            c = col['lt'] if i < ww * 0.3 else (col['md'] if i < ww * 0.7 else col['dk'])
            vl(d, x0 - ex_ + i, yt, y1, c)
            px(d, x0 - ex_ + i, yt, col['hi'] if i < ww // 2 else col['dd'])
    # 两边小柱（圆柱 + 柱头）
    for cx in (x0 - 6, x1 + 6):
        vl(d, cx - 1, 116, y1, TRIM['hi'])
        vl(d, cx, 116, y1, TRIM['md'])
        vl(d, cx + 1, 116, y1, TRIM['dd'])
        hl(d, cx - 2, cx + 2, 115, TRIM['lt'])
        hl(d, cx - 2, cx + 2, 114, TRIM['hi'])
    # 门洞 + 两扇门
    rise = w // 2 + 1
    top = M.arch_rows(w, rise, pointed=True)
    for i in range(w):
        yt = apex + rise - int(round(top[i]))
        c = M.WOOD['dk'] if (i % 4) else M.WOOD['dd']
        if i == w // 2:
            c = (16, 10, 12)                                          # 两扇门的缝
        vl(d, x0 + i, yt, y1, c)
        px(d, x0 + i, yt, INK)
        px(d, x0 + i, yt + 1, (24, 16, 18))                           # 门洞上沿的影
    for hy in (apex + 12, apex + 20, apex + 27):                        # 铁合页（从两边伸到中间）
        hl(d, x0 + 1, x0 + w // 2 - 2, hy, IRON['md'])
        hl(d, x0 + w // 2 + 2, x1 - 1, hy, IRON['md'])
        px(d, x0 + w // 2 - 2, hy - 1, IRON['hi'])
        px(d, x0 + w // 2 + 2, hy - 1, IRON['hi'])
    for sx in (x0 + w // 2 - 3, x0 + w // 2 + 3):                      # 门环
        d.ellipse((sx - 1, apex + 15, sx + 1, apex + 18), outline=C(IRON['hi']))
    vl(d, x0, apex + rise, y1, INK)
    vl(d, x1, apex + rise, y1, INK)


def steps_img(cv):
    """门前四级石阶（每级 2 px：上面一行亮、前脸一行暗，越往下越宽）；缝里几簇枯草；两边矮石栏墙 + 石球。"""
    d = cv.d
    steps = [(145, 175, 139), (141, 179, 141), (137, 183, 143), (133, 187, 145)]
    for k, (a_, b_, y) in enumerate(steps):
        hl(d, a_, b_, y, STN['lt'])
        hl(d, a_, b_, y + 1, STN['dk'])
        px(d, a_, y, STN['hi'])
        px(d, b_, y + 1, STN['dd'])
        for s in range(int(hrange(2, 5, k, 1))):                          # 裂缝 + 枯草
            gx = int(hrange(a_ + 2, b_ - 2, k, s, 2))
            px(d, gx, y, STN['dd'])
            if hash01(k, s, 3) < 0.7:
                px(d, gx, y - 1, (150, 128, 70))
                px(d, gx + 1, y - 1, (124, 104, 58))
                if hash01(k, s, 4) < 0.5:
                    px(d, gx - 1, y - 2, (166, 142, 80))
    hl(d, 133, 187, 147, INK)
    # 石栏墙（台阶两侧）
    for (wx0, wx1) in ((127, 132), (188, 193)):
        rect(d, wx0, 128, wx1, 146, STN['md'])
        vl(d, wx0, 128, 146, STN['lt'])
        vl(d, wx1, 128, 146, STN['dd'])
        hl(d, wx0 - 1, wx1 + 1, 127, STN['hi'])
        hl(d, wx0 - 1, wx1 + 1, 128, STN['dk'])
        for yy in (134, 140):
            hl(d, wx0, wx1, yy, STN['dk'])
        cx = (wx0 + wx1) // 2
        d.ellipse((cx - 3, 120, cx + 3, 126), fill=C(STN['md']), outline=C(INK))
        px(d, cx - 1, 122, STN['hi'])
        px(d, cx - 2, 123, STN['lt'])
        px(d, cx + 2, 124, STN['dd'])
        rect(d, cx - 2, 126, cx + 2, 127, STN['dk'])
        rect(d, wx0 - 1, 126, wx1 + 1, 126, INK)


def mansion(cv, glow):
    """整栋馆（固有色，白天的逆光已经画进去）。glow：夜里会透红光的像素（1 暗 … 3 亮）。"""
    d = cv.d
    # ---- 左塔楼（圆柱 + 尖锥顶）
    shade_cols(d, 41, 59, 62, BASE_Y, BLK, round_=True)
    stone_courses(cv.im, (41, 62, 59, BASE_Y), BLK, bh=5, bw=7, seed=1)
    for (yy0, yy1) in ((80, 92), (104, 116)):                           # 窄窗
        rect(d, 49, yy0, 51, yy1, (18, 14, 22))
        px(d, 50, yy0 - 1, (18, 14, 22))
        vl(d, 48, yy0, yy1, TRIM['lt'])
        vl(d, 52, yy0, yy1, TRIM['dk'])
        hl(d, 47, 53, yy1 + 1, TRIM['md'])
        for yy in range(yy0 + 1, yy1, 2):
            if hash01(3, yy) < 0.5:
                glow[yy, 50] = 1
    hl(d, 40, 60, 62, TRIM['hi'])                                      # 檐口
    hl(d, 40, 60, 63, TRIM['dk'])
    cone = [(37, 62), (63, 62), (50, 14)]
    roof_scales(cv.im, cone, SLATE, seed=2)
    d.line((37, 62, 50, 14), fill=C(INK))
    d.line((63, 62, 50, 14), fill=C(INK))
    d.line((38, 61, 50, 15), fill=C(RIM))                              # 逆光：左坡一道亮
    vl(d, 50, 7, 14, IRON['md'])                                       # 铁尖
    px(d, 50, 6, IRON['hi'])
    hl(d, 48, 52, 11, IRON['md'])
    # ---- 左翼
    shade_cols(d, 59, 129, 66, BASE_Y, BLK)
    stone_courses(cv.im, (60, 66, 128, BASE_Y), BLK, bh=5, bw=12, seed=3)
    # 屋顶
    roof_l = [(56, 66), (131, 66), (121, 42), (68, 42)]
    roof_scales(cv.im, roof_l, SLATE, seed=4)
    d.line((56, 66, 68, 42), fill=C(INK))
    d.line((68, 42, 121, 42), fill=C(INK))
    hl(d, 69, 120, 43, RIM)
    for x in range(70, 121, 5):                                        # 屋脊铁花
        vl(d, x, 38, 41, IRON['md'])
        px(d, x, 37, IRON['hi'])
    hl(d, 68, 121, 41, IRON['md'])
    # 烟囱
    rect(d, 72, 30, 79, 48, BLK['md'])
    vl(d, 72, 30, 48, RIM)
    vl(d, 79, 30, 48, BLK['dd'])
    rect(d, 71, 28, 80, 30, TRIM['md'])
    hl(d, 71, 80, 28, TRIM['hi'])
    for yy in range(33, 48, 3):
        hl(d, 73, 78, yy, BLK['dk'])
    # 老虎窗
    dx0, dy0, dw, dh = DORMER
    for i in range(dw + 4):
        yy = dy0 + abs(i - (dw + 4) // 2) * 0.9
        vl(d, dx0 - 2 + i, int(yy), dy0 + dh, BLK['md'] if i else RIM)
    d.line((dx0 - 2, dy0 + 6, dx0 - 2 + (dw + 4) // 2, dy0 - 1), fill=C(SLATE['lt']))
    d.line((dx0 - 2 + (dw + 4) // 2, dy0 - 1, dx0 + dw + 2, dy0 + 6), fill=C(SLATE['dk']))
    rect(d, dx0 + 2, dy0 + 5, dx0 + dw - 2, dy0 + dh - 1, (14, 10, 16))      # 碎了的窗洞（黑）
    px(d, dx0 + 3, dy0 + 6, (110, 116, 136))                                # 残玻璃
    px(d, dx0 + 4, dy0 + 6, (80, 84, 104))
    px(d, dx0 + dw - 3, dy0 + dh - 2, (96, 100, 120))
    hl(d, dx0 + 1, dx0 + dw - 1, dy0 + dh, TRIM['md'])
    # 楼层线 + 檐口
    hl(d, 58, 130, 66, TRIM['hi'])
    hl(d, 58, 130, 67, TRIM['md'])
    hl(d, 58, 130, 68, TRIM['dd'])
    hl(d, 59, 129, 108, TRIM['lt'])
    hl(d, 59, 129, 109, TRIM['dk'])
    hl(d, 59, 129, 136, TRIM['md'])                                   # 墙基
    hl(d, 59, 129, 137, TRIM['lt'])
    rect(d, 59, 138, 129, BASE_Y, TRIM['dk'])
    # ---- 中间门楼
    shade_cols(d, 129, 191, 54, BASE_Y, BLK)
    stone_courses(cv.im, (130, 54, 190, BASE_Y), BLK, bh=5, bw=10, seed=5)
    # 方塔 + 百叶拱窗
    shade_cols(d, 140, 180, 33, 54, BLK)
    stone_courses(cv.im, (141, 33, 179, 54), BLK, bh=5, bw=8, seed=6)
    for cx in (151, 169):
        rect(d, cx - 3, 40, cx + 3, 51, (18, 14, 22))
        d.pieslice((cx - 3, 37, cx + 3, 43), 180, 360, fill=C((18, 14, 22)))
        for yy in range(42, 51, 2):
            hl(d, cx - 3, cx + 3, yy, (54, 50, 62))                    # 百叶
        vl(d, cx - 4, 39, 51, TRIM['lt'])
        vl(d, cx + 4, 39, 51, TRIM['dk'])
        hl(d, cx - 4, cx + 4, 52, TRIM['md'])
    hl(d, 138, 182, 33, TRIM['hi'])
    hl(d, 138, 182, 34, TRIM['dk'])
    # 尖顶
    spire = [(136, 33), (184, 33), (160, 3)]
    roof_scales(cv.im, spire, SLATE, seed=7)
    d.line((136, 33, 160, 3), fill=C(INK))
    d.line((184, 33, 160, 3), fill=C(INK))
    d.line((137, 32, 159, 4), fill=C(RIM))
    for (ax, ay) in ((148, 18), (172, 18)):                            # 尖顶上两个小天窗
        rect(d, ax - 1, ay, ax + 1, ay + 4, (18, 14, 22))
        px(d, ax, ay - 1, SLATE['lt'])
    vl(d, 160, 0, 3, IRON['md'])                                       # 风向标的杆（标在 strip）
    # 门楼顶的女儿墙（城齿）+ 两角尖塔
    for x in range(129, 192):
        hl(d, x, x, 54, TRIM['md'] if x % 6 < 3 else TRIM['dk'])
        if x % 6 < 3:
            vl(d, x, 50, 53, TRIM['md'])
            px(d, x, 50, TRIM['hi'] if x < 160 else TRIM['lt'])
    for cx in (131, 189):
        rect(d, cx - 2, 40, cx + 2, 56, TRIM['md'])
        vl(d, cx - 2, 40, 56, TRIM['hi'])
        vl(d, cx + 2, 40, 56, TRIM['dd'])
        for k in range(8):
            hw = max(0, 2 - k // 3)
            hl(d, cx - hw, cx + hw, 39 - k, TRIM['lt'] if k % 2 else TRIM['md'])
        px(d, cx, 31, IRON['hi'])
    rose_window(cv, *ROSE, glow_mask=glow)
    # 门楼两侧的窄尖窗
    for cx in (138, 182):
        lancet(cv, cx, 66, 92, 6, kind='slit', seed=cx)
    hl(d, 129, 191, 108, TRIM['lt'])
    hl(d, 129, 191, 109, TRIM['dk'])
    portal(cv)
    hl(d, 129, 191, 137, TRIM['lt'])
    rect(d, 129, 138, 191, BASE_Y, TRIM['dk'])
    # ---- 右翼（比左翼矮，屋顶右端是斜脊）
    shade_cols(d, 191, 253, 70, BASE_Y, BLK)
    stone_courses(cv.im, (192, 70, 253, BASE_Y), BLK, bh=5, bw=12, seed=8)
    roof_r = [(189, 70), (256, 70), (212, 51), (197, 51)]
    roof_scales(cv.im, roof_r, SLATE, seed=9)
    d.line((189, 70, 197, 51), fill=C(INK))
    d.line((197, 51, 212, 51), fill=C(INK))
    d.line((212, 51, 256, 70), fill=C(INK))
    hl(d, 198, 211, 52, RIM)
    for x in range(199, 212, 4):
        vl(d, x, 47, 50, IRON['md'])
        px(d, x, 46, IRON['hi'])
    hl(d, 197, 212, 50, IRON['md'])
    rect(d, 205, 38, 211, 54, BLK['md'])                               # 烟囱
    vl(d, 205, 38, 54, RIM)
    vl(d, 211, 38, 54, BLK['dd'])
    rect(d, 204, 36, 212, 38, TRIM['md'])
    hl(d, 204, 212, 36, TRIM['hi'])
    hl(d, 189, 256, 70, TRIM['hi'])
    hl(d, 189, 256, 71, TRIM['md'])
    hl(d, 189, 256, 72, TRIM['dd'])
    hl(d, 191, 253, 108, TRIM['lt'])
    hl(d, 191, 253, 109, TRIM['dk'])
    hl(d, 191, 253, 136, TRIM['md'])
    hl(d, 191, 253, 137, TRIM['lt'])
    rect(d, 191, 138, 253, BASE_Y, TRIM['dk'])
    vl(d, 253, 72, BASE_Y, BLK['dd'])
    # ---- 窗（楼上黑帘、楼下木板）
    for (cx, w) in UP_WIN:
        lancet(cv, cx, UP_Y0 if w == 14 else UP_Y0 + 2, UP_Y1, w, kind='curtain', seed=cx, glow_mask=glow)
        lancet(cv, cx, LOW_Y0, LOW_Y1, w - 2 if w == 14 else w, kind='boards', seed=cx + 1)
    # 开间之间的扶壁（细竖条）
    for x in (89, 110, 210, 230):
        vl(d, x, 70, 135, BLK['lt'])
        vl(d, x + 1, 70, 135, BLK['dk'])
    # 枯死的爬山虎（左翼墙角往上爬：细的褐色枝，几片干叶）
    vines = [(61, 138, 22, 1), (66, 138, 34, 2), (125, 138, 26, 3)]
    for (vx, vy, L, s) in vines:
        x, y = vx, vy
        for k in range(L):
            px(d, x, y, (78, 60, 44))
            if hash01(s, k) < 0.25:
                px(d, x + (1 if hash01(s, k, 1) < 0.5 else -1), y, (112, 86, 52))
            y -= 1 if hash01(s, k, 2) < 0.8 else 0
            x += int(round(hrange(-1, 1, s, k, 3))) if k % 3 == 0 else 0
    # 外轮廓墨线（馆的剪影边：只描对着天的那一圈，靠逆光亮边之外）
    _rim_ink(cv.im)


def _rim_ink(im):
    """不透明区域靠天的那一圈描 1 px 墨线（只往外描：上、左、右）。"""
    a = np.array(im)
    m = a[..., 3] > 0
    edge = np.zeros_like(m)
    edge[1:, :] |= m[:-1, :] & ~m[1:, :]
    edge[:-1, :] |= m[1:, :] & ~m[:-1, :]
    edge[:, 1:] |= m[:, :-1] & ~m[:, 1:]
    edge[:, :-1] |= m[:, 1:] & ~m[:, :-1]
    edge[BASE_Y:, :] = False
    a[edge, :3] = INK
    a[edge, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))


# ============================================================ 围栏 / 大门 / 树 / 地面
def gargoyle(d, x, y, face):
    """门柱顶上的石雕滴水兽（蹲着、收着翅膀、头往外探；约 9×9）：x = 中心、y = 脚。face = −1 朝左 / 1 朝右。"""
    s = face
    body = [(-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1),
            (-2, -2), (-1, -2), (0, -2), (1, -2), (-1, -3), (0, -3), (1, -3), (-1, -4), (0, -4)]
    for (dx, dy) in body:
        px(d, x + dx * s, y + dy, STN['md'])
    for (dx, dy) in ((-2, -3), (-3, -4), (-3, -5), (-2, -5), (-4, -6)):          # 收着的翅膀（往后上翘）
        px(d, x + dx * s, y + dy, STN['dk'])
    for (dx, dy) in ((1, -4), (2, -4), (2, -5), (3, -5), (1, -5), (3, -4)):      # 头往外探
        px(d, x + dx * s, y + dy, STN['md'])
    px(d, x + 2 * s, y - 6, STN['dk'])                                         # 角
    px(d, x + 4 * s, y - 5, STN['dk'])                                         # 嘴
    px(d, x + 3 * s, y - 5, (150, 40, 40))                                     # 一点红眼（风化的漆）
    px(d, x + (-2 if s > 0 else 2), y - 1, STN['hi'])
    px(d, x - 1 * s, y - 3, STN['lt'])


def fence(cv):
    d = cv.d
    # 基座
    for (x0, x1) in ((36, 133), (187, PW - 1)):
        rect(d, x0, 143, x1, 146, STN['md'])
        hl(d, x0, x1, 142, STN['hi'])
        hl(d, x0, x1, 143, STN['lt'])
        hl(d, x0, x1, 146, STN['dk'])
        for x in range(x0 + 3, x1, 9):
            vl(d, x, 143, 146, STN['dk'])
        # 铁栏
        for x in range(x0 + 2, x1 - 1, 4):
            vl(d, x, 118, 141, IRON['dk'])
            px(d, x, 117, IRON['md'])
            px(d, x, 116, IRON['hi'])
            px(d, x - 1, 118, IRON['dk'])
            px(d, x + 1, 118, IRON['dk'])
        for yy in (122, 137):
            hl(d, x0, x1, yy, IRON['md'])
            hl(d, x0, x1, yy + 1, IRON['dd'])
        for x in range(x0 + 4, x1 - 1, 8):                          # 横档之间的小卷花
            px(d, x, 124, IRON['md'])
            px(d, x - 1, 125, IRON['md'])
            px(d, x + 1, 125, IRON['md'])
    # 石柱
    for (x0, top, deco) in ((30, 104, 'ball'), (134, 98, 'garg_l'), (178, 98, 'garg_r'), (296, 106, 'ball')):
        x1 = x0 + 8
        rect(d, x0, top, x1, 146, STN['md'])
        vl(d, x0, top, 146, STN['hi'])
        vl(d, x0 + 1, top, 146, STN['lt'])
        vl(d, x1, top, 146, STN['dd'])
        vl(d, x1 - 1, top, 146, STN['dk'])
        for yy in range(top + 6, 146, 7):
            hl(d, x0 + 1, x1 - 1, yy, STN['dk'])
        rect(d, x0 - 1, top - 3, x1 + 1, top - 1, STN['lt'])
        hl(d, x0 - 1, x1 + 1, top - 3, STN['hi'])
        hl(d, x0 - 1, x1 + 1, top - 1, STN['dk'])
        cx = x0 + 4
        if deco == 'ball':
            d.ellipse((cx - 3, top - 10, cx + 3, top - 4), fill=C(STN['md']), outline=C(INK))
            px(d, cx - 1, top - 8, STN['hi'])
            px(d, cx + 2, top - 6, STN['dd'])
        else:
            gargoyle(d, cx, top - 4, -1 if deco == 'garg_l' else 1)
        vl(d, x0 - 1, top - 3, 146, INK)
        vl(d, x1 + 1, top - 3, 146, INK)
    # 大门（两扇，拱形顶）
    gx0, gx1 = 143, 177
    for x in range(gx0, gx1 + 1):
        u = abs(x - 160) / 17.0
        top = int(round(104 + 8 * u * u))
        if (x - gx0) % 3 == 1 or x in (gx0, gx1, 160):
            vl(d, x, top, 146, IRON['dk'] if x != 160 else IRON['dd'])
            px(d, x, top - 1, IRON['md'])
            px(d, x, top - 2, IRON['hi'])
        hl(d, x, x, top + 2, IRON['md'])
        hl(d, x, x, top + 3, IRON['dd'])
    for yy in (120, 131, 141):
        hl(d, gx0, gx1, yy, IRON['md'])
        hl(d, gx0, gx1, yy + 1, IRON['dd'])
    for (sx, sy) in ((150, 125), (170, 125), (150, 136), (170, 136)):        # 卷花
        d.ellipse((sx - 2, sy - 2, sx + 2, sy + 2), outline=C(IRON['md']))
        px(d, sx - 1, sy - 2, IRON['hi'])
    # 门顶中间的铁纹章（圆牌 + 一只展翅蝙蝠的剪影）
    d.ellipse((155, 104, 165, 114), fill=C(IRON['dk']), outline=C(IRON['hi']))
    for (dx, dy) in ((0, 0), (0, 1), (-1, 0), (1, 0), (-2, -1), (2, -1), (-3, 0), (3, 0), (-3, -1), (3, -1), (-1, -1), (1, -1)):
        px(d, 160 + dx, 109 + dy, IRON['hi'])
    hl(d, gx0, gx1, 146, IRON['dd'])
    # 门柱上的门闩（铁）
    rect(d, 158, 128, 162, 130, IRON['md'])
    px(d, 159, 128, IRON['hi'])


def tree(cv):
    """枯树（逆光：几乎是剪影，只在左边描一道亮边）：粗而扭的树干在围栏后面，往左上弯；三根主枝再一层层分叉，
    细枝像手指；往左上那根伸到乌鸦脚下（anchors.crow），那一段是平的。"""
    d = cv.d
    bark_md, bark_dk, bark_dd = BARK_N['md'], BARK_N['dk'], BARK_N['dd']
    rim = BARK_N['rim']
    # 树干：从 (262,146) 往上到 y 92，底宽 14、顶宽 7，带一点扭
    top = None
    for k in range(0, 55):
        y = 146 - k
        x = TREE_X + int(round(-4 * math.sin(k / 54 * math.pi * 0.55) + 0.8 * math.sin(k * 0.33)))
        w = int(round(14 - k * 0.13)) + (2 if k < 4 else 0)
        x0 = x - w // 2
        hl(d, x0, x0 + w - 1, y, bark_md)
        px(d, x0, y, rim)
        px(d, x0 + 1, y, BARK_N['lt'])
        hl(d, x0 + w - 3, x0 + w - 1, y, bark_dk)
        px(d, x0 + w - 1, y, bark_dd)
        if hash01(21, y) < 0.45:                                       # 树皮竖纹
            px(d, x0 + int(hrange(2, w - 2, 21, y, 1)), y, bark_dd)
        top = (x, y, w)
    d.ellipse((258, 112, 263, 120), fill=C((14, 10, 14)))                # 树洞
    px(d, 258, 114, BARK_N['lt'])
    for (rx, s_) in ((253, -1), (271, 1)):                              # 露出基座的树根
        for k in range(6):
            px(d, rx + s_ * k, 146 - (k // 2), bark_md)
            px(d, rx + s_ * k, 147 - (k // 2), bark_dd)

    def limb(x0, y0, x1, y1, w0, w1=1, bend=0.0):
        n = int(max(abs(x1 - x0), abs(y1 - y0), 1))
        for s in range(n + 1):
            u = s / n
            x = x0 + (x1 - x0) * u + bend * math.sin(math.pi * u)
            y = y0 + (y1 - y0) * u
            w = max(1, int(round(w0 + (w1 - w0) * u)))
            xx, yy = int(round(x)), int(round(y))
            for j in range(w):
                c = bark_dk if (j == w - 1 or w == 1) else bark_md
                px(d, xx - w // 2 + j, yy, c)
            if w >= 2:
                px(d, xx - w // 2, yy, rim)

    def twigs(x, y, ang, L, depth, seed):
        """一根细枝再分两叉（往上、往外伸，像手指）。"""
        if depth == 0 or L < 3:
            return
        x1 = x + L * math.cos(ang)
        y1 = y - L * math.sin(ang)
        limb(x, y, x1, y1, 2 if depth > 2 else 1, 1)
        for k, da in enumerate((-0.45, 0.4)):
            twigs(x1, y1, ang + da + hrange(-0.2, 0.2, seed, k), L * hrange(0.55, 0.75, seed, k, 1), depth - 1,
                  seed * 3 + k + 1)
    tx, ty, tw = top
    # 往左上那根：伸到乌鸦脚下，x 231–248 那一段在 y 60–62 是平的
    limb(tx - 2, ty + 2, 248, 62, 6, 3, bend=-3)
    for x in range(231, 249):
        px(d, x, 60, rim if x < 236 else BARK_N['lt'])
        px(d, x, 61, bark_md)
        px(d, x, 62, bark_dd)
    px(d, 230, 61, bark_dk)
    twigs(231, 61, math.radians(150), 9, 3, 1)
    twigs(236, 62, math.radians(215), 7, 2, 2)
    twigs(247, 60, math.radians(100), 8, 2, 3)
    # 往右上那根
    limb(tx + 2, ty + 1, 290, 40, 6, 2, bend=4)
    twigs(290, 40, math.radians(70), 10, 3, 4)
    twigs(290, 40, math.radians(20), 9, 3, 5)
    twigs(280, 54, math.radians(-10), 10, 2, 6)
    # 往上那根
    limb(tx, ty, 266, 26, 6, 2, bend=-3)
    twigs(266, 26, math.radians(120), 9, 3, 7)
    twigs(266, 26, math.radians(70), 10, 3, 8)
    twigs(262, 52, math.radians(140), 8, 2, 9)
    twigs(256, 84, math.radians(200), 7, 2, 10)                         # 下面一根短断枝


def ground(cv):
    """院子（围栏后：枯草 + 碎石小路）+ 街面（土路：几颗小石子、两道很浅的车辙；可走带对比压低）。"""
    d = cv.d
    rect(d, 0, BASE_Y + 1, PW - 1, FENCE_Y - 1, (112, 98, 66))          # 院子的枯草地（大半被基座挡着）
    for x in range(0, PW):
        for y in range(BASE_Y + 1, FENCE_Y):
            r = hash01(31, x, y)
            if r < 0.2:
                px(d, x, y, (138, 120, 76))
            elif r < 0.32:
                px(d, x, y, (88, 76, 54))
    rect(d, 141, BASE_Y + 1, 179, FENCE_Y - 1, (150, 140, 124))          # 碎石小路
    a = np.array(cv.im)
    y0 = FENCE_Y
    rows = H - y0
    base = np.array(DIRT['base'], np.float32)
    nz = A._fbm(PW + 8, rows + 8, 10, seed=41)[4:4 + rows, 4:4 + PW]
    col = np.empty((rows, PW, 3), np.float32)
    col[:] = base
    col *= (1 + 0.045 * (nz - 0.5) * 2)[..., None]
    col[0] = np.array(DIRT['dd'], np.float32)                          # 围栏脚下一道影
    col[1] = np.array(DIRT['dk'], np.float32)
    col[2] = np.array(DIRT['dk'], np.float32) * 0.5 + base * 0.5
    for (ry, s) in ((158, 1), (168, 2)):                              # 两道很浅的车辙（整行一样亮：不算“不平”）
        col[ry - y0] = col[ry - y0] * 0.965
    a[y0:, :, :3] = np.clip(col, 0, 255).astype(np.uint8)
    a[y0:, :, 3] = 255
    for i in range(140):                                               # 小石子（1–2 px，亮一点点）
        x = int(hrange(0, PW - 2, 43, i))
        y = int(hrange(y0 + 4, H - 1, 43, i, 1))
        if 3 <= x <= 44 and 149 <= y <= 167:            # 吉普停车位：剧情摆车，这块地面一颗石子都不放（自检要求平地）
            continue
        c = DIRT['lt'] if hash01(43, i, 2) < 0.7 else DIRT['dk']
        a[y, x, :3] = c
        if hash01(43, i, 3) < 0.3:
            a[y, x + 1, :3] = DIRT['dk']
    cv.im.paste(Image.fromarray(a, 'RGBA'))
    # 围栏脚的一溜杂草（在基座下沿，不进可走带）
    for x in range(36, PW, 3):
        if 133 < x < 187:
            continue
        if hash01(47, x) < 0.5:
            px(d, x, FENCE_Y - 1, (128, 112, 64))
            px(d, x + 1, FENCE_Y - 2, (150, 130, 74))


def lamp_post(cv):
    """左边一根没点的煤气路灯（铁杆 + 四面玻璃的灯笼 + 顶上的小尖）：夜里也不亮——这条街没人管。"""
    d = cv.d
    x = 22
    vl(d, x, 104, FENCE_Y, IRON['md'])
    vl(d, x - 1, 104, FENCE_Y, IRON['hi'])
    vl(d, x + 1, 104, FENCE_Y, IRON['dd'])
    rect(d, x - 2, FENCE_Y - 4, x + 2, FENCE_Y, IRON['md'])
    hl(d, x - 3, x + 3, 112, IRON['md'])
    rect(d, x - 3, 98, x + 3, 104, (60, 62, 72))
    vl(d, x - 3, 98, 104, IRON['dk'])
    vl(d, x + 3, 98, 104, IRON['dk'])
    vl(d, x, 98, 104, IRON['dk'])
    px(d, x - 2, 99, (130, 136, 150))
    hl(d, x - 4, x + 4, 97, IRON['md'])
    hl(d, x - 3, x + 3, 96, IRON['hi'])
    px(d, x, 94, IRON['md'])
    px(d, x, 95, IRON['md'])


# ============================================================ 合成：白天 / 夜里
@lru_cache(maxsize=1)
def albedo():
    """除了天和远景以外的固有色（白天的逆光已经画进去）+ 夜里透光的遮罩。"""
    cv = M.Canvas(PW, H)
    glow = np.zeros((H, PW), np.uint8)
    mansion(cv, glow)
    lamp_post(cv)
    steps_img(cv)
    ground(cv)
    tree(cv)
    fence(cv)
    return cv, glow


def _night_field():
    """夜里的乘数：整体压成月夜的冷暗（左上月亮那边略亮）+ 窗下的墙被红光染一点。"""
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    base = np.empty((H, PW, 3), np.float32)
    k = 0.30 + 0.10 * np.clip(1 - np.hypot(xx - MOON[0], yy - MOON[1]) / 260.0, 0, 1)
    base[:] = np.array((0.62, 0.70, 1.10), np.float32)
    base *= k[..., None]
    bay = A._bayer(PW, H)
    # 窗下 / 玫瑰窗周围的墙被红光染（分档 + 抖）
    for (cx, cy, r) in [(c, 90, 16) for (c, w) in UP_WIN if w == 14] + [(ROSE[0], ROSE[1], 22)]:
        g = np.clip(1 - np.hypot(xx - cx, (yy - cy) * 0.8) / r, 0, 1)
        q = np.floor(g * 3 + bay * 0.9) / 3
        base += q[..., None] * np.array((0.30, 0.06, 0.04), np.float32)
    return base


@lru_cache(maxsize=1)
def day_img():
    cv, _ = albedo()
    im = sky_day()
    im.alpha_composite(skyline(True))
    im.alpha_composite(cv.im)
    return im


def _glow_colors(glow, level=1.0):
    """夜里窗帘后的红光：glow 1 / 2 / 3 → GLOW 里的颜色；level 是亮度呼吸（0.8–1.0）。"""
    out = np.zeros((H, PW, 4), np.uint8)
    for g in (1, 2, 3):
        m = glow == g
        c = np.array(GLOW[g] if g < 3 else GLOW[3], np.float32)
        if g == 1:
            c = np.array(GLOW[1], np.float32)
        c = np.clip(c * level, 0, 255)
        out[m, :3] = c.astype(np.uint8)
        out[m, 3] = 255
    return Image.fromarray(out, 'RGBA')


@lru_cache(maxsize=1)
def night_img():
    cv, glow = albedo()
    a = np.array(cv.im).astype(np.float32)
    f = _night_field()
    a[..., :3] = np.clip(a[..., :3] * f, 0, 255)
    lit = Image.fromarray(a.astype(np.uint8), 'RGBA')
    im = sky_night()
    im.alpha_composite(skyline(False))
    im.alpha_composite(lit)
    im.alpha_composite(_glow_colors(glow, 1.0))
    return im


# ============================================================ strip
CROW_GRID = (
    # 朝左站着的乌鸦（12×9，最后一行是脚，踩在树枝 y 60 上面一行）：k 身子、s 翅膀的蓝紫光泽、b 嘴、e 眼、f 脚、
    # r 头顶的逆光（剪影在亮天前面也要分得出头和背）
    '..rrr.......',
    'bbkekk......',
    '..kkkkk.....',
    '...kkkkkk...',
    '...kksskkk..',
    '...kkkssskkk',
    '....kkkkk.kk',
    '.....kkk...k',
    '.....f.f....',
)
CROW_TILT = (                                                          # 歪头：脸转过来看人，嘴往下斜，露出两只红眼
    '...rr.......',
    '..kkkk......',
    '.bekek......',
)


def _crow_frame(f):
    """树枝上的乌鸦（脚在 CROW_FOOT，朝左）：8 帧——呼吸（翅膀光泽上下挪 1 px）、第 2 帧尾巴一翘、第 3 帧头往前探、
    第 4–5 帧歪头（脸转过来，两点红眼）、第 6 帧眨眼、第 7 帧背上的羽毛抖一下。不叫（“连乌鸦都不叫”）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    pal = {'k': (20, 16, 26), 's': (66, 68, 104), 'b': (70, 64, 58), 'e': (220, 48, 40), 'f': (70, 64, 58),
           'r': (112, 104, 122)}
    rows = [list(r) for r in CROW_GRID]
    if f in (4, 5):
        rows = [list(r) for r in CROW_TILT] + rows[3:]
        rows[3][0] = 'b'
        if f == 5:
            rows[0] = list('..rr........')
    if f == 6:
        rows[1] = list(''.join(rows[1]).replace('e', 'k'))
    if f in (1, 2):                                                    # 呼吸：光泽往上挪一行
        rows[4] = list('...kssskkk..')
        rows[5] = list('...kkkksskkk')
    if f == 2:                                                         # 尾巴一翘
        rows[6][11] = '.'
        rows[7][11] = '.'
        rows[4][10] = 'k'
        rows[4][11] = 'k'
    if f == 7:                                                         # 抖羽毛
        rows[2][7] = 'k'
        rows[3][9] = 'k'
        rows[2][8] = 'k'
    if f == 3:                                                         # 头往前探一点（要歪头了）
        rows[0] = list('.rrr........')
        rows[1] = list('bkekk.......')
        rows[2] = list('.kkkkkk.....')
    x0, y0 = CROW_FOOT[0] - 5, CROW_FOOT[1] - 1 - (len(rows) - 1)
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                px(d, x0 + i, y0 + j, pal[ch])
    return im


def _vane_frame(f):
    """尖顶的铁风向标：一只展翅蝙蝠，绕杆转一圈（8 帧：侧面 → 斜 → 正面窄 → 斜 → 侧面反过来 …）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y = 160, 1
    widths = (5, 4, 1, 4, 5, 4, 1, 4)
    w = widths[f]
    flip = 1 if f < 4 else -1
    col = IRON['dk']
    px(d, x, y, IRON['hi'])
    if w <= 1:
        vl(d, x, y - 1, y + 1, col)
        return im
    for k in range(1, w + 1):
        px(d, x - k, y, col)
        px(d, x + k, y, col)
        if k == w:
            px(d, x - k, y - 1, col)
            px(d, x + k, y - 1, col)
    px(d, x + flip * (w // 2), y + 1, col)                              # 一侧垂下的尾 / 头（看出朝向）
    px(d, x - flip, y - 1, IRON['hi'])
    return im


def _curtain_raw(f):
    """老虎窗碎玻璃里飘出来的一角黑帘（风从左边来：往右外飘，8 帧摆一个来回）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    dx0, dy0, dw, dh = DORMER
    x0, y0 = dx0 + dw - 3, dy0 + 6
    ph = math.sin(f / N8 * math.tau)
    L = 7
    for k in range(L):
        u = k / (L - 1)
        sway = int(round((2 + 2 * ph) * u + 0.8 * math.sin(f / N8 * math.tau * 2 + k) * u))
        y = y0 + k
        w = 2 if k < L - 2 else 1
        for j in range(w):
            c = CURTAIN['lt'] if j == 0 else CURTAIN['dk']
            px(d, x0 + sway + j, y, c)
    px(d, x0 + int(round((2 + 2 * ph))) + 1, y0 + L, CURTAIN['dd'])
    return im


def _leaves_raw(f):
    """围栏脚下几片枯叶被风卷着往右滚（8 帧走 24 px 回到原位；在后沿 y 148–151，不进可走带中间）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for i, (x0, y) in enumerate(((52, 149), (94, 150), (212, 149), (276, 150))):
        x = x0 + (f * 3 + i * 7) % 24
        hop = (0, 1, 1, 0)[(f + i) % 4]
        c = (126, 92, 52) if i % 2 else (148, 110, 60)
        px(d, x, y - hop, c)
        px(d, x + 1, y - hop, dk(c, 0.8) if (f + i) % 2 else c)
    return im


def _crows_far_raw(f):
    """两只乌鸦绕尖塔盘旋（远：每只 3–5 px，8 帧绕一圈）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for i in range(2):
        a = (f / N8 + i * 0.5) * math.tau
        x = 160 + 34 * math.cos(a)
        y = 24 + 9 * math.sin(a)
        ph = (f + i * 2) % 4
        col = (30, 26, 36)
        px(d, round(x), round(y), col)
        if ph in (0, 2):
            px(d, round(x) - 1, round(y) - 1, col)
            px(d, round(x) + 1, round(y) - 1, col)
            px(d, round(x) - 2, round(y) - (2 if ph == 0 else 0), col)
            px(d, round(x) + 2, round(y) - (2 if ph == 0 else 0), col)
        else:
            px(d, round(x) - 1, round(y), col)
            px(d, round(x) + 1, round(y), col)
    return im


def _bats_raw(f):
    """夜里四只蝙蝠绕着塔楼和尖顶飞（8 帧一圈，翅膀 4 个姿势）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for i, (cx, cy, rx, ry, ph0) in enumerate(((160, 30, 46, 12, 0.0), (160, 40, 30, 8, 0.4), (54, 40, 18, 10, 0.2),
                                               (240, 30, 22, 8, 0.7))):
        a = (f / N8 + ph0) * math.tau * (1 if i % 2 == 0 else -1)
        x = cx + rx * math.cos(a)
        y = cy + ry * math.sin(a)
        M.bat(d, round(x), round(y), f + i, col=(10, 6, 16))
    return im


def _glow_raw(f):
    """夜里窗帘后的红光一明一暗（8 帧：呼吸），只画发红光的那些像素。"""
    _, glow = albedo()
    lv = 0.86 + 0.14 * math.cos(f / N8 * math.tau)
    return _glow_colors(glow, lv)


def _cache(raw):
    memo = {}

    def fn(t):
        f = M.frame_of(t, FPS)
        if f not in memo:
            memo[f] = raw(f)
        return memo[f]
    return fn


def _night_ver(raw):
    """白天的 strip 帧 → 夜里版（同一套乘数），给 night 层上面用。"""
    def fn2(f):
        im = raw(f)
        a = np.array(im).astype(np.float32)
        a[..., :3] = np.clip(a[..., :3] * _night_field(), 0, 255)
        return Image.fromarray(a.astype(np.uint8), 'RGBA')
    return fn2


crow_fn = _cache(_crow_frame)
vane_fn = _cache(_vane_frame)
curtain_fn = _cache(_curtain_raw)
curtain_n_fn = _cache(_night_ver(_curtain_raw))
leaves_fn = _cache(_leaves_raw)
crows_far_fn = _cache(_crows_far_raw)
bats_fn = _cache(_bats_raw)
glow_fn = _cache(_glow_raw)


@lru_cache(maxsize=1)
def tables():
    layers = [M.L_static('day', day_img(), crop=False)]
    for (name, fn) in (('crows_far', crows_far_fn), ('curtain', curtain_fn), ('leaves', leaves_fn)):
        layers.append(M.L_strip(name, M.auto_box(fn, N8, FPS), N8, FPS, fn))
    layers.append(M.L_static('night', night_img(), key='night', crop=False))
    for (name, fn) in (('curtain_n', curtain_n_fn), ('glow_n', glow_fn), ('bats_n', bats_fn)):
        layers.append(M.L_strip(name, M.auto_box(fn, N8, FPS), N8, FPS, fn, key='night'))
    for (name, fn) in (('vane', vane_fn), ('crow', crow_fn)):
        layers.append(M.L_strip(name, M.auto_box(fn, N8, FPS), N8, FPS, fn))
    return layers, []


def anchors():
    anc = {k: (list(v) if not isinstance(v[0], list) else [list(p) for p in v]) for k, v in ANCHORS.items()}
    anc.update(fence_y=FENCE_Y, door_box=[143, 101, 177, 139], steps_box=[133, 139, 187, 147])
    return anc


def compose(camX=0, t=0.5, state=None):
    layers, fg = tables()
    return M.compose(layers, fg, camX, t, state)


# ============================================================ 导出 / 自检
def export(ex, BJ):
    layers, fg = tables()
    st = M.export_stage(ex, PW, GROUND, WALK, layers, fg, anchors())
    if ex.check_on:
        _checks(ex, BJ, st, layers, fg)
    return st


def _checks(ex, BJ, st, layers, fg):
    cfg = dict(title='馆门口', PW=PW, walk=WALK, base=day_img(), states=[{}, {'night': 1}], stand=STAND,
               required=REQUIRED, size_limit=250 * 1024, flat=(0, PW, WALK[0], WALK[1] + 1, 18, 0.012))
    M.common_checks(ex, BJ, st, layers, fg, cfg)
    ex.checked('夜里那张整张不透明', int((np.array(night_img())[..., 3] != 255).sum()))
    # 乌鸦的脚踩在树枝上：CROW_FOOT 正下方一行是树枝（不是天）
    d = np.array(day_img())
    x, y = CROW_FOOT
    ex.checked('乌鸦脚下 (%d,%d) 是树枝' % (x, y + 1), 0 if tuple(d[y + 1, x, :3]) in (BARK_N['md'], BARK_N['lt'], BARK_N['dk'], BARK_N['dd'], BARK_N['rim']) else 1)
    # 乌鸦的剪影背后是天（看得清）：乌鸦身体那几行的背景比乌鸦亮很多
    crow = np.array(_crow_frame(0))[..., 3] > 0
    bgl = M.lum(d[..., :3].astype(np.float32))[crow].mean()
    ex.checked('乌鸦背后的亮度 %.0f ≥ 110（剪影看得清）' % bgl, 0 if bgl >= 110 else 1)
    # 吉普停车位（x 5–43，y 147–166）只有地面：没有柱子 / 灯杆伸进可走带
    ex.checked('吉普停车位 y 150–166 只有地面（和行中位差 > 18 的像素）',
               int((np.abs(M.lum(d[150:167, 5:44, :3].astype(np.float32)) -
                           np.median(M.lum(d[150:167, 5:44, :3].astype(np.float32)), axis=1, keepdims=True)) > 18).sum()))
    # 两扇调查的窗在 anchors.windows：窗洞中心那一点是黑帘
    for (wx, wy) in ANCHORS['windows']:
        c = d[wy, wx + 2, :3]
        ex.checked('窗 (%d,%d) 是拉着黑帘的窗' % (wx, wy), 0 if int(c.max()) < 80 else 1)
    # 夜里窗是红的
    n = np.array(night_img())
    for (wx, wy) in ANCHORS['windows']:
        reg = n[wy - 8:wy + 12, wx - 6:wx + 7, :3].astype(np.int32)
        red = int(((reg[..., 0] > 120) & (reg[..., 0] > reg[..., 2] * 2)).sum())
        ex.checked('夜里窗 (%d,%d) 透出红光（红像素 %d ≥ 6）' % (wx, wy, red), 0 if red >= 6 else 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch11', 'after')
    os.makedirs(od, exist_ok=True)
    out = Image.new('RGB', (PW * 2 + 4, H), (0, 0, 0))
    out.paste(compose(0, 0.5).convert('RGB'), (0, 0))
    out.paste(compose(0, 0.5, {'night': 1}).convert('RGB'), (PW + 4, 0))
    out.resize((out.width * 2, out.height * 2), Image.NEAREST).save(os.path.join(od, 'mansion_exterior_solo.png'))
    print('ok')
