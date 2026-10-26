# -*- coding: utf-8 -*-
r"""desert_noon —— 第6章「阿拉伯沙漠」：正午，热得发白。地图 desert_ch6（骑骆驼 + 第 12 战「太阳」）。
2026-10-18 第二轮（desert 组）按体验版精度重画（改前是 later_stages.desert('noon')：三条平涂的沙丘带 + 一个圆太阳）。
沙丘 / 天 / 岩石 / 骨头 / 热浪这些零件和 desert_night.py、desert_day.py 共用，在 desert_parts.py。
2026-10-19 第三轮按游玩脚本定稿改布局：镜子穹顶先藏在 dome（x 160，岩石 1 和低沙丘之间一块后沿“直得古怪”的平沙地，
6-03 的伏笔），被打裂后跑到 dome2（x 530，原来那块平沙地）；低沙丘挪到 x 190–300；加 ride_end（骑骆驼终点，岩石 3 的影子里），
岩石 3 的伞盖压低加宽，让 ride_end 和 6-05 众人站的点都落在影子里；沙丘的影子改成贴右坡的月牙（原来像金字塔）。

地图 640 宽、ground 160、可走带 y 148–176（一整片平的沙地，风纹压得很淡）；侧视平视。
太阳在画面左上的天上（逆光一点：光从左上后方来），所以岩石 / 车的影子往人这边、往右落在可走带上——
剧情用影子判“在阴影里”（anchors.shade 是每块岩石在地上的阴影框）。不画第二个太阳（替身的太阳剧情自己画）。
从左到右（世界坐标）：
  x 0–48      众人的车：一辆 80 年代的白色四驱（朝右停着），车顶行李架上绑着皮箱 / 帆布包 / 油桶，车尾挂备胎，
              天线上系着一块红格子头巾（strip 飘）；车身下半截一层沙尘，影子落在右前方（anchors.car = 影子里站人的点）
  x 48–84     三只油桶（两只立着：褪色的蓝 / 锈红，一只躺着）、一只绿色油桶罐；车辙从左边一路压过来
  x 80–136    岩石 1（x 100）：一根上宽下窄的砂岩柱（风蚀的“蘑菇头”），层理、竖裂缝、风蚀洞、沙漆，脚下沙堆 + 一块小石头
  x 136–186   DOME1：一小块平沙地（anchors.dome = 镜子穹顶第一个藏身处，剧情画）：后沿一道笔直的亮边 + 上面一行暗线，
              地面比四周亮一点、一道风纹 / 一颗碎石都没有（穹顶把四周的沙子照进去，“光得古怪”），两头 4 px 抖动过渡
  x 190–300   一道低的近沙丘（风纹 + 贴右坡的月牙影）、几丛骆驼刺 / 干草；x 210 沙里半埋着一个牛头骨（anchors.skull），
              后沿散着几根骨头、一片药西瓜藤；x 262 一棵枯死的金合欢
  x 304–362   岩石 2（x 330）：两层台阶状的方岩（上层窄），一道劈开的竖缝，顶上趴着一只蜥蜴（strip 做俯卧撑）
  x 380–490   第二道低沙丘、灌木
  x 496–552   DOME2：原来那块平沙地（anchors.dome2 = 穹顶逃到的第二处，剧情画；后沿平直、什么都不放，两头 18 px 拉平）
  x 543–607   岩石 3（x 570）：一朵“蘑菇石”（粗柄 + 压低伸宽的硬岩板伞盖，伞盖下面一道深影）；
              ride_end（560,166）和 6-05 众人（rocks[2] − 4 / + 14 / + 30）都在它的影子里
  x 600–640   沙地、干草
天上：几乎发白的天、左上的太阳（大光晕）、很淡的卷云；远处：两道淡紫的岩山（层理、冲沟），岩山前一溜远沙丘 + 平的沙地
（地平线 y 114），地平线上的热浪和“水光”（海市蜃楼）、一根尘卷风；中景：几座大沙丘（迎风坡亮、风纹，滑落面背光）。

图层（从后往前）：
  sky       static           320×180 正午的天（顶上浅蓝 → 地平线发白）+ 太阳 + 光晕
  sky_dusk  pick   key dusk  0 = 1×1 透明；1 = 傍晚的天（紫 → 橙，太阳落到左边的岩山后面：近景的影子都往右下落，太阳得在左边才对得上）
  cirrus    wrap   k 0.04  vx 0.8   卷云（640 循环）
  vultures  strip  k 0.2            高处盘旋的三只秃鹫（16 帧 @4 fps）
  mtn       pano   k 0.12           远处两道岩山（359 宽）
  far       pano   k 0.3            远沙丘 + 地平线前的平沙地（416 宽）
  shimmer   strip  k 0.3            地平线一带的热浪（远景几行按行横移）+ 海市蜃楼的水光（8 帧 @4 fps）
  devil     strip  k 0.3            平沙地上的一根尘卷风（8 帧 @4 fps）
  mid       pano   k 0.6            大沙丘（512 宽）
  heat_mid  strip  k 0.6  key heat  更强的热浪：中景沙丘脚下几行扭得更厉害 + 更多水光（8 帧 @4 fps）
  drift     strip  k 0.6            两座大沙丘脊上被风吹起的细沙（8 帧 @4 fps）
  near      pano   k 1              可走带 + 近沙丘 + 车 + 油桶 + 三块岩石 + 牛头骨 + 枯树 + 灌木（640 宽）
  flag      strip  k 1              车天线上的红格子头巾（8 帧 @4 fps）
  lizard    strip  k 1              岩石 2 顶上的蜥蜴（8 帧 @4 fps）
  *_dk      strip  key dusk         热浪 / 尘卷风 / 扬沙 / 头巾 / 蜥蜴的傍晚换色孪生（同框同帧，盖住正午颜色的那条；10-19 加）
  heat      tint   key heat  #fff0b0 0.14   偏黄
  dusk      tint   key dusk  #7c3c5c 0.10   傍晚调色（打完回程用；天 / 岩山 / 远中近景另有 dusk 的 pick）
锚点：arrive [60,164]、car [30,168]、rocks [[100,166],[330,166],[570,166]]、
      shade [[86,120,140,176],[316,120,370,176],[556,120,610,176]]、skull [210,166]、camels [[250,172],[450,172]]、
      dome [160,147]、dome2 [530,147]、ride_end [560,166]；
      另加 horizon 114、rock_tops（三块岩石顶的 [x, y]）、walk_x [8,632]、walk_back 142。
剧情摆（背景不画）：骆驼、镜子穹顶、阿拉伯·法兹、第二个太阳。车画在底图（剧情不摆车道具）。
单独运行：python -B tools\bg_new\desert_noon.py → tools\bg_new\_preview\ch6\after\desert_noon_solo_*.png
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
    """沙丘 / 天 / 岩石 / 热浪等零件跟 desert_night / desert_day 共用（同一个模块名，三张图只加载一次）。"""
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
WALK = (148, 176)
CIRRUS_P, CIRRUS_K, CIRRUS_VX = 640, 0.04, 0.8
BIRD_K = 0.2
MTN_K, FAR_K, MID_K = 0.12, 0.3, 0.6
MTNW, FARW, MIDW, BIRDW = P.layer_w(MTN_K), P.layer_w(FAR_K), P.layer_w(MID_K), P.layer_w(BIRD_K)
HZ = 114                      # 地平线（远景平沙地的远边）
BACK = 142                    # 近景沙地的后沿（大致；按列起伏）
# 2026-10-19 第三轮改布局（游玩脚本定稿）：镜子穹顶先藏在 dome（x 160），被打裂后跑到 dome2（x 530）。
#   DOME1 = 第一个藏身处：岩石 1 和低沙丘之间一小块后沿“笔直得古怪”的平沙地（6-03 调查的伏笔，所以两头不做过渡）；
#   DOME2 = 原来那块平沙地（两头照旧 18 px 慢慢拉平）。穹顶由剧情画（宽 24、高 8，底在 y 147），这两段后沿下面什么都不放。
DOME1 = (136, 186)
DOME2 = (496, 552)
FLATS = (DOME1, DOME2)
DOME_Y = 141
N_ANIM, FPS_ANIM = 8, 4.0
N_BIRD = 16
ROCK_X = (100, 330, 570)
ROCK_BASE = 146               # 岩石脚（站在可走带后沿）
SH_SX, SH_SY = 0.3, 0.56      # 影子：离地 h 的点落到 (x + h·sx, base + h·sy)

ANCHORS = dict(
    arrive=[60, 164],
    car=[30, 168],                                     # 车影里站人的点（车画在底图，剧情不摆车道具）
    rocks=[[100, 166], [330, 166], [570, 166]],        # 岩石前（影子里）站人的点
    shade=[[86, 120, 140, 176], [316, 120, 370, 176], [556, 120, 610, 176]],
    skull=[210, 166],
    camels=[[250, 172], [450, 172]],
    dome=[160, 147],                                   # 镜子穹顶第一个藏身处（DOME1 中间，穹顶底）
    dome2=[530, 147],                                  # 穹顶逃到的第二处（DOME2）
    ride_end=[560, 166],                               # 骑骆驼的终点：岩石 3 的影子里
    walk_x=[8, 632],
)
STAND = ('arrive', 'car', 'rocks', 'skull', 'camels', 'ride_end')
# 6-05 众人下骆驼后站的点（rocks[2] − 4 / + 14 / + 30）：自检要求都落在岩石 3 的影子里
PARTY_SHADE = [(ANCHORS['ride_end'][0], 166)] + [(ANCHORS['rocks'][2][0] + d, 166) for d in (-4, 14, 30)]

# ============================================================ 调色（正午：发白、低饱和，阴影偏一点紫）
SKY_STOPS = [(0.0, (158, 192, 226)), (0.2, (178, 206, 232)), (0.42, (206, 222, 234)), (0.56, (228, 234, 234)),
             (0.66, (240, 240, 232)), (1.0, (247, 242, 228))]
HAZE = (240, 236, 226)
MTN_PAL = ((112, 88, 100), (136, 108, 116), (162, 132, 130), (190, 158, 142), (214, 186, 160))
FAR_DUNE = dict(hi=(250, 242, 220), lit=(242, 230, 202), lit2=(236, 220, 190), toe=(230, 212, 182),
                rip=(232, 216, 186), rip_hi=(248, 238, 214), sh=(220, 200, 184), sh_d=(210, 188, 176),
                sh_l=(228, 210, 192), ink=(204, 182, 170))
FAR_FLAT = (234, 220, 192)
MID_DUNE = dict(hi=(254, 244, 214), lit=(246, 226, 182), lit2=(238, 212, 164), toe=(228, 198, 152),
                rip=(226, 196, 150), rip_hi=(254, 242, 208), sh=(210, 176, 152), sh_d=(194, 158, 142),
                sh_l=(222, 190, 162), ink=(178, 140, 126))
MID_FLAT = (230, 204, 160)
NEAR_DUNE = dict(hi=(255, 244, 210), lit=(244, 222, 176), lit2=(236, 208, 160), toe=(230, 202, 156),
                 rip=(228, 198, 152), rip_hi=(250, 234, 196), sh=(206, 170, 146), sh_d=(188, 150, 134),
                 sh_l=(218, 184, 156), ink=(170, 130, 116))
FLOOR = dict(base=(236, 212, 166), rip=(226, 200, 155), rip_hi=(244, 224, 182), lip=(250, 236, 200),
             edge=(214, 186, 146))
ROCK = dict(ink=(92, 56, 52), deep=(126, 78, 66), sh=(160, 106, 86), mid=(206, 156, 116), lit=(230, 190, 144),
            hi=(248, 222, 180),
            red=dict(deep=(120, 70, 60), sh=(154, 96, 78), mid=(200, 140, 104), lit=(224, 172, 128), hi=(242, 206, 164)),
            pale=dict(deep=(134, 92, 78), sh=(170, 122, 98), mid=(214, 170, 132), lit=(236, 204, 162),
                      hi=(250, 230, 194)))
BONE = dict(bone=(240, 232, 212), hi=(255, 252, 238), sh=(196, 182, 160), dark=(96, 74, 64), sand=FLOOR['base'],
            sand_hi=FLOOR['rip_hi'], sand_sh=(214, 186, 146))
SHRUB = ((122, 98, 78), (144, 128, 100), (168, 154, 118), (198, 186, 148))
DEAD = ((176, 150, 120), (226, 210, 180), (128, 102, 84))
HEAT_TINT = ('#fff0b0', 0.14)
DUSK_TINT = ('#7c3c5c', 0.10)


# ============================================================ 天
@lru_cache(maxsize=1)
def sky_img():
    im = P.sky_base(SKY_STOPS, bands=16)
    P.sun(im, 60, 16, 8, (255, 255, 252), (255, 248, 222), (255, 252, 238), 62, 120, rings=7)
    d = ImageDraw.Draw(im)
    for (dx, dy) in ((-13, 0), (13, 0), (0, -13), (0, 13)):            # 刺眼的四道短光芒（像素十字）
        for k in range(3):
            px(d, 60 + dx + (k if dx > 0 else -k if dx < 0 else 0), 16 + dy + (k if dy > 0 else -k if dy < 0 else 0),
               (255, 254, 246))
    return im


@lru_cache(maxsize=1)
def sky_dusk_img():
    im = P.sky_base([(0.0, (64, 56, 116)), (0.25, (120, 78, 132)), (0.45, (196, 104, 112)), (0.58, (236, 146, 100)),
                     (0.66, (250, 186, 118)), (1.0, (252, 214, 150))], bands=16)
    # 2026-10-19：太阳从右边挪到左边——近景的岩石 / 车影都往右下落（傍晚只换调色、不重画影子），
    # 光源在左边才和影子方向一致
    P.sun(im, 64, 99, 9, (255, 236, 170), (255, 190, 110), (255, 170, 100), 46, 110, rings=6)
    return im


@lru_cache(maxsize=1)
def cirrus_img():
    return P.cirrus_img(CIRRUS_P, 70, 6, 61, (246, 248, 248), (226, 236, 242))


def birds_frame(f):
    im = A._new(BIRDW, H)
    d = ImageDraw.Draw(im)
    P.circling(d, f, N_BIRD, 205, 28, 40, 9, 3, (84, 70, 70), (120, 100, 96), 5)
    return im


BIRD_BOX = (150, 14, 262, 44)


# ============================================================ 远景：岩山（k 0.12）
@lru_cache(maxsize=1)
def mtn_img():
    """远处的岩山：后面一排平顶的砂岩台地（陡崖 + 崖下碎石坡），前面一道矮的嶙峋石岭；都罩着厚厚的热霾。"""
    im = A._new(MTNW, H)
    back = P.mesa_heights(MTNW, [(40, 22, 26, 16), (122, 30, 18, 14), (198, 18, 40, 20), (270, 27, 22, 14),
                                 (342, 20, 30, 16)], 11)
    P.paint_ridge(im, 0, MTNW, HZ + 2, back, MTN_PAL, 12, strata=6, shear=0.5)
    im = P.haze(im, 0.52, HAZE)
    front = A._new(MTNW, H)
    fr = P.ridge_heights(MTNW, [(70, 13, 34, 0.3), (160, 16, 40, -0.2), (232, 10, 30, 0.2), (302, 14, 36, 0.0)], 13,
                         jag=0.35, cell=6.0)
    P.paint_ridge(front, 0, MTNW, HZ + 2, fr, MTN_PAL, 14, strata=3)
    front = P.haze(front, 0.36, HAZE)
    im.alpha_composite(front)
    return im


# ============================================================ 远景：远沙丘 + 平沙地（k 0.3）
FAR_DUNES = P.dune_row(-30, FARW + 30, 116, 4, 9, 23, ratio=(2.8, 4.0), base_jit=1.0)


@lru_cache(maxsize=1)
def far_img():
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    rect(d, 0, HZ, FARW - 1, 160, FAR_FLAT)
    a = np.array(im)
    nz = P.fbm2(FARW, H, 18, 2, 21)
    for y in range(HZ, 161):                                          # 平沙地上几道很淡的横纹（远处的沙垄）
        for x in range(FARW):
            if nz[y, x] > 0.62:
                a[y, x, :3] = (226, 210, 182)
            elif nz[y, x] < 0.3:
                a[y, x, :3] = (240, 228, 204)
    im = Image.fromarray(a, 'RGBA')
    P.paint_dunes(im, FAR_DUNES, FAR_DUNE, 22, ripples=False, streaks=False)
    d = ImageDraw.Draw(im)
    hl(d, 0, FARW - 1, HZ, (246, 240, 226))                           # 地平线一道亮（热空气）
    # 地平线上一支驼队（剪影，罩着热霾）
    P.caravan(d, 132, HZ + 1, 4, (176, 150, 142), (160, 134, 128), seed=3)
    # 平沙地上几座很远的小石丘（只有几个像素）
    for (x, w, h) in ((70, 7, 3), (160, 5, 2), (250, 9, 3), (330, 6, 2), (392, 8, 3)):
        for k in range(w):
            hh = int(round(h * math.sin(math.pi * (k + 0.5) / w)))
            vl(d, x + k, HZ + 4 - hh, HZ + 4, (206, 180, 168) if k < w * 0.6 else (190, 164, 156))
    return P.haze(im, 0.32, HAZE)


SHIM_BOX = (0, HZ - 2, FARW, HZ + 14)


def shimmer_frame(f):
    return P.shimmer_rows(far_img(), SHIM_BOX[1], SHIM_BOX[3], f, N_ANIM, 1.0, 31,
                          mirage=(HZ + 2, HZ + 9, (226, 234, 238), (210, 224, 234)))


DEVIL_X, DEVIL_Y = 330, HZ + 9
DEVIL_BOX = (DEVIL_X - 12, DEVIL_Y - 26, DEVIL_X + 16, DEVIL_Y + 1)


def devil_frame(f):
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    P.dust_devil(d, DEVIL_X, DEVIL_Y, 24, f, N_ANIM, ((240, 228, 206), (222, 204, 180), (204, 184, 164)), 41, lean=5)
    return im


# ============================================================ 中景：大沙丘（k 0.6）
MID_DUNES = (P.dune_row(-60, MIDW + 60, 124, 7, 15, 71) +
             P.dune_row(-40, MIDW + 60, 134, 10, 22, 72, big=[(1, 34), (4, 30)]) +
             P.dune_row(-80, MIDW + 80, 145, 8, 15, 73, ratio=(3.2, 4.4)))
BIG = sorted(MID_DUNES, key=lambda q: q['base'] - q['top'])[-2:]          # 最高的两座：脊上扬沙
BIG[1].update(kind='star', arm=(0.35, 12, 9))                                  # 最高的那座是星状丘


@lru_cache(maxsize=1)
def mid_img():
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    rect(d, 0, 128, MIDW - 1, 152, MID_FLAT)
    P.paint_dunes(im, MID_DUNES, MID_DUNE, 33, rip_gap=3.6)
    # 两三块从沙丘之间冒出来的小岩头（被沙埋了大半的岩脊）
    for (x, b, w, h, sd) in ((300, 139, 16, 9, 1), (92, 140, 10, 6, 2), (455, 141, 12, 7, 3)):
        m = P.poly_m((MIDW, H), [P.rough_poly([(x, b), (x + 2, b - h + 2), (x + w * 0.4, b - h), (x + w - 3, b - h + 1),
                                               (x + w, b)], sd, 0.7)])
        P.shade_rock(im, m, ROCK, 200 + sd, bands=[(3, 'pale'), (40, None)], cracks=1, holes=0, varnish=2)
    d = ImageDraw.Draw(im)
    for i in range(70):                                                # 丘间平地的碎石点
        x, y = int(hrange(0, MIDW, i, 34)), int(hrange(139, 152, i, 35))
        if np.array(im)[y, x, :3].tolist() == list(MID_FLAT):
            px(d, x, y, (206, 178, 140))
    ys = np.arange(H, dtype=np.float32)[:, None]
    amt = np.clip(0.22 - (ys - 80) / 70 * 0.12, 0.08, 0.22)              # 上面（远）罩雾多一点
    return P.haze(im, amt, HAZE)


SPIN_BOXES = [(int(q['cx']) - 2, int(q['top']) - 4, int(q['cx']) + 20, int(q['top']) + 10) for q in BIG]


def drift_frame(f):
    """两座大沙丘脊上被风吹下来的细沙（沿着滑落面往右下飘）。只留落在沙丘身上的点：傍晚的 pick 盖得住，不会剩白点。"""
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    for (cx, top) in [(int(q['cx']), int(q['top'])) for q in BIG]:
        P.spindrift(d, [(cx, top + 1), (cx - 2, top + 2), (cx + 1, top + 3)], f, N_ANIM, (255, 248, 226),
                    (238, 222, 192), cx, reach=15)
    a = np.array(im)
    a[np.array(mid_img())[..., 3] == 0] = 0
    return Image.fromarray(a, 'RGBA')


HEAT_BOX = (0, 124, MIDW, 142)


def heat_mid_frame(f):
    return P.shimmer_rows(mid_img(), HEAT_BOX[1], HEAT_BOX[3], f, N_ANIM, 2.0, 37,
                          mirage=(132, 142, (232, 238, 240), (214, 226, 236)))


# ============================================================ 近景
def back_line():
    """近景沙地后沿每列的 y：缓缓起伏；两段镜子穹顶的地方拉平成直线。
    DOME1（x 136–186）两头只留 2 px 过渡：别处的后沿都在轻轻起伏，只有这一段像用尺子画的（“直得古怪”）；
    DOME2（x 496–552）照原来两头 18 px 慢慢拉平。"""
    n = P.fbm1(PW, 40.0, 51, octaves=3)
    y = BACK + 2.2 * n
    xs = np.arange(PW)
    for (x0, x1), ramp in ((DOME1, 2.0), (DOME2, 18.0)):
        w = np.clip(np.minimum(xs - (x0 - ramp), (x1 + ramp) - xs) / ramp, 0, 1)
        y = y * (1 - w) + DOME_Y * w
    return np.round(y).astype(int)


PATCH = mix(FLOOR['base'], FLOOR['rip_hi'], 0.45)
PATCH_FADE = 4                # 平沙地左右两头抖动过渡的宽度


def paint_dome1_patch(im):
    """DOME1（x 136–186）那一小块平沙地 = 太阳战的伏笔：镜子穹顶把四周的沙子照进去，这块地看着“太光了”——
    没有风纹、比四周亮一点；后沿一道笔直的亮边，亮边上面一行暗线（远边往下掉一点的影），
    这样别处后沿都在轻轻起伏、只有这一段像用尺子画的（6-03 承太郎：“后沿直得像用尺子画的”）。
    左右两头 PATCH_FADE px 用 Bayer 抖动过渡回普通沙地（硬边的亮方块就太假了）。只改 y DOME_Y−1 … 可走带前一行。"""
    a = np.array(im)
    bay = P.bayer(PW, H)
    x0, x1 = DOME1
    for x in range(x0, x1 + 1):
        u = min(x - x0, x1 - x) / float(PATCH_FADE)               # 0 = 两头，≥ 1 = 中段
        for y in range(DOME_Y + 1, WALK[0]):
            if u >= 1 or bay[y, x] < u:
                a[y, x, :3] = PATCH
        if u >= 1 or bay[DOME_Y, x] < u:
            a[DOME_Y, x, :3] = FLOOR['lip']
            a[DOME_Y - 1, x, :3] = NEAR_DUNE['sh_l']
            a[DOME_Y - 1, x, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))


# 低沙丘挪到 x 190–300（第三轮：把 x 136–186 让给 DOME1）；牛头骨（x 210）和枯树（x 262）在它前面
NEAR_DUNES = (P.dune_row(190, 262, 146, 7, 14, 96, ratio=(2.8, 3.8)) + P.dune_row(372, 486, 146, 8, 15, 82) +
              P.dune_row(600, 690, 146, 7, 13, 83))


def rock_masks():
    """三块岩石的形状（多边形拼起来再抖一下轮廓）：返回 [(主体 mask, 伞盖 mask 或 None, 顶 [x, y], 面 [(mask, 档)] 或 None), ...]。"""
    sz = (PW, H)
    out = []
    # 岩石 1（x 100）：上宽下窄的砂岩柱（风把腰磨细了），顶上压着一块平的硬岩板；右前方一块小石头
    cap = P.rough_poly([(78, 100), (81, 95), (93, 93), (110, 92), (122, 94), (126, 98), (124, 102), (112, 105),
                        (92, 105), (81, 104)], 1, 0.8)
    body = P.rough_poly([(88, 104), (114, 104), (112, 116), (115, 128), (121, 139), (124, ROCK_BASE),
                         (82, ROCK_BASE), (85, 138), (90, 125), (87, 114)], 2, 1.2)
    stone = P.rough_poly([(122, ROCK_BASE), (124, 139), (130, 137), (135, 140), (136, ROCK_BASE)], 3, 0.6)
    out.append((P.poly_m(sz, [body, stone]), P.poly_m(sz, [cap]), [102, 92], None))
    # 岩石 2（x 330）：两层台阶状的方岩（上层窄、顶平），竖直的岩面一块块：左侧面亮、正面中间调、右侧面背光
    lower = [(304, ROCK_BASE), (305, 127), (309, 120), (349, 118), (357, 123), (361, 134), (364, ROCK_BASE)]
    upper = [(313, 121), (314, 105), (318, 99), (346, 98), (350, 103), (352, 113), (351, 121)]
    lo_r, up_r = P.rough_poly(lower, 4, 0.7), P.rough_poly(upper, 5, 0.6)
    m2 = P.poly_m(sz, [lo_r, up_r])
    left_f = P.poly_m(sz, [[(300, ROCK_BASE + 1), (300, 120), (311, 118), (310, 127), (309, ROCK_BASE + 1)],
                           [(310, 121), (311, 98), (319, 96), (318, 104), (317, 121)]])
    right_f = P.poly_m(sz, [[(350, ROCK_BASE + 1), (350, 121), (368, 121), (368, ROCK_BASE + 1)],
                            [(341, 122), (341, 99), (356, 99), (356, 122)]])
    front_f = m2 & ~left_f & ~right_f
    out.append((m2, None, [332, 98], [(left_f, 4.2), (front_f, 3.0), (right_f, 1.7)]))
    # 岩石 3（x 570）：蘑菇石：粗一点的柄 + 压得低、伸得宽的伞盖，柄脚一圈台座。
    #   第三轮：骑骆驼的终点 ride_end（560,166）和 6-05 众人（566 / 584 / 600）都要站在它的影子里——
    #   影子落点 = (x + 0.3h, 146 + 0.56h)，y 166 那一行对应离地约 36 px，所以伞盖下沿压到 y 118、两边伸到 x 544–606
    #   伞盖是一层硬岩板：顶面平、略往右斜，两头是崩出来的直角台阶（圆的伞盖像面包，第三轮看图改掉）
    cap3 = P.rough_poly([(543, 112), (544, 106), (548, 104), (549, 100), (557, 98), (572, 97), (588, 96), (597, 97),
                         (600, 100), (604, 101), (607, 107), (606, 112), (602, 116), (590, 118), (575, 119), (562, 119),
                         (552, 118), (546, 116)], 6, 0.7)
    stem = P.rough_poly([(561, 117), (584, 117), (583, 125), (586, 133), (592, 140), (596, ROCK_BASE),
                         (552, ROCK_BASE), (556, 140), (560, 133), (562, 125)], 7, 1.0)
    out.append((P.poly_m(sz, [stem]), P.poly_m(sz, [cap3]), [574, 96], None))
    return out


ROCK_BANDS = [[(12, 'pale'), (9, None), (5, 'red'), (10, None), (5, 'pale'), (8, None), (40, 'red')],
              [(7, 'pale'), (10, None), (5, 'red'), (8, None), (6, 'pale'), (40, None)],
              [(8, 'pale'), (9, None), (6, 'red'), (8, None), (40, 'pale')]]


def draw_car(im):
    """白色四驱（朝右，x 0–48，轮胎着地 y 151）：车身、车窗反着天光、门缝、门把、后视镜、前脸格栅 + 圆灯、黑保险杠、
    轮拱、车顶行李架（皮箱、帆布包、两只绿油桶、一卷帆布）、车尾备胎；下半截一层沙尘。"""
    d = ImageDraw.Draw(im)
    gy = 151
    body, body_s, body_d = (232, 226, 208), (200, 192, 174), (150, 142, 130)
    stripe = (164, 96, 62)
    tire, hub = (44, 40, 44), (160, 156, 150)
    glass, glass_hi = (170, 196, 214), (236, 244, 248)
    ink = (64, 52, 52)
    # 车身下半（含前脸）
    rect(d, 1, 133, 46, 145, body)
    rect(d, 1, 141, 46, 145, body_s)                                  # 下半截背光
    hl(d, 1, 46, 133, (246, 242, 230))
    hl(d, 1, 46, 137, stripe)                                         # 腰线的棕色条
    hl(d, 1, 46, 138, dk(stripe, 0.8))
    rect(d, 33, 129, 46, 133, body)                                   # 引擎盖（比车厢低）
    hl(d, 33, 46, 129, (246, 242, 230))
    # 车厢 + 车窗
    rect(d, 3, 121, 32, 132, body)
    hl(d, 3, 32, 121, (246, 242, 230))
    vl(d, 3, 121, 145, (246, 242, 230))
    for (x0, x1) in ((5, 13), (15, 22), (24, 29)):
        rect(d, x0, 123, x1, 130, glass)
        hl(d, x0, x1, 123, glass_hi)
        for k in range(3):                                            # 斜的反光
            px(d, x0 + 2 + k, 128 - k, glass_hi)
        hl(d, x0, x1, 131, body_d)
    d.polygon([(30, 123), (32, 123), (34, 130), (30, 130)], fill=C(glass))  # 前风挡（斜）
    vl(d, 32, 122, 130, body_s)
    for x in (14, 23):                                                # 门缝
        vl(d, x, 122, 144, body_d)
    for x in (12, 21):                                                # 门把
        hl(d, x - 2, x, 135, (120, 116, 112))
    rect(d, 33, 126, 34, 127, (60, 56, 60))                           # 后视镜
    # 前脸：格栅、圆灯、保险杠
    rect(d, 45, 131, 47, 140, (96, 92, 92))
    for y in range(132, 140, 2):
        hl(d, 45, 47, y, (170, 166, 160))
    d.ellipse((42, 131, 45, 134), fill=C((250, 246, 220)))
    px(d, 43, 132, (255, 255, 255))
    rect(d, 41, 143, 48, 145, (52, 48, 50))
    hl(d, 41, 48, 143, (110, 106, 106))
    rect(d, 0, 143, 3, 145, (52, 48, 50))                             # 后保险杠
    # 轮拱 + 轮胎
    for wx in (11, 37):
        d.ellipse((wx - 6, 139, wx + 6, 151), fill=C((70, 62, 60)))
        d.ellipse((wx - 5, 141, wx + 5, gy), fill=C(tire))
        d.ellipse((wx - 2, 144, wx + 2, 148), fill=C(hub))
        px(d, wx, 146, (90, 86, 84))
        px(d, wx - 1, 144, (210, 206, 200))
        for k in range(-4, 5, 2):                                     # 胎纹（下沿沾着沙）
            px(d, wx + k, gy - 1, (120, 104, 84))
    # 车身下半截的沙尘（底下厚、往上稀）
    a = np.array(im)
    bay = P.bayer(PW, H)
    for y in range(136, 146):
        for x in range(1, 47):
            if a[y, x, 3] and bay[y, x] < (y - 136) / 12.0 * 0.6:
                a[y, x, :3] = mix(tuple(int(v) for v in a[y, x, :3]), (214, 188, 146), 0.55)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    # 车尾备胎（左边露出一半）
    d.ellipse((-4, 125, 5, 139), fill=C(tire))
    d.ellipse((-1, 129, 3, 135), fill=C(hub))
    px(d, 1, 132, (90, 86, 84))
    # 行李架 + 行李
    hl(d, 3, 32, 119, ink)
    for x in (4, 12, 20, 28, 32):
        vl(d, x, 119, 121, ink)
    rect(d, 5, 113, 15, 118, (150, 92, 56))                           # 皮箱
    hl(d, 5, 15, 113, (186, 124, 80))
    vl(d, 10, 113, 118, (110, 64, 40))
    rect(d, 16, 114, 23, 118, (176, 168, 130))                        # 帆布包
    hl(d, 16, 23, 114, (206, 198, 160))
    px(d, 19, 113, (140, 132, 100))
    for x0 in (24, 28):                                               # 两只绿油桶
        rect(d, x0, 112, x0 + 3, 118, (86, 104, 64))
        hl(d, x0, x0 + 3, 112, (120, 140, 90))
        vl(d, x0 + 3, 112, 118, (60, 74, 46))
    rect(d, 6, 110, 14, 112, (196, 176, 136))                         # 一卷帆布
    hl(d, 6, 14, 110, (220, 204, 168))
    # 墨线：车身下沿 / 右沿
    hl(d, 1, 46, 146, ink)
    vl(d, 47, 129, 145, ink)
    vl(d, 0, 121, 142, (120, 112, 104))
    vl(d, ANT[0], 113, ANT[1], (70, 66, 70))                         # 天线（头巾在 strip 里飘）


ANT = (40, 129)               # 天线根


def flag_frame(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y0 = ANT
    top = 113
    ph = math.tau * f / N_ANIM
    for i in range(1, 8):                                             # 红白格子头巾：往右飘、一波一波
        u = i / 7
        wav = 1.3 * math.sin(ph - u * 4.2) * u
        hh = int(round(4 - 2 * u))
        yy = top + 1 + wav + u * 1.2
        for r in range(hh):
            c = (206, 52, 52) if (i + r) % 2 else (244, 236, 226)
            if r == hh - 1:
                c = dk(c, 0.8)
            px(d, x + i, int(round(yy)) + r, c)
    return im


FLAG_BOX = (40, 111, 50, 122)


def draw_drums(im):
    """三只油桶 + 一只油桶罐（x 48–84，站在可走带后沿）：圆柱的左边一线亮、右边暗，两道桶箍，桶顶一圈椭圆亮边，锈斑往下淌。"""
    d = ImageDraw.Draw(im)

    def drum(x0, top, col, seed):
        w, base = 9, 150
        rect(d, x0, top, x0 + w - 1, base, col)
        vl(d, x0 + 1, top + 1, base, lt(col, 0.25))
        vl(d, x0 + 2, top + 1, base, lt(col, 0.12))
        vl(d, x0 + w - 2, top + 1, base, dk(col, 0.78))
        vl(d, x0 + w - 1, top, base, dk(col, 0.6))
        for yy in (top + 4, base - 4):
            hl(d, x0, x0 + w - 1, yy, dk(col, 0.72))
            hl(d, x0 + 1, x0 + 3, yy - 1, lt(col, 0.3))
        hl(d, x0 + 1, x0 + w - 2, top, lt(col, 0.4))
        hl(d, x0 + 2, x0 + w - 3, top + 1, dk(col, 0.7))
        px(d, x0 + 6, top + 1, (60, 56, 56))                          # 桶盖口
        for k in range(3):                                             # 锈
            rx = x0 + int(hrange(2, w - 2, seed, k))
            for j in range(int(hrange(2, 6, seed, k, 1))):
                px(d, rx, top + 5 + j + k * 2, (150, 84, 50))
        hl(d, x0, x0 + w - 1, base, (90, 70, 60))
    drum(49, 136, (70, 108, 150), 1)
    drum(58, 137, (170, 80, 50), 2)
    # 躺着的一只（黄，桶底朝人）
    x0, y0 = 68, 143
    rect(d, x0, y0, x0 + 12, 150, (204, 164, 64))
    hl(d, x0, x0 + 12, y0, (236, 204, 110))
    hl(d, x0, x0 + 12, 150, (140, 104, 40))
    for xx in (x0 + 4, x0 + 8):
        vl(d, xx, y0, 150, (170, 130, 50))
    d.ellipse((x0 + 10, y0, x0 + 15, 150), fill=C((186, 146, 54)))
    d.ellipse((x0 + 11, y0 + 2, x0 + 14, 148), fill=C((150, 112, 40)))
    px(d, x0 + 12, y0 + 3, (236, 204, 110))
    # 油桶罐（绿）
    rect(d, 44, 143, 48, 150, (90, 108, 68))
    hl(d, 44, 48, 143, (126, 146, 96))
    px(d, 45, 142, (70, 70, 70))
    vl(d, 48, 143, 150, (62, 76, 48))


def draw_fragments(im):
    """岩石脚下掉下来的碎岩（贴着可走带后沿，都只有 2–5 px 高）+ 两片贴地的药西瓜藤。"""
    d = ImageDraw.Draw(im)
    rp = dict(ink=ROCK['ink'], sh=ROCK['sh'], mid=ROCK['mid'], lit=ROCK['lit'], hi=ROCK['hi'])
    # DOME1（x 136–186）上一块碎岩都不放：那块平沙地要“干净得古怪”
    for (x, y, w, h) in ((74, 147, 5, 3), (128, 147, 4, 2), (298, 147, 4, 3), (366, 147, 6, 3),
                         (373, 147, 3, 2), (592, 147, 5, 3), (599, 147, 3, 2)):
        P.boulder(d, x, y, w, h, rp)
    P.colocynth(d, 236, 147, 13, 3)
    P.colocynth(d, 470, 146, 12, 7)


def draw_skull_bones(im):
    d = ImageDraw.Draw(im)
    P.ox_skull(im, ANCHORS['skull'][0], ANCHORS['skull'][1] + 1, BONE)
    d = ImageDraw.Draw(im)
    P.bone(d, 194, 148, 6, BONE, 0.15)                                # 后沿散着的骨头（让开 DOME1）
    P.bone(d, 222, 149, 5, BONE, -0.3)
    P.bone(d, 229, 146, 4, BONE, 0.5)
    for (x, y) in ((203, 150), (252, 148)):                           # 两节脊椎骨
        rect(d, x, y - 1, x + 1, y, BONE['bone'])
        px(d, x, y - 1, BONE['hi'])
        px(d, x + 2, y, BONE['sh'])
    mul_box = P.mul_box
    mul_box(im, (204, 168, 217, 168), P.SOFT_MUL)                      # 牛头骨脚下一线影


def draw_plants(im, back):
    d = ImageDraw.Draw(im)
    # 灌木 / 干草都让开 DOME1（x 136–186）和 DOME2（x 496–552）
    for (x, w, h, sd) in ((191, 10, 8, 1), (243, 14, 10, 3), (292, 8, 6, 4), (396, 12, 9, 5),
                          (458, 10, 8, 6), (478, 7, 5, 7), (618, 12, 9, 8)):
        y = int(back[x]) + 3
        P.cast_shadow(im, [(x - 2, y), (x + w // 2 + 3, y), (x + w // 2 + 7, y + 3), (x + 1, y + 3)], mul=P.SOFT_MUL)
        P.shrub(im, x, y, w, h, sd * 11, SHRUB)
    d = ImageDraw.Draw(im)
    for (x, h, sd) in ((232, 5, 2), (300, 7, 3), (372, 5, 4), (412, 6, 5), (490, 4, 6), (604, 6, 7),
                       (630, 5, 8), (20, 4, 9), (214, 5, 10)):
        y = int(back[x]) + 2
        P.tuft(d, x, y, h, (196, 178, 120), (160, 140, 96), sd * 7, lean=1)
    # 可走带前沿（y 176–179，镜头最下面）几撮干草：只有 3–4 px 高，不挡脚
    for (x, sd) in ((96, 1), (268, 2), (444, 3), (590, 4)):
        P.tuft(d, x, 179, 4, (204, 186, 128), (170, 150, 100), sd * 13)
    # 枯死的金合欢
    P.dead_tree(im, 262, int(back[262]) + 2, 40, 5, *DEAD)


def draw_pebbles(im, back):
    d = ImageDraw.Draw(im)
    for i in range(60):
        x = int(hrange(0, PW, i, 71))
        y = int(hrange(back[x] + 2, 178, i, 72))
        if any(abs(x - rx) < 30 for rx in ROCK_X) and y < 152:
            continue
        if any(x0 - 6 < x < x1 + 6 for (x0, x1) in FLATS) and y < 156:
            continue
        if hash01(i, 73) < 0.35:
            continue
        sz = 2 if hash01(i, 74) < 0.7 else 3
        P.pebble(d, x, y, (214, 186, 150), (238, 216, 184), (196, 168, 132), w=sz)
    # 车辙：从左边压过来的两道（淡）
    for (y0, y1) in ((154, 155), (160, 161)):
        for x in range(0, 96):
            if hash01(x // 3, y0, 75) < 0.8:
                px(d, x, y0 + (1 if (x // 9) % 2 else 0), (226, 200, 156))
                if x % 3 == 0:
                    px(d, x, y1 + (1 if (x // 9) % 2 else 0), (244, 224, 184))


@lru_cache(maxsize=1)
def near_parts():
    im = A._new(PW, H)
    back = back_line()
    P.paint_dunes(im, NEAR_DUNES, NEAR_DUNE, 61, rip_gap=3.5)
    P.paint_floor(im, 0, PW, back, H - 1, FLOOR, 62, gap0=3.0, gap1=8.5, dash=0.3)
    paint_dome1_patch(im)
    # 三块岩石：先算影子压在沙地上，再画岩石
    rocks = rock_masks()
    allm = np.zeros((H, PW), bool)
    for (body, cap, tip, faces) in rocks:
        allm |= body
        if cap is not None:
            allm |= cap
    shadows = np.zeros((H, PW), bool)
    for (body, cap, tip, faces) in rocks:
        m = body | cap if cap is not None else body
        shadows |= P.rock_shadow(m, ROCK_BASE, SH_SX, SH_SY, ground_top=ROCK_BASE)
    # 车的影子（车身离地 ≈ 30 px）
    car = np.zeros((H, PW), bool)
    car[110:152, 0:48] = True
    car_sh = P.rock_shadow(car, 151, SH_SX, 0.56, ground_top=151)
    drums = np.zeros((H, PW), bool)
    drums[136:151, 49:67] = True
    drums_sh = P.rock_shadow(drums, 150, SH_SX, SH_SY * 0.8, ground_top=150)
    P.apply_shadow(im, shadows | car_sh | drums_sh)
    # 岩石脚下的沙堆（迎风的左边高）+ 岩石
    for i, ((body, cap, tip, faces), bands) in enumerate(zip(rocks, ROCK_BANDS)):
        P.shade_rock(im, body, ROCK, 100 + i, bands=bands, cracks=3, holes=3, varnish=6, faces=faces)
        if cap is not None:
            # 伞盖在下面的柱子上投一道深影（伞盖底下 3–4 行）
            cm = cap.copy()
            sh1 = np.zeros_like(cm)
            sh2 = np.zeros_like(cm)
            for k in range(1, 3):
                sh1[k:] |= cm[:-k]
            for k in range(3, 6):
                sh2[k:] |= cm[:-k]
            sh1 &= body & ~cap
            sh2 &= body & ~cap & ~sh1
            P.mul_mask(im, sh1, np.array((0.6, 0.52, 0.54), np.float32))         # 紧贴伞盖底下最深（暖的深影）
            P.mul_mask(im, sh2, np.array((0.86, 0.8, 0.82), np.float32))
            # 岩石 3 的伞盖只留一道裂缝（两道竖缝并排像一张脸，第三轮看图改掉）
            P.shade_rock(im, cap, ROCK, 110 + i, bands=[(4, 'pale'), (40, None)], cracks=2 if i == 0 else 1, holes=0,
                         varnish=4)
    for (x0, x1, pk, h) in ((78, 96, 84, 6), (300, 318, 305, 7), (553, 568, 557, 6)):
        P.sand_drift(im, x0, x1, ROCK_BASE + 1, pk, h, FLOOR, x0)
    draw_fragments(im)
    draw_car(im)
    draw_drums(im)
    draw_skull_bones(im)
    draw_plants(im, back)
    draw_pebbles(im, back)
    im = P.opaque(im)
    return im, back, shadows


def near_img():
    return near_parts()[0]


LIZ = (336, 97)               # 蜥蜴趴的位置（岩石 2 顶上）


def lizard_frame(f):
    """蜥蜴（侧面朝左，9×3）：每两帧撑起 / 趴下一次（沙漠蜥蜴的俯卧撑），尾巴尖左右摆。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y = LIZ
    up = (0, 1, 1, 0, 0, 1, 0, 0)[f]
    col, col2, eye = (150, 120, 84), (186, 156, 110), (40, 30, 30)
    hl(d, x, x + 4, y - 1 - up, col)
    hl(d, x + 1, x + 3, y - 2 - up, col2)
    px(d, x - 1, y - 1 - up, col)
    px(d, x - 2, y - up, col)
    px(d, x - 1, y - 2 - up, col2)
    px(d, x - 1, y - 2 - up, eye) if f % 4 == 1 else None
    for (lx, ly) in ((x, y), (x + 4, y)):
        px(d, lx, ly, col)
    sw = (0, 1, 1, 0, -1, -1, 0, 1)[f]
    for k in range(4):
        px(d, x + 5 + k, y - 1 + (1 if k > 1 else 0) + (sw if k == 3 else 0), col if k < 2 else col2)
    return im


LIZ_BOX = (330, 92, 346, 99)

R_FLAG = P.cache_frames(flag_frame, N_ANIM, FPS_ANIM)
R_LIZ = P.cache_frames(lizard_frame, N_ANIM, FPS_ANIM)
R_SHIM = P.cache_frames(shimmer_frame, N_ANIM, FPS_ANIM)
R_DEVIL = P.cache_frames(devil_frame, N_ANIM, FPS_ANIM)
R_DRIFT = P.cache_frames(drift_frame, N_ANIM, FPS_ANIM)
R_HEAT = P.cache_frames(heat_mid_frame, N_ANIM, FPS_ANIM)
R_BIRDS = P.cache_frames(birds_frame, N_BIRD, FPS_ANIM)


# ============================================================ 图层表
DUSK_MTN = [(0.0, (60, 36, 70)), (0.6, (112, 70, 104)), (0.8, (146, 90, 118)), (1.0, (190, 124, 138))]
DUSK_FAR = [(0.0, (70, 40, 70)), (0.6, (146, 88, 108)), (0.85, (204, 126, 118)), (1.0, (238, 168, 130))]
DUSK_MID = [(0.0, (56, 30, 58)), (0.5, (126, 68, 94)), (0.7, (192, 108, 104)), (0.86, (234, 148, 112)),
            (1.0, (255, 194, 140))]
# 傍晚时盖在白天小动画上的“换色孪生”（P.regraded_render，同框同帧、带 key dusk，排在原帧条和那一层的傍晚 pick 后面）：
# 第三轮看图发现傍晚时沙脊扬沙是白的、蜥蜴是绿的、尘卷风 / 热浪也是正午的颜色；key 只能“开了才画”，只好再盖一条换好色的
R_SHIM_DK = P.regraded_render(R_SHIM, DUSK_FAR, keep=0.2)
R_DEVIL_DK = P.regraded_render(R_DEVIL, DUSK_FAR, keep=0.2)
R_DRIFT_DK = P.regraded_render(R_DRIFT, DUSK_MID, keep=0.25)
R_FLAG_DK = P.regraded_render(R_FLAG, DUSK_MID, keep=0.3)
R_LIZ_DK = P.regraded_render(R_LIZ, DUSK_MID, keep=0.3)


@lru_cache(maxsize=1)
def spec():
    """图层表（从后往前）。傍晚（key dusk）：天 / 岩山 / 远景 / 中景 / 近景各有一张梯度映射出来的 pick 盖在原层上
    （同一个视差，像素位置一样），卷云和秃鹫被傍晚的天盖住（傍晚不画）；最后再罩一层很淡的 tint 把小 strip 也染一下。"""
    near = near_img()
    L = [dict(type='static', name='sky', img=sky_img()),
         dict(type='wrap', name='cirrus', img=cirrus_img(), period=CIRRUS_P, k=CIRRUS_K, vx=CIRRUS_VX, y=0),
         dict(type='strip', name='vultures', box=BIRD_BOX, n=N_BIRD, fps=FPS_ANIM, fn=R_BIRDS, k=BIRD_K),
         dict(type='pick', name='sky_dusk', key='dusk', values=[0, 1], imgs=[P.blank1(), sky_dusk_img()], k=0.0),
         dict(type='pano', name='mtn', img=mtn_img(), k=MTN_K),
         P.time_pick('mtn_dusk', 'dusk', mtn_img(), MTN_K, DUSK_MTN, keep=0.15),
         dict(type='pano', name='far', img=far_img(), k=FAR_K),
         dict(type='strip', name='shimmer', box=SHIM_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_SHIM, k=FAR_K),
         dict(type='strip', name='devil', box=DEVIL_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_DEVIL, k=FAR_K),
         P.time_pick('far_dusk', 'dusk', far_img(), FAR_K, DUSK_FAR, keep=0.2),
         dict(type='strip', name='shimmer_dk', box=SHIM_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_SHIM_DK, k=FAR_K, key='dusk'),
         dict(type='strip', name='devil_dk', box=DEVIL_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_DEVIL_DK, k=FAR_K, key='dusk'),
         dict(type='pano', name='mid', img=mid_img(), k=MID_K),
         dict(type='strip', name='heat_mid', box=HEAT_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_HEAT, k=MID_K, key='heat'),
         dict(type='strip', name='drift_a', box=SPIN_BOXES[0], n=N_ANIM, fps=FPS_ANIM, fn=R_DRIFT, k=MID_K),
         dict(type='strip', name='drift_b', box=SPIN_BOXES[1], n=N_ANIM, fps=FPS_ANIM, fn=R_DRIFT, k=MID_K),
         P.time_pick('mid_dusk', 'dusk', mid_img(), MID_K, DUSK_MID, keep=0.25),
         dict(type='strip', name='drift_a_dk', box=SPIN_BOXES[0], n=N_ANIM, fps=FPS_ANIM, fn=R_DRIFT_DK, k=MID_K,
              key='dusk'),
         dict(type='strip', name='drift_b_dk', box=SPIN_BOXES[1], n=N_ANIM, fps=FPS_ANIM, fn=R_DRIFT_DK, k=MID_K,
              key='dusk'),
         dict(type='pano', name='near', img=near, k=1.0),
         P.time_pick('near_dusk', 'dusk', near, 1.0, DUSK_MID, keep=0.3),
         dict(type='strip', name='flag', box=FLAG_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_FLAG, k=1.0),
         dict(type='strip', name='lizard', box=LIZ_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_LIZ, k=1.0),
         dict(type='strip', name='flag_dk', box=FLAG_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_FLAG_DK, k=1.0, key='dusk'),
         dict(type='strip', name='lizard_dk', box=LIZ_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_LIZ_DK, k=1.0, key='dusk'),
         dict(type='tint', name='heat', color=HEAT_TINT[0], alpha=HEAT_TINT[1], key='heat'),
         dict(type='tint', name='dusk', color=DUSK_TINT[0], alpha=DUSK_TINT[1], key='dusk')]
    return L


def compose(camX, t=0.5, state=None):
    return P.compose(spec(), camX, t, state)


# ============================================================ 导出
def export(ex, BJ):
    sp = spec()
    layers = P.export_layers(ex, BJ, sp)
    anchors = dict(ANCHORS)
    rocks = rock_masks()
    anchors.update(horizon=HZ, rock_tops=[r[2] for r in rocks], walk_back=BACK)
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, sp)
    return st


def _checks(ex, BJ, st, sp):
    near, back, shadows = near_parts()
    P.std_checks(ex, BJ, st, sp, [], '沙漠正午', PW, WALK, near, sky_img(), ANCHORS, stand=STAND,
                 opaque_bands=[('远景 地平线以下（y %d–150）整条不透明' % HZ, far_img(), (0, HZ, FARW, 150)),
                               ('中景 丘间平地（y 128–150）整条不透明', mid_img(), (0, 128, MIDW, 150))])
    a = np.array(near)[..., :3].astype(np.float32)
    L = P.lum(a)
    # 每块岩石：高过人（≥ 40 px）、阴影框里可走带那部分大半在影子里、影子比旁边的沙地暗
    tall = 0
    for (body, cap, tip, faces) in rock_masks():
        m = body | cap if cap is not None else body
        ys = np.nonzero(m.any(1))[0]
        tall += 0 if (ROCK_BASE - ys.min()) >= 40 else 1
    ex.checked('三块岩石都高过人（≥ 40 px，不满足的块数）', tall)
    for (x0, y0, x1, y1), rx in zip(ANCHORS['shade'], ROCK_X):
        cov = shadows[WALK[0]:y1, x0:x1].mean()
        ex.checked('岩石 x %d 的阴影框里可走带 %.0f%% 在影子里（≥ 45%%）' % (rx, cov * 100), 0 if cov >= 0.45 else 1)
        sh = L[WALK[0]:y1, x0:x1][shadows[WALK[0]:y1, x0:x1]]
        lit = L[WALK[0]:y1, x1 + 10:x1 + 40]
        ex.checked('岩石 x %d 的影子比旁边沙地暗（%.0f vs %.0f，差 ≥ 25）' % (rx, sh.mean(), lit.mean()),
                   0 if lit.mean() - sh.mean() >= 25 else 1)
        sx, sy = ANCHORS['rocks'][ROCK_X.index(rx)]
        ex.checked('rocks 锚点 (%d,%d) 站在影子里' % (sx, sy), 0 if shadows[sy, sx] else 1)
    cx, cy = ANCHORS['car']
    ex.checked('car 锚点 (%d,%d) 站在车影里' % (cx, cy), 0 if L[cy, cx] < P.lum(np.array(FLOOR['base'], np.float32)) - 25 else 1)
    # 剧情：车影 = @car 左右 22 px 都能躲 → 这一段在 y 168 那一行至少七成是影子
    lum0 = P.lum(np.array(FLOOR['base'], np.float32))
    row = L[cy, cx - 22:cx + 23]
    ex.checked('车影：@car ± 22 px 在 y %d 有 %.0f%% 是影子（≥ 70%%）' % (cy, (row < lum0 - 25).mean() * 100),
               0 if (row < lum0 - 25).mean() >= 0.7 else 1)
    # 6-05 下骆驼后（ride_end + 乔瑟夫 / 波鲁纳雷夫 / 花京院）都站在岩石 3 的影子里，也都在 shade[2] 框里
    b3 = ANCHORS['shade'][2]
    for (x, y) in PARTY_SHADE:
        ok = shadows[y, x] and b3[0] <= x <= b3[2] and b3[1] <= y <= b3[3]
        ex.checked('6-05 站位 (%d,%d) 在岩石 3 的影子里、也在 shade[2] 框里' % (x, y), 0 if ok else 1)
    # 两段镜子穹顶：后沿是一条平直的线，后沿下面到可走带前没有东西（只有沙地的颜色）
    base = np.array(FLOOR['base'], np.float32)
    for name, (x0, x1) in (('dome', DOME1), ('dome2', DOME2)):
        ys = set(back[x0:x1 + 1].tolist())
        ex.checked('%s 一段（x %d–%d）后沿平直（y 的种类 = %d）' % (name, x0, x1, len(ys)), len(ys) - 1)
        sub = a[DOME_Y + 1:WALK[0] + 4, x0 + 6:x1 - 4]
        busy = int((np.abs(sub - base).max(-1) > 22).sum())
        ex.checked('%s 一段后沿下面没有放东西（离沙色太远的像素）' % name, busy)
        ax_, ay_ = ANCHORS[name]
        ex.checked('%s 锚点 (%d,%d) 在这一段中间（穹顶宽 24 放得下）' % (name, ax_, ay_),
                   0 if (x0 <= ax_ - 12 and ax_ + 12 <= x1 and DOME_Y < ay_ < WALK[0]) else 1)
    # DOME1 是伏笔：平沙地中段（去掉两头的抖动过渡）光得古怪，一个风纹 / 碎石都没有，后沿那一行整条是亮边
    x0, x1 = DOME1[0] + PATCH_FADE, DOME1[1] - PATCH_FADE
    rip = int((np.abs(a[DOME_Y + 1:WALK[0], x0:x1 + 1] - np.array(PATCH, np.float32)).max(-1) > 0).sum())
    ex.checked('dome 平沙地（x %d–%d，y %d–%d）光得古怪：没有风纹 / 碎石（不是平沙色的像素）' %
               (x0, x1, DOME_Y + 1, WALK[0] - 1), rip)
    lip = int((np.abs(a[DOME_Y, x0:x1 + 1] - np.array(FLOOR['lip'], np.float32)).max(-1) > 0).sum())
    ex.checked('dome 平沙地后沿 y %d 整条是一道笔直的亮边（不是亮边的像素）' % DOME_Y, lip)
    # 可走带平整：风纹压得很淡（影子 / 车和油桶 / 牛头骨 / 前沿干草以外的地方亮度标准差小）
    wb = L[WALK[0]:WALK[1] + 1]
    msk = ~shadows[WALK[0]:WALK[1] + 1]
    sk = np.zeros_like(msk)
    sk[:, 0:90] = True
    sk[:, ANCHORS['skull'][0] - 12:ANCHORS['skull'][0] + 12] = True
    std = wb[msk & ~sk].std()
    ex.checked('可走带（影子 / 车 / 牛头骨以外）亮度标准差 %.1f ≤ 8' % std, 0 if std <= 8 else 1)
    fr = np.concatenate([np.array(compose(cx, 0.5).convert('RGB'))[108:148].astype(np.float32) for cx in (0, 160, 320)], 1)
    ex.note('可走带亮度：均值 %.0f、标准差 %.1f；后面那一条（镜头 0 / 160 / 320 拼出来）y108–147 均值 %.0f、标准差 %.1f' %
            (wb[msk & ~sk].mean(), std, P.lum(fr).mean(), P.lum(fr).std()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch6', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        compose(camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'desert_noon_solo_%d.png' % camX))
    world = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    world.alpha_composite(near_img())
    world.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'desert_noon_near.png'))
    print('ok')
