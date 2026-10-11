# -*- coding: utf-8 -*-
r"""freighter_deck —— 无人货轮的甲板（第2章：漂了一夜，早上登上一艘空无一人的大货轮——它其实是猩猩的替身「力量」）。

2026-10-10 晚 第2章按体验版精度重画（改前：later_stages 里 320 宽的 A._freighter_static + 一条海面波纹）。
侧视、甲板高度平视；地图 640 宽、ground 156、可走带 y 146–172。阴天晨雾，光线偏冷偏灰；锈、雾、安静，还没长肉。
从左到右（世界坐标）：
  x 0–60     远侧舷墙的缺口 + 舷梯顶（两根栏杆柱、扶手绳、吊舷梯的小吊杆）；缆桩上系着他们那条救生艇的缆绳
  x 60–80    前桅（横桁、桅灯、雷达反射器、拉索）
  x 80–150   餐厅（厨房）甲板室：钢门虚掩（门缝漏出暖光）、起雾的小窗、GALLEY 牌、救生圈、菜筐、水桶拖把、
             屋顶的烟道帽和通风筒——烟道和门缝冒热气（strip）
  x 150–198  系泊绞盘（钢缆卷筒、绞缆头、刹车手轮、电机）+ 一盘缆绳
  x 196–270  大铁笼：后壁 / 顶上的栏 / 右侧面 / 地板（稻草、报纸、铁碗、香蕉皮）画在甲板层；
             正面铁栏是 pick（key cage_open：0 关着、1 门开着），剧情另用同一张图当 depth 道具画在猩猩前面
  x 268–304  油桶、喇叭口通风筒
  x 304–452  货舱口（围板 + 舱盖）、集装箱（左两层、右一层）、吊车立柱；
             吊车上半截（回转房 + 吊臂 + 钢缆 + 吊钩）是 pick（key crane：0 吊臂朝左、吊钩挂在铁笼上空；
             1 转到朝右、吊钩挂在货舱门上空）
  x 452–500  通往货舱的门（小门楼，门敞着、里面黑，看得见往下的楼梯），旁边消防栓、缆桩
  x 516–640  上层建筑（单独一层，盖在吊臂前面）：主甲板两扇门——左边舰桥门（敞着，里面是上楼的梯子）、
             右边办公室门（敞着，灯下的台子上摊着航海日志）；救生艇 + 吊艇架、驾驶台一排窗、驾驶台翼、
             雷达（转，strip）、天线、烟囱
远景（pano k 0.35）：阴天、雾里的淡太阳、平静的海、雾里隐约的岛。雾三层（wrap，横向首尾相接，慢慢往左飘）：
  海平线上一条（k 0.45）、甲板上一层薄的（k 1，压低可走带后面的对比）、高处一层（k 0.7，笼住吊车 / 驾驶台的上半截）。
前景（fg）：近侧一道矮栏杆（扶手 y 161，只挡可走带前半的脚和小腿）+ 两只低缆桩。
笼子“夹住”角色：猩猩（strength，脚底锚点）站 anchors.cage_inside；剧情加一个道具
  {type:'image', image: anchors.cage_front.images[cage_open], x: anchors.cage_front.x, y: anchors.cage_front.y,
   depth: anchors.cage_front.depth}，它和背景里的 pick 是同一张图——猩猩在它后面、可走带上的人在它前面。
单独运行：python -B tools\bg_new\freighter_deck.py → tools\bg_new\_preview\ch2\after\freighter_deck_*.png
  （world 整条 / cage 笼子夹人 / crane 吊车两个角度 / anchors 锚点）
"""
import sys
sys.dont_write_bytecode = True

import io  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
GAME = os.path.dirname(TOOLS)
SRC = os.path.join(os.path.dirname(GAME), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import gradient, hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402

W, H = 320, 180
PW = 640                       # 地图宽
FARW, FAR_K = 448, 0.35        # 远景：镜头 0…320 → 偏移 0…112
GROUND = 156
BAND = (146, 172)              # 可走带（脚底 y）
WALK_X = (10, 630)
HZ = 100                       # 海平线
BW_TOP, BW_BASE = 117, 134     # 远侧舷墙：顶（扶手）/ 底（甲板远边）
GAP = (18, 44)                 # 舷墙缺口（舷梯）
C = A._c4

# 各样东西的位置（世界坐标）
GALLEY = (80, 94, 150, 140)            # 甲板室墙面（x0, y顶, x1, y底）
G_DOOR = (102, 103, 118, 140)          # 餐厅门
G_WIN = (125, 105, 145, 119)           # 起雾的小窗
STACK_X = 136                          # 烟道帽中心
CAGE_F = (198, 92, 262, 146)           # 铁笼正面（左, 顶, 右, 底）
CAGE_D = (6, -9)                       # 后壁相对正面的偏移
CAGE_DOOR = (222, 98, 242, 143)        # 笼门（正面里）
CAGE_BOX = (190, 82, 270, 151)         # 笼门 pick 图的范围（含开门时往外甩的门扇）
CAGE_INSIDE = (232, 140)               # 猩猩脚底
CAGE_DEPTH = 144.5                     # 正面铁栏道具的纵深（猩猩 140 < 它 < 可走带 146）
HATCH = (304, 452)                     # 货舱口
PED_X = 378                            # 吊车立柱中心
CRANE_BOX = (254, 0, 492, 90)          # 吊车 pick 图的范围
BOOTH = (456, 94, 498, 142)            # 货舱门的小门楼
H_DOOR = (466, 104, 484, 142)          # 货舱门洞
SUP_X0 = 516                           # 上层建筑从这里开始
B_DOOR = (552, 106, 570, 142)          # 舰桥门
L_DOOR = (598, 106, 624, 142)          # 办公室门（航海日志）
STEAM_BOX = (106, 28, 156, 112)
STEAM_N, STEAM_FPS = 16, 8.0           # 2 s 一圈
RADAR_BOX = (548, 2, 574, 16)
RADAR_X, RADAR_Y = 561, 9
RADAR_N, RADAR_FPS = 16, 8.0           # 2 s 转一圈
SUN = (196, 30)                        # 远景里的太阳

# ---------------------------------------------------------------- 调色（阴天晨雾：冷、灰、低饱和）
FOG = (212, 217, 219)
SKY0, SKY1, SKY2 = (138, 149, 161), (170, 179, 186), (202, 207, 208)
SEA0, SEA1, SEA2 = (168, 177, 181), (126, 141, 148), (98, 114, 124)
DECK_F, DECK_N = (118, 98, 90), (104, 82, 74)       # 红丹甲板漆（旧、发灰）：远 / 近
RUST, RUST_D, RUST_L = (138, 84, 58), (94, 60, 48), (164, 108, 76)
BARE = (110, 106, 104)                              # 磨掉漆的钢
WHITE, WHITE_D, WHITE_L = (192, 194, 188), (156, 158, 154), (214, 216, 210)
BULW = (170, 172, 166)                              # 舷墙内侧
EQ = (94, 108, 100)                                 # 设备的灰绿漆
EQ_D, EQ_L = (64, 76, 70), (128, 142, 132)
YEL, YEL_D, YEL_L = (198, 164, 70), (144, 112, 46), (226, 200, 120)
INK = (40, 38, 40)
HAZ_Y, HAZ_K = (206, 172, 60), (44, 42, 44)
ORANGE = (214, 112, 60)
ROPE = (176, 162, 128)
CAGE_P = (96, 108, 112)                             # 笼子：蓝灰钢（旧）


# ============================================================ 小工具
def shade(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c)


def mx(a, b, u):
    return mix(a, b, u)


def rect(d, box, fill, outline=None):
    d.rectangle(box, fill=C(fill) if fill is not None else None, outline=C(outline) if outline else None)


def line(d, pts, fill, width=1):
    d.line(pts, fill=C(fill), width=width)


def px(d, x, y, fill):
    d.point((x, y), fill=C(fill))


def arr(im):
    return np.array(im).astype(np.float32)


def img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def poly_mask(w, h, pts):
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m) > 0


def box_mask(box, w=PW, h=H):
    m = np.zeros((h, w), bool)
    x0, y0, x1, y1 = box
    m[max(0, y0):max(0, y1 + 1), max(0, x0):max(0, x1 + 1)] = True
    return m


def snoise(w, h, cx, cy, seed, octaves=3, wrap=False):
    """横向拉长的值噪声 [0,1]（cx / cy = 横 / 竖方向的格子大小）；wrap=True 时横向首尾相接。"""
    sx = max(1.0, cx / float(cy))
    ww = int(math.ceil(w / sx))
    if wrap:
        while ww % cy:
            ww += 1
        base = A._fbm_wrap(ww, h, cy, seed, octaves)
        tri = np.concatenate([base, base, base], axis=1)
        big = np.array(Image.fromarray(tri.astype(np.float32), 'F').resize((int(round(ww * 3 * sx)), h), Image.BILINEAR))
        k = int(round(ww * sx))
        out = big[:, k:k + w]
        if out.shape[1] < w:
            out = np.concatenate([out, big[:, :w - out.shape[1]]], axis=1)
        return out
    base = A._fbm(ww + 2, h, cy, seed, octaves)
    big = np.array(Image.fromarray(base.astype(np.float32), 'F').resize((int(round((ww + 2) * sx)), h), Image.BILINEAR))
    return big[:, :w]


def bayer(w, h):
    return A._bayer(w, h)


def tex(im, box, amt, seed, cell=3):
    x0, y0, x1, y1 = box
    A._tex_noise(im, (max(0, x0), max(0, y0), min(im.width, x1), min(im.height, y1)), amt, seed, cell)


# ---------------------------------------------------------------- 锈（numpy，就地）：流痕、锈点、墙脚积锈、起泡剥落、铆钉
def _blend_px(a, y, x, col, f):
    a[y, x, :3] = a[y, x, :3] * (1 - f) + np.asarray(col, np.float32) * f


def rust_streaks(a, box, n, seed, col=RUST, amax=0.5, lmin=3, lmax=14, starts=None, mask=None, width2=0.12):
    """竖直锈流痕：从 starts（[(x,y)]）或框上半随机位置往下流，越往下越淡（阶梯化，不糊）。"""
    x0, y0, x1, y1 = box
    hh, ww = a.shape[:2]
    pts = starts if starts is not None else [(int(hrange(x0, x1, seed, i, 1)), int(hrange(y0, y0 + (y1 - y0) * 0.55, seed, i, 2)))
                                              for i in range(n)]
    for i, (sx, sy) in enumerate(pts):
        L = int(hrange(lmin, lmax, seed, i, 3))
        wide = hash01(seed, i, 4) < width2
        for k in range(L):
            y = sy + k
            if y > y1 or y >= hh or y < 0:
                break
            f = amax * (1 - k / float(L)) ** 0.7
            f = round(f * 4) / 4.0
            if f <= 0:
                continue
            for xx in ((sx, sx + 1) if (wide and k < L * 0.5) else (sx,)):
                if not (0 <= xx < ww) or a[y, xx, 3] == 0:
                    continue
                if mask is not None and not mask[y, xx]:
                    continue
                _blend_px(a, y, xx, col, f)


def pitting(a, box, n, seed, mask=None, col=RUST_D, f=0.55, bias=1.8):
    """锈点：1–2 px 的深锈点，越往下越多。"""
    x0, y0, x1, y1 = box
    hh, ww = a.shape[:2]
    for i in range(n):
        u = hash01(seed, i, 1) ** (1.0 / bias)
        y = int(y0 + (y1 - y0) * u)
        x = int(hrange(x0, x1, seed, i, 2))
        for (xx, yy) in ((x, y), (x + 1, y)) if hash01(seed, i, 3) < 0.3 else ((x, y),):
            if 0 <= xx < ww and 0 <= yy < hh and a[yy, xx, 3] > 0 and (mask is None or mask[yy, xx]):
                _blend_px(a, yy, xx, col, f)
                if yy + 1 < hh and hash01(seed, i, 4) < 0.5 and (mask is None or mask[yy + 1, xx]):
                    _blend_px(a, yy + 1, xx, col, f * 0.5)


def rust_band(a, box, h, seed, mask=None, col=RUST_D, col2=RUST, f=0.55):
    """墙脚积锈：框底下 h 行，越往下越密（Bayer 抖动 + 噪声边，不糊）。"""
    x0, y0, x1, y1 = box
    ya = y1 - h + 1
    w = x1 - x0 + 1
    n = A._vnoise(w, h, 3, seed)
    th = bayer(PW, H)
    for j in range(h):
        y = ya + j
        if not (0 <= y < a.shape[0]):
            continue
        u = (j + 1) / float(h)
        for i in range(w):
            x = x0 + i
            if not (0 <= x < a.shape[1]) or a[y, x, 3] == 0 or (mask is not None and not mask[y, x]):
                continue
            v = u * 0.95 + (n[j, i] - 0.5) * 0.7
            if th[y, x] < v:
                _blend_px(a, y, x, col if n[j, i] < 0.55 else col2, f)


def blisters(a, box, seed, thr=0.8, mask=None, col=RUST, f=0.5, cell=2):
    """起泡 / 小块剥落：小噪声块换成半锈色，块下沿压暗一道（漆皮翘起的影子）。"""
    x0, y0, x1, y1 = box
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(a.shape[1] - 1, x1), min(a.shape[0] - 1, y1)
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if w <= 1 or h <= 1:
        return
    n = A._vnoise(w, h, cell, seed)
    m = n > thr
    sub = a[y0:y1 + 1, x0:x1 + 1]
    mm = m & (sub[..., 3] > 0)
    if mask is not None:
        mm &= mask[y0:y1 + 1, x0:x1 + 1]
    sub[mm, :3] = sub[mm, :3] * (1 - f) + np.array(col, np.float32) * f
    dn = np.zeros_like(mm)
    dn[1:] = mm[:-1] & ~mm[1:]
    dn &= sub[..., 3] > 0
    if mask is not None:
        dn &= mask[y0:y1 + 1, x0:x1 + 1]
    sub[dn, :3] *= 0.9


def rivets_h(d, x0, x1, y, step, base, phase=0):
    for x in range(x0 + phase, x1 + 1, step):
        px(d, x, y, shade(base, 1.18))
        px(d, x + 1, y + 1, shade(base, 0.78))


def rivets_v(d, x, y0, y1, step, base):
    for y in range(y0, y1 + 1, step):
        px(d, x, y, shade(base, 1.18))
        px(d, x + 1, y + 1, shade(base, 0.78))


def diamond_plate(d, box, base, step=4):
    """花纹钢板（防滑纹）：一格一个小斜条，方向交替；上左亮、下右暗。"""
    x0, y0, x1, y1 = box
    rect(d, box, base)
    j = 0
    for y in range(y0, y1 - 1, 3):
        for i, x in enumerate(range(x0 + (j % 2) * 2, x1 - 1, step)):
            if (i + j) % 2:
                px(d, x, y, shade(base, 1.14))
                px(d, x + 1, y + 1, shade(base, 0.82))
            else:
                px(d, x + 1, y, shade(base, 1.14))
                px(d, x, y + 1, shade(base, 0.82))
        j += 1


def veil(a, y_top, y_bot, amax, col=FOG):
    """雾：越往上越淡（y_bot 以下不加，y_top 处加到 amax）。只动不透明的像素。"""
    hh = a.shape[0]
    ys = np.arange(hh, dtype=np.float32)
    f = (np.clip((y_bot - ys) / float(max(1, y_bot - y_top)), 0, 1) * amax)[:, None, None]
    m = (a[..., 3] > 0)[..., None]
    out = a[..., :3] * (1 - f) + np.array(col, np.float32) * f
    a[..., :3] = np.where(m, out, a[..., :3])


def grade(im, amt=0.06):
    """统一调色：降饱和 + 往冷灰偏一点。"""
    return A._grade(im, sat=0.84, val=1.0, tint=(150, 164, 178), tint_amt=amt)


# ---------------------------------------------------------------- 3×5 小字（铭牌 / 喷字）
FONT3 = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'], 'B': ['##.', '#.#', '##.', '#.#', '##.'],
    'C': ['.##', '#..', '#..', '#..', '.##'], 'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'E': ['###', '#..', '##.', '#..', '###'], 'F': ['###', '#..', '##.', '#..', '#..'],
    'G': ['.##', '#..', '#.#', '#.#', '.##'], 'H': ['#.#', '#.#', '###', '#.#', '#.#'],
    'I': ['###', '.#.', '.#.', '.#.', '###'], 'K': ['#.#', '#.#', '##.', '#.#', '#.#'],
    'L': ['#..', '#..', '#..', '#..', '###'], 'M': ['#.#', '###', '###', '#.#', '#.#'],
    'N': ['##.', '#.#', '#.#', '#.#', '#.#'], 'O': ['.#.', '#.#', '#.#', '#.#', '.#.'],
    'P': ['##.', '#.#', '##.', '#..', '#..'], 'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['.##', '#..', '.#.', '..#', '##.'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '###'], 'V': ['#.#', '#.#', '#.#', '#.#', '.#.'],
    'W': ['#.#', '#.#', '###', '###', '#.#'], 'X': ['#.#', '#.#', '.#.', '#.#', '#.#'],
    'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'],
    '0': ['###', '#.#', '#.#', '#.#', '###'], '1': ['.#.', '##.', '.#.', '.#.', '###'],
    '2': ['##.', '..#', '.#.', '#..', '###'], '3': ['##.', '..#', '.#.', '..#', '##.'],
    '4': ['#.#', '#.#', '###', '..#', '..#'], '5': ['###', '#..', '##.', '..#', '##.'],
    '6': ['.##', '#..', '###', '#.#', '###'], '7': ['###', '..#', '.#.', '.#.', '.#.'],
    '8': ['###', '#.#', '###', '#.#', '###'], '9': ['###', '#.#', '###', '..#', '##.'],
    '.': ['...', '...', '...', '...', '.#.'], '-': ['...', '...', '###', '...', '...'],
    '^': ['.#.', '###', '#.#', '...', '...'], '!': ['.#.', '.#.', '.#.', '...', '.#.'],
}


def text3(d, x, y, s, col, pitch=4):
    cx = x
    for ch in s.upper():
        g = FONT3.get(ch)
        if g is not None:
            for r, row in enumerate(g):
                for c_, v in enumerate(row):
                    if v == '#':
                        d.point((cx + c_, y + r), fill=C(col))
        cx += pitch if ch != ' ' else pitch - 1
    return cx


def text_w(s, pitch=4):
    return sum((pitch if ch != ' ' else pitch - 1) for ch in s) - 1


def plate(d, x_mid, y, s, bg=(222, 222, 212), ink=(40, 40, 44), border=(104, 104, 100)):
    """白底铭牌 + 3×5 字；返回牌子的框（给锈避开用）。"""
    tw = text_w(s)
    x0 = x_mid - tw // 2 - 2
    box = (x0, y, x0 + tw + 3, y + 6)
    rect(d, box, bg, border)
    text3(d, x0 + 2, y + 1, s, ink)
    px(d, box[0] + 1, box[1] + 1, shade(bg, 1.06))
    return box


# ---------------------------------------------------------------- 常用零件
def cyl_v(d, x0, x1, y0, y1, base, hi=1.16, lo=0.66):
    """竖直圆柱（光从左上）：左边亮、右边暗。"""
    w = x1 - x0 + 1
    for i in range(w):
        u = i / max(1, w - 1)
        k = hi - (hi - lo) * u ** 1.2
        if w >= 5 and 0.15 < u < 0.4:
            k += 0.06
        line(d, (x0 + i, y0, x0 + i, y1), shade(base, k))


def hazard(d, box, phase=0, step=3):
    """黄黑警示斜纹。"""
    x0, y0, x1, y1 = box
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            k = ((x + y + phase) // step) % 2
            d.point((x, y), fill=C(HAZ_Y if k == 0 else HAZ_K))


def lifebuoy(d, cx, cy, r=6, bg=WHITE):
    """救生圈：橙色 + 四段白带 + 外面一圈绳；中间的洞填 bg（后面的墙色，略暗 = 圈投下的影子）。"""
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C(ORANGE), outline=C(shade(ORANGE, 0.55)))
    d.ellipse((cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3), fill=C(shade(bg, 0.78)), outline=C(shade(ORANGE, 0.6)))
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        for rr in (r - 1.5, r - 2.2):
            for da in (0, 0.2):
                d.point((round(cx + math.cos(a + da) * rr), round(cy + math.sin(a + da) * rr)), fill=C((232, 230, 222)))
    d.arc((cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1), 200, 250, fill=C((240, 168, 118)))
    for ang in range(0, 360, 45):
        a = math.radians(ang + 22)
        d.point((round(cx + math.cos(a) * (r + 1)), round(cy + math.sin(a) * (r + 1))), fill=C(ROPE))


def bitts(d, x, base, h=9, col=(72, 74, 78)):
    """双柱缆桩（底座 + 两根短柱 + 帽）。x = 左柱左边。"""
    rect(d, (x - 2, base - 3, x + 15, base), shade(col, 0.85), INK)
    line(d, (x - 1, base - 3, x + 14, base - 3), shade(col, 1.25))
    for bx in (x, x + 9):
        cyl_v(d, bx, bx + 4, base - h, base - 4, col)
        rect(d, (bx - 1, base - h - 2, bx + 5, base - h), shade(col, 1.1), shade(col, 0.6))
        line(d, (bx, base - h - 2, bx + 4, base - h - 2), shade(col, 1.45))


def mushroom(d, x, base, h=8, col=WHITE):
    """蘑菇头通风筒。"""
    cyl_v(d, x, x + 2, base - h, base, col)
    d.ellipse((x - 3, base - h - 4, x + 5, base - h + 1), fill=C(shade(col, 0.95)), outline=C(shade(col, 0.55)))
    line(d, (x - 2, base - h - 3, x + 3, base - h - 3), shade(col, 1.12))
    line(d, (x - 3, base - h, x + 5, base - h), shade(col, 0.5))


def curve(d, p0, p1, sag, col, n=16):
    prev = None
    for s in np.linspace(0, 1, n):
        x = p0[0] + (p1[0] - p0[0]) * s
        y = p0[1] + (p1[1] - p0[1]) * s + sag * 4 * s * (1 - s)
        if prev is not None:
            line(d, (prev[0], prev[1], round(x), round(y)), col)
        prev = (round(x), round(y))


# ============================================================ 远景（天 + 海 + 雾里的岛）
@lru_cache(maxsize=1)
def far_layer():
    im = A._new(FARW, H, SKY0)
    gradient(im, (0, 0, FARW, HZ), [SKY0, SKY1, SKY2, (210, 214, 214)], bands=12)
    a = arr(im)
    n = snoise(FARW, HZ, 64, 7, 11)                          # 层云：横向拉长的明暗带
    a[:HZ, :, :3] *= (1 + (n[..., None] - 0.5) * 0.09)
    n2 = snoise(FARW, HZ, 90, 10, 23)
    dark = np.clip((n2 - 0.6) / 0.4, 0, 1)[..., None] * np.clip(1 - np.arange(HZ)[:, None, None] / 70.0, 0, 1)
    a[:HZ, :, :3] = a[:HZ, :, :3] * (1 - dark * 0.12) + np.array((120, 130, 142)) * dark * 0.12
    im = img(a)
    sx, sy = SUN                                             # 雾里的太阳（淡）+ 一道层云压在它下半
    A._glow(im, sx, sy, 36, 22, (236, 234, 224), 56, rings=5)
    d = ImageDraw.Draw(im)
    d.ellipse((sx - 7, sy - 7, sx + 7, sy + 7), fill=C((232, 232, 222)))
    d.ellipse((sx - 6, sy - 6, sx + 6, sy + 6), fill=C((240, 238, 230)))
    lay = A._new(FARW, H)
    ld = ImageDraw.Draw(lay)
    for (y0, h, al) in ((sy + 1, 3, 120), (sy + 5, 2, 90), (sy - 4, 1, 60)):
        ld.rectangle((sx - 40, y0, sx + 50, y0 + h - 1), fill=C((176, 184, 190), al))
    im.alpha_composite(lay)
    a = arr(im)
    ys = np.arange(HZ, dtype=np.float32)                      # 海平线附近起雾（亮、灰）
    hz = np.clip((ys - (HZ - 26)) / 26.0, 0, 1) ** 1.6
    a[:HZ, :, :3] = a[:HZ, :, :3] * (1 - hz[:, None, None] * 0.55) + np.array(FOG) * hz[:, None, None] * 0.55
    im = img(a)
    gradient(im, (0, HZ, FARW, H), [SEA0, SEA1, SEA2, (90, 106, 118)], bands=9)
    d = ImageDraw.Draw(im)
    for (x0, x1, hh, seed, k) in ((236, 318, 6, 3, 0.20), (300, 352, 3, 5, 0.16), (392, 440, 4, 7, 0.14), (8, 44, 2, 9, 0.12)):
        pts = []                                             # 雾里隐约的岛（很淡）
        for x in range(x0, x1 + 1, 2):
            u = (x - x0) / float(x1 - x0)
            yy = HZ - hh * max(0.0, math.sin(u * math.pi)) ** 0.7 * (0.75 + 0.25 * math.sin(x * 0.21 + seed))
            pts.append((x, yy))
        pts += [(x1, HZ), (x0, HZ)]
        d.polygon(pts, fill=C(mx(SEA0, (118, 128, 138), k)))
    line(d, (0, HZ, FARW, HZ), mx(SEA0, (226, 230, 230), 0.4))
    for i in range(520):                                     # 海面：稀疏的亮 / 暗短线（越近越长）
        u = hash01(i, 71) ** 1.5
        y = HZ + 2 + int(u * (H - HZ - 3))
        L = 2 + int(u * 9 * hash01(i, 72))
        x = int(hrange(-10, FARW, i, 73))
        c = mx(SEA1, (196, 204, 208), 0.45) if hash01(i, 74) < 0.5 else mx(SEA2, (70, 86, 98), 0.4)
        line(d, (x, y, x + L, y), c)
    for i in range(40):                                      # 太阳下面一条淡淡的反光
        y = HZ + 2 + int(hrange(0, 30, i, 81))
        x = sx + int(hrange(-6, 6, i, 82) * (1 + (y - HZ) / 12.0))
        line(d, (x, y, x + int(hrange(1, 4, i, 83)), y), (204, 208, 206))
    return grade(im, 0.04)


# ============================================================ 雾带（wrap，横向首尾相接）
def fog_band(w, h, seed, amax, cx, cy, thr, env):
    n = snoise(w, h, cx, cy, seed, octaves=3, wrap=True)
    e = np.array([env(k / float(max(1, h - 1))) for k in range(h)], np.float32)[:, None]
    al = np.clip((n - thr) / (1 - thr), 0, 1) * e * amax
    step = amax / 4.0
    q = np.clip(np.floor(al / step + bayer(w, h)) * step, 0, amax)   # 4 级透明度，Bayer 抖动接缝
    a = np.zeros((h, w, 4), np.float32)
    a[..., :3] = FOG
    a[..., 3] = q
    return img(a)


FOGF_Y, FOGL_Y, FOGH_Y = 70, 96, 0


@lru_cache(maxsize=1)
def fog_far():
    """海平线上的一条雾带（y 70–134），k 0.45、每秒往左飘 2 px。"""
    return fog_band(640, 64, 31, 96, 120, 9, 0.42, lambda u: max(0.0, math.sin(min(1.0, u * 1.15) * math.pi)) ** 1.3)


@lru_cache(maxsize=1)
def fog_low():
    """甲板上的薄雾（y 96–150）：压低可走带后面的对比；k 1、每秒往左飘 2.5 px。"""
    return fog_band(640, 54, 59, 56, 110, 8, 0.38, lambda u: max(0.0, math.sin(u * math.pi)) ** 0.9)


@lru_cache(maxsize=1)
def fog_high():
    """高处的薄雾（y 0–66）：笼住吊车、桅杆、驾驶台的上半截，k 0.7、每秒往左飘 3 px。"""
    return fog_band(640, 66, 47, 76, 150, 10, 0.46, lambda u: (max(0.0, math.sin(u * math.pi)) ** 0.8) * (1.0 - 0.35 * u))


# ============================================================ 甲板层
def _floor(im):
    """甲板（y 134–180）：红丹漆的旧钢板，接缝 + 焊点、锈斑、磨掉漆的地方、湿印；可走带里对比压低。"""
    a = arr(im)
    y0 = BW_BASE
    hh = H - y0
    ys = np.arange(hh, dtype=np.float32)[:, None]
    base = np.array(DECK_F, np.float32) + (np.array(DECK_N, np.float32) - np.array(DECK_F, np.float32)) * (ys / hh)[..., None]
    base = np.broadcast_to(base, (hh, PW, 3)).copy()
    n = snoise(PW, hh, 30, 6, 101)
    rustm = np.clip((n - 0.56) / 0.2, 0, 1)
    base = base * (1 - rustm[..., None] * 0.32) + np.array(RUST) * rustm[..., None] * 0.32
    n2 = snoise(PW, hh, 26, 5, 103)
    worn = np.clip((0.34 - n2) / 0.14, 0, 1)
    base = base * (1 - worn[..., None] * 0.28) + np.array(BARE) * worn[..., None] * 0.28
    n3 = A._vnoise(PW, hh, 2, 107) - 0.5
    base *= (1 + n3[..., None] * 0.05)
    a[y0:, :, :3] = base
    a[y0:, :, 3] = 255
    im2 = img(a)
    d = ImageDraw.Draw(im2)
    a = arr(im2)
    # 纵向接缝（沿船长方向的钢板边）+ 横向对接缝（错开）；可走带里浅一点
    rows = [y0, 139, 147, 157, 168, H]
    for j in range(1, len(rows) - 1):
        y = rows[j]
        k = 0.86 if y < BAND[0] else 0.93
        a[y, :, :3] *= k
        a[y + 1, :, :3] *= 1.04
    for j in range(len(rows) - 1):
        ya, yb = rows[j] + 1, rows[j + 1] - 1
        off = int(hrange(0, 60, j, 5))
        step = 58 + j * 6
        for x in range(off, PW, step):
            a[ya:yb + 1, x, :3] *= (0.88 if ya < BAND[0] else 0.94)
            if j <= 1:                                   # 远处两排：焊缝边上一串焊点
                a[ya + 1:yb:2, x + 1, :3] *= 1.07
    # 舷墙脚下的阴影 + 积锈
    for k, f in enumerate((0.6, 0.72, 0.84, 0.93)):
        a[y0 + k, :, :3] *= f
    rust_streaks(a, (0, y0, PW, y0 + 6), 0, 113,
                 starts=[(int(hrange(0, PW, i, 114)), y0 + 1) for i in range(140)], col=RUST_D, amax=0.5, lmin=2, lmax=5)
    pitting(a, (0, y0 + 2, PW - 1, H - 1), 900, 115, col=RUST_D, f=0.32, bias=1.0)
    im2 = img(a)
    d = ImageDraw.Draw(im2)
    # 湿印（雾水积的薄薄一层：暗一点，远边一条反光）
    for (cx, cy, rx, ry) in ((186, 150, 10, 1), (342, 165, 14, 2), (424, 151, 7, 1), (590, 161, 11, 2), (44, 167, 9, 1)):
        a = arr(im2)
        m = np.zeros((H, PW), bool)
        yy, xx = np.mgrid[0:H, 0:PW]
        m = ((xx - cx) / float(rx)) ** 2 + ((yy - cy) / float(ry + 0.5)) ** 2 <= 1.0
        a[m, :3] *= 0.86
        im2 = img(a)
        d = ImageDraw.Draw(im2)
        line(d, (cx - rx + 2, cy - ry, cx + rx - 3, cy - ry), mx(DECK_F, (172, 180, 186), 0.45))
    # 登船口、货舱门口、两扇门口的花纹钢板（防滑）
    for box in ((12, 136, 50, 141), (462, 143, 490, 147), (546, 143, 576, 147), (594, 143, 630, 147)):
        diamond_plate(d, box, mx(BARE, DECK_F, 0.3))
        line(d, (box[0], box[1], box[2], box[1]), shade(BARE, 1.1))
        line(d, (box[0], box[3], box[2], box[3]), shade(BARE, 0.7))
    # 近边：排水沟的小挡条 + 排水孔（大部分被前景栏杆挡着）
    line(d, (0, 176, PW, 176), shade(DECK_N, 0.78))
    line(d, (0, 177, PW, 177), shade(DECK_N, 1.08))
    for x in range(30, PW, 64):
        rect(d, (x, 178, x + 4, 179), (48, 40, 38))
    return im2


def _bulwark(im):
    """远侧舷墙（y 117–134）：内侧灰白漆、扶手、肘板、排水口、两排铆钉；锈流痕、锈点、墙脚积锈；缺口给舷梯。"""
    d = ImageDraw.Draw(im)
    for y in range(BW_TOP + 2, BW_BASE):
        u = (y - BW_TOP) / float(BW_BASE - BW_TOP)
        line(d, (0, y, PW, y), mx(shade(BULW, 1.05), shade(BULW, 0.86), u))
    line(d, (0, BW_TOP - 1, PW, BW_TOP - 1), (210, 212, 206))       # 扶手（圆管）
    line(d, (0, BW_TOP, PW, BW_TOP), (182, 184, 178))
    line(d, (0, BW_TOP + 1, PW, BW_TOP + 1), (118, 118, 114))
    rivets_h(d, 2, PW, BW_TOP + 3, 4, BULW)
    rivets_h(d, 0, PW, BW_BASE - 3, 4, shade(BULW, 0.9), phase=2)
    for x in range(10, PW, 24):                                      # 肘板（内侧看是一条竖板）
        if GAP[0] - 4 <= x <= GAP[1] + 2:
            continue
        line(d, (x, BW_TOP + 2, x, BW_BASE - 1), shade(BULW, 1.08))
        line(d, (x + 1, BW_TOP + 2, x + 1, BW_BASE - 1), shade(BULW, 0.86))
        d.polygon([(x - 2, BW_BASE - 1), (x + 3, BW_BASE - 1), (x + 1, BW_BASE - 5)], fill=C(shade(BULW, 0.9)))
    for x in (70, 168, 286, 384, 486, 560):                          # 排水口（带翻板）
        rect(d, (x, BW_BASE - 5, x + 10, BW_BASE - 1), (66, 70, 72))
        line(d, (x, BW_BASE - 6, x + 10, BW_BASE - 6), shade(BULW, 0.74))
        line(d, (x + 1, BW_BASE - 5, x + 9, BW_BASE - 5), (92, 98, 100))
    a = arr(im)
    m = np.zeros((H, PW), bool)
    m[BW_TOP - 1:BW_BASE, :] = True
    starts = [(int(hrange(0, PW, i, 201)), BW_TOP + 2) for i in range(90)]
    starts += [(x + 1, BW_TOP + 2) for x in range(10, PW, 48)]
    rust_streaks(a, (0, BW_TOP, PW, BW_BASE), 0, 203, starts=starts, amax=0.42, lmin=3, lmax=13, mask=m)
    pitting(a, (0, BW_TOP + 2, PW - 1, BW_BASE - 1), 260, 204, mask=m, f=0.45)
    blisters(a, (0, BW_TOP + 2, PW - 1, BW_BASE - 2), 205, thr=0.82, mask=m, f=0.4)
    rust_band(a, (0, BW_TOP, PW - 1, BW_BASE - 1), 4, 207, mask=m, f=0.45)
    a[:BW_BASE, GAP[0]:GAP[1] + 1, 3] = 0                  # 缺口：透出后面的海
    im2 = img(a)
    tex(im2, (0, BW_TOP + 2, PW, BW_BASE), 0.04, 211)
    return im2


def _gangway(im):
    """舷梯：缺口两边的端柱、舷梯平台的栏杆柱 + 扶手绳（往左下伸出去）、吊舷梯的小吊杆、甲板上的花纹板
    + 斑马线；系着救生艇缆绳的缆桩；舷墙上一只救生圈。"""
    d = ImageDraw.Draw(im)
    g0, g1 = GAP
    # 缺口外：舷梯平台的边（甲板高度）+ 两根栏杆柱 + 扶手绳往左下走（舷梯顺着船壳往下）
    line(d, (g0, BW_BASE - 1, g1, BW_BASE - 1), (84, 86, 88))
    line(d, (g0, BW_BASE - 2, g1, BW_BASE - 2), (138, 140, 140))
    for k in range(3):                                               # 平台的格栅
        line(d, (g0 + 2 + k * 8, BW_BASE - 3, g0 + 6 + k * 8, BW_BASE - 3), (110, 112, 112))
    post = (202, 202, 196)
    for sx in (g0 + 4, g1 - 4):
        line(d, (sx, 110, sx, BW_BASE - 3), post)
        line(d, (sx + 1, 110, sx + 1, BW_BASE - 3), shade(post, 0.62))
        d.ellipse((sx - 1, 108, sx + 2, 111), fill=C(post), outline=C((112, 110, 106)))
    curve(d, (g1 - 3, 111), (g0 + 5, 113), 3, ROPE)                  # 平台上的扶手绳
    curve(d, (g1 - 3, 120), (g0 + 5, 122), 2, shade(ROPE, 0.86))
    curve(d, (g0 + 4, 111), (g0 - 8, 121), 1, ROPE)                  # 往左下伸出去（被舷墙挡住）
    curve(d, (g0 + 4, 120), (g0 - 8, 128), 1, shade(ROPE, 0.86))
    for ex_ in (g0 - 3, g1 + 1):                                     # 端柱（舷墙断口的圆边）
        cyl_v(d, ex_, ex_ + 2, 113, BW_BASE - 1, BULW, hi=1.18, lo=0.7)
        d.ellipse((ex_ - 1, 111, ex_ + 3, 115), fill=C((204, 206, 200)), outline=C((118, 118, 114)))
    # 吊舷梯的小吊杆：甲板上一根粗柱 + 弯过来的臂 + 滑车 + 钢缆垂到缺口外
    p0 = g1 + 6
    cyl_v(d, p0, p0 + 3, 92, 139, (186, 188, 182))
    hazard(d, (p0, 131, p0 + 3, 139), step=2)
    rect(d, (p0 - 2, 138, p0 + 5, 140), (90, 92, 94), INK)
    for k in range(15):                                              # 弯臂（粗 2 px）
        s = k / 14.0
        x = round(p0 + 1 - s * 15)
        y = round(92 - 6 * math.sin(s * math.pi * 0.6))
        rect(d, (x - 1, y - 1, x, y), (180, 182, 176))
        px(d, x, y - 1, (214, 216, 210))
        px(d, x - 1, y, (128, 130, 126))
    hx, hy = p0 - 14, 89
    d.ellipse((hx - 2, hy, hx + 2, hy + 4), fill=C((150, 152, 150)), outline=C((70, 72, 74)))   # 滑轮
    px(d, hx, hy + 2, (60, 60, 64))
    line(d, (hx, hy + 5, hx, 100), (92, 94, 98))                     # 钢缆 → 吊钩 → 两根吊索拉着舷梯平台的两根柱子
    d.arc((hx - 2, 100, hx + 1, 104), 0, 200, fill=C((110, 112, 116)))
    line(d, (hx, 103, g0 + 5, 109), (104, 106, 110))
    line(d, (hx, 103, g1 - 3, 109), (104, 106, 110))
    # 甲板上的斑马线（登船口）
    hazard(d, (g0 - 3, BW_BASE + 1, g1 + 3, BW_BASE + 2), step=3)
    # 救生圈（缺口左边的舷墙上）
    lifebuoy(d, 8, 125, r=6, bg=BULW)
    # 缆桩 + 他们那条救生艇的缆绳（8 字绕两圈，拖到缺口外）
    bx = 62
    bitts(d, bx, 141, h=8)
    for k in range(3):
        line(d, (bx + 1, 133 + k, bx + 12, 136 - k), ROPE)
        line(d, (bx + 1, 136 - k, bx + 12, 133 + k), shade(ROPE, 0.84))
    curve(d, (bx + 1, 137), (g1 - 4, BW_BASE - 2), 3, ROPE, n=20)
    curve(d, (bx + 1, 138), (g1 - 4, BW_BASE - 1), 3, shade(ROPE, 0.7), n=20)
    return im


def _foremast(im):
    """前桅（x ≈ 72）：细桅杆 + 横桁 + 桅灯 + 雷达反射器 + 拉索 + 挂旗绳。"""
    d = ImageDraw.Draw(im)
    mxc = 72
    line(d, (mxc + 14, 31, mxc + 28, BW_TOP - 1), (96, 98, 102))   # 拉索（左边那根会穿过舷梯，不画）
    line(d, (mxc, 9, -6, 70), (96, 98, 102))                        # 前支索（往船头）
    line(d, (mxc + 2, 10, mxc + 9, 30), (126, 126, 130))            # 挂旗绳
    cyl_v(d, mxc - 2, mxc + 2, 8, BW_BASE - 1, (180, 182, 176))
    rect(d, (mxc - 4, BW_BASE - 3, mxc + 4, BW_BASE), shade(EQ, 0.9), INK)
    rect(d, (mxc - 16, 30, mxc + 16, 31), (166, 168, 162))          # 横桁 + 桅灯
    line(d, (mxc - 16, 30, mxc + 16, 30), (204, 206, 200))
    for lx in (mxc - 15, mxc + 14):
        rect(d, (lx - 1, 32, lx + 1, 35), (64, 64, 68))
        px(d, lx, 33, (218, 214, 192))
    rect(d, (mxc - 2, 4, mxc + 2, 8), (64, 64, 68))                 # 桅顶灯
    px(d, mxc, 5, (224, 220, 204))
    d.polygon([(mxc + 3, 44), (mxc + 8, 40), (mxc + 8, 48)], fill=C((152, 156, 160)), outline=C((92, 94, 98)))   # 雷达反射器
    line(d, (mxc + 3, 44, mxc + 3, 50), (92, 94, 98))
    a = arr(im)
    rust_streaks(a, (mxc - 3, 8, mxc + 3, BW_BASE), 0, 221,
                 starts=[(mxc + int(hrange(-2, 2, i, 222)), int(hrange(10, 120, i, 223))) for i in range(10)],
                 amax=0.4, lmin=3, lmax=10, mask=box_mask((mxc - 2, 8, mxc + 2, BW_BASE)))
    return img(a)


def _galley(im):
    """餐厅（厨房）甲板室：白漆钢墙、门虚掩漏暖光、起雾的小窗、GALLEY 牌、救生圈、菜筐、管子、屋顶的烟道和通风筒。"""
    x0, y0, x1, y1 = GALLEY
    d = ImageDraw.Draw(im)
    # 屋顶上的东西（先画，被屋檐挡住根部）
    sx = STACK_X
    cyl_v(d, sx - 2, sx + 2, 74, y0 - 2, (122, 118, 114))
    for yy in range(78, y0 - 2, 5):
        line(d, (sx - 2, yy, sx + 2, yy), (98, 92, 88))
    d.polygon([(sx - 6, 75), (sx, 70), (sx + 6, 75)], fill=C((136, 132, 128)), outline=C((72, 68, 66)))   # 烟道雨帽
    line(d, (sx - 5, 75, sx + 5, 75), (72, 68, 66))
    line(d, (sx - 2, 72, sx, 71), (178, 174, 168))
    line(d, (sx - 3, 76, sx + 3, 76), (54, 50, 50))                 # 帽子底下的缝（冒热气的地方）
    mushroom(d, 88, y0 - 3, h=7, col=WHITE)
    gx = 120                                                        # 鹅颈通风管
    cyl_v(d, gx, gx + 2, 80, y0 - 2, WHITE)
    d.arc((gx - 4, 76, gx + 3, 84), 180, 360, fill=C(WHITE_D), width=3)
    line(d, (gx - 4, 80, gx - 4, 83), shade(WHITE, 0.6))
    for xx in range(x0, x1 + 1, 10):                                # 屋顶栏杆
        line(d, (xx, 84, xx, y0 - 3), (150, 152, 148))
    line(d, (x0, 84, x1, 84), (178, 180, 174))
    line(d, (x0, 88, x1, 88), (142, 144, 140))
    # 墙面 + 竖向板缝铆钉
    for y in range(y0, y1 + 1):
        u = (y - y0) / float(y1 - y0)
        line(d, (x0, y, x1, y), mx(shade(WHITE, 1.02), shade(WHITE, 0.86), u ** 1.4))
    for xx in (x0 + 2, 124, x1 - 2):
        rivets_v(d, xx, y0 + 4, y1 - 10, 4, shade(WHITE, 0.94))
    rect(d, (x0, y1 - 8, x1, y1), (84, 96, 88))                     # 墙脚的灰绿踢脚
    line(d, (x0, y1 - 8, x1, y1 - 8), (118, 130, 120))
    rect(d, (x0 - 2, y0 - 4, x1 + 2, y0 - 1), shade(WHITE, 0.92))   # 屋檐
    line(d, (x0 - 2, y0 - 4, x1 + 2, y0 - 4), WHITE_L)
    line(d, (x0 - 2, y0 - 1, x1 + 2, y0 - 1), (112, 112, 108))
    line(d, (x0, y0, x1, y0), shade(WHITE, 0.72))                   # 屋檐下的阴影
    line(d, (x0, y0 + 1, x1, y0 + 1), shade(WHITE, 0.84))
    line(d, (x0, y0, x0, y1), WHITE_L)
    line(d, (x1, y0, x1, y1), shade(WHITE, 0.7))
    # 管子：墙上一根竖管 + 一根横管 + 阀门手轮
    cyl_v(d, 97, 99, y0 + 2, y1 - 9, (152, 154, 150))
    line(d, (x0 + 1, 127, 97, 127), (152, 154, 150))
    line(d, (x0 + 1, 128, 97, 128), (112, 114, 110))
    d.ellipse((94, 114, 101, 120), outline=C((166, 54, 46)))
    line(d, (94, 117, 101, 117), (166, 54, 46))
    line(d, (97, 114, 97, 120), (166, 54, 46))
    # 门（钢门、圆角、虚掩：右边一条缝漏出厨房的暖光）
    dx0, dy0, dx1, dy1 = G_DOOR
    rect(d, (dx0 - 1, dy0 - 1, dx1 + 1, dy1), (122, 124, 120))
    d.rounded_rectangle((dx0, dy0, dx1 - 2, dy1 - 4), radius=3, fill=C((168, 176, 168)), outline=C((92, 98, 92)))
    line(d, (dx0 + 1, dy0 + 3, dx0 + 1, dy1 - 6), (196, 202, 194))
    line(d, (dx0 + 3, dy0 + 1, dx1 - 5, dy0 + 1), (196, 202, 194))
    rect(d, (dx1 - 1, dy0 + 1, dx1, dy1 - 4), (36, 28, 26))        # 门缝
    line(d, (dx1, dy0 + 3, dx1, dy1 - 6), (220, 168, 106))         # 缝里的灯光
    px(d, dx1 - 1, dy1 - 6, (150, 110, 70))
    for yy in (dy0 + 7, dy0 + 18, dy0 + 29):                        # 门把（压紧扣）
        line(d, (dx1 - 5, yy, dx1 - 3, yy), (66, 68, 66))
        px(d, dx1 - 5, yy - 1, (206, 208, 202))
    cxw, cyw = (dx0 + dx1 - 2) // 2, dy0 + 9                        # 门上的圆窗（里面亮着灯）
    d.ellipse((cxw - 3, cyw - 3, cxw + 3, cyw + 3), fill=C((132, 134, 128)))
    d.ellipse((cxw - 2, cyw - 2, cxw + 2, cyw + 2), fill=C((220, 186, 130)))
    px(d, cxw - 1, cyw - 1, (248, 232, 192))
    rect(d, (dx0 - 1, dy1 - 3, dx1 + 1, dy1), (96, 102, 96))        # 门槛（高门槛）
    line(d, (dx0 - 1, dy1 - 3, dx1 + 1, dy1 - 3), (152, 156, 150))
    sign = plate(d, (dx0 + dx1) // 2, 96, 'GALLEY')
    # 起雾的小窗：玻璃一层水汽（暖白），几道流下来的水痕透出里面暖暗的厨房，中间一团灶台的灯光
    wx0, wy0, wx1, wy1 = G_WIN
    d.rounded_rectangle((wx0 - 1, wy0 - 1, wx1 + 1, wy1 + 1), radius=3, fill=C((142, 144, 138)), outline=C((96, 98, 94)))
    d.rounded_rectangle((wx0 + 1, wy0 + 1, wx1 - 1, wy1 - 1), radius=2, fill=C((206, 196, 178)))
    A._glow(im, wx0 + 11, wy0 + 9, 7, 4, (255, 214, 150), 90, rings=3)
    a = arr(im)
    n = A._vnoise(wx1 - wx0, wy1 - wy0, 2, 301)
    sub = a[wy0 + 2:wy1 - 1, wx0 + 2:wx1 - 1, :3]
    sub[:] = sub * (0.94 + n[:sub.shape[0], :sub.shape[1], None] * 0.1)
    im = img(a)
    d = ImageDraw.Draw(im)
    for (xx, top, L) in ((wx0 + 4, wy0 + 5, 8), (wx0 + 9, wy0 + 3, 10), (wx0 + 15, wy0 + 6, 7)):   # 水痕
        for k in range(L):
            yy = top + k
            if yy >= wy1 - 1:
                break
            px(d, xx, yy, (124, 96, 76) if k % 3 else (164, 128, 98))
        px(d, xx, top - 1, (232, 226, 214))
    line(d, (wx0 + 2, wy0 + 2, wx1 - 3, wy0 + 2), (234, 228, 216))
    line(d, (wx0 - 1, wy1 + 2, wx1 + 1, wy1 + 2), (224, 226, 218))   # 窗台
    lifebuoy(d, 89, 109, r=6)                                       # 救生圈（门左边）
    # 菜筐（窗下）：木条筐 + 卷心菜 + 洋葱
    cx0, cy0, cx1, cy1 = 124, 130, 142, 141
    rect(d, (cx0, cy0, cx1, cy1), (150, 118, 80), (86, 62, 42))
    for yy in (cy0 + 3, cy0 + 7):
        line(d, (cx0 + 1, yy, cx1 - 1, yy), (114, 86, 56))
    for xx in (cx0 + 6, cx0 + 12):
        line(d, (xx, cy0 + 1, xx, cy1 - 1), (126, 96, 64))
    for (vx, col, r_) in ((cx0 + 3, (118, 152, 92), 3), (cx0 + 9, (134, 166, 104), 3), (cx0 + 15, (198, 170, 114), 2),
                          (cx0 + 13, (206, 180, 124), 2)):
        d.ellipse((vx - r_, cy0 - r_, vx + r_, cy0 + r_ - 1), fill=C(col), outline=C(shade(col, 0.6)))
        px(d, vx - 1, cy0 - r_ + 1, shade(col, 1.22))
    # 门边一只水桶 + 拖把（扔下没收）
    rect(d, (82, 132, 88, 140), (128, 136, 142), (72, 76, 80))
    line(d, (82, 132, 88, 132), (176, 182, 188))
    line(d, (93, 141, 99, 108), (148, 120, 82))
    d.polygon([(90, 140), (96, 140), (95, 136), (91, 136)], fill=C((194, 188, 170)))
    # 锈：屋檐、窗角、门边、管子往下流；墙脚积锈；锈点、起泡（避开铭牌 / 门 / 窗 / 救生圈）
    a = arr(im)
    keep = box_mask((x0, y0, x1, y1)) & ~box_mask(sign) & ~box_mask((dx0 - 1, dy0 - 1, dx1 + 1, dy1)) \
        & ~box_mask((wx0 - 1, wy0 - 1, wx1 + 1, wy1 + 2)) & ~box_mask((82, 102, 96, 116)) & ~box_mask((cx0 - 4, cy0 - 4, cx1, cy1))
    starts = [(int(hrange(x0, x1, i, 311)), y0 + 2) for i in range(20)]
    starts += [(wx0, wy1 + 3), (wx1, wy1 + 3), (dx0 - 2, dy0 + 2), (dx1 + 2, dy0 + 2), (98, 121), (97, 129), (sign[0], sign[3] + 1)]
    rust_streaks(a, (x0, y0, x1, y1), 0, 313, starts=starts, amax=0.45, lmin=4, lmax=20, mask=keep)
    pitting(a, (x0, y0 + 2, x1, y1 - 8), 80, 314, mask=keep, f=0.45)
    blisters(a, (x0, y0 + 2, x1, y1 - 9), 315, thr=0.83, mask=keep, f=0.45)
    rust_band(a, (x0, y0, x1, y1 - 8), 5, 316, mask=keep, f=0.4)
    rust_band(a, (x0, y0, x1, y1), 4, 317, mask=box_mask((x0, y1 - 8, x1, y1)) & ~box_mask((dx0 - 1, dy0, dx1 + 1, dy1)), f=0.5)
    im = img(a)
    tex(im, (x0, y0, x1 + 1, y1 + 1), 0.035, 321)
    return im


def _winch(im):
    """系泊绞盘：底座、两个轴承座、钢缆卷筒（斜绕的钢缆）、法兰、绞缆头、刹车手轮、电机 + 散热片；前面一盘缆绳。"""
    d = ImageDraw.Draw(im)
    base = 140
    rect(d, (150, base - 4, 198, base), shade(EQ, 0.8), INK)        # 底座
    line(d, (151, base - 4, 197, base - 4), EQ_L)
    rivets_h(d, 152, 196, base - 2, 6, shade(EQ, 0.8))
    for (ax0, ax1) in ((158, 163), (181, 186)):                     # 轴承座（梯形）
        d.polygon([(ax0 - 2, base - 4), (ax1 + 2, base - 4), (ax1, 123), (ax0, 123)], fill=C(EQ), outline=C(INK))
        line(d, (ax0, 124, ax0 - 1, base - 5), EQ_L)
        d.ellipse((ax0, 119, ax1, 126), fill=C(shade(EQ, 1.1)), outline=C(INK))
        px(d, (ax0 + ax1) // 2, 122, (40, 40, 40))
    rect(d, (164, 117, 180, 132), (116, 116, 112))                  # 卷筒 + 斜绕的钢缆
    for k, yy in enumerate(range(118, 132, 2)):
        line(d, (164, yy, 180, yy + 1), (90, 90, 88))
        line(d, (164, yy + 1, 180, yy + 2), (138, 138, 134))
    line(d, (164, 117, 180, 117), (164, 164, 160))
    line(d, (164, 132, 180, 132), (66, 66, 64))
    for fx in (163, 180):                                           # 法兰
        rect(d, (fx, 113, fx + 1, 136), shade(EQ, 1.05))
        px(d, fx, 113, EQ_L)
        px(d, fx + 1, 136, EQ_D)
    for k, yy in enumerate(range(120, 134)):                        # 绞缆头（沙漏形，左端）
        u = abs(yy - 127) / 7.0
        hw = 2 + round(2.6 * u)
        line(d, (153 - hw, yy, 153 + hw, yy), shade(EQ, 1.12 - 0.035 * k))
    line(d, (149, 120, 157, 120), EQ_L)
    line(d, (153, 126, 153, 128), EQ_D)
    rect(d, (188, 117, 197, 136), EQ, INK)                          # 电机 + 散热片 + 铭牌
    for yy in range(119, 135, 2):
        line(d, (189, yy, 196, yy), EQ_D)
    rect(d, (190, 124, 194, 127), (198, 198, 188))
    line(d, (189, 117, 196, 117), EQ_L)
    line(d, (172, 116, 172, 108), (70, 74, 72))                     # 刹车手轮（红圈）
    d.ellipse((167, 105, 177, 109), outline=C((166, 52, 44)))
    line(d, (168, 107, 176, 107), (130, 44, 38))
    px(d, 172, 105, (214, 112, 100))
    for r in range(9, 2, -2):                                       # 甲板上一盘缆绳（在可走带后沿，低对比）
        d.ellipse((174 - r * 1.6, 145 - r * 0.32, 174 + r * 1.6, 145 + r * 0.32), outline=C(shade(ROPE, 0.84 + r * 0.015)))
    d.ellipse((171, 144, 177, 146), fill=C(shade(ROPE, 0.62)))
    a = arr(im)
    m = box_mask((148, 104, 199, base))
    rust_streaks(a, (148, 112, 199, base), 22, 331, amax=0.42, lmin=2, lmax=8, mask=m)
    pitting(a, (148, 112, 199, base), 60, 332, mask=m, f=0.5)
    return img(a)


# ---------------------------------------------------------------- 铁笼
def _cage_pts():
    fx0, fy0, fx1, fy1 = CAGE_F
    dx, dy = CAGE_D
    return fx0, fy0, fx1, fy1, fx0 + dx, fy0 + dy, fx1 + dx, fy1 + dy


def _cage_back(im):
    """铁笼里面（画在背景）：后壁（下半钢板、上半铁栏）、顶上的栏、右侧面、地板（稻草 / 报纸 / 铁碗 / 香蕉皮）、垫木、影子。"""
    fx0, fy0, fx1, fy1, bx0, by0, bx1, by1 = _cage_pts()
    P = CAGE_P
    a = arr(im)
    for y in range(fy1 - 2, fy1 + 4):                               # 地上的影子（笼子底下压暗）
        a[y, fx0 - 2:bx1 + 3, :3] *= min(1.0, 0.64 + 0.07 * (y - (fy1 - 2)))
    im = img(a)
    d = ImageDraw.Draw(im)
    # 后壁：下半钢板（带竖筋）
    rect(d, (bx0, 118, bx1, by1), shade(P, 0.74))
    for xx in range(bx0 + 8, bx1, 12):
        line(d, (xx, 119, xx, by1), shade(P, 0.86))
        line(d, (xx + 1, 119, xx + 1, by1), shade(P, 0.62))
    line(d, (bx0, 118, bx1, 118), shade(P, 0.96))
    # 后壁上半：横梁 + 竖栏（透出舷墙 / 海）
    rect(d, (bx0, by0, bx1, by0 + 3), shade(P, 0.7))
    line(d, (bx0, by0, bx1, by0), shade(P, 0.9))
    for xx in range(bx0 + 4, bx1, 7):
        line(d, (xx, by0 + 4, xx, 117), shade(P, 0.74))
        line(d, (xx + 1, by0 + 4, xx + 1, 117), shade(P, 0.56))
    line(d, (bx0, 108, bx1, 108), shade(P, 0.66))
    rect(d, (bx0, by0, bx0 + 1, by1), shade(P, 0.62))
    rect(d, (bx1 - 1, by0, bx1, by1), shade(P, 0.52))
    # 顶上：前后横梁之间一排纵向的栏（从下面看，透得见天）
    for xx in range(fx0 + 4, fx1, 7):
        line(d, (xx, fy0 + 4, xx + CAGE_D[0], by0 + 3), shade(P, 0.6))
    # 右侧面（平行四边形：竖栏 + 下半钢板）
    for k in range(1, CAGE_D[0] + 1):
        x = fx1 + k
        ya = fy0 + round(CAGE_D[1] * k / CAGE_D[0])
        yb = fy1 + round(CAGE_D[1] * k / CAGE_D[0])
        if k % 2 == 0:
            line(d, (x, ya + 2, x, yb - 15), shade(P, 0.92))
        line(d, (x, yb - 15, x, yb), shade(P, 0.78))
        px(d, x, ya, shade(P, 0.86))
        px(d, x, ya + 1, shade(P, 0.74))
    line(d, (fx1, fy1 - 15, bx1, by1 - 15), shade(P, 1.06))
    rect(d, (fx1 + 2, fy1 - 12, fx1 + 4, fy1 - 8), (214, 184, 70))  # 侧面一块小警示牌
    # 地板（木板 + 稀稀的稻草）
    d.polygon([(fx0, fy1 - 2), (fx1, fy1 - 2), (bx1, by1), (bx0, by1)], fill=C((128, 106, 80)))
    for k in range(1, 4):
        yy = by1 + round((fy1 - 2 - by1) * k / 4.0)
        xa = bx0 + round((fx0 - bx0) * k / 4.0)
        xb = bx1 + round((fx1 - bx1) * k / 4.0)
        line(d, (xa, yy, xb, yy), (110, 90, 66))
    for i in range(70):                                             # 稻草
        x = int(hrange(fx0 + 2, bx1 - 2, i, 341))
        y = int(hrange(by1 + 1, fy1 - 2, i, 342))
        L = int(hrange(1, 4, i, 343))
        c = (178, 156, 104) if hash01(i, 344) < 0.6 else (150, 128, 84)
        line(d, (x, y, x + L, y - (1 if hash01(i, 345) < 0.3 else 0)), c)
    for (nx, ny, w_, h_) in ((240, 136, 12, 4), (204, 138, 10, 3)):   # 报纸（摊开两张）+ 一叠
        d.polygon([(nx, ny + h_), (nx + w_, ny + h_), (nx + w_ + 2, ny), (nx + 2, ny)], fill=C((212, 208, 196)),
                  outline=C((150, 146, 136)))
        for k in range(1, h_):
            line(d, (nx + 3, ny + k, nx + w_ - 1, ny + k), (128, 126, 120))
        line(d, (nx + w_ // 2 + 1, ny, nx + w_ // 2, ny + h_), (176, 172, 160))
    rect(d, (252, 132, 258, 135), (200, 196, 184), (132, 128, 120))
    line(d, (253, 133, 257, 133), (112, 110, 106))
    d.ellipse((213, 132, 221, 135), fill=C((150, 156, 160)), outline=C((86, 88, 92)))   # 铁碗
    line(d, (214, 133, 220, 133), (192, 196, 200))
    for (bx_, by_) in ((227, 141), (247, 140)):                     # 香蕉皮
        line(d, (bx_, by_, bx_ + 3, by_ - 1), (218, 192, 76))
        px(d, bx_ + 4, by_ - 2, (110, 88, 42))
        line(d, (bx_ + 1, by_ + 1, bx_ + 3, by_ + 1), (192, 164, 62))
    for sx_ in (fx0 + 2, fx1 - 10):                                 # 垫木
        rect(d, (sx_, fy1, sx_ + 8, fy1 + 2), (114, 90, 64), (70, 54, 38))
    a = arr(im)
    m = poly_mask(PW, H, [(fx0, fy0), (fx1, fy0), (bx1, by0), (bx1, by1), (fx1, fy1), (fx0, fy1), (bx0, by1), (bx0, by0)])
    m &= ~box_mask((fx0, by1, bx1, fy1))
    rust_streaks(a, (bx0, by0, bx1 + 1, by1), 22, 351, amax=0.4, lmin=2, lmax=9, mask=m)
    pitting(a, (bx0, by0, bx1 + 1, by1), 40, 352, mask=m, f=0.45)
    return img(a)


def cage_front(state):
    """铁笼正面（透明底，只有铁栏 / 框 / 门 / 锁）。state 0 = 关着，1 = 门开着（门扇往外甩到左边，锁挂开）。
    这张图既是背景里的 pick（key cage_open），也是剧情的 depth 道具（画在猩猩前面）。只有全透明 / 全不透明两种像素。"""
    fx0, fy0, fx1, fy1 = CAGE_F
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    P = CAGE_P
    hi, mid, lo = shade(P, 1.5), shade(P, 1.05), shade(P, 0.64)
    dx0, dy0, dx1, dy1 = CAGE_DOOR

    def bar(x, ya, yb):
        line(d, (x, ya, x, yb), shade(P, 1.38))
        line(d, (x + 1, ya, x + 1, yb), shade(P, 0.74))

    for x in range(fx0 + 7, fx1 - 4, 7):                           # 竖栏（门洞那一段另画）
        if dx0 - 2 <= x <= dx1:
            continue
        bar(x, fy0 + 4, fy1 - 4)
    for y, c in ((119, hi), (120, mid), (121, lo)):                 # 中间一道横撑
        line(d, (fx0, y, dx0 - 1, y), c)
        line(d, (dx1 + 1, y, fx1, y), c)
    for (ya, yb) in ((fy0, fy0 + 4), (fy1 - 4, fy1)):               # 顶梁 / 底梁（槽钢）+ 铆钉
        rect(d, (fx0, ya, fx1, yb), mid)
        line(d, (fx0, ya, fx1, ya), hi)
        line(d, (fx0, yb, fx1, yb), lo)
        line(d, (fx0, ya + 2, fx1, ya + 2), shade(P, 0.88))
        for xx in range(fx0 + 3, fx1, 8):
            px(d, xx, ya + 1, shade(P, 1.7))
    for (xa, xb) in ((fx0, fx0 + 2), (fx1 - 2, fx1)):               # 角柱（角钢）
        line(d, (xa, fy0, xa, fy1), hi)
        line(d, (xa + 1, fy0, xa + 1, fy1), mid)
        line(d, (xb, fy0, xb, fy1), lo)
    for ex_ in (fx0 + 3, fx1 - 6):                                  # 吊耳
        d.ellipse((ex_, fy0 - 4, ex_ + 3, fy0), outline=C(shade(P, 1.3)))
    rect(d, (fx1 - 13, 125, fx1 - 6, 131), (212, 180, 66), (60, 50, 30))   # 警示牌「!」
    text3(d, fx1 - 11, 126, '!', (40, 36, 30))
    if state == 0:
        rect(d, (dx0, dy0, dx1, dy0 + 1), mid)
        line(d, (dx0, dy0, dx1, dy0), hi)
        rect(d, (dx0, dy1 - 1, dx1, dy1), mid)
        line(d, (dx0, dy0, dx0, dy1), hi)
        line(d, (dx1, dy0, dx1, dy1), lo)
        for x in range(dx0 + 5, dx1 - 1, 5):
            bar(x, dy0 + 2, dy1 - 2)
        line(d, (dx0, 120, dx1, 120), mid)
        for hy in (dy0 + 5, dy1 - 7):                               # 铰链
            rect(d, (dx0 - 2, hy, dx0 + 1, hy + 3), shade(P, 1.2))
        rect(d, (dx1 - 1, 116, dx1 + 3, 118), shade(P, 1.25))       # 搭扣 + 挂锁
        d.arc((dx1, 118, dx1 + 4, 123), 180, 360, fill=C((178, 178, 174)))
        rect(d, (dx1 - 1, 121, dx1 + 5, 126), (142, 114, 62), (72, 56, 32))
        px(d, dx1 + 2, 123, (42, 32, 22))
        px(d, dx1, 122, (198, 168, 98))
        line(d, (dx0 + 8, 121, dx0 + 9, 125), (182, 172, 142))     # 门上挂的货签
        rect(d, (dx0 + 7, 125, dx0 + 12, 130), (206, 182, 124), (138, 114, 72))
        line(d, (dx0 + 8, 127, dx0 + 11, 127), (122, 98, 62))
    else:
        line(d, (dx0, dy0, dx1, dy0), hi)                           # 门洞的门框
        line(d, (dx0, dy0 + 1, dx1, dy0 + 1), lo)
        ox0 = dx0 - 9                                               # 门扇往外（朝镜头）甩开、靠在左边：压扁成一窄条
        for k, x in enumerate(range(ox0, dx0 + 1)):
            dyk = round(3 * (1 - k / 9.0))                          # 离镜头更近 → 下沿往下错
            ya, yb = dy0 + dyk, dy1 + dyk
            if k in (0, 9):
                line(d, (x, ya, x, yb), hi if k == 0 else mid)
            elif k % 2 == 0:
                line(d, (x, ya + 2, x, yb - 2), shade(P, 1.2))
            for yy, c in ((ya, mid), (ya + 1, mid), (yb, lo), (yb - 1, mid), (120 + dyk, mid)):
                px(d, x, yy, c)
        for hy in (dy0 + 5, dy1 - 7):
            rect(d, (dx0 - 2, hy, dx0 + 1, hy + 3), shade(P, 1.2))
        lx, ly = ox0 - 1, 122                                       # 挂锁：开了，挂在门扇外沿
        d.arc((lx - 1, ly - 4, lx + 3, ly + 1), 180, 300, fill=C((178, 178, 174)))
        rect(d, (lx - 1, ly, lx + 4, ly + 5), (142, 114, 62), (72, 56, 32))
        px(d, lx + 1, ly + 2, (42, 32, 22))
        rect(d, (dx1 - 1, 116, dx1 + 3, 118), shade(P, 1.25))       # 门洞右边的搭扣
    a = np.array(im)                                                # 锈点（稀）
    m = a[..., 3] > 0
    ys, xs = np.nonzero(m)
    for i in range(len(xs)):
        r = hash01(int(xs[i]), int(ys[i]), 361)
        if r < 0.045:
            a[ys[i], xs[i], :3] = RUST if r < 0.025 else RUST_D
    return grade(Image.fromarray(a, 'RGBA'))


def _vents_drums(im):
    """喇叭口通风筒（朝左前方，看得见红色的喇叭口和白色的罩背）+ 两只油桶。"""
    d = ImageDraw.Draw(im)
    for (x, col, h) in ((270, (134, 68, 52), 16), (281, (72, 92, 116), 15)):     # 油桶
        base = 142
        cyl_v(d, x, x + 9, base - h, base, col)
        for yy in (base - h + 4, base - 4):
            line(d, (x, yy, x + 9, yy), shade(col, 0.72))
            line(d, (x, yy - 1, x + 9, yy - 1), shade(col, 1.22))
        d.ellipse((x, base - h - 2, x + 9, base - h + 1), fill=C(shade(col, 1.08)), outline=C(shade(col, 0.6)))
        px(d, x + 6, base - h - 1, (42, 38, 36))
    vx = 296                                                        # 喇叭口通风筒（侧看：竖管往上弯向左，喇叭口朝左）
    cyl_v(d, vx - 3, vx + 3, 100, 141, WHITE)
    rect(d, (vx - 5, 138, vx + 5, 141), shade(WHITE, 0.8), INK)
    outer, inner = [], []
    for k in range(13):                                             # 弯头 + 喇叭：外轮廓（上 / 右）、内轮廓（下 / 左）
        s = k / 12.0
        ang = s * math.pi / 2
        r_out, r_in = 9 + 2 * s, 3 - 1.5 * s
        cxp, cyp = vx - 6, 100                                      # 弯头圆心
        outer.append((cxp + math.cos(ang) * (r_out), cyp - math.sin(ang) * (r_out) - 4 * s * s))
        inner.append((cxp + math.cos(ang) * (r_in), cyp - math.sin(ang) * (r_in) + 2 * s * s))
    mouth_x = vx - 8
    pts = [(vx + 3, 101)] + outer + [(mouth_x - 3, 83), (mouth_x - 3, 103)] + inner[::-1] + [(vx - 3, 101)]
    d.polygon([(round(x), round(y)) for x, y in pts], fill=C(WHITE), outline=C(shade(WHITE, 0.55)))
    for k in range(1, 12):                                          # 上面亮、下面暗
        p, q = outer[k], inner[k]
        line(d, (round(p[0]), round(p[1]) + 1, round(p[0] + (q[0] - p[0]) * 0.35), round(p[1] + (q[1] - p[1]) * 0.35)), WHITE_L)
        line(d, (round(q[0] + (p[0] - q[0]) * 0.3), round(q[1] + (p[1] - q[1]) * 0.3), round(q[0]), round(q[1]) - 1),
             shade(WHITE, 0.74))
    d.ellipse((mouth_x - 6, 82, mouth_x - 1, 104), fill=C((150, 54, 46)), outline=C(shade(WHITE, 0.6)))   # 喇叭口（侧看是一条窄椭圆）
    d.ellipse((mouth_x - 4, 86, mouth_x - 2, 100), fill=C((104, 38, 34)))
    d.arc((mouth_x - 6, 82, mouth_x - 1, 104), 110, 250, fill=C(WHITE_L))
    a = arr(im)
    m = box_mask((262, 80, 304, 142))
    rust_streaks(a, (262, 84, 304, 142), 14, 371, amax=0.42, lmin=3, lmax=11, mask=m)
    pitting(a, (262, 84, 304, 142), 30, 372, mask=m, f=0.45)
    return img(a)


def _container(d, x0, y0, x1, y1, col, label=None):
    """集装箱长边：波纹、上下梁、角件、门端锁杆（右端）、喷字。返回字的框（给锈避开）。"""
    rect(d, (x0, y0, x1, y1), col, shade(col, 0.45))
    for x in range(x0 + 3, x1 - 2):
        c = shade(col, (1.1, 1.0, 0.82, 0.92)[(x - x0) % 4])
        line(d, (x, y0 + 3, x, y1 - 3), c)
    for (ya, yb) in ((y0, y0 + 2), (y1 - 2, y1)):
        rect(d, (x0, ya, x1, yb), shade(col, 0.88))
        line(d, (x0, ya, x1, ya), shade(col, 1.22))
    for (cx, cy) in ((x0, y0), (x1 - 3, y0), (x0, y1 - 3), (x1 - 3, y1 - 3)):
        rect(d, (cx, cy, cx + 3, cy + 3), shade(col, 0.6))
        px(d, cx + 1, cy + 1, (32, 30, 30))
    for xx in (x1 - 7, x1 - 4):                                     # 门端（右边）：两根锁杆
        line(d, (xx, y0 + 3, xx, y1 - 3), shade(col, 0.6))
        rect(d, (xx - 1, (y0 + y1) // 2 - 1, xx + 1, (y0 + y1) // 2 + 1), shade(col, 0.5))
    if label:
        text3(d, x0 + 6, y0 + 6, label[0], (222, 222, 214))
        text3(d, x0 + 6, y0 + 13, label[1], (208, 208, 200))
        return (x0 + 5, y0 + 5, x0 + 6 + text_w(label[0]) + 1, y0 + 18)
    return (x0, y0, x0, y0)


def _hatch_containers(im):
    """货舱口（围板 + 舱盖）、集装箱（左两层、右一层）、绑扎杆、吊车立柱。"""
    d = ImageDraw.Draw(im)
    hx0, hx1 = HATCH
    conts = [(306, 80, 362, 120, (144, 76, 60), ('TRLU', '2046')), (310, 40, 358, 80, (72, 116, 114), ('NOSU', '7731')),
             (396, 80, 450, 120, (70, 92, 124), ('SPWU', '0388'))]
    labels = [_container(d, *c[:5], label=c[5]) for c in conts]
    for x in (311, 355):                                            # 两层之间的扭锁
        rect(d, (x, 79, x + 2, 81), (42, 42, 46))
    a = arr(im)                                                     # 集装箱的锈：顶梁 / 角件往下流、锈点、凹痕
    for i, (x0, y0, x1, y1, col, _) in enumerate(conts):
        keep = box_mask((x0 + 1, y0 + 1, x1 - 1, y1 - 1)) & ~box_mask(labels[i])
        starts = [(int(hrange(x0 + 2, x1 - 2, i, k, 381)), y0 + 3) for k in range(16)]
        starts += [(x0 + 1, y0 + 4), (x1 - 2, y0 + 4)]
        rust_streaks(a, (x0, y0, x1, y1), 0, 382 + i, starts=starts, amax=0.42, lmin=3, lmax=18, mask=keep)
        pitting(a, (x0 + 1, y0 + 2, x1 - 1, y1 - 1), 40, 385 + i, mask=keep, f=0.45)
        rust_band(a, (x0 + 1, y0, x1 - 1, y1 - 1), 4, 388 + i, mask=keep, f=0.4)
        dx_ = int(hrange(x0 + 10, x1 - 16, i, 389))                 # 一处凹痕（几根波纹压暗）
        a[y0 + 14:y0 + 26, dx_:dx_ + 6, :3] *= 0.9
    im = img(a)
    d = ImageDraw.Draw(im)
    pc = PED_X                                                      # 吊车立柱（从舱盖后面升上来）
    cyl_v(d, pc - 9, pc + 9, 54, 121, YEL)
    hazard(d, (pc - 9, 54, pc + 9, 57), step=3)
    rect(d, (pc - 12, 52, pc + 12, 53), (98, 98, 100))             # 平台 + 栏杆
    line(d, (pc - 12, 52, pc + 12, 52), (158, 158, 160))
    for xx in range(pc - 12, pc + 13, 6):
        line(d, (xx, 46, xx, 51), (122, 122, 126))
    line(d, (pc - 12, 46, pc + 12, 46), (152, 152, 156))
    for yy in range(60, 120, 4):                                    # 爬梯
        line(d, (pc - 3, yy, pc + 1, yy), shade(YEL, 0.62))
    line(d, (pc - 4, 58, pc - 4, 120), shade(YEL, 0.7))
    line(d, (pc + 2, 58, pc + 2, 120), shade(YEL, 0.7))
    rect(d, (pc + 4, 92, pc + 8, 98), (198, 198, 188))             # 铭牌
    line(d, (pc + 5, 94, pc + 7, 94), (62, 62, 62))
    rivets_v(d, pc - 7, 60, 118, 6, YEL)
    a = arr(im)
    m = box_mask((pc - 9, 58, pc + 9, 121))
    rust_streaks(a, (pc - 9, 58, pc + 9, 121), 0, 391, starts=[(int(hrange(pc - 8, pc + 8, i, 392)), int(hrange(58, 100, i, 393)))
                                                               for i in range(14)], amax=0.45, lmin=4, lmax=18, mask=m)
    pitting(a, (pc - 9, 58, pc + 9, 120), 30, 394, mask=m, f=0.45)
    im = img(a)
    d = ImageDraw.Draw(im)
    top = shade(EQ, 1.14)                                           # 舱盖顶面（y 118–126）
    rect(d, (hx0, 118, hx1, 126), top)
    line(d, (hx0, 118, hx1, 118), shade(EQ, 0.9))
    for yy in (121, 124):
        line(d, (hx0, yy, hx1, yy), shade(EQ, 1.0))
    for xx in range(hx0 + 30, hx1, 37):
        line(d, (xx, 118, xx, 126), shade(EQ, 0.8))
        line(d, (xx + 1, 118, xx + 1, 126), shade(EQ, 1.25))
    for (xa, ya, xb, yb) in ((308, 112, 318, 126), (360, 112, 350, 126), (398, 112, 408, 126), (448, 112, 438, 126)):
        line(d, (xa, ya, xb, yb), (150, 150, 146))                  # 绑扎杆
        px(d, (xa + xb) // 2, (ya + yb) // 2, (190, 190, 186))
    for y in range(126, 143):                                       # 舱口围板（近侧立面 y 126–142）
        u = (y - 126) / 16.0
        line(d, (hx0, y, hx1, y), mx(shade(EQ, 1.02), shade(EQ, 0.8), u))
    hazard(d, (hx0, 126, hx1, 127), step=4)
    for xx in range(hx0 + 8, hx1, 16):                              # 肘板
        line(d, (xx, 128, xx, 141), shade(EQ, 1.14))
        line(d, (xx + 1, 128, xx + 1, 141), shade(EQ, 0.74))
    for xx in range(hx0 + 4, hx1, 20):                              # 压紧扣
        rect(d, (xx, 128, xx + 2, 131), shade(EQ, 0.62))
        px(d, xx + 1, 128, shade(EQ, 1.3))
    for yy in range(129, 142, 3):                                   # 小梯子
        line(d, (hx0 + 3, yy, hx0 + 7, yy), (150, 152, 148))
    rivets_h(d, hx0 + 2, hx1 - 2, 140, 4, shade(EQ, 0.84))
    line(d, (hx0, 142, hx1, 142), shade(EQ, 0.56))
    a = arr(im)
    m = box_mask((hx0, 118, hx1, 142))
    rust_streaks(a, (hx0, 118, hx1, 142), 0, 395, starts=[(int(hrange(hx0, hx1, i, 396)), 128) for i in range(34)],
                 amax=0.42, lmin=3, lmax=12, mask=m)
    pitting(a, (hx0, 118, hx1, 142), 90, 397, mask=m, f=0.45)
    rust_band(a, (hx0, 126, hx1, 141), 4, 398, mask=m, f=0.45)
    im = img(a)
    tex(im, (hx0, 40, hx1 + 1, 143), 0.04, 399)
    return im


def _booth(im):
    """通往货舱的小门楼：门敞着、门里黑，看得见往下的楼梯和扶手；门扇贴在右边墙上；No.2 HOLD 牌、消防箱、通风帽。"""
    x0, y0, x1, y1 = BOOTH
    d = ImageDraw.Draw(im)
    mushroom(d, 461, y0 - 3, h=6, col=WHITE)
    for y in range(y0, y1 + 1):
        u = (y - y0) / float(y1 - y0)
        line(d, (x0, y, x1, y), mx(shade(WHITE, 0.98), shade(WHITE, 0.84), u ** 1.3))
    rect(d, (x0 - 2, y0 - 3, x1 + 2, y0 - 1), shade(WHITE, 0.9))
    line(d, (x0 - 2, y0 - 3, x1 + 2, y0 - 3), WHITE_L)
    line(d, (x0, y0, x1, y0), shade(WHITE, 0.72))
    line(d, (x0, y0, x0, y1), WHITE_L)
    line(d, (x1, y0, x1, y1), shade(WHITE, 0.68))
    rect(d, (x0, y1 - 6, x1, y1), (84, 96, 88))
    for xx in (x0 + 2, x1 - 2):
        rivets_v(d, xx, y0 + 4, y1 - 8, 4, shade(WHITE, 0.94))
    hx0, hy0, hx1, hy1 = H_DOOR                                     # 门洞：里面黑，往下的楼梯 + 扶手
    hazard(d, (hx0 - 2, hy0 - 2, hx1 + 2, hy0 - 1), step=3)
    rect(d, (hx0 - 2, hy0, hx0 - 1, hy1), HAZ_Y)
    rect(d, (hx1 + 1, hy0, hx1 + 2, hy1), HAZ_Y)
    for y in range(hy0, hy1 + 1):
        u = (y - hy0) / float(hy1 - hy0)
        line(d, (hx0, y, hx1, y), mx((42, 42, 48), (22, 20, 26), u))
    for k, yy in enumerate((hy1 - 2, hy1 - 6, hy1 - 10, hy1 - 14)):  # 台阶（往下、往里）
        c = mx((98, 96, 94), (38, 36, 40), k / 3.5)
        line(d, (hx0 + 1 + k, yy, hx1 - 1 - k, yy), c)
        line(d, (hx0 + 1 + k, yy + 1, hx1 - 1 - k, yy + 1), shade(c, 0.6))
    line(d, (hx0 + 2, hy0 + 14, hx0 + 9, hy1 - 3), (90, 88, 86))   # 扶手
    line(d, (hx0 + 2, hy0 + 15, hx0 + 2, hy1 - 2), (66, 64, 64))
    rect(d, (hx0 - 2, hy1 - 3, hx1 + 2, hy1), (96, 100, 96))        # 门槛
    line(d, (hx0 - 2, hy1 - 3, hx1 + 2, hy1 - 3), (152, 156, 150))
    d.polygon([(hx1 + 3, hy0 + 1), (x1 - 1, hy0 + 3), (x1 - 1, hy1 - 2), (hx1 + 3, hy1 - 3)], fill=C((168, 174, 166)),
              outline=C((96, 100, 96)))                              # 门扇：贴在右边墙上
    line(d, (hx1 + 4, hy0 + 3, hx1 + 4, hy1 - 5), (200, 204, 196))
    for yy in (hy0 + 8, hy0 + 20, hy0 + 32):
        line(d, (x1 - 6, yy, x1 - 3, yy), (66, 68, 66))
    sign = plate(d, (hx0 + hx1) // 2, 96, 'NO.2 HOLD')
    rect(d, (x0 + 2, 112, x0 + 8, 126), (172, 50, 44), (90, 26, 24))   # 消防箱（左墙）
    line(d, (x0 + 3, 113, x0 + 7, 113), (210, 98, 88))
    rect(d, (x0 + 4, 118, x0 + 6, 121), (226, 220, 210))
    a = arr(im)
    keep = box_mask((x0, y0, x1, y1)) & ~box_mask((hx0 - 2, hy0 - 2, x1, hy1)) & ~box_mask(sign) & ~box_mask((x0 + 2, 112, x0 + 8, 126))
    starts = [(int(hrange(x0, x1, i, 401)), y0 + 2) for i in range(12)] + [(hx0 - 3, hy0 + 1), (sign[0], sign[3] + 1)]
    rust_streaks(a, (x0, y0, x1, y1), 0, 403, starts=starts, amax=0.45, lmin=4, lmax=18, mask=keep)
    pitting(a, (x0, y0 + 2, x1, y1 - 6), 40, 404, mask=keep, f=0.45)
    blisters(a, (x0, y0 + 2, x1, y1 - 7), 405, thr=0.84, mask=keep, f=0.45)
    rust_band(a, (x0, y0, x1, y1), 5, 406, mask=box_mask((x0, y1 - 7, x1, y1)) & ~box_mask((hx0 - 2, hy0, hx1 + 2, hy1)), f=0.5)
    im = img(a)
    tex(im, (x0, y0, x1 + 1, y1 + 1), 0.035, 407)
    return im


def _deck_bits(im):
    """散在甲板上的小东西：缆桩、蘑菇头通风筒、测深管帽、消防栓。"""
    d = ImageDraw.Draw(im)
    bitts(d, 500, 141, h=8)
    mushroom(d, 6, BW_BASE + 6, h=6, col=WHITE)
    for x in (148, 438):                                            # 测深管帽（黄铜）
        d.ellipse((x - 2, 143, x + 2, 145), fill=C((150, 128, 76)), outline=C((92, 76, 42)))
        px(d, x - 1, 143, (196, 176, 120))
    hx = 507                                                        # 消防栓
    cyl_v(d, hx - 2, hx + 2, 120, 138, (168, 52, 46))
    rect(d, (hx - 4, 124, hx + 4, 126), (146, 44, 40))
    d.ellipse((hx - 3, 117, hx + 3, 121), fill=C((186, 62, 54)), outline=C((90, 26, 24)))
    rect(d, (hx - 4, 137, hx + 4, 139), (90, 92, 94), INK)
    return im


@lru_cache(maxsize=1)
def deck_layer():
    """甲板层（pano k 1，640 宽）：上面是透明的（透出远景的天和海），舷墙及以下全不透明。"""
    im = A._new(PW, H)
    for fn in (_floor, _bulwark, _gangway, _foremast, _galley, _winch, _cage_back, _vents_drums, _hatch_containers,
               _booth, _deck_bits):
        im = fn(im)
    a = arr(im)
    veil(a, 20, 118, 0.2)                                          # 越高越淡（雾）
    return grade(img(a))


# ============================================================ 吊车上半截（pick key crane）
def _jib(d, foot, tip, wf=7, wt=3):
    """桁架吊臂：上下弦 + 之字斜撑；吊臂头的警示斑马 + 滑轮；根部铰座。"""
    fx, fy = foot
    tx, ty = tip
    L = math.hypot(tx - fx, ty - fy)
    ux, uy = (tx - fx) / L, (ty - fy) / L
    nx, ny = -uy, ux
    if ny > 0:
        nx, ny = -nx, -ny                                          # 法线朝上

    def P(s, side):
        w = wf + (wt - wf) * s
        return (fx + ux * L * s + nx * w / 2 * side, fy + uy * L * s + ny * w / 2 * side)
    n = int(L // 7)
    for i in range(n):                                             # 斜撑
        a0, b1, a2 = P(i / float(n), 1), P((i + 0.5) / n, -1), P((i + 1) / float(n), 1)
        line(d, (round(a0[0]), round(a0[1]), round(b1[0]), round(b1[1])), YEL_D)
        line(d, (round(b1[0]), round(b1[1]), round(a2[0]), round(a2[1])), shade(YEL, 0.86))
    for side, col in ((1, YEL_L), (-1, YEL_D)):                    # 上弦 / 下弦
        p0, p1 = P(0, side), P(1, side)
        line(d, (round(p0[0]), round(p0[1]), round(p1[0]), round(p1[1])), col)
    p0, p1 = P(0, 1), P(1, 1)
    line(d, (round(p0[0] - nx), round(p0[1] - ny), round(p1[0] - nx), round(p1[1] - ny)), YEL)
    for k in range(6):                                             # 吊臂头：警示斑马
        q = P(1 - k / L, 0)
        q2 = P(1 - k / L, 0.6)
        c = HAZ_Y if (k // 2) % 2 == 0 else HAZ_K
        d.point((round(q[0]), round(q[1])), fill=C(c))
        d.point((round(q2[0]), round(q2[1])), fill=C(c))
    d.ellipse((tx - 2, ty - 1, tx + 2, ty + 3), fill=C((72, 72, 76)), outline=C(INK))
    px(d, tx, ty + 1, (152, 152, 156))
    d.ellipse((fx - 3, fy - 3, fx + 3, fy + 3), fill=C(shade(YEL, 0.8)), outline=C(INK))
    px(d, fx, fy, (42, 42, 42))


def _crane_house(d, side):
    """回转房：机器房（百叶）+ 司机室（在吊臂那一侧：side −1 左、+1 右）+ 配重 + A 字架。返回 (吊臂根, A 字架顶)。"""
    pc = PED_X
    x0, x1, y0, y1 = pc - 22, pc + 22, 30, 52
    rect(d, (pc - 10, 51, pc + 10, 54), (72, 72, 76))               # 回转支承
    line(d, (pc - 10, 51, pc + 10, 51), (132, 132, 136))
    rect(d, (x0, y0, x1, y1), YEL, shade(YEL, 0.45))
    for y in range(y0 + 1, y1):
        u = (y - y0) / float(y1 - y0)
        line(d, (x0 + 1, y, x1 - 1, y), mx(shade(YEL, 1.06), shade(YEL, 0.84), u))
    line(d, (x0, y0, x1, y0), YEL_L)
    line(d, (x0 + 1, y0 + 1, x0 + 1, y1 - 1), shade(YEL, 1.12))
    cx0, cx1 = (x0, x0 + 15) if side < 0 else (x1 - 15, x1)        # 司机室
    rect(d, (cx0, y0 - 2, cx1, y1), shade(YEL, 0.96), shade(YEL, 0.45))
    line(d, (cx0, y0 - 2, cx1, y0 - 2), YEL_L)
    wx0, wx1 = (cx0 + 2, cx1 - 3) if side < 0 else (cx0 + 3, cx1 - 2)
    rect(d, (wx0, y0 + 2, wx1, y0 + 10), (60, 76, 86), (42, 42, 46))
    line(d, (wx0 + 1, y0 + 3, wx1 - 2, y0 + 3), (138, 152, 160))
    px(d, wx0 + 1, y0 + 4, (178, 190, 196))
    line(d, ((wx0 + wx1) // 2, y0 + 2, (wx0 + wx1) // 2, y0 + 10), (42, 42, 46))
    rect(d, (wx0, y0 + 13, wx1, y0 + 19), shade(YEL, 0.84))         # 司机室门
    px(d, wx1 - 1 if side < 0 else wx0 + 1, y0 + 16, (62, 62, 62))
    mx0, mx1 = (cx1 + 3, x1 - 7) if side < 0 else (x0 + 7, cx0 - 3)   # 机器房百叶
    for y in range(y0 + 4, y1 - 4, 2):
        line(d, (mx0, y, mx1, y), shade(YEL, 0.7))
    kx0, kx1 = (x1 - 6, x1) if side < 0 else (x0, x0 + 6)          # 配重 + 警示纹
    rect(d, (kx0, y0 + 2, kx1, y1), (62, 62, 66))
    hazard(d, (kx0, y1 - 5, kx1, y1), step=2)
    ax = pc + 12 * (-side)                                         # A 字架
    for (bx_, col) in ((ax - 6, shade(YEL, 0.95)), (ax + 6, shade(YEL, 0.75))):
        line(d, (bx_, y0, ax, 14), col, width=2)
    d.ellipse((ax - 2, 12, ax + 2, 16), fill=C((72, 72, 76)), outline=C(INK))
    foot = (x0 + 6, y1 - 4) if side < 0 else (x1 - 6, y1 - 4)
    return foot, (ax, 14)


CRANE_STATES = {0: dict(side=-1, tip=(266, 4), hook_y=58), 1: dict(side=1, tip=(478, 12), hook_y=72)}


def crane_img(state):
    """吊车上半截（透明底）：0 = 吊臂朝左（吊钩挂在铁笼上空），1 = 转到朝右（吊钩挂在货舱门上空）。"""
    st = CRANE_STATES[state]
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    foot, top = _crane_house(d, st['side'])
    tx, ty = st['tip']
    for o in (0, 1):                                               # 变幅钢缆（A 字架顶 → 吊臂头），两根
        line(d, (top[0], top[1] + o, tx + (2 if st['side'] < 0 else -2), ty + o), (68, 68, 72))
    _jib(d, foot, (tx, ty))
    hy = st['hook_y']                                              # 起升钢缆 + 吊钩组
    line(d, (tx, ty + 3, tx, hy), (58, 58, 62))
    line(d, (tx + 1, ty + 3, tx + 1, hy), (98, 98, 102))
    rect(d, (tx - 3, hy, tx + 3, hy + 6), YEL, INK)
    hazard(d, (tx - 2, hy + 4, tx + 2, hy + 5), step=2)
    line(d, (tx - 2, hy + 1, tx + 2, hy + 1), YEL_L)
    line(d, (tx, hy + 7, tx, hy + 8), (82, 82, 86))
    d.arc((tx - 3, hy + 8, tx + 3, hy + 14), 0, 270, fill=C((98, 100, 104)), width=2)
    px(d, tx + 2, hy + 9, (152, 152, 158))
    a = arr(im)
    m = a[..., 3] > 0
    rust_streaks(a, CRANE_BOX, 26, 411 + state, amax=0.4, lmin=2, lmax=7, mask=m)
    pitting(a, CRANE_BOX, 70, 413 + state, mask=m, f=0.4)
    veil(a, 0, 118, 0.2)
    return grade(img(a))


# ============================================================ 上层建筑（单独一层，盖在吊臂前面）
SUP_DECKS = dict(A=(100, 142), B=(64, 100), C=(36, 64), top=(26, 36))


def _lifeboat(d, x0, y0, x1, y1):
    """救生艇（侧看，船头朝左）：橙色艇身（弯的龙骨线）、白色篷布 + 绑绳、舷边的扶手绳、艇名。"""
    Lw = x1 - x0
    top = y0 + 6                                                    # 舷边（篷布下沿）

    def sheer(x):                                                   # 舷边：船头（左）翘起 3 px、船尾翘 1 px
        u = (x - x0) / float(Lw)
        return top - 3 * max(0.0, 1 - u / 0.18) ** 1.5 - 1 * max(0.0, (u - 0.88) / 0.12)

    def keel(x):                                                    # 龙骨：中间最低，船头弯上去、船尾圆
        u = (x - x0) / float(Lw)
        return y1 - 1 - 7 * max(0.0, 1 - u / 0.22) ** 2 - 5 * max(0.0, (u - 0.84) / 0.16) ** 2
    up = [(x, sheer(x)) for x in range(x0, x1 + 1)]
    dn = [(x, keel(x)) for x in range(x1, x0 - 1, -1)]
    d.polygon([(round(x), round(y)) for x, y in up + dn], fill=C(ORANGE), outline=C(shade(ORANGE, 0.48)))
    for x in range(x0 + 1, x1):                                     # 圆鼓鼓的艇身：上亮、下暗
        ya, yb = round(sheer(x)) + 1, round(keel(x)) - 1
        for y in range(ya, yb + 1):
            u = (y - ya) / float(max(1, yb - ya))
            if u < 0.18:
                d.point((x, y), fill=C(shade(ORANGE, 1.18)))
            elif u > 0.62:
                d.point((x, y), fill=C(shade(ORANGE, 0.8 if u < 0.85 else 0.66)))
    for x in range(x0 + 2, x1 - 1):                                 # 护舷条
        px(d, x, round(sheer(x)) + 3, shade(ORANGE, 0.6))
    for k in range(5):                                              # 扶手绳（一段段垂下来）
        xa = x0 + 6 + k * 9
        curve(d, (xa, round(sheer(xa)) + 4), (xa + 9, round(sheer(xa + 9)) + 4), 1, (230, 222, 202), n=8)
    text3(d, x0 + 8, top + 7, 'NO.1', (60, 40, 32))
    d.rounded_rectangle((x0 + 5, y0, x1 - 4, top), radius=3, fill=C((206, 206, 196)), outline=C((128, 128, 122)))   # 篷布
    for xx in range(x0 + 10, x1 - 5, 7):
        line(d, (xx, y0 + 1, xx, top - 1), (176, 176, 168))
    line(d, (x0 + 7, y0 + 1, x1 - 7, y0 + 1), (230, 230, 222))


@lru_cache(maxsize=1)
def super_layer():
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x0, x1 = SUP_X0, PW
    yA0, yA1 = SUP_DECKS['A']
    yB0, yB1 = SUP_DECKS['B']
    yC0, yC1 = SUP_DECKS['C']
    yT0, yT1 = SUP_DECKS['top']
    # 烟囱（在驾驶台后面，往后斜）：黑顶、红带 + 白菱形、浅黄身
    fx0, fx1 = 598, 636
    for y in range(4, 41):
        u = (y - 4) / 36.0
        xa, xb = round(fx0 + 4 - 4 * u), round(fx1 + 4 - 4 * u)
        for x in range(xa, xb + 1):
            v = (x - xa) / float(max(1, xb - xa))
            c = (46, 44, 46) if y < 10 else (160, 58, 48) if 14 <= y <= 21 else (184, 160, 112)
            d.point((x, y), fill=C(shade(c, 1.12 - 0.42 * v)))
    cx, cy = fx0 + 18, 17
    d.polygon([(cx, cy - 3), (cx + 3, cy), (cx, cy + 3), (cx - 3, cy)], fill=C((226, 224, 216)))
    for ex_ in (fx0 + 10, fx0 + 22):                               # 排气管口
        rect(d, (ex_ + 3, 0, ex_ + 6, 4), (62, 60, 62))
    line(d, (fx0 + 4, 4, fx1 + 4, 4), (92, 88, 88))
    line(d, (fx0 + 3, 11, fx1 + 3, 11), (204, 196, 170))
    # 主体三层 + 顶层
    for (ya, yb, xa) in ((yA0, yA1, x0), (yB0, yB1 - 1, x0 + 6), (yC0, yC1 - 1, x0 + 2), (yT0, yT1 - 1, x0 + 30)):
        for y in range(ya, yb + 1):
            u = (y - ya) / float(max(1, yb - ya))
            line(d, (xa, y, x1, y), mx(shade(WHITE, 1.0), shade(WHITE, 0.86), u ** 1.3))
        line(d, (xa, ya, xa, yb), WHITE_L)
        for xx in range(xa + 24, x1, 32):                          # 竖向板缝 + 铆钉
            line(d, (xx, ya + 2, xx, yb - 1), shade(WHITE, 0.9))
            rivets_v(d, xx + 1, ya + 3, yb - 2, 4, shade(WHITE, 0.95))
    for (y, xa) in ((yA0 - 1, x0 - 2), (yB0 - 1, x0 + 2), (yC0 - 1, x0 - 14), (yT0 - 1, x0 + 28)):   # 甲板边 + 影子
        rect(d, (xa, y - 2, x1, y), shade(WHITE, 0.94))
        line(d, (xa, y - 2, x1, y - 2), WHITE_L)
        line(d, (xa, y + 1, x1, y + 1), shade(WHITE, 0.66))
        line(d, (xa, y + 2, x1, y + 2), shade(WHITE, 0.8))
    # 驾驶台翼（往左伸出去）+ 栏杆 + 绿色舷灯
    rect(d, (x0 - 14, yC0 + 18, x0 + 2, yC0 + 20), shade(WHITE, 0.9))
    for xx in range(x0 - 14, x0 + 3, 5):
        line(d, (xx, yC0 + 6, xx, yC0 + 18), (150, 152, 148))
    line(d, (x0 - 14, yC0 + 6, x0 + 2, yC0 + 6), (186, 188, 182))
    line(d, (x0 - 14, yC0 + 12, x0 + 2, yC0 + 12), (150, 152, 148))
    rect(d, (x0 - 13, yC0 + 13, x0 - 9, yC0 + 17), (62, 66, 62))
    px(d, x0 - 11, yC0 + 15, (96, 206, 124))
    # 驾驶台一排窗（深色玻璃反着雾，第 7 扇亮着灯——没有人，灯却开着）
    wins = []
    for i, wx in enumerate(range(x0 + 8, x1 - 4, 11)):
        rect(d, (wx, yC0 + 5, wx + 8, yC0 + 15), (66, 84, 94), (46, 48, 52))
        line(d, (wx + 1, yC0 + 6, wx + 7, yC0 + 6), (152, 166, 172))
        line(d, (wx + 1, yC0 + 7, wx + 3, yC0 + 7), (120, 136, 144))
        if i == 6:
            rect(d, (wx + 1, yC0 + 8, wx + 7, yC0 + 14), (204, 176, 120))
        wins.append((wx, yC0 + 5, wx + 8, yC0 + 15))
    rect(d, (x0 + 2, yC0 + 1, x1, yC0 + 3), shade(WHITE, 0.62))     # 遮阳檐
    # 顶层（罗经甲板）：栏杆、雷达桅（雷达在 strip 里转）、信号灯横杆、天线、探照灯
    for xx in range(x0 + 30, x1, 6):
        line(d, (xx, yT0 - 7, xx, yT0 - 3), (150, 152, 148))
    line(d, (x0 + 30, yT0 - 7, x1, yT0 - 7), (186, 188, 182))
    cyl_v(d, RADAR_X - 1, RADAR_X + 1, RADAR_Y + 3, yT0 - 3, (178, 180, 174))
    rect(d, (RADAR_X - 8, 20, RADAR_X + 8, 21), (160, 162, 158))
    for lx in (RADAR_X - 7, RADAR_X + 6):
        rect(d, (lx - 1, 22, lx + 1, 24), (62, 62, 66))
        px(d, lx, 23, (214, 206, 182))
    for ax_ in (586, 592):
        line(d, (ax_, 2, ax_, yT0 - 3), (112, 112, 116))
    rect(d, (548, yT0 - 6, 553, yT0 - 3), (92, 94, 98))
    d.ellipse((546, yT0 - 7, 550, yT0 - 3), fill=C((208, 208, 200)), outline=C((82, 82, 86)))
    # B 层：舷窗一排 + 吊艇架 + 救生艇
    for wx in range(x0 + 70, x1 - 6, 14):
        d.ellipse((wx - 3, yB0 + 10, wx + 3, yB0 + 16), fill=C((150, 148, 142)))
        d.ellipse((wx - 2, yB0 + 11, wx + 2, yB0 + 15), fill=C((72, 88, 98)))
        px(d, wx - 1, yB0 + 12, (172, 184, 190))
    dav = (x0 + 10, x0 + 52)
    for dx_ in dav:                                                # 吊艇架（弯臂，根在 B 层甲板上）
        for k in range(18):
            s = k / 17.0
            x = dx_ - round(7 * math.sin(s * math.pi * 0.5))
            y = yB1 - 3 - k * 2
            rect(d, (x, y, x + 2, y + 1), (126, 132, 130))
            px(d, x, y, (176, 182, 180))
            px(d, x + 2, y + 1, (82, 86, 86))
            px(d, x - 1, y, (70, 74, 74))
        rect(d, (dx_ - 2, yB1 - 4, dx_ + 4, yB1 - 1), (110, 114, 112), INK)
        d.ellipse((dx_ - 9, yB1 - 39, dx_ - 4, yB1 - 34), fill=C((96, 100, 100)), outline=C(INK))   # 架子头的滑轮
    _lifeboat(d, x0 + 2, yB0 + 6, x0 + 54, yB0 + 24)
    for dx_ in dav:                                                # 吊艇索（从架子头垂到艇上）
        line(d, (dx_ - 6, yB1 - 37, dx_ - 6, yB0 + 7), (82, 82, 86))
        rect(d, (dx_ - 7, yB0 + 3, dx_ - 5, yB0 + 6), (70, 70, 74))
    for xx in range(x0 + 6, x1, 7):                                # B 层外走道的栏杆（A 层屋顶边上）
        line(d, (xx, yA0 - 10, xx, yA0 - 3), (150, 152, 148))
    line(d, (x0 + 6, yA0 - 10, x1, yA0 - 10), (190, 192, 186))
    line(d, (x0 + 6, yA0 - 6, x1, yA0 - 6), (150, 152, 148))
    # A 层（主甲板）：外楼梯、舷窗、救生圈、两扇门
    for k in range(12):
        y = yA1 - 3 - k * 4
        xa = x0 + 6 + k * 2
        line(d, (xa, y, xa + 7, y), (152, 154, 150))
        line(d, (xa, y + 1, xa + 7, y + 1), (112, 114, 110))
    line(d, (x0 + 4, yA1 - 12, x0 + 30, yA0 - 8), (178, 180, 174))
    line(d, (x0 + 4, yA1 - 1, x0 + 4, yA1 - 12), (152, 154, 150))
    ports = (544, 586, 634)
    for wx in ports:
        d.ellipse((wx - 4, 112, wx + 4, 120), fill=C((156, 138, 100)))
        d.ellipse((wx - 3, 113, wx + 3, 119), fill=C((72, 88, 98)))
        px(d, wx - 2, 114, (172, 184, 190))
    lifebuoy(d, 540, 131, r=6)
    bx0, by0, bx1, by1 = B_DOOR                                    # 舰桥门（敞着：门扇贴在左墙，门里是往上的楼梯）
    rect(d, (bx0 - 1, by0 - 1, bx1 + 1, by1), (110, 112, 108))
    for y in range(by0, by1 - 2):
        u = (y - by0) / float(by1 - by0)
        line(d, (bx0, y, bx1, y), mx((66, 64, 66), (40, 38, 42), u))
    for k in range(7):
        y = by1 - 5 - k * 5
        xa = bx0 + 2 + k * 2
        line(d, (xa, y, bx1 - 1, y), mx((126, 122, 116), (72, 70, 70), k / 6.0))
        line(d, (xa, y + 1, bx1 - 1, y + 1), (48, 46, 48))
    line(d, (bx0 + 1, by1 - 10, bx1 - 2, by0 + 6), (112, 110, 106))
    d.polygon([(bx0 - 9, by0 + 2), (bx0 - 2, by0), (bx0 - 2, by1 - 3), (bx0 - 9, by1 - 2)], fill=C((168, 176, 168)),
              outline=C((96, 100, 96)))
    for yy in (by0 + 8, by0 + 20):
        line(d, (bx0 - 8, yy, bx0 - 6, yy), (66, 68, 66))
    rect(d, (bx0 - 1, by1 - 3, bx1 + 1, by1), (96, 102, 96))
    line(d, (bx0 - 1, by1 - 3, bx1 + 1, by1 - 3), (152, 156, 150))
    sign_b = plate(d, (bx0 + bx1) // 2, 99, 'BRIDGE ^')
    lx0, ly0, lx1, ly1 = L_DOOR                                    # 办公室门（敞着：灯下的台子上摊着航海日志）
    rect(d, (lx0 - 1, ly0 - 1, lx1 + 1, ly1), (110, 112, 108))
    for y in range(ly0, ly1 - 2):
        u = (y - ly0) / float(ly1 - ly0)
        line(d, (lx0, y, lx1, y), mx((98, 88, 74), (60, 54, 48), u))
    rect(d, (lx0 + 2, ly0 + 4, lx0 + 11, ly0 + 11), (168, 160, 132), (92, 82, 66))   # 墙上的海图
    line(d, (lx0 + 3, ly0 + 7, lx0 + 10, ly0 + 9), (112, 132, 142))
    line(d, (lx0 + 4, ly0 + 9, lx0 + 6, ly0 + 6), (150, 110, 80))
    d.ellipse((lx1 - 9, ly0 + 3, lx1 - 3, ly0 + 9), fill=C((202, 192, 162)), outline=C((92, 72, 42)))   # 挂钟
    line(d, (lx1 - 6, ly0 + 6, lx1 - 6, ly0 + 4), (42, 32, 22))
    line(d, (lx1 - 6, ly0 + 6, lx1 - 4, ly0 + 6), (42, 32, 22))
    lc = (lx0 + lx1) // 2 + 1
    A._glow(im, lc, ly0 + 22, 13, 10, (255, 212, 140), 80, rings=4)
    d = ImageDraw.Draw(im)
    line(d, (lc, ly0, lc, ly0 + 11), (62, 58, 52))                  # 吊灯
    d.polygon([(lc - 4, ly0 + 15), (lc - 2, ly0 + 11), (lc + 2, ly0 + 11), (lc + 4, ly0 + 15)], fill=C((72, 94, 72)))
    line(d, (lc - 3, ly0 + 16, lc + 3, ly0 + 16), (255, 230, 172))
    rect(d, (lc - 7, ly0 + 24, lc + 7, ly0 + 26), (122, 86, 56))     # 台子（斜面）+ 腿 + 底座
    line(d, (lc - 7, ly0 + 24, lc + 7, ly0 + 24), (160, 120, 82))
    rect(d, (lc - 1, ly0 + 27, lc + 1, ly1 - 4), (98, 68, 46))
    rect(d, (lc - 5, ly1 - 4, lc + 5, ly1 - 3), (88, 62, 42))
    d.polygon([(lc - 7, ly0 + 23), (lc, ly0 + 21), (lc + 7, ly0 + 23), (lc + 7, ly0 + 24), (lc - 7, ly0 + 24)],
              fill=C((240, 234, 214)))                              # 摊开的日志
    line(d, (lc, ly0 + 21, lc, ly0 + 24), (152, 142, 122))
    for k in (2, 4, 5):
        px(d, lc - k, ly0 + 23, (92, 88, 82))
    line(d, (lc + 3, ly0 + 22, lc + 6, ly0 + 19), (42, 42, 62))      # 钢笔（墨水还没干）
    px(d, lc + 3, ly0 + 23, (30, 30, 70))
    d.polygon([(lx1 + 2, ly0), (lx1 + 9, ly0 + 2), (lx1 + 9, ly1 - 2), (lx1 + 2, ly1 - 3)], fill=C((168, 176, 168)),
              outline=C((96, 100, 96)))
    rect(d, (lx0 - 1, ly1 - 3, lx1 + 1, ly1), (96, 102, 96))
    line(d, (lx0 - 1, ly1 - 3, lx1 + 1, ly1 - 3), (152, 156, 150))
    rect(d, (x0, yA1 - 5, x1, yA1), (84, 96, 88))                  # 墙脚灰绿踢脚
    for (a0, a1) in ((bx0 - 1, bx1 + 1), (lx0 - 1, lx1 + 1)):
        rect(d, (a0, yA1 - 5, a1, yA1), (96, 102, 96))
    # 锈：每层甲板边、窗下、舷窗往下流；锈点、起泡、墙脚积锈（避开门、牌子、窗、救生艇）
    a = arr(im)
    m = a[..., 3] > 0
    protect = box_mask((bx0 - 10, by0 - 1, bx1 + 1, by1)) | box_mask((lx0 - 1, ly0 - 1, lx1 + 10, ly1)) | box_mask(sign_b) \
        | box_mask((x0 + 2, yB0, x0 + 56, yB0 + 26)) | box_mask((532, 124, 548, 138))
    for wb in wins:
        protect |= box_mask(wb)
    for wx in ports:
        protect |= box_mask((wx - 4, 112, wx + 4, 120))
    keep = m & ~protect
    starts = []
    for (y, n_, sd) in ((yA0 + 3, 26, 421), (yB0 + 3, 22, 422), (yC0 + 16, 22, 423), (yT0 + 1, 10, 424)):
        starts += [(int(hrange(x0, x1, i, sd)), y) for i in range(n_)]
    starts += [(wx - 1, 121) for wx in ports] + [(wx + 1, yB0 + 17) for wx in range(x0 + 70, x1 - 6, 14)]
    starts += [(wb[0] + 1, wb[3] + 1) for wb in wins[::2]]
    rust_streaks(a, (x0 - 16, 0, x1, yA1), 0, 425, starts=starts, amax=0.42, lmin=4, lmax=20, mask=keep)
    pitting(a, (x0, yT0, x1, yA1 - 6), 220, 426, mask=keep, f=0.42)
    blisters(a, (x0, yC0, x1 - 1, yA1 - 6), 427, thr=0.84, mask=keep, f=0.42)
    for (ya, yb) in ((yA0, yA1 - 5), (yB0, yB1 - 1), (yC0, yC1 - 1)):
        rust_band(a, (x0, ya, x1 - 1, yb), 4, 428 + ya, mask=keep, f=0.38)
    rust_band(a, (x0, yA0, x1 - 1, yA1), 5, 431, mask=box_mask((x0, yA1 - 5, x1, yA1)) & ~protect, f=0.5)
    veil(a, 0, 118, 0.24)
    im = img(a)
    tex(im, (x0, 0, x1, yA1), 0.035, 433)
    return grade(im)


# ============================================================ 前景：近侧矮栏杆
@lru_cache(maxsize=1)
def rail_layer():
    """近侧栏杆（fg，画在人前面）：上扶手 y 160–162、中间一道 y 169–170、立柱每 40 px；背光偏暗、带锈；
    两只低缆桩压在甲板沿上。只挡可走带前半（y > 160）的脚和小腿。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    dark, mid, hi = (54, 58, 64), (84, 88, 94), (136, 140, 146)
    for x in range(14, PW, 40):
        line(d, (x, 161, x, H - 1), mid)
        line(d, (x + 1, 161, x + 1, H - 1), dark)
        rect(d, (x - 2, H - 3, x + 3, H - 1), dark)
        px(d, x - 2, H - 3, mid)
    line(d, (0, 160, PW, 160), hi)
    line(d, (0, 161, PW, 161), mid)
    line(d, (0, 162, PW, 162), dark)
    line(d, (0, 169, PW, 169), mid)
    line(d, (0, 170, PW, 170), dark)
    for bx in (226, 520):
        rect(d, (bx - 2, 175, bx + 15, H - 1), (62, 64, 68))
        line(d, (bx - 1, 175, bx + 14, 175), (104, 106, 110))
        for k in (0, 9):
            cyl_v(d, bx + k, bx + k + 4, 170, 175, (72, 74, 80), hi=1.2, lo=0.6)
            rect(d, (bx + k - 1, 168, bx + k + 5, 170), (86, 88, 94))
            line(d, (bx + k - 1, 168, bx + k + 5, 168), (132, 134, 140))
    a = arr(im)
    m = a[..., 3] > 0
    ys, xs = np.nonzero(m)
    for i in range(len(xs)):
        r = hash01(int(xs[i]), int(ys[i]), 441)
        if r < 0.07:
            a[ys[i], xs[i], :3] = RUST_D if r < 0.045 else (118, 74, 50)
    return grade(img(a), 0.03)


# ============================================================ 会动的
def _puff(lay, cx, cy, r, al, col=(228, 230, 230)):
    al = int(round(al / 16.0)) * 16
    if al <= 0:
        return
    d = ImageDraw.Draw(lay)
    d.ellipse((round(cx - r), round(cy - r * 0.8), round(cx + r), round(cy + r * 0.8)), fill=C(col, al))
    if r > 2.2:
        d.ellipse((round(cx - r * 0.55), round(cy - r * 0.6), round(cx + r * 0.25), round(cy)), fill=C((244, 246, 246), min(255, al + 32)))


def steam_frame(t):
    """餐厅冒的热气（世界坐标整幅透明图）：烟道帽 5 团慢慢往上飘、往左偏、散开、变淡；门缝 3 缕贴着墙往上。
    2 s 一圈，严格闭合（每团都是 t/2 的周期函数）。"""
    T = STEAM_N / STEAM_FPS
    im = A._new(PW, H)
    for i in range(5):
        u = ((t / T) + i / 5.0) % 1.0
        cx = STACK_X - 1 + math.sin(u * math.pi * 2 + i * 1.7) * 1.6 - u * 11
        cy = 72 - u * 38
        r = 1.8 + u * 5.0
        al = 190 * (1 - u) ** 1.1 * min(1.0, u * 5 + 0.35)
        _puff(im, cx, cy, r, al)
    for i in range(3):
        u = ((t / T) + i / 3.0 + 0.17) % 1.0
        cx = G_DOOR[2] + 1 + math.sin(u * math.pi * 2 + i) * 1.0 + u * 2
        cy = G_DOOR[1] + 5 - u * 18
        r = 1.0 + u * 2.4
        al = 128 * (1 - u) * min(1.0, u * 4 + 0.3)
        _puff(im, cx, cy, r, al, col=(232, 228, 222))
    return im


def radar_frame(t):
    """雷达天线转（侧看：长条长度 ∝ |cos θ|，背面朝我们时暗）。2 s 一圈。"""
    T = RADAR_N / RADAR_FPS
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    th = (t / T) * math.tau
    hw = abs(math.cos(th)) * 10
    front = math.sin(th) > 0
    c = (188, 190, 188) if front else (122, 124, 124)
    x0, x1 = round(RADAR_X - hw), round(RADAR_X + hw)
    rect(d, (x0, RADAR_Y - 1, max(x0, x1), RADAR_Y + 1), c)
    if front:
        line(d, (x0, RADAR_Y - 1, max(x0, x1), RADAR_Y - 1), (222, 224, 222))
    rect(d, (RADAR_X - 2, RADAR_Y + 1, RADAR_X + 2, RADAR_Y + 3), (92, 94, 98))
    a = arr(im)
    veil(a, 0, 118, 0.24)
    return grade(img(a))


# ============================================================ 导出
def _png_bytes(im):
    b = io.BytesIO()
    im.save(b, 'PNG', optimize=True)
    return b.tell()


def _strength_ext():
    """猩猩 idle 两帧相对脚底锚点的外框（读 tools\\_meta\\chars.json + 图集；读不到用量好的数）。"""
    try:
        meta = json.load(open(os.path.join(TOOLS, '_meta', 'chars.json'), encoding='utf-8'))['chars']['strength']
        idx = json.load(open(os.path.join(TOOLS, '_meta', 'img_index.json'), encoding='utf-8'))
        sheet = Image.open(os.path.join(GAME, 'assets', *idx[meta['image']]['file'].split('/'))).convert('RGBA')
        cw, ch = meta['cell']
        row = meta['animations']['idle']['row']
        best = None
        for f in range(meta['animations']['idle']['frames']):
            bb = sheet.crop((f * cw, row * ch, f * cw + cw, row * ch + ch)).getbbox()
            if bb:
                best = bb if best is None else (min(best[0], bb[0]), min(best[1], bb[1]), max(best[2], bb[2]), max(best[3], bb[3]))
        px_, py_ = meta['pivot']
        return (best[0] - px_, best[1] - py_, best[2] - px_, best[3] - py_)
    except Exception:
        return (-18, -40, 19, 0)


def layers_raw():
    return dict(far=far_layer(), deck=deck_layer(), sup=super_layer(), rail=rail_layer(), fogf=fog_far(), fogl=fog_low(),
                fogh=fog_high(), crane=[crane_img(0), crane_img(1)], cage=[cage_front(0), cage_front(1)])


def export(ex, BJ):
    R = layers_raw()
    crane_imgs = [ex.img('crane%d' % i, im.crop(CRANE_BOX)) for i, im in enumerate(R['crane'])]
    cage_imgs = [ex.img('cage_front%d' % i, im.crop(CAGE_BOX)) for i, im in enumerate(R['cage'])]
    sb = R['sup'].getbbox()
    sup_c = R['sup'].crop((sb[0], 0, PW, sb[3]))
    layers = [dict(type='pano', image=ex.img('far', R['far']), k=FAR_K, x=0, y=0),
              dict(type='wrap', image=ex.img('fog_far', R['fogf']), period=R['fogf'].width, k=0.45, y=FOGF_Y, vx=2.0),
              dict(type='pano', image=ex.img('deck', R['deck']), k=1.0, x=0, y=0),
              dict(type='pick', images=crane_imgs, key='crane', x=CRANE_BOX[0], y=CRANE_BOX[1], k=1.0),
              dict(type='pano', image=ex.img('super', sup_c), k=1.0, x=sb[0], y=0),
              ex.bake('steam', STEAM_BOX, STEAM_N, STEAM_FPS, steam_frame, screen=False, k=1.0),
              ex.bake('radar', RADAR_BOX, RADAR_N, RADAR_FPS, radar_frame, screen=False, k=1.0),
              dict(type='wrap', image=ex.img('fog_low', R['fogl']), period=R['fogl'].width, k=1.0, y=FOGL_Y, vx=2.5),
              dict(type='wrap', image=ex.img('fog_high', R['fogh']), period=R['fogh'].width, k=0.7, y=FOGH_Y, vx=3.0),
              # 笼子正面放在雾后面画（离镜头最近，不该被雾罩住）；剧情的 depth 道具用同一张图，叠上去画面不变
              dict(type='pick', images=cage_imgs, key='cage_open', x=CAGE_BOX[0], y=CAGE_BOX[1], k=1.0)]
    rb = R['rail'].getbbox()
    fg = [dict(type='pano', image=ex.img('rail', R['rail'].crop((0, rb[1], PW, rb[3]))), k=1.0, x=0, y=rb[1])]
    cage_front_spec = dict(images=cage_imgs, x=CAGE_BOX[0], y=CAGE_BOX[1], depth=CAGE_DEPTH, key='cage_open')
    anchors = dict(gangway=[30, 152], galley=[110, 150], cage=[230, 152], cage_inside=list(CAGE_INSIDE),
                   cage_box=[CAGE_F[0], CAGE_F[1] + CAGE_D[1], CAGE_F[2] + CAGE_D[0], CAGE_F[3]],
                   cage_front=cage_front_spec, crane=[372, 150],
                   crane_hook=[[CRANE_STATES[s]['tip'][0], CRANE_STATES[s]['hook_y'] + 14] for s in (0, 1)],
                   hold_door=[475, 150], bridge=[561, 150], log=[611, 150], walk_x=list(WALK_X),
                   galley_door=[G_DOOR[0], G_DOOR[1], G_DOOR[2] + 1, G_DOOR[3]], steam=[STACK_X, 70],
                   hold_box=list(H_DOOR), bridge_door=list(B_DOOR), log_door=list(L_DOOR), log_book=[612, 129],
                   horizon=HZ, deck_far=BW_BASE, rail_top=160)
    st = ex.stage(PW, GROUND, BAND, layers, fg, anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    imgs = ex.images
    picks = {L['key']: L for L in st['layers'] if L['type'] == 'pick'}
    # 1 各镜头整屏不露黑（远景是整张不透明的，任何状态 / 时刻都应该铺满）
    bad = 0
    for camX in (0, 64, 128, 192, 256, 320):
        for t in (0.0, 0.7, 1.4):
            for s in ({}, dict(crane=1, cage_open=1)):
                im = np.array(BJ.ref_render(st, imgs, camX, t, s).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('货轮 camX 0…320 × 3 个时刻 × 两组状态 整屏没有露黑', bad)
    ex.checked('货轮 远景层整张不透明', int((np.array(R['far'])[..., 3] != 255).sum()))
    ex.checked('货轮 甲板层 y ≥ 舷墙底整片不透明（甲板没有洞）', int((np.array(R['deck'])[BW_BASE:, :, 3] != 255).sum()))
    # 2 strip 2 s 闭合 + 帧条宽；wrap 层宽 = period（横向首尾相接）
    for name, fn, box, n, fps in (('steam', steam_frame, STEAM_BOX, STEAM_N, STEAM_FPS),
                                  ('radar', radar_frame, RADAR_BOX, RADAR_N, RADAR_FPS)):
        T = n / fps
        ex.checked('货轮 strip %s %.1f s 严格闭合（t=0 vs t=%.1f）' % (name, T, T),
                   BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)) + (0 if abs(T - 2.0) < 1e-9 else 1))
        ex.checked('货轮 strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
    wb = 0
    for L in st['layers']:
        if L['type'] == 'wrap':
            im = imgs[L['image']]
            wb += int(im.width != L['period'])
    ex.checked('货轮 雾带 wrap 图宽 = period（横向首尾相接，自己循环）', wb)
    # 3 锚点都在地图里；站人的锚点在可走带 / walk_x 里
    pts = []
    for k, v in st['anchors'].items():
        if k == 'walk_x':
            continue
        if isinstance(v, list) and len(v) == 2 and all(isinstance(q, (int, float)) for q in v):
            pts.append((k, v))
        elif isinstance(v, list) and len(v) == 4 and all(isinstance(q, (int, float)) for q in v):
            pts += [(k + '0', v[:2]), (k + '1', v[2:])]
        elif isinstance(v, list) and v and all(isinstance(q, list) for q in v):
            pts += [(k + str(i), q) for i, q in enumerate(v)]
    out = sum(1 for k, (x, y) in pts if not (0 <= x <= PW and 0 <= y <= H))
    stand = ('gangway', 'galley', 'cage', 'crane', 'hold_door', 'bridge', 'log')
    out += sum(1 for k in stand if not (BAND[0] <= st['anchors'][k][1] <= BAND[1] and WALK_X[0] <= st['anchors'][k][0] <= WALK_X[1]))
    ex.checked('货轮 锚点都在地图里，调查点站在可走带 / walk_x 里（%d 个点）' % len(pts), out)
    # 4 pick：每张尺寸一致；crane 两张只在吊车区域不同、cage_open 两张只在笼门那一块不同
    for key, L in picks.items():
        sizes = {imgs[k].size for k in L['images']}
        ex.checked('货轮 pick %s %d 张尺寸一致 %s' % (key, len(L['images']), sorted(sizes)[0]), len(sizes) - 1)
    c0, c1 = [np.array(imgs[k]) for k in picks['crane']['images']]
    ys, xs = np.nonzero(np.abs(c0.astype(int) - c1.astype(int)).max(-1) > 0)
    ex.note('crane 两张不同的像素 %d，范围 x %d–%d y %d–%d（世界坐标）' % (len(xs), xs.min() + CRANE_BOX[0], xs.max() + CRANE_BOX[0],
                                                               ys.min() + CRANE_BOX[1], ys.max() + CRANE_BOX[1]))
    bad = 0
    for camX in (100, 200, 300):
        g0 = BJ.ref_render(st, imgs, camX, 0.5, dict(crane=0))
        g1 = BJ.ref_render(st, imgs, camX, 0.5, dict(crane=1))
        dm = np.abs(np.array(g0, int) - np.array(g1, int)).max(-1) > 0
        sx0, sx1 = CRANE_BOX[0] - camX, CRANE_BOX[2] - camX
        dm[CRANE_BOX[1]:CRANE_BOX[3], max(0, sx0):max(0, min(W, sx1))] = False
        bad += int(dm.sum())
    ex.checked('货轮 crane 0/1 整屏只在吊车区域（x %d–%d, y < %d）不同' % (CRANE_BOX[0], CRANE_BOX[2], CRANE_BOX[3]), bad)
    k0, k1 = [np.array(imgs[k]) for k in picks['cage_open']['images']]
    ys, xs = np.nonzero(np.abs(k0.astype(int) - k1.astype(int)).max(-1) > 0)
    dx0, dy0, dx1, dy1 = CAGE_DOOR
    inside = (xs + CAGE_BOX[0] >= dx0 - 12) & (xs + CAGE_BOX[0] <= dx1 + 6) & (ys + CAGE_BOX[1] >= dy0 - 1) & \
             (ys + CAGE_BOX[1] <= dy1 + 4)
    ex.checked('货轮 cage_open 0/1 只在笼门那一块不同', int((~inside).sum()))
    # 5 笼子夹住猩猩：猩猩（idle 两帧的外框）站在笼子里，铁栏道具的纵深在猩猩和可走带之间；铁栏图只有全透明 / 全不透明
    ext = _strength_ext()
    fx0, fy0, fx1, fy1 = CAGE_F
    cx, cy = CAGE_INSIDE
    ok = (fx0 + 3 <= cx + ext[0] and cx + ext[2] <= fx1 - 3 and fy0 + 4 <= cy + ext[1] and cy + ext[3] <= fy1)
    ok = ok and (cy < CAGE_DEPTH < BAND[0]) and (fy1 + CAGE_D[1] < cy)
    ex.checked('货轮 猩猩（%d×%d）放得进笼子、depth %.1f 夹在猩猩 y %d 和可走带 %d 之间' %
               (ext[2] - ext[0], ext[3] - ext[1], CAGE_DEPTH, cy, BAND[0]), 0 if ok else 1)
    al = np.concatenate([np.array(imgs[k])[..., 3].ravel() for k in picks['cage_open']['images']])
    ex.checked('货轮 铁栏图只有全透明 / 全不透明像素（道具叠在 pick 上不变色）', int(((al > 0) & (al < 255)).sum()))
    # 道具叠上去（没人的时候）画面一个像素都不变
    bad = 0
    spec = st['anchors']['cage_front']
    for s in (0, 1):
        g = BJ.ref_render(st, imgs, 120, 0.3, dict(cage_open=s), fg=False)
        g2 = g.copy()
        g2.alpha_composite(imgs[spec['images'][s]], (spec['x'] - 120, spec['y']))
        bad += BJ.ndiff(g, g2)
    ex.checked('货轮 cage_front 道具叠在背景 pick 上：没人时画面不变', bad)
    # 6 前景栏杆只挡脚和小腿：最高的不透明行 ≥ 160（可走带最前面 y 172 的人最多挡 12 px）
    top = st['fg'][0]['y']
    ex.checked('货轮 前景栏杆顶 y %d（只挡 y > %d 的人的脚 / 小腿）' % (top, top), 0 if top >= 160 else 1)
    # 7 大小
    tot = sum(_png_bytes(v) for k, v in imgs.items() if k.startswith('bg/freighter_deck/'))
    ex.checked('货轮 全部图层 PNG 合计 ≤ 600 KB（%.0f KB）' % (tot / 1024.0), max(0, tot - 600 * 1024))
    # 8 可走带后面压低对比（记数，不卡）：局部对比（拉普拉斯均值）
    lap_all = []
    for camX in (0, 160, 320):
        g = np.array(BJ.ref_render(st, imgs, camX, 0.0, {}).convert('L')).astype(float)
        lap_all.append(np.abs(g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]))
    lap = np.concatenate(lap_all, axis=1)
    ex.note('局部对比（拉普拉斯均值）：y 146–172 %.1f，y 110–146 %.1f，y < 110 %.1f' %
            (lap[145:171].mean(), lap[109:145].mean(), lap[:109].mean()))


# ============================================================ 单独预览
def _char(cid, anim='idle', frame=0):
    meta = json.load(open(os.path.join(TOOLS, '_meta', 'chars.json'), encoding='utf-8'))['chars'][cid]
    idx = json.load(open(os.path.join(TOOLS, '_meta', 'img_index.json'), encoding='utf-8'))
    sheet = Image.open(os.path.join(GAME, 'assets', *idx[meta['image']]['file'].split('/'))).convert('RGBA')
    cw, ch = meta['cell']
    row = meta['animations'][anim]['row']
    return sheet.crop((frame * cw, row * ch, frame * cw + cw, row * ch + ch)), meta['pivot']


def _scene_with_cage(BJ, st, images, camX, t, s, extra=()):
    """按游戏里的画序拼一帧：背景 → 猩猩（y 140）→ 铁栏道具（depth 144.5）→ 可走带上的人 → 前景。"""
    im = BJ.ref_render(st, images, camX, t, dict(cage_open=s), fg=False).convert('RGBA')
    sfr, (spx, spy) = _char('strength')
    cx, cy = CAGE_INSIDE
    im.alpha_composite(sfr, (cx - spx - camX, cy - spy))
    spec = st['anchors']['cage_front']
    im.alpha_composite(images[spec['images'][s]], (spec['x'] - camX, spec['y']))
    for cid, x, y in sorted(extra, key=lambda e: e[2]):
        fr, (fpx, fpy) = _char(cid)
        im.alpha_composite(fr, (x - fpx - camX, y - fpy))
    for L in st['fg']:
        BJ.ref_layer(im, L, images, camX, t, {})
    return im


if __name__ == '__main__':
    import importlib.util
    spec_ = importlib.util.spec_from_file_location('bg_jojo', os.path.join(TOOLS, 'bg_jojo.py'))
    BJ = importlib.util.module_from_spec(spec_)
    sys.modules['bg_jojo'] = BJ
    spec_.loader.exec_module(BJ)
    out = os.path.join(HERE, '_preview', 'ch2', 'after')
    os.makedirs(out, exist_ok=True)
    c = BJ.standalone_c(os.path.join(HERE, '_preview', 'ch2', 'freighter_deck_solo'))
    ex = BJ.Ex(c, check=True)
    ex.begin('freighter_deck')
    st = export(ex, BJ)
    # 整条（左半镜头 0、右半镜头 320），2 倍
    world = Image.new('RGB', (PW, H))
    for cx in (0, 320):
        world.paste(BJ.ref_render(st, ex.images, cx, 0.6, {}).convert('RGB'), (cx, 0))
    world.resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(out, 'freighter_deck_world.png'))
    # 笼子：猩猩站在笼子里（道具铁栏画在它前面），承太郎站在笼子前、阿布德尔在可走带前沿；关 / 开，4 倍
    tiles = []
    for s in (0, 1):
        im = _scene_with_cage(BJ, st, ex.images, 120, 0.6, s, extra=(('jotaro', 196, 152), ('avdol', 268, 170)))
        tiles.append(im.convert('RGB').crop((60, 64, 180, 180)).resize((480, 464), Image.NEAREST))
    sheet = Image.new('RGB', (968, 464), (20, 20, 24))
    for i, t_ in enumerate(tiles):
        sheet.paste(t_, (i * 488, 0))
    sheet.save(os.path.join(out, 'freighter_deck_cage.png'))
    # 吊车两个角度（镜头 220），2 倍
    sheet = Image.new('RGB', (W * 2 * 2 + 8, H * 2), (20, 20, 24))
    for i in range(2):
        im = BJ.ref_render(st, ex.images, 220, 0.6, dict(crane=i)).convert('RGB')
        sheet.paste(im.resize((W * 2, H * 2), Image.NEAREST), (i * (W * 2 + 8), 0))
    sheet.save(os.path.join(out, 'freighter_deck_crane.png'))
    pv = importlib.util.spec_from_file_location('bg_new_pv', os.path.join(HERE, '_pv.py'))
    PV = importlib.util.module_from_spec(pv)
    pv.loader.exec_module(PV)
    PV._anchor_preview('freighter_deck', st, ex, BJ, out, PV._font(11))
    bad = [ch['label'] for ch in ex.report['freighter_deck']['checks'] if not ch['ok']]
    print('ok' if not bad else 'NG %s' % bad, out)
