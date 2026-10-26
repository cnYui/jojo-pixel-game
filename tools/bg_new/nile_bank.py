# -*- coding: utf-8 -*-
r"""nile_bank —— 第9章「尼罗河岸」：科翁坡北边一个河边小镇的岸，正午（地图 nile_ch9；第 18 战段 2 卡恩、段 3 被附身的波鲁纳雷夫）。
2026-10-19 nile 组按体验版精度新画（改前是 later_stages 的平涂占位）。共用零件在 nile_parts.py。

地图 640 宽、ground 160、可走带 y 148–176（岸上的泥土路：压实的尼罗河泥 + 车辙 + 小石子，对比压得很低）；侧视平视，
人站在路上，背后隔着一道矮石堤（压顶石 y 144、立面 145–147，人掉不进河）就是尼罗河：河面从对岸水线 y 84 一直铺到 y 143，
宽、远处映着天、近处绿褐，对岸的倒影、长亮纹、太阳正下方一竖条日光的反光（strip，跟着镜头不动——太阳在无穷远）、
满河的波光（strip）、会往左流的短水纹（wrap）、三条三角帆船漂过。太阳在左上偏高（正午：影子短、落在正下方偏右）。
从左到右（世界坐标）：
  x 0–100     两棵海枣树（长在堤外的岸上，树干从堤后面伸出来，树冠 strip）、路边给人喝水的两只陶罐（木架上）（anchors.arrive）
  x 100–156   渔夫的地方（anchors.fisher）：压顶石上一只鱼篓、一圈缆绳、一只木桶、一根石头拴船桩
  x 156–214   渔夫的小木船拴在堤外（strip：上下起伏 1 px、船头船尾的小水纹；船身蓝色舷带、斜搭着一支桨、一堆网），
              缆绳拴在桩上（anchors.boat：船前面站人的点）
  x 214–340   打水漂的那一段：只有矮堤，河面干净（anchors.skip_spot 站人、anchors.river [220,140] 是第一跳的水面，
              之后每跳往右 18 px：x 220–328、y 140 一整条都是水，剧情在上面画白色水花圈）；
              x 249–276 一个很矮的晒网架（两根短桩 + 一根横杆在 y 141，渔网搭在杆上垂到堤脚，杆上一串软木浮子；
              anchors.nets），架子右边地上堆着一小堆网
  x 290–470   一棵大树（老无花果树：粗的树干在 x 388–402 堤后面，三根大枝、浓密的树冠 y 14–90，树荫淡淡地落在路上）下面的
              露天理发摊：两根木桩 + 横梁的镜架（圆镜挂在横梁正中，anchors.mirror [330,112]）、左桩上挂一条磨剃刀的皮带、
              横梁右头搭着两条毛巾（strip 飘）、一个铁三脚的搪瓷脸盆架 + 地上的水壶、一张小木桌（梳子、剪刀、刷子、肥皂杯）、
              树干上钉着一块理发店的小招牌（剪刀图）；理发椅（红皮、镀铬扶手、铸铁底座）在可走带里 anchors.barber_chair
              （坐姿的脚点 [330,158]，椅子朝右），是单独的 pick 层：key chair_cut = 1 时换成劈成两半的椅子（两半各往外倒、
              切口露出白色的填充物、地上几块木屑）；理发师卡恩站 anchors.barber
  x 440–520   小茶摊（anchors.tea）：绿白条纹的布篷（波浪边 strip）+ 两根木杆、蓝底黄边的木柜台（阿拉伯文）、铜茶炊
              （顶上冒热气 strip）、一盘红茶玻璃杯、一把薄荷、糖罐；右边一条给客人坐的木长凳
  x 498–546   河上一条停着的三角帆船（strip：上下起伏、倒影晃；anchors.felucca [520,120]）
  x 538–594   芦苇丛（anchors.reeds）：这一段没有石堤，是一道湿泥的岸坡，芦苇比人还高（顶 y ~104，strip 摆）；
              芦苇边一只白鹭在泥里啄食（strip）
  x 594–640   石堤接着往右、堤后一棵海枣树（strip）、一块蓝色路牌（白字 LUXOR + 箭头）（anchors.exit）
远景：对岸（西岸）的台地沙山（平顶 + 台阶 + 冲沟，不画尖顶）、贴水的海枣林 / 甘蔗田、几栋土坯房、一座宣礼塔。

图层（从后往前）：
  sky       static           320×180 正午的天 + 太阳（x 150）
  clouds    wrap   k 0.08 vx 1.0   小积云 + 云丝（640 循环）
  far       pano   k 0.3           远景 416 宽：对岸台地、绿带、房子、宣礼塔、整条河面（y 84–150，带对岸倒影）
  glint     strip  k 0.3           满河的波光（8 帧 @4 fps）
  sunglare  strip  k 0             太阳正下方的一竖条日光反光（跟着镜头不动）
  ripples   wrap   k 0.6 vx −3     会往左流的短水纹（160 循环，y 96–143）
  felucca   clouds k 0.35–0.4      三条三角帆船（带倒影）在远处漂（span 560）
  kites     clouds                 两只高处盘旋的黑鸢
  near      pano   k 1             石堤 + 路 + 岸上的东西（640 宽）
  palm_0…2、boat、felucca_near、reeds、egret、steam、towels、valance   strip k 1（各 8 帧 @4 fps）
  chair_cut pick   k 1  key chair_cut   理发椅：0 = 完整、1 = 劈成两半
锚点（素材总表 §一，第9章，定稿值一个不改）：arrive [40,164]、fisher [130,162]、river [220,140]、skip_spot [190,166]、
      boat [200,150]、nets [262,150]、barber_chair [330,158]、barber [356,160]、mirror [330,112]、tea [470,156]、
      reeds [560,160]、felucca [520,120]、exit [626,162]。
另导出：skip_line（打水漂七跳的水面点 [[220,140] … [328,140]]）、chair_box（理发椅 pick 图的框）、mirror_box、tea_box（茶摊）、
      reeds_box、boat_box、nets_box、tree（大树树干）、embankment 144（压顶石那一行）、water_y 84（对岸水线）。
key：chair_cut（理发椅被劈成两半；pick 层，values [0, 1]）。
单独运行：python -B tools/bg_new/nile_bank.py → tools/bg_new/_preview/ch9/after/nile_bank_solo.png
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
LAD = NP.SST_LADDER

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (148, 176)
EMB = 144                       # 石堤压顶石那一行（145–147 立面；148 起是路）
N, FPS = NP.N, NP.FPS
CLOUD_P, CLOUD_K, CLOUD_VX = 640, 0.08, 1.0
FAR_K = 0.3
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 416
SHORE = 84                      # 对岸水线（远景层）
RIP_Y, RIP_H, RIP_P, RIP_K, RIP_VX = 96, 48, 160, 0.6, -3.0
BOAT_SPAN = 560
SUN = (150, 16)

REED = (538, 594)               # 没有石堤、长芦苇的那一段
SKIP = [[220 + 18 * i, 140] for i in range(7)]                  # 打水漂七跳的水面点（实施文档：第一跳在 @river，每跳往右 18）
SKIP_CLEAN = (212, 124, 338, 140)                               # 这一块近景必须透明（只看得见水）
NETS = (249, 276)               # 晒网架两根短桩
POSTS = (318, 342)              # 镜架两根木桩（左沿）
MIRROR = (330, 112, 7)          # 圆镜中心 + 半径
TRUNK = (388, 402)
TEA = (444, 504)                # 茶摊布篷
CHAIR_BOX = (304, 116, 356, 160)                                # 理发椅 pick 图的框（x0, y0, x1, y1，右下不含）

ANCHORS = dict(arrive=[40, 164], fisher=[130, 162], river=[220, 140], skip_spot=[190, 166], boat=[200, 150],
               nets=[262, 150], barber_chair=[330, 158], barber=[356, 160], mirror=[330, 112], tea=[470, 156],
               reeds=[560, 160], felucca=[520, 120], exit=[626, 162])
STAND = ('arrive', 'fisher', 'skip_spot', 'boat', 'nets', 'barber_chair', 'barber', 'tea', 'reeds', 'exit')
REQUIRED = tuple(ANCHORS)

# 路：压实的尼罗河泥（偏灰的土褐，比沙暗一点，对比低）
ROAD, ROAD_D, ROAD_L = (196, 170, 132), (184, 157, 120), (210, 186, 150)
MUD = ((92, 72, 56), (118, 94, 70), (142, 116, 86))
LEATHER = ((112, 34, 32), (166, 54, 48), (206, 98, 82))
CHROME = ((96, 100, 110), (150, 154, 164), (200, 204, 212), (236, 238, 242))
IRON_C = ((46, 46, 52), (70, 70, 78), (112, 112, 120))
TREE_BARK = ((70, 56, 46), (98, 80, 62), (128, 106, 82), (156, 134, 104))
TREE_LEAF = ((34, 70, 44), (52, 98, 54), (78, 128, 64), (122, 164, 84))


# ============================================================ 天 / 远景
@lru_cache(maxsize=1)
def sky_img():
    return NP.sky_img(NP.SKY_NOON, SUN, sun_r=7)


@lru_cache(maxsize=1)
def clouds_img():
    return NP.clouds_img(29)


@lru_cache(maxsize=1)
def far_img():
    """远景 416 宽：对岸台地（y 50–76）→ 绿带 + 房子 + 宣礼塔（到 y 83）→ 整条河（y 84–150）。罩雾：越远越淡。"""
    im = A._new(FARW, H)
    NP.ridge(im, 0, FARW, 50, 76, 17)
    NP.greenbelt(im, 0, FARW, 64, SHORE, 15, houses=[(58, 8, 5), (68, 10, 6), (206, 9, 5), (318, 12, 6), (332, 7, 4)],
                 minaret=(80, 15))
    NP.water_body(im, 0, FARW, SHORE, 150, 19, refl=10, streaks=0.55)
    amt = np.zeros((H, 1), np.float32)
    amt[:SHORE - 16] = 0.3
    amt[SHORE - 16:SHORE] = 0.16
    amt[SHORE:] = 0.05
    return NP.haze(im, amt)


@lru_cache(maxsize=1)
def ripples_img():
    # 水纹不能太密：满河的白道道会像下雨，人和水花反而看不清
    return NP.ripples_img(RIP_P, RIP_H, 23, dens=0.012, light=mix(NP.NILE_HI, NP.NILE_MID, 0.35))


@lru_cache(maxsize=1)
def _glint_raw():
    return NP.glint_raw((FARW, H), (0, SHORE + 4, FARW, 140), 41, 64)


@lru_cache(maxsize=1)
def _glare_raw():
    return NP.glint_raw((W, H), (SUN[0] - 40, SHORE + 2, SUN[0] + 40, 142), 37, 70, center=SUN[0], spread=30)


BOATS = [(40, 76, 2.0, 1, 12, 11, 2, 0.32), (250, 78, -1.4, -1, 9, 8, 6, 0.3), (420, 81, 2.6, 1, 16, 14, 4, 0.4)]


@lru_cache(maxsize=1)
def felucca_imgs():
    return [NP.felucca_refl(L, sh, sd, face=fc) for (x0, y, vx, fc, L, sh, sd, k) in BOATS]


# ============================================================ 近景零件
def draw_road(im):
    """岸上的泥土路（y 148–179）：压实的泥 + 低对比的斑驳 + 两道淡车辙 + 小石子；树荫下压暗一点（对比仍然低）。"""
    P.sand_ground(im, 0, PW - 1, WALK[0], H - 1, ROAD, ROAD_D, ROAD_L, 301, ruts=(160, 171), pebbles=110)
    a = np.array(im)
    nz = A._fbm(200 + 8, 24 + 8, 5, seed=307)[4:28, 4:204]
    for y in range(148, 172):
        for x in range(292, 492):
            u = abs(x - 392) / 100.0
            if nz[y - 148, x - 292] > 0.42 + 0.35 * u + 0.012 * (y - 148):
                a[y, x, :3] = (a[y, x, :3].astype(np.float32) * np.array((0.93, 0.93, 0.96))).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))


def draw_embankment(im):
    """矮石堤（y 144–147）：一层压顶石（上沿受光）+ 一层立面方石；上面一行墨线（和河面分开）。芦苇那一段是湿泥岸坡。"""
    for (x0, x1, sd) in ((0, REED[0] - 1, 311), (REED[1], PW - 1, 312)):
        NP.ashlar(im, (x0, EMB, x1, 147), sd, course=4, blen=(9, 18), joint_i=1, pits=0.01)
        d = ImageDraw.Draw(im)
        hl(d, x0, x1, EMB - 1, INK)
    d = ImageDraw.Draw(im)
    for x in range(REED[0], REED[1]):                              # 湿泥岸坡：上沿一线水边的亮、往下越来越干
        for y in range(EMB - 1, 148):
            r = y - (EMB - 1)
            c = MUD[0] if r == 0 else (MUD[1] if r < 3 else MUD[2])
            if r == 0 and hash01(313, x) < 0.5:
                c = (150, 170, 160)
            if r >= 2 and hash01(314, x, y) < 0.18:
                c = MUD[1]
            px(d, x, y, c)
    vl(d, REED[0] - 1, EMB - 1, 147, INK)
    vl(d, REED[1], EMB - 1, 147, INK)
    for bx in (150, 610):                                          # 石头拴船桩
        rect(d, bx - 2, EMB - 6, bx + 2, EMB - 1, LAD[4])
        vl(d, bx - 2, EMB - 6, EMB - 1, LAD[5])
        vl(d, bx + 2, EMB - 6, EMB - 1, LAD[2])
        hl(d, bx - 2, bx + 2, EMB - 6, LAD[6])
        hl(d, bx - 2, bx + 2, EMB - 7, INK)
        vl(d, bx - 3, EMB - 6, EMB - 1, INK)
        vl(d, bx + 3, EMB - 6, EMB - 1, INK)
    P.soft_shadow(im, 0, PW - 1, 148, depth=1, slant=0)


def draw_left(im):
    """x 0–100：两棵海枣树（树干从堤后面伸出来）+ 木架上的两只陶水罐。"""
    NP.behind(im, lambda lay: (P.palm_trunk(lay, 18, EMB - 1, 76, lean=3, seed=21),
                               P.palm_trunk(lay, 60, EMB - 1, 64, lean=-2, seed=22)))
    d = ImageDraw.Draw(im)
    P.zir_stand(d, 80, 147)
    P.soft_shadow(im, 80, 98, 148, depth=1, slant=2)


def draw_fisher(im):
    """渔夫的地方（x 100–156）：压顶石上的鱼篓、一圈缆绳、木桶；拴船桩在 draw_embankment。"""
    d = ImageDraw.Draw(im)
    for y in range(EMB - 8, EMB):                                  # 鱼篓（编织的，中间鼓）
        u = (y - (EMB - 8)) / 7.0
        half = int(round(4 + 1.5 * math.sin(math.pi * u)))
        for x in range(113 - half, 113 + half + 1):
            c = (196, 160, 104) if (x + y) % 2 else (164, 128, 80)
            if x == 113 + half:
                c = (128, 96, 60)
            px(d, x, y, c)
    hl(d, 110, 116, EMB - 9, (120, 90, 56))
    for k in range(3):                                             # 一圈缆绳
        hl(d, 122 + k, 131 - k, EMB - 1 - k, (206, 178, 126) if k % 2 else (170, 140, 96))
    rect(d, 137, EMB - 7, 143, EMB - 1, NP.WOOD)                   # 木桶
    vl(d, 137, EMB - 7, EMB - 1, NP.WOOD_HI)
    vl(d, 143, EMB - 7, EMB - 1, NP.WOOD_D)
    hl(d, 137, 143, EMB - 5, (90, 90, 96))
    hl(d, 137, 143, EMB - 2, (90, 90, 96))
    hl(d, 137, 143, EMB - 7, (150, 190, 200))
    for (x0, x1, y0) in ((109, 117, EMB - 9), (136, 144, EMB - 8)):
        hl(d, x0, x1, y0 - 1, INK)


def draw_nets(im):
    """晒网架（x 249–276）：两根短桩、一根横杆（y 141，比水花那一行低）、渔网搭在杆上垂到堤脚（菱形网眼透出后面的石头），
    杆上一串软木浮子；右边路沿上堆着一小堆网。"""
    d = ImageDraw.Draw(im)
    x0, x1 = NETS
    for x in (x0, x1):
        vl(d, x, 142, 147, NP.WOOD)
        vl(d, x + 1, 143, 147, NP.WOOD_D)
    hl(d, x0 - 2, x1 + 3, 142, NP.WOOD_HI)
    hl(d, x0 - 2, x1 + 3, 141, INK)
    for x in range(x0, x1 + 2):
        for y in range(143, 149):
            if (x + y) % 3 == 0 or (x - y) % 3 == 0:
                px(d, x, y, (214, 196, 160) if y < 145 else (190, 172, 138))
    for x in range(x0 + 1, x1 + 1, 4):
        px(d, x, 143, (220, 120, 60))
        px(d, x + 1, 143, (180, 96, 48))
    for y in range(147, 151):                                      # 地上一小堆网
        half = 6 - (150 - y)
        for x in range(282 - half, 282 + half + 1):
            if (x + y) % 2 == 0:
                px(d, x, y, (200, 182, 146))


def draw_tree(im):
    """大树（老无花果树）：粗树干（x 388–402，从堤后面长出来）+ 三根大枝 + 浓密的树冠（y 14–90，左上亮）；外沿墨线。"""
    def trunk(lay):
        d = ImageDraw.Draw(lay)
        for y in range(70, EMB):
            u = (EMB - y) / float(EMB - 70)
            cx = 395 + int(round(3 * math.sin(u * 2.4)))
            half = 7 - int(round(2 * u)) + (2 if y > EMB - 6 else 0)
            for x in range(cx - half, cx + half + 1):
                s = (x - (cx - half)) / max(1.0, 2.0 * half)
                c = TREE_BARK[3] if s < 0.2 else (TREE_BARK[2] if s < 0.5 else (TREE_BARK[1] if s < 0.85 else TREE_BARK[0]))
                if (y + x // 3) % 7 == 0 and 0.1 < s < 0.9:
                    c = TREE_BARK[0]                               # 树皮的纵裂
                px(d, x, y, c)
            px(d, cx - half - 1, y, INK)
            px(d, cx + half + 1, y, INK)
        for (xa, ya, xb, yb, wd) in ((394, 84, 336, 62, 4), (398, 80, 446, 60, 4), (395, 76, 404, 40, 3)):
            n_ = max(abs(xb - xa), abs(yb - ya))
            for k in range(n_ + 1):
                u = k / float(n_)
                x = int(round(xa + (xb - xa) * u))
                y = int(round(ya + (yb - ya) * u - 6 * math.sin(math.pi * u)))
                w_ = max(1, int(round(wd * (1 - 0.5 * u))))
                for q in range(-w_, w_ + 1):
                    px(d, x, y + q, TREE_BARK[2] if q < 0 else TREE_BARK[1])
                px(d, x, y - w_ - 1, INK)
                px(d, x, y + w_ + 1, INK)
        for (cx, cy, rx, ry, sd) in ((336, 50, 46, 24, 1), (398, 34, 44, 26, 2), (448, 54, 30, 20, 3), (372, 70, 30, 12, 4)):
            V._canopy(d, cx, cy, rx, ry, 330 + sd, pal=TREE_LEAF)
        lay2 = P.leafy(lay, (286, 6, 482, 96), TREE_LEAF, 337) if hasattr(P, 'leafy') else lay
        if lay2 is not None and lay2 is not lay:
            lay.paste(lay2)
        rimmed = P.outer_rim(lay)
        lay.paste(rimmed)
    NP.behind(im, trunk)
    d = ImageDraw.Draw(im)
    rect(d, 389, 112, 401, 119, (240, 236, 226))                   # 树干上的小招牌：白底、红字、一把剪刀
    hl(d, 389, 401, 112, (255, 252, 244))
    for x in range(391, 400, 2):
        px(d, x, 114, (186, 52, 48))
    px(d, 393, 117, (60, 60, 70))
    px(d, 397, 117, (60, 60, 70))
    px(d, 394, 116, (60, 60, 70))
    px(d, 396, 116, (60, 60, 70))
    px(d, 395, 115, (60, 60, 70))
    rect(d, 388, 111, 402, 120, None, outline=INK)


def draw_barber(im):
    """理发摊：镜架（两根木桩 + 横梁、圆镜挂正中）、左桩上挂磨刀皮带、搪瓷脸盆架 + 水壶、小木桌（梳子 / 剪刀 / 刷子 / 肥皂杯）。
    理发椅不在这里（pick 层），毛巾是 strip。"""
    d = ImageDraw.Draw(im)
    for x in POSTS:
        vl(d, x, 98, 147, NP.WOOD)
        vl(d, x + 1, 98, 147, NP.WOOD_D)
        vl(d, x - 1, 98, 147, INK)
        vl(d, x + 2, 98, 147, INK)
    hl(d, 314, 352, 98, NP.WOOD_HI)
    hl(d, 314, 352, 99, NP.WOOD_D)
    hl(d, 314, 352, 97, INK)
    hl(d, 314, 352, 100, INK)
    cx, cy, r = MIRROR
    vl(d, cx, 101, cy - r - 1, (60, 50, 44))                       # 挂绳
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            dd = math.hypot(x - cx, y - cy)
            if dd <= r - 1.4:
                u = (y - (cy - r)) / (2.0 * r)
                c = mix((206, 228, 236), (150, 184, 200), u)       # 镜面映着天
                if abs((x - cx) + (y - cy) + 2) <= 1 and dd < r - 2:
                    c = (250, 252, 252)                            # 一道斜的高光
                px(d, x, y, c)
            elif dd <= r + 0.2:
                px(d, x, y, NP.WOOD_HI if (x < cx and y < cy) else NP.WOOD_D)
            elif dd <= r + 1.2:
                px(d, x, y, INK)
    for y in range(104, 122):                                      # 左桩上挂的磨刀皮带
        px(d, 321, y, (132, 86, 50) if y % 4 else (104, 66, 40))
        px(d, 322, y, (104, 66, 40))
    px(d, 321, 103, (180, 180, 186))
    px(d, 322, 103, (120, 120, 128))
    # 脸盆架：铁三脚 + 搪瓷盆（白、蓝边）+ 地上的搪瓷水壶
    for (xa, xb) in ((355, 350), (355, 360), (355, 355)):
        for k in range(20):
            u = k / 19.0
            px(d, int(round(xa + (xb - xa) * u)), 128 + k, IRON_C[1])
    hl(d, 351, 359, 128, IRON_C[2])
    for y in range(122, 128):
        u = (y - 122) / 5.0
        half = int(round(7 - 2 * u * u))
        for x in range(355 - half, 355 + half + 1):
            px(d, x, y, (240, 242, 240) if x < 357 else (206, 210, 214))
    hl(d, 348, 362, 122, (60, 100, 170))
    hl(d, 350, 360, 123, (170, 200, 220))
    hl(d, 348, 362, 121, INK)
    rect(d, 364, 140, 368, 147, (232, 234, 232))                   # 水壶
    vl(d, 368, 140, 147, (196, 198, 202))
    px(d, 369, 141, (196, 198, 202))
    px(d, 370, 140, (196, 198, 202))
    hl(d, 364, 368, 139, (60, 100, 170))
    # 小木桌 + 东西
    rect(d, 372, 136, 386, 137, NP.WOOD_HI)
    hl(d, 372, 386, 138, NP.WOOD_D)
    for x in (373, 385):
        vl(d, x, 139, 147, NP.WOOD_D)
    hl(d, 372, 386, 135, INK)
    hl(d, 374, 378, 134, (40, 40, 44))                             # 梳子
    for x in range(374, 379):
        px(d, x, 133, (40, 40, 44) if x % 2 else (220, 210, 190))
    px(d, 380, 134, (170, 174, 182))                               # 剪刀
    px(d, 381, 133, (170, 174, 182))
    px(d, 382, 134, (170, 174, 182))
    rect(d, 383, 131, 384, 134, (236, 230, 214))                   # 刷子
    px(d, 383, 130, (240, 240, 240))
    px(d, 384, 130, (240, 240, 240))
    P.soft_shadow(im, 348, 388, 148, depth=1, slant=2)


def draw_tea(im):
    """小茶摊（x 444–520）：绿白条纹布篷（波浪边是 strip）+ 两根木杆、蓝底黄边的柜台（阿拉伯文）、铜茶炊、一盘红茶杯、薄荷、糖罐、长凳。"""
    P.awning(im, TEA[0], TEA[1], 94, 6, (46, 140, 96), (240, 236, 222), stripe=4, scallop=False, shadow=0)
    d = ImageDraw.Draw(im)
    for x in (TEA[0] + 2, TEA[1] - 2):
        vl(d, x, 100, 147, NP.WOOD)
        vl(d, x + 1, 100, 147, NP.WOOD_D)
        vl(d, x - 1, 100, 147, INK)
    rect(d, 450, 128, 498, 147, (52, 104, 168))                    # 柜台
    rect(d, 450, 126, 498, 127, NP.WOOD_HI)
    hl(d, 450, 498, 125, INK)
    rect(d, 451, 129, 497, 146, None, outline=(230, 190, 80))
    P.sign_ar(d, 455, 132, 493, 138, (52, 104, 168), (244, 240, 230), seed=11)
    for x in range(453, 497, 6):
        px(d, x, 142, (230, 190, 80))
        px(d, x + 1, 143, (230, 190, 80))
    vl(d, 449, 125, 147, INK)
    vl(d, 499, 125, 147, INK)
    B = P.BRASS                                                    # 铜茶炊：圆肚 + 圆顶 + 小烟囱 + 龙头
    for y in range(110, 126):
        half = 5 if y > 112 else 4
        for x in range(459 - half, 459 + half + 1):
            s = (x - (459 - half)) / (2.0 * half)
            c = B[3] if 0.15 < s < 0.35 else (B[2] if s < 0.6 else (B[1] if s < 0.85 else B[0]))
            px(d, x, y, c)
        px(d, 459 - half - 1, y, INK)
        px(d, 459 + half + 1, y, INK)
    hl(d, 456, 462, 109, B[2])
    hl(d, 456, 462, 108, INK)
    vl(d, 459, 103, 108, B[1])
    vl(d, 460, 103, 108, B[0])
    px(d, 465, 119, B[2])
    px(d, 466, 120, B[1])
    rect(d, 470, 124, 490, 125, (196, 198, 204))                   # 托盘 + 五只红茶玻璃杯
    for k, x in enumerate(range(471, 490, 4)):
        vl(d, x, 120, 123, (176, 60, 32))
        vl(d, x + 1, 120, 123, (214, 120, 70))
        px(d, x, 119, (240, 236, 226))
        px(d, x + 1, 119, (240, 236, 226))
    for (x, y) in ((493, 121), (494, 120), (495, 121), (492, 122), (494, 122), (496, 122)):
        px(d, x, y, (70, 150, 70))                                 # 薄荷
    vl(d, 494, 123, 125, (60, 110, 60))
    rect(d, 485, 116, 489, 123, (236, 236, 230))                   # 糖罐
    hl(d, 485, 489, 115, (60, 100, 170))
    rect(d, 506, 140, 520, 141, NP.WOOD_HI)                        # 长凳
    for x in (507, 519):
        vl(d, x, 142, 147, NP.WOOD_D)
    hl(d, 506, 520, 139, INK)
    P.soft_shadow(im, 448, 522, 148, depth=1, slant=2)


def draw_right(im):
    """x 594–640：堤后一棵海枣树 + 蓝色路牌（白字 LUXOR + 箭头）。"""
    NP.behind(im, lambda lay: P.palm_trunk(lay, 616, EMB - 1, 70, lean=-3, seed=23))
    d = ImageDraw.Draw(im)
    vl(d, 631, 116, 147, (150, 150, 156))
    vl(d, 632, 116, 147, (100, 100, 108))
    rect(d, 612, 110, 639, 119, (44, 92, 160), outline=(236, 236, 230))
    NP.tiny_text(d, 614, 112, 'LUXOR', (246, 246, 240))
    hl(d, 632, 636, 114, (246, 246, 240))
    px(d, 635, 113, (246, 246, 240))
    px(d, 635, 115, (246, 246, 240))
    hl(d, 612, 639, 109, INK)
    P.soft_shadow(im, 628, 636, 148, depth=1, slant=2)


@lru_cache(maxsize=1)
def near_img():
    im = A._new(PW, H)
    draw_road(im)
    draw_embankment(im)
    draw_tree(im)
    draw_left(im)
    draw_fisher(im)
    draw_nets(im)
    draw_barber(im)
    draw_tea(im)
    draw_right(im)
    return NP.opaque(im)


# ============================================================ 理发椅（pick）
def chair_img(cut=False):
    """理发椅（朝右，世界坐标画进 CHAIR_BOX 那么大的图）：铸铁圆底座 + 镀铬立柱、红皮座垫、往后微仰的红皮靠背 + 头枕、
    镀铬扶手、前面的脚踏板；外沿墨线。cut：从座垫中间（x 327）劈开，左半往左倒、右半往右倒（越往上倒得越多），
    切口露出白色填充物，地上几块木屑 / 皮屑。"""
    x0, y0, x1, y1 = CHAIR_BOX
    im = A._new(x1 - x0, y1 - y0)
    d = ImageDraw.Draw(im)

    def P_(x, y, c):
        px(d, x - x0, y - y0, c)
    for y in range(156, 159):                                      # 底座
        a_ = {156: (324, 336), 157: (322, 338), 158: (321, 339)}[y]
        for x in range(a_[0], a_[1] + 1):
            P_(x, y, IRON_C[2] if y == 156 else IRON_C[1] if x < 334 else IRON_C[0])
    for y in range(150, 156):                                      # 立柱
        for x, c in ((328, CHROME[3]), (329, CHROME[2]), (330, CHROME[1]), (331, CHROME[0])):
            P_(x, y, c)
    for k in range(4):                                             # 脚踏
        P_(334 + k, 150 + k, CHROME[1])
    for x in range(336, 346):
        P_(x, 153, CHROME[3] if x < 340 else CHROME[2])
        P_(x, 154, CHROME[0])
    for x in range(318, 338):                                      # 座垫
        P_(x, 146, LEATHER[2])
        for y in (147, 148, 149):
            P_(x, y, LEATHER[1] if x < 334 else LEATHER[0])
        P_(x, 150, LEATHER[0])
    for y in range(124, 147):                                      # 靠背（往后仰）
        sh = (146 - y) // 8
        xa = 315 - sh
        P_(xa, y, CHROME[2])
        for x in range(xa + 1, xa + 5):
            P_(x, y, LEATHER[1] if (x - xa) != 2 or y % 5 else LEATHER[0])
        P_(xa + 5, y, LEATHER[0])
        if y < 128:
            P_(xa + 1, y, LEATHER[2])
    for y in range(119, 124):                                      # 头枕 + 镀铬杆
        for x in range(311, 318):
            P_(x, y, LEATHER[2] if y == 119 else (LEATHER[1] if x < 316 else LEATHER[0]))
    P_(313, 123, CHROME[2])
    for x in range(318, 335):                                      # 扶手
        P_(x, 139, CHROME[3])
        P_(x, 140, CHROME[2])
        P_(x, 141, CHROME[0])
    for y in range(141, 147):
        P_(334, y, CHROME[2])
        P_(335, y, CHROME[0])
    a = np.array(im)
    if cut:
        out = np.zeros_like(a)
        cx = 327 - x0
        for yy in range(a.shape[0]):
            y = yy + y0
            lean = max(0, 156 - y)
            dl = -(lean // 4) - 1                                  # 左半（靠背）往左倒得多
            dr = (lean // 3) + 2                                   # 右半（座垫前半 + 扶手 + 脚踏）往右歪
            dy = 1 if y < 150 else 0
            for xx in range(a.shape[1]):
                if a[yy, xx, 3] == 0:
                    continue
                if y >= 155:                                       # 底座留在原地
                    out[yy, xx] = a[yy, xx]
                    continue
                if xx < cx:
                    nx_, ny_ = xx + dl, yy + dy
                else:
                    nx_, ny_ = xx + dr, yy + dy + (1 if y < 142 else 0)
                if 0 <= nx_ < a.shape[1] and 0 <= ny_ < a.shape[0]:
                    out[ny_, nx_] = a[yy, xx]
        a = out
        im2 = Image.fromarray(a, 'RGBA')
        d2 = ImageDraw.Draw(im2)
        for y in range(122, 152):                                  # 切口：白色填充物（只在皮面上）
            yy = y - y0
            lean = max(0, 156 - y)
            for (xx, s) in ((cx - 2 - lean // 4, -1), (cx + 2 + lean // 3, 1)):
                if 0 <= xx < a.shape[1] and 0 <= yy + 1 < a.shape[0] and a[min(a.shape[0] - 1, yy + 1), xx, 3]:
                    if hash01(341, y, s) < 0.7:
                        px(d2, xx, yy + 1, (244, 238, 222) if hash01(342, y, s) < 0.6 else (210, 200, 180))
        for k in range(9):                                         # 地上的木屑 / 皮屑
            xx = int(hrange(306, 352, 343, k)) - x0
            yy = int(hrange(155, 159, 344, k)) - y0
            px(d2, xx, yy, (176, 132, 84) if k % 3 else LEATHER[1])
        a = np.array(im2)
    op = a[..., 3] > 0                                             # 外沿墨线（不描贴地的下沿）
    nb = np.zeros_like(op)
    nb[:-1] |= op[1:]
    nb[1:] |= op[:-1]
    nb[:, 1:] |= op[:, :-1]
    nb[:, :-1] |= op[:, 1:]
    rim = nb & ~op
    rim[159 - y0:, :] = False
    a[rim, :3] = INK
    a[rim, 3] = 255
    return Image.fromarray(a, 'RGBA')


# ============================================================ 会动的
PALMS = [(21, 67, 12, 21), (58, 79, 11, 22), (613, 73, 12, 23)]    # (树冠中心 x, y, 半径, 种子)


def _palm_raw(i):
    cx, cy, R, sd = PALMS[i]

    def raw(f):
        im = A._new(PW, H)
        P.palm_crown(im, cx, cy, R, seed=sd, f=f)
        return P.outer_rim(im)
    return raw


def _boat_raw(f):
    """拴着的小木船（x 154–208，吃水线 y 142）：尼罗河上渔船常见的刷漆——绿船身、一道白条、黄色船舷，两头往上翘（船头高）；
    船里搭着一支桨、一堆网；上下起伏 0 / 1 px；船头船尾的小水纹每帧往外走 1 px；缆绳拴在石桩上。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    dy = 1 if math.sin(math.tau * f / N + 0.4) > 0.25 else 0
    x0, x1 = 154, 208
    for x in range(x0, x1 + 1):
        u = (x - x0) / float(x1 - x0)
        sheer = int(round(5 * max(0.0, u - 0.78) / 0.22 * max(0.0, u - 0.78) / 0.22))     # 船头翘
        sheer += int(round(3 * (max(0.0, 0.16 - u) / 0.16) ** 2))                        # 船尾翘
        top = 135 - sheer
        for y in range(top + dy, 143):
            r = y - (top + dy)
            if r == 0:
                c = (232, 190, 80)                                 # 船舷（黄）
            elif r == 1:
                c = (236, 232, 218)                                # 白条
            elif y >= 141:
                c = (44, 86, 66)                                   # 吃水线附近（湿、暗）
            else:
                c = (70, 128, 96) if u < 0.7 else (60, 112, 86)
                if (x - x0) % 11 == 0:
                    c = (52, 96, 72)                               # 船板缝
            px(d, x, y, c)
        px(d, x, top + dy - 1, INK)
    for y in range(129 + dy, 143):
        px(d, x1 + 1, y, INK)
    px(d, x1, 128 + dy, (232, 190, 80))                            # 船头柱顶
    px(d, x0 - 1, 132 + dy, INK)
    for k in range(38):                                            # 一支桨斜搭在船上（桨叶在船尾外）
        x = 162 + k
        y = 128 + dy + k // 9
        px(d, x, y, (190, 152, 104))
        if k < 2:
            px(d, x, y + 1, (190, 152, 104))
    for x in range(172, 186):                                      # 船里一堆网
        px(d, x, 133 + dy - (1 if 175 < x < 183 else 0), (214, 196, 160))
    px(d, 178, 131 + dy, (220, 120, 60))
    for k in range(8):                                             # 缆绳：船尾 → 石桩
        px(d, 153 - k // 2, 134 + dy + (k * (EMB - 6 - 134 - dy)) // 8, (190, 160, 110))
    for (cx, s_) in ((x0 - 2, -1), (x1 + 2, 1)):                   # 小水纹：每帧往外走 1 px，两道错开半圈
        for q in range(2):
            xx = cx + s_ * (1 + (f + q * 4) % N)
            hl(d, min(xx, xx + s_ * 2), max(xx, xx + s_ * 2), 142, NP.NILE_HI)
    return im


FEL_X, FEL_DECK = 520, 124


@lru_cache(maxsize=1)
def _felucca_base():
    return P.felucca_img(26, 24, 5, face=-1, band=(200, 70, 60))


def _felucca_raw(f):
    """停在河上的三角帆船（anchors.felucca [520,120]）：船身中心 x 520、甲板 y 124；上下起伏 0 / 1 px，倒影每行左右晃。"""
    g = _felucca_base()
    im = A._new(PW, H)
    dy = 1 if math.sin(math.tau * f / N) > 0.3 else 0
    gx, gy = FEL_X - g.width // 2, FEL_DECK - (g.height - 3) + dy
    im.alpha_composite(g, (gx, gy))
    src = np.array(g.transpose(Image.FLIP_TOP_BOTTOM)).astype(np.float32)
    a = np.array(im).astype(np.float32)
    wat = np.array(NP.NILE_MID, np.float32)
    for j in range(1, 17):
        ty = gy + g.height - 2 + j
        if ty >= EMB - 1:
            break
        row = src[j]
        sh = int(round(1.2 * math.sin(math.tau * f / N + j * 0.9)))
        row = np.roll(row, sh, axis=0)
        bay = A._bayer(PW, H)[ty, gx:gx + g.width]
        m = (row[:, 3] > 0) & (bay < 0.9 - j * 0.045) & (a[ty, gx:gx + g.width, 3] == 0)
        c = wat * 0.55 + row[:, :3] * 0.45
        seg = a[ty, gx:gx + g.width]
        seg[m, :3] = c[m]
        seg[m, 3] = 255
        a[ty, gx:gx + g.width] = seg
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


@lru_cache(maxsize=1)
def _reeds_raw():
    return NP.reeds_raw((PW, H), REED[0] + 1, REED[1] - 2, EMB + 1, 104, 61, n=70, amp=1.6)


EGRET_POSE = [(0, 0, 0), (0, -1, 0), (1, 0, 0), (2, 3, 1), (2, 4, 1), (1, 1, 0), (0, -1, 0), (0, 0, 1)]   # (脖子前伸, 头低, 特征)


def _egret_raw(f):
    """芦苇边泥里的一只白鹭（脚 y 146）：每帧一个姿势——站、抬头、伸脖子、低头啄（两帧）、收回、再抬头、甩一下尾巴，8 帧闭合。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y = 597, 146
    fw, low, ex_ = EGRET_POSE[f % N]
    for k in range(5):
        px(d, x + 1, y - k, (60, 56, 50))                          # 腿
        px(d, x + 3, y - k, (60, 56, 50))
    rect(d, x, y - 9, x + 5, y - 5, (246, 246, 242))               # 身子
    hl(d, x + 1, x + 5, y - 5, (210, 214, 216))
    px(d, x + 6, y - 6 - (1 if (ex_ and f == 7) else 0), (210, 214, 216))      # 尾（第 7 帧甩一下）
    hx, hy = x - 1 - fw, y - 14 + low                              # 头的位置
    for k in range(6):                                             # S 形的脖子：从肩（x, y−9）到头
        u = k / 5.0
        nx_ = int(round(x + (hx - x) * u + (1 if 0.3 < u < 0.7 else 0)))
        ny_ = int(round((y - 9) + (hy - (y - 9)) * u))
        px(d, nx_, ny_, (246, 246, 242))
    px(d, hx, hy, (246, 246, 242))
    px(d, hx - 1, hy + (1 if low > 2 else 0), (240, 190, 60))      # 嘴（黄）
    px(d, hx - 2, hy + (2 if low > 2 else 0), (240, 190, 60))
    px(d, hx + 1, hy - 1, (40, 40, 40)) if low < 3 else None
    return P.outer_rim(im)


def _steam_raw(f):
    """茶炊烟囱顶上的热气：几团往上飘、往右散、越高越稀（硬边抖开），8 帧闭合。"""
    im = A._new(PW, H)
    a = np.zeros((H, PW, 4), np.uint8)
    for k in range(3):
        u = ((f + k * N / 3.0) % N) / N
        cy = 102 - u * 10
        cx = 459.5 + u * 5 + math.sin(u * 6 + k) * 1.2
        r = 1.2 + u * 2.0
        al = 0.85 * (1 - u)
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and 0 <= y < H:
                    a[y, x, :3] = (246, 244, 238)
                    a[y, x, 3] = max(a[y, x, 3], int(255 * al))
    return P.hard_alpha(Image.fromarray(a, 'RGBA'))


def _towels_raw(f):
    """镜架横梁右头搭着的两条毛巾（白底蓝条）：下摆被河风吹得一摆一摆，8 帧闭合。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for k, (x0, L) in enumerate(((345, 13), (350, 11))):
        for r in range(L):
            u = r / float(L - 1)
            sw = int(round(1.6 * u * math.sin(math.tau * f / N + k * 1.7 + u * 1.5)))
            for c_ in range(4):
                col = (244, 244, 240) if c_ < 3 else (206, 210, 214)
                if r in (L - 3, L - 2):
                    col = (70, 110, 176) if c_ < 3 else (52, 86, 140)
                px(d, x0 + c_ + sw, 101 + r, col)
    return P.outer_rim(im)


def _valance_raw(f):
    im = A._new(PW, H)
    P.valance(ImageDraw.Draw(im), TEA[0], TEA[1], 100, (46, 140, 96), (240, 236, 222), f, stripe=4)
    return im


@lru_cache(maxsize=1)
def strips():
    """近景 strip：[(名字, 框, 帧函数)]，框按画出来的东西算（auto_box）。"""
    out = []
    for i in range(len(PALMS)):
        fn = NP.cached_frames(_palm_raw(i))
        out.append(('palm_%d' % i, P.auto_box(fn, N, FPS), fn))
    for name, raw in (('boat', _boat_raw), ('felucca_near', _felucca_raw), ('reeds', _reeds_raw()),
                      ('egret', _egret_raw), ('steam', _steam_raw), ('towels', _towels_raw), ('valance', _valance_raw)):
        fn = NP.cached_frames(raw)
        out.append((name, P.auto_box(fn, N, FPS), fn))
    return out


# ============================================================ 图层表 / 导出
@lru_cache(maxsize=1)
def table():
    tb = [('static', 'sky', sky_img(), 0, 0),
          ('wrap', 'clouds', clouds_img(), CLOUD_P, CLOUD_K, 4, CLOUD_VX)]
    fim, fy = P.crop_pano(far_img())
    tb.append(('pano', 'far', fim, FAR_K, 0, fy))
    gf = NP.cached_frames(_glint_raw())
    tb.append(('strip', 'glint', P.auto_box(gf, N, FPS), N, FPS, gf, FAR_K))
    sf = NP.cached_frames(_glare_raw())
    tb.append(('strip', 'sunglare', P.auto_box(sf, N, FPS), N, FPS, sf, 0.0))
    tb.append(('wrap', 'ripples', ripples_img(), RIP_P, RIP_K, RIP_Y, RIP_VX))
    boats = felucca_imgs()
    tb.append(('clouds', 'felucca', BOAT_SPAN,
               [('felucca%d' % i, boats[i], b[0], b[1], b[2], b[7]) for i, b in enumerate(BOATS)]))
    kimg, kl = NP.kites()
    tb.append(('clouds', 'kites', 460, [('kite%d' % i, kimg, x0, y, vx, k) for i, (y, vx, k, x0) in enumerate(kl)]))
    nim, ny = P.crop_pano(near_img())
    tb.append(('pano', 'near', nim, 1.0, 0, ny))
    for (name, box, fn) in strips():
        tb.append(('strip', name, box, N, FPS, fn, 1.0))
    tb.append(('pick', 'chair_cut', [chair_img(False), chair_img(True)], [0, 1], CHAIR_BOX[0], CHAIR_BOX[1], 1.0))
    return tuple(tb)


def compose(camX, t=0.5, state=None):
    return P.compose(table(), camX, t, state)


def anchors():
    anc = {k: list(v) for k, v in ANCHORS.items()}
    anc.update(
        skip_line=[list(p) for p in SKIP],
        chair_box=list(CHAIR_BOX),
        mirror_box=[MIRROR[0] - MIRROR[2] - 1, MIRROR[1] - MIRROR[2] - 1, MIRROR[0] + MIRROR[2] + 2, MIRROR[1] + MIRROR[2] + 2],
        tea_box=[TEA[0], 94, TEA[1] + 17, 148],
        reeds_box=[REED[0], 104, REED[1], 148],
        boat_box=[152, 126, 212, 144],
        nets_box=[NETS[0] - 2, 140, 289, 151],
        tree=[TRUNK[0], 70, TRUNK[1] + 1, EMB],
        embankment=EMB, water_y=SHORE)
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
    cfg = dict(title='尼罗河岸', PW=PW, walk=WALK, near=near_img(), opaque_rows=(EMB - 1, H), sky=sky_img(),
               states=[{}, {'chair_cut': 1}], stand=STAND, required=REQUIRED, size_limit=250 * 1024, cams_step=40,
               flat=(0, PW, WALK[0], WALK[1] + 1, 22, 0.012), flat_skip=[tuple(anc['nets_box'])])
    P.common_checks(ex, BJ, st, tb, cfg)
    NP.anchor_values(ex, anc, ANCHORS)
    NP.state_checks(ex, BJ, st, ['chair_cut'], [0, 160, 320], '尼罗河岸')
    # 打水漂那一段河面要干净：近景 + 每个近景 strip 的每一帧，在 SKIP_CLEAN 里一个像素都不画（镜架两根桩除外）
    a = np.array(near_img())
    x0, y0, x1, y1 = SKIP_CLEAN
    keep = np.ones((y1 - y0 + 1, x1 - x0 + 1), bool)
    for p_ in POSTS:
        keep[:, p_ - 1 - x0:p_ + 3 - x0] = False
    m = (a[y0:y1 + 1, x0:x1 + 1, 3] > 0) & keep
    ex.checked('打水漂那一段（x %d–%d、y %d–%d）近景透明（只看得见水；镜架的桩除外）' % (x0, x1, y0, y1), int(m.sum()))
    hit = 0
    for (name, box, fn) in strips():
        for i in range(N):
            fa = np.array(fn(i / FPS))[y0:y1 + 1, x0:x1 + 1, 3] > 0
            hit += int((fa & keep).sum())
    ex.checked('近景 strip 每一帧都不画进打水漂那段水面（像素）', hit)
    bad = 0
    for camX in (60, 120, 160):
        im = np.array(compose(camX, 0.0).convert('RGB')).astype(int)
        for (sx, sy) in SKIP:
            if 0 <= sx - camX < W:
                r, g, b = im[sy, sx - camX]
                water = (b >= r - 8 and g >= r - 8) or min(r, g, b) >= 225      # 水色，或者波光的亮点
                bad += 0 if water else 1
    ex.checked('七个水花点拼出来都是水（水色或波光，镜头 60 / 120 / 160）', bad)
    # 理发椅：坐点 x 330 在椅座上（座垫 y 146–150 在坐姿的屁股高度：脚点 158 往上 8–12）、劈开前后两张图不一样
    ci0 = np.array(chair_img(False))
    ok = ci0[146 - CHAIR_BOX[1], 330 - CHAIR_BOX[0], 3] > 0
    ex.checked('理发椅座垫在 anchors.barber_chair 正上方（x 330、y 146）', 0 if ok else 1)
    ex.checked('chair_cut 两张图不一样（差的像素）', 0 if BJ.ndiff_rgba(chair_img(False), chair_img(True)) > 50 else 1)
    # 镜子：mirror 锚点就在镜面上
    mx, my = ANCHORS['mirror']
    ex.checked('anchors.mirror 落在圆镜镜面上', 0 if a[my, mx, 3] > 0 and a[my, mx, 2] > 140 else 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch9', 'after')
    os.makedirs(od, exist_ok=True)
    full = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    for cx in (0, 320):
        full.paste(compose(cx, 0.5), (cx, 0))
    full.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'nile_bank_solo.png'))
    print('ok')
