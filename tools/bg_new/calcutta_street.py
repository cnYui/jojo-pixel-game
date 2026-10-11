# -*- coding: utf-8 -*-
r"""calcutta_street —— 第4章「加尔各答」：1980 年代末的加尔各答街头（人山人海、热闹、旧），热带强阳光、灰黄的霾天。
2026-10-11 ch4 按体验版精度重画（改前是 later_stages 里借 city_street('varanasi') 拼的一排重复平涂楼）。

地图 1280 宽、ground 154、可走带 y 148–176（= 马路：补过的旧沥青 + 两根电车轨 y 163 / 171）；侧视平视，太阳在左上（影子往右下）。
竖向：楼脚 = 人行道后沿 y 138；人行道 138–145（旧石板）；路缘石 146 顶 / 147 侧；摊子、车、路人都在 y ≤ 147（可走带后面）。
从左到右（世界坐标）：
  x 0–142     火车站（红砖站房一角）：奶油石线脚、垛口女儿墙、钟楼（钟、四坡石板瓦顶）、二层成对细拱窗、站名牌（色块）+ 火车头徽章；
              大拱门（中线 58、半径 28、拱顶 y 64，红白相间拱石）里：钢屋架、发车牌、挂钟、停着的褐红车厢、尽头站台的亮口、
              往外走的人潮剪影（anchors.arrive）；右边两个小拱门、左边售票窗；门口红衣搬运工头顶行李
  x 142–196   一道刷石灰的矮墙（墙后空着，看得见中景）+ 压水井 + 铁桶 + 一摊湿印；老榕树（x 170）：粗干、板根、气根、大树冠
  x 196–300   A 赭黄三层：彩色玻璃扇形气窗的拱窗、铸铁阳台（搭着晾的纱丽 strip）、宝瓶栏杆女儿墙；一楼香料铺；
              门口香料摊（x 204–296：竹竿 + 遮阳布 strip、矮木台上 8 盘尖尖的香料粉、4 只卷口麻袋、一杆秤）（anchors.spice / spice_vendor）
  x 300–332   窄楼（陶土红）：封闭木阳台、卷闸门 + 铁皮雨棚
  x 332–424   B 青蓝三层：甜食铺（玻璃柜、日光灯）；门口茶摊（x 338–380：蓝漆柜台、陶土炉 + 大铝壶（蒸汽 strip）、陶杯塔、饼干罐、
              老板）+ 长凳上三个喝茶的人 + 蓝塑料布（strip）（anchors.chai）
  x 424–604   C 奶白大楼：通高壁柱、三角窗楣、通长铸铁阳台；一楼柱廊（9 根圆柱，廊子里深影：纱丽、照相馆、药房、卷闸门、裁缝、杂货）；
              楼顶手绘电影广告牌（x 444–586，y 8–39：大背头小胡子男主角、点红点的女主角、持枪反派、火光、色块标题，晒褪色、卷角）
              —— 第 7 战段 2 的背景：x 440–720 的可走带上只有路面纹理（自检），廊子压了对比；anchors.cow 是剧情放牛的位置，背景不画牛
  x 604–722   D 鲑鱼粉三层：两座木头封闭阳台、中间一扇窗挂着晾衣（strip）、三角山花；一楼铜器铺 + 楼梯门；门口停着黄色 Ambassador
              出租车（x 602–680，车头朝左：镀铬保险杠 / 腰线、圆大灯、车顶白灯箱、机械计价器的红旗子、包橙色头巾的司机）（anchors.taxi）
  x 722–812   E 薄荷绿两层 + 屋顶铁皮棚：修车铺（挂着的轮胎、自行车）；门口人力车（x 722–800：大木轮、黑漆车厢、红坐垫、
              撑开的黑折叠篷、两根车把落地，车夫坐在车把上歇着，手里一只小铜铃）（anchors.rickshaw）
  x 812–852   窄楼（淡黄）+ 楼梯门；x 862 电车站牌（挂在架空线杆上：白底红边、蓝色电车小图）+ 等车的人
  x 852–946   一层老货栈（陶瓦檐、剥落的石灰墙、半开的大木门）；路边小神龛（x 884–916：白台子、红边龛身、橙红神像、花环、
              弧形小尖塔 + 宝瓶 + 小旗（strip）、铜铃、油灯 + 一根香（strip））（anchors.shrine）；菩提树（x 930，树下白砖台、红白线）
  x 946–1054  F 灰蓝三层：混凝土遮阳板（chajja）、铁阳台；一楼银行铁栅门 + 杂货铺；门口水果推车（x 986–1030：红黄条大伞、香蕉、
              芒果、青椰子、木瓜、番石榴、荔枝）；楼顶：楼梯间 + 铁腿水箱 + 天线，女儿墙顶 y 41 —— roof_hh=1 时 x 1012 蹲着牛仔帽人影
  x 1054–1172 G 剥落的老宅：大片露砖、霉斑道子、墙缝里的小菩提、坏掉的百叶、彩色气窗、山花；铁阳台上晾着纱丽（strip）；
              一楼卷闸门 + 楼梯门；门口槟榔摊（x 1080–1110，木箱子里盘腿坐着卖槟榔的）、躺着一头戴花环的白瘤牛（x 1116–1150）；
              x 1150 带变压器的电线杆，乱线从这里拉向两边
  x 1172–1232 巷口（第 7 战那条巷子）：两边侧墙往消失点 (1202, 102) 收 —— 左墙背光、右墙上半截一道斜阳；湿石板地 + 明沟 + 水洼；
              尽头一面被照亮的墙 + 小门，再往上是巷子尽头那栋楼（巷子封闭、深）；三道晾衣绳（衣服 strip）、吊灯泡、水管、电表箱；
              巷口地上淌出来一摊水（anchors.alley_mouth）
  x 1232–1280 H 淡紫灰：宝瓶栏杆、铁阳台、卷闸门（出图）
街上：电车架空线（接触线 y 21 一直拉过去 + 下垂的承力索 + 吊弦；杆在 x 132 / 432 / 700 / 862）；楼和杆之间乱拉的电线（WIRES，
    上面停着鸽子 / 乌鸦 strip）；人行道上 30 来个路人（比主角矮一圈、颜色压灰：长衫、衬衫、背心围裤、纱丽、红衣搬运工、
    撑黑伞的老人、头顶筐的妇女、小孩、合掌的妇女、长凳上喝茶的）；几扇开着的窗里探出头的住户。
光：太阳在左上；檐口 / 阳台 / 窗楣的影落在下方偏右，窗洞上沿 / 左沿暗；铺子里上暗下亮。可走带后面（y 96–147）往中间色收了 18 % 对比。

巷子配色（india_alley 照这个，和巷口是同一条巷子）：墙 ALLEY_WALL (138,126,98) / 阴影 ALLEY_SH (104,96,78) / 深 ALLEY_DK (72,68,58)、
    地 ALLEY_FLOOR (92,86,74)、水洼 ALLEY_PUDDLE (128,138,142)（高光 (168,176,178)）、尽头被照亮的墙 (172,158,120)、
    晾衣绳 (40,38,40)、衣服 (200,60,80) / (240,236,226) / (60,120,170) / (230,170,50) / (120,80,150)（压暗 0.82）。

图层（从后往前）：
  sky        static              灰黄的热天（上灰蓝、往下发黄）+ 左上发白的太阳
  clouds     wrap  k .08 vx .9   霾里的扁云 + 长长的薄层云（640 循环）
  rain_sky   wrap  k .05 vx 4    key 'rain'（真值就画）：铅灰的层积云，整片不透明，盖住晴天
  clear_sky  image screen        key 'sunbeam'：雨后的湿灰云，左上裂开一道口子透出太阳 + 光柱
  far        pano  k .22         豪拉大桥、邮政总局圆顶、高等法院塔、纪念柱、维多利亚纪念堂、高压电线塔、圣保罗教堂塔、80 年代高楼、烟囱
  (flock)    clouds              远处的两小群鸽子 / 乌鸦
  mid        pano  k .5          屋顶一线：水箱、鱼骨天线、鸽子笼、晾衣绳、神庙尖顶、清真寺、高架水塔、椰子树、榕树冠、广告牌铁架背面
  near       pano  k 1           整条街（1280）
  wet        image k 1 y 138     key 'rain'：湿地面（近景 y 138–179 变暗变冷 + 店面 / 车 / 人的倒影 + 积水 + 发亮的钢轨 / 路缘）
  wet        image k 1 y 138     key 'sunbeam'：同一张（雨停了地还是湿的）
  laundry_a / laundry_d / laundry_g  strip k 1  8 帧 @4 fps  晾的衣服飘（A 阳台、D 两个木阳台之间、G 阳台 + 巷子里三道绳）
  tarps      strip k 1  8 帧 @4 fps  香料摊 / 茶摊的遮阳布下沿起伏
  birds_a / birds_b / birds_c        strip k 1  8 帧 @4 fps  电线上的鸟转头、理毛、乌鸦张嘴、偶尔扑翅膀
  steam      strip k 1  8 帧 @6 fps  茶壶的蒸汽
  shrine     strip k 1  8 帧 @8 fps  油灯火苗、香的烟、塔尖小旗
  roof_hh    pick  k 1  key 'roof_hh' values [0, 1]：0 = 空（透明）、1 = F 楼顶女儿墙后面蹲着的牛仔帽人影（17×12 框，人影 10 px 高）
  tint       key 'rain'     #36445a α .40 × rain（JS：数字 = α 乘数；ref_render 真值就画满）
  tint       key 'sunbeam'  #4a5568 α .24
  beam       image k 1 x 380  key 'sunbeam'：从左上斜照下来的一道暖光，落在 x 540–640 的路面上一片亮斑 + 几粒浮尘
  splash     strip screen 8 帧 @12 fps  key 'rain'：地上的雨点（小皇冠 → 涟漪）
  fg: fg     pick  k 1.3 key 'rain' values [0, 1]：两根近处的电车线杆（前景世界 x 300 / 1340：镜头 0–235、790–960 看得见，
                           战斗镜头看不见）；1 = 同一张预先罩了雨天色
  fg: rain   strip screen 10 帧 @15 fps key 'rain'：整屏斜着落的雨丝（在人物前面）
状态用法：S.state('rain', 1) 下雨（数字 0–1 只调暗色的深浅；> 0 时雨丝 / 湿地 / 雨云都出来）；雨停那一刻 S.state('rain', 0) +
    S.state('sunbeam', 1)（地还湿、云裂开、一道光照下来）；S.state('roof_hh', 1) 楼顶出现牛仔帽人影，0 收回。
单独运行：python -B tools\bg_new\calcutta_street.py → tools\bg_new\_preview\ch4\calcutta_dev\solo_*.png
"""
import sys
sys.dont_write_bytecode = True

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

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 1280                     # 地图宽
GROUND = 154
WALK = (148, 176)             # 可走纵深带（脚底 y）
CLOUD_K, CLOUD_VX = 0.08, 0.9
RAINSKY_K, RAINSKY_VX = 0.05, 4.0
FAR_K, MID_K, FG_K = 0.22, 0.5, 1.3
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 532
MIDW = W + int(math.ceil((PW - W) * MID_K))      # 800
# 竖向（近景）
BASE_Y = 138                  # 楼脚 = 人行道后沿（楼画到 137）
FOOT_Y = 138                  # 人行道面 138–145
KERB_Y = 146                  # 路缘石顶（亮）/ 147 侧面（暗）
STREET_Y = 148                # 马路（= 可走带）从这一行开始
RAILS = (163, 171)            # 电车轨道两根轨的轨头（下一行是暗槽）
WIRE_Y = 21                   # 电车架空接触线

# 各段的 x 范围（右边不含）
STATION = (0, 142)            # 火车站（红砖站房一角 + 大拱门出口 + 钟楼）
BANYAN_X = 170                # 老榕树（树干 x）
B_SPICE = (196, 300)          # A 赭黄三层：香料铺 + 门口香料摊
B_NARROW = (300, 332)         # 窄楼（陶土红，木阳台，卷闸门）
B_CHAI = (332, 424)           # B 青蓝三层：甜食铺 + 门口茶摊
B_GRAND = (424, 604)          # C 奶白大楼：柱廊 + 楼顶手绘电影广告牌（战斗段的背景，对比压低）
B_PINK = (604, 722)           # D 鲑鱼粉：铜器铺 + 门口出租车
B_GREEN = (722, 812)          # E 薄荷绿两层 + 铁皮屋顶棚：修车铺 + 门口人力车
B_SLIM = (812, 852)           # 窄楼（淡黄）+ 电车站牌
COMPOUND = (852, 946)         # 一层老货栈（瓦檐）+ 小神龛 + 菩提树
B_TALL = (946, 1054)          # F 灰蓝三层：楼顶平台（荷尔·荷斯在这里偷看）
B_OLD = (1054, 1172)          # G 剥落的老宅：槟榔摊、躺着的牛
ALLEY = (1172, 1232)          # 巷口
B_EDGE = (1232, 1280)         # H 淡紫灰（右边出图）

SPICE_STALL = (204, 296)      # 香料摊（台面 + 一圈香料堆 + 麻袋）
CHAI_STALL = (338, 380)       # 茶摊（炉子 + 水壶 + 陶杯）
BENCH = (384, 418)            # 茶摊的长凳
TAXI = (602, 680)             # 黄色 Ambassador 出租车（车头朝左）
RICKSHAW = (722, 800)         # 人力车（车把朝左落地）
SHRINE = (884, 916)           # 路边小神龛
TRAM_STOP_X = 862             # 电车站牌杆
PEEPAL_X = 930                # 菩提树树干
HH = (1012, 41)               # 荷尔·荷斯（蹲在 F 楼顶女儿墙后面）：x 中线、女儿墙顶 y（人影画在 y 31–40）
POLES = (166, 432, 736, 862, 1150)   # 电车架空线的杆（862 兼电车站牌；1150 是带变压器的电线杆）
PAAN = (1080, 1110)           # 槟榔摊（木箱子）
FRUIT = (986, 1030)           # 水果推车（F 楼门口）
COW_BG = (1116, 1150)         # 背景里躺着的牛（不在 x 500）

N_ANIM, FPS_ANIM = 8, 4.0
N_STEAM, FPS_STEAM = 8, 6.0
N_FLAME, FPS_FLAME = 4, 8.0
N_RAIN, FPS_RAIN = 10, 15.0
N_SPLASH, FPS_SPLASH = 8, 12.0
C = A._c4

ANCHORS = dict(
    arrive=[70, 164],          # 一行人从车站拱门出来
    spice=[250, 160],          # 香料摊前（调查点）
    spice_vendor=[270, 154],   # 香料小贩站的位置
    chai=[370, 160],           # 茶摊 / 路边人群前
    cow=[500, 166],            # 圣牛（剧情放精灵；背景这里不画牛）
    taxi=[640, 152],           # 出租车旁
    rickshaw=[760, 152],       # 人力车旁
    shrine=[900, 150],         # 小神龛 / 电车站前
    roof=[HH[0], HH[1] - 5],   # 楼顶的牛仔帽人影（roof_hh=1 时；人影 y 34–44 的中间）
    alley_mouth=[1202, 152],   # 巷口
    walk_x=[10, 1270],
)

# ============================================================ 调色
INK = (36, 30, 34)
SKY_STOPS = [(166, 178, 188), (186, 192, 194), (206, 205, 192), (222, 213, 186), (232, 220, 188)]
HAZE = (216, 209, 190)
FOOT = (178, 170, 154)
FOOT_S = (164, 156, 141)
FOOT_HI = (188, 181, 166)
KERB_HI = (204, 198, 184)
KERB_F = (128, 121, 110)
STREET = (152, 142, 126)
STREET_S = (141, 131, 116)
STREET_HI = (161, 152, 136)
RAIL_HI = (176, 170, 160)
RAIL_D = (122, 115, 106)
BRICK = (164, 88, 64)
BRICK_D = (132, 66, 50)
BRICK_HI = (184, 110, 82)
MORTAR = (178, 152, 130)
SHUT = (60, 108, 84)          # 百叶窗（绿）
WOOD = (122, 84, 56)
WOOD_D = (92, 62, 42)
WOOD_HI = (152, 110, 74)
IRON = (42, 46, 46)
IRON_HI = (86, 94, 92)
DARK_IN = (58, 50, 52)        # 窗洞里（屋里暗）
LEAF_D = (40, 78, 44)
LEAF = (60, 110, 56)
LEAF_M = (88, 138, 70)
LEAF_HI = (132, 172, 92)
BARK = (112, 98, 82)
BARK_D = (78, 68, 58)
BARK_HI = (146, 132, 112)
SKIN = ((132, 92, 66), (116, 80, 58), (150, 106, 78), (102, 70, 52))
HAIR = (34, 30, 32)
TAXI_Y = (236, 188, 42)
SHADOW_MUL = np.array((0.74, 0.76, 0.86), np.float32)
SOFT_MUL = np.array((0.84, 0.85, 0.92), np.float32)
# 下雨：tint 颜色 / alpha（JS 里 alpha × rain）
RAIN_TINT = ('#36445a', 0.40)
SUN_TINT = ('#4a5568', 0.24)  # 雨停（sunbeam）：整体还是阴一点，只有那道光亮
# 巷子（和 india_alley 同一条：深灰黄灰泥、晾衣绳、水洼）
ALLEY_WALL = (138, 126, 98)
ALLEY_SH = (104, 96, 78)
ALLEY_DK = (72, 68, 58)
ALLEY_FLOOR = (92, 86, 74)
ALLEY_PUDDLE = (128, 138, 142)


# ============================================================ 小工具
def dk(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


def lt(c, k):
    return mix(c, (255, 255, 255), k)


def hl(d, x0, x1, y, c):
    if x1 >= x0:
        d.line((x0, y, x1, y), fill=C(c))


def vl(d, x, y0, y1, c):
    if y1 >= y0:
        d.line((x, y0, x, y1), fill=C(c))


def px(d, x, y, c):
    d.point((x, y), fill=C(c))


def rect(d, x0, y0, x1, y1, c, outline=None):
    if x1 >= x0 and y1 >= y0:
        d.rectangle((x0, y0, x1, y1), fill=C(c) if c is not None else None, outline=C(outline) if outline else None)


def mul_box(im, box, mul, level=1.0):
    """box（右下含）里不透明的像素乘 mul；level < 1 时按 Bayer 只压一部分。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(im.width - 1, x1), min(im.height - 1, y1)
    if x1 < x0 or y1 < y0:
        return
    a = np.array(im.crop((x0, y0, x1 + 1, y1 + 1))).astype(np.float32)
    m = a[..., 3] > 0
    if level < 1.0:
        m &= A._bayer(im.width, im.height)[y0:y1 + 1, x0:x1 + 1] < level
    a[m, :3] *= np.asarray(mul, np.float32)
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'), (x0, y0))


def mul_mask(im, mask, mul, level=1.0):
    a = np.array(im).astype(np.float32)
    m = mask & (a[..., 3] > 0)
    if level < 1.0:
        m &= A._bayer(im.width, im.height) < level
    a[m, :3] *= np.asarray(mul, np.float32)
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def poly_mask(size, pts):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m) > 0


def cast_shadow(im, pts, level=1.0, mul=SHADOW_MUL):
    mul_mask(im, poly_mask(im.size, pts), mul, level)


def mottle(im, box, base, dark, light, seed, cell=4, lo=0.3, hi=0.7):
    """斑驳：box 里颜色正好是 base 的像素，按 fbm 噪声换成 dark / light（边缘 Bayer 抖动）。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(im.width - 1, x1), min(im.height - 1, y1)
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if w <= 0 or h <= 0:
        return
    a = np.array(im)
    sub = a[y0:y1 + 1, x0:x1 + 1]
    is_base = (sub[..., 0] == base[0]) & (sub[..., 1] == base[1]) & (sub[..., 2] == base[2]) & (sub[..., 3] > 0)
    n = A._fbm(w + 8, h + 8, cell, seed=seed % 997)[4:4 + h, 4:4 + w]
    bay = A._bayer(x1 + 1, y1 + 1)[y0:y1 + 1, x0:x1 + 1]
    dm = is_base & ((n > hi + 0.05) | ((n > hi) & (bay < 0.5)))
    lm = is_base & ((n < lo - 0.05) | ((n < lo) & (bay < 0.5)))
    sub[dm, :3] = dark
    sub[lm, :3] = light
    a[y0:y1 + 1, x0:x1 + 1] = sub
    im.paste(Image.fromarray(a, 'RGBA'))


def stain(im, x, y0, length, seed, width=1, k=0.8, ymax=None):
    """霉斑水渍（加尔各答雨季留下的黑道子）：从 (x, y0) 往下淌，越往下越稀；乘暗已经画好的墙。"""
    a = np.array(im).astype(np.float32)
    ymax = H - 1 if ymax is None else ymax
    xx = x
    for yy in range(y0, min(ymax + 1, y0 + length)):
        u = (yy - y0) / max(1, length)
        if hash01(seed, yy, 3) < 0.12:
            xx += 1 if hash01(seed, yy, 4) < 0.5 else -1
            xx = max(x - 1, min(x + 1, xx))
        for j in range(width):
            p = 1.0 - u * 0.85 - j * 0.25
            if hash01(seed, yy, j, 5) < p and 0 <= xx + j < im.width and a[yy, xx + j, 3] > 0:
                a[yy, xx + j, :3] *= k + (1 - k) * u * 0.6
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def grime(im, x0, x1, y1, h=10, k=0.82):
    """墙脚溅上去的泥灰：从 y1 往上 h 行，越往下越暗（Bayer）。"""
    for i in range(h):
        y = y1 - i
        lev = 1.0 - i / h
        mul_box(im, (x0, y, x1, y), (k + 0.04, k + 0.02, k), level=lev)


def _tile(im, w):
    out = A._new(w, im.height)
    for x in range(0, w, im.width):
        out.paste(im, (x, 0))
    return out


def _canopy(d, cx, cy, rx, ry, seed, pal=(LEAF_D, LEAF, LEAF_M, LEAF_HI)):
    """树冠：一堆椭圆疙瘩，左上亮、右下暗、底下一圈深色。"""
    blobs = []
    n = max(5, int(rx * ry / 40))
    for i in range(n):
        ang = hrange(0, math.tau, seed, i, 1)
        r = hrange(0.1, 0.85, seed, i, 2)
        bx = cx + math.cos(ang) * rx * r
        by = cy + math.sin(ang) * ry * r * 0.8
        br = hrange(0.28, 0.45, seed, i, 3) * min(rx, ry * 1.6)
        blobs.append((bx, by, br))
    for (bx, by, br) in blobs:
        d.ellipse((bx - br, by - br * 0.75 + 1, bx + br, by + br * 0.75 + 1), fill=C(pal[0]))
    for (bx, by, br) in blobs:
        d.ellipse((bx - br, by - br * 0.75, bx + br, by + br * 0.75), fill=C(pal[1]))
    for (bx, by, br) in blobs:
        rr = br * 0.62
        d.ellipse((bx - rr - br * 0.25, by - br * 0.7, bx + rr - br * 0.25, by - br * 0.7 + rr * 1.0), fill=C(pal[2]))
    for (bx, by, br) in blobs:
        if by < cy:
            rr = br * 0.3
            d.ellipse((bx - rr - br * 0.4, by - br * 0.62, bx + rr - br * 0.4, by - br * 0.62 + rr * 0.9), fill=C(pal[3]))


def haze_img(im, amt_top, amt_bot, col=HAZE, y0=0, y1=H):
    """空气透视：不透明的像素往 col 混，混合量从 amt_top（y0）到 amt_bot（y1）。"""
    a = np.array(im).astype(np.float32)
    ys = np.arange(im.height, dtype=np.float32)[:, None]
    amt = np.clip(amt_top + (ys - y0) / max(1, y1 - y0) * (amt_bot - amt_top), min(amt_top, amt_bot),
                  max(amt_top, amt_bot))
    m = a[..., 3] > 0
    hz = np.array(col, np.float32)
    a[..., :3] = np.where(m[..., None], a[..., :3] * (1 - amt[..., None]) + hz * amt[..., None], a[..., :3])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def _hex(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def tinted(im, tint):
    """把 tint 层（颜色、alpha）预先罩在不透明像素上（前景用：人物夹在背景和前景中间，前景要自己罩）。"""
    col = np.array(_hex(tint[0]), np.float32)
    al = int(255 * tint[1]) / 255.0
    a = np.array(im).astype(np.float32)
    m = a[..., 3] > 0
    a[m, :3] = a[m, :3] * (1 - al) + col * al
    return Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA')


# ============================================================ 天空 / 云 / 雨天的云
@lru_cache(maxsize=1)
def sky_img():
    """灰黄的热天：上面发灰蓝、往下越来越黄（霾）；左上一个发白的太阳 + 一大圈光晕。"""
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), SKY_STOPS, bands=12)
    A._glow(im, 52, 24, 70, 50, (250, 240, 212), 70, rings=6)
    d = ImageDraw.Draw(im)
    d.ellipse((46, 18, 58, 30), fill=C((252, 244, 222)))
    d.ellipse((48, 20, 56, 28), fill=C((255, 252, 238)))
    return im


@lru_cache(maxsize=1)
def clouds_img():
    """640 循环：霾里的几朵扁云 + 拉得很长的薄层云。"""
    im = A._new(640, 84)
    pal = ((244, 238, 222), (230, 224, 208), (214, 208, 194), (200, 196, 184))
    for i in range(5):
        w = hrange(52, 100, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.28, 0.4, i, 2), 610 + i, pal)
        cx = (i + hrange(0.1, 0.9, i, 3)) * 640 / 5
        y = 84 - cl.height - int(hrange(0, 30, i, 4))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    d = ImageDraw.Draw(im)
    for i in range(10):
        y = int(hrange(3, 50, i, 21))
        L = int(hrange(70, 180, i, 22))
        x0 = int(hrange(0, 640, i, 23))
        for k in range(L):
            s = math.sin(math.pi * k / L)
            xx = (x0 + k) % 640
            if hash01(i, k, 24) < 1.3 * s ** 0.6 - 0.15:
                d.point((xx, y), fill=C((230, 226, 210)))
            if hash01(i, k, 25) < 1.1 * s - 0.35:
                d.point((xx, y + 1), fill=C((222, 218, 204)))
    return im


@lru_cache(maxsize=1)
def rain_sky_img():
    """下雨的天（wrap 640，整片不透明，盖住晴天的天和云）：低低的铅灰色积雨云，云底更暗，几道亮一点的云缘。"""
    w, h = 640, 140
    im = A._new(w, h)
    gradient(im, (0, 0, w, h), [(88, 98, 112), (104, 112, 124), (122, 128, 136), (138, 142, 144)], bands=10)
    a = np.array(im)
    n = A._fbm_wrap(w, h * 3, 40, seed=411)[::3]                  # 横向拉长的云团（层积云）
    n2 = A._fbm_wrap(w, h * 2, 10, seed=412)[::2]
    bay = A._bayer(w, h)
    ys = np.arange(h, dtype=np.float32)[:, None] / h
    v = n * 0.8 + n2 * 0.2 + ys * 0.06
    for (c, th) in (((118, 126, 136), 0.36), ((80, 88, 104), 0.47), ((70, 78, 94), 0.54), ((60, 66, 82), 0.61)):
        m = (v > th + 0.015) | ((v > th) & (bay < 0.5))
        a[m, :3] = c
    lite = (v < 0.33) | ((v < 0.35) & (bay < 0.5))
    a[lite, :3] = (140, 146, 152)
    a[..., 3] = 255
    return Image.fromarray(a, 'RGBA')


@lru_cache(maxsize=1)
def clear_sky_img():
    """雨停（sunbeam）：还是一层湿灰的云，左上裂开一道口子，透出亮白的天 + 太阳，斜着几道光柱往右下。"""
    w, h = W, 140
    im = A._new(w, h)
    gradient(im, (0, 0, w, h), [(128, 136, 146), (146, 152, 158), (164, 168, 168), (178, 180, 176)], bands=10)
    a = np.array(im)
    n = A._fbm(w + 8, h * 3 + 8, 30, seed=421)[4:4 + h * 3:3, 4:4 + w]
    bay = A._bayer(w, h)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rift = np.exp(-(((xx - 92) / 70.0) ** 2 + ((yy - 22) / 20.0) ** 2)) * 0.9 - (n - 0.5) * 0.7
    a[(n > 0.52) | ((n > 0.5) & (bay < 0.5)), :3] = (114, 122, 134)
    a[(n > 0.6) | ((n > 0.58) & (bay < 0.5)), :3] = (100, 108, 122)
    for (th, c) in ((0.30, (196, 198, 190)), (0.45, (224, 222, 206)), (0.6, (242, 238, 222))):
        m = (rift > th + 0.03) | ((rift > th) & (bay < 0.5))
        a[m, :3] = c
    edge = (rift > 0.22) & (rift < 0.3) & (bay < 0.5)
    a[edge, :3] = (232, 214, 170)                                  # 裂口边上被照亮的云缘（偏暖）
    a[..., 3] = 255
    im = Image.fromarray(a, 'RGBA')
    A._glow(im, 98, 18, 40, 22, (255, 246, 214), 90, rings=4)
    d = ImageDraw.Draw(im)
    d.ellipse((93, 13, 103, 23), fill=C((255, 250, 232)))
    # 光柱（往右下，淡淡的几条）
    lay = A._new(w, h)
    ld = ImageDraw.Draw(lay)
    for (x0, wd, al) in ((84, 10, 22), (104, 6, 18), (122, 14, 16), (70, 5, 14)):
        for k in range(3):
            ld.polygon([(x0 + k, 26), (x0 + wd - k, 26), (x0 + wd + 120 - k, h), (x0 + 120 - wd + k, h)],
                       fill=(255, 244, 210, al // 2 + k * 4))
    im.alpha_composite(lay)
    a = np.array(im)
    a[..., 3] = 255
    return Image.fromarray(a, 'RGBA')


def bird_img(kind=0):
    """远处的一小群鸽子 / 乌鸦（一张小图里 5–8 只，翅膀有上有下）。"""
    g = A._new(30, 12)
    d = ImageDraw.Draw(g)
    col = (70, 70, 78) if kind == 0 else (46, 44, 50)
    n = 7 if kind == 0 else 5
    for i in range(n):
        x = int(hrange(1, 26, kind, i, 1))
        y = int(hrange(1, 9, kind, i, 2))
        if hash01(kind, i, 3) < 0.5:
            for (dx, dy) in ((0, 0), (1, 1), (3, 1), (4, 0)):
                px(d, x + dx, y + dy, col)
            px(d, x + 2, y + 2, col)
        else:
            for (dx, dy) in ((0, 1), (1, 1), (2, 1), (3, 1), (4, 1)):
                px(d, x + dx, y + dy, col)
            px(d, x + 1, y + 2, col)
            px(d, x + 3, y + 2, col)
    return g


BIRDS = [(18, -6.0, 0.3, 60, 0), (34, -4.2, 0.26, 260, 1), (12, -5.0, 0.32, 380, 0)]   # (y, vx, k, x0, 图)


# ============================================================ 远景：豪拉大桥 / 邮政总局圆顶 / 高等法院 / 纪念柱 / 维多利亚纪念堂 / 教堂尖塔 / 烟囱
def _howrah(d, x0, x1, deck):
    """豪拉大桥（悬臂钢桁架）的侧影：两座高塔、M 形上弦、桥面、桁架斜杆。"""
    t1, t2 = x0 + int((x1 - x0) * 0.24), x0 + int((x1 - x0) * 0.76)
    top = deck - 66
    mid = (x0 + x1) // 2
    chord = [(x0, deck - 22), (t1, top), (mid - 14, deck - 38), (mid, deck - 42), (mid + 14, deck - 38), (t2, top),
             (x1, deck - 22)]

    def ychord(x):
        for (ax, ay), (bx, by) in zip(chord, chord[1:]):
            if ax <= x <= bx:
                return ay + (by - ay) * (x - ax) / max(1, bx - ax)
        return deck

    col, col_d = (118, 126, 134), (98, 106, 116)
    for x in range(x0, x1 + 1):
        if (x - x0) % 6 == 0:
            vl(d, x, int(ychord(x)), deck, col_d)
    for x in range(x0, x1 - 5, 6):
        y0, y1 = ychord(x), ychord(x + 6)
        d.line((x, deck, x + 6, round(y1)), fill=C(col_d))
        d.line((x, round(y0), x + 6, deck), fill=C(col_d))
    d.line([(x, round(y)) for (x, y) in chord], fill=C(col), width=2)
    for tx in (t1, t2):                                               # 塔：两根腿 + 交叉撑
        for yy in range(top - 2, deck + 1):
            u = (yy - top) / (deck - top)
            half = 1 + int(3 * u)
            px(d, tx - half, yy, col)
            px(d, tx + half, yy, col_d)
            if (yy - top) % 8 < 1:
                hl(d, tx - half, tx + half, yy, col)
        for k in range(0, deck - top - 8, 8):
            d.line((tx - 1, top + k, tx + 2, top + k + 8), fill=C(col_d))
    rect(d, x0 - 4, deck, x1 + 4, deck + 2, (124, 128, 132))          # 桥面
    hl(d, x0 - 4, x1 + 4, deck, (150, 152, 154))


def _domed(d, cx, base, drum_w, drum_h, rx, ry, col, cupola=True):
    """圆顶（鼓座 + 半球 + 小灯笼亭）：左亮右暗。"""
    rect(d, cx - drum_w // 2, base - drum_h, cx + drum_w // 2, base, col)
    for xx in range(cx - drum_w // 2 + 1, cx + drum_w // 2, 3):
        vl(d, xx, base - drum_h + 2, base - 2, dk(col, 0.8))
    vl(d, cx + drum_w // 2, base - drum_h, base, dk(col, 0.78))
    top = base - drum_h
    for x in range(cx - rx, cx + rx + 1):
        u = (x - cx) / rx
        hgt = ry * math.sqrt(max(0.0, 1 - u * u))
        c = mix(lt(col, 0.18), dk(col, 0.72), (u + 1) / 2)
        vl(d, x, int(round(top - hgt)), top, c)
    if cupola:
        rect(d, cx - 1, top - ry - 5, cx + 1, top - ry - 1, col)
        vl(d, cx, top - ry - 9, top - ry - 6, dk(col, 0.6))


@lru_cache(maxsize=1)
def far_img():
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    # 一长条连绵的低楼（y 76–124），屋顶上零星的水箱 / 小屋
    x, i = 0, 0
    pal = [(206, 192, 170), (190, 176, 160), (214, 204, 186), (182, 170, 162), (200, 184, 156), (176, 168, 156)]
    while x < FARW:
        w = int(hrange(9, 24, i, 1))
        top = int(hrange(80, 102, i, 2))
        col = pal[int(hash01(i, 3) * len(pal))]
        rect(d, x, top, x + w - 1, 124, col)
        vl(d, x + w - 1, top, 124, dk(col, 0.84))
        for y in range(top + 3, 122, 4):
            for xx in range(x + 2, x + w - 2, 3):
                if hash01(xx, y, i, 4) < 0.7:
                    px(d, xx, y, dk(col, 0.74))
        if hash01(i, 5) < 0.35:
            tx = x + int(hrange(1, max(2, w - 5), i, 6))
            rect(d, tx, top - 3, tx + 3, top - 1, dk(col, 0.7))
        x += w
        i += 1
    # 树丛
    for i in range(16):
        tx = int(hrange(0, FARW, i, 11))
        _canopy(d, tx, int(hrange(92, 104, i, 12)), hrange(6, 12, i, 13), hrange(4, 7, i, 14), 300 + i,
                pal=((70, 96, 70), (86, 112, 80), (104, 128, 90), (124, 146, 100)))
    # 豪拉大桥（地图左头，车站那边）
    _howrah(d, 2, 156, 96)
    # 邮政总局（GPO）：柱廊 + 鼓座圆顶
    gx = 186
    rect(d, gx - 18, 74, gx + 18, 112, (230, 222, 200))
    for xx in range(gx - 16, gx + 17, 3):
        vl(d, xx, 80, 100, (196, 188, 168))
    hl(d, gx - 19, gx + 19, 74, (244, 238, 222))
    _domed(d, gx, 74, 18, 12, 11, 14, (236, 230, 214))
    # 高等法院的哥特式塔
    hx = 230
    rect(d, hx, 40, hx + 12, 108, (196, 146, 118))
    vl(d, hx + 12, 40, 108, (166, 118, 96))
    for (xx, yy) in ((hx, 32), (hx + 4, 34), (hx + 8, 34), (hx + 12, 32)):
        vl(d, xx, yy, 40, (186, 136, 110))
    for yy in range(46, 104, 9):
        rect(d, hx + 3, yy, hx + 4, yy + 5, (130, 96, 84))
        rect(d, hx + 8, yy, hx + 9, yy + 5, (130, 96, 84))
    # 纪念柱（Ochterlony / Shaheed Minar）：细高的柱子、两层小阳台、顶上土耳其式小圆亭
    mx = 274
    rect(d, mx - 7, 96, mx + 7, 110, (226, 218, 198))
    rect(d, mx - 3, 18, mx + 3, 96, (234, 226, 206))
    vl(d, mx + 3, 18, 96, (200, 192, 172))
    vl(d, mx - 1, 22, 94, (214, 206, 186))
    for yy in (52, 30):
        rect(d, mx - 5, yy, mx + 5, yy + 2, (240, 234, 218))
        hl(d, mx - 5, mx + 5, yy + 3, (196, 188, 168))
    rect(d, mx - 4, 12, mx + 4, 17, (236, 228, 208))
    d.pieslice((mx - 4, 6, mx + 4, 16), 180, 360, fill=C((228, 220, 200)))
    vl(d, mx, 2, 6, (180, 172, 156))
    # 维多利亚纪念堂（白色大理石：宽台基 + 拱廊 + 中间大圆顶 + 天使 + 四角小圆亭）
    vx = 362
    rect(d, vx - 44, 82, vx + 44, 112, (242, 240, 232))
    for xx in range(vx - 40, vx + 41, 6):
        rect(d, xx, 88, xx + 2, 100, (214, 212, 206))
        d.pieslice((xx, 86, xx + 2, 90), 180, 360, fill=C((214, 212, 206)))
    hl(d, vx - 45, vx + 45, 82, (252, 250, 246))
    rect(d, vx - 20, 70, vx + 20, 82, (240, 238, 230))
    _domed(d, vx, 70, 22, 8, 14, 17, (244, 242, 236))
    vl(d, vx, 36, 40, (120, 120, 120))                               # 天使
    px(d, vx - 1, 37, (120, 120, 120))
    px(d, vx + 1, 37, (120, 120, 120))
    for cx in (vx - 36, vx + 36):
        _domed(d, cx, 82, 8, 6, 5, 6, (238, 236, 228), cupola=False)
    # 圣保罗教堂的塔
    sx = 432
    rect(d, sx, 34, sx + 10, 108, (214, 210, 200))
    vl(d, sx + 10, 34, 108, (180, 176, 168))
    for (xx, yy) in ((sx, 26), (sx + 5, 28), (sx + 10, 26)):
        vl(d, xx, yy, 34, (200, 196, 186))
    rect(d, sx + 3, 44, sx + 7, 56, (150, 146, 140))
    d.pieslice((sx + 3, 41, sx + 7, 47), 180, 360, fill=C((150, 146, 140)))
    # 高压电线塔（两座钢架塔 + 三根往两边下垂的线）
    PY = ((300, 34), (412, 40))
    for (tx, top) in PY:
        for yy in range(top, 112):
            u = (yy - top) / (112 - top)
            half = int(1 + 6 * u)
            px(d, tx - half, yy, (118, 122, 128))
            px(d, tx + half, yy, (100, 104, 112))
            if (yy - top) % 6 == 0:
                hl(d, tx - half, tx + half, yy, (118, 122, 128))
                d.line((tx - half, yy, tx + half + 1, yy + 6), fill=C((110, 114, 120)))
        for (yy, w) in ((top + 4, 9), (top + 12, 7)):
            hl(d, tx - w, tx + w, yy, (110, 114, 120))
    (ax, ay), (bx, by) = PY
    for k, (dy, dx) in enumerate(((4, 9), (4, -9), (12, 7))):
        for x in range(200, FARW):
            if ax + dx <= x <= bx + dx:
                u = (x - ax - dx) / (bx - ax)
                yy = ay + dy + (by - ay) * u + 9 * math.sin(math.pi * u)
            elif x < ax + dx:
                yy = ay + dy + (ax + dx - x) * 0.18
            else:
                yy = by + dy + (x - bx - dx) * 0.18
            if hash01(x, k, 31) < 0.85:
                px(d, x, round(yy), (120, 124, 130))
    # 80 年代的新高楼（灰色混凝土格子）
    tx = 458
    rect(d, tx, 30, tx + 18, 112, (184, 186, 184))
    rect(d, tx + 19, 32, tx + 22, 112, (156, 158, 158))
    for y in range(33, 110, 3):
        for xx in range(tx + 2, tx + 17, 3):
            rect(d, xx, y, xx + 1, y + 1, (146, 150, 152))
    vl(d, tx + 9, 20, 29, (130, 132, 134))
    # 烟囱 + 一缕烟
    for (cx, top) in ((496, 40), (508, 50)):
        rect(d, cx, top, cx + 3, 108, (170, 112, 92))
        hl(d, cx - 1, cx + 4, top, (130, 90, 76))
        for k in range(26):
            xx = cx + 2 + k
            yy = top - 3 - int(k * 0.35 + 2 * math.sin(k * 0.4))
            if hash01(cx, k, 7) < 0.8:
                rect(d, xx, yy, xx + 1, yy + 1 + (k // 9), (196, 192, 184))
    return haze_img(im, 0.42, 0.62, y0=20, y1=120)


# ============================================================ 中景：屋顶一线（水箱、鱼骨天线、鸽子笼、晾衣、神庙尖顶、清真寺、棕榈、榕树）
def _antenna(d, x, top, h, col=(70, 72, 78)):
    """80 年代的鱼骨电视天线：一根杆 + 几道从长到短的横杆。"""
    vl(d, x, top, top + h, col)
    for k, w in enumerate((5, 4, 4, 3, 2)):
        y = top + 1 + k * 2
        hl(d, x - w // 2, x + (w + 1) // 2, y, col)


def _tank(d, x, top, w=7, h=6, col=(150, 150, 146)):
    """屋顶水箱（混凝土 / 铁皮）：方箱 + 顶盖 + 一根管子。"""
    rect(d, x, top, x + w - 1, top + h - 1, col)
    hl(d, x, x + w - 1, top, lt(col, 0.25))
    vl(d, x + w - 1, top, top + h - 1, dk(col, 0.75))
    vl(d, x + 1, top + h, top + h + 3, dk(col, 0.6))


def _mid_bldg(d, x, w, top, col, seed, base=132):
    """中景的楼：平顶女儿墙 + 一排排窗（百叶）+ 右侧背光的一条；屋顶上的小东西按种子挑。"""
    rect(d, x, top, x + w - 1, base, col)
    vl(d, x + w - 1, top, base, dk(col, 0.8))
    hl(d, x - 1, x + w, top, lt(col, 0.3))
    hl(d, x - 1, x + w, top + 1, dk(col, 0.86))
    for y in range(top + 6, base - 6, 11):
        for xx in range(x + 3, x + w - 4, 6):
            c = (68, 104, 84) if hash01(seed, xx, y, 1) < 0.6 else (64, 56, 58)
            rect(d, xx, y, xx + 2, y + 5, c)
            hl(d, xx - 1, xx + 3, y + 6, lt(col, 0.2))
        hl(d, x, x + w - 1, y + 8, dk(col, 0.88))
    r = hash01(seed, 9)
    if r < 0.3:
        _tank(d, x + int(hrange(1, max(2, w - 8), seed, 10)), top - 6)
    elif r < 0.55:
        _antenna(d, x + int(hrange(2, max(3, w - 3), seed, 11)), top - 14, 13)
    elif r < 0.75:
        rx = x + int(hrange(1, max(2, w - 12), seed, 12))
        rect(d, rx, top - 8, rx + 10, top - 1, mix(col, (150, 140, 130), 0.4))   # 屋顶小屋
        hl(d, rx - 1, rx + 11, top - 9, (118, 112, 106))
        rect(d, rx + 3, top - 5, rx + 5, top - 1, (70, 62, 60))
    if hash01(seed, 13) < 0.5:                                      # 屋顶晾衣绳
        lx = x + 2
        hl(d, lx, lx + min(w - 4, 16), top - 5, (90, 84, 80))
        for k in range(3):
            cc = ((210, 70, 80), (236, 230, 214), (70, 120, 180), (230, 170, 60))[int(hash01(seed, k, 14) * 4)]
            rect(d, lx + 2 + k * 5, top - 4, lx + 4 + k * 5, top - 1, cc)


def _palm(d, cx, cy, L, seed, trunk_base=None, pal=(LEAF_D, LEAF, LEAF_M)):
    """椰子树（中景小号，静止）：几片下垂的羽状叶 + 细树干。"""
    if trunk_base is not None:
        for y in range(cy, trunk_base):
            u = (y - cy) / max(1, trunk_base - cy)
            x = cx + int(2 * math.sin(u * 2.4))
            px(d, x, y, BARK)
            px(d, x + 1, y, BARK_D)
    for k in range(9):
        ang = math.radians(-160 + k * 40 + hrange(-8, 8, seed, k))
        for s in range(L):
            x = cx + math.cos(ang) * s
            y = cy + math.sin(ang) * s * 0.55 + (s * s) / (L * 1.6)
            px(d, round(x), round(y), pal[1] if s < L * 0.6 else pal[0])
            if s % 2 == 0 and s > 2:
                px(d, round(x), round(y) + 1, pal[0])
    px(d, cx, cy, (110, 120, 60))


@lru_cache(maxsize=1)
def mid_img():
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    pal = [(222, 196, 150), (206, 170, 160), (186, 196, 200), (226, 214, 188), (200, 180, 142), (176, 186, 168),
           (214, 184, 170), (196, 176, 190)]
    # 一排高低不齐的楼（屋顶 y 30–82）
    x, i = 0, 0
    while x < MIDW:
        w = int(hrange(22, 46, i, 1))
        top = int(hrange(50, 96, i, 2))
        _mid_bldg(d, x, w, top, pal[int(hash01(i, 3) * len(pal))], 500 + i)
        x += w + int(hrange(0, 3, i, 4))
        i += 1
    # 神庙尖顶（赭橙色的曲线塔身 + 一面三角小旗）
    tx, tb = 250, 92
    for y in range(tb - 56, tb + 1):
        u = (y - (tb - 56)) / 56
        half = int(round(3 + 9 * math.sin(min(1.0, u * 1.3) * math.pi / 2)))
        for xx in range(tx - half, tx + half + 1):
            v = (xx - (tx - half)) / max(1, 2 * half)
            c = mix((222, 150, 86), (170, 100, 60), v)
            if (y - tb) % 5 == 0:
                c = dk(c, 0.86)
            px(d, xx, y, c)
    d.ellipse((tx - 4, tb - 62, tx + 4, tb - 55), fill=C((206, 140, 80)))
    vl(d, tx, tb - 74, tb - 62, (110, 90, 70))
    d.polygon([(tx + 1, tb - 74), (tx + 9, tb - 71), (tx + 1, tb - 68)], fill=C((230, 120, 40)))
    rect(d, tx - 14, tb, tx + 14, 132, (210, 160, 110))
    # 清真寺（白绿色圆顶 + 两座宣礼塔）
    qx = 540
    rect(d, qx - 20, 70, qx + 20, 132, (230, 230, 220))
    for xx in range(qx - 16, qx + 17, 8):
        rect(d, xx, 84, xx + 3, 100, (110, 140, 120))
        d.pieslice((xx, 81, xx + 3, 87), 180, 360, fill=C((110, 140, 120)))
    _domed(d, qx, 70, 16, 4, 12, 13, (214, 228, 214))
    for mx in (qx - 22, qx + 22):
        rect(d, mx - 2, 30, mx + 2, 132, (236, 236, 228))
        vl(d, mx + 2, 30, 132, (196, 196, 190))
        rect(d, mx - 3, 44, mx + 3, 45, (214, 226, 212))
        d.pieslice((mx - 3, 24, mx + 3, 32), 180, 360, fill=C((200, 220, 200)))
        vl(d, mx, 19, 24, (150, 150, 140))
    # 高架水塔（混凝土柱子 + 水罐）
    wx = 404
    for lx in (wx - 8, wx + 8):
        d.line((lx, 132, wx + (lx - wx) // 2, 54), fill=C((150, 146, 140)), width=2)
    for y in (100, 76):
        hl(d, wx - 7, wx + 7, y, (150, 146, 140))
    rect(d, wx - 11, 38, wx + 11, 54, (170, 166, 160))
    hl(d, wx - 11, wx + 11, 38, (196, 192, 186))
    vl(d, wx + 11, 38, 54, (130, 126, 122))
    d.pieslice((wx - 11, 32, wx + 11, 44), 180, 360, fill=C((160, 156, 150)))
    # 鸽子笼（竹架子 + 小格子），屋顶上
    for (bx, by) in ((120, 52), (676, 46)):
        rect(d, bx, by, bx + 14, by + 10, (176, 150, 104))
        for xx in range(bx, bx + 15, 3):
            vl(d, xx, by, by + 10, (130, 108, 74))
        for yy in range(by, by + 11, 3):
            hl(d, bx, bx + 14, yy, (130, 108, 74))
        vl(d, bx + 1, by + 10, by + 22, (130, 108, 74))
        vl(d, bx + 13, by + 10, by + 22, (130, 108, 74))
        vl(d, bx + 7, by - 12, by, (120, 100, 70))                   # 赶鸽子的竹竿 + 小旗
        rect(d, bx + 8, by - 12, bx + 11, by - 10, (220, 70, 60))
    # 树：椰子树 / 大榕树的树冠
    for (cx, cy, L, sd) in ((150, 44, 12, 1), (166, 50, 10, 2), (470, 40, 13, 3), (760, 48, 11, 4), (330, 52, 10, 5)):
        _palm(d, cx, cy, L, sd, trunk_base=cy + 70)
    for (cx, cy, rx, ry, sd) in ((620, 66, 34, 22, 31), (40, 72, 26, 16, 32), (300, 80, 22, 14, 33)):
        _canopy(d, cx, cy, rx, ry, sd, pal=((48, 82, 50), (66, 106, 62), (90, 132, 76), (124, 160, 94)))
    # 屋顶广告牌的背面（铁架子）
    ax = 712
    for xx in range(ax, ax + 38, 6):
        vl(d, xx, 30, 62, (96, 92, 90))
    for yy in (30, 40, 50, 60):
        hl(d, ax, ax + 36, yy, (96, 92, 90))
    for xx in range(ax, ax + 36, 12):
        d.line((xx, 30, xx + 12, 50), fill=C((110, 106, 104)))
    return haze_img(im, 0.24, 0.34, y0=20, y1=130)


# ============================================================ 近景：地面
def draw_ground(im):
    """人行道（138–145，旧石板）+ 路缘石（146 顶 / 147 侧）+ 马路（148–179：补过的旧沥青 + 电车轨道）。
    马路就是可走带：纹理都压得很淡；x 440–720 只有平的纹理（战斗场地）。"""
    d = ImageDraw.Draw(im)
    rect(d, 0, FOOT_Y, PW - 1, KERB_Y - 1, FOOT)
    mottle(im, (0, FOOT_Y, PW - 1, KERB_Y - 1), FOOT, FOOT_S, FOOT_HI, 41, cell=5, lo=0.25, hi=0.75)
    d = ImageDraw.Draw(im)
    a = np.array(im).astype(np.float32)
    x, i = 0, 0
    while x < PW:                                                   # 一块块石板（明暗 ±4 %），竖缝 + 中间一道横缝
        w = int(hrange(9, 18, i, 42))
        f = hrange(0.96, 1.04, i, 43)
        a[FOOT_Y + 1:KERB_Y, x + 1:x + w, :3] *= f
        x += w
        i += 1
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))
    d = ImageDraw.Draw(im)
    x, i = 0, 0
    while x < PW:
        w = int(hrange(9, 18, i, 42))
        vl(d, x, FOOT_Y + 1, KERB_Y - 1, mix(FOOT, FOOT_S, 0.8))
        if hash01(i, 44) < 0.25:                                    # 碎了一角
            px(d, x + 1, KERB_Y - 1, FOOT_S)
            px(d, x + 2, KERB_Y - 1, mix(FOOT, FOOT_S, 0.6))
            px(d, x + 1, KERB_Y - 2, mix(FOOT, FOOT_S, 0.6))
        x += w
        i += 1
    for x in range(0, PW, 2):
        px(d, x, FOOT_Y + 4, mix(FOOT, FOOT_S, 0.55))
    hl(d, 0, PW - 1, FOOT_Y, dk(FOOT, 0.8))                         # 楼脚下一道暗缝
    hl(d, 0, PW - 1, KERB_Y, KERB_HI)
    hl(d, 0, PW - 1, KERB_Y + 1, KERB_F)
    x, i = 0, 0
    while x < PW:
        px(d, x, KERB_Y, mix(KERB_HI, KERB_F, 0.5))
        px(d, x, KERB_Y + 1, dk(KERB_F, 0.86))
        if hash01(i, 45) < 0.3:                                     # 路缘石缺口
            xx = x + int(hrange(3, 14, i, 46))
            px(d, xx, KERB_Y, KERB_F)
            px(d, xx + 1, KERB_Y, mix(KERB_HI, KERB_F, 0.6))
        x += int(hrange(18, 30, i, 47))
        i += 1
    # 马路
    rect(d, 0, STREET_Y, PW - 1, H - 1, STREET)
    mottle(im, (0, STREET_Y, PW - 1, H - 1), STREET, STREET_S, STREET_HI, 43, cell=7, lo=0.22, hi=0.8)
    d = ImageDraw.Draw(im)
    for x in range(PW):                                             # 路边一道浅浅的排水沟
        px(d, x, STREET_Y, mix(STREET, KERB_F, 0.45 if x % 3 else 0.6))
    # 补过的沥青块（低对比，边上一圈略深）
    for i in range(22):
        x0 = int(hrange(0, PW - 30, i, 48))
        y0 = int(hrange(150, 172, i, 49))
        w, h = int(hrange(10, 34, i, 50)), int(hrange(3, 7, i, 51))
        c = mix(STREET, (128, 122, 114), 0.45)
        rect(d, x0, y0, x0 + w, min(H - 1, y0 + h), c)
        hl(d, x0, x0 + w, y0, mix(c, STREET_S, 0.5))
        for xx in range(x0, x0 + w, 3):
            if hash01(i, xx, 52) < 0.4:
                px(d, xx, y0 + int(hrange(1, h, i, xx, 53)), mix(c, STREET_HI, 0.5))
    # 电车轨道（两根：轨头一行亮、下面一行暗槽；中间铺的石块略深）
    for y in range(RAILS[0] + 2, RAILS[1]):
        for x in range(PW):
            u, v = x % 7, (y - RAILS[0] - 2) % 3
            if v == 2 or u == ((y // 3) * 3) % 7:
                px(d, x, y, mix(STREET, STREET_S, 0.55))
    for ry in RAILS:
        hl(d, 0, PW - 1, ry - 1, mix(STREET, STREET_HI, 0.5))
        hl(d, 0, PW - 1, ry, RAIL_HI)
        hl(d, 0, PW - 1, ry + 1, RAIL_D)
        for x in range(23 if ry == RAILS[0] else 47, PW, 72):        # 钢轨接头
            px(d, x, ry, mix(RAIL_HI, RAIL_D, 0.5))
            px(d, x + 1, ry, mix(RAIL_HI, RAIL_D, 0.3))
    # 细裂缝
    for i in range(40):
        x, y = int(hrange(0, PW, i, 54)), int(hrange(150, 178, i, 55))
        for k in range(int(hrange(3, 9, i, 56))):
            if y not in RAILS and y - 1 not in RAILS:
                px(d, x, y, mix(STREET, STREET_S, 0.95))
            x += 1
            y += (1 if hash01(i, k, 57) < 0.3 else (-1 if hash01(i, k, 57) > 0.8 else 0))
            y = max(149, min(179, y))
    # 沙井盖（铸铁圆盖：压扁的椭圆 + 一圈纹）
    for x in (318, 588, 1010):
        d.ellipse((x - 7, 155, x + 7, 160), fill=C(mix(STREET, (96, 92, 88), 0.4)))
        d.ellipse((x - 5, 156, x + 5, 159), outline=C(mix(STREET, (96, 92, 88), 0.55)))
        hl(d, x - 3, x + 3, 157, mix(STREET, (120, 114, 108), 0.4))
    # 碎东西：万寿菊花瓣（神龛 / 茶摊一带多）、碎纸、树叶、小石子
    for i in range(170):
        x = int(hrange(0, PW, i, 58))
        y = int(hrange(149, 179, i, 59))
        if y in RAILS:
            continue
        r = hash01(i, 60)
        if 440 <= x < 720 and r < 0.6:
            continue
        near = min(abs(x - 900), abs(x - 370), abs(x - 160))
        if r < 0.35 and near < 60:
            px(d, x, y, (226, 150, 50) if hash01(i, 61) < 0.6 else (236, 196, 70))   # 花瓣
        elif r < 0.55:
            px(d, x, y, mix(STREET, (226, 222, 210), 0.5))           # 碎纸
            if hash01(i, 62) < 0.5:
                px(d, x + 1, y, mix(STREET, (226, 222, 210), 0.35))
        elif r < 0.75:
            px(d, x, y, mix(STREET, (120, 120, 70), 0.5))            # 树叶
        else:
            px(d, x, y, mix(STREET, STREET_S, 0.9))                  # 小石子
            px(d, x, y - 1, mix(STREET, STREET_HI, 0.8))
    # 湿印 / 小水洼（压水井、茶摊、神龛、巷口淌出来的水）：深一点的湿块，中间一小片反天光
    for (cx, cy, rx, ry) in ((152, 151, 16, 2.5), (360, 150, 12, 2), (896, 151, 14, 2.5), (1206, 152, 22, 3.5),
                             (1238, 158, 10, 2), (60, 150, 8, 1.6)):
        m = np.zeros((H, PW), bool)
        yy, xx = np.mgrid[0:H, 0:PW]
        n = A._fbm(PW + 8, H + 8, 4, seed=int(cx))[4:4 + H, 4:4 + PW]
        m = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 + (n - 0.5) * 1.2 < 1.0
        m[:STREET_Y] = False
        mul_mask(im, m, (0.86, 0.86, 0.88))
        m2 = ((xx - cx) / (rx * 0.55)) ** 2 + ((yy - cy) / (ry * 0.5)) ** 2 + (n - 0.5) * 1.2 < 1.0
        m2[:STREET_Y + 1] = False
        a = np.array(im)
        a[m2, :3] = (np.array((170, 172, 168)) * 0.6 + a[m2, :3] * 0.4).astype(np.uint8)
        im.paste(Image.fromarray(a, 'RGBA'))


# ============================================================ 近景：墙面的零件
def plaster(im, box, base, sh, hi, seed, cell=4):
    """灰泥墙：底色 + fbm 斑驳（暗 / 亮两档）。"""
    d = ImageDraw.Draw(im)
    rect(d, *box, base)
    mottle(im, box, base, mix(base, sh, 0.5), mix(base, hi, 0.55), seed, cell=cell)


def brick_patch(im, cx, cy, rx, ry, seed, clip=None):
    """灰泥掉了露出来的红砖：不规则的一块（fbm 抖边），砖 5×2 + 1 px 灰缝错缝；
    凹进去：里面上沿 / 左沿暗（灰泥的厚度投下的影），外面下沿 / 右沿一圈灰泥的断口亮。"""
    x0, x1 = int(cx - rx - 3), int(cx + rx + 3)
    y0, y1 = int(cy - ry - 3), int(cy + ry + 3)
    if clip:
        x0, y0 = max(x0, clip[0]), max(y0, clip[1])
        x1, y1 = min(x1, clip[2]), min(y1, clip[3])
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if w <= 2 or h <= 2:
        return
    n = A._fbm(w + 8, h + 8, 3, seed=seed % 997)[4:4 + h, 4:4 + w]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = ((xx + x0 - cx) / rx) ** 2 + ((yy + y0 - cy) / ry) ** 2
    m = r + (n - 0.5) * 1.3 < 1.0
    a = np.array(im)
    sub = a[y0:y1 + 1, x0:x1 + 1]
    m &= sub[..., 3] > 0
    out = sub.copy()
    for (j, i) in zip(*np.nonzero(m)):
        X, Y = x0 + i, y0 + j
        row = Y // 3
        if Y % 3 == 2 or (X + (row % 2) * 3) % 6 == 5:
            c = MORTAR
        else:
            b = hash01((X + (row % 2) * 3) // 6, row, seed, 7)
            c = BRICK if b < 0.55 else (BRICK_D if b < 0.8 else BRICK_HI)
            if Y % 3 == 0:
                c = lt(c, 0.08)
        out[j, i, :3] = c
    mm = m
    top = mm & ~np.roll(mm, 1, 0)
    left = mm & ~np.roll(mm, 1, 1)
    top2 = mm & ~np.roll(mm, 2, 0)
    out[top | left, :3] = (out[top | left, :3] * 0.66).astype(np.uint8)
    out[top2 & ~top, :3] = (out[top2 & ~top, :3] * 0.84).astype(np.uint8)
    lip = (~mm) & (np.roll(mm, 1, 0) | np.roll(mm, 1, 1)) & (sub[..., 3] > 0)
    out[lip, :3] = np.clip(out[lip, :3].astype(np.int16) + 26, 0, 255).astype(np.uint8)
    a[y0:y1 + 1, x0:x1 + 1] = out
    im.paste(Image.fromarray(a, 'RGBA'))


def _win_mask(w, h, kind):
    """窗洞形状（局部坐标）：arch = 半圆顶、seg = 浅弧顶、其余方的。"""
    m = np.ones((h, w), bool)
    if kind == 'arch':
        r = (w - 1) / 2
        for yy in range(int(math.ceil(r)) + 1):
            for xx in range(w):
                if (xx - r) ** 2 + (yy - r) ** 2 > (r + 0.35) ** 2:
                    m[yy, xx] = False
    elif kind == 'seg':
        for xx in range(w):
            u = (xx - (w - 1) / 2) / max(1, (w - 1) / 2)
            m[:int(round(2 * u * u)), xx] = False
    return m


def window(im, x, y0, w, h, kind='rect', shutter=SHUT, trim=(236, 228, 210), wall_sh=None, state='closed',
           seed=0, fan_glass='plain', hood=None):
    """一扇窗（x..x+w−1，y0..y0+h−1）：线脚框 + 百叶（绿漆，两扇）+ 拱窗的扇形气窗（辐条，有的嵌彩色玻璃）；
    窗洞上沿 / 左沿暗（凹进去），窗台下一道影。state：closed 关着 / half 开一扇（屋里暗 + 窗帘）/
    open 两扇都推开贴在墙上（看得见铁栏杆）/ broken 一扇歪着、掉了几片百叶 / dark 空洞。
    hood：'pedi'（三角楣）/ 'flat'（平檐）/ 'chajja'（混凝土遮阳板，影子落在窗上）。"""
    m = _win_mask(w, h, kind)
    d = ImageDraw.Draw(im)
    sh_d, sh_hi = dk(shutter, 0.7), lt(shutter, 0.22)
    wall_sh = wall_sh or dk(trim, 0.7)
    mm = np.zeros((h + 2, w + 2), bool)
    mm[1:-1, 1:-1] = m
    grow = mm.copy()
    grow[:-1] |= mm[1:]
    grow[1:] |= mm[:-1]
    grow[:, :-1] |= mm[:, 1:]
    grow[:, 1:] |= mm[:, :-1]
    for yy, xx in zip(*np.nonzero(grow & ~mm)):
        px(d, x - 1 + xx, y0 - 1 + yy, trim)
    r = (w - 1) / 2
    fan_h = int(math.ceil(r)) + 1 if kind == 'arch' else 0
    mid = x + w // 2
    for yy, xx in zip(*np.nonzero(m)):
        X, Y = x + xx, y0 + yy
        if yy < fan_h:                                             # 扇形气窗
            c = (64, 74, 92)
            ang = math.degrees(math.atan2(r + 1 - yy, xx - r))
            spoke = abs(((ang + 180) % 36) - 18) > 15 or yy == fan_h - 1
            if spoke:
                c = trim
            elif fan_glass == 'color':
                c = ((176, 60, 60), (60, 110, 170), (220, 180, 70), (70, 140, 90))[int(((ang + 180) // 36)) % 4]
            elif (xx + yy) % 3 == 0:
                c = (120, 136, 156)
            px(d, X, Y, c)
            continue
        yb = yy - fan_h
        leaf = 'l' if X < mid else 'r'
        if state == 'dark' or (state == 'half' and leaf == 'l') or state == 'open' or \
                (state == 'broken' and leaf == 'r' and yb > 3 and hash01(seed, yb, 9) < 0.5):
            c = DARK_IN
            if state == 'half' and xx in (1, 2):
                c = (214, 200, 176) if yb % 4 else (190, 174, 150)  # 窗帘
            elif state == 'open' and xx % 3 == 1:
                c = (34, 34, 36)                                    # 铁栏杆
            elif state == 'open' and yb % 6 == 3 and hash01(seed, xx, 10) < 0.5:
                c = (80, 70, 66)
            px(d, X, Y, c)
            continue
        c = shutter if (yb % 2 == 0) else sh_d
        if X in (x, mid) or X == x + w - 1 or X == mid - 1:
            c = sh_hi if X in (x, mid) else sh_d
        if yb == 0 or yy == h - 1:
            c = sh_hi
        px(d, X, Y, c)
    if state == 'broken':                                          # 歪掉的那一扇：往右下斜着挂
        for k in range(min(h - fan_h - 2, 10)):
            xx = x + w + 1 + k // 4
            yy = y0 + fan_h + 2 + k
            px(d, xx, yy, shutter if k % 2 == 0 else sh_d)
            px(d, xx + 1, yy, sh_d)
    if state == 'open':                                            # 推开的两扇贴在墙上
        lw = max(2, w // 2 - 1)
        for (sx, side) in ((x - 1 - lw, 0), (x + w + 1, 1)):
            for yy in range(fan_h, h):
                for k in range(lw):
                    c = shutter if (yy % 2 == 0) else sh_d
                    if k == (lw - 1 if side == 0 else 0):
                        c = sh_hi
                    px(d, sx + k, y0 + yy, c)
            vl(d, sx + (lw if side == 1 else -1), y0 + fan_h + 1, y0 + h, wall_sh)   # 打开的百叶投在墙上的影
    # 凹进去的影：上沿一行 + 左沿一列
    a = np.array(im)
    for yy, xx in zip(*np.nonzero(m)):
        top = yy == 0 or not m[yy - 1, xx]
        left = xx == 0 or not m[yy, xx - 1]
        if top or left or (yy == fan_h and fan_h):
            a[y0 + yy, x + xx, :3] = (a[y0 + yy, x + xx, :3] * 0.7).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    y1 = y0 + h - 1
    rect(d, x - 2, y1 + 1, x + w + 1, y1 + 2, trim)                # 窗台
    hl(d, x - 2, x + w + 1, y1 + 1, lt(trim, 0.4))
    hl(d, x - 1, x + w + 2, y1 + 3, wall_sh)
    if kind == 'arch':
        rect(d, mid - 1, y0 - 3, mid + 1, y0, trim)                  # 拱心石
        vl(d, mid + 1, y0 - 3, y0, wall_sh)
    if hood == 'pedi':
        for k in range(w // 2 + 3):
            px(d, x - 2 + k, y0 - 3 - k // 2, trim)
            px(d, x + w + 1 - k, y0 - 3 - k // 2, trim)
            px(d, x - 1 + k, y0 - 2 - k // 2, wall_sh)
        hl(d, x - 2, x + w + 1, y0 - 2, trim)
        hl(d, x - 1, x + w + 2, y0 - 1, wall_sh)
    elif hood == 'flat':
        rect(d, x - 3, y0 - 4, x + w + 2, y0 - 2, trim)
        hl(d, x - 3, x + w + 2, y0 - 4, lt(trim, 0.4))
        hl(d, x - 2, x + w + 3, y0 - 1, wall_sh)
    elif hood == 'chajja':                                         # 混凝土遮阳板：薄板 + 板下的影（盖住窗的上半截）
        rect(d, x - 4, y0 - 4, x + w + 3, y0 - 3, (196, 192, 184))
        hl(d, x - 4, x + w + 3, y0 - 4, (220, 216, 208))
        hl(d, x - 4, x + w + 3, y0 - 2, (120, 116, 112))
        mul_box(im, (x - 3, y0 - 1, x + w + 4, y0 + 3), (0.72, 0.74, 0.82))
        mul_box(im, (x - 2, y0 + 4, x + w + 4, y0 + 6), (0.82, 0.84, 0.9), level=0.5)


def cornice(im, x0, x1, y, trim, wall, depth=3, dentils=True):
    """线脚 / 檐口：顶上一行亮、中间 trim、（齿饰）、下沿一行暗；墙上落两行影（第二行 Bayer 一半）。"""
    d = ImageDraw.Draw(im)
    hl(d, x0, x1, y, lt(trim, 0.45))
    for k in range(1, depth):
        hl(d, x0, x1, y + k, trim)
    yd = y + depth
    if dentils:
        for x in range(x0, x1 + 1):
            px(d, x, yd, trim if x % 3 else dk(trim, 0.7))
        yd += 1
    hl(d, x0, x1, yd, dk(trim, 0.72))
    mul_box(im, (x0 + 1, yd + 1, x1, yd + 1), (0.78, 0.8, 0.88))
    mul_box(im, (x0 + 1, yd + 2, x1, yd + 2), (0.84, 0.86, 0.92), level=0.5)
    return yd + 1


def iron_balcony(im, x0, x1, yfloor, rail_h=9, trim=(230, 222, 204), seed=0):
    """铸铁阳台：楼板（亮面 + 下沿暗 + 小托架）+ 板下墙上的影；栏杆：上下两道扶手、2 px 一根的栏杆、中间一圈圈卷花。"""
    d = ImageDraw.Draw(im)
    rect(d, x0, yfloor, x1, yfloor + 1, trim)
    hl(d, x0, x1, yfloor, lt(trim, 0.4))
    hl(d, x0, x1, yfloor + 2, dk(trim, 0.6))
    for x in range(x0 + 3, x1 - 1, 10):                            # 托架
        rect(d, x, yfloor + 3, x + 1, yfloor + 4, dk(trim, 0.8))
        px(d, x, yfloor + 5, dk(trim, 0.8))
    mul_box(im, (x0 + 2, yfloor + 3, x1 + 1, yfloor + 5), (0.76, 0.78, 0.86))
    mul_box(im, (x0 + 3, yfloor + 6, x1 + 2, yfloor + 7), (0.84, 0.86, 0.92), level=0.5)
    d = ImageDraw.Draw(im)
    ytop = yfloor - rail_h
    hl(d, x0, x1, ytop, IRON_HI)
    hl(d, x0, x1, ytop + 1, IRON)
    hl(d, x0, x1, yfloor - 1, IRON)
    for x in range(x0, x1 + 1, 2):
        vl(d, x, ytop + 2, yfloor - 2, IRON)
    for x in range(x0 + 1, x1 - 2, 5):                             # 卷花
        cy = ytop + 2 + (rail_h - 3) // 2
        d.ellipse((x, cy - 1, x + 3, cy + 2), outline=C(IRON))
    for x in (x0, x1):
        rect(d, x, ytop, x + (1 if x == x0 else 0), yfloor - 1, IRON)


def wood_balcony(im, x0, x1, ytop, yfloor, wood=WOOD, seed=0):
    """木头的封闭阳台（凸出来的木窗廊）：上面一道小坡檐、百叶板、雕花横条、下面两根斜撑；影落在右下。"""
    d = ImageDraw.Draw(im)
    wd, wh = dk(wood, 0.72), lt(wood, 0.2)
    d.polygon([(x0 - 2, ytop), (x1 + 2, ytop), (x1 + 1, ytop - 3), (x0 - 1, ytop - 3)], fill=C(dk(wood, 0.85)))
    hl(d, x0 - 1, x1 + 1, ytop - 3, wh)
    rect(d, x0, ytop + 1, x1, yfloor, wood)
    for y in range(ytop + 2, yfloor - 4):
        for x in range(x0 + 1, x1):
            if (x - x0) % 6 in (0, 5):
                px(d, x, y, wd if (x - x0) % 6 == 5 else wh)
            elif y % 2 == 0:
                px(d, x, y, wd)
    for x in range(x0 + 1, x1, 2):                                 # 雕花横条
        px(d, x, yfloor - 3, wh)
        px(d, x + 1, yfloor - 2, wd)
    hl(d, x0, x1, yfloor, wd)
    for x in (x0 + 2, x1 - 2):                                     # 斜撑
        d.line((x, yfloor + 1, x + (3 if x < (x0 + x1) // 2 else -3), yfloor + 6), fill=C(wd))
    mul_box(im, (x1 + 1, ytop + 1, x1 + 2, yfloor + 2), (0.76, 0.78, 0.86))
    mul_box(im, (x0 + 2, yfloor + 1, x1 + 2, yfloor + 3), (0.8, 0.82, 0.88))


def parapet(im, x0, x1, ytop, kind, trim, wall, seed=0):
    """屋顶女儿墙：baluster（宝瓶栏杆，栏杆之间透出后面）/ solid（实墙 + 两角瓶饰）/ broken（缺了几块、长草）。"""
    d = ImageDraw.Draw(im)
    if kind == 'baluster':
        rect(d, x0, ytop, x1, ytop + 1, trim)
        hl(d, x0, x1, ytop, lt(trim, 0.4))
        hl(d, x0, x1, ytop + 2, dk(trim, 0.7))
        a = np.array(im)
        for x in range(x0, x1 + 1):                                # 栏杆之间是空的（透出后面）
            k = (x - x0) % 4
            for y in range(ytop + 3, ytop + 8):
                if k == 3 and x0 + 2 < x < x1 - 2:
                    a[y, x, 3] = 0
                elif k == 0:
                    a[y, x, :3] = lt(trim, 0.2) if y != ytop + 5 else trim
                    a[y, x, 3] = 255
                elif k == 1:
                    a[y, x, :3] = trim if y not in (ytop + 4, ytop + 6) else lt(trim, 0.1)
                    a[y, x, 3] = 255
                else:
                    a[y, x, :3] = dk(trim, 0.75)
                    a[y, x, 3] = 255
        im.paste(Image.fromarray(a, 'RGBA'))
        d = ImageDraw.Draw(im)
        rect(d, x0, ytop + 8, x1, ytop + 9, trim)
        hl(d, x0, x1, ytop + 10, dk(trim, 0.72))
        for x in (x0, x1 - 2):                                     # 两头的墩子
            rect(d, x, ytop - 1, x + 2, ytop + 9, trim)
            vl(d, x + 2, ytop - 1, ytop + 9, dk(trim, 0.75))
        return ytop + 11
    if kind in ('solid', 'broken'):
        rect(d, x0, ytop, x1, ytop + 6, wall)
        hl(d, x0 - 1, x1 + 1, ytop, lt(trim, 0.3))
        hl(d, x0 - 1, x1 + 1, ytop + 1, trim)
        hl(d, x0, x1, ytop + 2, dk(wall, 0.8))
        for x in range(x0 + 4, x1 - 3, 9):                         # 浅浅的方格线脚
            rect(d, x, ytop + 3, x + 6, ytop + 5, None, outline=dk(wall, 0.86))
        if kind == 'broken':
            a = np.array(im)
            for i in range(3):
                bx = int(hrange(x0 + 6, x1 - 10, seed, i, 81))
                bw = int(hrange(3, 7, seed, i, 82))
                for x in range(bx, bx + bw):
                    dep = int(2 + 3 * math.sin(math.pi * (x - bx) / bw))
                    a[ytop:ytop + dep, x, 3] = 0
                    a[ytop + dep, x, :3] = BRICK_D
            im.paste(Image.fromarray(a, 'RGBA'))
        return ytop + 7
    return ytop


def urn(d, x, y, trim):
    """女儿墙角上的瓶饰。"""
    rect(d, x - 1, y - 2, x + 1, y, trim)
    d.ellipse((x - 2, y - 6, x + 2, y - 2), fill=C(trim))
    px(d, x + 1, y - 4, dk(trim, 0.75))
    px(d, x, y - 7, trim)


def pilaster(im, x, y0, y1, trim, w=4):
    """壁柱：左亮右暗，右边墙上一道影；上下柱头柱础。"""
    d = ImageDraw.Draw(im)
    rect(d, x, y0, x + w - 1, y1, trim)
    vl(d, x, y0, y1, lt(trim, 0.35))
    vl(d, x + w - 1, y0, y1, dk(trim, 0.8))
    mul_box(im, (x + w, y0 + 2, x + w, y1), (0.8, 0.82, 0.9))
    for yy in (y0, y1 - 1):
        rect(d, x - 1, yy, x + w, yy + 1, lt(trim, 0.2))
        hl(d, x - 1, x + w, yy + 2 if yy == y0 else yy - 1, dk(trim, 0.78))


def sapling(d, x, y, seed, s=1.0):
    """墙缝里长出来的小菩提树苗（心形叶子一小丛）+ 几根往下钻的根。"""
    for k in range(int(4 * s)):
        vl(d, x + (k % 2), y + 1, y + 2 + k * 2, (110, 92, 70))
    n = int(6 * s) + 2
    for i in range(n):
        lx = x + int(hrange(-4, 5, seed, i, 1) * s)
        ly = y - int(hrange(0, 6, seed, i, 2) * s)
        c = (LEAF_M, LEAF, LEAF_HI)[int(hash01(seed, i, 3) * 3)]
        rect(d, lx, ly, lx + 1, ly + 1, c)
        px(d, lx + 1, ly + 2, dk(c, 0.8))


def signboard(im, x0, y0, x1, y1, bg, fg, kind='bars', seed=0):
    """招牌（只画色块和图形，不写字）：铁皮框、底色、几道粗色条 / 一个小图标；kind：bars / pot / cup / tyre / cross / tram。"""
    d = ImageDraw.Draw(im)
    rect(d, x0, y0, x1, y1, bg)
    rect(d, x0, y0, x1, y1, None, outline=dk(bg, 0.6))
    hl(d, x0 + 1, x1 - 1, y0 + 1, lt(bg, 0.25))
    mul_box(im, (x0 + 1, y1 + 1, x1 + 1, y1 + 1), (0.78, 0.8, 0.88))
    d = ImageDraw.Draw(im)
    h = y1 - y0
    ix = x0 + 3
    if kind in ('pot', 'cup', 'tyre', 'cross', 'chili'):            # 左边一个小图标
        cx, cy = x0 + 3 + (h - 4) // 2, (y0 + y1) // 2
        if kind == 'pot':
            d.ellipse((cx - 3, cy - 2, cx + 3, cy + 3), fill=C((222, 176, 70)))
            hl(d, cx - 2, cx + 2, cy - 3, (240, 206, 110))
            px(d, cx - 1, cy - 1, (255, 236, 170))
        elif kind == 'cup':
            rect(d, cx - 2, cy - 2, cx + 2, cy + 3, (226, 220, 206))
            px(d, cx + 3, cy, (226, 220, 206))
            px(d, cx - 1, cy - 4, (200, 200, 200))
            px(d, cx + 1, cy - 5, (200, 200, 200))
        elif kind == 'tyre':
            d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), outline=C((40, 40, 44)), width=2)
        elif kind == 'cross':
            rect(d, cx - 1, cy - 3, cx + 1, cy + 3, (60, 160, 90))
            rect(d, cx - 3, cy - 1, cx + 3, cy + 1, (60, 160, 90))
        elif kind == 'chili':
            d.line((cx - 3, cy + 2, cx + 2, cy - 2), fill=C((210, 40, 30)), width=2)
            px(d, cx + 3, cy - 3, (60, 120, 50))
        ix = cx + 6
    yy = y0 + 2
    while yy + 1 < y1 - 1:                                         # 粗色条（像字但不是字）
        xx = ix
        while xx < x1 - 3:
            L = int(hrange(3, 9, seed, xx, yy, 1))
            rect(d, xx, yy, min(x1 - 3, xx + L), yy + 1, fg)
            xx += L + 2
        yy += 4


def tin_awning(im, x0, x1, y, depth=6, col=(150, 150, 146), rust=True, seed=0):
    """铁皮遮雨棚（瓦楞铁，往外斜下来）：一道道竖纹、锈斑、下沿一行暗、底下一大片影。"""
    d = ImageDraw.Draw(im)
    for x in range(x0, x1 + 1):
        for k in range(depth):
            c = col if (x - x0) % 3 else dk(col, 0.8)
            if k == 0:
                c = lt(c, 0.25)
            if rust and hash01(x // 3, k, seed, 5) < 0.18:
                c = mix(c, (150, 84, 50), 0.6)
            px(d, x, y + k, c)
        px(d, x, y + depth, dk(col, 0.5))
    mul_box(im, (x0, y + depth + 1, x1 + 1, y + depth + 6), (0.72, 0.74, 0.82))
    mul_box(im, (x0, y + depth + 7, x1 + 2, y + depth + 8), (0.84, 0.86, 0.9), level=0.5)


def shade_interior(im, top_k=0.58, bot_k=0.8, cool=(0.94, 0.97, 1.08)):
    """铺子里的阴影：上暗下亮（下半截有路面的反光），偏冷。原地改。"""
    a = np.array(im).astype(np.float32)
    h = a.shape[0]
    u = np.arange(h, dtype=np.float32)[:, None] / max(1, h - 1)
    k = top_k + (bot_k - top_k) * u ** 0.9
    mul = np.stack([k * cool[0], k * cool[1], k * cool[2]], -1)
    a[..., :3] = a[..., :3] * np.minimum(mul, 1.0)
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


# ============================================================ 近景：一楼铺面（局部坐标，最后统一压阴影）
def shop_img(kind, w, h, seed):
    """一楼铺子里看得见的东西（w × h），先画亮色，最后 shade_interior 压阴影（上暗下亮）。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    R = lambda *k: hrange(0, 1, seed, *k)  # noqa: E731
    backs = dict(spice=(196, 170, 130), sweets=(214, 206, 186), saris=(196, 180, 160), brass=(150, 120, 92),
                 cycle=(170, 166, 156), grocery=(204, 190, 158), pharmacy=(206, 214, 210), photo=(176, 170, 196),
                 tailor=(200, 192, 170), stair=(150, 140, 126), shutter=(150, 156, 150), godown=(120, 92, 66),
                 bank=(170, 170, 160))
    back = backs[kind]
    rect(d, 0, 0, w - 1, h - 1, back)
    hl(d, 0, w - 1, 0, dk(back, 0.55))
    hl(d, 0, w - 1, 1, dk(back, 0.72))
    rect(d, 0, h - 3, w - 1, h - 1, mix(back, (120, 112, 100), 0.5))          # 地面
    if kind == 'spice':
        for row, yy in enumerate((9, 16)):                         # 后墙两层架子：一排排玻璃罐
            hl(d, 2, w - 3, yy, (130, 96, 64))
            for xx in range(3, w - 4, 4):
                c = ((200, 60, 40), (226, 170, 50), (150, 100, 50), (110, 130, 60), (230, 210, 150))[int(R(row, xx) * 5)]
                rect(d, xx, yy - 4, xx + 2, yy - 1, (196, 210, 214))
                rect(d, xx, yy - 3, xx + 2, yy - 1, c)
                px(d, xx, yy - 4, (236, 240, 240))
        for xx in range(4, w - 4, 9):                              # 挂着的干辣椒串 / 大蒜辫
            for k in range(6):
                px(d, xx + (k % 2), 2 + k, (190, 40, 30) if R(xx, 3) < 0.6 else (226, 214, 180))
        for xx in range(2, w - 8, 8):                              # 地上的麻袋（卷口，露出里面的颜色）
            c = ((210, 60, 36), (230, 180, 60), (140, 96, 60), (236, 228, 200), (100, 120, 60))[int(R(xx, 4) * 5)]
            rect(d, xx, h - 10, xx + 6, h - 2, (196, 174, 130))
            hl(d, xx, xx + 6, h - 10, (220, 204, 160))
            rect(d, xx + 1, h - 12, xx + 5, h - 10, c)
            px(d, xx + 2, h - 13, lt(c, 0.25))
            vl(d, xx + 6, h - 9, h - 2, (160, 140, 104))
        rect(d, w // 2 - 3, 2, w // 2 + 3, 7, (200, 60, 50))      # 墙上的神像画（色块）
        rect(d, w // 2 - 2, 3, w // 2 + 2, 6, (230, 196, 120))
    elif kind == 'sweets':
        rect(d, 0, 2, w - 1, 3, (236, 236, 226))                  # 日光灯管
        hl(d, 4, w - 5, 2, (255, 255, 250))
        rect(d, 3, 6, 10, 13, (220, 220, 214))                    # 挂历（色块）
        rect(d, 4, 7, 9, 10, (90, 140, 190))
        for (gx0, gx1) in ((2, w // 2 - 2), (w // 2 + 1, w - 3)):  # 两个玻璃柜：一盘盘甜食
            rect(d, gx0, h - 16, gx1, h - 3, (150, 110, 74))
            rect(d, gx0 + 1, h - 15, gx1 - 1, h - 6, (176, 200, 206))
            hl(d, gx0 + 1, gx1 - 1, h - 15, (220, 236, 240))
            for (yy, k) in ((h - 12, 0), (h - 8, 1)):
                c = ((246, 244, 232), (150, 80, 50), (240, 150, 50), (240, 214, 120))[int(R(gx0, k) * 4)]
                for xx in range(gx0 + 2, gx1 - 1, 2):
                    px(d, xx, yy, c)
                    px(d, xx, yy + 1, dk(c, 0.85))
                hl(d, gx0 + 2, gx1 - 2, yy + 2, (200, 200, 196))
        d.ellipse((w // 2 - 6, 10, w // 2 + 6, 16), fill=C((176, 130, 60)))   # 后面的大铜锅
        hl(d, w // 2 - 4, w // 2 + 3, 10, (226, 186, 100))
    elif kind == 'saris':
        for xx in range(1, w - 3, 4):                              # 挂着的纱丽（竖条，带金边）
            c = ((200, 50, 70), (230, 150, 40), (60, 120, 180), (90, 160, 90), (190, 70, 150), (230, 210, 80),
                 (120, 60, 140))[int(R(xx, 5) * 7)]
            L = int(8 + R(xx, 6) * 8)
            rect(d, xx, 3, xx + 2, 3 + L, c)
            vl(d, xx + 2, 3, 3 + L, dk(c, 0.75))
            hl(d, xx, xx + 2, 3 + L, (230, 200, 100))
        for row in range(2):                                      # 叠好的布
            yy = h - 12 + row * 4
            for xx in range(2, w - 4, 5):
                c = ((180, 60, 60), (60, 110, 160), (220, 180, 70), (90, 150, 100), (236, 230, 216))[int(R(xx, row, 7) * 5)]
                rect(d, xx, yy, xx + 3, yy + 2, c)
                hl(d, xx, xx + 3, yy, lt(c, 0.3))
    elif kind == 'brass':
        for row, yy in enumerate((10, 18, h - 6)):                 # 三层架子上的铜器（锅、罐、盘）
            hl(d, 1, w - 2, yy + 1, (96, 70, 48))
            xx = 2
            while xx < w - 5:
                k = int(R(row, xx) * 3)
                c, chi = ((200, 150, 60), (250, 210, 120)) if R(row, xx, 1) < 0.75 else ((176, 180, 186), (236, 240, 244))
                if k == 0:                                         # 罐
                    d.ellipse((xx, yy - 5, xx + 4, yy), fill=C(c))
                    rect(d, xx + 1, yy - 7, xx + 3, yy - 5, c)
                    px(d, xx + 1, yy - 4, chi)
                    xx += 6
                elif k == 1:                                       # 锅
                    d.ellipse((xx, yy - 3, xx + 6, yy + 1), fill=C(c))
                    hl(d, xx + 1, xx + 5, yy - 3, chi)
                    xx += 8
                else:                                              # 竖着的盘子
                    d.ellipse((xx, yy - 6, xx + 5, yy), fill=C(c))
                    d.ellipse((xx + 1, yy - 5, xx + 4, yy - 1), outline=C(chi))
                    xx += 7
        for xx in range(4, w - 4, 7):                              # 挂着的钢桶
            vl(d, xx + 2, 2, 3, (90, 90, 90))
            d.polygon([(xx, 4), (xx + 4, 4), (xx + 3, 8), (xx + 1, 8)], fill=C((190, 194, 200)))
    elif kind == 'cycle':
        for xx in range(3, w - 8, 9):                              # 挂着的轮胎
            d.ellipse((xx, 3, xx + 7, 10), outline=C((40, 40, 42)), width=2)
        for (cx, cy) in ((10, h - 8), (24, h - 8)):                # 一辆自行车
            d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), outline=C((50, 50, 56)))
            px(d, cx, cy, (160, 160, 166))
        d.line((10, h - 8, 16, h - 15, 24, h - 8), fill=C((40, 70, 120)))
        d.line((16, h - 15, 23, h - 15, 24, h - 8), fill=C((40, 70, 120)))
        hl(d, 14, 18, h - 17, (40, 40, 40))
        rect(d, w - 18, 12, w - 4, 24, (150, 120, 90))             # 挂工具的板
        for xx in range(w - 16, w - 5, 3):
            vl(d, xx, 14, 14 + int(R(xx, 8) * 7), (120, 124, 130))
        rect(d, w - 22, h - 9, w - 14, h - 3, (130, 120, 110))     # 打气筒 / 工具箱
    elif kind == 'grocery':
        for row, yy in enumerate((9, 17)):
            hl(d, 2, w - 3, yy, (130, 96, 64))
            for xx in range(3, w - 4, 3):
                c = ((200, 60, 50), (230, 190, 70), (70, 130, 80), (70, 100, 170), (230, 230, 220))[int(R(row, xx) * 5)]
                rect(d, xx, yy - 4 + int(R(row, xx, 1) * 2), xx + 1, yy - 1, c)
        for xx in range(4, w - 6, 5):                              # 一串串挂着的小包装
            for k in range(5):
                px(d, xx, 2 + k * 2, ((220, 60, 60), (240, 200, 60), (60, 140, 200))[(k + xx) % 3])
        for xx in range(1, w - 7, 7):
            rect(d, xx, h - 10, xx + 6, h - 2, (226, 214, 180))
            hl(d, xx + 1, xx + 5, h - 11, ((246, 244, 236), (230, 190, 70), (200, 120, 60))[int(R(xx, 9) * 3)])
    elif kind == 'pharmacy':
        for row, yy in enumerate((8, 15)):
            rect(d, 2, yy - 6, w - 3, yy, (226, 230, 226))
            for xx in range(3, w - 4, 3):
                c = ((140, 80, 40), (60, 90, 160), (240, 240, 236), (60, 140, 90))[int(R(row, xx) * 4)]
                rect(d, xx, yy - 4, xx + 1, yy - 1, c)
            hl(d, 2, w - 3, yy, (160, 170, 166))
        rect(d, 3, h - 12, w - 4, h - 3, (130, 150, 150))
        hl(d, 3, w - 4, h - 12, (200, 220, 220))
    elif kind == 'photo':
        rect(d, 4, 3, w - 5, h - 6, (140, 170, 200))              # 画的布景（蓝天 + 一棵棕榈）
        rect(d, 4, h - 14, w - 5, h - 6, (110, 150, 100))
        vl(d, w // 2, 8, h - 10, (110, 90, 70))
        for k in range(-4, 5, 2):
            d.line((w // 2, 8, w // 2 + k, 11), fill=C((60, 110, 60)))
        for xx in (2, w - 9):                                      # 墙上的相框
            rect(d, xx, 6, xx + 6, 13, (60, 50, 40))
            rect(d, xx + 1, 7, xx + 5, 12, (200, 180, 160))
            px(d, xx + 3, 9, (90, 70, 60))
    elif kind == 'tailor':
        rect(d, 4, h - 14, 22, h - 11, (130, 96, 64))              # 案子 + 缝纫机
        rect(d, 8, h - 20, 16, h - 15, (30, 30, 34))
        hl(d, 8, 16, h - 20, (90, 90, 96))
        px(d, 9, h - 18, (200, 170, 80))
        for xx in range(26, w - 4, 4):                             # 挂着的衬衫
            c = ((236, 236, 230), (150, 180, 210), (200, 190, 150))[int(R(xx, 10) * 3)]
            rect(d, xx, 4, xx + 3, 13, c)
            px(d, xx - 1, 5, c)
            px(d, xx + 4, 5, c)
    elif kind == 'stair':
        rect(d, 0, 0, w - 1, h - 1, (110, 100, 88))
        for k in range(10):                                        # 往上的楼梯
            y = h - 3 - k * 3
            hl(d, 2 + k * 2, w - 3, y, (150, 138, 120))
            hl(d, 2 + k * 2, w - 3, y + 1, (90, 82, 72))
        px(d, w // 2, 3, (250, 240, 200))                          # 灯泡
        vl(d, w // 2, 0, 2, (60, 56, 52))
    elif kind == 'shutter':
        for y in range(0, h):                                      # 卷闸门（瓦楞铁）
            c = (162, 168, 160) if y % 3 else (128, 134, 128)
            if y % 3 == 1:
                c = (178, 184, 176)
            hl(d, 0, w - 1, y, c)
        rect(d, 0, 0, w - 1, 3, (110, 114, 110))
        rect(d, w // 2 - 1, h - 6, w // 2 + 1, h - 4, (60, 56, 52))   # 挂锁
        for i in range(3):                                         # 撕了一半的海报（色块）
            x0_ = int(R(i, 11) * (w - 10))
            y0_ = int(4 + R(i, 12) * (h - 16))
            c = ((220, 200, 120), (200, 90, 80), (120, 170, 200))[i % 3]
            rect(d, x0_, y0_, x0_ + 6, y0_ + 8, c)
            px(d, x0_ + 6, y0_ + 8, back)
            px(d, x0_ + 5, y0_ + 8, back)
            hl(d, x0_ + 1, x0_ + 5, y0_ + 3, dk(c, 0.7))
        im = A._grade(im, sat=0.8, val=1.0)
        return im                                                   # 卷闸门在外面，不压屋里的阴影
    elif kind == 'godown':
        for x in range(w):                                         # 两扇大木门（竖板 + 铁钉）
            c = (126, 88, 58) if x % 4 else (100, 70, 46)
            vl(d, x, 0, h - 1, c)
        vl(d, w // 2, 0, h - 1, (60, 40, 28))
        for y in (4, h // 2, h - 5):
            for x in range(1, w - 1, 3):
                px(d, x, y, (60, 56, 52))
        rect(d, w // 2 + 1, 2, w - 2, h - 2, (52, 40, 34))           # 一扇半开（里面暗）
        im = A._grade(im, sat=0.9, val=1.0)
        return im
    elif kind == 'bank':
        rect(d, 2, h - 14, w - 3, h - 4, (130, 110, 84))           # 柜台
        hl(d, 2, w - 3, h - 14, (170, 150, 116))
        for x in range(0, w):                                      # 铁栅门（菱形格）
            for y in range(2, h):
                if (x + y) % 6 == 0 or (x - y) % 6 == 0:
                    px(d, x, y, (50, 54, 56))
        hl(d, 0, w - 1, 2, (70, 74, 76))
    shade_interior(im)
    return im


# ============================================================ 近景：背景里的行人（比主角小一圈、颜色压灰）
KURTA = [(236, 232, 220), (200, 216, 230), (230, 214, 170), (186, 206, 176), (220, 192, 182)]
SHIRTS = [(150, 170, 200), (200, 186, 150), (236, 232, 222), (130, 150, 120), (190, 120, 100), (120, 140, 170)]
PANTS = [(70, 70, 80), (110, 100, 90), (60, 70, 96), (150, 140, 120)]
SARIS = [(200, 50, 70), (60, 120, 170), (220, 150, 40), (110, 70, 150), (70, 140, 100), (230, 110, 120)]
LUNGI = [(70, 110, 160), (60, 120, 90), (150, 70, 80)]


def person(d, x, base, kind, seed, h=36, face=1, ground=KERB_Y - 1):
    """一个路人（x = 中线，base = 脚底 y；sit 时 base = 凳面 y、ground = 地面）。光从左边来：身子左边亮、右边暗。
    kind = kurta 长衫+睡裤 / shirt 衬衫长裤 / dhoti 背心+围裤（露小腿）/ sari 纱丽 / porter 红衣搬运工（头顶行李）/
    kid 小孩 / umbrella 撑黑伞的老人 / basket 头顶筐的妇女 / pray 合掌的妇女 / sit 坐着喝茶 / squat 蹲着。"""
    R = lambda *k: hash01(seed, *k)  # noqa: E731
    sk = SKIN[int(R(1) * len(SKIN))]
    skd = dk(sk, 0.78)
    if kind == 'kid':
        h = 24
    top = base - h
    hx = x - 2
    fem = kind in ('sari', 'basket', 'pray')

    def head(y):
        rect(d, hx, y, hx + 3, y + 4, sk)
        vl(d, hx + 3, y + 1, y + 4, skd)
        hl(d, hx, hx + 3, y, HAIR)
        px(d, hx + (3 if face < 0 else 0), y + 1, HAIR)
        px(d, hx + (2 if face > 0 else 1), y + 2, dk(sk, 0.55))      # 眼睛
        if fem:                                                    # 发髻 / 长辫
            bx = hx - 1 if face > 0 else hx + 4
            rect(d, bx, y + 1, bx, y + 3, HAIR)
            vl(d, hx + (0 if face > 0 else 3), y + 1, y + 6, HAIR)

    def torso(y, col, rows=10, sleeve='short'):
        rect(d, x - 3, y, x + 2, y + rows - 1, col)
        vl(d, x - 3, y, y + rows - 1, lt(col, 0.12))
        vl(d, x + 2, y, y + rows - 1, dk(col, 0.82))
        for (ax, c) in ((x - 4, lt(col, 0.05)), (x + 3, dk(col, 0.75))):   # 胳膊：袖子 + 手
            n_sl = 3 if sleeve == 'short' else (rows - 1 if sleeve == 'long' else 0)
            for k in range(rows - 1):
                px(d, ax, y + 1 + k, c if k < n_sl else (sk if ax < x else skd))
            px(d, ax, y + rows, sk if ax < x else skd)

    if kind == 'sit':                                              # 坐在长凳上喝茶：base = 凳面
        col = SHIRTS[int(R(2) * len(SHIRTS))]
        lg = LUNGI[int(R(3) * len(LUNGI))]
        head(base - 18)
        rect(d, x - 2, base - 13, x + 2, base - 4, col)
        vl(d, x + 2, base - 13, base - 4, dk(col, 0.8))
        for k in range(6):                                         # 大腿（往前平伸，格子围裤，膝盖鼓一点）
            xx = x - 2 * face + k * face if face > 0 else x + 2 - k
            for yy in (base - 3, base - 2, base - 1):
                px(d, xx, yy, lg if (xx + yy) % 2 else (230, 226, 214))
        px(d, x + 4 * face, base - 4, lg)
        sx = x + 4 * face
        vl(d, sx, base, ground - 1, sk)                             # 小腿
        px(d, sx, ground, dk(sk, 0.6))
        px(d, sx + face, ground, dk(sk, 0.6))
        vl(d, x + 3 * face, base - 12, base - 8, sk)                # 端杯子的手（举到嘴边）
        px(d, x + 3 * face, base - 14, (176, 100, 64))
        px(d, x + 3 * face, base - 13, sk)
        return
    if kind == 'squat':
        col = SHIRTS[int(R(2) * len(SHIRTS))]
        head(base - 16)
        rect(d, x - 3, base - 11, x + 3, base - 4, col)
        rect(d, x - 3, base - 4, x + 3, base - 1, (230, 226, 214))
        px(d, x - 3, base - 1, sk)
        px(d, x + 3, base - 1, skd)
        return
    head(top)
    ty = top + 5
    if fem:
        sari = SARIS[int(R(3) * len(SARIS))]
        bord = ((230, 196, 80), (236, 230, 214), (180, 40, 40))[int(R(4) * 3)]
        blouse = dk(sari, 0.7) if R(5) < 0.5 else (226, 196, 120)
        torso(ty, blouse, rows=5)
        hl(d, x - 3, x + 2, ty + 5, sk)                             # 露一截腰
        for y in range(ty + 6, base):                              # 裙摆往下微微张开，前面几道褶
            u = (y - ty - 6) / max(1, base - ty - 7)
            half = 3 + int(u * 1.5)
            hl(d, x - half, x + half - 1, y, sari)
            px(d, x - half, y, lt(sari, 0.12))
            px(d, x + half - 1, y, dk(sari, 0.8))
            if (y - ty) % 2 == 0:
                px(d, x + face, y, dk(sari, 0.86))
        hl(d, x - 4, x + 3, base - 2, bord)
        hl(d, x - 4, x + 3, base - 1, dk(bord, 0.8))
        for k in range(11):                                        # 纱丽的一角斜搭过肩
            xx = x - 3 + k // 2 if face > 0 else x + 2 - k // 2
            px(d, xx, ty + k, lt(sari, 0.22))
            if k % 3 == 0:
                px(d, xx + (1 if face > 0 else -1), ty + k, bord)
        if kind == 'pray':
            rect(d, x + 2 * face, ty + 2, x + 2 * face + face, ty + 4, sk)
        if kind == 'basket':
            d.ellipse((x - 6, top - 5, x + 5, top), fill=C((176, 140, 80)))
            hl(d, x - 5, x + 4, top - 5, (206, 170, 100))
            for k in range(4):
                px(d, x - 4 + k * 3, top - 6, ((90, 150, 60), (230, 120, 40), (210, 60, 40), (90, 150, 60))[k])
            vl(d, x + 3, top - 1, ty + 1, skd)
        return
    if kind == 'kid':
        torso(ty, SHIRTS[int(R(2) * len(SHIRTS))], rows=7)
        rect(d, x - 3, ty + 7, x + 2, ty + 10, (70, 80, 100))       # 短裤
        for xx in (x - 3, x + 1):
            vl(d, xx, ty + 11, base - 1, sk)
            vl(d, xx + 1, ty + 11, base - 1, skd)
        return
    walk = R(7) < 0.5
    if kind in ('kurta', 'umbrella'):
        col = KURTA[int(R(2) * len(KURTA))] if kind == 'kurta' else (236, 232, 220)
        torso(ty, col, rows=10, sleeve='long')
        for y in range(ty + 10, ty + 16):                          # 长衫下摆到膝盖
            hl(d, x - 3, x + 2, y, col)
            px(d, x + 2, y, dk(col, 0.82))
        hl(d, x - 3, x + 2, ty + 15, dk(col, 0.88))
        legc = (232, 228, 216)
        for y in range(ty + 16, base):
            o = (1 if walk and y > base - 6 else 0)
            hl(d, x - 3 - o, x - 2 - o, y, legc)
            hl(d, x + o, x + 1 + o, y, dk(legc, 0.84))
        hl(d, x - 3, x - 2, base - 1, (90, 70, 50))
        hl(d, x, x + 1, base - 1, (90, 70, 50))
    elif kind in ('dhoti', 'porter'):
        if kind == 'dhoti':
            torso(ty, (238, 236, 228), rows=10, sleeve='none')
        else:
            torso(ty, (196, 46, 40), rows=10, sleeve='short')
            px(d, x - 4, ty + 4, (226, 186, 80))                    # 铜臂章
        dh = (236, 232, 222)
        for y in range(ty + 10, base - 4):                         # 围裤：到小腿，左亮右暗，一道斜褶
            u = (y - ty - 10) / max(1, base - ty - 14)
            half = 3 + (1 if u > 0.5 else 0)
            hl(d, x - half, x + half - 1, y, dh)
            px(d, x + half - 1, y, dk(dh, 0.82))
            px(d, x - 2 + int(u * 3), y, dk(dh, 0.88))
        for xx in (x - 3, x + 1):                                  # 小腿 + 拖鞋
            vl(d, xx, base - 4, base - 2, sk)
            vl(d, xx + 1, base - 4, base - 2, skd)
            hl(d, xx, xx + 1, base - 1, (80, 60, 44))
    else:                                                          # shirt：衬衫 + 长裤 + 鞋
        col = SHIRTS[int(R(2) * len(SHIRTS))]
        pc = PANTS[int(R(6) * len(PANTS))]
        torso(ty, col, rows=10, sleeve='short' if R(8) < 0.6 else 'long')
        hl(d, x - 3, x + 2, ty + 10, dk(pc, 0.8))                  # 腰带
        for y in range(ty + 11, base):
            o = (1 if walk and y > base - 7 else 0)
            hl(d, x - 3 - o, x - 1 - o, y, pc)
            hl(d, x + o, x + 2 + o, y, dk(pc, 0.82))
        hl(d, x - 3, x - 1, base - 1, (40, 34, 32))
        hl(d, x, x + 2, base - 1, (40, 34, 32))
    if kind == 'porter':                                           # 头顶的行李箱 + 举着扶住的手
        rect(d, x - 5, top - 5, x + 5, top - 1, (110, 70, 44))
        hl(d, x - 5, x + 5, top - 5, (150, 104, 66))
        vl(d, x - 5, top - 4, top - 1, (90, 56, 36))
        px(d, x, top - 6, (60, 50, 40))
        vl(d, x + 3, top - 1, ty + 1, skd)
    elif kind == 'umbrella':                                       # 黑伞（加尔各答的男人大太阳天也打）
        cy = top - 3
        for xx in range(-7, 8):
            yy = cy - int(round(4 * math.sqrt(max(0, 1 - (xx / 7.5) ** 2))))
            vl(d, x + xx, yy, cy, (40, 38, 44))
            if xx % 3 == 0:
                px(d, x + xx, cy + 1, (40, 38, 44))
        hl(d, x - 4, x + 1, cy - 4, (90, 90, 100))
        vl(d, x, cy, ty + 3, (60, 50, 40))


# 背景里的人：(x, 脚底 y, 样式, 朝向, 身高)。主角 ~46 px，路人 30–37 px（站在后面的人行道上，算远一点）
CROWD = [
    (22, 145, 'porter', 1, 36), (36, 144, 'sari', -1, 33), (108, 145, 'kurta', -1, 35), (122, 144, 'umbrella', 1, 34),
    (134, 145, 'basket', -1, 33),
    (88, 144, 'kurta', -1, 34), (162, 145, 'kid', 1, 0), (184, 144, 'dhoti', -1, 35),
    (310, 145, 'shirt', 1, 35), (322, 144, 'sari', -1, 32),
    (426, 145, 'shirt', -1, 35),
    (470, 140, 'dhoti', 1, 31), (520, 140, 'kurta', 1, 31), (566, 140, 'sari', -1, 30), (592, 140, 'shirt', -1, 31),
    (692, 144, 'shirt', -1, 35), (806, 145, 'squat', -1, 0),
    (818, 145, 'kurta', 1, 35), (832, 145, 'basket', -1, 33), (846, 144, 'kid', 1, 0), (876, 145, 'pray', 1, 33),
    (962, 145, 'umbrella', 1, 34), (1040, 144, 'basket', -1, 32),
    (1062, 145, 'shirt', 1, 35), (1072, 144, 'kurta', -1, 34), (1160, 145, 'dhoti', -1, 34),
    (1252, 145, 'umbrella', -1, 34), (1270, 145, 'porter', -1, 35),
]
SITTERS = [(388, 134, 1), (398, 134, -1), (410, 134, 1)]           # 茶摊长凳上坐着的（x, 凳面 y, 朝向）


def crowd_layer():
    """路人单独画一层，压灰（往空气色混 28 %、饱和度 0.7），再贴回近景：读起来是背景，不会被当成可以说话的人。"""
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    for i, (x, base, kind, face, h) in enumerate(CROWD):
        person(d, x, base, kind, 300 + i, h=h or 36, face=face)
    for i, (x, base, face) in enumerate(SITTERS):
        person(d, x, base, 'sit', 400 + i, face=face)
    lay = A._grade(lay, sat=0.72, val=1.0)
    return haze_img(lay, 0.26, 0.26, col=(200, 192, 176))


# ============================================================ 近景：临街的殖民时期老楼
# floors：每层窗（y 窗顶、h 窗高、n 扇、w 宽、kind 窗型、hood 窗楣、fan 气窗玻璃、states 每扇的状态
#         c 关 / h 开一扇 / o 全开 / b 坏了 / d 空洞、bal 'iron' 这一层的通长铁阳台、xs 手排 x）
# shops：一楼铺面 (x0, x1, 种类)；sign：(x0, x1, 底色, 色条色, 图标)；bricks：露砖 (cx, cy, rx, ry)；
# saplings：墙缝里的小树 (x, y, 大小)；stains：霉斑道子的条数
BLDS = [
    dict(name='spice', x=B_SPICE, top=34, wall=(214, 168, 98), sh=(186, 138, 74), hi=(232, 198, 136),
         trim=(240, 228, 200), shutter=(56, 104, 82), parapet='baluster', seed=11,
         floors=[dict(y=44, h=20, n=4, w=9, kind='arch', fan='color', states='chco'),
                 dict(y=72, h=23, n=4, w=9, kind='rect', hood='flat', states='ohcb', bal='iron')],
         gf=109, shops=[(200, 296, 'spice')], sign=(206, 290, (150, 44, 32), (240, 204, 96), 'chili'),
         bricks=[(291, 58, 5, 7), (205, 100, 5, 3), (240, 40, 4, 2)], saplings=[(297, 36, 1.0), (201, 66, 0.7)], stains=8),
    dict(name='narrow', x=B_NARROW, top=58, wall=(196, 112, 82), sh=(166, 88, 64), hi=(214, 140, 108),
         trim=(226, 206, 180), shutter=(70, 96, 120), parapet='solid', seed=12,
         floors=[], woodbal=[(304, 327, 66, 92)],
         gf=104, shops=[(304, 328, 'shutter')], tin=(301, 331, 96), bricks=[(318, 98, 4, 2)], stains=4),
    dict(name='chai', x=B_CHAI, top=42, wall=(128, 178, 180), sh=(98, 146, 152), hi=(164, 204, 202),
         trim=(234, 232, 220), shutter=(130, 84, 56), parapet='solid', urns=True, seed=13,
         floors=[dict(y=51, h=19, n=3, w=10, kind='seg', states='hcb'),
                 dict(y=78, h=19, n=3, w=10, kind='rect', hood='pedi', states='coh')],
         gf=110, shops=[(336, 420, 'sweets')], sign=(342, 414, (232, 222, 196), (190, 60, 56), 'pot'),
         bricks=[(414, 66, 6, 8), (340, 92, 4, 3)], saplings=[(420, 40, 0.8)], stains=7),
    dict(name='grand', x=B_GRAND, top=46, wall=(226, 214, 190), sh=(196, 182, 158), hi=(240, 232, 214),
         trim=(244, 238, 222), shutter=(64, 110, 90), parapet='baluster', seed=14,
         floors=[dict(y=55, h=19, n=7, w=8, kind='rect', hood='pedi', states='chcocdh'),
                 dict(y=82, h=17, n=7, w=8, kind='rect', states='ocochco', bal='iron')],
         gf=107, shops=[], pilasters=True, bricks=[(598, 70, 4, 6), (430, 100, 4, 3)], stains=10,
         colonnade=['saris', 'photo', 'pharmacy', 'shutter', 'tailor', 'grocery', 'saris', 'shutter']),
    dict(name='pink', x=B_PINK, top=36, wall=(214, 148, 128), sh=(184, 118, 102), hi=(232, 178, 158),
         trim=(242, 226, 210), shutter=(60, 100, 86), parapet='solid', pedi=True, seed=15,
         floors=[dict(y=44, h=21, n=4, w=9, kind='rect', hood='flat', states='ohcc'),
                 dict(y=74, h=22, n=1, w=10, kind='rect', states='o', xs=[658])],
         woodbal=[(611, 641, 70, 96), (683, 713, 70, 96)],
         gf=106, shops=[(608, 690, 'brass'), (694, 718, 'stair')], sign=(612, 686, (40, 62, 98), (232, 196, 90), 'pot'),
         bricks=[(708, 52, 6, 5), (622, 100, 3, 2)], saplings=[(720, 38, 0.9)], stains=8),
    dict(name='green', x=B_GREEN, top=64, wall=(156, 190, 150), sh=(124, 160, 120), hi=(184, 212, 176),
         trim=(236, 236, 222), shutter=(150, 90, 60), parapet='solid', seed=16, shed=(736, 800, 52),
         floors=[dict(y=73, h=20, n=3, w=10, kind='seg', hood='chajja', states='hoc')],
         gf=106, shops=[(726, 808, 'cycle')], tin=(723, 811, 98), sign=None,
         bricks=[(800, 82, 5, 4)], stains=5),
    dict(name='slim', x=B_SLIM, top=48, wall=(230, 210, 150), sh=(200, 178, 118), hi=(242, 228, 180),
         trim=(244, 238, 222), shutter=(66, 110, 92), parapet='solid', seed=17,
         floors=[dict(y=57, h=18, n=1, w=10, kind='arch', states='h', xs=[827]),
                 dict(y=83, h=16, n=2, w=7, kind='rect', states='co')],
         gf=104, shops=[(816, 848, 'stair')], stains=4),
    dict(name='tall', x=B_TALL, top=48, wall=(160, 168, 172), sh=(132, 140, 146), hi=(186, 192, 194),
         trim=(232, 232, 226), shutter=(66, 100, 88), parapet='solid', seed=18,
         floors=[dict(y=58, h=20, n=4, w=9, kind='rect', hood='chajja', states='chcd'),
                 dict(y=86, h=15, n=4, w=9, kind='rect', states='ocho', bal='iron')],
         gf=109, shops=[(950, 1000, 'bank'), (1004, 1050, 'grocery')],
         sign=(1008, 1046, (230, 200, 70), (60, 60, 120), 'bars'), bricks=[(1048, 70, 4, 5)], stains=9),
    dict(name='old', x=B_OLD, top=30, wall=(206, 178, 112), sh=(170, 142, 86), hi=(226, 204, 148),
         trim=(232, 220, 190), shutter=(62, 98, 80), parapet='broken', pedi=True, seed=19,
         floors=[dict(y=39, h=22, n=4, w=11, kind='arch', fan='color', states='bdhb'),
                 dict(y=70, h=24, n=4, w=10, kind='rect', hood='flat', states='ocbo', bal='iron')],
         gf=107, shops=[(1058, 1124, 'shutter'), (1128, 1168, 'stair')],
         bricks=[(1066, 50, 8, 9), (1150, 60, 10, 6), (1106, 98, 6, 3), (1162, 30, 5, 4)],
         saplings=[(1088, 29, 1.2), (1168, 66, 0.9), (1112, 63, 0.6)], stains=12),
    dict(name='edge', x=B_EDGE, top=40, wall=(184, 166, 182), sh=(154, 136, 154), hi=(206, 192, 204),
         trim=(238, 232, 230), shutter=(70, 96, 120), parapet='baluster', seed=20,
         floors=[dict(y=49, h=18, n=2, w=9, kind='seg', states='ch'),
                 dict(y=75, h=19, n=2, w=9, kind='rect', states='oc', bal='iron')],
         gf=105, shops=[(1236, 1280, 'shutter')], bricks=[(1270, 90, 5, 4)], stains=5),
]


def _win_xs(x0, x1, n, w):
    span = x1 - x0 + 1
    gap = (span - n * w) / (n + 1)
    return [int(round(x0 + gap * (i + 1) + w * i)) for i in range(n)]


def draw_colonnade(im, b):
    """大楼一楼的柱廊（战斗段的背景）：廊子里是深影，后墙一排铺面（纱丽、照相馆、药房、卷闸门、裁缝、杂货……），
    前面一排圆柱（柱头、柱础，左亮右暗，影子落在后墙上），廊子地面高出人行道一级。"""
    x0, x1 = b['x']
    xr = x1 - 1
    gf, trim, wall, seed = b['gf'], b['trim'], b['wall'], b['seed']
    bays = b['colonnade']
    ix0, ix1 = x0 + 3, xr - 3
    w, hgt = ix1 - ix0 + 1, BASE_Y - gf
    back = A._new(w, hgt)
    bd = ImageDraw.Draw(back)
    rect(bd, 0, 0, w - 1, hgt - 1, mix(wall, (120, 110, 100), 0.35))
    n = len(bays)
    for i, kind in enumerate(bays):
        a, bb = int(i * w / n), int((i + 1) * w / n)
        sim = shop_img(kind, bb - a - 4, hgt - 9, seed * 5 + i)
        back.alpha_composite(sim, (a + 2, 5))
        bd = ImageDraw.Draw(back)
        hl(bd, a + 1, bb - 2, 4, mix(trim, (90, 80, 70), 0.3))      # 每家的门楣
    rect(bd, 0, 0, w - 1, 3, dk(wall, 0.55))                        # 廊子顶（楼板底）+ 梁
    for x in range(0, w, 9):
        vl(bd, x, 0, 3, dk(wall, 0.45))
    for y in range(hgt - 4, hgt):                                  # 廊子地面（黑白花砖）
        for x in range(w):
            c = (206, 200, 186) if (x // 3 + y) % 2 else (150, 144, 134)
            px(bd, x, y, c)
    shade_interior(back, top_k=0.55, bot_k=0.9, cool=(0.95, 0.97, 1.05))
    im.alpha_composite(back, (ix0, gf))
    d = ImageDraw.Draw(im)
    hl(d, x0, xr, BASE_Y - 1, mix(trim, (150, 144, 134), 0.4))       # 台阶边
    xs = [int(round(x0 + 2 + (xr - 7 - (x0 + 2)) * k / n)) for k in range(n + 1)]
    for cx in xs:
        mul_box(im, (cx + 5, gf + 3, cx + 8, BASE_Y - 3), (0.74, 0.76, 0.86))   # 柱子投在后墙上的影
        d = ImageDraw.Draw(im)
        for y in range(gf, BASE_Y - 1):
            for k, c in enumerate((lt(trim, 0.3), trim, trim, dk(trim, 0.86), dk(trim, 0.72))):
                px(d, cx + k, y, c)
        rect(d, cx - 1, gf, cx + 5, gf + 2, lt(trim, 0.2))           # 柱头
        hl(d, cx - 1, cx + 5, gf + 3, dk(trim, 0.75))
        rect(d, cx - 1, BASE_Y - 5, cx + 5, BASE_Y - 2, trim)        # 柱础
        hl(d, cx - 1, cx + 5, BASE_Y - 5, lt(trim, 0.3))
        vl(d, cx + 5, BASE_Y - 4, BASE_Y - 2, dk(trim, 0.7))


def facade(im, b):
    """一栋临街楼的正面：灰泥墙（斑驳）+ 露砖 + 檐口 / 女儿墙 + 每层的窗 / 腰线 / 阳台 + 一楼铺面（铺子、壁柱、门楣、招牌）
    + 霉斑道子 + 墙脚泥灰 + 墙缝小树。光从左上来：凸出来的东西影子落在右下。"""
    x0, x1 = b['x']
    xr = x1 - 1
    wall, sh, hi, trim, seed = b['wall'], b['sh'], b['hi'], b['trim'], b['seed']
    top = b['top']
    wall_sh = dk(wall, 0.72)
    plaster(im, (x0, top, xr, BASE_Y - 1), wall, sh, hi, seed)
    for (cx, cy, rx, ry) in b.get('bricks', []):
        brick_patch(im, cx, cy, rx, ry, seed * 7 + cx, clip=(x0, top + 4, xr, BASE_Y - 1))
    d = ImageDraw.Draw(im)
    # 屋顶：女儿墙 + 檐口
    pk = b.get('parapet', 'solid')
    if pk == 'baluster':
        parapet(im, x0, xr, top - 11, 'baluster', trim, wall, seed)
    else:
        parapet(im, x0, xr, top - 7, pk, trim, wall, seed)
    if b.get('pedi'):                                              # 正中一块山花（三角楣 + 圆形盲窗）
        cx = (x0 + x1) // 2
        hw = min(18, (x1 - x0) // 4)
        ptop = top - 7 - hw // 2 - 2
        d = ImageDraw.Draw(im)
        d.polygon([(cx - hw, top - 6), (cx + hw, top - 6), (cx, ptop)], fill=C(wall))
        d.line([(cx - hw, top - 6), (cx, ptop), (cx + hw, top - 6)], fill=C(trim))
        d.line([(cx - hw + 2, top - 7), (cx, ptop + 1)], fill=C(lt(trim, 0.4)))
        d.line([(cx, ptop + 1), (cx + hw - 2, top - 7)], fill=C(dk(wall, 0.8)))
        d.ellipse((cx - 3, top - 13, cx + 3, top - 8), fill=C(trim))
        d.ellipse((cx - 2, top - 12, cx + 2, top - 9), fill=C(dk(wall, 0.6)))
    if b.get('urns'):
        for ux in (x0 + 2, xr - 2):
            urn(d, ux, top - 7, trim)
    cornice(im, x0 - 1, x1, top, trim, wall, depth=3, dentils=True)
    # 每层的窗
    for fi, f in enumerate(b['floors']):
        xs = f.get('xs') or _win_xs(x0 + 4, xr - 4, f['n'], f['w'])
        for i, wx in enumerate(xs):
            st = dict(c='closed', h='half', o='open', b='broken', d='dark')[f['states'][i % len(f['states'])]]
            window(im, wx, f['y'], f['w'], f['h'], f['kind'], b['shutter'], trim, wall_sh, st, seed * 10 + fi * 5 + i,
                   f.get('fan', 'plain'), f.get('hood'))
        yb = f['y'] + f['h']
        if f.get('bal') == 'iron':
            iron_balcony(im, x0 + 3, xr - 3, yb, rail_h=9 if f['h'] > 18 else 7, trim=trim, seed=seed + fi)
        elif fi < len(b['floors']) - 1:
            cornice(im, x0, xr, yb + 4, trim, wall, depth=2, dentils=False)
    if b.get('pilasters'):                                          # 大楼：通高的壁柱（窗与窗之间）
        f = b['floors'][0]
        xs = _win_xs(x0 + 4, xr - 4, f['n'], f['w'])
        for i in range(len(xs) + 1):
            px_ = (x0 + 1) if i == 0 else ((xs[i - 1] + f['w'] + xs[i]) // 2 - 2 if i < len(xs) else xr - 4)
            pilaster(im, px_, top + 5, b['gf'] - 6, trim)
    for (wx0, wx1, yt, yf) in b.get('woodbal', []):
        wood_balcony(im, wx0, wx1, yt, yf, seed=seed)
    d = ImageDraw.Draw(im)
    # 一楼：门楣（通长的梁）+ 招牌 + 铺面 + 壁柱
    gf = b['gf']
    rect(d, x0, gf - 3, xr, gf - 1, trim)
    hl(d, x0, xr, gf - 3, lt(trim, 0.4))
    shops = b.get('shops') or []
    for (sx0, sx1, kind) in shops:
        sx0, sx1 = max(sx0, x0 + 4), min(sx1, xr - 3)
        sim = shop_img(kind, sx1 - sx0, BASE_Y - gf, seed * 3 + sx0)
        im.alpha_composite(sim, (sx0, gf))
        d = ImageDraw.Draw(im)
        vl(d, sx0, gf, BASE_Y - 1, dk(wall, 0.55))                  # 门洞左沿的影
        hl(d, sx0, sx1 - 1, gf, dk(wall, 0.5))
        hl(d, sx0, sx1 - 1, BASE_Y - 1, mix(trim, (150, 144, 134), 0.5))   # 门槛石
    d = ImageDraw.Draw(im)
    if shops:
        piers = [x0, xr - 3] + [s1[1] for s1, s2 in zip(shops, shops[1:])]   # 两头 + 两家铺子之间（4 px 宽）
        for pxx in sorted(set(piers)):
            pxx = min(max(pxx, x0), xr - 3)
            rect(d, pxx, gf - 1, pxx + 3, BASE_Y - 1, mix(wall, trim, 0.4))
            vl(d, pxx, gf - 1, BASE_Y - 1, lt(mix(wall, trim, 0.4), 0.3))
            vl(d, pxx + 3, gf - 1, BASE_Y - 1, mix(wall, sh, 0.8))
    if b.get('colonnade'):
        draw_colonnade(im, b)
    mul_box(im, (x0, gf, xr, gf + 2), (0.8, 0.82, 0.9))                 # 门楣下的影
    if b.get('sign'):
        sx0, sx1, bg, fg, ic = b['sign']
        signboard(im, sx0, gf - 12, sx1, gf - 5, bg, fg, ic, seed)
    if b.get('tin'):
        tx0, tx1, ty = b['tin']
        tin_awning(im, tx0, tx1, ty, depth=5, seed=seed)
    # 霉斑道子：屋檐下、窗台下往下淌
    for i in range(b.get('stains', 6)):
        sx = int(hrange(x0 + 2, xr - 2, seed, i, 61))
        if b['floors'] and hash01(seed, i, 62) < 0.6:
            f = b['floors'][int(hash01(seed, i, 63) * len(b['floors']))]
            sy = f['y'] + f['h'] + 4
        else:
            sy = top + 6
        stain(im, sx, sy, int(hrange(6, 22, seed, i, 64)), seed * 31 + i, width=1 + int(hash01(seed, i, 65) * 2),
              ymax=gf - 4)
    grime(im, x0, xr, BASE_Y - 1, h=7)
    d = ImageDraw.Draw(im)
    for (sx, sy, s) in b.get('saplings', []):
        sapling(d, sx, sy, seed + sx, s)
    vl(d, xr, top + 4, BASE_Y - 1, dk(wall, 0.84))                   # 楼角（右边背光的一条）


# ============================================================ 近景：火车站（红砖站房一角 + 大拱门出口 + 钟楼）
ST_BR, ST_BRD, ST_BRH, ST_MO = (168, 80, 60), (140, 64, 48), (186, 102, 76), (182, 134, 110)
ST_STONE, ST_STONE_S, ST_STONE_HI = (226, 210, 180), (192, 174, 146), (240, 230, 208)
ARCH = (58, 28, 92)           # 大拱门：中线 x、半径、起拱线 y（拱顶 y 64，门洞到 137）


def brick_fill(im, box, seed, cols=(ST_BR, ST_BRD, ST_BRH), mortar=ST_MO, mort_k=0.5):
    """一大片红砖墙（numpy）：砖 5×2 + 1 px 灰缝错缝，每块砖的颜色按种子挑；灰缝和砖的对比压低（mort_k）。"""
    x0, y0, x1, y1 = box
    a = np.array(im)
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    row = ys // 3
    bx = (xs + (row % 2) * 3) // 6
    hsh = (np.sin(bx * 12.9898 + row * 78.233 + seed) * 43758.5453) % 1.0
    c0, c1, c2 = [np.array(c, np.uint8) for c in cols]
    out = np.where((hsh < 0.6)[..., None], c0, np.where((hsh < 0.82)[..., None], c1, c2))
    mo = np.array(mix(cols[0], mortar, mort_k), np.uint8)
    joint = (ys % 3 == 2) | ((xs + (row % 2) * 3) % 6 == 5)
    out[joint] = mo
    top = ys % 3 == 0
    out[top & ~joint] = np.clip(out[top & ~joint].astype(np.int16) + 8, 0, 255).astype(np.uint8)
    a[y0:y1 + 1, x0:x1 + 1, :3] = out
    a[y0:y1 + 1, x0:x1 + 1, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))


def station_interior(w, h):
    """拱门里的车站大厅（局部坐标）：钢屋架、发车牌、挂钟、停着的褐红色车厢、尽头站台的亮口、往外走的人潮（剪影）。"""
    im = A._new(w, h)
    d = ImageDraw.Draw(im)
    rect(d, 0, 0, w - 1, h - 1, (104, 96, 90))
    cx = w // 2
    rect(d, cx - 6, h - 40, cx + 8, h - 14, (206, 196, 168))       # 尽头站台外的亮光
    rect(d, cx - 6, h - 22, cx + 8, h - 14, (176, 168, 150))
    for k in range(7):                                             # 钢屋架（三角桁架往里收）
        y = 6 + k * 3
        hl(d, 0, w - 1, y, (78, 72, 70))
        for x in range(k % 2 * 4, w, 8):
            d.line((x, y, x + 4, y + 3), fill=C((78, 72, 70)))
    for x in range(-10, w + 10, 9):                                # 屋顶天窗透下来的几道光
        d.line((x, 26, x + 8, h - 20), fill=C((122, 114, 106)))
    # 停着的车厢（褐红色，一排窗）
    rect(d, 0, h - 40, cx - 14, h - 18, (126, 52, 42))
    hl(d, 0, cx - 14, h - 41, (90, 40, 34))
    for x in range(2, cx - 16, 5):
        rect(d, x, h - 36, x + 2, h - 31, (206, 186, 146))
    hl(d, 0, cx - 14, h - 26, (176, 150, 96))
    rect(d, cx + 16, h - 38, w - 1, h - 18, (118, 50, 40))
    for x in range(cx + 18, w - 2, 5):
        rect(d, x, h - 34, x + 2, h - 30, (196, 176, 140))
    # 发车牌 + 挂钟
    rect(d, cx - 11, 26, cx + 11, 33, (30, 30, 36))
    for y in (28, 31):
        for x in range(cx - 9, cx + 10, 2):
            if hash01(x, y, 3) < 0.7:
                px(d, x, y, (236, 196, 70))
    vl(d, cx, 18, 25, (60, 56, 54))
    d.ellipse((cx - 3, 35, cx + 3, 41), fill=C((236, 232, 220)), outline=C((60, 56, 54)))
    px(d, cx, 37, INK)
    px(d, cx + 1, 38, INK)
    rect(d, 0, h - 14, w - 1, h - 1, (150, 140, 124))              # 站台地面
    for x in range(-20, w + 20, 7):
        d.line((x, h - 1, cx + (x - cx) * 0.4, h - 14), fill=C((136, 126, 112)))
    shade_interior(im, top_k=0.5, bot_k=0.82)
    d = ImageDraw.Draw(im)
    for y in range(h - 40, h - 21):                                # 亮口不压暗
        for x in range(cx - 6, cx + 9):
            px(d, x, y, (210, 200, 172) if y < h - 30 else (186, 178, 156))
    # 往外走的人潮（剪影：远的小、暗；近的大一点、带点颜色）
    order = sorted(range(18), key=lambda i: -hash01(i, 72))
    for i in order:                                                # 远的先画
        x = int(hrange(3, w - 3, i, 71))
        far = hash01(i, 72)
        hh = int(12 + (1 - far) * 12)
        base = h - 1 - int(far * 10)
        col = mix((50, 44, 48), ((150, 60, 60), (200, 196, 184), (70, 90, 130), (160, 120, 60))[i % 4], 0.45 * (1 - far))
        hw = 1 if hh < 18 else 2
        d.ellipse((x - hw, base - hh, x + hw, base - hh + 2 + hw), fill=C(dk(col, 0.8)))     # 头
        rect(d, x - hw - 1, base - hh + 3 + hw, x + hw, base - hh * 0.4, col)               # 身子
        for lx in (x - hw, x + hw - 1):                                                      # 腿
            vl(d, lx, round(base - hh * 0.4) + 1, base, dk(col, 0.85))
        if i % 5 == 0:                                             # 头顶行李
            rect(d, x - 3, base - hh - 3, x + 2, base - hh - 1, mix(col, (120, 90, 60), 0.5))
    return im


def draw_station(im):
    x0, x1 = STATION
    xr = x1 - 1
    d = ImageDraw.Draw(im)
    brick_fill(im, (x0, 30, xr, BASE_Y - 1), 3)
    brick_fill(im, (96, 12, 127, 30), 4)                             # 钟楼
    brick_fill(im, (x0, 20, 13, 30), 5)                              # 左边出图的另一座小塔
    d = ImageDraw.Draw(im)
    # 女儿墙：奶油色压顶 + 一个个垛口（缺口透出后面）
    rect(d, 14, 24, 95, 29, ST_BR)
    rect(d, 128, 24, xr, 29, ST_BR)
    a = np.array(im)
    for x in list(range(16, 94, 7)) + list(range(130, xr - 2, 7)):
        a[24:27, x:x + 3, 3] = 0
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for xx in list(range(14, 95)) + list(range(128, x1)):
        if a[24, xx, 3]:
            px(d, xx, 24, ST_STONE_HI)
    cornice(im, x0, xr, 30, ST_STONE, ST_BR, depth=3, dentils=True)
    # 钟楼：角上奶油石块（隅石）、钟、上面四坡石板瓦顶 + 尖顶
    for (qx, side) in ((96, 0), (124, 1)):
        for y in range(12, 31, 4):
            w = 4 if (y // 4) % 2 else 3
            rect(d, qx if side == 0 else qx + 4 - w, y, (qx + w - 1) if side == 0 else qx + 3, y + 2, ST_STONE)
    cornice(im, 94, 129, 10, ST_STONE, ST_BR, depth=2, dentils=False)
    d = ImageDraw.Draw(im)
    for y in range(1, 10):                                         # 四坡顶（暗蓝灰石板瓦）
        u = (y - 1) / 8
        half = int(3 + 14 * u)
        for x in range(112 - half, 112 + half + 1):
            c = (88, 94, 108) if x < 112 else (70, 74, 88)
            if (y + x // 3) % 3 == 0:
                c = dk(c, 0.9)
            px(d, x, y, c)
    vl(d, 112, 0, 1, (60, 60, 66))
    d.ellipse((105, 15, 119, 29), fill=C(ST_STONE))                 # 钟面
    d.ellipse((107, 17, 117, 27), fill=C((246, 242, 230)))
    for k in range(12):
        ang = math.tau * k / 12
        px(d, round(112 + math.cos(ang) * 4.5), round(22 + math.sin(ang) * 4.5), (90, 84, 80))
    vl(d, 112, 18, 22, INK)
    hl(d, 112, 115, 22, INK)
    for y in range(9, 20):                                         # 左边小塔的顶（出图）
        u = (y - 9) / 10
        half = int(2 + 9 * u)
        for x in range(4 - half, 4 + half + 1):
            if 0 <= x:
                px(d, x, y, (88, 94, 108) if x < 4 else (70, 74, 88))
    cornice(im, x0, 14, 20, ST_STONE, ST_BR, depth=2, dentils=False)
    # 二层：成对的细拱窗（奶油石窗套）
    d = ImageDraw.Draw(im)
    for wx in (4, 11, 100, 107, 116, 123, 132):
        rect(d, wx - 1, 39, wx + 5, 60, ST_STONE)
        d.pieslice((wx - 1, 37, wx + 5, 43), 180, 360, fill=C(ST_STONE))
        rect(d, wx, 42, wx + 4, 58, (60, 56, 64))
        d.pieslice((wx, 39, wx + 4, 45), 180, 360, fill=C((60, 56, 64)))
        vl(d, wx + 2, 42, 58, (110, 104, 104))
        hl(d, wx, wx + 4, 49, (110, 104, 104))
        vl(d, wx, 42, 58, (40, 38, 44))
        hl(d, wx - 2, wx + 6, 61, ST_STONE_HI)
        hl(d, wx - 1, wx + 7, 62, ST_BRD)
    cornice(im, x0, xr, 64, ST_STONE, ST_BR, depth=2, dentils=False)
    # 拱门上方的站名牌（深蓝底 + 黄色色条，不写字）+ 圆形徽章（火车头剪影）
    signboard(im, 30, 44, 86, 54, (30, 52, 104), (236, 200, 80), 'bars', 7)
    d = ImageDraw.Draw(im)
    d.ellipse((52, 34, 64, 44), fill=C((236, 200, 80)))
    d.ellipse((53, 35, 63, 43), fill=C((30, 52, 104)))
    rect(d, 55, 39, 61, 41, (236, 200, 80))
    rect(d, 59, 37, 61, 38, (236, 200, 80))
    px(d, 56, 42, (236, 200, 80))
    px(d, 60, 42, (236, 200, 80))
    # 石砌墙基（126–137）
    rect(d, x0, 124, xr, BASE_Y - 1, ST_STONE)
    for y in range(124, BASE_Y, 5):
        hl(d, x0, xr, y, ST_STONE_S)
        off = 0 if (y // 5) % 2 else 5
        for x in range(x0 + off, x1, 10):
            vl(d, x, y + 1, min(BASE_Y - 1, y + 4), ST_STONE_S)
    hl(d, x0, xr, 123, ST_STONE_HI)
    # 大拱门：里面的大厅 + 一圈红白相间的拱石 + 两边的壁柱
    cx, r, spring = ARCH
    atop = spring - r
    ins = station_interior(2 * r + 1, BASE_Y - atop)
    m = np.zeros((BASE_Y - atop, 2 * r + 1), bool)
    for yy in range(BASE_Y - atop):
        for xx in range(2 * r + 1):
            y = yy + atop
            if y >= spring or (xx - r) ** 2 + (y - spring) ** 2 <= r * r:
                m[yy, xx] = True
    ai = np.array(ins)
    ai[~m, 3] = 0
    im.alpha_composite(Image.fromarray(ai, 'RGBA'), (cx - r, atop))
    d = ImageDraw.Draw(im)
    for ang in range(180, 361):
        rad = math.radians(ang)
        blk = ((ang - 180) // 12) % 2
        for rr in (r + 1, r + 2, r + 3):
            c = (ST_STONE if blk else ST_BR) if rr < r + 3 else ST_STONE_S
            if rr == r + 1:
                c = dk(c, 0.82)
            px(d, round(cx + math.cos(rad) * rr), round(spring + math.sin(rad) * rr), c)
    rect(d, cx - 2, atop - 5, cx + 2, atop, ST_STONE_HI)
    vl(d, cx + 2, atop - 5, atop, ST_STONE_S)
    for xx in (cx - r - 4, cx + r + 1):                            # 门洞两边的方柱
        rect(d, xx, spring - 2, xx + 3, BASE_Y - 1, ST_STONE)
        vl(d, xx, spring - 2, BASE_Y - 1, ST_STONE_HI)
        vl(d, xx + 3, spring - 2, BASE_Y - 1, ST_STONE_S)
        rect(d, xx - 1, spring - 3, xx + 4, spring - 1, ST_STONE_HI)
    mul_box(im, (cx - r, atop + 2, cx - r + 1, BASE_Y - 1), (0.7, 0.72, 0.8))
    # 右边一楼两个小拱门（里面暗、几个人影）
    for ccx in (104, 126):
        rr = 7
        for yy in range(112 - rr, BASE_Y):
            for xx in range(ccx - rr, ccx + rr + 1):
                if yy >= 112 or (xx - ccx) ** 2 + (yy - 112) ** 2 <= rr * rr:
                    u = (yy - (112 - rr)) / (BASE_Y - 112 + rr)
                    px(d, xx, yy, mix((70, 62, 62), (110, 100, 94), u))
        for ang in range(180, 361, 4):
            rad = math.radians(ang)
            px(d, round(ccx + math.cos(rad) * (rr + 1)), round(112 + math.sin(rad) * (rr + 1)), ST_STONE)
        for k in range(2):
            hx = ccx - 3 + k * 5
            rect(d, hx - 1, 122 + k * 2, hx + 1, BASE_Y - 2, (60, 54, 54))
            d.ellipse((hx - 1, 118 + k * 2, hx + 1, 121 + k * 2), fill=C((70, 60, 58)))
    # 左边：售票窗（菱形铁格）+ 小蓝牌
    rect(d, 6, 96, 22, 116, ST_STONE)
    rect(d, 7, 97, 21, 115, (70, 64, 62))
    for x in range(7, 22):
        for y in range(97, 116):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                px(d, x, y, (40, 40, 42))
    hl(d, 5, 23, 117, ST_STONE_HI)
    hl(d, 6, 24, 118, ST_BRD)
    signboard(im, 6, 86, 22, 92, (40, 80, 150), (240, 240, 230), 'bars', 8)
    grime(im, x0, xr, BASE_Y - 1, h=8, k=0.84)
    for i in range(6):
        stain(im, int(hrange(2, 140, i, 91)), 67, int(hrange(8, 20, i, 92)), 900 + i, width=2, ymax=122)


# ============================================================ 近景：车站和老榕树之间的小巷口（矮墙后面看得见中景）
def draw_lane(im):
    """x 142–196：一道刷了石灰的矮墙（y 112–137，墙头碎了几块），墙后面空着（中景的楼从这里露出来）；
    墙根一口压水井（铸铁）+ 铁桶。"""
    d = ImageDraw.Draw(im)
    x0, x1 = STATION[1], B_SPICE[0]
    WH, WH_S = (222, 216, 200), (194, 186, 168)
    plaster(im, (x0, 112, x1 - 1, BASE_Y - 1), WH, WH_S, (236, 232, 220), 31)
    brick_patch(im, 186, 122, 6, 4, 33, clip=(x0, 113, x1 - 1, BASE_Y - 1))
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, 112, (240, 236, 226))
    hl(d, x0, x1 - 1, 113, WH_S)
    a = np.array(im)
    for (bx, bw) in ((150, 5), (176, 4)):                          # 墙头缺口
        for x in range(bx, bx + bw):
            dep = int(1 + 2 * math.sin(math.pi * (x - bx) / bw))
            a[112:112 + dep, x, 3] = 0
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for k in range(3):                                             # 墙上褪色的色带（以前刷的标语，色块）
        hl(d, x0 + 4, x1 - 6, 118 + k * 4, ((206, 120, 100), (110, 140, 180), (206, 120, 100))[k])
    grime(im, x0, x1 - 1, BASE_Y - 1, h=9)
    # 压水井
    d = ImageDraw.Draw(im)
    px_, base = 150, 140
    rect(d, px_ - 8, base, px_ + 8, KERB_Y - 1, (168, 164, 156))   # 水泥台（湿的，深一点）
    hl(d, px_ - 8, px_ + 8, base, (190, 186, 178))
    rect(d, px_ - 2, 118, px_ + 1, base - 1, (52, 70, 62))
    vl(d, px_ - 2, 118, base - 1, (90, 112, 100))
    rect(d, px_ - 3, 116, px_ + 2, 118, (44, 58, 52))
    d.line((px_ + 1, 124, px_ + 6, 126), fill=C((52, 70, 62)), width=2)   # 出水口
    d.line((px_ - 2, 117, px_ - 10, 110), fill=C((52, 70, 62)), width=2)  # 压杆
    px(d, px_ - 11, 109, (90, 112, 100))
    rect(d, px_ + 4, 133, px_ + 9, 139, (176, 180, 186))           # 铁桶
    hl(d, px_ + 4, px_ + 9, 133, (220, 224, 228))
    vl(d, px_ + 9, 134, 139, (130, 134, 140))
    d.arc((px_ + 4, 129, px_ + 9, 136), 180, 360, fill=C((120, 124, 130)))
    for y in range(127, 133):                                      # 一股水
        px(d, px_ + 7, y, (170, 196, 210))


# ============================================================ 近景：巷口（第 7 战那条巷子：深灰黄灰泥、晾衣绳、水洼）
ALLEY_VP = (1202, 102)
ALLEY_U = 0.64                # 巷子尽头的深度（0 = 巷口，1 = 消失点）


def _avp(x, y, u=ALLEY_U):
    return x + (ALLEY_VP[0] - x) * u, y + (ALLEY_VP[1] - y) * u


def draw_alley(im):
    """巷口 x 1172–1232：两边的侧墙往消失点收（左墙背光、右墙上半截有一道斜阳）、湿石板地 + 中间的明沟 + 水洼、
    尽头一面被照亮的墙和一扇小门、三道横过巷子的晾衣绳（衣服在 strip）、一盏吊灯泡、水管、电表箱。"""
    d = ImageDraw.Draw(im)
    ax0, ax1 = ALLEY[0], ALLEY[1] - 1
    ftop = 24
    fl, fr = (ax0, KERB_Y - 1), (ax1, KERB_Y - 1)
    bl, br = _avp(*fl), _avp(*fr)
    tl, tr = _avp(ax0, ftop), _avp(ax1, ftop + 6)
    # 尽头的墙（被照亮）+ 小门 + 门里一点光
    bw0, bw1 = round(bl[0]), round(br[0])
    rect(d, bw0, round(tl[1]), bw1, round(bl[1]), (172, 158, 120))
    mottle(im, (bw0, round(tl[1]), bw1, round(bl[1])), (172, 158, 120), (150, 138, 104), (186, 172, 134), 51, cell=3)
    d = ImageDraw.Draw(im)
    rect(d, bw0 + 6, round(bl[1]) - 14, bw0 + 11, round(bl[1]) - 1, (70, 58, 50))
    rect(d, bw0 + 7, round(bl[1]) - 13, bw0 + 8, round(bl[1]) - 2, (120, 96, 70))
    rect(d, bw1 - 7, round(tl[1]) + 8, bw1 - 4, round(tl[1]) + 12, (60, 56, 52))
    # 巷子尽头那栋楼（在两边侧墙顶线之间露出来，一直盖到前面两栋楼的顶）：暗一点、几扇小窗、一条晾衣
    far_poly = [(ax0, ftop), (ax1, ftop + 6), tr, tl]
    d.polygon(far_poly, fill=C((128, 118, 96)))
    mf = poly_mask(im.size, far_poly)
    a = np.array(im)
    nn = A._fbm(PW + 8, H + 8, 3, seed=53)[4:4 + H, 4:4 + PW]
    a[mf & (nn > 0.6), :3] = (112, 104, 86)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for (wx, wy) in ((1192, 40), (1206, 40), (1192, 56), (1206, 56), (1199, 66)):
        rect(d, wx, wy, wx + 3, wy + 5, (58, 54, 52))
        hl(d, wx - 1, wx + 4, wy + 6, (150, 140, 116))
    hl(d, ax0 + 6, ax1 - 4, 32, (150, 140, 116))
    # 地面
    d.polygon([fl, fr, br, bl], fill=C(ALLEY_FLOOR))
    for y in range(round(bl[1]), KERB_Y):
        u = (KERB_Y - 1 - y) / max(1, KERB_Y - 1 - bl[1])
        xa = ax0 + (bl[0] - ax0) * u
        xb = ax1 + (br[0] - ax1) * u
        step = max(2, int(6 * (1 - u)))
        for x in range(int(xa) + 1, int(xb)):
            if (y % 3 == 0) or ((x - int(xa)) % step == 0 and hash01(x, y, 5) < 0.6):
                px(d, x, y, dk(ALLEY_FLOOR, 0.88))
        px(d, round(xa + (xb - xa) * 0.5), y, (64, 60, 54))           # 中间的明沟
    for (cx, cy, rx, ry) in ((1196, 140, 9, 2.4), (1214, 132, 5, 1.5), (1204, 126, 3, 1)):   # 水洼（反着天光）
        d.ellipse((cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1), fill=C(dk(ALLEY_FLOOR, 0.8)))
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=C(ALLEY_PUDDLE))
        hl(d, round(cx - rx * 0.4), round(cx + rx * 0.2), round(cy - ry * 0.3), (168, 176, 178))
    # 左墙（G 楼的侧墙，背光）
    d.polygon([(ax0, ftop), tl, bl, fl], fill=C(ALLEY_SH))
    m = poly_mask(im.size, [(ax0, ftop), tl, bl, fl])
    a = np.array(im)
    n = A._fbm(PW + 8, H + 8, 4, seed=52)[4:4 + H, 4:4 + PW]
    bay = A._bayer(PW, H)
    a[m & ((n > 0.62) | ((n > 0.58) & (bay < 0.5))), :3] = ALLEY_DK
    a[m & ((n < 0.36) | ((n < 0.4) & (bay < 0.5))), :3] = mix(ALLEY_SH, ALLEY_WALL, 0.5)
    # 右墙（H 楼的侧墙）：下半截在影里，上半截一道斜阳
    mr = poly_mask(im.size, [(ax1, ftop + 6), tr, br, fr])
    a[mr, :3] = ALLEY_WALL
    a[mr & ((n > 0.62) | ((n > 0.58) & (bay < 0.5))), :3] = ALLEY_SH
    yy, xx = np.mgrid[0:H, 0:PW]
    lit = mr & (yy < 64 - (xx - ax1) * 0.9)
    a[lit, :3] = (np.array(a[lit, :3], np.float32) * 1.18 + 10).clip(0, 255).astype(np.uint8)
    a[(m | mr) & (yy > 100), :3] = (a[(m | mr) & (yy > 100), :3] * 0.88).astype(np.uint8)
    a[m | mr, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    d.line([(ax0, ftop), tl, bl], fill=C(ALLEY_DK))
    # 墙上的东西：水管、小门、铁窗、电表箱
    d.line([(ax0 + 3, ftop + 4), _avp(ax0 + 3, ftop + 4, 0.25)], fill=C((70, 74, 72)))
    for (u0, u1, y0, y1) in ((0.12, 0.26, 92, 145), (0.38, 0.48, 70, 92)):
        p = [_avp(ax0, y0, u0), _avp(ax0, y0, u1), _avp(ax0, y1, u1), _avp(ax0, y1, u0)]
        d.polygon(p, fill=C((76, 60, 50) if y1 > 100 else (50, 46, 46)))
    for (u0, u1, y0, y1) in ((0.08, 0.2, 60, 82),):
        p = [_avp(ax1, y0, u0), _avp(ax1, y0, u1), _avp(ax1, y1, u1), _avp(ax1, y1, u0)]
        d.polygon(p, fill=C((54, 50, 50)))
        for k in range(1, 4):
            q0, q1 = _avp(ax1, y0, u0 + (u1 - u0) * k / 4), _avp(ax1, y1, u0 + (u1 - u0) * k / 4)
            d.line([q0, q1], fill=C((30, 30, 30)))
    p = _avp(ax1, 104, 0.14)
    rect(d, round(p[0]) - 3, round(p[1]), round(p[0]), round(p[1]) + 5, (150, 150, 140))
    # 吊灯泡（电线从左墙拉过来）
    lx, ly = 1200, 84
    d.line([_avp(ax0, 60, 0.3), (lx, ly - 6)], fill=C((30, 30, 32)))
    vl(d, lx, ly - 6, ly - 1, (30, 30, 32))
    rect(d, lx - 1, ly, lx + 1, ly + 2, (236, 226, 180))
    # 晾衣绳（衣服在 laundry strip 里）
    for (u, y) in ALLEY_LINES:
        a0, a1 = _avp(ax0, y, u), _avp(ax1, y + 3, u)
        pts = [(round(a0[0] + (a1[0] - a0[0]) * k / 10), round(a0[1] + (a1[1] - a0[1]) * k / 10 + 2 * math.sin(math.pi * k / 10)))
               for k in range(11)]
        d.line(pts, fill=C((40, 38, 40)))
    # 巷口地上：从巷子里淌出来的水
    mul_box(im, (ax0, FOOT_Y, ax1, KERB_Y - 1), (0.86, 0.86, 0.9))


ALLEY_LINES = [(0.12, 50), (0.34, 62), (0.52, 70)]               # (深度 u, 左墙上的 y)


# ============================================================ 近景：老货栈（瓦檐）一段
def draw_compound(im):
    """x 852–946：一层老货栈 —— 石灰刷的墙（剥落处露出旧的粉色和砖）、往外斜的陶瓦檐（y 90–99）、
    一扇大木门（半开）；屋檐上面空着，看得见中景和菩提树冠。"""
    x0, x1 = COMPOUND
    xr = x1 - 1
    WH, WH_S, WH_HI = (224, 218, 200), (196, 188, 170), (238, 234, 222)
    plaster(im, (x0, 99, xr, BASE_Y - 1), WH, WH_S, WH_HI, 61)
    mottle(im, (x0, 99, xr, BASE_Y - 1), WH, (214, 170, 160), WH_HI, 62, cell=6, lo=0.18, hi=0.82)
    brick_patch(im, 900, 108, 7, 4, 63, clip=(x0, 100, xr, BASE_Y - 1))
    brick_patch(im, 940, 126, 4, 6, 64, clip=(x0, 100, xr, BASE_Y - 1))
    d = ImageDraw.Draw(im)
    for y in range(90, 99):                                        # 陶瓦檐（一垄垄，往外斜）
        for x in range(x0 - 1, x1 + 1):
            k = (x + (1 if (y - 90) % 4 >= 2 else 0)) % 3
            c = ((200, 110, 74), (176, 92, 62), (146, 74, 50))[k]
            if y == 90:
                c = (120, 64, 46)
            if hash01(x // 3, (y - 90) // 2, 66) < 0.08:
                c = dk(c, 0.78)
            px(d, x, y, c)
    for x in range(x0 - 1, x1 + 1, 3):
        px(d, x, 99, (110, 58, 42))
        px(d, x + 1, 99, (170, 90, 60))
    mul_box(im, (x0, 100, xr, 103), (0.72, 0.74, 0.82))
    mul_box(im, (x0, 104, xr, 105), (0.84, 0.86, 0.92), level=0.5)
    sim = shop_img('godown', 18, BASE_Y - 108, 67)
    im.alpha_composite(sim, (856, 108))
    d = ImageDraw.Draw(im)
    rect(d, 854, 105, 875, 107, (232, 226, 210))
    vl(d, 854, 105, BASE_Y - 1, (232, 226, 210))
    vl(d, 875, 105, BASE_Y - 1, (196, 188, 170))
    grime(im, x0, xr, BASE_Y - 1, h=9)
    for i in range(4):
        stain(im, int(hrange(x0 + 2, xr - 2, i, 68)), 104, int(hrange(6, 16, i, 69)), 690 + i, width=2)


# ============================================================ 近景：大楼顶上的手绘电影广告牌（战斗段的背景）
BILL = (444, 8, 586, 39)


def draw_billboard(im):
    """C 楼楼顶的手绘电影广告牌（80 年代加尔各答的电影院大海报）：画的是一个大背头小胡子的男主角脸、
    戴红点的女主角、右边持枪的反派剪影和一片火光，标题只用粗色块（不写字）；铁架子、底下一排灯泡、右上角卷起来的一块。"""
    x0, y0, x1, y1 = BILL
    d = ImageDraw.Draw(im)
    # 铁架子（板子下面到屋顶）
    for x in range(x0 + 4, x1 - 2, 12):
        vl(d, x, y1 + 2, 46, (70, 68, 66))
        d.line((x, y1 + 2, x + 6, 46), fill=C((86, 84, 80)))
    hl(d, x0, x1, y1 + 4, (70, 68, 66))
    board = A._new(x1 - x0 + 1, y1 - y0 + 1)
    gradient(board, (0, 0, board.width, board.height), [(84, 46, 96), (150, 60, 90), (220, 110, 60), (240, 170, 70)], bands=7)
    bd = ImageDraw.Draw(board)
    bw, bh = board.width, board.height
    for i in range(14):                                            # 火光（右下）
        fx = int(hrange(bw * 0.62, bw - 2, i, 1))
        fh = int(hrange(6, 16, i, 2))
        bd.polygon([(fx - 4, bh), (fx + 4, bh), (fx + int(hrange(-2, 3, i, 3)), bh - fh)],
                   fill=C(((250, 210, 80), (240, 140, 40), (220, 70, 40))[i % 3]))
    # 反派剪影（持枪）
    vx = bw - 18
    rect(bd, vx - 3, 10, vx + 3, bh - 1, (36, 26, 34))
    bd.ellipse((vx - 3, 4, vx + 3, 11), fill=C((36, 26, 34)))
    hl(bd, vx - 5, vx + 5, 5, (36, 26, 34))
    bd.line((vx - 3, 14, vx - 12, 12), fill=C((36, 26, 34)), width=2)
    rect(bd, vx - 15, 11, vx - 11, 12, (36, 26, 34))
    # 男主角的大脸（左）
    fx, fy = 22, 17
    SKN, SKD, SKH = (214, 150, 104), (176, 112, 76), (236, 184, 140)
    bd.ellipse((fx - 13, fy - 11, fx + 13, fy + 15), fill=C(SKN))
    bd.ellipse((fx + 2, fy - 8, fx + 13, fy + 14), fill=C(SKD))
    bd.ellipse((fx - 11, fy - 9, fx - 2, fy + 2), fill=C(SKH))
    bd.pieslice((fx - 14, fy - 18, fx + 14, fy + 2), 180, 360, fill=C((24, 20, 26)))   # 大背头
    bd.ellipse((fx - 15, fy - 6, fx - 10, fy + 6), fill=C((24, 20, 26)))
    for ex in (fx - 6, fx + 5):                                    # 浓眉 + 眼睛
        hl(bd, ex - 3, ex + 3, fy - 2, (30, 22, 24))
        rect(bd, ex - 2, fy + 1, ex + 2, fy + 2, (250, 246, 236))
        px(bd, ex, fy + 1, (30, 22, 24))
        px(bd, ex, fy + 2, (30, 22, 24))
    vl(bd, fx, fy + 2, fy + 7, SKD)
    rect(bd, fx - 5, fy + 9, fx + 5, fy + 10, (30, 22, 24))          # 小胡子
    hl(bd, fx - 3, fx + 3, fy + 12, (170, 70, 60))
    # 女主角（中间，小一点）：长发、额头红点、黄耳环
    gx, gy = 58, 15
    bd.ellipse((gx - 11, gy - 10, gx + 11, gy + 18), fill=C((30, 22, 30)))
    bd.ellipse((gx - 7, gy - 7, gx + 7, gy + 10), fill=C((226, 168, 128)))
    bd.ellipse((gx + 1, gy - 5, gx + 7, gy + 10), fill=C((200, 140, 104)))
    px(bd, gx, gy - 4, (220, 30, 40))
    for ex in (gx - 3, gx + 3):
        rect(bd, ex - 1, gy, ex + 1, gy, (30, 22, 24))
    hl(bd, gx - 2, gx + 2, gy + 6, (210, 70, 90))
    px(bd, gx - 8, gy + 5, (250, 210, 80))
    px(bd, gx + 8, gy + 5, (250, 210, 80))
    for k in range(5):                                             # 头上一朵花
        px(bd, gx - 9 + k % 3, gy - 6 + k // 3, (250, 250, 240))
    # 标题：一串粗色块（黄底红边，像字但不是字）
    tx = 76
    for i in range(6):
        w = int(hrange(4, 8, i, 7))
        h = int(hrange(7, 11, i, 8))
        ty = 4 + int(hrange(0, 3, i, 9))
        rect(bd, tx - 1, ty - 1, tx + w, ty + h, (170, 30, 30))
        rect(bd, tx, ty, tx + w - 1, ty + h - 1, (250, 220, 70))
        if hash01(i, 10) < 0.5:
            rect(bd, tx + 1, ty + h // 2, tx + w - 2, ty + h // 2, (170, 30, 30))
        else:
            vl(bd, tx + w // 2, ty + 2, ty + h - 1, (170, 30, 30))
        tx += w + 2
    for k in range(4):                                             # 下面一行小字（白色细条）
        hl(bd, 78 + k * 9, 84 + k * 9, 19, (240, 236, 226))
    a = np.array(board).astype(np.float32)                         # 晒褪色：整体往米白混一点 + 斑驳
    n = A._fbm(bw + 8, bh + 8, 5, seed=81)[4:4 + bh, 4:4 + bw]
    fade = 0.12 + (n > 0.62) * 0.2
    a[..., :3] = a[..., :3] * (1 - fade[..., None]) + np.array((226, 214, 190)) * fade[..., None]
    board = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    bd = ImageDraw.Draw(board)
    bd.polygon([(bw - 10, 0), (bw - 1, 0), (bw - 1, 8)], fill=C((236, 230, 214)))   # 右上角卷起来
    bd.line((bw - 10, 0, bw - 1, 8), fill=C((150, 140, 126)))
    bd.rectangle((0, 0, bw - 1, bh - 1), outline=C((60, 52, 50)))
    im.alpha_composite(board, (x0, y0))
    d = ImageDraw.Draw(im)
    hl(d, x0 - 1, x1 + 1, y1 + 1, (90, 86, 82))                    # 板下的走道 + 灯泡
    hl(d, x0 - 1, x1 + 1, y1 + 2, (60, 56, 54))
    for x in range(x0 + 2, x1, 6):
        px(d, x, y1 + 3, (236, 220, 160))


# ============================================================ 近景：摊子 / 神龛 / 槟榔摊
SPICES = [(206, 46, 32), (234, 180, 44), (150, 100, 56), (226, 96, 50), (124, 70, 42), (198, 170, 66),
          (236, 134, 44), (96, 120, 56)]


def draw_spice_stall(im):
    """香料摊：两根竹竿（遮阳布在 strip）、一张矮木台，台上一排铜盘、每盘一座尖尖的香料粉堆（辣椒红、姜黄、孜然、
    咖喱、肉桂、芥末、橙黄、绿香草），台前地上四只卷口麻袋（干辣椒、月桂叶、黑胡椒、姜黄根），右竿上挂一杆秤。"""
    x0, x1 = SPICE_STALL
    d = ImageDraw.Draw(im)
    for x in (x0 + 1, x1 - 2):
        vl(d, x, 100, KERB_Y - 1, (182, 152, 100))
        vl(d, x + 1, 100, KERB_Y - 1, (140, 112, 70))
        for y in range(104, KERB_Y, 8):
            hl(d, x, x + 1, y, (150, 120, 76))
    rect(d, x0 + 6, 125, x1 - 6, 128, (150, 108, 70))              # 台面
    hl(d, x0 + 6, x1 - 6, 125, (190, 146, 100))
    hl(d, x0 + 6, x1 - 6, 128, (100, 70, 46))
    for x in (x0 + 8, (x0 + x1) // 2, x1 - 9):
        rect(d, x, 129, x + 1, KERB_Y - 1, (110, 78, 50))
    rect(d, x0 + 7, 129, x1 - 7, 131, (90, 64, 44))                 # 台子底下的暗
    for i, cx in enumerate(range(x0 + 13, x1 - 9, 10)):
        c = SPICES[i % len(SPICES)]
        d.ellipse((cx - 5, 122, cx + 5, 126), fill=C((200, 160, 82)))   # 铜盘
        hl(d, cx - 4, cx + 4, 122, (236, 204, 120))
        hgt = 6 + (i % 3)
        for r in range(hgt):                                        # 锥形的粉堆：左亮右暗
            y = 123 - r
            half = max(0, int(round(5 - r * 5.0 / hgt)))
            for x in range(cx - half, cx + half + 1):
                cc = c
                if x < cx - half / 3:
                    cc = lt(c, 0.16)
                elif x > cx + half / 3:
                    cc = dk(c, 0.8)
                if hash01(x, y, i, 3) < 0.12:
                    cc = dk(cc, 0.86)
                px(d, x, y, cc)
        px(d, cx, 123 - hgt, lt(c, 0.3))
    for k, (sx, kind) in enumerate(((x0 + 10, 'chili'), (x0 + 30, 'leaf'), (x0 + 54, 'pepper'), (x0 + 72, 'root'))):
        rect(d, sx, 135, sx + 12, KERB_Y - 1, (196, 170, 122))       # 麻袋
        for y in range(136, KERB_Y - 1, 2):
            for x in range(sx + (y // 2) % 2, sx + 12, 2):
                px(d, x, y, (178, 152, 106))
        vl(d, sx + 12, 135, KERB_Y - 1, (150, 126, 86))
        rect(d, sx - 1, 133, sx + 13, 135, (218, 194, 144))         # 卷起来的袋口
        hl(d, sx - 1, sx + 13, 135, (170, 146, 102))
        for x in range(sx, sx + 13):                               # 袋口里冒出来的东西
            for y in (130, 131, 132):
                if hash01(x, y, k, 5) < (0.9 if y > 130 else 0.5):
                    c = dict(chili=((200, 40, 30), (150, 24, 20)), leaf=((120, 130, 70), (90, 100, 54)),
                             pepper=((60, 50, 46), (90, 80, 70)), root=((210, 150, 50), (170, 110, 40)))[kind]
                    px(d, x, y, c[int(hash01(x, y, 6) * 2)])
    bx = x1 - 13                                                   # 挂在竹竿上的秤
    hl(d, bx - 6, bx + 6, 108, (90, 70, 50))
    vl(d, bx, 104, 108, (90, 70, 50))
    for sx in (bx - 6, bx + 6):
        d.line((sx, 108, sx - 2, 114), fill=C((150, 140, 120)))
        d.line((sx, 108, sx + 2, 114), fill=C((150, 140, 120)))
        hl(d, sx - 3, sx + 3, 115, (206, 166, 86))
        hl(d, sx - 2, sx + 2, 116, (160, 120, 60))
    cast_shadow(im, [(x0 + 6, 131), (x1 - 4, 131), (x1, KERB_Y - 1), (x0 + 10, KERB_Y - 1)], level=0.5, mul=SOFT_MUL)


def draw_chai_stall(im):
    """茶摊：刷蓝漆（褪了色）的木柜台，台上一口陶土炉（炉口发红）+ 大铝壶（蒸汽在 strip）、叠成小塔的陶杯、
    两罐饼干；老板在柜台后面（只露上半身）；右边一条长凳（坐着喝茶的人在 SITTERS）。遮雨的蓝塑料布在 strip。"""
    x0, x1 = CHAI_STALL
    d = ImageDraw.Draw(im)
    for x in (x0 - 2, BENCH[1] + 3):                               # 撑塑料布的竹竿
        vl(d, x, 98, KERB_Y - 1, (182, 152, 100))
        vl(d, x + 1, 98, KERB_Y - 1, (140, 112, 70))
    lay = A._new(PW, H)
    person(ImageDraw.Draw(lay), 362, 140, 'shirt', 77, h=34, face=-1)
    lay = haze_img(A._grade(lay, sat=0.72), 0.26, 0.26, col=(200, 192, 176))
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    BL, BLD = (98, 132, 152), (76, 104, 124)
    rect(d, x0, 119, x1, KERB_Y - 1, BL)
    mottle(im, (x0, 119, x1, KERB_Y - 1), BL, BLD, (130, 160, 172), 71, cell=3)
    d = ImageDraw.Draw(im)
    for x in range(x0 + 6, x1, 7):
        vl(d, x, 120, KERB_Y - 1, BLD)
    hl(d, x0, x1, 127, (220, 222, 210))
    rect(d, x0 - 1, 116, x1 + 1, 118, (150, 110, 72))
    hl(d, x0 - 1, x1 + 1, 116, (190, 150, 104))
    rect(d, x0 + 3, 108, x0 + 15, 115, (178, 110, 74))             # 陶土炉
    hl(d, x0 + 3, x0 + 15, 108, (200, 136, 96))
    rect(d, x0 + 7, 111, x0 + 11, 115, (240, 130, 50))
    rect(d, x0 + 8, 112, x0 + 10, 114, (252, 200, 90))
    d.ellipse((x0 + 3, 98, x0 + 15, 108), fill=C((184, 188, 194)))  # 大铝壶
    hl(d, x0 + 5, x0 + 10, 99, (230, 232, 236))
    d.ellipse((x0 + 9, 101, x0 + 14, 107), fill=C((150, 154, 160)))
    rect(d, x0 + 7, 96, x0 + 10, 97, (150, 154, 160))
    d.arc((x0 + 4, 93, x0 + 14, 101), 200, 340, fill=C((90, 94, 100)))
    d.line((x0 + 3, 103, x0, 100), fill=C((170, 174, 180)), width=2)   # 壶嘴（朝左）
    for row in range(4):                                           # 陶杯塔
        for k in range(4 - row):
            cx = x0 + 20 + k * 4 + row * 2
            cy = 115 - row * 3
            rect(d, cx, cy - 2, cx + 2, cy, (178, 98, 62))
            hl(d, cx, cx + 2, cy - 2, (210, 140, 100))
    for (jx, c) in ((x1 - 7, (214, 170, 100)), (x1 - 3, (190, 120, 70))):
        rect(d, jx, 109, jx + 3, 115, (206, 218, 218))
        rect(d, jx, 111, jx + 3, 115, c)
        hl(d, jx, jx + 3, 108, (220, 60, 50))
    b0, b1 = BENCH                                                 # 长凳
    rect(d, b0, 134, b1, 135, (140, 100, 64))
    hl(d, b0, b1, 134, (176, 134, 90))
    for x in (b0 + 1, b1 - 2):
        rect(d, x, 136, x + 1, KERB_Y - 1, (100, 70, 46))
    cast_shadow(im, [(x0, KERB_Y - 2), (x1 + 2, KERB_Y - 2), (x1 + 5, KERB_Y - 1), (x0 + 2, KERB_Y - 1)], mul=SOFT_MUL)


def draw_fruit_cart(im):
    """水果推车（thela）：木板车面、两只自行车轮、往左伸的车把；车上一堆堆芒果、青椰子、木瓜、番石榴、荔枝，
    一把褪色的红黄条大伞，伞骨上挂着一串串香蕉；伞杆上挂一杆秤。"""
    x0, x1 = FRUIT
    d = ImageDraw.Draw(im)
    base = KERB_Y - 1
    cast_shadow(im, [(x0 + 2, base - 1), (x1 + 2, base - 1), (x1 + 6, base + 1), (x0 + 6, base + 1)], mul=SOFT_MUL)
    for wx in (x0 + 9, x1 - 9):                                    # 车轮
        d.ellipse((wx - 6, base - 12, wx + 6, base), outline=C((44, 44, 48)))
        d.ellipse((wx - 5, base - 11, wx + 5, base - 1), outline=C((80, 80, 86)))
        for an in range(0, 180, 30):
            r = math.radians(an)
            d.line((wx - math.cos(r) * 5, base - 6 - math.sin(r) * 5, wx + math.cos(r) * 5, base - 6 + math.sin(r) * 5),
                   fill=C((150, 150, 156)))
    rect(d, x0, 126, x1, 129, (150, 108, 70))                       # 车面
    hl(d, x0, x1, 126, (190, 146, 100))
    hl(d, x0, x1, 129, (96, 66, 44))
    d.line((x0, 128, x0 - 10, 125), fill=C((130, 94, 60)), width=2)  # 车把
    ux = (x0 + x1) // 2
    vl(d, ux, 98, 126, (200, 200, 206))                            # 伞杆
    vl(d, ux + 1, 98, 126, (140, 140, 146))
    hl(d, ux - 4, ux + 4, 108, (90, 70, 50))                       # 秤
    for sx in (ux - 4, ux + 4):
        hl(d, sx - 2, sx + 2, 112, (206, 166, 86))
        d.line((sx, 108, sx, 111), fill=C((150, 140, 120)))
    piles = [(x0 + 4, (236, 170, 50), 'mango'), (x0 + 13, (90, 150, 60), 'coco'), (x0 + 22, (230, 130, 50), 'papaya'),
             (x0 + 31, (170, 200, 100), 'guava'), (x0 + 38, (200, 50, 50), 'litchi')]
    for (px0, col, kind) in piles:
        rows = 3 if kind != 'litchi' else 4
        for r in range(rows):
            n = 4 - r if kind != 'litchi' else 5 - r
            sz = 3 if kind in ('mango', 'coco', 'papaya') else 2
            for k in range(n):
                fx = px0 + k * sz + r * sz // 2
                fy = 125 - r * (sz - 1)
                if kind == 'papaya':
                    rect(d, fx, fy - 1, fx + sz, fy, col)
                    px(d, fx + sz, fy - 1, (90, 140, 60))
                else:
                    d.ellipse((fx, fy - sz + 1, fx + sz - 1, fy), fill=C(col))
                px(d, fx, fy - sz + 1, lt(col, 0.35))
    R_ = 22                                                        # 大伞（红黄条，褪色）
    for x in range(ux - R_, ux + R_ + 1):
        u = (x - ux) / R_
        top = 96 + int(round(5 * u * u))
        bot = 102 + int(round(2 * u * u))
        seg = int((math.asin(max(-1, min(1, u))) / math.pi + 0.5) * 8)
        c = (206, 80, 60) if seg % 2 == 0 else (236, 200, 96)
        for y in range(top, bot + 1):
            cc = lt(c, 0.2) if y == top else (dk(c, 0.8) if y > bot - 2 else c)
            if u > 0.3:
                cc = dk(cc, 0.9)
            px(d, x, y, cc)
    for (bx, by) in ((ux - 14, 104), (ux + 10, 105)):              # 一串串香蕉
        vl(d, bx, by - 2, by, (110, 90, 50))
        for k in range(4):
            d.arc((bx - 3 + k, by + k, bx + 2 + k, by + 5 + k), 20, 160, fill=C((236, 206, 70)))
    mul_box(im, (ux - R_ + 2, 103, ux + R_ + 2, 106), (0.8, 0.82, 0.9), level=0.5)


def draw_paan(im):
    """槟榔摊（paan）：架在四条腿上的木箱子，开着的窗口里盘腿坐着卖槟榔的（白背心），窗口上沿挂满一串串小包装（色块），
    前沿一只铜盘摆着绿色的蒌叶；一盏光灯泡、一面小镜子；铁皮顶往外伸。"""
    x0, x1 = PAAN
    d = ImageDraw.Draw(im)
    for x in (x0 + 2, x1 - 3):
        rect(d, x, 131, x + 1, KERB_Y - 1, WOOD_D)
    rect(d, x0, 108, x1, 131, WOOD)
    for x in range(x0 + 3, x1, 4):
        vl(d, x, 108, 131, WOOD_D)
    hl(d, x0, x1, 108, WOOD_HI)
    rect(d, x0 + 3, 112, x1 - 3, 126, (96, 64, 44))                # 窗口里（暖光）
    rect(d, x0 + 4, 113, x1 - 4, 125, (126, 86, 56))
    cx = (x0 + x1) // 2 + 2
    rect(d, cx - 1, 113, cx + 1, 114, (250, 236, 180))             # 灯泡
    lay = A._new(PW, H)
    ld = ImageDraw.Draw(lay)
    ld.rectangle((cx - 4, 116, cx + 3, 120), fill=C(SKIN[1]))      # 卖槟榔的：头 + 白背心 + 盘起来的腿
    hl(ld, cx - 4, cx + 3, 116, HAIR)
    rect(ld, cx - 5, 121, cx + 4, 126, (236, 232, 222))
    hl(ld, cx - 7, cx + 6, 126, (200, 194, 180))
    px(ld, cx - 6, 123, SKIN[1])
    lay = A._grade(lay, sat=0.8)
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    for x in range(x0 + 4, x1 - 3, 2):                             # 一串串小包装
        for k in range(int(hrange(3, 7, x, 1))):
            px(d, x, 113 + k, ((220, 60, 60), (240, 200, 60), (190, 196, 204), (60, 120, 200), (90, 170, 90))[(x + k) % 5])
    rect(d, x0 + 2, 126, x1 - 2, 127, (176, 132, 84))              # 前沿
    d.ellipse((x0 + 4, 124, x0 + 14, 127), fill=C((200, 160, 80)))  # 铜盘 + 蒌叶
    for k in range(5):
        px(d, x0 + 6 + k * 2, 124, (90, 150, 70))
        px(d, x0 + 7 + k * 2, 125, (70, 126, 56))
    rect(d, x1 - 9, 122, x1 - 5, 125, (190, 60, 60))               # 烟盒（色块）
    rect(d, x1 - 2, 114, x1, 119, (190, 210, 220))                 # 小镜子
    rect(d, x0 - 3, 104, x1 + 3, 107, (150, 150, 146))             # 铁皮顶
    hl(d, x0 - 3, x1 + 3, 104, (190, 190, 186))
    hl(d, x0 - 3, x1 + 3, 107, (96, 96, 94))
    mul_box(im, (x0, 108, x1 + 2, 110), (0.76, 0.78, 0.86))
    cast_shadow(im, [(x1, 131), (x1 + 6, 131), (x1 + 8, KERB_Y - 1), (x1 + 1, KERB_Y - 1)], mul=SOFT_MUL)


def draw_shrine(im):
    """路边小神龛（x 884–916）：刷白的砖台子 + 两级台阶，龛身白墙红边、拱形龛洞里一尊橙红色的神像，龛洞一圈万寿菊花环，
    龛顶一座小小的弧形尖塔 + 金色宝瓶 + 一面小旗（旗、灯火、香烟在 strip）；挂一只小铜铃，台上摆着花和椰子。"""
    x0, x1 = SHRINE
    cx = (x0 + x1) // 2
    d = ImageDraw.Draw(im)
    WH, WH_S = (236, 230, 214), (204, 196, 178)
    rect(d, x0 - 2, 136, x1 + 2, KERB_Y - 1, WH)                     # 台子 + 台阶
    hl(d, x0 - 2, x1 + 2, 136, (248, 246, 238))
    hl(d, x0 - 2, x1 + 2, 140, WH_S)
    hl(d, x0 - 4, x1 + 4, 141, (244, 240, 230))
    rect(d, x0 - 4, 142, x1 + 4, KERB_Y - 1, WH_S)
    rect(d, cx - 11, 104, cx + 11, 135, WH)
    vl(d, cx + 11, 104, 135, WH_S)
    rect(d, cx - 11, 130, cx + 11, 135, (204, 80, 52))
    hl(d, cx - 11, cx + 11, 130, (230, 120, 80))
    for yy in range(108, 130):                                     # 龛洞（拱）
        for xx in range(cx - 6, cx + 7):
            if yy >= 114 or (xx - cx) ** 2 + (yy - 114) ** 2 <= 36:
                px(d, xx, yy, (128, 36, 34) if yy > 112 else (110, 30, 30))
    d.ellipse((cx - 3, 112, cx + 3, 118), fill=C((232, 112, 40)))   # 神像
    rect(d, cx - 4, 118, cx + 4, 127, (222, 92, 40))
    hl(d, cx - 3, cx + 3, 111, (240, 200, 80))
    px(d, cx - 1, 114, (250, 250, 250))
    px(d, cx + 1, 114, (250, 250, 250))
    px(d, cx, 116, (150, 20, 20))
    for k in range(3):
        hl(d, cx - 4, cx + 4, 120 + k * 3, (240, 190, 70))
    for ang in range(180, 361, 15):                                # 花环
        rad = math.radians(ang)
        px(d, round(cx + math.cos(rad) * 8), round(114 + math.sin(rad) * 8), (236, 140, 40) if ang % 30 else (246, 206, 60))
    for yy in range(114, 129, 2):
        px(d, cx - 8, yy, (236, 140, 40))
        px(d, cx + 8, yy, (246, 206, 60))
    for y in range(84, 104):                                       # 弧形小尖塔
        u = (y - 84) / 20
        half = int(round(2 + 9 * math.sin(u * math.pi / 2)))
        for xx in range(cx - half, cx + half + 1):
            c = (226, 124, 64) if xx <= cx else (192, 96, 50)
            if (y - 84) % 4 == 0:
                c = dk(c, 0.86)
            px(d, xx, y, c)
    hl(d, cx - 12, cx + 12, 104, (250, 246, 236))
    d.ellipse((cx - 2, 79, cx + 2, 84), fill=C((226, 186, 70)))     # 宝瓶
    px(d, cx, 78, (240, 210, 110))
    vl(d, cx, 68, 77, (110, 90, 70))                               # 旗杆（旗在 strip）
    vl(d, cx + 9, 104, 106, (90, 80, 60))                          # 铜铃
    d.ellipse((cx + 8, 106, cx + 10, 109), fill=C((214, 170, 70)))
    for (fx, c) in ((x0 + 1, (236, 140, 40)), (x0 + 4, (246, 206, 60)), (x1 - 4, (236, 140, 40)), (x1 - 1, (246, 206, 60))):
        d.ellipse((fx - 1, 134, fx + 1, 136), fill=C(c))           # 供的花
    d.ellipse((x1 - 9, 132, x1 - 5, 136), fill=C((120, 86, 56)))    # 椰子
    px(d, x1 - 8, 133, (160, 120, 80))
    rect(d, cx - 2, 128, cx + 2, 129, (150, 80, 50))               # 油灯（火苗在 strip）
    cast_shadow(im, [(cx + 11, 105), (cx + 15, 108), (cx + 15, 135), (cx + 12, 135)], mul=SOFT_MUL)


def draw_peepal_base(im):
    """菩提树：树根下一圈刷白的砖台（中间一道橙色），树干缠着红白线；树冠在最后画（盖在屋檐、电线前面）。"""
    d = ImageDraw.Draw(im)
    x = PEEPAL_X
    rect(d, x - 14, 134, x + 14, KERB_Y - 1, (230, 224, 208))
    hl(d, x - 14, x + 14, 134, (246, 242, 232))
    hl(d, x - 14, x + 14, 138, (226, 130, 60))
    vl(d, x + 14, 135, KERB_Y - 1, (196, 188, 170))
    for y in range(60, 134):                                       # 树干（有棱、往上分叉）
        w = 9 if y > 110 else (8 if y > 84 else 6)
        for k in range(w):
            c = BARK_HI if k < 2 else (BARK if k < w - 2 else BARK_D)
            if (y // 4 + k) % 5 == 0:
                c = dk(c, 0.86)
            px(d, x - w // 2 + k, y, c)
    for k in range(4):                                             # 根往两边伸
        d.line((x - 4, 130 + k, x - 9 - k * 2, 134), fill=C(BARK))
        d.line((x + 4, 130 + k, x + 9 + k * 2, 134), fill=C(BARK_D))
    for y in (118, 120, 122):
        hl(d, x - 4, x + 4, y, (200, 40, 40) if y != 120 else (240, 236, 226))
    for (ax, ay, bx, by) in ((x, 76, x - 22, 50), (x + 1, 70, x + 24, 46), (x, 66, x - 4, 40)):
        d.line((ax, ay, bx, by), fill=C(BARK), width=3)


def draw_banyan_base(im):
    """老榕树（x 170）：很粗的树干 + 板根，从枝上垂下来的一根根气根（有几根扎进地里成了柱子）。"""
    d = ImageDraw.Draw(im)
    x = BANYAN_X
    for y in range(40, KERB_Y):
        w = 16 if y > 120 else (13 if y > 80 else 11)
        if y > 136:
            w += (y - 136) * 2
        for k in range(w):
            c = BARK_HI if k < 3 else (BARK if k < w - 3 else BARK_D)
            if ((y // 3) + k * 2) % 7 == 0:
                c = dk(c, 0.84)
            if k in (w // 2, w // 2 + 1) and y % 9 < 5:
                c = BARK_D
            px(d, x - w // 2 + k, y, c)
    for (ax, ay, bx, by, wd) in ((x - 2, 56, x - 30, 30, 4), (x + 2, 52, x + 34, 26, 4), (x, 46, x - 8, 18, 3),
                                 (x + 1, 48, x + 14, 16, 3)):
        d.line((ax, ay, bx, by), fill=C(BARK), width=wd)
        d.line((ax + 1, ay + 1, bx + 1, by + 1), fill=C(BARK_D), width=1)
    for i in range(16):                                            # 气根
        rx = int(hrange(x - 30, x + 30, i, 1))
        y0 = int(hrange(28, 46, i, 2))
        L = int(hrange(14, 60, i, 3))
        if i in (3, 9):
            L = KERB_Y - 1 - y0                                    # 扎进地里的那几根
        for y in range(y0, min(KERB_Y, y0 + L)):
            xx = rx + int(math.sin(y * 0.2 + i) * 0.8)
            px(d, xx, y, (126, 112, 92) if y % 5 else (100, 88, 74))
        if i in (3, 9):
            vl(d, rx + 1, y0 + 10, KERB_Y - 1, BARK_D)


def draw_tram_sign(im, x):
    """电车站牌（挂在架空线杆上）：白底红边的方牌，中间一个蓝色电车小图（不写字）。"""
    d = ImageDraw.Draw(im)
    rect(d, x + 2, 96, x + 14, 106, (240, 238, 230))
    rect(d, x + 2, 96, x + 14, 106, None, outline=(196, 50, 44))
    rect(d, x + 5, 99, x + 11, 102, (50, 90, 160))
    vl(d, x + 8, 97, 98, (50, 90, 160))
    px(d, x + 6, 103, (40, 40, 40))
    px(d, x + 10, 103, (40, 40, 40))
    hl(d, x + 6, x + 10, 100, (200, 220, 240))
    hl(d, x + 1, x + 2, 98, (60, 70, 66))
    hl(d, x + 1, x + 2, 104, (60, 70, 66))
    mul_box(im, (x + 15, 97, x + 15, 107), (0.8, 0.82, 0.9))


# ============================================================ 近景：黄色 Ambassador 出租车 / 人力车 / 躺着的牛
def draw_taxi(im):
    """黄色 Ambassador 出租车（车头朝左）：圆鼓鼓的车身、弧形车顶、镀铬保险杠和腰线、圆大灯、车顶白色顶灯箱、
    前翼子板上那只老式机械计价器（红旗子）、驾驶座上包头巾的司机；车底一片暗影，影子往右下落到马路边。"""
    x0, x1 = TAXI
    d = ImageDraw.Draw(im)
    Y, YD, YH, YK = TAXI_Y, (198, 148, 26), (250, 222, 112), (150, 106, 22)
    CH, CHD = (214, 216, 218), (128, 132, 138)
    GL, GLH = (88, 106, 122), (150, 170, 186)
    mul_box(im, (x0 + 2, 142, x1 - 2, KERB_Y + 1), (0.6, 0.62, 0.7))             # 车底的暗
    cast_shadow(im, [(x0 + 8, KERB_Y + 1), (x1 + 2, KERB_Y + 1), (x1 + 6, STREET_Y + 1), (x0 + 12, STREET_Y + 1)],
                mul=SOFT_MUL)
    body = [(x0 + 1, 128), (x0 + 4, 125), (x0 + 26, 123), (x0 + 30, 122), (x0 + 36, 112), (x0 + 40, 110),
            (x0 + 62, 110), (x0 + 66, 112), (x0 + 72, 122), (x1 - 1, 125), (x1, 130), (x1, 138), (x1 - 2, 141),
            (x0 + 2, 141), (x0, 137)]
    d.polygon(body, fill=C(Y))
    for y in range(110, 142):                                      # 竖向明暗：上亮、腰线下暗、底边更暗
        for x in range(x0, x1 + 1):
            p = im.getpixel((x, y))
            if p[:3] != Y:
                continue
            c = Y
            if y >= 136:
                c = YD
            if y >= 140:
                c = YK
            if 126 <= y <= 127:
                c = YH
            px(d, x, y, c)
    d.line(body[:7], fill=C(YH))
    d.line(body[6:10], fill=C(YH))
    for poly in ([(x0 + 37, 113), (x0 + 48, 113), (x0 + 48, 121), (x0 + 33, 121)],
                 [(x0 + 50, 113), (x0 + 62, 113), (x0 + 66, 121), (x0 + 50, 121)]):   # 侧窗（带镀铬框）
        m = poly_mask(im.size, poly)
        a = np.array(im)
        ys_, xs_ = np.nonzero(m)
        for (y, x) in zip(ys_, xs_):
            a[y, x, :3] = GLH if (x - y) % 9 in (0, 1) else GL
        im.paste(Image.fromarray(a, 'RGBA'))
        d = ImageDraw.Draw(im)
        hl(d, poly[0][0], poly[1][0], 112, CH)
        hl(d, poly[3][0], poly[2][0], 122, CHD)
    vl(d, x0 + 49, 112, 122, Y)                                    # 中柱
    d.polygon([(x0 + 64, 113), (x0 + 66, 113), (x0 + 70, 121), (x0 + 64, 121)], fill=C(GL))   # 后窗
    d.line((x0 + 31, 121, x0 + 36, 113), fill=C(GL))                # 前挡风（侧面看是一条斜边）
    d.line((x0 + 32, 121, x0 + 37, 113), fill=C(GLH))
    rect(d, x0 + 40, 114, x0 + 44, 117, (232, 140, 50))            # 司机：橙色头巾 + 头
    rect(d, x0 + 40, 118, x0 + 44, 121, SKIN[3])
    px(d, x0 + 40, 119, HAIR)
    for x in (x0 + 35, x0 + 49, x0 + 64):                          # 车门缝 + 把手
        vl(d, x, 124, 138, YD)
    for x in (x0 + 38, x0 + 52):
        hl(d, x, x + 2, 127, CH)
    hl(d, x0 + 3, x1 - 2, 132, CH)                                 # 腰线（镀铬）
    hl(d, x0 + 3, x1 - 2, 133, CHD)
    for (wx, wy) in ((x0 + 14, 141), (x0 + 63, 141)):              # 轮拱 + 轮胎 + 轮毂
        d.pieslice((wx - 8, wy - 8, wx + 8, wy + 8), 180, 360, fill=C((52, 44, 34)))
        d.ellipse((wx - 6, wy - 6, wx + 6, KERB_Y), fill=C((32, 32, 36)))
        d.ellipse((wx - 3, wy - 3, wx + 3, wy + 3), fill=C(CH))
        d.ellipse((wx - 1, wy - 1, wx + 1, wy + 1), fill=C(CHD))
        px(d, wx - 2, wy - 2, (250, 250, 250))
        d.arc((wx - 8, wy - 8, wx + 8, wy + 8), 180, 360, fill=C(YH))
    rect(d, x0 - 2, 136, x0 + 6, 138, CH)                           # 保险杠
    hl(d, x0 - 2, x0 + 6, 136, (250, 250, 250))
    rect(d, x1 - 4, 136, x1 + 2, 138, CH)
    d.ellipse((x0, 127, x0 + 4, 131), fill=C(CH))                   # 圆大灯
    px(d, x0 + 1, 128, (255, 252, 230))
    for y in (132, 134):                                           # 前格栅
        hl(d, x0, x0 + 2, y, CHD)
    rect(d, x1 - 1, 128, x1, 131, (200, 50, 40))                    # 尾灯
    rect(d, x0 + 44, 106, x0 + 54, 109, (240, 238, 228))            # 车顶灯箱（不写字）
    rect(d, x0 + 44, 106, x0 + 54, 109, None, outline=(80, 76, 70))
    hl(d, x0 + 46, x0 + 52, 107, (200, 60, 50))
    rect(d, x0 + 26, 117, x0 + 29, 121, (40, 40, 44))               # 机械计价器 + 红旗子
    rect(d, x0 + 27, 114, x0 + 28, 116, (210, 50, 40))
    px(d, x0 + 27, 118, (220, 220, 200))


def draw_rickshaw(im):
    """人力车（手拉的，停着）：一只很大的木辐条轮、黑漆车厢 + 红坐垫 + 撑开的黑篷、两根长车把往左落在地上；
    车夫坐在车把上歇着（白背心、格子围裤、肩上一条红白格毛巾，手里一只小铜铃）。"""
    x0, x1 = RICKSHAW
    d = ImageDraw.Draw(im)
    base = KERB_Y
    wcx, wcy, wr = 772, base - 12, 11
    cast_shadow(im, [(x0 + 4, base), (x1 + 2, base), (x1 + 6, STREET_Y + 1), (x0 + 8, STREET_Y + 1)], mul=SOFT_MUL)
    WD, WDL = (150, 108, 66), (186, 146, 98)
    for k in range(2):                                             # 车把（两根，往左斜到地）
        d.line((x0 + 2, base - 1 - k, 760, 122 + k), fill=C(WDL if k == 0 else WD), width=1)
    hl(d, x0, x0 + 4, base - 1, (110, 80, 50))
    BLK, BLKH = (44, 38, 36), (86, 78, 72)
    d.polygon([(758, 120), (788, 120), (788, 126), (784, 130), (760, 130)], fill=C(BLK))   # 车厢
    hl(d, 758, 788, 120, BLKH)
    hl(d, 760, 786, 126, (190, 160, 90))
    rect(d, 750, 128, 762, 130, (100, 76, 52))                      # 踏板
    hl(d, 750, 762, 128, (140, 108, 72))
    rect(d, 760, 114, 786, 119, (156, 52, 46))                      # 坐垫
    hl(d, 760, 786, 114, (190, 86, 76))
    rect(d, 782, 100, 788, 119, (150, 48, 42))                      # 靠背
    vl(d, 782, 100, 119, (186, 80, 70))
    pcx, pcy, hrx, hry = 788, 117, 25, 20                          # 篷：撑开的黑色折叠篷（侧面一个鼓起来的弧，几道同心篷骨）
    hood = [(pcx, pcy)]
    for k in range(0, 91, 5):
        an = math.radians(180 + k)
        hood.append((pcx + hrx * math.cos(an), pcy + hry * math.sin(an)))
    hood += [(pcx + 3, pcy - hry), (pcx + 3, pcy)]
    d.polygon(hood, fill=C((40, 36, 40)))
    for sc in (0.6, 0.82):
        d.arc((pcx - hrx * sc, pcy - hry * sc, pcx + hrx * sc, pcy + hry * sc), 185, 268, fill=C((70, 66, 72)))
    d.arc((pcx - hrx, pcy - hry, pcx + hrx, pcy + hry), 200, 262, fill=C((104, 98, 104)))
    d.line((pcx - hrx + 1, pcy - 1, pcx - 9, pcy + 3), fill=C((150, 150, 156)))    # 撑篷的铁杆
    px(d, pcx - hrx, pcy, (90, 86, 92))
    d.ellipse((wcx - wr, wcy - wr, wcx + wr, wcy + wr), outline=C((80, 54, 34)), width=2)   # 大木轮
    d.ellipse((wcx - wr + 2, wcy - wr + 2, wcx + wr - 2, wcy + wr - 2), outline=C((120, 86, 54)))
    for ang in range(0, 180, 15):
        rad = math.radians(ang)
        d.line((wcx - math.cos(rad) * (wr - 2), wcy - math.sin(rad) * (wr - 2),
                wcx + math.cos(rad) * (wr - 2), wcy + math.sin(rad) * (wr - 2)), fill=C((150, 112, 72)))
    d.ellipse((wcx - 2, wcy - 2, wcx + 2, wcy + 2), fill=C((70, 60, 50)))
    px(d, wcx - 1, wcy - 1, (200, 180, 140))
    d.arc((wcx - wr - 2, wcy - wr - 2, wcx + wr + 2, wcy + wr + 2), 200, 340, fill=C(BLK))   # 挡泥板
    # 车夫：坐在车把上（x 740），朝左
    lay = A._new(PW, H)
    ld = ImageDraw.Draw(lay)
    sx, sy = 742, 132                                              # 坐的那一点（车把上）
    sk = SKIN[3]
    rect(ld, sx - 2, sy - 22, sx + 1, sy - 18, sk)                 # 头
    hl(ld, sx - 2, sx + 1, sy - 22, HAIR)
    px(ld, sx - 2, sy - 20, dk(sk, 0.7))
    rect(ld, sx - 3, sy - 17, sx + 2, sy - 9, (236, 234, 226))     # 白背心
    vl(ld, sx - 4, sy - 16, sy - 10, sk)
    vl(ld, sx + 3, sy - 16, sy - 9, sk)
    for k in range(5):                                             # 肩上的红白格毛巾
        px(ld, sx - 3 + k, sy - 17 + (k % 2), (200, 50, 50) if k % 2 else (240, 236, 226))
    px(ld, sx - 5, sy - 10, (226, 186, 70))                        # 小铜铃
    for y in range(sy - 8, sy + 1):                                # 格子围裤（坐着，往左伸）
        for x in range(sx - 5, sx + 3):
            px(ld, x, y, (90, 110, 160) if (x + y) % 3 else (220, 220, 214))
    for x in (sx - 5, sx - 2):                                     # 小腿垂到地上
        vl(ld, x, sy + 1, base - 2, sk)
        hl(ld, x - 1, x, base - 1, dk(sk, 0.7))
    lay = A._grade(lay, sat=0.85)
    im.alpha_composite(lay)


def draw_cow_bg(im):
    """背景里一头躺着的白色瘤牛（x 1116–1150，人行道上；脖子上一串万寿菊花环）—— 剧情的牛在 x 500，那是另一头。"""
    x0, x1 = COW_BG
    d = ImageDraw.Draw(im)
    base = KERB_Y - 1
    WHc, WHs, WHd = (232, 226, 212), (204, 196, 180), (170, 162, 148)
    cast_shadow(im, [(x0 + 4, base - 2), (x1 + 2, base - 2), (x1 + 5, base), (x0 + 6, base)], mul=SOFT_MUL)
    d.ellipse((x0 + 8, base - 14, x1, base), fill=C(WHc))
    d.ellipse((x0 + 14, base - 7, x1, base), fill=C(WHs))
    d.ellipse((x0 + 11, base - 17, x0 + 18, base - 11), fill=C(WHc))   # 瘤（肩峰）
    px(d, x0 + 12, base - 16, (244, 240, 230))
    rect(d, x0 + 2, base - 15, x0 + 10, base - 8, WHc)              # 头（朝左）
    rect(d, x0, base - 11, x0 + 3, base - 7, WHs)
    px(d, x0, base - 9, (70, 60, 56))
    px(d, x0 + 4, base - 13, INK)
    for (hx, hy) in ((x0 + 5, base - 16), (x0 + 4, base - 17), (x0 + 8, base - 16), (x0 + 9, base - 17)):
        px(d, hx, hy, (120, 100, 80))
    px(d, x0 + 4, base - 18, (60, 50, 44))
    px(d, x0 + 9, base - 18, (60, 50, 44))
    for k in range(6):                                             # 花环
        px(d, x0 + 8 + (k % 2), base - 14 + k, (236, 140, 40) if k % 2 else (246, 206, 60))
    for x in range(x0 + 6, x0 + 14):                               # 折起来的前腿
        px(d, x, base, WHd)
    d.arc((x1 - 6, base - 9, x1 + 2, base - 1), 270, 90, fill=C(WHd))  # 尾巴
    px(d, x1 + 1, base - 2, (60, 50, 44))


# ============================================================ 近景：架空线杆 / 电线
def wire_y(x, ax, ay, bx, by, sag):
    u = (x - ax) / max(1, bx - ax)
    return ay + (by - ay) * u + sag * math.sin(math.pi * u)


WIRES = [  # (x0, y0, x1, y1, 下垂)：楼和杆之间乱拉的电线
    (0, 64, 136, 56, 6), (136, 58, 196, 70, 4), (300, 74, 424, 70, 9), (300, 77, 424, 74, 11),
    (424, 77, 604, 75, 4), (604, 68, 704, 60, 7), (704, 62, 862, 66, 10), (704, 66, 862, 72, 13),
    (862, 62, 946, 54, 6), (946, 82, 1150, 60, 9), (1150, 60, 1060, 82, 5), (1150, 62, 1232, 72, 4),
    (1150, 64, 1280, 56, 9), (1150, 68, 1110, 98, 3), (1150, 58, 1172, 40, 2),
]
BIRDS_ON_WIRE = [(318, 2, 0), (340, 2, 1), (352, 2, 0), (372, 3, 1), (730, 6, 0), (748, 6, 1), (760, 7, 0),
                 (778, 6, 0), (1180, 11, 1), (1196, 11, 0), (1188, 11, 0)]   # (x, 电线编号, 0 鸽子 / 1 乌鸦)


def draw_pole(im, x, transformer=False):
    """架空线杆（墨绿铸铁管：左亮右暗、底座一圈圈线脚、顶上一颗球）+ 伸出来的挑臂和吊线；transformer：带变压器的电线杆。"""
    d = ImageDraw.Draw(im)
    top = 6 if not transformer else 30
    for y in range(top, KERB_Y):
        px(d, x - 1, y, (104, 122, 112))
        px(d, x, y, (72, 88, 82))
        px(d, x + 1, y, (50, 62, 58))
    for (y, w) in ((130, 2), (134, 3), (KERB_Y - 3, 3)):
        rect(d, x - w, y, x + w, y + 2, (72, 88, 82))
        hl(d, x - w, x + w, y, (110, 128, 118))
        vl(d, x + w, y, y + 2, (46, 56, 52))
    for y in (60, 100):
        hl(d, x - 2, x + 2, y, (110, 128, 118))
    if not transformer:
        d.ellipse((x - 2, top - 4, x + 2, top), fill=C((72, 88, 82)))
        px(d, x - 1, top - 3, (120, 140, 130))
        hl(d, x + 1, x + 10, 15, (72, 88, 82))                     # 挑臂 + 斜撑 + 吊线
        d.line((x + 1, 22, x + 8, 16), fill=C((72, 88, 82)))
        rect(d, x + 9, 16, x + 10, 17, (200, 196, 180))
        vl(d, x + 10, 18, WIRE_Y, (50, 52, 54))
    else:                                                          # 横担 + 瓷瓶 + 变压器 + 一团乱线
        for y in (36, 44):
            hl(d, x - 9, x + 9, y, (70, 72, 74))
            for xx in (x - 8, x - 3, x + 3, x + 8):
                rect(d, xx, y - 2, xx, y - 1, (220, 220, 210))
        rect(d, x - 8, 62, x - 2, 76, (110, 116, 112))
        hl(d, x - 8, x - 2, 62, (150, 156, 150))
        for y in range(64, 76, 3):
            hl(d, x - 7, x - 3, y, (90, 96, 92))
        vl(d, x - 2, 62, 76, (80, 86, 82))
        for k in range(4):                                         # 杆上盘着的一小卷线
            d.arc((x - 4 + k % 2, 78 + k * 2, x + 4 + k % 3, 83 + k * 2), 20, 300, fill=C((36, 34, 38)))
        rect(d, x + 2, 94, x + 6, 100, (150, 150, 140))           # 电表箱
        hl(d, x + 2, x + 6, 94, (190, 190, 180))
    mul_box(im, (x + 2, top + 2, x + 2, KERB_Y - 1), (0.84, 0.86, 0.92), level=0.5)


def draw_wires(im):
    d = ImageDraw.Draw(im)
    WK = (36, 34, 38)
    for (ax, ay, bx, by, sag) in WIRES:
        lo, hi_ = min(ax, bx), max(ax, bx)
        for x in range(lo, hi_ + 1):
            y = wire_y(x, ax, ay, bx, by, sag)
            px(d, x, round(y), WK)
    # 电车架空线：接触线（y 21，一直拉过去）+ 上面一根承力索（两根杆之间下垂）+ 每 8 px 一根吊弦
    poles = [p for p in POLES if p != 1150]
    spans = [(-200, poles[0])] + list(zip(poles, poles[1:])) + [(poles[-1], PW + 200)]
    for (a, b) in spans:
        for x in range(max(0, a + 10), min(PW, b + 10)):
            u = (x - (a + 10)) / max(1, (b - a))
            ym = 14 + 4 * math.sin(math.pi * u)
            px(d, x, round(ym), (60, 60, 64))
            px(d, x, WIRE_Y, (44, 44, 48))
            if (x - a) % 8 == 0:
                vl(d, x, round(ym) + 1, WIRE_Y - 1, (96, 96, 100))


# ============================================================ 近景：两棵树的树冠（最后画，盖在屋檐和电线前面）
BANYAN_PAL = ((34, 62, 40), (50, 88, 52), (72, 116, 62), (108, 150, 82))
PEEPAL_PAL = ((44, 84, 44), (66, 118, 58), (96, 150, 74), (146, 190, 104))


def draw_crowns(im):
    d = ImageDraw.Draw(im)
    x = BANYAN_X
    _canopy(d, x, 20, 58, 18, 701, pal=BANYAN_PAL)
    _canopy(d, x - 38, 30, 28, 11, 702, pal=BANYAN_PAL)
    _canopy(d, x + 40, 26, 30, 12, 703, pal=BANYAN_PAL)
    _canopy(d, x - 4, 8, 34, 9, 704, pal=BANYAN_PAL)
    _canopy(d, x - 56, 40, 14, 7, 705, pal=BANYAN_PAL)
    _canopy(d, x + 58, 38, 14, 7, 706, pal=BANYAN_PAL)
    x = PEEPAL_X
    _canopy(d, x, 48, 40, 22, 711, pal=PEEPAL_PAL)
    _canopy(d, x - 26, 58, 20, 10, 712, pal=PEEPAL_PAL)
    _canopy(d, x + 28, 54, 22, 11, 713, pal=PEEPAL_PAL)
    for i in range(40):                                            # 菩提叶的小尖（亮绿点点）
        lx = int(hrange(x - 50, x + 50, i, 714))
        ly = int(hrange(28, 66, i, 715))
        if im.getpixel((lx, ly))[3] and im.getpixel((lx, ly))[:3] in PEEPAL_PAL[1:3]:
            px(d, lx, ly, PEEPAL_PAL[3])


# ============================================================ 近景：整条街
def draw_shadows(im):
    """路人脚下 / 杆子 / 摊子投在人行道上的淡影（往右下）。"""
    for (x, base, kind, face, h) in CROWD:
        cast_shadow(im, [(x - 2, base), (x + 4, base), (x + 6, min(KERB_Y - 1, base + 1)), (x, min(KERB_Y - 1, base + 1))],
                    mul=SOFT_MUL)
    for x in POLES:
        cast_shadow(im, [(x + 2, KERB_Y - 2), (x + 5, KERB_Y - 2), (x + 7, KERB_Y + 1), (x + 4, KERB_Y + 1)], mul=SOFT_MUL)


def compress_band(im):
    """可走带后面（y 100–147）压对比：往一个中间色收 18 %（从 y 96 起渐变），人物站上去是清楚的。"""
    a = np.array(im).astype(np.float32)
    mid = np.array((150, 140, 124), np.float32)
    for y in range(96, STREET_Y):
        k = 1.0 - 0.18 * min(1.0, (y - 96) / 8)
        m = a[y, :, 3] > 0
        a[y, m, :3] = mid + (a[y, m, :3] - mid) * k
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


@lru_cache(maxsize=1)
def near_parts():
    """返回 (整条街, 只有地面的那一张)。"""
    im = A._new(PW, H)
    draw_ground(im)
    ground = im.copy()
    draw_alley(im)
    draw_station(im)
    draw_lane(im)
    for b in BLDS:
        facade(im, b)
    draw_rooftop_f(im)
    draw_window_people(im)
    draw_laundry_ropes(im)
    draw_compound(im)
    draw_billboard(im)
    draw_banyan_base(im)
    draw_peepal_base(im)
    draw_spice_stall(im)
    draw_chai_stall(im)
    draw_paan(im)
    draw_fruit_cart(im)
    draw_shrine(im)
    im.alpha_composite(crowd_layer())
    draw_cow_bg(im)
    draw_taxi(im)
    draw_rickshaw(im)
    for x in POLES:
        draw_pole(im, x, transformer=(x == 1150))
    draw_tram_sign(im, TRAM_STOP_X)
    draw_wires(im)
    draw_crowns(im)
    draw_shadows(im)
    compress_band(im)
    im = A._grade(im, sat=0.94, val=1.0)
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    g = A._grade(ground, sat=0.94, val=1.0)
    compress_band(g)
    return Image.fromarray(a, 'RGBA'), g


def near_img():
    return near_parts()[0]


# ============================================================ 会动的（strip，世界坐标，k 1）
# 晾衣：(绳子 x0, x1, y0, y1, 下垂, 衣服列表[(离绳头 x, 宽, 长, 颜色, 样式)])；样式 sari 纱丽（长、带金边）/ shirt / lungi（格子）/ towel
LAUNDRY = [
    ('a', 208, 292, 86, 86, 0, [(2, 8, 13, (200, 50, 70), 'sari'), (14, 5, 7, (240, 238, 228), 'shirt'),
                                (24, 9, 14, (230, 160, 40), 'sari'), (40, 6, 9, (70, 110, 170), 'lungi'),
                                (52, 4, 6, (240, 236, 220), 'towel'), (62, 9, 12, (110, 60, 140), 'sari')]),
    ('d', 642, 682, 73, 75, 3, [(3, 6, 15, (60, 140, 120), 'sari'), (13, 5, 7, (236, 232, 220), 'shirt'),
                                (22, 6, 9, (200, 70, 60), 'lungi'), (31, 5, 13, (236, 196, 70), 'sari')]),
    ('g', 1062, 1164, 85, 85, 0, [(4, 9, 14, (220, 120, 150), 'sari'), (18, 5, 7, (150, 190, 220), 'shirt'),
                                  (30, 6, 9, (60, 90, 70), 'lungi'), (48, 9, 13, (240, 210, 90), 'sari'),
                                  (64, 4, 6, (240, 240, 232), 'towel'), (78, 8, 12, (180, 60, 50), 'sari')]),
]
LAUNDRY_BOXES = [('laundry_a', (204, 84, 296, 104)), ('laundry_d', (638, 70, 688, 96)),
                 ('laundry_g', (1058, 42, 1234, 104))]
TARPS = [(SPICE_STALL[0] - 2, SPICE_STALL[1] + 2, 98, (214, 128, 60)), (CHAI_STALL[0] - 4, BENCH[1] + 4, 96, (64, 110, 170))]
TARP_BOX = (198, 94, 428, 108)
BIRD_BOXES = [('birds_a', (312, 62, 380, 84)), ('birds_b', (724, 60, 786, 84)), ('birds_c', (1174, 66, 1202, 84))]
STEAM_BOX = (334, 70, 364, 99)
SHRINE_BOX = (888, 66, 914, 131)


def _cloth(d, x0, y0, w, h, col, sty, f, k):
    """一件衣服：上沿固定在绳上，越往下摆得越多（风从左来）。"""
    ph = math.tau * f / N_ANIM + k * 1.3
    for r in range(h):
        u = r / max(1, h - 1)
        dx = round(1.6 * u * math.sin(ph) + 0.5 * u)
        for c in range(w):
            cc = col
            if sty == 'lungi' and ((c // 2 + r // 2) % 2 == 0):
                cc = (236, 232, 222)
            if sty == 'sari' and r >= h - 2:
                cc = (226, 190, 80)                                # 金边
            if sty == 'shirt' and r > 4 and c in (0, w - 1):
                continue
            if c == w - 1:
                cc = dk(cc, 0.82)
            if r == 0:
                cc = lt(cc, 0.18)
            px(d, x0 + c + dx, y0 + r, cc)
        if sty == 'shirt' and r == 1:
            px(d, x0 - 1 + dx, y0 + r, col)
            px(d, x0 + w + dx, y0 + r, dk(col, 0.82))


def laundry_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    k = 0
    for (name, x0, x1, y0, y1, sag, clothes) in LAUNDRY:
        for (ox, w, h, col, sty) in clothes:
            x = x0 + ox
            y = round(wire_y(x + w // 2, x0, y0, x1, y1, sag))
            _cloth(d, x, y + 1, w, h, col, sty, f, k)
            px(d, x + 1, y, (210, 210, 206))
            k += 1
    ax0, ax1 = ALLEY[0], ALLEY[1] - 1                              # 巷子里三道晾衣绳（远的小）
    for j, (u, y) in enumerate(ALLEY_LINES):
        a0, a1 = _avp(ax0, y, u), _avp(ax1, y + 3, u)
        s = 1 - u * 0.8
        for i in range(4):
            v = (i + 0.7) / 5
            x = a0[0] + (a1[0] - a0[0]) * v
            yy = a0[1] + (a1[1] - a0[1]) * v + 2 * math.sin(math.pi * v)
            col = ((200, 60, 80), (240, 236, 226), (60, 120, 170), (230, 170, 50), (120, 80, 150))[(i + j * 2) % 5]
            _cloth(d, round(x), round(yy) + 1, max(2, round(5 * s)), max(3, round(9 * s)), dk(col, 0.82),
                   'shirt' if i % 2 else 'sari', f, k)
            k += 1
    return im


def tarps_frame(t):
    """摊子上的遮阳布：上沿绑死在竹竿上，下沿一圈荷叶边随风起伏。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    for j, (x0, x1, y, col) in enumerate(TARPS):
        for x in range(x0, x1 + 1):
            wv = math.sin(math.tau * f / N_ANIM - x * 0.35 + j)
            hem = y + 4 + (1 if wv > 0.3 else 0) + (1 if wv > 0.85 else 0)
            for yy in range(y, hem + 1):
                c = col
                if yy == y:
                    c = lt(col, 0.25)
                elif yy >= hem - 1:
                    c = dk(col, 0.78)
                if j == 0 and (x - x0) % 8 < 4 and y < yy < hem - 1:
                    c = mix(c, (240, 220, 170), 0.35)              # 褪了色的条纹帆布
                px(d, x, yy, c)
            if wv > 0.6 and (x - x0) % 7 == 3:
                px(d, x, hem + 1, dk(col, 0.7))
    return im


def birds_frame(t):
    """电线上的鸽子 / 乌鸦：大多站着，各自按自己的节奏转头、低头理毛，乌鸦偶尔张嘴，有一只隔一阵扑一下翅膀。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    for i, (x, wi, kind) in enumerate(BIRDS_ON_WIRE):
        ax, ay, bx, by, sag = WIRES[wi]
        y = round(wire_y(x, ax, ay, bx, by, sag)) - 1
        body, head = ((120, 122, 132), (96, 98, 110)) if kind == 0 else ((40, 38, 44), (60, 58, 64))
        st = (f + 3 * i) % N_ANIM
        fc = 1 if i % 2 == 0 else -1
        if st == 4:
            fc = -fc                                               # 转头
        rect(d, x - 1, y - 2, x + 1, y, body)
        px(d, x - 2 * fc, y - (1 if st == 1 else 0), dk(body, 0.8))   # 尾巴（偶尔翘一下）
        bow = st == 6 and kind == 0
        hx, hy = (x + 2 * fc, y - 1) if bow else (x + 2 * fc, y - 3)
        px(d, hx, hy, head)
        px(d, hx + fc, hy, (200, 160, 80) if kind == 0 else (70, 70, 74))
        if kind == 1 and st == 6:                                  # 乌鸦张嘴
            px(d, hx + fc, hy - 1, (70, 70, 74))
        if kind == 0:
            px(d, x + fc, y - 3, lt(body, 0.2))
        if i % 4 == 1 and st in (2, 3):                            # 扑翅膀
            px(d, x - 1, y - 3, body)
            px(d, x - 2, y - 4 - (st == 3), body)
            px(d, x + 1, y - 4 - (st == 2), body)
    return im


def steam_frame(t):
    """茶壶冒的蒸汽：几团半透明的白气从壶盖上往上飘、越来越淡、往右偏。"""
    im = A._new(PW, H)
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    f = int(math.floor(t * FPS_STEAM + 1e-6)) % N_STEAM
    x0, y0 = CHAI_STALL[0] + 9, 95
    for i in range(5):
        u = ((f / N_STEAM) + i / 5) % 1.0
        x = x0 + u * 8 + 2 * math.sin(u * 5 + i)
        y = y0 - u * 22
        r = 1 + u * 2.5
        a = int(170 * (1 - u))
        d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=(240, 240, 236, a))
    im.alpha_composite(lay)
    return im


def shrine_frame(t):
    """神龛：油灯的火苗跳、一根香的烟往上绕、塔尖上的小旗飘。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * 8.0 + 1e-6)) % N_ANIM
    cx = (SHRINE[0] + SHRINE[1]) // 2
    fl = (0, 1, 0, -1, 1, 0, -1, 0)[f]                             # 火苗
    px(d, cx, 127, (255, 220, 120))
    px(d, cx + (fl > 0), 126, (250, 170, 60))
    if f % 3 != 2:
        px(d, cx + fl, 125, (240, 120, 40))
    sx = cx + 6                                                    # 香 + 烟
    vl(d, sx, 126, 130, (150, 60, 40))
    px(d, sx, 125, (240, 120, 60))
    for k in range(16):
        y = 124 - k
        x = sx + round(1.5 * math.sin(k * 0.5 - f * math.tau / N_ANIM))
        if (k + f) % 5 != 0:
            px(d, x, y, (214, 210, 204) if k < 9 else (196, 194, 190))
    for k in range(7):                                             # 小旗（三角形，往右飘）
        wv = round(math.sin(f * math.tau / N_ANIM - k * 0.9))
        top = 68 + k // 3
        bot = 74 - k // 2
        for y in range(top, bot):
            px(d, cx + 1 + k, y + wv, (226, 110, 40) if k < 5 else (240, 150, 60))
    return im


STRIPS = [(n, b, N_ANIM, FPS_ANIM, laundry_frame) for (n, b) in LAUNDRY_BOXES] + \
         [('tarps', TARP_BOX, N_ANIM, FPS_ANIM, tarps_frame)] + \
         [(n, b, N_ANIM, FPS_ANIM, birds_frame) for (n, b) in BIRD_BOXES] + \
         [('steam', STEAM_BOX, N_STEAM, FPS_STEAM, steam_frame), ('shrine', SHRINE_BOX, N_ANIM, 8.0, shrine_frame)]


WINDOW_PEOPLE = [('chai', 1, 2, 'old'), ('pink', 1, 0, 'kid'), ('old', 0, 2, 'woman'), ('spice', 0, 3, 'woman'),
                 ('tall', 1, 0, 'old')]   # (楼名, 第几层, 第几扇, 谁)：开着的窗里探出头的住户


def draw_window_people(im):
    """几扇开着的窗里的住户（只露头和肩膀，窗里暗，颜色压灰）：看街的老头、趴着窗的小孩、晾衣服的妇女。"""
    byname = {b['name']: b for b in BLDS}
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    for k, (name, fi, wi, who) in enumerate(WINDOW_PEOPLE):
        b = byname[name]
        f = b['floors'][fi]
        x0, x1 = b['x']
        xs = f.get('xs') or _win_xs(x0 + 4, x1 - 1 - 4, f['n'], f['w'])
        wx = xs[wi]
        cx = wx + f['w'] // 2 - (1 if who != 'woman' else 0)
        if f['states'][wi % len(f['states'])] == 'h':              # 只开了左边一扇：人在左半边
            cx = wx + 2
        yb = f['y'] + f['h'] - 1
        sk = SKIN[(k + 1) % len(SKIN)]
        hy = yb - (8 if who == 'kid' else 11)
        rect(d, cx - 2, hy, cx + 1, hy + 4, sk)
        vl(d, cx + 1, hy + 1, hy + 4, dk(sk, 0.78))
        hl(d, cx - 2, cx + 1, hy, (220, 220, 214) if who == 'old' else HAIR)
        if who == 'woman':
            vl(d, cx - 3, hy + 1, hy + 6, HAIR)
            col = SARIS[k % len(SARIS)]
        else:
            col = (236, 232, 222) if who == 'old' else (90, 140, 190)
        rect(d, cx - 3, hy + 5, cx + 2, yb, col)
        vl(d, cx + 2, hy + 5, yb, dk(col, 0.8))
        if who == 'kid':                                           # 趴在窗台上的两只手
            px(d, cx - 3, yb, sk)
            px(d, cx + 2, yb, sk)
    lay = haze_img(A._grade(lay, sat=0.75), 0.18, 0.18, col=(170, 160, 150))
    im.alpha_composite(lay)


def draw_laundry_ropes(im):
    """晾衣绳本身（静止，画在近景里；衣服在 laundry strip）。"""
    d = ImageDraw.Draw(im)
    for (name, x0, x1, y0, y1, sag, clothes) in LAUNDRY:
        for x in range(x0, x1 + 1):
            px(d, x, round(wire_y(x, x0, y0, x1, y1, sag)), (70, 64, 60))
        for x in (x0, x1):
            rect(d, x - 1, y0 - 1 if x == x0 else y1 - 1, x, (y0 if x == x0 else y1) + 1, (60, 60, 64))


# ============================================================ 下雨（key rain）/ 雨停那一道光（key sunbeam）
@lru_cache(maxsize=1)
def wet_img():
    """湿地面（盖住近景 y 138–179）：整体变暗变冷；马路上照出上面的店面 / 车 / 人（以 y 147.5 为镜面，竖着拉成一道道），
    积水的地方倒影更清楚、偏天光；钢轨和路缘石的湿边更亮。从近景本身算出来，所以和近景的东西一一对得上。"""
    near = np.array(near_img()).astype(np.float32)
    y0 = FOOT_Y
    h = H - y0
    out = near[y0:].copy()
    out[..., :3] *= np.array((0.74, 0.77, 0.84), np.float32)
    pud = A._fbm(PW + 8, h * 3 + 8, 10, seed=601)[4:4 + h * 3:3, 4:4 + PW]
    bay = A._bayer(PW, H)[y0:]
    sky = np.array((150, 156, 164), np.float32)
    for y in range(STREET_Y, H):
        r = y - STREET_Y
        src = 147 - r
        row = (near[src] + near[max(0, src - 1)]) * 0.5
        dx = int(round(1.2 * math.sin(r * 1.7)))
        row = np.roll(row, dx, axis=0)
        k = np.full(PW, 0.32 * (1 - r / 44), np.float32)
        cols = np.array([hash01(x // 2, 611) for x in range(PW)], np.float32)
        k[cols < 0.22] *= 0.5                                      # 竖着的一道道（倒影被雨打散）
        p = pud[y - y0]
        wet = (p > 0.6) | ((p > 0.57) & (bay[y - y0] < 0.5))
        k[wet] = 0.58
        refl = row[:, :3]
        refl = np.where(wet[:, None], refl * 0.8 + sky * 0.2, refl)
        out[y - y0, :, :3] = out[y - y0, :, :3] * (1 - k[:, None]) + refl * k[:, None]
        edge = (p > 0.54) & (p <= 0.57)
        out[y - y0, edge, :3] *= 0.86
    for ry in RAILS:
        out[ry - y0, :, :3] = np.minimum(255, out[ry - y0, :, :3] * 1.25 + 14)
    out[KERB_Y - y0, :, :3] = np.minimum(255, out[KERB_Y - y0, :, :3] * 1.15 + 10)
    out[..., 3] = 255
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')


def rain_frame(t):
    """雨丝（整屏，屏幕坐标）：一百多道斜线往左下落，近的长、亮，远的短、淡；每道沿自己那条斜线一圈一圈落，n 帧闭合。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_RAIN + 1e-6)) % N_RAIN
    span = H + 40
    for i in range(150):
        near_ = hash01(i, 801) < 0.35
        L = int(hrange(7, 11, i, 802)) if near_ else int(hrange(4, 7, i, 803))
        a = int(hrange(120, 170, i, 804)) if near_ else int(hrange(60, 100, i, 805))
        ph = hash01(i, 806)
        y = -20 + ((ph + f / N_RAIN) % 1.0) * span
        x = hrange(-40, W + 50, i, 807) - 0.25 * (y + 20)
        col = (214, 222, 236, a) if near_ else (190, 200, 216, a)
        d.line((round(x), round(y), round(x + 0.25 * L), round(y - L)), fill=col)
    return im


def splash_frame(t):
    """地上的雨点（屏幕坐标，y 146–179）：一个点溅起一个小皇冠，下一帧变成一圈扁扁的涟漪。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_SPLASH + 1e-6)) % N_SPLASH
    for i in range(46):
        p = int(hash01(i, 811) * N_SPLASH)
        x = int(hrange(2, W - 4, i, 812))
        y = int(hrange(STREET_Y + 1, H - 2, i, 813))
        if i % 3 == 0:
            y = int(hrange(FOOT_Y + 1, KERB_Y - 1, i, 814))
        age = (f - p) % N_SPLASH
        c = (206, 214, 226, 190)
        if age == 0:
            d.point((x, y - 1), fill=c)
            d.point((x - 1, y - 2), fill=c)
            d.point((x + 1, y - 2), fill=c)
        elif age == 1:
            d.ellipse((x - 2, y - 1, x + 2, y + 1), outline=(190, 200, 214, 140))
        elif age == 2 and i % 2 == 0:
            d.ellipse((x - 3, y - 1, x + 3, y + 1), outline=(176, 186, 200, 70))
    return im


RAIN_BOX = (0, 0, W, H)
SPLASH_BOX = (0, FOOT_Y, W, H)
BEAM_X0 = 380


@lru_cache(maxsize=1)
def beam_img():
    """雨停：从左上云缝里斜照下来的一道光（暖白、半透明、边上淡），落在 x 560–620 的路面上一片亮斑，光里几粒浮尘。"""
    w = 320
    im = A._new(w, H)
    for (grow, al) in ((10, 26), (5, 30), (0, 36)):
        lay = A._new(w, H)
        ImageDraw.Draw(lay).polygon([(40 - grow, 0), (92 + grow, 0), (250 + grow, 176), (160 - grow, 176)],
                                    fill=(255, 240, 200, al))
        im.alpha_composite(lay)
    lay = A._new(w, H)
    ld = ImageDraw.Draw(lay)
    for (rx, ry, al) in ((52, 8, 34), (38, 6, 40), (24, 4, 48)):
        ld.ellipse((205 - rx, 165 - ry, 205 + rx, 165 + ry), fill=(255, 242, 206, al))
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    for i in range(18):
        v = hash01(i, 821)
        y = int(v * 170)
        x = int(40 + (210 - 40) * v * 0.95 + hrange(4, 60, i, 822))
        d.point((x, y), fill=(255, 250, 230, 150))
    return im


# ============================================================ 楼顶的牛仔帽（key roof_hh）
HH_BOX = (HH[0] - 8, HH[1] - 12, HH[0] + 9, HH[1])


def hh_img(on):
    """F 楼顶女儿墙后面蹲着的人影：只露出肩膀、脑袋和一顶宽檐牛仔帽（10 px 高）；嘴边一点烟头的火。"""
    w, h = HH_BOX[2] - HH_BOX[0], HH_BOX[3] - HH_BOX[1]
    im = A._new(w, h)
    if not on:
        return im
    d = ImageDraw.Draw(im)
    cx = HH[0] - HH_BOX[0]
    SIL, SIL_H = (50, 42, 48), (74, 64, 70)
    HAT, HAT_H, HAT_D = (96, 74, 56), (132, 104, 76), (64, 48, 40)
    rect(d, cx - 4, h - 3, cx + 4, h - 1, SIL)                     # 肩膀（贴着女儿墙）
    px(d, cx - 4, h - 3, SIL_H)
    rect(d, cx - 2, h - 6, cx + 1, h - 4, SIL)                     # 脑袋（帽檐的影里）
    px(d, cx + 1, h - 5, (96, 74, 62))
    hl(d, cx - 6, cx + 5, h - 7, HAT_D)                            # 帽檐（宽、两头往上翘）
    hl(d, cx - 5, cx + 4, h - 7, HAT)
    px(d, cx - 6, h - 8, HAT)
    px(d, cx + 5, h - 8, HAT)
    rect(d, cx - 3, h - 10, cx + 2, h - 8, HAT)                    # 帽冠（中间一道凹）
    hl(d, cx - 3, cx + 2, h - 10, HAT_H)
    px(d, cx, h - 10, HAT_D)
    hl(d, cx - 3, cx + 2, h - 8, HAT_D)
    px(d, cx + 3, h - 4, (255, 150, 60))                           # 烟头
    return im


def draw_rooftop_f(im):
    """F 楼顶：左边一间楼梯间（小门、檐）+ 架在铁腿上的水箱 + 一根天线；女儿墙后面是平台。"""
    d = ImageDraw.Draw(im)
    x0 = B_TALL[0] + 4
    WALLc = (176, 182, 184)
    rect(d, x0, 26, x0 + 26, 40, WALLc)
    vl(d, x0 + 26, 26, 40, (140, 146, 150))
    rect(d, x0 - 1, 24, x0 + 27, 25, (214, 214, 208))
    hl(d, x0, x0 + 27, 26, (120, 124, 128))
    rect(d, x0 + 4, 30, x0 + 9, 40, (80, 70, 64))
    vl(d, x0 + 4, 30, 40, (56, 48, 46))
    for (lx) in (x0 + 13, x0 + 23):
        vl(d, lx, 14, 23, (70, 72, 74))
    rect(d, x0 + 12, 6, x0 + 24, 14, (60, 62, 66))                 # 水箱
    hl(d, x0 + 12, x0 + 24, 6, (110, 112, 116))
    vl(d, x0 + 24, 6, 14, (44, 46, 50))
    _antenna(d, x0 + 34, 22, 18)
    for i in range(2):
        stain(im, x0 + 3 + i * 14, 27, 10, 950 + i, width=2)


# ============================================================ 前景（人前面，k 1.3）：两根近处的电车线杆
FG_POLES = [300, 1340]          # 前景世界 x（屏幕 x = 它 − camX·1.3）：镜头 0–235 和 790–960 才看得见，战斗段（镜头 ~400）看不见
FG_X0 = 136


@lru_cache(maxsize=1)
def fg_img():
    w = FG_POLES[-1] - FG_X0 + 30
    im = A._new(w, H)
    d = ImageDraw.Draw(im)
    for j, P in enumerate(FG_POLES):
        X = P - FG_X0
        for y in range(H):
            for k, c in enumerate(((78, 96, 88), (60, 76, 70), (46, 58, 54), (40, 50, 48), (30, 38, 36))):
                px(d, X - 2 + k, y, c)
        for y in (40, 96, 150):
            rect(d, X - 3, y, X + 3, y + 2, (60, 76, 70))
            hl(d, X - 3, X + 3, y, (100, 120, 110))
        if j == 0:                                                 # 挂路灯的弯臂
            d.arc((X - 2, 4, X + 22, 30), 180, 270, fill=C((50, 62, 58)), width=2)
            rect(d, X + 9, 3, X + 17, 5, (50, 62, 58))
            rect(d, X + 10, 6, X + 16, 9, (220, 214, 190))
            hl(d, X + 9, X + 17, 10, (50, 62, 58))
        else:                                                      # 杆上一只铁皮接线盒 + 两道箍
            rect(d, X + 3, 70, X + 8, 80, (110, 116, 110))
            hl(d, X + 3, X + 8, 70, (150, 156, 150))
            vl(d, X + 8, 71, 80, (76, 82, 78))
            px(d, X + 5, 75, (60, 60, 60))
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    return Image.fromarray(a, 'RGBA')


# ============================================================ 组装
@lru_cache(maxsize=1)
def build():
    near, ground = near_parts()
    fg = fg_img()
    bb = fg.getbbox()
    fg0 = fg.crop(bb)
    return dict(sky=sky_img(), clouds=clouds_img(), rain_sky=rain_sky_img(), clear_sky=clear_sky_img(),
                far=far_img(), mid=mid_img(), near=near, ground=ground, wet=wet_img(), beam=beam_img(),
                hh=[hh_img(False), hh_img(True)], fg=[fg0, tinted(fg0, RAIN_TINT)], fg_xy=(FG_X0 + bb[0], bb[1]),
                birds=[bird_img(0), bird_img(1)])


def compose(camX, t=0.5, state=None, fg=True, js=True):
    """直接拼一帧（不经导出），预览 / 自检用。js=True 时 tint 的 alpha × 数值（同 engine\\bg.js）；
    js=False 时同 ref_render（真值就画满 alpha）。"""
    st = state or {}
    R = build()
    rain, sun, hh = st.get('rain', 0) or 0, st.get('sunbeam', 0) or 0, st.get('roof_hh', 0) or 0
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    o = int(math.floor(camX * CLOUD_K + t * CLOUD_VX)) % 640
    out.alpha_composite(_tile(R['clouds'], 1280).crop((o, 0, o + W, R['clouds'].height)))
    if rain:
        o = int(math.floor(camX * RAINSKY_K + t * RAINSKY_VX)) % 640
        out.alpha_composite(_tile(R['rain_sky'], 1280).crop((o, 0, o + W, R['rain_sky'].height)))
    if sun:
        out.alpha_composite(R['clear_sky'])
    for key, k in (('far', FAR_K),):
        ox = math.floor(camX * k)
        out.alpha_composite(R[key].crop((ox, 0, ox + W, H)))
    for (y, vx, k, x0, bi) in BIRDS:
        x = (x0 + t * vx - camX * k) % 460 - 100
        paste(out, R['birds'][bi], math.floor(x), y)
    ox = math.floor(camX * MID_K)
    out.alpha_composite(R['mid'].crop((ox, 0, ox + W, H)))
    out.alpha_composite(R['near'].crop((camX, 0, camX + W, H)))
    if rain:
        paste(out, R['wet'], -camX, FOOT_Y)
    if sun:
        paste(out, R['wet'], -camX, FOOT_Y)
    for (name, box, n, fps, fn) in STRIPS:
        f = int(math.floor(t * fps)) % n
        fr = fn(f / fps).crop(box)
        paste(out, fr, box[0] - camX, box[1])
    paste(out, R['hh'][1 if hh else 0], HH_BOX[0] - camX, HH_BOX[1])
    for (key, v, tint) in (('rain', rain, RAIN_TINT), ('sunbeam', sun, SUN_TINT)):
        if v:
            a = tint[1] * (v if js else 1)
            out.alpha_composite(Image.new('RGBA', (W, H), _hex(tint[0]) + (int(255 * a),)))
    if sun:
        paste(out, R['beam'], BEAM_X0 - camX, 0)
    if rain:
        f = int(math.floor(t * FPS_SPLASH)) % N_SPLASH
        paste(out, splash_frame(f / FPS_SPLASH).crop(SPLASH_BOX), 0, SPLASH_BOX[1])
    if fg:
        fx, fy = R['fg_xy']
        paste(out, R['fg'][1 if rain else 0], fx - math.floor(camX * FG_K), fy)
        if rain:
            f = int(math.floor(t * FPS_RAIN)) % N_RAIN
            out.alpha_composite(rain_frame(f / FPS_RAIN))
    return out


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0)]
    cim, cy = BJ.crop_rows(R['clouds'])
    layers.append(dict(type='wrap', image=ex.img('clouds', cim), period=640, k=CLOUD_K, y=cy, vx=CLOUD_VX))
    layers.append(dict(type='wrap', image=ex.img('rain_sky', R['rain_sky']), period=640, k=RAINSKY_K, y=0,
                       vx=RAINSKY_VX, key='rain'))
    layers.append(dict(type='image', image=ex.img('clear_sky', R['clear_sky']), x=0, y=0, screen=True, key='sunbeam'))
    fim, fy = BJ.crop_rows(R['far'])
    layers.append(dict(type='pano', image=ex.img('far', fim), k=FAR_K, x=0, y=fy))
    bk = [ex.img('flock%d' % i, im) for i, im in enumerate(R['birds'])]
    layers.append(dict(type='clouds', span=460,
                       clouds=[dict(image=bk[bi], x0=float(x0), y=y, vx=vx, k=k) for (y, vx, k, x0, bi) in BIRDS]))
    mim, my = BJ.crop_rows(R['mid'])
    layers.append(dict(type='pano', image=ex.img('mid', mim), k=MID_K, x=0, y=my))
    nim, ny = BJ.crop_rows(R['near'])
    layers.append(dict(type='pano', image=ex.img('near', nim), k=1.0, x=0, y=ny))
    wk = ex.img('wet', R['wet'])
    layers.append(dict(type='image', image=wk, x=0, y=FOOT_Y, k=1.0, key='rain'))
    layers.append(dict(type='image', image=wk, x=0, y=FOOT_Y, k=1.0, key='sunbeam'))
    for (name, box, n, fps, fn) in STRIPS:
        layers.append(ex.bake(name, box, n, fps, fn, screen=False, k=1.0))
    hk = [ex.img('roof_hh%d' % i, im) for i, im in enumerate(R['hh'])]
    layers.append(dict(type='pick', key='roof_hh', values=[0, 1], images=hk, x=HH_BOX[0], y=HH_BOX[1], k=1.0))
    layers.append(dict(type='tint', color=RAIN_TINT[0], alpha=RAIN_TINT[1], key='rain'))
    layers.append(dict(type='tint', color=SUN_TINT[0], alpha=SUN_TINT[1], key='sunbeam'))
    layers.append(dict(type='image', image=ex.img('beam', R['beam']), x=BEAM_X0, y=0, k=1.0, key='sunbeam'))
    sp = ex.bake('splash', SPLASH_BOX, N_SPLASH, FPS_SPLASH, splash_frame, screen=True, key='rain')
    layers.append(sp)
    fx, fy = R['fg_xy']
    fk = [ex.img('fg%d' % i, im) for i, im in enumerate(R['fg'])]
    fg = [dict(type='pick', key='rain', values=[0, 1], images=fk, x=fx, y=fy, k=FG_K),
          ex.bake('rain', RAIN_BOX, N_RAIN, FPS_RAIN, rain_frame, screen=True, key='rain')]
    anchors = dict(ANCHORS)
    anchors.update(spice_box=[SPICE_STALL[0], 112, SPICE_STALL[1], KERB_Y],
                   chai_box=[CHAI_STALL[0], 94, BENCH[1], KERB_Y],
                   taxi_box=[TAXI[0] - 2, 104, TAXI[1] + 2, KERB_Y + 1],
                   rickshaw_box=[RICKSHAW[0], 90, RICKSHAW[1], KERB_Y + 1],
                   shrine_box=[SHRINE[0] - 4, 66, SHRINE[1] + 4, KERB_Y],
                   roof_box=list(HH_BOX), alley_box=[ALLEY[0], 24, ALLEY[1], KERB_Y],
                   station_arch=[ARCH[0] - ARCH[1], ARCH[2] - ARCH[1], ARCH[0] + ARCH[1] + 1, BASE_Y],
                   billboard=list(BILL), tram_stop=[TRAM_STOP_X, 96], paan=[(PAAN[0] + PAAN[1]) // 2, 150],
                   pump=[150, 150], fruit=[(FRUIT[0] + FRUIT[1]) // 2, 152], battle_clear=[440, 720], rails=list(RAILS),
                   kerb=KERB_Y)
    st = ex.stage(PW, GROUND, WALK, layers, fg, anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


STAND = ('arrive', 'spice', 'spice_vendor', 'chai', 'cow', 'taxi', 'rickshaw', 'shrine', 'alley_mouth')


def _checks(ex, BJ, st, R):
    imgs = ex.images
    cams = list(range(0, PW - W + 1, 80))
    states = [{}, dict(rain=1), dict(sunbeam=1), dict(roof_hh=1), dict(rain=1, roof_hh=1)]
    # 1 各镜头整屏不露黑（晴天 / 雨天 / 雨停 / 楼顶有人）
    bad = 0
    for camX in cams:
        for t in (0.0, 0.75, 1.5):
            for s in states:
                im = np.array(BJ.ref_render(st, imgs, camX, t, s).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('加尔各答街 镜头 0–960（每 80）× 3 个时刻 × 5 种状态 整屏都有画（没有露黑）', bad)
    for k in ('sky', 'rain_sky', 'clear_sky'):
        ex.checked('%s 整张不透明' % k, int((np.array(R[k])[..., 3] != 255).sum()))
    a = np.array(R['near'])
    ex.checked('近景 人行道 / 路缘 / 马路（y 138–179）整条不透明', int((a[FOOT_Y:, :, 3] != 255).sum()))
    ex.checked('近景只有 0 / 255 两种透明度', int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum()))
    ex.checked('湿地面整张不透明、和近景同宽', int((np.array(R['wet'])[..., 3] != 255).sum()) + abs(R['wet'].width - PW))
    semi = sum(int(((np.array(f)[..., 3] > 0) & (np.array(f)[..., 3] < 255)).sum()) for f in R['fg'])
    ex.checked('前景只有 0 / 255 两种透明度', semi)
    # 2 strip 闭合 + 帧条宽 + 每帧都在动
    extra = [('splash', SPLASH_BOX, N_SPLASH, FPS_SPLASH, splash_frame), ('rain', RAIN_BOX, N_RAIN, FPS_RAIN, rain_frame)]
    for (name, box, n, fps, fn) in STRIPS + extra:
        T = n / fps
        ex.checked('strip %s %.2f s 闭合（t=0 vs t=%.2f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
    # 3 锚点在地图里；站人的锚点在可走带 / walk_x 里
    out = 0
    wx = ANCHORS['walk_x']
    for k, v in ANCHORS.items():
        if k == 'walk_x':
            out += not (0 <= v[0] < v[1] <= PW)
        else:
            out += not (0 <= v[0] <= PW and 0 <= v[1] <= H)
            if k in STAND:
                out += not (WALK[0] <= v[1] <= WALK[1] and wx[0] <= v[0] <= wx[1])
    for k in ('spice_box', 'chai_box', 'taxi_box', 'rickshaw_box', 'shrine_box', 'roof_box', 'alley_box', 'station_arch',
              'billboard'):
        b = st['anchors'][k]
        out += not (0 <= b[0] < b[2] <= PW and 0 <= b[1] < b[3] <= H)
    ex.checked('锚点都在地图里、站人的锚点在可走带 / walk_x 里（不满足的条数）', out)
    # 4 pick 每张尺寸一致；楼顶人影：0 张是空的、1 张有人、人影在 anchors.roof 一带
    ex.checked('roof_hh pick 两张尺寸一致', 0 if R['hh'][0].size == R['hh'][1].size else 1)
    h0, h1 = np.array(R['hh'][0]), np.array(R['hh'][1])
    ex.checked('roof_hh=0 那张全透明', int((h0[..., 3] > 0).sum()))
    n1 = int((h1[..., 3] > 0).sum())
    ys, xs = np.nonzero(h1[..., 3] > 0)
    cx, cy = HH_BOX[0] + xs.mean(), HH_BOX[1] + ys.mean()
    ex.checked('roof_hh=1 人影 %d px、高 %d px（8–12）、中心 (%.0f, %.0f) 离 anchors.roof ≤ 4 px' %
               (n1, ys.max() - ys.min() + 1, cx, cy),
               0 if (n1 >= 30 and 8 <= ys.max() - ys.min() + 1 <= 12 and abs(cx - ANCHORS['roof'][0]) <= 4 and
                     abs(cy - ANCHORS['roof'][1]) <= 4) else 1)
    nb = np.array(R['near'])
    sil = nb[HH_BOX[1]:HH_BOX[3], HH_BOX[0]:HH_BOX[2]]
    ex.checked('人影后面（女儿墙以上）是空的：近景在人影框里不透明的像素（女儿墙那一行以上）',
               int((sil[:-1, :, 3] > 0)[h1[:-1, :, 3] > 0].sum()))
    ex.checked('前景 pick 两张尺寸一致', 0 if R['fg'][0].size == R['fg'][1].size else 1)
    ex.checked('前景 rain 那张 = 原图罩同一层雨天色（逐像素）', BJ.ndiff_rgba(R['fg'][1], tinted(R['fg'][0], RAIN_TINT)))
    # 5 战斗场地：x 440–720 的可走带（y 150–176）上只有路面纹理，没有挡人的东西
    g = np.array(R['ground'])
    diff = np.abs(nb[150:177, 440:721, :3].astype(int) - g[150:177, 440:721, :3].astype(int)).max(-1) > 0
    ex.checked('战斗场地 x 440–720、y 150–176：近景 = 纯路面（不同的像素）', int(diff.sum()))
    vis = [c for c in range(0, PW - W + 1, 4) for P in FG_POLES
           if -6 < P - math.floor(c * FG_K) < W + 6 and 380 <= c <= 520]
    ex.checked('前景的杆在战斗镜头（camX 380–520）里看不见（看得见的镜头数）', len(vis))
    # 6 下雨：更暗、更冷；雨停：光柱那里比旁边亮
    dark, cool = 0, 0
    for camX in (0, 480, 960):
        g0 = np.asarray(BJ.ref_render(st, imgs, camX, 0.5, {}, fg=False).convert('RGB'), np.float32)
        g1 = np.asarray(BJ.ref_render(st, imgs, camX, 0.5, dict(rain=1), fg=False).convert('RGB'), np.float32)
        dark += int(_lum(g1).mean() > _lum(g0).mean() * 0.8)
        cool += int((g1[..., 2] - g1[..., 0]).mean() <= (g0[..., 2] - g0[..., 0]).mean())
    ex.checked('下雨 rain=1：整体亮度降到 80 % 以下（没降够的镜头数）', dark)
    ex.checked('下雨 rain=1：更冷（B−R 没变大的镜头数）', cool)
    g2 = np.asarray(BJ.ref_render(st, imgs, 400, 0.5, dict(sunbeam=1), fg=False).convert('RGB'), np.float32)
    inb = _lum(g2[150:176, 190:220]).mean()
    outb = _lum(g2[150:176, 20:50]).mean()
    ex.checked('雨停 sunbeam=1（镜头 400）：光斑（屏幕 x 190–220）比旁边（x 20–50）亮 %.0f vs %.0f' % (inb, outb),
               0 if inb > outb + 8 else 1)
    # 7 导出 vs 直接拼（含前景、雨丝、溅水）
    for camX in (0, 320, 480, 960):
        for t in (0.0, 1.25):
            for s in ({}, dict(rain=1), dict(sunbeam=1, roof_hh=1)):
                got = BJ.ref_render(st, imgs, camX, t, s)
                ex.checked('加尔各答街 camX=%d t=%.2f %s 导出 vs 直接拼' % (camX, t, s or '晴'),
                           BJ.ndiff(got, compose(camX, t, s, js=False)))
    # 8 街道不重样：近景楼面（y 0–137）任意两块 64 px 宽、不重叠的窗口都差得够多
    lum = _lum(nb[:BASE_Y, :, :3].astype(np.float32))
    blocks = [(x, lum[:, x:x + 64]) for x in range(0, PW - 64 + 1, 16)]
    worst = 1e9
    for i, (xa, ba) in enumerate(blocks):
        for xb, bb_ in blocks[i + 1:]:
            if xb - xa >= 64:
                worst = min(worst, float(np.abs(ba - bb_).mean()))
    ex.checked('街道不重样：任意两块不重叠的 64 px 楼面平均亮度差最小 %.1f（≥ 12）' % worst, 0 if worst >= 12 else 1)
    # 9 大小
    idx = (ex.c.get('index') if isinstance(ex.c, dict) else None) or {}
    tot = sum(v['bytes'] for k, v in idx.items() if k.startswith('bg/%s/' % ex.key))
    if tot:
        ex.checked('整张背景 %.0f KB ≤ 900 KB' % (tot / 1024), max(0, tot - 900 * 1024))
    nm = _lum(nb[..., :3].astype(np.float32))
    ex.note('可走带后面的亮度：马路 y148–176 均值 %.0f 标准差 %.1f；一楼铺面 y104–137 均值 %.0f 标准差 %.1f' %
            (nm[148:177].mean(), nm[148:177].std(), nm[104:138].mean(), nm[104:138].std()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch4', 'calcutta_dev')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 320, 640, 960):
        compose(camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'solo_%d.png' % camX))
    for nm, st in (('rain', dict(rain=1)), ('sunbeam', dict(sunbeam=1)), ('roof_hh', dict(roof_hh=1))):
        cam = 880 if nm == 'roof_hh' else 400
        compose(cam, 0.5, st).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(od, 'solo_%s.png' % nm))
    print('ok')
