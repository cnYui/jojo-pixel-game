# -*- coding: utf-8 -*-
r"""cairo_sewer —— 第10章「开罗」：开罗的旧下水道（地图 sewer_ch10），第 23 战「荷鲁斯神」段 2（伊奇 vs 佩特夏普）。
2026-10-19 第三轮背景重画（interiors 组）新画（改前是 later_stages 的占位）。共用零件在 interior_parts.py。

地图 640 宽、ground 156、可走带 y 148–172；侧视平视，看的是隧道的内墙。
竖向：y 0–43 砖砌的筒拱（砖层越往上越薄、越暗：拱顶在头顶上弯过去）；44–46 起拱线的石带；47–131 砖墙；
132–149 墙脚的大石块（防水的条石，一道发黑的水位线）；平台从“上沿”（anchors.platforms 的 y：150 / 152）往前到 y 166，
166–169 平台前沿的路缘石，y 170–179 前面的水渠（暗绿的水，wrap 往左流）。
从左到右（世界坐标）：
  x 0–140    平台 0（上沿 150）：anchors.arrive [40,160] 在这里；墙上一盏铁丝罩的检修灯
  x 120      拱顶上的第一个铁栅（anchors.grates[0]）：街上的日光从栅缝里落下来，一道斜斜的光柱照到平台上（光柱里浮尘 strip）
  x 140–170  水道 1：墙脚一个拱形的涵洞往外淌水，水从后往前流进前面的水渠；上面架着一块铁格栅便桥（人能走过去，格子里看得到水）
  x 170–300  平台 1（上沿 152）：一根锈水管从墙上部垂下来、阀门手轮；管子底下一滴一滴往下滴（strip）；墙脚一个老鼠洞（老鼠探头 strip）
  x 300–330  水道 2（同上）
  x 330–470  平台 2（上沿 150）：墙上一块蓝色搪瓷的区段牌（阿拉伯字）；第二盏检修灯（接触不好，一闪一闪 strip）
  x 400      拱顶上的第二个铁栅（anchors.grates[1]）+ 光柱
  x 470–500  水道 3（同上）
  x 500–640  平台 3（上沿 152）：墙上一排铁爬梯一直通到拱顶的出口铁栅（anchors.exit_grate [610,40]，伊奇从这里爬出去）
每隔 80 px 一根石砌的壁柱（x 60、140、220 …，拱顶上接一道砖砌的拱肋）——“一连串砖砌的拱”；整条隧道两根锈水管（大的 y 58–63、
小的 y 70–72）沿墙走，管子底下、起拱线下面挂着钟乳一样的白色水垢；墙上有往下淌的水渍和青苔。

图层（从后往前）：
  near       pano  k 1           整条隧道（打好光：偏冷的暗绿环境光 + 两道光柱 + 三盏检修灯 + 出口铁栅的天光；分档）
  water      wrap  k 1  vx 9     前面水渠的水（往左流，64 px 一圈）
  gap0–2     strip k 1           三条水道：涵洞口翻起的白沫 + 往前流的水纹 + 上面的铁格栅便桥（同一组帧、三个框）
  motes0–1   strip k 1           两道光柱里的浮尘
  drip       strip k 1           水管底下的水滴（凝结 → 落下 → 溅开）+ 拱顶滴进水渠的水滴（一圈水纹）
  rat        strip k 1           墙脚老鼠洞里探头的老鼠
  lamp       strip k 1           x 400 那盏检修灯接触不好
  frost      pick  k 1  key frost（0–3）  冻掉的平台：从左往右第 1…n 块平台盖一层白霜（上沿一道亮白边、霜面、前沿挂冰棱、
                                           前面的水结一层薄冰）
锚点：arrive [40,160]、platforms [[0,150,140],[170,152,300],[330,150,470],[500,152,640]]（x0、平台上沿 y、x1）、
  grates [[120,20],[400,20]]、exit_grate [610,40]；另外多导出：walk_x [8,632]、water_y 170（前面水渠的水面，y 再往下就是水里）、
  gaps（三条水道 [x0,x1]）、bridges（三块铁格栅便桥 [x0,y0,x1,y1]）、ladder [610,148]（爬梯脚）、lamps（三盏检修灯）。
key：frost（0–3：冻掉的平台数）。
单独运行：python -B tools/bg_new/cairo_sewer.py → tools/bg_new/_preview/ch10/after/cairo_sewer_solo_*.png
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


def _parts():
    key = 'bg_new_interior_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'interior_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
fno = P.frame_no

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 156
WALK = (148, 172)
VAULT = 43                    # 筒拱到这里
SPRING = (44, 46)             # 起拱线石带
ASHLAR = 132                  # 墙脚条石从这里开始
CURB = 166                    # 平台前沿路缘石（166 亮边、167–169 立面）
WATER_Y = 170                 # 前面水渠的水面
PLAT = [(0, 150, 140), (170, 152, 300), (330, 150, 470), (500, 152, 640)]
GAPS = [(PLAT[i][2], PLAT[i + 1][0]) for i in range(3)]
PIERS = [60, 140, 220, 300, 380, 460, 540, 620]
GRATES = [(120, 20), (400, 20)]
EXIT = (610, 40)
LAMPS = [(220, 84), (380, 84), (540, 84)]   # 检修灯（挂在壁柱上）
FLICKER = 1                   # LAMPS[1] 接触不好
DRIP = (246, 64)              # 水管底下滴水的地方
DRIP2 = (442, 47)             # 拱脚往水渠里滴
RAT = (262, 146)              # 老鼠洞
PIPE_Y = (58, 63)
PIPE2_Y = (70, 72)
VPIPE = 240                   # 垂下来的那根水管
SIGN = (352, 98)

INK = (24, 26, 26)
BRICK = [(98, 64, 52), (110, 72, 56), (88, 60, 50), (104, 78, 62), (92, 70, 58)]
MORTAR = (62, 54, 48)
STONE = [(70, 72, 66), (104, 104, 94), (126, 124, 110), (150, 146, 128)]     # 条石 / 壁柱：暗 → 亮
SLAB = [(100, 102, 92), (138, 136, 120), (150, 146, 128), (166, 160, 140)]   # 平台的石板（比墙亮：人站上去看得清）
WATER = [(18, 44, 40), (26, 70, 62), (38, 96, 82), (78, 140, 118), (140, 190, 166)]   # 偏青的暗绿：和灰石板一眼分开
RUST = [(70, 40, 30), (110, 62, 40), (150, 90, 52), (184, 120, 70)]
IRON = [(30, 32, 34), (52, 54, 56), (78, 80, 82), (110, 112, 112)]
LIME = (206, 210, 196)        # 水垢
MOSS = [(52, 74, 46), (70, 96, 56), (92, 118, 66)]

ANCHORS = dict(arrive=[40, 160], platforms=[list(p) for p in PLAT], grates=[list(g) for g in GRATES],
               exit_grate=list(EXIT), walk_x=[8, 632], water_y=WATER_Y, gaps=[list(g) for g in GAPS],
               bridges=[[g0, 156, g1, 163] for (g0, g1) in GAPS], ladder=[610, 148], lamps=[list(l) for l in LAMPS])


def plat_at(x):
    for (x0, y, x1) in PLAT:
        if x0 <= x < x1:
            return y
    return None


# ============================================================ 墙 / 拱 / 平台（不打光的颜色）
def base_array():
    a = np.zeros((H, PW, 3), np.float32)
    # 筒拱：砖层越往上越薄（拱顶弯过头顶）、越暗
    ys = [0, 2, 4, 7, 10, 14, 19, 25, 31, 37, VAULT + 1]
    for r in range(len(ys) - 1):
        y0, y1 = ys[r], ys[r + 1] - 1
        bw = 6 + r
        off = (bw // 2) * (r % 2)
        for y in range(y0, y1 + 1):
            for x in range(PW):
                c = (x + off) // bw
                if y == y1 or (x + off) % bw == bw - 1:
                    a[y, x] = MORTAR
                else:
                    a[y, x] = BRICK[int(hash01(r, c, 31) * len(BRICK))]
        a[y0:y1 + 1] *= 0.62 + 0.3 * (r / (len(ys) - 2))
    # 起拱线石带
    a[SPRING[0]:SPRING[1] + 1] = STONE[2]
    a[SPRING[0]] = STONE[3]
    a[SPRING[1]] = STONE[1]
    # 砖墙
    P.bricks(a, 0, SPRING[1] + 1, PW - 1, ASHLAR - 1, BRICK, seed=17, bw=10, bh=4, mortar=MORTAR)
    # 墙脚条石（大块、错缝）+ 平台背后的墙一直到平台上沿
    for y in range(ASHLAR, 153):
        r = (y - ASHLAR) // 6
        for x in range(PW):
            off = 9 * (r % 2)
            if (y - ASHLAR) % 6 == 5 or (x + off) % 18 == 17:
                a[y, x] = STONE[0]
            else:
                c = STONE[1] if hash01(r, (x + off) // 18, 5) < 0.6 else mix(STONE[1], STONE[2], 0.5)
                a[y, x] = c
                if (y - ASHLAR) % 6 == 0:
                    a[y, x] = STONE[2]
    # 水位线：一道发黑的带子 + 下面青苔
    a[140:143] *= 0.78
    for x in range(PW):
        for y in range(143, 146):
            if hash01(x // 3, y, 9) < 0.35:
                a[y, x] = MOSS[1]
    # 平台：石板（三排，越往前越高）、上沿一条暗缝（墙脚的影）、前沿路缘石
    for (x0, top, x1) in PLAT:
        rows = [top, top + 4, top + 9, CURB]
        for r in range(3):
            for y in range(rows[r], rows[r + 1]):
                L = 14 + r * 4
                off = (r * 7) % L
                for x in range(x0, x1):
                    if y == rows[r + 1] - 1 or (x + off) % L == L - 1:
                        a[y, x] = SLAB[0]
                    else:
                        a[y, x] = SLAB[1 + int(hash01(r, (x + off) // L, 3) * 3) % 3]
        a[top, x0:x1] = dk(SLAB[0], 0.8)
        a[CURB, x0:x1] = SLAB[3]
        a[CURB + 1:WATER_Y, x0:x1] = STONE[1]
        a[WATER_Y - 1, x0:x1] = STONE[0]
        # 两头：平台的端面（亮边 + 深影），一眼看得出“到头了”
        # 左端：迎光的端面一条亮边；右端：石面边上一条亮棱 + 背光的端面一条暗线；水道里贴着平台再压一条深影
        if x0 > 0:
            a[top:WATER_Y, x0] = SLAB[3]
            a[top:WATER_Y, x0 + 1] = mix(SLAB[2], SLAB[3], 0.5)
        if x1 < PW:
            a[top:WATER_Y, x1 - 2] = SLAB[3]
            a[top:WATER_Y, x1 - 1] = STONE[0]
    # 水道（平台之间）+ 前面的水渠
    for (g0, g1) in GAPS:
        for y in range(150, H):
            for x in range(g0, g1):
                a[y, x] = water_col(x, y)
            a[y, g0] = WATER[0]                                     # 平台端面落在水里的影
    for y in range(WATER_Y, H):
        for x in range(PW):
            a[y, x] = water_col(x, y)
    return a


def water_col(x, y):
    """暗绿的水：越往前越深一点；静态的底色（会动的波纹在 wrap / strip 里）。"""
    u = (y - 150) / 30.0
    c = mix(WATER[2], WATER[1], u)
    if hash01(x // 2, y, 77) < 0.06:
        c = WATER[3]
    return c


def draw_piers(d):
    """壁柱：石块砌的方柱（左亮右暗、一块块错缝的条石），往上接拱顶的一道砖拱肋（越往上越窄越暗）。"""
    for p in PIERS:
        x0, x1 = p - 5, p + 4
        top = SPRING[0]
        for y in range(top, 153):
            b = (y - top) // 7
            c = STONE[2] if b % 2 == 0 else mix(STONE[1], STONE[2], 0.6)
            hl(d, x0, x1, y, c)
            if (y - top) % 7 == 6:
                hl(d, x0, x1, y, STONE[0])
        vl(d, x0, top, 152, STONE[3])
        vl(d, x1, top, 152, STONE[0])
        vl(d, x1 + 1, top + 2, 152, dk(BRICK[2], 0.55))                      # 壁柱落在墙上的影
        rect(d, x0 - 1, top - 2, x1 + 1, top, STONE[3], outline=INK)            # 柱头
        for y in range(0, top - 2):                                              # 拱肋：竖的楔形砖
            w2 = 3 + y * 2 // top
            for x in range(p - w2, p + w2 + 1):
                c = BRICK[3] if (x + y // 3) % 3 else MORTAR
                px(d, x, y, dk(c, 0.6 + 0.35 * y / top))
            px(d, p - w2 - 1, y, INK)
            px(d, p + w2 + 1, y, INK)


def draw_culverts(d):
    """每条水道后面墙脚的拱形涵洞：黑洞洞的口、砖砌的拱圈（楔形砖）、口沿上挂着水垢。"""
    for (g0, g1) in GAPS:
        cx = (g0 + g1) // 2
        r = 11
        top = 150 - r - 10
        d.pieslice((cx - r - 3, top - 3, cx + r + 3, top + 2 * r + 3), 180, 360, fill=P.C(BRICK[3]), outline=P.C(INK))
        rect(d, cx - r - 3, top + r, cx + r + 3, 151, BRICK[3], outline=INK)
        for k in range(0, 181, 18):                                                # 拱圈的楔形砖缝
            a = math.radians(180 + k)
            for q in (r + 1, r + 2):
                px(d, int(round(cx + q * math.cos(a))), int(round(top + r + q * math.sin(a))), MORTAR)
        d.pieslice((cx - r, top, cx + r, top + 2 * r), 180, 360, fill=P.C((16, 22, 22)))
        rect(d, cx - r, top + r, cx + r, 151, (16, 22, 22))
        for k in range(r - 3):                                                    # 里面一点点光（水面反光）
            px(d, cx - r + 3 + k * 2, 148, (40, 60, 54))
        for (u, L) in ((-7, 3), (-2, 2), (4, 4), (8, 2)):                         # 口沿的水垢
            for q in range(L):
                px(d, cx + u, top + r - int(math.sqrt(max(0, r * r - u * u))) + q, LIME if q < L - 1 else dk(LIME, 0.8))


def draw_pipes(d):
    """两根沿墙走的锈水管（管卡每 64 px 一个）+ 一根垂下来的管子和阀门手轮；管子底下挂水垢、往下淌的锈水渍。"""
    y0, y1 = PIPE_Y
    for y in range(y0, y1 + 1):
        u = (y - y0) / (y1 - y0)
        c = RUST[3] if u < 0.2 else (RUST[2] if u < 0.5 else (RUST[1] if u < 0.85 else RUST[0]))
        hl(d, 0, PW - 1, y, c)
    for x in range(0, PW):
        if hash01(x // 3, 61) < 0.12:
            px(d, x, y0 + 2 + int(hash01(x, 2) * 3), RUST[0])
    hl(d, 0, PW - 1, y1 + 1, INK)
    for x in range(14, PW, 64):                                                     # 管卡
        rect(d, x, y0 - 1, x + 2, y1 + 1, IRON[2], outline=INK)
        vl(d, x + 1, y1 + 2, y1 + 4, IRON[1])
    y0, y1 = PIPE2_Y
    hl(d, 0, PW - 1, y0, (120, 130, 120))
    hl(d, 0, PW - 1, y0 + 1, (84, 94, 86))
    hl(d, 0, PW - 1, y1, (56, 62, 58))
    hl(d, 0, PW - 1, y1 + 1, INK)
    # 垂下来的管子 → 拐进地下；阀门手轮
    x = VPIPE
    rect(d, x, y1 + 2, x + 4, 148, RUST[2])
    vl(d, x, y1 + 2, 148, RUST[3])
    vl(d, x + 4, y1 + 2, 148, RUST[0])
    vl(d, x + 5, y1 + 2, 148, INK)
    rect(d, x - 1, 100, x + 5, 103, RUST[1], outline=INK)                           # 法兰
    cx, cy = x + 2, 116
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), outline=P.C((150, 40, 34)))
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), outline=P.C((110, 28, 26)))
    for k in range(4):
        a = math.radians(45 + k * 90)
        d.line((cx, cy, cx + round(5 * math.cos(a)), cy + round(5 * math.sin(a))), fill=P.C((130, 36, 30)))
    px(d, cx, cy, IRON[3])
    # 水垢：管子底下、起拱线下面挂着一根根白色的“钟乳”
    for x in range(3, PW, 7):
        if hash01(x, 13) < 0.45:
            L = 1 + int(hash01(x, 14) * 4)
            for q in range(L):
                px(d, x, PIPE_Y[1] + 2 + q, LIME if q < L - 1 else dk(LIME, 0.75))
        if hash01(x, 15) < 0.3:
            L = 2 + int(hash01(x, 16) * 5)
            for q in range(L):
                px(d, x + 2, SPRING[1] + 1 + q, LIME if q < L - 1 else dk(LIME, 0.75))
    # 锈水渍：管卡底下往下淌
    for x in range(15, PW, 64):
        for q in range(int(10 + hash01(x, 3) * 22)):
            if hash01(x, q, 4) < 0.8:
                px(d, x + (q // 9) % 2, PIPE_Y[1] + 5 + q, dk(RUST[1], 0.8))


def draw_wall_details(d):
    """检修灯的铁丝罩 + 电线、区段牌、青苔斑、出口铁栅 + 铁爬梯、拱顶的两个铁栅、老鼠洞。"""
    for (lx, ly) in LAMPS:                                                           # 检修灯（灯泡本身打光后画）
        rect(d, lx - 3, ly - 6, lx + 3, ly - 5, IRON[2], outline=INK)
        for k in range(-3, 4, 2):
            vl(d, lx + k, ly - 4, ly + 4, IRON[2])
        hl(d, lx - 3, lx + 3, ly + 4, IRON[1])
        hl(d, lx - 2, lx + 2, ly, IRON[2])
        d.line((lx, ly - 7, lx + 12, PIPE2_Y[1] + 2), fill=P.C((30, 30, 30)))       # 电线搭到小管子上
    sx, sy = SIGN                                                                    # 区段牌：蓝搪瓷、白边、阿拉伯字
    rect(d, sx, sy, sx + 16, sy + 9, (46, 82, 150), outline=(220, 224, 226))
    rect(d, sx - 1, sy - 1, sx + 17, sy + 10, None, outline=INK)
    for x in range(sx + 3, sx + 14):
        y = sy + 4 + int(round(1.2 * math.sin(x * 0.9)))
        px(d, x, y, (226, 230, 232))
    px(d, sx + 6, sy + 2, (226, 230, 232))
    px(d, sx + 11, sy + 7, (226, 230, 232))
    for k in range(3):                                                                # 牌子底下锈了一块
        px(d, sx + 13 + k, sy + 8, (150, 90, 52))
    for (mx, my, n) in ((30, 120, 30), (196, 110, 24), (300, 124, 34), (430, 116, 26), (560, 122, 30), (110, 80, 12)):
        for i in range(n):                                                            # 青苔斑
            u = mx + int(hrange(-10, 10, mx, i))
            v = my + int(hrange(-6, 10, mx, i, 2))
            px(d, u, v, MOSS[int(hash01(mx, i, 3) * 3)])
    # 出口：拱顶上的铁栅（伊奇从这里出去）+ 墙上一排铁爬梯
    ex, ey = EXIT
    rect(d, ex - 10, ey - 6, ex + 10, ey + 6, IRON[1], outline=INK)
    rect(d, ex - 8, ey - 4, ex + 8, ey + 4, (60, 64, 60))                          # 栅后面的天光打光以后画
    for x in range(ex - 6, ex + 7, 3):
        vl(d, x, ey - 4, ey + 4, IRON[0])
    vl(d, ex - 6, ey + 7, 150, IRON[2])
    vl(d, ex + 6, ey + 7, 150, IRON[2])
    vl(d, ex - 5, ey + 7, 150, IRON[0])
    vl(d, ex + 7, ey + 7, 150, IRON[0])
    for y in range(ey + 12, 150, 7):
        hl(d, ex - 6, ex + 6, y, IRON[3])
        hl(d, ex - 5, ex + 7, y + 1, IRON[0])
    # 拱顶上的两个铁栅（日光打光以后画在栅缝里）
    for (gx, gy) in GRATES:
        rect(d, gx - 10, gy - 4, gx + 10, gy + 4, IRON[1], outline=INK)
    # 老鼠洞
    rx, ry = RAT
    d.pieslice((rx - 4, ry - 4, rx + 4, ry + 4), 180, 360, fill=P.C((14, 16, 16)))
    rect(d, rx - 4, ry, rx + 4, ry + 2, (14, 16, 16))
    px(d, rx - 5, ry, STONE[0])
    px(d, rx + 5, ry, STONE[0])


def draw_debris(d):
    """角落的零碎：半截破木板、一只倒着的铁皮桶、几块碎砖（都贴着墙脚，不进可走带）。"""
    rect(d, 92, 145, 108, 147, (96, 70, 46), outline=INK)
    hl(d, 93, 107, 145, (130, 98, 64))
    rect(d, 522, 141, 530, 149, (90, 96, 92), outline=INK)
    hl(d, 522, 530, 144, (120, 126, 120))
    hl(d, 521, 531, 141, (130, 136, 130))
    for (bx, by) in ((112, 149), (116, 150), (418, 149), (596, 151)):
        rect(d, bx, by - 1, bx + 2, by, BRICK[1], outline=INK)


# ============================================================ 打光
def shaft_poly(gx):
    """拱顶铁栅落下来的光柱：上窄下宽，往右下斜一点（街上的太阳在左上）。"""
    return [(gx - 8, 24), (gx + 8, 24), (gx + 26, 152), (gx - 2, 152)]


@lru_cache(maxsize=1)
def shaft_mask():
    m = np.zeros((H, PW), bool)
    for (gx, gy) in GRATES:
        m |= P.poly_mask((PW, H), shaft_poly(gx))
    return m


@lru_cache(maxsize=1)
def light_mult():
    """偏冷的暗绿环境光（拱顶更暗）；两道光柱（暖白、边缘按 Bayer 抖）、三盏检修灯、出口铁栅的天光。"""
    yy, xx = np.mgrid[0:H, 0:PW].astype(np.float32)
    amb = 0.52 + 0.1 * np.clip((yy - 40) / 110.0, 0, 1) - 0.12 * np.clip((40 - yy) / 40.0, 0, 1)
    amb += 0.14 * np.clip((yy - 149) / 3.0, 0, 1)            # 平台 / 水面这一截提亮：人站在上面要看得清
    lights = [dict(x=gx + 8, y=120, r=64, k=0.42, p=1.3, sx=1.3, sy=0.6, col=(1.12, 1.08, 0.94)) for (gx, gy) in GRATES]
    lights += [dict(x=lx, y=ly + 4, r=46, k=0.5 if i != FLICKER else 0.36, p=1.6, sy=0.9, col=(1.16, 1.0, 0.7))
               for i, (lx, ly) in enumerate(LAMPS)]
    lights.append(dict(x=EXIT[0], y=EXIT[1] + 30, r=50, k=0.3, p=1.4, sy=0.6, col=(1.08, 1.06, 0.96)))
    m = P.light_map(PW, H, amb, lights, n=9, cool=(0.82, 0.96, 0.94))
    sm = shaft_mask()
    bay = P.bayer(PW, H)
    yy_i = np.mgrid[0:H, 0:PW][0]
    k = np.where(yy_i > 146, 1.4, 1.28)
    edge = np.zeros_like(sm)
    edge[:, 1:] |= sm[:, 1:] != sm[:, :-1]
    inner = sm & ~(edge & (bay < 0.5))
    m[inner] *= np.stack([k, k * 0.98, k * 0.88], -1)[inner]
    return m


@lru_cache(maxsize=1)
def near_img():
    a = base_array()
    im = Image.fromarray(np.concatenate([np.clip(a, 0, 255), np.full((H, PW, 1), 255, np.float32)], -1).astype(np.uint8),
                         'RGBA')
    d = ImageDraw.Draw(im)
    draw_piers(d)
    draw_culverts(d)
    draw_pipes(d)
    draw_wall_details(d)
    draw_debris(d)
    im = P.apply_light(im, light_mult())
    d = ImageDraw.Draw(im)
    for (gx, gy) in GRATES:                                                         # 栅缝里的日光（自己发光）
        rect(d, gx - 8, gy - 2, gx + 8, gy + 2, (250, 242, 210))
        for x in range(gx - 6, gx + 7, 3):
            vl(d, x, gy - 2, gy + 2, IRON[0])
        P.glow(im, gx, gy + 6, 16, 8, (255, 240, 200), 40, rings=2)
    ex, ey = EXIT
    rect(d, ex - 8, ey - 4, ex + 8, ey + 4, (226, 230, 214))
    for x in range(ex - 6, ex + 7, 3):
        vl(d, x, ey - 4, ey + 4, IRON[0])
    for i, (lx, ly) in enumerate(LAMPS):
        P.glow(im, lx, ly, 14, 10, (255, 220, 150), 40, rings=2)
        bulb(d, lx, ly, 1.0)
    shaft_floor(im)
    return P.opaque(im)


def bulb(d, lx, ly, k):
    c0 = mix((110, 100, 80), (255, 248, 210), k)
    c1 = mix((96, 88, 70), (255, 210, 120), k)
    rect(d, lx - 1, ly - 3, lx + 1, ly + 2, c1)
    vl(d, lx, ly - 2, ly + 1, c0)


def shaft_floor(im):
    """光柱落到平台上的那一块：亮一档 + 铁栅的格子影（几道暗条）。"""
    d = ImageDraw.Draw(im)
    a = np.array(im)
    for (gx, gy) in GRATES:
        for x in range(gx - 2, gx + 27):
            y = 152
            while y < CURB:
                if (x - gx) % 6 in (2, 3) and plat_at(x) is not None and y >= plat_at(x):
                    a[y, x, :3] = (a[y, x, :3].astype(np.float32) * 0.84).astype(np.uint8)
                y += 1
    im.paste(Image.fromarray(a, 'RGBA'))


# ============================================================ 会动的
@lru_cache(maxsize=1)
def water_tex():
    """前面水渠的水（64 px 一圈，wrap 往左流）：底色 + 一道道亮的波纹短线 + 靠近路缘石那一排暗影。"""
    per = 64
    im = P.new(per, H - WATER_Y)
    d = ImageDraw.Draw(im)
    for y in range(H - WATER_Y):
        for x in range(per):
            px(d, x, y, water_col(x, y + WATER_Y))
    hl(d, 0, per - 1, 0, dk(WATER[1], 0.7))
    for i in range(14):
        y = 1 + int(hash01(i, 5) * (H - WATER_Y - 2))
        x = int(hash01(i, 6) * per)
        L = 3 + int(hash01(i, 7) * 6)
        c = WATER[3] if i % 3 else WATER[4]
        for k in range(L):
            px(d, (x + k) % per, y, c)
    return im


def gap_frame(t):
    """三条水道：涵洞口翻白沫、水纹从后往前流（8 帧走一个周期）；上面一块铁格栅便桥（每帧都画，盖在水上）。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    for gi, (g0, g1) in enumerate(GAPS):
        for y in range(150, H):
            for x in range(g0, g1):
                px(d, x, y, water_col(x, y))
            px(d, g0, y, WATER[0])
        for i in range(10):                                                            # 往前流的波纹
            y = 151 + ((int(hash01(gi, i) * 30) + f * 4) % 30)
            x = g0 + 2 + int(hash01(gi, i, 2) * (g1 - g0 - 8))
            hl(d, x, x + 2 + i % 3, y, WATER[3] if i % 2 else WATER[4])
        cx = (g0 + g1) // 2
        for k in range(7):                                                              # 涵洞口的白沫
            u = cx - 8 + k * 3 + ((f + k) % 3) - 1
            px(d, u, 150 + (f + k) % 2, (196, 214, 204))
            px(d, u + 1, 151, (150, 180, 166))
        # 铁格栅便桥：铁框 + 格子（格子里看得到水）
        bx0, by0, bx1, by1 = g0 - 1, 156, g1, 163
        rect(d, bx0, by0, bx1, by0 + 1, IRON[2])
        rect(d, bx0, by1 - 1, bx1, by1, IRON[1])
        vl(d, bx0, by0, by1, IRON[3])
        vl(d, bx1, by0, by1, IRON[0])
        for y in range(by0 + 2, by1 - 1):
            for x in range(bx0 + 1, bx1):
                if (x - bx0) % 3 == 0 or (y - by0) % 2 == 0:
                    px(d, x, y, IRON[2] if (y - by0) % 2 == 0 else IRON[1])
        hl(d, bx0, bx1, by1 + 1, INK)
        hl(d, bx0 + 1, bx1 - 1, by1 + 2, WATER[0])                                       # 便桥落在水面上的影
    return im


def motes_frame(t):
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    sm = shaft_mask()
    for i, (gx, gy) in enumerate(GRATES):
        P.motes(d, (gx - 4, 30, gx + 24, 146), t, 2.0, 12, (240, 236, 210), seed=11 + i,
                ok=lambda x, y: 0 <= x < PW and 0 <= y < H and bool(sm[y, x]))
    return im


def drip_frame(t):
    """两处滴水（8 帧一个周期）：0–3 帧水珠在管子底下慢慢鼓起来，4–5 帧往下掉，6 帧落地溅开，7 帧一圈水纹。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    f = fno(t)
    for (x, y0, y1, water) in ((DRIP[0], DRIP[1] + 1, 152, False), (DRIP2[0], DRIP2[1] + 1, 174, True)):
        if f < 4:
            for q in range(f // 2 + 1):
                px(d, x, y0 + q, (170, 200, 196))
            px(d, x, y0 + f // 2 + 1, (220, 236, 232)) if f % 2 else None
        elif f < 6:
            y = y0 + int((y1 - y0) * (0.35 if f == 4 else 0.85))
            vl(d, x, y, y + 2, (200, 226, 222))
        elif f == 6:
            for (u, v) in ((-2, -1), (2, -1), (-1, -2), (1, -2), (0, 0)):
                px(d, x + u, y1 + v, (200, 226, 222))
        else:
            if water:
                hl(d, x - 3, x + 3, y1, (110, 150, 132))
                px(d, x - 4, y1, (80, 120, 104))
                px(d, x + 4, y1, (80, 120, 104))
            else:
                hl(d, x - 2, x + 2, y1, (130, 136, 128))
    return im


RAT_FR = [  # (伸出来几 px, 眼睛亮 0/1, 胡子 0/1/2)
    (0, 1, 0), (1, 0, 0), (2, 1, 1), (3, 1, 2), (3, 0, 1), (2, 1, 2), (1, 1, 0), (0, 0, 0)]


def rat_frame(t):
    """墙脚老鼠洞里的老鼠：先是黑暗里两点眼光，探出鼻尖、半个头、整个头（胡子一抖一抖），再缩回去。"""
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    out, eye, wh = RAT_FR[fno(t)]
    rx, ry = RAT
    if out == 0:
        px(d, rx - 1 + (1 if eye else 0), ry - 1, (220, 60, 50) if eye else (120, 40, 36))
        px(d, rx + 1 + (1 if eye else 0), ry - 1, (220, 60, 50) if eye else (120, 40, 36))
        return im
    body = (110, 100, 96)
    for k in range(out + 2):                                                            # 头往左伸出洞口
        vl(d, rx - 2 - k, ry - 2, ry + 1, body if k < out + 1 else dk(body, 0.8))
    px(d, rx - 3 - out, ry, (220, 150, 150))                                              # 粉鼻子
    px(d, rx - 1 - out, ry - 2, (30, 20, 20) if eye else body)                           # 眼睛
    px(d, rx - out, ry - 3, (160, 130, 126))                                              # 耳朵
    if wh:
        px(d, rx - 4 - out, ry - (1 if wh == 1 else 0), (200, 196, 190))
        px(d, rx - 4 - out, ry + (1 if wh == 2 else 0) + 1, (200, 196, 190))
    return im


LAMP_K = (1.0, 0.82, 0.25, 0.95, 0.6, 1.0, 0.3, 0.88)


def lamp_frame(t):
    im = P.new(PW, H)
    d = ImageDraw.Draw(im)
    lx, ly = LAMPS[FLICKER]
    k = LAMP_K[fno(t)]
    bulb(d, lx, ly, k)
    if k < 0.5:                                                                           # 灭下去：灯罩里那一圈也暗
        for (u, v) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            px(d, lx + u, ly + v, (70, 64, 52))
    return im


# ============================================================ 白霜（key frost）
@lru_cache(maxsize=None)
def frost_img(n):
    """前 n 块平台冻住：霜面（白 / 淡蓝按 Bayer 抖，石板缝还隐约看得见）、上沿一道亮白边（剧情的预警条对这里）、
    路缘石挂一排冰棱垂进水里、前面那一段水面结一层薄冰。图高 y 146–179（四张一样大）。"""
    y0 = 146
    im = P.new(PW, H - y0)
    a = np.array(im)
    near = np.array(near_img())
    bay = P.bayer(PW, H)
    for i in range(n):
        x0, top, x1 = PLAT[i]
        for y in range(top, WATER_Y + 4):
            for x in range(x0, x1):
                if y < CURB:
                    base = near[y, x, :3].astype(np.float32)
                    k = 0.62 + 0.25 * (bay[y, x] > 0.55)
                    c = base * (1 - k) + np.array((226, 240, 248)) * k
                    if (x * 7 + y * 3) % 11 == 0:
                        c = np.array((250, 254, 255))
                elif y <= CURB + 3:
                    c = np.array((190, 220, 236)) if bay[y, x] < 0.7 else np.array((150, 190, 214))
                else:                                                                  # 前面的薄冰
                    c = np.array((168, 206, 222)) if (x + y) % 5 else np.array((214, 236, 244))
                a[y - y0, x, :3] = np.clip(c, 0, 255)
                a[y - y0, x, 3] = 255
        a[top - y0, x0:x1, :3] = (250, 254, 255)
        a[top - y0 + 1, x0:x1, :3] = (214, 236, 248)
        for x in range(x0 + 2, x1 - 1, 3):                                               # 冰棱
            L = 2 + int(hash01(x, i, 8) * 5)
            for q in range(L):
                yy = CURB + 4 + q
                if yy - y0 < a.shape[0]:
                    a[yy - y0, x, :3] = (236, 248, 255) if q < L - 1 else (170, 210, 230)
                    a[yy - y0, x, 3] = 255
    return Image.fromarray(a, 'RGBA')


# ============================================================ 组装
@lru_cache(maxsize=1)
def specs():
    S = [dict(t='pano', name='near', img=near_img(), k=1.0),
         dict(t='wrap', name='water', img=water_tex(), period=64, k=1.0, y=WATER_Y, vx=9.0)]
    for i, (g0, g1) in enumerate(GAPS):
        S.append(P.strip('gap%d' % i, gap_frame, (g0 - 2, 146, g1 + 2, H)))
    for i, (gx, gy) in enumerate(GRATES):
        S.append(P.strip('motes%d' % i, motes_frame, (gx - 8, 26, gx + 30, 150)))
    S += [P.strip('drip', drip_frame, (DRIP[0] - 6, DRIP2[1] - 2, DRIP2[0] + 6, H)),
          P.strip('rat', rat_frame, (RAT[0] - 10, RAT[1] - 6, RAT[0] + 4, RAT[1] + 4)),
          P.strip('lamp', lamp_frame, (LAMPS[FLICKER][0] - 4, LAMPS[FLICKER][1] - 5, LAMPS[FLICKER][0] + 5,
                                        LAMPS[FLICKER][1] + 5)),
          dict(t='pick', name='frost', key='frost', values=[0, 1, 2, 3], imgs=[frost_img(n) for n in range(4)],
               x=0, y=146, k=1.0)]
    return S


def anchors():
    return {k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in ANCHORS.items()}


def export(ex, BJ):
    S = specs()
    layers, fg = P.export_layers(ex, BJ, S)
    st = ex.stage(PW, GROUND, WALK, layers, fg, anchors())
    if ex.check_on:
        _checks(ex, BJ, st, S)
    return st


def _checks(ex, BJ, st, S):
    near = near_img()
    m0, s0 = P.walk_stats(near, (152, 166))
    cfg = dict(
        name='下水道', pw=PW, walk=WALK,
        states=[{}, {'frost': 1}, {'frost': 2}, {'frost': 3}],
        opaque=[('近景整张不透明（地下，没有天）', near, (0, 0, PW, H))],
        binary=[('近景只有 0 / 255 两种透明度', near)] + [('白霜第 %d 张只有 0 / 255' % n, frost_img(n)) for n in range(4)],
        stand=['arrive', 'ladder'],
        inside=['grates', 'exit_grate', 'lamps', 'bridges'],
        notes=['平台石面亮度（y 152–166）：均值 %.0f 标准差 %.1f' % (m0, s0)],
    )
    P.std_checks(ex, BJ, st, S, cfg)
    an = st['anchors']
    ex.checked('platforms 和素材总表一致（4 块，x0 / 上沿 / x1）',
               int(an['platforms'] != [[0, 150, 140], [170, 152, 300], [330, 150, 470], [500, 152, 640]]))
    # 平台边缘一眼看清：上沿那一行比上面一行（墙脚）暗、端面那一列和旁边水道的颜色差得开
    a = np.array(near)[..., :3].astype(np.int16)
    lum = a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11
    weak = 0
    for (x0, top, x1) in PLAT:
        xs = slice(max(0, x0 + 3), min(PW, x1 - 3))
        weak += int((np.abs(lum[top, xs] - lum[top + 2, xs]) < 6).sum() > (x1 - x0) * 0.5)
        weak += int((np.abs(lum[CURB, xs] - lum[CURB + 2, xs]) < 10).sum() > (x1 - x0) * 0.3)
    for (g0, g1) in GAPS:                                      # 便桥前后露出水的两行（y 153、165）
        for y in (153, 165):
            weak += int(abs(lum[y, g0 - 2] - lum[y, g0 + 3]) < 20) + int(abs(lum[y, g1] - lum[y, g1 - 4]) < 20)
    ex.checked('平台的上沿 / 前沿路缘石 / 两头端面都和旁边差得开（不清楚的处数）', weak)
    # 白霜：第 n 张正好盖住前 n 块平台（别的平台上没有霜）
    bad = 0
    for n in range(4):
        fa = np.array(frost_img(n))[..., 3] > 0
        for i, (x0, top, x1) in enumerate(PLAT):
            cnt = int(fa[:, x0:x1].sum())
            bad += int((cnt == 0) if i < n else (cnt > 0))
    ex.checked('白霜第 n 张正好盖住从左往右前 n 块平台（不对的块数）', bad)
    w = np.array(near)[WATER_Y:, :, :3].astype(np.int16)
    ex.checked('y ≥ %d 整条都是水的颜色（偏绿、偏暗：不像的像素）' % WATER_Y,
               int(((w[..., 1] < w[..., 0]) | (w.max(-1) > 200)).sum()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch10', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        P.direct(specs(), camX, 0.5, {'frost': 2}).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'cairo_sewer_solo_%d.png' % camX))
    print('ok')
