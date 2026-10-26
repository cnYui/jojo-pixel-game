# -*- coding: utf-8 -*-
r"""egypt_temple —— 第9章「科翁坡神殿」：尼罗河边的砂岩神殿遗迹，上午（地图 temple_ch9；第 18 战段 1 恰卡的场地）。
2026-10-19 nile 组按体验版精度新画（改前是 later_stages 的平涂占位）。共用零件在 nile_parts.py。

地图 640 宽、ground 160、可走带 y 148–176（磨旧的砂岩铺地 + 吹进来的沙，对比压得很低）；侧视平视，太阳在左上
（立面左沿亮、右沿暗，柱子的影子往右落在后墙上 → 柱间一道道斜进来的光）。墙脚 = 地面后沿 y 146，所有东西画在 y ≤ 145。
从左到右（世界坐标）：
  x 0–56      塔门残段（往右收分的大斜墙、顶上的凹弧檐口塌了一半、三行阴刻字 + 王名圈），门前一根旗杆（埃及国旗 strip）
              （anchors.arrive 在它前面）
  x 54–108    矮墙 + 景点牌（蓝底白字 KOM OMBO + 阿拉伯文，两根木桩）；导游站 anchors.guide；墙后一棵海枣树（树冠 strip）
  x 108–238   柱廊（anchors.colonnade）：四根开放纸莎草柱头的砂岩圆柱（柱身浮雕带、柱头残留的绿 / 蓝彩），顶上一段额枋
              + 凹弧檐口（右边那段塌了，第四根柱子只剩顶板）；柱子后面是一道矮一点的后墙（阴刻字、在柱影里），
              柱间斜进来的光柱里飘着灰尘（strip），额枋下面几只小燕子绕圈飞（strip）
  x 236–304   象形文字墙（anchors.hieroglyph，调查点 / 问答小游戏）：上沿坍塌、一道 kheker 饰带、一栏竖排的象形文字，
              下面三个神的阴刻立像——左：豺狼头的阿努比斯（黑）、中：鹰头的荷鲁斯（戴双冠）、右：鳄鱼头的索贝克（绿，
              羽冠 + 日盘）——都握着权杖、提着生命符，颜料掉了一部分；再下面一栏纸莎草纹饰带 + 墙基
              （神像在 y 75–115：站在可走带后沿的人头顶在 y ≥ 115，挡不住）
  x 304–372   游客站的空地（anchors.tourists）：后面一道坍得很矮的墙（中间最低，墙头上看得见远处的尼罗河和对岸的绿带）、
              两截断柱、一小堆散落的方石、游客路线的绳栏（铁桩 + 麻绳）；墙后一棵海枣树（strip）
  x 372–456   刀匠旧作坊的遗迹：靠神殿搭的土坯墙（抹灰剥落、灶口上方一片烟熏黑）、一张石台（两块石墩 + 石板），
              台上一个木头刀架挂着三把生锈的弯刀，第三个钉子空着（“刀架上少了一把”；恰卡站 anchors.sword_rack，
              剧情摆的弯刀 prop.anubis_sword 拿在他手里，背景不画）；石砧、土灶、靠着的火钳、破陶罐
  x 456–532   残缺的雕像（anchors.statue）：黑花岗岩的坐像，脖子以上断掉了（断口是粗糙的亮面），双手放在膝上；
              高石座上一道横排的字，右下角一道裂缝（anchors.statue_base：“底座的缝里卡着一个小东西”，东西是剧情给的，不画）；
              后面一道坍矮的墙、一棵海枣树（strip）
  x 532–594   内殿的门（anchors.sanctum）：整面墙 + 凹弧檐口，门楣上一个带翅膀的日盘（红日 + 蓝绿的翅膀），两边门框刻字，
              门洞里黑洞洞的
  x 594–640   最右两根柱子（cx 600、637）+ 额枋；两柱之间 x 608–629 只有一道矮的护墙（y 132 以下），上面露出一段尼罗河：
              水面、对岸的绿带和台地沙山（anchors.nile_view [612,128] 正好在水面上——扔刀的方向）；anchors.exit 在它前面
远景：对岸（西岸）的台地沙山（平顶 + 台阶 + 冲沟，不画尖顶）、贴水的一条海枣林 / 甘蔗田、几栋土坯房和一座宣礼塔、
尼罗河（对岸倒影、亮水纹、波光 strip、两条三角帆船漂过）。

图层（从后往前）：
  sky       static           320×180 上午的天 + 左上的太阳
  clouds    wrap   k 0.08 vx 1.0   小积云 + 云丝（640 循环）
  far       pano   k 0.25          远景 400 宽：台地沙山、绿带、房子、宣礼塔、尼罗河（水面 y 108 起）
  glint     strip  k 0.25          河面的波光（8 帧 @4 fps）
  felucca   clouds k 0.25          两条三角帆船（带倒影）在河上慢慢漂（span 520）
  kites     clouds                 两只高处盘旋的黑鸢
  near      pano   k 1             整座神殿（640 宽）
  palm_0…2  strip  k 1             三棵海枣树的树冠（8 帧 @4 fps）
  flag      strip  k 1             门前旗杆上的埃及国旗
  swallows  strip  k 1             额枋下绕圈飞的小燕子
  motes     strip  k 1             柱间光柱里飘的灰尘
锚点（素材总表 §一，第9章，定稿值一个不改）：arrive [40,164]、guide [96,160]、colonnade [180,120]、hieroglyph [250,150]、
      tourists [320,162]、sword_rack [410,152]、statue [500,140]、statue_base [506,162]、sanctum [585,156]、
      nile_view [612,128]、exit [626,162]。
另导出：gods（三个神的头的位置 {anubis, horus, sobek}，问答小游戏要指的话用）、hieroglyph_box（字墙）、rack_box（刀架）、
      rack_empty（空着的那个钉子）、door_box（内殿门洞）、nile_gap（最右两柱之间露河的那一块）、back 146（墙脚）。
key：无（素材总表 §一 这一行没有 key；规格里的 dusk 脚本没用到，不做）。
单独运行：python -B tools/bg_new/egypt_temple.py → tools/bg_new/_preview/ch9/after/egypt_temple_solo.png
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
LAD, SHADE = NP.SST_LADDER, NP.SST_SHADE

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (148, 176)
BACK = 146                      # 墙脚 = 地面后沿（墙、柱子画到 y 145）
N, FPS = NP.N, NP.FPS
CLOUD_P, CLOUD_K, CLOUD_VX = 640, 0.08, 1.0
FAR_K = 0.25
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 400
WATER_Y = 108                   # 远景层里河面的上沿（对岸的水线）
BOAT_SPAN = 520

COLS = (122, 156, 190, 224)     # 柱廊四根柱子的中线
COL_W = 20
COL_TOP = 34                    # 顶板上沿
ARCH = (108, 202, 24, 33)       # 额枋 x0, x1, y0, y1（右边那段塌了：第四根柱子上面没有）
GODS_X = (242, 262, 282)        # 三个神的左沿（各 18 宽）
GOD_Y = 75                      # 神像顶（脚在 y 115）
WALL_G = (238, 302)             # 象形文字墙
RACK = (395, 431)               # 刀架两根立柱的外沿
RACK_PEGS = (402, 409, 416, 423)
RACK_EMPTY = 416                # 空着的钉子（少了一把）
PLINTH = (482, 520, 120)        # 雕像石座 x0, x1, 顶
DOOR = (560, 588, 92)           # 内殿门洞 x0, x1, 顶（到墙脚）
COL_R = (600, 637)              # 最右两根柱子的中线
COL_RW = 14
GAP = (608, 629)                # 两柱之间露河的那一块
PARAPET = 135                   # 护墙顶（nile_view y 128 下面留 6 行水面）

ANCHORS = dict(arrive=[40, 164], guide=[96, 160], colonnade=[180, 120], hieroglyph=[250, 150], tourists=[320, 162],
               sword_rack=[410, 152], statue=[500, 140], statue_base=[506, 162], sanctum=[585, 156],
               nile_view=[612, 128], exit=[626, 162])
STAND = ('arrive', 'guide', 'hieroglyph', 'tourists', 'sword_rack', 'statue_base', 'sanctum', 'exit')
REQUIRED = tuple(ANCHORS)

# 铺地（比墙淡、对比低：人站上去看得清）
G_LAD = [(204, 176, 136), (207, 180, 140), (210, 184, 144), (215, 189, 149), (222, 197, 157), (229, 206, 167),
         (236, 216, 180)]                                          # 低端几档挨得很近：坑 / 缝叠在一起也不会扎眼
SAND_T = ((228, 204, 162), (236, 214, 176))
RUST = ((92, 54, 40), (138, 82, 52), (176, 112, 70), (204, 150, 104))
DOOR_DARK = (22, 18, 22)


# ============================================================ 天 / 远景
@lru_cache(maxsize=1)
def sky_img():
    return NP.sky_img(NP.SKY_MORNING, (46, 22))


@lru_cache(maxsize=1)
def clouds_img():
    return NP.clouds_img(23)


@lru_cache(maxsize=1)
def far_img():
    """远景 400 宽：对岸台地（y 76–101）→ 绿带 + 房子 + 宣礼塔（到 y 107）→ 尼罗河（y 108–150）。整体罩雾，越远越淡。"""
    im = A._new(FARW, H)
    NP.ridge(im, 0, FARW, 74, 101, 7)
    NP.greenbelt(im, 0, FARW, 92, WATER_Y, 5, houses=[(118, 9, 6), (129, 7, 5), (262, 11, 6), (275, 6, 4)],
                 minaret=(140, 17))
    NP.water_body(im, 0, FARW, WATER_Y, 150, 9)
    amt = np.zeros((H, 1), np.float32)
    amt[:WATER_Y - 14] = 0.34
    amt[WATER_Y - 14:WATER_Y] = 0.2
    amt[WATER_Y:] = 0.08
    return NP.haze(im, amt)


GLINT_BOX = (0, WATER_Y + 2, FARW, 142)


@lru_cache(maxsize=1)
def _glint_raw():
    return NP.glint_raw((FARW, H), GLINT_BOX, 31, 70)


def glint_fn():
    return NP.cached_frames(_glint_raw())


BOATS = [(40, 102, 2.2, 1, 14, 12, 3), (300, 106, -1.6, -1, 10, 9, 8)]     # (x0, y, vx, 朝向, 船长, 帆高, 种子)


@lru_cache(maxsize=1)
def felucca_imgs():
    return [NP.felucca_refl(L, sh, sd, face=fc) for (x0, y, vx, fc, L, sh, sd) in BOATS]


# ============================================================ 近景零件
def draw_ground(im):
    """铺地：三排越往前越宽的砂岩石板（缝只比板暗一档）+ 吹进来的沙（fbm 一片片、边缘抖开，墙脚积得多）+ 几道细裂缝。"""
    for (y0, y1, crs, bl, sd) in ((BACK, 155, 10, (26, 44), 41), (156, 165, 10, (30, 52), 42), (166, H - 1, 14, (34, 60), 43)):
        NP.ashlar(im, (0, y0, PW - 1, y1), sd, lad=G_LAD, base_i=4, course=crs, blen=bl, var=1, pits=0.006, chips=0.0,
                  joint_i=3, top_hi=False)
    a = np.array(im)
    hh = H - BACK
    nz = A._fbm(PW + 8, hh + 8, 14, seed=61)[4:4 + hh, 4:4 + PW]
    bay = A._bayer(PW, H)[BACK:H, :PW]
    yy = np.arange(hh)[:, None]
    thr = 0.62 - 0.16 * np.clip(1.0 - yy / 10.0, 0, 1)            # 墙脚那几行沙积得多
    m1 = nz > thr
    m2 = (nz > thr - 0.05) & (bay < 0.5)
    sub = a[BACK:H, :PW]
    sub[m2, :3] = SAND_T[0]
    sub[m1, :3] = SAND_T[0]
    sub[m1 & (nz > thr + 0.08) & (bay < 0.5), :3] = SAND_T[1]
    a[BACK:H, :PW] = sub
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for i in range(7):                                             # 细裂缝（低对比）
        x = int(hrange(10, PW - 10, 71, i))
        y = int(hrange(150, 176, 72, i))
        for k in range(int(hrange(5, 12, 73, i))):
            px(d, x, y, G_LAD[3])
            x += 1
            if hash01(74, i, k) < 0.4:
                y += 1 if hash01(75, i, k) < 0.5 else -1


def contact_shadow(im):
    """墙脚接地的一行影：墙 / 柱子 / 石台站着的地方（y 145 不透明）下面 y 146 暗一档、y 147 抖开一半。"""
    a = np.array(im)
    stand = a[BACK - 1, :, 3] > 0
    bay = A._bayer(PW, H)
    for x in np.nonzero(stand)[0]:
        a[BACK, x, :3] = G_LAD[2]
        if bay[BACK + 1, x] < 0.5:
            a[BACK + 1, x, :3] = G_LAD[3]
    im.paste(Image.fromarray(a, 'RGBA'))


def cavetto(im, x0, x1, y0, y1, seed, paint=True):
    """凹弧檐口（埃及神庙墙顶那一圈往外翻的弧）：上面几行往外伸、下面收回到墙面；竖着一道道凹槽（蓝 / 绿的残色），
    下沿一根圆线脚（torus：一行亮一行暗）；底下 2 行落影。"""
    d = ImageDraw.Draw(im)
    hh = y1 - y0
    for r in range(hh):
        u = r / max(1.0, hh - 1.0)                                  # 0 = 顶（伸得最远）
        ext = int(round(3 * (1 - u) ** 2))
        for x in range(x0 - ext, x1 + ext + 1):
            t = 5 if u < 0.3 else (4 if u < 0.7 else 3)
            c = LAD[t]
            if (x - x0) % 4 == 0:
                c = LAD[t - 1]
                if paint and hash01(seed, x, 1) < 0.55:
                    c = NP.PAINT['B'] if (x // 4) % 2 else NP.PAINT['G']
            px(d, x, y0 + r, c)
    hl(d, x0 - 3, x1 + 3, y0, LAD[6])
    hl(d, x0 - 3, x1 + 3, y0 - 1, INK)
    hl(d, x0, x1, y1, LAD[6])
    hl(d, x0, x1, y1 + 1, LAD[2])
    vl(d, x0 - 4, y0, y0 + 2, INK)
    vl(d, x1 + 4, y0, y0 + 2, INK)


def draw_pylon(im):
    """塔门残段（x 0–56）：往右收分的大斜墙（底宽到 56、顶收到 46）、左半截还留着凹弧檐口、右半截塌了；
    墙面大块方石 + 三竖行阴刻字 + 一个王名圈；斜边一道圆线脚（背光暗）+ 墨线。"""
    top = 30
    NP.ashlar(im, (0, top, 56, BACK - 1), 101, course=9, blen=(16, 30), joint_i=2, pits=0.012)
    a = np.array(im)
    for y in range(top, BACK):
        xr = int(round(56 - (BACK - 1 - y) * 10.0 / (BACK - 1 - top)))
        a[y, xr + 1:57, 3] = 0
        a[y, xr, :3] = LAD[1]
        a[y, xr - 1, :3] = LAD[3]
        a[y, xr + 1, :3] = INK
        a[y, xr + 1, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    NP.broken_top(im, 22, 48, 40, 58, 111)
    cavetto(im, 0, 20, 22, 30, 3)
    for k, x in enumerate((8, 15, 22)):
        NP.glyph_column(im, x, 66, 124, 120 + k)
    d = ImageDraw.Draw(im)
    rect(d, 30, 72, 37, 96, None, outline=LAD[1])                 # 王名圈
    for q in range(76, 94, 4):
        hl(d, 32, 35, q, LAD[2])
    hl(d, 30, 37, 97, LAD[6])
    hl(d, 29, 38, 99, LAD[1])


def draw_flag_pole(im):
    """门前的旗杆（x 60，顶 y 70）：细铁杆、顶上一个小球、底下一个水泥墩。旗子是 strip。"""
    d = ImageDraw.Draw(im)
    vl(d, 60, 70, BACK - 4, (188, 188, 192))
    vl(d, 61, 70, BACK - 4, (120, 120, 128))
    px(d, 60, 69, (226, 196, 96))
    px(d, 61, 69, (176, 140, 60))
    rect(d, 57, BACK - 4, 64, BACK - 1, (190, 186, 178))
    hl(d, 57, 64, BACK - 4, (222, 218, 208))
    vl(d, 64, BACK - 4, BACK - 1, (150, 146, 140))


def draw_entrance(im):
    """入口（x 54–108）：一道坍矮的方石墙 + 墙后一棵海枣树（树干画进底图、树冠 strip）+ 景点牌。"""
    NP.ashlar(im, (52, 112, 108, BACK - 1), 131, course=8, blen=(14, 26), joint_i=2)
    NP.broken_top(im, 52, 108, 112, 126, 133)
    NP.behind(im, lambda lay: P.palm_trunk(lay, 84, 118, 52, lean=2, seed=5))
    d = ImageDraw.Draw(im)
    for x in (68, 98):                                             # 两根木桩
        vl(d, x, 106, BACK - 1, NP.WOOD)
        vl(d, x + 1, 106, BACK - 1, NP.WOOD_D)
    rect(d, 64, 102, 103, 117, (46, 86, 150), outline=(236, 232, 220))
    hl(d, 65, 102, 103, (78, 120, 182))
    P.sign_ar(d, 67, 104, 100, 109, (46, 86, 150), (240, 238, 228), seed=7)
    NP.tiny_text(d, 66 + (37 - NP.text_width('KOM OMBO')) // 2, 111, 'KOM OMBO', (244, 242, 232))
    hl(d, 64, 103, 118, NP.WOOD_K)
    P.soft_shadow(im, 64, 103, 119, depth=2, slant=2)


def draw_colonnade(im):
    """柱廊（x 108–238）：后墙（阴刻字，柱影里）→ 四根柱子 → 额枋 + 凹弧檐口。"""
    # 后墙：方石、上沿坍到 y 84–100；先按受光画，再把每根柱子的影子（往右 8 px）压暗 → 柱间斜进来的光
    NP.ashlar(im, (106, 84, 234, BACK - 1), 141, course=8, blen=(16, 30), joint_i=2, pits=0.01)
    NP.broken_top(im, 106, 234, 84, 100, 143)
    for k in range(10):
        NP.glyph_column(im, 110 + k * 13, 104, 136, 150 + k)
    a = np.array(im)
    sh = np.zeros((H, PW), bool)
    for cx in COLS:
        sh[60:BACK, cx - COL_W // 2 + 8:cx + COL_W // 2 + 8] = True
    sh[:, :106] = False
    sh[:, 235:] = False
    im.paste(Image.fromarray(a, 'RGBA'))
    NP.mul_mask(im, sh, NP.SHADOW_MUL)
    for i, cx in enumerate(COLS):
        NP.column(im, cx, BACK - 1, COL_TOP, COL_W, 160 + i, cap_h=12, flare=5)
        P.soft_shadow(im, cx - COL_W // 2, cx + COL_W // 2 + 2, BACK, depth=2, slant=5)
    # 额枋：一层大石梁（阴刻一行字）+ 上面的凹弧檐口；右端断口
    x0, x1, y0, y1 = ARCH
    NP.ashlar(im, (x0, y0, x1, y1), 171, course=10, blen=(30, 44), joint_i=2, top_hi=False)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1, y0 + 2, LAD[2])
    for x in range(x0 + 3, x1 - 2, 3):
        if hash01(173, x) < 0.7:
            px(d, x, y0 + 5, LAD[1])
            px(d, x + 1, y0 + 6, LAD[6])
    hl(d, x0, x1, y1, LAD[2])
    hl(d, x0, x1, y1 + 1, INK)
    vl(d, x0 - 1, y0, y1 + 1, INK)
    a = np.array(im)                                               # 右端断口：一级级缺
    for k, x in enumerate(range(x1 - 6, x1 + 1)):
        cut = y0 + max(0, (k - 1)) * 2
        a[y0:cut, x, 3] = 0
        if cut < y1:
            a[cut, x, :3] = LAD[6]
    a[y0:y1 + 2, x1 + 1, :3] = INK
    a[y0:y1 + 2, x1 + 1, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    cavetto(im, x0, x1 - 30, 16, y0 - 1, 175)
    # 额枋下沿往后墙落的一道影
    NP.mul_box(im, (x0, y1 + 2, x1, y1 + 5), NP.SOFT_MUL)


def draw_glyph_wall(im):
    """象形文字墙（x 236–304）：打磨过的大块方石（缝很淡）、上沿坍塌、kheker 饰带、一栏竖排字、三个神、纸莎草饰带、墙基。"""
    x0, x1 = WALL_G
    NP.ashlar(im, (x0 - 2, 44, x1 + 2, BACK - 1), 181, course=9, blen=(20, 36), var=1, pits=0.006, chips=0.12, joint_i=3)
    NP.broken_top(im, x0 - 2, x1 + 2, 44, 54, 183, step=(5, 12))
    d = ImageDraw.Draw(im)
    # kheker 饰带 y 56–62：一排束起来的芦苇头（每 4 px 一个），下面一道分栏线
    for x in range(x0, x1 + 1):
        k = (x - x0) % 4
        if k == 0:
            vl(d, x, 57, 62, LAD[2])
            px(d, x, 56, LAD[1])
        elif k == 1:
            px(d, x, 57, LAD[6])
            vl(d, x, 58, 62, LAD[5])
        elif k == 2 and hash01(185, x) < 0.5:
            vl(d, x, 59, 62, NP.PAINT['B'])
    hl(d, x0, x1, 63, LAD[1])
    hl(d, x0, x1, 64, LAD[6])
    for k in range(12):                                            # 一栏竖排字 y 66–72（神的名字和祷文）
        NP.glyph_column(im, x0 + 1 + k * 5 + (k // 4), 66, 73, 190 + k, colw=5, paint=0.35)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1, 74, LAD[1])
    for i, kind in enumerate(('anubis', 'horus', 'sobek')):
        g, m = NP.relief_god(kind)
        NP.place_relief(im, g, GODS_X[i], GOD_Y, 200 + i, wear=0.2)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1, GOD_Y + 41, LAD[1])                              # 神脚下的地线
    hl(d, x0, x1, GOD_Y + 42, LAD[6])
    # 纸莎草饰带 y 120–138：一排纸莎草（茎 + 伞形花），阴刻
    for k, x in enumerate(range(x0 + 2, x1 - 1, 5)):
        hgt = 12 + (k % 2) * 4
        vl(d, x, 137 - hgt, 137, LAD[2])
        vl(d, x + 1, 137 - hgt + 1, 137, LAD[6])
        for (dx, dy) in ((-2, 1), (-1, 0), (0, -1), (1, 0), (2, 1)):
            px(d, x + dx, 137 - hgt + dy, LAD[2] if hash01(187, k) < 0.6 else NP.PAINT['G'])
    hl(d, x0, x1, 139, LAD[1])
    hl(d, x0, x1, 140, LAD[6])
    vl(d, x0 - 3, 46, BACK - 1, INK)
    vl(d, x1 + 3, 46, BACK - 1, INK)
    vl(d, x1 + 2, 50, BACK - 1, LAD[2])
    vl(d, x0 - 2, 50, BACK - 1, LAD[5])


def draw_tourist_area(im):
    """游客站的空地（x 304–372）：后面一道坍得很矮的墙（中间最低，看得见远处的河）、两截断柱、一小堆方石、绳栏。"""
    NP.ashlar(im, (305, 104, 372, BACK - 1), 211, course=8, blen=(14, 28), joint_i=2)
    tops = []
    for x in range(305, 373):                                      # 墙顶：两头高、中间低（成块地缺）
        u = abs((x - 338) / 34.0)
        tops.append(int(124 - 18 * u ** 1.4 + hrange(-2, 2, 213, x // 6)))
    a = np.array(im)
    for k, x in enumerate(range(305, 373)):
        y = max(104, tops[k])
        a[104:y, x, 3] = 0
        a[y, x, :3] = LAD[6]
        a[y + 1, x, :3] = LAD[5]
        if y - 1 >= 0:
            a[y - 1, x, :3] = INK
            a[y - 1, x, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    NP.behind(im, lambda lay: P.palm_trunk(lay, 334, 124, 58, lean=-2, seed=11))
    NP.column(im, 318, BACK - 1, 0, 14, 215, cap='broken', broken=118, paint=False)
    NP.column(im, 352, BACK - 1, 0, 14, 216, cap='broken', broken=102, paint=False)
    NP.block(im, 360, BACK - 1, 11, 6, 217)
    NP.block(im, 366, BACK - 7, 7, 5, 218, shadow=False)
    NP.block(im, 306, BACK - 1, 8, 5, 219)
    d = ImageDraw.Draw(im)
    posts = (308, 330, 344, 371)                                   # 绳栏：铁桩 + 麻绳（两桩之间下垂）
    for x in posts:
        vl(d, x, 132, BACK - 1, (70, 66, 70))
        vl(d, x + 1, 133, BACK - 1, (40, 38, 44))
        px(d, x, 131, (150, 146, 150))
        px(d, x + 1, 131, (96, 92, 98))
    for (xa, xb) in zip(posts[:-1], posts[1:]):
        for x in range(xa + 1, xb + 1):
            u = (x - xa) / float(xb - xa)
            y = int(round(134 + 3.2 * 4 * u * (1 - u)))
            px(d, x, y, (210, 176, 120))
            px(d, x, y + 1, (150, 118, 80))


def mudbrick_wall(im, x0, x1, y0, y1, seed):
    """土坯墙：小砖（3 行一层、6–9 宽）+ 几片还没掉的抹灰（平、亮、边缘一圈裂）。"""
    NP.ashlar(im, (x0, y0, x1, y1), seed, lad=NP.MUDBRICK, base_i=3, course=3, blen=(6, 9), var=1, pits=0.0,
              chips=0.0, joint_i=1, top_hi=False, mott=True)
    a = np.array(im)
    hh, ww = y1 - y0 + 1, x1 - x0 + 1
    nz = A._fbm(ww + 8, hh + 8, 10, seed=seed % 997)[4:4 + hh, 4:4 + ww]
    pl = nz > 0.6
    sub = a[y0:y1 + 1, x0:x1 + 1]
    sub[pl, :3] = NP.MUDBRICK[4]
    edge = pl & ~np.roll(pl, 1, axis=0)
    sub[edge, :3] = NP.MUDBRICK[5]
    edge2 = pl & ~np.roll(pl, -1, axis=0)
    sub[edge2, :3] = NP.MUDBRICK[2]
    a[y0:y1 + 1, x0:x1 + 1] = sub
    im.paste(Image.fromarray(a, 'RGBA'))


def draw_workshop(im):
    """刀匠旧作坊（x 372–456）：土坯墙 + 烟熏、石台 + 刀架（三把锈弯刀、一个空钉子）、石砧、土灶、火钳、破陶罐。"""
    mudbrick_wall(im, 372, 456, 96, BACK - 1, 221)
    NP.broken_top(im, 372, 456, 94, 112, 223, step=(4, 10), lad=NP.MUDBRICK + [NP.MUDBRICK[-1]])
    a = np.array(im)                                               # 灶口上方的烟熏：往上散开的一片（fbm 定边，成片压暗）
    nz = A._fbm(40, 40, 6, seed=227)
    for y in range(98, 128):
        for x in range(430, 457):
            u = (128 - y) / 30.0
            dx = abs(x - 444) / (5 + 9 * u)
            if a[y, x, 3] and dx + 0.5 * nz[y - 98, x - 430] < 1.05 - 0.35 * u:
                a[y, x, :3] = (a[y, x, :3] * (0.5 if dx < 0.55 - 0.3 * u else 0.7)).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    vl(d, 371, 98, BACK - 1, INK)
    vl(d, 457, 100, BACK - 1, INK)
    # 土灶（x 434–454）：圆顶、黑灶口、口前一摊灰
    for y in range(122, BACK):
        u = (y - 122) / 23.0
        half = int(round(10 * min(1.0, 0.55 + u * 1.2)))
        for x in range(444 - half, 444 + half + 1):
            t = 4 if x < 444 - half // 3 else (3 if x < 444 + half // 2 else 2)
            px(d, x, y, NP.MUDBRICK[t])
        px(d, 444 - half - 1, y, INK)
        px(d, 444 + half + 1, y, INK)
    hl(d, 438, 450, 121, INK)
    rect(d, 439, 132, 449, 141, (34, 26, 24))
    hl(d, 440, 448, 131, NP.MUDBRICK[1])
    for x in range(439, 450):
        if hash01(229, x) < 0.6:
            px(d, x, 140, (110, 104, 100))
    hl(d, 436, 452, 145, (150, 144, 136))
    # 石台：两块石墩 + 一块石板
    NP.block(im, 394, BACK - 1, 7, 12, 231, shadow=False)
    NP.block(im, 424, BACK - 1, 7, 12, 232, shadow=False)
    NP.block(im, 390, 133, 44, 4, 233)
    d = ImageDraw.Draw(im)
    # 刀架后面的壁龛（墙上挖进去的一块，暗）：刀和架子要从同色的土坯墙里跳出来
    rect(d, RACK[0] - 2, 100, RACK[1] + 2, 129, (78, 58, 46))
    hl(d, RACK[0] - 2, RACK[1] + 2, 100, (52, 38, 32))
    vl(d, RACK[0] - 2, 100, 129, (52, 38, 32))
    hl(d, RACK[0] - 1, RACK[1] + 2, 101, (64, 48, 40))
    vl(d, RACK[1] + 3, 99, 129, NP.MUDBRICK[5])
    hl(d, RACK[0] - 2, RACK[1] + 3, 99, NP.MUDBRICK[5])
    # 刀架：两根木立柱 + 上下两道横梁 + 四个木钉
    for x in (RACK[0] + 2, RACK[1] - 3):
        vl(d, x, 104, 128, NP.WOOD)
        vl(d, x + 1, 104, 128, NP.WOOD_D)
        px(d, x, 103, NP.WOOD_HI)
    for y in (106, 120):
        hl(d, RACK[0], RACK[1], y, NP.WOOD_HI)
        hl(d, RACK[0], RACK[1], y + 1, NP.WOOD_D)
    vl(d, RACK[0] - 1, 103, 129, INK)
    vl(d, RACK[1] + 1, 103, 129, INK)
    hl(d, RACK[0], RACK[1], 105, INK)
    for x in RACK_PEGS:
        px(d, x, 108, NP.WOOD_K)
        px(d, x, 109, NP.WOOD)
    # 三把锈弯刀（挂在钉子上：刀柄朝上、刀身往下弯），第三个钉子空着
    for k, x in enumerate(RACK_PEGS):
        if x == RACK_EMPTY:
            px(d, x, 110, (196, 170, 130))                         # 空钉子下面：一圈没落灰的亮印子
            px(d, x, 111, (196, 170, 130))
            continue
        vl(d, x, 110, 113, (150, 104, 62))                         # 刀柄（缠着皮绳）
        px(d, x, 111, (96, 64, 40))
        hl(d, x - 1, x + 1, 114, (206, 168, 90))                   # 铜护手
        for j in range(14):                                        # 刀身：越往下越往右弯（弯刀），刃口一线发白
            yy = 115 + j
            xx = x + int(round(0.035 * j * j))
            px(d, xx, yy, RUST[1] if j % 4 == 3 else RUST[2])
            px(d, xx + 1, yy, (226, 214, 196) if j < 12 else RUST[3])
            if hash01(235, k, j) < 0.2:
                px(d, xx, yy, RUST[0])
    # 石砧（x 377–389）、火钳、破陶罐
    rect(d, 379, 139, 387, BACK - 1, (92, 88, 92))
    rect(d, 377, 136, 390, 138, (120, 116, 122))
    hl(d, 377, 390, 136, (164, 160, 166))
    px(d, 391, 137, (120, 116, 122))
    vl(d, 378, 139, BACK - 1, INK)
    vl(d, 388, 139, BACK - 1, (60, 56, 62))
    for k in range(10):
        px(d, 433 - k // 3, 135 + k, (70, 64, 66))
        px(d, 435 - k // 4, 135 + k, (70, 64, 66))
    for (cx, base, r) in ((412, BACK - 1, 4), (456, BACK - 1, 3)):
        for y in range(base - 2 * r + 1, base + 1):
            half = int(round(r * math.sqrt(max(0.0, 1 - ((y - (base - r)) / float(r)) ** 2))))
            for x in range(cx - half, cx + half + 1):
                px(d, x, y, (184, 104, 70) if x < cx else (146, 80, 56))
        hl(d, cx - r + 1, cx, base - 2 * r + 1, (210, 136, 96))
    a = np.array(im)                                               # 罐子破了一块
    a[BACK - 7:BACK - 4, 413:416, :3] = (70, 40, 32)
    im.paste(Image.fromarray(a, 'RGBA'))


def draw_statue(im):
    """残缺的雕像（x 456–532）：后墙 → 石座（一行横排字 + 右下的裂缝）→ 黑花岗岩坐像（脖子以上断了）。"""
    NP.ashlar(im, (458, 112, 532, BACK - 1), 241, course=8, blen=(14, 28), joint_i=2)
    NP.broken_top(im, 458, 532, 112, 126, 243)
    NP.behind(im, lambda lay: P.palm_trunk(lay, 470, 118, 46, lean=1, seed=13))
    d = ImageDraw.Draw(im)
    vl(d, 457, 114, BACK - 1, INK)
    NP.block(im, 460, BACK - 1, 13, 6, 245)
    x0, x1, top = PLINTH
    NP.ashlar(im, (x0, top, x1, BACK - 1), 247, course=26, blen=(40, 41), joint_i=3, pits=0.008, chips=0.0)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1, top, LAD[6])
    hl(d, x0, x1, top + 1, LAD[5])
    vl(d, x1 - 1, top + 1, BACK - 1, LAD[2])
    vl(d, x1, top + 1, BACK - 1, LAD[1])
    for x in range(x0 + 3, x1 - 3, 3):                             # 石座上一行横排字
        if hash01(249, x) < 0.8:
            px(d, x, 128, LAD[1])
            px(d, x + 1, 129, LAD[6])
            if hash01(250, x) < 0.5:
                px(d, x, 129, LAD[1])
    hl(d, x0 + 2, x1 - 3, 125, LAD[2])
    hl(d, x0 + 2, x1 - 3, 132, LAD[2])
    cx, y = 509, 136                                               # 右下的裂缝（缝里黑）
    for k in range(10):
        px(d, cx, y + k, (40, 30, 28))
        px(d, cx + 1, y + k, LAD[6] if k % 3 else LAD[5])
        if k % 3 == 2:
            cx += 1 if k < 6 else -1
    vl(d, x0 - 1, top, BACK - 1, INK)
    vl(d, x1 + 1, top, BACK - 1, INK)
    hl(d, x0, x1, top - 1, INK)
    # 灰花岗岩的站像（朝右、迈步）：脖子以上断了（断口一圈粗糙的亮面）、前臂断在肘部；肩宽腰细，一看就是“缺了头的人像”
    G = NP.GRANITE
    shape = {}                                                     # y → [(x0, x1), …]

    def span(y, x0_, x1_):
        shape.setdefault(y, []).append((x0_, x1_))
    for y in range(80, 83):                                        # 断颈
        span(y, 496, 500)
    for y in range(83, 87):                                        # 肩（宽）
        span(y, 490, 505)
    for y in range(87, 96):                                        # 胸 → 腰
        span(y, 491 + (y - 87) // 4, 504 - (y - 87) // 3)
    for y in range(87, 101):                                       # 后臂贴着身子垂下来，拳头在 y 99–101
        span(y, 489, 491)
    for y in range(87, 91):                                        # 前臂断在肘部
        span(y, 504, 506)
    for y in range(96, 106):                                       # 短裙（前片往前伸出一个三角）
        span(y, 493, 503 + max(0, (y - 99) // 2))
    for y in range(106, 118):                                      # 两条腿：后腿直、前腿往前迈
        span(y, 494, 497)
        f = (y - 106) / 11.0
        span(y, 500 + int(round(4 * f)), 503 + int(round(4 * f)))
    span(118, 492, 499)                                            # 脚
    span(118, 503, 510)
    span(119, 492, 499)
    span(119, 503, 510)
    for y, sp in shape.items():
        for (xa, xb) in sp:
            for xx in range(xa, xb + 1):
                u = (xx - xa) / max(1.0, float(xb - xa))
                t = 4 if u < 0.22 else (3 if u < 0.6 else 2)
                px(d, xx, y, G[t])
    hl(d, 496, 500, 80, (176, 172, 174))                           # 断颈的断面（受光、粗糙）
    px(d, 497, 79, (150, 146, 150))
    px(d, 499, 79, (150, 146, 150))
    hl(d, 490, 497, 83, G[5])                                      # 肩上的受光
    for xx in range(492, 503, 2):                                  # 胸前宽领刻的两道弧
        px(d, xx, 88 + abs(xx - 497) // 3, G[2])
        px(d, xx, 90 + abs(xx - 497) // 3, G[2])
    hl(d, 493, 503, 96, G[1])                                      # 腰带
    for xx in range(495, 503, 2):                                  # 短裙的褶
        vl(d, xx, 98, 104, G[2])
    hl(d, 504, 506, 87, (150, 146, 150))                           # 断臂的断面
    for (xx, yy) in ((492, 86), (501, 92), (495, 110), (505, 113)):
        px(d, xx, yy, G[5])                                        # 花岗岩的闪点
    a = np.array(im)                                               # 外沿墨线（站像整圈描，脚贴着石座不描下沿）
    m = np.zeros((H, PW), bool)
    for y, sp in shape.items():
        for (xa, xb) in sp:
            m[y, xa:xb + 1] = True
    nb = np.zeros_like(m)
    nb[:-1] |= m[1:]
    nb[1:] |= m[:-1]
    nb[:, 1:] |= m[:, :-1]
    nb[:, :-1] |= m[:, 1:]
    rim = nb & ~m
    rim[top:, :] = False
    a[rim, :3] = INK
    a[rim, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    P.soft_shadow(im, 492, 510, top, depth=2, slant=4)


def winged_disk(d, cx, cy):
    """带翅膀的日盘（门楣正中）：红日 + 两条眼镜蛇 + 往两边伸的翅膀（三道蓝 / 绿 / 红的羽毛带，往外越来越窄）。"""
    for k in range(1, 17):
        h_ = max(1, 4 - k // 5)
        for r in range(h_):
            c = (NP.PAINT['B'], NP.PAINT['G'], NP.PAINT['R'], NP.PAINT['B'])[r]
            if k % 2 == 0 and r == 0:
                c = dk(c, 0.82)
            px(d, cx - 3 - k, cy - 1 + r, c)
            px(d, cx + 3 + k, cy - 1 + r, c)
    for (dx, dy) in ((-2, -1), (-1, -2), (0, -2), (1, -2), (2, -1), (-2, 0), (-1, -1), (0, -1), (1, -1), (2, 0),
                     (-2, 1), (-1, 0), (0, 0), (1, 0), (2, 1), (-1, 1), (0, 1), (1, 1), (-1, 2), (0, 2), (1, 2)):
        px(d, cx + dx, cy + dy, NP.PAINT['R'])
    px(d, cx - 1, cy - 1, (232, 120, 96))
    for s in (-1, 1):                                              # 两条眼镜蛇（日盘两边垂下来）
        vl(d, cx + s * 3, cy, cy + 3, NP.PAINT['Y'])
        px(d, cx + s * 3, cy - 1, NP.PAINT['y'])


def draw_sanctum(im):
    """内殿的墙和门（x 532–594）：整面方石墙 + 凹弧檐口 → 门楣（带翅膀的日盘）+ 门框刻字 → 黑洞洞的门洞。"""
    NP.ashlar(im, (532, 36, 594, BACK - 1), 251, course=9, blen=(16, 30), joint_i=2)
    cavetto(im, 532, 592, 26, 35, 253)
    x0, x1, top = DOOR
    d = ImageDraw.Draw(im)
    rect(d, x0 - 8, 70, x1 + 6, top - 1, LAD[4])                   # 门楣 + 门框（打磨平的整块）
    hl(d, x0 - 8, x1 + 6, 70, LAD[6])
    hl(d, x0 - 8, x1 + 6, 76, LAD[2])
    hl(d, x0 - 8, x1 + 6, 77, LAD[6])
    for x in range(x0 - 8, x1 + 7):
        if (x - x0) % 3 == 0:
            vl(d, x, 71, 75, LAD[3])
    winged_disk(d, (x0 + x1) // 2, 84)
    NP.glyph_column(im, x0 - 7, top + 2, 140, 255, colw=6)
    NP.glyph_column(im, x1 + 1, top + 2, 140, 256, colw=6)
    d = ImageDraw.Draw(im)
    vl(d, x0 - 9, 70, BACK - 1, LAD[2])
    vl(d, x1 + 7, 70, BACK - 1, LAD[2])
    a = np.array(im)                                               # 门洞：黑、上沿 / 左沿再暗（墙厚挡光），门槛上一点沙
    for y in range(top, BACK):
        for x in range(x0, x1 + 1):
            u = (y - top) / float(BACK - top)
            c = np.array(DOOR_DARK, np.float32)
            if x - x0 > 3 and y - top > 3:
                c = c + np.array((10, 8, 8), np.float32) * (0.3 + 0.7 * u)
            a[y, x, :3] = c.astype(np.uint8)
    a[BACK - 2:BACK, x0:x1 + 1, :3] = (70, 58, 50)
    a[top, x0:x1 + 1, :3] = INK
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    vl(d, x0 - 1, top, BACK - 1, LAD[1])                           # 左门框内沿背光、右门框内沿（朝左）受光
    vl(d, x1, top + 1, BACK - 3, LAD[3])
    vl(d, x1 + 1, top, BACK - 1, LAD[5])
    hl(d, 532, 594, 25, INK)
    vl(d, 531, 26, BACK - 1, INK)


def draw_right_end(im):
    """最右（x 594–640）：两根柱子 + 额枋；两柱之间只有一道矮护墙（y 132 以下），上面透明 → 远景的尼罗河。"""
    NP.ashlar(im, (GAP[0] - 2, PARAPET, GAP[1] + 2, BACK - 1), 261, course=7, blen=(12, 20), joint_i=2)
    d = ImageDraw.Draw(im)
    hl(d, GAP[0] - 2, GAP[1] + 2, PARAPET, LAD[6])
    hl(d, GAP[0] - 2, GAP[1] + 2, PARAPET - 1, INK)
    for i, cx in enumerate(COL_R):
        NP.column(im, cx, BACK - 1, COL_TOP, COL_RW, 270 + i, cap_h=11, flare=4)
    NP.ashlar(im, (592, 24, PW - 1, 33), 281, course=10, blen=(26, 40), joint_i=2, top_hi=False)
    d = ImageDraw.Draw(im)
    hl(d, 592, PW - 1, 33, LAD[2])
    hl(d, 592, PW - 1, 34, INK)
    hl(d, 592, PW - 1, 23, INK)
    for x in range(594, PW, 3):
        if hash01(283, x) < 0.7:
            px(d, x, 28, LAD[1])
            px(d, x + 1, 29, LAD[6])
    NP.mul_box(im, (GAP[0], 35, GAP[1], 37), NP.SOFT_MUL)


@lru_cache(maxsize=1)
def near_img():
    im = A._new(PW, H)
    draw_ground(im)
    draw_pylon(im)
    draw_entrance(im)
    draw_flag_pole(im)                                             # 旗杆立在矮墙前面
    draw_glyph_wall(im)                                            # 字墙先画：第四根柱子的柱头往右张开，要盖在字墙左沿上
    draw_colonnade(im)
    draw_tourist_area(im)
    draw_workshop(im)
    draw_statue(im)
    draw_sanctum(im)
    draw_right_end(im)
    contact_shadow(im)
    P.compress_band(im, 126, BACK, (206, 176, 132), amt=0.1, ramp=10)
    return NP.opaque(im)


# ============================================================ 会动的
PALMS = [(86, 64, 12, 1), (332, 64, 13, 2), (471, 70, 11, 3)]      # (树冠中心 x, y, 半径, 种子)；树干画在近景里


def _palm_raw(i):
    cx, cy, R, sd = PALMS[i]

    def raw(f):
        im = A._new(PW, H)
        P.palm_crown(im, cx, cy, R, seed=sd, f=f)
        return P.outer_rim(im)
    return raw


FLAG_X, FLAG_Y = 61, 70


def _flag_raw(f):
    im = A._new(PW, H)
    P.egypt_flag(ImageDraw.Draw(im), FLAG_X, FLAG_Y, f, L=12, hgt=7)
    return im


SWALLOW_BOX = (110, 38, 236, 66)
MOTE_GAPS = [(cx + COL_W // 2 + 8, cx + 34 - COL_W // 2) for cx in COLS[:3]]


def _motes_raw():
    base = NP.motes_raw((PW, H), (COLS[0], 62, COLS[3], 138), 41, n=22)

    def raw(f):
        im = base(f)
        a = np.array(im)
        keep = np.zeros(PW, bool)
        for (g0, g1) in MOTE_GAPS:
            keep[g0:g1 + 1] = True
        a[:, ~keep, 3] = 0
        return Image.fromarray(a, 'RGBA')
    return raw


@lru_cache(maxsize=1)
def strips():
    """近景 strip：[(名字, 框, 帧函数)]，框按画出来的东西算（auto_box）。"""
    out = []
    for i in range(len(PALMS)):
        fn = NP.cached_frames(_palm_raw(i))
        out.append(('palm_%d' % i, P.auto_box(fn, N, FPS), fn))
    fn = NP.cached_frames(_flag_raw)
    out.append(('flag', P.auto_box(fn, N, FPS), fn))
    fn = NP.cached_frames(NP.swallows_raw((PW, H), SWALLOW_BOX, 51, n=3))
    out.append(('swallows', P.auto_box(fn, N, FPS), fn))
    fn = NP.cached_frames(_motes_raw())
    out.append(('motes', P.auto_box(fn, N, FPS), fn))
    return out


# ============================================================ 图层表 / 导出
@lru_cache(maxsize=1)
def table():
    tb = [('static', 'sky', sky_img(), 0, 0),
          ('wrap', 'clouds', clouds_img(), CLOUD_P, CLOUD_K, 6, CLOUD_VX)]
    fim, fy = P.crop_pano(far_img())
    tb.append(('pano', 'far', fim, FAR_K, 0, fy))
    gf = glint_fn()
    tb.append(('strip', 'glint', P.auto_box(gf, N, FPS), N, FPS, gf, FAR_K))
    boats = felucca_imgs()
    tb.append(('clouds', 'felucca', BOAT_SPAN,
               [('felucca%d' % i, boats[i], b[0], b[1], b[2], FAR_K) for i, b in enumerate(BOATS)]))
    kimg, kl = NP.kites()
    tb.append(('clouds', 'kites', 460, [('kite%d' % i, kimg, x0, y, vx, k) for i, (y, vx, k, x0) in enumerate(kl)]))
    nim, ny = P.crop_pano(near_img())
    tb.append(('pano', 'near', nim, 1.0, 0, ny))
    for (name, box, fn) in strips():
        tb.append(('strip', name, box, N, FPS, fn, 1.0))
    return tuple(tb)


def compose(camX, t=0.5, state=None):
    return P.compose(table(), camX, t, state)


def anchors():
    anc = {k: list(v) for k, v in ANCHORS.items()}
    anc.update(
        gods={k: [GODS_X[i] + 9, GOD_Y + 6] for i, k in enumerate(('anubis', 'horus', 'sobek'))},
        hieroglyph_box=[WALL_G[0], 56, WALL_G[1], 141],
        rack_box=[RACK[0], 103, RACK[1] + 1, 133],
        rack_empty=[RACK_EMPTY, 110],
        door_box=[DOOR[0], DOOR[2], DOOR[1] + 1, BACK],
        nile_gap=[GAP[0], 36, GAP[1] + 1, PARAPET],
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
    cfg = dict(title='科翁坡神殿', PW=PW, walk=WALK, near=near_img(), opaque_rows=(BACK, H), sky=sky_img(),
               states=[{}], stand=STAND, required=REQUIRED, size_limit=250 * 1024, cams_step=40,
               flat=(0, PW, WALK[0], WALK[1] + 1, 22, 0.012))
    P.common_checks(ex, BJ, st, tb, cfg)
    NP.anchor_values(ex, anc, ANCHORS)
    # 扔刀的方向：nile_view 周围 9×9 在近景里是透明的，拼出来是远景的河面（水色：偏蓝绿，不是天也不是墙）
    a = np.array(near_img())
    nx, ny = ANCHORS['nile_view']
    ex.checked('nile_view 周围 9×9 近景透明（露出远景）', int((a[ny - 4:ny + 5, nx - 4:nx + 5, 3] > 0).sum()))
    bad = 0
    for camX in (300, 310, 320):
        im = np.array(compose(camX, 0.0).convert('RGB')).astype(int)
        sx = nx - camX
        win = im[ny - 2:ny + 3, sx - 3:sx + 4].reshape(-1, 3)
        wet = sum(1 for (r, g, b) in win if b >= r - 6 and g >= r - 6 and r < 200)
        bad += 0 if wet >= 0.6 * len(win) else 1
    ex.checked('nile_view 拼出来是水面（镜头 300 / 310 / 320，7×5 里六成以上是偏蓝绿的水色）', bad)
    # 三个神的头在 y 50 以下（对白框盖不到）、站在可走带后沿的人（头顶 ≥ y 115）挡不到神像
    ex.checked('三个神像在 y %d–%d（对白框以下、后沿的人头以上）' % (GOD_Y, GOD_Y + 40),
               0 if (GOD_Y >= 50 and GOD_Y + 40 <= 116) else 1)
    # 刀架那段（剧情摆恰卡 + 弯刀）可走带只有地面
    lum = P._lum(a[..., :3].astype(np.float32))
    seg = lum[WALK[0]:WALK[1] + 1, 380:440]
    ex.checked('刀架前 x 380–440 可走带只有铺地（和中位亮度差 > 24 的像素）',
               int((np.abs(seg - np.median(seg)) > 24).sum()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch9', 'after')
    os.makedirs(od, exist_ok=True)
    full = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    for cx in (0, 320):
        full.paste(compose(cx, 0.5), (cx, 0))
    full.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'egypt_temple_solo.png'))
    print('ok')
