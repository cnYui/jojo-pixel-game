# -*- coding: utf-8 -*-
r"""mansion_stairs —— 终章「DIO 的馆」大楼梯（地图 stairs_fin，F-02：波鲁纳雷夫一级级爬向 DIO，爬到第 10 级时间被停住，
最后承太郎他们打穿右边的墙冲进来）。2026-10-20 mansion 组（b）按体验版精度从头画。零件在 mansion_parts_b.py / mansion_parts.py。

地图 320 宽、ground 160、可走带 y 146–174；夜；侧视平视（正对着楼梯的侧面）。
**踏面必须正好在 15 个脚点上**（波鲁纳雷夫一级级爬，脚底 = 脚点）：第 i 级（i = 0…14）的踏面是 x 34+12i … 45+12i、最上面一行 y = 160−6i；
脚点 = (40+12i, 160−6i) = 踏面中间那一格的正上方（人物脚底最后一行 = y−1，踏面第一行就是 y）。第 1 级比最下面的地（y 166）高 6 px。
自检里逐级核对：脚点那一行是红地毯的亮边、正上面一行不是台阶。

从左到右（世界坐标）：
  x 0–33     楼下：入口的大门（波鲁纳雷夫从这里进来，anchors.bottom [18,166]）、墙纸 + 护墙板；楼梯起点一根大立柱（前景，fg）
  x 34–213   大楼梯：红地毯铺在台阶上（每级的竖面也包着地毯、拐角一根铜杆）、侧板是桃花心木 + 一块块凸板；斜着的护墙板 + 腰线 + 墙纸，
             墙上三幅肖像沿楼梯往上挂（眼睛会转）、三个壁烛台、一盏大吊灯（x 96，烛火 + 水晶闪）；前景一道雕花扶手 + 栏杆（fg，在人前面，
             栏杆高出台阶 10 px = 人的腰，挡不到上半身）
  x 198–272  平台背后的大尖拱窗（三扇窗格，anchors.moon_window [236,40]）：夜空、一轮满月、星星、云从月亮前飘过、一只蝙蝠飞过；窗是逆光：
             DIO（剧情摆，逆光剪影 alpha .7）站在 anchors.landing [214,76]，背后就是最亮的窗格
  x 214–319  顶上平台（y 76）：红地毯 + 金边、檐口线脚的前沿；平台右端一扇门（anchors.exit [267,76] 是走到那里“出场”的位置，门在它右边）
  平台下面  x 214–319：墙纸 + 护墙板、条案和花瓶、一副铠甲、一幅大画像；右边墙上 x 284–318 就是被打穿的地方（key wall_broken）
  地面       深色大理石板（可走带 y 146–174，压平）
图层（从后往前）：
  base       pano k 1             整张底图（已打光，不透明）：墙、楼梯、窗、平台、地
  wallbroken static key wall_broken  墙被打穿：边缘是碎砖 / 灰泥的断面、洞里是夜里的院子（天、树篱、草地）、洞口漏进来的冷光落在地上
  moonclouds / bat   strip         窗里：云从月亮前面飘过（整图周期 = 窗宽，首尾闭合）、一只蝙蝠飞过
  flames0–2  strip                三个壁烛台的火苗；chand 吊灯的 6 根烛 + sparkle 水晶闪；candel 平台上的烛台
  eyes       strip                三幅肖像的眼珠（慢慢转）
  motes      strip                月光里飘的浮尘
  dust       strip key wall_broken  洞口飘起来的灰尘
  rail       fg                   前景：雕花扶手 + 栏杆 + 两头的立柱（在人物前面）
锚点（素材总表定稿）：steps（15 个脚点）、bottom [18,166]、top [266,76]、landing [214,76]、moon_window [236,40]、wall_break [300,140]、exit [267,76]；
      另导出 hole_box（墙洞的框）、door_box（平台右端门的门洞）、stair_box（楼梯整体的框）。
key：wall_broken（0 / 1）= 右边的墙被打穿（承太郎他们从洞里冲进来；碎砖由剧情画，背景只留断面 + 洞 + 洞口的光）。
单独运行：python -B tools\bg_new\mansion_stairs.py → tools\bg_new\_preview\final\after\mansion_stairs_solo.png
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
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from engine.core import gradient, hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _load(key, fname):
    """importlib 按路径加载同目录的零件模块（模块名固定，进程里只加载一份）。"""
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, fname))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


M = _load('bg_new_mansion_parts', 'mansion_parts.py')
B = _load('bg_new_mansion_parts_b', 'mansion_parts_b.py')
dk, lt, hl, vl, px, rect = M.dk, M.lt, M.hl, M.vl, M.px, M.rect
INK = M.INK
H = M.H
N8 = M.N8
FPS = M.FPS_SLOW
FPS_FIRE = M.FPS_FIRE

PW = 320
GROUND = 160
WALK = (146, 174)
FLOOR_Y = 148                                  # 后墙和地的交线
STAIR_FLOOR = 166                              # 楼梯脚下的地（bottom 锚点就站在这）
NST, SW, SH = 15, 12, 6                        # 15 级，每级宽 12、高 6
X0 = 34                                        # 第 0 级的左沿
LAND_X, LAND_Y = 214, 76                       # 顶上平台的左沿 / 脚点 y
STEPS = [[40 + SW * i, 160 - SH * i] for i in range(NST)]

ANCHORS = {
    'steps': STEPS,
    'bottom': [18, 166],
    'top': [266, 76],
    'landing': [214, 76],
    'moon_window': [236, 40],
    'wall_break': [300, 140],
    'exit': [267, 76],
}
REQUIRED = tuple(ANCHORS)
STAND = ('bottom', 'top', 'landing', 'exit')   # 站人的点（y 在可走带里的不查：楼梯 / 平台本来就在可走带上面）

HOLE = [(292, 148), (288, 141), (289, 133), (285, 125), (288, 118), (285, 108), (290, 98), (297, 93), (305, 93),
        (310, 92), (315, 99), (313, 109), (318, 116), (315, 124), (317, 132), (314, 140), (316, 148)]   # 洞要把墙上那幅画（y 94–118）整个吞进去，最高点 y 92；断面一圈再往上顶多碰到平台前沿线脚的最后两行
WIN = dict(cx=236, y_top=10, y_bot=64, gw=73, rise=34)
MULL_X = (224, 248)
TRANSOM_Y = 47
EXIT_DOOR = (284, 28, 22, 48)                  # 平台右端的门：门洞 x0, y0（拱顶）, w, h → 门槛行 y0+h−1 = 75
SCONCES = [(91, 91), (141, 66), (183, 45)]     # 壁烛台（x, 托盘行）：沿楼梯往上
PORTRAITS = [(66, 'noble'), (116, 'lady'), (166, 'old')]
CHAND = dict(cx=96, y_top=6, y_ring=36)

# 配色
PAPER_N = dict(base=(88, 24, 42), dk=(70, 17, 34), lt=(108, 36, 52), gold=(140, 98, 60))     # 夜里的暗红锦缎墙纸
CAR = dict(hi=(236, 100, 104), top=(196, 48, 66), mid=(150, 30, 50), dk=(104, 20, 38), riser=(126, 24, 42),
           rod=(238, 198, 100), rod_d=(150, 112, 52))                                          # 地毯（红）+ 铜杆
FLAG_H = dict(hi=(100, 96, 120), lt=(84, 80, 104), md=(66, 62, 86), dk=(48, 44, 68), dd=(28, 24, 44))   # 大厅的深色大理石板
RAIL = dict(hi=(226, 162, 108), lt=(190, 122, 76), md=(140, 84, 50), dk=(92, 52, 32), dd=(52, 28, 20))   # 扶手：打过蜡的亮一档的木头，才分得出侧板
T_FLOOR = (0.98, 0.96, 1.06)                   # 地面铺平的那层光：偏冷
T_STAIR = (1.30, 0.98, 0.78)                   # 楼梯上补的一层暖光（让红地毯在夜里看得清）
T_MOON2 = (0.84, 0.95, 1.22)                   # 窗里的月光：比 T_MOON 少一点蓝（石套、窗台不要被染成荧光蓝）


def pitch(x):
    """楼梯的“节线”（各级前沿 (34+12i, 160−6i) 连成的斜线，斜率 −0.5）。"""
    return 160 - (x - X0) / 2.0


# ============================================================ 底图：墙 / 楼梯 / 窗 / 平台 / 地
def _stairs_body(cv):
    """楼梯本体：整块桃花心木侧板（从锯齿顶一直到地面），上面包红地毯：踏面 3 行（亮边 / 面 / 暗边）+ 竖面 2 px 宽（也包着地毯），
    竖面最下面一行是铜杆（把地毯压在拐角里）。侧板下半是一块块凸板（每两级一块，板顶跟着台阶一级级抬高），脚下一条踢脚板。"""
    d = cv.d
    WD = M.WOOD
    for i in range(NST):
        x0 = X0 + SW * i
        yt = 160 - SH * i
        rect(d, x0, yt, x0 + SW - 1, STAIR_FLOOR - 1, WD['md'])
        for x in range(x0, x0 + SW):                                  # 侧板的木纹：竖向细纹，亮暗相间
            if hash01(i, x, 5) < 0.4:
                vl(d, x, yt + 4 + int(hash01(i, x, 6) * 6), min(STAIR_FLOOR - 4, yt + 12 + int(hash01(i, x, 7) * 24)), WD['dk'])
    # 凸板
    for k in range(1, 8):
        xa = X0 + 2 * SW * k + 2
        xb = min(X0 + SW * NST - 2, xa + 2 * SW - 5)
        ya = 160 - SH * min(NST - 1, 2 * k + 1) + 11
        yb = STAIR_FLOOR - 5
        if yb - ya < 5 or xb - xa < 4:
            continue
        rect(d, xa, ya, xb, yb, WD['md'], outline=WD['dd'])
        hl(d, xa + 1, xb - 1, ya + 1, WD['lt'])
        vl(d, xa + 1, ya + 1, yb - 1, WD['lt'])
        hl(d, xa + 1, xb - 1, yb - 1, WD['dk'])
        vl(d, xb - 1, ya + 1, yb - 1, WD['dk'])
        rect(d, xa + 3, ya + 3, xb - 3, yb - 3, lt(WD['md'], 0.05))
        if yb - ya >= 22 and xb - xa >= 14:                           # 板心一块菱形的雕花（左上亮、右下暗），大块的凸板才有
            cx_, cy_ = (xa + xb) // 2, (ya + yb) // 2
            for (ax, ay, bx, by, c) in ((cx_ - 4, cy_, cx_, cy_ - 7, WD['hi']), (cx_, cy_ - 7, cx_ + 4, cy_, WD['lt']),
                                        (cx_ - 4, cy_, cx_, cy_ + 7, WD['lt']), (cx_, cy_ + 7, cx_ + 4, cy_, WD['dk'])):
                d.line((ax, ay, bx, by), fill=M.C(c))
            px(d, cx_, cy_, WD['dk'])
        for g in range(3):
            gx = xa + 4 + int(hrange(0, max(1, xb - xa - 8), k, g, 1))
            vl(d, gx, ya + 4 + int(hrange(0, 5, k, g, 2)), min(yb - 4, ya + 10 + int(hrange(0, 20, k, g, 3))), WD['dk'])
    M.skirting(cv, X0, X0 + SW * NST - 1, STAIR_FLOOR - 4, 4)
    # 红地毯：踏面 + 竖面 + 铜杆
    for i in range(NST):
        x0 = X0 + SW * i
        yt = 160 - SH * i
        hl(d, x0 + 2, x0 + SW - 1, yt, CAR['hi'])
        hl(d, x0 + 2, x0 + SW - 1, yt + 1, CAR['top'])
        hl(d, x0 + 2, x0 + SW - 1, yt + 2, CAR['mid'])
        hl(d, x0 + 2, x0 + SW - 1, yt + 3, INK)
        for x in range(x0 + 3, x0 + SW, 4):                           # 地毯上的金线花纹：每 4 px 一点
            px(d, x, yt + 1, CAR['rod_d'])
        vl(d, x0, yt, yt + SH - 2, CAR['dk'])
        vl(d, x0 + 1, yt, yt + SH - 2, CAR['riser'])
        px(d, x0, yt, CAR['mid'])
        px(d, x0 + 1, yt, CAR['hi'])
        px(d, x0, yt + SH - 1, CAR['rod_d'])
        px(d, x0 + 1, yt + SH - 1, CAR['rod'])
        px(d, x0 + 2, yt + SH - 1, CAR['rod_d'])
    hl(d, X0, X0 + SW * NST - 1, STAIR_FLOOR, INK)
    M.mul_box(cv.im, (X0 - 1, STAIR_FLOOR + 1, X0 + SW * NST + 3, STAIR_FLOOR + 3), (0.55, 0.55, 0.66))   # 脚下接触影


def _rake_wainscot(cv):
    """斜着的护墙板（跟着楼梯上去）：腰线（亮 / 中 / 珠 / 暗 4 行）+ 板的上槽 + 每 26 px 一道竖槽 + 木纹；板一直画到被台阶盖住的地方。"""
    d = cv.d
    WD = M.WOOD
    for x in range(X0, X0 + SW * NST):
        yp = int(round(pitch(x)))
        yd = yp - 36
        for r, c in enumerate((WD['hi'], WD['lt'], WD['md'] if x % 3 else WD['hi'], WD['dd'])):
            px(d, x, yd + r, c)
        for y in range(yd + 4, yp + 8):
            px(d, x, y, WD['md'])
        px(d, x, yp - 31, WD['dd'])
        px(d, x, yp - 30, WD['lt'])
        if (x - X0) % 26 == 0:
            vl(d, x, yp - 31, yp + 8, WD['dd'])
        elif (x - X0) % 26 == 1:
            vl(d, x, yp - 29, yp + 8, WD['lt'])
        elif (x - X0) % 26 == 25:
            vl(d, x, yp - 29, yp + 8, WD['dk'])
    for k in range(40):                                               # 木纹：斜着的短线
        gx = X0 + int(hrange(2, SW * NST - 12, 11, k, 1))
        gy = int(round(pitch(gx))) - 26 + int(hrange(0, 18, 11, k, 2))
        for s_ in range(int(hrange(4, 10, 11, k, 3))):
            if (gx + s_ - X0) % 26 not in (0, 1, 25):
                px(d, gx + s_, gy + (s_ + 1) // 2, WD['dk'])


def _big_window(cv):
    """平台背后的大尖拱窗：石套 + 夜空（月 / 星 / 远处的树线）+ 三扇窗格的窗棂 + 一道横档 + 铅条。"""
    geo = B.arch_window(cv, WIN['cx'], WIN['y_top'], WIN['y_bot'], WIN['gw'], pointed=True, rise=WIN['rise'])
    gw = WIN['gw']
    gh = WIN['y_bot'] - WIN['y_top'] + 1
    sky = _window_sky(gw, gh)
    full = A._new(PW, H)
    full.paste(sky, (geo['gx0'], WIN['y_top']))
    full.putalpha(Image.fromarray((geo['mask'] * 255).astype(np.uint8), 'L'))
    cv.paste_emissive(full)
    blocked = B.window_bars(cv, geo, lead_rows=(), transom=TRANSOM_Y, mullion_x=MULL_X)
    return geo, blocked


def _window_sky(gw, gh):
    """月夜：天顶深蓝紫 → 地平线一抹发白的蓝雾（所以逆光站着的人有东西衬着）；一轮满月在中间窗格；几颗星；底下一条树线 + 远处的灯。"""
    im = A._new(gw, gh, (0, 0, 0))
    gradient(im, (0, 0, gw, gh), [(0, (24, 28, 74)), (0.38, (54, 72, 136)), (0.7, (118, 138, 198)), (1, (150, 166, 212))], bands=16)
    a = np.array(im).astype(np.float32)
    mx, my = gw // 2, 24                                              # 月亮在整个玻璃的正中（局部坐标 gw//2, 24）
    for i in range(16):
        x, y = int(hrange(0, gw, 5, i, 1)), int(hrange(1, 36, 5, i, 2))
        if abs(x - mx) <= 13 and abs(y - my) <= 13:                   # 别落在月亮上
            continue
        a[y, x, :3] = mix((236, 236, 255), (130, 130, 190), hash01(5, i, 3) * 0.7)
    B._disc_glow(a, mx, my, 9.0, 20.0, (252, 248, 222), (190, 196, 250), k=0.8)
    for (dx, dy, c) in ((-3, -2, (228, 220, 190)), (2, 2, (222, 214, 184)), (4, -3, (236, 230, 200)), (-2, 4, (226, 218, 188)),
                        (0, -5, (234, 228, 198))):
        a[my + dy, mx + dx, :3] = c
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    hor = gh - 7
    for x in range(gw):                                               # 远处的树线 / 丘陵：高低起伏的一条黑边
        h_ = 3 + int(2.2 * math.sin(x * 0.21) + 1.8 * math.sin(x * 0.07 + 1.3) + 1.2 * hash01(x, 9))
        rect(d, x, hor - h_, x, gh - 1, (12, 14, 34))
    for k in range(7):                                                # 远处小镇的几盏灯
        x = int(hrange(2, gw - 2, 6, k, 1))
        px(d, x, gh - 3 - int(hrange(0, 3, 6, k, 2)), (255, 214, 130))
    return im


def _platform(cv):
    """顶上平台（x 214–319，脚点行 y 76）：深色大理石 + 一道红地毯（金边）+ 檐口线脚的前沿（y 82–89）+ 后墙的腰线。"""
    d = cv.d
    x0, x1 = LAND_X, PW - 1
    B.flagstones(cv, x0, x1, 70, 81, pal=FLAG_H, seed=17)
    M.carpet(cv, x0, x1, 73, 80, pal=dict(M.CARPET, base=(150, 32, 46), lt=(176, 50, 60)), seed=3, pattern=False)
    M.cornice(cv, x0, x1, 82, pal=M.WOOD, dentil=True)
    # 前沿下面的阴影（平台出挑，下面的墙更暗）
    M.mul_box(cv.im, (x0, 90, x1, 98), (0.62, 0.62, 0.72), level=0.7)


def _wall(cv, info):
    """后墙：墙纸（整面）→ 天花 + 檐口 → 左右两段水平护墙板 + 腰线 + 踢脚 → 斜护墙板 → 楼下的门 → 平台背后的墙腰线 → 画像 / 烛台。"""
    M.wallpaper(cv, (0, 14, PW - 1, FLOOR_Y - 1), seed=3, pal=PAPER_N)
    d = cv.d
    for y in range(0, 6):                                             # 天花：暗木板
        hl(d, 0, PW - 1, y, mix(M.WOOD['dd'], (10, 6, 14), 0.5 + 0.08 * y))
    for x in range(9, PW, 17):
        vl(d, x, 0, 5, (14, 8, 12))
    M.cornice(cv, 0, PW - 1, 6, pal=M.WOOD, dentil=True)
    # 水平护墙板：楼梯左边 / 平台下面
    for (xa, xb) in ((0, X0 - 1), (LAND_X, PW - 1)):
        M.dado_rail(cv, xa, xb, 120)
        M.wainscot(cv, xa, xb, 124, 142, panel=26, gap=5, seed=xa)
        M.skirting(cv, xa, xb, 143, 5)
    # 平台背后那一层（窗以外的墙）：腰线 + 矮护墙板（窗台下）
    M.dado_rail(cv, LAND_X, PW - 1, 47)
    M.wainscot(cv, LAND_X, PW - 1, 51, 66, panel=26, gap=5, seed=77)
    _rake_wainscot(cv)


@lru_cache(maxsize=2)
def albedo(broken):
    """满光时的固有色：返回 (Canvas, info)。broken = 墙被打穿的那一版（只多画墙洞 + 碎砖断面 + 洞里的夜景）。"""
    cv = M.Canvas(PW, H)
    info = {}
    d = cv.d
    _wall(cv, info)
    # 窗（先画墙，再画窗：窗盖在墙纸上）
    geo, blocked = _big_window(cv)
    info['win'], info['blocked'] = geo, blocked
    # 平台 + 地
    _platform(cv)
    B.flagstones(cv, 0, PW - 1, FLOOR_Y, H - 1, pal=FLAG_H, seed=21)
    # 楼下的门（入口）
    M.gothic_door(cv, 3, 98, 22, 49, seed=2, keyhole=True)
    # 楼梯（盖在墙和地上面）
    _stairs_body(cv)
    # 平台右端的门（出口）
    M.gothic_door(cv, *EXIT_DOOR, seed=8, keyhole=True)
    # 楼梯墙上的肖像（沿楼梯往上）
    info['portraits'] = []
    for cx, subj in PORTRAITS:
        y1 = int(round(pitch(cx))) - 36 - 5
        info['portraits'].append((M.portrait(cv, cx - 10, y1 - 25, cx + 9, y1, subj, seed=cx), cx, y1 - 25, y1, subj))
    # 烛台：楼梯墙上 3 个；烟痕要先画
    for (sx, sy) in SCONCES:
        M.soot(cv, sx, max(16, sy - 30), sy - 6, w=4, seed=sx)
    info['flames'] = [M.sconce(cv, sx, sy, arms=1, seed=sx)[0] for (sx, sy) in SCONCES]
    # 吊灯
    info['chand'] = B.chandelier(cv, CHAND['cx'], CHAND['y_top'], CHAND['y_ring'], seed=3)
    # 平台下面的墙：条案 + 花瓶、铠甲、画像、烛台
    top = M.console_table(cv, 222, 246, FLOOR_Y - 1, seed=4)
    M.dead_flowers(cv, 234, top - 1)
    M.armor_stand(cv, 262, FLOOR_Y - 1, with_halberd=False)                   # 不带长戟：戟尖会捅穿头顶的平台前沿
    M.mul_box(cv.im, (250, 86, 282, FLOOR_Y), (0.78, 0.78, 0.84))               # 钢甲比墙纸亮太多，夜里压暗一档（别抢了平台上的戏）
    M.portrait(cv, 292, 97, 311, 118, 'lady', seed=11, cord=False)    # 墙洞位置上的画像（墙被打穿时一起没了；没有挂绳：洞要把它整个吞进去）
    M.soot(cv, 276, 94, 108, w=4, seed=6)
    info['flames2'] = [M.sconce(cv, 276, 112, arms=1, seed=276)[0]]
    # 平台右端的落地烛台
    info['candel'] = M.candelabra(cv, 313, LAND_Y - 1, h=24, arms=3, seed=9)
    # 蛛网
    M.cobweb(cv, 0, 16, 11, 'tl', seed=1)
    M.cobweb(cv, PW - 1, 16, 11, 'tr', seed=2)
    if broken:
        info['hole'] = _hole(cv)
    return cv, info


# ============================================================ 墙洞（key wall_broken）
def _hole(cv):
    """被打穿的墙：墙洞（不规则的一圈）里是夜里的院子；洞口一圈 3–4 px 是墙的断面（灰泥 / 红砖 / 石块 + 几道裂缝）；
    洞口底边贴着地。洞里的东西自己发光（夜空 / 草地不吃厅里的光）。"""
    ys = np.mgrid[0:H, 0:PW][0]
    hole_m = M.poly_mask((PW, H), HOLE)
    hole_img = Image.fromarray((hole_m * 255).astype(np.uint8), 'L')
    from scipy import ndimage
    dist = ndimage.distance_transform_edt(~hole_m)                       # 离洞口的距离：断面不是一圈整齐的描边，往外越来越碎
    keep = np.array([[hash01(x // 2, y // 2, 34) for x in range(PW)] for y in range(H)])
    ring_m = (dist > 0) & (dist <= 4.2) & (keep < np.clip(1.2 - (dist - 1.5) / 3.5, 0, 1)) & (ys < FLOOR_Y + 1)
    ring_m |= (dist > 0) & (dist <= 1.5) & (ys < FLOOR_Y + 1)            # 贴着洞的第一圈一定有
    # 洞里：夜空 → 远处树篱 → 草地（整个 PW×H 上画，再按洞的形状裁）
    ia = np.zeros((H, PW, 4), np.uint8)
    for y in range(90, FLOOR_Y + 1):
        t = (y - 94) / float(FLOOR_Y - 94)
        ia[y, :, :3] = mix((14, 18, 56), (70, 86, 140), max(0.0, min(1.0, t * 1.25)))
    ia[..., 3] = 255
    inner = Image.fromarray(ia, 'RGBA')
    ind = ImageDraw.Draw(inner)
    for x in range(280, 320):                                         # 树篱的剪影
        h_ = 8 + int(3 * math.sin(x * 0.45) + 2 * math.sin(x * 0.17 + 2.0) + 2 * hash01(x, 31))
        rect(ind, x, 132 - h_, x, 141, (10, 22, 30))
    for x in range(280, 320):                                         # 草地
        for y in range(138, FLOOR_Y + 1):
            c = mix((22, 44, 54), (14, 28, 36), (y - 138) / 10.0)
            if hash01(x, y, 32) < 0.15:
                c = lt(c, 0.12)
            px(ind, x, y, c)
    for (sx, sy) in ((296, 104), (306, 112), (289, 118), (312, 99), (300, 124)):    # 星
        px(ind, sx, sy, (230, 232, 255))
    fa = np.array(inner)
    fa[~hole_m] = 0
    cv.paste_emissive(Image.fromarray(fa, 'RGBA'))
    # 断面一圈
    a = np.array(cv.im)
    for y, x in zip(*np.nonzero(ring_m)):
        r = hash01(int(x) // 2, int(y) // 2, 33)                      # 2×2 一块：断面是一块块碎砖 / 灰泥，不是满天星的细点
        if r < 0.36:
            c = (190, 176, 160)                                       # 灰泥（暖白）
        elif r < 0.78:
            c = (150, 70, 56)                                         # 红砖
        else:
            c = (74, 62, 70)                                          # 烧黑 / 缺口
        k = 1.0 - 0.10 * (dist[y, x] - 1)                            # 越往外越暗一点（墙面上的阴影）
        a[y, x, :3] = tuple(int(v * max(0.55, k)) for v in c)
    cv.im.paste(Image.fromarray(a, 'RGBA'))
    d = cv.d
    edge = hole_m & ~(np.array(hole_img.filter(ImageFilter.MinFilter(3))) > 0)      # 洞的内沿一圈暗线（洞有厚度）
    for y, x in zip(*np.nonzero(edge)):
        if y <= FLOOR_Y:
            px(d, int(x), int(y), (40, 34, 52))
    for k, (sx, sy, dx, dy) in enumerate(((284, 112, -1, 0), (286, 128, -1, 1), (299, 99, -1, 0), (316, 100, 1, 0),
                                          (319, 120, 1, 0), (284, 106, -1, 0), (308, 96, 1, 0))):    # 裂缝（从断面往外）
        x, y = sx, sy
        for s_ in range(int(hrange(5, 10, 41, k, 1))):
            if 0 <= x < PW and 14 <= y < FLOOR_Y:
                px(d, x, y, (50, 42, 54))
            x += dx if hash01(41, k, s_) < 0.8 else 0
            y += dy if hash01(42, k, s_) < 0.7 else (1 if hash01(43, k, s_) < 0.5 else 0)
    return dict(mask=hole_m, ring=ring_m)


# ============================================================ 光
def light(broken=False, scale=None):
    """夜里的大厅：环境光（偏紫蓝、很暗）+ 三个壁烛台 + 吊灯（暖）+ 月光（窗里透进来的冷光，落在平台和楼梯顶上）+ 楼梯上补的一层暖光（红地毯要看得清）。
    可走带（地面）靠一层铺平的光，不跟着烛光一圈圈走。broken：墙洞漏进来的院子里的月光（冷，落在洞口附近的地上 / 墙上）。"""
    scale = scale or {}
    L = M.Light(PW, H, amb=0.25, tint=M.T_AMB)
    yy, xx = L.yy, L.xx
    extra = -0.06 * np.clip((24 - yy) / 24.0, 0, 1)
    extra -= (0.06 * np.clip((20 - xx) / 20.0, 0, 1) + 0.10 * np.clip((xx - 300) / 20.0, 0, 1)) * (yy < FLOOR_Y)
    L.amb_add(np.maximum(extra, -0.18))
    stair_m = np.zeros((H, PW), bool)                                      # 楼梯本体（锯齿顶以下、脚下的地以上）
    for i in range(NST):
        x0 = X0 + SW * i
        stair_m[160 - SH * i - 1:STAIR_FLOOR, x0:x0 + SW] = True
    fl = np.where((yy >= FLOOR_Y) & ~stair_m, 0.62, 0.0).astype(np.float32)   # 地面铺平的光：楼梯本体不吃（否则楼梯侧板在 y=148 处亮暗一刀切）
    fl -= np.where((yy >= FLOOR_Y) & ~stair_m, 0.12 * np.clip((FLOOR_Y + 6 - yy) / 6.0, 0, 1), 0.0).astype(np.float32)
    L.add(fl, T_FLOOR)
    L.add(np.where(stair_m, 0.34, 0.0).astype(np.float32), T_STAIR)        # 楼梯上补的暖光（红地毯在夜里看得清）
    for i, (sx, sy) in enumerate(SCONCES):
        L.point(sx, sy - 4, 50, 0.9 * scale.get(i, 1.0), M.T_WARM, sy=1.0, power=1.8, clip=(0, 14, PW, FLOOR_Y))
    L.point(276, 108, 44, 0.9, M.T_WARM, sy=1.0, power=1.8, clip=(214, 90, PW, FLOOR_Y))
    L.point(CHAND['cx'], CHAND['y_ring'] - 2, 84, 0.75 * scale.get('chand', 1.0), M.T_WARM, sy=1.0, power=1.7, clip=(0, 14, PW, FLOOR_Y))
    L.point(313, LAND_Y - 26, 40, 0.9, M.T_WARM, sy=1.0, power=1.7, clip=(214, 40, PW, 90))
    L.point(238, 76, 54, 0.60, T_MOON2, sy=3.2, power=1.3, clip=(205, 70, 300, 84))   # 窗里的月光落在平台上：窗正下面一片冷光（DIO 站在它的边上）
    # 月光：窗口一团 + 斜着落下来的一道（落在楼梯顶和侧墙上）
    d_ = np.hypot(xx - 236, (yy - 34) * 0.9)                                # 窗口的一团月光：平台出挑的下面（x≥214, y>92）照不到，渐隐而不是硬切
    gate = np.where(xx >= LAND_X, np.clip((100 - yy) / 8.0, 0, 1), 1.0).astype(np.float32)
    L.add((0.85 * np.clip(1 - d_ / 124.0, 0, 1) ** 1.5 * gate * (yy < FLOOR_Y)).astype(np.float32), T_MOON2)
    fade = lambda yy_, xx_: np.clip((150 - yy_) / 80.0, 0, 1)             # noqa: E731
    L.poly([(204, 68), (262, 68), (178, 130), (126, 130)], 0.30, T_MOON2, soft=1.8, fade=fade)
    if broken:
        L.point(302, 128, 64, 0.95, (0.74, 0.92, 1.36), sy=1.0, power=1.4, clip=(230, 94, PW, 150))
        L.point(300, 156, 34, 0.55, (0.74, 0.92, 1.36), sy=2.4, power=1.3, clip=(250, 148, PW, 180))
    return L


def fine_mask():
    m = np.zeros((H, PW), bool)
    m[FLOOR_Y:, :] = True
    return m


def field(broken=False, scale=None):
    return light(broken, scale).field(levels=14, fine=fine_mask(), fine_levels=30)


@lru_cache(maxsize=2)
def base_img(broken=False):
    cv, _ = albedo(broken)
    return M.apply(cv, field(broken))


@lru_cache(maxsize=1)
def broken_overlay():
    """墙打穿之后和原来不一样的像素（墙洞 + 断面 + 洞口漏进来的冷光落在墙 / 地上）：盖在底图上就是被打穿的墙。"""
    a = np.array(base_img(False))
    b = np.array(base_img(True))
    _, info = albedo(True)
    diff = (a[..., :3] != b[..., :3]).any(-1)
    out = np.zeros_like(b)
    out[diff] = b[diff]
    out[..., 3] = np.where(diff, 255, 0)
    return Image.fromarray(out, 'RGBA')


# ============================================================ 前景：扶手
@lru_cache(maxsize=1)
def rail_img():
    """前景的雕花扶手：从楼梯脚的大立柱沿楼梯斜着往上到顶上那根立柱；每级两根栏杆；扶手比台阶高 10 px（= 人的腰 / 胯），
    栏杆只有 1 px 宽，人的上半身完全不挡。已打光（同底图的光）。"""
    cv = M.Canvas(PW, H)
    d = cv.d
    WD = RAIL
    # 栏杆：每级两根（x0+3 / x0+9），从扶手下面到踏面
    for i in range(NST - 1):
        x0 = X0 + SW * i
        for bx in (x0 + 3, x0 + 9):
            yr = int(round(pitch(bx))) - 10
            vl(d, bx, yr + 2, 160 - SH * i, WD['md'])
            px(d, bx, yr + 3, WD['hi'])
            px(d, bx, yr + 6, WD['lt'])                                # 栏杆上的一圈车削
            px(d, bx, yr + 7, WD['dd'])
    # 扶手：x 31 → 200，3 行（亮 / 中 / 暗）
    for x in range(31, 201):
        yr = int(round(pitch(x))) - 10
        px(d, x, yr, WD['hi'])
        px(d, x, yr + 1, WD['lt'])
        px(d, x, yr + 2, WD['dk'])
    # 立柱（下：楼梯脚；上：第 13 级）：方柱 + 柱帽 + 铜球
    y_top_post = int(round(pitch(199))) - 10                            # 上面那根只高出扶手一点点（球在扶手线上），不长到人的胸口去
    for (cx_, ytop, ybot) in ((30, 140, STAIR_FLOOR - 1), (199, y_top_post, 160 - SH * 13)):
        rect(d, cx_ - 2, ytop + 5, cx_ + 2, ybot, WD['md'], outline=INK)
        vl(d, cx_ - 1, ytop + 6, ybot - 1, WD['lt'])
        vl(d, cx_ + 2, ytop + 6, ybot - 1, WD['dk'])
        rect(d, cx_ - 3, ytop + 3, cx_ + 3, ytop + 5, WD['lt'], outline=INK)
        hl(d, cx_ - 2, cx_ + 2, ytop + 3, WD['hi'])
        d.ellipse((cx_ - 2, ytop - 2, cx_ + 2, ytop + 2), fill=C_(M.GOLD['md']), outline=C_(INK))
        px(d, cx_ - 1, ytop - 1, M.GOLD['hi'])
        px(d, cx_ + 1, ytop + 1, M.GOLD['dd'])
        for yy in range(ytop + 8, ybot - 3, 6):                       # 柱身的凹槽
            hl(d, cx_ - 1, cx_ + 1, yy, WD['dk'])
    return M.apply(cv, field(False), floor=0.0)


def C_(c):
    return M.C(c)


# ============================================================ strip
def _cache(raw, fps):
    memo = {}

    def fn(t):
        f = M.frame_of(t, fps)
        if f not in memo:
            memo[f] = raw(f)
        return memo[f]
    return fn


def _lit_canvas(draw_fn, broken=False):
    cv = M.Canvas(PW, H)
    draw_fn(cv)
    return M.apply(cv, field(broken), floor=0.0)


def _glass_clip(im):
    _, info = albedo(False)
    ok = info['win']['mask'] & ~info['blocked']
    a = np.array(im)
    a[~ok] = 0
    return Image.fromarray(a, 'RGBA')


def _moonclouds_raw(f):
    gw = WIN['gw']
    gh = WIN['y_bot'] - WIN['y_top'] + 1
    frs = _moonclouds_frames()
    _, info = albedo(False)
    full = A._new(PW, H)
    full.paste(frs[f], (info['win']['gx0'], WIN['y_top']))
    return _glass_clip(full)


@lru_cache(maxsize=1)
def _moonclouds_frames():
    gw = WIN['gw']
    gh = WIN['y_bot'] - WIN['y_top'] + 1
    pal = ((176, 186, 226), (118, 130, 188), (70, 82, 140), (60, 70, 128))          # 月光照亮的云：亮边 + 蓝灰
    return B.cloud_frames(gw, gh, N8, y_rows=(12, 34, 44), seed=9, pal=pal)


FPS_CLOUD = 2.0


def _bat_raw(f):
    gw = WIN['gw']
    gh = WIN['y_bot'] - WIN['y_top'] + 1
    im = A._new(gw, gh)
    d = ImageDraw.Draw(im)
    a = math.tau * f / N8
    for i, (cx, cy, ax, ay, ph) in enumerate(((20, 40, 16, 6, 0.0), (52, 28, 12, 8, 3.1))):    # 两只蝙蝠，绕着窗洞里两个窗格各飞一个椭圆
        M.bat(d, cx + ax * math.cos(a + ph), cy + ay * math.sin(a + ph), f + i)
    _, info = albedo(False)
    full = A._new(PW, H)
    full.paste(im, (info['win']['gx0'], WIN['y_top']))
    return _glass_clip(full)


def _flames_fn(points, seed0):
    """火苗 strip 的帧函数。M.flame 的形状由 (帧号 + seed) 决定，个别 seed 会有相邻两帧一模一样——从 seed0 起往后挑第一个 8 帧首尾相接都在动的。"""
    for k in range(40):
        fn = M.flames_frame_fn(points, PW, H, seed0=seed0 + k)
        fr = [np.array(fn(i / FPS_FIRE)) for i in range(N8)]
        if all((fr[i] != fr[(i + 1) % N8]).any() for i in range(N8)):
            return fn
    raise ValueError('找不到每帧都在动的火苗 seed')


def _sparkle_raw(f):
    """吊灯的水晶：每颗按自己的相位一闪（亮 → 白点 + 十字），其余时候是暗的小点。"""
    _, info = albedo(False)
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate(info['chand']['crystals']):
        ph = (f + i * 2) % N8
        if ph == 0:
            for (dx, dy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                px(d, x + dx, y + dy, (200, 214, 255))
            px(d, x, y, (255, 255, 255))
        elif ph in (1, 7):
            px(d, x, y, (236, 242, 255))
        else:
            px(d, x, y, (120, 128, 168))
    return im


EYE_PLAN = [(0, 0, -1, -1, 0, 1, 1, 0), (0, 1, 1, 0, 0, -1, -1, 0), (-1, -1, 0, 0, 1, 1, 0, 0)]


def _eyes_raw(f):
    _, info = albedo(False)

    def draw(cv):
        for i, (p, cx, y0, y1, subj) in enumerate(info['portraits']):
            M.eye_px(cv.d, p['eyes'], EYE_PLAN[i][f], subj)
            px(cv.d, cx - 7 + f, y0 + 1, (255, 246, 214))            # 金框上沿一粒慢慢走的高光
    return _lit_canvas(draw)


def _motes_fn():
    fn, _ = M.motes_frame_fn([(204, 70), (262, 70), (178, 128), (128, 128)], PW, H, n=12, seed=61, col=(226, 232, 255),
                             drift=(1.0, 1.0))
    return fn


def _dust_fn():
    fn, _ = M.motes_frame_fn([(286, 100), (316, 100), (316, 146), (284, 146)], PW, H, n=16, seed=71, col=(214, 206, 196),
                             drift=(1.0, 1.0))
    return fn


# ============================================================ 图层表 / 导出
@lru_cache(maxsize=1)
def tables():
    _, info = albedo(False)
    layers = [M.L_pano('base', base_img(False), 1.0, crop=False)]
    layers.append(M.L_static('wallbroken', broken_overlay(), 0, 0, key='wall_broken'))
    fn = _cache(_moonclouds_raw, FPS_CLOUD)
    layers.append(M.L_strip('moonclouds', M.auto_box(fn, N8, FPS_CLOUD), N8, FPS_CLOUD, fn))
    fn = _cache(_bat_raw, FPS)
    layers.append(M.L_strip('bat', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    for i, pt in enumerate(info['flames']):
        fn = _flames_fn([pt], seed0=i * 3)
        layers.append(M.L_strip('flames%d' % i, M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _flames_fn(info['flames2'], seed0=11)
    layers.append(M.L_strip('flames3', M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _flames_fn(info['chand']['flames'], seed0=20)
    layers.append(M.L_strip('chand', M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _flames_fn(info['candel'], seed0=30)
    layers.append(M.L_strip('candel', M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _cache(_sparkle_raw, FPS)
    layers.append(M.L_strip('sparkle', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    fn = _cache(_eyes_raw, FPS)
    layers.append(M.L_strip('eyes', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    fn = _motes_fn()
    layers.append(M.L_strip('motes', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    fn = _dust_fn()
    layers.append(M.L_strip('dust', M.auto_box(fn, N8, FPS), N8, FPS, fn, key='wall_broken'))
    fg = [M.L_static('rail', rail_img(), 0, 0)]
    return layers, fg


def anchors():
    anc = {k: ([list(p) for p in v] if isinstance(v[0], list) else list(v)) for k, v in ANCHORS.items()}
    anc.update(hole_box=[283, 93, 319, 149],
               door_box=[EXIT_DOOR[0] - 3, EXIT_DOOR[1] - 4, EXIT_DOOR[0] + EXIT_DOOR[2] + 3, EXIT_DOOR[1] + EXIT_DOOR[3]],
               stair_box=[X0, LAND_Y, X0 + SW * NST, STAIR_FLOOR],
               window_box=[WIN['cx'] - WIN['gw'] // 2 - 3, WIN['y_top'] - 4, WIN['cx'] + WIN['gw'] // 2 + 4, WIN['y_bot'] + 5])
    return anc


def compose(camX=0, t=0.5, state=None, with_fg=True):
    layers, fg = tables()
    return M.compose(layers, fg, camX, t, state, with_fg=with_fg)


def export(ex, BJ):
    layers, fg = tables()
    st = M.export_stage(ex, PW, GROUND, WALK, layers, fg, anchors())
    if ex.check_on:
        _checks(ex, BJ, st, layers, fg)
    return st


def _checks(ex, BJ, st, layers, fg):
    cfg = dict(title='大楼梯', PW=PW, walk=WALK, base=base_img(False), states=[{}, {'wall_broken': 1}], stand=(),
               required=REQUIRED, size_limit=250 * 1024, flat=(0, PW, WALK[0], WALK[1] + 1, 18, 0.012),
               flat_skip=[(X0 - 4, 146, X0 + SW * NST + 4, 172)])     # 楼梯本体和它脚下的接触影压进可走带的那一块（楼梯自己、不是地面）
    M.common_checks(ex, BJ, st, layers, fg, cfg)
    cv, info = albedo(False)
    a = np.array(cv.im)
    # 15 个脚点：踏面第一行（脚点那一行）是红地毯的亮边、正上面一行不是台阶；左右各 4 px 的踏面都在
    steps = st['anchors']['steps']
    ex.checked('steps 一共 15 个、和素材总表一致（%d 个，首 %s 末 %s）' % (len(steps), steps[0], steps[-1]),
               int(len(steps) != 15 or steps[0] != [40, 160] or steps[-1] != [208, 76]))
    bad = []
    for i, (sx, sy) in enumerate(steps):
        tread = [tuple(a[sy, sx + dx, :3]) for dx in (-3, -1, 0, 2, 4)]
        above = [tuple(a[sy - 1, sx + dx, :3]) for dx in (-3, 0, 3)]
        if any(t_ != tuple(CAR['hi']) for t_ in tread):
            bad.append('%d踏面' % i)
        if any(u_ in (tuple(CAR['hi']), tuple(CAR['top'])) for u_ in above):
            bad.append('%d上方' % i)
        if i and a[sy + 6, sx - 12 + 3, 3] == 0:
            bad.append('%d下级' % i)
    ex.checked('15 个脚点：脚点那一行是踏面（红地毯亮边）、正上面一行是空的（不满足：%s）' % (','.join(bad) or '无'), len(bad))
    # 踏面是整条的斜线：相邻两级踏面顶行 y 差 6、x 差 12
    ys = [160 - SH * i for i in range(NST)]
    ex.checked('相邻两级：高 6 px、宽 12 px（脚点 y %s…）' % ys[:3], int(any(steps[i + 1][1] - steps[i][1] != -6 or steps[i + 1][0] - steps[i][0] != 12 for i in range(NST - 1))))
    # 最后一级接平台：第 14 级踏面右边紧挨平台地毯，同高
    ex.checked('第 14 级（y 76）的右边是平台（y %d），顶面同高' % LAND_Y, int(LAND_Y != steps[-1][1]))
    # 平台：脚点 landing / top / exit 的正下面一行是地毯（脚站在地毯上）
    for nm in ('landing', 'top', 'exit'):
        x, y = st['anchors'][nm]
        px_ = tuple(a[y + 1, x, :3])
        ex.checked('anchors.%s (%d,%d) 脚下是平台（y %d 起是地面，不是空的）' % (nm, x, y, y), int(a[y, x, 3] == 0 or a[y - 1, x, 3] == 0))
    # 前景扶手：不挡上半身——每级脚点上方 17–32 px 范围里（上半身），扶手 fg 的不透明像素一个都没有
    ra = np.array(rail_img())[..., 3] > 0
    leak = 0
    for (sx, sy) in steps[:-1]:
        leak += int(ra[sy - 32:sy - 17, sx - 5:sx + 6].sum())
    ex.checked('前景扶手不挡人的上半身（脚点上方 17–32 px、±5 px 里的扶手像素 %d）' % leak, leak)
    # 窗：moon_window 在窗洞里、月亮在窗里
    g = info['win']
    mx, my = st['anchors']['moon_window']
    ex.checked('anchors.moon_window (%d,%d) 在窗洞里' % (mx, my), 0 if g['mask'][my, mx] else 1)
    # 平台背后的窗：逆光——DIO 站的位置（landing）背后 y 36–64 的窗格是亮的（亮度 > 90）
    b = np.array(base_img(False)).astype(np.float32)
    lx, ly = st['anchors']['landing']
    back = M.lum(b[40:55, lx - 8:lx + 9, :3])
    ex.checked('landing 背后（窗格 y 40–54）够亮，逆光（平均亮度 %.0f ≥ 80）' % back.mean(), int(back.mean() < 80))
    # 墙洞：wall_broken=1 时洞里的夜空 / 树篱，洞外一圈断面；wall_broken=0 时那一块是画像
    on = np.array(M.compose(layers, fg, 0, 0.0, {'wall_broken': 1}))
    off = np.array(M.compose(layers, fg, 0, 0.0, {}))
    _, info_b = albedo(True)
    hm = info_b['hole']['mask'] & (np.mgrid[0:H, 0:PW][0] < FLOOR_Y)
    same_h = int((on[..., :3] == off[..., :3]).all(-1)[hm].sum())
    ex.checked('wall_broken=1：洞里的像素都变了（没变的 %d / %d）' % (same_h, int(hm.sum())), int(same_h > 0.05 * hm.sum()))
    wx, wy = st['anchors']['wall_break']
    ex.checked('anchors.wall_break (%d,%d) 在墙洞里' % (wx, wy), 0 if info_b['hole']['mask'][wy, wx] else 1)
    # 只有右边的墙变了：楼梯（x < 214）整块一模一样
    stairs_same = (on[:, :214, :3] == off[:, :214, :3]).all()
    ex.checked('wall_broken 只改右边的墙：楼梯那一半（x<214）开 / 关一模一样', 0 if stairs_same else 1)
    # 15 级楼梯、DIO 站的平台都不被 key 层盖住（base 和 overlay 在这两处没有重叠的差异）
    ex.checked('wall_broken 层不碰平台（x≥214, y 60–85：平台地面 + 前沿线脚上半 开 / 关一模一样）', 0 if (on[60:85, 214:, :3] == off[60:85, 214:, :3]).all() else 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'final', 'after')
    os.makedirs(od, exist_ok=True)
    out = Image.new('RGB', (PW, H * 2 + 4), (0, 0, 0))
    out.paste(compose(0, 0.5).convert('RGB'), (0, 0))
    out.paste(compose(0, 0.5, {'wall_broken': 1}).convert('RGB'), (0, H + 4))
    out.resize((out.width * 3, out.height * 3), Image.NEAREST).save(os.path.join(od, 'mansion_stairs_solo.png'))
    print('ok')
