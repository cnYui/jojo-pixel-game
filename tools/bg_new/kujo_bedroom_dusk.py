"""预览：python -B tools\\bg_new\\bgpro_preview.py kujo_bedroom_dusk

荷莉的卧室·黄昏（游戏层加细节，2026-10-10 bg-pro）：布局、锚点、行灯闪烁 strip 和原导出
bg_jojo.exp_kujo_bedroom_dusk 一样（被褥位置 (150,166) 周围的榻榻米保持干净），只把底图画细：

  天花板木纹；栏间换成竖格子；墙：土墙砂粒 + 墙角阴影，左上挂一个小相框（荷莉和小时候的承太郎）
  障子窗：木窗框 + 窗台，纸面右上被夕阳照得更亮、格子投影，松枝影子加松针
  金屏风：金箔方格、黑漆边框和铰链、梅枝两枝 + 花苞
  架子：花瓶、小相框、首饰盒；行灯：木框腿和提手（灯纸和光晕仍是 strip）
  托盘：水盆、毛巾外加一个水杯；榻榻米织纹；门口一双拖鞋
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
from PIL import ImageDraw
from engine import bg_asia as A
from engine.core import hrange, hash01, mix

W, H = 320, 180
C = A._c4
ANDON_BOX = (265, 116, 320, 173)


def R(d, box, col, outline=None):
    d.rectangle(box, fill=C(col), outline=C(outline) if outline else None)


def L(d, pts, col, width=1):
    d.line(pts, fill=C(col), width=width)


def P(d, x, y, col):
    d.point((round(x), round(y)), fill=C(col))


@lru_cache(maxsize=1)
def static():
    Pv = A._KJ['dusk']
    img = A._new(col=(120, 90, 60))
    d = ImageDraw.Draw(img)
    # 天花板 + 栏间（竖格子）+ 长押
    R(d, (0, 0, W, 10), (110, 76, 48))
    for x in range(0, W, 12):
        L(d, (x, 0, x, 10), (90, 60, 38))
        L(d, (x + 1, 0, x + 1, 10), (124, 88, 58))
    for i in range(24):
        y = int(hrange(2, 9, i, 3))
        xa = int(hrange(0, W, i, 4))
        L(d, (xa, y, xa + int(hrange(6, 20, i, 5)), y), (98, 66, 42))
    R(d, (0, 10, W, 26), (176, 156, 120))
    for x in range(2, W, 5):
        L(d, (x, 12, x, 25), (204, 184, 146))
        L(d, (x + 1, 12, x + 1, 25), (150, 120, 84))
    L(d, (0, 12, W, 12), (150, 112, 70))
    L(d, (0, 18, W, 18), (150, 112, 70))
    R(d, (0, 10, W, 11), (120, 86, 52))
    R(d, (0, 26, W, 30), (150, 108, 66))
    L(d, (0, 26, W, 26), (190, 150, 104))
    L(d, (0, 30, W, 30), (90, 62, 38))
    # 土墙
    R(d, (0, 31, W, 140), (206, 186, 150))
    A._tex_noise(img, (0, 30, W, 140), 0.07, 21)
    d = ImageDraw.Draw(img)
    for i in range(260):
        P(d, hrange(0, W, i, 41), hrange(32, 136, i, 42), (190, 168, 132) if i % 2 else (220, 202, 168))
    A._blend_rect(img, (0, 31, W, 34), (80, 50, 30), 40)
    d = ImageDraw.Draw(img)
    # 小相框（荷莉和小时候的承太郎）
    R(d, (48, 38, 64, 52), (110, 76, 46))
    R(d, (50, 40, 62, 50), (226, 214, 190))
    R(d, (51, 41, 61, 45), (176, 200, 220))
    d.ellipse((52, 43, 55, 46), fill=C((240, 210, 120)))
    R(d, (52, 46, 55, 49), (230, 120, 140))
    d.ellipse((57, 45, 59, 47), fill=C((40, 36, 40)))
    R(d, (57, 47, 59, 49), (40, 50, 80))
    L(d, (56, 36, 52, 38), (90, 70, 50))
    L(d, (56, 36, 60, 38), (90, 70, 50))
    # 障子窗：外框、窗台、纸面亮暗、格子投影、松枝影子
    wx0, wy0, wx1, wy1 = 118, 38, 300, 112
    paper = (250, 180, 120)
    R(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), (120, 84, 50))
    L(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy0 - 3), (160, 118, 76))
    A._shoji(d, wx0, wy0, wx1, wy1, paper=paper, wood=(130, 92, 56), cell=(13, 12))
    for cx in range(wx0, wx1 - 12, 13):                                        # 越往右上越亮
        for cy in range(wy0, wy1 - 18, 12):                                    # 最下面一排是腰板，不动
            u = (cx - wx0) / (wx1 - wx0) * 0.7 + (1 - (cy - wy0) / (wy1 - wy0)) * 0.3
            if u > 0.55:
                R(d, (cx + 1, cy + 1, cx + 12, cy + 11), mix(paper, (255, 214, 156), (u - 0.55) * 1.6))
            L(d, (cx + 1, cy + 11, cx + 12, cy + 11), mix(paper, (130, 92, 56), 0.25))
    sh = mix(paper, (60, 60, 80), 0.28)
    L(d, (wx1 - 6, wy0 + 10, wx0 + 90, wy0 + 26), sh, 2)
    L(d, (wx0 + 120, wy0 + 20, wx0 + 110, wy0 + 44), sh)
    L(d, (wx0 + 150, wy0 + 18, wx0 + 160, wy0 + 6), sh)
    for (px_, py_, r) in ((wx0 + 86, wy0 + 24, 12), (wx0 + 110, wy0 + 46, 9), (wx0 + 150, wy0 + 16, 10),
                          (wx1 - 14, wy0 + 12, 8), (wx0 + 162, wy0 + 6, 6)):
        d.ellipse((px_ - r, py_ - r * 0.5, px_ + r, py_ + r * 0.5), fill=C(sh))
        for k in range(-r + 1, r, 2):                                            # 松针
            L(d, (px_ + k, py_ - r * 0.5 - 1, px_ + k + 1, py_ - r * 0.5 - 2), sh)
    for x in range(wx0, wx1 + 1, 13):
        L(d, (x, wy0, x, wy1), (130, 92, 56))
    for y in range(wy0, wy1 + 1, 12):
        L(d, (wx0, y, wx1, y), (130, 92, 56))
    R(d, (wx0 - 5, wy1 + 3, wx1 + 5, wy1 + 6), (140, 98, 60))                   # 窗台
    L(d, (wx0 - 5, wy1 + 3, wx1 + 5, wy1 + 3), (196, 150, 100))
    A._blend_rect(img, (wx0 - 3, wy1 + 7, wx1 + 3, wy1 + 9), (80, 50, 30), 50)
    d = ImageDraw.Draw(img)
    # 柱子（木纹）
    for x in (6, 110, 306):
        A._post(d, x, 26, 142)
        for i in range(4):
            xx = x + 1 + int(hrange(0, 4, x, i))
            ya = int(hrange(30, 100, x, i, 1))
            L(d, (xx, ya, xx, ya + int(hrange(10, 36, x, i, 2))), (126, 88, 52))
    # 金屏风：金箔方格、黑漆框、铰链、梅枝
    pw = 20
    for i in range(4):
        x0 = 14 + i * pw
        top = 62 if i % 2 == 0 else 60
        col = (206, 170, 90) if i % 2 == 0 else (186, 150, 76)
        R(d, (x0, top, x0 + pw, 146), col)
        for gy in range(top + 2, 144, 6):
            for gx in range(x0 + 2, x0 + pw - 1, 6):
                if hash01(gx, gy, 7) < 0.45:
                    R(d, (gx, gy, gx + 5, gy + 5), mix(col, (255, 226, 140), 0.18))
                L(d, (gx, gy, gx + 5, gy), mix(col, (120, 90, 40), 0.18))
        d.rectangle((x0, top, x0 + pw, 146), outline=C((40, 24, 18)))
        L(d, (x0 + 1, top + 1, x0 + pw - 1, top + 1), (90, 60, 30))
        if i:
            for hy in (top + 14, 128):
                R(d, (x0 - 1, hy, x0 + 1, hy + 2), (200, 170, 100))
    L(d, (14, 146, 94, 146), (60, 36, 24))
    L(d, (20, 120, 40, 98, 66, 90, 88, 76), (70, 50, 36), 2)
    L(d, (40, 98, 36, 86), (70, 50, 36))
    L(d, (66, 90, 70, 104, 80, 110), (70, 50, 36))
    L(d, (22, 140, 30, 128, 44, 124), (80, 58, 40))
    for (px_, py_) in ((40, 98), (52, 94), (66, 90), (76, 84), (88, 76), (30, 110), (58, 86), (36, 86), (72, 104),
                       (80, 110), (30, 128), (44, 124)):
        d.ellipse((px_ - 2, py_ - 2, px_ + 2, py_ + 2), fill=C((236, 120, 150)))
        P(d, px_, py_, (255, 220, 230))
        P(d, px_ - 1, py_ + 1, (200, 80, 110))
    for (px_, py_) in ((46, 96), (62, 88), (84, 79), (26, 134)):
        P(d, px_, py_, (220, 70, 100))
    # 架子：花瓶、小相框、首饰盒
    R(d, (256, 124, 296, 130), (110, 70, 40))
    L(d, (256, 124, 296, 124), (150, 104, 66))
    R(d, (258, 130, 262, 142), (90, 56, 32))
    R(d, (290, 130, 294, 142), (90, 56, 32))
    R(d, (262, 136, 290, 137), (90, 56, 32))
    d.ellipse((270, 110, 280, 124), fill=C((200, 80, 70)), outline=C((100, 40, 36)))
    L(d, (272, 113, 272, 118), (236, 140, 120))
    L(d, (275, 110, 272, 100), (60, 110, 60))
    L(d, (274, 106, 278, 104), (60, 110, 60))
    d.ellipse((268, 96, 276, 102), fill=C((250, 240, 240)))
    P(d, 272, 99, (240, 200, 90))
    R(d, (259, 116, 266, 124), (70, 50, 36))
    R(d, (260, 117, 265, 122), (190, 200, 214))
    R(d, (283, 119, 293, 124), (140, 40, 50))
    L(d, (283, 119, 293, 119), (200, 90, 90))
    P(d, 288, 121, (240, 200, 100))
    # 门槛 + 榻榻米（织纹）
    R(d, (0, 136, W, 142), (150, 108, 66))
    L(d, (0, 136, W, 136), (196, 150, 100))
    L(d, (0, 139, W, 139), (126, 88, 52))
    A._tatami(d, img, 142, H, [[60, 150, 240], [20, 110, 200, 290]], seed=2)
    d = ImageDraw.Draw(img)
    for y in range(144, H, 2):
        for x in range((y // 2) % 3, W, 3):
            if hash01(x, y, 98) < 0.35:
                P(d, x, y, (196, 188, 120) if (x + y) % 2 else (170, 162, 98))
    for y in (142, 156):
        for x in range(1, W, 4):
            P(d, x, y + 1, (96, 112, 84))
    A._blend_rect(img, (0, 143, W, 145), (60, 40, 20), 50)
    d = ImageDraw.Draw(img)
    # 托盘：水盆、毛巾、水杯
    A._blend_rect(img, (221, 164, 254, 166), (60, 40, 20), 60)
    d = ImageDraw.Draw(img)
    R(d, (222, 158, 252, 164), (120, 60, 40), (70, 34, 24))
    L(d, (223, 159, 251, 159), (150, 84, 56))
    d.ellipse((226, 152, 240, 160), fill=C((190, 196, 206)), outline=C((100, 106, 120)))
    d.ellipse((228, 153, 238, 157), fill=C((150, 200, 230)))
    L(d, (230, 154, 233, 154), (210, 236, 250))
    R(d, (242, 154, 250, 158), (250, 250, 250), (180, 180, 190))
    L(d, (243, 156, 249, 156), (210, 214, 226))
    R(d, (244, 150, 247, 154), (200, 220, 236), (140, 150, 170))
    # 门口一双拖鞋
    for sx in (20, 28):
        d.rounded_rectangle((sx, 168, sx + 6, 171), radius=1, fill=C((150, 110, 160)), outline=C((90, 60, 100)))
        L(d, (sx + 1, 168, sx + 4, 168), (200, 170, 210))
    # 行灯：木框腿 + 提手（灯纸 / 光晕在 strip）
    R(d, (296, 132, 314, 158), (90, 56, 32))
    R(d, (298, 134, 312, 154), (240, 220, 170))
    L(d, (305, 134, 305, 154), (90, 56, 32))
    L(d, (298, 144, 312, 144), (90, 56, 32))
    R(d, (296, 158, 298, 161), (70, 42, 24))
    R(d, (312, 158, 314, 161), (70, 42, 24))
    L(d, (300, 129, 310, 129), (70, 42, 24))
    L(d, (300, 129, 300, 132), (70, 42, 24))
    L(d, (310, 129, 310, 132), (70, 42, 24))
    img = A._grade(img, sat=0.95, val=Pv['val'], tint=Pv['tint'], tint_amt=Pv['ta'])
    return img


def export(ex, BJ):
    base = static()

    def andon(t):
        img = BJ.blank()
        fl = 0.85 + 0.15 * BJ._noise_loop(t * 3, 5, BJ.ANDON_K)
        A._glow(img, 305, 144, 40, 28, (255, 190, 100), int(70 * fl), rings=4)
        d = ImageDraw.Draw(img)
        d.rectangle((298, 134, 312, 154), fill=A._c4(mix((240, 200, 130), (255, 236, 170), fl)))
        d.line((305, 134, 305, 154), fill=A._c4((90, 56, 32)))
        d.line((298, 144, 312, 144), fill=A._c4((90, 56, 32)))
        return img
    strip = ex.bake('andon', ANDON_BOX, int(BJ.ANDON_K / 3 * BJ.ANDON_FPS), BJ.ANDON_FPS, andon)
    layers = [dict(type='static', image=ex.img('static', base)), strip]
    anchors = dict(futon=[150, 166], window=[118, 38, 300, 112], andon=[305, 144], walk_x=[40, 290],
                   shelf=[256, 124, 296, 142], tray=[222, 152, 252, 164])
    st = ex.stage(320, 158, (150, 176), layers, anchors=anchors)
    if ex.check_on:
        def direct(t):
            img = base.copy()
            f = int(math.floor(t * strip['fps'])) % strip['n']
            img.alpha_composite(andon(f / strip['fps']).crop(ANDON_BOX), ANDON_BOX[:2])
            return img
        for t in (0.0, 1.7, 3.3):
            ex.checked('卧室 t=%.1f 导出 vs 直接绘制' % t, BJ.ndiff_rgba(BJ.ref_render(st, ex.images, 0, t), direct(t)))
        ex.checked('卧室底图不透明', int((np.array(base)[:, :, 3] != 255).sum()))
    return st
