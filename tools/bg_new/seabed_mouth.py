# -*- coding: utf-8 -*-
r"""seabed_mouth —— 第7章「红海」：海底巨嘴（地图 seabed_ch7），第 15 战段 2「女教皇·巨嘴」的场地。
2026-10-19 第三轮背景重画（sea 组）新画（改前是 later_stages 的占位）。共用零件在 sea_parts.py。

地图 320 宽（单屏，镜头不动）、ground 160、可走带 y 150–174（stages_ch06_09.js 的登记值；游玩脚本表里写的 145–176
是上颚咬下来的伤害框——舌面从 y 147 一直铺到画面底，两种都盖得住）。侧视平视：人被吞进女教皇变出来的海底巨嘴里，
看的是嘴的内侧：上面是上颚，下面是下牙床 + 舌头，左边是喉咙，右边是闭着的嘴唇（唇缝外面是海）。
光：从右边唇缝透进来的海里的蓝光——亮面朝右、喉咙那头最暗（全图一致）。

从上到下：
  y 0–44      上颚的硬腭：一道道横的腭褶，越往上越暗（对白框盖着这一段，只当气氛）
  y 40–68     上牙床：一条横着的肉棱，下沿是牙龈线（牙位微微往上拱、牙缝处牙龈乳头往下垂）；
              每个牙位（anchors.upper，x 60…260）一个往下开口的牙槽凹坑——剧情的 6 颗上牙插在这里，背景不画牙；
              牙龈线比牙根尖（锚点 y + 1）低 2 px 左右，牙看上去插在牙龈里
  y 64–140    嘴的内壁（颊黏膜）：竖的软褶、湿亮的高光、几根血管、一道淡淡的咬合线；越往喉咙越暗
  y 136–150   下牙床：同上，牙槽往上开口（anchors.lower）；上沿比锚点 y 高 10 px，下牙的根穿过牙床
  y 147–180   舌头：粉红的软地面 = 可走带（舌乳头的小点压得很淡），前沿往下卷
从左到右：
  x 0–50      喉咙：黑洞洞的咽喉（几圈软骨环往里收）、前后两道腭弓（前面那道朝光的一侧亮）、悬雍垂（strip 轻轻晃）；
              舌根往下卷进喉咙：x < 34 的地面一路暗下去（= 剧情“被卷进喉咙”的范围，throat.x + 10）
  x 50–262    牙床 + 内壁 + 舌面（战斗区）；x 120、240 两处牙龈乳头挂着口水（strip）
  x 262–320   嘴角：上下唇在 x 290 合拢，往右张开一道楔形的唇缝，缝里是海底（蓝光、斜的光柱、远处的沙底、礁石、海草、
              小鱼影）；唇外沿粘着几颗藤壶（这张嘴是女教皇用海底的岩石变的）；唇缝透进来的光（焦散）、冒进来的气泡（strip）
剧情摆的东西（背景不画）：12 颗牙（prop.upper_tooth / lower_tooth）、众人的潜水头盔。

图层（从后往前）：
  wall       static            内壁 + 喉咙 + 两道腭弓 + 唇缝外的海（整张不透明）
  lower      static            下牙床 + 下唇（只有 0 / 255）
  jaw        pick  key bite    上颚（硬腭 + 上牙床 + 上唇）：bite = 1 那张整体往下移 12 px，顶上补 12 行硬腭（两张同尺寸）
  uvula      strip             悬雍垂左右晃（8 帧 @4 fps）
  spit_open  static key spit   嘴张开：唇缝变成一个大口子（嘴角移到 x 232），外面的海亮得发白
  tongue     static            舌头（可走带；只有 0 / 255）
  flow       strip             往喉咙吸的水流：几道流线上的虚线往喉咙走、空中的碎屑越靠近越快、舌面上一道道往左拖的水纹
  rays       strip             唇缝透进来的光在内壁 / 舌尖上晃：网状的焦散亮纹，越靠唇缝越亮
  drool0/1   strip             两处牙龈乳头上的口水：挂着 → 拉长 → 断 → 落到下牙床溅开（同一组帧、两个框）
  bubbles    strip             唇缝冒进来的气泡往上浮、在上唇底下破掉；下牙床那边偶尔冒一串
  bite_dim   static key bite   咬下来时的暗角（四角 + 压下来的上牙床下面一道阴影；分档 + Bayer，像素风）
  spit_glow  static key spit   张嘴时照进来的大片亮光（从口子往左一圈圈淡下去的光晕）
  spit_tint  tint   key spit   整屏提亮一点
锚点（素材总表的定稿值）：throat [24,152]、upper [[60,64],[100,62],[140,60],[180,60],[220,62],[260,64]]（上排牙根中心）、
  lower [[60,148],[100,150],[140,150],[180,150],[220,150],[260,148]]（下排）、arrive [250,162]；
  额外：walk_x [8,312]、uvula（悬雍垂尖）、lips（唇缝中心）、throat_box（喉咙洞的框）。
key：bite（上颚压下来：pick 下移 12 px + 暗角）、spit（嘴张开吐人：右边亮光）。
单独运行：python -B tools\bg_new\seabed_mouth.py → tools\bg_new\_preview\ch7\after\seabed_mouth_solo*.png
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
from scipy import ndimage  # noqa: E402

from engine.core import gradient, hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _parts():
    key = 'bg_new_sea_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'sea_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
C = P.C
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
N_ANIM, FPS_ANIM = P.N_ANIM, P.FPS_ANIM
fno = P.frame_no

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 320
GROUND = 160
WALK = (150, 174)
BITE_DY = 12                  # key bite：上颚整体往下移的距离（素材总表定稿）
EXT = BITE_DY                 # 上颚画布往上多画 12 行硬腭：下移以后顶上不露底
JAW_H = 116                   # 上颚 pick 图的高度：嘴角最低 y 100，下移后 112，留几行余量
UPPER = [[60, 64], [100, 62], [140, 60], [180, 60], [220, 62], [260, 64]]
LOWER = [[60, 148], [100, 150], [140, 150], [180, 150], [220, 150], [260, 148]]
TEETH_X = [p[0] for p in UPPER]
PAPILLAE = [80, 120, 160, 200, 240]          # 牙缝（牙龈乳头）
CORNER = (290, 100)           # 嘴角：上下唇在这里合拢，往右张开一道楔形的唇缝
LIPS_R = (79.0, 123.0)        # 唇缝在画面右沿（x 320）的上沿 / 下沿
TH_C = (12.0, 122.0)          # 喉咙洞（椭圆）的中心
TH_R = (36.0, 64.0)
UV_X, UV_LEN = 20, 22         # 悬雍垂：x、长度
DROOL_X = (120, 240)          # 口水挂在这两处牙龈乳头上（都在牙缝里，不挡剧情的牙）
SPIT_C = (232, 104)           # key spit：嘴张开以后的嘴角

ANCHORS = dict(
    throat=[24, 152],          # 喉咙口（剧情：被卷到 throat.x + 10 以内就“被卷进喉咙”）
    upper=UPPER,               # 上排牙根中心（剧情的 prop.upper_tooth 从这里往下挂 27 px）
    lower=LOWER,               # 下排牙根中心（prop.lower_tooth 立在 max(152, y + 4)）
    arrive=[250, 162],
    walk_x=[8, 312],           # 同战斗 arena [8, 312]
)

# ============================================================ 调色（避开纯黑：自检用 RGB 全 0 判断露黑）
INK = (40, 8, 20)
GUM = [(44, 10, 24), (62, 15, 32), (84, 22, 42), (110, 32, 52), (138, 46, 64), (168, 64, 80), (198, 92, 104),
       (226, 130, 136)]                                                       # 牙床 / 嘴唇：暗 → 亮
CHEEK = [(28, 7, 17), (38, 10, 22), (50, 13, 28), (64, 18, 34), (80, 24, 42), (98, 32, 50), (120, 44, 60),
         (146, 60, 74)]                                                       # 内壁（比牙床暗一截，人站在前面看得清）
THROAT = [(16, 5, 11), (22, 6, 14), (30, 8, 18), (40, 11, 23), (52, 14, 29)]
TONGUE = [(112, 42, 62), (134, 56, 76), (156, 72, 90), (176, 88, 104), (194, 104, 118), (210, 122, 132),
          (228, 146, 152)]
SOCK = [(22, 5, 13), (34, 8, 19), (52, 13, 27), (86, 26, 44)]                 # 牙槽：最深 → 朝光的内壁
SPEC = (244, 182, 190)        # 湿亮的高光（带粉：不能白到像牙——背景不画牙，自检按“牙白”查）
SALIVA = (232, 208, 218)
VEIN = (72, 18, 44)
BARN = [(214, 214, 200), (150, 150, 140), (60, 56, 60)]                       # 藤壶：亮 / 暗 / 口


# ============================================================ 小工具
def ss(t):
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return t * t * (3 - 2 * t)


def bump(d, half):
    """|d| < half 时的 cos² 包络（中间 1、两头 0）。"""
    if abs(d) >= half:
        return 0.0
    c = math.cos(math.pi * d / (2.0 * half))
    return c * c


def lambert(z, light, smooth=1.0):
    """高度场 → 朝光程度（-1..1）。light = (x, y, z)：x > 0 光从右边来、y < 0 光从上面来。"""
    zz = ndimage.gaussian_filter(z.astype(np.float32), smooth) if smooth else z.astype(np.float32)
    gy, gx = np.gradient(zz)
    L = np.asarray(light, np.float32)
    L = L / np.linalg.norm(L)
    return (-gx * L[0] - gy * L[1] + L[2]) / np.sqrt(gx * gx + gy * gy + 1.0)


def quant(u, n, dither=0.55):
    """0..1 → 调色板档位：只在档与档的交界按 Bayer 抖（像素风，不是满屏噪点）。"""
    h, w = u.shape
    bay = A._bayer(w, h)
    return np.clip(np.floor(u * (n - 1) + 0.5 + (bay - 0.5) * dither), 0, n - 1).astype(int)


def lum(a):
    a = a.astype(np.float32)
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


# ============================================================ 轮廓线
def ubase(x):
    """上牙龈线的大形（不算牙位起伏）：中间高两头低，比锚点 y 低 4.5 px → 牙位处（再往上拱 1.5）比牙根尖低 2 px。"""
    return 64.5 + 4.0 * ((x - 160) / 100.0) ** 2


def uedge_s(x):
    """上颚下沿的大形（世界 y）：左边软腭往喉咙垂、右边上唇往嘴角收，过了嘴角沿唇缝往右上走。"""
    if x < 54:
        return ubase(54) + (54 - x) * 0.32 + ((54 - x) / 54.0) ** 2 * 6.0
    if x <= 262:
        return ubase(x)
    if x <= CORNER[0]:
        return ubase(262) + (CORNER[1] - ubase(262)) * ss((x - 262) / float(CORNER[0] - 262))
    return CORNER[1] - (x - CORNER[0]) * (CORNER[1] - LIPS_R[0]) / float(W - CORNER[0])


def uedge(x):
    """上颚下沿（牙位处往上拱 1.5 px 贴着牙根，牙缝处牙龈乳头往下垂 3 px）。"""
    e = uedge_s(x)
    for tx in TEETH_X:
        e -= 1.5 * bump(x - tx, 7)
    for m in PAPILLAE:
        e += 3.0 * bump(x - m, 8)
    return e


def lbase(x):
    """下牙床上沿的大形：比锚点 y 高 10 px（下牙立在 152–154，根穿过牙床）。"""
    return 140.0 - 2.0 * ((x - 160) / 100.0) ** 2


def ltop_s(x):
    if x < 46:
        return 999.0                                              # 牙床在舌根后面收掉了
    if x < 60:
        return lbase(60) + ((60 - x) / 14.0) ** 2 * 14.0
    if x <= 262:
        return lbase(x)
    if x <= CORNER[0]:
        return lbase(262) + (CORNER[1] - lbase(262)) * ss((x - 262) / float(CORNER[0] - 262))
    return CORNER[1] + (x - CORNER[0]) * (LIPS_R[1] - CORNER[1]) / float(W - CORNER[0])


def ltop(x):
    t = ltop_s(x)
    for tx in TEETH_X:
        t += 1.5 * bump(x - tx, 7)
    for m in PAPILLAE:
        t -= 3.0 * bump(x - m, 8)
    return t


def tback(x):
    """舌头后沿（贴着下牙床）；x < 52 舌根往下卷进喉咙。"""
    b = 147.0 + 0.7 * math.sin(x / 17.0 + 0.5) + 0.4 * math.sin(x / 6.1 + 1.0)
    if x < 52:
        b += ((52 - x) / 52.0) ** 2 * 24.0
    return b


UE = np.array([uedge(x) for x in range(W)], np.float32)
UES = np.array([uedge_s(x) for x in range(W)], np.float32)
LT = np.array([ltop(x) for x in range(W)], np.float32)
LTS = np.array([ltop_s(x) for x in range(W)], np.float32)
TB = np.array([tback(x) for x in range(W)], np.float32)


# ============================================================ 嘴外的海
@lru_cache(maxsize=2)
def outside_img(bright=False):
    """嘴外的海（整张 320×180，世界坐标；唇缝 / 张嘴的口子里看到的是它的一部分）：上亮下深的蓝、斜的光柱、
    远处的沙底（沙纹 + 亮脊）、礁石剪影、海草、几条小鱼影。bright = 张嘴那一下：整体往白里提。"""
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), [(0.0, (196, 238, 248)), (0.34, (112, 198, 230)), (0.62, (44, 124, 178)),
                                (1.0, (18, 62, 112))], bands=14)
    a = np.array(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    s = (xx * 0.5 + yy) % 38
    shaft = (s < 6) & (A._bayer(W, H) < np.clip(1 - yy / 160.0, 0, 1) * 0.9)
    a[shaft, :3] = a[shaft, :3] * 0.8 + 255 * 0.2
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    for x in range(W):                                             # 远处的沙底
        fy = int(round(118 + 3 * math.sin(x / 23.0) + 1.5 * math.sin(x / 8.0 + 1)))
        for y in range(fy, H):
            c = mix((132, 168, 178), (64, 98, 126), (y - fy) / 46.0)
            if (y - fy) % 5 == 2 and hash01(x // 4, y, 3) < 0.6:
                c = dk(c, 0.86)
            px(d, x, y, c)
        px(d, x, fy, (166, 198, 204))
    for (x0, w, h, sd) in ((244, 22, 10, 1), (270, 14, 7, 2), (300, 18, 9, 3)):   # 礁石剪影（远，罩着蓝）
        for k in range(w):
            u = k / float(w - 1)
            top = int(round(121 - h * math.sin(math.pi * u) ** 0.7 + hrange(-1, 1, sd, k)))
            vl(d, x0 + k, top, 124, (46, 84, 112))
            px(d, x0 + k, top, (72, 116, 140))
    for (kx, base, L, ph) in ((256, 126, 26, 0.0), (284, 124, 20, 1.3), (312, 125, 30, 2.1), (300, 126, 14, 0.7)):
        for k in range(L):                                         # 海草（往右上飘的一条条）
            y = base - k
            x = kx + int(round(2.2 * math.sin(k / 6.0 + ph) + k * 0.08))
            px(d, x, y, (30, 98, 104) if k % 4 else (52, 128, 120))
            if k % 5 == 2:
                px(d, x + 1, y - 1, (40, 112, 112))
    for (fx, fy) in ((298, 96), (306, 92), (262, 84), (276, 70)):  # 小鱼影
        hl(d, fx, fx + 2, fy, (36, 80, 116))
        px(d, fx + 3, fy - 1, (36, 80, 116))
        px(d, fx + 3, fy + 1, (36, 80, 116))
    if bright:
        a = np.array(im).astype(np.float32)
        k = np.clip(1.0 - np.hypot((xx - 330) / 120.0, (yy - 90) / 90.0), 0, 1)[..., None] * 0.7 + 0.25
        a[..., :3] = a[..., :3] * (1 - k) + np.array((236, 250, 255), np.float32) * k
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    return im


# ============================================================ 内壁 / 喉咙（wall）
FOLDS = [(74, 66, 12, 4.2), (118, 128, 11, 3.6), (166, 158, 13, 4.4), (214, 224, 11, 3.6), (258, 250, 12, 4.2)]
# 竖的软褶：(y 60 处 x, y 150 处 x, 半宽, 高)——宽而矮、间距不等，读起来是软的肉，不是一排柱子


def cheek_rgb():
    """颊黏膜：整体往外鼓（中间亮）+ 几道宽的软褶（光从右来：褶的右边亮）+ 一点起伏；贴着上下牙床、靠喉咙那头暗下去。
    明暗只用中间几档：内壁是人物身后的底，要暗、要静。"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    z = 7.0 * np.sin(np.clip((yy - 58) / 92.0, 0, 1) * math.pi)
    for i, (xa, xb, w_, amp) in enumerate(FOLDS):
        u = np.clip((yy - 60) / 90.0, 0, 1)
        cx = xa + (xb - xa) * u + 3.0 * np.sin(yy / 14.0 + i * 1.7)
        z += amp * np.exp(-((xx - cx) / w_) ** 2)
    z += (A._fbm(W, H, 9, seed=73) - 0.5) * 3.0
    lam = lambert(z, (0.8, -0.15, 0.55), smooth=1.6)
    u = np.clip((lam - 0.28) / 0.9, 0, 1)
    ao = (0.4 + 0.6 * np.clip((yy - 64) / 24.0, 0, 1)) * (0.5 + 0.5 * np.clip((146 - yy) / 24.0, 0, 1))
    ao *= 0.42 + 0.58 * np.clip((xx - 44) / 76.0, 0, 1)
    q = quant(u * ao, len(CHEEK))
    return np.array(CHEEK, np.uint8)[q], q, lam


def throat_paint(rgb):
    """喉咙洞：椭圆里径向变暗（中心最深），几圈软骨环在朝光的右半边亮一档。"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - TH_C[0]) / TH_R[0]) ** 2 + ((yy - TH_C[1]) / TH_R[1]) ** 2)
    inside = d < 1.0
    q = quant(np.clip(d, 0, 1) ** 1.6, len(THROAT), dither=0.7)
    ring = ((np.abs(d - 0.40) < 0.03) | (np.abs(d - 0.60) < 0.032) | (np.abs(d - 0.80) < 0.03)) & (xx > TH_C[0] - 2)
    q = np.clip(q + ring.astype(int), 0, len(THROAT) - 1)
    rgb[inside] = np.array(THROAT, np.uint8)[q][inside]
    return inside


def pillar(rgb, cxf, y0, y1, half, pal):
    """一道腭弓（竖的肉柱）：中心线 x = cxf(y)，两头收细；横截面半圆柱，朝右（光）的一半亮，左沿描墨线。"""
    bay = A._bayer(W, H)
    n = len(pal)
    for y in range(y0, y1 + 1):
        u = (y - y0) / float(y1 - y0)
        hw = half * (0.55 + 0.45 * math.sin(math.pi * u) ** 0.6)
        cx = cxf(y)
        for x in range(int(math.floor(cx - hw)), int(math.ceil(cx + hw)) + 1):
            if not (0 <= x < W):
                continue
            s = (x - cx) / hw
            if abs(s) > 1.0:
                continue
            v = 0.5 + 0.5 * s * 0.9 + 0.12 * math.sqrt(max(0.0, 1 - s * s))
            k = int(np.clip(math.floor(v * (n - 1) + 0.5 + (bay[y, x] - 0.5) * 0.6), 0, n - 1))
            rgb[y, x] = pal[k]
            if s < -0.8:
                rgb[y, x] = INK


@lru_cache(maxsize=1)
def wall_img():
    rgb, q, lam = cheek_rgb()
    rgb = rgb.copy()
    yy, xx = np.mgrid[0:H, 0:W]
    # 湿的反光：褶子最朝光的地方顺着褶子竖着的几道短亮痕（不是满墙的小点——小点多了像星星 / 灰尘）
    top = lam > np.percentile(lam[64:140, 60:280], 96)
    spec = top & (yy > 74) & (yy < 132) & (xx > 70) & (xx < 284)
    for (y, x) in zip(*np.nonzero(spec)):
        if hash01(x // 2, y // 5, 51) < 0.22:
            rgb[y, x] = CHEEK[-1] if hash01(x, y, 52) < 0.75 else SPEC
    im = Image.fromarray(np.dstack([rgb, np.full((H, W), 255, np.uint8)]), 'RGBA')
    d = ImageDraw.Draw(im)
    # 咬合线（颊黏膜上一道淡淡的横棱）
    for x in range(66, 282):
        y = int(round(104 + 1.2 * math.sin(x / 21.0) + 0.6 * math.sin(x / 7.0)))
        if hash01(x, 61) < 0.8:
            c = tuple(int(v) for v in rgb[y, x])
            px(d, x, y, mix(c, CHEEK[-2], 0.6))
            px(d, x, y + 1, dk(c, 0.82))
    # 血管：几根细细的、分叉的暗紫线（只在内壁上半，压得很淡）
    for (x0, y0, L, ang, sd) in ((84, 78, 30, 0.35, 1), (150, 74, 26, -0.2, 2), (206, 80, 34, 0.25, 3),
                                 (118, 120, 22, -0.3, 4), (242, 118, 20, 0.4, 5)):
        x, y = float(x0), float(y0)
        for k in range(L):
            x += math.cos(ang + 0.5 * math.sin(k / 4.0 + sd))
            y += math.sin(ang + 0.5 * math.sin(k / 4.0 + sd))
            c = tuple(int(v) for v in rgb[int(y), int(x)])
            px(d, int(x), int(y), mix(c, VEIN, 0.55))
            if k == L // 2:                                        # 分一个小叉
                bx, by = x, y
                for j in range(L // 3):
                    bx += math.cos(ang + 0.9)
                    by += math.sin(ang + 0.9)
                    c = tuple(int(v) for v in rgb[int(by), int(bx)])
                    px(d, int(bx), int(by), mix(c, VEIN, 0.45))
    rgb = np.array(im)[..., :3].copy()
    # 喉咙 + 两道腭弓（后面那道暗、前面那道朝光的一侧亮）
    throat_paint(rgb)
    pillar(rgb, lambda y: 29 + 4 * math.sin(math.pi * (y - 76) / 86.0), 76, 162, 3.6,
           [THROAT[2], CHEEK[1], CHEEK[2], CHEEK[3]])
    pillar(rgb, lambda y: 42 + 6 * math.sin(math.pi * (y - 64) / 100.0), 64, 164, 5.2,
           [GUM[1], GUM[2], GUM[3], GUM[4], GUM[5]])
    # 唇缝外的海（嘴角往右的楔形；上下唇画在 jaw / lower 里，这里多铺几行让唇压住）
    out = np.array(outside_img(False))[..., :3]
    for x in range(CORNER[0] - 1, W):
        y0 = int(math.floor(UES[x])) - 4
        y1 = int(math.ceil(LTS[x])) + 4
        rgb[y0:y1, x] = out[y0:y1, x]
    # 嘴角那一小段内壁收进去的折痕（暗）
    for x in range(272, CORNER[0] + 1):
        yc = (UES[x] + LTS[x]) / 2.0
        hh = max(0.0, (LTS[x] - UES[x]) / 2.0 - 1)
        for y in range(int(yc - hh), int(yc + hh) + 1):
            k = 1.0 - abs(y - yc) / max(1.0, hh + 1)
            if k > 0.55 and hash01(x, y, 71) < 0.9:
                rgb[y, x] = THROAT[3] if k > 0.8 else CHEEK[1]
    return Image.fromarray(np.dstack([rgb, np.full((H, W), 255, np.uint8)]), 'RGBA')


# ============================================================ 上颚（jaw，pick）
@lru_cache(maxsize=1)
def jaw_canvas():
    """上颚画布：世界 y 从 −12 画到 JAW_H − 1（多出来的 12 行是硬腭，给 bite 下移以后补顶）。
    返回 RGBA（JAW_H + 12 行）。"""
    hh = JAW_H + EXT
    yy = (np.arange(hh, dtype=np.float32) - EXT)[:, None] + np.zeros((1, W), np.float32)
    xx = np.arange(W, dtype=np.float32)[None, :] + np.zeros((hh, 1), np.float32)
    mask = yy <= UE[None, :]
    # 高度场：沿下沿走的一条肉棱（上半径 12、下半径 = 到下沿的距离 → 牙龈乳头也是圆的），棱上面是一道道横的腭褶
    yc = UES[None, :] - 11.0
    dy = yy - yc
    rb = np.maximum(3.0, UE[None, :] - yc + 0.6)
    r = np.where(dy < 0, 12.0, rb)
    z = np.sqrt(np.clip(1 - (dy / r) ** 2, 0, 1)) * 12.0
    above = dy < -12.0
    v = -dy - 12.0
    # 腭褶：间距、走向、高低都不匀（一道道整齐的横纹会像木纹），被噪声打断成一段段
    wob = 3.0 * np.sin(xx / 23.0 + 1.3) + 2.0 * np.sin(xx / 9.0 + v / 7.0)
    per = 7.0 + 2.0 * np.sin(xx / 41.0)
    brk = A._fbm(W, hh, 11, seed=97)
    rib = 2.0 * (0.5 - 0.5 * np.cos(2 * np.pi * (v + wob) / per)) * np.clip(brk * 1.8 - 0.35, 0, 1)
    z = np.where(above, rib, z)
    z += (A._fbm(W, hh, 6, seed=91) - 0.5) * 1.6
    lam = lambert(z, (0.6, 0.45, 0.65), smooth=0.9)              # 光从右下（唇缝在嘴的中间高度）来
    u = np.clip((lam - 0.18) / 0.86, 0, 1)
    u = np.where(above, u * (0.12 + 0.36 * np.clip(1 - v / 40.0, 0, 1) ** 1.5), u)   # 硬腭：远、背光，越往上越暗
    u = u * (0.5 + 0.5 * np.clip((xx - 8) / 64.0, 0, 1))         # 软腭往喉咙那头暗
    q = quant(u, len(GUM))
    rgb = np.array(GUM, np.uint8)[q]
    # 靠唇缝那头，朝光的面带一点海水的青色（光源是唇缝外的海）
    cy_ = np.clip((xx - 196) / 110.0, 0, 1) * (q >= len(GUM) - 3) * 0.28
    rgb = np.clip(rgb * (1 - cy_[..., None]) + np.array((120, 196, 222), np.float32) * cy_[..., None], 0, 255
                  ).astype(np.uint8)
    # 肉棱上湿亮的高光：最朝光的那一圈、零零星星
    hot = (q == len(GUM) - 1) & ~above & mask
    for (r_, c_) in zip(*np.nonzero(hot)):
        if hash01(c_, r_, 17) < 0.16:
            rgb[r_, c_] = SPEC
    # 牙槽：每个牙位一个往下开口的小坑（上半最深、右下的内壁被唇缝的光照到一点），坑边一圈牙龈亮一档
    for (tx, gy) in UPPER:
        e0 = float(UE[tx])
        cy = e0 - 2.6
        for y in range(int(cy - 6), int(e0) + 3):
            r_ = y + EXT
            for x in range(tx - 7, tx + 8):
                dd = ((x - tx) / 4.6) ** 2 + ((y - cy) / 4.2) ** 2
                if dd < 1.0 and y <= e0 + 1.6:
                    mask[r_, x] = True
                    if (x - tx) > 1.2 and (y - cy) > 0.3 and dd > 0.3:
                        rgb[r_, x] = SOCK[3] if dd > 0.62 else SOCK[2]
                    else:
                        rgb[r_, x] = SOCK[0] if dd < 0.5 else SOCK[1]
                elif 1.0 <= dd < 1.9 and y >= cy - 2 and mask[r_, x]:
                    rgb[r_, x] = GUM[min(len(GUM) - 1, int(q[r_, x]) + 1)]
    # 下沿描一道深色的线（牙槽口除外）：唇缝的光从下面来，牙龈线本身亮，靠这条线和内壁分开
    for x in range(W):
        rows = np.nonzero(mask[:, x])[0]
        if len(rows):
            r_ = rows.max()
            if not any(abs(x - tx) <= 3 for tx in TEETH_X):
                rgb[r_, x] = INK
    # 上唇外沿粘的几颗藤壶（这张嘴是海底的岩石变的）：小小的一个土包，顶上一个暗口
    for i in range(5):
        x = int(hrange(298, 317, i, 31))
        y = int(UES[x] - hrange(5, 14, i, 32)) + EXT
        if all(mask[y + dy, x + dx] for dx in (-1, 0, 1) for dy in (0, 1)):
            rgb[y, x] = BARN[2]
            rgb[y + 1, x - 1] = BARN[1]                            # 光从右边（唇缝）来：右亮左暗
            rgb[y + 1, x] = BARN[0]
            rgb[y + 1, x + 1] = BARN[0]
    a = np.dstack([rgb, np.where(mask, 255, 0).astype(np.uint8)])
    return a


@lru_cache(maxsize=1)
def jaw_imgs():
    """(常态, bite)：bite 那张 = 画布从世界 y −12 开始取 → 整个上颚往下移 12 px，顶上是多画的硬腭。"""
    a = jaw_canvas()
    return (Image.fromarray(a[EXT:EXT + JAW_H].copy(), 'RGBA'), Image.fromarray(a[0:JAW_H].copy(), 'RGBA'))


# ============================================================ 下牙床（lower）
@lru_cache(maxsize=1)
def lower_img():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    mask = (yy >= LT[None, :]) & (yy < 162)
    yc = LTS[None, :] + 10.0
    dy = yy - yc
    z = np.where(dy < 0, np.sqrt(np.clip(1 - (dy / 10.0) ** 2, 0, 1)) * 10.0, 10.0 - dy * 0.15)
    rt = np.maximum(2.0, yc - LT[None, :])                        # 牙龈乳头也是圆的
    z = np.where(dy < 0, np.sqrt(np.clip(1 - (dy / rt) ** 2, 0, 1)) * 10.0, z)
    z += (A._fbm(W, H, 6, seed=93) - 0.5) * 1.4
    lam = lambert(z, (0.6, -0.55, 0.6), smooth=0.9)               # 光从右上来：牙床上半亮
    u = np.clip((lam - 0.2) / 0.8, 0, 1)
    u = u * (0.55 + 0.45 * np.clip((xx - 40) / 60.0, 0, 1))
    q = quant(u, len(GUM))
    rgb = np.array(GUM, np.uint8)[q]
    cy_ = np.clip((xx - 196) / 110.0, 0, 1) * (q >= len(GUM) - 3) * 0.28          # 同上颚：靠唇缝的亮面带青
    rgb = np.clip(rgb * (1 - cy_[..., None]) + np.array((120, 196, 222), np.float32) * cy_[..., None], 0, 255
                  ).astype(np.uint8)
    hot = (q == len(GUM) - 1) & mask
    for (r_, c_) in zip(*np.nonzero(hot)):
        if hash01(c_, r_, 19) < 0.16:
            rgb[r_, c_] = SPEC
    for (tx, gy) in LOWER:                                         # 牙槽：往上开口
        t0 = float(LT[tx])
        cy = t0 + 2.6
        for y in range(int(t0) - 3, int(cy + 6)):
            for x in range(tx - 7, tx + 8):
                dd = ((x - tx) / 4.6) ** 2 + ((y - cy) / 4.2) ** 2
                if dd < 1.0 and y >= t0 - 1.6:
                    mask[y, x] = True
                    if (x - tx) > 1.2 and (y - cy) < -0.3 and dd > 0.3:
                        rgb[y, x] = SOCK[3] if dd > 0.62 else SOCK[2]
                    else:
                        rgb[y, x] = SOCK[0] if dd < 0.5 else SOCK[1]
                elif 1.0 <= dd < 1.9 and y <= cy + 2 and mask[y, x]:
                    rgb[y, x] = GUM[min(len(GUM) - 1, int(q[y, x]) + 1)]
    for x in range(W):                                             # 上沿描线（牙槽口除外）
        rows = np.nonzero(mask[:, x])[0]
        if len(rows) and not any(abs(x - tx) <= 3 for tx in TEETH_X):
            rgb[rows.min(), x] = INK
    for i in range(6):                                             # 下唇外沿的藤壶
        x = int(hrange(298, 317, i, 33))
        y = int(LTS[x] + hrange(5, 18, i, 34))
        if all(mask[y + dy, x + dx] for dx in (-1, 0, 1) for dy in (0, 1)):
            rgb[y, x] = BARN[2]
            rgb[y + 1, x - 1] = BARN[1]                            # 光从右边（唇缝）来：右亮左暗
            rgb[y + 1, x] = BARN[0]
            rgb[y + 1, x + 1] = BARN[0]
    return Image.fromarray(np.dstack([rgb, np.where(mask, 255, 0).astype(np.uint8)]), 'RGBA')


# ============================================================ 舌头（tongue，可走带）
@lru_cache(maxsize=1)
def tongue_img():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    mask = yy >= np.floor(TB)[None, :]
    dy = yy - TB[None, :]
    z = 6.0 * np.sqrt(np.clip(dy / 5.0, 0, 1)) - 0.04 * np.clip(dy, 0, None)      # 后沿一道圆的舌缘，往前微微下坡
    z -= np.clip((yy - 173) / 7.0, 0, 1) ** 2 * 7.0                              # 前沿往下卷（舌头的侧面）
    z += (A._fbm(W, H, 9, seed=95) - 0.5) * 1.2
    lam = lambert(z, (0.55, -0.6, 0.65), smooth=1.0)
    u = np.clip((lam - 0.25) / 0.75, 0, 1)
    k = 1.0 - 0.92 * np.clip((64 - xx) / 64.0, 0, 1) ** 1.3     # 舌根往喉咙卷：x < 64 一路暗下去
    q = quant(u * k, len(TONGUE))
    # 舌乳头：零星的小点（亮一档，右下跟一个暗一档），只在可走带里、压得很淡
    yi, xi = np.nonzero(mask & (yy > TB[None, :] + 4) & (yy < 175) & (xx > 52))
    for (y, x) in zip(yi, xi):
        h = hash01(x, y, 23)
        if h < 0.05:
            q[y, x] = min(len(TONGUE) - 1, q[y, x] + 1)
            if y + 1 < H and x + 1 < W:
                q[y + 1, x + 1] = max(0, q[y + 1, x + 1] - 1)
    rgb = np.array(TONGUE, np.uint8)[q]
    # 喉咙那头：舌根的颜色往喉咙的暗红里混（不是简单压暗，免得发灰）
    kk = np.clip((60 - xx) / 60.0, 0, 1) ** 1.2
    rgb = (rgb.astype(np.float32) * (1 - kk[..., None] * 0.75) + np.array(THROAT[1], np.float32) * kk[..., None] * 0.75)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    # 后沿：和牙床之间的一道深缝；前沿最底一行暗
    for x in range(W):
        r0 = int(math.floor(TB[x]))
        rgb[r0, x] = (64, 16, 34) if x >= 40 else THROAT[1]
        rgb[H - 1, x] = dk(tuple(int(v) for v in rgb[H - 1, x]), 0.8)
    return Image.fromarray(np.dstack([rgb, np.where(mask, 255, 0).astype(np.uint8)]), 'RGBA')


# ============================================================ 动的东西
UVULA_REGION = (6, 70, 36, 106)


@lru_cache(maxsize=N_ANIM)
def _uvula(f):
    """悬雍垂：从软腭垂下来的一颗肉坠（上细下圆），尖端左右晃 ±2 px；朝右的一边亮、左边和底描墨线。"""
    a = np.zeros((H, W, 4), np.uint8)
    sway = 2.0 * math.sin(math.tau * f / N_ANIM)
    top = int(UE[UV_X]) - 3
    bay = A._bayer(W, H)
    for i in range(UV_LEN + 1):
        u = i / float(UV_LEN)
        y = top + i
        cx = UV_X + sway * u * u
        hw = 1.5 + 2.9 * min(u, 0.68) ** 0.8                     # 上细下粗的一颗肉坠
        if u > 0.68:                                               # 底下收圆
            hw *= math.sqrt(max(0.0, 1 - ((u - 0.68) / 0.32) ** 2))
        for x in range(int(math.floor(cx - hw)), int(math.ceil(cx + hw)) + 1):
            s = (x - cx) / max(0.6, hw)
            if abs(s) > 1.05:
                continue
            v = 0.45 + 0.45 * s + 0.1 * (1 - u)
            k = int(np.clip(math.floor(v * 5 + 0.5 + (bay[y, x] - 0.5) * 0.6), 0, 5))
            a[y, x, :3] = GUM[1 + k]
            a[y, x, 3] = 255
            if s < -0.75 or (u > 0.95):
                a[y, x, :3] = INK
    yb = top + UV_LEN - 4
    xb = int(round(UV_X + sway * 0.8 + 1))
    a[yb, xb, :3] = SPEC                                           # 湿的高光
    return Image.fromarray(a, 'RGBA')


def uvula_frame(t):
    return _uvula(fno(t))


FLOW_REGION = (0, 60, 176, 180)
STREAMS = [((116, 82), (60, 76), (14, 106)), ((128, 106), (66, 102), (14, 117)), ((116, 130), (60, 132), (14, 128))]
# 流线：起点、控制点、终点（往喉咙收；只在喉咙这一半，免得像划痕横穿战斗区）


def _bez(p0, p1, p2, u):
    return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
            (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1])


@lru_cache(maxsize=N_ANIM)
def _flow(f):
    """往喉咙吸的水流（半透明）：① 四道流线上的虚线往喉咙走（每帧 2 px，16 px 一周期 = 8 帧闭合）；
    ② 空中十几粒碎屑从右往喉咙收，越近越快（p² 缓动）；③ 舌面上一道道往左拖的水纹（≈ 舌头卷人的 40 px/s）。"""
    a = np.zeros((H, W, 4), np.uint8)

    def put(x, y, col, al):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H and al > a[y, x, 3]:
            a[y, x] = col + (int(al),)
    for j, (p0, p1, p2) in enumerate(STREAMS):
        pts = [_bez(p0, p1, p2, i / 400.0) for i in range(401)]
        s = 0.0
        last = pts[0]
        for (x, y) in pts:
            s += math.hypot(x - last[0], y - last[1])
            last = (x, y)
            ph = (s - 2.0 * f - j * 5) % 16.0
            if ph < 4:
                fade = ss((p0[0] - x) / 36.0) * (1 - ss((26 - x) / 14.0))
                put(x, y, (232, 176, 186), 56 * fade)
    for i in range(11):                                           # 碎屑
        p = (hash01(i, 401) + f / float(N_ANIM)) % 1.0
        sx, sy = hrange(78, 150, i, 402), hrange(68, 140, i, 403)
        ex, ey = TH_C[0] + hrange(-3, 6, i, 404), TH_C[1] + hrange(-24, 18, i, 405)
        q = p * p
        x = sx + (ex - sx) * q
        y = sy + (ey - sy) * q + 1.5 * math.sin(math.tau * p + i)
        fade = ss(p / 0.15) * (1 - ss((p - 0.78) / 0.22))
        q2 = max(0.0, p - 0.05) ** 2
        tx_, ty_ = sx + (ex - sx) * q2, sy + (ey - sy) * q2
        put(x, y, (236, 196, 200), 150 * fade)
        put((x + tx_) / 2, (y + ty_) / 2, (214, 160, 170), 90 * fade)
        put(tx_, ty_, (196, 136, 150), 50 * fade)
    for i in range(10):                                           # 舌面的水纹（往左拖）
        p = (hash01(i, 411) + f / float(N_ANIM)) % 1.0
        y = int(hrange(153, 172, i, 412))
        x0 = hrange(118, 170, i, 413)
        x = x0 - 80 * p
        fade = ss(p / 0.12) * (1 - ss((44 - x) / 12.0))
        L = int(hrange(4, 7, i, 414))
        for k in range(L):
            put(x + k, y, (236, 162, 168), 96 * fade * (1 - k / float(L + 1)))
    return Image.fromarray(a, 'RGBA')


def flow_frame(t):
    return _flow(fno(t))


RAYS_REGION = (150, 60, 320, 180)


CAUSTIC_PTS = [(gx + hrange(-4, 4, gx, gy, 1), gy + hrange(-3, 3, gx, gy, 2), hrange(0, math.tau, gx, gy, 3))
               for gx in range(180, 336, 10) for gy in range(54, 190, 9)]


@lru_cache(maxsize=N_ANIM)
def _rays(f):
    """唇缝透进来的光在嘴里晃：水面焦散那种网状的亮纹（一格格的边），投在内壁和舌尖上，越靠唇缝越亮、往里淡掉。
    （半透明的“光束”叠在暗红上会发灰，像烟；焦散是直接照亮肉的表面，读得出来是光。）
    网 = 一把散点的 Voronoi 边（到最近两点的距离差很小的地方）；每个点绕自己的小圆走，8 帧走一圈 → 闭合。"""
    from scipy.spatial import cKDTree
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ph = math.tau * f / float(N_ANIM)
    pts = np.array([(x + 2.6 * math.cos(ph + t), y + 2.2 * math.sin(ph + t)) for (x, y, t) in CAUSTIC_PTS], np.float32)
    dd, _ = cKDTree(pts).query(np.c_[xx.ravel(), yy.ravel()], k=2)
    gap = (dd[:, 1] - dd[:, 0]).reshape(H, W)
    line = gap < 0.9
    node = gap < 0.45                                              # 网眼交汇的地方更亮一点
    dist = np.hypot((xx - 322) / 96.0, (yy - 101) / 58.0)
    fade = np.clip(1.0 - dist, 0, 1) ** 0.9
    wall = (yy > UE[None, :] + 3) & (yy < LT[None, :] - 2) & (xx < CORNER[0] - 1)      # 内壁上（唇缝里不画）
    tng = (yy > TB[None, :] + 2) & (yy < 175)                                          # 舌尖上（更淡）
    al = np.where(wall, 170 * fade, np.where(tng, 90 * fade, 0)) * line * np.where(node, 1.0, 0.75)
    al = np.floor(al / 16.0) * 16.0                                # 透明度分档（省字节、像素风）
    a = np.zeros((H, W, 4), np.uint8)
    a[..., :3] = (255, 162, 170)                                   # 偏暖的粉白：照在红肉上是“亮”，不发灰
    a[..., 3] = np.clip(al, 0, 255).astype(np.uint8)
    a[..., 3][(al < 32)] = 0
    return Image.fromarray(a, 'RGBA')


def rays_frame(t):
    return _rays(fno(t))


DROOL_REGIONS = [(DROOL_X[0] - 4, 60, DROOL_X[0] + 5, 146), (DROOL_X[1] - 4, 60, DROOL_X[1] + 5, 146)]


@lru_cache(maxsize=N_ANIM)
def _drool(f):
    """两处牙龈乳头上的口水（不透明的小像素）：挂着一滴 → 越拉越长 → 断开往下掉 → 落到下牙床溅开；两处错开 4 帧。"""
    a = np.zeros((H, W, 4), np.uint8)

    def put(x, y, col):
        if 0 <= x < W and 0 <= y < H:
            a[y, x, :3] = col
            a[y, x, 3] = 255
    for j, x in enumerate(DROOL_X):
        g = (f + 4 * j) % N_ANIM
        e = int(math.floor(UE[x])) + 1
        land = int(math.floor(LT[x])) - 1
        if g <= 3:                                                 # 挂着、越拉越长
            L = (0, 2, 5, 9)[g]
            for y in range(e, e + L):
                put(x, y, (210, 172, 188))
            yd = e + L
            put(x, yd, SALIVA)
            put(x, yd + 1, SALIVA)
            if g >= 1:
                put(x + 1, yd, (196, 160, 176))
                put(x, yd + 2, (200, 166, 182))
            put(x - 1 if g % 2 else x, yd, (252, 240, 244))
        elif g <= 6:                                               # 断了往下掉（越掉越快），乳头上留一小截
            put(x, e, (210, 172, 188))
            if g == 4:
                put(x, e + 1, (210, 172, 188))
            yd = e + (16, 36, 60)[g - 4]
            yd = min(yd, land - 3)
            for k in range(2 + (g - 4)):
                put(x, yd - k, SALIVA if k else (252, 240, 244))
            put(x + 1, yd, (196, 160, 176))
        else:                                                      # 落地溅开
            put(x, e, (210, 172, 188))
            for (dx, dy) in ((-3, -2), (-2, -1), (2, -1), (3, -2), (0, 0), (-1, 0), (1, 0)):
                put(x + dx, land + dy, SALIVA if dy < 0 else (210, 172, 188))
    return Image.fromarray(a, 'RGBA')


def drool_frame(t):
    return _drool(fno(t))


BUB_REGION = (110, 56, 320, 150)


def _bubble(a, x, y, r):
    """一颗气泡：一圈浅青的边 + 左上一点白高光，中间透明（看得见后面）。"""
    x, y = int(round(x)), int(round(y))
    if r <= 1:
        ring = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        ring = [(dx, dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                if abs(math.hypot(dx, dy) - r) < 0.6]
    for (dx, dy) in ring:
        if 0 <= x + dx < W and 0 <= y + dy < H:
            a[y + dy, x + dx] = (176, 228, 240, 210)
    hx, hy = x - max(0, r - 1), y - max(0, r - 1)
    if 0 <= hx < W and 0 <= hy < H:
        a[hy, hx] = (250, 255, 255, 240)


@lru_cache(maxsize=N_ANIM)
def _bubbles(f):
    """唇缝冒进来的气泡：往上浮、往左飘、左右摆，碰到上唇就破（最后一下画个小水花）；下牙床那边偶尔冒一串小的。"""
    a = np.zeros((H, W, 4), np.uint8)
    for i in range(9):
        p = (hash01(i, 601) + f / float(N_ANIM)) % 1.0
        x0, y0 = hrange(293, 316, i, 602), hrange(98, 118, i, 603)
        x = x0 - hrange(6, 16, i, 604) * p + 1.2 * math.sin(math.tau * (2 * p + hash01(i, 605)))
        y = y0 - hrange(26, 40, i, 606) * p
        r = 1 if hash01(i, 607) < 0.6 else 2
        ceil_ = UE[int(min(W - 1, max(0, round(x))))] + 2 + r
        if y < ceil_:
            if y > ceil_ - 6:                                      # 刚碰到：破成两三点
                for (dx, dy) in ((-1, 0), (1, -1), (0, 1)):
                    xx_, yy_ = int(round(x)) + dx, int(round(ceil_)) + dy
                    if 0 <= xx_ < W and 0 <= yy_ < H:
                        a[yy_, xx_] = (210, 242, 250, 170)
            continue
        _bubble(a, x, y, r)
    for i in range(3):                                            # 嘴里的小气泡（从下牙床的牙缝冒出来）
        p = (hash01(i, 611) + f / float(N_ANIM)) % 1.0
        x0 = (160, 200, 160)[i] + hrange(-3, 3, i, 612)
        y0 = LT[int(x0)] - 2
        y = y0 - 60 * p
        x = x0 + 1.0 * math.sin(math.tau * (2 * p) + i)
        if y < UE[int(x0)] + 4:
            continue
        _bubble(a, x, y, 1)
    return Image.fromarray(a, 'RGBA')


def bubbles_frame(t):
    return _bubbles(fno(t))


# ============================================================ key bite / spit
@lru_cache(maxsize=1)
def bite_dim_img():
    """咬下来时的暗角：四角压暗 + 压下来的上牙床下面一道阴影（往下淡）；透明度分 5 档、档的交界按 Bayer 抖。"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 170) / 200.0) ** 2 + ((yy - 112) / 118.0) ** 2)
    al = np.clip((d - 0.55) / 0.5, 0, 1) * 150
    s = yy - (UE[None, :] + BITE_DY)
    al += np.where((s > 0) & (s < 16), (1 - s / 16.0) * 90, 0)
    al = np.clip(al, 0, 200)
    lv = np.clip(np.floor(al / 40.0 + A._bayer(W, H)), 0, 5)
    a = np.zeros((H, W, 4), np.uint8)
    a[..., :3] = (26, 4, 12)
    a[..., 3] = (lv * 40).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def spit_top(x):
    u = max(0.0, (x - SPIT_C[0]) / float(W - SPIT_C[0]))
    return SPIT_C[1] - 86.0 * u ** 0.75


def spit_bot(x):
    u = max(0.0, (x - SPIT_C[0]) / float(W - SPIT_C[0]))
    return SPIT_C[1] + 48.0 * u ** 0.8


@lru_cache(maxsize=1)
def spit_open_img():
    """嘴张开：嘴角移到 x 232，口子往右张到 y 18–152；口子里是亮得发白的海，上下唇翻开（朝光的唇沿亮、外沿描线）。"""
    out = np.array(outside_img(True))
    a = np.zeros((H, W, 4), np.uint8)
    for x in range(SPIT_C[0], W):
        t_, b_ = spit_top(x), spit_bot(x)
        for y in range(max(0, int(t_) - 10), min(H, int(b_) + 11)):
            if t_ <= y <= b_:
                a[y, x] = out[y, x]
            elif t_ - 10 <= y < t_:                                # 上唇（往上翻）：越靠口子越亮
                k = (y - (t_ - 10)) / 10.0
                lvl = int(np.clip(round(2 + k * 5 + (hash01(x, y, 41) - 0.5)), 0, len(GUM) - 1))
                a[y, x, :3] = GUM[lvl]
                a[y, x, 3] = 255
            elif b_ < y <= b_ + 10:                                # 下唇
                k = 1 - (y - b_) / 10.0
                lvl = int(np.clip(round(2 + k * 5 + (hash01(x, y, 42) - 0.5)), 0, len(GUM) - 1))
                a[y, x, :3] = GUM[lvl]
                a[y, x, 3] = 255
        y_top = max(0, int(t_) - 10)
        a[y_top, x, :3] = INK
        a[y_top, x, 3] = 255
        y_bot = min(H - 1, int(b_) + 10)
        a[y_bot, x, :3] = INK
        a[y_bot, x, 3] = 255
    return Image.fromarray(a, 'RGBA')


@lru_cache(maxsize=1)
def spit_glow_img():
    """张嘴那一下照进来的大片亮光：从口子往左一圈圈淡下去的光晕（半透明，分档）。
    （硬边的光束多边形叠在暗红上会变成一块块灰板，所以只用一圈圈的椭圆光晕。）"""
    im = A._new(W, H)
    A._glow(im, 336, 100, 230, 130, (255, 240, 232), 96, rings=7)
    A._glow(im, 318, 100, 90, 70, (246, 252, 255), 80, rings=4)
    return im


# ============================================================ 组装
def _strip(name, fn, region, key=None):
    d = dict(t='strip', name=name, box=P.auto_box(fn, N_ANIM, FPS_ANIM, region), n=N_ANIM, fps=FPS_ANIM, fn=fn,
             k=1.0)
    if key:
        d['key'] = key
    return d


@lru_cache(maxsize=1)
def specs():
    j0, j1 = jaw_imgs()
    S = [dict(t='static', name='wall', img=wall_img()),
         dict(t='static', name='lower', img=lower_img()),
         dict(t='pick', name='jaw', key='bite', values=[0, 1], imgs=[j0, j1], k=1.0),
         _strip('uvula', uvula_frame, UVULA_REGION),
         dict(t='static', name='spit_open', img=spit_open_img(), key='spit'),
         dict(t='static', name='tongue', img=tongue_img()),
         _strip('flow', flow_frame, FLOW_REGION),
         _strip('rays', rays_frame, RAYS_REGION),
         _strip('drool0', drool_frame, DROOL_REGIONS[0]),
         _strip('drool1', drool_frame, DROOL_REGIONS[1]),
         _strip('bubbles', bubbles_frame, BUB_REGION),
         dict(t='static', name='bite_dim', img=bite_dim_img(), key='bite'),
         dict(t='static', name='spit_glow', img=spit_glow_img(), key='spit'),
         dict(t='tint', name='spit_tint', color='#fff2ea', alpha=0.1, key='spit')]
    return S


def anchors():
    an = dict(ANCHORS)
    an.update(uvula=[int(round(UV_X)), int(UE[UV_X]) - 3 + UV_LEN],
              lips=[305, int(round((UES[305] + LTS[305]) / 2))],
              throat_box=[0, int(UE[40]), 46, 172])
    return an


# ============================================================ 导出
def export(ex, BJ):
    S = specs()
    layers, fg = P.export_layers(ex, BJ, S)
    st = ex.stage(PW, GROUND, WALK, layers, fg, anchors())
    if ex.check_on:
        _checks(ex, BJ, st, S)
    return st


def _checks(ex, BJ, st, S):
    wall, low, tong = wall_img(), lower_img(), tongue_img()
    j0, j1 = jaw_imgs()
    m0, s0 = P.walk_stats(tong, WALK, 60, W)
    cfg = dict(
        name='海底巨嘴', pw=PW, walk=WALK,
        states=[{}, {'bite': True}, {'spit': True}],
        opaque=[('底图（内壁 + 喉咙 + 唇缝外的海）整张不透明', wall, (0, 0, W, H)),
                ('舌头 x 60–320、y 150–180 整片不透明', tong, (60, 150, W, H)),
                ('bite 那张上颚顶上 12 行整片不透明（下移后顶上不露底）', j1, (0, 0, W, BITE_DY))],
        binary=[('舌头只有 0 / 255 两种透明度', tong), ('下牙床只有 0 / 255', low),
                ('上颚（常态）只有 0 / 255', j0), ('上颚（bite）只有 0 / 255', j1),
                ('张嘴的口子只有 0 / 255', spit_open_img())],
        stand=['throat', 'arrive'],
        inside=['upper', 'lower', 'uvula', 'lips', 'throat_box'],
        notes=['可走带亮度（舌面 x 60–320，y 150–174）：均值 %.0f 标准差 %.1f' % (m0, s0)],
    )
    P.std_checks(ex, BJ, st, S, cfg)
    a0, a1 = np.array(j0), np.array(j1)
    ex.checked('上颚 bite 那张 = 常态整体往下移 %d px（逐像素比）' % BITE_DY,
               int((np.abs(a1[BITE_DY:].astype(int) - a0[:JAW_H - BITE_DY].astype(int)).max(-1) > 0).sum()))
    ex.checked('上颚常态那张最底下 %d 行全透明（下移的余量没被画满）' % BITE_DY, int((a0[JAW_H - BITE_DY:, :, 3] > 0).sum()))
    # 牙槽：每个牙位的凹坑里有够深的暗像素
    L0 = lum(a0[..., :3])
    few = []
    for (tx, gy) in UPPER:
        e0 = int(UE[tx])
        n = int(((L0[e0 - 6:e0 + 2, tx - 4:tx + 5] < 32) & (a0[e0 - 6:e0 + 2, tx - 4:tx + 5, 3] > 0)).sum())
        if n < 10:
            few.append(('上', tx, n))
    al = np.array(low)
    Ll = lum(al[..., :3])
    for (tx, gy) in LOWER:
        t0 = int(LT[tx])
        n = int(((Ll[t0 - 1:t0 + 7, tx - 4:tx + 5] < 32) & (al[t0 - 1:t0 + 7, tx - 4:tx + 5, 3] > 0)).sum())
        if n < 10:
            few.append(('下', tx, n))
    ex.checked('12 个牙位都有牙槽凹坑（暗像素 < 10 的：%s）' % (few or '无'), len(few))
    bad = [tx for (tx, gy) in UPPER if not (1.0 <= UE[tx] - (gy + 1) <= 4.0)]
    ex.checked('上排牙根尖（锚点 y + 1）比牙龈线高 1–4 px（插在牙龈里；不满足的牙位 %s）' % (bad or '无'), len(bad))
    bad = [tx for (tx, gy) in LOWER if not (gy - LT[tx] >= 6.0)]
    ex.checked('下牙床上沿比下排锚点 y 高 ≥ 6 px（下牙的根穿过牙床；不满足的 %s）' % (bad or '无'), len(bad))
    # 背景不画牙：静态层拼起来，牙的框里没有“牙白”（很亮、不太红）的像素
    comp = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for im_ in (wall, low, j0, tong):
        comp.alpha_composite(im_)
    c = np.array(comp)[..., :3].astype(int)
    white = (c.min(-1) > 186) & ((c.max(-1) - c.min(-1)) < 60)
    nw = 0
    for (tx, gy) in UPPER:
        nw += int(white[gy:gy + 28, tx - 10:tx + 11].sum())
    for (tx, gy) in LOWER:
        nw += int(white[gy - 26:gy + 4, tx - 10:tx + 11].sum())
    ex.checked('背景没画牙（12 个牙的框里“牙白”像素）', nw)
    Lc = lum(c)
    ex.checked('喉咙洞中心（x 0–20，y 104–140）是暗的（亮度 > 40 的像素）', int((Lc[104:140, 0:20] > 40).sum()))
    lx, ly = anchors()['lips']
    ex.checked('唇缝里看得见海（唇缝中心 [%d, %d] 偏蓝：B > R）' % (lx, ly), int(not c[ly, lx, 2] > c[ly, lx, 0]))
    ex.checked('喉咙那头的地面（x 0–30，y 158–174）比舌面暗一截（亮度均值 < 舌面的 0.5）',
               int(not Lc[158:175, 0:30].mean() < 0.5 * Lc[152:175, 120:240].mean()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch7', 'after')
    os.makedirs(od, exist_ok=True)
    for nm, s in (('', {}), ('_bite', {'bite': True}), ('_spit', {'spit': True})):
        P.direct(specs(), 0, 0.5, s).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'seabed_mouth_solo%s.png' % nm))
    print('ok')
