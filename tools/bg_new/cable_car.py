# -*- coding: utf-8 -*-
r"""cable_car —— 第3章 新加坡：1980 年代跨海缆车（花柏山 → 圣淘沙）的车厢里面，白天。2026-10-11 ch3 按体验版精度重画。

改前（later_stages.cablecar()）是一个红框 + 两块天空，看不出是缆车。重画后 320 单屏，ground 156，可走带 y 150–170；
侧视：看到车厢的后壁（长边）和地板，车厢内部 x 40–280，x < 40 / x > 280 是车厢两头的端壁（人走不过去）。
整张图左右对称（对称轴 x 159.5）：
  x 0–39      左端壁：线路图牌（花柏山 ●—— 海 ——● 圣淘沙，只画图形）、对讲机 + 红色紧急按钮、灭火器、
              禁烟牌、下面一排暖气百叶；最左 4 px 是车厢剖开的断面（深红）
  x 40–79     左端窗（战斗机关，win_l）：上面一扇气窗（y 29–55），一道横梁，下面一整块大玻璃 y 60–140
              （x 44–75，中心 59.5），粗窗框 + 铆钉；玻璃上一枚“请勿倚靠”的小贴纸（只在 pick 0 里）
  x 82–137    左长椅（青绿色人造革，三个座位）+ 上面两扇大侧窗（x 84–109 / 113–138，y 29–106，上面一截是
              能翻开的通风小窗 y 29–43）+ 窗台下的镀铬扶手
  x 139–180   中间的双开拉门（门中缝 x 159|160、两个竖把手、门上两扇窗、门下一截踢脚板）+ 门楣上的车厢编号牌
  x 183–237   右长椅（同左）
  x 240–279   右端窗（win_r，中心 259.5）
  x 280–319   右端壁：紧急说明图牌、急救箱（绿十字）、禁烟牌、暖气百叶
  天花板 y 0–21：透视的面板缝、两条日光灯罩、中间一扇天窗（看得见车顶的吊臂和头顶那根承载索）；
              y 17–18 一根镀铬吊环杆，挂着 8 个吊环（吊环是 strip，跟着车厢的晃动轻轻摆）
  竖扶手杆：x 78 / 241 两根，从天花板到地板
  地板 y 146–175：铝合金防滑花纹板（压低了对比），窗户斜射进来的几块光斑；y 176–179 是近侧门槛（剖面）
窗外（窗户是透明洞，后面一层层叠起来）：
  sky     static            天空渐变（窗外 + 天窗）
  clouds  wrap  vx 2        云（640 循环，往左慢慢飘）
  outside strip 16 帧 @4fps 远景：左边港口的集装箱吊机 + 城市天际线、中间远处的船和小岛、右边圣淘沙（绿岛 + 沙滩
                            + 红屋顶 + 灯塔）、海平线 y 62、海面底色、对面那根回程缆绳 y 33——整块随车厢晃动
                            上下 ±1 px（4 s 一个来回，sin 取整：0,0,1,1,1,1,1,0,0,0,−1,−1,−1,−1,−1,0）
  sea0–3  wrap  vx 2/4/7/11 海面浪花 + 港口里的船（越近越快：远处的集装箱船 / 油轮，中间的货船、驳船 bumboat、
                            拖船、渡轮，近处的舢板），船尾带白色尾迹；stage.state.speed 可调快慢 / 停
  gondola clouds vx −60     对面开过来的缆车车厢（同样的红 / 奶油配色，里面两个乘客的剪影），两节相隔 600 px = 每 10 s 迎面过来一节
  tower   wrap  vx 32       缆车塔（钢桁架 + 横担 + 托索轮组），period 1280 = 40 s 经过一次
  cabin   static            车厢内景（窗户是透明洞 / 半透明玻璃反光；端窗大玻璃的洞是全透明，玻璃在 pick 里）
  win_l   pick  key 'win_l' 0 = 端窗完好（淡淡的玻璃色 + 两道反光 + 贴纸）；1 = 撞碎（窗框四周一圈锯齿碎玻璃 + 裂纹，
  win_r   pick  key 'win_r'     中间空了直接看到外面的天和海；窗台和地板上散着十几块碎玻璃）
  straps  strip 16 帧 @4fps 吊环（和窗外的晃动同一个 4 s 周期，反向摆 ±1 px）
晃动：engine\bg.js 没有“整层上下动”的图层，所以没改引擎——车里的东西（地板、座椅）不动（人物脚底不会漂），
      把晃动做进窗外远景的 strip（整片天际线 / 海平线 / 回程缆绳一起上下 ±1 px）和吊环 strip 里：从车里看就是车厢在晃。
锚点：win_l [60,152] / win_r [260,152]（端窗前站人）、door [160,152]、seat_l [100,150] / seat_r [220,150]
      （坐着的人脚底；座垫面 y 139–142，对上承太郎 sit 帧的屁股）、anne_corner [268,160]、walk_x [40,280]；
      另给 win_l_glass / win_r_glass（大玻璃框）、sit {y 150, seat_top 139}、horizon 62、cable_y 33、shards（碎玻璃落地范围）。
单独运行：python -B tools\bg_new\cable_car.py → tools\bg_new\_preview\ch3\after\cable_car_solo*.png
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

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
GROUND = 156
WALK = (150, 170)
X_L, X_R = 40, 280            # 车厢内部（两头是端壁）
HZ = 62                       # 窗外海平线
CABLE_Y = 33                  # 窗外回程缆绳
N_SW, FPS_SW = 16, 4.0        # 晃动：16 帧 @4 fps = 4 s 一个来回
SWAY = [int(round(math.sin(math.tau * f / N_SW))) for f in range(N_SW)]
OUT_BOX = (40, 27, 280, 142)  # 窗外远景 strip（所有窗户都在这个框里）
STRAP_BOX = (40, 14, 280, 48)
# 车厢里
CEIL_B = 21                   # 天花板下沿
HDR = (22, 28)                # 窗上横梁
GL_T, GL_B = 29, 106          # 侧窗玻璃
VENT_B = 43                   # 侧窗上面一截通风小窗的下沿（横档 44–45）
SILL = (107, 110)
GRAB_Y = 113                  # 窗台下的镀铬扶手 113–114
BK_T = 118                    # 靠背顶
SEAT_T = 139                  # 座垫面 139–142
SEAT_F = 143                  # 座垫前沿
BASE_B = 149                  # 座椅底座前沿下边（落在地板上）
FLOOR = 146                   # 后壁脚 / 地板起点
FRONT = 176                   # 近侧门槛 176–179
EW_X = {'l': (44, 75), 'r': (244, 275)}      # 端窗大玻璃 x（含）
EW_T, EW_B = 60, 140                          # 端窗大玻璃 y（含）
TR_T, TR_B = 29, 55                           # 端窗上面的气窗
PANES = [(84, 109), (113, 138), (181, 206), (210, 235)]
BENCHES = [(82, 136), (183, 237)]
DOOR = (139, 180)             # 门框（含）
DOOR_GL = [(145, 156), (163, 174)]
DOOR_GL_Y = (34, 92)
POLES = [78, 240]             # 竖扶手杆（2 px 宽：x, x+1）
STRAPS = [56, 76, 98, 120, 199, 221, 243, 263]
SKY_X = (147, 172)            # 天窗（在天花板下沿的 x；往上按透视展开）
VP = (159.5, 95.0)            # 透视灭点
C = A._c4

ANCHORS = dict(
    win_l=[60, 152], win_r=[260, 152], door=[160, 152],
    seat_l=[100, 150], seat_r=[220, 150], anne_corner=[268, 160],
)

# ============================================================ 调色
INK = (44, 30, 32)
RED_HI = (222, 94, 74)
RED = (188, 56, 46)
RED_M = (160, 44, 40)
RED_D = (120, 32, 32)
RED_K = (86, 24, 26)
CREAM_HI = (248, 242, 226)
CREAM = (234, 225, 204)
CREAM_M = (220, 210, 188)
CREAM_S = (200, 189, 166)
CREAM_D = (170, 158, 138)
CEIL_HI = (236, 230, 214)
CEIL = (218, 211, 194)
CEIL_D = (180, 172, 154)
TEAL_HI = (104, 152, 156)
TEAL_L = (84, 134, 142)
TEAL = (68, 118, 128)
TEAL_M = (58, 104, 114)
TEAL_D = (44, 82, 92)
TEAL_K = (32, 60, 68)
CHROME_HI = (246, 248, 250)
CHROME = (204, 210, 218)
CHROME_M = (160, 166, 176)
CHROME_D = (110, 116, 128)
FLOOR_B = (132, 128, 122)     # 地板（靠后壁）
FLOOR_F = (114, 110, 106)     # 地板（近处）
GASKET = (52, 46, 48)
# 车厢外观（对面那节车 / cable_view 共用）
GLASS_D = (34, 56, 74)
GLASS = (56, 90, 114)
GLASS_HI = (150, 192, 212)
HANGER = (78, 82, 92)
HANGER_HI = (140, 146, 156)
HANGER_D = (50, 54, 62)
# 窗外
SKY = [(62, 124, 198), (84, 148, 216), (118, 176, 228), (166, 206, 234), (204, 226, 236)]
SEA = [(176, 208, 206), (122, 174, 176), (84, 148, 158), (62, 126, 144), (48, 108, 130), (40, 94, 118)]
HAZE = (204, 222, 228)


# ============================================================ 小工具
def dk(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


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
        d.rectangle((x0, y0, x1, y1), fill=C(c), outline=C(outline) if outline else None)


def poly_mask(size, pts):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m) > 0


def sea_color(y):
    u = max(0.0, min(1.0, (y - HZ) / (H - HZ))) * (len(SEA) - 1)
    i = min(len(SEA) - 2, int(u))
    return mix(SEA[i], SEA[i + 1], u - i)


def frame_of(t, n=N_SW, fps=FPS_SW):
    return int(math.floor(t * fps + 1e-6)) % n


def _tile(im, w):
    out = A._new(w, im.height)
    for x in range(0, w, im.width):
        out.paste(im, (x, 0))
    return out


# ============================================================ 车厢外观（对面开过来的那节 / cable_view 的大车厢）
def draw_digits(d, x, y, s, col):
    """3×5 的小方块数字（只画图形）。"""
    font = {'0': ('111', '101', '101', '101', '111'), '1': ('010', '110', '010', '010', '111'),
            '2': ('111', '001', '111', '100', '111'), '3': ('111', '001', '011', '001', '111'),
            '7': ('111', '001', '010', '010', '010'), '4': ('101', '101', '111', '001', '001')}
    for ch in s:
        g = font[ch]
        for r, row in enumerate(g):
            for c_, b in enumerate(row):
                if b == '1':
                    px(d, x + c_, y + r, col)
        x += 4


def gondola(w, h, hanger, panes=2, people=(), broken=None, slope=0.0, num='17'):
    """缆车车厢外观（侧视）。w×h = 车身；hanger = 车顶到缆绳的吊臂长度；panes = 侧窗数；
    people = 有乘客剪影的窗（下标）；broken = 撞碎的窗（下标，玻璃没了、能看穿到车里和对面的窗）；
    slope = 缆绳斜率（挂钩的两个轮子跟着斜）。返回 (RGBA, (gx, gy) 挂钩中心——缆绳穿过的那一点, body_box)。
    配色和车里一致：红窗框 / 红车顶 / 奶油色下半截车身 / 镀铬腰线 / 深红裙边。"""
    pad = 4
    big = w >= 40
    gy = 4                                     # 缆绳（2 px 粗）的上沿在图里的 y：缆绳本身不画在这张图里
    iw, ih = w + pad * 2, h + hanger + gy + 5
    im = A._new(iw, ih)
    d = ImageDraw.Draw(im)
    bx0, by0 = pad, gy + 3 + hanger
    bx1, by1 = bx0 + w - 1, by0 + h - 1
    cx = bx0 + w // 2
    rh = max(2, h // 10)                       # 车顶
    wb0 = by0 + rh + 1                         # 窗带
    wb1 = by0 + rh + int(round(h * 0.46))
    # ---- 吊臂：从车顶中间竖直往上；顶上的挂钩 = 两个轮子骑在缆绳上 + 一块夹板从前面包住缆绳
    arm_w = 2 if not big else 3
    for k in range(arm_w):
        vl(d, cx - arm_w // 2 + k, gy + 3, by0 - 1, HANGER_HI if k == 0 else (HANGER if k < arm_w - 1 else HANGER_D))
    if big:                                    # 吊臂中段的减震器 / 车顶的吊臂底座
        rect(d, cx - 2, by0 - hanger // 2 - 2, cx + 2, by0 - hanger // 2 + 2, HANGER_D)
        hl(d, cx - 2, cx + 2, by0 - hanger // 2 - 2, HANGER_HI)
        rect(d, cx - 5, by0 - 3, cx + 5, by0 - 1, HANGER_D)
        hl(d, cx - 5, cx + 5, by0 - 3, HANGER_HI)
    else:
        rect(d, cx - 3, by0 - 2, cx + 3, by0 - 1, HANGER_D)
        hl(d, cx - 3, cx + 3, by0 - 2, HANGER_HI)
    gw = 5 if not big else 8
    for sx in (-1, 1):                         # 两个轮子（压在缆绳上，跟着缆绳的斜度）
        wx = cx + sx * gw // 2
        wy = gy - 2 + int(round(slope * sx * gw / 2))
        if big:
            d.ellipse((wx - 2, wy - 2, wx + 2, wy + 2), fill=C(HANGER_D), outline=C(HANGER_HI))
            px(d, wx, wy, HANGER_HI)
        else:
            d.ellipse((wx - 1, wy - 1, wx + 1, wy + 1), fill=C(HANGER_D))
            px(d, wx, wy - 1, HANGER_HI)
    d.line((cx - gw // 2, gy - 2 - int(round(slope * gw / 2)), cx + gw // 2, gy - 2 + int(round(slope * gw / 2))),
           fill=C(HANGER))                                            # 轮轴之间的梁
    ytop = gy - 1 + int(round(slope * -2))
    rect(d, cx - 2, min(ytop, gy - 1), cx + 2, gy + 3, HANGER)       # 夹板（缆绳从它后面穿过）
    vl(d, cx - 2, min(ytop, gy - 1), gy + 3, HANGER_HI)
    vl(d, cx + 2, min(ytop, gy - 1), gy + 3, HANGER_D)
    # ---- 车身底色
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=3 if big else 2, fill=C(CREAM), outline=C(INK))
    # 车顶（红，比车身窄一点，圆角）
    d.rounded_rectangle((bx0 + 1, by0, bx1 - 1, by0 + rh), radius=2, fill=C(RED_M), outline=C(INK))
    hl(d, bx0 + 3, bx1 - 3, by0 + 1, RED_HI)
    if big:
        rect(d, cx + 8, by0 - 2, cx + 14, by0, RED_D)                # 车顶通风罩
        hl(d, cx + 8, cx + 14, by0 - 2, RED)
    # 窗带：红窗框 + 玻璃
    rect(d, bx0 + 1, wb0, bx1 - 1, wb1, RED)
    hl(d, bx0 + 1, bx1 - 1, wb0, RED_HI)
    hl(d, bx0 + 1, bx1 - 1, wb1, RED_D)
    mul = 3 if big else 2
    inner0, inner1 = bx0 + 2, bx1 - 2
    pw = (inner1 - inner0 + 1 - mul * (panes - 1)) / panes
    pane_boxes = []
    for i in range(panes):
        x0 = int(round(inner0 + i * (pw + mul)))
        x1 = int(round(inner0 + i * (pw + mul) + pw)) - 1
        y0, y1 = wb0 + (2 if big else 1), wb1 - (2 if big else 1)
        pane_boxes.append((x0, y0, x1, y1))
        if broken is not None and i == broken:
            _broken_pane(d, x0, y0, x1, y1, big)
            continue
        # 玻璃：上面反着天光（亮），往下变深；中间透过车里能看到对面那排窗（亮的长方块）
        for y in range(y0, y1 + 1):
            v = (y - y0) / max(1, y1 - y0)
            c = mix(GLASS_HI, GLASS, min(1.0, v * 2.2)) if v < 0.45 else mix(GLASS, GLASS_D, (v - 0.45) / 0.55)
            hl(d, x0, x1, y, c)
        if big:
            rect(d, x0 + 2, y0 + 2, x1 - 2, y0 + (y1 - y0) // 2, mix(GLASS_HI, (200, 226, 236), 0.4))
            hl(d, x0 + 2, x1 - 2, y0 + (y1 - y0) // 2 + 1, GLASS)
        if big:                               # 透过玻璃看到对面那排青绿色椅背（和车里一样）
            hl(d, x0, x1, y1 - 2, mix(TEAL, GLASS_D, 0.35))
            hl(d, x0, x1, y1 - 1, mix(TEAL_M, GLASS_D, 0.35))
            hl(d, x0, x1, y1, mix(TEAL_D, GLASS_D, 0.35))
        # 反光：一道斜线
        for k in range(0, (y1 - y0) // 2 + 1):
            xx = x0 + 1 + k // 2 + (2 if big else 0)
            if xx <= x1:
                px(d, xx, y1 - k - 1, mix(GLASS, (230, 244, 250), 0.55))
        if i in people:                       # 乘客剪影（头 + 肩）
            pc = (x0 + x1) // 2
            sc = (30, 30, 42)
            if big:
                d.ellipse((pc - 2, y1 - 9, pc + 1, y1 - 5), fill=C(sc))
                rect(d, pc - 3, y1 - 4, pc + 2, y1, sc)
                px(d, pc - 4, y1, sc)
                px(d, pc + 3, y1, sc)
                px(d, pc - 1, y1 - 9, (64, 60, 74))
            else:
                rect(d, pc - 1, y1 - 4, pc, y1 - 3, sc)
                rect(d, pc - 2, y1 - 2, pc + 1, y1, sc)
    # 腰线（镀铬）
    hl(d, bx0 + 1, bx1 - 1, wb1 + 1, CHROME_HI)
    hl(d, bx0 + 1, bx1 - 1, wb1 + 2, CHROME_M)
    # 下半截：奶油色车身 + 一道红细条 + 编号牌；底下深红裙边
    lb0, lb1 = wb1 + 3, by1 - (3 if big else 2)
    for y in range(lb0, lb1 + 1):
        v = (y - lb0) / max(1, lb1 - lb0)
        hl(d, bx0 + 1, bx1 - 1, y, CREAM if v < 0.55 else CREAM_M)
    if big:
        ys = lb0 + (lb1 - lb0) // 2 + 1
        hl(d, bx0 + 1, bx1 - 1, ys, RED)
        rect(d, cx - 6, lb0 + 1, cx + 5, lb0 + 7, CREAM_HI, outline=CREAM_D)
        draw_digits(d, cx - 4, lb0 + 2, num, (150, 36, 34))
    else:
        hl(d, bx0 + 1, bx1 - 1, lb0 + (lb1 - lb0) // 2, RED)
    d.rounded_rectangle((bx0, lb1 + 1, bx1, by1), radius=3 if big else 2, fill=C(RED_D), outline=C(INK))
    hl(d, bx0 + 2, bx1 - 2, lb1 + 1, RED)
    # 体积：左边一道亮边、右边一道暗边
    for y in range(by0 + 2, by1 - 1):
        p = im.getpixel((bx0 + 1, y))
        if p[3]:
            px(d, bx0 + 1, y, mix(p[:3], (255, 255, 255), 0.25))
        p = im.getpixel((bx1 - 1, y))
        if p[3]:
            px(d, bx1 - 1, y, dk(p[:3], 0.78))
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=3 if big else 2, outline=C(INK))
    return im, (cx, gy), (bx0, by0, bx1, by1), pane_boxes


def _broken_pane(d, x0, y0, x1, y1, big):
    """车厢外观上被撞碎的那扇窗：玻璃没了，看得穿——车里暗一些：对面那扇窗（亮）、奶油色的墙、青绿色椅背；
    窗框四周一圈亮白的锯齿碎玻璃（上沿挂着两根长尖），窗下沿外面的车身上蹭了几道。"""
    mid = y0 + (y1 - y0) * 50 // 100
    for y in range(y0, y1 + 1):                                                          # 车里（背光，暗）
        v = (y - y0) / max(1, y1 - y0)
        hl(d, x0, x1, y, (70, 62, 64) if v < 0.15 else ((96, 86, 82) if v < 0.75 else TEAL_K))
    fx0, fx1 = x0 + 3, x1 - 3                                                            # 对面那扇窗：一小块亮的天
    for y in range(y0 + 3, mid + 1):
        hl(d, fx0, fx1, y, mix((128, 170, 200), (176, 210, 228), (y - y0 - 3) / max(1, mid - y0 - 3)))
    hl(d, fx0, fx1, mid + 1, RED_D)
    vl(d, (fx0 + fx1) // 2, y0 + 3, mid, RED_D)
    GL, GE = (178, 216, 232), (250, 254, 255)
    for x in range(x0, x1 + 1):                                                          # 上沿锯齿（偶尔长尖）
        dt = int(hrange(0, 3.6, x, 71))
        if hash01(x, 76) < 0.16:
            dt += int(hrange(2, 5 if big else 2, x, 77))
        for y in range(y0, y0 + dt):
            px(d, x, y, GL)
        px(d, x, y0 + dt, GE)
    for x in range(x0, x1 + 1):                                                          # 下沿
        db = int(hrange(0, 3.8, x, 73))
        for y in range(y1 - db + 1, y1 + 1):
            px(d, x, y, GL)
        px(d, x, y1 - db, GE)
    for y in range(y0, y1 + 1):                                                          # 左右两边
        dl = int(hrange(0, 2.6, y, 74))
        dr = int(hrange(0, 2.6, y, 75))
        for k in range(dl):
            px(d, x0 + k, y, GL)
        px(d, x0 + dl, y, GE) if dl else None
        for k in range(dr):
            px(d, x1 - k, y, GL)
        px(d, x1 - dr, y, GE) if dr else None


# ============================================================ 窗外：天空 / 云
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, HZ), SKY, bands=10)
    gradient(im, (0, HZ, W, H), SEA, bands=10)
    return im


CLOUD_Y0 = 28


@lru_cache(maxsize=1)
def clouds_img():
    """640 循环的云（y 28–61）：海平线上一排平底积云 + 上面几朵小的。"""
    hh = HZ - CLOUD_Y0
    im = A._new(640, hh)
    pal = ((255, 255, 255), (236, 244, 250), (206, 224, 240), (184, 206, 228))
    for i in range(6):
        w = hrange(40, 84, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.26, 0.34, i, 2), 600 + i, pal)
        cx = (i + hrange(0.15, 0.85, i, 3)) * 640 / 6
        y = hh - 3 - cl.height + int(hrange(-2, 1, i, 4))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    pal2 = ((255, 255, 255), (232, 240, 250), (206, 222, 240), (184, 204, 230))
    for i in range(5):
        w = hrange(16, 30, i, 11)
        cl = A._cloud_sprite(w, w * 0.34, 700 + i, pal2)
        cx = (i + hrange(0.1, 0.9, i, 12)) * 640 / 5
        y = int(hrange(1, 12, i, 13))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    return im


# ============================================================ 窗外：远景（会随车厢晃）
def _hills(a, x0, x1, base, peaks, seed, lit, mid, shade, rim, haze):
    """远岛：几座山峰叠成的轮廓；朝左的坡亮、朝右的坡暗，山脚往海平线方向发灰（空气透视）。"""
    xs = np.arange(x0, x1, dtype=np.float32)
    hgt = np.zeros_like(xs)
    for (pxx, ph, pw) in peaks:
        hgt += ph * np.exp(-((xs - pxx) / pw) ** 2)
    taper = np.minimum(1.0, np.minimum(xs - x0, x1 - 1 - xs) / 5.0)
    hgt *= np.clip(taper, 0, 1)
    bay = A._bayer(a.shape[1], a.shape[0])
    for i, x in enumerate(range(x0, x1)):
        top = int(round(base - hgt[i]))
        if top >= base:
            continue
        sl = (hgt[min(i + 1, len(xs) - 1)] - hgt[max(i - 1, 0)]) * 0.5
        for y in range(top, base):
            v = sl + hrange(-0.25, 0.25, seed, x, y // 3)
            if v > 0.4 or (v > 0.12 and bay[y, x] < 0.5):
                c = lit
            elif v < -0.4 or (v < -0.12 and bay[y, x] < 0.5):
                c = shade
            else:
                c = mid
            depth = (y - top) / max(1.0, base - top)
            if depth > 0.55 and bay[y, x] < (depth - 0.55) * 1.5:
                c = haze
            a[y, x, :3] = c
            a[y, x, 3] = 255
        a[top, x, :3] = rim if sl >= -0.1 else mid


def _skyline(d, x0, x1, seed, hz=HZ):
    """港口那边的城市天际线（雾里的高楼，亮面朝左）+ 集装箱吊机 + 码头上的集装箱。"""
    x = x0
    i = 0
    while x < x1:
        bw = int(hrange(4, 9, seed, i, 1))
        bh = int(hrange(4, 15, seed, i, 2)) if hash01(seed, i, 3) < 0.75 else int(hrange(14, 19, seed, i, 4))
        back = hash01(seed, i, 5) < 0.45
        base_c = (166, 186, 200) if back else (146, 168, 186)
        lit = mix(base_c, (220, 232, 238), 0.45)
        rect(d, x, hz - bh, x + bw - 1, hz - 1, base_c)
        vl(d, x, hz - bh, hz - 1, lit)
        if bw > 5:
            vl(d, x + 1, hz - bh, hz - 1, mix(base_c, lit, 0.5))
        hl(d, x, x + bw - 1, hz - bh, lit)
        for wy in range(hz - bh + 2, hz - 2, 3):                   # 一排排窗（很淡）
            for wx in range(x + 2, x + bw - 1, 2):
                if hash01(seed, i, wx, wy) < 0.5:
                    px(d, wx, wy, mix(base_c, (110, 130, 150), 0.35))
        if bh > 15 and hash01(seed, i, 6) < 0.6:                   # 楼顶的天线
            vl(d, x + bw // 2, hz - bh - 3, hz - bh - 1, base_c)
        x += bw - (1 if back else 0) + int(hrange(0, 3, seed, i, 7))
        i += 1


def _crane(d, x, h, hz=HZ):
    """集装箱岸桥（雾里）：两条腿 + 顶梁 + 伸向海面的吊臂 + 小司机室。"""
    c = (176, 150, 148)
    cl = (198, 178, 174)
    vl(d, x, hz - h, hz - 1, c)
    vl(d, x + 5, hz - h, hz - 1, c)
    hl(d, x - 1, x + 6, hz - h, cl)
    hl(d, x, x + 5, hz - h + 3, c)
    d.line((x + 5, hz - h, x + 14, hz - h + 1), fill=C(c))            # 吊臂伸向海
    d.line((x - 1, hz - h, x - 4, hz - h), fill=C(c))
    d.line((x + 2, hz - h - 3, x + 12, hz - h), fill=C(cl))           # 拉索
    vl(d, x + 2, hz - h - 3, hz - h, c)
    rect(d, x + 8, hz - h + 1, x + 9, hz - h + 2, (150, 140, 146))


@lru_cache(maxsize=1)
def far_img():
    """远景（320×180，透明底）：海面底色（海平线以下不透明）、城市 / 港口、远处的船和小岛、圣淘沙、回程缆绳。"""
    im = A._new(W, H)
    gradient(im, (0, HZ, W, H), SEA, bands=12)
    d = ImageDraw.Draw(im)
    # 港口：天际线（后排淡、前排深）+ 吊机 + 码头
    _skyline(d, 36, 126, 11)
    for (cx_, h_) in ((96, 11), (110, 12), (124, 10)):
        _crane(d, cx_, h_)
    for x in range(88, 136):                                        # 码头 + 集装箱（一排彩色小块，雾里发灰）
        col = [(176, 132, 120), (140, 160, 176), (190, 176, 140), (150, 170, 150)][int(hash01(x // 3, 41) * 4)]
        if hash01(x // 3, 42) < 0.8:
            px(d, x, HZ - 2, mix(col, HAZE, 0.35))
        px(d, x, HZ - 1, (150, 160, 168))
    a = np.array(im)
    # 远处的小岛（中间偏右）+ 圣淘沙
    _hills(a, 150, 168, HZ, [(156, 3, 4), (162, 4, 4)], 7,
           (150, 180, 170), (132, 164, 160), (116, 148, 150), (170, 196, 188), (172, 198, 204))
    _hills(a, 182, 280, HZ, [(196, 7, 9), (214, 13, 11), (236, 10, 12), (256, 12, 10), (270, 6, 8)], 3,
           (112, 162, 112), (90, 140, 98), (70, 116, 86), (140, 186, 132), (150, 184, 170))
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 圣淘沙：沙滩、红屋顶的房子、灯塔、几棵椰树
    for x in range(188, 276):
        if hash01(x // 4, 51) < 0.82:
            px(d, x, HZ - 1, (236, 222, 180))
        if hash01(x // 5, 52) < 0.35:
            px(d, x, HZ - 2, (226, 214, 176))
    for (hx, hy) in ((200, HZ - 4), (205, HZ - 4), (226, HZ - 5), (248, HZ - 4), (253, HZ - 5)):
        rect(d, hx, hy, hx + 2, hy + 1, (232, 230, 220))
        hl(d, hx, hx + 2, hy - 1, (196, 104, 86))
    vl(d, 262, HZ - 17, HZ - 10, (236, 236, 230))                   # 山顶的灯塔
    px(d, 263, HZ - 15, (200, 200, 196))
    px(d, 262, HZ - 18, (214, 92, 70))
    for (tx, ty) in ((193, HZ - 3), (218, HZ - 3), (241, HZ - 3), (268, HZ - 3)):
        vl(d, tx, ty - 3, ty, (96, 112, 90))
        hl(d, tx - 1, tx + 1, ty - 4, (80, 128, 86))
        px(d, tx - 2, ty - 3, (80, 128, 86))
        px(d, tx + 2, ty - 3, (80, 128, 86))
    # 海平线上远远的船
    for (sx, L) in ((140, 7), (172, 5), (60, 4)):
        hl(d, sx, sx + L, HZ - 1, (120, 138, 150))
        rect(d, sx + L - 2, HZ - 3, sx + L - 1, HZ - 2, (150, 164, 172))
    # 海平线：一道亮的雾线 + 下面一行浅色
    hl(d, 0, W - 1, HZ, (214, 232, 230))
    hl(d, 0, W - 1, HZ + 1, (184, 212, 210))
    return im


@lru_cache(maxsize=1)
def cable_img():
    """回程缆绳（2 px 粗的钢索，上沿一排反光点 = 绞股）。不跟着晃：对面那节车的轮子一直骑在上面。返回 (图, y0)。"""
    im = A._new(W, 3)
    d = ImageDraw.Draw(im)
    for x in range(W):
        px(d, x, 1, (56, 60, 70))
        px(d, x, 2, (84, 88, 100))
        if x % 3 == 0:
            px(d, x, 0, (150, 170, 192))
        if x % 3 == 1:
            px(d, x, 1, (92, 98, 110))
    return im, CABLE_Y - 1


def outside_frame(t):
    f = frame_of(t)
    im = A._new(W, H)
    paste(im, far_img(), 0, SWAY[f])
    return im


# ============================================================ 窗外：海面浪花 + 船（wrap）
SEA_BANDS = [(HZ + 2, 72, 2.0), (72, 88, 4.0), (88, 108, 7.0), (108, 142, 11.0)]
SEA_P = 640


def _wake(d, x, y, L, toward, y0, col_hi, col_lo):
    """船尾的白色尾迹：往船尾方向展开成 V 字，越远越淡（toward = −1 往左展开）。"""
    for k in range(L):
        xx = x + toward * k
        sp = k // 3
        a = 1 - k / L
        c = mix(col_lo, col_hi, a)
        px(d, xx % SEA_P, y - y0, c)
        if sp:
            if hash01(k, x, 1) < 0.8 * a + 0.2:
                px(d, xx % SEA_P, y - y0 - min(sp, 2), c)
            if hash01(k, x, 2) < 0.8 * a + 0.2:
                px(d, xx % SEA_P, y - y0 + min(sp, 3), c)


def _ship(d, kind, x, y, y0, haze=0.0):
    """港口里的船（侧视、朝左开，y = 水线）。haze 越大越发灰（远）。"""
    def h_(c):
        return mix(c, HAZE, haze)
    yy = y - y0
    if kind == 'box':                     # 集装箱船：深色船身 + 一排排彩色集装箱 + 船尾白色船楼
        L = 26
        d.polygon([(x, yy - 3), (x + L, yy - 3), (x + L - 1, yy), (x + 2, yy)], fill=C(h_((60, 52, 58))))
        hl(d, x + 1, x + L - 1, yy - 1, h_((150, 60, 50)))
        for k in range(2, 18, 2):
            col = [(196, 80, 60), (70, 110, 160), (210, 176, 70), (90, 140, 100)][int(hash01(x, k) * 4)]
            rect(d, x + k, yy - 5, x + k + 1, yy - 4, h_(col))
            if hash01(x, k, 2) < 0.6:
                rect(d, x + k, yy - 6, x + k + 1, yy - 6, h_(dk(col, 0.85)))
        rect(d, x + 20, yy - 8, x + 24, yy - 4, h_((236, 236, 230)))
        hl(d, x + 20, x + 24, yy - 7, h_((80, 100, 120)))
        rect(d, x + 22, yy - 10, x + 23, yy - 9, h_((180, 70, 60)))
    elif kind == 'tanker':
        L = 22
        d.polygon([(x, yy - 2), (x + L, yy - 2), (x + L - 1, yy), (x + 1, yy)], fill=C(h_((70, 76, 86))))
        hl(d, x + 1, x + L - 1, yy - 1, h_((130, 70, 60)))
        hl(d, x + 3, x + 16, yy - 3, h_((120, 124, 130)))
        rect(d, x + 17, yy - 6, x + 20, yy - 3, h_((230, 230, 224)))
    elif kind == 'cargo':                 # 杂货船：船头翘、船中两根吊杆、船尾船楼
        L = 30
        d.polygon([(x, yy - 5), (x + 3, yy - 3), (x + L, yy - 3), (x + L - 1, yy), (x + 3, yy)], fill=C(h_((42, 50, 64))))
        hl(d, x + 3, x + L - 1, yy - 1, h_((160, 64, 52)))
        hl(d, x + 4, x + L - 2, yy - 3, h_((96, 104, 116)))
        for k in (9, 15):
            vl(d, x + k, yy - 10, yy - 4, h_((120, 120, 120)))
            d.line((x + k, yy - 10, x + k - 4, yy - 5), fill=C(h_((140, 140, 140))))
        rect(d, x + 21, yy - 9, x + 27, yy - 4, h_((232, 230, 222)))
        hl(d, x + 22, x + 26, yy - 7, h_((70, 90, 110)))
        rect(d, x + 24, yy - 12, x + 25, yy - 10, h_((40, 40, 44)))
        px(d, x + 24, yy - 12, h_((200, 70, 60)))
    elif kind == 'bumboat':               # 驳船（新加坡河上那种木头船：船头画着眼睛，上面一个篷）
        L = 16
        d.polygon([(x, yy - 4), (x + 3, yy - 2), (x + L - 2, yy - 2), (x + L, yy - 4), (x + L - 1, yy), (x + 2, yy)],
                  fill=C(h_((150, 92, 52))))
        hl(d, x + 2, x + L - 2, yy - 2, h_((214, 170, 90)))
        px(d, x + 2, yy - 2, h_((250, 250, 240)))
        px(d, x + 3, yy - 2, h_((40, 40, 40)))
        hl(d, x + 4, x + L - 3, yy - 6, h_((196, 70, 56)))                  # 篷
        hl(d, x + 5, x + L - 4, yy - 7, h_((220, 96, 70)))
        vl(d, x + 5, yy - 5, yy - 3, h_((90, 60, 40)))
        vl(d, x + L - 4, yy - 5, yy - 3, h_((90, 60, 40)))
    elif kind == 'tug':                   # 拖船：红黑船身、白驾驶室、黑烟囱
        L = 12
        d.polygon([(x, yy - 3), (x + L, yy - 3), (x + L - 1, yy), (x + 1, yy)], fill=C(h_((40, 40, 46))))
        hl(d, x + 1, x + L - 1, yy - 1, h_((190, 60, 46)))
        rect(d, x + 3, yy - 6, x + 7, yy - 4, h_((240, 238, 230)))
        hl(d, x + 4, x + 6, yy - 5, h_((70, 96, 120)))
        rect(d, x + 8, yy - 7, x + 9, yy - 4, h_((30, 30, 34)))
        px(d, x + 8, yy - 7, h_((214, 170, 60)))
    elif kind == 'ferry':                 # 渡轮：白船身、蓝条、两层窗
        L = 20
        d.polygon([(x, yy - 4), (x + L, yy - 4), (x + L - 2, yy), (x + 2, yy)], fill=C(h_((240, 240, 236))))
        hl(d, x + 1, x + L - 2, yy - 1, h_((50, 90, 160)))
        rect(d, x + 4, yy - 7, x + L - 4, yy - 5, h_((236, 236, 232)))
        for k in range(5, L - 4, 2):
            px(d, x + k, yy - 6, h_((70, 96, 126)))
            px(d, x + k, yy - 3, h_((70, 96, 126)))
        hl(d, x + 4, x + L - 4, yy - 8, h_((200, 60, 50)))
    elif kind == 'sampan':
        L = 9
        hl(d, x, x + L, yy - 1, h_((120, 80, 50)))
        hl(d, x + 1, x + L - 1, yy, h_((90, 58, 38)))
        px(d, x, yy - 2, h_((120, 80, 50)))
        rect(d, x + 4, yy - 4, x + 5, yy - 2, h_((70, 70, 90)))           # 撑船的人
        px(d, x + 4, yy - 5, h_((210, 190, 140)))
        d.line((x + 6, yy - 5, x + 9, yy + 1), fill=C(h_((150, 120, 80))))


SHIPS = [  # (band, kind, x, waterline y, haze, 尾迹长度)
    (0, 'box', 300, 69, 0.45, 0), (0, 'tanker', 540, 68, 0.5, 0),
    (1, 'cargo', 120, 84, 0.25, 10), (1, 'bumboat', 430, 82, 0.2, 8),
    (2, 'tug', 230, 101, 0.08, 18), (2, 'ferry', 500, 104, 0.08, 22),
    (3, 'sampan', 90, 126, 0.0, 6), (3, 'bumboat', 370, 134, 0.0, 14),
]


@lru_cache(maxsize=8)
def sea_band_img(i):
    """第 i 条海面（透明底，640 循环）：浪花短线（亮线 + 下面一道暗线）+ 这条带里的船和尾迹。
    最下面一条（只在端窗里看得到，人站在前面）压低了对比。"""
    y0, y1, vx = SEA_BANDS[i]
    im = A._new(SEA_P, y1 - y0)
    d = ImageDraw.Draw(im)

    def seg(x, y, L, col):
        for xx in range(x, x + L):
            px(d, xx % SEA_P, y - y0, col)
    calm = 0.55 if i == 3 else 1.0
    for y in range(y0, y1):
        u = (y - HZ) / (H - HZ)
        sea = sea_color(y)
        lite = mix(sea, (232, 246, 244), (0.36 + 0.1 * (1 - u)) * calm)
        dark = dk(sea, 1 - 0.14 * calm)
        gap = 1 + int(u * 4)
        if (y - HZ) % (gap + 1):
            continue
        n = int((26 - 10 * u) * (0.8 if i == 3 else 1.0))
        for j in range(n):
            x = int(hrange(0, SEA_P, y, j, 21))
            L = max(1, int(round((1 + u * 9) * hrange(0.5, 1.25, y, j, 22))))
            if hash01(y, j, 23) < 0.7:
                seg(x, y, L, lite)
                if u > 0.2 and y + 1 < y1:
                    seg(x + 1, y + 1, max(1, L - 1), dark)
            else:
                seg(x, y, L, dark)
    for (b, kind, x, wy, hz, wk) in SHIPS:
        if b != i:
            continue
        if wk:
            _wake(d, x + {'tug': 12, 'ferry': 20, 'bumboat': 16, 'cargo': 30, 'sampan': 9}.get(kind, 10), wy, wk, 1, y0,
                  mix((246, 252, 250), sea_color(wy), 0.15), sea_color(wy))
        _ship(d, kind, x, wy, y0, hz)
    return im


# ============================================================ 窗外：缆车塔（wrap，40 s 经过一次）
TOWER_P = 1280
TOWER_Y0 = 22
TOWER_X = 240                      # 塔在图里的 x（t≈0 时在屏幕右半边）
ST_C = (104, 112, 124)
ST_HI = (156, 164, 176)
ST_D = (72, 78, 90)


@lru_cache(maxsize=1)
def tower_img():
    """钢桁架缆车塔的上半截：两根主腿往下张开、X 形斜撑、顶上横担伸出去（托着回程缆绳的托索轮组）。"""
    hh = 142 - TOWER_Y0
    im = A._new(TOWER_P, hh)
    d = ImageDraw.Draw(im)
    cx = TOWER_X

    def Y(y):
        return y - TOWER_Y0
    top, bot = 30, 141

    def leg_x(y, side):
        u = (y - top) / (bot - top)
        return cx + side * (7 + 14 * u)
    for side in (-1, 1):
        for y in range(top, bot + 1):
            x = int(round(leg_x(y, side)))
            px(d, x, Y(y), ST_HI if side < 0 else ST_D)
            px(d, x + 1, Y(y), ST_C)
            px(d, x - side, Y(y), ST_C if side < 0 else ST_D)
    yy = top + 4
    k = 0
    while yy < bot:
        y2 = min(bot, yy + 12 + k * 2)
        for (ya, yb) in ((yy, y2),):
            d.line((leg_x(ya, -1), Y(ya), leg_x(yb, 1), Y(yb)), fill=C(ST_C))
            d.line((leg_x(ya, 1), Y(ya), leg_x(yb, -1), Y(yb)), fill=C(ST_D))
        hl(d, int(leg_x(y2, -1)), int(leg_x(y2, 1)), Y(y2), ST_C)
        yy = y2
        k += 1
    # 顶上横担（往两边伸，左边一截出了窗户上沿）+ 托索轮组托着缆绳（缆绳 y 33 从轮子上面过）
    rect(d, cx - 22, Y(26), cx + 22, Y(29), ST_C)
    hl(d, cx - 22, cx + 22, Y(26), ST_HI)
    hl(d, cx - 22, cx + 22, Y(29), ST_D)
    for x in range(cx - 20, cx + 21, 5):
        d.line((x, Y(29), x + 3, Y(26)), fill=C(ST_D))
    rect(d, cx - 12, Y(30), cx - 11, Y(37), ST_D)                     # 吊架（从缆绳前面挂下来）
    rect(d, cx + 11, Y(30), cx + 12, Y(37), ST_D)
    rect(d, cx - 13, Y(38), cx + 13, Y(39), ST_D)                     # 轮组的梁
    hl(d, cx - 13, cx + 13, Y(38), ST_C)
    for x in range(cx - 10, cx + 11, 4):                              # 托索轮（缆绳 y 33–34 压在上面）
        d.ellipse((x - 1, Y(35), x + 1, Y(37)), fill=C((60, 64, 74)), outline=C(ST_HI))
    # 塔身上的检修梯 + 红白航空警示带
    for y in range(top + 6, bot, 3):
        hl(d, cx - 1, cx + 1, Y(y), ST_HI)
    for y in range(30, 40):
        for side in (-1, 1):
            x = int(round(leg_x(y, side)))
            c = (214, 70, 56) if (y // 3) % 2 == 0 else (236, 234, 228)
            px(d, x, Y(y), c)
            px(d, x + 1, Y(y), dk(c, 0.85))
    return im


# ============================================================ 窗外：对面开过来的那节车（clouds）
GON_SPAN, GON_VX = 1200, -60.0
GON_X0S = (252.0, 852.0)        # 两节车相隔 600 px：10 s 迎面过来一节


@lru_cache(maxsize=1)
def gondola_small():
    im, (gx, gy), _, _ = gondola(42, 30, 9, panes=3, people=(0, 2), num='12')
    return im, gx, gy


def gondola_y():
    im, gx, gy = gondola_small()
    return CABLE_Y - gy


# ============================================================ 车厢内景
def ceil_x(xb, y):
    """天花板上一条往镜头这边延伸的线：在天花板下沿（y 21）处是 xb，往上按透视展开。"""
    return VP[0] + (xb - VP[0]) * (VP[1] - y) / (VP[1] - CEIL_B)


def floor_x(xb, y):
    """地板上往镜头这边延伸的线：在后壁脚（y 146）处是 xb。"""
    return VP[0] + (xb - VP[0]) * (y - VP[1]) / (FLOOR - VP[1])


def glass_rects():
    """所有玻璃洞：(名字, x0, y0, x1, y1)（含）。"""
    out = []
    for i, (x0, x1) in enumerate(PANES):
        out.append(('pane%d_vent' % i, x0, GL_T, x1, VENT_B))
        out.append(('pane%d' % i, x0, VENT_B + 3, x1, GL_B))
    for i, (x0, x1) in enumerate(DOOR_GL):
        out.append(('door%d' % i, x0, DOOR_GL_Y[0], x1, DOOR_GL_Y[1]))
    for s, (x0, x1) in EW_X.items():
        out.append(('transom_' + s, x0, TR_T, x1, TR_B))
    return out


def skylight_poly():
    x0, x1 = SKY_X
    y0, y1 = 3, 15
    return [(ceil_x(x0, y0), y0), (ceil_x(x1, y0), y0), (ceil_x(x1, y1), y1), (ceil_x(x0, y1), y1)]


def _ceiling(im):
    d = ImageDraw.Draw(im)
    gradient(im, (0, 0, W, CEIL_B - 1), [mix(CEIL_D, (150, 142, 126), 0.4), CEIL_D, CEIL, CEIL_HI], bands=7)
    d = ImageDraw.Draw(im)
    for xb in range(48, 280, 28):                                   # 透视的面板缝
        if SKY_X[0] - 4 < xb < SKY_X[1] + 4:
            continue
        d.line((ceil_x(xb, CEIL_B - 2), CEIL_B - 2, ceil_x(xb, 0), 0), fill=C(mix(CEIL_D, CEIL, 0.3)))
    for y in (7, 13):
        hl(d, 0, W - 1, y, mix(CEIL_D, CEIL, 0.45))
    # 日光灯罩（两条，透视梯形）
    for (xa, xb) in ((66, 118), (201, 253)):
        pts = [(ceil_x(xa, 8), 8), (ceil_x(xb, 8), 8), (ceil_x(xb, 12), 12), (ceil_x(xa, 12), 12)]
        d.polygon(pts, fill=C((252, 248, 232)), outline=C(CEIL_D))
        hl(d, int(ceil_x(xa, 9)) + 2, int(ceil_x(xb, 9)) - 2, 9, (255, 254, 246))
        for k in range(1, 6):
            xx = xa + (xb - xa) * k / 6
            d.line((ceil_x(xx, 9), 9, ceil_x(xx, 11), 11), fill=C((232, 228, 210)))
    # 天窗：窄窄一圈深红框（玻璃是洞，后面是天）；车顶的吊臂 + 头顶那根承载索从天窗里看得见
    sp = skylight_poly()
    d.polygon([(sp[0][0] - 2, sp[0][1] - 2), (sp[1][0] + 2, sp[1][1] - 2), (sp[2][0] + 2, sp[2][1] + 2),
               (sp[3][0] - 2, sp[3][1] + 2)], fill=C(RED_M), outline=C(RED_K))
    d.line([(sp[3][0] - 1, sp[3][1] + 1), (sp[2][0] + 1, sp[2][1] + 1)], fill=C(RED_HI))
    # 喇叭 + 烟感（小圆）
    for (x, y) in ((40 + 8, 10), (W - 49, 10)):
        d.ellipse((x - 3, y - 2, x + 3, y + 2), fill=C(CEIL_HI), outline=C(CEIL_D))
        for k in (-1, 1):
            px(d, x + k, y, (150, 144, 130))
    # 檐口（天花板和墙的交线）
    hl(d, 0, W - 1, CEIL_B - 2, CEIL_HI)
    hl(d, 0, W - 1, CEIL_B - 1, CREAM_S)
    hl(d, 0, W - 1, CEIL_B, (150, 140, 122))


def _skylight_inside(im):
    """天窗里（画在洞里，不透明）：头顶那根承载索横着过去，车顶的吊臂从下面竖上去，顶上两个轮子骑在索上。"""
    d = ImageDraw.Draw(im)
    sp = skylight_poly()
    xa, xb = int(math.ceil(sp[0][0])), int(sp[1][0])
    y_c = 6
    for x in range(xa, xb + 1):                                     # 承载索（2 px，近一点、粗一点）
        px(d, x, y_c, (60, 64, 76) if x % 3 else (120, 128, 142))
        px(d, x, y_c + 1, (40, 42, 52))
    cx = 159
    rect(d, cx - 1, y_c + 2, cx + 2, 15, HANGER)                      # 吊臂
    vl(d, cx - 1, y_c + 2, 15, HANGER_HI)
    vl(d, cx + 2, y_c + 2, 15, HANGER_D)
    for wx in (cx - 4, cx + 5):                                      # 两个轮子压在索上
        rect(d, wx - 1, y_c - 3, wx + 1, y_c - 1, (40, 44, 54))
        px(d, wx, y_c - 2, HANGER_HI)
    hl(d, cx - 4, cx + 5, y_c - 2, HANGER_D)
    rect(d, cx - 2, y_c - 1, cx + 3, y_c + 3, HANGER_D)               # 夹板（包住索）
    hl(d, cx - 2, cx + 3, y_c - 1, HANGER_HI)


def _frame_bevel(d, x0, y0, x1, y1):
    """玻璃洞四周：1 px 橡胶条（深）+ 外面一圈框的高光 / 阴影。"""
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), outline=C(GASKET))
    hl(d, x0 - 2, x1 + 2, y0 - 2, RED_D)          # 框的内侧（上沿在阴影里）
    vl(d, x0 - 2, y0 - 1, y1 + 2, RED_D)
    hl(d, x0 - 1, x1 + 2, y1 + 2, RED_HI)         # 下沿朝上受光
    vl(d, x1 + 2, y0 - 1, y1 + 1, RED_HI)


def _back_wall(im):
    d = ImageDraw.Draw(im)
    # 窗上横梁 + 窗带（整块红框，玻璃之后挖洞）+ 窗台
    rect(d, X_L, HDR[0], X_R - 1, GL_B, RED)
    hl(d, X_L, X_R - 1, HDR[0], RED_HI)
    hl(d, X_L, X_R - 1, HDR[1], RED_D)
    for x in range(X_L + 6, X_R - 4, 8):                             # 横梁上的铆钉
        px(d, x, HDR[0] + 3, RED_HI)
        px(d, x, HDR[0] + 4, RED_D)
    # 下半截墙（座椅后面）
    gradient(im, (X_L, SILL[1] + 1, X_R, FLOOR), [CREAM_M, CREAM_S, mix(CREAM_S, CREAM_D, 0.5)], bands=4)
    d = ImageDraw.Draw(im)
    rect(d, X_L, SILL[0], X_R - 1, SILL[1], RED_M)
    hl(d, X_L, X_R - 1, SILL[0], RED_HI)
    hl(d, X_L, X_R - 1, SILL[1], RED_K)
    hl(d, X_L, X_R - 1, SILL[1] + 1, CREAM_D)
    rect(d, X_L, FLOOR - 3, X_R - 1, FLOOR - 1, (96, 88, 82))         # 踢脚线
    hl(d, X_L, X_R - 1, FLOOR - 3, (130, 120, 110))
    # 侧窗：通风小窗的横档 + 窗框斜面 + 拉手；窗间立柱上的铆钉
    for i, (x0, x1) in enumerate(PANES):
        _frame_bevel(d, x0, GL_T, x1, VENT_B)
        _frame_bevel(d, x0, VENT_B + 3, x1, GL_B)
        rect(d, x0 + (x1 - x0) // 2 - 2, VENT_B + 1, x0 + (x1 - x0) // 2 + 2, VENT_B + 2, CHROME_M)   # 通风窗拉手
        hl(d, x0 + (x1 - x0) // 2 - 2, x0 + (x1 - x0) // 2 + 2, VENT_B + 1, CHROME_HI)
        for y in range(GL_T + 4, GL_B, 10):
            px(d, x0 - 3, y, RED_HI)
            px(d, x1 + 3, y, RED_D)
    # 端窗：粗框 + 横梁 + 铆钉（大玻璃的洞在 pick 里）
    for s, (x0, x1) in EW_X.items():
        _frame_bevel(d, x0, TR_T, x1, TR_B)
        rect(d, x0 - 4, TR_B + 2, x1 + 4, EW_T - 2, RED_M)            # 气窗和大玻璃之间的横梁
        hl(d, x0 - 4, x1 + 4, TR_B + 2, RED_HI)
        hl(d, x0 - 4, x1 + 4, EW_T - 2, RED_D)
        rect(d, x0 - 4, EW_B + 1, x1 + 4, FLOOR - 4, RED_M)            # 窗台（低，玻璃一直落到 y 140）
        hl(d, x0 - 4, x1 + 4, EW_B + 1, RED_HI)
        for x in range(x0 - 3, x1 + 4):                               # 窗台上一道黄黑警示斜纹（压暗了）
            for y in (EW_B + 1, EW_B + 2):
                px(d, x, y, (196, 166, 72) if ((x + y) // 3) % 2 == 0 else (74, 64, 56))
        rect(d, x0 - 4, EW_B + 3, x1 + 4, FLOOR - 4, (170, 174, 182))   # 铝踢脚板
        hl(d, x0 - 4, x1 + 4, EW_B + 3, CHROME)
        for x in range(x0, x1 + 1, 6):
            px(d, x, EW_B + 4, CHROME_D)
        _frame_bevel(d, x0, EW_T, x1, EW_B)
        for y in range(EW_T + 2, EW_B, 7):                           # 粗窗框上一列铆钉
            for xx in (x0 - 3, x1 + 3):
                px(d, xx, y, RED_HI)
                px(d, xx, y + 1, RED_K)
        for xx in (x0 + 6, x1 - 6):                                  # 横梁上的螺栓
            px(d, xx, TR_B + 3, RED_HI)
    # 窗台下的镀铬扶手（长椅那两段）
    for (x0, x1) in BENCHES:
        hl(d, x0 + 1, x1 - 1, GRAB_Y, CHROME_HI)
        hl(d, x0 + 1, x1 - 1, GRAB_Y + 1, CHROME_D)
        for x in (x0 + 3, x1 - 3, (x0 + x1) // 2):
            rect(d, x, GRAB_Y - 2, x + 1, GRAB_Y - 1, CHROME_M)


def _door(im):
    d = ImageDraw.Draw(im)
    x0, x1 = DOOR
    rect(d, x0, HDR[1] + 1, x1, FLOOR - 1, RED_M)                    # 门框
    vl(d, x0, HDR[1] + 1, FLOOR - 1, RED_HI)
    vl(d, x1, HDR[1] + 1, FLOOR - 1, RED_K)
    rect(d, x0 + 3, HDR[1] + 1, x1 - 3, HDR[1] + 4, (120, 116, 112))  # 门顶的拉门机构罩
    hl(d, x0 + 3, x1 - 3, HDR[1] + 1, (160, 156, 150))
    for (la, lb) in ((x0 + 3, 159), (160, x1 - 3)):                  # 两扇门
        rect(d, la, HDR[1] + 5, lb, FLOOR - 1, CREAM)
        vl(d, la, HDR[1] + 5, FLOOR - 1, CREAM_HI)
        vl(d, lb, HDR[1] + 5, FLOOR - 1, CREAM_S)
        rect(d, la + 1, 96, lb - 1, 99, RED)                         # 门上的一道红条
        hl(d, la + 1, lb - 1, 96, RED_HI)
        rect(d, la + 1, 136, lb - 1, FLOOR - 2, (176, 180, 188))      # 踢脚板
        hl(d, la + 1, lb - 1, 136, CHROME)
        for yy in range(139, FLOOR - 2, 3):
            hl(d, la + 2, lb - 2, yy, (156, 160, 168))
        rect(d, la + 2, 104, lb - 2, 132, mix(CREAM, CREAM_M, 0.5))   # 下半截门板（凹进去一点）
        hl(d, la + 2, lb - 2, 104, CREAM_S)
        vl(d, la + 2, 104, 132, CREAM_S)
        hl(d, la + 2, lb - 2, 132, CREAM_HI)
    for (gx0, gx1) in DOOR_GL:
        y0, y1 = DOOR_GL_Y
        rect(d, gx0 - 2, y0 - 2, gx1 + 2, y1 + 2, RED)
        _frame_bevel(d, gx0, y0, gx1, y1)
    vl(d, 159, HDR[1] + 5, FLOOR - 1, (40, 36, 40))                   # 门中缝（橡胶条）
    vl(d, 160, HDR[1] + 5, FLOOR - 1, (64, 58, 60))
    for hx in (156, 163):                                            # 竖把手
        vl(d, hx, 102, 118, CHROME_HI)
        vl(d, hx + 1, 102, 118, CHROME_D)
        px(d, hx, 101, CHROME_M)
        px(d, hx, 119, CHROME_M)
    # 门上的黄色警示贴（夹手：小三角）
    for (cx_, cy_) in ((150, 110), (169, 110)):
        d.polygon([(cx_, cy_ - 4), (cx_ - 4, cy_ + 2), (cx_ + 4, cy_ + 2)], fill=C((236, 196, 60)), outline=C((90, 70, 30)))
        px(d, cx_, cy_ - 1, (60, 50, 30))
        px(d, cx_, cy_ + 1, (60, 50, 30))
    # 门楣上的车厢编号牌（白底红字，只画图形）+ 牌子两边的小灯
    rect(d, 149, HDR[0] - 1, 170, HDR[1], CREAM_HI, outline=RED_K)
    draw_digits(d, 154, HDR[0] + 1, '17', RED_D)
    hl(d, 150, 169, HDR[1] - 1, CREAM_S)
    for lx in (145, 174):
        rect(d, lx - 1, HDR[0] + 2, lx + 1, HDR[0] + 4, (250, 236, 170))
        px(d, lx, HDR[0] + 3, (255, 255, 230))
    # 门槛
    rect(d, x0 + 1, FLOOR - 1, x1 - 1, FLOOR + 1, (176, 180, 188))
    hl(d, x0 + 1, x1 - 1, FLOOR - 1, CHROME_HI)
    hl(d, x0 + 1, x1 - 1, FLOOR + 1, CHROME_D)


def _bench(im, x0, x1):
    """一段长椅（青绿色人造革）：靠背（三个座位，竖缝）、座垫面、前沿，下面是带暖气百叶的底座。压低了对比。"""
    d = ImageDraw.Draw(im)
    # 靠背
    for y in range(BK_T, SEAT_T):
        v = (y - BK_T) / (SEAT_T - BK_T)
        c = TEAL_L if v < 0.12 else (TEAL if v < 0.75 else TEAL_M)
        hl(d, x0, x1, y, c)
    d.rounded_rectangle((x0, BK_T - 1, x1, SEAT_T - 1), radius=3, outline=C(TEAL_D))
    hl(d, x0 + 3, x1 - 3, BK_T, TEAL_HI)
    n = 3
    for k in range(1, n):
        xs = x0 + (x1 - x0) * k // n
        vl(d, xs, BK_T + 2, SEAT_T - 2, TEAL_D)
        vl(d, xs + 1, BK_T + 3, SEAT_T - 2, TEAL_L)
    for k in range(n):                                               # 每个座位靠背一道横缝（压低对比）
        xa = x0 + (x1 - x0) * k // n + 3
        xb = x0 + (x1 - x0) * (k + 1) // n - 3
        hl(d, xa, xb, BK_T + 9, TEAL_M)
    # 座垫面（从上面斜看下去，亮一点）+ 前沿圆角
    for y in range(SEAT_T, SEAT_F):
        hl(d, x0 - 1, x1 + 1, y, TEAL_HI if y == SEAT_T else TEAL_L)
    hl(d, x0 - 1, x1 + 1, SEAT_F, TEAL)
    hl(d, x0 - 1, x1 + 1, SEAT_F + 1, TEAL_D)
    for k in range(1, n):
        xs = x0 + (x1 - x0) * k // n
        vl(d, xs, SEAT_T + 1, SEAT_F, TEAL)
    # 底座（奶油色铁皮 + 暖气百叶）落在地板上 y 149
    rect(d, x0 + 1, SEAT_F + 2, x1 - 1, BASE_B, CREAM_S)
    hl(d, x0 + 1, x1 - 1, SEAT_F + 2, TEAL_K)
    for y in (SEAT_F + 4, SEAT_F + 6):
        for x in range(x0 + 4, x1 - 3, 6):
            hl(d, x, x + 3, y, CREAM_D)
    hl(d, x0 + 1, x1 - 1, BASE_B, (120, 112, 102))
    # 两头的镀铬扶手（L 形）
    for (ax, side) in ((x0 - 1, -1), (x1 + 1, 1)):
        vl(d, ax, BK_T + 8, SEAT_T + 2, CHROME)
        vl(d, ax - side, BK_T + 8, SEAT_T + 2, CHROME_D)
        hl(d, min(ax, ax - side * 4), max(ax, ax - side * 4), BK_T + 8, CHROME_HI)


def _end_wall(im, left):
    """端壁（正对着画；最外 4 px 是剖开的断面）。左：线路图、对讲机、灭火器、禁烟牌；右：紧急说明、急救箱、禁烟牌。"""
    d = ImageDraw.Draw(im)
    if left:
        x0, x1 = 0, X_L - 1
    else:
        x0, x1 = X_R, W - 1
    gradient(im, (x0, CEIL_B + 1, x1 + 1, FRONT), [mix(CREAM_M, CREAM_S, 0.4), CREAM_S, mix(CREAM_S, CREAM_D, 0.6)], bands=5)
    d = ImageDraw.Draw(im)
    # 天花板和端壁的交线（往镜头这边斜上去）：交线以上是天花板（压暗一点）
    for x in range(x0, x1 + 1):
        dist = (X_L - 1 - x) if left else (x - X_R)
        yj = int(round(CEIL_B - dist * 0.42))
        for y in range(max(0, yj), CEIL_B + 1):
            d.point((x, y), fill=C(mix(CREAM_M, CREAM_S, 0.3) if y > yj else (150, 140, 122)))
    # 剖开的断面（深红）+ 转角立柱
    cut = (x0, x0 + 3) if left else (x1 - 3, x1)
    rect(d, cut[0], 0, cut[1], FRONT - 1, RED_D)
    vl(d, cut[1] if left else cut[0], 0, FRONT - 1, RED_M)
    vl(d, cut[0] if left else cut[1], 0, FRONT - 1, RED_K)
    post = (X_L - 4, X_L - 1) if left else (X_R, X_R + 3)
    rect(d, post[0], CEIL_B + 1, post[1], FRONT - 1, RED_M)
    vl(d, post[0], CEIL_B + 1, FRONT - 1, RED_HI if not left else RED_D)
    vl(d, post[1], CEIL_B + 1, FRONT - 1, RED_D if not left else RED_HI)
    # 一道腰线（奶油色墙上的红线）+ 下面暖气百叶
    wx0, wx1 = (x0 + 5, post[0] - 2) if left else (post[1] + 2, x1 - 5)
    hl(d, wx0, wx1, 108, RED)
    hl(d, wx0, wx1, 109, RED_D)
    rect(d, wx0, 148, wx1, 172, mix(CREAM_S, CREAM_D, 0.6), outline=CREAM_D)
    for y in range(151, 171, 3):
        hl(d, wx0 + 2, wx1 - 2, y, (130, 120, 108))
        hl(d, wx0 + 2, wx1 - 2, y + 1, CREAM_S)
    hl(d, wx0, wx1, 173, (110, 102, 94))
    if left:
        # 线路图：花柏山 ●——（海）——● 圣淘沙，红色小车厢在线上
        rect(d, 7, 33, 32, 58, (60, 56, 60))
        rect(d, 8, 34, 31, 57, (244, 240, 228))
        rect(d, 9, 50, 30, 56, (120, 176, 196))                         # 海
        for x in range(10, 30, 3):
            px(d, x, 52 + (x // 3) % 2, (180, 214, 226))
        d.polygon([(9, 50), (9, 40), (14, 44), (17, 50)], fill=C((96, 150, 96)))     # 花柏山
        d.polygon([(23, 50), (27, 46), (30, 47), (30, 50)], fill=C((110, 166, 104)))  # 圣淘沙
        d.line((11, 41, 28, 47), fill=C((50, 50, 60)))
        d.ellipse((9, 39, 13, 43), fill=C(RED), outline=C(RED_K))
        d.ellipse((26, 45, 30, 49), fill=C(RED), outline=C(RED_K))
        rect(d, 18, 44, 20, 46, RED)
        vl(d, 19, 42, 43, (50, 50, 60))
        hl(d, 10, 22, 36, (90, 90, 100))                                # 标题（只画横线）
        hl(d, 10, 18, 37, (150, 150, 160))
        # 对讲机 + 红色紧急按钮
        rect(d, 20, 66, 32, 84, (150, 152, 156), outline=(88, 90, 96))
        hl(d, 21, 31, 67, (190, 192, 196))
        for y in range(70, 77, 2):
            for x in range(23, 30, 2):
                px(d, x, y, (70, 72, 78))
        d.ellipse((24, 78, 28, 82), fill=C((214, 50, 44)), outline=C((110, 30, 30)))
        px(d, 25, 79, (255, 150, 140))
        # 灭火器（挂在支架上）
        rect(d, 9, 96, 12, 98, (90, 90, 96))
        d.rounded_rectangle((8, 100, 15, 126), radius=3, fill=C((200, 44, 40)), outline=C((100, 22, 22)))
        vl(d, 9, 103, 124, (240, 110, 100))
        rect(d, 10, 96, 13, 100, (40, 40, 44))
        d.line((14, 98, 18, 104), fill=C((40, 40, 44)))
        d.line((18, 104, 17, 116), fill=C((40, 40, 44)))
        rect(d, 9, 110, 14, 114, (236, 232, 220))
        hl(d, 7, 16, 127, (90, 90, 96))
        # 禁烟牌
        _no_smoking(d, 28, 96)
    else:
        # 紧急说明图牌（三行小人 + 箭头）
        rect(d, 287, 33, 312, 58, (60, 56, 60))
        rect(d, 288, 34, 311, 57, (244, 240, 228))
        rect(d, 288, 34, 311, 37, (40, 120, 70))
        for k, y in enumerate((41, 47, 53)):
            rect(d, 291, y - 2, 292, y, (50, 50, 60))                   # 小人
            px(d, 291, y - 3, (50, 50, 60))
            d.line((295, y - 1, 300, y - 1), fill=C((50, 50, 60)))      # 箭头
            px(d, 299, y - 2, (50, 50, 60))
            px(d, 299, y, (50, 50, 60))
            rect(d, 303, y - 3, 308, y, [(120, 176, 196), (214, 60, 50), (240, 200, 60)][k])
        # 急救箱（白底绿十字）
        rect(d, 287, 66, 302, 80, (240, 240, 236), outline=(130, 130, 130))
        hl(d, 288, 301, 67, (255, 255, 255))
        rect(d, 293, 69, 296, 77, (50, 150, 80))
        rect(d, 290, 72, 299, 74, (50, 150, 80))
        hl(d, 287, 302, 80, (110, 110, 110))
        # 禁烟牌 + 一块小镜子似的检查记录卡
        _no_smoking(d, 307, 72)
        rect(d, 300, 92, 312, 104, (230, 226, 210), outline=(140, 134, 120))
        for y in range(95, 103, 2):
            hl(d, 302, 310, y, (170, 164, 150))


def _no_smoking(d, cx, cy):
    d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=C((250, 250, 248)), outline=C((206, 46, 40)))
    hl(d, cx - 2, cx + 2, cy, (60, 60, 60))
    px(d, cx + 3, cy, (230, 120, 60))
    d.line((cx - 3, cy - 3, cx + 3, cy + 3), fill=C((206, 46, 40)))


def _floor(im):
    """铝合金防滑花纹板（交错的短斜纹，压低对比）+ 往灭点收的板缝 + 近侧门槛（剖面）。"""
    a = np.array(im)
    for y in range(FLOOR, FRONT):
        u = (y - FLOOR) / (FRONT - FLOOR)
        base = mix(FLOOR_B, FLOOR_F, u)
        a[y, :, :3] = base
        a[y, :, 3] = 255
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    y = FLOOR + 2
    row = 0
    while y < FRONT - 1:
        u = (y - FLOOR) / (FRONT - FLOOR)
        base = mix(FLOOR_B, FLOOR_F, u)
        hi = mix(base, (176, 172, 166), 0.32)
        lo = dk(base, 0.86)
        step = 6 + int(u * 3)
        off = (row % 2) * (step // 2)
        for x in range(off, W, step):
            xx = x
            if row % 2 == 0:                       # '/'
                px(d, xx, y + 1, hi)
                px(d, xx + 1, y, hi)
                px(d, xx + 1, y + 1, lo)
            else:                                  # '\'
                px(d, xx, y, hi)
                px(d, xx + 1, y + 1, hi)
                px(d, xx, y + 1, lo)
        y += 3 + int(u * 2)
        row += 1
    for xb in (40, 100, 160, 220, 280):            # 板缝（往灭点收）
        for yy in range(FLOOR + 1, FRONT):
            x = int(round(floor_x(xb, yy)))
            if 0 <= x < W:
                p = im.getpixel((x, yy))
                d.point((x, yy), fill=C(dk(p[:3], 0.88)))
    hl(d, 0, W - 1, 161, dk(mix(FLOOR_B, FLOOR_F, 0.5), 0.9))
    # 后壁脚 / 座椅前面的接触阴影
    for x in range(W):
        p = im.getpixel((x, FLOOR))
        d.point((x, FLOOR), fill=C(dk(p[:3], 0.82)))
    for (x0, x1) in BENCHES:
        hl(d, x0, x1, BASE_B + 1, dk(FLOOR_B, 0.8))
        for x in range(x0 + 1, x1, 2):
            px(d, x, BASE_B + 2, dk(FLOOR_B, 0.9))
    # 近侧门槛（车厢地板的剖面）
    rect(d, 0, FRONT, W - 1, H - 1, (84, 82, 84))
    hl(d, 0, W - 1, FRONT, (176, 178, 182))
    hl(d, 0, W - 1, FRONT + 1, (128, 128, 132))
    for x in range(4, W, 16):
        px(d, x, FRONT + 2, (150, 150, 154))


def _sun_patches(im):
    """窗户斜射进来的光斑（地板上，往右下斜的平行四边形，边缘抖动）。"""
    a = np.array(im).astype(np.float32)
    bay = A._bayer(W, H)
    m = np.zeros((H, W), np.float32)
    ops = [(x0, x1, 151, 20) for (x0, x1) in PANES] + [(x0, x1, 150, 14) for (x0, x1) in DOOR_GL] + \
          [(x0, x1, 147, 26) for (x0, x1) in EW_X.values()]
    for (x0, x1, yt, hgt) in ops:
        sk = 0.5
        pts = [(x0 + 5, yt), (x1 + 5, yt), (x1 + 5 + sk * hgt, yt + hgt), (x0 + 5 + sk * hgt, yt + hgt)]
        pm = poly_mask((W, H), pts)
        m = np.maximum(m, pm.astype(np.float32))
    # 边上一圈只亮一半（抖动），中间亮满
    core = ndimage.binary_erosion(m > 0, iterations=1)
    lvl = np.where(core, 1.0, np.where(m > 0, 0.5, 0.0))
    on = (bay < lvl) & (np.arange(H)[:, None] >= FLOOR) & (np.arange(H)[:, None] < FRONT)
    a[on, :3] = a[on, :3] * np.array((1.13, 1.11, 1.06), np.float32) + 4
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def _poles_and_rail(im):
    d = ImageDraw.Draw(im)
    # 竖扶手杆（天花板到地板）
    for x in POLES:
        vl(d, x, CEIL_B - 1, BASE_B, CHROME_HI)
        vl(d, x + 1, CEIL_B - 1, BASE_B, CHROME_D)
        rect(d, x - 1, CEIL_B - 2, x + 2, CEIL_B, CHROME_M)
        rect(d, x - 1, BASE_B - 1, x + 2, BASE_B + 1, CHROME_M)
        hl(d, x - 1, x + 2, BASE_B - 1, CHROME_HI)
        hl(d, x - 2, x + 3, BASE_B + 2, dk(FLOOR_B, 0.78))
    # 吊环杆（天花板下面，y 17–18）+ 吊架
    x0, x1 = X_L + 4, X_R - 5
    hl(d, x0, x1, 17, CHROME_HI)
    hl(d, x0, x1, 18, CHROME_D)
    for x in (x0, 88, 132, 187, 231, x1):
        vl(d, x, 12 if not (SKY_X[0] < x < SKY_X[1]) else 16, 16, CHROME_M)
        px(d, x, 11, CHROME_D)


def _texture_and_grade(im):
    A._tex_noise(im, (0, 0, W, CEIL_B), 0.035, 81)
    A._tex_noise(im, (X_L, HDR[0], X_R, FLOOR), 0.03, 82)
    A._tex_noise(im, (0, CEIL_B, X_L, FRONT), 0.03, 83)
    A._tex_noise(im, (X_R, CEIL_B, W, FRONT), 0.03, 84)
    # 光：窗户那一带最亮，天花板远处、两头端壁、地板近处慢慢暗下去（4 % 一档，Bayer 抖动过渡）
    a = np.array(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    li = np.ones((H, W), np.float32)
    li *= 0.88 + 0.12 * np.clip(yy / CEIL_B, 0, 1)
    li *= 1 - 0.08 * np.clip((np.abs(xx - 159.5) - 118) / 42, 0, 1)
    li *= 1 - 0.06 * np.clip((yy - 158) / 18, 0, 1) * (yy < FRONT)
    q = np.floor(li * 25 + A._bayer(W, H)) / 25.0
    a[..., :3] *= q[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    out = A._grade(im, sat=0.95, val=1.0)
    return out


@lru_cache(maxsize=1)
def cabin_opaque():
    """不含玻璃的内景（窗户位置先是红框，_punch 再挖洞）。"""
    im = A._new(W, H, CREAM)
    _ceiling(im)
    _back_wall(im)
    _door(im)
    for (x0, x1) in BENCHES:
        _bench(im, x0, x1)
    _end_wall(im, True)
    _end_wall(im, False)
    _floor(im)
    _sun_patches(im)
    _poles_and_rail(im)
    return _texture_and_grade(im)


def _glare(a, x0, y0, x1, y1, seed, tint_a=26, streak_a=(64, 40)):
    """玻璃：整块淡淡的白蓝色（半透明）+ 两道斜反光。直接写像素（洞里原来是透明的）。"""
    a[y0:y1 + 1, x0:x1 + 1, :3] = (222, 238, 246)
    a[y0:y1 + 1, x0:x1 + 1, 3] = tint_a
    c0 = int(hrange(-6, 10, seed, 1))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            s = (x - x0) + (y1 - y) * 0.55 - c0
            if 0 <= s % 40 < 3:
                a[y, x, :3] = (250, 252, 255)
                a[y, x, 3] = streak_a[0]
            elif 5 <= s % 40 < 6:
                a[y, x, :3] = (246, 250, 255)
                a[y, x, 3] = streak_a[1]


def _punch(im):
    """挖洞：侧窗 / 门窗 / 气窗 = 半透明玻璃（淡色 + 反光）；天窗 = 全透明（再画吊臂和承载索）；端窗大玻璃 = 全透明。"""
    a = np.array(im)
    for i, (name, x0, y0, x1, y1) in enumerate(glass_rects()):
        _glare(a, x0, y0, x1, y1, i)
    sm = poly_mask((W, H), skylight_poly())
    a[sm, 3] = 0
    for s, (x0, x1) in EW_X.items():
        a[EW_T:EW_B + 1, x0:x1 + 1, 3] = 0
        a[EW_T:EW_B + 1, x0:x1 + 1, :3] = 0
    im = Image.fromarray(a, 'RGBA')
    _skylight_inside(im)
    return im


# ============================================================ 端窗：完好 / 撞碎
def _ew_intact(im, s):
    x0, x1 = EW_X[s]
    a = np.array(im)
    _glare(a, x0, EW_T, x1, EW_B, 30 + (s == 'r'), tint_a=34, streak_a=(70, 44))
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    # “请勿倚靠”警示贴：黄色三角 + 黑色感叹号（只画图形），贴在大玻璃靠上的角上
    cx, cy = (x0 + 7, EW_T + 8) if s == 'l' else (x1 - 7, EW_T + 8)
    d.polygon([(cx, cy - 5), (cx - 5, cy + 4), (cx + 5, cy + 4)], fill=C((240, 200, 62)), outline=C((70, 56, 30)))
    vl(d, cx, cy - 2, cy + 1, (40, 34, 26))
    px(d, cx, cy + 3, (40, 34, 26))


SHARD_EDGE = (236, 248, 252)
SHARD_IN = (190, 222, 232)
SHARD_D = (120, 160, 176)


def _zigzag(seed, k, length, deep):
    """沿一条边生成锯齿断口：[(沿边位置, 往里的深度)]，谷浅尖深，偶尔一根很长的尖。"""
    pts = [(0.0, hrange(1, 4, seed, k, 99))]
    t = 0.0
    i = 0
    while True:
        t += hrange(2.5, 6.0, seed, k, i, 5)
        if t >= length:
            break
        tip = hrange(3, 9, seed, k, i, 2) * deep
        if hash01(seed, k, i, 3) < 0.22:
            tip += hrange(6, 16, seed, k, i, 4) * deep
        pts.append((t, tip))
        t += hrange(2.5, 6.0, seed, k, i, 6)
        if t >= length:
            break
        pts.append((t, hrange(0, 2.2, seed, k, i, 1)))
        i += 1
    pts.append((float(length), hrange(1, 4, seed, k, 98)))
    return pts


def _ew_broken(im, s):
    """撞碎：中间整块没了（全透明，直接看到天和海）；窗框四周留一圈锯齿状的碎玻璃（淡玻璃色半透明，
    断口一道亮白线 + 里面一道浅青线），长尖上有几道裂纹；窗台、踢脚板和前面的地板上散着十几块碎玻璃。"""
    x0, x1 = EW_X[s]
    a = np.array(im)
    seed = 7 if s == 'l' else 9
    gw, gh = x1 - x0, EW_B - EW_T
    fill = Image.new('L', (W, H), 0)
    edge = Image.new('L', (W, H), 0)
    rim = Image.new('L', (W, H), 0)
    crack = Image.new('L', (W, H), 0)
    df, de, dr, dc = (ImageDraw.Draw(m) for m in (fill, edge, rim, crack))
    sides = [  # (k, 长度, 位置→坐标, 往里的方向, 深度系数)
        (1, gw, lambda t, dd: (x0 + t, EW_T + dd), (0, -1), 1.15),     # 上沿（挂着的尖长一点）
        (2, gw, lambda t, dd: (x0 + t, EW_B - dd), (0, 1), 0.7),       # 下沿
        (3, gh, lambda t, dd: (x0 + dd, EW_T + t), (-1, 0), 0.85),     # 左沿
        (4, gh, lambda t, dd: (x1 - dd, EW_T + t), (1, 0), 0.85),      # 右沿
    ]
    for (k, L, P, (ox, oy), deep) in sides:
        zz = _zigzag(seed, k, L, deep)
        line = [P(t, dd) for (t, dd) in zz]
        base0, base1 = P(0, 0), P(L, 0)
        df.polygon([base0] + line + [base1], fill=255)
        de.line(line, fill=255)
        dr.line([(x + ox, y + oy) for (x, y) in line], fill=255)
        for j, (t, dd) in enumerate(zz):                             # 长尖上的裂纹：从尖往框斜回去
            if dd > 9:
                tx, ty = P(t, dd)
                bx, by = P(t + hrange(-5, 5, seed, k, j, 7), 0)
                dc.line((tx, ty, bx, by), fill=255)
    # 两个角上大一点的三角碎片
    for i, (cx, cy, sx, sy) in enumerate([(x0, EW_T, 1, 1), (x1, EW_B, -1, -1)] if s == 'l' else
                                         [(x1, EW_T, -1, 1), (x0, EW_B, 1, -1)]):
        Lx, Ly = hrange(9, 15, seed, i, 21), hrange(14, 24, seed, i, 22)
        tri = [(cx, cy), (cx + sx * Lx, cy), (cx, cy + sy * Ly)]
        df.polygon(tri, fill=255)
        de.line([tri[1], tri[2]], fill=255)
        dc.line((cx + sx * 2, cy + sy * 2, cx + sx * Lx * 0.45, cy + sy * Ly * 0.55), fill=255)
    box = np.zeros((H, W), bool)
    box[EW_T:EW_B + 1, x0:x1 + 1] = True
    rem = (np.array(fill) > 0) & box
    e = (np.array(edge) > 0) & box
    r = (np.array(rim) > 0) & rem & ~e
    c_ = (np.array(crack) > 0) & rem & ~e
    a[box, 3] = 0
    a[box, :3] = 0
    a[rem, :3] = SHARD_IN
    a[rem, 3] = 104
    a[r, :3] = (176, 220, 234)
    a[r, 3] = 170
    a[c_, :3] = (244, 250, 252)
    a[c_, 3] = 150
    a[e, :3] = SHARD_EDGE
    a[e, 3] = 236
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    # 碎玻璃（窗台 / 踢脚板 / 地板上），三角小块 + 亮点
    for i in range(16):
        fx = hrange(x0 - 4, x1 + 12, seed, i, 41) if s == 'l' else hrange(x0 - 12, x1 + 4, seed, i, 41)
        fy = hrange(EW_B + 1, 157, seed, i, 42) ** 1.0
        if fy < FLOOR and hash01(seed, i, 43) < 0.5:
            fy = hrange(FLOOR, 156, seed, i, 44)
        fx, fy = int(fx), int(fy)
        sz = 1 + int(hash01(seed, i, 45) * 3)
        if sz == 1:
            px(d, fx, fy, SHARD_EDGE)
            px(d, fx + 1, fy, SHARD_D)
        else:
            pts = [(fx, fy), (fx + sz, fy - (sz - 1)), (fx + sz + 1, fy)]
            d.polygon(pts, fill=C(SHARD_IN), outline=C(SHARD_D))
            px(d, fx + sz, fy - (sz - 1), SHARD_EDGE)
            px(d, fx + 1, fy, (90, 120, 136))


@lru_cache(maxsize=4)
def cabin_full(sl=0, sr=0):
    """某个端窗状态下完整的车厢层（RGBA）。"""
    im = _punch(cabin_opaque().copy())
    for s, st in (('l', sl), ('r', sr)):
        if st:
            _ew_broken(im, s)
        else:
            _ew_intact(im, s)
    return im


def _pick_split():
    """base（两种状态都一样的像素）+ 两扇端窗各自的 pick 框和两张图。"""
    full00 = np.array(cabin_full(0, 0))
    base = full00.copy()
    out = {}
    for s, (sl, sr) in (('l', (1, 0)), ('r', (0, 1))):
        a1 = np.array(cabin_full(sl, sr))
        diff = (full00 != a1).any(-1)
        ys, xs = np.nonzero(diff)
        box = (int(xs.min()) - 1, int(ys.min()) - 1, int(xs.max()) + 2, int(ys.max()) + 2)
        x0, y0, x1, y1 = box
        same = ~diff & (full00[..., 3] == 255)
        sub = base[y0:y1, x0:x1]
        sub[~same[y0:y1, x0:x1]] = 0
        out[s] = (box, [Image.fromarray(full00).crop(box), Image.fromarray(a1).crop(box)])
    return Image.fromarray(base, 'RGBA'), out


@lru_cache(maxsize=1)
def build():
    base, picks = _pick_split()
    return dict(sky=sky_img(), clouds=clouds_img(), far=far_img(), sea=[sea_band_img(i) for i in range(len(SEA_BANDS))],
                cable=cable_img(), tower=tower_img(), gondola=gondola_small()[0], cabin=base, picks=picks)


# ============================================================ 吊环（strip）
def straps_frame(t):
    """吊环：挂在吊环杆上，带子 + 三角形的塑料拉手，跟着车厢晃（和窗外反向）±1 px。"""
    im = A._new(W, H)
    d = ImageDraw.Draw(im)
    f = frame_of(t)
    ph = math.tau * f / N_SW
    for i, x in enumerate(STRAPS):
        sw = -1.25 * math.sin(ph - 0.35 + 0.08 * (i % 3))
        dx = int(round(sw))
        top = 19
        L = 16 + (i % 2) * 2
        bx = x + dx
        rect(d, x - 1, 16, x + 1, 19, (64, 60, 62))                     # 绕在杆上的扣
        px(d, x - 1, 16, (110, 104, 104))
        for y in range(top, top + L):                                    # 带子（2 px）
            u = (y - top) / L
            xx = int(round(x + dx * u))
            px(d, xx, y, (72, 70, 76))
            px(d, xx + 1, y, (46, 44, 50))
        ry = top + L
        rect(d, bx - 1, ry, bx + 2, ry + 1, (90, 86, 90))                # 扣环
        # 三角拉手
        d.polygon([(bx - 3, ry + 2), (bx + 4, ry + 2), (bx + 0.5, ry + 8)], outline=C((232, 222, 190)))
        d.line((bx - 3, ry + 2, bx + 4, ry + 2), fill=C((250, 244, 220)), width=2)
        px(d, bx - 2, ry + 4, (200, 190, 160))
        px(d, bx + 3, ry + 4, (170, 160, 134))
    return im


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0),
              dict(type='wrap', image=ex.img('clouds', R['clouds']), period=640, k=0.0, y=CLOUD_Y0, vx=2.0),
              ex.bake('outside', OUT_BOX, N_SW, FPS_SW, outside_frame)]
    for i, (y0, y1, vx) in enumerate(SEA_BANDS):
        layers.append(dict(type='wrap', image=ex.img('sea%d' % i, R['sea'][i]), period=SEA_P, k=0.0, y=y0, vx=vx))
    layers.append(dict(type='static', image=ex.img('cable', R['cable'][0]), x=0, y=R['cable'][1]))
    gk = ex.img('gondola', R['gondola'])
    layers.append(dict(type='clouds', span=GON_SPAN, clouds=[dict(image=gk, x0=x0, y=gondola_y(), vx=GON_VX, k=0.0)
                                                            for x0 in GON_X0S]))
    layers.append(dict(type='wrap', image=ex.img('tower', R['tower']), period=TOWER_P, k=0.0, y=TOWER_Y0, vx=32.0))
    layers.append(dict(type='static', image=ex.img('cabin', R['cabin']), x=0, y=0))
    for s in ('l', 'r'):
        box, ims = R['picks'][s]
        keys = [ex.img('win_%s%d' % (s, i), im) for i, im in enumerate(ims)]
        layers.append(dict(type='pick', images=keys, key='win_' + s, values=[0, 1], x=box[0], y=box[1], k=0.0))
    layers.append(ex.bake('straps', STRAP_BOX, N_SW, FPS_SW, straps_frame))
    anchors = dict(ANCHORS)
    anchors.update(walk_x=[X_L, X_R], walls=[[0, X_L], [X_R, W]],
                   win_l_glass=[EW_X['l'][0], EW_T, EW_X['l'][1] + 1, EW_B + 1],
                   win_r_glass=[EW_X['r'][0], EW_T, EW_X['r'][1] + 1, EW_B + 1],
                   win_l_box=list(R['picks']['l'][0]), win_r_box=list(R['picks']['r'][0]),
                   sit=dict(y=150, seat_top=SEAT_T), benches=[list(b) for b in BENCHES],
                   horizon=HZ, cable_y=CABLE_Y, floor=FLOOR)
    st = ex.stage(W, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def compose(t, sl=0, sr=0, straps=True):
    """直接拼一帧（不经导出），自检和预览用。"""
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    o = int(math.floor(t * 2.0)) % 640
    out.alpha_composite(_tile(R['clouds'], 1280).crop((o, 0, o + W, R['clouds'].height)), (0, CLOUD_Y0))
    out.alpha_composite(outside_frame(t).crop(OUT_BOX), OUT_BOX[:2])
    for i, (y0, y1, vx) in enumerate(SEA_BANDS):
        o = int(math.floor(t * vx)) % SEA_P
        out.alpha_composite(_tile(R['sea'][i], SEA_P * 2).crop((o, 0, o + W, y1 - y0)), (0, y0))
    out.alpha_composite(R['cable'][0], (0, R['cable'][1]))
    for x0 in GON_X0S:
        gx = math.floor((x0 + t * GON_VX) % GON_SPAN - 100)
        paste(out, R['gondola'], gx, gondola_y())
    o = int(math.floor(t * 32.0)) % TOWER_P
    out.alpha_composite(_tile(R['tower'], TOWER_P * 2).crop((o, 0, o + W, R['tower'].height)), (0, TOWER_Y0))
    out.alpha_composite(cabin_full(sl, sr))
    if straps:
        out.alpha_composite(straps_frame(t).crop(STRAP_BOX), STRAP_BOX[:2])
    return out


def _checks(ex, BJ, st, R):
    states = [dict(), dict(win_l=1), dict(win_r=1), dict(win_l=1, win_r=1)]
    bad = 0
    for t in (0.0, 0.75, 1.5, 3.25, 9.0, 21.0):
        for s in states:
            im = np.array(BJ.ref_render(st, ex.images, 0, t, s).convert('RGB'))
            bad += int((im.sum(-1) == 0).sum())
    ex.checked('缆车 t × 端窗四种状态 整屏都有画（没有露黑）', bad)
    ex.checked('天空底图整张不透明', int((np.array(R['sky'])[..., 3] != 255).sum()))
    # 车厢层：只有玻璃 / 天窗 / 端窗位置不是完全不透明
    a = np.array(cabin_full(0, 0))[..., 3]
    allowed = np.zeros((H, W), bool)
    for (_, x0, y0, x1, y1) in glass_rects():
        allowed[y0:y1 + 1, x0:x1 + 1] = True
    for (x0, x1) in EW_X.values():
        allowed[EW_T:EW_B + 1, x0:x1 + 1] = True
    allowed |= poly_mask((W, H), skylight_poly())
    ex.checked('车厢层只有窗户 / 天窗是透明或半透明', int(((a < 255) & ~allowed).sum()))
    ex.checked('两头端壁（x 0–39 / 280–319）和地板（y 146–179）整块不透明',
               int((a[:, :X_L] < 255).sum() + (a[:, X_R:] < 255).sum() + (a[FLOOR:, :] < 255).sum()))
    # 端窗 pick：base + pick(s) = 直接画；两张尺寸一致；只在框里不同
    for s in ('l', 'r'):
        box, ims = R['picks'][s]
        ex.checked('端窗 %s pick 两张尺寸一致' % s, 0 if ims[0].size == ims[1].size else 1)
        for v in (0, 1):
            sl = v if s == 'l' else 0
            sr = v if s == 'r' else 0
            comp = R['cabin'].copy()
            for s2, v2 in (('l', sl), ('r', sr)):
                b2, ims2 = R['picks'][s2]
                comp.alpha_composite(ims2[v2], (b2[0], b2[1]))
            want = cabin_full(sl, sr)
            ex.checked('端窗 %s=%d：base + pick 合成 = 直接画（RGBA 逐像素）' % (s, v), BJ.ndiff_rgba(comp, want))
        g0 = BJ.ref_render(st, ex.images, 0, 1.0, {})
        g1 = BJ.ref_render(st, ex.images, 0, 1.0, {'win_' + s: 1})
        dm = (np.abs(np.asarray(g0.convert('RGB'), np.int16) - np.asarray(g1.convert('RGB'), np.int16)).max(-1) > 0)
        inb = np.zeros_like(dm)
        inb[box[1]:box[3], box[0]:box[2]] = True
        ex.checked('端窗 %s 两态只在框 %s 里不同（框外差异像素）' % (s, list(box)), int((dm & ~inb).sum()),
                   extra='框内差 %d px' % int((dm & inb).sum()))
        ex.checked('端窗 %s 两态在框内确实不同' % s, 0 if int((dm & inb).sum()) > 400 else 1)
    # strip 闭合 / 宽度
    for name, box, fn in (('outside', OUT_BOX, outside_frame), ('straps', STRAP_BOX, straps_frame)):
        ex.checked('strip %s 4 s 闭合（t=0 vs t=4）' % name, BJ.ndiff_rgba(fn(0.0).crop(box), fn(N_SW / FPS_SW).crop(box)))
        ex.checked('strip %s 帧条宽 ≤ 4096' % name, 0 if (box[2] - box[0]) * N_SW <= 4096 else 1)
    # wrap 图宽 = period（首尾接得上靠图里的东西都按周期画）
    ex.checked('wrap 图宽 = period（云 640 / 海 640 / 塔 1280）',
               int(R['clouds'].width != 640) + sum(int(im.width != SEA_P) for im in R['sea']) + int(R['tower'].width != TOWER_P))
    # 锚点
    out = 0
    for k, v in ANCHORS.items():
        out += not (X_L <= v[0] <= X_R and WALK[0] <= v[1] <= WALK[1])
    ex.checked('锚点都在车厢里、可走带里（不满足的条数）', out)
    # 导出层 vs 直接拼
    for s in (dict(), dict(win_l=1, win_r=1)):
        for t in (0.0, 1.25, 2.6, 7.3, 19.0):
            got = BJ.ref_render(st, ex.images, 0, t, s)
            want = compose(t, s.get('win_l', 0), s.get('win_r', 0))
            ex.checked('缆车 %s t=%.2f 导出 vs 直接拼' % ('碎' if s else '好', t), BJ.ndiff(got, want))
    ex.note('端窗 pick 框：win_l %s / win_r %s' % (list(R['picks']['l'][0]), list(R['picks']['r'][0])))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch3', 'after')
    os.makedirs(od, exist_ok=True)
    compose(1.0).convert('RGB').resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(od, 'cable_car_solo.png'))
    compose(1.0, 1, 1).convert('RGB').resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(od, 'cable_car_solo_broken.png'))
    print('ok', SWAY)
