# -*- coding: utf-8 -*-
r"""aswan_town —— 第8章「阿斯旺」：尼罗河边的小城，努比亚风格的彩色土坯房（第 17 战 克努姆 + 托特，三个预言）。
2026-10-19 egypt-town 组按体验版精度重画（改前是 later_stages.town(5)：一排平涂方块房）。零件在 egypt_town_parts.py。

地图 960 宽、ground 160、可走带 y 148–176（压实的沙土路 / 清真寺前的石板广场，对比压得很低）；侧视平视，
太阳在左上（墙左沿亮、右沿暗，挑出来的东西往右下落影）。墙脚 = 地面后沿 y 146，房子 / 摊子都画在 y ≤ 145；
可走带里只有平的东西，外加剧情要坐 / 要站上去的三样矮东西（橘子堆、茶桌 + 两把椅子、喷泉池沿，都 ≤ 9 px 高，
自检的“可走带平整”把这三个框排除）。
从左到右（世界坐标）：
  x 0–34      街口：浅蓝的两层转角房（挑出的木格窗、三角垛、白色锯齿带、拱顶小门、嵌在墙上的瓷盘、蓝色路牌）
  x 34–70     矮院墙（三角垛 + 蓝色折线带）+ 路边给人喝水的两只陶罐（木架上，sabil）+ 墙后一棵海枣树（树冠 strip 摆）；
              墙头上面看得见远处的尼罗河和帆船（anchors.arrive）
  x 70–206    黄色努比亚房子：屋顶一段筒拱 + 一个穹顶、镂空三角孔的女儿墙、蓝白锯齿带、两扇木格小高窗、
              右边蓝门套的拱顶绿门 + 门楣上挂的鳄鱼标本；门前的橘子摊：两根木杆撑橙白条纹布篷（波浪边 strip 飘）、
              靠墙三摞椰枣枝筐、木台上堆成山的橘子（插一块价牌）、一台白色弹簧秤、台下麻袋和空筐；
              台前可走带后沿地上铺一块麻布，又堆一小堆橘子（堆顶 = anchors.orange，剧情把“特别亮的那颗”放在这；
              老板 npc 站 anchors.orange_vendor）
  x 206–250   青绿的两层窄房：阶梯垛、白菱形带、关着的百叶窗 + 窗台花盆、墙上画的努比亚壁画（白帆船 + 黄太阳）、
              红门 + 白门套
  x 250–372   茶馆（白墙青绿边）：二楼两扇青绿百叶窗 + 中间一扇木格窗、绿底白字的招牌（左边一只茶杯）；
              一楼两个尖拱敞口：左边里面是长凳、靠墙一排水烟壶、乌姆·库勒苏姆的小相框，右边是柜台（铜茶炊冒热气 strip、
              架子上一排排玻璃茶杯、茶叶罐、收音机、挂钟）；拱下挂铜灯笼；门外长凳 + 一张小圆桌 + 水烟壶 + 抽水烟的老人
              （背景人，压灰，烟 strip）；可走带里一张小圆铁桌（anchors.tea_table，桌面 y 150–152 = anchors.tea）+
              两把木椅（anchors.tea_seats：乔瑟夫朝右坐左边那把、阿布德尔朝左坐右边那把）；老板 npc 站 anchors.teahouse_owner
  x 372–480   布店（粉墙）：二楼铁栏杆小阳台 + 花盆 + 两扇百叶窗、蓝底白字招牌；一楼敞开的店面（卷帘门收在上面）、
              架子上一卷卷彩布、柜台上叠好的布；蓝白条纹遮阳棚（波浪边 strip）下一根横杆挂着六块布（strip 被风吹得摆）；
              门边靠着几卷布（anchors.cloth）
  x 480–566   马车停靠点：土坯院墙（镂空女儿墙）+ 墙后一棵大无花果树（树冠斑驳的光、地上淡淡的树荫）、
              一块“马车站”蓝牌（白色马车图）、墙脚一堆三叶草料 + 草料袋
  x 566–640   蓝色努比亚房子（筒拱屋顶、三角孔女儿墙、门楣鳄鱼、瓷盘、画在墙上的海枣树）；门前石头水槽（水面 strip 闪光）、
              墙上伸出来的水龙头、一只黑胶皮桶、拴马桩（铁环）；可走带 x 500–640 只留路面 + 马蹄印 + 车辙（马车和马是剧情道具，
              anchors.carriage）
  x 640–686   赭黄三层楼（挑出的木格窗、百叶窗、拉下的绿卷帘门 + 小招牌），门口一根木电线杆
  x 686–714   窄巷（anchors.alley）：两边的墙往里收、巷底一扇小蓝门 + 两级台阶、巷子里很暗，头顶两根晾衣绳（strip）；
              巷口右边一摞木箱（anchors.crate，伊奇钻到后面）；波因哥站 anchors.boingo
  x 714–752   白色两层房：墙上画的朝觐画（黑色天房 + 蓝飞机 + 骆驼）、蓝框窗；屋顶旗杆上的埃及国旗（strip）
  x 752–900   清真寺：奶白色的墙 + 阶梯垛、左边两孔尖拱回廊、正中墙上一块大理石碑、后面的大穹顶（鼓座小窗 + 新月）、
              右边带门楼的尖拱正门（半开的绿门、上面一道绿底金字）、门口几双拖鞋、右端宣礼塔（两层阳台 + 喇叭 + 新月）、
              回廊前一棵海枣树（strip）；广场铺石板；正中可走带后沿一个八角喷泉池（池沿顶 y 150、前壁 151–157，
              假承太郎站在池沿上：anchors.fountain，z 6）、池中一根石柱托着石碗，水从顶上冒、从碗沿往下淌（strip）；
              池边的鸽子在啄食（strip，anchors.pigeons）
  x 900–960   去车站的路：一棵海枣树、矮墙 + 铁栏杆、蓝色路牌（白色火车 + 箭头）（anchors.exit）
头顶：x 248 / 484 / 638 / 904 四根木电线杆之间拉着电线（y 20–60，在对白框后面也不要紧）。
远景：尼罗河西岸的金色沙山（山顶风之圆顶、阿迦汗陵墓、山腰一排贵族墓的洞口）、河面、河里的黑色花岗岩、对岸的海枣；
中景：城里后排的房顶（穹顶、筒拱、水箱、天线、晾的衣服）、远处一座宣礼塔、右边火车站（钟楼）。

图层（从后往前）：
  sky       static           320×180 上午的天 + 左上的太阳
  clouds    wrap   k 0.08 vx 1.2   干热天的小积云 + 云丝（640 循环）
  far       pano   k 0.25          远景 480 宽：西岸沙山、河面、花岗岩、对岸海枣（罩雾）
  sparkle   strip  k 0.25          河面的闪光（8 帧 @4 fps）
  felucca   clouds k 0.25          三条三角帆船在河上慢慢漂（span 520）
  mid       pano   k 0.55          中景 672 宽：后排房顶 + 宣礼塔 + 火车站
  birds     clouds k 0.15          两只在高处盘旋的鸢
  near      pano   k 1             整条街（960 宽）
  palm_0…2  strip  k 1             三棵海枣树的树冠（8 帧 @4 fps）
  valance_0/1 strip k 1            橘子摊、布店遮阳棚的波浪边
  cloths    strip  k 1             布店门口挂的六块布
  steam_0/1 strip  k 1             茶炊的热气、门外老人的水烟
  trough    strip  k 1             水槽水面的闪光
  laundry   strip  k 1             窄巷里的晾衣绳
  flag      strip  k 1             白房子屋顶的国旗
  fountain  strip  k 1             喷泉的水
  pigeons   strip  k 1             喷泉边啄食的鸽子
锚点：arrive [40,164]、orange [150,152]、orange_vendor [168,160]、tea_table [300,158]、tea [300,152]、teahouse_owner [330,156]、
      cloth [420,150]、carriage [560,162]、boingo [690,156]、alley [700,150]、crate [716,158]、fountain [810,156]、exit [940,162]
      （素材总表 §一.3）；另导出 tea_seats [[286,158],[314,158]]（两把椅子的坐点 = 坐姿的脚点）、tea_top 150（桌面最上一行）、
      orange_heap / tea_box / fountain_box（三样矮东西的框）、fountain_rim 150（池沿顶）、pigeons（鸽子的位置）、
      trough [584,138]、hitch [606,128]、crates_box、alley_box、mosque_door [854,145]、lane_back 146。
key：无（素材总表没有要求）。
单独运行：python -B tools\bg_new\aswan_town.py → tools\bg_new\_preview\ch8\after\aswan_town_solo.png
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
mul_box, mul_mask, poly_mask, cast_shadow, mottle, haze, opaque = (P.mul_box, P.mul_mask, P.poly_mask, P.cast_shadow,
                                                                  P.mottle, P.haze, P.opaque)
SHADOW_MUL, SOFT_MUL = P.SHADOW_MUL, P.SOFT_MUL
INK = P.INK
WOOD_HI, WOOD, WOOD_D, WOOD_K = P.WOOD_HI, P.WOOD, P.WOOD_D, P.WOOD_K
IRON, IRON_HI, BRASS = P.IRON, P.IRON_HI, P.BRASS
DARK_IN = P.DARK_IN

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 960
GROUND = 160
WALK = (148, 176)
LANE = 146                     # 墙脚 = 地面后沿（房子画到 y 145）
N, FPS = P.N_ANIM, P.FPS_ANIM
CLOUD_P, CLOUD_K, CLOUD_VX = 640, 0.08, 1.2
FAR_K, MID_K, BIRD_K = 0.25, 0.55, 0.15
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 480
MIDW = W + int(math.ceil((PW - W) * MID_K))      # 672
RIVER = (97, 108)              # 远景层里河面的 y 范围
BOAT_SPAN = 520

H0 = (0, 34)
GATE = (34, 70)
H1 = (70, 206)
STALL = (98, 186)
HEAP = (137, 164)              # 可走带后沿地上那一小堆橘子（麻布）
H2 = (206, 250)
TEA = (250, 372)
CLOTH = (372, 480)
STOP = (480, 566)              # 院墙 + 大树（马车停靠点的后面）
H5 = (566, 640)
H6 = (640, 686)
ALLEY = (686, 714)
H7 = (714, 752)
MOSQUE = (752, 900)
FOUNT = (786, 834)             # 喷泉池（可走带后沿）
PLAZA = (744, 906)             # 石板广场
ROAD = (900, 960)
POLES = (248, 484, 638, 904)
TABLE_X, TABLE_TOP, TABLE_BASE = 300, 150, 158
SEATS = ((286, 1), (314, -1))  # 两把椅子：(坐姿脚点 x, 人朝向)
RIM_TOP = 150                  # 喷泉池沿顶（假承太郎站在上面：fountain.y 156 − z 6）

ANCHORS = dict(arrive=[40, 164], orange=[150, 152], orange_vendor=[168, 160], tea_table=[300, 158], tea=[300, 152],
               teahouse_owner=[330, 156], cloth=[420, 150], carriage=[560, 162], boingo=[690, 156], alley=[700, 150],
               crate=[716, 158], fountain=[810, 156], exit=[940, 162])
STAND = ('arrive', 'orange_vendor', 'tea_table', 'teahouse_owner', 'cloth', 'carriage', 'boingo', 'alley', 'crate',
         'fountain', 'exit')
REQUIRED = tuple(ANCHORS)

# ============================================================ 调色
SKY_STOPS = [(56, 116, 196), (80, 142, 212), (118, 172, 224), (172, 204, 226), (234, 226, 200)]
HAZE = (228, 216, 192)
GRD = (214, 190, 150)          # 压实的沙土路
GRD_S = (204, 179, 139)
GRD_HI = (223, 201, 163)
PAVE = (208, 196, 172)         # 广场石板
PAVE_S = (196, 184, 160)
PAVE_HI = (217, 207, 186)
NUB_BLUE, NUB_SKY, NUB_YELLOW, NUB_PINK, NUB_TURQ = P.NUB_BLUE, P.NUB_SKY, P.NUB_YELLOW, P.NUB_PINK, P.NUB_TURQ
NUB_OCHRE, LIME, MUD = P.NUB_OCHRE, P.LIME, P.MUD
CREAM = (238, 228, 206)        # 清真寺的奶白
STONE = (214, 192, 152)        # 门楼的石头
TEAL = (52, 138, 128)          # 茶馆的青绿边
O_HI, O_MD, O_DK, O_KK = P.ORANGE_C
LEAF_D, LEAF, LEAF_M, LEAF_HI = P.LEAF_D, P.LEAF, P.LEAF_M, P.LEAF_HI
WATER = ((236, 248, 250), (190, 224, 236), (140, 190, 210), (96, 150, 180))
PIGEON_C = (124, 128, 142)


def fidx(t):
    return P.frame_of(t, N, FPS)


# ============================================================ 天 / 远景 / 中景
def sky_img():
    return P.sun_sky(SKY_STOPS, (46, 22), sun_r=6)


def clouds_img():
    return P.wisps_img(period=CLOUD_P, hgt=58, seed=31)


def far_ridge(x):
    """西岸沙山的山脊线 y（越小越高）：几道正弦叠起来，x 118 一座尖山（顶上风之圆顶）、x 300 一座圆山（阿迦汗陵墓）。"""
    return (80 + 6 * math.sin(x * 0.021 + 0.6) + 3.5 * math.sin(x * 0.061 + 2.1) + 1.6 * math.sin(x * 0.17 + 0.4)
            - 15 * math.exp(-((x - 118) / 24.0) ** 2) - 10 * math.exp(-((x - 300) / 38.0) ** 2))


@lru_cache(maxsize=1)
def far_img():
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    lit, mid, sh, deep = (246, 220, 170), (232, 200, 146), (210, 172, 122), (184, 146, 104)
    for x in range(FARW):
        top = int(round(far_ridge(x)))
        slope = far_ridge(x + 1.5) - far_ridge(x - 1.5)
        for y in range(top, RIVER[0] - 1):
            u = (y - top) / max(1.0, RIVER[0] - 1 - top)
            if slope < -0.5:
                c = lit                                            # 朝左的坡（向阳）
            elif slope < 0.35:
                c = mid
            elif slope < 1.1:
                c = sh
            else:
                c = deep
            if u > 0.55:                                           # 山脚的沙往下淌，颜色更平
                c = mix(c, mid, 0.5)
            if (y + int(x * 0.35)) % 9 == 0 and hash01(x // 5, y, 711) < 0.6:
                c = dk(c, 0.95)                                    # 风刻出来的层理
            px(d, x, y, c)
        px(d, x, top, lt(lit, 0.3) if slope < 0 else mid)
    # 山腰一排贵族墓（风之圆顶那座山的腰上，一个个黑洞口 + 下面一道踩出来的小路）
    for i in range(9):
        x = 84 + i * 8 + int(hrange(-1, 2, i, 712))
        y = int(far_ridge(x)) + 9 + (i % 2)
        rect(d, x, y, x + 1, y + 2, (120, 92, 70))
        px(d, x + 2, y, (226, 196, 150))
    for x in range(80, 160):
        y = int(far_ridge(x)) + 13 + int(1.5 * math.sin(x * 0.2))
        if hash01(x, 713) < 0.7:
            px(d, x, y, (238, 212, 168))
    # 风之圆顶（尖山顶上一个小穹顶）
    tx, ty = 118, int(far_ridge(118))
    rect(d, tx - 3, ty - 4, tx + 3, ty - 1, (236, 222, 196))
    d.pieslice((tx - 3, ty - 8, tx + 3, ty - 2), 180, 360, fill=C((240, 228, 204)))
    px(d, tx + 3, ty - 3, (196, 178, 150))
    # 阿迦汗陵墓：圆山顶上一座粉色砂岩的方殿 + 中间一个穹顶 + 两边的小塔楼
    mx, my = 300, int(far_ridge(300))
    rect(d, mx - 9, my - 7, mx + 9, my - 1, (222, 176, 150))
    hl(d, mx - 9, mx + 9, my - 7, (240, 206, 182))
    for k in (-6, -2, 2, 6):
        rect(d, mx + k, my - 5, mx + k, my - 3, (150, 108, 96))
    d.pieslice((mx - 5, my - 15, mx + 5, my - 5), 180, 360, fill=C((230, 190, 164)))
    px(d, mx - 3, my - 12, (246, 214, 194))
    for k in (-9, 9):
        rect(d, mx + k, my - 10, mx + k + (1 if k < 0 else -1), my - 7, (214, 168, 142))
    vl(d, mx + 9, my - 7, my - 1, (180, 136, 116))
    # 岸边：对岸一道深绿（矮树丛 + 芦苇）+ 几棵海枣
    for x in range(FARW):
        yb = RIVER[0] - 1 + int(round(math.sin(x * 0.09) * 0.6))
        for y in range(yb - 2, RIVER[0] + 1):
            c = (120, 140, 90) if (x + y) % 3 else (100, 124, 80)
            px(d, x, y, c)
    for i, x in enumerate((14, 36, 52, 170, 186, 214, 352, 380, 396, 430, 452)):
        h = int(hrange(10, 17, i, 714))
        yb = RIVER[0] - 2
        vl(d, x, yb - h, yb, (120, 100, 76))
        for k in range(-4, 5):
            yy = yb - h + abs(k) // 2 + (1 if abs(k) > 3 else 0)
            px(d, x + k, yy, (90, 120, 76))
            if abs(k) > 1:
                px(d, x + k, yy + 1, (76, 104, 66))
    # 河面（远处浅、近处深；几道横的亮纹）
    for y in range(RIVER[0] + 1, RIVER[1] + 1):
        u = (y - RIVER[0]) / float(RIVER[1] - RIVER[0])
        base = mix((150, 196, 212), (96, 154, 184), u)
        for x in range(FARW):
            c = base
            if (x * 3 + y * 17) % 23 == 0:
                c = lt(base, 0.25)
            elif (x + y * 7) % 31 == 0:
                c = dk(base, 0.92)
            px(d, x, y, c)
    # 河里的黑色花岗岩（象岛那一片：圆滚滚的大石头，顶上亮、水边一道白）
    for i in range(7):
        cx = int(hrange(196, 268, i, 715))
        cy = RIVER[1] - int(hrange(1, 5, i, 716))
        rx, ry = int(hrange(3, 7, i, 717)), int(hrange(2, 4, i, 718))
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=C((96, 84, 82)))
        hl(d, cx - rx + 1, cx, cy - ry, (150, 132, 122))
        px(d, cx - rx + 1, cy - ry + 1, (130, 114, 106))
        hl(d, cx - rx, cx + rx, cy + ry, (214, 232, 236))
    # 近岸（象岛 / 东岸，绝大部分被中景挡住）：海枣林 + 绿地，铺到底
    for y in range(RIVER[1] + 1, H):
        u = min(1.0, (y - RIVER[1]) / 20.0)
        hl(d, 0, FARW - 1, y, mix((128, 150, 96), (150, 156, 104), u))
    for i in range(40):
        x = int(hrange(0, FARW, i, 719))
        y = RIVER[1] + 1 + int(hrange(0, 6, i, 720))
        for k in range(-3, 4):
            px(d, x + k, y + abs(k) // 2, (90, 120, 72))
    # 空气透视：越远（越往上）罩得越多
    amt = np.zeros((H, 1), np.float32)
    for y in range(H):
        amt[y, 0] = 0.42 if y < RIVER[0] - 3 else (0.26 if y <= RIVER[1] else 0.3)
    im = haze(im, amt, HAZE)
    return opaque(im)


def sparkle_frame_raw(f):
    """河面的闪光（远景层坐标）：一颗颗亮点按帧亮 / 灭，每颗的相位不同。"""
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    for i in range(46):
        x = int(hrange(0, FARW - 3, i, 731))
        y = int(hrange(RIVER[0] + 2, RIVER[1] - 1, i, 732))
        ph = int(hash01(i, 733) * N)
        k = (f + ph) % N
        if k < 3:
            c = (246, 252, 250) if k == 1 else (206, 230, 236)
            px(d, x, y, c)
            if k == 1:
                px(d, x + 1, y, (214, 236, 240))
    return im


@lru_cache(maxsize=N)
def _sparkle(f):
    return sparkle_frame_raw(f)


def sparkle_frame(t):
    return _sparkle(fidx(t))


SPARKLE_BOX = (0, RIVER[0] + 1, FARW, RIVER[1])


def felucca_imgs():
    """三条帆船（远景里的小船：船身 14–18 px）。"""
    return [P.felucca_img(16, 15, seed=0), P.felucca_img(14, 13, seed=1, face=-1), P.felucca_img(18, 16, seed=2)]


BOATS = [(40.0, RIVER[0] + 8 - 21, 2.6), (230.0, RIVER[0] + 9 - 19, -1.8), (380.0, RIVER[0] + 10 - 22, 2.0)]


def mid_house(im, x0, x1, top, col, seed, roof=None):
    """中景的一栋房（罩雾前先画清楚）：抹灰 + 小窗洞 + 门洞 + 屋顶的东西（dome / vault / tank / antenna / laundry）。"""
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = P.wall_pal(col)
    rect(d, x0, top, x1 - 1, H - 1, md)
    vl(d, x0, top, H - 1, hi)
    vl(d, x1 - 1, top, H - 1, sh)
    hl(d, x0, x1 - 1, top, hi)
    for i in range(max(1, (x1 - x0) // 9)):
        wx = x0 + 3 + i * 9
        if wx + 3 > x1 - 2:
            break
        for wy in range(top + 5, 130, 13):
            if hash01(seed, i, wy, 1) < 0.72:
                rect(d, wx, wy, wx + 2, wy + 3, dk(md, 0.55))
                hl(d, wx - 1, wx + 3, wy + 4, hi)
    if roof == 'dome':
        P.dome(im, (x0 + x1) // 2, top, max(5, (x1 - x0) // 3), col, drum=1)
    elif roof == 'vault':
        P.vault(im, x0 + 2, x1 - 3, top, col)
    elif roof == 'tank':
        rect(d, x0 + 3, top - 6, x0 + 10, top - 1, (178, 178, 180))
        hl(d, x0 + 3, x0 + 10, top - 6, (214, 214, 214))
        vl(d, x0 + 4, top - 1, top, (110, 110, 112))
        vl(d, x0 + 9, top - 1, top, (110, 110, 112))
    elif roof == 'antenna':
        ax = x1 - 6
        vl(d, ax, top - 12, top, (96, 96, 100))
        for k, w in ((0, 4), (3, 3), (6, 2)):
            hl(d, ax - w, ax + w, top - 12 + k, (96, 96, 100))
    elif roof == 'laundry':
        V.wire(d, x0 + 1, top - 6, x1 - 2, top - 6, 2, (90, 86, 84))
        vl(d, x0 + 1, top - 6, top, (110, 100, 90))
        vl(d, x1 - 2, top - 6, top, (110, 100, 90))
        for k in range(4):
            cx = x0 + 4 + k * ((x1 - x0 - 8) // 4)
            c = P.CLOTH[int(hash01(seed, k, 3) * len(P.CLOTH))]
            rect(d, cx, top - 5, cx + 2, top - 2, c)
    elif roof == 'crenel':
        P.crenels(im, x0, x1 - 1, top, col, 'tri', size=2, gap=1)


@lru_cache(maxsize=1)
def mid_img():
    """中景（672 宽，k 0.55）：后排的房顶。x 0–96 一片低的海枣林（街口的墙头上看得见河），x 600 起火车站。"""
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    for x in range(MIDW):                                          # 一直铺到底的地 / 院墙（被近景挡住的部分）
        yb = 122 + int(round(2 * math.sin(x * 0.05)))
        for y in range(yb, H):
            px(d, x, y, (200, 176, 136) if (x + y) % 5 else (192, 168, 130))
    # 海枣林（低，x 0–100）：树干 + 树冠
    for i, (x, h) in enumerate(((10, 22), (26, 18), (44, 26), (62, 20), (80, 24), (98, 16))):
        yb = 124
        vl(d, x, yb - h, yb, (150, 116, 84))
        vl(d, x + 1, yb - h, yb, (120, 92, 66))
        for k in range(9):
            ang = math.radians(-10 + k * 25)
            for j in range(1, 8):
                xx = x + int(round(math.cos(ang) * j))
                yy = yb - h - int(round(math.sin(ang) * j * 0.6)) + j * j // 12
                px(d, xx, yy, (70, 120, 64) if j % 2 else (96, 146, 76))
    houses = [(104, 136, 100, NUB_PINK, 'dome'), (136, 160, 108, LIME, 'tank'), (160, 196, 94, NUB_SKY, 'crenel'),
              (196, 222, 104, NUB_YELLOW, 'vault'), (222, 256, 90, LIME, 'antenna'), (256, 280, 106, NUB_TURQ, 'dome'),
              (280, 318, 98, (222, 196, 160), 'laundry'), (318, 340, 110, NUB_PINK, None), (340, 372, 96, LIME, 'tank'),
              (372, 404, 102, NUB_OCHRE, 'vault'), (404, 430, 92, NUB_BLUE, 'antenna'), (452, 486, 100, LIME, 'dome'),
              (486, 512, 108, NUB_YELLOW, 'laundry'), (512, 548, 96, (222, 196, 160), 'crenel'),
              (548, 576, 104, NUB_PINK, 'tank'), (576, 600, 110, LIME, None)]
    for i, (x0, x1, top, col, roof) in enumerate(houses):
        mid_house(im, x0, x1, top, col, 760 + i, roof)
    d = ImageDraw.Draw(im)
    # 远处一座宣礼塔（x 440）
    P.minaret(im, 441, 124, 44, 8, (236, 228, 210), speakers=False)
    # 火车站（x 600–672）：两层的殖民时期站房 + 钟楼 + 拱窗
    x0, x1 = 600, MIDW
    hi, md, sh, kk = P.wall_pal((226, 196, 150))
    rect(d, x0, 92, x1 - 1, H - 1, md)
    hl(d, x0, x1 - 1, 92, hi)
    hl(d, x0, x1 - 1, 93, lt(md, 0.1))
    for wx in range(x0 + 4, x1 - 4, 9):
        rect(d, wx, 100, wx + 4, 108, dk(md, 0.55))
        d.pieslice((wx, 97, wx + 4, 103), 180, 360, fill=C(dk(md, 0.55)))
        rect(d, wx, 114, wx + 4, 121, dk(md, 0.6))
    hl(d, x0, x1 - 1, 110, sh)
    tx = 628                                                       # 钟楼
    rect(d, tx, 70, tx + 12, 92, md)
    vl(d, tx, 70, 92, hi)
    vl(d, tx + 12, 70, 92, sh)
    d.ellipse((tx + 3, 74, tx + 9, 80), fill=C((244, 240, 228)))
    px(d, tx + 6, 77, (40, 40, 40))
    px(d, tx + 6, 76, (40, 40, 40))
    px(d, tx + 7, 77, (40, 40, 40))
    for k in range(4):
        hl(d, tx - 1 + k, tx + 13 - k, 69 - k, sh if k % 2 else md)
    vl(d, tx + 6, 60, 65, (90, 90, 96))
    # 后排的海枣（插在房子中间）
    for i, (x, top) in enumerate(((132, 86), (226, 80), (350, 84), (436, 92), (520, 82), (594, 88))):
        vl(d, x, top, 124, (140, 110, 80))
        vl(d, x + 1, top, 124, (116, 88, 64))
        for k in range(11):
            ang = math.radians(-20 + k * 22)
            L = 9 if 2 < k < 9 else 7
            for j in range(1, L):
                xx = x + int(round(math.cos(ang) * j))
                yy = top - int(round(math.sin(ang) * j * 0.55)) + j * j // 10
                px(d, xx, yy, (62, 112, 60) if j % 2 else (90, 140, 72))
    im = haze(im, 0.3, HAZE)
    im = A._grade(im, sat=0.86, val=1.0)
    return opaque(im)


def birds_img():
    return V.kite_bird_img()


BIRDS = [(14, 3.0, BIRD_K, 60), (24, -2.2, BIRD_K, 300)]


# ============================================================ 近景：地面
def draw_ground(im):
    d = ImageDraw.Draw(im)
    rect(d, 0, LANE, PW - 1, H - 1, GRD)
    mottle(im, (0, LANE, PW - 1, H - 1), GRD, GRD_S, GRD_HI, 811, cell=7, lo=0.24, hi=0.78)
    a = np.array(im)
    bay = A._bayer(PW, H)
    # 广场石板：一排排往前变高的长方石（透视），石缝比石面深一点，个别石块偏暖 / 偏灰；两头按 Bayer 抖开接沙土路
    rows = [LANE, 149, 153, 158, 164, 171, H]
    x0, x1 = PLAZA
    for r in range(len(rows) - 1):
        ya, yb = rows[r], rows[r + 1]
        sw = 10 + (yb - ya) * 3
        off = int(hrange(0, sw, r, 812))
        for y in range(ya, yb):
            for x in range(x0 - 12, min(PW, x1 + 12)):
                if x < x0 + 4 and bay[y, x] >= (x - (x0 - 12)) / 16.0:
                    continue
                if x > x1 - 4 and bay[y, x] >= ((x1 + 12) - x) / 16.0:
                    continue
                kx = (x + off) // sw
                tone = hash01(r, kx, 813)
                c = PAVE if tone < 0.6 else (PAVE_HI if tone < 0.8 else mix(PAVE, (214, 190, 160), 0.6))
                if (x + off) % sw == 0 or y == ya:
                    c = PAVE_S
                elif y == ya + 1 and (x + off) % sw == 1:
                    c = lt(c, 0.06)
                elif hash01(x, y, 814) < 0.05:
                    c = dk(c, 0.97)
                a[y, x, :3] = c
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    # 车辙：两道淡淡的轮子印（马车从左一直走到广场边）
    for ry in (157, 168):
        for x in range(0, x0 - 6):
            if hash01(x // 11, ry, 815) < 0.75:
                yy = ry + int(round(math.sin(x * 0.017 + ry) * 0.8))
                c = im.getpixel((x, yy))[:3]
                px(d, x, yy, dk(c, 0.955))
    # 脚印（成对的小暗点）
    for i in range(110):
        x = int(hrange(8, PW - 8, i, 816))
        y = int(hrange(149, 175, i, 817))
        c = im.getpixel((x, y))[:3]
        px(d, x, y, dk(c, 0.95))
        px(d, x + 3, y + 1, dk(c, 0.95))
    # 马蹄印（停靠点那一段：一个个小 U）
    for i in range(26):
        x = int(hrange(494, 640, i, 818))
        y = int(hrange(150, 172, i, 819))
        c = im.getpixel((x, y))[:3]
        px(d, x, y, dk(c, 0.93))
        px(d, x + 2, y, dk(c, 0.93))
        px(d, x + 1, y + 1, dk(c, 0.95))
    # 橘子皮、碎纸、稻草屑（都压得很淡）
    for i in range(24):
        x = int(hrange(110, 260, i, 820))
        y = int(hrange(150, 174, i, 821))
        px(d, x, y, mix(GRD, O_MD, 0.42))
        if i % 3 == 0:
            px(d, x + 1, y, mix(GRD, O_DK, 0.38))
    for i in range(40):
        x = int(hrange(480, 640, i, 822))
        y = int(hrange(148, 175, i, 823))
        px(d, x, y, mix(GRD, (226, 206, 120), 0.45))
    # 水槽前湿了一片（深一点、Bayer 抖开边）
    a = np.array(im)
    for y in range(LANE, 152):
        for x in range(562, 610):
            u = 1.0 - max(abs(x - 586) / 26.0, (y - LANE) / 6.0)
            if u > 0 and bay[y, x] < u * 1.3:
                a[y, x, :3] = (a[y, x, :3].astype(np.float32) * np.array((0.9, 0.9, 0.92))).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))


def ground_shade(im):
    """墙脚压一道暗（房子挡住了一点天光）+ 广场 / 路面上，立着的东西往右下落的淡影。"""
    a = np.array(im)
    for x in range(PW):
        if a[LANE - 1, x, 3] > 0:
            a[LANE, x, :3] = (a[LANE, x, :3] * np.array((0.86, 0.86, 0.9))).astype(np.uint8)
            a[LANE + 1, x, :3] = (a[LANE + 1, x, :3] * np.array((0.94, 0.94, 0.96))).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))


# ============================================================ 近景：小工具
# 路牌上的白色图标（X = 白）：马头（像象棋的马，比整辆马车在这么小的牌子上好认）、
# 蒸汽火车（司机室 + 锅炉 + 烟囱 + 轮子）
PICTO_CARRIAGE = '''
....XX...
...XXXX..
..XXXXXX.
.XXX.XXXX
XXXX..XXX
.XX..XXXX
....XXXXX
...XXXXXX
..XXXXXXX
'''
PICTO_TRAIN = '''
.......XX...
XXXX...XX...
X..X.XXXXXX.
XXXXXXXXXXXX
XXXXXXXXXXXX
.X.X...X.X..
'''


picto, leafy, bird_cage, bicycle = P.picto, P.leafy, P.bird_cage, P.bicycle
soft_shadow, arch_mask, put_inside = P.soft_shadow, P.arch_mask, P.put_inside


def oranges(d, pts, seed):
    """一个个橘子（3×3 的小球：左上亮、右下暗）；pts 后画的盖在前面。个别偏黄 / 偏红、个别带一片叶子。"""
    for i, (x, y) in enumerate(pts):
        tone = hash01(seed, i, 1)
        hi, md, dd, kk = O_HI, O_MD, O_DK, O_KK
        if tone < 0.18:
            hi, md = lt(O_HI, 0.12), mix(O_MD, (250, 176, 50), 0.5)
        elif tone > 0.86:
            md, dd = mix(O_MD, (226, 96, 30), 0.45), mix(O_DK, (170, 60, 20), 0.4)
        px(d, x + 1, y, hi)
        px(d, x + 2, y, md)
        px(d, x, y + 1, hi)
        px(d, x + 1, y + 1, md)
        px(d, x + 2, y + 1, dd)
        px(d, x, y + 2, md)
        px(d, x + 1, y + 2, dd)
        px(d, x + 2, y + 2, kk)
        if hash01(seed, i, 2) < 0.08:
            px(d, x + 1, y - 1, LEAF)
            px(d, x + 2, y - 1, LEAF_D)


def orange_pile(d, cx, base, half_w, hgt, seed, flat=0.8):
    """一堆橘子（从下往上一排排收窄，上一排在后、先画）：cx 中线、base 最下一排的底、half_w 底排半宽、hgt 堆高。"""
    rows = max(1, hgt // 2)
    for r in range(rows - 1, -1, -1):
        u = r / float(max(1, rows))
        hw = half_w * (1.0 - u) ** flat
        y = base - 2 - r * 2
        off = (r % 2) * 1.5
        pts = []
        n = max(1, int(hw * 2 / 3))
        for k in range(n):
            x = int(round(cx - hw + off + k * 3 + hrange(-0.4, 0.4, seed, r, k)))
            if x + 2 > cx + hw + 1:
                break
            pts.append((x, y + (1 if hash01(seed, r, k, 3) < 0.3 else 0)))
        oranges(d, pts, seed * 31 + r)


# ============================================================ 近景：街口
def draw_h0(im):
    x0, x1 = H0
    top = 54
    P.plaster(im, x0, x1, top, LANE - 1, NUB_SKY, 901, streaks=2)
    P.crenels(im, x0, x1 - 1, top, NUB_SKY, 'tri', size=3, gap=1)
    d = ImageDraw.Draw(im)
    P.frieze(d, x0, x1 - 1, top + 2, 3, 'tri', LIME, dk(NUB_SKY, 0.7))
    P.mashrabiya(im, 9, 66, 16, 22, seed=1)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, 99, lt(NUB_SKY, 0.35))                       # 楼层线脚
    hl(d, x0, x1 - 1, 100, dk(NUB_SKY, 0.78))
    P.frieze(d, x0, x1 - 1, 102, 3, 'zig', NUB_BLUE)
    top_door = P.door(im, 12, LANE - 1, 12, 36, P.DOOR_BLUE, frame=LIME, arch=True, pattern='zig', pcol=NUB_BLUE, seed=3)
    d = ImageDraw.Draw(im)
    for (cx, cy, col) in ((4, 116, (60, 100, 170)), (30, 116, (190, 60, 60)), (4, 126, (70, 140, 90))):
        P.plate(d, cx, cy, 2, col)
    rect(d, 26, 128, 33, 133, (36, 72, 140), outline=(230, 230, 230))   # 蓝色搪瓷路牌（白字）
    P.sign_ar(d, 27, 129, 32, 132, None, (240, 240, 236), seed=5, dots=False)
    P.spout(im, x1 - 6, top + 6, L=5, wall=NUB_SKY, stain_len=16)
    return top_door


def draw_gate(im):
    x0, x1 = GATE
    P.palm_trunk(im, 58, 130, 64, lean=3, seed=5)                  # 墙后的海枣树（树冠在 strip）
    P.plaster(im, x0, x1, 124, LANE - 1, LIME, 905, streaks=1, cracks=1)
    P.crenels(im, x0, x1 - 1, 124, LIME, 'tri', size=3, gap=1)
    d = ImageDraw.Draw(im)
    P.frieze(d, x0 + 1, x1 - 2, 127, 3, 'zig', NUB_BLUE)
    P.brick_patch(im, 60, 136, 5, 3, 906)
    d = ImageDraw.Draw(im)
    P.zir_stand(d, 40, LANE - 1)                                   # 路边的水罐（sabil）
    soft_shadow(im, 40, 58, LANE, depth=1, slant=4)


# ============================================================ 近景：黄房子 + 橘子摊
def draw_h1(im):
    x0, x1 = H1
    # 屋顶后面的筒拱 + 穹顶（先画，女儿墙压在脚上）；筒拱端面不画一圈圈拱砖（像素小了读起来像靶子）
    P.vault(im, 82, 118, 84, MUD, rings=False)
    P.dome(im, 170, 84, 15, NUB_YELLOW, vents=4)
    yb = P.lattice_parapet(im, x0, x1 - 1, 77, NUB_YELLOW)
    P.plaster(im, x0, x1, yb, LANE - 1, NUB_YELLOW, 911, streaks=3)
    d = ImageDraw.Draw(im)
    P.frieze(d, x0, x1 - 1, yb + 1, 4, 'tri', NUB_BLUE, LIME)
    P.frieze(d, x0, x1 - 1, LANE - 6, 3, 'check', dk(NUB_YELLOW, 0.86))
    top = P.door(im, 188, LANE - 1, 14, 40, P.DOOR_GREEN, frame=NUB_BLUE, arch=True, pattern='tri', pcol=LIME, seed=7)
    d = ImageDraw.Draw(im)
    P.crocodile(d, 184, top - 9, L=22)
    P.grille_window(im, 78, 94, 8, 8, NUB_YELLOW, frame=NUB_BLUE)
    P.grille_window(im, 146, 94, 8, 8, NUB_YELLOW, frame=NUB_BLUE)
    d = ImageDraw.Draw(im)
    for (cx, cy, col) in ((94, 96, (60, 100, 170)), (128, 96, (60, 140, 120)), (174, 96, (190, 60, 60))):
        P.plate(d, cx, cy, 2, col)
    P.spout(im, 102, yb + 1, L=5, wall=NUB_YELLOW, stain_len=12)
    P.brick_patch(im, 80, 132, 5, 4, 912)


def draw_stall(im):
    a, b = STALL
    d = ImageDraw.Draw(im)
    # 靠墙：三摞椰枣枝筐，筐里的橘子冒尖
    for (cx0, cw, ch, base) in ((a + 3, 14, 9, LANE - 1), (a + 3, 14, 9, LANE - 10), (a + 18, 12, 8, LANE - 1)):
        P.crate(d, cx0, base, cw, ch, col=(186, 150, 98), kind='jarid', seed=cx0 + base)
        pts = [(cx0 + 1 + k * 3, base - ch - 1 + (k % 2)) for k in range((cw - 2) // 3)]
        oranges(d, pts, cx0 + base)
    # 木台
    ty = 128
    rect(d, a + 14, ty, b - 6, ty + 1, WOOD_HI)
    rect(d, a + 14, ty + 2, b - 6, ty + 3, WOOD_D)
    hl(d, a + 14, b - 6, ty + 4, WOOD_K)
    for lx in (a + 16, (a + b) // 2 + 4, b - 8):
        rect(d, lx, ty + 4, lx + 1, LANE - 1, WOOD_D)
        px(d, lx, ty + 4, WOOD)
    hl(d, a + 16, b - 8, LANE - 5, WOOD_D)                          # 腿间的横撑
    # 台下：两只麻袋、一只空筐
    P.sack(d, a + 26, LANE - 1, 8, 10, (196, 170, 120))
    P.sack(d, a + 36, LANE - 1, 7, 8, (184, 160, 112))
    P.basket(d, b - 26, LANE - 1, 10, 6)
    # 台上：堆成山的橘子（宽 60、高 20；最下一排坐在台面上）
    orange_pile(d, (a + b) // 2 - 2, ty - 1, 31, 21, 921, flat=0.85)
    # 价牌：一根小棍插在橘子山上，白纸板红字
    vl(d, a + 26, 112, 122, (150, 120, 80))
    rect(d, a + 22, 107, a + 31, 112, (244, 240, 228), outline=(200, 194, 180))
    P.sign_ar(d, a + 22, 107, a + 31, 112, None, (196, 40, 40), seed=8, dots=False)
    # 弹簧秤（白搪瓷 + 圆表盘 + 红指针 + 钢托盘）
    sx = b - 14
    rect(d, sx - 3, ty - 9, sx + 3, ty - 1, (232, 232, 226))
    vl(d, sx + 3, ty - 9, ty - 1, (176, 176, 170))
    d.ellipse((sx - 2, ty - 8, sx + 2, ty - 4), fill=C((250, 250, 246)))
    d.line((sx, ty - 6, sx + 1, ty - 8), fill=C((210, 40, 40)))
    hl(d, sx - 5, sx + 5, ty - 11, (196, 200, 206))
    hl(d, sx - 4, sx + 4, ty - 10, (150, 154, 160))
    oranges(d, [(sx - 3, ty - 14), (sx, ty - 14), (sx - 1, ty - 16)], 77)
    # 两根木杆 + 篷布（下沿的波浪边在 strip）+ 篷下的影
    for xx in (a - 1, b):
        vl(d, xx, 98, LANE - 1, WOOD_HI)
        vl(d, xx + 1, 98, LANE - 1, WOOD_D)
        px(d, xx, 97, WOOD)
    P.awning(im, a - 3, b + 2, 99, 5, (232, 118, 48), (246, 238, 216), stripe=4, scallop=False, shadow=6)
    soft_shadow(im, a + 12, b - 4, LANE, depth=1, slant=4)


def draw_heap(im):
    """可走带后沿地上的那一小堆：一块麻布（压扁的梯形）+ 一堆橘子，堆顶在 anchors.orange（150, 151–152）。"""
    d = ImageDraw.Draw(im)
    x0, x1 = HEAP
    for y in range(154, 159):                                      # 麻布：越近越宽
        u = (y - 154) / 4.0
        a, b = int(round(x0 + 2 - u * 2)), int(round(x1 - 2 + u * 2))
        for x in range(a, b + 1):
            c = (184, 156, 108) if (x + y) % 2 else (172, 144, 98)
            if y == 158:
                c = (150, 126, 86)
            px(d, x, y, c)
    soft_shadow(im, x0, x1, 159, depth=1, slant=3)
    d = ImageDraw.Draw(im)
    orange_pile(d, 150, 157, 11, 7, 931, flat=0.7)
    oranges(d, [(149, 150)], 932)                                  # 堆顶那一颗（剧情把亮的那颗盖在这）
    oranges(d, [(x0 + 1, 155), (x1 - 4, 156)], 933)                # 滚到边上的两颗


# ============================================================ 近景：青绿窄房
def draw_h2(im):
    x0, x1 = H2
    top = 50
    P.plaster(im, x0, x1, top, LANE - 1, NUB_TURQ, 921, streaks=3)
    P.crenels(im, x0, x1 - 1, top, NUB_TURQ, 'step', size=3, gap=2)
    d = ImageDraw.Draw(im)
    P.frieze(d, x0, x1 - 1, top + 3, 5, 'diamond', LIME, P.PAINT_RED)
    P.grille_window(im, 214, 64, 12, 16, NUB_TURQ, frame=LIME, kind='shutter', shutter=(70, 110, 160), state='closed',
                    seed=3)
    P.grille_window(im, 234, 66, 8, 10, NUB_TURQ, frame=LIME)
    d = ImageDraw.Draw(im)
    for (fx, col) in ((214, (196, 70, 60)), (219, (230, 190, 60)), (224, (196, 70, 60))):   # 窗台花盆
        rect(d, fx, 80, fx + 2, 82, (170, 90, 60))
        px(d, fx + 1, 79, LEAF)
        px(d, fx, 78, col)
        px(d, fx + 2, 79, LEAF_M)
    hl(d, x0, x1 - 1, 92, lt(NUB_TURQ, 0.3))
    hl(d, x0, x1 - 1, 93, dk(NUB_TURQ, 0.78))
    # 墙上画的努比亚壁画（门左边那块墙）：白色帆船 + 黄太阳 + 两道蓝水纹
    sx, sy = 208, 98
    d.ellipse((sx + 12, sy, sx + 17, sy + 5), fill=C((246, 206, 70)))
    for k in range(8):
        ang = k * math.pi / 4
        px(d, sx + 14 + int(round(math.cos(ang) * 4)), sy + 2 + int(round(math.sin(ang) * 4)), (246, 206, 70))
    hl(d, sx + 1, sx + 13, sy + 15, P.PAINT_WHITE)                 # 船身
    hl(d, sx + 3, sx + 11, sy + 16, P.PAINT_WHITE)
    vl(d, sx + 6, sy + 5, sy + 14, (120, 80, 50))                  # 桅杆 + 三角帆
    for k in range(9):
        hl(d, sx + 7, sx + 7 + max(0, 5 - k // 2), sy + 6 + k, P.PAINT_WHITE)
    for k in range(2):
        for x in range(sx, sx + 16):
            if (x + k * 2) % 4 < 2:
                px(d, x, sy + 18 + k * 2, P.PAINT_BLUE)
    P.door(im, 230, LANE - 1, 13, 38, P.DOOR_RED, frame=LIME, arch=False, pattern='dots', pcol=P.PAINT_BLUE, seed=4)
    d = ImageDraw.Draw(im)
    rect(d, 209, 126, 213, 132, (180, 180, 184))                     # 电表箱
    hl(d, 209, 213, 126, (214, 214, 216))
    px(d, 211, 129, (60, 60, 64))
    rect(d, 236, top - 7, 245, top - 1, (176, 176, 178))            # 屋顶的水箱
    hl(d, 236, 245, top - 7, (214, 214, 214))
    vl(d, 245, top - 7, top - 1, (130, 130, 134))
    P.spout(im, x1 - 7, top + 6, L=5, wall=NUB_TURQ, stain_len=14)


# ============================================================ 近景：茶馆
def tea_interior_left(w, h):
    """左拱洞里：后墙（暖暗）+ 靠墙长凳 + 坐垫、一排水烟壶、乌姆·库勒苏姆的小相框、挂着的软管。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    wall, wall_d = (120, 92, 72), (96, 72, 58)
    rect(d, 0, 0, w - 1, h - 1, wall)
    for y in range(0, h, 2):
        for x in range(w):
            if hash01(x, y, 941) < 0.18:
                px(d, x, y, wall_d)
    rect(d, 0, h - 6, w - 1, h - 1, (88, 70, 60))                   # 里面的地（深色水磨石）
    for x in range(0, w, 4):
        px(d, x, h - 4, (104, 84, 70))
    # 相框：金框、深底、一张脸（黑头发 + 墨镜）
    fx, fy = 6, 14
    rect(d, fx, fy, fx + 8, fy + 10, (200, 160, 70))
    rect(d, fx + 1, fy + 1, fx + 7, fy + 9, (60, 50, 60))
    rect(d, fx + 3, fy + 3, fx + 5, fy + 6, (190, 150, 120))
    hl(d, fx + 2, fx + 6, fy + 2, (30, 26, 30))
    px(d, fx + 3, fy + 4, (20, 20, 20))
    px(d, fx + 5, fy + 4, (20, 20, 20))
    hl(d, fx + 2, fx + 6, fy + 8, (120, 40, 60))
    # 长凳 + 坐垫（红绿条纹）
    sy = h - 13
    rect(d, 2, sy, w - 6, sy + 1, (150, 104, 66))
    for x in range(2, w - 6):
        px(d, x, sy - 1, ((180, 50, 50), (60, 120, 80), (220, 180, 70))[(x // 3) % 3])
    for lx in (3, (w - 6) // 2, w - 8):
        vl(d, lx, sy + 2, h - 6, (110, 76, 50))
    # 一排水烟壶（玻璃底 + 铜杆）
    for i, (sx, g) in enumerate(((10, (110, 160, 150)), (18, (160, 90, 120)), (26, (90, 130, 170)))):
        P.shisha(d, sx, h - 6, glass=g)
    # 墙上挂的一个日历（白 + 红日期）
    rect(d, w - 12, 10, w - 6, 18, (236, 232, 222))
    hl(d, w - 12, w - 6, 10, (200, 50, 50))
    for k in range(3):
        hl(d, w - 11, w - 7, 12 + k * 2, (150, 146, 140))
    return im


def tea_interior_right(w, h):
    """右拱洞里：后墙架子上一排排玻璃茶杯 + 茶叶罐 + 收音机、挂钟；木柜台上的铜茶炊（热气在 strip）、托盘。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    wall, wall_d = (126, 98, 76), (100, 78, 62)
    rect(d, 0, 0, w - 1, h - 1, wall)
    for y in range(0, h, 2):
        for x in range(w):
            if hash01(x, y, 942) < 0.16:
                px(d, x, y, wall_d)
    # 挂钟
    d.ellipse((w // 2 - 4, 3, w // 2 + 4, 11), fill=C((240, 236, 226)))
    d.ellipse((w // 2 - 4, 3, w // 2 + 4, 11), outline=C((90, 70, 50)))
    vl(d, w // 2, 4, 7, (30, 30, 30))
    hl(d, w // 2, w // 2 + 2, 7, (30, 30, 30))
    # 两层架子：玻璃杯（亮白 + 浅蓝反光）、茶叶罐、收音机
    for sy in (18, 27):
        hl(d, 2, w - 3, sy, (160, 116, 76))
        hl(d, 2, w - 3, sy + 1, (96, 68, 46))
    for k in range(12):
        gx = 4 + k * 3
        if gx > w - 6:
            break
        rect(d, gx, 14, gx + 1, 17, (214, 228, 232))
        px(d, gx, 14, (250, 252, 252))
    for k, col in enumerate(((200, 60, 50), (60, 120, 170), (220, 180, 60), (80, 140, 90))):
        rect(d, 4 + k * 5, 22, 7 + k * 5, 26, col)
        hl(d, 4 + k * 5, 7 + k * 5, 22, lt(col, 0.3))
    rx = w - 16                                                    # 收音机
    rect(d, rx, 21, rx + 11, 26, (110, 76, 50))
    rect(d, rx + 1, 22, rx + 5, 25, (180, 160, 120))
    for k in range(3):
        px(d, rx + 7 + k, 23, (40, 34, 30))
    vl(d, rx + 10, 15, 20, (180, 180, 186))
    # 柜台（木，前脸有竖板）
    cy = h - 17
    rect(d, 2, cy, w - 3, h - 1, (128, 86, 54))
    hl(d, 1, w - 2, cy, (178, 132, 84))
    hl(d, 1, w - 2, cy + 1, (150, 104, 66))
    for x in range(5, w - 3, 5):
        vl(d, x, cy + 3, h - 2, (106, 70, 44))
    hl(d, 2, w - 3, h - 1, (80, 56, 40))
    # 铜茶炊（鼓肚子、龙头、顶上的小烟囱）
    sx = 18
    d.ellipse((sx - 6, cy - 16, sx + 6, cy - 2), fill=C(BRASS[1]))
    d.chord((sx - 6, cy - 16, sx + 6, cy - 2), 120, 240, fill=C(BRASS[2]))
    d.chord((sx - 6, cy - 16, sx + 6, cy - 2), 300, 60, fill=C(BRASS[0]))
    px(d, sx - 3, cy - 12, BRASS[3])
    px(d, sx - 4, cy - 10, BRASS[3])
    rect(d, sx - 2, cy - 19, sx + 2, cy - 16, BRASS[1])
    hl(d, sx - 3, sx + 3, cy - 19, BRASS[2])
    vl(d, sx, cy - 22, cy - 20, (70, 60, 56))
    rect(d, sx - 4, cy - 2, sx + 4, cy, BRASS[0])
    hl(d, sx + 6, sx + 8, cy - 6, BRASS[2])                        # 龙头
    px(d, sx + 8, cy - 5, BRASS[0])
    # 托盘 + 两杯茶 + 一碟薄荷叶
    hl(d, w - 20, w - 8, cy - 1, (200, 204, 210))
    P.tea_glass(d, w - 18, cy - 2)
    P.tea_glass(d, w - 13, cy - 2)
    hl(d, 28, 34, cy - 1, (226, 226, 222))
    for k in range(3):
        px(d, 29 + k * 2, cy - 2, LEAF_M)
    return im


TEA_ARCH_L = (258, 296)        # 左拱洞 x0..x1（不含）
TEA_ARCH_R = (310, 360)
TEA_SPRING = 109               # 起拱线（拱高一点，茶炊的热气才有地方飘）
TEA_RISE = 11


def draw_teahouse(im):
    x0, x1 = TEA
    top = 58
    P.plaster(im, x0, x1, top, LANE - 1, LIME, 931, streaks=3)
    P.crenels(im, x0, x1 - 1, top, LIME, 'step', size=3, gap=2)
    d = ImageDraw.Draw(im)
    P.frieze(d, x0, x1 - 1, top + 2, 4, 'tri', TEAL, lt(TEAL, 0.4))
    hl(d, x0, x1 - 1, top + 7, dk(LIME, 0.84))
    for wx in (264, 342):                                          # 二楼两扇青绿百叶窗
        P.grille_window(im, wx, 68, 12, 16, LIME, frame=lt(TEAL, 0.5), kind='shutter', shutter=TEAL,
                        state='half' if wx == 264 else 'closed', seed=wx)
    P.mashrabiya(im, 300, 64, 22, 22, seed=5)
    d = ImageDraw.Draw(im)
    # 招牌：绿底白字 + 左边一只茶杯
    sx0, sx1, sy0, sy1 = 262, 360, 88, 96
    rect(d, sx0, sy0, sx1, sy1, (40, 108, 72), outline=(26, 70, 48))
    hl(d, sx0 + 1, sx1 - 1, sy0 + 1, (70, 140, 100))
    P.sign_ar(d, sx0 + 14, sy0, sx1 - 2, sy1, None, (244, 240, 226), seed=11, rows=1)
    gx, gy = sx0 + 4, sy0 + 2
    rect(d, gx, gy, gx + 4, gy + 5, (230, 236, 236))
    rect(d, gx + 1, gy + 2, gx + 3, gy + 5, (190, 60, 34))
    hl(d, gx - 1, gx + 5, gy + 6, (230, 230, 226))
    mul_box(im, (sx0 + 2, sy1 + 1, sx1 + 2, sy1 + 2), SHADOW_MUL, level=0.6)
    # 两个尖拱敞口（里面的东西先画好再按拱的形状贴进来）
    for (a, b, fn) in ((TEA_ARCH_L[0], TEA_ARCH_L[1], tea_interior_left), (TEA_ARCH_R[0], TEA_ARCH_R[1], tea_interior_right)):
        inner = fn(b - a, (LANE - 1) - (TEA_SPRING - TEA_RISE) + 1)
        put_inside(im, inner, a, TEA_SPRING, TEA_RISE, pointed=True)
    d = ImageDraw.Draw(im)
    for (a, b) in (TEA_ARCH_L, TEA_ARCH_R):                        # 拱脚的小柱头 + 门槛
        for xx in (a - 2, b):
            rect(d, xx, TEA_SPRING - 1, xx + 1, TEA_SPRING, lt(LIME, 0.3))
        hl(d, a - 1, b, LANE - 1, (196, 188, 170))
    # 拱下挂的铜灯笼（链子从拱顶垂下来）
    for cx in ((TEA_ARCH_L[0] + TEA_ARCH_L[1]) // 2, (TEA_ARCH_R[0] + TEA_ARCH_R[1]) // 2):
        P.lantern(d, cx, TEA_SPRING - TEA_RISE + 1, chain=4)
    # 门外：长凳（带靠背）+ 一只水烟壶 + 一张小圆桌（抽水烟的老人在 people 层，坐在长凳左头）
    P.bench(d, 252, 292, 137, LANE - 1, wood=(150, 104, 64), back=True)
    P.shisha(d, 268, LANE - 1, glass=(120, 170, 150))
    P.round_table(d, 282, LANE - 1, 136, r=5, col=(170, 176, 180))
    P.tea_glass(d, 279, 135)
    P.tea_glass(d, 284, 135)
    soft_shadow(im, 252, 292, LANE, depth=1, slant=4)
    # 右边门外靠墙一摞塑料箱（汽水瓶）
    for k in range(2):
        yb = LANE - 1 - k * 6
        rect(d, 362, yb - 5, 370, yb, (200, 60, 50))
        hl(d, 362, 370, yb - 5, (230, 110, 90))
        for x in range(363, 370, 2):
            px(d, x, yb - 6, (90, 60, 40))
            px(d, x, yb - 7, (200, 220, 210))
    P.spout(im, x0 + 2, top + 8, L=5, wall=LIME, stain_len=14)


def draw_tea_table(im):
    """可走带里的小圆铁桌 + 两把木椅（乔瑟夫朝右坐左边、阿布德尔朝左坐右边；坐姿的屁股在脚点往后 0–6 px、高 6 px）。"""
    d = ImageDraw.Draw(im)
    for (sx, face) in SEATS:
        cx = sx - 3 * face                                         # 椅子中心在坐姿屁股下面
        P.chair(d, cx, TABLE_BASE, face=face, col=(150, 104, 62), seat_y=TABLE_BASE - 6)
    P.round_table(d, TABLE_X, TABLE_BASE, TABLE_TOP, r=6, col=(164, 170, 174))
    soft_shadow(im, TABLE_X - 6, TABLE_X + 6, TABLE_BASE + 1, depth=1, slant=3)
    for (sx, face) in SEATS:
        soft_shadow(im, sx - 3 * face - 3, sx - 3 * face + 3, TABLE_BASE + 1, depth=1, slant=2)


# ============================================================ 近景：布店
CLOTH_SHOP = (380, 472)        # 店面敞口
CLOTH_RAIL = 106               # 挂布的横杆


def draw_cloth_shop(im):
    x0, x1 = CLOTH
    top = 52
    P.plaster(im, x0, x1, top, LANE - 1, NUB_PINK, 951, streaks=3)
    P.crenels(im, x0, x1 - 1, top, NUB_PINK, 'tri', size=3, gap=1)
    d = ImageDraw.Draw(im)
    P.frieze(d, x0, x1 - 1, top + 2, 3, 'zig', LIME, None)
    for wx in (386, 452):                                          # 二楼两扇百叶窗
        P.grille_window(im, wx, 64, 12, 16, NUB_PINK, frame=LIME, kind='shutter', shutter=(70, 110, 160),
                        state='open' if wx == 386 else 'half', seed=wx)
    # 中间的铁栏杆小阳台 + 门 + 花盆
    d = ImageDraw.Draw(im)
    rect(d, 414, 62, 438, 84, DARK_IN)
    rect(d, 413, 61, 439, 61, lt(NUB_PINK, 0.4))
    vl(d, 426, 62, 84, (90, 70, 60))
    rect(d, 410, 84, 442, 85, (200, 196, 190))
    hl(d, 410, 442, 86, (120, 110, 104))
    for x in range(411, 442, 3):
        vl(d, x, 77, 83, IRON)
    hl(d, 410, 442, 76, IRON_HI)
    for (fx, col) in ((412, (210, 60, 70)), (434, (240, 200, 60))):
        rect(d, fx, 81, fx + 4, 83, (170, 90, 60))
        rect(d, fx, 77, fx + 4, 80, LEAF)
        px(d, fx + 1, 77, col)
        px(d, fx + 3, 78, col)
    mul_box(im, (412, 87, 444, 90), SHADOW_MUL, level=0.7)
    # 招牌：蓝底白字 + 一卷布的小图
    sx0, sx1, sy0, sy1 = 384, 468, 91, 99
    rect(d, sx0, sy0, sx1, sy1, (42, 82, 150), outline=(28, 54, 100))
    hl(d, sx0 + 1, sx1 - 1, sy0 + 1, (80, 120, 186))
    P.sign_ar(d, sx0 + 12, sy0, sx1 - 2, sy1, None, (246, 242, 230), seed=21)
    rect(d, sx0 + 3, sy0 + 3, sx0 + 9, sy0 + 5, (220, 80, 90))
    px(d, sx0 + 9, sy0 + 4, (250, 200, 200))
    # 店面：卷帘门收在上面、里面三层架子的彩布卷、柜台上叠好的布、一面镜子
    a, b = CLOTH_SHOP
    rect(d, a, 101, b - 1, LANE - 1, (92, 72, 64))
    for yy in range(101, 106):
        hl(d, a, b - 1, yy, (160, 164, 160) if yy % 2 else (186, 190, 184))
    hl(d, a, b - 1, 106, (96, 100, 98))
    for sy in (115, 124, 133):
        hl(d, a + 1, b - 2, sy, (156, 114, 74))
        hl(d, a + 1, b - 2, sy + 1, (100, 72, 48))
        x = a + 2
        k = 0
        while x < b - 7:
            col = P.CLOTH[int(hash01(sy, k, 952) * len(P.CLOTH))]
            wv = 6 + int(hash01(sy, k, 953) * 3)
            rect(d, x, sy - 4, x + wv - 1, sy - 1, col)
            hl(d, x, x + wv - 1, sy - 4, lt(col, 0.3))
            vl(d, x + wv - 1, sy - 4, sy - 1, dk(col, 0.7))
            px(d, x, sy - 2, dk(col, 0.6))
            x += wv + 1
            k += 1
    rect(d, a + 6, 136, b - 7, 137, (176, 132, 86))                 # 柜台
    rect(d, a + 6, 138, b - 7, LANE - 1, (132, 92, 58))
    for x in range(a + 9, b - 7, 6):
        vl(d, x, 139, LANE - 2, (110, 74, 46))
    for k, col in enumerate(((236, 220, 180), (200, 60, 70), (70, 120, 180), (240, 190, 60))):
        rect(d, a + 10 + k * 8, 133, a + 16 + k * 8, 135, col)
        hl(d, a + 10 + k * 8, a + 16 + k * 8, 133, lt(col, 0.3))
    rect(d, b - 14, 108, b - 9, 113, (190, 210, 214))               # 镜子
    rect(d, b - 15, 107, b - 8, 114, None, outline=(170, 130, 70))
    vl(d, a, 101, LANE - 1, dk(NUB_PINK, 0.6))                      # 敞口左沿 / 上沿的影（墙的厚度）
    vl(d, a + 1, 101, LANE - 1, (70, 56, 50))
    mul_box(im, (a, 107, b - 1, 109), SHADOW_MUL)
    d = ImageDraw.Draw(im)
    # 挂布的横杆（两头钉在墙上）
    hl(d, a - 2, b + 1, CLOTH_RAIL, (120, 90, 60))
    hl(d, a - 2, b + 1, CLOTH_RAIL + 1, (80, 60, 44))
    # 遮阳棚（蓝白条纹，波浪边在 strip）
    P.awning(im, a - 4, b + 3, 99, 4, (52, 104, 170), (240, 240, 232), stripe=4, scallop=False, shadow=0)
    # 门边靠着的布卷
    d = ImageDraw.Draw(im)
    for k, (fx, col) in enumerate(((374, (220, 70, 80)), (377, (60, 140, 120)), (474, (240, 190, 60)),
                                   (477, (120, 80, 170)))):
        lean = 1 if k % 2 else 0
        for yy in range(118, LANE):
            u = (yy - 118) / float(LANE - 118)
            xx = fx + int(round((1 - u) * 2 * lean))
            px(d, xx, yy, col)
            px(d, xx + 1, yy, dk(col, 0.75))
        px(d, fx + 2 * lean, 117, lt(col, 0.4))
    soft_shadow(im, a, b, LANE, depth=1, slant=3)


# ============================================================ 近景：马车停靠点
def draw_stop(im):
    x0, x1 = STOP
    # 墙后的大无花果树：树干露在墙头上一截、树冠一团团（左上亮），树冠里漏几处天
    d = ImageDraw.Draw(im)
    for yy in range(84, 113):
        u = (yy - 84) / 28.0
        hw = 2 + int(u * 2)
        for k in range(-hw, hw + 1):
            c = (132, 112, 92) if k < 0 else ((104, 88, 74) if k < hw else (76, 64, 56))
            px(d, 522 + k, yy, c)
    for (bx, by, ex, ey) in ((522, 92, 500, 70), (523, 88, 544, 64), (522, 96, 556, 84)):
        d.line((bx, by, ex, ey), fill=C((112, 94, 80)))
        d.line((bx, by + 1, ex, ey + 1), fill=C((90, 76, 64)))
    pal = ((46, 86, 52), (66, 116, 62), (96, 146, 76), (140, 182, 96))
    V._canopy(d, 522, 66, 44, 26, 961, pal=pal)
    V._canopy(d, 494, 82, 18, 12, 962, pal=pal)
    V._canopy(d, 552, 80, 20, 14, 963, pal=pal)
    leafy(im, (470, 34, 576, 100), pal, 964)                       # 平涂的疙瘩上加叶子的碎、边上啃 / 冒叶子
    # 院墙（土坯抹灰 + 镂空女儿墙）
    yb = P.lattice_parapet(im, x0, x1 - 1, 110, MUD, hole=3, period=5)
    P.plaster(im, x0, x1, yb, LANE - 1, MUD, 964, streaks=2, cracks=3)
    P.brick_patch(im, 540, 128, 7, 4, 965)
    P.brick_patch(im, 496, 136, 4, 3, 966)
    # 树荫：墙上 + 墙脚那两行地上一片斑驳的影（不进可走带：可走带要平、马车停靠段要只有路面）
    m = np.zeros((H, PW), bool)
    for y in range(yb, WALK[0]):
        for x in range(x0, x1 + 14):
            if hash01(x // 3, y // 2, 967) < 0.62:
                m[y, x] = True
    mul_mask(im, m, SOFT_MUL, level=0.85)
    d = ImageDraw.Draw(im)
    # “马车站”蓝牌：木杆上一块蓝铁皮，白色的马车图标
    vl(d, 492, 104, LANE - 1, (110, 110, 116))
    vl(d, 493, 104, LANE - 1, (76, 76, 82))
    rect(d, 486, 100, 499, 112, (44, 90, 170), outline=(230, 230, 230))
    picto(im, PICTO_CARRIAGE, 488, 102)
    d = ImageDraw.Draw(im)
    # 墙上刷的旧汽水广告（红圆 + 白瓶子 + 一行字，晒褪了色）+ 靠墙的自行车 + 墙头趴着的猫
    rect(d, 526, 122, 556, 134, (214, 196, 176))
    d.ellipse((528, 123, 538, 133), fill=C((190, 70, 60)))
    rect(d, 532, 124, 534, 132, (236, 232, 222))
    px(d, 533, 123, (236, 232, 222))
    P.sign_ar(d, 540, 124, 555, 132, None, (60, 90, 150), seed=61, rows=2, dots=False)
    bicycle(d, 506, LANE - 1)
    for (cx_, cy_) in ((548, 109),):
        rect(d, cx_, cy_ - 2, cx_ + 5, cy_, (60, 54, 50))
        px(d, cx_ + 6, cy_ - 3, (60, 54, 50))
        px(d, cx_ + 6, cy_ - 2, (60, 54, 50))
        px(d, cx_ + 7, cy_ - 3, (60, 54, 50))
        px(d, cx_ + 6, cy_ - 4, (60, 54, 50))
        px(d, cx_ + 8, cy_ - 4, (60, 54, 50))
        hl(d, cx_ - 3, cx_ - 1, cy_, (60, 54, 50))
        px(d, cx_ - 4, cy_ - 1, (60, 54, 50))
    # 墙脚：一堆三叶草料（绿）+ 一只草料袋
    for k in range(40):
        x = int(hrange(548, 566, k, 968))
        y = int(hrange(LANE - 7, LANE - 1, k, 969))
        if y >= LANE - 7 + abs(x - 557) // 3:
            px(d, x, y, (LEAF, LEAF_M, (120, 160, 70), LEAF_D)[k % 4])
    P.sack(d, 540, LANE - 1, 8, 9, (200, 180, 130))


def draw_h5(im):
    x0, x1 = H5
    P.vault(im, 576, 614, 84, NUB_BLUE, rings=False)
    yb = P.lattice_parapet(im, x0, x1 - 1, 78, NUB_BLUE)
    P.plaster(im, x0, x1, yb, LANE - 1, NUB_BLUE, 971, streaks=3)
    d = ImageDraw.Draw(im)
    P.frieze(d, x0, x1 - 1, yb + 1, 4, 'tri', LIME, NUB_YELLOW)
    # 门矮一点（36），门楣上的鳄鱼才落在花纹带下面的墙上
    top = P.door(im, 616, LANE - 1, 16, 36, (176, 120, 60), frame=NUB_YELLOW, arch=True, pattern='tri', pcol=P.PAINT_RED,
                 seed=9)
    d = ImageDraw.Draw(im)
    P.crocodile(d, 613, top - 9, L=22)
    for (cx, cy, col) in ((608, 112, (60, 100, 170)), (638, 112, (190, 60, 60)), (608, 120, (230, 190, 60))):
        P.plate(d, cx, cy, 2, col)
    P.grille_window(im, 574, 98, 9, 9, NUB_BLUE, frame=LIME)
    d = ImageDraw.Draw(im)
    # 墙上画的海枣树（白杆 + 绿叶）
    tx = 594
    for yy in range(104, 124):
        px(d, tx + (1 if yy < 110 else 0), yy, P.PAINT_WHITE)
    for k in range(7):
        ang = math.radians(20 + k * 23)
        for j in range(1, 6):
            px(d, tx + 1 + int(round(math.cos(ang) * j)), 104 - int(round(math.sin(ang) * j * 0.7)) + j // 2, (60, 150, 80))
    # 水槽（石头）+ 墙上伸出来的水龙头
    a, b = 570, 600
    rect(d, a, 136, b, LANE - 1, (172, 164, 150))
    hl(d, a, b, 136, (210, 204, 192))
    hl(d, a + 1, b - 1, 137, (120, 150, 160))                       # 水面
    hl(d, a + 1, b - 1, 138, (100, 132, 146))
    vl(d, a, 136, LANE - 1, (196, 190, 178))
    vl(d, b, 136, LANE - 1, (130, 124, 112))
    for x in range(a + 3, b - 2, 6):
        vl(d, x, 140, LANE - 2, (156, 148, 136))
    hl(d, a, b, LANE - 1, (120, 112, 102))
    rect(d, 584, 126, 585, 129, IRON_HI)                            # 水龙头
    hl(d, 584, 588, 126, IRON_HI)
    px(d, 588, 127, IRON)
    for k in range(3):
        px(d, 588, 129 + k * 2, WATER[1])
    # 黑胶皮桶
    rect(d, 562, 138, 568, LANE - 1, (50, 46, 46))
    hl(d, 562, 568, 138, (90, 86, 86))
    vl(d, 562, 138, LANE - 1, (76, 72, 70))
    # 拴马桩（木桩 + 铁环）
    rect(d, 605, 127, 607, LANE - 1, WOOD)
    vl(d, 605, 127, LANE - 1, WOOD_HI)
    vl(d, 607, 127, LANE - 1, WOOD_D)
    hl(d, 605, 607, 126, lt(WOOD, 0.3))
    d.ellipse((606, 130, 610, 134), outline=C(IRON_HI))
    soft_shadow(im, a, b, LANE, depth=1, slant=3)
    P.spout(im, x0 + 4, yb + 1, L=5, wall=NUB_BLUE, stain_len=12)


# ============================================================ 近景：赭黄楼 + 窄巷 + 木箱
def draw_h6(im):
    x0, x1 = H6
    top = 42
    P.plaster(im, x0, x1, top, LANE - 1, NUB_OCHRE, 981, streaks=4)
    P.crenels(im, x0, x1 - 1, top, NUB_OCHRE, 'step', size=3, gap=2)
    d = ImageDraw.Draw(im)
    P.frieze(d, x0, x1 - 1, top + 2, 3, 'check', lt(NUB_OCHRE, 0.4))
    P.mashrabiya(im, 652, 54, 20, 24, seed=7)
    P.grille_window(im, 656, 92, 10, 14, NUB_OCHRE, frame=LIME, kind='shutter', shutter=P.DOOR_GREEN, state='half', seed=6)
    d = ImageDraw.Draw(im)
    for yy in (86, 112):
        hl(d, x0, x1 - 1, yy, lt(NUB_OCHRE, 0.3))
        hl(d, x0, x1 - 1, yy + 1, dk(NUB_OCHRE, 0.78))
    # 一楼：拉下的绿卷帘门 + 小招牌
    a, b = 646, 680
    rect(d, a, 120, b, LANE - 1, (70, 120, 96))
    for yy in range(120, LANE):
        if yy % 2 == 0:
            hl(d, a, b, yy, (90, 140, 112))
    hl(d, a, b, LANE - 4, (50, 90, 72))
    rect(d, a + 14, LANE - 4, a + 20, LANE - 3, IRON_HI)            # 锁
    rect(d, a - 1, 117, b + 1, 119, (200, 190, 170))
    rect(d, a + 4, 112, b - 4, 117, (236, 220, 120), outline=(160, 140, 60))
    P.sign_ar(d, a + 4, 112, b - 4, 117, None, (150, 40, 40), seed=31, dots=False)
    P.brick_patch(im, 645, 100, 4, 3, 982)
    d = ImageDraw.Draw(im)
    bird_cage(d, 646, 90)                                          # 窗边挂的鸟笼
    ax = 676                                                       # 屋顶的电视天线（80 年代）
    vl(d, ax, top - 16, top - 1, (100, 100, 106))
    for k, w in ((0, 5), (3, 4), (6, 3), (9, 2)):
        hl(d, ax - w, ax + w, top - 16 + k, (100, 100, 106))


ALLEY_BACK = 128               # 巷子尽头地面的 y（巷子往里微微上坡）
ALLEY_IN = (692, 708)          # 巷底的宽（透视收窄）


def draw_alley(im):
    a, b = ALLEY
    ia, ib = ALLEY_IN
    d = ImageDraw.Draw(im)
    # 巷底的房子：一面墙 + 小蓝门 + 两级台阶 + 门上一盏小灯
    wall = (214, 186, 150)
    rect(d, ia, 66, ib - 1, ALLEY_BACK, wall)
    mottle(im, (ia, 66, ib - 1, ALLEY_BACK), wall, dk(wall, 0.92), lt(wall, 0.08), 991, cell=3)
    d = ImageDraw.Draw(im)
    rect(d, ia + 4, 104, ia + 11, ALLEY_BACK - 3, (60, 100, 150))
    vl(d, ia + 7, 104, ALLEY_BACK - 3, (40, 70, 110))
    px(d, ia + 6, 116, BRASS[2])
    hl(d, ia + 2, ia + 13, ALLEY_BACK - 2, (180, 168, 150))
    hl(d, ia + 1, ia + 14, ALLEY_BACK - 1, (160, 148, 130))
    rect(d, ia + 7, 98, ia + 8, 99, (250, 230, 160))
    # 两边的墙（透视）：左墙朝右（背阴）、右墙朝左（上半截受光）
    for x in range(a, ia):
        u = (x - a) / float(ia - a)
        t = int(round(42 + u * (66 - 42)))
        yb = int(round(LANE - 1 - u * (LANE - 1 - ALLEY_BACK)))
        for y in range(t, yb + 1):
            c = (150, 116, 84) if (x + y) % 5 else (138, 106, 78)
            px(d, x, y, c)
    for x in range(ib, b):
        u = (b - 1 - x) / float(b - 1 - ib)
        t = int(round(60 + u * (66 - 60)))
        yb = int(round(LANE - 1 - u * (LANE - 1 - ALLEY_BACK)))
        for y in range(t, yb + 1):
            c = (214, 206, 190) if y < 96 else (186, 178, 164)
            if (x * 3 + y) % 7 == 0:
                c = dk(c, 0.93)
            px(d, x, y, c)
    # 地面（往里上坡，石板缝）
    for y in range(ALLEY_BACK, LANE):
        u = (y - ALLEY_BACK) / float(LANE - 1 - ALLEY_BACK)
        xa = int(round(ia - u * (ia - a)))
        xb = int(round(ib - 1 + u * (b - ib)))
        for x in range(xa, xb + 1):
            c = (176, 160, 134) if (y % 4) else (160, 146, 122)
            px(d, x, y, c)
    # 墙上的一根管子、一只破筐、一只趴在台阶上的猫
    vl(d, a + 3, 60, 140, (110, 104, 100))
    P.basket(d, ib - 7, ALLEY_BACK + 7, 6, 4, (170, 140, 90))
    cx, cy = ia + 12, ALLEY_BACK - 3
    rect(d, cx, cy - 2, cx + 4, cy, (70, 64, 60))
    px(d, cx + 4, cy - 3, (70, 64, 60))
    px(d, cx + 5, cy - 3, (70, 64, 60))
    px(d, cx + 5, cy - 2, (200, 190, 80))
    hl(d, cx - 2, cx, cy, (70, 64, 60))
    # 整条巷子罩在影子里（右墙上半截除外），越往里越暗
    m = np.zeros((H, PW), bool)
    for y in range(40, LANE):
        for x in range(a, b):
            if not (x >= ib and y < 96):
                m[y, x] = True
    mul_mask(im, m, SHADOW_MUL)
    m2 = np.zeros((H, PW), bool)                                   # 巷底再暗一档（整块乘，不用 Bayer：抖开会出棋盘格）
    m2[66:ALLEY_BACK + 1, ia:ib] = True
    mul_mask(im, m2, np.array((0.88, 0.87, 0.9), np.float32))
    # 晾衣绳的两头（钉子），绳和衣服在 strip
    d = ImageDraw.Draw(im)
    for (y0, y1) in ((80, 82), (94, 95)):
        px(d, a + 1, y0, IRON)
        px(d, b - 2, y1, IRON)


CRATES = [(708, LANE + 1, 14, 12, (176, 136, 88)), (721, LANE + 1, 13, 10, (164, 126, 80)),
          (710, LANE - 11, 12, 10, (186, 146, 96))]


def draw_crates(im):
    d = ImageDraw.Draw(im)
    for i, (x0, base, w, h, col) in enumerate(CRATES):
        P.crate(d, x0, base, w, h, col=col, kind='plank', seed=40 + i)
    for k in range(5):                                             # 箱子上的麻绳、标签
        px(d, 712 + k, 127, (200, 180, 130))
    rect(d, 724, 140, 729, 143, (230, 226, 210))
    P.sign_ar(d, 724, 140, 729, 143, None, (60, 60, 60), seed=41, dots=False)
    for k in range(6):                                             # 塞在箱子后面的一卷旧报纸（剧情：伊奇从这叼出漫画页）
        px(d, 733 + k // 3, 142 + k % 3, (226, 222, 206))
    soft_shadow(im, 708, 734, LANE + 2, depth=1, slant=3)


def draw_h7(im):
    x0, x1 = H7
    top = 60
    P.plaster(im, x0, x1, top, LANE - 1, LIME, 1001, streaks=2)
    P.crenels(im, x0, x1 - 1, top, LIME, 'tri', size=3, gap=1)
    d = ImageDraw.Draw(im)
    P.frieze(d, x0, x1 - 1, top + 2, 3, 'tri', NUB_BLUE)
    vl(d, 746, 28, top - 1, (150, 150, 156))                       # 旗杆（旗在 strip）
    px(d, 746, 27, BRASS[2])
    P.grille_window(im, 722, 72, 10, 12, LIME, frame=NUB_BLUE, kind='bars')
    P.grille_window(im, 738, 72, 8, 12, LIME, frame=NUB_BLUE)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, 92, lt(LIME, 0.3))
    hl(d, x0, x1 - 1, 93, dk(LIME, 0.84))
    # 朝觐画：黑色天房（金带）+ 蓝飞机 + 黄骆驼
    kx, ky = 734, 104
    rect(d, kx, ky, kx + 8, ky + 8, (30, 28, 32))
    hl(d, kx, kx + 8, ky + 2, (214, 170, 60))
    hl(d, kx - 1, kx + 9, ky + 9, (120, 110, 100))
    ax, ay = 718, 100
    hl(d, ax, ax + 10, ay, P.PAINT_BLUE)
    hl(d, ax + 1, ax + 9, ay + 1, P.PAINT_BLUE)
    vl(d, ax + 5, ay - 3, ay + 4, P.PAINT_BLUE)
    vl(d, ax + 1, ay - 2, ay, P.PAINT_BLUE)
    cxm, cym = 720, 118
    rect(d, cxm, cym, cxm + 7, cym + 2, (214, 170, 80))
    px(d, cxm + 2, cym - 1, (214, 170, 80))
    px(d, cxm + 3, cym - 2, (214, 170, 80))
    vl(d, cxm + 8, cym - 3, cym, (214, 170, 80))
    px(d, cxm + 9, cym - 3, (214, 170, 80))
    for lx in (cxm, cxm + 2, cxm + 5, cxm + 7):
        vl(d, lx, cym + 3, cym + 6, (214, 170, 80))
    for x in range(716, 750, 2):                                   # 画下面一道绿色的“路”
        px(d, x, 127, (70, 150, 90))


# ============================================================ 近景：清真寺 + 喷泉
def draw_mosque(im):
    x0, x1 = MOSQUE
    top = 96
    # 后面的大穹顶（鼓座一圈小窗 + 新月）
    d = ImageDraw.Draw(im)
    rect(d, 790, 86, 834, top, CREAM)
    for x in range(794, 832, 6):
        rect(d, x, 89, x + 1, 93, DARK_IN)
    hl(d, 790, 834, 86, lt(CREAM, 0.3))
    vl(d, 834, 86, top, dk(CREAM, 0.8))
    P.dome(im, 812, 86, 21, CREAM, hgt=20, finial=BRASS[2], courses=False, drum=2)
    d = ImageDraw.Draw(im)
    px(d, 811, 60, BRASS[2])
    px(d, 813, 60, BRASS[2])
    px(d, 811, 59, BRASS[2])
    # 墙 + 阶梯垛（左边一直接到白房子，不留缝）
    P.plaster(im, x0, x1 - 4, top, LANE - 1, CREAM, 1011, streaks=2, cracks=1)
    P.crenels(im, x0, x1 - 5, top, CREAM, 'step', size=3, gap=2)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 5, top + 3, dk(CREAM, 0.86))
    P.frieze(d, x0, x1 - 5, top + 5, 3, 'chev', (176, 150, 110))
    # 左边两孔尖拱回廊（里面暗：后墙 + 一盏灯 + 一排拖鞋架）
    for (a, b) in ((760, 778), (782, 800)):
        inner = A._new(b - a, (LANE - 1) - (122 - 10) + 1)
        di = ImageDraw.Draw(inner)
        rect(di, 0, 0, b - a - 1, inner.height - 1, (150, 132, 112))
        for y in range(0, inner.height, 3):
            hl(di, 0, b - a - 1, y, (140, 122, 104))
        rect(di, 0, inner.height - 5, b - a - 1, inner.height - 1, (170, 152, 126))
        P.lantern(di, (b - a) // 2, 0, chain=5)
        put_inside(im, inner, a, 122, 10, pointed=True)
    d = ImageDraw.Draw(im)
    # 中间墙上的大理石碑（白底 + 金字），喷泉柱就在它前面
    rect(d, 800, 104, 824, 116, (236, 234, 228), outline=(176, 160, 130))
    hl(d, 801, 823, 105, (250, 250, 246))
    P.sign_ar(d, 801, 105, 823, 115, None, (176, 140, 60), seed=51, rows=2, dots=True)
    # 右边门楼：石头框 + 尖拱门洞 + 半开的绿门 + 门上一道绿底金字 + 门楼顶的小垛
    ga, gb = 838, 870
    rect(d, ga, 92, gb, LANE - 1, STONE)
    vl(d, ga, 92, LANE - 1, lt(STONE, 0.3))
    vl(d, gb, 92, LANE - 1, dk(STONE, 0.75))
    P.crenels(im, ga, gb - 1, 92, STONE, 'step', size=3, gap=1)
    d = ImageDraw.Draw(im)
    rect(d, ga + 3, 96, gb - 3, 101, (40, 110, 70))
    P.sign_ar(d, ga + 3, 96, gb - 3, 101, None, (226, 190, 90), seed=52, dots=False)
    inner = A._new(20, (LANE - 1) - (116 - 12) + 1)
    di = ImageDraw.Draw(inner)
    rect(di, 0, 0, 19, inner.height - 1, (70, 58, 52))
    rect(di, 0, 6, 9, inner.height - 1, (60, 120, 86))               # 左扇（关着）
    for x in range(1, 9, 3):
        vl(di, x, 7, inner.height - 2, (44, 96, 66))
    for y in range(10, inner.height - 2, 6):
        for x in (2, 6):
            px(di, x, y, BRASS[2])
    rect(di, 12, 8, 13, inner.height - 1, (50, 104, 74))             # 右扇（推开，只看见边）
    rect(di, 14, 10, 19, inner.height - 1, (110, 90, 74))           # 门里的光（院子）
    hl(di, 14, 19, inner.height - 3, (150, 130, 100))
    put_inside(im, inner, ga + 6, 116, 12, pointed=True)
    d = ImageDraw.Draw(im)
    for k in range(3):                                             # 门口三级台阶
        hl(d, ga + 2 - k, gb - 2 + k, LANE - 3 + k, lt(STONE, 0.15) if k % 2 == 0 else dk(STONE, 0.85))
    for (sx, col) in ((ga + 4, (60, 50, 44)), (ga + 8, (120, 80, 50)), (gb - 7, (40, 40, 60))):   # 拖鞋
        hl(d, sx, sx + 2, LANE - 1, col)
        px(d, sx + 1, LANE - 2, col)
    # 宣礼塔（右端，从地面起）
    P.minaret(im, 886, LANE - 1, 14, 11, CREAM)
    d = ImageDraw.Draw(im)
    P.lantern(d, 874, 102, chain=2)                                # 门楼右边墙上的铜灯（回廊里已经各挂一盏）
    soft_shadow(im, x0 + 4, x1 - 4, LANE, depth=1, slant=4)


def draw_fountain(im):
    """八角喷泉池（可走带后沿）：池沿顶 y 150（亮）、前壁 151–157（石头 + 竖缝 + 一圈蓝白瓷砖）、池后沿 y 146；
    池中一根石柱（y 124–149）托着一只石碗（y 119–124），顶上一个小喷嘴（水在 strip）。"""
    d = ImageDraw.Draw(im)
    a, b = FOUNT
    st, st_hi, st_sh, st_kk = (206, 194, 172), (230, 222, 204), (176, 164, 144), (140, 128, 112)
    # 池后沿（远的那一圈）+ 水面（strip 画涟漪，这里画底色）
    hl(d, a + 4, b - 4, LANE, st_hi)
    hl(d, a + 3, b - 3, LANE + 1, st)
    for y in range(LANE + 2, RIM_TOP):
        hl(d, a + 2, b - 2, y, WATER[2] if y < RIM_TOP - 1 else WATER[3])
    # 石柱 + 石碗 + 喷嘴（在水面上，碗在可走带后沿以上）
    cx = 810
    rect(d, cx - 2, 124, cx + 2, RIM_TOP - 1, st)
    vl(d, cx - 2, 124, RIM_TOP - 1, st_hi)
    vl(d, cx + 2, 124, RIM_TOP - 1, st_sh)
    for y in (130, 138, 144):
        hl(d, cx - 3, cx + 3, y, st_hi)
        hl(d, cx - 3, cx + 3, y + 1, st_sh)
    for k in range(5):                                             # 石碗（上宽下窄）
        hw = 11 - k * 2
        hl(d, cx - hw, cx + hw, 119 + k, st_hi if k == 0 else (st if k < 3 else st_sh))
    hl(d, cx - 10, cx + 10, 120, WATER[1])
    rect(d, cx - 1, 114, cx + 1, 118, st_sh)
    px(d, cx - 1, 114, st_hi)
    # 前壁（八角：正面一块 + 两边斜面）
    for y in range(RIM_TOP, RIM_TOP + 8):
        k = y - RIM_TOP
        for x in range(a, b + 1):
            if x < a + 6:
                c = st_hi if k == 0 else lt(st, 0.08)                # 左斜面（受光）
            elif x > b - 6:
                c = st_hi if k == 0 else st_sh                       # 右斜面（背光）
            else:
                c = st_hi if k == 0 else st
            if k == 2:
                c = (64, 110, 170) if (x // 2) % 2 else (236, 236, 230)   # 一圈蓝白瓷砖
            elif k == 7:
                c = st_kk
            elif k > 2 and (x - a) % 8 == 0:
                c = dk(c, 0.86)
            px(d, x, y, c)
    for y in range(RIM_TOP + 1, RIM_TOP + 8):
        px(d, a + 6, y, st_sh)
        px(d, b - 6, y, dk(st_sh, 0.9))
    soft_shadow(im, a, b, RIM_TOP + 8, depth=1, slant=4)


def draw_road(im):
    x0, x1 = ROAD
    P.palm_trunk(im, 912, LANE - 1, 82, lean=-3, seed=9)
    d = ImageDraw.Draw(im)
    # 矮墙 + 铁栏杆（花园）
    rect(d, 920, 136, x1 - 1, LANE - 1, (226, 214, 190))
    hl(d, 920, x1 - 1, 136, (240, 232, 214))
    hl(d, 920, x1 - 1, LANE - 1, (180, 168, 146))
    for x in range(922, x1, 4):
        vl(d, x, 124, 135, IRON)
        px(d, x, 123, IRON_HI)
    hl(d, 920, x1 - 1, 126, IRON)
    for k in range(10):                                            # 栏杆后的灌木
        cx = 924 + k * 4
        for j in range(5):
            px(d, cx + j - 2, 133 - abs(j - 2) // 2 - (k % 2), (LEAF_D, LEAF, LEAF_M)[(k + j) % 3])
    # 路牌：蓝底、白色火车 + 箭头
    vl(d, 942, 106, LANE - 1, (120, 120, 126))
    vl(d, 943, 106, LANE - 1, (86, 86, 92))
    rect(d, 926, 103, 957, 114, (40, 86, 164), outline=(236, 236, 236))
    picto(im, PICTO_TRAIN, 929, 106)                               # 火车
    d = ImageDraw.Draw(im)
    hl(d, 943, 952, 109, (246, 246, 246))                           # 箭头
    px(d, 951, 108, (246, 246, 246))
    px(d, 951, 110, (246, 246, 246))
    px(d, 950, 107, (246, 246, 246))
    px(d, 950, 111, (246, 246, 246))
    soft_shadow(im, 920, x1 - 1, LANE, depth=1, slant=3)


def draw_poles(im):
    d = ImageDraw.Draw(im)
    tops = {248: 24, 484: 30, 638: 22, 904: 30}
    pins = {}
    for x in POLES:
        pins[x] = P.power_pole(d, x, tops[x], LANE - 1)
    for (xa, xb, sag) in ((248, 484, 9), (484, 638, 7), (638, 904, 10)):
        for k in (0, 3):
            pa, pb = pins[xa][k], pins[xb][k]
            V.wire(d, pa[0], pa[1], pb[0], pb[1], sag + k, (52, 46, 46))
    V.wire(d, 0, 50, pins[248][0][0], pins[248][0][1], 6, (52, 46, 46))
    V.wire(d, 30, 56, pins[248][1][0], pins[248][1][1], 5, (52, 46, 46))
    V.wire(d, pins[904][3][0], pins[904][3][1], PW - 1, 40, 4, (52, 46, 46))
    for x in POLES:
        soft_shadow(im, x - 1, x + 1, LANE, depth=1, slant=4)


PEOPLE = [  # (x, 脚 / 凳面 y, 样式, 朝向, seed, 身高, 地面 y, 衣服)：背景里的人（压灰）
    (257, 137, 'smoke', 1, 3, 27, LANE - 1, (236, 232, 222)),           # 茶馆门外抽水烟的老人
    (468, 138, 'shop', -1, 5, 27, LANE - 1, (90, 104, 140)),            # 布店门口坐着的店主
    (876, 141, 'sit', -1, 7, 27, LANE - 1, (214, 204, 180)),            # 清真寺门边台阶上坐着的人
]


def finish(im):
    """近景和贴在近景上的 strip 用同一套调色 + 可走带后面 y 106–145 压对比（不然 strip 框边上会有色差）。"""
    im = A._grade(im, sat=0.95, val=1.0)
    P.compress_band(im, 106, LANE, (200, 182, 152), amt=0.14, ramp=10)
    return im


@lru_cache(maxsize=1)
def near_img():
    im = A._new(PW, H)
    draw_ground(im)
    draw_h0(im)
    draw_gate(im)
    draw_h1(im)
    draw_stall(im)
    draw_h2(im)
    draw_teahouse(im)
    draw_cloth_shop(im)
    draw_stop(im)
    draw_h5(im)
    draw_h6(im)
    draw_alley(im)
    draw_h7(im)
    draw_mosque(im)
    draw_road(im)
    P.palm_trunk(im, 758, LANE - 1, 70, lean=4, seed=11)
    im = P.outer_rim(im, INK, y1=LANE)
    draw_crates(im)
    draw_poles(im)
    lay = P.people_layer((PW, H), PEOPLE, sat=0.7, amt=0.26, col=(214, 200, 178))
    im.alpha_composite(lay)
    ground_shade(im)
    draw_heap(im)
    draw_tea_table(im)
    draw_fountain(im)
    im = finish(im)
    return opaque(im)


# ============================================================ strip（动的东西：都画在世界坐标的透明整张上）
PALMS = [(58 + 3, 66, 18, 0), (912 - 3, 63, 19, 1), (758 + 4, 75, 17, 2)]   # (树冠中心 x, y, R, seed)


def palms_raw(f):
    im = A._new(PW, H)
    for (cx, cy, R, sd) in PALMS:
        P.palm_crown(im, cx, cy, R, seed=sd, f=f, n=N)
    return finish(im)


VALANCES = [(STALL[0] - 3, STALL[1] + 2, 104, (232, 118, 48), (246, 238, 216), 0.0),
            (CLOTH_SHOP[0] - 4, CLOTH_SHOP[1] + 3, 103, (52, 104, 170), (240, 240, 232), 1.3)]


def valance_raw(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for (a, b, y, c1, c2, sd) in VALANCES:
        P.valance(d, a, b, y, c1, c2, f, stripe=4, n=N, seed=sd)
    return finish(im)


CLOTH_PIECES = [(384, 11, 30, 0), (398, 10, 26, 2), (411, 12, 33, 4), (426, 10, 28, 1), (439, 11, 31, 6),
                (453, 12, 27, 3)]           # (左 x, 宽, 长, 花样 / CLOTH 色号)


def cloths_raw(f):
    """六块挂布：顶边钉在横杆上，越往下被风吹得越往右摆（各自的相位），下沿的穗子跟着抖。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    ph0 = math.tau * f / N
    for i, (x0, w, L, kind) in enumerate(CLOTH_PIECES):
        col = P.CLOTH[(kind * 3 + i) % len(P.CLOTH)]
        col2 = P.CLOTH[(kind * 3 + i + 4) % len(P.CLOTH)]
        hi, sh = lt(col, 0.22), dk(col, 0.72)
        for r in range(L):
            u = r / float(L - 1)
            sway = 2.2 * math.sin(ph0 + i * 1.3) * u ** 1.6 + 0.8 * u
            belly = 0.8 * math.sin(ph0 * 2 + i) * math.sin(math.pi * u)
            xs = x0 + int(round(sway + belly))
            yy = CLOTH_RAIL + 1 + r
            for k in range(w):
                c = col
                if kind % 3 == 0 and (r // 4) % 2 == 1:
                    c = col2                                       # 横条纹
                elif kind % 3 == 1 and (k + r) % 6 == 0:
                    c = col2                                       # 斜点花
                elif kind % 3 == 2 and (k in (1, w - 2) or r in (2, L - 3)):
                    c = col2                                       # 镶边
                if k == 0:
                    c = lt(c, 0.2)
                elif k == w - 1:
                    c = dk(c, 0.7)
                elif (k + int(round(belly * 2))) % 4 == 3:
                    c = dk(c, 0.88)                                # 竖褶
                px(d, xs + k, yy, c)
        yb = CLOTH_RAIL + 1 + L                                    # 穗子
        xs = x0 + int(round(2.2 * math.sin(ph0 + i * 1.3) + 0.8))
        for k in range(0, w, 2):
            ln = 1 + int((f + k + i) % 3 == 0)
            for q in range(ln):
                px(d, xs + k, yb + q, sh)
        hl(d, x0, x0 + w - 1, CLOTH_RAIL + 1, hi)
    return finish(im)


# (底 x, 底 y, 高, seed)：茶炊烟囱口（右拱洞里 x 18、柜台面往上 22）、老人嘴边
STEAMS = [(TEA_ARCH_R[0] + 18, TEA_SPRING - TEA_RISE + (LANE - 1 - (TEA_SPRING - TEA_RISE) + 1 - 17) - 23, 7, 0),
          (259, 120, 10, 1)]


def steam_raw(f):
    """茶炊的热气、老人吐的水烟：一缕缕往上飘、往右散的白点（硬边，按 Bayer 抖开浓淡）。"""
    im = A._new(PW, H)
    a = np.zeros((H, PW, 4), np.float32)
    for (x0, y0, hgt, sd) in STEAMS:
        for j in range(3):
            for k in range(hgt):
                u = k / float(hgt)
                ph = (f / float(N) + j / 3.0 + u * 0.6) % 1.0
                x = x0 + int(round(math.sin(math.tau * (u * 1.2 + f / float(N) + j * 0.33 + sd)) * (1 + u * 2) + u * 3))
                y = y0 - k
                al = (1.0 - u) * (0.55 + 0.45 * math.sin(math.tau * ph))
                if 0 <= y < H:
                    a[y, x, :3] = (246, 244, 238)
                    a[y, x, 3] = max(a[y, x, 3], al * 255)
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    return finish(P.hard_alpha(im))


def trough_raw(f):
    """水槽水面上的两三点反光，跟着龙头滴下来的水一圈圈动。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for i in range(5):
        x = 572 + ((i * 6 + f * 2) % 27)
        px(d, x, 137, WATER[0] if (i + f) % 2 else WATER[1])
    k = f % 4                                                      # 龙头滴下的水
    px(d, 588, 129 + k * 2, WATER[1])
    if k == 3:
        px(d, 587, 137, WATER[0])
        px(d, 589, 137, WATER[0])
    return finish(im)


LINES = [(ALLEY[0] + 1, 80, ALLEY[1] - 2, 82, 2), (ALLEY[0] + 1, 94, ALLEY[1] - 2, 95, 2)]


def laundry_raw(f):
    """窄巷头顶两根晾衣绳：一件衬衫、一条毛巾、一条小孩裤子……下摆被巷子里的穿堂风吹得摆。（巷子在影子里，压暗。）"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    items = [((214, 214, 206), 6, 7), ((200, 70, 70), 4, 9), ((70, 110, 170), 5, 6), ((230, 200, 80), 4, 8),
             ((150, 170, 150), 6, 7)]
    for li, (x0, y0, x1, y1, sag) in enumerate(LINES):
        pts = V.garland_pts(x0, y0, x1, y1, sag)
        d.line([(round(x), round(y)) for (x, y) in pts], fill=C((90, 86, 84)))
        n = 3 if li == 0 else 2
        for j in range(n):
            col, w, L = items[(li * 3 + j) % len(items)]
            xa = x0 + 3 + j * ((x1 - x0 - 6) // n)
            ya = int(round(pts[min(len(pts) - 1, xa - x0)][1])) + 1
            sw = math.sin(math.tau * f / N + j * 1.7 + li)
            for r in range(L):
                dx = int(round(sw * 1.2 * (r / float(L))))
                for k in range(w):
                    c = col if k > 0 else lt(col, 0.2)
                    if k == w - 1:
                        c = dk(col, 0.75)
                    px(d, xa + k + dx, ya + r, c)
            px(d, xa, ya - 1, (200, 190, 170))
            px(d, xa + w - 1, ya - 1, (200, 190, 170))
    im = finish(im)
    a = np.array(im).astype(np.float32)
    m = a[..., 3] > 0
    a[m, :3] *= SHADOW_MUL
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')


def flag_raw(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    P.egypt_flag(d, 746, 28, f, n=N, L=11, hgt=6)
    return finish(im)


def fountain_raw(f):
    """喷泉：顶上喷嘴冒的水（一小簇往上再落回碗里）、碗沿往池里淌的水线（水珠往下走）、池面的一圈圈涟漪。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    cx = 810
    for k in range(5):                                             # 顶上的一簇
        h = 3 + (k * 2 + f) % 4
        x = cx - 2 + k
        for j in range(h):
            px(d, x, 113 - j, WATER[0] if j == h - 1 else WATER[1])
    for side in (-1, 1):                                           # 碗沿两边往下淌
        xs = cx + side * 11
        for y in range(121, RIM_TOP - 1):
            ph = (y + f * 3 + (0 if side < 0 else 4)) % 7
            if ph < 4:
                px(d, xs + (side if y > 132 else 0), y, WATER[0] if ph == 0 else WATER[1])
        for k in range(3):
            px(d, xs + side * k, RIM_TOP - 2, WATER[0] if (k + f) % 2 else WATER[2])
    for k in range(3):                                             # 碗里的水溅出来的亮点
        px(d, cx - 8 + ((k * 7 + f * 3) % 17), 119, WATER[0])
    for i in range(10):                                            # 池面的涟漪
        x = FOUNT[0] + 3 + ((i * 5 + f * 2) % (FOUNT[1] - FOUNT[0] - 6))
        y = LANE + 2 + (i % 2)
        px(d, x, y, WATER[0] if (i + f) % 3 else WATER[1])
        px(d, x + 1, y, WATER[1])
    return finish(im)


PIGEONS = [(770, 151, 0), (777, 149, 3), (790, RIM_TOP - 1, 5), (842, 150, 2), (851, 153, 6)]   # (x, 脚 y, 相位)


def pigeons_raw(f):
    """五只鸽子：啄食（低头 / 抬头）、走一两步、偶尔扑一下翅膀；池沿上那只在喝水。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for i, (x, y, ph) in enumerate(PIGEONS):
        k = (f + ph) % N
        pose = (0, 1, 1, 0, 2, 0, 1, 3)[k] if i != 1 else (3, 3, 0, 1, 0, 2, 0, 1)[k]
        dx = (0, 0, 1, 1, 1, 1, 0, 0)[k] if i in (0, 3) else 0
        col = PIGEON_C if i % 2 == 0 else (150, 146, 150)
        P.pigeon(d, x + dx, y, pose, col=col)
    return finish(im)


_cached = P.cached_frames


palms_frame = _cached(palms_raw)
valance_frame = _cached(valance_raw)
cloths_frame = _cached(cloths_raw)
steam_frame = _cached(steam_raw)
trough_frame = _cached(trough_raw)
laundry_frame = _cached(laundry_raw)
flag_frame = _cached(flag_raw)
fountain_frame = _cached(fountain_raw)
pigeons_frame = _cached(pigeons_raw)


def _boxes_of(fn, groups):
    """一个帧函数画的几处东西各自一个框：groups = [(x0, x1)]（世界 x 范围），框 = 这一段里 n 帧画到的外接框。"""
    out = []
    for (xa, xb) in groups:
        out.append(P.auto_box(fn, N, FPS, limit=(xa, 0, xb, H)))
    return out


@lru_cache(maxsize=1)
def strips():
    """(name, box, fn) 列表（k 1）。框都从画出来的东西算（auto_box），改动画不用手调框。"""
    out = []
    for i, bx in enumerate(_boxes_of(palms_frame, [(30, 96), (880, 945), (730, 800)])):
        out.append(('palm_%d' % i, bx, palms_frame))
    for i, bx in enumerate(_boxes_of(valance_frame, [(STALL[0] - 6, STALL[1] + 6), (CLOTH_SHOP[0] - 8, CLOTH_SHOP[1] + 8)])):
        out.append(('valance_%d' % i, bx, valance_frame))
    out.append(('cloths', P.auto_box(cloths_frame, N, FPS), cloths_frame))
    for i, bx in enumerate(_boxes_of(steam_frame, [(300, 360), (250, 290)])):
        out.append(('steam_%d' % i, bx, steam_frame))
    out.append(('trough', P.auto_box(trough_frame, N, FPS), trough_frame))
    out.append(('laundry', P.auto_box(laundry_frame, N, FPS), laundry_frame))
    out.append(('flag', P.auto_box(flag_frame, N, FPS), flag_frame))
    out.append(('fountain', P.auto_box(fountain_frame, N, FPS), fountain_frame))
    out.append(('pigeons', P.auto_box(pigeons_frame, N, FPS), pigeons_frame))
    return out


@lru_cache(maxsize=1)
def table():
    """图层表（从后往前），compose / export 共用。"""
    tb = [('static', 'sky', sky_img(), 0, 0),
          ('wrap', 'clouds', clouds_img(), CLOUD_P, CLOUD_K, 4, CLOUD_VX)]
    fim, fy = P.crop_pano(far_img())
    tb.append(('pano', 'far', fim, FAR_K, 0, fy))
    sp = _cached(sparkle_frame_raw)
    tb.append(('strip', 'sparkle', P.auto_box(sp, N, FPS), N, FPS, sp, FAR_K))
    boats = felucca_imgs()
    tb.append(('clouds', 'felucca', BOAT_SPAN,
               [('felucca%d' % i, boats[i], x0, y, vx, FAR_K) for i, (x0, y, vx) in enumerate(BOATS)]))
    mim, my = P.crop_pano(mid_img())
    tb.append(('pano', 'mid', mim, MID_K, 0, my))
    bird = birds_img()
    tb.append(('clouds', 'birds', 460, [('bird%d' % i, bird, x0, y, vx, k) for i, (y, vx, k, x0) in enumerate(BIRDS)]))
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
        tea_seats=[[sx, TABLE_BASE] for (sx, face) in SEATS],
        tea_top=TABLE_TOP,
        orange_heap=[HEAP[0] - 2, 149, HEAP[1] + 6, 161],
        tea_box=[SEATS[0][0] - 8, TABLE_BASE - 15, SEATS[1][0] + 11, TABLE_BASE + 3],
        fountain_box=[FOUNT[0] - 2, LANE, FOUNT[1] + 6, RIM_TOP + 9],
        fountain_rim=RIM_TOP,
        pigeons=[[x, y] for (x, y, ph) in PIGEONS],
        trough=[584, 138], hitch=[606, 128],
        crates_box=[708, 125, 735, LANE + 2],
        alley_box=[ALLEY[0], 42, ALLEY[1], LANE],
        mosque_door=[854, LANE - 1],
        lane_back=LANE)
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
    anc = st['anchors']
    cfg = dict(title='阿斯旺', PW=PW, walk=WALK, near=near_img(), opaque_rows=(LANE, H), sky=sky_img(),
               states=[{}], stand=STAND, required=REQUIRED, size_limit=350 * 1024, cams_step=40,
               flat=(0, PW, WALK[0], WALK[1] + 1, 22, 0.012),
               flat_skip=[tuple(anc['orange_heap']), tuple(anc['tea_box']), tuple(anc['fountain_box'])])
    P.common_checks(ex, BJ, st, tb, cfg)
    # 剧情摆马车 + 马的那一段（x 500–640）近景可走带里只有路面（没有高出地面的东西）
    a = np.array(near_img()).astype(np.float32)
    lum = P._lum(a[..., :3])
    seg = lum[WALK[0]:WALK[1] + 1, 500:640]
    med = np.median(seg)
    ex.checked('马车停靠段 x 500–640 可走带只有路面（和中位亮度差 > 24 的像素）', int((np.abs(seg - med) > 24).sum()))
    # 茶桌桌面在 anchors.tea 那一行（道具放上去不会悬空 / 陷进桌子）
    tx, ty = anc['tea']
    ex.checked('anchors.tea (%d,%d) 正好在桌面上（桌面 y %d–%d）' % (tx, ty, TABLE_TOP, TABLE_TOP + 2),
               0 if TABLE_TOP <= ty <= TABLE_TOP + 2 else 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch8', 'after')
    os.makedirs(od, exist_ok=True)
    full = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    for cx in (0, 320, 640):
        full.paste(compose(cx, 0.5), (cx, 0))
    full.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'aswan_town_solo.png'))
    print('ok')
