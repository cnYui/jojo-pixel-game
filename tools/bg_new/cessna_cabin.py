# -*- coding: utf-8 -*-
r"""cessna_cabin —— 第6章「塞斯纳机舱」：飞越阿拉伯沙漠的小飞机，侧剖（机头朝左），白天飞行中。花京院在这里睡着、
进了死神13 的梦；婴儿的篮子放在后排地板上。2026-10-18 ch6-misc 组新画（改前是 later_stages.cessna()：三扇方窗 + 三张木板凳）。

地图 320 宽（单屏）、ground 164、可走带 y 154–172 = 机舱地板（窄窄一条地毯）；侧视，近侧的机身剖开拿掉了，
看得见远侧的舱壁和窗。人物约 30 px 高，所以天花板压在 y 86（站着的人头顶上只剩二十来像素）——舱里窄、低、压迫；
天花板上面是剖开的机身顶（铝蒙皮 + 隔热棉 + 衬板），再上面是一段高单翼的翼根，最上面是天（对白框挡住也不要紧）。
从左到右（世界坐标）：
  x 0–18      机头：白色整流罩（红色饰条、进气口、排气管）、螺旋桨毂（尖锥）和转成一片模糊圆盘的螺旋桨（strip）
  x 12–50     斜的前风挡（剖开的那一半，透明，外面是天 / 地平线下的沙漠）、风挡框、A 柱；风挡上沿挂着一只蓝眼睛护身符（strip 晃）
  x 16–46     仪表板：遮光罩、磁罗盘、六块圆表（空速 / 姿态 / 高度 / 转弯 / 航向 / 升降）、无线电（绿数字）、开关、
              油门 / 混合比拉杆、驾驶盘（盘杆从仪表板伸出来 + 羊角握把）、地板上的方向舵踏板
  x 50–110    驾驶舱：左座（anchors.pilot，乔瑟夫）和右座（anchors.copilot，纵列画成一前一后）——棕色人造革座椅；
              头顶一大扇侧窗（门窗）、门把手、挂在钩子上的耳机（strip 晃）、灭火瓶、地图袋
  x 110–296   客舱：四张朝左的座椅（anchors.seats，两排各两座），三扇圆角舷窗（window_band：外面的云往后飘、
              远处的地平线和沙漠，远侧的机翼撑杆斜着穿过第一扇窗），机身肋骨（一道道竖的隆起）、扶手、烟灰缸、座位口袋、
              垂着的安全带、天花板上的顶灯 / 出风口 / 禁烟牌；后排上面一张行李网（兜着行李袋、相机包、卷起来的毯子、帽子）；
              婴儿篮放在最后两排之间的地板上（anchors.baby，底图那里只有地毯）
  x 298–320   机舱门：圆角门框、门窗、拉杆把手、红色开门杆、铰链
  y 173–180   剖开的机腹（铝蒙皮 + 肋）
光：白天，光从窗外进来（窗边的墙、座椅顶亮），舱里偏暗、偏暖；可走带（地毯）对比压得很低。

图层（从后往前）：
  sky         static           天（上深蓝、地平线 y 114 发白）+ 地平线下面的沙漠（很淡、罩雾）
  desert      wrap   vx −6     地平线下面的沙丘纹（往后退得很慢 = 飞得高）
  clouds_far  wrap   vx −16    远处的云（地平线上下）
  clouds_near wrap   vx −52    近处掠过的碎云（快，看得出在飞）
  night_sky   static key night 夜空（星星、月亮、暗的地平线）
  night_land  wrap   vx −6  key night  夜里的沙漠：远处几点村子的灯
  strut       static           远侧的机翼撑杆（从窗外斜着穿过第一扇窗；跟飞机一起不动）
  cabin       static           机舱（窗、风挡、机身外面是透明洞；近景只有 0 / 255 透明度）
  prop        strip            螺旋桨：模糊圆盘 + 两片桨叶的残影转（8 帧 @8 fps）
  charm       strip            风挡上的护身符 + 钩子上的耳机随气流轻晃（8 帧 @4 fps）
  night_tint  tint   key night 夜航：整屏压暗偏蓝
  night_lights static key night 夜航：顶灯亮了（灯下一圈暖光照在天花板 / 座椅上）、仪表背光、阅读灯
  gauges      strip            仪表指针轻轻抖、无线电的灯闪（8 帧 @4 fps；放在夜航压暗后面，夜里也是亮的）
  alarm_tint  tint   key alarm 警报：整屏泛红
  alarm       strip  key alarm 警报：仪表板上的主警告灯 + 天花板上的红色警灯一闪一闪（8 帧 @4 fps）
锚点：pilot [64,164]、copilot [96,164]、seats [[150,166],[196,166],[242,166],[288,166]]（坐点 = 规格表）、
      baby [270,158]、window_band [110,98,320,126]（规格写的是 [110,62,320,100]：按人物比例窗户放到了头的高度，见交付记录）；
      另导出 walk_x、seat_boxes（每张椅子的框）、seat_cushion_y（坐垫面）、cockpit_seats、windows（每扇窗的框）、door、
      panel、yoke、windshield（多边形）、prop（螺旋桨中心）、ceiling_y、floor_back。
key：alarm（警报灯 strip + 泛红 tint）、night（夜航：窗外夜空 + 舱内灯光）。
单独运行：python -B tools\bg_new\cessna_cabin.py → tools\bg_new\_preview\ch6\after\cessna_cabin_solo_*.png
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
GROUND = 164
WALK = (154, 172)
FLOOR_BACK = 153              # 地毯后沿（舱壁的踢脚板落在这一行）
FLOOR_FRONT = 172             # 地毯前沿（剖面）
CEIL = 86                     # 天花板衬板下沿
HORIZON = 114                 # 窗外地平线
WIN_Y = (98, 126)             # 舷窗（玻璃）上下沿
WINDOWS = [(116, 160), (168, 212), (220, 264)]       # 三扇舷窗（玻璃 x0, x1）
COCK_WIN = (52, 104, 94, 124)                        # 驾驶舱侧窗（门窗）玻璃 x0, x1, y0, y1
DOOR = (299, 318)             # 机舱门
SEATS = [150, 196, 242, 288]
PILOT, COPILOT = 64, 96
CUSHION_Y = 140               # 坐垫面
N_ANIM, FPS_ANIM = 8, 4.0
N_PROP, FPS_PROP = 8, 8.0
PROP_C = (3, 141)             # 螺旋桨毂中心
WS_POLY = [(14, 117), (45, 80), (49, 83), (49, 116)]  # 前风挡（剖开的那一半，透明）
P_SKY_VX = dict(desert=-6.0, clouds_far=-16.0, clouds_near=-52.0, night_land=-6.0)

ANCHORS = dict(
    pilot=[PILOT, 164],        # 左座（乔瑟夫）
    copilot=[COPILOT, 164],    # 右座
    seats=[[s, 166] for s in SEATS],
    baby=[270, 158],           # 婴儿篮（放在后两排之间的地板上，底图这里只有地毯）
    window_band=[110, WIN_Y[0], 320, WIN_Y[1]],
    walk_x=[30, 298],
)

# ============================================================ 调色
SKY_DAY = [(48, 98, 182), (78, 132, 206), (132, 176, 224), (196, 218, 236)]
LAND_DAY = [(222, 206, 180), (210, 188, 156), (196, 168, 128)]
WALL = (184, 170, 148)        # 舱壁（米灰人造革）
WALL_S = (162, 148, 128)
WALL_D = (126, 112, 96)
WALL_HI = (204, 192, 172)
HEADLINER = (206, 196, 176)
SEAT = (130, 80, 56)          # 棕色人造革座椅
SEAT_HI = (166, 110, 76)
SEAT_D = (90, 54, 40)
SEAT_K = (58, 36, 28)
CARPET = (104, 66, 58)
CARPET_S = (94, 58, 52)
CARPET_HI = (114, 74, 64)
ALU = (204, 208, 212)         # 铝蒙皮
ALU_HI = (234, 236, 238)
ALU_D = (150, 156, 164)
ALU_K = (104, 110, 120)
PAINT = (240, 240, 234)       # 外面的白漆
STRIPE = (196, 52, 46)        # 红色饰条
INSUL = (214, 190, 122)       # 隔热棉
PANEL = (58, 60, 66)
PANEL_HI = (92, 96, 104)
PANEL_K = (30, 30, 36)
GAUGE = (20, 20, 24)
INK = (40, 30, 30)


# ============================================================ 机身轮廓
def roof_y(x):
    """机身顶的外轮廓（x 46–320）：中间最高、往机尾慢慢收低一点。"""
    return int(round(76 + ((x - 150) / 170.0) ** 2 * 6))


def ws_x(y):
    """前风挡斜线（外沿）在 y 行的 x：从整流罩顶 (14, 117) 斜到机顶 (45, 80)。"""
    return 14 + (117 - y) * (45 - 14) / (117 - 80)


# ============================================================ 窗外：天 / 沙漠 / 云
@lru_cache(maxsize=1)
def sky_img():
    """白天的天：上深蓝 → 地平线发白；地平线下面是很远很淡的沙漠（罩着雾）。"""
    im = A._new(W, H)
    gradient(im, (0, 0, W, HORIZON), SKY_DAY, bands=10)
    gradient(im, (0, HORIZON, W, H), LAND_DAY, bands=6)
    d = ImageDraw.Draw(im)
    hl(d, 0, W - 1, HORIZON, (236, 238, 236))
    hl(d, 0, W - 1, HORIZON + 1, (226, 218, 200))
    for i in range(6):                                              # 高空卷云（两头尖、中间厚 2 px）
        cx, y, L = hrange(0, W, i, 61), int(hrange(6, 52, i, 62)), int(hrange(26, 60, i, 63))
        for k in range(L):
            u = k / (L - 1)
            th = int(round(2.2 * math.sin(math.pi * u) ** 0.8))
            x = int(cx - L / 2 + k)
            if th <= 0 or not 0 <= x < W:
                continue
            for r in range(th):
                px(d, x, y + r + int(k * 0.06), (226, 236, 248) if r == 0 else (176, 200, 232))
    return im


@lru_cache(maxsize=1)
def desert_img():
    """地平线下面的沙丘纹（640 循环）：一道道弯弯的亮线 / 暗线，越往下（越近）越长、越清楚。"""
    im = A._new(640, H - HORIZON - 2)
    d = ImageDraw.Draw(im)
    for i in range(70):
        y = int((hash01(i, 1) ** 1.4) * (im.height - 2)) + 1
        x = hrange(0, 640, i, 2)
        L = int(4 + 22 * (y / im.height) * hrange(0.5, 1.0, i, 3))
        c = (232, 216, 188) if hash01(i, 4) < 0.5 else (188, 160, 124)
        for k in range(L):
            yy = y + int(round(1.2 * math.sin(k / max(1, L) * math.pi)))
            px(d, int(x + k) % 640, min(im.height - 1, yy), c)
    for i in range(6):                                             # 几块深色的岩石地 / 干河床
        x0 = hrange(0, 640, i, 5)
        y = int(hrange(8, im.height - 4, i, 6))
        for k in range(int(hrange(10, 30, i, 7))):
            px(d, int(x0 + k) % 640, y, (170, 146, 116))
            if k % 3:
                px(d, int(x0 + k + 1) % 640, y + 1, (180, 156, 124))
    return im


def _cloud_layer(seed, n, ymin, ymax, wmin, wmax, pal, flat=0.34):
    im = A._new(640, H)
    for i in range(n):
        w = hrange(wmin, wmax, seed, i, 1)
        cl = A._cloud_sprite(w, w * flat, seed * 10 + i, pal)
        cx = (i + hrange(0.1, 0.9, seed, i, 2)) * 640 / n
        y = int(hrange(ymin, ymax, seed, i, 3))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    return im


@lru_cache(maxsize=1)
def clouds_far_img():
    return _cloud_layer(3, 7, 62, 120, 24, 48, ((252, 252, 252), (236, 240, 246), (210, 222, 236), (190, 204, 224)))


@lru_cache(maxsize=1)
def clouds_near_img():
    return _cloud_layer(7, 4, 84, 132, 30, 56, ((255, 255, 255), (242, 244, 248), (220, 228, 238), (198, 210, 228)), 0.28)


@lru_cache(maxsize=1)
def night_sky_img():
    """夜空：上面深蓝紫、地平线附近一圈淡淡的月光；星星（一部分 2 px 的亮星）、月亮（舷窗 1 里看得见）；
    地平线下面的沙漠只剩一点月光照着的沙丘边。（后面还会罩一层夜航 tint，所以这里画得亮一点）"""
    im = A._new(W, H)
    gradient(im, (0, 0, W, HORIZON), [(20, 26, 70), (34, 42, 96), (64, 72, 128)], bands=8)
    gradient(im, (0, HORIZON, W, H), [(52, 52, 78), (38, 38, 60), (28, 28, 46)], bands=5)
    d = ImageDraw.Draw(im)
    for i in range(90):
        x, y = int(hrange(0, W, i, 11)), int(hrange(0, HORIZON - 3, i, 12) ** 1.0)
        c = (236, 236, 255) if hash01(i, 13) < 0.5 else (190, 200, 240)
        px(d, x, y, c)
        if hash01(i, 14) < 0.12:
            px(d, x + 1, y, mix(c, (40, 46, 96), 0.4))
            px(d, x, y + 1, mix(c, (40, 46, 96), 0.4))
    mx, my, r = 138, 105, 6                                         # 月亮（第一扇舷窗里）
    d.ellipse((mx - r, my - r, mx + r, my + r), fill=C((246, 240, 214)))
    d.ellipse((mx - r + 3, my - r - 1, mx + r + 3, my + r - 1), fill=C(mix((34, 42, 96), (64, 72, 128), 0.6)))
    hl(d, 0, W - 1, HORIZON, (84, 90, 130))
    for i in range(40):                                             # 月光照着的沙丘边
        x = int(hrange(0, W, i, 15))
        y = int(hrange(HORIZON + 3, H - 6, i, 16))
        hl(d, x, x + int(hrange(3, 12, i, 17)), y, (74, 72, 100))
    return im


@lru_cache(maxsize=1)
def night_land_img():
    """夜里的沙漠（640 循环）：远处几点村子 / 营地的灯（暖黄，一两个像素）。"""
    im = A._new(640, H - HORIZON - 2)
    d = ImageDraw.Draw(im)
    for i in range(18):
        x = int(hrange(0, 640, i, 21))
        y = int(hrange(1, im.height - 6, i, 22) * (0.4 + 0.6 * hash01(i, 23)))
        c = (255, 214, 120) if hash01(i, 24) < 0.7 else (255, 170, 90)
        px(d, x, y, c)
        if hash01(i, 25) < 0.4:
            px(d, x + 2, y, mix(c, (40, 40, 60), 0.4))
    return im


@lru_cache(maxsize=1)
def strut_img():
    """远侧的机翼撑杆：从窗外右上（翼下）斜到左下（机身下沿），只有从窗户里看得见的那一截；白漆 + 一道暗边。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for k in range(4):
        c = (226, 228, 228) if k < 2 else (170, 176, 184)
        d.line((150 + k, 88, 108 + k, 140), fill=C(c))
    d.line((154, 88, 112, 140), fill=C((120, 126, 136)))
    return im


# ============================================================ 机舱：零件
def gauge(d, cx, cy, r, kind='w', ang=None, seed=0):
    """圆表：黑表盘 + 一圈刻度 + 指针；kind 'adi' 姿态仪（上蓝下棕）。"""
    d.ellipse((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), fill=C((86, 88, 94)))
    if kind == 'adi':
        d.pieslice((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=C((70, 130, 200)))
        d.pieslice((cx - r, cy - r, cx + r, cy + r), 0, 180, fill=C((150, 100, 56)))
        return
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C(GAUGE))
    for k in range(8):
        a = k / 8 * math.tau
        px(d, round(cx + math.cos(a) * (r - 0.6)), round(cy + math.sin(a) * (r - 0.6)), (190, 194, 200))
    if ang is not None:
        col = (250, 250, 250) if kind == 'w' else (255, 206, 70)
        d.line((cx, cy, round(cx + math.cos(ang) * (r - 1)), round(cy + math.sin(ang) * (r - 1))), fill=C(col))


GAUGES = [(25, 126, 3, 'w', 4.2), (33, 125, 3, 'adi', 0), (41, 124, 3, 'w', 5.4),
          (25, 135, 3, 'y', 0.4), (33, 134, 3, 'w', 3.6), (41, 133, 3, 'w', 6.0)]   # (x, y, r, 种类, 指针角)


def cowl_top(x):
    """整流罩顶（x 0–17）：从桨毂后面往防火墙抬起来、前面圆。"""
    u = x / 17.0
    return int(round(130 - 12 * math.sqrt(u)))


def cowl_bot(x):
    u = x / 17.0
    return int(round(158 + 12 * u * u))


def draw_cowling(im):
    """机头整流罩（外面）：白漆、上沿一道深色描边、下半截渐暗、一道红饰条、三道散热百叶、前面的进气口、
    下面的排气管；防火墙那道接缝；螺旋桨毂（红色尖锥，被画面左边切掉一点）。"""
    d = ImageDraw.Draw(im)
    for x in range(0, 18):
        top, bot = cowl_top(x), cowl_bot(x)
        for y in range(top, bot + 1):
            u = (y - top) / max(1, bot - top)
            c = PAINT if u < 0.45 else (mix(PAINT, ALU_D, 0.3) if u < 0.75 else mix(PAINT, ALU_K, 0.45))
            if 0.3 < u < 0.38:
                c = STRIPE if u < 0.35 else dk(STRIPE, 0.8)
            px(d, x, y, c)
        px(d, x, top, (90, 92, 98))
        px(d, x, top + 1, ALU_HI)
        px(d, x, bot, (70, 72, 80))
    vl(d, 17, cowl_top(17), cowl_bot(17), ALU_K)                      # 和防火墙的接缝
    for k in range(3):                                                # 散热百叶
        y = 138 + k * 3
        hl(d, 9, 14, y, (60, 62, 70))
        hl(d, 9, 14, y + 1, ALU_HI)
    rect(d, 3, 150, 8, 155, (30, 30, 34))                             # 进气口
    hl(d, 3, 8, 150, (90, 90, 96))
    d.line((11, 168, 17, 174), fill=C((96, 86, 80)))                  # 排气管
    d.line((11, 169, 17, 175), fill=C((56, 52, 50)))
    cx, cy = PROP_C                                                   # 桨毂（尖锥朝左）
    for x in range(-3, 9):
        hw = int(round(7 * max(0.0, (x + 3) / 11.0) ** 0.6))
        if hw <= 0:
            continue
        vl(d, x, cy - hw, cy + hw, (226, 60, 52) if x < 6 else (176, 42, 38))
        if x >= 0:
            px(d, x, cy - hw, (252, 150, 130))
            px(d, x, cy + hw, (130, 30, 30))
    vl(d, 8, cy - 8, cy + 8, (80, 80, 86))


def draw_roof(im):
    """剖开的机身顶（x 46–320）：外面白漆 → 剖面（亮的铝边、深色的桁条、黄的隔热棉、米色衬板）→ 天花板下沿 CEIL。
    每 16 px 一根剖开的隔框（深一点、往下伸到天花板）。"""
    d = ImageDraw.Draw(im)
    for x in range(46, W):
        y0 = roof_y(x)
        px(d, x, y0, ALU_HI)
        px(d, x, y0 + 1, PAINT)
        px(d, x, y0 + 2, ALU_D)
        px(d, x, y0 + 3, ALU_K)
        for y in range(y0 + 4, CEIL - 3):
            c = INSUL if (x + y) % 3 else dk(INSUL, 0.86)
            px(d, x, y, c)
        hl(d, x, x, CEIL - 3, lt(HEADLINER, 0.15))
        for y in range(CEIL - 2, CEIL + 1):
            px(d, x, y, HEADLINER if y < CEIL else dk(HEADLINER, 0.82))
    for x in range(54, W, 16):                                       # 剖开的隔框
        y0 = roof_y(x)
        rect(d, x, y0 + 3, x + 1, CEIL - 3, ALU_K)
        px(d, x, y0 + 3, ALU_HI)
    for x in range(48, W, 5):                                        # 外面一排铆钉
        px(d, x, roof_y(x) + 1, (210, 210, 206))


def wing_th(x):
    """翼根在 x 处的厚度（坐在机顶上的上半个翼型：前缘圆、最厚在 30 % 弦长，约 14 px）。"""
    x0, x1 = 66, 200
    u = min(1.0, max(0.0, (x - x0) / (x1 - x0)))
    yt = 5 * 0.12 * (0.2969 * math.sqrt(u) - 0.126 * u - 0.3516 * u * u + 0.2843 * u ** 3 - 0.1015 * u ** 4)
    return max(1, int(round(yt * 2 * (x1 - x0) * 0.85)))


def draw_wing(im):
    """翼根（高单翼，坐在机顶上 x 64–200）：翼型的侧影（前缘圆、最厚在 30 %、后缘薄）、白漆、前缘一道红、
    中间一道蒙皮接缝 + 铆钉、后面的襟翼（单独一块，中间一道缝）、上面一个油箱盖。"""
    d = ImageDraw.Draw(im)
    x0, x1 = 66, 200
    for x in range(x0, x1 + 1):
        u = (x - x0) / (x1 - x0)
        th = wing_th(x)
        base = roof_y(x)
        for y in range(base - th, base):
            v = (y - (base - th)) / max(1, th)
            c = PAINT if v < 0.45 else (mix(PAINT, ALU_D, 0.4) if v < 0.8 else ALU_D)
            if u < 0.05:
                c = STRIPE if v < 0.8 else dk(STRIPE, 0.8)
            px(d, x, y, c)
        px(d, x, base - th, ALU_HI if u > 0.04 else STRIPE)
    for x in range(x0 + 8, x1 - 20, 5):                              # 蒙皮接缝上的一排铆钉
        px(d, x, roof_y(x) - wing_th(x) + 3, ALU_D)
    xf = 172                                                         # 襟翼缝
    for y in range(roof_y(xf) - wing_th(xf), roof_y(xf)):
        px(d, xf, y, ALU_K)
    for x in range(xf + 1, x1 + 1):                                  # 襟翼（颜色略暗一点）
        for y in range(roof_y(x) - wing_th(x), roof_y(x)):
            c = im.getpixel((x, y))[:3]
            px(d, x, y, dk(c, 0.94))
    cx = 104                                                         # 油箱盖
    yy = roof_y(cx) - wing_th(cx) - 1
    hl(d, cx - 2, cx + 2, yy, (120, 124, 130))
    hl(d, cx - 1, cx + 1, yy - 1, (170, 174, 180))
    # 翼根整流罩和机顶接上的那一道阴影
    for x in range(x0, x1 + 1):
        px(d, x, roof_y(x) - 1, ALU_D)


def draw_wall(im, holes):
    """远侧的舱壁（x 46–298，天花板到踢脚板）：上半截米色衬板、窗带、下半截深一点的护墙板 + 一道扶手、
    踢脚板；舷窗是透明洞（3 px 的窗框：深色胶条 + 浅色窗套）。"""
    d = ImageDraw.Draw(im)
    rect(d, 46, CEIL + 1, DOOR[0] - 1, FLOOR_BACK, WALL)
    gradient(im, (46, CEIL + 1, DOOR[0], 96), [mix(WALL, HEADLINER, 0.5), WALL], bands=3)
    gradient(im, (46, 130, DOOR[0], FLOOR_BACK - 4), [WALL_S, mix(WALL_S, WALL_D, 0.5)], bands=4)
    d = ImageDraw.Draw(im)
    hl(d, 46, DOOR[0] - 1, 129, WALL_HI)                            # 扶手上沿
    rect(d, 46, 130, DOOR[0] - 1, 132, (120, 84, 62))               # 扶手（木纹胶板）
    hl(d, 46, DOOR[0] - 1, 130, (150, 108, 80))
    hl(d, 46, DOOR[0] - 1, 133, WALL_D)
    rect(d, 46, FLOOR_BACK - 4, DOOR[0] - 1, FLOOR_BACK, (92, 80, 70))   # 踢脚板
    hl(d, 46, DOOR[0] - 1, FLOOR_BACK - 4, (128, 114, 100))
    for x in range(52, DOOR[0], 9):
        px(d, x, FLOOR_BACK - 2, (70, 60, 54))
    # 人造革的皱纹 + 缝线
    for i in range(160):
        x = int(hrange(46, DOOR[0], i, 31))
        y = int(hrange(CEIL + 2, 128, i, 32))
        c = im.getpixel((x, y))[:3]
        px(d, x, y, dk(c, 0.94) if hash01(i, 33) < 0.6 else lt(c, 0.06))
    for x in range(50, DOOR[0], 2):
        px(d, x, 96, dk(WALL, 0.88))
    # 舷窗
    for (x0, x1) in WINDOWS:
        win(im, d, x0, x1, WIN_Y[0], WIN_Y[1], holes)
    x0, x1, y0, y1 = COCK_WIN
    win(im, d, x0, x1, y0, y1, holes, r=5)


def win(im, d, x0, x1, y0, y1, holes, r=6):
    """一扇圆角舷窗：外圈浅色窗套（3 px）、里圈深色胶条、玻璃是洞；窗下沿那块墙被窗外的光照亮一点。"""
    d.rounded_rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 4), radius=r + 3, fill=C(WALL_HI))
    d.rounded_rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), radius=r + 2, fill=C(lt(WALL_HI, 0.15)))
    d.rounded_rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), radius=r + 1, fill=C((54, 50, 52)))
    hl(d, x0 + r, x1 - r, y1 + 4, dk(WALL_HI, 0.86))
    holes.append((x0, y0, x1, y1, r))


def draw_frames(im):
    """机身肋骨：舷窗之间一道道竖的隆起（左亮、右暗、两颗螺丝），从天花板到踢脚板——舱里像一根管子。"""
    d = ImageDraw.Draw(im)
    for x in (110, 164, 216, 268, 294):
        rect(d, x, CEIL + 1, x + 3, FLOOR_BACK - 5, mix(WALL, WALL_HI, 0.4))
        vl(d, x, CEIL + 1, FLOOR_BACK - 5, WALL_HI)
        vl(d, x + 3, CEIL + 1, FLOOR_BACK - 5, WALL_D)
        for y in (100, 122, 142):
            px(d, x + 1, y, (120, 116, 110))
        cast_shadow(im, [(x + 4, CEIL + 1), (x + 5, CEIL + 1), (x + 5, FLOOR_BACK - 5), (x + 4, FLOOR_BACK - 5)],
                    mul=SOFT_MUL)


def draw_ceiling_bits(im):
    """天花板上：顶灯（灭着）、三只球形出风口、禁烟 / 系安全带的小牌（图标）、一根拉手。"""
    d = ImageDraw.Draw(im)
    rect(d, 175, CEIL - 1, 186, CEIL + 2, (226, 222, 210))           # 顶灯
    hl(d, 176, 185, CEIL + 2, (190, 184, 170))
    hl(d, 177, 184, CEIL + 3, (236, 232, 220))
    for x in (132, 228, 272):                                        # 出风口
        d.ellipse((x - 2, CEIL + 1, x + 2, CEIL + 4), fill=C((176, 172, 164)), outline=C((130, 126, 120)))
        px(d, x, CEIL + 2, (80, 80, 86))
    rect(d, 116, CEIL + 2, 128, CEIL + 7, (44, 44, 50))               # 禁烟 / 安全带小牌
    rect(d, 117, CEIL + 3, 121, CEIL + 6, (232, 232, 226))
    d.line((117, CEIL + 3, 121, CEIL + 6), fill=C((200, 60, 50)))
    rect(d, 123, CEIL + 3, 127, CEIL + 6, (232, 232, 226))
    hl(d, 124, 126, CEIL + 5, (60, 60, 66))
    for (x, L) in ((206, 6),):                                       # 拉手
        vl(d, x, CEIL + 1, CEIL + L, (90, 86, 84))
        hl(d, x - 2, x + 2, CEIL + L, (120, 116, 112))


def draw_seat(im, s, dim=1.0, cockpit=False):
    """一张朝左的座椅（中心 s）：靠背在右边、往后仰（顶 y 116，横缝线 + 侧面厚度 + 左沿高光）、头枕套（白）、
    坐垫（左边伸出去、前沿圆）、坐垫下面的铁座架 + 滑轨（落在踢脚板 / 地毯后沿）；背后挂着的安全带。"""
    d = ImageDraw.Draw(im)

    def k(c):
        return tuple(int(v * dim) for v in c)
    top = 116 if not cockpit else 118
    bx0, bx1 = s + 4, s + 12
    # 座架 + 滑轨
    hl(d, s - 12, s + 12, FLOOR_BACK, k((70, 70, 76)))
    for lx in (s - 9, s + 6):
        vl(d, lx, 147, FLOOR_BACK, k((88, 90, 96)))
        px(d, lx, FLOOR_BACK, k((50, 50, 56)))
    d.line((s - 9, 147, s + 6, FLOOR_BACK - 1), fill=C(k((70, 72, 78))))
    # 靠背（往后仰：顶往右 2 px）
    back = [(bx0, top + 1), (bx1 - 1, top), (bx1 + 2, 146), (bx0 + 1, 146)]
    d.polygon(back, fill=C(k(SEAT)), outline=C(k(SEAT_K)))
    for y in range(top + 6, 144, 6):                                 # 横缝线（软包）
        u = (y - top) / (146 - top)
        hl(d, bx0 + 1 + int(u * 1.2), bx1 + int(u * 2), y, k(SEAT_D))
    d.line((bx0 + 1, top + 2, bx0 + 2, 144), fill=C(k(SEAT_HI)))
    d.line((bx1, top + 2, bx1 + 2, 144), fill=C(k(SEAT_D)))
    d.rectangle((bx0 + 1, top + 1, bx1 - 1, top + 4), fill=C(k((232, 228, 216))))   # 头枕套
    hl(d, bx0 + 1, bx1 - 1, top + 4, k((196, 190, 176)))
    # 坐垫
    d.rounded_rectangle((s - 12, CUSHION_Y, bx0 + 2, 146), radius=2, fill=C(k(SEAT)), outline=C(k(SEAT_K)))
    hl(d, s - 11, bx0 + 1, CUSHION_Y + 1, k(SEAT_HI))
    hl(d, s - 11, bx0 + 1, 145, k(SEAT_D))
    for x in range(s - 8, bx0, 6):
        px(d, x, CUSHION_Y + 3, k(SEAT_D))
    # 安全带（从靠背和坐垫的缝里垂下来）
    vl(d, bx0 - 1, 141, 150, k((70, 74, 84)))
    rect(d, bx0 - 2, 149, bx0, 151, k((176, 180, 186)))
    cast_shadow(im, [(bx1 + 3, top + 4), (bx1 + 5, top + 6), (bx1 + 5, 147), (bx1 + 3, 147)], mul=SOFT_MUL)


def draw_cockpit(im, holes):
    """驾驶舱：前风挡框 + A 柱（风挡玻璃是洞）、遮光罩 + 磁罗盘、仪表板（六块表的底盘在 strip 里画指针）、
    无线电、开关、油门 / 混合比、驾驶盘、方向舵踏板；侧墙：挂耳机的钩子、灭火瓶、地图袋。"""
    d = ImageDraw.Draw(im)
    # 驾驶舱的侧墙从风挡后面开始（x 46 以前是机头）
    rect(d, 18, 117, 46, FLOOR_BACK, (66, 64, 66))                  # 仪表板后面的暗处（防火墙）
    # 仪表板（斜着朝我们这边）
    d.polygon([(18, 118), (46, 116), (48, 146), (22, 148)], fill=C(PANEL), outline=C(PANEL_K))
    d.line((19, 118, 46, 116), fill=C(PANEL_HI))
    for (gx, gy, r, kind, ang) in GAUGES:
        gauge(d, gx, gy, r, kind)
    rect(d, 22, 140, 44, 145, (40, 42, 46))                         # 无线电
    for x in range(24, 43, 4):
        px(d, x, 142, (90, 230, 120))
        px(d, x + 1, 142, (60, 160, 90))
    for x in range(21, 46, 3):                                      # 一排开关
        px(d, x, 138, (200, 204, 210))
    hl(d, 14, 47, 117, (40, 40, 44))                                 # 遮光罩
    hl(d, 14, 47, 116, (76, 76, 82))
    rect(d, 30, 112, 34, 115, (30, 30, 34))                          # 磁罗盘
    rect(d, 31, 113, 33, 114, (236, 230, 200))
    px(d, 32, 111, (90, 90, 96))
    # 油门（黑球）+ 混合比（红球）拉杆
    hl(d, 46, 49, 141, (150, 154, 160))
    d.ellipse((49, 139, 52, 142), fill=C((30, 30, 34)))
    hl(d, 46, 48, 145, (150, 154, 160))
    d.ellipse((48, 143, 51, 146), fill=C((190, 40, 36)))
    # 驾驶盘：盘杆从仪表板伸出来、羊角握把（侧面看是一根竖的把）
    hl(d, 46, 54, 131, (110, 112, 118))
    hl(d, 46, 54, 132, (70, 72, 78))
    rect(d, 54, 124, 56, 139, (34, 34, 38))
    vl(d, 54, 125, 138, (96, 98, 104))
    px(d, 55, 124, (200, 60, 50))
    rect(d, 52, 130, 54, 133, (60, 62, 66))
    # 方向舵踏板
    for (x, y) in ((28, 150), (34, 152)):
        d.line((x + 6, y - 6, x, y), fill=C((70, 72, 78)), width=2)
        rect(d, x - 3, y, x + 2, y + 2, (40, 40, 44))
    # 风挡框 + A 柱（风挡玻璃是透明洞，外面是天）
    d.line([(14, 117), (45, 80)], fill=C((44, 44, 48)), width=3)
    d.line([(45, 80), (50, 84), (50, 116)], fill=C((70, 70, 74)), width=3)
    d.line([(46, 81), (49, 84)], fill=C((150, 152, 156)))
    # 侧墙：挂耳机的钩子（耳机在 strip 里）、灭火瓶、地图袋
    d = ImageDraw.Draw(im)
    rect(d, 106, 100, 108, 101, (120, 120, 126))
    d.rounded_rectangle((122, 134, 128, 150), radius=2, fill=C((196, 40, 36)), outline=C((90, 20, 20)))   # 灭火瓶
    rect(d, 124, 131, 126, 134, (40, 40, 44))
    vl(d, 123, 136, 148, (240, 110, 100))
    rect(d, 121, 141, 129, 142, (90, 96, 100))
    d.polygon([(81, 128), (95, 128), (94, 138), (82, 138)], fill=C((96, 70, 54)))   # 地图袋 + 露出来的航图
    hl(d, 81, 95, 128, (130, 96, 72))
    d.line((84, 127, 90, 124), fill=C((236, 228, 196)))
    d.line((85, 127, 92, 125), fill=C((210, 200, 166)))
    px(d, 88, 125, (80, 120, 180))


def draw_net(im):
    """后排上面的行李网：网后面兜着一只绿帆布袋、黑相机包、卷起来的红格子毯、一顶草帽、一个水壶；网眼是一格格菱形，
    四个挂钩挂在天花板上，中间往下垂。"""
    d = ImageDraw.Draw(im)
    x0, x1 = 222, 292
    d.rounded_rectangle((226, CEIL + 1, 250, CEIL + 9), radius=3, fill=C((96, 112, 70)), outline=C((60, 70, 44)))
    hl(d, 228, 248, CEIL + 2, (124, 140, 90))
    rect(d, 252, CEIL + 2, 262, CEIL + 9, (40, 40, 44))              # 相机包
    hl(d, 252, 262, CEIL + 2, (80, 80, 86))
    px(d, 257, CEIL + 5, (200, 200, 206))
    for x in range(264, 282):                                        # 卷起来的红格子毯
        for y in range(CEIL + 2, CEIL + 8):
            c = (170, 44, 40) if ((x // 2) + (y // 2)) % 2 else (210, 196, 170)
            px(d, x, y, c)
    vl(d, 264, CEIL + 2, CEIL + 7, (120, 30, 30))
    d.ellipse((283, CEIL + 2, 291, CEIL + 8), fill=C((214, 190, 120)))   # 草帽
    hl(d, 282, 292, CEIL + 7, (180, 152, 86))
    # 网
    for x in range(x0, x1 + 1):
        u = (x - x0) / (x1 - x0)
        sag = int(round(3 * math.sin(u * math.pi)))
        y = CEIL + 9 + sag
        px(d, x, y, (40, 40, 44))
        if (x - x0) % 4 == 0:
            for k in range(1, 9 + sag):
                if (k + (x - x0) // 4) % 2:
                    px(d, x + (k % 2), y - k, (40, 40, 44))
    for x in range(x0, x1 + 1, 18):
        rect(d, x, CEIL, x + 1, CEIL + 1, (150, 150, 156))


def draw_door(im):
    """机舱门（x 299–318）：圆角门框（深色密封条）、门板、小圆窗（洞）、拉杆把手、红色开门杆、两个铰链。"""
    d = ImageDraw.Draw(im)
    x0, x1 = DOOR
    rect(d, x0, CEIL + 1, W - 1, FLOOR_BACK, WALL_S)
    d.rounded_rectangle((x0 + 1, 92, x1, FLOOR_BACK), radius=6, fill=C((50, 46, 46)))
    d.rounded_rectangle((x0 + 2, 93, x1 - 1, FLOOR_BACK - 1), radius=5, fill=C(mix(WALL, WALL_HI, 0.3)))
    vl(d, x0 + 3, 98, FLOOR_BACK - 3, WALL_HI)
    vl(d, x1 - 2, 98, FLOOR_BACK - 3, WALL_D)
    rect(d, x0 + 4, 132, x1 - 3, 134, (120, 84, 62))                # 门上的扶手
    rect(d, x0 + 6, 120, x0 + 12, 123, (150, 154, 160))             # 拉杆把手
    hl(d, x0 + 6, x0 + 12, 120, (200, 204, 210))
    rect(d, x0 + 4, 138, x0 + 7, 146, (196, 40, 36))                 # 红色开门杆
    for y in (100, 140):                                             # 铰链
        rect(d, x1 - 1, y, x1 + 1, y + 5, (130, 134, 140))
    hl(d, x0 + 2, x1 - 1, FLOOR_BACK - 6, (92, 80, 70))


def draw_floor(im):
    """机舱地板（y 153–172）：棕红地毯（小方格织纹，明暗差很小）、两道座椅滑轨（平的金属条）、前沿剖面；
    机腹（y 173–179）：剖开的铝蒙皮 + 肋。"""
    d = ImageDraw.Draw(im)
    rect(d, 0, FLOOR_BACK + 1, W - 1, FLOOR_FRONT, CARPET)
    for y in range(FLOOR_BACK + 1, FLOOR_FRONT + 1):
        for x in range(16, W):
            if (x // 2 + y // 2) % 2 == 0 and hash01(x // 2, y // 2, 41) < 0.5:
                px(d, x, y, CARPET_S)
            elif hash01(x, y, 42) < 0.05:
                px(d, x, y, CARPET_HI)
    hl(d, 0, W - 1, FLOOR_BACK + 1, dk(CARPET, 0.8))                 # 踢脚板下的暗
    for y in (162, 170):                                             # 座椅滑轨（嵌在地毯里的平金属条）
        hl(d, 20, W - 1, y, (122, 106, 98))
        for x in range(24, W, 6):
            px(d, x, y, (96, 82, 76))
    for i in range(14):                                              # 几处踩脏的地方 / 掉的沙子（婴儿篮那块不撒）
        x, y = int(hrange(20, W, i, 43)), int(hrange(155, 171, i, 44))
        if 248 <= x <= 292:
            continue
        px(d, x, y, (130, 100, 80))
    hl(d, 0, W - 1, FLOOR_FRONT, (126, 90, 78))                      # 地毯前沿剖面
    rect(d, 0, FLOOR_FRONT + 1, W - 1, H - 1, ALU_D)
    hl(d, 0, W - 1, FLOOR_FRONT + 1, ALU_HI)
    hl(d, 0, W - 1, FLOOR_FRONT + 2, ALU)
    for x in range(6, W, 16):                                        # 地板梁
        rect(d, x, FLOOR_FRONT + 3, x + 2, H - 3, ALU_K)
        px(d, x, FLOOR_FRONT + 3, ALU)
    hl(d, 0, W - 1, H - 2, ALU)
    hl(d, 0, W - 1, H - 1, PAINT)
    for x in range(3, W, 5):
        px(d, x, H - 2, (180, 184, 190))


@lru_cache(maxsize=1)
def cabin_parts():
    """返回 (机舱层, 洞的列表)。先画舱壁 / 机顶 / 门再打洞（舷窗、前风挡、门上的小圆窗、机身外面），然后才画挡在窗前的
    座椅、驾驶舱、行李网、整流罩——不然洞会把椅背打穿。"""
    holes = []
    im = A._new(W, H)
    draw_floor(im)
    draw_wall(im, holes)
    draw_frames(im)
    draw_ceiling_bits(im)
    draw_roof(im)
    draw_wing(im)
    draw_door(im)
    # 窗边：窗外的光照进来，窗下那一截墙亮一点
    a = np.array(im).astype(np.float32)
    for (x0, x1) in WINDOWS + [(COCK_WIN[0], COCK_WIN[1])]:
        y0 = (WIN_Y[1] if x0 != COCK_WIN[0] else COCK_WIN[3]) + 5
        sub = a[y0:y0 + 6, x0:x1 + 1]
        m = sub[..., 3] > 0
        sub[m, :3] = np.clip(sub[m, :3] * 1.06 + 4, 0, 255)
    im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    A._tex_noise(im, (46, CEIL + 1, DOOR[0], 129), 0.03, 51)
    # 打洞
    a = np.array(im)
    m = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(m)
    for h in holes:
        x0, y0, x1, y1, r = h
        md.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=255)
    md.polygon(WS_POLY, fill=255)
    md.ellipse((DOOR[0] + 6, 101, DOOR[0] + 14, 113), fill=255)      # 门上的小圆窗
    a[np.array(m) > 0, 3] = 0
    outside = np.zeros((H, W), bool)
    for x in range(W):
        if x < 46:
            top = int(math.ceil(ws_x_inv(x)))
        else:
            top = wing_top(x) if 66 <= x <= 200 else roof_y(x)
        outside[:max(0, top), x] = True
    a[outside, 3] = 0
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    im = Image.fromarray(a, 'RGBA')
    # 挡在窗前的东西
    draw_seat(im, COPILOT, dim=0.9, cockpit=True)
    draw_cockpit(im, holes)
    draw_seat(im, PILOT, dim=1.0, cockpit=True)
    for s_ in SEATS:
        draw_seat(im, s_)
    draw_net(im)
    draw_cowling(im)
    im = A._grade(im, sat=0.92, val=0.98)
    im = opaque(im)
    # 玻璃反光（两道斜的亮线，画在玻璃上：不透明的像素）
    d = ImageDraw.Draw(im)
    for (x0, x1) in WINDOWS:
        for k in range(3):
            xx = x0 + 8 + k
            d.line((xx, WIN_Y[1] - 3, xx + 9, WIN_Y[0] + 3), fill=C((246, 250, 255)) if k == 1 else C((214, 228, 240)))
    d.line((26, 112, 38, 96), fill=C((236, 244, 250)))
    return im, holes


def ws_x_inv(x):
    """前风挡斜线：x 处机身外轮廓的 y（x 14–45 之间），再往前是整流罩顶。"""
    if x >= 45:
        return roof_y(46)
    if x >= 14:
        return min(117 - (x - 14) * (117 - 80) / (45 - 14), cowl_top(min(17, x)))
    return cowl_top(x)


def wing_top(x):
    """机身外轮廓在 x 处的顶（翼根顶 + 油箱盖那两行），再往上是天。"""
    top = roof_y(x) - wing_th(x)
    cap_y = roof_y(104) - wing_th(104) - 1
    if 102 <= x <= 106:
        top = min(top, cap_y if not 103 <= x <= 105 else cap_y - 1)
    return top


# ============================================================ 会动的
PROP_BOX = (0, 96, 16, 180)


def prop_frame(t):
    """螺旋桨（strip，8 帧 @8 fps）：侧面看是一片竖着的模糊圆盘（隔点抖出来的半透明），两片桨叶的残影上下扫
    （桨尖 y = 中心 ± R·cosθ，转半圈 = 8 帧，两片桨对称所以首尾接得上）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_PROP, N_PROP)
    cx, cy = PROP_C
    R, rx = 40, 8
    bay = A._bayer(W, H)
    for y in range(cy - R, cy + R + 1):
        v = (y - cy) / R
        hw = rx * math.sqrt(max(0.0, 1 - v * v))
        for x in range(int(cx - hw), int(cx + hw) + 1):
            if not (PROP_BOX[0] <= x < PROP_BOX[2] and PROP_BOX[1] <= y < PROP_BOX[3]):
                continue
            edge = abs(x - cx) > hw - 1.2
            on_cowl = cowl_top(max(0, min(17, x))) <= y <= cowl_bot(max(0, min(17, x))) and x >= 0
            dens = 0.55 if edge else (0.14 if on_cowl else 0.26)
            if bay[y, x] < dens:
                px(d, x, y, (120, 128, 140) if on_cowl else ((236, 240, 246) if not edge else (196, 202, 212)))
    th = math.pi * f / N_PROP
    for sgn in (1, -1):
        tip = cy + sgn * R * math.cos(th)
        sx = cx + sgn * 3 * math.sin(th)
        for k in range(R):
            u = k / R
            y = round(cy + (tip - cy) * u)
            x = round(cx + (sx - cx) * u)
            if PROP_BOX[1] <= y < PROP_BOX[3] and 0 <= x < PROP_BOX[2]:
                px(d, x, y, (70, 70, 76) if u < 0.85 else (230, 200, 60))
    return im


CHARM_BOX = (34, 82, 46, 100)
HEADSET_BOX = (100, 100, 114, 118)


def charm_frame(t):
    """风挡上沿挂着的蓝眼睛护身符（nazar）+ 钩子上挂着的耳机：随气流轻轻晃。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    sw = math.sin(math.tau * f / N_ANIM)
    ax, ay = 40, 83
    L = 9
    ex = round(ax + sw * 2)
    for k in range(L):
        px(d, round(ax + sw * 2 * k / L), ay + k, (120, 110, 90))
    ey = ay + L
    d.ellipse((ex - 2, ey, ex + 2, ey + 4), fill=C((40, 90, 180)))
    px(d, ex, ey + 2, (250, 250, 250))
    px(d, ex - 1, ey + 2, (120, 170, 230))
    px(d, ex + 1, ey + 2, (120, 170, 230))
    px(d, ex, ey + 2, (20, 20, 30))
    vl(d, ex, ey + 5, ey + 6, (200, 60, 50))
    # 耳机（挂在 x 107 的钩子上）：头箍 + 两只耳罩 + 一截线
    hx, hy = 107, 102
    dx = (0, 1, 1, 1, 0, -1, -1, -1)[f]
    cord = (0, 1, 2, 1, 0, -1, -2, -1)[f]
    d.arc((hx - 4 + dx, hy, hx + 4 + dx, hy + 8), 180, 360, fill=C((40, 40, 46)))
    for ox in (-4, 3):
        rect(d, hx + ox + dx, hy + 4, hx + ox + 1 + dx, hy + 9, (30, 30, 34))
        px(d, hx + ox + dx, hy + 5, (90, 90, 96))
    for k in range(6):
        px(d, hx + 3 + dx + round(cord * k / 5), hy + 10 + k, (60, 60, 66))
    return im


GAUGE_BOX = (20, 120, 46, 146)   # 含 x 22 / 43 的两颗灯


def gauges_frame(t):
    """仪表指针（strip）：空速 / 高度 / 升降表的指针跟着气流抖一两度、转弯表的小球晃、无线电的发射灯一闪一闪。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    for i, (gx, gy, r, kind, ang) in enumerate(GAUGES):
        if kind == 'adi':
            tilt = (0, 1, 1, 0, 0, -1, -1, 0)[(f + i) % N_ANIM]
            d.line((gx - r + 1, gy - tilt, gx + r - 1, gy + tilt), fill=C((240, 240, 240)))
            px(d, gx, gy - 1, (255, 210, 60))
            continue
        a = ang + 0.25 * math.sin(math.tau * f / N_ANIM + i * 1.7)
        col = (250, 250, 250) if kind == 'w' else (255, 206, 70)
        d.line((gx, gy, round(gx + math.cos(a) * (r - 1)), round(gy + math.sin(a) * (r - 1))), fill=C(col))
    if f % 4 < 2:
        px(d, 43, 141, (255, 80, 60))
    else:
        px(d, 43, 141, (90, 30, 30))
    px(d, 22, 141, (120, 255, 140) if f % 2 == 0 else (40, 80, 50))      # 应答机回复灯
    return im


ALARM_BOXES = [('alarm_panel', (14, 104, 30, 118)), ('alarm_ceiling', (140, CEIL - 2, 164, CEIL + 10))]


def alarm_frame(t):
    """警报（strip，key alarm）：遮光罩上的主警告灯（红）2 Hz 闪 + 天花板上一盏红色警灯一胀一缩（亮的时候灯罩发白、
    周围一圈隔点的红光）。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = fidx(t, FPS_ANIM, N_ANIM)
    on = f % 2 == 0
    lx, ly = 22, 113
    rect(d, lx - 3, ly - 2, lx + 3, ly + 1, (255, 70, 50) if on else (110, 20, 20))
    hl(d, lx - 2, lx + 2, ly - 2, (255, 210, 190) if on else (150, 40, 36))
    if on:
        bay = A._bayer(W, H)
        for y in range(ly - 8, ly + 4):
            for x in range(lx - 7, lx + 8):
                r = math.hypot(x - lx, (y - ly) * 1.3)
                if 3 < r < 7 and bay[y, x] < 0.5 - r * 0.05:
                    px(d, x, y, (255, 90, 70))
    cx, cy = 152, CEIL + 2
    lvl = (1.0, 0.7, 0.35, 0.15, 0.35, 0.7, 1.0, 0.85)[f]
    rect(d, cx - 3, cy - 1, cx + 3, cy + 2, mix((120, 24, 24), (255, 80, 60), lvl))
    hl(d, cx - 2, cx + 2, cy - 1, mix((150, 40, 36), (255, 220, 200), lvl))
    bay = A._bayer(W, H)
    for y in range(cy, cy + 8):
        for x in range(cx - 11, cx + 12):
            r = math.hypot(x - cx, (y - cy) * 1.6)
            if 3 < r < 11 * lvl + 1 and bay[y, x] < 0.42 * lvl:
                px(d, x, y, (255, 70, 56))
    return im


@lru_cache(maxsize=1)
def night_lights_img():
    """夜航开着的灯（key night，画在夜航压暗后面）：顶灯亮了（灯罩发白），灯下那一圈的舱壁 / 椅背 / 地毯照回原来的
    亮度（偏暖），边缘按 Bayer 抖开；每张座椅上方一小圈阅读灯；仪表板背光（表盘泛琥珀色）。只有 0 / 255 透明度。"""
    cab = np.array(cabin_parts()[0]).astype(np.float32)
    out = np.zeros_like(cab)
    bay = A._bayer(W, H)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lit = np.zeros((H, W), np.float32)
    for (cx, cy, rx, ry, a) in [(181, CEIL + 3, 74, 60, 1.0)] + [(s + 2, CEIL + 4, 16, 40, 0.75) for s in SEATS[1:]] + \
            [(PILOT + 6, CEIL + 4, 18, 44, 0.7)]:
        r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        lit = np.maximum(lit, np.clip(1.15 - r, 0, 1) * a)
    for (x0, y0, x1, y1) in (CHARM_BOX, HEADSET_BOX):
        lit[y0:y1, x0:x1] = 0
    lit[:CEIL - 2, :] = 0                                            # 只照舱里：机顶 / 机翼在外面，不会被顶灯照亮
    lit[:, :46] = 0
    core = lit > 0.55                                                # 灯下一圈实的、外面一圈隔点抖开（不要大片网点）
    rim = (lit > 0.3) & ~core & (bay < 0.5)
    m = (core | rim) & (cab[..., 3] > 0)
    warm = np.array((1.06, 0.94, 0.76), np.float32)
    out[m, :3] = np.clip(cab[m, :3] * warm * (0.62 + 0.38 * lit[m, None]), 0, 255)
    out[m, 3] = 255
    im = Image.fromarray(out.astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    rect(d, 176, CEIL, 185, CEIL + 2, (255, 246, 214))              # 顶灯灯罩亮了
    hl(d, 177, 184, CEIL + 3, (255, 236, 180))
    for (gx, gy, r, kind, ang) in GAUGES:                            # 仪表背光
        d.ellipse((gx - r, gy - r, gx + r, gy + r), fill=C((46, 36, 20)))
        for k in range(8):
            a = k / 8 * math.tau
            px(d, round(gx + math.cos(a) * (r - 0.6)), round(gy + math.sin(a) * (r - 0.6)), (255, 190, 90))
    for x in range(24, 43, 4):
        px(d, x, 142, (120, 255, 150))
    return im


STRIPS = [('prop', PROP_BOX, N_PROP, FPS_PROP, prop_frame, None),
          ('charm', CHARM_BOX, N_ANIM, FPS_ANIM, charm_frame, None),
          ('headset', HEADSET_BOX, N_ANIM, FPS_ANIM, charm_frame, None),
          ('gauges', GAUGE_BOX, N_ANIM, FPS_ANIM, gauges_frame, None)] + \
         [(n, b, N_ANIM, FPS_ANIM, alarm_frame, 'alarm') for (n, b) in ALARM_BOXES]
NIGHT_TINT = ('#0c1436', 0.46)
ALARM_TINT = ('#ff2414', 0.2)


@lru_cache(maxsize=1)
def build():
    cabin, holes = cabin_parts()
    return dict(sky=sky_img(), desert=desert_img(), clouds_far=clouds_far_img(), clouds_near=clouds_near_img(),
                night_sky=night_sky_img(), night_land=night_land_img(), strut=strut_img(), cabin=cabin, holes=holes,
                night_lights=night_lights_img())


def _wrap_paste(out, im, P_, vx, t, y):
    o = int(math.floor(t * vx)) % P_
    tl = P.tile(im, P_ * 2)
    paste(out, tl.crop((o, 0, o + W, im.height)), 0, y)


def _tint(out, col, a):
    lay = Image.new('RGBA', (W, H), tuple(int(col[i:i + 2], 16) for i in (1, 3, 5)) + (int(255 * a),))
    out.alpha_composite(lay)


def compose(camX=0, t=0.5, state=None):
    """直接拼一帧（不经导出），自检 / 预览用。state = {'night': 1, 'alarm': 1}。"""
    st = state or {}
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    _wrap_paste(out, R['desert'], 640, P_SKY_VX['desert'], t, HORIZON + 2)
    _wrap_paste(out, R['clouds_far'], 640, P_SKY_VX['clouds_far'], t, 0)
    _wrap_paste(out, R['clouds_near'], 640, P_SKY_VX['clouds_near'], t, 0)
    if st.get('night'):
        out.alpha_composite(R['night_sky'])
        _wrap_paste(out, R['night_land'], 640, P_SKY_VX['night_land'], t, HORIZON + 2)
    out.alpha_composite(R['strut'])
    out.alpha_composite(R['cabin'])
    for (name, box, n, fps, fn, key) in STRIPS:
        if name in ('prop', 'charm', 'headset'):
            paste(out, fn(t).crop(box), box[0], box[1])
    if st.get('night'):
        _tint(out, *NIGHT_TINT)
        out.alpha_composite(R['night_lights'])
    for (name, box, n, fps, fn, key) in STRIPS:
        if name == 'gauges':
            paste(out, fn(t).crop(box), box[0], box[1])
    if st.get('alarm'):
        _tint(out, *ALARM_TINT)
        for (name, box, n, fps, fn, key) in STRIPS:
            if key == 'alarm':
                paste(out, fn(t).crop(box), box[0], box[1])
    return out


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0)]
    for name in ('desert', 'clouds_far', 'clouds_near'):
        im, y = (R[name], HORIZON + 2) if name == 'desert' else BJ.crop_rows(R[name])
        layers.append(dict(type='wrap', image=ex.img(name, BJ.tile_to(im, 640, 640 + W)), period=640, k=0.0, y=y,
                           vx=P_SKY_VX[name]))
    layers.append(dict(type='static', image=ex.img('night_sky', R['night_sky']), x=0, y=0, key='night'))
    layers.append(dict(type='wrap', image=ex.img('night_land', BJ.tile_to(R['night_land'], 640, 640 + W)), period=640,
                       k=0.0, y=HORIZON + 2, vx=P_SKY_VX['night_land'], key='night'))
    sim, sy = BJ.crop_rows(R['strut'])
    layers.append(dict(type='static', image=ex.img('strut', sim), x=0, y=sy))
    layers.append(dict(type='static', image=ex.img('cabin', R['cabin']), x=0, y=0))
    bake = {n: (b, nn, fps, fn, key) for (n, b, nn, fps, fn, key) in STRIPS}
    for n in ('prop', 'charm', 'headset'):
        b, nn, fps, fn, key = bake[n]
        layers.append(ex.bake(n, b, nn, fps, fn, screen=True))
    layers.append(dict(type='tint', color=NIGHT_TINT[0], alpha=NIGHT_TINT[1], key='night'))
    lim, ly = BJ.crop_rows(R['night_lights'])
    layers.append(dict(type='static', image=ex.img('night_lights', lim), x=0, y=ly, key='night'))
    b, nn, fps, fn, key = bake['gauges']
    layers.append(ex.bake('gauges', b, nn, fps, fn, screen=True))
    layers.append(dict(type='tint', color=ALARM_TINT[0], alpha=ALARM_TINT[1], key='alarm'))
    for (n, b) in ALARM_BOXES:
        layers.append(ex.bake(n, b, N_ANIM, FPS_ANIM, alarm_frame, screen=True, key='alarm'))
    anchors = dict(ANCHORS)
    anchors.update(seat_boxes=[[s - 12, 116, s + 15, FLOOR_BACK] for s in SEATS],
                   cockpit_seats=[[PILOT - 12, 118, PILOT + 15, FLOOR_BACK], [COPILOT - 12, 118, COPILOT + 15, FLOOR_BACK]],
                   seat_cushion_y=CUSHION_Y, ceiling_y=CEIL, floor_back=FLOOR_BACK,
                   windows=[[x0, WIN_Y[0], x1, WIN_Y[1]] for (x0, x1) in WINDOWS] +
                   [[COCK_WIN[0], COCK_WIN[2], COCK_WIN[1], COCK_WIN[3]]],
                   door=[DOOR[0], 92, DOOR[1] + 1, FLOOR_BACK], panel=[18, 112, 48, 148], yoke=[55, 131],
                   windshield=[list(p) for p in WS_POLY], prop=list(PROP_C), horizon=HORIZON)
    st = ex.stage(W, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    states = ({}, {'night': True}, {'alarm': True}, {'night': True, 'alarm': True})
    P.check_no_black(ex, BJ, st, [0], (0.0, 0.6, 1.3, 7.7), states, '塞斯纳机舱')
    for name in ('sky', 'night_sky'):
        ex.checked('%s 整张不透明' % name, int((np.array(R[name])[..., 3] != 255).sum()))
    a = np.array(R['cabin'])
    ex.checked('机舱层 地板 + 机腹（y 153–180）整条不透明', int((a[FLOOR_BACK:, :, 3] != 255).sum()))
    P.check_alpha01(ex, '机舱层', R['cabin'])
    P.check_alpha01(ex, '夜航灯光层', R['night_lights'])
    # 窗洞真的是洞（舷窗玻璃中间透明）、天花板以下除了窗都是实的
    holes = 0
    for (x0, x1) in WINDOWS:
        holes += int((a[WIN_Y[0] + 2:WIN_Y[0] + 10, x0 + 24:x0 + 31, 3] != 0).sum() > 0)
    ex.checked('三扇舷窗中间是透明的（窗外的天看得见）', holes)
    inner = a[CEIL + 1:FLOOR_BACK, 52:DOOR[0], 3] == 0
    ex.checked('舱壁上只有舷窗 / 驾驶舱侧窗是洞（窗框外的洞像素）',
               int(inner.sum()) - sum(int((a[y0:y1 + 1, x0:x1 + 1, 3] == 0).sum()) for (x0, y0, x1, y1) in
                                      [(x0, WIN_Y[0], x1, WIN_Y[1]) for (x0, x1) in WINDOWS] +
                                      [(COCK_WIN[0], COCK_WIN[2], COCK_WIN[1], COCK_WIN[3])] if x0 >= 52))
    P.check_strips(ex, BJ, [(n, b, nn, fps, fn) for (n, b, nn, fps, fn, key) in STRIPS])
    P.check_wraps(ex, BJ, st)
    P.check_anchor_inside(ex, st['anchors'], W, WALK, ('pilot', 'copilot', 'seats', 'baby'))
    # 婴儿篮放的地方（x 270 ±18、y 154–158）只有地毯
    P.check_flat_spots(ex, R['cabin'], [(270, 158)], CARPET, 30, '婴儿篮放的地方（x 252–288，y 154–161）只有地毯',
                       half_w=18, up=4, down=4, y_min=FLOOR_BACK + 2)
    for t in (0.0, 0.6, 1.3):
        for state in ({}, {'night': True}, {'alarm': True}, {'night': True, 'alarm': True}):
            got = BJ.ref_render(st, ex.images, 0, t, state)
            ex.checked('机舱 t=%.2f %s 导出 vs 直接拼' % (t, '+'.join(state) or '白天'), BJ.ndiff(got, compose(0, t, state)))
    nm = P.lum(a[..., :3].astype(np.float32))
    ex.note('地毯亮度：y154–172 均值 %.0f 标准差 %.1f' % (nm[154:173].mean(), nm[154:173].std()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch6', 'after')
    os.makedirs(od, exist_ok=True)
    for i, state in enumerate(({}, {'night': 1}, {'alarm': 1})):
        compose(0, 0.5, state).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'cessna_cabin_solo_%d.png' % i))
    print('ok')
