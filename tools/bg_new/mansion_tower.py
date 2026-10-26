# -*- coding: utf-8 -*-
r"""mansion_tower —— 第11章「DIO 的馆」塔顶石室（地图 tower_ch11，11-14 会合 → 11-15 第27战努凯萨克 → 11-16 开棺 → 日落）。
2026-10-20 mansion 组（b）按体验版精度从头画。零件在 mansion_parts_b.py（塔顶专用）和 mansion_parts.py（馆里共用）。

地图 320 宽、ground 160、可走带 y 150–172；侧视平视，正对着塔的内墙（像 game_room / mansion_corridor 一样）。
石室偏暗：蓝紫的方整石墙、石板地、梁上一排粗木梁；整面墙最亮的东西是中间那扇圆拱高窗（窗外是日落时的开罗），
所以眼睛会先落在窗和窗下石台上的棺材上。可走带（石板地）亮度压平，人站上去看得清。
从左到右（世界坐标）：
  x 7–52     左边通下去的拱门（旋转楼梯口，anchors.stairs [30,160] = 承太郎他们从这里上来；门里一团从下面透上来的暖光在闪）
  x 56–68    壁烛台（2 根蜡烛）；x 74–93 壁挂旗（暗红 + 金徽）+ 旗下的铁箍箱
  x 112      落地烛台（3 根蜡烛）
  x 122–198  石台（只有台面和正面；棺材 prop.coffin 由剧情摆在 anchors.coffin [160,150]，背景不画棺材）
  x 126–193  窗帘（两边收起来用金绑带系着）+ 帘头；x 142–177 圆拱高窗（anchors.window [160,85]）；
             窗里：日落（太阳沉了一半、云在慢慢飘、开罗的剪影）；key night = 太阳落下去：夜空、一轮满月、星在闪、蝙蝠飞过
  x 208      落地烛台（3 根蜡烛）
  x 214–258  浅一点的石墙 + 壁烛台（x 224）；anchors.landing [236,156] = 努凯萨克背对众人站的楼梯平台（地上一圈很淡的圆形拼花）
  x 266–305  右边通下去的拱门（另一边的楼梯，门里一团冷色的光）
  x 308–319  墙角 + 蛛网
图层（从后往前）：
  base       pano k 1            整张底图（日落时的光；已打光，不透明）
  clouds     strip k 1           窗里的云：每帧右移一截，一圈正好回到原位（白天才有；夜里被 night 层盖住）
  night      static k 1 key night 夜里和白天不同的像素（窗里的夜空、月光、窗边墙面的冷光）——盖在 base 和云上面
  stars / moonclouds / bats  strip key night   星在闪、云从月亮前面飘过、几只蝙蝠绕着窗飞（只在窗洞里，不压在窗棂上）
  flames0–3  strip k 1           四处烛台的火苗（形状会晃，8 帧 1 秒一圈）
  glowL / glowR  strip k 1       两个拱门里透上来的暖 / 冷光一闪一闪
  motes0 / motes1  strip k 1     窗里射出来的两道光里飘的浮尘
  spider     strip k 1           蜘蛛顺着丝线慢慢上下爬
锚点（素材总表定稿）：stairs [30,160]、arrive [50,164]、coffin [160,150]、window [160,85]、landing [236,156]；
      另导出 window_box、dais_box、arch_left_box、arch_right_box（门洞框）。
key：night（0 / 1）= 太阳落下去：窗外变夜空 + 月光，蝙蝠出现。
单独运行：python -B tools\bg_new\mansion_tower.py → tools\bg_new\_preview\ch11\after\mansion_tower_solo.png
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
H = M.H
N8 = M.N8
FPS = M.FPS_SLOW
FPS_FIRE = M.FPS_FIRE

PW = 320
GROUND = 160
WALK = (150, 172)
FLOOR_Y = 146                                  # 墙和地的交线（踢脚板在它上面 5 行）

ANCHORS = {
    'stairs': [30, 160],
    'arrive': [50, 164],
    'coffin': [160, 150],
    'window': [160, 85],
    'landing': [236, 156],
}
REQUIRED = tuple(ANCHORS)
STAND = ('stairs', 'arrive', 'landing')        # 站人的点（y 在可走带里；coffin 是物件的底，不在这里查）

WIN = dict(cx=160, y_top=46, y_bot=118, gw=36)
LEAD_ROWS = (18, 50)                           # 铅条（相对 y_top）；中间 35 的位置是石横档
TRANSOM_Y = WIN['y_top'] + 35
ARCH_L = (10, 92, 40, 54)                      # 左门洞 x0, y0（拱顶）, w, h（门槛行 y0+h−1 = 145）
ARCH_R = (266, 92, 40, 54)
DAIS = (122, 198, 143, 151)                    # 石台 x0, x1, 台面顶行, 正面顶行（正面 4 行）
SCONCES = [(62, 100, 2), (224, 100, 2)]        # 壁烛台 (x, 托盘行, 蜡烛数)
CANDELABRA = [(112, 149), (208, 149)]          # 落地烛台 (x, 底行)
T_FLOOR = (1.00, 0.96, 1.04)                   # 地面铺平的一层光：偏中性的冷，免得石板被烛光推成橙色
SHAFT_A = [(146, 108), (172, 108), (138, 146), (88, 146)]       # 窗里射出的两道光（落在墙上）
SHAFT_B = [(174, 108), (180, 108), (228, 146), (206, 146)]


# ============================================================ 底图（固有色）
@lru_cache(maxsize=2)
def albedo(night):
    """满光时的固有色：返回 (Canvas, info)。night 只换窗外的天（其他一模一样）；光照在 light() 里区分。"""
    cv = M.Canvas(PW, H)
    info = {}
    d = cv.d
    # 墙：方整石（蓝紫），整面一起铺，再盖天花和檐口
    M.ashlar(cv, (0, 14, PW - 1, FLOOR_Y - 1), pal=B.STONE_B, bw=26, bh=10, seed=5)
    B.timber_beam(cv, 0, PW - 1, 0, 13, seed=3)
    M.cornice(cv, 0, PW - 1, 14, pal=B.STONE_B, dentil=True)
    # 墙面的磨损：几道水渍（塔顶漏雨）
    for (sx, sl, sw) in ((40, 70, 4), (102, 52, 3), (252, 58, 5), (312, 60, 4)):
        M.damp_stain(cv, sx, 24, sl, w=sw, seed=sx)
    # 墙脚 + 石板地
    B.plinth(cv, 0, PW - 1, FLOOR_Y - 5, 5, pal=B.STONE_B)
    B.flagstones(cv, 0, PW - 1, FLOOR_Y, H - 1, seed=9)
    # 左右两个拱门
    info['arch_l'] = B.stair_arch(cv, *ARCH_L, glow=(255, 150, 70), seed=1)
    info['arch_r'] = B.stair_arch(cv, *ARCH_R, glow=(150, 120, 230), seed=3)
    for k in ('arch_l', 'arch_r'):                                           # 门里透上来的光：自己发光（不吃环境光）
        for (gx, gy, gc) in B.glow_pixels(info[k], 1.0):
            cv.glow_px(gx, gy, gc)
    # 壁挂旗 + 铁箍箱
    B.banner(cv, 74, 93, 28, 104, seed=2)
    B.chest(cv, 76, 147, 24, 12, seed=5)
    B.skull(cv, 91, 135)                                                      # 箱盖上一颗头骨
    B.books(cv, 54, 147, seed=3)                                              # 箱子左边地上叠着的旧书
    B.goblet(cv, 106, 148)                                                    # 烛台脚边一只倒了的杯子 + 一滩酒
    B.bat_hanging(cv, 238, 22)                                                # 梁下面倒挂着睡觉的一只蝙蝠（夜里窗外那几只就是它的同类）
    # 烟痕要先画（在墙上），烛台后画
    for (sx, sy, _) in SCONCES:
        M.soot(cv, sx, 50, sy - 6, w=5, seed=sx)
    # 右边墙上高处一扇被黑布封死的窄窗（高过人头，免得和努凯萨克的深色头发抢对比），右边漏一线光
    info['slit'] = M.black_window(cv, 247, 26, 14, 62, slit='r', boards=False, seed=6, light=(255, 214, 160))
    # 高窗：石套 + 窗外的天 + 窗棂 / 铅条
    geo = B.arch_window(cv, WIN['cx'], WIN['y_top'], WIN['y_bot'], WIN['gw'])
    sky = B.window_sky(WIN['gw'], WIN['y_bot'] - WIN['y_top'] + 1, bool(night), seed=7)
    full = A._new(PW, H)
    full.paste(sky, (geo['gx0'], WIN['y_top']))
    m_img = Image.fromarray((geo['mask'] * 255).astype(np.uint8), 'L')
    full.putalpha(m_img)
    cv.paste_emissive(full)
    info['blocked'] = B.window_bars(cv, geo, lead_rows=LEAD_ROWS, transom=TRANSOM_Y)
    info['win'] = geo
    # 窗帘 + 帘头（两边收起来）
    M.velvet_curtain(cv, 121, 139, 42, 126, side='l', tie=96, seed=3)
    M.velvet_curtain(cv, 181, 199, 42, 126, side='r', tie=96, seed=4)
    M.valance(cv, 119, 201, 38, h=6)
    # 石台
    B.dais(cv, DAIS[0], DAIS[1], DAIS[2], DAIS[3], 4, seed=2)
    # 烛台
    info['flames'] = {}
    info['flames']['sc0'] = M.sconce(cv, SCONCES[0][0], SCONCES[0][1], arms=SCONCES[0][2], seed=11)
    info['flames']['sc1'] = M.sconce(cv, SCONCES[1][0], SCONCES[1][1], arms=SCONCES[1][2], seed=12)
    info['flames']['cd0'] = M.candelabra(cv, CANDELABRA[0][0], CANDELABRA[0][1], h=26, arms=3, seed=13)
    info['flames']['cd1'] = M.candelabra(cv, CANDELABRA[1][0], CANDELABRA[1][1], h=26, arms=3, seed=14)
    # 蛛网
    M.cobweb(cv, 0, 22, 14, 'tl', seed=1)
    M.cobweb(cv, PW - 1, 22, 13, 'tr', seed=2)
    M.cobweb(cv, 269, 94, 9, 'tl', seed=3)
    # 落点：努凯萨克站的地方，地上一圈很淡的圆形拼花（比周围石板亮 / 暗 5 % 以内，不破坏可走带的平整）
    for r, k in ((20, 0.95), (14, 1.04), (8, 0.96)):
        ell = Image.new('L', (PW, H), 0)
        ImageDraw.Draw(ell).ellipse((236 - r, 158 - r // 3 - 1, 236 + r, 158 + r // 3 + 1), fill=255)
        M.mul_mask(cv.im, np.array(ell) > 0, (k, k, k * 1.02), level=1.0)
    return cv, info


# ============================================================ 光
def light(night, scale=None):
    """环境光（偏紫蓝、很暗）+ 4 处烛光 + 窗里来的光：白天 = 夕阳的暖光（一团 + 两道斜光），夜里 = 月光（冷、弱）。
    烛光只照墙（clip 到 y < 146），可走带靠一层铺平的光——人站上去不会被一圈圈光带切开。"""
    scale = scale or {}
    L = M.Light(PW, H, amb=0.28, tint=M.T_AMB)
    yy, xx = L.yy, L.xx
    extra = -0.05 * np.clip((26 - yy) / 26.0, 0, 1)                         # 天花更暗
    extra -= (0.14 * np.clip((20 - xx) / 20.0, 0, 1) + 0.14 * np.clip((xx - 300) / 20.0, 0, 1)) * (yy < FLOOR_Y)   # 塔是圆的：两边的墙往里收，越来越暗（地面不跟着暗：可走带要平）
    L.amb_add(np.maximum(extra, -0.19))
    fl = np.where(yy >= FLOOR_Y, 0.66, 0.0).astype(np.float32)
    fl -= np.where(yy >= FLOOR_Y, 0.12 * np.clip((FLOOR_Y + 6 - yy) / 6.0, 0, 1), 0.0).astype(np.float32)
    L.add(fl, T_FLOOR)
    for (sx, sy, _) in SCONCES:
        L.point(sx, sy - 4, 70, 1.25, M.T_WARM, sy=1.1, power=1.7, clip=(0, 14, PW, FLOOR_Y))
    for (cx, cy) in CANDELABRA:
        L.point(cx, cy - 28, 78, 1.15, M.T_WARM, sy=1.0, power=1.7, clip=(0, 14, PW, FLOOR_Y))
    if not night:
        L.point(160, 86, 82, 1.0, M.T_SUN, sy=0.95, power=1.35, clip=(0, 22, PW, FLOOR_Y))
        fade = lambda yy_, xx_: np.clip((152 - yy_) / 64.0, 0, 1)            # noqa: E731
        L.poly(SHAFT_A, 0.52, M.T_SUN, soft=1.6, fade=fade)
        L.poly(SHAFT_B, 0.42, M.T_SUN, soft=1.6, fade=fade)
        L.point(160, 146, 44, 0.55, M.T_SUN, sy=2.2, power=1.4, clip=(100, 136, 220, 160))   # 石台台面也吃一点光
    else:
        L.point(160, 86, 74, 0.46, M.T_MOON, sy=0.95, power=1.4, clip=(0, 22, PW, FLOOR_Y))
        fade = lambda yy_, xx_: np.clip((152 - yy_) / 64.0, 0, 1)            # noqa: E731
        L.poly(SHAFT_A, 0.15, M.T_MOON, soft=1.6, fade=fade)
        L.poly(SHAFT_B, 0.12, M.T_MOON, soft=1.6, fade=fade)
        L.point(160, 146, 44, 0.30, M.T_MOON, sy=2.2, power=1.4, clip=(100, 136, 220, 160))
    return L


def floor_mask():
    m = np.zeros((H, PW), bool)
    m[FLOOR_Y:, :] = True
    return m


def field(night, scale=None):
    return light(night, scale).field(levels=14, fine=floor_mask(), fine_levels=30)


@lru_cache(maxsize=2)
def base_img(night=False):
    cv, _ = albedo(night)
    return M.apply(cv, field(night))


@lru_cache(maxsize=1)
def night_overlay():
    """夜里和白天不一样的像素（整个玻璃 + 被月光 / 夕阳照得不同的墙面和石台）：盖在白天的底图上就是夜景。
    玻璃的像素一律算进去（哪怕和白天碰巧同色）：窗里的云 strip 在它下面，夜里必须被盖干净。"""
    a = np.array(base_img(False))
    b = np.array(base_img(True))
    _, info = albedo(False)
    diff = (a[..., :3] != b[..., :3]).any(-1) | info['win']['mask']
    out = np.zeros_like(b)
    out[diff] = b[diff]
    out[..., 3] = np.where(diff, 255, 0)
    return Image.fromarray(out, 'RGBA')


# ============================================================ strip
def _cache(raw, fps):
    memo = {}

    def fn(t):
        f = M.frame_of(t, fps)
        if f not in memo:
            memo[f] = raw(f)
        return memo[f]
    return fn


def _glass_clip(im):
    """窗里的东西（云 / 星 / 蝙蝠）只留在“窗洞里、不是窗棂 / 铅条 / 洞边阴影”的像素上。"""
    _, info = albedo(False)
    ok = info['win']['mask'] & ~info['blocked']
    a = np.array(im)
    a[~ok] = 0
    return Image.fromarray(a, 'RGBA')


def _in_glass(frame_img, gx0, gy0):
    """glass 局部坐标里画好的图 → 整张 PW×H 的透明图。"""
    full = A._new(PW, H)
    full.paste(frame_img, (gx0, gy0))
    return full


def _clouds_raw(night):
    gw = WIN['gw']
    gh = WIN['y_bot'] - WIN['y_top'] + 1
    if night:
        frs = B.cloud_frames(gw, gh, N8, y_rows=(12, 28), seed=5, pal=B.CLOUD_NIGHT)
    else:
        frs = B.cloud_frames(gw, gh, N8, y_rows=(8, 24, 42), seed=3, pal=B.CLOUD_DAY)
    _, info = albedo(False)

    def raw(f):
        return _glass_clip(_in_glass(frs[f], info['win']['gx0'], WIN['y_top']))
    return raw


FPS_CLOUD = 2.0                                  # 云慢：8 帧 @ 2 fps = 4 s 一圈（一帧走 gw/8 ≈ 4 px）


def _stars_raw(f):
    gw = WIN['gw']
    gh = WIN['y_bot'] - WIN['y_top'] + 1
    sky = np.array(B.window_sky(gw, gh, True, seed=7))
    im = A._new(gw, gh)
    d = ImageDraw.Draw(im)
    for i, (x, y, b) in enumerate(B.star_positions(gw, gh, 7)):
        on = ((f + i * 3) % 8) < 5                       # 5/8 亮，3/8 暗（暗 = 比天色亮一点点的点）
        c = mix((230, 230, 255), (120, 116, 170), b * 0.7) if on else tuple(int(v) for v in sky[y, x, :3] * 0.6 + 70)
        px(d, x, y, c)
    _, info = albedo(False)
    return _glass_clip(_in_glass(im, info['win']['gx0'], WIN['y_top']))


def _bats_raw(f):
    gw = WIN['gw']
    gh = WIN['y_bot'] - WIN['y_top'] + 1
    im = A._new(gw, gh)
    d = ImageDraw.Draw(im)
    for i, (cx, cy, ax, ay, ph) in enumerate(((13, 36, 11, 9, 0.0), (20, 24, 8, 7, 2.1), (8, 50, 9, 5, 4.2))):
        a = math.tau * f / N8 + ph
        M.bat(d, cx + ax * math.cos(a), cy + ay * math.sin(a * 1.0), f + i)
    _, info = albedo(False)
    return _glass_clip(_in_glass(im, info['win']['gx0'], WIN['y_top']))


def _flame_fn(points, seed0=0, big=()):
    base = M.flames_frame_fn(points, PW, H, seed0=seed0, big=big)
    return base


def _glow_raw(which, night=False):
    _, info = albedo(night)
    ai = info[which]
    S = (0.80, 0.92, 1.05, 1.18, 1.05, 0.92, 0.80, 0.70)
    basepx = {(x, y): c for (x, y, c) in B.glow_pixels(ai, 1.0)}

    def raw(f):
        im = A._new(PW, H)
        d = ImageDraw.Draw(im)
        for (x, y, c) in B.glow_pixels(ai, S[f]):
            if basepx[(x, y)] != c:
                px(d, x, y, c)
        return im
    return raw


def _spider_raw(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x = 57
    y = 66 + int(round(5 + 5 * math.sin(math.tau * f / N8)))
    vl(d, x, 22, y - 1, (150, 146, 164))                  # 丝线从檐口下面一直垂到蜘蛛（线是挂在檐口线脚上的）
    for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        px(d, x + dx - 0, y + dy, (22, 16, 28))
    for (dx, dy) in ((-2, 0), (-2, 1), (-1, 2), (3, 0), (3, 1), (2, 2)):
        px(d, x + dx, y + dy, (30, 24, 36))
    return im


def _motes_fn(poly, seed):
    fn, _ = M.motes_frame_fn(poly, PW, H, n=9, seed=seed, col=(248, 244, 236), drift=(1.0, 1.0))
    return fn


# ============================================================ 图层表 / 导出
@lru_cache(maxsize=1)
def tables():
    _, info = albedo(False)
    layers = [M.L_pano('base', base_img(False), 1.0, crop=False)]
    fn = _cache(_clouds_raw(False), FPS_CLOUD)
    layers.append(M.L_strip('clouds', M.auto_box(fn, N8, FPS_CLOUD), N8, FPS_CLOUD, fn))
    layers.append(M.L_static('night', night_overlay(), 0, 0, key='night'))
    fn = _cache(_clouds_raw(True), FPS_CLOUD)
    layers.append(M.L_strip('moonclouds', M.auto_box(fn, N8, FPS_CLOUD), N8, FPS_CLOUD, fn, key='night'))
    fn = _cache(_stars_raw, FPS)
    layers.append(M.L_strip('stars', M.auto_box(fn, N8, FPS), N8, FPS, fn, key='night'))
    fn = _cache(_bats_raw, FPS)
    layers.append(M.L_strip('bats', M.auto_box(fn, N8, FPS), N8, FPS, fn, key='night'))
    for i, k in enumerate(('sc0', 'cd0', 'cd1', 'sc1')):
        pts = info['flames'][k]
        fn = _flame_fn(pts, seed0=i * 5, big=())
        layers.append(M.L_strip('flames%d' % i, M.auto_box(fn, N8, FPS_FIRE), N8, FPS_FIRE, fn))
    for name, which in (('glowL', 'arch_l'), ('glowR', 'arch_r')):
        fn = _cache(_glow_raw(which), FPS)
        layers.append(M.L_strip(name, M.auto_box(fn, N8, FPS), N8, FPS, fn))
    for i, poly in enumerate((SHAFT_A, SHAFT_B)):
        fn = _motes_fn(poly, 40 + i)
        layers.append(M.L_strip('motes%d' % i, M.auto_box(fn, N8, FPS), N8, FPS, fn))
    fn = _cache(_spider_raw, FPS)
    layers.append(M.L_strip('spider', M.auto_box(fn, N8, FPS), N8, FPS, fn))
    return layers, []


def anchors():
    anc = {k: list(v) for k, v in ANCHORS.items()}
    g = albedo(False)[1]['win']
    anc.update(window_box=[g['gx0'] - 3, WIN['y_top'] - 3, g['gx1'] + 4, WIN['y_bot'] + 5],
               dais_box=[DAIS[0], DAIS[2], DAIS[1] + 1, DAIS[3] + 4],
               arch_left_box=[ARCH_L[0] - 3, ARCH_L[1] - 4, ARCH_L[0] + ARCH_L[2] + 3, ARCH_L[1] + ARCH_L[3]],
               arch_right_box=[ARCH_R[0] - 3, ARCH_R[1] - 4, ARCH_R[0] + ARCH_R[2] + 3, ARCH_R[1] + ARCH_R[3]])
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
    cfg = dict(title='塔顶', PW=PW, walk=WALK, base=base_img(False), states=[{}, {'night': 1}], stand=STAND,
               required=REQUIRED, size_limit=250 * 1024, flat=(0, PW, WALK[0], WALK[1] + 1, 18, 0.012),
               flat_skip=[(DAIS[0] - 3, 150, DAIS[1] + 4, 160)])      # 石台的正面和接触影压进可走带 1–8 px：它是棺材的座，不算地面
    M.common_checks(ex, BJ, st, layers, fg, cfg)
    # 夜里的底图也整张不透明；night 层盖住白天的玻璃
    nb = np.array(base_img(True))
    ex.checked('夜里的底图整张不透明', int((nb[..., 3] != 255).sum()))
    on = np.array(M.compose(layers, fg, 0, 0.0, {'night': 1}))
    off = np.array(M.compose(layers, fg, 0, 0.0, {}))
    _, info = albedo(False)
    gm = info['win']['mask'] & ~info['blocked']
    same = int((on[..., :3] == off[..., :3]).all(-1)[gm].sum())
    ex.checked('night=1：玻璃里的像素和白天不同（相同的像素 %d / %d）' % (same, int(gm.sum())), int(same > 0.1 * gm.sum()))
    # 窗里夜里的颜色：比白天暗（太阳落下去了）
    lum_on, lum_off = float(M.lum(on[..., :3][gm]).mean()), float(M.lum(off[..., :3][gm]).mean())
    ex.checked('night=1：窗里整体比白天暗（亮度 %.0f → %.0f）' % (lum_off, lum_on), int(lum_on >= lum_off))
    # 白天的云不能在夜里露出来：night=1 时去掉“云”那一层，窗洞里的像素必须一模一样（被 night 层盖干净了）
    no_cloud = [L for L in layers if L['name'] != 'clouds']
    on2 = np.array(M.compose(no_cloud, fg, 0, 0.0, {'night': 1}))
    leak = int((on[..., :3] != on2[..., :3]).any(-1)[gm].sum())
    ex.checked('night=1：窗里没有漏出白天的云（去掉云层前后不同的像素 %d）' % leak, leak)
    # 锚点：window 在窗里、coffin 在石台上、landing 在地上
    g = info['win']
    wx, wy = ANCHORS['window']
    ex.checked('anchors.window 在窗洞里（%d,%d）' % (wx, wy), 0 if g['mask'][wy, wx] else 1)
    cx, cy = ANCHORS['coffin']
    ex.checked('anchors.coffin x 在石台上、棺材底 y 压着台面（台面 %d–%d、正面 %d）' % (DAIS[2], DAIS[3] - 1, DAIS[3]),
               0 if (DAIS[0] <= cx <= DAIS[1] and DAIS[2] < cy <= DAIS[3]) else 1)
    # 石台那一块背景里没画棺材：石台中间正上方（台面以上 6–26 行）是墙，亮度和旁边的墙差不多（没有棺材的金线 / 黑盖）
    b = np.array(base_img(False)).astype(np.float32)
    strip_l = M.lum(b[DAIS[2] - 22:DAIS[2] - 2, 144:152, :3]).mean()
    strip_r = M.lum(b[DAIS[2] - 22:DAIS[2] - 2, 168:176, :3]).mean()
    ex.checked('石台上方没有画棺材（%d 行 × 两侧亮度 %.0f / %.0f，应相近）' % (20, strip_l, strip_r), int(abs(strip_l - strip_r) > 40))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch11', 'after')
    os.makedirs(od, exist_ok=True)
    out = Image.new('RGB', (PW, H * 2 + 4), (0, 0, 0))
    out.paste(compose(0, 0.5).convert('RGB'), (0, 0))
    out.paste(compose(0, 0.5, {'night': 1}).convert('RGB'), (0, H + 4))
    out.resize((out.width * 3, out.height * 3), Image.NEAREST).save(os.path.join(od, 'mansion_tower_solo.png'))
    print('ok')
