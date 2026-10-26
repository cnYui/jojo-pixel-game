# -*- coding: utf-8 -*-
r"""desert_day —— 第8章「埃及东部沙漠」：白天的石漠。地图 desert_ch8（第 16 战段 1 盖布神 · 沙地）/ glide_ch8（段 2 滑翔）。
2026-10-19 第三轮（desert 组）新画（改前是 later_stages.desert('day')：三条平涂的沙丘带）。
沙丘 / 岩山 / 地面 / 岩石 / 骨头 / 热浪这些零件和 desert_noon.py、desert_night.py 共用，在 desert_parts.py。

地图 640 宽、ground 160、可走带 y 148–178（浅色的沙砾地，压得平、对比低——剧情要在上面画深一档的湿痕和声圈）；侧视平视。
比阿拉伯那张更多碎石和岩丘（“石漠”）；太阳在左上的高天（正午），影子短、往右落。
从左到右（世界坐标）：
  x 0–60      沙砾地：从左边开进来的两道车辙（SPW 吉普停在 anchors.jeep，剧情摆，底图只有地面）
  x 64–92     半埋的路标：一根歪了的铁杆、一块褪色的白铁牌（一行阿拉伯文 + 一个红箭头 →），杆上系的一条破布在风里飘（帧条）
  x 96–150    岩丘 1（anchors.rocks[0] 在它前面）：风化成一摞圆石的花岗岩丘（顶上歪着摞一块），脚下沙堆
  x 160–240   一副骆驼骨架（倒在可走带后沿）、几丛枯草
  x 262–352   岩丘 2（anchors.rocks[1]）：最高的一座，一整块大圆石被一道斜缝劈开 + 右后一块矮岩 + 一块滚落的圆石；
              圆石上一只蜥蜴（帧条）
  x 370–420   一棵金合欢（平顶的伞形树冠，阴影一小块）
  x 437–520   岩丘 3（anchors.rocks[2]）：一道矮的砂岩台坎（层理横着走、裂缝、风蚀洞）+ 脚下几块崩落的棱角石块
  x 500–560   空的沙砾地（anchors.grave，剧情插拐杖的地方，底图只有地面）
  x 560–640   大沙丘（anchors.dune_ndoul = 恩多尔跪坐的点，在沙丘脚下）：迎风坡亮、风纹，沙脊上扬沙（帧条）
天上：高远的蓝天、左上的太阳、几缕卷云、两只盘旋的鸢；远处：红海山地那种嶙峋的暗色岩山（罩着热霾）、地平线一溜热浪；
远景：平的砾石原 + 低丘 + 远沙丘、一根尘卷风；中景：一座座孤立的岩丘（光秃的圆顶 / 圆石堆）、砾石原、干河床、几棵小金合欢。
第三轮（10-19）看图改的：远 / 中景的沙丘改成圆顶的缓丘（尖脊 + 三角影子的小沙丘在埃及远看是一排小金字塔）；
岩丘全部改用 P.boulder_parts / paint_boulders 画（每块圆石按自己的鼓面法线着色，原来的毛刺轮廓远看像趴着的动物）；
卷云挪开太阳（像彗星尾巴）；路标箭头（像红十字）和路标的影子（一大块方的）；夕阳时白天颜色的小动画换色（见图层表 *_ss）。

图层（从后往前）：
  sky          static              320×180 正午的天（顶上深蓝 → 地平线发白）+ 太阳
  sky_sunset   pick   key sunset   0 = 1×1 透明；1 = 夕阳的天（太阳落到右边——西边——的地平线上）
  cirrus       wrap   k 0.04 vx 1  卷云（640 循环）
  kites        strip  k 0.2        高处盘旋的两只鸢（16 帧 @4 fps）
  mtn          pano   k 0.12       远处的岩山
  mtn_sunset   pick   key sunset
  far          pano   k 0.3        远景砾石原 + 远沙丘
  smoke        strip  k 0.3  key smoke  远处坠毁直升机的黑烟柱（从远沙丘后面冒起来，底下一点火光；8 帧 @4 fps）
  shimmer      strip  k 0.3        地平线一带的热浪 + 水光（8 帧 @4 fps）
  devil        strip  k 0.3        砾石原上的一根尘卷风（8 帧 @4 fps）
  far_sunset   pick   key sunset
  shimmer_ss / devil_ss  strip  k 0.3  key sunset  热浪 / 尘卷风的夕阳换色孪生（同框同帧，盖住白天颜色的那条）
  mid          pano   k 0.6        中景的岩丘 / 砾石原
  mid_sunset   pick   key sunset
  near         pano   k 1          可走带 + 路标 + 三座岩丘 + 骆驼骨架 + 金合欢 + 右边的大沙丘（640 宽）
  near_sunset  pick   key sunset   夕阳版近景：整张重画（岩丘 / 沙丘 / 树的影子往左拉得很长），再按夕阳调色
  rag          strip  k 1          路标上系的破布（8 帧 @4 fps）
  lizard       strip  k 1          岩丘 2 的大石头上一只蜥蜴（8 帧 @4 fps）
  spin         strip  k 1          大沙丘脊上被风吹起的细沙（8 帧 @4 fps）
  rag_ss / lizard_ss / spin_ss  strip  k 1  key sunset  破布 / 蜥蜴 / 扬沙的夕阳换色孪生
  sunset       tint   key sunset   #ff9a50 0.12
  —— 滑翔段（key glide = 1 才画；整屏盖住上面所有层，镜头不管在哪都一样，k 0）——
  glide_sky    static key glide    整屏的天（同正午的天）
  glide_cloud  wrap   key glide  vx 14    积云（P.cumulus_sprite：底平、花椰菜顶）+ 卷云（天上要有东西，人在 y 48–150 飞）
  glide_far    wrap   key glide  vx 30    远景：岩山 + 砾石原（规格的“远景”层）
  glide_mid    wrap   key glide  vx 90    中景：岩丘、沙丘、金合欢、干河床（规格的“中景”层）
  glide_ground wrap   key glide  vx 200   地面：沙砾、碎石、枯草（规格的“地面”层）
锚点（素材总表 / 规格的值）：arrive [40,164]、jeep [28,166]、crash [520,108]、rocks [[120,160],[300,158],[470,162]]、
      pebbles（5 颗石子的点）、dune_ndoul [600,150]、grave [560,164]；
      另加 walk_x [8,632]、horizon、rock_tops、smoke_k 0.3（黑烟柱所在远景层的视差）、
      smoke_x（黑烟柱底在远景层里的 x：镜头 camX 时在屏幕 smoke_x − camX·0.3；镜头 320 时正好在 crash 的 x 520）、dune_crest。
剧情摆（背景不画）：SPW 吉普、石子、拐杖墓碑、直升机剪影。
单独运行：python -B tools\bg_new\desert_day.py → tools\bg_new\_preview\ch8\after\desert_day_solo_*.png
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

from engine.core import hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _parts_mod():
    """沙丘 / 岩山 / 地面 / 岩石等零件跟 desert_noon / desert_night 共用（同一个模块名，三张图只加载一次）。"""
    key = 'bg_new_desert_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'desert_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts_mod()
C = P.C
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (148, 178)
CIRRUS_P, CIRRUS_K, CIRRUS_VX = 640, 0.04, 1.0
BIRD_K = 0.2
MTN_K, FAR_K, MID_K = 0.12, 0.3, 0.6
MTNW, FARW, MIDW, BIRDW = P.layer_w(MTN_K), P.layer_w(FAR_K), P.layer_w(MID_K), P.layer_w(BIRD_K)
HZ = 116                      # 地平线（远景砾石原的远边）
BACK = 145                    # 近景沙地的后沿（大致；按列起伏）
N_ANIM, FPS_ANIM = 8, 4.0
N_BIRD = 16
ROCK_BASE = 147
SH_SX, SH_SY = 0.25, 0.34     # 正午的影子：离地 h 的点落到 (x + h·sx, base + h·sy)（太阳高，影子短）
SS_SX, SS_SY = -2.4, 0.22     # 夕阳的影子：太阳在右边（西边）贴着地平线，影子往左拉得很长
SMOKE_X = 296                 # 黑烟柱底在远景层（k 0.3）里的 x：镜头 320 时在屏幕 296 − 96 = 200 = 世界 520（crash）
GLIDE_P = 640                 # 滑翔段 wrap 层的周期
# 规格：远 / 中 / 地面 ≈ 30 / 90 / 200；中景取 88——90 的话 std_checks 里 t = 0.1 那一帧 0.1 × 90 正好落在整数上，
# 浮点取整差 1 px，wrap 闭合那一项会误报（游戏里偏移是连续的，没有区别）
GLIDE_VX = dict(cloud=14.0, far=30.0, mid=88.0, ground=200.0)

ANCHORS = dict(
    arrive=[40, 164],
    jeep=[28, 166],                                    # SPW 吉普停的点（剧情摆）
    crash=[520, 108],                                  # 远处直升机坠落的点（天上；黑烟见 smoke_x）
    rocks=[[120, 160], [300, 158], [470, 162]],        # 三座岩丘前站人的点
    pebbles=[[136, 166], [214, 171], [318, 163], [402, 170], [490, 166]],   # 5 颗石子（剧情摆）：三座岩丘旁边 + 散落
    dune_ndoul=[600, 150],                             # 恩多尔跪坐的点（大沙丘脚下）
    grave=[560, 164],                                  # 埋恩多尔、插拐杖的点（剧情摆）
    walk_x=[8, 632],
)
STAND = ('arrive', 'jeep', 'rocks', 'pebbles', 'dune_ndoul', 'grave')

# ============================================================ 调色（正午、石漠：比阿拉伯那张蓝一点的天、暗一点的岩石）
SKY_STOPS = [(0.0, (84, 140, 206)), (0.2, (110, 162, 218)), (0.42, (150, 190, 228)), (0.56, (192, 214, 228)),
             (0.64, (222, 226, 220)), (1.0, (234, 230, 214))]
HAZE = (226, 222, 206)
MTN_PAL = ((92, 76, 80), (114, 92, 92), (138, 112, 106), (164, 136, 120), (192, 164, 142))
FAR_DUNE = dict(hi=(246, 234, 206), lit=(236, 220, 186), lit2=(228, 210, 176), toe=(220, 200, 166),
                rip=(222, 204, 170), rip_hi=(242, 230, 200), sh=(208, 186, 164), sh_d=(198, 176, 158),
                sh_l=(214, 194, 170), ink=(190, 166, 150))
FAR_FLAT = (222, 202, 166)
MID_DUNE = dict(hi=(250, 236, 200), lit=(238, 216, 172), lit2=(230, 204, 158), toe=(220, 192, 146),
                rip=(220, 190, 146), rip_hi=(248, 230, 192), sh=(204, 170, 140), sh_d=(188, 154, 130),
                sh_l=(214, 182, 150), ink=(170, 134, 116))
MID_FLAT = (222, 196, 154)
NEAR_DUNE = dict(hi=(255, 242, 206), lit=(242, 220, 174), lit2=(234, 206, 158), toe=(226, 196, 150),
                 rip=(224, 194, 148), rip_hi=(250, 232, 192), sh=(204, 166, 136), sh_d=(186, 148, 124),
                 sh_l=(216, 180, 148), ink=(164, 124, 106))
FLOOR = dict(base=(232, 212, 174), rip=(222, 200, 162), rip_hi=(242, 224, 188), lip=(248, 234, 202),
             edge=(210, 186, 148))
GRAVEL = ((196, 170, 136), (176, 148, 118), (214, 192, 158), (150, 124, 104))   # 碎石：中、暗、亮、更暗
ROCK = dict(ink=(66, 46, 46), deep=(92, 64, 58), sh=(120, 86, 74), mid=(156, 116, 94), lit=(188, 150, 118),
            hi=(218, 186, 150),
            red=dict(deep=(98, 60, 52), sh=(128, 82, 66), mid=(166, 112, 86), lit=(196, 146, 110), hi=(224, 182, 142)),
            pale=dict(deep=(104, 80, 70), sh=(134, 108, 92), mid=(172, 140, 114), lit=(204, 174, 142),
                      hi=(230, 206, 172)))
BONE = dict(bone=(240, 232, 214), hi=(255, 252, 240), sh=(196, 184, 164), dark=(96, 76, 66), sand=FLOOR['base'],
            sand_hi=FLOOR['rip_hi'], sand_sh=(210, 186, 150))
SHRUB = ((120, 98, 76), (128, 124, 92), (150, 146, 106), (184, 178, 132))
DEAD = ((170, 146, 116), (220, 204, 174), (124, 100, 84))
ACACIA = dict(trunk=(110, 82, 64), trunk_l=(146, 114, 86), leaf_d=(84, 104, 62), leaf=(110, 134, 76),
              leaf_l=(144, 166, 96))
SUNSET_TINT = ('#ff9a50', 0.12)


# ============================================================ 天
@lru_cache(maxsize=1)
def sky_img():
    im = P.sky_base(SKY_STOPS, bands=16)
    P.sun(im, 54, 18, 7, (255, 255, 250), (255, 248, 224), (255, 250, 236), 48, 96, rings=6)
    return im


@lru_cache(maxsize=1)
def sky_sunset_img():
    """夕阳：太阳落到右边（西边）的地平线上，天从顶上的紫蓝 → 橙 → 地平线的金黄。"""
    im = P.sky_base([(0.0, (66, 70, 136)), (0.22, (118, 92, 148)), (0.4, (196, 112, 116)), (0.52, (238, 146, 94)),
                     (0.6, (250, 182, 104)), (1.0, (252, 208, 132))], bands=16)
    P.sun(im, 268, 104, 10, (255, 236, 168), (255, 196, 110), (255, 170, 90), 54, 120, rings=6)
    return im


@lru_cache(maxsize=1)
def cirrus_img():
    # 整条往左转 230 px（循环图，转多少都接得上）：原来开场那一缕卷云正好从太阳里拖出来，像一颗彗星（第三轮看图改）；
    # 转完以后开场时太阳那一带（屏幕 x 0–225）是空的，卷云按 vx 1 往左飘，两分多钟后才经过太阳
    im = P.cirrus_img(CIRRUS_P, 64, 5, 711, (240, 246, 250), (214, 230, 242))
    return Image.fromarray(np.roll(np.array(im), -230, axis=1), 'RGBA')


def birds_frame(f):
    """两只鸢在高处盘旋（比秃鹫小、翅膀窄）。"""
    im = A._new(BIRDW, H)
    d = ImageDraw.Draw(im)
    P.circling(d, f, N_BIRD, 214, 36, 34, 8, 2, (70, 58, 60), (110, 90, 84), 7)
    return im


BIRD_BOX = (172, 22, 256, 50)


# ============================================================ 远景：岩山（k 0.12）
def serrated(w, humps, seed, amp=6.0, fine=2.5, period=None):
    """锯齿状的岩山脊线：几座宽的山体（高斯形的鼓包取最大）+ 一层“脊状噪声”（1 − |n|，尖的峰、圆的谷）+ 一层细碎的齿。
    不用一个个三角形的尖峰——单独的尖锥配上左亮右暗的两个坡面，在埃及的天底下就是一座金字塔（第三轮看图改掉）。"""
    xs = np.arange(w, dtype=np.float64)
    h = np.zeros(w)
    for (cx, ph, hw) in humps:
        for dx in ((-period, 0, period) if period else (0,)):
            u = (xs - cx - dx) / hw
            h = np.maximum(h, ph * np.exp(-u * u))
    n1 = P.fbm1(w, 13.0, seed, octaves=3, period=period)
    ridged = 1 - 2 * np.abs(n1)                                         # 脊状噪声：尖峰
    n2 = P.fbm1(w, 3.0, seed + 1, octaves=2, period=period)
    k = np.clip(h / 8.0, 0, 1)                                          # 山脚那几像素不加齿
    return np.clip(h + amp * ridged * k + fine * n2 * k, 0, None)


def mtn_paint(w, period=None):
    """红海山地那种嶙峋的暗色岩山：后面一道连绵的锯齿山脊（几座宽的山体 + 脊状噪声）、前面一道矮的乱石岭；罩着热霾。
    period 给了就横向循环（滑翔段用）。"""
    im = A._new(w, H)
    humps = [(30, 18, 30), (96, 24, 34), (160, 16, 26), (226, 26, 40), (300, 19, 30), (350, 14, 24)]
    if w > 400:
        humps += [(410, 23, 36), (478, 17, 28), (540, 25, 38), (610, 18, 30)]
    back = serrated(w, humps, 721, amp=6.0, fine=2.0, period=period)
    P.paint_ridge(im, 0, w, HZ + 2, back, MTN_PAL, 722, strata=4, shear=0.7, period=period)
    im = P.haze(im, 0.42, HAZE)
    front = A._new(w, H)
    fh = [(60, 9, 26), (140, 11, 30), (214, 7, 22), (286, 10, 26)]
    if w > 400:
        fh += [(372, 10, 28), (450, 8, 24), (520, 11, 30), (596, 9, 24)]
    fr = serrated(w, fh, 723, amp=3.0, fine=1.5, period=period)
    P.paint_ridge(front, 0, w, HZ + 2, fr, MTN_PAL, 724, strata=3, period=period)
    front = P.haze(front, 0.34, HAZE)
    im.alpha_composite(front)
    return im


@lru_cache(maxsize=1)
def mtn_img():
    return mtn_paint(MTNW)


# ============================================================ 远景：砾石原 + 远沙丘（k 0.3）
def rolling(dunes, widen=1.5):
    """远 / 中景的沙丘改成圆顶的缓丘（鲸背丘、右坡也是余弦坡、背光面宽的抖动过渡）：一排尖脊、右边挂一块三角影子的
    小沙丘在埃及的天底下远看就是一排小金字塔（第三轮看图改）。"""
    for q in dunes:
        q['kind'] = 'whale'
        q['q'] = 0
        q['wr'] *= widen
    return dunes


FAR_DUNES = rolling(P.dune_row(-30, FARW + 30, HZ + 3, 3, 8, 731, ratio=(3.0, 4.2), base_jit=1.0))


def far_paint(w, period=None, dunes=None):
    im = A._new(w, H)
    d = ImageDraw.Draw(im)
    rect(d, 0, HZ, w - 1, 160, FAR_FLAT)
    a = np.array(im)
    nz = P.fbm2(w, H, 16, 2, 732, period=period)
    sp = P.fbm2(w, H, 3, 2, 733, period=period)
    for y in range(HZ, 161):                                          # 砾石原：成片的暗砾 + 亮沙
        for x in range(w):
            if nz[y, x] > 0.6 and sp[y, x] > 0.5:
                a[y, x, :3] = (204, 182, 150)
            elif nz[y, x] < 0.32:
                a[y, x, :3] = (232, 216, 184)
    im = Image.fromarray(a, 'RGBA')
    P.paint_dunes(im, dunes if dunes is not None else FAR_DUNES, FAR_DUNE, 734, ripples=False, streaks=False,
                  period=period)
    d = ImageDraw.Draw(im)
    hl(d, 0, w - 1, HZ, (240, 234, 220))                              # 地平线一道亮（热空气）
    # 砾石原上几座很远的小岩丘（几个像素）
    for i in range(int(w / 70)):
        x = int(hrange(4, w - 12, i, 735))
        ww_, hh_ = int(hrange(5, 10, i, 736)), int(hrange(2, 4, i, 737))
        for k in range(ww_):
            h_ = int(round(hh_ * math.sin(math.pi * (k + 0.5) / ww_)))
            vl(d, x + k, HZ + 4 - h_, HZ + 4, (184, 156, 140) if k < ww_ * 0.6 else (168, 140, 128))
    return P.haze(im, 0.3, HAZE)


@lru_cache(maxsize=1)
def far_img():
    return far_paint(FARW)


SHIM_BOX = (0, HZ - 2, FARW, HZ + 12)


def shimmer_frame(f):
    return P.shimmer_rows(far_img(), SHIM_BOX[1], SHIM_BOX[3], f, N_ANIM, 1.0, 741,
                          mirage=(HZ + 2, HZ + 8, (214, 228, 238), (196, 216, 232)))


DEVIL_X, DEVIL_Y = 130, HZ + 10
DEVIL_BOX = (DEVIL_X - 12, DEVIL_Y - 24, DEVIL_X + 16, DEVIL_Y + 1)


def devil_frame(f):
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    P.dust_devil(d, DEVIL_X, DEVIL_Y, 22, f, N_ANIM, ((236, 222, 196), (216, 196, 168), (196, 174, 150)), 742, lean=4)
    return im


SMOKE_BOX = (SMOKE_X - 12, 30, SMOKE_X + 44, HZ + 6)


def smoke_frame(f):
    """坠毁直升机的黑烟柱：从远沙丘后面（地平线下一点）冒起来，越往上越粗、越淡，被高空的风吹得往右弯；
    一团一团往上滚（每帧往上挪一团的间距）：团的芯是实的黑，边上按离芯的远近抖动（看着是半透明、在翻滚），
    左沿被太阳照亮一线；底下一点火光一闪一闪。"""
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    bx, by = SMOKE_X, HZ + 4
    top = SMOKE_BOX[1] + 3
    # 16 团、每帧往上挪一团，8 帧挪 8 团；每团的样子只看 i % 8 → 第 8 帧和第 0 帧一模一样（首尾闭合）；
    # 从上往下画（下面的团盖住上面的），画的顺序不随帧变
    puffs = sorted(((((i + f) / 16.0) % 1.0), i % 8) for i in range(16))
    for (u, j) in reversed(puffs):
        cy = by - u * (by - top)
        cx = bx + 30 * u ** 2.2 + 1.6 * math.sin(j * 1.7 + u * 7)
        r = 1.8 + 8.0 * u ** 0.85
        rx, ry = r * (1 + 0.5 * u ** 2), r * (1 - 0.2 * u)               # 上面被风拉扁、往两边摊
        for yy in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for xx in range(int(cx - rx) - 1, int(cx + rx) + 2):
                e = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
                if e > 1 or not (SMOKE_BOX[0] <= xx < SMOKE_BOX[2] and SMOKE_BOX[1] <= yy < SMOKE_BOX[3]):
                    continue
                keep = 1.0 if e < 0.45 else (1 - e) / 0.55                # 边上抖动
                keep *= 1.0 if u < 0.7 else max(0.0, 1 - (u - 0.7) * 2.6)   # 顶上散掉
                if hash01(xx - int(cx), yy - int(cy), j, 743) > keep:
                    continue
                side = (xx - cx) / rx
                if side < -0.6 and e > 0.3:
                    c = (124, 114, 110)                                   # 向阳的左沿
                elif e < 0.35:
                    c = (34, 30, 34)
                elif side > 0.2:
                    c = (46, 42, 46)
                else:
                    c = (64, 58, 60)
                if u > 0.5:
                    c = mix(c, (132, 128, 130), (u - 0.5) * 1.1)            # 越高越淡
                px(d, xx, yy, c)
    for k in range(3):                                                # 底下的火光
        if (f + k) % 3:
            px(d, bx - 1 + k, by - 1 - (f + k) % 2, (255, 150, 60) if k != 1 else (255, 210, 120))
    return im


# ============================================================ 中景：岩丘 / 砾石原（k 0.6）
MID_DUNES = rolling(P.dune_row(-60, MIDW + 60, 128, 5, 10, 751) + P.dune_row(-40, MIDW + 60, 141, 5, 9, 752, ratio=(3.2, 4.4)))
MID_HILLS = [(28, 141, 34, 18, 1), (150, 140, 22, 12, 2), (246, 142, 46, 24, 3), (370, 141, 28, 15, 4),
             (452, 142, 40, 20, 5)]


def inselberg_specs(x, base, w, h, seed):
    """一座孤立岩丘的圆石摆法（x = 左脚、base = 脚、w × h = 大致的宽高）。两种，按 seed 挑：
      · 圆顶（bornhardt）：一整块压扁的大圆石当山体，顶上 / 肩上顶着两三块小圆石；
      · 石堆（kopje）：底下两三块大圆石并排，上面再摞一两块。
    第三轮看图改：原来是一个对称的圆鼓包 + 竖条层理 + 裂缝，远看像一座蜂窝茅屋。"""
    sp = []
    sd = seed * 10
    if hash01(seed, 7) < 0.5:
        # 圆顶：山体 + 脚边一两块矮圆石。顶上不摞小石头——圆包上顶两个小圆疙瘩远看是一只青蛙 / 河马的眼睛（第三轮看图改）
        sp.append(dict(cx=x + w * 0.5, base=base, w=w, h=h * 0.82, p=2.0, rnd=1.5, wob=0.05, seed=sd + 1))
        for k in range(1 + int(w > 30)):
            u = (0.08, 0.9)[k] if hash01(seed, 8) < 0.5 else (0.9, 0.08)[k]
            bw = w * hrange(0.2, 0.28, seed, k, 10)
            sp.append(dict(cx=x + w * u, base=base, w=bw, h=bw * hrange(0.45, 0.6, seed, k, 11), p=2.3,
                           seed=sd + 2 + k))
    else:
        # 石堆：底下一排三四块、上面并排两块（上面那排要大，和底下差不多大——一大坨上顶一小块就成了脑袋）
        # 一块占大半的主石 + 两边靠着的两块 + 前面一块小的，大小高低都错开
        # （两排排得整整齐齐的圆石远看像一垛草捆 / 一摞箱子，第三轮看图改的）
        flip = hash01(seed, 23) < 0.5
        for (u, bw, bh, p_, k) in ((0.42, 0.62, 0.95, 2.2, 0), (0.12, 0.32, 0.5, 2.4, 1), (0.8, 0.38, 0.62, 2.3, 2),
                                   (0.58, 0.18, 0.26, 2.0, 3)):
            uu = 1 - u if flip else u
            sp.append(dict(cx=x + w * uu + hrange(-1.5, 1.5, seed, k, 12), base=base, w=w * bw * hrange(0.9, 1.1, seed, k, 13),
                           h=h * bh * hrange(0.9, 1.08, seed, k, 14), p=p_, rot=hrange(-0.12, 0.12, seed, k, 19),
                           seed=sd + 5 + k))
    return sp


def inselberg(im, x, base, w, h, seed, pal, w_img):
    """一座孤立的岩丘（中景）：圆石堆（见 inselberg_specs）、脚下碎石坡；整层最后再罩热霾，所以石头不画裂缝 / 沙漆。"""
    parts = P.boulder_parts(inselberg_specs(x, base, w, h, seed), (w_img, H))
    P.paint_boulders(im, parts, pal, 760 + seed, speck=0.03, grain=0.35, cracks=0, varnish=0)
    d = ImageDraw.Draw(im)
    if hash01(seed, 7) < 0.5 and parts:
        # 圆顶上顺着表面的两道剥落纹（花岗岩圆顶一层层剥落的“洋葱皮”）：一看就是石头，不是一个光溜溜的包
        q = parts[0]
        bx0, by0 = q['box'][0], q['box'][1]
        mm = q['m']
        for depth, ua, ub in ((3, 0.16, 0.6), (6, 0.32, 0.82)):
            for c in range(mm.shape[1]):
                u = c / max(1, mm.shape[1] - 1)
                rows = np.nonzero(mm[:, c])[0]
                if not (ua <= u <= ub) or len(rows) < depth + 3 or hash01(seed, depth, c // 3, 761) < 0.2:
                    continue
                px(d, bx0 + c, by0 + rows[0] + depth, pal['sh'] if u < 0.55 else pal['deep'])
    for k in range(int(w / 3)):                                       # 脚下碎石坡
        xx = x - 3 + int(hrange(0, w + 6, seed, k, 2))
        yy = base - int(hrange(0, 3, seed, k, 3))
        px(d, xx, yy, GRAVEL[k % 4])


def acacia(im, x, y, h, seed, pal, small=False):
    """一棵金合欢：歪的细树干往上分叉，顶上一片扁平的伞形树冠（上沿亮、下沿暗，中间几个空洞透出天）。"""
    d = ImageDraw.Draw(im)
    top = y - h
    # 树干 + 两根分叉
    d.line([(x, y), (x + 1, top + h * 0.45)], fill=C(pal['trunk']))
    d.line([(x + 1, top + h * 0.45), (x - 3, top + 3)], fill=C(pal['trunk']))
    d.line([(x + 1, top + h * 0.45), (x + 5, top + 3)], fill=C(pal['trunk']))
    if not small:
        vl(d, x - 1, int(top + h * 0.5), y, pal['trunk_l'])
    cw = int(h * (1.6 if not small else 1.4))
    for k in range(cw):                                               # 伞形树冠
        u = k / max(1, cw - 1)
        th = int(round((2.5 if small else 4) * math.sin(math.pi * u) ** 0.6)) + 1
        xx = x - cw // 2 + k
        for r in range(th):
            yy = top - r + (1 if hash01(seed, k, 1) < 0.25 else 0)
            if hash01(seed, k, r, 2) < 0.08:
                continue
            c = pal['leaf_l'] if r == th - 1 else (pal['leaf_d'] if r == 0 else pal['leaf'])
            px(d, xx, yy, c)
        px(d, xx, top + 1, pal['leaf_d']) if hash01(seed, k, 3) < 0.5 else None


@lru_cache(maxsize=1)
def mid_img():
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    rect(d, 0, 132, MIDW - 1, 152, MID_FLAT)
    P.paint_dunes(im, MID_DUNES, MID_DUNE, 753, rip_gap=3.8)
    for (x, b, w, h, sd) in MID_HILLS:
        inselberg(im, x, b, w, h, sd, ROCK, MIDW)
    d = ImageDraw.Draw(im)
    # 干河床（一道浅色的弯沙带，边上一溜暗的碎石）
    for x in range(MIDW):
        y = 147 + int(round(1.5 * math.sin(x * 0.03) + 0.8 * math.sin(x * 0.011 + 1)))
        if np.array(im)[y, x, 3] and hash01(x // 2, 754) < 0.9:
            px(d, x, y, (236, 220, 186))
            px(d, x, y + 1, (206, 180, 146))
    for (x, sd) in ((100, 1), (214, 2), (330, 3), (420, 4)):          # 几棵远一点的小金合欢
        acacia(im, x, 143, 9, 755 + sd, ACACIA, small=True)
    d = ImageDraw.Draw(im)
    a = np.array(im)
    for i in range(90):                                               # 砾石点
        x, y = int(hrange(0, MIDW, i, 756)), int(hrange(140, 152, i, 757))
        if a[y, x, :3].tolist() == list(MID_FLAT):
            px(d, x, y, GRAVEL[i % 4])
    ys = np.arange(H, dtype=np.float32)[:, None]
    amt = np.clip(0.22 - (ys - 90) / 60 * 0.12, 0.08, 0.22)
    return P.haze(im, amt, HAZE)


# ============================================================ 近景
def back_line():
    """近景沙地后沿每列的 y：缓缓起伏。"""
    n = P.fbm1(PW, 40.0, 771, octaves=3)
    return np.round(BACK + 2.0 * n).astype(int)


NEAR_DUNES = (P.dune_row(-20, 60, 147, 4, 8, 772) + P.dune_row(150, 250, 147, 4, 8, 773) +
              P.dune_row(340, 440, 147, 4, 7, 774))
for _q in NEAR_DUNES:
    _q['kind'] = 'whale'      # 后沿这几道矮沙垄只有 4–8 px 高：画成没有滑落面的鲸背丘（带月牙影的小三角远看像小金字塔）
# 恩多尔的大沙丘：迎风坡从 x 508 慢慢升到地图右边的沙脊（x 636），滑落面在地图外——
# 只露出一道长长的、上面圆鼓的迎风坡（两边都是直坡的大三角在埃及就是金字塔，第三轮看图改掉）
BIG_DUNE = dict(cx=636.0, top=112.0, base=147.0, wl=128.0, wr=40.0, bl=-22.0, p=0.8, q=1.3, wob=1.5)
SIGN = (76, 147)              # 路标杆脚


# 三座岩丘：一摞摞风化的花岗岩圆石（P.boulder_parts / paint_boulders：每块按自己的“鼓面”法线着色，块和块之间一道缝）。
# 第三轮看图改：原来用抖过轮廓的多边形拼、按左右距离着色，轮廓上一圈毛刺，岩丘 3 远看像一群趴着的刺猬 / 骆驼。
# 每块 dict(cx, base, w, h, p, seed, …)：p 越大越方；从后往前排（后排的先画，前面的压住它）。
ROCK_SPECS = [
    # 岩丘 1（x 120）：一块大圆石、右边一块、顶上歪着摞一块（偏左，不在正中——正中摞一块像个脑袋）、前面一块小的；
    # 左脚是沙堆（sand_drift），不再放小圆石（被沙堆盖一半，像伸出来的一个嘴）
    [dict(cx=118, base=ROCK_BASE, w=36, h=24, p=2.3, seed=11),
     dict(cx=139, base=ROCK_BASE, w=20, h=15, p=2.2, seed=12),
     dict(cx=109, base=127, w=22, h=11, p=2.4, bury=0.1, rot=-0.12, seed=13),
     dict(cx=128, base=ROCK_BASE, w=11, h=6, p=2.0, seed=15)],
    # 岩丘 2（x 300，最高）：右后一块矮岩；一整块大圆石被一道斜的裂缝劈开（同一个形状按一条斜线切成两半，右半往右挪 1 px；
    # 缝不在正中、是斜的——正中一道竖缝的圆石远看像一颗咖啡豆）；前面一块滚落的圆石（蜥蜴趴在它顶上）；左脚一块碎石
    [dict(cx=324, base=ROCK_BASE, w=26, h=28, p=2.6, seed=21),
     dict(cx=292, base=ROCK_BASE, w=41, h=39, p=2.35, rnd=2.2, wob=0.05, cut=(299, -0.2, 'L'), seed=22),
     dict(cx=293, base=ROCK_BASE, w=41, h=39, p=2.35, rnd=2.2, wob=0.05, cut=(299, -0.2, 'R'), seed=22),
     dict(cx=342, base=ROCK_BASE, w=17, h=11, p=2.0, seed=24),
     dict(cx=269, base=ROCK_BASE, w=10, h=6, p=2.0, seed=25)],
    # 岩丘 3（x 470）：一道矮的砂岩台坎（LEDGE，层理横着走，见 rock_piles）+ 脚下几块崩落的棱角石块
    # （第三轮看图改：原来是一排圆包 / 分面石块，远看都像一窝趴着的动物）
    [dict(cx=452, base=ROCK_BASE, w=10, h=6, p=3.0, rnd=1.6, rot=0.25, facets=3, seed=34),
     dict(cx=500, base=ROCK_BASE, w=9, h=5, p=3.0, rnd=1.6, rot=-0.2, facets=3, seed=35),
     dict(cx=515, base=ROCK_BASE, w=12, h=5, p=3.2, rnd=1.6, rot=0.3, facets=3, seed=36)],
]
ROCK_CRACKS = (1, 1, 0)       # 每块圆石几道裂缝（岩丘 3 的崩落石块小，不画）
# 岩丘 3 的砂岩台坎：顶上大致平、一级级往两边低下去（P.shade_rock 着色：层理、裂缝、风蚀洞、沙漆）
LEDGE_PTS = [(437, ROCK_BASE), (438, 142), (442, 138), (449, 136), (457, 135), (462, 132), (471, 131), (481, 130),
             (486, 132), (492, 133), (497, 136), (503, 139), (507, 143), (511, ROCK_BASE)]
LEDGE_BANDS = [(3, 'pale'), (4, None), (3, 'red'), (4, None), (40, 'pale')]


@lru_cache(maxsize=1)
def ledge_mask():
    return P.poly_m((PW, H), [P.rough_poly(LEDGE_PTS, 37, 0.5, step=3.0)])


@lru_cache(maxsize=1)
def rock_piles():
    """三座岩丘：[(圆石几何 parts, 合起来的遮罩, 顶 [x, y]), ...]（世界坐标）；岩丘 3 的遮罩含砂岩台坎。"""
    out = []
    for i, sp in enumerate(ROCK_SPECS):
        parts = P.boulder_parts(sp, (PW, H))
        m = P.boulder_union(parts, (PW, H))
        if i == 2:
            m = m | ledge_mask()
        ys, xs = np.nonzero(m)
        j = int(np.argmin(ys))
        out.append((parts, m, [int(xs[j]), int(ys[j])]))
    return out


def rock_polys():
    """兼容旧名：[(遮罩, 顶 [x, y]), ...]。"""
    return [(m, tip) for (parts, m, tip) in rock_piles()]


ACACIA_X, ACACIA_H = 392, 31


def draw_tracks(im):
    """从左边开进来的两道车辙（很淡，只压在可走带里，不挡事）。"""
    d = ImageDraw.Draw(im)
    for (y0, k) in ((157, 0), (166, 1)):
        for x in range(0, 70):
            if hash01(x // 3, y0, 781) < 0.8:
                yy = y0 + (1 if (x // 11 + k) % 2 else 0)
                px(d, x, yy, FLOOR['rip'])
                if x % 4 == 0:
                    px(d, x, yy + 1, FLOOR['rip_hi'])


def sign_plate():
    x, y = SIGN
    return [(x - 12, 119), (x + 3, 117), (x + 4, 125), (x - 11, 127)]          # 牌子（往左歪一点）


def sign_mask():
    """路标（杆 + 牌子）的遮罩：算影子用。"""
    m = Image.new('L', (PW, H), 0)
    dd = ImageDraw.Draw(m)
    x, y = SIGN
    dd.line([(x, y), (x - 4, 125)], fill=255)
    dd.line([(x + 1, y), (x - 3, 125)], fill=255)
    dd.polygon(sign_plate(), fill=255)
    return np.array(m) > 0


def draw_sign(im, mode):
    """半埋的路标：歪的铁杆、褪色的白铁牌（锈斑、一个红箭头、一行阿拉伯文的笔画），杆脚堆着沙。"""
    d = ImageDraw.Draw(im)
    x, y = SIGN
    pole, pole_l = (96, 92, 96), (140, 136, 138)
    d.line([(x, y), (x - 4, 125)], fill=C(pole))
    d.line([(x + 1, y), (x - 3, 125)], fill=C(dk(pole, 0.8)))
    d.line([(x - 1, y - 2), (x - 5, 127)], fill=C(pole_l)) if mode == 'day' else None
    pl = sign_plate()
    d.polygon(pl, fill=C((222, 216, 200)))
    d.line([pl[0], pl[1]], fill=C((244, 240, 228)))
    d.line([pl[3], pl[2]], fill=C((120, 104, 92)))
    d.line([pl[1], pl[2]], fill=C((150, 136, 120)))
    for (sx, sy) in ((x - 10, 120), (x - 9, 120), (x - 7, 120), (x - 6, 120), (x - 5, 121), (x - 3, 120), (x - 2, 120)):
        px(d, sx, sy, (60, 70, 90))                                    # 一行阿拉伯文（几笔连写的笔画）
    # 红箭头 →：6 px 的杆 + 三个像素的箭头（第三轮看图改：原来箭头在杆中间、上下各一点，看着像一个红十字）
    red = (150, 50, 40)
    hl(d, x - 9, x - 4, 123, red)
    for (sx, sy) in ((x - 4, 122), (x - 4, 124), (x - 3, 123)):
        px(d, sx, sy, red)
    for (sx, sy) in ((x + 1, 119), (x + 2, 122), (x - 10, 126), (x + 2, 124)):
        px(d, sx, sy, (170, 110, 70))                                  # 锈斑
    # 杆脚的沙堆
    P.sand_drift(im, x - 7, x + 6, y, x - 2, 3, FLOOR, 782)


def draw_skeleton(im):
    P.camel_skeleton(im, 186, ROCK_BASE, BONE, seed=3)


def draw_shrubs(im, back):
    for (x, w, h, sd) in ((54, 10, 7, 1), (156, 9, 6, 2), (246, 11, 8, 3), (360, 8, 6, 4), (426, 10, 7, 5),
                          (528, 9, 6, 6)):
        y = int(back[x]) + 3
        P.shrub(im, x, y, w, h, sd * 17 + 3, SHRUB)
    d = ImageDraw.Draw(im)
    for (x, h, sd) in ((16, 4, 1), (92, 5, 2), (176, 4, 3), (238, 5, 4), (350, 4, 5), (412, 5, 6), (508, 4, 7),
                       (546, 5, 8), (630, 4, 9)):
        y = int(back[x]) + 2
        P.tuft(d, x, y, h, (196, 178, 122), (164, 144, 100), sd * 7 + 1, lean=1)


def draw_gravel(im, back, mode):
    """石漠：后沿那一条多撒碎石（大小不一、亮上沿暗下沿），可走带里只撒很少、很淡的小砾（不和剧情的石子道具混）。"""
    d = ImageDraw.Draw(im)
    for i in range(140):
        x = int(hrange(0, PW, i, 791))
        if back[x] + 1 > WALK[0] - 2:                                   # 后沿那一条太窄的地方不撒
            continue
        y = int(hrange(back[x] + 1, WALK[0] - 1, i, 792))               # 石子 + 它脚下那一线影都在可走带前面
        if hash01(i, 793) < 0.25:
            continue
        w = 2 if hash01(i, 794) < 0.6 else 3
        P.pebble(d, x, y, GRAVEL[0], GRAVEL[2], GRAVEL[1], w=w, h=1 if w == 2 else 2)
    peb = ANCHORS['pebbles'] + [ANCHORS['grave'], ANCHORS['jeep'], ANCHORS['dune_ndoul']]
    for i in range(70):
        x = int(hrange(0, PW, i, 795))
        y = int(hrange(WALK[0] + 4, H - 1, i, 796))
        if any(abs(x - px_) < 14 and abs(y - py_) < 8 for (px_, py_) in peb):
            continue
        if hash01(i, 797) < 0.4:
            continue
        px(d, x, y, FLOOR['rip'])
        px(d, x + 1, y, FLOOR['rip_hi'])


def acacia_mask():
    """金合欢树冠的大致形状（算影子用）。"""
    m = np.zeros((H, PW), bool)
    top = ROCK_BASE - ACACIA_H
    cw = int(ACACIA_H * 1.6)
    m[top - 4:top + 2, ACACIA_X - cw // 2:ACACIA_X + cw // 2] = True
    m[top:ROCK_BASE, ACACIA_X - 1:ACACIA_X + 2] = True
    return m


@lru_cache(maxsize=2)
def near_build(mode='day'):
    """近景（mode 'day' = 正午；'sunset' = 夕阳版：太阳在右边贴着地平线，岩石右边亮、影子往左拉得很长，沙丘的明暗反过来）。
    夕阳版画完还是正午的颜色，导出时再按亮度映射成夕阳的颜色（pick 盖在正午那张上，像素位置一模一样）。"""
    im = A._new(PW, H)
    back = back_line()
    sunset = mode == 'sunset'
    if sunset:
        # 沙丘的明暗反过来：迎风坡（左）背光、滑落面（右）迎着夕阳——用一套“反着的”调色板，形状不变
        pal = dict(NEAR_DUNE, hi=NEAR_DUNE['sh_l'], lit=NEAR_DUNE['sh'], lit2=NEAR_DUNE['sh'], toe=NEAR_DUNE['sh_d'],
                   rip=NEAR_DUNE['sh_d'], rip_hi=NEAR_DUNE['sh_l'], sh=NEAR_DUNE['lit'], sh_d=NEAR_DUNE['hi'],
                   sh_l=NEAR_DUNE['lit2'])
    else:
        pal = NEAR_DUNE
    P.paint_dunes(im, NEAR_DUNES + [BIG_DUNE], pal, 801, rip_gap=3.4)
    P.paint_floor(im, 0, PW, back, H - 1, FLOOR, 802, gap0=3.0, gap1=8.5, dash=0.3)
    draw_tracks(im)
    # 影子（先压在地上再画东西）
    sx, sy = (SS_SX, SS_SY) if sunset else (SH_SX, SH_SY)
    rocks = rock_piles()
    shadows = np.zeros((H, PW), bool)
    for (parts, m, tip) in rocks:
        shadows |= P.rock_shadow(m, ROCK_BASE, sx, sy, ground_top=ROCK_BASE)
    shadows |= P.rock_shadow(acacia_mask(), ROCK_BASE, sx, sy, ground_top=ROCK_BASE)
    # 路标的影子按杆 + 牌子的真实形状投（第三轮看图改：原来用整块矩形投，地上一大块灰方块）
    shadows |= P.rock_shadow(sign_mask(), ROCK_BASE, sx, sy, ground_top=ROCK_BASE, dilate=0)
    if sunset:
        dm = np.zeros((H, PW), bool)                                   # 大沙丘也投一大片影子到左边
        for x in range(int(BIG_DUNE['cx'] - BIG_DUNE['wl']), PW):
            y0 = int(round(P.dune_y(x, BIG_DUNE['cx'], BIG_DUNE['top'], BIG_DUNE['base'], BIG_DUNE['wl'],
                                    BIG_DUNE['wr'], BIG_DUNE['p'], BIG_DUNE['q'])))
            dm[y0:ROCK_BASE, x] = True
        shadows |= P.rock_shadow(dm, ROCK_BASE, sx, sy, ground_top=ROCK_BASE)
    shadows &= np.arange(H)[:, None] >= back[None, :]
    P.apply_shadow(im, shadows)
    light = 'right' if sunset else 'left'
    # 岩丘 3 的砂岩台坎先画（崩落的石块压在它脚下）
    P.shade_rock(im, ledge_mask(), ROCK, 813, bands=LEDGE_BANDS, cracks=3, holes=2, varnish=3, light=light)
    for (parts, m, tip), i in zip(rocks, range(3)):
        P.paint_boulders(im, parts, ROCK, 810 + i, light=light, cracks=ROCK_CRACKS[i], varnish=1)
    for (x0, x1, pk, h) in ((94, 108, 99, 4), (264, 278, 269, 5), (440, 452, 444, 4)):
        P.sand_drift(im, x0, x1, ROCK_BASE + 1, pk, h, FLOOR, x0)
    draw_sign(im, mode)
    draw_skeleton(im)
    acacia(im, ACACIA_X, ROCK_BASE, ACACIA_H, 820, ACACIA)
    draw_shrubs(im, back)
    draw_gravel(im, back, mode)
    im = P.opaque(im)
    return im, back, shadows


def near_img():
    return near_build('day')[0]


# ============================================================ 近景上会动的
RAG_ROOT = (SIGN[0] - 3, 129)


def rag_frame(f):
    """路标杆上系的一条破布（褪色的红）：往右飘，一波一波。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y = RAG_ROOT
    ph = math.tau * f / N_ANIM
    for i in range(1, 9):
        u = i / 8
        wav = 1.4 * math.sin(ph - u * 4.0) * u
        hh = 3 if i < 4 else 2
        yy = y + wav + u * 1.5
        for r in range(hh):
            c = (178, 70, 60) if r == 0 else (140, 52, 48)
            if i == 8 and r == hh - 1:
                continue
            px(d, x + i, int(round(yy)) + r, c)
    px(d, x, y, (120, 44, 40))
    return im


RAG_BOX = (RAG_ROOT[0], RAG_ROOT[1] - 3, RAG_ROOT[0] + 10, RAG_ROOT[1] + 7)


def _liz_spot():
    """蜥蜴趴的地方：岩丘 2 前面那块滚落圆石的顶（按画出来的遮罩找 x 340 那一列的顶，石头形状改了也贴得上）。"""
    q = rock_piles()[1][0][3]
    x0, y0 = q['box'][0], q['box'][1]
    return (338, y0 + int(np.argmax(q['m'][:, 340 - x0])))


LIZ = _liz_spot()             # 蜥蜴趴的地方（岩丘 2 前面那块圆石顶上）


def lizard_frame(f):
    """沙色的蜥蜴（侧面朝左）：两帧一次俯卧撑，尾巴尖摆。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y = LIZ
    up = (0, 1, 1, 0, 0, 1, 0, 0)[f]
    col, col2, eye = (170, 146, 104), (204, 182, 136), (40, 30, 30)
    hl(d, x, x + 4, y - 1 - up, col)
    hl(d, x + 1, x + 3, y - 2 - up, col2)
    px(d, x - 1, y - 1 - up, col)
    px(d, x - 2, y - up, col)
    px(d, x - 1, y - 2 - up, eye if f % 4 == 1 else col2)
    for (lx, ly) in ((x, y), (x + 4, y)):
        px(d, lx, ly, col)
    sw = (0, 1, 1, 0, -1, -1, 0, 1)[f]
    for k in range(4):
        px(d, x + 5 + k, y - 1 + (1 if k > 1 else 0) + (sw if k == 3 else 0), col if k < 2 else col2)
    return im


LIZ_BOX = (LIZ[0] - 3, LIZ[1] - 5, LIZ[0] + 10, LIZ[1] + 2)


def spin_frame(f):
    """大沙丘脊上被风吹起的细沙（往右下飘）；只留落在沙丘身上 / 天上的点（沙丘外的天也可以，细沙本来就飘在空中）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    cx, top = int(BIG_DUNE['cx']), int(BIG_DUNE['top'])
    P.spindrift(d, [(cx, top + 1), (cx - 3, top + 2), (cx - 6, top + 4), (cx + 1, top + 3)], f, N_ANIM,
                (255, 248, 226), (240, 224, 192), 830, reach=16)
    return im


SPIN_BOX = (int(BIG_DUNE['cx']) - 7, int(BIG_DUNE['top']) - 2, min(PW, int(BIG_DUNE['cx']) + 20),
            int(BIG_DUNE['top']) + 12)


# ============================================================ 滑翔段（key glide）：整屏重画的五层，全都横向循环、k 0、自己往左卷
CUMULUS_PAL = ((255, 255, 255), (238, 244, 250), (210, 224, 240), (180, 200, 226))


@lru_cache(maxsize=1)
def glide_cloud_img():
    """天上的积云（大小、高低错开，远的小、近的大）+ 几缕卷云：人在 y 48–150 飞，天占了大半个画面，不能是一整片平色。"""
    specs = [(40, 46, 46, 0.42), (138, 30, 30, 0.4), (214, 70, 62, 0.38), (300, 22, 24, 0.42), (372, 56, 40, 0.44),
             (462, 38, 54, 0.4), (548, 78, 70, 0.36), (610, 26, 28, 0.4)]
    im = P.cumulus_row2(GLIDE_P, 96, specs, CUMULUS_PAL, 841)        # 底平、球面明暗的积云（引擎那种锯齿底像一排牙）
    ci = P.cirrus_img(GLIDE_P, 96, 4, 842, (242, 248, 252), (220, 234, 246))
    out = A._new(GLIDE_P, 96)
    out.alpha_composite(ci)
    out.alpha_composite(im)
    return out


GLIDE_FAR_DUNES = rolling(P.dune_row(-30, GLIDE_P + 30, HZ + 3, 3, 8, 851, ratio=(3.0, 4.2), base_jit=1.0))


@lru_cache(maxsize=1)
def glide_far_img():
    """远景（vx 30）：岩山 + 砾石原 + 远沙丘，横向 640 循环；从山脊一直不透明到 y 160（下面中景盖住）。"""
    im = far_paint(GLIDE_P, period=GLIDE_P, dunes=GLIDE_FAR_DUNES)
    m = mtn_paint(GLIDE_P, period=GLIDE_P)
    out = A._new(GLIDE_P, H)
    out.alpha_composite(m)
    out.alpha_composite(im)
    return out


GLIDE_MID_DUNES = rolling(P.dune_row(-40, GLIDE_P + 40, 132, 5, 11, 861) +
                          P.dune_row(-60, GLIDE_P + 60, 146, 6, 12, 862, ratio=(3.2, 4.4)))
GLIDE_HILLS = [(18, 144, 40, 24, 21), (120, 143, 26, 14, 22), (196, 145, 56, 30, 23), (300, 144, 30, 16, 24),
               (380, 145, 48, 26, 25), (470, 143, 24, 12, 26), (530, 145, 60, 32, 27)]


@lru_cache(maxsize=1)
def glide_mid_img():
    """中景（vx 90）：一座座孤立的岩丘、沙丘、干河床、几棵金合欢；从丘顶一直不透明到 y 160。"""
    im = A._new(GLIDE_P, H)
    d = ImageDraw.Draw(im)
    rect(d, 0, 134, GLIDE_P - 1, 160, MID_FLAT)
    P.paint_dunes(im, GLIDE_MID_DUNES, MID_DUNE, 863, rip_gap=3.8, period=GLIDE_P)
    for (x, b, w, h, sd) in GLIDE_HILLS:
        inselberg(im, x, b, w, h, sd, ROCK, GLIDE_P)
    d = ImageDraw.Draw(im)
    for x in range(GLIDE_P):                                          # 干河床（循环的波形：接缝两边对得上）
        y = 152 + int(round(1.5 * math.sin(x * math.tau / GLIDE_P * 5) + 0.8 * math.sin(x * math.tau / GLIDE_P * 13 + 1)))
        if hash01(x // 2, 864) < 0.9:
            px(d, x, y, (236, 220, 186))
            px(d, x, y + 1, (206, 180, 146))
    for (x, sd) in ((84, 1), (168, 2), (262, 3), (350, 4), (444, 5), (506, 6), (612, 7)):
        acacia(im, x, 147, int(hrange(9, 13, sd, 865)), 866 + sd, ACACIA, small=True)
    d = ImageDraw.Draw(im)
    a = np.array(im)
    for i in range(160):                                              # 砾石点
        x, y = int(hrange(0, GLIDE_P, i, 867)), int(hrange(140, 160, i, 868))
        if a[y, x, :3].tolist() == list(MID_FLAT):
            px(d, x, y, GRAVEL[i % 4])
    ys = np.arange(H, dtype=np.float32)[:, None]
    amt = np.clip(0.2 - (ys - 90) / 60 * 0.12, 0.06, 0.2)
    return P.haze(im, amt, HAZE)


GLIDE_GROUND_TOP = 150


@lru_cache(maxsize=1)
def glide_ground_img():
    """地面（vx 200）：沙砾地（风纹）、成片的碎石、几丛枯草、偶尔一块大石头 / 一截白骨；上沿 y 150 附近凹凸（石头 / 草冒出来）。"""
    im = A._new(GLIDE_P, H)
    top = np.round(GLIDE_GROUND_TOP + 1.5 * P.fbm1(GLIDE_P, 30.0, 871, octaves=3, period=GLIDE_P)).astype(int)
    P.paint_floor(im, 0, GLIDE_P, top, H - 1, FLOOR, 872, gap0=2.5, gap1=6.0, dash=0.3, period=GLIDE_P)
    d = ImageDraw.Draw(im)
    for i in range(220):                                              # 碎石（越往下越大 = 越近）
        x = int(hrange(0, GLIDE_P - 4, i, 873))
        y = int(hrange(top[x] + 2, H - 1, i, 874))
        u = (y - GLIDE_GROUND_TOP) / 30.0
        w = 2 if u < 0.4 else (3 if hash01(i, 875) < 0.7 else 4)
        P.pebble(d, x, y, GRAVEL[0], GRAVEL[2], GRAVEL[1], w=w, h=1 if w < 3 else 2)
    for i in range(14):                                               # 冒出地面的大石头
        x = int(hrange(6, GLIDE_P - 20, i, 876))
        y = int(top[x]) + 3
        w, h = int(hrange(5, 12, i, 877)), int(hrange(3, 6, i, 878))
        P.boulder(d, x, y, w, h, dict(ink=ROCK['ink'], sh=ROCK['sh'], mid=ROCK['mid'], lit=ROCK['lit'], hi=ROCK['hi']))
    for i in range(18):                                               # 枯草
        x = int(hrange(4, GLIDE_P - 6, i, 879))
        P.tuft(d, x, int(top[x]) + 2, int(hrange(3, 6, i, 880)), (196, 178, 122), (164, 144, 100), i * 5 + 2, lean=-1)
    for (x, ang) in ((140, 0.2), (412, -0.15)):                        # 两截白骨
        P.bone(d, x, int(top[x]) + 6, 6, BONE, ang)
    return P.opaque(im)


# ============================================================ 帧条缓存
R_RAG = P.cache_frames(rag_frame, N_ANIM, FPS_ANIM)
R_LIZ = P.cache_frames(lizard_frame, N_ANIM, FPS_ANIM)
R_SPIN = P.cache_frames(spin_frame, N_ANIM, FPS_ANIM)
R_SHIM = P.cache_frames(shimmer_frame, N_ANIM, FPS_ANIM)
R_DEVIL = P.cache_frames(devil_frame, N_ANIM, FPS_ANIM)
R_SMOKE = P.cache_frames(smoke_frame, N_ANIM, FPS_ANIM)
R_BIRDS = P.cache_frames(birds_frame, N_BIRD, FPS_ANIM)


# ============================================================ 图层表
SUNSET_MTN = [(0.0, (56, 34, 64)), (0.6, (110, 64, 90)), (0.8, (150, 84, 96)), (1.0, (196, 120, 110))]
SUNSET_FAR = [(0.0, (70, 40, 66)), (0.6, (156, 86, 90)), (0.85, (214, 130, 100)), (1.0, (244, 174, 120))]
SUNSET_MID = [(0.0, (52, 28, 52)), (0.5, (128, 66, 80)), (0.7, (196, 108, 90)), (0.86, (238, 150, 100)),
              (1.0, (255, 198, 132))]
# 夕阳时盖在白天小动画上的“换色孪生”（P.regraded_render）：尘卷风 / 地平线热浪露在换了色的远景上、扬沙 / 蜥蜴 / 破布
# 露在夕阳版近景上都是白天的颜色，很扎眼；key 只能“开了才画”，所以夕阳时再画一条同框同帧、换好色的盖在上面
R_SHIM_SS = P.regraded_render(R_SHIM, SUNSET_FAR, keep=0.2)
R_DEVIL_SS = P.regraded_render(R_DEVIL, SUNSET_FAR, keep=0.2)
R_RAG_SS = P.regraded_render(R_RAG, SUNSET_MID, keep=0.3)
R_LIZ_SS = P.regraded_render(R_LIZ, SUNSET_MID, keep=0.3)
R_SPIN_SS = P.regraded_render(R_SPIN, SUNSET_MID, keep=0.3)


def sunset_near_pick():
    g, y = P.crop_alpha_rows(P.regrade(near_build('sunset')[0], SUNSET_MID, keep=0.3))
    return dict(type='pick', name='near_sunset', key='sunset', values=[0, 1], imgs=[P.blank1(), g], k=1.0, x=0, y=y)


def glide_layers():
    return [dict(type='static', name='glide_sky', img=sky_img(), key='glide'),
            dict(type='wrap', name='glide_cloud', img=glide_cloud_img(), period=GLIDE_P, k=0.0,
                 vx=GLIDE_VX['cloud'], y=0, key='glide'),
            dict(type='wrap', name='glide_far', img=glide_far_img(), period=GLIDE_P, k=0.0, vx=GLIDE_VX['far'], y=0,
                 key='glide'),
            dict(type='wrap', name='glide_mid', img=glide_mid_img(), period=GLIDE_P, k=0.0, vx=GLIDE_VX['mid'], y=0,
                 key='glide'),
            dict(type='wrap', name='glide_ground', img=glide_ground_img(), period=GLIDE_P, k=0.0,
                 vx=GLIDE_VX['ground'], y=0, key='glide')]


@lru_cache(maxsize=1)
def spec():
    """图层表（从后往前）。夕阳（key sunset）：天 / 岩山 / 远中景是梯度映射出来的 pick，近景是整张重画的夕阳版（长影子）；
    滑翔（key glide）的五层排在最后，整屏盖住前面所有东西（镜头在哪都一样）。"""
    near = near_img()
    L = [dict(type='static', name='sky', img=sky_img()),
         dict(type='wrap', name='cirrus', img=cirrus_img(), period=CIRRUS_P, k=CIRRUS_K, vx=CIRRUS_VX, y=0),
         dict(type='strip', name='kites', box=BIRD_BOX, n=N_BIRD, fps=FPS_ANIM, fn=R_BIRDS, k=BIRD_K),
         dict(type='pick', name='sky_sunset', key='sunset', values=[0, 1], imgs=[P.blank1(), sky_sunset_img()], k=0.0),
         dict(type='pano', name='mtn', img=mtn_img(), k=MTN_K),
         P.time_pick('mtn_sunset', 'sunset', mtn_img(), MTN_K, SUNSET_MTN, keep=0.15),
         dict(type='pano', name='far', img=far_img(), k=FAR_K),
         dict(type='strip', name='smoke', box=SMOKE_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_SMOKE, k=FAR_K, key='smoke'),
         dict(type='strip', name='shimmer', box=SHIM_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_SHIM, k=FAR_K),
         dict(type='strip', name='devil', box=DEVIL_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_DEVIL, k=FAR_K),
         P.time_pick('far_sunset', 'sunset', far_img(), FAR_K, SUNSET_FAR, keep=0.2),
         dict(type='strip', name='shimmer_ss', box=SHIM_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_SHIM_SS, k=FAR_K, key='sunset'),
         dict(type='strip', name='devil_ss', box=DEVIL_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_DEVIL_SS, k=FAR_K, key='sunset'),
         dict(type='pano', name='mid', img=mid_img(), k=MID_K),
         P.time_pick('mid_sunset', 'sunset', mid_img(), MID_K, SUNSET_MID, keep=0.25),
         dict(type='pano', name='near', img=near, k=1.0),
         sunset_near_pick(),
         dict(type='strip', name='rag', box=RAG_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_RAG, k=1.0),
         dict(type='strip', name='lizard', box=LIZ_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_LIZ, k=1.0),
         dict(type='strip', name='spin', box=SPIN_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_SPIN, k=1.0),
         dict(type='strip', name='rag_ss', box=RAG_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_RAG_SS, k=1.0, key='sunset'),
         dict(type='strip', name='lizard_ss', box=LIZ_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_LIZ_SS, k=1.0, key='sunset'),
         dict(type='strip', name='spin_ss', box=SPIN_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_SPIN_SS, k=1.0, key='sunset'),
         dict(type='tint', name='sunset', color=SUNSET_TINT[0], alpha=SUNSET_TINT[1], key='sunset')]
    return L + glide_layers()


def compose(camX, t=0.5, state=None):
    return P.compose(spec(), camX, t, state)


# ============================================================ 导出
def export(ex, BJ):
    sp = spec()
    layers = P.export_layers(ex, BJ, sp)
    anchors = dict(ANCHORS)
    anchors.update(horizon=HZ, walk_back=BACK, rock_tops=[r[1] for r in rock_polys()], smoke_k=FAR_K, smoke_x=SMOKE_X,
                   dune_crest=[int(BIG_DUNE['cx']), int(BIG_DUNE['top'])])
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, sp)
    return st


def _checks(ex, BJ, st, sp):
    near, back, shadows = near_build('day')
    P.std_checks(ex, BJ, st, sp, [], '石漠白天', PW, WALK, near, sky_img(), ANCHORS, stand=STAND,
                 opaque_bands=[('远景 地平线以下（y %d–150）整条不透明' % HZ, far_img(), (0, HZ, FARW, 150)),
                               ('中景 丘间平地（y 132–150）整条不透明', mid_img(), (0, 132, MIDW, 150)),
                               ('滑翔 地面层 y %d–179 整条不透明' % (GLIDE_GROUND_TOP + 3), glide_ground_img(),
                                (0, GLIDE_GROUND_TOP + 3, GLIDE_P, H)),
                               ('滑翔 中景层 y 134–159 整条不透明', glide_mid_img(), (0, 134, GLIDE_P, 160)),
                               ('滑翔 远景层 y %d–159 整条不透明' % HZ, glide_far_img(), (0, HZ, GLIDE_P, 160))])
    a = np.array(near)[..., :3].astype(np.float32)
    L = P.lum(a)
    base = np.array(FLOOR['base'], np.float32)
    # 可走带沙色够浅（剧情要在上面画“深一档”的湿痕和声圈）
    # 平整：后沿两行（岩丘 / 骨架 / 沙堆的脚）和影子以外
    wb = L[WALK[0] + 2:WALK[1] + 1]
    msk = ~shadows[WALK[0] + 2:WALK[1] + 1]
    ex.checked('可走带沙色够浅：亮度均值 %.0f ≥ 195' % wb[msk].mean(), 0 if wb[msk].mean() >= 195 else 1)
    std = wb[msk].std()
    ex.checked('可走带（后沿两行、影子以外）亮度标准差 %.1f ≤ 8' % std, 0 if std <= 8 else 1)
    # 剧情要摆东西 / 站人的点：周围只有平地（影子这种同色压暗不算东西）
    shade_col = base * np.array(P.SHADOW_MUL)
    for name in ('arrive', 'jeep', 'grave', 'dune_ndoul'):
        pts = [ANCHORS[name]]
        for (x, y) in pts:
            sub = a[max(WALK[0], y - 4):y + 3, x - 8:x + 9]                # 只看可走带里那几行（dune_ndoul 就在沙丘脚下）
            dev = np.minimum(np.abs(sub - base).max(-1), np.abs(sub - shade_col).max(-1))
            ex.checked('%s 点 (%d,%d) 周围 17×7 只有平地（不是沙 / 影子的像素）' % (name, x, y), int((dev > 30).sum()))
    busy = 0
    for (x, y) in ANCHORS['pebbles']:
        sub = a[y - 3:y + 3, x - 6:x + 7]
        dev = np.minimum(np.abs(sub - base).max(-1), np.abs(sub - shade_col).max(-1))
        busy += int((dev > 30).sum())
    ex.checked('5 个 pebbles 点周围只有平地（剧情摆石子道具，背景不能先画石头）', busy)
    near_rock = sum(1 for (x, y) in ANCHORS['pebbles'] if min(abs(x - r[0]) for r in ANCHORS['rocks']) <= 20)
    ex.checked('pebbles 有 3 颗在岩丘旁边（± 20 px），其余散落（在岩丘旁边的颗数 = %d）' % near_rock,
               0 if near_rock == 3 else 1)
    # 恩多尔的大沙丘：dune_ndoul 那一列后面真的有沙丘（丘面比后沿高 ≥ 20 px）
    x = ANCHORS['dune_ndoul'][0]
    col = np.array(near)[:, x, 3] > 0
    ytop = int(np.argmax(col))
    ex.checked('dune_ndoul (x %d) 后面是大沙丘（丘面 y %d，比后沿高 %d ≥ 20 px）' % (x, ytop, BACK - ytop),
               0 if BACK - ytop >= 20 else 1)
    # 黑烟柱：镜头 320 时烟柱底正好在 crash 的 x（远景层视差 k 0.3）
    sx = SMOKE_X - math.floor(320 * FAR_K)
    ex.checked('smoke 烟柱底：镜头 320 时在屏幕 x %d = crash x %d − 320' % (sx, ANCHORS['crash'][0]),
               abs(sx - (ANCHORS['crash'][0] - 320)))
    # 滑翔：三层 wrap 的速度照规格（远 30 / 中 90 / 地面 200），只在 key glide 时画
    gl = [L_ for L_ in st['layers'] if L_.get('key') == 'glide' and L_['type'] == 'wrap']
    vxs = sorted(L_['vx'] for L_ in gl)
    want = (30.0, 90.0, 200.0)
    ok = all(any(abs(v - w_) <= w_ * 0.05 for v in vxs) for w_ in want)
    ex.checked('glide wrap 层的 vx = %s（含远 ≈ 30 / 中 ≈ 90 / 地面 ≈ 200，± 5%%）' % vxs, 0 if ok else 1)
    # 滑翔：key glide 打开以后，正常的岩山 / 远中近景一个像素都不露（镜头在哪、别的 key 开没开都一样）
    gonly = dict(st, layers=[L_ for L_ in st['layers'] if L_.get('key') == 'glide'], fg=[])
    leak = 0
    for camX in (0, 160, 320):
        for t in (0.0, 1.3, 5.7):
            for extra in ({}, {'smoke': 1}, {'smoke': 1, 'sunset': 1}):
                stt = dict(extra, glide=1)
                leak += BJ.ndiff(BJ.ref_render(st, ex.images, camX, t, stt), BJ.ref_render(gonly, ex.images, camX, t, stt))
    ex.checked('glide = 1 时整屏只有滑翔的五层（3 个镜头 × 3 个时刻 × 3 种 key 组合，露出来的像素）', leak)
    # 滑翔：天（y 0–110）不是一整片平色——每一帧天上都有云（和天底色不一样的像素 ≥ 4%）
    poor = 0
    for t in (0.0, 2.0, 9.0, 21.0):
        g = np.array(BJ.ref_render(gonly, ex.images, 0, t, {'glide': 1}).convert('RGB'))[0:110].astype(np.int32)
        s = np.array(sky_img().convert('RGB'))[0:110].astype(np.int32)
        frac = (np.abs(g - s).max(-1) > 6).mean()
        poor += int(frac < 0.04)
    ex.checked('滑翔的天上一直有云 / 远山（4 个时刻里和底色不同的像素 < 4% 的次数）', poor)
    fr = np.concatenate([np.array(compose(cx, 0.5).convert('RGB'))[108:148].astype(np.float32) for cx in (0, 160, 320)], 1)
    ex.note('可走带亮度：均值 %.0f、标准差 %.1f；后面那一条（镜头 0 / 160 / 320 拼出来）y108–147 均值 %.0f、标准差 %.1f' %
            (wb[msk].mean(), std, P.lum(fr).mean(), P.lum(fr).std()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch8', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        compose(camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'desert_day_solo_%d.png' % camX))
    compose(0, 0.5, {'glide': 1}).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
        os.path.join(od, 'desert_day_solo_glide.png'))
    print('ok')
