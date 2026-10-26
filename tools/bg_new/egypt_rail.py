# -*- coding: utf-8 -*-
r"""egypt_rail —— 第9章「卢克索的铁路」：城外的小火车站和一段铁轨，下午（地图 rail_ch9；第 19 战段 2 巴斯特女神 玛丽亚）。
2026-10-19 nile 组按体验版精度新画（改前是 later_stages 的平涂占位）。共用零件在 nile_parts.py。

地图 640 宽、ground 160、可走带 y 148–178；**铁轨带 y 164–172（anchors.rail_band，剧情在这条带上放火车 prop.train）**。
侧视平视，太阳在左上（下午，影子往右下）。可走带从后往前：站台 / 碎石地（y 146–160）→ 站台前沿（y 158 黄线、159–163
混凝土立面）→ 铁轨（碎石道床 y 162–175、枕木每 8 px 一根 y 164–172、两条钢轨：远轨 y 165–166、近轨 y 169–171）→
前面一窄条碎石地（y 176–179）。铁轨横穿整张图；人站在站台、碎石地和铁轨上都行（铁轨是平的，不会穿插）。
从左到右（世界坐标）：
  x 0–180     小站：后面一栋黄色抹灰的站房（平顶 + 白色女儿墙、拱门、两扇绿百叶窗、阿拉伯文站名牌）、
              站台上的遮阳棚（三根铁柱 + 瓦楞铁皮顶 + 木锯齿檐，顶上一面埃及国旗 strip）、檐下挂着站牌
              （白底黑字 LUXOR + 阿拉伯文）、靠墙一条木长椅（anchors.bench）、几只行李麻袋和木箱；
              x 146–178 一座水塔（四根铁脚 + 斜撑 + 圆铁罐 + 锥顶，给蒸汽车头加水的水鹤，出水口滴水 strip）
              （anchors.platform [90,156]：站台上站人的点）
  x 180–640   铁路后面的碎石地 + 稀稀拉拉的干草；三根电线杆（x 232 / 372 / 512）拉着电线，线上停着几只小鸟（strip）；
              一间刷白的巡道工小屋（蓝门、小窗、门边靠一辆自行车）、一摞旧枕木、一只生锈的油桶；
              x 572–600 臂板信号机（铁格子柱 + 爬梯 + 红白的臂板 + 灯；anchors.signal）：
              key rumble = 1 时臂板放平、灯变红（pick），平时臂板斜上、绿灯；脚下一个继电器箱
远景：西岸的台地沙山（平顶 + 台阶 + 冲沟，不画尖顶）、远处的村子、地平线上一排海枣、沙原上的尘卷风（strip）；
中景：一片海枣林（树冠 strip 两棵）、土坯院墙、一座白色圆顶的小圣墓、甘蔗 / 苜蓿田和一条灌溉渠。
key：rumble（火车要来）——铁轨上一道道亮光往左窜、道床上的小石子跳、两边扬起小土（rumble_0 / rumble_1 两条 strip，
      各管半张图）+ 信号机臂板放平、红灯（pick）；剧情另外让 @rail_band 闪红。

图层（从后往前）：
  sky       static           320×180 下午的天 + 左上的太阳
  clouds    wrap   k 0.08 vx 1.0   小积云 + 云丝（640 循环）
  far       pano   k 0.2           远景 384 宽：台地沙山、远处的村子、地平线上的海枣、沙原（y 到 130 不透明）
  devil     strip  k 0.2           沙原上的尘卷风（8 帧 @4 fps）
  mid       pano   k 0.5           中景 480 宽：海枣林、土坯墙、白圆顶圣墓、田、灌溉渠（y 122–145 不透明）
  mpalm_0/1 strip  k 0.5           中景两棵海枣树的树冠
  kites     clouds                 两只高处盘旋的黑鸢
  near      pano   k 1             站台 + 铁路 + 碎石地（640 宽）
  flag、drip、birds   strip k 1    站台棚顶的国旗、水鹤出水口的水滴、电线上的小鸟
  rumble_0/1 strip k 1  key rumble  铁轨的震动（亮光、跳石子、扬土）
  signal    pick   k 1  key rumble  信号机的臂板 + 灯（0 = 斜上 + 绿灯，1 = 放平 + 红灯）
锚点（素材总表 §一，第9章，定稿值一个不改）：platform [90,156]、tracks [320,168]、rail_band [0,164,640,172]、
      signal [580,140]、bench [60,152]。
另导出：rails（两条钢轨轨面的 y [165, 169]）、platform_box（站台面 [0,146,180,158]）、platform_edge 158（黄线）、
      sleepers（枕木间距 8、第一根 x 2）、water_tower、hut、signal_head（臂板 + 灯的框）、back 146。
单独运行：python -B tools/bg_new/egypt_rail.py → tools/bg_new/_preview/ch9/after/egypt_rail_solo.png
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
    """nile 组的零件（tools/bg_new/nile_parts.py，按路径加载，模块名同 bg_jojo.bg_new，不改 sys.path 顺序）。"""
    key = 'bg_new_nile_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'nile_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


NP = _parts()
P, V, A = NP.P, NP.V, NP.A
C = NP.C
dk, lt, hl, vl, px, rect = NP.dk, NP.lt, NP.hl, NP.vl, NP.px, NP.rect
INK = NP.INK

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (148, 178)
BACK = 146                      # 地面后沿（站房、电线杆、小屋站在这一行上）
RAIL_BAND = (164, 172)          # 铁轨带（枕木上下沿）
RAIL_FAR, RAIL_NEAR = 165, 169  # 两条钢轨轨面那一行（远轨 165–166、近轨 169–171）
BALLAST = (162, 175)            # 碎石道床
PLAT_X1 = 180                   # 站台右端
PLAT_EDGE = 158                 # 站台前沿的黄线
SLEEPER_P, SLEEPER_X0 = 8, 2
N, FPS = NP.N, NP.FPS
CLOUD_P, CLOUD_K, CLOUD_VX = 640, 0.08, 1.0
FAR_K, MID_K = 0.2, 0.5
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 384
MIDW = W + int(math.ceil((PW - W) * MID_K))      # 480
SUN = (64, 30)
POLES = (232, 372, 512)
SIG_X = 586                     # 信号机柱子中线
HUT = (290, 330)

ANCHORS = dict(platform=[90, 156], tracks=[320, 168], rail_band=[0, 164, 640, 172], signal=[580, 140], bench=[60, 152])
STAND = ('platform', 'tracks', 'bench')
REQUIRED = tuple(ANCHORS)

CONC = ((150, 144, 134), (176, 170, 158), (194, 188, 176), (208, 202, 190), (222, 216, 204))   # 站台混凝土
GRAVEL = ((120, 106, 92), (146, 130, 112), (166, 150, 130), (184, 168, 146), (200, 186, 164))  # 碎石地 / 道床
SLEEPER = ((54, 40, 32), (82, 62, 46), (108, 84, 62))
STEEL = ((58, 54, 56), (96, 90, 90), (176, 172, 168), (222, 220, 214))
OCHRE_WALL = (226, 186, 116)
GRASS = ((150, 140, 80), (182, 168, 96), (122, 112, 66))


# ============================================================ 天 / 远景 / 中景
@lru_cache(maxsize=1)
def sky_img():
    return NP.sky_img(NP.SKY_AFTERNOON, SUN)


@lru_cache(maxsize=1)
def clouds_img():
    return NP.clouds_img(37)


@lru_cache(maxsize=1)
def far_img():
    """远景 384 宽：台地沙山（y 74–102）、远处的村子 + 地平线上一排海枣（到 y 112）、沙原（y 112–130，不透明，免得中景下面露天）。"""
    im = A._new(FARW, H)
    NP.ridge(im, 0, FARW, 74, 102, 27)
    d = ImageDraw.Draw(im)
    for y in range(102, 131):                                      # 沙原：越近越暖、越亮
        u = (y - 102) / 28.0
        hl(d, 0, FARW - 1, y, mix((222, 196, 150), (232, 204, 156), u))
    for i in range(70):                                            # 沙原上的小沙丘影子（短横线）
        x = int(hrange(0, FARW, 29, i))
        y = int(hrange(114, 130, 30, i))
        hl(d, x, x + int(hrange(3, 9, 31, i)), y, (214, 186, 140))
    NP.greenbelt(im, 0, FARW, 98, 113, 25, houses=[(100, 10, 6), (112, 7, 5), (250, 9, 5)], minaret=(122, 16), palms=0.8)
    amt = np.zeros((H, 1), np.float32)
    amt[:100] = 0.34
    amt[100:113] = 0.22
    amt[113:] = 0.1
    return NP.haze(im, amt)


DEVIL_X = 210


def _devil_raw(f):
    """沙原上的尘卷风：一根往上散开的灰黄沙柱，绕着自己转（一侧亮一侧暗、轮流换），根部扬起的沙一圈圈往外，8 帧闭合。"""
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    base = 126
    for k in range(26):
        y = base - k
        half = 1 + k // 7
        cx = DEVIL_X + int(round(1.5 * math.sin(k * 0.35 + math.tau * f / N)))
        for x in range(cx - half, cx + half + 1):
            s_ = (x - cx + half + f) % 3
            if hash01(33, k, x - cx, f) < 0.75 - k * 0.012:
                px(d, x, y, (226, 206, 168) if s_ == 0 else (206, 184, 146))
    for q in range(3):
        r = 2 + ((f + q * 3) % N)
        px(d, DEVIL_X - r, base + 1, (210, 188, 148))
        px(d, DEVIL_X + r, base + 1, (210, 188, 148))
    return im


@lru_cache(maxsize=1)
def mid_img():
    """中景 480 宽：甘蔗 / 苜蓿田（y 128–145，不透明）+ 一条灌溉渠、海枣林（树干 + 树冠，两棵的树冠另做 strip）、
    土坯院墙、一座白色圆顶的小圣墓。整体罩一点雾。"""
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    for y in range(124, 146):                                      # 田
        for x in range(MIDW):
            band = ((x // 26) + (y // 7)) % 3
            c = ((112, 150, 76), (132, 166, 84), (150, 170, 92))[band]
            if (x + y * 3) % 5 == 0:
                c = dk(c, 0.86)
            px(d, x, y, c)
    for x in range(MIDW):                                          # 灌溉渠（亮水一线 + 两边的土埂）
        y = 136 + int(round(1.5 * math.sin(x * 0.02)))
        px(d, x, y - 1, (170, 140, 100))
        px(d, x, y, (150, 190, 196))
        px(d, x, y + 1, (120, 98, 72))
    for (x0, x1, top) in ((40, 120, 116), (300, 380, 118)):        # 土坯院墙
        rect(d, x0, top, x1, 127, NP.MUDBRICK[3])
        hl(d, x0, x1, top, NP.MUDBRICK[5])
        for x in range(x0, x1 + 1, 7):
            vl(d, x, top + 2, 127, NP.MUDBRICK[2])
        hl(d, x0, x1, top - 1, INK)
    cx = 196                                                       # 白色圆顶的小圣墓
    rect(d, cx - 10, 106, cx + 10, 127, (238, 234, 222))
    vl(d, cx + 10, 106, 127, (204, 200, 190))
    for r in range(10):
        half = int(round(math.sqrt(max(0, 81 - r * r))))
        hl(d, cx - half, cx + half, 105 - r, (244, 242, 234) if r > 2 else (226, 222, 212))
        px(d, cx + half, 105 - r, (206, 202, 192))
    vl(d, cx, 92, 95, (214, 178, 90))
    rect(d, cx - 3, 116, cx + 3, 127, (60, 120, 100))
    for (x, h, sd) in ((14, 46, 1), (64, 54, 2), (98, 40, 3), (150, 58, 4), (232, 44, 5), (262, 56, 6), (338, 48, 7),
                       (404, 52, 8), (440, 42, 9), (468, 50, 10)):
        top = P.palm_trunk(im, x, 128, h, lean=int(hrange(-3, 3, 41, sd)), seed=sd, w0=3)
        if (x, h) not in MPALMS_STRIP:
            P.palm_crown(im, top[0], top[1], 11, seed=sd, f=0, amp=0.0)
    im = P.outer_rim(im)
    return NP.haze(im, 0.16)


MPALMS_STRIP = {(150, 58), (404, 52)}                               # 这两棵的树冠做 strip（中景里动）


def _mpalm_raw(i):
    (x, h) = sorted(MPALMS_STRIP)[i]
    sd = 4 if x == 150 else 8
    lean = int(hrange(-3, 3, 41, sd))

    def raw(f):
        im = A._new(MIDW, H)
        P.palm_crown(im, x + lean, 128 - h, 11, seed=sd, f=f)
        return NP.haze(P.outer_rim(im), 0.16)
    return raw


# ============================================================ 近景
def draw_ground(im):
    """铁路后面 / 前面的碎石地（低对比的斑驳 + 小石子 + 干草丛），站台那一段另画。"""
    P.sand_ground(im, 0, PW - 1, BACK, H - 1, GRAVEL[3], GRAVEL[2], GRAVEL[4], 401, ruts=(), pebbles=220)
    d = ImageDraw.Draw(im)
    for i in range(36):                                            # 干草丛（只在后沿那几行 / 道床前面，矮）
        x = int(hrange(PLAT_X1 + 4, PW - 4, 403, i))
        y = int(hrange(BACK + 1, 152, 404, i)) if i % 3 else int(hrange(176, 179, 405, i))
        for k in range(3):
            px(d, x + k - 1, y - (1 if k == 1 else 0), GRASS[k])
        px(d, x, y - 2, GRASS[1])


def draw_lineside_bits(im):
    """碎石地后沿的零碎：一根公里桩（白桩黑道）、几丛骆驼刺（低矮的灰绿刺丛）、电线杆脚下的影。"""
    d = ImageDraw.Draw(im)
    rect(d, 408, 136, 411, BACK - 1, (240, 238, 230))
    for y in (138, 141):
        hl(d, 408, 411, y, (40, 40, 44))
    vl(d, 411, 136, BACK - 1, (200, 198, 190))
    hl(d, 408, 411, 135, INK)
    for (cx, w, h, sd) in ((252, 9, 5, 1), (362, 7, 4, 2), (540, 11, 6, 3), (624, 8, 5, 4)):
        for y in range(BACK - h, BACK):
            u = (y - (BACK - h)) / float(h)
            half = int(round(w / 2.0 * math.sqrt(max(0.0, 1 - (1 - u) ** 2))))
            for x in range(cx - half, cx + half + 1):
                r = hash01(461, sd, x, y)
                c = (112, 116, 72) if r < 0.45 else ((138, 140, 86) if r < 0.85 else (164, 158, 100))
                px(d, x, y, c)
        hl(d, cx - w // 2 + 1, cx + w // 2 - 1, BACK - h - 1, INK)
    for x in POLES:
        P.soft_shadow(im, x - 2, x + 2, BACK, depth=2, slant=6)


def draw_track(im):
    """铁轨（横穿整张图）：碎石道床（上下两道斜坡亮边）→ 枕木（每 8 px 一根，顶面亮一行、墨线描边）→ 两条钢轨
    （轨头亮、轨腰暗、轨底一行影）→ 钢轨和枕木交叉的地方一个黑道钉。"""
    d = ImageDraw.Draw(im)
    y0, y1 = BALLAST
    for y in range(y0, y1 + 1):
        for x in range(PW):
            r = hash01(411, x, y)
            c = GRAVEL[1] if r < 0.4 else (GRAVEL[2] if r < 0.8 else GRAVEL[3])
            if y in (y0, y1):
                c = GRAVEL[3] if r < 0.6 else GRAVEL[4]
            px(d, x, y, c)
    hl(d, 0, PW - 1, y0 - 1, GRAVEL[1])
    for x in range(SLEEPER_X0, PW, SLEEPER_P):                     # 枕木
        rect(d, x, RAIL_BAND[0], x + 3, RAIL_BAND[1], SLEEPER[1])
        hl(d, x, x + 3, RAIL_BAND[0], SLEEPER[2])
        vl(d, x + 3, RAIL_BAND[0] + 1, RAIL_BAND[1], SLEEPER[0])
        vl(d, x - 1, RAIL_BAND[0], RAIL_BAND[1], GRAVEL[1])        # 枕木左边一道道床的影
        if hash01(413, x) < 0.3:
            px(d, x + 1, RAIL_BAND[0] + 3 + int(hrange(0, 4, 414, x)), SLEEPER[0])     # 木纹裂
    # 钢轨不描墨线：枕木要从远轨上面（y 164）、两轨之间（167–168）、近轨下面（172）露出来，铁轨才看得出是“铁轨”
    for (ry, rows) in ((RAIL_FAR, 2), (RAIL_NEAR, 3)):             # 钢轨
        hl(d, 0, PW - 1, ry, STEEL[3])
        hl(d, 0, PW - 1, ry + 1, STEEL[1])
        if rows == 3:
            hl(d, 0, PW - 1, ry + 2, STEEL[0])
        for x in range(SLEEPER_X0, PW, SLEEPER_P):
            px(d, x + 1, ry + rows, (30, 28, 30))                  # 道钉
            px(d, x + 2, ry + rows, STEEL[1])
        for x in range(0, PW, 37):                                 # 轨缝
            px(d, x, ry, STEEL[1])


def draw_station(im):
    """小站（x 0–180）：站房 → 遮阳棚 → 长椅、行李 → 站台面（混凝土方砖、黄线、前沿立面）。水塔另画。"""
    d = ImageDraw.Draw(im)
    pal = P.wall_pal(OCHRE_WALL)
    rect(d, 0, 76, 138, BACK - 1, pal[1])                          # 站房墙
    NP.mottle(im, (0, 76, 138, BACK - 1), pal[1], pal[2], pal[0], 421, cell=5, streaks=3)
    d = ImageDraw.Draw(im)
    rect(d, 0, 70, 140, 75, (240, 236, 224))                       # 白色女儿墙 + 檐线
    hl(d, 0, 140, 70, (252, 250, 244))
    hl(d, 0, 140, 76, (196, 190, 176))
    hl(d, 0, 140, 69, INK)
    vl(d, 140, 70, BACK - 1, INK)
    vl(d, 139, 77, BACK - 1, pal[2])
    for x in range(4, 136, 9):                                     # 女儿墙上的镂空小方孔
        rect(d, x, 72, x + 2, 73, (200, 194, 180))
    # 拱门（黑，门里一张贴着时刻表的板）+ 两扇绿百叶窗
    for (x0, x1, top, kind) in ((44, 60, 104, 'door'), (10, 24, 100, 'win'), (106, 120, 100, 'win')):
        w = x1 - x0 + 1
        for x in range(x0, x1 + 1):
            u = (x - x0 + 0.5) / w
            ah = int(round(math.sqrt(max(0.0, 1 - (2 * u - 1) ** 2)) * (w / 2.0)))
            yt = top - ah
            bot = BACK - 1 if kind == 'door' else 124
            for y in range(yt, bot + 1):
                if kind == 'door':
                    c = (44, 36, 36)
                else:
                    c = (64, 130, 100) if (y - yt) % 3 else (48, 104, 80)
                    if x in (x0 + w // 2,):
                        c = (40, 84, 64)
                px(d, x, y, c)
            px(d, x, yt - 1, (250, 246, 236))
        vl(d, x0 - 1, top - 2, (BACK - 1 if kind == 'door' else 125), (250, 246, 236))
        vl(d, x1 + 1, top - 2, (BACK - 1 if kind == 'door' else 125), (250, 246, 236))
        if kind == 'win':
            hl(d, x0 - 2, x1 + 2, 125, (250, 246, 236))
            hl(d, x0 - 2, x1 + 2, 126, pal[2])
    rect(d, 48, 112, 56, 122, (236, 232, 220))                     # 门里贴的时刻表
    for y in range(114, 121, 2):
        hl(d, 49, 55, y, (90, 90, 96))
    rect(d, 66, 80, 100, 90, (40, 92, 70), outline=(236, 220, 150))   # 墙上阿拉伯文站名牌（绿底金字）
    P.sign_ar(d, 68, 82, 98, 88, (40, 92, 70), (236, 220, 150), seed=13)
    # 遮阳棚：三根铁柱 + 瓦楞铁皮顶（y 94–99）+ 木锯齿檐；棚下墙上一道影
    NP.mul_box(im, (0, 101, 146, 112), NP.SHADOW_MUL)
    d = ImageDraw.Draw(im)
    for x in (18, 72, 126):
        vl(d, x, 100, BACK + 9, (70, 74, 80))
        vl(d, x + 1, 100, BACK + 9, (40, 42, 48))
        px(d, x, BACK + 10, (40, 42, 48))
    for x in range(0, 148):
        for y in range(94, 100):
            c = (150, 156, 160) if (x // 2) % 2 else (118, 124, 130)
            if y == 94:
                c = (196, 200, 204)
            px(d, x, y, c)
        if x % 4 < 2:
            px(d, x, 100, (178, 120, 70))
            if x % 4 == 0:
                px(d, x, 101, (150, 98, 58))
    hl(d, 0, 148, 93, INK)
    vl(d, 148, 93, 100, INK)
    rect(d, 84, 104, 116, 111, (244, 242, 236), outline=(40, 40, 44))  # 站牌（挂在棚檐下：白底黑字 LUXOR + 阿拉伯文）
    vl(d, 88, 101, 103, (60, 60, 66))
    vl(d, 112, 101, 103, (60, 60, 66))
    NP.tiny_text(d, 86, 105, 'LUXOR', (30, 30, 34))
    P.sign_ar(d, 106, 105, 114, 110, (244, 242, 236), (30, 30, 34), seed=17)
    # 长椅（靠墙，坐面 y 140，anchors.bench [60,152] 是坐 / 站的点）
    rect(d, 46, 132, 74, 135, NP.WOOD)
    hl(d, 46, 74, 132, NP.WOOD_HI)
    rect(d, 46, 139, 76, 141, NP.WOOD)
    hl(d, 46, 76, 139, NP.WOOD_HI)
    hl(d, 46, 76, 142, NP.WOOD_D)
    for x in (48, 73):
        vl(d, x, 136, BACK - 1, (60, 60, 66))
        vl(d, x, 142, BACK - 1, (60, 60, 66))
    hl(d, 45, 77, 131, INK)
    P.soft_shadow(im, 46, 78, BACK, depth=2, slant=4)
    d = ImageDraw.Draw(im)
    # 行李：两只麻袋、一只木箱（靠墙）
    P.sack(d, 92, BACK - 1, w=8, h=9)
    P.sack(d, 101, BACK - 1, w=7, h=8)
    P.crate(d, 110, BACK - 1, 11, 9, kind='plank', seed=3)
    # 站台面：混凝土方砖（y 146–157）、黄线 158、前沿立面 159–163
    for y in range(BACK, PLAT_EDGE):
        for x in range(0, PLAT_X1):
            c = CONC[3] if hash01(431, x // 5, y // 3) < 0.7 else CONC[2]
            if (x % 24 == 0) or (y - BACK) % 6 == 5:
                c = CONC[2]
            if hash01(432, x, y) < 0.04:
                c = CONC[2]
            px(d, x, y, c)
    hl(d, 0, PLAT_X1 - 1, PLAT_EDGE, (226, 190, 70))
    hl(d, 0, PLAT_X1 - 1, PLAT_EDGE + 1, CONC[4])
    for y in range(PLAT_EDGE + 2, 164):
        hl(d, 0, PLAT_X1 - 1, y, CONC[1] if y < 162 else CONC[0])
    for x in range(0, PLAT_X1, 24):
        vl(d, x, PLAT_EDGE + 2, 163, CONC[0])
    vl(d, PLAT_X1, BACK, 163, CONC[0])
    vl(d, PLAT_X1 + 1, PLAT_EDGE + 2, 163, INK)
    # 站台尽头往下的斜坡（站台到碎石地）
    for k in range(6):
        hl(d, PLAT_X1 + 1, PLAT_X1 + 1 + k, PLAT_EDGE + 2 - k // 2, CONC[2])
    P.soft_shadow(im, 0, PLAT_X1, BACK, depth=1, slant=0)


def draw_tower(im):
    """水塔（x 146–178）：四根铁脚（两两看得见）+ 交叉斜撑、圆铁罐（铆钉、左亮右暗）+ 锥顶 + 爬梯；
    右边伸出一根给车头加水的水鹤（弯管 + 帆布软管），出水口在 (176, 112)，水滴是 strip。"""
    d = ImageDraw.Draw(im)
    legs = [(150, 147), (172, 175)]
    for (xt, xb) in legs:
        for y in range(70, BACK):
            u = (y - 70) / float(BACK - 70)
            x = int(round(xt + (xb - xt) * u))
            px(d, x, y, (84, 84, 92))
            px(d, x + 1, y, (52, 52, 60))
    for y0_ in (82, 102, 122):                                     # 交叉斜撑
        for k in range(20):
            u = k / 19.0
            xa = int(round(151 + 21 * u))
            px(d, xa, y0_ + int(round(18 * u)), (70, 70, 78))
            px(d, xa, y0_ + 18 - int(round(18 * u)), (70, 70, 78))
        hl(d, 150, 173, y0_, (96, 96, 104))
    for y in range(52, 71):                                        # 罐
        for x in range(144, 180):
            s_ = (x - 144) / 35.0
            c = (150, 160, 166) if s_ < 0.2 else ((126, 136, 142) if s_ < 0.6 else (96, 104, 112))
            if (y - 52) % 6 == 0:
                c = dk(c, 0.84)                                     # 铁板接缝
            if (y - 52) % 6 == 1 and x % 4 == 0:
                c = lt(c, 0.25)                                     # 铆钉
            px(d, x, y, c)
    for r in range(8):                                             # 锥顶
        hl(d, 144 + r * 2, 179 - r * 2, 51 - r, (110, 118, 124) if r % 2 else (132, 140, 146))
    px(d, 161, 43, (90, 96, 100))
    px(d, 162, 42, (90, 96, 100))
    for y in range(72, BACK):                                      # 爬梯
        px(d, 158, y, (64, 64, 72))
        px(d, 162, y, (64, 64, 72))
        if y % 4 == 0:
            hl(d, 158, 162, y, (96, 96, 104))
    for k in range(10):                                            # 水鹤：从罐底伸出来的弯管 → 往下垂的帆布软管
        px(d, 179 + min(k, 4), 66 + k, (60, 60, 68))
    for y in range(76, 112):
        px(d, 183, y, (120, 96, 70) if y % 3 else (96, 76, 56))
        px(d, 184, y, (96, 76, 56))
    hl(d, 182, 185, 112, (60, 60, 68))
    a = np.array(im)                                               # 外沿墨线（罐、顶、脚对着天的那一圈）
    m = np.zeros((H, PW), bool)
    m[40:BACK, 140:190] = True
    op = a[..., 3] > 0
    nb = np.zeros_like(op)
    nb[:-1] |= op[1:]
    nb[:, 1:] |= op[:, :-1]
    nb[:, :-1] |= op[:, 1:]
    rim = nb & ~op & m
    rim[:, :140] = False
    a[rim & (np.arange(H)[:, None] < 72), :3] = INK
    a[rim & (np.arange(H)[:, None] < 72), 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))


def draw_lineside(im):
    """铁路后面（x 180–640）：三根电线杆 + 电线（接到站房）、巡道工小屋 + 自行车、一摞旧枕木、生锈的油桶、信号机的柱子和继电器箱。"""
    d = ImageDraw.Draw(im)
    tops = []
    for i, x in enumerate(POLES):
        tops.append(P.power_pole(d, x, 74, BACK - 1, lean=(1 if i == 1 else 0)))
    pts = [((140, 80), (140, 80))] + tops
    for (a_, b_) in zip(pts[:-1], pts[1:]):
        for j in range(2):
            V.wire(d, a_[j][0], a_[j][1], b_[j][0], b_[j][1], 5, col=(44, 40, 44))
    last = tops[-1]
    for j in range(2):
        V.wire(d, last[j][0], last[j][1], PW + 40, last[j][1] + 6, 6, col=(44, 40, 44))
    x0, x1 = HUT                                                   # 巡道工小屋（刷白、平顶、蓝门、小窗）
    rect(d, x0, 118, x1, BACK - 1, (234, 230, 218))
    NP.mottle(im, (x0, 118, x1, BACK - 1), (234, 230, 218), (214, 208, 194), (246, 244, 236), 441, cell=4, streaks=2)
    d = ImageDraw.Draw(im)
    rect(d, x0 - 1, 114, x1 + 1, 117, (214, 206, 190))
    hl(d, x0 - 1, x1 + 1, 114, (246, 244, 236))
    hl(d, x0 - 1, x1 + 1, 113, INK)
    vl(d, x0 - 2, 114, BACK - 1, INK)
    vl(d, x1 + 2, 114, BACK - 1, INK)
    vl(d, x1, 118, BACK - 1, (200, 196, 184))
    rect(d, x0 + 6, 126, x0 + 15, BACK - 1, (52, 104, 168))       # 蓝门
    vl(d, x0 + 6, 126, BACK - 1, (80, 132, 196))
    px(d, x0 + 13, 136, (230, 200, 90))
    rect(d, x0 + 22, 124, x0 + 32, 132, (60, 54, 56))               # 小窗（铁栏）
    for x in range(x0 + 24, x0 + 32, 3):
        vl(d, x, 124, 132, (150, 150, 156))
    hl(d, x0 + 21, x0 + 33, 133, (250, 248, 240))
    P.bicycle(d, x1 + 4, BACK - 1)
    P.soft_shadow(im, x0, x1 + 22, BACK, depth=2, slant=5)
    d = ImageDraw.Draw(im)
    for k in range(4):                                             # 一摞旧枕木
        y = BACK - 1 - k * 3
        rect(d, 440 + (k % 2) * 2, y - 2, 470 - (k % 2) * 2, y, SLEEPER[1])
        hl(d, 440 + (k % 2) * 2, 470 - (k % 2) * 2, y - 2, SLEEPER[2])
        px(d, 440 + (k % 2) * 2, y - 1, SLEEPER[0])
    hl(d, 442, 468, BACK - 13, INK)
    rect(d, 476, 134, 485, BACK - 1, (140, 72, 46))                # 生锈的油桶
    vl(d, 476, 134, BACK - 1, (176, 100, 66))
    vl(d, 485, 134, BACK - 1, (96, 50, 36))
    hl(d, 476, 485, 137, (110, 56, 38))
    hl(d, 476, 485, 142, (110, 56, 38))
    hl(d, 476, 485, 133, INK)
    P.soft_shadow(im, 440, 486, BACK, depth=2, slant=4)
    d = ImageDraw.Draw(im)
    # 信号机：铁格子柱（x 584–588，y 88–145）+ 爬梯；臂板和灯在 pick 层
    for y in range(88, BACK):
        px(d, SIG_X - 2, y, (70, 70, 78))
        px(d, SIG_X + 2, y, (50, 50, 58))
        if (y // 3) % 2:
            px(d, SIG_X - 1 + (y % 3), y, (96, 96, 104))
    vl(d, SIG_X - 3, 88, BACK - 1, INK)
    vl(d, SIG_X + 3, 88, BACK - 1, INK)
    for y in range(96, BACK, 4):                                   # 爬梯
        hl(d, SIG_X - 7, SIG_X - 4, y, (90, 90, 98))
    vl(d, SIG_X - 7, 94, BACK - 1, (70, 70, 78))
    vl(d, SIG_X - 4, 94, BACK - 1, (70, 70, 78))
    rect(d, SIG_X - 2, 86, SIG_X + 2, 87, (60, 60, 68))
    px(d, SIG_X, 85, (60, 60, 68))
    rect(d, 594, 134, 604, BACK - 1, (120, 128, 120))              # 继电器箱
    hl(d, 594, 604, 134, (160, 168, 160))
    vl(d, 604, 134, BACK - 1, (90, 96, 90))
    hl(d, 594, 604, 133, INK)
    rect(d, 597, 137, 601, 139, (226, 196, 70))
    P.soft_shadow(im, 580, 606, BACK, depth=2, slant=4)


@lru_cache(maxsize=1)
def near_img():
    im = A._new(PW, H)
    draw_ground(im)
    draw_lineside(im)
    draw_lineside_bits(im)
    draw_station(im)
    draw_tower(im)
    draw_track(im)
    P.compress_band(im, 112, BACK, (190, 170, 140), amt=0.08, ramp=10)
    return NP.opaque(im)


# ============================================================ 信号机（pick）
SIG_BOX = (570, 84, 606, 112)


def signal_img(danger):
    """臂板 + 灯（世界坐标画进 SIG_BOX）：平时臂板斜着往上（45°，开通）、灯绿；rumble 时臂板放平（停车）、灯红、灯罩一圈亮。"""
    x0, y0, x1, y1 = SIG_BOX
    im = A._new(x1 - x0, y1 - y0)
    d = ImageDraw.Draw(im)

    def P_(x, y, c):
        px(d, x - x0, y - y0, c)
    pv = (SIG_X + 1, 92)                                           # 臂板转轴
    for k in range(16):                                            # 臂板：红底、靠外一道白条
        if danger:
            x, y = pv[0] + 2 + k, pv[1]
            pts = [(x, y - 1), (x, y), (x, y + 1)]
        else:
            x, y = pv[0] + 2 + int(round(k * 0.72)), pv[1] - int(round(k * 0.72))
            pts = [(x, y - 1), (x, y), (x + 1, y)]
        c = (246, 244, 236) if 10 <= k <= 12 else (200, 52, 44)
        for (xx, yy) in pts:
            P_(xx, yy, c)
    rect(d, pv[0] - 2 - x0, pv[1] - 1 - y0, pv[0] + 1 - x0, pv[1] + 1 - y0, (40, 40, 46))
    lx, ly = SIG_X - 8, 101                                        # 灯（左边的灯箱 + 圆玻璃）
    rect(d, lx - 3 - x0, ly - 3 - y0, lx + 3 - x0, ly + 3 - y0, (34, 34, 40))
    col = (255, 70, 56) if danger else (96, 230, 140)
    for (dx, dy) in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        P_(lx + dx, ly + dy, col)
    P_(lx - 1, ly - 1, (255, 240, 220))
    if danger:
        for (dx, dy) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            P_(lx + dx, ly + dy, (255, 150, 120))
    hl(d, lx + 4 - x0, SIG_X - 3 - x0, ly - y0, (60, 60, 68))      # 灯箱的托架
    a = np.array(im)
    op = a[..., 3] > 0
    nb = np.zeros_like(op)
    nb[:-1] |= op[1:]
    nb[1:] |= op[:-1]
    nb[:, 1:] |= op[:, :-1]
    nb[:, :-1] |= op[:, 1:]
    rim = nb & ~op
    a[rim, :3] = INK
    a[rim, 3] = 255
    return Image.fromarray(a, 'RGBA')


# ============================================================ 会动的
def _flag_raw(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    vl(d, 30, 76, 93, (190, 190, 196))
    P.egypt_flag(d, 30, 77, f, L=11, hgt=6)
    return im


def _drip_raw(f):
    """水鹤软管口的水滴：一滴滴往下落（每帧往下 4 px），落到站台上溅一下，8 帧闭合。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for q in range(2):
        g = (f + q * 4) % N
        y = 114 + g * 4
        if y < BACK:
            px(d, 183, y, (170, 210, 226))
            px(d, 183, y + 1, (120, 170, 196))
        else:
            px(d, 181, BACK - 1, (170, 210, 226))
            px(d, 185, BACK - 1, (170, 210, 226))
    px(d, 183, 113, (150, 196, 214) if f % 2 else (120, 170, 196))
    return im


BIRDS_ON_WIRE = [(268, 0), (282, 3), (420, 5), (436, 1)]           # (x, 相位)：停在第一根电线上


@lru_cache(maxsize=1)
def _wire_y():
    """电线（第一根）在每个 x 的 y（从近景图里找：电线杆之间那一根）。"""
    a = np.array(near_img())
    out = {}
    for (x, ph) in BIRDS_ON_WIRE:
        col = a[60:110, x]
        ys = [60 + i for i in range(col.shape[0]) if col[i, 3] > 0 and col[i, 0] < 70]
        out[x] = ys[0] if ys else 80
    return out


def _birds_raw(f):
    """电线上停着的四只小鸟：低头、抬头、扭身，每帧至少一只在动；一只偶尔扑一下翅膀，8 帧闭合。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    wy = _wire_y()
    for (x, ph) in BIRDS_ON_WIRE:
        y = wy[x] - 1
        g = (f + ph) % N
        col = (60, 54, 52)
        rect(d, x, y - 2, x + 2, y, col)
        px(d, x + 3, y - 1, col)                                   # 尾
        if g in (0, 1, 2):
            px(d, x - 1, y - 3, col)                               # 抬头
            px(d, x - 2, y - 3, (200, 150, 80))
        elif g in (3, 4):
            px(d, x - 1, y - 1, col)                               # 低头理羽毛
        elif g == 5:
            px(d, x, y - 4, col)                                   # 扑翅
            px(d, x + 2, y - 4, col)
            px(d, x - 1, y - 3, col)
        else:
            px(d, x, y - 3, col)
            px(d, x - 1, y - 3, (200, 150, 80))
    return im


def _rumble_raw(half):
    """rumble（火车要来）：两条钢轨轨面上一道道亮光往左窜（每帧 5 px、间隔 40 px，8 帧刚好一圈）、道床上的小石子
    一跳一跳（隔帧换位置）、道床两边扬起的小土（一闪一闪）。half = 0 管 x 0–319、1 管 x 320–639（帧条宽 ≤ 4096）。"""
    xa, xb = half * 320, half * 320 + 320

    def raw(f):
        im = A._new(PW, H)
        d = ImageDraw.Draw(im)
        for ry in (RAIL_FAR, RAIL_NEAR):
            for base in range(xa - 40, xb + 40, 40):
                x = base - 5 * f + (0 if ry == RAIL_FAR else 17)
                for k in range(7):
                    xx = x + k
                    if xa <= xx < xb:
                        px(d, xx, ry, (255, 250, 214) if 2 <= k <= 4 else (246, 226, 170))
        for i in range(36):                                        # 跳起来的小石子
            x = int(hrange(xa, xb - 1, 451, i))
            if (i + f) % 2:
                y = int(hrange(BALLAST[0], BALLAST[1], 452, i))
                if not (RAIL_FAR - 1 <= y <= RAIL_FAR + 1 or RAIL_NEAR - 1 <= y <= RAIL_NEAR + 2):
                    px(d, x, y - 1, GRAVEL[4])
        for i in range(14):                                        # 两边扬起的小土
            x = int(hrange(xa + 2, xb - 4, 453, i))
            if (i + f) % 3 == 0:
                y = BALLAST[0] - 1 if i % 2 else BALLAST[1] + 1
                hl(d, x, x + 2, y, (214, 196, 160))
                px(d, x + 1, y - 1, (214, 196, 160))
        return im
    return raw


@lru_cache(maxsize=1)
def strips():
    """近景 strip：[(名字, 框, 帧函数, key)]，框按画出来的东西算（auto_box）。"""
    out = []
    for name, raw in (('flag', _flag_raw), ('drip', _drip_raw), ('birds', _birds_raw)):
        fn = NP.cached_frames(raw)
        out.append((name, P.auto_box(fn, N, FPS), fn, None))
    for i in range(2):
        fn = NP.cached_frames(_rumble_raw(i))
        out.append(('rumble_%d' % i, P.auto_box(fn, N, FPS), fn, 'rumble'))
    return out


# ============================================================ 图层表 / 导出
@lru_cache(maxsize=1)
def table():
    tb = [('static', 'sky', sky_img(), 0, 0),
          ('wrap', 'clouds', clouds_img(), CLOUD_P, CLOUD_K, 8, CLOUD_VX)]
    fim, fy = P.crop_pano(far_img())
    tb.append(('pano', 'far', fim, FAR_K, 0, fy))
    dv = NP.cached_frames(_devil_raw)
    tb.append(('strip', 'devil', P.auto_box(dv, N, FPS), N, FPS, dv, FAR_K))
    mim, my = P.crop_pano(mid_img())
    tb.append(('pano', 'mid', mim, MID_K, 0, my))
    for i in range(len(MPALMS_STRIP)):
        fn = NP.cached_frames(_mpalm_raw(i))
        tb.append(('strip', 'mpalm_%d' % i, P.auto_box(fn, N, FPS), N, FPS, fn, MID_K))
    kimg, kl = NP.kites()
    tb.append(('clouds', 'kites', 460, [('kite%d' % i, kimg, x0, y, vx, k) for i, (y, vx, k, x0) in enumerate(kl)]))
    nim, ny = P.crop_pano(near_img())
    tb.append(('pano', 'near', nim, 1.0, 0, ny))
    for (name, box, fn, key) in strips():
        tb.append(('strip', name, box, N, FPS, fn, 1.0, key) if key else ('strip', name, box, N, FPS, fn, 1.0))
    tb.append(('pick', 'rumble', [signal_img(False), signal_img(True)], [0, 1], SIG_BOX[0], SIG_BOX[1], 1.0))
    return tuple(tb)


def compose(camX, t=0.5, state=None):
    return P.compose(table(), camX, t, state)


def anchors():
    anc = {k: list(v) for k, v in ANCHORS.items()}
    anc.update(
        rails=[RAIL_FAR, RAIL_NEAR],
        platform_box=[0, BACK, PLAT_X1, PLAT_EDGE],
        platform_edge=PLAT_EDGE,
        sleepers=dict(period=SLEEPER_P, x0=SLEEPER_X0),
        water_tower=[144, 42, 186, BACK],
        hut=[HUT[0] - 2, 113, HUT[1] + 3, BACK],
        signal_head=list(SIG_BOX),
        back=BACK)
    return anc


def export(ex, BJ):
    tb = table()
    layers = P.export_layers(ex, BJ, tb)
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors())
    if ex.check_on:
        _checks(ex, BJ, st, tb)
    return st


def _checks(ex, BJ, st, tb):
    anc = st['anchors']
    # 可走带平整：铁轨带本来就该是一道清楚的铁轨，站台和碎石地颜色也不一样，所以分开查：
    #   通用项查 x 180–640 的碎石地（排除道床 y 161–176），站台面另查
    cfg = dict(title='铁路', PW=PW, walk=WALK, near=near_img(), opaque_rows=(BACK, H), sky=sky_img(),
               states=[{}, {'rumble': 1}], stand=STAND, required=REQUIRED, size_limit=250 * 1024, cams_step=40,
               flat=(PLAT_X1 + 8, PW, WALK[0], WALK[1] + 1, 22, 0.012), flat_skip=[(0, BALLAST[0] - 1, PW, BALLAST[1] + 1)])
    P.common_checks(ex, BJ, st, tb, cfg)
    NP.anchor_values(ex, anc, ANCHORS)
    NP.state_checks(ex, BJ, st, ['rumble'], [0, 160, 320], '铁路')
    a = np.array(near_img())
    lum = P._lum(a[..., :3].astype(np.float32))
    seg = lum[WALK[0]:PLAT_EDGE, 0:PLAT_X1]
    ex.checked('站台面 y %d–%d 平整（和中位亮度差 > 22 的像素）' % (WALK[0], PLAT_EDGE - 1),
               int((np.abs(seg - np.median(seg)) > 22).sum()))
    # 铁轨带：两条钢轨轨面整条都是钢色（亮 / 轨缝那一点暗）；枕木上沿 / 下沿正好是 rail_band 的 164 / 172
    bad = 0
    for ry in (RAIL_FAR, RAIL_NEAR):
        row = [tuple(c) for c in a[ry, :, :3].astype(int)]
        bad += sum(1 for c in row if c not in (STEEL[3], STEEL[1]))
    ex.checked('两条钢轨轨面（y %d / %d）整条连续（只有亮钢色和轨缝）' % (RAIL_FAR, RAIL_NEAR), bad)
    sl = [tuple(c) for c in a[:, SLEEPER_X0, :3].astype(int)]
    wood = (SLEEPER[0], SLEEPER[1], SLEEPER[2])
    ok = (sl[RAIL_BAND[0]] in wood and sl[RAIL_BAND[1]] in wood and
          sl[RAIL_BAND[0] - 1] not in wood and sl[RAIL_BAND[1] + 1] not in wood)
    ex.checked('枕木的上下沿正好是 rail_band y %d / %d（外面一行是道床）' % RAIL_BAND, 0 if ok else 1)
    # rumble：开了以后铁轨上确实多了亮光（拼出来的差）
    d0 = BJ.ref_render(st, ex.images, 160, 0.5, {})
    d1 = BJ.ref_render(st, ex.images, 160, 0.5, {'rumble': 1})
    ex.checked('rumble 开 / 关拼出来不一样（铁轨亮光 + 信号机）', 0 if BJ.ndiff(d0, d1) > 30 else 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch9', 'after')
    os.makedirs(od, exist_ok=True)
    full = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    for cx in (0, 320):
        full.paste(compose(cx, 0.5), (cx, 0))
    full.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'egypt_rail_solo.png'))
    print('ok')
