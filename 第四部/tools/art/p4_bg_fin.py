# 第四部终章（杜王町 / 钻石是不会碎的）的背景：3 张新图 + 5 张别章背景的变体，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_fin.json（build_p4.py 会把 _meta/bg_*.json 并进 bg.json）。
#   用法：python3 第四部/tools/art/p4_bg_fin.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   图层 pack 一律 'final'（打包成 data/img_bg_final.js，进终章时才加载）。
#   变体（雨天街口、幽灵小路冷 / 暖、港口夏末）从别章已经画好的图层调色生成，存成本章 pack 里的新 key；
#   别章的图还没进仓库时跳过并打印提示，等那几章的背景合进来以后再跑一遍本脚本即可。
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import OUT, preview, save_layers, sky_far, liv_floor  # noqa: E402

PACK = 'final'
W_ROOM_G = 134          # 室内：墙脚线（地板从这里往下画），和序章客厅一样


def poly(d, pts, col):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=C(col))


def kanji(im, x, y, text, col, size=12):
    """文泉驿点阵正黑 12 px 点阵字（招牌、车身字用），返回 (宽, 高)"""
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    im.paste(C(col), (int(x), int(y)), m)
    return m.width, m.height


def bayer(h, w):
    return np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]


def field_paint(img, f, cols, box=None):
    """强度场 f（0..1）按 cols 分档上色，档与档之间 4×4 Bayer 抖动；f < 0 的地方不动"""
    a = np.array(img)
    h, w = f.shape
    n = len(cols) - 1
    t = np.clip(f, 0, 1) * n
    k = np.clip(np.floor(t + bayer(h, w) - .5).astype(int), 0, n)
    pal = np.array([c3(c) for c in cols], np.uint8)
    x0, y0 = (box[0], box[1]) if box else (0, 0)
    sub = a[y0:y0 + h, x0:x0 + w]
    m = f >= 0
    sub[..., :3][m] = pal[k][m]
    sub[..., 3][m] = 255
    return Image.fromarray(a, 'RGBA')


def strip_frames(n, w, h):
    return Image.new('RGBA', (w * n, h), (0, 0, 0, 0))


# ============================================================ 空房子 empty_house（480 宽，雨停后的阴天，室内）
#   住宅区里一间没人住的房子（段 B、段 C）。左起：通玄关的门洞、砖砌壁炉（炉膛里一堆烟灰）、大窗（窗外是湿漉漉的住宅区，
#   吉良在外面）、窗下盖着白布的沙发、小圆桌上的花瓶、纸箱、电话台、上二楼的楼梯。
#   可切换：ash（0 满 → 3 撒光）、vase（0 好的 / 1 碎了）、glass（1 = 窗玻璃破洞）、ring（1 = 电话在响）。
def eh_room():
    W, G = 480, W_ROOM_G
    im = new(W, 180, '#d4cdbd')
    d = ImageDraw.Draw(im)
    # ---- 墙纸：褪色的竖条纹 + 小花点
    for x in range(0, W, 10):
        line(d, (x, 12, x, G - 26), '#cac2b0')
        for y in range(18 + (x // 10) % 2 * 7, G - 28, 14):
            px(d, x + 5, y, '#bdb5a2')
    im = grad(im, (0, 0, W, 16), ('#57524a', '#7e786c', '#a8a090', '#c4bcaa'))
    d = ImageDraw.Draw(im)
    rect(d, (0, 14, W, 15), '#e2dccd')                               # 顶角线
    line(d, (0, 16, W, 16), '#a49c8a')
    # 天花板渗水的黄渍（两块）
    for cx, cy, rx, ry in ((152, 22, 26, 8), (396, 20, 18, 6)):
        yy, xx = np.mgrid[0:24, 0:2 * rx + 4]
        f = 1 - np.sqrt(((xx - rx - 2) / rx) ** 2 + ((yy - 4) / ry) ** 2)
        f = np.where(f > 0, f, -1)
        im = field_paint(im, f, ('#c4bcaa', '#bdb096', '#b0a280'), box=(cx - rx - 2, 16))
    d = ImageDraw.Draw(im)
    # ---- 护墙板
    rect(d, (0, G - 26, W, G), '#86705a')
    line(d, (0, G - 26, W, G - 26), '#a48c70')
    line(d, (0, G - 25, W, G - 25), '#6a5644')
    for x in range(4, W, 40):
        rect(d, (x, G - 21, x + 33, G - 5), '#7a6550')
        line(d, (x, G - 21, x + 33, G - 21), '#64503e')
        line(d, (x, G - 5, x + 33, G - 5), '#96806a')
    # 墙上摘掉画框留下的浅色印子（钉子还在）
    for x0, y0, x1, y1 in ((86, 34, 122, 60), (362, 44, 386, 74), (330, 38, 350, 52)):
        rect(d, (x0, y0, x1, y1), '#ddd7c8')
        line(d, (x0, y1 + 1, x1, y1 + 1), '#c2baa8')
        px(d, (x0 + x1) // 2, y0 - 4, '#5a5048')
        line(d, ((x0 + x1) // 2, y0 - 4, x0 + 3, y0), '#b4ac98')
        line(d, ((x0 + x1) // 2, y0 - 4, x1 - 3, y0), '#b4ac98')
    # ---- 地板（序章客厅同款木地板，后面整体调灰）
    im = liv_floor(im, 0, W, G)
    d = ImageDraw.Draw(im)
    # ---- 门洞（通玄关）
    rect(d, (6, 44, 46, G), '#6e5844')
    rect(d, (10, 48, 42, G), '#2c2824')
    im = grad(im, (10, 48, 42, G), ('#24201c', '#34302a', '#3e3830'))
    d = ImageDraw.Draw(im)
    rect(d, (10, G - 12, 42, G), '#4a4036')                          # 玄关地面（低一级）
    line(d, (10, G - 12, 42, G - 12), '#5e5244')
    rect(d, (14, G - 46, 22, G - 40), '#565048')                     # 玄关鞋柜上方的挂钩
    line(d, (6, 44, 46, 44), '#8a7258')
    line(d, (46, 44, 46, G), '#4e3e30')
    # ---- 壁炉（砖砌，木头壁炉架）
    fx0, fx1, ftop = 58, 148, G - 66
    rect(d, (fx0, ftop, fx1, G), '#94584a')
    for r, y in enumerate(range(ftop, G, 5)):
        line(d, (fx0, y, fx1, y), '#76433a')
        for x in range(fx0 + (r % 2) * 5, fx1, 10):
            line(d, (x, y + 1, x, y + 4), '#76433a')
            px(d, x + 2, y + 1, '#ae6c5a')
    line(d, (fx0, ftop, fx0, G), '#ae6c5a')
    line(d, (fx1, ftop, fx1, G), '#5e352c')
    rect(d, (52, ftop - 6, 154, ftop), '#64503a')                   # 壁炉架
    line(d, (52, ftop - 6, 154, ftop - 6), '#8c7052')
    line(d, (52, ftop + 1, 154, ftop + 1), '#3e3024')
    rect(d, (60, ftop - 12, 63, ftop - 6), '#e6e0cc')                # 半截蜡烛
    px(d, 61, ftop - 13, '#3a3430')
    rect(d, (134, ftop - 9, 146, ftop - 7), '#3a3430')               # 扣着放倒的相框
    line(d, (134, ftop - 10, 146, ftop - 10), '#8a7a62')
    # 炉膛：拱顶 + 黑色内壁 + 炉栅
    bx0, bx1, btop = 78, 128, G - 44
    rect(d, (bx0, btop + 6, bx1, G), '#1c1816')
    ellipse(d, (bx0, btop, bx1, btop + 14), '#1c1816')
    for y in range(btop + 10, G, 5):
        line(d, (bx0 + 4, y, bx1 - 4, y), '#2a221e')
    for x in range(bx0 + 2, bx1, 6):                                 # 拱券的立砖
        a = (x - bx0) / (bx1 - bx0) * math.pi
        px(d, x, btop + 7 - 7 * math.sin(a), '#ae6c5a')
    rect(d, (bx0 + 6, G - 9, bx1 - 6, G - 8), '#3e3a38')             # 炉栅
    for x in range(bx0 + 8, bx1 - 6, 5):
        line(d, (x, G - 9, x, G - 3), '#3e3a38')
    # 炉膛口上面熏黑的一圈
    im = dither_fill(im, (bx0 - 2, btop - 6, bx1 + 2, btop), '#94584a', '#5e3a32', .45)
    d = ImageDraw.Draw(im)
    # ---- 大窗（窗外：雨停后的住宅区）
    wx0, wy0, wx1, wy1 = 166, 34, 306, 112
    mx = (wx0 + wx1) // 2
    view = new(wx1 - wx0, wy1 - wy0)
    vw, vh = view.size
    view = grad(view, (0, 0, vw, 40), ('#8e9aac', '#a4aebe', '#bcc4d0'))
    vd = ImageDraw.Draw(view)
    rect(vd, (0, 40, vw, vh), '#bcc4d0')
    cloud(view, 14, 16, 40, seed=3, cols=('#d0d6de', '#c0c8d2', '#a8b2c0'))
    cloud(view, 80, 12, 34, seed=4, cols=('#d0d6de', '#c0c8d2', '#a8b2c0'))
    vd = ImageDraw.Draw(view)
    # 对面的房子（屋顶 + 墙 + 窗）、围墙、电线杆、湿马路
    rect(vd, (8, 34, 92, 66), '#b8b2a6')
    view = tiled_roof(view, 6, 94, 24, 34, ('#56606e', '#44505c', '#6a7684', '#2e3640'))
    vd = ImageDraw.Draw(view)
    for x in (16, 44, 70):
        rect(vd, (x, 42, x + 14, 54), '#6e7c8c')
        line(vd, (x + 7, 42, x + 7, 54), '#c8c4b8')
    rect(vd, (100, 40, vw, 66), '#a8a498')
    view = tiled_roof(view, 98, vw + 4, 32, 40, ('#6a5248', '#54403a', '#7e665a', '#3a2c28'))
    vd = ImageDraw.Draw(view)
    rect(vd, (110, 46, 126, 58), '#6e7c8c')
    rect(vd, (0, 62, vw, 72), '#a09a8e')                             # 围墙
    for x in range(0, vw, 9):
        line(vd, (x, 62, x, 72), '#8e887c')
    line(vd, (0, 62, vw, 62), '#b6b0a4')
    rect(vd, (0, 72, vw, vh), '#5a5e66')                             # 湿马路
    for x in range(2, vw, 7):
        line(vd, (x, 73, x, 73 + (x * 7) % 4), '#8a92a2')
    rect(vd, (112, 4, 114, 72), '#7e7a72')                           # 电线杆
    line(vd, (100, 10, 126, 10), '#5e5a54')
    line(vd, (0, 14, vw, 18), '#3a3a40')
    line(vd, (0, 20, vw, 23), '#3a3a40')
    view = tint(view, (.94, .96, 1.0))
    im.alpha_composite(view, (wx0, wy0))
    d = ImageDraw.Draw(im)
    # 玻璃上的反光斜条
    for k in range(3):
        for i in range(10):
            px(d, wx0 + 14 + k * 46 + i, wy0 + 30 - i, '#dfe5ec')
    # 窗框
    rect(d, (wx0 - 4, wy0 - 4, wx1 + 4, wy0), '#e0d9cb')
    rect(d, (wx0 - 4, wy1, wx1 + 4, wy1 + 3), '#e0d9cb')
    rect(d, (wx0 - 4, wy0 - 4, wx0, wy1 + 3), '#e0d9cb')
    rect(d, (wx1, wy0 - 4, wx1 + 4, wy1 + 3), '#e0d9cb')
    rect(d, (mx - 2, wy0, mx + 1, wy1), '#e0d9cb')
    rect(d, (wx0, wy0 + 20, wx1, wy0 + 22), '#e0d9cb')               # 上面的气窗横档
    line(d, (wx0 - 4, wy1 + 4, wx1 + 4, wy1 + 4), '#a49c8a')
    line(d, (wx0, wy0, wx1, wy0), '#b8b0a0')
    rect(d, (wx0 - 10, wy1 + 4, wx1 + 10, wy1 + 7), '#cfc8b8')       # 窗台板
    line(d, (wx0 - 10, wy1 + 8, wx1 + 10, wy1 + 8), '#9c9482')
    # 光秃秃的窗帘杆 + 左边剩下的一片纱帘
    rect(d, (wx0 - 14, 27, wx1 + 14, 28), '#6a5644')
    ellipse(d, (wx0 - 17, 25, wx0 - 12, 30), '#6a5644')
    ellipse(d, (wx1 + 12, 25, wx1 + 17, 30), '#6a5644')
    curtain = Image.new('L', (W, 180), 0)
    cd = ImageDraw.Draw(curtain)
    cd.polygon([(wx0 - 8, 29), (wx0 + 18, 29), (wx0 + 10, 70), (wx0 + 14, wy1 + 2), (wx0 - 8, wy1 + 2)], fill=255)
    cm = np.array(curtain) > 0
    a = np.array(im)
    yy, xx = np.mgrid[0:180, 0:W]
    lace = cm & (((xx + yy) % 2) == 0)
    a[lace, :3] = (a[lace, :3] * .5 + np.array(c3('#f2f0ea')) * .5).astype(np.uint8)
    edge = cm & ~np.roll(cm, 1, axis=1)
    a[edge, :3] = np.array(c3('#e6e2da'))
    fold = cm & ((xx - wx0 + 8) % 7 == 0) & (yy % 2 == 0)
    a[fold, :3] = np.array(c3('#cfccc4'))
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # ---- 窗下盖着白布的沙发
    sx0, sx1 = 178, 296
    sheet = [(sx0, G - 2), (sx0 - 2, G - 18), (sx0 + 4, G - 30), (sx0 + 16, G - 34), (sx1 - 16, G - 34), (sx1 - 4, G - 30),
             (sx1 + 2, G - 18), (sx1, G - 2)]
    poly(d, sheet, '#e6e4de')
    poly(d, [(sx0 + 4, G - 22), (sx1 - 4, G - 22), (sx1 - 2, G - 18), (sx0 + 2, G - 18)], '#cfcdc6')   # 坐垫的棱
    for x in (204, 236, 262):                                        # 布的褶子
        line(d, (x, G - 30, x - 3, G - 3), '#c8c6be')
        line(d, (x + 1, G - 30, x - 2, G - 3), '#f4f2ee')
    for x in range(sx0, sx1, 4):                                     # 下摆的波浪
        px(d, x, G - 2 - (x // 4) % 2, '#bebcb4')
    line(d, (sx0 + 16, G - 34, sx1 - 16, G - 34), '#f6f4f0')
    # ---- 小圆桌（花瓶另做一层）
    rect(d, (337, G - 30, 341, G - 4), '#5a4230')
    line(d, (337, G - 30, 337, G - 4), '#7a5a40')
    for s in (-1, 1):
        line(d, (339, G - 6, 339 + s * 9, G), '#5a4230')
    line(d, (339, G - 4, 339, G), '#5a4230')
    ellipse(d, (314, G - 35, 364, G - 29), '#6e5038')
    ellipse(d, (314, G - 36, 364, G - 31), '#8a6648')
    line(d, (320, G - 35, 356, G - 35), '#a07a58')
    # ---- 纸箱一摞
    for bx, by, bw, bh in ((370, G - 22, 30, 22), (374, G - 38, 24, 16)):
        rect(d, (bx, by, bx + bw, by + bh), '#b08a5a')
        line(d, (bx, by, bx + bw, by), '#c8a274')
        line(d, (bx + bw, by, bx + bw, by + bh), '#8a6a42')
        rect(d, (bx + bw // 2 - 1, by, bx + bw // 2 + 1, by + bh), '#c8b48c')
        rect(d, (bx + 4, by + 5, bx + 11, by + 8), '#ece4d0')
    # ---- 电话台 + 九十年代的按键电话
    rect(d, (404, G - 30, 436, G), '#6a5038')
    line(d, (404, G - 30, 436, G - 30), '#8c6c4e')
    rect(d, (408, G - 24, 432, G - 18), '#5a422e')
    px(d, 420, G - 21, '#d0b070')
    rect(d, (408, G - 14, 432, G - 2), '#5a422e')
    poly(d, [(409, G - 31), (431, G - 31), (428, G - 37), (412, G - 37)], '#26242a')      # 机身
    line(d, (412, G - 37, 428, G - 37), '#4a4852')
    for i in range(3):
        for j in range(2):
            px(d, 416 + i * 3, G - 35 + j * 2, '#c8c4cc')
    rect(d, (408, G - 41, 432, G - 38), '#26242a')                   # 听筒
    rect(d, (406, G - 42, 411, G - 37), '#26242a')
    rect(d, (429, G - 42, 434, G - 37), '#26242a')
    line(d, (410, G - 41, 430, G - 41), '#4a4852')
    for i in range(6):                                               # 卷线 + 墙上的插口
        px(d, 435 + i, G - 30 + i * 2 + (i % 2), '#26242a')
    rect(d, (439, G - 52, 442, G - 48), '#e8e2d2')
    line(d, (440, G - 48, 440, G - 30), '#26242a')
    # ---- 上二楼的楼梯（往右上走出画）
    rect(d, (444, 16, W, G), '#c4bca8')
    for i in range(5):                                               # 踏步：8 宽 11 高
        sx, sy = 448 + i * 8, G - i * 11
        rect(d, (sx, sy - 11, W, sy), '#7a5e44')
        rect(d, (sx, sy - 11, W, sy - 9), '#a88a68')                 # 踏板
        line(d, (sx, sy - 8, W, sy - 8), '#5e4634')
        line(d, (sx, sy - 11, sx, sy), '#6a5038')
    for i in range(5):                                               # 扶手和栏杆
        x = 450 + i * 8
        y = G - 11 * i - 11
        line(d, (x, y - 24, x, y), '#4e3a2a')
    line(d, (446, G - 30, W, G - 30 - (W - 446) * 11 / 8), '#6e5038', 2)
    line(d, (446, G - 31, W, G - 31 - (W - 446) * 11 / 8), '#8c6c4e')
    rect(d, (444, G - 34, 448, G), '#5a4230')                        # 起步柱
    rect(d, (443, G - 37, 449, G - 34), '#7a5a40')
    # ---- 灯：天花板垂下来的光秃秃的灯泡（不亮）
    line(d, (236, 16, 236, 22), '#3a3430')
    rect(d, (234, 22, 238, 24), '#6a645a')
    ellipse(d, (233, 24, 239, 30), '#e8e4d0')
    px(d, 234, 26, '#ffffff')
    # ---- 地上：壁炉前的石板、门口散落的传单、灰尘
    rect(d, (50, G, 156, G + 4), '#8a8680')
    line(d, (50, G, 156, G), '#a8a49c')
    line(d, (50, G + 4, 156, G + 4), '#6a6660')
    for i, (x, y) in enumerate(((22, G + 6), (34, G + 12), (54, G + 20), (16, G + 22), (66, G + 9))):
        rect(d, (x, y, x + 7, y + 3), '#ece8dc' if i % 2 else '#e4d8b0')
        line(d, (x + 1, y + 1, x + 5, y + 1), '#b8a88a')
    im = noise_specks(im, (0, G + 1, W, 180), ['#c4a880', '#8c6c4c', '#d0b890'], 520, 71)
    # 窗下的地上：阴天的淡光
    lm = Image.new('L', (W, 180), 0)
    ImageDraw.Draw(lm).polygon([(wx0 - 6, G + 2), (wx1 + 6, G + 2), (wx1 - 6, 179), (wx0 - 30, 179)], fill=255)
    f = np.array(lm.filter(ImageFilter.BoxBlur(6))).astype(float) / 255
    fq = np.clip(np.floor(f * 3 + bayer(180, W) - .4) / 3, 0, 1)
    room = np.array(im).astype(float)
    sel = fq > .3
    room[sel, :3] = room[sel, :3] * .92 + np.array([226, 230, 236]) * .08
    im = Image.fromarray(room.astype(np.uint8), 'RGBA')
    # 蜘蛛网（左上角、楼梯顶上）
    d = ImageDraw.Draw(im)
    for cx, cy, s in ((0, 17, 1), (W - 1, 17, -1)):
        for r in (5, 9, 13):
            line(d, (cx, cy + r, cx + s * r, cy), '#ece8de')
        for k in range(4):
            a_ = k * math.pi / 8 + .1
            line(d, (cx, cy, cx + s * 14 * math.cos(a_), cy + 14 * math.sin(a_)), '#e2ded4')
    # 整间屋子调成阴天的冷灰
    im = tint(im, (.9, .93, .99), (2, 3, 8), desat=.18)
    win = (wx0, wy0, wx1, wy1, mx)
    return im, G, win


def eh_ash():
    """炉膛里的烟灰：撒一次少一层（pick values 0..3）"""
    out = []
    for k in range(4):
        im = new(50, 14)
        d = ImageDraw.Draw(im)
        h = [9, 6, 3, 0][k]
        if h:
            rx = int(h * 2.5)
            ellipse(d, (25 - rx, 13 - h, 25 + rx, 13 + h), '#8a8680')
            ellipse(d, (25 - rx * .8, 13 - h, 25 + rx * .5, 13 + h // 2), '#a8a49c')
            rng = np.random.RandomState(80 + k)
            for _ in range(h * 6):
                x, y = rng.randint(25 - rx, 25 + rx), rng.randint(13 - h, 13)
                if im.getpixel((x, y))[3]:
                    px(d, x, y, ['#6e6a66', '#c4c0b8', '#5a5654'][rng.randint(3)])
        for x in range(3, 47, 5):                                    # 炉底撒落的一层薄灰（撒光了也剩一点）
            px(d, x, 13, '#6e6a66')
        out.append(im)
    return out


def eh_vase(G):
    """小圆桌上的青花瓷花瓶：0 好的 / 1 碎了（桌上剩瓶底，碎片散到地上）。图层原点 (300, G - 62)"""
    ox, oy = 300, G - 62
    ok = new(84, 92)
    d = ImageDraw.Draw(ok)
    cx, base = 339 - ox, G - 36 - oy
    prof = [(0, 4), (3, 6), (6, 8), (10, 9), (14, 9), (17, 8), (20, 5), (22, 3), (24, 3), (26, 4)]   # (离瓶底高度, 半径)
    for i in range(len(prof) - 1):
        (h0, r0), (h1, r1) = prof[i], prof[i + 1]
        for h in range(h0, h1):
            r = r0 + (r1 - r0) * (h - h0) / (h1 - h0)
            y = base - h
            line(d, (cx - r, y, cx + r, y), '#eef0f4')
            px(d, cx - r, y, '#c8ccd6')
            px(d, cx + r, y, '#a8aebc')
            px(d, cx + r - 1, y, '#c8ccd6')
    for y in range(base - 15, base - 9):                             # 青花：一圈缠枝
        px(d, cx - 6 + (y % 3) * 2, y, '#3a5aa8')
        px(d, cx + 2 + ((y + 1) % 3) * 2, y, '#3a5aa8')
    line(d, (cx - 8, base - 17, cx + 8, base - 17), '#3a5aa8')
    line(d, (cx - 8, base - 7, cx + 8, base - 7), '#3a5aa8')
    line(d, (cx - 2, base - 22, cx - 2, base - 19), '#ffffff')
    line(d, (cx - 4, base - 14, cx - 4, base - 6), '#ffffff')
    line(d, (cx - 4, base - 26, cx + 4, base - 26), '#c8ccd6')
    # 插着的两枝干花
    line(d, (cx - 1, base - 26, cx - 6, base - 36), '#7a6a4a')
    line(d, (cx + 1, base - 26, cx + 5, base - 38), '#7a6a4a')
    for x, y in ((cx - 6, base - 37), (cx + 5, base - 39), (cx - 3, base - 33)):
        px(d, x, y, '#b89a6a')
        px(d, x + 1, y, '#a07e52')
    broken = new(84, 92)
    d = ImageDraw.Draw(broken)
    for h, r in ((0, 4), (1, 5), (2, 6), (3, 7)):                    # 剩下的瓶底，豁口参差
        line(d, (cx - r, base - h, cx + r, base - h), '#eef0f4')
        px(d, cx + r, base - h, '#a8aebc')
    for x in (cx - 6, cx - 3, cx + 1, cx + 5):
        px(d, x, base - 4, '#eef0f4')
    line(d, (cx - 7, base - 2, cx + 7, base - 2), '#3a5aa8')
    rng = np.random.RandomState(91)
    shards = [(cx - 14, base + 1), (cx + 12, base + 1), (cx - 20, base + 30), (cx + 18, base + 38), (cx - 4, base + 44),
              (cx + 30, base + 26), (cx - 30, base + 48), (cx + 6, base + 52)]
    for i, (x, y) in enumerate(shards):
        s = rng.randint(2, 4)
        pts = [(x, y - s), (x + s + 1, y), (x + rng.randint(-1, 2), y + s - 1), (x - s, y + rng.randint(0, 2))]
        poly(d, pts, '#eef0f4')
        line(d, (x - s, y, x + s, y), '#c8ccd6')
        if i % 2:
            px(d, x, y - 1, '#3a5aa8')
    for _ in range(18):
        px(d, cx + rng.randint(-34, 34), base + rng.randint(30, 56), ['#eef0f4', '#c8ccd6'][rng.randint(2)])
    line(d, (cx - 22, base + 40, cx - 10, base + 44), '#7a6a4a')    # 干花掉在地上
    px(d, cx - 23, base + 40, '#b89a6a')
    return [ok, broken], (ox, oy)


def eh_glass(win):
    """窗玻璃右扇被打出一个洞（碎片扔出去 / 空气弹钻进来）"""
    wx0, wy0, wx1, wy1, mx = win
    im = new(wx1 - wx0, wy1 - wy0)
    d = ImageDraw.Draw(im)
    cx, cy = (mx + wx1) // 2 - wx0, 52
    for k in range(9):
        a = k * 2 * math.pi / 9 + .3
        r = 18 + (k * 7) % 11
        line(d, (cx, cy, cx + r * math.cos(a), cy + r * .8 * math.sin(a)), '#f2f6fa')
    ring = [(cx + 7 * math.cos(a) + (2 if i % 2 else -1), cy + 6 * math.sin(a)) for i, a in
            enumerate(np.linspace(0, 2 * math.pi, 10, endpoint=False))]
    poly(d, ring, '#4a525e')
    for i in range(len(ring)):
        x0_, y0_ = ring[i]
        x1_, y1_ = ring[(i + 1) % len(ring)]
        line(d, (x0_, y0_, x1_, y1_), '#e6ecf2')
    return im


def eh_ring():
    """电话铃响：听筒两边的“震动线”，4 帧，第 4 帧停一拍"""
    n, w, h = 4, 48, 20
    out = strip_frames(n, w, h)
    d = ImageDraw.Draw(out)
    for f in range(3):
        ox = f * w
        r = 3 + f
        for s in (-1, 1):
            cx = ox + 24 + s * (16 + f)
            for k in range(3):
                y = 6 + k * 3
                line(d, (cx, y, cx + s * r, y - 1 + k), '#f4e080' if k != 1 else '#ffffff')
        line(d, (ox + 20, 1 + f % 2, ox + 28, 1 + f % 2), '#f4e080')
    return out


def eh_drip(win):
    """窗外屋檐滴下来的水（雨刚停）：8 帧循环，只在玻璃范围里"""
    wx0, wy0, wx1, wy1, mx = win
    w, h, n = wx1 - wx0, wy1 - wy0, 8
    out = strip_frames(n, w, h)
    d = ImageDraw.Draw(out)
    for x, ph in ((12, 0), (38, 3), (58, 5), (88, 2), (116, 6), (130, 1)):
        if abs(wx0 + x - mx) < 4:
            continue
        for f in range(n):
            t = ((f + ph) % n) / n
            y = 2 + t * (h - 10)
            d.line([(f * w + x, int(y)), (f * w + x, int(y) + 3)], fill=C('#e6eef6', 220))
            px(d, f * w + x, int(y) + 4, '#ffffff')
    return out


def empty_house():
    W = 480
    room, G, win = eh_room()
    ash = eh_ash()
    (vase_ok, vase_bk), (vox, voy) = eh_vase(G)
    glass = eh_glass(win)
    ring = eh_ring()
    drip = eh_drip(win)
    wx0, wy0, wx1, wy1, mx = win
    layers = {'room': room, 'vase_ok': vase_ok, 'vase_broken': vase_bk, 'glass_hole': glass, 'ring': ring, 'drip': drip}
    for i, im in enumerate(ash):
        layers[f'ash_{i}'] = im
    K = 'bg/empty_house/'
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(door=[26, 148], fireplace=[103, 148], ash=[103, G - 6], window=[236, 74], window_r=[(mx + wx1) // 2, 74],
                             window_floor=[236, 148], sofa=[237, 146], vase=[339, 148], vase_top=[339, G - 50], boxes=[384, 146],
                             phone=[420, 148], phone_top=[420, G - 40], stairs=[460, 148], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': K + 'room', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': K + 'drip', 'n': 8, 'fps': 6, 'k': 1, 'x': wx0, 'y': wy0},
                        {'type': 'image', 'image': K + 'glass_hole', 'k': 1, 'x': wx0, 'y': wy0, 'key': 'glass'},
                        {'type': 'pick', 'images': [K + f'ash_{i}' for i in range(4)], 'values': [0, 1, 2, 3], 'key': 'ash', 'k': 1,
                         'x': 78, 'y': G - 14},
                        {'type': 'pick', 'images': [K + 'vase_ok', K + 'vase_broken'], 'key': 'vase', 'k': 1, 'x': vox, 'y': voy},
                        {'type': 'strip', 'image': K + 'ring', 'n': 4, 'fps': 10, 'k': 1, 'x': 396, 'y': G - 50, 'key': 'ring'},
                        {'type': 'tint', 'color': '#203050', 'alpha': 0.06}],
                fg=[])
    pv = room.copy()
    pv.alpha_composite(ash[0], (78, G - 14))
    pv.alpha_composite(vase_ok, (vox, voy))
    preview('empty_house', {'room': pv}, ['room'], W)
    pv2 = room.copy()
    pv2.alpha_composite(ash[2], (78, G - 14))
    pv2.alpha_composite(vase_bk, (vox, voy))
    pv2.alpha_composite(glass, (wx0, wy0))
    pv2.alpha_composite(ring.crop((48, 0, 96, 20)), (396, G - 50))
    pv2.save(os.path.join(LIB.ASSETS, 'preview', 'bg_empty_house_after.png'))
    save_layers('empty_house', layers, meta)
    return meta


# ============================================================ 住宅区街道 residential_street（960 宽，雨刚停的阴天）
#   段 D、段 E：仗助走出空房子以后的近身战，救护车开来，ACT3 和时停。左起：邻家、那间空房子的外面（“売家”牌、关着的雨户）、
#   邻家、垃圾站、岔路口（弯道镜）、开着绣球花的人家、自动售货机、邻家、自行车。路面和人行道都是湿的，到处是水洼。
#   可切换：ambulance（pick：0 没有 / 1 停着 / 2 倒车，倒车灯亮）、siren（1 = 车顶红灯转）、rain（1 = 又下起小雨）、pm（傍晚色）。
AMB_X, AMB_Y = 690, 99          # 停在路的里侧（车轮落在 y 146，人站在它前面）


def hydrangea(img, x0, x1, top, bot, seed=0):
    """绣球花丛（七月的雨季）：一团团圆的花球，蓝紫 / 粉"""
    img = hedge(img, x0, x1, top + 4, bot, seed=seed, cols=('#2a4e36', '#3e6a44', '#5a8a52', '#78a868'))
    d = ImageDraw.Draw(img)
    rng = np.random.RandomState(seed)
    for _ in range(int((x1 - x0) / 5)):
        cx, cy = rng.randint(x0 + 3, x1 - 3), rng.randint(top + 2, bot - 4)
        pal = [('#6a6ab8', '#8a8ad8', '#b4b4ec'), ('#8a5aa8', '#aa7ac8', '#d0a8e4'), ('#c86a94', '#e08ab0', '#f4b8d0')][rng.randint(3)]
        ellipse(d, (cx - 3, cy - 3, cx + 3, cy + 3), pal[0])
        ellipse(d, (cx - 3, cy - 3, cx + 1, cy + 1), pal[1])
        px(d, cx - 1, cy - 2, pal[2])
        px(d, cx + 1, cy, pal[2])
    return img


def curve_mirror(img, x, ground):
    d = ImageDraw.Draw(img)
    rect(d, (x - 1, ground - 78, x + 1, ground), '#e07a2a')
    line(d, (x - 1, ground - 78, x - 1, ground), '#f09a4a')
    for y in range(ground - 60, ground, 10):
        line(d, (x - 1, y, x + 1, y), '#f4f0e6')
    ellipse(d, (x - 12, ground - 100, x + 12, ground - 76), '#e07a2a')
    ellipse(d, (x - 10, ground - 98, x + 10, ground - 78), '#8a98aa')
    ellipse(d, (x - 9, ground - 97, x + 6, ground - 84), '#a8b6c6')
    line(d, (x - 6, ground - 82, x + 6, ground - 82), '#5a5e66')     # 镜子里弯过去的路
    line(d, (x - 4, ground - 86, x - 2, ground - 92), '#e6e2d6')
    return img


def empty_house_ext(img, x, ground):
    """那间空房子的外面：两层，外墙发灰、二楼雨户关着、一楼窗户里没窗帘，信箱塞满了传单，围墙上挂“売家”牌"""
    w, h = 130, 80
    img = house(img, x, ground, w, h, wall='#d2ccbf', wall2='#aea898', seed=61, roof=('#4a4e56', '#383c44', '#5e646e', '#24282e'),
                door='#6a5a4a', curtain=None)
    d = ImageDraw.Draw(img)
    top = ground - h
    for i in range(2):                                               # 二楼的雨户（防雨窗板）关着
        wx = x + 10 + i * (w // 2)
        rect(d, (wx - 1, top + 7, wx + 23, top + 25), '#8a8a86')
        for k in range(wx + 2, wx + 22, 4):
            line(d, (k, top + 8, k, top + 24), '#74746e')
        line(d, (wx - 1, top + 7, wx + 23, top + 7), '#a4a49e')
    rect(d, (x + 8, ground - 30, x + 40, ground - 10), '#2e3238')    # 一楼窗户：屋里黑着，没窗帘
    rect(d, (x + 23, ground - 30, x + 24, ground - 10), '#e2ddd0')
    for i in range(4):
        px(d, x + 12 + i * 7, ground - 26 + i % 2, '#8a96a6')
    # 外墙的水渍（从屋檐往下）
    for k in (x + 6, x + 52, x + 98):
        for y in range(top + 2, top + 22, 2):
            px(d, k + (y // 2) % 2, y, '#bab4a6')
    return img


def ambulance(reverse=False):
    """九十年代的高顶救护车（侧面，车头朝右）：白车身、红腰线、车身红字“救急車”、车顶红灯。reverse = 倒车灯 + 刹车灯亮"""
    w, h = 90, 48
    im = new(w, h)
    d = ImageDraw.Draw(im)
    rect(d, (2, 4, 64, 38), '#f2f2ee')                               # 后厢
    line(d, (2, 4, 64, 4), '#ffffff')
    line(d, (2, 4, 2, 38), '#c8ccd0')
    poly(d, [(64, 12), (78, 14), (88, 28), (88, 38), (64, 38)], '#f2f2ee')   # 驾驶室
    poly(d, [(66, 15), (77, 16), (84, 27), (66, 27)], '#4e5e70')     # 车窗
    line(d, (68, 17, 74, 25), '#8aa0b6')
    rect(d, (2, 27, 88, 30), '#d02a34')                              # 红腰线
    line(d, (2, 31, 88, 31), '#a01e28')
    kanji(im, 10, 8, '救急車', '#d02a34')
    rect(d, (48, 8, 60, 22), '#cfd6dc')                              # 后厢侧窗（磨砂）
    line(d, (48, 15, 60, 15), '#f2f2ee')
    line(d, (40, 6, 40, 37), '#d0d4d8')                              # 侧滑门的缝
    px(d, 37, 22, '#8a8e92')
    rect(d, (0, 36, 90, 40), '#6a6e74')                              # 保险杠 + 底盘
    line(d, (0, 36, 90, 36), '#9a9ea4')
    rect(d, (85, 30, 89, 33), '#fff4c0')                             # 大灯
    tail = '#ff4040' if reverse else '#b02a30'
    rect(d, (1, 28, 3, 34), tail)                                    # 尾灯
    if reverse:
        rect(d, (1, 24, 3, 27), '#ffffff')                           # 倒车灯
        px(d, 0, 25, '#fff8d0')
    for wx in (16, 72):                                              # 轮子
        ellipse(d, (wx - 7, 34, wx + 7, 47), '#1e1e22')
        ellipse(d, (wx - 3, 38, wx + 3, 44), '#8a8e94')
        px(d, wx, 41, '#cfd2d6')
    rect(d, (6, 0, 18, 4), '#a8222c')                                # 车顶红灯（灭）
    rect(d, (62, 8, 74, 12), '#a8222c')
    line(d, (6, 0, 18, 0), '#d04a52')
    line(d, (62, 8, 74, 8), '#d04a52')
    rect(d, (24, 1, 34, 4), '#e6e8ea')                               # 车顶扬声器
    return im


def siren_strip():
    """车顶红灯轮流亮（4 帧），叠在救护车上；画在 90×20 的框里（灯在框里 y 0–12）"""
    n, w, h = 4, 90, 20
    out = strip_frames(n, w, h)
    d = ImageDraw.Draw(out)
    for f in range(n):
        ox = f * w
        for (x0, y0), on in (((6, 0), f in (0, 1)), ((62, 8), f in (2, 3))):
            if not on:
                continue
            rect(d, (ox + x0, y0, ox + x0 + 12, y0 + 4), '#ff3a44')
            rect(d, (ox + x0 + 2, y0 + 1, ox + x0 + 10, y0 + 3), '#ffb0b0')
            for k in range(-3, 16, 3):                               # 一圈抖动的红晕
                px(d, ox + x0 + k, y0 - 1 if y0 else y0 + 6, '#ff6a70')
                if y0:
                    px(d, ox + x0 + k + 1, y0 - 2, '#ff6a70')
    return out


def street_far():
    far = sky_far(640, seed=21, cols=('#7e8ca2', '#96a2b4', '#b0bac8', '#c8d0da'), sea=False)
    d = ImageDraw.Draw(far)
    # 云缝里透出来的一点亮（雨停了）
    for x0, y0, w in ((120, 26, 70), (420, 18, 60)):
        for i in range(4):
            line(d, (x0 + i * 4, y0 + i, x0 + w - i * 3, y0 + i), mix('#c8d0da', '#eef2f4', .6 - i * .12))
    a = np.array(far).astype(float)
    hi = a[..., :3].mean(axis=2) > 214                               # 白云 → 灰云
    a[hi, :3] = a[hi, :3] * .86 + np.array([150, 160, 176]) * .14
    far = Image.fromarray(a.astype(np.uint8), 'RGBA')
    return tint(far, (.96, .97, 1.0), desat=.12)


def street_near():
    W, G = 960, 136
    near = new(W, 180)
    roofs = [('#3e4a5e', '#2e3848', '#56647a', '#1e2632'), ('#6a3e36', '#4e2c28', '#8a5246', '#341c1a'),
             ('#3a5a52', '#2a4440', '#4e766a', '#1c2e2a')]
    for x, w, h, s, wall in ((-6, 104, 74, 1, '#e2dccc'), (380, 96, 70, 2, '#dfe2e6'), (612, 100, 78, 3, '#efe2cc'),
                              (762, 104, 72, 4, '#e2d6c6'), (880, 90, 68, 5, '#e8e4d8')):
        near = house(near, x, G - 10, w, h, wall=wall, wall2=mix(wall, '#000000', .18), seed=s, roof=roofs[s % 3])
    near = empty_house_ext(near, 200, G - 10)
    d = ImageDraw.Draw(near)
    # 岔路（520–596）：一条往里拐的小路，路面收窄到远处
    poly(d, [(520, G), (596, G), (566, 104), (552, 104)], '#56585e')
    for y in range(106, G, 6):
        t = (y - 104) / (G - 104)
        px(d, 559 + t * 2, y, '#d8d4c8')
    near = block_wall(near, 470, 520, G - 18, G)
    near = block_wall(near, 596, 612, G - 18, G)
    # 围墙 + 树篱 + 门柱
    for x0, x1 in ((0, 70), (98, 200), (480, 520)):
        near = hedge(near, x0, x1, G - 26, G - 18, seed=x0 + 3)
        near = block_wall(near, x0, x1, G - 18, G)
    for x0, x1 in ((200, 290), (318, 330), (330, 380), (612, 650), (676, 760), (762, 830), (858, 960)):
        near = block_wall(near, x0, x1, G - 18, G)
    near = hedge(near, 330, 470, G - 26, G - 18, seed=37)
    near = block_wall(near, 380, 470, G - 18, G)
    near = hedge(near, 762, 830, G - 26, G - 18, seed=41)
    near = hedge(near, 858, 960, G - 26, G - 18, seed=43)
    near = hydrangea(near, 612, 760, G - 30, G - 16, seed=45)        # 绣球花那家
    near = block_wall(near, 612, 650, G - 18, G)
    near = block_wall(near, 676, 760, G - 18, G)
    # 空房子门前：杂草长出来、门柱、塞满传单的信箱、“売家”牌
    near = hedge(near, 200, 290, G - 30, G - 18, seed=47, cols=('#3a5a3a', '#527a48', '#6e9858', '#8cb06a'))
    near = block_wall(near, 200, 290, G - 18, G)
    d = ImageDraw.Draw(near)
    for gx in (290, 312):
        rect(d, (gx, G - 30, gx + 6, G), '#a8a094')
        rect(d, (gx - 1, G - 32, gx + 7, G - 30), '#c4bcae')
    rect(d, (278, G - 30, 288, G - 20), '#7a7e86')                  # 信箱
    rect(d, (279, G - 28, 287, G - 26), '#2a2a2a')
    for i in range(4):
        rect(d, (279 + i * 2, G - 29 - i % 2, 280 + i * 2, G - 26), '#f2eee2')
    rect(d, (282, G - 20, 284, G - 8), '#5a5a5e')
    rect(d, (226, G - 34, 258, G - 18), '#f4f2ea')                  # 売家 牌子
    rect(d, (226, G - 34, 258, G - 33), '#d02a34')
    kanji(near, 230, G - 33, '売家', '#d02a34')
    for i in range(6):
        px(d, 232 + i * 4, G - 20, '#3a3a40')
    line(d, (230, G - 18, 230, G - 14), '#8a8a86')
    line(d, (254, G - 18, 254, G - 14), '#8a8a86')
    # 垃圾站（绿网罩着几袋垃圾）
    for i, (bx, col) in enumerate(((486, '#e8e8e0'), (496, '#d8dce4'), (506, '#e4e0d4'))):
        ellipse(d, (bx - 6, G - 12, bx + 6, G + 1), col)
        px(d, bx - 2, G - 8, '#b8b8b0')
    for x in range(478, 516, 3):
        line(d, (x, G - 14, x + 2, G + 1), '#3a8a4a')
    line(d, (478, G - 13, 515, G - 13), '#3a8a4a')
    rect(d, (470, G - 30, 480, G - 22), '#f4f2ea')                  # 收垃圾日的小牌
    line(d, (472, G - 27, 478, G - 27), '#3a8a4a')
    line(d, (472, G - 25, 477, G - 25), '#8a8a86')
    # 电线杆 + 电线、弯道镜
    poles = [90, 340, 610, 830]
    for x in poles:
        near = pole(near, x, G + 2, 126)
    near = wires(near, [(x, G + 2 - 126 + 7) for x in poles], sag=9)
    near = curve_mirror(near, 598, G + 2)
    near = vending(near, 662, G + 2, body='#2a5ab0', accent='#eef2f8')
    d = ImageDraw.Draw(near)
    # 自行车（靠在最右边那家门口）
    bx, by = 900, G - 2
    for wx in (bx, bx + 18):
        d.ellipse((wx - 6, by - 6, wx + 6, by + 6), outline=C('#2a2a30'), width=2)
        line(d, (wx - 5, by, wx + 5, by), '#8a8a90')
        line(d, (wx, by - 5, wx, by + 5), '#8a8a90')
    line(d, (bx, by, bx + 8, by - 8), '#c83a3a')
    line(d, (bx + 8, by - 8, bx + 18, by), '#c83a3a')
    line(d, (bx + 8, by - 8, bx + 16, by - 9), '#c83a3a')
    line(d, (bx + 16, by - 9, bx + 18, by), '#c83a3a')
    rect(d, (bx + 5, by - 11, bx + 9, by - 10), '#2a2a30')
    line(d, (bx + 16, by - 9, bx + 17, by - 13), '#8a8a90')
    rect(d, (bx + 14, by - 14, bx + 20, by - 13), '#2a2a30')
    # 湿的人行道和马路
    near = sidewalk(near, 0, W, G, 162, cols=('#9a9890', '#8a8880', '#aeaca4', '#7c7a74'))
    near = asphalt(near, 0, W, 162, 180, cols=('#3e3e46', '#36363e', '#4a4a54', '#5a5a64'))
    near = rain_ground(near, 166, 180, 9, '#6e7690')
    sw = Image.new('L', (W, 180), 0)                                 # 人行道上没干的深色水迹
    sd = ImageDraw.Draw(sw)
    rng = np.random.RandomState(29)
    for _ in range(26):
        cx, cy = rng.randint(0, W), rng.randint(G + 3, 160)
        sd.ellipse((cx - rng.randint(10, 30), cy - 3, cx + rng.randint(10, 30), cy + 3), fill=255)
    f = np.array(sw.filter(ImageFilter.BoxBlur(3))).astype(float) / 255
    a = np.array(near).astype(float)
    m = (np.floor(f * 2 + bayer(180, W) - .2) >= 1) & (np.arange(180)[:, None] > G) & (np.arange(180)[:, None] < 162)
    a[m, :3] *= .86
    near = Image.fromarray(a.astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(near)
    for x in range(0, W, 3):                                          # 路缘石上一条湿亮边
        px(d, x, 162, '#8a92a4' if (x // 3) % 2 else '#a8b0c0')
    for cx, cy, w in ((60, 170, 40), (178, 152, 22), (320, 174, 50), (452, 156, 18), (560, 168, 34), (700, 150, 20),
                      (820, 172, 44), (930, 154, 24)):
        near = puddle(near, cx, cy, w, cols=('#55647e', '#94a2bc', '#d4dce8'))
    # 水洼里的倒影：电线杆
    d = ImageDraw.Draw(near)
    for x in poles:
        for y in range(G + 4, G + 12, 2):
            px(d, x, y, '#6a6e76')
    return near, G


def residential_street():
    W = 960
    far = street_far()
    near, G = street_near()
    amb = ambulance(False)
    amb_r = ambulance(True)
    none = new(1, 1)
    siren = siren_strip()
    rain = rain_strip(320, 180, n=10, near=36, far=30, length=(6, 4), slant=-0.18, cols=('#c8d4e8', '#8e9cb8'), alpha=(150, 100), seed=91)
    layers = {'far': far, 'near': near, 'amb_none': none, 'ambulance': amb, 'ambulance_rev': amb_r, 'siren': siren, 'rain': rain}
    K = 'bg/residential_street/'
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 174],
                anchors=dict(emptyhouse=[264, 146], emptyhouse_gate=[304, 148], emptyhouse_win=[224, 112], forsale=[242, 146],
                             garbage=[496, 146], sideroad=[558, 146], mirror=[598, 146], hydrangea=[686, 146], vending=[673, 148],
                             ambulance=[AMB_X + 45, 150], amb_rear=[AMB_X - 8, 150], amb_door=[AMB_X + 40, 150],
                             amb_front=[AMB_X + 98, 150], bike=[909, 146], walk_x=[8, 952]),
                layers=[{'type': 'pano', 'image': K + 'far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': K + 'near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'pick', 'images': [K + 'amb_none', K + 'ambulance', K + 'ambulance_rev'], 'values': [0, 1, 2],
                         'key': 'ambulance', 'k': 1, 'x': AMB_X, 'y': AMB_Y},
                        {'type': 'strip', 'image': K + 'siren', 'n': 4, 'fps': 6, 'k': 1, 'x': AMB_X, 'y': AMB_Y, 'key': 'siren'},
                        {'type': 'tint', 'color': '#203050', 'alpha': 0.08},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[{'type': 'strip', 'image': K + 'rain', 'n': 10, 'fps': 14, 'screen': True, 'x': 0, 'y': 0, 'w': 320, 'h': 180,
                     'alpha': 0.7, 'key': 'rain'}])
    pv = far.resize((W, 180), Image.NEAREST)
    pv.alpha_composite(near)
    preview('residential_street', {'room': pv}, ['room'], W)
    pv2 = pv.copy()
    pv2.alpha_composite(amb, (AMB_X, AMB_Y))
    pv2.alpha_composite(siren.crop((0, 0, 90, 20)), (AMB_X, AMB_Y))
    pv2.save(os.path.join(LIB.ASSETS, 'preview', 'bg_residential_street_amb.png'))
    save_layers('residential_street', layers, meta)
    return meta


# ============================================================ 亿泰的梦 afterlife_dream（320 宽，一片白，远处有光）
#   形兆问亿泰要去哪里。整片发白的空间，右边远处一团暖白的光，脚下一条淡淡的石子路通过去；四角稍微压灰，光才看得出来。
#   可切换：fade（数字：整片刷白的浓度，过场淡入淡出用）。
DREAM_LIGHT = (234, 102)


def afterlife_dream():
    W, H = 320, 180
    lx, ly = DREAM_LIGHT
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    r = np.sqrt(((xx - lx) / 300) ** 2 + ((yy - ly) / 210) ** 2)
    f = np.clip(1 - r, 0, 1) ** .8
    # 地平线下面稍暗一点、偏暖
    f = np.where(yy > 118, f * .9, f)
    im = new(W, H)
    im = field_paint(im, f, ('#c6cad4', '#d6d8de', '#e4e4e4', '#efede8', '#f7f5ef', '#fcfbf6'))
    # 光：核心 + 十字形的光芒 + 地上的倒影
    core = np.sqrt(((xx - lx) / 14) ** 2 + ((yy - ly) / 12) ** 2)
    rays = np.zeros_like(f)
    ang = np.arctan2(yy - ly, xx - lx)
    dist = np.sqrt((xx - lx) ** 2 + (yy - ly) ** 2)
    for k in range(8):
        a0 = k * math.pi / 4 + .2
        da = np.abs((ang - a0 + math.pi) % (2 * math.pi) - math.pi)
        rays = np.maximum(rays, np.clip(1 - da / .035, 0, 1) * np.clip(1 - dist / (40 if k % 2 else 80), 0, 1) * (k % 2 * .5 + .5))
    refl = np.clip(1 - np.abs(xx - lx) / 5, 0, 1) * np.clip(1 - (yy - 118) / 50, 0, 1) * (yy > 118)
    g = np.clip(np.clip(1 - core, 0, 1) * 1.4 + rays * .32 + refl * .45, 0, 1)
    gq = np.floor(g * 4 + bayer(H, W)) / 4
    a = np.array(im)
    for lv, col in ((.25, '#fff8e4'), (.5, '#fff2c8'), (.75, '#fffbea'), (1.0, '#ffffff')):
        a[gq >= lv, :3] = c3(col)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 地平线（离光越近越淡）
    for x in range(W):
        if abs(x - lx) > 18:
            px(d, x, 118, '#dad8d0' if abs(x - lx) > 60 else '#e8e6de')
    # 石子路：从脚下（160, 176）通到光底下（lx, 120），近大远小
    for i in range(14):
        t = i / 13
        x = 150 + (lx - 150) * (t ** .7)
        y = 176 - (176 - 121) * (t ** .55)
        s = 7 * (1 - t) + 1.5
        ellipse(d, (x - s * 1.6, y - s * .45, x + s * 1.6, y + s * .45), '#d6d2c4')
        ellipse(d, (x - s * 1.4, y - s * .45, x + s * 1.2, y + s * .2), '#e6e2d6')
    # 远处地平线上几块浮着的淡影（像雾里的山）
    for x0, w_, h_ in ((20, 70, 8), (96, 50, 5), (282, 40, 6)):
        for x in range(x0, x0 + w_):
            hh = h_ * math.sin((x - x0) / w_ * math.pi)
            for y in range(int(118 - hh), 118):
                if (x + y) % 2 == 0:
                    px(d, x, y, '#dcdcdc')
    # 浮在空中的光点（12 帧，绕小圈慢慢飘）
    rng = np.random.RandomState(5)
    n = 12
    motes = strip_frames(n, W, H)
    md = ImageDraw.Draw(motes)
    pts = [(rng.uniform(4, W - 4), rng.uniform(20, 170), rng.uniform(2, 5), rng.uniform(0, 6.28), rng.randint(3)) for _ in range(34)]
    for fi in range(n):
        for x, y, rr, ph, ci in pts:
            a_ = ph + 2 * math.pi * fi / n
            X, Y = x + rr * math.cos(a_), y + rr * .6 * math.sin(a_) - 2 * math.sin(2 * math.pi * fi / n)
            b = .5 + .5 * math.sin(ph * 3 + 2 * math.pi * fi / n * 2)
            if b < .2:
                continue
            col = ['#e4d29a', '#c8ccd8', '#f0e2b0'][ci]
            md.point((int(fi * W + X), int(Y)), fill=C(col, 255 if b > .6 else 160))
    # 光的呼吸：核心外面一圈淡金色的环，6 帧一缩一放
    pn, pw = 6, 64
    pulse = strip_frames(pn, pw, pw)
    for fi in range(pn):
        rr = 16 + 5 * math.sin(2 * math.pi * fi / pn)
        yy2, xx2 = np.mgrid[0:pw, 0:pw].astype(float)
        dd = np.sqrt((xx2 - pw / 2) ** 2 + ((yy2 - pw / 2) * 1.15) ** 2)
        ringf = np.clip(1 - np.abs(dd - rr) / 3, 0, 1)
        q = np.floor(ringf * 2 + bayer(pw, pw) - .3) / 2
        arr = np.zeros((pw, pw, 4), np.uint8)
        arr[q > 0, :3] = c3('#f6e6b0')
        arr[q > 0, 3] = 200
        pulse.alpha_composite(Image.fromarray(arr, 'RGBA'), (fi * pw, 0))
    layers = {'base': im, 'motes': motes, 'pulse': pulse}
    K = 'bg/afterlife_dream/'
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(light=[lx, ly], light_floor=[lx, 124], path=[150, 168], keicho=[204, 150], okuyasu=[120, 158],
                             walk_x=[8, 312]),
                layers=[{'type': 'pano', 'image': K + 'base', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'strip', 'image': K + 'pulse', 'n': 6, 'fps': 4, 'k': 1, 'x': lx - pw // 2, 'y': ly - pw // 2},
                        {'type': 'strip', 'image': K + 'motes', 'n': 12, 'fps': 5, 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'tint', 'color': '#ffffff', 'alpha': 1, 'key': 'fade'}],
                fg=[])
    pv = im.copy()
    pv.alpha_composite(pulse.crop((0, 0, pw, pw)), (lx - pw // 2, ly - pw // 2))
    pv.alpha_composite(motes.crop((0, 0, W, H)))
    preview('afterlife_dream', {'room': pv}, ['room'], W)
    save_layers('afterlife_dream', layers, meta)
    return meta


# ============================================================ 别章背景的变体（从那一章画好的图层调色生成）
#   key → (底图 key, 做法, 已经有就直接用、不再生成的同义 key)
VARIANTS = {
    'morning_corner_rain': ('morning_corner', 'rain', ()),                 # 第11章的早上街口 → 雨天（段 A）
    'ghost_alley_cold': ('ghost_alley', 'cold', ()),                       # 第6章的幽灵小路 → 冷色（吉良的最后）
    'ghost_alley_dawn': ('ghost_alley', 'dawn', ()),                       # → 天亮的暖色（铃美升天）
    'morioh_harbor_late': ('morioh_harbor', 'late', ()),                   # 第4章的杜王港 → 夏末（送乔瑟夫和承太郎）
    # 川尻家傍晚不用另做：第8章的 kawajiri_house 自带 key 'dusk'（state.dusk = 1）
}
MODES = {
    'rain': dict(mul=(.62, .66, .76), add=(0, 4, 12), desat=.3, tint=('#203050', .14)),
    'cold': dict(mul=(.78, .86, 1.0), add=(0, 2, 14), desat=.3, tint=('#1a2a48', .14)),
    'dawn': dict(mul=(1.06, .98, .88), add=(20, 10, 0), desat=.05, tint=('#ffb070', .10)),
    'dusk': dict(mul=(1.0, .8, .68), add=(14, 2, 0), desat=.1, tint=('#ff7a3a', .14)),
    'late': dict(mul=(1.04, .98, .88), add=(10, 6, 0), desat=.08, tint=('#ffc080', .08)),
}


def all_bg_meta():
    out = {}
    for fp in sorted(glob.glob(os.path.join(LIB.META, 'bg*.json'))):
        if os.path.basename(fp) == 'bg_fin.json':
            continue
        out.update(LIB.load_json(fp, {}) or {})
    return out


def make_variant(key):
    base, mode, alias = VARIANTS[key]
    metas = all_bg_meta()
    for a in alias:
        if a in metas:
            print(f'  {key}：第{metas[a].get("pack")}包里已经有 {a}，直接用它，不另生成')
            return None
    if base not in metas:
        print(f'  {key}：底图 {base} 还没进仓库（那一章的背景合进来以后再跑一遍），先跳过')
        return None
    M = MODES[mode]
    src = metas[base]
    rng_rain = None
    rename = {}

    def conv(path):
        name = path.split('/')[-1]
        fp = os.path.join(LIB.ASSETS, path + '.png')
        im = Image.open(fp).convert('RGBA')
        im = tint(im, M['mul'], M['add'], desat=M['desat'])
        if mode == 'rain' and im.height == 180 and name in ('near', 'room', 'base'):
            im = rain_ground(im, 150, 180, 17, '#8a96ae')
        out_path = f'bg/{key}/{name}'
        os.makedirs(os.path.join(OUT, key), exist_ok=True)
        im.save(os.path.join(OUT, key, name + '.png'))
        rename[path] = out_path
        return out_path

    def walk(Ls):
        res = []
        for L in Ls:
            L = dict(L)
            if L.get('type') == 'tint' and L.get('key') == 'pm' and mode in ('dusk', 'dawn'):
                continue
            if 'image' in L and str(L['image']).startswith('bg/'):
                L['image'] = conv(L['image'])
            if 'images' in L:
                L['images'] = [conv(p) if str(p).startswith('bg/') else p for p in L['images']]
            res.append(L)
        return res

    meta = dict(src)
    meta['pack'] = PACK
    meta['variantOf'] = base
    meta['layers'] = walk(src.get('layers') or []) + [{'type': 'tint', 'color': M['tint'][0], 'alpha': M['tint'][1]}]
    meta['fg'] = walk(src.get('fg') or [])
    if mode == 'rain':
        rain = rain_strip(320, 180, n=10, near=64, far=48, length=(8, 4), slant=-0.2, cols=('#c8d4e8', '#8e9cb8'), alpha=(190, 130),
                          seed=33)
        splash = splash_strip(320, 34, n=6, count=16, col='#c8d4e8', seed=34)
        rain.save(os.path.join(OUT, key, 'rain.png'))
        splash.save(os.path.join(OUT, key, 'splash.png'))
        meta['fg'] += [{'type': 'strip', 'image': f'bg/{key}/rain', 'n': 10, 'fps': 14, 'screen': True, 'x': 0, 'y': 0, 'w': 320, 'h': 180,
                        'alpha': 0.85},
                       {'type': 'strip', 'image': f'bg/{key}/splash', 'n': 6, 'fps': 12, 'screen': True, 'x': 0, 'y': 142, 'w': 320,
                        'h': 34}]
    print(f'  {key}：从 {base}（{src.get("pack")}）生成 {len(rename)} 层')
    return meta


import glob  # noqa: E402

SCENES = {'empty_house': empty_house, 'residential_street': residential_street, 'afterlife_dream': afterlife_dream}


def main(keys):
    path = os.path.join(LIB.META, 'bg_fin.json')
    meta = LIB.load_json(path, {}) or {}
    for k in keys or (list(SCENES) + list(VARIANTS)):
        if k in SCENES:
            meta[k] = SCENES[k]()
        else:
            r = make_variant(k)
            if r:
                meta[k] = r
            else:
                meta.pop(k, None)
        print('背景', k)
    LIB.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
