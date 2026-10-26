# -*- coding: utf-8 -*-
r"""mansion_hall —— 第11章「DIO 的馆」一楼大厅（地图 hall_ch11：11-10 看不见的虚空 / 11-12 阳光 / 11-13 光柱里的两个人；
也是第10章回忆（地图 flashback_ch10）里 DIO 坐在楼梯上的那个地方，剧情给它加 sepia 滤镜）。
2026-10-20 mansion 组按体验版精度从头画（旧稿是 later_stages 里的原工程 _hall_static）。零件在 mansion_parts.py，
大厅专用的（石柱 / 壁炉 / 吊灯 / 楼梯 / 破洞）直接写在本文件里，不动共用零件。

320 单屏，ground 154（柱脚），可走带 y 148–174；侧视平视；馆里偏暗，壁炉的火和吊灯是仅有的暖光，窗被黑布封死。
竖向：天花 0–3、檐口 4–11、石墙 12–115（方整石块）、腰线 116–119、护墙板 120–137、踢脚板 138–142、
地面 143–179（暗色大理石棋盘格，中间一条红地毯 156–171）。
从左到右（世界坐标）：
  x 1–20     左端一扇尖拱木门（从走廊 / 幻觉走廊进来的门）；地毯从屏幕左边一直铺到右边
  x 23–37    柱 a（anchors.pillar_a [30,154]）：14 px 宽的整块大理石柱身（y 27–142，中段什么装饰都没有——
             剧情会在这里刻半圆缺口），上有柱头（y 12–26），下有柱础（y 143–154）
  x 38–51    暗紫的旗帜（金边、金菱形）；旗帜下面 x 45 一只青瓷花瓶 + 枯玫瑰
  x 53–96    壁炉（anchors.fireplace [75,142]）：石砌烟囱墙 + 家徽 + 壁炉台（台上两支烛台、一座小金钟）+ 尖拱炉膛
             （两根铁柴架、两段木柴、炭火 + 火苗 strip，火光会呼吸）+ 炉前石板；这是整座大厅最亮的暖光
  x 98–109   旗帜；旗帜下面 x 104 一只包铁皮的旧木箱
  x 111–125  柱 b（anchors.pillar_b [118,154]）；柱头右边垂下一只小蜘蛛
  x 126–194  DIO 的肖像（anchors.portrait [160,80]，金框 35×47、红眼睛偶尔转一下）+ 两侧壁烛台 + 画下面的条案
             （两支烛台、醒酒器、盛着暗红酒的高脚杯、一本合上的书）；吊灯（anchors.chandelier [160,30]）悬在正中，
             8 支蜡烛的火苗 strip + 水晶轮流闪
  x 195–209  柱 c（anchors.pillar_c [202,154]：阿布德尔 −40、波鲁纳雷夫 −10、伊奇 +14；瓦尼拉从虚空里出来落在 +13）
  x 210–224  落地三头烛台（x 217，在墙脚、不挡可走带）
  x 219–267  楼梯平台上方的高窗（黑布封死 + 两根木板 + 一线光）+ 两边的丝绒帘 + 帘头
  x 236–319  楼梯：从右下角（x 319）往左上走 7 级（每级 9 × 5 px）到平台（y 113）；踏面铺红地毯，梯帮是比墙亮一档的石块，
             梯帮下沿往下是楼梯底下的暗处，平台下面一扇小木门；平台上一座三头烛台，楼梯脚（x 316）一根望柱 + 灯笼。
             anchors.stairs_up [300,160]：站在楼梯前；anchors.dio_seat [306,143]：第10章回忆里 DIO 的 dio.sit_back
             的 pivot——屁股坐在第 2 级（x 302–311、顶 y 138）、脚踩第 1 级（顶 y 143），腿朝右伸下去（回忆里荷尔·荷斯
             站在左边的地上，枪口抬起来对着他）
  x 268–312  key breach：墙上一个被抹掉的球形大洞（anchors.breach [290,100]，半径 22，透出开罗的白天），圆得像用圆规画的，
             洞沿有 3 px 的切面（下半亮）和几道放射的裂缝；柱 d 在洞前面，把洞挡住中间 14 px（柱子在前、洞在后）；
             楼梯踏面上掉了几块碎石
  x 283–297  柱 d（anchors.pillar_d [290,154]）
  x 254–294  key beam：从洞里斜斜照下来的阳光光柱（中心线从洞下沿 (289,104) 到地上 (274,164)，洞本身不盖光），
             落地中心 x 274，地上一块暖白的光斑（半宽 19、高 24，边缘一圈亮边；anchors.beam_zone [256,148,292,174]：
             瓦尼拉被打进这个范围 = 离中心 18 px 内就算进光）
图层（从后往前）：
  base     pano k 1            整张底图（打好光，不透明）
  breach   pano k 1  key breach  洞（天空 + 屋顶，发光）+ 洞沿 + 白天的光洒在洞周围的墙 / 楼梯 / 柱 d 上（只留和底图不同的像素）
  beam     pano k 1  key beam    光柱：空气里的光（10 档抖动的暖色亮带）+ 三道光线 + 地上的光斑（只留和 breach 状态不同的像素）
  fire     strip 8 帧 @8 fps     壁炉：火光的呼吸（炉口周围的墙 / 柱 / 地，±14 %）+ 三簇火舌 + 炭火明暗 + 往上飘的火星
  chand    strip 8 帧 @8 fps     吊灯的 8 支蜡烛 + 水晶轮流闪一下
  mantel   strip 8 帧 @8 fps     壁炉台上的两支烛台
  sconce   strip 8 帧 @8 fps     两个壁烛台 + 条案上的两支烛台 + 落地烛台的 3 支 + 平台烛台的 3 支
  lantern  strip 8 帧 @8 fps     楼梯脚灯笼里的火苗（发光，灯笼本身在底图里）
  eyes     strip 8 帧 @4 fps     肖像的眼睛（红眼珠偶尔转、偶尔眨）+ 金框上走过的一粒高光
  spider   strip 8 帧 @4 fps     柱 b 的柱头下面垂着一只小蜘蛛，丝一伸一缩
  motes    strip 8 帧 @4 fps  key beam  光柱里飘的浮尘
  rays     strip 8 帧 @4 fps  key beam  光柱里三道光线一明一暗
锚点（素材总表定稿，值不改）：pillar_a [30,154] / pillar_b [118,154] / pillar_c [202,154] / pillar_d [290,154]、
  pillar_tops（每根柱子 [上端 y, 下端 y] = [12,154]）、beam_x [250,166]、breach [290,100]、portrait [160,80]、
  void_path [152,160,168]、stairs_up [300,160]；
  另外多导出：pillar_shaft [27,142]（柱身只有素石、没装饰的那一段：刻缺口随便刻）、pillar_w 14、
  beam_center [274,164]、beam_zone [256,148,292,174]（光斑的落地范围：中心 ± 18，剧情判“进光”用它的 x0 / x1）、beam_box（光斑 + 光柱的外框）、breach_r 22、dio_seat、stair_steps、
  fireplace、chandelier、door_left。
key：breach（0 / 1）、beam（0 / 1）。两个都开才是 11-12 之后的样子。
单独运行：python -B tools/bg_new/mansion_hall.py → tools/bg_new/_preview/ch11/after/mansion_hall_solo.png
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
from scipy import ndimage  # noqa: E402

from engine.core import hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _parts():
    """mansion_parts（importlib 按路径加载，同 mansion_exterior）。"""
    key = 'bg_new_mansion_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'mansion_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


M = _parts()
dk, lt, hl, vl, px, rect = M.dk, M.lt, M.hl, M.vl, M.px, M.rect
C = M.C
H = M.H
N8 = M.N8
FPS = M.FPS_SLOW
FPS_FIRE = M.FPS_FIRE
GOLD, IRON, WOOD, STONE = M.GOLD, M.IRON, M.WOOD, M.STONE

PW = 320
GROUND = 154
WALK = (148, 174)
PILLARS = (30, 118, 202, 290)
CAP_TOP = 12                                    # 柱头最上面一行
SHAFT = (27, 142)                               # 柱身（整块石头、没装饰）的上下端
WALL_BASE = 142                                 # 踢脚板下沿 = 墙脚
FIRE_X = 75
PORTRAIT_BOX = (143, 57, 177, 103)              # 画框（35×47，中心正好 (160, 80)）
HOLE = (290, 100, 22)                           # 破洞：圆心、半径
BEAM_TOP = (289, 104)                           # 光柱从洞里出来的位置（中心）
BEAM_FOOT = (274, 164)                          # 光斑中心
BEAM_RANGE = (256, 292)                         # 落地中心 ± 18
STEP_W, STEP_H, N_STEPS = 9, 5, 7
DIO_SEAT = (306, 143)
CHAND = (160, 30)

# ---- 调色
CHIM = dict(hi=(156, 142, 142), lt=(128, 116, 120), md=(102, 92, 100), dk=(76, 68, 80), dd=(46, 40, 54))   # 烟囱的石头：比墙暖、亮一档
MBL = dict(hi=(206, 200, 216), lt=(174, 166, 190), md=(140, 132, 160), dk=(104, 96, 124), dd=(66, 60, 86))  # 柱子：冷灰带紫的大理石
FLOOR_L, FLOOR_D = (96, 88, 110), (70, 62, 84)                   # 棋盘格两色：对比压低（可走带要平：亮度差 ≈ 26，打光后更小）
RUG = dict(base=(122, 26, 40), lt=(146, 40, 52), dk=(88, 14, 30), dd=(56, 8, 22), gold=(196, 150, 68), gold_d=(140, 100, 46))
SOOT = (26, 18, 22)
T_AMB = (0.72, 0.72, 1.14)                      # 大厅的环境光：偏紫、很暗
T_FLOOR = (1.08, 0.94, 0.94)
T_DAYB = (1.02, 1.12, 1.30)                     # 洞里透进来的白天（偏冷白）
T_SUN2 = (1.34, 1.14, 0.78)                     # 光柱本身（暖）
SUN_ADD = (255, 226, 164)                       # 光柱的“空气里的光”（加色）

ANCHORS = {
    'pillar_a': [30, 154], 'pillar_b': [118, 154], 'pillar_c': [202, 154], 'pillar_d': [290, 154],
    'pillar_tops': [[CAP_TOP, 154]] * 4,
    'beam_x': [250, 166], 'breach': [290, 100], 'portrait': [160, 80],
    'void_path': [152, 160, 168], 'stairs_up': [300, 160],
}
REQUIRED = tuple(ANCHORS)
STAND = ('pillar_a', 'pillar_b', 'pillar_c', 'pillar_d', 'beam_x', 'stairs_up')


# ============================================================ 零件：石柱 / 柱头 / 柱础
def pillar(cv, cx, seed):
    """整块大理石柱：柱身 14 px（x−7..x+6，圆柱的明暗 5 档：左边亮、右边暗）+ 细细的纵向纹路；柱头（方顶板 + 内弧的圆盘 + 颈环）、
    柱础（圆环 + 方基座）。柱身 y 27–142 不放任何装饰（刻缺口的地方）。"""
    d = cv.d
    x0, x1 = cx - 7, cx + 6
    s0, s1 = SHAFT
    stops = [MBL['hi'], MBL['lt'], MBL['md'], MBL['dk'], MBL['dd']]
    nz = A._fbm(16, s1 - s0 + 9, 7, seed=seed)[:, :]
    for i, x in enumerate(range(x0, x1 + 1)):
        u = i / 13.0
        k = u * 4.0
        a_, b_ = stops[int(k)], stops[min(4, int(k) + 1)]
        base = mix(a_, b_, k - int(k))
        for y in range(s0, s1 + 1):
            n = nz[y - s0 + 4, i + 1]
            c = base
            if abs(n - 0.5) < 0.026:                                   # 纵向的石纹：一道道发暗的细纹
                c = dk(base, 0.82)
            elif hash01(seed, x, y) < 0.03:                            # 斑点
                c = dk(base, 0.93)
            px(d, x, y, c)
    vl(d, x0 - 1, s0, s1, M.INK)
    vl(d, x1 + 1, s0, s1, M.INK)
    # 柱头：方顶板
    rect(d, cx - 10, CAP_TOP, cx + 10, CAP_TOP + 3, MBL['md'], outline=M.INK)
    hl(d, cx - 9, cx + 9, CAP_TOP + 1, MBL['hi'])
    hl(d, cx - 9, cx + 9, CAP_TOP + 2, MBL['lt'])
    vl(d, cx - 9, CAP_TOP + 1, CAP_TOP + 2, MBL['hi'])
    hl(d, cx - 9, cx + 9, CAP_TOP + 3, MBL['dk'])
    # 圆盘（向下收窄）+ 一圈叶饰
    for k, y in enumerate(range(CAP_TOP + 4, CAP_TOP + 13)):
        hw = 9 - int(round(2.2 * k / 8.0))
        for x in range(cx - hw, cx + hw + 1):
            u = (x - (cx - hw)) / max(1, 2 * hw)
            c = MBL['lt'] if u < 0.28 else (MBL['md'] if u < 0.62 else MBL['dk'])
            px(d, x, y, c)
        px(d, cx - hw - 1, y, M.INK)
        px(d, cx + hw + 1, y, M.INK)
    for k, lx in enumerate(range(cx - 7, cx + 8, 3)):                  # 叶饰：小 V 形的暗纹
        px(d, lx, CAP_TOP + 6, MBL['dd'])
        px(d, lx + 1, CAP_TOP + 7, MBL['dd'])
        px(d, lx - 1, CAP_TOP + 7, MBL['dd'])
        px(d, lx, CAP_TOP + 8, MBL['dk'])
    hl(d, cx - 8, cx + 8, CAP_TOP + 13, MBL['hi'])                     # 颈环
    hl(d, cx - 8, cx + 8, CAP_TOP + 14, MBL['dd'])
    # 柱础：圆环 + 方基座
    hl(d, cx - 8, cx + 8, 143, MBL['lt'])
    hl(d, cx - 8, cx + 8, 144, MBL['dk'])
    px(d, cx - 8, 143, MBL['hi'])
    rect(d, cx - 10, 145, cx + 10, 154, MBL['md'], outline=M.INK)
    hl(d, cx - 9, cx + 9, 146, MBL['hi'])
    vl(d, cx - 9, 146, 153, MBL['lt'])
    vl(d, cx + 9, 147, 153, MBL['dk'])
    hl(d, cx - 9, cx + 9, 153, MBL['dd'])
    for x in range(cx - 8, cx + 9, 5):                                 # 基座上的一两处缺角
        if hash01(seed, x, 1) < 0.3:
            px(d, x, 148, MBL['dk'])


# ============================================================ 零件：壁炉
def fireplace(cv, cx):
    """石砌烟囱墙（中间一块带家徽的嵌板）+ 壁炉台（齿饰）+ 两根石柱腿 + 尖拱炉膛（砖缝、铁柴架、两段木柴、炭火）+ 炉前石板。
    返回 dict(box=炉膛框, coals=[(x, y)], mantel_y=台面 y)。"""
    d = cv.d
    bx0, bx1 = cx - 22, cx + 21
    M.ashlar(cv, (bx0, CAP_TOP, bx1, 95), pal=CHIM, bw=22, bh=11, seed=3, chips=True)
    vl(d, bx0, CAP_TOP, 95, CHIM['hi'])
    vl(d, bx1, CAP_TOP, 95, CHIM['dd'])
    vl(d, bx0 - 1, CAP_TOP, 100, M.INK)
    vl(d, bx1 + 1, CAP_TOP, 100, M.INK)
    # 嵌板（凹进去的一块，四周一圈线脚）+ 家徽
    px0, px1, py0, py1 = bx0 + 5, bx1 - 5, 30, 90
    rect(d, px0, py0, px1, py1, dk(CHIM['md'], 0.78), outline=CHIM['dd'])
    hl(d, px0 + 1, px1 - 1, py0 + 1, CHIM['dk'])
    vl(d, px0 + 1, py0 + 1, py1 - 1, CHIM['dk'])
    hl(d, px0 + 1, px1 - 1, py1 - 1, CHIM['hi'])
    vl(d, px1 - 1, py0 + 1, py1 - 1, CHIM['lt'])
    M.coat_of_arms(cv, cx, 44)
    for k in range(3):                                                 # 家徽下面一排小盾 / 菱形浮雕
        yy = 76 + k * 4
        for dx in (-9, -3, 3, 9):
            px(d, cx + dx, yy, CHIM['hi'])
            px(d, cx + dx + 1, yy + 1, CHIM['dd'])
    # 壁炉台（y 96–100）+ 齿饰 + 托架
    rect(d, cx - 27, 96, cx + 26, 100, CHIM['md'], outline=M.INK)
    hl(d, cx - 26, cx + 25, 97, CHIM['hi'])
    hl(d, cx - 26, cx + 25, 98, CHIM['lt'])
    hl(d, cx - 26, cx + 25, 100, CHIM['dk'])
    for x in range(cx - 26, cx + 26, 3):
        px(d, x, 101, CHIM['dd'])
        px(d, x + 1, 101, CHIM['lt'])
    for sx in (cx - 24, cx + 22):                                      # 台下的托架（卷涡）
        vl(d, sx, 101, 104, CHIM['md'])
        px(d, sx + (1 if sx < cx else -1), 104, CHIM['dk'])
    # 两根石柱腿（方整石块）
    for (jx0, jx1) in ((cx - 22, cx - 15), (cx + 14, cx + 21)):
        M.ashlar(cv, (jx0, 102, jx1, WALL_BASE), pal=CHIM, bw=8, bh=10, seed=jx0, chips=False)
        vl(d, jx0, 102, WALL_BASE, CHIM['hi'])
        vl(d, jx1, 102, WALL_BASE, CHIM['dd'])
    # 炉膛：尖拱
    ox0, ox1 = cx - 14, cx + 13
    top = M.arch_rows(ox1 - ox0 + 1, 11, pointed=True)
    box_top = 200
    for i in range(ox1 - ox0 + 1):
        yt = 113 - int(round(top[i]))
        box_top = min(box_top, yt)
        for y in range(yt, WALL_BASE):
            c = SOOT
            if y % 4 == 0 or (((ox0 + i) + (y // 4) * 4) % 8 == 0):    # 炉膛里的砖缝
                c = dk(SOOT, 0.6)
            elif y % 4 == 1:
                c = lt(SOOT, 0.05)
            px(d, ox0 + i, y, c)
        px(d, ox0 + i, yt - 1, CHIM['dd'])                              # 拱圈：两圈楔形石
        px(d, ox0 + i, yt - 2, CHIM['hi'] if (ox0 + i) % 4 < 2 else CHIM['lt'])
        px(d, ox0 + i, yt - 3, CHIM['md'] if (ox0 + i) % 4 < 2 else CHIM['dk'])
    px(d, cx, box_top - 4, CHIM['hi'])                                  # 拱心石
    px(d, cx - 1, box_top - 3, CHIM['hi'])
    px(d, cx + 1, box_top - 3, CHIM['lt'])
    # 炉底：灰 + 炭
    rect(d, ox0, 139, ox1, WALL_BASE - 1, (54, 44, 48))
    for x in range(ox0, ox1 + 1):
        if hash01(cx, x, 2) < 0.5:
            px(d, x, 139, (92, 80, 84))
    # 铁柴架（两根立柱带球顶 + 横杆）
    for ax in (cx - 11, cx + 10):
        vl(d, ax, 128, 140, IRON['md'])
        vl(d, ax - 1 if ax < cx else ax + 1, 134, 140, IRON['dk'])
        px(d, ax, 127, IRON['hi'])
        px(d, ax - 1, 128, IRON['hi'])
        px(d, ax + 1, 128, IRON['md'])
        hl(d, ax - 1 if ax > cx else ax, ax if ax > cx else ax + 1, 136, IRON['hi'])
    # 两段木柴（下面一根、上面一根），断面有年轮
    for (lx0, lx1, ly) in ((cx - 10, cx + 9, 137), (cx - 7, cx + 6, 133)):
        rect(d, lx0, ly, lx1, ly + 3, (88, 52, 34))
        hl(d, lx0, lx1, ly, (126, 80, 50))
        hl(d, lx0, lx1, ly + 3, (46, 26, 20))
        for x in range(lx0 + 2, lx1, 4):
            px(d, x, ly + 1, (62, 36, 26))
        px(d, lx0, ly + 1, (190, 150, 100))                             # 断面
        px(d, lx0, ly + 2, (150, 110, 70))
        px(d, lx1, ly + 1, (190, 150, 100))
    # 炭火：发光（emissive），明暗在 strip 里再跳
    coals = []
    for x in range(ox0 + 3, ox1 - 2):
        for y in range(138, 142):
            r = hash01(cx, x, y, 5)
            if r < 0.34 and not (y == 138 and r > 0.2):
                c = (232, 92, 38) if r < 0.14 else (176, 52, 30)
                cv.glow_px(x, y, c)
                coals.append((x, y))
    # 炉前石板
    rect(d, cx - 31, WALL_BASE + 1, cx + 31, 147, CHIM['md'], outline=M.INK)
    hl(d, cx - 30, cx + 30, WALL_BASE + 2, CHIM['hi'])
    hl(d, cx - 30, cx + 30, 146, CHIM['dk'])
    for x in range(cx - 30, cx + 31, 10):
        vl(d, x, WALL_BASE + 3, 146, CHIM['dd'])
    # 炉口的一圈烟熏：拱圈上方的石头发黑
    M.soot(cv, cx, 80, 98, w=14, k=0.78, seed=5)
    return dict(box=(ox0, box_top, ox1, WALL_BASE - 1), coals=coals)


def mantel_candle(cv, x, y):
    """壁炉台上的矮黄铜烛台（底在 y）：底盘、立杆、托盘、蜡烛。返回火苗底。"""
    d = cv.d
    hl(d, x - 2, x + 2, y, GOLD['dk'])
    hl(d, x - 1, x + 1, y - 1, GOLD['md'])
    vl(d, x, y - 4, y - 2, GOLD['md'])
    px(d, x - 1, y - 3, GOLD['hi'])
    hl(d, x - 2, x + 2, y - 5, GOLD['lt'])
    px(d, x - 2, y - 5, GOLD['hi'])
    return M.candle(cv, x, y - 6, h=5, seed=x)


def mantel_clock(cv, cx, y):
    """壁炉台上的小金钟（y = 底）：拱顶的黄铜壳、白表盘（四个刻度，指针停在 12 点——馆里的时间是 DIO 的）、两只小脚。"""
    d = cv.d
    rect(d, cx - 5, y - 9, cx + 4, y - 1, GOLD['dk'], outline=M.INK)
    hl(d, cx - 3, cx + 2, y - 10, M.INK)
    hl(d, cx - 4, cx + 3, y - 9, GOLD['md'])
    px(d, cx - 4, y - 8, GOLD['hi'])
    px(d, cx, y - 11, GOLD['hi'])                                            # 顶上的小球
    d.ellipse((cx - 3, y - 8, cx + 2, y - 2), fill=C((226, 224, 214)), outline=C(GOLD['md']))
    for (dx, dy) in ((0, -3), (2, -1), (0, 1), (-2, -1)):                    # 12 / 3 / 6 / 9 点
        px(d, cx + dx, y - 5 + dy + 0, (40, 30, 30))
    px(d, cx, y - 5, (40, 30, 30))
    px(d, cx, y - 6, (40, 30, 30))
    px(d, cx - 4, y, GOLD['dk'])
    px(d, cx + 3, y, GOLD['dk'])


def chest(cv, cx, yf):
    """靠墙的旧木箱（宽 14、高 10，底在 yf）：圆弧盖、两道铁箍、一把锁。"""
    d = cv.d
    x0, x1 = cx - 7, cx + 6
    rect(d, x0, yf - 9, x1, yf, WOOD['md'], outline=M.INK)
    hl(d, x0 + 1, x1 - 1, yf - 8, WOOD['hi'])
    hl(d, x0 + 1, x1 - 1, yf - 5, WOOD['dk'])                                 # 盖和箱身的缝
    for bx in (x0 + 3, x1 - 3):
        vl(d, bx, yf - 8, yf - 1, IRON['md'])
        vl(d, bx - 1, yf - 8, yf - 1, IRON['hi'])
        px(d, bx, yf - 5, IRON['dd'])
    px(d, (x0 + x1) // 2, yf - 5, GOLD['md'])
    px(d, (x0 + x1) // 2, yf - 4, GOLD['dk'])
    hl(d, x0 + 1, x1 - 1, yf - 1, WOOD['dd'])


# ============================================================ 零件：旗帜 / 条案上的小物件 / 吊灯 / 楼梯
def banner(cv, x0, x1, y0, y1, seed=0):
    """柱间的旗帜：金色横杆（两头带球）+ 暗紫的绸（竖褶、金边）+ 燕尾下摆 + 金菱形纹章 + 底边金流苏。"""
    d = cv.d
    P = dict(hi=(120, 44, 118), lt=(96, 30, 96), md=(72, 20, 74), dk=(52, 12, 56), dd=(32, 6, 38))
    hl(d, x0 - 2, x1 + 2, y0, GOLD['hi'])
    hl(d, x0 - 2, x1 + 2, y0 + 1, GOLD['dk'])
    px(d, x0 - 3, y0, GOLD['lt'])
    px(d, x1 + 3, y0, GOLD['lt'])
    for x in range(x0, x1 + 1):
        u = (x - x0) / max(1, x1 - x0)
        notch = int(round(5 * (1 - abs(2 * u - 1)))) if u > 0 else 0
        yb = y1 - 5 + notch if True else y1
        for y in range(y0 + 2, yb + 1):
            ph = ((x - x0) + (hash01(seed, 1) * 3)) % 4
            c = P['lt'] if ph < 1.2 else (P['md'] if ph < 3 else P['dk'])
            if x in (x0, x1) or y == y0 + 2:
                c = GOLD['md'] if (y + x) % 2 else GOLD['dk']
            px(d, x, y, c)
        px(d, x, yb, GOLD['lt'] if x % 2 else GOLD['dk'])               # 下摆的金边
        if x % 3 == 0:
            vl(d, x, yb + 1, yb + 2, GOLD['md'])                       # 流苏
    cxm = (x0 + x1) // 2
    my = y0 + (y1 - y0) // 2 - 2
    for k in range(5):                                                 # 金菱形
        hl(d, cxm - (2 - abs(k - 2)), cxm + (2 - abs(k - 2)), my + k - 2, GOLD['lt'] if k < 3 else GOLD['md'])
    px(d, cxm, my, P['dd'])
    vl(d, x0 - 1, y0 + 1, y1 - 3, M.INK)
    vl(d, x1 + 1, y0 + 1, y1 - 3, M.INK)


def table_things(cv, x0, x1, top):
    """条案台面上的小物件（台面上沿 y = top）：左边一个醒酒器，右边一个盛着暗红酒的高脚杯，中间一本合上的书。"""
    d = cv.d
    gx = x0 + 6                                                        # 醒酒器
    rect(d, gx - 2, top - 7, gx + 2, top - 1, (46, 22, 34), outline=(86, 60, 80))
    vl(d, gx, top - 11, top - 8, (86, 60, 80))
    hl(d, gx - 1, gx + 1, top - 12, (120, 96, 110))
    px(d, gx - 2, top - 6, (184, 120, 140))
    wx = x1 - 6                                                        # 高脚杯
    rect(d, wx - 2, top - 7, wx + 2, top - 4, (150, 40, 56), outline=(146, 150, 170))
    px(d, wx - 2, top - 7, (230, 230, 240))
    vl(d, wx, top - 3, top - 1, (146, 150, 170))
    hl(d, wx - 2, wx + 2, top - 1, (146, 150, 170))
    bx = (x0 + x1) // 2 - 4                                            # 书
    rect(d, bx, top - 3, bx + 8, top - 1, (60, 42, 70), outline=M.INK)
    hl(d, bx + 1, bx + 7, top - 3, (150, 120, 70))


def chandelier(cv, cx, cy):
    """吊灯（侧视）：链子从天花垂下来、铁圈（前沿弧线带铜光）、8 根辐条、圈上 8 个烛杯 + 蜡烛、下面一圈水晶坠和中间的尖饰。
    返回 8 个火苗底的坐标。"""
    d = cv.d
    for y in range(0, cy - 12):                                        # 链子：一节亮一节暗
        px(d, cx, y, IRON['hi'] if y % 3 == 0 else IRON['md'])
        if y % 3 == 1:
            px(d, cx + 1, y, IRON['dk'])
    rect(d, cx - 3, 0, cx + 3, 1, GOLD['md'])                            # 顶上的吊盘
    hl(d, cx - 3, cx + 3, 0, GOLD['hi'])
    rx, ry = 26, 4
    for k in range(0, 360, 4):                                         # 铁圈：前沿一整圈椭圆（2 px 粗），上半亮、下半暗
        a = math.radians(k)
        x, y = round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a))
        front = math.sin(a) > 0
        px(d, x, y, GOLD['hi'] if (front and k % 8 == 0) else (GOLD['lt'] if front else IRON['md']))
        px(d, x, y + 1, GOLD['dk'] if front else IRON['dk'])
    for k in range(-3, 4):                                             # 辐条：从链子下端的小圈到铁圈
        x1 = cx + int(round(k * rx / 3.4))
        n = 14
        for s in range(n + 1):
            u = s / n
            x = round(cx + (x1 - cx) * u)
            y = round(cy - 12 + (cy + ry * 0.6 * (1 - (k / 3.4) ** 2) ** 0.5 - (cy - 12)) * u)
            if hash01(cx, k, s) < 0.9:
                px(d, x, y, IRON['md'] if k % 2 else IRON['dk'])
    d.ellipse((cx - 4, cy - 15, cx + 4, cy - 10), outline=C(GOLD['md']), fill=C(IRON['dk']))
    px(d, cx - 2, cy - 14, GOLD['hi'])
    flames = []
    cv.chand_crystals = []
    for k, off in enumerate((-23, -17, -9, -3, 3, 9, 17, 23)):
        x = cx + off
        y = cy + int(round(ry * (1 - (off / float(rx)) ** 2) ** 0.5)) - 1
        rect(d, x - 1, y, x + 1, y + 1, GOLD['md'])                     # 烛杯
        px(d, x - 1, y, GOLD['hi'])
        flames.append(M.candle(cv, x, y - 1, h=5, seed=k + 40))
    for off in range(-22, 23, 4):                                      # 水晶坠
        x = cx + off
        y = cy + int(round(ry * (1 - (off / float(rx)) ** 2) ** 0.5)) + 2
        px(d, x, y, (200, 210, 240))
        px(d, x, y + 1, (150, 164, 214))
        if off % 8 == 0:
            px(d, x, y + 2, (240, 244, 255))
            cv.chand_crystals.append((x, y + 1))
    vl(d, cx, cy + 5, cy + 13, GOLD['md'])                              # 中间的尖饰
    vl(d, cx - 1, cy + 6, cy + 10, GOLD['hi'])
    d.ellipse((cx - 2, cy + 8, cx + 2, cy + 12), fill=C(GOLD['lt']), outline=C(GOLD['dk']))
    px(d, cx, cy + 14, (240, 244, 255))
    return flames


def stair_tops():
    """每级踏面 (x0, x1, y_top)：第 0 级在最右（贴着屏幕右边），往左一级级升高，第 6 级 = 平台的右端。"""
    out = []
    for i in range(N_STEPS):
        x1 = PW - 1 - STEP_W * i
        out.append((x1 - STEP_W + 1, x1, 148 - STEP_H * (i + 1)))
    return out


STAIR = dict(hi=(190, 174, 170), lt=(158, 142, 146), md=(128, 114, 124), dk=(94, 82, 98), dd=(56, 48, 66))   # 楼梯的石头：比墙亮一档、偏暖，轮廓才分得开


def stairs(cv):
    """楼梯（侧面）：下面是石砌的梯帮（方整石块，比墙亮），每级踏面铺一层红地毯（3 px），踏口一粒铜压毯杆，毯子顺着右边的竖面垂下去；
    平台一块厚石板 + 下面的石墙和一个小壁龛。从右下角往左上升，平台在 x 236–265、y 113。踏面和梯帮之间一道 1 px 墨线。"""
    d = cv.d
    tops = stair_tops()
    lx0, ly0 = 236, 113
    sub = M.Canvas(PW - lx0, 148 - ly0)
    M.ashlar(sub, (0, 0, PW - lx0 - 1, 148 - ly0 - 1), pal=STAIR, bw=24, bh=9, seed=11, chips=True)
    prof = np.zeros((148 - ly0, PW - lx0), bool)
    for x in range(lx0, PW):
        yt = ly0
        for (a_, b_, y) in tops:
            if a_ <= x <= b_:
                yt = y
        prof[yt - ly0:, x - lx0] = True
    a = np.array(sub.im).astype(np.float32)
    ytop = np.array([ly0 + int(np.argmax(prof[:, c])) for c in range(prof.shape[1])])
    yy_ = np.arange(prof.shape[0])[:, None] + ly0
    under = yy_ >= (ytop[None, :] + 9)                                      # 梯帮面 9 px 以下 = 楼梯底下，背光、发暗
    a[..., :3] = np.where(under[..., None], a[..., :3] * np.array((0.46, 0.46, 0.56)), a[..., :3])
    a[~prof, 3] = 0
    cv.im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'), (lx0, ly0))
    for c in range(prof.shape[1]):                                          # 梯帮面下沿的一道暗线（斜着走）
        yb = ytop[c] + 9
        if yb < 147:
            px(d, lx0 + c, yb, STAIR['dd'])
    for (a_, b_, y) in tops:
        hl(d, a_, b_, y - 1, M.INK)                                       # 踏面上沿的墨线
        hl(d, a_, b_ - 1, y, RUG['lt'])                                   # 地毯：亮 / 中 / 暗 三行
        hl(d, a_, b_ - 1, y + 1, RUG['base'])
        hl(d, a_, b_ - 1, y + 2, RUG['dk'])
        vl(d, b_, y, y + STEP_H - 1, RUG['dk'])                            # 竖面：毯子垂下来
        px(d, b_, y, RUG['base'])
        px(d, b_ - 1, y + 1, GOLD['hi'])                                   # 压毯杆（踏口）
        px(d, b_, y + 1, GOLD['md'])
        vl(d, b_ + 1, y - 1, y + STEP_H, M.INK)                            # 竖面右边的墨线
    # 平台：厚石板（顶面亮、前沿暗）
    px1 = tops[-1][0] - 1
    rect(d, lx0, ly0 - 1, px1, ly0 + 3, STAIR['lt'], outline=M.INK)
    hl(d, lx0 + 1, px1 - 1, ly0, STAIR['hi'])
    hl(d, lx0 + 1, px1 - 1, ly0 + 3, STAIR['dk'])
    vl(d, lx0, ly0 - 1, 147, M.INK)
    M.mul_box(cv.im, (lx0 + 1, ly0 + 4, px1, ly0 + 9), (0.72, 0.72, 0.8))   # 板下的阴影
    keep = cv.im.crop((236, 149, 266, 153))                                    # 小门太矮，锁孔会画到门脚下面的地面上：画完把那几行地面还原
    M.gothic_door(cv, 244, 126, 12, 21, kind='arch', seed=13)                 # 平台底下的小木门（楼梯下的储物间）
    cv.im.paste(keep, (236, 149))
    M.mul_box(cv.im, (lx0 + 1, 145, PW - 1, 147), (0.78, 0.78, 0.86))        # 梯帮脚下的暗
    # 楼梯在后面的墙上落一道影子（平台上沿到顶、墙上），让它从墙里“凸”出来
    M.mul_box(cv.im, (lx0 - 3, ly0 - 12, lx0 - 1, 147), (0.7, 0.7, 0.78))


def newel_lantern(cv, cx, y_step):
    """楼梯脚的望柱（深色木头、顶上一粒铜球）+ 柱顶一盏小铁灯笼（四面玻璃、里面一朵火苗）。y_step = 柱子立在的那级踏面的 y。
    返回灯笼里火苗的位置（strip 里画火苗）。"""
    d = cv.d
    top = y_step - 15
    rect(d, cx - 1, top, cx + 1, y_step - 1, WOOD['md'], outline=M.INK)
    vl(d, cx - 1, top + 1, y_step - 2, WOOD['hi'])
    hl(d, cx - 1, cx + 1, top + 5, WOOD['dd'])
    # 灯笼：铁框 + 玻璃（发暖光）
    lx0, lx1, ly0, ly1 = cx - 3, cx + 3, top - 8, top - 1
    rect(d, lx0, ly0, lx1, ly1, (150, 96, 40), outline=M.INK)
    rect(d, lx0 + 1, ly0 + 1, lx1 - 1, ly1 - 1, (232, 164, 76))
    for (x, y) in ((lx0 + 1, ly0 + 1), (lx0 + 2, ly0 + 1), (lx0 + 1, ly0 + 2)):
        cv.glow_px(x, y, (255, 226, 150))
    cv.glow_rect(lx0 + 2, ly0 + 2, lx1 - 2, ly1 - 2, (250, 190, 90))
    vl(d, cx, ly0 + 1, ly1 - 1, IRON['md'])                                    # 灯笼的中间一道铁条
    hl(d, lx0 - 1, lx1 + 1, ly0 - 1, IRON['md'])                               # 帽
    px(d, cx, ly0 - 2, IRON['hi'])
    px(d, cx, ly0 - 3, GOLD['hi'])
    return (cx, ly0 + 5)


# ============================================================ 破洞（key breach）
def hole_layer():
    """球形大洞里看到的外面：天空（上蓝下暖）、太阳、开罗的屋顶 / 宣礼塔 / 圆顶（偏黄的灰泥）、远处一层薄雾。
    返回 (RGBA 图, 圆心在图里的 x, y)：整个圆都是发光的。"""
    cx0, cy0, r = HOLE
    S = 2 * r + 7
    c = S // 2
    yy, xx = np.mgrid[0:S, 0:S] - c
    dist = np.hypot(xx, yy)
    arr = np.zeros((S, S, 4), np.float32)
    t = np.clip((yy + r) / (2.0 * r), 0, 1)
    sky_top, sky_mid, sky_low = np.array((112, 176, 236)), np.array((190, 222, 244)), np.array((252, 232, 196))
    sky = np.where((t < 0.55)[..., None], sky_top + (sky_mid - sky_top) * (t / 0.55)[..., None],
                   sky_mid + (sky_low - sky_mid) * ((t - 0.55) / 0.45)[..., None])
    arr[..., :3] = sky
    # 太阳 + 光晕
    sd = np.hypot(xx - 9, yy + 11)
    arr[..., :3] += (np.clip(1 - sd / 15.0, 0, 1) ** 1.4)[..., None] * np.array((60, 40, 10))
    arr[sd <= 3.6, :3] = (255, 252, 232)
    arr[..., 3] = np.where(dist <= r, 255, 0)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    roof = (226, 194, 148)
    roof_s = (198, 160, 116)
    far = (214, 204, 196)
    # 远处的一排矮楼（薄雾色）
    for (bx, bw, top) in ((-22, 9, 6), (-12, 8, 3), (-3, 10, 5), (8, 9, 2), (18, 8, 4)):
        rect(d, c + bx, c + top + 4, c + bx + bw, c + r, far)
    # 近处的屋顶：平顶楼 + 宣礼塔 + 圆顶
    for (bx, bw, top, col) in ((-24, 13, 9, roof), (-9, 12, 13, roof_s), (5, 14, 8, roof), (17, 10, 12, roof_s)):
        rect(d, c + bx, c + top, c + bx + bw, c + r, col)
        hl(d, c + bx, c + bx + bw, c + top, lt(col, 0.35))
        for wx in range(bx + 3, bx + bw - 1, 5):
            px(d, c + wx, c + top + 4, (120, 88, 66))
            px(d, c + wx, c + top + 5, (120, 88, 66))
    rect(d, c - 5, c - 7, c - 3, c + 13, (230, 214, 184))                # 宣礼塔
    vl(d, c - 5, c - 7, c + 13, (252, 240, 214))
    hl(d, c - 6, c - 2, c - 1, (170, 140, 104))
    for k in range(4):
        px(d, c - 4, c - 12 + k, (230, 214, 184))
    px(d, c - 4, c - 13, (230, 214, 184))
    px(d, c - 4, c - 14, (200, 60, 50))
    d.pieslice((c + 7, c + 3, c + 17, c + 15), 180, 360, fill=C((238, 220, 188)))   # 圆顶
    px(d, c + 12, c + 2, (200, 170, 100))
    a = np.array(im)
    a[dist > r, 3] = 0
    return Image.fromarray(a, 'RGBA'), c, c


def paint_hole(cv, cracks=True):
    """把洞画进 albedo：洞沿的切面（3 px，圆得像用圆规画的：上半暗、下半亮——洞下沿接住了外面的光）、放射的裂缝、
    楼梯上掉的碎石；洞里（天空 + 屋顶）是发光的。柱 d 之后再画，所以柱子会挡在洞前面。"""
    cx0, cy0, r = HOLE
    d = cv.d
    for y in range(cy0 - r - 4, cy0 + r + 5):
        for x in range(cx0 - r - 4, cx0 + r + 5):
            dd = math.hypot(x - cx0, y - cy0)
            if r < dd <= r + 1.2:
                px(d, x, y, M.INK)
            elif r + 1.2 < dd <= r + 3.4:
                ang = math.atan2(y - cy0, x - cx0)                      # +y = 下
                lit = 0.5 + 0.5 * math.sin(ang)                         # 下半亮
                col = mix(STONE['dk'], (222, 210, 190), lit * 0.9)
                px(d, x, y, col)
    if cracks:
        for k in range(9):                                              # 从洞沿往外裂开的细缝
            ang = math.radians(k * 40 + hrange(-14, 14, k, 1))
            L_ = int(hrange(5, 15, k, 2))
            x, y = cx0 + (r + 4) * math.cos(ang), cy0 + (r + 4) * math.sin(ang)
            for s in range(L_):
                ang += hrange(-0.35, 0.35, k, s, 3)
                x += math.cos(ang)
                y += math.sin(ang)
                xi, yi = int(round(x)), int(round(y))
                if 0 <= xi < PW and CAP_TOP <= yi < 140:
                    px(d, xi, yi, M.INK)
    im, ox, oy = hole_layer()
    cv.paste_emissive(im, cx0 - ox, cy0 - oy)


def scatter_rubble(cv):
    """楼梯踏面上掉的碎石（只在洞打开时有）：灰白的小块 + 一点点粉尘。"""
    d = cv.d
    for (a_, b_, y) in stair_tops():
        if b_ < 270:
            continue
        for k in range(2):
            x = int(hrange(a_ + 1, b_ - 1, a_, k, 1))
            if hash01(a_, k, 2) < 0.75:
                hl(d, x, x + int(hrange(0, 2, a_, k, 3)), y - 1, (186, 176, 168))
                px(d, x, y - 2, (214, 204, 196)) if hash01(a_, k, 4) < 0.4 else None


# ============================================================ 底图（albedo）
@lru_cache(maxsize=None)
def albedo(hole=False):
    """满光时的固有色：返回 (Canvas, info)。hole = 把破洞也画进去（洞要画在柱 d 和楼梯的后面，所以整张重画一遍）。"""
    cv = M.Canvas(PW, H)
    d = cv.d
    info = {}
    # 天花 + 檐口（石质横梁）+ 石墙 + 腰线 / 护墙板 / 踢脚板
    rect(d, 0, 0, PW - 1, 3, (30, 24, 38))
    for x in range(0, PW, 40):
        vl(d, x, 0, 3, (14, 10, 20))
    M.cornice(cv, 0, PW - 1, 4, STONE)
    M.ashlar(cv, (0, CAP_TOP, PW - 1, 115), pal=STONE, bw=30, bh=13, seed=5, chips=True)
    M.mul_box(cv.im, (0, CAP_TOP, PW - 1, CAP_TOP + 8), (0.78, 0.78, 0.86))          # 檐口下面的暗
    M.dado_rail(cv, 0, PW - 1, 116, WOOD)
    M.wainscot(cv, 0, PW - 1, 120, 137, WOOD, panel=32, gap=6, seed=4)
    M.skirting(cv, 0, PW - 1, 138, 5, WOOD)
    # 地面：棋盘格 + 红地毯
    M.checker_floor(cv, 0, PW - 1, 143, H - 1, FLOOR_L, FLOOR_D, 160, seed=3)
    M.runner(cv, 0, PW - 1, 156, 171, RUG, seed=3)                                 # 地毯从屏幕左边铺到右边（两头都出画面：免得地毯头在可走带里突然断掉）
    M.mul_box(cv.im, (0, 143, PW - 1, 145), (0.66, 0.66, 0.74))                    # 墙脚的接触影
    # 左端的门
    M.gothic_door(cv, 4, 84, 14, 54, kind='arch', seed=6)
    # 旗帜（柱 a 右边、柱 b 左边的窄墙）
    banner(cv, 41, 49, 22, 100, seed=1)
    banner(cv, 100, 108, 22, 100, seed=2)
    banner(cv, 302, 309, 22, 100, seed=3)                                          # 柱 d 右边：洞打开时会被圆洞削掉下半截
    # 壁炉
    info['fire'] = fireplace(cv, FIRE_X)
    info['mantel_flames'] = [mantel_candle(cv, FIRE_X - 19, 95), mantel_candle(cv, FIRE_X + 19, 95)]
    mantel_clock(cv, FIRE_X, 95)
    # 柱 a 右边旗帜下面：落地的青瓷花瓶 + 枯玫瑰（和走廊里的那一束是一对）
    M.dead_flowers(cv, 45, WALL_BASE)
    # 旗帜的下面右边：一只包铁皮的旧木箱
    chest(cv, 104, WALL_BASE)
    # 墙上的水渍（屋顶漏水）：从檐口洇下来
    for (sx, sl, sw) in ((24, 70, 4), (162, 30, 3), (230, 40, 4), (310, 56, 4)):
        M.damp_stain(cv, sx, 13, sl, w=sw, seed=sx)
    # 肖像 + 条案 + 壁烛台
    x0, y0, x1, y1 = PORTRAIT_BOX
    info['portrait'] = M.portrait(cv, x0, y0, x1, y1, 'dio', seed=3)
    M.mul_box(cv.im, (x0 + 4, y0 + 4, x1 - 4, y1 - 4), (0.82, 0.78, 0.74))                 # 清漆发暗的油画
    M.mul_box(cv.im, (x0 + 4, y0 + 28, x1 - 4, y1 - 4), (0.66, 0.58, 0.5))                 # DIO 的黄外套压深，别比脸还跳
    info['sconce_flames'] = []
    for sx in (131, 189):
        M.soot(cv, sx, 60, 82, w=5, seed=sx)
        info['sconce_flames'].append(M.sconce(cv, sx, 90, arms=1, seed=sx)[0])
    top = M.console_table(cv, 140, 180, WALL_BASE, seed=2)
    table_things(cv, 140, 180, top - 1)
    for cx_ in (141, 179):                                             # 条案上的两支矮烛台（在台面两端，火苗不压在画框上）
        info['sconce_flames'].append(mantel_candle(cv, cx_, top - 1))
    # 落地三头烛台
    info['floor_candles'] = M.candelabra(cv, 217, WALL_BASE, h=44, arms=3, seed=7)
    # 楼梯平台上方的高窗 + 帘子
    M.black_window(cv, 232, 22, 22, 78, slit='l', boards=True, seed=9)
    M.velvet_curtain(cv, 219, 228, 24, 111, side='l', pal=M.VELVET, seed=3)
    M.velvet_curtain(cv, 257, 266, 24, 111, side='r', pal=M.VELVET, seed=4)
    M.valance(cv, 218, 267, 19, h=6)
    # 破洞（柱 d 和楼梯之前画）
    if hole:
        paint_hole(cv)
    stairs(cv)
    info['landing_candles'] = M.candelabra(cv, 252, 112, h=24, arms=3, seed=9)             # 平台上的三头烛台
    info['lantern'] = newel_lantern(cv, 316, stair_tops()[0][2])                           # 楼梯脚的灯笼：照亮最下面两级（DIO 坐的地方）
    if hole:
        scatter_rubble(cv)
    # 柱子 + 它们在墙上 / 地上的影子（光在中间：吊灯和壁炉；a、b 的影子往左，c、d 往右）
    for i, cx in enumerate(PILLARS):
        sh = (cx - 17, cx - 8) if cx < 160 else (cx + 8, cx + 17)
        M.mul_box(cv.im, (sh[0], CAP_TOP + 4, sh[1], 142), (0.74, 0.74, 0.82))
        M.mul_box(cv.im, (sh[0] + (2 if cx < 160 else -2), CAP_TOP + 4, sh[1] - (2 if cx < 160 else -2), 142), (0.9, 0.9, 0.94))
        pillar(cv, cx, seed=20 + i)
        sx0, sx1 = (cx - 22, cx + 9) if cx < 160 else (cx - 9, cx + 22)           # 地上的影子（棋盘格 / 地毯上）
        M.mul_box(cv.im, (sx0, 155, sx1, 158), (0.74, 0.74, 0.8))
    # 吊灯
    info['chand_flames'] = chandelier(cv, *CHAND)
    info['chand_crystals'] = cv.chand_crystals
    # 角落的蛛网（柱头和檐口之间）
    for (x, y, r_, corner, s) in ((0, 12, 12, 'tl', 1), (40, 12, 10, 'tl', 2), (109, 12, 10, 'tr', 3), (127, 12, 10, 'tl', 4),
                                  (195, 12, 10, 'tr', 5), (213, 12, 12, 'tl', 6)):
        M.cobweb(cv, x, y, r_, corner, seed=s)
    info['spider_anchor'] = (127, 12)
    return cv, info


# ============================================================ 光
@lru_cache(maxsize=1)
def sun_geom():
    """光柱的几何：返回 (shaft 多边形, 光斑多边形, 空气里的光的遮罩 H×W 浮点, 光斑遮罩)。
    光柱 = 洞的圆沿着 (−16, +64) 的方向扫下来：中心线从 (289,104) 到 (274,164)，半宽从 21 缩到 19。"""
    (tx, ty), (fx, fy) = BEAM_TOP, BEAM_FOOT
    shaft = [(tx - 21, ty), (tx + 21, ty), (fx + 19, fy), (fx - 19, fy)]
    ell = [(fx + 19 * math.cos(a), fy + 12 * math.sin(a)) for a in np.linspace(0, math.tau, 48, endpoint=False)]
    yy, xx = np.mgrid[0:H, 0:PW]
    disc = np.hypot(xx - HOLE[0], yy - HOLE[1]) <= HOLE[2] + 4                      # 洞本身是光源：光柱从洞的下沿出来，不盖在洞上
    sm = M.poly_mask((PW, H), shaft).astype(np.float32) * (~disc)
    em = M.poly_mask((PW, H), ell).astype(np.float32)
    return shaft, ell, sm, em


def soft_mask(m, sigma):
    """多边形遮罩软一点（高斯）；尾巴 < 0.004 的地方切成 0（免得没光的地方出现一丝丝浮点差，白白多出像素）。"""
    s = ndimage.gaussian_filter(m, sigma)
    s[s < 0.004] = 0
    return s


def light(hole=False, beam=False, fs=1.0):
    L = M.Light(PW, H, amb=0.28, tint=T_AMB)
    yy, xx = L.yy, L.xx
    extra = -0.05 * np.clip((20 - yy) / 20.0, 0, 1)
    extra -= 0.12 * np.clip((16 - xx) / 16.0, 0, 1) + 0.10 * np.clip((xx - 304) / 16.0, 0, 1)
    L.amb_add(np.maximum(extra, -0.15))
    # 地面（可走带）：铺平的一层，只有壁炉一边极缓地亮一点（高斯，免得人走过去时脚下一圈圈光）
    fl = np.where(yy >= 143, 0.60 + 0.07 * np.exp(-((xx - FIRE_X) / 90.0) ** 2), 0.0).astype(np.float32)
    fl -= np.where(yy >= 143, 0.14 * np.clip((152 - yy) / 9.0, 0, 1), 0.0).astype(np.float32)
    L.add(fl, T_FLOOR)
    # 壁炉：最亮的暖光，照墙（clip y<146）
    L.point(FIRE_X, 124, 108, 1.20 * fs, M.T_FIRE, sy=1.0, power=1.5, clip=(0, 0, 200, 146))
    # 吊灯
    L.point(CHAND[0], CHAND[1] + 6, 110, 0.80, M.T_WARM, sy=1.0, power=1.6, clip=(0, 0, PW, 146))
    # 壁烛台、条案上的烛、落地烛台、壁炉台上的烛
    for (x, y, r_, k) in ((131, 88, 46, 0.70), (189, 88, 46, 0.70), (160, 112, 40, 0.5), (217, 100, 56, 0.85), (252, 96, 64, 0.95), (316, 124, 44, 0.8)):
        L.point(x, y, r_, k, M.T_WARM, sy=1.0, power=1.6, clip=(0, 0, PW, 146))
    # 肖像画框的小灯：眼睛得看得清
    L.point(160, 80, 34, 0.40, M.T_WARM, sy=0.9, power=1.2, clip=(130, 50, 190, 112))
    if hole:                                                           # 白天从洞里透进来：洞周围的墙、楼梯、柱 d、平台
        L.point(HOLE[0], HOLE[1], 78, 0.95, T_DAYB, sy=1.0, power=1.3, clip=(200, 0, PW, 160))
    if beam:
        shaft, ell, sm, em = sun_geom()
        L.add(0.80 * soft_mask(sm, 1.0), T_SUN2)                        # 光柱照亮它穿过的东西（楼梯、柱 d、墙）
        L.add(1.10 * soft_mask(em, 0.7) * (yy >= 143), T_SUN2)          # 地上的光斑：比周围亮得多
    return L


def floor_mask():
    m = np.zeros((H, PW), bool)
    m[143:, :] = True
    return m


@lru_cache(maxsize=None)
def field(hole=False, beam=False, fs=1.0):
    return light(hole, beam, fs).field(levels=14, fine=floor_mask(), fine_levels=28, jitter=0.24)


@lru_cache(maxsize=None)
def lit(hole=False, beam=False, fs=1.0):
    cv, _ = albedo(hole)
    return M.apply(cv, field(hole, beam, fs))


WARM_WHITE = (255, 238, 192)


def _beam_lit_image():
    """beam 状态的整张图：打光之后再往光柱里加“空气里的光”和三道斑驳的光线，地上光斑的核心往暖白里混（红地毯 / 棋盘格上都够亮）、
    边缘一圈更亮的亮边（落地范围一眼看清）。"""
    im = np.array(lit(True, True)).astype(np.float32)
    shaft, ell, sm, em = sun_geom()
    yy, xx = np.mgrid[0:H, 0:PW]
    bay = A._bayer(PW, H)
    # 空气里的光：10 档、Bayer 抖动，上面（离洞近）浓、往下淡；只加在光柱范围里（洞本身排除）
    dens = soft_mask(sm, 0.8) * (0.24 - 0.11 * np.clip((yy - 104) / 60.0, 0, 1))
    q = np.floor(dens * 10 + bay) / 10.0
    q[sm < 0.5] = 0
    # 三道光线（斜着、比周围亮）：沿光柱方向的窄条
    ang = (BEAM_FOOT[0] - BEAM_TOP[0]) / float(BEAM_FOOT[1] - BEAM_TOP[1])
    for (off, wd, amp) in ((-10, 1.2, 0.18), (2, 1.6, 0.24), (12, 1.0, 0.16)):
        cxl = BEAM_TOP[0] + off + ang * (yy - BEAM_TOP[1])
        ray = (np.abs(xx - cxl) < wd) & (sm > 0.5) & (yy < 156)
        q = np.where(ray, q + amp, q)
    im[..., :3] = np.clip(im[..., :3] + q[..., None] * np.array(SUN_ADD, np.float32), 0, 255)
    # 光斑：核心往暖白里混（4 档抖动），边缘一圈亮边
    core = soft_mask(em, 0.55) * (yy >= 143)
    aq = np.floor(np.clip(core * 0.74, 0, 1) * 4 + bay * 0.9) / 4.0
    aq[em < 0.5] = 0
    im[..., :3] = im[..., :3] * (1 - aq[..., None]) + np.array(WARM_WHITE, np.float32) * aq[..., None]
    edge = (em > 0.5) & (ndimage.binary_erosion(em > 0.5, iterations=1) == 0)
    im[edge, :3] = np.clip(im[edge, :3] + np.array((70, 62, 36), np.float32), 0, 255)
    return Image.fromarray(np.clip(im, 0, 255).round().astype(np.uint8), 'RGBA')


@lru_cache(maxsize=1)
def base_img():
    return lit(False, False)


def _diff_layer(new, old, extra_keep=None):
    """new 和 old 不一样的像素 → 透明底的图（不透明度 0 / 255）。extra_keep（H×W 布尔）里的像素也保留。"""
    a, b = np.array(new), np.array(old)
    diff = (a != b).any(-1)
    if extra_keep is not None:
        diff |= extra_keep
    out = np.zeros_like(a)
    out[diff] = a[diff]
    out[diff, 3] = 255
    return Image.fromarray(out, 'RGBA')


@lru_cache(maxsize=1)
def breach_img():
    cv, _ = albedo(True)
    base_hole = lit(True, False)
    # 洞本身（含被柱 d 挡住的部分之外的圆）一定要保留：用 albedo 里 emissive 的像素
    return _diff_layer(base_hole, base_img(), cv.emis())


@lru_cache(maxsize=1)
def beam_img():
    return _diff_layer(_beam_lit_image(), lit(True, False))


# ============================================================ strip
def _cache(raw, fps=FPS):
    memo = {}

    def fn(t):
        f = M.frame_of(t, fps)
        if f not in memo:
            memo[f] = raw(f)
        return memo[f]
    return fn


def _flame_fn(points, big=(), seed0=0, sparkle=()):
    """一组烛火的 strip 帧函数（8 帧 @8 fps）：每朵火苗相位错开。sparkle = [(x, y)]：吊灯的水晶，轮流闪一下（十字亮点）。"""
    def raw(f):
        im = A._new(PW, H)
        d = ImageDraw.Draw(im)
        for i, (x, y) in enumerate(points):
            M.flame(d, x, y, f, seed=seed0 + i, big=(i in big))
        for i, (x, y) in enumerate(sparkle):
            k = (f + i * 3) % N8
            if k == 0:
                px(d, x, y, (255, 255, 255))
                for (dx, dy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    px(d, x + dx, y + dy, (186, 200, 240))
            elif k == 1:
                px(d, x, y, (226, 234, 255))
        return im
    return _cache(raw, FPS_FIRE)


FIRE_BREATH = [1.0 + 0.09 * math.sin(math.tau * f / N8) + 0.05 * math.sin(2 * math.tau * f / N8 + 1.1) for f in range(N8)]


@lru_cache(maxsize=None)
def fire_glow(f):
    """第 f 帧壁炉火光的强弱（±14 % 呼吸）：整张图按这个强度重新打一遍光，只留和底图不一样的像素。
    只做炉口周围：半径 26 以内全留、26–56 之间按 Bayer 抖动一点点减少（边缘是抖动的、不是一圈硬边）、56 以外不动——
    再远的变化肉眼看不出，PNG 体积却会涨好几倍（整张图重打光的差异像素每帧上万个，每个颜色都不一样，几乎不压缩）。"""
    new = np.array(lit(False, False, round(FIRE_BREATH[f], 4)))
    base = np.array(base_img())
    diff = (new[..., :3] != base[..., :3]).any(-1)
    yy, xx = np.mgrid[0:H, 0:PW]
    dist = np.hypot(xx - FIRE_X, yy - 124)
    keep = dist < 26 + (56 - 26) * (1 - A._bayer(PW, H))
    diff &= keep
    out = np.zeros_like(new)
    out[diff] = new[diff]
    out[diff, 3] = 255
    return Image.fromarray(out, 'RGBA')


def _fire_raw(f):
    """壁炉里的火：火光的呼吸 + 三簇火舌（高度各自起伏）+ 炭火明暗 + 往上飘的火星（8 帧飘一圈）。火舌最下面是白芯、往上黄、橙、尖是红。"""
    im = fire_glow(f).copy()
    d = ImageDraw.Draw(im)
    info = albedo(False)[1]['fire']
    ox0, _, ox1, _ = info['box']
    cx = (ox0 + ox1) // 2
    pal = ((255, 250, 222), (255, 222, 120), (250, 156, 52), (210, 80, 34), (150, 40, 28))
    tongues = ((cx - 5, 10, 0), (cx, 14, 3), (cx + 5, 9, 5))              # (x, 基础高度, 相位)
    for (tx, h0, ph) in tongues:
        h = h0 + [0, 2, 3, 1, -1, 1, 2, 0][(f + ph) % 8]
        lean = [0, 1, 1, 0, -1, -1, 0, 1][(f + ph * 2) % 8]
        for r in range(h):
            u = r / float(h)
            hw = int(round(3.2 * (1 - u) ** 0.8 + (0.6 if r < 2 else 0)))
            ci = 0 if (u < 0.18) else (1 if u < 0.45 else (2 if u < 0.75 else (3 if u < 0.92 else 4)))
            xx = tx + int(round(lean * u * 2))
            for x in range(xx - hw, xx + hw + 1):
                core = abs(x - xx) <= hw * 0.4
                px(d, x, 139 - 1 - r, pal[max(0, ci - 1)] if core else pal[ci])
    for (x, y) in info['coals']:                                          # 炭火明暗：每块炭按自己的相位亮 / 暗
        k = (f + int(hash01(x, y, 3) * 8)) % 8
        c = [(255, 150, 70), (240, 110, 44), (214, 84, 36), (176, 56, 30), (150, 44, 28), (176, 56, 30), (214, 84, 36), (240, 110, 44)][k]
        px(d, x, y, c)
    for i in range(5):                                                    # 火星：从炉膛往上飘、8 帧回到原位
        ph = (f + i * 3) % 8
        x = cx - 8 + i * 4 + int(round(math.sin((ph + i) * 0.8) * 1.2))
        y = 128 - ph * 2
        if y > 110:
            px(d, x, y, (255, 226, 140) if ph < 4 else (250, 160, 70))
    return im


def _eyes_raw(f):
    """DIO 肖像的眼睛（红眼珠发光）：看左 / 看右 / 偶尔眨一下；金框上沿一粒高光慢慢走过去（保证每帧都在动）。"""
    p = albedo(False)[1]['portrait']
    look = (0, 1, 1, 0, -1, -1, 9, 0)[f]
    cv = M.Canvas(PW, H)
    M.eye_px(cv.d, p['eyes'], 0 if look == 9 else look, 'dio', blink=(look == 9))
    if look != 9:
        for (ex_, ey_) in p['eyes']:
            cv.e.point((ex_ + (1 if look >= 0 else 0), ey_), fill=255)
    gx = PORTRAIT_BOX[0] + 3 + f * 3
    cv.glow_px(gx, PORTRAIT_BOX[1] + 1, (255, 246, 214))
    return M.apply(cv, field(False, False), floor=0.0)


def _spider_raw(f):
    """柱 b 柱头右边垂下来的小蜘蛛：丝一伸一缩（±2 px），腿一抖一抖。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y0 = 127, 12
    L_ = 14 + int(round(2 * math.sin(math.tau * f / N8)))
    for y in range(y0, y0 + L_):
        px(d, x, y, (104, 100, 116))
    y = y0 + L_
    px(d, x, y, (22, 16, 26))
    px(d, x, y + 1, (22, 16, 26))
    px(d, x - 1, y + 1, (22, 16, 26))
    px(d, x + 1, y + 1, (22, 16, 26))
    wig = f % 2
    px(d, x - 2, y + wig, (22, 16, 26))
    px(d, x + 2, y + wig, (22, 16, 26))
    px(d, x - 2, y + 2 - wig, (22, 16, 26))
    px(d, x + 2, y + 2 - wig, (22, 16, 26))
    px(d, x, y + 1, (120, 20, 30)) if f % 4 == 0 else None
    return im


def _motes_fn():
    shaft, _, _, _ = sun_geom()
    fn, _ = M.motes_frame_fn(shaft, PW, H, n=34, seed=88, col=(255, 248, 226), drift=(1.0, 1.0))
    return fn


def _rays_raw(f):
    """光柱里三道光线一明一暗：同样的位置、颜色按帧往亮 / 暗两头走（8 帧闭合），保证每帧都变。"""
    im = np.array(_beam_lit_image()).astype(np.float32)
    out = np.zeros((H, PW, 4), np.uint8)
    shaft, ell, sm, em = sun_geom()
    yy, xx = np.mgrid[0:H, 0:PW]
    ang = (BEAM_FOOT[0] - BEAM_TOP[0]) / float(BEAM_FOOT[1] - BEAM_TOP[1])
    for i, (off, wd) in enumerate(((-10, 1.2), (2, 1.6), (12, 1.0))):
        cxl = BEAM_TOP[0] + off + ang * (yy - BEAM_TOP[1])
        ray = (np.abs(xx - cxl) < wd) & (sm > 0.5) & (yy < 156) & (yy > 110)
        k = 0.5 + 0.5 * math.sin(math.tau * (f / float(N8) + i / 3.0))
        col = np.clip(im[..., :3] * (0.92 + 0.22 * k) + 14 * k, 0, 255)
        out[ray, :3] = col[ray].astype(np.uint8)
        out[ray, 3] = 255
    return Image.fromarray(out, 'RGBA')


# ============================================================ 图层表 / 导出
@lru_cache(maxsize=1)
def tables():
    info = albedo(False)[1]
    layers = [M.L_pano('base', base_img(), 1.0, crop=False),
              M.L_pano('breach', breach_img(), 1.0, key='breach'),
              M.L_pano('beam', beam_img(), 1.0, key='beam')]
    fn = _cache(_fire_raw, FPS_FIRE)
    layers.append(M.L_strip('fire', M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _flame_fn(info['chand_flames'], big=tuple(range(8)), seed0=10, sparkle=info['chand_crystals'])
    layers.append(M.L_strip('chand', M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _flame_fn(info['mantel_flames'], seed0=30)
    layers.append(M.L_strip('mantel', M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _flame_fn(info['sconce_flames'] + list(info['floor_candles']) + list(info['landing_candles']), seed0=50)

    layers.append(M.L_strip('sconce', M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _flame_fn([(info['lantern'][0], info['lantern'][1])], seed0=71)          # 单朵火苗要挑相邻帧都不同的相位
    layers.append(M.L_strip('lantern', M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _cache(_eyes_raw)
    layers.append(M.L_strip('eyes', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    fn = _cache(_spider_raw)
    layers.append(M.L_strip('spider', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    fn = _motes_fn()
    layers.append(M.L_strip('motes', M.auto_box(fn, N8, FPS), N8, FPS, fn, key='beam'))
    fn = _cache(_rays_raw)
    layers.append(M.L_strip('rays', M.auto_box(fn, N8, FPS), N8, FPS, fn, key='beam'))
    return layers, []


def anchors():
    anc = {k: ([list(p) for p in v] if isinstance(v[0], list) else list(v)) for k, v in ANCHORS.items()}
    steps = [[a_, b_, y] for (a_, b_, y) in stair_tops()]
    anc.update(pillar_shaft=list(SHAFT), pillar_w=14, beam_center=list(BEAM_FOOT), beam_zone=[BEAM_RANGE[0], WALK[0], BEAM_RANGE[1], WALK[1]],
               beam_box=[BEAM_FOOT[0] - 40, 104, BEAM_FOOT[0] + 40, 178], breach_r=HOLE[2],
               dio_seat=list(DIO_SEAT), stair_steps=steps, fireplace=[FIRE_X, WALL_BASE], chandelier=list(CHAND),
               door_left=[12, 150])
    return anc


def compose(camX=0, t=0.5, state=None):
    layers, fg = tables()
    return M.compose(layers, fg, camX, t, state)


def export(ex, BJ):
    layers, fg = tables()
    st = M.export_stage(ex, PW, GROUND, WALK, layers, fg, anchors())
    if ex.check_on:
        _checks(ex, BJ, st, layers, fg)
    return st


def _checks(ex, BJ, st, layers, fg):
    states = [{}, {'breach': 1}, {'beam': 1}, {'breach': 1, 'beam': 1}]
    skip = [(cx - 25, 146, cx + 25, 160) for cx in PILLARS] + [(FIRE_X - 33, 143, FIRE_X + 33, 149)]
    cfg = dict(title='大厅', PW=PW, walk=WALK, base=base_img(), states=states, stand=STAND, required=REQUIRED,
               size_limit=250 * 1024, flat=(0, PW, WALK[0], WALK[1] + 1, 18, 0.012), flat_skip=skip)
    M.common_checks(ex, BJ, st, layers, fg, cfg)
    full = lambda s: np.array(M.compose(layers, fg, 0, 0.0, s))   # noqa: E731
    lum = lambda a: M.lum(a[..., :3].astype(np.float32))          # noqa: E731
    base, both = full({}), full({'breach': 1, 'beam': 1})
    lb, lo = lum(base), lum(both)
    # 光斑一眼看得清：落地范围（x 256–292，y 154–172）比同样的地面（x 190–230）亮得多；范围外 8 px 处回落到周围的亮度
    inside = lo[154:173, BEAM_RANGE[0] + 2:BEAM_RANGE[1] - 1].mean()
    around = lo[154:173, 190:230].mean()
    ex.checked('光斑（x %d–%d）平均亮度 %.0f，比旁边的地面（%.0f）亮 %.0f（要 ≥ 55）' %
               (BEAM_RANGE[0], BEAM_RANGE[1], inside, around, inside - around), 0 if inside - around >= 55 else 1)
    out_l = lo[154:173, BEAM_RANGE[0] - 12:BEAM_RANGE[0] - 4].mean()
    out_r = lo[154:173, BEAM_RANGE[1] + 5:BEAM_RANGE[1] + 12].mean()
    ex.checked('光斑边缘清楚：范围外 5–12 px 的亮度（左 %.0f / 右 %.0f）比范围内（%.0f）至少低 35' % (out_l, out_r, inside),
               0 if (inside - max(out_l, out_r) >= 35) else 1)
    # 光斑里每一行都亮：落地的范围里没有“掉到地毯暗处”的洞（逐列最小值）
    cols_dark = int((lo[158:170, BEAM_RANGE[0] + 3:BEAM_RANGE[1] - 2].mean(0) < around + 35).sum())
    ex.checked('光斑范围里每一列（y 158–169 的平均）都比周围亮 ≥ 35（暗的列 %d）' % cols_dark, cols_dark)
    # 光柱在空气里：洞下面（y 112–148、x 262–300）比没光柱时亮
    air = lo[112:148, 262:300].mean() - lb[112:148, 262:300].mean()
    ex.checked('光柱穿过的墙 / 楼梯（x 262–300，y 112–148）开光柱后亮度 +%.0f（要 ≥ 25）' % air, 0 if air >= 25 else 1)
    # 破洞：圆里（排除柱 d 的 x 283–297）的像素和没洞时不一样、而且偏亮 / 偏蓝
    cx0, cy0, r = HOLE
    yy, xx = np.mgrid[0:H, 0:PW]
    disc = (np.hypot(xx - cx0, yy - cy0) <= r - 1) & ~((xx >= cx0 - 7) & (xx <= cx0 + 6))
    bh = full({'breach': 1})
    chg = (bh[..., :3] != base[..., :3]).any(-1)[disc].mean()
    ex.checked('breach=1：圆洞（半径 %d）里 %.0f %% 的像素变成了洞里的天空 / 屋顶（≥ 98 %%）' % (r, 100 * chg), 0 if chg >= 0.98 else 1)
    sky = bh[cy0 - r + 5:cy0 - r + 12, cx0 - 13:cx0 - 7, :3].astype(np.int32)
    ex.checked('洞的上半是天空（蓝 − 红 = %.0f ≥ 20）' % (sky[..., 2].mean() - sky[..., 0].mean()), 0 if sky[..., 2].mean() - sky[..., 0].mean() >= 20 else 1)
    # 柱 d 在洞前面：洞开着时柱身中段（x 284–296、y 80–120）还是柱子（偏灰紫、不是天空）
    pil = bh[84:116, cx0 - 5:cx0 + 5, :3].astype(np.float32)
    blue = float((pil[..., 2] - pil[..., 0]).mean())
    ex.checked('breach=1：柱 d 还立在洞前面（柱身 x %d–%d 的蓝 − 红 = %.0f，天空那种 > 60 就算被盖住了）' % (cx0 - 5, cx0 + 4, blue), 0 if blue < 55 else 1)
    # 圆不是椭圆：洞的横向宽度和竖向高度一样（含柱 d 挡着的）
    # 柱身干净：每根柱身（x−5..x+4，y 30–139）在 albedo（满光固有色）里逐列的纵向亮度标准差都很小——只有细石纹，没有装饰 / 缺口
    # （打光后的底图有从上到下的光照渐变，不算装饰，所以看固有色）
    alb = albedo(False)[0]
    la = M.lum(np.array(alb.im)[..., :3].astype(np.float32))
    for i, cx in enumerate(PILLARS):
        reg = la[30:140, cx - 5:cx + 5]
        sd = float(reg.std(0).max())                                   # 逐列：细石纹造成的起伏
        rows = np.convolve(reg.mean(1), np.ones(7) / 7.0, mode='valid')   # 逐行平均再滑动平均 7 行：横向的环 / 带会留下来，细石纹会被抹平
        rng = float(rows.max() - rows.min())
        ex.checked('柱 %s 的柱身中段（y 30–139）固有色：逐列纵向标准差最大 %.1f（≤ 16）、逐行平均（滑动 7 行）的起伏 %.1f（≤ 11）：整块石头，没有装饰' %
                   ('abcd'[i], sd, rng), 0 if (sd <= 16 and rng <= 11) else 1)
    # 锚点：柱 / 光 / 楼梯和画面上画的东西对得上
    a_ = st['anchors']
    for i, cx in enumerate(PILLARS):
        ex.checked('anchors.pillar_%s = (%d,%d) 就是画的柱子（柱脚 154、柱身中心 x %d）' % ('abcd'[i], a_['pillar_' + 'abcd'[i]][0], a_['pillar_' + 'abcd'[i]][1], cx),
                   0 if a_['pillar_' + 'abcd'[i]] == [cx, 154] else 1)
    ex.checked('anchors.pillar_tops 每根 [上端, 下端] = [%d,154]' % CAP_TOP, 0 if a_['pillar_tops'] == [[CAP_TOP, 154]] * 4 else 1)
    ex.checked('anchors.stairs_up [300,160] 在楼梯前面的可走带里（第 2 级 x 302–311）', 0 if a_['stairs_up'] == [300, 160] else 1)
    # 肖像的眼睛在画框里；红眼
    p = albedo(False)[1]['portrait']
    x0, y0, x1, y1 = PORTRAIT_BOX
    ex.checked('肖像的眼睛在画框 %s 里' % (PORTRAIT_BOX,), 0 if all(x0 < ex_ < x1 and y0 < ey < y1 for ex_, ey in p['eyes']) else 1)
    ex.checked('anchors.portrait [160,80] 是画框中心（框 %s）' % (PORTRAIT_BOX,), 0 if abs((x0 + x1) / 2.0 - 160) <= 0.5 and abs((y0 + y1) / 2.0 - 80) <= 0.5 else 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch11', 'after')
    os.makedirs(od, exist_ok=True)
    states = [{}, {'breach': 1}, {'breach': 1, 'beam': 1}]
    out = Image.new('RGB', (PW, H * 3 + 8), (0, 0, 0))
    for i, s in enumerate(states):
        out.paste(compose(0, 0.5, s).convert('RGB'), (0, i * (H + 4)))
    out.resize((out.width * 3, out.height * 3), Image.NEAREST).save(os.path.join(od, 'mansion_hall_solo.png'))
    print('ok')
