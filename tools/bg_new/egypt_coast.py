# -*- coding: utf-8 -*-
r"""egypt_coast —— 第7章章末「被吐到埃及海岸」（地图 coast_ch7）/ 第8章开头「SPW 的直升机、伊奇登场」（地图 coast_ch8）。
2026-10-19 第三轮背景重画（sea 组）新画（改前是 later_stages 的占位）。共用零件在 sea_parts.py。

地图 320 宽（单屏，镜头不动）、ground 160、可走带 y 148–176；侧视平视。埃及的红海岸边，上午（第8章用的是下午，同一张）：
海在左边和后面，海岸线从左前斜着退到右后的海平线；右边是陆地，土路通往远处海边的白色小镇和清真寺，后面是红海山地。
红海在埃及的东边——上午的太阳在左上的海面上（亮面朝左上，影子落在右下）；傍晚（key dusk）太阳落到右边的山后面。

从后往前：
  天空 + 左上的太阳、几朵积云（慢慢飘）
  远山：x 90 往右一长条锯齿状的红海山地（赭红 / 灰紫，罩雾）
  海：海平线 y 96，远处深蓝 → 近岸碧绿（越靠海岸线越浅），浪花横条慢慢漂，太阳下的波光；海平线上一条货船慢慢走
  远处海边的小镇（x 222–316）：一片白色方盒子房子、一座清真寺（圆顶 + 宣礼塔）、几棵小椰枣树
  中景（y 100–146）：机坪后面三只骆驼（一只低头吃草、一只站着甩尾巴、一只卧着嚼东西）、一根风向袋（直升机坪左后角）、
              两只油桶（右后角）、一排电线杆顺着土路往小镇走（越远越矮）、两棵椰枣树
  近景 可走带（y 148–176）：
    x 0–150    沙滩：海岸线在 x 0 退到 y 166（浪一推一退，strip），湿沙一条、干沙上的风纹、贝壳、海草、一截漂流木
               （anchors.shore / arrive / midler 都在这里；米朵拉趴在 midler，剧情摆）
    x 108–140  双语路牌（anchors.sign，蓝底白字：上一行阿拉伯文的笔画、下一行 EGYPT），两根柱子立在可走带后沿
    x 150–246  直升机坪：一块晒白的水泥地，地上一个褪了色的 H 圈（anchors.helipad 是圈心；SPW 直升机剧情摆），
               沙子吹上来盖住边角、几道裂缝、两道轮胎印
    x 250–320  土路（anchors.road = 出口）：压实的土、两道车辙、路边的石头，往右后弯到小镇
剧情摆的东西（背景不画）：米朵拉的背影（anchors.midler）、SPW 直升机（anchors.helipad）；纪念品“金属的牙”是调查点（shore + 30）。

图层（从后往前）：
  sky        static              天空渐变 + 左上的太阳（海平线以上，整片不透明）
  dusk_sky   static  key dusk    傍晚的天：上紫下橙、右边山后面一团落日的光
  clouds     wrap    vx 1.2      积云（640 循环）
  far        static              海面底色（近岸碧绿）+ 远山 + 海平线
  sea0–4     wrap    vx −.3…−1.1 海面浪花（越近越快）
  glint      strip               太阳下的波光（8 帧 @4 fps）
  ship       clouds              海平线上的货船
  gulls      strip               海滩上空绕圈的两只海鸥
  land       static              陆地：远处的小镇 / 中景 / 可走带的沙滩、机坪、土路 + 路牌、电线杆、油桶、风向袋杆、树干（只有 0 / 255）
  waves      strip               海岸线上的浪：水膜一推一退 + 白泡沫（沿岸错相，像斜着打上来的浪）
  palm0–1    strip               两棵椰枣树的树冠
  sock       strip               风向袋（风从海上来，往右飘）
  camels     strip               远处的三只骆驼（低头吃草、甩尾巴、卧着的那只嚼东西）
  dusk_a/b   tint    key dusk    傍晚（先压一层冷紫，再罩暖橙）
  lights     static  key dusk    小镇亮起的灯（窗户、宣礼塔的一圈灯）
锚点（素材总表的定稿值）：arrive [60,164]、shore [30,170]、helipad [200,162]（H 圈心）、sign [124,150]（路牌脚下，路牌本身
  在 x 108–140、y 112–146）、road [290,162]（土路出口）、midler [100,170]（米朵拉趴着的点）、beach [150,168]（伊奇来回跑的中心）；
  额外：walk_x [4,316]、horizon、sign_box（路牌框）、pad_box（水泥地框）、sock（风向袋杆顶）、town（宣礼塔顶）。
key：dusk（傍晚）。
单独运行：python -B tools\bg_new\egypt_coast.py → tools\bg_new\_preview\ch7\after\egypt_coast_solo*.png
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

from engine.core import gradient, hash01, hrange, mix, noise1  # noqa: E402
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
mul_box, mul_mask, poly_mask, cast_shadow, mottle, haze, opaque = (P.mul_box, P.mul_mask, P.poly_mask, P.cast_shadow,
                                                                  P.mottle, P.haze, P.opaque)
SHADOW_MUL, SOFT_MUL = P.SHADOW_MUL, P.SOFT_MUL
N_ANIM, FPS_ANIM = P.N_ANIM, P.FPS_ANIM
fno = P.frame_no

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 320
GROUND = 160
WALK = (148, 176)
HZ = 96                       # 海平线
COAST_END = 236               # 海岸线在这里碰到海平线（再往右全是陆地）
SEA_BOT = 172                 # 海面底色画到这一行（再往下被沙滩盖住）
SUN = (40, 26, 6)
SIGN = (108, 112, 140, 129)   # 路牌板 x0, y0, x1, y1（含）；两根柱子立到 y 146
SIGN_POSTS = (113, 135)
PAD_BACK, PAD_FRONT = (168, 150, 232), (154, 176, 246)    # 水泥地：后沿 (x0, y, x1)、前沿 (x0, y, x1)
HELI = (200, 162, 26, 9)      # H 圈：圈心 x, y、半轴 rx, ry
SOCK_POLE = (152, 146, 112)   # 风向袋杆：x、底 y、顶 y
DRUMS = [(229, 146, (58, 98, 156)), (237, 147, (168, 74, 50))]     # 油桶：左 x、底 y、颜色
POLES = [(253, 147, 56, 9), (256, 127, 33, 6), (259, 115, 19, 4), (261, 108, 11, 2)]   # 电线杆：x、底 y、高、横担宽（沿土路左沿）
PALMS = [(84, 141, 88, 70, 4, 20, 11), (298, 133, 300, 98, 2, 12, 12)]   # (根 x, 根 y, 树冠 x, 树冠 y, 往右弯, 叶长, 种子)
CAMELS = [(176, 109, 0), (190, 107, 1), (205, 105, 2)]       # 骆驼：脚 x、脚 y、样子（0 低头吃草、1 甩尾巴、2 卧着）
TOWN_X = (222, 316)
MOSQUE = (248, 103)           # 清真寺：左 x、底 y
MINARET = (262, 104, 26)      # 宣礼塔：x、底 y、高

ANCHORS = dict(
    arrive=[60, 164],          # 被吐上岸的地方
    shore=[30, 170],           # 海边（纪念品“金属的牙”在 shore + 30）
    helipad=[200, 162],        # H 圈心（SPW 直升机降落的点）
    sign=[124, 150],           # 路牌脚下（调查点在 y + 10）
    road=[290, 162],           # 土路出口（去小镇）
    midler=[100, 170],         # 米朵拉趴着的点（剧情摆背影）
    beach=[150, 168],          # 伊奇以这里为中心左右 50 px 来回跑（沙滩 → 机坪边上，一片平地）
    walk_x=[4, 316],
)

# ============================================================ 调色
INK = (58, 44, 40)
HAZE = (214, 222, 228)
SKY_STOPS = [(70, 134, 206), (96, 158, 222), (130, 186, 232), (174, 210, 236), (214, 230, 236)]
SEA_FAR = [(92, 146, 196), (62, 128, 186), (44, 126, 178), (36, 140, 176), (40, 164, 178)]     # 海平线 → 近处（按 y）
SHALLOW = [(56, 182, 182), (98, 204, 194), (142, 222, 206)]                                  # 近岸：越靠海岸线越浅
SAND_L = (244, 232, 204)
SAND = (232, 216, 182)
SAND_S = (220, 202, 166)
SAND_D = (200, 180, 144)
WET = (198, 182, 150)
WET_D = (176, 160, 132)
PAD = (214, 206, 188)         # 晒白的水泥
PAD_S = (198, 190, 172)
PAD_L = (226, 220, 204)
PAINT = (242, 236, 210)       # 褪了色的白漆（偏黄）
ROAD = (208, 184, 146)        # 压实的土路（只比沙暗一点：可走带里对比压低）
ROAD_S = (192, 168, 132)
ROAD_L = (220, 198, 160)
WALL = (238, 234, 224)        # 小镇的白墙
WALL_S = (204, 200, 196)
WOOD = [(150, 112, 76), (120, 88, 60), (90, 66, 48)]
STEEL = [(196, 200, 204), (150, 156, 164), (104, 110, 120)]
SIGN_BLUE = (40, 92, 160)
SIGN_BLUE_D = (30, 70, 128)


def coast_y(x):
    """海岸线（海和沙滩的分界，世界 y）：左前（x 0 → y 166）斜着退到右后（x 236 碰到海平线）。"""
    if x >= COAST_END:
        return float(HZ)
    u = 1.0 - x / float(COAST_END)
    return HZ + 70.0 * u ** 1.6 + 0.8 * math.sin(x / 9.0) * u


def sea_color(x, y):
    """海面底色：按 y 从海平线的深蓝到近处的碧绿，越靠海岸线越浅（看得见沙底）。"""
    u = max(0.0, min(1.0, (y - HZ) / float(SEA_BOT - HZ))) * (len(SEA_FAR) - 1)
    i = min(len(SEA_FAR) - 2, int(u))
    c = mix(SEA_FAR[i], SEA_FAR[i + 1], u - i)
    dist = coast_y(x) - y
    if dist < 14:
        k = (14 - dist) / 14.0
        j = min(2, int(k * 3))
        c = mix(c, SHALLOW[j], 0.45 + 0.4 * k)
    return c


def road_span(y):
    """土路在第 y 行的左右沿：从小镇（y 104，x 266 一线细）往前变宽，越近越往右弯出画面。"""
    u = max(0.0, (y - 104) / 72.0)
    cx = 266.0 + 30.0 * u ** 1.5
    hw = 2.5 + (y - 104) * 0.42
    return cx - hw, cx + hw


def pad_span(y):
    """水泥地在第 y 行的左右沿（梯形：后窄前宽）。"""
    u = (y - PAD_BACK[1]) / float(PAD_FRONT[1] - PAD_BACK[1])
    return PAD_BACK[0] + (PAD_FRONT[0] - PAD_BACK[0]) * u, PAD_BACK[2] + (PAD_FRONT[2] - PAD_BACK[2]) * u


CY = np.array([coast_y(x) for x in range(W)], np.float32)


# ============================================================ 天空 / 云 / 远景
@lru_cache(maxsize=1)
def sky_img():
    return P.sky_img(HZ + 2, SKY_STOPS, sun=SUN)


@lru_cache(maxsize=1)
def dusk_sky_img():
    """傍晚的天：上面压成蓝紫、往下橙粉；右边山后面一团落日的光（太阳落在西边的山里）。"""
    im = A._new(W, HZ + 2)
    gradient(im, (0, 0, W, HZ + 2), [(70, 66, 132), (128, 92, 150), (214, 120, 120), (250, 168, 112), (255, 206, 142)],
             bands=12)
    A._glow(im, 286, HZ - 30, 110, 46, (255, 196, 120), 120, rings=6)
    return im


@lru_cache(maxsize=1)
def clouds_img():
    return P.clouds_img(640, HZ - 6, 5, 6, 23, HZ - 34)


PEAKS = [  # 红海山地：(峰顶 x, 高, 左半宽, 右半宽, 层 0 = 后排（更远更淡）/ 1 = 前排, 种子)
    (150, 24, 32, 26, 0, 1), (206, 32, 34, 30, 0, 2), (262, 40, 38, 30, 0, 3), (318, 33, 30, 30, 0, 4),
    (118, 11, 26, 20, 1, 5), (178, 19, 26, 22, 1, 6), (236, 24, 26, 26, 1, 7), (292, 21, 28, 24, 1, 8),
    (338, 17, 20, 20, 1, 9), (205, 13, 16, 18, 1, 10), (266, 15, 18, 16, 1, 11), (150, 9, 14, 16, 1, 12)]
MTN_LIT = [(206, 176, 156), (196, 160, 136)]       # 迎光（朝左）的坡：后排 / 前排
MTN_SHD = [(164, 134, 132), (150, 112, 102)]       # 背光的坡
MTN_GUL = [(150, 122, 124), (128, 94, 86)]         # 冲沟


def draw_mountains(a):
    """红海山地：一座座峰（左坡迎着左上的光亮、右坡暗，中间一道弯弯的山脊线），后排先画、更淡；
    坡上几道冲沟（顺坡往下的暗线）、峰尖一点亮边；山脚罩雾。（逐列按坡度上色会出一排竖条，像风琴管，所以按峰画。）"""
    for (cx, hgt, wl, wr, layer, sd) in sorted(PEAKS, key=lambda p: p[4]):
        fog0 = 0.42 if layer == 0 else 0.26
        peak_y = HZ - hgt
        for x in range(max(0, cx - wl), min(W, cx + wr + 1)):
            u = (cx - x) / float(wl) if x < cx else (x - cx) / float(wr)
            # 轮廓：不能是光滑的三角（在埃及会被看成金字塔）——坡上一个肩膀、两档大小的锯齿、越往上越碎
            prof = (1 - u) ** 1.25 + 0.16 * math.exp(-((u - 0.5) / 0.13) ** 2) * (1 if (x < cx) == (sd % 2 == 0) else 0.4)
            jag = (noise1(x / 3.2, sd) * 2.6 + noise1(x / 1.3, sd + 50) * 1.2) * (0.35 + 0.65 * (1 - u))
            top = int(round(HZ - hgt * min(1.0, prof) + jag))
            for y in range(max(0, top), HZ):
                xr = cx + (y - peak_y) * 0.24 + 1.4 * math.sin(y / 4.0 + sd)       # 山脊线
                c = MTN_LIT[layer] if x < xr else MTN_SHD[layer]
                # 冲沟：左坡往左下、右坡往右下的几道斜线
                s = (x - xr) - (y - peak_y) * (-0.9 if x < xr else 0.9)
                if abs((s + sd * 3) % 9.0 - 4.5) < 0.6 and y > peak_y + 4 and hash01(int(s // 9), sd, 2) < 0.7:
                    c = MTN_GUL[layer]
                depth = max(0.0, (y - peak_y) / float(max(1, hgt)))
                a[y, x, :3] = mix(c, HAZE, min(0.85, fog0 + 0.28 * depth ** 1.5))
                a[y, x, 3] = 255
            if top < HZ and x < cx + 3:
                a[max(0, top), x, :3] = mix(lt(MTN_LIT[layer], 0.2), HAZE, fog0)


@lru_cache(maxsize=1)
def far_img():
    """远景：海面底色（海平线 → y 172，碧绿的近岸跟着海岸线走）+ 红海山地（亮面朝左上，越远越淡）+ 海平线。"""
    im = A._new(W, H)
    a = np.array(im)
    for y in range(HZ, SEA_BOT + 1):
        for x in range(W):
            c = sea_color(x, y)
            a[y, x, :3] = c
            a[y, x, 3] = 255
    draw_mountains(a)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    hl(d, 0, COAST_END + 4, HZ, (222, 236, 240))                   # 海平线：一道亮的雾线
    hl(d, 0, COAST_END + 4, HZ + 1, (150, 192, 216))
    for i in range(40):                                            # 静态的长涌（很淡的深色长条）
        y = HZ + 3 + int(hash01(i, 21) ** 1.2 * (SEA_BOT - HZ - 6))
        x = int(hrange(-20, W, i, 22))
        L = int(hrange(10, 30, i, 23) * (0.6 + (y - HZ) / float(SEA_BOT - HZ)))
        for xx in range(max(0, x), min(W - 1, x + L)):
            if y < CY[xx] - 2:
                px(d, xx, y, dk(sea_color(xx, y), 0.94))
    return im


SEA_BANDS = [(97, 104, -0.3), (104, 113, -0.45), (113, 125, -0.65), (125, 140, -0.85), (140, 162, -1.1)]


def _sea_at(y):
    return sea_color(0, min(y, 150))


@lru_cache(maxsize=8)
def sea_band_img(i):
    y0, y1, vx = SEA_BANDS[i]
    return P.sea_band_img(640, y0, y1, HZ, SEA_BOT, _sea_at, 700 + i, density=0.9 if i < 3 else 0.75)


@lru_cache(maxsize=N_ANIM)
def _glint(f):
    """太阳下的波光（太阳 x 40）：一柱闪点，2 s 一周；落在沙滩上的不画（只在海面上）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for i in range(56):
        gy = HZ + 2 + int(hash01(i, 90) ** 1.3 * 52)
        spread = 3 + (gy - HZ) * 0.7
        gx = int(round(SUN[0] + hrange(-spread, spread, i, 91)))
        if not (0 <= gx < W) or gy >= CY[gx] - 2:
            continue
        ph = (f / float(N_ANIM) + hash01(i, 92)) % 1.0
        if ph < 0.38:
            px(d, gx, gy, (255, 255, 244) if ph < 0.15 else (214, 240, 248))
            if ph < 0.12 and gy > HZ + 14 and gx + 1 < W and gy < CY[gx + 1] - 2 and gx > 0:
                px(d, gx - 1, gy, (196, 232, 244))
                px(d, gx + 1, gy, (196, 232, 244))
    return _mask_occ(im)


def glint_frame(t):
    return _glint(fno(t))


@lru_cache(maxsize=1)
def ship_img():
    """海平线上的一条小货船（剪影 + 白色的船楼、一缕烟），罩着雾。"""
    g = A._new(26, 9)
    d = ImageDraw.Draw(g)
    for x in range(2, 24):                                         # 船身：船头（左）微微翘
        top = 5 if x > 4 else 6 - (4 - x) // 2
        vl(d, x, top, 7, (70, 74, 86))
    hl(d, 3, 23, 8, (110, 120, 134))
    rect(d, 16, 2, 21, 4, (236, 236, 232))                         # 船楼
    hl(d, 16, 21, 2, (250, 250, 248))
    px(d, 17, 3, (120, 130, 140))
    px(d, 19, 3, (120, 130, 140))
    vl(d, 19, 0, 1, (90, 90, 96))                                  # 烟囱
    rect(d, 6, 3, 9, 4, (176, 88, 62))                             # 几只集装箱
    rect(d, 10, 3, 13, 4, (78, 126, 150))
    px(d, 22, 0, (200, 204, 208))
    px(d, 24, 0, (214, 218, 222))
    return haze(g, 0.3, HAZE)


def ship_items():
    g = ship_img()
    return [dict(img=g, x0=210.0, y=HZ + 1 - g.height + 1, vx=-0.6, k=0.0)]


GULL_C = (74, 46)


@lru_cache(maxsize=N_ANIM)
def _gulls(f):
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for i in range(2):
        ph = math.tau * (f / float(N_ANIM) + i / 2.0)
        x = round(GULL_C[0] + (30 + 10 * i) * math.cos(ph))
        y = round(GULL_C[1] + (6 + 2 * i) * math.sin(ph))
        P.gull(d, x, y, (f + i * 2) % 4)
    return im


def gulls_frame(t):
    return _gulls(fno(t))


# ============================================================ 陆地（land，只有 0 / 255）
def draw_ground(im):
    """陆地底色：海岸线以下（x ≥ 236 从海平线起）；远处罩雾、近处暖；湿沙一条；可走带里沙滩 / 机坪 / 土路。"""
    a = np.array(im)
    bay = A._bayer(W, H)
    for x in range(W):
        top = int(math.ceil(CY[x]))
        for y in range(top, H):
            fog = max(0.0, min(1.0, (146 - y) / 50.0)) * 0.42
            c = SAND
            if y > 120:
                c = mix(SAND, SAND_L, 0.15)
            a[y, x, :3] = mix(c, HAZE, fog)
            a[y, x, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    mottle(im, (0, 120, W - 1, H - 1), mix(SAND, SAND_L, 0.15), SAND_S, SAND_L, 41, cell=9, lo=0.3, hi=0.72)
    a = np.array(im)
    for x in range(W):                                             # 湿沙：海岸线往下一条（近宽远窄）
        if x >= COAST_END:
            break
        e = CY[x]
        ww = 2.0 + 9.0 * (1 - x / float(COAST_END)) ** 1.2
        for y in range(int(math.ceil(e)), int(e + ww) + 1):
            if y >= H:
                break
            u = (y - e) / ww
            c = mix(WET_D, WET, u)
            if u > 0.75 and bay[y, x] < (u - 0.75) * 4:
                c = mix(WET, SAND, 0.5)
            fog = max(0.0, min(1.0, (146 - y) / 50.0)) * 0.42
            a[y, x, :3] = mix(c, HAZE, fog)
        y = int(math.ceil(e))
        if y < H:
            a[y, x, :3] = mix(mix(WET_D, (150, 196, 204), 0.45), HAZE, max(0.0, min(1.0, (146 - y) / 50.0)) * 0.42)
    # 最前面几行稍微暗一点（框住画面）
    for y in range(170, H):
        a[y, :, :3] = (a[y, :, :3].astype(np.float32) * (1.0 - 0.01 * (y - 169))).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))


def draw_far_plain(im):
    """远处的平地：几道很矮的沙梁（亮边）、一点点灌木；小镇脚下一道浅色的沙。"""
    d = ImageDraw.Draw(im)
    for (x0, x1, y, sd) in ((150, 214, 112, 1), (236, 320, 110, 2), (200, 300, 118, 3), (120, 190, 126, 4)):
        for x in range(x0, x1):
            u = (x - x0) / float(x1 - x0)
            yy = int(round(y - 2.0 * math.sin(math.pi * u) + 0.6 * math.sin(x / 5.0 + sd)))
            if yy > CY[x] + 2:
                fog = max(0.0, min(1.0, (146 - yy) / 50.0)) * 0.42
                px(d, x, yy, mix(SAND_L, HAZE, fog))
                px(d, x, yy + 1, mix(SAND_S, HAZE, fog))
    for i in range(26):                                            # 远处的小灌木（几个暗点）
        x = int(hrange(120, 318, i, 41))
        y = int(hrange(104, 140, i, 42))
        if y <= CY[x] + 3 or (TOWN_X[0] - 4 < x < TOWN_X[1] and y < 110):
            continue
        fog = max(0.0, min(1.0, (146 - y) / 50.0)) * 0.5
        c = mix((120, 128, 80), HAZE, fog)
        px(d, x, y, c)
        if y > 118:
            px(d, x + 1, y, mix((96, 106, 66), HAZE, fog))
            px(d, x, y - 1, mix((146, 150, 92), HAZE, fog))


TOWN_WINDOWS = []             # draw_town 画的小窗位置（傍晚亮灯用）


def draw_town(im):
    """远处海边的小镇（x 222–316，脚在 y 102–106）：两排白色方盒子房子（亮面朝左、右边一窄条暗面、黑的小窗）、
    几户顶上有小圆顶、一座清真寺（大圆顶 + 宣礼塔）、几棵小椰枣树；整片罩雾。先画到一张透明图上再罩雾贴回去。"""
    g = A._new(W, H)
    d = ImageDraw.Draw(g)
    del TOWN_WINDOWS[:]

    def window(x, y):
        px(d, x, y, (96, 104, 120))
        TOWN_WINDOWS.append((x, y))

    def house(x0, w, h, base, dome=False, seed=0):
        top = base - h
        rect(d, x0, top, x0 + w - 1, base, WALL)
        vl(d, x0 + w - 1, top, base, WALL_S)
        if w > 4:
            vl(d, x0 + w - 2, top + 1, base, mix(WALL, WALL_S, 0.5))
        hl(d, x0, x0 + w - 1, top, (250, 248, 242))
        for k in range(1 + w // 4):                               # 小窗（一层一排）
            wx = x0 + 1 + k * 3
            if wx < x0 + w - 2 and h > 3:
                window(wx, top + 2)
                if h > 7 and hash01(seed, k, 3) < 0.6:
                    window(wx, top + 5)
        if dome:
            cx = x0 + w // 2
            for (dx, dy) in ((-1, -1), (0, -1), (1, -1), (0, -2)):
                px(d, cx + dx, top + dy, (220, 230, 222))
        elif hash01(seed, 5) < 0.35 and w > 5:                     # 屋顶上的水箱（埃及的平顶房几乎家家有）
            tx_ = x0 + 1 + int(hash01(seed, 6) * (w - 4))
            hl(d, tx_, tx_ + 1, top - 1, (120, 124, 132))
            hl(d, tx_, tx_ + 1, top - 2, (150, 154, 160))
        if hash01(seed, 7) < 0.25 and h > 5:                       # 蓝色的门 / 窗框
            px(d, x0 + 1, base - 1, (70, 120, 170))
            px(d, x0 + 1, base - 2, (70, 120, 170))
    x = TOWN_X[0]
    i = 0
    while x < TOWN_X[1]:                                           # 后排（脚高一点、矮；挨得紧）
        w = int(hrange(5, 9, i, 51))
        h = int(hrange(4, 9, i, 52))
        if not (MOSQUE[0] - 2 < x < MOSQUE[0] + 16):
            house(x, w, h, 101 + int(hrange(0, 2, i, 53)), dome=hash01(i, 54) < 0.15, seed=i)
        x += w + int(hrange(-1, 2, i, 55))
        i += 1
    # 清真寺：方的礼拜殿 + 大圆顶（浅绿灰）+ 宣礼塔（细高、中间一圈阳台、尖顶）
    mx, mb = MOSQUE
    rect(d, mx, mb - 7, mx + 13, mb, WALL)
    vl(d, mx + 13, mb - 7, mb, WALL_S)
    for k in range(3):
        window(mx + 2 + k * 4, mb - 4)
        window(mx + 2 + k * 4, mb - 3)
    for yy in range(mb - 14, mb - 7):                              # 圆顶
        r = 5.5 * math.sqrt(max(0.0, 1 - ((mb - 7 - yy) / 7.0) ** 2))
        for xx in range(int(mx + 7 - r), int(mx + 7 + r) + 1):
            px(d, xx, yy, (200, 222, 208) if xx < mx + 7 else (170, 194, 182))
    vl(d, mx + 7, mb - 17, mb - 15, (210, 190, 120))               # 圆顶上的小尖 + 新月
    px(d, mx + 8, mb - 18, (226, 206, 120))
    tx, tb, th = MINARET
    rect(d, tx, tb - th, tx + 2, tb, WALL)
    vl(d, tx + 2, tb - th, tb, WALL_S)
    hl(d, tx - 1, tx + 3, tb - th + 8, (250, 248, 242))            # 阳台
    hl(d, tx - 1, tx + 3, tb - th + 9, WALL_S)
    hl(d, tx - 1, tx + 3, tb - 14, (250, 248, 242))
    px(d, tx + 1, tb - th - 1, (226, 230, 224))                    # 尖顶
    px(d, tx + 1, tb - th - 2, (210, 190, 120))
    px(d, tx + 1, tb - th + 3, (96, 104, 120))                     # 塔上的小窗
    px(d, tx + 1, tb - th + 13, (96, 104, 120))
    x = TOWN_X[0] + 3
    i = 0
    while x < TOWN_X[1] - 2:                                       # 前排（脚低一点、高一点）
        w = int(hrange(6, 11, i, 61))
        h = int(hrange(5, 10, i, 62))
        if not (MOSQUE[0] - 4 < x < MINARET[0] + 4) and not (262 < x < 272):     # 土路进镇的口子空着
            house(x, w, h, 104 + int(hrange(0, 3, i, 63)), dome=hash01(i, 64) < 0.15, seed=i + 40)
        x += w + int(hrange(0, 4, i, 65))
        i += 1
    for (tx_, ty_) in ((230, 104), (283, 105), (309, 104)):        # 镇子里的小椰枣树
        vl(d, tx_, ty_ - 9, ty_, (150, 128, 96))
        P.palm_crown(d, tx_, ty_ - 9, 5, 0.2, tx_, nuts=False)
    ga = np.array(g)                                               # 后排的窗可能被前排的房子 / 树挡住：只留还看得见的
    TOWN_WINDOWS[:] = [(x, y) for (x, y) in TOWN_WINDOWS if tuple(ga[y, x, :3]) == (96, 104, 120)]
    g = haze(g, 0.26, HAZE)
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    hl(d, TOWN_X[0] - 2, TOWN_X[1], 106, mix(SAND_L, HAZE, 0.4))  # 镇子脚下一道浅色的沙


def draw_road(im):
    """土路：从小镇（y 104，很窄）一路往前变宽、往右偏；压实的土 + 两道车辙 + 路边的石头；远处罩雾。"""
    d = ImageDraw.Draw(im)
    for y in range(104, H):
        l, r = road_span(y)
        fog = max(0.0, min(1.0, (146 - y) / 50.0)) * 0.42
        for x in range(int(math.floor(l)), min(W, int(math.ceil(r)) + 1)):
            if x < 0:
                continue
            u = (x - l) / max(1.0, r - l)
            c = ROAD
            if u < 0.07 or u > 0.93:                               # 路边：踩出来的浅色土
                c = mix(ROAD, SAND, 0.55)
            elif (abs(u - 0.3) < 0.03 or abs(u - 0.7) < 0.03) and hash01(x, y // 3, 70) < 0.75:
                c = ROAD_S                                         # 两道车辙（断断续续）
            elif hash01(x // 2, y, 71) < 0.07:
                c = ROAD_L
            px(d, x, y, mix(c, HAZE, fog))
    for i in range(40):                                            # 路边的石头（近大远小）
        y = int(hrange(110, 177, i, 72) ** 1.0)
        l, r = road_span(y)
        side = l - 1 if i % 2 else r + 1
        x = int(round(side + hrange(-1, 1, i, 73)))
        if not (0 <= x < W - 1):
            continue
        s = 1 if y < 140 else 2
        fog = max(0.0, min(1.0, (146 - y) / 50.0)) * 0.42
        if s == 1:
            px(d, x, y, mix((150, 136, 116), HAZE, fog))
        else:
            hl(d, x, x + 1, y, mix((176, 160, 136), HAZE, fog))
            hl(d, x, x + 1, y + 1, mix((128, 114, 96), HAZE, fog))
            px(d, x, y - 1, mix((196, 182, 158), HAZE, fog))


@lru_cache(maxsize=1)
def paint_mask():
    """H 圈的漆（没褪之前）：一圈（两头 2 px、前后 1 px，像地上压扁的圆）+ 一个 H（两竖 2 px 宽、一横）。"""
    hx, hy, rx, ry = HELI
    pm = Image.new('L', (W, H), 0)
    dm = ImageDraw.Draw(pm)
    dm.ellipse((hx - rx, hy - ry, hx + rx, hy + ry), outline=255)
    dm.ellipse((hx - rx + 1, hy - ry, hx + rx - 1, hy + ry), outline=255)
    for sx in (-8, 7):
        dm.rectangle((hx + sx, hy - 5, hx + sx + 1, hy + 5), fill=255)
    dm.line((hx - 6, hy, hx + 6, hy), fill=255)
    return np.array(pm) > 0


def draw_pad(im):
    """直升机坪：一块晒白的水泥地（梯形，后窄前宽）+ 褪了色的 H 圈（漆掉了一块块）+ 裂缝 + 两道轮胎印 + 边角吹上来的沙。"""
    a = np.array(im)
    stain = A._fbm(W, H, 7, seed=83)
    paint = paint_mask()
    for y in range(PAD_BACK[1], PAD_FRONT[1] + 1):
        l, r = pad_span(y)
        for x in range(int(math.ceil(l)), int(math.floor(r)) + 1):
            c = PAD
            if stain[y, x] < 0.36:                                 # 水泥上大块的旧污渍（成片的，不是满地碎点）
                c = PAD_S
            elif stain[y, x] > 0.68:
                c = PAD_L
            if paint[y, x] and hash01(x // 2, y // 2, 82) > 0.14:  # 褪色的漆：掉了几块，但 H 圈还认得出来
                c = PAINT if hash01(x, y, 83) > 0.22 else mix(PAINT, PAD, 0.5)
            # 边上吹上来的沙：只在边沿 3 px 里，一小撮一小撮（按 4 px 一段决定盖不盖）
            e = min(x - l, r - x, (y - PAD_BACK[1]) * 2.0, (PAD_FRONT[1] - y) * 2.0)
            if e < 3 and hash01(x // 4, y // 2, 84) < 0.55 - e * 0.15:
                c = SAND_S if e > 1.5 else SAND
            a[y, x, :3] = c
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    l, r = pad_span(PAD_BACK[1])
    hl(d, int(math.ceil(l)) + 2, int(r) - 2, PAD_BACK[1], mix(PAD_S, SAND_D, 0.5))     # 后沿一道浅浅的边
    for y in range(PAD_BACK[1] + 1, PAD_FRONT[1] + 1):             # 右沿一道浅浅的阴影（水泥地比沙高一点点）
        l, r = pad_span(y)
        px(d, int(math.floor(r)) + 1, y, mix(SAND_S, SAND_D, 0.5))
    for (x0, y0, segs, sd) in ((172, 156, 9, 1), (222, 167, 7, 2), (190, 173, 6, 3)):   # 裂缝
        x, y = x0, y0
        for k in range(segs):
            px(d, x, y, mix(PAD_S, (150, 140, 126), 0.6))
            x += 1 if hash01(sd, k, 84) < 0.7 else 0
            y += 1 if hash01(sd, k, 85) < 0.35 else (-1 if hash01(sd, k, 86) < 0.2 else 0)
    for k in range(3):                                             # 两道轮胎印（车从土路开进来调过头）
        for x in range(214 + k * 14, 226 + k * 14):
            if hash01(x, k, 87) < 0.7:
                px(d, x, 171 - k, mix(PAD_S, (168, 158, 140), 0.5))
                px(d, x + 2, 174 - k, mix(PAD_S, (168, 158, 140), 0.5))


def draw_beach(im):
    """沙滩（x 0–150）：整片风纹、高潮线上的干海草和碎贝壳、贝壳 / 小石子、冲上来的海草、一截漂流木；
    midler / beach / arrive 那几块不撒大东西（米朵拉和伊奇要在上面）。"""
    d = ImageDraw.Draw(im)

    def ok(x, y):
        return 0 <= x < 150 and y > CY[x] + 12 and not (PAD_FRONT[0] - 2 <= x)
    P.ripple_field(d, (0, 150, 152, H - 2), SAND_S, SAND_L, 61, ok=ok, sp0=3, sp1=5)
    P.ripple_field(d, (110, 128, 240, 146), mix(SAND_S, HAZE, 0.2), mix(SAND_L, HAZE, 0.2), 62,
                   ok=lambda x, y: y > CY[x] + 8 and not (SIGN[0] - 3 < x < SIGN[2] + 3) and x < 246,
                   sp0=2, sp1=3, dash=(3, 7))
    for x in range(0, 200):                                        # 高潮线：断断续续的干海草 + 碎贝壳
        y = int(CY[x] + 2.0 + 10.0 * (1 - x / float(COAST_END)) ** 1.2 + (1 if math.sin(x / 11.0) > 0.4 else 0))
        if y >= H - 1:
            continue
        h_ = hash01(x, 91)
        if h_ < 0.3:
            px(d, x, y, (150, 136, 100) if h_ < 0.18 else (122, 116, 82))
        elif h_ < 0.36:
            px(d, x, y, (240, 232, 220))
    keep = [(ANCHORS['midler'][0] - 14, ANCHORS['midler'][0] + 14), (ANCHORS['beach'][0] - 8, ANCHORS['beach'][0] + 8),
            (ANCHORS['shore'][0] + 24, ANCHORS['shore'][0] + 36)]
    for i in range(46):
        x = int(hrange(4, 148, i, 92))
        y = int(hrange(152, H - 2, i, 93))
        if y < CY[x] + 12 or any(a_ <= x <= b_ for (a_, b_) in keep):
            continue
        k = i % 6
        if k < 3:
            P.shell(d, x, y, k, i)
        elif k == 3:
            px(d, x, y, (198, 186, 166))
            px(d, x + 1, y, (170, 158, 140))
        else:
            px(d, x, y, mix(SAND_S, SAND_D, 0.6))
    for (x, y) in ((44, 160), (128, 158), (16, 176)):              # 冲上来的海草
        for k in range(5):
            px(d, x + k, y + (1 if k % 2 else 0), (96, 104, 62) if k % 3 else (124, 104, 66))
        px(d, x + 2, y - 1, (120, 128, 74))
    # 一截漂流木（晒白的，躺在高潮线附近；在可走带后沿，不高过 3 px）
    x0, y0 = 68, 149
    for k in range(16):
        y = y0 + (k // 6)
        px(d, x0 + k, y, (196, 184, 160))
        px(d, x0 + k, y + 1, (150, 136, 112))
        if k % 5 == 2:
            px(d, x0 + k, y - 1, (214, 204, 182))
    px(d, x0 + 16, y0 + 2, (130, 116, 96))
    hl(d, x0 + 2, x0 + 17, y0 + 3, mix(SAND_S, SAND_D, 0.5))       # 影子


def draw_sign(im):
    """双语路牌（蓝底白字白边）：上一行阿拉伯文（像形状的笔画：مصر 的样子）、下一行 EGYPT；两根镀锌管柱子立在可走带后沿。"""
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = SIGN
    for (sx, k) in ((SIGN_POSTS[0], 0), (SIGN_POSTS[1], 1)):       # 柱子（左亮右暗）+ 地上的影子（往右下）
        vl(d, sx, y1 + 1, 146, STEEL[0])
        vl(d, sx + 1, y1 + 1, 146, STEEL[2])
        hl(d, sx + 1, sx + 5, 147, mix(SAND_S, SAND_D, 0.6))
    rect(d, x1 + 1, y0 + 2, x1 + 1, y1 + 1, (150, 136, 112))       # 板子的厚度 / 背面的暗边
    rect(d, x0, y0, x1, y1, (244, 244, 240))
    rect(d, x0 + 1, y0 + 1, x1 - 1, y1 - 1, SIGN_BLUE)
    hl(d, x0 + 1, x1 - 1, y1 - 1, SIGN_BLUE_D)
    hl(d, x0, x1, y1 + 1, (90, 84, 80))
    white = (246, 246, 242)
    ARABIC = ['..........1..........',                             # 阿拉伯文：右边 م 的小圈、中间 ص 的长圈、左边 ر 往下勾
              '.......11111....11...',
              '.1....1.....1..1..1..',
              '.1...111111111111111.',
              '.1...................',
              '1....................']
    ax, ay = x0 + 6, y0 + 2
    for r_, row in enumerate(ARABIC):
        for c_, ch in enumerate(row):
            if ch == '1':
                px(d, ax + c_, ay + r_, white)
    GLYPH = {'E': ('111', '100', '110', '100', '111'), 'G': ('011', '100', '101', '101', '011'),
             'Y': ('101', '101', '010', '010', '010'), 'P': ('110', '101', '110', '100', '100'),
             'T': ('111', '010', '010', '010', '010')}
    gx, gy = x0 + 7, y0 + 10
    for ch in 'EGYPT':
        for r_, row in enumerate(GLYPH[ch]):
            for c_, v in enumerate(row):
                if v == '1':
                    px(d, gx + c_, gy + r_, white)
        gx += 4
    for (bx, by) in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):   # 螺丝
        px(d, bx, by, (150, 170, 196))
    for k in range(5):                                             # 晒褪的一角 + 一点锈
        px(d, x1 - 1 - k // 2, y0 + 1 + k, mix(SIGN_BLUE, (190, 200, 210), 0.35))
    px(d, x0 + 1, y1 - 2, (150, 104, 70))


def draw_poles(im):
    """电线杆：沿土路左边一根根往小镇走（越远越矮、越淡）；横担 + 白瓷瓶；电线微微下垂，最近那根的线往右前方出画。"""
    d = ImageDraw.Draw(im)
    tops = []
    for i, (x, b, h, cw) in enumerate(POLES):
        fog = 0.1 + 0.16 * i
        top = b - h
        vl(d, x, top, b, mix(WOOD[0], HAZE, fog))
        if h > 20:
            vl(d, x + 1, top, b, mix(WOOD[2], HAZE, fog))
        hl(d, x - cw // 2, x + cw // 2 + (1 if h > 20 else 0), top + 2, mix(WOOD[1], HAZE, fog))
        for s in (-1, 1):
            px(d, x + s * (cw // 2), top + 1, mix((236, 236, 232), HAZE, fog))
        if h > 20:                                                 # 近处那根：脚下的影子、杆上的牌子
            hl(d, x + 2, x + 9, b + 1, mix(SAND_S, SAND_D, 0.55))
            px(d, x, top + 18, (214, 70, 54))
            px(d, x + 1, top + 18, (176, 56, 44))
        tops.append((x, top + 1, cw))
    for (xa, ya, ca), (xb, yb, cb) in zip(tops, tops[1:]):          # 杆与杆之间一根线（远处的线细到看不见，只牵一根）
        P.wire(d, xa + ca // 2, ya, xb + cb // 2, yb, 1.2 if ca > 4 else 0.6, (104, 98, 96))
    x, y, c_ = tops[0]
    P.wire(d, x + c_ // 2, y, W + 4, y - 6, 2.4, (92, 86, 86))     # 最近那根往右前方出画


def draw_drums(im):
    """两只油桶（机坪右后角，SPW 加油用的）：圆柱（左亮右暗）、两道箍、顶上一圈亮边、锈斑；脚下的影子往右下。"""
    d = ImageDraw.Draw(im)
    for (x, b, col) in DRUMS:
        top = b - 9
        for k in range(7):
            c = lt(col, 0.25) if k == 1 else (col if k < 4 else dk(col, 0.78 if k < 6 else 0.62))
            vl(d, x + k, top, b, c)
        hl(d, x, x + 6, top, lt(col, 0.4))
        hl(d, x + 1, x + 5, top - 1, dk(col, 0.7))
        for yy in (top + 3, top + 6):
            hl(d, x, x + 6, yy, dk(col, 0.7))
        px(d, x + 2, top + 4, (150, 92, 60))
        px(d, x + 5, top + 7, (150, 92, 60))
        hl(d, x + 3, x + 10, b + 1, mix(SAND_S, SAND_D, 0.7))
        hl(d, x + 6, x + 9, b, mix(SAND_S, SAND_D, 0.5))


def draw_sock_pole(im):
    """风向袋的杆：细的钢管（红白相间），顶上一个圈；袋子本身在 strip sock 里飘。"""
    d = ImageDraw.Draw(im)
    x, b, top = SOCK_POLE
    for y in range(top, b + 1):
        band = ((y - top) // 4) % 2
        vl(d, x, y, y, (214, 82, 64) if band == 0 else (236, 234, 228))
        px(d, x + 1, y, (150, 60, 48) if band == 0 else (180, 178, 172))
    hl(d, x - 1, x + 2, top - 1, (90, 90, 96))
    hl(d, x + 1, x + 6, b + 1, mix(SAND_S, SAND_D, 0.55))
    for (dx, dy) in ((-3, 0), (3, 0)):                             # 杆脚的三根拉线桩
        px(d, x + dx, b, (120, 110, 96))


def draw_palm_trunks(im):
    d = ImageDraw.Draw(im)
    for (rx, ry, cx, cy, bend, L, sd) in PALMS:
        w0, w1 = (4, 3) if L > 15 else (3, 2)
        P.palm_trunk(d, rx, ry, cx, cy + 2, bend, w0=w0, w1=w1)
        hl(d, rx + 2, rx + 9, ry + 1, mix(SAND_S, SAND_D, 0.5))    # 影子
        if L > 15:
            P.bush(d, rx - 4, ry + 1, 6, 3, 970 + sd, pal=P.DRY_BUSH)


def draw_mid_bushes(im):
    """中景几丛干灌木 / 骆驼刺（机坪后面、土路两边）。"""
    d = ImageDraw.Draw(im)
    for (x, y, rx, ry, sd) in ((140, 140, 5, 3, 1), (208, 132, 4, 2, 2), (246, 128, 4, 2, 3), (312, 140, 6, 3, 4),
                               (176, 124, 3, 2, 5)):
        fog = max(0.0, min(1.0, (146 - y) / 50.0)) * 0.42
        P.bush(d, x, y, rx, ry, 990 + sd, pal=tuple(mix(c, HAZE, fog) for c in P.DRY_BUSH))


@lru_cache(maxsize=1)
def _land():
    """(陆地图, 立着的东西的遮罩)：先画地面，再画立在地上的东西（树干、油桶、杆子、路牌）；
    两次的差 = 立着的东西——海岸线上的浪、海面波光不能画到它们前面（路牌就立在海岸线上）。"""
    im = A._new(W, H)
    draw_ground(im)
    draw_far_plain(im)
    draw_town(im)
    draw_road(im)
    draw_mid_bushes(im)
    draw_pad(im)
    draw_beach(im)
    base = np.array(im)[..., :3].copy()
    draw_palm_trunks(im)
    draw_drums(im)
    draw_sock_pole(im)
    draw_poles(im)
    draw_sign(im)
    occ = (np.array(im)[..., :3] != base).any(-1)
    im = A._grade(im, sat=0.98, val=1.0)
    return opaque(im), occ


def land_img():
    return _land()[0]


def occluder():
    return _land()[1]


def _mask_occ(im):
    """把立着的东西前面的像素抠掉（浪 / 波光用）。"""
    a = np.array(im)
    a[occluder(), 3] = 0
    return Image.fromarray(a, 'RGBA')


# ============================================================ 动的东西
WAVE_REGION = (0, 88, 236, H)


@lru_cache(maxsize=N_ANIM)
def _waves(f):
    """海岸线上的浪：水膜从海那边推上来又退回去（推上来的距离近大远小，沿岸错相 = 斜着打上来），
    边上一道白泡沫、后面一道碎的；退下去的时候留一道淡淡的泡沫痕。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for x in range(0, COAST_END - 6):
        e0 = CY[x]
        amp = 1.0 + 6.0 * (1 - x / float(COAST_END)) ** 1.5
        ph = math.tau * f / float(N_ANIM) - x * 0.045
        e = e0 + amp * (0.5 + 0.5 * math.sin(ph))
        ei = int(round(e))
        top = int(math.floor(e0)) - 1
        for y in range(top, ei):
            if y < 0 or y >= H:
                continue
            u = (y - top) / max(1.0, ei - top)
            if (x + y) % 2 == 0 or u < 0.5:
                px(d, x, y, mix((120, 206, 200), (176, 230, 220), u))
        if 0 <= ei < H and hash01(x, f, 3) > 0.08:
            px(d, x, ei, (250, 252, 250))
        if 0 <= ei - 2 < H and (x + f) % 3 == 0 and hash01(x, f, 4) > 0.3:
            px(d, x, ei - 2, (232, 246, 244))
        if math.cos(ph) < -0.2 and hash01(x // 2, 5) < 0.55:       # 退的时候留下的泡沫痕
            yy = int(round(e0 + amp + 0.5))
            if yy < H:
                px(d, x, yy, (232, 238, 232))
    return _mask_occ(im)


def waves_frame(t):
    return _waves(fno(t))


def palm_frame(i):
    @lru_cache(maxsize=N_ANIM)
    def _f(f):
        im = A._new(W, H)
        d = ImageDraw.Draw(im)
        rx, ry, cx, cy, bend, L, sd = PALMS[i]
        sway = 0.85 * math.sin(math.tau * f / float(N_ANIM) + sd * 0.9)
        pal = None
        if L < 15:                                                 # 远一点的那棵罩一点雾
            pal = tuple(mix(c, HAZE, 0.18) for c in P.PALM_PAL['leaf'])
        P.palm_crown(d, cx, cy, L, sway, sd, pal=pal)
        return im

    def fn(t):
        return _f(fno(t))
    return fn


PALM_FNS = [palm_frame(i) for i in range(len(PALMS))]
SOCK_REGION = (SOCK_POLE[0] - 2, SOCK_POLE[2] - 6, SOCK_POLE[0] + 20, SOCK_POLE[2] + 12)


@lru_cache(maxsize=N_ANIM)
def _sock(f):
    """风向袋：一头粗一头细的布筒，橙白相间三节，风从海上（左边）来、往右飘；沿袋身往后传的波 + 尾巴一甩一甩。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    x0, b, top = SOCK_POLE
    L = 13
    for c in range(L):
        u = c / float(L - 1)
        ph = math.tau * f / float(N_ANIM) - c * 0.55
        droop = 1.2 * u + 0.8 * u * math.sin(ph)
        hh = 4.0 - 2.4 * u
        y0 = top + droop - hh / 2.0 + 1
        seg = int(u * 2.999)
        col = (236, 112, 46) if seg != 1 else (244, 240, 230)
        for r in range(int(round(hh)) + 1):
            cc = col if r < hh - 0.5 else dk(col, 0.78)
            if r == 0:
                cc = lt(col, 0.25)
            if math.cos(ph) < -0.5 and r > 0:
                cc = dk(cc, 0.88)
            px(d, x0 + 2 + c, int(round(y0 + r)), cc)
    return im


def sock_frame(t):
    return _sock(fno(t))


CAMEL_REGION = (160, 104, 236, 136)
CAMEL_PAL = {'h': (216, 182, 134), 'm': (186, 148, 104), 'd': (138, 104, 72), 'e': (84, 64, 50)}
# 单峰骆驼（朝左，15×13，脚在最底一行）：h 迎光（左上）、m 中间、d 背光 / 腿、e 眼睛和嘴
CAMEL_SPR = {
    'stand': ['.hm............',
              'hmmd...........',
              '.emd...........',
              '..md.....hh....',
              '..md....hmmh...',
              '...md..hmmmmh..',
              '...mmhmmmmmmmd.',
              '....mmmmmmmmmdd',
              '....dmmmmmmmmd.',
              '....d.d...d.d..',
              '....d.d...d.d..',
              '....d.d...d.d..',
              '....d.d...d.d..'],
    'graze': ['...............',
              '...............',
              '...............',
              '.........hh....',
              '........hmmh...',
              '.......hmmmmh..',
              '....mhhmmmmmmd.',
              '...mmmmmmmmmmdd',
              '..md.dmmmmmmmd.',
              '.md..d.d...d.d.',
              'hmd..d.d...d.d.',
              'mme..d.d...d.d.',
              '.d...d.d...d.d.'],
    'kneel': ['...............',
              '...............',
              '...............',
              '...............',
              '.hm............',
              'hmmd...........',
              '.emd.....hh....',
              '..md....hmmh...',
              '...md..hmmmmh..',
              '...mmhmmmmmmmd.',
              '....mmmmmmmmmmd',
              '...ddmmmmmmmmdd',
              '..ddddddddddd..'],
}
CAMELS = [(172, 131, 'graze'), (190, 129, 'stand'), (210, 132, 'kneel')]   # 脚 x（左沿）、脚 y、样子


def _camel(a, x0, yb, kind, f):
    """贴一只骆驼（左上角 = (x0, yb − 12)）；按帧做小动作：吃草的那只头一抬一低、站着的甩尾巴 + 耳朵动、
    卧着的嘴在嚼。全身罩一点雾（中景）。"""
    rows = [list(r) for r in CAMEL_SPR[kind]]
    if kind == 'graze' and f in (2, 3, 4, 5):                       # 抬头嚼两口：头和脖子前段往上挪 1 px
        for c in range(0, 4):
            col = [rows[r][c] for r in range(13)]
            col = col[1:] + ['.']
            for r in range(13):
                rows[r][c] = col[r]
    tail = (7, 14) if f % 4 < 2 else (8, 14)                        # 尾巴甩：第 7 行 / 第 8 行
    rows[7][14] = '.'
    rows[8][14] = '.'
    if kind != 'kneel':
        rows[tail[0]][tail[1]] = 'd'
    else:
        rows[10 + (f % 4 < 2)][14] = 'd'
    if kind == 'stand' and f in (1, 5):                             # 耳朵动一下
        rows[0][1], rows[0][2] = '.', 'h'
    if kind == 'kneel' and f % 2:                                   # 嚼：下巴一开一合
        rows[6][1] = 'm'
    y0 = yb - 12
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != '.':
                a[y0 + r, x0 + c, :3] = mix(CAMEL_PAL[ch], HAZE, 0.14)
                a[y0 + r, x0 + c, 3] = 255
    for k in range(3, 14):                                          # 脚下一道淡影子（往右下）
        if a[yb + 1, x0 + k + 1, 3] == 0:
            a[yb + 1, x0 + k + 1] = mix(SAND_S, SAND_D, 0.45) + (255,)


@lru_cache(maxsize=N_ANIM)
def _camels(f):
    a = np.zeros((H, W, 4), np.uint8)
    for i, (x, y, kind) in enumerate(CAMELS):
        _camel(a, x, y, kind, (f + 3 * i) % N_ANIM)
    return Image.fromarray(a, 'RGBA')


def camels_frame(t):
    return _camels(fno(t))


@lru_cache(maxsize=1)
def lights_img():
    """傍晚小镇亮起来的灯：一部分窗户变暖黄、宣礼塔阳台一圈小灯、清真寺圆顶下一点光。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    land_img()                                                     # 先画一遍陆地，TOWN_WINDOWS 才有值
    occ = occluder().copy()
    for fn in PALM_FNS:                                            # 树冠（strip，会晃）挡住的地方也不画灯
        for i in range(N_ANIM):
            occ |= np.array(fn(i / FPS_ANIM))[..., 3] > 0
    for (x, y) in TOWN_WINDOWS:
        if hash01(x, y, 97) < 0.6 and not occ[y, x]:               # 六成的窗亮灯；被电线杆 / 树挡住的不画
            px(d, x, y, (255, 214, 120))
    tx, tb, th = MINARET
    for dx in (-1, 1, 3):                                          # 宣礼塔阳台的一圈小灯
        if not occ[tb - th + 7, tx + dx]:
            px(d, tx + dx, tb - th + 7, (255, 230, 150))
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
    S = [dict(t='static', name='sky', img=sky_img()),
         dict(t='static', name='dusk_sky', img=dusk_sky_img(), key='dusk'),
         dict(t='wrap', name='clouds', img=clouds_img(), period=640, k=0.0, vx=1.2),
         dict(t='static', name='far', img=far_img())]
    for i, (y0, y1, vx) in enumerate(SEA_BANDS):
        S.append(dict(t='wrap', name='sea%d' % i, img=sea_band_img(i), period=640, k=0.0, vx=vx, y=y0))
    S += [_strip('glint', glint_frame, (0, HZ, 100, 160)),
          dict(t='clouds', name='ship', span=420, items=ship_items()),
          _strip('gulls', gulls_frame, (30, 30, 120, 60)),
          dict(t='static', name='land', img=land_img()),
          _strip('waves', waves_frame, WAVE_REGION)]
    for i, (rx, ry, cx, cy, bend, L, sd) in enumerate(PALMS):
        reg = (cx - L - 10, cy - L - 6, cx + L + 12, cy + L + 10)
        S.append(_strip('palm%d' % i, PALM_FNS[i], reg))
    S += [_strip('sock', sock_frame, SOCK_REGION),
          _strip('camels', camels_frame, CAMEL_REGION),
          dict(t='tint', name='dusk_a', color='#2c2a64', alpha=0.18, key='dusk'),
          dict(t='tint', name='dusk_b', color='#ff8a3c', alpha=0.2, key='dusk'),
          dict(t='static', name='lights', img=lights_img(), key='dusk')]
    return S


def anchors():
    an = dict(ANCHORS)
    tx, tb, th = MINARET
    an.update(horizon=HZ, sign_box=[SIGN[0], SIGN[1], SIGN[2], 146],
              pad_box=[PAD_FRONT[0], PAD_BACK[1], PAD_FRONT[2], PAD_FRONT[1]],
              sock=[SOCK_POLE[0], SOCK_POLE[2]], town=[tx + 1, tb - th - 2])
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
    land = land_img()
    m0, s0 = P.walk_stats(land, WALK, 40, W)          # x < 40 的可走带后沿是海（在远景层），只量陆地
    cfg = dict(
        name='埃及海岸', pw=PW, walk=WALK,
        states=[{}, {'dusk': True}],
        opaque=[('天空底图整张不透明', sky_img(), (0, 0, W, HZ + 2)),
                ('傍晚的天整张不透明', dusk_sky_img(), (0, 0, W, HZ + 2)),
                ('远景 海面（海平线 → y 172）整片不透明', far_img(), (0, HZ, W, SEA_BOT + 1)),
                ('海面一直铺到海岸线下面（x 0–40 的海 + 陆地之间没有缝）', far_img(), (0, HZ, 40, int(math.ceil(coast_y(0))) + 2)),
                ('陆地 可走带（x 40–320，y 148–176）+ 前沿 整片不透明', land, (40, WALK[0], W, H)),
                ('陆地 海岸线以下（x 0–40）整片不透明（x < 40 的可走带后沿是海，由远景层盖住）', land,
                 (0, int(math.ceil(coast_y(0))) + 1, 40, H))],
        binary=[('陆地层只有 0 / 255 两种透明度', land)],
        stand=['arrive', 'shore', 'helipad', 'road', 'midler', 'beach'],
        inside=['sign', 'sign_box', 'pad_box', 'sock', 'town'],
        notes=['可走带亮度（陆地 x 40–320，y 148–176）：均值 %.0f 标准差 %.1f' % (m0, s0)],
    )
    P.std_checks(ex, BJ, st, S, cfg)
    a = np.array(land)[..., :3].astype(np.float32)
    L = P._lum(a)
    hx, hy, rx, ry = HELI
    # H 圈：圈心那一片（H 的横杠）比水泥地亮一点、但对比压低（褪了色）
    paint = int(((np.abs(a - np.array(PAINT, np.float32)).max(-1) < 34) & paint_mask()).sum())
    ex.checked('H 圈画了（圈和 H 上褪色白漆的像素 ≥ 80：%d）' % paint, int(paint < 80))
    ex.checked('H 圈是褪色的（漆和水泥地的亮度差 < 30）',
               int(not abs(P._lum(np.array([PAINT], np.float32))[0] - P._lum(np.array([PAD], np.float32))[0]) < 30))
    # 剧情摆东西的地方是空的平地：直升机（helipad ±24、y 150–176）、米朵拉（midler ±14）、伊奇跑的那一片（beach ±50 的地面）
    for (lab, box, base, tol) in (('直升机坪 H 圈一带（x 176–224，y 150–176）没有高出来的东西（离水泥 / 漆色太远的像素）',
                                   (176, 150, 224, 177), PAD, 46),
                                  ('米朵拉趴的那片沙（x 86–114，y 164–176）只有平的沙', (86, 164, 114, 177), SAND, 40)):
        x0, y0, x1, y1 = box
        sub = a[y0:y1, x0:x1]
        ex.checked(lab, int((np.abs(sub - np.array(base, np.float32)).max(-1) > tol).sum()))
    # 路牌：板子在 sign 锚点正上方、整块在 y 50 以下（对白框盖不住）、柱子脚不进可走带
    sx = (SIGN[0] + SIGN[2]) / 2.0
    ex.checked('路牌板居中在 sign.x（%d）上、在 y 50 以下、柱脚在可走带后沿（≤ 147）' % ANCHORS['sign'][0],
               int(abs(sx - ANCHORS['sign'][0]) > 1) + int(SIGN[1] < 50) + int(146 > WALK[0] - 1))
    # 海岸线：shore 在海边（离海岸线 ≤ 20 px）、arrive / midler / beach 在干沙上（离海岸线 ≥ 10 px）
    far = [k for k in ('arrive', 'midler', 'beach') if ANCHORS[k][1] - coast_y(ANCHORS[k][0]) < 10]
    ex.checked('shore 离海岸线 ≤ 20 px（%.0f），arrive / midler / beach 在干沙上（太近的：%s）'
               % (ANCHORS['shore'][1] - coast_y(ANCHORS['shore'][0]), far or '无'),
               int(ANCHORS['shore'][1] - coast_y(ANCHORS['shore'][0]) > 20) + len(far))
    # 土路出口 road 在路面上
    l, r = road_span(ANCHORS['road'][1])
    ex.checked('road 锚点在土路路面上（x %.0f–%.0f）' % (l, r), int(not l + 2 <= ANCHORS['road'][0] <= r - 2))
    lum_sign = L[SIGN[1] + 2:SIGN[3] - 1, SIGN[0] + 2:SIGN[2] - 1]
    ex.checked('路牌上有白字（板上亮度 > 200 的像素 ≥ 30）', int((lum_sign > 200).sum() < 30))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch7', 'after')
    os.makedirs(od, exist_ok=True)
    for nm, s in (('', {}), ('_dusk', {'dusk': True})):
        P.direct(specs(), 0, 0.5, s).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'egypt_coast_solo%s.png' % nm))
    print('ok')
