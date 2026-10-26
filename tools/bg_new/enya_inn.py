# -*- coding: utf-8 -*-
r"""enya_inn —— 第5章「雾之镇」旅馆一楼大堂，夜里点着煤油灯（地图 inn_ch5：进旅馆 + 第 10 战「正义」）。
2026-10-18 ch5-town 组按体验版精度重画（改前是 ch5_scenes.inn()：一面平涂墙 + 方块门 / 柜台）。
老旧、体面、却静得发毛：墙纸是暗橄榄绿的大马士革花纹、下半截护墙板，煤油灯的暖光一团一团的，角落都是暗的；
门上的玻璃外面全是雾，门缝底下一缕缕雾钻进来。调色 / 画法零件在 ch5_town_parts.py。

320 单屏，ground 160，可走带 y 148–176（木地板 + 一块旧波斯地毯，压低了对比）；侧视平视，后墙 + 地板（地板从 y 146 起）。
竖向：天花板木板 + 两道梁 0–7，檐口线 8–11，墙纸 12–103，腰线 104–106，护墙板 107–138，踢脚板 139–145，地板 146–179。
从左到右（家具都靠后墙，正面最低到 y 147，不进可走带）：
  x 6–20     衣帽架（anchors.coat）：三脚木架、顶上挂着一顶礼帽和一件长大衣，脚边斜靠一把黑伞
  x 22–48    入口双开门（anchors.door）：门套、半圆气窗、两扇门上半截镶玻璃——外面是雾（strip 流动），门缝底下雾钻进来
  x 50–58    壁灯（玻璃灯罩 + 火苗 strip）
  x 58–137   去二楼的木楼梯（anchors.stairs = 楼梯脚）：12 级（每级 5×5）往右上到 y 81 的平台，平台后面是一道黑洞洞的拱门；
             靠我们这边一道扶手（底下的望柱、一根根栏杆、平台上的一截栏杆）；楼梯下面封着护墙板，
             里面一扇厕所门（anchors.wc_door，门上一块白搪瓷 WC 小牌）
  x 130–170  旧沙发（anchors.sofa / guest：荷尔·荷斯坐 / 站的地方）：驼峰靠背、拉扣、褪色的暗红丝绒、一个靠垫；
             上面一幅金框风景画（雪山 + 湖，夜里看是暗的）
  x 172–183  小圆几：烟灰缸里搁着一支没抽完的烟（烟 strip）、一只威士忌杯、一张叠好的报纸
  x 178      第二盏壁灯
  x 189–203  落地钟（anchors.clock = 钟面中心）：胡桃木钟壳、钟面、钟摆窗里的铜钟摆（strip 左右摆）
  x 206–238  壁炉：大理石炉框、壁炉台上一对烛台 / 一只花瓶 / 两个相框，炉膛里的火（strip）+ 柴架；
             壁炉上方一只鹿头标本（大角，木盾托；anchors.skull = 雾骷髅飘的位置就在鹿头前面）
  x 240–316  接待柜台（anchors.counter_box / counter）：木柜台（台面亮边、正面三块凹板）、台面上的铜铃（anchors.bell）、
             摊开的登记簿 + 墨水瓶和羽毛笔、一盏煤油灯（火苗 strip）；后墙一排信格 + 钥匙板（两排钥匙 + 铜牌，anchors.keys）
  天花板     中间一盏黄铜吊灯（五个玻璃灯罩，strip 轻轻晃 + 火苗跳）
光：夜里，整体压暗（偏冷的环境光）；吊灯 / 壁灯 / 柜台的煤油灯 / 壁炉各打一团暖光（分档 + 抖动，直接烘进底图），
门上的玻璃透进一点冷的雾光。灯罩、火苗、门外的雾是“自己发光”的，压暗以后才画。可走带后面（y 108–147）收了 12 % 对比。

图层（从后往前）：
  room       static          整张底图（不透明，夜里的打光烘在里面）
  doorfog    strip  8 帧 @4 fps   门玻璃 / 气窗外面流动的雾 + 门缝底下钻进来的一缕缕雾
  pendulum   strip  8 帧 @4 fps   落地钟的钟摆（2 s 一个来回）
  fire       strip  8 帧 @8 fps   壁炉的火 + 炉口地上一圈跳动的光
  lamp / sconce_l / sconce_r  strip 8 帧 @4 fps   柜台煤油灯 / 两盏壁灯的火苗（同一个帧函数）
  smoke      strip  8 帧 @4 fps   烟灰缸里那支烟冒的细烟
  chandelier strip  8 帧 @4 fps   吊灯（整个灯身挂在链子上轻轻晃 ±1 px，五个火苗跳）
  fog_tint   tint   key 'fog'    #8a969a α 0.22：雾漫进来，画面变灰
  fg: counter_front  pano key 'counter'（可选，规格之外加的）：柜台正面那一截（和底图一模一样），画在人物前面——
                     剧情把恩雅放在 anchors.counter_behind [272,147]（柜台后面）再打开它，柜台就挡住她的下半身
  fg: floor_fog      wrap key 'fog'  vx 5   地上漫过来的一层雾（人物前面，y 136–180；规格写 fg strip，
                     用 wrap 一样是“在动的一层雾”，首尾无缝、比 8 帧的 strip 小得多）
锚点（规格要求的名字一个不少，值照规格）：door [30,162]、coat [16,150]、stairs [70,150]、wc_door [104,152]、sofa [150,154]、
  guest [150,163]、clock [196,110]、counter [272,161]（柜台前面，人站点）、counter_box [240,118,316,150]、bell [258,124]、
  keys [292,96]、skull [220,76]
  另外多导出：counter_behind [272,147]（柜台后面：配 key 'counter'）、landing [128,81]（楼梯平台）、upstairs [128,62]
  （平台后面的拱门）、fireplace [222,146]、painting [153,93]、deer [221,70]、lamp_light [300,114]、walk_x [8,312]。
key：fog（雾漫进来）、counter（可选：柜台前沿画到人物前面）。
单独运行：python -B tools\bg_new\enya_inn.py → tools\bg_new\_preview\ch5\enya_inn_dev\*.png
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _parts():
    key = 'bg_new_ch5_town_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'ch5_town_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402

C = A._c4
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
mul_box, cast_shadow, mottle = P.mul_box, P.cast_shadow, P.mottle

# ============================================================ 尺寸 / 竖向结构
W, H = 320, 180
GROUND = 160
WALK = (148, 176)
N_ANIM, FPS_ANIM = 8, 4.0
FPS_FIRE = 8.0
CROWN = (8, 11)
PAPER = (12, 103)
DADO = 104
WAIN = (107, 138)
SKIRT = (139, 145)
FLOOR = 146

DOOR = (22, 48)
STAIR_X0, STEP, NSTEP = 60, 5, 12      # 楼梯脚 x、每级 5×5、12 级
LANDING = (120, 137, 81)               # 平台 x0, x1, 台面 y
SOFA = (130, 170)
TABLE = (172, 183)
CLOCK_X = (189, 203)
FIRE = (206, 238)
COUNTER = (240, 316)
CTOP = 130                             # 柜台台面 y（台面 130–131，正面 132–147）
LAMP_X = 300                           # 柜台煤油灯
SCONCES = ((53, 90), (179, 92))        # 壁灯（灯罩底 x, y）
CHAND = (160, 4)                       # 吊灯挂点

ANCHORS = dict(
    door=[30, 162], coat=[16, 150], stairs=[70, 150], wc_door=[104, 152], sofa=[150, 154], guest=[150, 163],
    clock=[196, 110], counter=[272, 161], counter_box=[240, 118, 316, 150], bell=[258, 124], keys=[292, 96],
    skull=[220, 76],
    counter_behind=[272, 147], landing=[128, 81], upstairs=[128, 62], fireplace=[222, 146], painting=[153, 93],
    deer=[221, 70], lamp_light=[LAMP_X, 114], walk_x=[8, 312],
)
STAND = ('door', 'coat', 'stairs', 'wc_door', 'sofa', 'guest', 'counter')

# ============================================================ 调色（“白天的固有色”，最后统一压暗再打灯）
INK = (30, 24, 24)
PAPER_C = (104, 112, 92)              # 墙纸（暗橄榄绿）
PAPER_D = (92, 100, 82)
PAPER_HI = (118, 124, 100)
CEIL = (70, 56, 48)
BEAM = (54, 42, 36)
WD = (112, 76, 52)                    # 胡桃木
WD_D = (84, 56, 40)
WD_HI = (138, 98, 68)
WD_K = (58, 38, 28)
FLOOR_C = (152, 114, 82)
FLOOR_D = (136, 100, 72)
FLOOR_HI = (162, 122, 88)
RUG = (160, 88, 74)
RUG_B = (140, 102, 76)
RUG_G = (170, 130, 86)
RUG_N = (122, 116, 124)
VELVET = (124, 52, 54)
VELVET_D = (96, 38, 42)
VELVET_HI = (150, 72, 70)
MARBLE = (176, 170, 160)
MARBLE_D = (146, 140, 132)
BRASS = (204, 164, 86)
BRASS_D = (150, 112, 54)
BRASS_HI = (240, 214, 140)
FLAME_HI = (255, 244, 196)
FLAME = (255, 196, 96)
FLAME_D = (226, 120, 44)
GLASS_FOG = (132, 146, 150)           # 门玻璃外面的雾（自己发光，不压暗）
AMBIENT = np.array((0.56, 0.56, 0.64), np.float32)
WARM = (255, 204, 136)
FOG_TINT = ('#8a969a', 0.22)
FOG_C = (150, 160, 164)


# ============================================================ 墙 / 天花板 / 地板
def draw_shell(im):
    d = ImageDraw.Draw(im)
    rect(d, 0, 0, W - 1, CROWN[0] - 1, CEIL)                        # 天花板木板 + 两道梁
    for x in range(0, W, 9):
        vl(d, x, 0, CROWN[0] - 1, dk(CEIL, 0.86))
    for bx in (72, 236):
        rect(d, bx - 6, 0, bx + 6, CROWN[0] + 1, BEAM)
        vl(d, bx - 6, 0, CROWN[0] + 1, lt(BEAM, 0.12))
        hl(d, bx - 6, bx + 6, CROWN[0] + 1, dk(BEAM, 0.7))
    rect(d, 0, CROWN[0], W - 1, CROWN[1], WD)                       # 檐口线
    hl(d, 0, W - 1, CROWN[0], WD_HI)
    hl(d, 0, W - 1, CROWN[1], WD_D)
    for x in range(0, W, 3):
        px(d, x, CROWN[0] + 2, WD_D)
    rect(d, 0, PAPER[0], W - 1, PAPER[1], PAPER_C)                  # 墙纸：大马士革花纹（8×12 一格，错位）
    a = np.array(im)
    for y in range(PAPER[0], PAPER[1] + 1):
        for x in range(W):
            ty, tx = (y - PAPER[0]) % 12, (x + ((y - PAPER[0]) // 12 % 2) * 4) % 8
            m = abs(tx - 3.5) + abs(ty - 5.5) * 0.66
            if 2.2 < m < 3.2 or (tx in (3, 4) and ty in (2, 9)):
                a[y, x, :3] = PAPER_HI
            elif m < 1.2:
                a[y, x, :3] = PAPER_D
            elif tx == 0 and ty % 2 == 0:
                a[y, x, :3] = PAPER_D
    im.paste(Image.fromarray(a, 'RGBA'))
    mottle(im, (0, PAPER[0], W - 1, PAPER[1]), PAPER_C, dk(PAPER_C, 0.92), lt(PAPER_C, 0.05), 201, cell=6)
    d = ImageDraw.Draw(im)
    for y in (18, 19):                                             # 挂画线
        hl(d, 0, W - 1, y, WD if y == 18 else WD_D)
    for (sx, sy, L) in ((96, 22, 30), (186, 30, 22), (300, 20, 26), (12, 40, 34)):   # 墙纸上的水渍 / 起翘
        for k in range(L):
            if hash01(sx, k, 202) < 0.8:
                px(d, sx + k // 9, sy + k, dk(PAPER_C, 0.84))
    rect(d, 0, DADO, W - 1, DADO + 2, WD)                           # 腰线
    hl(d, 0, W - 1, DADO, WD_HI)
    hl(d, 0, W - 1, DADO + 2, WD_D)
    rect(d, 0, WAIN[0], W - 1, WAIN[1], WD)                         # 护墙板：一块块凸板
    for x0 in range(2, W, 20):
        rect(d, x0, WAIN[0] + 4, x0 + 15, WAIN[1] - 4, dk(WD, 0.92))
        hl(d, x0, x0 + 15, WAIN[0] + 4, WD_D)
        vl(d, x0, WAIN[0] + 4, WAIN[1] - 4, WD_D)
        hl(d, x0, x0 + 15, WAIN[1] - 4, WD_HI)
        vl(d, x0 + 15, WAIN[0] + 4, WAIN[1] - 4, WD_HI)
    mottle(im, (0, WAIN[0], W - 1, WAIN[1]), WD, dk(WD, 0.94), lt(WD, 0.05), 203, cell=3)
    d = ImageDraw.Draw(im)
    rect(d, 0, SKIRT[0], W - 1, SKIRT[1], WD_D)                     # 踢脚板
    hl(d, 0, W - 1, SKIRT[0], WD)
    hl(d, 0, W - 1, SKIRT[1], WD_K)


def draw_floor(im):
    """木地板：一条条横着的地板（越近越宽），接缝错开；中间一块旧波斯地毯（低对比）。"""
    a = np.array(im)
    y, row = FLOOR, 0
    while y < H:
        rh = 3 if y < 156 else (4 if y < 168 else 5)
        for x in range(W):
            c = FLOOR_C
            seg = (x + row * 23) // 31
            f = hrange(0.95, 1.05, row, seg, 211)
            if (x + row * 23) % 31 == 0:
                c = FLOOR_D
            for yy in range(y, min(H, y + rh)):
                cc = c if yy < y + rh - 1 else FLOOR_D
                if yy == y and c is FLOOR_C:
                    cc = FLOOR_HI
                a[yy, x, :3] = [min(255, int(v * f)) for v in cc]
                a[yy, x, 3] = 255
        y += rh
        row += 1
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for i in range(50):                                            # 钉子 / 磨痕
        x, yy = int(hrange(0, W, i, 212)), int(hrange(FLOOR + 1, H, i, 213))
        px(d, x, yy, FLOOR_D if i % 3 else (88, 66, 50))
    x0, x1, y0, y1 = 96, 236, 150, 171                              # 地毯
    for yy in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            e = min(x - x0, x1 - x, (yy - y0) * 2, (y1 - yy) * 2)
            c = RUG
            if e < 2:
                c = RUG_B
            elif e < 5:
                c = RUG_G if (x + yy) % 4 < 2 else RUG_B
            elif e < 6:
                c = RUG_B
            else:
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                m = abs(x - cx) / 3 + abs(yy - cy)
                if 5 < m < 6.5:
                    c = RUG_G
                elif m < 3:
                    c = RUG_N
                elif (x // 6 + yy // 3) % 5 == 0 and m > 9:
                    c = mix(RUG, RUG_G, 0.4)
            if hash01(x, yy, 214) < 0.12:
                c = dk(c, 0.9)                                     # 磨秃的地方
            px(d, x, yy, c)
    for x in range(x0, x1 + 1, 2):                                  # 两头的穗
        px(d, x, y0 - 1, RUG_G)
        px(d, x, y1 + 1, RUG_G)
    rect(d, 20, FLOOR, 48, FLOOR + 3, (88, 76, 60))                 # 门口的地垫
    for x in range(20, 49, 2):
        px(d, x, FLOOR + 1, (100, 86, 68))


# ============================================================ 门 / 衣帽架
def draw_door(im):
    d = ImageDraw.Draw(im)
    a, b = DOOR
    rect(d, a - 3, 88, b + 2, SKIRT[1], WD_D)                       # 门套
    vl(d, a - 3, 88, SKIRT[1], WD)
    vl(d, b + 2, 88, SKIRT[1], WD_K)
    hl(d, a - 4, b + 3, 87, WD_HI)
    cx = (a + b - 1) / 2                                           # 半圆气窗（外面的雾在 strip 里，这里先画框）
    for x in range(a, b):
        u = (x - cx) / ((b - a) / 2)
        top = 100 - int(round(9 * math.sqrt(max(0.0, 1 - u * u))))
        vl(d, x, top, 100, GLASS_FOG)
        px(d, x, top - 1, WD)
    for k in range(5):                                             # 气窗的放射窗棂
        ang = math.pi * (k + 1) / 6
        for r in range(1, 10):
            px(d, round(cx - math.cos(ang) * r * 1.4), round(100 - math.sin(ang) * r), WD_D)
    hl(d, a, b - 1, 101, WD)
    for (x0, x1) in ((a, a + 12), (a + 13, b - 1)):                 # 两扇门
        rect(d, x0, 102, x1, SKIRT[1], WD)
        vl(d, x0, 102, SKIRT[1], WD_HI)
        vl(d, x1, 102, SKIRT[1], WD_K)
        rect(d, x0 + 2, 104, x1 - 2, 122, GLASS_FOG)                # 玻璃（雾）
        hl(d, x0 + 2, x1 - 2, 113, WD_D)                            # 玻璃中间一道横档
        rect(d, x0 + 2, 126, x1 - 2, 140, dk(WD, 0.86))             # 下面一块凹板
        hl(d, x0 + 2, x1 - 2, 126, WD_D)
        vl(d, x0 + 2, 126, 140, WD_D)
        hl(d, x0 + 2, x1 - 2, 140, WD_HI)
    px(d, a + 11, 124, BRASS)                                       # 门把手
    px(d, a + 14, 124, BRASS)
    px(d, a + 11, 125, BRASS_D)
    px(d, a + 14, 125, BRASS_D)
    rect(d, a + 5, 141, a + 8, 143, BRASS_D)                        # 门挡


def door_glass_mask():
    """门上 / 气窗里能看到外面雾的那些像素（strip 只在这里画雾）。"""
    m = np.zeros((H, W), bool)
    a, b = DOOR
    cx = (a + b - 1) / 2
    for x in range(a, b):
        u = (x - cx) / ((b - a) / 2)
        top = 100 - int(round(9 * math.sqrt(max(0.0, 1 - u * u))))
        m[top:101, x] = True
    for (x0, x1) in ((a, a + 12), (a + 13, b - 1)):
        m[104:123, x0 + 2:x1 - 1] = True
        m[113, x0 + 2:x1 - 1] = False
    for k in range(5):
        ang = math.pi * (k + 1) / 6
        for r in range(1, 10):
            m[round(100 - math.sin(ang) * r), round(cx - math.cos(ang) * r * 1.4)] = False
    return m


def draw_coat_rack(im):
    """衣帽架：三脚木架、顶上一个圆头；左钩挂一顶礼帽（歪着）、右钩挂一件大衣（只到半截，看得出是挂着的）+ 一条围巾，
    脚边斜靠一把黑伞。帽子和大衣分开挂，免得看上去像一个站着的人。"""
    lay = A._new(W, H)
    d = ImageDraw.Draw(lay)
    x = 14
    for (dx, dy) in ((-5, 4), (5, 4), (0, 3)):                      # 三只脚
        d.line((x, 140, x + dx, 140 + dy), fill=C(WD_D))
    vl(d, x, 96, 141, WD)
    vl(d, x + 1, 96, 141, WD_D)
    d.ellipse((x - 1, 92, x + 2, 95), fill=C(WD_HI))                # 圆头
    for (hx, hy) in ((x - 4, 99), (x + 5, 99), (x - 3, 104), (x + 4, 104)):   # 挂钩
        d.line((x, hy + 2, hx, hy), fill=C(BRASS_D))
        px(d, hx, hy - 1, BRASS)
    rect(d, x - 9, 100, x - 2, 101, (44, 40, 40))                   # 礼帽（挂在左钩上，歪着）
    d.polygon([(x - 8, 100), (x - 7, 94), (x - 3, 94), (x - 3, 100)], fill=C((52, 48, 48)))
    hl(d, x - 7, x - 3, 98, (110, 60, 56))
    for yy in range(101, 121):                                     # 大衣（挂在右钩上，肩膀塌着，下摆到 y 120）
        u = (yy - 101) / 19
        hw = int(round(2 + 3 * u))
        for xx in range(x + 4 - hw, x + 5 + hw):
            c = (96, 80, 66)
            if xx == x + 4 - hw:
                c = (112, 94, 78)
            elif xx >= x + 4 + hw - 1:
                c = (74, 62, 52)
            elif (xx + yy) % 5 == 0 and u > 0.3:
                c = (86, 72, 60)
            px(d, xx, yy, c)
    for yy in range(104, 118, 4):
        px(d, x + 5, yy, (60, 50, 42))
    for k in range(10):                                            # 围巾（从钩子上垂下来）
        px(d, x + 2 - (k // 5), 102 + k, (120, 60, 56) if k % 3 else (90, 44, 42))
    for k in range(26):                                            # 斜靠的黑伞
        px(d, 4 + k // 9, 144 - k, (40, 38, 44))
    d.polygon([(3, 128), (6, 118), (9, 128)], fill=C((46, 44, 50)))
    hl(d, 2, 4, 145, (60, 50, 44))
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)


# ============================================================ 楼梯 + 厕所门
def step_top(k):
    """第 k 级（0 = 最下面）的踏面 y 和 x 范围。"""
    return 141 - STEP * k, STAIR_X0 + STEP * k, STAIR_X0 + STEP * k + STEP - 1


def draw_stairs(im):
    d = ImageDraw.Draw(im)
    lx0, lx1, ly = LANDING
    # 平台后面的拱门（黑洞洞的二楼走廊，深处一扇虚掩的门缝透出一点光）
    rect(d, lx0 - 1, 44, lx1 + 1, ly, WD_D)
    for x in range(lx0 + 1, lx1):
        u = (x - (lx0 + lx1) / 2) / ((lx1 - lx0) / 2)
        top = 52 - int(round(6 * math.sqrt(max(0.0, 1 - u * u))))
        vl(d, x, top, ly - 1, (26, 22, 24))
        px(d, x, top - 1, WD)
    vl(d, (lx0 + lx1) // 2 + 2, 62, ly - 4, (120, 92, 60))           # 门缝的光
    # 楼梯下面封起来的护墙板（从斜梁底下到地面），里面一扇厕所门
    a = np.array(im)
    for x in range(STAIR_X0 - 1, lx1 + 1):
        k = min(NSTEP - 1, max(0, (x - STAIR_X0) // STEP))
        yb = 146 - STEP * (k + 1) + 7 if x < lx0 else ly + 5         # 斜梁下沿
        for y in range(max(yb, PAPER[0]), SKIRT[0]):
            a[y, x, :3] = dk(WD, 0.8) if (x - STAIR_X0) % 14 not in (0, 1) else dk(WD_D, 0.85)
            a[y, x, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for x0 in range(STAIR_X0 + 2, lx1 - 8, 14):                       # 护墙板上的凹板（顺着楼梯斜着变矮）
        k = min(NSTEP - 1, max(0, (x0 + 10 - STAIR_X0) // STEP))
        top = max(146 - STEP * (k + 1) + 11, 90) if x0 + 10 < lx0 else ly + 10
        if top < 132:
            rect(d, x0 + 1, top, x0 + 10, 134, dk(WD, 0.72))
            hl(d, x0 + 1, x0 + 10, top, dk(WD_D, 0.85))
            vl(d, x0 + 1, top, 134, dk(WD_D, 0.85))
            hl(d, x0 + 1, x0 + 10, 134, WD)
    wx0, wx1 = 97, 111                                              # 厕所门
    rect(d, wx0 - 2, 109, wx1 + 2, SKIRT[1], WD_D)
    rect(d, wx0, 111, wx1, SKIRT[1], (104, 72, 50))
    vl(d, wx0, 111, SKIRT[1], WD_HI)
    vl(d, wx1, 111, SKIRT[1], WD_K)
    for (y0, y1) in ((114, 126), (129, 142)):
        rect(d, wx0 + 2, y0, wx1 - 2, y1, dk((104, 72, 50), 0.9))
        hl(d, wx0 + 2, wx1 - 2, y0, WD_D)
        hl(d, wx0 + 2, wx1 - 2, y1, WD_HI)
    px(d, wx1 - 2, 128, BRASS)
    px(d, wx1 - 2, 129, BRASS_D)
    rect(d, wx0, 115, wx0 + 13, 123, (222, 222, 214))                # WC 小搪瓷牌（字四周留一圈白边才读得出）
    rect(d, wx0, 115, wx0 + 13, 123, None, outline=(70, 90, 130))
    P.text_px(d, wx0 + 2, 117, 'WC', (50, 70, 120), font=P.FONT3, gap=1)
    px(d, wx0 + 1, 116, (120, 120, 116))                             # 掉了瓷的角
    px(d, wx0 + 12, 122, (120, 120, 116))
    # 踏步：每级踏面亮一行、下面一行暗（立板），斜梁一道
    for x in range(STAIR_X0 - 1, lx0):                               # 斜梁（扶手这边的那根）：上沿亮、下沿暗
        yb = 146 - (x - STAIR_X0) + 1
        for j, y in enumerate(range(yb, yb + 4)):
            px(d, x, y, (WD_HI, WD, WD_D, WD_K)[j])
    for k in range(NSTEP):
        ty, x0, x1 = step_top(k)
        rect(d, x0, ty, x1, ty + STEP - 1, (110, 54, 50))           # 一级：铺着红地毯的踏面 + 立板
        hl(d, x0 - 1, x1, ty, lt(WD_HI, 0.15))                      # 踏步鼻（亮，往前伸 1 px）
        hl(d, x0, x1, ty + 1, (130, 66, 58))
        for y in range(ty + 2, ty + STEP):                         # 立板（暗）
            hl(d, x0, x1, y, (86, 42, 40) if y < ty + STEP - 1 else (64, 32, 32))
        px(d, x1, ty + 1, BRASS)                                    # 压地毯的铜条
        vl(d, x1 + 1, ty, ty + STEP - 1, WD_K)                       # 上一级立板前的一道暗缝
    rect(d, lx0, ly, lx1, ly + 4, WD)                                # 平台
    hl(d, lx0, lx1, ly, WD_HI)
    hl(d, lx0, lx1, ly + 4, WD_K)
    # 扶手：底下的望柱 + 栏杆 + 斜扶手 + 平台上的一截
    lay = A._new(W, H)
    ld = ImageDraw.Draw(lay)
    rect(ld, 57, 116, 60, 145, WD)                                   # 望柱
    vl(ld, 57, 116, 145, WD_HI)
    vl(ld, 60, 116, 145, WD_K)
    ld.ellipse((56, 110, 61, 115), fill=C(WD_HI))
    px(ld, 57, 111, lt(WD_HI, 0.2))
    rect(ld, 56, 140, 61, 145, WD_D)
    for k in range(NSTEP):                                          # 栏杆：每级一根（中间鼓一点的车木栏杆）
        ty, x0, x1 = step_top(k)
        bx = x0 + 2
        top = ty - 22 - 2
        vl(ld, bx, top, ty - 1, WD)
        px(ld, bx + 1, top + 6, WD_D)
        px(ld, bx + 1, ty - 4, WD_D)
    for x in range(58, lx0 + 1):                                      # 斜扶手
        y = 141 - 22 - (x - STAIR_X0) - 1
        hl(ld, x, x, y, WD_HI)
        hl(ld, x, x, y + 1, WD)
        px(ld, x, y + 2, WD_K)
    yr = 141 - 22 - (lx0 - STAIR_X0) - 1                              # 平台栏杆
    hl(ld, lx0, lx1, yr, WD_HI)
    hl(ld, lx0, lx1, yr + 1, WD)
    for bx in range(lx0 + 1, lx1, 3):
        vl(ld, bx, yr + 2, ly - 1, WD_D)
    rect(ld, lx1 - 1, yr - 3, lx1 + 1, ly + 4, WD)
    vl(ld, lx1 + 1, yr - 3, ly + 4, WD_K)
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)


# ============================================================ 沙发 / 小圆几 / 画
def draw_sofa(im):
    lay = A._new(W, H)
    d = ImageDraw.Draw(lay)
    a, b = SOFA
    for x in range(a + 4, b - 3):                                    # 驼峰靠背
        u = (x - a - 4) / (b - a - 8)
        top = 124 - int(round(4 * math.sin(math.pi * u) ** 1.5))
        for y in range(top, 136):
            c = VELVET
            if y == top:
                c = VELVET_HI
            elif y > 133:
                c = VELVET_D
            d.point((x, y), fill=C(c))
    for k, x in enumerate(range(a + 8, b - 6, 6)):                   # 拉扣
        for y in (128, 132):
            px(d, x + (3 if y == 132 else 0), y, VELVET_D)
            px(d, x + (3 if y == 132 else 0) + 1, y - 1, VELVET_HI)
    rect(d, a + 3, 136, b - 3, 140, VELVET)                          # 坐垫
    hl(d, a + 3, b - 3, 136, VELVET_HI)
    vl(d, (a + b) // 2, 136, 140, VELVET_D)
    rect(d, a + 2, 141, b - 2, 143, WD)                              # 木裙边 + 脚
    hl(d, a + 2, b - 2, 141, WD_HI)
    for lx in (a + 3, b - 4):
        rect(d, lx, 144, lx + 1, SKIRT[1] + 1, WD_D)
    for (x0, sgn) in ((a, 1), (b - 5, -1)):                          # 两边的卷扶手
        rect(d, x0, 130, x0 + 4, 141, VELVET)
        d.ellipse((x0 - 1, 127, x0 + 5, 133), fill=C(VELVET_HI))
        d.ellipse((x0 + 1, 129, x0 + 3, 131), fill=C(VELVET_D))
        vl(d, x0 + (4 if sgn > 0 else 0), 132, 141, VELVET_D)
    rect(d, b - 14, 130, b - 7, 136, (150, 130, 96))                 # 靠垫（褪色的金）
    hl(d, b - 14, b - 7, 130, (176, 156, 116))
    px(d, b - 11, 133, (120, 100, 70))
    P.ink(lay, INK, sides='all')
    im.alpha_composite(lay)


def draw_table(im):
    lay = A._new(W, H)
    d = ImageDraw.Draw(lay)
    a, b = TABLE
    cx = (a + b) // 2
    rect(d, a, 130, b, 131, WD_HI)                                   # 圆桌面
    hl(d, a, b, 132, WD_D)
    vl(d, cx, 133, 142, WD)                                          # 独腿 + 三脚
    d.line((cx, 142, a + 1, 145), fill=C(WD_D))
    d.line((cx, 142, b - 1, 145), fill=C(WD_D))
    rect(d, a + 1, 128, a + 5, 129, (120, 124, 130))                 # 烟灰缸 + 那支烟
    hl(d, a + 2, a + 4, 127, (150, 154, 160))
    hl(d, a + 4, a + 8, 127, (226, 222, 210))
    px(d, a + 8, 127, (230, 120, 60))
    rect(d, b - 3, 125, b - 1, 129, (170, 196, 196))                 # 威士忌杯
    hl(d, b - 3, b - 1, 128, (190, 130, 60))
    rect(d, a + 5, 129, b - 4, 129, (200, 196, 182))                 # 报纸
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)


def draw_painting(im):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 139, 82, 167, 104
    rect(d, x0, y0, x1, y1, BRASS_D)                                 # 金框
    rect(d, x0 + 1, y0 + 1, x1 - 1, y1 - 1, BRASS)
    hl(d, x0 + 1, x1 - 1, y0 + 1, BRASS_HI)
    for x in range(x0 + 2, x1 - 1, 3):
        px(d, x, y1 - 1, BRASS_D)
    ix0, iy0, ix1, iy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 3
    for y in range(iy0, iy1 + 1):                                    # 夜色的风景：天、雪山、湖、松林
        u = (y - iy0) / (iy1 - iy0)
        hl(d, ix0, ix1, y, mix((84, 100, 112), (130, 140, 140), u))
    pts = [(ix0, iy0 + 9), (ix0 + 6, iy0 + 3), (ix0 + 10, iy0 + 6), (ix0 + 15, iy0 + 1), (ix1, iy0 + 8), (ix1, iy0 + 11),
           (ix0, iy0 + 11)]
    d.polygon(pts, fill=C((110, 118, 126)))
    for (sx, sy) in ((ix0 + 6, iy0 + 3), (ix0 + 15, iy0 + 1)):
        hl(d, sx - 1, sx + 1, sy + 1, (210, 214, 214))
        px(d, sx, sy, (226, 230, 230))
    rect(d, ix0, iy0 + 11, ix1, iy1, (70, 92, 104))                  # 湖
    for x in range(ix0 + 1, ix1, 4):
        px(d, x, iy0 + 13, (120, 140, 150))
    for x in range(ix0, ix1 + 1, 2):                                 # 松林
        h = 3 + (x * 7) % 4
        vl(d, x, iy0 + 11 - h, iy0 + 11, (50, 68, 58))
    d.line((x0 + 6, y0 - 1, (x0 + x1) // 2, y0 - 9), fill=C(BRASS_D))   # 挂绳 + 钉子
    d.line((x1 - 6, y0 - 1, (x0 + x1) // 2, y0 - 9), fill=C(BRASS_D))
    px(d, (x0 + x1) // 2, y0 - 10, BRASS_HI)
    mul_box(im, (x0 + 1, y1 + 1, x1 + 1, y1 + 2), (0.7, 0.72, 0.8))
    mul_box(im, (x1 + 1, y0 + 1, x1 + 1, y1), (0.7, 0.72, 0.8))


# ============================================================ 落地钟
def draw_clock(im):
    lay = A._new(W, H)
    d = ImageDraw.Draw(lay)
    a, b = CLOCK_X
    cx, cy = 196, 110
    rect(d, a, 100, b, 120, WD)                                      # 钟头
    d.polygon([(a - 1, 100), (cx, 94), (b + 1, 100)], fill=C(WD_D))  # 尖顶山花
    px(d, cx, 93, BRASS_HI)
    hl(d, a - 1, b + 1, 100, WD_HI)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=C(BRASS_D))     # 钟面
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=C((222, 214, 190)))
    for k in range(12):
        ang = k * math.tau / 12
        px(d, round(cx + math.sin(ang) * 4.5), round(cy - math.cos(ang) * 4.5), (70, 60, 50))
    for (ang, L) in ((math.tau * 11.3 / 12, 3), (math.tau * 0.75, 4)):   # 11 点 45 分
        for r in range(1, L + 1):
            px(d, round(cx + math.sin(ang) * r), round(cy - math.cos(ang) * r), (40, 34, 30))
    rect(d, a + 1, 121, b - 1, 139, WD)                              # 钟身 + 钟摆窗（暗，钟摆在 strip）
    rect(d, cx - 4, 123, cx + 4, 137, (40, 30, 26))
    rect(d, cx - 4, 123, cx + 4, 137, None, outline=BRASS_D)
    vl(d, a + 1, 121, 139, WD_HI)
    vl(d, b - 1, 121, 139, WD_K)
    rect(d, a - 1, 140, b + 1, SKIRT[1] + 1, WD_D)                   # 底座
    hl(d, a - 1, b + 1, 140, WD_HI)
    for x in range(a + 1, b, 4):
        px(d, x, 143, WD_K)
    P.ink(lay, INK, sides='all')
    im.alpha_composite(lay)


PEND_BOX = (191, 123, 202, 138)


# ============================================================ 壁炉 + 鹿头
def draw_fireplace(im):
    lay = A._new(W, H)
    d = ImageDraw.Draw(lay)
    a, b = FIRE
    rect(d, a, 112, b, SKIRT[1], MARBLE)                             # 大理石炉框
    for i in range(30):                                              # 大理石的纹
        x, y = int(hrange(a, b, i, 231)), int(hrange(114, 145, i, 232))
        L = int(hrange(2, 5, i, 233))
        for k in range(L):
            px(d, x + k, y + k // 2, MARBLE_D)
    vl(d, a, 112, SKIRT[1], lt(MARBLE, 0.2))
    vl(d, b, 112, SKIRT[1], MARBLE_D)
    rect(d, a - 3, 109, b + 3, 112, lt(MARBLE, 0.1))                 # 壁炉台
    hl(d, a - 3, b + 3, 109, lt(MARBLE, 0.3))
    hl(d, a - 3, b + 3, 112, MARBLE_D)
    fx0, fx1 = 213, 231                                              # 炉膛（暗）+ 柴架 + 木柴
    for x in range(fx0, fx1 + 1):
        u = (x - (fx0 + fx1) / 2) / ((fx1 - fx0) / 2)
        top = 125 - int(round(3 * math.sqrt(max(0.0, 1 - u * u))))
        vl(d, x, top, SKIRT[1], (30, 24, 22))
        px(d, x, top - 1, MARBLE_D)
    for x in range(fx0, fx1 + 1):                                    # 炉膛里的砖
        for y in range(126, SKIRT[1], 3):
            if (x + (y // 3) * 3) % 6 == 0:
                px(d, x, y, (44, 32, 28))
    rect(d, fx0 + 2, 141, fx1 - 2, 142, (60, 40, 30))               # 木柴
    rect(d, fx0 + 4, 139, fx1 - 4, 140, (76, 50, 34))
    for x in (fx0 + 2, fx1 - 2):                                     # 柴架
        vl(d, x, 137, SKIRT[1], (40, 40, 44))
        px(d, x, 136, BRASS_D)
    rect(d, a - 2, 144, b + 2, 147, (120, 110, 104))                 # 炉前石
    hl(d, a - 2, b + 2, 144, (140, 130, 122))
    # 壁炉台上：一对烛台、一只花瓶、两个相框
    for x in (a + 2, b - 2):
        rect(d, x - 1, 104, x + 1, 108, BRASS)
        hl(d, x - 2, x + 2, 108, BRASS_D)
        rect(d, x, 99, x, 103, (226, 220, 200))                      # 蜡烛（没点）
    rect(d, a + 9, 101, a + 13, 108, (70, 90, 110))                  # 花瓶 + 枯花
    hl(d, a + 10, a + 12, 100, (90, 110, 130))
    for k in range(4):
        vl(d, a + 9 + k, 96 - k % 2, 99, (110, 100, 80))
    for (x0, c) in ((b - 13, (180, 170, 150)), (b - 8, (160, 150, 136))):
        rect(d, x0, 102, x0 + 4, 108, BRASS_D)
        rect(d, x0 + 1, 103, x0 + 3, 107, c)
        px(d, x0 + 2, 104, (90, 80, 70))
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)


def draw_deer(im):
    """壁炉上方的鹿头标本：盾形木托、鹿脸（朝左前方）、一对大角往上张开。"""
    lay = A._new(W, H)
    d = ImageDraw.Draw(lay)
    cx = 221
    d.polygon([(cx - 7, 74), (cx + 7, 74), (cx + 7, 86), (cx, 91), (cx - 7, 86)], fill=C(WD))   # 木托
    hl(d, cx - 7, cx + 7, 74, WD_HI)
    vl(d, cx + 7, 74, 86, WD_K)
    FUR, FUR_D, FUR_HI = (130, 98, 70), (100, 74, 54), (156, 122, 90)
    d.ellipse((cx - 5, 66, cx + 5, 80), fill=C(FUR))                 # 脖子 + 头
    d.polygon([(cx - 4, 70), (cx + 3, 70), (cx + 1, 84), (cx - 2, 84)], fill=C(FUR))
    d.polygon([(cx - 2, 76), (cx + 1, 76), (cx, 86)], fill=C(FUR_HI))
    px(d, cx - 3, 72, (20, 16, 14))                                 # 玻璃眼睛
    px(d, cx + 3, 72, (20, 16, 14))
    px(d, cx - 3, 71, (200, 190, 170))
    rect(d, cx - 1, 84, cx + 1, 86, (40, 32, 30))                    # 鼻头
    for (ex, ey, sgn) in ((cx - 7, 68, -1), (cx + 7, 68, 1)):        # 耳朵
        d.polygon([(ex, ey), (ex + 4 * sgn, ey - 2), (ex + sgn, ey + 3)], fill=C(FUR_D))
    for sgn in (-1, 1):                                              # 鹿角
        pts = [(cx + 3 * sgn, 66)]
        x, y = cx + 3 * sgn, 66
        for k in range(14):
            x += sgn * (1 if k % 3 else 0) + (sgn if k > 8 else 0)
            y -= 1
            pts.append((x, y))
        d.line(pts, fill=C((200, 186, 160)), width=1)
        for (k, L) in ((3, 4), (7, 5), (11, 4)):                     # 分叉
            bx, by = pts[k]
            d.line((bx, by, bx + sgn * (L - 1), by - L), fill=C((186, 170, 146)))
    vl(d, cx, 66, 68, FUR_D)
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)
    mul_box(im, (cx - 6, 92, cx + 9, 93), (0.7, 0.72, 0.8))


# ============================================================ 柜台
def draw_counter(im):
    a, b = COUNTER
    d = ImageDraw.Draw(im)
    # 后墙：一排信格 + 钥匙板
    gx0, gx1, gy0, gy1 = 246, 268, 82, 108
    rect(d, gx0, gy0, gx1, gy1, WD_D)
    for r in range(4):
        for c in range(4):
            x, y = gx0 + 1 + c * 5 + (c // 2), gy0 + 1 + r * 6 + (r // 2)
            rect(d, x, y, x + 3, y + 4, (40, 28, 22))
            hl(d, x, x + 3, y + 4, WD)
            if hash01(r, c, 241) < 0.45:                               # 格子里的信 / 明信片
                rect(d, x, y + 2, x + 2, y + 4, ((206, 198, 176), (180, 190, 196), (210, 184, 150))[(r + c) % 3])
    rect(d, gx0 - 1, gy0 - 2, gx1 + 1, gy0 - 1, WD_HI)
    kx0, kx1, ky0, ky1 = 276, 308, 85, 107                            # 钥匙板（中心 292, 96）
    rect(d, kx0, ky0, kx1, ky1, WD)
    rect(d, kx0, ky0, kx1, ky1, None, outline=WD_K)
    hl(d, kx0 + 1, kx1 - 1, ky0 + 1, WD_HI)
    for r, yy in enumerate((89, 99)):
        for k in range(6):
            x = kx0 + 3 + k * 5
            px(d, x, yy, BRASS_HI)                                    # 钩子
            if not (r == 1 and k == 4):                               # 有一格空着（有人住进来了）
                vl(d, x, yy + 1, yy + 3, (176, 170, 160))            # 钥匙
                rect(d, x - 1, yy + 4, x + 1, yy + 6, BRASS)          # 铜牌
                px(d, x, yy + 5, BRASS_D)
    # 柜台：台面 + 正面三块凹板（正面最低到 y 147，不进可走带）
    rect(d, a, CTOP, b, CTOP + 1, WD_HI)
    hl(d, a, b, CTOP, lt(WD_HI, 0.2))
    rect(d, a + 1, CTOP + 2, b - 1, 147, WD)
    hl(d, a + 1, b - 1, CTOP + 2, WD_K)
    for i in range(3):
        x0 = a + 4 + i * 25
        rect(d, x0, CTOP + 6, x0 + 20, 143, dk(WD, 0.88))
        hl(d, x0, x0 + 20, CTOP + 6, WD_D)
        vl(d, x0, CTOP + 6, 143, WD_D)
        hl(d, x0, x0 + 20, 143, WD_HI)
        vl(d, x0 + 20, CTOP + 6, 143, WD_HI)
        d.ellipse((x0 + 8, CTOP + 9, x0 + 12, CTOP + 13), outline=C(WD_D))     # 凹板上的小圆花
    vl(d, a + 1, CTOP + 2, 147, WD_HI)
    vl(d, b - 1, CTOP + 2, 147, WD_K)
    hl(d, a + 1, b - 1, 147, WD_K)
    # 台面上：铜铃（anchors.bell）、登记簿 + 墨水瓶 + 羽毛笔、煤油灯座（灯罩和火苗在 strip）
    bx, by = 258, 124
    d.ellipse((bx - 3, by - 2, bx + 3, by + 5), fill=C(BRASS))
    rect(d, bx - 3, by + 3, bx + 3, CTOP - 1, BRASS)
    hl(d, bx - 4, bx + 4, CTOP - 1, BRASS_D)
    px(d, bx - 1, by, BRASS_HI)
    px(d, bx, by - 3, BRASS_D)
    px(d, bx, by - 4, BRASS_HI)
    rect(d, 266, 126, 286, CTOP - 1, (196, 186, 160))               # 摊开的登记簿
    vl(d, 276, 126, CTOP - 1, (120, 100, 80))
    for yy in (127, 129):
        for xx in range(268, 285):
            if xx != 276 and hash01(xx, yy, 242) < 0.7:
                px(d, xx, yy, (110, 100, 90))
    hl(d, 265, 287, CTOP - 1, (120, 60, 50))                        # 红皮封面的边
    rect(d, 289, 126, 291, CTOP - 1, (40, 40, 60))                  # 墨水瓶 + 羽毛笔
    d.line((290, 125, 294, 118), fill=C((220, 216, 204)))
    px(d, 294, 117, (236, 232, 220))
    rect(d, LAMP_X - 3, 126, LAMP_X + 3, CTOP - 1, BRASS)           # 煤油灯座
    hl(d, LAMP_X - 3, LAMP_X + 3, 126, BRASS_HI)
    rect(d, LAMP_X - 1, 122, LAMP_X + 1, 125, BRASS_D)
    rect(d, 308, 127, 313, CTOP - 1, (60, 70, 80))                  # “请按铃”小立牌（只画形状）
    hl(d, 309, 312, 128, (200, 196, 186))


@lru_cache(maxsize=1)
def counter_front():
    """柜台正面那一截（台面 + 正面），从底图里抠出来：key 'counter' 打开时画到人物前面，和底图一模一样，只是改了前后。"""
    room = room_img()
    a = np.array(room)
    out = np.zeros_like(a)
    a0, b0 = COUNTER
    out[CTOP:148, a0:b0 + 1] = a[CTOP:148, a0:b0 + 1]
    return Image.fromarray(out, 'RGBA')


# ============================================================ 壁灯 / 吊灯（静态部分）
def draw_sconce_brackets(im):
    lay = A._new(W, H)
    d = ImageDraw.Draw(lay)
    for (x, y) in SCONCES:
        rect(d, x - 1, y + 2, x + 1, y + 8, BRASS_D)                  # 墙上的铜底座 + 弯臂
        px(d, x, y + 9, BRASS)
        d.line((x, y + 5, x + 3, y + 2), fill=C(BRASS))
        rect(d, x + 1, y, x + 5, y + 1, BRASS)                        # 灯碗
        hl(d, x + 1, x + 5, y + 1, BRASS_D)
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)


# ============================================================ 组装底图（固有色 → 压暗 → 打灯 → 自发光）
LIGHTS = [  # (cx, cy, rx, ry, 颜色, 强度)
    (160, 22, 130, 62, WARM, 0.8),            # 吊灯：天花板 + 墙的上半截
    (160, 162, 190, 40, WARM, 0.5),           # 吊灯落在地上（大、匀）
    (222, 136, 70, 46, (255, 160, 90), 0.95), # 壁炉
    (222, 152, 44, 10, (255, 160, 90), 0.35),
    (LAMP_X + 2, 116, 54, 42, WARM, 0.95),    # 柜台煤油灯
    (SCONCES[0][0] + 3, 92, 26, 34, WARM, 0.75),
    (SCONCES[1][0] + 3, 94, 26, 32, WARM, 0.75),
    (35, 112, 26, 40, (160, 180, 196), 0.35), # 门玻璃透进来的雾光（冷）
]


@lru_cache(maxsize=1)
def room_img():
    im = A._new(W, H)
    draw_shell(im)
    draw_floor(im)
    draw_door(im)
    draw_stairs(im)
    draw_painting(im)
    draw_deer(im)
    draw_fireplace(im)
    draw_clock(im)
    draw_sofa(im)
    draw_table(im)
    draw_counter(im)
    draw_coat_rack(im)
    draw_sconce_brackets(im)
    for (x0, x1) in (SOFA, CLOCK_X, (FIRE[0] - 2, FIRE[1] + 2), COUNTER, (6, 22)):   # 家具在地板上落的淡影
        P.ground_shadow(im, x0, x1, FLOOR, depth=2, slant=3)
    glass = door_glass_mask()
    a = np.array(im).astype(np.float32)
    keep = a[glass].copy()
    a[..., :3] *= AMBIENT                                            # 夜里：整体压暗、偏冷
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    for (cx, cy, rx, ry, col, amt) in LIGHTS:
        P.add_light(im, cx, cy, rx, ry, col, amt, steps=4, mode='mul', power=1.3)
    a = np.array(im)
    a[glass] = keep.astype(np.uint8)                                 # 门外的雾不压暗（它是亮的那一边）
    im = Image.fromarray(a, 'RGBA')
    P.compress_band(im, 108, 147, 0.88, (84, 66, 54))
    fl = np.array(im)[148:177, :, :3].reshape(-1, 3).mean(0)
    P.compress_band(im, 148, H - 1, 0.62, tuple(int(v) for v in fl), ramp_rows=1)   # 地板上的光斑收一收：可走带平整
    im = A._grade(im, sat=0.92, val=1.0)
    return P.opaque(im)


# ============================================================ 会动的（strip，屏幕坐标 = 世界坐标）
DOORFOG_BOX = (DOOR[0] - 4, 90, DOOR[1] + 30, 152)


def doorfog_frame(t):
    """门玻璃 / 气窗外面流动的雾（只画在玻璃里）+ 门缝底下钻进来、往右散开的几缕雾。"""
    im = A._new(W, H)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    m = door_glass_mask()
    a = np.zeros((H, W, 4), np.uint8)
    n = A._fbm_wrap(64, 72, 16, seed=251, octaves=3)
    off = f * 8                                                      # 一圈 64 px / 8 帧
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        v = n[(y - 88) % 72, (x + off) % 64]
        c = mix(GLASS_FOG, (176, 186, 188), max(0.0, min(1.0, (v - 0.35) * 2.2)))
        if (v > 0.62) and ((x + y + f) % 2 == 0):
            c = (190, 198, 198)
        a[y, x, :3] = c
        a[y, x, 3] = 255
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    bay = A._bayer(W, H)
    for i in range(5):                                               # 门缝底下钻进来的雾：一团团往右飘、变淡
        u = ((f / N_ANIM) + i / 5) % 1.0
        cx = DOOR[0] + 4 + i * 4 + u * 26
        cy = 146 - 2 * math.sin(u * math.pi) - (i % 2)
        r = 1.5 + u * 2.5
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r * 2.2), int(cx + r * 2.2) + 1):
                q = 1 - math.hypot((xx - cx) / 2.2, yy - cy) / r
                if q > 0 and yy < 152 and q * (1 - u * 0.8) > bay[yy, xx] * 0.9:
                    d.point((xx, yy), fill=(160, 170, 176, int(44 + 50 * (1 - u))))
    return im


def pendulum_frame(t):
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    ang = 0.32 * math.sin(math.tau * f / N_ANIM)
    cx, top = 196, 123
    L = 11
    for k in range(L):
        px(d, round(cx + math.sin(ang) * k), top + k, BRASS_D)
    bx, by = round(cx + math.sin(ang) * L), top + L
    d.ellipse((bx - 2, by - 1, bx + 2, by + 3), fill=C(BRASS))
    px(d, bx - 1, by, BRASS_HI)
    px(d, bx + 1, by + 2, BRASS_D)
    return im


FIRE_BOX = (FIRE[0] + 6, 116, FIRE[1] - 5, 152)


def fire_frame(t):
    """壁炉的火：几条火舌（根上亮黄、往上变橙变红、尖上一点点火星），每帧高低左右都变；炉口地上一圈跳动的光。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_FIRE, N_ANIM)
    bay = A._bayer(W, H)
    fx0, fx1 = 214, 230
    for x in range(fx0, fx1 + 1):
        u = (x - (fx0 + fx1) / 2) / ((fx1 - fx0) / 2)
        base_h = 9 * (1 - u * u) ** 0.6
        h = base_h * (0.7 + 0.3 * math.sin(f * math.tau / N_ANIM * 2 + x * 1.7)) + 2 * hash01(x, f, 261)
        top = round(140 - h)
        for y in range(top, 141):
            v = (140 - y) / max(1, h)
            c = FLAME_HI if v < 0.3 else (FLAME if v < 0.65 else FLAME_D)
            px(d, x, y, c)
    for k in range(3):                                               # 火星
        sx = fx0 + int(hrange(2, 14, f, k, 262))
        sy = 128 - int(hrange(0, 8, f, k, 263))
        px(d, sx, sy, (255, 200, 120))
    for yy in range(144, 152):                                        # 炉口地上一圈跳动的光
        for xx in range(FIRE[0] + 6, FIRE[1] - 5):
            r = math.hypot((xx - 222) / 16.0, (yy - 144) / 7.0)
            amp = 0.75 + 0.25 * math.sin(f * math.tau / N_ANIM * 3)
            if r < 1 and (1 - r) * amp > bay[yy, xx] * 0.9:
                d.point((xx, yy), fill=(255, 170, 90, int(40 + 50 * (1 - r) * amp)))
    return im


LAMP_BOXES = [('lamp', (LAMP_X - 6, 104, LAMP_X + 7, 126)),
              ('sconce_l', (SCONCES[0][0] - 1, SCONCES[0][1] - 12, SCONCES[0][0] + 8, SCONCES[0][1])),
              ('sconce_r', (SCONCES[1][0] - 1, SCONCES[1][1] - 12, SCONCES[1][0] + 8, SCONCES[1][1]))]


def lamp_chimney(d, cx, base, h, f, j):
    """煤油灯的玻璃灯罩（亮）+ 里面的火苗：灯罩肚子鼓、颈细；火苗按帧伸缩、偏一点。"""
    for y in range(base - h, base):
        u = (base - y) / h
        hw = 2 if u < 0.55 else 1
        hl(d, cx - hw, cx + hw, y, (238, 210, 150) if u < 0.55 else (220, 200, 160))
    fl = (0, 1, 0, -1, 0, 1, 1, -1)[(f + j * 3) % 8]
    fh = (3, 4, 3, 2, 4, 3, 2, 4)[(f + j * 5) % 8]
    for k in range(fh):
        px(d, cx + (fl if k == fh - 1 else 0), base - 2 - k, FLAME_HI if k < fh - 1 else FLAME)
    px(d, cx, base - 1, (150, 170, 230))


def lamps_frame(t):
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    bay = A._bayer(W, H)
    lamp_chimney(d, LAMP_X, 122, 14, f, 0)
    for j, (x, y) in enumerate(SCONCES):
        lamp_chimney(d, x + 3, y, 10, f, j + 1)
    for j, (cx, cy, R) in enumerate(((LAMP_X, 114, 6), (SCONCES[0][0] + 3, SCONCES[0][1] - 5, 4),
                                     (SCONCES[1][0] + 3, SCONCES[1][1] - 5, 4))):
        rr = R + (1 if (f + j) % 3 == 0 else 0)                       # 一圈光晕（半透明，跟着火苗呼吸）
        for yy in range(cy - rr, cy + rr + 1):
            for xx in range(cx - rr, cx + rr + 1):
                q = 1 - math.hypot(xx - cx, yy - cy) / rr
                if q > 0 and q > bay[yy, xx] * 0.8 and im.getpixel((xx, yy))[3] == 0:
                    d.point((xx, yy), fill=(255, 214, 150, int(40 + 50 * q)))
    return im


SMOKE_BOX = (TABLE[0] + 4, 100, TABLE[0] + 18, 127)


def smoke_frame(t):
    """烟灰缸里那支烟冒的细烟：一条往上绕的线，越往上越淡、断断续续。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    x0, y0 = TABLE[0] + 8, 126
    for k in range(24):
        y = y0 - k
        x = x0 + round(1.6 * math.sin(k * 0.45 - f * math.tau / N_ANIM) + k * 0.12)
        if (k + f) % 6 != 0 and hash01(k, f, 271) < 1.05 - k / 30:
            d.point((x, y), fill=(196, 194, 190, int(150 - k * 4)))
    return im


CHAND_BOX = (CHAND[0] - 22, CHAND[1], CHAND[0] + 23, 40)


def chandelier_frame(t):
    """黄铜吊灯：链子挂在天花板上（顶不动），灯身左右晃 ±1 px；五个玻璃灯罩里的火苗各跳各的。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    sw = (0, 1, 1, 0, 0, -1, -1, 0)[f]
    cx, top = CHAND
    for y in range(top, 20):                                          # 链子（越往下偏得越多）
        u = (y - top) / 16
        x = cx + round(sw * u)
        px(d, x, y, BRASS_D if y % 2 else BRASS)
    bx = cx + sw
    rect(d, bx - 2, 20, bx + 2, 23, BRASS)                            # 灯身
    hl(d, bx - 2, bx + 2, 20, BRASS_HI)
    d.ellipse((bx - 3, 26, bx + 3, 31), fill=C(BRASS_D))
    vl(d, bx, 24, 33, BRASS)
    px(d, bx, 34, BRASS_HI)
    for k, ox in enumerate((-16, -8, 0, 8, 16)):                      # 五条弯臂 + 灯碗 + 灯罩
        ax = bx + ox
        ay = 27 if ox == 0 else 27 + abs(ox) // 8
        d.line((bx, 28, ax, ay), fill=C(BRASS))
        rect(d, ax - 2, ay - 1, ax + 2, ay, BRASS)
        lamp_chimney(d, ax, ay - 1, 8, f, k + 4)
    return im


# ============================================================ 雾（key 'fog'）
@lru_cache(maxsize=1)
def floor_fog():
    return P.fog_band(W, 44, 281, 122, prof=P.ramp(44, [(0, 0), (12, 0.5), (26, 1), (44, 0.8)]), cell=32, stretch=4,
                      levels=(0, 28, 54, 80, 102, 122), col=FOG_C), 136


# ============================================================ 组装
@lru_cache(maxsize=1)
def build():
    ff, fy = floor_fog()
    layers = [
        P.L_static('room', room_img()),
        P.L_strip('doorfog', DOORFOG_BOX, N_ANIM, FPS_ANIM, doorfog_frame, screen=True),
        P.L_strip('pendulum', PEND_BOX, N_ANIM, FPS_ANIM, pendulum_frame, screen=True),
        P.L_strip('fire', FIRE_BOX, N_ANIM, FPS_FIRE, fire_frame, screen=True),
    ] + [P.L_strip(n, b, N_ANIM, FPS_ANIM, lamps_frame, screen=True) for (n, b) in LAMP_BOXES] + [
        P.L_strip('smoke', SMOKE_BOX, N_ANIM, FPS_ANIM, smoke_frame, screen=True),
        P.L_strip('chandelier', CHAND_BOX, N_ANIM, FPS_ANIM, chandelier_frame, screen=True),
        P.L_tint(FOG_TINT[0], FOG_TINT[1], key='fog'),
    ]
    fg = [
        P.L_pano('counter_front', counter_front(), 1.0, key='counter'),
        P.L_wrap('floor_fog', ff, W, 0.0, fy, 5.0, key='fog'),
    ]
    return dict(layers=layers, fg=fg, room=room_img())


def compose(camX=0, t=0.5, state=None, fg=True):
    R = build()
    return P.compose(R['layers'], R['fg'], camX, t, state, with_fg=fg)


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    st = P.export_stage(ex, W, GROUND, WALK, R['layers'], R['fg'], dict(ANCHORS))
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    keys = P.keys_of(R['layers'], R['fg'])
    allon = {k: True for k in keys}
    P.check_no_black(ex, BJ, st, W, '旅馆大堂', [{}, allon], times=(0.0, 0.5, 0.75, 1.5, 7.0))
    P.check_opaque(ex, R['room'], (0, 0, W, H), '底图')
    P.check_alpha01(ex, R['room'], '底图')
    P.check_strips(ex, BJ, P.strips_of(R['layers'], R['fg']))
    P.check_wraps(ex, BJ, st)
    out = P.check_anchors(ex, st['anchors'], W, WALK, STAND, ANCHORS['walk_x'])
    ex.checked('锚点都在地图里、站人的锚点在可走带 / walk_x 里（不满足的条数）', out)
    need = ('door', 'coat', 'stairs', 'wc_door', 'sofa', 'guest', 'clock', 'counter', 'counter_box', 'bell', 'keys', 'skull')
    ex.checked('规格要求的 12 个锚点名都在', sum(k not in st['anchors'] for k in need))
    a = np.array(R['room']).astype(int)
    # 柜台：正面在 counter_box 里、最低到 y 147（不进可走带）；铃、钥匙、钟面、鹿头都画在锚点上
    cb = ANCHORS['counter_box']
    front = a[CTOP + 2:148, cb[0]:cb[2], :3]
    ex.checked('柜台正面（x 240–316，y 132–147）都是木头（暗暖色，R > B）',
               int((front[..., 0] <= front[..., 2]).sum()))
    bx, by = ANCHORS['bell']
    bell = a[by - 2:by + 5, bx - 3:bx + 4, :3]
    ex.checked('铜铃在 bell 锚点上（黄铜像素 ≥ 15）', 0 if int(((bell[..., 0] > 140) & (bell[..., 0] > bell[..., 2] + 50)).sum()) >= 15 else 1)
    kx, ky = ANCHORS['keys']
    kb = a[ky - 10:ky + 11, kx - 15:kx + 16, :3]
    ex.checked('钥匙板在 keys 锚点上（铜牌像素 ≥ 30）', 0 if int(((kb[..., 0] > 150) & (kb[..., 0] > kb[..., 2] + 50)).sum()) >= 30 else 1)
    cx, cy = ANCHORS['clock']
    face = a[cy - 3:cy + 4, cx - 3:cx + 4, :3]
    ex.checked('钟面在 clock 锚点上（中心 7×7 亮像素 ≥ 25）', 0 if int((P.lum(face) > 130).sum()) >= 25 else 1)
    sx, sy = ANCHORS['skull']
    deer = a[sy - 8:sy + 6, sx - 5:sx + 6, :3]
    ex.checked('skull 锚点就在鹿头上（鹿毛色像素 ≥ 40）', 0 if int(((deer[..., 0] > deer[..., 2] + 20)).sum()) >= 40 else 1)
    ex.checked('柜台正面图层（key counter）和底图那一截一模一样（打开 / 关上画面不变）',
               BJ.ndiff(compose(0, 0.0, {}), compose(0, 0.0, {'counter': True})))
    mean, std = P.check_walk_flat(ex, R['room'], WALK, '旅馆大堂')
    ex.note('可走带 y148–176 亮度均值 %.0f 标准差 %.1f' % (mean, std))
    ex.checked('可走带够亮，人物看得清（均值 %.0f ≥ 60）' % mean, 0 if mean >= 60 else 1)
    nm = P.lum(a[..., :3].astype(np.float32))
    ex.note('可走带后面 y108–147 亮度均值 %.0f 标准差 %.1f' % (nm[108:148].mean(), nm[108:148].std()))
    P.check_export_vs_compose(ex, BJ, st, R['layers'], R['fg'], '旅馆大堂', (0,), (0.0, 0.5, 1.25, 9.0),
                              [{}, {'fog': True}, {'counter': True}, allon])


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch5', 'enya_inn_dev')
    os.makedirs(od, exist_ok=True)
    compose(0, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'solo.png'))
    compose(0, 0.5, {'fog': True}).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'solo_fog.png'))
    print('ok')
