# -*- coding: utf-8 -*-
r"""brain_inside —— 第5章：乔瑟夫的脑内（地图 brain_ch5，第 11 战「恋人」线 A：花京院和波鲁纳雷夫缩小了钻进去打）。
2026-10-18 ch5-road 组按体验版精度重画（改前是 ch5_scenes.brain()：五个大圆圈 + 两道波浪线 + 一层平涂的地）。

地图 320 宽（单屏，镜头不动），ground 150、可走带 130–176（脑内能上下飘得多一点，地面要宽）。
不是伤口、不是血肉——是“微观世界”：一条往深处收的粉红色有机隧道，暖光从隧道尽头透过来。
画面（屏幕坐标）：
  隧道      消失点 (160, 88)：四周的壁是一圈圈往深处缩小的褶皱（脑回），每一圈弯弯曲曲；褶皱的脊受尽头的暖光
            （亮、偏暖），沟里是深紫；越往深处越往尽头的粉白色光里化开（大气透视），四周最近的壁最暗、细节最多
  地面      y 112 往下是一层软软的组织（可走带 130–176）：一道道横着的浅褶（越近越宽）、湿润的高光点、
            零星的小细胞，对比压得很低
  神经元    壁上挂着六个神经元（细胞体：亮面朝尽头、细胞核 + 核仁；树突分叉、越分越细），远处还有两个小的；
            每个伸出一根轴突（带髓鞘的一节一节）顺着壁往隧道深处去——电信号光点顺着它流（signals strip）
  血管      左壁、右壁各一棵贴着壁分叉的血管（玫红，不是暗红的血：带一道湿亮的高光），一胀一缩（vessels strip）
  薄膜      天花板上垂下来两片半透明的薄膜（底下的褶皱透出来）、神经元之间一张薄网
  神经节    地上五个神经节（nodes 锚点：恋人分身出现的地方）：一圈小细胞围着一个发光的核，光一明一暗（nodes strip）
  漂浮物    几十颗小囊泡 / 光尘在空中慢慢飘（motes strip）
光：主光是隧道尽头的暖粉白光（褶皱的脊亮、朝着我们的那面暗），加一点从镜头这边来的冷紫补光；
   地面上可走带那一段只差一两级明暗，人物（游戏里缩成 0.5 倍）站上去看得清。

图层（从后往前）：
  base     static             整个隧道 + 地面 + 神经元 + 轴突 + 薄膜（只有 0 / 255 透明度）
  glow     strip  8 帧 @4 fps  隧道尽头的光一呼一吸（亮度一档一档地变）
  vessels  strip  8 帧 @8 fps  两棵血管一胀一缩（1 s 一下，像心跳）——左右两个框共用一个帧函数
  signals  strip 16 帧 @8 fps  电信号光点顺着轴突流向深处（金黄 / 白，带一节拖尾）——每根轴突一个框
  nodes    strip  8 帧 @4 fps  地上神经节的光一明一暗 + 一圈小火花
  motes    strip  8 帧 @4 fps  空中慢慢飘的小囊泡 / 光尘
  swell    pick   key pulse   0 = 不画（1×1 透明）；1 = 两棵血管胀大一圈、更红（乔瑟夫受伤）
  throb    strip  key pulse   血管周围一阵阵泛红的晕（半透明，8 帧 @8 fps）
  red      tint   key pulse   整片泛红（#e0283c，alpha 0.2；state.pulse 是数字时引擎会乘上它）

锚点：arrive [80,150]、center [160,150]、nodes [[60,140],[130,160],[200,138],[262,166],[290,146]]（神经节）；
      另外导出：vp [160,88]（隧道消失点）、floor_top 112（地面最远处的 y）、neurons（壁上神经元细胞体的中心）。
key：pulse。
单独运行：python -B tools\bg_new\brain_inside.py → tools\bg_new\_preview\ch5\after\brain_inside_solo.png
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
    key = 'bg_new_ch5_road_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'ch5_road_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
C = A._c4
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
ellipse, line = P.ellipse, P.line
frame_of = P.frame_of

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 320
GROUND = 150
WALK = (130, 176)
VP = (160, 88)                 # 隧道消失点（尽头的光）
FLOOR_TOP = 112                # 地面最远处（中间）的 y；两边抬到 126
RX, RY = 196.0, 124.0          # 壁的“深度”椭圆（越靠近画面边越近）
RING = 0.8                     # 每一圈褶皱往里缩 20%
FY = 236.0                     # 地面的深度换算：s = (y − VP.y) / (FY − VP.y)
N_GLOW, FPS_GLOW = 8, 4.0
N_VES, FPS_VES = 8, 8.0
N_SIG, FPS_SIG = 16, 8.0
N_NODE, FPS_NODE = 8, 4.0
N_MOTE, FPS_MOTE = 8, 4.0
N_THROB, FPS_THROB = 8, 8.0

ANCHORS = dict(
    arrive=[80, 150],
    center=[160, 150],
    nodes=[[60, 140], [130, 160], [200, 138], [262, 166], [290, 146]],   # 神经节（恋人分身出现的点）
)

# ============================================================ 调色（亮部偏暖、暗部偏紫）
WALL = [(54, 22, 58), (82, 32, 76), (116, 46, 96), (154, 64, 114), (192, 88, 134), (226, 122, 156), (248, 166, 182)]
FLOOR = [(150, 70, 112), (170, 84, 124), (188, 100, 136), (204, 118, 148), (220, 140, 162)]
GLOW = (255, 220, 222)          # 尽头的光
FOG = (236, 158, 182)           # 往深处化进去的颜色
SOMA = [(150, 82, 140), (192, 124, 172), (228, 168, 200), (248, 206, 224), (255, 236, 240)]
NUCLEUS = (132, 66, 132)
DEND = (224, 160, 196)
DEND_D = (170, 102, 150)
AXON = (238, 186, 208)
MYELIN = (252, 226, 236)
VESSEL = [(92, 20, 58), (124, 30, 70), (156, 42, 84), (200, 90, 124), (238, 166, 186)]     # 玫红偏紫，不是血的鲜红
VESSEL_SW = [(116, 14, 48), (156, 22, 58), (194, 38, 72), (234, 92, 112), (255, 168, 178)]
SIGNAL = [(255, 255, 236), (255, 232, 140), (248, 176, 96)]


# ============================================================ 隧道的几何
@lru_cache(maxsize=1)
def geom():
    """每个像素：是不是地面、深度 s（1 = 画面边上最近，→0 = 尽头）、绕消失点的角度。"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (xx - VP[0]) / RX
    dy = (yy - VP[1]) / RY
    s_w = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    # 地面边：中间最远（y 112），往两边抬到 y 124 左右（可走带 130 往下整条都是地）；边上一点一点鼓起来（肉褶的脚）
    xr = (xx[0] - VP[0]) / 160.0
    edge = FLOOR_TOP + 12 * xr ** 2 + 2.2 * np.sin(xx[0] * 0.09 + 0.7) + 1.4 * np.sin(xx[0] * 0.23 + 2.1)
    edge = np.minimum(edge, 127)
    ftop = np.broadcast_to(edge[None, :], (H, W))
    floor = yy >= ftop
    s_f = np.clip((yy - VP[1]) / (FY - VP[1]), 0.02, 2.0)
    s = np.where(floor, s_f, np.maximum(s_w, 0.02))
    return floor, s, th, ftop


def _profile(frac):
    """一圈褶皱的明暗（沿深度方向 0→1）：沟（最暗）→ 朝我们的那面（慢慢亮）→ 脊（最亮，尽头的光擦过来）→ 背面（很窄）→ 沟。"""
    lut = np.array([0, 0, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6, 5, 3, 1, 0], np.float32)
    i = np.clip((frac * 16).astype(int), 0, 15)
    return lut[i]


@lru_cache(maxsize=1)
def base_img():
    floor, s, th, ftop = geom()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    b = P.bayer(W, H)
    nz = A._fbm(W, H, 10, 501)
    nz2 = A._fbm(W, H, 4, 502)
    out = np.zeros((H, W, 3), np.float32)
    # ---- 壁：一圈圈弯弯曲曲的褶皱（脑回）
    u = np.log(np.maximum(s, 0.02)) / math.log(RING)
    u = u + 0.32 * np.sin(th * 3 + 1.1) + 0.18 * np.sin(th * 7 - 0.6) + 0.1 * np.sin(th * 13 + 2.0) + (nz - 0.5) * 0.9
    frac = u - np.floor(u)
    lev = _profile(frac)
    lev = lev + (nz2 - 0.5) * 1.0 + (b - 0.5) * 0.55                   # 级与级交界抖动（弱一点，不要满屏棋盘点）
    near = np.clip((s - 0.75) / 0.5, 0, 1)                             # 最近的壁再压暗一点（四周暗、中间亮）
    lev = lev - near * 1.6
    li = np.clip(np.floor(lev + 0.5), 0, len(WALL) - 1).astype(int)
    wall_c = np.array(WALL, np.float32)[li]
    # 往深处化进尽头的光（按深度分几档 + 抖动，不做平滑渐变）
    fog = np.clip((0.55 - s) / 0.5, 0, 1)
    fog = np.floor(fog * 5 + b * 0.9) / 5.0
    wall_c = wall_c * (1 - fog[..., None] * 0.85) + np.array(FOG, np.float32) * fog[..., None] * 0.85
    # ---- 地面：一层软软的组织——透视压扁的细胞纹（Voronoi：细胞边亮一级像湿的膜、中间本色）+ 很淡的横褶，
    #      只差一两级（可走带要静）
    from scipy.spatial import cKDTree
    v = np.log(np.maximum(s, 0.02)) / math.log(0.86)
    # 细胞在“地面坐标”里大小一样：横向按 1/s 放大、纵向按深度圈数，换算到屏幕上近处约 12×4 px（透视压扁）、远处更小
    X = (xx - VP[0]) / np.maximum(s, 0.05) / 26.0
    Y = v * 2.5
    pts = np.array([(hrange(-34, 34, i, 591), hrange(4, 30, i, 592)) for i in range(2400)], np.float32)
    tree = cKDTree(pts)
    dd, _ = tree.query(np.c_[X.ravel(), Y.ravel()], k=2)
    gap = (dd[:, 1] - dd[:, 0]).reshape(H, W)
    ff = v - np.floor(v + 0.12 * np.sin(xx * 0.035 + 0.4) + (nz - 0.5) * 0.5)
    flev = 2.0 + np.where(gap < 0.16, 1.0, 0.0) - np.where((ff > 0.05) & (ff < 0.2), 0.6, 0.0)
    flev = flev + (nz2 - 0.5) * 0.8 + (b - 0.5) * 0.5
    ffog = np.clip((0.4 - s) / 0.3, 0, 1)
    fi = np.clip(np.floor(flev + 0.5), 0, len(FLOOR) - 1).astype(int)
    floor_c = np.array(FLOOR, np.float32)[fi]
    ffog = np.floor(ffog * 4 + b * 0.9) / 4.0
    floor_c = floor_c * (1 - ffog[..., None] * 0.8) + np.array(FOG, np.float32) * ffog[..., None] * 0.8
    out = np.where(floor[..., None], floor_c, wall_c)
    # 地面和壁交界的一道褶缝（暗）+ 缝上面一道亮边（壁脚鼓起来）
    edge = floor & ~np.roll(floor, 1, axis=0)
    out[edge] = np.array(WALL[1], np.float32)                          # 暗缝
    dn1 = np.roll(edge, 1, axis=0) & floor
    out[dn1] = np.array(FLOOR[4], np.float32)                          # 地面这边鼓起来的一道亮唇
    up1 = np.roll(edge, -1, axis=0) & ~floor
    up2 = np.roll(edge, -2, axis=0) & ~floor
    out[up1] = np.array(WALL[5], np.float32)                           # 壁脚的肉褶（亮两行，受尽头的光）
    out[up2] = np.array(WALL[4], np.float32)
    # 尽头的光：消失点一圈圈粉白色的光晕（台阶状）
    r = np.sqrt(((xx - VP[0]) / 1.3) ** 2 + (yy - VP[1]) ** 2)
    for (rr, k) in ((34, 0.25), (22, 0.45), (13, 0.7), (7, 0.9)):
        m = (r < rr + (b - 0.5) * 3)
        out[m] = out[m] * (1 - k) + np.array(GLOW, np.float32) * k
    a = np.zeros((H, W, 4), np.uint8)
    a[..., :3] = np.clip(out, 0, 255).astype(np.uint8)
    a[..., 3] = 255
    im = P.img(a)
    draw_membranes(im)
    draw_floor_bits(im)
    draw_axons(im)
    draw_neurons(im)
    draw_nodes_static(im)
    return P.opaque(im)


# ============================================================ 薄膜（半透明：把底下的颜色和膜色混起来）
MEMBRANES = [  # (左上 x, 右上 x, 顶 y, 下垂最深的 y, 种子)：从天花板的褶皱上垂下来的薄纱
    (60, 124, 0, 44, 1), (204, 268, 0, 40, 2), (40, 76, 84, 112, 3),
]


def _veil_mask(x0, x1, y0, y1, sd):
    """一片下垂的薄膜：上沿挂在 y0，下沿是一条往下鼓、带两三处小波浪的弧（不是直边多边形）。"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = np.clip((xx - x0) / float(x1 - x0), 0, 1)
    sn = np.clip(np.sin(np.pi * u), 0, None)                            # float32 的 sin(π) 会是 −1e−7，先夹住
    low = y0 + (y1 - y0) * sn ** 0.8 + 2.0 * np.sin(u * 9 + sd) * sn
    return (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= low), low[0]


def draw_membranes(im):
    """半透明的膜：把底下已经画好的褶皱和膜色（粉白）混起来——底下的东西还透得出来；膜上几道竖着的细纹、
    下沿一线亮边（尽头的光从后面照透）、亮边下面一行淡淡的暗（膜的厚边）。"""
    a = np.array(im).astype(np.float32)
    col = np.array((255, 196, 220), np.float32)
    b = P.bayer(W, H)
    for (x0, x1, y0, y1, sd) in MEMBRANES:
        m, low = _veil_mask(x0, x1, y0, y1, sd)
        k = np.where(b < 0.5, 0.4, 0.32)
        a[m, :3] = a[m, :3] * (1 - k[m][:, None]) + col * k[m][:, None]
        for x in range(x0 + 4, x1 - 3, 6):                               # 竖着的细纹（顺着膜往下）
            for y in range(y0 + 1, int(low[x]) - 1):
                if hash01(x, y, sd, 511) < 0.7:
                    a[y, x, :3] = a[y, x, :3] * 0.88 + np.array((255, 220, 230), np.float32) * 0.12
        for x in range(x0 + 1, x1):
            y = int(low[x])
            if 0 <= y < H - 1:
                a[y, x, :3] = (255, 226, 236)
                a[y + 1, x, :3] = a[y + 1, x, :3] * 0.8
    im.paste(P.img(a))


# ============================================================ 地面上的小东西
def draw_floor_bits(im):
    """地面上的湿润高光（一两个像素的亮点，越近越大）、零星的小细胞（扁扁的圆、中间一点核）、几根细细的毛细管。"""
    floor, s, th, ftop = geom()
    d = ImageDraw.Draw(im)
    for i in range(70):
        x = int(hrange(4, W - 4, i, 521))
        y = int(hrange(FLOOR_TOP + 4, H - 1, i, 522))
        if not floor[y, x]:
            continue
        sc = float(s[y, x])
        if i % 3 == 0:                                                   # 小细胞
            rx = max(1, int(round(2.4 * sc * 1.6)))
            ellipse(d, x - rx, y - 1, x + rx, y + 1, FLOOR[3])
            px(d, x, y, FLOOR[1])
            px(d, x - rx + 1, y - 1, FLOOR[4])
        else:                                                            # 湿亮点
            px(d, x, y, FLOOR[4])
            if sc > 0.75:
                px(d, x + 1, y, (236, 170, 186))
    for (x0, y0, L, sd) in ((20, 172, 60, 1), (226, 168, 70, 2), (120, 176, 40, 3)):   # 毛细管（很细、很淡）
        x, y = float(x0), float(y0)
        for k in range(L):
            x += 1
            y += math.sin(k * 0.21 + sd) * 0.6
            if 0 <= int(y) < H and floor[int(y), int(x) % W]:
                px(d, int(x) % W, int(y), (178, 78, 118))


# ============================================================ 神经元 + 轴突
NEURONS = [  # (x, y, 半径, 种子)：壁上近处的六个 + 尽头附近两个小的
    (40, 66, 10, 1), (22, 100, 9, 2), (280, 64, 10, 3), (300, 98, 9, 4), (104, 22, 7, 5), (222, 26, 7, 6),
    (128, 76, 3, 7), (196, 72, 3, 8),
]


def axon_pts(i):
    """第 i 个神经元的轴突：从细胞体出发，顺着壁弯向消失点（三次贝塞尔），返回点列（屏幕坐标，浮点）。"""
    x, y, r, sd = NEURONS[i]
    tx = VP[0] + (x - VP[0]) * 0.18
    ty = VP[1] + (y - VP[1]) * 0.18
    c1 = (x + (VP[0] - x) * 0.25 + hrange(-10, 10, sd, 531), y + (VP[1] - y) * 0.1 + hrange(-8, 8, sd, 532))
    c2 = (x + (VP[0] - x) * 0.6, y + (VP[1] - y) * 0.55 + hrange(-6, 6, sd, 533))
    pts = []
    n = 60
    for k in range(n + 1):
        u = k / n
        bx = (1 - u) ** 3 * x + 3 * (1 - u) ** 2 * u * c1[0] + 3 * (1 - u) * u * u * c2[0] + u ** 3 * tx
        by = (1 - u) ** 3 * y + 3 * (1 - u) ** 2 * u * c1[1] + 3 * (1 - u) * u * u * c2[1] + u ** 3 * ty
        pts.append((bx, by))
    return pts


def draw_axons(im):
    d = ImageDraw.Draw(im)
    for i in range(len(NEURONS)):
        pts = axon_pts(i)
        r = NEURONS[i][2]
        for k, (x, y) in enumerate(pts):
            u = k / (len(pts) - 1)
            c = mix(AXON, FOG, u * 0.8)
            px(d, int(round(x)), int(round(y)), c)
            if r >= 6 and u < 0.45:                                      # 近处的轴突粗一点，下边一线暗
                px(d, int(round(x)), int(round(y)) + 1, mix(DEND_D, FOG, u * 0.6))
            if r >= 6 and k % 6 == 3 and u < 0.7:                        # 髓鞘：一节一节的亮珠
                px(d, int(round(x)) - 1, int(round(y)), mix(MYELIN, FOG, u * 0.6))
                px(d, int(round(x)) + 1, int(round(y)), mix(MYELIN, FOG, u * 0.6))


def _dendrite(d, x, y, ang, L, depth, sd, col, w):
    """一根树突：往外伸、慢慢弯，到头分两叉（递归 depth 层），越分越细越淡。"""
    ex = x + math.cos(ang) * L
    ey = y + math.sin(ang) * L
    mx = (x + ex) / 2 + math.cos(ang + 1.57) * hrange(-2, 2, sd, 541)
    my = (y + ey) / 2 + math.sin(ang + 1.57) * hrange(-2, 2, sd, 542)
    line(d, [(x, y), (mx, my), (ex, ey)], col, width=w)
    if depth > 0:
        for k, da in enumerate((-0.55, 0.5)):
            _dendrite(d, ex, ey, ang + da + hrange(-0.2, 0.2, sd, k, 543), L * hrange(0.55, 0.75, sd, k, 544),
                      depth - 1, sd * 3 + k + 1, mix(col, DEND_D, 0.3), 1)
    else:
        px(d, int(round(ex)), int(round(ey)), mix(col, (255, 230, 240), 0.4))   # 树突末端的小突触扣


def draw_neurons(im):
    """细胞体：略呈三角的圆，朝尽头那边（消失点方向）亮、背面暗，外沿描深紫；中间细胞核 + 一点亮的核仁；
    树突五六根，近处的分两层叉。"""
    d = ImageDraw.Draw(im)
    for i, (x, y, r, sd) in enumerate(NEURONS):
        far = r <= 3
        col = mix(DEND, FOG, 0.55) if far else DEND
        n = 4 if far else 6
        for k in range(n):
            ang = k / n * math.tau + hrange(-0.3, 0.3, sd, k, 551)
            _dendrite(d, x, y, ang, r * hrange(1.8, 2.6, sd, k, 552), 0 if far else (2 if k % 2 == 0 else 1),
                      sd * 10 + k, col, 2 if (r >= 7 and k % 2 == 0) else 1)
    for i, (x, y, r, sd) in enumerate(NEURONS):
        far = r <= 3
        pal = [mix(c, FOG, 0.5) for c in SOMA] if far else SOMA
        lx, ly = VP[0] - x, VP[1] - y                                    # 朝光的方向
        L = math.hypot(lx, ly) or 1.0
        lx, ly = lx / L, ly / L
        for yy in range(int(y - r - 1), int(y + r + 2)):
            for xx in range(int(x - r - 1), int(x + r + 2)):
                ddx, ddy = (xx - x) / r, (yy - y) / (r * 0.9)
                ang = math.atan2(ddy, ddx)
                rad = 1.0 + 0.12 * math.cos(3 * ang + sd)                # 略呈三角
                dd = math.hypot(ddx, ddy) / rad
                if dd > 1.0:
                    continue
                if dd > 0.82:
                    c = pal[0]                                           # 外沿描边（深紫）
                else:
                    lam = (ddx * lx + ddy * ly) * 0.8 + (1 - dd) * 0.6
                    c = pal[min(4, max(1, int(lam * 2.2 + 2.2)))]
                px(d, xx, yy, c)
        if not far:                                                      # 细胞核 + 核仁
            nx, ny = int(round(x + lx * r * 0.15)), int(round(y + ly * r * 0.15))
            nr = max(2, r // 3)
            ellipse(d, nx - nr, ny - nr, nx + nr, ny + nr, NUCLEUS)
            px(d, nx + int(lx * 1.5), ny + int(ly * 1.5), (255, 240, 210))
            px(d, nx - nr + 1, ny - nr + 1, mix(NUCLEUS, SOMA[3], 0.4))


# ============================================================ 神经节（地上）
def node_scale(y):
    floor, s, th, ftop = geom()
    return float(np.clip(s[int(y), W // 2] * 1.25, 0.45, 1.3))


def draw_nodes_static(im):
    """神经节的底：一个扁圆的浅色垫子 + 一圈小细胞（1–2 px 的疙瘩），往两边拉出几根细纤维。"""
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate(ANCHORS['nodes']):
        k = node_scale(y)
        rx, ry = 8 * k, 3 * k
        for j in range(4):                                              # 纤维
            ang = j / 4 * math.pi + 0.3
            L = 18 * k
            line(d, [(x + math.cos(ang) * rx, y + math.sin(ang) * ry * 0.4),
                     (x + math.cos(ang) * (rx + L), y + math.sin(ang) * (ry + L * 0.12))], FLOOR[3])
            line(d, [(x - math.cos(ang) * rx, y - math.sin(ang) * ry * 0.4),
                     (x - math.cos(ang) * (rx + L), y - math.sin(ang) * (ry + L * 0.12))], FLOOR[3])
        ellipse(d, x - rx, y - ry, x + rx, y + ry, (214, 128, 160))
        ellipse(d, x - rx * 0.6, y - ry * 0.6, x + rx * 0.6, y + ry * 0.6, (236, 160, 184))
        for j in range(9):
            ang = j / 9 * math.tau
            cx, cy = x + math.cos(ang) * rx * 0.95, y + math.sin(ang) * ry * 0.95
            px(d, int(round(cx)), int(round(cy)), (246, 190, 208))
            px(d, int(round(cx)), int(round(cy)) + 1, (176, 92, 130))


NODE_BOXES = []
for _i, (_x, _y) in enumerate(ANCHORS['nodes']):
    _k = 1.3
    NODE_BOXES.append(('nodes%d' % _i, (int(_x - 9 * _k) - 1, int(_y - 3 * _k) - 4, int(_x + 9 * _k) + 2, int(_y + 3 * _k) + 2)))


@lru_cache(maxsize=None)
def _node_f(f):
    """神经节的光：核一明一暗（四档），亮的时候外面一圈小火花转半格。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate(ANCHORS['nodes']):
        k = node_scale(y)
        v = 0.5 + 0.5 * math.sin(math.tau * f / N_NODE + i * 1.3)
        lv = int(v * 3.99)
        cols = [(240, 170, 192), (248, 196, 210), (255, 220, 228), (255, 244, 236)]
        rx, ry = 3 * k + lv * 0.5, 1.2 * k + lv * 0.25
        ellipse(d, x - rx, y - ry, x + rx, y + ry, cols[lv])
        px(d, x, y, (255, 255, 246) if lv >= 2 else cols[lv])
        ang = (f / N_NODE + i * 0.17) * math.tau                         # 一颗淡淡的光尘一直绕着神经节转
        px(d, int(round(x + math.cos(ang) * 9 * k)), int(round(y + math.sin(ang) * 2.6 * k)), (250, 200, 214))
        if lv >= 2:
            for j in range(4):
                ang = (j / 4 + f / N_NODE * 0.5 + i * 0.1) * math.tau
                px(d, int(round(x + math.cos(ang) * 6 * k)), int(round(y + math.sin(ang) * 2.2 * k)) - 1, (255, 236, 170))
    return im


def nodes_frame(t):
    return _node_f(frame_of(t, N_NODE, FPS_NODE))


# ============================================================ 尽头的光（strip）
GLOW_BOX = (VP[0] - 30, VP[1] - 22, VP[0] + 31, VP[1] + 23)


@lru_cache(maxsize=None)
def _glow_f(f):
    """尽头的光一呼一吸：最里面两圈的半径跟着 sin 变（台阶状，整像素）。只画框里，外圈留给 base。"""
    im = A._new(W, H)
    a = np.zeros((H, W, 4), np.uint8)
    base = np.array(base_img())
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    b = P.bayer(W, H)
    r = np.sqrt(((xx - VP[0]) / 1.3) ** 2 + (yy - VP[1]) ** 2)
    v = 0.5 + 0.5 * math.sin(math.tau * f / N_GLOW)
    x0, y0, x1, y1 = GLOW_BOX
    sub = np.zeros((H, W), bool)
    sub[y0:y1, x0:x1] = True
    out = base[..., :3].astype(np.float32)
    for (rr, k) in ((16 + v * 4, 0.35), (9 + v * 3, 0.6), (4 + v * 2, 0.85)):
        m = (r < rr + (b - 0.5) * 2) & sub
        out[m] = out[m] * (1 - k) + np.array(GLOW, np.float32) * k
    chg = sub & (np.abs(out - base[..., :3]).max(-1) > 0)
    a[chg, :3] = np.clip(out[chg], 0, 255).astype(np.uint8)
    a[chg, 3] = 255
    return P.img(a)


def glow_frame(t):
    return _glow_f(frame_of(t, N_GLOW, FPS_GLOW))


# ============================================================ 血管（strip + pick）
VESSEL_TRUNKS = [  # (起点, 控制点 1, 控制点 2, 终点, 起始粗细, 种子)：贴着壁从画面边往隧道深处去
    ((0, 124), (34, 112), (84, 100), (134, 93), 3.6, 1),
    ((0, 40), (36, 46), (86, 70), (130, 82), 2.6, 2),
    ((320, 122), (284, 110), (236, 98), (186, 93), 3.6, 3),
    ((320, 36), (286, 44), (238, 68), (190, 82), 2.6, 4),
]


def _bez(p0, p1, p2, p3, n):
    pts = []
    for k in range(n + 1):
        u = k / n
        pts.append(((1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u * u * p2[0] + u ** 3 * p3[0],
                    (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u * u * p2[1] + u ** 3 * p3[1]))
    return pts


@lru_cache(maxsize=1)
def _vessel_paths():
    """[(点列, 起始粗细)]：四根主干（越往深处越细）+ 每隔十来个像素一根顺着褶皱横着长的小分枝。"""
    paths = []
    for (p0, p1, p2, p3, w0, sd) in VESSEL_TRUNKS:
        pts = _bez(p0, p1, p2, p3, 40)
        paths.append((pts, w0))
        for k in range(5, 34, 9):
            x, y = pts[k]
            nx, ny = pts[k + 1][0] - x, pts[k + 1][1] - y
            side = 1 if (k // 9) % 2 else -1
            ang = math.atan2(ny, nx) + side * hrange(0.7, 1.0, sd, k, 582)       # 斜着往外长（不是直角的刺）
            bl = (1 - k / 44.0) * hrange(14, 22, sd, k, 581)
            bp = [(x, y)]
            for j in range(1, 6):
                a_ = ang + 0.5 * j / 5 * side                                     # 顺着褶皱慢慢弯过去
                x += math.cos(a_) * bl / 5
                y += math.sin(a_) * bl / 5
                bp.append((x, y))
            paths.append((bp, w0 * 0.5 * (1 - k / 48.0)))
            fx, fy = bp[3]                                                        # 分枝再分一小叉
            fp = [(fx, fy)]
            fa = ang - side * 0.6
            for j in range(1, 4):
                fx += math.cos(fa) * bl / 7
                fy += math.sin(fa) * bl / 7
                fp.append((fx, fy))
            paths.append((fp, 1.0))
    return paths


def _draw_vessels(d, swell, pal, f=0):
    """按 swell 画血管：每段圆头粗线（暗边，半嵌在壁里）→ 里面一条本色 → 左上一线湿亮的高光；越往深处越细、
    颜色越往深处的雾里化。"""
    for (pts, w0) in _vessel_paths():
        n = len(pts)
        for j, ((xa, ya), (xb, yb)) in enumerate(zip(pts, pts[1:])):
            u = j / max(1, n - 1)
            w = max(1.0, w0 * (1 - u * 0.7) + swell)
            wi = int(round(w))
            fogk = 0.0 if w0 < 2 else u * 0.45
            c = [mix(cc, FOG, fogk) for cc in pal]
            line(d, [(xa, ya), (xb, yb)], c[0], width=wi + 1)
            if wi >= 2:
                line(d, [(xa, ya), (xb, yb)], c[2], width=wi - 1)
            if wi >= 3:
                line(d, [(xa - 1, ya - 1), (xb - 1, yb - 1)], c[3])
            if wi >= 3 and (j + f) % 3 == 0:                             # 湿亮的反光点顺着血管往深处挪（血在流）
                px(d, int((xa + xb) / 2) - 1, int((ya + yb) / 2) - 1, c[4])


def _beat(f):
    """心跳曲线（8 帧 1 s）：猛地胀一下、回落、再小胀一下、平。"""
    return (0.0, 1.0, 0.65, 0.3, 0.55, 0.25, 0.1, 0.02)[f % 8]


def _vessel_layer(swell, pal, f=0):
    im = A._new(W, H)
    _draw_vessels(ImageDraw.Draw(im), swell, pal, f)
    return P.opaque(im)


@lru_cache(maxsize=None)
def _ves_f(f):
    return _vessel_layer(_beat(f) * 0.9, VESSEL, f)


def vessels_frame(t):
    return _ves_f(frame_of(t, N_VES, FPS_VES))


@lru_cache(maxsize=1)
def _ves_boxes():
    a = np.array(_vessel_layer(1.0, VESSEL))[..., 3] > 0
    boxes = []
    for (x0, x1) in ((0, 160), (160, W)):
        sub = a[:, x0:x1]
        ys, xs = np.nonzero(sub)
        boxes.append((x0 + int(xs.min()), int(ys.min()), x0 + int(xs.max()) + 1, int(ys.max()) + 1))
    return boxes


VES_BOXES = [('vessels_l', None), ('vessels_r', None)]


@lru_cache(maxsize=1)
def swell_img():
    """pick 的第 1 张：两棵血管胀大一圈、更红（乔瑟夫受伤）。整块裁到血管的外框。"""
    im = A._new(W, H)
    _draw_vessels(ImageDraw.Draw(im), 1.8, VESSEL_SW)
    return P.opaque(im)


@lru_cache(maxsize=None)
def _throb_f(f):
    """血管周围一阵阵泛红的晕（半透明，透明度 0 / 50 / 90 三档）：跟着心跳 2 倍快地一胀一缩。"""
    beat = (1.0, 0.5, 0.15, 0.6, 1.0, 0.45, 0.1, 0.55)[f % 8]
    m = np.array(swell_img())[..., 3] > 0
    from scipy import ndimage
    halo1 = ndimage.binary_dilation(m, iterations=2 + int(beat * 3)) & ~m
    halo2 = ndimage.binary_dilation(m, iterations=1 + int(beat * 1.5)) & ~m
    a = np.zeros((H, W, 4), np.uint8)
    a[halo1, :3] = (240, 40, 70)
    a[halo1, 3] = 50
    a[halo2, :3] = (250, 70, 96)
    a[halo2, 3] = 90
    return Image.fromarray(a, 'RGBA')


def throb_frame(t):
    return _throb_f(frame_of(t, N_THROB, FPS_THROB))


# ============================================================ 电信号（strip，每根轴突一个框）
def _sig_box(i):
    pts = axon_pts(i)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (int(min(xs)) - 3, int(min(ys)) - 3, int(max(xs)) + 4, int(max(ys)) + 4)


SIG_BOXES = [('signals%d' % i, _sig_box(i)) for i in range(len(NEURONS))]


@lru_cache(maxsize=None)
def _sig_f(f):
    """每根轴突上两三颗光点从细胞体往隧道深处流（16 帧 2 s 一圈），近处 2×2 + 一节拖尾，远处 1 px，越远越淡。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for i in range(len(NEURONS)):
        pts = axon_pts(i)
        n = len(pts) - 1
        r = NEURONS[i][2]
        for j in range(3 if r >= 6 else 1):
            u = (f / N_SIG + j / 3.0 + hash01(i, 561)) % 1.0
            k = int(u * n)
            x, y = pts[k]
            xi, yi = int(round(x)), int(round(y))
            fade = u * 0.7
            core = mix(SIGNAL[0], FOG, fade)
            mid = mix(SIGNAL[1], FOG, fade)
            tail = mix(SIGNAL[2], FOG, fade)
            if r >= 6 and u < 0.5:
                rect(d, xi, yi, xi + 1, yi + 1, mid)
                px(d, xi, yi, core)
            else:
                px(d, xi, yi, core)
            for t_ in (1, 2):                                           # 拖尾（往细胞体那边）
                kb = max(0, k - t_ * 2)
                bx, by = pts[kb]
                px(d, int(round(bx)), int(round(by)), tail if t_ == 2 else mid)
    return im


def signals_frame(t):
    return _sig_f(frame_of(t, N_SIG, FPS_SIG))


# ============================================================ 漂浮的小囊泡 / 光尘（strip）
MOTE_BOX = (0, 0, W, 130)


@lru_cache(maxsize=None)
def _mote_f(f):
    """空中慢慢飘的东西：小囊泡（3×3 的圈、亮边在左上）+ 光尘（1 px），各自绕一个小椭圆转（8 帧一圈）。只在 y < 130。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    for i in range(34):
        cx = hrange(8, W - 8, i, 571)
        cy = hrange(10, 122, i, 572)
        ang = math.tau * (f / N_MOTE + hash01(i, 573)) * (1 if i % 2 else -1)
        x = int(round(cx + math.cos(ang) * hrange(2, 5, i, 574)))
        y = int(round(cy + math.sin(ang) * hrange(1, 3, i, 575)))
        if i % 3 == 0:
            for (ox, oy) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                px(d, x + ox, y + oy, (246, 196, 214))
            px(d, x - 1, y - 1, (255, 236, 240))
        else:
            px(d, x, y, (255, 220, 200) if i % 2 else (240, 200, 236))
    return im


def motes_frame(t):
    return _mote_f(frame_of(t, N_MOTE, FPS_MOTE))


# ============================================================ 组装 / 导出
@lru_cache(maxsize=1)
def _strips():
    vb = _ves_boxes()
    return ([('glow', GLOW_BOX, N_GLOW, FPS_GLOW, glow_frame)] +
            [('vessels_l', vb[0], N_VES, FPS_VES, vessels_frame), ('vessels_r', vb[1], N_VES, FPS_VES, vessels_frame)] +
            [(n, b, N_SIG, FPS_SIG, signals_frame) for (n, b) in SIG_BOXES] +
            [(n, b, N_NODE, FPS_NODE, nodes_frame) for (n, b) in NODE_BOXES] +
            [('motes', MOTE_BOX, N_MOTE, FPS_MOTE, motes_frame)])


@lru_cache(maxsize=1)
def build():
    sw = swell_img()
    bb = sw.getchannel('A').getbbox()
    return dict(base=base_img(), swell=sw.crop(bb), swell_box=bb, throb_box=(max(0, bb[0] - 6), max(0, bb[1] - 6),
                                                                            min(W, bb[2] + 6), min(H, bb[3] + 6)))


TINT = dict(color='#e0283c', alpha=0.2)


def compose(t=0.5, pulse=False):
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['base'])
    for (n, box, nn, fps, fn) in _strips():
        paste(out, fn(t).crop(box), box[0], box[1])
    if pulse:
        out.alpha_composite(R['swell'], R['swell_box'][:2])
        tb = R['throb_box']
        paste(out, throb_frame(t).crop(tb), tb[0], tb[1])
        col = tuple(int(TINT['color'][i:i + 2], 16) for i in (1, 3, 5))
        out.alpha_composite(Image.new('RGBA', (W, H), col + (int(255 * TINT['alpha']),)))
    return out


def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('base', R['base']), x=0, y=0)]
    for (n, box, nn, fps, fn) in _strips():
        layers.append(ex.bake(n, box, nn, fps, fn, screen=False, k=1.0))
    bb = R['swell_box']
    layers.append(dict(type='pick', key='pulse', values=[0, 1], x=bb[0], y=bb[1], k=1.0,
                       images=[ex.img('swell0', A._new(1, 1)), ex.img('swell1', R['swell'])]))
    layers.append(ex.bake('throb', R['throb_box'], N_THROB, FPS_THROB, throb_frame, screen=False, k=1.0, key='pulse'))
    layers.append(dict(type='tint', key='pulse', color=TINT['color'], alpha=TINT['alpha']))
    anchors = dict(ANCHORS)
    anchors.update(vp=list(VP), floor_top=FLOOR_TOP, neurons=[[x, y] for (x, y, r, sd) in NEURONS if r >= 6])
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    P.check_no_black(ex, BJ, st, '脑内 4 个时刻 × pulse 关 / 开 整屏都有画（没有露黑）', states=({}, {'pulse': True}))
    P.check_opaque(ex, '底图整张不透明', R['base'], (0, 0, W, H))
    P.check_alpha_binary(ex, '底图只有 0 / 255 两种透明度', R['base'])
    P.check_alpha_binary(ex, 'pick 胀大的血管只有 0 / 255 两种透明度', R['swell'])
    strips = list(_strips()) + [('throb', R['throb_box'], N_THROB, FPS_THROB, throb_frame)]
    P.check_strips(ex, BJ, strips)
    floor, s, th, ftop = geom()
    ex.checked('地面盖住整条可走带（y 130–176、x 0–320 里不是地面的像素）', int((~floor[WALK[0]:WALK[1] + 1]).sum()))
    a = np.array(R['base'])[..., :3].astype(np.float32)
    lum = P.lum(a)
    band = lum[WALK[0]:WALK[1] + 1]
    mu = float(np.median(band))
    far_ = int((np.abs(band - mu) > 45).sum())
    # 神经节的垫子是故意的亮点，不算
    nm = np.zeros_like(band, bool)
    for (x, y) in ANCHORS['nodes']:
        nm[max(0, y - 6 - WALK[0]):y + 6 - WALK[0], max(0, x - 30):x + 30] = True
    ex.checked('可走带 y 130–176 低对比（和中位数差 > 45 的像素，神经节一圈不算）',
               int(((np.abs(band - mu) > 45) & ~nm).sum()), limit=200, extra='含神经节 %d' % far_)
    out = 0
    for k in ('arrive', 'center'):
        x, y = ANCHORS[k]
        out += not (0 <= x < PW and WALK[0] <= y <= WALK[1] and floor[y, x])
    for (x, y) in ANCHORS['nodes']:
        out += not (0 <= x < PW and WALK[0] <= y <= WALK[1] and floor[y, x])
    ex.checked('锚点 arrive / center / 五个神经节都在可走带的地面上（不满足的条数）', out)
    ex.checked('pick 两张：0 = 1×1 透明、1 = 胀大的血管（不透明像素 > 300）',
               int(np.array(R['swell'])[..., 3].astype(bool).sum() <= 300))
    for t in (0.0, 1.25, 3.4, 11.0):
        for pu in (False, True):
            got = BJ.ref_render(st, ex.images, 0, t, {'pulse': True} if pu else {})
            ex.checked('脑内 t=%.2f pulse=%d 导出 vs 直接拼' % (t, pu), BJ.ndiff(got, compose(t, pu)))
    ex.note('可走带亮度中位数 %.0f、标准差 %.1f' % (mu, float(band.std())))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch5', 'after')
    os.makedirs(od, exist_ok=True)
    sheet = Image.new('RGB', (W * 2, H), (0, 0, 0))
    sheet.paste(compose(0.5).convert('RGB'), (0, 0))
    sheet.paste(compose(0.5, True).convert('RGB'), (W, 0))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(os.path.join(od, 'brain_inside_solo.png'))
    print('ok')
