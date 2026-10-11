# -*- coding: utf-8 -*-
r"""singapore_hotel —— 新加坡一家老派酒店的单人间，夜里（第3章：波鲁纳雷夫一个人回房间，冰箱里藏着诅咒的迪波）。

2026-10-11 第3章按体验版的精度重画（改前是 later_stages.room('hotel')：米色平墙 + 方块床 + 一扇蓝窗）。
320 单屏，ground 156，可走带 y 148–176；侧视平视，后墙 + 地板（地板从 y 132 起）。

从左到右（家具 x 范围是定死的，战斗逻辑按这些 x 判断玩偶藏在哪；门 / 床 / 床头柜 / 梳妆柜 / 冰箱 / 窗组 自检逐个核对）：
  门       x 6–34    木门框 + 三格气窗 + 四块凸板门；猫眼、门链（挂着没扣）、门把上挂“请勿打扰”牌（只画图形：红条 + 月亮）、
                     门背后的疏散图；走廊的灯从气窗、门缝、猫眼透进来（门前地板一小片暖光）；
                     门上方一台穿墙空调（百叶出风口 + 红色待机灯 + 下面墙纸上的水渍），旁边一块“禁带榴莲”牌（图形）
  衣帽架   x 42–56   挂着酒店浴袍和一把收起来的伞；门边电灯开关
  床       x 60–140  左头右尾：高床头板 / 矮床尾板、两只枕头、白床单（侧面的褶）、床尾搭一条蜡染毯子；
                     床单下沿和地板之间一道黑缝（y 139–146，玩偶藏身处）；墙上一幅日落海景油画（帆船 + 椰树）+ 两盏壁灯（关着）
  床头柜   x 145–158 抽屉 + 下格（圣经、电话簿）；上面一盏青花瓷台灯（灯罩 x 144–158 发暖光，上下口在墙上照出一道光）
  梳妆柜   x 160–190 两只抽屉 + 两扇柜门、弯腿（柜底一道暗缝 y 135–139）；台面上兰花、转盘电话、房卡钥匙；
                     上面一面金框镜子（镜面 167–185 × 72–107，中心 (176, 89.5)；里面是台灯那一角左右翻过来、暗一点蓝一点）
  藤椅 + 小圆桌 + 行李箱  x 194–235（藤椅在桌子后面；桌上一盘红毛丹 + 烟灰缸；皮箱立着，贴旅行贴纸、挂行李牌）；挂钟 1 点 50
  散尾葵   铜盆 x 239–249，叶子伸到 216–265（画在冰箱前面）
  冰箱     x 250–276 米白色迷你吧（门缝、门把、铭牌、底部散热格栅）；台面上冰桶、倒扣的两只杯子、价目卡；上方一幅兰花小画
  窗 + 窗帘 x 280–318 暗红丝绒落地窗帘（褶 + 金色绑带 + 帘头波浪下摆 + 流苏吊穗）；玻璃 286–303 × 46–117（中心 (294.5, 81.5)），
                     窗外新加坡夜景（渐变夜空、星星、高楼亮窗、港口的灯和倒影、一条船）
  天花板   檐口齿饰；中间一台吊扇（石膏圆花 + 吊杆 + 电机罩，叶片是 strip），右边一盏乳白玻璃吊灯（关着）
  地板     柚木地板（低对比），中间一块暗红地毯（细边、很淡的菱格和中心圆；可走带上压低对比），床在台灯光里往前投一道影

图层（从下到上）：
  static  room        整张底图（不透明；夜里的打光烘在里面：蓝的环境光 + 台灯暖光（分档 + 交界处抖一点）+ 窗外冷光 + 走廊灯）
  strip   night       窗外：航空障碍灯 2 s 闪一次、两颗星闪、一扇窗灯亮灭（16 帧 @8 fps，2 s 闭合；只画亮的那几个像素）
  pick    fridge      key 'fridge'，values [0, 1]（48×70，画在 FRIDGE_BOX 左上角 (244, 98)）：0 = 空图；1 = 冰箱门自己开了
                      （门绕右边合页向右前方打开到 x 286，里面冷白的光、两层空的铁丝格 + 空的果菜盒，门内侧几瓶饮料，
                      冷光照到地板 / 旁边窗帘，门底下漫出一点冷气）
  pick    mess        key 'mess'，values [0, 1]（320×180）：0 = 空图；1 = 打完以后的狼藉：台灯倒在床头柜前的地上（灯罩朝右前方、
                      灯泡还亮，墙上那道光没了）、前面那只枕头被割开羽毛散一地、右边窗帘被划了三刀 + 扯下一片、
                      地毯上四道刀痕、藤椅侧着倒在桌子前面
                      两张 pick 的像素不重叠，同时打开 = 各自叠上去（自检）
  strip   fan         吊扇叶片（8 帧 @12 fps = 2/3 s 转 1/4 圈；四叶一样，所以 1/4 圈就闭合）
台灯的光没有用 glow 图层：bg_jojo.ref_render（预览 / 自检用的 Python 版公式）不认识 'glow'，用了 ch3_preview 会直接报错；
光直接烘进底图和 pick（JS 和 Python 拼出来逐像素一样）。

单独运行：python -B tools\bg_new\singapore_hotel.py → tools\bg_new\_preview\ch3\singapore_hotel_solo.png（四种状态）
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
WALK = (148, 176)
C4 = A._c4

# ---------------------------------------------------------------- 竖向结构
CEIL = 7                 # 天花板 0–7
CROWN = (8, 13)          # 檐口线
PRAIL = 21               # 挂画线 21–22
PAPER = (23, 99)         # 墙纸
DADO = 100               # 腰线 100–102
LOWER = (103, 123)       # 护墙板
SKIRT = (124, 131)       # 踢脚板
JUNC = 132               # 地板从这一行开始

# ---------------------------------------------------------------- 家具 x 范围（含两端；自检核对）
DOOR_X = (6, 34)
COAT_X = (42, 56)
BED_X = (60, 140)
STAND_X = (145, 158)
DRESSER_X = (160, 190)
FRIDGE_X = (250, 276)
WINDOW_X = (280, 318)
SPEC_X = {'door': DOOR_X, 'bed': BED_X, 'stand': STAND_X, 'dresser': DRESSER_X, 'fridge': FRIDGE_X,
          'window': WINDOW_X}

LAMP_C = (151, 95)                 # 灯罩中心（光源）
MIRROR = (165, 70, 187, 109)       # 镜框（含）；镜面 167–185 × 72–107，中心 (176, 89.5)
GLASS = (167, 72, 185, 107)
WIN_GLASS = (286, 46, 303, 117)    # 窗玻璃（含），中心 (294.5, 81.5)；左边一列被窗帘挡住
PELMET_Y = (28, 35)
FAN_C = (160, 33)                  # 叶片平面中心
FAN_R, FAN_E = 32, 0.22            # 叶片半径、俯仰压扁
N_FAN, FAN_FPS = 8, 12.0           # 8 帧转 1/4 圈
N_WIN, WIN_FPS = 16, 8.0           # 窗外 2 s 一圈
FAN_BOX = (125, 25, 196, 42)       # 叶片 strip 的框（右下不含）
WIN_BOX = (286, 46, 304, 118)

FRIDGE_BOX = (244, 98, 292, 168)   # 冰箱 pick 的框（右下不含）
MESS_BOXES = {                     # 狼藉只在这些框里（右下不含）
    'pillow': (60, 92, 141, 147),
    'feathers': (52, 132, 150, 176),
    'lamp': (118, 46, 184, 152),
    'chair': (186, 100, 237, 148),
    'curtain': (300, 36, 320, 140),
    'rug': (70, 148, 224, 176),
}

# ---------------------------------------------------------------- 调色
WOOD = dict(hi=(170, 118, 78), lt=(146, 98, 64), md=(122, 80, 52), dk=(92, 58, 38), dd=(62, 38, 26))
TEAK = (132, 90, 58)
BRASS = [(96, 70, 34), (150, 116, 56), (204, 166, 86), (240, 214, 140)]
SHEET = dict(hi=(244, 242, 234), lt=(230, 230, 224), md=(210, 212, 214), dk=(176, 180, 192), dd=(128, 130, 148))
VELVET = dict(hi=(176, 62, 66), lt=(150, 46, 54), md=(126, 36, 46), dk=(96, 24, 36), dd=(64, 16, 28))
CREAM = dict(hi=(240, 236, 220), lt=(226, 220, 200), md=(206, 200, 180), dk=(170, 164, 146), dd=(110, 106, 96))


def R(d, box, col, outline=None):
    if col is None and outline is None:
        return
    d.rectangle(box, fill=C4(col) if col is not None else None, outline=C4(outline) if outline else None)


def L(d, pts, col, w=1):
    d.line(pts, fill=C4(col), width=w)


def P(d, x, y, col, a=255):
    d.point((int(x), int(y)), fill=C4(col, a))


def sh(c, k):
    return tuple(int(max(0, min(255, round(v * k)))) for v in c)


def blank(w=W, h=H):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def toimg(a):
    return Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA')


# ============================================================ 墙 + 地板（numpy albedo）
@lru_cache(maxsize=1)
def wall_albedo():
    a = np.zeros((H, W, 3), np.float32)
    for y in range(0, CEIL + 1):                                   # 天花板（越往上越暗）
        a[y] = mix((104, 100, 90), (150, 146, 130), y / CEIL)
    crown = {8: (112, 106, 92), 9: (214, 208, 190), 10: (176, 170, 152), 11: (228, 222, 204), 12: (188, 182, 162),
             13: (120, 114, 98)}
    for y, c in crown.items():
        a[y] = c
    for x in range(0, W, 4):                                      # 檐口的齿饰
        a[12, x] = (150, 144, 126)
    for y in range(14, PRAIL):                                     # 檐壁（素灰泥）
        a[y] = (204, 200, 180)
    a[PRAIL] = (148, 104, 68)
    a[PRAIL + 1] = (94, 62, 42)
    # 墙纸：细竖条 + 小菱花（低对比）
    base, dk, lt = np.array((182, 184, 156), np.float32), (170, 172, 146), (194, 196, 168)
    for y in range(PAPER[0], PAPER[1] + 1):
        a[y] = base
        for x in range(0, W, 7):
            a[y, x] = dk
            if x + 1 < W:
                a[y, x + 1] = lt
    motif = ['..x..', '.x.x.', 'x.o.x', '.x.x.', '..x..']
    for j, gy in enumerate(range(PAPER[0] + 4, PAPER[1] - 4, 12)):
        off = 3 + (j % 2) * 7
        for gx in range(off, W, 14):
            for yy, row in enumerate(motif):
                for xx, ch in enumerate(row):
                    if not 0 <= gx + xx - 2 < W:
                        continue
                    if ch == 'x':
                        a[gy + yy, gx + xx - 2] = (172, 166, 136)
                    elif ch == 'o':
                        a[gy + yy, gx + xx - 2] = (198, 192, 158)
    a[PAPER[0]] *= 0.86                                            # 挂画线下的阴影
    # 腰线
    a[DADO] = (168, 122, 84)
    a[DADO + 1] = (130, 90, 60)
    a[DADO + 2] = (84, 56, 38)
    # 护墙板：一格格凸板
    for y in range(LOWER[0], LOWER[1] + 1):
        a[y] = (112, 76, 52)
    for x0 in range(-6, W, 34):
        x1 = x0 + 29
        for x in range(max(0, x0), min(W, x1 + 1)):
            a[LOWER[0] + 3, x] = (82, 54, 36)
            a[LOWER[1] - 3, x] = (142, 100, 68)
            for y in range(LOWER[0] + 4, LOWER[1] - 3):
                a[y, x] = (120, 82, 56)
        for y in range(LOWER[0] + 3, LOWER[1] - 2):
            if 0 <= x0 < W:
                a[y, x0] = (82, 54, 36)
            if 0 <= x1 < W:
                a[y, x1] = (142, 100, 68)
    # 踢脚板
    a[SKIRT[0]] = (152, 110, 74)
    a[SKIRT[0] + 1] = (118, 80, 54)
    for y in range(SKIRT[0] + 2, SKIRT[1]):
        a[y] = (98, 66, 44)
    a[SKIRT[1]] = (58, 38, 26)
    # 墙面的纹理（很淡）+ 上面一点旧黄
    nz = A._fbm(W, H, 14, 5) - 0.5
    a[14:LOWER[1] + 1] *= (1 + 0.06 * nz[14:LOWER[1] + 1])[..., None]
    for y in range(PAPER[0], PAPER[0] + 12):
        a[y] = a[y] * 0.97 + np.array((150, 130, 90), np.float32) * 0.03
    return a


RUG_Y = (150, 174)


def rug_edges(y):
    t = (y - RUG_Y[0]) / (RUG_Y[1] - RUG_Y[0])
    return 72 - 10 * t, 236 + 10 * t


@lru_cache(maxsize=1)
def floor_albedo():
    a = np.zeros((H, W, 3), np.float32)
    rows = [132, 134, 137, 140, 144, 148, 153, 158, 164, 170, 177, 181]
    for i in range(len(rows) - 1):
        y0, y1 = rows[i], min(H, rows[i + 1])
        Lp = 26 + i * 7
        off = int(hrange(0, Lp, i, 3))
        xs = list(range(-off, W, Lp))
        for k, xa in enumerate(xs):
            f = 0.93 + 0.12 * hash01(i, k, 5)
            col = np.array(TEAK, np.float32) * f
            xa0, xb = max(0, xa), min(W, xa + Lp)
            a[y0:y1, xa0:xb] = col
            for g in range(int(hrange(0, 3, i, k, 6)) + 1):                    # 木纹
                gy = int(hrange(y0 + 1, y1, i, k, g, 7))
                gx0 = int(hrange(xa0, xb, i, k, g, 8))
                for x in range(gx0, min(xb, gx0 + int(hrange(6, 18, i, k, g, 9)))):
                    if gy < H:
                        a[gy, x] *= 0.93
            if 0 <= xa < W:                                          # 板头缝
                a[y0:y1, xa] *= 0.80
                if xa + 1 < W:
                    a[y0:y1, xa + 1] *= 1.04
        a[y0] *= 0.82                                                # 板缝
        if y0 + 1 < y1:
            a[y0 + 1] *= 1.04
    for y in range(JUNC, JUNC + 3):                                  # 墙脚的暗
        a[y] *= 0.70 + 0.1 * (y - JUNC)
    # 地毯
    for y in range(RUG_Y[0], RUG_Y[1] + 1):
        xl, xr = rug_edges(y)
        v = (y - RUG_Y[0]) / (RUG_Y[1] - RUG_Y[0])
        for x in range(int(math.ceil(xl)), int(math.floor(xr)) + 1):
            u = (x - xl) / (xr - xl)
            du, dv = min(x - xl, xr - x), min(y - RUG_Y[0], RUG_Y[1] - y)
            dd = min(du / 1.6, dv)
            if dd < 1:
                c = (80, 38, 38)
            elif dd < 3:
                c = (136, 104, 70) if (x + y) % 4 else (124, 92, 62)
            elif dd < 4:
                c = (84, 38, 40)
            else:
                c = (116, 46, 48)
                lu = abs(((u * 26) % 2) - 1) + abs(((v * 4) % 2) - 1)
                if lu < 0.22:
                    c = (108, 42, 46)
                me = ((u - 0.5) / 0.13) ** 2 + ((v - 0.5) / 0.30) ** 2
                if me < 1:
                    c = (100, 50, 58) if me > 0.55 else (108, 56, 58)
            a[y, x] = c
        if y % 2 == 0:                                               # 两头的流苏
            for x in (int(math.ceil(xl)) - 1, int(math.floor(xr)) + 1):
                a[y, x] = (196, 180, 150)
    return a


def rug_slashes(a):
    """狼藉：地毯上几道刀痕（割开的口子露出浅色的底布，边上一道暗）。"""
    cuts = [((88, 156), (126, 152)), ((104, 167), (150, 159)), ((150, 171), (196, 163)), ((172, 157), (204, 154))]
    for (x0, y0), (x1, y1) in cuts:
        n = max(abs(x1 - x0), abs(y1 - y0))
        for s in range(n + 1):
            u = s / n
            x = int(round(x0 + (x1 - x0) * u))
            y = int(round(y0 + (y1 - y0) * u))
            w = 1 if 0.12 < u < 0.88 else 0
            a[y, x] = (190, 170, 136) if w else (160, 132, 106)
            if w:
                a[y + 1, x] = (52, 20, 24)
                if hash01(x, y, 3) < 0.3:
                    a[y - 1, x] = (168, 120, 104)


# ============================================================ 物件（PIL，一件一层）
class Pieces:
    """按画的先后叠：每件一层 RGBA，记下 bbox（自检核对家具 x 范围）和是否自发光（不吃打光）。"""

    def __init__(self):
        self.items = []

    def new(self, name, emissive=False):
        im = blank()
        self.items.append((name, im, emissive))
        return ImageDraw.Draw(im)

    def bbox(self, prefix):
        bbs = [im.getchannel('A').getbbox() for n, im, e in self.items if n == prefix or n.startswith(prefix + '.')]
        bbs = [b for b in bbs if b]
        if not bbs:
            return None
        return (min(b[0] for b in bbs), min(b[1] for b in bbs), max(b[2] for b in bbs) - 1, max(b[3] for b in bbs) - 1)


def wood_post(d, x0, x1, y0, y1, pal=WOOD, lit_right=True):
    """竖着的一根木头（左右明暗）。"""
    w = x1 - x0 + 1
    for j in range(w):
        u = j / max(1, w - 1)
        if not lit_right:
            u = 1 - u
        c = pal['dk'] if u < 0.2 else pal['md'] if u < 0.55 else pal['lt'] if u < 0.85 else pal['hi']
        L(d, (x0 + j, y0, x0 + j, y1), c)


# ---------------------------------------------------------------- 门 + 门上的空调
def draw_door(S):
    d = S.new('door')
    wd = WOOD
    R(d, (6, 60, 34, 131), wd['md'])                                     # 门框
    L(d, (6, 60, 6, 131), wd['dk'])
    L(d, (7, 61, 7, 131), wd['hi'])
    L(d, (8, 61, 8, 131), wd['lt'])
    L(d, (34, 60, 34, 131), wd['dd'])
    L(d, (33, 61, 33, 131), wd['dk'])
    L(d, (6, 60, 34, 60), wd['dd'])
    L(d, (7, 61, 33, 61), wd['hi'])
    R(d, (6, 57, 34, 59), wd['lt'])                                      # 门楣
    L(d, (6, 57, 34, 57), wd['hi'])
    L(d, (6, 60, 34, 60), wd['dd'])
    # 气窗：三格磨砂玻璃，透出走廊的灯（自发光，另一层）
    for x in (16, 17, 23, 24):
        L(d, (x, 63, x, 70), wd['md'])
    R(d, (9, 71, 31, 73), wd['md'])
    L(d, (9, 71, 31, 71), wd['hi'])
    L(d, (9, 73, 31, 73), wd['dd'])
    # 门板（下沿和门槛之间留一道缝，走廊的灯从缝里漏进来）
    R(d, (9, 74, 31, 129), (134, 88, 58))
    L(d, (9, 74, 9, 129), wd['dd'])
    L(d, (31, 74, 31, 129), (156, 106, 70))
    for (x0, y0, x1, y1) in ((11, 77, 19, 101), (21, 77, 29, 101), (11, 106, 19, 128), (21, 106, 29, 128)):
        R(d, (x0, y0, x1, y1), (120, 78, 52))
        L(d, (x0, y0, x1, y0), wd['dd'])
        L(d, (x0, y0, x0, y1), wd['dk'])
        L(d, (x0, y1, x1, y1), (164, 112, 74))
        L(d, (x1, y0, x1, y1), (152, 104, 68))
        R(d, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), (138, 92, 60))
        L(d, (x0 + 2, y0 + 2, x1 - 2, y0 + 2), (156, 106, 70))
        L(d, (x1 - 2, y0 + 3, x1 - 2, y1 - 2), (114, 76, 50))
    # 门背后的疏散图（白卡 + 红框 + 几道线）
    R(d, (12, 80, 22, 91), (232, 228, 214), (150, 40, 40))
    L(d, (14, 83, 20, 83), (120, 120, 126))
    L(d, (14, 83, 14, 88), (120, 120, 126))
    L(d, (17, 86, 20, 86), (120, 120, 126))
    L(d, (14, 88, 18, 88), (120, 120, 126))
    P(d, 19, 88, (220, 40, 40))
    P(d, 16, 82, (60, 150, 80))
    # 猫眼
    P(d, 26, 85, BRASS[3])
    P(d, 27, 85, BRASS[2])
    P(d, 26, 86, BRASS[1])
    P(d, 27, 86, (20, 18, 22))
    # 门锁旋钮 + 门把 + 锁孔
    R(d, (27, 96, 29, 98), BRASS[1])
    P(d, 27, 96, BRASS[3])
    R(d, (26, 103, 29, 105), BRASS[2])
    L(d, (26, 103, 28, 103), BRASS[3])
    P(d, 26, 104, BRASS[3])
    P(d, 29, 105, BRASS[0])
    L(d, (24, 104, 25, 104), BRASS[2])
    P(d, 28, 108, (30, 22, 18))
    # 门链：从门框上的链座垂下来（没扣）
    R(d, (31, 94, 33, 95), BRASS[1])
    for i, y in enumerate(range(96, 106)):
        x = 32 - (1 if 99 <= y <= 102 else 0)
        P(d, x, y, BRASS[3] if i % 2 == 0 else BRASS[0])
    P(d, 31, 106, BRASS[2])
    P(d, 32, 106, BRASS[1])
    # “请勿打扰”牌：挂在门把上（红条 + 黄月亮 + 三个点）
    L(d, (25, 105, 25, 107), (180, 170, 150))
    R(d, (22, 107, 28, 121), (236, 228, 206), (150, 130, 110))
    R(d, (23, 108, 27, 110), (196, 40, 46))
    d.ellipse((23, 112, 27, 116), fill=C4((246, 206, 90)))
    d.ellipse((24, 111, 28, 115), fill=C4((236, 228, 206)))
    for x in (23, 25, 27):
        P(d, x, 119, (90, 80, 120))
    # 门槛的铜条
    L(d, (9, 131, 31, 131), BRASS[2])
    d = S.new('door.corridor', emissive=True)                               # 走廊的灯：气窗、门缝、猫眼
    for (xa, xb) in ((10, 15), (18, 22), (25, 30)):
        for y in range(63, 71):
            u = (y - 63) / 7.0
            for x in range(xa, xb + 1):
                c = mix((132, 112, 80), (82, 70, 56), u)
                if (x + y) % 5 == 0:
                    c = sh(c, 0.92)
                P(d, x, y, c)
        L(d, (xa, 63, xb, 63), (150, 130, 96))
    L(d, (10, 130, 30, 130), (255, 214, 150))
    P(d, 9, 130, (180, 140, 96))
    P(d, 31, 130, (180, 140, 96))
    P(d, 27, 86, (210, 186, 140))

    # 门上方的穿墙空调（百叶出风口 + 控制面板 + 红色待机灯；下面墙纸上一圈水渍）
    d = S.new('ac')
    R(d, (8, 30, 32, 42), CREAM['lt'], CREAM['dd'])
    L(d, (9, 31, 31, 31), CREAM['hi'])
    R(d, (10, 34, 26, 40), (120, 116, 104))
    for y in range(34, 41):
        L(d, (10, y, 26, y), (204, 198, 180) if y % 2 == 0 else (98, 94, 84))
    R(d, (28, 33, 30, 40), CREAM['md'], CREAM['dk'])
    P(d, 29, 37, (120, 116, 104))
    L(d, (9, 42, 31, 42), CREAM['dd'])
    L(d, (8, 43, 32, 43), (150, 140, 112))                              # 底下的阴影
    d = S.new('ac.led', emissive=True)
    P(d, 29, 35, (255, 60, 50))


def stain(a):
    """空调下面墙纸上的水渍（albedo 里画）。"""
    for y in range(44, 58):
        for x in range(12, 30):
            r = ((x - 21) / 9.0) ** 2 + ((y - 44) / 14.0) ** 2
            if r < 1:
                a[y, x] = a[y, x] * (0.95 + 0.03 * r)
            if 0.82 < r < 1.0 and hash01(x, y, 11) < 0.7:
                a[y, x] = a[y, x] * 0.86 + np.array((140, 112, 70), np.float32) * 0.14


# ---------------------------------------------------------------- 衣帽架
def draw_coat(S):
    d = S.new('coat')
    wd = WOOD
    L(d, (49, 76, 49, 137), wd['dk'])
    L(d, (50, 76, 50, 137), wd['lt'])
    R(d, (48, 73, 51, 75), wd['md'])
    L(d, (48, 73, 51, 73), wd['hi'])
    for (x, y, dx) in ((47, 78, -1), (52, 78, 1)):                    # 挂钩
        P(d, x, y, wd['md'])
        P(d, x + dx, y - 1, wd['md'])
        P(d, x + 2 * dx, y - 2, wd['hi'])
    L(d, (43, 138, 49, 134), wd['dk'])                                  # 三脚
    L(d, (56, 138, 50, 134), wd['md'])
    L(d, (49, 138, 50, 134), wd['dk'])
    # 浴袍（左钩）
    pts = [(46, 79), (48, 80), (48, 84), (49, 108), (44, 110), (42, 108), (42, 92), (43, 82)]
    d.polygon(pts, fill=C4(SHEET['lt']))
    L(d, (43, 82, 42, 92), SHEET['md'])
    L(d, (42, 93, 42, 108), SHEET['md'])
    L(d, (45, 84, 46, 106), SHEET['md'])
    L(d, (43, 96, 48, 96), (196, 196, 204))                             # 腰带
    P(d, 44, 97, (196, 196, 204))
    P(d, 44, 98, (182, 182, 194))
    L(d, (43, 109, 48, 108), SHEET['dk'])
    P(d, 46, 79, SHEET['hi'])
    # 收起来的伞（右钩）
    L(d, (53, 77, 54, 76), (60, 40, 30))
    L(d, (55, 77, 55, 80), (60, 40, 30))
    d.polygon([(53, 81), (56, 81), (57, 96), (55, 103), (54, 103), (52, 96)], fill=C4((40, 70, 56)))
    L(d, (56, 82, 56, 96), (64, 100, 80))
    L(d, (54, 84, 53, 95), (28, 50, 40))
    L(d, (54, 104, 54, 108), (150, 150, 150))
    P(d, 55, 88, (140, 120, 70))


# ---------------------------------------------------------------- 墙上的画 / 钟 / 小画 / 开关
def draw_wall_art(S):
    # 床上方：日落海景油画（金框）
    d = S.new('painting')
    x0, y0, x1, y1 = 78, 44, 122, 70
    R(d, (x0, y0, x1, y1), BRASS[1])
    L(d, (x0, y0, x1, y0), BRASS[3])
    L(d, (x0, y0, x0, y1), BRASS[2])
    L(d, (x0, y1, x1, y1), BRASS[0])
    L(d, (x1, y0, x1, y1), BRASS[0])
    R(d, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), None, (176, 138, 66))
    cx0, cy0, cx1, cy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 3
    hz = 60
    for y in range(cy0, hz):
        u = (y - cy0) / (hz - cy0)
        L(d, (cx0, y, cx1, y), mix((120, 84, 120), (236, 150, 92), u ** 0.8) if u < 0.75 else
          mix((236, 150, 92), (250, 206, 130), (u - 0.75) * 4))
    d.ellipse((101, 54, 107, 60), fill=C4((255, 226, 150)))
    L(d, (cx0, hz, cx1, hz), (250, 206, 130))
    for y in range(hz + 1, cy1 + 1):
        u = (y - hz) / (cy1 - hz)
        L(d, (cx0, y, cx1, y), mix((70, 96, 110), (36, 60, 76), u))
    for i, y in enumerate(range(hz + 1, cy1 + 1)):                     # 太阳的倒影
        w = 3 - i // 2
        if w > 0:
            L(d, (104 - w, y, 104 + w, y), (240, 180, 110) if i % 2 == 0 else (200, 140, 100))
    for (sx, sy) in ((86, 52), (95, 49), (113, 51)):                   # 云
        L(d, (sx, sy, sx + 5, sy), (240, 170, 140))
    # 帆船剪影（红帆）
    L(d, (88, 60, 97, 60), (40, 28, 30))
    L(d, (89, 61, 96, 61), (40, 28, 30))
    d.polygon([(90, 59), (93, 52), (94, 59)], fill=C4((150, 54, 40)))
    d.polygon([(94, 59), (96, 54), (97, 59)], fill=C4((130, 44, 34)))
    L(d, (93, 52, 93, 59), (40, 28, 30))
    # 椰树剪影
    L(d, (83, 66, 85, 52), (34, 30, 30))
    for (dx, dy) in ((-4, 2), (-3, -2), (3, -2), (4, 2), (0, -3)):
        L(d, (85, 52, 85 + dx, 52 + dy), (34, 40, 32))
    L(d, (cx0, cy1, cx0 + 6, cy1 - 1), (40, 40, 36))                   # 前景的沙滩一角
    L(d, (cx0, cy1 - 1, cx0 + 3, cy1 - 1), (60, 52, 44))
    # 挂画的线
    L(d, (100, 40, 90, 44), (90, 80, 60))
    L(d, (100, 40, 110, 44), (90, 80, 60))
    P(d, 100, 39, BRASS[2])

    # 画两边的一对壁灯（关着：铜臂 + 乳白郁金香灯罩）
    d = S.new('sconce')
    for sx in (71, 129):
        R(d, (sx - 1, 60, sx + 1, 65), BRASS[1])
        P(d, sx - 1, 60, BRASS[3])
        P(d, sx + 1, 65, BRASS[0])
        L(d, (sx, 63, sx, 58), BRASS[2])
        P(d, sx - 1, 57, BRASS[2])
        P(d, sx + 1, 57, BRASS[0])
        d.polygon([(sx - 3, 52), (sx + 3, 52), (sx + 2, 56), (sx - 2, 56)], fill=C4((214, 210, 196)))
        L(d, (sx - 3, 52, sx + 3, 52), (240, 238, 228))
        L(d, (sx + 2, 53, sx + 1, 56), (170, 166, 154))
        P(d, sx - 2, 53, (246, 244, 236))
    # 门边的“禁带榴莲”牌（只画图形：白底、榴莲、红圈斜杠）
    d = S.new('durian_sign')
    R(d, (40, 48, 53, 61), (236, 234, 224), (120, 116, 104))
    L(d, (41, 49, 52, 49), (250, 250, 244))
    d.ellipse((43, 51, 50, 58), fill=C4((150, 150, 60)))
    for (x, y) in ((44, 52), (46, 51), (48, 52), (49, 54), (48, 56), (46, 57), (44, 56), (43, 54), (46, 54)):
        P(d, x, y, (100, 104, 40))
    P(d, 46, 50, (90, 70, 40))
    d.ellipse((41, 49, 52, 60), outline=C4((200, 36, 40)))
    L(d, (43, 51, 50, 58), (200, 36, 40))
    L(d, (44, 51, 51, 58), (200, 36, 40))

    # 挂钟（1 点 50）
    d = S.new('clock')
    cx, cy = 222, 62
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=C4(WOOD['md']))
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), outline=C4(WOOD['dd']))
    d.arc((cx - 6, cy - 6, cx + 6, cy + 6), 200, 330, fill=C4(WOOD['hi']))
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=C4((232, 224, 198)))
    for k in range(12):
        ang = k * math.tau / 12
        P(d, round(cx + 4.4 * math.sin(ang)), round(cy - 4.4 * math.cos(ang)), (110, 100, 86) if k % 3 else (40, 34, 30))
    ha = (1 + 50 / 60) / 12 * math.tau
    ma = 50 / 60 * math.tau
    L(d, (cx, cy, round(cx + 2.6 * math.sin(ha)), round(cy - 2.6 * math.cos(ha))), (30, 26, 24))
    L(d, (cx, cy, round(cx + 4.2 * math.sin(ma)), round(cy - 4.2 * math.cos(ma))), (30, 26, 24))
    P(d, cx, cy, (190, 40, 40))

    # 冰箱上方的小画（兰花版画）
    d = S.new('print')
    R(d, (255, 64, 270, 85), (40, 34, 30))
    R(d, (256, 65, 269, 84), (226, 218, 194))
    R(d, (258, 67, 267, 82), (236, 230, 210))
    L(d, (262, 82, 262, 72), (70, 110, 70))
    L(d, (262, 75, 265, 71), (70, 110, 70))
    for (fx, fy) in ((261, 71), (264, 70), (266, 73), (260, 74)):
        P(d, fx, fy, (176, 90, 170))
        P(d, fx + 1, fy, (206, 130, 196))
        P(d, fx, fy + 1, (140, 60, 140))
    L(d, (259, 82, 261, 79), (80, 120, 74))
    L(d, (265, 82, 266, 79), (80, 120, 74))

    # 门边的电灯开关
    d = S.new('switch')
    R(d, (38, 98, 41, 104), CREAM['lt'], CREAM['dk'])
    P(d, 39, 100, BRASS[2])
    P(d, 39, 101, BRASS[1])


# ---------------------------------------------------------------- 床
def draw_bed(S, mess):
    wd = WOOD
    d = S.new('bed')
    # 床下的黑缝（床单下沿到地板）
    R(d, (66, 139, 134, 146), (20, 14, 18))
    for x in range(68, 133, 9):
        P(d, x, 145, (34, 24, 26))
    L(d, (66, 146, 134, 146), (30, 22, 24))
    # 床头板（高，左）+ 床尾板（矮，右）
    wood_post(d, 60, 66, 92, 146, lit_right=True)
    d.ellipse((60, 87, 66, 95), fill=C4(wd['md']))
    d.arc((60, 87, 66, 95), 180, 300, fill=C4(wd['dk']))
    d.arc((60, 87, 66, 95), 300, 360, fill=C4(wd['hi']))
    P(d, 63, 86, wd['hi'])
    L(d, (62, 98, 62, 138), wd['dk'])                                    # 床头板的嵌线
    L(d, (64, 98, 64, 138), wd['hi'])
    L(d, (62, 98, 64, 98), wd['dk'])
    L(d, (62, 138, 64, 138), wd['hi'])
    wood_post(d, 134, 140, 108, 146, lit_right=False)
    L(d, (134, 107, 140, 107), wd['hi'])
    L(d, (134, 108, 140, 108), wd['lt'])
    L(d, (136, 112, 136, 136), wd['hi'])
    L(d, (138, 112, 138, 136), wd['dk'])
    # 床垫顶面（一条，亮）+ 床单侧面（褶）+ 下沿（波浪）
    R(d, (67, 109, 133, 112), SHEET['hi'])
    L(d, (67, 113, 133, 113), SHEET['md'])
    for x in range(67, 134):
        hem = 137 + (1 if (x // 3) % 3 == 0 else 0) + (1 if (x // 9) % 2 else 0)
        for y in range(114, hem + 1):
            ph = (x - 67) % 11
            c = SHEET['lt']
            if ph in (0,):
                c = SHEET['dk']
            elif ph in (1, 10):
                c = SHEET['md']
            elif ph in (5, 6):
                c = SHEET['hi']
            if y >= hem - 1:
                c = sh(c, 0.88)
            P(d, x, y, c)
    # 被子翻下来的边（靠枕头那头）
    L(d, (90, 108, 90, 120), SHEET['dk'])
    L(d, (91, 108, 91, 121), SHEET['hi'])
    L(d, (92, 109, 92, 121), SHEET['md'])
    L(d, (67, 108, 89, 108), SHEET['md'])
    # 床尾搭的蜡染毯子（靛蓝底；上下赭色边、中间一格格小菱花；下摆流苏）
    for x in range(110, 134):
        top = 107 if x > 112 else 108
        bot = 127 + (1 if x % 4 == 0 else 0)
        for y in range(top, bot + 1):
            u, v = x - 110, y - top
            c = (52, 58, 98)
            if v in (2, 3) or bot - y in (2, 3):
                c = (150, 106, 60) if (u + v) % 4 else (118, 80, 48)
            elif v in (4,) or bot - y == 4:
                c = (196, 176, 134) if u % 2 == 0 else (52, 58, 98)
            elif 6 <= v <= bot - top - 6:
                mu, mv = (u + (v // 5) * 2) % 4, v % 5
                if (mu, mv) in ((1, 1), (0, 2), (2, 2), (1, 3)):
                    c = (124, 90, 58)
                elif (mu, mv) == (1, 2):
                    c = (186, 164, 124)
            if y <= 112:
                c = sh(c, 1.08)
            P(d, x, y, c)
        if x % 2 == 0:
            P(d, x, bot + 1, (196, 176, 134))
    L(d, (110, 108, 110, 128), (36, 40, 74))
    # 枕头
    pillow(d, 67, 95, 81, 110, mess, seed=1)
    L(d, (70, 101, 80, 101), SHEET['dk'])                                 # 前面那只枕头压出来的影
    pillow(d, 71, 102, 94, 113, mess, seed=2, front=True)


def pillow(d, x0, y0, x1, y1, mess, seed, front=False):
    """鼓鼓的枕头：圆角、上面亮（台灯在右边 → 右上更亮）、下沿一道影、四个角翘出来、中间一道凹。"""
    r = min(5, (y1 - y0) // 2)
    d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=C4(SHEET['dd']))
    d.rounded_rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), radius=r - 1, fill=C4(SHEET['md']))
    d.rounded_rectangle((x0 + 2, y0 + 1, x1 - 1, y1 - 3), radius=max(1, r - 1), fill=C4(SHEET['lt']))
    d.rounded_rectangle((x0 + 5, y0 + 1, x1 - 2, y0 + (y1 - y0) // 2), radius=2, fill=C4(SHEET['hi']))
    for (cx, cy) in ((x0, y0 + 1), (x1, y0 + 1), (x0, y1 - 1), (x1, y1 - 1)):     # 四个角翘出来
        P(d, cx, cy, SHEET['lt'] if cy < y1 - 1 else SHEET['dk'])
    mx = (x0 + x1) // 2
    L(d, (mx, y0 + 1, mx + 1, y0 + 3), SHEET['md'])                                 # 中间的凹
    L(d, (x0 + 3, y1 - 1, x1 - 2, y1 - 1), SHEET['dd'])
    if mess and front:                                               # 被割开：一道口子，里面的羽毛往外翻
        L(d, (x0 + 4, y0 + 6, x1 - 4, y0 + 3), (70, 66, 80))
        L(d, (x0 + 5, y0 + 7, x1 - 5, y0 + 4), (120, 118, 130))
        for i in range(10):
            fx = int(hrange(x0 + 4, x1 - 4, seed, i, 1))
            fy = int(hrange(y0 - 3, y0 + 5, seed, i, 2))
            P(d, fx, fy, (250, 250, 246))
            P(d, fx + 1, fy, (226, 228, 232))
        d.polygon([(x0 + 8, y0 + 4), (x0 + 12, y0 - 2), (x0 + 16, y0 + 3)], fill=C4((246, 246, 242)))
        L(d, (x0 + 9, y0 + 3, x0 + 12, y0 - 1), (210, 212, 222))


def draw_feathers(S):
    """狼藉：羽毛散一地（床上、床前的地板，少量落到可走带的前沿）。"""
    d = S.new('feathers')
    for i in range(70):
        if i < 22:
            x, y = hrange(70, 132, i, 1), hrange(105, 112, i, 2)
        elif i < 54:
            x, y = hrange(56, 148, i, 1), hrange(141, 154, i, 2)
        else:
            x, y = hrange(64, 140, i, 1), hrange(154, 172, i, 2)
        x, y = int(x), int(y)
        c = (250, 250, 246) if hash01(i, 3) < 0.6 else (214, 216, 224)
        P(d, x, y, c)
        if hash01(i, 4) < 0.45:
            P(d, x + 1, y, (196, 198, 210))
        if hash01(i, 5) < 0.2:
            P(d, x, y - 1, (240, 240, 236))


# ---------------------------------------------------------------- 床头柜 + 台灯
def draw_stand(S):
    wd = WOOD
    d = S.new('stand')
    R(d, (145, 113, 158, 115), wd['lt'])
    L(d, (145, 113, 158, 113), wd['hi'])
    L(d, (145, 115, 158, 115), wd['dk'])
    R(d, (146, 116, 157, 134), wd['md'])
    L(d, (146, 116, 146, 134), wd['dk'])
    L(d, (157, 116, 157, 134), wd['lt'])
    R(d, (147, 117, 156, 123), wd['lt'])                                  # 抽屉
    L(d, (147, 123, 156, 123), wd['dd'])
    L(d, (147, 117, 156, 117), wd['hi'])
    L(d, (150, 120, 153, 120), BRASS[2])
    P(d, 151, 121, BRASS[0])
    R(d, (147, 125, 156, 133), (38, 26, 22))                              # 下格（圣经 + 电话簿）
    R(d, (148, 128, 151, 133), (110, 30, 34))
    L(d, (148, 128, 151, 128), (150, 56, 54))
    P(d, 149, 130, BRASS[2])
    R(d, (152, 130, 156, 133), (196, 186, 150))
    L(d, (152, 131, 156, 131), (150, 140, 110))
    L(d, (146, 134, 157, 134), wd['dk'])
    for x in (146, 157):                                                  # 四条短腿
        L(d, (x, 135, x, 139), wd['dk'])
        L(d, (x + (1 if x == 146 else -1), 135, x + (1 if x == 146 else -1), 138), wd['md'])


def draw_lamp(S, fallen):
    if not fallen:
        d = S.new('lamp')
        # 青花瓷灯座（白底 + 蓝花）+ 铜颈
        d.ellipse((147, 103, 155, 113), fill=C4((226, 230, 232)))
        L(d, (148, 112, 154, 112), (150, 160, 176))
        for (x, y) in ((149, 106), (151, 105), (153, 107), (150, 109), (152, 110), (154, 109), (148, 108)):
            P(d, x, y, (50, 80, 150))
        L(d, (149, 104, 153, 104), (40, 70, 140))
        L(d, (148, 111, 154, 111), (40, 70, 140))
        P(d, 148, 105, (250, 252, 252))
        P(d, 148, 106, (250, 252, 252))
        L(d, (150, 101, 152, 101), BRASS[1])
        L(d, (149, 102, 153, 102), BRASS[2])
        d = S.new('lamp.shade', emissive=True)
        shade(d, 151, 88, 100, 4, 7)
    else:
        # 倒在床头柜前的地上：青花瓷灯座横躺、灯罩歪着朝右前方，里面的灯泡还亮；电线拖回床头柜
        d = S.new('lamp')
        L(d, (146, 138, 144, 141), (40, 30, 26))
        L(d, (144, 141, 141, 142), (40, 30, 26))
        d.ellipse((136, 139, 148, 147), fill=C4((214, 218, 224)))
        d.arc((136, 139, 148, 147), 200, 340, fill=C4((244, 246, 248)))
        L(d, (138, 146, 146, 146), (130, 140, 160))
        for (x, y) in ((139, 142), (141, 144), (143, 141), (145, 143), (140, 145), (144, 145), (142, 142)):
            P(d, x, y, (50, 80, 150))
        L(d, (137, 141, 137, 145), (40, 70, 140))
        L(d, (149, 142, 150, 142), BRASS[3])
        L(d, (149, 143, 151, 143), BRASS[1])
        L(d, (149, 144, 150, 144), BRASS[0])
        L(d, (148, 112, 154, 112), (84, 54, 36))                         # 床头柜面上空了，只剩一圈印子
        d = S.new('lamp.shade', emissive=True)
        # 灯罩躺着：窄口贴着灯座、宽口朝右前方张开
        d.polygon([(151, 140), (151, 146), (163, 147), (163, 135)], fill=C4((250, 222, 160)))
        L(d, (151, 140, 163, 135), (232, 186, 120))
        L(d, (151, 146, 163, 147), (214, 160, 100))
        for k in range(3):
            L(d, (154 + k * 3, 139 - k, 154 + k * 3, 146), (240, 200, 136))
        d.ellipse((161, 135, 165, 147), fill=C4((255, 246, 214)))
        d.ellipse((162, 138, 164, 144), fill=C4((255, 255, 240)))
        L(d, (161, 136, 161, 146), (226, 176, 110))


def shade(d, cx, y0, y1, top_hw, bot_hw):
    """灯罩（自发光的布面：中间亮、两边暗，竖褶）。"""
    for y in range(y0, y1 + 1):
        u = (y - y0) / (y1 - y0)
        hw = top_hw + (bot_hw - top_hw) * u
        xa, xb = int(round(cx - hw)), int(round(cx + hw))
        for x in range(xa, xb + 1):
            v = abs(x - cx) / max(1, hw)
            c = (255, 240, 196) if v < 0.35 else (250, 222, 160) if v < 0.7 else (232, 186, 120)
            if (x - xa) % 3 == 1 and 0 < x - xa < xb - xa:
                c = sh(c, 0.93)
            P(d, x, y, c)
    L(d, (cx - top_hw, y0, cx + top_hw, y0), (204, 150, 92))
    L(d, (cx - bot_hw, y1, cx + bot_hw, y1), (255, 246, 214))


# ---------------------------------------------------------------- 梳妆柜 + 镜子
def draw_dresser(S):
    wd = WOOD
    d = S.new('dresser')
    R(d, (160, 110, 190, 112), wd['lt'])                                   # 台面
    L(d, (160, 110, 190, 110), wd['hi'])
    L(d, (160, 112, 190, 112), wd['dk'])
    R(d, (161, 113, 189, 132), wd['md'])                                   # 柜身
    L(d, (161, 113, 161, 132), wd['lt'])
    L(d, (189, 113, 189, 132), wd['dk'])
    for (x0, x1) in ((163, 174), (176, 187)):
        R(d, (x0, 114, x1, 119), wd['lt'])                                   # 抽屉
        L(d, (x0, 119, x1, 119), wd['dd'])
        L(d, (x0, 114, x1, 114), wd['hi'])
        cx = (x0 + x1) // 2
        L(d, (cx - 1, 116, cx + 1, 116), BRASS[2])
        P(d, cx, 117, BRASS[0])
        R(d, (x0, 121, x1, 131), wd['md'])                                   # 柜门
        L(d, (x0, 121, x1, 121), wd['dd'])
        L(d, (x0, 121, x0, 131), wd['dk'])
        L(d, (x0, 131, x1, 131), wd['hi'])
        L(d, (x1, 121, x1, 131), wd['lt'])
        R(d, (x0 + 2, 123, x1 - 2, 129), wd['lt'])
        L(d, (x0 + 2, 123, x1 - 2, 123), wd['dk'])
        L(d, (x0 + 2, 129, x1 - 2, 129), wd['hi'])
    L(d, (175, 113, 175, 132), wd['dd'])
    P(d, 173, 126, BRASS[3])
    P(d, 173, 127, BRASS[0])
    P(d, 178, 126, BRASS[3])
    P(d, 178, 127, BRASS[0])
    R(d, (161, 132, 189, 133), wd['dk'])                                    # 裙边（波浪）+ 弯腿
    for x in range(165, 186):
        if (x - 165) % 7 in (2, 3, 4):
            P(d, x, 134, wd['dk'])
    for (x, dx) in ((161, 1), (189, -1)):
        L(d, (x, 134, x, 136), wd['md'])
        L(d, (x + dx, 134, x + dx, 135), wd['dk'])
        P(d, x + dx, 137, wd['dk'])
        P(d, x + dx, 138, wd['md'])
        P(d, x + 2 * dx, 139, wd['dk'])
        P(d, x + dx, 139, wd['md'])
    R(d, (163, 135, 187, 139), (26, 18, 20))                                # 柜底的暗缝
    L(d, (163, 139, 187, 139), (36, 26, 26))
    # 台面上：兰花（紫）、转盘电话（米白）、房卡钥匙（大铜牌）
    d = S.new('dresser.top')
    R(d, (164, 104, 168, 109), (220, 224, 226))
    L(d, (164, 104, 168, 104), (180, 190, 200))
    P(d, 164, 107, (250, 252, 252))
    L(d, (166, 103, 166, 92), (70, 110, 66))
    L(d, (166, 96, 169, 92), (70, 110, 66))
    L(d, (164, 108, 161, 105), (60, 104, 64))
    L(d, (168, 108, 171, 106), (60, 104, 64))
    for (fx, fy) in ((165, 92), (168, 91), (170, 94), (164, 95), (167, 89)):
        P(d, fx, fy, (190, 100, 190))
        P(d, fx + 1, fy, (226, 150, 220))
        P(d, fx, fy + 1, (150, 66, 150))
    R(d, (178, 105, 186, 109), (222, 214, 190))                              # 电话
    L(d, (178, 105, 186, 105), (240, 234, 214))
    d.ellipse((180, 105, 184, 108), fill=C4((196, 188, 166)))
    P(d, 182, 106, (120, 110, 96))
    R(d, (177, 102, 187, 103), (214, 206, 182))
    P(d, 177, 104, (200, 192, 170))
    P(d, 187, 104, (200, 192, 170))
    L(d, (186, 109, 189, 109), (60, 56, 52))
    R(d, (171, 108, 174, 109), BRASS[2])                                     # 钥匙铜牌
    P(d, 171, 108, BRASS[3])
    L(d, (175, 109, 176, 109), (160, 160, 170))


GLASS_KEY = (1, 2, 3)                                    # 镜面占位色（拼完以后按它找出露出来的镜面）


def draw_mirror(S):
    d = S.new('mirror')
    x0, y0, x1, y1 = MIRROR
    R(d, (x0, y0, x1, y1), BRASS[1])
    L(d, (x0, y0, x1, y0), BRASS[3])
    L(d, (x0, y0, x0, y1), BRASS[2])
    L(d, (x1, y0, x1, y1), BRASS[0])
    L(d, (x0, y1, x1, y1), BRASS[0])
    R(d, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), None, (120, 86, 40))
    for y in range(y0 + 4, y1 - 2, 6):                                         # 金框上的雕花点
        P(d, x0, y, BRASS[3])
        P(d, x1, y + 3, BRASS[1])
    # 顶上的贝壳饰
    d.polygon([(170, y0), (176, y0 - 6), (182, y0)], fill=C4(BRASS[1]))
    L(d, (171, y0 - 1, 176, y0 - 6), BRASS[3])
    L(d, (176, y0 - 5, 176, y0 - 1), BRASS[0])
    P(d, 173, y0 - 2, BRASS[0])
    P(d, 179, y0 - 2, BRASS[2])
    P(d, 176, y0 - 7, BRASS[2])
    # 镜面先填占位色（打光以后再换成反射）
    R(d, GLASS, GLASS_KEY)


# ---------------------------------------------------------------- 藤椅 + 小圆桌 + 行李箱
RATTAN = dict(hi=(214, 180, 120), lt=(192, 156, 100), md=(168, 132, 84), dk=(128, 96, 60), dd=(86, 62, 40))


def rattan_fill(d, pts_mask):
    for (x, y) in pts_mask:
        c = RATTAN['lt'] if (x + y) % 2 == 0 else RATTAN['md']
        if (x // 2 + y // 2) % 3 == 0:
            c = RATTAN['hi'] if (x + y) % 2 == 0 else RATTAN['dk']
        P(d, x, y, c)


def chair_upright(d):
    back = []
    for y in range(104, 126):
        hw = 7 if y > 108 else 7 - (108 - y)
        for x in range(203 - hw, 204 + hw):
            back.append((x, y))
    rattan_fill(d, back)
    d.arc((196, 102, 210, 116), 180, 360, fill=C4(RATTAN['dd']))
    L(d, (196, 109, 196, 126), RATTAN['dd'])
    L(d, (210, 109, 210, 126), RATTAN['dk'])
    for (x0, x1) in ((195, 198), (208, 211)):                               # 扶手
        R(d, (x0, 118, x1, 121), RATTAN['lt'])
        L(d, (x0, 118, x1, 118), RATTAN['hi'])
        L(d, (x0, 121, x1, 121), RATTAN['dd'])
    R(d, (196, 125, 210, 128), RATTAN['md'])                                   # 座
    L(d, (196, 125, 210, 125), RATTAN['hi'])
    L(d, (196, 128, 210, 128), RATTAN['dd'])
    R(d, (198, 122, 208, 125), (150, 60, 50))                                  # 坐垫（红）
    L(d, (198, 122, 208, 122), (186, 86, 70))
    for x in (197, 209):                                                       # 腿
        L(d, (x, 129, x, 140), RATTAN['dk'])
    L(d, (197, 136, 209, 136), RATTAN['dd'])


CHAIR_FALLEN_AT = (190, 131)                              # 倒下的藤椅（转 90° 侧躺）左上角


def chair_fallen_img():
    """狼藉：藤椅侧着倒在桌子前面的地上（直立的样子转 90°：靠背朝左、四条腿朝右）。"""
    im = blank()
    chair_upright(ImageDraw.Draw(im))
    bb = im.getbbox()
    sub = im.crop(bb).transpose(Image.ROTATE_90)
    out = blank()
    out.alpha_composite(sub, CHAIR_FALLEN_AT)
    return out


def draw_table_chair(S, mess):
    d = S.new('chair')
    if not mess:
        chair_upright(d)
    wd = WOOD
    d = S.new('table')
    L(d, (205, 127, 205, 142), wd['dk'])                                       # 柱
    L(d, (206, 127, 206, 142), wd['lt'])
    L(d, (204, 127, 204, 141), wd['md'])
    for (xa, xb) in ((197, 204), (207, 214)):                                   # 三脚
        L(d, (xa, 146, xb, 142) if xa < 205 else (xa, 142, xb, 146), wd['dk'])
    L(d, (204, 143, 206, 143), wd['md'])
    P(d, 196, 146, wd['dd'])
    P(d, 215, 146, wd['dd'])
    d.ellipse((194, 120, 216, 126), fill=C4(wd['lt']))                         # 桌面
    d.arc((194, 120, 216, 126), 180, 360, fill=C4(wd['hi']))
    L(d, (195, 124, 215, 124), wd['md'])
    L(d, (196, 125, 214, 125), wd['dk'])
    L(d, (198, 126, 212, 126), wd['dd'])
    # 桌上：一盘红毛丹 + 玻璃烟灰缸
    d.ellipse((205, 119, 214, 122), fill=C4((210, 214, 220)))
    for (x, y, c) in ((207, 117, (190, 40, 40)), (209, 116, (210, 60, 46)), (211, 117, (180, 36, 40)),
                      (208, 119, (200, 50, 40)), (210, 119, (170, 30, 36)), (212, 119, (196, 46, 40))):
        P(d, x, y, c)
        P(d, x + 1, y, sh(c, 0.8))
        P(d, x, y - 1, (220, 120, 90))
    P(d, 209, 115, (90, 140, 70))
    L(d, (197, 121, 201, 121), (170, 190, 200))
    L(d, (198, 122, 200, 122), (120, 140, 150))
    if mess:
        S.new('chair.fallen')
        S.items[-1][1].alpha_composite(chair_fallen_img())


def draw_luggage(S):
    """波鲁纳雷夫的旧皮箱：立着、圆角、两条皮带 + 铜扣、包角、提手、旅行贴纸、挂一张行李牌。"""
    d = S.new('luggage')
    body, dk, lt, hi = (138, 86, 48), (96, 56, 32), (162, 104, 60), (186, 126, 76)
    x0, y0, x1, y1 = 215, 123, 235, 145
    d.rounded_rectangle((x0, y0, x1, y1), radius=3, fill=C4(dk))
    d.rounded_rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), radius=2, fill=C4(body))
    L(d, (x0 + 3, y0 + 1, x1 - 3, y0 + 1), hi)                                  # 顶边亮
    L(d, (x0 + 1, y0 + 3, x0 + 1, y1 - 3), lt)
    L(d, (x1 - 1, y0 + 3, x1 - 1, y1 - 3), (110, 66, 38))
    L(d, (x0 + 3, y1 - 1, x1 - 3, y1 - 1), (84, 50, 28))
    L(d, (x0 + 2, y0 + 3, x1 - 2, y0 + 3), (120, 74, 42))                      # 箱盖的缝
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):   # 包角
        P(d, cx + sx, cy + sy, (70, 40, 24))
        P(d, cx + 2 * sx, cy + sy, (70, 40, 24))
        P(d, cx + sx, cy + 2 * sy, (70, 40, 24))
        P(d, cx + sx, cy + sy, BRASS[1])
    for x in (220, 230):                                                        # 两条皮带 + 铜扣
        L(d, (x, y0 + 1, x, y1 - 1), (84, 50, 28))
        L(d, (x + 1, y0 + 1, x + 1, y1 - 1), (110, 68, 38))
        R(d, (x - 1, y0 + 6, x + 2, y0 + 8), BRASS[2])
        P(d, x - 1, y0 + 6, BRASS[3])
        P(d, x + 1, y0 + 7, BRASS[0])
    R(d, (222, 119, 228, 122), (70, 42, 24))                                    # 提手
    R(d, (223, 120, 227, 121), (34, 22, 16))
    L(d, (223, 119, 227, 119), (150, 100, 60))
    P(d, 222, 122, BRASS[1])
    P(d, 228, 122, BRASS[1])
    # 旅行贴纸（蓝的、米色圆的、绿的）
    R(d, (223, 128, 228, 132), (64, 104, 170))
    L(d, (224, 130, 227, 130), (230, 226, 210))
    P(d, 224, 129, (240, 210, 90))
    d.ellipse((216, 134, 221, 139), fill=C4((226, 210, 160)))
    d.ellipse((217, 135, 220, 138), outline=C4((180, 50, 50)))
    R(d, (231, 135, 233, 140), (70, 140, 90))
    P(d, 232, 137, (240, 230, 200))
    R(d, (223, 137, 228, 139), (200, 70, 60))
    L(d, (224, 138, 227, 138), (240, 220, 180))
    # 行李牌
    L(d, (228, 121, 231, 124), (200, 190, 160))
    R(d, (230, 124, 233, 129), (236, 226, 196), (150, 130, 100))
    L(d, (231, 126, 232, 126), (120, 110, 100))
    L(d, (216, 146, 234, 146), (40, 26, 20))


# ---------------------------------------------------------------- 棕榈盆栽
def draw_palm(S):
    """墙角一盆散尾葵：圆肚铜盆 + 七片往两边垂下来的羽状叶。"""
    d = S.new('palm')
    fronds = [(-2.45, 22), (-2.15, 30), (-1.88, 36), (-1.62, 40), (-1.38, 34), (-1.12, 26), (-0.88, 18)]
    base = (243.5, 126.0)
    for i, (ang, Lf) in enumerate(fronds):
        x, y = base
        a_ = ang
        curl = (-0.028 if ang < -1.57 else 0.028) * (1.5 if abs(ang + 1.57) > 0.45 else 1.0)
        pts = []
        for s_ in range(Lf):
            a_ += curl
            x += math.cos(a_)
            y += math.sin(a_)
            pts.append((x, y, a_))
        for s_, (fx, fy, fa) in enumerate(pts):
            if s_ > 2 and s_ % 2 == 1:                                          # 小叶：从叶轴往下垂
                k = 1 - s_ / Lf
                ll = 2 + int(round(3 * k))
                for side in (-1, 1):
                    for q in range(1, ll + 1):
                        px_ = fx + side * q * 0.55
                        py_ = fy + q * 0.9
                        c = (62, 110, 60) if q < ll else (44, 82, 48)
                        if side == 1 and q == 1:
                            c = (100, 150, 84)
                        P(d, round(px_), round(py_), c)
        for s_, (fx, fy, fa) in enumerate(pts):                                  # 叶轴压在小叶上面
            P(d, round(fx), round(fy), (92, 136, 72) if s_ < Lf * 0.6 else (76, 120, 64))
    # 圆肚铜盆
    for y in range(127, 140):
        u = (y - 127) / 12.0
        hw = 4.0 + 1.6 * math.sin(math.pi * min(1.0, u * 1.1))
        xa, xb = int(round(243.5 - hw)), int(round(243.5 + hw))
        for x in range(xa, xb + 1):
            v = (x - xa) / max(1, xb - xa)
            c = BRASS[1] if v > 0.75 else BRASS[2] if v > 0.35 else BRASS[3] if v > 0.2 else BRASS[1]
            if x == xa or x == xb:
                c = BRASS[0]
            P(d, x, y, c)
    L(d, (239, 126, 248, 126), BRASS[3])
    L(d, (239, 127, 248, 127), BRASS[0])
    L(d, (240, 132, 247, 132), BRASS[0])
    L(d, (241, 139, 246, 139), BRASS[0])
    L(d, (240, 125, 247, 125), (44, 32, 26))


# ---------------------------------------------------------------- 冰箱
def draw_fridge(S, opened):
    d = S.new('fridge')
    cr = CREAM
    R(d, (250, 111, 276, 140), cr['md'])
    L(d, (250, 111, 276, 111), cr['hi'])                                       # 顶面
    L(d, (250, 112, 276, 112), cr['lt'])
    L(d, (250, 111, 250, 140), cr['dk'])
    L(d, (276, 111, 276, 140), cr['dd'])
    R(d, (251, 134, 275, 138), (78, 78, 82))                                    # 散热格栅
    for x in range(252, 275, 2):
        L(d, (x, 135, x, 137), (120, 120, 124))
    L(d, (251, 134, 275, 134), (60, 60, 64))
    L(d, (251, 138, 275, 138), (150, 148, 140))
    for x in (251, 275):
        P(d, x, 140, (60, 58, 56))
        P(d, x, 139, (90, 88, 84))
    L(d, (252, 140, 274, 140), (40, 36, 34))
    if not opened:
        d.rounded_rectangle((251, 113, 275, 133), radius=2, fill=C4(cr['lt']), outline=C4((120, 116, 104)))
        L(d, (253, 114, 273, 114), cr['hi'])
        L(d, (252, 115, 252, 131), cr['hi'])
        L(d, (274, 115, 274, 131), cr['dk'])
        L(d, (253, 132, 273, 132), cr['dk'])
        R(d, (254, 117, 255, 129), (90, 90, 96))                                # 门把（竖的凹槽 + 镀铬）
        L(d, (254, 117, 254, 129), (210, 214, 220))
        P(d, 255, 129, (60, 60, 66))
        L(d, (262, 116, 267, 116), (190, 196, 204))                             # 铭牌
        P(d, 262, 117, (120, 124, 130))
        for (x, y) in ((274, 116), (274, 130)):                                 # 合页
            P(d, x, y, (150, 150, 156))
    else:
        R(d, (251, 113, 275, 133), (60, 64, 70))                                 # 门框的密封条
        d2 = S.new('fridge.inside', emissive=True)
        for y in range(114, 133):                                               # 内胆：越往里越亮
            for x in range(252, 275):
                u = min(x - 252, 274 - x, y - 114, 132 - y)
                c = (150, 176, 196) if u == 0 else (196, 222, 236) if u == 1 else (226, 242, 250) if u < 4 else (240, 250, 255)
                P(d2, x, y, c)
        P(d2, 254, 115, (255, 255, 240))                                        # 小灯
        P(d2, 255, 115, (255, 255, 226))
        for y in (120, 126):                                                    # 两层空的铁丝格
            L(d2, (252, y, 274, y), (130, 150, 166))
            for x in range(253, 274, 2):
                P(d2, x, y - 1, (186, 206, 220))
            L(d2, (253, y + 1, 273, y + 1), (210, 230, 242))
        R(d2, (253, 128, 273, 132), (206, 228, 240))                             # 下面的果菜盒（空）
        L(d2, (253, 128, 273, 128), (170, 196, 214))
        L(d2, (254, 130, 272, 130), (226, 242, 250))
        # 门：绕右边的合页往右前方打开（看到门的内侧：密封条、两层门架、几瓶饮料）
        d3 = S.new('fridge.door')
        door = [(276, 112), (286, 114), (286, 141), (276, 134)]
        d3.polygon(door, fill=C4(cr['lt']))
        L(d3, (276, 112, 286, 114), cr['hi'])
        L(d3, (286, 114, 286, 141), cr['dk'])
        L(d3, (276, 134, 286, 141), cr['dd'])
        L(d3, (277, 114, 277, 133), (150, 150, 156))
        for x in range(278, 286):
            yt = 114 + (x - 276) * 0.2
            yb = 134 + (x - 276) * 0.7
            P(d3, x, round(yt) + 1, (160, 164, 170))
            P(d3, x, round(yb) - 1, (160, 164, 170))
        for (y0, cols) in ((121, ((60, 130, 70), (120, 70, 40))), (130, ((200, 40, 40), (230, 230, 220)))):
            for k, c in enumerate(cols):
                x = 279 + k * 3
                yy = y0 + round((x - 276) * 0.45)
                R(d3, (x, yy - 4, x + 1, yy), c)
                P(d3, x, yy - 5, sh(c, 1.2))
            L(d3, (278, y0 + 1, 285, y0 + 5), (200, 204, 210))
    # 台面上：托盘、冰桶、倒扣的两只杯子、价目卡
    d = S.new('fridge.top')
    L(d, (253, 110, 273, 110), (70, 50, 40))
    L(d, (254, 109, 272, 109), (110, 80, 60))
    R(d, (256, 103, 261, 108), (176, 182, 190))
    L(d, (256, 103, 261, 103), (226, 230, 236))
    L(d, (256, 104, 256, 108), (220, 226, 232))
    L(d, (261, 104, 261, 108), (110, 116, 124))
    L(d, (257, 102, 260, 102), (120, 126, 134))
    for x0 in (265, 269):
        R(d, (x0, 105, x0 + 2, 108), (170, 196, 206))
        L(d, (x0, 105, x0, 108), (226, 240, 246))
        L(d, (x0 + 2, 105, x0 + 2, 108), (120, 140, 150))
    d.polygon([(262, 108), (263, 104), (264, 108)], fill=C4((236, 232, 220)))
    P(d, 263, 106, (180, 40, 40))


def fridge_cold_spill(floor, opened):
    """冰箱开着：冷白的光照到地板 / 旁边的窗帘 / 墙脚（只在 FRIDGE_BOX 里）。"""
    if not opened:
        return None
    x0, y0, x1, y1 = FRIDGE_BOX
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    box = (xx >= x0 + 1) & (xx < x1 - 1) & (yy >= y0 + 1) & (yy < y1 - 1)
    # 地板上一块梯形的光（开口往前扩）
    fl = (yy >= 140) & box & floor
    t = np.clip((yy - 140) / 24.0, 0, 1)
    xl, xr = 250 - 6 * t, 278 + 9 * t
    inside = (xx >= xl) & (xx <= xr)
    k = np.where(fl & inside, 0.55 * (1 - t) ** 1.3, 0)
    edge = np.clip(np.minimum(xx - xl, xr - xx) / 4.0, 0, 1)
    k *= edge
    # 周围一圈淡淡的（墙、窗帘、棕榈盆）
    dd = np.hypot(xx - 263, (yy - 124) * 1.2)
    k2 = np.where(box, 0.30 * np.clip(1 - dd / 28.0, 0, 1) ** 1.5, 0)
    return k + k2


# ---------------------------------------------------------------- 窗 + 窗帘
def night_view():
    """窗玻璃里的夜景（18×72，自发光）：渐变夜空 + 星星 + 高楼亮窗 + 港口的灯。"""
    x0, y0, x1, y1 = WIN_GLASS
    w, h = x1 - x0 + 1, y1 - y0 + 1
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    hz = HZ                                                          # 海平线（局部 y）
    for y in range(h):
        if y < hz:
            u = y / hz
            c = mix((8, 12, 34), (26, 26, 66), u / 0.72) if u < 0.72 else mix((26, 26, 66), (92, 62, 108), (u - 0.72) / 0.28)
        else:
            u = (y - hz) / (h - hz)
            c = mix((24, 26, 54), (8, 12, 28), u)
        L(d, (0, y, w - 1, y), c)
    for (sx, sy, c) in STARS:
        P(d, sx, sy, c)
    # 远处一排矮楼（淡）
    for (bx0, bx1, top) in ((0, 3, 50), (3, 7, 53), (8, 10, 48), (12, 17, 51)):
        R(d, (bx0, top, bx1, hz - 1), (46, 42, 82))
        for x in range(bx0, bx1 + 1, 2):
            if hash01(x, top, 23) < 0.5:
                P(d, x, top + 2 + int(hash01(x, 24) * 6), (200, 160, 110))
    # 近处几栋高楼（暗）+ 亮着的窗
    for (bx0, bx1, top) in TOWERS:
        R(d, (bx0, top, bx1, hz - 1), (20, 24, 46))
        L(d, (bx0, top, bx1, top), (36, 40, 70))
        L(d, (bx1, top + 1, bx1, hz - 1), (16, 18, 36))
    L(d, (SPIRE[0], SPIRE[1], SPIRE[0], TOWERS[2][2] - 1), (34, 38, 64))      # 最高那栋的天线
    for (bx0, bx1, top) in TOWERS:
        for y in range(top + 2, hz - 1, 2):
            for x in range(bx0 + 1, bx1, 1 if bx1 - bx0 < 4 else 2):
                r = hash01(x, y, 17)
                if r < 0.40 and (x, y) != WIN_BLINK:
                    P(d, x, y, (255, 214, 120) if r < 0.24 else (214, 226, 255) if r < 0.32 else (240, 168, 90))
    P(d, SPIRE[0], SPIRE[1], (110, 30, 30))                                    # 障碍灯（灭的时候）
    P(d, WIN_BLINK[0], WIN_BLINK[1], (40, 40, 60))
    # 港口：海面、码头灯和倒影、远处一条船
    L(d, (0, hz, w - 1, hz), (64, 56, 84))
    for (lx, c) in ((1, (255, 210, 120)), (6, (255, 240, 200)), (10, (255, 196, 106)), (15, (226, 238, 255))):
        P(d, lx, hz - 1, c)
        for k in range(1, 9, 2):
            if hz + k < h:
                P(d, lx, hz + k, sh(c, 0.55 - k * 0.04))
                P(d, lx + (1 if k % 4 == 1 else 0), hz + k + 1, sh(c, 0.32))
    L(d, (4, hz + 6, 11, hz + 6), (30, 30, 50))
    L(d, (5, hz + 5, 9, hz + 5), (40, 40, 62))
    P(d, 5, hz + 4, (255, 240, 220))
    P(d, 10, hz + 5, (220, 60, 50))
    P(d, 7, hz + 4, (255, 220, 160))
    return im


HZ = 62                                                    # 窗外海平线（玻璃里的局部 y）
TOWERS = [(1, 4, 30), (5, 8, 38), (9, 13, 18), (14, 17, 33)]
SPIRE = (11, 11)                                          # 天线顶（障碍灯）
STARS = ((3, 3, (220, 226, 255)), (13, 7, (180, 190, 240)), (6, 13, (160, 170, 230)), (16, 2, (200, 206, 250)),
         (1, 19, (150, 160, 220)))
WIN_BLINK = (6, 46)                                       # 会亮灭的那扇窗


def draw_window(S, torn):
    # 窗框（白漆木）+ 窗台
    d = S.new('window.frame')
    R(d, (283, 43, 306, 120), (214, 212, 200))
    L(d, (283, 43, 306, 43), (236, 234, 222))
    L(d, (306, 43, 306, 120), (160, 158, 148))
    R(d, (281, 120, 308, 122), (224, 222, 210))
    L(d, (281, 120, 308, 120), (246, 244, 232))
    L(d, (281, 122, 308, 122), (140, 138, 128))
    L(d, (282, 123, 307, 123), (120, 110, 90))
    d = S.new('window.view', emissive=True)
    v = night_view()
    S.items[-1][1].alpha_composite(v, (WIN_GLASS[0], WIN_GLASS[1]))
    d = S.new('window.mullion')
    gx0, gy0, gx1, gy1 = WIN_GLASS
    for x in (294, 295):
        L(d, (x, gy0, x, gy1), (200, 198, 188) if x == 294 else (150, 148, 140))
    for y in (69, 93):
        L(d, (gx0, y, gx1, y), (204, 202, 192))
        L(d, (gx0, y + 1, gx1, y + 1), (146, 144, 136))
    L(d, (gx0, gy0, gx1, gy0), (120, 118, 112))
    L(d, (gx0, gy1, gx1, gy1), (226, 224, 214))
    for (gx, gy) in ((288, 52), (298, 74), (289, 99)):                     # 玻璃上的反光
        L(d, (gx, gy + 3, gx + 3, gy), (110, 120, 156))
    # 窗帘：左帘（窄）+ 右帘（宽），都在 y 104 绑起来；最上面帘头
    d = S.new('window.curtain_l')
    curtain(d, 280, 286, PELMET_Y[1], 138, tie=TIE_Y, side='l')
    d = S.new('window.curtain_r')
    curtain(d, 304, 318, PELMET_Y[1], 138, tie=TIE_Y, side='r')
    if torn:
        torn_curtain(S)
    d = S.new('window.pelmet')
    y0, y1 = PELMET_Y
    R(d, (280, y0, 318, y1), VELVET['md'])
    L(d, (280, y0, 318, y0), VELVET['dk'])
    L(d, (280, y0 + 1, 318, y0 + 1), VELVET['hi'])
    L(d, (280, y0 + 2, 318, y0 + 2), VELVET['lt'])
    for x in range(280, 319):                                                # 帘头的波浪下摆 + 金流苏
        ph = (x - 280) % 13
        sag = int(round(2.2 * math.sin(math.pi * ph / 13)))
        for y in range(y1 - 2, y1 + sag + 1):
            P(d, x, y, VELVET['md'] if y < y1 + sag else VELVET['dk'])
        if ph in (3, 4, 5, 6, 7, 8, 9):
            P(d, x, y1 - 3, VELVET['lt'])
        P(d, x, y1 + sag + 1, BRASS[2] if x % 2 == 0 else BRASS[1])
        if x % 2 == 0:
            P(d, x, y1 + sag + 2, BRASS[0])
    L(d, (280, y0 + 5, 318, y0 + 5), BRASS[2])
    for x in (280, 293, 306, 318):                                           # 吊穗
        L(d, (x, y1, x, y1 + 5), BRASS[2])
        P(d, x, y1 + 6, BRASS[3])
        P(d, x, y1 + 7, BRASS[1])
    L(d, (280, y0, 280, y1), VELVET['dk'])
    L(d, (318, y0, 318, y1), VELVET['dd'])


TIE_Y = 104


def curtain(d, x0, x1, y0, y1, tie, side):
    """丝绒落地窗帘：竖褶（亮 / 中 / 暗循环），绑带处收窄，下面再散开。"""
    w = x1 - x0 + 1
    for y in range(y0, y1 + 1):
        if y < tie:
            pinch = (y - y0) / (tie - y0)
            shrink = int(round(pinch ** 2 * (2 if side == 'l' else 3)))
        else:
            shrink = int(round(max(0, 1 - (y - tie) / 14.0) * (2 if side == 'l' else 3)))
        if side == 'l':
            xa, xb = x0, x1 - shrink
        else:
            xa, xb = x0 + shrink, x1
        n = xb - xa + 1
        for i in range(n):
            u = i / max(1, n - 1)
            ph = (u * (w / 3.4)) % 1.0
            c = VELVET['hi'] if ph < 0.18 else VELVET['lt'] if ph < 0.4 else VELVET['md'] if ph < 0.7 else VELVET['dk']
            if y > y1 - 2:
                c = sh(c, 0.8)
            P(d, xa + i, y, c)
        P(d, xa if side == 'r' else xb, y, VELVET['dd'] if side == 'r' else VELVET['hi'])
    # 绑带（金色流苏绳）
    if side == 'l':
        xa, xb = x0, x1 - 2
    else:
        xa, xb = x0 + 3, x1
    L(d, (xa, tie, xb, tie), BRASS[2])
    L(d, (xa, tie + 1, xb, tie + 1), BRASS[0])
    tx = xb if side == 'l' else xa
    for k in range(4):
        P(d, tx, tie + 2 + k, BRASS[2] if k % 2 == 0 else BRASS[1])


def torn_curtain(S):
    """狼藉：右帘被划了三刀（斜的口子露出后面的暗墙，口子边上翻起的布）+ 下摆扯下一片垂着。"""
    d = S.new('window.tear')
    cuts = [((306, 48), (316, 68)), ((305, 74), (317, 96)), ((307, 108), (315, 122))]
    for (xa, ya), (xb, yb) in cuts:
        n = max(abs(xb - xa), abs(yb - ya))
        for s in range(n + 1):
            u = s / n
            x = round(xa + (xb - xa) * u)
            y = round(ya + (yb - ya) * u)
            wdt = 1 if 0.15 < u < 0.85 else 0
            P(d, x, y, (24, 14, 20))
            if wdt:
                P(d, x + 1, y, (40, 26, 30))
                P(d, x - 1, y, VELVET['hi'])
                P(d, x + 2, y + 1, VELVET['dd'])
    # 扯下来的一片
    d.polygon([(309, 124), (316, 124), (314, 139), (311, 137)], fill=C4(VELVET['md']))
    L(d, (309, 124, 311, 137), VELVET['hi'])
    L(d, (316, 124, 314, 139), VELVET['dd'])
    for x in (310, 312, 315):
        P(d, x, 123, (220, 200, 180))


# ---------------------------------------------------------------- 天花板：吊扇（不转的部分）+ 吊灯（关着）
def draw_ceiling(S):
    d = S.new('ceiling_rose')                                                    # 吊扇上面的石膏圆花饰
    cx = FAN_C[0]
    d.ellipse((cx - 14, 4, cx + 14, 9), fill=C4((186, 180, 160)))
    d.ellipse((cx - 14, 4, cx + 14, 9), outline=C4((130, 124, 108)))
    d.ellipse((cx - 9, 5, cx + 9, 8), outline=C4((214, 208, 188)))
    for k in range(-12, 13, 3):
        P(d, cx + k, 8, (150, 144, 126))
    d = S.new('fan')
    R(d, (cx - 4, 8, cx + 4, 10), BRASS[1])                                     # 吊盘
    L(d, (cx - 4, 8, cx + 4, 8), BRASS[3])
    L(d, (cx - 3, 11, cx + 3, 11), BRASS[0])
    L(d, (cx - 1, 12, cx - 1, 25), (60, 46, 34))                                 # 吊杆
    L(d, (cx, 12, cx, 25), (128, 98, 64))
    L(d, (cx + 1, 12, cx + 1, 25), (84, 62, 44))
    R(d, (cx - 2, 18, cx + 2, 19), BRASS[1])                                     # 吊杆上的接头
    L(d, (cx - 2, 18, cx + 2, 18), BRASS[3])
    d.ellipse((cx - 8, 25, cx + 8, 32), fill=C4((96, 70, 46)))                    # 电机罩
    d.arc((cx - 8, 25, cx + 8, 32), 195, 300, fill=C4((156, 118, 76)))
    L(d, (cx - 7, 28, cx + 7, 28), BRASS[2])
    L(d, (cx - 6, 31, cx + 6, 31), (58, 40, 28))
    R(d, (cx - 2, 33, cx + 2, 35), (80, 58, 40))                                  # 底帽 + 吊穗
    L(d, (cx - 2, 33, cx + 2, 33), (120, 90, 60))
    P(d, cx, 36, BRASS[2])
    P(d, cx, 37, BRASS[1])
    d = S.new('pendant')
    for y in range(0, 15):                                                       # 吊链
        P(d, 250, y, BRASS[2] if y % 2 == 0 else BRASS[0])
    R(d, (247, 15, 253, 16), BRASS[1])
    d.pieslice((242, 16, 258, 34), 180, 360, fill=C4((208, 210, 210)))
    L(d, (243, 24, 257, 24), (176, 180, 184))
    L(d, (244, 25, 256, 25), BRASS[1])
    for (x, y) in ((246, 20), (247, 19), (248, 18)):
        P(d, x, y, (236, 238, 236))
    for x in range(250, 257):
        P(d, x, 23, (184, 190, 200))


# ============================================================ 拼 albedo
@lru_cache(maxsize=4)
def build(mess, fridge):
    """返回 (albedo float H×W×3, emissive bool H×W, Pieces)。"""
    a = wall_albedo().copy()
    fl = floor_albedo()
    a[JUNC:] = fl[JUNC:]
    stain(a)
    if mess:
        rug_slashes(a)
    S = Pieces()
    draw_ceiling(S)
    draw_door(S)
    draw_wall_art(S)
    draw_coat(S)
    draw_window(S, torn=mess)
    draw_bed(S, mess)
    draw_stand(S)
    draw_mirror(S)
    draw_dresser(S)
    draw_luggage(S)
    draw_table_chair(S, mess)
    draw_fridge(S, fridge)
    draw_palm(S)
    draw_lamp(S, fallen=mess)
    if mess:
        draw_feathers(S)
    # 接触阴影（家具脚下）
    for (xa, xb, ya, yb, k) in ((60, 141, 146, 149, 0.7), (145, 158, 139, 141, 0.7), (161, 189, 139, 141, 0.7),
                                (195, 216, 145, 148, 0.75), (216, 235, 146, 148, 0.7), (239, 249, 139, 141, 0.7),
                                (250, 277, 140, 142, 0.7), (279, 319, 138, 140, 0.75), (42, 57, 138, 140, 0.8)):
        a[ya:yb + 1, xa:xb] *= k
    emis = np.zeros((H, W), bool)
    cover = np.zeros((H, W), bool)
    img = toimg(np.concatenate([a, np.full((H, W, 1), 255, np.float32)], -1))
    for name, im, e in S.items:
        al = np.array(im)[..., 3]
        img.alpha_composite(im)
        emis = np.where(al >= 128, e, emis)
        if not name.startswith('feathers'):
            cover |= al >= 128
    yy = np.arange(H)[:, None]
    S.floor = (yy >= JUNC) & ~cover                                             # 露出来的地板（打地板的光）
    out = np.array(img).astype(np.float32)[..., :3]
    S.glass = (out == np.array(GLASS_KEY, np.float32)).all(-1)               # 露出来的镜面（台面上的东西挡住的不算）
    return out, emis, S


# ============================================================ 打光
AMB_WALL, AMB_FLOOR = 0.33, 0.50
LAMP_R, LAMP_K = 136.0, 0.98


def quant(Lv, n, bay):
    return np.floor(Lv * n + 0.5 + (bay - 0.5) * 0.3) / n


CONE_TOP = 48                                            # 灯罩上口那道光照到的最高处


def cone_mask(mess):
    """灯罩上下口照到墙上的两道光（台灯倒了就没有）。返回强度（H×W）。"""
    k = np.zeros((H, W), np.float32)
    if mess:
        return k
    cx = LAMP_C[0]
    for y in range(CONE_TOP, 88):
        hw = 6.5 + (88 - y) * 0.62
        u = 1 - (88 - y) / float(88 - CONE_TOP)
        for x in range(int(cx - hw) - 1, int(cx + hw) + 2):
            if 0 <= x < W:
                e = hw - abs(x - cx + 0.5)
                if e > 0:
                    k[y, x] = 0.42 * u ** 1.1 * min(1.0, e / 1.5)
    for y in range(101, 114):
        hw = 7 + (y - 101) * 0.7
        for x in range(int(cx - hw), int(cx + hw) + 1):
            k[y, x] = max(k[y, x], 0.34)
    return k


@lru_cache(maxsize=4)
def light_field(mess, fridge):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bay = A._bayer(W, H)
    floor = build(mess, fridge)[2].floor
    dl = np.hypot(xx - LAMP_C[0], (yy - LAMP_C[1]) * 1.15)
    sl = np.clip(1 - dl / LAMP_R, 0, 1) ** 1.45
    dw = np.hypot(xx - 294, (yy - 86) * 0.7)
    sw = np.clip(1 - dw / 84.0, 0, 1) ** 2.0
    amb = np.where(floor, AMB_FLOOR, AMB_WALL + 0.05 * np.clip((yy - 112) / 30.0, 0, 1)).astype(np.float32)
    amb = amb - 0.08 * np.clip((24 - yy) / 24.0, 0, 1)                    # 天花板一带更暗
    amb = amb - 0.06 * np.clip((60 - xx) / 60.0, 0, 1) * (yy < JUNC)      # 门那一角暗一点
    # 床在台灯左前方投下的影子（地板上）
    shadow = np.zeros((H, W), np.float32)
    for y in range(147, 158):
        t = (y - 147) / 11.0
        xa, xb = 58 - 6 * t, 138 - 14 * t
        shadow[y, int(xa):int(xb)] = 0.16 * (1 - t)
    shadow *= floor
    # 地板：窗外冷光照进来的一块（斜着往左前方）
    win_fl = np.zeros((H, W), np.float32)
    for y in range(JUNC, H):
        t = (y - JUNC) / (H - JUNC)
        c = 296 - 34 * t
        hw = 9 + 10 * t
        e = np.clip((hw - np.abs(xx[y] - c)) / 4.0, 0, 1)
        win_fl[y] = 0.16 * e * (1 - 0.6 * t)
    win_fl *= floor
    # 门缝漏进来的走廊灯：门前地板上一小片暖光
    door_fl = np.zeros((H, W), np.float32)
    for y in range(JUNC, JUNC + 9):
        t = (y - JUNC) / 9.0
        e = np.clip((11 + 4 * t - np.abs(xx[y] - 20)) / 3.0, 0, 1)
        door_fl[y] = 0.40 * e * (1 - t) ** 1.3
    door_fl *= floor
    cone = cone_mask(mess)
    I = amb + LAMP_K * sl + 0.32 * sw + cone + win_fl + door_fl - shadow
    cold = fridge_cold_spill(floor, fridge)
    if cold is not None:
        I = I + cold
    else:
        cold = np.zeros((H, W), np.float32)
    q = np.where(floor, quant(I, 22, bay), quant(I, 16, bay))          # 地板分得细一点（可走带不出一圈圈的光带）
    ambT = np.array((0.74, 0.84, 1.18), np.float32)
    lampT = np.array((1.24, 0.98, 0.66), np.float32)
    winT = np.array((0.72, 0.92, 1.34), np.float32)
    coldT = np.array((0.88, 1.04, 1.20), np.float32)
    wa, wl, ww, wc = amb, LAMP_K * sl + cone + door_fl, 0.32 * sw + win_fl, cold
    tot = wa + wl + ww + wc + 1e-6
    tint = (wa[..., None] * ambT + wl[..., None] * lampT + ww[..., None] * winT + wc[..., None] * coldT) / tot[..., None]
    m = q[..., None] * tint
    return m


@lru_cache(maxsize=4)
def lit(mess, fridge):
    alb, emis, S = build(mess, fridge)
    m = light_field(mess, fridge)
    out = np.where(emis[..., None], alb, np.clip(alb * m, 0, 255))
    out = np.maximum(out, 6)
    im = toimg(np.concatenate([out, np.full((H, W, 1), 255, np.float32)], -1))
    # 灯罩一圈柔光 + 地板上的倒影
    if not mess:
        A._glow(im, LAMP_C[0], LAMP_C[1] + 1, 15, 12, (255, 200, 120), 46, rings=3)
        A._blend_rect(im, (148, 140, 154, 146), (255, 200, 130), 22)
        A._blend_rect(im, (150, 140, 152, 147), (255, 210, 150), 22)
    else:
        A._glow(im, 157, 143, 18, 9, (255, 196, 120), 50, rings=3)
    # 窗：玻璃周围一圈冷光，窗台上反光
    A._glow(im, 295, 82, 13, 34, (120, 150, 230), 16, rings=2)
    # 空调待机灯
    A._glow(im, 29, 35, 2, 2, (255, 60, 50), 60, rings=1)
    if fridge:
        A._glow(im, 263, 123, 18, 16, (200, 236, 255), 36, rings=3)
        A._blend_rect(im, (252, 141, 276, 143), (230, 246, 255), 40)
        mist(im)
    # 自发光的东西压在光晕上面重画一次（保持清楚）
    a = np.array(im)
    a[emis] = np.concatenate([alb, np.full((H, W, 1), 255, np.float32)], -1).astype(np.uint8)[emis]
    im = Image.fromarray(a, 'RGBA')
    return im


def mist(im):
    """冰箱冒出来的一点冷气（静态）。"""
    d = ImageDraw.Draw(im)
    lay = blank()
    ld = ImageDraw.Draw(lay)
    for i in range(7):                                                   # 从门缝底下漫出来的几小团
        x = hrange(250, 282, i, 1)
        y = hrange(137, 145, i, 2)
        rx, ry = hrange(2, 4, i, 3), hrange(1, 1.8, i, 4)
        ld.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(214, 236, 248, 70))
    for i in range(6):
        ld.point((int(hrange(252, 280, i, 5)), int(hrange(138, 145, i, 6))), fill=(240, 250, 255, 150))
    im.alpha_composite(lay)


MIRROR_SRC = (134, 74)


def mirror_fill(im, glass):
    """镜面：房间（取左边台灯 + 灯罩照亮的墙那一块，左右翻转、压暗、偏蓝）+ 两道斜反光。
    始终用 (0, 0) 状态的房间；glass = 露出来的镜面像素（台面上的兰花 / 电话挡住的不动）。"""
    src = lit(0, 0)
    x0, y0, x1, y1 = GLASS
    w, h = x1 - x0 + 1, y1 - y0 + 1
    crop = np.array(src.crop((MIRROR_SRC[0], MIRROR_SRC[1], MIRROR_SRC[0] + w, MIRROR_SRC[1] + h))
                    .transpose(Image.FLIP_LEFT_RIGHT)).astype(np.float32)
    rgb = crop[..., :3] * np.array((0.62, 0.70, 0.86), np.float32) + np.array((8, 12, 26), np.float32)
    ref = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ra = np.zeros((H, W, 4), np.uint8)
    ra[y0:y1 + 1, x0:x1 + 1, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    ra[y0:y1 + 1, x0:x1 + 1, 3] = 255
    ref = Image.fromarray(ra, 'RGBA')
    d = ImageDraw.Draw(ref)
    for k in range(10):                                                        # 斜反光
        P(d, x0 + 4 + k, y0 + 17 - k, (176, 196, 220))
        if k < 8:
            P(d, x0 + 6 + k, y0 + 17 - k, (140, 160, 196))
    for k in range(5):
        P(d, x1 - 5 + k, y1 - 1 - k, (150, 170, 206))
    a = np.array(im)
    a[glass] = np.array(ref)[glass]
    return Image.fromarray(a, 'RGBA')


@lru_cache(maxsize=4)
def render(mess, fridge):
    """第 (mess, fridge) 状态的整张底图（320×180，不透明，不含 strip）。"""
    return mirror_fill(lit(mess, fridge), build(mess, fridge)[2].glass)


# ============================================================ 会动的：吊扇叶片、窗外
@lru_cache(maxsize=1)
def fan_palette():
    m = light_field(0, 0)[FAN_C[1] + 2, FAN_C[0]]
    under = np.clip(np.array((150, 104, 68), np.float32) * m * 1.15, 0, 255)
    top = np.clip(np.array((110, 74, 48), np.float32) * m, 0, 255)
    edge = np.clip(np.array((60, 40, 28), np.float32) * m, 0, 255)
    iron = np.clip(np.array(BRASS[2], np.float32) * m * 1.1, 0, 255)
    return [tuple(int(v) for v in c) for c in (under, top, edge, iron)]


BLADE = [(5, -1.2), (9, -2.6), (12, -3.6), (29, -3.6), (31, -3.0), (32, -1.8),
         (32, 1.8), (31, 3.0), (29, 3.6), (12, 3.6), (9, 2.6), (5, 1.2)]


def fan_frame(t):
    """叶片：四片木桨叶在一个水平面里转（从下面往上看，近的叶片在上、远的在下），近的后画。"""
    img = blank()
    d = ImageDraw.Draw(img)
    f = int(math.floor(t * FAN_FPS + 1e-6)) % N_FAN
    th0 = (math.pi / 2) * f / N_FAN + 0.3
    under, top, edge, iron = fan_palette()
    far = sh(under, 0.78)
    cx, cy = FAN_C
    blades = sorted([th0 + k * math.pi / 2 for k in range(4)], key=lambda th: math.sin(th))   # 远的先画
    for th in blades:
        c, s = math.cos(th), math.sin(th)
        proj = lambda r, w: (cx + r * c - w * s, cy - (r * s + w * c) * FAN_E)   # noqa: E731
        poly = [proj(r, w) for (r, w) in BLADE]
        near = s > 0
        d.polygon(poly, fill=C4(under if near else far))
        # 叶片的厚度：靠下的那条边一道暗线；靠上的那条边亮一点
        e1 = [proj(r, w) for (r, w) in BLADE[:6]]
        e2 = [proj(r, w) for (r, w) in BLADE[6:]]
        lo, hi_ = (e1, e2) if sum(p[1] for p in e1) > sum(p[1] for p in e2) else (e2, e1)
        d.line([(x, y + 1) for (x, y) in lo], fill=C4(edge))
        d.line(hi_, fill=C4(sh(under, 1.15) if near else under))
        # 铜叶架
        d.line([proj(3, 0), proj(11, 0)], fill=C4(iron), width=1)
    return img


def night_anim(t):
    """窗外会动的像素（只画亮的那一刻；底图里是暗的）：航空障碍灯 2 s 闪一次、两颗星闪、一扇窗灯亮灭。"""
    img = blank()
    d = ImageDraw.Draw(img)
    f = int(math.floor(t * WIN_FPS + 1e-6)) % N_WIN
    x0, y0 = WIN_GLASS[0], WIN_GLASS[1]
    sx, sy = x0 + SPIRE[0], y0 + SPIRE[1]
    if f in (0, 1, 2):                                                 # 最高那栋楼顶的红灯
        P(d, sx, sy, (255, 70, 60))
        if f == 1:
            P(d, sx - 1, sy, (190, 50, 50))
            P(d, sx + 1, sy, (190, 50, 50))
            P(d, sx, sy - 1, (190, 50, 50))
    (s1x, s1y, _), (s2x, s2y, _) = STARS[0], STARS[3]
    if f in (4, 5, 6, 7):                                              # 星星
        P(d, x0 + s1x, y0 + s1y, (255, 255, 255))
        if f in (5, 6):
            P(d, x0 + s1x - 1, y0 + s1y, (150, 160, 220))
            P(d, x0 + s1x + 1, y0 + s1y, (150, 160, 220))
    if f in (10, 11, 12):
        P(d, x0 + s2x, y0 + s2y, (255, 255, 255))
    if 6 <= f < 14:                                                    # 一扇窗亮着
        P(d, x0 + WIN_BLINK[0], y0 + WIN_BLINK[1], (255, 220, 130))
    return img


# ============================================================ 导出 + 自检
def overlay_of(mess, fridge, box=None):
    """和 (0, 0) 不一样的像素（其余透明）；box 给出时裁成框。"""
    base = np.array(render(0, 0))
    cur = np.array(render(mess, fridge))
    diff = (base != cur).any(-1)
    out = np.zeros_like(cur)
    out[diff] = cur[diff]
    im = Image.fromarray(out, 'RGBA')
    return im.crop(box) if box else im


def anchors():
    return dict(
        door=[20, 156], bed=[100, 152], hide_bed=[100, 170], mirror=[176, 152], hide_cabinet=[175, 168],
        luggage=[225, 160], fridge=[263, 152], hide_fridge=[263, 170], window=[294, 152],
        lamp=[151, 152], table=[205, 158],
        # 物件本身的位置（调查点的气泡 / 特效可以照这个放）
        mirror_center=[176, 90], window_center=[294, 82], fridge_door=[263, 123], lamp_shade=[151, 94],
        bed_gap=[66, 139, 134, 146], cabinet_gap=[163, 135, 187, 139], fan=[FAN_C[0], FAN_C[1]],
        lamp_fallen=[150, 143], clock=[222, 62],
        walk_x=[14, 308])


def direct(t, mess=0, fridge=0):
    im = render(mess, fridge).copy()
    im.alpha_composite(night_anim(t))
    im.alpha_composite(fan_frame(t))
    return im


def export(ex, BJ):
    layers = [dict(type='static', image=ex.img('room', render(0, 0)))]
    layers.append(ex.bake('night', WIN_BOX, N_WIN, WIN_FPS, night_anim, screen=False, k=1.0))
    fr = [ex.img('fridge0', blank(FRIDGE_BOX[2] - FRIDGE_BOX[0], FRIDGE_BOX[3] - FRIDGE_BOX[1])),
          ex.img('fridge1', overlay_of(0, 1, FRIDGE_BOX))]
    layers.append(dict(type='pick', images=fr, key='fridge', values=[0, 1], x=FRIDGE_BOX[0], y=FRIDGE_BOX[1], k=1.0))
    ms = [ex.img('mess0', blank()), ex.img('mess1', overlay_of(1, 0))]
    layers.append(dict(type='pick', images=ms, key='mess', values=[0, 1], x=0, y=0, k=1.0))
    layers.append(ex.bake('fan', FAN_BOX, N_FAN, FAN_FPS, fan_frame, screen=False, k=1.0))
    st = ex.stage(W, GROUND, WALK, layers, [], anchors())
    if ex.check_on:
        checks(ex, BJ, st)
    return st


def _in_any(boxes, shape):
    m = np.zeros(shape, bool)
    for (x0, y0, x1, y1) in boxes:
        m[y0:y1, x0:x1] = True
    return m


def checks(ex, BJ, st):
    imgs = ex.images
    base = np.array(render(0, 0))
    # 1 底图整屏不透明、不露黑
    ex.checked('底图整屏不透明', int((base[..., 3] != 255).sum()))
    ex.checked('四种状态整屏不露黑', sum(int((np.array(BJ.ref_render(st, imgs, 0, 0.3, {'mess': m, 'fridge': f})
                                                  .convert('RGB')).sum(-1) == 0).sum()) for m in (0, 1) for f in (0, 1)))
    # 2 导出层 vs 直接拼（四种状态 × 几个时刻）
    for m in (0, 1):
        for f in (0, 1):
            for t in (0.0, 0.45, 1.3, 2.0):
                got = BJ.ref_render(st, imgs, 0, t, {'mess': m, 'fridge': f})
                ex.checked('mess %d fridge %d t %.2f 导出 vs 直接拼' % (m, f, t), BJ.ndiff_rgba(got, direct(t, m, f)))
    # 3 strip 闭合
    ex.checked('吊扇叶片 %d 帧（1/4 圈）闭合' % N_FAN, BJ.ndiff_rgba(fan_frame(0).crop(FAN_BOX), fan_frame(N_FAN / FAN_FPS).crop(FAN_BOX)))
    ex.checked('窗外 2 s 闭合', BJ.ndiff_rgba(night_anim(0).crop(WIN_BOX), night_anim(N_WIN / WIN_FPS).crop(WIN_BOX)))
    steps = [BJ.ndiff_rgba(fan_frame(i / FAN_FPS), fan_frame((i + 1) / FAN_FPS)) for i in range(N_FAN)]
    ex.checked('吊扇每一步变化差不多（不跳帧：最大 ≤ 1.6 × 中位）%s' % steps,
               int(max(steps) > 1.6 * float(np.median(steps))))
    fan_bb = Image.fromarray(np.max([np.array(fan_frame(i / FAN_FPS))[..., 3] for i in range(N_FAN)], 0)).getbbox()
    ex.checked('吊扇叶片都在 strip 的框里 %s' % (fan_bb,),
               int(not (fan_bb[0] >= FAN_BOX[0] and fan_bb[1] >= FAN_BOX[1] and fan_bb[2] <= FAN_BOX[2] and fan_bb[3] <= FAN_BOX[3])))
    nb = Image.fromarray(np.max([np.array(night_anim(i / WIN_FPS))[..., 3] for i in range(N_WIN)], 0)).getbbox()
    ex.checked('窗外会动的像素都在玻璃里', int(not (nb[0] >= WIN_BOX[0] and nb[1] >= WIN_BOX[1] and nb[2] <= WIN_BOX[2] and nb[3] <= WIN_BOX[3])))
    # 4 锚点都在地图里
    bad = 0
    for k, v in st['anchors'].items():
        if k == 'walk_x':
            bad += int(not (0 <= v[0] < v[1] <= W))
            continue
        vs = v if isinstance(v[0], (list, tuple)) else [v]
        for p in vs:
            for i in range(0, len(p), 2):
                bad += int(not (0 <= p[i] <= W and 0 <= p[i + 1] <= H))
    ex.checked('锚点都在地图里（%d 个）' % len(st['anchors']), bad)
    wx = st['anchors']['walk_x']
    bad = 0
    for k in ('door', 'bed', 'hide_bed', 'mirror', 'hide_cabinet', 'luggage', 'fridge', 'hide_fridge', 'window', 'lamp', 'table'):
        x, y = st['anchors'][k]
        bad += int(not (wx[0] <= x <= wx[1] and WALK[0] <= y <= WALK[1]))
    ex.checked('站位锚点都在可走范围里（walk_x × 可走带）', bad)
    # 5 pick 每张尺寸一致、两张 pick 不重叠
    for L_ in st['layers']:
        if L_['type'] == 'pick':
            sizes = {imgs[k].size for k in L_['images']}
            ex.checked('pick %s 两张尺寸一致 %s' % (L_['key'], sorted(sizes)), len(sizes) - 1)
            ex.checked('pick %s 第 0 张是空的' % L_['key'], int((np.array(imgs[L_['images'][0]])[..., 3] > 0).sum()))
    fo = np.zeros((H, W), bool)
    fo[FRIDGE_BOX[1]:FRIDGE_BOX[3], FRIDGE_BOX[0]:FRIDGE_BOX[2]] = np.array(overlay_of(0, 1, FRIDGE_BOX))[..., 3] > 0
    mo = np.array(overlay_of(1, 0))[..., 3] > 0
    ex.checked('fridge 和 mess 的像素不重叠', int((fo & mo).sum()))
    # 6 fridge 只在冰箱区域不同、mess 只在狼藉的物件处不同
    d01 = (np.array(render(0, 1)) != base).any(-1)
    ex.checked('fridge 1 只在冰箱区域 %s 不同（框外差异像素）' % (FRIDGE_BOX,),
               int((d01 & ~_in_any([FRIDGE_BOX], d01.shape)).sum()), extra='框内 %d px' % int(d01.sum()))
    d10 = (np.array(render(1, 0)) != base).any(-1)
    ex.checked('mess 1 只在狼藉的物件处不同（框外差异像素）', int((d10 & ~_in_any(MESS_BOXES.values(), d10.shape)).sum()),
               extra='框内 %d px' % int(d10.sum()))
    for name, box in MESS_BOXES.items():
        x0, y0, x1, y1 = box
        ex.checked('mess 1 的 %s 那一块确实变了' % name, int(not d10[y0:y1, x0:x1].any()))
    d11 = np.array(render(1, 1))
    comb = base.copy()
    comb[d10] = np.array(render(1, 0))[d10]
    comb[d01] = np.array(render(0, 1))[d01]
    ex.checked('mess + fridge 同时打开 = 两张各自叠上去', int((comb != d11).any(-1).sum()))
    # 7 家具 x 范围（含两端）和规格一致
    _, _, S = build(0, 0)
    for k, (xa, xb) in SPEC_X.items():
        bb = S.bbox(k)
        ex.checked('家具 %s x 范围 %d–%d（实际 %d–%d）' % (k, xa, xb, bb[0], bb[2]), int(bb[0] != xa) + int(bb[2] != xb))
    # 家具都在可走带后面（底边 < 148）
    bad = []
    for n, im, e in S.items:
        bb = im.getchannel('A').getbbox()
        if bb and bb[3] - 1 >= WALK[0] and not n.startswith('feathers'):
            bad.append(n)
    ex.checked('家具都不进可走带（底边 < %d）%s' % (WALK[0], bad), len(bad))
    _, _, S1 = build(1, 1)
    bad = []
    for n, im, e in S1.items:
        bb = im.getchannel('A').getbbox()
        if bb and bb[3] - 1 >= WALK[0] and not n.startswith('feathers'):
            bad.append(n)
    ex.checked('狼藉 / 冰箱开着的东西也不进可走带 %s' % bad, len(bad))
    # 8 可走带的对比度（地板纹理压低）：y 150–176 亮度横向差 > 24 的像素比例 ≤ 4%
    Y = base[..., :3].astype(np.float32) @ np.array((0.299, 0.587, 0.114), np.float32)
    band = Y[150:177]
    edges = int((np.abs(np.diff(band, axis=1)) > 24).sum())
    ex.checked('可走带 y 150–176 强边像素（≤ 4%）', edges, limit=int(0.04 * band.size))
    # 9 体积
    tot = 0
    for k in set(k for L_ in st['layers'] for k in ([L_.get('image')] + list(L_.get('images') or [])) if k):
        bio = io.BytesIO()
        imgs[k].save(bio, 'PNG', optimize=True)
        tot += bio.tell()
    ex.checked('整张背景 ≤ 400 KB（%.1f KB）' % (tot / 1024), int(tot > 400 * 1024))


# ============================================================ 单独预览
if __name__ == '__main__':
    out_dir = os.path.join(HERE, '_preview', 'ch3')
    os.makedirs(out_dir, exist_ok=True)
    tiles = [direct(0.3, m, f) for (m, f) in ((0, 0), (0, 1), (1, 0), (1, 1))]
    sheet = Image.new('RGB', (W * 2 + 4, H * 2 + 4), (16, 16, 20))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert('RGB'), ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    p = os.path.join(out_dir, 'singapore_hotel_solo.png')
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(p)
    print('ok', p)
