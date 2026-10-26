# -*- coding: utf-8 -*-
r"""redsea_island —— 第7章「红海」：红海里的小岛（地图 island_ch7），第 14 战「审判」的场地。上午，碧绿的浅海、白沙。
2026-10-18 第二轮背景重画（sea 组）新画（改前是 later_stages 的 320 单屏占位：一片沙 + 一个方块屋）。
共用零件在 sea_parts.py（同组四张共用；它再引用 varanasi_street.py 的小工具和 underwater.py 的石头打光）。

地图 480 宽、ground 160、可走带 y 148–176（白沙，压低了对比）；侧视平视，海在沙滩后面，太阳在左上（上午）。
从左到右（世界坐标）：
  x 0–44      木栈桥小码头：晒白的桥面木板（y 146–165，板缝暗、三排钉子 = 底下的龙骨）、前沿一道横梁 + 四根桩子立在浅水里；
              桥面前面（y 166 往下）是一湾浅水（看得见沙底的波纹，水边一道白泡沫，strip lap 一推一退），
              SPW 的小艇（剧情道具，anchors.boat）就漂在这里、拴在桩子上；后沿两根系船桩 + 救生圈、
              一根挂红色三角旗的竹竿（strip）、一个油桶 + 一只木箱（anchors.pier 在桥面上）
  x 44–120    沙滩：一棵椰子树（x 60）、往右走的一串脚印、几处海草和贝壳
  x 104–172   老人的位置（anchors.oldman / umbrella）：红白条的阳伞（伞杆插在后沿）、伞下一张草席 + 小矮凳、
              左边插在沙里的钓竿（钓线 + 浮标 strip，浮标在浅水里一沉一浮）、饵桶、钓具箱、右边一个小炭炉上坐着铜壶（热气 strip）
  x 176–290   中间的空沙地（x 214–274 只有平的沙，anchors.lamp 神灯放这里）；后沿拉上岸的小渔船、x 196 一棵往左歪的椰子树；
              两处螃蟹洞（anchors.crabs），洞口各有一只小螃蟹横着爬进爬出（strip crabs）
  x 286–360   礁石一堆（藤壶、湿的深色底、绿藻；anchors.rocks 是礁石前面站人的点）；x 334 一棵椰子树；
              x 341–343 两块礁石之间一道竖的礁石缝（anchors.crack；剧情的海螺纪念品在 rocks + 22 = 342，花京院的触须伸进这道缝）
  x 330–480   沙丘慢慢往后抬（沙丘上海葡萄灌木、滨草），x 360–440 一间木板墙 + 椰叶顶的渔家小屋（anchors.hut / hut_door）：
              门半开（屋里黑）、支起来的木板窗（窗口黑）、檐下挂着一串鱼干和一盏马灯、门边一口水缸、靠墙一支船桨；
              屋右边两根竹竿之间晾着渔网（strip 轻轻摆，网顶一排浮子），竿脚下一堆网；最右边一条往岛里去的沙路（anchors.exit）
剧情摆的东西（背景不画）：神灯（anchors.lamp）、SPW 小艇（anchors.boat）、老人（anchors.oldman）。
远景：海平线 y 86、远处一长条阿拉伯海岸（低矮的赭灰色山）、两条三角帆船（clouds 慢慢漂）、天上海鸥。
光：太阳在左上，亮面朝左上，影子落在右下（沙上的影子都很淡）。

图层（从后往前）：
  sky        static          天空渐变 + 左上的太阳（屏幕固定）
  clouds     wrap   k .1  vx 1.0   积云（640 循环）
  far        pano   k .25         远景 360 宽：远处的阿拉伯海岸、小岛、海面底色（海平线 y 86 一直到 y 147）
  sea0–4     wrap   k .3–.8       海面浪花（5 条，越近视差越大；都慢慢往左漂）
  glint      strip  screen        太阳下的波光（8 帧 @4 fps）
  dhows      clouds               海平线上两条三角帆船
  gulls      strip  k .5          海上空绕圈的三只海鸥（8 帧 @4 fps）
  gull_glide clouds               两只滑翔的海鸥
  reef       pano   k .7          浅水里的珊瑚礁 / 白沙底的颜色块、水里的几块小礁石（432 宽）
  buoy       strip  k .7          红白浮标一起一伏（8 帧 @4 fps）
  hill       pano   k .9          小屋后面的小山丘（灌木、岩头）（464 宽）
  shore      pano   k 1           湿沙（干沙后沿到水边那一窄条，x 44–342）
  surf       strip  k 1           拍岸的浪（水膜一推一退 + 泡沫线，8 帧 @4 fps）
  near       pano   k 1           干沙 + 栈桥 + 浅水 + 阳伞 + 树干 + 礁石 + 小屋 + 网竿 + 沙丘（480 宽）
  lap        strip  k 1           栈桥前面的浅水：水纹往右漂、水边的泡沫一推一退、桩子脚下一圈水纹
  palm0–2    strip  k 1           三棵椰子树的树冠（8 帧 @4 fps）
  flag       strip  k 1           栈桥竹竿上的三角旗
  float      strip  k 1           钓线 + 浮标
  steam      strip  k 1           铜壶的热气
  net        strip  k 1           晾着的渔网
  crabs      strip  k 1           两只小螃蟹在洞口横着爬（8 帧 @4 fps）
  burnt      pano   k 1  key burnt  小屋门口被火燎黑：门框 / 门扇焦黑、门两边和门楣的墙板熏黑、门上的檐草烧焦，
                                  门前往左一道烧焦的沙（7-04 火焰从 hut_door 往左喷 30 px）、水缸熏黑半边
  smoke      strip  k 1  key burnt  门洞和檐口冒的烟（往上飘、被海风吹向右）+ 门框 / 焦沙上一闪一闪的炭火星
  dusk_a/b   tint        key dusk   傍晚（先压一层冷紫，再罩暖橙）
锚点（规格要求的 11 个 + 额外）：arrive [56,164]、pier [20,160]、boat [24,170]、oldman [140,160]、umbrella [140,130]（伞面）、
  crabs [[200,172],[300,174]]、lamp [244,166]、rocks [320,158]、hut [400,150]、hut_door [398,160]、exit [470,162]；
  额外：walk_x、horizon、hut_box（小屋框）、window（窗口中心）、rod_tip、float（浮标）、crack（礁石缝的中点 [342, 141]）、
  burnt_box（焦黑的范围）、palms。
key：burnt（小屋门口焦黑 + 冒烟）、dusk（傍晚 tint）。
单独运行：python -B tools\bg_new\redsea_island.py → tools\bg_new\_preview\ch7\after\redsea_island_solo_*.png
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
PW = 480
GROUND = 160
WALK = (148, 176)
HZ = 86                       # 海平线
SEA_BOT = 147                 # 海面底色画到这一行（再往下被湿沙 / 干沙盖住）
CLOUD_K, CLOUD_VX = 0.1, 1.0
FAR_K, REEF_K, HILL_K, GULL_K = 0.25, 0.7, 0.9, 0.5
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 360
REEFW = W + int(math.ceil((PW - W) * REEF_K))    # 432
HILLW = W + int(math.ceil((PW - W) * HILL_K))    # 464
GULLW = W + int(math.ceil((PW - W) * GULL_K))    # 400
PIER_X = 44                   # 栈桥到这里为止（往右是沙滩）
PIER_Y = (146, 165)           # 桥面（后沿 → 前沿亮边）；166–168 前沿横梁，再往下是浅水
PIER_FRONT = 166
PILES = (2, 13, 24, 34)       # 前沿的四根桩（左 x，3 px 宽）
SAND_X0 = 30                  # 干沙最左从这里铺（桥面前面那湾浅水再盖上去）
SHORE_X = (44, 342)           # 有湿沙 / 拍岸浪的一段
DUNE_X = (322, 372)           # 沙丘从这里开始往后抬（干沙后沿 146 → 132）
HUT = (360, 440)
DOOR = (389, 406, 100)        # 门洞 x0, x1, 门顶 y（门底 141）
WIN = (414, 429, 106, 119)
NET_POLES = (450, 474)
CLEAR = (214, 274)            # 神灯那块空沙地（可走带里只有平的沙）
PALMS = [  # (根 x, 根 y, 树冠 x, 树冠 y, 往右弯, 叶长, 种子)
    (60, 146, 78, 56, 6, 22, 1),
    (198, 146, 186, 46, -5, 24, 2),
    (334, 146, 322, 58, -4, 20, 3),
]
ROD_BUTT, ROD_TIP = (124, 146), (101, 97)
FLOAT_XY = (88, 127)
KETTLE = (163, 140)
SEA_BANDS = [(87, 95, 0.3, -0.25), (95, 105, 0.38, -0.4), (105, 117, 0.48, -0.6), (117, 130, 0.6, -0.9),
             (130, 141, 0.76, -1.3)]
GLINT_REGION = (4, HZ + 1, 104, 141)
BUOY_XY = (176, 121)          # 浮标（reef 层坐标）
CRACK_X = 342                 # 礁石缝（= rocks.x + 22：剧情的海螺纪念品 ch7_conch 在这里，花京院的触须伸进去摸）
CRACK_Y = (133, 147)          # 缝从这里裂到礁石脚
# key burnt：7-04 阿布德尔的火从小屋门口（hut_door）往左喷出 30 px → 焦的是门框、门两边的墙、门楣上的檐草和门前往左一道沙
SCORCH_SAND = (378, 154, 30, 6)   # 门前焦沙：中心 x、y，半径 rx、ry（往左拖长）

ANCHORS = dict(
    arrive=[56, 164],          # 栈桥上岸的地方
    pier=[20, 160],            # 栈桥上
    boat=[24, 170],            # SPW 的小艇（剧情道具）停在栈桥前沿
    oldman=[140, 160],         # 老人（剧情 NPC）坐在伞下的小凳上
    umbrella=[140, 130],       # 阳伞伞面（物件；素材总表的定稿值）
    crabs=[[200, 172], [300, 174]],
    lamp=[244, 166],           # 神灯（剧情道具）放的空沙地
    rocks=[320, 158],          # 礁石前面站人的点
    hut=[400, 150],            # 小屋前
    hut_door=[398, 160],       # 门前
    exit=[470, 162],
    walk_x=[6, 474],
)

# ============================================================ 调色
INK = (54, 44, 48)
SKY_STOPS = [(62, 126, 202), (86, 150, 218), (122, 178, 230), (168, 206, 234), (212, 230, 236)]
SEA_STOPS = [(74, 132, 186), (54, 122, 178), (40, 124, 172), (32, 138, 170), (36, 160, 170), (56, 186, 176),
             (100, 210, 190)]
SEA_AT = P.sea_color_fn(SEA_STOPS, HZ, SEA_BOT)
HAZE = (206, 222, 230)
SAND_L = (250, 245, 230)
SAND = (241, 233, 213)
SAND_S = (230, 220, 197)
SAND_D = (212, 198, 170)
SAND_K = (182, 166, 138)
WET = (196, 182, 156)
WET_D = (172, 158, 134)
WOODP = [(208, 192, 160), (180, 160, 128), (150, 128, 100), (114, 94, 72), (80, 66, 54)]   # 晒白的木头 亮 → 深
THATCH = [(226, 200, 138), (200, 170, 110), (166, 136, 86), (128, 102, 64), (90, 72, 48)]
ROPE = (214, 196, 150)
ROPE_D = (166, 146, 104)
RED = (204, 62, 54)
CREAM = (244, 234, 214)


def edge_y(x):
    """干沙的后沿（再往后是湿沙 / 海）：沙滩上微微起伏；DUNE_X 起慢慢抬成沙丘（146 → 132）。"""
    base = 146 + round(1.1 * math.sin(x / 17.0) + 0.7 * math.sin(x / 7.3 + 1.0))
    if x < DUNE_X[0]:
        return int(min(147, base))
    u = min(1.0, (x - DUNE_X[0]) / float(DUNE_X[1] - DUNE_X[0]))
    u = u * u * (3 - 2 * u)
    top = 132 + round(1.6 * math.sin(x / 13.0))
    return int(round(base + (top - base) * u))


SHALLOW = [(84, 186, 184), (110, 204, 196), (138, 218, 206), (160, 228, 214)]   # 浅水：深 → 浅（看得见沙底）


def water_x(y):
    """桥面前面那湾浅水的右边界（y ≥ PIER_FRONT）：沙滩往前慢慢往左伸（近处的沙嘴），水边微微起伏。"""
    return int(round(45 - (y - PIER_FRONT) * 0.62 + 0.8 * math.sin(y * 0.9)))


# ============================================================ 天空 / 云 / 远景
@lru_cache(maxsize=1)
def sky_img():
    return P.sky_img(HZ + 2, SKY_STOPS, sun=(46, 22, 6))


@lru_cache(maxsize=1)
def clouds_img():
    return P.clouds_img(640, HZ - 2, 6, 5, 7, HZ - 5)


@lru_cache(maxsize=1)
def far_img():
    """远景：海面底色（海平线 → y 147，横条，视差无所谓）+ 远处的阿拉伯海岸（一长条低矮的山）+ 左边一座小岛。"""
    im = A._new(FARW, H)
    gradient(im, (0, HZ, FARW, SEA_BOT + 1), SEA_STOPS, bands=14)
    a = np.array(im)
    bay = A._bayer(FARW, H)
    # 远处的阿拉伯海岸：x 118 起一长条，几座平顶的山 + 两座尖一点的；越往右越淡
    xs = np.arange(FARW, dtype=np.float32)
    hgt = np.zeros(FARW, np.float32)
    for (cx, hh, ww) in ((150, 6, 16), (178, 9, 14), (206, 5, 18), (236, 11, 12), (262, 7, 20), (300, 9, 16),
                         (330, 5, 18), (352, 7, 12)):
        hgt += hh * np.exp(-((xs - cx) / ww) ** 2)
    hgt += 2.2 * (xs > 124) * np.clip((xs - 124) / 8.0, 0, 1)
    for x in range(FARW):
        h_ = hgt[x] + 0.8 * math.sin(x * 0.7) * (hgt[x] > 3)
        top = int(round(HZ - h_))
        if top >= HZ:
            continue
        sl = hgt[min(FARW - 1, x + 1)] - hgt[max(0, x - 1)]
        for y in range(top, HZ):
            c = (182, 164, 168)
            if sl > 0.35 or (sl > 0.1 and bay[y, x] < 0.5):
                c = (200, 184, 182)
            elif sl < -0.35 or (sl < -0.1 and bay[y, x] < 0.5):
                c = (160, 146, 160)
            depth = (y - top) / max(1.0, HZ - top)
            if depth > 0.6 and bay[y, x] < (depth - 0.6) * 1.8:
                c = (196, 194, 200)
            a[y, x, :3] = mix(c, HAZE, 0.18 + 0.25 * (x / FARW))
            a[y, x, 3] = 255
        a[top, x, :3] = mix((214, 200, 194), HAZE, 0.2)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    hl(d, 120, FARW - 1, HZ - 1, (222, 214, 196))                   # 海岸脚下一道亮沙
    for (x, w) in ((196, 3), (201, 2), (283, 3)):                   # 海岸上一点点白房子
        hl(d, x, x + w - 1, HZ - 2, (236, 232, 222))
    vl(d, 288, HZ - 5, HZ - 2, (226, 222, 214))                     # 宣礼塔一样的小白点
    # 左边一座小岛（礁石 + 两棵小树的剪影）
    for x in range(26, 52):
        u = (x - 26) / 26.0
        hh = int(round(4 * math.sin(math.pi * u) ** 0.7 + (1 if 34 < x < 40 else 0)))
        if hh > 0:
            vl(d, x, HZ - hh, HZ - 1, mix((150, 150, 132), HAZE, 0.35) if x < 40 else mix((128, 130, 120), HAZE, 0.35))
    for (tx, th) in ((34, 7), (41, 6)):
        P.palm_crown(d, tx, HZ - th, 4, 0.0, tx, pal=tuple(mix(c, HAZE, 0.45) for c in P.PALM_PAL['leaf']), nuts=False)
        vl(d, tx, HZ - th, HZ - 3, mix((120, 110, 90), HAZE, 0.45))
    # 海平线：一道亮的雾线 + 下面一行浅色
    hl(d, 0, FARW - 1, HZ, (218, 234, 238))
    hl(d, 0, FARW - 1, HZ + 1, (164, 200, 220))
    # 静态的长涌（很淡的深色长条）
    for i in range(46):
        y = HZ + 3 + int(hash01(i, 21) ** 1.2 * (SEA_BOT - HZ - 6))
        u = (y - HZ) / (SEA_BOT - HZ)
        x = int(hrange(-20, FARW, i, 22))
        L = int(hrange(10, 36, i, 23) * (0.6 + u))
        hl(d, max(0, x), min(FARW - 1, x + L), y, dk(SEA_AT(y), 0.94))
    return im


@lru_cache(maxsize=8)
def sea_band_img(i):
    y0, y1, k, vx = SEA_BANDS[i]
    return P.sea_band_img(640, y0, y1, HZ, SEA_BOT, SEA_AT, 300 + i, density=1.0 if i < 3 else 0.8)


def glint_frame(t):
    """太阳下的波光（屏幕坐标，太阳 x 46）：点状闪光，2 s 一周。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    for i in range(64):
        gy = HZ + 2 + int(hash01(i, 90) ** 1.3 * 50)
        spread = 3 + (gy - HZ) * 0.7
        gx = int(round(46 + hrange(-spread, spread, i, 91)))
        ph = (f / N_ANIM + hash01(i, 92)) % 1.0
        if ph < 0.38:
            px(d, gx, gy, (255, 255, 244) if ph < 0.15 else (214, 240, 248))
            if ph < 0.12 and gy > HZ + 16:
                px(d, gx - 1, gy, (196, 232, 244))
                px(d, gx + 1, gy, (196, 232, 244))
    return im


DHOWS = [(19, 0.5, 40.0, False), (12, -0.32, 250.0, True)]       # (船长, vx, x0, 双帆)
DHOW_SPAN = 460


def dhow_items():
    out = []
    for i, (L, vx, x0, two) in enumerate(DHOWS):
        g = P.dhow_img(L, sail=(250, 246, 234), haze_col=HAZE, amt=0.14 + 0.16 * i, two=two)
        out.append(dict(img=g, x0=x0, y=HZ + 2 - g.height, vx=vx, k=FAR_K))
    return out


GULL_C = (236, 58)            # 海鸥绕圈的中心（gulls 层坐标，k .5）


def gulls_frame(t):
    im = A._new(GULLW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    for i in range(3):
        ph = math.tau * (f / N_ANIM + i / 3.0)
        x = round(GULL_C[0] + (34 + 8 * i) * math.cos(ph))
        y = round(GULL_C[1] + (7 + 2 * i) * math.sin(ph))
        P.gull(d, x, y, (f + i * 3) % 4)
    return im


def glide_items():
    g = P.gull_img()
    return [dict(img=g, x0=60.0, y=40, vx=-6.0, k=0.3), dict(img=P.gull_img(dark=True), x0=300.0, y=30, vx=-3.6, k=0.25)]


# ============================================================ 浅水的珊瑚礁（k .7）
@lru_cache(maxsize=1)
def reef_img():
    """浅水底：深色的珊瑚礁块 / 白沙底的亮块。噪声横向拉长（斜着看过去，礁块被压扁成一条条横的），
    礁块朝上的边亮一格（珊瑚顶受光），越近（y 大）颜色越实；靠岸一条亮的沙底；几块露出水面的小礁石。"""
    w = REEFW
    im = A._new(w, H)
    a = np.array(im)
    y0, y1 = 110, SEA_BOT + 1
    hh = y1 - y0
    big = A._fbm(w, hh * 3, 13, seed=41)[::3]
    det = A._fbm(w, hh * 2, 4, seed=43)[::2]
    bay = A._bayer(w, H)[y0:y1]
    reef_m = np.zeros((hh, w), bool)
    for r in range(hh):
        u = r / float(hh)
        n = big[r] + (det[r] - 0.5) * 0.22
        thr = 0.6 - 0.05 * u
        reef_m[r] = (n > thr + 0.03) | ((n > thr) & (bay[r] < 0.5))
        if u < 0.25:                                               # 远的礁块：边上抖掉一些
            reef_m[r] &= bay[r] < 0.35 + u * 2.6
    for r in range(hh):
        y = y0 + r
        u = r / float(hh)
        sea = np.array(SEA_AT(y), np.float32)
        reef = sea * np.array((0.64, 0.8, 0.85), np.float32)
        reef_d = sea * np.array((0.52, 0.68, 0.77), np.float32)
        crest = sea + (np.array((176, 230, 214), np.float32) - sea) * 0.3
        sandb = sea + (np.array((236, 248, 230), np.float32) - sea) * (0.16 + 0.34 * u)
        n = big[r] + (det[r] - 0.5) * 0.22
        for x in range(w):
            if reef_m[r, x]:
                top = r == 0 or not reef_m[r - 1, x]
                c = crest if (top and u > 0.2) else (reef_d if (n[x] > 0.72 and det[r, x] > 0.45) else reef)
                a[y, x, :3] = c
                a[y, x, 3] = 255
            elif u > 0.55 and (n[x] < 0.42 or (n[x] < 0.46 and bay[r, x] < 0.5)):
                a[y, x, :3] = sandb
                a[y, x, 3] = 255
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 几块露出水面的小礁石（各自一圈白浪花）
    for (rx, ry, rw, sd) in ((126, 125, 9, 1), (268, 118, 6, 2), (380, 128, 11, 3)):
        r, m = P.rock_img(rw, 6, [(rw / 2, 6, rw / 2, 4.5)], 600 + sd, wet=2)
        paste(im, r, rx - rw // 2, ry - 6)
        d = ImageDraw.Draw(im)
        hl(d, rx - rw // 2 - 2, rx - rw // 2 + rw + 1, ry, (226, 246, 244))
        px(d, rx - rw // 2 - 3, ry, (180, 226, 228))
        px(d, rx + rw // 2 + 2, ry - 1, (238, 250, 250))
    return im


def buoy_frame(t):
    im = A._new(REEFW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    dy = (0, 0, 1, 1, 1, 0, 0, -1)[f]
    x, y = BUOY_XY
    r = 3 + (f % 4)
    hl(d, x - r - 1, x - r + 1, y + 1, (190, 236, 232))           # 一圈圈往外扩的水纹
    hl(d, x + r - 1, x + r + 1, y + 1, (190, 236, 232))
    if f % 4 < 2:
        hl(d, x - 2, x + 2, y + 2, (150, 214, 214))
    P.buoy(d, x, y, dy)
    hl(d, x - 3, x + 3, y + 1, (60, 120, 130))                     # 水下的影
    return im


# ============================================================ 小山丘（k .9）
@lru_cache(maxsize=1)
def hill_img():
    """小屋后面的小山丘：干草坡（左亮右暗）+ 岩头 + 一簇簇灌木；底下被近景的沙丘盖住。"""
    w = HILLW
    hh = H
    # 红海里的小岛是干的：赭黄的砂岩 / 珊瑚石灰岩坡，稀稀拉拉几丛耐旱灌木、坡顶一棵平顶的金合欢
    balls = [(424, 152, 66, 64), (384, 152, 44, 40), (456, 152, 34, 70), (348, 152, 30, 18)]
    m, z = P.blob(w, hh, balls, 71, noise=0.12, cell=7, base=150)
    pal = [(128, 96, 72), (162, 128, 92), (192, 160, 116), (216, 188, 142), (236, 214, 174)]
    rgba, q = P.shade(m, z, pal, 71, bump=0.7, facet=0.2, fcell=8, dither=0.4, seam=0.45, outline=(110, 82, 64),
                      speck=0.02)
    rgba = P.haze(Image.fromarray(rgba, 'RGBA'), 0.12, HAZE)
    im = rgba
    d = ImageDraw.Draw(im)
    # 几道横的岩层（砂岩一层层的，亮线 + 下面暗线）
    for (y, x0, x1) in ((112, 372, 410), (100, 404, 446), (124, 356, 384), (92, 430, 462)):
        for x in range(x0, x1):
            if m[y, x] and m[y + 1, x]:
                px(d, x, y, (226, 202, 160))
                px(d, x, y + 1, (150, 118, 88))
    # 稀稀拉拉的灌木（深橄榄绿，底下一点影）
    for i in range(18):
        x = int(hrange(340, w - 4, i, 81))
        col = m[:, min(w - 1, x)]
        if not col.any():
            continue
        top = int(np.argmax(col))
        y = top + int(hrange(3, 30, i, 82))
        if y > 138 or not m[min(hh - 1, y), x]:
            continue
        s = hrange(0.6, 1.1, i, 83)
        hl(d, x - int(4 * s), x + int(5 * s), y + 1, (140, 108, 80))
        P.bush(d, x, y, 4.5 * s, 3 * s, 900 + i, pal=P.DRY_BUSH if i % 3 == 0 else P.BUSH_PAL)
    # 坡顶一棵平顶的金合欢
    tx, ty = 446, 82
    d.line((tx, ty, tx - 3, ty - 9), fill=C((100, 78, 60)))
    d.line((tx, ty, tx + 4, ty - 8), fill=C((100, 78, 60)))
    vl(d, tx, ty - 2, ty + 2, (100, 78, 60))
    for k in range(3):
        P.canopy(d, tx - 6 + k * 6, ty - 11, 6, 2.6, 960 + k, pal=P.BUSH_PAL)
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    return Image.fromarray(a, 'RGBA')


# ============================================================ 湿沙（k 1）+ 拍岸的浪
@lru_cache(maxsize=1)
def shore_img():
    """干沙后沿到水边的一窄条湿沙（y 139–147）：深一点、带一道道天空的反光；左边栈桥那段没有（桩子直接立在水里）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x0, x1 = SHORE_X
    for x in range(x0, x1):
        e = edge_y(x)
        top = 139 + (1 if math.sin(x / 9.0) > 0.6 else 0)
        for y in range(top, max(e, top) + 1):
            u = (y - top) / max(1, e - top)
            c = mix(WET_D, WET, u)
            if (y == top) or (hash01(x // 3, y, 11) < 0.12):
                c = mix(c, (176, 214, 222), 0.4)                    # 天空的反光
            px(d, x, y, c)
    for i in range(30):                                            # 冲上来的小贝壳 / 海草
        x = int(hrange(x0 + 4, x1 - 4, i, 12))
        y = int(hrange(141, 146, i, 13))
        if i % 3:
            P.shell(d, x, y, i % 3, i)
        else:
            hl(d, x, x + 2, y, (88, 96, 60))
            px(d, x + 1, y - 1, (110, 118, 70))
    return im


SURF_REGION = (SHORE_X[0], 134, SHORE_X[1], 149)


def surf_frame(t):
    """拍岸的浪：水膜从海那边一推一退（边线 = 正弦，沿 x 错相，像斜着打上来的浪），边上一道白泡沫、后面一道碎的；
    退下去的时候在最远处留一道淡淡的泡沫痕。8 帧 = 2 s 一周。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    x0, x1 = SHORE_X
    for x in range(x0, x1):
        ph = math.tau * f / N_ANIM - x * 0.043
        e = 142.4 + 2.3 * math.sin(ph) + 0.6 * math.sin(2 * ph + x * 0.11)
        ei = int(round(e))
        lim = edge_y(x)
        ei = min(ei, lim)
        for y in range(137, ei):
            u = (y - 137) / max(1.0, ei - 137)
            if (x + y) % 2 == 0 or u < 0.35:
                px(d, x, y, mix((150, 220, 214), (200, 238, 230), u))
        if hash01(x, f, 3) > 0.1:
            px(d, x, ei, (248, 252, 250))
        if (x + f) % 3 == 0 and hash01(x, f, 4) > 0.3:
            px(d, x, ei - 2, (234, 248, 246))
        if math.cos(ph) < -0.2 and hash01(x // 2, 5) < 0.6:          # 退潮的时候留下的泡沫痕
            yy = min(lim, int(round(142.4 + 2.3 + 0.6)))
            px(d, x, yy, (226, 236, 230))
        if 137 <= ei - 4 and (x * 7 + f) % 11 == 0:
            px(d, x, ei - 4, (226, 246, 244))
    return im


# ============================================================ 近景
def draw_sand(im):
    """干沙：底色 + 大块明暗 + 风纹 + 贝壳 / 碎珊瑚 / 海草 / 脚印 / 螃蟹洞；前沿暗一点，后沿一道潮湿的深线。"""
    d = ImageDraw.Draw(im)
    for x in range(SAND_X0, PW):                                   # 栈桥前面的沙嘴从 x 30 起（浅水由 draw_pier 再盖上去）
        e = edge_y(x) if x >= PIER_X else PIER_FRONT
        vl(d, x, e, H - 1, SAND)
    mottle(im, (SAND_X0, 128, PW - 1, H - 1), SAND, SAND_S, SAND_L, 31, cell=9, lo=0.3, hi=0.72)
    d = ImageDraw.Draw(im)
    a = np.array(im)
    for y in range(168, H):                                        # 最前面几行稍微暗一点（框住画面）
        k = 1.0 - 0.008 * (y - 167)
        row = a[y, SAND_X0:, :3].astype(np.float32) * k
        a[y, SAND_X0:, :3] = row.astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for x in range(PIER_X, PW):                                    # 后沿：一道潮湿的深线 + 上面一行亮
        e = edge_y(x)
        if x < DUNE_X[0] + 10:
            px(d, x, e, SAND_D)
            px(d, x, e + 1, mix(SAND_S, SAND_D, 0.4))
        else:
            px(d, x, e, mix(SAND_L, SAND, 0.4))

    def ok(x, y):
        return PIER_X + 2 <= x < PW - 1 and y > edge_y(x) + 2
    # 整片风纹（后面密、前面疏），沙丘坡上再一片
    P.ripple_field(d, (PIER_X, 151, PW - 2, H - 2), SAND_S, SAND_L, 51, ok=ok, sp0=3, sp1=5)
    P.ripple_field(d, (DUNE_X[0] + 16, 136, PW - 2, 147), SAND_S, SAND_L, 52, ok=ok, sp0=3, sp1=3, dash=(3, 7))
    # 高潮线：后沿往前两三行一道断断续续的干海草 + 碎贝壳（海滩上最像海滩的一道线）
    for x in range(PIER_X + 6, DUNE_X[0] + 6):
        y = edge_y(x) + 3 + (1 if math.sin(x / 11.0) > 0.4 else 0)
        h_ = hash01(x, 71)
        if h_ < 0.34:
            px(d, x, y, (150, 136, 100) if h_ < 0.2 else (122, 116, 82))
        elif h_ < 0.4:
            px(d, x, y, (236, 226, 214))
        if h_ < 0.08:
            px(d, x, y - 1, (170, 150, 110))
    for i in range(70):                                            # 贝壳 / 碎珊瑚 / 小石子（神灯那块不撒）
        x = int(hrange(PIER_X + 4, PW - 4, i, 61))
        y = int(hrange(149, H - 2, i, 62))
        if CLEAR[0] - 6 < x < CLEAR[1] + 6:
            continue
        k = i % 6
        if k < 3:
            P.shell(d, x, y, k, i)
        elif k == 3:
            px(d, x, y, (198, 186, 166))
            px(d, x + 1, y, (170, 158, 140))
        else:
            px(d, x, y, mix(SAND_S, SAND_D, 0.6))
    for (x, y) in ((92, 150), (176, 149), (284, 150), (128, 172)):    # 冲上来的海草（暗绿 / 褐）
        for k in range(5):
            px(d, x + k, y + (1 if k % 2 else 0), (96, 104, 62) if k % 3 else (124, 104, 66))
        px(d, x + 2, y - 1, (120, 128, 74))
    # 一串脚印：从栈桥上岸往右走（左右脚交替，越往右越淡）
    for i in range(16):
        x = 52 + i * 9
        y = 166 + (2 if i % 2 else -1) + int(2 * math.sin(i * 0.5))
        if x > CLEAR[0] - 12:
            break
        c = mix(SAND_S, SAND_D, 0.55 - i * 0.02)
        hl(d, x, x + 2, y, c)
        px(d, x + 1, y - 1, mix(SAND, SAND_S, 0.6))
        px(d, x + 3, y, mix(SAND_S, SAND_D, 0.3))
    # 螃蟹洞：一个小黑点 + 一圈刨出来的湿沙粒
    for (cx, cy) in ANCHORS['crabs']:
        for (hx, hy) in ((cx - 9, cy - 3), (cx + 7, cy + 1)):
            px(d, hx, hy, (120, 106, 88))
            px(d, hx + 1, hy, (148, 134, 112))
            for k in range(6):
                ang = k * 1.05 + 0.3
                px(d, hx + round(2.6 * math.cos(ang)), hy + round(1.3 * math.sin(ang)), mix(SAND_S, WET, 0.5))
    # 小海星（剧情的海螺纪念品在礁石缝里，这里只是点缀；x 214–274 是神灯那块空沙地，不撒）
    P.shell(d, 288, 176, 3, 1)
    P.shell(d, 362, 168, 3, 2)


def draw_pier(im):
    """木栈桥（x 0–43）+ 桥面前面那湾浅水（y 166 往下、x < water_x(y)）。
    桥面 y 146–165：晒白的竖木板（每块 4–5 px、颜色错开、板缝暗、顺纹的短线、节疤），三排钉子（底下的龙骨，后面密前面疏 =
    桥面是平躺着往远处去的），越往后越暗一点点；165 前沿亮边、166–168 前沿横梁（钉头）。
    下面是浅水：桥下一窄条阴影、四根桩子（水线上一圈藻 + 藤壶，水下一截发绿），再往前是看得见沙底波纹的浅水，
    水边一格湿沙（泡沫的推退在 strip lap）。SPW 的小艇是剧情道具（anchors.boat），这里只画前沿一个系缆桩和垂进水里的缆绳。
    后沿两根系船桩（一根挂救生圈）+ 竹竿 + 油桶 + 木箱，后角一卷缆绳。"""
    d = ImageDraw.Draw(im)
    x1 = PIER_X - 1
    y0, y1 = PIER_Y
    # ---- 浅水：先铺满桥面前面（再画桩子、横梁压在上面）
    for y in range(PIER_FRONT, H):
        wx = water_x(y)
        u = (y - PIER_FRONT) / float(H - 1 - PIER_FRONT)
        for x in range(0, wx):
            c = mix(SHALLOW[1], SHALLOW[3], 0.15 + 0.8 * u)
            if y <= PIER_FRONT + 6:                                # 桥下的阴影（往前慢慢变浅）
                c = mix(c, (40, 104, 116), 0.62 - 0.09 * (y - PIER_FRONT))
            elif x >= wx - 3:                                      # 水边最浅（沙底透上来）
                c = mix(c, (190, 226, 204), 0.35 if x == wx - 1 else 0.18)
            ph = math.sin(x / 4.3 + y * 1.7) + 0.6 * math.sin(x / 9.1 - y * 0.8)
            if y > PIER_FRONT + 6:                                 # 沙底的波纹：一道道很缓的亮线 / 暗线
                if ph > 1.15:
                    c = mix(c, (200, 240, 226), 0.42)
                elif ph < -1.3:
                    c = dk(c, 0.93)
            px(d, x, y, c)
        px(d, wx, y, WET_D)                                        # 水边：湿沙一格深、一格浅
        px(d, wx + 1, y, WET)
        px(d, wx + 2, y, mix(WET, SAND_S, 0.5))
    # ---- 桥面木板
    planks = []
    x = 0
    i = 0
    while x <= x1:
        w = 4 + (1 if hash01(i, 5) < 0.4 else 0)
        planks.append((x, min(x1, x + w - 1), i))
        x += w
        i += 1
    joists = (149, 155, 162)
    for (a_, b_, i) in planks:
        base = mix(WOODP[0], (226, 216, 192), hrange(0.0, 0.55, i, 6))
        if hash01(i, 10) < 0.3:
            base = mix(base, (196, 192, 182), 0.35)                # 有几块晒得发灰
        for xx in range(a_, b_ + 1):
            for y in range(y0, y1 + 1):
                c = base
                if xx == b_:                                         # 板缝：往远处（y 小）越暗越密实，近处淡一点
                    c = mix(base, (90, 76, 62), 0.5 + 0.35 * (1 - (y - y0) / float(y1 - y0))) if y > y0 + 1 else WOODP[3]
                elif xx == a_:
                    c = lt(base, 0.08)
                elif hash01(xx, y // 3, i, 7) < 0.11:
                    c = mix(base, WOODP[2], 0.5)                     # 顺纹的短线
                c = mix(c, WOODP[2], 0.14 * (1 - (y - y0) / float(y1 - y0)))   # 往后（远）一点点暗
                px(d, xx, y, c)
        for y in joists:                                           # 钉子（一排一根龙骨）
            px(d, a_ + 1, y, (122, 108, 94))
            if b_ - a_ >= 4:
                px(d, b_ - 1, y, (122, 108, 94))
        if hash01(i, 8) < 0.3:                                     # 节疤
            ky = int(hrange(150, 161, i, 9))
            px(d, a_ + 2, ky, WOODP[3])
            px(d, a_ + 2, ky + 1, WOODP[2])
    hl(d, 0, x1, y0, WOODP[3])                                     # 后沿（桥面的厚度）
    hl(d, 0, x1, y1, lt(WOODP[0], 0.3))                            # 前沿亮边
    hl(d, 0, x1, PIER_FRONT, WOODP[1])                             # 前沿横梁
    hl(d, 0, x1, PIER_FRONT + 1, WOODP[2])
    hl(d, 0, x1, PIER_FRONT + 2, WOODP[3])
    for x in range(3, x1, 6):
        px(d, x, PIER_FRONT + 1, (78, 70, 66))                     # 横梁上的钉头
    vl(d, x1, y0, PIER_FRONT + 2, WOODP[4])                        # 栈桥右端（下面是沙）
    for (x, y) in ((x1 + 1, 160), (x1 + 1, 162), (x1 + 2, 163), (x1 + 1, 164), (x1 + 2, 165)):
        px(d, x, y, SAND_S)                                        # 栈桥脚下吹积的一点沙
    # ---- 四根桩：亮左暗右，水线上一圈藻 + 藤壶，水下一截发绿发淡
    for bx in PILES:
        for y in range(PIER_FRONT + 3, 178):
            for k, c in enumerate((WOODP[1], WOODP[2], WOODP[4])):
                px(d, bx + k, y, mix(c, SHALLOW[1], 0.55) if y >= 175 else c)
        hl(d, bx, bx + 2, 172, (80, 124, 66))
        hl(d, bx, bx + 2, 173, (58, 98, 58))
        px(d, bx + 1, 171, (226, 220, 200))
        px(d, bx + 2, 170, (190, 184, 168))
        hl(d, bx - 1, bx + 3, 174, (196, 238, 232))               # 水线（一推一退的水纹在 strip）
    # ---- 前沿的系缆桩 + 一根缆绳垂进水里（小艇拴在这里）
    rect(d, 18, 162, 21, 165, WOODP[3])
    hl(d, 17, 22, 162, WOODP[2])
    hl(d, 18, 21, 161, WOODP[1])
    P.wire(d, 21, 163, 30, 171, 2, ROPE_D)
    P.wire(d, 21, 162, 30, 170, 2, ROPE)
    # ---- 系船桩（后沿两根，高出桥面）
    for (bx, top) in ((6, 128), (28, 132)):
        rect(d, bx, top, bx + 3, y0, WOODP[2])
        vl(d, bx, top, y0, WOODP[1])
        vl(d, bx + 3, top, y0, WOODP[4])
        hl(d, bx, bx + 3, top, WOODP[0])
        hl(d, bx - 1, bx + 4, top + 4, ROPE_D)                     # 缠着的绳
        hl(d, bx - 1, bx + 4, top + 5, ROPE)
        hl(d, bx - 1, bx + 4, y0, WOODP[4])                        # 桩脚压在桥面上的暗
    for (cx, cy) in ((8, 141),):                                   # 挂在桩上的救生圈（橙白四段）
        for yy in range(cy - 4, cy + 5):
            for xx in range(cx - 4, cx + 5):
                r = math.hypot(xx - cx, yy - cy)
                if 2.0 <= r < 4.4:
                    ang = math.atan2(yy - cy, xx - cx)
                    c = (236, 110, 50) if int((ang + math.pi) / (math.pi / 2)) % 2 else (246, 242, 232)
                    if xx - cx > 1 and yy - cy > 0:
                        c = dk(c, 0.8)
                    px(d, xx, yy, c)
    # 竹竿（顶上挂三角旗，旗在 strip）
    vl(d, 38, 94, y0, (206, 186, 120))
    vl(d, 39, 94, y0, (156, 136, 84))
    for y in range(98, y0, 6):
        px(d, 38, y, (130, 112, 70))
    hl(d, 36, 41, y0 - 1, WOODP[3])
    # 油桶（红漆掉了一半）+ 木箱
    rect(d, 13, 134, 20, y0, (176, 60, 50))
    vl(d, 13, 134, y0, (210, 92, 76))
    vl(d, 20, 134, y0, (110, 38, 34))
    for y in (137, 143):
        hl(d, 13, 20, y, (132, 46, 40))
    rect(d, 15, 132, 17, 133, (90, 86, 84))
    for (x, y) in ((16, 139), (18, 140), (14, 141)):
        px(d, x, y, (150, 110, 96))
    rect(d, 24, 138, 34, y0, WOODP[1])
    rect(d, 24, 138, 34, 138, WOODP[0])
    vl(d, 34, 138, y0, WOODP[3])
    d.line((25, 139, 33, 145), fill=C(WOODP[2]))
    d.line((25, 145, 33, 139), fill=C(WOODP[2]))
    hl(d, 24, 34, y0, WOODP[4])
    # 后角一卷盘好的缆绳（平放在桥面上，压扁的椭圆 = 平躺着）
    d.ellipse((2, 149, 13, 153), outline=C(ROPE_D))
    d.ellipse((4, 150, 11, 152), outline=C(ROPE))
    px(d, 7, 151, ROPE_D)


LAP_REGION = (0, PIER_FRONT + 3, 52, H)


def lap_frame(t):
    """栈桥前面浅水的动（2 s 一圈）：水面的亮纹往右漂、水边的泡沫一推一退（推上来时水膜盖住一两格湿沙）、
    桩子脚下的水纹一圈圈往外扩。相位都是 2π·f/8 的整数倍 → 第 8 帧回到第 0 帧。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    ph = math.tau * f / N_ANIM
    for y in range(PIER_FRONT + 7, H):
        wx = water_x(y)
        for x in range(0, wx - 1):
            v = math.sin(x / 3.1 - ph + y * 2.3) + 0.55 * math.sin(x / 6.7 + 2 * ph - y * 1.1)
            if v > 1.3:
                px(d, x, y, (222, 248, 240))
            elif v > 1.18 and (x + y) % 2:
                px(d, x, y, (190, 236, 226))
        push = int(round(0.6 + 1.6 * math.sin(ph - y * 0.33)))     # 水边：推上来 / 退下去
        for k in range(max(0, push)):
            px(d, wx + k, y, (176, 222, 214))                      # 推上来的一层水膜
        px(d, wx + max(0, push), y, (246, 252, 250))               # 泡沫的边
        if push > 0 and (y + f) % 2:
            px(d, wx + push - 1, y, (226, 246, 242))
    for j, bx in enumerate(PILES):                                 # 桩脚的水纹
        r = (f + j * 3) % 4
        px(d, bx - 2 - r, 174, (214, 244, 238))
        px(d, bx + 4 + r, 174, (214, 244, 238))
        if r < 2:
            px(d, bx - 1 - r, 175, (176, 226, 220))
            px(d, bx + 3 + r, 175, (176, 226, 220))
    return im


def draw_parasol(im):
    """老人的阳伞：红白相间的伞面（8 片，左亮右暗，伞边一圈流苏）、伞杆插在后沿；伞下的影子很淡地落在沙上（右下）。
    伞下一张草席（平的）+ 小矮凳；左边插着钓竿（钓线和浮标在 strip），饵桶、钓具箱、小炭炉 + 铜壶。"""
    cx, top, rim = 140, 116, 132
    R = 22
    cast_shadow(im, [(128, 149), (170, 149), (178, 157), (136, 157)], mul=SOFT_MUL)
    d = ImageDraw.Draw(im)
    # 草席（菱形透视：后沿窄一点）
    for y in range(152, 165):
        u = (y - 152) / 12.0
        a_, b_ = int(126 - 3 * u), int(158 + 3 * u)
        for x in range(a_, b_ + 1):
            c = (214, 190, 134) if (x + y // 2) % 4 else (186, 160, 108)
            if y in (152, 164) or x in (a_, b_):
                c = (170, 144, 96)
            px(d, x, y, c)
    # 小矮凳（三条腿 + 圆面，5 px 高）
    hl(d, 136, 145, 155, WOODP[0])
    hl(d, 136, 145, 156, WOODP[2])
    for lx in (137, 141, 144):
        vl(d, lx, 157, 160, WOODP[3])
    # 伞杆
    for y in range(top, 147):
        u = (y - top) / (147 - top)
        x = round(cx + 6 * u)
        px(d, x, y, (226, 220, 204))
        px(d, x + 1, y, (150, 144, 132))
    hl(d, 145, 148, 146, (120, 110, 96))
    # 伞面：扁圆顶（略从下往上看），8 片红白相间
    for xx in range(cx - R, cx + R + 1):
        u = (xx - cx) / R
        yt = top + int(round((abs(u) ** 1.6) * (rim - top)))
        for yy in range(yt, rim + 1):
            ang = math.atan2(xx - cx, 6.0 + (yy - top) * 0.5)
            gore = int((ang + math.pi) / (math.pi / 4)) % 2
            c = RED if gore else CREAM
            if u < -0.45:
                c = lt(c, 0.12)
            elif u > 0.4:
                c = dk(c, 0.84)
            px(d, xx, yy, c)
        px(d, xx, yt, lt(RED if ((xx - cx) // 6) % 2 else CREAM, 0.2) if u < 0.3 else dk(CREAM, 0.8))
    hl(d, cx - R, cx + R, rim + 1, (150, 48, 44))                  # 伞边（暗）
    for k, xx in enumerate(range(cx - R, cx + R + 1, 2)):          # 流苏
        px(d, xx, rim + 2, CREAM if k % 2 else RED)
    vl(d, cx, top - 3, top - 1, (200, 190, 170))                   # 伞顶
    px(d, cx, top - 4, (236, 200, 90))
    # 钓竿（插在沙里的一截铁管里，竿往左后方伸到海上；竿梢以后在 strip）
    rect(d, ROD_BUTT[0] - 1, 140, ROD_BUTT[0] + 1, 147, (110, 112, 118))
    px(d, ROD_BUTT[0] - 1, 140, (160, 164, 170))
    d.line((ROD_BUTT[0], ROD_BUTT[1] - 6, ROD_TIP[0], ROD_TIP[1]), fill=C((84, 64, 48)))
    d.line((ROD_BUTT[0], ROD_BUTT[1] - 2, ROD_BUTT[0] - 2, ROD_BUTT[1] - 8), fill=C((60, 52, 50)))
    d.ellipse((ROD_BUTT[0] - 4, 132, ROD_BUTT[0], 136), outline=C((150, 150, 156)))   # 绕线轮
    px(d, ROD_BUTT[0] - 2, 134, (90, 90, 96))
    # 饵桶（锌皮）+ 钓具箱（绿）
    rect(d, 106, 139, 113, 147, (168, 172, 176))
    vl(d, 106, 139, 147, (206, 210, 214))
    vl(d, 113, 139, 147, (118, 122, 130))
    hl(d, 106, 113, 139, (120, 124, 132))
    d.arc((106, 134, 113, 142), 180, 360, fill=C((110, 110, 116)))
    rect(d, 150, 142, 158, 147, (70, 122, 90))
    hl(d, 150, 158, 142, (104, 156, 116))
    vl(d, 158, 142, 147, (44, 84, 60))
    rect(d, 153, 141, 155, 141, (60, 60, 66))
    # 小炭炉（陶）+ 铜壶（热气在 strip）
    kx, ky = KETTLE
    rect(d, kx - 4, ky + 2, kx + 4, 147, (150, 92, 64))
    vl(d, kx - 4, ky + 2, 147, (186, 120, 86))
    vl(d, kx + 4, ky + 2, 147, (104, 62, 44))
    rect(d, kx - 2, ky + 4, kx + 1, ky + 6, (240, 120, 40))        # 炉口的炭火
    px(d, kx - 1, ky + 5, (255, 210, 110))
    d.ellipse((kx - 4, ky - 5, kx + 3, ky + 2), fill=C((196, 136, 64)))
    px(d, kx - 2, ky - 3, (236, 190, 110))
    px(d, kx - 3, ky - 2, (236, 190, 110))
    d.line((kx + 3, ky - 1, kx + 6, ky - 4), fill=C((176, 118, 54)))   # 壶嘴
    hl(d, kx - 2, kx + 1, ky - 6, (140, 92, 46))                   # 壶把
    px(d, kx - 3, ky - 5, (140, 92, 46))
    px(d, kx + 2, ky - 5, (140, 92, 46))


def draw_palm_trunks(im):
    """三棵椰子树的树干（树冠在 strip）：根部一小堆沙，影子很淡地往右下拖。"""
    for (rx, ry, cx, cy, bend, L, sd) in PALMS:
        # 影子贴着后沿往右拖（不压到 y 153 往下：x 214–274 那块空沙地要留给神灯）
        cast_shadow(im, [(rx + 1, ry + 2), (rx + 32, ry + 4), (rx + 33, ry + 6), (rx + 1, ry + 4)], mul=SOFT_MUL)
        d = ImageDraw.Draw(im)
        P.palm_trunk(d, rx, ry, cx, cy + 2, bend, w0=5, w1=3)
        hl(d, rx - 4, rx + 5, ry + 1, SAND_S)
        hl(d, rx - 2, rx + 3, ry, SAND_L)


ROCKS = [  # (左上 x, 底 y, 宽, 高, 种子, 椭球 [(cx, cy, rx, ry)，按宽 / 高的比例])
    (286, 148, 11, 8, 3, [(0.45, 1.0, 0.48, 0.95), (0.72, 1.0, 0.32, 0.62)]),
    (296, 148, 26, 25, 1, [(0.45, 1.0, 0.48, 0.95), (0.72, 1.0, 0.32, 0.62)]),
    (318, 148, 42, 19, 2, [(0.3, 1.0, 0.32, 0.88), (0.6, 1.0, 0.34, 1.0), (0.86, 1.0, 0.2, 0.62)]),   # 中间裂缝的那块
]


def draw_rocks(im):
    """礁石一堆（石灰岩 + 珊瑚礁的灰褐色）：湿的深色底、藤壶、几簇绿藻；影子往右下落在沙上。
    最右边那块大礁石（x 318–360）从中间裂开一道竖缝（CRACK_X = rocks + 22）：缝里暗、上窄下宽，缝的右沿朝左受光、
    左沿背光，缝脚掏出一个小黑洞、洞口一小洼湿沙反着一点天光——剧情的海螺纪念品藏在这里（背景不画海螺）。"""
    for (x0, by, w, h, sd, balls) in ROCKS:
        r, m = P.rock_img(w, h, [(w * a, h * b, w * c, h * e) for (a, b, c, e) in balls], 500 + sd, wet=4)
        cast_shadow(im, [(x0 + w - 4, by - 2), (x0 + w + 8, by + 1), (x0 + w + 6, by + 3), (x0 + 4, by + 3)], mul=SOFT_MUL)
        paste(im, r, x0, by - h)
        d = ImageDraw.Draw(im)
        P.barnacle_dots(d, m, 520 + sd, max(2, w // 4), h - 7, h - 2, ox=x0, oy=by - h)
        for i in range(max(1, w // 6)):                             # 水线上的绿藻
            x = x0 + int(hrange(2, w - 3, sd, i, 3))
            y = by - int(hrange(2, 5, sd, i, 4))
            if abs(x - CRACK_X) < 4:
                continue
            if m[min(h - 1, y - (by - h)), min(w - 1, x - x0)]:
                hl(d, x, x + 2, y, (76, 120, 64))
                px(d, x + 1, y - 1, (110, 152, 80))
    # ---- 礁石缝
    d = ImageDraw.Draw(im)
    a = np.array(im)
    y0, y1 = CRACK_Y
    for y in range(y0, y1 + 1):
        u = (y - y0) / float(y1 - y0)
        xc = CRACK_X + (1 if math.sin(y * 0.8 + 0.5) > 0.7 else 0) - (1 if u > 0.8 else 0)   # 缝走得有点歪
        half = 0 if u < 0.35 else 1                               # 上面 1 px、往下 3 px 宽
        xa, xb = xc - half, xc + half
        if a[y, xa - 1, 3] == 0 or a[y, xb + 1, 3] == 0:          # 缝只裂在石头上
            continue
        for x in range(xa, xb + 1):
            px(d, x, y, (34, 30, 38) if (x == xc or u > 0.35) else (56, 48, 54))
        px(d, xa - 1, y, dk(P.ROCK_PAL[1], 0.9))                  # 左沿背光
        px(d, xb + 1, y, P.ROCK_PAL[3] if y % 3 else P.ROCK_PAL[4])   # 右沿朝左，受光
    # 缝脚的小黑洞（海螺就在这里面）+ 洞口一小洼湿沙
    rect(d, CRACK_X - 2, y1 - 2, CRACK_X + 2, y1, (30, 26, 34))
    hl(d, CRACK_X - 1, CRACK_X + 1, y1 - 3, (44, 38, 46))
    px(d, CRACK_X + 3, y1 - 1, P.ROCK_PAL[3])
    hl(d, CRACK_X - 3, CRACK_X + 3, y1 + 1, WET_D)
    hl(d, CRACK_X - 2, CRACK_X + 2, y1 + 2, WET)
    px(d, CRACK_X - 1, y1 + 1, (150, 196, 206))                    # 一点天光
    px(d, CRACK_X, y1 + 1, (186, 220, 228))


def draw_tidepool(im):
    """礁石脚下一小洼积水（映着天）+ 一块小石头。"""
    d = ImageDraw.Draw(im)
    d.ellipse((279, 147, 293, 151), fill=C(WET_D))
    d.ellipse((280, 148, 292, 150), fill=C((168, 212, 222)))
    hl(d, 282, 288, 148, (214, 238, 242))
    for (x, y, w, h, sd) in ((276, 148, 7, 5, 5), (362, 147, 6, 4, 6)):
        r, m = P.rock_img(w, h, [(w / 2, h, w / 2, h * 0.9)], 540 + sd, wet=2)
        paste(im, r, x, y - h)


def draw_hut(im):
    """渔家小屋：石头垫的地基、竖木板墙（每块 4 px，缝暗、两道横撑、钉子、补过的一块）、半开的门、支起来的木板窗、
    椰叶厚顶（层层往下、下沿参差、屋脊一捆）；檐下挂鱼干、马灯；门边水缸，右边靠着一支船桨。"""
    x0, x1 = HUT
    d = ImageDraw.Draw(im)
    cast_shadow(im, [(x1 - 2, 102), (x1 + 10, 108), (x1 + 12, 148), (x1 - 2, 148)], mul=SOFT_MUL)
    cast_shadow(im, [(x0 + 2, 148), (x1 + 2, 148), (x1 + 8, 151), (x0 + 6, 151)], mul=SOFT_MUL)
    d = ImageDraw.Draw(im)
    # 地基：一排石头
    for i, sx in enumerate(range(x0 - 2, x1 + 2, 7)):
        c = mix((168, 158, 140), (196, 186, 166), hash01(i, 31))
        rect(d, sx, 142, sx + 6, 147, c)
        hl(d, sx, sx + 6, 142, lt(c, 0.2))
        vl(d, sx + 6, 142, 147, dk(c, 0.7))
        hl(d, sx, sx + 6, 147, dk(c, 0.6))
    # 墙：竖木板
    wy0, wy1 = 96, 141
    for xx in range(x0 + 2, x1 - 1):
        bi = (xx - x0 - 2) // 4
        j = (xx - x0 - 2) % 4
        base = mix(WOODP[1], WOODP[2], hrange(0.0, 0.6, bi, 33))
        for y in range(wy0, wy1 + 1):
            c = base
            if j == 0:
                c = WOODP[4] if y % 7 else WOODP[3]                   # 板缝
            elif j == 1:
                c = lt(base, 0.1)
            elif hash01(xx, y // 4, 34) < 0.08:
                c = dk(base, 0.86)
            px(d, xx, y, c)
    for y in (104, 132):                                           # 两道横撑
        hl(d, x0 + 2, x1 - 2, y, WOODP[0])
        hl(d, x0 + 2, x1 - 2, y + 1, WOODP[2])
        hl(d, x0 + 2, x1 - 2, y + 2, WOODP[4])
        for xx in range(x0 + 4, x1 - 2, 4):
            px(d, xx, y + 1, (70, 64, 66))
    rect(d, 368, 112, 376, 124, (164, 118, 78))                    # 补过的一块新木板
    hl(d, 368, 376, 112, (196, 150, 100))
    vl(d, 376, 112, 124, (120, 84, 56))
    vl(d, x0 + 2, wy0, wy1, WOODP[0])                              # 墙角亮 / 暗
    vl(d, x1 - 2, wy0, wy1, WOODP[4])
    # 门：门框 + 半开（门扇往里推开，只看得见窄窄一条；屋里黑）
    a_, b_, dt = DOOR
    rect(d, a_ - 2, dt - 2, b_ + 2, wy1, WOODP[2])
    vl(d, a_ - 2, dt - 2, wy1, WOODP[0])
    vl(d, b_ + 2, dt - 2, wy1, WOODP[4])
    hl(d, a_ - 2, b_ + 2, dt - 2, WOODP[0])
    rect(d, a_, dt, b_, wy1, (34, 26, 26))
    for y in range(dt + 8, wy1, 9):                                # 屋里一点点看得出来的东西（暗的）
        px(d, b_ - 3, y, (52, 42, 40))
    rect(d, a_, dt, a_ + 4, wy1, (120, 96, 72))                    # 门扇（侧着，透视变窄）
    vl(d, a_ + 4, dt, wy1, (86, 68, 54))
    vl(d, a_, dt, wy1, (150, 124, 94))
    for y in (dt + 8, dt + 30):
        hl(d, a_ + 1, a_ + 3, y, (96, 76, 58))
    hl(d, a_, b_, wy1, (60, 48, 44))
    # 窗：窗洞黑、上面一块往外支起来的木板（一根小棍撑着）
    wx0, wx1, wy_0, wy_1 = WIN
    rect(d, wx0 - 1, wy_0 - 1, wx1 + 1, wy_1 + 1, WOODP[3])
    rect(d, wx0, wy_0, wx1, wy_1, (30, 24, 26))
    px(d, wx0 + 3, wy_0 + 4, (60, 50, 48))
    hl(d, wx0 - 2, wx1 + 2, wy_1 + 2, WOODP[0])                    # 窗台
    hl(d, wx0 - 2, wx1 + 2, wy_1 + 3, WOODP[4])
    for k in range(5):                                             # 支起来的窗板（往外斜）
        hl(d, wx0 - 1 + k, wx1 + 1 + k, wy_0 - 2 - k, WOODP[1] if k < 4 else WOODP[0])
    hl(d, wx0 + 3, wx1 + 4, wy_0 - 2, WOODP[3])
    d.line((wx1 + 1, wy_1, wx1 + 4, wy_0 - 5), fill=C(WOODP[3]))    # 撑棍
    # 椰叶顶：一层层往下压的叶捆（每层 5 行：上沿亮、往下一根根叶脉、下沿参差的暗边），左边受光、右边暗
    ry0, ry1 = 70, 100
    nlay = (ry1 - ry0) // 5 + 1
    for j in range(nlay):
        ya = ry0 + j * 5
        for y in range(ya, min(ry1, ya + 6) + 1):
            u = (y - ry0) / float(ry1 - ry0)
            a_r = int(round(x0 + 14 - 22 * u))
            b_r = int(round(x1 - 14 + 22 * u))
            for xx in range(a_r, b_r + 1):
                v = (xx - a_r) / max(1, b_r - a_r)
                r = y - ya
                tone = 1 if r < 2 else 2 if r < 4 else 3
                tone -= 1 if v < 0.22 else 0
                tone += 1 if v > 0.8 else 0
                if (xx * 3 + j * 5) % 5 == 0 and r > 0:              # 一根根的叶脉
                    tone += 1
                if hash01(xx, y, 35) < 0.06:
                    tone += 1
                if r >= 5 and hash01(xx, j, 36) < 0.45:             # 下沿参差：有的叶尖多垂一行
                    tone = 3
                px(d, xx, y, THATCH[max(0, min(4, tone))])
        for xx in range(int(round(x0 + 14 - 22 * (ya - ry0) / 30.0)), int(round(x1 - 14 + 22 * (ya - ry0) / 30.0)) + 1):
            if hash01(xx, j, 37) < 0.3:
                px(d, xx, ya, THATCH[0])                            # 上一层叶尖压在这一层上的亮点
    for xx in range(x0 - 8, x1 + 9):                               # 最下沿：垂下来的叶尖
        L = int(hrange(0, 4, xx, 36))
        for k in range(L):
            px(d, xx, ry1 + 1 + k, THATCH[2] if k < L - 1 else THATCH[3])
    rect(d, x0 + 12, ry0 - 4, x1 - 12, ry0, THATCH[2])             # 屋脊一捆（几道绑绳）
    hl(d, x0 + 12, x1 - 12, ry0 - 4, THATCH[0])
    hl(d, x0 + 12, x1 - 12, ry0 - 3, THATCH[1])
    for xx in range(x0 + 16, x1 - 12, 9):
        vl(d, xx, ry0 - 4, ry0, THATCH[4])
        vl(d, xx + 1, ry0 - 4, ry0, ROPE_D)
    for (sx, sy) in ((x0 + 10, ry0 - 6), (x1 - 12, ry0 - 7)):        # 屋脊两头翘出来的几根叶梗
        d.line((sx + 2, ry0 - 2, sx, sy), fill=C(THATCH[2]))
        d.line((sx + 3, ry0 - 2, sx + 2, sy - 1), fill=C(THATCH[3]))
    mul_box(im, (x0 + 2, wy0, x1 - 2, wy0 + 5), SHADOW_MUL)        # 檐下的影
    mul_box(im, (x0 + 2, wy0 + 6, x1 - 2, wy0 + 7), SHADOW_MUL, level=0.5)
    d = ImageDraw.Draw(im)
    # 檐下一串鱼干 + 马灯
    P.wire(d, 363, 102, 384, 102, 2, ROPE_D)
    for k, fx in enumerate(range(365, 384, 4)):
        vl(d, fx, 103 + (k % 2), 108 + (k % 2), (176, 166, 150))
        px(d, fx + 1, 104 + (k % 2), (140, 130, 116))
        px(d, fx, 109 + (k % 2), (120, 112, 100))
    vl(d, 385, 101, 103, (70, 66, 64))
    rect(d, 383, 104, 387, 110, (196, 160, 70))
    rect(d, 384, 105, 386, 109, (236, 220, 170))
    hl(d, 383, 387, 111, (70, 66, 64))
    # 门边的水缸（陶）
    d.ellipse((364, 128, 377, 147), fill=C((178, 112, 72)))
    d.chord((364, 128, 377, 147), 270, 90, fill=C((140, 84, 54)))
    hl(d, 366, 375, 129, (204, 140, 96))
    hl(d, 366, 375, 130, (90, 60, 44))
    px(d, 367, 134, (214, 156, 110))
    # 靠墙的船桨
    d.line((434, 147, 441, 104), fill=C(WOODP[1]))
    d.line((435, 147, 442, 104), fill=C(WOODP[3]))
    rect(d, 439, 100, 443, 110, WOODP[0])
    vl(d, 443, 100, 110, WOODP[3])
    # 窗下一条长凳（凳面 + 两条腿 + 凳下的暗），凳上一只编的鱼篓
    rect(d, 410, 135, 431, 136, WOODP[0])
    hl(d, 410, 431, 137, WOODP[3])
    for lx in (412, 428):
        vl(d, lx, 138, 147, WOODP[2])
        vl(d, lx + 1, 138, 147, WOODP[4])
    rect(d, 414, 129, 421, 134, (186, 154, 98))
    for xx in range(414, 422, 2):
        vl(d, xx, 129, 134, (150, 118, 72))
    hl(d, 415, 420, 128, (214, 186, 126))
    # 门前一块垫脚的扁石头（平的，在可走带后沿）
    rect(d, DOOR[0] + 2, 148, DOOR[1] - 2, 149, (186, 178, 160))
    hl(d, DOOR[0] + 2, DOOR[1] - 2, 148, (208, 200, 182))


CANOE = (230, 272, 147)       # 拉上岸的小渔船：船头 x、船尾 x、龙骨 y


def draw_canoe(im):
    """拉上岸的木渔船（船头朝左往上翘）：白色上舷、一道红线、蓝船身，船头画一只眼睛；两支桨斜搭在船上；影子往右下。"""
    x0, x1, by = CANOE
    L = x1 - x0
    cast_shadow(im, [(x0 + 6, by), (x1 + 4, by), (x1 + 9, by + 2), (x0 + 10, by + 2)], mul=SOFT_MUL)
    d = ImageDraw.Draw(im)
    for i in range(L + 1):
        u = i / float(L)
        x = x0 + i
        sheer = by - 8 - int(round(5 * (1 - u) ** 3 + 2.4 * u ** 4))
        keel = by - int(round(3 * (1 - u) ** 6 + 1.5 * u ** 8))
        for y in range(sheer, keel + 1):
            v = (y - sheer) / max(1.0, keel - sheer)
            c = (234, 230, 216) if v < 0.36 else (62, 112, 152)
            if y == sheer:
                c = (250, 248, 238)
            elif y == sheer + 3:
                c = (196, 64, 52)
            elif y == keel:
                c = (40, 62, 84)
            if u > 0.82:
                c = dk(c, 0.84)
            px(d, x, y, c)
        if i % 9 == 4:
            px(d, x, sheer + 1, (190, 186, 172))                    # 船舷上的钉子
    ex_, ey_ = x0 + 5, by - 9                                      # 船头的眼睛
    px(d, ex_, ey_, (40, 40, 48))
    px(d, ex_ + 1, ey_, (250, 250, 250))
    px(d, ex_ - 1, ey_, (200, 70, 50))
    d.line((x0 + 12, by - 15, x0 + 34, by - 10), fill=C(WOODP[1]))   # 两支桨
    d.line((x0 + 12, by - 14, x0 + 34, by - 9), fill=C(WOODP[3]))
    rect(d, x0 + 9, by - 17, x0 + 13, by - 14, WOODP[0])
    d.line((x0 + 18, by - 11, x0 + 40, by - 13), fill=C(WOODP[2]))
    rect(d, x0 + 38, by - 15, x0 + 42, by - 12, WOODP[1])
    d.line((x1 + 1, by - 6, x1 + 9, by + 1), fill=C(ROPE_D))         # 船尾一根缆绳拖在沙上
    px(d, x1 + 9, by + 1, ROPE)


def draw_net_static(im):
    """晾网的两根竹竿 + 竿脚一堆网（网本身在 strip）；再往右一条往岛里去的沙路。"""
    d = ImageDraw.Draw(im)
    for x in NET_POLES:
        vl(d, x, 96, 146, (206, 186, 120))
        vl(d, x + 1, 96, 146, (150, 130, 82))
        for y in range(100, 146, 7):
            px(d, x, y, (132, 112, 72))
        hl(d, x - 1, x + 2, 146, (120, 104, 70))
    for i in range(14):                                            # 竿脚一堆网
        x = 452 + int(hrange(0, 18, i, 41))
        y = 141 + int(hrange(0, 6, i, 42))
        hl(d, x, x + 3, y, (106, 112, 80) if i % 2 else (86, 92, 66))
    for (x, y) in ((455, 141), (463, 142), (468, 140)):
        px(d, x, y, (226, 200, 140))
    # 往岛里去的沙路（沙丘上一道浅色、踩实的沙）
    for y in range(133, 147):
        u = (147 - y) / 14.0
        a_ = int(458 + 14 * u)
        for x in range(a_, min(PW, a_ + 10)):
            px(d, x, y, mix(SAND_L, SAND, 0.3) if (x + y) % 3 else SAND)


def draw_dune(im):
    """沙丘（x 322 往右慢慢抬到 y 132）：朝左的坡亮、朝右暗一点；海葡萄灌木、一丛丛滨草。"""
    d = ImageDraw.Draw(im)
    for i in range(16):
        x = int(hrange(DUNE_X[0] + 10, PW - 6, i, 51))
        if HUT[0] - 6 < x < HUT[1] + 6 or NET_POLES[0] - 4 < x < NET_POLES[1] + 4:
            continue
        y = edge_y(x) + 1
        L = int(hrange(3, 7, i, 52))
        for k in range(L):                                         # 滨草：几根往右斜的细叶
            hgt = int(hrange(3, 8, i, k, 53))
            d.line((x + k, y, x + k + hgt // 3, y - hgt), fill=C((116, 140, 70) if k % 2 else (150, 166, 86)))
    for (x, sd) in ((346, 1), (446, 2), (476, 3)):
        y = edge_y(x) + 1
        P.bush(d, x, y, 7, 4, 940 + sd)


# ============================================================ 会动的（strip）
def palm_frame(i):
    def fn(t):
        im = A._new(PW, H)
        d = ImageDraw.Draw(im)
        f = fno(t)
        rx, ry, cx, cy, bend, L, sd = PALMS[i]
        sway = 0.85 * math.sin(math.tau * f / N_ANIM + sd * 0.9)
        P.palm_crown(d, cx, cy, L, sway, sd)
        return im
    return fn


PALM_FNS = [palm_frame(i) for i in range(len(PALMS))]


def flag_frame(t):
    """栈桥竹竿顶上的红三角旗：往右飘（风从海上来），沿旗身往后传的波。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    hx, hy = 40, 95
    L = 11
    for c in range(L):
        ph = math.tau * f / N_ANIM - c * 0.7
        dy = 1.3 * math.sin(ph) * (c / (L - 1))
        hh = int(round(5 * (1 - c / L))) + 1
        for r in range(hh):
            col = RED if r < hh - 1 or hh == 1 else dk(RED, 0.72)
            if math.cos(ph) < -0.4:
                col = dk(col, 0.82)
            px(d, hx + c, round(hy + r + dy + c * 0.2), col)
    return im


def float_frame(t):
    """钓线 + 浮标：线从竿梢垂下来（一点点弧），浮标一沉一浮，旁边一圈圈水纹。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    dy = (0, 0, 1, 2, 1, 0, 0, -1)[f]
    fx, fy = FLOAT_XY[0], FLOAT_XY[1] + dy
    P.wire(d, ROD_TIP[0], ROD_TIP[1], fx, fy - 2, 3 + (1 if dy > 0 else 0), (232, 232, 226))
    r = 2 + f % 4
    hl(d, fx - r - 1, fx - r, FLOAT_XY[1] + 1, (196, 240, 232))
    hl(d, fx + r, fx + r + 1, FLOAT_XY[1] + 1, (196, 240, 232))
    px(d, fx, fy - 2, (246, 246, 240))
    px(d, fx, fy - 1, RED)
    px(d, fx, fy, RED)
    px(d, fx + 1, fy, dk(RED, 0.7))
    return im


def steam_frame(t):
    """铜壶嘴的热气：三团往上飘、往右偏、越来越淡（2 s 一圈）。"""
    im = A._new(PW, H)
    f = fno(t)
    sx, sy = KETTLE[0] + 6, KETTLE[1] - 5
    a = np.zeros((H, PW, 4), np.uint8)
    for i in range(3):
        u = ((f / N_ANIM) + i / 3.0) % 1.0
        x = sx + 1 + int(round(3 * u + math.sin(u * 6.3 + i)))
        y = sy - 1 - int(round(13 * u))
        al = int(200 * (1 - u))
        if al < 30:
            continue
        for (dx, dy) in ((0, 0), (1, 0), (0, -1), (1, -1)) if u > 0.35 else ((0, 0), (0, -1)):
            if 0 <= y + dy < H:
                a[y + dy, x + dx] = (246, 246, 244, al)
    return Image.fromarray(a, 'RGBA')


NET_REGION = (NET_POLES[0] + 2, 96, NET_POLES[1], 142)


def net_frame(t):
    """晾着的渔网：上沿挂在两根竿之间的绳上（一排浮子），网身往下垂、下沿随风轻轻摆；斜格子网眼。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    a_, b_ = NET_POLES[0] + 2, NET_POLES[1] - 1
    sw = math.sin(math.tau * f / N_ANIM)
    mesh = (96, 108, 78)
    mesh_d = (74, 84, 62)
    for x in range(a_, b_ + 1):
        u = (x - a_) / float(b_ - a_)
        top = 101 + round(2.4 * 4 * u * (1 - u))
        bot = 136 + round(2 * math.sin(math.pi * u) + sw * 1.4 * math.sin(math.pi * u) + 0.6 * math.sin(u * 9 + f))
        for y in range(top + 1, bot + 1):
            v = (y - top) / max(1.0, bot - top)
            xo = x + round(sw * 1.2 * v * math.sin(math.pi * u))
            if (xo + y) % 4 == 0 or (xo - y) % 4 == 0:
                px(d, xo, y, mesh if v < 0.7 else mesh_d)
        px(d, x, top, ROPE_D)
        if x % 4 == 1:
            px(d, x, top + 1, (232, 206, 144) if x % 8 == 1 else (214, 112, 60))   # 浮子
        px(d, x + round(sw * 1.2 * math.sin(math.pi * u)), bot, mesh_d)
    return im


# ---------------------------------------------------------------- key burnt：小屋门口被火燎黑 + 冒烟
SOOT = (50, 42, 42)
CHAR = (30, 24, 26)


@lru_cache(maxsize=1)
def burnt_full():
    """key burnt（世界坐标，透明底，只留和近景不一样的像素）：把近景里的小屋门口燎黑。
    熏黑的程度 s(x, y) 0..1 分 3 档（档和档交界按 bayer 抖，硬边像素），每档往焦黑色多混一点：
      · 门框、门扇整片焦黑；门两边的墙板离门框越远越淡、越往上熏得越宽（火苗往上散），往左比往右远（火往左喷）；
      · 门洞正上方到檐下整段熏黑，门楣上的檐草烧焦一块（离门越近越黑，边参差）；
      · 门前往左一道焦沙（拖长的椭圆，近门最黑），门前的垫脚石熏黑；门左边的水缸熏黑右半边。
    剧情 7-04 的火焰特效从 hut_door 往左喷 30 px——焦的范围和它对得上。"""
    base = np.array(near_img())
    a = base.astype(np.float32)
    ys, xs = np.mgrid[0:H, 0:PW].astype(np.float32)
    nz = A._fbm(PW, H, 5, seed=93)
    bay = A._bayer(PW, H)
    da, db, dt = DOOR
    dcx = (da + db) / 2.0
    s = np.zeros((H, PW), np.float32)
    # 1) 墙板 + 门框
    wall = (ys >= 94) & (ys <= 141) & (xs >= HUT[0] + 2) & (xs <= HUT[1] - 2)
    up = np.clip((141 - ys) / 45.0, 0, 1)
    dl = (da - 3) - xs
    dr = xs - (db + 3)
    sl = np.clip(1 - dl / (5 + 13 * up), 0, 1) * (dl >= 0)
    sr = np.clip(1 - dr / (3 + 6 * up), 0, 1) * (dr >= 0)
    sw = np.maximum(sl, sr) * (0.5 + 0.5 * up)
    frame = (xs >= da - 3) & (xs <= db + 3)
    sw = np.where(frame, 1.0, sw)
    above = (ys < dt) & (np.abs(xs - dcx) <= (db - da) / 2.0 + 6)
    sw = np.where(above, np.maximum(sw, 0.9), sw)
    s = np.where(wall, np.clip(sw + (nz - 0.5) * 0.45, 0, 1), s)
    # 2) 门楣上的檐草
    roof = (ys >= 80) & (ys <= 106) & (np.abs(xs - dcx) <= 24) & (base[..., 3] > 0) & ~wall
    sroof = 1 - np.abs(xs - dcx) / 24.0 - (101 - ys) / 20.0
    s = np.where(roof, np.maximum(s, np.clip(sroof * 1.5 + (nz - 0.5) * 0.7, 0, 1)), s)
    # 3) 门前往左一道焦沙 + 垫脚石
    cx, cy, rx, ry = SCORCH_SAND
    dd = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2 + (nz - 0.5) * 0.8
    toward_door = np.clip((xs - (cx - rx)) / (2.0 * rx), 0, 1)
    ss = np.clip((1 - dd) * 1.5, 0, 1) * (0.45 + 0.55 * toward_door)
    sand = (ys >= 147) & (ys <= cy + ry + 2) & (dd < 1)
    s = np.where(sand, np.maximum(s, ss), s)
    step = (ys >= 148) & (ys <= 149) & (xs >= da + 2) & (xs <= db - 2)
    s = np.where(step, np.maximum(s, 0.8), s)
    # 4) 门左边的水缸：右半边（朝门的一面）熏黑
    jar = ((xs - 370.5) / 6.6) ** 2 + ((ys - 137.5) / 9.6) ** 2 <= 1.0
    s = np.where(jar, np.maximum(s, np.clip((xs - 368) / 9.0, 0, 1) * 0.75), s)
    # 量化成 3 档
    q = s + (bay - 0.5) * 0.18
    lvl = np.where(q > 0.78, 3, np.where(q > 0.5, 2, np.where(q > 0.24, 1, 0)))
    k = np.array((0.0, 0.32, 0.6, 0.86), np.float32)[lvl][..., None]
    tgt = np.where((lvl == 3)[..., None], np.array(CHAR, np.float32), np.array(SOOT, np.float32))
    out = a[..., :3] * (1 - k) + tgt * k
    changed = (lvl > 0) & (base[..., 3] > 0)
    res = np.zeros((H, PW, 4), np.uint8)
    res[changed, :3] = np.clip(np.round(out[changed]), 0, 255).astype(np.uint8)
    res[changed, 3] = 255
    im = Image.fromarray(res, 'RGBA')
    d = ImageDraw.Draw(im)
    for i in range(30):                                            # 焦沙上一点点灰白的灰
        x = int(hrange(cx - rx * 0.8, cx + rx * 0.8, i, 94))
        y = int(hrange(cy - ry * 0.7, cy + ry * 0.8, i, 95))
        if res[y, x, 3] and res[y, x, :3].sum() < 330:
            hl(d, x, x + (i % 2), y, (150, 144, 138) if i % 3 else (178, 172, 164))
    for y in range(dt + 3, 140, 5):                                # 门扇上一道道烧裂的炭纹
        px(d, da + 2, y, (74, 48, 38))
        px(d, da + 1, y + 1, (60, 42, 36))
    return im


@lru_cache(maxsize=1)
def burnt_crop():
    im = burnt_full()
    bb = im.getbbox()
    return im.crop((bb[0], 0, bb[2], H)), bb[0]


SMOKE_SRC = [(398, 99, 1.0), (386, 91, 0.75), (370, 152, 0.5)]    # 门楣、门左上的檐口、门前焦沙（x、y、浓度）
EMBERS = [(387, 110), (387, 124), (408, 106), (408, 133), (397, 141), (362, 154), (372, 156), (383, 152), (392, 150),
          (395, 90), (404, 95)]


def smoke_frame(t):
    """门口冒的烟：三缕往上飘、被海风吹向右（越高越淡、越散；旗子也往右飘）+ 门框 / 檐草 / 焦沙上一闪一闪的炭火星。"""
    a = np.zeros((H, PW, 4), np.uint8)
    f = fno(t)
    # 10-19 看图：原来烟团小（半径 1–3）、只升 34 px，和檐草的颜色挤在一起几乎看不见 → 烟团大一点、多一团、
    # 升到屋顶上面的天空里（那里对比才出得来），颜色由深灰到浅灰
    for j, (sx, sy, dens) in enumerate(SMOKE_SRC):
        for i in range(5):
            u = ((f / N_ANIM) + i / 5.0 + j * 0.17) % 1.0
            x = sx + int(round(16 * u + 1.6 * math.sin(u * 6.3 + j)))
            y = sy - 2 - int(round(58 * u * (0.6 + 0.4 * dens)))
            al = int(200 * dens * (1 - u) ** 0.7)
            if al < 24:
                continue
            col = (70, 64, 66) if u < 0.3 else ((118, 112, 112) if u < 0.6 else (160, 156, 156))
            r = 1 + int(u * 4)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r and 0 <= y + dy < H and hash01(x + dx, y + dy, i, j) < 0.85:
                        a[y + dy, x + dx] = col + (al,)
    for k, (ex, ey) in enumerate(EMBERS):                          # 炭火星：3 帧亮 1 帧暗，错开相位
        on = (f + k * 3) % 4 != 0
        a[ey, ex] = (255, 150, 60, 255) if on else (150, 64, 40, 255)
        if on and (f + k) % 2:
            a[ey, ex + 1] = (255, 224, 128, 255)
    return Image.fromarray(a, 'RGBA')


# ---------------------------------------------------------------- 螃蟹
CRAB_SHELL = ((242, 140, 96), (212, 88, 58), (150, 56, 42))


def crab(d, x, y, f, part=2):
    """一只小螃蟹（7×4，正面看）：两颗竖起来的黑眼、橘红的壳（上沿亮）、两只白尖的钳、腿每帧交替。
    part：0 = 只露眼睛（还在洞里）、1 = 露出上半身、2 = 整只。x, y = 壳的左下角。"""
    hi, sh, dkc = CRAB_SHELL
    px(d, x + 1, y - 2, (40, 30, 34))
    px(d, x + 3, y - 2, (40, 30, 34))
    if part == 0:
        return
    hl(d, x, x + 4, y - 1, sh)
    px(d, x + 1, y - 1, hi)
    px(d, x + 2, y - 1, hi)
    px(d, x - 1, y - 1, (236, 226, 214))
    px(d, x + 5, y - 1, (236, 226, 214))
    if part == 1:
        return
    hl(d, x, x + 4, y, dkc)
    if f % 2:
        for lx in (x - 1, x + 2, x + 5):
            px(d, lx, y + 1, dkc)
    else:
        for lx in (x, x + 4):
            px(d, lx, y + 1, dkc)
        px(d, x - 1, y, dkc)
        px(d, x + 5, y, dkc)


def crabs_frame(t):
    """两只螃蟹（anchors.crabs 附近，8 帧 @4 fps）：一只从右边的洞口探出眼睛、爬出来横着走两步、再退回洞里；
    另一只在第二个洞旁边横着来回爬。每帧位置 / 腿都不一样，第 8 帧回到第 0 帧。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    (c0x, c0y), (c1x, c1y) = ANCHORS['crabs']
    hx, hy = c0x + 7, c0y + 1                                      # 洞（draw_sand 里画的那个）
    off = (0, 0, 1, 3, 5, 4, 2, 0)[f]
    part = (0, 1, 2, 2, 2, 2, 2, 1)[f]
    crab(d, hx - 2 + off, hy, f, part)
    xs = (0, 2, 5, 8, 10, 8, 5, 2)
    crab(d, c1x - 7 + xs[f], c1y - 1, f + 1)
    return im


# ============================================================ 组装
@lru_cache(maxsize=1)
def near_img():
    im = A._new(PW, H)
    draw_sand(im)
    draw_dune(im)
    draw_pier(im)
    draw_palm_trunks(im)
    draw_parasol(im)
    draw_canoe(im)
    draw_rocks(im)
    draw_tidepool(im)
    draw_hut(im)
    draw_net_static(im)
    im = A._grade(im, sat=0.98, val=1.0)
    return opaque(im)


@lru_cache(maxsize=1)
def specs():
    """图层表（从后往前）。strip 的框按帧里实际画到的范围算。"""
    glide = glide_items()
    S = [dict(t='static', name='sky', img=sky_img()),
         dict(t='wrap', name='clouds', img=clouds_img(), period=640, k=CLOUD_K, vx=CLOUD_VX),
         dict(t='pano', name='far', img=far_img(), k=FAR_K)]
    for i, (y0, y1, k, vx) in enumerate(SEA_BANDS):
        S.append(dict(t='wrap', name='sea%d' % i, img=sea_band_img(i), period=640, k=k, vx=vx, y=y0))
    S += [dict(t='strip', name='glint', box=P.auto_box(glint_frame, N_ANIM, FPS_ANIM, GLINT_REGION), n=N_ANIM,
               fps=FPS_ANIM, fn=glint_frame, screen=True),
          dict(t='clouds', name='dhow', span=DHOW_SPAN, items=dhow_items()),
          dict(t='strip', name='gulls', box=P.auto_box(gulls_frame, N_ANIM, FPS_ANIM, (150, 30, 330, 90)), n=N_ANIM,
               fps=FPS_ANIM, fn=gulls_frame, k=GULL_K),
          dict(t='clouds', name='gull', span=460, items=glide),
          dict(t='pano', name='reef', img=reef_img(), k=REEF_K),
          dict(t='strip', name='buoy', box=P.auto_box(buoy_frame, N_ANIM, FPS_ANIM, (160, 100, 200, 130)), n=N_ANIM,
               fps=FPS_ANIM, fn=buoy_frame, k=REEF_K),
          dict(t='pano', name='hill', img=hill_img(), k=HILL_K),
          dict(t='pano', name='shore', img=shore_img(), k=1.0),
          dict(t='strip', name='surf', box=P.auto_box(surf_frame, N_ANIM, FPS_ANIM, SURF_REGION), n=N_ANIM, fps=FPS_ANIM,
               fn=surf_frame, k=1.0),
          dict(t='pano', name='near', img=near_img(), k=1.0),
          dict(t='strip', name='lap', box=P.auto_box(lap_frame, N_ANIM, FPS_ANIM, LAP_REGION), n=N_ANIM, fps=FPS_ANIM,
               fn=lap_frame, k=1.0)]
    for i, (rx, ry, cx, cy, bend, L, sd) in enumerate(PALMS):
        reg = (cx - L - 10, cy - L - 6, cx + L + 12, cy + L + 10)
        S.append(dict(t='strip', name='palm%d' % i, box=P.auto_box(PALM_FNS[i], N_ANIM, FPS_ANIM, reg), n=N_ANIM,
                      fps=FPS_ANIM, fn=PALM_FNS[i], k=1.0))
    S += [dict(t='strip', name='flag', box=P.auto_box(flag_frame, N_ANIM, FPS_ANIM, (36, 88, 60, 110)), n=N_ANIM,
               fps=FPS_ANIM, fn=flag_frame, k=1.0),
          dict(t='strip', name='float', box=P.auto_box(float_frame, N_ANIM, FPS_ANIM, (78, 92, 106, 134)), n=N_ANIM,
               fps=FPS_ANIM, fn=float_frame, k=1.0),
          dict(t='strip', name='steam', box=P.auto_box(steam_frame, N_ANIM, FPS_ANIM, (160, 110, 190, 140)), n=N_ANIM,
               fps=FPS_ANIM, fn=steam_frame, k=1.0),
          dict(t='strip', name='net', box=P.auto_box(net_frame, N_ANIM, FPS_ANIM, (440, 90, 480, 146)), n=N_ANIM,
               fps=FPS_ANIM, fn=net_frame, k=1.0),
          dict(t='strip', name='crabs', box=P.auto_box(crabs_frame, N_ANIM, FPS_ANIM, (180, 160, 320, 180)), n=N_ANIM,
               fps=FPS_ANIM, fn=crabs_frame, k=1.0)]
    bim, bx = burnt_crop()
    S += [dict(t='pano', name='burnt', img=bim, k=1.0, x=bx, key='burnt'),
          dict(t='strip', name='smoke', box=P.auto_box(smoke_frame, N_ANIM, FPS_ANIM, (340, 16, 470, 172)), n=N_ANIM,
               fps=FPS_ANIM, fn=smoke_frame, k=1.0, key='burnt'),
          dict(t='tint', name='dusk_a', color='#2c2a64', alpha=0.16, key='dusk'),
          dict(t='tint', name='dusk_b', color='#ff8a3c', alpha=0.22, key='dusk')]
    return S


def anchors():
    an = dict(ANCHORS)
    an.update(horizon=HZ, hut_box=[HUT[0] - 8, 66, HUT[1] + 8, 148], window=[(WIN[0] + WIN[1]) // 2, (WIN[2] + WIN[3]) // 2],
              rod_tip=list(ROD_TIP), float=list(FLOAT_XY), crack=[CRACK_X, (CRACK_Y[0] + CRACK_Y[1]) // 2],
              burnt_box=list(burnt_full().getbbox()),
              palms=[[cx, cy] for (rx, ry, cx, cy, b, L, s) in PALMS])
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
    near = near_img()
    m0, s0 = P.walk_stats(near, WALK, PIER_X, PW)
    cfg = dict(
        name='红海小岛', pw=PW, walk=WALK,
        states=[{}, {'burnt': True}, {'dusk': True}, {'burnt': True, 'dusk': True}],
        opaque=[('天空底图整张不透明', sky_img(), (0, 0, W, HZ + 2)),
                ('远景 海面（海平线 → y 147）整片不透明', far_img(), (0, HZ, FARW, SEA_BOT + 1)),
                ('近景 可走带（y 148–176）+ 前沿 整条不透明', near, (0, WALK[0], PW, H)),
                ('近景 沙丘（x 372–480，y 134 往下）不透明', near, (DUNE_X[1], 134, PW, H))],
        binary=[('近景只有 0 / 255 两种透明度', near), ('小山丘层只有 0 / 255 两种透明度', hill_img()),
                ('焦黑层只有 0 / 255 两种透明度', burnt_full())],
        stand=['arrive', 'pier', 'boat', 'oldman', 'crabs', 'lamp', 'rocks', 'hut', 'hut_door', 'exit'],
        inside=['umbrella', 'hut_box', 'window', 'rod_tip', 'float', 'crack', 'burnt_box', 'palms'],
        clear=[('神灯那块空沙地（x 214–274，y 153–176）只有平的沙（离沙色太远的像素）', near,
                (CLEAR[0], 153, CLEAR[1], 177), SAND, 40)],
        notes=['可走带亮度（干沙 x 44–480，y 148–176）：均值 %.0f 标准差 %.1f' % (m0, s0)],
    )
    P.std_checks(ex, BJ, st, S, cfg)
    # 小屋的门 / 窗确实是黑的（剧情说“门半开、窗口黑”）
    a = np.array(near)[..., :3].astype(np.float32)
    lum = P._lum(a)
    ex.checked('小屋门洞里（x 394–405，y 104–138）是暗的（亮度 > 70 的像素）',
               int((lum[104:139, DOOR[0] + 5:DOOR[1]] > 70).sum()))
    ex.checked('小屋窗口（窗洞里）是暗的（亮度 > 70 的像素）', int((lum[WIN[2] + 1:WIN[3], WIN[0] + 1:WIN[1]] > 70).sum()))
    # 礁石缝：rocks + 22 那一列（±1）从缝顶到缝脚都要有暗缝（亮度 < 60）——剧情的海螺纪念品和花京院的触须对着它
    rx_ = ANCHORS['rocks'][0] + 22
    miss = sum(1 for y in range(CRACK_Y[0] + 2, CRACK_Y[1] + 1) if not (lum[y, rx_ - 1:rx_ + 2] < 60).any())
    ex.checked('礁石缝在 rocks + 22（x %d，y %d–%d）每一行都有暗缝（缺的行数）' % (rx_, CRACK_Y[0] + 2, CRACK_Y[1]), miss)
    # 焦黑层只落在小屋门口一带（hut_door 往左 50 px、往右 20 px 以内），神灯那块空沙地不受影响
    bb = burnt_full().getbbox()
    hx = ANCHORS['hut_door'][0]
    ex.checked('焦黑层范围 %s 在小屋门口一带（x %d–%d）' % (list(bb), hx - 50, hx + 40),
               int(bb[0] < hx - 50) + int(bb[2] > hx + 40))
    # 栈桥前面的浅水：SPW 小艇（anchors.boat + 8）那一点是水
    bx_, by_ = ANCHORS['boat'][0] + 8, ANCHORS['boat'][1]
    ex.checked('小艇的位置（boat + 8 = [%d, %d]）是浅水（x < 水边）' % (bx_, by_), int(not bx_ < water_x(by_) - 2))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch7', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 80, 160):
        P.direct(specs(), camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'redsea_island_solo_%d.png' % camX))
    print('ok')
