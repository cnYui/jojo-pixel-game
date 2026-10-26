# -*- coding: utf-8 -*-
r"""dream_carnival —— 第6章「死神13 的梦」：夜里的游乐园，紫粉色的天，像一张儿童画慢慢变得不对劲。第 13 战的场地。
2026-10-18 ch6-misc 组在原工程 bg_egypt.dream_carnival 的基础上重画（改前：漩涡天 + 一个摩天轮圈 + 一顶帐篷 + 纯色地面；
later_stages 只用了第 0 相位的天和静态的帐篷）。保留原工程的点子：漩涡天、戴睡帽的月亮、摩天轮、马戏帐篷、
飘着的玩具（直接用原工程的气球 / 鸭子 / 积木 / 星星小精灵），地面换成强透视的棋盘格。

地图 320 宽（单屏）、ground 160、可走带 y 140–176 = 棋盘格地面的前半截；地平线 y 100（消失点 x 160），
棋盘格从地平线一路铺到画面下沿，越近格子越大（最前一排约 26×14），远处的格子抖成一片雾。侧视 + 强透视。
从左到右：
  x 14–98     旋转木马：红白条纹的尖顶、金色的饰边 + 一圈灯泡、扇贝形的垂边、镜面的中柱、圆台子；
              五匹木马（前三后二）骑在铜杆上一上一下（strip）；木马的眼睛是红点（anchors.carousel 站在它前面）
  x 54–142    摩天轮（中心 (98,72)、半径 44）：两道轮圈、8 根辐条、16 颗灯泡（追着闪）、8 个吊厢（粉 / 黄相间，一直往下垂）
              ——整轮慢慢转（strip，16 帧转 90°）；前面的 A 字架和轮毂不动；脚下一个售票亭，亭顶一张笑得太宽的小丑脸
              （anchors.wheel 站在它前面）
  x 140–210   糖果摊：粉白竖条的小亭子、扇贝形的遮阳篷、柜台上一排糖果罐、一架棉花糖、两根大棒棒糖（螺旋）插在亭顶、
              亭顶一颗包糖纸的大糖果招牌；右边柱子上拴着一串气球（strip 飘）
  x 222–308   马戏帐篷（大顶篷）：粉黄放射条纹的顶、扇贝垂边 + 一圈跑马灯（strip）、蓝绿白竖条的围墙、门帘掀开、
              里面黑洞洞的、有两只眼睛在看（strip 眨眼）；顶上一面小旗（strip）；顶到两根彩杆拉着两串三角旗（anchors.tent）
  远处        地平线上一座歪歪扭扭的城堡剪影（尖顶都是斜的、几个亮着的窗、一扇窗里有一双眼睛：strip 闪）、
              紫色的远丘、一段过山车的轨道剪影和一座螺旋滑梯塔
  天          紫 → 粉的漩涡天（围着月亮一圈圈转开，像儿童画用蜡笔涂的）、戴睡帽的月牙（闭着眼，偶尔睁开一只：strip）、
              一闪一闪的十字星（strip）、慢慢飘的棉花糖云（clouds，底下往下滴）、五只飘着的玩具（strip 上下浮）
  地上        四根老式路灯（圆灯罩 + 一圈隔点的光）、两串彩灯（strip 追着闪）、几段红绳围栏、
              可走带后沿散着的玩具：歪倒的泰迪熊（一只眼睛是 X 形缝线）、两块写着 1 和 3 的积木、一只小陀螺、一个小丑盒子
  可走带      三个玩具箱放的地方（anchors.toys，x 90 / 170 / 250）只有棋盘格
key：checker（地面变成陷阱：可走带里的黑格一格格亮起紫光，从远往近一波一波推过来：strip）、
     dark（梦变黑：整屏压暗的 tint）。

图层（从后往前）：
  sky         static           漩涡天 + 地平线一道粉光（320×100）
  stars       strip            十字星闪（8 帧 @4 fps）
  moon        strip            戴睡帽的月牙，偶尔睁眼（8 帧 @4 fps）
  clouds      clouds           三朵棉花糖云慢慢飘（k 0）
  floaters_*  strip            飘着的玩具（原工程的气球 / 鸭子 / 积木 / 星星）（8 帧 @4 fps）
  far         static           远丘、城堡剪影、过山车轨道、螺旋滑梯塔
  castle      strip            城堡窗户闪（8 帧 @4 fps）
  floor       static           强透视棋盘格地面（y 100–180，整片不透明）+ 东西投在地上的影
  trap        strip  key checker  陷阱：黑格亮紫光（8 帧 @4 fps）
  ferris      strip            摩天轮转动的部分（16 帧 @4 fps，4 s 转 90°）
  near        static           木马的顶 / 中柱 / 台子、摩天轮的 A 字架 + 轮毂、售票亭、糖果摊、帐篷、路灯、围栏、玩具（只有 0 / 255）
  horses      strip            木马一上一下（8 帧 @4 fps）
  balloons    strip            糖果摊的一串气球（8 帧 @4 fps）
  lights_*    strip            彩灯追着闪、木马顶的灯泡、帐篷跑马灯、帐篷里的眼睛眨（8 帧 @4 fps）
  flag        strip            帐篷顶的小旗（8 帧 @4 fps）
  dark        tint   key dark  梦变黑
锚点：arrive [60,160]、toys [[90,162],[170,162],[250,162]]、carousel [56,150]、wheel [98,151]、tent [265,134]（规格表）；
      另导出 wheel_hub [98,72]、wheel_r 44、moon [264,30]、candy [175,150]、castle [180,74]、horizon 100、
      checker（透视棋盘的参数：消失点、行的分界 y、最前一排每格宽）、walk_x；
      checker_dark（2026-10-19 加：地图可走带 y 135–177 里每个深格的近似矩形 [[x0, y0, x1, y1], …]，x1 / y1 不含，
      宽 < 4 的碎格丢掉；第6章梦二的棋盘陷阱直接循环它。算法见 checker_dark_rects；画面一个像素没改）。
单独运行：python -B tools\bg_new\dream_carnival.py → tools\bg_new\_preview\ch6\after\dream_carnival_solo_*.png
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
from engine import bg_egypt as E  # noqa: E402


def _parts():
    """ch6 组共用的小工具 / 自检（tools\\bg_new\\ch6_parts.py，按路径加载）。"""
    key = 'bg_new_ch6_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'ch6_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
C = A._c4
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
mul_box, cast_shadow, opaque = P.mul_box, P.cast_shadow, P.opaque
SHADOW_MUL, SOFT_MUL = P.SHADOW_MUL, P.SOFT_MUL
fidx = P.fidx

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
GROUND = 160
WALK = (140, 176)
HZ = 100                      # 地平线（棋盘格的消失线）
VPX = 160                     # 消失点 x
TD = 0.0026                   # 透视：一行格子在 1/(y−HZ) 上的步长
TW = 0.34                     # 透视：一格的宽 = TW·(y−HZ)
N_ANIM, FPS_ANIM = 8, 4.0
N_WHEEL = 16
WHEEL = (98, 72, 44)          # 摩天轮 中心 x, y, 半径
CAROUSEL = (56, 14, 98)       # 旋转木马 中心 x, 左, 右
CAR_BASE = 138                # 木马台子底
STALL = (144, 206)            # 糖果摊
TENT = (222, 308)
TENT_PEAK = (265, 60)
TENT_BASE = 134
MOON = (264, 30, 15)
LAMPS = [6, 132, 214, 316]
TOYS = [[90, 162], [170, 162], [250, 162]]

ANCHORS = dict(
    arrive=[60, 160],
    toys=TOYS,
    carousel=[56, 150],        # 站在旋转木马前
    wheel=[98, 151],           # 站在摩天轮（售票亭）前
    tent=[265, 134],           # 帐篷门口（物件：门帘底）
    walk_x=[8, 312],
)

# ============================================================ 调色
INK = (40, 14, 56)
SKY_STOPS = [(30, 12, 60), (70, 26, 108), (140, 52, 150), (214, 98, 170), (250, 160, 176), (255, 204, 178)]
FLOOR_L = (214, 152, 200)     # 棋盘格 浅格
FLOOR_D = (138, 84, 164)      # 棋盘格 深格（对比压低：人物站上去看得清）
FOG = (236, 166, 196)         # 远处的雾（地平线的粉光）
GOLD = (244, 200, 84)
GOLD_D = (184, 130, 50)
PINK = (246, 96, 150)
PINK_D = (180, 54, 110)
CREAM = (255, 236, 206)
TEAL = (70, 196, 196)
TEAL_D = (40, 130, 146)
LILAC = (196, 150, 230)
CANDY = [(246, 80, 130), (255, 214, 80), (90, 200, 240), (120, 220, 140), (200, 120, 240), (255, 150, 60)]


# ============================================================ 天
@lru_cache(maxsize=1)
def sky_img():
    """漩涡天：竖的渐变（上深紫、地平线粉橙）上叠一圈圈围着月亮转开的漩涡带（像蜡笔一圈圈涂的），
    分成 14 档、档和档之间按 Bayer 抖开；地平线上一道粉光。"""
    h = HZ + 2
    yy, xx = np.mgrid[0:h, 0:W].astype(np.float32)
    mx, my = MOON[0], MOON[1]
    dx, dy = xx - mx, (yy - my) * 1.15
    r = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    swirl = np.sin(r * 0.11 - th * 2.0) * 0.5 + 0.5                      # 一圈圈的螺旋带
    u = np.clip(yy / (h - 1), 0, 1) ** 0.85
    u = np.clip(u + (swirl - 0.5) * 0.26 * (1 - u * 0.6) - np.clip(1 - r / 60, 0, 1) * 0.18, 0, 1)
    bands = 14
    q = u * (bands - 1)
    thr = A._bayer(W, h)
    uu = (np.floor(q) + ((q - np.floor(q)) > thr)) / (bands - 1)
    pos = np.linspace(0, 1, len(SKY_STOPS))
    cols = np.array(SKY_STOPS, np.float32)
    out = np.stack([np.interp(uu, pos, cols[:, k]) for k in range(3)], -1)
    a = np.zeros((h, W, 4), np.uint8)
    a[..., :3] = np.clip(out, 0, 255).astype(np.uint8)
    a[..., 3] = 255
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    for i in range(46):                                                  # 蜡笔的笔触：顺着漩涡一圈圈的短弧（亮一点）
        rr = hrange(26, 260, i, 1)
        a0 = hrange(0, math.tau, i, 2)
        L = hrange(0.12, 0.3, i, 3) * (60 / max(30, rr) + 0.4)
        for k in range(24):
            a = a0 + L * k / 23
            x = int(round(mx + math.cos(a) * rr))
            y = int(round(my + math.sin(a) * rr / 1.15))
            if 0 <= x < W and 2 <= y < HZ - 10:
                c = im.getpixel((x, y))[:3]
                px(d, x, y, lt(c, 0.14) if i % 3 else dk(c, 0.9))
    a = np.array(im).astype(np.float32)                                   # 四角压暗（梦的边缘发黑）
    yy2, xx2 = np.mgrid[0:h, 0:W].astype(np.float32)
    vig = np.clip(1.0 - 0.32 * np.clip(np.hypot((xx2 - 160) / 190, (yy2 - 90) / 110) - 0.55, 0, 1) / 0.6, 0.68, 1)
    q = np.floor(vig * 10 + A._bayer(W, h)) / 10.0
    a[..., :3] *= q[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    A._glow(im, MOON[0], MOON[1], 46, 40, (255, 220, 200), 46, rings=4)  # 月亮周围一圈光
    return opaque(im)


STAR_PTS = [(int(hrange(4, 236, 88, i)), int(hrange(4, 84, 88, i, 1))) for i in range(16)] + \
           [(int(hrange(296, 318, 89, i)), int(hrange(6, 60, 89, i, 1))) for i in range(3)]
STAR_BOX = (0, 0, W, 90)


def stars_frame(t):
    """十字星（strip）：每颗星自己的相位——灭 / 一个点 / 十字 / 大十字（中心白、四个角带一点粉）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    for i, (x, y) in enumerate(STAR_PTS):
        lv = (0, 1, 2, 3, 2, 1, 1, 0)[(f + int(hash01(i, 3) * 8)) % N_ANIM]
        c = (255, 250, 210) if i % 3 else (170, 255, 230)
        if lv >= 1:
            px(d, x, y, c)
        if lv >= 2:
            for (ox, oy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                px(d, x + ox, y + oy, mix(c, (200, 100, 200), 0.4))
        if lv >= 3:
            for (ox, oy) in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                px(d, x + ox, y + oy, mix(c, (200, 100, 200), 0.65))
    return im


MOON_BOX = (240, 4, 294, 52)


def moon_frame(t):
    """戴睡帽的月牙（strip）：牙尖朝左、脸在里面那道弧上（闭着的眼、往上弯的嘴、一点腮红）——
    8 帧里有两帧眼睛慢慢睁开一条缝、露出一点红（梦里不对劲的地方）；睡帽尖上的白绒球一晃一晃。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    mx, my, r = MOON
    yy, xx = np.mgrid[0:2 * r + 3, 0:2 * r + 3] - (r + 1)
    a = (xx * xx + yy * yy <= r * r) & ~((xx - 7) ** 2 + (yy + 4) ** 2 <= (r - 2) ** 2)
    ys, xs = np.nonzero(a)
    for y, x in zip(ys, xs):
        wx, wy = mx - r - 1 + x, my - r - 1 + y
        edge = not a[min(a.shape[0] - 1, y + 1), x] or not a[y, min(a.shape[1] - 1, x + 1)]
        px(d, wx, wy, (226, 190, 120) if edge else (255, 236, 160))
    for (x, y) in ((mx - 12, my - 4), (mx - 13, my + 2), (mx - 11, my + 7)):   # 月面上的几个坑
        px(d, x, y, (236, 206, 130))
    eye = (0, 0, 0, 0, 0, 1, 2, 1)[f]                                   # 0 闭 / 1 一条缝 / 2 睁开
    ex, ey = mx - 7, my - 1
    if eye == 0:
        d.line((ex - 1, ey, ex + 1, ey + 1), fill=C((120, 70, 60)))
        px(d, ex - 2, ey - 1, (120, 70, 60))
    else:
        hl(d, ex - 2, ex + 1, ey, (250, 250, 240))
        hl(d, ex - 2, ex + 1, ey - 1, (120, 70, 60))
        if eye == 2:
            hl(d, ex - 2, ex + 1, ey + 1, (250, 250, 240))
            px(d, ex - 1, ey, (200, 20, 40))
            px(d, ex - 1, ey + 1, (120, 10, 30))
        else:
            px(d, ex - 1, ey, (200, 20, 40))
    for (x, y) in ((mx - 6, my + 5), (mx - 5, my + 6), (mx - 4, my + 6)):   # 嘴（往上弯的笑）
        px(d, x, y, (120, 70, 60))
    px(d, mx - 9, my + 3, (250, 140, 150))
    px(d, mx - 10, my + 3, (250, 140, 150))
    cap = [(mx - 4, my - 14), (mx + 4, my - 12), (mx + 15, my - 21)]   # 睡帽
    d.polygon(cap, fill=C((90, 150, 230)))
    d.line((mx - 1, my - 13, mx + 6, my - 15), fill=C((250, 250, 255)))
    d.line((mx + 6, my - 16, mx + 11, my - 18), fill=C((250, 250, 255)))
    bx, by = mx + 16 + (0, 1, 2, 1, 0, -1, -2, -1)[f], my - 22                    # 绒球每帧都晃（三角波）
    d.ellipse((bx - 2, by - 2, bx + 2, by + 2), fill=C((255, 250, 240)))
    px(d, bx - 1, by - 1, (255, 255, 255))
    return im


@lru_cache(maxsize=8)
def candy_cloud(w, seed):
    """棉花糖云：粉 / 淡紫的一团（原工程的云精灵换颜色），底下几根往下滴的“糖丝”。"""
    pal = ((255, 214, 236), (240, 170, 214), (214, 136, 200), (180, 104, 176))
    cl = A._cloud_sprite(w, w * 0.34, seed, pal)
    im = A._new(cl.width, cl.height + 7)
    paste(im, cl, 0, 0)
    d = ImageDraw.Draw(im)
    for k in range(4):
        x = int(hrange(3, cl.width - 3, seed, k))
        L = int(hrange(2, 7, seed, k, 1))
        for j in range(L):
            if im.getpixel((x, cl.height - 2))[3] > 0:
                px(d, x, cl.height - 1 + j, (214, 136, 200) if j < L - 1 else (240, 170, 214))
    return im


CLOUDS = [(48, 30, 3.0, 40.0, 11), (36, 56, 2.0, 230.0, 12), (30, 16, 4.0, 380.0, 13)]   # (宽, y, vx, x0, 种子)
CLOUD_SPAN = 520


FLOATERS = [('balloon', 146, 22, None), ('duck', 196, 40, None), ('star', 26, 24, None),
            ('block', 226, 46, (('b', (240, 70, 110)), ('B', (170, 40, 90)))),
            ('balloon', 300, 70, (('r', (90, 220, 150)), ('R', (40, 150, 110))))]
FLOAT_BOXES = [('floaters_%d' % i, (x - 2, y - 3, x + 13, y + 22)) for i, (nm, x, y, rc) in enumerate(FLOATERS)]


def floaters_frame(t):
    """飘着的玩具（strip，原工程 bg_egypt 的小精灵）：每个上下浮 2 px、左右晃 1 px，气球底下一根细线跟着摆。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    for i, (nm, x, y, rc) in enumerate(FLOATERS):
        ph = math.tau * f / N_ANIM + i * 1.9
        bx = x + round(math.sin(ph) * 1.0)
        by = y + round(math.sin(ph + 1.2) * 2.0)
        if nm == 'balloon':
            for j in range(10):
                px(d, round(bx + 4 + math.sin(ph + j * 0.6) * 1.0), by + 9 + j, (250, 240, 255))
        paste(im, E._toy(nm, rc), bx, by)
    return im


# ============================================================ 远景：远丘 / 城堡 / 过山车
CASTLE_WINS = [(150, 78), (164, 68), (180, 60), (196, 72), (167, 90)]


@lru_cache(maxsize=1)
def far_img():
    """远丘（两层紫，上沿亮）+ 一座歪歪扭扭的城堡剪影（尖顶往不同方向斜，像孩子画歪了）+ 左边一段过山车轨道 +
    右边一座螺旋滑梯塔。都是剪影色，月亮那边（右）一道亮边。窗户的灯在 strip 里。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for (base, amp, sc, sd, col, rim) in ((96, 10, 0.03, 3, (126, 56, 140), (170, 96, 176)),
                                          (100, 6, 0.05, 5, (104, 44, 124), (150, 80, 164))):
        for x in range(W):
            v = sum(math.sin(x * sc * (k + 1) + hrange(0, 6.3, sd, k)) / (k + 1) for k in range(3))
            y0 = int(round(base - amp * (0.5 + 0.35 * v)))
            vl(d, x, y0, HZ + 1, col)
            px(d, x, y0, rim)
    # 城堡（x 140–220）：城墙（垛口）+ 五座塔，每座塔顶一顶比塔身宽的尖帽子（往不同方向歪，像孩子画歪了），月亮那边一道亮边
    body = (74, 32, 104)
    roof = (104, 36, 116)
    rimc = (140, 84, 166)
    rect(d, 146, 86, 214, HZ + 1, body)
    for x in range(146, 215, 4):
        rect(d, x, 83, x + 1, 85, body)
    hl(d, 146, 214, 86, rimc)
    for (cx, w, top, lean, rh) in ((151, 8, 72, -3, 12), (165, 9, 62, 2, 14), (181, 13, 52, -2, 18), (197, 9, 64, 3, 14),
                                   (210, 7, 74, -2, 11)):
        rect(d, cx - w // 2, top, cx + w // 2, HZ, body)                    # 塔身
        vl(d, cx + w // 2, top, HZ, rimc)
        for x in range(cx - w // 2, cx + w // 2 + 1, 3):                   # 塔顶一圈垛口
            px(d, x, top - 1, body)
        for k in range(rh):                                                 # 尖帽子（圆锥顶，比塔宽 2 px，往 lean 歪）
            u = k / (rh - 1)
            hw = (w / 2 + 2) * u
            xc = cx + lean * (1 - u)
            yy = top - 2 - rh + 1 + k
            hl(d, int(round(xc - hw)), int(round(xc + hw)), yy, roof)
            px(d, int(round(xc + hw)), yy, rimc)
        hl(d, cx - w // 2 - 2, cx + w // 2 + 2, top - 2, (60, 22, 84))       # 帽檐
        fx, fy = cx + lean, top - 2 - rh
        vl(d, fx, fy - 4, fy, body)                                         # 小旗
        for k in range(3):
            px(d, fx + 1 + k, fy - 4 + k // 2, (196, 70, 120))
    d.polygon([(176, HZ + 1), (176, 94), (181, 90), (186, 94), (186, HZ + 1)], fill=C((30, 10, 44)))   # 拱门
    for (x, y) in CASTLE_WINS:                                               # 拱窗洞（暗；亮的在 strip）
        rect(d, x, y, x + 1, y + 2, (40, 16, 56))
    # 过山车轨道（左，x 0–60）：一道起伏的双轨 + 一排支架
    for x in range(0, 70):
        y = int(round(78 + 10 * math.sin(x * 0.09 + 0.4) + 4 * math.sin(x * 0.23)))
        px(d, x, y, (96, 40, 118))
        px(d, x, y + 2, (96, 40, 118))
        if x % 7 == 0:
            vl(d, x, y + 3, HZ, (96, 40, 118))
            if x % 14 == 0:
                d.line((x, y + 3, x + 7, HZ), fill=C((96, 40, 118)))
    # 螺旋滑梯塔（右，x 296）
    for y in range(52, HZ + 1):
        hw = 3 + (y - 52) * 0.05
        hl(d, int(296 - hw), int(296 + hw), y, (96, 40, 118))
        if (y // 4) % 2 == 0:
            px(d, int(296 + hw) + 1, y, (150, 80, 164))
            px(d, int(296 - hw) - 1, y + 2, (150, 80, 164))
    d.polygon([(291, 52), (296, 42), (301, 52)], fill=C((96, 40, 118)))
    return P.haze(im, 0.12, (210, 120, 180))


CASTLE_BOX = (148, 58, 200, 94)


def castle_frame(t):
    """城堡的窗（strip）：几扇窗的灯忽明忽暗；中间那扇偶尔亮出一双眼睛。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    tx, ty = CASTLE_WINS[1]                                              # 塔顶那扇窗里像烛火一样每帧闪
    rect(d, tx, ty, tx + 1, ty + 2, (255, 170, 80) if f % 2 else (255, 226, 140))
    for i, (x, y) in enumerate(CASTLE_WINS):
        if i == 1:
            continue
        on = (f + i * 3) % N_ANIM < 5
        if i == 2:
            if f in (3, 4):
                px(d, x, y + 1, (255, 240, 120))
                px(d, x + 1, y + 1, (255, 240, 120))
            continue
        if on:
            rect(d, x, y, x + 1, y + 2, (255, 214, 110) if i % 2 else (255, 190, 90))
            px(d, x, y, (255, 246, 190))
    return im


# ============================================================ 棋盘格地面
@lru_cache(maxsize=1)
def checker_cov():
    """透视棋盘格（y HZ+1 … 179）：每个像素 4×4 超采样算“深格覆盖率”，返回 (覆盖率 H×W, 行号 H×W)。
    行：row = floor(1 / (TD·(y−HZ)))；列：col = floor((x − VPX + 歪) / (TW·(y−HZ)))；
    歪 = 1.6·sin(0.21·(y−HZ) + 1.3)——格子线有一点点扭，像手画的、不太对劲。"""
    ss = 4
    ys = HZ + (np.arange((H - HZ) * ss, dtype=np.float32) + 0.5) / ss
    xs = (np.arange(W * ss, dtype=np.float32) + 0.5) / ss
    yp = np.maximum(ys - HZ, 0.05)[:, None]
    wob = 1.6 * np.sin(0.21 * yp + 1.3)
    row = np.floor(1.0 / (TD * yp))
    col = np.floor((xs[None, :] - VPX + wob) / (TW * yp))
    chk = ((row + col) % 2).astype(np.float32)
    cov = chk.reshape(H - HZ, ss, W, ss).mean(axis=(1, 3))
    full = np.zeros((H, W), np.float32)
    full[HZ:] = cov
    yc = np.arange(H, dtype=np.float32)[:, None] + 0.5
    rows = np.floor(1.0 / (TD * np.maximum(yc - HZ, 0.05))).repeat(W, 1)
    return full, rows


CHECKER_DARK_Y = (135, 177)   # 地图 dream_ch6 的可走带（游玩脚本：135–177；危险区只取落在这里面的深格）


def checker_dark_rects(y0=CHECKER_DARK_Y[0], y1=CHECKER_DARK_Y[1], min_w=4):
    """可走带（y y0 … y1）里每个深格的近似矩形 [[x0, y0, x1, y1], ...]（x1 / y1 不含：宽 = x1 − x0），从远到近、从左到右。
    2026-10-19 第三轮加（素材总表 §一.2）：第6章梦二（6-14）的棋盘陷阱直接循环这个列表、对齐画面上的透视格，
    原来剧情是自己摆 8 个方块，和地上的格子对不上。
    算法和 checker_cov 是同一个公式（行 = floor(1/(TD·(y−HZ)))、列 = floor((x − VPX + 歪)/(TW·(y−HZ)))、
    歪 = 1.6·sin(0.21·(y−HZ) + 1.3)、(行 + 列) 为奇数 = 深格），按像素中心取样：
    同一个深格（行号、列号都相同）在每一行像素上有一段 [左, 右]；透视格是梯形，左右边取这几行的中位数（≈ 中间那一行，
    最贴近画面），上下就是这格落在 y0 … y1 里的那几行。宽 < min_w 的碎格（画面两头被切掉的）丢掉。"""
    xs = np.arange(W, dtype=np.float64) + 0.5
    cells = {}
    for y in range(y0, y1 + 1):
        yp = max(y + 0.5 - HZ, 0.05)
        wob = 1.6 * math.sin(0.21 * yp + 1.3)
        row = math.floor(1.0 / (TD * yp))
        col = np.floor((xs - VPX + wob) / (TW * yp)).astype(int)
        dark = ((row + col) % 2) == 1
        for c in np.unique(col[dark]):
            sel = np.nonzero(dark & (col == c))[0]
            cells.setdefault((row, int(c)), {})[y] = (int(sel.min()), int(sel.max()))
    out = []
    for (row, c), per in cells.items():
        ys = sorted(per)
        lx = int(round(float(np.median([per[y][0] for y in ys]))))
        rx = int(round(float(np.median([per[y][1] for y in ys])))) + 1
        if rx - lx < min_w:
            continue
        out.append([lx, ys[0], rx, ys[-1] + 1])
    out.sort(key=lambda r: (r[1], r[0]))
    return out


def floor_rows():
    """可走带里每一行格子的上下分界 y（给剧情：陷阱格 / 站位按这个对齐）。"""
    out = []
    prev = None
    for y in range(HZ + 1, H):
        r = math.floor(1.0 / (TD * (y + 0.5 - HZ)))
        if prev is not None and r != prev and y >= WALK[0] - 6:
            out.append(y)
        prev = r
    return out


@lru_cache(maxsize=1)
def floor_img():
    """棋盘格地面：覆盖率分 4 档按 Bayer 抖成浅 / 深两色之间（远处自然糊成一片中间色）、离地平线近的几行往粉雾混；
    地平线一道亮线；最后把东西投在地上的影压上去（木马台子、摩天轮脚、糖果摊、帐篷、路灯）。"""
    cov, rows = checker_cov()
    levels = 4
    thr = A._bayer(W, H)
    q = cov * levels
    lv = (np.floor(q) + ((q - np.floor(q)) > thr)) / levels
    c1, c2 = np.array(FLOOR_L, np.float32), np.array(FLOOR_D, np.float32)
    col = c1 + (c2 - c1) * lv[..., None]
    ry = np.arange(H, dtype=np.float32)[:, None] - HZ
    fog = np.clip(1.0 - ry / 22.0, 0, 1) ** 1.2
    fm = np.broadcast_to(fog, (H, W)) > thr * 0.95
    col[fm] = col[fm] * 0.45 + np.array(FOG, np.float32) * 0.55
    a = np.zeros((H, W, 4), np.uint8)
    a[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    a[HZ:, :, 3] = 255
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    hl(d, 0, W - 1, HZ, (255, 214, 226))
    hl(d, 0, W - 1, HZ + 1, (246, 190, 214))
    # 东西投在地上的影（往右下，灯光 / 月光从左上）
    for (a0, b0, y0, y1, dx) in ((14, 98, CAR_BASE - 2, CAR_BASE + 4, 8), (70, 128, 134, 139, 6), (STALL[0], STALL[1], 136, 141, 6),
                                 (TENT[0] + 4, TENT[1], TENT_BASE, TENT_BASE + 5, 7)):
        cast_shadow(im, [(a0 + 4, y0), (b0, y0), (b0 + dx, y1), (a0 + 4 + dx, y1)], mul=SOFT_MUL)
    for x in LAMPS:
        cast_shadow(im, [(x + 1, 137), (x + 3, 137), (x + 9, 141), (x + 7, 141)], mul=SOFT_MUL)
    return im


TRAP_BOX = (0, WALK[0], W, H)


def trap_frame(t):
    """陷阱（strip，key checker）：可走带里的深格亮起紫光，一波一波从远往近推（按格子的行号错开相位），
    亮的时候格子中间发白、四周一圈亮紫；浅格不动。分 4 档颜色（帧条好压缩）。"""
    cov, rows = checker_cov()
    f = fidx(t, FPS_ANIM, N_ANIM)
    a = np.zeros((H, W, 4), np.uint8)
    dark = cov > 0.5
    ph = (f / N_ANIM - rows * 0.18) % 1.0
    b = np.clip(np.cos(ph * math.tau) * 0.5 + 0.5, 0, 1)
    bq = np.floor(b * 3.999) / 3.0
    base = np.array((86, 30, 120), np.float32)
    glow = np.array((214, 120, 255), np.float32)
    col = base + (glow - base) * bq[..., None]
    edge = dark & ~(np.roll(dark, 1, 0) & np.roll(dark, -1, 0) & np.roll(dark, 1, 1) & np.roll(dark, -1, 1))
    col[edge] = np.minimum(255, col[edge] + 40)
    m = dark.copy()
    m[:TRAP_BOX[1]] = False
    a[m, :3] = np.clip(col[m], 0, 255).astype(np.uint8)
    a[m, 3] = 255
    return Image.fromarray(a, 'RGBA')


# ============================================================ 摩天轮（转动的部分）
WHEEL_BOX = (WHEEL[0] - WHEEL[2] - 8, WHEEL[1] - WHEEL[2] - 6, WHEEL[0] + WHEEL[2] + 9, WHEEL[1] + WHEEL[2] + 14)


def ferris_frame(t):
    """摩天轮（strip，16 帧 @4 fps）：两道轮圈（粉紫 + 描边）、8 根辐条、16 颗灯泡（每 4 颗亮一颗，追着跑）、
    8 个吊厢（粉 / 黄相间，挂钩在轮圈上、厢体一直往下垂）。16 帧转 90°（吊厢颜色两个一循环，所以首尾接得上）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_WHEEL)
    cx, cy, R = WHEEL
    ang0 = f / N_WHEEL * (math.pi / 2)
    for k in range(8):                                                   # 辐条
        a = ang0 + k * math.pi / 4
        d.line((cx, cy, round(cx + math.cos(a) * R), round(cy + math.sin(a) * R)), fill=C((150, 86, 176)))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=C(INK), width=1)
    d.ellipse((cx - R + 1, cy - R + 1, cx + R - 1, cy + R - 1), outline=C((222, 124, 214)), width=2)
    d.ellipse((cx - R + 7, cy - R + 7, cx + R - 7, cy + R - 7), outline=C((160, 90, 186)), width=1)
    for k in range(16):                                                  # 灯泡
        a = ang0 + k * math.pi / 8
        on = (k + f) % 4 == 0
        x, y = round(cx + math.cos(a) * R), round(cy + math.sin(a) * R)
        px(d, x, y, (255, 250, 190) if on else (200, 130, 160))
        if on:
            for (ox, oy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                px(d, x + ox, y + oy, (255, 200, 120))
    gcols = [(246, 90, 140), (255, 214, 90)]
    for k in range(8):                                                   # 吊厢
        a = ang0 + k * math.pi / 4 + math.pi / 8
        gx, gy = round(cx + math.cos(a) * R), round(cy + math.sin(a) * R)
        c = gcols[k % 2]
        vl(d, gx, gy, gy + 2, INK)
        d.rounded_rectangle((gx - 4, gy + 3, gx + 4, gy + 10), radius=2, fill=C(c), outline=C(INK))
        hl(d, gx - 3, gx + 3, gy + 4, lt(c, 0.4))                         # 顶篷
        rect(d, gx - 2, gy + 6, gx + 2, gy + 7, mix(c, INK, 0.55))        # 窗
        px(d, gx - 3, gy + 9, dk(c, 0.7))
    return im


# ============================================================ 近景：零件
def stripes_fill(d, pts_fn, x0, x1, y0, y1, c1, c2, w=4, inside=None):
    for x in range(x0, x1 + 1):
        c = c1 if ((x - x0) // w) % 2 == 0 else c2
        for y in range(y0, y1 + 1):
            if inside is None or inside(x, y):
                px(d, x, y, c)


def scallops(d, x0, x1, y, cols, w=6, depth=4, outline=INK):
    """扇贝形垂边：一个个半圆往下垂，颜色轮着换，外面描一圈墨线。"""
    k = 0
    for xa in range(x0, x1, w):
        c = cols[k % len(cols)]
        for x in range(xa, min(x1, xa + w)):
            u = (x - xa + 0.5) / w * 2 - 1
            hh = int(round(depth * math.sqrt(max(0.0, 1 - u * u))))
            vl(d, x, y, y + hh, c)
            px(d, x, y + hh + 1, outline)
        k += 1


def lamp_post(im, x, top=98):
    """老式路灯：深紫的铸铁杆（底座 + 两道箍）、一颗圆灯罩（亮）、灯周围一圈隔点抖出来的光。"""
    d = ImageDraw.Draw(im)
    bay = A._bayer(W, H)
    for y in range(top - 9, top + 10):
        for xx in range(x - 9, x + 10):
            r = math.hypot(xx - x, (y - top) * 1.1)
            if 3 < r < 9 and 0 <= xx < W and bay[y, xx] < 0.55 - r * 0.05:
                c = im.getpixel((xx, y))
                if c[3] == 0:
                    px(d, xx, y, (255, 220, 170))
    vl(d, x, top + 3, 137, (60, 30, 80))
    vl(d, x + 1, top + 3, 137, (40, 18, 56))
    rect(d, x - 2, 135, x + 3, 138, (60, 30, 80))
    for y in (110, 124):
        hl(d, x - 1, x + 2, y, (110, 70, 130))
    d.ellipse((x - 3, top - 3, x + 3, top + 3), fill=C((255, 240, 196)), outline=C((60, 30, 80)))
    px(d, x - 1, top - 1, (255, 255, 240))
    hl(d, x - 2, x + 3, top - 4, (60, 30, 80))


def draw_wheel_frame(im):
    """摩天轮不动的部分（在转动的轮子前面）：A 字架（两根斜腿 + 一道横梁）、轮毂（金 + 粉），脚下的售票亭
    （条纹顶、一扇小窗、亭顶一张笑得太宽的小丑脸）。"""
    d = ImageDraw.Draw(im)
    cx, cy, R = WHEEL
    for sx in (-26, 26):
        d.line((cx, cy, cx + sx, 136), fill=C(INK), width=4)
        d.line((cx, cy, cx + sx, 136), fill=C((150, 90, 176)), width=2)
        d.line((cx + (1 if sx > 0 else -1), cy + 2, cx + sx + (1 if sx > 0 else -1), 136), fill=C((196, 140, 214)))
    d.line((cx - 20, 120, cx + 20, 120), fill=C(INK), width=3)
    d.line((cx - 20, 120, cx + 20, 120), fill=C((150, 90, 176)), width=1)
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=C(GOLD), outline=C(INK))
    d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=C(PINK))
    px(d, cx - 3, cy - 3, (255, 240, 180))
    # 售票亭（摩天轮右脚边）
    bx0, bx1 = 112, 130
    rect(d, bx0, 112, bx1, 138, (240, 222, 240))
    for x in range(bx0, bx1 + 1, 4):
        vl(d, x, 112, 138, (196, 120, 200))
    rect(d, bx0 + 3, 118, bx1 - 3, 126, (60, 24, 76))
    hl(d, bx0 + 3, bx1 - 3, 118, (40, 14, 56))
    px(d, bx0 + 6, 121, (255, 220, 120))                               # 窗里一盏小灯
    hl(d, bx0 - 1, bx1 + 1, 127, GOLD)
    d.rectangle((bx0, 112, bx1, 138), outline=C(INK))
    for k in range(5):                                                   # 条纹顶
        hl(d, bx0 - 2 + k // 2, bx1 + 2 - k // 2, 111 - k, PINK if k % 2 == 0 else CREAM)
    hl(d, bx0, bx1, 106, INK)
    fx, fy = (bx0 + bx1) // 2, 101                                       # 小丑脸
    d.ellipse((fx - 6, fy - 5, fx + 6, fy + 5), fill=C((250, 244, 240)), outline=C(INK))
    px(d, fx - 3, fy - 2, INK)
    px(d, fx + 2, fy - 2, INK)
    d.ellipse((fx - 1, fy - 1, fx + 1, fy + 1), fill=C((230, 40, 60)))
    d.arc((fx - 5, fy - 2, fx + 5, fy + 4), 10, 170, fill=C((200, 30, 50)))   # 笑得太宽的嘴
    px(d, fx - 5, fy + 1, (200, 30, 50))
    px(d, fx + 5, fy + 1, (200, 30, 50))
    for (ox, c) in ((-7, (90, 200, 240)), (7, (120, 220, 140))):        # 两撮彩色头发
        d.ellipse((fx + ox - 2, fy - 4, fx + ox + 2, fy), fill=C(c), outline=C(INK))


def carousel_roof(d):
    """旋转木马的顶：红白放射条纹的尖顶（顶上一颗金球 + 小旗杆）、金色饰边、扇贝垂边。灯泡在 lights strip 里。"""
    cx, x0, x1 = CAROUSEL
    top, eave = 66, 90
    for y in range(top, eave + 1):
        u = (y - top) / (eave - top)
        hw = 4 + (x1 - x0) / 2 * u ** 0.9
        for x in range(int(cx - hw), int(cx + hw) + 1):
            k = int(((x - cx) / max(1, hw)) * 5 + 5)
            c = PINK if k % 2 == 0 else CREAM
            if y > eave - 2:
                c = dk(c, 0.86)
            px(d, x, y, c)
        px(d, int(cx - hw), y, INK)
        px(d, int(cx + hw), y, INK)
    d.ellipse((cx - 3, top - 6, cx + 3, top), fill=C(GOLD), outline=C(INK))
    vl(d, cx, top - 12, top - 6, INK)
    for k in range(4):
        px(d, cx + 1 + k, top - 12 + k // 2, (90, 200, 240))
    hl(d, x0 - 1, x1 + 1, eave + 1, GOLD)                               # 金饰边
    hl(d, x0 - 1, x1 + 1, eave + 2, GOLD_D)
    hl(d, x0 - 1, x1 + 1, eave + 3, INK)
    scallops(d, x0, x1 + 1, eave + 4, (PINK, CREAM, (90, 200, 240)), w=7, depth=4)


def carousel_column(d):
    """中柱：镜面板（一格格亮紫 / 白）+ 金箍。"""
    cx = CAROUSEL[0]
    rect(d, cx - 5, 98, cx + 5, 130, (150, 90, 186))
    for y in range(100, 128, 6):
        rect(d, cx - 4, y, cx + 4, y + 4, (220, 200, 246))
        px(d, cx - 3, y + 1, (255, 255, 255))
        vl(d, cx + 4, y, y + 4, (150, 120, 200))
    for y in (98, 129):
        hl(d, cx - 6, cx + 6, y, GOLD)
    vl(d, cx - 6, 98, 130, INK)
    vl(d, cx + 6, 98, 130, INK)


def draw_carousel(im):
    """旋转木马不动的部分：顶、中柱、圆台子（正面一圈彩色面板 + 金边 + 底下暗）。木马和铜杆在 horses strip 里。"""
    d = ImageDraw.Draw(im)
    cx, x0, x1 = CAROUSEL
    carousel_roof(d)
    carousel_column(d)
    d = ImageDraw.Draw(im)
    rect(d, x0 - 2, 128, x1 + 2, CAR_BASE, (120, 56, 140))              # 台子
    hl(d, x0 - 2, x1 + 2, 128, GOLD)
    hl(d, x0 - 2, x1 + 2, 129, (230, 170, 230))
    for k, x in enumerate(range(x0 + 2, x1, 12)):                      # 面板
        rect(d, x, 131, x + 8, 136, CANDY[k % len(CANDY)])
        hl(d, x, x + 8, 131, lt(CANDY[k % len(CANDY)], 0.4))
        d.rectangle((x, 131, x + 8, 136), outline=C(INK))
    hl(d, x0 - 2, x1 + 2, CAR_BASE, INK)
    vl(d, x0 - 2, 128, CAR_BASE, INK)
    vl(d, x1 + 2, 128, CAR_BASE, INK)


_HORSE = """
....kkk.............
...kmmmk............
..kbbmmmk...........
.kbrbbmmk...........
kbbbbbbmk...........
kbbkbbbbmk..........
.kk.kbbbbkkkkkkkk...
.....kbbbbbggbbbbk..
.....kbbbbbggbbbbbkk
.....ksssssssssssbkm
....kbbk.....kbbsk.m
...kbbk.......kbbk..
...kbk.........kbbk.
...khk..........khk.
"""


@lru_cache(maxsize=8)
def horse_img(col, face):
    """木马（20×14，像素格手画：弓起来的脖子 + 鬃毛、往下压的马头、红点眼睛（不对劲）、金马鞍、前腿收、后腿蹬、尾巴）。
    face 1 = 朝左。col = (身子, 鬃毛)。"""
    body, mane = col
    pal = {'k': INK, 'b': body, 's': dk(body, 0.8), 'm': mane, 'g': GOLD, 'r': (230, 30, 40), 'h': (60, 30, 50)}
    im = A._grid(_HORSE, pal)
    return im if face > 0 else im.transpose(Image.FLIP_LEFT_RIGHT)


HORSES = [(26, 0, ((250, 246, 240), (246, 120, 170)), 1, False), (42, 2, ((200, 150, 240), (255, 220, 90)), -1, True),
          (70, 5, ((150, 220, 240), (240, 90, 140)), 1, True), (56, 3, ((255, 200, 120), (130, 90, 200)), 1, False),
          (86, 6, ((250, 170, 200), (90, 200, 160)), -1, False)]          # (x, 相位, 颜色, 朝向, 后排)
HORSE_BOX = (CAROUSEL[1] - 2, 94, CAROUSEL[2] + 3, 131)   # 含中柱底下那道金箍（y 129–130）


def horses_frame(t):
    """木马（strip）：后排两匹（暗一点）→ 中柱（盖在后排前面）→ 前排三匹；每匹骑在一根铜杆上，一上一下 3 px
    （相位错开），铜杆从顶到台子。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    for back in (True, False):
        for (x, ph, col, face, is_back) in HORSES:
            if is_back != back:
                continue
            dy = round(3 * math.sin(math.tau * (f + ph) / N_ANIM))
            pole_c = (220, 180, 90) if not back else (170, 130, 80)
            vl(d, x, 94, 128, pole_c)
            px(d, x, 94 + (f + ph) % 8 * 4, (255, 240, 170))              # 铜杆上一点反光往下溜
            c = col if not back else (dk(col[0], 0.78), dk(col[1], 0.78))
            paste(im, horse_img(c, face), x - 10, 106 + dy)
        if back:
            carousel_column(d)
    return im


def draw_stall(im):
    """糖果摊：粉白竖条的亭子、柜台、一排糖果罐（彩色糖豆）、一架棉花糖、扇贝遮阳篷（两根彩杆）、亭顶两根螺旋大棒棒糖、
    一颗包糖纸的大糖果招牌。"""
    d = ImageDraw.Draw(im)
    x0, x1 = STALL
    for x in range(x0, x1 + 1):                                          # 亭身
        c = (250, 160, 196) if ((x - x0) // 5) % 2 == 0 else (255, 244, 248)
        vl(d, x, 118, 138, c)
    d.rectangle((x0, 118, x1, 138), outline=C(INK))
    rect(d, x0 - 2, 116, x1 + 2, 118, (150, 90, 186))                   # 柜台面
    hl(d, x0 - 2, x1 + 2, 116, (210, 160, 236))
    hl(d, x0 - 2, x1 + 2, 119, INK)
    for k, x in enumerate(range(x0 + 4, x1 - 6, 9)):                    # 糖果罐
        d.rounded_rectangle((x, 106, x + 6, 115), radius=2, fill=C((230, 236, 250)), outline=C(INK))
        for j in range(7):
            px(d, x + 1 + j % 5, 109 + j // 3 + (j % 2), CANDY[(k + j) % len(CANDY)])
        rect(d, x + 1, 104, x + 5, 105, CANDY[(k + 3) % len(CANDY)])
        px(d, x + 1, 107, (255, 255, 255))
    for k in range(3):                                                   # 棉花糖架
        cx = x1 - 4 - k * 4
        vl(d, cx, 104, 113, (240, 230, 200))
        d.ellipse((cx - 2, 99 - k, cx + 2, 104 - k), fill=C((255, 190, 226) if k % 2 == 0 else (200, 200, 255)))
    for (px_, lean) in ((x0 + 1, 0), (x1 - 1, 0)):                       # 两根彩杆
        for y in range(92, 138):
            c = (255, 250, 245) if (y // 3) % 2 else (240, 70, 110)
            px(d, px_, y, c)
    for y in range(90, 99):                                              # 遮阳篷（往下斜）
        u = (y - 90) / 8
        for x in range(x0 - 4, x1 + 5):
            c = PINK if ((x - x0 + 2) // 6) % 2 == 0 else CREAM
            px(d, x, y, c if u < 0.85 else dk(c, 0.84))
    hl(d, x0 - 4, x1 + 4, 89, INK)
    scallops(d, x0 - 4, x1 + 5, 99, (PINK, CREAM), w=6, depth=3)
    for (cx, cy, r, cols) in ((x0 + 8, 76, 7, ((246, 80, 130), (255, 246, 250))), (x1 - 8, 72, 8, ((90, 200, 240), (255, 246, 250)))):
        vl(d, cx, cy + r, 89, (250, 244, 230))                           # 大棒棒糖（螺旋）
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                dd = math.hypot(xx - cx, yy - cy)
                if dd <= r:
                    a = math.atan2(yy - cy, xx - cx)
                    k = int((dd * 0.9 + a / math.tau * 6) % 2)
                    px(d, xx, yy, cols[k])
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=C(INK))
    sx, sy = (x0 + x1) // 2, 82                                          # 包糖纸的大糖果招牌
    d.ellipse((sx - 8, sy - 5, sx + 8, sy + 5), fill=C((255, 214, 80)), outline=C(INK))
    d.polygon([(sx - 8, sy), (sx - 14, sy - 5), (sx - 14, sy + 5)], fill=C((255, 160, 200)), outline=C(INK))
    d.polygon([(sx + 8, sy), (sx + 14, sy - 5), (sx + 14, sy + 5)], fill=C((255, 160, 200)), outline=C(INK))
    for k in range(-6, 7, 3):
        d.line((sx + k, sy - 4, sx + k + 2, sy + 4), fill=C((240, 120, 60)))
    vl(d, sx, sy + 6, 89, INK)


def draw_tent(im):
    """马戏帐篷：放射条纹的顶（粉 / 黄）、扇贝垂边、蓝绿白竖条的围墙、掀开的门帘、黑洞洞的门里（眼睛在 strip 里）、
    顶上旗杆、两根彩杆拉着两串三角旗。"""
    lay = A._new(W, H)
    d = ImageDraw.Draw(lay)
    x0, x1 = TENT
    ax, ay = TENT_PEAK
    eave = 100
    rect(d, x0 + 4, eave, x1 - 4, TENT_BASE, (244, 232, 246))            # 围墙
    for x in range(x0 + 4, x1 - 4, 8):
        rect(d, x, eave, x + 3, TENT_BASE, TEAL)
    n = 10
    for i in range(n):                                                    # 顶
        a = x0 + (x1 - x0) * i / n
        b = x0 + (x1 - x0) * (i + 1) / n
        d.polygon([(ax, ay), (a, eave + 2), (b, eave + 2)], fill=C(PINK if i % 2 == 0 else (255, 226, 120)))
    lay = P.outline(lay, INK)
    d = ImageDraw.Draw(lay)
    scallops(d, x0 + 1, x1, eave + 2, (PINK, (255, 226, 120)), w=7, depth=4)
    d.polygon([(ax - 11, TENT_BASE), (ax, 108), (ax + 11, TENT_BASE)], fill=C((36, 12, 52)))   # 门里
    d.polygon([(ax - 11, TENT_BASE), (ax, 108), (ax - 6, TENT_BASE)], fill=C(PINK))          # 掀开的门帘
    d.polygon([(ax + 11, TENT_BASE), (ax, 108), (ax + 6, TENT_BASE)], fill=C(PINK))
    d.line((ax - 11, TENT_BASE, ax, 108), fill=C(INK))
    d.line((ax + 11, TENT_BASE, ax, 108), fill=C(INK))
    for (x, y) in ((ax - 8, 124), (ax + 8, 124)):                         # 门帘的绑带
        px(d, x, y, GOLD)
        px(d, x, y + 1, GOLD)
    hl(d, x0 + 4, x1 - 4, TENT_BASE, INK)
    vl(d, ax, ay - 12, ay, INK)                                            # 旗杆
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    for (px_, top) in ((216, 96), (314, 98)):                              # 两根彩杆 + 三角旗
        for y in range(top, 138):
            c = (255, 250, 245) if (y // 3) % 2 else (90, 200, 240)
            px(d, px_, y, c)
        d.ellipse((px_ - 2, top - 4, px_ + 2, top), fill=C(GOLD), outline=C(INK))
    for (bx, by) in ((216, 96), (314, 98)):
        pts = P.V.garland_pts(ax, ay + 2, bx, by, 6)
        d.line([(round(x), round(y)) for (x, y) in pts], fill=C(INK))
        for k in range(2, len(pts) - 2, 4):
            x, y = pts[k]
            c = CANDY[(k // 4) % len(CANDY)]
            d.polygon([(round(x) - 2, round(y)), (round(x) + 2, round(y)), (round(x), round(y) + 4)], fill=C(c))


def draw_fences(im):
    """几段红绳围栏（金色矮柱 + 往下垂的红绳），只在可走带后沿的空当里。"""
    d = ImageDraw.Draw(im)
    for (a, b) in ((134, 144), (208, 224)):
        posts = list(range(a, b + 1, 8))
        for x in posts:
            rect(d, x, 131, x + 1, 139, GOLD)
            px(d, x, 130, (255, 240, 170))
            px(d, x + 1, 139, GOLD_D)
        for (p0, p1) in zip(posts, posts[1:]):
            for x in range(p0 + 2, p1):
                u = (x - p0) / (p1 - p0)
                px(d, x, 132 + round(2 * math.sin(u * math.pi)), (210, 40, 60))


def draw_toys(im):
    """可走带后沿散着的玩具：歪倒的泰迪熊（一只眼睛是 X 形缝线、肚子上一道缝线）、两块写着 1 / 3 的积木、
    一只小陀螺、一个开着盖的小丑盒子（弹簧上的小丑头）。都画在 y ≤ 139（可走带外）。"""
    d = ImageDraw.Draw(im)
    bx, by = 132, 139                                                       # 泰迪熊（坐着往左歪）
    bear, bear_d = (196, 140, 96), (150, 100, 66)
    d.ellipse((bx - 6, by - 9, bx + 2, by), fill=C(bear), outline=C(INK))   # 身子
    d.ellipse((bx - 9, by - 15, bx - 1, by - 8), fill=C(bear), outline=C(INK))   # 头
    for (ex, ey) in ((bx - 9, by - 15), (bx - 3, by - 16)):                 # 耳朵
        d.ellipse((ex - 1, ey - 1, ex + 2, ey + 2), fill=C(bear_d), outline=C(INK))
    px(d, bx - 7, by - 12, INK)                                             # 一只眼睛
    for (x, y) in ((bx - 4, by - 13), (bx - 2, by - 11), (bx - 2, by - 13), (bx - 4, by - 11), (bx - 3, by - 12)):   # X 形缝线眼睛
        px(d, x, y, INK)
    px(d, bx - 5, by - 10, (60, 30, 30))
    for y in range(by - 7, by - 1, 2):                                      # 肚子上的缝线
        px(d, bx - 2, y, (90, 40, 40))
    d.ellipse((bx - 1, by - 3, bx + 4, by), fill=C(bear_d), outline=C(INK))   # 伸出来的脚
    for (x, ch, col) in ((216, '1', (90, 200, 240)), (226, '3', (255, 214, 80))):    # 积木 1 / 3
        rect(d, x, 131, x + 7, 138, col)
        d.rectangle((x, 131, x + 7, 138), outline=C(INK))
        hl(d, x + 1, x + 6, 132, lt(col, 0.4))
        if ch == '1':
            vl(d, x + 4, 133, 137, INK)
            px(d, x + 3, 134, INK)
        else:
            hl(d, x + 2, x + 5, 133, INK)
            px(d, x + 5, 134, INK)
            hl(d, x + 3, x + 5, 135, INK)
            px(d, x + 5, 136, INK)
            hl(d, x + 2, x + 5, 137, INK)
    tx, ty = 8, 139                                                         # 陀螺（倒在地上）
    d.polygon([(tx, ty - 4), (tx + 8, ty - 6), (tx + 9, ty - 1), (tx + 1, ty)], fill=C((240, 70, 110)), outline=C(INK))
    hl(d, tx + 2, tx + 7, ty - 3, (255, 214, 80))
    px(d, tx + 10, ty - 3, INK)
    jx, jy = 304, 139                                                       # 小丑盒子
    rect(d, jx, jy - 7, jx + 8, jy, (120, 220, 140))
    d.rectangle((jx, jy - 7, jx + 8, jy), outline=C(INK))
    d.line((jx, jy - 7, jx - 4, jy - 11), fill=C(INK))                       # 掀开的盖
    for k in range(4):                                                      # 弹簧
        px(d, jx + 4 + (1 if k % 2 else -1), jy - 8 - k, (200, 200, 210))
    d.ellipse((jx + 1, jy - 17, jx + 7, jy - 11), fill=C((250, 244, 240)), outline=C(INK))
    px(d, jx + 3, jy - 15, INK)
    px(d, jx + 5, jy - 15, INK)
    px(d, jx + 4, jy - 13, (230, 40, 60))
    d.polygon([(jx + 1, jy - 17), (jx + 4, jy - 22), (jx + 7, jy - 17)], fill=C((240, 70, 110)), outline=C(INK))


@lru_cache(maxsize=1)
def near_img():
    """近景：摩天轮架子 + 售票亭、旋转木马、糖果摊、帐篷、路灯、围栏、玩具（只有 0 / 255 透明度，地面在 floor 层）。"""
    im = A._new(W, H)
    draw_wheel_frame(im)
    draw_carousel(im)
    draw_stall(im)
    draw_tent(im)
    for x in LAMPS:
        lamp_post(im, x)
    draw_fences(im)
    draw_toys(im)
    im = A._grade(im, sat=1.0, val=1.0)
    return opaque(im)


# ============================================================ 会动的：气球 / 彩灯 / 旗
BALLOONS = [(198, 62, (246, 80, 130)), (206, 56, (255, 214, 80)), (214, 64, (90, 200, 240)), (203, 72, (120, 220, 140)),
            (212, 74, (200, 120, 240))]
BALLOON_KNOT = (205, 104)
BALLOON_BOX = (190, 46, 224, 106)


def balloons_frame(t):
    """糖果摊右边柱子上拴着的一串气球（strip）：每只上下浮 1–2 px、左右晃，线都收到柱子上的结；气球上一点高光，
    有一只是笑脸（画得有点歪）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    kx, ky = BALLOON_KNOT
    pos = []
    for i, (x, y, c) in enumerate(BALLOONS):
        ph = math.tau * f / N_ANIM + i * 1.3
        bx, by = x + round(math.sin(ph) * 1.2), y + round(math.sin(ph + 0.8) * 1.6)
        pos.append((bx, by, c, i))
    for (bx, by, c, i) in pos:                                             # 线（先画）
        d.line((bx, by + 6, kx, ky), fill=C((250, 240, 255)))
    for (bx, by, c, i) in pos:
        d.ellipse((bx - 4, by - 5, bx + 4, by + 5), fill=C(c), outline=C(INK))
        px(d, bx - 2, by - 3, lt(c, 0.6))
        px(d, bx, by + 6, dk(c, 0.7))
        if i == 1:                                                        # 笑脸气球
            px(d, bx - 2, by - 1, INK)
            px(d, bx + 1, by - 2, INK)
            d.arc((bx - 3, by - 1, bx + 2, by + 3), 20, 160, fill=C(INK))
    return im


def festoon(x0, y0, x1, y1, sag, step=4):
    pts = P.V.garland_pts(x0, y0, x1, y1, sag)
    return [(round(x), round(y)) for (x, y) in pts[::step]]


FESTOONS = [festoon(CAROUSEL[0], 60, 132, 92, 10), festoon(132, 92, 214, 92, 9), festoon(214, 92, 265, 58, 4)]
LIGHT_BOXES = [('lights_a', (54, 58, 136, 106)), ('lights_b', (128, 88, 218, 106)), ('lights_c', (210, 54, 268, 98)),
               ('lights_car', (CAROUSEL[1] - 2, 96, CAROUSEL[2] + 4, 101)), ('lights_tent', (TENT[0], 105, TENT[1] + 1, 110)),
               ('lights_eyes', (TENT_PEAK[0] - 4, 118, TENT_PEAK[0] + 5, 123))]


def lights_frame(t):
    """彩灯（strip）：三串彩灯（每 4 颗亮一组、追着跑）+ 木马顶垂边下的一圈灯泡（隔一个亮）+ 帐篷垂边下的跑马灯 +
    帐篷门里一双眼睛（大部分时间睁着，眨一下）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    for j, pts in enumerate(FESTOONS):
        d.line(pts, fill=C(INK))
        for k, (x, y) in enumerate(pts[1:-1]):
            c = CANDY[(k + j) % len(CANDY)]
            on = (k + f + j) % 4 != 0
            px(d, x, y + 1, c if on else dk(c, 0.45))
            if on and (k + f) % 4 == 1:
                px(d, x, y + 2, lt(c, 0.5))
    cx, x0, x1 = CAROUSEL
    for k, x in enumerate(range(x0 + 1, x1 + 1, 4)):
        on = (k + f) % 2 == 0
        px(d, x, 98, (255, 246, 180) if on else (170, 120, 90))
        if on:
            px(d, x, 99, (255, 200, 120))
    for k, x in enumerate(range(TENT[0] + 3, TENT[1] - 2, 5)):
        on = (k - f) % 3 == 0
        px(d, x, 107, (255, 250, 200) if on else (190, 120, 140))
        if on:
            px(d, x, 108, (255, 190, 120))
    look = (-1, 0, 1, 0, -1, None, 1, 0)[f]                               # 门里的眼睛：左看、右看，眨一下（每帧都不一样）
    ex, ey = TENT_PEAK[0], 120
    for ox in (-3, 2):
        if look is None:
            hl(d, ex + ox, ex + ox + 1, ey + 1, (120, 160, 60))
        else:
            px(d, ex + ox, ey, (220, 255, 120))
            px(d, ex + ox + 1, ey, (220, 255, 120))
            px(d, ex + ox, ey + 1, (150, 200, 60))
            px(d, ex + ox + 1, ey + 1, (150, 200, 60))
            px(d, ex + ox + (1 if look > 0 else 0), ey + 1, (30, 10, 20))
            if look == 0:                                                 # 正看着你：两个像素都是瞳孔
                px(d, ex + ox + 1, ey + 1, (30, 10, 20))
    return im


FLAG_BOX = (TENT_PEAK[0], TENT_PEAK[1] - 14, TENT_PEAK[0] + 10, TENT_PEAK[1] - 6)


def flag_frame(t):
    """帐篷顶的小旗（strip）：绿旗一节节往右飘、像波浪一样抖。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    ax, ay = TENT_PEAK
    for i in range(1, 9):
        y = ay - 12 + round(math.sin(math.tau * f / N_ANIM - i * 0.8) * 1.0)
        hh = 4 - i // 3
        vl(d, ax + i, y, y + hh, (90, 220, 150) if i < 7 else (60, 170, 120))
    return im


STRIPS = [('stars', STAR_BOX, N_ANIM, FPS_ANIM, stars_frame, None),
          ('moon', MOON_BOX, N_ANIM, FPS_ANIM, moon_frame, None)] + \
         [(n, b, N_ANIM, FPS_ANIM, floaters_frame, None) for (n, b) in FLOAT_BOXES] + \
         [('castle', CASTLE_BOX, N_ANIM, FPS_ANIM, castle_frame, None),
          ('trap', TRAP_BOX, N_ANIM, FPS_ANIM, trap_frame, 'checker'),
          ('ferris', WHEEL_BOX, N_WHEEL, FPS_ANIM, ferris_frame, None),
          ('horses', HORSE_BOX, N_ANIM, FPS_ANIM, horses_frame, None),
          ('balloons', BALLOON_BOX, N_ANIM, FPS_ANIM, balloons_frame, None)] + \
         [(n, b, N_ANIM, FPS_ANIM, lights_frame, None) for (n, b) in LIGHT_BOXES] + \
         [('flag', FLAG_BOX, N_ANIM, FPS_ANIM, flag_frame, None)]
DARK_TINT = ('#12061c', 0.55)
# 拼的顺序：天 → 星 / 月 → 云 → 飘的玩具 → 远景 → 城堡窗 → 地面 → 陷阱 → 摩天轮 → 近景 → 木马 / 气球 / 彩灯 / 旗 → dark
ORDER = ['sky', 'stars', 'moon', 'clouds'] + [n for (n, b) in FLOAT_BOXES] + \
        ['far', 'castle', 'floor', 'trap', 'ferris', 'near', 'horses', 'balloons'] + [n for (n, b) in LIGHT_BOXES] + \
        ['flag', 'dark']


@lru_cache(maxsize=1)
def build():
    return dict(sky=sky_img(), far=far_img(), floor=floor_img(), near=near_img())


def compose(camX=0, t=0.5, state=None):
    """直接拼一帧（不经导出），自检 / 预览用。state = {'checker': 1, 'dark': 1}。"""
    st = state or {}
    R = build()
    sm = {n: (b, nn, fps, fn, key) for (n, b, nn, fps, fn, key) in STRIPS}
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for name in ORDER:
        if name in ('sky', 'far', 'floor', 'near'):
            out.alpha_composite(R[name])
        elif name == 'clouds':
            for (w, y, vx, x0, sd) in CLOUDS:
                x = (x0 + t * vx) % CLOUD_SPAN - 100
                paste(out, candy_cloud(w, sd), math.floor(x), y)
        elif name == 'dark':
            if st.get('dark'):
                lay = Image.new('RGBA', (W, H), tuple(int(DARK_TINT[0][i:i + 2], 16) for i in (1, 3, 5)) +
                                (int(255 * DARK_TINT[1]),))
                out.alpha_composite(lay)
        else:
            b, nn, fps, fn, key = sm[name]
            if key and not st.get(key):
                continue
            paste(out, fn(t).crop(b), b[0], b[1])
    return out


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    sm = {n: (b, nn, fps, fn, key) for (n, b, nn, fps, fn, key) in STRIPS}
    layers = []
    for name in ORDER:
        if name == 'sky':
            layers.append(dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0))
        elif name in ('far', 'floor', 'near'):
            im, y = BJ.crop_rows(R[name])
            layers.append(dict(type='static', image=ex.img(name, im), x=0, y=y))
        elif name == 'clouds':
            layers.append(dict(type='clouds', span=CLOUD_SPAN, clouds=[
                dict(image=ex.img('cloud%d' % i, candy_cloud(w, sd)), x0=float(x0), y=y, vx=vx, k=0.0)
                for i, (w, y, vx, x0, sd) in enumerate(CLOUDS)]))
        elif name == 'dark':
            layers.append(dict(type='tint', color=DARK_TINT[0], alpha=DARK_TINT[1], key='dark'))
        else:
            b, nn, fps, fn, key = sm[name]
            layers.append(ex.bake(name, b, nn, fps, fn, screen=True, key=key))
    anchors = dict(ANCHORS)
    anchors.update(wheel_hub=[WHEEL[0], WHEEL[1]], wheel_r=WHEEL[2], moon=[MOON[0], MOON[1]], candy=[175, 150],
                   castle=[180, 74], horizon=HZ, candy_box=[STALL[0] - 4, 64, STALL[1] + 5, 139],
                   tent_box=[TENT[0], TENT_PEAK[1] - 14, TENT[1] + 1, TENT_BASE + 1],
                   carousel_box=[CAROUSEL[1] - 2, 54, CAROUSEL[2] + 3, CAR_BASE + 1],
                   checker=dict(vp=[VPX, HZ], rows=floor_rows(), td=TD, tw=TW,
                                note='row = floor(1/(td·(y−horizon)))，col = floor((x−vp.x)/(tw·(y−horizon)))，(row+col) 为奇数 = 深格'),
                   # 2026-10-19：可走带（y 135–177）里每个深格的近似矩形 [x0, y0, x1, y1]（x1 / y1 不含），陷阱直接循环它
                   checker_dark=checker_dark_rects())
    st = ex.stage(W, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    states = ({}, {'checker': True}, {'dark': True}, {'checker': True, 'dark': True})
    P.check_no_black(ex, BJ, st, [0], (0.0, 0.75, 1.5, 3.25, 9.0), states, '梦里的游乐园')
    ex.checked('天空底图（y 0–101）整片不透明', int((np.array(R['sky'])[..., 3] != 255).sum()))
    fa = np.array(R['floor'])
    ex.checked('棋盘格地面（y 100–180）整片不透明（可走带 140–176 在里面）', int((fa[HZ:, :, 3] != 255).sum()))
    for name in ('near', 'floor', 'far'):
        P.check_alpha01(ex, '%s 层' % name, R[name])
    P.check_strips(ex, BJ, [(n, b, nn, fps, fn) for (n, b, nn, fps, fn, key) in STRIPS])
    P.check_anchor_inside(ex, st['anchors'], W, WALK, ('arrive', 'toys', 'carousel', 'wheel'))
    # 近景（木马 / 摩天轮 / 糖果摊 / 帐篷 / 玩具）不伸进可走带：y 140 以下近景全透明
    na = np.array(R['near'])
    ex.checked('近景的东西都在可走带后沿以外（y ≥ 140 的近景像素）', int((na[WALK[0]:, :, 3] > 0).sum()))
    # 三个玩具箱放的地方只有棋盘格（近景 / 别的 strip 都不在那：y 146–166，x ±12）
    busy = 0
    for (x, y) in TOYS:
        for (n, b, nn, fps, fn, key) in STRIPS:
            if key:
                continue
            if b[0] < x + 12 and b[2] > x - 12 and b[1] < y + 4 and b[3] > y - 16:
                busy += 1
    ex.checked('三个玩具箱放的地方（±12，y 146–166）没有会动的东西压着', busy)
    # 透视棋盘：可走带里一行比一行高（越近越大）
    rows = floor_rows()
    hs = [b - a for a, b in zip(rows, rows[1:])]
    ex.checked('棋盘格行高越往前越大（强透视）', sum(1 for a, b in zip(hs, hs[1:]) if b < a - 1))
    # checker_dark（10-19 加，陷阱直接循环它）：矩形都在图里、宽 ≥ 4、在可走带 135–177 里；每个矩形里大半是深格
    # （透视格是梯形，画面两头的格子斜得厉害，矩形只能近似）；可走带里的深格大部分被盖到；矩形互不重叠
    rects = st['anchors']['checker_dark']
    dark = checker_cov()[0] > 0.5
    cover = np.zeros(dark.shape, bool)
    bad, overlap, fr = 0, 0, []
    for (x0, y0, x1, y1) in rects:
        bad += not (0 <= x0 < x1 <= W and CHECKER_DARK_Y[0] <= y0 < y1 <= CHECKER_DARK_Y[1] + 1 and x1 - x0 >= 4)
        fr.append(float(dark[y0:y1, x0:x1].mean()))
        overlap += int(cover[y0:y1, x0:x1].sum())
        cover[y0:y1, x0:x1] = True
    ex.checked('checker_dark 共 %d 个矩形：都在图里、宽 ≥ 4、在可走带 y %d–%d 里（不满足的个数）' %
               ((len(rects),) + CHECKER_DARK_Y), bad + (0 if rects else 1))
    ex.checked('checker_dark 每个矩形里深格像素 ≥ 60%%（最少 %.0f%%、平均 %.0f%%）' % (min(fr) * 100, np.mean(fr) * 100),
               sum(1 for f in fr if f < 0.6))
    band = dark[CHECKER_DARK_Y[0]:CHECKER_DARK_Y[1] + 1]
    cv = float((band & cover[CHECKER_DARK_Y[0]:CHECKER_DARK_Y[1] + 1]).sum()) / max(1, int(band.sum()))
    ex.checked('可走带里的深格像素 %.0f%% 落在 checker_dark 的矩形里（≥ 80%%）' % (cv * 100), 0 if cv >= 0.8 else 1)
    ex.checked('checker_dark 的矩形互不重叠（重叠的像素）', overlap)
    for t in (0.0, 0.75, 3.25):
        for state in states:
            got = BJ.ref_render(st, ex.images, 0, t, state)
            ex.checked('梦 t=%.2f %s 导出 vs 直接拼' % (t, '+'.join(state) or '平常'), BJ.ndiff(got, compose(0, t, state)))
    nm = P.lum(fa[..., :3].astype(np.float32))
    ex.note('可走带（棋盘格）亮度：y140–176 均值 %.0f 标准差 %.1f；行分界 %s' % (nm[140:177].mean(), nm[140:177].std(), rows))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch6', 'after')
    os.makedirs(od, exist_ok=True)
    for i, state in enumerate(({}, {'checker': 1}, {'dark': 1})):
        compose(0, 0.5, state).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'dream_carnival_solo_%d.png' % i))
    print('ok')
