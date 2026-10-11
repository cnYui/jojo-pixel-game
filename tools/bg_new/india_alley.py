# -*- coding: utf-8 -*-
r"""india_alley —— 第4章 加尔各答：一条窄后巷，下着雨（第 7 战「皇帝 + 倒吊人」的场地）。

2026-10-11 第4章按体验版的精度重画（改前是 bg_asia._alley_static：一面平墙 + 镜子 + 橱窗 + 三块天蓝色的水洼）。
320 单屏，ground 156，可走带 y 146–176；侧视平视：看到的是巷子“对面”那堵墙（三栋旧楼并排），
镜头这一侧的楼只露出最上面一道挑檐（y 0–4），晾衣绳和电线从挑檐斜着拉到对面墙上——看得出巷子很窄。
颜色和加尔各答街（calcutta_street 最右边的巷口）一致：深灰黄灰泥、晾衣绳、水洼。

从左到右（巷子深处在左，巷口在右——剧情的站位：荷尔·荷斯、阿布德尔从右边的巷口进来，波鲁纳雷夫在左边的镜子前）：
  A 楼     x 0–107   最左边：墙上一块褪色的手绘老广告（只用色块）、墙角一台墨绿的手压水泵（水泥台子 + 出水嘴下一只铁皮桶）；
                     理发店：墙上一块铁皮招牌（剪刀 + 梳子图形）；**落地镜**（木框 x 23–72 × y 42–113，外沿往右歪 2 px，
                     顶上一块拱形雕花顶饰（左边低 1 px），两条腿站在地上，右腿短一截垫了块砖 → 有点歪；
                     左上角搭一条毛巾，右框挂着梳子剪刀），镜面是正的矩形 x 28–67 × y 46–109（anchor mirror_box =
                     [28,46,68,110]，右下不含），映出镜头这一侧的墙（暗、偏蓝灰：天 / 挑檐 / 带铁栏的窗 / 排水管 / 湿地面）；
                     理发店门洞 x 78–103（红白条纹雨篷、里面一盏灯泡、理发椅、墙上小镜子和日历）；
                     楼上一扇绿百叶窗 + 小阳台（栏杆上搭一条褐红纱丽）；楼顶女儿墙 + 远处屋顶（水箱、天线）
  B 楼     x 108–197 住家：一扇旧木门（双扇、褪色的青蓝漆剥落露出木头、铁钉、挂锁、上面一扇拱形铁花气窗、门牌）；
                     一根铸铁排水管 x 150–153 从顶上下来，出水口弯向排水沟；电表箱 + 一大把乱电线；
                     褪色的旧海报（只用色块：撕掉一半的品红 / 黄 / 青）；墙根一口大陶水缸（铝盖 + 钢杯）；
                     门左边一只装满垃圾的铁皮桶；楼上一个阳台（花盆）+ 一扇铁栅窗
  C 楼     x 198–303 街角的小杂货店（店门开在大街那一面，看不见）：黄底红字的铁皮招牌（伪天城文 + 瓶子 / 罐子图形）、
                     瓦楞铁皮雨篷；**橱窗**（绿漆木框 x 204–291 × y 61–117，框顶挂一串万寿菊花环），玻璃 x 208–287 × y 64–113
                     （anchor window_box = [208,64,288,114]），里面三层货架（糖果罐、汽水瓶、铁皮罐、肥皂、一串零食袋）——压暗；
                     玻璃上映着镜头这一侧的墙（和镜子里是同一堵墙）+ 两道斜反光；橱窗下一截绿漆木护板、
                     两袋麻袋、一摞装瓶子的木箱、一只煤油桶；转角（x 296–303，被大街的光照亮、隅石）挂蓝色路名牌、
                     一个铁灯架（白天关着），墙根一只蓝塑料桶 + 一把扫帚
  巷口     x 304–319 巷子通到大街：对街一栋浅色楼（雾蒙蒙）、店铺雨篷、打伞的路人、黄色出租车的车尾、湿的柏油路；
                     上面是开着的天（挑檐到 x 296 为止）——人从这里进来（anchor entrance [312,160]），雨停以后的光也从这里照进来
  墙根     y 132–141 返潮的墙脚（盐霜线、青苔）；y 142–144 明沟（几处门口盖着石板），y 145 沟沿石
  地面     y 146–179 湿石板 + 泥（压低了对比），贴着墙脚的十几行映出墙脚（湿地面的倒影）；
                     **三个水洼**中心 (92,172) / (173,172) / (276,172)，半宽 15 / 16 / 15、半高 3（y 169–175，两头各鼓出去一块），
                     远沿映墙脚（暗）→ 近沿映天（亮），几段亮条
  头顶     镜头这一侧的挑檐 y 0–4（x 0–296，波纹铁皮边、铁托架、吊着一盆绿萝）；四根晾衣绳（衬衫、毛巾、纱丽、
           格子笼吉、黄库尔塔……）、几根下垂的电线，墙上横拉的一把电线（瓷绝缘子），在 B|C 交界处拐上去

图层（从下到上）：
  static  alley            整张底图（不透明；阴天：上亮下暗、右边巷口那边亮一点、左边巷子深处暗一点、理发店门洞里的灯是暖的）
  pick    mirror           key 'mirror'，values [0, 1]（框 MIRROR_PICK，左上角 (18, 30)）：0 = 空图；1 = 镜子碎了
                           （玻璃大部分掉光、露出后面的木背板，框里剩一圈锯齿碎片 + 裂纹，镜子脚下 / 沟里一小片碎玻璃）
  pick    window           key 'window'，values [0, 1]（框 WINDOW_PICK，左上角 (198, 56)）：0 = 空图；1 = 橱窗碎了
                           （中间空了，直接看到货架，框边一圈锯齿碎片，护板顶和地上一小片碎玻璃）
  tint    rain             key 'rain'：#36445a × 0.40（JS：state.rain 是数字就当 alpha 的乘数，0 = 不画）
  strip   rain             key 'rain'：12 帧 @16 fps（0.75 s 闭合）整屏：两层斜雨丝 + 地上溅起的水花 + 水洼涟漪
                           + 雨篷 / 阳台滴水 + 排水管出水口的水柱 + 明沟里流动的水光
  pick    sunbeam          key 'sunbeam'，values [0, 1]（320×180，半透明叠加）：0 = 空图；1 = 雨停：整体暖一点、巷口那边亮得多
                           + 一道斜光从右上的巷口照下来（左边沿 x = 267 − 0.80·y，宽 42，里面两道更亮的光柱；
                           斜着扫过橱窗，落在 x 139–181 的地面上，湿石板 / 水洼 (173,172) 闪光；anchor sunbeam_spot [160,160]）
  strip   sun_motes        key 'sunbeam'：16 帧 @8 fps（2 s 闭合，框 (100,0)–(320,180)）光里飘的水汽亮点
  fg（画在人物前面）：
  strip   rain_fg          key 'rain'：12 帧 @16 fps 近处稀疏的长雨丝（alpha 很低，不挡人；不想要就把 fg 这一条删掉）
rain = 0（或没有）= 阴天不下雨（雨停），地面和水洼还是湿的。
光不用 glow 图层（bg_jojo.ref_render 不认识）；灯泡的暖光、湿地面的倒影都烘在底图里。

锚点（全部世界坐标；框都是 [x0,y0,x1,y1]、右下不含）：见 anchors()。
自检（ex.checked）：底图不透明；16 种 key 组合 × 3 个时刻不露黑、导出层 = 直接拼（逐像素）；三条 strip 闭合 / 不跳帧 /
  帧条宽 ≤ 4096 / 像素都在框里；锚点在地图里、站位锚点在可走范围里；pick 两张同尺寸、第 0 张空、只在自己的框里不同、
  玻璃区域 ≥ 60% 变了、两张 pick 不重叠且一起打开 = 各自叠上去；玻璃像素外框 = mirror_box / window_box 且框里全是玻璃、
  玻璃偏暗平整（亮度均值 45–115、标准差 ≤ 24）；水洼面积 / 中心 / 上下范围；物件都不进可走带；物件 x 范围；
  可走带 / 可走带后面的强边比例；总体积 ≤ 400 KB。
单独运行：python -B tools\bg_new\india_alley.py → tools\bg_new\_preview\ch4\after\india_alley_solo.png（六种状态）、
  india_alley_solo_rain.png（下雨连续 4 帧）
"""
import sys
sys.dont_write_bytecode = True

import io  # noqa: E402
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

W, H = 320, 180
GROUND = 156
WALK = (146, 176)
C4 = A._c4

# ---------------------------------------------------------------- x 范围（含两端）
MOUTH_X0 = 304                      # x 304–319 巷口外的大街（人从右边进来；剧情的站位按这个写）
A_X = (0, 107)
B_X = (108, 197)
C_X = (198, 303)                    # C 楼是街角的店：橱窗朝巷子，店门在大街那一面（看不见）
NEAR_X = (0, 296)                   # 镜头这一侧的挑檐

# ---------------------------------------------------------------- 竖向
A_ROOF = 15                         # A 楼女儿墙顶
C_ROOF = 9                          # C 楼女儿墙顶
A_BAND = (62, 65)                   # A 楼腰线
B_BAND = (58, 61)
PLINTH = (132, 141)                 # 返潮的墙脚
DRAIN = (142, 144)                  # 明沟
CURB = 145                          # 沟沿石
FLOOR0 = 146                        # 地面从这一行开始（= 可走带后沿）

# ---------------------------------------------------------------- 物件（含两端）
MIRROR_FRAME = (24, 42, 71, 113)
MIRROR_GLASS = (28, 46, 67, 109)
WINDOW_FRAME = (204, 61, 291, 117)
WINDOW_GLASS = (208, 64, 287, 113)
BARBER_DOOR = (78, 76, 103, 141)
WOOD_DOOR = (116, 76, 146, 141)
PIPE_X = (150, 153)
PUMP_X = 9                          # 墙角的手压水泵（铁柱 x 8–10）
BULB_BARBER = (90, 85)
PUDDLES = [(92, 172, 15, 3), (173, 172, 16, 3), (276, 172, 15, 3)]    # 中心 x, y，半宽，半高
SPEC_X = {'mirror': (22, 74), 'barber': (74, 108), 'door': (114, 148), 'pipe': (148, 157), 'store_window': (202, 293),
          'pump': (1, 18)}                    # 各物件（含毛巾 / 卡箍 / 门槛石 / 水桶）实际占的 x 范围（含两端；自检核对）

# pick 的框（右下不含）
MIRROR_PICK = (18, 30, 80, 156)
WINDOW_PICK = (198, 56, 300, 156)

# 雨停以后的那道光（从右上的巷口照进来）：左边沿 x = BEAM_X0 − y·BEAM_SLOPE，宽 BEAM_W
BEAM_X0, BEAM_W, BEAM_SLOPE = 267.0, 42.0, 0.80
BEAM_BOX = (100, 0, 320, 180)

N_RAIN, FPS_RAIN = 12, 16.0          # 0.75 s 一圈
N_MOTE, FPS_MOTE = 16, 8.0           # 2 s 一圈
RAIN_TINT = ('#36445a', 0.40)        # 和 calcutta_street 下雨的 tint 一样

# ---------------------------------------------------------------- 调色
PLA = {'A': (172, 156, 118), 'B': (162, 152, 116), 'C': (170, 154, 120)}   # 深灰黄灰泥（albedo，打光后 ≈ (138,126,98)）
WASH_B = (128, 150, 146)                                                   # B 楼下半截褪色的青绿涂料
BRICKS = [(150, 86, 64), (134, 74, 56), (160, 98, 72), (142, 82, 62)]
MORTAR = (160, 150, 128)
WOOD = dict(hi=(150, 106, 70), lt=(128, 88, 58), md=(104, 70, 46), dk=(78, 52, 36), dd=(52, 34, 26))
IRON = (46, 46, 50)
IRON_HI = (96, 98, 102)
GREEN = dict(hi=(118, 150, 124), lt=(96, 128, 106), md=(78, 108, 90), dk=(58, 82, 70), dd=(40, 56, 50))
TEAL = dict(hi=(132, 164, 166), lt=(110, 142, 146), md=(92, 122, 128), dk=(70, 96, 102), dd=(50, 68, 74))
TERRA = dict(hi=(190, 118, 80), lt=(168, 100, 66), md=(148, 84, 56), dk=(116, 64, 44), dd=(82, 44, 32))
SKIN = (120, 84, 62)
GLASS_EDGE = (226, 236, 242)
GLASS_RIM = (150, 174, 192)
GLASS_IN = (124, 146, 162)
MIRROR_KEY = (1, 2, 3)               # 镜面占位色（拼完以后换成倒影）
WINDOW_KEY = (1, 2, 5)               # 橱窗玻璃占位色
HOLE_KEY = (1, 2, 7)                 # 橱窗碎了以后的空洞（换成货架）


def R(d, box, col, outline=None):
    d.rectangle(box, fill=C4(col) if col is not None else None, outline=C4(outline) if outline else None)


def L(d, pts, col, w=1):
    d.line(pts, fill=C4(col), width=w)


def P(d, x, y, col, a=255):
    d.point((int(round(x)), int(round(y))), fill=C4(col, a))


def sh(c, k):
    return tuple(int(max(0, min(255, round(v * k)))) for v in c)


def blank(w=W, h=H):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def toimg(a):
    return Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA')


def rgba(a3):
    return toimg(np.concatenate([a3, np.full(a3.shape[:2] + (1,), 255, np.float32)], -1))


def mask_of(draw_fn, size=(W, H)):
    m = Image.new('L', size, 0)
    draw_fn(ImageDraw.Draw(m))
    return np.array(m) > 0


# ============================================================ 墙（numpy albedo）
def _noise1(seed, cell=4):
    return A._fbm(W, 1, cell, seed)[0]


def streaks(a, x0, x1, y0, lmin, lmax, seed, k=0.84, thr=0.52):
    """从一道檐口 / 窗台往下挂的水渍：一列列竖条，越往下越淡。"""
    n = _noise1(seed, 3)
    for x in range(max(0, x0), min(W, x1 + 1)):
        if n[x] < thr:
            continue
        ln = int(lmin + (lmax - lmin) * hash01(seed, x // 2, 7))
        for y in range(y0, min(H, y0 + ln)):
            u = (y - y0) / max(1, ln)
            a[y, x] *= k + (1 - k) * u ** 0.8


def damp(a, x0, x1, seed):
    """返潮的墙脚：不规则的上沿 + 一道盐霜线，越往下越暗、越绿。"""
    n = _noise1(seed, 6)
    for x in range(x0, x1 + 1):
        top = int(110 + 14 * n[x])
        a[top, x] = a[top, x] * 1.07
        if top - 1 >= 0 and hash01(x, seed, 3) < 0.5:
            a[top - 1, x] = a[top - 1, x] * 1.04
        for y in range(top + 1, PLINTH[1] + 1):
            u = (y - top) / max(1, PLINTH[1] - top)
            c = a[y, x] * (0.95 - 0.16 * u)
            a[y, x] = c * (1 - 0.14 * u) + np.array((84, 98, 70), np.float32) * 0.14 * u


def peel(a, cx, cy, rx, ry, seed, kind='brick'):
    """灰泥剥落：边上一圈翘起来的亮边，下沿一道影，里面露砖（或更早的一层旧漆）。"""
    nz = A._fbm(W, H, 3, seed)
    yy, xx = np.mgrid[0:H, 0:W]
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 + (nz - 0.5) * 1.1
    inside = d < 1.0
    lip = (d >= 1.0) & (d < 1.35)
    if kind == 'paint':
        old = np.array((178, 162, 146), np.float32)
        a[inside] = a[inside] * 0.35 + old * 0.65
        a[lip & (yy < cy)] *= 1.08
        a[lip & (yy >= cy)] *= 0.88
        return
    for y, x in zip(*np.nonzero(inside)):
        row = y // 3
        if y % 3 == 2:
            c = MORTAR
        else:
            off = 3 if row % 2 else 0
            if (x + off) % 7 == 6:
                c = MORTAR
            else:
                c = BRICKS[int(hash01((x + off) // 7, row, seed) * 4)]
        a[y, x] = c
        if y % 3 == 0:
            a[y, x] = a[y, x] * 1.06
    edge_top = lip & (yy <= cy)
    a[edge_top] *= 1.10
    sh_ = np.zeros_like(inside)
    sh_[1:] = inside[1:] & ~inside[:-1]                      # 洞的上沿往里一行是暗的（灰泥的厚度）
    a[sh_] *= 0.70
    a[lip & (yy > cy)] *= 0.86


def crack(a, x, y, n, seed, dx_bias=0.0):
    """一道细裂缝：往下随机走 n 步，暗线 + 右边一个亮像素；中途偶尔分叉。"""
    fx = float(x)
    for i in range(n):
        yy = y + i
        if not (0 <= yy < H):
            break
        fx += hrange(-0.9, 0.9, seed, i) + dx_bias
        xi = int(round(fx))
        if 0 <= xi < W - 1:
            a[yy, xi] *= 0.62
            a[yy, xi + 1] *= 1.06
        if hash01(seed, i, 9) < 0.06 and i > 3:
            bx = fx
            for j in range(int(hrange(3, 7, seed, i, 10))):
                bx += 0.8 if hash01(seed, i, 11) < 0.5 else -0.8
                yb = yy + j
                xb = int(round(bx))
                if 0 <= yb < H and 0 <= xb < W:
                    a[yb, xb] *= 0.72


def hband(a, x0, x1, y0, cols):
    for i, c in enumerate(cols):
        a[y0 + i, x0:x1 + 1] = c


@lru_cache(maxsize=1)
def wall_albedo():
    a = np.zeros((H, W, 3), np.float32)
    a[:, :B_X[0]] = PLA['A']
    a[:, B_X[0]:C_X[0]] = PLA['B']
    a[:, C_X[0]:] = PLA['C']
    big = A._fbm(W, H, 12, 41) - 0.5
    fine = A._fbm(W, H, 4, 43) - 0.5
    k = 1 + np.round((0.17 * big + 0.08 * fine) / 0.03) * 0.03
    a *= k[..., None]
    # B 楼下半截一层褪色的青绿涂料（大片剥落，上沿参差）
    nz = A._fbm(W, H, 5, 44)
    top = 66 + (8 * _noise1(45, 5)).astype(int)
    for x in range(B_X[0], B_X[1] + 1):
        for y in range(top[x], PLINTH[0]):
            if nz[y, x] > 0.36 + 0.12 * (1 - (y - top[x]) / 40.0):
                a[y, x] = a[y, x] * 0.42 + np.array(WASH_B, np.float32) * 0.58 * k[y, x]
                if y > 0 and nz[y - 1, x] <= 0.36 + 0.12 * (1 - (y - 1 - top[x]) / 40.0):
                    a[y, x] *= 1.08                              # 漆皮的边翘起来一点
    # A 楼：女儿墙、檐口、腰线
    x0, x1 = A_X[0], A_X[1]
    hband(a, x0, x1, A_ROOF, [(188, 176, 142), (170, 158, 122), PLA['A'], PLA['A'], (150, 138, 104), (112, 102, 80)])
    for x in range(x0, x1 + 1, 9):                                 # 女儿墙上一格格的透空砖（暗点）
        if x + 4 <= x1:
            a[A_ROOF + 2:A_ROOF + 4, x + 2:x + 5] = (112, 102, 82)
    hband(a, x0, x1, A_BAND[0], [(190, 178, 144), (160, 148, 114), (150, 138, 106), (104, 96, 76)])
    # B 楼腰线
    hband(a, B_X[0], B_X[1], B_BAND[0], [(186, 176, 142), (156, 148, 114), (146, 138, 106), (102, 96, 76)])
    # C 楼：女儿墙 + 檐口
    hband(a, C_X[0], C_X[1], C_ROOF, [(190, 178, 146), (172, 160, 126), PLA['C'], (150, 138, 108), (108, 98, 80)])
    # 楼和楼之间的接缝：B 往前凸一点（左边一道暗、右边一道亮）
    a[:, B_X[0]] *= 0.72
    a[:, B_X[0] + 1] *= 1.06
    a[C_ROOF:, C_X[0]] *= 0.70                                      # C 楼左边的壁柱
    a[C_ROOF:, C_X[0] + 1:C_X[0] + 4] *= 1.07
    a[C_ROOF:, C_X[0] + 4] *= 0.86
    a[C_ROOF:, 296] *= 0.84                                         # C 楼右边转角的壁柱（被大街的光照亮）
    a[C_ROOF:, 297:C_X[1] + 1] *= 1.07
    a[C_ROOF:, C_X[1]] *= 1.05
    # 水渍：檐口 / 腰线 / 阳台 / 招牌下面挂下来
    streaks(a, A_X[0], A_X[1], A_ROOF + 6, 6, 26, 51)
    streaks(a, A_X[0], A_X[1], A_BAND[1] + 1, 4, 16, 52, k=0.86)
    streaks(a, 76, 106, 54, 6, 18, 53, k=0.80, thr=0.45)            # A 阳台下
    streaks(a, B_X[0] + 2, B_X[1], B_BAND[1] + 1, 6, 24, 54)
    streaks(a, 118, 158, 36, 8, 22, 55, k=0.80, thr=0.45)           # B 阳台下
    streaks(a, 164, 186, 36, 4, 14, 56, k=0.84)
    streaks(a, C_X[0] + 5, 295, C_ROOF + 6, 6, 22, 57)
    streaks(a, 292, 302, 62, 4, 12, 58, k=0.86)
    streaks(a, 2, 20, 60, 10, 30, 60, k=0.86)                        # 水泵上面墙上的一片水渍
    for x in range(154, 160):                                       # 排水管旁边漏水的一长条湿印
        for y in range(56, 132):
            if hash01(x, 59) < 0.8:
                u = (y - 56) / 76.0
                a[y, x] *= 0.80 + 0.12 * u if x < 158 else 0.90 + 0.06 * u
    # 返潮的墙脚
    damp(a, 0, W - 1, 61)
    # 剥落
    for (cx, cy, rx, ry, sd, kind) in ((21, 52, 4, 9, 71, 'brick'), (75, 44, 4, 7, 72, 'paint'), (116, 50, 8, 5, 73, 'brick'),
                                       (190, 46, 6, 6, 74, 'brick'), (176, 126, 9, 4, 75, 'brick'), (112, 104, 3, 9, 76, 'paint'),
                                       (291, 28, 6, 5, 77, 'brick'), (247, 26, 5, 3, 78, 'paint'), (202, 96, 3, 10, 79, 'paint'),
                                       (60, 22, 6, 3, 80, 'paint'), (6, 30, 5, 7, 89, 'brick')):
        peel(a, cx, cy, rx, ry, sd, kind)
    # 裂缝
    for (x, y, n, sd, b) in ((104, 66, 22, 81, -0.1), (16, 22, 30, 82, 0.05), (150, 62, 10, 83, 0.0), (186, 62, 26, 84, 0.1),
                             (122, 8, 22, 85, 0.0), (258, 16, 18, 86, -0.05), (298, 66, 30, 87, 0.0), (76, 66, 10, 88, 0.0)):
        crack(a, x, y, n, sd, b)
    return a


# ============================================================ 地面（numpy albedo）
FLOOR_ROWS = [146, 149, 153, 158, 164, 171, 180]


@lru_cache(maxsize=1)
def floor_albedo():
    """湿石板（大小不一、缝很淡）+ 石板缺了的地方是泥；对比压低（人站在上面要清楚）。"""
    a = np.zeros((H, W, 3), np.float32)
    mud = A._fbm(W, H, 8, 91)
    grain = A._fbm(W, H, 2, 97) - 0.5
    sheen = A._fbm(W, H, 5, 92)
    base = np.array((108, 103, 93), np.float32)
    a[DRAIN[0]:] = base
    for i in range(len(FLOOR_ROWS) - 1):
        y0, y1 = FLOOR_ROWS[i], min(H, FLOOR_ROWS[i + 1])
        Lp = 14 + i * 6
        x = -int(hrange(0, Lp, i, 93))
        k = 0
        while x < W:
            ln = int(Lp + hrange(-5, 8, i, k, 94))
            f = 0.95 + 0.08 * hash01(i, k, 95)
            col = base * f
            ya = y0 + (1 if hash01(i, k, 98) < 0.3 and y1 - y0 > 4 else 0)        # 有的石板高低错一点
            xa, xb = max(0, x), min(W, x + ln)
            a[y0:y1, xa:xb] = col
            if xb > xa:
                a[ya, xa:xb] = col * 0.86                                          # 横缝（跟着这块石板）
                if ya + 1 < y1:
                    a[ya + 1, xa:xb] = col * 1.03
            if 0 <= x < W:                                                         # 竖缝
                a[ya:y1, x] = col * 0.84
            if hash01(i, k, 96) < 0.25 and xb - 3 > xa:                             # 缺了角
                a[y1 - 1, xb - 3:xb] = col * 0.86
            x += ln
            k += 1
    a[DRAIN[0]:] *= (1 + 0.05 * np.round(grain[DRAIN[0]:] / 0.2) * 0.2)[..., None]
    # 泥：石板缺了的地方（边上软一点）
    for y in range(FLOOR0, H):
        for x in range(W):
            m = mud[y, x]
            if m > 0.60:
                a[y, x] = a[y, x] * 0.40 + np.array((98, 88, 72), np.float32) * 0.60
            elif m > 0.57 and (x + y) % 2 == 0:
                a[y, x] = a[y, x] * 0.70 + np.array((98, 88, 72), np.float32) * 0.30
    # 湿的反光：一小段一小段横的亮条（天光）
    for y in range(FLOOR0 + 2, H):
        for x in range(W):
            if sheen[y, x] > 0.68 and (y + x // 9) % 4 == 0:
                a[y, x] = a[y, x] * 0.80 + np.array((150, 156, 162), np.float32) * 0.20
    # 沟沿石 + 明沟 + 墙脚
    a[CURB, :] = (134, 128, 116)
    for x in range(0, W, 21):
        a[CURB, x] = (98, 92, 82)
    a[DRAIN[0], :] = (40, 42, 44)
    a[DRAIN[0] + 1, :] = (58, 64, 68)
    a[DRAIN[1], :] = (46, 50, 54)
    return a


# ============================================================ 物件（PIL，一件一层）
class Pieces:
    def __init__(self):
        self.items = []

    def new(self, name, emissive=False):
        im = blank()
        self.items.append((name, im, emissive))
        return ImageDraw.Draw(im)

    def paste(self, name, im, xy=(0, 0), emissive=False):
        lay = blank()
        lay.alpha_composite(im, xy)
        self.items.append((name, lay, emissive))

    def bbox(self, prefix):
        bbs = [im.getchannel('A').getbbox() for n, im, e in self.items if n == prefix or n.startswith(prefix + '.')]
        bbs = [b for b in bbs if b]
        if not bbs:
            return None
        return (min(b[0] for b in bbs), min(b[1] for b in bbs), max(b[2] for b in bbs) - 1, max(b[3] for b in bbs) - 1)


# ---------------------------------------------------------------- 天 + 远处屋顶 + 巷口外的大街（自发光，不吃打光）
def sky_col(y):
    return mix((170, 178, 188), (204, 206, 204), min(1.0, max(0.0, y / 42.0)))


def draw_sky(S):
    """只在真的露天的地方画天：A 楼女儿墙上面（x 0–107，y < 15）、C 楼女儿墙上面（x 198–303，y < 9）；巷口上面的天在 draw_mouth。"""
    d = S.new('sky', emissive=True)
    for (x0, x1, y1) in ((A_X[0], A_X[1], A_ROOF - 1), (C_X[0], C_X[1], C_ROOF - 1)):
        for y in range(0, y1 + 1):
            L(d, (x0, y, x1, y), sky_col(y))
    # 远处的屋顶：雾蒙蒙的方块 + 水箱 + 天线
    haze = (176, 180, 186)
    haze2 = (164, 168, 176)
    for (x0, x1, top, c, yb) in ((0, 18, 7, haze2, A_ROOF - 1), (16, 40, 9, haze, A_ROOF - 1), (38, 62, 6, haze2, A_ROOF - 1),
                                 (60, 84, 10, haze, A_ROOF - 1), (84, 107, 7, haze2, A_ROOF - 1), (233, 258, 4, haze2, C_ROOF - 1),
                                 (256, 286, 6, haze, C_ROOF - 1), (284, 303, 3, haze2, C_ROOF - 1)):
        R(d, (x0, top, x1, yb), c)
        L(d, (x0, top, x1, top), sh(c, 1.05))
        for x in range(x0 + 2, x1 - 1, 4):
            if hash01(x, top, 31) < 0.45 and top + 3 <= yb:
                P(d, x, top + 2 + int(hash01(x, 32) * 2), sh(c, 0.93))
    # 水箱（架子上的圆柱）+ 电视天线
    R(d, (44, 1, 54, 4), (150, 154, 160))
    L(d, (44, 1, 54, 1), (168, 172, 178))
    for x in (45, 53):
        L(d, (x, 5, x, 6), (130, 134, 140))
    L(d, (92, 2, 92, 9), (120, 124, 132))
    L(d, (88, 3, 96, 3), (120, 124, 132))
    L(d, (89, 5, 95, 5), (120, 124, 132))
    R(d, (268, 0, 290, 5), (152, 154, 158))
    L(d, (268, 3, 290, 3), (138, 140, 146))
    for x in (270, 288):
        L(d, (x, 6, x, 8), (130, 132, 138))
    L(d, (296, 0, 296, 6), (120, 124, 132))
    L(d, (293, 1, 299, 1), (120, 124, 132))


def draw_mouth(S):
    """巷口（x 304–319）：对街一栋浅色楼（雾蒙蒙）、店铺、打伞的路人、黄色出租车的车尾、湿的柏油路。
    先在 16 px 宽的小图里按“街在左边”画，再左右翻过来贴到右边。"""
    w = W - MOUTH_X0
    tmp = blank(w, H)
    d = ImageDraw.Draw(tmp)
    x1 = w - 1
    for y in range(0, 44):
        L(d, (0, y, x1, y), mix((206, 208, 206), (214, 214, 208), y / 44.0))
    fac = (182, 174, 158)
    R(d, (0, 24, x1, 141), fac)                                       # 对街的楼
    L(d, (0, 24, x1, 24), (196, 190, 176))
    for (y0, y1) in ((32, 50), (62, 80)):                             # 两层拱窗（暗）+ 窗台
        for x0 in (2, 11):
            R(d, (x0, y0 + 2, x0 + 4, y1), (150, 146, 140))
            L(d, (x0 + 1, y0 + 1, x0 + 3, y0 + 1), (150, 146, 140))
            L(d, (x0, y1 + 1, x0 + 4, y1 + 1), (198, 192, 180))
            L(d, (x0, y0 + 6, x0 + 4, y0 + 6), (166, 160, 150))
    L(d, (0, 56, x1, 56), (164, 158, 146))                            # 阳台
    for x in range(0, x1 + 1, 2):
        L(d, (x, 52, x, 55), (150, 146, 140))
    for x in range(0, x1 + 1, 3):                                     # 店铺的条纹雨篷
        L(d, (x, 96, x, 101), (184, 132, 112))
    L(d, (0, 102, x1, 102), (150, 120, 104))
    R(d, (0, 103, x1, 128), (140, 136, 130))                          # 店面（暗）
    for (gx, c) in ((2, (176, 120, 96)), (6, (150, 164, 140)), (10, (190, 170, 110)), (14, (140, 150, 170))):
        R(d, (gx, 108, gx + 2, 116), c)
    R(d, (0, 117, x1, 120), (156, 150, 140))
    # 湿的柏油路 + 对面人行道（一直画到明沟那几行：巷子的沟在转角就没了）
    R(d, (0, 129, x1, CURB), (150, 150, 150))
    L(d, (0, 129, x1, 129), (176, 174, 168))
    for x in range(0, x1 + 1, 4):
        P(d, x, 134, (168, 168, 168))
        P(d, x + 2, 138, (164, 164, 166))
        P(d, x + 1, 143, (166, 166, 168))
    L(d, (0, CURB, x1, CURB), (140, 140, 140))
    # 黄色出租车（Ambassador）车尾：车身 + 尾灯 + 后窗 + 轮子
    R(d, (0, 124, 10, 137), (212, 176, 64))
    L(d, (0, 124, 9, 124), (226, 196, 96))
    R(d, (0, 118, 7, 123), (196, 164, 64))
    R(d, (1, 119, 6, 122), (150, 160, 166))
    L(d, (0, 133, 10, 133), (70, 66, 60))
    P(d, 10, 127, (200, 60, 50))
    P(d, 10, 128, (200, 60, 50))
    R(d, (2, 137, 6, 140), (54, 54, 58))
    P(d, 4, 138, (110, 110, 114))
    # 打伞的路人（黑伞 + 白衬衫 + 灰裤子）
    d.pieslice((7, 108, 15, 117), 180, 360, fill=C4((64, 64, 72)))
    L(d, (11, 108, 11, 106), (64, 64, 72))
    L(d, (11, 113, 11, 118), (90, 86, 84))
    R(d, (10, 118, 13, 128), (200, 198, 190))
    P(d, 11, 117, SKIN)
    R(d, (10, 129, 13, 138), (120, 120, 128))
    P(d, 10, 139, (60, 56, 56))
    P(d, 13, 139, (60, 56, 56))
    S.paste('mouth', tmp.transpose(Image.FLIP_LEFT_RIGHT), (MOUTH_X0, 0), emissive=True)
    # C 楼的转角（灰泥的厚度：被大街的光照亮的一道，里面暗一道；隅石）
    d = S.new('corner')
    cx = C_X[1]
    L(d, (cx, C_ROOF, cx, PLINTH[1]), (196, 184, 150))
    L(d, (cx - 1, C_ROOF, cx - 1, PLINTH[1]), (156, 144, 112))
    for y in range(C_ROOF + 4, PLINTH[0], 7):                         # 隅石
        L(d, (cx - 2, y, cx, y), (126, 114, 90))
    L(d, (cx - 1, PLINTH[0], cx, PLINTH[1]), (120, 112, 92))


# ---------------------------------------------------------------- 镜头这一侧的挑檐（自发光：本来就在暗处）
def draw_near(S):
    d = S.new('near', emissive=True)
    x0, x1 = NEAR_X
    R(d, (x0, 0, x1, 2), (38, 36, 40))
    for x in range(x0, x1 + 1):                                       # 波纹铁皮的边
        P(d, x, 3, (74, 74, 78) if x % 3 else (56, 56, 60))
        if x % 3 == 1:
            P(d, x, 4, (62, 62, 66))
    for x in (28, 96, 168, 244):                                      # 挑檐下的铁托架
        L(d, (x, 3, x, 7), (34, 32, 36))
        L(d, (x, 7, x + 5, 3), (34, 32, 36))
    L(d, (x1, 0, x1, 5), (30, 28, 32))                                # 端头
    L(d, (x0, 0, x0, 4), (30, 28, 32))
    # 吊着的一盆绿萝（x 60）
    L(d, (62, 4, 62, 7), (40, 38, 40))
    R(d, (59, 8, 65, 11), (120, 70, 50))
    L(d, (59, 8, 65, 8), (150, 92, 64))
    for (lx, ly) in ((58, 12), (59, 14), (64, 13), (66, 15), (60, 16), (65, 11)):
        P(d, lx, ly, (60, 104, 58))
        P(d, lx, ly + 1, (44, 82, 46))


# ---------------------------------------------------------------- A 楼最左边：墙上一块褪色的手绘广告 + 墙角的手压水泵
def draw_pump(S):
    d = S.new('wall_ad')
    x0, y0, x1, y1 = 1, 72, 20, 102                                     # 手绘在灰泥上的老广告（只用色块，褪得只剩一半）
    wear = A._fbm(W, H, 3, 131)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if wear[y, x] > 0.62:
                continue                                                 # 漆掉了，露出灰泥
            c = (170, 74, 62)
            if x0 + 2 <= x <= x1 - 2 and y0 + 2 <= y <= y1 - 2:
                c = (204, 196, 170)
                if y0 + 5 <= y <= y0 + 9:
                    c = (60, 92, 130)                                    # 一道蓝条
                elif y0 + 13 <= y <= y0 + 22 and x0 + 4 <= x <= x1 - 4:
                    c = (176, 140, 60) if (x + y) % 5 else (150, 110, 50)   # 中间一个黄色的块（商品）
            P(d, x, y, mix(c, (164, 150, 116), 0.35))
    d = S.new('pump')
    # 水泥台子（湿的）
    R(d, (1, 138, 18, 141), (128, 124, 116))
    L(d, (1, 138, 18, 138), (150, 146, 138))
    L(d, (1, 141, 18, 141), (92, 88, 82))
    # 铁柱（墨绿漆、上面细下面粗一点）+ 泵头 + 手柄（往左上翘）+ 出水嘴（朝右）
    iron = dict(hi=(98, 116, 106), lt=(74, 92, 84), md=(56, 72, 66), dk=(38, 48, 46))
    for y in range(117, 138):
        hw = 1 if y < 128 else 2
        for x in range(PUMP_X - hw, PUMP_X + hw + 1):
            c = iron['lt'] if x == PUMP_X - hw else iron['dk'] if x == PUMP_X + hw else iron['md']
            P(d, x, y, c)
    R(d, (PUMP_X - 3, 112, PUMP_X + 3, 117), iron['md'])                   # 泵头
    L(d, (PUMP_X - 3, 112, PUMP_X + 3, 112), iron['hi'])
    L(d, (PUMP_X - 3, 113, PUMP_X - 3, 117), iron['lt'])
    L(d, (PUMP_X + 3, 113, PUMP_X + 3, 117), iron['dk'])
    R(d, (PUMP_X - 1, 110, PUMP_X + 1, 111), iron['dk'])                   # 顶上的盖
    L(d, (PUMP_X - 3, 114, 1, 106), iron['md'])                            # 手柄
    L(d, (PUMP_X - 3, 115, 1, 107), iron['dk'])
    P(d, 1, 106, iron['hi'])
    L(d, (PUMP_X + 2, 121, PUMP_X + 6, 121), iron['md'])                   # 出水嘴
    L(d, (PUMP_X + 2, 122, PUMP_X + 6, 122), iron['dk'])
    P(d, PUMP_X + 6, 123, iron['dk'])
    R(d, (PUMP_X - 2, 136, PUMP_X + 2, 137), iron['dk'])                   # 底座
    # 出水嘴下面一只铁皮桶
    R(d, (13, 132, 18, 140), (138, 142, 144))
    L(d, (13, 132, 18, 132), (176, 180, 182))
    L(d, (13, 133, 13, 140), (160, 164, 166))
    L(d, (18, 133, 18, 140), (96, 100, 102))
    L(d, (14, 136, 17, 136), (110, 114, 116))
    d.arc((13, 128, 18, 135), 180, 360, fill=C4((90, 94, 96)))              # 提手
    P(d, 15, 133, (90, 110, 130))                                           # 桶里的水
    P(d, 16, 133, (120, 140, 156))


# ---------------------------------------------------------------- A 楼：招牌、楼上窗 + 阳台、理发店门洞 + 雨篷
def draw_building_a(S):
    # 墙上的铁皮招牌（褪色的蓝底 + 奶白边 + 剪刀 / 梳子图形 + 伪文字）
    d = S.new('barber_sign')
    x0, y0, x1, y1 = 28, 21, 68, 32
    R(d, (x0, y0, x1, y1), (78, 112, 132), (196, 188, 160))
    L(d, (x0 + 1, y0 + 1, x1 - 1, y0 + 1), (100, 136, 154))
    for (cx, cy) in ((32, 24), (32, 29)):                             # 剪刀：两个圈 + 交叉的刃
        d.ellipse((cx - 1, cy - 1, cx + 1, cy + 1), outline=C4((226, 222, 206)))
    L(d, (34, 24, 38, 28), (226, 222, 206))
    L(d, (34, 29, 38, 25), (226, 222, 206))
    R(d, (40, 24, 41, 30), (200, 70, 60))                              # 理发的红白柱
    for y in (25, 27, 29):
        P(d, 40, y, (230, 226, 214))
    A._devanagari(d, 44, 24, 4, (226, 218, 190), 301)
    L(d, (44, 30, 62, 30), (160, 160, 150))                            # 梳子（齿）
    for x in range(45, 62, 2):
        P(d, x, 31, (160, 160, 150))
    for (bx, by) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        P(d, bx, by, (90, 80, 70))
    for x in range(x0 + 3, x1 - 2, 5):                                 # 铁锈往下流
        if hash01(x, 302) < 0.6:
            L(d, (x, y1 + 1, x, y1 + 1 + int(hrange(2, 7, x, 303))), (138, 110, 82))
    # 楼上的窗（绿百叶，一扇半开）+ 铁栏小阳台 + 搭在栏杆上的纱丽
    d = S.new('a_window')
    wx0, wy0, wx1, wy1 = 80, 24, 101, 50
    R(d, (wx0 - 2, wy0 - 2, wx1 + 2, wy1), (186, 174, 140))            # 窗套
    L(d, (wx0 - 2, wy0 - 3, wx1 + 2, wy0 - 3), (120, 110, 88))
    R(d, (wx0, wy0, wx1, wy1), (42, 38, 40))
    for (sx0, sx1, open_) in ((wx0, wx0 + 10, False), (wx0 + 11, wx1, True)):
        if open_:
            R(d, (sx0, wy0, sx0 + 2, wy1), GREEN['dk'])                  # 半开的那扇只露一条边
            for y in range(wy0 + 4, wy1, 4):                          # 屋里的铁栅
                L(d, (sx0 + 3, y, sx1, y), (70, 70, 74))
            for x in range(sx0 + 5, sx1, 3):
                L(d, (x, wy0, x, wy1), (64, 64, 68))
            continue
        R(d, (sx0, wy0, sx1, wy1), GREEN['md'])
        for y in range(wy0 + 1, wy1, 2):
            L(d, (sx0 + 1, y, sx1 - 1, y), GREEN['dk'])
        L(d, (sx0, wy0, sx0, wy1), GREEN['hi'])
        L(d, (sx1, wy0, sx1, wy1), GREEN['dd'])
    d = S.new('a_balcony')
    R(d, (76, 51, 106, 53), (176, 166, 134))                             # 阳台板
    L(d, (76, 53, 106, 53), (112, 104, 84))
    for x in (79, 103):
        L(d, (x, 54, x + (2 if x < 90 else -2), 57), (130, 120, 96))      # 托架
    L(d, (77, 43, 105, 43), IRON)                                         # 栏杆
    L(d, (77, 44, 105, 44), IRON_HI)
    for x in range(77, 106, 3):
        L(d, (x, 45, x, 50), IRON)
    # 纱丽：褐红 + 金边，搭在栏杆上垂下来
    sari = [(82, 43), (97, 43), (98, 47), (96, 58), (93, 60), (90, 58), (86, 61), (83, 57)]
    d.polygon(sari, fill=C4((134, 52, 62)))
    for x in range(84, 97, 3):
        L(d, (x, 45, x - 1, 57), (110, 40, 52))
    L(d, (83, 57, 86, 61), (190, 156, 70))
    L(d, (86, 61, 90, 58), (190, 156, 70))
    L(d, (90, 58, 93, 60), (190, 156, 70))
    L(d, (93, 60, 96, 58), (190, 156, 70))
    L(d, (82, 43, 97, 43), (160, 70, 80))
    # 理发店门洞（里面：灯泡照着的后墙、理发椅、墙上小镜子、日历、搁板上的瓶子、地砖）
    d = S.new('barber_in')
    x0, y0, x1, y1 = BARBER_DOOR
    for y in range(y0 + 2, y1 + 1):
        for x in range(x0 + 2, x1 - 1):
            dd = math.hypot(x - BULB_BARBER[0], (y - BULB_BARBER[1]) * 0.8)
            u = min(1.0, dd / 40.0)
            c = mix((150, 118, 84), (54, 44, 40), u ** 0.8)
            if y >= 130:                                                # 地砖（黑白格，暗）
                c = mix((112, 100, 86), (60, 52, 46), u) if (x // 3 + y // 2) % 2 else mix((84, 74, 64), (44, 38, 34), u)
            P(d, x, y, c)
    R(d, (82, 93, 93, 104), (90, 80, 70))                                # 墙上的镜子（映着灯泡）
    R(d, (83, 94, 92, 103), (126, 132, 134))
    P(d, 88, 96, (240, 230, 200))
    P(d, 89, 96, (220, 206, 170))
    L(d, (82, 105, 93, 105), (120, 92, 60))                              # 搁板 + 瓶子
    for (bx, c) in ((83, (60, 110, 70)), (85, (170, 120, 60)), (88, (70, 90, 150)), (91, (180, 60, 60))):
        R(d, (bx, 102, bx + 1, 104), c)
    R(d, (96, 89, 101, 99), (196, 110, 54))                              # 日历（橙色，中间一个人形色块）
    R(d, (97, 90, 100, 95), (226, 170, 90))
    L(d, (98, 91, 98, 94), (120, 60, 50))
    R(d, (96, 96, 101, 99), (230, 224, 210))
    # 理发椅（红坐垫 + 镀铬脚）
    R(d, (88, 108, 98, 111), (72, 40, 38))                               # 靠背
    R(d, (87, 112, 100, 119), (128, 46, 44))
    L(d, (87, 112, 100, 112), (158, 66, 60))
    R(d, (86, 120, 101, 123), (110, 38, 38))
    L(d, (86, 120, 101, 120), (146, 60, 56))
    L(d, (84, 116, 86, 116), (150, 150, 154))                            # 扶手
    L(d, (101, 116, 103, 116), (150, 150, 154))
    L(d, (93, 124, 93, 133), (150, 150, 154))
    L(d, (94, 124, 94, 133), (100, 100, 104))
    L(d, (89, 134, 98, 134), (130, 130, 134))
    d = S.new('barber_in.bulb', emissive=True)
    L(d, (BULB_BARBER[0], y0 + 2, BULB_BARBER[0], BULB_BARBER[1] - 2), (40, 36, 34))
    R(d, (BULB_BARBER[0] - 1, BULB_BARBER[1] - 1, BULB_BARBER[0] + 1, BULB_BARBER[1] + 1), (255, 226, 160))
    P(d, BULB_BARBER[0], BULB_BARBER[1], (255, 250, 220))
    # 门框（木）+ 门槛石
    d = S.new('barber_frame')
    wood_frame(d, x0, y0, x1, y1)
    R(d, (x0 - 2, 139, x1 + 2, 141), (150, 144, 132))
    L(d, (x0 - 2, 139, x1 + 2, 139), (174, 168, 156))
    # 红白条纹的帆布雨篷（褪色、湿、下沿荷叶边）
    d = S.new('barber_awning')
    ax0, ax1 = 74, 108
    for x in range(ax0, ax1 + 1):
        stripe = ((x - ax0) // 4) % 2 == 0
        c = (164, 72, 64) if stripe else (196, 188, 168)
        for y in range(67, 73):
            u = (y - 67) / 5.0
            P(d, x, y, sh(c, 0.82 + 0.22 * u))
        scal = 73 + (1 if (x - ax0) % 4 in (1, 2) else 0)
        for y in range(73, scal + 1):
            P(d, x, y, sh(c, 0.92))
    L(d, (ax0, 66, ax1, 66), (90, 84, 74))                               # 雨篷顶的铁杆
    A._devanagari(d, 80, 69, 5, (238, 230, 210), 304)
    L(d, (ax0, 67, ax0, 75), (80, 76, 70))
    L(d, (ax1, 67, ax1, 75), (80, 76, 70))


def wood_frame(d, x0, y0, x1, y1, pal=WOOD):
    """门框：左右两根立柱（亮的在左）+ 过梁。"""
    R(d, (x0, y0, x0 + 1, y1), pal['md'])
    L(d, (x0, y0, x0, y1), pal['hi'])
    R(d, (x1 - 1, y0, x1, y1), pal['md'])
    L(d, (x1, y0, x1, y1), pal['dd'])
    L(d, (x1 - 1, y0 + 2, x1 - 1, y1), pal['dk'])
    R(d, (x0, y0, x1, y0 + 1), pal['lt'])
    L(d, (x0, y0, x1, y0), pal['hi'])
    L(d, (x0 + 2, y0 + 2, x1 - 2, y0 + 2), pal['dd'])


# ---------------------------------------------------------------- 落地镜（木框、拱形顶饰、两条腿，右腿垫砖）
def draw_mirror(S, broken):
    d = S.new('mirror.stand')
    x0, y0, x1, y1 = MIRROR_FRAME
    # 两条腿 + 横撑（右腿短一截，垫了一块砖）
    for (lx, yb) in ((27, 141), (66, 137)):
        R(d, (lx, y1 + 1, lx + 1, yb), WOOD['md'])
        L(d, (lx, y1 + 1, lx, yb), WOOD['lt'])
        L(d, (lx + 1, y1 + 1, lx + 1, yb), WOOD['dk'])
    L(d, (28, 127, 66, 127), WOOD['md'])
    L(d, (28, 128, 66, 128), WOOD['dd'])
    R(d, (63, 138, 71, 141), TERRA['md'])                                  # 砖
    L(d, (63, 138, 71, 138), TERRA['hi'])
    L(d, (71, 138, 71, 141), TERRA['dd'])
    P(d, 66, 140, TERRA['dk'])
    d = S.new('mirror')
    # 框（深色清漆木，左上亮、右下暗，里面一道铜色的线）。外沿往右歪 2 px（上面偏右、下面偏左：镜子没站正），
    # 镜面本身还是正的矩形（剧情按矩形画倒影）
    def ox(y):
        return int(round((y1 - y) / float(y1 - y0) * 2.0)) - 1      # 上沿 +1、下沿 −1
    for y in range(y0, y1 + 1):
        xa, xb = x0 + ox(y), x1 + ox(y)
        L(d, (xa, y, xb, y), WOOD['md'])
        P(d, xa, y, WOOD['lt'])
        P(d, xb, y, WOOD['dd'])
        if y0 < y < y1:
            P(d, xb - 1, y, WOOD['dk'])
    L(d, (x0 + ox(y0), y0, x1 + ox(y0), y0), WOOD['hi'])
    L(d, (x0 + ox(y0) + 1, y0 + 1, x1 + ox(y0) - 1, y0 + 1), WOOD['lt'])
    L(d, (x0 + ox(y1), y1, x1 + ox(y1), y1), WOOD['dd'])
    L(d, (x0 + ox(y1) + 1, y1 - 1, x1 + ox(y1) - 1, y1 - 1), WOOD['dk'])
    gx0, gy0, gx1, gy1 = MIRROR_GLASS
    R(d, (gx0 - 1, gy0 - 1, gx1 + 1, gy1 + 1), None, (150, 118, 66))
    L(d, (gx0 - 1, gy1 + 1, gx1 + 1, gy1 + 1), (112, 86, 50))
    for y in range(y0 + 6, y1 - 3, 8):                                     # 框上的雕花点
        P(d, x0 + 1 + ox(y), y, WOOD['hi'])
        P(d, x1 - 1 + ox(y + 4), y + 4, WOOD['dd'])
    # 拱形顶饰（左边比右边低 1 px：镜子有点歪）+ 顶上的小尖
    cx = 47.5
    for x in range(34, 62):
        u = (x - cx) / 14.0
        top = int(round(33 + 7 * u * u)) + (1 if x < 40 else 0)
        L(d, (x, top, x, y0 - 1), WOOD['md'])
        P(d, x, top, WOOD['hi'] if x < cx else WOOD['lt'])
    for x in range(38, 58):
        u = (x - cx) / 10.0
        top = int(round(37 + 4 * u * u))
        if top < y0 - 1:
            P(d, x, top, WOOD['dk'])
    d.ellipse((45, 36, 50, 40), fill=C4(WOOD['dk']))
    P(d, 46, 37, WOOD['hi'])
    L(d, (47, 29, 47, 32), WOOD['md'])
    L(d, (48, 29, 48, 32), WOOD['dk'])
    P(d, 47, 28, WOOD['hi'])
    # 右框上挂着梳子和剪刀
    L(d, (70, 58, 70, 59), (60, 56, 52))
    R(d, (72, 60, 73, 68), (38, 36, 40))
    for y in range(61, 68, 2):
        P(d, 74, y, (38, 36, 40))
    L(d, (71, 62, 71, 63), (60, 56, 52))
    d.ellipse((72, 70, 74, 72), outline=C4((170, 172, 176)))
    d.ellipse((72, 73, 74, 75), outline=C4((170, 172, 176)))
    L(d, (73, 76, 73, 81), (190, 192, 196))
    # 左上角搭一条毛巾（米白 + 两道红条，中间一道褶），只盖在框上
    tw = [(22, 41), (32, 41), (32, 45), (27, 45), (27, 62), (25, 64), (22, 61)]
    d.polygon(tw, fill=C4((196, 190, 174)))
    L(d, (22, 41, 32, 41), (218, 214, 200))
    L(d, (24, 42, 24, 62), (172, 166, 150))
    L(d, (22, 53, 27, 53), (156, 64, 60))
    L(d, (22, 55, 27, 55), (156, 64, 60))
    L(d, (22, 42, 22, 61), (160, 154, 140))
    L(d, (23, 63, 26, 63), (150, 144, 130))
    # 镜面：完好 = 整块占位色；碎了 = 后面的木背板 + 一圈锯齿碎片（占位色）
    if not broken:
        R(d, (gx0, gy0, gx1, gy1), MIRROR_KEY)
    else:
        d = S.new('mirror.back')
        for y in range(gy0, gy1 + 1):
            for x in range(gx0, gx1 + 1):
                c = (66, 50, 38) if (x * 7 + y // 9) % 11 else (52, 40, 30)
                if (x + 3) % 13 == 0:
                    c = (58, 44, 34)
                if y in (gy0, gy0 + 1) or x in (gx0, gx0 + 1):
                    c = sh(c, 0.7)                                         # 框的影子
                P(d, x, y, c)
        L(d, (gx0, 78, gx1, 78), (48, 36, 28))                             # 背板的拼缝 + 钉子
        for (nx, ny) in ((31, 49), (64, 49), (31, 106), (64, 106), (47, 77)):
            P(d, nx, ny, (110, 104, 96))
        d = S.new('mirror.shards')
        rem = shard_mask(MIRROR_GLASS, 17)[0]
        a = np.zeros((H, W, 4), np.uint8)
        a[rem] = MIRROR_KEY + (255,)
        S.items[-1][1].paste(Image.fromarray(a, 'RGBA'))


# ---------------------------------------------------------------- B 楼：木门、排水管、电表箱、海报、水缸、垃圾桶、楼上
def draw_building_b(S):
    # 楼上：落地窗 + 阳台（花盆）
    d = S.new('b_upper')
    wx0, wy0, wx1, wy1 = 126, 6, 150, 31
    R(d, (wx0 - 2, wy0 - 2, wx1 + 2, wy1), (180, 170, 136))
    R(d, (wx0, wy0, wx1, wy1), (40, 38, 42))
    for sx0 in (wx0, wx0 + 13):                                            # 两扇百叶（左关、右开一半）
        sx1 = sx0 + 11
        if sx0 > wx0:
            R(d, (sx0 + 6, wy0, sx1, wy1), TEAL['md'])
            for y in range(wy0 + 1, wy1, 2):
                L(d, (sx0 + 7, y, sx1 - 1, y), TEAL['dk'])
            L(d, (sx0 + 6, wy0, sx0 + 6, wy1), TEAL['hi'])
            L(d, (sx0 + 1, wy0 + 6, sx0 + 4, wy0 + 6), (90, 84, 80))      # 屋里挂着的衣服
            R(d, (sx0 + 1, wy0 + 7, sx0 + 4, wy0 + 15), (120, 100, 140))
            continue
        R(d, (sx0, wy0, sx1, wy1), TEAL['md'])
        for y in range(wy0 + 1, wy1, 2):
            L(d, (sx0 + 1, y, sx1 - 1, y), TEAL['dk'])
        L(d, (sx0, wy0, sx0, wy1), TEAL['hi'])
        L(d, (sx1, wy0, sx1, wy1), TEAL['dd'])
    R(d, (118, 32, 158, 34), (178, 168, 134))                              # 阳台板
    L(d, (118, 34, 158, 34), (110, 102, 82))
    L(d, (119, 24, 157, 24), IRON)
    L(d, (119, 25, 157, 25), IRON_HI)
    for x in range(119, 158, 2):
        L(d, (x, 26, x, 31), IRON if x % 4 else IRON_HI)
    for (px_, c) in ((122, (60, 110, 60)), (140, (80, 120, 56)), (154, (60, 104, 64))):   # 花盆（陶盆 + 一丛绿）
        R(d, (px_, 27, px_ + 3, 31), TERRA['md'])
        L(d, (px_, 27, px_ + 3, 27), TERRA['hi'])
        for (lx, ly) in ((0, 25), (1, 23), (2, 24), (3, 22), (-1, 24), (4, 25), (1, 21)):
            P(d, px_ + lx, ly, c)
            P(d, px_ + lx, ly + 1, sh(c, 0.75))
    # 右边一扇铁栅小窗（屋里挂一块布）
    wx0, wy0, wx1, wy1 = 166, 12, 184, 33
    R(d, (wx0 - 2, wy0 - 2, wx1 + 2, wy1 + 2), (176, 166, 132))
    R(d, (wx0, wy0, wx1, wy1), (44, 40, 44))
    R(d, (wx0 + 2, wy0 + 1, wx0 + 9, wy0 + 14), (150, 120, 70))
    L(d, (wx0 + 2, wy0 + 1, wx0 + 9, wy0 + 1), (110, 90, 60))
    for x in range(wx0 + 2, wx1, 3):
        L(d, (x, wy0, x, wy1), (78, 80, 84))
    for y in (wy0 + 7, wy0 + 15):
        L(d, (wx0, y, wx1, y), (78, 80, 84))
    L(d, (wx0 - 2, wy1 + 2, wx1 + 2, wy1 + 2), (120, 112, 90))
    # 门牌（蓝底白字的搪瓷小牌）
    d = S.new('door.plate')
    R(d, (120, 69, 127, 73), (54, 84, 140), (220, 220, 210))
    L(d, (122, 71, 125, 71), (220, 220, 210))
    # 木门：拱形铁花气窗 + 两扇（青蓝漆剥落）+ 铁钉 + 挂锁
    d = S.new('door')
    x0, y0, x1, y1 = WOOD_DOOR
    R(d, (x0, y0 + 6, x1, y1), (120, 104, 82))                              # 石门套
    d.pieslice((x0, y0, x1, y0 + 16), 180, 360, fill=C4((120, 104, 82)))
    d.pieslice((x0 + 2, y0 + 2, x1 - 2, y0 + 18), 180, 360, fill=C4((42, 38, 38)))
    L(d, (x0 + 2, y0 + 10, x1 - 2, y0 + 10), (86, 80, 72))
    cx_, cy_ = (x0 + x1) / 2.0, y0 + 10
    for k in range(7):                                                      # 放射状铁花
        ang = math.pi + k * math.pi / 6
        L(d, (cx_, cy_, cx_ + 13 * math.cos(ang), cy_ + 8 * math.sin(ang)), (86, 84, 82))
    d.arc((cx_ - 5, cy_ - 4, cx_ + 5, cy_ + 4), 180, 360, fill=C4((96, 94, 92)))
    L(d, (x0, y0 + 6, x0, y1), (146, 130, 104))
    L(d, (x1, y0 + 6, x1, y1), (86, 74, 58))
    lx0, lx1 = x0 + 3, x1 - 3
    wear_ = A._fbm(W, H, 4, 111)
    for x in range(lx0, lx1 + 1):
        for y in range(y0 + 12, y1 - 1):
            plank = (x - lx0) % 4
            c = TEAL['md'] if plank in (1, 2) else TEAL['dk'] if plank == 3 else TEAL['lt']
            wear = wear_[y, x]
            if wear > 0.58:                                                  # 漆掉了露出灰木头
                c = (124, 110, 92) if plank in (1, 2) else (98, 86, 72)
            if y > y1 - 8:
                c = sh(c, 0.85)
            P(d, x, y, c)
    L(d, ((x0 + x1) // 2, y0 + 12, (x0 + x1) // 2, y1 - 2), (36, 34, 34))    # 两扇中间的缝
    for y in (y0 + 20, y0 + 44):                                             # 横档
        L(d, (lx0, y, lx1, y), TEAL['hi'])
        L(d, (lx0, y + 1, lx1, y + 1), TEAL['dd'])
    for y in range(y0 + 15, y1 - 3, 8):                                      # 铁钉
        for x in range(lx0 + 2, lx1, 5):
            P(d, x, y, (40, 40, 42))
            P(d, x - 1, y - 1, (120, 120, 120))
    R(d, (129, 108, 133, 110), (70, 70, 72))                                 # 搭扣 + 挂锁
    R(d, (130, 111, 133, 115), (166, 136, 62))
    L(d, (130, 111, 133, 111), (206, 176, 96))
    P(d, 131, 113, (60, 50, 30))
    d.arc((129, 106, 134, 112), 180, 360, fill=C4((150, 150, 150)))
    R(d, (x0 - 2, 139, x1 + 2, 141), (150, 144, 132))                        # 门槛石
    L(d, (x0 - 2, 139, x1 + 2, 139), (176, 170, 158))
    # 排水管（铸铁，锈点，卡箍）+ 出水口弯向明沟
    d = S.new('pipe')
    p0, p1 = PIPE_X
    R(d, (p0, 4, p1, 133), (66, 64, 62))
    L(d, (p0, 4, p0, 133), (50, 48, 48))
    L(d, (p0 + 1, 4, p0 + 1, 133), (104, 102, 98))
    L(d, (p1, 4, p1, 133), (44, 42, 42))
    for y in range(10, 130, 23):
        R(d, (p0 - 1, y, p1 + 1, y + 1), (80, 78, 76))
        L(d, (p0 - 1, y, p1 + 1, y), (120, 118, 114))
        P(d, p0 - 2, y, (60, 58, 56))
        P(d, p1 + 2, y, (60, 58, 56))
    for (ry, rh) in ((40, 6), (72, 10), (98, 5), (118, 8)):                  # 锈
        for y in range(ry, ry + rh):
            P(d, p0 + 2 + (y % 2), y, (120, 74, 48))
    d.polygon([(p0, 132), (p1, 132), (p1 + 4, 136), (p1 + 4, 139), (p1 + 1, 139), (p0, 136)], fill=C4((66, 64, 62)))
    L(d, (p1, 132, p1 + 4, 136), (104, 102, 98))
    L(d, (p1 + 2, 139, p1 + 4, 139), (30, 30, 32))
    P(d, p1 + 3, 138, (30, 30, 32))
    # 电表箱（两只灰铁盒、表盘）+ 一大把乱电线从上面进来
    d = S.new('meters')
    for (bx0, by0, bx1, by1) in ((160, 66, 167, 78), (169, 68, 177, 81)):
        R(d, (bx0, by0, bx1, by1), (128, 130, 126), (70, 72, 70))
        L(d, (bx0 + 1, by0 + 1, bx1 - 1, by0 + 1), (160, 162, 156))
        d.ellipse((bx0 + 2, by0 + 3, bx0 + 5, by0 + 6), fill=C4((214, 212, 200)), outline=C4((60, 60, 60)))
        P(d, bx0 + 3, by0 + 4, (40, 40, 40))
        L(d, (bx0 + 2, by1 - 2, bx1 - 2, by1 - 2), (96, 98, 94))
        L(d, (bx1 - 1, by0 + 2, bx1 - 1, by1 - 2), (110, 84, 60))
    # 褪色的旧海报（只用色块，撕掉一半）
    d = S.new('posters')
    poster(d, (162, 88, 178, 110), (164, 104, 120), seed=1, deco='face')
    poster(d, (176, 92, 195, 114), (188, 170, 104), seed=2, deco='bands')
    poster(d, (165, 112, 184, 122), (186, 182, 168), seed=3, deco='block')
    # 大陶水缸（铝盖 + 钢杯）
    d = S.new('urn')
    for y in range(122, 142):
        u = (y - 122) / 19.0
        hw = 5 + 3.6 * math.sin(math.pi * min(1.0, u * 1.25))
        cx = 185
        xa, xb = int(round(cx - hw)), int(round(cx + hw))
        for x in range(xa, xb + 1):
            v = (x - xa) / max(1, xb - xa)
            c = TERRA['hi'] if 0.15 < v < 0.32 else TERRA['lt'] if v < 0.5 else TERRA['md'] if v < 0.8 else TERRA['dk']
            if x in (xa, xb):
                c = TERRA['dd']
            if y > 138:
                c = sh(c, 0.82)
            P(d, x, y, c)
    L(d, (180, 121, 190, 121), TERRA['hi'])
    L(d, (179, 120, 191, 120), (158, 160, 164))                              # 铝盖
    L(d, (180, 119, 190, 119), (186, 188, 192))
    R(d, (186, 116, 188, 118), (176, 180, 186))                              # 钢杯
    P(d, 188, 117, (120, 124, 130))
    L(d, (181, 128, 189, 128), (182, 112, 76))                               # 一道白灰画的线（记号）
    # 垃圾桶（凹了的铁皮桶 + 冒出来的垃圾）
    d = S.new('bin')
    R(d, (104, 125, 116, 141), (112, 114, 112))
    L(d, (104, 125, 104, 141), (86, 88, 86))
    L(d, (105, 125, 105, 141), (140, 142, 138))
    L(d, (116, 125, 116, 141), (74, 76, 74))
    for y in (129, 136):
        L(d, (104, y, 116, y), (90, 92, 90))
        L(d, (104, y + 1, 116, y + 1), (132, 134, 130))
    L(d, (110, 131, 112, 134), (86, 88, 86))                                  # 凹痕
    for (rx, ry) in ((107, 132), (114, 138), (108, 139)):
        P(d, rx, ry, (128, 86, 56))
    L(d, (103, 124, 117, 124), (128, 130, 126))
    for (gx, gy, c) in ((105, 122, (196, 190, 172)), (107, 121, (60, 106, 54)), (109, 120, (70, 116, 60)), (111, 122, (176, 150, 110)),
                        (113, 121, (196, 190, 172)), (115, 123, (150, 70, 60)), (106, 123, (80, 70, 60)), (112, 123, (60, 106, 54))):
        R(d, (gx, gy, gx + 1, 123), c)
    L(d, (108, 119, 112, 121), (70, 116, 60))                                 # 香蕉叶
    for (gx, gy) in ((100, 140), (102, 141), (118, 140)):                     # 掉在地上的纸团
        P(d, gx, gy, (176, 170, 154))


def poster(d, box, col, seed, deco):
    x0, y0, x1, y1 = box
    pts = []
    for x in range(x0, x1 + 1):                                               # 撕过的下沿 / 右沿用锯齿
        pts.append((x, y1 - int(hrange(0, 3, seed, x, 1)) * (1 if (x - x0) > (x1 - x0) * 0.4 else 0)))
    poly = [(x0, y0)] + [(x1 - int(hrange(0, 2, seed, 2)), y0)] + pts[::-1]
    poly = [(x0, y0), (x1, y0)] + [(x1 - int(hrange(0, 3, seed, y, 3)), y) for y in range(y0, y1 + 1, 2)] + pts[::-1]
    d.polygon(poly, fill=C4(col))
    if deco == 'face':
        d.ellipse((x0 + 3, y0 + 3, x0 + 11, y0 + 13), fill=C4(mix(col, (214, 184, 160), 0.6)))
        R(d, (x0 + 1, y1 - 7, x1 - 2, y1 - 4), mix(col, (80, 50, 60), 0.6))
        R(d, (x0 + 10, y0 + 2, x1 - 1, y0 + 5), mix(col, (230, 220, 200), 0.5))
    elif deco == 'bands':
        R(d, (x0 + 1, y0 + 4, x1 - 2, y0 + 7), mix(col, (176, 70, 56), 0.7))
        R(d, (x0 + 3, y0 + 10, x0 + 9, y0 + 17), mix(col, (90, 116, 150), 0.7))
        R(d, (x0 + 11, y0 + 12, x1 - 3, y0 + 14), mix(col, (60, 50, 50), 0.5))
        d.polygon([(x0, y0), (x0 + 6, y0), (x0, y0 + 5)], fill=C4((206, 200, 184)))   # 左上角撕掉露出底下的白纸
    else:
        R(d, (x0 + 2, y0 + 2, x0 + 8, y1 - 2), mix(col, (100, 150, 160), 0.6))
        L(d, (x0 + 10, y0 + 3, x1 - 3, y0 + 3), mix(col, (60, 50, 50), 0.5))
    L(d, (x0, y0, x1, y0), mix(col, (60, 50, 40), 0.25))


# ---------------------------------------------------------------- C 楼：楼上、招牌、铁皮雨篷、橱窗、护板、麻袋 / 木箱、店门
def draw_building_c(S, broken):
    d = S.new('c_upper')
    for (wx0, open_) in ((214, False), (264, True)):                          # 两扇拱顶百叶窗
        wx1, wy0, wy1 = wx0 + 17, 18, 37
        R(d, (wx0 - 2, wy0 - 1, wx1 + 2, wy1 + 1), (184, 172, 140))
        d.pieslice((wx0 - 2, wy0 - 6, wx1 + 2, wy0 + 4), 180, 360, fill=C4((184, 172, 140)))
        d.pieslice((wx0, wy0 - 4, wx1, wy0 + 4), 180, 360, fill=C4((42, 38, 40)))
        R(d, (wx0, wy0, wx1, wy1), (42, 38, 40))
        if open_:
            R(d, (wx0, wy0, wx0 + 2, wy1), GREEN['md'])
            R(d, (wx1 - 2, wy0, wx1, wy1), GREEN['dk'])
            for y in range(wy0 + 2, wy1, 3):
                L(d, (wx0 + 3, y, wx1 - 3, y), (70, 70, 74))
            R(d, (wx0 + 5, wy0 + 4, wx0 + 12, wy0 + 12), (64, 58, 60))       # 屋里的一面镜子 / 柜子
        else:
            for sx0 in (wx0, wx0 + 9):
                R(d, (sx0, wy0 - 3, sx0 + 8, wy1), GREEN['md'])
                for y in range(wy0 - 2, wy1, 2):
                    L(d, (sx0 + 1, y, sx0 + 7, y), GREEN['dk'])
                L(d, (sx0, wy0 - 3, sx0, wy1), GREEN['hi'])
                L(d, (sx0 + 8, wy0 - 3, sx0 + 8, wy1), GREEN['dd'])
        L(d, (wx0 - 3, wy1 + 2, wx1 + 3, wy1 + 2), (196, 186, 154))          # 窗台
        L(d, (wx0 - 3, wy1 + 3, wx1 + 3, wy1 + 3), (112, 102, 82))
    R(d, (219, 34, 224, 38), TERRA['md'])                                     # 窗台上的花盆
    for (lx, ly) in ((219, 32), (220, 30), (222, 31), (223, 29), (224, 32), (221, 28)):
        P(d, lx, ly, (70, 116, 60))
    # 招牌（黄底、深红边、伪天城文 + 瓶子 / 罐子图形）
    d = S.new('store_sign')
    x0, y0, x1, y1 = 206, 41, 290, 53
    R(d, (x0, y0, x1, y1), (188, 160, 78), (116, 44, 40))
    L(d, (x0 + 1, y0 + 1, x1 - 1, y0 + 1), (210, 186, 104))
    R(d, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), None, (204, 178, 98))
    A._devanagari(d, 224, 45, 10, (122, 40, 40), 311)
    R(d, (211, 45, 213, 51), (54, 104, 66))                                    # 瓶子
    L(d, (212, 43, 212, 44), (54, 104, 66))
    P(d, 211, 46, (110, 170, 120))
    R(d, (281, 46, 286, 51), (222, 214, 190))                                  # 罐子
    R(d, (281, 44, 286, 45), (176, 50, 46))
    P(d, 282, 47, (190, 120, 60))
    for (bx, by) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        P(d, bx, by, (90, 70, 50))
    for x in (216, 238, 262, 284):                                             # 锈斑
        P(d, x, y1 - 1, (130, 90, 56))
        P(d, x + 1, y1 - 2, (150, 104, 64))
    # 瓦楞铁皮雨篷（从墙上斜出来，前沿 y 60）
    d = S.new('store_awning')
    ax0, ax1 = 202, 293
    rust_ = A._fbm(W, H, 3, 121)[57]
    for x in range(ax0, ax1 + 1):
        ridge = (x - ax0) % 4
        c = (138, 136, 132) if ridge == 0 else (118, 116, 112) if ridge == 1 else (98, 96, 94) if ridge == 2 else (110, 108, 104)
        rust = rust_[x] > 0.6
        for y in range(54, 60):
            cc = c
            if rust and y > 55:
                cc = mix(c, (130, 84, 56), 0.6)
            P(d, x, y, sh(cc, 0.86 + 0.04 * (y - 54)))
        P(d, x, 60, (64, 62, 60) if ridge else (90, 88, 86))
    L(d, (ax0, 53, ax1, 53), (90, 86, 80))
    # 橱窗木框（褪色的绿漆）
    d = S.new('store_window')
    x0, y0, x1, y1 = WINDOW_FRAME
    gx0, gy0, gx1, gy1 = WINDOW_GLASS
    R(d, (x0, y0, x1, y1), GREEN['md'])
    L(d, (x0, y0, x1, y0), GREEN['hi'])
    L(d, (x0, y0, x0, y1), GREEN['lt'])
    L(d, (x1, y0, x1, y1), GREEN['dd'])
    L(d, (gx0 - 1, gy0 - 1, gx1 + 1, gy0 - 1), GREEN['dd'])                    # 里口：上 / 左暗、下 / 右亮
    L(d, (gx0 - 1, gy0 - 1, gx0 - 1, gy1 + 1), GREEN['dk'])
    L(d, (gx0 - 1, gy1 + 1, gx1 + 1, gy1 + 1), GREEN['hi'])
    L(d, (gx1 + 1, gy0 - 1, gx1 + 1, gy1 + 1), GREEN['lt'])
    R(d, (x0 - 1, y1 - 2, x1 + 1, y1), GREEN['lt'])                            # 窗台（凸出来一点）
    L(d, (x0 - 1, y1 - 2, x1 + 1, y1 - 2), GREEN['hi'])
    L(d, (x0 - 1, y1, x1 + 1, y1), GREEN['dd'])
    wear = A._fbm(W, H, 3, 123)
    for y in range(y0, y1 + 1):                                                # 漆掉的地方露出木头
        for x in range(x0, x1 + 1):
            if (gx0 - 1 <= x <= gx1 + 1 and gy0 - 1 <= y <= gy1 + 1):
                continue
            if wear[y, x] > 0.64:
                P(d, x, y, (124, 104, 80) if wear[y, x] < 0.7 else (100, 84, 64))
    if not broken:
        R(d, (gx0, gy0, gx1, gy1), WINDOW_KEY)
    else:
        rem = shard_mask(WINDOW_GLASS, 23)[0]
        box = np.zeros((H, W), bool)
        box[gy0:gy1 + 1, gx0:gx1 + 1] = True
        a = np.zeros((H, W, 4), np.uint8)
        a[box] = HOLE_KEY + (255,)
        a[rem] = WINDOW_KEY + (255,)
        S.paste('store_window.glass', Image.fromarray(a, 'RGBA'))
    # 护板（竖木板，绿漆，下面烂了一截）
    d = S.new('kick')
    for x in range(x0, x1 + 1):
        plank = (x - x0) % 6
        c = GREEN['md'] if plank in (1, 2, 3) else GREEN['lt'] if plank == 4 else GREEN['dk'] if plank == 5 else GREEN['dd']
        for y in range(118, 142):
            cc = c
            if wear[y, x] > 0.62:
                cc = (110, 96, 76)
            if y >= 136:
                cc = mix(cc, (54, 58, 50), (y - 135) / 7.0)
            P(d, x, y, cc)
    L(d, (x0, 118, x1, 118), GREEN['dd'])
    # 麻袋两只
    d = S.new('sacks')
    for (sx0, sx1, top, tie) in ((204, 214, 128, 209), (212, 223, 131, 218)):
        for y in range(top, 142):
            u = (y - top) / max(1, 141 - top)
            bulge = int(round(1.6 * math.sin(math.pi * min(1.0, u * 1.3))))
            for x in range(sx0 - bulge, sx1 + bulge + 1):
                c = (172, 150, 108) if (x + y) % 3 else (150, 128, 90)
                if x >= sx1 + bulge - 1:
                    c = (124, 106, 74)
                if y > 139:
                    c = sh(c, 0.8)
                P(d, x, y, c)
        L(d, (tie - 1, top - 2, tie + 1, top - 2), (150, 128, 90))
        L(d, (tie, top - 1, tie, top), (110, 92, 64))
    R(d, (206, 133, 210, 136), (160, 70, 60))                                   # 红色的印记（色块）
    # 木箱（装瓶子）+ 煤油桶
    d = S.new('crates')
    crate(d, 262, 128, 277, 141)
    crate(d, 275, 121, 291, 141)
    for (bx, c) in ((278, (60, 110, 70)), (281, (120, 74, 40)), (284, (60, 110, 70)), (287, (120, 74, 40)), (264, (60, 110, 70)),
                    (267, (140, 90, 50)), (270, (60, 110, 70)), (273, (140, 90, 50))):
        top = 117 if bx > 276 else 124
        R(d, (bx, top, bx + 1, top + 3), c)
        P(d, bx, top - 1, sh(c, 1.25))
    R(d, (255, 132, 261, 141), (150, 154, 156))                                 # 煤油桶
    L(d, (255, 132, 261, 132), (190, 194, 196))
    L(d, (256, 133, 256, 141), (186, 190, 192))
    L(d, (261, 133, 261, 141), (100, 104, 106))
    R(d, (257, 130, 258, 131), (90, 92, 96))
    L(d, (255, 137, 261, 137), (170, 70, 56))
    # 橱窗框顶上挂一串万寿菊花环（只挂在框上，不垂到玻璃上）
    d = S.new('garland')
    gx0_, gx1_ = WINDOW_FRAME[0] + 1, WINDOW_FRAME[2] - 1
    for x in range(gx0_, gx1_ + 1):
        k = (x - gx0_) % 22
        sag = int(round(1.4 * math.sin(math.pi * k / 22)))
        P(d, x, 61 + sag, (226, 136, 40) if x % 2 else (244, 178, 60))
        if sag == 0 and k == 0:
            P(d, x, 60, (90, 80, 60))                                            # 钉子
        if x % 4 == 0:
            P(d, x, 62 + sag, (64, 112, 52))                                     # 芒果叶
    # 街角：路名牌（蓝底白字的搪瓷牌，只画色块）+ 铁灯架（白天关着）+ 墙根一只塑料桶和一把扫帚
    d = S.new('corner_bits')
    R(d, (292, 70, 300, 75), (52, 84, 138), (214, 214, 204))
    L(d, (294, 72, 298, 72), (214, 214, 204))
    L(d, (294, 73, 297, 73), (170, 176, 190))
    L(d, (298, 46, 302, 46), IRON)                                               # 灯架
    L(d, (298, 47, 298, 50), IRON)
    L(d, (297, 47, 297, 47), IRON)
    R(d, (295, 50, 299, 52), (60, 64, 66))                                       # 灯罩
    L(d, (295, 50, 299, 50), (100, 104, 106))
    P(d, 297, 53, (190, 186, 170))                                              # 灯泡（关着）
    R(d, (293, 133, 299, 141), (66, 104, 150))                                  # 塑料桶（蓝）
    L(d, (293, 133, 299, 133), (100, 140, 180))
    L(d, (293, 134, 293, 141), (88, 126, 168))
    L(d, (299, 134, 299, 141), (46, 76, 110))
    L(d, (294, 137, 298, 137), (54, 88, 128))
    L(d, (301, 106, 298, 132), (120, 96, 60))                                   # 扫帚（竹柄 + 一把细枝）
    for k in range(5):
        L(d, (298, 132, 295 + k * 1.5, 141), (150, 128, 80) if k % 2 else (122, 102, 64))


def crate(d, x0, y0, x1, y1):
    R(d, (x0, y0, x1, y1), (78, 56, 38))
    for y in range(y0 + 1, y1, 3):
        L(d, (x0 + 1, y, x1 - 1, y), (134, 100, 66))
        L(d, (x0 + 1, y + 1, x1 - 1, y + 1), (112, 82, 54))
    L(d, (x0, y0, x0, y1), (150, 114, 76))
    L(d, (x1, y0, x1, y1), (70, 50, 34))
    L(d, (x0, y0, x1, y0), (156, 120, 80))


# ---------------------------------------------------------------- 墙根：门口盖着明沟的石板
def draw_slabs(S):
    d = S.new('slabs')
    for (x0, x1) in ((76, 105), (114, 148)):
        R(d, (x0, DRAIN[0], x1, CURB), (118, 112, 102))
        L(d, (x0, DRAIN[0], x1, DRAIN[0]), (146, 140, 128))
        L(d, (x0, CURB, x1, CURB), (90, 84, 76))
        P(d, x0, DRAIN[0] + 1, (80, 76, 70))
        P(d, x1, DRAIN[0] + 1, (80, 76, 70))


# ---------------------------------------------------------------- 晾衣绳 + 衣服、电线
def sag_line(p0, p1, sag, n=None):
    (x0, y0), (x1, y1) = p0, p1
    n = n or int(max(abs(x1 - x0), abs(y1 - y0)) * 1.5) + 2
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n + sag * 4 * (i / n) * (1 - i / n)) for i in range(n + 1)]


def line_y(pts, x):
    best = min(pts, key=lambda p: abs(p[0] - x))
    return best[1]


CLOTHES_LINES = [((40, 3), (106, 30), 4), ((114, 3), (196, 46), 5), ((226, 3), (306, 28), 4), ((150, 4), (200, 6), 9)]


def draw_lines(S):
    d = S.new('wires')
    # 天上的电线（下垂；从挑檐拉到对面楼顶，横七竖八）
    for (p0, p1, sag, c) in (((0, 10), (122, 4), 12, (46, 44, 48)), ((0, 20), (104, 15), 8, (56, 54, 58)),
                             ((150, 4), (320, 12), 10, (46, 44, 48)), ((226, 4), (320, 26), 5, (56, 54, 58)),
                             ((70, 4), (164, 54), 5, (52, 50, 54))):
        pts = sag_line(p0, p1, sag)
        for (x, y) in pts:
            P(d, x, y, c)
    # 墙上横拉的一把电线（两根，各自在托架之间下垂）+ 往电表箱去的引线
    brackets = [18, 44, 76, 108, 140, 158, 182, 197]
    for k, (dy, sag, c) in enumerate(((0, 2.0, (44, 42, 46)), (2, 3.0, (70, 66, 68)))):
        for i in range(len(brackets) - 1):
            xa, xb = brackets[i], brackets[i + 1]
            ya = yb = 66 + dy if xa < 108 else 62 + dy
            if xb == 108:
                yb = 62 + dy
            for (x, y) in sag_line((xa, ya), (xb, yb), sag + 0.3 * (i % 2)):
                P(d, x, y, c)
    for (x, y0, y1) in ((162, 64, 66), (172, 64, 68)):
        L(d, (x, y0, x, y1), (44, 42, 46))
    for x in brackets:                                                          # 瓷绝缘子
        P(d, x, 65 if x < 108 else 61, (210, 206, 196))
    # B|C 交界处往上拐到 C 楼招牌上面，再横着拉到右边出图
    for (p0, p1, sag, c) in (((197, 62), (204, 40), 0, (44, 42, 46)), ((197, 64), (205, 41), 0, (70, 66, 68)),
                             ((204, 40), (262, 39), 2.0, (44, 42, 46)), ((262, 39), (320, 40), 2.4, (44, 42, 46)),
                             ((205, 41), (320, 42), 3.0, (70, 66, 68))):
        for (x, y) in sag_line(p0, p1, sag):
            P(d, x, y, c)
    # 一团乱线（排水管旁边）
    for i in range(5):
        cx, cy = 159 + hrange(-3, 3, i, 401), 57 + hrange(-2, 2, i, 402)
        r = hrange(2, 4, i, 403)
        d.arc((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), int(hrange(0, 180, i, 404)), int(hrange(200, 360, i, 405)),
              fill=C4((36, 34, 38)))
    # 晾衣绳 + 衣服
    d = S.new('laundry')
    for li, (p0, p1, sag) in enumerate(CLOTHES_LINES):
        pts = sag_line(p0, p1, sag)
        for (x, y) in pts:
            P(d, x, y, (196, 192, 180) if li != 3 else (170, 168, 160))
        P(d, p1[0], p1[1], (90, 88, 84))                                         # 墙上的钉子
    garments = [  # (绳, x, 宽, 长, 颜色, 款式)
        (0, 56, 8, 11, (70, 98, 146), 'shirt'), (0, 68, 6, 9, (214, 208, 192), 'towel'), (0, 80, 7, 10, (196, 120, 140), 'dress'),
        (0, 93, 5, 7, (150, 150, 158), 'towel'),
        (1, 128, 6, 22, (206, 132, 50), 'sari'), (1, 138, 7, 12, (70, 120, 90), 'lungi'), (1, 168, 6, 8, (210, 206, 196), 'shirt'),
        (1, 180, 4, 6, (60, 60, 90), 'towel'),
        (2, 240, 7, 12, (196, 176, 90), 'kurta'), (2, 254, 5, 7, (160, 60, 60), 'towel'), (2, 268, 6, 10, (120, 140, 170), 'shirt'),
        (2, 286, 4, 5, (210, 206, 196), 'towel'),
        (3, 172, 5, 6, (176, 70, 80), 'towel'), (3, 184, 6, 7, (90, 110, 150), 'towel'),
    ]
    for (li, gx, gw, gl, col, kind) in garments:
        p0, p1, sag = CLOTHES_LINES[li]
        pts = sag_line(p0, p1, sag)
        garment(d, gx, gw, gl, col, kind, lambda x, pts=pts: line_y(pts, x))


def garment(d, x0, w, ln, col, kind, ly):
    """挂在绳上的一件衣服：上沿跟着绳子，顶上亮、往下暗，竖褶。"""
    for i in range(w):
        x = x0 + i
        top = int(round(ly(x))) + 1
        bot = top + ln
        if kind == 'shirt':
            bot = top + ln - (2 if i in (0, w - 1) else 0)
        elif kind == 'dress':
            bot = top + ln + (1 if i in (0, w - 1) else 0)
        elif kind == 'sari':
            bot = top + ln - int(abs(i - w / 2) * 2)
        elif kind == 'lungi':
            bot = top + ln - (i % 2)
        for y in range(top, bot + 1):
            u = (y - top) / max(1, ln)
            c = col
            if kind == 'lungi' and ((x // 2 + y // 2) % 2 == 0):
                c = sh(col, 0.78)
            if kind == 'kurta' and y - top in (2, 3) and 2 <= i <= w - 3:
                c = sh(col, 0.85)
            k = 1.08 - 0.22 * u
            if i == 0:
                k *= 1.06
            if i == w - 1:
                k *= 0.82
            if (i + 1) % 3 == 0:
                k *= 0.9
            P(d, x, y, sh(c, k))
        P(d, x, top - 1, (220, 216, 206) if i in (1, w - 2) else sh(col, 1.1))      # 夹子 / 搭在绳上的折边


# ============================================================ 碎玻璃的形状（照 cable_car._ew_broken）
def _zigzag(seed, k, length, deep):
    pts = [(0.0, hrange(1, 4, seed, k, 99))]
    t = 0.0
    i = 0
    while True:
        t += hrange(2.5, 6.0, seed, k, i, 5)
        if t >= length:
            break
        tip = hrange(3, 9, seed, k, i, 2) * deep
        if hash01(seed, k, i, 3) < 0.22:
            tip += hrange(6, 14, seed, k, i, 4) * deep
        pts.append((t, tip))
        t += hrange(2.5, 6.0, seed, k, i, 6)
        if t >= length:
            break
        pts.append((t, hrange(0, 2.2, seed, k, i, 1)))
        i += 1
    pts.append((float(length), hrange(1, 4, seed, k, 98)))
    return pts


@lru_cache(maxsize=4)
def shard_mask(glass, seed):
    """框里剩下的锯齿碎片：返回 (rem 碎片, edge 断口亮线, rim 断口里面一道, crack 裂纹)，都是 H×W bool。"""
    x0, y0, x1, y1 = glass
    gw, gh = x1 - x0, y1 - y0
    fill, edge, rim, crk = (Image.new('L', (W, H), 0) for _ in range(4))
    df, de, dr, dc = (ImageDraw.Draw(m) for m in (fill, edge, rim, crk))
    sides = [(1, gw, lambda t, dd: (x0 + t, y0 + dd), (0, -1), 1.1), (2, gw, lambda t, dd: (x0 + t, y1 - dd), (0, 1), 0.7),
             (3, gh, lambda t, dd: (x0 + dd, y0 + t), (-1, 0), 0.8), (4, gh, lambda t, dd: (x1 - dd, y0 + t), (1, 0), 0.8)]
    for (k, Ln, Pf, (ox, oy), deep) in sides:
        zz = _zigzag(seed, k, Ln, deep)
        line = [Pf(t, dd) for (t, dd) in zz]
        df.polygon([Pf(0, 0)] + line + [Pf(Ln, 0)], fill=255)
        de.line(line, fill=255)
        dr.line([(x + ox, y + oy) for (x, y) in line], fill=255)
        for j, (t, dd) in enumerate(zz):
            if dd > 8:
                tx, ty = Pf(t, dd)
                bx, by = Pf(t + hrange(-5, 5, seed, k, j, 7), 0)
                dc.line((tx, ty, bx, by), fill=255)
    for i, (cx, cy, sx, sy) in enumerate([(x0, y0, 1, 1), (x1, y1, -1, -1)]):         # 两个角上大一点的三角碎片
        Lx, Ly = hrange(9, 15, seed, i, 21), hrange(14, 22, seed, i, 22)
        tri = [(cx, cy), (cx + sx * Lx, cy), (cx, cy + sy * Ly)]
        df.polygon(tri, fill=255)
        de.line([tri[1], tri[2]], fill=255)
        dc.line((cx + sx * 2, cy + sy * 2, cx + sx * Lx * 0.45, cy + sy * Ly * 0.55), fill=255)
    box = np.zeros((H, W), bool)
    box[y0:y1 + 1, x0:x1 + 1] = True
    rem = (np.array(fill) > 0) & box
    e = (np.array(edge) > 0) & rem
    r = (np.array(rim) > 0) & rem & ~e
    c = (np.array(crk) > 0) & rem & ~e
    return rem, e, r, c


# ============================================================ 拼 albedo
@lru_cache(maxsize=4)
def build(mb, wb):
    """返回 (albedo float H×W×3, emissive bool H×W, Pieces)。"""
    a = wall_albedo().copy()
    fl = floor_albedo()
    a[DRAIN[0]:] = fl[DRAIN[0]:]
    S = Pieces()
    draw_sky(S)
    draw_mouth(S)
    draw_pump(S)
    draw_building_a(S)
    draw_building_b(S)
    draw_building_c(S, wb)
    draw_slabs(S)
    draw_lines(S)
    draw_mirror(S, mb)
    draw_near(S)
    # 接触阴影（墙脚的东西下面）
    for (xa, xb, ya, yb, k) in ((26, 72, 140, 141, 0.7), (103, 118, 140, 141, 0.7), (177, 194, 140, 141, 0.7),
                                (203, 225, 140, 141, 0.72), (254, 300, 140, 141, 0.72), (1, 19, 140, 141, 0.75)):
        a[ya:yb + 1, xa:xb] *= k
    emis = np.zeros((H, W), bool)
    cover = np.zeros((H, W), bool)
    img = rgba(a)
    for name, im, e in S.items:
        al = np.array(im)[..., 3]
        img.alpha_composite(im)
        emis = np.where(al >= 128, e, emis)
        cover |= al >= 128
    S.cover = cover
    out = np.array(img).astype(np.float32)[..., :3]
    return out, emis, S


# ============================================================ 打光（阴天：上亮下暗、巷口那边亮、门洞里的灯是暖的）
def quant(Lv, n, bay):
    return np.floor(Lv * n + 0.5 + (bay - 0.5) * 0.35) / n


AO_BOXES = [  # (x0, x1, y0, y1, 最暗的系数)：从 y0 往下渐亮
    (76, 106, 54, 62, 0.80), (74, 108, 75, 84, 0.78), (118, 158, 35, 44, 0.80), (202, 293, 61, 66, 0.78),
    (0, 107, A_BAND[1] + 1, A_BAND[1] + 4, 0.90), (20, 76, 114, 141, 0.86), (206, 290, 42, 44, 0.9),
]


@lru_cache(maxsize=1)
def light_field():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bay = A._bayer(W, H)
    wall = 0.98 - 0.22 * np.clip((yy - 14) / 128.0, 0, 1)
    wall += 0.10 * np.clip(1 - (C_X[1] - xx) / 80.0, 0, 1)                     # 巷口（右边）那边亮一点
    wall -= 0.06 * np.clip((110 - xx) / 110.0, 0, 1)                           # 巷子深处（左边）暗一点
    wall -= 0.08 * np.clip((yy - PLINTH[0]) / 12.0, 0, 1)                      # 墙脚
    gnd = 0.86 + 0.08 * np.clip((yy - FLOOR0) / 34.0, 0, 1) + 0.07 * np.clip(1 - (W - 1 - xx) / 70.0, 0, 1)
    gnd -= 0.10 * np.clip(1 - (yy - DRAIN[0]) / 6.0, 0, 1)                     # 贴着墙脚的地面暗
    Lv = np.where(yy >= DRAIN[0], gnd, wall)
    for (x0, x1, y0, y1, k) in AO_BOXES:
        u = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)
        f = k + (1 - k) * u
        m = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
        Lv = np.where(m, Lv * f, Lv)
    q = quant(Lv, 24, bay)
    # 冷的天光 + 理发店门洞里那盏灯的暖光（照到门框、门口的地面）
    cool = np.array((0.96, 0.99, 1.05), np.float32)
    warmT = np.array((1.25, 1.02, 0.72), np.float32)
    w = np.zeros((H, W), np.float32)
    for (bx, by, r, k) in ((BULB_BARBER[0], BULB_BARBER[1] + 26, 30.0, 0.30),):
        dd = np.hypot(xx - bx, (yy - by) * 0.75)
        w += k * np.clip(1 - dd / r, 0, 1) ** 1.6
    w = np.floor(w * 12 + 0.5 + (bay - 0.5) * 0.4) / 12
    m = q[..., None] * cool + w[..., None] * warmT * 0.55
    return m


@lru_cache(maxsize=4)
def lit(mb, wb):
    alb, emis, S = build(mb, wb)
    m = light_field()
    out = np.where(emis[..., None], alb, np.clip(alb * m, 0, 255))
    out = np.maximum(out, 6)
    key = np.zeros((H, W), np.uint8)                                            # 玻璃占位色在打光以前就记下来
    for i, kc in enumerate((MIRROR_KEY, WINDOW_KEY, HOLE_KEY)):
        key[(alb == np.array(kc, np.float32)).all(-1)] = i + 1
    im = rgba(out)
    A._glow(im, BULB_BARBER[0], BULB_BARBER[1], 9, 8, (255, 210, 140), 60, rings=3)
    wet_glints(im)
    a = np.array(im)
    a[emis] = np.array(rgba(alb))[emis]
    return a, key


def wet_glints(im):
    """湿地面上：理发店门洞的暖光、巷口的天光在地上拉出来的竖条倒影（很淡）。"""
    lay = blank()
    d = ImageDraw.Draw(lay)
    for (x0, x1, col, a0) in ((80, 101, (255, 200, 130), 46), (MOUTH_X0, W - 1, (220, 224, 226), 44)):
        for y in range(FLOOR0, FLOOR0 + 16):
            u = (y - FLOOR0) / 16.0
            a = int(a0 * (1 - u) ** 1.2)
            for x in range(x0, x1 + 1):
                if (x + y) % 2 == 0 or u < 0.3:
                    if hash01(x, y, 501) < 0.85 - 0.5 * u:
                        d.point((x, y), fill=C4(col, a))
    im.alpha_composite(lay)


# ============================================================ 玻璃：倒影 / 货架 / 碎片
@lru_cache(maxsize=1)
def opposite():
    """镜头这一侧的那堵墙（画面里看不见；镜子、橱窗里映出来的就是它），屏幕坐标 320×180 的 float RGB。
    y < 52 天（两根电线）、52–55 挑檐、56–99 墙（带铁栏的窗、门、排水管、窗下的晾衣绳）、≥ 100 湿地面。"""
    a = np.zeros((H, W, 3), np.float32)
    for y in range(H):
        if y < 52:
            a[y] = mix((196, 200, 206), (176, 182, 190), y / 52.0)
        elif y < 56:
            a[y] = (76, 78, 84) if y < 55 else (60, 62, 68)
        elif y < 100:
            a[y] = (116, 118, 120)
        else:
            a[y] = (78, 78, 80)
    nz = A._fbm(W, H, 6, 501) - 0.5
    a[56:100] *= (1 + 0.10 * np.round(nz[56:100] / 0.25) * 0.25)[..., None]
    a[56] *= 0.7
    a[99] *= 0.8
    for x in range(W):                                                          # 电线
        for (y0, s) in ((20, 6), (34, 4)):
            y = int(round(y0 + s * math.sin(x / 50.0)))
            a[y, x] = (70, 72, 78)
    for (wx0, wx1, wy0, wy1) in ((50, 64, 64, 82), (226, 248, 66, 84), (282, 300, 60, 80)):    # 带铁栏的窗
        a[wy0 - 2:wy1 + 3, wx0 - 2:wx1 + 3] = (132, 132, 130)
        a[wy0:wy1 + 1, wx0:wx1 + 1] = (70, 74, 80)
        for x in range(wx0 + 2, wx1, 4):
            a[wy0:wy1 + 1, x] = (98, 100, 104)
        a[wy1 + 2, wx0 - 2:wx1 + 3] = (150, 150, 146)
    a[64:100, 108:132] = (84, 76, 70)                                          # 一扇门
    a[64:100, 119] = (64, 58, 54)
    a[62:64, 106:134] = (132, 132, 130)
    a[56:100, 34:37] = (80, 80, 82)                                            # 排水管（镜子里看得到）
    a[56:100, 34] = (100, 100, 102)
    a[56:100, 266:269] = (80, 80, 82)
    for (x0, x1, y0, c) in ((40, 46, 58, (138, 104, 104)), (200, 210, 58, (170, 168, 160)), (254, 262, 58, (104, 116, 140))):
        a[y0:y0 + 8, x0:x1] = c                                               # 窗下晾着的衣服
    for y in range(100, H):                                                    # 湿地面：一道道亮的反光
        if y % 4 == 1:
            for x in range(W):
                if hash01(x // 6, y, 502) < 0.4:
                    a[y, x] = (104, 106, 110)
    return a


@lru_cache(maxsize=1)
def window_interior():
    """橱窗里面（玻璃框 80×50 那么大，局部坐标）：三层货架、糖果罐、汽水瓶、铁皮罐、肥皂、上面一串零食袋。"""
    gx0, gy0, gx1, gy1 = WINDOW_GLASS
    w, h = gx1 - gx0 + 1, gy1 - gy0 + 1
    im = Image.new('RGBA', (w, h), C4((70, 60, 50)))
    d = ImageDraw.Draw(im)
    for y in range(h):                                                         # 后墙（右边离店门的灯近，亮一点）
        for x in range(w):
            u = x / (w - 1)
            P(d, x, y, mix((60, 52, 46), (104, 86, 66), u ** 1.5))
    for x in range(0, w, 3):                                                   # 一串零食袋
        c = [(200, 60, 60), (230, 190, 60), (60, 130, 200), (90, 170, 90)][(x // 3) % 4]
        R(d, (x, 2, x + 1, 7), c)
        P(d, x, 1, (180, 180, 180))
    L(d, (0, 1, w - 1, 1), (150, 150, 150))
    for sy in (16, 30, 44):                                                    # 货架板
        L(d, (0, sy, w - 1, sy), (132, 96, 62))
        L(d, (0, sy + 1, w - 1, sy + 1), (60, 42, 30))
    for sy, row in ((16, 0), (30, 1), (44, 2)):                                # 货：每层随机摆
        x = 1 + row
        k = 0
        while x < w - 4:
            kind = int(hash01(row, k, 601) * 5)
            if kind == 0:                                                      # 玻璃糖果罐
                c = [(220, 80, 70), (240, 180, 60), (90, 180, 90), (230, 120, 170)][int(hash01(row, k, 602) * 4)]
                R(d, (x, sy - 8, x + 4, sy - 1), (150, 170, 166))
                R(d, (x + 1, sy - 6, x + 3, sy - 1), c)
                R(d, (x, sy - 9, x + 4, sy - 9), (176, 60, 50))
                P(d, x, sy - 7, (220, 236, 236))
                x += 6
            elif kind == 1:                                                    # 汽水瓶（三只）
                for j in range(3):
                    c = (70, 120, 70) if (j + k) % 2 else (110, 70, 40)
                    R(d, (x + j * 2, sy - 6, x + j * 2, sy - 1), c)
                    P(d, x + j * 2, sy - 7, (200, 190, 140))
                x += 7
            elif kind == 2:                                                    # 铁皮罐
                R(d, (x, sy - 5, x + 3, sy - 1), (170, 172, 176))
                R(d, (x, sy - 4, x + 3, sy - 3), (190, 60, 50) if k % 2 else (60, 90, 160))
                x += 5
            elif kind == 3:                                                    # 肥皂 / 盒子一摞
                for j in range(2):
                    R(d, (x, sy - 2 - j * 3, x + 4, sy - 1 - j * 3), (210, 200, 160) if j else (70, 110, 170))
                x += 6
            else:                                                              # 一包包的（立着）
                R(d, (x, sy - 7, x + 2, sy - 1), (230, 190, 70))
                L(d, (x, sy - 5, x + 2, sy - 5), (190, 60, 50))
                x += 4
            k += 1
    R(d, (0, 46, w - 1, h - 1), (96, 74, 52))                                  # 底下的台面
    L(d, (0, 46, w - 1, 46), (134, 104, 70))
    for (bx, c) in ((10, (220, 80, 70)), (40, (240, 180, 60)), (66, (90, 180, 90))):
        R(d, (bx, 47, bx + 2, 48), c)
    a = np.array(im).astype(np.float32)[..., :3]
    lum = a @ np.array((0.299, 0.587, 0.114), np.float32)
    a = lum[..., None] + (a - lum[..., None]) * 0.62                             # 压暗、去一点饱和
    return a * 0.66


def mirror_rgb():
    x0, y0, x1, y1 = MIRROR_GLASS
    o = opposite()[y0:y1 + 1, x0:x1 + 1]
    rgb = o * np.array((0.58, 0.63, 0.72), np.float32) + np.array((10, 13, 22), np.float32)
    v = np.linspace(0, 1, y1 - y0 + 1, dtype=np.float32)[:, None, None]
    return rgb * (1.0 - 0.10 * v)


def window_rgb(clear=False):
    x0, y0, x1, y1 = WINDOW_GLASS
    inside = window_interior()
    if clear:
        return inside * 1.10
    o = opposite()[y0:y1 + 1, x0:x1 + 1]
    refl = o * np.array((0.54, 0.60, 0.70), np.float32) + np.array((8, 12, 22), np.float32)
    return inside * 0.40 + refl * 0.62


SHEEN = (172, 192, 214)


def glass_fill(a, key, mb, wb):
    """占位色 → 倒影 / 货架；碎了的再描断口和裂纹；完好的加两道斜反光。"""
    for (kid, glass, rgbf, broken, seed) in ((1, MIRROR_GLASS, mirror_rgb, mb, 17), (2, WINDOW_GLASS, window_rgb, wb, 23)):
        x0, y0, x1, y1 = glass
        sub = key[y0:y1 + 1, x0:x1 + 1] == kid
        rgb = rgbf()
        blk = a[y0:y1 + 1, x0:x1 + 1, :3]
        blk[sub] = np.clip(rgb[sub], 0, 255)
        if broken:                                                            # 断口：亮一道（带着倒影的颜色）、里面一道暗（玻璃的厚度）
            rem, e, r, c = shard_mask(glass, seed)
            a[r, :3] = a[r, :3] * 0.72
            a[c, :3] = a[c, :3] * 0.45 + np.array((196, 210, 222), np.float32) * 0.55
            a[e, :3] = a[e, :3] * 0.40 + np.array(GLASS_EDGE, np.float32) * 0.60
            ys, xs = np.nonzero(e)                                            # 几个尖上闪一下
            for i in range(0, len(ys), 23):
                a[ys[i], xs[i], :3] = (244, 248, 252)
        else:                                                                 # 两道斜反光（静态；剧情自己再画会动的那道）
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    s = (x - x0) + (y1 - y) * 0.6
                    if 6 <= s % 46 < 8 or s % 46 == 11:
                        k = 0.30 if s % 46 < 8 else 0.16
                        a[y, x, :3] = a[y, x, :3] * (1 - k) + np.array(SHEEN, np.float32) * k
            a[y0, x0:x1 + 1, :3] = a[y0, x0:x1 + 1, :3] * 0.75                    # 上沿一道框的影子
    hole = key == 3
    if hole.any():
        x0, y0, x1, y1 = WINDOW_GLASS
        rgb = window_rgb(clear=True)
        blk = a[y0:y1 + 1, x0:x1 + 1, :3]
        sub = hole[y0:y1 + 1, x0:x1 + 1]
        blk[sub] = np.clip(rgb[sub], 0, 255)


def fallen_glass(im, which):
    """地上 / 沟里的一小片碎玻璃。"""
    d = ImageDraw.Draw(im)
    if which == 'mirror':
        rng = (30, 74, 139, 151, 31)
    else:
        rng = (210, 290, 139, 151, 37)
    x0, x1, y0, y1, seed = rng
    for i in range(18):
        fx = int(hrange(x0, x1, seed, i, 41))
        fy = int(hrange(y0, y1, seed, i, 42))
        if which == 'window' and hash01(seed, i, 46) < 0.3:
            fy = 117                                                            # 窗台上也落了几片
        sz = 1 + int(hash01(seed, i, 45) * 3)
        if sz == 1:
            P(d, fx, fy, GLASS_EDGE)
            P(d, fx + 1, fy, GLASS_RIM)
        else:
            pts = [(fx, fy), (fx + sz, fy - (sz - 1)), (fx + sz + 1, fy)]
            d.polygon(pts, fill=C4(GLASS_IN), outline=C4(GLASS_RIM))
            P(d, fx + sz, fy - (sz - 1), GLASS_EDGE)


WET_ROWS = 13                         # 湿地面上墙脚的倒影（只映到 y ≥ 118 的墙脚，碎不碎都一样）


def wet_reflection(a):
    """湿地面：贴着墙脚的十几行映出墙脚（2:1 压扁、越远越淡、隔行横晃 1 px）。"""
    src = a[..., :3].copy()
    for r in range(WET_ROWS):
        y = FLOOR0 + r
        sy = DRAIN[0] - 2 - 2 * r
        row = (src[sy] + src[sy - 1]) * 0.5
        if r % 2:
            row = np.roll(row, 1 if r % 4 == 1 else -1, axis=0)
        al = 0.30 * (1 - r / WET_ROWS) ** 1.3
        a[y, :, :3] = a[y, :, :3] * (1 - al) + row * 0.92 * al


@lru_cache(maxsize=4)
def pre(mb, wb):
    """打光 + 湿地面倒影 + 玻璃 + 碎玻璃（不含水洼）。"""
    a, key = lit(mb, wb)
    a = a.astype(np.float32)
    wet_reflection(a)
    glass_fill(a, key, mb, wb)
    im = toimg(a)
    if mb:
        fallen_glass(im, 'mirror')
    if wb:
        fallen_glass(im, 'window')
    return im


# ============================================================ 水洼
@lru_cache(maxsize=1)
def puddle_masks():
    nz = A._fbm(W, H, 3, 701)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    out = []
    for j, (cx, cy, rx, ry) in enumerate(PUDDLES):
        d = ((xx - cx) / rx) ** 2 + ((yy - cy) / (ry + 0.6)) ** 2 + (nz - 0.5) * 0.8
        m = d < 1.0
        for k in range(2):                                                       # 两头各鼓出去一块（不规则）
            sx = -1 if (j + k) % 2 else 1
            lx, ly = cx + sx * rx * hrange(0.45, 0.75, j, k, 702), cy + hrange(-0.5, 1.5, j, k, 703)
            lr = rx * hrange(0.30, 0.45, j, k, 704)
            m |= ((xx - lx) / lr) ** 2 + ((yy - ly) / (ry * 0.8)) ** 2 + (nz - 0.5) * 0.6 < 1.0
        out.append(m & (np.abs(yy - cy) <= ry))
    return out


@lru_cache(maxsize=1)
def puddle_layer():
    """水洼：一块平的水面——映出上面的墙（压扁、偏蓝）再混一点天光，比地面亮；远沿一道暗（墙脚的影），
    中间一道亮的天光反光，近沿一圈湿泥（只用完好状态的画面，碎不碎都一样）。"""
    src = np.array(pre(0, 0)).astype(np.float32)[..., :3]
    lay = np.zeros((H, W, 4), np.float32)
    skyc = np.array((160, 170, 184), np.float32)
    for j, ((cx, cy, rx, ry), m) in enumerate(zip(PUDDLES, puddle_masks())):
        ys, xs = np.nonzero(m)
        top, bot = ys.min(), ys.max()
        n = bot - top + 1
        span = int((DRAIN[0] - 4 - 30) / n)                                    # 每一行水面映 span 行墙（取平均 = 水里模糊的倒影）
        for y, x in zip(ys, xs):
            r = y - top
            u = r / max(1, n - 1)                                               # 0 = 远沿（映墙脚，暗）→ 1 = 近沿（映高处 + 天，亮）
            s1 = DRAIN[0] - 4 - span * r
            c = src[s1 - span + 1:s1 + 1, max(0, x - 1):x + 2].reshape(-1, 3).mean(0)
            c = c * np.array((0.56, 0.62, 0.74), np.float32) + np.array((4, 10, 22), np.float32)
            w = 0.08 + 0.50 * u ** 1.2
            c = c * (1 - w) + skyc * w
            if r == 0:
                c = c * 0.80
            lay[y, x, :3] = c
            lay[y, x, 3] = 255
        for i in range(4):                                                      # 几段长短不一的亮条（天光）
            hy = top + 2 + int(hash01(j, i, 712) * max(1, n - 3))
            hx = int(cx + hrange(-rx + 3, rx - 6, j, i, 713))
            for x in range(hx, hx + int(hrange(2, 7, j, i, 714))):
                if m[hy, x]:
                    lay[hy, x, :3] = lay[hy, x, :3] * 0.45 + np.array((214, 222, 232), np.float32) * 0.55
        ring = np.zeros_like(m)                                                # 一圈湿泥（只在近沿和两头）
        ring[1:] |= m[:-1]
        ring[:, 1:] |= m[:, :-1]
        ring[:, :-1] |= m[:, 1:]
        ring &= ~m
        for y, x in zip(*np.nonzero(ring)):
            if y >= cy - 1:
                lay[y, x, :3] = src[y, x] * 0.80
                lay[y, x, 3] = 255
    return toimg(lay)


@lru_cache(maxsize=4)
def render(mb, wb):
    """第 (mirror, window) 状态的整张底图（320×180，不透明，不含 tint / strip / 光）。"""
    im = pre(mb, wb).copy()
    im.alpha_composite(puddle_layer())
    return im


# ============================================================ 雨（strip，key 'rain'）
def _plot(a, x, y, col, al):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H and al > a[y, x, 3]:
        a[y, x, :3] = col
        a[y, x, 3] = al


DRIPS = [  # (x, 起点 y, 落到 y)
    (75, 75, 141), (82, 75, 141), (90, 75, 141), (97, 75, 141), (107, 75, 141),
    (203, 61, 141), (216, 61, 117), (231, 61, 117), (249, 61, 117), (266, 61, 117), (283, 61, 117), (293, 61, 141),
    (80, 54, 66), (92, 54, 66), (104, 54, 66), (121, 35, 57), (137, 35, 57), (155, 35, 57),
]


def rain_frame(t):
    f = int(math.floor(t * FPS_RAIN + 1e-6)) % N_RAIN
    a = np.zeros((H, W, 4), np.uint8)
    ph = f / N_RAIN
    # 远的雨丝（短、淡、一圈落一趟）+ 近一点的（长、亮、一圈落两趟）
    for (n, ln0, ln1, col, al, hd, trips, seed) in ((170, 3, 4, (168, 180, 198), 92, 132, 1, 801),
                                                    (70, 6, 8, (204, 212, 228), 128, 176, 2, 802)):
        for i in range(n):
            v = ph * trips + hash01(i, seed)
            kp = int(math.floor(v)) % trips                                    # 第几趟：每一趟换一个 x（不会老在同一列落）
            u = v % 1.0
            y = -10 + u * 200
            x = (hrange(0, W + 60, i, kp, seed + 1) - 0.25 * (y + 10)) % (W + 60) - 30
            ln = int(hrange(ln0, ln1 + 1, i, seed + 2))
            for k in range(ln):
                _plot(a, x + 0.25 * k, y - k, col, hd if k == 0 else al)
    # 地上溅起的水花（每个出现两帧：先是一个小冠，再是两点）
    for i in range(30):
        k0 = int(hash01(i, 811) * N_RAIN)
        s = (f - k0) % N_RAIN
        if s > 1:
            continue
        x = hrange(2, W - 2, i, 812)
        y = hrange(FLOOR0 + 1, H - 2, i, 813)
        if any(m[int(y), int(x)] for m in puddle_masks()):
            continue
        c = (206, 214, 226)
        if s == 0:
            _plot(a, x, y, c, 190)
            _plot(a, x - 1, y - 1, c, 150)
            _plot(a, x + 1, y - 1, c, 150)
        else:
            _plot(a, x - 2, y - 1, c, 120)
            _plot(a, x + 2, y - 1, c, 120)
    # 水洼里的涟漪（每个水洼三圈，错开相位；圈只画在水洼里面）
    pm = puddle_masks()
    for j, (cx, cy, rx, ry) in enumerate(PUDDLES):
        for r in range(3):
            f0 = (j * 5 + r * 4) % N_RAIN
            s = (f - f0) % N_RAIN
            if s >= 6:
                continue
            px_ = cx + hrange(-rx * 0.5, rx * 0.5, j, r, 821)
            py_ = cy + hrange(-1, 1, j, r, 822)
            if s == 0:
                _plot(a, px_, py_, (230, 236, 244), 220)
                _plot(a, px_, py_ - 1, (210, 220, 232), 150)
                continue
            erx, ery = 1 + 1.5 * s, 0.6 + 0.4 * s
            al = int(210 * (1 - s / 6.0))
            for q in range(36):
                th = q * math.tau / 36
                x = int(round(px_ + erx * math.cos(th)))
                y = int(round(py_ + ery * math.sin(th)))
                if 0 <= y < H and 0 <= x < W and pm[j][y, x]:
                    _plot(a, x, y, (196, 210, 224), al)
    # 雨篷 / 阳台滴水（越落越快）
    for i, (x, y0, y1) in enumerate(DRIPS):
        for rep in range(2):
            u = (ph + hash01(i, rep, 831)) % 1.0
            y = y0 + (y1 - y0) * u * u
            _plot(a, x, y, (214, 222, 234), 210)
            _plot(a, x, y - 1, (190, 202, 218), 140)
            if u > 0.88:
                _plot(a, x - 1, y1 - 1, (200, 210, 224), 150)
                _plot(a, x + 1, y1 - 1, (200, 210, 224), 150)
    # 排水管出水口的水柱 + 沟里的水花
    sx, sy = PIPE_X[1] + 3, 139
    for k in range(6):
        x = sx + k * 0.6
        y = sy + k * 0.9
        on = (k - f) % 3 == 0
        _plot(a, x, y, (220, 228, 238) if on else (160, 176, 194), 230 if on else 200)
        _plot(a, x + 1, y, (176, 190, 206), 170)
    for k in range(4):
        if (k + f) % 2 == 0:
            _plot(a, sx + 1 + k * 2 - 2, DRAIN[0] + (k % 2), (210, 220, 232), 190)
    # 明沟里流动的水光（往右流，一圈 48 px）
    for x in range(W):
        if (x - 4 * f) % 48 in (0, 1, 2) and not (76 <= x <= 105 or 114 <= x <= 148 or x >= MOUTH_X0):
            _plot(a, x, DRAIN[0] + 1, (140, 152, 166), 200)
    return Image.fromarray(a, 'RGBA')


def rain_fg_frame(t):
    """近处稀疏的长雨丝（fg，画在人物前面，alpha 很低）。"""
    f = int(math.floor(t * FPS_RAIN + 1e-6)) % N_RAIN
    a = np.zeros((H, W, 4), np.uint8)
    for i in range(34):
        v = f / N_RAIN * 3 + hash01(i, 851)
        kp = int(math.floor(v)) % 3
        u = v % 1.0
        y = -16 + u * 210
        x = (hrange(0, W + 60, i, kp, 852) - 0.25 * (y + 16)) % (W + 60) - 30
        ln = int(hrange(10, 15, i, 853))
        for k in range(ln):
            _plot(a, x + 0.25 * k, y - k, (220, 228, 240), 74 if k else 104)
    return Image.fromarray(a, 'RGBA')


# ============================================================ 雨停：一道斜光（pick + 水汽亮点 strip，key 'sunbeam'）
def beam_left(y):
    """光的左边沿（从右上的巷口斜着往左下照）。"""
    return BEAM_X0 - y * BEAM_SLOPE


def beam_s(x, y):
    return x - beam_left(y)


@lru_cache(maxsize=1)
def beam_img():
    bay = A._bayer(W, H)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    s = beam_s(xx, yy)
    e = np.minimum(s, BEAM_W - s)
    inb = e >= 0
    core = np.where(yy < FLOOR0, 0.22 + 0.12 * np.clip(1 - yy / 120.0, 0, 1), 0.30)
    rays = ((np.abs(s - 11) < 1.6) | (np.abs(s - 29) < 2.2)) & (yy < FLOOR0)     # 光里两道更亮的光柱
    core = core + np.where(rays, 0.08, 0.0)
    edge = np.clip(e / 5.0, 0, 1)
    a_beam = np.where(inb, core * np.where(edge >= 1, 1.0, np.where(bay < edge, 1.0, 0.45)), 0.0)
    near_mouth = np.clip(1 - np.hypot(xx - (MOUTH_X0 + 8), yy * 0.8) / 60.0, 0, 1)
    a_glob = 0.05 + 0.20 * near_mouth                                            # 整体暖一点，巷口那边亮得多
    al = 1 - (1 - a_beam) * (1 - a_glob)
    col = np.zeros((H, W, 3), np.float32)
    col[:] = (255, 238, 196)
    out = np.concatenate([col, (al * 255)[..., None]], -1)
    # 光落在地上：湿石板 / 水洼上闪的亮点
    for i in range(14):                                                          # 湿石板上闪的几点（一点 + 右边一点淡的）
        y = int(hrange(FLOOR0 + 2, H - 2, i, 901))
        x = int(beam_left(y) + hrange(3, BEAM_W - 4, i, 902))
        if 0 <= x < W - 1:
            out[y, x] = (255, 250, 228, 200)
            out[y, x + 1] = (255, 244, 210, 120)
    for m in puddle_masks():                                                     # 水洼在光里：整片亮起来 + 两三段很亮的横条
        sel = m & inb
        if not sel.any():
            continue
        ys, xs = np.nonzero(sel)
        for y, x in zip(ys, xs):
            out[y, x, 3] = max(out[y, x, 3], 110)
        hy = int(np.median(ys))
        for x in range(xs.min() + 1, xs.max()):
            if sel[hy, x] and (x // 4) % 2 == 0:
                out[hy, x] = (255, 250, 230, 210)
    return toimg(out)


def motes_frame(t):
    f = int(math.floor(t * FPS_MOTE + 1e-6)) % N_MOTE
    a = np.zeros((H, W, 4), np.uint8)
    for i in range(16):
        u = (f / N_MOTE + hash01(i, 911)) % 1.0
        y = hrange(20, 150, i, 912) + 10 * u
        x = beam_left(y) + hrange(4, BEAM_W - 4, i, 913)
        b = math.sin(math.pi * u)
        if b < 0.3:
            continue
        al = 210 if b > 0.8 else 140
        _plot(a, x, y, (255, 248, 220), al)
        if b > 0.9 and i % 3 == 0:
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                _plot(a, x + dx, y + dy, (255, 236, 190), 90)
    return Image.fromarray(a, 'RGBA')


# ============================================================ 导出 + 自检
def overlay_of(mb, wb, box=None):
    base = np.array(render(0, 0))
    cur = np.array(render(mb, wb))
    diff = (base != cur).any(-1)
    out = np.zeros_like(cur)
    out[diff] = cur[diff]
    im = Image.fromarray(out, 'RGBA')
    return im.crop(box) if box else im


def tint_layer():
    c, al = RAIN_TINT
    return Image.new('RGBA', (W, H), tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (int(255 * al),))


def anchors():
    gx0, gy0, gx1, gy1 = MIRROR_GLASS
    wx0, wy0, wx1, wy1 = WINDOW_GLASS
    fx0, fy0, fx1, fy1 = MIRROR_FRAME
    fx0, fx1 = fx0 - 1, fx1 + 1                                # 框歪了 ±1 px（下沿偏左、上沿偏右）
    sx0, sy0, sx1, sy1 = WINDOW_FRAME
    y_top, y_bot = 0, 160
    return dict(
        mirror_box=[gx0, gy0, gx1 + 1, gy1 + 1],            # 镜面（右下不含）= 剧情 GLASS.mirror
        window_box=[wx0, wy0, wx1 + 1, wy1 + 1],            # 橱窗玻璃（右下不含）= 剧情 GLASS.window
        puddles=[[cx, cy] for (cx, cy, rx, ry) in PUDDLES],  # 三个水洼中心
        puddle_r=[[rx, ry] for (cx, cy, rx, ry) in PUDDLES],  # 半宽、半高
        mirror=[48, 160], window=[248, 160],                 # 站在镜子 / 橱窗前的地面位置
        eye_a=[120, 163], eye_b=[211, 163],                  # 两个路人（剧情放 NPC）
        entrance=[312, 160],                                 # 巷口（右边，人从大街进来）
        walk_x=[4, 316],
        # 物件本身（特效 / 气泡 / 破坏物可以照这个放）
        mirror_frame=[fx0, fy0, fx1 + 1, fy1 + 1], window_frame=[sx0, sy0, sx1 + 1, sy1 + 1],
        mirror_center=[(gx0 + gx1 + 1) // 2, (gy0 + gy1 + 1) // 2], window_center=[(wx0 + wx1 + 1) // 2, (wy0 + wy1 + 1) // 2],
        mirror_shards=[30, 139, 76, 152], window_shards=[210, 139, 292, 152],     # 碎了以后地上碎玻璃的范围
        mouth=[MOUTH_X0, 0, W, 146],                         # 巷口外的大街那一条（亮）
        barber=[90, 156], door=[131, 156], pump=[PUMP_X + 4, 156], pipe_spout=[PIPE_X[1] + 4, 139],
        sunbeam_spot=[int(beam_left(y_bot) + BEAM_W / 2), y_bot],                 # 光落地的中心
        sunbeam_line=[[int(beam_left(y_top) + BEAM_W / 2), y_top], [int(beam_left(176) + BEAM_W / 2), 176]],
    )


def direct(t, rain=0, mirror=0, window=0, sun=0, fg=True):
    """直接拼一帧（不经导出），自检和预览用；层的顺序和 export 一样。"""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    im.alpha_composite(render(mirror, window))
    if rain:
        im.alpha_composite(tint_layer())
        im.alpha_composite(rain_frame(t))
    if sun:
        im.alpha_composite(beam_img())
        im.alpha_composite(motes_frame(t).crop(BEAM_BOX), BEAM_BOX[:2])
    if fg and rain:
        im.alpha_composite(rain_fg_frame(t))
    return im


def export(ex, BJ):
    layers = [dict(type='static', image=ex.img('alley', render(0, 0)))]
    for (key, box, mb, wb) in (('mirror', MIRROR_PICK, 1, 0), ('window', WINDOW_PICK, 0, 1)):
        ims = [ex.img(key + '0', blank(box[2] - box[0], box[3] - box[1])), ex.img(key + '1', overlay_of(mb, wb, box))]
        layers.append(dict(type='pick', images=ims, key=key, values=[0, 1], x=box[0], y=box[1], k=1.0))
    layers.append(dict(type='tint', key='rain', color=RAIN_TINT[0], alpha=RAIN_TINT[1]))
    layers.append(ex.bake('rain', (0, 0, W, H), N_RAIN, FPS_RAIN, rain_frame, screen=False, key='rain', k=1.0))
    layers.append(dict(type='pick', images=[ex.img('sun0', blank()), ex.img('sun1', beam_img())], key='sunbeam', values=[0, 1],
                       x=0, y=0, k=1.0))
    layers.append(ex.bake('sun_motes', BEAM_BOX, N_MOTE, FPS_MOTE, motes_frame, screen=False, key='sunbeam', k=1.0))
    fg = [ex.bake('rain_fg', (0, 0, W, H), N_RAIN, FPS_RAIN, rain_fg_frame, screen=False, key='rain', k=1.0)]
    st = ex.stage(W, GROUND, WALK, layers, fg, anchors())
    if ex.check_on:
        checks(ex, BJ, st)
    return st


def _walk_pts(v):
    if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
        for p in v:
            yield from _walk_pts(p)
    elif isinstance(v, (list, tuple)):
        yield list(v)


STATES = [dict(rain=r, mirror=m, window=w, sunbeam=s) for r in (0, 1) for m in (0, 1) for w in (0, 1) for s in (0, 1)]


def checks(ex, BJ, st):
    imgs = ex.images
    base = np.array(render(0, 0))
    ex.checked('底图整屏不透明', int((base[..., 3] != 255).sum()))
    # 1 所有 key 组合（雨 / 不雨 × 镜子 × 橱窗 × 光）整屏不露黑，导出层 vs 直接拼逐像素一样
    black = 0
    bad = 0
    for s in STATES:
        for t in (0.0, 0.37, 1.31):
            got = BJ.ref_render(st, imgs, 0, t, s)
            black += int((np.array(got.convert('RGB')).sum(-1) == 0).sum())
            bad += BJ.ndiff_rgba(got, direct(t, s['rain'], s['mirror'], s['window'], s['sunbeam']))
    ex.checked('16 种状态 × 3 个时刻 整屏不露黑', black)
    ex.checked('16 种状态 × 3 个时刻 导出 vs 直接拼（逐像素）', bad)
    # 2 strip 闭合 / 不跳帧 / 宽度 / 只画在框里
    for (name, fn, n, fps, box) in (('rain', rain_frame, N_RAIN, FPS_RAIN, (0, 0, W, H)), ('rain_fg', rain_fg_frame, N_RAIN, FPS_RAIN, (0, 0, W, H)),
                                    ('sun_motes', motes_frame, N_MOTE, FPS_MOTE, BEAM_BOX)):
        ex.checked('strip %s 闭合（t = n/fps vs 0）' % name, BJ.ndiff_rgba(fn(0.0).crop(box), fn(n / fps).crop(box)))
        steps = [BJ.ndiff_rgba(fn(i / fps), fn((i + 1) / fps)) for i in range(n)]
        ex.checked('strip %s 每一步变化差不多（最大 ≤ 1.6 × 中位）%s' % (name, steps), int(max(steps) > 1.6 * float(np.median(steps))))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), int((box[2] - box[0]) * n > 4096))
        bb = Image.fromarray(np.max([np.array(fn(i / fps))[..., 3] for i in range(n)], 0)).getbbox()
        ex.checked('strip %s 的像素都在框 %s 里 %s' % (name, box, bb),
                   int(bool(bb) and not (bb[0] >= box[0] and bb[1] >= box[1] and bb[2] <= box[2] and bb[3] <= box[3])))
    # 3 锚点都在地图里；站位锚点在可走范围里
    badn = 0
    for k, v in st['anchors'].items():
        for p in _walk_pts(v):
            if k == 'walk_x':
                badn += int(not (0 <= p[0] < p[1] <= W))
                continue
            for i in range(0, len(p) - 1, 2):
                badn += int(not (0 <= p[i] <= W and 0 <= p[i + 1] <= H))
    ex.checked('锚点都在地图里（%d 个）' % len(st['anchors']), badn)
    wx = st['anchors']['walk_x']
    badn = 0
    for k in ('mirror', 'window', 'eye_a', 'eye_b', 'entrance', 'barber', 'door', 'pump', 'sunbeam_spot'):
        x, y = st['anchors'][k]
        badn += int(not (wx[0] <= x <= wx[1] and WALK[0] <= y <= WALK[1]))
    for (x, y) in st['anchors']['puddles']:
        badn += int(not (wx[0] <= x <= wx[1] and WALK[0] <= y <= WALK[1]))
    ex.checked('站位锚点 / 水洼中心都在可走范围里（walk_x × y %d–%d）' % WALK, badn)
    # 4 pick：每张尺寸一致、第 0 张是空的、只在框里不同、两张 pick 不重叠、一起打开 = 各自叠上去
    for L_ in st['layers']:
        if L_['type'] == 'pick':
            sizes = {imgs[k].size for k in L_['images']}
            ex.checked('pick %s 两张尺寸一致 %s' % (L_['key'], sorted(sizes)), len(sizes) - 1)
            ex.checked('pick %s 第 0 张是空的' % L_['key'], int((np.array(imgs[L_['images'][0]])[..., 3] > 0).sum()))
    d10 = (np.array(render(1, 0)) != base).any(-1)
    d01 = (np.array(render(0, 1)) != base).any(-1)
    for (nm, dm, box) in (('mirror', d10, MIRROR_PICK), ('window', d01, WINDOW_PICK)):
        inb = np.zeros((H, W), bool)
        inb[box[1]:box[3], box[0]:box[2]] = True
        ex.checked('%s 1 只在框 %s 里不同（框外差异像素）' % (nm, list(box)), int((dm & ~inb).sum()), extra='框内 %d px' % int(dm.sum()))
        x0, y0, x1, y1 = MIRROR_GLASS if nm == 'mirror' else WINDOW_GLASS
        g = dm[y0:y1 + 1, x0:x1 + 1].mean()
        ex.checked('%s 1 玻璃区域大部分变了（%.0f%% ≥ 60%%）' % (nm, g * 100), int(g < 0.6))
    ex.checked('mirror 和 window 的差异像素不重叠', int((d10 & d01).sum()))
    comb = base.copy()
    comb[d10] = np.array(render(1, 0))[d10]
    comb[d01] = np.array(render(0, 1))[d01]
    ex.checked('mirror + window 同时碎 = 两张各自叠上去', int((comb != np.array(render(1, 1))).any(-1).sum()))
    # 5 玻璃框 = anchors；玻璃是一块平整、偏暗的反光面（剧情在里面画倒吊人）
    _, key = lit(0, 0)
    for (nm, kid, glass) in (('mirror_box', 1, MIRROR_GLASS), ('window_box', 2, WINDOW_GLASS)):
        ys, xs = np.nonzero(key == kid)
        got = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        want = st['anchors'][nm]
        x0, y0, x1, y1 = want
        full = int((key[y0:y1, x0:x1] == kid).sum())
        ex.checked('%s 玻璃像素的外框 %s = anchors %s，框里全是玻璃（%d / %d）' % (nm, got, want, full, (x1 - x0) * (y1 - y0)),
                   int(got != want) + ((x1 - x0) * (y1 - y0) - full))
        Y = base[y0:y1, x0:x1, :3].astype(np.float32) @ np.array((0.299, 0.587, 0.114), np.float32)
        ex.checked('%s 玻璃偏暗、平整（亮度均值 %.0f ∈ [45,115]，标准差 %.1f ≤ 24）' % (nm, Y.mean(), Y.std()),
                   int(not (45 <= Y.mean() <= 115)) + int(Y.std() > 24))
    # 6 水洼：三个都画了、中心在水面上
    for (cx, cy, rx, ry), m in zip(PUDDLES, puddle_masks()):
        ex.checked('水洼 (%d,%d) 面积 %d px（≥ 0.8 × 椭圆 %d）、中心在水面上、上下不超过 ±%d' % (cx, cy, int(m.sum()), int(math.pi * rx * ry), ry),
                   int(m.sum() < 0.8 * math.pi * rx * ry) + int(not m[cy, cx]) + int((np.nonzero(m)[0].min() < cy - ry) or (np.nonzero(m)[0].max() > cy + ry)))
    # 7 墙脚的东西都不进可走带（底边 < 146；地上的碎玻璃除外）
    for (mb, wb) in ((0, 0), (1, 1)):
        _, _, S = build(mb, wb)
        bad = [n for n, im, e in S.items if (im.getchannel('A').getbbox() or (0, 0, 0, 0))[3] - 1 >= WALK[0]]
        ex.checked('物件都不进可走带（mirror %d window %d）%s' % (mb, wb, bad), len(bad))
    _, _, S = build(0, 0)
    for k, (xa, xb) in SPEC_X.items():
        nm = {'mirror': 'mirror', 'barber': 'barber_awning', 'door': 'door', 'pipe': 'pipe', 'store_window': 'store_awning',
              'pump': 'pump'}[k]
        bb = S.bbox(nm)
        ex.checked('物件 %s x 范围 %d–%d（实际 %d–%d）' % (nm, xa, xb, bb[0], bb[2]), int(bb[0] != xa) + int(bb[2] != xb))
    # 8 可走带的对比度（压低）：y 150–176 横向强边像素比例；可走带后面 y 110–145 的强边比例
    Y = base[..., :3].astype(np.float32) @ np.array((0.299, 0.587, 0.114), np.float32)
    band = Y[150:177]
    edges = int((np.abs(np.diff(band, axis=1)) > 24).sum())
    ex.checked('可走带 y 150–176 强边像素（≤ 3%）', edges, limit=int(0.03 * band.size))
    band = Y[110:146]
    edges = int((np.abs(np.diff(band, axis=1)) > 40).sum())
    ex.checked('可走带后面 y 110–145 很强的边（Δ>40）像素（≤ 8%）', edges, limit=int(0.08 * band.size))
    # 9 体积
    tot = 0
    for k in set(k for L_ in st['layers'] + st['fg'] for k in ([L_.get('image')] + list(L_.get('images') or [])) if k):
        bio = io.BytesIO()
        imgs[k].save(bio, 'PNG', optimize=True)
        tot += bio.tell()
    ex.checked('整张背景 ≤ 400 KB（%.1f KB）' % (tot / 1024), int(tot > 400 * 1024))


# ============================================================ 单独预览
if __name__ == '__main__':
    out_dir = os.path.join(HERE, '_preview', 'ch4', 'after')
    os.makedirs(out_dir, exist_ok=True)
    combos = [(0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 1, 0), (1, 1, 1, 0), (0, 0, 0, 1), (0, 1, 1, 1)]
    sheet = Image.new('RGB', (W * 2 + 4, H * 3 + 8), (16, 16, 20))
    for i, (r, m, w, s) in enumerate(combos):
        sheet.paste(direct(0.3, r, m, w, s).convert('RGB'), ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    p = os.path.join(out_dir, 'india_alley_solo.png')
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(p)
    fr = Image.new('RGB', (W * 2 + 4, H * 2 + 4), (16, 16, 20))
    for i in range(4):
        fr.paste(direct(i / FPS_RAIN, 1).convert('RGB'), ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    p2 = os.path.join(out_dir, 'india_alley_solo_rain.png')
    fr.resize((fr.width * 2, fr.height * 2), Image.NEAREST).save(p2)
    print('ok', p, p2)
