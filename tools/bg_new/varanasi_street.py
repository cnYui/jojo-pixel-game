# -*- coding: utf-8 -*-
r"""varanasi_street —— 第4章「贝拿勒斯（瓦拉纳西）」：老城里的窄街（gali），白天。乔瑟夫一个人逛（手臂上长着「女帝」）。
2026-10-11 ch4 按体验版精度重画（改前是 later_stages.city_street(…, 'varanasi')：一排重复的平涂楼）。
这个文件也放瓦拉纳西两张图共用的调色和建筑零件（ganges_ghat.py 在模块加载时引用这里）。

地图 640 宽、ground 154、可走带 y 148–176（人走在石板路上）；侧视平视，太阳在左上。
从左到右（世界坐标）：
  x 0–46      街口：一条往里退的横巷（看得见尽头的房子），巷口一棵大菩提树（树干绑红线），
              树下一圈石台（chabutra），台上几块抹了朱砂的小石头 + 三叉戟（anchors.arrive）
  x 46–134    B1 赭黄三层：二楼雕花木阳台（jharokha），三楼百叶窗 + 晾着的纱丽、屋顶小房间 + 电视天线；
              一层门口的石台（otla）上是水果摊：竹竿撑的麻布篷、篷下挂几串香蕉、中间一杆铜秤、
              一大筐芒果、右前方一筐红石榴（anchors.fruit）
  x 134–210   B2 粉色两层 + 屋顶房：一层绿色卷帘门（拉起一半）+ 红底招牌（天城文只用色块），二楼两扇蓝框拱窗 +
              中间一幅褪色的手绘广告（色块）；门前一个警察岗亭（奶油色木亭、蓝色“POLICE”牌、红白斜纹底、
              尖顶 + 红灯）（anchors.police）
  x 210–252   B3 天蓝窄楼：铜钉木门、墙上的神龛（象头神：朱红色块 + 花环 + 小油灯）、电表箱、二楼铁阳台 + 罗勒盆栽；
              门口趴着一头白色瘤牛（脖子上一圈万寿菊花环、额头一点朱砂，尾巴 strip 甩）
  x 252–334   B4 芥末黄三层：二楼长木阳台（格栅栏杆）、三楼三扇彩色玻璃拱窗；一层报纸摊：一摞摞报纸、
              一排挂着的杂志、正中钉着一张头版（报头 + 标题色块 + 一个看不清的人像轮廓）（anchors.newspaper）
  x 334–364   B5 白灰窄高楼（四层）：拱顶雕花木门、竖招牌（色块）、窄百叶窗
  x 364–452   B6 青绿两层：二楼一整面褪色的手绘广告（色块）；一层甜食 / 奶茶铺：泥灶上的大黑锅在炸 jalebi、
              铝壶冒热气（strip）、陶杯（kulhad）一摞摞、玻璃柜里一盘盘甜食（anchors.sweets）
  x 452–536   B7 小神庙：红白竖条纹的围墙、三级台阶、层层雕花的门框、门楣挂的万寿菊花串、大铜铃、
              门里一盏油灯和朱红色的神像；门上方一座砂岩尖塔（shikhara）+ 顶上金色宝瓶和藏红色三角旗（strip）
              （anchors.temple）
  x 536–574   B8 赭红三层：拱窗、窗台上坐着一只猴子
  x 574–640   通往河坛的门洞：砂岩门楼（尖拱、雕花横带、门顶一座小亭子 chhatri），透过拱门看得见一级级往下的石阶、
              亮晃晃的恒河（strip 波光）和对岸的沙洲；门右边墙上一块指向河坛的牌子（anchors.ghat_stairs）
街边贴着墙脚的小东西：B8 墙边一辆黑色老自行车、神庙台阶下几双拖鞋、B5 门边陶水罐、B3 门边铜水壶 + 铁桶。
头顶：两根电线杆（x 137 水泥杆 + 路灯；x 450 铁杆 + 喇叭）之间、杆子到各家屋顶乱拉的电线；
      两串彩色三角纸旗沿街垂着（strip 轻轻晃）；神庙门口 / 神龛 / 门洞的花串（strip）。
光：太阳在左上；立面亮、遮阳板 / 阳台下面有影，屋里暗；可走带后面（y 110–176）压了对比。

图层（从后往前）：
  sky       static           320×180 白天的天（偏暖的蓝、地平线发灰白）+ 左上的太阳
  clouds    wrap   k 0.1  vx 1.0   淡淡的积云（640 循环）
  far       pano   k 0.25          远景 400 宽：远处的尖塔、清真寺的两根宣礼塔、圆顶、屋顶、树、天上几只风筝（都罩了雾）
  mid       pano   k 0.55          中景 496 宽：屋顶一片（水箱、天线、晾衣绳、屋顶房）、金顶的尖塔（Kashi Vishwanath）、
                                   树冠；横巷尽头看得见的几户人家
  kites     clouds                 两只在高处盘旋的黑鸢
  pigeons   strip  k 0.55          中景屋顶上空绕圈的一群鸽子（8 帧 @4 fps）
  near      pano   k 1             整条街（640 宽）
  bunt_a/b  strip  k 1             两串三角纸旗（8 帧 @4 fps）
  garlands  strip  k 1             神龛 / 神庙门 / 门洞的花串（8 帧 @4 fps）
  flag      strip  k 1             尖塔顶的三角旗（8 帧 @4 fps）
  steam     strip  k 1             奶茶壶的热气（8 帧 @4 fps）
  cow       strip  k 1             牛甩尾巴、动耳朵（8 帧 @4 fps）
  river     strip  k 1             门洞里的河面波光（8 帧 @4 fps）
  fg: wires pano   k 1.25          镜头前面头顶的几根电线（只在画面上沿 y < 30，不挡人）
单独运行：python -B tools\bg_new\varanasi_street.py → tools\bg_new\_preview\ch4\after\varanasi_street_solo_*.png
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
PW = 640
GROUND = 154
WALK = (148, 176)
CLOUD_K, CLOUD_VX = 0.1, 1.0
FAR_K, MID_K, FG_K = 0.25, 0.55, 1.25
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 400
MIDW = W + int(math.ceil((PW - W) * MID_K))      # 496
FGW = W + int(math.ceil((PW - W) * FG_K))        # 720
LANE = 146                    # 街的后沿（墙 / 石台站在这一行上）
PL_TOP = 137                  # 门口石台（otla）顶面 137–139、立面 140–145
N_ANIM, FPS_ANIM = 8, 4.0
C = A._c4

B1 = (46, 134)
B2 = (134, 210)
B3 = (210, 252)
B4 = (252, 334)
B5 = (334, 364)
B6 = (364, 452)
B7 = (452, 536)
B8 = (536, 574)
GATE = (574, 640)
ARCH = (586, 628)             # 门洞（含两边），尖拱顶 y ARCH_TOP，起拱 ARCH_SPRING
ARCH_TOP, ARCH_SPRING = 70, 94
POLES = (137, 450)
VP = (22, 104)                # 横巷的消失点
LANE_U = 0.46                 # 横巷尽头的深度

ANCHORS = dict(
    arrive=[40, 164],          # 街口（菩提树前）
    fruit=[90, 152],           # 水果摊前（女帝偷吃）
    police=[170, 164],         # 警察岗亭前（剧情放警察）
    newspaper=[285, 152],      # 报纸摊前（头版：通缉手臂上有怪物的外国老头）
    sweets=[400, 152],         # 甜食 / 奶茶铺前
    temple=[495, 150],         # 小神庙门口（台阶下）
    ghat_stairs=[607, 152],    # 通往河坛的门洞前
    walk_x=[12, 630],
)

# ============================================================ 调色（瓦拉纳西两张共用）
INK = (46, 34, 40)
SKY_STOPS = [(66, 124, 196), (92, 150, 214), (132, 180, 228), (178, 206, 232), (222, 222, 212)]
HAZE = (214, 210, 198)
SAND_HI = (238, 210, 166)
SAND = (218, 182, 134)
SAND_S = (190, 150, 106)
SAND_D = (152, 114, 82)
SAND_K = (108, 78, 60)
OCHRE = (224, 166, 84)
PINK = (222, 152, 148)
SKYBLUE = (130, 182, 206)
MUSTARD = (214, 188, 104)
LIME = (234, 228, 212)
TEAL = (98, 162, 148)
TERRA = (192, 110, 82)
SAFFRON = (236, 128, 42)
BRICK = (166, 94, 72)
BRICK_D = (128, 68, 54)
MORTAR = (196, 162, 134)
WOOD_HI = (166, 116, 72)
WOOD = (124, 82, 52)
WOOD_D = (88, 58, 38)
WOOD_K = (60, 40, 30)
SHUT_G = (70, 126, 100)
SHUT_B = (72, 114, 156)
IRON = (52, 50, 56)
IRON_HI = (96, 94, 102)
DARK_IN = (60, 48, 50)
MARI_HI = (255, 214, 92)
MARI = (248, 166, 36)
MARI_D = (216, 108, 22)
VERMIL = (212, 62, 40)
GOLD_HI = (252, 222, 120)
GOLD = (230, 182, 72)
GOLD_D = (176, 124, 44)
LEAF_D = (34, 76, 46)
LEAF = (52, 110, 56)
LEAF_M = (82, 144, 66)
LEAF_HI = (132, 182, 84)
STONE = (192, 178, 156)       # 街面石板（偏暖的砂岩灰）
STONE_S = (180, 166, 145)
STONE_HI = (200, 188, 168)
SHADOW_MUL = np.array((0.74, 0.76, 0.86), np.float32)
SOFT_MUL = np.array((0.86, 0.87, 0.93), np.float32)
CLOTH = [(214, 52, 74), (240, 196, 56), (64, 132, 196), (238, 120, 168), (90, 168, 96), (246, 140, 40),
         (150, 80, 170), (244, 238, 224)]


# ============================================================ 小工具（照 singapore_street）
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


def mottle(im, box, base, dark, light, seed, cell=4, lo=0.3, hi=0.7, streaks=0):
    """灰泥墙的斑驳：box 里颜色正好是 base 的像素按 fbm 噪声换成 dark / light；streaks 道往下淌的水渍。"""
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
    for i in range(streaks):
        sx = int(hrange(0, w - 1, seed, i, 7))
        L = int(hrange(h * 0.15, h * 0.55, seed, i, 8))
        for yy in range(L):
            if hash01(seed, i, yy, 9) < 1.0 - yy / max(1, L) * 0.8 and (is_base[yy, sx] or (sub[yy, sx, :3] == light).all()):
                sub[yy, sx, :3] = dark
    a[y0:y1 + 1, x0:x1 + 1] = sub
    im.paste(Image.fromarray(a, 'RGBA'))


def _tile(im, w):
    out = A._new(w, im.height)
    for x in range(0, w, im.width):
        out.paste(im, (x, 0))
    return out


def _hex(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def haze(im, amt, col=HAZE):
    """空气透视：不透明像素往 col 混 amt（标量或 H×1 数组）。"""
    a = np.array(im).astype(np.float32)
    m = a[..., 3] > 0
    amt = np.asarray(amt, np.float32)
    if amt.ndim == 0:
        amt = np.full((a.shape[0], 1), float(amt), np.float32)
    hz = np.array(col, np.float32)
    a[..., :3] = np.where(m[..., None], a[..., :3] * (1 - amt[..., None]) + hz * amt[..., None], a[..., :3])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def opaque(im):
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    return Image.fromarray(a, 'RGBA')


# ============================================================ 建筑零件（两张共用）
def facade(im, x0, x1, top, base, col, seed, streaks=3, cell=5):
    """灰泥墙面：底色 + 斑驳 + 水渍；左沿亮、右沿暗（太阳在左上）。x1 不含。"""
    d = ImageDraw.Draw(im)
    rect(d, x0, top, x1 - 1, base, col)
    mottle(im, (x0, top, x1 - 1, base), col, dk(col, 0.91), lt(col, 0.12), seed, cell=cell, streaks=streaks)
    d = ImageDraw.Draw(im)
    vl(d, x0, top, base, lt(col, 0.22))
    vl(d, x1 - 1, top, base, dk(col, 0.8))
    return d


def brick_patch(im, x, y, w, h, seed):
    """灰泥掉了一块，露出里面的薄砖（lakhori）：砖 2 行一层、灰缝错开，边缘不规则，下沿一道灰泥的影。"""
    d = ImageDraw.Draw(im)
    for r in range(h):
        u = r / max(1, h - 1)
        sh = math.sin(math.pi * u)
        a = x + int(round((1 - sh) * w * 0.3 + hrange(-1, 1, seed, r, 1)))
        b = x + w - 1 - int(round((1 - sh) * w * 0.25 + hrange(-1, 1, seed, r, 2)))
        for xx in range(a, b + 1):
            c = BRICK if (r % 3) else MORTAR
            if r % 3 and (xx + (r // 3) * 3) % 7 == 0:
                c = MORTAR
            if r % 3 and hash01(seed, xx, r, 3) < 0.15:
                c = BRICK_D
            px(d, xx, y + r, c)
        if r == 0 or r == h - 1:
            continue
        px(d, b + 1, y + r, (255, 236, 210) if False else lt(MORTAR, 0.1))


def sign_board(d, x0, y0, x1, y1, bg, fg, rows=1, seed=0, border=None):
    """招牌：底色 + 边框 + 天城文的“样子”（一条横的上划线 shirorekha + 下面的小竖笔），只是色块、读不出字。"""
    rect(d, x0, y0, x1, y1, bg, outline=border or dk(bg, 0.7))
    hl(d, x0 + 1, x1 - 1, y0 + 1, lt(bg, 0.25))
    ih = (y1 - y0 - 2) / rows
    for r in range(rows):
        yy = int(y0 + 2 + r * ih + max(0, (ih - 4) / 2))
        x = x0 + 3
        k = 0
        while x < x1 - 3:
            wl = int(hrange(4, 9, seed, r, k, 1))
            wl = min(wl, x1 - 3 - x)
            if wl < 2:
                break
            hl(d, x, x + wl - 1, yy, fg)
            for xx in range(x, x + wl, 2):
                if hash01(seed, r, k, xx, 2) < 0.75:
                    px(d, xx, yy + 1, fg)
                    if hash01(seed, r, k, xx, 3) < 0.5 and yy + 2 < y1:
                        px(d, xx, yy + 2, fg)
            x += wl + 2
            k += 1


def poster(im, x, y, w, h, seed, fade=0.35):
    """褪色的招贴：底色 + 一两个色块（人像轮廓 / 圆 / 条），边角撕掉一点，颜色往墙色褪。"""
    lay = A._new(im.width, im.height)
    d = ImageDraw.Draw(lay)
    pal = [(220, 70, 60), (240, 200, 80), (70, 120, 190), (236, 236, 220), (90, 160, 100), (230, 120, 170)]
    bg = pal[int(hash01(seed, 1) * len(pal))]
    fg = pal[int(hash01(seed, 2) * len(pal))]
    if fg == bg:
        fg = (40, 40, 50)
    rect(d, x, y, x + w - 1, y + h - 1, bg)
    kind = int(hash01(seed, 3) * 3)
    if kind == 0:                                               # 人像
        cx = x + w // 2
        d.ellipse((cx - w // 5, y + 2, cx + w // 5, y + 2 + w // 2.5), fill=C(fg))
        rect(d, cx - w // 3, y + 2 + int(w // 2.5), cx + w // 3, y + h - 3, fg)
    elif kind == 1:                                             # 一个圆 + 一条
        d.ellipse((x + 1, y + 1, x + w * 0.6, y + w * 0.6), fill=C(fg))
        rect(d, x + 1, y + h - 4, x + w - 2, y + h - 3, (40, 40, 50))
    else:                                                       # 两条横带
        rect(d, x + 1, y + 2, x + w - 2, y + 3 + h // 5, fg)
        rect(d, x + 1, y + h // 2, x + w - 3, y + h // 2 + 1, (40, 40, 50))
    if hash01(seed, 4) < 0.6:                                   # 撕掉一角
        for k in range(3):
            for j in range(3 - k):
                lay.putpixel((x + w - 1 - j, y + h - 1 - k), (0, 0, 0, 0))
    a = np.array(lay).astype(np.float32)
    b = np.array(im).astype(np.float32)
    m = a[..., 3] > 0
    a[m, :3] = a[m, :3] * (1 - fade) + b[m, :3] * fade
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def chajja(im, x0, x1, y, col, depth=3):
    """遮阳板（chhajja）：上沿亮线、正面、下沿暗线，墙上落一道影（往右下错 1）。x1 含。"""
    d = ImageDraw.Draw(im)
    hl(d, x0, x1, y, lt(col, 0.3))
    for k in range(1, depth):
        hl(d, x0, x1, y + k, col if k < depth - 1 else dk(col, 0.78))
    mul_box(im, (x0 + 1, y + depth, x1, y + depth + 2), SHADOW_MUL)
    mul_box(im, (x0 + 2, y + depth + 3, x1, y + depth + 3), SHADOW_MUL, level=0.5)


def parapet(im, x0, x1, y, col, kind='plain', seed=0):
    """女儿墙：plain = 一道压顶；arch = 一排小盲拱；post = 一排小栏柱。y = 压顶上沿。x1 含。"""
    d = ImageDraw.Draw(im)
    hl(d, x0 - 1, x1 + 1, y, lt(col, 0.35))
    hl(d, x0 - 1, x1 + 1, y + 1, col)
    hl(d, x0 - 1, x1 + 1, y + 2, dk(col, 0.72))
    if kind == 'arch':
        for x in range(x0 + 2, x1 - 3, 6):
            rect(d, x, y + 5, x + 3, y + 8, dk(col, 0.72))
            hl(d, x + 1, x + 2, y + 4, dk(col, 0.72))
            px(d, x, y + 5, dk(col, 0.6))
    elif kind == 'post':
        for x in range(x0 + 1, x1, 3):
            vl(d, x, y + 4, y + 8, lt(col, 0.18))
            vl(d, x + 1, y + 4, y + 8, dk(col, 0.62))
        hl(d, x0, x1, y + 9, dk(col, 0.8))


def win_shutter(im, x, y, w, h, wall, col, state='closed', seed=0, frame=None):
    """百叶窗：窗洞（上 / 左沿暗）+ 窗套 + 窗台；closed = 两扇百叶关着；open = 推开（窗洞里暗、铁栏杆）；half = 一开一关。"""
    d = ImageDraw.Draw(im)
    fr = frame or lt(wall, 0.35)
    rect(d, x - 1, y - 2, x + w, y - 1, fr)                       # 窗套上沿 + 小檐
    hl(d, x - 2, x + w + 1, y - 3, lt(fr, 0.2))
    rect(d, x - 1, y + h, x + w, y + h, fr)                       # 窗台
    hl(d, x - 1, x + w, y + h + 1, dk(wall, 0.72))
    vl(d, x - 1, y, y + h - 1, fr)
    vl(d, x + w, y, y + h - 1, dk(fr, 0.85))
    rect(d, x, y, x + w - 1, y + h - 1, DARK_IN)
    hw = w // 2

    def leaf(a, b):
        rect(d, a, y, b, y + h - 1, col)
        for yy in range(y + 2, y + h - 1, 2):
            hl(d, a + 1, b - 1, yy, dk(col, 0.74))
        vl(d, a, y, y + h - 1, lt(col, 0.25))
        vl(d, b, y, y + h - 1, dk(col, 0.62))
        hl(d, a, b, y, lt(col, 0.2))

    def bars(a, b):
        for xx in range(a + 1, b, 2):
            vl(d, xx, y + 1, y + h - 1, IRON_HI)
        hl(d, a, b, y + h // 2, IRON_HI)
        hl(d, a, b, y, dk(DARK_IN, 0.7))
        vl(d, a, y, y + h - 1, dk(DARK_IN, 0.7))

    if state == 'closed':
        leaf(x, x + hw - 1)
        leaf(x + hw, x + w - 1)
    elif state == 'open':
        bars(x, x + w - 1)
        rect(d, x - 3, y, x - 2, y + h - 1, col)                  # 推开贴在墙上的两扇
        vl(d, x - 3, y, y + h - 1, lt(col, 0.2))
        rect(d, x + w + 1, y, x + w + 2, y + h - 1, dk(col, 0.82))
    else:
        leaf(x, x + hw - 1)
        bars(x + hw, x + w - 1)
        rect(d, x + w + 1, y, x + w + 2, y + h - 1, dk(col, 0.82))
    mul_box(im, (x + w + 1 if state == 'closed' else x + w + 3, y + 1, x + w + 1 if state == 'closed' else x + w + 3,
                 y + h), SHADOW_MUL)


def arch_mask_rows(w, rise, pointed=True):
    """宽 w 的拱：返回每一列的拱顶相对起拱线的高度（0..rise）。pointed = 尖拱（两段圆弧），否则半圆。"""
    out = []
    for i in range(w):
        u = (i + 0.5) / w * 2 - 1                                   # −1..1
        if pointed:
            v = 1 - abs(u)
            out.append(rise * (1 - (1 - v) ** 2) ** 0.5 * (0.55 + 0.45 * v) / 1.0)
        else:
            out.append(rise * max(0.0, 1 - u * u) ** 0.5)
    return out


def win_arch(im, x, y, w, h, wall, frame, glass=True, seed=0, shut=None):
    """拱窗：半圆拱顶（彩色玻璃扇形气窗）+ 下半截百叶 / 铁栏；窗套一圈 frame 色，拱心一块亮石。"""
    d = ImageDraw.Draw(im)
    r = w // 2
    rows = arch_mask_rows(w, r, pointed=False)
    for i in range(w):
        top = y + r - int(round(rows[i]))
        vl(d, x + i, top - 1, top - 1, frame)
        vl(d, x + i, top, y + r, DARK_IN)
        if glass and top < y + r:
            for yy in range(top, y + r):
                ang = math.atan2(y + r - yy, (x + i + 0.5) - (x + w / 2))
                k = int((ang / math.pi) * 5)
                c = ((214, 64, 60), (240, 196, 70), (70, 140, 200), (90, 170, 110), (230, 120, 60))[k % 5]
                if (yy - top) == 0 or i in (0, w - 1):
                    c = frame
                px(d, x + i, yy, dk(c, 0.82) if (x + i + yy) % 2 else c)
    hl(d, x, x + w - 1, y + r, frame)
    rect(d, x + w // 2 - 1, y - 2, x + w // 2, y - 1, lt(frame, 0.3))     # 拱心石
    win_shutter(im, x, y + r + 1, w, h - r - 1, wall, shut or SHUT_B, state='half' if seed % 2 else 'open',
                frame=frame)


def jharokha(im, x, y, w, h, wood=WOOD, seed=0):
    """雕花木阳台（jharokha）：顶上一道弯的小檐、一排小柱子之间是格栅（jaali）、下面挑出的一排托架；墙上落影。
    (x, y) = 左上；w × h = 檐口到底板；托架往下再伸 5 行。"""
    cast_shadow(im, [(x + 2, y + h), (x + w + 2, y + h), (x + w + 4, y + h + 9), (x + 4, y + h + 9)])
    cast_shadow(im, [(x + w, y + 3), (x + w + 3, y + 5), (x + w + 3, y + h + 4), (x + w, y + h)])
    d = ImageDraw.Draw(im)
    hi, md, dkk, k = WOOD_HI, wood, dk(wood, 0.72), dk(wood, 0.5)
    # 小檐：中间拱起（bangaldar），两头翘
    for i in range(-2, w + 2):
        u = (i + 2) / (w + 3)
        bump = int(round(2.2 * math.sin(math.pi * u)))
        vl(d, x + i, y + 2 - bump, y + 3, md)
        px(d, x + i, y + 1 - bump, hi)
        px(d, x + i, y + 4, k)
    px(d, x - 3, y + 1, md)
    px(d, x + w + 2, y + 1, md)
    # 身子：柱子 + 格栅
    body0, body1 = y + 5, y + h - 4
    rect(d, x, body0, x + w - 1, body1, dkk)
    n = max(2, int(round(w / 7)))
    step = (w - 2) / n
    for j in range(n + 1):
        cx = x + int(round(j * step))
        vl(d, cx, body0, body1, hi)
        vl(d, cx + 1, body0, body1, md)
    for j in range(n):
        a = x + int(round(j * step)) + 2
        b = x + int(round((j + 1) * step)) - 1
        for yy in range(body0, body1 + 1):
            for xx in range(a, b + 1):
                rel = yy - body0
                if rel < 3:                                        # 小尖拱
                    mid = (a + b) / 2
                    if abs(xx - mid) > rel + 0.5:
                        continue
                c = DARK_IN if (xx + yy) % 2 else md
                if rel >= 3 and (yy - body0) % 4 == 3:
                    c = md
                px(d, xx, yy, c)
    # 底板 + 托架
    hl(d, x - 1, x + w, body1 + 1, hi)
    rect(d, x - 1, body1 + 2, x + w, body1 + 3, md)
    hl(d, x - 1, x + w, body1 + 4, k)
    nb = max(2, w // 9)
    for j in range(nb + 1):
        bx = x + int(round(j * (w - 3) / nb))
        for r in range(5):
            hl(d, bx + r // 2, bx + 2 - r // 2 + (1 if r < 2 else 0), body1 + 5 + r, md if r < 3 else dkk)
        px(d, bx, body1 + 5, hi)


def door_carved(im, x, y, w, h, wood=WOOD, frame=SAND_S, studs=True, arch=False):
    """老木门：砂岩门框（两道线脚）+ 两扇木门（竖板、铜钉、门环），门楣上一个小龛；arch = 门顶半圆。"""
    d = ImageDraw.Draw(im)
    rect(d, x - 3, y - 4, x + w + 2, y + h - 1, frame)
    vl(d, x - 3, y - 4, y + h - 1, lt(frame, 0.3))
    hl(d, x - 3, x + w + 2, y - 4, lt(frame, 0.3))
    vl(d, x + w + 2, y - 4, y + h - 1, dk(frame, 0.75))
    rect(d, x - 1, y - 2, x + w, y + h - 1, dk(frame, 0.85))
    rect(d, x, y, x + w - 1, y + h - 1, wood)
    if arch:
        r = w // 2
        rows = arch_mask_rows(w, r, pointed=False)
        for i in range(w):
            top = y + r - int(round(rows[i]))
            vl(d, x + i, y - 2, top - 1, dk(frame, 0.85) if top - 1 >= y - 2 else frame)
    hw = w // 2
    for xx in range(x, x + w):
        if (xx - x) % 3 == 2:
            vl(d, xx, y + 1, y + h - 1, dk(wood, 0.8))
    vl(d, x + hw - 1, y, y + h - 1, dk(wood, 0.55))
    vl(d, x + hw, y, y + h - 1, lt(wood, 0.15))
    vl(d, x, y, y + h - 1, dk(wood, 0.6))
    if studs:
        for yy in range(y + 4, y + h - 2, 5):
            for xx in (x + 2, x + hw - 3, x + hw + 2, x + w - 3):
                px(d, xx, yy, GOLD)
    for xx in (x + hw - 3, x + hw + 2):                         # 门环
        px(d, xx, y + h // 2, GOLD_D)
        px(d, xx, y + h // 2 + 1, GOLD)
    hl(d, x, x + w - 1, y + h - 1, dk(wood, 0.6))


def shikhara(im, cx, base_y, top_y, half_w, pal=None, minis=True, gold=False, flagpole=True):
    """北印度曲线尖塔：外轮廓从底往上收成弧形，横着一层层的棱（bhumi，每 3 行）；正中一条凸出来的中脊（ratha）；
    顶上扁圆带棱的 amalaka + 宝瓶（kalasha）+ 旗杆。左亮右暗。minis = 底部两边各贴一座小一号的（urushringa）。
    pal = (亮, 中, 暗, 深)；gold = 整座贴金（中景的金顶寺）。返回旗杆顶 (x, y)。"""
    pal = pal or ((GOLD_HI, GOLD, GOLD_D, (130, 88, 34)) if gold else (SAND_HI, SAND, SAND_S, SAND_K))
    d = ImageDraw.Draw(im)
    hgt = base_y - top_y
    if minis and half_w >= 8:
        for sgn in (-1, 1):
            shikhara(im, cx + sgn * int(half_w * 0.62), base_y, base_y - int(hgt * 0.5), int(half_w * 0.42), pal,
                     minis=False, flagpole=False)
        d = ImageDraw.Draw(im)

    def hw_at(y):
        u = (base_y - y) / max(1, hgt)
        return max(1.0, half_w * (1 - u ** 1.7) ** 0.6)

    for y in range(top_y, base_y + 1):
        hw = hw_at(y)
        x0, x1 = int(round(cx - hw)), int(round(cx + hw))
        ridge = (base_y - y) % 3 == 0
        for x in range(x0, x1 + 1):
            v = (x - cx) / max(1.0, hw)
            if v < -0.5:
                c = pal[0]
            elif v < 0.3:
                c = pal[1]
            else:
                c = pal[2]
            if abs(v) < 0.22:                                       # 中脊：亮一点、棱错半格
                c = pal[0] if v < 0.05 else pal[1]
                if (base_y - y) % 3 == 1:
                    c = pal[2]
            elif ridge:
                c = pal[2] if v < 0.3 else pal[3]
            px(d, x, y, c)
        px(d, x0, y, pal[0] if (base_y - y) % 3 else pal[1])
        px(d, x1, y, pal[3])
    # amalaka（扁圆、带竖棱）+ 宝瓶 + 旗杆
    aw = max(2, int(round(hw_at(top_y) + 2)))
    ay = top_y - 2
    for xx in range(cx - aw, cx + aw + 1):
        c = (pal[0] if xx < cx else pal[2]) if (xx - cx) % 2 else pal[1]
        vl(d, xx, ay, ay + 2, c)
    hl(d, cx - aw + 1, cx + aw - 1, ay - 1, pal[1])
    hl(d, cx - aw + 1, cx + aw - 1, ay + 2, pal[3])
    gx, gy = cx, ay - 2
    vl(d, gx, gy - 2, gy, GOLD)
    px(d, gx - 1, gy, GOLD_D)
    px(d, gx + 1, gy, GOLD_D)
    px(d, gx - 1, gy - 1, GOLD)
    px(d, gx + 1, gy - 1, GOLD_D)
    px(d, gx, gy - 3, GOLD_HI)
    if flagpole:
        vl(d, gx, gy - 10, gy - 4, (92, 70, 50))
        return (gx, gy - 10)
    return (gx, gy - 3)


def chhatri(im, cx, base_y, w, h, pal=None, dome=None):
    """小亭子（chhatri）：台基、两根看得见的柱子 + 中间的拱、一道挑檐、半球形的顶（带棱）+ 尖顶。
    w = 檐宽，h = 台基到檐口的高度；顶另外高 w*0.45。"""
    pal = pal or (SAND_HI, SAND, SAND_S, SAND_K)
    dome = dome or pal
    d = ImageDraw.Draw(im)
    x0, x1 = cx - w // 2, cx + w // 2
    hl(d, x0 + 1, x1 - 1, base_y, pal[2])                        # 台基
    hl(d, x0 + 1, x1 - 1, base_y - 1, pal[0])
    cy0 = base_y - 1 - h
    for (a, b) in ((x0 + 2, x0 + 3), (x1 - 3, x1 - 2), (cx - 1, cx)):
        rect(d, a, cy0 + 2, b, base_y - 2, pal[1])
        vl(d, a, cy0 + 2, base_y - 2, pal[0])
        vl(d, b, cy0 + 2, base_y - 2, pal[2])
    for (a, b) in ((x0 + 4, cx - 2), (cx + 1, x1 - 4)):           # 柱间：暗（能看穿到后面的影）
        if b >= a:
            rect(d, a, cy0 + 3, b, base_y - 2, dk(pal[2], 0.62))
            hl(d, a, b, cy0 + 2, pal[1])
            px(d, a, cy0 + 3, pal[1])
            px(d, b, cy0 + 3, pal[1])
    hl(d, x0, x1, cy0, pal[0])                                    # 挑檐
    hl(d, x0, x1, cy0 + 1, pal[2])
    px(d, x0 - 1, cy0 - 1, pal[1])
    px(d, x1 + 1, cy0 - 1, pal[1])
    r = max(2, (w - 2) // 2)
    dh = max(2, int(r * 0.9))
    for xx in range(cx - r, cx + r + 1):
        u = (xx - cx) / r
        top = cy0 - 1 - int(round(dh * max(0.0, 1 - u * u) ** 0.5))
        for yy in range(top, cy0):
            c = dome[0] if u < -0.35 else (dome[1] if u < 0.3 else dome[2])
            if (xx - cx) % 3 == 0 and yy > top:
                c = dome[2] if u < 0.3 else dome[3]
            px(d, xx, yy, c)
    tip = cy0 - 1 - dh
    vl(d, cx, tip - 3, tip - 1, GOLD)
    px(d, cx, tip - 4, GOLD_HI)
    return tip - 4


def garland_pts(x0, y0, x1, y1, sag):
    n = max(2, int(abs(x1 - x0)))
    pts = []
    for i in range(n + 1):
        u = i / n
        pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + sag * 4 * u * (1 - u)))
    return pts


def draw_garland(d, x0, y0, x1, y1, sag, dx=0.0, seed=0, thick=True):
    """万寿菊花串：沿一条下垂的弧，每个点一朵（橙 / 黄 / 深橙交替），thick 时下面再一排。dx = 中间往右摆多少。"""
    for i, (x, y) in enumerate(garland_pts(x0, y0, x1, y1, sag)):
        u = i / max(1, abs(x1 - x0))
        xx = round(x + dx * 4 * u * (1 - u))
        yy = round(y)
        c = (MARI, MARI_HI, MARI_D, MARI)[(i + seed) % 4]
        px(d, xx, yy, c)
        if thick:
            px(d, xx, yy + 1, MARI_D if i % 2 else MARI)


def hang_garland(d, x, y, L, dx=0.0, seed=0):
    """一条垂下来的花串（长 L）：底下一朵大的 + 一撮叶子。dx = 底端往右摆多少（−1..1）。"""
    for k in range(L):
        u = k / max(1, L - 1)
        xx = x + round(dx * u * u * 2)
        c = (MARI, MARI_HI, MARI_D)[(k + seed) % 3]
        px(d, xx, y + k, c)
    xb = x + round(dx * 2)
    px(d, xb - 1, y + L, MARI_D)
    px(d, xb, y + L, MARI)
    px(d, xb + 1, y + L, MARI_D)
    px(d, xb, y + L + 1, LEAF_M)


def wire(d, x0, y0, x1, y1, sag, col=(44, 40, 44), step=1):
    pts = garland_pts(x0, y0, x1, y1, sag)
    d.line([(round(x), round(y)) for (x, y) in pts[::step]], fill=C(col))


def kite_bird_img():
    """黑鸢（滑翔）：一字形的翅膀 + 叉尾。"""
    g = A._new(9, 4)
    d = ImageDraw.Draw(g)
    c = (64, 54, 54)
    for (x, y) in ((0, 1), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, 0), (7, 0), (8, 1)):
        px(d, x, y, c)
    px(d, 4, 2, c)
    px(d, 4, 3, dk(c, 0.8))
    return g


def paper_kite(d, x, y, col, tail=6, lean=1):
    """纸风筝（patang）：菱形 + 中间一条竖骨 + 往下飘的尾巴 + 一根往下拉的线（淡）。"""
    for dy in range(-2, 3):
        hw = 2 - abs(dy)
        hl(d, x - hw, x + hw, y + dy, col)
    px(d, x, y - 2, lt(col, 0.4))
    vl(d, x, y - 1, y + 1, dk(col, 0.7))
    for k in range(tail):
        px(d, x + (k // 2) * lean * (1 if k % 4 < 2 else 0), y + 3 + k, dk(col, 0.85))


# ---------------------------------------------------------------- 牛（趴着的白色瘤牛，朝左）
COW_W1, COW_W2, COW_W3, COW_W4, COW_OL = (250, 246, 236), (232, 226, 214), (206, 198, 184), (172, 162, 150), \
    (118, 104, 96)


@lru_cache(maxsize=1)
def cow_img():
    """42×20：头朝左下（短角、往后垂的耳朵、深色嘴鼻、额头一点朱砂）、脖子下的垂皮、肩上的瘤峰、凸出来的胯骨、
    前腿跪着膝盖往前、后腿收在肚子下；脖子上一圈万寿菊花环。光从左上：上沿亮、下半截暗、下 / 右沿描深色边。
    尾巴不画（在 strip 里甩）。"""
    w, h = 42, 20
    m = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(m)
    md.ellipse((13, 5, 41, 20), fill=255)
    md.polygon([(12, 8), (13, 3), (16, 1), (19, 1), (22, 4), (24, 7), (18, 10)], fill=255)
    md.ellipse((30, 4, 40, 13), fill=255)
    md.polygon([(8, 4), (13, 3), (17, 8), (16, 16), (11, 15)], fill=255)
    md.polygon([(8, 9), (13, 10), (13, 16), (10, 14)], fill=255)
    md.polygon([(5, 2), (8, 2), (10, 4), (9, 8), (6, 12), (4, 14), (1, 14), (0, 12), (2, 8), (3, 4)], fill=255)
    md.polygon([(13, 14), (17, 15), (15, 19), (7, 19), (7, 17), (11, 17)], fill=255)
    md.polygon([(31, 13), (36, 12), (39, 19), (30, 19)], fill=255)
    a = np.array(m) > 0
    out = np.zeros((h, w, 4), np.uint8)
    ys = np.arange(h)[:, None].repeat(w, 1)
    out[a, :3] = COW_W2
    out[a & (ys > h * 0.72), :3] = COW_W3
    out[a & (ys > h * 0.86), :3] = COW_W4
    out[a, 3] = 255
    up = np.zeros_like(a)
    up[1:, :] = a[:-1, :]
    out[a & ~up, :3] = COW_W1
    dn = np.zeros_like(a)
    dn[:-1, :] = a[1:, :]
    rt = np.zeros_like(a)
    rt[:, :-1] = a[:, 1:]
    edge = a & (~dn | ~rt) & (ys > 6)
    out[edge & (ys > 14), :3] = COW_OL
    out[edge & (ys <= 14), :3] = COW_W4
    im = Image.fromarray(out, 'RGBA')
    d = ImageDraw.Draw(im)
    for (x, y) in ((5, 1), (5, 0), (8, 1)):                           # 角
        px(d, x, y, (196, 184, 156))
    px(d, 9, 0, (90, 80, 72))
    px(d, 6, 0, (90, 80, 72))
    for (x, y) in ((9, 4), (10, 5), (11, 6), (12, 7)):                # 耳朵
        px(d, x, y, COW_W2)
        px(d, x, y + 1, (190, 160, 150))
    px(d, 12, 8, COW_W4)
    px(d, 13, 8, COW_W4)
    for (x, y) in ((6, 9), (5, 10), (5, 11), (4, 12)):                # 右下颊
        px(d, x, y, COW_W3)
    px(d, 4, 6, (30, 24, 24))                                         # 眼
    px(d, 5, 6, (30, 24, 24))
    px(d, 4, 5, (110, 96, 90))
    px(d, 6, 3, VERMIL)                                               # 朱砂
    for (x, y) in ((0, 12), (1, 12), (0, 13), (1, 13), (2, 13), (3, 14), (2, 14)):   # 嘴鼻
        px(d, x, y, (96, 88, 86))
    px(d, 1, 12, (60, 54, 54))
    px(d, 2, 12, (140, 128, 122))
    for k, (x, y) in enumerate(((9, 8), (10, 9), (11, 10), (12, 11), (13, 11), (14, 10), (15, 9))):   # 花环
        px(d, x, y, MARI if k % 2 else MARI_HI)
        px(d, x, y + 1, MARI_D)
    px(d, 7, 18, (70, 60, 56))                                        # 蹄子
    px(d, 8, 18, (70, 60, 56))
    px(d, 37, 18, (70, 60, 56))
    px(d, 33, 5, COW_W1)                                              # 胯骨亮点
    px(d, 34, 5, COW_W1)
    for x in (22, 25, 28):                                            # 肋骨
        px(d, x, 11, COW_W3)
        px(d, x + 1, 12, COW_W3)
    for (x, y) in ((31, 14), (32, 15), (33, 16)):                     # 后腿折线
        px(d, x, y, COW_W3)
    return im


def cow_tail(d, x, y, f, n=N_ANIM):
    """牛尾巴：从屁股往右下垂到地上、末端一撮黑毛；f 帧：慢慢左右甩。"""
    ph = math.tau * f / n
    sw = math.sin(ph)
    L = 10
    for k in range(L):
        u = k / (L - 1)
        xx = x + round(u * 2 + sw * 3 * u * u)
        yy = y + k
        px(d, xx, yy, COW_W3 if k < L - 3 else (60, 52, 50))
        if k < 3:
            px(d, xx - 1, yy, COW_W2)
    px(d, x + round(2 + sw * 3) + 1, y + L - 1, (60, 52, 50))
    px(d, x + round(2 + sw * 3) - 1, y + L - 1, (60, 52, 50))


# ============================================================ 天空 / 云
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), SKY_STOPS, bands=12)
    A._glow(im, 46, 22, 44, 36, (255, 244, 214), 70, rings=5)
    d = ImageDraw.Draw(im)
    d.ellipse((40, 16, 52, 28), fill=C((255, 246, 220)))
    d.ellipse((42, 18, 50, 26), fill=C((255, 254, 244)))
    return im


@lru_cache(maxsize=1)
def clouds_img():
    """640 循环：淡淡的积云（底平、偏暖），只在天的上半截。"""
    im = A._new(640, 80)
    pal = ((255, 255, 252), (240, 240, 238), (216, 220, 228), (196, 202, 216))
    for i in range(5):
        w = hrange(50, 92, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.32, 0.46, i, 2), 400 + i, pal)
        cx = (i + hrange(0.1, 0.9, i, 3)) * 640 / 5
        y = 80 - cl.height - int(hrange(0, 22, i, 4))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    for i in range(6):
        w = hrange(14, 34, i, 11)
        cl = A._cloud_sprite(w, w * 0.32, 500 + i, pal)
        cx = (i + hrange(0.1, 0.9, i, 12)) * 640 / 6
        y = int(hrange(2, 30, i, 13))
        for dx in (-640, 0, 640):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    return im


KITES = [(30, -4.0, 0.3, 60), (44, -2.6, 0.22, 260)]          # (y, vx, k, x0)：两只黑鸢


# ============================================================ 远景（k 0.25，400 宽）
def far_block(d, x, w, top, base, col, seed):
    rect(d, x, top, x + w - 1, base, col)
    vl(d, x, top, base, lt(col, 0.18))
    rect(d, x + w - 2, top, x + w - 1, base, dk(col, 0.82))
    hl(d, x - 1, x + w, top, lt(col, 0.25))
    for yy in range(top + 4, base - 2, 6):
        for xx in range(x + 2, x + w - 3, 4):
            if hash01(seed, xx, yy) < 0.7:
                px(d, xx, yy, dk(col, 0.62))
                px(d, xx, yy + 1, dk(col, 0.62))


@lru_cache(maxsize=1)
def far_img():
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    pal_walls = [(214, 190, 160), (230, 214, 190), (204, 170, 140), (222, 200, 176), (196, 180, 170)]
    # 一层远处的屋顶（矮的、连成一片）
    x = 0
    i = 0
    while x < FARW:
        w = int(hrange(10, 24, i, 1))
        top = int(hrange(70, 86, i, 2))
        far_block(d, x, w, top, 140, pal_walls[i % 5], i)
        x += w
        i += 1
    # 尖塔（三座）、清真寺宣礼塔（两根）+ 圆顶、水塔
    for (cx, base, top, hw) in ((58, 86, 44, 9), (188, 84, 52, 7), (338, 86, 40, 10)):
        shikhara(im, cx, base, top, hw, pal=((236, 214, 186), (220, 196, 166), (196, 170, 144), (170, 146, 126)),
                 minis=True)
    d = ImageDraw.Draw(im)
    mx = 262
    for tx in (mx - 14, mx + 14):                                     # 宣礼塔
        rect(d, tx - 1, 24, tx + 1, 84, (236, 230, 216))
        vl(d, tx + 1, 24, 84, (206, 198, 186))
        for yy in (40, 58):
            hl(d, tx - 2, tx + 2, yy, (210, 202, 190))
        d.ellipse((tx - 2, 19, tx + 2, 25), fill=C((236, 230, 216)))
        vl(d, tx, 16, 18, (200, 170, 90))
    d.ellipse((mx - 10, 60, mx + 10, 78), fill=C((240, 236, 226)))  # 圆顶
    d.chord((mx - 10, 60, mx + 10, 78), 300, 60, fill=C((214, 208, 198)))
    vl(d, mx, 55, 59, (200, 170, 90))
    rect(d, mx - 13, 70, mx + 13, 86, (226, 218, 204))
    for xx in range(mx - 11, mx + 12, 4):
        rect(d, xx, 74, xx + 1, 80, (196, 186, 172))
    d.ellipse((120, 64, 134, 76), fill=C((228, 222, 212)))            # 一个白圆顶
    rect(d, 118, 72, 136, 86, (222, 208, 186))
    rect(d, 304, 56, 310, 62, (200, 194, 186))                        # 水塔
    vl(d, 305, 63, 84, (186, 180, 172))
    vl(d, 309, 63, 84, (186, 180, 172))
    # 远处的树冠
    for (tx, ty, rx, ry, sd) in ((96, 76, 12, 7, 1), (226, 78, 10, 6, 2), (372, 74, 14, 8, 3), (16, 78, 9, 6, 4)):
        _canopy(d, tx, ty, rx, ry, 300 + sd, pal=((92, 120, 92), (112, 140, 104), (136, 160, 118), (160, 180, 132)))
    # 天上的纸风筝（男孩们在屋顶放的）
    for (kx, ky, col) in ((84, 30, (226, 70, 80)), (176, 20, (250, 210, 70)), (318, 36, (90, 170, 220))):
        paper_kite(d, kx, ky, col, tail=5)
        for k in range(1, 26):
            if k % 2 == 0:
                px(d, kx + k // 3, ky + 2 + k, (150, 150, 160))
    ys = np.arange(H, dtype=np.float32)[:, None]
    amt = np.clip(0.45 + (ys - 20) / 120 * 0.2, 0.45, 0.62)
    return haze(im, amt)


def _canopy(d, cx, cy, rx, ry, seed, pal=(LEAF_D, LEAF, LEAF_M, LEAF_HI)):
    """树冠：一堆椭圆疙瘩，左上亮、右下暗、底下一圈深色（照 singapore_street）。"""
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


# ============================================================ 中景（k 0.55，496 宽）：屋顶一片 + 金顶寺
def tv_antenna(d, x, y, h, col=(70, 70, 78)):
    """80 年代的电视天线（鱼骨形）：一根竖杆 + 顶上一根横杆、一排短横。"""
    vl(d, x, y, y + h, col)
    hl(d, x - 6, x + 6, y, col)
    for k in range(-5, 6, 2):
        vl(d, x + k, y - 1, y + 1, col)
    hl(d, x - 3, x + 3, y + 4, col)


def water_tank(d, x, y, w, h, col=(200, 196, 188)):
    rect(d, x, y, x + w - 1, y + h - 1, col)
    hl(d, x, x + w - 1, y, lt(col, 0.3))
    vl(d, x + w - 1, y, y + h - 1, dk(col, 0.75))
    hl(d, x, x + w - 1, y + h, dk(col, 0.6))
    for k in range(1, w - 1, 3):
        px(d, x + k, y + h - 2, dk(col, 0.85))


def roof_house(im, x, w, top, base, col, seed, rails=True):
    """中景的一栋房子（只看得见上面几层）：墙、窗洞、女儿墙；屋顶上随机放水箱 / 天线 / 屋顶房 / 晾衣绳 / 盆栽。"""
    d = facade(im, x, x + w, top, base, col, seed, streaks=1, cell=4)
    for yy in range(top + 8, base - 8, 14):
        for xx in range(x + 3, x + w - 5, 8):
            if hash01(seed, xx, yy, 1) < 0.78:
                rect(d, xx, yy, xx + 3, yy + 6, dk(col, 0.5))
                hl(d, xx, xx + 3, yy, dk(col, 0.38))
                hl(d, xx - 1, xx + 4, yy + 7, lt(col, 0.25))
                if hash01(seed, xx, yy, 2) < 0.4:
                    rect(d, xx, yy, xx + 1, yy + 6, (SHUT_G, SHUT_B, WOOD)[int(hash01(seed, xx, 3) * 3)])
    parapet(im, x, x + w - 1, top - 1, col, 'post' if rails and hash01(seed, 4) < 0.4 else 'plain')
    d = ImageDraw.Draw(im)
    r = hash01(seed, 5)
    if r < 0.35:
        water_tank(d, x + int(hrange(2, w - 12, seed, 6)), top - 8, 9, 7)
    elif r < 0.6:
        rx = x + int(hrange(1, max(2, w - 16), seed, 7))
        rect(d, rx, top - 10, rx + 13, top - 2, lt(col, 0.15))
        rect(d, rx + 3, top - 7, rx + 6, top - 2, dk(col, 0.45))
        hl(d, rx - 1, rx + 14, top - 11, dk(col, 0.7))
    if hash01(seed, 8) < 0.55:
        tv_antenna(d, x + int(hrange(3, w - 4, seed, 9)), top - int(hrange(14, 22, seed, 10)), 12)
    if hash01(seed, 11) < 0.45 and w > 20:                              # 晾衣绳
        y0 = top - 5
        a, b = x + 3, x + w - 4
        wire(d, a, y0, b, y0, 1, (90, 86, 90))
        for k in range(a + 2, b - 2, 4):
            if hash01(seed, k, 12) < 0.7:
                c = CLOTH[int(hash01(seed, k, 13) * len(CLOTH))]
                rect(d, k, y0 + 1, k + 2, y0 + 4 + int(hash01(seed, k, 14) * 3), c)


@lru_cache(maxsize=1)
def mid_img():
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    pal = [(226, 186, 128), (220, 170, 160), (180, 204, 214), (236, 230, 214), (210, 196, 120), (200, 140, 112),
           (164, 196, 170)]
    # 后排（高一点、淡一点）
    x, i = 0, 0
    while x < MIDW:
        w = int(hrange(22, 40, i, 21))
        top = int(hrange(28, 50, i, 22))
        roof_house(im, x, w, top, 140, pal[(i * 3) % len(pal)], 50 + i)
        x += w
        i += 1
    # 金顶寺（Kashi Vishwanath）：两座贴金的尖塔 + 一个金圆顶，下面白色的寺墙
    gx = 262
    d = ImageDraw.Draw(im)
    rect(d, gx - 26, 54, gx + 30, 140, (238, 232, 218))
    for xx in range(gx - 24, gx + 29, 6):
        vl(d, xx, 60, 140, (214, 206, 192))
    hl(d, gx - 27, gx + 31, 54, (250, 246, 236))
    shikhara(im, gx, 56, 8, 13, gold=True, minis=True)
    shikhara(im, gx + 20, 56, 30, 6, gold=True, minis=False, flagpole=False)
    d = ImageDraw.Draw(im)
    d.ellipse((gx - 24, 40, gx - 10, 56), fill=C(GOLD))
    d.chord((gx - 24, 40, gx - 10, 56), 270, 90, fill=C(GOLD_D))
    d.chord((gx - 24, 40, gx - 10, 56), 200, 250, fill=C(GOLD_HI))
    vl(d, gx - 17, 35, 39, GOLD_HI)
    # 前排（矮、颜色实一点）
    x, i = 6, 0
    while x < MIDW:
        w = int(hrange(20, 34, i, 31))
        top = int(hrange(52, 70, i, 32))
        if abs(x + w / 2 - gx) < 34:
            x += w
            i += 1
            continue
        roof_house(im, x, w, top, 140, pal[(i * 5 + 2) % len(pal)], 80 + i)
        x += w + int(hrange(0, 6, i, 33))
        i += 1
    d = ImageDraw.Draw(im)
    # 树冠（楝树 / 菩提）
    for (tx, ty, rx, ry, sd) in ((128, 52, 18, 12, 1), (370, 56, 16, 11, 2), (452, 48, 20, 13, 3)):
        vl(d, tx, ty + 6, 140, (96, 80, 66))
        _canopy(d, tx, ty, rx, ry, 600 + sd, pal=((56, 96, 60), (76, 124, 70), (104, 150, 84), (148, 184, 104)))
    # 横巷尽头那几户（近景横巷开口里看得见：mid x 0–70，地面 y 128）
    for (hx, hw2, col) in ((0, 22, (224, 196, 150)), (22, 26, (200, 160, 170)), (48, 24, (176, 196, 200))):
        dd = facade(im, hx, hx + hw2, 74, 128, col, 900 + hx, streaks=1, cell=3)
        door_carved(im, hx + hw2 // 2 - 4, 110, 8, 18, wood=WOOD, frame=dk(col, 0.86), studs=False)
        dd = ImageDraw.Draw(im)
        win_shutter(im, hx + 4, 86, 6, 9, col, SHUT_G if hx % 2 else SHUT_B, 'closed')
        win_shutter(im, hx + hw2 - 10, 86, 6, 9, col, SHUT_B, 'open')
        chajja(im, hx, hx + hw2 - 1, 104, lt(col, 0.1), depth=2)
        dd = ImageDraw.Draw(im)
        parapet(im, hx, hx + hw2 - 1, 72, col)
    d = ImageDraw.Draw(im)
    rect(d, 0, 129, 72, 140, (176, 164, 148))
    hl(d, 0, 72, 129, (150, 140, 126))
    return haze(im, 0.2)


# 鸽子群（中景上空绕圈，strip，中景坐标）
PIGEON_BOX = (150, 2, 250, 44)
PIGEON_C = (200, 22)          # 绕圈的中心（中景坐标）


def pigeons_frame(t):
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    cx, cy = PIGEON_C
    for i in range(9):
        ph = math.tau * (f / N_ANIM + i / 9.0 * 0.55 + hash01(i, 71) * 0.06)
        rx = 40 + 6 * hash01(i, 72)
        ry = 13 + 4 * hash01(i, 73)
        x = round(cx + rx * math.cos(ph))
        y = round(cy + ry * math.sin(ph) + 2 * hash01(i, 74))
        up = (f + i) % 2 == 0
        col = (88, 90, 102) if math.sin(ph) > 0 else (120, 122, 134)
        px(d, x, y, col)
        if up:
            px(d, x - 1, y - 1, col)
            px(d, x + 1, y - 1, col)
        else:
            px(d, x - 1, y, col)
            px(d, x + 1, y, col)
    return im


# ============================================================ 近景：地面
def draw_ground(im):
    """石板街（146–179）：后沿一道排水沟盖板，石板一行行错缝，明暗差 ±3 %；花瓣、落叶、几处湿印子。都压得很淡。"""
    d = ImageDraw.Draw(im)
    rect(d, 0, LANE, PW - 1, H - 1, STONE)
    mottle(im, (0, LANE + 2, PW - 1, H - 1), STONE, STONE_S, STONE_HI, 41, cell=6, lo=0.22, hi=0.8)
    d = ImageDraw.Draw(im)
    hl(d, 0, PW - 1, LANE, dk(STONE, 0.72))                     # 墙脚的排水沟（盖着长条石板）
    hl(d, 0, PW - 1, LANE + 1, dk(STONE, 0.86))
    for x in range(0, PW, 11):
        px(d, x, LANE + 1, dk(STONE, 0.7))
    bands = [(LANE + 2, 155), (155, 163), (163, 171), (171, H)]
    for bi, (ya, yb) in enumerate(bands):
        if bi:
            for x in range(0, PW, 2):
                px(d, x, ya, STONE_S)
            for x in range(1, PW, 2):
                px(d, x, ya, mix(STONE, STONE_S, 0.5))
        step = 20 + bi * 5
        off = (bi * 13) % step
        for x in range(off, PW, step):
            vl(d, x, ya + 1, yb - 1, mix(STONE, STONE_S, 0.75))
    a = np.array(im).astype(np.float32)
    for bi, (ya, yb) in enumerate(bands):
        step = 20 + bi * 5
        off = (bi * 13) % step
        xs = [0] + list(range(off, PW, step)) + [PW]
        for xa, xb in zip(xs, xs[1:]):
            f = hrange(0.97, 1.03, bi, xa, 43)
            a[ya + 1:yb, xa + 1:xb, :3] *= f
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))
    d = ImageDraw.Draw(im)
    for i in range(40):                                           # 细裂缝 / 磨亮的地方
        x, y = int(hrange(0, PW, i, 44)), int(hrange(149, 178, i, 45))
        for k in range(int(hrange(2, 6, i, 46))):
            px(d, x, y, mix(STONE, STONE_S, 0.9))
            x += 1
            y += (1 if hash01(i, k, 47) < 0.3 else (-1 if hash01(i, k, 47) > 0.8 else 0))
            y = max(149, min(178, y))
    for (xa, xb, cols) in ((452, 540, (MARI, MARI_D, MARI_HI)), (200, 252, (MARI, MARI_D)), (0, 50, (120, 140, 70))):
        for i in range(int((xb - xa) / 2.5)):                       # 神庙门口的花瓣 / 牛旁边掉的花 / 树下落叶
            x, y = int(hrange(xa, xb, i, xa, 48)), int(hrange(148, 166, i, xa, 49))
            if hash01(i, xa, 50) < 0.55:
                c = cols[i % len(cols)] if isinstance(cols[0], tuple) else cols
                px(d, x, y, mix(c, STONE, 0.35))
    for (x, y, w) in ((338, 168, 14), (120, 172, 10), (560, 160, 12)):   # 湿印子（泼过水）
        for k in range(w):
            for j in range(2):
                if hash01(x, k, j, 51) < 0.8:
                    px(d, x + k, y + j, dk(STONE, 0.93))
    for x in range(0, PW, 3):                                       # 最下面一行：对面房子的影子边
        px(d, x, H - 1, dk(STONE, 0.9))


def plinth(im, x0, x1, top=PL_TOP, col=SAND_S, seed=0):
    """门口的石台（otla）：顶面 top..top+2 亮、立面 top+3..LANE−1 砌块。x1 含。"""
    d = ImageDraw.Draw(im)
    hl(d, x0, x1, top, lt(col, 0.35))
    hl(d, x0, x1, top + 1, lt(col, 0.2))
    hl(d, x0, x1, top + 2, lt(col, 0.1))
    rect(d, x0, top + 3, x1, LANE - 1, col)
    hl(d, x0, x1, top + 3, dk(col, 0.72))
    for yy in range(top + 6, LANE, 3):
        hl(d, x0, x1, yy, dk(col, 0.88))
    for yy in range(top + 3, LANE, 3):
        off = 0 if (yy // 3) % 2 else 5
        for xx in range(x0 + off, x1, 10):
            vl(d, xx, yy + 1, min(LANE - 1, yy + 2), dk(col, 0.86))
    vl(d, x0, top, LANE - 1, lt(col, 0.2))
    vl(d, x1, top + 3, LANE - 1, dk(col, 0.7))
    mottle(im, (x0 + 1, top + 4, x1 - 1, LANE - 1), col, dk(col, 0.93), lt(col, 0.06), 70 + seed, cell=3)


def shop_dark(im, x0, y0, x1, y1, seed, shelves=True):
    """一层铺面里面：暗（上面更暗、下面一点地面反光、偏冷），后墙几层架子 + 罐子 / 布袋。x1 / y1 含。"""
    d = ImageDraw.Draw(im)
    for y in range(y0, y1 + 1):
        u = (y - y0) / max(1, y1 - y0)
        hl(d, x0, x1, y, mix((44, 36, 40), (82, 70, 68), u ** 1.4))
    if shelves:
        for sy in range(y0 + 8, y1 - 6, 9):
            hl(d, x0 + 1, x1 - 1, sy, (96, 76, 60))
            for xx in range(x0 + 2, x1 - 2, 3):
                if hash01(seed, xx, sy) < 0.7:
                    c = ((140, 110, 80), (160, 140, 110), (110, 120, 140), (150, 70, 60), (180, 160, 100))[
                        int(hash01(seed, xx, sy, 2) * 5)]
                    hh = 2 + int(hash01(seed, xx, sy, 3) * 4)
                    rect(d, xx, sy - hh, xx + 1, sy - 1, dk(c, 0.72))
                    px(d, xx, sy - hh, dk(c, 0.9))


# ============================================================ 近景：街口（横巷 + 菩提树）
def _toward(x, y, u=LANE_U):
    return (x + (VP[0] - x) * u, y + (VP[1] - y) * u)


def draw_side_lane(im):
    d = ImageDraw.Draw(im)
    ex = _toward(0, LANE)
    fx = _toward(B1[0], LANE)
    d.polygon([(0, LANE), (B1[0] - 1, LANE), (fx[0], fx[1]), (ex[0], ex[1])], fill=C(STONE_S))
    for k in range(1, 6):                                         # 地上的横缝（越远越密）
        u = LANE_U * (1 - (1 - k / 6.0) ** 1.6)
        a, b = _toward(0, LANE, u), _toward(B1[0] - 1, LANE, u)
        hl(d, int(a[0]) + 1, int(b[0]) - 1, int(round(a[1])), dk(STONE_S, 0.88))
    a = _toward(0, 28)                                            # 左边那栋的右侧墙（背光）
    d.polygon([(0, 28), (a[0], a[1]), (ex[0], ex[1]), (0, LANE)], fill=C(dk(PINK, 0.66)))
    for k in range(3):
        u = 0.12 + k * 0.1
        p0, p1 = _toward(0, 60 + k * 2, u), _toward(0, 74 + k * 2, u)
        vl(d, int(p0[0]), int(p0[1]), int(p1[1]), dk(PINK, 0.42))
    b = _toward(B1[0] - 1, 20)                                    # B1 的左侧墙（朝左，亮）
    sw = lt(OCHRE, 0.1)
    d.polygon([(B1[0] - 1, 20), (b[0], b[1]), (fx[0], fx[1]), (B1[0] - 1, LANE)], fill=C(sw))
    for (ya, yb) in ((34, 50), (64, 82), (100, 124)):             # 侧墙上的窗（透视压扁）
        for u0 in (0.08, 0.24):
            p0, p1 = _toward(B1[0] - 1, ya, u0), _toward(B1[0] - 1, yb, u0 + 0.08)
            q0 = _toward(B1[0] - 1, ya, u0 + 0.08)
            d.polygon([(p0[0], p0[1]), (q0[0], q0[1]), (p1[0], p1[1]), (p0[0], p1[1] - (q0[1] - p0[1]))],
                      fill=C(dk(sw, 0.55)))
    # 侧墙上沿的女儿墙线、墙脚
    d.line([(B1[0] - 1, 20), (b[0], b[1])], fill=C(lt(sw, 0.3)))
    d.line([(B1[0] - 1, LANE), (fx[0], fx[1])], fill=C(dk(sw, 0.7)))
    # 巷子里挂的电线
    wire(d, 0, 50, b[0], b[1] + 18, 3, (60, 56, 60))
    wire(d, 0, 62, b[0] - 2, b[1] + 30, 4, (60, 56, 60))


def draw_tree(im):
    """巷口的菩提树：粗树干（盘根、气根）、树干绑红线，下面一圈石台，台上几块抹了朱砂的小石头 + 三叉戟 + 小油灯；
    树冠很大，盖住左上角（树冠在近景里，挡住一点 B1 的左上）。"""
    d = ImageDraw.Draw(im)
    tx = 22
    # 石台（chabutra）：顶面 132–134，立面 135–145
    plinth(im, 2, 44, top=132, col=lt(SAND_S, 0.08), seed=1)
    d = ImageDraw.Draw(im)
    for (x0, x1) in ((4, 12), (30, 42)):                          # 立面刷了白灰 + 一道朱红
        rect(d, x0, 137, x1, 144, (226, 216, 200))
        hl(d, x0, x1, 140, VERMIL)
    # 两根粗枝（大半藏在树冠里）
    BK = ((146, 126, 104), (116, 98, 80), (84, 70, 60))
    for (bx, by, ex_, ey, w0) in ((tx - 1, 90, tx - 26, 40, 5), (tx + 2, 86, tx + 40, 34, 5), (tx, 80, tx + 6, 20, 4)):
        n = int(math.hypot(ex_ - bx, ey - by))
        for i in range(n + 1):
            u = i / n
            x = bx + (ex_ - bx) * u + 3 * math.sin(u * 3.0)
            y = by + (ey - by) * u
            w = max(2, int(round(w0 * (1 - 0.5 * u))))
            for k in range(w):
                px(d, round(x) - w // 2 + k, round(y), BK[0] if k == 0 else (BK[1] if k < w - 1 else BK[2]))
    # 树干：根部张开（盘根）、往上变细、竖着的扭纹
    for y in range(78, 133):
        u = (132 - y) / 54.0
        w = int(round(9 + 2 * (1 - u) + 7 * (1 - u) ** 5))
        x0 = tx - w // 2 + int(round(1.5 * math.sin(y * 0.09)))
        for k in range(w):
            v = k / max(1, w - 1)
            c = BK[0] if v < 0.22 else (BK[1] if v < 0.68 else BK[2])
            if (k * 5 + y // 4) % 9 == 0:
                c = dk(c, 0.84)
            if v > 0.3 and (k * 7 + y // 3) % 11 == 0:
                c = lt(c, 0.12)
            px(d, x0 + k, y, c)
    # 树冠（菩提：大、心形叶，颜色偏亮的黄绿）
    pal = ((40, 86, 44), (62, 122, 56), (96, 158, 70), (150, 196, 92))
    for (cx, cy, rx, ry, sd) in ((14, 30, 40, 28, 11), (-10, 52, 22, 16, 12), (46, 46, 20, 18, 13),
                                 (24, 66, 28, 12, 14), (58, 20, 14, 12, 15), (28, 4, 34, 12, 16)):
        _canopy(d, cx, cy, rx, ry, 700 + sd, pal=pal)
    for i in range(130):                                            # 一片片亮的心形叶
        x = int(hrange(-24, 70, i, 81))
        y = int(hrange(0, 74, i, 82))
        if math.hypot((x - 18) / 50.0, (y - 34) / 38.0) < 1 and hash01(i, 83) < 0.6:
            if im.getpixel((x, y))[3] if 0 <= x < im.width else 0:
                px(d, x, y, (176, 214, 110))
                px(d, x + 1, y + 1, (120, 176, 80))
    for (ax, ay, L) in ((tx + 16, 70, 24), (tx - 10, 72, 18), (tx + 30, 62, 16), (tx - 18, 64, 12)):   # 气根
        for k in range(L):
            px(d, ax + (k // 8), ay + k, (128, 110, 90) if k % 3 else (100, 84, 70))
    for yy in (104, 106, 107):                                     # 绑的红线 / 黄线
        hl(d, tx - 4, tx + 4, yy, VERMIL if yy != 106 else MARI_HI)
    rect(d, tx - 3, 114, tx + 3, 122, (196, 64, 44))               # 一块红布
    hl(d, tx - 3, tx + 3, 114, (226, 96, 60))
    # 台上的小石头（朱砂）、三叉戟、小油灯
    for (sx, sy) in ((8, 131), (34, 131), (39, 131)):
        d.ellipse((sx - 2, sy - 3, sx + 2, sy), fill=C(VERMIL))
        px(d, sx - 1, sy - 3, (240, 120, 90))
        px(d, sx, sy - 1, (150, 40, 30))
    vl(d, 14, 116, 131, (110, 110, 118))                           # 三叉戟
    hl(d, 12, 16, 118, (110, 110, 118))
    for xx in (12, 14, 16):
        vl(d, xx, 114 if xx == 14 else 115, 118, (150, 150, 160))
    rect(d, 13, 122, 15, 124, VERMIL)                              # 绑了一块红布
    px(d, 44 - 16, 130, (176, 100, 60))                            # 油灯
    px(d, 44 - 15, 130, (176, 100, 60))
    px(d, 44 - 15, 129, (255, 220, 120))
    # 树冠（菩提：大、心形叶，颜色偏亮的黄绿）
    pal = ((40, 86, 44), (62, 122, 56), (96, 158, 70), (150, 196, 92))
    for (cx, cy, rx, ry, sd) in ((14, 26, 38, 22, 11), (-8, 40, 22, 14, 12), (46, 30, 22, 16, 13), (22, 4, 30, 12, 14),
                                 (58, 46, 12, 8, 15)):
        _canopy(d, cx, cy, rx, ry, 700 + sd, pal=pal)
    for i in range(70):                                             # 一片片亮的心形叶
        x = int(hrange(-20, 66, i, 81))
        y = int(hrange(0, 58, i, 82))
        if math.hypot((x - 16) / 46.0, (y - 28) / 30.0) < 1 and hash01(i, 83) < 0.6:
            px(d, x, y, (176, 214, 110))
            px(d, x + 1, y + 1, (120, 176, 80))


# ============================================================ 近景：B1 赭黄三层 + 水果摊
def draw_b1(im):
    x0, x1 = B1
    facade(im, x0, x1, 22, LANE - 1, OCHRE, 101, streaks=4)
    d = ImageDraw.Draw(im)
    brick_patch(im, 112, 70, 14, 9, 3)
    brick_patch(im, 52, 108, 10, 7, 4)
    # 屋顶：女儿墙（小盲拱）+ 屋顶小房间 + 电视天线
    parapet(im, x0, x1 - 1, 20, OCHRE, 'arch')
    d = ImageDraw.Draw(im)
    rect(d, 98, 6, 126, 19, (236, 214, 176))
    hl(d, 97, 127, 5, (250, 232, 200))
    vl(d, 126, 6, 19, (196, 170, 130))
    rect(d, 104, 9, 110, 19, dk(OCHRE, 0.5))
    win_shutter(im, 116, 9, 6, 6, (236, 214, 176), SHUT_G, 'closed')
    d = ImageDraw.Draw(im)
    tv_antenna(d, 64, 2, 18)
    # 三楼：三扇百叶窗 + 铁栏杆的小阳台，栏杆上搭着纱丽
    for (wx, st) in ((54, 'open'), (84, 'closed'), (114, 'half')):
        win_shutter(im, wx, 30, 11, 15, OCHRE, SHUT_G, st)
    d = ImageDraw.Draw(im)
    hl(d, 50, 130, 47, lt(OCHRE, 0.3))
    rect(d, 50, 48, 130, 49, dk(OCHRE, 0.72))
    for xx in range(51, 130, 3):
        vl(d, xx, 42, 47, IRON)
    hl(d, 50, 130, 42, IRON_HI)
    for (sx, L, c) in ((56, 10, CLOTH[0]), (70, 14, CLOTH[1]), (96, 12, CLOTH[2]), (108, 8, CLOTH[7])):
        rect(d, sx, 42, sx + L - 1, 43, lt(c, 0.15))
        rect(d, sx, 44, sx + L - 1, 49 + (L % 3), c)
        hl(d, sx, sx + L - 1, 46, dk(c, 0.78))
        vl(d, sx + L - 1, 44, 49 + (L % 3), dk(c, 0.72))
    chajja(im, x0, x1 - 1, 52, lt(OCHRE, 0.12))
    # 二楼：雕花木阳台（jharokha）+ 两边的小窗
    jharokha(im, 70, 58, 40, 26, WOOD, seed=1)
    win_shutter(im, 52, 64, 9, 13, OCHRE, SHUT_B, 'closed')
    win_shutter(im, 120, 64, 9, 13, OCHRE, SHUT_B, 'open')
    poster(im, 54, 84, 7, 8, 11)
    chajja(im, x0, x1 - 1, 92, lt(OCHRE, 0.12))
    # 一层：铺面（暗）+ 门口石台
    shop_dark(im, 54, 97, 126, PL_TOP - 1, 1)
    d = ImageDraw.Draw(im)
    vl(d, 53, 96, PL_TOP - 1, dk(OCHRE, 0.7))
    vl(d, 127, 96, PL_TOP - 1, lt(OCHRE, 0.2))
    plinth(im, x0 + 1, x1 - 2, seed=2)


FRUIT = (58, 122)             # 水果摊（篷的 x 范围）


def draw_fruit_stall(im):
    """水果摊：两根竹竿撑一块旧麻布篷（条纹），篷下的横竿挂四串香蕉、正中一杆铜秤；
    石台上一张木桌：左边一大筐芒果、中间一摞香蕉、右前方一筐红石榴（最醒目）；桌下几个木箱。"""
    d = ImageDraw.Draw(im)
    a, b = FRUIT
    for xx in (a + 1, b - 1):                                      # 竹竿
        vl(d, xx, 88, PL_TOP + 1, (196, 170, 112))
        vl(d, xx + 1, 88, PL_TOP + 1, (150, 124, 78))
        for yy in range(92, PL_TOP, 7):
            px(d, xx, yy, (230, 206, 150))
    for i in range(a - 2, b + 3):                                   # 篷：往前斜（上沿 87，下沿 95），蓝白旧条纹
        u = (i - a + 2) / (b - a + 4)
        sag = int(round(1.5 * math.sin(math.pi * u * 3)))
        for yy in range(87, 95 + sag):
            c = (176, 196, 210) if ((i - a) // 5) % 2 else (226, 222, 206)
            if yy == 87:
                c = lt(c, 0.2)
            if yy >= 93 + sag:
                c = dk(c, 0.82)
            px(d, i, yy, c)
    mul_box(im, (a, 96 + 1, b, 99), SHADOW_MUL)
    hl(d, a + 2, b - 2, 97, (150, 124, 78))                          # 挂香蕉的横竿
    for (bx, n) in ((a + 8, 4), (a + 20, 5), (b - 22, 5), (b - 10, 4)):   # 香蕉串（挂着：一梳梳往上翘的香蕉）
        cx = bx + 2
        vl(d, cx, 97, 99 + n * 3, (110, 104, 56))                      # 蕉轴
        for r in range(n):
            y = 100 + r * 3
            hw = 4 - r // 2
            for k in range(-hw, hw + 1):
                up = 1 if abs(k) >= hw - 1 else 0                     # 两头往上翘
                c = (246, 214, 76) if k < 0 else (226, 186, 52)
                if abs(k) == hw:
                    c = (176, 182, 70)                                 # 尖端还青
                px(d, cx + k, y - up, c)
                px(d, cx + k, y + 1 - up, (206, 164, 44) if abs(k) < hw else (150, 150, 60))
            px(d, cx, y, (150, 120, 50))
        px(d, cx, 101 + n * 3, (96, 84, 46))
    cx = (a + b) // 2                                                # 铜秤
    vl(d, cx, 97, 104, (120, 100, 60))
    hl(d, cx - 7, cx + 7, 104, (196, 150, 70))
    px(d, cx, 103, (230, 190, 90))
    for sx in (cx - 7, cx + 7):
        d.line((sx, 104, sx - 2, 109), fill=C((150, 120, 70)))
        d.line((sx, 104, sx + 2, 109), fill=C((150, 120, 70)))
        hl(d, sx - 3, sx + 3, 110, (220, 170, 70))
        hl(d, sx - 2, sx + 2, 111, (170, 120, 50))
    # 桌子
    ty = 124
    rect(d, a + 2, ty, b - 2, ty + 1, WOOD_HI)
    rect(d, a + 2, ty + 2, b - 2, ty + 3, WOOD_D)
    for lx in (a + 4, b - 5):
        rect(d, lx, ty + 4, lx + 1, PL_TOP, WOOD_D)
    for (cx0, cw, col) in ((a + 8, 14, (176, 132, 82)), (a + 26, 12, (160, 118, 72)), (b - 26, 16, (184, 140, 88))):
        rect(d, cx0, ty + 6, cx0 + cw, PL_TOP, col)                 # 木箱
        hl(d, cx0, cx0 + cw, ty + 6, lt(col, 0.25))
        hl(d, cx0, cx0 + cw, ty + 9, dk(col, 0.75))
        vl(d, cx0 + cw, ty + 6, PL_TOP, dk(col, 0.65))
    # 芒果一大筐（左）
    bx0, bx1 = a + 4, a + 28
    d.ellipse((bx0, ty - 4, bx1, ty + 3), fill=C((170, 130, 70)))
    hl(d, bx0 + 2, bx1 - 2, ty - 2, (206, 166, 96))
    for i in range(34):
        x = int(hrange(bx0 + 2, bx1 - 3, i, 91))
        y = int(ty - 4 - hrange(0, 9, i, 92) * (1 - abs((x - (bx0 + bx1) / 2) / ((bx1 - bx0) / 2)) ** 2))
        c = ((246, 196, 60), (238, 150, 40), (180, 190, 70), (250, 214, 90))[i % 4]
        rect(d, x, y, x + 2, y + 1, c)
        px(d, x, y, lt(c, 0.3))
        px(d, x + 2, y + 1, dk(c, 0.75))
    # 中间：躺着的几串香蕉 + 几个木瓜
    for k in range(3):
        hl(d, a + 31, a + 41, ty - 2 - k * 2, (244, 210, 70))
        hl(d, a + 32, a + 42, ty - 1 - k * 2, (214, 176, 48))
    for (px0, c) in ((a + 44, (236, 150, 50)), (a + 49, (130, 168, 70))):
        d.ellipse((px0, ty - 5, px0 + 5, ty), fill=C(c))
        px(d, px0 + 1, ty - 4, lt(c, 0.4))
    # 一筐红石榴（右前方，最醒目）
    gx0, gx1 = b - 20, b - 1
    rect(d, gx0, ty - 2, gx1, ty + 8, (150, 108, 62))               # 竹筐
    for xx in range(gx0, gx1 + 1, 2):
        vl(d, xx, ty - 1, ty + 8, (126, 90, 52))
    hl(d, gx0, gx1, ty - 2, (190, 146, 90))
    hl(d, gx0, gx1, ty + 3, (190, 146, 90))
    for i in range(16):
        x = gx0 + 1 + (i * 5) % 18 + (1 if (i // 4) % 2 else 0)
        y = ty - 4 - (i // 4) * 2 + (1 if i % 2 else 0)
        if x > gx1 - 2:
            continue
        d.ellipse((x, y - 1, x + 3, y + 2), fill=C((204, 36, 48)))
        px(d, x + 1, y - 1, (240, 96, 96))
        px(d, x + 3, y + 1, (140, 20, 36))
        px(d, x + 2, y - 2, (120, 30, 30))                           # 石榴顶上的小冠
    for (x, y) in ((gx0 - 3, ty + 9), (gx0 + 5, PL_TOP - 1)):       # 掉在石台上的两个
        d.ellipse((x, y - 1, x + 2, y + 1), fill=C((204, 36, 48)))
        px(d, x, y - 1, (240, 96, 96))
    cast_shadow(im, [(gx1 + 1, ty - 1), (gx1 + 3, ty + 1), (gx1 + 3, ty + 9), (gx1 + 1, ty + 9)], mul=SOFT_MUL)


# ============================================================ 近景：B2 粉色两层 + 警察岗亭
def draw_b2(im):
    x0, x1 = B2
    facade(im, x0, x1, 52, LANE - 1, PINK, 202, streaks=3)
    d = ImageDraw.Draw(im)
    parapet(im, x0, x1 - 1, 50, PINK, 'post')
    d = ImageDraw.Draw(im)
    rect(d, 150, 34, 188, 48, (236, 226, 210))                      # 屋顶房（白灰）
    hl(d, 149, 189, 33, (250, 244, 232))
    vl(d, 188, 34, 48, (200, 190, 174))
    rect(d, 156, 38, 162, 48, dk(PINK, 0.5))
    win_shutter(im, 172, 38, 8, 6, (236, 226, 210), SHUT_B, 'open')
    d = ImageDraw.Draw(im)
    water_tank(d, 164, 25, 14, 8, (186, 186, 180))
    brick_patch(im, 194, 60, 12, 8, 5)
    # 二楼：两扇蓝框拱窗 + 中间褪色的手绘广告
    win_arch(im, 141, 58, 12, 24, PINK, (236, 230, 220), seed=1)
    win_arch(im, 191, 58, 12, 24, PINK, (236, 230, 220), seed=2)
    ad = (158, 58, 185, 82)                                         # 广告：黄底、红圆、一个瓶子、两行字
    lay = A._new(im.width, im.height)
    ld = ImageDraw.Draw(lay)
    rect(ld, ad[0], ad[1], ad[2], ad[3], (236, 206, 92))
    rect(ld, ad[0] + 1, ad[1] + 1, ad[2] - 1, ad[1] + 4, (200, 60, 50))
    ld.ellipse((ad[0] + 3, ad[1] + 7, ad[0] + 13, ad[1] + 17), fill=C((210, 64, 52)))
    rect(ld, ad[0] + 17, ad[1] + 7, ad[0] + 21, ad[1] + 19, (70, 110, 70))
    rect(ld, ad[0] + 18, ad[1] + 5, ad[0] + 20, ad[1] + 6, (70, 110, 70))
    hl(ld, ad[0] + 18, ad[0] + 18, ad[1] + 9, (160, 210, 160))
    sign_board(ld, ad[0] + 2, ad[1] + 19, ad[2] - 2, ad[3] - 1, (236, 206, 92), (60, 50, 60), seed=4, border=(236, 206, 92))
    a = np.array(lay).astype(np.float32)
    b = np.array(im).astype(np.float32)
    m = a[..., 3] > 0
    n = A._fbm(im.width, im.height, 3, seed=55)
    f = 0.32 + 0.3 * n[m]
    a[m, :3] = a[m, :3] * (1 - f[:, None]) + b[m, :3] * f[:, None]
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))
    chajja(im, x0, x1 - 1, 86, lt(PINK, 0.12))
    # 一层：红底招牌 + 绿色卷帘门（拉起一半，下面看得见铺子里）
    d = ImageDraw.Draw(im)
    sign_board(d, 140, 90, 204, 97, (190, 40, 44), (250, 220, 120), seed=7)
    shop_dark(im, 140, 100, 204, LANE - 1, 2)
    d = ImageDraw.Draw(im)
    for yy in range(100, 122):                                       # 卷帘门（波纹）
        c = (78, 120, 96) if yy % 2 else (96, 142, 114)
        hl(d, 140, 204, yy, c)
    hl(d, 140, 204, 122, (60, 92, 74))
    hl(d, 140, 204, 123, (40, 40, 40))
    for xx in (146, 198):                                            # 门框
        pass
    vl(d, 139, 99, LANE - 1, dk(PINK, 0.7))
    vl(d, 205, 99, LANE - 1, lt(PINK, 0.2))
    hl(d, 139, 205, 99, lt(PINK, 0.3))
    # 墙上的电表箱 + 一束电线
    rect(d, 136, 104, 138, 110, (176, 176, 168))


POLICE = (153, 189)           # 岗亭 x 范围


def draw_police_booth(im):
    """警察岗亭：奶油色木亭（四方、尖顶四坡、顶上一盏红灯），前脸一块蓝底白字的 POLICE 牌（色块）、一个窗口（里面暗、
    一部黑电话），下半截红白斜纹；旁边靠着一根长棍（lathi）。"""
    a, b = POLICE
    d = ImageDraw.Draw(im)
    body0 = 106
    cast_shadow(im, [(b, body0 + 4), (b + 6, body0 + 8), (b + 8, LANE + 3), (b, LANE + 3)], mul=SOFT_MUL)
    cast_shadow(im, [(a + 3, LANE), (b + 1, LANE), (b + 8, LANE + 4), (a + 6, LANE + 4)], mul=SOFT_MUL)
    d = ImageDraw.Draw(im)
    cream, cream_s = (232, 222, 196), (198, 186, 160)
    rect(d, a, body0, b, LANE - 1, cream)
    vl(d, a, body0, LANE - 1, lt(cream, 0.4))
    rect(d, b - 5, body0, b, LANE - 1, cream_s)                       # 右侧面（背光）
    vl(d, b - 6, body0, LANE - 1, dk(cream, 0.85))
    # 尖顶（四坡）+ 红灯
    for yy in range(94, body0):
        u = (yy - 94) / (body0 - 94)
        hw = int(round(4 + u * ((b - a) / 2 + 3)))
        cx = (a + b) // 2
        hl(d, cx - hw, cx + hw, yy, (176, 60, 52))
        hl(d, cx - hw, cx - hw // 3, yy, (206, 86, 70))
        hl(d, cx + hw // 2, cx + hw, yy, (140, 44, 40))
    hl(d, a - 3, b + 3, body0, (110, 36, 34))
    hl(d, a - 3, b + 3, body0 + 1, dk(cream, 0.7))
    cx = (a + b) // 2
    rect(d, cx - 1, 89, cx + 1, 93, (230, 50, 40))
    px(d, cx - 1, 89, (255, 160, 140))
    hl(d, cx - 2, cx + 2, 93, (60, 60, 60))
    # POLICE 牌
    sy0 = body0 + 4
    rect(d, a + 3, sy0, b - 8, sy0 + 6, (40, 76, 150))
    hl(d, a + 3, b - 8, sy0, (80, 116, 190))
    xx = a + 6
    for k in range(6):                                                 # 六个“字母”色块
        rect(d, xx, sy0 + 2, xx + 2, sy0 + 4, (244, 244, 240))
        if k in (1, 4):
            px(d, xx + 1, sy0 + 3, (40, 76, 150))
        xx += 4
    # 窗口
    wy0, wy1 = sy0 + 10, sy0 + 20
    rect(d, a + 4, wy0, b - 9, wy1, (52, 46, 50))
    hl(d, a + 4, b - 9, wy0, (30, 26, 30))
    rect(d, a + 3, wy1 + 1, b - 8, wy1 + 2, WOOD)                     # 窗台
    hl(d, a + 3, b - 8, wy1 + 1, WOOD_HI)
    rect(d, a + 9, wy1 - 3, a + 13, wy1, (24, 24, 28))                 # 黑电话
    hl(d, a + 8, a + 14, wy1 - 4, (40, 40, 44))
    rect(d, b - 18, wy0 + 2, b - 13, wy1, (90, 80, 70))                # 里面的人影（帽子）——只是暗一点的块
    # 下半截：红白斜纹
    for yy in range(wy1 + 4, LANE - 1):
        for x in range(a + 1, b - 6):
            c = (210, 50, 46) if ((x + yy) // 3) % 2 else (240, 236, 228)
            px(d, x, yy, c)
        for x in range(b - 5, b + 1):
            c = (164, 40, 38) if ((x + yy) // 3) % 2 else (196, 190, 182)
            px(d, x, yy, c)
    hl(d, a, b, wy1 + 3, WOOD_D)
    hl(d, a, b, LANE - 1, (110, 100, 90))
    # 长棍（lathi）
    d.line((b + 3, LANE - 1, b + 6, 112), fill=C((150, 110, 60)))
    px(d, b + 6, 112, (200, 170, 110))


# ============================================================ 近景：B3 天蓝窄楼 + 神龛 + 牛
COW_XY = (211, 127)           # 牛（42×20）左上角：肚子贴着街的后沿（y 146）


def draw_b3(im):
    x0, x1 = B3
    facade(im, x0, x1, 14, LANE - 1, SKYBLUE, 303, streaks=4)
    d = ImageDraw.Draw(im)
    parapet(im, x0, x1 - 1, 12, SKYBLUE, 'plain')
    d = ImageDraw.Draw(im)
    rect(d, 236, 4, 246, 11, (150, 120, 96))                          # 屋顶的鸽子笼（木）
    for xx in range(237, 246, 2):
        vl(d, xx, 6, 10, (80, 60, 50))
    hl(d, 235, 247, 3, (176, 146, 116))
    brick_patch(im, 214, 26, 9, 12, 7)
    win_shutter(im, 226, 22, 12, 22, SKYBLUE, SHUT_G, 'half')        # 四楼高窗
    chajja(im, x0, x1 - 1, 50, lt(SKYBLUE, 0.15))
    # 三楼：铁阳台 + 罗勒盆栽 + 门
    d = ImageDraw.Draw(im)
    rect(d, 222, 56, 240, 84, DARK_IN)
    door_carved(im, 223, 57, 16, 28, WOOD, frame=lt(SKYBLUE, 0.3), studs=False)
    d = ImageDraw.Draw(im)
    hl(d, x0 + 2, x1 - 3, 85, lt(SKYBLUE, 0.35))
    rect(d, x0 + 2, 86, x1 - 3, 87, dk(SKYBLUE, 0.7))
    for xx in range(x0 + 3, x1 - 3, 2):
        vl(d, xx, 76, 84, IRON)
    hl(d, x0 + 2, x1 - 3, 75, IRON_HI)
    for (px0, h) in ((x0 + 6, 6), (x1 - 12, 8)):                      # 罗勒（tulsi）盆
        rect(d, px0, 70, px0 + 4, 74, (176, 90, 60))
        hl(d, px0, px0 + 4, 70, (210, 120, 80))
        for k in range(h):
            px(d, px0 + 2 + (k % 3) - 1, 69 - k, LEAF_M if k % 2 else LEAF)
        px(d, px0 + 1, 66, LEAF_HI)
    mul_box(im, (x0 + 3, 88, x1 - 2, 90), SHADOW_MUL)
    # 一层：铜钉大木门 + 神龛 + 电表箱
    door_carved(im, 223, 98, 18, 48, WOOD, frame=SAND_S)
    d = ImageDraw.Draw(im)
    nx, ny = 212, 104                                                  # 神龛：小拱龛、朱红色的象头神、花环、油灯
    rect(d, nx - 1, ny - 2, nx + 7, ny + 13, lt(SKYBLUE, 0.4))
    rect(d, nx, ny, nx + 6, ny + 11, (70, 50, 46))
    hl(d, nx + 1, nx + 5, ny - 1, (70, 50, 46))
    rect(d, nx + 2, ny + 4, nx + 4, ny + 10, VERMIL)
    rect(d, nx + 1, ny + 7, nx + 5, ny + 10, VERMIL)
    px(d, nx + 3, ny + 3, VERMIL)
    px(d, nx + 2, ny + 5, (255, 236, 200))
    px(d, nx + 4, ny + 5, (255, 236, 200))
    px(d, nx + 3, ny + 7, dk(VERMIL, 0.7))                            # 象鼻
    px(d, nx + 3, ny + 8, dk(VERMIL, 0.7))
    hl(d, nx - 1, nx + 7, ny + 12, SAND_S)
    px(d, nx + 1, ny + 11, (255, 220, 120))                           # 油灯
    rect(d, 244, 102, 249, 112, (190, 190, 182))                      # 电表箱
    rect(d, 245, 104, 248, 107, (60, 70, 80))
    px(d, 246, 105, (200, 220, 230))
    vl(d, 246, 92, 101, (40, 40, 44))
    vl(d, 248, 92, 101, (40, 40, 44))


def draw_cow(im):
    x, y = COW_XY
    cast_shadow(im, [(x + 8, y + 19), (x + 42, y + 19), (x + 46, y + 21), (x + 10, y + 21)], mul=SHADOW_MUL)
    paste(im, cow_img(), x, y)


# ============================================================ 近景：B4 芥末黄三层 + 报纸摊
def draw_b4(im):
    x0, x1 = B4
    facade(im, x0, x1, 26, LANE - 1, MUSTARD, 404, streaks=4)
    d = ImageDraw.Draw(im)
    parapet(im, x0, x1 - 1, 24, MUSTARD, 'post')
    d = ImageDraw.Draw(im)
    tv_antenna(d, 320, 6, 18)
    for wx in (260, 287, 314):                                         # 三楼三扇彩色玻璃拱窗
        win_arch(im, wx, 32, 12, 22, MUSTARD, (240, 232, 208), seed=wx)
    brick_patch(im, 300, 40, 9, 10, 8)
    chajja(im, x0, x1 - 1, 58, lt(MUSTARD, 0.12))
    # 二楼：长木阳台（格栅栏杆），后面三扇门
    d = ImageDraw.Draw(im)
    for dx in (262, 286, 310):
        rect(d, dx, 64, dx + 11, 86, DARK_IN)
        door_carved(im, dx + 1, 66, 10, 20, (110, 80, 60), frame=lt(MUSTARD, 0.3), studs=False)
    d = ImageDraw.Draw(im)
    rect(d, x0 + 3, 75, x1 - 4, 86, WOOD)
    hl(d, x0 + 3, x1 - 4, 75, WOOD_HI)
    hl(d, x0 + 3, x1 - 4, 76, WOOD_D)
    for yy in range(78, 86):
        for xx in range(x0 + 4, x1 - 4):
            if (xx + yy) % 2 == 0 and (xx - x0) % 8 not in (0, 1):
                px(d, xx, yy, DARK_IN)
    for xx in range(x0 + 3, x1 - 3, 8):
        vl(d, xx, 75, 86, WOOD_HI)
        vl(d, xx + 1, 77, 86, WOOD_D)
    hl(d, x0 + 2, x1 - 3, 87, WOOD_HI)
    rect(d, x0 + 2, 88, x1 - 3, 89, WOOD_D)
    for bx in range(x0 + 6, x1 - 4, 12):                              # 托架
        for r in range(4):
            hl(d, bx + r // 2, bx + 2, 90 + r, WOOD if r < 2 else WOOD_D)
    mul_box(im, (x0 + 4, 90, x1 - 2, 93), SHADOW_MUL)
    # 一层：铺面（暗）+ 石台
    shop_dark(im, x0 + 3, 98, x1 - 4, PL_TOP - 1, 4)
    d = ImageDraw.Draw(im)
    hl(d, x0 + 2, x1 - 3, 97, lt(MUSTARD, 0.3))
    plinth(im, x0 + 1, x1 - 2, seed=4)


NEWS = (256, 322)


def draw_news_stall(im):
    """报纸摊：铁皮小檐（波纹）、两根细铁杆拉一排绳，夹着一排杂志（彩色封面色块）；
    正中钉着一张大头版（报头黑条 + 粗标题 + 一个看不清的人像轮廓）；台上一摞摞报纸（白边 + 灰色的字行）。"""
    a, b = NEWS
    d = ImageDraw.Draw(im)
    for yy in range(92, 97):                                           # 铁皮檐
        c = (150, 156, 160) if yy % 2 else (118, 124, 130)
        hl(d, a - 2, b + 2, yy, c)
    hl(d, a - 2, b + 2, 92, (190, 196, 200))
    mul_box(im, (a, 97, b + 2, 99), SHADOW_MUL)
    for xx in (a, b):
        vl(d, xx, 97, PL_TOP, (70, 70, 78))
    for (ya, n) in ((101, 9), (112, 8)):                               # 两排杂志
        hl(d, a, b, ya - 1, (200, 200, 200))
        for i in range(n):
            x = a + 3 + i * ((b - a - 6) // n)
            if a + 24 <= x <= a + 38 and ya == 101:
                continue
            c = ((214, 60, 70), (60, 120, 200), (240, 200, 60), (80, 170, 110), (230, 120, 170), (250, 250, 240),
                 (150, 90, 180))[(i * 3 + ya) % 7]
            rect(d, x, ya, x + 5, ya + 8, c)
            hl(d, x, x + 5, ya, lt(c, 0.3))
            rect(d, x + 1, ya + 2, x + 4, ya + 5, dk(c, 0.7) if (i + ya) % 3 else (250, 240, 220))
            hl(d, x + 1, x + 4, ya + 7, (250, 250, 250))
            px(d, x + 2, ya - 1, (230, 230, 230))
    # 头版（正中、最大）
    fx0, fy0 = a + 24, 100
    rect(d, fx0, fy0, fx0 + 15, fy0 + 20, (240, 236, 222))
    rect(d, fx0 + 1, fy0 + 1, fx0 + 14, fy0 + 3, (30, 30, 34))         # 报头
    hl(d, fx0 + 3, fx0 + 12, fy0 + 2, (240, 236, 222))
    rect(d, fx0 + 1, fy0 + 5, fx0 + 14, fy0 + 6, (70, 66, 70))         # 粗标题
    rect(d, fx0 + 2, fy0 + 8, fx0 + 8, fy0 + 15, (176, 170, 160))      # 照片框：灰底 + 一个看不清的人像
    d.ellipse((fx0 + 3, fy0 + 9, fx0 + 7, fy0 + 12), fill=C((96, 90, 90)))
    rect(d, fx0 + 3, fy0 + 13, fx0 + 7, fy0 + 15, (96, 90, 90))
    px(d, fx0 + 7, fy0 + 12, (196, 110, 120))                          # 手臂上一点红（女帝？）
    for yy in range(fy0 + 8, fy0 + 19, 2):
        hl(d, fx0 + 10, fx0 + 14, yy, (150, 146, 140))
    hl(d, fx0 + 2, fx0 + 14, fy0 + 17, (150, 146, 140))
    hl(d, fx0 + 2, fx0 + 12, fy0 + 19, (150, 146, 140))
    px(d, fx0 + 7, fy0, (200, 60, 50))                                 # 图钉
    # 台子 + 一摞摞报纸
    ty = 124
    rect(d, a + 2, ty, b - 2, ty + 2, WOOD_HI)
    rect(d, a + 2, ty + 3, b - 2, PL_TOP - 1, WOOD)
    for xx in range(a + 4, b - 2, 6):
        vl(d, xx, ty + 4, PL_TOP - 1, WOOD_D)
    hl(d, a + 2, b - 2, ty + 3, WOOD_D)
    x = a + 4
    i = 0
    while x < b - 10:
        w = int(hrange(7, 11, i, 61))
        hgt = int(hrange(4, 9, i, 62))
        for k in range(hgt):
            y = ty - 1 - k
            c = (238, 234, 220) if k % 2 else (216, 210, 196)
            hl(d, x + (k % 2), x + w - 1 - (k % 3 == 0), y, c)
        hl(d, x + 1, x + w - 2, ty - hgt, (246, 244, 236))
        for k in range(1, w - 2, 2):
            px(d, x + k, ty - hgt, (150, 146, 140))
        x += w + 1
        i += 1
    rect(d, b - 8, ty - 7, b - 3, ty - 1, (60, 60, 64))                # 一个装零钱的铁盒
    hl(d, b - 8, b - 3, ty - 7, (110, 110, 116))


# ============================================================ 近景：B5 白灰窄高楼
def draw_b5(im):
    x0, x1 = B5
    facade(im, x0, x1, 8, LANE - 1, LIME, 505, streaks=5)
    d = ImageDraw.Draw(im)
    parapet(im, x0, x1 - 1, 6, LIME, 'arch')
    for (wy, st) in ((16, 'closed'), (46, 'open'), (76, 'half')):
        win_shutter(im, 342, wy, 13, 18, LIME, SHUT_B, st)
        chajja(im, x0, x1 - 1, wy + 22, lt(LIME, 0.2), depth=2)
    d = ImageDraw.Draw(im)
    sign_board(d, x1 - 7, 34, x1 - 2, 70, (40, 90, 150), (250, 240, 200), rows=1, seed=9)   # 竖招牌（色块）
    rect(d, x1 - 6, 36, x1 - 3, 68, (40, 90, 150))
    for yy in range(38, 68, 4):
        hl(d, x1 - 6, x1 - 3, yy, (250, 240, 200))
    door_carved(im, 340, 104, 16, 42, (104, 66, 46), frame=SAND_S, arch=True)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, LANE - 1, SAND_S)


# ============================================================ 近景：B6 青绿两层 + 甜食 / 奶茶铺
SWEETS = (368, 448)
STOVE = (372, 392)            # 泥灶 x
KETTLE = (396, 128)           # 奶茶壶（壶嘴往右上冒热气）


def draw_b6(im):
    x0, x1 = B6
    facade(im, x0, x1, 46, LANE - 1, TEAL, 606, streaks=3)
    d = ImageDraw.Draw(im)
    parapet(im, x0, x1 - 1, 44, TEAL, 'plain')
    d = ImageDraw.Draw(im)
    rect(d, 410, 34, 440, 43, (222, 214, 196))                        # 屋顶小房间
    hl(d, 409, 441, 33, (240, 232, 214))
    rect(d, 414, 37, 418, 43, dk(TEAL, 0.5))
    water_tank(d, 378, 36, 12, 7, (176, 178, 176))
    # 二楼：一整面褪色的手绘广告（蓝底、一个笑脸色块、一个茶杯色块、两行字）+ 右边一扇小窗
    ad = (370, 52, 430, 80)
    lay = A._new(im.width, im.height)
    ld = ImageDraw.Draw(lay)
    rect(ld, ad[0], ad[1], ad[2], ad[3], (70, 110, 176))
    rect(ld, ad[0] + 2, ad[1] + 2, ad[2] - 2, ad[1] + 10, (236, 200, 80))
    sign_board(ld, ad[0] + 3, ad[1] + 3, ad[2] - 3, ad[1] + 9, (236, 200, 80), (176, 40, 40), seed=12,
               border=(236, 200, 80))
    ld.ellipse((ad[0] + 4, ad[1] + 12, ad[0] + 18, ad[1] + 26), fill=C((240, 214, 170)))
    px(ld, ad[0] + 8, ad[1] + 17, (60, 40, 40))
    px(ld, ad[0] + 13, ad[1] + 17, (60, 40, 40))
    hl(ld, ad[0] + 8, ad[0] + 13, ad[1] + 21, (190, 70, 60))
    rect(ld, ad[0] + 26, ad[1] + 15, ad[0] + 36, ad[1] + 25, (240, 240, 232))   # 茶杯
    rect(ld, ad[0] + 37, ad[1] + 17, ad[0] + 39, ad[1] + 21, (240, 240, 232))
    hl(ld, ad[0] + 27, ad[0] + 35, ad[1] + 16, (176, 110, 60))
    sign_board(ld, ad[0] + 42, ad[1] + 13, ad[2] - 3, ad[3] - 3, (70, 110, 176), (250, 250, 240), rows=2, seed=13,
               border=(70, 110, 176))
    a = np.array(lay).astype(np.float32)
    b = np.array(im).astype(np.float32)
    m = a[..., 3] > 0
    n = A._fbm(im.width, im.height, 4, seed=66)
    f = 0.30 + 0.32 * n[m]
    a[m, :3] = a[m, :3] * (1 - f[:, None]) + b[m, :3] * f[:, None]
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))
    win_shutter(im, 436, 58, 10, 16, TEAL, (200, 120, 60), 'open')
    chajja(im, x0, x1 - 1, 86, lt(TEAL, 0.15))
    d = ImageDraw.Draw(im)
    sign_board(d, 370, 90, 446, 97, (250, 196, 60), (170, 30, 40), seed=14)
    shop_dark(im, 370, 100, 446, PL_TOP - 1, 6)
    d = ImageDraw.Draw(im)
    vl(d, 369, 99, PL_TOP - 1, dk(TEAL, 0.7))
    vl(d, 447, 99, PL_TOP - 1, lt(TEAL, 0.2))
    for (bx, c) in ((378, (200, 200, 206)), (386, (210, 170, 90)), (392, (200, 200, 206))):   # 架子上的铝桶 / 铜锅
        rect(d, bx, 106, bx + 5, 113, c)
        hl(d, bx, bx + 5, 106, lt(c, 0.4))
        vl(d, bx + 5, 106, 113, dk(c, 0.7))
    plinth(im, x0 + 1, x1 - 2, seed=6)


def draw_sweets(im):
    """甜食 / 奶茶铺：石台左边一个泥灶（橙红的火口）上一口大黑锅在炸 jalebi（橙色的圈）、灶后一个煤油炉上一把铝壶；
    右边一个木框玻璃柜，里面三层：橙色的 jalebi、黄色的 laddoo 球、白 / 棕的方块甜食；台上一摞陶杯（kulhad）；
    门口一条木长凳。"""
    d = ImageDraw.Draw(im)
    a, b = STOVE
    # 泥灶
    rect(d, a, 126, b, PL_TOP - 1, (176, 112, 76))
    hl(d, a, b, 126, (206, 142, 98))
    vl(d, b, 126, PL_TOP - 1, (140, 86, 60))
    rect(d, a + 6, 130, a + 13, 134, (60, 30, 24))
    rect(d, a + 7, 131, a + 12, 134, (240, 120, 40))
    hl(d, a + 8, a + 11, 133, (255, 210, 90))
    # 大黑锅 + jalebi
    for xx in range(a - 2, b + 3):
        u = (xx - (a - 2)) / (b + 4 - a)
        dep = int(round(4 * math.sin(math.pi * u)))
        vl(d, xx, 123, 123 + dep, (40, 38, 40))
    hl(d, a - 3, b + 3, 122, (90, 88, 92))
    hl(d, a - 1, b + 1, 123, (176, 140, 60))                            # 油面
    for k in range(4):
        cx = a + 3 + k * 5
        for (dx, dy) in ((0, 0), (1, -1), (2, 0), (1, 1)):
            px(d, cx + dx, 122 + dy, (240, 150, 40))
    # 煤油炉 + 铝壶
    kx, ky = KETTLE
    rect(d, kx - 3, ky + 2, kx + 4, PL_TOP - 1, (70, 70, 76))
    hl(d, kx - 3, kx + 4, ky + 2, (110, 110, 118))
    d.ellipse((kx - 4, ky - 6, kx + 4, ky + 2), fill=C((196, 198, 204)))
    hl(d, kx - 2, kx + 1, ky - 5, (236, 238, 242))
    vl(d, kx + 3, ky - 4, ky + 1, (150, 152, 160))
    d.line((kx + 4, ky - 3, kx + 7, ky - 6), fill=C((176, 178, 186)))  # 壶嘴
    d.arc((kx - 3, ky - 10, kx + 3, ky - 4), 180, 360, fill=C((120, 122, 130)))   # 提手
    # 陶杯（kulhad）一摞摞
    for (cx0, n) in ((400, 4), (405, 3)):
        for k in range(n):
            y = PL_TOP - 2 - k * 2
            hl(d, cx0, cx0 + 3, y, (190, 104, 70))
            hl(d, cx0, cx0 + 3, y + 1, (156, 80, 56))
            px(d, cx0, y, (214, 134, 96))
    # 玻璃柜
    g0, g1 = 412, 446
    rect(d, g0, 112, g1, PL_TOP - 1, (100, 70, 48))
    rect(d, g0 + 1, 113, g1 - 1, 133, (70, 80, 86))
    for (sy, kind) in ((114, 'jalebi'), (121, 'laddoo'), (128, 'barfi')):
        hl(d, g0 + 1, g1 - 1, sy + 6, (150, 150, 150))                  # 托盘
        for xx in range(g0 + 2, g1 - 2, 4):
            if kind == 'jalebi':
                for (dx, dy) in ((0, 1), (1, 0), (2, 1), (1, 2), (3, 2)):
                    px(d, xx + dx, sy + 2 + dy, (244, 150, 40) if dx % 2 else (250, 190, 60))
            elif kind == 'laddoo':
                d.ellipse((xx, sy + 2, xx + 3, sy + 5), fill=C((242, 190, 60)))
                px(d, xx + 1, sy + 2, (255, 230, 140))
            else:
                c = (240, 236, 222) if (xx // 4) % 2 else (150, 96, 70)
                rect(d, xx, sy + 3, xx + 2, sy + 5, c)
                px(d, xx, sy + 3, lt(c, 0.3))
    for yy in range(113, 134, 3):                                       # 玻璃反光（斜的亮条）
        px(d, g0 + 3 + (yy - 113) // 3, yy, (210, 226, 236))
        px(d, g0 + 4 + (yy - 113) // 3, yy, (170, 190, 204))
    hl(d, g0, g1, 112, (140, 100, 70))
    vl(d, g1, 112, PL_TOP - 1, (70, 48, 34))
    # 门口的木长凳（在街上，靠墙）
    rect(d, 452 - 30, 140, 452 - 6, 141, WOOD_HI)
    rect(d, 452 - 30, 142, 452 - 6, 142, WOOD_D)
    for lx in (452 - 28, 452 - 9):
        vl(d, lx, 143, LANE + 1, WOOD_D)
    cast_shadow(im, [(452 - 29, LANE + 2), (452 - 5, LANE + 2), (452 - 2, LANE + 4), (452 - 26, LANE + 4)], mul=SOFT_MUL)


def steam_frame(t):
    """奶茶壶嘴冒的热气：两缕连着的白气，从壶嘴往右上飘、左右摆（波往上走），越往上越淡、越稀（8 帧循环）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    sx, sy = KETTLE[0] + 7, KETTLE[1] - 7
    for k in range(2):
        ph = math.tau * f / N_ANIM + k * math.pi
        n = 16 if k == 0 else 12
        for j in range(n):
            v = j / n
            y = sy - 1 - v * 20
            x = sx + v * (5 + k * 2) + (1.0 + 1.6 * v) * math.sin(v * 7.0 - ph)
            if hash01(j, k, f, 7) < v * 0.75:                         # 越往上越稀
                continue
            c = (246, 246, 244) if v < 0.35 else ((226, 228, 230) if v < 0.7 else (204, 208, 212))
            px(d, round(x), round(y), c)
            if v < 0.3:
                px(d, round(x) + 1, round(y), (236, 238, 240))
    return im


# ============================================================ 近景：B7 小神庙
TEMPLE_DOOR = (480, 510)
BELL = (506, 98)


def draw_temple(im):
    """小神庙：围墙刷红白竖条纹（瓦拉纳西的神庙 / 河坛常见）、正中门楼（砂岩、层层线脚、门楣一排小龛），
    三级台阶；门里暗、一盏油灯照着朱红色的神像（神猴哈奴曼：只是色块）；门楣挂一串万寿菊、右边一口大铜铃；
    门楼上是一座砂岩尖塔（shikhara），顶上金宝瓶 + 旗杆（旗子在 strip）。"""
    x0, x1 = B7
    d = ImageDraw.Draw(im)
    wall_top = 82
    for x in range(x0, x1):                                             # 围墙：红白竖条纹
        c = (232, 224, 210) if ((x - x0) // 4) % 2 else (196, 84, 60)
        vl(d, x, wall_top, LANE - 1, c)
    mottle(im, (x0, wall_top, x1 - 1, LANE - 1), (232, 224, 210), (214, 204, 190), (244, 238, 228), 707, cell=4)
    mottle(im, (x0, wall_top, x1 - 1, LANE - 1), (196, 84, 60), (176, 72, 52), (210, 104, 76), 708, cell=4)
    d = ImageDraw.Draw(im)
    vl(d, x0, wall_top, LANE - 1, (246, 240, 232))
    parapet(im, x0, x1 - 1, wall_top - 2, (224, 214, 196), 'arch')
    for (cx, ty) in ((x0 + 9, wall_top - 2), (x1 - 10, wall_top - 2)):   # 围墙两头的小尖顶
        chhatri(im, cx, ty, 12, 9)
    # 门楼（砂岩）
    g0, g1 = 470, 520
    rect(d, g0, 74, g1, LANE - 1, SAND)
    mottle(im, (g0, 74, g1, LANE - 1), SAND, SAND_S, SAND_HI, 709, cell=3)
    d = ImageDraw.Draw(im)
    vl(d, g0, 74, LANE - 1, SAND_HI)
    vl(d, g1, 74, LANE - 1, SAND_D)
    for yy in range(78, LANE - 10, 6):                                  # 砌块缝
        hl(d, g0 + 1, g0 + 7, yy, SAND_S)
        hl(d, g1 - 7, g1 - 1, yy, SAND_S)
    hl(d, g0 - 2, g1 + 2, 74, SAND_HI)
    hl(d, g0 - 2, g1 + 2, 75, SAND_S)
    hl(d, g0 - 1, g1 + 1, 76, SAND_D)
    for k in range(6):                                                  # 门楣一排小龛（每个里面一点朱红）
        nx = g0 + 6 + k * 7
        rect(d, nx, 79, nx + 4, 85, SAND_D)
        hl(d, nx + 1, nx + 3, 78, SAND_D)
        px(d, nx + 2, 82, VERMIL if k % 2 else MARI)
    hl(d, g0 + 2, g1 - 2, 87, SAND_HI)
    hl(d, g0 + 2, g1 - 2, 88, SAND_K)
    # 门框：三道线脚往里收
    a, b = TEMPLE_DOOR
    for k, c in enumerate((SAND_HI, SAND_S, SAND_D)):
        rect(d, a - 6 + k * 2, 92 + k * 2, b + 6 - k * 2, 138, c)
    for yy in range(96, 138, 3):                                        # 门框上的小雕花
        px(d, a - 5, yy, SAND_D)
        px(d, b + 5, yy, SAND_K)
    for yy in range(98, 139):                                            # 门里（暗，下面一点暖光）
        u = (yy - 98) / 40
        hl(d, a, b, yy, mix((34, 26, 28), (70, 50, 42), u))
    cx = (a + b) // 2
    for yy in range(102, 131):                                           # 神像后面的金色背光（拱形）
        u = (yy - 102) / 28
        hw = int(round(8 * min(1.0, (u * 3) ** 0.5)))
        hl(d, cx - hw, cx + hw, yy, (96, 70, 40))
        px(d, cx - hw, yy, (176, 132, 64))
        px(d, cx + hw, yy, (150, 110, 52))
    A._glow(im, cx, 124, 12, 9, (255, 196, 110), 46, rings=3)
    d = ImageDraw.Draw(im)
    # 神像（神猴哈奴曼，只是色块）：通身涂朱砂、银冠、银眼、红衣金边、胸前一挂万寿菊、右边立着一根金色的锤（gada）
    S, Sd = (228, 92, 44), (176, 60, 32)
    d.ellipse((cx - 3, 105, cx + 3, 112), fill=C(S))                     # 头
    rect(d, cx - 2, 103, cx + 2, 105, (214, 214, 220))                   # 银冠
    px(d, cx, 102, (240, 240, 246))
    px(d, cx - 1, 108, (250, 250, 244))                                  # 银眼
    px(d, cx + 1, 108, (250, 250, 244))
    px(d, cx, 110, Sd)
    rect(d, cx - 5, 113, cx + 5, 127, S)                                 # 身子（肩宽）
    vl(d, cx + 5, 113, 127, Sd)
    rect(d, cx - 4, 119, cx + 4, 127, (196, 32, 40))                     # 红衣
    hl(d, cx - 4, cx + 4, 119, GOLD)
    hl(d, cx - 4, cx + 4, 127, GOLD)
    for k, (x, y) in enumerate(((cx - 4, 113), (cx - 3, 115), (cx - 2, 117), (cx - 1, 118), (cx, 118), (cx + 1, 118),
                                (cx + 2, 117), (cx + 3, 115), (cx + 4, 113))):   # 花环（U 形）
        px(d, x, y, MARI if k % 2 else MARI_HI)
    vl(d, cx + 8, 112, 128, GOLD_D)                                      # 锤
    d.ellipse((cx + 6, 108, cx + 10, 113), fill=C(GOLD))
    px(d, cx + 7, 109, GOLD_HI)
    rect(d, cx - 7, 128, cx + 7, 131, (120, 96, 72))                     # 台座
    hl(d, cx - 7, cx + 7, 128, (160, 132, 100))
    for (lx, fl) in ((cx - 11, 0), (cx + 11, 1)):                        # 两盏铜油灯（灯座 + 火苗）
        vl(d, lx, 124, 133, GOLD_D)
        hl(d, lx - 2, lx + 2, 133, GOLD_D)
        hl(d, lx - 2, lx + 2, 123, GOLD)
        px(d, lx, 121, (255, 236, 160))
        px(d, lx, 122, (255, 190, 80))
    for bx in (a + 3, b - 3):                                            # 门里挂的小铃
        vl(d, bx, 98, 101, (90, 74, 50))
        rect(d, bx - 1, 102, bx + 1, 103, GOLD_D)
    # 台阶（三级，越往下越宽）
    for k in range(3):
        y = 138 + k * 3
        rect(d, a - 8 - k * 4, y, b + 8 + k * 4, y + 2, SAND_S)
        hl(d, a - 8 - k * 4, b + 8 + k * 4, y, SAND_HI)
        vl(d, b + 8 + k * 4, y, y + 2, SAND_D)
        for xx in range(a - 6 - k * 4, b + 8 + k * 4, 2):              # 台阶上的花瓣
            if hash01(xx, k, 77) < 0.12:
                px(d, xx, y + 1, MARI)
    # 门楣上的铜铃挂钩（铃在 strip 里也画，这里画固定的那口小铃 + 铃绳）
    bx, by = BELL
    vl(d, bx, 92, by - 2, (90, 70, 50))
    # 尖塔
    top = shikhara(im, 495, 73, 22, 21, minis=True)
    assert tuple(top) == TEMPLE_FLAG, top
    d = ImageDraw.Draw(im)
    for k in range(3):                                                   # 尖塔上挂的旧花串、涂的一道朱红
        hl(d, 488 + k, 502 - k, 60 + k * 9, VERMIL if k == 1 else lt(SAND, 0.2))


def draw_temple_bell(d):
    bx, by = BELL
    d.ellipse((bx - 3, by - 2, bx + 3, by + 5), fill=C(GOLD))
    rect(d, bx - 3, by + 2, bx + 3, by + 5, GOLD)
    hl(d, bx - 4, bx + 4, by + 5, GOLD_D)
    px(d, bx - 2, by, GOLD_HI)
    vl(d, bx - 2, by + 1, by + 3, GOLD_HI)
    vl(d, bx + 2, by, by + 4, GOLD_D)
    px(d, bx, by + 6, (120, 90, 40))


# ============================================================ 近景：B8 赭红三层 + 猴子
def draw_b8(im):
    x0, x1 = B8
    facade(im, x0, x1, 18, LANE - 1, TERRA, 808, streaks=4)
    d = ImageDraw.Draw(im)
    parapet(im, x0, x1 - 1, 16, TERRA, 'post')
    for wy in (26, 60):
        win_arch(im, 542, wy, 10, 22, TERRA, (236, 214, 190), seed=wy)
        win_arch(im, 558, wy, 10, 22, TERRA, (236, 214, 190), seed=wy + 1)
        chajja(im, x0, x1 - 1, wy + 25, lt(TERRA, 0.12), depth=2)
    brick_patch(im, 556, 96, 12, 10, 9)
    d = ImageDraw.Draw(im)
    rect(d, 542, 104, 566, LANE - 1, DARK_IN)                            # 一层：小门洞（暗）+ 一辆靠着的自行车
    door_carved(im, 545, 106, 18, 40, (96, 60, 44), frame=lt(TERRA, 0.25), studs=True)
    d = ImageDraw.Draw(im)
    poster(im, 538, 112, 6, 9, 21)
    poster(im, 566, 116, 6, 8, 25)
    # 猴子（坐在二楼窗台上，尾巴垂下来）
    mx, my = 556, 84
    mc, md = (150, 120, 96), (110, 86, 70)
    rect(d, mx, my - 6, mx + 4, my, mc)
    d.ellipse((mx, my - 10, mx + 4, my - 6), fill=C(mc))
    px(d, mx + 1, my - 8, (220, 170, 150))
    px(d, mx + 2, my - 8, (220, 170, 150))
    px(d, mx + 1, my - 9, (30, 20, 20))
    px(d, mx + 3, my - 9, (30, 20, 20))
    vl(d, mx + 4, my - 4, my, md)
    for k in range(9):
        px(d, mx + 5 + (k > 5), my + 1 + k, md)
    vl(d, mx + 1, my + 1, my + 2, md)
    vl(d, mx + 3, my + 1, my + 2, md)


# ============================================================ 近景：通往河坛的门洞
def arch_top(x):
    """门洞的尖拱：x → 拱内沿的 y（ARCH 之外返回 None）。"""
    a, b = ARCH
    if not (a <= x <= b):
        return None
    cx = (a + b) / 2
    hw = (b - a) / 2
    u = min(1.0, abs(x + 0.5 - cx) / (hw + 0.5))
    rise = ARCH_SPRING - ARCH_TOP
    return int(round(ARCH_SPRING - rise * (1 - u ** 1.7) ** 0.62))


RIVER_BOX = (ARCH[0], 100, ARCH[1] + 1, 122)
RIVER_Y = (106, 121)          # 门洞里看得见的河面


def draw_vista(im):
    """门洞里的远景：天（淡）、对岸的沙洲（一条白沙 + 几棵小树）、河（亮、反光）、一条小船，下面一级级往下的石阶
    （近的宽、远的窄，越往下越亮），两边是夹着石阶的房子侧墙（暗、往里收）。"""
    a, b = ARCH
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    gradient(lay, (a, ARCH_TOP, b + 1, 104), [(150, 192, 228), (200, 218, 232), (236, 230, 214)], bands=5)
    rect(d, a, 102, b, 105, (234, 222, 190))                              # 对岸沙洲
    hl(d, a, b, 102, (246, 238, 214))
    for tx in (a + 6, a + 9, b - 12):
        rect(d, tx, 99, tx + 1, 101, (120, 140, 110))
    gradient(lay, (a, RIVER_Y[0], b + 1, RIVER_Y[1] + 1), [(196, 214, 222), (150, 182, 196), (120, 156, 168)], bands=5)
    hl(d, a, b, RIVER_Y[0], (236, 240, 236))
    bx = a + 20                                                           # 远处一条小船（剪影）
    hl(d, bx, bx + 7, 110, (80, 64, 54))
    hl(d, bx + 1, bx + 6, 111, (100, 80, 66))
    vl(d, bx + 4, 106, 109, (90, 74, 60))
    # 石阶（从 146 往上到 122：近的高、远的矮）
    y = LANE - 1
    hs = [4, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1]
    k = 0
    while y > RIVER_Y[1]:
        h = hs[min(k, len(hs) - 1)]
        top = max(RIVER_Y[1] + 1, y - h + 1)
        rect(d, a, top, b, y, mix(SAND_HI, SAND, 0.3 + 0.05 * k))
        hl(d, a, b, top, lt(SAND_HI, 0.15))
        if y - top >= 2:
            hl(d, a, b, y, mix(SAND_S, SAND, 0.4))
        y = top - 1
        k += 1
    # 两边夹着的墙（往里收）
    for yy in range(ARCH_TOP, LANE):
        u = max(0.0, (LANE - yy) / (LANE - RIVER_Y[0]))
        wl = int(round(6 - 3 * min(1.0, u)))
        wr = int(round(8 - 4 * min(1.0, u)))
        hl(d, a, a + wl, yy, dk(SAND_S, 0.66))
        hl(d, b - wr, b, yy, dk(SAND, 0.82))
        px(d, a + wl, yy, dk(SAND_S, 0.5))
        px(d, b - wr, yy, lt(SAND, 0.1))
    # 只留门洞里
    m = np.zeros((H, PW), bool)
    for x in range(a, b + 1):
        top = arch_top(x)
        if top is not None:
            m[top:LANE, x] = True
    arr = np.array(lay)
    arr[~m] = 0
    im.alpha_composite(Image.fromarray(arr, 'RGBA'))
    return m


def draw_gate(im):
    """门楼（砂岩）：拱两边的墩子、拱上的雕花横带 + 挑檐 + 一扇小窗，顶上一座小亭子；拱的内沿一圈线脚；
    门右边墙上刷着一块指向河坛的牌子（白底红字 + 箭头，色块），左墩上一个小龛点着油灯。"""
    x0, x1 = GATE
    d = ImageDraw.Draw(im)
    top = 40
    rect(d, x0, top, x1 - 1, LANE - 1, SAND)
    mottle(im, (x0, top, x1 - 1, LANE - 1), SAND, SAND_S, SAND_HI, 909, cell=3, streaks=3)
    d = ImageDraw.Draw(im)
    for yy in range(top + 6, LANE, 7):                                    # 砌块缝
        off = 0 if (yy // 7) % 2 else 6
        hl(d, x0 + 1, x1 - 1, yy, dk(SAND, 0.9))
        for xx in range(x0 + off, x1, 12):
            vl(d, xx, yy - 6, yy - 1, dk(SAND, 0.92))
    vl(d, x0, top, LANE - 1, SAND_HI)
    # 拱洞 + 拱沿线脚
    m = draw_vista(im)
    d = ImageDraw.Draw(im)
    a, b = ARCH
    for x in range(a - 3, b + 4):
        t0 = arch_top(min(max(x, a), b))
        if t0 is None:
            continue
        if x < a or x > b:
            continue
        px(d, x, t0 - 1, SAND_D)
        px(d, x, t0 - 2, SAND_HI)
        px(d, x, t0 - 3, SAND_S)
    for yy in range(ARCH_SPRING, LANE):
        vl(d, a - 1, yy, yy, SAND_D)
        vl(d, a - 2, yy, yy, SAND_HI)
        vl(d, b + 1, yy, yy, SAND_K)
        vl(d, b + 2, yy, yy, SAND_S)
    hl(d, a - 4, a - 1, ARCH_SPRING - 1, SAND_HI)                         # 起拱处的小托
    hl(d, b + 1, b + 4, ARCH_SPRING - 1, SAND_HI)
    hl(d, a - 4, b + 4, LANE - 1, SAND_S)                                  # 门槛
    hl(d, a - 4, b + 4, LANE - 2, SAND_HI)
    # 拱上的雕花横带 + 挑檐
    for xx in range(x0 + 1, x1):
        if (xx - x0) % 4 == 0:
            px(d, xx, 60, SAND_D)
            px(d, xx + 1, 61, SAND_D)
        else:
            px(d, xx, 61, SAND_HI)
    hl(d, x0, x1 - 1, 63, SAND_K)
    chajja(im, x0 - 2, x1 - 1, 52, SAND_HI)
    d = ImageDraw.Draw(im)
    for xx in range(x0 + 2, x1 - 2, 5):                                    # 挑檐下的小托架
        vl(d, xx, 55, 57, SAND_D)
    sign_board(d, 588, 42, 626, 50, (244, 232, 200), (150, 36, 40), seed=31, border=(150, 36, 40))   # 河坛的名字（色块）
    px(d, 591, 46, VERMIL)
    px(d, 623, 46, VERMIL)
    mul_box(im, (589, 51, 627, 51), SHADOW_MUL)
    d = ImageDraw.Draw(im)
    # 女儿墙 + 顶上的小亭子
    parapet(im, x0, x1 - 1, top - 2, SAND, 'arch')
    chhatri(im, 607, top - 2, 18, 12)
    for cx in (x0 + 4, x1 - 5):                                             # 两角的小尖
        im2 = ImageDraw.Draw(im)
        rect(im2, cx - 1, top - 8, cx + 1, top - 3, SAND)
        px(im2, cx, top - 9, GOLD)
    d = ImageDraw.Draw(im)
    # 左墩上的小龛 + 油灯
    rect(d, 577, 108, 583, 118, (70, 50, 44))
    hl(d, 578, 582, 107, (70, 50, 44))
    px(d, 580, 116, (255, 230, 140))
    px(d, 580, 115, (255, 196, 90))
    hl(d, 576, 584, 119, SAND_HI)
    # 门右边墙上刷的指路：白灰底 + 一行字（色块）+ 往左（门洞）指的黑箭头
    sx0, sy0 = 630, 98
    rect(d, sx0, sy0, x1 - 1, sy0 + 13, (240, 234, 220))
    hl(d, sx0, x1 - 1, sy0, (250, 246, 236))
    hl(d, sx0 + 1, x1 - 2, sy0 + 3, (40, 36, 40))
    for xx in range(sx0 + 1, x1 - 1, 2):
        px(d, xx, sy0 + 4, (40, 36, 40))
    hl(d, sx0 + 3, x1 - 2, sy0 + 9, (40, 36, 40))                           # 箭杆
    for k in range(3):                                                       # 箭头（朝左）
        vl(d, sx0 + 1 + k, sy0 + 9 - k, sy0 + 9 + k, (40, 36, 40))
    return m


def river_frame(t):
    """门洞里的河面波光：一闪一闪的亮点 + 短横（8 帧循环），只在露出来的河面上。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    vm = vista_mask()
    for i in range(26):
        y = RIVER_Y[0] + 1 + int(hash01(i, 311) ** 0.8 * (RIVER_Y[1] - RIVER_Y[0] - 1))
        x = int(hrange(ARCH[0], ARCH[1], i, 312))
        ph = (f / N_ANIM + hash01(i, 313)) % 1.0
        if ph > 0.55:
            continue
        L = 1 + int((y - RIVER_Y[0]) / 6) + (1 if ph < 0.2 else 0)
        c = (255, 252, 236) if ph < 0.25 else (226, 236, 236)
        for xx in range(x, x + L):
            if 0 <= xx < PW and vm[y, xx]:
                px(d, xx, y, c)
    return im


# ============================================================ 近景：电线杆 / 电线 / 纸旗 / 花串
def draw_poles(im):
    d = ImageDraw.Draw(im)
    p1, p2 = POLES
    # 1 水泥杆（灰）+ 路灯 + 横担 + 绝缘子 + 一个接线盒
    for y in range(14, LANE + 1):
        u = (y - 14) / (LANE - 14)
        w = 2 if u < 0.5 else 3
        for k in range(w):
            c = (196, 192, 184) if k == 0 else ((160, 156, 150) if k < w - 1 else (122, 118, 114))
            px(d, p1 - 1 + k, y, c)
    for (yy, hw) in ((18, 8), (26, 6)):
        hl(d, p1 - hw, p1 + hw, yy, (110, 104, 100))
        for xx in (p1 - hw, p1 + hw):
            px(d, xx, yy - 1, (236, 236, 228))
    rect(d, p1 + 2, 60, p1 + 6, 68, (130, 130, 126))                    # 接线盒
    hl(d, p1 + 2, p1 + 6, 60, (170, 170, 166))
    d.line((p1, 34, p1 - 10, 30), fill=C((90, 90, 90)))                 # 路灯臂 + 灯罩
    rect(d, p1 - 14, 29, p1 - 9, 31, (80, 80, 84))
    hl(d, p1 - 13, p1 - 10, 32, (250, 246, 220))
    for k in range(5):                                                   # 杆上缠的一圈电线
        px(d, p1 - 2, 80 + k * 2, (40, 40, 44))
        px(d, p1 + 2, 81 + k * 2, (40, 40, 44))
    # 2 铁杆（墨绿）+ 横担 + 喇叭
    for y in range(18, LANE + 1):
        px(d, p2 - 1, y, (76, 96, 86))
        px(d, p2, y, (52, 70, 62))
        px(d, p2 + 1, y, (36, 50, 44))
    hl(d, p2 - 9, p2 + 9, 22, (52, 70, 62))
    hl(d, p2 - 7, p2 + 7, 30, (52, 70, 62))
    for xx in (p2 - 9, p2 - 3, p2 + 3, p2 + 9):
        px(d, xx, 21, (236, 236, 228))
    for k in range(6):                                                   # 喇叭（朝左，往外张）
        vl(d, p2 - 2 - k, 40 - k // 2, 43 + k // 2, (190, 190, 196) if k < 5 else (120, 120, 126))
    rect(d, p2 - 1, 39, p2, 44, (90, 90, 96))
    rect(d, p2 + 2, 88, p2 + 5, 96, (176, 176, 170))                    # 一块搪瓷牌
    hl(d, p2 + 2, p2 + 5, 90, VERMIL)
    hl(d, p2 + 2, p2 + 5, 93, VERMIL)
    # 电线：两根杆之间、杆到屋顶、从左边进来、往右边出去
    WC = (44, 40, 44)
    for (ya, yb, sag) in ((18, 22, 16), (18, 21, 20), (26, 30, 12), (26, 30, 22)):
        wire(d, p1 - 8 + (ya - 18), ya, p2 - 9 + (yb - 21), yb, sag, WC)
    for (x0, y0, x1, y1, sag) in ((0, 30, p1 - 8, 18, 6), (0, 22, p1 + 8, 18, 9), (p1 + 6, 26, 200, 52, 4),
                                  (p1 - 6, 26, 98, 20, 3), (p1, 34, 46, 60, 6), (p2 + 9, 21, PW, 14, 8),
                                  (p2 + 7, 30, 586, 44, 7), (p2 - 7, 30, 360, 10, 5), (p2 + 3, 21, 536, 18, 3),
                                  (p1 + 2, 62, 252, 64, 8), (p2 - 2, 60, 330, 92, 10)):
        wire(d, x0, y0, x1, y1, sag, WC)
    for (x0, y0, x1) in ((B1[0] + 2, 95, B1[1] - 2), (B2[0] + 2, 88 + 10, B4[1] - 2), (B6[0], 98, B7[0] - 2)):
        wire(d, x0, y0, x1, y0, 1, (60, 56, 60))                        # 墙上沿着钉的线


BUNTING = [  # (x0, y0, x1, y1, 垂度, 种子)：沿街垂着的两串三角纸旗
    (138, 58, 268, 64, 12, 1),
    (372, 56, 470, 60, 10, 2),
]
BUNT_BOXES = [('bunt_a', (136, 54, 272, 84)), ('bunt_b', (370, 52, 474, 76))]
GARLAND_BOX = (206, 62, 636, 108)


def bunting_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    for (x0, y0, x1, y1, sag, sd) in BUNTING:
        pts = garland_pts(x0, y0, x1, y1, sag)
        d.line([(round(x), round(y)) for (x, y) in pts], fill=C((230, 228, 220)))
        for k, i in enumerate(range(2, len(pts) - 2, 6)):
            x, y = pts[i]
            ph = math.tau * f / N_ANIM + k * 0.8 + sd
            sw = math.sin(ph)
            col = ((226, 60, 70), (250, 200, 60), (70, 140, 210), (80, 180, 110), (240, 130, 180), (250, 150, 50))[
                (k + sd) % 6]
            tipx = round(x + 1 + sw * 1.2)
            for r in range(5):                                         # 三角旗：上宽下尖，往一边摆
                hw = 2 - r // 2
                ox = round(sw * 1.2 * r / 4)
                hl(d, round(x) - hw + 1 + ox, round(x) + hw + 1 + ox, round(y) + 1 + r, col if r < 4 else dk(col, 0.8))
            px(d, tipx, round(y) + 6, dk(col, 0.7))
    return im


def garlands_frame(t):
    """神龛 / 神庙门 / 门洞的花串，铜铃（铃身跟着轻轻晃）。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    sw = math.sin(math.tau * f / N_ANIM)
    sw2 = math.sin(math.tau * f / N_ANIM + 1.3)
    # 神龛上的一小串
    draw_garland(d, 210, 100, 220, 100, 4, dx=sw * 0.8, seed=1, thick=False)
    # 神庙门楣：横着一串 + 垂下来的几条（toran）
    a, b = TEMPLE_DOOR
    draw_garland(d, a - 6, 91, b + 6, 91, 3, dx=sw * 0.6, seed=2)
    for k, xx in enumerate(range(a - 4, b + 6, 5)):
        hang_garland(d, xx, 93, 5 + (k % 2) * 3, dx=sw * (0.6 + 0.2 * (k % 3)), seed=k)
    # 铜铃（挂在门楣右边）
    bx, by = BELL
    lay = A._new(PW, H)
    draw_temple_bell(ImageDraw.Draw(lay))
    off = round(sw2 * 1.0)
    paste(im, lay.crop((bx - 5, by - 3, bx + 6, by + 8)), bx - 5 + off, by - 3)
    d = ImageDraw.Draw(im)
    # 门洞拱上挂的花串（两段弧）+ 拱两边垂下的两条
    a2, b2 = ARCH
    draw_garland(d, a2 - 3, ARCH_SPRING - 2, (a2 + b2) // 2, ARCH_TOP - 4, 5, dx=sw2 * 0.8, seed=3)
    draw_garland(d, (a2 + b2) // 2, ARCH_TOP - 4, b2 + 3, ARCH_SPRING - 2, 5, dx=sw2 * 0.8, seed=4)
    hang_garland(d, a2 - 3, ARCH_SPRING, 10, dx=sw2 * 0.8, seed=5)
    hang_garland(d, b2 + 3, ARCH_SPRING, 10, dx=sw2 * 0.8, seed=6)
    # 牛脖子上的花环不动（在牛图里）
    return im


FLAG_BOX = (494, 5, 510, 20)


def flag_frame(t):
    """尖塔顶的藏红色三角旗（带一道深色边）：顺风往右飘、波一下。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    gx, gy = TEMPLE_FLAG
    for i in range(1, 13):
        u = i / 12
        wav = 1.3 * math.sin(math.tau * f / N_ANIM - u * 4.2) * u
        hh = int(round(5 * (1 - u) + 1))
        y0 = round(gy + 1 + wav + u * 1.5)
        for r in range(hh):
            c = SAFFRON if r < hh - 1 else dk(SAFFRON, 0.75)
            if wav > 0.5 and r == 0:
                c = lt(SAFFRON, 0.25)
            px(d, gx + i, y0 + r, c)
    return im


COW_TAIL = (COW_XY[0] + 40, COW_XY[1] + 9)
COW_BOX = (COW_XY[0] + 8, COW_XY[1] + 3, COW_XY[0] + 48, COW_XY[1] + 20)


def cow_frame(t):
    """牛：尾巴甩（从屁股垂到地上的一段在摆）+ 耳朵偶尔动一下。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = int(math.floor(t * FPS_ANIM + 1e-6)) % N_ANIM
    cow_tail(d, COW_TAIL[0], COW_TAIL[1], f)
    ex, ey = COW_XY[0] + 12, COW_XY[1] + 7                              # 耳朵尖：第 2、3 帧抖起来
    if f in (2, 3):
        px(d, ex, ey - 2, COW_W2)
        px(d, ex + 1, ey - 2, (190, 160, 150))
    else:
        px(d, ex, ey + 1, COW_W4)
        px(d, ex + 1, ey + 1, COW_W4)
    return im


STEAM_BOX = (KETTLE[0] + 4, KETTLE[1] - 32, KETTLE[0] + 18, KETTLE[1] - 5)


# ============================================================ 前景（人前面，k 1.25）：镜头前头顶的电线
@lru_cache(maxsize=1)
def fg_img():
    im = A._new(FGW, 34)
    d = ImageDraw.Draw(im)
    WC = (30, 28, 32)
    for (x0, y0, x1, y1, sag) in ((-10, 2, 330, 8, 14), (250, 0, 730, 6, 18), (420, 10, 730, 0, 8)):
        wire(d, x0, y0, x1, y1, sag, WC)
    for (cx, cy) in ((150, 18), (560, 16)):                                # 两团缠在一起的线
        for k in range(10):
            a = k * 0.7
            px(d, round(cx + 4 * math.cos(a)), round(cy + 2 * math.sin(a * 1.3)), WC)
        for k in range(8):
            px(d, cx + (k % 3) - 1, cy + 2 + k, WC)
    return opaque(im)


# ============================================================ 组装
@lru_cache(maxsize=1)
def near_parts():
    """返回 (整条街, 门洞里能看到远景的那片 mask)。"""
    im = A._new(PW, H)
    draw_ground(im)
    draw_side_lane(im)
    draw_b1(im)
    draw_b2(im)
    draw_b3(im)
    draw_b4(im)
    draw_b5(im)
    draw_b6(im)
    draw_temple(im)
    draw_b8(im)
    m = draw_gate(im)
    draw_poles(im)
    draw_tree(im)
    draw_fruit_stall(im)
    draw_police_booth(im)
    draw_cow(im)
    draw_news_stall(im)
    draw_sweets(im)
    draw_props(im)
    draw_shadows(im)
    im = A._grade(im, sat=0.98, val=1.0)
    return opaque(im), m


def draw_props(im):
    """街边的小东西（都贴着墙脚，不挡路）：B8 墙边靠着的一辆黑色老自行车、神庙台阶下脱的几双拖鞋、
    B5 门边一摞陶水罐（matka）、B3 门边的铜水壶 + 铁桶。"""
    d = ImageDraw.Draw(im)
    # 自行车（朝左，靠墙）
    bx, by = 544, 139
    for wx in (bx, bx + 17):
        d.ellipse((wx - 6, by - 6, wx + 6, by + 6), outline=C((40, 38, 42)))
        d.ellipse((wx - 5, by - 5, wx + 5, by + 5), outline=C((110, 108, 112)))
        px(d, wx, by, (150, 150, 156))
    BK = (36, 34, 40)
    d.line((bx, by, bx + 7, by - 9), fill=C(BK))                       # 前叉 → 车头
    d.line((bx + 7, by - 9, bx + 15, by - 8), fill=C(BK))              # 上梁
    d.line((bx + 8, by - 5, bx + 13, by), fill=C(BK))                  # 下梁 → 中轴
    d.line((bx + 13, by, bx + 17, by), fill=C(BK))                     # 后下叉
    d.line((bx + 15, by - 8, bx + 17, by), fill=C(BK))                 # 后上叉
    d.line((bx + 15, by - 8, bx + 13, by), fill=C(BK))                 # 立管
    hl(d, bx + 12, bx + 17, by - 10, (60, 46, 40))                     # 车座
    d.line((bx + 7, by - 9, bx + 5, by - 13), fill=C(BK))              # 车把
    hl(d, bx + 3, bx + 7, by - 13, (90, 90, 96))
    rect(d, bx + 16, by - 9, bx + 22, by - 8, (70, 66, 60))            # 后座架
    cast_shadow(im, [(bx - 4, LANE), (bx + 24, LANE), (bx + 28, LANE + 3), (bx, LANE + 3)], mul=SOFT_MUL)
    d = ImageDraw.Draw(im)
    # 神庙台阶下的拖鞋
    for (x, c) in ((462, (60, 50, 46)), (467, (196, 60, 50)), (523, (70, 110, 160)), (528, (90, 70, 50))):
        hl(d, x, x + 2, LANE + 1, c)
        hl(d, x + 1, x + 3, LANE + 2, dk(c, 0.8))
    # 陶水罐（matka）
    for (x, y, r) in ((336, 141, 3), (337, 136, 2)):
        d.ellipse((x - r, y - r, x + r, y + r), fill=C((180, 96, 62)))
        px(d, x - 1, y - r + 1, (214, 134, 96))
        hl(d, x - 1, x + 1, y - r - 1, (150, 76, 50))
    # 铜水壶 + 铁桶
    d.ellipse((246, 140, 250, 145), fill=C(GOLD_D))
    px(d, 247, 141, GOLD_HI)
    hl(d, 247, 249, 139, GOLD)
    rect(d, 241, 139, 245, 145, (150, 156, 160))
    hl(d, 241, 245, 139, (196, 200, 204))
    vl(d, 245, 139, 145, (110, 114, 120))


def draw_shadows(im):
    """立在街上 / 石台上的东西往右下的淡影（压在街面最上面几行）。"""
    for x in POLES:
        cast_shadow(im, [(x + 1, LANE), (x + 4, LANE), (x + 8, LANE + 5), (x + 5, LANE + 5)], mul=SOFT_MUL)
    for (a, b) in ((B1[0] + 1, B1[1] - 2), (B4[0] + 1, B4[1] - 2), (B6[0] + 1, B6[1] - 2), (2, 44)):
        cast_shadow(im, [(a + 3, LANE), (b + 1, LANE), (b + 5, LANE + 3), (a + 6, LANE + 3)], mul=SOFT_MUL)


TEMPLE_FLAG = (495, 8)        # 旗杆顶（draw_temple 里用 shikhara 的返回值核对）


def near_img():
    return near_parts()[0]


@lru_cache(maxsize=1)
def vista_mask():
    return near_parts()[1]


STRIPS = [('bunt_a', BUNT_BOXES[0][1], N_ANIM, FPS_ANIM, bunting_frame),
          ('bunt_b', BUNT_BOXES[1][1], N_ANIM, FPS_ANIM, bunting_frame),
          ('garlands', GARLAND_BOX, N_ANIM, FPS_ANIM, garlands_frame),
          ('flag', FLAG_BOX, N_ANIM, FPS_ANIM, flag_frame),
          ('steam', STEAM_BOX, N_ANIM, FPS_ANIM, steam_frame),
          ('cow', COW_BOX, N_ANIM, FPS_ANIM, cow_frame),
          ('river', RIVER_BOX, N_ANIM, FPS_ANIM, river_frame)]


@lru_cache(maxsize=1)
def build():
    near, _ = near_parts()
    fg = fg_img()
    bb = fg.getbbox()
    return dict(sky=sky_img(), clouds=clouds_img(), far=far_img(), mid=mid_img(), near=near,
                fg=fg.crop(bb), fg_xy=(bb[0], bb[1]))


def compose(camX, t=0.5, fg=True):
    """直接拼一帧（不经导出），自检 / 预览用。"""
    R = build()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    out.alpha_composite(R['sky'])
    o = int(math.floor(camX * CLOUD_K + t * CLOUD_VX)) % 640
    cl = _tile(R['clouds'], 1280)
    paste(out, cl.crop((o, 0, o + W, cl.height)), 0, 0)
    for key, k in (('far', FAR_K), ('mid', MID_K)):
        ox = math.floor(camX * k)
        out.alpha_composite(R[key].crop((ox, 0, ox + W, H)))
        if key == 'mid':
            bird = kite_bird_img()
            for (y, vx, kk, x0) in KITES:
                x = (x0 + t * vx - camX * kk) % 460 - 100
                paste(out, bird, math.floor(x), y)
            pg = pigeons_frame(t).crop(PIGEON_BOX)
            paste(out, pg, PIGEON_BOX[0] - math.floor(camX * MID_K), PIGEON_BOX[1])
    out.alpha_composite(R['near'].crop((camX, 0, camX + W, H)))
    for (name, box, n, fps, fn) in STRIPS:
        paste(out, fn(t).crop(box), box[0] - camX, box[1])
    if fg:
        fx, fy = R['fg_xy']
        paste(out, R['fg'], fx - math.floor(camX * FG_K), fy)
    return out


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    layers = [dict(type='static', image=ex.img('sky', R['sky']), x=0, y=0)]
    cim, cy = BJ.crop_rows(R['clouds'])
    layers.append(dict(type='wrap', image=ex.img('clouds', BJ.tile_to(cim, 640, 640 + W)), period=640, k=CLOUD_K, y=cy,
                       vx=CLOUD_VX))
    for key, k in (('far', FAR_K), ('mid', MID_K)):
        im, y = BJ.crop_rows(R[key])
        layers.append(dict(type='pano', image=ex.img(key, im), k=k, x=0, y=y))
    bk = ex.img('kite_bird', kite_bird_img())
    layers.append(dict(type='clouds', span=460, clouds=[dict(image=bk, x0=float(x0), y=y, vx=vx, k=k)
                                                       for (y, vx, k, x0) in KITES]))
    layers.append(ex.bake('pigeons', PIGEON_BOX, N_ANIM, FPS_ANIM, pigeons_frame, screen=False, k=MID_K))
    nim, ny = BJ.crop_rows(R['near'])
    layers.append(dict(type='pano', image=ex.img('near', nim), k=1.0, x=0, y=ny))
    for (name, box, n, fps, fn) in STRIPS:
        layers.append(ex.bake(name, box, n, fps, fn, screen=False, k=1.0))
    fx, fy = R['fg_xy']
    fg = [dict(type='pano', image=ex.img('fg', R['fg']), k=FG_K, x=fx, y=fy)]
    anchors = dict(ANCHORS)
    anchors.update(fruit_box=[FRUIT[0], 86, FRUIT[1] + 1, PL_TOP],
                   police_box=[POLICE[0] - 3, 88, POLICE[1] + 4, LANE],
                   newspaper_box=[NEWS[0] - 2, 92, NEWS[1] + 3, PL_TOP],
                   front_page=[NEWS[0] + 24, 100, NEWS[0] + 40, 121],
                   sweets_box=[SWEETS[0], 90, SWEETS[1] - 1, PL_TOP],
                   temple_door=[TEMPLE_DOOR[0], 98, TEMPLE_DOOR[1] + 1, 138],
                   ghat_arch=[ARCH[0], ARCH_TOP, ARCH[1] + 1, LANE],
                   cow=[COW_XY[0] + 17, COW_XY[1] + 13],
                   shrine_niche=[215, 110], lane_back=LANE)
    st = ex.stage(PW, GROUND, WALK, layers, fg, anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


STAND = ('arrive', 'fruit', 'police', 'newspaper', 'sweets', 'temple', 'ghat_stairs')


def _checks(ex, BJ, st, R):
    imgs = ex.images
    cams = list(range(0, PW - W + 1, 40))
    bad = 0
    for camX in cams:
        for t in (0.0, 0.75, 1.5):
            im = np.array(BJ.ref_render(st, imgs, camX, t, {}).convert('RGB'))
            bad += int((im.sum(-1) == 0).sum())
    ex.checked('瓦拉纳西窄街 镜头 0–320（每 40）× 3 个时刻 整屏都有画（没有露黑）', bad)
    ex.checked('天空底图整张不透明', int((np.array(R['sky'])[..., 3] != 255).sum()))
    a = np.array(R['near'])
    ex.checked('近景 街面（y 146–180）整条不透明', int((a[LANE:, :, 3] != 255).sum()))
    ex.checked('近景只有 0 / 255 两种透明度', int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum()))
    fa = np.array(R['fg'])
    ex.checked('前景只有 0 / 255 两种透明度、只在画面上沿（y < 34）',
               int(((fa[..., 3] > 0) & (fa[..., 3] < 255)).sum()) + int(R['fg_xy'][1] + R['fg'].height > 34))
    # strip 闭合 + 帧条宽 + 每帧在动
    for (name, box, n, fps, fn) in STRIPS + [('pigeons', PIGEON_BOX, N_ANIM, FPS_ANIM, pigeons_frame)]:
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
    # 画的东西都在框里（同一个帧函数的几个 strip 合起来算：框外有画 = 那部分会丢）
    fns = {}
    for (name, box, n, fps, fn) in STRIPS + [('pigeons', PIGEON_BOX, N_ANIM, FPS_ANIM, pigeons_frame)]:
        fns.setdefault(fn, []).append((name, box, n, fps))
    for fn, items in fns.items():
        lost = 0
        n, fps = items[0][2], items[0][3]
        for i in range(n):
            a = np.array(fn(i / fps))[..., 3] > 0
            for (_, box, _, _) in items:
                a[box[1]:box[3], box[0]:box[2]] = False
            lost += int(a.sum())
        ex.checked('strip %s 每帧画的东西都在框里（框外的像素）' % '+'.join(it[0] for it in items), lost)
    # 锚点
    out = 0
    wx = ANCHORS['walk_x']
    for k, v in ANCHORS.items():
        if k == 'walk_x':
            out += not (0 <= v[0] < v[1] <= PW)
        else:
            out += not (0 <= v[0] <= PW and 0 <= v[1] <= H)
            if k in STAND:
                out += not (WALK[0] <= v[1] <= WALK[1] and wx[0] <= v[0] <= wx[1])
    for k in ('fruit_box', 'police_box', 'newspaper_box', 'front_page', 'sweets_box', 'temple_door', 'ghat_arch'):
        b = st['anchors'][k]
        out += not (0 <= b[0] < b[2] <= PW and 0 <= b[1] < b[3] <= H)
    ex.checked('锚点都在地图里、站人的锚点在可走带 / walk_x 里（不满足的条数）', out)
    # 调查点的东西真的画在那：石榴筐里红的够多、头版里有报头的黑条、门洞里有亮的河
    fb = np.array(R['near'].crop((FRUIT[1] - 22, 112, FRUIT[1] + 2, 134))).astype(int)
    red = int(((fb[..., 0] > 150) & (fb[..., 0] > 2.5 * fb[..., 1]) & (fb[..., 0] > 2 * fb[..., 2])).sum())
    ex.checked('石榴筐里红色像素 ≥ 40（= %d）' % red, 0 if red >= 40 else 1)
    fp = np.array(R['near'].crop(tuple(st['anchors']['front_page']))).astype(int)
    blk = int((fp[..., :3].max(-1) < 60).sum())
    ex.checked('头版上有报头黑条（暗像素 ≥ 20，= %d）' % blk, 0 if blk >= 20 else 1)
    rv = np.array(R['near'].crop((ARCH[0] + 8, RIVER_Y[0], ARCH[1] - 8, RIVER_Y[1]))).astype(np.float32)
    ex.checked('门洞里的河面够亮（平均亮度 %.0f ≥ 150）' % _lum(rv).mean(), 0 if _lum(rv).mean() >= 150 else 1)
    # 导出 vs 直接拼
    for camX in (0, 120, 200, 320):
        for t in (0.0, 1.25):
            got = BJ.ref_render(st, imgs, camX, t, {})
            ex.checked('窄街 camX=%d t=%.2f 导出 vs 直接拼' % (camX, t), BJ.ndiff(got, compose(camX, t)))
    nm = _lum(np.array(R['near'])[..., :3].astype(np.float32))
    ex.note('可走带后面的亮度：街面 y148–176 均值 %.0f 标准差 %.1f；一层铺面 y110–145 均值 %.0f 标准差 %.1f' %
            (nm[148:177].mean(), nm[148:177].std(), nm[110:146].mean(), nm[110:146].std()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch4', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        compose(camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'varanasi_street_solo_%d.png' % camX))
    world = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    world.alpha_composite(build()['near'])
    world.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'varanasi_street_near.png'))
    cw = Image.new('RGBA', (40, 18), (120, 120, 120, 255))
    paste(cw, cow_img(), 3, 2)
    cw.convert('RGB').resize((40 * 8, 18 * 8), Image.NEAREST).save(os.path.join(od, 'varanasi_cow.png'))
    print('ok')
