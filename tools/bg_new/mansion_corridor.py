# -*- coding: utf-8 -*-
r"""mansion_corridor —— 第11章「DIO 的馆」馆内长走廊（地图 corridor_ch11，11-04 泰伦斯领路 → 11-05 地板翻开）。
2026-10-19 mansion 组按体验版精度从头画（旧稿是 later_stages 里的一块平涂）。零件和场景框架在 mansion_parts.py。

地图 640 宽、ground 156、可走带 y 150–174；侧视平视（正对着走廊的内墙，像 game_room 一样）。风格和 game_room 一致：
暗红锦缎墙纸 + 桃花心木护墙板 + 金框肖像 + 铜烛台，只是更大、更阴；整条走廊像夜里一样暗（DIO 怕光），高窗都被黑布封死，
只在布边漏出 1 px 的一线光。烛光暖、阴影冷：墙上一圈圈暖光，地面（可走带）压平——地毯和木板的亮度不跟着烛光走，
人站上去永远看得清（自检：可走带行内亮度差）。
“这里没有风”：烛火的形状一帧都不变，只有颜色 / 光晕极弱地一明一暗（呼吸）；蜘蛛网、帘子都不画成会摆的。
从左到右（世界坐标）：
  x 0–12     走廊左端的丝绒帘（走廊从这里延伸出去）
  x 31–50    高窗 A（黑布封死，右边漏一线光，窗前飘浮尘）
  x 80       烛台 1（anchors.candles[0]，火苗在 y 89–94）
  x 106–133  肖像 1（anchors.portraits[0]，中心 [120,100]）
  x 146–172  条案 + 青瓷花瓶 + 枯玫瑰（生活小物件）
  x 190      烛台 2（anchors.candles[1]）
  x 196–223  “连钥匙孔都没有”的门（anchors.locked_door [200,152]：门板上只有铁环拉手和一块实心铁板）
  x 246–273  肖像 2（anchors.portraits[1]）
  x 293–311  落地大摆钟（摆在动，指针停在 12 点）
  x 330      烛台 3（anchors.candles[2]；泰伦斯由剧情摆在 [340,160]，站在烛台和窗之间）
  x 351–370  高窗 B（左边漏光）
  x 386–413  肖像 3（anchors.portraits[2]）
  x 428–451  全身铠甲 + 长戟
  x 470      烛台 4（anchors.candles[3]）
  x 462–498  地板暗门（anchors.trapdoor [480,166]；地毯上只有一圈很淡的接缝）。key trap：门板翻起来靠在墙上（露出木头的反面），
             地上一个黑洞
  x 498–517  高窗 C（右边漏光）
  x 546–573  游戏室的门（anchors.door_game [560,152]，门上一块铜牌）
  x 598–639  走廊右端的丝绒帘 + 帘头（anchors.exit [626,162]）
图层（从后往前）：
  base      pano k 1         整张底图（壳 + 窗 + 肖像 + 门 + 家具 + 烛台；已打光，不透明）
  candle0–3 strip k 1        每个烛台一条：烛火（形状不变、颜色极弱地呼吸）+ 周围墙上的光晕呼吸（只画变了的像素）
  eyes0–2   strip k 1        三幅肖像的眼睛：偶尔转一下（+ 金框上一粒慢慢走过的高光，保证每帧都在动）
  clock     strip k 1        大摆钟里的钟摆
  motes0–2  strip k 1        三扇窗前飘着的浮尘
  moth      strip k 1        烛台 3 旁一只绕着火苗打转的飞蛾
  trap      pano k 1 key trap  地板暗门翻开（门板 + 黑洞）
锚点（素材总表定稿）：arrive [40,164]、portraits [[120,100],[260,100],[400,100]]、candles [[80,96],[190,96],[330,96],[470,96]]、
      locked_door [200,152]、telence [340,160]、trapdoor [480,166]、door_game [560,152]、exit [626,162]；
      另导出 trap_box（暗门的框）、door_box / game_door_box（两扇门的门洞框）。
单独运行：python -B tools\bg_new\mansion_corridor.py → tools\bg_new\_preview\ch11\after\mansion_corridor_solo.png
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

PW = 640
GROUND = 156
WALK = (150, 174)

ANCHORS = {
    'arrive': [40, 164],
    'portraits': [[120, 100], [260, 100], [400, 100]],
    'candles': [[80, 96], [190, 96], [330, 96], [470, 96]],
    'locked_door': [200, 152],
    'telence': [340, 160],
    'trapdoor': [480, 166],
    'door_game': [560, 152],
    'exit': [626, 162],
}
REQUIRED = tuple(ANCHORS)
STAND = ('arrive', 'telence', 'trapdoor', 'exit', 'locked_door', 'door_game')

CANDLE_X = [80, 190, 330, 470]
TRAY_Y = 100                                   # 烛台托盘那一行；烛芯 y 95、火苗底 y 93、火苗 y 88–93
FLAME_BASE = TRAY_Y - 7                        # = candle() 返回的火苗底
PORTRAIT_X = [120, 260, 400]
PORTRAIT_SUBJ = ['noble', 'lady', 'old']
PORTRAIT_Y = (81, 118)                         # 画框上下沿（中心 y 99.5 ≈ anchors 的 100）
WIN = [(31, 'r'), (351, 'l'), (498, 'r')]      # 高窗 x0（宽 20）和漏光的那一边
WIN_Y0, WIN_W, WIN_H = 26, 20, 80
LOCK = (199, 92, 22, 56)                       # 锁着的门：门洞 x0, y0（尖拱顶点）, w, h
GAME = (548, 92, 24, 56)                       # 游戏室的门
TRAP = (462, 155, 498, 176)                    # 暗门的洞 x0, y0, x1, y1（地毯上）
CLOCK_X = 302
ARMOR_X = 438
TABLE = (148, 170)
T_CRT = (0.62, 0.92, 1.45)                     # 游戏室电视漏出来的冷光
T_FLOOR = (1.12, 0.96, 0.90)                  # 地面铺平的那层光：偏中性的暖，免得红地毯被烛光推成橙色
RUG = dict(base=(150, 40, 50), lt=(178, 60, 66), dk=(112, 26, 40), dd=(66, 12, 26), gold=(200, 154, 72),
           gold_d=(146, 106, 50))             # 比馆里别处的 CARPET 亮一档：深色衣服站上去才分得开
WOOD = M.WOOD
PAPER = dict(base=(118, 32, 48), dk=(94, 22, 40), lt=(142, 48, 60), gold=(176, 122, 66))


# ============================================================ 底图
@lru_cache(maxsize=1)
def albedo():
    """满光时的固有色：返回 (Canvas, info)；info 里是别处要用的位置（眼睛、窗缝、钟摆）。"""
    cv = M.Canvas(PW, H)
    info = {}
    M.corridor_shell(cv, 0, PW - 1, paper=PAPER, wood=WOOD, rug=RUG, seed=11)
    # 暗门在地毯上的接缝：很淡的一圈（比周围暗 8 %），知道的人才看得出
    x0, y0, x1, y1 = TRAP
    for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):
        M.mul_box(cv.im, (ax, ay, bx, by), (0.9, 0.9, 0.92))
    # 墙面的磨损：几道从檐口洇下来的水渍（屋顶漏水）+ 一处墙纸剥落
    for (sx, sl, sw) in ((233, 52, 5), (437, 60, 6), (578, 44, 4), (62, 38, 4)):
        M.damp_stain(cv, sx, 18, sl, w=sw, seed=sx)
    M.peel(cv, 556, 36, 8, 11, seed=3, under=(112, 86, 76))
    # 烛台上方的烟痕要先画（在墙纸上），烛台后画
    for x in CANDLE_X:
        M.soot(cv, x, 56, FLAME_BASE - 6, w=5, seed=x)
    # 高窗 ×3
    info['win'] = []
    for i, (wx0, side) in enumerate(WIN):
        info['win'].append(M.black_window(cv, wx0, WIN_Y0, WIN_W, WIN_H, slit=side, boards=(i != 1), seed=i * 5 + 2))
    # 肖像 ×3
    info['portraits'] = []
    for i, cx in enumerate(PORTRAIT_X):
        info['portraits'].append(M.portrait(cv, cx - 14, PORTRAIT_Y[0], cx + 13, PORTRAIT_Y[1], PORTRAIT_SUBJ[i], seed=i + 1))
    # 门
    M.gothic_door(cv, *LOCK, seed=4, keyhole=False)
    M.gothic_door(cv, *GAME, seed=9, plaque=(M.GOLD['md'], 'dice'))
    # 游戏室的门缝：门里是一台没关的电视，门缝底下漏出一线冷光（也是整条走廊里最远处唯一的冷色，指给人看“门在那里”）
    cv.glow_rect(GAME[0] + 1, GAME[1] + GAME[3] - 1, GAME[0] + GAME[2] - 2, GAME[1] + GAME[3] - 1, (120, 160, 250))
    # 条案 + 花瓶
    top = M.console_table(cv, TABLE[0], TABLE[1], 148, seed=2)
    M.dead_flowers(cv, (TABLE[0] + TABLE[1]) // 2, top - 1)
    # 凸面镜（条案上面）+ 家徽（铠甲上面）
    M.round_mirror(cv, (TABLE[0] + TABLE[1]) // 2, 66, 9)
    M.coat_of_arms(cv, ARMOR_X, 46)
    # 摆钟 + 铠甲
    info['clock'] = M.grandfather_clock(cv, CLOCK_X, 148, 70)
    M.armor_stand(cv, ARMOR_X, 148)
    # 烛台（4 个）
    info['flames'] = []
    for x in CANDLE_X:
        info['flames'].append(M.sconce(cv, x, TRAY_Y, arms=1, seed=x)[0])
    # 两端的丝绒帘
    M.velvet_curtain(cv, 0, 12, 20, 148, side='r', pal=M.VELVET, seed=1)
    M.valance(cv, 0, 12, 18, h=6)
    M.velvet_curtain(cv, 598, 639, 20, 148, side='l', pal=M.VELVET, seed=2)
    M.valance(cv, 598, 639, 18, h=6)
    # 蛛网（角落里，没有风所以不摆）
    M.cobweb(cv, 14, 21, 11, 'tl', seed=1)
    M.cobweb(cv, 596, 21, 12, 'tr', seed=2)
    M.cobweb(cv, 320, 21, 10, 'tl', seed=3)
    return cv, info


def light(scale=None):
    """环境光 + 4 个烛台的点光源。烛光只照墙（clip 到 y < 148）：可走带的亮度靠 amb_add 铺平，不跟着烛光一圈圈走。
    scale = {烛台序号: 乘数}：烛光呼吸时某一个烛台的强度。"""
    scale = scale or {}
    L = M.Light(PW, H, amb=0.26, tint=M.T_AMB)
    yy, xx = L.yy, L.xx
    extra = np.zeros((H, PW), np.float32)
    extra -= 0.04 * np.clip((24 - yy) / 24.0, 0, 1)                  # 天花板 / 檐口更暗
    extra -= 0.20 * np.clip((20 - xx) / 20.0, 0, 1) + 0.20 * np.clip((xx - 620) / 20.0, 0, 1)   # 走廊两端往黑暗里延伸
    L.amb_add(np.maximum(extra, -0.17))                              # 环境光 0.26 − 0.17 = 0.09：别减到 0 以下（Light 的色调是除以总亮度算的）
    # 地面铺平：暖色的一层（烛光落在地毯上的底色），不跟着烛台一圈圈走；墙脚一点点接触暗
    fl = np.where(yy >= 149, 0.70, 0.0).astype(np.float32)
    fl -= np.where(yy >= 149, 0.14 * np.clip((156 - yy) / 7.0, 0, 1), 0.0).astype(np.float32)
    L.add(fl, T_FLOOR)
    for i, x in enumerate(CANDLE_X):
        L.point(x, FLAME_BASE - 2, 96, 1.30 * scale.get(i, 1.0), M.T_WARM, sy=1.1, power=1.7, clip=(0, 0, PW, 148))
    L.point(GAME[0] + GAME[2] // 2, GAME[1] + GAME[3] - 5, 40, 0.75, T_CRT, sy=0.9, power=1.4, clip=(0, 60, PW, 148))
    for cx in PORTRAIT_X:                                            # 画框上的小灯：肖像是要调查的东西，眼睛得看得清
        L.point(cx, 98, 34, 0.50, M.T_WARM, sy=0.9, power=1.2, clip=(0, 60, PW, 124))
    return L


def floor_mask():
    m = np.zeros((H, PW), bool)
    m[149:, :] = True
    return m


def field(scale=None):
    return light(scale).field(levels=14, fine=floor_mask(), fine_levels=30)


@lru_cache(maxsize=1)
def base_img():
    cv, _ = albedo()
    return M.apply(cv, field())


# ============================================================ strip
def _cache(raw):
    memo = {}

    def fn(t):
        f = M.frame_of(t, FPS)
        if f not in memo:
            memo[f] = raw(f)
        return memo[f]
    return fn


def _lit_canvas(draw_fn):
    """在透明 Canvas 上按固有色画 strip 的一帧，再乘上底图同一套光照（发光的像素保留原色）。"""
    cv = M.Canvas(PW, H)
    draw_fn(cv)
    return M.apply(cv, field(), floor=0.0)


# --- 烛火：形状一帧都不变，颜色呼吸（b 0–4）；光晕呼吸只留“变了的像素”
FLAME_ROWS = (                  # (dx, 行 r = 离火苗底几行, 颜色序号 0 白芯 … 3 橙)
    (0, 0, 0), (-1, 1, 3), (0, 1, 0), (1, 1, 3), (-1, 2, 3), (0, 2, 1), (1, 2, 3), (0, 3, 1), (0, 4, 2), (0, 5, 3),
)
BREATH = (0, 1, 2, 3, 4, 3, 2, 1)       # 8 帧的亮度级（0 最暗 … 4 最亮），相邻两帧一定不同


def _flame_px(d, x, y, b):
    for (dx, r, ci) in FLAME_ROWS:
        c = M.FLAME[ci]
        k = (b - 2) * 0.05
        c = lt(c, k) if k > 0 else dk(c, 1 + k * 1.3)
        px(d, x + dx, y - r, c)


def _candle_frames(i):
    """第 i 个烛台的 8 帧：墙上光晕（只留和底图不同的像素，限制在半径 24 内：再远的变化肉眼看不出、PNG 却要大好几倍）+ 火苗。"""
    base = np.array(base_img())
    x = CANDLE_X[i]
    yy, xx = np.mgrid[0:H, 0:PW]
    near = (np.hypot(xx - x, (yy - (FLAME_BASE - 2)) * 1.1) < 24)
    cv, _ = albedo()
    out = []
    for f in range(N8):
        s = 1.0 + 0.05 * math.sin(math.tau * f / N8 + i * 1.3)
        im = np.array(M.apply(cv, field({i: s})))
        diff = (im[..., :3] != base[..., :3]).any(-1) & near
        fr = np.zeros((H, PW, 4), np.uint8)
        fr[diff, :3] = im[diff, :3]
        fr[diff, 3] = 255
        img = Image.fromarray(fr, 'RGBA')
        d = ImageDraw.Draw(img)
        _flame_px(d, x, FLAME_BASE, BREATH[f])
        out.append(img)
    return out


@lru_cache(maxsize=None)
def candle_frames(i):
    return _candle_frames(i)


def candle_fn(i):
    def fn(t):
        return candle_frames(i)[M.frame_of(t, FPS)]
    return fn


# --- 肖像的眼睛：偶尔转一下 + 金框上一粒慢慢走过的高光
EYE_PLAN = [(0, 0, 0, 0, 0, 1, 1, 0), (0, 0, -1, -1, -1, 0, 0, 0), (0, 1, 1, 0, 0, 0, -1, -1)]


def _eyes_raw(i):
    def raw(f):
        cx = PORTRAIT_X[i]
        _, info = albedo()
        p = info['portraits'][i]

        def draw(cv):
            M.eye_px(cv.d, p['eyes'], EYE_PLAN[i][f], PORTRAIT_SUBJ[i])
            gx = cx - 14 + 3 + f * 3                                   # 金框上沿珠线上走的一粒高光
            px(cv.d, gx, PORTRAIT_Y[0] + 1, (255, 246, 214))
        return _lit_canvas(draw)
    return raw


# --- 摆钟的钟摆
def _clock_raw(f):
    _, info = albedo()
    return _lit_canvas(lambda cv: M.pendulum_draw(cv.d, info['clock'], f))


# --- 窗前浮尘
def _motes_fn(i):
    wx0 = WIN[i][0]
    poly = [(wx0, WIN_Y0 + 14), (wx0 + WIN_W - 1, WIN_Y0 + 14), (wx0 + WIN_W - 1, WIN_Y0 + WIN_H - 2), (wx0, WIN_Y0 + WIN_H - 2)]
    fn, _ = M.motes_frame_fn(poly, PW, H, n=9, seed=50 + i, col=(255, 240, 200), drift=(1.0, 1.0))
    return fn


# --- 飞蛾：绕着烛台 3 的火苗转圈（翅膀一上一下）
def _moth_raw(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    cx, cy = CANDLE_X[2], FLAME_BASE - 4
    a = math.tau * f / N8
    mx = cx + 12 * math.cos(a)
    my = cy + 7 * math.sin(a * 1.0) - 2
    x, y = int(round(mx)), int(round(my))
    col, wing = (232, 214, 176), (190, 168, 134)
    px(d, x, y, (120, 96, 80))
    up = f % 2 == 0
    px(d, x - 1, y - 1 if up else y + 1, col)
    px(d, x + 1, y - 1 if up else y + 1, col)
    px(d, x - 2, y, wing)
    px(d, x + 2, y, wing)
    return im


# ============================================================ 地板暗门（key trap）
@lru_cache(maxsize=1)
def trap_img():
    """暗门翻开：门板（反面是光木板 + 铁合页，靠在墙上）+ 地毯上一个黑洞（远边能看到一点洞壁，往下全黑）。"""
    cv = M.Canvas(PW, H)
    d = cv.d
    x0, y0, x1, y1 = TRAP
    # 门板（靠墙立起来，y 120–153，比洞宽一点点）
    lx0, lx1, ly0, ly1 = x0 + 1, x1 - 1, 120, 154
    rect(d, lx0, ly0, lx1, ly1, WOOD['md'], outline=M.INK)
    for x in range(lx0 + 1, lx1):
        k = (x - lx0) % 6
        if k == 0:
            vl(d, x, ly0 + 1, ly1 - 1, WOOD['dd'])                      # 板缝
        elif k == 1:
            vl(d, x, ly0 + 1, ly1 - 1, WOOD['lt'])
        if hash01(21, x) < 0.35:
            vl(d, x, ly0 + 3 + int(hash01(22, x) * 12), ly0 + 8 + int(hash01(23, x) * 20), WOOD['dk'])   # 木纹
    for by in (ly0 + 6, ly1 - 8):                                      # 两道横撑
        rect(d, lx0 + 1, by, lx1 - 1, by + 3, WOOD['dk'])
        hl(d, lx0 + 1, lx1 - 1, by, WOOD['md'])
        for xx in range(lx0 + 3, lx1 - 2, 6):
            px(d, xx, by + 1, M.IRON['hi'])                            # 铆钉
    d.line((lx0 + 2, ly1 - 6, lx1 - 2, ly0 + 9), fill=C(WOOD['dd']), width=2)    # 斜撑
    for hx in (lx0 + 5, lx1 - 9):                                      # 铁合页（在门板和地面相接的那一边）
        rect(d, hx, ly1 - 4, hx + 4, ly1 - 1, M.IRON['md'], outline=M.IRON['dd'])
        px(d, hx + 1, ly1 - 3, M.IRON['hi'])
    hl(d, lx0, lx1, ly0 + 1, WOOD['hi'])
    mul_box = M.mul_box
    mul_box(cv.im, (lx0 + 1, ly1 - 12, lx1 - 1, ly1 - 1), (0.78, 0.78, 0.86), level=0.5)       # 贴着地面那段暗一点
    # 洞：梯形（远边窄、近边宽）
    pit = [(x0 + 2, y0), (x1 - 2, y0), (x1 + 1, y1), (x0 - 1, y1)]
    ImageDraw.Draw(cv.im).polygon(pit, fill=C((6, 4, 10)))
    for y in range(y0, y0 + 6):                                        # 远边的洞壁：越往下越黑
        u = (y - y0) / 5.0
        hl(d, x0 + 2 - int(u), x1 - 2 + int(u), y, mix((58, 38, 36), (8, 6, 12), u))
        for xx in range(x0 + 3, x1 - 2, 5):
            px(d, xx, y, mix((30, 20, 22), (6, 4, 10), u))               # 洞壁木板缝
    hl(d, x0 + 1, x1 - 1, y0 - 1, RUG['dd'])                           # 地毯被切开的边（卷起一点）
    hl(d, x0, x1, y1, RUG['dd'])
    hl(d, x0 - 1, x1 + 1, y1 + 1, WOOD['hi'])                          # 近边：地板的厚度
    hl(d, x0 - 1, x1 + 1, y1 + 2, WOOD['dk'])
    for yy in range(y0, y1 + 1):
        px(d, x0 - 1 + (yy - y0) // 9, yy, RUG['dd'])
        px(d, x1 + 1 - (yy - y0) // 9, yy, RUG['dd'])
    return cv


@lru_cache(maxsize=1)
def trap_layer_img():
    cv = trap_img()
    return M.apply(cv, field(), floor=0.0)


# ============================================================ 图层表 / 导出
@lru_cache(maxsize=1)
def tables():
    layers = [M.L_pano('base', base_img(), 1.0, crop=False)]
    for i in range(4):
        fn = candle_fn(i)
        layers.append(M.L_strip('candle%d' % i, M.auto_box(fn, N8, FPS), N8, FPS, fn))
    for i in range(3):
        fn = _cache(_eyes_raw(i))
        layers.append(M.L_strip('eyes%d' % i, M.auto_box(fn, N8, FPS), N8, FPS, fn))
    fn = _cache(_clock_raw)
    layers.append(M.L_strip('clock', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    for i in range(3):
        fn = _motes_fn(i)
        layers.append(M.L_strip('motes%d' % i, M.auto_box(fn, N8, FPS), N8, FPS, fn))
    fn = _cache(_moth_raw)
    layers.append(M.L_strip('moth', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    layers.append(M.L_pano('trap', trap_layer_img(), 1.0, key='trap', crop=True))
    return layers, []


def anchors():
    anc = {k: ([list(p) for p in v] if isinstance(v[0], list) else list(v)) for k, v in ANCHORS.items()}
    anc.update(trap_box=[TRAP[0] - 2, 120, TRAP[2] + 2, TRAP[3] + 4],
               door_box=[LOCK[0] - 3, LOCK[1] - 4, LOCK[0] + LOCK[2] + 3, LOCK[1] + LOCK[3]],
               game_door_box=[GAME[0] - 3, GAME[1] - 4, GAME[0] + GAME[2] + 3, GAME[1] + GAME[3]])
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
    cfg = dict(title='走廊', PW=PW, walk=WALK, base=base_img(), states=[{}, {'trap': 1}], stand=STAND,
               required=REQUIRED, size_limit=250 * 1024, flat=(0, PW, WALK[0], WALK[1] + 1, 18, 0.012),
               flat_skip=[(TRAP[0] - 3, 150, TRAP[2] + 3, 180)])
    M.common_checks(ex, BJ, st, layers, fg, cfg)
    # 烛火不晃：火苗在 5 个亮度级下占的像素位置一模一样；而且每一帧的 strip 里这些位置都有火苗
    masks = set()
    for b in range(5):
        im = A._new(PW, H)
        _flame_px(ImageDraw.Draw(im), CANDLE_X[0], FLAME_BASE, b)
        masks.add(tuple(map(tuple, np.argwhere(np.array(im)[..., 3] > 0))))
    ex.checked('烛火不晃：5 个亮度级的火苗形状种类 = %d（应是 1）' % len(masks), len(masks) - 1)
    miss = 0
    im = A._new(PW, H)
    _flame_px(ImageDraw.Draw(im), 100, FLAME_BASE, 2)
    pts = np.argwhere(np.array(im)[..., 3] > 0) - np.array([0, 100])
    for i in range(4):
        for f in range(N8):
            a = np.array(candle_frames(i)[f])
            miss += sum(int(a[y, x + CANDLE_X[i], 3] == 0) for (y, x) in pts)
    ex.checked('每个烛台每一帧的 strip 里都画着火苗（缺的像素 %d）' % miss, miss)
    # 烛台火苗正好在 anchors.candles 的 x、y 96 上下
    for i, (ax, ay) in enumerate(ANCHORS['candles']):
        ex.checked('烛台 %d 的火苗在 anchors.candles (%d,%d) 附近（火苗 y %d–%d）' % (i, ax, ay, FLAME_BASE - 5, FLAME_BASE),
                   0 if (ax == CANDLE_X[i] and FLAME_BASE - 8 <= ay <= FLAME_BASE + 6) else 1)
    # 地板暗门：翻开后洞里是黑的、门板在墙上；没开时那一块是地毯
    b = np.array(base_img())
    on = np.array(M.compose(tables()[0], [], 0, 0.0, {'trap': 1}))
    x0, y0, x1, y1 = TRAP
    hole = on[y0 + 8:y1 - 1, x0 + 4:x1 - 3, :3].astype(np.int32).sum(-1)
    ex.checked('trap=1：洞里（y %d–%d）几乎全黑（亮度和 > 60 的像素 %d）' % (y0 + 8, y1 - 2, int((hole > 60).sum())), int((hole > 60).sum()))
    closed = b[y0 + 8:y1 - 1, x0 + 4:x1 - 3, :3].astype(np.int32).sum(-1)
    ex.checked('trap=0：暗门位置是地毯（亮度和 > 60 的像素 %d / %d）' % (int((closed > 60).sum()), closed.size),
               0 if (closed > 60).mean() > 0.9 else 1)
    # 画像的眼睛在画像里
    _, info = albedo()
    for i, p in enumerate(info['portraits']):
        ex.checked('肖像 %d 的眼睛在画框里' % i, 0 if all(PORTRAIT_X[i] - 14 < ex_ < PORTRAIT_X[i] + 13 and PORTRAIT_Y[0] < ey < PORTRAIT_Y[1] for ex_, ey in p['eyes']) else 1)
    # 锁着的门：门板上没有锁孔（门洞里没有“暗点 + 暗点”的竖直小孔）
    bb = np.array(base_img())
    hx, hy = LOCK[0] + LOCK[2] - 5, LOCK[1] + (LOCK[3] + LOCK[2] // 2 + 1) // 2 + 4
    keyhole = bb[hy + 6:hy + 8, hx, :3].astype(np.int32).sum(-1)
    ex.checked('锁着的门（%d,%d）没有锁孔（该处亮度和 %s）' % (hx, hy + 6, keyhole.tolist()), 0 if (keyhole > 40).all() else 1)


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch11', 'after')
    os.makedirs(od, exist_ok=True)
    out = Image.new('RGB', (PW, H * 2 + 4), (0, 0, 0))
    out.paste(compose(0, 0.5).convert('RGB'), (0, 0))
    out.paste(compose(0, 0.5, {'trap': 1}).convert('RGB'), (0, H + 4))
    out.resize((out.width * 2, out.height * 2), Image.NEAREST).save(os.path.join(od, 'mansion_corridor_solo.png'))
    print('ok')
