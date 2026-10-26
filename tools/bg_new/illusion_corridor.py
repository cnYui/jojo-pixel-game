# -*- coding: utf-8 -*-
r"""illusion_corridor —— 第11章 b25「次中音萨克斯」的幻觉走廊（地图 illusion_ch11，11-09）。
同一段走廊（mansion_corridor）的幻觉版：偏紫、顶上的线条有点歪、肖像都变成同一张脸（苍白、红眼）、烛台倒挂着、烛火往下烧；
每个变体里藏着一块假墙（和真墙几乎一样，只有很细的破绽）。2026-10-19 mansion 组按体验版精度从头画。

地图 640 宽、ground 156、可走带 y 150–174（和真走廊一样的壳：天花、檐口、墙纸、腰线、护墙板、踢脚板、木地板、地毯；
三扇封死的高窗、两端的丝绒帘三个变体一模一样——这就是“一眼看得出是同一段走廊”）。
key（都是 pick，值取最接近的那张）：
  variant 0 / 1 / 2   三个变体：墙纸颜色（李子紫红 / 靛紫 / 洋红）、三幅肖像的位置、四个烛台的位置不同；假墙分别在 x 285 / 430 / 180
                      （x 70 / 120 / 335 的烛台 / 肖像在几个变体里保持原位当“记号”，其余的挪位置；变体之间的肖像 / 烛台至少隔 25 px，
                      免得一个变体的眼睛 / 火苗被另一个变体的遮盖层误盖）
  menace  0–3         紫色幻觉逐级加深（紫色有序抖动的薄雾，从天花往下压；可走带最多盖 12 %）——剧情还会叠 alpha .08 → .33 的紫，背景克制
  cracked 0–3         当前变体假墙上的裂纹逐级加深（0 无 / 1 细纹 / 2 蛛网状 + 掉灰 / 3 大裂口 + 里面透紫光）
  open    0 / 1       假墙打开：露出后面的小房间（昏暗的紫色房间，地上有碎灰泥）
各 key 能任意组合。要点：“当前变体”的裂纹 / 打开 / 动画是靠遮盖层做的——裂纹层和打开层把三处假墙的位置都画了，
然后 cover（pick variant）把另外两个变体的假墙位置 / 烛台火苗 / 肖像眼睛的位置用底图的原像素盖回去，所以只会在当前变体里出现。
图层（从后往前）：
  common   pano           三个变体一模一样的像素（天花 / 檐口 / 三扇窗 / 两端的帘 / 腰线以下的护墙板、地板、地毯，约一半）：
                          变体光（烛光、画框灯）只照墙纸区，这些像素三个变体才逐像素一样，只存一份
  base     pick variant   三个变体各自“和共用图不一样”的像素（墙纸 + 肖像 + 烛台 + 自己的假墙）；共用图 + 它 = 原来的整张底图（已打光、
                          顶上沿的线条轻微歪斜；不透明）
  cracks   pick cracked   裂纹（0 = 空）
  opened   pano key open  打开后的小房间（三处）
  flames   strip 8 fps    倒挂烛台往下烧的紫火（三个变体的烛台位置都画）
  eyes     strip          肖像的眼睛：同步地看向左 / 右、偶尔一眨（三个变体的肖像位置都画）
  sparks   strip          墙纸上的金点一明一暗（幻觉里的墙纸在“爬”）
  motes0–2 strip          三扇窗前飘着的紫色浮尘
  cover    pick variant   把别的变体的动态像素盖回去
  menace   pick menace    紫雾
锚点（素材总表定稿）：arrive [40,164]、fake_walls [[285,140],[430,140],[180,140]]、fake_wall_boxes（对应三个框）、exit [626,162]；
      另导出 variant_candles（3 组 × 4 个 [x, 烛芯 y]）/ variant_portraits（3 组 × 3 个 [x, 眼睛 y]）、crack_points（裂纹的中心）。
      烛台 / 肖像写成点的列表（不是 [x1, x2, x3, x4] 这种数列）：数列里 4 个数会被锚点自检当成框、判成越界。
单独运行：python -B tools\bg_new\illusion_corridor.py → tools\bg_new\_preview\ch11\after\illusion_corridor_solo.png
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
from scipy import ndimage  # noqa: E402

from engine.core import hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _parts():
    """mansion_parts（importlib 按路径加载，同 mansion_exterior）。"""
    key = 'bg_new_mansion_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'mansion_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


M = _parts()
dk, lt, hl, vl, px, rect = M.dk, M.lt, M.hl, M.vl, M.px, M.rect
C = M.C
H = M.H
N8 = M.N8
FPS = M.FPS_SLOW
FPS_FIRE = M.FPS_FIRE

PW = 640
GROUND = 156
WALK = (150, 174)

# ---- 三个变体：墙纸、假墙、肖像、烛台
PAPERS = [
    dict(base=(98, 34, 72), dk=(76, 24, 58), lt=(122, 48, 92), gold=(166, 114, 156)),      # 李子紫红
    dict(base=(66, 44, 108), dk=(50, 32, 88), lt=(88, 62, 132), gold=(150, 128, 194)),     # 靛紫
    dict(base=(112, 40, 92), dk=(88, 28, 74), lt=(136, 58, 114), gold=(178, 124, 172)),    # 洋红（压低）
]
VARS = [
    dict(fake=285, candles=[70, 150, 335, 455], portraits=[120, 215, 395]),
    dict(fake=430, candles=[70, 215, 335, 480], portraits=[120, 270, 560]),
    dict(fake=180, candles=[105, 225, 335, 455], portraits=[140, 290, 425]),
]
FAKE_W = 20                                     # 假墙框：x ± 20、y 96–156
FAKE_Y = (96, 156)
WICK_Y = 100                                    # 倒挂蜡烛的烛芯（火苗从这里往下烧）
PORTRAIT_Y = (81, 118)
WIN = [(31, 'r'), (351, 'l'), (498, 'r')]       # 高窗：和真走廊一模一样
WIN_Y0, WIN_W, WIN_H = 26, 20, 80
RUG = dict(base=(104, 40, 84), lt=(128, 58, 106), dk=(76, 26, 64), dd=(46, 14, 44), gold=(184, 148, 126),
           gold_d=(136, 104, 92))               # 真走廊的地毯偏紫的版本（花纹一样）
VIO_FLAME = ((255, 246, 255), (240, 176, 255), (196, 100, 236), (124, 50, 176))      # 紫火：白芯 → 粉紫 → 紫
T_VIO = (1.08, 0.78, 1.28)                      # 紫火的光
T_PAMB = (0.80, 0.66, 1.18)                     # 环境光：比馆里别处更紫
T_FLOORV = (1.04, 0.88, 1.08)
MENACE_COL = ((86, 30, 126), (124, 58, 176))    # 紫雾的两个颜色（深、浅）
ANCHORS = {
    'arrive': [40, 164],
    'fake_walls': [[285, 140], [430, 140], [180, 140]],
    'fake_wall_boxes': [[285 - FAKE_W, FAKE_Y[0], 285 + FAKE_W, FAKE_Y[1]],
                        [430 - FAKE_W, FAKE_Y[0], 430 + FAKE_W, FAKE_Y[1]],
                        [180 - FAKE_W, FAKE_Y[0], 180 + FAKE_W, FAKE_Y[1]]],
    'exit': [626, 162],
}
REQUIRED = tuple(ANCHORS)
STAND = ('arrive', 'exit')


# ============================================================ 顶上沿歪斜
def warp(im):
    """“透视有点歪”：每一列按自己的幅度把内容往下挪（天花那一行最多挪 4 px，往下线性减到腰线 / 地面 = 0），
    幅度沿 x 缓缓起伏——地面和可走带一行都不动（自检要求平整），歪的只有墙和顶。所有层（底图、裂纹、动画帧）用同一个函数。"""
    a = np.array(im)
    yy = np.arange(H)[:, None]
    xx = np.arange(PW)[None, :]
    amp = 2.6 * np.sin(math.tau * xx / 420.0 + 0.6) + 1.2 * np.sin(math.tau * xx / 170.0 + 2.0)
    prof = np.clip((148 - yy) / 131.0, 0, 1)
    s = np.round(amp * prof).astype(int)
    src = np.clip(yy - s, 0, H - 1)
    return Image.fromarray(a[src, xx], 'RGBA')


# ============================================================ 底图
def sconce_inv(cv, x, wick_y, seed=0):
    """倒挂的烛台：画一个正常的壁烛台，上下翻过来贴上去——背板在上、托盘在中间、蜡烛往下垂，烛芯在最下面（火苗往下烧）。"""
    tmp = M.Canvas(24, 40)
    M.sconce(tmp, 12, 26, arms=1, seed=seed)
    flip = tmp.im.crop((0, 14, 24, 37)).transpose(Image.FLIP_TOP_BOTTOM)      # 烛芯原来在第 20 行 → 裁出第 6 行 → 翻成第 16 行
    cv.im.alpha_composite(flip, (x - 12, wick_y - 16))


@lru_cache(maxsize=None)
def albedo(v):
    """第 v 个变体满光时的固有色：返回 (Canvas, info)。"""
    cfg, paper = VARS[v], PAPERS[v]
    cv = M.Canvas(PW, H)
    info = {}
    M.corridor_shell(cv, 0, PW - 1, paper=paper, wood=M.WOOD, rug=RUG, seed=11, ceil=(32, 22, 44))
    # 假墙：和真墙同一套墙纸 / 护墙板，只是百合纹和小花对调、护墙板的板缝错开 2 px、底色多一点点红——细的破绽
    F = cfg['fake']
    x0, x1 = F - FAKE_W, F + FAKE_W - 1
    p2 = dict(paper, base=tuple(min(255, c + 3) for c in paper['base']))
    M.wallpaper(cv, (x0, FAKE_Y[0], x1, M.CORR['rail'] - 1), seed=11, pal=p2, swap=True, age=False)
    M.dado_rail(cv, x0, x1, M.CORR['rail'], M.WOOD)
    M.wainscot(cv, x0, x1, M.CORR['wain'][0], M.CORR['wain'][1], M.WOOD, panel=28, gap=5, seed=11, off=2)
    M.skirting(cv, x0, x1, M.CORR['skirt'][0], 5, M.WOOD)
    info['fake_box'] = [x0, FAKE_Y[0], x1 + 1, FAKE_Y[1]]
    # 高窗 ×3（三个变体一样）
    for i, (wx0, side) in enumerate(WIN):
        M.black_window(cv, wx0, WIN_Y0, WIN_W, WIN_H, slit=side, boards=(i != 1), seed=i * 5 + 2)
    # 肖像：同一张脸
    info['portraits'] = []
    for i, cx in enumerate(cfg['portraits']):
        info['portraits'].append(M.portrait(cv, cx - 14, PORTRAIT_Y[0], cx + 13, PORTRAIT_Y[1], 'same', seed=v * 7 + i))
    # 倒挂的烛台
    for x in cfg['candles']:
        sconce_inv(cv, x, WICK_Y, seed=x)
    # 两端的丝绒帘 + 角落的蛛网（和真走廊一样）
    M.velvet_curtain(cv, 0, 12, 20, 148, side='r', pal=M.VELVET, seed=1)
    M.valance(cv, 0, 12, 18, h=6)
    M.velvet_curtain(cv, 598, 639, 20, 148, side='l', pal=M.VELVET, seed=2)
    M.valance(cv, 598, 639, 18, h=6)
    M.cobweb(cv, 14, 21, 11, 'tl', seed=1)
    M.cobweb(cv, 596, 21, 12, 'tr', seed=2)
    return cv, info


@lru_cache(maxsize=1)
def window_canvas():
    """只画三扇窗（透明底）：返回 (Canvas, 窗的不透明遮罩)。窗是三个变体共用的东西——
    烛光不照进窗的像素，三个变体里的窗才会逐像素一样（也才能只存一份）。"""
    cv = M.Canvas(PW, H)
    for i, (wx0, side) in enumerate(WIN):
        M.black_window(cv, wx0, WIN_Y0, WIN_W, WIN_H, slit=side, boards=(i != 1), seed=i * 5 + 2)
    return cv, np.array(cv.im)[..., 3] > 0


@lru_cache(maxsize=1)
def variant_zone():
    """变体光能照到的地方（H×PW 的 0 / 1 浮点）：墙纸区（y 17–119），挖掉窗和两端的帘；腰线往下渐渐收到 0
    （y ≥ 122 完全不受变体光影响 = 护墙板 / 地板 / 地毯三个变体一样）。"""
    yy = np.arange(H)[:, None].astype(np.float32)
    zone = np.clip((122.0 - yy) / 12.0, 0, 1) * (yy >= 17) * np.ones((1, PW), np.float32)
    zone[:, :14] = 0                                                    # 左帘
    zone[:, 598:] = 0                                                   # 右帘
    zone[window_canvas()[1]] = 0
    return zone.astype(np.float32)


def light(v):
    cfg = VARS[v]
    L = M.Light(PW, H, amb=0.30, tint=T_PAMB)
    yy, xx = L.yy, L.xx
    extra = np.zeros((H, PW), np.float32)
    extra -= 0.04 * np.clip((24 - yy) / 24.0, 0, 1)
    extra -= 0.20 * np.clip((20 - xx) / 20.0, 0, 1) + 0.20 * np.clip((xx - 620) / 20.0, 0, 1)
    L.amb_add(np.maximum(extra, -0.2))
    fl = np.where(yy >= 149, 0.62, 0.0).astype(np.float32)
    fl -= np.where(yy >= 149, 0.14 * np.clip((156 - yy) / 7.0, 0, 1), 0.0).astype(np.float32)
    L.add(fl, T_FLOORV)
    # 腰线以下的护墙板：三个变体共用的一层淡淡的“地毯反光”，免得护墙板黑成一块（板的凹凸要看得出来）
    sm = np.clip((yy - 108.0) / 20.0, 0, 1)
    wash = np.where(yy < 149, 0.26 * sm * sm * (3 - 2 * sm), 0.0).astype(np.float32)
    L.add(wash, T_FLOORV)
    zone = variant_zone()
    for x in cfg['candles']:                                          # 烛光：只照变体自己的墙纸区（见 variant_zone）
        d = np.hypot(xx - x, (yy - (WICK_Y + 4)) * 1.1)
        L.add(1.05 * np.clip(1 - d / 90.0, 0, 1) ** 1.7 * zone, T_VIO)
    for cx in cfg['portraits']:                                       # 画框的小灯：眼睛得看得清
        d = np.hypot(xx - cx, (yy - 98) * 0.9)
        L.add(0.50 * np.clip(1 - d / 34.0, 0, 1) ** 1.2 * zone, T_VIO)
    return L


def floor_mask():
    m = np.zeros((H, PW), bool)
    m[149:, :] = True
    return m


@lru_cache(maxsize=None)
def field(v):
    # 墙上的光分得粗一点（12 档、抖动 0.2）：三个变体的整张底图各占一份 PNG，抖得越碎越大
    return light(v).field(levels=12, fine=floor_mask(), fine_levels=26, jitter=0.2)


@lru_cache(maxsize=None)
def base_img(v):
    cv, _ = albedo(v)
    return warp(M.apply(cv, field(v)))


def _lit(v, draw_fn, do_warp=True):
    """在透明 Canvas 上按固有色画 strip 的一帧 / 一层，乘上第 v 个变体的光照（发光的像素保留原色），再歪斜。"""
    cv = M.Canvas(PW, H)
    draw_fn(cv)
    im = M.apply(cv, field(v), floor=0.0)
    return warp(im) if do_warp else im


@lru_cache(maxsize=1)
def split_bases():
    """三个变体的整张底图 → (共用图, [变体 0、1、2 各自只留“和共用图不一样”的像素])。
    为什么拆：三张整图各 70 KB，其实天花 / 窗 / 帘 / 腰线以下三个变体一样（变体光被 variant_zone 挡在外面），
    只有墙纸区不同——共用的存一份，变体只存差异，PNG 体积砍掉将近一半。
    “一样”的判定做了一次开运算：墙纸上碰巧三个变体同色的零星像素不算共用（否则共用图满是散点、反而更大）。
    拆出来的两层叠回去逐像素等于原整图（自检里验证）。"""
    arrs = [np.array(base_img(v)) for v in range(3)]
    eq = (arrs[0] == arrs[1]).all(-1) & (arrs[0] == arrs[2]).all(-1)
    shared = ndimage.binary_opening(eq, structure=np.ones((3, 3), bool))
    com = np.zeros_like(arrs[0])
    com[shared] = arrs[0][shared]
    parts = []
    for a in arrs:
        o = np.zeros_like(a)
        o[~shared] = a[~shared]
        parts.append(Image.fromarray(o, 'RGBA'))
    return Image.fromarray(com, 'RGBA'), parts


# ============================================================ 裂纹（cracked 1–3）
CRACK_LEN = {1: 15, 2: 27, 3: 40}
CRACK_COUNT = {1: 4, 2: 7, 3: 11}
CRACK_C = (112, 114)                                # 裂纹的中心相对 x、y：墙纸和腰线交界上面一点，裂缝往上下两边都能走


def _crack_walk(F, k, level, n):
    """第 k 条裂纹：从中心附近出发，朝 k/n 圈的方向随机折着往外走，走 CRACK_LEN[level] 步；返回点列。"""
    ang = k * math.tau / n + hrange(-0.35, 0.35, F, k, 1)
    x, y = F + hrange(-2, 2, F, k, 2), CRACK_C[1] + hrange(-2, 2, F, k, 3)
    pts = []
    for s in range(int(CRACK_LEN[level] * hrange(0.75, 1.15, F, k, 4))):
        ang += hrange(-0.55, 0.55, F, k, s, 5)
        x += math.cos(ang)
        y += math.sin(ang) * 1.05
        xi, yi = int(round(x)), int(round(y))
        if not (F - FAKE_W + 1 <= xi <= F + FAKE_W - 2 and FAKE_Y[0] + 3 <= yi <= 146):
            break
        pts.append((xi, yi))
    return pts


CRACK_GLOW = {1: (122, 74, 168), 2: (166, 100, 220), 3: (218, 146, 255)}     # 缝里透出来的紫光，逐级更亮（墙后的小房间有光）


def _draw_cracks(d, F, level):
    """裂缝 = 一道发紫光的细线 + 旁边一道暗边（背景是暗紫的墙，纯黑的缝看不见，所以让缝自己亮）。"""
    glow = CRACK_GLOW[level]
    n = CRACK_COUNT[level]
    for k in range(n):
        pts = _crack_walk(F, k, level, n)
        for i, (x, y) in enumerate(pts):
            px(d, x, y, glow if i % 5 != 4 else dk(glow, 0.7))
            px(d, x + 1, y, (10, 2, 16))
            if level >= 2 and i < len(pts) * 0.55:
                px(d, x, y + 1, dk(glow, 0.55))                          # 靠近中心的一段粗一点
                px(d, x + 1, y + 1, (10, 2, 16))
        if level >= 2 and pts and k % 2 == 0:                           # 岔出去的一小段
            bx, by = pts[len(pts) // 2]
            sgn = -1 if k % 4 == 0 else 1
            for j in range(6 + 4 * (level - 2)):
                xx, yy = bx + sgn * (j + 1), by + (j // 2) * (1 if k % 3 else -1)
                if F - FAKE_W + 1 <= xx <= F + FAKE_W - 2 and FAKE_Y[0] + 3 <= yy <= 146:
                    px(d, xx, yy, dk(glow, 0.85))
                    px(d, xx, yy + 1, (10, 2, 16))
    if level >= 2:                                                       # 中间掉了一块灰泥（边缘参差：一半亮、一半暗）
        R = 5 if level == 2 else 10
        cx, cy = F, CRACK_C[1]
        for y in range(cy - R - 1, cy + R + 2):
            for x in range(cx - R - 1, cx + R + 2):
                ang = math.atan2(y - cy, x - cx)
                rr = R * (0.72 + 0.28 * math.sin(ang * 3 + F) + 0.12 * math.sin(ang * 7 + 1))
                dd = math.hypot((x - cx) * 0.9, (y - cy) * 1.0)
                if dd < rr:
                    px(d, x, y, (16, 6, 28) if level == 2 else (48, 20, 84))
                elif dd < rr + 1.1:
                    px(d, x, y, glow if (x + y) % 2 == 0 else (10, 2, 16))
        for i in range(4 + 5 * (level - 2)):                             # 掉在地上的碎灰泥
            ccx = F + int(hrange(-14, 14, F, i, 6))
            ccy = 149 + int(hrange(0, 5, F, i, 7))
            hl(d, ccx, ccx + int(hrange(0, 2, F, i, 3)), ccy, (186, 156, 186))
            px(d, ccx, ccy + 1, (116, 90, 124))


@lru_cache(maxsize=None)
def crack_img(level):
    if level == 0:
        return A._new(PW, H)
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for cfg in VARS:
        _draw_cracks(d, cfg['fake'], level)
    return warp(im)


# ============================================================ 假墙打开（open）
def _open_room(im, F):
    """假墙后的小房间：不规则的洞口（碎墙纸边）里是一间一点透视的昏暗紫色小房间——天花、左右墙面往里收、后墙有暗纹和一团
    灯的光晕、地板的板缝往中间聚；洞口前地上一堆碎灰泥。"""
    d = ImageDraw.Draw(im)
    x0, x1, top, bot = F - 18, F + 17, 99, 148
    # 洞口外轮廓（碎边）
    outer = [(x0 + 1, top + 4), (x0 + 6, top), (F - 5, top + 2), (F + 3, top - 1), (F + 11, top + 2), (x1 - 1, top + 3),
             (x1 + 1, top + 14), (x1, bot), (x0, bot), (x0 - 1, top + 20)]
    d.polygon(outer, fill=C((176, 130, 176)), outline=C((26, 10, 36)))
    bx0, bx1, bt, bb = F - 10, F + 10, 110, 138                         # 后墙
    ix0, ix1, it, ib = x0 + 3, x1 - 3, top + 3, bot - 2                 # 洞口里侧一圈
    d.polygon([(ix0, it), (ix1, it), (bx1, bt), (bx0, bt)], fill=C((24, 12, 40)))             # 天花
    d.polygon([(ix0, it), (bx0, bt), (bx0, bb), (ix0, ib)], fill=C((36, 18, 58)))              # 左墙
    d.polygon([(ix1, it), (bx1, bt), (bx1, bb), (ix1, ib)], fill=C((28, 14, 48)))              # 右墙
    d.polygon([(bx0, bb), (bx1, bb), (ix1, ib), (ix0, ib)], fill=C((86, 52, 110)))             # 地板
    rect(d, bx0, bt, bx1, bb - 1, (60, 30, 96))                                                  # 后墙
    for y in range(bt + 1, bb - 1, 3):                                   # 后墙的暗纹
        for x in range(bx0 + 1 + (y // 3 % 2) * 2, bx1, 4):
            px(d, x, y, (70, 38, 108))
    cx, cy = F, 122                                                      # 后墙上一团灯的光晕（抖动的同心环）
    for r, c in ((8, (74, 40, 114)), (5, (96, 54, 134)), (2, (140, 84, 170))):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C(c))
    for k in range(-3, 4):                                               # 地板板缝往中间聚
        d.line((F + k * 3, bb, F + k * 6, ib), fill=C((58, 34, 78)))
    hl(d, bx0, bx1, bb - 1, (40, 22, 60))
    hl(d, ix0, ix1, ib, (30, 14, 44))
    # 洞口上沿的碎渣、右边一道暗边
    for x in range(x0 + 5, x1 - 4):
        if hash01(F, x, 3) < 0.45:
            px(d, x, top + int(hash01(F, x, 4) * 3) + 1, (176, 138, 176))
    vl(d, x1 - 1, top + 4, bot, (26, 10, 36))
    for i in range(10):                                                  # 洞口前的碎灰泥
        ccx = F + int(hrange(-18, 18, F, i, 11))
        ccy = 149 + int(hrange(0, 5, F, i, 12))
        hl(d, ccx, ccx + int(hrange(0, 3, F, i, 13)), ccy, (186, 156, 186))
        px(d, ccx, ccy + 1, (116, 90, 124))


@lru_cache(maxsize=1)
def open_img():
    im = A._new(PW, H)
    for cfg in VARS:
        _open_room(im, cfg['fake'])
    return warp(im)


# ============================================================ 紫雾（menace）
@lru_cache(maxsize=None)
def menace_img(level):
    """紫色有序抖动的薄雾：密度 = 级别系数 × 烟的噪声 × 竖向分布（天花最浓、往下渐淡；可走带 ≤ 12 %）。
    只有 0 / 255 透明度：被选中的像素换成深紫 / 浅紫（浅紫在最密的地方）。"""
    if level == 0:
        return A._new(PW, H)
    yy, xx = np.mgrid[0:H, 0:PW]
    bay = A._bayer(PW, H)
    n = A._fbm(PW + 8, H + 8, 36, seed=19)[4:4 + H, 4:4 + PW]
    k = {1: 0.12, 2: 0.26, 3: 0.42}[level]
    prof = np.where(yy < 149, 1.0 - 0.55 * np.clip((yy - 17) / 131.0, 0, 1), 0.0)
    dens = k * (0.30 + 1.0 * n) * prof
    dens = np.where(yy >= 149, np.minimum(0.12, 0.09 * level * (0.4 + n)), dens)      # 可走带：最多 12 %
    rnd = np.random.default_rng(31).random((H, PW)).astype(np.float32)
    thr = 0.55 * bay + 0.45 * rnd                                       # 纯 Bayer 会是一张规规矩矩的网；掺 45 % 随机才像雾
    m = thr < dens
    out = np.zeros((H, PW, 4), np.uint8)
    deep = m & (thr >= dens * 0.40)
    lite = m & (thr < dens * 0.40)
    out[deep, :3] = MENACE_COL[0]
    out[lite, :3] = MENACE_COL[1]
    out[m, 3] = 255
    return Image.fromarray(out, 'RGBA')


# ============================================================ strip
def _cache(raw, fps=FPS):
    memo = {}

    def fn(t):
        f = M.frame_of(t, fps)
        if f not in memo:
            memo[f] = raw(f)
        return memo[f]
    return fn


FLAME_POINTS = sorted({x for cfg in VARS for x in cfg['candles']})


def _flames_raw(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for i, x in enumerate(FLAME_POINTS):
        M.flame(d, x, WICK_Y + 1, f, seed=i, down=True, big=True, pal=VIO_FLAME)
    return warp(im)


EYE_SEQ = (0, 1, 9, 1, 0, -1, 9, -1)            # look：9 = 眨眼；三幅肖像同步看过去再看回来（幻觉：一张脸）；相邻两帧一定不同


def _eyes_raw(f):
    """所有变体里所有肖像的眼睛（按位置去重）：每幅按自己所在变体的光照算颜色，红眼珠自己发光；睁眼时再点一粒高光。"""
    seen = set()
    out = A._new(PW, H)
    look = EYE_SEQ[f]
    for v in range(3):
        cv = M.Canvas(PW, H)
        n = 0
        for p in albedo(v)[1]['portraits']:
            key = tuple(p['eyes'][0])
            if key in seen:
                continue
            seen.add(key)
            M.eye_px(cv.d, p['eyes'], 0 if look == 9 else look, 'same', blink=(look == 9))
            if look != 9:
                for (ex_, ey_) in p['eyes']:
                    cv.e.point((ex_ + (1 if look > 0 else 0), ey_), fill=255)       # 红眼珠自己发光
            n += 1
        if n:
            out.alpha_composite(M.apply(cv, field(v), floor=0.0))
    return warp(out)


@lru_cache(maxsize=1)
def _spark_points():
    """从墙纸的金点位置里挑 10 个：y 30–66（所有变体里都是空墙纸）、避开窗和裂纹。"""
    cv, _ = albedo(0)
    a = np.array(cv.im)
    gold = np.array(PAPERS[0]['gold'])
    pts = []
    for y in range(30, 67):
        for x in range(60, 600):
            if any(wx - 6 <= x <= wx + WIN_W + 6 for wx, _ in WIN):
                continue
            if tuple(a[y, x, :3]) == tuple(gold):
                pts.append((x, y))
    out = []
    for i in range(10):
        out.append(pts[int(hash01(77, i) * len(pts))])
    return out


def _sparks_raw(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate(_spark_points()):
        if (f - i) % N8 in (0, 1):
            px(d, x, y, (236, 196, 255))
            if (f - i) % N8 == 0:
                px(d, x + 1, y, (170, 110, 220))
                px(d, x - 1, y, (170, 110, 220))
                px(d, x, y - 1, (170, 110, 220))
                px(d, x, y + 1, (170, 110, 220))
    return warp(im)


def _motes_fn(i):
    wx0 = WIN[i][0]
    poly = [(wx0, WIN_Y0 + 14), (wx0 + WIN_W - 1, WIN_Y0 + 14), (wx0 + WIN_W - 1, WIN_Y0 + WIN_H - 2), (wx0, WIN_Y0 + WIN_H - 2)]
    fn, _ = M.motes_frame_fn(poly, PW, H, n=9, seed=60 + i, col=(226, 180, 255), drift=(1.0, 1.0))
    return fn


# ============================================================ 遮盖层（cover）
def _hide_boxes(v):
    """第 v 个变体要盖掉的小框：别的变体的烛台火苗、肖像眼睛（自己的位置不盖）。"""
    mine_c = set(VARS[v]['candles'])
    mine_p = {tuple(p['eyes'][0]) for p in albedo(v)[1]['portraits']}
    boxes = []
    other_c = sorted({x for u, cfg in enumerate(VARS) if u != v for x in cfg['candles']} - mine_c)
    for x in other_c:
        boxes.append((x - 3, WICK_Y + 1, x + 4, WICK_Y + 12))
    seen = set()
    for u, cfg in enumerate(VARS):
        if u == v:
            continue
        for p in albedo(u)[1]['portraits']:
            key = tuple(p['eyes'][0])
            if key in mine_p or key in seen:
                continue
            seen.add(key)
            xs = [e[0] for e in p['eyes']]
            ys = [e[1] for e in p['eyes']]
            boxes.append((min(xs) - 2, min(ys) - 4, max(xs) + 4, max(ys) + 4))
    return boxes


@lru_cache(maxsize=None)
def cover_mask(v):
    """第 v 个变体里要被盖回底图的像素：别的假墙位置上“裂纹 1–3 级 / 洞口”会画到的像素（取并集），
    加上别的变体的火苗 / 眼睛的小框。裂纹 / 洞口三处都画了，当前变体的那一处不盖。"""
    m = np.zeros((H, PW), bool)
    touched = np.zeros((H, PW), bool)
    for lv in (1, 2, 3):
        touched |= np.array(crack_img(lv))[..., 3] > 0
    touched |= np.array(open_img())[..., 3] > 0
    for u, cfg in enumerate(VARS):
        if u == v:
            continue
        F = cfg['fake']
        m[:, F - FAKE_W - 3:F + FAKE_W + 3] |= touched[:, F - FAKE_W - 3:F + FAKE_W + 3]
    for (x0, y0, x1, y1) in _hide_boxes(v):
        m[max(0, y0):y1, max(0, x0):x1] = True
    return m


@lru_cache(maxsize=None)
def cover_img(v):
    base = np.array(base_img(v))
    m = cover_mask(v)
    out = np.zeros_like(base)
    out[m] = base[m]
    return Image.fromarray(out, 'RGBA')


# ============================================================ 图层表 / 导出
@lru_cache(maxsize=1)
def tables():
    com, parts = split_bases()
    layers = [M.L_pano('common', com, 1.0, 0, 0, crop=False),
              M.L_pick('base', 'variant', [0, 1, 2], parts, x=0, y=0, k=1.0)]
    layers.append(M.L_pick('cracks', 'cracked', [0, 1, 2, 3], [crack_img(i) for i in range(4)], x=0, y=0, k=1.0))
    layers.append(M.L_pano('opened', open_img(), 1.0, key='open'))
    fn = _cache(_flames_raw, FPS_FIRE)
    layers.append(M.L_strip('flames', M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    fn = _cache(_eyes_raw)
    layers.append(M.L_strip('eyes', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    fn = _cache(_sparks_raw)
    layers.append(M.L_strip('sparks', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    for i in range(3):
        fn = _motes_fn(i)
        layers.append(M.L_strip('motes%d' % i, M.auto_box(fn, N8, FPS), N8, FPS, fn))
    layers.append(M.L_pick('cover', 'variant', [0, 1, 2], [cover_img(v) for v in range(3)], x=0, y=0, k=1.0))
    layers.append(M.L_pick('menace', 'menace', [0, 1, 2, 3], [menace_img(i) for i in range(4)], x=0, y=0, k=1.0))
    return layers, []


def anchors():
    anc = {k: ([list(p) for p in v] if isinstance(v[0], list) else list(v)) for k, v in ANCHORS.items()}
    anc.update(variant_candles=[[[x, WICK_Y] for x in c['candles']] for c in VARS],         # 每个变体 4 个：[x, 烛芯 y]
               variant_portraits=[[[x, PORTRAIT_Y[0] + 12] for x in c['portraits']] for c in VARS],    # 每个变体 3 个：[x, 眼睛 y 附近]
               crack_points=[[c['fake'], 122] for c in VARS])
    return anc


def compose(camX=0, t=0.5, state=None):
    layers, fg = tables()
    return M.compose(layers, fg, camX, t, state)


def export(ex, BJ):
    layers, fg = tables()
    st = M.export_stage(ex, PW, GROUND, WALK, layers, fg, anchors())
    if ex.check_on:
        _checks(ex, BJ, st, layers, fg)
    return st


def _checks(ex, BJ, st, layers, fg):
    states = [{}, {'variant': 1}, {'variant': 2}, {'cracked': 3}, {'variant': 1, 'cracked': 2, 'menace': 2},
              {'variant': 2, 'open': 1, 'menace': 3}]
    cfg = dict(title='幻觉走廊', PW=PW, walk=WALK, base=base_img(0), states=states, stand=STAND, required=REQUIRED,
               size_limit=250 * 1024, flat=(0, PW, WALK[0], WALK[1] + 1, 18, 0.012), cams_step=80,
               export_states=[{}, {'variant': 1, 'cracked': 1, 'menace': 1}, {'variant': 2, 'cracked': 3, 'open': 1, 'menace': 3}])
    M.common_checks(ex, BJ, st, layers, fg, cfg)
    # 另两个变体的可走带也要平整
    for v in (1, 2):
        lumb = M.lum(np.array(base_img(v))[..., :3].astype(np.float32))
        bad = 0
        for y in range(WALK[0], WALK[1] + 1):
            row = lumb[y]
            bad += int((np.abs(row - np.median(row)) > 18).sum())
        tot = (WALK[1] - WALK[0] + 1) * PW
        ex.checked('变体 %d 可走带平整（行内亮度差 > 18 的像素 %.2f %% ≤ 1.2 %%）' % (v, 100.0 * bad / tot), 0 if bad <= 0.012 * tot else bad)
    # 同一段走廊：三扇窗逐像素一样——只比窗自己的像素（窗洞四角露出来的是墙纸，墙纸颜色本来就按变体不同，不算窗）。
    # 固有色（albedo）和打完光的整张底图两个都比：后者要求烛光没有照进窗里（见 variant_zone）。
    wcv, wmask = window_canvas()
    wref = np.array(wcv.im)
    wm_lit = np.array(warp(Image.fromarray(np.where(wmask[..., None], 255, 0).astype(np.uint8).repeat(4, -1), 'RGBA')))[..., 3] > 0
    wins = 0
    for v in range(3):
        wins += int((np.array(albedo(v)[0].im)[wmask] != wref[wmask]).any(-1).sum())
        if v:
            wins += int((np.array(base_img(v))[wm_lit] != np.array(base_img(0))[wm_lit]).any(-1).sum())
    ex.checked('三个变体的三扇高窗（固有色 + 打光后）逐像素一样（窗 %d px，差 %d px）' % (int(wmask.sum()), wins), wins)
    # 共用图 + 变体图叠回去 = 原来的整张底图（拆分不损像素）；共用的部分占大头
    com, parts = split_bases()
    lost = 0
    for v in range(3):
        rec = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
        rec.alpha_composite(com)
        rec.alpha_composite(parts[v])
        lost += int((np.array(rec) != np.array(base_img(v))).any(-1).sum())
    ex.checked('共用图 + 变体图叠回去逐像素等于三张整底图（差 %d px；共用图占 %.0f %%）' %
               (lost, 100.0 * (np.array(com)[..., 3] > 0).mean()), lost)
    same = np.array([PAPERS[i]['base'] for i in range(3)])
    ex.checked('三个变体的墙纸底色互不相同', 0 if len({tuple(c) for c in same}) == 3 else 1)
    # 假墙：和“没有假墙”的真墙比，只有一小部分像素不同（细的破绽），但确实有
    for v in range(3):
        cv, info = albedo(v)
        F = VARS[v]['fake']
        box = info['fake_box']
        a = np.array(cv.im.crop((box[0], 100, box[2], 119)))[..., :3].astype(np.int32)
        # 同一块墙在“没有假墙”时的样子（重新画一次墙纸）
        ref = M.Canvas(PW, H)
        M.wallpaper(ref, (0, 17, PW - 1, 119), seed=11, pal=PAPERS[v])
        b = np.array(ref.im.crop((box[0], 100, box[2], 119)))[..., :3].astype(np.int32)
        diff = (np.abs(a - b).sum(-1) > 24).mean()
        ex.checked('变体 %d 假墙：墙纸上不同的像素占 %.0f %%（要 3 %%–45 %%：看得出一点、又不明显）' % (v, 100 * diff),
                   0 if 0.03 <= diff <= 0.45 else 1)
    # 裂纹逐级加深
    cnt = [int((np.array(crack_img(i))[..., 3] > 0).sum()) for i in range(4)]
    ex.checked('裂纹逐级加深（像素数 %s 严格递增、0 级为空）' % cnt, 0 if cnt[0] == 0 and cnt[0] < cnt[1] < cnt[2] < cnt[3] else 1)
    # 紫雾逐级加深、可走带最多 12 %
    mc = [float((np.array(menace_img(i))[..., 3] > 0).mean()) for i in range(4)]
    ex.checked('紫雾逐级加深（覆盖率 %s）' % ['%.1f%%' % (100 * q) for q in mc], 0 if mc[0] == 0 and mc[0] < mc[1] < mc[2] < mc[3] else 1)
    fl = max(float((np.array(menace_img(i))[WALK[0]:WALK[1] + 1, :, 3] > 0).mean()) for i in range(4))
    ex.checked('紫雾在可走带上最多盖 %.1f %%（≤ 12 %%）' % (100 * fl), 0 if fl <= 0.121 else 1)
    # 遮盖层不能盖住自己变体的动态像素（烛火 / 眼睛 / 火花）
    ov = 0
    dyn = [np.array(_flames_raw(f))[..., 3] > 0 for f in range(N8)] + [np.array(_eyes_raw(f))[..., 3] > 0 for f in range(N8)]
    for v in range(3):
        cov = np.array(cover_img(v))[..., 3] > 0
        for f, m in enumerate(dyn):
            # 别的变体的火苗 / 眼睛本来就该被盖：只算“自己变体的烛台 / 肖像位置”上的
            own = np.zeros((H, PW), bool)
            for x in VARS[v]['candles']:
                own[WICK_Y - 1:WICK_Y + 12, x - 3:x + 4] = True
            for p in albedo(v)[1]['portraits']:
                for (ex_, ey_) in p['eyes']:
                    own[ey_ - 5:ey_ + 5, ex_ - 2:ex_ + 4] = True
            ov += int((cov & m & own).sum())
    ex.checked('遮盖层没有盖住自己变体的烛火 / 眼睛（重叠 %d px）' % ov, ov)
    # 打开：假墙那个框里六成以上的像素变了（露出一间小房间）
    for v in range(3):
        F = VARS[v]['fake']
        cam = max(0, min(PW - 320, F - 160))
        o = np.array(M.compose(layers, fg, cam, 0.0, {'variant': v, 'open': 1}))
        n = np.array(M.compose(layers, fg, cam, 0.0, {'variant': v}))
        cx = F - cam
        chg = (o[100:146, cx - 16:cx + 16, :3] != n[100:146, cx - 16:cx + 16, :3]).any(-1).mean()
        ex.checked('变体 %d 打开后假墙框里 %.0f %% 的像素变了（≥ 60 %%）' % (v, 100 * chg), 0 if chg >= 0.6 else 1)
    # 每个变体：cracked 3 + open 1 只改自己的假墙那一带，别的两处假墙位置（裂纹 / 洞口三处都画了、靠 cover 盖回去）一个像素都不能变
    for v in range(3):
        cam = max(0, min(PW - 320, VARS[v]['fake'] - 160))
        s0 = np.array(M.compose(layers, fg, cam, 0.0, {'variant': v}))
        s1 = np.array(M.compose(layers, fg, cam, 0.0, {'variant': v, 'cracked': 3, 'open': 1}))
        d_ = (s0 != s1).any(-1)
        mine = int(d_.sum())
        other = 0
        for u in range(3):
            if u == v:
                continue
            F = VARS[u]['fake'] - cam
            if F + FAKE_W > 0 and F - FAKE_W < 320:
                other += int(d_[:, max(0, F - FAKE_W):min(320, F + FAKE_W)].sum())
        ex.checked('variant %d 时 cracked / open 只改自己的假墙 x %d（别的假墙位置被改了 %d px，自己那处改了 %d px）' %
                   (v, VARS[v]['fake'], other, mine), other if mine > 0 else other + 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch11', 'after')
    os.makedirs(od, exist_ok=True)
    rows = []
    for st in ({'variant': 0}, {'variant': 1, 'cracked': 2, 'menace': 1}, {'variant': 2, 'cracked': 3, 'open': 1, 'menace': 3}):
        row = Image.new('RGB', (PW, H), (0, 0, 0))
        for cx in (0, 320):
            row.paste(compose(cx, 0.5, st).convert('RGB'), (cx, 0))
        rows.append(row)
    out = Image.new('RGB', (PW, H * 3 + 8), (0, 0, 0))
    for i, r in enumerate(rows):
        out.paste(r, (0, i * (H + 4)))
    out.resize((out.width * 2, out.height * 2), Image.NEAREST).save(os.path.join(od, 'illusion_corridor_solo.png'))
    print('ok')
