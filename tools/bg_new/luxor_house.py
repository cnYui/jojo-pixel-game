# -*- coding: utf-8 -*-
r"""luxor_house —— 第9章「卢克索的民宅」：第 20 战段 1 小孩波鲁纳雷夫的躲猫猫、段 2 小学生承太郎（阿莱西 / 塞特神）。
2026-10-19 egypt-town 组按体验版精度重画（改前是 later_stages.room('house')：一块平涂的房间）。零件在 egypt_town_parts.py。

地图 640 宽、ground 160、可走带 y 146–176（花砖地，对比压得很低；客厅一块旧地毯也是平的）；侧视平视，两间房：
左客厅（x 0–316）、右卧室（x 324–640），x 320 一道门框（anchors.door）。墙脚 = 地面后沿 y 146，家具都靠墙、画在 y ≤ 145。
**光**：下午很热，百叶窗都关着，屋里暗；唯一亮的是客厅天花板垂下来的吊灯（anchors.lamp [300,96]）——剧情按它算阿莱西
影子的方向，所以这张图的明暗也按它来：离灯越远越暗（一圈圈分档、Bayer 抖开边），每件家具朝灯的那一面亮、影子往离灯的方向落；
灯左边的家具按“太阳在左”画好再左右翻（零件都是左边受光）。窗缝里漏进来几道日光，落在地上是几块淡淡的光斑（灰尘在里面飘 strip）。
从左到右（世界坐标）：
  x 4–34      客厅大门（木门，门缝下一道光）（anchors.arrive 在门前）
  x 42–76     落地窗 + 两幅到地的酒红色窗帘（金色流苏、帘头、铜帘杆），两幅之间露出一道关着的百叶窗、缝里透光
              （藏身点 1：anchors.hide_curtain，框 hide_curtain_box）
  x 80–134    “法鲁克式”的描金沙发（墨绿丝绒、雕花靠背）；墙上一幅尼罗河帆船的油画
  x 138–172   高大的胡桃木衣柜（雕花顶、左门一面椭圆镜子、右门虚掩着一道黑缝、黄铜拉手）（藏身点 2）
  x 176–220   电视角：木电视柜 + 带木纹外壳的电视（兔耳天线）+ 一瓶塑料花；墙上一只带钟摆的挂钟（strip）
  x 224–274   大鱼缸（木柜做的座、黑框玻璃缸、灯罩、水草、小城堡、气泡和三条鱼都在 strip）——缸有 46×30，比小孩还大
              （藏身点 3：anchors.hide_aquarium，伏击只在这）；墙上一块“奉至仁至慈的真主之名”的书法框
  x 278–294   一盆橡皮树
  x 300       吊灯：从天花板垂下一根长线、乳白玻璃灯罩、灯泡亮着，墙上一圈暖光（anchors.lamp）
  x 308–332   两间房中间的门框（木框、里面是暗的过道、开着的门扇贴在卧室那边）（anchors.door）
  x 338–374   卧室的窗（百叶窗半关、窗台上一盆罗勒）+ 窗下的床头柜（小台灯、闹钟、一杯水）
  x 388–450   木床（雕花床头、白枕头、花被子垂到床沿、床腿之间床底一道黑缝：躲得进一个小孩）（藏身点 4）
  x 456–484   墙上一张结婚照、上面一台吊扇（strip 转）
  x 490–524   一只大木箱（木板 + 斜撑 + 两只绳把手 + 喷的字，上面叠着一条毯子）（藏身点 5）
  x 528–550   墙上一块小搁板（香水瓶、梳子）
  x 552–590   碗柜（上半截纱门里摆着盘子茶杯、中间台面上一把水壶、下半截两扇木门）（藏身点 6）
  x 600–632   卧室另一扇高窗（百叶关着、旁边扎起来的窗帘），窗缝的光落在地上
天花板 y 0–13（一道石膏线脚），墙裙 y 118–145（油漆的深一档的护墙 + 一道细线 + 木踢脚板）。
key：axe_curtain、axe_wardrobe、axe_aquarium、axe_bed、axe_crate、axe_cupboard（pick：0 = 没砍过、1 = 斧痕 / 碎木 / 玻璃裂纹 /
     割破的布、地上的木屑。只叠在家具上，不挡 strip 里的鱼）。

图层（从后往前）：
  room      static           整张房间（640 宽，k 1 的 pano：天花板 / 墙 / 家具 / 地，已按吊灯打好光）
  fish      strip  k 1       鱼缸：三条鱼游、气泡、水草摆（8 帧 @4 fps）
  clock     strip  k 1       挂钟的钟摆
  fan       strip  k 1       卧室吊扇
  dust_0/1  strip  k 1       两道窗缝光里飘的灰尘
  axe_*     pick   k 1       六处砍过的痕迹（剧情开 axe_<名字>）
锚点：arrive [40,166]、door [320,156]、hide_curtain [58,156]、hide_wardrobe [155,156]、hide_aquarium [249,156]、
      hide_bed [418,160]、hide_crate [506,160]、hide_cupboard [570,156]、hide_*_box（六个家具框）、lamp [300,96]（素材总表）；
      另导出 lamp_cord [300,14]（吊灯线顶）、floor_back 146。六个藏身点从左到右：curtain、wardrobe、aquarium、bed、crate、cupboard。
单独运行：python -B tools\bg_new\luxor_house.py → tools\bg_new\_preview\ch9\after\luxor_house_solo.png
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
from engine import bg_asia as A  # noqa: E402


def _parts():
    """egypt-town 组的零件（tools\\bg_new\\egypt_town_parts.py，按路径加载，模块名同 bg_jojo.bg_new，不改 sys.path 顺序）。"""
    key = 'bg_new_egypt_town_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'egypt_town_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
V = P.V
C = P.C
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
mul_box, mul_mask, poly_mask, cast_shadow, mottle, opaque = (P.mul_box, P.mul_mask, P.poly_mask, P.cast_shadow,
                                                            P.mottle, P.opaque)
SHADOW_MUL, SOFT_MUL = P.SHADOW_MUL, P.SOFT_MUL
IRON, IRON_HI, BRASS = P.IRON, P.IRON_HI, P.BRASS
DARK_IN = P.DARK_IN
cached = P.cached_frames

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (146, 176)
LANE = 146                     # 墙脚 = 地面后沿
N, FPS = P.N_ANIM, P.FPS_ANIM
CEIL = 13                      # 天花板线脚的下沿
DADO = 118                     # 墙裙的上沿
SKIRT = 142                    # 踢脚板的上沿
LAMP = (300, 96)
DIVIDE = 320

# 六个藏身点：名字 → (站点, 家具框 [x0, y0, x1, y1]，世界坐标、x1 / y1 不含)
HIDES = {
    'curtain': ([58, 156], [42, 40, 76, 146]),
    'wardrobe': ([155, 156], [136, 76, 174, 146]),
    'aquarium': ([249, 156], [224, 82, 274, 146]),
    'bed': ([418, 160], [388, 104, 450, 146]),
    'crate': ([506, 160], [490, 116, 524, 146]),
    'cupboard': ([570, 156], [552, 86, 590, 146]),
}
ANCHORS = dict(arrive=[40, 166], door=[320, 156], lamp=list(LAMP))
for _k, (_pt, _bx) in HIDES.items():
    ANCHORS['hide_' + _k] = list(_pt)
    ANCHORS['hide_%s_box' % _k] = list(_bx)
STAND = ('arrive', 'door') + tuple('hide_' + k for k in HIDES)
REQUIRED = tuple(ANCHORS)

# ============================================================ 调色
WALL_L = (182, 204, 186)       # 客厅：淡薄荷绿
WALL_R = (226, 198, 188)       # 卧室：淡藕粉
DADO_L = (122, 150, 132)       # 墙裙（油漆，深一档）
DADO_R = (176, 136, 132)
CEIL_C = (214, 206, 190)
TILE = (186, 174, 154)         # 花砖
TILE_M = (176, 163, 143)       # 花砖上的花（深一点）
TILE_G = (170, 158, 138)       # 砖缝
WALNUT = ((168, 116, 72), (128, 84, 50), (96, 62, 38), (66, 42, 28))       # 亮 / 中 / 暗 / 深
PINE = ((200, 160, 104), (170, 130, 80), (136, 100, 60), (100, 72, 44))
GOLD = ((250, 222, 140), (214, 170, 74), (170, 126, 48), (118, 84, 34))
VELVET = ((90, 150, 110), (60, 112, 82), (42, 84, 60), (28, 56, 42))
WINE = ((196, 70, 80), (150, 40, 52), (114, 28, 40), (78, 18, 28))
WATER_C = ((110, 190, 204), (64, 150, 176), (44, 112, 146), (30, 80, 112))   # 水：比墙深、偏蓝，一眼看得出是一缸水
LAMP_C = (255, 240, 196)
FLOOR_SHADOW = np.array((0.92, 0.92, 0.95), np.float32)


def fidx(t):
    return P.frame_of(t, N, FPS)


def side_of(x):
    """家具在灯的哪一边：灯左边的要翻（朝灯的右边受光）。"""
    return x < LAMP[0]


# ============================================================ 房间：墙 / 天花板 / 地
def draw_shell(im):
    d = ImageDraw.Draw(im)
    # 两面墙（客厅薄荷绿 / 卧室藕粉），分界在门框正中
    for (x0, x1, wall, dado, seed) in ((0, DIVIDE, WALL_L, DADO_L, 1301), (DIVIDE, PW, WALL_R, DADO_R, 1302)):
        rect(d, x0, CEIL + 1, x1 - 1, DADO - 1, wall)
        mottle(im, (x0, CEIL + 1, x1 - 1, DADO - 1), wall, dk(wall, 0.95), lt(wall, 0.06), seed, cell=5, streaks=3)
        d = ImageDraw.Draw(im)
        rect(d, x0, DADO, x1 - 1, SKIRT - 1, dado)
        mottle(im, (x0, DADO + 1, x1 - 1, SKIRT - 1), dado, dk(dado, 0.94), lt(dado, 0.06), seed + 7, cell=4)
        d = ImageDraw.Draw(im)
        hl(d, x0, x1 - 1, DADO, lt(dado, 0.35))                      # 墙裙上沿的一道细线
        hl(d, x0, x1 - 1, DADO + 1, dk(dado, 0.8))
        rect(d, x0, SKIRT, x1 - 1, LANE - 1, WALNUT[2])               # 踢脚板
        hl(d, x0, x1 - 1, SKIRT, WALNUT[1])
        hl(d, x0, x1 - 1, LANE - 1, WALNUT[3])
        # 墙上滚筒刷的花纹（80 年代埃及民宅常见的“滚花”：一排排小四瓣花，比墙深一点点）
        for y in range(CEIL + 8, DADO - 4, 10):
            for x in range(x0 + 4 + (y // 10 % 2) * 6, x1 - 3, 12):
                c = dk(wall, 0.93)
                px(d, x, y, c)
                px(d, x - 1, y + 1, c)
                px(d, x + 1, y + 1, c)
                px(d, x, y + 2, c)
    # 天花板 + 石膏线脚
    rect(d, 0, 0, PW - 1, CEIL - 4, CEIL_C)
    for x in range(0, PW, 40):                                     # 天花板上一道道棕榈木梁的端头（深色方块）
        rect(d, x + 6, 0, x + 13, CEIL - 6, (190, 176, 154))
        hl(d, x + 6, x + 13, CEIL - 6, (168, 154, 134))
    rect(d, 0, CEIL - 3, PW - 1, CEIL, (236, 230, 216))
    hl(d, 0, PW - 1, CEIL - 3, (250, 246, 236))
    hl(d, 0, PW - 1, CEIL - 1, (196, 188, 172))
    hl(d, 0, PW - 1, CEIL + 1, (160, 150, 136))                    # 线脚下面一道影
    # 地：花砖（一排排往前变高、每块砖中间一朵四瓣花，对比压得很低）
    rows = [LANE, 149, 153, 158, 164, 171, H]
    for r in range(len(rows) - 1):
        ya, yb = rows[r], rows[r + 1]
        sw = 8 + (yb - ya) * 2
        off = (r % 2) * (sw // 2)
        for y in range(ya, yb):
            for x in range(PW):
                u = (x + off) % sw
                v = y - ya
                c = TILE
                if u == 0 or v == 0:
                    c = TILE_G
                else:
                    cu, cv = abs(u - sw // 2), abs(v - (yb - ya) // 2)
                    if (cu <= 1 and cv <= max(1, (yb - ya) // 3)) or (cv == 0 and cu <= sw // 4):
                        c = TILE_M
                px(d, x, y, c)


def draw_rug(im):
    """客厅地上一块旧地毯（褪色的红 + 米色花边 + 中间一块菱形），平的。"""
    d = ImageDraw.Draw(im)
    for y in range(152, 172):
        u = (y - 152) / 19.0
        a = int(round(86 - u * 8))
        b = int(round(220 + u * 8))
        for x in range(a, b + 1):
            c = (150, 92, 80)
            edge = min(x - a, b - x, y - 152, 171 - y)
            if edge == 0:
                c = (196, 170, 130)
            elif edge == 2:
                c = (184, 150, 110)
            elif edge > 3:
                cx, cy = (a + b) / 2.0, 161.5
                if abs(x - cx) / 40.0 + abs(y - cy) / 7.0 < 1.0:
                    c = (110, 104, 124) if (abs(x - cx) / 40.0 + abs(y - cy) / 7.0) < 0.6 else (166, 128, 96)
                elif (x + y) % 9 == 0:
                    c = (170, 110, 90)
            px(d, x, y, c)
        if y % 2 == 0:                                             # 两头的穗
            px(d, a - 1, y, (210, 196, 170))
            px(d, b + 1, y, (210, 196, 170))


# ============================================================ 家具（局部坐标、太阳在左；灯左边的会翻）
def wardrobe_img(w, h, dmg=False):
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = WALNUT
    top = 6
    # 雕花顶（一道冠线 + 中间的花饰）
    hl(d, 0, w - 1, top, hi)
    hl(d, 0, w - 1, top + 1, md)
    hl(d, 1, w - 2, top + 2, sh)
    for k in range(5):
        hl(d, w // 2 - 5 + k, w // 2 + 5 - k, top - 1 - k, md if k % 2 else hi)
    rect(d, 1, top + 3, w - 2, h - 5, md)
    vl(d, 1, top + 3, h - 5, hi)
    vl(d, w - 2, top + 3, h - 5, kk)
    mid = w // 2
    for (a, b) in ((3, mid - 1), (mid + 1, w - 4)):                 # 两扇门（门板 + 凹框）
        rect(d, a, top + 5, b, h - 9, md)
        rect(d, a + 2, top + 8, b - 2, h - 12, sh)
        rect(d, a + 3, top + 9, b - 3, h - 13, md)
        hl(d, a + 2, b - 2, top + 8, kk)
        vl(d, a + 2, top + 8, h - 12, kk)
        hl(d, a + 3, b - 2, h - 12, hi)
        vl(d, b - 2, top + 9, h - 12, hi)
        for y in range(top + 10, h - 13, 3):                       # 木纹
            if hash01(a, y, 1311) < 0.6:
                hl(d, a + 4, b - 4, y, dk(md, 0.92))
    cx, cy = (3 + mid - 1) // 2, (top + h - 9) // 2                 # 左门的椭圆镜子
    d.ellipse((cx - 4, cy - 8, cx + 4, cy + 8), fill=C(GOLD[2]))
    d.ellipse((cx - 3, cy - 7, cx + 3, cy + 7), fill=C((150, 170, 176)))
    for k in range(4):
        px(d, cx - 2 + k // 2, cy - 5 + k, (214, 228, 232))
    vl(d, mid, top + 5, h - 9, kk)                                 # 右门虚掩：中缝一道黑
    vl(d, mid + 1, top + 5, h - 9, DARK_IN)
    for x in (mid - 2, mid + 3):                                   # 黄铜拉手
        rect(d, x, cy - 2, x, cy + 2, GOLD[1])
        px(d, x, cy - 2, GOLD[0])
    rect(d, 1, h - 8, w - 2, h - 5, sh)                             # 底座 + 一个抽屉
    hl(d, 1, w - 2, h - 8, hi)
    rect(d, mid - 2, h - 7, mid + 2, h - 6, GOLD[1])
    for x in (2, w - 4):                                           # 矮脚
        rect(d, x, h - 4, x + 1, h - 1, kk)
    if dmg:
        axe_marks(d, [(mid + 3, top + 14, 9, 1), (mid + 6, top + 26, 7, -1), (4, h - 20, 6, 1)], md)
        chips(d, w, h, 7, PINE[0], seed=1)
    return im


def axe_marks(d, cuts, wood_mid):
    """斧痕：一道道斜着的深口子（黑芯 + 下沿一道翻起来的浅木茬），cuts = [(x, y, 长, 斜向)]。"""
    for (x, y, L, s) in cuts:
        for k in range(L):
            xx, yy = x + k, y + int(round(k * 0.5 * s))
            px(d, xx, yy, (34, 22, 18))
            px(d, xx, yy + 1, (60, 36, 26))
            px(d, xx, yy - 1, lt(wood_mid, 0.35))                  # 翻起来的新木头（浅）
            if k % 3 == 1:
                px(d, xx + 1, yy - 2, lt(wood_mid, 0.5))           # 木刺
    return d


def chips(d, w, h, n, col, seed=0):
    """砍下来的碎木屑：散在家具脚下（局部坐标的最下面两行）。"""
    for i in range(n):
        x = int(hrange(0, w - 2, seed, i, 1))
        y = h - 1 - int(hrange(0, 2, seed, i, 2))
        px(d, x, y, col)
        if i % 2 == 0:
            px(d, x + 1, y, dk(col, 0.8))


def aquarium_img(w, h, dmg=False):
    """大鱼缸：下面木柜座（两扇门）、上面黑框玻璃缸（灯罩、水、底砂、水草、小城堡）。鱼、气泡在 strip。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = WALNUT
    st = AQ_STAND
    rect(d, 0, st, w - 1, h - 3, md)                                # 柜座
    hl(d, 0, w - 1, st, hi)
    vl(d, 0, st, h - 3, hi)
    vl(d, w - 1, st, h - 3, kk)
    for (a, b) in ((3, w // 2 - 2), (w // 2 + 1, w - 4)):
        rect(d, a, st + 3, b, h - 6, sh)
        rect(d, a + 1, st + 4, b - 1, h - 7, md)
        px(d, b - 2 if a < w // 2 else a + 2, (st + h) // 2, GOLD[1])
    for x in (1, w - 3):
        rect(d, x, h - 2, x + 1, h - 1, kk)
    # 缸：灯罩（黑）+ 玻璃框（深灰，四角亮）+ 水（上浅下深）+ 底砂
    rect(d, 0, 0, w - 1, 3, (40, 40, 44))
    hl(d, 0, w - 1, 0, (90, 90, 96))
    hl(d, 2, w - 3, 3, (250, 246, 220))                             # 灯罩下沿的灯条
    tx0, ty0, tx1, ty1 = AQ_WATER
    rect(d, tx0 - 2, ty0 - 2, tx1 + 1, ty1 + 1, (40, 42, 46))            # 黑框（上下沿 2 px、两边 2 px）
    vl(d, tx0 - 2, ty0 - 2, ty1 + 1, (150, 156, 160))                  # 框的受光边（银）
    hl(d, tx0 - 2, tx1 + 1, ty1 + 1, (70, 72, 76))
    for y in range(ty0, ty1):
        u = (y - ty0) / float(ty1 - ty0)
        c = WATER_C[0] if u < 0.12 else (WATER_C[1] if u < 0.5 else WATER_C[2])
        hl(d, tx0, tx1 - 1, y, c)
    hl(d, tx0, tx1 - 1, ty0, lt(WATER_C[0], 0.3))                  # 水面
    for y in range(ty1 - 4, ty1):                                  # 底砂（彩色小石子）
        for x in range(tx0, tx1):
            r = hash01(x, y, 1321)
            px(d, x, y, (214, 190, 140) if r < 0.6 else ((170, 140, 100) if r < 0.85 else (220, 120, 100)))
    # 小城堡（左下）
    cx = tx0 + 5
    rect(d, cx, ty1 - 11, cx + 7, ty1 - 4, (200, 170, 130))
    for k in range(0, 8, 2):
        px(d, cx + k, ty1 - 12, (200, 170, 130))
    rect(d, cx + 2, ty1 - 8, cx + 4, ty1 - 4, (60, 50, 50))
    vl(d, cx + 7, ty1 - 11, ty1 - 4, (160, 130, 96))
    # 一块石头（右下）+ 气泵管
    d.ellipse((tx1 - 12, ty1 - 7, tx1 - 3, ty1 - 3), fill=C((110, 112, 106)))
    px(d, tx1 - 10, ty1 - 7, (150, 150, 144))
    vl(d, tx1 - 16, ty0 + 1, ty1 - 4, (200, 210, 210))
    rect(d, tx1 - 17, ty1 - 5, tx1 - 15, ty1 - 4, (90, 90, 96))
    # 玻璃的反光：左上一道斜的亮
    for k in range(3):                                             # 只在角上一小道（长了会被看成一串气泡）
        px(d, tx0 + 1 + k, ty0 + 1 + k * 2, lt(WATER_C[0], 0.45))
        px(d, tx0 + 1 + k, ty0 + 2 + k * 2, lt(WATER_C[0], 0.25))
    vl(d, tx0 - 1, ty0 - 1, ty1, (120, 126, 130))                   # 框的受光边
    if dmg:
        cx, cy = tx0 + (tx1 - tx0) * 2 // 3, ty0 + 9                 # 玻璃上一个砍出来的星形裂纹
        for ang in range(0, 360, 45):
            L = 6 + (ang // 45) % 3 * 2
            for j in range(1, L):
                xx = cx + int(round(math.cos(math.radians(ang + 7)) * j))
                yy = cy + int(round(math.sin(math.radians(ang + 7)) * j * 0.8))
                if tx0 <= xx < tx1 and ty0 <= yy < ty1:
                    px(d, xx, yy, (240, 250, 250))
        d.ellipse((cx - 1, cy - 1, cx + 1, cy + 1), fill=C((30, 40, 44)))
        for k in range(5):                                          # 柜门上一道斧痕
            px(d, w // 2 + 3 + k, st + 6 + k // 2, (34, 22, 18))
            px(d, w // 2 + 3 + k, st + 5 + k // 2, lt(md, 0.35))
    return im


AQ_STAND = 42                  # 鱼缸局部坐标：柜座上沿
AQ_WATER = (3, 7, 47, 39)      # 水的范围（局部 x0, y0, x1, y1 不含）：44×32，比小孩（13×18）大得多


def sofa_img(w, h):
    """法鲁克式沙发：描金的雕花木框（拱形靠背顶上一朵花饰）、墨绿丝绒的靠背和坐垫、两边扶手、弯腿。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    g0, g1, g2, g3 = GOLD
    v0, v1, v2, v3 = VELVET
    # 靠背：拱形的金框 + 丝绒（上亮下暗、几颗拉扣）
    for x in range(3, w - 3):
        u = (x - w / 2.0) / (w / 2.0 - 3)
        t = 4 + int(round(6 * u * u))
        for y in range(t, h - 13):
            c = v1 if y > t + 2 else v0
            if (x + y) % 7 == 0 and y > t + 3:
                c = v2
            px(d, x, y, c)
        px(d, x, t - 1, g1 if x < w // 2 else g2)
        px(d, x, t - 2, g0 if x < w // 2 else g1)
    for k in range(5):                                             # 顶上的花饰
        hl(d, w // 2 - 3 + k // 2, w // 2 + 3 - k // 2, 1 + k, g1 if k % 2 else g0)
    for x in range(8, w - 8, 9):                                   # 拉扣
        px(d, x, 10 + ((x // 9) % 2) * 3, v3)
    # 扶手（两边金色卷头）
    for (a, sgn) in ((0, 1), (w - 6, -1)):
        rect(d, a, h - 18, a + 5, h - 9, v1)
        d.ellipse((a, h - 20, a + 5, h - 15), fill=C(g1))
        px(d, a + 1, h - 19, g0)
        vl(d, a, h - 18, h - 9, g1)
        vl(d, a + 5, h - 18, h - 9, g2)
    # 坐垫
    rect(d, 5, h - 13, w - 6, h - 9, v0)
    hl(d, 5, w - 6, h - 13, lt(v0, 0.2))
    hl(d, 5, w - 6, h - 9, v2)
    vl(d, w // 2, h - 13, h - 10, v2)
    # 下框 + 弯腿
    hl(d, 1, w - 2, h - 8, g1)
    hl(d, 1, w - 2, h - 7, g2)
    for x in (3, w // 2, w - 5):
        d.line((x, h - 6, x + (1 if x < w // 2 else -1), h - 1), fill=C(g2))
        px(d, x, h - 6, g0)
    # 一个绣花靠垫
    rect(d, 8, h - 20, 15, h - 14, (210, 170, 90))
    hl(d, 8, 15, h - 20, (236, 200, 120))
    px(d, 11, h - 17, (170, 60, 50))
    return im


def tv_corner_img(w, h):
    """电视角：木电视柜（两扇门）、上面带木纹外壳的电视（灰屏 + 一道反光、旋钮、兔耳天线）、钩花桌布、一瓶塑料花。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = WALNUT
    ct = h - 20
    rect(d, 2, ct, w - 3, h - 3, md)
    hl(d, 2, w - 3, ct, hi)
    vl(d, 2, ct, h - 3, hi)
    vl(d, w - 3, ct, h - 3, kk)
    for (a, b) in ((5, w // 2 - 2), (w // 2 + 1, w - 6)):
        rect(d, a, ct + 4, b, h - 6, sh)
        rect(d, a + 1, ct + 5, b - 1, h - 7, md)
    for x in (3, w - 5):
        rect(d, x, h - 2, x + 1, h - 1, kk)
    for x in range(4, w - 4):                                      # 钩花桌布（白，下沿一排小三角）
        px(d, x, ct - 1, (236, 232, 222))
        if x % 3 == 0:
            px(d, x, ct, (236, 232, 222))
    # 电视
    ta, tb, tt = 6, w - 12, ct - 22
    rect(d, ta, tt, tb, ct - 2, (126, 86, 54))
    hl(d, ta, tb, tt, (160, 116, 76))
    vl(d, tb, tt, ct - 2, (90, 60, 40))
    rect(d, ta + 2, tt + 3, tb - 9, ct - 5, (60, 66, 70))           # 屏幕
    rect(d, ta + 3, tt + 4, tb - 10, ct - 6, (84, 92, 96))
    for k in range(4):
        px(d, ta + 4 + k, tt + 5 + k // 2, (130, 140, 146))
    for k in range(3):                                             # 旋钮
        d.ellipse((tb - 6, tt + 4 + k * 5, tb - 3, tt + 7 + k * 5), fill=C((200, 196, 186)))
    d.line((ta + 10, tt - 1, ta + 4, tt - 12), fill=C((170, 170, 176)))   # 兔耳天线
    d.line((ta + 12, tt - 1, ta + 20, tt - 11), fill=C((170, 170, 176)))
    rect(d, ta + 9, tt - 2, ta + 13, tt - 1, (60, 60, 64))
    # 一瓶塑料花
    fx = w - 7
    rect(d, fx - 2, ct - 8, fx + 2, ct - 2, (70, 120, 170))
    px(d, fx - 2, ct - 7, (130, 170, 210))
    for (ox, oy, col) in ((-3, -12, (230, 70, 90)), (0, -14, (250, 200, 60)), (3, -11, (230, 70, 90)), (1, -10, (240, 240, 230))):
        vl(d, fx + ox // 2, ct - 9, ct + oy + 2, (80, 140, 70))
        px(d, fx + ox, ct + oy, col)
        px(d, fx + ox + 1, ct + oy, col)
        px(d, fx + ox, ct + oy + 1, dk(col, 0.8))
    return im


def plant_img(w, h):
    """一盆橡皮树：陶盆 + 几片大叶子（深绿、叶脉亮）。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    pa, pb = 3, w - 4
    for y in range(h - 9, h):
        u = (y - (h - 9)) / 8.0
        a, b = int(round(pa + u * 2)), int(round(pb - u * 2))
        hl(d, a, b, y, (184, 100, 66) if y > h - 8 else (214, 130, 90))
        px(d, a, y, (214, 130, 90))
        px(d, b, y, (140, 70, 46))
    vl(d, w // 2, 8, h - 9, (110, 90, 60))
    for i, (lx, ly, sgn) in enumerate(((w // 2, 6, -1), (w // 2, 12, 1), (w // 2, 18, -1), (w // 2, 24, 1),
                                       (w // 2, 30, -1), (w // 2, 2, 1))):
        for k in range(7):
            x = lx + sgn * (1 + k)
            y = ly + int(round(math.sin(k / 6.0 * math.pi) * -2)) + k // 3
            c = (48, 100, 56) if k < 6 else (36, 80, 44)
            px(d, x, y, c)
            px(d, x, y + 1, (40, 86, 48))
            if k in (2, 4):
                px(d, x, y - 1, (70, 130, 76))
    return im


def curtain_img(w, h, dmg=False):
    """落地窗 + 两幅酒红窗帘：帘头（褶皱 + 金流苏）、铜帘杆、两幅帘子到地（竖褶、暗纹、底边金穗），
    中间露出关着的百叶窗、缝里透光。局部坐标，太阳在左（整件会翻：朝灯那边亮）。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    w0, w1, w2, w3 = WINE
    # 中间的窗（关着的绿百叶，一条条缝里是白光）
    gx0, gx1 = 12, w - 12
    rect(d, gx0, 8, gx1, h - 26, (60, 90, 70))
    for y in range(9, h - 26, 2):
        hl(d, gx0 + 1, gx1 - 1, y, (250, 238, 196) if y % 4 == 1 else (80, 116, 90))
    vl(d, (gx0 + gx1) // 2, 8, h - 26, (40, 60, 48))
    hl(d, gx0 - 1, gx1 + 1, h - 25, (226, 220, 206))                # 窗台
    # 铜帘杆 + 两头的球
    hl(d, 0, w - 1, 3, BRASS[2])
    hl(d, 0, w - 1, 4, BRASS[0])
    d.ellipse((-1, 1, 2, 5), fill=C(BRASS[2]))
    d.ellipse((w - 3, 1, w, 5), fill=C(BRASS[2]))
    # 两幅帘子
    for (a, b) in ((1, 13), (w - 14, w - 2)):
        for x in range(a, b + 1):
            k = (x - a) % 4
            c = w1 if k in (1, 2) else (w0 if k == 0 else w2)
            for y in range(6, h - 1):
                cc = c
                if (y // 3 + x) % 5 == 0 and k != 3:
                    cc = dk(c, 0.9)                                # 暗纹
                px(d, x, y, cc)
        for x in range(a, b + 1, 2):                               # 底边的金穗
            px(d, x, h - 2, GOLD[1])
            px(d, x, h - 1, GOLD[2])
        vl(d, a, 6, h - 2, w0)
        vl(d, b, 6, h - 2, w3)
    # 帘头（横着一段，下沿一排小三角 + 金流苏）
    rect(d, 0, 5, w - 1, 10, w1)
    hl(d, 0, w - 1, 5, w0)
    for x in range(0, w, 4):
        for k in range(3):
            hl(d, x + k, x + 3 - k, 11 + k, w2 if k < 2 else w3)
        px(d, x + 1, 14, GOLD[1])
        px(d, x + 1, 15, GOLD[2])
    for y in range(6, 10, 2):
        hl(d, 0, w - 1, y, dk(w1, 0.9))
    if dmg:
        for (x0, y0, L) in ((3, 40, 14), (w - 12, 52, 12)):        # 帘子被砍开的两道口子（里面露出黑的窗洞 + 布丝）
            for k in range(L):
                xx, yy = x0 + k // 2, y0 + k
                if 0 <= xx < w:
                    px(d, xx, yy, (26, 22, 24))
                    px(d, xx + 1, yy, (50, 36, 40))
                    if k % 3 == 0:
                        px(d, xx - 1, yy, lt(w0, 0.3))
        hl(d, 0, 6, 3, (90, 70, 40))                               # 帘杆被砍歪了一截
        px(d, 7, 4, BRASS[2])
        chips(d, w, h, 6, w0, seed=3)
    return im


def bed_img(w, h, dmg=False):
    """木床（侧面，床头在左）：实木的床头板（拱形顶 + 雕花椭圆 + 两根柱子到地）、矮一点的床尾板、两个镶花边的白枕头、
    花床罩从床垫上垂下来盖住床框（下沿一排波浪穗）、床尾叠着一条毯子；床罩下面、床腿之间一道 9 px 的黑缝（床底躲得进小孩）。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = WALNUT
    mt, rail, drape = 18, 27, 31                                    # 床垫顶、床框、床罩下沿
    fa = w - 7                                                      # 床尾板左沿
    # 床底的黑缝（先画，床腿盖在上面）
    rect(d, 6, drape + 1, fa, h - 2, (36, 28, 28))
    for x in range(8, fa, 6):
        px(d, x, h - 3, (66, 54, 48))                              # 床底一点灰尘
    # 床头板：拱形顶的实木板（左亮右暗）+ 雕花椭圆 + 两根柱子
    for x in range(0, 9):
        u = (x - 4) / 4.5
        t = 3 + int(round(3 * u * u))
        for y in range(t, rail + 3):
            c = md if 1 < x < 7 else (hi if x <= 1 else sh)
            px(d, x, y, c)
        px(d, x, t - 1, hi if x < 5 else md)
    d.ellipse((2, 7, 6, 13), outline=C(GOLD[2]))
    px(d, 4, 10, GOLD[1])
    for x in (0, 8):
        rect(d, x, 0, x + 1, h - 1, md if x == 0 else sh)
        px(d, x, 0, GOLD[1])
        px(d, x + 1, 0, GOLD[2])
    # 床尾板：矮的实木板 + 两根柱子
    for x in range(fa, w):
        for y in range(mt - 6, drape + 1):
            px(d, x, y, md if fa < x < w - 1 else (hi if x == fa else kk))
    hl(d, fa, w - 1, mt - 6, hi)
    for x in (fa, w - 2):
        rect(d, x, mt - 8, x + 1, h - 1, md)
        px(d, x, mt - 8, GOLD[1])
    hl(d, fa + 1, w - 2, mt, sh)
    # 床垫 + 两个白枕头（镶一道花边）
    rect(d, 9, mt, fa - 1, rail, (236, 232, 222))
    hl(d, 9, fa - 1, mt, (250, 248, 240))
    for x in (10, 19):
        d.ellipse((x, mt - 5, x + 9, mt + 1), fill=C((246, 244, 236)))
        hl(d, x + 2, x + 7, mt - 5, (255, 255, 252))
        for k in range(0, 10, 2):
            px(d, x + k, mt + 1, (220, 200, 200))
    # 花床罩：盖到床尾、从床沿垂下来（红底 + 白 / 金小花），下沿一排波浪穗
    for x in range(26, fa):
        for y in range(mt - 2, drape + 1):
            c = (176, 60, 70)
            if (x + y * 3) % 7 == 0:
                c = (240, 220, 200)
            elif (x * 2 + y) % 11 == 0:
                c = (220, 170, 70)
            if y == mt - 2:
                c = lt(c, 0.2)
            elif y == rail:
                c = dk(c, 0.82)                                    # 床沿的折
            px(d, x, y, c)
    for x in range(9, 26):                                         # 枕头下面那截：白床单垂下来
        for y in range(rail, drape + 1):
            px(d, x, y, (226, 222, 212) if y < drape else (200, 196, 186))
    for x in range(26, fa, 3):                                     # 波浪穗
        px(d, x + 1, drape + 1, (220, 180, 90))
        px(d, x, drape, (150, 44, 54))
    # 床尾叠着的一条毯子（条纹）
    for y in range(mt - 4, mt + 1):
        for x in range(fa - 12, fa - 1):
            c = ((70, 100, 150), (230, 220, 200), (200, 120, 60))[(y + x // 4) % 3]
            if y == mt - 4:
                c = lt(c, 0.2)
            px(d, x, y, c)
    # 床腿（床罩下面露出来一截）
    for x in (9, w // 2, fa - 2):
        rect(d, x, drape + 1, x + 1, h - 1, sh)
        px(d, x, drape + 1, md)
    if dmg:
        axe_marks(d, [(fa, mt - 4, 6, 1), (2, 14, 6, 1)], md)
        for y in range(rail - 2, drape + 1):                        # 床罩被劈开一道口子（露出黑的床底）
            for x in range(36 + (y - rail) // 2, 42 + (y - rail) // 3):
                px(d, x, y, (40, 30, 30))
        for i in range(12):                                        # 棉絮 / 羽毛飞出来
            x = int(hrange(30, fa - 4, i, 1331))
            y = int(hrange(mt - 3, rail + 2, i, 1332))
            px(d, x, y, (252, 252, 250))
            if i % 3 == 0:
                px(d, x + 1, y - 1, (236, 236, 230))
    return im


def crate_img(w, h, dmg=False):
    """大木箱：木板（横缝）+ 斜撑 + 四角铁皮、两只绳把手、喷的黑字；上面叠着一条条纹毯子。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = PINE
    top = 6
    rect(d, 0, top, w - 1, h - 1, md)
    for y in range(top + 5, h - 1, 5):
        hl(d, 0, w - 1, y, sh)
        hl(d, 0, w - 1, y - 1, lt(md, 0.08))
    d.line((2, h - 3, w - 3, top + 2), fill=C(hi))                 # 斜撑
    d.line((2, h - 2, w - 3, top + 3), fill=C(sh))
    for x in (0, w - 3):                                           # 竖档
        rect(d, x, top, x + 2, h - 1, hi if x == 0 else sh)
    hl(d, 0, w - 1, top, hi)
    vl(d, w - 1, top, h - 1, kk)
    hl(d, 0, w - 1, h - 1, kk)
    for (x, y) in ((1, top + 1), (w - 3, top + 1), (1, h - 3), (w - 3, h - 3)):   # 四角铁皮
        rect(d, x, y, x + 1, y + 1, IRON_HI)
    for (x, y) in ((6, top + 8), (w - 10, top + 8)):              # 绳把手
        d.arc((x - 2, y - 1, x + 3, y + 3), 0, 180, fill=C((210, 190, 140)))
    P.sign_ar(d, 6, top + 12, w - 7, top + 18, None, (50, 44, 40), seed=41, dots=False)
    # 上面叠着的毯子（条纹，垂下来一角）
    for y in range(0, top + 1):
        for x in range(2, w - 4):
            c = ((200, 80, 60), (240, 220, 180), (60, 90, 140))[(x // 3) % 3]
            if y == 0:
                c = lt(c, 0.2)
            px(d, x, y, c)
    for y in range(top + 1, top + 6):
        for x in range(w - 8, w - 4):
            px(d, x, y, ((200, 80, 60), (240, 220, 180), (60, 90, 140))[(x // 3) % 3])
    if dmg:
        for y in range(top + 9, top + 16):                          # 一块木板被劈开（黑的缺口 + 两边木茬）
            for x in range(10 + (y - top - 9) // 2, 18 + (y - top - 9) // 3):
                px(d, x, y, (30, 22, 18))
        axe_marks(d, [(8, top + 8, 10, 1), (w - 14, h - 9, 6, -1)], md)
        chips(d, w, h, 8, hi, seed=7)
    return im


def cupboard_img(w, h, dmg=False):
    """碗柜：上半截两扇纱门（里面摆着盘子、茶杯）、中间台面（一把铝水壶、一个糖罐）、下半截两扇木门（躲得进小孩）、顶上一道冠线。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = PINE
    top = 4
    hl(d, 0, w - 1, top - 2, hi)
    hl(d, 0, w - 1, top - 1, md)
    rect(d, 1, top, w - 2, h - 3, md)
    vl(d, 1, top, h - 3, hi)
    vl(d, w - 2, top, h - 3, kk)
    ua, ub = top + 2, top + 18                                     # 上半截：纱门
    rect(d, 3, ua, w - 4, ub, (80, 64, 56))
    for (y, n) in ((ua + 6, 4), (ua + 13, 5)):                     # 两层隔板：盘子立着、茶杯一排
        hl(d, 3, w - 4, y + 1, sh)
        for k in range(n):
            x = 5 + k * ((w - 10) // n)
            if y == ua + 6:
                d.ellipse((x, y - 5, x + 5, y), fill=C((236, 236, 228)))
                d.ellipse((x + 1, y - 4, x + 4, y - 1), outline=C((80, 120, 180)))
            else:
                rect(d, x, y - 3, x + 2, y, (236, 236, 228))
                px(d, x + 3, y - 2, (236, 236, 228))
    for y in range(ua, ub + 1):                                    # 纱网（细点）
        for x in range(3, w - 3):
            if (x + y) % 2 == 0 and hash01(x, y, 1341) < 0.35:
                px(d, x, y, (150, 140, 130))
    vl(d, w // 2, ua, ub, sh)
    for (a, b) in ((3, w // 2 - 1), (w // 2 + 1, w - 4)):
        rect(d, a, ua, b, ub, None, outline=hi)
    ct = ub + 2                                                    # 台面
    hl(d, 0, w - 1, ct, hi)
    hl(d, 0, w - 1, ct + 1, sh)
    kx = 9                                                         # 铝水壶
    d.ellipse((kx - 4, ct - 8, kx + 4, ct - 1), fill=C((190, 192, 196)))
    px(d, kx - 2, ct - 7, (236, 238, 240))
    hl(d, kx + 4, kx + 7, ct - 5, (190, 192, 196))
    d.arc((kx - 3, ct - 11, kx + 3, ct - 5), 180, 360, fill=C((90, 90, 96)))
    rect(d, w - 12, ct - 6, w - 7, ct - 1, (236, 232, 222))         # 糖罐
    hl(d, w - 12, w - 7, ct - 6, (200, 60, 60))
    la = ct + 3                                                    # 下半截：两扇木门（门板 + 凹框 + 拉手）
    for (a, b) in ((3, w // 2 - 1), (w // 2 + 1, w - 4)):
        rect(d, a, la, b, h - 6, md)
        rect(d, a + 2, la + 2, b - 2, h - 8, sh)
        rect(d, a + 3, la + 3, b - 3, h - 9, md)
        px(d, b - 2 if a < w // 2 else a + 2, (la + h) // 2, GOLD[1])
    for x in (2, w - 4):
        rect(d, x, h - 2, x + 1, h - 1, kk)
    if dmg:
        axe_marks(d, [(w // 2 + 2, la + 4, 8, 1), (5, la + 10, 7, -1)], md)
        for k in range(4):                                         # 一只盘子碎了（碎片掉在台面上）
            px(d, 12 + k * 3, ct - 1, (236, 236, 228))
            px(d, 13 + k * 3, ct - 2, (80, 120, 180))
        d.ellipse((w // 2 + 3, ua + 1, w // 2 + 8, ua + 6), fill=C((80, 64, 56)))   # 上面空了一个盘子的位置
        chips(d, w, h, 8, hi, seed=9)
    return im


def door_frame_img(w, h):
    """两间房之间的门框：木框（左右门柱 + 门楣）、里面暗的过道（远处一点墙）、开着的门扇贴在卧室那边（侧面一窄条）。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = WALNUT
    rect(d, 3, 4, w - 4, h - 1, (54, 44, 42))
    for y in range(4, h, 3):
        hl(d, 3, w - 4, y, (60, 50, 48))
    rect(d, 7, 14, w - 8, h - 6, (72, 62, 58))                       # 过道尽头的墙（一点点亮）
    hl(d, 3, w - 4, h - 2, (90, 78, 70))
    for x in (0, w - 3):                                           # 门柱
        rect(d, x, 0, x + 2, h - 1, md)
        vl(d, x, 0, h - 1, hi)
        vl(d, x + 2, 0, h - 1, sh)
    rect(d, 0, 0, w - 1, 3, md)                                     # 门楣
    hl(d, 0, w - 1, 0, hi)
    hl(d, 0, w - 1, 3, kk)
    return im


def window_img(w, h, tied=False):
    """卧室的窗（百叶半关：上面几条缝透光、下面关死）+ 窗台；tied = 旁边一幅扎起来的窗帘。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    rect(d, 0, 0, w - 1, h - 1, (226, 220, 206))                    # 窗套
    rect(d, 2, 2, w - 3, h - 6, (50, 70, 58))
    for y in range(3, h - 6, 2):
        bright = y < h // 2
        hl(d, 3, w - 4, y, (252, 240, 200) if (bright and y % 4 == 3) else (78, 112, 88))
    vl(d, w // 2, 2, h - 6, (40, 56, 46))
    hl(d, 0, w - 1, h - 5, (240, 236, 224))                         # 窗台
    hl(d, 0, w - 1, h - 4, (190, 182, 168))
    if tied:
        for y in range(0, h + 6):
            x = w - 2 + (2 if y > h // 2 else 0) - abs(y - h // 2) // 6
            px(d, x, y, WINE[1])
            px(d, x + 1, y, WINE[2])
    return im


def basil_pot(d, x, y):
    rect(d, x - 3, y - 4, x + 3, y, (184, 100, 66))
    hl(d, x - 3, x + 3, y - 4, (214, 130, 90))
    for k in range(9):
        px(d, x - 3 + k % 7, y - 5 - k // 3 - (k % 2), (70, 130, 70) if k % 2 else (100, 160, 80))


def nightstand(d, x0, base):
    """床头柜（一个抽屉 + 一扇门）+ 上面的小台灯（布罩）、闹钟、一杯水。"""
    hi, md, sh, kk = WALNUT
    top = base - 18
    rect(d, x0, top, x0 + 17, base - 2, md)
    hl(d, x0, x0 + 17, top, hi)
    vl(d, x0, top, base - 2, hi)
    vl(d, x0 + 17, top, base - 2, kk)
    hl(d, x0 + 2, x0 + 15, top + 5, kk)
    px(d, x0 + 8, top + 3, GOLD[1])
    rect(d, x0 + 2, top + 7, x0 + 15, base - 4, sh)
    px(d, x0 + 13, top + 11, GOLD[1])
    for x in (x0 + 1, x0 + 15):
        rect(d, x, base - 1, x + 1, base, kk)
    lx = x0 + 5                                                    # 台灯
    vl(d, lx, top - 6, top - 1, BRASS[1])
    hl(d, lx - 2, lx + 2, top - 1, BRASS[0])
    for k in range(5):
        hl(d, lx - 2 - k // 2, lx + 2 + k // 2, top - 11 + k, (230, 200, 150) if k < 4 else (200, 170, 120))
    d.ellipse((x0 + 10, top - 5, x0 + 14, top - 1), fill=C((200, 60, 60)))   # 闹钟
    px(d, x0 + 12, top - 3, (250, 250, 240))
    px(d, x0 + 10, top - 6, (200, 60, 60))
    px(d, x0 + 14, top - 6, (200, 60, 60))
    rect(d, x0 + 15, top - 4, x0 + 16, top - 1, (190, 220, 226))      # 一杯水


# ============================================================ 墙上的东西
def draw_wall_decor(im):
    d = ImageDraw.Draw(im)
    # 客厅大门（木门、门缝下一道光、门边一个挂钩挂着一把伞）
    da, db = 6, 30
    rect(d, da - 3, 96, db + 2, LANE - 1, WALNUT[1])
    vl(d, da - 3, 96, LANE - 1, WALNUT[0])
    P.door(im, da, LANE - 1, db - da, 46, (120, 80, 50), frame=None, arch=False, studs=False, seed=1301, sill=False)
    d = ImageDraw.Draw(im)
    hl(d, da, db - 1, LANE - 2, (250, 230, 170))                    # 门缝下的光
    rect(d, da - 3, 82, db + 2, 94, WALNUT[1])                      # 门上的气窗（木格子，透光）
    rect(d, da - 1, 84, db, 92, (240, 226, 180))
    for x in range(da, db, 4):
        vl(d, x, 84, 92, WALNUT[2])
    hl(d, da - 1, db, 88, WALNUT[2])
    # 沙发上面的盘子架：一道木搁板 + 五只立着的蓝白瓷盘
    hl(d, 84, 132, 56, WALNUT[0])
    hl(d, 84, 132, 57, WALNUT[2])
    for k in range(5):
        P.plate(d, 89 + k * 10, 52, 3, ((60, 100, 170), (190, 60, 60), (60, 140, 120), (60, 100, 170), (200, 150, 50))[k])
    # 电视上面：两张小相框（全家福）
    for (fx, fy, col) in ((180, 62, (120, 100, 90)), (206, 60, (90, 110, 120))):
        rect(d, fx, fy, fx + 8, fy + 10, GOLD[2])
        rect(d, fx + 1, fy + 1, fx + 7, fy + 9, (220, 214, 200))
        for k in range(3):
            px(d, fx + 2 + k * 2, fy + 4, (150, 120, 100))
            vl(d, fx + 2 + k * 2, fy + 5, fy + 8, col)
    # 尼罗河帆船的油画（沙发上面）
    fx0, fy0, fx1, fy1 = 92, 66, 124, 88
    rect(d, fx0, fy0, fx1, fy1, GOLD[1])
    rect(d, fx0 + 2, fy0 + 2, fx1 - 2, fy1 - 2, (120, 170, 200))
    for y in range(fy0 + 2, fy0 + 9):
        hl(d, fx0 + 2, fx1 - 2, y, mix((246, 200, 140), (120, 170, 200), (y - fy0 - 2) / 7.0))
    rect(d, fx0 + 2, fy0 + 13, fx1 - 2, fy1 - 2, (60, 120, 160))
    hl(d, fx0 + 2, fx1 - 2, fy0 + 13, (190, 220, 230))
    rect(d, fx0 + 2, fy0 + 10, fx1 - 2, fy0 + 12, (110, 140, 80))  # 对岸
    paste(im, P.felucca_img(12, 10, seed=1), fx0 + 10, fy0 + 3)
    d = ImageDraw.Draw(im)
    hl(d, fx0, fx1, fy0, GOLD[0])
    vl(d, fx1, fy0, fy1, GOLD[2])
    hl(d, fx0, fx1, fy1, GOLD[3])
    # 书法框（鱼缸上面）
    bx0, by0, bx1, by1 = 228, 62, 270, 76
    rect(d, bx0, by0, bx1, by1, (60, 40, 30))
    rect(d, bx0 + 2, by0 + 2, bx1 - 2, by1 - 2, (30, 70, 50))
    P.sign_ar(d, bx0 + 2, by0 + 2, bx1 - 2, by1 - 2, None, (226, 190, 90), seed=1303, rows=1)
    # 挂钟（电视上面：圆钟面 + 木壳 + 下面钟摆的盒子，钟摆在 strip）
    cx, cy = CLOCK
    rect(d, cx - 5, cy - 6, cx + 5, cy + 20, WALNUT[1])
    vl(d, cx - 5, cy - 6, cy + 20, WALNUT[0])
    vl(d, cx + 5, cy - 6, cy + 20, WALNUT[3])
    d.ellipse((cx - 4, cy - 5, cx + 4, cy + 3), fill=C((240, 236, 224)))
    vl(d, cx, cy - 3, cy - 1, (30, 30, 30))
    hl(d, cx, cx + 2, cy - 1, (30, 30, 30))
    rect(d, cx - 3, cy + 5, cx + 3, cy + 18, (60, 46, 36))
    # 卧室：结婚照（金框、黑白照片：两个人）+ 搁板（香水瓶、梳子）+ 一面小镜子
    wx0, wy0 = 460, 62
    rect(d, wx0, wy0, wx0 + 20, wy0 + 16, GOLD[1])
    rect(d, wx0 + 2, wy0 + 2, wx0 + 18, wy0 + 14, (200, 196, 186))
    for (px0, col) in ((wx0 + 6, (70, 70, 70)), (wx0 + 12, (236, 236, 232))):
        d.ellipse((px0 - 2, wy0 + 4, px0 + 1, wy0 + 7), fill=C((150, 140, 130)))
        rect(d, px0 - 2, wy0 + 8, px0 + 1, wy0 + 14, col)
    sx0 = 530
    hl(d, sx0, sx0 + 20, 90, WALNUT[0])
    hl(d, sx0, sx0 + 20, 91, WALNUT[2])
    for k, col in enumerate(((200, 120, 160), (120, 180, 200), (230, 190, 90))):
        rect(d, sx0 + 2 + k * 5, 85, sx0 + 4 + k * 5, 89, col)
        px(d, sx0 + 3 + k * 5, 84, (220, 220, 220))
    hl(d, sx0 + 17, sx0 + 20, 89, (60, 50, 50))
    d.ellipse((534, 60, 546, 78), fill=C(GOLD[2]))
    d.ellipse((535, 61, 545, 77), fill=C((160, 176, 182)))
    for k in range(4):
        px(d, 537 + k // 2, 63 + k, (214, 228, 232))
    # 卧室日历
    rect(d, 592, 118 - 26, 598, 118 - 16, (236, 232, 222))
    hl(d, 592, 598, 92, (200, 50, 50))
    # 木箱上面的墙上挂着一块礼拜毯（深红底、米色边、中间一个尖拱的壁龛图案、下沿流苏）
    ra, rb, rt, rbm = 494, 520, 64, 104
    for y in range(rt, rbm):
        for x in range(ra, rb):
            c = (150, 40, 50)
            edge = min(x - ra, rb - 1 - x, y - rt, rbm - 1 - y)
            if edge == 0:
                c = (90, 30, 36)
            elif edge in (1, 2):
                c = (220, 196, 150) if (x + y) % 3 else (60, 110, 90)
            else:
                cx = (ra + rb - 1) / 2.0
                arch = rt + 10 + abs(x - cx) * 0.9
                if y > arch and abs(x - cx) < 8:
                    c = (60, 110, 90) if y > arch + 2 else (220, 196, 150)
            px(d, x, y, c)
    for x in range(ra, rb, 2):
        px(d, x, rbm, (220, 210, 180))
    vl(d, (ra + rb) // 2, rt - 3, rt - 1, IRON)                     # 挂钉
    # 梳妆台（结婚照下面）：三个抽屉 + 一面能翻的镜子 + 两瓶香水
    ta, tb = 456, 486
    hi, md, sh, kk = WALNUT
    rect(d, ta, 122, tb, LANE - 3, md)
    hl(d, ta, tb, 122, hi)
    vl(d, ta, 122, LANE - 3, hi)
    vl(d, tb, 122, LANE - 3, kk)
    for y in (128, 134):
        hl(d, ta + 2, tb - 2, y, kk)
        px(d, (ta + tb) // 2, y - 3, GOLD[1])
    for x in (ta + 1, tb - 2):
        rect(d, x, LANE - 2, x + 1, LANE - 1, kk)
    for x in (ta + 4, tb - 4):                                     # 镜架
        vl(d, x, 100, 121, md)
    d.ellipse((ta + 6, 98, tb - 6, 120), fill=C(GOLD[2]))
    d.ellipse((ta + 7, 99, tb - 7, 119), fill=C((156, 172, 178)))
    for k in range(5):
        px(d, ta + 10 + k // 2, 102 + k, (210, 224, 228))
    for (bx_, col) in ((ta + 3, (200, 120, 160)), (tb - 6, (120, 180, 200))):
        rect(d, bx_, 117, bx_ + 2, 121, col)
        px(d, bx_ + 1, 116, (220, 220, 220))


CLOCK = (196, 52)              # 挂钟钟面中心


def place(im, sprite, x0, y0, flip):
    """把局部坐标画好的家具贴进房间；flip = 在灯左边（翻过来，朝灯的一面亮）。"""
    if flip:
        sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
    paste(im, sprite, x0, y0)


def furniture_sprites(dmg=False):
    """(名字, 局部图, x0, y0, 翻?)；dmg = 画砍过的样子（只用来做 pick 的痕迹图）。"""
    out = []
    bx = HIDES['curtain'][1]
    out.append(('curtain', curtain_img(bx[2] - bx[0], bx[3] - bx[1], dmg), bx[0], bx[1], side_of(bx[0])))
    bx = HIDES['wardrobe'][1]
    out.append(('wardrobe', wardrobe_img(bx[2] - bx[0], bx[3] - bx[1], dmg), bx[0], bx[1], side_of(bx[0])))
    bx = HIDES['aquarium'][1]
    out.append(('aquarium', aquarium_img(bx[2] - bx[0], bx[3] - bx[1], dmg), bx[0], bx[1], side_of(bx[0])))
    bx = HIDES['bed'][1]
    out.append(('bed', bed_img(bx[2] - bx[0], bx[3] - bx[1], dmg), bx[0], bx[1], side_of(bx[0])))
    bx = HIDES['crate'][1]
    out.append(('crate', crate_img(bx[2] - bx[0], bx[3] - bx[1], dmg), bx[0], bx[1], side_of(bx[0])))
    bx = HIDES['cupboard'][1]
    out.append(('cupboard', cupboard_img(bx[2] - bx[0], bx[3] - bx[1], dmg), bx[0], bx[1], side_of(bx[0])))
    return out


def draw_furniture(im):
    # 非藏身点的家具
    place(im, sofa_img(54, 30), 80, LANE - 30, True)
    place(im, tv_corner_img(44, 56), 176, LANE - 56, True)
    place(im, plant_img(16, 40), 278, LANE - 40, True)
    place(im, door_frame_img(24, 50), DIVIDE - 12, LANE - 50, False)
    win = window_img(30, 46)
    place(im, win, 342, 54, False)
    d = ImageDraw.Draw(im)
    basil_pot(d, 352, 95)
    nightstand(d, 340, LANE - 1)
    place(im, window_img(28, 52, tied=True), 602, 50, False)
    # 门扇（开着，贴在卧室那边的墙上：一窄条侧面 + 一点门板）
    d = ImageDraw.Draw(im)
    rect(d, DIVIDE + 13, 98, DIVIDE + 16, LANE - 2, WALNUT[1])
    vl(d, DIVIDE + 13, 98, LANE - 2, WALNUT[0])
    vl(d, DIVIDE + 16, 98, LANE - 2, WALNUT[3])
    px(d, DIVIDE + 15, 124, GOLD[1])
    # 六个藏身点
    for (name, spr, x0, y0, flip) in furniture_sprites(False):
        place(im, spr, x0, y0, flip)


def draw_lamp(im):
    """吊灯：天花板上一个圆托 → 一根长线 → 乳白玻璃钟形罩 → 灯泡（亮）。灯的光晕在 light_pass 里一起算。"""
    d = ImageDraw.Draw(im)
    x, y = LAMP
    rect(d, x - 3, CEIL + 1, x + 3, CEIL + 2, (200, 196, 186))
    vl(d, x, CEIL + 3, y - 10, (60, 56, 54))
    for k in range(8):                                             # 灯罩（上窄下宽）
        hw = 2 + k
        hl(d, x - hw, x + hw, y - 9 + k, (250, 244, 226) if k < 6 else (236, 226, 200))
        px(d, x - hw, y - 9 + k, (255, 252, 240))
        px(d, x + hw, y - 9 + k, (214, 204, 182))
    hl(d, x - 9, x + 9, y - 1, (226, 214, 188))
    d.ellipse((x - 2, y - 2, x + 2, y + 1), fill=C(LAMP_C))          # 灯泡
    px(d, x, y + 1, (255, 255, 236))


# ============================================================ 打光（以吊灯为中心一圈圈分档 + 家具影子 + 窗缝光斑）
LIGHT_BANDS = [(30, 1.08), (60, 1.04), (95, 1.0), (135, 0.95), (180, 0.9), (230, 0.85), (9999, 0.8)]   # (半径上限, 亮度倍数)


def light_pass(im):
    a = np.array(im).astype(np.float32)
    bay = A._bayer(PW, H)
    ys, xs = np.mgrid[0:H, 0:PW].astype(np.float32)
    r = np.hypot(xs - LAMP[0], (ys - LAMP[1]) * 1.25)
    k = np.zeros((H, PW), np.float32)
    prev_r, prev_k = 0.0, LIGHT_BANDS[0][1]
    for i, (rr, kk) in enumerate(LIGHT_BANDS):
        m = (r >= prev_r) & (r < rr)
        k[m] = kk
        prev_r = rr
    # 分档的边用 Bayer 抖开 6 px（像素画的光圈）
    for i in range(len(LIGHT_BANDS) - 1):
        rr, k_in = LIGHT_BANDS[i]
        k_out = LIGHT_BANDS[i + 1][1]
        band = (r >= rr - 3) & (r < rr + 3)
        u = (r - (rr - 3)) / 6.0
        k[band] = np.where(bay[band] < u[band], k_out, k_in)
    # 地面（可走带）只吃很淡的一层（人站上去要看得清，可走带要平）
    floor = ys >= LANE
    k[floor] = 0.96 + (k[floor] - 0.8) * 0.14
    a[..., :3] *= k[..., None]
    im2 = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    im.paste(im2)


def furniture_shadows(im):
    """家具挡住灯光：墙上离灯那一侧一道影（宽 3–6，离灯越远越宽）+ 墙脚 / 地上两行接触影。"""
    for (name, bx) in [(k, v[1]) for k, v in HIDES.items()] + [('sofa', [80, LANE - 30, 134, LANE]),
                                                               ('tv', [176, LANE - 30, 220, LANE]),
                                                               ('plant', [278, LANE - 40, 294, LANE]),
                                                               ('night', [340, LANE - 18, 358, LANE]),
                                                               ('dresser', [456, 122, 487, LANE])]:
        x0, y0, x1, y1 = bx
        cx = (x0 + x1) / 2.0
        far = abs(cx - LAMP[0])
        wd = 3 + int(far / 80)
        if name == 'curtain':
            continue                                               # 窗帘本来就贴着墙
        if cx < LAMP[0]:
            pts = [(x0 - wd, y0 + 4), (x0, y0 + 2), (x0, y1 - 1), (x0 - wd, y1 - 1)]
        else:
            pts = [(x1, y0 + 2), (x1 + wd, y0 + 4), (x1 + wd, y1 - 1), (x1, y1 - 1)]
        cast_shadow(im, pts, mul=SOFT_MUL)
        # 地上的接触影：这张图的可走带从墙脚 y 146 就开始，影子压得很淡（和地面差 < 22），只是让家具“坐”在地上
        cast_shadow(im, [(x0, LANE), (x1, LANE), (x1 + (2 if cx >= LAMP[0] else -2), LANE + 1),
                         (x0 + (2 if cx >= LAMP[0] else -2), LANE + 1)], mul=FLOOR_SHADOW)


BEAMS = [(52, 64, 1), (606, 628, -1), (346, 368, -1)]   # 窗缝光落在地上的光斑：(窗 x0, x1, 往哪边斜)


def sun_patches(im):
    """窗缝里漏进来的日光，落在地上是几块淡淡的、一条条（百叶缝）的光斑。"""
    a = np.array(im).astype(np.float32)
    for (x0, x1, s) in BEAMS:
        for y in range(LANE + 2, 172):
            u = (y - LANE) / 26.0
            xa = int(round(x0 + s * u * 30))
            xb = int(round(x1 + s * u * 30))
            for x in range(min(xa, xb), max(xa, xb)):
                if 0 <= x < PW and (y // 2) % 2 == 0:
                    a[y, x, :3] = np.minimum(255, a[y, x, :3] * np.array((1.07, 1.06, 1.02)))
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def lamp_glow(im):
    """灯泡周围一圈暖光（只把墙 / 天花板往暖白里提一点，硬边分两档），灯罩下沿亮。"""
    a = np.array(im).astype(np.float32)
    x, y = LAMP
    ys, xs = np.mgrid[0:H, 0:PW].astype(np.float32)
    r = np.hypot(xs - x, (ys - y) * 1.2)
    for (rr, amt) in ((22, 0.16), (12, 0.14)):
        m = (r < rr) & (ys < LANE)
        a[m, :3] = a[m, :3] + (np.array(LAMP_C, np.float32) - a[m, :3]) * amt
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def finish(im):
    return A._grade(im, sat=0.94, val=1.0)


@lru_cache(maxsize=1)
def room_raw():
    """打光前的整张房间（axe 痕迹图要和它同一套打光 / 调色）。"""
    im = A._new(PW, H)
    draw_shell(im)
    draw_rug(im)
    draw_wall_decor(im)
    draw_furniture(im)
    draw_lamp(im)
    return im


def lit(im):
    im = im.copy()
    furniture_shadows(im)
    light_pass(im)
    sun_patches(im)
    lamp_glow(im)
    return finish(im)


@lru_cache(maxsize=1)
def room_img():
    return opaque(lit(room_raw()))


def floor_chips(im, name):
    """砍下来的东西掉在家具前面的地上（y 146–149，平的小碎块）：木屑 / 窗帘的布丝 / 鱼缸漏出来的一滩水 / 棉絮。"""
    d = ImageDraw.Draw(im)
    bx = HIDES[name][1]
    if name == 'aquarium':                                         # 一滩水（亮一点的蓝灰，扁扁的）
        cx = (bx[0] + bx[2]) // 2
        for y in range(LANE, LANE + 4):
            hw = 14 - (y - LANE) * 3
            for x in range(cx - hw, cx + hw + 1):
                if hash01(x, y, 1351) < 0.85:
                    px(d, x, y, (150, 180, 186) if (x + y) % 3 else (190, 214, 220))
        return
    col = {'curtain': WINE[1], 'bed': (250, 250, 246)}.get(name, PINE[0])
    for i in range(12):
        x = int(hrange(bx[0] + 2, bx[2] - 2, i, 1352, len(name)))
        y = LANE + int(hrange(0, 4, i, 1353, len(name)))
        px(d, x, y, col)
        if i % 3 == 0:
            px(d, x + 1, y, dk(col, 0.8))


@lru_cache(maxsize=1)
def axe_imgs():
    """六张砍痕图：在打光前的房间上画砍过的家具 → 一样打光调色 → 和没砍的比，只留变了的像素（其余透明）。"""
    base = np.array(room_img())
    out = {}
    for (name, spr, x0, y0, flip) in furniture_sprites(True):
        im = room_raw().copy()
        place(im, spr, x0, y0, flip)
        floor_chips(im, name)
        a = np.array(opaque(lit(im)))
        bx = HIDES[name][1]
        X0, Y0, X1, Y1 = bx[0] - 2, bx[1] - 2, bx[2] + 2, min(H, bx[3] + 4)
        sub_a, sub_b = a[Y0:Y1, X0:X1].copy(), base[Y0:Y1, X0:X1]
        diff = (sub_a[..., :3] != sub_b[..., :3]).any(-1)
        sub_a[~diff, 3] = 0
        sub_a[diff, 3] = 255
        out[name] = (Image.fromarray(sub_a, 'RGBA'), X0, Y0)
    return out


# ============================================================ strip
def fish_raw(f):
    """鱼缸：三条鱼来回游（4 帧往一边、4 帧往回）、气泡从气泵管往上冒、水草摆。画在世界坐标的透明整张上。"""
    im = A._new(PW, H)
    bx = HIDES['aquarium'][1]
    flip = side_of(bx[0])
    loc = A._new(bx[2] - bx[0], bx[3] - bx[1])
    d = ImageDraw.Draw(loc)
    tx0, ty0, tx1, ty1 = AQ_WATER
    # 水草（右边一丛、中间一丛）
    for (base_x, hgt, ph) in ((tx1 - 20, 16, 0.0), (tx0 + 18, 12, 1.7), (tx0 + 26, 18, 3.1)):
        for j in range(3):
            for k in range(hgt - j * 3):
                sw = int(round(math.sin(math.tau * f / N + ph + j + k * 0.25) * (k / float(hgt)) * 1.6))
                px(d, base_x + j * 2 + sw, ty1 - 4 - k, (60, 150, 80) if (k + j) % 3 else (90, 180, 100))
    # 气泡：一串从气泵管口往上冒
    bxp = tx1 - 13                                                 # 气泡在气泵管口旁边往上冒（贴着管子会看不见）
    for k in range(5):
        yy = ty1 - 6 - ((k * 6 + f * 3) % (ty1 - ty0 - 6))
        px(d, bxp + (k % 2), yy, (230, 248, 250))
        if k % 2 == 0:
            px(d, bxp + (k % 2) + 1, yy, (190, 230, 236))
    # 三条鱼：来回游（位置按帧走一个来回，n 帧闭合），转身时换方向
    fishes = [((240, 140, 40), (250, 200, 90), 6, 14, 2), ((70, 120, 200), (150, 190, 240), 30, 20, 5),
              ((240, 230, 220), (200, 60, 60), 20, 26, 3)]
    for i, (c1, c2, x0, y0, span) in enumerate(fishes):
        k = (f + i * 3) % N
        go = k < N // 2
        u = (k if go else N - k) / float(N // 2)
        x = int(round(x0 + span * 2 * u)) + tx0
        y = y0 + (1 if (k + i) % 4 < 2 else 0)
        face = 1 if go else -1
        # 鱼身 4 px + 尾巴 2 px + 眼睛
        for j in range(4):
            px(d, x + j * face, y, c1)
        px(d, x + face, y - 1, c1)
        px(d, x + 2 * face, y - 1, c2)
        px(d, x + face, y + 1, c2)
        px(d, x - face, y - 1, c2)
        px(d, x - face, y + 1, c2)
        px(d, x + 3 * face, y, (20, 20, 20))
    if flip:
        loc = loc.transpose(Image.FLIP_LEFT_RIGHT)
    paste(im, loc, bx[0], bx[1])
    return finish_strip(im)


def clock_raw(f):
    """挂钟的钟摆（左右摆，8 帧一个来回）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    cx, cy = CLOCK
    ang = math.sin(math.tau * f / N) * 0.35
    for j in range(2, 11):
        x = cx + int(round(math.sin(ang) * j))
        px(d, x, cy + 5 + j, (200, 170, 90))
    x = cx + int(round(math.sin(ang) * 11))
    d.ellipse((x - 2, cy + 15, x + 2, cy + 18), fill=C(GOLD[1]))
    px(d, x - 1, cy + 15, GOLD[0])
    return finish_strip(im)


FAN = (478, CEIL + 1)


def fan_raw(f):
    """卧室吊扇：一根短杆 + 电机罩 + 四片木扇叶（8 帧转 90°，正好闭合）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y = FAN
    vl(d, x, y, y + 6, (90, 86, 84))
    rect(d, x - 3, y + 7, x + 3, y + 9, (200, 196, 186))
    hl(d, x - 3, x + 3, y + 7, (236, 232, 222))
    ang0 = (math.pi / 2) * f / N
    for k in range(4):
        ang = ang0 + k * math.pi / 2
        for j in range(3, 16):
            xx = x + int(round(math.cos(ang) * j))
            yy = y + 9 + int(round(math.sin(ang) * j * 0.18))
            px(d, xx, yy, WALNUT[1] if j < 15 else WALNUT[2])
            if abs(math.cos(ang)) > 0.5:
                px(d, xx, yy + 1, WALNUT[2])
    return finish_strip(im)


def dust_raw(f):
    """窗缝光里飘的灰尘：几颗亮点沿着光的方向慢慢往下飘（各自的相位），n 帧闭合。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for bi, (x0, x1, s) in enumerate(BEAMS[:2]):
        for i in range(7):
            ph = (i / 7.0 + f / float(N)) % 1.0
            y = int(round(100 + ph * 40))
            x = int(round((x0 + x1) / 2.0 + (i - 3) * 3 + s * ph * 16))
            if (i + f) % 3:
                px(d, x, y, (250, 240, 210))
    return finish_strip(im)


def finish_strip(im):
    """strip 也要和房间同一套打光（离灯远的地方暗一点）+ 调色。"""
    a = np.array(im).astype(np.float32)
    ys, xs = np.mgrid[0:H, 0:PW].astype(np.float32)
    r = np.hypot(xs - LAMP[0], (ys - LAMP[1]) * 1.25)
    k = np.full((H, PW), LIGHT_BANDS[-1][1], np.float32)
    for (rr, kk) in reversed(LIGHT_BANDS):
        k[r < rr] = kk
    a[..., :3] *= k[..., None]
    return finish(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


fish_frame = cached(fish_raw)
clock_frame = cached(clock_raw)
fan_frame = cached(fan_raw)
dust_frame = cached(dust_raw)


@lru_cache(maxsize=1)
def strips():
    out = [('fish', P.auto_box(fish_frame, N, FPS), fish_frame),
           ('clock', P.auto_box(clock_frame, N, FPS), clock_frame),
           ('fan', P.auto_box(fan_frame, N, FPS), fan_frame)]
    for i, (x0, x1, s) in enumerate(BEAMS[:2]):
        out.append(('dust_%d' % i, P.auto_box(dust_frame, N, FPS, limit=(x0 - 30, 0, x1 + 30, H)), dust_frame))
    return out


AXE_ORDER = ('curtain', 'wardrobe', 'aquarium', 'bed', 'crate', 'cupboard')


@lru_cache(maxsize=1)
def table():
    tb = []
    rim, ry = P.crop_pano(room_img())
    tb.append(('pano', 'room', rim, 1.0, 0, ry))
    for (name, box, fn) in strips():
        tb.append(('strip', name, box, N, FPS, fn, 1.0))
    axes = axe_imgs()
    for name in AXE_ORDER:
        img, x0, y0 = axes[name]
        blank = A._new(img.width, img.height)
        tb.append(('pick', 'axe_' + name, [blank, img], (0, 1), x0, y0, 1.0))
    return tuple(tb)


def compose(camX, t=0.5, state=None):
    return P.compose(table(), camX, t, state)


def anchors():
    anc = {k: list(v) for k, v in ANCHORS.items()}
    anc.update(lamp_cord=[LAMP[0], CEIL + 1], floor_back=LANE)
    return anc


# ============================================================ 导出
def export(ex, BJ):
    tb = table()
    layers = P.export_layers(ex, BJ, tb)
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors())
    if ex.check_on:
        _checks(ex, BJ, st, tb)
    return st


def _checks(ex, BJ, st, tb):
    all_axe = {'axe_' + k: 1 for k in AXE_ORDER}
    cfg = dict(title='卢克索民宅', PW=PW, walk=WALK, near=room_img(), opaque_rows=(0, H), sky=room_img(),
               states=[{}, all_axe], stand=STAND, required=REQUIRED, size_limit=250 * 1024, cams_step=40,
               flat=(0, PW, WALK[0], WALK[1] + 1, 22, 0.012),
               flat_skip=[(76, 150, 232, 174)])
    P.common_checks(ex, BJ, st, tb, cfg)
    # 每个砍痕 pick 都真有东西、而且都落在自己的家具框附近（剧情闪红的框和斧痕对得上）
    for name in AXE_ORDER:
        img, x0, y0 = axe_imgs()[name]
        n = int((np.array(img)[..., 3] > 0).sum())
        bb = img.getchannel('A').getbbox()
        bx = HIDES[name][1]
        inside = bb is not None and bb[0] + x0 >= bx[0] - 3 and bb[2] + x0 <= bx[2] + 3 and bb[1] + y0 >= bx[1] - 3
        ex.checked('axe_%s 砍痕 %d px（≥ 20）、落在 hide_%s_box 里' % (name, n, name), 0 if (n >= 20 and inside) else 1)
    # 鱼缸“躲得进一个小孩”：水的范围 ≥ 小孩波鲁纳雷夫（13×18）
    tx0, ty0, tx1, ty1 = AQ_WATER
    ex.checked('鱼缸里水的范围 %d×%d ≥ 小孩 13×18' % (tx1 - tx0, ty1 - ty0), 0 if (tx1 - tx0 >= 13 and ty1 - ty0 >= 18) else 1)
    # 吊灯在 anchors.lamp：灯泡那一点比周围亮
    a = np.array(room_img()).astype(np.float32)
    lum = P._lum(a[..., :3])
    lx, ly = LAMP
    ex.checked('吊灯灯泡在 anchors.lamp（灯泡亮度 %.0f ≥ 220）' % lum[ly - 1, lx], 0 if lum[ly - 1, lx] >= 220 else 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch9', 'after')
    os.makedirs(od, exist_ok=True)
    full = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    for cx in (0, 320):
        full.paste(compose(cx, 0.5), (cx, 0))
    full.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'luxor_house_solo.png'))
    print('ok')
