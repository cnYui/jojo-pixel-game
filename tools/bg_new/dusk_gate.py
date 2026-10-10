"""预览：python -B tools\\bg_new\\bgpro_preview.py dusk_gate

空条家门口的黄昏（序-18 出发过场；游戏层加细节，2026-10-10 bg-pro）：图层结构、视差、乌鸦 clouds、
路面反光 strip、锚点都和原导出 bg_jojo.exp_dusk_gate 一样（剧情 gate_pro 只演过场：四人剪影从 x 120 走到 330），
只把每层的图画细：

  天空：顶上几颗刚亮的星
  远处东京：楼里零星亮灯、几栋楼顶的航空灯、塔身的横档和顶上红灯
  中景屋顶：电视天线、烟囱、更多亮着的窗
  电线杆：第一根杆上挂一盏路灯（暖色光晕）、第二根杆上的变压器
  近景：院墙的灰泥纹理和瓦檐一排瓦当、门柱上「空条」门牌和信箱、门楣下一盏门灯；门里的踏脚石；
        墙根的排水沟盖板、路边白线、井盖、松树更多的轮廓光
  主角们走的那一段（x 120–330，y 146–160）路面只加很淡的东西，剪影照样清楚
"""
import sys
sys.dont_write_bytecode = True

import math
import os
from functools import lru_cache

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np
from PIL import Image, ImageDraw
from engine import bg_asia as A
from engine.core import hrange, hash01, paste, mix

W, H = 320, 180


def C(c, a=255):
    return tuple(int(v) for v in c[:3]) + (a,)


def P(d, x, y, col, a=255):
    d.point((round(x), round(y)), fill=C(col, a))


@lru_cache(maxsize=1)
def images(s05_id):
    import importlib
    s05 = importlib.import_module('scenes.s05_holly')
    # 天空 + 星
    sky = s05._dusk_sky().copy()
    d = ImageDraw.Draw(sky)
    for i in range(10):
        x, y = hrange(4, 316, i, 201), hrange(3, 26, i, 202)
        P(d, x, y, (255, 236, 220) if i % 3 else (220, 210, 255))
    # 远处东京：亮灯 + 航空灯
    far = s05._dusk_far().copy()
    a = np.array(far)
    ys, xs = np.nonzero(a[:, :, 3] > 0)
    for k, (y, x) in enumerate(zip(ys, xs)):
        if 116 <= y <= 146 and hash01(int(x), int(y), 203) < 0.035 and y % 2 == 0:
            a[y, x, :3] = (255, 196, 120) if hash01(int(x), int(y), 204) < 0.6 else (210, 120, 100)
    far = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(far)
    tx0 = 306
    for yv in (84, 112, 136):                                                  # 塔身横档
        u = (yv - 70) / 80
        half = 1 + int(u * u * 14)
        d.line((tx0 - half - 1, yv, tx0 + half + 1, yv), fill=(130, 50, 96, 255))
    P(d, tx0, 61, (255, 70, 60))
    P(d, tx0, 99, (255, 120, 80))
    a = np.array(far)
    for x in range(0, far.width - 4, 1):                                       # 高楼顶上的航空灯
        col = a[:, x, 3]
        nz = np.nonzero(col)[0]
        if len(nz) and nz[0] < 124 and hash01(x, 205) < 0.12 and abs(x - tx0) > 16:
            a[nz[0] - 1, x] = (255, 80, 70, 255)
    far = Image.fromarray(a, 'RGBA')
    # 中景屋顶：天线、烟囱、亮窗
    mid = s05._dusk_mid().copy()
    d = ImageDraw.Draw(mid)
    col = (58, 22, 62, 255)
    x, i = 118, 0
    while x < mid.width:
        bw = int(hrange(22, 40, i, 11))
        top = int(hrange(132, 140, i, 12))
        if hash01(i, 206) > 0.5:                                               # 电视天线
            ax = x + int(hrange(6, bw - 6, i, 207))
            d.line((ax, top - 9, ax, top), fill=col)
            d.line((ax - 3, top - 7, ax + 3, top - 7), fill=col)
            d.line((ax - 2, top - 5, ax + 2, top - 5), fill=col)
        elif hash01(i, 208) > 0.5:                                             # 烟囱
            cx = x + int(hrange(4, bw - 8, i, 209))
            d.rectangle((cx, top - 4, cx + 2, top), fill=col)
        if hash01(i, 210) > 0.45:
            wx = x + int(hrange(4, bw - 6, i, 211))
            d.rectangle((wx, top + 10, wx + 1, top + 11), fill=(255, 176, 100, 255))
        x += bw + int(hrange(2, 8, i, 15))
        i += 1
    # 近景
    near = s05._dusk_near().copy()
    d = ImageDraw.Draw(near)
    ox = s05.NEAR_OX
    wall, dark, rim = (46, 22, 52), (26, 12, 32), (255, 150, 96)
    for k in range(160):                                                       # 院墙灰泥
        x_, y_ = hrange(0, 128 + ox, k, 212), hrange(129, 140, k, 213)
        if near.getpixel((int(x_), int(y_)))[:3] == wall:
            P(d, x_, y_, (56, 28, 62))
    for x_ in range(1, 132 + ox, 4):                                           # 瓦当
        if near.getpixel((x_, 127))[:3] == dark:
            P(d, x_, 127, (70, 36, 70))
            P(d, x_ + 1, 127, (36, 16, 40))
    for x_ in range(0, 132 + ox, 2):
        if near.getpixel((x_, 121))[:3] == rim and hash01(x_, 214) < 0.25:
            P(d, x_, 120, (255, 190, 130))
    gx = ox                                                                    # 近景图的 x = 世界 x + 40
    d.rectangle((gx + 87, 104, gx + 93, 116), fill=C((140, 92, 80)))           # 门牌「空条」（逆光，压暗）
    d.rectangle((gx + 87, 104, gx + 93, 116), outline=C((90, 50, 50)))
    for k, y_ in enumerate((106, 111)):
        d.line((gx + 89, y_, gx + 91, y_), fill=C((50, 26, 30)))
        d.line((gx + 90, y_, gx + 90, y_ + 3), fill=C((50, 26, 30)))
    d.rectangle((gx + 30, 112, gx + 37, 120), fill=C((70, 34, 48)))           # 信箱
    d.line((gx + 31, 114, gx + 36, 114), fill=C((20, 8, 24)))
    d.line((gx + 30, 112, gx + 37, 112), fill=C((130, 70, 70)))
    lamp = Image.new('RGBA', near.size, (0, 0, 0, 0))                          # 门灯（门楣下）
    A._glow(lamp, gx + 62, 104, 14, 10, (255, 196, 120), 70, rings=3)
    near.alpha_composite(lamp)
    d = ImageDraw.Draw(near)
    d.rectangle((gx + 60, 101, gx + 64, 105), fill=C((255, 226, 160)))
    d.line((gx + 60, 101, gx + 64, 101), fill=C(dark))
    for (sx, sy, rw) in ((62, 140, 6), (56, 136, 4), (66, 133, 3)):           # 门里的踏脚石
        d.ellipse((gx + sx - rw, sy - 1, gx + sx + rw, sy + 1), fill=C((140, 70, 64)))
    for x_ in range(0, 128 + ox, 6):                                           # 墙根排水沟盖板
        d.line((x_, 148, x_ + 4, 148), fill=C((64, 30, 56)))
    d.line((0, 150, near.width, 150), fill=C((60, 26, 52)))
    for x_ in range(0, near.width, 2):                                         # 路边白线（被夕阳染色）
        d.point((x_, 151), fill=C((120, 56, 66)))
    d.ellipse((ox + 300, 166, ox + 316, 170), fill=C((52, 22, 50)), outline=C((80, 36, 62)))   # 井盖
    for (cx, cy, rx) in ((112, 66, 12), (98, 76, 11), (130, 80, 12), (104, 92, 10), (138, 94, 9), (122, 72, 8)):
        d.line((gx + cx - rx + 2, cy - 3, gx + cx - rx + 5, cy - 3), fill=C((200, 96, 86)))   # 松叶轮廓光
        P(d, gx + cx + rx - 2, cy + 1, (110, 44, 64))
    return sky, far, mid, near


def poles_img(BJ):
    POX = 48
    poles = BJ.blank(W + 200 + POX, H)
    pf = BJ.FakeFr(0, poles)
    BJ._poles_world(pf, POX)
    d = ImageDraw.Draw(poles)
    col = (30, 12, 34, 255)
    p1 = 150 + POX                                                             # 第一根杆：路灯
    d.line((p1 + 2, 84, p1 + 9, 82), fill=col)
    d.rectangle((p1 + 8, 82, p1 + 12, 84), fill=col)
    glow = Image.new('RGBA', poles.size, (0, 0, 0, 0))
    A._glow(glow, p1 + 10, 86, 9, 7, (255, 200, 130), 70, rings=3)
    poles.alpha_composite(glow)
    d = ImageDraw.Draw(poles)
    d.line((p1 + 9, 85, p1 + 11, 85), fill=(255, 230, 170, 255))
    p2 = 300 + POX                                                             # 第二根杆：变压器
    d.rectangle((p2 + 3, 72, p2 + 7, 80), fill=col)
    d.line((p2 + 3, 72, p2 + 7, 72), fill=(120, 50, 70, 255))
    pb = poles.getbbox()
    return poles.crop((pb[0], 0, pb[2], H)), -POX + pb[0]


def export(ex, BJ):
    s05 = BJ.scene('s05_holly')
    T_F = s05.T_F
    sky, far, mid, near = images(id(s05))
    clouds = BJ.roll_x(s05._dusk_clouds(), 40)
    cim, cy = BJ.crop_rows(clouds)
    layers = [dict(type='static', image=ex.img('sky', sky)),
              dict(type='wrap', image=ex.img('streaks', cim), period=640, k=0.0, y=cy, vx=3.0)]
    layers.append(dict(type='pano', image=ex.img('far', far), k=0.25, x=0, y=0))
    crows = []
    bird = BJ.blank(7, 3)
    ImageDraw.Draw(bird).line((0, 0, 3, 2, 6, 0), fill=(30, 12, 34, 255))
    kbird = ex.img('crow', bird)
    for i in range(3):
        u0 = ((0 - T_F) * 0.09 + i * 0.13) % 1.0
        bx0 = 330 - u0 * 360 + i * 7
        by = 64 + i * 7
        crows.append(dict(image=kbird, x0=round(bx0 - 3 + 100, 3), y=by - 2, vx=-0.09 * 360, k=0))
    layers.append(dict(type='clouds', span=430, clouds=crows))
    layers.append(dict(type='pano', image=ex.img('mid', mid), k=0.6, x=0, y=0))
    pim, px0 = poles_img(BJ)
    layers.append(dict(type='pano', image=ex.img('poles', pim), k=0.8, x=px0, y=0))
    layers.append(dict(type='pano', image=ex.img('near', near), k=1.0, x=-s05.NEAR_OX, y=0))

    def glitter(t):
        f = BJ.FakeFr(t)
        for i in range(10):
            x = 212 + hrange(-40, 40, i, 41) + math.sin(t * BJ.DG_GLINT_W + i) * 2
            y = 152 + i * 2
            if BJ.blink(t + hash01(i, 42), 0.5, 0.6):
                f.d.line((round(x), y, round(x) + int(hrange(2, 7, i, 43)), y), fill=(200, 96, 80, 255))
        return f.img
    layers.append(ex.bake('glitter', (168, 152, 262, 171), int(BJ.DG_GLINT_L * BJ.DG_GLINT_FPS), BJ.DG_GLINT_FPS, glitter))
    anchors = dict(gate=[39, 101, 85, 147], gate_posts=[[30, 38], [86, 94]], door_x=62, sun=[212, 120],
                   cam=[-40, 100], wall_end=128, walk_x=[0, 420])
    st = ex.stage(420, 152, (148, 172), layers, anchors=anchors)
    if ex.check_on:
        for camX in (-40, 0, 40, 100):
            want = Image.new('RGBA', (W, H), (0, 0, 0, 255))
            paste(want, sky, 0, 0)
            BJ.ref_layer(want, layers[1], ex.images, camX, 0, {})
            paste(want, far, -math.floor(camX * 0.25), 0)
            paste(want, mid, -math.floor(camX * 0.6), 0)
            paste(want, pim, px0 - math.floor(camX * 0.8), 0)
            paste(want, near, -s05.NEAR_OX - math.floor(camX), 0)
            got = BJ.ref_render(st, ex.images, camX, 0, only={'static', 'wrap', 'pano'})
            ex.checked('黄昏门口 camX=%d 天空/云/远/中/杆/近 vs 直接贴图' % camX, BJ.ndiff_rgba(got, want))
        ex.checked('黄昏门口 天空不透明', int((np.array(sky)[:, :, 3] != 255).sum()))
    return st
