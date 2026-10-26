# -*- coding: utf-8 -*-
r"""mansion_parts_b —— 「DIO 的馆」后两张背景（mansion_tower 第11章塔顶、mansion_stairs 终章大楼梯）共用 / 专用的零件。

为什么单开一个文件：mansion_parts.py 同时有别的子代理在改（illusion_corridor / mansion_hall），这里只读它、import 它的
函数（调色、Canvas / Light / apply、图层表、导出框架、小工具），自己的新零件放在这里，两边的改动互不冲突。
小工具（dk / lt / hl / vl / px / rect / mul_box …）原样取自 mansion_parts，风格和已验收的 mansion_corridor / game_room 一致。

内容：
  塔顶石室：flagstones（石板地）、plinth（墙脚）、timber_beam（木梁天花）、arch_window + window_bars（圆拱 / 尖拱高窗）、
            window_sky + cloud_frames + star_positions（窗外的天：日落 / 夜）、dais（石台）、banner（壁挂旗）、chest / skull / books /
            goblet / bat_hanging（小物件）、stair_arch + glow_pixels（通下去的拱门 + 里面透上来的光）。
  大楼梯：   chandelier（吊灯）；楼梯本体 / 扶手 / 墙洞这些只用一次的画法直接写在 mansion_stairs.py 里。
本文件不导出任何背景 key。
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import gradient, hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _parts():
    """mansion_parts（importlib 按路径加载，模块名和 mansion_corridor 等一致，进程里只加载一份）。"""
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
W = M.W
INK = M.INK

# 塔顶 / 楼梯间的石头：比外墙的黑石亮一档、偏紫蓝（夜里点着蜡烛看起来像冷石头）
STONE_B = dict(hi=(128, 122, 144), lt=(104, 98, 122), md=(82, 78, 100), dk=(60, 56, 78), dd=(34, 30, 48))
FLAG = dict(hi=(104, 100, 120), lt=(88, 84, 104), md=(72, 68, 88), dk=(54, 50, 70), dd=(32, 28, 46))   # 地上的石板


# ============================================================ 地面：石板
def flagstones(cv, x0, x1, y0, y1, pal=FLAG, seed=0, seam=0.86, glint=1.05):
    """石板地（侧视的透视）：一排排错缝的大石板，越近越高（行高 4→8）；每块略有色差 + 噪声斑驳，
    板缝（竖 / 横）压暗一点、板的上沿亮一线，再撒几道细裂缝和碎屑。对比压得很低——这是可走带，人站上去要看得清。"""
    a = np.array(cv.im).astype(np.float32)
    ww, hh = x1 - x0 + 1, y1 - y0 + 1
    nz = A._fbm(ww + 8, hh + 8, 5, seed=seed % 997)[4:4 + hh, 4:4 + ww]
    ys = [y0]
    h, i = 4, 0
    while ys[-1] <= y1:
        ys.append(ys[-1] + h)
        i += 1
        h = 4 + i // 2
    for r in range(len(ys) - 1):
        ya, yb = ys[r], min(y1 + 1, ys[r + 1])
        if ya > y1:
            break
        L = 26 + r * 7
        off = int(hrange(0, L, seed, r, 1))
        for k, xa in enumerate(range(x0 - off, x1 + 1, L)):
            f = hrange(0.92, 1.08, seed, r, k, 2)
            xa0, xb = max(x0, xa), min(x1 + 1, xa + L)
            if xa0 >= xb:
                continue
            col = np.array(pal['md'], np.float32) * f
            sub = nz[ya - y0:yb - y0, xa0 - x0:xb - x0]
            a[ya:yb, xa0:xb, :3] = col * (1 + 0.14 * (sub - 0.5))[..., None]
            if x0 <= xa <= x1:
                a[ya:yb, xa, :3] *= seam                               # 竖缝
        a[ya, x0:x1 + 1, :3] *= seam                                   # 横缝
        if ya + 1 < yb:
            a[ya + 1, x0:x1 + 1, :3] *= glint                          # 上沿亮一线
    for i in range(int(ww / 26)):                                      # 细裂缝：沿板走向歪歪扭扭
        x = int(hrange(x0 + 2, x1 - 10, seed, i, 11))
        y = int(hrange(y0 + 2, y1 - 3, seed, i, 12))
        for s in range(int(hrange(4, 10, seed, i, 13))):
            if x0 <= x <= x1 and y0 <= y <= y1:
                a[y, x, :3] = np.array(pal['dk'], np.float32) * 0.92
            x += 1
            y += 1 if hash01(seed, i, s, 14) < 0.3 else 0
    for i in range(int(ww * hh / 90)):                                 # 碎屑 / 小坑
        x = int(hrange(x0, x1, seed, i, 15))
        y = int(hrange(y0, y1, seed, i, 16))
        a[y, x, :3] = np.array(pal['dk'] if hash01(seed, i, 17) < 0.6 else pal['lt'], np.float32)
    a[y0:y1 + 1, x0:x1 + 1, 3] = 255
    cv.im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def plinth(cv, x0, x1, y, h=5, pal=STONE_B):
    """墙脚的石踢脚：顶一道亮、中间一层、底一道墨线；下面落一道影子在地上。y = 顶行。"""
    d = cv.d
    hl(d, x0, x1, y, pal['hi'])
    for k in range(1, h - 1):
        hl(d, x0, x1, y + k, pal['md'] if k % 2 else pal['lt'])
    hl(d, x0, x1, y + h - 1, INK)
    for x in range(x0 + 6, x1, 22):                                    # 石块接缝
        vl(d, x, y + 1, y + h - 2, pal['dd'])
    M.mul_box(cv.im, (x0, y + h, x1, y + h + 1), (0.62, 0.62, 0.72))


# ============================================================ 天花：木梁 + 石托
def timber_beam(cv, x0, x1, y0=0, y1=13, seed=0):
    """天花：最上面几行是暗木板（竖缝），下面一根粗主梁（亮上沿、暗下沿、横木纹、铁箍 + 钉头），梁下一道影子落在墙上。"""
    d = cv.d
    WD = M.WOOD
    for y in range(y0, y0 + 6):
        hl(d, x0, x1, y, mix(WD['dd'], (10, 6, 14), 0.5 + 0.08 * (y - y0)))
    for x in range(x0 + 9, x1, 17):
        vl(d, x, y0, y0 + 5, (14, 8, 12))
    by0 = y0 + 6
    rect(d, x0, by0, x1, y1, WD['md'])
    hl(d, x0, x1, by0, WD['dd'])
    hl(d, x0, x1, by0 + 1, WD['hi'])
    hl(d, x0, x1, by0 + 2, WD['lt'])
    hl(d, x0, x1, y1 - 1, WD['dk'])
    hl(d, x0, x1, y1, INK)
    for i in range(int((x1 - x0) / 6)):                                # 横木纹
        gx = int(hrange(x0, x1 - 12, seed, i, 1))
        gy = int(hrange(by0 + 3, y1 - 2, seed, i, 2))
        hl(d, gx, gx + int(hrange(5, 16, seed, i, 3)), gy, WD['dk'])
    for bx in range(x0 + 30, x1, 96):                                  # 铁箍
        rect(d, bx, by0, bx + 3, y1, M.IRON['md'])
        vl(d, bx, by0, y1, M.IRON['hi'])
        vl(d, bx + 3, by0, y1, M.IRON['dd'])
        px(d, bx + 1, by0 + 2, M.IRON['hi'])
        px(d, bx + 1, y1 - 3, M.IRON['hi'])
    M.mul_box(cv.im, (x0, y1 + 1, x1, y1 + 3), (0.6, 0.6, 0.7))
    M.mul_box(cv.im, (x0, y1 + 4, x1, y1 + 5), (0.82, 0.82, 0.88), level=0.5)


# ============================================================ 圆拱高窗 + 窗外的天
def arch_window(cv, cx, y_top, y_bot, gw, pal=STONE_B, frame=3, pointed=False, rise=None):
    """圆拱高窗的石套 + 窗台。玻璃宽 gw、半圆拱（起拱线 = y_top + gw/2），y_bot = 玻璃最下面一行。
    先画石套（亮左暗右的斜面 + 拱圈上的辐射状拱石缝 + 拱心石）；玻璃里面不画，返回的 mask 给调用者贴窗外的天。
    pointed = True：尖拱（哥特式，rise 自己给：拱顶比半圆高 / 矮都行）；拱石缝改成沿拱圈每 6 列一小道。
    返回 dict(gx0, gx1, y_top, y_bot, spring, rise, mask（H×W bool）)。"""
    d = cv.d
    gx0 = cx - gw // 2
    gx1 = gx0 + gw - 1
    rise = int(rise) if rise is not None else int(round(gw / 2.0))
    spring = y_top + rise
    arch_i = M.arch_rows(gw, rise, pointed=pointed)
    arch_o = M.arch_rows(gw + 2 * frame, rise + frame, pointed=pointed)
    sill_y = y_bot + 1
    for i in range(-frame, gw + frame):                                # 石套：一列一列画（拱圈 + 两侧窗框）
        io = i + frame
        yt = spring - int(round(arch_o[io]))
        c = pal['lt'] if i < gw // 2 else pal['md']
        if i < 0 or i >= gw:
            c = pal['lt'] if i < 0 else pal['dk']
        vl(d, gx0 + i, yt, sill_y + 2, c)
        px(d, gx0 + i, yt, INK)
        px(d, gx0 + i, yt + 1, pal['hi'] if i < gw // 2 else pal['lt'])
    vl(d, gx0 - frame, spring - 1, sill_y + 2, pal['hi'])             # 左外沿一道亮
    vl(d, gx1 + frame, spring - 1, sill_y + 2, pal['dd'])             # 右外沿一道暗
    if not pointed:
        for k in range(1, 8):                                          # 拱石缝：从起拱线往上，每 22.5° 一道（径向）
            a = math.pi * k / 8.0
            r0, r1 = gw / 2.0 + 0.5, gw / 2.0 + frame + 0.5
            d.line((gx0 + gw / 2.0 - 0.5 - r0 * math.cos(a), spring - r0 * math.sin(a),
                    gx0 + gw / 2.0 - 0.5 - r1 * math.cos(a), spring - r1 * math.sin(a)), fill=C(pal['dd']))
        top_o = spring - int(round(arch_o[(gw + 2 * frame) // 2]))
        rect(d, cx - 2, top_o - 2, cx + 1, top_o + 2, pal['lt'], outline=INK)    # 拱心石
        px(d, cx - 1, top_o - 1, pal['hi'])
        px(d, cx + 1, top_o + 2, pal['dk'])
    else:
        for i in range(-frame + 3, gw + frame - 2, 6):                 # 尖拱的拱石缝：拱圈那几 px 里一小道一小道
            io = i + frame
            yt = spring - int(round(arch_o[io]))
            yi = spring - int(round(arch_i[min(max(i, 0), gw - 1)])) if 0 <= i < gw else yt + frame
            for yy in range(yt + 1, min(yt + frame + 1, yi + 1)):
                px(d, gx0 + i, yy, pal['dd'])
    # 窗台：比窗宽出去一截，上沿亮、下面一道暗，再往墙上落一道影子
    xa, xb = gx0 - frame - 3, gx1 + frame + 3
    hl(d, xa, xb, sill_y, pal['hi'])
    hl(d, xa, xb, sill_y + 1, pal['lt'])
    hl(d, xa, xb, sill_y + 2, pal['md'])
    hl(d, xa, xb, sill_y + 3, pal['dk'])
    hl(d, xa, xb, sill_y + 4, INK)
    px(d, xa, sill_y, INK)
    px(d, xb, sill_y, INK)
    M.mul_box(cv.im, (xa + 1, sill_y + 5, xb - 1, sill_y + 8), (0.62, 0.62, 0.72), level=0.6)
    mask = np.zeros((H, cv.w), bool)
    for i in range(gw):
        yt = spring - int(round(arch_i[i]))
        mask[yt:y_bot + 1, gx0 + i] = True
    return dict(gx0=gx0, gx1=gx1, y_top=y_top, y_bot=y_bot, spring=spring, rise=rise, mask=mask, cx=cx)


def window_bars(cv, geo, lead_rows=(), pal=STONE_B, lead=(30, 24, 38), transom=None, bars=True, mullion_x=None):
    """窗里的格子：铅条（深色 1 px 横线，贴在玻璃上）+ 中间一根石窗棂（竖）+ 一道石横档（transom = 横档的 y）。
    都画在玻璃 mask 里面；最后沿玻璃的拱边内侧压一圈深色（窗洞很深，玻璃缩在石套里面）。返回“窗里不透光”的 mask
    （strip 画云 / 蝙蝠时要避开它们，免得压在窗棂上面）。"""
    d = cv.d
    m = geo['mask']
    gx0, gx1, y_top, y_bot, cx = geo['gx0'], geo['gx1'], geo['y_top'], geo['y_bot'], geo['cx']
    blocked = np.zeros_like(m)
    for ry in lead_rows:
        y = y_top + ry
        for x in range(gx0, gx1 + 1):
            if m[y, x]:
                px(d, x, y, lead)
                blocked[y, x] = True
    if bars:
        xs = [cx - 1] if mullion_x is None else list(mullion_x)         # 每根窗棂 2 px 宽（x, x+1）
        for mx in xs:
            for x, c0, c1 in ((mx, pal['lt'], pal['hi']), (mx + 1, pal['md'], pal['dk'])):
                for y in range(y_top, y_bot + 1):
                    if m[y, x]:
                        px(d, x, y, c0 if y % 2 else c1)
                        blocked[y, x] = True
        if transom is not None:
            for x in range(gx0, gx1 + 1):
                for yy, c in ((transom, pal['lt']), (transom + 1, pal['md']), (transom + 2, pal['dk'])):
                    if m[yy, x]:
                        px(d, x, yy, c)
                        blocked[yy, x] = True
    # 窗洞的深度：玻璃拱边内侧一圈深色（左 / 上 2 px、右 1 px）
    inner = m.copy()
    shade = np.zeros_like(m)
    for dx, dy in ((1, 0), (0, 1), (1, 1)):
        shade |= m & ~np.roll(np.roll(m, dx, 1), dy, 0)
    shade |= m & ~np.roll(m, -1, 1)
    ys, xs = np.nonzero(shade & inner)
    for y, x in zip(ys.tolist(), xs.tolist()):
        px(d, x, y, mix(INK, (40, 30, 50), 0.4))
        blocked[y, x] = True
    return blocked


def _disc_glow(a, cx, cy, r_core, r_glow, core, glow_col, k=0.55):
    """给 numpy 图（h×w×3）画一个带光晕的圆（光晕按 Bayer 抖动，硬边像素）。"""
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot(xx - cx, yy - cy)
    bay = A._bayer(w, h)
    t = np.clip(1 - (d - r_core) / max(1.0, r_glow - r_core), 0, 1) ** 2 * k
    m = (d > r_core) & (t > bay * 0.9)
    a[m, :3] = a[m, :3] * 0.45 + np.array(glow_col, np.float32) * 0.55
    a[d <= r_core, :3] = core


def skyline(d, gw, gh, horizon, col, lights=None):
    """远处开罗城的剪影（按窗宽的比例摆）：一排低矮的平屋顶、一座带尖顶的圆顶清真寺（右三分之二处）、三座带阳台的宣礼塔。
    lights = 夜里亮着的几扇小窗的颜色，None = 白天不画。太阳沉在左边那格窗里（gw×0.26），所以这一带只留低矮的屋顶。"""
    x = 0
    k = 0
    while x < gw:                                                      # 平屋顶
        w = int(hrange(3, 7, 31, k))
        h = int(hrange(2, 6, 32, k))
        rect(d, x, horizon - h, x + w - 1, gh - 1, col)
        x += w
        k += 1
    cx = int(gw * 0.70)                                                # 圆顶清真寺：墙身 + 圆顶 + 尖
    rect(d, cx - 5, horizon - 6, cx + 5, gh - 1, col)
    for r in range(5):
        hw = int(round(5 * math.sqrt(max(0.0, 1 - ((r + 0.5) / 5.0) ** 2))))
        hl(d, cx - hw, cx + hw, horizon - 7 - r, col)
    vl(d, cx, horizon - 15, horizon - 12, col)
    px(d, cx, horizon - 16, col)
    for mx, mh in ((int(gw * 0.92), 17), (int(gw * 0.52), 11), (int(gw * 0.05), 9)):      # 宣礼塔
        rect(d, mx, horizon - mh, mx + 1, gh - 1, col)
        rect(d, mx - 1, horizon - mh + 4, mx + 2, horizon - mh + 5, col)
        px(d, mx, horizon - mh - 1, col)
        px(d, mx, horizon - mh - 2, col)
    if lights:
        skyline_lights(d, gw, horizon, lights)


def skyline_lights(d, gw, horizon, col, dim=1.0):
    """剪影里亮着的几扇小窗（夜里很亮，日落时很暗很少）。"""
    for (fx, dy) in ((0.08, 1), (0.34, 2), (0.45, 3), (0.62, 4), (0.78, 2), (0.9, 6), (0.20, 3), (0.58, 1), (0.97, 2)):
        lx = int(gw * fx)
        if 0 <= lx < gw and hash01(lx, dy, 77) < dim:
            px(d, lx, horizon - dy, col)


def star_positions(gw, gh, seed=0, n=10):
    """夜空里的星：[(x, y, 亮度 0..1)]。底图和“星闪”strip 用同一份，闪的就是底图里的那几颗。"""
    hor = int(gh * 0.82)
    out = []
    for i in range(n):
        x, y = int(hrange(0, gw, seed, i, 1)), int(hrange(1, hor - 10, seed, i, 2))
        if abs(x - int(gw * 0.72)) <= 7 and abs(y - 27) <= 8:           # 别落在月亮上
            x = (x + 11) % gw
        out.append((x, y, hash01(seed, i, 3)))
    return out


def window_sky(gw, gh, night, seed=0):
    """窗外的天（gw×gh，不透明 RGBA；贴进玻璃的拱形里时由 mask 裁）。
    日落（night=False）：顶上紫、往下洋红 → 橙 → 地平线一抹金，太阳沉了一半（在地平线上面一点）；
    夜（night=True）：深蓝紫、一撮星、右边一轮满月；开罗的剪影在底部，夜里点着几盏小灯。"""
    im = A._new(gw, gh, (0, 0, 0))
    hor = int(gh * 0.82)
    if night:
        gradient(im, (0, 0, gw, gh), [(0, (6, 6, 26)), (0.5, (22, 22, 62)), (0.85, (52, 42, 92)), (1, (66, 50, 100))], bands=12)
    else:
        gradient(im, (0, 0, gw, gh), [(0, (52, 34, 104)), (0.30, (136, 52, 118)), (0.52, (232, 98, 88)),
                                      (0.66, (252, 160, 84)), (0.78, (255, 188, 100)), (1, (255, 206, 122))], bands=16)
    a = np.array(im).astype(np.float32)
    if night:
        for (x, y, b) in star_positions(gw, gh, seed):                 # 星
            a[y, x, :3] = mix((230, 230, 255), (120, 116, 170), b * 0.7)
        _disc_glow(a, gw * 0.72, 27.0, 4.6, 10.0, (252, 246, 218), (170, 170, 240), k=0.7)
        mx, my = int(gw * 0.72), 27
        for (dx, dy, c) in ((-2, -1, (226, 216, 186)), (1, 1, (222, 212, 180)), (2, -2, (234, 226, 196))):   # 月面的坑
            a[my + dy, mx + dx, :3] = c
    else:
        _disc_glow(a, gw * 0.26, hor - 4.0, 6.0, 14.0, (255, 253, 232), (255, 214, 130), k=0.9)
    # 城的剪影：先画成白色遮罩，再按纵向渐变上色（越往下越黑），屋顶最上面一行被光擦亮（日落：橙，离太阳越近越亮；夜：月光的冷边）
    sil = A._new(gw, gh)
    skyline(ImageDraw.Draw(sil), gw, gh, hor, (255, 255, 255))
    m = np.array(sil)[..., 3] > 0
    top_c, bot_c = ((22, 18, 46), (8, 6, 20)) if night else ((96, 44, 84), (36, 20, 50))
    sun_x = gw * 0.26
    for y in range(gh):
        t = min(1.0, max(0.0, (y - (hor - 17)) / float(max(1, gh - (hor - 17)))))
        a[y, m[y], :3] = mix(top_c, bot_c, t)
    edge = m & ~np.roll(m, 1, 0)
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys.tolist(), xs.tolist()):
        if night:
            a[y, x, :3] = (70, 66, 120)
        else:
            k = max(0.0, 1 - abs(x - sun_x) / (gw * 0.7))
            a[y, x, :3] = mix((150, 70, 90), (255, 170, 90), k)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    skyline_lights(d, gw, hor, (255, 196, 108) if night else (255, 176, 96), dim=1.0 if night else 0.4)
    return im


CLOUD_DAY = ((255, 214, 160), (246, 170, 130), (214, 96, 118), (200, 90, 120))       # 亮面 / 边 / 下沿 / 尾
CLOUD_NIGHT = ((70, 66, 124), (52, 50, 104), (34, 32, 78), (30, 28, 70))             # 夜里的云：比天空略亮的暗蓝，像被月光勾了边


def cloud_frames(gw, gh, n=8, y_rows=(10, 26, 40), seed=0, pal=CLOUD_DAY):
    """日落的云（贴在玻璃里面的整张 gw×gh 透明图 × n 帧）：横向拉长的几缕，上沿被夕阳染亮、下沿偏洋红；
    整个图案的周期 = gw（宽度和玻璃一样），每帧右移 gw/n，n 帧正好走完一圈 → 首尾闭合。"""
    P = gw
    frames = []
    for f in range(n):
        im = A._new(gw, gh)
        d = ImageDraw.Draw(im)
        shift = int(round(f * P / float(n)))
        for ci, y in enumerate(y_rows):
            w = int(hrange(9, 14, seed, ci, 1))
            x0 = int(hrange(0, P, seed, ci, 2))
            for rep in (-1, 0, 1):
                cx = x0 + shift + rep * P
                for k in range(-w // 2, w // 2 + 1):
                    u = abs(k) / (w / 2.0)
                    th = 1 if u > 0.55 else 2
                    px(d, cx + k, y, pal[0] if u < 0.7 else pal[1])
                    if th == 2:
                        px(d, cx + k, y + 1, pal[2])
                px(d, cx - w // 2 - 1, y + 1, pal[3])
        frames.append(im)
    return frames


# ============================================================ 石台 / 壁挂旗 / 铁箍箱
def dais(cv, x0, x1, y_top, y_face, h_face=4, pal=STONE_B, seed=0):
    """石台（棺材座）：台面（浅，y_top..y_face−1，前后一条凹线表示台沿）+ 正面（线脚：亮边、暗缝、小方块浮雕）。
    台高只有几 px，人从前面走过去也不会被它挡着。"""
    d = cv.d
    for y in range(y_top, y_face):
        u = (y - y_top) / max(1, y_face - y_top - 1)
        hl(d, x0, x1, y, mix(pal['lt'], pal['md'], u * 0.6))
    nz = A._fbm(x1 - x0 + 9, y_face - y_top + 9, 4, seed=seed + 21)[4:4 + y_face - y_top, 4:4 + x1 - x0 + 1]
    a = np.array(cv.im).astype(np.float32)                             # 台面的石头纹理：噪声一点点明暗
    a[y_top:y_face, x0:x1 + 1, :3] *= (1 + 0.20 * (nz - 0.5))[..., None]
    cv.im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))
    d = cv.d
    hl(d, x0, x1, y_top, pal['hi'])
    hl(d, x0 + 1, x1 - 1, y_top + 1, pal['dk'])                       # 台沿的凹线
    for x in range(x0 + 5, x1 - 3, 9):                                 # 台面上的接缝
        px(d, x, y_top + 2, pal['dk'])
        px(d, x, y_top + 3, pal['dk'])
    for k in range(h_face):
        c = pal['hi'] if k == 0 else (pal['md'] if k < h_face - 1 else pal['dk'])
        hl(d, x0, x1, y_face + k, c)
    for x in range(x0 + 4, x1 - 3, 12):                                # 正面的小方块浮雕
        rect(d, x, y_face + 1, x + 4, y_face + h_face - 2, pal['lt'], outline=pal['dd'])
        px(d, x + 1, y_face + 1, pal['hi'])
    hl(d, x0, x1, y_face + h_face, INK)
    vl(d, x0, y_top, y_face + h_face, INK)
    vl(d, x1, y_top, y_face + h_face, INK)
    M.mul_box(cv.im, (x0 - 1, y_face + h_face + 1, x1 + 3, y_face + h_face + 3), (0.55, 0.55, 0.66))   # 接触影
    M.mul_box(cv.im, (x0 + 2, y_face + h_face + 4, x1 + 1, y_face + h_face + 4), (0.8, 0.8, 0.88), level=0.5)


def banner(cv, x0, x1, y_rod, y_bot, pal=None, seed=0, emblem=True):
    """壁挂旗：铜杆（两端球）、竖褶（亮 / 中 / 暗循环）、两边金边、下摆燕尾 + 金流苏，中间一个金色圆徽。"""
    pal = pal or M.VELVET
    d = cv.d
    w = x1 - x0 + 1
    hl(d, x0 - 3, x1 + 3, y_rod, M.GOLD['md'])
    hl(d, x0 - 3, x1 + 3, y_rod - 1, M.GOLD['hi'])
    for sx in (x0 - 4, x1 + 4):
        rect(d, sx - 1, y_rod - 2, sx + 1, y_rod + 1, M.GOLD['lt'], outline=INK)
        px(d, sx - 1, y_rod - 2, M.GOLD['hi'])
    notch = max(4, w // 3)
    for i in range(w):
        u = i / max(1, w - 1)
        ph = (u * (w / 3.4) + hash01(seed, 1) * 0.3) % 1.0
        c = pal['hi'] if ph < 0.14 else pal['lt'] if ph < 0.36 else pal['md'] if ph < 0.66 else pal['dk']
        bot = y_bot - int(round(notch * (1 - abs(u * 2 - 1))))          # 燕尾：中间短、两边长
        for y in range(y_rod + 2, bot + 1):
            cc = c
            if y < y_rod + 6:
                cc = dk(c, 0.82)                                       # 杆下面一道褶影
            px(d, x0 + i, y, cc)
        px(d, x0 + i, bot, pal['dd'])
        if i % 2 == 0:
            px(d, x0 + i, bot + 1, M.GOLD['md'])                       # 流苏
            px(d, x0 + i, bot + 2, M.GOLD['dk'])
    vl(d, x0, y_rod + 2, y_bot, M.GOLD['md'])                          # 金边
    vl(d, x1, y_rod + 2, y_bot, M.GOLD['dk'])
    hl(d, x0, x1, y_rod + 8, M.GOLD['md'])
    if emblem:
        cx, cy = (x0 + x1) // 2, y_rod + 8 + (y_bot - y_rod - 8) // 2 - 3
        d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=C(M.GOLD['md']), outline=C(M.GOLD['dd']))
        d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=C(pal['dd']))
        px(d, cx - 3, cy - 3, M.GOLD['hi'])
        px(d, cx, cy, M.GOLD['lt'])
    M.mul_box(cv.im, (x1 + 1, y_rod + 3, x1 + 2, y_bot), (0.62, 0.62, 0.7))   # 旗在墙上的影子（右下）


def chest(cv, x0, yb, w=24, h=12, seed=0):
    """铁箍木箱（yb = 箱底一行，x0 = 左沿）：木板、两道竖铁箍 + 横带、圆弧箱盖（亮上沿）、铜锁牌、脚下接触影。"""
    d = cv.d
    WD = M.WOOD
    y0 = yb - h + 1
    rect(d, x0, y0 + 3, x0 + w - 1, yb, WD['md'], outline=INK)
    for yy in range(y0 + 4, yb):                                       # 木板：横缝
        if (yy - y0) % 4 == 0:
            hl(d, x0 + 1, x0 + w - 2, yy, WD['dk'])
    for k in range(w // 3):
        gx = x0 + 2 + int(hrange(0, w - 5, seed, k, 1))
        gy = y0 + 4 + int(hrange(0, h - 6, seed, k, 2))
        hl(d, gx, gx + 2, gy, WD['dd'])
    for r in range(3):                                                 # 圆弧盖
        hl(d, x0 + 1 + (2 - r) * 1, x0 + w - 2 - (2 - r) * 1, y0 + r, WD['hi'] if r == 0 else WD['lt'])
    hl(d, x0 + 1, x0 + w - 2, y0 + 3, WD['dd'])
    px(d, x0, y0 + 2, INK)
    px(d, x0 + w - 1, y0 + 2, INK)
    for bx in (x0 + 3, x0 + w - 5):                                    # 竖铁箍
        rect(d, bx, y0 + 1, bx + 1, yb, M.IRON['md'])
        vl(d, bx, y0 + 1, yb, M.IRON['hi'])
        px(d, bx, y0 + 4, M.IRON['hi'])
        px(d, bx + 1, yb - 2, M.IRON['hi'])
    rect(d, x0 + w // 2 - 2, y0 + 3, x0 + w // 2 + 2, y0 + 7, M.GOLD['md'], outline=M.GOLD['dd'])   # 锁牌
    px(d, x0 + w // 2 - 1, y0 + 4, M.GOLD['hi'])
    px(d, x0 + w // 2, y0 + 6, INK)
    M.mul_box(cv.im, (x0 - 1, yb + 1, x0 + w + 1, yb + 2), (0.55, 0.55, 0.66))


def skull(cv, cx, yb):
    """一颗头骨（宽 6、高 6，yb = 下颌最下面一行）：骨白（左亮右暗）、两个黑眼窝、鼻孔、一排牙；摆在箱子 / 台面上当小物件。"""
    d = cv.d
    BONE = ((236, 228, 204), (210, 200, 174), (150, 140, 124))
    rows = ('.xxxx.',
            'xxxxxx',
            'x.xx.x',
            'xxxxxx',
            '.xxxx.',
            '..x.x.')
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != 'x':
                continue
            col = BONE[0] if c < 2 else (BONE[1] if c < 4 else BONE[2])
            if r == 2 and c in (0, 5):
                col = BONE[2]
            px(d, cx - 3 + c, yb - 5 + r, col)
    for c in (1, 4):                                                   # 眼窝
        px(d, cx - 3 + c, yb - 3, (20, 14, 22))
    px(d, cx, yb - 3, (60, 52, 50))
    for (dx, dy) in ((-3, -5), (2, -5), (-3, 0), (2, 0)):              # 墨线只描外轮廓的四个角，保持 6 px 的小体量
        pass
    M.mul_box(cv.im, (cx - 3, yb + 1, cx + 3, yb + 1), (0.55, 0.55, 0.66))


def chandelier(cv, cx, y_top, y_ring, rx=19, ry=4, n=6, seed=0, pal=None):
    """吊灯（铜）：天花上的圆盘、一节节垂下来的链、一个压扁成椭圆的铜环（后半圈暗、前半圈亮）、四根从中心伸到环上的支臂、
    绕环均匀的 n 根蜡烛、环下面一串垂饰（小水晶 + 坠球）。返回 dict(flames=[(x, y)] 火苗底, crystals=[(x, y)] 水晶的位置)。"""
    pal = pal or M.GOLD
    d = cv.d
    # 天花上的圆盘 + 链
    hl(d, cx - 3, cx + 3, y_top, pal['md'])
    hl(d, cx - 2, cx + 2, y_top + 1, pal['dk'])
    hub_y = y_ring - 5
    for y in range(y_top + 2, hub_y):
        px(d, cx, y, pal['lt'] if (y - y_top) % 3 else pal['dd'])
        if (y - y_top) % 3 == 0:
            px(d, cx + 1, y, pal['dk'])
    # 环：椭圆，后半圈（上）先画
    pts_back, pts_front = [], []
    for k in range(0, 73):
        a = math.tau * k / 72.0
        x = cx + rx * math.cos(a)
        y = y_ring + ry * math.sin(a)
        (pts_front if math.sin(a) >= 0 else pts_back).append((int(round(x)), int(round(y))))
    for (x, y) in pts_back:
        px(d, x, y, pal['dk'])
    # 支臂：中心 → 环上左右两端（侧视几乎是水平的两条弧）+ 前后各一条
    for sgn in (-1, 1):
        for k in range(rx - 3):
            x = cx + sgn * (k + 2)
            y = hub_y + 1 + int(round((y_ring - hub_y - 1) * (k / float(rx - 3)) ** 1.5))
            px(d, x, y, pal['md'])
            px(d, x, y + 1, pal['dk'])
    rect(d, cx - 2, hub_y - 1, cx + 2, hub_y + 2, pal['lt'], outline=INK)       # 中心的圆球
    px(d, cx - 1, hub_y, pal['hi'])
    # 蜡烛：先画在环后半圈的，再画前半圈的（前面的盖住后面的）
    angs = [(math.tau * k / n + 0.4) for k in range(n)]
    flames = []
    order = sorted(range(n), key=lambda k: math.sin(angs[k]))
    for k in order:
        a = angs[k]
        x = int(round(cx + rx * math.cos(a)))
        y = int(round(y_ring + ry * math.sin(a)))
        hl(d, x - 2, x + 2, y, pal['lt'])                                         # 托盘
        hl(d, x - 1, x + 1, y + 1, pal['dk'])
        flames.append(M.candle(cv, x, y - 1, h=5, seed=seed * 5 + k))
        if math.sin(a) >= 0:
            pass
    for (x, y) in pts_front:
        px(d, x, y, pal['hi'] if x < cx else pal['lt'])
        px(d, x, y + 1, pal['md'] if x < cx else pal['dk'])
    # 垂饰：环前沿垂下几串小水晶，中间一个坠球
    crystals = []
    for dx in (-rx + 3, -rx // 2, rx // 2, rx - 3):
        x = cx + dx
        y0 = y_ring + 1 + int(round(ry * math.sqrt(max(0.0, 1 - (dx / float(rx)) ** 2))))
        vl(d, x, y0, y0 + 3, (150, 150, 176))
        px(d, x, y0 + 4, (236, 238, 255))
        crystals.append((x, y0 + 4))
    vl(d, cx, y_ring + 1, y_ring + 6, pal['md'])
    d.ellipse((cx - 2, y_ring + 6, cx + 2, y_ring + 10), fill=C(pal['md']), outline=C(INK))
    px(d, cx - 1, y_ring + 7, pal['hi'])
    px(d, cx + 1, y_ring + 9, pal['dd'])
    crystals.append((cx, y_ring + 11))
    px(d, cx, y_ring + 11, (236, 238, 255))
    return dict(flames=flames, crystals=crystals)


def books(cv, x, yb, seed=0):
    """地上叠着的三本旧书（x = 左沿，yb = 最下面一行）：一本比一本窄、书脊颜色各不相同、页边一道浅色、书脊上一道金线。"""
    d = cv.d
    cols = (((92, 36, 40), (150, 70, 66)), ((44, 60, 84), (86, 112, 150)), ((70, 56, 34), (128, 104, 64)))
    for k, (dark, light) in enumerate(cols):
        w = 12 - k * 2
        y1 = yb - k * 3
        ox = int(hrange(0, 2, seed, k, 1))
        rect(d, x + ox, y1 - 2, x + ox + w - 1, y1, dark, outline=INK)
        hl(d, x + ox + 1, x + ox + w - 2, y1 - 2, light)
        hl(d, x + ox + 1, x + ox + w - 2, y1, (214, 204, 176))                         # 页边
        px(d, x + ox + 2, y1 - 1, M.GOLD['md'])
    M.mul_box(cv.im, (x - 1, yb + 1, x + 13, yb + 2), (0.55, 0.55, 0.66))


def goblet(cv, x, yb):
    """倒在地上的高脚杯（铜）：杯身横着、杯脚朝右；地上一小滩暗红的酒。"""
    d = cv.d
    G = M.GOLD
    hl(d, x - 3, x + 1, yb - 2, G['lt'])
    hl(d, x - 3, x + 1, yb - 1, G['md'])
    hl(d, x - 2, x + 1, yb, G['dk'])
    px(d, x - 4, yb - 2, G['hi'])
    px(d, x + 2, yb - 1, G['md'])
    hl(d, x + 3, x + 4, yb - 1, G['dk'])
    px(d, x + 5, yb - 2, G['dk'])
    px(d, x + 5, yb, G['dk'])
    for k in range(5):                                                                 # 洒出来的酒
        px(d, x - 6 - k, yb, (70, 12, 24) if k % 2 == 0 else (92, 18, 32))
    M.mul_box(cv.im, (x - 4, yb + 1, x + 5, yb + 1), (0.55, 0.55, 0.66))


def bat_hanging(cv, x, y):
    """倒挂在梁下面睡觉的蝙蝠（宽 5、高 6，y = 爪子抓着的那一行）：翅膀收拢裹住身子，两只小耳朵朝下，一粒淡红的眼。"""
    d = cv.d
    c, c2 = (24, 16, 28), (44, 34, 52)
    px(d, x, y, (70, 60, 50))
    px(d, x + 1, y, (70, 60, 50))
    for k, (hw, yy) in enumerate(((2, y + 1), (2, y + 2), (2, y + 3), (1, y + 4))):
        hl(d, x + 1 - hw, x + hw, yy, c)
        px(d, x + 1 - hw, yy, c2)
    px(d, x, y + 5, c)
    px(d, x + 1, y + 5, c)
    px(d, x - 1, y + 6, c)
    px(d, x + 2, y + 6, c)
    px(d, x + 1, y + 5, (150, 50, 60))


# ============================================================ 通下去的拱门（旋转楼梯口）
def stair_arch(cv, x0, y0, w, h, glow=(255, 150, 70), seed=0, pal=STONE_B):
    """通向旋转楼梯的尖拱门洞（没有门板）：先画一圈比门套更宽的拱石（亮左暗右 + 拱石缝），再用 gothic_door 画石门套
    并把门板盖掉；门洞里是深黑的弧形内墙 + 一根立在中间的石柱（旋转楼梯的中柱）+ 绕着柱子一级级往上的踏板
    （左右交错伸到墙边，下沿被从下面透上来的光照亮）+ 门槛里面一小块平台。光（torch）是 emissive，strip 里让它一闪一闪。
    (x0, y0) = 门洞左上（拱顶那行），w × h = 门洞宽高。返回 dict(interior=bool mask, glow=[(x, y, u)], under=画完黑洞后的像素)。"""
    rise = w // 2 + 1
    y1 = y0 + h - 1
    d = cv.d
    ring = 4                                                           # 外圈拱石的厚度
    n_o = w + 2 * (3 + ring)
    top_o = M.arch_rows(n_o, rise + 3 + ring, pointed=True)
    for i in range(n_o):
        xx = x0 - 3 - ring + i
        yt = y0 + rise - int(round(top_o[i]))
        c = pal['lt'] if i < n_o // 2 else pal['md']
        if i < ring or i >= n_o - ring:
            c = pal['lt'] if i < ring else pal['dk']
        vl(d, xx, yt, y1 + 2, c)
        px(d, xx, yt, INK)
        px(d, xx, yt + 1, pal['hi'] if i < n_o // 2 else pal['lt'])
    for k in range(1, 9):                                              # 拱石缝：斜着一道道（上半圈）
        a_ = math.pi * k / 9.0
        r0, r1 = w / 2.0 + 3.5, w / 2.0 + 3.0 + ring + 0.5
        cx_ = x0 + (w - 1) / 2.0
        cy_ = y0 + rise
        d.line((cx_ - r0 * math.cos(a_), cy_ - r0 * math.sin(a_), cx_ - r1 * math.cos(a_), cy_ - r1 * math.sin(a_)),
               fill=C(pal['dd']))
    vl(d, x0 - 3 - ring, y0 + rise, y1 + 2, pal['hi'])
    vl(d, x0 + w + 2 + ring, y0 + rise, y1 + 2, pal['dd'])
    M.gothic_door(cv, x0, y0, w, h, pal=M.WOOD, frame=pal, kind='arch', seed=seed, keyhole=False)
    top = M.arch_rows(w, rise, pointed=True)
    inter = np.zeros((H, cv.w), bool)
    for i in range(w):
        yt = y0 + rise - int(round(top[i]))
        inter[yt:y1 + 1, x0 + i] = True
        for y in range(yt, y1 + 1):
            v = (y - yt) / max(1.0, (y1 - yt))
            c = mix((8, 6, 14), (22, 16, 24), v)
            if i < 3:
                c = dk(c, 0.7)                                         # 左边的侧壁更黑
            px(d, x0 + i, y, c)
    for i in range(int(w * 0.62), w):                                  # 右半边是弧形的内墙：一道道水平石缝
        for y in range(y0 + rise - 2, y1 - 6):
            if inter[y, x0 + i] and (y + seed) % 6 == 0:
                px(d, x0 + i, y, (34, 28, 44))
    # 中柱
    xn = x0 + int(w * 0.44)
    cy0, cy1 = y0 + rise + 2, y1 - 7
    for k in range(6):
        c = (28, 24, 38) if k in (0, 5) else ((60, 54, 76) if k in (1, 2) else (44, 40, 58))
        vl(d, xn + k, cy0, cy1, c)
    hl(d, xn - 1, xn + 6, cy0, (84, 78, 100))
    hl(d, xn - 1, xn + 6, cy0 + 1, (36, 32, 48))
    # 绕柱的踏板：从门槛往上，每 6 px 一级，左右交错（伸到墙边 / 伸到另一边），3 px 厚，下沿 1 px 亮（被下面的光照着）
    k = 0
    for yy in range(y1 - 8 - 6, cy0 + 4, -6):
        left = (k % 2 == 0)
        xa, xb = (x0 + 3, xn - 1) if left else (xn + 6, x0 + w - 3)
        hl(d, xa, xb, yy, (66, 60, 84))                                # 踏板上面
        hl(d, xa, xb, yy + 1, (44, 40, 58))
        hl(d, xa, xb, yy + 2, (92, 84, 108))                           # 下沿亮边
        k += 1
    # 门槛里面一小块平台
    for y in range(y1 - 6, y1 + 1):
        for i in range(2, w - 2):
            px(d, x0 + i, y, mix((54, 48, 66), (30, 26, 40), (y - (y1 - 6)) / 6.0))
    hl(d, x0 + 2, x0 + w - 3, y1 - 6, (86, 80, 100))
    under = np.array(cv.im).copy()
    gl = []
    gh_ = 30
    for i in range(w):
        for y in range(y1 - gh_, y1 - 5):
            if inter[y, x0 + i]:
                u = (y - (y1 - gh_)) / float(gh_ - 5)
                gl.append((x0 + i, y, u))
    return dict(interior=inter, glow=gl, under=under, glow_col=glow, box=(x0, y0, x0 + w - 1, y1))


def glow_pixels(info, s=1.0):
    """stair_arch 的暖光：返回 [(x, y, 颜色)]，s = 强度（1.0 = 静态底图用的，strip 的每帧给不同的 s 就一闪一闪）。
    强度随高度平方上升，再按 Bayer 抖动成“一圈圈”的硬边；中柱（亮一点的石头）上的光更实。"""
    out = []
    under = info['under']
    gc = np.array(info['glow_col'], np.float32)
    bay = A._bayer(under.shape[1], under.shape[0])
    for (x, y, u) in info['glow']:
        k = min(1.0, (u ** 1.8) * 0.85 * s)
        base = under[y, x, :3].astype(np.float32)
        q = math.floor(k * 5 + bay[y, x] * 0.9) / 5.0
        out.append((x, y, tuple(int(v) for v in np.clip(base * (1 - 0.35 * q) + gc * q * 0.62, 0, 255))))
    return out
