# -*- coding: utf-8 -*-
r"""submarine —— 第7章「红海」：SPW 财团准备的潜艇舱内（地图 sub_ch7），第 15 战段 1「女教皇·伪装」的场地。
2026-10-19 第三轮背景重画（sea 组）新画（改前是 later_stages 的占位）。共用零件在 sea_parts.py。

地图 640 宽、ground 160、可走带 y 150–176（钢甲板，花纹压得很淡）；侧视平视，看的是艇壳的内壁，顶上六盏昏黄的笼罩灯。
从上到下：y 0–22 顶棚（艇壳弯过头顶：包布的蒸汽管、红色消防管、电缆槽、吊架）；y 22–46 墙上部一排横管（绿漆水管、铜管、
电缆束 + 卡子）；y 46–141 铆钉钢板（三道横缝、六根肋骨）；141–148 踢脚带；149 墙脚的阴影；150 往下钢甲板。
从左到右（世界坐标）：
  x 0–29      艏部横隔舱壁：一扇关着的椭圆水密门（一圈压紧扳手，没有转盘——转盘把手只在艉部那扇门上，免得和金属物件混）
  x 31–34     一根竖管，管上一只压力表（obj_pressure_gauge）
  x 44–120    操舵台（anchors.helm）：绿漆钢台（一排开关、三盏指示灯会闪、小电表），台上竖起一只黄铜舵轮；墙上的深度计（大表盘，
              指针微微抖）、从墙上部下来的黄铜传声筒；台面右端一只罗盘（obj_compass，小罗经柜）；上面一个舷窗
  x 130–180   阀组：一根竖管接一根横的总管，总管上一只红色手轮阀门（obj_valve），总管右端往下滴水、滴进墙脚的小铁桶（strip drip）；
              上面一个配电箱（黄色警告牌、闸刀把手）
  x 176–204   潜望镜（anchors.periscope）：从顶棚的套筒里垂下来，下端是目镜箱 + 两只折起来的把手
  x 210–222   墙上的挂钩挂着一副黄铜望远镜（obj_binoculars，带子挂在钩上）
  x 236–314   海图桌（anchors.chart）：桌上靠墙一台收音机（obj_radio，天线线拉到墙上部，调谐窗的灯会闪）、一卷海图、分规、
              一本红皮的航海日志（剧情纪念品在 chart + 12）；桌下两个抽屉；墙上钉着一张红海的海图；上面一个舷窗
  x 310–332   工具板：画着工具轮廓的挂板，只挂着一把大扳手（obj_wrench），锤子 / 起子的位置空着（只剩轮廓）
  x 344–404   小厨房（anchors.galley）：钢台面 + 柜门；电炉上一把搪瓷咖啡壶（热气 strip）、旁边一只金属杯（obj_metal_cup）；
              墙上一根挂杯架挂着三只白色搪瓷杯；椭圆的刮胡镜，镜下小搁板上立着一把剃刀（obj_razor）和一支刷子
  x 412–428   两个窄长的铁皮柜（百叶通风口）
  x 430–470   双层铺位（anchors.bunks）：条纹床垫、灰毯子、枕头，帘子拉了一半，上铺墙上钉着一张小照片；上面一个舷窗
  x 471–484   一根竖管在这里拐弯（obj_pipe_elbow），往右变成一根横管沿墙走到潜水装备那边、再钻进墙上部
  x 494–578   潜水装备（anchors.gear）：一卷挂着的气管、墙上绑着一只氧气瓶（obj_oxygen_tank，黄色瓶箍）、搁板上一顶黄铜潜水头盔、
              挂钩上挂着两套帆布潜水服；墙脚的矮凳上放着一只潜水靴（obj_diving_boot，铅底）
  x 580–596   通往指挥塔的直梯，顶上的舱口盖开着（里面黑）
  x 598–640   艉部横隔舱壁 + 水密门（anchors.hatch），门上一只舱门把手（obj_hatch_handle）
舷窗外面是深蓝的海：气泡往上冒、小鱼游过去（strip）。

12 件金属（女教皇会伪装成其中一件；剧情 7-10 把 prop.disguise_<名字>（10×10，pivot 底中，z = 152 − y − 5）摆在锚点上，
  平时透明、只在眨眼那 0.22 s 显示）：每件都画在锚点的 10×10 框里（x−5..x+4、y−5..y+4，和道具的框一样大），眨眼那一帧
  正好盖住底图的这一件；彼此 x 间距 ≥ 32、y 在 114–142（都在可走带后沿上面）。挂钩、带子、管子的两头这些“连着的东西”
  画在框外。锚点 objects 按剧情 METAL 的顺序（压力表、阀门、扳手、金属杯、剃刀、望远镜、弯管、收音机、潜水靴、氧气瓶、
  罗盘、舱门把手；规格里列的顺序不一样，以剧情 ch07.js 的 METAL 为准）。别的东西不画成这 12 种（杯架上是白色搪瓷杯、
  左边的门没有转盘、深度计是墙上的大表盘），免得认错。

图层（从后往前）：
  near       pano  k 1          整个舱内（打好光：六盏笼罩灯的暖光圈 + 冷的环境光，分档、只在档的交界抖）
  port0–2    strip k 1          三个舷窗里的海（气泡往上冒、小鱼游过去；同一组帧、三个框）
  lamp       strip k 1          x 400 那盏灯接触不好，一闪一闪
  blink0–1   strip k 1          操舵台的指示灯 + 深度计指针 / 收音机调谐窗的灯（同一组帧、两个框）
  steam      strip k 1          咖啡壶的热气
  drip       strip k 1          阀组滴水 → 小铁桶里的水纹
  water      pano  k 1  key leak   地上积了一层水（半透明的水膜 + 灯的倒影亮条 + 水纹）
  spray0–3   strip k 1  key leak   四处管道接缝喷水（同一组帧、四个框）
  bulbs_off  pano  k 1  key dark   停电：六个灯泡灭了（灰玻璃）
  dark       tint       key dark   整屏压暗
  emerg      pano  k 1  key dark   两盏应急灯亮着（红橙色 + 一圈光晕 + 往下的一小片光）
  alarm_t    tint       key alarm  红色
  beacon0–1  strip k 1  key alarm  顶棚两盏旋转警报灯（灯罩一亮一暗 + 往两边扫的红光；同一组帧、两个框）
锚点：arrive [40,164]、helm [70,160]、periscope [190,152]、chart [280,154]、galley [360,152]、bunks [450,150]、gear [530,150]、
  hatch [610,156]、obj_pressure_gauge … obj_hatch_handle（12 件，见 OBJ）、objects（12 个点，METAL 顺序）；
  额外：walk_x、ports（舷窗中心）、lamps（灯泡）、logbook（航海日志 [292,126]）。
key：alarm、leak、dark。
单独运行：python -B tools\bg_new\submarine.py → tools\bg_new\_preview\ch7\after\submarine_solo_*.png
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
    key = 'bg_new_sea_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'sea_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
C = P.C
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
N_ANIM, FPS_ANIM = P.N_ANIM, P.FPS_ANIM
fno = P.frame_no

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (150, 176)
CEIL = 22                     # 顶棚（艇壳弯过头顶的那一段）到这里
SEAMS = (46, 78, 110)         # 钢板的三道横缝
KICK = 141                    # 踢脚带 141–148
FLOOR = 150                   # 甲板从这里开始（149 是墙脚的阴影线）
FWD_X = 29                    # 艏部横隔舱壁的右沿
AFT_X = 598                   # 艉部横隔舱壁的左沿
RIBS = [38, 124, 226, 336, 406, 488]          # 肋骨（6 px 宽）
LAMPS = [60, 172, 290, 400, 512, 612]         # 笼罩灯（灯泡中心 y LAMP_Y）
LAMP_Y = 28
FLICKER = 3                   # LAMPS[3] = 400 那盏接触不好
PORTS = [(76, 62), (282, 70), (450, 64)]      # 舷窗中心（外圈黄铜 r 9、玻璃 r 6）
PORT_R, GLASS_R = 9.2, 6.2
BEACONS = [(214, 21), (470, 21)]              # 旋转警报灯
EMERG = [(250, 50), (560, 50)]                # 应急灯
DEPTH = (98, 96)              # 深度计
WHEEL = (68, 113)             # 舵轮
DRIP = (177, 127)             # 阀组滴水的地方
BUCKET = (172, 180)           # 小铁桶 x 范围（桶底在墙脚）
POT = (348, 356)              # 咖啡壶 x 范围
SPRAYS = [(142, 16), (309, 33), (446, 11), (540, 112)]   # key leak：喷水的接缝

# 12 件金属：中心 [x, y]（剧情按名字取；10×10 框 x−5..x+4、y−5..y+4）
OBJ = dict(pressure_gauge=(36, 116), valve=(152, 124), wrench=(320, 120), metal_cup=(364, 135), razor=(396, 128),
           binoculars=(216, 128), pipe_elbow=(476, 114), radio=(262, 124), diving_boot=(556, 142),
           oxygen_tank=(508, 130), compass=(108, 120), hatch_handle=(618, 120))
METAL = ['pressure_gauge', 'valve', 'wrench', 'metal_cup', 'razor', 'binoculars', 'pipe_elbow', 'radio', 'diving_boot',
         'oxygen_tank', 'compass', 'hatch_handle']    # 和 story\ch07.js 的 METAL 同顺序

ANCHORS = dict(
    arrive=[40, 164],          # 从艏部那扇门进来
    helm=[70, 160],            # 操舵台（乔瑟夫掌舵）
    periscope=[190, 152],
    chart=[280, 154],          # 海图桌前
    galley=[360, 152],         # 小厨房前
    bunks=[450, 150],
    gear=[530, 150],           # 潜水装备前
    hatch=[610, 156],          # 艉部水密门 / 直梯前
    walk_x=[8, 632],
)

# ============================================================ 调色
INK = (36, 32, 40)
WALL = (146, 158, 142)        # 舱壁的浅灰绿漆
WALL_L = (168, 180, 162)
WALL_D = (124, 136, 122)
WALL_DD = (100, 110, 100)
CEILC = (104, 112, 106)
KICKC = (92, 104, 94)
FLOORC = (124, 122, 114)
FLOOR_L = (136, 134, 124)
FLOOR_D = (104, 102, 96)
STEEL = [(44, 50, 60), (86, 100, 114), (122, 140, 156), (152, 170, 186), (200, 212, 222)]   # 金属物件：暗 → 亮
BRASS = [(92, 70, 38), (146, 116, 62), (188, 156, 92), (226, 200, 128)]
COPPER = [(108, 60, 36), (160, 96, 56), (204, 140, 88)]
PAINT = [(66, 82, 70), (92, 110, 94), (118, 136, 118), (146, 162, 144)]      # 绿漆管子 / 台子：暗 → 亮
LAG = [(150, 142, 124), (184, 176, 156), (212, 204, 182), (232, 226, 206)]  # 包布的蒸汽管
REDP = [(104, 32, 28), (146, 46, 38), (182, 62, 50), (214, 100, 84)]
CANVAS = [(92, 80, 58), (124, 108, 78), (156, 138, 102), (186, 168, 128)]
WOOD = [(74, 52, 38), (104, 76, 52), (136, 102, 70), (168, 132, 92)]
CREAM = (226, 222, 186)
SEA_IN = [(30, 78, 122), (20, 54, 94), (12, 34, 66)]   # 舷窗外的海：上 → 下


def disc_pts(cx, cy, r):
    """圆心 (cx, cy)（可以落在半格上）、半径 r 的圆盘里的像素。"""
    out = []
    for y in range(int(math.floor(cy - r)), int(math.ceil(cy + r)) + 1):
        for x in range(int(math.floor(cx - r)), int(math.ceil(cx + r)) + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                out.append((x, y))
    return out


def stamp(d, x0, y0, rows, pal):
    """按字符格子画一个小东西（'.' 透明）。"""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != '.':
                px(d, x0 + i, y0 + j, pal[ch])


# ============================================================ 12 件金属（正常版）
OPAL = {'k': INK, '1': STEEL[0], '2': STEEL[1], '3': STEEL[2], '4': STEEL[3], '5': STEEL[4],
        'b': BRASS[0], 'B': BRASS[1], 'y': BRASS[2], 'Y': BRASS[3], 'c': CREAM, 'R': REDP[2], 'r': REDP[1],
        'e': (64, 40, 28), 'A': (150, 96, 44), 'g': (28, 40, 56), 'G': (168, 198, 220), 'o': (220, 184, 68),
        'O': (166, 132, 40), 'l': (92, 80, 64), 'L': (132, 116, 90), 'm': (172, 156, 124)}

GRIDS = {
    'wrench': ['......4...',
               '.....42...',
               '.....42.42',
               '.....43332',
               '....43332.',
               '...4332...',
               '..4332....',
               '.4k32.....',
               '.432......',
               '..2.......'],
    'metal_cup': ['..........',
                  '.k44444k..',
                  '.4eeeee2..',
                  '.54333212k',
                  '.5433321.2',
                  '.5433321.2',
                  '.54333212k',
                  '.5433321..',
                  '.k22221k..',
                  '..........'],
    'razor': ['..........',
              '.k555555k.',
              '.43333332.',
              '.k222222k.',
              '....42....',
              '....41....',
              '....42....',
              '....41....',
              '....42....',
              '...k22k...'],
    'binoculars': ['..........',
                   '.kBk..kBk.',
                   '.yBBBBBBb.',
                   '.yBBkkBBb.',
                   '.yBb..yBb.',
                   '.yBb..yBb.',
                   '.kgk..kgk.',
                   '.gGg..gGg.',
                   '.kkk..kkk.',
                   '..........'],
    'radio': ['........k.',
              '........4.',
              '.k555555k.',
              '.4k2k2AA2k',
              '.4k2k2AA2k',
              '.4k2k2332k',
              '.43333332k',
              '.4k33k332k',
              '.k2222222k',
              '.k......k.'],
    'diving_boot': ['..kmmk....',
                    '..mLLl....',
                    '..mLyl....',
                    '..mLLl....',
                    '..mLyl....',
                    '..mLLLl...',
                    '.mLLLLLyy.',
                    '.mLLLLByyB',
                    '.lllllBBBb',
                    '.k1111111k'],
    'oxygen_tank': ['...k44k...',
                    '....32....',
                    '...4332...',
                    '..543321..',
                    '..kkkkkk..',
                    '..ooooOO..',
                    '..oooOOO..',
                    '..543321..',
                    '..543321..',
                    '...k22k...'],
    'compass': ['..........',
                '...kkkk...',
                '..kGccGk..',
                '.kccRccck.',
                '.kcckccck.',
                '.yBBBBBBb.',
                '.yBBBBBBb.',
                '..yBBBBb..',
                '...kBBk...',
                '..kBBBBk..'],
    'hatch_handle': ['..........',
                     '....45....',
                     '..445543..',
                     '..4kkkk2..',
                     '.43k..k32.',
                     '.43....32.',
                     '.43....32.',
                     '.43....32.',
                     '.k1k..k1k.',
                     '..........'],
}


def obj_pressure_gauge(d, x, y):
    """压力表：圆的，黑外圈、钢表圈（左上亮）、奶白表盘、几个刻度、红指针指在右上（正常范围），下面一截接管。"""
    cx, cy = x - 0.5, y - 1.0
    for (u, v) in disc_pts(cx, cy, 4.6):
        r = math.hypot(u - cx, v - cy)
        s = (u - cx) + (v - cy)
        if r > 3.8:
            c = INK
        elif r > 2.9:
            c = STEEL[4] if s < -1.2 else (STEEL[1] if s > 1.2 else STEEL[2])
        else:
            c = CREAM
        px(d, u, v, c)
    for (u, v) in ((x - 3, y - 1), (x - 2, y - 3), (x, y - 4), (x + 1, y - 3)):
        px(d, u, v, STEEL[2])                                      # 刻度
    px(d, x - 1, y - 1, INK)                                       # 指针轴
    px(d, x, y - 2, REDP[2])
    px(d, x + 1, y - 3, REDP[2])
    hl(d, x - 2, x, y + 3, STEEL[1])                              # 下面接管
    hl(d, x - 2, x, y + 4, INK)


def obj_valve(d, x, y):
    """阀门：红手轮（左上亮、右下暗），十字辐条 + 钢轮毂；轮圈中间透出后面的总管。"""
    cx, cy = x - 0.5, y - 0.5
    for (u, v) in disc_pts(cx, cy, 4.7):
        r = math.hypot(u - cx, v - cy)
        s = (u - cx) + (v - cy)
        if r > 3.1:
            c = REDP[3] if s < -1.5 else (REDP[0] if s > 2.4 else (REDP[1] if s > 0.6 else REDP[2]))
            px(d, u, v, c)
        elif abs(u - cx) < 1.0 or abs(v - cy) < 1.0:
            px(d, u, v, STEEL[3] if s < 0 else STEEL[1])          # 辐条
    rect(d, x - 1, y - 1, x, y, STEEL[2])                          # 轮毂
    px(d, x - 1, y - 1, STEEL[4])
    px(d, x, y, INK)


def obj_pipe_elbow(d, x, y):
    """弯管（┌ 形）：横的一截从右边来、在左上拐一个弯往下；管子 3 px 粗，外侧（上 / 左）亮、内侧暗，弯里面一道墨线。
    框外两头接着直管（draw_elbow_pipes 画）。"""
    x0, y0 = x - 5, y - 5
    bx, by = x0 + 5, y0 + 5                                        # 弯的圆心
    for j in range(10):
        for i in range(10):
            u, v = x0 + i, y0 + j
            if i >= 5 and j <= 2:                                  # 横的一截
                c = (STEEL[4], STEEL[3], STEEL[1])[j]
            elif i <= 2 and j >= 5:                                # 竖的一截
                c = (STEEL[4], STEEL[3], STEEL[1])[i]
            elif i < 5 and j < 5:
                r = math.hypot(u + 0.5 - bx, v + 0.5 - by)
                if r > 5.2 or r < 2.2:
                    continue
                c = STEEL[4] if r > 4.4 else (STEEL[3] if r > 3.3 else STEEL[1])
            else:
                continue
            px(d, u, v, c)
    hl(d, x0 + 5, x0 + 9, y0 + 3, INK)                             # 横管下沿的影
    vl(d, x0 + 3, y0 + 5, y0 + 9, INK)                             # 竖管右沿的影
    px(d, x0 + 4, y0 + 4, INK)
    px(d, x0 + 3, y0 + 4, STEEL[0])
    px(d, x0 + 4, y0 + 3, STEEL[0])


def draw_objects(d):
    """12 件金属的正常版（中心在 OBJ 的锚点上）。"""
    for name, (x, y) in OBJ.items():
        if name in GRIDS:
            stamp(d, x - 5, y - 5, GRIDS[name], OPAL)
        elif name == 'pressure_gauge':
            obj_pressure_gauge(d, x, y)
        elif name == 'valve':
            obj_valve(d, x, y)
        elif name == 'pipe_elbow':
            obj_pipe_elbow(d, x, y)


# ============================================================ 墙 / 顶棚 / 甲板
def wall_base():
    """墙面（numpy RGB）：每块钢板（肋骨之间 × 横缝之间）颜色错开一点，fbm 斑驳分三档（只在档的交界抖）；
    越往下越脏一点（墙脚）。顶棚往上越来越暗（艇壳弯过头顶）。"""
    a = np.zeros((H, PW, 3), np.float32)
    nz = A._fbm(PW, H, 7, seed=11)
    bay = A._bayer(PW, H)
    xs_e = [FWD_X + 1] + RIBS + [AFT_X]
    ys_e = [CEIL] + list(SEAMS) + [KICK]
    for i in range(len(xs_e) - 1):
        for j in range(len(ys_e) - 1):
            off = hrange(-5, 5, i, j, 13)
            a[ys_e[j]:ys_e[j + 1], xs_e[i]:xs_e[i + 1]] = np.array(WALL, np.float32) + off
    q = nz + (bay - 0.5) * 0.12
    lo = (q < 0.38)[..., None]
    hi = (q > 0.64)[..., None]
    a = np.where(lo, a * 0.93, np.where(hi, a * 1.05, a))
    ys = np.arange(H, dtype=np.float32)[:, None, None]
    a *= 1.0 - 0.07 * np.clip((ys - 112) / 30.0, 0, 1)            # 墙脚脏一点
    # 顶棚：往上越来越暗，三档
    for y in range(CEIL):
        k = 0.66 + 0.3 * (y / float(CEIL))
        k = round(k * 8) / 8.0
        a[y] = np.array(CEILC, np.float32) * k
    # 踢脚带
    a[KICK:FLOOR - 1] = np.array(KICKC, np.float32)
    a[KICK] = np.array(PAINT[3], np.float32) * 0.92
    a[FLOOR - 1] = np.array((58, 62, 60), np.float32)              # 墙脚的阴影线
    return a


def floor_base(a):
    """钢甲板（y 150–179）：防滑菱形纹（只比底色亮一点点）、每 80 px 一道拼缝（近大远小，往两边斜一点）+ 角上螺栓；
    中间一条被鞋磨亮的路。"""
    for y in range(FLOOR, H):
        v = (y - FLOOR) / float(H - 1 - FLOOR)
        for x in range(PW):
            c = np.array(FLOORC, np.float32)
            if (y % 4 == 1 and (x + 2 * y) % 8 in (0, 1)) or (y % 4 == 3 and (x - 2 * y) % 8 in (4, 5)):
                c = c + 9
            if 158 <= y <= 170 and hash01(x // 3, y, 7) < 0.25:
                c = c + 5                                          # 磨亮的路
            a[y, x] = c * (1.0 - 0.05 * v)
        if y == FLOOR:                                             # 贴着墙脚一条排水沟：暗的槽 + 一根根亮的格栅
            a[y] = np.array((84, 84, 82), np.float32)
        elif y == FLOOR + 1:
            a[y, ::3] = np.array((132, 130, 122), np.float32)
            a[y, 1::3] = np.array((90, 90, 86), np.float32)
            a[y, 2::3] = np.array((90, 90, 86), np.float32)
    for i in range(9):
        xs = 40 + 80 * i
        for y in range(FLOOR, H):
            x = int(round(xs + (xs - 320) * (y - FLOOR) / 420.0))
            if 0 <= x < PW - 1:
                a[y, x] = np.array(FLOOR_D, np.float32)
                a[y, x + 1] = np.array(FLOOR_L, np.float32)
        for y in (153, 175):
            x = int(round(xs + (xs - 320) * (y - FLOOR) / 420.0))
            for dx in (-4, 5):
                if 0 <= x + dx < PW:
                    a[y, x + dx] = np.array(FLOOR_L, np.float32) + 10
                    if x + dx + 1 < PW:
                        a[y + 1, x + dx + 1] = np.array(FLOOR_D, np.float32)
    # 地上一块检修盖板（舱底）：浅浅的一圈缝 + 中间一个凹下去的拉环
    for x in range(246, 270):
        a[161, x] = np.array(FLOOR_D, np.float32)
        a[169, x] = np.array(FLOOR_L, np.float32)
    for y in range(161, 170):
        a[y, 246] = np.array(FLOOR_D, np.float32)
        a[y, 269] = np.array(FLOOR_L, np.float32)
    for (x, y) in ((256, 164), (257, 164), (258, 165), (255, 165), (256, 166), (257, 166)):
        a[y, x] = np.array(FLOOR_D, np.float32)


def draw_shell(d):
    """钢板的横缝 + 铆钉、肋骨、顶棚的管子 / 电缆槽 / 吊架、墙上部的一排横管。"""
    # 横缝：上一块压着下一块（缝口亮、下面一道影）+ 缝两边各一排铆钉
    for y in SEAMS:
        hl(d, FWD_X + 1, AFT_X - 1, y, WALL_L)
        hl(d, FWD_X + 1, AFT_X - 1, y + 1, WALL_DD)
        for x in range(FWD_X + 4, AFT_X - 2, 5):
            for yy in (y - 2, y + 4):
                px(d, x, yy, WALL_L)
                px(d, x + 1, yy + 1, WALL_DD)
    # 肋骨：左沿受光、右沿暗、右边落一道影；中线一串铆钉；顶上弯进顶棚（越往上越暗越窄）
    for rx in RIBS:
        for y in range(0, KICK):
            top = y < CEIL
            k = 0.7 + 0.3 * (y / float(CEIL)) if top else 1.0
            xo = int(round((rx - 320) * max(0, CEIL - y) / 160.0))
            cols = (WALL_L, (138, 150, 134), (138, 150, 134), (128, 140, 124), (116, 128, 112), WALL_DD)
            for k_, c in enumerate(cols):
                px(d, rx + xo + k_, y, dk(c, k))
            if not top:
                px(d, rx + 6, y, dk(WALL, 0.84))                     # 落在墙上的影
        for y in range(CEIL + 4, KICK - 2, 7):
            px(d, rx + 2, y, WALL_L)
            px(d, rx + 3, y + 1, WALL_DD)
        hl(d, rx - 1, rx + 7, KICK - 1, WALL_DD)                     # 肋骨脚
        hl(d, rx - 1, rx + 7, KICK - 2, (128, 140, 124))
    # 顶棚：包布蒸汽管（y 3–10，每 14 px 一道箍）、红色消防总管（12–15）、电缆槽（17–20）、吊架
    for x in range(PW):
        for y, c in zip(range(3, 11), (LAG[1], LAG[3], LAG[2], LAG[2], LAG[2], LAG[1], LAG[0], INK)):
            px(d, x, y, dk(c, 0.84))
        if x % 14 == 0:
            vl(d, x, 3, 9, dk(LAG[0], 0.8))
            vl(d, x + 1, 3, 9, dk(LAG[0], 0.9))
        for y, c in zip(range(12, 16), (REDP[3], REDP[2], REDP[1], REDP[0])):
            px(d, x, y, dk(c, 0.86))
        for y, c in zip(range(17, 21), ((70, 72, 76), (56, 56, 62), (64, 62, 66), (44, 44, 50))):
            px(d, x, y, c if (x + y) % 3 else dk(c, 0.8))
    for x in range(10, PW, 40):                                    # 吊架
        vl(d, x, 0, 21, (60, 64, 66))
        vl(d, x + 1, 0, 21, (88, 94, 94))
        hl(d, x - 2, x + 3, 21, (60, 64, 66))
    for x in range(0, PW, 96):                                     # 消防总管的法兰
        rect(d, x + 50, 11, x + 52, 16, REDP[1])
        vl(d, x + 50, 11, 16, REDP[3])
    # 墙上部的横管：绿漆水管（31–34，法兰）、铜管（37–38）、电缆束（40–43，卡子）
    xa, xb = FWD_X + 1, AFT_X - 1
    for x in range(xa, xb + 1):
        for y, c in zip(range(31, 35), (PAINT[3], PAINT[2], PAINT[1], PAINT[0])):
            px(d, x, y, c)
        px(d, x, 35, dk(WALL, 0.82))
        px(d, x, 37, COPPER[2])
        px(d, x, 38, COPPER[0])
        for y, c in zip(range(40, 44), ((104, 104, 106), (80, 80, 86), (90, 88, 92), (58, 58, 64))):
            px(d, x, y, dk(c, 0.82) if (x + 2 * y) % 5 == 0 else c)
        px(d, x, 44, dk(WALL, 0.84))
    for x in range(xa + 30, xb, 92):
        rect(d, x, 30, x + 2, 35, PAINT[2])
        vl(d, x, 30, 35, PAINT[3])
        vl(d, x + 2, 30, 35, PAINT[0])
    for x in range(xa + 8, xb, 24):                                # 电缆卡子
        rect(d, x, 39, x + 1, 44, (150, 156, 150))
        px(d, x + 1, 44, (90, 96, 92))


# ============================================================ 各处的设备（从左到右）
def draw_fwd_bulkhead(d):
    """艏部横隔舱壁（x 0–29）：暗一点的钢板 + 竖加强筋；中间一扇关着的椭圆水密门（厚门框、门扇左亮右暗、一圈压紧扳手、
    右边两个铰链、门上一块黄铜小牌）。"""
    rect(d, 0, 0, FWD_X, KICK + 7, (118, 130, 116))
    for x in (2, 26):
        vl(d, x, 0, KICK + 6, (136, 148, 132))
        vl(d, x + 1, 0, KICK + 6, (98, 108, 98))
    vl(d, FWD_X, 0, KICK + 7, INK)
    cx, cy, rx, ry = 14.5, 96.0, 10.5, 38.0
    for y in range(int(cy - ry - 4), int(cy + ry + 5)):
        for x in range(0, FWD_X):
            e = ((x - cx) / (rx + 3)) ** 2 + ((y - cy) / (ry + 3)) ** 2
            e2 = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if e2 <= 1.0:
                c = (138, 150, 134)
                if x - cx < -rx * 0.55:
                    c = (156, 168, 150)
                elif x - cx > rx * 0.6:
                    c = (112, 124, 110)
                px(d, x, y, c)
            elif e <= 1.0:
                s = (x - cx) / rx * 0.5 + (y - cy) / ry
                px(d, x, y, (164, 176, 158) if s < -0.4 else ((92, 102, 92) if s > 0.5 else (124, 136, 120)))
    for ang in range(0, 360, 60):                                  # 压紧扳手（一圈六个）
        a_ = math.radians(ang + 30)
        u = int(round(cx + (rx + 1.5) * math.cos(a_)))
        v = int(round(cy + (ry + 1.5) * math.sin(a_)))
        rect(d, u - 1, v - 1, u + 1, v, (70, 76, 80))
        px(d, u - 1, v - 1, (170, 176, 172))
    for y in (70, 122):                                            # 铰链
        rect(d, 24, y, 27, y + 4, (80, 88, 86))
        vl(d, 24, y, y + 4, (150, 158, 152))
    rect(d, 11, 80, 18, 84, BRASS[1])                              # 门上的小铜牌
    hl(d, 11, 18, 80, BRASS[3])
    for x in range(12, 18, 2):
        px(d, x, 82, BRASS[0])
    hl(d, 0, FWD_X, KICK + 7, (58, 62, 60))


def draw_gauge_pipe(d):
    """压力表那根竖管（x 31–34）：从墙上部的水管下来、钻进甲板；两个法兰、两个卡子。"""
    for y in range(35, FLOOR - 1):
        for k, c in enumerate((PAINT[3], PAINT[2], PAINT[1], PAINT[0])):
            px(d, 31 + k, y, c)
    for y in (58, 96):
        rect(d, 30, y, 35, y + 2, PAINT[2])
        hl(d, 30, 35, y, PAINT[3])
        hl(d, 30, 35, y + 2, PAINT[0])
    for y in (74, 136):
        hl(d, 30, 36, y, (150, 156, 150))
        px(d, 36, y, (80, 88, 84))


def draw_helm(d):
    """操舵台（x 44–120）：绿漆钢台（台面亮沿、面板上一排拨动开关、小电表、三盏指示灯、下面的百叶、踢脚凹进去），
    台上竖起一根轴撑着黄铜舵轮（八根辐条、伸出来的把手）；墙上的深度计（黄铜表圈、奶白表盘、刻度、黑指针、下面一块黑铭牌）、
    从墙上部下来的黄铜传声筒（喇叭口 + 链子拴的盖）；台面右端的罗盘是 12 件金属之一（obj_compass）。"""
    x0, x1 = 44, 120
    rect(d, x0, 125, x1, 148, PAINT[2])
    hl(d, x0, x1, 125, PAINT[3])
    hl(d, x0, x1, 126, lt(PAINT[3], 0.12))
    hl(d, x0, x1, 127, PAINT[1])
    vl(d, x0, 125, 148, PAINT[3])
    vl(d, x1, 125, 148, PAINT[0])
    for (x, y) in ((x0 + 2, 129), (x1 - 2, 129), (x0 + 2, 143), (x1 - 2, 143)):
        px(d, x, y, PAINT[0])                                      # 面板螺丝
    for i, x in enumerate(range(50, 92, 6)):                       # 拨动开关
        rect(d, x, 131, x + 2, 133, (60, 66, 70))
        px(d, x + 1, 130 - (i % 2), (200, 206, 204))
        px(d, x + 1, 131, (150, 156, 156))
    rect(d, 50, 136, 61, 142, INK)                                 # 小电表
    rect(d, 51, 137, 60, 141, CREAM)
    d.line((52, 141, 57, 138), fill=C(INK))
    for x in (96, 102, 108):                                       # 指示灯（亮的在 strip blink）
        rect(d, x - 1, 136, x + 1, 138, (54, 58, 62))
    for y in (143, 145):                                           # 百叶
        hl(d, 66, 92, y, PAINT[0])
    rect(d, x0 + 1, 146, x1 - 1, 148, PAINT[0])                    # 踢脚凹进去
    # 舵轮的轴 + 舵轮
    cx, cy = WHEEL
    rect(d, cx - 1, cy, cx + 1, 125, STEEL[2])
    vl(d, cx - 1, cy, 125, STEEL[3])
    vl(d, cx + 1, cy, 125, STEEL[1])
    for k in range(8):                                             # 辐条 + 伸出来的把手
        ang = math.radians(k * 45 + 22.5)
        for r in np.arange(1.5, 12.6, 0.5):
            u, v = int(round(cx + r * math.cos(ang))), int(round(cy + r * math.sin(ang)))
            c = BRASS[2] if r < 9 else (WOOD[3] if r < 11.5 else WOOD[1])
            px(d, u, v, c)
    for (u, v) in disc_pts(cx, cy, 9.6):
        r = math.hypot(u - cx, v - cy)
        if r > 8.2:
            s = (u - cx) + (v - cy)
            px(d, u, v, BRASS[3] if s < -4 else (BRASS[0] if s > 5 else BRASS[2] if s < 1 else BRASS[1]))
    for (u, v) in disc_pts(cx, cy, 2.2):
        px(d, u, v, BRASS[1])
    px(d, cx - 1, cy - 1, BRASS[3])
    # 深度计
    dx_, dy_ = DEPTH
    for (u, v) in disc_pts(dx_, dy_, 8.4):
        r = math.hypot(u - dx_, v - dy_)
        s = (u - dx_) + (v - dy_)
        if r > 7.4:
            c = INK
        elif r > 6.0:
            c = BRASS[3] if s < -3 else (BRASS[0] if s > 3 else BRASS[2])
        else:
            c = CREAM
        px(d, u, v, c)
    for k in range(9):                                             # 刻度（下面留一个缺口）
        ang = math.radians(135 + k * 33.75)
        u, v = int(round(dx_ + 4.8 * math.cos(ang))), int(round(dy_ + 4.8 * math.sin(ang)))
        px(d, u, v, (96, 90, 78) if k % 2 else (60, 56, 52))
    rect(d, dx_ - 6, dy_ + 10, dx_ + 6, dy_ + 12, INK)             # 黑铭牌
    for x in range(dx_ - 5, dx_ + 6, 2):
        px(d, x, dy_ + 11, (190, 190, 180))
    # 传声筒（黄铜管从墙上部下来，喇叭口 + 拴着的盖）
    for y in range(45, 88):
        px(d, 117, y, BRASS[3])
        px(d, 118, y, BRASS[2])
        px(d, 119, y, BRASS[0])
    for y in (60, 76):
        hl(d, 116, 120, y, (150, 156, 150))
    for j, (a_, b_) in enumerate(((115, 121), (114, 122), (114, 122))):
        hl(d, a_, b_, 88 + j, BRASS[3] if j == 0 else BRASS[1])
    hl(d, 115, 121, 91, INK)
    P.wire(d, 121, 89, 120, 98, 2, (90, 90, 92))
    rect(d, 118, 98, 121, 99, BRASS[1])


def draw_manifold(d):
    """阀组（x 130–180）：一根竖管从墙上部下来接横的总管（y 120–125，两头法兰），总管右端一个往下的弯头钻进甲板；
    总管上的红手轮是 12 件金属之一（obj_valve）。上面一个配电箱（门、闸刀把手、黄色警告牌、穿线管），墙脚一只小铁桶接滴水。"""
    for y in range(45, 121):                                       # 竖管
        for k, c in enumerate((PAINT[3], PAINT[2], PAINT[1], PAINT[0])):
            px(d, 134 + k, y, c)
    rect(d, 133, 64, 138, 66, PAINT[2])
    hl(d, 133, 138, 64, PAINT[3])
    for x in range(130, 179):                                      # 总管
        for y, c in zip(range(120, 126), (PAINT[3], PAINT[3], PAINT[2], PAINT[2], PAINT[1], PAINT[0])):
            px(d, x, y, c)
    px(d, 130, 126, dk(WALL, 0.8))
    hl(d, 130, 178, 126, dk(WALL, 0.84))
    for x in (130, 142, 162, 176):                                 # 法兰
        rect(d, x, 119, x + 2, 126, PAINT[2])
        vl(d, x, 119, 126, PAINT[3])
        vl(d, x + 2, 119, 126, PAINT[0])
    rect(d, 150, 117, 154, 119, STEEL[2])                          # 阀门的阀盖（手轮在 obj_valve）
    for y in range(126, FLOOR - 1):                                # 右端往下的管子
        for k, c in enumerate((PAINT[3], PAINT[2], PAINT[1], PAINT[0])):
            px(d, 166 + k, y, c)
    rect(d, 165, 134, 170, 136, PAINT[2])
    hl(d, 165, 170, 134, PAINT[3])
    # 配电箱
    bx0, by0, bx1, by1 = 148, 54, 172, 84
    rect(d, bx0, by0, bx1, by1, (112, 122, 112))
    rect(d, bx0 + 2, by0 + 2, bx1 - 2, by1 - 2, (128, 138, 126))
    hl(d, bx0, bx1, by0, (160, 170, 156))
    vl(d, bx0, by0, by1, (150, 160, 146))
    vl(d, bx1, by0, by1, (78, 86, 78))
    hl(d, bx0, bx1, by1, (70, 78, 70))
    for (x, y) in ((bx0 + 1, by0 + 1), (bx1 - 1, by0 + 1), (bx0 + 1, by1 - 1), (bx1 - 1, by1 - 1)):
        px(d, x, y, (80, 88, 80))
    d.polygon([(158, 60), (154, 67), (162, 67)], fill=C((222, 186, 52)))   # 黄色警告牌
    px(d, 158, 63, INK)
    px(d, 158, 65, INK)
    rect(d, 173, 62, 175, 76, (70, 76, 80))                        # 闸刀把手
    rect(d, 174, 58, 176, 62, (180, 60, 48))
    px(d, 174, 58, (220, 110, 90))
    for x in range(152, 168, 3):                                   # 门下的散热缝
        vl(d, x, 76, 80, (96, 104, 96))
    for y in range(44, by0):                                       # 穿线管
        px(d, 152, y, (150, 154, 150))
        px(d, 153, y, (98, 104, 100))
    # 墙脚的小铁桶（接滴水）
    a_, b_ = BUCKET
    for y in range(142, FLOOR - 1):
        u = (y - 142) / 6.0
        xa, xb = a_ + int(round(u * 0.6)), b_ - int(round(u * 0.6))
        hl(d, xa, xb, y, (150, 156, 158))
        px(d, xa, y, (196, 202, 204))
        px(d, xb, y, (96, 102, 108))
    hl(d, a_, b_, 142, (200, 206, 208))
    hl(d, a_ + 1, b_ - 1, 143, (70, 90, 104))                      # 桶里的水
    d.arc((a_, 137, b_, 147), 200, 340, fill=C((110, 116, 120)))   # 提梁


def draw_periscope(d):
    """潜望镜（x 174–204）：顶棚的套筒（粗）+ 法兰、钢管（左亮右暗、三道箍）垂下来，下端目镜箱在人眼的高度（y 116–130：
    站在 anchors.periscope 的人正好凑上去）、左边黑色眼罩、面板上一个小窗；两只折起来的把手（竖着，端头一个球）。"""
    for y in range(0, 12):                                         # 套筒
        for k, x in enumerate(range(183, 198)):
            c = (132, 140, 140) if k < 3 else ((104, 112, 112) if k < 11 else (78, 84, 86))
            px(d, x, y, dk(c, 0.8))
    rect(d, 181, 11, 199, 13, (120, 128, 128))
    hl(d, 181, 199, 11, (170, 178, 176))
    hl(d, 181, 199, 13, (70, 76, 78))
    y0, y1 = 116, 130
    for y in range(14, y0 + 1):                                    # 镜管
        for k, c in enumerate(((178, 186, 186), (156, 164, 166), (132, 140, 144), (120, 128, 132), (104, 112, 116),
                               (84, 90, 96), (62, 68, 74))):
            px(d, 187 + k, y, c)
    for y in (32, 62, 94):
        rect(d, 186, y, 194, y + 1, (100, 108, 110))
        hl(d, 186, 194, y, (176, 184, 184))
    # 目镜箱
    x0, x1 = 181, 199
    rect(d, x0, y0, x1, y1, (110, 118, 120))
    hl(d, x0 + 1, x1 - 1, y0, (170, 178, 178))
    vl(d, x0, y0 + 1, y1 - 1, (150, 158, 158))
    vl(d, x1, y0 + 1, y1 - 1, (66, 72, 76))
    hl(d, x0 + 1, x1 - 1, y1, (60, 66, 70))
    for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        px(d, x, y, dk(WALL, 0.9))                                 # 圆角
    rect(d, 177, y0 + 4, 180, y0 + 9, (40, 40, 44))                # 眼罩
    px(d, 177, y0 + 4, (70, 70, 74))
    rect(d, 185, y0 + 4, 195, y0 + 8, (90, 98, 100))               # 面板上的小窗 + 刻度
    hl(d, 186, 194, y0 + 6, (60, 66, 70))
    for x in range(186, 195, 2):
        px(d, x, y0 + 5, (190, 196, 190))
    for (hx, s) in ((174, -1), (202, 1)):                          # 折起来的把手（横杆接到箱子上，竖着折上去）
        rect(d, hx, y0 + 3, hx + 1, y0 + 15, (78, 84, 88))
        vl(d, hx, y0 + 3, y0 + 15, (150, 158, 160))
        rect(d, hx - 1, y0 + 15, hx + 2, y0 + 17, (50, 50, 54))
        px(d, hx - 1, y0 + 15, (110, 110, 116))
        if s < 0:
            hl(d, hx + 2, 176, y0 + 10, (96, 104, 108))
        else:
            hl(d, 200, hx - 1, y0 + 10, (96, 104, 108))
    rect(d, 188, y1 + 1, 192, y1 + 3, (90, 98, 100))               # 下端
    hl(d, 188, 192, y1 + 3, (54, 58, 62))


def draw_binoculars_hook(d):
    """挂望远镜的钩子 + 带子（望远镜本身是 obj_binoculars）。"""
    x, y = OBJ['binoculars']
    rect(d, x - 2, y - 15, x + 1, y - 13, (80, 86, 88))            # 钩座
    px(d, x - 2, y - 15, (160, 166, 164))
    vl(d, x - 1, y - 12, y - 10, (70, 74, 78))
    px(d, x, y - 10, (70, 74, 78))
    d.line((x - 4, y - 5, x - 1, y - 10), fill=C((92, 66, 44)))    # 带子
    d.line((x + 3, y - 5, x, y - 10), fill=C((92, 66, 44)))


def draw_chart_table(d):
    """海图桌（x 236–314）：木桌面（亮沿 + 黄铜包边）、桌下两个抽屉（黄铜拉手）、踢脚；桌上一卷海图、分规、
    红皮航海日志（剧情纪念品 chart + 12 = 292）；墙上钉着一张红海的海图；收音机（obj_radio）的天线线拉到墙上部。"""
    x0, x1 = 236, 314
    rect(d, x0, 129, x1, 131, WOOD[3])
    hl(d, x0, x1, 129, lt(WOOD[3], 0.18))
    hl(d, x0, x1, 131, BRASS[1])
    rect(d, x0 + 2, 132, x1 - 2, 148, WOOD[1])
    vl(d, x0 + 2, 132, 148, WOOD[2])
    vl(d, x1 - 2, 132, 148, WOOD[0])
    for (a_, b_) in ((x0 + 5, 272), (276, x1 - 5)):                # 抽屉
        rect(d, a_, 134, b_, 141, WOOD[2])
        hl(d, a_, b_, 134, WOOD[3])
        hl(d, a_, b_, 141, WOOD[0])
        m = (a_ + b_) // 2
        rect(d, m - 2, 137, m + 2, 138, BRASS[2])
        px(d, m - 2, 137, BRASS[3])
    for x in range(x0 + 4, x1 - 3, 3):                             # 木纹
        if hash01(x, 31) < 0.4:
            vl(d, x, 143, 147, WOOD[0])
    rect(d, x0 + 3, 146, x1 - 3, 148, WOOD[0])
    # 桌上：一卷海图（横放的圆筒）、分规、航海日志
    rect(d, 272, 125, 286, 128, (226, 218, 190))
    hl(d, 272, 286, 125, (244, 240, 222))
    hl(d, 272, 286, 128, (176, 168, 140))
    vl(d, 286, 125, 128, (196, 186, 156))
    px(d, 287, 126, (160, 150, 126))
    d.line((296, 128, 300, 122), fill=C(BRASS[2]))                 # 分规
    d.line((304, 128, 300, 122), fill=C(BRASS[1]))
    px(d, 300, 121, BRASS[3])
    rect(d, 288, 125, 296, 128, (140, 40, 36))                     # 航海日志（红皮）
    hl(d, 288, 296, 125, (178, 64, 54))
    hl(d, 289, 296, 127, (232, 224, 200))                          # 书页
    vl(d, 288, 125, 128, (100, 28, 26))
    # 墙上的海图（钉着，四角图钉）：纸色 + 海是浅蓝、岸是土黄（红海：一道斜着的长条海）
    mx0, my0, mx1, my1 = 252, 86, 300, 112
    rect(d, mx0, my0, mx1, my1, (226, 216, 184))
    for y in range(my0 + 2, my1 - 1):
        for x in range(mx0 + 2, mx1 - 1):
            u = (x - mx0) / float(mx1 - mx0)
            v = (y - my0) / float(my1 - my0)
            c_ = 0.5 + 0.35 * (u - 0.5) - 0.9 * (v - 0.5) * 0.4
            if abs(v - (0.2 + 0.7 * u)) < 0.16 + 0.04 * math.sin(u * 9):
                px(d, x, y, (150, 186, 196))                       # 红海
            elif hash01(x // 2, y // 2, 41) < 0.12:
                px(d, x, y, (200, 178, 132))
            else:
                px(d, x, y, (222, 206, 160))
            del c_
    d.line((mx0 + 6, my0 + 6, mx1 - 8, my1 - 4), fill=C((160, 70, 60)))   # 航线（红笔）
    for (x, y) in ((mx0 + 6, my0 + 6), (mx0 + 20, my0 + 11), (mx1 - 8, my1 - 4)):
        px(d, x, y, (200, 50, 40))
    hl(d, mx0, mx1, my1, (170, 160, 130))
    vl(d, mx1, my0, my1, (170, 160, 130))
    for (x, y) in ((mx0, my0), (mx1, my0), (mx0, my1), (mx1, my1)):
        px(d, x, y, (190, 40, 36))
    # 收音机的天线线
    rx, ry = OBJ['radio']
    vl(d, rx + 3, 46, ry - 6, (60, 60, 64))
    for y in range(52, ry - 6, 12):
        px(d, rx + 4, y, (170, 170, 164))                          # 线卡


def draw_toolboard(d):
    """工具板（x 310–332，y 98–138）：浅色的洞洞板（一格格小黑洞）、画着白色工具轮廓（锤子、起子空着，只剩轮廓），
    中间两根挂钉挂着大扳手（obj_wrench）。"""
    x0, y0, x1, y1 = 310, 98, 332, 138
    rect(d, x0, y0, x1, y1, (146, 132, 102))                       # 洞洞板深一点：亮的钢扳手才跳得出来
    hl(d, x0, x1, y0, (174, 162, 130))
    vl(d, x0, y0, y1, (168, 156, 124))
    vl(d, x1, y0, y1, (104, 94, 72))
    hl(d, x0, x1, y1, (98, 88, 68))
    for y in range(y0 + 3, y1 - 1, 4):
        for x in range(x0 + 3, x1 - 1, 4):
            px(d, x, y, (92, 82, 62))
    # 空着的锤子轮廓（左上）、起子轮廓（右下）
    W_ = (238, 236, 226)
    rect(d, x0 + 2, y0 + 4, x0 + 8, y0 + 6, None, outline=W_)
    vl(d, x0 + 5, y0 + 7, y0 + 16, W_)
    vl(d, x1 - 4, y1 - 16, y1 - 3, W_)
    rect(d, x1 - 5, y1 - 8, x1 - 3, y1 - 3, None, outline=W_)
    # 扳手的挂钉
    x, y = OBJ['wrench']
    px(d, x + 2, y - 6, (60, 56, 50))
    px(d, x - 3, y + 5, (60, 56, 50))
    rect(d, x0 + 3, y1 - 6, x0 + 9, y1 - 3, (190, 180, 120))       # 一块小标签
    hl(d, x0 + 4, x0 + 8, y1 - 5, (120, 110, 70))


def draw_galley(d):
    """小厨房（x 344–404）：不锈钢台面（亮沿）+ 两扇柜门；电炉 + 搪瓷咖啡壶（蓝灰带白点、壶嘴朝左、把手朝右）；
    金属杯是 obj_metal_cup；墙上的挂杯架（木条 + 三只白色搪瓷杯）；椭圆刮胡镜 + 镜下的小搁板（剃刀是 obj_razor、旁边一支刷子）。"""
    x0, x1 = 344, 404
    rect(d, x0, 139, x1, 141, (178, 184, 186))
    hl(d, x0, x1, 139, (214, 220, 222))
    hl(d, x0, x1, 141, (110, 116, 120))
    rect(d, x0 + 1, 142, x1 - 1, 148, (112, 124, 112))
    for (a_, b_) in ((x0 + 3, 372), (376, x1 - 3)):                 # 柜门
        rect(d, a_, 143, b_, 147, (124, 136, 122))
        hl(d, a_, b_, 143, (146, 158, 142))
        vl(d, b_, 143, 147, (92, 102, 92))
        px(d, (b_ - 2) if a_ < 372 else (a_ + 2), 145, (190, 196, 196))
    # 电炉 + 咖啡壶
    a_, b_ = POT
    rect(d, a_ - 1, 136, b_ + 1, 138, (54, 54, 58))
    hl(d, a_ - 1, b_ + 1, 136, (92, 92, 96))
    hl(d, a_, b_, 138, (150, 64, 40))                              # 电炉丝的一点红
    for y in range(127, 136):                                      # 壶身（下宽上窄）
        u = (y - 127) / 8.0
        xa, xb = a_ + 1 - int(round(u)), b_ - 1 + int(round(u))
        for x in range(xa, xb + 1):
            c = (100, 124, 152)
            if x == xa:
                c = (140, 164, 188)
            elif x == xb:
                c = (66, 84, 110)
            if hash01(x, y, 51) < 0.12:
                c = (214, 222, 228)                                # 搪瓷上的白点
            px(d, x, y, c)
    hl(d, a_ + 1, b_ - 1, 126, (150, 172, 194))                    # 壶盖 + 盖钮
    px(d, (a_ + b_) // 2, 125, INK)
    d.line((a_ - 1, 131, a_ - 3, 128), fill=C((100, 124, 152)))    # 壶嘴
    px(d, a_ - 3, 128, (140, 164, 188))
    vl(d, b_ + 1, 128, 133, (66, 84, 110))                         # 把手
    px(d, b_ + 2, 129, (66, 84, 110))
    px(d, b_ + 2, 132, (66, 84, 110))
    # 挂杯架 + 三只白色搪瓷杯（蓝边）
    hl(d, 358, 382, 104, WOOD[3])
    hl(d, 358, 382, 105, WOOD[1])
    for cx in (362, 370, 378):
        px(d, cx, 106, (60, 60, 64))
        rect(d, cx - 2, 107, cx + 1, 111, (232, 232, 224))
        hl(d, cx - 2, cx + 1, 107, (70, 100, 160))                 # 蓝杯沿
        vl(d, cx + 1, 108, 111, (188, 188, 182))
        px(d, cx + 2, 109, (200, 200, 194))
        hl(d, cx - 2, cx + 1, 112, (150, 150, 146))
    # 刮胡镜（椭圆，深色框，镜面浅灰蓝 + 一道斜的反光）+ 小搁板
    mx, my, rx, ry = 395.0, 106.0, 7.0, 10.0
    for y in range(int(my - ry) - 1, int(my + ry) + 2):
        for x in range(int(mx - rx) - 1, int(mx + rx) + 2):
            e = ((x - mx) / rx) ** 2 + ((y - my) / ry) ** 2
            if e <= 1.0:
                c = (176, 194, 202) if (x - mx) + (y - my) * 0.5 < 0 else (150, 168, 178)
                if abs((x - mx) + (y - my) * 0.7 + 2) < 0.8:
                    c = (226, 236, 240)
                px(d, x, y, c)
            elif e <= 1.32:
                px(d, x, y, WOOD[1] if (x - mx) + (y - my) > 0 else WOOD[2])
    rect(d, 386, 133, 404, 134, WOOD[3])
    hl(d, 386, 404, 134, WOOD[0])
    for x in (388, 402):
        d.line((x, 135, x + (2 if x < 395 else -2), 138), fill=C(WOOD[0]))
    vl(d, 388, 128, 132, WOOD[2])                                  # 刷子：木柄 + 白毛
    vl(d, 389, 128, 132, WOOD[1])
    rect(d, 387, 125, 390, 127, (232, 228, 214))
    px(d, 390, 125, (200, 196, 182))


def draw_lockers(d):
    """两个窄长铁皮柜（x 412–428，y 66–148）：上下两排百叶通风口、竖把手、小号码牌；柜顶放着一卷叠好的毛巾。"""
    for i, x0 in enumerate((412, 421)):
        x1 = x0 + 7
        rect(d, x0, 66, x1, 148, (122, 136, 124))
        vl(d, x0, 66, 148, (150, 164, 150))
        vl(d, x1, 66, 148, (88, 100, 90))
        hl(d, x0, x1, 66, (160, 172, 158))
        for y0 in (72, 132):
            for y in range(y0, y0 + 7, 2):
                hl(d, x0 + 2, x1 - 2, y, (78, 90, 80))
                hl(d, x0 + 2, x1 - 2, y + 1, (140, 152, 140))
        rect(d, x1 - 2, 100, x1 - 1, 108, (180, 186, 184))
        px(d, x1 - 1, 108, (90, 96, 96))
        rect(d, x0 + 2, 84, x0 + 5, 86, (226, 222, 196))
        px(d, x0 + 3, 85, INK)
        if i:
            px(d, x0 + 4, 85, INK)
    rect(d, 413, 61, 426, 65, (196, 184, 150))                     # 毛巾
    hl(d, 413, 426, 61, (222, 212, 180))
    hl(d, 413, 426, 63, (170, 156, 124))


def draw_bunks(d):
    """双层铺位（x 430–470）：钢管床架、条纹床垫、灰毯子（一道红条）、枕头；帘子（帆布）从帘杆垂下来，只拉了右半边；
    下铺下面一个抽屉；上铺墙上钉着一张小照片。"""
    x0, x1 = 430, 470
    for x in (x0, x1 - 1):
        vl(d, x, 84, 148, (176, 184, 184))
        vl(d, x + 1, 84, 148, (104, 112, 116))
    for (top, base) in ((99, 106), (129, 136)):
        rect(d, x0 + 2, base, x1 - 2, base + 1, (96, 104, 108))   # 床板 / 床架
        hl(d, x0 + 2, x1 - 2, base, (150, 158, 160))
        for y in range(top + 2, base):                             # 床垫（蓝白条纹的边）
            for x in range(x0 + 2, x1 - 1):
                c = (214, 216, 212) if (x // 2) % 2 else (150, 166, 196)
                if y == base - 1:
                    c = dk(c, 0.8)
                px(d, x, y, c)
        for y in range(top, top + 3):                              # 毯子
            for x in range(x0 + 10, x1 - 1):
                c = (120, 122, 120) if (x + y) % 5 else (104, 106, 104)
                if 30 <= x - x0 <= 32:
                    c = (156, 54, 44)
                px(d, x, y, c)
        hl(d, x0 + 10, x1 - 2, top, (150, 152, 150))
        rect(d, x0 + 2, top, x0 + 8, top + 3, (230, 226, 210))     # 枕头
        hl(d, x0 + 2, x0 + 8, top, (244, 242, 232))
        px(d, x0 + 8, top + 3, (190, 186, 170))
    rect(d, x0 + 3, 139, x1 - 3, 147, (118, 130, 120))             # 抽屉
    hl(d, x0 + 3, x1 - 3, 139, (146, 158, 146))
    hl(d, x0 + 3, x1 - 3, 147, (84, 96, 86))
    for x in (442, 458):
        rect(d, x - 1, 142, x + 1, 143, (186, 192, 190))
    rect(d, 437, 88, 441, 93, (232, 226, 206))                     # 小照片
    rect(d, 438, 89, 440, 92, (120, 106, 92))
    px(d, 439, 89, (200, 170, 140))
    # 帘杆 + 帘子（右半边，竖着的褶）
    for (ry, bottom) in ((86, 105), (114, 135)):
        hl(d, x0 + 1, x1 - 1, ry, (180, 186, 186))
        for x in range(452, x1 - 1):
            for y in range(ry + 1, bottom + 1):
                k = (x - 452) % 4
                c = (CANVAS[3], CANVAS[2], CANVAS[2], CANVAS[1])[k]
                if y == bottom:
                    c = CANVAS[0]
                px(d, x, y, c)
        for x in range(452, x1 - 1, 2):
            px(d, x, ry + 1, (90, 90, 92))                         # 帘环


def draw_elbow_pipes(d):
    """弯管两头的直管：竖的往下钻进甲板（一个法兰）、横的往右沿墙走到 578，再弯上去钻进墙上部（两个法兰）。
    弯头本身是 obj_pipe_elbow，这里只画框外的部分。"""
    x, y = OBJ['pipe_elbow']
    x0, y0 = x - 5, y - 5
    for yy in range(y0 + 10, FLOOR - 1):                           # 竖的
        for k, c in enumerate((STEEL[4], STEEL[3], STEEL[1])):
            px(d, x0 + k, yy, c)
        px(d, x0 + 3, yy, INK)
    rect(d, x0 - 1, y0 + 12, x0 + 3, y0 + 13, STEEL[2])
    hl(d, x0 - 1, x0 + 3, y0 + 12, STEEL[4])
    xr = 578
    for xx in range(x0 + 10, xr):                                  # 横的
        for k, c in enumerate((STEEL[4], STEEL[3], STEEL[1])):
            px(d, xx, y0 + k, c)
        px(d, xx, y0 + 3, INK)
    for fx in (x0 + 12, 532):
        rect(d, fx, y0 - 1, fx + 1, y0 + 3, STEEL[2])
        vl(d, fx, y0 - 1, y0 + 3, STEEL[4])
    for yy in range(45, y0 + 3):                                   # 右端弯上去
        for k, c in enumerate((STEEL[4], STEEL[3], STEEL[1])):
            px(d, xr + k, yy, c)
        px(d, xr + 3, yy, INK)
    px(d, xr, y0, STEEL[3])


def draw_suit(d, cx, top, sd):
    """一套挂着的帆布潜水服（衣架挂在领口）：黄铜领圈、往两边鼓的肩、身子（几道竖褶 + 腰带）、两只袖子垂在两边
    （和身子之间留一道缝，袖口是黑橡胶）、两条腿（中间一道缝，裤脚收紧）。光从左上来：左边亮、右边暗。"""
    rect(d, cx - 1, top - 3, cx + 1, top - 1, (80, 86, 88))       # 挂钩
    px(d, cx - 1, top - 3, (160, 166, 164))
    cl = CANVAS
    for y in range(top + 3, top + 62):
        u = y - top
        if u < 7:
            half = 4 + u                                           # 肩往两边鼓
        elif u < 32:
            half = 9 - (1 if u > 26 else 0)                        # 身子
        else:
            half = 7                                               # 两条腿
        for x in range(cx - half, cx + half + 1):
            k = x - (cx - half)
            c = cl[3] if k < 2 else (cl[2] if k < 2 * half - 1 else cl[1])
            if u >= 32 and abs(x - cx) <= 0:
                c = cl[0]                                          # 两腿中间的缝
            elif u >= 32 and (x - cx) in (-1, 1):
                c = cl[1]
            if hash01(x, u // 4, sd, 61) < 0.06 or (u > 8 and (x - cx + sd) % 5 == 0 and u < 30):
                c = dk(c, 0.88)                                    # 褶子
            if u in (24, 25):
                c = (86, 66, 46) if u == 24 else (64, 48, 36)      # 腰带
            px(d, x, y, c)
        if u >= 58:                                                # 裤脚收紧
            px(d, cx - half, y, dk(WALL, 0.85))
            px(d, cx + half, y, dk(WALL, 0.85))
    for side in (-1, 1):                                           # 袖子（和身子之间一道缝）
        ax = cx + side * 11
        for y in range(top + 8, top + 34):
            px(d, ax, y, cl[2] if side < 0 else cl[1])
            px(d, ax + side, y, cl[3] if side < 0 else cl[0])
            px(d, ax - side, y, dk(WALL, 0.8))                     # 缝里的暗
        rect(d, min(ax, ax + side), top + 34, max(ax, ax + side), top + 37, (40, 40, 46))   # 黑橡胶袖口
    for (u, v) in disc_pts(cx, top + 3, 3.4):                      # 黄铜领圈（中间是空的）
        r = math.hypot(u - cx, v - top - 3)
        if r > 1.7:
            px(d, u, v, BRASS[3] if v < top + 2 else (BRASS[2] if v < top + 4 else BRASS[1]))
        else:
            px(d, u, v, (40, 36, 34))


def draw_gear(d):
    """潜水装备（x 494–578）：挂着的一卷黑气管、墙上的氧气瓶托架（氧气瓶是 obj_oxygen_tank）、搁板 + 黄铜潜水头盔
    （圆顶、正面圆窗带护栅、两边小窗、下面的领盘、一圈螺栓）、两个挂钩挂着帆布潜水服（铜领圈、袖子垂着、黑橡胶袖口）、
    墙脚的矮木凳（潜水靴是 obj_diving_boot）。"""
    # 一卷气管（挂在钩子上的黑圈）
    hx, hy = 506, 70
    rect(d, hx - 1, hy - 3, hx + 1, hy - 1, (80, 86, 88))
    for (u, v) in disc_pts(hx, hy + 9, 7.4):
        r = math.hypot(u - hx, v - hy - 9)
        if r > 4.6:
            c = (56, 54, 58) if (u + v) % 3 else (34, 32, 38)
            if (u - hx) + (v - hy - 9) < -6:
                c = (92, 90, 94)
            px(d, u, v, c)
    vl(d, hx + 6, hy + 14, hy + 26, (46, 44, 50))                  # 垂下来的一截 + 铜接头
    rect(d, hx + 5, hy + 26, hx + 7, hy + 28, BRASS[2])
    # 氧气瓶托架（框外的那一点：上下两个卡座）
    ox, oy = OBJ['oxygen_tank']
    for yy in (oy - 2, oy + 4):
        px(d, ox - 4, yy, (60, 64, 66))
        px(d, ox + 3, yy, (60, 64, 66))
    # 搁板 + 头盔
    rect(d, 514, 104, 548, 105, WOOD[3])
    hl(d, 514, 548, 105, WOOD[0])
    for x in (517, 545):
        d.line((x, 106, x + (3 if x < 530 else -3), 110), fill=C((80, 86, 88)))
    cx, cy = 529.0, 94.0
    for (u, v) in disc_pts(cx, cy, 8.4):                           # 圆顶
        if v > cy + 5:
            continue
        s = (u - cx) * 0.8 + (v - cy)
        c = BRASS[3] if s < -5 else (BRASS[2] if s < -1 else (BRASS[1] if s < 4 else BRASS[0]))
        px(d, u, v, c)
    for y in range(int(cy + 5), 104):                              # 领盘（下宽）
        u = (y - cy - 5) / 4.0
        xa, xb = int(cx - 8 - 3 * u), int(cx + 8 + 3 * u)
        for x in range(xa, xb + 1):
            c = BRASS[2] if x < cx - 3 else (BRASS[1] if x < cx + 5 else BRASS[0])
            px(d, x, y, c)
    for x in range(int(cx - 9), int(cx + 11), 3):                  # 领盘的一圈螺栓
        px(d, x, 101, BRASS[3])
    for (u, v) in disc_pts(cx + 1, cy, 3.6):                       # 正面圆窗 + 护栅
        r = math.hypot(u - cx - 1, v - cy)
        px(d, u, v, INK if r > 2.6 else (52, 70, 84))
    vl(d, int(cx + 1), int(cy - 3), int(cy + 3), BRASS[2])
    hl(d, int(cx - 2), int(cx + 4), int(cy), BRASS[2])
    px(d, int(cx), int(cy - 2), (150, 180, 196))
    for (u, v) in ((cx - 6, cy - 1), (cx + 7, cy - 1)):            # 两边小窗
        rect(d, int(u) - 1, int(v) - 1, int(u) + 1, int(v) + 1, INK)
        px(d, int(u), int(v), (60, 80, 96))
    # 两套帆布潜水服（后面那套先画）
    draw_suit(d, 567, 58, 2)
    draw_suit(d, 551, 58, 1)
    # 矮木凳
    rect(d, 538, 147, 576, 148, WOOD[3])
    hl(d, 538, 576, 147, lt(WOOD[3], 0.15))
    for x in (540, 573):
        px(d, x, 148, WOOD[0])


def draw_ladder_aft(d):
    """直梯（x 580–596，通往指挥塔，顶上的舱口盖开着：里面黑、盖子斜在右上）+ 艉部横隔舱壁和水密门
    （厚门框、一圈压紧扳手、左边两个铰链、门上一块铜牌；门把手是 obj_hatch_handle）。"""
    # 顶上的舱口（指挥塔的圆筒，里面黑）+ 开着的盖子
    rect(d, 578, 0, 597, 8, (40, 40, 46))
    vl(d, 578, 0, 8, (120, 126, 126))
    vl(d, 597, 0, 8, (70, 76, 78))
    hl(d, 576, 599, 9, (140, 148, 146))
    hl(d, 576, 599, 10, (80, 86, 86))
    d.polygon([(596, 8), (604, 0), (607, 0), (599, 9)], fill=C((110, 118, 118)))
    d.line((596, 8, 604, 0), fill=C((160, 168, 166)))
    # 艉部横隔舱壁
    rect(d, AFT_X, 0, PW - 1, KICK + 7, (118, 130, 116))
    vl(d, AFT_X, 0, KICK + 7, INK)
    vl(d, AFT_X + 1, 0, KICK + 7, (150, 162, 146))
    for x in (602, 636):
        vl(d, x, 0, KICK + 6, (136, 148, 132))
        vl(d, x + 1, 0, KICK + 6, (98, 108, 98))
    cx, cy, rx, ry = 619.0, 106.0, 12.0, 37.0
    for y in range(int(cy - ry - 4), int(cy + ry + 5)):
        for x in range(AFT_X + 2, PW):
            e = ((x - cx) / (rx + 3)) ** 2 + ((y - cy) / (ry + 3)) ** 2
            e2 = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if e2 <= 1.0:
                c = (138, 150, 134)
                if x - cx < -rx * 0.55:
                    c = (156, 168, 150)
                elif x - cx > rx * 0.6:
                    c = (112, 124, 110)
                px(d, x, y, c)
            elif e <= 1.0:
                s = (x - cx) / rx * 0.5 + (y - cy) / ry
                px(d, x, y, (164, 176, 158) if s < -0.4 else ((92, 102, 92) if s > 0.5 else (124, 136, 120)))
    for ang in range(0, 360, 60):
        a_ = math.radians(ang)
        u = int(round(cx + (rx + 1.5) * math.cos(a_)))
        v = int(round(cy + (ry + 1.5) * math.sin(a_)))
        rect(d, u - 1, v - 1, u + 1, v, (70, 76, 80))
        px(d, u - 1, v - 1, (170, 176, 172))
    for y in (80, 128):
        rect(d, 605, y, 608, y + 4, (80, 88, 86))
        vl(d, 605, y, y + 4, (150, 158, 152))
    rect(d, 615, 84, 623, 88, BRASS[1])
    hl(d, 615, 623, 84, BRASS[3])
    for x in (617, 621):                                           # 铜牌上的“2”号（两个点）
        px(d, x, 86, BRASS[0])
    hl(d, AFT_X, PW - 1, KICK + 7, (58, 62, 60))
    # 直梯
    for x in (581, 594):
        for y in range(10, FLOOR - 1):
            px(d, x, y, (176, 184, 182))
            px(d, x + 1, y, (100, 108, 108))
    for y in range(16, FLOOR - 2, 7):
        hl(d, 583, 593, y, (190, 196, 194))
        hl(d, 583, 593, y + 1, (84, 90, 92))


DIGITS = {'0': ('111', '101', '101', '101', '111'), '1': ('010', '110', '010', '010', '111'),
          '2': ('111', '001', '111', '100', '111'), '3': ('111', '001', '111', '001', '111'),
          '4': ('101', '101', '111', '001', '001'), '5': ('111', '100', '111', '001', '111'),
          '6': ('111', '100', '111', '101', '111'), '7': ('111', '001', '001', '010', '010'),
          '8': ('111', '101', '111', '101', '111'), '9': ('111', '101', '111', '001', '111')}


def stencil(d, x, y, s, col, seed):
    """喷漆的数字（3×5，字距 1），磨掉一点点。"""
    for i, ch in enumerate(s):
        for j, row in enumerate(DIGITS[ch]):
            for k, b in enumerate(row):
                if b == '1' and hash01(x + i * 4 + k, y + j, seed) > 0.12:
                    px(d, x + i * 4 + k, y + j, col)


def draw_details(d):
    """墙上的生活小物件：肋骨旁边喷的肋位号、操舵台边的舰内电话、潜望镜旁的软木告示板、工具板上面的对讲喇叭、
    厨房墙上的急救箱和日历、柜门上搭的一块擦碗布、直梯脚下甲板上的黄黑警示条。"""
    for i, rx in enumerate(RIBS):                                  # 肋位号
        stencil(d, rx + 8, 50, str(14 + 4 * i), (214, 214, 196), 70 + i)
    # 舰内电话（声力电话）：绿漆盒子 + 挂在右边的黑听筒 + 卷线
    rect(d, 47, 78, 56, 92, PAINT[2])
    hl(d, 47, 56, 78, PAINT[3])
    vl(d, 56, 78, 92, PAINT[0])
    hl(d, 47, 56, 92, PAINT[0])
    rect(d, 49, 81, 54, 83, (60, 66, 68))
    px(d, 50, 86, (200, 60, 50))
    rect(d, 58, 79, 59, 91, (34, 34, 38))
    rect(d, 57, 78, 60, 80, (46, 46, 52))
    rect(d, 57, 90, 60, 92, (46, 46, 52))
    px(d, 57, 78, (90, 90, 96))
    for y in range(93, 101):
        px(d, 58 + (y % 2), y, (40, 40, 44))
    # 软木告示板（几张纸、一张照片、图钉）
    bx0, by0, bx1, by1 = 205, 56, 223, 88
    rect(d, bx0, by0, bx1, by1, WOOD[1])
    rect(d, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, (150, 108, 66))
    for i in range(40):
        x = int(hrange(bx0 + 1, bx1, i, 81))
        y = int(hrange(by0 + 1, by1, i, 82))
        px(d, x, y, (120, 84, 52) if i % 2 else (176, 132, 84))
    for (x0, y0, x1, y1, c, pin) in ((207, 59, 213, 68, (236, 234, 224), (200, 50, 40)),
                                     (215, 60, 221, 72, (226, 214, 170), (230, 190, 50)),
                                     (208, 72, 215, 84, (196, 210, 222), (60, 110, 200))):
        rect(d, x0, y0, x1, y1, c)
        hl(d, x0, x1, y1, dk(c, 0.8))
        for yy in range(y0 + 2, y1 - 1, 2):
            hl(d, x0 + 1, x1 - 1 - (yy % 3), yy, dk(c, 0.72))
        px(d, (x0 + x1) // 2, y0, pin)
    rect(d, 217, 76, 221, 84, (60, 54, 50))                        # 照片
    rect(d, 218, 77, 220, 80, (196, 160, 128))
    hl(d, 218, 220, 82, (120, 96, 80))
    px(d, 219, 75, (200, 50, 40))
    # 对讲喇叭（工具板上面，方的，横格栅 + 红按钮 + 线拉到墙上部）
    rect(d, 314, 66, 327, 80, (74, 78, 82))
    hl(d, 314, 327, 66, (120, 124, 128))
    for y in range(68, 78, 2):
        hl(d, 316, 325, y, (112, 116, 120))
    rect(d, 319, 81, 322, 82, (190, 54, 44))
    for y in range(45, 66):
        px(d, 320, y, (60, 62, 66))
    # 急救箱（白底红十字）
    rect(d, 345, 50, 357, 61, (226, 226, 218))
    hl(d, 345, 357, 50, (244, 244, 238))
    vl(d, 357, 50, 61, (160, 160, 152))
    hl(d, 345, 357, 61, (150, 150, 142))
    rect(d, 350, 52, 352, 59, (200, 40, 36))
    rect(d, 347, 54, 355, 56, (200, 40, 36))
    # 日历（红色月份条 + 日期点，圈了一天）
    rect(d, 364, 62, 378, 84, (236, 234, 226))
    rect(d, 364, 62, 378, 66, (186, 50, 44))
    for x in range(366, 377, 3):
        px(d, x, 64, (240, 220, 210))
    for j in range(5):
        for i in range(5):
            px(d, 366 + i * 3, 69 + j * 3, (120, 120, 116))
    d.ellipse((371, 73, 375, 77), outline=C((200, 40, 36)))
    vl(d, 378, 62, 84, (170, 168, 160))
    hl(d, 364, 378, 84, (170, 168, 160))
    px(d, 371, 60, (90, 90, 92))
    px(d, 371, 61, (60, 60, 64))
    # 搭在柜门上的擦碗布（白底红格）
    for y in range(141, 148):
        for x in range(392, 398):
            c = (232, 228, 220) if (x + y // 2) % 3 else (196, 70, 60)
            if x == 397:
                c = dk(c, 0.8)
            px(d, x, y, c)
    # 直梯脚下甲板上的黄黑警示条（平的漆）
    for y in range(FLOOR + 1, FLOOR + 4):
        for x in range(578, 598):
            px(d, x, y, (214, 176, 50) if ((x + y) // 3) % 2 else (46, 42, 40))


def draw_lamp_housings(d):
    """六盏笼罩灯的灯座 + 搪瓷灯罩 + 铁丝笼（灯泡发光的部分在打光以后画）；两盏警报灯（红玻璃罩，不亮）；两盏应急灯（不亮）。"""
    for lx in LAMPS:
        vl(d, lx, 15, 21, (60, 64, 66))
        rect(d, lx - 4, 22, lx + 4, 24, (64, 86, 70))
        hl(d, lx - 4, lx + 4, 22, (96, 120, 100))
        hl(d, lx - 5, lx + 5, 24, (44, 60, 50))
        for x in (lx - 3, lx, lx + 3):
            vl(d, x, 25, 32, (70, 70, 72))
        hl(d, lx - 3, lx + 3, 32, (70, 70, 72))
        hl(d, lx - 2, lx + 2, 29, (70, 70, 72))
    for (bx, by) in BEACONS:
        rect(d, bx - 4, by - 2, bx + 4, by, (60, 62, 66))
        hl(d, bx - 4, bx + 4, by - 2, (110, 112, 116))
        for (u, v) in disc_pts(bx - 0.5, by + 3, 3.6):
            if v > by:
                px(d, u, v, (120, 36, 34) if (u - bx) + (v - by) > 1 else (156, 52, 48))
        px(d, bx - 2, by + 2, (196, 110, 100))
    for (ex, ey) in EMERG:
        rect(d, ex - 5, ey - 3, ex + 5, ey + 3, (88, 94, 92))
        hl(d, ex - 5, ex + 5, ey - 3, (140, 146, 142))
        rect(d, ex - 3, ey - 1, ex + 3, ey + 2, (96, 44, 36))
        hl(d, ex - 5, ex + 5, ey + 3, (54, 58, 58))


def draw_portholes(d):
    """三个舷窗：黄铜外圈（左上亮、右下暗）+ 一圈 8 个螺栓；玻璃里的海在打光以后画（PORT_BASE），strip 再叠气泡和小鱼。"""
    for (cx, cy) in PORTS:
        for (u, v) in disc_pts(cx, cy, PORT_R):
            r = math.hypot(u - cx, v - cy)
            if r <= GLASS_R:
                px(d, u, v, SEA_IN[1])
                continue
            s = (u - cx) + (v - cy)
            if r > PORT_R - 0.9:
                c = BRASS[0]
            else:
                c = BRASS[3] if s < -6 else (BRASS[2] if s < 0 else (BRASS[1] if s < 6 else BRASS[0]))
            px(d, u, v, c)
        for k in range(8):
            ang = math.radians(k * 45 + 22.5)
            u, v = int(round(cx + 7.8 * math.cos(ang))), int(round(cy + 7.8 * math.sin(ang)))
            px(d, u, v, BRASS[3] if k in (4, 5) else INK)


def contact_shadows(im):
    """设备落在墙上 / 甲板上的影（光在上面偏左）：台子、桌子、柜子、铺位、凳子脚下的甲板暗一窄条。"""
    for (x0, x1) in ((44, 121), (236, 315), (344, 405), (412, 429), (430, 471), (538, 577), (170, 181), (0, FWD_X + 1),
                     (AFT_X, PW - 1)):
        P.mul_box(im, (x0 + 1, FLOOR, x1 + 2, FLOOR + 1), (0.8, 0.8, 0.82))
        P.mul_box(im, (x0 + 2, FLOOR + 2, x1 + 2, FLOOR + 2), (0.9, 0.9, 0.92))
    for (x0, y0, x1, y1) in ((121, 126, 122, 148), (315, 130, 316, 148), (405, 140, 406, 148), (199, 101, 201, 116),
                             (300, 87, 301, 113), (333, 99, 334, 139), (173, 55, 174, 85)):
        P.mul_box(im, (x0, y0, x1, y1), (0.84, 0.84, 0.86))


# ============================================================ 打光
def quant(L, n, bay):
    """光照分 n 档；只在档和档的交界抖一窄条（大片是平的，像手画的光）。"""
    return np.floor(L * n + 0.5 + (bay - 0.5) * 0.28) / n


@lru_cache(maxsize=1)
def light_mult():
    """六盏灯的暖光圈 + 冷的环境光（墙：灯下面一个往下拉长的光圈；甲板：灯正下方一片亮）。分 10 档。"""
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    s = np.zeros((H, PW), np.float32)
    for lx in LAMPS:
        dd = np.hypot(xx - lx, (yy - LAMP_Y) * 0.6)
        s = s + np.clip(1 - dd / 100.0, 0, 1) ** 1.5
    s = np.clip(s, 0, 1)
    bay = A._bayer(PW, H)
    amb = 0.47 + 0.13 * np.clip((yy - 60) / 80.0, 0, 1)
    q = quant(amb + 0.74 * s, 10, bay)
    ca = np.array((0.84, 0.94, 1.06), np.float32)                  # 环境光偏冷
    cp = np.array((1.12, 0.98, 0.74), np.float32)                  # 灯光昏黄
    tint = ca[None, None, :] * (1 - s[..., None]) + cp[None, None, :] * s[..., None]
    m = q[..., None] * tint
    m[:CEIL] *= 0.8
    # 甲板
    sf = np.zeros((H, PW), np.float32)
    for lx in LAMPS:
        dd = np.hypot((xx - lx) * 0.85, (yy - FLOOR) * 2.4)
        sf = sf + np.clip(1 - dd / 100.0, 0, 1) ** 1.4
    sf = np.clip(sf, 0, 1)
    qf = quant(0.74 + 0.34 * sf - 0.012 * np.clip(yy - 168, 0, 12), 10, bay)
    ampf, poolf = np.array((0.9, 0.97, 1.05), np.float32), np.array((1.1, 0.99, 0.82), np.float32)
    tf = ampf[None, None, :] * (1 - sf[..., None]) + poolf[None, None, :] * sf[..., None]
    m[FLOOR:] = (qf[..., None] * tf)[FLOOR:]
    return m


def albedo(with_objects=True):
    """整张舱内（打光以前的颜色，RGBA 不透明）。with_objects=False：不画 12 件金属（自检用：比一比锚点框里画了没有）。"""
    a = wall_base()
    floor_base(a)
    im = Image.fromarray(np.clip(np.concatenate([a, np.full((H, PW, 1), 255, np.float32)], -1), 0, 255).astype(np.uint8),
                         'RGBA')
    d = ImageDraw.Draw(im)
    draw_shell(d)
    draw_fwd_bulkhead(d)
    draw_gauge_pipe(d)
    draw_portholes(d)
    draw_helm(d)
    draw_manifold(d)
    draw_periscope(d)
    draw_binoculars_hook(d)
    draw_chart_table(d)
    draw_toolboard(d)
    draw_galley(d)
    draw_lockers(d)
    draw_bunks(d)
    draw_elbow_pipes(d)
    draw_gear(d)
    draw_ladder_aft(d)
    draw_lamp_housings(d)
    draw_details(d)
    if with_objects:
        draw_objects(d)
    contact_shadows(im)
    return im


def lit(im):
    """打光 + 发光的东西（灯泡 + 光晕、舷窗里的海、指示灯 / 调谐窗的底色）。"""
    a = np.array(im).astype(np.float32)
    a[..., :3] = np.clip(a[..., :3] * light_mult(), 8, 255)
    out = Image.fromarray(a.astype(np.uint8), 'RGBA')
    for lx in LAMPS:
        A._glow(out, lx, LAMP_Y + 1, 24, 15, (255, 206, 130), 46, rings=3)
    d = ImageDraw.Draw(out)
    for lx in LAMPS:
        bulb(d, lx, 1.0)
    for (cx, cy) in PORTS:
        port_glass(d, cx, cy, -1)
    for x in (96, 102, 108):
        px(d, x, 137, (90, 60, 40))
    return out


def bulb(d, lx, k):
    """灯泡（k = 亮度 0..1）：芯最亮、外面一圈暖黄。"""
    c0 = mix((120, 112, 96), (255, 248, 220), k)
    c1 = mix((104, 98, 86), (255, 214, 140), k)
    rect(d, lx - 1, LAMP_Y - 2, lx + 1, LAMP_Y + 2, c1)
    vl(d, lx, LAMP_Y - 1, LAMP_Y + 1, c0)
    px(d, lx - 2, LAMP_Y, c1)
    px(d, lx + 2, LAMP_Y, c1)


def port_glass(d, cx, cy, f):
    """舷窗玻璃里的海：上亮下暗的深蓝、斜斜的一道光；f ≥ 0 时加气泡和小鱼（strip 用），f = −1 只画底色。"""
    for (u, v) in disc_pts(cx, cy, GLASS_R):
        t = (v - (cy - GLASS_R)) / (2 * GLASS_R)
        c = mix(SEA_IN[0], SEA_IN[2], t)
        if abs((u - cx) - (v - cy) * 0.4 + 1) < 1.0 and v < cy + 2:
            c = mix(c, (90, 150, 190), 0.45)                       # 水里斜下来的一道光
        px(d, u, v, c)
    if f >= 0:
        i = PORTS.index((cx, cy))
        for k in range(3):                                         # 气泡：8 帧往上冒一圈
            bx = cx - 3 + k * 3 + (1 if (f + k) % 4 < 2 else 0)
            by = cy + 5 - ((f + k * 3 + i) % 8) * 11 // 8 - 0
            if (bx - cx) ** 2 + (by - cy) ** 2 <= (GLASS_R - 0.8) ** 2:
                px(d, bx, by, (170, 214, 236))
                if k == 1 and (bx - cx) ** 2 + (by - 1 - cy) ** 2 <= (GLASS_R - 0.8) ** 2:
                    px(d, bx, by - 1, (120, 176, 210))
        fx = cx - 9 + ((f * 3 + i * 5) % 24) - 4                   # 小鱼：从左往右游过去（有的帧在窗外）
        fy = cy - 1 + (i % 2) * 2
        for (u, v, c) in ((fx, fy, (232, 196, 80)), (fx + 1, fy, (232, 196, 80)), (fx + 2, fy, (250, 230, 140)),
                          (fx - 1, fy - 1, (200, 160, 60)), (fx - 1, fy + 1, (200, 160, 60))):
            if (u - cx) ** 2 + (v - cy) ** 2 <= (GLASS_R - 0.6) ** 2:
                px(d, u, v, c)
    for (u, v) in ((cx - 3, cy - 4), (cx - 4, cy - 3), (cx - 2, cy - 4)):   # 玻璃的反光
        px(d, u, v, (200, 226, 240))
    px(d, cx + 3, cy + 3, (110, 150, 180))


@lru_cache(maxsize=1)
def near_img():
    return P.opaque(lit(albedo(True)))


@lru_cache(maxsize=1)
def near_bare():
    """不画 12 件金属的版本（只给自检用）。"""
    return lit(albedo(False))


# ============================================================ 会动的（strip）
def port_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    for (cx, cy) in PORTS:
        port_glass(d, cx, cy, f)
    return im


LAMP_K = (1.0, 0.86, 1.0, 0.42, 0.95, 0.7, 1.0, 0.8)              # 接触不好的那盏：每帧亮度都不一样


def lamp_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    lx = LAMPS[FLICKER]
    k = LAMP_K[fno(t)]
    bulb(d, lx, k)
    if k < 0.75:                                                   # 暗下去的时候，灯罩下面那一圈光也暗一点
        for x in range(lx - 4, lx + 5):
            if (x + fno(t)) % 2:
                px(d, x, LAMP_Y + 5, (110, 104, 86))
    return im


def blink_frame(t):
    """操舵台：三盏指示灯轮流亮（红 / 绿 / 黄）、深度计的指针抖一格；收音机：调谐窗的灯一明一暗。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    cols = ((255, 80, 60), (110, 255, 130), (255, 196, 70))
    for i, x in enumerate((96, 102, 108)):
        on = (f + i * 3) % 8 < 4 if i != 1 else f % 2 == 0
        px(d, x, 137, cols[i] if on else dk(cols[i], 0.35))
        if on:
            px(d, x, 136, lt(cols[i], 0.4))
    dx_, dy_ = DEPTH                                               # 深度计的表盘（照抄打好光的近景）+ 指针（每帧重画）
    na = near_img().load()
    for (u, v) in disc_pts(dx_, dy_, 5.9):
        px(d, u, v, na[u, v][:3])
    ang = math.radians(250 + (0, 6, 2, -4, 0, 4, -2, -6)[f])
    for r in (1, 2, 3, 4):
        px(d, int(round(dx_ + r * math.cos(ang))), int(round(dy_ + r * math.sin(ang))), (40, 34, 36))
    px(d, dx_, dy_, (150, 40, 34))
    rx, ry = OBJ['radio']                                          # 调谐窗（obj_radio 的 A 格）
    k = (1.0, 0.75, 0.9, 0.6, 1.0, 0.82, 0.68, 0.92)[f]
    c = mix((120, 70, 30), (255, 200, 100), k)
    rect(d, rx + 1, ry - 2, rx + 2, ry - 1, c)
    px(d, rx + 1, ry - 2, lt(c, 0.3))
    return im


def steam_frame(t):
    """咖啡壶嘴的热气：三团往上飘、往右偏、越来越淡（2 s 一圈）。"""
    a = np.zeros((H, PW, 4), np.uint8)
    f = fno(t)
    sx, sy = POT[0] - 3, 127
    for i in range(3):
        u = ((f / N_ANIM) + i / 3.0) % 1.0
        x = sx + int(round(4 * u + math.sin(u * 6.3 + i)))
        y = sy - 1 - int(round(16 * u))
        al = int(190 * (1 - u))
        if al < 30:
            continue
        for (dx, dy) in ((0, 0), (1, 0), (0, -1), (1, -1)) if u > 0.35 else ((0, 0), (0, -1)):
            a[y + dy, x + dx] = (236, 232, 222, al)
    return Image.fromarray(a, 'RGBA')


def drip_frame(t):
    """阀组右端的法兰滴水：一滴慢慢鼓起来 → 掉下去 → 落进桶里 → 一圈水纹（8 帧，每帧都不一样）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    x, y = DRIP
    wc, hc = (150, 196, 220), (220, 240, 250)
    if f == 0:
        px(d, x, y, wc)
    elif f == 1:
        px(d, x, y, wc)
        px(d, x, y + 1, hc)
    elif f in (2, 3, 4):
        yy = y + (3, 8, 13)[f - 2]
        vl(d, x, yy, yy + 1, wc)
        px(d, x, yy, hc)
    elif f == 5:
        hl(d, x - 1, x + 1, 143, hc)                               # 落进桶里：一圈水纹
        px(d, x, 142, hc)
    elif f == 6:
        px(d, x - 2, 143, hc)
        px(d, x + 2, 143, hc)
    else:
        px(d, x - 3, 143, wc)
        px(d, x + 3, 143, wc)
        px(d, x, y, wc)
    return im


# ---------------------------------------------------------------- key leak：积水 + 喷水
@lru_cache(maxsize=1)
def water_img():
    """地上一层积水（半透明）：整片蓝灰的水膜、灯底下一道道微微晃的暖色倒影（软的竖条，越近越宽）、一道道水纹亮线、
    贴墙一道亮边。人走在上面照样看得清（水膜很淡）。"""
    a = np.zeros((H, PW, 4), np.uint8)
    a[FLOOR:, :] = (64, 100, 120, 84)
    for lx in LAMPS:                                               # 灯的倒影
        # 10-19 看图：原来每两行左右来回错 1 px、亮芯透明度 150，红色警报下像一串橙色的火苗 →
        # 晃得慢一点、断成一截截的横纹、整体淡一些（倒影只是地上有水的提示，不能抢可走带）
        for y in range(FLOOR + 2, H - 1):
            v = (y - FLOOR) / float(H - FLOOR)
            w = 1 + int(v * 3)
            off = int(round(1.0 * math.sin(y * 0.22 + lx * 0.1)))
            if (y * 7 + lx) % 5 == 0:
                continue
            for x in range(lx - w + off, lx + w + 1 + off):
                if 0 <= x < PW:
                    core = abs(x - lx - off) < max(1, w - 1)
                    a[y, x] = (240, 222, 170, 110) if core else (214, 196, 150, 64)
    for i in range(110):                                           # 水纹（横的短亮线，后面密前面疏）
        y = FLOOR + 3 + int(hash01(i, 71) ** 1.3 * (H - FLOOR - 5))
        x = int(hrange(0, PW - 14, i, 72))
        L = int(hrange(4, 13, i, 73))
        for k in range(L):
            if (k + i) % 5:
                a[y, x + k] = (180, 210, 224, 116)
    a[FLOOR, :] = (190, 214, 224, 150)                             # 贴墙的一道亮边
    return Image.fromarray(a, 'RGBA')


def spray_frame(t):
    """四处接缝漏水：接缝口往斜下方喷出三股水（近处两 px 粗、远处散成水珠），水雾一亮一暗；
    喷到头的水一滴滴往下落到甲板上（每帧往下 17 px），落地的地方一圈水花。8 帧，每帧都不一样，第 8 帧回到第 0 帧。"""
    a = np.zeros((H, PW, 4), np.uint8)
    f = fno(t)
    for j, (sx, sy) in enumerate(SPRAYS):
        side = -1 if j % 2 else 1
        for s in range(3):
            vx = side * (0.45 + 0.32 * s)
            L = 16 + 3 * s + (f + s + j) % 3
            for k in range(L):
                u = k / float(L)
                x = int(round(sx + vx * k))
                y = int(round(sy + 1 + 0.05 * k * k + 0.35 * k))
                if not (0 <= x < PW - 1 and 0 <= y < H):
                    continue
                if u < 0.4:
                    a[y, x] = (206, 232, 244, 230)
                    a[y, x + (1 if side > 0 else -1)] = (170, 210, 230, 160)
                elif u < 0.75 or (k + f + s) % 3 == 0:
                    a[y, x] = (226, 242, 250, 220)
        for k in range(7):                                         # 接缝口的水雾
            x = sx + int(hrange(-3, 4, j, k, f))
            y = sy + int(hrange(-2, 3, j, k, f, 2))
            a[y, x] = (232, 242, 248, 130)
        dx = sx + side * 12                                        # 往下落的水滴
        for k in range(4):
            y = sy + 20 + (f * 17 + k * 34) % 136
            if y < FLOOR - 1:
                a[y, dx] = (214, 236, 248, 220)
                a[y + 1, dx] = (170, 206, 228, 160)
        r = 1 + f % 4                                              # 落地的水花
        for xx in (dx - r - 1, dx - r, dx + r, dx + r + 1):
            a[FLOOR + 1, xx] = (226, 242, 250, 200)
        if f % 4 == 0:
            a[FLOOR, dx] = (240, 248, 252, 230)
            a[FLOOR - 1, dx - 1] = (226, 242, 250, 180)
            a[FLOOR - 1, dx + 1] = (226, 242, 250, 180)
    return Image.fromarray(a, 'RGBA')


# ---------------------------------------------------------------- key dark：停电
@lru_cache(maxsize=1)
def bulbs_off_img():
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for lx in LAMPS:
        rect(d, lx - 2, LAMP_Y - 2, lx + 2, LAMP_Y + 2, (96, 92, 84))
        vl(d, lx, LAMP_Y - 1, LAMP_Y + 1, (130, 124, 112))
        px(d, lx - 1, LAMP_Y - 1, (150, 146, 136))
    return im


@lru_cache(maxsize=1)
def emerg_img():
    """两盏应急灯：灯罩亮红橙、外面一圈光晕（半透明）、往下一小片光照在墙上。"""
    im = A._new(PW, H)
    for (ex, ey) in EMERG:
        A._glow(im, ex, ey + 2, 26, 18, (255, 120, 60), 70, rings=4)
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([(ex - 4, ey + 3), (ex + 4, ey + 3), (ex + 22, ey + 70), (ex - 22, ey + 70)],
                                    fill=(255, 130, 70, 34))
        im.alpha_composite(lay)
        d = ImageDraw.Draw(im)
        rect(d, ex - 3, ey - 1, ex + 3, ey + 2, (255, 150, 90))
        hl(d, ex - 2, ex + 2, ey, (255, 226, 180))
    return im


# ---------------------------------------------------------------- key alarm：旋转警报灯
def beacon_frame(t):
    """警报灯：灯罩里的光一圈圈转（转到正面时整个罩子亮白、侧面时一边亮），两道红光往左右扫，扫到正面时最短。"""
    a = np.zeros((H, PW, 4), np.uint8)
    im = Image.fromarray(a, 'RGBA')
    f = fno(t)
    th = math.tau * f / N_ANIM
    for (bx, by) in BEACONS:
        c = math.cos(th)
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        L = 8 + 64 * abs(c)
        side = 1 if c >= 0 else -1
        ex = bx + side * L
        sp = 6 + 14 * abs(c)
        ld.polygon([(bx, by + 2), (bx, by + 5), (ex, by + 3 + sp), (ex, by + 3 - sp * 0.6)], fill=(255, 50, 46, 46))
        ld.polygon([(bx, by + 3), (bx, by + 4), (ex, by + 3 + sp * 0.35), (ex, by + 3 - sp * 0.15)],
                   fill=(255, 96, 84, 72))                         # 亮芯
        if abs(math.sin(th)) > 0.7:                                # 转到正面：整个罩子的光晕
            ld.ellipse((bx - 11, by - 6, bx + 11, by + 12), fill=(255, 60, 60, 64))
        im.alpha_composite(lay)
        d = ImageDraw.Draw(im)
        for (u, v) in disc_pts(bx - 0.5, by + 3, 3.6):
            if v > by:
                hot = (u - bx) * side > 0
                px(d, u, v, (255, 200, 190) if (hot and abs(c) > 0.4) else (232, 60, 52))
    return im


# ============================================================ 组装
def _strip(name, fn, region, key=None):
    return dict(t='strip', name=name, box=P.auto_box(fn, N_ANIM, FPS_ANIM, region), n=N_ANIM, fps=FPS_ANIM, fn=fn,
                k=1.0, key=key)


@lru_cache(maxsize=1)
def specs():
    S = [dict(t='pano', name='near', img=near_img(), k=1.0)]
    for i, (cx, cy) in enumerate(PORTS):
        r = int(GLASS_R) + 1
        S.append(_strip('port%d' % i, port_frame, (cx - r, cy - r, cx + r + 1, cy + r + 1)))
    lx = LAMPS[FLICKER]
    S += [_strip('lamp', lamp_frame, (lx - 6, LAMP_Y - 4, lx + 7, LAMP_Y + 7)),
          _strip('blink0', blink_frame, (86, 86, 112, 140)),
          _strip('blink1', blink_frame, (OBJ['radio'][0] - 2, OBJ['radio'][1] - 4, OBJ['radio'][0] + 5, OBJ['radio'][1])),
          _strip('steam', steam_frame, (POT[0] - 8, 100, POT[0] + 10, 130)),
          _strip('drip', drip_frame, (DRIP[0] - 5, DRIP[1] - 1, DRIP[0] + 6, 145)),
          dict(t='pano', name='water', img=water_img(), k=1.0, key='leak')]
    for i, (sx, sy) in enumerate(SPRAYS):
        S.append(_strip('spray%d' % i, spray_frame, (sx - 36, sy - 6, sx + 37, FLOOR + 3), key='leak'))
    S += [dict(t='pano', name='bulbs_off', img=bulbs_off_img(), k=1.0, key='dark'),
          dict(t='tint', name='dark', color='#060814', alpha=0.62, key='dark'),
          dict(t='pano', name='emerg', img=emerg_img(), k=1.0, key='dark'),
          dict(t='tint', name='alarm_t', color='#ff1e28', alpha=0.2, key='alarm')]
    for i, (bx, by) in enumerate(BEACONS):
        S.append(_strip('beacon%d' % i, beacon_frame, (bx - 76, 0, bx + 77, by + 44), key='alarm'))
    for L in S:
        if L.get('key') is None:
            L.pop('key', None)
    return S


def anchors():
    an = dict(ANCHORS)
    for name in METAL:
        an['obj_' + name] = list(OBJ[name])
    an['objects'] = [list(OBJ[name]) for name in METAL]
    an.update(ports=[list(p) for p in PORTS], lamps=[[lx, LAMP_Y] for lx in LAMPS], logbook=[292, 126])
    return an


# ============================================================ 导出
def export(ex, BJ):
    S = specs()
    layers, fg = P.export_layers(ex, BJ, S)
    st = ex.stage(PW, GROUND, WALK, layers, fg, anchors())
    if ex.check_on:
        _checks(ex, BJ, st, S)
    return st


def _checks(ex, BJ, st, S):
    near = near_img()
    m0, s0 = P.walk_stats(near, WALK)
    cfg = dict(
        name='潜艇', pw=PW, walk=WALK,
        states=[{}, {'alarm': True}, {'leak': True}, {'dark': True}, {'alarm': True, 'leak': True},
                {'alarm': True, 'leak': True, 'dark': True}],
        opaque=[('近景整张不透明（舱内没有天）', near, (0, 0, PW, H))],
        binary=[('近景只有 0 / 255 两种透明度', near), ('停电的灯泡层只有 0 / 255', bulbs_off_img())],
        stand=['arrive', 'helm', 'periscope', 'chart', 'galley', 'bunks', 'gear', 'hatch'],
        inside=['obj_' + n for n in METAL] + ['objects', 'ports', 'lamps', 'logbook'],
        notes=['可走带亮度（y 150–176）：均值 %.0f 标准差 %.1f' % (m0, s0)],
    )
    P.std_checks(ex, BJ, st, S, cfg)
    # 12 件金属：y 在 110–150、整个 10×10 框在可走带后沿上面；按 x 排好以后相邻间距 ≥ 30；框里确实画了东西
    bad = sum(1 for n in METAL if not (110 <= OBJ[n][1] <= 150 and OBJ[n][1] + 4 < WALK[0]))
    ex.checked('12 件金属的 y 都在 110–150、10×10 框不进可走带（不满足的件数）', bad)
    xs = sorted(OBJ[n][0] for n in METAL)
    gaps = [b - a for a, b in zip(xs, xs[1:])]
    ex.checked('12 件金属按 x 排开，相邻间距 ≥ 30（最小 %d）' % min(gaps), sum(1 for g in gaps if g < 30))
    a1 = np.array(near)[..., :3].astype(np.int16)
    a0 = np.array(near_bare())[..., :3].astype(np.int16)
    few = []
    for n in METAL:
        x, y = OBJ[n]
        diff = (np.abs(a1[y - 5:y + 5, x - 5:x + 5] - a0[y - 5:y + 5, x - 5:x + 5]).max(-1) > 0).sum()
        if diff < 24:
            few.append((n, int(diff)))
    ex.checked('12 件金属在锚点的 10×10 框里都画了（像素 < 24 的：%s）' % (few or '无'), len(few))
    ex.checked('anchors.objects 和 obj_* 一致、按剧情 METAL 顺序（12 个）',
               int(st['anchors']['objects'] != [st['anchors']['obj_' + n] for n in METAL]) + abs(len(METAL) - 12))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch7', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        P.direct(specs(), camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'submarine_solo_%d.png' % camX))
    print('ok')
