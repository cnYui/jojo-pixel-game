# -*- coding: utf-8 -*-
r"""desert_night —— 第6章「坠机后的夜营」：夜，沙漠，满天星，冷蓝色调 + 篝火的暖光。地图 camp_ch6（6-13 夜营自由走动、6-15 天亮）。
2026-10-19 第三轮（desert 组）新画（改前是 later_stages.desert('night')：三条平涂的沙丘带）。
沙丘 / 岩山 / 地面 / 岩石这些零件和 desert_noon.py、desert_day.py 共用，在 desert_parts.py。

地图 640 宽、ground 160、可走带 y 148–176（月光下的沙地，压得平、对比低）；侧视平视。
月亮在画面左上（月牙，冷白，一圈台阶状的光晕），月光从左上来：沙丘 / 岩山 / 残骸的左上亮、右下暗；篝火在 x 300，附近一圈沙地、石凳、
行李、帐篷右侧被火光染成暖橙（烘进底图），火苗 / 火星 / 火边一圈会跳的光在帧条里。
从左到右（世界坐标）：
  x 0–70      沙地、两丛灌木、一块半埋的岩石；灌木后面一双狐狸眼睛（耳廓狐，帧条：眨眼、偶尔转头）
  x 88–147    行李堆：乔瑟夫的大皮箱（上面一盏点着的马灯）、帆布旅行袋、一只绿色水桶（jerrycan）、一卷红格子毯
  x 150–214   临时帐篷（anchors.tent 在门口前面）：三角形的帆布帐篷（正面朝人，3/4 看得见右侧屋面），左片门帘卷起、
              里面是红色睡袋；帐篷杆从顶上露出来，两边拉着绳子和木桩；右片门帘挨着门缝的下角在夜风里掀起来（帧条）
  x 188–238   从帐篷杆头拉到一根木棍的晾衣绳：挂着一条条纹毛巾、一件衬衫
  x 214       婴儿篮放的点（anchors.cradle，剧情摆，底图只有沙地）
  x 240–360   篝火（anchors.campfire）：一圈石头围着的火塘、交叉的柴、火苗 + 火星 + 烟（帧条 8 帧 @8 fps）；
              四个当凳子的东西（anchors.seats）：x 262 一块平石头（承太郎）、x 340 一只横放的铁皮箱（乔瑟夫）、
              前排 x 322 一块圆石头（波鲁纳雷夫，朝左）、前排 x 278 一块矮石头（花京院 6-14 坐下）——
              前排两块分在火的两边，坐上人也挡不住火（10-19 验收改：原来一块在 x 300 正挡火）；
              火边一把咖啡壶（dallah）、两只铁杯、后面一堆捡来的枯枝；火光照亮一圈沙地（烘进底图）
  x 388–470   从残骸往营地撒过来一路的东西：一只摔开的手提箱（衣服露出来）、甩出来的一张座椅（棕色人造革）、
              一块弯了的蒙皮（带一截红条）、一只木货箱、几颗铆钉 / 碎片
  x 468–604   坠毁的塞斯纳（anchors.wreck）：白漆红饰条、尾翼顶一道红、机身上一串登记号，机头朝左扎进一道沙坎里、
              机尾翘起（机身轴线上翘 16°）；上面那片桨叶往后卷、下面那片扎在沙里，机头撞瘪的皱褶；
              近侧机翼从翼根断下来、躺在机身前面的沙上（翼尖红、断口锯齿 + 垂下来的线缆），只剩一截弯掉的撑杆；
              远侧主轮歪着；舷窗里映着一点篝火；发动机罩缝里冒一缕烟（帧条）；机身下一滩漏出来的油（沙地深一档）
  x 604–640   机身在沙里犁出来的一道沟（从右边过来）、一个掉下来的机轮
天上：深蓝的夜空（顶上更深）、月牙 + 一圈冷光晕、斜着的银河（亮带 + 暗的尘埃带 + 密的小星）、满天星；
几颗亮星会闪（帧条），偶尔一颗流星（帧条）。远处：平顶的岩山剪影（罩着夜雾）、远沙丘；中景：月光下的大沙丘。

图层（从后往前）：
  sky        static              320×180 夜空 + 月亮 + 银河 + 星（不含会闪的那几颗）
  twinkle_*  strip  屏幕坐标     会闪的亮星（每颗一条，8 帧 @4 fps）
  meteor     strip  屏幕坐标     流星（24 帧 @4 fps，每 6 s 划过一次；框里另有一颗亮星一直在闪，保证每帧都在变）
  sky_dawn   pick   key dawn     0 = 1×1 透明；1 = 天快亮：地平线泛白 → 粉橙 → 上面还是蓝紫（星没了，月亮淡了）
  mtn        pano   k 0.12       远处的平顶岩山（夜雾）
  mtn_dawn   pick   key dawn     同一层的黎明调色
  far        pano   k 0.3        远沙丘 + 平沙地
  far_dawn   pick   key dawn
  mid        pano   k 0.6        中景大沙丘（月光）
  mid_dawn   pick   key dawn
  near       pano   k 1          可走带 + 近沙丘 + 帐篷 + 行李 + 火塘（不含火苗）+ 石凳 + 残骸 + 碎片（640 宽）
  near_dawn  pick   key dawn
  fox        strip  k 1          灌木后面的狐狸眼睛（8 帧 @4 fps）
  flap       strip  k 1          帐篷门帘的一角在风里掀起来又落下（8 帧 @4 fps）
  lantern    strip  k 1          皮箱上的马灯：火苗一跳一跳 + 一圈真半透明的暖光（8 帧 @4 fps）
  fire       strip  k 1          篝火：火苗 + 火星 + 烟 + 火塘边一圈会跳的光（8 帧 @8 fps）
  smoke      strip  k 1          残骸发动机罩冒的一缕烟（8 帧 @4 fps）
  flap_dw / smoke_dw  strip  key dawn  门帘 / 烟的黎明换色孪生（同框同帧，盖住夜里颜色的那条；10-19 加，火和马灯是光源不换）
  dawn       tint   key dawn     #ffd8c0 0.08（黎明：再罩一点暖白，把帧条也染一下）
锚点（素材总表 / 规格的值；seats 10-19 验收时改过）：arrive [60,164]、tent [176,156]、cradle [214,164]、campfire [300,162]、
      seats [[262,166],[340,166],[322,174],[278,174]]（承太郎、乔瑟夫、波鲁纳雷夫、花京院）、wreck [540,158]；
      另加 walk_x [8,632]、horizon、moon（屏幕坐标）、fire_pit [300,159]（火塘中心）、
      seat_boxes（四个凳子的框）。不导出凳面高度：sit 动作的锚点在脚下、已经含凳高，
      剧情坐下时脚点 = seats[i]、z = 0（10-19 验收拿掉了 seat_z：4 个数会被当成一个框，也容易被误加到 z 上）、tent_box、wreck_box、altimeter [514,160]（6-13 纪念品的点 = wreck − 26）。
剧情摆（背景不画）：婴儿篮、众人。
注意：bg_jojo.ref_render 不认识 glow / stars 图层，所以火光烘进底图 + 帧条（帧条里的光晕是真半透明，JS 和预览都按 source-over 叠），
星星闪也是帧条。
单独运行：python -B tools\bg_new\desert_night.py → tools\bg_new\_preview\ch6\after\desert_night_solo_*.png
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


def _parts_mod():
    """沙丘 / 岩山 / 地面 / 岩石等零件跟 desert_noon / desert_day 共用（同一个模块名，三张图只加载一次）。"""
    key = 'bg_new_desert_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'desert_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts_mod()
C = P.C
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (148, 176)
MTN_K, FAR_K, MID_K = 0.12, 0.3, 0.6
MTNW, FARW, MIDW = P.layer_w(MTN_K), P.layer_w(FAR_K), P.layer_w(MID_K)
HZ = 116                      # 地平线（远景平沙地的远边）
BACK = 145                    # 近景沙地的后沿（大致；按列起伏）
N_ANIM, FPS_ANIM = 8, 4.0
FIRE_FPS = 8.0                # 火苗跳得快一点（8 帧 @8 fps = 1 s 一圈）
MOON = (62, 34, 8)            # 屏幕坐标 + 半径（天是 static）
FIRE = (300, 159)             # 火塘中心（火苗的根）

ANCHORS = dict(
    arrive=[60, 164],
    tent=[176, 156],                                   # 帐篷门口前面（调查点 y + 8）
    cradle=[214, 164],                                 # 婴儿篮放的点（剧情摆）
    campfire=[300, 162],                               # 篝火（调查点 / 目标箭头）
    seats=[[262, 166], [340, 166], [322, 174], [278, 174]],   # 坐的点（脚点）：承太郎、乔瑟夫、波鲁纳雷夫、花京院（6-14）
    wreck=[540, 158],                                  # 坠毁的塞斯纳（调查点 y + 6）
    walk_x=[8, 632],
)
STAND = ('arrive', 'cradle', 'campfire', 'seats', 'tent', 'wreck')
# 凳子：坐的人朝向（承太郎朝右、乔瑟夫朝左、波鲁纳雷夫朝左、花京院朝右）→ 凳子中心往背后挪 3 px（屁股在脚后面）
# 前排两块在火的两边（火苗 x 294–306 留空）：一块在火正前方的话，坐上去的人整个挡住篝火
SEAT_FACE = (1, -1, -1, 1)
SEAT_W = (15, 16, 13, 12)
SEAT_Z = (6, 7, 6, 6)         # 凳面离地的高度（只是凳子画多高；sit 动作锚点在脚下、已含凳高 → 剧情 z 用 0）

# ============================================================ 调色（夜：冷蓝；火光：暖橙）
SKY_STOPS = [(0.0, (7, 10, 30)), (0.2, (10, 15, 40)), (0.42, (16, 25, 58)), (0.56, (24, 35, 74)),
             (0.63, (34, 46, 88)), (1.0, (42, 54, 98))]
NIGHT_HAZE = (38, 50, 92)
MTN_PAL = ((18, 22, 46), (24, 29, 56), (31, 37, 68), (40, 48, 84), (54, 64, 102))
FAR_DUNE = dict(hi=(84, 94, 134), lit=(68, 78, 118), lit2=(60, 69, 108), toe=(54, 62, 100),
                rip=(58, 66, 104), rip_hi=(76, 86, 124), sh=(42, 48, 84), sh_d=(37, 42, 77),
                sh_l=(47, 53, 89), ink=(33, 37, 70))
FAR_FLAT = (52, 60, 98)
MID_DUNE = dict(hi=(112, 120, 160), lit=(90, 98, 138), lit2=(80, 88, 128), toe=(72, 80, 120),
                rip=(76, 84, 124), rip_hi=(100, 108, 148), sh=(50, 56, 92), sh_d=(44, 49, 84),
                sh_l=(58, 64, 100), ink=(36, 40, 72))
MID_FLAT = (70, 78, 118)
NEAR_DUNE = dict(hi=(128, 136, 172), lit=(106, 114, 152), lit2=(96, 104, 142), toe=(90, 96, 136),
                 rip=(92, 100, 140), rip_hi=(118, 126, 164), sh=(62, 68, 104), sh_d=(52, 57, 94),
                 sh_l=(72, 78, 114), ink=(40, 44, 78))
FLOOR = dict(base=(102, 107, 143), rip=(94, 99, 135), rip_hi=(113, 118, 154), lip=(130, 137, 172),
             edge=(84, 88, 124))
ROCK = dict(ink=(26, 26, 48), deep=(44, 42, 68), sh=(60, 58, 86), mid=(86, 84, 112), lit=(114, 112, 142),
            hi=(140, 140, 170),
            red=dict(deep=(48, 40, 64), sh=(66, 54, 80), mid=(92, 78, 104), lit=(120, 104, 132), hi=(146, 130, 160)),
            pale=dict(deep=(52, 50, 74), sh=(70, 68, 96), mid=(98, 96, 124), lit=(126, 126, 156), hi=(152, 154, 184)))
SHRUB = ((40, 44, 62), (46, 56, 72), (58, 70, 86), (78, 92, 110))
INK = (22, 22, 40)
# 火光：按原像素亮度映射到这条暖色带（保留材质的明暗），再按离火的距离混进去
FIRE_RAMP = [(0.0, (34, 16, 16)), (0.25, (92, 46, 34)), (0.45, (160, 88, 54)), (0.62, (214, 134, 76)),
             (0.8, (244, 182, 110)), (1.0, (255, 226, 168))]
DAWN_TINT = ('#ffd8c0', 0.08)


# ============================================================ 天
def _milky_way(hh=H, ww=W):
    """银河：一条从右下地平线弯到左上的亮带（二次贝塞尔中线），亮度按离中线的距离衰减、被噪声切成一团一团，
    中间偏一侧一道暗的尘埃带。返回 0–1 的亮度图（ww × hh）。"""
    Y, X = np.mgrid[0:hh, 0:ww].astype(np.float64)
    ts = np.linspace(0, 1, 70)
    p0, p1, p2 = np.array([330.0, 122.0]), np.array([246.0, 36.0]), np.array([118.0, -16.0])
    pts = ((1 - ts) ** 2)[:, None] * p0 + (2 * (1 - ts) * ts)[:, None] * p1 + (ts ** 2)[:, None] * p2
    d = np.full((hh, ww), 1e9)
    side = np.zeros((hh, ww))
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        u = np.clip(((X - ax) * dx + (Y - ay) * dy) / L2, 0, 1)
        qx, qy = ax + u * dx, ay + u * dy
        dd = np.hypot(X - qx, Y - qy)
        cr = np.sign(dx * (Y - ay) - dy * (X - ax))                 # 在中线哪一侧（尘埃带只在一侧）
        sel = dd < d
        d = np.where(sel, dd, d)
        side = np.where(sel, cr, side)
    nz = P.fbm2(ww, hh, 9, 9, 401)
    band = np.exp(-(d / 15.0) ** 2) * (0.45 + 0.75 * nz)
    lane = np.exp(-((d - 4.0) / 3.2) ** 2) * (side > 0) * (P.fbm2(ww, hh, 6, 6, 402) > 0.42)
    return np.clip(band - 0.55 * lane, 0, 1), d


def _star_list():
    """满天星：(x, y, 档)；档 0 = 暗（比天亮一点）、1 = 中、2 = 亮。银河里多撒一倍的暗星。"""
    mw, d = _milky_way()
    out = []
    for i in range(300):
        x, y = int(hrange(0, W, i, 411)), int(hrange(0, 124, i, 412))
        r = hash01(i, 413)
        lvl = 2 if r < 0.06 else (1 if r < 0.3 else 0)
        out.append((x, y, lvl))
    for i in range(260):
        x, y = int(hrange(0, W, i, 421)), int(hrange(0, 124, i, 422))
        if mw[y, x] > 0.25 and hash01(i, 423) < mw[y, x] * 1.3:
            out.append((x, y, 0 if hash01(i, 424) < 0.8 else 1))
    return out


# 会闪的亮星（屏幕坐标；不画进底图，帧条里画）：躲开月亮和对白框后面最挤的地方也没关系，只是让天活一点
TWINKLE = [(28, 62), (112, 18), (148, 58), (214, 12), (288, 48), (304, 92)]
METEOR_BOX = (176, 66, 236, 98)
METEOR_STAR = (226, 92)


@lru_cache(maxsize=1)
def sky_img():
    im = P.sky_base(SKY_STOPS, bands=16)
    a = np.array(im).astype(np.float64)
    mw, _ = _milky_way()
    bay = P.bayer(W, H)
    # 银河的亮带：往冷白混，分 3 档抖动（像素画的“光雾”）
    lv = P.dq(mw * 3.2, 4, bay)
    glow = np.array([0, 0.1, 0.2, 0.32])[lv]
    a[..., :3] = a[..., :3] * (1 - glow[..., None]) + np.array((150, 156, 200)) * glow[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    # 月亮的光晕（冷白，台阶状）
    mx, my, mr = MOON
    A._glow(im, mx, my, mr * 5.2, mr * 5.0, (150, 166, 214), 46, rings=5)
    d = ImageDraw.Draw(im)
    base = np.array(im)
    for (x, y, lvl) in _star_list():
        if math.hypot(x - mx, y - my) < mr * 4.2:
            continue
        sky = tuple(int(v) for v in base[y, x, :3])
        col = (mix(sky, (170, 180, 220), 0.35), (176, 186, 226), (236, 240, 255))[lvl]
        px(d, x, y, col)
    for (x, y) in ((70, 88), (182, 30), (250, 70), (12, 20), (300, 22)):              # 几颗静止的十字亮星
        px(d, x, y, (240, 244, 255))
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sky = tuple(int(v) for v in base[y + dy, x + dx, :3])
            px(d, x + dx, y + dy, mix(sky, (190, 200, 240), 0.55))
    for (x, y) in TWINKLE + [METEOR_STAR]:                         # 会闪的星先把天抹干净（帧条整框是不透明的）
        for yy in range(y - 2, y + 3):
            for xx in range(x - 2, x + 3):
                px(d, xx, yy, tuple(int(v) for v in base[yy, xx, :3]))
    # 凸月：亮面 + 明暗交界处暗一档 + 两三块月海；右下缺一块（月亮的暗面比天亮一点点）
    d.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=C((60, 66, 100)))
    m = np.zeros((H, W), bool)
    Y, X = np.mgrid[0:H, 0:W]
    disc = (X - mx) ** 2 + (Y - my) ** 2 <= mr * mr + 0.5
    cut = (X - (mx + 5.5)) ** 2 + (Y - (my + 2.5)) ** 2 <= (mr - 0.5) ** 2
    lit = disc & ~cut
    edge = lit & ((X - (mx + 5.5)) ** 2 + (Y - (my + 2.5)) ** 2 <= (mr + 1.2) ** 2)
    a = np.array(im)
    a[lit, :3] = (238, 236, 214)
    a[edge, :3] = (196, 196, 186)
    for (sx, sy, r) in ((-3, -2, 1.6), (-1, 2, 1.3), (-4, 2, 1.0)):            # 月海
        mm = lit & ((X - (mx + sx)) ** 2 + (Y - (my + sy)) ** 2 <= r * r)
        a[mm, :3] = (206, 204, 190)
    rim = lit & ((X - mx) ** 2 + (Y - my) ** 2 > (mr - 1) ** 2) & (X < mx)
    a[rim, :3] = (252, 250, 236)
    return Image.fromarray(a, 'RGBA')


TW_SEQ = (0, 1, 2, 3, 2, 1, 0, 1)            # 闪烁的档（相邻两帧、首尾都不一样）


def _star_px(d, x, y, lvl, sky):
    """一颗亮星的样子：档 0 暗、1 亮点、2 亮点 + 十字、3 亮点 + 长十字。"""
    if lvl == 0:
        px(d, x, y, mix(sky, (170, 180, 222), 0.4))
        return
    px(d, x, y, (240, 244, 255) if lvl >= 2 else (196, 204, 238))
    if lvl >= 2:
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px(d, x + dx, y + dy, mix(sky, (190, 200, 240), 0.6 if lvl == 3 else 0.4))
    if lvl == 3:
        for (dx, dy) in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            px(d, x + dx, y + dy, mix(sky, (170, 180, 230), 0.3))


def twinkle_frame_fn(i):
    x, y = TWINKLE[i]
    ph = int(hrange(0, 8, i, 431))

    def fn(f):
        im = A._new(W, H)
        sky = sky_img()
        box = (x - 2, y - 2, x + 3, y + 3)
        im.paste(sky.crop(box), box[:2])
        d = ImageDraw.Draw(im)
        s = tuple(int(v) for v in np.array(sky)[y, x, :3])
        _star_px(d, x, y, TW_SEQ[(f + ph) % 8], s)
        return im
    return fn


N_METEOR = 24


def meteor_frame(f):
    """流星：每 24 帧（6 s）划过一次（第 3–5 帧：头亮、尾巴拖长再散）；框里另有一颗亮星一直按 TW_SEQ 闪。"""
    im = A._new(W, H)
    sky = sky_img()
    im.paste(sky.crop(METEOR_BOX), METEOR_BOX[:2])
    d = ImageDraw.Draw(im)
    sa = np.array(sky)
    x, y = METEOR_STAR
    _star_px(d, x, y, TW_SEQ[f % 8], tuple(int(v) for v in sa[y, x, :3]))
    k = f - 3
    if 0 <= k < 3:
        hx, hy = 216 - k * 14, 70 + k * 6                          # 往左下划
        L = (6, 12, 10)[k]
        for j in range(L):
            xx, yy = hx + int(round(j * 2.2)), hy - int(round(j * 0.95))
            if not (METEOR_BOX[0] <= xx < METEOR_BOX[2] and METEOR_BOX[1] <= yy < METEOR_BOX[3]):
                continue
            s = tuple(int(v) for v in sa[yy, xx, :3])
            u = j / max(1, L - 1)
            if k == 2 and hash01(j, 441) < 0.4:                     # 最后一帧尾巴散掉
                continue
            px(d, xx, yy, mix((250, 250, 255), s, u ** 0.8))
    return im


@lru_cache(maxsize=1)
def sky_dawn_img():
    """天快亮：地平线一道白里透粉，往上橙粉 → 紫 → 顶上还是深蓝；星都没了，月亮淡成一个浅色的影子。"""
    im = P.sky_base([(0.0, (30, 34, 78)), (0.25, (58, 54, 108)), (0.42, (108, 80, 134)), (0.54, (178, 116, 140)),
                     (0.6, (226, 156, 140)), (0.64, (246, 204, 170)), (1.0, (250, 222, 190))], bands=16)
    mx, my, mr = MOON
    d = ImageDraw.Draw(im)
    d.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=C((92, 92, 136)))
    d.ellipse((mx - mr + 1, my - mr + 1, mx + mr - 3, my + mr - 2), fill=C((110, 108, 150)))
    for (x, y) in ((214, 12), (112, 18)):                          # 最亮的两颗还看得见
        px(d, x, y, (170, 170, 214))
    return im


# ============================================================ 远景：岩山（k 0.12）
@lru_cache(maxsize=1)
def mtn_img():
    """远处的平顶岩山剪影：后面一排砂岩台地、前面一道矮石岭；月光从左上，罩着夜雾（往地平线的蓝里混）。"""
    im = A._new(MTNW, H)
    back = P.mesa_heights(MTNW, [(52, 20, 24, 16), (140, 26, 16, 14), (214, 16, 34, 18), (290, 24, 20, 14),
                                 (352, 18, 26, 16)], 511)
    P.paint_ridge(im, 0, MTNW, HZ + 2, back, MTN_PAL, 512, strata=5, shear=0.5)
    im = P.haze(im, 0.42, NIGHT_HAZE)
    front = A._new(MTNW, H)
    fr = P.ridge_heights(MTNW, [(90, 11, 30, 0.3), (176, 14, 36, -0.2), (262, 9, 28, 0.2), (330, 12, 30, 0.0)], 513,
                         jag=0.35, cell=6.0)
    P.paint_ridge(front, 0, MTNW, HZ + 2, fr, MTN_PAL, 514, strata=3)
    front = P.haze(front, 0.26, NIGHT_HAZE)
    im.alpha_composite(front)
    return im


# ============================================================ 远景：远沙丘 + 平沙地（k 0.3）
FAR_DUNES = P.dune_row(-30, FARW + 30, HZ + 2, 4, 9, 523, ratio=(2.8, 4.0), base_jit=1.0)


@lru_cache(maxsize=1)
def far_img():
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    rect(d, 0, HZ, FARW - 1, 160, FAR_FLAT)
    a = np.array(im)
    nz = P.fbm2(FARW, H, 18, 2, 521)
    for y in range(HZ, 161):                                          # 平沙地上几道很淡的横纹（远处的沙垄）
        for x in range(FARW):
            if nz[y, x] > 0.64:
                a[y, x, :3] = (48, 55, 92)
            elif nz[y, x] < 0.3:
                a[y, x, :3] = (58, 66, 104)
    im = Image.fromarray(a, 'RGBA')
    P.paint_dunes(im, FAR_DUNES, FAR_DUNE, 522, ripples=False, streaks=False)
    d = ImageDraw.Draw(im)
    hl(d, 0, FARW - 1, HZ, (62, 72, 112))                             # 地平线一道淡的亮（月光照着远处的沙）
    return P.haze(im, 0.22, NIGHT_HAZE)


# ============================================================ 中景：大沙丘（k 0.6）
MID_DUNES = (P.dune_row(-60, MIDW + 60, 126, 7, 14, 531) +
             P.dune_row(-40, MIDW + 60, 136, 10, 20, 532, big=[(2, 30)]) +
             P.dune_row(-80, MIDW + 80, 146, 7, 13, 533, ratio=(3.2, 4.4)))


@lru_cache(maxsize=1)
def mid_img():
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    rect(d, 0, 130, MIDW - 1, 152, MID_FLAT)
    P.paint_dunes(im, MID_DUNES, MID_DUNE, 534, rip_gap=3.8)
    # 两块从沙里冒出来的矮岩头（月光下只剩亮的顶边和黑的影）
    for (x, b, w, h, sd) in ((150, 141, 14, 8, 1), (380, 142, 11, 6, 2)):
        m = P.poly_m((MIDW, H), [P.rough_poly([(x, b), (x + 2, b - h + 2), (x + w * 0.4, b - h), (x + w - 3, b - h + 1),
                                               (x + w, b)], sd, 0.7)])
        P.shade_rock(im, m, ROCK, 540 + sd, bands=[(3, 'pale'), (40, None)], cracks=1, holes=0, varnish=1)
    ys = np.arange(H, dtype=np.float32)[:, None]
    amt = np.clip(0.2 - (ys - 90) / 60 * 0.12, 0.06, 0.2)               # 上面（远）罩夜雾多一点
    return P.haze(im, amt, NIGHT_HAZE)


# ============================================================ 近景：小工具
def lum_map(rgb, ramp):
    """按亮度把颜色映射到一条色带（火光用）。rgb: (..., 3) float。"""
    l = P.lum(rgb) / 255.0
    pos = np.array([p_ for p_, _ in ramp])
    cols = np.array([c for _, c in ramp], np.float64)
    return np.stack([np.interp(l, pos, cols[:, k]) for k in range(3)], -1)


def fire_light(im, cx, cy, rx, ry, strength=1.0, steps=5, lift=0.85, up=0.7):
    """篝火照亮附近：每个不透明像素按离火的（椭圆）距离 → 0–1 的光量，分 steps 档、档与档之间 Bayer 抖动（像素画的光圈）；
    光量 w 把原色换成“被火照着的暖色”（原亮度提一点再映射到 FIRE_RAMP），混 w。
    比火高的地方光衰减得快（up：火在地上，帐篷顶 / 箱子上沿照不太到）。透明像素不动（近景只能 0 / 255）。"""
    a = np.array(im).astype(np.float64)
    hh, ww = a.shape[:2]
    Y, X = np.mgrid[0:hh, 0:ww].astype(np.float64)
    dy = np.where(Y < cy, (Y - cy) / (ry / up), (Y - cy) / ry)
    dist = np.sqrt(((X - cx) / rx) ** 2 + dy ** 2)
    w = np.clip(1 - dist, 0, 1) ** 1.1 * strength
    bay = P.bayer(ww, hh)
    wq = np.floor(w * steps + bay * 0.999) / steps
    base = a[..., :3]
    warm = lum_map(np.clip(base * (1 + lift * wq[..., None]), 0, 255), FIRE_RAMP)
    out = base * (1 - wq[..., None]) + warm * wq[..., None]
    m = a[..., 3] > 0
    a[..., :3] = np.where(m[..., None], out, base)
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def back_line():
    """近景沙地后沿每列的 y：缓缓起伏。"""
    n = P.fbm1(PW, 44.0, 551, octaves=3)
    return np.round(BACK + 2.0 * n).astype(int)


NEAR_DUNES = (P.dune_row(-10, 70, 147, 6, 11, 561, ratio=(2.8, 3.8)) + P.dune_row(214, 250, 147, 5, 8, 562) +
              P.dune_row(362, 452, 147, 6, 12, 563) + P.dune_row(600, 690, 147, 6, 10, 564))


def draw_shrubs(im, back):
    for (x, w, h, sd) in ((20, 12, 9, 1), (40, 9, 7, 2), (236, 8, 6, 3), (372, 10, 7, 4), (458, 8, 6, 5),
                          (624, 11, 8, 6)):
        y = int(back[x]) + 3
        P.shrub(im, x, y, w, h, sd * 13 + 5, SHRUB)
    d = ImageDraw.Draw(im)
    for (x, h, sd) in ((8, 5, 1), (66, 4, 2), (90, 5, 3), (226, 4, 4), (396, 5, 5), (436, 4, 6), (612, 5, 7)):
        y = int(back[x]) + 2
        P.tuft(d, x, y, h, (70, 78, 100), (58, 64, 88), sd * 7 + 3, lean=1)


def draw_rock_left(im):
    """左边一块半埋的岩石（月光：左上亮）。"""
    m = P.poly_m((PW, H), [P.rough_poly([(52, 147), (54, 140), (60, 136), (69, 135), (76, 139), (79, 147)], 571, 0.8)])
    P.shade_rock(im, m, ROCK, 572, bands=[(4, 'pale'), (5, None), (40, 'red')], cracks=1, holes=1, varnish=2)


# ============================================================ 近景：行李堆 + 马灯
LANTERN = (113, 126)          # 马灯的灯芯（暖光中心）


def draw_luggage(im):
    """行李堆（x 88–147，靠在可走带后沿）：绿色水桶、乔瑟夫的大皮箱（铜包角、两道皮带）上放一盏点着的马灯、
    帆布旅行袋（上面搭一卷红格子毯）。月光从左上：左上亮、右下暗；马灯 / 篝火的暖光后面统一烘。"""
    d = ImageDraw.Draw(im)
    # 水桶（jerrycan，侧面 X 形压筋）
    jc, jl, jd = (54, 66, 56), (74, 88, 72), (36, 44, 40)
    rect(d, 89, 133, 98, 147, jc)
    vl(d, 89, 134, 147, jl)
    vl(d, 98, 133, 147, jd)
    hl(d, 89, 98, 133, jl)
    for k in range(9):
        px(d, 90 + k, 135 + k, jd)
        px(d, 98 - k, 135 + k, jd)
    rect(d, 91, 130, 93, 132, (60, 60, 70))                           # 提手 / 盖
    px(d, 92, 130, (90, 90, 104))
    hl(d, 89, 98, 147, INK)
    # 大皮箱
    bx0, by0, bx1, by1 = 100, 134, 125, 147
    lc, ll, ld = (74, 50, 48), (96, 68, 60), (50, 34, 38)
    rect(d, bx0, by0, bx1, by1, lc)
    hl(d, bx0, bx1, by0, ll)
    vl(d, bx0, by0, by1, ll)
    hl(d, bx0, bx1, by0 + 3, ld)                                       # 盖缝
    vl(d, bx1, by0, by1, ld)
    for x in (bx0 + 6, bx1 - 6):                                       # 两道皮带 + 带扣
        vl(d, x, by0, by1, (44, 30, 32))
        px(d, x, by0 + 5, (150, 132, 90))
    for (x, y) in ((bx0, by0), (bx1, by0), (bx0, by1), (bx1, by1)):    # 铜包角
        px(d, x, y, (150, 128, 84))
    px(d, (bx0 + bx1) // 2, by0 + 4, (160, 140, 96))                   # 锁
    hl(d, bx0, bx1, by1, INK)
    vl(d, bx1 + 1, by0 + 1, by1, INK)
    # 马灯（hurricane lantern）：底座、玻璃罩、铁丝框、顶盖、提环
    lx, ly = LANTERN
    rect(d, lx - 3, 131, lx + 3, 133, (60, 60, 70))                    # 底座（压在箱盖上）
    hl(d, lx - 3, lx + 3, 131, (96, 96, 110))
    rect(d, lx - 2, 124, lx + 2, 130, (150, 120, 80))                  # 玻璃罩（被灯火照亮）
    vl(d, lx - 2, 124, 130, (200, 160, 100))
    rect(d, lx - 1, 126, lx + 1, 129, (250, 214, 140))
    px(d, lx, 125, (255, 244, 200))
    for x in (lx - 3, lx + 3):                                         # 铁丝框
        vl(d, x, 124, 130, (70, 70, 84))
    rect(d, lx - 2, 122, lx + 2, 123, (70, 70, 84))                    # 顶盖
    hl(d, lx - 1, lx + 1, 121, (90, 90, 104))
    for (x, y) in ((lx - 2, 120), (lx - 1, 119), (lx, 119), (lx + 1, 119), (lx + 2, 120)):  # 提环
        px(d, x, y, (84, 84, 98))
    # 帆布旅行袋 + 红格子毯
    bc, bl_, bd = (76, 80, 70), (96, 100, 86), (54, 56, 52)
    d.ellipse((127, 137, 147, 150), fill=C(bc))
    rect(d, 128, 143, 146, 147, bc)
    d.arc((127, 137, 147, 150), 180, 270, fill=C(bl_))
    hl(d, 130, 144, 141, bd)                                           # 拉链
    for x in (132, 141):
        px(d, x, 140, (120, 112, 90))
    hl(d, 128, 146, 147, INK)
    for x in range(129, 143):                                          # 毯子卷（红格）
        for y in range(133, 138):
            c = (112, 40, 48) if ((x // 2 + y // 2) % 2) else (84, 30, 40)
            if y == 133:
                c = (134, 60, 66)
            px(d, x, y, c)
    for y in range(133, 138):                                          # 卷的两头
        px(d, 128, y, (70, 26, 34))
        px(d, 143, y, (96, 36, 44))


# ============================================================ 近景：帐篷
TENT_X, TENT_BASE, TENT_TOP = 176, 147, 121


def tent_poly():
    """帐篷正面（三角形）+ 往右后方退的右侧屋面（3/4 视角，显出体积）。"""
    front = [(154, TENT_BASE), (TENT_X, TENT_TOP), (198, TENT_BASE)]
    side = [(TENT_X, TENT_TOP), (TENT_X + 12, TENT_TOP - 3), (210, TENT_BASE - 3), (198, TENT_BASE)]
    return front, side


CANVAS = ((92, 94, 108), (112, 114, 128), (72, 72, 90), (54, 54, 72))     # 帆布：中、亮、暗、更暗


def draw_tent(im):
    """临时帐篷：帆布（白天是卡其色，月光下发灰蓝）、正面两片门帘：左片卷起来系住（露出里面的黑和红色睡袋），
    右片垂着（下角在帧条里抖）；顶上露出帐篷杆头；两根拉绳斜拉到木桩。缝线、门帘边一道深色。"""
    d = ImageDraw.Draw(im)
    front, side = tent_poly()
    cv, cv_l, cv_d, cv_dd = CANVAS
    # 右侧屋面（暗一档）+ 屋面上两道缝线
    d.polygon(side, fill=C(cv_d))
    for k in (0.35, 0.7):
        x0 = TENT_X + (198 - TENT_X) * k
        y0 = TENT_TOP + (TENT_BASE - TENT_TOP) * k
        d.line([(round(x0), round(y0)), (round(x0 + 12), round(y0 - 3))], fill=C(cv_dd))
    # 正面 + 左边一线亮（月光）
    d.polygon(front, fill=C(cv))
    for y in range(TENT_TOP, TENT_BASE + 1):
        u = (y - TENT_TOP) / (TENT_BASE - TENT_TOP)
        xl = int(round(TENT_X - 22 * u))
        px(d, xl, y, cv_l)
        px(d, xl + 1, y, cv_l)
    # 门：左片卷起（门洞是一个窄三角，里面黑 + 睡袋），右片垂着
    door_top = TENT_TOP + 5
    d.polygon([(TENT_X, door_top), (TENT_X - 9, TENT_BASE), (TENT_X, TENT_BASE)], fill=C((20, 18, 34)))
    rect(d, TENT_X - 7, TENT_BASE - 3, TENT_X - 1, TENT_BASE - 1, (84, 34, 44))   # 睡袋
    hl(d, TENT_X - 7, TENT_X - 1, TENT_BASE - 3, (110, 50, 58))
    px(d, TENT_X - 5, TENT_BASE - 4, (126, 120, 104))
    for k in range(5):                                                 # 卷起来的左片 + 系带
        y = door_top + 8 + k
        x = TENT_X - 9 + k // 2
        px(d, x - 1, y, cv_l)
        px(d, x, y, cv)
        px(d, x + 1, y, cv_dd)
    px(d, TENT_X - 9, door_top + 10, (150, 128, 84))
    d.line([(TENT_X, door_top), (TENT_X, TENT_BASE)], fill=C(cv_dd))   # 门缝
    d.line([(TENT_X, TENT_TOP), (TENT_X + 11, TENT_BASE)], fill=C(cv_d))   # 正面右半的缝线
    # 杆头 + 拉绳 + 木桩
    vl(d, TENT_X, TENT_TOP - 4, TENT_TOP, (120, 100, 76))
    px(d, TENT_X, TENT_TOP - 5, (150, 130, 96))
    for (x1, y1) in ((150, TENT_BASE), (214, TENT_BASE - 1)):
        d.line([(TENT_X, TENT_TOP - 2), (x1, y1)], fill=C((110, 106, 112)))
        vl(d, x1, y1 - 2, y1 + 1, (110, 86, 64))
        px(d, x1, y1 - 3, (140, 116, 86))
    # 墨线：底边、右侧屋面的外沿
    hl(d, 154, 198, TENT_BASE + 1, INK)
    d.line([(198, TENT_BASE), (210, TENT_BASE - 3)], fill=C(INK))
    d.line([(TENT_X + 12, TENT_TOP - 3), (210, TENT_BASE - 3)], fill=C(dk(cv_dd, 0.8)))
    # 帐篷脚下的影子（月光从左上：往右后）
    P.cast_shadow(im, [(150, TENT_BASE + 1), (212, TENT_BASE - 2), (218, TENT_BASE + 1), (156, TENT_BASE + 3)],
                  mul=P.SOFT_MUL)


FLAP_BOX = (TENT_X + 1, TENT_BASE - 9, TENT_X + 12, TENT_BASE + 1)
FLAP_SEQ = (0, 1, 2, 3, 4, 3, 2, 1)           # 门帘下角卷起来多少 px（相邻两帧、首尾都不一样）


def flap_frame(f):
    """右片门帘挨着门缝的那个下角被夜风掀起来又落下（8 帧一圈）：先把底图那一块原样贴上，
    再按“折角”画：折线左下露出门里的黑，折过来的那一小块是帆布背面（暗一档），折线一道亮。"""
    im = A._new(PW, H)
    near = near_parts()[0]
    x0, y0, x1, y1 = FLAP_BOX
    im.paste(near.crop(FLAP_BOX), (x0, y0))
    a = np.array(im)
    cv, cv_l, cv_d, cv_dd = flap_cols()
    k = FLAP_SEQ[f]
    front = P.poly_m((PW, H), [tent_poly()[0]])
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not front[y, x] or x <= TENT_X:
                continue
            s_ = (x - (TENT_X + 1)) + (TENT_BASE - y)
            if s_ < k:
                a[y, x, :3] = (20, 18, 34)                              # 掀起来的地方露出门里的黑
            elif s_ < 2 * k:
                a[y, x, :3] = cv_l if s_ == k else cv_dd                # 折线一道亮 + 折过来的帆布背面
    return Image.fromarray(a, 'RGBA')


@lru_cache(maxsize=1)
def flap_cols():
    """门帘在底图里被火光烘过的颜色（帧条和底图要一样）：取底图门帘中间几个像素的颜色。"""
    near = np.array(near_parts()[0])
    y = TENT_BASE - 6
    mid = tuple(int(v) for v in near[y, TENT_X + 5, :3])
    return mid, lt(mid, 0.12), dk(mid, 0.8), dk(mid, 0.62)


# ============================================================ 近景：火塘、凳子、火边的东西
def seat_boxes():
    """三个凳子的框（x0, y0, x1, y1）：中心按坐的人朝向往背后挪 3 px。"""
    out = []
    for (sx, sy), f, w, z in zip(ANCHORS['seats'], SEAT_FACE, SEAT_W, SEAT_Z):
        cx = sx - 3 * f
        out.append([cx - w // 2, sy - z, cx - w // 2 + w - 1, sy])
    return out


def draw_firepit(im):
    """火塘：一圈烧黑的石头围着灰烬，中间交叉的几根柴（火苗在帧条里）。"""
    d = ImageDraw.Draw(im)
    fx, fy = FIRE
    d.ellipse((fx - 11, fy - 2, fx + 11, fy + 3), fill=C((40, 36, 44)))       # 烧黑的沙
    d.ellipse((fx - 8, fy - 1, fx + 8, fy + 2), fill=C((58, 50, 52)))         # 灰烬
    for (x0, y0, x1, y1) in ((fx - 8, fy + 1, fx + 4, fy - 3), (fx + 8, fy + 1, fx - 3, fy - 4),
                             (fx - 6, fy - 1, fx + 7, fy - 1)):
        d.line([(x0, y0), (x1, y1)], fill=C((70, 48, 40)))
        d.line([(x0, y0 - 1), (x1, y1 - 1)], fill=C((96, 66, 52)))
    for (x, y) in ((fx - 2, fy - 2), (fx + 1, fy - 3), (fx + 3, fy - 1), (fx - 4, fy)):
        px(d, x, y, (200, 90, 40))
    for k in range(10):                                                # 一圈石头（前排大、后排小）
        ang = math.tau * k / 10 + 0.2
        sx = fx + 12 * math.cos(ang)
        sy = fy + 3.2 * math.sin(ang)
        w = 4 if math.sin(ang) > 0 else 3
        h = 3 if math.sin(ang) > 0 else 2
        x0, y0 = int(round(sx - w / 2)), int(round(sy))
        rect(d, x0, y0 - h + 1, x0 + w - 1, y0, (70, 66, 84))
        hl(d, x0, x0 + w - 2, y0 - h + 1, (104, 100, 120))
        px(d, x0 + w - 1, y0, (40, 38, 54))
        hl(d, x0, x0 + w - 1, y0 + 1, (40, 38, 54))


def draw_seats(im):
    """四个凳子：承太郎坐的平石头、乔瑟夫坐的横放铁皮箱、波鲁纳雷夫坐的圆石头、花京院坐的矮石头（凳面高 SEAT_Z）。"""
    (a0, b0, a1, b1), (c0, e0, c1, e1), (g0, h0, g1, h1), (k0, j0, k1, j1) = seat_boxes()
    m = P.poly_m((PW, H), [P.rough_poly([(a0, b1), (a0 + 1, b0 + 2), (a0 + 4, b0), (a1 - 3, b0), (a1, b0 + 2),
                                         (a1, b1)], 581, 0.5)])
    P.shade_rock(im, m, ROCK, 582, bands=[(2, 'pale'), (40, None)], cracks=0, holes=0, varnish=1)
    d = ImageDraw.Draw(im)
    tc, tl_, td = (62, 72, 66), (84, 96, 86), (42, 50, 48)             # 铁皮箱（军绿，铆钉，锁扣）
    rect(d, c0, e0, c1, e1, tc)
    hl(d, c0, c1, e0, tl_)
    vl(d, c0, e0, e1, tl_)
    vl(d, c1, e0, e1, td)
    hl(d, c0, c1, e0 + 2, td)
    for x in (c0 + 2, c1 - 2):
        px(d, x, e0 + 4, (130, 130, 120))
    rect(d, (c0 + c1) // 2 - 1, e0 + 3, (c0 + c1) // 2 + 1, e0 + 4, (120, 110, 80))
    hl(d, c0, c1, e1, INK)
    m = P.poly_m((PW, H), [P.rough_poly([(g0, h1), (g0 + 1, h0 + 2), (g0 + 4, h0), (g1 - 4, h0), (g1 - 1, h0 + 2),
                                         (g1, h1)], 583, 0.6)])
    P.shade_rock(im, m, ROCK, 584, bands=[(2, 'pale'), (40, None)], cracks=0, holes=0, varnish=1)
    m = P.poly_m((PW, H), [P.rough_poly([(k0, j1), (k0 + 1, j0 + 1), (k0 + 3, j0), (k1 - 3, j0), (k1, j0 + 2),
                                         (k1, j1)], 585, 0.6)])          # 花京院的：矮一点、扁一点的一块
    P.shade_rock(im, m, ROCK, 586, bands=[(2, 'pale'), (40, None)], cracks=0, holes=0, varnish=1)
    for (x0, y0, x1, y1) in seat_boxes():                              # 凳子脚下一线影
        P.mul_box(im, (x0 + 1, y1 + 1, x1 + 2, y1 + 1), P.SHADOW_MUL)


def draw_camp_things(im):
    """火边：咖啡壶（dallah）、两只铁杯；后面一堆捡来的枯枝（靠在可走带后沿）。"""
    d = ImageDraw.Draw(im)
    for k in range(9):
        x0 = 318 + int(hrange(0, 10, k, 591))
        y0 = 149 - int(hrange(0, 5, k, 592))
        L = int(hrange(8, 15, k, 593))
        ang = hrange(-0.35, 0.25, k, 594)
        x1, y1 = x0 + int(L * math.cos(ang)), y0 + int(L * math.sin(ang))
        d.line([(x0, y0), (x1, y1)], fill=C((76, 62, 58) if k % 2 else (96, 80, 70)))
        if k % 3 == 0:
            px(d, x1, y1 - 1, (96, 80, 70))
    hl(d, 318, 334, 150, INK)
    cx, cy = 286, 158                                                  # 咖啡壶：壶身、长嘴、尖顶壶盖、把手
    rect(d, cx - 2, cy - 4, cx + 2, cy, (140, 118, 70))
    hl(d, cx - 2, cx + 2, cy - 4, (180, 156, 96))
    vl(d, cx + 2, cy - 4, cy, (96, 80, 50))
    rect(d, cx - 1, cy - 6, cx + 1, cy - 5, (150, 128, 76))
    px(d, cx, cy - 7, (190, 166, 104))
    px(d, cx - 3, cy - 4, (140, 118, 70))
    px(d, cx - 4, cy - 5, (140, 118, 70))
    px(d, cx - 5, cy - 6, (160, 136, 84))
    px(d, cx + 3, cy - 3, (96, 80, 50))
    px(d, cx + 3, cy - 1, (96, 80, 50))
    hl(d, cx - 2, cx + 3, cy + 1, INK)
    for (x, y) in ((314, 161), (318, 160)):                            # 两只铁杯
        rect(d, x, y - 2, x + 1, y, (120, 124, 136))
        px(d, x, y - 2, (170, 174, 186))
        px(d, x + 2, y - 1, (90, 92, 104))


# ============================================================ 近景：坠毁的塞斯纳
# 机身在自己的坐标里画（u = 从机头往机尾，v = 从机腹往上），再按“机头朝左下扎进沙里”的姿态转到世界坐标：
#   机头（u 0, v 0）在 (NOSE_X, NOSE_Y)，机身轴线往右上翘 PITCH 度。所有零件都是多边形 → 转完再填色，边缘干净。
NOSE_X, NOSE_Y = 488.0, 150.0
PITCH = math.radians(16.0)
_CS, _SN = math.cos(PITCH), math.sin(PITCH)
WHITE = dict(hi=(164, 172, 204), lit=(136, 144, 180), mid=(110, 116, 152), sh=(82, 86, 120), deep=(60, 62, 94))
RED = dict(lit=(140, 56, 72), mid=(112, 42, 60), sh=(82, 32, 50))
GLASS, GLASS_HI = (24, 30, 56), (84, 96, 140)


def p2w(u, v):
    return (NOSE_X + u * _CS - v * _SN, NOSE_Y - u * _SN - v * _CS)


def w2p(x, y):
    dx, dy = x - NOSE_X, y - NOSE_Y
    return dx * _CS - dy * _SN, -dx * _SN - dy * _CS


def pm(pts):
    """(u, v) 多边形 → 世界坐标的遮罩。"""
    return P.poly_m((PW, H), [[p2w(u, v) for (u, v) in pts]])


FUSE = [(0, 2), (-1.5, 5), (-2.5, 9), (-2, 14), (0, 17), (8, 18.5), (19, 19.5), (29, 27), (51, 27.5), (78, 21),
        (100, 15.5), (112, 13.5), (113, 11), (108, 9), (80, 5), (58, 1.5), (50, 0), (20, -0.5), (8, 0)]
FIN = [(90, 15.5), (99, 30), (104, 38), (107, 40.5), (113.5, 40.5), (113.5, 14), (104, 15.5)]
STAB = [(97, 13), (116.5, 12.5), (117, 11), (99, 10.5)]
WING_ROOT = [(21, 27), (22.5, 29.5), (27, 31.5), (36, 32), (45, 31), (50, 29.5), (51, 27.5)]
WINDOWS = [[(21, 19.5), (29.5, 26), (30.5, 26), (30.5, 19.5)],
           [(31.5, 18.5), (31.5, 26), (40, 26), (40, 18.5)],
           [(42, 18.5), (42, 26), (49, 26), (51.5, 19)]]
STRIPE = [(1, 8), (60, 9), (100, 11.5), (108, 13), (108, 15), (100, 13.5), (60, 11), (1, 10)]
FIN_BAND = [(103, 35.5), (106, 39.5), (113.5, 39.5), (113.5, 35.5)]
SMOKE_SRC = p2w(10, 19)
WRECK_BOX = [476, 76, 604, 152]


def _prof(pts, u):
    """多边形在 u 处的上 / 下 v（机身明暗按离机腹的相对高度分档）。"""
    vs = []
    n = len(pts)
    for i in range(n):
        (u0, v0), (u1, v1) = pts[i], pts[(i + 1) % n]
        if (u0 - u) * (u1 - u) <= 0 and u0 != u1:
            vs.append(v0 + (v1 - v0) * (u - u0) / (u1 - u0))
    return (min(vs), max(vs)) if vs else (0.0, 1.0)


def shade_skin(a, mask, poly, pal, bay, top_band=0.8):
    """机身蒙皮：按离机腹的相对高度分档（月光从上来：上面亮、机腹暗），档与档之间抖动。"""
    ys, xs = np.nonzero(mask)
    for (y, x) in zip(ys, xs):
        u, v = w2p(x + 0.5, y + 0.5)
        lo, hi = _prof(poly, u)
        r = (v - lo) / max(0.5, hi - lo)
        lv = 0.55 + 3.3 * r + (bay[y, x] - 0.5) * 0.32
        k = ('deep', 'sh', 'mid', 'lit', 'hi')[int(np.clip(math.floor(lv), 0, 4))]
        if r > top_band:
            k = 'hi'
        a[y, x, :3] = pal[k]
        a[y, x, 3] = 255


def outline(a, mask, ink, hi=None):
    """右 / 下边墨线，左 / 上边（向月光的一侧）亮边。"""
    left, right, top, bottom = P.edge_masks(mask)
    a[right | bottom, :3] = ink
    if hi is not None:
        a[(left | top) & ~(right | bottom), :3] = hi


def draw_wreck(im):
    a = np.array(im)
    bay = P.bayer(PW, H)
    # 机身下面一滩漏出来的油（沙地深一档）+ 月光下的影子（往右）
    oil = P.poly_m((PW, H), [[(484, 149), (494, 146), (522, 146), (530, 149), (514, 151), (490, 151)]])
    a[oil & (a[..., 3] > 0), :3] = (a[oil & (a[..., 3] > 0), :3] * np.array((0.7, 0.7, 0.78))).astype(np.uint8)
    im.paste(Image.fromarray(a, 'RGBA'))
    P.cast_shadow(im, [(500, 147), (592, 132), (606, 140), (598, 147), (520, 150)], mul=P.SOFT_MUL)
    a = np.array(im)
    # 远侧的主起落架（机身后面）：歪的弹簧腿 + 机轮
    d = ImageDraw.Draw(im)
    a_img = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(a_img)
    gx, gy = p2w(44, 0)
    d.line([(round(gx), round(gy)), (round(gx + 5), round(gy + 6))], fill=C((70, 72, 96)))
    d.ellipse((round(gx + 1), round(gy + 3), round(gx + 9), round(gy + 10)), fill=C((22, 22, 32)))
    d.ellipse((round(gx + 4), round(gy + 5), round(gx + 6), round(gy + 7)), fill=C((80, 80, 100)))
    a = np.array(a_img)
    # 机身 / 垂尾 / 平尾 / 翼根
    for poly in (STAB, FIN, FUSE):
        m = pm(poly)
        shade_skin(a, m, poly, WHITE, bay)
    m_fuse = pm(FUSE) | pm(FIN) | pm(STAB)
    # 翼根（远侧机翼还连着：机顶上一截翼型）
    m_wing = pm(WING_ROOT) & ~pm(FUSE)
    ys, xs = np.nonzero(m_wing)
    for (y, x) in zip(ys, xs):
        u, v = w2p(x + 0.5, y + 0.5)
        a[y, x, :3] = WHITE['hi'] if v > 30.5 else WHITE['lit']
        a[y, x, 3] = 255
    # 红饰条 + 垂尾的红带
    for poly in (STRIPE, FIN_BAND):
        m = pm(poly) & m_fuse
        ys, xs = np.nonzero(m)
        for (y, x) in zip(ys, xs):
            u, v = w2p(x + 0.5, y + 0.5)
            lo, hi = _prof(STRIPE if poly is STRIPE else FIN, u)
            a[y, x, :3] = RED['lit'] if (v - lo) / max(0.5, hi - lo) > 0.6 else RED['mid']
    # 舷窗：深色玻璃 + 一道斜的月光反光 + 一点篝火的倒影
    for wp in WINDOWS:
        m = pm(wp)
        a[m, :3] = GLASS
        ys, xs = np.nonzero(m)
        for (y, x) in zip(ys, xs):
            u, v = w2p(x + 0.5, y + 0.5)
            if 0 <= (u + v * 0.6) % 9 < 1.4:
                a[y, x, :3] = GLASS_HI
    fx, fy = p2w(35, 21)
    a[int(round(fy)), int(round(fx)), :3] = (200, 120, 70)
    a[int(round(fy)), int(round(fx)) + 1, :3] = (150, 90, 60)
    outline(a, m_fuse | m_wing, INK, None)
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)

    def ln(p0, p1, col):
        d.line([tuple(round(v) for v in p2w(*p0)), tuple(round(v) for v in p2w(*p1))], fill=C(col))
    # 门缝、门把、整流罩的散热百叶、蒙皮接缝、方向舵铰链、登记号
    for (p0, p1) in (((30.5, 3), (30.5, 27)), ((41, 2), (41, 27)), ((30.5, 3), (41, 2)), ((20, 0), (19.5, 19)),
                     ((60, 1.5), (60, 25)), ((80, 5), (80, 20.5)), ((108.5, 14), (109, 40))):
        ln(p0, p1, WHITE['sh'])
    ln((38, 12), (39.5, 12), (60, 60, 80))
    for k in range(4):
        ln((4 + k * 3, 15), (6 + k * 3, 15), WHITE['sh'])
    for k in range(5):                                                 # 登记号（5 个小方块字）
        u0 = 66 + k * 3.4
        ln((u0, 13.5), (u0, 16), (52, 54, 80))
        ln((u0 + 1, 16), (u0 + 1.6, 16), (52, 54, 80))
    # 近侧机翼的撑杆：从机腹往上只剩一截，弯了；近侧翼根撕开的铝皮（锯齿）
    ln((37, 1), (35, 9), (100, 104, 136))
    ln((35, 9), (37.5, 12), (100, 104, 136))
    for k in range(6):
        u = 23 + k * 4.4
        ln((u, 27.5), (u + 1.5, 25 + (k % 2) * 1.5), (64, 66, 96))
    # 螺旋桨：上面那片往后弯（桨尖贴着整流罩），下面那片扎在沙里；红色桨毂
    for (p0, p1) in (((-3, 11), (-4.5, 17)), ((-4.5, 17), (-3.5, 22)), ((-3.5, 22), (-0.5, 25)), ((-0.5, 25), (3, 26))):
        ln(p0, p1, (78, 80, 100))
        ln((p0[0] - 0.9, p0[1]), (p1[0] - 0.9, p1[1]), (128, 130, 150))
    ln((-3, 8), (-5, 2), (78, 80, 100))
    ln((-3.9, 8), (-5.9, 2), (128, 130, 150))
    for (p0, p1) in (((3, 4), (7, 9)), ((5, 3), (9, 6)), ((11, 2), (13, 5)), ((2, 13), (6, 16))):   # 机头撞瘪的皱褶
        ln(p0, p1, WHITE['deep'])
    sx, sy = p2w(-3, 10)
    d.ellipse((round(sx) - 2, round(sy) - 2, round(sx) + 2, round(sy) + 2), fill=C((126, 44, 54)))
    px(d, round(sx) - 1, round(sy) - 1, (170, 80, 86))
    # 断下来的近侧机翼：躺在机身前面的沙上（白色上表面、前缘一道暗、翼尖红、断口锯齿 + 垂下来的线缆）
    wing = [(500, 146), (561, 142), (565, 147), (503, 151)]
    d.polygon(wing, fill=C(WHITE['lit']))
    d.line([(500, 146), (561, 142)], fill=C(WHITE['hi']))
    d.line([(503, 151), (565, 147)], fill=C(INK))
    d.line([(502, 149), (563, 145)], fill=C(WHITE['mid']))             # 副翼 / 襟翼的缝
    d.polygon([(500, 146), (506, 145.6), (509, 150.8), (503, 151)], fill=C(RED['lit']))   # 翼尖
    for k in range(5):                                                 # 断口锯齿
        y = 142 + k
        px(d, 561 + (k % 2) * 2, y, WHITE['sh'])
        px(d, 562 + (k % 2) * 2, y, INK)
    for (x0, y0, x1, y1) in ((563, 144, 568, 149), (564, 146, 567, 151)):
        d.line([(x0, y0), (x1, y1)], fill=C((60, 60, 70)))
    px(d, 568, 149, (170, 90, 60))
    # 机头扎进去的沙坎：把整流罩下半截和下面那片桨叶埋住
    for x in range(468, 507):
        u = (x - 468) / 38.0
        hy = int(round(10 * math.sin(math.pi * min(1.0, u * 1.25)) ** 1.2)) if u < 0.8 else int(round(10 * (1 - u) * 4.2))
        hy = max(0, hy)
        top = 148 - hy
        for y in range(top, 149):
            c = NEAR_DUNE['lit'] if x < 486 else NEAR_DUNE['sh_l']
            if y == top:
                c = NEAR_DUNE['hi'] if x < 486 else NEAR_DUNE['sh']
            px(d, x, y, c)
    # 机身在沙里犁出来的沟（从右边过来）+ 一个掉下来的机轮
    for x in range(598, PW):
        if hash01(x // 3, 601) < 0.85:
            px(d, x, 143, FLOOR['edge'])
            px(d, x, 142, FLOOR['lip'])
            px(d, x, 145, FLOOR['rip_hi'])
    d.ellipse((612, 140, 622, 147), fill=C((24, 24, 34)))
    d.ellipse((615, 142, 619, 145), fill=C((76, 76, 96)))
    hl(d, 613, 621, 147, INK)


def draw_line_laundry(im):
    """帐篷右边一根木棍拉一条晾衣绳（从帐篷杆头拉过来）：挂着一条毛巾和一件衬衫（白天洗的，夜里还没收）。"""
    d = ImageDraw.Draw(im)
    vl(d, 236, 124, 147, (96, 78, 64))                                  # 木棍
    px(d, 236, 123, (120, 100, 80))
    hl(d, 236, 238, 147, INK)
    pts = [(TENT_X + 12, TENT_TOP - 3)]
    for k in range(1, 12):                                             # 绳子中间垂一点
        u = k / 11
        pts.append((TENT_X + 12 + (236 - TENT_X - 12) * u, TENT_TOP - 3 + (124 - TENT_TOP + 3) * u + 3 * math.sin(math.pi * u)))
    d.line([(round(x), round(y)) for (x, y) in pts], fill=C((112, 108, 116)))
    def line_y(x):
        return int(round(np.interp(x, [q[0] for q in pts], [q[1] for q in pts])))
    # 毛巾（条纹）
    x0 = 204
    for x in range(x0, x0 + 6):
        y0 = line_y(x) + 1
        for y in range(y0, y0 + 9):
            px(d, x, y, (120, 124, 150) if (y - y0) % 4 else (84, 64, 100))
        px(d, x, y0 + 9, (70, 72, 96))
    # 衬衫（领口、两只袖子垂着）
    x0 = 216
    for x in range(x0, x0 + 9):
        y0 = line_y(x) + 1
        hh = 10 if 2 <= x - x0 <= 6 else 5
        for y in range(y0, y0 + hh):
            px(d, x, y, (134, 138, 164) if x - x0 < 5 else (112, 116, 144))
        px(d, x, y0 + hh, (78, 80, 104))
    px(d, x0 + 4, line_y(x0 + 4) + 1, (70, 72, 96))                    # 领口


def draw_debris(im):
    """飞机上掉下来的东西：一块弯了的蒙皮（带一截红条）、一只摔开的手提箱（衣服露出来）、甩出来的一张座椅、
    一只木货箱、几颗铆钉 / 碎片——从残骸往营地撒过来一路。"""
    d = ImageDraw.Draw(im)
    # 甩出来的座椅（棕色人造革，侧倒：靠背朝左倒在沙上，座架朝天）
    sc, sl, sd = (86, 60, 58), (108, 78, 72), (60, 42, 46)
    rect(d, 406, 141, 419, 146, sc)                                     # 坐垫（竖着）
    hl(d, 406, 419, 141, sl)
    d.polygon([(404, 146), (407, 137), (411, 137), (410, 146)], fill=C(sd))   # 靠背
    for x in (408, 413, 417):                                           # 横缝线
        vl(d, x, 142, 146, sd)
    d.line([(419, 141), (423, 137)], fill=C((110, 112, 130)))            # 座架的两根铁管
    d.line([(416, 141), (420, 137)], fill=C((90, 92, 110)))
    hl(d, 404, 420, 147, INK)
    # 木货箱（钉着横板，侧面印着一个字母框）
    bx0, by0, bx1, by1 = 452, 138, 466, 147
    rect(d, bx0, by0, bx1, by1, (96, 80, 70))
    hl(d, bx0, bx1, by0, (120, 102, 88))
    vl(d, bx0, by0, by1, (120, 102, 88))
    for y in (by0 + 3, by0 + 6):
        hl(d, bx0, bx1, y, (70, 58, 54))
    vl(d, bx1, by0, by1, (64, 52, 50))
    rect(d, bx0 + 4, by0 + 1, bx0 + 8, by0 + 2, (60, 50, 50))           # 印字
    hl(d, bx0, bx1 + 1, by1 + 1, INK)
    d.polygon([(428, 147), (432, 141), (444, 140), (447, 146), (440, 148)], fill=C(WHITE['mid']))
    d.line([(432, 141), (444, 140)], fill=C(WHITE['hi']))
    d.line([(431, 144), (446, 143)], fill=C(RED['mid']))
    hl(d, 429, 446, 148, INK)
    # 手提箱：盖子掀开靠在后面，箱里衣服（白衬衫、蓝毛衣、红围巾）
    rect(d, 388, 143, 402, 148, (70, 54, 60))
    hl(d, 388, 402, 143, (96, 76, 80))
    d.polygon([(388, 143), (390, 136), (404, 137), (402, 143)], fill=C((60, 46, 54)))
    d.line([(390, 136), (404, 137)], fill=C((90, 70, 76)))
    for (x, y, c) in ((390, 142, (150, 152, 170)), (391, 142, (150, 152, 170)), (393, 142, (64, 78, 128)),
                      (394, 141, (64, 78, 128)), (396, 142, (130, 44, 54)), (397, 143, (130, 44, 54)),
                      (399, 142, (150, 152, 170)), (403, 147, (130, 44, 54)), (404, 148, (130, 44, 54))):
        px(d, x, y, c)
    hl(d, 388, 405, 149, INK)
    for (x, y) in ((452, 151), (466, 156), (476, 153), (414, 158), (500, 160), (520, 163), (580, 154)):
        px(d, x, y, (140, 146, 176))
        px(d, x + 1, y + 1, (70, 74, 104))


# ============================================================ 近景：拼起来
FOX = (34, 139)               # 狐狸两只眼睛中间（灌木后面）


def draw_fox(im):
    """灌木后面探出来的耳廓狐：月光下浅灰褐的头顶 + 一对实心的大三角耳朵（耳朵里面暗、外沿一线亮），
    下半个头被灌木挡住（灌木后画）；眼睛在帧条里。"""
    d = ImageDraw.Draw(im)
    x, y = FOX
    fur, fur_l, fur_d, ear_in = (78, 78, 100), (100, 100, 124), (56, 56, 78), (52, 44, 64)
    d.ellipse((x - 4, y - 2, x + 4, y + 3), fill=C(fur))
    hl(d, x - 2, x + 2, y - 2, fur_l)
    for s_ in (-1, 1):                                                 # 两只大耳朵（往外斜张）
        bx = x + s_ * 2
        tri = [(bx - 2, y - 1), (bx + 2, y - 1), (bx + s_ * 3, y - 7)]
        d.polygon(tri, fill=C(fur))
        d.line([(bx, y - 2), (bx + s_ * 2, y - 5)], fill=C(ear_in))
        d.line([(bx - s_ * 2, y - 1), (bx + s_ * 3, y - 7)], fill=C(fur_l if s_ < 0 else fur_d))
    px(d, x, y + 2, (40, 40, 58))                                      # 鼻尖


def draw_pebbles(im, back):
    d = ImageDraw.Draw(im)
    for i in range(46):
        x = int(hrange(0, PW, i, 611))
        y = int(hrange(back[x] + 3, 178, i, 612))
        if 240 < x < 360 and y < 176:                                  # 火塘一圈不撒（凳子 / 火边的东西在那）
            continue
        if hash01(i, 613) < 0.3:
            continue
        P.pebble(d, x, y, (92, 96, 130), (116, 120, 154), (74, 78, 112), w=2 if hash01(i, 614) < 0.7 else 3)


@lru_cache(maxsize=1)
def near_parts():
    im = A._new(PW, H)
    back = back_line()
    P.paint_dunes(im, NEAR_DUNES, NEAR_DUNE, 621, rip_gap=3.5)
    P.paint_floor(im, 0, PW, back, H - 1, FLOOR, 622, gap0=3.0, gap1=8.5, dash=0.3)
    draw_fox(im)
    draw_shrubs(im, back)
    draw_rock_left(im)
    draw_luggage(im)
    draw_tent(im)
    draw_line_laundry(im)
    draw_debris(im)
    draw_wreck(im)
    draw_pebbles(im, back)
    draw_firepit(im)
    draw_seats(im)
    draw_camp_things(im)
    # 火光：大圈（照到凳子、柴堆、帐篷右边一点）+ 马灯的小圈
    fire_light(im, FIRE[0], FIRE[1], 104, 22, strength=0.95, steps=5)
    fire_light(im, LANTERN[0], LANTERN[1] + 4, 26, 12, strength=0.75, steps=4, up=0.9)
    im = P.opaque(im)
    return im, back


def near_img():
    return near_parts()[0]


# ============================================================ 会动的（帧条）
FIRE_BOX = (FIRE[0] - 19, FIRE[1] - 36, FIRE[0] + 20, FIRE[1] + 8)
TONGUES = [(-5, 8, 0.0, 3), (-2, 14, 1.3, 4), (1, 18, 2.6, 5), (4, 12, 3.9, 4), (6, 7, 5.2, 3)]
FLAME = ((150, 40, 30), (224, 92, 36), (250, 156, 52), (255, 214, 110), (255, 248, 210))


def fire_frame(f):
    """篝火：几条火舌（根粗、尖细，每帧高低 / 左右晃，外红内黄、根部白）+ 往上飘的火星 + 火头上一点烟 +
    火塘边一圈真半透明的暖光（大小一帧一变 = 火光在跳）。8 帧 @8 fps。"""
    im = A._new(PW, H)
    fx, fy = FIRE
    ph = math.tau * f / N_ANIM
    halo = A._new(PW, H)
    r = 15 + (0, 1, 2, 1, 0, 2, 1, 0)[f]
    A._glow(halo, fx, fy - 1, r, r * 0.38, (255, 150, 60), 64, rings=3)
    im.alpha_composite(halo)
    d = ImageDraw.Draw(im)
    for (dx, h0, p, bw) in TONGUES:
        hh = h0 * (0.82 + 0.18 * math.sin(ph * 2 + p) + 0.08 * math.sin(ph * 3 + p * 1.7))
        n = int(round(hh))
        for r_ in range(n):
            u = r_ / max(1, n - 1)
            wdt = bw * (1 - u) ** 0.75
            cx = fx + dx + math.sin(ph + p + u * 2.2) * 1.6 * u ** 1.3
            y = fy - 1 - r_
            x0, x1 = int(round(cx - wdt / 2)), int(round(cx + wdt / 2))
            for x in range(x0, max(x0, x1) + 1):
                e = abs(x - cx) / max(0.6, wdt / 2)                   # 0 = 火舌中线，1 = 边
                lvl = 4 - u * 3.2 - e * 1.6
                if r_ < 2:
                    lvl += 0.6
                px(d, x, y, FLAME[int(np.clip(round(lvl), 0, 4))])
    for i in range(6):                                                 # 火星
        age = (f + int(hrange(0, 8, i, 631))) % 8
        if age > 5:
            continue
        x = fx + int(hrange(-6, 6, i, 632)) + int(round(math.sin(age * 0.9 + i) * 1.5))
        y = fy - 12 - age * 3 - int(hrange(0, 3, i, 633))
        px(d, x, y, ((255, 236, 170), (255, 200, 110), (250, 150, 70), (220, 110, 50), (170, 70, 40), (120, 50, 40))[age])
    for i in range(3):                                                 # 火头上的烟（稀，往右上飘）
        age = (f + i * 3) % 8
        y = fy - 20 - age * 2
        x = fx - 1 + int(round(age * 0.6)) + i
        for k in range(3):
            xx, yy = x + k - 1, y - (k % 2)
            if hash01(i, age, k, 634) < 0.6 - age * 0.05:
                px(d, xx, yy, (78, 80, 104) if age < 4 else (66, 70, 96))
    return im


SMOKE_BOX = (int(SMOKE_SRC[0]) - 6, 86, int(SMOKE_SRC[0]) + 28, int(SMOKE_SRC[1]) + 2)


def smoke_frame(f):
    """残骸冒的一缕烟：从发动机罩的缝里出来，往上、被夜风吹得往右弯，越高越散；左沿被月光照亮一线。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    sx, sy = SMOKE_SRC
    ph = math.tau * f / N_ANIM
    top = SMOKE_BOX[1] + 2
    for y in range(int(sy) - 1, top, -1):
        u = (sy - y) / (sy - top)
        cx = sx + 16 * u ** 1.6 + math.sin(ph - y * 0.32) * (0.6 + 2.2 * u)
        wdt = 1.2 + 4.0 * u
        dens = 0.95 - 0.75 * u
        for x in range(int(math.floor(cx - wdt)), int(math.ceil(cx + wdt)) + 1):
            e = (x - cx) / max(0.6, wdt)
            if abs(e) > 1:
                continue
            if hash01(x - int(sx), y, f, 641) > dens * (1 - 0.5 * abs(e)):
                continue
            c = (110, 114, 140) if e < -0.45 else ((84, 88, 112) if e < 0.4 else (66, 70, 96))
            px(d, x, y, c)
    return im


FOX_BOX = (FOX[0] - 4, FOX[1] - 1, FOX[0] + 5, FOX[1] + 2)
FOX_SEQ = (0, 1, 0, 2, 3, 2, 0, 4)            # 0 正看、1 往左看、2 眯、3 闭、4 往右看（相邻两帧都不一样）


def fox_frame(f):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    x, y = FOX
    s = FOX_SEQ[f]
    dx = {1: -1, 4: 1}.get(s, 0)
    eye, eye2 = (214, 220, 140), (150, 170, 110)
    for ex in (x - 2, x + 2):
        if s == 3:
            px(d, ex + dx, y + 1, (60, 62, 80))
        elif s == 2:
            px(d, ex + dx, y + 1, eye2)
        else:
            px(d, ex + dx, y, eye)
            px(d, ex + dx, y + 1, eye2)
    return im


LANTERN_BOX = (LANTERN[0] - 8, LANTERN[1] - 8, LANTERN[0] + 9, LANTERN[1] + 10)


def lantern_frame(f):
    """马灯：玻璃罩里的火苗高低一跳一跳，外面一圈真半透明的暖光跟着大小变。"""
    im = A._new(PW, H)
    lx, ly = LANTERN
    r = (6, 7, 6, 5, 6, 7, 7, 5)[f]
    halo = A._new(PW, H)
    A._glow(halo, lx, ly + 1, r, r, (255, 180, 90), 54, rings=2)
    im.alpha_composite(halo)
    d = ImageDraw.Draw(im)
    hgt = (2, 3, 2, 1, 2, 3, 3, 1)[f]
    for k in range(hgt + 1):
        px(d, lx, ly + 2 - k, (255, 248, 210) if k < hgt else (255, 200, 110))
    px(d, lx - 1 + (f % 2), ly + 2, (255, 214, 140))
    return im


def twinkle_box(i):
    x, y = TWINKLE[i]
    return (x - 2, y - 2, x + 3, y + 3)


R_FIRE = P.cache_frames(fire_frame, N_ANIM, FIRE_FPS)
R_SMOKE = P.cache_frames(smoke_frame, N_ANIM, FPS_ANIM)
R_FOX = P.cache_frames(fox_frame, N_ANIM, FPS_ANIM)
R_FLAP = P.cache_frames(flap_frame, N_ANIM, FPS_ANIM)
R_LANTERN = P.cache_frames(lantern_frame, N_ANIM, FPS_ANIM)
R_METEOR = P.cache_frames(meteor_frame, N_METEOR, FPS_ANIM)
R_TW = [P.cache_frames(twinkle_frame_fn(i), N_ANIM, FPS_ANIM) for i in range(len(TWINKLE))]


# ============================================================ 图层表
DAWN_MTN = [(0.0, (40, 30, 64)), (0.5, (86, 62, 100)), (0.8, (140, 96, 124)), (1.0, (186, 138, 150))]
DAWN_FAR = [(0.0, (52, 38, 72)), (0.5, (118, 84, 114)), (0.8, (176, 124, 132)), (1.0, (222, 170, 156))]
DAWN_MID = [(0.0, (46, 32, 60)), (0.35, (98, 70, 100)), (0.6, (164, 114, 124)), (0.8, (214, 156, 144)),
            (1.0, (244, 202, 174))]
# 黎明时盖在夜里颜色的小动画上的“换色孪生”（P.regraded_render，同框同帧、带 key dawn）：第三轮看图发现天亮以后
# 帐篷门帘还是夜里的青灰、飞机冒的烟还是青蓝色。火 / 马灯是光源，天亮了也还是那个颜色，不换；狐狸眼睛同理
R_FLAP_DW = P.regraded_render(R_FLAP, DAWN_MID, keep=0.35)
R_SMOKE_DW = P.regraded_render(R_SMOKE, DAWN_MID, keep=0.35)


@lru_cache(maxsize=1)
def spec():
    """图层表（从后往前）。黎明（key dawn）：天 / 岩山 / 远中近景各有一张梯度映射出来的 pick 盖在原层上
    （同一个视差，像素位置一样）；亮星 / 流星在 sky_dawn 下面，天一亮就看不见了；最后一层很淡的暖白 tint 把帧条也染一下。"""
    near = near_img()
    L = [dict(type='static', name='sky', img=sky_img())]
    for i in range(len(TWINKLE)):
        L.append(dict(type='strip', name='twinkle_%d' % i, box=twinkle_box(i), n=N_ANIM, fps=FPS_ANIM, fn=R_TW[i],
                      screen=True))
    L += [dict(type='strip', name='meteor', box=METEOR_BOX, n=N_METEOR, fps=FPS_ANIM, fn=R_METEOR, screen=True),
          dict(type='pick', name='sky_dawn', key='dawn', values=[0, 1], imgs=[P.blank1(), sky_dawn_img()], k=0.0),
          dict(type='pano', name='mtn', img=mtn_img(), k=MTN_K),
          P.time_pick('mtn_dawn', 'dawn', mtn_img(), MTN_K, DAWN_MTN, keep=0.15),
          dict(type='pano', name='far', img=far_img(), k=FAR_K),
          P.time_pick('far_dawn', 'dawn', far_img(), FAR_K, DAWN_FAR, keep=0.2),
          dict(type='pano', name='mid', img=mid_img(), k=MID_K),
          P.time_pick('mid_dawn', 'dawn', mid_img(), MID_K, DAWN_MID, keep=0.25),
          dict(type='pano', name='near', img=near, k=1.0),
          P.time_pick('near_dawn', 'dawn', near, 1.0, DAWN_MID, keep=0.35),
          dict(type='strip', name='fox', box=FOX_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_FOX, k=1.0),
          dict(type='strip', name='flap', box=FLAP_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_FLAP, k=1.0),
          dict(type='strip', name='lantern', box=LANTERN_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_LANTERN, k=1.0),
          dict(type='strip', name='fire', box=FIRE_BOX, n=N_ANIM, fps=FIRE_FPS, fn=R_FIRE, k=1.0),
          dict(type='strip', name='smoke', box=SMOKE_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_SMOKE, k=1.0),
          dict(type='strip', name='flap_dw', box=FLAP_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_FLAP_DW, k=1.0, key='dawn'),
          dict(type='strip', name='smoke_dw', box=SMOKE_BOX, n=N_ANIM, fps=FPS_ANIM, fn=R_SMOKE_DW, k=1.0, key='dawn'),
          dict(type='tint', name='dawn', color=DAWN_TINT[0], alpha=DAWN_TINT[1], key='dawn')]
    return L


def compose(camX, t=0.5, state=None):
    return P.compose(spec(), camX, t, state)


# ============================================================ 导出
def export(ex, BJ):
    sp = spec()
    layers = P.export_layers(ex, BJ, sp)
    anchors = dict(ANCHORS)
    anchors.update(horizon=HZ, walk_back=BACK, moon=list(MOON[:2]), fire_pit=list(FIRE), seat_boxes=seat_boxes(),
                   tent_box=[150, TENT_TOP - 5, 214, TENT_BASE + 1], wreck_box=list(WRECK_BOX),
                   altimeter=[ANCHORS['wreck'][0] - 26, 160])
    st = ex.stage(PW, GROUND, WALK, layers, [], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, sp)
    return st


def _checks(ex, BJ, st, sp):
    near, back = near_parts()
    P.std_checks(ex, BJ, st, sp, [], '沙漠夜营', PW, WALK, near, sky_img(), ANCHORS, stand=STAND,
                 opaque_bands=[('远景 地平线以下（y %d–150）整条不透明' % HZ, far_img(), (0, HZ, FARW, 150)),
                               ('中景 丘间平地（y 130–150）整条不透明', mid_img(), (0, 130, MIDW, 150))])
    a = np.array(near)[..., :3].astype(np.float32)
    L = P.lum(a)
    # 婴儿篮的点 / 帐篷门口 / 残骸前 / 到达点：脚下只有平沙地（剧情会在 cradle 摆篮子，背景不能先画东西）
    base = np.array(FLOOR['base'], np.float32)
    for name in ('cradle', 'arrive', 'tent', 'wreck'):
        x, y = ANCHORS[name]
        sub = a[y - 4:y + 3, x - 8:x + 9]
        busy = int((np.abs(sub - base).max(-1) > 40).sum())
        ex.checked('%s 点 (%d,%d) 周围 17×7 只有平沙地（离沙色太远的像素）' % (name, x, y), busy)
    # 凳子：每个 seat 点就在自己凳子的框里（坐上去不悬空），凳子不高过 8 px（可走带规矩）
    bad = 0
    for (sx, sy), (x0, y0, x1, y1) in zip(ANCHORS['seats'], seat_boxes()):
        bad += not (x0 <= sx <= x1 and y1 == sy and (y1 - y0) <= 8)
    ex.checked('每个 seat 点都落在自己凳子的框里、凳子 ≤ 8 px 高（不满足的个数）', bad)
    # 10-19：前排的凳子不许挡火——坐的人身体约 ±10 px，火苗 x 294–306 要露出来
    fx = FIRE[0]
    ex.checked('前排凳子离火苗中心都 ≥ 18 px（坐上人也挡不住火；太近的个数）',
               sum(1 for (sx, sy) in ANCHORS['seats'] if sy > FIRE[1] + 8 and abs(sx - fx) < 18))
    # 火光：火塘附近的沙地明显比远处暖、比远处亮（篝火要照亮一圈）
    fx, fy = FIRE
    ring = a[fy + 6:fy + 12, fx - 40:fx + 41].reshape(-1, 3)
    far_ = a[fy + 6:fy + 12, 40:120].reshape(-1, 3)
    warm = float((ring[:, 0] - ring[:, 2]).mean() - (far_[:, 0] - far_[:, 2]).mean())
    ex.checked('火光：火塘前那一圈沙地比远处暖（R−B 多 %.0f ≥ 40）' % warm, 0 if warm >= 40 else 1)
    # 可走带平整：后沿两行（东西的脚 / 影子）、火光圈（x 200–400）、残骸的油渍和断翼（x 470–580）以外，亮度标准差小
    wb = L[WALK[0] + 2:WALK[1] + 1]
    msk = np.ones_like(wb, bool)
    msk[:, 200:400] = False
    msk[:, 470:580] = False
    std = wb[msk].std()
    ex.checked('可走带（火光圈以外）亮度标准差 %.1f ≤ 8' % std, 0 if std <= 8 else 1)
    fr = np.concatenate([np.array(compose(cx, 0.5).convert('RGB'))[108:148].astype(np.float32) for cx in (0, 160, 320)], 1)
    ex.note('可走带亮度：均值 %.0f、标准差 %.1f；后面那一条（镜头 0 / 160 / 320 拼出来）y108–147 均值 %.0f、标准差 %.1f' %
            (wb[msk].mean(), std, P.lum(fr).mean(), P.lum(fr).std()))


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch6', 'after')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        compose(camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'desert_night_solo_%d.png' % camX))
    print('ok')
