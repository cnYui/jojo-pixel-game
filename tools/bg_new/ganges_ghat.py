# -*- coding: utf-8 -*-
r"""ganges_ghat —— 第4章「贝拿勒斯」：恒河边的河坛（ghat），上午的阳光。第 8 战「女帝」的场地。
2026-10-11 ch4 按体验版精度重画（改前是 later_stages.ghat()：一排三角顶的方块房 + 横条台阶）。
调色和建筑零件跟 varanasi_street.py 共用（同一座城），模块加载时引用它。

地图 640 宽、ground 158、可走带 y 148–176：一大块平整的石台（台面 146–175，压低了对比），石台前沿 176 下面
露出一窄条恒河水（177–179，往右流）；侧视平视，从河上看河坛，太阳在左上（上午）。
从左到右（世界坐标）：
  x 0–96      石台往左伸成一段码头（anchors.arrive），码头后面是水：顺着河岸往左看过去，远处一座座河坛越来越小、
              对岸一条白沙洲；水上漂着几条小木船（clouds 层慢慢漂）；码头后沿拴着一条木船（两根拴船桩、缆绳，
              strip 轻轻起伏）
  x 96–142    河坛的角楼（八角形的砂岩墩子，正面一个大拱龛、几道线脚，顶上一圈垛口 + 一座小亭子 chhatri，
              墩子脚下靠着一支船桨）
  x 142–640   宽石阶：下半段 4 级（立面 4 + 踏面 2）→ 第 5 级的踏面是中间的宽平台（y 112–117）→ 上半段 4 级
              （立面 2 + 踏面 1）→ 第二道窄平台（y 95–97）→ 再几级到 y 84，接着后面的宫殿 / 寺庙（另一层）。台阶上：
                · 五把竹伞（chhatri 草伞，半宽 19–22，伞下一张木榻 takht，榻上铜碗、彩色的点额粉、叠好的布、经书）
                  站在宽平台上，伞边的布穗 strip 飘；x 405 那把站在一块往前伸出来的石台（podium）上
                · 第二道平台上一排六座小石亭（里面一座小林伽 + 两朵万寿菊）
                · 一座小神龛（白灰、红白条的小尖顶 + 藏红小旗，龛里黑色林伽 + 三道白灰纹、花环）立在石台后沿
                  x 214–234（anchors.shrine），右边一排小油灯（strip 闪）
                · 六条顺着踏面平铺晒着的纱丽（一头搭在下面那级的立面上）、几处万寿菊花堆和散花瓣、铜水壶、
                  卷起来的草席、两个装花的竹篮、两根插小旗的竹竿；一群鸽子在台阶上啄食（strip）
  石台上 x 100 / 325 / 555（y 166）三个木桶（剧情放精灵，其中一个柏油桶）的位置只有平整的石板，后面没有大物件。
光：上午的太阳在左上（从河上照过来）；台阶的踏面最亮、立面次之、每级下沿一道暗线；伞、神龛、角楼的影子落在右下。

图层（从后往前）：
  sky       static           320×180 上午的天（偏暖、地平线发白）+ 左上的太阳
  clouds    wrap   k 0.1  vx 1.2   淡积云（640 循环）
  far       pano   k 0.3           远景 416 宽：宫殿后面更远的城（尖塔、圆顶，罩了雾）；左边一段顺着河岸看过去的远景：
                                   一座座越来越小的河坛、对岸沙洲、河面（海平线 y 104，水一直到 y 146）
  glint     strip  k 0.3           左边远景河面的波光（8 帧 @4 fps）
  boats     clouds                 远景河面上慢慢漂的三条小木船（各自的速度 / 视差）
  kites     clouds                 两只高处盘旋的黑鸢（跟窄街共用一张图）
  palace    pano   k 0.6           河坛顶上的宫殿 / 寺庙一排（512 宽）：双塔的砂岩宫殿、赭红的大宅、红白条纹墙的河边神庙
                                   （高尖塔）、刷着河坛名字的白房子、带转角小亭的淡黄宫殿、粉色圆顶楼、砂岩塔楼 + 树
  pflag     strip  k 0.6           神庙尖塔顶的藏红色三角旗（8 帧 @4 fps）
  doves     strip  k 0.6           宫殿上空绕圈的几只鸽子（8 帧 @4 fps）
  near      pano   k 1             台阶 + 角楼 + 石台 + 码头 + 拴着的船 + 伞 + 神龛 + 纱丽……（640 宽）
  boat      strip  k 1             拴着的船上下起伏 1 px + 船头船尾拍起的小水纹（8 帧 @4 fps）
  umbrellas_0…4 strip k 1          五把伞的伞面 + 布穗（各一条，8 帧 @4 fps）
  lamps     strip  k 1             神龛前的油灯火苗（8 帧 @8 fps）
  pigeons   strip  k 1             台阶上啄食的鸽子（8 帧 @4 fps）
  river     wrap   k 1   vx −5     石台前沿下面那条河（96 循环，往右流）
单独运行：python -B tools\bg_new\ganges_ghat.py → tools\bg_new\_preview\ch4\after\ganges_ghat_solo_*.png
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

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _street_mod():
    """调色 / 建筑零件跟 varanasi_street.py 共用（同一个模块名，bg_jojo.bg_new('varanasi_street') 会直接复用）。"""
    key = 'bg_new_varanasi_street'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'varanasi_street.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


V = _street_mod()
C = A._c4
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, cast_shadow, mottle, haze, opaque = (V.mul_box, V.mul_mask, V.poly_mask, V.cast_shadow,
                                                                  V.mottle, V.haze, V.opaque)
SAND_HI, SAND, SAND_S, SAND_D, SAND_K = V.SAND_HI, V.SAND, V.SAND_S, V.SAND_D, V.SAND_K
MARI_HI, MARI, MARI_D, VERMIL = V.MARI_HI, V.MARI, V.MARI_D, V.VERMIL
GOLD_HI, GOLD, GOLD_D = V.GOLD_HI, V.GOLD, V.GOLD_D
WOOD_HI, WOOD, WOOD_D, WOOD_K = V.WOOD_HI, V.WOOD, V.WOOD_D, V.WOOD_K
SHADOW_MUL, SOFT_MUL, DARK_IN = V.SHADOW_MUL, V.SOFT_MUL, V.DARK_IN

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 158
WALK = (148, 176)
CLOUD_K, CLOUD_VX = 0.1, 1.2
FAR_K, PAL_K = 0.3, 0.6
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 416
PALW = W + int(math.ceil((PW - W) * PAL_K))      # 512
HZ = 104                      # 远景河面的地平线
PLAT = 146                    # 石台后沿（台阶最下面一级的脚）
LIP = 175                     # 石台前沿的亮边
FACE = 176                    # 石台前沿的立面
WATER = 177                   # 河（177–179）
STEP_TOP = 84                 # 台阶顶（接宫殿）
LANDING = (112, 117)          # 中间那道宽平台（踏面）
LANDING2 = (95, 97)           # 上半段的第二道窄平台（一排小亭子站在上面）
JETTY_X = 96                  # 码头（左边能看到水）到这里为止
BASTION = (96, 142)           # 角楼
SHRINE = (214, 234)           # 小神龛
BARRELS = [[100, 166], [325, 166], [555, 166]]
UMBRELLAS = [(186, 0, 20), (282, 1, 22), (405, 2, 21), (500, 3, 19), (606, 4, 22)]   # (伞杆 x, 种子, 半宽)：都站在中间平台上
N_ANIM, FPS_ANIM = 8, 4.0
N_LAMP, FPS_LAMP = 8, 8.0
RIVER_P, RIVER_VX = 96, -5.0

ANCHORS = dict(
    arrive=[60, 160],          # 码头上（乔瑟夫从左边进场）
    shrine=[224, 152],         # 小神龛前
    river=[320, 178],          # 石台前沿下面的河面
    river_vista=[40, 128],     # 左边远景的河面（镜头 0 时的屏幕位置 ≈ 世界位置）
    barrels=BARRELS,
    walk_x=[10, 630],
)

# ============================================================ 调色（河坛这张自己的）
SKY_STOPS = [(84, 140, 204), (112, 164, 218), (152, 190, 228), (196, 212, 228), (236, 224, 204)]
HAZE = (226, 216, 200)
PLAT_C = (208, 192, 166)      # 石台（偏灰的砂岩，比台阶淡一点）
PLAT_S = (198, 182, 156)
PLAT_HI = (216, 202, 178)
TREAD = (232, 210, 174)       # 台阶踏面（最亮）
RISER = (206, 176, 138)       # 台阶立面
RISER_S = (192, 162, 124)
EDGE = (172, 140, 106)        # 每级下沿的暗线
WATER_C = [(126, 150, 140), (104, 132, 124), (88, 116, 112)]
VISTA_W = [(214, 220, 214), (176, 196, 196), (140, 170, 172), (116, 148, 150), (100, 132, 136)]


# ============================================================ 天空 / 云
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), SKY_STOPS, bands=12)
    A._glow(im, 54, 26, 50, 40, (255, 240, 206), 76, rings=5)
    d = ImageDraw.Draw(im)
    d.ellipse((48, 20, 60, 32), fill=C((255, 244, 214)))
    d.ellipse((50, 22, 58, 30), fill=C((255, 252, 238)))
    return im


@lru_cache(maxsize=1)
def clouds_img():
    im = A._new(640, 70)
    pal = ((255, 252, 246), (244, 238, 228), (222, 218, 214), (200, 198, 204))
    for i in range(5):
        w = hrange(44, 86, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.3, 0.42, i, 2), 800 + i, pal)
        cx = (i + hrange(0.1, 0.9, i, 3)) * 640 / 5
        y = 70 - cl.height - int(hrange(0, 26, i, 4))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    for i in range(5):
        w = hrange(14, 30, i, 11)
        cl = A._cloud_sprite(w, w * 0.3, 900 + i, pal)
        cx = (i + hrange(0.1, 0.9, i, 12)) * 640 / 5
        y = int(hrange(2, 24, i, 13))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    return im


# ============================================================ 远景（k 0.3）
def shore_y(x):
    """远景里顺着河岸往左看过去：河坛脚下那条岸线的 y（x 96 处最近、往左越来越远、贴近地平线）。"""
    u = max(0.0, min(1.0, x / 96.0))
    return HZ + 1 + int(round(14 * u ** 1.6))


@lru_cache(maxsize=1)
def far_img():
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    # 宫殿后面更远的城（x 100 以后才露出来）：一排淡淡的屋顶 + 尖塔 + 圆顶
    pal_walls = [(222, 204, 178), (232, 222, 204), (214, 190, 166), (226, 210, 190)]
    x, i = 96, 0
    while x < FARW:
        w = int(hrange(12, 26, i, 1))
        top = int(hrange(54, 74, i, 2))
        V.far_block(d, x, w, top, 120, pal_walls[i % 4], 40 + i)
        x += w
        i += 1
    for (cx, base, top, hw) in ((150, 70, 28, 9), (262, 66, 34, 7), (372, 70, 24, 10)):
        V.shikhara(im, cx, base, top, hw, pal=((240, 222, 196), (226, 206, 180), (204, 182, 160), (180, 160, 142)))
    d = ImageDraw.Draw(im)
    for (cx, cy, r) in ((206, 58, 8), (320, 60, 7)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C((236, 230, 220)))
        d.chord((cx - r, cy - r, cx + r, cy + r), 300, 60, fill=C((214, 206, 196)))
        rect(d, cx - r - 2, cy, cx + r + 2, 120, (226, 216, 200))
        vl(d, cx, cy - r - 4, cy - r - 1, (200, 172, 100))
    for (tx, ty, rx, ry, sd) in ((126, 66, 12, 7, 1), (300, 64, 10, 6, 2), (400, 62, 14, 8, 3)):
        V._canopy(d, tx, ty, rx, ry, 330 + sd, pal=((98, 126, 98), (118, 146, 110), (140, 164, 122), (164, 184, 136)))
    im = haze(im, 0.5, HAZE)
    # 顺着河岸往左看的远景（x 0–100）：天到地平线、对岸沙洲、河、一座座越来越小的河坛
    vista = A._new(FARW, H)
    gradient(vista, (0, HZ, 104, PLAT + 1), VISTA_W, bands=7)
    vd = ImageDraw.Draw(vista)
    for x in range(0, 70):                                         # 对岸沙洲：一条白沙，左边宽一点
        h = 2 + int(2 * (1 - x / 70.0))
        for y in range(HZ - h + 1, HZ + 1):
            px(vd, x, y, (236, 226, 200) if y < HZ else (214, 204, 182))
    for k in range(5):                                             # 沙洲上几点小树 / 小船
        x = int(hrange(4, 60, k, 21))
        px(vd, x, HZ - 3, (140, 150, 120))
    hl(vd, 0, 103, HZ + 1, (236, 236, 226))
    x = 100
    k = 0
    while x > 2:                                                   # 一座座河坛（往左越来越小、越来越淡）
        u = x / 100.0
        sy = shore_y(x)
        bw = max(3, int(round(4 + 18 * u ** 1.3)))
        bh = max(2, int(round(3 + 34 * u ** 1.5 * hrange(0.6, 1.0, k, 22))))
        col = [(224, 196, 152), (214, 170, 140), (232, 222, 200), (220, 186, 120), (206, 158, 128)][k % 5]
        col = mix(col, HAZE, 0.25 + 0.5 * (1 - u))
        x0 = x - bw
        rect(vd, x0, sy - bh, x - 1, sy, col)
        vl(vd, x - 1, sy - bh, sy, dk(col, 0.85))
        hl(vd, x0, x - 1, sy - bh, lt(col, 0.2))
        if bw > 6:
            for yy in range(sy - bh + 3, sy - 2, 4):
                for xx in range(x0 + 2, x - 2, 3):
                    px(vd, xx, yy, dk(col, 0.7))
        if k % 3 == 1 and bw > 5:                                  # 小尖塔
            for yy in range(int(round(5 * u + 2))):
                hl(vd, x0 + bw // 2 - (int(round(5 * u + 2)) - yy) // 3, x0 + bw // 2 + (int(round(5 * u + 2)) - yy) // 3,
                   sy - bh - int(round(5 * u + 2)) + yy, col)
        for yy in range(sy - max(1, int(5 * u)), sy + 1):          # 河坛脚下的台阶（几道亮线）
            if (yy - sy) % 2 == 0:
                hl(vd, x0, x - 1, yy, lt(col, 0.3))
        x -= bw + (1 if u < 0.4 else 0)
        k += 1
    for x in range(0, 100):                                        # 岸线下面一道倒影（淡）
        sy = shore_y(x)
        for yy in range(sy + 1, min(PLAT, sy + 1 + int(6 * x / 100.0))):
            if (yy + x) % 2 == 0:
                c = vista.getpixel((x, yy))
                px(vd, x, yy, dk(c[:3], 0.9))
    va = np.array(vista)
    va[:HZ - 4, :] = 0
    va[:, 104:] = 0
    vista = Image.fromarray(va, 'RGBA')
    im.alpha_composite(vista)
    return im


@lru_cache(maxsize=1)
def far_water_mask():
    """远景里露出来的河面（波光只画在这上面）：地平线下面、岸线 / 河坛以下的水。"""
    m = np.zeros((H, FARW), bool)
    for x in range(0, 100):
        m[shore_y(x) + 2:PLAT, x] = True
    m[:HZ + 2] = False
    return m


GLINT_BOX = (0, HZ + 1, 100, PLAT)


def glint_frame(t):
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    wm = far_water_mask()
    for i in range(46):
        y = HZ + 2 + int(hash01(i, 401) ** 1.2 * (PLAT - HZ - 3))
        x = int(hrange(0, 100, i, 402))
        ph = (f / N_ANIM + hash01(i, 403)) % 1.0
        if ph > 0.5:
            continue
        L = 1 + int((y - HZ) / 10) + (1 if ph < 0.2 else 0)
        c = (250, 248, 232) if ph < 0.22 else (206, 222, 220)
        for xx in range(x, x + L):
            if 0 <= xx < FARW and wm[y, xx]:
                px(d, xx, y, c)
    return im


def boat_img(L, col, canopy=False, oar=True):
    """远处的小木船（侧面）：船身两头翘、一道彩色船舷，可能有个小篷、船夫的剪影 + 一支桨。"""
    h = 6 + (4 if canopy else 3)
    g = A._new(L + 4, h + 2)
    d = ImageDraw.Draw(g)
    by = h - 2
    for x in range(L):
        u = x / (L - 1)
        lift = int(round(2 * (abs(u - 0.5) * 2) ** 3))
        vl(d, x + 2, by - 2 - lift, by, (92, 66, 50))
        px(d, x + 2, by - 2 - lift, col)
    hl(d, 3, L, by + 1, (70, 56, 50))
    if canopy:
        rect(d, L // 3, by - 7, L // 3 + L // 3, by - 3, (196, 160, 110))
        hl(d, L // 3 - 1, L // 3 + L // 3 + 1, by - 7, (226, 196, 140))
    else:
        rect(d, L // 2, by - 6, L // 2 + 1, by - 3, (60, 50, 50))     # 船夫
        px(d, L // 2, by - 7, (60, 50, 50))
    if oar:
        d.line((L // 2 + 2, by - 4, L // 2 + 6, by + 1), fill=C((110, 90, 70)))
    return g


BOATS = [(L, col, cn, y, vx, x0) for (L, col, cn, y, vx, x0) in (
    (16, (70, 130, 170), False, 117, 2.2, 30.0),
    (11, (200, 70, 60), True, 110, -1.4, 160.0),
    (22, (90, 150, 90), True, 128, 1.6, 120.0),
)]
BOAT_SPAN = 240
KITE_K = 0.22


# ============================================================ 宫殿 / 寺庙（k 0.6，512 宽）
def palace_tower(im, x, w, top, base, col, seed):
    """八角形的塔楼（正面 + 两个斜面）：几道线脚、拱窗、顶上一座小亭子。"""
    d = ImageDraw.Draw(im)
    s = max(2, w // 5)
    rect(d, x, top, x + w - 1, base, col)
    rect(d, x, top, x + s - 1, base, lt(col, 0.12))
    rect(d, x + w - s, top, x + w - 1, base, dk(col, 0.8))
    for yy in range(top + 6, base, 9):
        hl(d, x, x + w - 1, yy, dk(col, 0.82))
        hl(d, x, x + w - 1, yy - 1, lt(col, 0.2))
    for yy in range(top + 10, base - 8, 18):
        cx = x + w // 2
        rect(d, cx - 2, yy, cx + 1, yy + 7, dk(col, 0.45))
        hl(d, cx - 1, cx, yy - 1, dk(col, 0.45))
    V.chhatri(im, x + w // 2, top - 1, w + 2, 8)


def arch_row(d, x0, x1, y, h, col, step=7, w=4):
    """一排拱窗 / 拱廊（暗）。"""
    for xx in range(x0, x1 - w, step):
        rect(d, xx, y + 2, xx + w - 1, y + h, dk(col, 0.42))
        hl(d, xx + 1, xx + w - 2, y + 1, dk(col, 0.42))
        hl(d, xx - 1, xx + w, y + h + 1, lt(col, 0.25))
        px(d, xx, y + 2, dk(col, 0.6))


@lru_cache(maxsize=1)
def palace_img():
    im = A._new(PALW, H)
    d = ImageDraw.Draw(im)
    # 河坛顶上一道连续的砂岩墙（宫殿的台基），y 70–92；墙上一排拱门 / 拱龛
    base_top = 72
    rect(d, 100, base_top, PALW - 1, 92, (214, 184, 140))
    mottle(im, (100, base_top, PALW - 1, 92), (214, 184, 140), (200, 168, 126), (226, 198, 158), 21, cell=3)
    d = ImageDraw.Draw(im)
    hl(d, 100, PALW - 1, base_top, (236, 210, 170))
    for xx in range(108, PALW - 6, 14):
        rect(d, xx, 78, xx + 5, 90, (120, 92, 70))
        hl(d, xx + 1, xx + 4, 77, (120, 92, 70))
        px(d, xx, 78, (160, 128, 96))
    # P1 双塔砂岩宫殿（x 104–172）
    x0, x1 = 104, 172
    V.facade(im, x0, x1, 30, base_top, SAND, 31, streaks=2)
    d = ImageDraw.Draw(im)
    arch_row(d, x0 + 12, x1 - 12, 36, 8, SAND, step=6, w=3)          # 顶层拱廊
    hl(d, x0, x1 - 1, 47, SAND_HI)
    hl(d, x0, x1 - 1, 48, SAND_D)
    V.jharokha(im, 124, 52, 20, 14, (150, 104, 66), seed=3)
    for wx in (112, 152, 160):
        V.win_shutter(im, wx, 54, 5, 9, SAND, V.SHUT_G, 'closed' if wx % 3 else 'open')
    V.parapet(im, x0, x1 - 1, 28, SAND, 'arch')
    palace_tower(im, x0 - 2, 14, 16, base_top, SAND_S, 1)
    palace_tower(im, x1 - 12, 14, 16, base_top, SAND_S, 2)
    # P2 赭红大宅（x 172–230）
    x0, x1 = 172, 230
    V.facade(im, x0, x1, 26, base_top, V.TERRA, 32, streaks=3)
    d = ImageDraw.Draw(im)
    for wy in (32, 46, 60):
        for wx in range(x0 + 4, x1 - 6, 9):
            V.win_shutter(im, wx, wy, 5, 8, V.TERRA, V.SHUT_G if (wx + wy) % 3 else V.SHUT_B,
                          ('closed', 'open', 'half')[(wx // 9 + wy) % 3])
    V.parapet(im, x0, x1 - 1, 24, V.TERRA, 'post')
    d = ImageDraw.Draw(im)
    V.wire(d, x0 + 3, 21, x1 - 4, 21, 1, (90, 86, 90))                 # 屋顶晾衣绳
    for k, xx in enumerate(range(x0 + 5, x1 - 6, 5)):
        c = V.CLOTH[k % len(V.CLOTH)]
        rect(d, xx, 22, xx + 2, 25 + k % 3, c)
    V.tv_antenna(d, x1 - 10, 8, 14)
    # P3 河边神庙（x 230–292）：红白竖条纹的围墙 + 高尖塔
    x0, x1 = 230, 292
    flag = V.shikhara(im, 261, 62, 14, 17, minis=True)               # 尖塔在围墙后面（先画）
    d = ImageDraw.Draw(im)
    for x in range(x0, x1):
        c = (236, 228, 214) if ((x - x0) // 4) % 2 else (200, 88, 62)
        vl(d, x, 56, base_top, c)
    V.parapet(im, x0, x1 - 1, 54, (226, 216, 200), 'arch')
    d = ImageDraw.Draw(im)
    rect(d, 255, 62, 267, base_top, (60, 44, 40))                    # 神庙门
    hl(d, 254, 268, 61, SAND_HI)
    vl(d, 254, 62, base_top, SAND_HI)
    vl(d, 268, 62, base_top, SAND_D)
    V.draw_garland(d, 255, 63, 267, 63, 3)
    rect(d, 259, 66, 263, base_top - 1, (226, 92, 44))               # 门里一点朱红（神像）
    V.chhatri(im, x0 + 7, 54, 10, 8)
    V.chhatri(im, x1 - 8, 54, 10, 8)
    # P4 白房子（x 292–340），墙上刷着河坛的名字（白底红字，色块）
    x0, x1 = 292, 340
    V.facade(im, x0, x1, 34, base_top, V.LIME, 34, streaks=3)
    d = ImageDraw.Draw(im)
    V.sign_board(d, x0 + 3, 50, x1 - 4, 62, (246, 240, 226), (176, 40, 40), rows=2, seed=41, border=(176, 40, 40))
    for wx in (x0 + 6, x0 + 22, x0 + 36):
        V.win_shutter(im, wx, 38, 6, 8, V.LIME, V.SHUT_B, 'open' if wx % 2 else 'closed')
    V.parapet(im, x0, x1 - 1, 32, V.LIME, 'plain')
    d = ImageDraw.Draw(im)
    rect(d, x0 + 26, 22, x0 + 40, 31, (226, 210, 186))
    rect(d, x0 + 29, 25, x0 + 32, 31, (120, 100, 90))
    V.water_tank(d, x0 + 6, 25, 10, 7)
    # P5 淡黄大宫殿（x 340–424）：一排拱窗、阳台、转角小亭
    x0, x1 = 340, 424
    V.facade(im, x0, x1, 20, base_top, (232, 206, 132), 35, streaks=3)
    d = ImageDraw.Draw(im)
    arch_row(d, x0 + 4, x1 - 2, 26, 9, (232, 206, 132), step=8, w=4)
    V.chajja(im, x0, x1 - 1, 38, (240, 220, 160))
    for k, wx in enumerate(range(x0 + 6, x1 - 8, 14)):
        V.win_arch(im, wx, 44, 7, 14, (232, 206, 132), (246, 236, 214), seed=k)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, 62, (246, 232, 190))
    rect(d, x0, 63, x1 - 1, 64, (196, 170, 104))
    for xx in range(x0 + 1, x1 - 1, 3):
        vl(d, xx, 58, 62, (200, 176, 110))
    V.parapet(im, x0, x1 - 1, 18, (232, 206, 132), 'post')
    V.chhatri(im, x0 + 8, 18, 14, 10)
    V.chhatri(im, x1 - 9, 18, 14, 10)
    # P6 粉色圆顶楼（x 424–470）
    x0, x1 = 424, 470
    V.facade(im, x0, x1, 34, base_top, V.PINK, 36, streaks=2)
    d = ImageDraw.Draw(im)
    for wx in range(x0 + 4, x1 - 6, 10):
        V.win_arch(im, wx, 40, 6, 14, V.PINK, (240, 230, 220), seed=wx)
    V.parapet(im, x0, x1 - 1, 32, V.PINK, 'plain')
    d = ImageDraw.Draw(im)
    for (cx, r) in ((x0 + 14, 7), (x0 + 32, 5)):
        d.ellipse((cx - r, 32 - r * 2, cx + r, 32), fill=C((240, 226, 222)))
        d.chord((cx - r, 32 - r * 2, cx + r, 32), 300, 60, fill=C((214, 196, 192)))
        vl(d, cx, 32 - r * 2 - 4, 32 - r * 2 - 1, GOLD)
    # P7 砂岩塔楼 + 树（x 470–512）
    palace_tower(im, 474, 18, 22, base_top, (210, 176, 128), 3)
    V.facade(im, 492, PALW, 40, base_top, V.OCHRE, 37, streaks=2)
    d = ImageDraw.Draw(im)
    for wx in (496, 506):
        V.win_shutter(im, wx, 48, 5, 9, V.OCHRE, V.SHUT_G, 'closed')
    V.parapet(im, 492, PALW - 1, 38, V.OCHRE, 'plain')
    d = ImageDraw.Draw(im)
    # 宫殿之间冒出来的树冠（菩提）
    for (tx, ty, rx, ry, sd) in ((170, 22, 12, 9, 1), (342, 18, 10, 8, 2), (470, 34, 12, 9, 3)):
        V._canopy(d, tx, ty, rx, ry, 520 + sd, pal=((50, 96, 54), (70, 128, 64), (102, 160, 78), (150, 194, 98)))
    # 台基墙上的几块招贴 / 涂的朱红
    for (xx, yy, sd) in ((118, 80, 1), (306, 80, 3), (446, 80, 4)):
        V.poster(im, xx, yy, 6, 8, 30 + sd, fade=0.3)
    im = haze(im, 0.14, HAZE)
    a = np.array(im)
    a[93:, :] = 0                                                   # 只留 y ≤ 92（下面被台阶盖住）
    return Image.fromarray(a, 'RGBA'), flag


PFLAG_BOX = (260, 0, 276, 12)


def pflag_frame(t):
    im = A._new(PALW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    gx, gy = palace_parts()[1]
    for i in range(1, 12):
        u = i / 11
        wav = 1.2 * math.sin(math.tau * f / N_ANIM - u * 4.0) * u
        hh = int(round(4 * (1 - u) + 1))
        y0 = round(gy + 1 + wav + u * 1.5)
        for r in range(hh):
            c = V.SAFFRON if r < hh - 1 else dk(V.SAFFRON, 0.75)
            px(d, gx + i, y0 + r, c)
    return im


DOVE_BOX = (300, 0, 420, 40)


def doves_frame(t):
    """宫殿上空绕圈的鸽子（宫殿层坐标）：7 只，绕一个扁椭圆，翅膀一上一下。"""
    im = A._new(PALW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    cx, cy = 360, 18
    for i in range(7):
        ph = math.tau * (f / N_ANIM + i / 7.0 * 0.5 + hash01(i, 91) * 0.05)
        x = round(cx + (48 + 6 * hash01(i, 92)) * math.cos(ph))
        y = round(cy + (11 + 3 * hash01(i, 93)) * math.sin(ph))
        col = (96, 98, 110) if math.sin(ph) > 0 else (128, 130, 142)
        px(d, x, y, col)
        if (f + i) % 2 == 0:
            px(d, x - 1, y - 1, col)
            px(d, x + 1, y - 1, col)
        else:
            px(d, x - 1, y, col)
            px(d, x + 1, y, col)
    return im


@lru_cache(maxsize=1)
def palace_parts():
    return palace_img()


# ============================================================ 近景：台阶 / 石台 / 码头
def step_rows():
    """台阶从下往上的每一行是什么：返回 {y: ('tread' | 'riser' | 'edge' | 'landing', 第几级)}。
    下半段 4 级（立面 4：最下一行是暗线 + 踏面 2）→ 第 5 级的踏面就是中间的宽平台 LANDING（6 行）→
    上半段 4 级（立面 2 + 踏面 1）→ 第二道窄平台 LANDING2（3 行）→ 再往上几级到 STEP_TOP。"""
    rows = {}
    st = dict(y=PLAT - 1, k=0)

    def step(riser, tread, kind='tread'):
        y, k = st['y'], st['k']
        for r in range(riser):
            if y - r >= STEP_TOP:
                rows[y - r] = ('edge' if r == 0 else 'riser', k)
        y -= riser
        for r in range(tread):
            if y - r >= STEP_TOP:
                rows[y - r] = (kind, k)
        st['y'], st['k'] = y - tread, k + 1

    for _ in range(4):
        step(4, 2)
    step(4, LANDING[1] - LANDING[0] + 1, 'landing')
    for _ in range(4):
        step(2, 1)
    step(2, LANDING2[1] - LANDING2[0] + 1, 'landing')
    while st['y'] >= STEP_TOP:
        step(2, 1)
    return rows


ROWS = step_rows()


def is_tread(y):
    return ROWS.get(y, ('', 0))[0] in ('tread', 'landing')


def draw_steps(im):
    """x 142–640 的宽石阶：踏面亮、立面次之、每级下沿一道暗线；石块竖缝（每级错开）、缺角、磨亮的踏面中间，
    上半段越往上越淡（离得远）。"""
    a = np.array(im)
    nz = A._fbm(PW + 8, H + 8, 4, seed=77)[4:4 + H, 4:4 + PW]
    x0 = BASTION[1]
    for y in range(STEP_TOP, PLAT):
        kind, k = ROWS[y]
        far = max(0.0, (LANDING[0] - y) / (LANDING[0] - STEP_TOP))      # 上半段越往上越远
        for x in range(x0, PW):
            if kind in ('tread', 'landing'):
                c = TREAD
                if nz[y, x] > 0.62:
                    c = mix(TREAD, RISER, 0.35)
                elif nz[y, x] < 0.3:
                    c = lt(TREAD, 0.1)
            elif kind == 'riser':
                c = RISER if nz[y, x] < 0.6 else RISER_S
                bw = 9 + (k % 3) * 2
                if (x + k * 5) % bw == 0:
                    c = EDGE
            else:
                c = EDGE if nz[y, x] < 0.7 else dk(EDGE, 0.9)
            if far > 0:
                c = mix(c, HAZE, 0.18 * far)
            a[y, x, :3] = c
            a[y, x, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for i in range(70):                                            # 缺角 / 磨亮
        x = int(hrange(x0, PW, i, 61))
        y = int(hrange(STEP_TOP, PLAT, i, 62))
        if ROWS[y][0] == 'edge':
            px(d, x, y, RISER)
            px(d, x + 1, y, RISER)
        elif ROWS[y][0] == 'riser' and hash01(i, 63) < 0.5:
            px(d, x, y, dk(RISER, 0.86))
    # 两道平台的石板缝（近的那道缝往右下斜一点，透视）
    for xx in range(x0 + 6, PW, 22):
        for yy in range(LANDING[0] + 1, LANDING[1] + 1):
            px(d, xx + (yy - LANDING[0]) // 3, yy, mix(TREAD, EDGE, 0.4))
    for xx in range(x0 + 10, PW, 16):
        vl(d, xx, LANDING2[0] + 1, LANDING2[1], mix(TREAD, EDGE, 0.35))


def draw_platform(im):
    """石台（146–175）：大块石板（明暗 ±3 %、细缝很淡），后沿一道台阶脚的阴影，前沿 175 亮边 + 176 立面；
    码头那段（x 0–96）后沿是石头的边，后面就是水。"""
    d = ImageDraw.Draw(im)
    rect(d, 0, PLAT, PW - 1, LIP - 1, PLAT_C)
    mottle(im, (0, PLAT, PW - 1, LIP - 1), PLAT_C, PLAT_S, PLAT_HI, 88, cell=7, lo=0.22, hi=0.8)
    d = ImageDraw.Draw(im)
    bands = [(PLAT + 1, 155), (155, 164), (164, LIP)]
    for bi, (ya, yb) in enumerate(bands):
        if bi:
            for x in range(0, PW, 2):
                px(d, x, ya, mix(PLAT_C, PLAT_S, 0.8))
        step = 34 + bi * 6
        off = (bi * 19) % step
        for x in range(off, PW, step):
            vl(d, x, ya + 1, yb - 1, mix(PLAT_C, PLAT_S, 0.8))
    a = np.array(im).astype(np.float32)
    for bi, (ya, yb) in enumerate(bands):
        step = 34 + bi * 6
        off = (bi * 19) % step
        xs = [0] + list(range(off, PW, step)) + [PW]
        for xa, xb in zip(xs, xs[1:]):
            a[ya + 1:yb, xa + 1:xb, :3] *= hrange(0.975, 1.025, bi, xa, 89)
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))
    d = ImageDraw.Draw(im)
    for i in range(40):                                            # 细裂缝 / 水渍
        x, y = int(hrange(0, PW, i, 90)), int(hrange(PLAT + 2, LIP - 1, i, 91))
        for k in range(int(hrange(2, 6, i, 92))):
            px(d, x, y, mix(PLAT_C, PLAT_S, 0.95))
            x += 1
            y += (1 if hash01(i, k, 93) < 0.3 else (-1 if hash01(i, k, 93) > 0.8 else 0))
            y = max(PLAT + 1, min(LIP - 1, y))
    for i in range(30):                                            # 花瓣（淡；三个木桶站的地方不撒）
        x, y = int(hrange(150, PW, i, 94)), int(hrange(PLAT + 1, 160, i, 95))
        if all(abs(x - bx) > 12 for (bx, by) in BARRELS):
            px(d, x, y, mix(MARI, PLAT_C, 0.45))
    for x in range(0, PW):                                         # 前沿（靠水那几行）湿一点
        for y in range(LIP - 3, LIP):
            if hash01(x, y, 96) < 0.25 + 0.2 * (y - LIP + 3):
                px(d, x, y, dk(PLAT_C, 0.94))
    hl(d, 0, PW - 1, LIP, lt(PLAT_C, 0.25))
    hl(d, 0, PW - 1, FACE, (150, 128, 100))
    for x in range(0, PW, 26):
        px(d, x, FACE, (124, 104, 82))
    # 台阶脚 / 码头后沿
    hl(d, BASTION[1], PW - 1, PLAT, mix(PLAT_C, EDGE, 0.6))
    hl(d, 0, JETTY_X - 1, PLAT, lt(PLAT_C, 0.3))                   # 码头后沿：石头的亮边
    rect(d, 0, PLAT - 2, JETTY_X - 1, PLAT - 1, (150, 128, 100))   # 码头后沿往水里的立面（只露 2 行）
    hl(d, 0, JETTY_X - 1, PLAT - 2, (176, 154, 124))


def draw_bastion(im):
    """角楼（x 96–142）：八角形的砂岩墩子，左斜面亮、正面中、右斜面暗；三道线脚、一个大拱龛（里面暗、
    涂了朱红的小神像 + 花）、两个小窗洞、顶上一圈垛口 + 一座小亭子；墩脚靠着一支船桨。"""
    x0, x1 = BASTION
    top = 56
    d = ImageDraw.Draw(im)
    fa, fb = x0 + 7, x1 - 7
    rect(d, x0, top, fa - 1, PLAT - 1, SAND_HI)
    rect(d, fa, top, fb - 1, PLAT - 1, SAND)
    rect(d, fb, top, x1 - 1, PLAT - 1, SAND_S)
    for (a, b, c) in ((x0, fa - 1, SAND_HI), (fa, fb - 1, SAND), (fb, x1 - 1, SAND_S)):
        mottle(im, (a, top, b, PLAT - 1), c, dk(c, 0.93), lt(c, 0.08), 100 + a, cell=3, streaks=2)
    d = ImageDraw.Draw(im)
    for yy in range(top + 8, PLAT, 7):                             # 砌块缝
        hl(d, x0, x1 - 1, yy, dk(SAND, 0.88))
        off = 0 if (yy // 7) % 2 else 5
        for xx in range(x0 + off, x1, 10):
            vl(d, xx, yy + 1, min(PLAT - 1, yy + 6), dk(SAND, 0.9))
    for yy in (top + 4, 96, 124):                                  # 线脚
        hl(d, x0 - 1, x1, yy, SAND_HI)
        hl(d, x0 - 1, x1, yy + 1, SAND_D)
    vl(d, fa - 1, top, PLAT - 1, lt(SAND_HI, 0.3))
    vl(d, fb, top, PLAT - 1, SAND_D)
    # 大拱龛
    cx = (x0 + x1) // 2
    for yy in range(100, 123):
        u = (yy - 100)
        hw = 7 if u > 5 else int(round(7 * math.sqrt(max(0.0, 1 - ((5 - u) / 6.0) ** 2))))
        hl(d, cx - hw, cx + hw, yy, mix((60, 44, 40), (90, 66, 54), (yy - 100) / 22))
    for yy in range(100, 123):
        hw = 8 if yy - 100 > 5 else int(round(8 * math.sqrt(max(0.0, 1 - ((5 - (yy - 100)) / 6.0) ** 2))))
        px(d, cx - hw, yy, SAND_D)
        px(d, cx + hw, yy, SAND_HI)
    rect(d, cx - 2, 112, cx + 2, 121, VERMIL)
    d.ellipse((cx - 2, 108, cx + 2, 113), fill=C(VERMIL))
    px(d, cx - 1, 110, (250, 246, 236))
    px(d, cx + 1, 110, (250, 246, 236))
    V.draw_garland(d, cx - 6, 102, cx + 6, 102, 4)
    for xx in (cx - 5, cx + 4):
        px(d, xx, 121, (255, 220, 120))
    # 小窗洞
    for (wx, wy) in ((cx - 9, 68), (cx + 6, 68), (cx - 2, 80)):
        rect(d, wx, wy, wx + 3, wy + 6, (70, 54, 48))
        hl(d, wx, wx + 3, wy - 1, SAND_D)
        hl(d, wx - 1, wx + 4, wy + 7, SAND_HI)
    # 垛口 + 小亭子
    for xx in range(x0, x1, 5):
        rect(d, xx, top - 4, xx + 2, top - 1, SAND if xx < fb else SAND_S)
        px(d, xx, top - 4, SAND_HI)
    V.chhatri(im, cx, top - 2, 22, 13)
    d = ImageDraw.Draw(im)
    # 一棵从石缝里长出来的小菩提
    V._canopy(d, x0 + 4, top - 8, 7, 5, 911, pal=((44, 92, 48), (66, 128, 60), (100, 164, 74), (150, 200, 96)))
    vl(d, x0 + 5, top - 4, top + 2, (110, 90, 70))
    # 墩脚靠着的船桨
    d.line((x1 - 2, PLAT - 1, x1 + 4, 112), fill=C((150, 116, 76)))
    d.line((x1 - 1, PLAT - 1, x1 + 5, 112), fill=C((120, 90, 60)))
    rect(d, x1 + 3, 108, x1 + 6, 113, (170, 134, 90))
    cast_shadow(im, [(x1, top + 6), (x1 + 8, top + 14), (x1 + 8, PLAT - 1), (x1, PLAT - 1)])


# 码头后面拴着的船（k 1，strip 起伏）
MOOR = (14, 136)              # 船身左端、船舷 y
MOOR_L = 52
MOOR_BOX = (2, 122, 82, PLAT - 2)


def moored_frame(t):
    """拴在码头后沿的木船（只露出船舷以上：船身被码头挡住下半截）：船头往左上翘、一道蓝绿色船舷、船中间一个竹篷、
    两支桨搁在船舷上；8 帧里起伏 1 px。两根拴船桩、缆绳在近景里。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    dy = (0, 0, 1, 1, 1, 0, 0, 0)[f]
    x0, y0 = MOOR[0], MOOR[1] + dy
    for i in range(MOOR_L):
        u = i / (MOOR_L - 1)
        lift = int(round(6 * max(0.0, 1 - u * 5) ** 1.5 + 3 * max(0.0, (u - 0.85) / 0.15) ** 2))
        top = y0 - lift
        vl(d, x0 + i, top, PLAT - 3, (96, 70, 52))                # 船身（下半截藏在码头后沿后面）
        px(d, x0 + i, top, (150, 116, 84))
        px(d, x0 + i, top + 1, (60, 140, 150) if i % 9 else (220, 200, 90))     # 船舷彩带
        px(d, x0 + i, top + 2, (60, 140, 150))
        if top + 4 < PLAT - 2:
            px(d, x0 + i, top + 4, (78, 56, 42))
    for k in range(3):                                             # 船头 / 船尾拍起的小水纹（每帧挪一格）
        yy = 139 + k * 2
        for (bx, sgn) in ((x0 - 3, -1), (x0 + MOOR_L + 2, 1)):
            xs = bx + sgn * ((f + 2 * k) % 4)
            hl(d, min(xs, xs + 2 * sgn), max(xs, xs + 2 * sgn), yy, (214, 228, 224) if k else (236, 242, 236))
    # 竹篷
    cx = x0 + 24
    for xx in range(cx - 9, cx + 10):
        u = (xx - cx) / 9
        hgt = int(round(7 * math.sqrt(max(0.0, 1 - u * u))))
        for yy in range(y0 - hgt, y0):
            c = (206, 170, 110) if (xx + yy) % 3 else (176, 140, 88)
            if xx > cx + 4:
                c = dk(c, 0.85)
            px(d, xx, yy, c)
    hl(d, cx - 9, cx + 9, y0 - 1, (120, 92, 62))
    # 两支桨
    d.line((x0 + 6, y0 - 1, x0 + 40, y0 - 4), fill=C((176, 140, 92)))
    d.line((x0 + 10, y0, x0 + 46, y0 - 2), fill=C((150, 116, 76)))
    rect(d, x0 + 40, y0 - 6, x0 + 44, y0 - 4, (176, 140, 92))
    return im


def draw_mooring(im):
    """码头后沿两根拴船桩 + 缆绳（缆绳的另一头在船上，跟着船起伏差 1 px 不要紧，画在近景里）。"""
    d = ImageDraw.Draw(im)
    for (x, top) in ((10, 124), (76, 128)):
        rect(d, x, top, x + 2, PLAT - 1, (120, 92, 66))
        vl(d, x, top, PLAT - 1, (156, 124, 90))
        hl(d, x - 1, x + 3, top, (90, 70, 52))
        hl(d, x, x + 2, top + 5, (80, 60, 46))
    V.wire(d, 12, 128, 20, 134, 2, (176, 150, 100))
    V.wire(d, 76, 132, 62, 134, 2, (176, 150, 100))


# ---------------------------------------------------------------- 伞 / 木榻 / 平台上的东西
UMB_Y = 86                    # 伞顶 y（伞面 86–95，布穗到 98）
TAKHT_Y = 108                 # 木榻面


def draw_umbrella_static(im, ux, seed, R):
    """竹伞（chhatri）的伞杆 + 伞下的木榻（takht），榻上铜碗、几小碗点额粉（红 / 黄 / 白）、叠好的布、一个铜水壶。
    伞面在 strip 里画（布穗要飘）。伞的影子落在右下的平台上。"""
    d = ImageDraw.Draw(im)
    ty = TAKHT_Y
    tx0, tx1 = ux - R + 5, ux + R - 5
    cast_shadow(im, [(ux - R + 8, LANDING[0]), (ux + R + 4, LANDING[0]), (ux + R + 8, LANDING[1]),
                     (ux - R + 12, LANDING[1])], mul=SOFT_MUL)
    cast_shadow(im, [(tx0 + 3, LANDING[1] - 1), (tx1 + 2, LANDING[1] - 1), (tx1 + 5, LANDING[1] + 1),
                     (tx0 + 6, LANDING[1] + 1)], mul=SHADOW_MUL)
    d = ImageDraw.Draw(im)
    rect(d, tx0, ty, tx1, ty + 1, WOOD_HI)
    rect(d, tx0, ty + 2, tx1, ty + 3, WOOD)
    hl(d, tx0, tx1, ty + 4, WOOD_D)
    for lx in (tx0 + 1, tx1 - 2):
        rect(d, lx, ty + 5, lx + 1, LANDING[1] - 2, WOOD_D)
    rect(d, tx0 + 2, ty + 5, tx1 - 2, ty + 6, (70, 52, 40))         # 榻下的暗
    vl(d, ux, UMB_Y + 9, ty - 1, (200, 176, 116))                  # 伞杆（竹）
    vl(d, ux + 1, UMB_Y + 9, ty - 1, (154, 128, 80))
    for yy in range(UMB_Y + 12, ty, 4):
        px(d, ux, yy, (232, 210, 150))
    # 榻上的东西：叠好的布、点额粉的小铜碗、铜水壶、一本摊开的经书（白 + 红线）
    cl = V.CLOTH[(seed + 2) % len(V.CLOTH)]
    rect(d, tx0 + 2, ty - 2, tx0 + 8, ty - 1, cl)
    hl(d, tx0 + 2, tx0 + 8, ty - 2, lt(cl, 0.25))
    r = int(hash01(seed, 1) * 3)
    cols = ((214, 40, 50), (250, 200, 40), (246, 244, 236), (214, 40, 50), (250, 200, 40))[r:r + 3]
    for k, c in enumerate(cols):
        bx = ux + 3 + k * 3
        hl(d, bx, bx + 1, ty - 1, GOLD_D)
        px(d, bx, ty - 2, c)
        px(d, bx + 1, ty - 2, c)
    d.ellipse((tx1 - 4, ty - 4, tx1 - 1, ty - 1), fill=C(GOLD))
    px(d, tx1 - 3, ty - 3, GOLD_HI)
    if seed % 2 == 0:
        rect(d, ux - 5, ty - 1, ux - 2, ty - 1, (240, 236, 220))
        px(d, ux - 4, ty - 1, (200, 60, 50))


def umbrella_canopy(d, ux, seed, R, f):
    """伞面：扁的圆锥（略微从下往上看），草黄色、放射状的伞骨（左亮右暗），伞底一道暗边、
    伞边一圈彩色布穗（f 帧飘）。"""
    top = UMB_Y
    rim = top + 8
    for xx in range(ux - R, ux + R + 1):
        u = (xx - ux) / R
        yt = top + int(round(abs(u) ** 1.25 * (rim - top)))
        for yy in range(yt, rim + 1):
            c = (228, 198, 130)
            if u < -0.35:
                c = (242, 218, 152)
            elif u > 0.4:
                c = (198, 166, 104)
            if (xx - ux) % 4 == 0 and yy > yt:                      # 伞骨
                c = dk(c, 0.8)
            px(d, xx, yy, c)
        px(d, xx, yt, (250, 232, 176) if u < 0.3 else (214, 184, 120))
    hl(d, ux - R, ux + R, rim + 1, (130, 100, 60))                  # 伞底（暗）
    hl(d, ux - R + 2, ux + R - 2, rim + 2, (98, 76, 48))
    px(d, ux, top - 1, (150, 120, 70))
    px(d, ux, top - 2, (120, 96, 60))
    px(d, ux, top - 3, GOLD)
    col = ((200, 50, 50), (240, 150, 40), (60, 120, 180), (150, 60, 140), (60, 140, 90))[seed % 5]
    for k, xx in enumerate(range(ux - R, ux + R + 1, 2)):          # 布穗
        ph = math.tau * f / N_ANIM + k * 0.7 + seed
        L = 2 + (1 if math.sin(ph) > 0.2 else 0)
        dx = 1 if math.sin(ph + 0.6) > 0.5 else 0
        for r in range(L):
            px(d, xx + (dx if r == L - 1 else 0), rim + 2 + r, col if r < L - 1 else dk(col, 0.78))


UMB_BOXES = [('umbrellas_%d' % i, (ux - R - 2, UMB_Y - 4, ux + R + 3, UMB_Y + 14))
             for i, (ux, sd, R) in enumerate(UMBRELLAS)]


def umbrellas_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    for (ux, sd, R) in UMBRELLAS:
        umbrella_canopy(d, ux, sd, R, f)
    return im


PODIUM = (384, 426)           # 中间平台往前伸出来的一块石台（伞 2 站在上面）：顶面 = LANDING，正面 118–129


def draw_podium(im):
    a, b = PODIUM
    d = ImageDraw.Draw(im)
    for y in range(LANDING[0], LANDING[1] + 1):
        hl(d, a, b, y, TREAD if y > LANDING[0] else lt(TREAD, 0.15))
    for y in range(LANDING[1] + 1, 130):
        hl(d, a, b, y, RISER)
    mottle(im, (a, LANDING[1] + 1, b, 129), RISER, RISER_S, lt(RISER, 0.08), 61, cell=3)
    d = ImageDraw.Draw(im)
    for y in (121, 125):
        hl(d, a, b, y, RISER_S)
    for y in range(LANDING[1] + 1, 130):
        off = 0 if ((y - 118) // 4) % 2 else 6
        for x in range(a + off, b, 12):
            px(d, x, y, EDGE)
    hl(d, a, b, LANDING[1] + 1, lt(RISER, 0.25))
    hl(d, a, b, 129, EDGE)
    hl(d, a - 1, b + 1, LANDING[0], lt(TREAD, 0.25))
    vl(d, a, LANDING[0], 129, lt(RISER, 0.2))
    cast_shadow(im, [(b + 1, LANDING[1] + 1), (b + 7, LANDING[1] + 4), (b + 7, 131), (b + 1, 131)])
    cast_shadow(im, [(a + 2, 130), (b + 1, 130), (b + 6, 133), (a + 6, 133)], mul=SOFT_MUL)


PAVILIONS = (156, 238, 356, 454, 562, 632)    # 第二道平台上的一排小亭子（里面一座小林伽）


def draw_pavilions(im):
    for i, x in enumerate(PAVILIONS):
        w = 12 if i % 2 else 14
        tip = V.chhatri(im, x, LANDING2[1], w, 9)
        d = ImageDraw.Draw(im)
        px(d, x, LANDING2[1] - 2, (50, 46, 50))                      # 小林伽
        px(d, x, LANDING2[1] - 3, (50, 46, 50))
        px(d, x - 1, LANDING2[1] - 1, MARI)
        px(d, x + 1, LANDING2[1] - 1, MARI)
        cast_shadow(im, [(x + w // 2 + 1, LANDING2[1] - 9), (x + w // 2 + 4, LANDING2[1] - 6),
                         (x + w // 2 + 4, LANDING2[1] + 1), (x + w // 2 + 1, LANDING2[1] + 1)], mul=SOFT_MUL)
        _ = tip


# ---------------------------------------------------------------- 神龛 / 油灯 / 纱丽 / 鸽子 / 零碎
LAMPS = [(237 + k * 4, PLAT - 1) for k in range(6)]         # 神龛右边石台后沿的一排小油灯（灯碗 y）
LAMP_BOX = (234, PLAT - 6, 262, PLAT)


def draw_shrine(im):
    """小神龛：白灰的方身子 + 小尖顶（红白条）+ 藏红小旗，龛里黑色林伽（三道白灰纹 + 一点朱红）+ 一圈花环，
    龛前两盘万寿菊；右边一排小油灯（灯碗在这里，火苗在 strip）。"""
    a, b = SHRINE
    d = ImageDraw.Draw(im)
    cast_shadow(im, [(b + 1, 122), (b + 7, 128), (b + 9, PLAT + 3), (b + 1, PLAT + 3)], mul=SOFT_MUL)
    cast_shadow(im, [(a + 2, PLAT), (b + 1, PLAT), (b + 6, PLAT + 4), (a + 6, PLAT + 4)], mul=SOFT_MUL)
    d = ImageDraw.Draw(im)
    body = 122
    white, white_s = (240, 234, 222), (210, 202, 190)
    rect(d, a, body, b, PLAT - 1, white)
    rect(d, b - 4, body, b, PLAT - 1, white_s)
    vl(d, a, body, PLAT - 1, (252, 250, 244))
    hl(d, a - 1, b + 1, body, (252, 250, 244))
    hl(d, a - 1, b + 1, body + 1, VERMIL)
    hl(d, a - 1, b + 1, PLAT - 2, VERMIL)
    hl(d, a - 1, b + 1, PLAT - 1, (170, 60, 44))
    for yy in range(108, body):                                    # 小尖顶（红白横条）
        u = (yy - 108) / (body - 108)
        hw = int(round(2 + u * ((b - a) / 2 - 1)))
        cx = (a + b) // 2
        c = (236, 228, 214) if ((yy - 108) // 2) % 2 else (210, 80, 58)
        hl(d, cx - hw, cx + hw, yy, c)
        px(d, cx + hw, yy, dk(c, 0.8))
    cx = (a + b) // 2
    vl(d, cx, 98, 107, (110, 90, 70))                               # 小旗
    for i in range(1, 7):
        vl(d, cx + i, 99 + i // 3, 102 - i // 3, V.SAFFRON)
    px(d, cx, 107, GOLD)
    # 龛
    rect(d, a + 4, 128, b - 5, PLAT - 4, (52, 40, 40))
    hl(d, a + 5, b - 6, 127, (52, 40, 40))
    lx = (a + b) // 2 - 1                                           # 林伽
    d.ellipse((lx - 2, 133, lx + 2, 139), fill=C((40, 40, 46)))
    rect(d, lx - 4, 139, lx + 4, 141, (60, 60, 66))
    for yy in (134, 135, 136):
        hl(d, lx - 1, lx + 1, yy, (226, 226, 226) if yy != 135 else (40, 40, 46))
    px(d, lx, 135, VERMIL)
    V.draw_garland(d, a + 4, 129, b - 5, 129, 5, thick=False)
    for (fx, fy) in ((a - 4, PLAT - 2), (b + 1, PLAT - 3)):         # 两盘万寿菊（一盘放在台阶脚）
        d.ellipse((fx - 2, fy - 1, fx + 3, fy + 1), fill=C(MARI))
        px(d, fx, fy - 1, MARI_HI)
        px(d, fx + 2, fy, MARI_D)
    for (x, y) in LAMPS:                                             # 灯碗（陶）
        hl(d, x - 1, x + 1, y, (176, 100, 62))
        px(d, x, y - 1, (150, 84, 54))


def lamps_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_LAMP + 1e-6)) % N_LAMP
    for i, (x, y) in enumerate(LAMPS):
        ph = (f + i * 3) % N_LAMP
        hgt = (2, 3, 3, 2, 3, 4, 3, 2)[ph]
        lean = (0, 0, 1, 0, -1, 0, 0, 1)[ph]
        for r in range(hgt):
            c = (255, 250, 210) if r == 0 else ((255, 200, 80) if r < hgt - 1 else (240, 130, 40))
            px(d, x + (lean if r == hgt - 1 else 0), y - 2 - r, c)
    return im


SARIS = [  # (x0, 长, 第几级（下半段 0–3）, 底色, 边色)：顺着踏面平铺、一头搭在下面那级的立面上
    (176, 30, 3, (246, 244, 236), (200, 40, 40)),
    (262, 40, 1, (200, 30, 50), GOLD),
    (294, 32, 3, (244, 204, 70), (60, 140, 90)),
    (478, 40, 1, (80, 160, 110), (220, 70, 120)),
    (586, 36, 0, (236, 120, 170), (60, 90, 170)),
    (518, 28, 3, (70, 110, 190), (240, 200, 70)),
]


def draw_saris(im):
    """晒在台阶上的纱丽：一条长布平铺在一级的踏面上（2 行，亮），前沿垂下来搭在下面那级立面的上半截（2 行，暗），
    两头和下沿一道边色、中间几处褶子；布的影子落在立面上。"""
    d = ImageDraw.Draw(im)
    for i, (x0, L, k, col, bc) in enumerate(SARIS):
        ty = PLAT - 6 - 6 * k                                      # 这一级踏面的上一行（140 − 6k）
        x1 = x0 + L - 1
        hl(d, x0, x1, ty, lt(col, 0.12))
        hl(d, x0, x1, ty + 1, col)
        for r, c in ((2, dk(col, 0.82)), (3, dk(col, 0.72))):      # 垂下来的那截（在立面上）
            a = x0 + (1 if r == 3 else 0)
            b = x1 - (2 if r == 3 else 0)
            hl(d, a, b, ty + r, c)
        hl(d, x0 + 1, x1 - 2, ty + 4, dk(bc, 0.8))                 # 下沿的边
        for xx in (x0, x1):
            vl(d, xx, ty, ty + 3, bc)
        for xx in range(x0 + 5, x1 - 3, 9):                        # 褶子
            px(d, xx, ty + 2, dk(col, 0.62))
            px(d, xx + 1, ty + 3, dk(col, 0.6))
        mul_box(im, (x0 + 2, ty + 5, x1, ty + 5), SHADOW_MUL)
        d = ImageDraw.Draw(im)


PIGEON_SPOTS = [(438, 135), (445, 135), (452, 129), (459, 135), (467, 141), (444, 141), (472, 129)]
PIGEON_BOX = (434, 122, 480, 144)


def pigeon(d, x, y, pose, col=(124, 128, 142)):
    """一只鸽子（侧面朝左，5×4）：pose 0 = 站着、1 = 低头啄、2 = 抬头。"""
    hd = (100, 104, 118)
    rect(d, x, y - 2, x + 3, y, col)
    px(d, x + 4, y - 1, dk(col, 0.8))                               # 尾
    hl(d, x + 1, x + 2, y - 1, lt(col, 0.2))                        # 翅膀亮
    px(d, x + 2, y - 2, (150, 110, 160))                            # 颈上的紫绿光
    if pose == 1:
        px(d, x - 1, y, hd)
        px(d, x - 2, y + 1 if False else y, (220, 140, 120))
    elif pose == 2:
        px(d, x, y - 4, hd)
        px(d, x, y - 3, hd)
        px(d, x - 1, y - 4, (220, 140, 120))
    else:
        px(d, x, y - 3, hd)
        px(d, x - 1, y - 3, (220, 140, 120))
    px(d, x + 1, y + 1, (200, 100, 90))                             # 脚


def pigeons_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    for i, (x, y) in enumerate(PIGEON_SPOTS):
        seq = (0, 1, 1, 0, 2, 0, 1, 0)
        pose = seq[(f + i * 3) % N_ANIM]
        hop = 1 if (i == 3 and f in (4, 5)) else 0
        pigeon(d, x - hop, y, pose, col=((124, 128, 142), (150, 152, 162), (110, 112, 126))[i % 3])
    return im


def draw_bits(im):
    """台阶上的零碎：几处万寿菊花堆和散的花瓣、铜水壶、卷起来的草席、一根插着小旗的竹竿（祭司的地盘）、
    两个装花的竹篮。"""
    d = ImageDraw.Draw(im)
    for (x, y) in ((168, 108), (360, 108), (456, 134), (566, 108)):  # 花堆（在踏面上）
        d.ellipse((x - 3, y - 2, x + 3, y + 1), fill=C(MARI))
        px(d, x - 1, y - 2, MARI_HI)
        px(d, x + 2, y, MARI_D)
    for i in range(120):                                            # 散花瓣（只落在踏面上）
        x = int(hrange(BASTION[1] + 2, PW, i, 71))
        y = int(hrange(STEP_TOP + 2, PLAT - 1, i, 72))
        if is_tread(y) and hash01(i, 73) < 0.6:
            px(d, x, y, (MARI, MARI_D, (236, 80, 90), MARI_HI)[i % 4])
    for (x, y) in ((262, 140), (444, 108), (618, 140)):            # 铜水壶（lota）
        d.ellipse((x - 2, y - 3, x + 2, y + 1), fill=C(GOLD))
        px(d, x - 1, y - 2, GOLD_HI)
        hl(d, x - 1, x + 1, y - 4, GOLD_D)
    for (x, y, L) in ((534, 134, 12), (150, 140, 10)):              # 卷起来的草席
        rect(d, x, y - 3, x + L, y, (214, 186, 120))
        hl(d, x, x + L, y - 3, (236, 212, 150))
        hl(d, x, x + L, y, (170, 140, 86))
        vl(d, x + L, y - 3, y, (186, 156, 96))
        px(d, x + L, y - 2, (150, 120, 70))
    for (x, top) in ((338, 64), (628, 70)):                         # 插着小旗的竹竿
        vl(d, x, top, LANDING[0], (200, 176, 116))
        vl(d, x + 1, top, LANDING[0], (150, 124, 78))
        for i in range(1, 6):
            vl(d, x + 1 + i, top + 1 + i // 3, top + 4 - i // 3, (230, 60, 50) if x < 400 else V.SAFFRON)
    for (x, y) in ((250, 108), (470, 108)):                         # 装花的竹篮
        rect(d, x - 4, y - 3, x + 4, y, (170, 130, 76))
        for xx in range(x - 4, x + 5, 2):
            px(d, xx, y - 2, (140, 104, 60))
        hl(d, x - 3, x + 3, y - 4, MARI)
        px(d, x - 1, y - 5, MARI_HI)
        px(d, x + 2, y - 5, (236, 80, 90))


# ============================================================ 组装
@lru_cache(maxsize=1)
def near_img():
    im = A._new(PW, H)
    draw_platform(im)
    draw_steps(im)
    draw_bastion(im)
    draw_mooring(im)
    draw_saris(im)
    draw_podium(im)
    draw_pavilions(im)
    for (ux, sd, R) in UMBRELLAS:
        draw_umbrella_static(im, ux, sd, R)
    draw_shrine(im)
    draw_bits(im)
    im = A._grade(im, sat=0.98, val=1.0)
    return opaque(im)


@lru_cache(maxsize=1)
def river_img():
    """石台前沿下面那条河（3 行）：底色三行渐暗 + 一道道短的亮纹（96 循环，往右流）。"""
    im = A._new(RIVER_P, H - WATER)
    d = ImageDraw.Draw(im)
    for r in range(H - WATER):
        hl(d, 0, RIVER_P - 1, r, WATER_C[min(r, 2)])
    for i in range(14):
        x = int(hrange(0, RIVER_P, i, 501))
        r = int(hrange(0, H - WATER, i, 502))
        L = int(hrange(2, 6, i, 503))
        for k in range(L):
            px(d, (x + k) % RIVER_P, r, (196, 214, 206) if k < L - 1 else (156, 182, 176))
    px(d, 10, 0, (236, 240, 230))
    px(d, 54, 1, (236, 240, 230))
    return im


STRIPS_NEAR = [('boat', MOOR_BOX, N_ANIM, FPS_ANIM, moored_frame)] + \
              [(n, b, N_ANIM, FPS_ANIM, umbrellas_frame) for (n, b) in UMB_BOXES] + \
              [('lamps', LAMP_BOX, N_LAMP, FPS_LAMP, lamps_frame),
               ('pigeons', PIGEON_BOX, N_ANIM, FPS_ANIM, pigeons_frame)]
STRIPS_FAR = [('glint', GLINT_BOX, N_ANIM, FPS_ANIM, glint_frame, FAR_K)]
STRIPS_PAL = [('pflag', PFLAG_BOX, N_ANIM, FPS_ANIM, pflag_frame, PAL_K),
              ('doves', DOVE_BOX, N_ANIM, FPS_ANIM, doves_frame, PAL_K)]


@lru_cache(maxsize=1)
def build():
    pal, flag = palace_parts()
    return dict(sky=sky_img(), clouds=clouds_img(), far=far_img(), palace=pal, near=near_img(), river=river_img(),
                flag=flag)


def compose(camX, t=0.5):
    """直接拼一帧（不经导出），自检 / 预览用。"""
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    o = int(math.floor(camX * CLOUD_K + t * CLOUD_VX)) % 640
    cl = V._tile(R['clouds'], 1280)
    paste(out, cl.crop((o, 0, o + W, cl.height)), 0, 0)
    ox = math.floor(camX * FAR_K)
    out.alpha_composite(R['far'].crop((ox, 0, ox + W, H)))
    for (name, box, n, fps, fn, k) in STRIPS_FAR:
        paste(out, fn(t).crop(box), box[0] - math.floor(camX * k), box[1])
    for (L, col, cn, y, vx, x0) in BOATS:
        x = (x0 + t * vx - camX * FAR_K) % BOAT_SPAN - 100
        paste(out, boat_img(L, col, cn), math.floor(x), y)
    bird = V.kite_bird_img()
    for (y, vx, k, x0) in V.KITES:
        x = (x0 + t * vx - camX * k) % 460 - 100
        paste(out, bird, math.floor(x), y)
    ox = math.floor(camX * PAL_K)
    paste(out, R['palace'], -ox, 0)
    for (name, box, n, fps, fn, k) in STRIPS_PAL:
        paste(out, fn(t).crop(box), box[0] - math.floor(camX * k), box[1])
    out.alpha_composite(R['near'].crop((camX, 0, camX + W, H)))
    for (name, box, n, fps, fn) in STRIPS_NEAR:
        paste(out, fn(t).crop(box), box[0] - camX, box[1])
    o = int(math.floor(camX * 1.0 + t * RIVER_VX)) % RIVER_P
    rv = V._tile(R['river'], RIVER_P * 5)
    paste(out, rv.crop((o, 0, o + W, rv.height)), 0, WATER)
    return out


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0)]
    cim, cy = BJ.crop_rows(R['clouds'])
    layers.append(dict(type='wrap', image=ex.img('clouds', BJ.tile_to(cim, 640, 640 + W)), period=640, k=CLOUD_K, y=cy,
                       vx=CLOUD_VX))
    fim, fy = BJ.crop_rows(R['far'])
    layers.append(dict(type='pano', image=ex.img('far', fim), k=FAR_K, x=0, y=fy))
    for (name, box, n, fps, fn, k) in STRIPS_FAR:
        layers.append(ex.bake(name, box, n, fps, fn, screen=False, k=k))
    bl = []
    for i, (L, col, cn, y, vx, x0) in enumerate(BOATS):
        bl.append(dict(image=ex.img('boat%d' % i, boat_img(L, col, cn)), x0=float(x0), y=y, vx=vx, k=FAR_K))
    layers.append(dict(type='clouds', span=BOAT_SPAN, clouds=bl))
    bk = ex.img('kite_bird', V.kite_bird_img())
    layers.append(dict(type='clouds', span=460, clouds=[dict(image=bk, x0=float(x0), y=y, vx=vx, k=k)
                                                       for (y, vx, k, x0) in V.KITES]))
    pim, py = BJ.crop_rows(R['palace'])
    layers.append(dict(type='pano', image=ex.img('palace', pim), k=PAL_K, x=0, y=py))
    for (name, box, n, fps, fn, k) in STRIPS_PAL:
        layers.append(ex.bake(name, box, n, fps, fn, screen=False, k=k))
    nim, ny = BJ.crop_rows(R['near'])
    layers.append(dict(type='pano', image=ex.img('near', nim), k=1.0, x=0, y=ny))
    for (name, box, n, fps, fn) in STRIPS_NEAR:
        layers.append(ex.bake(name, box, n, fps, fn, screen=False, k=1.0))
    layers.append(dict(type='wrap', image=ex.img('river', BJ.tile_to(R['river'], RIVER_P, RIVER_P + W)),
                       period=RIVER_P, k=1.0, y=WATER, vx=RIVER_VX))
    anchors = dict(ANCHORS)
    anchors.update(shrine_box=[SHRINE[0], 98, SHRINE[1] + 1, PLAT],
                   umbrellas=[[ux, LANDING[0]] for (ux, sd, R) in UMBRELLAS],
                   bastion=[BASTION[0], 34, BASTION[1], PLAT],
                   moored_boat=[MOOR[0] + MOOR_L // 2, MOOR[1]],
                   steps=dict(top=STEP_TOP, landing=list(LANDING), foot=PLAT),
                   front_edge=FACE, water_y=WATER, horizon=HZ)
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def _checks(ex, BJ, st, R):
    imgs = ex.images
    bad = 0
    for camX in range(0, PW - W + 1, 40):
        for t in (0.0, 0.75, 1.5, 7.0):
            im = np.array(BJ.ref_render(st, imgs, camX, t, {}).convert('RGB'))
            bad += int((im.sum(-1) == 0).sum())
    ex.checked('河坛 镜头 0–320（每 40）× 4 个时刻 整屏都有画（没有露黑）', bad)
    ex.checked('天空底图整张不透明', int((np.array(R['sky'])[..., 3] != 255).sum()))
    a = np.array(R['near'])
    ex.checked('近景 石台 + 前沿（y 146–176）整条不透明', int((a[PLAT:WATER, :, 3] != 255).sum()))
    ex.checked('近景 台阶（x 142–640，y 84–146）整片不透明', int((a[STEP_TOP:PLAT, BASTION[1]:, 3] != 255).sum()))
    ex.checked('近景只有 0 / 255 两种透明度', int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum()))
    fa = np.array(R['far'])
    ex.checked('远景 左边河面（x 0–100，y 104–146）不透明', int((fa[HZ:PLAT, :100, 3] != 255).sum()))
    pa = np.array(R['palace'])
    ex.checked('宫殿层 y 84–92（接台阶顶的那几行）在 x 100–512 整条不透明', int((pa[STEP_TOP:93, 100:, 3] != 255).sum()))
    ex.checked('宫殿层从 x 100 起（镜头 0 时藏在角楼后面，往右走只会更往右，不会盖到左边的河）',
               int((pa[:, :100, 3] > 0).sum()))
    ra = np.array(R['river'])
    ex.checked('河（前沿下面 3 行）整条不透明', int((ra[..., 3] != 255).sum()))
    # strip 闭合 / 帧条宽 / 每帧在动 / 画的东西都在框里（同一个帧函数合起来算）
    allst = [(n, b, nn, fps, fn) for (n, b, nn, fps, fn) in STRIPS_NEAR] + \
            [(n, b, nn, fps, fn) for (n, b, nn, fps, fn, k) in STRIPS_FAR + STRIPS_PAL]
    for (name, box, n, fps, fn) in allst:
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
    fns = {}
    for (name, box, n, fps, fn) in allst:
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
    # wrap（河 / 云）闭合：t = period/|vx| 时和 t = 0 一样
    for L in [L for L in st['layers'] if L['type'] == 'wrap']:
        T = L['period'] / abs(L['vx'])
        one = dict(st, layers=[L], fg=[])
        g0 = BJ.ref_render(one, imgs, 0, 0.1, {})
        g1 = BJ.ref_render(one, imgs, 0, 0.1 + T, {})
        ex.checked('wrap %s 一圈 %.1f s 闭合' % (L['image'].split('/')[-1], T), BJ.ndiff(g0, g1))
    # 锚点
    out = 0
    wx = ANCHORS['walk_x']
    out += not (0 <= wx[0] < wx[1] <= PW)
    for k in ('arrive', 'shrine'):
        v = ANCHORS[k]
        out += not (WALK[0] <= v[1] <= WALK[1] and wx[0] <= v[0] <= wx[1])
    for v in BARRELS:
        out += not (WALK[0] <= v[1] <= WALK[1] and wx[0] <= v[0] <= wx[1])
    rv = ANCHORS['river']
    out += not (0 <= rv[0] < PW and WATER <= rv[1] < H)
    out += not (0 <= ANCHORS['river_vista'][0] < JETTY_X and HZ < ANCHORS['river_vista'][1] < PLAT)
    ex.checked('锚点都在地图里、站人的锚点 / 木桶在可走带里、river 在水上（不满足的条数）', out)
    # 木桶站的地方（x ±10，y 140–170）近景里没有大物件：只有石台的颜色（和台面均值差 < 26）
    base = np.array(PLAT_C, np.float32)
    busy = 0
    for (bx, by) in BARRELS:
        sub = a[by - 20:by + 4, bx - 10:bx + 11, :3].astype(np.float32)
        sub = sub[(np.arange(by - 20, by + 4) > PLAT)]                # 146 那一行是台阶脚的暗线，不算
        busy += int((np.abs(sub - base).max(-1) > 26).sum())
    ex.checked('三个木桶站的地方（x ±10，y 147–170）只有平整的石板（离台面色太远的像素）', busy)
    # 导出 vs 直接拼
    for camX in (0, 80, 200, 320):
        for t in (0.0, 1.25, 9.0):
            got = BJ.ref_render(st, imgs, camX, t, {})
            ex.checked('河坛 camX=%d t=%.2f 导出 vs 直接拼' % (camX, t), BJ.ndiff(got, compose(camX, t)))
    nm = _lum(a[..., :3].astype(np.float32))
    ex.note('可走带后面的亮度：石台 y148–175 均值 %.0f 标准差 %.1f；下半段台阶 y110–145 均值 %.0f 标准差 %.1f' %
            (nm[148:176].mean(), nm[148:176].std(), nm[110:146, 142:].mean(), nm[110:146, 142:].std()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch4', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        compose(camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'ganges_ghat_solo_%d.png' % camX))
    world = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    world.alpha_composite(build()['near'])
    world.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'ganges_ghat_near.png'))
    pal = Image.new('RGBA', (PALW, H), (90, 140, 200, 255))
    pal.alpha_composite(build()['palace'])
    pal.convert('RGB').resize((PALW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'ganges_ghat_palace.png'))
    print('ok')
