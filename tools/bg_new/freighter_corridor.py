# -*- coding: utf-8 -*-
r"""freighter_corridor —— 无人货轮的货舱过道：第2章 第4战「力量」（猩猩的替身就是整艘船）的战场。

2026-10-10 晚 第2章按体验版的精度重画（ch2 背景代理）。改前是 later_stages.room('freighter', 640)：一排一模一样的门，
外加一张 strip 竖条当“肉”。现在侧视、640 宽、ground 156、可走带 y 148–176（地图 hold_ch2 的定义，不变）。从远到近：

  sea     舷窗外的夜海和雾（static，只从开着的那个舷窗露出来：镜头动的时候海平线不动 = 最远的一层）
  hold    货舱过道（pano k 1，640×180，不透明，只有舷窗玻璃是半透明的）：
            顶   甲板横梁的梁头（每 44 px 一根）、三根纵向管（黄色细管 / 包保温布的蒸汽管 / 红色消防总管）+ 吊架、
                 法兰、闸阀手轮、三台链式吊葫芦（手拉链 + 吊钩）、吊在横梁上的探照灯
            墙   铆钉钢板（四列板、板缝 + 铆钉、竖向扶强材、两道强肋骨）、纵桁 + 电缆管、五盏带网罩的舱灯（暖光池）、
                 消防管阀组（三只手轮 + 压力表 + 泄压排汽管）、配电箱 + 船用电话、灭火器、消防水带卷盘、
                 “NO.2 HOLD” 模板字、吊钩警告牌、两个用盖板封死的舷窗、雷达显示器；墙脚踢脚板 + 一条旧黄线；
                 靠墙的木箱 / 油桶 / 盖帆布的货 / 绳卷 / 工具箱（都在墙脚，不进可走带）
            两头 x 0–44 / 596–640：横隔舱壁 + 水密门（压紧把手全扣上、铁链挂锁、红牌）+ 门上的警报灯罩
            地   花纹钢板（防滑纹，越近越疏，压低对比）、板缝和沉头螺栓、中间走出来的磨亮带、油渍、两个排水格栅
  lamps   五盏舱灯的灯泡和内圈光（strip 24 帧 @12 fps，2 s 一圈，轻微闪；294 那盏接触不良，偶尔暗一下）
  flesh   墙面变肉（pick，key 'flesh'，values [0, .33, .66, 1]，640×180；和第 0 档一样的像素都是透明的：
          0 / .33 只有墙面在动；.66 / 1 地板花纹和明暗不变，只是被红灯照得偏红）
            0    正常的钢铁（这一张是空的）
            .33  四处钢板鼓起来、裂口里露出肉、周围爬出血管；附近的铆钉变成粉色疙瘩；蒸汽管上鼓起一节肠子
            .66  两头和中间大片墙面变成肉（板缝变皱褶、铆钉变疙瘩、扶强材变肋骨、管子变肠子 / 血管 / 筋）；
                 舷窗、雷达、水密门被肉包住；五盏舱灯变成发红光的“眼睛”，整个货舱打上红光
            1    整个货舱都是活的：一团团鼓起的粉紫色肉、血管网、肋骨、肉筋、天花板一排牙齿、舷窗变成眼皮；地板照样清楚
  vents   两处漏汽（泄压排汽管、蒸汽管保温布接口），strip 24 帧 @12 fps，画在 flesh 上面（变成肉以后照样“喘气”）
  radar   雷达显示器的扫描线（strip 24 帧 @12 fps，2 s 转一圈）
  alarm   （可选，key 'alarm'）门上两盏警报灯转起来（strip）+ 整屏红光（tint，数字 = 强度）
  fg      前景竖管（pick，key 'flesh'，k 1.3）：三根 4 px 宽、间隔约 260，站在任何一只眼睛正下方时都不挡眼睛；
          0 / .33 铁管，.66 缠上肉筋，1 变成筋腱

三只“眼睛”的底座（剧情在这里生成 prop:ship_eye_*，代码再画一个 18×10 的椭圆 + 黄眼珠 + 竖瞳）：
  eye_porthole    [120, 70]  黄铜圈舷窗（玻璃 r 10，透明，看得见外面的海）；.66 起铜圈变成眼皮
  eye_searchlight [360, 40]  吊在横梁上的探照灯（U 形叉架，灯面 r 10）；1 变成肉柄
  eye_radar       [560, 60]  雷达显示器（绿屏 r 10，扫描线一直转）；.66 起机箱被肉包住
四档里三个底座都在原位（自检）。
单独运行：python -B tools\bg_new\freighter_corridor.py → tools\bg_new\_preview\ch2\freighter_corridor_solo.png（四档 × 三个镜头）
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
from scipy import ndimage  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from engine.core import hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402

W, H = 320, 180
PW = 640
GROUND = 156
WALK = (148, 176)
PH = H                                    # flesh pick 整张高：.33 只动墙面；.66 / 1 地板的花纹、明暗不变，只是被红灯照得偏红
LEVELS = (0.0, 0.33, 0.66, 1.0)
N_FR, FPS = 24, 12.0                      # 所有 strip：24 帧 @12 fps = 2 s 一圈
C = A._c4

EYE_PORT, EYE_SEARCH, EYE_RADAR = (120, 70), (360, 40), (560, 60)
EYES = {'eye_porthole': EYE_PORT, 'eye_searchlight': EYE_SEARCH, 'eye_radar': EYE_RADAR}
GLASS_R = 10                              # 三个底座的玻璃 / 灯面 / 屏幕半径（眼睛 18×10 的椭圆 + 精灵都在里面）

# ---------------------------------------------------------------- 结构（竖向）
BEAMS = [8 + 44 * i for i in range(15)]                    # 梁头
STIFF = [52, 96, 140, 228, 272, 316, 404, 492, 536]          # 扶强材（4 px）
FRAMES = [184, 448]                                          # 强肋骨（8 px）
BULK = ((37, 44), (596, 603))                                # 两头横隔舱壁的边（含）
# ---------------------------------------------------------------- 结构（横向）
CEIL = 11                                 # 梁头下沿
SPIPE = (13, 15)                          # 黄色细管
BPIPE = (17, 26)                          # 包保温布的蒸汽管
MPIPE = (28, 33)                          # 红色消防总管
STRINGER = 35                             # 纵桁 35–37
WALL_T = 38
CONDUIT = 39                              # 电缆管 39–40
STRAKES = [(WALL_T + 3, 53, (132, 146, 142), 20), (54, 89, (138, 152, 148), 68),
           (90, 117, (130, 144, 140), 20), (118, 139, (100, 114, 116), 68)]
KICK = 140                                # 踢脚板 140–145
JUNC = 146                                # 墙脚阴影
FLOOR_T = 147
# ---------------------------------------------------------------- 物件
LAMPS = [70, 196, 294, 426, 500]
LAMP_Y = 47
PORTS_CLOSED = [(294, 70), (426, 70)]
HOISTS = [(162, 92), (250, 86), (524, 98)]
DOOR_Y = 74
MANIFOLD_Y = 96                           # 阀组横管 96–101
VENT1 = (238, 60)                         # 泄压排汽管口
VENT2 = (392, 16)                         # 蒸汽管保温布接口（往上冒）
BEACONS = [(20, 66), (620, 66)]

SEA_Y, SEA_H = 54, 36                     # 舷窗外的海（static）只画 y 54–89
FG_K, FGW = 1.3, 736                      # 前景：k 1.3，宽 320 + 1.3×320
FG_X = [180, 470, 700]                    # 镜头停在 0 / 200 / 320（看舷窗 / 探照灯 / 雷达）时都不挡眼睛

LAMP_BOXES = [(lx - 10, 37, lx + 11, 58) for lx in LAMPS]
V1_REGION = (200, 0, 280, 72)              # 漏汽 strip 的框按 24 帧实际冒到的范围算（steam_boxes）
V2_REGION = (360, 0, 440, 40)
RADAR_BOX = (EYE_RADAR[0] - 10, EYE_RADAR[1] - 10, EYE_RADAR[0] + 11, EYE_RADAR[1] + 11)
BEACON_BOXES = [(bx - 18, 50, bx + 19, 92) for bx, _ in BEACONS]

# .33 的鼓包（x, y, 露出来的肉半径）和 .66 的大片（x, y, 半径）
CORES = [(82, 98, 8.0), (232, 50, 6.5), (328, 84, 8.5), (486, 100, 8.0), (300, 21, 8.0)]
REGIONS = [(82, 98, 40), (232, 60, 34), (328, 84, 32), (486, 98, 38), (300, 20, 46), (120, 72, 30), (560, 74, 34),
           (180, 128, 30), (424, 120, 28)]


# ============================================================ 小工具
def rect(d, box, col):
    d.rectangle(box, fill=C(col))


def line(d, pts, col, w=1):
    d.line(pts, fill=C(col), width=w)


def px(d, x, y, col):
    d.point((x, y), fill=C(col))


def sh(c, k):
    return tuple(int(max(0, min(255, round(v * k)))) for v in c)


def arr(im):
    return np.array(im).astype(np.float32)


def toimg(a):
    return Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA')


def rgba_full(a3):
    out = np.zeros(a3.shape[:2] + (4,), np.float32)
    out[..., :3] = a3
    out[..., 3] = 255
    return out


def put(a, x, y, col):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]:
        a[y, x, :3] = col


def mul(a, x, y, k):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]:
        a[y, x, :3] = np.clip(a[y, x, :3] * k, 0, 255)


def blend(a, x, y, col, u):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]:
        a[y, x, :3] = a[y, x, :3] * (1 - u) + np.array(col, np.float32) * u


def in_boxes(x, y, boxes, pad=0):
    for (x0, y0, x1, y1) in boxes:
        if x0 - pad <= x < x1 + pad and y0 - pad <= y < y1 + pad:
            return True
    return False


# 3×5 模板字
FONT = {
    'N': ['1001', '1101', '1011', '1001', '1001'], 'O': ['111', '101', '101', '101', '111'],
    '.': ['0', '0', '0', '0', '1'], '2': ['111', '001', '111', '100', '111'], 'H': ['101', '101', '111', '101', '101'],
    'L': ['100', '100', '100', '100', '111'], 'D': ['110', '101', '101', '101', '110'],
    'R': ['110', '101', '110', '101', '101'], 'A': ['010', '101', '111', '101', '101'],
    'F': ['111', '100', '110', '100', '100'], 'I': ['1', '1', '1', '1', '1'], 'E': ['111', '100', '110', '100', '111'],
    ' ': ['0', '0', '0', '0', '0'], '0': ['111', '101', '101', '101', '111'], '1': ['01', '11', '01', '01', '01'],
    '3': ['111', '001', '011', '001', '111'], '4': ['101', '101', '111', '001', '001'],
    '5': ['111', '100', '111', '001', '111'], '6': ['111', '100', '111', '101', '111'],
    '7': ['111', '001', '010', '010', '010'], '8': ['111', '101', '111', '101', '111'],
    '9': ['111', '101', '111', '001', '111'], 'T': ['111', '010', '010', '010', '010'],
}


def text_pts(s):
    pts, x = [], 0
    for ch in s:
        g = FONT[ch]
        for yy, row in enumerate(g):
            for xx, v in enumerate(row):
                if v == '1':
                    pts.append((x + xx, yy))
        x += len(g[0]) + 1
    return pts, x - 1


def stencil(a, x, y, s, col, u=1.0, wear=0.0, seed=0):
    pts, _ = text_pts(s)
    for (dx, dy) in pts:
        if wear and hash01(seed, dx, dy, 3) < wear:
            continue
        blend(a, x + dx, y + dy, col, u)


def ring_shade(a, cx, cy, r0, r1, pal, light=(-0.6, -0.8), inner_flip=True):
    """圆环（r0 ≤ r < r1）：按法线和光的方向取 pal[0..3]（暗 → 亮）；内半圈法线朝里（凸起的圈）。"""
    for y in range(int(cy - r1 - 1), int(cy + r1 + 2)):
        for x in range(int(cx - r1 - 1), int(cx + r1 + 2)):
            r = math.hypot(x - cx, y - cy)
            if r0 <= r < r1:
                nx, ny = (x - cx) / max(r, 1e-6), (y - cy) / max(r, 1e-6)
                lv = -(nx * light[0] + ny * light[1])
                if inner_flip and (r - r0) < (r1 - r0) * 0.45:
                    lv = -lv
                i = 0 if lv < -0.45 else 1 if lv < 0.15 else 2 if lv < 0.7 else 3
                put(a, x, y, pal[i])


def disc_pts(cx, cy, r):
    out = []
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if math.hypot(x - cx, y - cy) < r:
                out.append((x, y))
    return out


def walk(x, y, ang, n, seed, turn=0.55, pull=(0.0, 0.0)):
    """随机游走一条线（血管 / 筋），返回整数点列。"""
    pts = []
    for s in range(n):
        ang += (hash01(seed, s, 1) - 0.5) * turn
        dx, dy = math.cos(ang) + pull[0], math.sin(ang) + pull[1]
        L = math.hypot(dx, dy) or 1
        x += dx / L
        y += dy / L
        p = (int(round(x)), int(round(y)))
        if not pts or pts[-1] != p:
            pts.append(p)
    return pts


# ============================================================ 调色
STEEL_HI = (176, 188, 184)
RUST, RUST_D = (150, 90, 56), (104, 60, 40)
FL = dict(deep=(66, 28, 60), dark=(112, 50, 94), mid=(150, 76, 116), base=(182, 98, 132), light=(210, 126, 152),
          hi=(236, 170, 190), sheen=(252, 220, 228), vein=(80, 38, 96), vein_hi=(120, 70, 132),
          bone=(232, 214, 198), bone_hi=(250, 240, 226), bone_sh=(196, 166, 158), bone_dk=(146, 110, 122),
          cart=(222, 170, 176), tooth=(242, 234, 216), tooth_sh=(204, 188, 170), gum=(146, 54, 90))
PIPE_LAG = [(220, 214, 196), (210, 204, 186), (202, 196, 178), (196, 190, 172), (188, 182, 164), (178, 172, 154),
            (164, 158, 140), (146, 140, 124), (124, 118, 104), (98, 94, 84)]
PIPE_RED = [(196, 90, 76), (176, 66, 54), (160, 54, 44), (146, 46, 38), (120, 36, 30), (86, 26, 24)]
PIPE_YEL = [(214, 184, 90), (178, 148, 58), (118, 94, 36)]
GUT = [(244, 184, 196), (226, 148, 166), (212, 126, 146), (198, 110, 134), (184, 98, 124), (168, 86, 116),
       (150, 72, 106), (130, 58, 96), (108, 46, 84), (84, 34, 70)]
ARTERY = [(220, 108, 138), (190, 70, 108), (168, 54, 94), (150, 44, 84), (122, 34, 70), (90, 24, 56)]
TENDON = [(240, 214, 208), (214, 178, 180), (166, 124, 138)]
BRASS = [(96, 74, 40), (150, 120, 66), (190, 160, 96), (224, 198, 128)]
SCOPE_PAL = [(14, 40, 26), (30, 92, 56), (24, 74, 46), (10, 28, 18), (60, 150, 90)]
LENS_PALS = [[(170, 182, 166), (196, 206, 188), (142, 156, 142), (226, 216, 160), (240, 246, 234)],   # 铁皮档
             [(186, 150, 162), (210, 176, 186), (156, 120, 138), (236, 170, 160), (246, 222, 226)],   # 红光下的玻璃
             [(176, 102, 132), (204, 138, 160), (146, 76, 110), (230, 162, 170), (248, 214, 222)]]    # 肉膜


def lens_pal(li):
    """探照灯灯面的颜色（第 li 档）：0 / .33 铁皮，.66 红光，1 一层肉膜。"""
    return LENS_PALS[0 if li < 2 else 1 if li == 2 else 2]


# ============================================================ 钢铁的表面（albedo，不打光）
def butts_for(off):
    xs = []
    for x in range(off, PW, 96):
        if x < 50 or x > 590 or any(-6 < x - s < 12 for s in STIFF + FRAMES):
            continue
        xs.append(x)
    return xs


@lru_cache(maxsize=1)
def rivets():
    """铆钉位置（钢铁画铆钉、肉画疙瘩都用这一份）。"""
    out = []
    for (y0, y1, paint, off) in STRAKES[1:]:
        for x in range(46, 594, 6):
            if not any(-3 <= x - s <= 6 for s in STIFF) and not any(-3 <= x - s <= 10 for s in FRAMES):
                out.append((x, y0 + 2))
    for (y0, y1, paint, off) in STRAKES:
        for bx in butts_for(off):
            for y in range(y0 + 3, y1 - 2, 6):
                out.append((bx + 3, y))
    return out


def stiffener_steel(a, x0, top=WALL_T, bot=KICK - 1):
    cols = [(166, 178, 174), (130, 142, 138), (112, 124, 120), (74, 84, 82)]
    for j, c in enumerate(cols):
        a[top:bot + 1, x0 + j] = c
    for y in range(top, bot + 1):
        mul(a, x0 + 4, y, 0.76)
        mul(a, x0 + 5, y, 0.9)
    for i, wdt in enumerate((3, 2, 1)):                      # 上下两头的肘板
        for k in range(1, wdt + 1):
            put(a, x0 - k, top + i, (124, 136, 132))
            put(a, x0 + 3 + k, top + i, (96, 108, 104))
            put(a, x0 - k, bot - i, (118, 130, 126))
            put(a, x0 + 3 + k, bot - i, (90, 100, 98))


def frame_steel(a, x0, top=0, bot=JUNC - 1):
    cols = [(172, 184, 180), (142, 154, 150), (132, 144, 140), (128, 140, 136), (122, 134, 130), (112, 124, 120),
            (88, 98, 96), (62, 70, 70)]
    for j, c in enumerate(cols):
        a[top:bot + 1, x0 + j] = c
    for y in range(top, bot + 1):
        mul(a, x0 + 8, y, 0.7)
        mul(a, x0 + 9, y, 0.85)
    for y in range(top + 4, bot - 2, 7):                     # 一列铆钉
        mul(a, x0 + 3, y, 1.25)
        mul(a, x0 + 4, y, 1.05)
        mul(a, x0 + 3, y + 1, 0.92)
        mul(a, x0 + 4, y + 1, 0.7)
    for i in range(9):                                        # 和纵桁、踢脚板连接的大肘板
        for k in range(1, 9 - i):
            put(a, x0 - k, WALL_T + i, (126, 138, 134) if k > 1 else (150, 162, 158))
            put(a, x0 + 7 + k, WALL_T + i, (100, 112, 108))
            put(a, x0 - k, KICK - 1 - i, (116, 128, 124))
            put(a, x0 + 7 + k, KICK - 1 - i, (92, 102, 100))


def bulk_steel(a, xa, xb):
    """两头横隔舱壁的边：比强肋骨还粗的一道竖梁。"""
    w = xb - xa + 1
    for j in range(w):
        u = j / (w - 1)
        c = mix((150, 162, 158), (58, 66, 66), u ** 1.3)
        a[0:JUNC, xa + j] = c
    for y in range(6, JUNC - 2, 8):
        mul(a, xa + 3, y, 1.25)
        mul(a, xa + 4, y + 1, 0.7)


def pipe_rows(a, x0, x1, y0, pal):
    for i, c in enumerate(pal):
        a[y0 + i, x0:x1] = c


def vpipe(a, x0, y0, y1, pal):
    """竖管：pal 从左（亮）到右（暗）。"""
    for j, c in enumerate(pal):
        a[y0:y1 + 1, x0 + j] = c


@lru_cache(maxsize=1)
def steel_surface():
    a = np.zeros((H, PW, 3), np.float32)
    for y in range(0, CEIL + 1):                             # 天花板（上一层甲板的底面）
        a[y] = mix((34, 40, 44), (58, 66, 70), y / CEIL)
    for y in range(CEIL + 1, STRINGER):                      # 管子后面的墙顶（很暗）
        a[y] = mix((54, 62, 64), (80, 92, 92), (y - CEIL - 1) / (STRINGER - CEIL - 2))
    # 四列板：每块板颜色差一点、上亮下脏
    for si, (y0, y1, paint, off) in enumerate(STRAKES):
        edges = [0] + butts_for(off) + [PW]
        for k in range(len(edges) - 1):
            xa, xb = edges[k], edges[k + 1]
            f = 0.965 + 0.07 * hash01(si, k, 7)
            for y in range(y0, y1 + 1):
                g = 1.03 - 0.07 * (y - y0) / max(1, y1 - y0)
                a[y, xa:xb] = np.array(paint, np.float32) * f * g
    a[WALL_T:WALL_T + 3] = a[WALL_T + 3] * 0.8                 # 纵桁下面的影子
    # 纵桁
    a[STRINGER] = (150, 162, 160)
    a[STRINGER + 1] = (112, 124, 122)
    a[STRINGER + 2] = (64, 72, 72)
    # 板缝（上一块板的边亮、下面一行暗）
    for sy in (54, 90, 118):
        a[sy - 1] = np.minimum(255, a[sy - 1] * 1.16)
        a[sy] = a[sy] * 0.6
    for (y0, y1, paint, off) in STRAKES:
        for bx in butts_for(off):
            a[y0:y1 + 1, bx] *= 0.62
            a[y0:y1 + 1, bx + 1] = np.minimum(255, a[y0:y1 + 1, bx + 1] * 1.14)
    for (x, y) in rivets():
        mul(a, x, y, 1.28)
        mul(a, x + 1, y, 1.04)
        mul(a, x, y + 1, 0.94)
        mul(a, x + 1, y + 1, 0.7)
    # 踢脚板 + 旧黄线 + 墙脚
    a[KICK] = (120, 130, 128)
    a[KICK + 1] = (112, 100, 62)
    a[KICK + 2:JUNC] = (60, 66, 68)
    a[JUNC] = (30, 34, 36)
    # 锈：铆钉下面的锈水、墙脚往上返的锈
    for i in range(70):
        x = int(hrange(46, 594, i, 11))
        y0 = int(hrange(56, 128, i, 12))
        L = int(hrange(3, 14, i, 13))
        for k in range(L):
            blend(a, x, y0 + k, RUST, 0.42 * (1 - k / L))
    bay = A._bayer(PW, H)
    nz = A._fbm(PW, 12, 6, 17)
    for y in range(128, KICK):
        for x in range(0, PW):
            if bay[y, x] < (y - 126) / 16 * (0.25 + 0.5 * nz[y - 128, x]):
                blend(a, x, y, RUST_D, 0.35)
    # 扶强材、强肋骨、两头的隔舱壁边
    for x0 in STIFF:
        stiffener_steel(a, x0)
    for x0 in FRAMES:
        frame_steel(a, x0)
    for xa, xb in BULK:
        bulk_steel(a, xa, xb)
    # 两头隔舱壁的板（门的周围，深一点）
    for (x0, x1) in ((0, BULK[0][0] - 1), (BULK[1][1] + 1, PW - 1)):
        a[WALL_T:KICK, x0:x1 + 1] = np.array((92, 104, 104), np.float32)
        for y in range(WALL_T + 8, KICK, 16):
            a[y, x0:x1 + 1] *= 0.7
            a[y - 1, x0:x1 + 1] = np.minimum(255, a[y - 1, x0:x1 + 1] * 1.12)
    # 梁头（I 字形截面）
    for bx in BEAMS:
        for y in range(0, CEIL - 2):
            put(a, bx - 1, y, (100, 110, 114))
            put(a, bx, y, (84, 94, 98))
            put(a, bx + 1, y, (60, 68, 72))
            mul(a, bx + 2, y, 0.8)
        for x in range(bx - 4, bx + 5):
            put(a, x, CEIL - 2, (128, 138, 142))
            put(a, x, CEIL - 1, (92, 102, 106))
            put(a, x, CEIL, (50, 56, 60))
    # 三根纵向管 + 吊架
    pipe_rows(a, 0, PW, SPIPE[0], PIPE_YEL)
    pipe_rows(a, 0, PW, BPIPE[0], PIPE_LAG)
    pipe_rows(a, 0, PW, MPIPE[0], PIPE_RED)
    for x in range(3, PW, 14):                               # 保温布的捆扎带
        a[BPIPE[0]:BPIPE[1] + 1, x] *= 0.8
        a[BPIPE[0]:BPIPE[1] + 1, x + 1] = np.minimum(255, a[BPIPE[0]:BPIPE[1] + 1, x + 1] * 1.05)
    for x in range(50, PW, 110):                             # 保温布接口的铁皮箍
        for j, k in enumerate((1.0, 0.82, 0.62)):
            for y in range(BPIPE[0] - 1, BPIPE[1] + 2):
                put(a, x + j, y, sh((150, 156, 158), k * (1.1 - 0.4 * (y - BPIPE[0]) / 10)))
    for i in range(26):                                      # 保温布上的脏印子
        x, y = int(hrange(0, PW, i, 21)), int(hrange(BPIPE[0] + 2, BPIPE[1], i, 22))
        for k in range(int(hrange(2, 6, i, 23))):
            mul(a, x + k, y, 0.86)
    for fx in range(20, PW, 80):                             # 消防总管的法兰
        if 330 < fx < 390:
            continue
        for j, c in enumerate(((150, 154, 156), (118, 122, 124), (84, 88, 90))):
            for y in range(MPIPE[0] - 1, MPIPE[1] + 2):
                put(a, fx + j, y, c)
        put(a, fx + 1, MPIPE[0], (50, 52, 54))
        put(a, fx + 1, MPIPE[1], (50, 52, 54))
    for ax in range(100, PW, 160):                           # 管上的白色流向箭头
        for k in range(4):
            put(a, ax + k, MPIPE[0] + 2, (226, 222, 214))
        put(a, ax + 4, MPIPE[0] + 2, (226, 222, 214))
        put(a, ax + 3, MPIPE[0] + 1, (210, 206, 198))
        put(a, ax + 3, MPIPE[0] + 3, (210, 206, 198))
    for bx in BEAMS:                                         # 吊架：从梁头下来箍住三根管
        hx = bx + 6
        for y in range(CEIL + 1, MPIPE[1] + 2):
            put(a, hx, y, (72, 78, 82))
            put(a, hx + 1, y, (108, 114, 118))
        for x in range(hx - 2, hx + 4):
            put(a, x, BPIPE[1] + 1, (60, 64, 68))
            put(a, x, MPIPE[1] + 1, (60, 64, 68))
    # 阀组：消防总管往下的竖管 + 横管 + 泄压排汽管
    vpipe(a, 212, MPIPE[1], MANIFOLD_Y, [(196, 90, 76), (166, 60, 50), (146, 46, 38), (100, 30, 26)])
    pipe_rows(a, 196, 247, MANIFOLD_Y, PIPE_RED)
    for x in (194, 195, 196):                                # 盲板法兰
        for y in range(MANIFOLD_Y - 1, MANIFOLD_Y + 7):
            put(a, x, y, (140, 144, 146) if x == 194 else (106, 110, 112))
    for j, c in enumerate(((150, 154, 156), (118, 122, 124))):
        for y in range(MANIFOLD_Y - 1, MANIFOLD_Y + 7):
            put(a, 247 + j, y, c)
    for y in range(MPIPE[1] + 1, MANIFOLD_Y):                # 竖管上的两道箍
        if y in (52, 80):
            for x in range(211, 217):
                put(a, x, y, (70, 74, 78))
    vpipe(a, VENT1[0], VENT1[1] + 2, MANIFOLD_Y - 1, [(150, 156, 158), (98, 102, 104)])
    for x in range(VENT1[0] - 1, VENT1[0] + 3):
        put(a, x, VENT1[1], (64, 68, 70))
        put(a, x, VENT1[1] + 1, (110, 114, 116))
    # 电缆管（纵桁下面，五盏灯挂在上面）+ 卡子
    a[CONDUIT] = (92, 98, 100)
    a[CONDUIT + 1] = (52, 56, 58)
    for x in range(10, PW, 22):
        put(a, x, CONDUIT + 2, (46, 50, 52))
    # 模板字
    stencil(a, 330, 100, 'NO.2 HOLD', (226, 224, 214), 0.85, wear=0.16, seed=5)
    for x0 in STIFF + FRAMES:
        stencil(a, x0 + (10 if x0 in FRAMES else 6), 124, str((x0 - 8) // 4 + 10), (206, 210, 204), 0.32, wear=0.1, seed=x0)
    return a


# ============================================================ 肉的表面（albedo，同样的结构）
def rib(a, x0, wdt, top, bot, bow, seed):
    """竖向一根肋骨（略弯），左亮右暗，两边是肉的高光 / 影子，每 22 px 一节软骨。"""
    if wdt <= 4:
        cols = [FL['bone_hi'], FL['bone'], FL['bone_sh'], FL['bone_dk']]
    else:
        cols = [FL['bone_hi'], FL['bone_hi'], FL['bone'], FL['bone'], FL['bone'], FL['bone_sh'], FL['bone_dk']][:wdt]
        cols = cols + [FL['bone_dk']] * (wdt - len(cols))
    for y in range(top, bot + 1):
        u = (y - top) / max(1, bot - top)
        xc = x0 + int(round(bow * math.sin(math.pi * u)))
        put(a, xc - 1, y, FL['hi'])
        for j, c in enumerate(cols):
            put(a, xc + j, y, c)
        put(a, xc + wdt, y, FL['deep'])
        put(a, xc + wdt + 1, y, FL['dark'])
        if (y - top + int(seed)) % 22 in (0, 1):
            for j in range(wdt):
                put(a, xc + j, y, FL['cart'] if (y - top + int(seed)) % 22 == 0 else sh(FL['cart'], 0.82))


def tube(a, x0, x1, y0, pal, seed, seg=(6, 10), pinch=1, sheen=True):
    """横向一根“肠子”：pal 从上到下，每节 6–10 px，节与节之间收一圈。"""
    n = len(pal)
    x = x0
    k = 0
    while x < x1:
        L = int(hrange(seg[0], seg[1] + 0.99, seed, k))
        for i in range(L):
            xx = x + i
            if xx >= x1:
                break
            u = i / max(1, L - 1)
            p = pinch if (u < 0.12 or u > 0.88) else 0
            wob = int(round(0.6 * math.sin(xx / 11.0 + seed)))
            for r in range(n):
                yy = y0 + r + wob
                if r < p or r >= n - p:
                    continue
                c = pal[r]
                if p and r == p:
                    c = sh(pal[min(n - 1, r + 2)], 0.95)
                put(a, xx, yy, c)
            if i == 0:
                for r in range(p + 1, n - p - 1):
                    put(a, xx, y0 + r + wob, sh(pal[min(n - 1, r + 2)], 0.85))
            if sheen and 2 <= i <= 3 and n >= 6:
                put(a, xx, y0 + 1 + wob, FL['sheen'])
        x += L
        k += 1


def vtube(a, x0, y0, y1, pal, seed, seg=(6, 10)):
    """竖向的“血管”：pal 从左到右。"""
    n = len(pal)
    y = y0
    k = 0
    while y < y1:
        L = int(hrange(seg[0], seg[1] + 0.99, seed, k))
        for i in range(L):
            yy = y + i
            if yy > y1:
                break
            u = i / max(1, L - 1)
            p = 1 if (u < 0.12 or u > 0.88) else 0
            for j in range(n):
                if j < p or j >= n - p:
                    continue
                put(a, x0 + j, yy, pal[j])
        y += L
        k += 1


def veins_on(a, roots, seed, length, allow=None, trunk=True, col=None, col_hi=None):
    """从 roots [(x, y, 角度)] 长出血管（会分叉）；allow(x, y) 为假的点不画。"""
    col = col or FL['vein']
    col_hi = col_hi or FL['vein_hi']
    for i, (x, y, ang) in enumerate(roots):
        L = int(length[0] + (length[1] - length[0]) * hash01(seed, i, 5))
        pts = walk(x, y, ang, L, seed * 131 + i, turn=0.7)
        for s, (vx, vy) in enumerate(pts):
            if allow and not allow(vx, vy):
                continue
            put(a, vx, vy, col)
            if trunk and s < L * 0.45:
                put(a, vx, vy - 1, col_hi)
        for b in range(int(L / 9)):
            s0 = int(hrange(2, max(3, len(pts) - 2), seed, i, b, 7))
            if s0 >= len(pts):
                continue
            bx, by = pts[s0]
            bang = ang + (0.9 if hash01(seed, i, b, 8) < 0.5 else -0.9) + hrange(-0.3, 0.3, seed, i, b, 9)
            for (vx, vy) in walk(bx, by, bang, int(hrange(4, 11, seed, i, b, 10)), seed * 977 + i * 31 + b, turn=0.8):
                if allow and not allow(vx, vy):
                    continue
                put(a, vx, vy, col)


def cord(a, x0, top, bot, seed):
    """竖向一根肉筋（扶强材变的）：中间粗两头细（像一束肌肉），扭一点，带斜的肌纤维，两头连着肉。"""
    pal = [(236, 142, 156), (210, 98, 120), (186, 72, 100), (160, 56, 86), (130, 42, 72), (98, 30, 58)]
    for y in range(top, bot + 1):
        u = (y - top) / max(1, bot - top)
        wdt = 3 + int(round(2.4 * math.sin(math.pi * u) ** 0.7))
        xc = x0 + 2 + 1.6 * math.sin(u * math.pi * 1.6 + seed)
        xa = int(round(xc - wdt / 2))
        for j in range(wdt):
            c = pal[min(5, int(j * 6 / wdt))]
            if (y * 2 + j + int(seed * 3)) % 5 == 0 and 0 < j < wdt - 1:
                c = sh(c, 0.82)                               # 斜的肌纤维
            put(a, xa + j, y, c)
        put(a, xa - 1, y, FL['hi'])
        put(a, xa + wdt, y, FL['deep'])
        put(a, xa + wdt + 1, y, FL['dark'])


@lru_cache(maxsize=1)
def flesh_creases():
    """肉墙的折痕（板缝 / 竖缝 / 筋和骨头的两边，都带一点歪）：True = 折痕。"""
    cr = np.zeros((H, PW), bool)
    for si, sy in enumerate((WALL_T + 1, 56, 118, KICK - 2)):
        for x in range(PW):
            w = int(round(1.4 * math.sin(x / 17.0 + si * 1.7) + 0.9 * math.sin(x / 7.3 + si)))
            y = sy + w
            if 0 <= y < H:
                cr[y, x] = True
    for x0 in STIFF:
        cr[WALL_T:KICK, x0 - 2] = True
        cr[WALL_T:KICK, x0 + 7] = True
    for x0 in FRAMES:
        cr[WALL_T:KICK, x0 - 6] = True
        cr[WALL_T:KICK, x0 + 13] = True
    for i in range(26):                                      # 几道斜的皱纹，让格子不那么规整
        x, y = hrange(50, 590, i, 51), hrange(60, 130, i, 52)
        ang = hrange(-0.5, 0.5, i, 53) + (math.pi / 2 if i % 3 == 0 else 0)
        for s in range(int(hrange(6, 16, i, 54))):
            xx, yy = int(round(x + s * math.cos(ang))), int(round(y + s * math.sin(ang)))
            if WALL_T < yy < KICK and 0 <= xx < PW:
                cr[yy, xx] = True
    return cr


@lru_cache(maxsize=1)
def flesh_surface():
    a = np.zeros((H, PW, 3), np.float32)
    bay = A._bayer(PW, H)
    # 一团团鼓起来的肉疙瘩（大小不一、横向略长的细胞状）+ 原来板缝变的几道横向深褶：
    #   离缝越远越高，按高度的坡度打光（左上亮、右下暗）
    cr = flesh_creases()
    Ds = ndimage.distance_transform_edt(~cr)
    seeds = []
    for gy in range(WALL_T - 8, KICK + 10, 15):
        for gx in range(-10, PW + 14, 19):
            seeds.append((gx + hrange(-7, 7, gx, gy, 1), gy + hrange(-5, 5, gx, gy, 2)))
    seeds = np.array(seeds, np.float32)
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    pts = np.stack([xx.ravel() * 0.8, yy.ravel()], -1)
    dist, idx = cKDTree(seeds * np.array((0.8, 1.0), np.float32)).query(pts, k=2)
    e = (dist[:, 1] - dist[:, 0]).reshape(H, PW)
    owner = idx[:, 0].reshape(H, PW)
    D = np.minimum(Ds, e * 1.1)
    n1 = A._fbm(PW, H, 24, 41)
    hgt = np.clip(D / 7.0, 0, 1) ** 0.5 + 0.16 * (n1 - 0.5)
    hgt = ndimage.gaussian_filter(hgt, 0.8)
    slope = (np.roll(np.roll(hgt, 1, 0), 1, 1) - np.roll(np.roll(hgt, -1, 0), -1, 1))
    n2 = A._fbm(PW, H, 7, 43)
    tone = np.clip(np.floor((n1 * 0.6 + n2 * 0.4 - 0.32) * 5.0 + (bay - 0.5) * 0.6), 0, 2).astype(int) + 1
    tone = tone + np.where(slope > 0.08, 1, 0) - np.where(slope < -0.08, 1, 0) - np.where(slope < -0.22, 1, 0)
    tone = np.where(Ds < 1.5, -1, np.where(D < 1.3, 0, np.where(D < 2.4, np.minimum(tone, 1), tone)))
    pal = np.array([FL['deep'], FL['dark'], FL['mid'], FL['base'], FL['light'], FL['hi']], np.float32)
    a[:] = pal[np.clip(tone + 1, 0, 5)]
    for k, (sx_, sy_) in enumerate(seeds):                    # 每一团左上角一小块湿亮
        hx, hy = int(round(sx_ - 4)), int(round(sy_ - 3))
        for (dx, dy, c) in ((0, 0, FL['sheen']), (1, 0, FL['hi']), (-1, 1, FL['hi'])):
            x, y = hx + dx, hy + dy
            if 0 <= x < PW and WALL_T + 2 <= y < KICK - 3 and owner[y, x] == k and D[y, x] > 3:
                a[y, x] = c
    # 天花板 = 上颚：暗肉 + 横向的皱褶
    for y in range(0, CEIL + 1):
        for x in range(PW):
            w = int(round(1.2 * math.sin(x / 9.0 + y)))
            c = mix((78, 32, 64), (118, 52, 90), y / CEIL)
            if (y + w) % 4 == 0:
                c = mix(c, (156, 78, 116), 0.6)
            a[y, x] = c
    # 管子后面：深的肉腔
    for y in range(CEIL + 1, STRINGER):
        a[y] = a[y] * 0.5 + np.array((70, 30, 62), np.float32) * 0.5
    # 纵桁 → 一道鼓起的肉棱
    for x in range(PW):
        w = int(round(0.8 * math.sin(x / 13.0)))
        put(a, x, STRINGER - 1 + w, FL['deep'])
        put(a, x, STRINGER + w, FL['hi'])
        put(a, x, STRINGER + 1 + w, FL['light'])
        put(a, x, STRINGER + 2 + w, FL['mid'])
        put(a, x, STRINGER + 3 + w, FL['deep'])
    for (x, y) in rivets():                                  # 铆钉 → 疙瘩
        put(a, x, y, FL['hi'])
        put(a, x + 1, y, FL['light'])
        put(a, x, y + 1, FL['base'])
        put(a, x + 1, y + 1, FL['dark'])
    # 血管网：从纵桁那道肉棱往下流，主干两个像素宽（上沿亮一点）
    roots = [(int(hrange(0, PW, i, 71)), WALL_T + 3, math.pi / 2 + hrange(-0.6, 0.6, i, 72)) for i in range(30)]
    roots += [(int(hrange(0, PW, i, 73)), int(hrange(60, 130, i, 74)), hrange(0, math.tau, i, 75)) for i in range(18)]
    veins_on(a, roots, 7, (24, 64), allow=lambda x, y: WALL_T <= y < KICK - 2)
    # 可走带后面（y 104 往下）压低对比：往模糊过的自己靠一半
    lo = slice(104, KICK - 2)
    sm = ndimage.gaussian_filter(a[lo], (2.0, 2.0, 0))
    k = np.clip((np.arange(104, KICK - 2) - 100) / 14.0, 0, 1)[:, None, None] * 0.5
    a[lo] = a[lo] * (1 - k) + sm * k
    # 墙脚：一道很厚的肉卷
    for x in range(PW):
        w = int(round(0.9 * math.sin(x / 15.0) + 0.6 * math.sin(x / 5.1)))
        top = KICK - 3 + w
        for y in range(top, JUNC + 1):
            u = (y - top) / max(1, JUNC - top)
            c = FL['deep'] if y == top else FL['hi'] if y == top + 1 else FL['light'] if u < 0.35 else \
                FL['base'] if u < 0.6 else FL['mid'] if u < 0.85 else FL['deep']
            put(a, x, y, c)
    # 扶强材 → 肉筋，强肋骨 → 大肋骨，两头的隔舱壁边 → 更粗的骨头
    for i, x0 in enumerate(STIFF):
        cord(a, x0, WALL_T + 1, KICK - 3, i * 1.7)
    for i, x0 in enumerate(FRAMES):
        rib(a, x0, 8, 2, JUNC - 2, 5 if i % 2 else -5, 5 + i)
    for i, (xa, xb) in enumerate(BULK):
        rib(a, xa, xb - xa + 1, 2, JUNC - 2, -3 if i == 0 else 3, 11)
    # 两头隔舱壁的肉：更深
    for (x0, x1) in ((0, BULK[0][0] - 1), (BULK[1][1] + 1, PW - 1)):
        a[WALL_T:KICK, x0:x1 + 1] *= 0.86
    # 管子 → 筋 / 肠子 / 血管
    for x in range(PW):
        for r, c in enumerate(TENDON):
            put(a, x, SPIPE[0] + r, c)
        if (x // 3) % 2 == 0:
            put(a, x, SPIPE[0] + 1, sh(TENDON[2], 1.1))
    tube(a, 0, PW, BPIPE[0], GUT, 3, seg=(6, 10), pinch=1)
    tube(a, 0, PW, MPIPE[0], ARTERY, 9, seg=(10, 16), pinch=1, sheen=False)
    for bx in BEAMS:                                         # 吊架 → 细筋
        hx = bx + 6
        for y in range(CEIL + 1, MPIPE[1] + 2):
            put(a, hx, y, (214, 176, 182))
            put(a, hx + 1, y, (170, 120, 138))
    vtube(a, 212, MPIPE[1], MANIFOLD_Y, [ARTERY[0], ARTERY[2], ARTERY[3], ARTERY[5]], 13)
    tube(a, 196, 248, MANIFOLD_Y, ARTERY, 17, seg=(8, 12), pinch=1, sheen=False)
    vtube(a, VENT1[0], VENT1[1] + 2, MANIFOLD_Y - 1, [TENDON[0], TENDON[2]], 19)
    for x in range(PW):                                      # 电缆管 → 一根粗血管
        put(a, x, CONDUIT, FL['vein_hi'])
        put(a, x, CONDUIT + 1, FL['vein'])
    # 梁头 → 牙齿（强肋骨那两根是大獠牙）
    for bx in BEAMS:
        big = any(abs(bx - f) <= 4 for f in FRAMES)
        L = 15 if big else 9 + int(hrange(0, 4, bx, 81))
        hw = 4 if big else 3
        for y in range(0, L + 1):
            u = y / L
            half = hw * (1 - u ** 1.6) + 0.4
            xa, xb = int(round(bx - half)), int(round(bx + half))
            for x in range(xa, xb + 1):
                c = FL['tooth'] if x < bx + half * 0.3 else FL['tooth_sh']
                if x == xa:
                    c = (255, 250, 238)
                put(a, x, y, c)
            put(a, xa - 1, y, FL['deep'])
            put(a, xb + 1, y, FL['deep'])
        for x in range(bx - hw - 2, bx + hw + 3):            # 牙龈
            put(a, x, 0, FL['gum'])
            put(a, x, 1, sh(FL['gum'], 1.2))
    return a


# ============================================================ 变肉的范围（四档单调变大）
@lru_cache(maxsize=1)
def masks():
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    nz = A._fbm(PW, H, 16, 31) - 0.5
    nz2 = A._fbm(PW, H, 5, 37) - 0.5
    core = np.zeros((H, PW), bool)
    for (cx, cy, r) in CORES:
        d = np.hypot(xx - cx, (yy - cy) * 1.15)
        core |= d < r + 6.0 * nz2
    f = np.zeros((H, PW), np.float32)
    for (cx, cy, R) in REGIONS:
        d = np.hypot(xx - cx, (yy - cy) * 1.1)
        f = np.maximum(f, np.exp(-(d / R) ** 2))
    f = np.maximum(f, np.clip((100 - xx) / 50.0, 0, 1))
    f = np.maximum(f, np.clip((xx - 540) / 50.0, 0, 1))
    reg = (f + 0.5 * nz + 0.18 * nz2) > 0.5
    sx, sy = EYE_SEARCH
    reg &= np.hypot(xx - sx, yy - sy) > 26                      # 探照灯到最后一档才变
    wall = yy < FLOOR_T
    m33 = core & wall
    m66 = (core | reg) & wall
    m1 = wall.copy()
    return (np.zeros((H, PW), bool), m33, m66, m1)


def protected(x, y):
    """.33 / .66 的过渡效果（血管、鼓包、疙瘩）不碰：舱灯 strip 的框、三个底座。"""
    if in_boxes(x, y, LAMP_BOXES, pad=1):
        return True
    for (ex, ey) in EYES.values():
        if math.hypot(x - ex, y - ey) < 15:
            return True
    return False


@lru_cache(maxsize=4)
def surface(li):
    """第 li 档的墙面 albedo：钢铁 / 肉按 mask 合成，边上画鼓包、撕开的铁皮、爬出来的血管、变成疙瘩的铆钉。"""
    st = steel_surface()
    if li == 0:
        return st.copy()
    fl = flesh_surface()
    M = masks()[li]
    a = np.where(M[..., None], fl, st)
    if li == 3:
        return a
    prot = np.zeros((H, PW), bool)
    for (x0, y0, x1, y1) in LAMP_BOXES:
        prot[max(0, y0 - 1):y1 + 1, max(0, x0 - 1):x1 + 1] = True
    yy, xx = np.mgrid[0:H, 0:PW]
    for (ex, ey) in EYES.values():
        prot |= np.hypot(xx - ex, yy - ey) < 15
    dout = ndimage.distance_transform_edt(~M)
    din = ndimage.distance_transform_edt(M)
    # 鼓包：钢板在肉的外圈 2–8 px 被顶起来（左上亮、右下暗）
    blur = ndimage.gaussian_filter(M.astype(np.float32), 3.0)
    gy, gx = np.gradient(blur)
    lit = -(gx * -0.6 + gy * -0.8) * 9.0
    ring = (dout > 1) & (dout <= 8) & ~prot & (yy < FLOOR_T)
    k = np.where(lit > 0.12, 1.18, np.where(lit < -0.12, 0.8, 1.0))
    a = np.where(ring[..., None], a * k[..., None], a)
    # 肉从洞里鼓出来、压在铁皮上：右下方投一道影子；洞口的铁皮边往外卷（上 / 左亮，其余锈）
    shadow = np.roll(np.roll(M, 2, axis=0), 1, axis=1) & ~M & ~prot & (yy < FLOOR_T)
    a = np.where(shadow[..., None], a * 0.62, a)
    up = np.roll(M, 1, axis=0) | np.roll(M, 1, axis=1)
    edge_out = (dout == 1) & ~prot & (yy < FLOOR_T)
    a[edge_out & ~up] = STEEL_HI
    a[edge_out & up & ~shadow] = (92, 56, 42)
    # 肉的边：鼓起的唇（朝左上的一侧亮、朝右下的一侧暗）
    gy2, gx2 = np.gradient(din)
    face = (gx2 * -0.6 + gy2 * -0.8)                         # 边上的法线朝外 = 距离变小的方向
    lip = M & (din <= 2.5)
    a[lip & (face < -0.25)] = FL['hi']
    a[lip & (face > 0.25)] = FL['deep']
    a[lip & (din <= 1.2) & (np.abs(face) <= 0.25)] = FL['dark']
    # 附近的铆钉变疙瘩
    for (x, y) in rivets():
        dd = dout[y, x]
        if 0 < dd <= (14 if li == 1 else 10) and not prot[y, x]:
            put(a, x, y, FL['hi'])
            put(a, x + 1, y, FL['light'])
            put(a, x, y + 1, FL['base'])
            put(a, x + 1, y + 1, FL['dark'])
            if dd <= 7:
                put(a, x - 1, y, FL['light'])
                put(a, x, y - 1, FL['hi'])
                put(a, x + 2, y + 1, FL['deep'])
    # 爬出来的血管：从边上往外长
    by, bx = np.nonzero(edge_out)
    order = np.argsort(by * PW + bx)
    roots = []
    step = 7 if li == 1 else 11
    for j, idx in enumerate(order[::step]):
        x, y = int(bx[idx]), int(by[idx])
        m = M[max(0, y - 3):y + 4, max(0, x - 3):x + 4]
        cy, cx = np.argwhere(m).mean(0) if m.any() else (3, 3)
        ang = math.atan2(3 - cy, 3 - cx) + hrange(-0.5, 0.5, j, li, 91)
        roots.append((x, y, ang))
    length = (10, 28) if li == 1 else (10, 30)
    veins_on(a, roots, 40 + li, length,
             allow=lambda x, y: 0 <= y < FLOOR_T and 0 <= x < PW and not M[y, x] and not prot[y, x], trunk=False,
             col=(96, 40, 92), col_hi=(140, 80, 130))
    return a


# ============================================================ 物件（albedo 部分；发光的部分打光以后再画）
def lamp_housing(a, lx, eye=False):
    """舱灯：电缆管上下来一小截 + 接线盒 + 圆形灯座（灯泡、网罩打光以后画）。"""
    for y in (CONDUIT + 2, CONDUIT + 3):
        put(a, lx, y, (70, 74, 76))
        put(a, lx + 1, y, (104, 108, 110))
    for x in range(lx - 2, lx + 3):
        put(a, x, CONDUIT + 4, (96, 102, 104))
        put(a, x, CONDUIT + 5, (72, 78, 80))
    ring_shade(a, lx, LAMP_Y, 4.0, 6.2, [(44, 46, 48), (70, 72, 74), (104, 106, 108), (146, 148, 148)])


def porthole(a, cx, cy, mode):
    """舷窗。mode 'open'（玻璃透明，后面画）/ 'closed'（盖板封死）；肉档 'open_f' / 'closed_f'。"""
    flesh = mode.endswith('_f')
    if not flesh:
        ring_shade(a, cx, cy, 11.0, 14.6, BRASS)
        for k in range(8):
            ang = math.pi / 8 + k * math.pi / 4
            bx, by = int(round(cx + 12.8 * math.cos(ang))), int(round(cy + 12.8 * math.sin(ang)))
            put(a, bx, by, (66, 50, 28))
            put(a, bx - 1, by - 1, (232, 210, 140))
        ring_shade(a, cx, cy, 10.0, 11.0, [(40, 34, 24), (56, 46, 30), (70, 58, 38), (86, 72, 46)], inner_flip=False)
        for y in range(cy - 4, cy + 5):                      # 合页 + 压紧把手
            put(a, cx - 15, y, (110, 88, 50))
            put(a, cx - 16, y, (70, 54, 30))
        for x in range(cx + 14, cx + 18):
            put(a, x, cy - 1, (96, 76, 44))
            put(a, x, cy, (62, 48, 28))
    else:
        lid = [FL['deep'], FL['dark'], FL['base'], FL['hi']]
        ring_shade(a, cx, cy, 10.0, 14.6, lid)
        for x in range(cx - 15, cx + 16):                    # 眼皮的折痕
            dy = int(round(-math.sqrt(max(0.0, 15.5 ** 2 - (x - cx) ** 2))))
            put(a, x, cy + dy, FL['deep'])
            put(a, x, cy + dy + 1, FL['light'])
        ring_shade(a, cx, cy, 10.0, 11.0, [(110, 30, 60), (150, 44, 76), (190, 70, 100), (220, 110, 130)], inner_flip=False)
        for k in range(7):                                   # 睫毛
            ang = math.pi * (1.1 + 0.8 * k / 6)
            x0, y0 = cx + 14.5 * math.cos(ang), cy + 14.5 * math.sin(ang)
            for s in range(3):
                put(a, int(round(x0 + s * math.cos(ang))), int(round(y0 + s * math.sin(ang))), (40, 16, 34))
    if mode.startswith('closed'):
        if not flesh:
            for (x, y) in disc_pts(cx, cy, 11.0):
                nx, ny = (x - cx) / 11.0, (y - cy) / 11.0
                lv = -(nx * -0.6 + ny * -0.8)
                c = (110, 122, 120)
                put(a, x, y, sh(c, 1.0 + 0.16 * lv))
            for (x, y) in disc_pts(cx, cy, 3.0):
                put(a, x, y, (84, 94, 94))
            put(a, cx - 1, cy - 1, (150, 160, 158))
            for (dx, dy) in ((-8, 0), (8, 0), (0, -8), (0, 8)):
                for k in (-1, 0, 1):
                    put(a, cx + dx + (k if dy else 0), cy + dy + (k if dx else 0), (52, 56, 58))
                put(a, cx + dx, cy + dy, (140, 146, 146))
        else:
            for (x, y) in disc_pts(cx, cy, 11.0):
                put(a, x, y, FL['base'] if y < cy else FL['mid'])
            for x in range(cx - 9, cx + 10):                 # 闭着的眼缝 + 往下的睫毛
                yy = cy + int(round(1.5 * (1 - ((x - cx) / 9.0) ** 2)))
                put(a, x, yy, FL['deep'])
                put(a, x, yy - 1, FL['hi'])
            for k in range(5):
                x = cx - 6 + k * 3
                for s in range(1, 4):
                    put(a, x - (1 if k < 2 else 0) + (1 if k > 2 else 0) * (s // 2), cy + 2 + s, (40, 16, 34))


def searchlight(a, flesh):
    cx, cy = EYE_SEARCH
    if not flesh:
        for y in range(CEIL + 1, cy - 16):                   # 吊杆
            put(a, cx - 1, y, (118, 124, 128))
            put(a, cx, y, (84, 90, 94))
            put(a, cx + 1, y, (56, 60, 64))
        for x in range(cx - 16, cx + 17):                    # U 形叉架
            put(a, x, cy - 17, (124, 130, 134))
            put(a, x, cy - 16, (86, 92, 96))
            put(a, x, cy - 15, (56, 60, 64))
        for side in (-1, 1):
            xa = cx + side * 15
            for y in range(cy - 15, cy + 2):
                put(a, xa - 1, y, (120, 126, 130))
                put(a, xa, y, (84, 90, 94))
                put(a, xa + 1, y, (56, 60, 64))
            for (x, y) in disc_pts(xa, cy, 2.4):
                put(a, x, y, (70, 76, 80))
            put(a, xa - 1, cy - 1, (170, 176, 180))
        ring_shade(a, cx, cy, 11.5, 13.6, [(36, 38, 42), (58, 62, 66), (84, 88, 92), (122, 126, 130)])
        ring_shade(a, cx, cy, 10.0, 11.5, [(96, 100, 104), (136, 142, 146), (176, 182, 186), (222, 226, 228)])
        for k in range(9):                                   # 把手
            put(a, cx + 12 + k, cy + 8 + k // 2, (60, 64, 68))
            put(a, cx + 12 + k, cy + 7 + k // 2, (110, 116, 120))
        for k in range(14):                                  # 电线回到天花板
            put(a, cx + 6 + k // 3, cy - 18 - k, (40, 42, 46))
    else:
        for y in range(CEIL + 1, cy - 12):                   # 肉柄
            w = int(round(0.8 * math.sin(y / 3.0)))
            for j, c in enumerate((FL['hi'], FL['base'], FL['mid'], FL['dark'])):
                put(a, cx - 2 + j + w, y, c)
        for side in (-1, 1):                                 # 叉架 → 两根筋
            for y in range(cy - 16, cy + 2):
                xa = cx + side * (15 - int(round(2 * math.sin((y - cy + 16) / 18 * math.pi))))
                for j, c in enumerate(TENDON):
                    put(a, xa - 1 + j, y, c)
        ring_shade(a, cx, cy, 11.0, 14.2, [FL['deep'], FL['dark'], FL['base'], FL['hi']])
        ring_shade(a, cx, cy, 10.0, 11.0, [(110, 30, 60), (150, 44, 76), (190, 70, 100), (220, 110, 130)], inner_flip=False)
        veins_on(a, [(cx - 10, cy - 8, -2.4), (cx + 9, cy - 9, -0.7), (cx + 11, cy + 6, 0.5)], 77, (6, 12))


def radar(a, d_unused, flesh):
    cx, cy = EYE_RADAR
    x0, x1, y0, y1 = cx - 18, cx + 18, 38, 94
    body = (96, 110, 104)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = body
            if x == x0:
                c = (138, 152, 146)
            elif x == x1:
                c = (60, 70, 66)
            elif y == y0:
                c = (130, 144, 138)
            elif y == y1:
                c = (56, 64, 62)
            put(a, x, y, c)
    for y in range(y0 + 1, y0 + 8):                          # 屏幕上面的遮光罩
        for x in range(x0 + 2, x1 - 1):
            put(a, x, y, (70, 80, 76) if y < y0 + 7 else (44, 50, 48))
    pts, wdt = text_pts('RADAR')
    for (dx, dy) in pts:
        put(a, cx - wdt // 2 + dx, y0 + 2 + dy, (196, 206, 196))
    ring_shade(a, cx, cy, 10.0, 13.4, [(30, 34, 34), (48, 54, 54), (74, 82, 80), (110, 120, 116)])
    for i, kx in enumerate((cx - 10, cx, cx + 10)):          # 旋钮
        for (x, y) in disc_pts(kx, 81, 2.6):
            put(a, x, y, (40, 44, 44))
        put(a, kx - 1, 80, (130, 136, 134))
        put(a, kx, 79 + i % 2, (180, 186, 184))
    for y in range(86, 92, 2):                               # 散热缝
        for x in range(cx + 2, x1 - 2):
            put(a, x, y, (52, 60, 58))
    for side in (x0 - 2, x1 + 1):                            # 挂在墙上的角铁
        for y in (y0 + 6, y1 - 6):
            put(a, side, y, (60, 66, 66))
            put(a, side + 1, y, (60, 66, 66))
    for y in range(CONDUIT + 2, y0):                         # 电缆上到电缆管
        put(a, x1 - 4, y, (40, 42, 44))
        put(a, x1 - 3, y, (76, 80, 82))
    if flesh:
        # 肉从上面盖下来，把机箱包住（面板轮廓还看得出来）
        for y in range(y0 - 3, y1 + 3):
            for x in range(x0 - 3, x1 + 4):
                r = math.hypot(x - cx, y - cy)
                if r < 13.5:
                    continue
                edge = x in (x0 - 3, x1 + 3) or y in (y0 - 3, y1 + 2)
                top = y0 - 3 + int(round(2 * math.sin(x / 4.0)))
                if y < top:
                    continue
                c = a[y, x] * 0.35 + np.array(FL['base'], np.float32) * 0.65
                if edge or y == top:
                    c = FL['hi'] if y <= top + 1 else FL['deep']
                put(a, x, y, c)
        ring_shade(a, cx, cy, 10.0, 13.6, [FL['deep'], FL['dark'], FL['base'], FL['hi']])
        veins_on(a, [(x0, y0 + 10, 0.3), (x1, y0 + 20, 2.8), (cx - 6, y1, -1.4), (cx + 8, y1 - 2, -1.8)], 83, (8, 16))


def hoist(a, hx, hook_y):
    """链式吊葫芦：天花板吊耳 → 上钩 → 机身（红漆 + 齿轮盖）→ 起重链 → 吊钩；侧面挂一圈手拉链。"""
    for y in range(CEIL + 1, CEIL + 4):                      # 吊耳 + 卸扣
        put(a, hx, y, (80, 86, 90))
    put(a, hx - 1, CEIL + 3, (110, 116, 120))
    put(a, hx + 1, CEIL + 3, (60, 64, 68))
    for y in range(CEIL + 4, 19):
        put(a, hx, y, (150, 156, 160) if y % 2 else (90, 96, 100))
    bx0, by0, bx1, by1 = hx - 4, 19, hx + 4, 31
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            corner = (x in (bx0, bx1)) and (y in (by0, by1))
            if corner:
                continue
            c = (168, 66, 44)
            if x == bx0:
                c = (206, 104, 76)
            elif x >= bx1 - 1:
                c = (112, 40, 28)
            if y == by1:
                c = (90, 32, 24)
            put(a, x, y, c)
    for (x, y) in disc_pts(hx - 1, 25, 2.6):                 # 齿轮盖
        put(a, x, y, (118, 122, 126))
    put(a, hx - 2, 24, (180, 184, 188))
    put(a, hx + 2, 21, (230, 220, 180))                      # 铭牌
    for y in range(22, 29):                                  # 手拉链轮
        put(a, hx + 5, y, (60, 64, 68))
        put(a, hx + 6, y, (100, 104, 108))
    loop_y = hook_y + 14
    for y in range(28, loop_y):                              # 手拉链（一圈，两股）
        c = (150, 154, 158) if y % 2 else (78, 82, 86)
        put(a, hx + 6, y, c)
        put(a, hx + 9, y, (78, 82, 86) if y % 2 else (150, 154, 158))
    for x in range(hx + 6, hx + 10):
        put(a, x, loop_y, (120, 124, 128))
    for y in range(by1 + 1, hook_y - 6):                     # 起重链
        put(a, hx, y, (160, 164, 168) if y % 3 else (70, 74, 78))
        if y % 3 == 1:
            put(a, hx - 1, y, (96, 100, 104))
    for y in range(hook_y - 6, hook_y - 2):                  # 吊钩滑轮（黄色）
        for x in range(hx - 2, hx + 3):
            put(a, x, y, (204, 166, 56) if x < hx + 2 else (140, 108, 30))
    hook = [(0, 0), (0, 1), (0, 2), (-1, 3), (-2, 4), (-2, 5), (-1, 6), (0, 6), (1, 6), (2, 5), (2, 4)]
    for (dx, dy) in hook:
        put(a, hx + dx, hook_y - 2 + dy, (96, 100, 106))
    put(a, hx - 2, hook_y + 2, (170, 176, 182))
    put(a, hx + 2, hook_y + 2, (196, 200, 204))


def valve_wheel(a, cx, cy, col=(178, 44, 38)):
    hi, dk = sh(col, 1.3), sh(col, 0.6)
    for (x, y) in disc_pts(cx, cy, 4.6):
        r = math.hypot(x - cx, y - cy)
        if r >= 3.4:
            put(a, x, y, hi if (x - cx) + (y - cy) < 0 else dk)
    for k in range(-3, 4):
        put(a, cx + k, cy, col)
        put(a, cx, cy + k, col)
    put(a, cx, cy, (60, 60, 64))


def gauge(a, cx, cy, r=4.2, ang=-0.6):
    for (x, y) in disc_pts(cx, cy, r + 1):
        put(a, x, y, (40, 40, 44))
    for (x, y) in disc_pts(cx, cy, r):
        put(a, x, y, (222, 218, 202))
    for k in range(8):
        t = math.pi * (0.75 + 1.5 * k / 7)
        put(a, int(round(cx + (r - 0.8) * math.cos(t))), int(round(cy + (r - 0.8) * math.sin(t))), (70, 66, 60))
    for s in range(1, int(r)):
        put(a, int(round(cx + s * math.cos(ang))), int(round(cy + s * math.sin(ang))), (200, 30, 30))
    put(a, cx - 1, cy - 2, (250, 250, 244))


def wall_fixtures(a, li):
    """墙上的小东西：阀组手轮 + 压力表、配电箱、电话、灭火器、消防水带卷盘、警告牌。"""
    for i, x in enumerate((204, 222, 240)):
        valve_wheel(a, x, MANIFOLD_Y + 2, (178, 44, 38) if i != 1 else (60, 132, 76))
    for (x, y) in ((218, 66),):
        for k in range(212, x):
            put(a, k + 2, y, (150, 154, 156))
        gauge(a, x + 3, y)
    gauge(a, 232, 88, 3.4, -2.2)
    for y in range(92, MANIFOLD_Y):
        put(a, 232, y, (130, 134, 136))
    # 配电箱
    x0, y0, x1, y1 = 460, 58, 480, 88
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = (112, 122, 118)
            if x in (x0, x1) or y in (y0, y1):
                c = (66, 74, 72)
            elif x == x0 + 1 or y == y0 + 1:
                c = (150, 160, 156)
            put(a, x, y, c)
    for (dx, dy) in ((3, 2), (2, 3), (3, 3), (4, 3), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (0, 5), (1, 5), (2, 5),
                     (3, 5), (4, 5), (5, 5), (6, 5)):            # 黄色三角
        put(a, x0 + 6 + dx, y0 + 5 + dy, (226, 190, 60))
    put(a, x0 + 9, y0 + 8, (40, 36, 30))
    put(a, x0 + 9, y0 + 9, (40, 36, 30))
    for y in range(y0 + 20, y0 + 27, 2):
        for x in range(x0 + 4, x1 - 3):
            put(a, x, y, (70, 78, 76))
    for y in range(y0 + 12, y0 + 17):
        put(a, x1 - 3, y, (40, 44, 44))
    for y in range(CONDUIT + 2, y0):
        put(a, 470, y, (44, 48, 50))
        put(a, 471, y, (80, 86, 88))
    # 船用电话
    for y in range(64, 81):
        for x in range(484, 491):
            put(a, x, y, (64, 84, 72) if 485 <= x <= 489 and 65 <= y <= 79 else (40, 52, 44))
    for y in range(66, 77):
        put(a, 485, y, (24, 24, 28))
        put(a, 486, y, (40, 40, 46))
    for x in range(487, 490):
        put(a, x, 66, (180, 40, 40))
    for k, y in enumerate(range(77, 92)):
        put(a, 485 + (k % 3 == 1), y, (30, 30, 34))
    # 灭火器 + 红牌
    for y in range(86, 92):
        for x in range(57, 70):
            put(a, x, y, (176, 40, 36) if y not in (86, 91) else (120, 26, 24))
    stencil(a, 58, 87, 'FIRE', (240, 236, 230))
    for y in range(97, 116):
        for x in range(60, 66):
            c = [(214, 74, 64), (186, 48, 40), (170, 40, 34), (150, 34, 30), (126, 28, 24), (96, 20, 18)][x - 60]
            put(a, x, y, c)
    for x in range(60, 66):
        put(a, x, 96, (40, 40, 44))
    put(a, 62, 95, (150, 150, 156))
    put(a, 63, 95, (90, 90, 96))
    for k in range(6):
        put(a, 66 + k // 3, 97 + k, (30, 30, 34))
    for x in range(59, 67):
        put(a, x, 104, (50, 52, 56))
    # 消防水带卷盘（右边）
    cx, cy = 588, 108
    for (x, y) in disc_pts(cx, cy, 7.2):
        r = math.hypot(x - cx, y - cy)
        put(a, x, y, (186, 46, 40) if r >= 6 else (210, 196, 160) if int(r) % 2 else (176, 160, 126))
    for (x, y) in disc_pts(cx, cy, 2.0):
        put(a, x, y, (90, 30, 26))
    for y in range(cy + 7, cy + 12):
        put(a, cx, y, (70, 74, 76))
    # 吊钩警告牌（黄底黑三角）
    sx, sy = 326, 62
    for y in range(sy, sy + 11):
        for x in range(sx, sx + 13):
            put(a, x, y, (226, 194, 58) if 0 < x - sx < 12 and 0 < y - sy < 10 else (40, 38, 30))
    for k in range(5):
        for x in range(sx + 6 - k, sx + 7 + k):
            if k in (0, 4) or x in (sx + 6 - k, sx + 6 + k):
                put(a, x, sy + 3 + k, (36, 32, 26))
    put(a, sx + 6, sy + 5, (36, 32, 26))


def door(a, xa, xb, flesh):
    """水密门：门框（围板）+ 门扇 + 六个压紧把手 + 中间手轮 + 铁链挂锁 + 红牌 + 门框黄黑条。"""
    y0, y1 = DOOR_Y, JUNC
    for y in range(y0, y1):
        for x in range(xa, xb + 1):
            corner = (min(x - xa, xb - x) + min(y - y0, 99)) < 5
            if corner:
                continue
            c = (66, 74, 76)
            if x in (xa, xa + 1) or (y - y0) in (0, 1):
                c = (112, 104, 60) if ((y + x) // 3) % 2 else (44, 44, 42)
            if x in (xb, xb - 1):
                c = (92, 84, 48) if ((y + x) // 3) % 2 else (36, 36, 34)
            put(a, x, y, c)
    lx0, lx1, ly0, ly1 = xa + 4, xb - 4, y0 + 4, y1 - 5
    for y in range(ly0, ly1 + 1):
        for x in range(lx0, lx1 + 1):
            if (min(x - lx0, lx1 - x) + min(y - ly0, 99)) < 4:
                continue
            c = (112, 124, 122)
            if x == lx0 or y == ly0:
                c = (150, 162, 158)
            elif x == lx1 or y == ly1:
                c = (70, 78, 78)
            put(a, x, y, c)
    for y in range(y1 - 5, y1):                              # 门槛（围板下沿）
        for x in range(xa, xb + 1):
            put(a, x, y, (84, 92, 94) if y == y1 - 5 else (56, 62, 64))
    cxm = (xa + xb) // 2
    for y in (y0 + 14, y0 + 36, y0 + 58):                    # 压紧把手
        for x in (lx0 - 1, lx1 - 2):
            for k in range(4):
                put(a, x + k, y, (38, 40, 42))
            put(a, x + 1, y - 1, (140, 146, 148))
            put(a, x + 1, y + 1, (30, 32, 34))
    valve_wheel(a, cxm, y0 + 30, (54, 58, 62))
    for x in range(cxm - 7, cxm + 8):                        # 红牌 KEEP CLOSED（字太小，画成红白条）
        for y in range(y0 + 10, y0 + 15):
            put(a, x, y, (186, 40, 36) if y in (y0 + 10, y0 + 14) or x in (cxm - 7, cxm + 7) else (232, 226, 214))
        if (x - cxm) % 3 == 0:
            put(a, x, y0 + 12, (186, 40, 36))
    for k, x in enumerate(range(lx0, lx1 + 1)):              # 铁链（两个把手之间垂下来）+ 挂锁
        sag = int(round(5 * (1 - ((x - cxm) / max(1, (lx1 - lx0) / 2)) ** 2)))
        y = y0 + 36 + sag
        put(a, x, y, (150, 152, 156) if k % 2 else (70, 72, 76))
    for y in range(y0 + 41, y0 + 47):
        for x in range(cxm - 2, cxm + 3):
            put(a, x, y, (196, 160, 60) if x < cxm + 2 else (130, 100, 30))
    put(a, cxm - 1, y0 + 40, (110, 112, 116))
    put(a, cxm + 1, y0 + 40, (110, 112, 116))
    put(a, cxm, y0 + 44, (40, 30, 10))
    if flesh:
        for y in range(ly0, ly1 + 1):                        # 门扇上蒙了一层膜
            for x in range(lx0, lx1 + 1):
                if (min(x - lx0, lx1 - x) + min(y - ly0, 99)) < 4:
                    continue
                blend(a, x, y, FL['mid'], 0.42)
        for y in range(y0 - 2, y1 - 4):                      # 门框两边长出肉唇
            for side, x in ((-1, xa - 1), (1, xb + 1)):
                w = 1 + int(round(1.0 + math.sin(y / 5.0 + xa)))
                for k in range(w):
                    put(a, x - side * 0 + side * k, y, FL['hi'] if k == 0 else FL['base'])
                put(a, x + side * w, y, FL['deep'])
        veins_on(a, [(lx0 + 2, ly0 + 6, 0.9), (lx1 - 2, ly0 + 20, 2.2), (lx0 + 3, ly1 - 10, -0.5), (lx1 - 3, ly1 - 4, -2.6)],
                 50 + xa, (10, 20))


def beacon_housing(a, bx, by):
    for x in range(bx - 5, bx + 6):
        put(a, x, by + 3, (70, 74, 76))
        put(a, x, by + 4, (44, 46, 48))
    for (x, y) in disc_pts(bx, by + 2, 4.6):
        if y <= by + 2:
            put(a, x, y, (104, 28, 26) if x < bx + 2 else (74, 18, 18))
    put(a, bx - 2, by - 1, (156, 66, 60))
    for y in range(by - 2, by + 3):
        put(a, bx - 2, y, (50, 30, 30))
        put(a, bx + 2, y, (50, 30, 30))


# ---------------------------------------------------------------- 货（靠墙）
def crate(a, x0, y0, x1, y1, seed, wood=(116, 88, 58)):
    lt, dk, ink = sh(wood, 1.18), sh(wood, 0.74), sh(wood, 0.46)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = wood
            if (y - y0) % 5 == 4:
                c = dk
            if x in (x0, x1) or y in (y0, y1):
                c = ink
            elif x in (x0 + 1, x0 + 2) or y in (y0 + 1, y0 + 2):
                c = lt
            elif x in (x1 - 1, x1 - 2) or y in (y1 - 1, y1 - 2):
                c = dk
            put(a, x, y, c)
    n = min(x1 - x0, y1 - y0) - 6                            # 斜撑
    for k in range(n):
        x = x0 + 3 + int(k * (x1 - x0 - 6) / max(1, n))
        y = y1 - 3 - k * (y1 - y0 - 6) // max(1, n)
        put(a, x, y, lt)
        put(a, x + 1, y + 1, dk)
    for (x, y) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        put(a, x, y, (150, 152, 156))
    if hash01(seed, 1) < 0.7:                                 # 模板印：向上箭头 / 方框
        sx, sy = x0 + 4 + int(hrange(0, max(1, x1 - x0 - 14), seed, 2)), y0 + 5
        for k in range(4):
            put(a, sx + 2, sy + k, ink)
        put(a, sx + 1, sy + 1, ink)
        put(a, sx + 3, sy + 1, ink)
        for k in range(5):
            put(a, sx + 6 + k, sy, ink)
            put(a, sx + 6 + k, sy + 3, ink)


def drum(a, x0, y0, x1, y1, col, label=False):
    w = x1 - x0 + 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u = (x - x0) / max(1, w - 1)
            k = 1.25 if u < 0.15 else 1.1 if u < 0.35 else 1.0 if u < 0.6 else 0.82 if u < 0.85 else 0.62
            c = sh(col, k)
            if y == y0:
                c = sh(col, 1.35 if u < 0.6 else 1.0)
            if y in (y0 + (y1 - y0) // 3, y0 + 2 * (y1 - y0) // 3):
                c = sh(c, 1.22)
            if y in (y0 + (y1 - y0) // 3 + 1, y0 + 2 * (y1 - y0) // 3 + 1):
                c = sh(c, 0.7)
            put(a, x, y, c)
    put(a, x0, y0, sh(col, 0.5))
    put(a, x1, y0, sh(col, 0.5))
    if label:
        for y in range(y0 + 9, y0 + 14):
            for x in range(x0 + 3, x1 - 2):
                put(a, x, y, (214, 210, 196))
        put(a, x0 + 5, y0 + 11, (40, 40, 40))
        put(a, x0 + 6, y0 + 11, (200, 60, 40))


def cargo(a):
    crate(a, 46, 121, 71, 145, 1)
    crate(a, 72, 127, 95, 145, 2, (108, 82, 54))
    drum(a, 146, 123, 156, 145, (56, 78, 112), label=True)
    drum(a, 158, 124, 168, 145, (64, 86, 104))
    drum(a, 170, 136, 176, 145, (150, 120, 50))
    crate(a, 252, 111, 289, 145, 3, (124, 94, 62))
    # 盖帆布的一捆货 + 绳子
    for y in range(117, 146):
        for x in range(290, 331):
            top = 117 + int(round(3 * math.sin((x - 290) / 40 * math.pi) * -1 + 3 + 1.2 * math.sin(x / 3.0)))
            if y < top:
                continue
            u = (x - 290) / 40
            c = (90, 98, 74)
            if (x - 290) % 9 in (0, 1):
                c = (72, 78, 58) if (x - 290) % 9 == 0 else (106, 114, 88)
            if y == top:
                c = (122, 130, 102)
            if y > 141:
                c = sh(c, 0.82)
            put(a, x, y, sh(c, 1.05 - 0.12 * u))
    for x in range(290, 331):                                # 两道绳
        for yy in (124, 136):
            put(a, x, yy + int(round(math.sin(x / 2.0))), (176, 150, 96))
    drum(a, 386, 123, 396, 145, (130, 48, 40))
    drum(a, 398, 123, 408, 145, (148, 118, 50), label=True)
    for y in range(137, 146):                                # 铁桶（水桶）
        for x in range(412 + (145 - y) // 4, 422 - (145 - y) // 4):
            put(a, x, y, (130, 136, 138) if x < 418 else (92, 96, 98))
    for x in range(411, 424):
        put(a, x, 137 - int(round(3 * math.sin((x - 411) / 12 * math.pi))), (70, 74, 76))
    crate(a, 426, 130, 445, 145, 4, (112, 86, 56))
    crate(a, 500, 118, 527, 145, 5, (120, 90, 60))
    crate(a, 504, 106, 521, 117, 6, (110, 84, 56))
    for k in range(4):                                        # 绳卷
        for x in range(548, 569):
            t = (x - 558) / 10.5
            if abs(t) <= 1:
                yy = 141 - k * 2 + int(round(2.2 * math.sqrt(1 - t * t)))
                put(a, x, yy, (176, 150, 96) if (x + k) % 2 else (130, 108, 66))
                put(a, x, yy - 1, (196, 172, 118) if k == 3 else (150, 126, 82))
    for y in range(134, 146):                                # 工具箱
        for x in range(572, 591):
            put(a, x, y, (130, 52, 40) if y > 135 else (164, 74, 56))
    for x in range(578, 585):
        put(a, x, 132, (60, 62, 66))
    put(a, 578, 133, (60, 62, 66))
    put(a, 584, 133, (60, 62, 66))
    for x in range(572, 591):
        put(a, x, 139, (90, 34, 26))


def contact_shadows(a):
    """货和墙脚之间的接触阴影（先画）。"""
    for (x0, x1) in ((44, 98), (144, 179), (250, 333), (384, 447), (498, 530), (546, 592)):
        for x in range(x0, x1):
            for y in range(KICK, JUNC):
                mul(a, x, y, 0.78)


def engulf(a, box, seed, n=6):
    """被肉包住的边：沿框的边冒几个肉疙瘩 + 两根血管跨过去。"""
    x0, y0, x1, y1 = box
    per = [(x, y0) for x in range(x0, x1)] + [(x1, y) for y in range(y0, y1)] + [(x, y1) for x in range(x0, x1)] + \
          [(x0, y) for y in range(y0, y1)]
    for k in range(n):
        x, y = per[int(hash01(seed, k, 1) * len(per)) % len(per)]
        r = hrange(1.6, 3.4, seed, k, 2)
        for (qx, qy) in disc_pts(x, y, r):
            put(a, qx, qy, FL['base'] if qy > y - r * 0.4 else FL['hi'])
        put(a, int(x + r * 0.6), int(y + r * 0.6), FL['dark'])
    veins_on(a, [(x0, (y0 + y1) // 2, 0.2), (x1, y0 + 2, 2.7)], seed, (int((x1 - x0) * 0.6), int((x1 - x0) * 1.1)),
             trunk=False)


# ============================================================ 地板（四档一样）
@lru_cache(maxsize=1)
def floor_albedo():
    a = np.zeros((H - FLOOR_T, PW, 3), np.float32)
    base = np.array((92, 98, 98), np.float32)
    rows = list(range(FLOOR_T, H))
    for y in rows:
        a[y - FLOOR_T] = base * (0.86 if y < FLOOR_T + 1 else 0.93 if y < FLOOR_T + 3 else 1.0)
    # 防滑纹：一排排短斜条（“/” 和 “\” 交替，像花纹钢板），越往前越疏
    yy = FLOOR_T + 2
    j = 0
    while yy < H - 1:
        dx = 5 if yy < 158 else 6 if yy < 168 else 7
        for x in range(-8, PW + 8, dx):
            xx = x + (j % 2) * (dx // 2)
            if 155 <= yy <= 168 and hash01(xx, yy, 3) < 0.4:   # 中间走出来的磨亮带：纹磨平了一些
                continue
            hi, dk = (116, 122, 122), (70, 76, 76)
            if (xx // dx + j) % 2:
                put(a, xx + 1, yy - FLOOR_T, hi)
                put(a, xx, yy + 1 - FLOOR_T, dk)
            else:
                put(a, xx, yy - FLOOR_T, hi)
                put(a, xx + 1, yy + 1 - FLOOR_T, dk)
        yy += 3 if yy < 158 else 4 if yy < 168 else 5
        j += 1
    # 磨亮的走道
    for y in range(156, 169):
        a[y - FLOOR_T] = np.minimum(255, a[y - FLOOR_T] * 1.04)
    # 板缝 + 沉头螺栓
    for (y, off) in ((159, 40), (170, 100)):
        a[y - FLOOR_T] *= 0.66
        a[y + 1 - FLOOR_T] = np.minimum(255, a[y + 1 - FLOOR_T] * 1.12)
    for (ya, yb, off) in ((FLOOR_T, 158, 40), (161, 169, 100), (172, H - 1, 20)):
        for x in range(off, PW, 120):
            for y in range(ya, yb + 1):
                mul(a, x, y - FLOOR_T, 0.66)
                mul(a, x + 1, y - FLOOR_T, 1.1)
            for y in range(ya + 2, yb, 4):
                mul(a, x - 3, y - FLOOR_T, 0.72)
                mul(a, x + 4, y - FLOOR_T, 0.72)
    # 油渍、排水格栅
    for (ox, oy, rx, ry) in ((150, 166, 9, 2.5), (410, 158, 11, 2.5), (560, 173, 7, 2.0), (300, 152, 6, 1.5)):
        for y in range(int(oy - ry - 1), int(oy + ry + 2)):
            for x in range(int(ox - rx - 1), int(ox + rx + 2)):
                if ((x - ox) / rx) ** 2 + ((y - oy) / ry) ** 2 < 1 and 0 <= y - FLOOR_T < a.shape[0]:
                    mul(a, x, y - FLOOR_T, 0.8)
    for gx in (236, 520):
        for y in range(150, 154):
            for x in range(gx, gx + 13):
                put(a, x, y - FLOOR_T, (46, 50, 50) if (x - gx) % 2 == 0 or y in (150, 153) else (24, 26, 28))
        for x in range(gx, gx + 13):
            put(a, x, 154 - FLOOR_T, (116, 122, 122))
    for y in range(174, H):                                  # 最前面压暗
        a[y - FLOOR_T] *= 1.0 - 0.035 * (y - 173)
    return a


# ============================================================ 打光
def quant(L, n, bay):
    """光照分 n 档；只在档和档的交界抖一窄条（大片是平的，像手画的光）。"""
    return np.floor(L * n + 0.5 + (bay - 0.5) * 0.28) / n


@lru_cache(maxsize=2)
def light_mult(red):
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    s = np.zeros((H, PW), np.float32)
    for lx in LAMPS:
        d = np.hypot(xx - lx, (yy - LAMP_Y) * 0.62)
        s = s + np.clip(1 - d / 92.0, 0, 1) ** 1.6
    s = np.clip(s, 0, 1)
    bay = A._bayer(PW, H)
    amb = 0.46 + 0.16 * np.clip((yy - 60) / 80.0, 0, 1)       # 越往下越亮一点（地板反上来的光）
    q = quant(amb + 0.66 * s, 10, bay)
    if red:
        ca, cp = np.array((0.84, 0.70, 0.96), np.float32), np.array((1.26, 0.70, 0.76), np.float32)
    else:
        ca, cp = np.array((0.86, 0.96, 1.08), np.float32), np.array((1.12, 0.98, 0.76), np.float32)
    tint = ca[None, None, :] * (1 - s[..., None]) + cp[None, None, :] * s[..., None]
    m = q[..., None] * tint
    m[:CEIL + 1] *= 0.72
    m[CEIL + 1:STRINGER] *= 0.86
    m[(xx < 45) | (xx > 595)] *= 0.86
    # 地板：四档都用暖光（地板不进 pick）
    sf = np.zeros((H, PW), np.float32)
    for lx in LAMPS:
        d = np.hypot((xx - lx) * 0.85, (yy - FLOOR_T) * 2.6)
        sf = sf + np.clip(1 - d / 100.0, 0, 1) ** 1.4
    sf = np.clip(sf, 0, 1)
    qf = quant(0.74 + 0.36 * sf - 0.012 * np.clip(yy - 168, 0, 12), 10, bay)
    if red:                                                  # 红灯：地板只偏一点红，亮度和花纹不变（可走带照样看得清）
        ampf, poolf = np.array((0.96, 0.88, 0.98), np.float32), np.array((1.16, 0.88, 0.84), np.float32)
    else:
        ampf, poolf = np.array((0.90, 0.97, 1.05), np.float32), np.array((1.10, 0.99, 0.82), np.float32)
    tf = ampf[None, None, :] * (1 - sf[..., None]) + poolf[None, None, :] * sf[..., None]
    mf = qf[..., None] * tf
    m[FLOOR_T:] = mf[FLOOR_T:]
    return m


# ============================================================ 整档
def is_red(li):
    return li >= 2


@lru_cache(maxsize=4)
def albedo(li):
    """第 li 档（0..3）整张 albedo（RGBA，640×180；舷窗玻璃 alpha 0，后面画）。"""
    a3 = surface(li).copy()
    a3[FLOOR_T:] = floor_albedo()
    M = masks()[li]
    contact_shadows(a3)
    if li == 3:                                              # 最后一档：墙脚的肉往地板上伸几根细根
        for i in range(30):
            x = int(hrange(2, PW - 2, i, 101))
            L = int(hrange(1, 3.99, i, 102))
            for k in range(L):
                put(a3, x + (k if hash01(i, 103) < 0.5 else -k) // 2, FLOOR_T + k, FL['dark'] if k < L - 1 else FL['mid'])
    fl_at = lambda x, y: bool(M[min(H - 1, max(0, y)), min(PW - 1, max(0, x))])  # noqa: E731
    for lx in LAMPS:
        lamp_housing(a3, lx)
    for (cx, cy) in PORTS_CLOSED:
        porthole(a3, cx, cy, 'closed_f' if fl_at(cx, cy) else 'closed')
    porthole(a3, EYE_PORT[0], EYE_PORT[1], 'open_f' if fl_at(*EYE_PORT) else 'open')
    wall_fixtures(a3, li)
    for (hx, hy) in HOISTS:
        hoist(a3, hx, hy)
    for (bx, by) in BEACONS:
        beacon_housing(a3, bx, by)
    door(a3, 4, 36, fl_at(20, 110))
    door(a3, 604, 636, fl_at(620, 110))
    radar(a3, None, fl_at(*EYE_RADAR))
    searchlight(a3, fl_at(*EYE_SEARCH))
    cargo(a3)
    # 被肉包住的小东西
    boxes = [((458, 56, 482, 90), 1), ((483, 63, 492, 82), 2), ((56, 85, 70, 117), 3), ((580, 100, 596, 116), 4),
             ((324, 60, 340, 74), 5), ((198, 94, 250, 104), 6)]
    for (bx, s) in boxes:
        cx, cy = (bx[0] + bx[2]) // 2, (bx[1] + bx[3]) // 2
        if fl_at(cx, cy):
            engulf(a3, bx, 200 + s + li)
    if li >= 2:                                              # 货上爬了几根肉筋
        for i, (x, y, ang) in enumerate(((60, 121, -0.2), (262, 111, 0.1), (300, 119, 0.3), (512, 106, 0.0),
                                          (150, 123, 0.4), (430, 130, -0.1))):
            if li == 3 or fl_at(x, y - 6):
                veins_on(a3, [(x, y, ang)], 300 + i, (10, 18), col=FL['base'], col_hi=FL['hi'])
    out = rgba_full(a3)
    for (x, y) in disc_pts(EYE_PORT[0], EYE_PORT[1], GLASS_R):
        out[y, x, 3] = 0
    return out


@lru_cache(maxsize=4)
def lit(li):
    """打好光、画好灯罩外圈光和发光物（灯泡、灯芯除外），RGBA。"""
    a = albedo(li).copy()
    m = light_mult(is_red(li))
    op = a[..., 3] > 0
    a[..., :3] = np.where(op[..., None], np.clip(a[..., :3] * m, 0, 255), a[..., :3])
    a[..., :3] = np.where(op[..., None], np.maximum(a[..., :3], 8), a[..., :3])
    im = toimg(a)
    red = is_red(li)
    for lx in LAMPS:
        A._glow(im, lx, LAMP_Y, 24, 17, (255, 64, 76) if red else (255, 206, 130), 46 if red else 40, rings=3)
    # 雷达屏幕的绿光 + 屏幕
    A._glow(im, EYE_RADAR[0], EYE_RADAR[1], 17, 16, (90, 255, 150), 26, rings=2)
    d = ImageDraw.Draw(im)
    cx, cy = EYE_RADAR
    for (x, y) in disc_pts(cx, cy, GLASS_R):
        r = math.hypot(x - cx, y - cy)
        c = SCOPE_PAL[0]
        if r >= 8.6:
            c = SCOPE_PAL[3]
        elif abs(r - 3.5) < 0.5 or abs(r - 7.0) < 0.5:
            c = SCOPE_PAL[1]
        elif x == cx or y == cy:
            c = SCOPE_PAL[2]
        px(d, x, y, c)
    for (bx_, by_) in ((cx + 4, cy - 3), (cx - 6, cy + 4), (cx + 2, cy + 6)):
        px(d, bx_, by_, SCOPE_PAL[4])
    # 探照灯的灯面（不亮，反着光）
    sx, sy = EYE_SEARCH
    pal = lens_pal(li)
    for (x, y) in disc_pts(sx, sy, GLASS_R):
        r = math.hypot(x - sx, y - sy)
        c = pal[0]
        if int(r) in (2, 5, 8):
            c = pal[1]
        elif int(r) in (3, 6, 9):
            c = pal[2]
        if r < 1.5:
            c = pal[3]
        px(d, x, y, c)
    for k in range(5):
        px(d, sx - 6 + k, sy - 5 - (k // 2), pal[4])
    px(d, sx - 7, sy - 3, pal[4])
    # 舷窗玻璃：半透明的暗色 + 两道反光（后面的 static 层是海）
    ex_, ey_ = EYE_PORT
    gl = Image.new('RGBA', im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    for (x, y) in disc_pts(ex_, ey_, GLASS_R):
        gd.point((x, y), fill=(24, 40, 58, 70))
    for k in range(6):
        gd.point((ex_ - 6 + k, ey_ - 2 - k), fill=(220, 236, 246, 150))
    gd.point((ex_ + 4, ey_ + 4), fill=(220, 236, 246, 120))
    ga = np.array(gl)
    ia = np.array(im)
    msk = ga[..., 3] > 0
    ia[msk] = ga[msk]
    im = Image.fromarray(ia, 'RGBA')
    # 配电箱 / 雷达上的小指示灯
    d = ImageDraw.Draw(im)
    for (x, y, c) in ((474, 62, (110, 255, 140)), (476, 62, (255, 180, 60)), (548, 88, (255, 186, 60)),
                      (551, 88, (110, 255, 140))):
        px(d, x, y, c)
    return im


def lamp_k(i, f):
    """第 i 盏灯第 f 帧的亮度（24 帧一圈）。294 那盏（i = 2）接触不良。"""
    k = 0.92 + 0.08 * (0.5 + 0.5 * math.sin(2 * math.pi * f / N_FR * (2 + i % 3) + i * 1.7))
    if i == 2 and f in (7, 8, 15):
        k *= 0.45
    return k


def draw_lamps(im, li, ks):
    """灯泡 + 内圈光 + 网罩。li ≥ 2：发红光的“眼睛”。"""
    d = ImageDraw.Draw(im)
    red = is_red(li)
    for i, lx in enumerate(LAMPS):
        k = 1.0 if red else ks[i]
        A._glow(im, lx, LAMP_Y, 9, 8, (255, 70, 80) if red else (255, 222, 150), int((96 if red else 84) * k), rings=2)
        d = ImageDraw.Draw(im)
        for (x, y) in disc_pts(lx, LAMP_Y, 4.0):
            r = math.hypot(x - lx, y - LAMP_Y)
            if red:
                c = (255, 136, 126) if r < 1.6 else (234, 46, 64) if r < 2.8 else (156, 20, 42)
            else:
                c = (255, 248, 222) if r < 1.6 else (255, 226, 150) if r < 2.8 else (232, 186, 110)
                c = mix((112, 96, 70), c, k)
            px(d, x, y, c)
        if red:
            for y in range(LAMP_Y - 2, LAMP_Y + 3):          # 竖着的瞳孔
                px(d, lx, y, (64, 0, 22))
            px(d, lx - 1, LAMP_Y - 2, (255, 222, 220))
        for y in range(LAMP_Y - 3, LAMP_Y + 4):              # 网罩
            px(d, lx - 2, y, (64, 60, 54))
            px(d, lx + 2, y, (64, 60, 54))
        px(d, lx - 1, LAMP_Y + 4, (64, 60, 54))
        px(d, lx + 1, LAMP_Y + 4, (64, 60, 54))
    return im


@lru_cache(maxsize=8)
def render(li, f=None):
    """第 li 档、舱灯第 f 帧（None = 全亮）的整张（640×180 RGBA）。"""
    ks = [1.0] * len(LAMPS) if f is None else [lamp_k(i, f) for i in range(len(LAMPS))]
    im = draw_lamps(lit(li).copy(), li, ks)
    return im


@lru_cache(maxsize=4)
def overlay(li):
    """pick 的第 li 张（640×180）：和第 0 档不一样的像素；舱灯框只要动了一个像素就整框盖上。"""
    base = np.array(render(0))[:PH]
    cur = np.array(render(li))[:PH]
    diff = (base != cur).any(-1)
    for (x0, y0, x1, y1) in LAMP_BOXES:
        if diff[y0:y1, x0:x1].any():
            diff[y0:y1, x0:x1] = True
    out = np.zeros_like(cur)
    out[diff] = cur[diff]
    return Image.fromarray(out, 'RGBA')


# ============================================================ 会动的（strip）
def lamp_frame(t):
    f = int(math.floor(t * FPS + 1e-6)) % N_FR
    return render(0, f)


def steam_frame(t):
    im = Image.new('RGBA', (PW, H), (0, 0, 0, 0))
    u0 = (t % 2.0) / 2.0
    for (vx, vy, rise, drift, n, seed) in ((VENT1[0] + 1, VENT1[1] - 1, 34, -6, 4, 1), (VENT2[0], VENT2[1], 15, 14, 3, 2)):
        for i in range(n):
            u = (u0 + i / n + hash01(seed, i) * 0.05) % 1.0
            cx = vx + drift * u + 1.5 * math.sin(u * 6.3 + i)
            cy = vy - rise * u
            r = 1.2 + 4.2 * u
            al = int(150 * (1 - u) ** 1.2)
            if al < 10:
                continue
            lay = Image.new('RGBA', (PW, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ld.ellipse((cx - r, cy - r * 0.8, cx + r, cy + r * 0.8), fill=(224, 228, 232, al // 2))
            ld.ellipse((cx - r * 0.55, cy - r * 0.5, cx + r * 0.5, cy + r * 0.4), fill=(240, 242, 244, al))
            im.alpha_composite(lay)
    return im


@lru_cache(maxsize=1)
def steam_boxes():
    """两处漏汽 24 帧里实际画到的范围（各自一个框，帧条不切掉烟）。"""
    acc = np.zeros((H, PW), bool)
    for f in range(N_FR):
        acc |= np.array(steam_frame(f / FPS))[..., 3] > 0
    out = []
    for (x0, y0, x1, y1) in (V1_REGION, V2_REGION):
        ys, xs = np.nonzero(acc[y0:y1, x0:x1])
        out.append((x0 + int(xs.min()), y0 + int(ys.min()), x0 + int(xs.max()) + 1, y0 + int(ys.max()) + 1))
    return tuple(out)


def radar_frame(t):
    im = Image.new('RGBA', (PW, H), (0, 0, 0, 0))
    cx, cy = EYE_RADAR
    th = 2 * math.pi * ((t % 2.0) / 2.0) - math.pi / 2
    a = np.zeros((H, PW, 4), np.uint8)
    for (x, y) in disc_pts(cx, cy, GLASS_R - 0.6):
        dx, dy = x - cx, y - cy
        if dx == 0 and dy == 0:
            continue
        ang = math.atan2(dy, dx)
        lag = (th - ang) % (2 * math.pi)                     # 扫描线后面拖的余辉
        if lag < 0.22:
            a[y, x] = (150, 255, 180, 230)
        elif lag < 0.9:
            a[y, x] = (70, 210, 120, int(150 * (1 - lag / 0.9)) + 20)
    for (bx_, by_) in ((cx + 4, cy - 3), (cx - 6, cy + 4), (cx + 2, cy + 6)):
        lag = (th - math.atan2(by_ - cy, bx_ - cx)) % (2 * math.pi)
        if lag < 1.6:
            a[by_, bx_] = (200, 255, 210, 255)
    a[cy, cx] = (170, 255, 200, 255)
    return Image.fromarray(a, 'RGBA')


def beacon_frame(t):
    im = Image.new('RGBA', (PW, H), (0, 0, 0, 0))
    ph = (t % 1.0)
    for (bx, by) in BEACONS:
        lay = Image.new('RGBA', (PW, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        s = math.cos(2 * math.pi * ph)
        side = 1 if math.sin(2 * math.pi * ph) > 0 else -1
        L = int(14 * abs(s)) + 4
        al = int(70 * abs(s)) + 20
        ld.polygon([(bx, by), (bx + side * L, by - 9), (bx + side * L, by + 13)], fill=(255, 60, 40, al))
        im.alpha_composite(lay)
        A._glow(im, bx, by + 1, 11, 9, (255, 60, 40), 90, rings=3)
        d = ImageDraw.Draw(im)
        for (x, y) in disc_pts(bx, by + 2, 4.6):
            if y <= by + 2:
                px(d, x, y, (255, 90, 70) if abs(x - (bx + int(round(3 * s)))) <= 1 else (230, 40, 36))
        px(d, bx - 2, by - 1, (255, 220, 200))
    return im


# ============================================================ 舷窗外的海 / 前景
@lru_cache(maxsize=1)
def sea_img():
    im = Image.new('RGBA', (W, SEA_H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    hz = 72 - SEA_Y
    for y in range(SEA_H):
        if y < hz:
            c = mix((34, 44, 64), (78, 92, 112), (y / hz) ** 1.6)
        else:
            c = mix((40, 52, 72), (16, 22, 36), ((y - hz) / (SEA_H - hz)) ** 0.7)
        d.line((0, y, W, y), fill=C(c))
    d.line((0, hz, W, hz), fill=C((110, 122, 138)))
    for i in range(40):
        x, y = int(hrange(0, W, i, 1)), int(hrange(hz + 2, SEA_H - 1, i, 2))
        L = int(hrange(2, 5, i, 3))
        d.line((x, y, x + L, y), fill=C((52, 66, 88)))
    for i in range(9):                                       # 雾团
        x, y = hrange(0, W, i, 5), hrange(2, hz - 2, i, 6)
        d.line((x, y, x + hrange(8, 20, i, 7), y), fill=C((88, 100, 118)))
    return im


@lru_cache(maxsize=4)
def fg_img(li):
    im = Image.new('RGBA', (FGW, H), (0, 0, 0, 0))
    a = np.zeros((H, FGW, 4), np.float32)
    red = is_red(li)
    for i, fx in enumerate(FG_X):
        if li == 3:
            pal = [(150, 76, 110), (106, 46, 82), (74, 30, 60), (48, 20, 40)]
        elif red:
            pal = [(132, 74, 92), (82, 52, 66), (56, 38, 50), (38, 28, 36)]
        else:
            pal = [(112, 122, 128), (70, 78, 84), (48, 54, 60), (32, 36, 42)]
        for y in range(H):
            w = int(round(0.7 * math.sin(y / 6.0 + i))) if li == 3 else 0
            for j, c in enumerate(pal):
                a[y, fx + j + w, :3] = c
                a[y, fx + j + w, 3] = 255
        for by in (20, 166):                                 # 管卡
            for x in range(fx - 1, fx + 5):
                for y, k in ((by, 1.0), (by + 1, 0.7)):
                    a[y, x, :3] = sh((96, 44, 76) if li == 3 else (78, 52, 64) if red else (82, 90, 96), k)
                    a[y, x, 3] = 255
        if li == 3:
            for y in range(8, H - 6, 23):                    # 筋腱上的结
                for (dx, dy) in ((-1, 0), (4, 0), (-1, 1), (4, 1), (0, 2), (3, 2)):
                    a[y + dy, fx + dx, :3] = (110, 52, 86)
                    a[y + dy, fx + dx, 3] = 255
        elif li == 2:
            for y in range(4, H - 4):                        # 缠上去的肉筋（螺旋）
                ph = (y + i * 7) % 12
                if ph < 4:
                    x = fx - 1 + ph + (1 if ph >= 2 else 0)
                    a[y, x, :3] = (150, 70, 104) if ph < 2 else (110, 48, 80)
                    a[y, x, 3] = 255
    return toimg(a)


# ============================================================ 导出
def anchors():
    return dict(eye_porthole=list(EYE_PORT), eye_searchlight=list(EYE_SEARCH), eye_radar=list(EYE_RADAR),
                door_left=[4, DOOR_Y, 36, JUNC], door_right=[604, DOOR_Y, 636, JUNC],
                lamps=[[lx, LAMP_Y] for lx in LAMPS], hoists=[[hx, hy] for hx, hy in HOISTS],
                vents=[list(VENT1), list(VENT2)], manifold=[194, 88, 250, 104], radar=[542, 38, 578, 94],
                cargo=[[46, 121, 95, 145], [146, 123, 176, 145], [252, 111, 330, 145], [386, 123, 445, 145],
                       [500, 106, 527, 145], [548, 132, 590, 145]],
                walk_x=[8, 632])


def direct(camX, t, li, fg=True):
    """不经导出层，直接拼一帧（自检用）：海 → 第 li 档整张（灯 < .66 时按 t 闪）→ 漏汽 / 雷达 → 前景。"""
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(sea_img(), (0, SEA_Y))
    f = int(math.floor(t * FPS + 1e-6)) % N_FR
    full = render(li, f)
    out.alpha_composite(full.crop((camX, 0, camX + W, H)))
    for fn in (steam_frame, radar_frame):                      # strip 播的是第 floor(t·fps) 帧
        out.alpha_composite(fn(f / FPS).crop((camX, 0, camX + W, H)))
    if fg:
        o = int(math.floor(camX * FG_K))
        out.alpha_composite(fg_img(li).crop((o, 0, o + W, H)))
    return out


def export(ex, BJ):
    layers = [dict(type='static', image=ex.img('sea', sea_img()), x=0, y=SEA_Y),
              dict(type='pano', image=ex.img('hold', render(0)), k=1.0, x=0, y=0)]
    for i, box in enumerate(LAMP_BOXES):
        layers.append(ex.bake('lamp%d' % i, box, N_FR, FPS, lamp_frame, screen=False, k=1.0))
    ovs = [ex.img('flesh%d' % i, overlay(i)) for i in range(4)]
    layers.append(dict(type='pick', images=ovs, key='flesh', values=list(LEVELS), x=0, y=0, k=1.0))
    v1, v2 = steam_boxes()
    layers.append(ex.bake('steam_valve', v1, N_FR, FPS, steam_frame, screen=False, k=1.0))
    layers.append(ex.bake('steam_pipe', v2, N_FR, FPS, steam_frame, screen=False, k=1.0))
    layers.append(ex.bake('radar_sweep', RADAR_BOX, N_FR, FPS, radar_frame, screen=False, k=1.0))
    for i, box in enumerate(BEACON_BOXES):
        layers.append(ex.bake('alarm%d' % i, box, N_FR, FPS, beacon_frame, screen=False, k=1.0, key='alarm'))
    layers.append(dict(type='tint', color='#ff2a22', alpha=0.16, key='alarm'))
    fgs = [ex.img('fg%d' % i, fg_img(i)) for i in range(4)]
    fgl = [dict(type='pick', images=fgs, key='flesh', values=list(LEVELS), x=0, y=0, k=FG_K)]
    st = ex.stage(PW, GROUND, WALK, layers, fgl, anchors())
    if ex.check_on:
        checks(ex, BJ, st)
    return st


def checks(ex, BJ, st):
    imgs = ex.images
    # 1 底图：除了舷窗玻璃都不透明
    base = np.array(render(0))
    glass = np.zeros((H, PW), bool)
    for (x, y) in disc_pts(EYE_PORT[0], EYE_PORT[1], GLASS_R):
        glass[y, x] = True
    ex.checked('底图不透明（舷窗玻璃除外）', int(((base[..., 3] != 255) & ~glass).sum()))
    # 2 各镜头、四档整屏不露黑（含前景、所有 strip）
    bad = 0
    for camX in (0, 64, 120, 200, 260, 320):
        for v in LEVELS:
            im = np.array(BJ.ref_render(st, imgs, camX, 0.75, {'flesh': v}).convert('RGB'))
            bad += int((im.sum(-1) == 0).sum())
    ex.checked('镜头 0…320 × 四档 整屏都有画（不露黑）', bad)
    # 3 导出层 vs 直接拼（四档 × 几个镜头 / 时刻）
    for li, v in enumerate(LEVELS):
        for camX, t in ((0, 0.0), (160, 0.6), (320, 1.25)):
            got = BJ.ref_render(st, imgs, camX, t, {'flesh': v})
            ex.checked('flesh %.2f camX %d t %.2f 导出 vs 直接拼' % (v, camX, t), BJ.ndiff(got, direct(camX, t, li)))
    # 4 strip 2 s 闭合
    for name, fn, box in ([('lamp%d' % i, lamp_frame, b) for i, b in enumerate(LAMP_BOXES)] +
                          [('steam_valve', steam_frame, steam_boxes()[0]), ('steam_pipe', steam_frame, steam_boxes()[1]),
                           ('radar_sweep', radar_frame, RADAR_BOX)] +
                          [('alarm%d' % i, beacon_frame, b) for i, b in enumerate(BEACON_BOXES)]):
        ex.checked('%s 2 s 闭合' % name, BJ.ndiff_rgba(fn(0.0).crop(box), fn(2.0).crop(box)))
    # 5 pick 四张尺寸一致
    for L in st['layers'] + st['fg']:
        if L['type'] == 'pick':
            sizes = {imgs[k].size for k in L['images']}
            ex.checked('pick %s（k %.1f）四张尺寸一致 %s' % (L['key'], L.get('k', 0), sorted(sizes)), len(sizes) - 1)
    # 6 三只眼睛的锚点在四档里都落在底座上
    for li, v in enumerate(LEVELS):
        bad = 0
        for name, (ex_, ey_) in EYES.items():
            camX = min(PW - W, max(0, ex_ - 160))
            im = BJ.ref_render(st, imgs, camX, 0.0, {'flesh': v}, fg=False, only={'static', 'pano', 'pick'})
            a = np.array(im.convert('RGB')).astype(int)
            foot = [(x, y) for x in range(ex_ - 9, ex_ + 10) for y in range(ey_ - 8, ey_ + 6)
                    if ((x - ex_) / 9.5) ** 2 + ((y - ey_) / 5.5) ** 2 <= 1 or (abs(x - ex_) <= 5 and ey_ - 8 <= y < ey_)]
            if name == 'eye_porthole':                       # 玻璃：底图 + 这一档的 pick 叠起来仍然是半透明的
                pa = np.array(imgs[[L for L in st['layers'] if L['type'] == 'pano'][0]['image']])[..., 3]
                pk = [L for L in st['layers'] if L['type'] == 'pick'][0]
                oa = np.array(imgs[pk['images'][li]])[..., 3]
                for (x, y) in foot:
                    bad += int(math.hypot(x - ex_, y - ey_) >= GLASS_R or pa[y, x] >= 255 or oa[y, x] > 0)
            else:
                pal = SCOPE_PAL if name == 'eye_radar' else lens_pal(li)
                ps = {tuple(p) for p in pal}
                for (x, y) in foot:
                    bad += tuple(a[y, x - camX]) not in ps
        ex.checked('flesh %.2f 三只眼睛的脚印都落在玻璃 / 灯面 / 屏幕上（不符的像素）' % v, bad)
    # 6b 前景竖管：站在眼睛正下方时（镜头 = clamp(x − 160)）不挡眼睛（四档都查）
    bad = 0
    for li in range(4):
        fga = np.array(fg_img(li))[..., 3]
        for (ex_, ey_) in EYES.values():
            camX = min(PW - W, max(0, ex_ - 160))
            o = int(math.floor(camX * FG_K))
            sx = ex_ - camX
            bad += int((fga[ey_ - 9:ey_ + 7, o + sx - 12:o + sx + 13] > 0).sum())
    ex.checked('前景竖管不挡三只眼睛（站在眼睛下面时的镜头）', bad)
    # 7 可走带（y 148–176）：四档的地板花纹、明暗都和铁皮档一样（.66 / 1 只是被红灯照得偏红）
    #   亮度（Y）差的平均 ≤ 8；“哪里有花纹边”（|ΔY| > 6 的横向边）对不上的像素 ≤ 3%
    def luma(im):
        a = np.asarray(im.convert('RGB'), np.float32)
        return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    for li, v in enumerate(LEVELS[1:], 1):
        dy = mism = n = 0
        for camX in (0, 160, 320):
            y0 = luma(BJ.ref_render(st, imgs, camX, 0.0, {'flesh': 0}, fg=False))[148:177]
            y1 = luma(BJ.ref_render(st, imgs, camX, 0.0, {'flesh': v}, fg=False))[148:177]
            dy += float(np.abs(y0 - y1).mean()) / 3
            e0, e1 = np.abs(np.diff(y0, axis=1)) > 6, np.abs(np.diff(y1, axis=1)) > 6
            mism += int((e0 != e1).sum())
            n += e0.size
        ex.checked('flesh %.2f 可走带 y 148–176 亮度差平均（×10）' % v, int(round(dy * 10)), limit=80)
        ex.checked('flesh %.2f 可走带 y 148–176 地板花纹对不上的像素（≤ 3%%）' % v, mism, limit=int(0.03 * n))


# ============================================================ 单独预览
if __name__ == '__main__':
    out_dir = os.path.join(HERE, '_preview', 'ch2')
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for li in range(4):
        tiles = [direct(cx, 0.5, li) for cx in (0, 160, 320)]
        row = Image.new('RGB', (W * 3 + 8, H), (16, 16, 20))
        for i, t in enumerate(tiles):
            row.paste(t.convert('RGB'), (i * (W + 4), 0))
        rows.append(row)
    sheet = Image.new('RGB', (rows[0].width, (H + 4) * 4), (16, 16, 20))
    for i, r in enumerate(rows):
        sheet.paste(r, (0, i * (H + 4)))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(os.path.join(out_dir, 'freighter_corridor_solo.png'))
    print('ok', out_dir)
