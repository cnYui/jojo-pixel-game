# 第四部第3章（海边别墅 / 由花子与意大利菜）的背景：6 张，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   budogaoka_classroom  教室，放学后的斜阳（320）
#   seaside_villa        别墅室内：玄关、楼梯、餐桌、书房和电椅，窗外是海（640）；电椅 / 鞋柜 / 头发封口是可开关的图层
#   seaside_villa_out    别墅区和 48 米外的公用电话亭（640），远景和海岬共用
#   cape_cliff           海岬悬崖和下面的礁石（320），礁石边的浪花是帧条
#   trattoria            意大利餐厅前厅（480）
#   trattoria_kitchen    意大利餐厅后厨（480）：汤锅、烤箱、冰箱、水槽
#   用法：python3 第四部/tools/art/p4_bg_ch3.py [key ...]   元数据写 第四部/assets/_meta/bg_ch3.json（build_p4.py 会合并进 bg）
#         预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import save_layers, preview, liv_floor  # noqa: E402

PACK = 'ch3'
META = os.path.join(LIB.META, 'bg_ch3.json')


def L_pano(key, name, k=1):
    return {'type': 'pano', 'image': f'bg/{key}/{name}', 'k': k, 'x': 0, 'y': 0}


def wood_floor(im, x0, x1, G, tones, seam, grain, seed=5):
    """liv_floor 的换色版：越往下木条越宽"""
    d = ImageDraw.Draw(im)
    y, h, row = G, 3.0, 0
    rng = np.random.RandomState(seed)
    while y < 180:
        yb = min(180, int(round(y + h)))
        rect(d, (x0, int(y), x1, yb - 1), tones[row % len(tones)])
        line(d, (x0, yb - 1, x1, yb - 1), seam)
        plank = int(40 + h * 6)
        off = rng.randint(0, plank)
        for x in range(x0 - off, x1, plank):
            if x > x0:
                line(d, (x, int(y), x, yb - 2), seam)
        for _ in range(int((x1 - x0) / 18)):
            gx = rng.randint(x0, max(x0 + 1, x1 - 6))
            gy = rng.randint(int(y), max(int(y) + 1, yb - 1))
            line(d, (gx, gy, gx + rng.randint(2, 6), gy), grain[row % 2])
        y += h
        h = min(9.0, h * 1.18)
        row += 1
    return im


def tile_floor(im, x0, x1, G, a, b, seam, h0=4.0):
    d = ImageDraw.Draw(im)
    y, h, row = G, h0, 0
    while y < 180:
        yb = min(180, int(round(y + h)))
        tw = int(8 + h * 1.6)
        for i, x in enumerate(range(x0 - (row % 2) * tw // 2, x1, tw)):
            rect(d, (max(x0, x), int(y), min(x1, x + tw - 1), yb - 1), a if (i + row) % 2 else b)
        line(d, (x0, yb - 1, x1, yb - 1), seam)
        y += h
        h = min(10.0, h * 1.2)
        row += 1
    return im


def light_patch(w, h, quads, col, a=255):
    """斜阳 / 窗光：几块平行四边形，单独一张图（glow 图层用 lighter 叠上去）"""
    im = new(w, h)
    d = ImageDraw.Draw(im)
    for q in quads:
        d.polygon(q, fill=C(col, a))
    return im


def soften(im, a_mul):
    a = np.array(im)
    a[..., 3] = (a[..., 3].astype(float) * a_mul).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


# ============================================================ 教室 budogaoka_classroom（320，放学后的斜阳）
#   左：黑板 + 讲台；右：两扇大窗（外面是橙色的天、逆光的树和对面的教学楼）、窗下一排矮柜；
#   前面一排课桌，康一的课桌上有由花子留下的便当（粉色包袱）。地上是窗户投下来的斜光（glow 图层）。
def budogaoka_classroom():
    W, G = 320, 134
    key = 'budogaoka_classroom'
    wall, wall2, wall3 = '#ead6b4', '#dcc49e', '#c8ac84'
    im = new(W, 180, wall)
    im = grad(im, (0, 8, W, G), ('#d8bc94', wall2, wall, '#f0dcb8'))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 6), '#bca482')                                  # 天花板
    line(d, (0, 6, W, 6), '#f4e4c4')
    line(d, (0, 7, W, 7), '#a89070')
    for x in (60, 210):                                               # 日光灯（关着）
        rect(d, (x, 7, x + 44, 9), '#c8c2b4')
        line(d, (x + 2, 10, x + 42, 10), '#eeeae0')
    # ---------------- 黑板（6–122）
    bx0, by0, bx1, by1 = 8, 28, 122, 92
    rect(d, (bx0 - 3, by0 - 3, bx1 + 3, by1 + 3), '#8a6440')
    bevel(d, (bx0 - 3, by0 - 3, bx1 + 3, by1 + 3), '#a8805a', '#5e4228')
    im = grad(im, (bx0, by0, bx1, by1), ('#2a5444', '#2e5a48', '#33604c'))
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(3)
    for _ in range(70):                                               # 没擦干净的粉笔灰
        x, y = rng.randint(bx0 + 2, bx1 - 6), rng.randint(by0 + 2, by1 - 3)
        line(d, (x, y, x + rng.randint(2, 7), y + rng.randint(-1, 2)), '#4a7464')
    chalk = '#e8ece0'
    digits(d, bx1 - 22, by0 + 6, '5', chalk)                          # 右上角：日期 + 值日生
    line(d, (bx1 - 17, by0 + 10, bx1 - 15, by0 + 6), chalk)
    digits(d, bx1 - 13, by0 + 6, '12', chalk)
    for r in range(3):                                                # 值日：两行竖着的“字”
        line(d, (bx1 - 8, by0 + 16 + r * 6, bx1 - 4, by0 + 16 + r * 6), chalk)
        px(d, bx1 - 6, by0 + 18 + r * 6, chalk)
    for r, ln in enumerate((52, 40, 66, 30)):                         # 板书：几行横着的“字”
        y = by0 + 10 + r * 11
        x = bx0 + 8
        while x < bx0 + 8 + ln:
            gw = rng.randint(3, 6)
            if rng.rand() < .8:
                line(d, (x, y + rng.randint(0, 2), x + gw, y + rng.randint(0, 2)), chalk)
                px(d, x + gw // 2, y + 3, chalk)
            x += gw + 2
    ellipse(d, (bx0 + 74, by0 + 33, bx0 + 90, by0 + 49), '#f4d870')   # 黄色粉笔画的圆（例题的图）
    ellipse(d, (bx0 + 75, by0 + 34, bx0 + 89, by0 + 48), '#2e5a48')
    line(d, (bx0 + 82, by0 + 41, bx0 + 89, by0 + 38), '#f4d870')
    # 粉笔槽 + 板擦
    rect(d, (bx0 - 4, by1 + 4, bx1 + 4, by1 + 6), '#8a6440')
    line(d, (bx0 - 4, by1 + 4, bx1 + 4, by1 + 4), '#b08a62')
    rect(d, (bx0 + 20, by1 + 1, bx0 + 31, by1 + 3), '#4a4e6a')
    line(d, (bx0 + 20, by1 + 1, bx0 + 31, by1 + 1), '#8a8eaa')
    for cx, cc in ((bx0 + 44, '#f4f2ea'), (bx0 + 48, '#e86a5a'), (bx0 + 52, '#f4d870')):
        line(d, (cx, by1 + 3, cx + 3, by1 + 3), cc)
    # 黑板上方：班级标语（一张横幅纸）+ 扬声器
    rect(d, (34, 13, 96, 22), '#f6eedc')
    for x in range(38, 92, 7):
        line(d, (x, 16, x + 4, 16), '#3a3a44')
        line(d, (x + 1, 19, x + 3, 19), '#3a3a44')
    rect(d, (106, 12, 118, 22), '#e2d8c4')
    for y in range(14, 21, 2):
        line(d, (108, y, 116, y), '#a49a86')
    # 讲台（教卓）
    rect(d, (42, 108, 82, 112), '#a07a52')
    line(d, (42, 108, 82, 108), '#c49c70')
    rect(d, (45, 112, 79, G - 1), '#8a6440')
    bevel(d, (47, 115, 77, G - 4), '#9c764e', '#6e4e30')
    rect(d, (54, 104, 70, 108), '#f4f0e6')                            # 点名簿
    line(d, (54, 104, 70, 104), '#5a7ac0')
    # ---------------- 窗（132–316）：两大扇
    for wx0 in (134, 228):
        wx1, wy0, wy1 = wx0 + 84, 18, 98
        rect(d, (wx0 - 2, wy0 - 2, wx1 + 2, wy1 + 2), '#cfc8b8')
        im = grad(im, (wx0, wy0, wx1, wy1), ('#e88a62', '#f4a670', '#ffc488', '#ffdca4', '#fff0c8'))
        d = ImageDraw.Draw(im)
        # 太阳：右边那扇低低的
        if wx0 == 228:
            ellipse(d, (282, 42, 300, 60), '#fff2c8')
            ellipse(d, (285, 45, 297, 57), '#fffbe8')
        # 云（被夕阳照成粉橙色）
        cloud(im, wx0 + 6 + (wx0 % 7), 34, 28, seed=wx0, cols=('#ffe0c0', '#f8b896', '#e48c78'))
        d = ImageDraw.Draw(im)
        # 对面那栋教学楼（背光，暗）+ 逆光的树梢
        below = im.crop((wx0 - 2, wy1 + 1, wx1 + 3, 112))           # 树会画出窗外，画完把窗下这块还原
        rect(d, (wx0, 62, wx1, wy1), '#9a7a6a')
        rect(d, (wx0, 60, wx1, 62), '#7e6458')
        for x in range(wx0 + 4, wx1 - 6, 12):
            rect(d, (x, 66, x + 7, 71), '#f4c890')
            rect(d, (x, 77, x + 7, 82), '#d8a47c')
        for k in range(7):
            tx = wx0 + 6 + k * 13 + (k * 5) % 7
            ellipse(d, (tx - 9, 84 - (k % 3) * 3, tx + 9, 108), '#5e5a3a')
            ellipse(d, (tx - 7, 86 - (k % 3) * 3, tx + 3, 94), '#7e7442')
        im.paste(below, (wx0 - 2, wy1 + 1))
        d = ImageDraw.Draw(im)
        # 窗框：中梃 + 横档 + 月牙锁
        mx = (wx0 + wx1) // 2
        rect(d, (mx - 1, wy0, mx + 1, wy1), '#cfc8b8')
        line(d, (mx + 1, wy0, mx + 1, wy1), '#a8a090')
        line(d, (wx0, 58, wx1, 58), '#cfc8b8')
        rect(d, (mx - 2, 76, mx + 2, 78), '#a8a090')
        line(d, (wx0, wy1 + 2, wx1, wy1 + 2), '#a8a090')
        # 窗帘（奶油色，束在两边，被夕阳照透一半）
        for cx0 in (wx0 - 6, wx1 - 5):
            rect(d, (cx0, wy0 - 6, cx0 + 11, wy1 + 4), '#f4dcae')
            for x in range(cx0, cx0 + 11, 3):
                line(d, (x, wy0 - 6, x, wy1 + 4), '#e2c08e')
            rect(d, (cx0, 60, cx0 + 11, 62), '#c89c6a')
    rect(d, (124, 9, W, 11), '#a89070')                               # 窗帘轨
    # ---------------- 窗下矮柜（书包格子）
    rect(d, (130, 104, W, G - 1), '#b89468')
    line(d, (130, 104, W, 104), '#d4b084')
    for i, x in enumerate(range(132, W - 2, 23)):
        for r, y in enumerate((107, 120)):
            rect(d, (x, y, x + 20, y + 10), '#6e5236')
            line(d, (x, y + 10, x + 20, y + 10), '#d4b084')
            if (i * 3 + r) % 4 != 1:                                   # 格子里的书包 / 运动服袋
                col = ['#3a3e5a', '#2e3448', '#7a3a3a', '#3a5a4a'][(i + r) % 4]
                rect(d, (x + 2, y + 3, x + 18, y + 10), col)
                line(d, (x + 2, y + 3, x + 18, y + 3), mix(col, '#ffffff', .3))
    rect(d, (130, G - 3, W, G - 1), '#8a6a48')
    # 后墙下：踢脚线
    rect(d, (0, G - 3, 130, G - 1), '#8a6a48')
    # ---------------- 地板（浅色木地板）
    im = wood_floor(im, 0, W, G, ['#c69a68', '#bc9060', '#cca270', '#c09464'], '#8e6844', ('#a87e52', '#d0a674'), seed=7)
    d = ImageDraw.Draw(im)
    # ---------------- 一排课桌（站在地板最里面）
    def desk(x, y_floor, bag=False, bento=False):
        rect(d, (x, y_floor - 20, x + 26, y_floor - 18), '#d8b480')    # 桌面
        line(d, (x, y_floor - 20, x + 26, y_floor - 20), '#ecd0a0')
        rect(d, (x + 1, y_floor - 17, x + 25, y_floor - 13), '#7a7e86')  # 抽屉框（铁）
        line(d, (x + 1, y_floor - 13, x + 25, y_floor - 13), '#5a5e66')
        for lx in (x + 2, x + 23):
            rect(d, (lx, y_floor - 13, lx + 1, y_floor), '#8a8e96')
        # 椅子（推在桌子下面，露出靠背）
        rect(d, (x + 6, y_floor - 15, x + 20, y_floor - 11), '#c8a272')
        line(d, (x + 6, y_floor - 15, x + 20, y_floor - 15), '#e0bc8a')
        rect(d, (x + 7, y_floor - 10, x + 8, y_floor), '#6a6e76')
        rect(d, (x + 18, y_floor - 10, x + 19, y_floor), '#6a6e76')
        if bag:
            rect(d, (x + 22, y_floor - 12, x + 28, y_floor - 4), '#2e3448')
            line(d, (x + 23, y_floor - 14, x + 27, y_floor - 12), '#2e3448')
        if bento:                                                      # 粉色格子布包着的便当 + 一张小卡片
            rect(d, (x + 7, y_floor - 26, x + 19, y_floor - 21), '#f0a0b8')
            line(d, (x + 7, y_floor - 26, x + 19, y_floor - 26), '#ffd0dc')
            for gx in range(x + 8, x + 19, 3):
                line(d, (gx, y_floor - 25, gx, y_floor - 21), '#e080a0')
            d.polygon([(x + 11, y_floor - 26), (x + 13, y_floor - 30), (x + 15, y_floor - 26)], fill=C('#f0a0b8'))
            d.polygon([(x + 13, y_floor - 30), (x + 10, y_floor - 31), (x + 13, y_floor - 28)], fill=C('#e080a0'))
            d.polygon([(x + 13, y_floor - 30), (x + 16, y_floor - 31), (x + 13, y_floor - 28)], fill=C('#e080a0'))
            rect(d, (x + 19, y_floor - 23, x + 24, y_floor - 21), '#fff6f0')
            px(d, x + 21, y_floor - 22, '#e05a7a')                   # 心
    yf = G + 6
    for i, x in enumerate((96, 136, 176, 216, 256)):
        desk(x, yf, bag=(i in (0, 3)), bento=(i == 2))
    # 桌腿在地板上的影子
    for x in (96, 136, 176, 216, 256):
        im = dither_fill(im, (x + 1, yf, x + 27, yf + 2), '#a07a50', '#b08860', .5)
    d = ImageDraw.Draw(im)
    # 讲台下的教坛（木台阶）
    rect(d, (0, G, 128, G + 4), '#a47a4e')
    line(d, (0, G, 128, G), '#c8a070')
    line(d, (128, G, 128, G + 4), '#7a5634')
    rect(d, (0, G + 5, 128, G + 5), '#8e6844')
    # ---------------- 斜阳：窗户投到墙和地上的光（glow 图层）
    sun = light_patch(W, 180, [
        [(150, 112), (214, 112), (190, 134), (126, 134)],               # 左窗投在矮柜上
        [(244, 112), (316, 112), (292, 134), (220, 134)],
        [(120, 136), (190, 136), (150, 176), (70, 176)],                # 地板上的两块
        [(216, 136), (296, 136), (256, 176), (170, 176)],
        [(70, 30), (92, 30), (60, 92), (38, 92)],                       # 黑板上一道反光
    ], '#ffb060', 255)
    sun = soften(sun, .22)
    motes = {'type': 'petals', 'n': 14, 'colors': ['#fff0c8', '#ffd890'], 'seed': 51, 'y0': 40, 'y1': 70, 'vx': -6,
             'k': 0.1}
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 174],
                anchors=dict(blackboard=[64, 146], podium=[62, 146], desk=[189, 148], bento=[189, 116], window=[176, 146],
                             window2=[270, 146], lockers=[220, 146], door_l=[10, 156], walk_x=[10, 310]),
                layers=[L_pano(key, 'room'),
                        {'type': 'glow', 'image': f'bg/{key}/sun', 'k': 1, 'x': 0, 'y': 0, 'alpha': 1},
                        motes,
                        {'type': 'tint', 'color': '#ff9040', 'alpha': 0.08}], fg=[])
    pv = im.copy()
    a = np.array(pv).astype(int)
    b = np.array(sun).astype(int)
    a[..., :3] = np.clip(a[..., :3] + b[..., :3] * b[..., 3:4] // 255, 0, 255)
    pv = Image.fromarray(a.astype(np.uint8), 'RGBA')
    preview(key, {'room': pv}, ['room'], W)
    return {key: (save_layers(key, {'room': im, 'sun': sun}, meta))}


# ============================================================ 海边：共用的远景（天、海、远处的海岬）
SEA = dict(sky=('#5e9ee4', '#7cb4ec', '#9ccaf2', '#c4e0f6', '#e2f0f8'), sea=('#4a8ac4', '#3e7cb8', '#3470aa', '#2e6498'),
           hl='#a8d4f4', foam='#f4faff', rock=('#5a5048', '#3e3632', '#7a6e62', '#9a8e80'))


def coast_far(w, horizon=98, seed=1, cape=None, clouds=True):
    """天 + 海（到图底）。cape = (x, 宽, 高)：远处伸进海里的岬角剪影（上面一撮松、一座小灯塔）"""
    im = new(w, 180, SEA['sky'][-1])
    im = grad(im, (0, 0, w, horizon), SEA['sky'])
    rng = np.random.RandomState(seed)
    if clouds:
        for i in range(max(2, int(w / 120))):
            cloud(im, rng.randint(0, max(1, w - 50)), rng.randint(16, horizon - 40), rng.randint(30, 64), seed=seed * 10 + i)
    im = grad(im, (0, horizon, w, 180), SEA['sea'])
    d = ImageDraw.Draw(im)
    line(d, (0, horizon, w, horizon), '#8cbce4')
    # 海面的波光：越近越长、越稀
    for y in range(horizon + 2, 180, 3):
        k = (y - horizon) / (180 - horizon)
        step = int(10 + k * 26)
        ln = int(2 + k * 6)
        for x in range(-(y * 7) % step, w, step):
            if rng.rand() < .7:
                line(d, (x, y, x + ln, y), SEA['hl'] if rng.rand() < .7 else '#6aa4d8')
    if cape:
        cx, cw, chh = cape
        pts = [(cx, horizon + 1)]
        for i in range(0, cw + 1, 4):
            t = i / cw
            yy = horizon - chh * (np.sin(min(1, t * 1.6) * np.pi / 2) ** .7) * (1 - max(0, t - .75) * 2.2) - 2 * np.sin(i / 5)
            pts.append((cx + i, int(yy)))
        pts.append((cx + cw, horizon + 1))
        d.polygon(pts, fill=C('#6e8e8a'))
        for (x_, y_) in pts[1:-1]:
            px(d, x_, y_, '#8eaaa4')
        for i in range(5):                                            # 岬顶的松
            tx = cx + cw * .2 + i * cw * .1
            ty = horizon - chh * .95
            ellipse(d, (tx - 4, ty - 4, tx + 4, ty + 1), '#4a6a5e')
        rect(d, (cx + cw * .55, horizon - chh - 9, cx + cw * .55 + 2, horizon - chh + 1), '#f0ece4')
        px(d, cx + cw * .55 + 1, horizon - chh - 10, '#fff0b0')
        for x in range(cx, cx + cw, 3):                               # 岬脚的白浪
            px(d, x + (x // 3) % 2, horizon + 1, SEA['foam'])
    return im


def villa(img, x, ground, w=110, h=78, wall='#f4f0e6', wall2='#d8d2c4', roof=('#3e6a7a', '#2e5462', '#5a8a98', '#1e3a44'),
          shutter='#4a7a8a', door='#7a4a34', seed=0, lit=None, gable=True, chimney=True, bay=True):
    """西式两层别墅：护墙板横纹、坡屋顶 + 山墙、带百叶的窗、门廊和台阶"""
    d = ImageDraw.Draw(img)
    top = ground - h
    rect(d, (x, top, x + w, ground), wall)
    for yy in range(top + 3, ground, 3):                               # 横向的护墙板
        line(d, (x, yy, x + w, yy), mix(wall, wall2, .5))
    rect(d, (x, top, x + 2, ground), wall2)
    rect(d, (x + w - 2, top, x + w, ground), wall2)
    # 屋顶：两坡（侧面）+ 正中一个三角山墙
    rh = 24
    for i in range(rh):
        k = i / rh
        line(d, (x - 6 + (1 - k) * 18, top - rh + i, x + w + 6 - (1 - k) * 18, top - rh + i), roof[0] if i % 3 else roof[1])
    line(d, (x + 12, top - rh, x + w - 12, top - rh), roof[2])
    line(d, (x - 6, top, x + w + 6, top), roof[3])
    if chimney:
        cx_ = x + w - 26
        rect(d, (cx_, top - rh - 10, cx_ + 8, top - rh + 6), '#a86a54')
        rect(d, (cx_ - 1, top - rh - 12, cx_ + 9, top - rh - 10), '#7a4a3a')
    if gable:
        gx = x + w // 2
        d.polygon([(gx - 26, top + 1), (gx, top - rh - 6), (gx + 26, top + 1)], fill=C(roof[1]))
        d.polygon([(gx - 22, top), (gx, top - rh - 2), (gx + 22, top)], fill=C(wall))
        for yy in range(top - rh + 2, top, 3):
            hw = int((yy - (top - rh - 2)) * 22 / (rh + 2))
            line(d, (gx - hw, yy, gx + hw, yy), mix(wall, wall2, .5))
        ellipse(d, (gx - 5, top - 14, gx + 5, top - 4), '#e8e2d4')        # 山墙上的圆窗
        ellipse(d, (gx - 4, top - 13, gx + 4, top - 5), '#8ab4d0' if not lit else lit)
        line(d, (gx, top - 13, gx, top - 5), '#e8e2d4')
    # 二楼的窗（两扇，带百叶）
    for wx in (x + 12, x + w - 34):
        rect(d, (wx - 5, top + 9, wx - 1, top + 29), shutter)
        rect(d, (wx + 23, top + 9, wx + 27, top + 29), shutter)
        for yy in range(top + 10, top + 29, 2):
            line(d, (wx - 5, yy, wx - 1, yy), mix(shutter, '#000000', .25))
            line(d, (wx + 23, yy, wx + 27, yy), mix(shutter, '#000000', .25))
        window(d, (wx, top + 8, wx + 22, top + 30), frame='#fbf8f0', glass=('#8ab4d0', '#c4e0ee'), curtain='#f4ecdc', lit=lit)
        line(d, (wx, top + 19, wx + 22, top + 19), '#fbf8f0')
        rect(d, (wx - 2, top + 31, wx + 24, top + 32), wall2)
    mid = top + 38
    line(d, (x, mid, x + w, mid), wall2)
    # 一楼：凸窗 + 门廊
    if bay:
        bx = x + 8
        rect(d, (bx, mid + 6, bx + 38, ground - 6), wall2)
        for i in range(3):
            window(d, (bx + 2 + i * 12, mid + 8, bx + 12 + i * 12, ground - 12), frame='#fbf8f0', glass=('#7aa6c4', '#b8d6e8'),
                   curtain='#f4ecdc' if i != 1 else None, lit=lit, bars=False)
        rect(d, (bx - 2, mid + 3, bx + 40, mid + 6), roof[1])
        rect(d, (bx - 1, ground - 6, bx + 39, ground - 4), wall2)
    px0 = x + w - 44
    rect(d, (px0 - 4, mid + 2, px0 + 34, mid + 5), roof[1])          # 门廊顶
    line(d, (px0 - 4, mid + 2, px0 + 34, mid + 2), roof[2])
    for cxp in (px0 - 2, px0 + 30):
        rect(d, (cxp, mid + 6, cxp + 2, ground - 4), '#fbf8f0')
    rect(d, (px0 + 6, mid + 10, px0 + 24, ground - 4), door)
    rect(d, (px0 + 8, mid + 12, px0 + 22, ground - 6), mix(door, '#000000', .2))
    rect(d, (px0 + 11, mid + 14, px0 + 19, mid + 20), '#c4dcea')
    px(d, px0 + 20, mid + 28, '#e8c860')
    rect(d, (px0 - 4, ground - 4, px0 + 34, ground - 2), '#c8c2b4')   # 台阶
    rect(d, (px0 - 6, ground - 2, px0 + 36, ground), '#b4ae9e')
    return img


def iron_fence(img, x0, x1, ground, h=14, col='#3a3e44', hi='#6a707a'):
    d = ImageDraw.Draw(img)
    rect(d, (x0, ground - h, x1, ground - h + 1), col)
    rect(d, (x0, ground - 4, x1, ground - 3), col)
    for x in range(x0, x1 + 1, 4):
        line(d, (x, ground - h - 2, x, ground), col)
        px(d, x, ground - h - 3, hi)
    return img


def stone_wall(img, x0, x1, y_top, y_bot, seed=0, cols=('#b8ae9c', '#a0968a', '#d0c8b8', '#8a8274')):
    """乱石矮墙（海边别墅的院墙）"""
    rng = np.random.RandomState(seed)
    d = ImageDraw.Draw(img)
    rect(d, (x0, y_top, x1, y_bot), cols[1])
    y = y_top + 2
    while y < y_bot:
        hh = rng.randint(4, 7)
        x = x0 - rng.randint(0, 8)
        while x < x1:
            ww = rng.randint(6, 13)
            rect(d, (max(x0, x + 1), y, min(x1, x + ww - 1), min(y_bot, y + hh - 1)), cols[0])
            line(d, (max(x0, x + 1), y, min(x1, x + ww - 1), y), cols[2])
            x += ww
        y += hh
    rect(d, (x0, y_top, x1, y_top + 2), cols[2])
    line(d, (x0, y_top + 3, x1, y_top + 3), cols[3])
    return img


# ============================================================ 别墅区 seaside_villa_out（640）
#   左起：松 + 石墙、由花子的别墅（蓝屋顶、门廊、康一被关在二楼）、隔壁的奶油色别墅、护栏和海、48 米外的公用电话亭、又一栋别墅。
def seaside_villa_out():
    W, G = 640, 136
    key = 'seaside_villa_out'
    far = coast_far(480, horizon=100, seed=7, cape=(360, 110, 22))
    near = new(W, 180)
    d = ImageDraw.Draw(near)
    # 院子后面的草坡（只在房子之间露一点，挡住远景的海平线下沿）
    rect(d, (0, G - 26, W, G), '#7a9a5e')
    near = noise_specks(near, (0, G - 26, W, G), ['#8aac6a', '#6a8a52'], 500, 3)
    d = ImageDraw.Draw(near)
    # 左边：松 + 石墙
    for x, h, sd in ((18, 104, 11), (52, 84, 12)):
        near = pine(near, x, G - 4, h, seed=sd)
    near = stone_wall(near, 0, 70, G - 18, G, seed=1)
    # 由花子的别墅（76–206）
    near = villa(near, 80, G - 6, w=120, h=80, roof=('#3e6a7a', '#2e5462', '#5a8a98', '#1e3a44'), shutter='#4a7a8a', seed=1)
    d = ImageDraw.Draw(near)
    # 二楼左窗：拉着窗帘（康一被关在里面），窗台上一盆花
    rect(d, (93, G - 77, 113, G - 57), '#f0d8d8')
    for x in range(93, 114, 3):
        line(d, (x, G - 77, x, G - 57), '#dcbcbc')
    rect(d, (90, G - 54, 116, G - 52), '#c86a5a')
    for k in range(5):
        ellipse(d, (92 + k * 5, G - 58, 96 + k * 5, G - 54), '#e05a7a' if k % 2 else '#f4a0b8')
    near = stone_wall(near, 70, 216, G - 14, G, seed=2)
    near = iron_fence(near, 150, 190, G - 14, h=10)
    d = ImageDraw.Draw(near)
    rect(d, (146, G - 22, 151, G), '#c8c0ae')                          # 门柱 + 门牌
    rect(d, (189, G - 22, 194, G), '#c8c0ae')
    rect(d, (145, G - 24, 152, G - 22), '#e0d8c8')
    rect(d, (188, G - 24, 195, G - 22), '#e0d8c8')
    rect(d, (130, G - 30, 140, G - 20), '#2e5462')                     # 信箱
    rect(d, (131, G - 29, 139, G - 27), '#4a7a8a')
    rect(d, (134, G - 20, 135, G - 14), '#3a3e44')
    # 绣球花丛（院墙外）
    for x0 in (74, 112):
        near = hedge(near, x0, x0 + 26, G - 26, G - 14, seed=x0, cols=('#3a6a4a', '#5a8a5a', '#8ab0d8', '#c4d8f0'))
    # 隔壁：奶油色、红屋顶（224–330）
    near = villa(near, 228, G - 6, w=100, h=70, wall='#f4e6c8', wall2='#dcc8a0', roof=('#a8483a', '#8a3a2e', '#c86a54', '#5e261e'),
                 shutter='#7a8a5a', door='#5a6a4a', seed=2, gable=False, bay=True)
    near = hedge(near, 216, 340, G - 18, G, seed=21)
    d = ImageDraw.Draw(near)
    # 中段：护栏，后面直接是海（远景透出来）
    rect(d, (340, G - 26, 470, G), (0, 0, 0, 0))
    d.rectangle((340, G - 26, 470, G - 1), fill=(0, 0, 0, 0))
    rect(d, (340, G - 8, 470, G), '#8a9a6a')
    near = noise_specks(near, (340, G - 8, 470, G), ['#9aaa76', '#6e7e56'], 120, 4)
    d = ImageDraw.Draw(near)
    rect(d, (340, G - 22, 470, G - 19), '#f0f0ec')
    line(d, (340, G - 22, 470, G - 22), '#ffffff')
    line(d, (340, G - 19, 470, G - 19), '#b8bcc0')
    for x in range(344, 470, 20):
        rect(d, (x, G - 19, x + 2, G - 2), '#d8dcdc')
    near = pine(near, 420, G - 2, 98, seed=14)
    # 公用电话亭（48 米外）+ 旁边一根路牌
    near = phone_booth(near, 504, G + 2)
    d = ImageDraw.Draw(near)
    rect(d, (488, G - 40, 489, G + 2), '#8a8a90')
    rect(d, (478, G - 46, 499, G - 39), '#3a6ab8')
    line(d, (480, G - 43, 496, G - 43), '#e8f0f8')
    # 右边：又一栋别墅（白墙、深绿屋顶）
    near = villa(near, 540, G - 6, w=104, h=76, roof=('#3e5a46', '#2e4636', '#5a7a62', '#1e2e24'), shutter='#a85a4a', door='#4a3a2e',
                 seed=3, chimney=False)
    near = stone_wall(near, 528, W, G - 14, G, seed=3)
    near = pine(near, 530, G - 2, 90, seed=15)
    # 人行道（石板）+ 马路
    near = sidewalk(near, 0, W, G, 152, cols=('#c4bcae', '#aea698', '#d8d0c2', '#9a9284'))
    near = asphalt(near, 0, W, 152, 180)
    for x in (120, 380, 600):
        near = street_lamp(near, x, G + 2, 74)
    near = wires(near, [(-10, 34), (300, 40), (650, 34)], sag=12, col='#3a3e48')
    meta = dict(pack=PACK, w=W, ground=150, walk=[144, 176],
                anchors=dict(villa_door=[176, 146], villa_window=[103, 70], gate=[170, 148], mailbox=[135, 148], sea=[405, 146],
                             booth=[513, 148], sign=[489, 148], start=[24, 160], walk_x=[8, 632]),
                layers=[L_pano(key, 'far', 0.5), L_pano(key, 'near')], fg=[])
    preview(key, {'far': far.resize((W, 180), Image.NEAREST), 'near': near}, ['far', 'near'], W)
    return {key: save_layers(key, {'far': far, 'near': near}, meta)}


def sea_rock(d, x, base, w, h, seed=0, cols=None):
    """海里的礁石：一块不规则的多边形 + 亮面 + 底部白浪"""
    cols = cols or SEA['rock']
    rng = np.random.RandomState(seed)
    pts = [(x, base)]
    n = 6
    for i in range(n + 1):
        t = i / n
        pts.append((x + t * w, base - h * np.sin(np.pi * (0.1 + 0.8 * t)) * rng.uniform(.75, 1.1)))
    pts.append((x + w, base))
    d.polygon([(int(a), int(b)) for a, b in pts], fill=C(cols[0]))
    hl = [(int(a), int(b)) for a, b in pts[1:n // 2 + 2]]
    for (a, b), (a2, b2) in zip(hl, hl[1:]):
        line(d, (a, b, a2, b2), cols[2])
        line(d, (a, b + 1, a2, b2 + 1), cols[3] if (a // 3) % 2 else cols[2])
    line(d, (x + w * .55, base - h * .6, x + w * .7, base - 2), cols[1])
    for xx in range(int(x) - 2, int(x + w) + 3, 2):
        px(d, xx, base + (xx // 2) % 2, SEA['foam'])


def foam_strip(w, h, rocks, n=6, seed=0):
    """礁石脚下的白浪，n 帧循环：每块石头两侧的浪一涨一退"""
    rng = np.random.RandomState(seed)
    out = new(w * n, h)
    d = ImageDraw.Draw(out)
    for f in range(n):
        ph = f / n * 2 * np.pi
        for (rx, ry, rw) in rocks:
            for side in (-1, 1):
                reach = 3 + 3 * (0.5 + 0.5 * np.sin(ph + side))
                for k in range(int(reach)):
                    xx = rx + (rw if side > 0 else 0) + side * k * 2
                    yy = ry - (k % 2)
                    if 0 <= xx < w:
                        d.point((f * w + xx, yy), fill=C(SEA['foam'], 230 - k * 25))
                        if k % 2 == 0 and 0 <= yy + 1 < h:
                            d.point((f * w + xx + 1, yy + 1), fill=C('#c8e4f8', 200))
        for _ in range(10):                                            # 零星的浪花点
            xx, yy = rng.randint(0, w), rng.randint(h // 2, h)
            d.point((f * w + xx, yy), fill=C('#d8ecfa', 180))
    return out


# ============================================================ 海岬 cape_cliff（320）
#   左边草地上一棵被海风吹歪的松，后面一排旧木桩和绳子；右边是悬崖边（塌下去的就是这一块），崖下是礁石和白浪。
def cape_cliff():
    W = 320
    key = 'cape_cliff'
    far = coast_far(W, horizon=74, seed=9, clouds=True)
    d = ImageDraw.Draw(far)
    for x, base, w, h, sd in ((60, 118, 22, 16, 1), (88, 120, 10, 7, 2), (196, 112, 14, 11, 3), (150, 104, 8, 5, 4)):
        sea_rock(d, x, base, w, h, seed=sd)
    near = new(W, 180)
    d = ImageDraw.Draw(near)
    G = 138
    # 悬崖边的轮廓：草地右边在 x≈228（远）到 x≈262（近）之间断掉
    def edge_x(y):
        return int(228 + (y - G) * 0.8 + 3 * np.sin(y / 3.0) + 2 * np.sin(y / 7.1))
    # 崖下：靠崖的海面在阴影里（半透明压暗），礁石在最底下
    sh = new(W, 180)
    sd_ = ImageDraw.Draw(sh)
    for y in range(G, 180):
        ex = edge_x(y)
        sd_.line((ex, y, W, y), fill=C('#0e2a48', int(40 + (y - G) * 2.2)))
    near.alpha_composite(sh)
    d = ImageDraw.Draw(near)
    sea_rock(d, 270, 181, 44, 14, seed=5)
    sea_rock(d, 300, 176, 22, 9, seed=6)
    # 崖面：边线右边一大块往下的岩壁，横向的岩层 + 竖裂缝 + 左亮右暗
    for y in range(G - 2, 180):
        ex = edge_x(y)
        face_w = 16 + int((y - G) * .7)
        for x in range(ex, min(W, ex + face_w)):
            t = (x - ex) / face_w
            col = SEA['rock'][3] if t < .12 else SEA['rock'][2] if t < .4 else SEA['rock'][0] if t < .8 else SEA['rock'][1]
            if (y + int(2 * np.sin(x / 4.0))) % 6 == 0:
                col = mix(col, '#2a2420', .35)
            if (x * 7 + y // 9 * 13) % 23 == 0:
                col = SEA['rock'][1]
            px(d, x, y, col)
    # 草地（带深浅两色的草斑）
    for y in range(G, 180):
        ex = edge_x(y)
        line(d, (0, y, ex - 1, y), '#7ea05a')
    near = grad(near, (0, G, 226, G + 10), ('#8aaa62', '#7ea05a'))
    rng = np.random.RandomState(17)
    for _ in range(26):
        cx, cy = rng.randint(0, 220), rng.randint(G + 4, 178)
        rw = rng.randint(8, 22)
        near = dither_fill(near, (cx, cy, min(edge_x(cy) - 6, cx + rw), cy + rng.randint(2, 4)), '#7ea05a', '#6e9250', .5)
    d = ImageDraw.Draw(near)
    # 草地后沿（远处那条边，略高低起伏）
    for x in range(0, edge_x(G) + 2):
        yy = G - 1 - int(2 * np.sin(x / 11.0) + 1.2 * np.sin(x / 4.3))
        line(d, (x, yy, x, G), '#9ab86e')
        px(d, x, yy, '#b4d084')
    rng = np.random.RandomState(13)
    for _ in range(260):                                               # 草丛和野花
        y = rng.randint(G + 2, 180)
        x = rng.randint(0, max(1, edge_x(y) - 6))
        r = rng.rand()
        if r < .55:
            line(d, (x, y, x - 1, y - 2), '#5e8446')
            line(d, (x + 1, y, x + 2, y - 2), '#6a9050')
        elif r < .75:
            px(d, x, y, '#f4e070'); px(d, x, y - 1, '#5e8446')
        elif r < .85:
            px(d, x, y, '#f4f4f0')
        else:
            px(d, x, y, '#a8c47c')
    # 崖边露出来的一圈岩石（参差的边）
    for y in range(G - 1, 180):
        ex = edge_x(y)
        lip = 2 + int(2 * (0.5 + 0.5 * np.sin(y * 1.7)))
        line(d, (ex - lip, y, ex - 1, y), SEA['rock'][2])
        px(d, ex - lip, y, SEA['rock'][3])
    crack = [(206, 148), (212, 154), (210, 160), (219, 166), (226, 173), (232, 180)]
    for (a, b), (a2, b2) in zip(crack, crack[1:]):
        line(d, (a, b, a2, b2), '#4a5a3a')
    # 被海风吹歪的松（左）
    near = pine(near, 34, G + 2, 92, seed=31)
    d = ImageDraw.Draw(near)
    # 旧木桩 + 绳子的护栏：从左边拉到快到崖边的地方，最后一根歪了
    posts = [(70, G + 1), (110, G + 1), (150, G + 1), (186, G + 1), (214, G + 3)]
    for i, (x, b) in enumerate(posts):
        tilt = 3 if i == len(posts) - 1 else 0
        line(d, (x, b, x + tilt, b - 13), '#7a5a3e', 2)
        px(d, x + tilt, b - 14, '#a07a56')
    for (xa, ba), (xb, bb) in zip(posts, posts[1:]):
        for t in range(0, 41):
            u = t / 40
            x = xa + (xb - xa) * u
            y = (ba - 11) + ((bb - 11) - (ba - 11)) * u + 3 * 4 * u * (1 - u)
            px(d, x, y, '#c8b088')
    # 一块风化的木牌（“小心落石”，字只是几道刻痕）
    rect(d, (122, G - 18, 123, G + 2), '#6a4a32')
    rect(d, (113, G - 24, 132, G - 15), '#a88a62')
    bevel(d, (113, G - 24, 132, G - 15), '#c4a87e', '#7a5e40')
    for x in range(116, 129, 4):
        line(d, (x, G - 21, x + 2, G - 21), '#5a3e2a')
        line(d, (x + 1, G - 18, x + 2, G - 18), '#5a3e2a')
    foam = foam_strip(64, 30, [(14, 30, 44), (44, 25, 22)], n=6, seed=3)
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(edge=[236, 160], edge_far=[226, 146], crack=[216, 164], pine=[34, 150], sign=[122, 148],
                             rocks=[292, 172], sea=[150, 100], start=[40, 160], walk_x=[8, 234]),
                layers=[L_pano(key, 'far', 0), L_pano(key, 'near'),
                        {'type': 'strip', 'image': f'bg/{key}/foam', 'n': 6, 'fps': 5, 'k': 1, 'x': 256, 'y': 150, 'w': 64, 'h': 30}],
                fg=[])
    pv = near.copy()
    pv.alpha_composite(foam.crop((0, 0, 64, 30)), (256, 150))
    preview(key, {'far': far, 'near': pv}, ['far', 'near'], W)
    return {key: save_layers(key, {'far': far, 'near': near, 'foam': foam}, meta)}


# ============================================================ 别墅室内 seaside_villa（640）
#   左起：玄关（双开木门、扇形彩玻璃、伞架、镜子；石砖地）→ 楼梯（扶手是「滋」的陷阱）→ 餐厅（由花子做好的饭、海景窗）
#   → 书房（书架、书桌、墙上的“学习计划表”、落地窗外是海）。
#   电椅、鞋柜是单独的图（第 5 战段 1 要推到门口）；头发封住门 / 楼梯 / 窗和爬满墙的头发是四张可开关的叠加层。
VIL = dict(wall='#f2ede2', wall2='#e6dfd0', wall3='#d6cdb8', beam='#6a4a34', beam2='#8a644a', beam3='#4a3222',
           wain='#8aa4b2', wain_in='#7e98a6', wain_hi='#a8c0cc', wain_lo='#5e7886')


def sea_window(im, box, horizon_k=.55, seed=0, lace=True):
    """窗里的海：天、海平线、波光；窗框白色"""
    x0, y0, x1, y1 = box
    im = grad(im, (x0, y0, x1, y1), ('#7cb4ec', '#9ccaf2', '#c4e0f6'))
    hy = int(y0 + (y1 - y0) * horizon_k)
    im = grad(im, (x0, hy, x1, y1), ('#4a8ac4', '#3e7cb8', '#3470aa'))
    d = ImageDraw.Draw(im)
    line(d, (x0, hy, x1, y1 and hy), '#8cbce4')
    rng = np.random.RandomState(seed)
    for y in range(hy + 2, y1, 3):
        for x in range(x0 + rng.randint(0, 6), x1 - 3, rng.randint(7, 12)):
            line(d, (x, y, x + 2 + (y - hy) // 8, y), '#a8d4f4')
    cloud(im, x0 + 4, y0 + 10, min(30, x1 - x0 - 8), seed=seed + 3)
    return im


def hair_mass(w, h, roots, seed=0, length=(30, 60), dens=1.0, down=True):
    """头发：从 roots（x, y）长出很多根弯弯的发丝，黑色带一点紫的高光"""
    rng = np.random.RandomState(seed)
    im = new(w, h)
    d = ImageDraw.Draw(im)
    for (rx, ry) in roots:
        for _ in range(int(14 * dens)):
            x, y = rx + rng.uniform(-6, 6), ry + rng.uniform(-3, 3)
            ang = (np.pi / 2 if down else rng.uniform(0, 2 * np.pi)) + rng.uniform(-.6, .6)
            L = rng.uniform(*length)
            wob, ph = rng.uniform(.08, .2), rng.uniform(0, 6)
            col = '#1c1418' if rng.rand() < .75 else '#2e2230'
            for i in range(int(L)):
                a = ang + np.sin(i * wob + ph) * .7
                x += np.cos(a)
                y += np.sin(a)
                if 0 <= x < w and 0 <= y < h:
                    d.point((int(x), int(y)), fill=C(col))
                    if i % 9 == 4:
                        d.point((int(x), int(y)), fill=C('#5a4660'))
    return im


def jag_mask(im, seed=0, top_open=True):
    """把一团头发修成参差的轮廓：中心偏上的椭圆 + 噪声边，外面的像素去掉（top_open = 顶边整条保留，像从天花板垂下来）"""
    a = np.array(im)
    h, w = a.shape[:2]
    rng = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    ang = np.arctan2(yy - h * .45, xx - w / 2)
    edge = 1 + .12 * np.sin(ang * 5 + rng.uniform(0, 6)) + .08 * np.sin(ang * 11 + rng.uniform(0, 6))
    v = ((xx - w / 2) / (w * .58)) ** 2 + ((yy - h * .45) / (h * .6)) ** 2
    keep = v < edge ** 2
    if top_open:
        keep |= yy < h * .25
    a[..., 3] = np.where(keep, a[..., 3], 0)
    return Image.fromarray(a, 'RGBA')


def electric_chair():
    """电椅：一把木头扶手椅缠满电线，接一个带拉杆的开关盒（只是喜剧道具，不画束缚带）"""
    im = new(34, 44)
    d = ImageDraw.Draw(im)
    wd, wm, wl = '#5a3a26', '#7a5236', '#9a6e4a'
    rect(d, (6, 2, 26, 26), wm)                                        # 高靠背
    rect(d, (8, 4, 24, 24), wd)
    line(d, (6, 2, 26, 2), wl)
    for x in (11, 16, 21):
        line(d, (x, 5, x, 23), wm)
    rect(d, (3, 26, 29, 30), wl)                                       # 座
    line(d, (3, 26, 29, 26), '#b88a62')
    for x in (2, 27):                                                  # 扶手
        rect(d, (x, 18, x + 3, 21), wl)
        rect(d, (x + 1, 21, x + 2, 26), wm)
    for x in (4, 26):                                                  # 腿
        rect(d, (x, 30, x + 2, 43), wd)
    line(d, (6, 37, 26, 37), wm)
    # 缠在椅子上的电线（灰黑两根绕圈）
    for k, col in enumerate(('#2a2a30', '#5a5a64')):
        for i in range(0, 46):
            t = i / 45
            y = 4 + t * 36
            x = 16 + 11 * np.sin(t * 9 + k * 1.3)
            d.point((int(x), int(y)), fill=C(col))
    # 开关盒（挂在椅背上）+ 拉杆
    rect(d, (24, 8, 32, 16), '#c8a030')
    rect(d, (25, 9, 31, 15), '#e0bc48')
    line(d, (28, 9, 31, 4), '#3a3a40')
    rect(d, (30, 2, 32, 4), '#c83a3a')
    line(d, (32, 16, 33, 43), '#2a2a30')                               # 插头线垂到地上
    return im


def shoe_cabinet():
    im = new(34, 26)
    d = ImageDraw.Draw(im)
    rect(d, (0, 4, 33, 25), '#8a6444')
    line(d, (0, 4, 33, 4), '#b08a62')
    rect(d, (2, 7, 15, 22), '#7a5636')
    rect(d, (18, 7, 31, 22), '#7a5636')
    bevel(d, (2, 7, 15, 22), '#9a7452', '#5e4028')
    bevel(d, (18, 7, 31, 22), '#9a7452', '#5e4028')
    px(d, 14, 14, '#e8c860'); px(d, 19, 14, '#e8c860')
    rect(d, (1, 23, 32, 25), '#5e4028')
    rect(d, (24, 0, 28, 4), '#e8e4f0')                                 # 上面一个小花瓶
    px(d, 26, 0, '#e05a7a')
    return im


def seaside_villa():
    W, G = 640, 134
    key = 'seaside_villa'
    P = VIL
    im = new(W, 180, P['wall'])
    d = ImageDraw.Draw(im)
    # ---------------- 墙：灰泥 + 竖木梁 + 顶上的线脚
    rng = np.random.RandomState(4)
    for _ in range(900):
        x, y = rng.randint(0, W), rng.randint(12, 104)
        px(d, x, y, P['wall2'])
    im = grad(im, (0, 10, W, 24), (P['wall3'], P['wall2'], P['wall']))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 8), P['beam'])
    line(d, (0, 8, W, 8), P['beam2'])
    line(d, (0, 9, W, 9), P['beam3'])
    for x in range(10, W, 64):                                         # 天花板的横梁头
        rect(d, (x, 0, x + 6, 10), P['beam3'])
    # 护墙板（y 104–134，淡蓝灰）
    WT = 104
    rect(d, (0, WT, W, G), P['wain'])
    rect(d, (0, WT, W, WT + 2), P['wain_hi'])
    line(d, (0, WT + 3, W, WT + 3), P['wain_lo'])
    for x in range(2, W, 28):
        rect(d, (x + 2, WT + 7, x + 24, G - 7), P['wain_in'])
        bevel(d, (x + 2, WT + 7, x + 24, G - 7), P['wain_lo'], P['wain_hi'])
    rect(d, (0, G - 4, W, G), P['beam'])
    line(d, (0, G - 4, W, G - 4), P['beam2'])
    for x in (128, 266, 426):                                          # 分区的竖梁
        rect(d, (x, 0, x + 5, G), P['beam'])
        line(d, (x + 1, 0, x + 1, G), P['beam2'])
        line(d, (x + 5, 0, x + 5, G), P['beam3'])
    # ---------------- 玄关（0–128）
    dx0, dx1, dy0 = 30, 84, 46
    rect(d, (dx0 - 5, dy0 - 22, dx1 + 5, G), P['beam'])               # 门套
    d.pieslice((dx0 - 1, dy0 - 22, dx1 + 1, dy0 + 6), 180, 360, fill=C(P['beam3']))
    cx_ = (dx0 + dx1) // 2
    for k, col in enumerate(('#4a7ac0', '#e8c070', '#c0503a', '#e8c070', '#4a7ac0')):   # 扇形彩玻璃：五瓣
        a0 = 180 + k * 36
        d.pieslice((dx0 + 3, dy0 - 18, dx1 - 3, dy0 + 2), a0, a0 + 36, fill=C(col), outline=C(P['beam3']))
    ellipse(d, (cx_ - 5, dy0 - 12, cx_ + 5, dy0 - 2), P['beam3'])
    ellipse(d, (cx_ - 3, dy0 - 10, cx_ + 3, dy0 - 4), '#f4e0a0')
    rect(d, (dx0, dy0 - 8, dx1, dy0 - 6), P['beam3'])
    for lx0, lx1 in ((dx0, cx_ - 1), (cx_ + 1, dx1)):                 # 两扇门
        rect(d, (lx0, dy0 - 5, lx1, G - 1), '#7a4a32')
        for py0, py1 in ((dy0, dy0 + 32), (dy0 + 38, G - 8)):
            rect(d, (lx0 + 4, py0, lx1 - 4, py1), '#6a3e28')
            bevel(d, (lx0 + 4, py0, lx1 - 4, py1), '#5a3220', '#8a5a3e')
        line(d, (lx0, dy0 - 5, lx0, G - 1), '#8a5a3e')
    rect(d, (cx_ - 4, 92, cx_ - 2, 95), '#e8c860')                     # 黄铜把手（被电的那个）
    rect(d, (cx_ + 2, 92, cx_ + 4, 95), '#e8c860')
    px(d, cx_ - 3, 92, '#fff4b0'); px(d, cx_ + 3, 92, '#fff4b0')
    # 伞架 + 两把伞
    rect(d, (8, 112, 20, G - 1), '#4a5a6a')
    line(d, (8, 112, 20, 112), '#6a7a8a')
    line(d, (11, 112, 9, 92), '#c84a5a'); line(d, (12, 112, 10, 92), '#a83a4a')
    line(d, (16, 112, 18, 96), '#3a4a7a'); px(d, 18, 95, '#2a2a30')
    d.arc((5, 88, 12, 95), 180, 360, fill=C('#3a3a40'))
    # 椭圆镜子（鞋柜上方）
    ellipse(d, (98, 40, 120, 74), '#a88a5a')
    ellipse(d, (100, 42, 118, 72), '#c8dce4')
    line(d, (104, 50, 110, 44), '#eef6f8')
    line(d, (104, 54, 113, 45), '#eef6f8')
    # ---------------- 楼梯（134–264）：沿墙往右上爬，扶手 + 白栏杆
    sx0, sy0, sx1, sy1 = 140, G, 258, 28                               # 起点（地面）到终点（二楼）
    steps = 14
    sw, sh = (sx1 - sx0) / steps, (sy0 - sy1) / steps
    # 楼梯下面的三角：储物间的小门
    d.polygon([(sx0 + 10, G), (sx1, sy1 + 10), (sx1, G)], fill=C(P['wall2']))
    rect(d, (200, 94, 226, G - 4), '#7a5a40')
    bevel(d, (200, 94, 226, G - 4), '#9a7a5a', '#5a3e28')
    px(d, 222, 114, '#e8c860')
    # 踏步和踢面
    for i in range(steps):
        x = sx0 + i * sw
        y = sy0 - (i + 1) * sh
        rect(d, (x, y, x + sw + 1, y + sh), '#8a6444')
        line(d, (x, y, x + sw + 1, y), '#b08a62')
        line(d, (x, y + sh, x + sw + 1, y + sh), '#6a4a30')
    # 斜梁（楼梯侧板）
    for k in range(5):
        line(d, (sx0 + 4, G + 1 - k, sx1 + 4, sy1 + 13 - k), P['beam'] if k else P['beam3'])
    # 栏杆
    rail_dy = 22
    for i in range(steps):
        x = int(sx0 + 6 + i * sw)
        yb = int(sy0 - (i + 1) * sh)
        line(d, (x, yb, x, yb - rail_dy + 4), '#f4f0e6')
        px(d, x + 1, yb - 3, '#d8d0c0')
    for k, col in enumerate(('#5a3a26', '#8a5a3e', '#b07a54')):         # 扶手（「滋」会贴在这儿）
        line(d, (sx0 + 2, G - rail_dy - k + 2, sx1 + 6, sy1 - rail_dy + 12 - k), col)
    rect(d, (sx0, G - rail_dy - 6, sx0 + 5, G), '#6a4a30')             # 起步的立柱
    rect(d, (sx0 - 1, G - rail_dy - 9, sx0 + 6, G - rail_dy - 6), '#8a5a3e')
    ellipse(d, (sx0, G - rail_dy - 12, sx0 + 5, G - rail_dy - 8), '#b07a54')
    # 二楼楼板 + 一点点二楼的门洞
    rect(d, (sx1 - 2, 10, 266, sy1 + 2), '#3a2a20')
    rect(d, (sx1 - 2, sy1, 266, sy1 + 3), P['beam'])
    # 墙上：海景油画（楼梯上方）
    fx0, fy0 = 152, 28
    rect(d, (fx0, fy0, fx0 + 40, fy0 + 26), '#a8844a')
    im = sea_window(im, (fx0 + 3, fy0 + 3, fx0 + 37, fy0 + 23), .6, seed=8)
    d = ImageDraw.Draw(im)
    d.polygon([(fx0 + 22, fy0 + 15), (fx0 + 30, fy0 + 15), (fx0 + 27, fy0 + 17), (fx0 + 23, fy0 + 17)], fill=C('#f4f0e6'))
    line(d, (fx0 + 26, fy0 + 9, fx0 + 26, fy0 + 15), '#5a4a3a')
    # ---------------- 餐厅（272–426）
    wx0, wy0, wx1, wy1 = 290, 24, 350, 100
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), '#fbf8f0')
    im = sea_window(im, (wx0, wy0, wx1, wy1), .58, seed=11)
    d = ImageDraw.Draw(im)
    rect(d, (wx0 + 29, wy0, wx0 + 31, wy1), '#fbf8f0')
    line(d, (wx0, 60, wx1, 60), '#fbf8f0')
    for cx0 in (wx0 - 10, wx1 - 2):                                     # 白窗帘
        rect(d, (cx0, wy0 - 8, cx0 + 12, wy1 + 6), '#fbf8f2')
        for x in range(cx0, cx0 + 12, 3):
            line(d, (x, wy0 - 8, x, wy1 + 6), '#e6e0d4')
    rect(d, (wx0 - 14, wy0 - 11, wx1 + 14, wy0 - 9), P['beam'])
    # 餐边柜 + 一瓶玫瑰 + 康一的照片（偷拍的）
    rect(d, (362, 84, 418, 88), '#8a6444')
    line(d, (362, 84, 418, 84), '#b08a62')
    rect(d, (364, 88, 416, WT + 10), '#7a5636')
    for x in (366, 392):
        rect(d, (x, 91, x + 22, 101), '#6a4a30')
        bevel(d, (x, 91, x + 22, 101), '#8a6444', '#4a3222')
    rect(d, (372, 70, 378, 84), '#e8eef4')
    for k, (ox, oy) in enumerate(((-3, -4), (2, -6), (5, -2), (-1, -8), (4, -9))):
        ellipse(d, (375 + ox - 2, 70 + oy - 2, 375 + ox + 2, 70 + oy + 2), '#c8283a' if k % 2 else '#e04050')
    line(d, (374, 70, 372, 64), '#3a6a3a')
    rect(d, (396, 72, 408, 84), '#e8c860')
    rect(d, (397, 73, 407, 83), '#c8d4dc')
    ellipse(d, (399, 75, 405, 80), '#f0d0b0')
    rect(d, (399, 74, 405, 76), '#3a2e2a')
    px(d, 404, 73, '#e05a7a'); px(d, 405, 74, '#e05a7a'); px(d, 403, 74, '#e05a7a')   # 照片角上画了个心
    # 吊灯
    line(d, (346, 10, 346, 26), '#3a3a40')
    d.polygon([(338, 34), (346, 26), (354, 34)], fill=C('#c8a050'))
    line(d, (338, 34, 354, 34), '#8a6a30')
    rect(d, (344, 34, 348, 36), '#fff4c8')
    # ---------------- 书房（432–640）
    # 书架
    rect(d, (436, 20, 490, G - 1), '#6a4a30')
    for i, y in enumerate(range(24, G - 8, 22)):
        rect(d, (440, y, 486, y + 18), '#3e2a1c')
        x = 441
        rr = np.random.RandomState(i)
        while x < 484:
            bw = rr.randint(3, 6)
            bh = rr.randint(12, 18)
            col = ['#a83a3a', '#3a5a8a', '#4a7a4a', '#c8a050', '#e8e0d0', '#6a4a7a', '#2e3a4a'][rr.randint(7)]
            if rr.rand() < .1:
                d.polygon([(x, y + 18), (x + 3, y + 18), (x + 8, y + 18 - bh + 2), (x + 5, y + 18 - bh + 2)], fill=C(col))
                x += 8
                continue
            rect(d, (x, y + 18 - bh, min(484, x + bw - 1), y + 18), col)
            line(d, (x, y + 18 - bh, x, y + 18), mix(col, '#ffffff', .25))
            x += bw
        rect(d, (438, y + 18, 488, y + 20), '#8a6444')
    # 墙上的“学习计划表”（一张大纸，格子 + 一圈圈红心 + 康一的大头照）
    px0, py0 = 500, 40
    rect(d, (px0, py0, px0 + 58, py0 + 40), '#fffaf2')
    rect(d, (px0, py0, px0 + 58, py0 + 6), '#f4a0b8')
    for x in range(px0 + 4, px0 + 54, 7):
        line(d, (x, py0 + 2, x + 4, py0 + 2), '#c8506a')
    for r in range(4):
        for c in range(6):
            x, y = px0 + 3 + c * 9, py0 + 9 + r * 7
            rect(d, (x, y, x + 7, y + 5), '#f0e8dc')
            line(d, (x + 1, y + 2, x + 5, y + 2), '#8a8aa0')
            if (r * 6 + c) % 5 == 2:
                px(d, x + 6, y + 1, '#e05a7a')
    rect(d, (px0 + 44, py0 + 8, px0 + 55, py0 + 22), '#c8d4dc')
    ellipse(d, (px0 + 46, py0 + 11, px0 + 53, py0 + 18), '#f0d0b0')
    rect(d, (px0 + 46, py0 + 10, px0 + 53, py0 + 12), '#3a2e2a')
    for k in range(10):                                                 # 照片周围画了一圈心
        a = k / 10 * 2 * np.pi
        px(d, px0 + 49.5 + 8 * np.cos(a), py0 + 15 + 9 * np.sin(a), '#e05a7a')
    for x in (px0 + 1, px0 + 57):
        px(d, x, py0 + 1, '#c84a3a')
    # 书桌 + 台灯 + 一摞习题集
    rect(d, (498, 104, 572, 108), '#8a5a3e')
    line(d, (498, 104, 572, 104), '#b07a54')
    rect(d, (500, 108, 520, G - 1), '#6a4a30')
    bevel(d, (502, 111, 518, G - 4), '#7a5636', '#4a3222')
    rect(d, (566, 108, 570, G - 1), '#6a4a30')
    rect(d, (504, 92, 508, 104), '#3a5a3a')                            # 绿色台灯
    d.polygon([(500, 92), (512, 92), (510, 86), (502, 86)], fill=C('#2e6a46'))
    line(d, (502, 86, 510, 86), '#4a8a5e')
    rect(d, (500, 102, 512, 104), '#c8a050')
    for k, col in enumerate(('#e8e0d0', '#4a7ac0', '#e8e0d0', '#c84a3a', '#e8e0d0', '#f0c040')):   # 习题集一摞
        rect(d, (526 + k % 2, 103 - k * 2, 548 - k % 2, 104 - k * 2), col)
    rect(d, (554, 98, 560, 104), '#e8e4dc')                            # 笔筒
    line(d, (555, 98, 554, 92), '#e05a5a'); line(d, (557, 98, 558, 93), '#4a7ac0'); line(d, (559, 98, 561, 94), '#3a3a40')
    # 落地窗（580–636）：外面是海
    wx0, wy0, wx1, wy1 = 582, 20, 632, G - 6
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 2), '#fbf8f0')
    im = sea_window(im, (wx0, wy0, wx1, wy1), .5, seed=14)
    d = ImageDraw.Draw(im)
    rect(d, (wx0 + 24, wy0, wx0 + 26, wy1), '#fbf8f0')
    for y in (54, 92):
        line(d, (wx0, y, wx1, y), '#fbf8f0')
    rect(d, (wx0 + 20, 70, wx0 + 22, 76), '#c8a050')
    # 阳台栏杆（窗外）
    for x in range(wx0, wx1, 4):
        line(d, (x, wy1 - 14, x, wy1), '#f4f0e6')
    line(d, (wx0, wy1 - 15, wx1, wy1 - 15), '#e0dad0')
    for cx0 in (wx0 - 10, wx1 - 4):                                     # 蕾丝窗帘
        rect(d, (cx0, wy0 - 8, cx0 + 12, wy1 + 2), '#fbf8f2')
        for y in range(wy0 - 6, wy1, 4):
            for x in range(cx0 + (y // 4) % 2, cx0 + 12, 3):
                px(d, x, y, '#e6e0d4')
    rect(d, (wx0 - 14, wy0 - 11, W, wy0 - 9), P['beam'])
    # ---------------- 地板：玄关石砖，屋里深色木地板
    im = tile_floor(im, 0, 128, G, '#c8c0b0', '#b4ac9c', '#9a9284')
    im = wood_floor(im, 129, W, G, ['#7a5232', '#6e4a2c', '#845a38', '#724c2e'], '#4e321e', ('#62422a', '#8e6640'), seed=9)
    d = ImageDraw.Draw(im)
    rect(d, (128, G, 130, 180), '#8a6444')                             # 玄关到地板的那一级台阶
    line(d, (131, G, 131, 180), '#b08a62')
    # 门口的地垫
    rect(d, (34, 146, 80, 156), '#7a3a3a')
    rect(d, (36, 148, 78, 154), '#9a4a46')
    for x in range(38, 78, 4):
        px(d, x, 151, '#c8a050')
    # 餐桌 + 两把椅子 + 由花子做好的饭
    tx0, tx1, tt = 292, 404, 112
    for cxp in (280, 406):                                              # 两头的高背椅
        rect(d, (cxp, 92, cxp + 4, G + 6), '#5a3a26')
        rect(d, (cxp + (5 if cxp < 300 else -9), 118, cxp + (13 if cxp < 300 else -1), 121), '#7a5236')
        rect(d, (cxp + (12 if cxp < 300 else -9), 121, cxp + (13 if cxp < 300 else -8), G + 6), '#5a3a26')
        for yy in range(96, 116, 5):
            line(d, (cxp, yy, cxp + 4, yy), '#7a5236')
    rect(d, (tx0, tt, tx1, tt + 2), '#fbf8f2')                          # 白桌布
    rect(d, (tx0 - 2, tt + 2, tx1 + 2, tt + 16), '#f4f0e6')
    for x in range(tx0, tx1, 8):
        line(d, (x, tt + 4, x, tt + 16), '#e2dccc')
        d.arc((x - 2, tt + 14, x + 6, tt + 18), 0, 180, fill=C('#e2dccc'))
    rect(d, (tx0 + 6, tt + 16, tx0 + 9, G + 6), '#5a3a26')
    rect(d, (tx1 - 9, tt + 16, tx1 - 6, G + 6), '#5a3a26')
    for px_, food in ((312, '#a85a32'), (382, '#a85a32')):               # 汉堡肉 + 配菜
        ellipse(d, (px_ - 9, tt - 3, px_ + 9, tt + 1), '#ffffff')
        ellipse(d, (px_ - 5, tt - 5, px_ + 3, tt - 1), food)
        px(d, px_ + 4, tt - 2, '#4a9a4a'); px(d, px_ + 5, tt - 3, '#e8a030')
    ellipse(d, (338, tt - 7, 352, tt + 1), '#f4f0e6')                   # 汤碗
    ellipse(d, (340, tt - 6, 350, tt - 2), '#e8c070')
    for cxp in (330, 362):                                              # 烛台
        rect(d, (cxp, tt - 14, cxp + 1, tt), '#f4f0e6')
        rect(d, (cxp - 2, tt - 1, cxp + 3, tt), '#c8a050')
        px(d, cxp, tt - 16, '#ffd060'); px(d, cxp, tt - 15, '#ff9a30')
    for gx in (324, 370):                                               # 杯子（橙汁）
        rect(d, (gx, tt - 6, gx + 3, tt), '#f0a040')
        line(d, (gx, tt - 7, gx + 3, tt - 7), '#e8f0f4')
    # 家具影子
    im = dither_fill(im, (tx0, G + 6, tx1, G + 9), '#5e3e24', '#6e4a2c', .5)
    im = dither_fill(im, (496, G, 574, G + 3), '#5e3e24', '#6e4a2c', .5)
    # ---------------- 可开关的图层：电椅、鞋柜、头发
    chair, cab = electric_chair(), shoe_cabinet()
    hd = hair_mass(76, 110, [(x, 0) for x in range(0, 76, 6)] + [(0, y) for y in range(0, 110, 12)] + [(75, y) for y in range(0, 110, 12)],
                   seed=1, length=(40, 100), dens=1.4)
    hd = jag_mask(hd, seed=1)
    hs = hair_mass(140, 120, [(x, int(110 - x * .78)) for x in range(0, 140, 6)], seed=2, length=(24, 60), dens=1.3, down=False)
    hw = hair_mass(66, 124, [(x, 0) for x in range(0, 66, 5)] + [(0, y) for y in range(0, 124, 10)], seed=3, length=(40, 110), dens=1.4)
    hw = jag_mask(hw, seed=3)
    hall = hair_mass(W, 70, [(x, 0) for x in range(0, W, 9)], seed=4, length=(14, 50), dens=.9)
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(door=[57, 148], knob=[57, 93], umbrella=[14, 148], mirror=[109, 58], shoebox=[107, 148],
                             stairs=[150, 148], stairs_top=[250, 40], handrail=[200, 92], closet=[213, 148], painting=[172, 41],
                             table=[348, 150], dinner=[348, 108], window_dining=[320, 62], sideboard=[390, 148], photo=[402, 78],
                             bookshelf=[463, 148], desk=[535, 148], schedule=[529, 60], chair=[535, 150], window=[607, 148],
                             walk_x=[8, 632]),
                layers=[L_pano(key, 'room'),
                        {'type': 'image', 'image': f'bg/{key}/shoebox', 'k': 1, 'x': 90, 'y': G - 26 + 4, 'key': 'shoebox'},
                        {'type': 'image', 'image': f'bg/{key}/chair', 'k': 1, 'x': 518, 'y': G + 6 - 44, 'key': 'chair'},
                        {'type': 'image', 'image': f'bg/{key}/hair_walls', 'k': 1, 'x': 0, 'y': 8, 'key': 'hair_walls'},
                        {'type': 'image', 'image': f'bg/{key}/hair_door', 'k': 1, 'x': 20, 'y': 24, 'key': 'hair_door'},
                        {'type': 'image', 'image': f'bg/{key}/hair_stairs', 'k': 1, 'x': 132, 'y': 14, 'key': 'hair_stairs'},
                        {'type': 'image', 'image': f'bg/{key}/hair_window', 'k': 1, 'x': 574, 'y': 12, 'key': 'hair_window'}],
                fg=[])
    pv = im.copy()
    pv.alpha_composite(cab, (90, G - 22))
    pv.alpha_composite(chair, (518, G + 6 - 44))
    preview(key, {'room': pv}, ['room'], W)
    pv2 = pv.copy()
    for img_, xy in ((hall, (0, 8)), (hd, (20, 24)), (hs, (132, 14)), (hw, (574, 12))):
        pv2.alpha_composite(img_, xy)
    pv2.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'preview', 'bg_seaside_villa_hair.png'))
    return {key: save_layers(key, {'room': im, 'chair': chair, 'shoebox': cab, 'hair_door': hd, 'hair_stairs': hs, 'hair_window': hw,
                                   'hair_walls': hall}, meta)}


# ============================================================ 意大利餐厅 trattoria（前厅 480）/ trattoria_kitchen（后厨 480）
TR = dict(wall='#ecc88e', wall2='#e0b87a', wall3='#c89a5e', brick='#b8644a', brick2='#9a4e3a', brick3='#d4846a',
          beam='#5a3a26', beam2='#7a5236', beam3='#3e2618', wain='#3e5a44', wain_hi='#5a7a5e', wain_lo='#2a4030')


def plaster_wall(im, x0, x1, y0, y1, seed=0):
    """暖黄色灰泥墙 + 几块剥落露出的砖"""
    d = ImageDraw.Draw(im)
    rect(d, (x0, y0, x1, y1), TR['wall'])
    rng = np.random.RandomState(seed)
    for _ in range(int((x1 - x0) * (y1 - y0) / 40)):
        px(d, rng.randint(x0, x1), rng.randint(y0, y1), TR['wall2'])
    for _ in range(int((x1 - x0) / 110) + 1):
        bx, by = rng.randint(x0 + 10, x1 - 40), rng.randint(y0 + 30, y1 - 30)
        bw, bh = rng.randint(22, 36), rng.randint(12, 18)
        d.polygon([(bx, by + 2), (bx + 4, by - 1), (bx + bw - 3, by), (bx + bw, by + bh - 3), (bx + bw - 6, by + bh), (bx + 2, by + bh - 1)],
                  fill=C(TR['brick2']))
        for r, yy in enumerate(range(by + 1, by + bh - 1, 4)):
            for xx in range(bx + 2 + (r % 2) * 4, bx + bw - 3, 8):
                rect(d, (xx, yy, xx + 6, yy + 2), TR['brick'])
                line(d, (xx, yy, xx + 6, yy), TR['brick3'])
    return im


def checker_cloth(d, x0, x1, y_top, drop=14):
    """红白格子桌布（桌面 + 垂下来的一截）"""
    rect(d, (x0, y_top, x1, y_top + 2), '#f4f0e6')
    for yy in range(y_top + 3, y_top + drop):
        for xx in range(x0 - 2, x1 + 3):
            c = ((xx - x0) // 4 + (yy - y_top) // 4) % 2
            px(d, xx, yy, '#d8403a' if c else '#f4f0e6')
    line(d, (x0 - 2, y_top + drop, x1 + 2, y_top + drop), '#a83030')


def bentwood_chair(d, x, floor, face=1):
    """维也纳曲木椅（侧面）：face=1 椅背在左，-1 在右"""
    bx = x if face > 0 else x + 12
    rect(d, (bx, floor - 30, bx + 1, floor), '#4a2e1c')
    d.arc((bx - 4 if face > 0 else bx - 2, floor - 34, bx + 6 if face > 0 else bx + 8, floor - 24), 180, 360, fill=C('#4a2e1c'))
    rect(d, (x, floor - 14, x + 13, floor - 12), '#6a4228')
    line(d, (x, floor - 14, x + 13, floor - 14), '#8a5a3a')
    line(d, (x + (12 if face > 0 else 1), floor - 12, x + (12 if face > 0 else 1), floor), '#4a2e1c')
    d.arc((x + 2, floor - 8, x + 11, floor - 2), 0, 180, fill=C('#4a2e1c'))


def chianti(d, x, y):
    """草编瓶身的基安蒂酒瓶 + 插着的蜡烛"""
    ellipse(d, (x - 4, y - 8, x + 4, y), '#d8b060')
    for yy in range(y - 7, y, 2):
        line(d, (x - 3, yy, x + 3, yy), '#b08a40')
    rect(d, (x - 1, y - 14, x + 1, y - 8), '#3a6a3a')
    rect(d, (x - 1, y - 20, x, y - 14), '#f4f0e6')
    line(d, (x - 2, y - 15, x - 2, y - 12), '#f4f0e6')
    px(d, x, y - 22, '#ffd060'); px(d, x, y - 21, '#ff9a30')


def hanging_string(d, x, y0, n, col, col2, step=4, r=2):
    """挂着的一串大蒜 / 辣椒"""
    line(d, (x, y0, x, y0 + n * step), '#a08a5a')
    for i in range(n):
        yy = y0 + 3 + i * step
        ellipse(d, (x - r - (i % 2), yy - r, x + r - (i % 2), yy + r), col)
        px(d, x - (i % 2), yy - 1, col2)


def lamp_glow_img(w, h, spots, col='#ffb860'):
    """几盏吊灯 / 烛光的光晕，单独一张（glow 图层）"""
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    acc = np.zeros((h, w))
    for (cx, cy, r, k) in spots:
        v = 1 - np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.3) ** 2) / r
        acc += np.clip(v, 0, 1) ** 1.6 * k
    acc = np.clip(acc, 0, 1)
    lv = np.floor(acc * 5) / 5                                            # 分 5 档，带一点抖动，像素风的光晕
    th = BAYER[yy % 4, xx % 4] * .2
    lv = np.where(acc * 5 % 1 > th * 5, lv + .2, lv) * (acc > .02)
    cr = c3(col)
    a[..., 0], a[..., 1], a[..., 2] = cr
    a[..., 3] = np.clip(lv * 120, 0, 255).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def trattoria():
    W, G = 480, 134
    key = 'trattoria'
    P = TR
    im = new(W, 180, P['wall'])
    im = plaster_wall(im, 0, W, 10, 104, seed=5)
    d = ImageDraw.Draw(im)
    # 天花板的木梁
    rect(d, (0, 0, W, 9), P['beam'])
    line(d, (0, 9, W, 9), P['beam3'])
    for x in range(20, W, 70):
        rect(d, (x, 0, x + 8, 12), P['beam3'])
        line(d, (x, 0, x, 12), P['beam2'])
    # 护墙板（深绿）
    WT = 104
    rect(d, (0, WT, W, G), P['wain'])
    rect(d, (0, WT, W, WT + 2), '#c8a050')
    for x in range(4, W, 26):
        bevel(d, (x, WT + 6, x + 20, G - 6), P['wain_lo'], P['wain_hi'])
    rect(d, (0, G - 3, W, G), P['beam'])
    # ---------------- 左：店门（玻璃门 + 门上挂的小牌）+ 临街的窗
    dx0, dx1 = 14, 50
    rect(d, (dx0 - 3, 36, dx1 + 3, G), P['beam'])
    rect(d, (dx0, 39, dx1, G - 1), '#6a4228')
    im = grad(im, (dx0 + 4, 44, dx1 - 4, 100), ('#e8a870', '#f4c890', '#c8b8a0'))
    d = ImageDraw.Draw(im)
    for xx in range(dx0 + 4, dx1 - 4, 5):                               # 街对面的房子（反着看）
        rect(d, (xx, 80 - (xx % 3) * 4, xx + 4, 100), '#b89a7a')
    line(d, (dx0 + 6, 46, dx0 + 12, 52), '#fff4dc')
    rect(d, (dx1 - 6, 104, dx1 - 4, 110), '#c8a050')
    line(d, (dx0 + 18, 50, dx0 + 14, 56), '#a08a5a'); line(d, (dx0 + 18, 50, dx0 + 22, 56), '#a08a5a')
    rect(d, (dx0 + 10, 56, dx0 + 26, 63), '#f4f0e6')                    # 挂牌（字只是两道）
    line(d, (dx0 + 12, 59, dx0 + 24, 59), '#3e5a44')
    px(d, dx0 + 18, 61, '#d8403a')
    # 店门上方的小窗帘杆 + 三色短帘
    for k, col in enumerate(('#3e8a4a', '#f4f0e6', '#d8403a')):
        rect(d, (dx0 + k * 12, 38, dx0 + k * 12 + 11, 44), col)
    # 窗（60–120）
    wx0, wy0, wx1, wy1 = 62, 30, 122, 92
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), P['beam'])
    im = grad(im, (wx0, wy0, wx1, wy1), ('#e8a870', '#f4c890', '#f8dcae'))
    d = ImageDraw.Draw(im)
    for xx in range(wx0, wx1, 12):
        h_ = 26 + (xx * 7) % 14
        rect(d, (xx, wy1 - h_, xx + 10, wy1), '#c4a07e')
        rect(d, (xx + 2, wy1 - h_ + 4, xx + 5, wy1 - h_ + 8), '#ffe4a8')
        d.polygon([(xx - 1, wy1 - h_), (xx + 5, wy1 - h_ - 5), (xx + 11, wy1 - h_)], fill=C('#9a6a50'))
    rect(d, (wx0 + 29, wy0, wx0 + 31, wy1), P['beam'])
    line(d, (wx0, wy0 + 30, wx1, wy0 + 30), P['beam'])
    rect(d, (wx0 - 2, wy0, wx1 + 2, wy0 + 12), '#f4f0e6')               # 白色半截窗帘（蕾丝边）
    for xx in range(wx0 - 2, wx1 + 3, 3):
        px(d, xx, wy0 + 13, '#f4f0e6')
    for xx in range(wx0 + 4, wx1, 10):                                   # 窗台上的小罗勒盆
        pass
    rect(d, (wx0 - 6, wy1 + 3, wx1 + 6, wy1 + 6), P['beam2'])
    for k, xx in enumerate((wx0 + 8, wx0 + 26, wx0 + 44)):
        rect(d, (xx, wy1 - 2, xx + 7, wy1 + 3), '#c06a4a')
        for j in range(4):
            ellipse(d, (xx - 1 + j * 2, wy1 - 7 + (j % 2) * 2, xx + 3 + j * 2, wy1 - 2), '#4a8a3a' if j % 2 else '#6aaa4a')
    # ---------------- 墙上：黑板菜单、意大利风景画、挂着的大蒜和辣椒、酒架
    mx0, my0 = 146, 26
    rect(d, (mx0 - 3, my0 - 3, mx0 + 47, my0 + 55), P['beam2'])
    rect(d, (mx0, my0, mx0 + 44, my0 + 52), '#2e3430')
    rng = np.random.RandomState(9)
    line(d, (mx0 + 10, my0 + 5, mx0 + 34, my0 + 5), '#f4f0e6')         # 菜单标题
    line(d, (mx0 + 12, my0 + 7, mx0 + 32, my0 + 7), '#f4d870')
    for r in range(6):
        y = my0 + 13 + r * 6
        line(d, (mx0 + 4, y, mx0 + 4 + rng.randint(18, 28), y), '#e8ece0')
        for xx in range(mx0 + 34, mx0 + 41, 2):
            px(d, xx, y, '#e8ece0')
    px(d, mx0 + 4, my0 + 47, '#d8403a'); px(d, mx0 + 6, my0 + 47, '#f4f0e6'); px(d, mx0 + 8, my0 + 47, '#3e8a4a')
    # 风景画（托斯卡纳的丘陵和柏树）
    fx0, fy0 = 214, 34
    rect(d, (fx0, fy0, fx0 + 44, fy0 + 30), '#c8a050')
    im = grad(im, (fx0 + 3, fy0 + 3, fx0 + 41, fy0 + 27), ('#f4c890', '#f8e0b0'))
    d = ImageDraw.Draw(im)
    d.polygon([(fx0 + 3, fy0 + 20), (fx0 + 14, fy0 + 14), (fx0 + 26, fy0 + 18), (fx0 + 41, fy0 + 12), (fx0 + 41, fy0 + 27), (fx0 + 3, fy0 + 27)],
              fill=C('#9ab05a'))
    d.polygon([(fx0 + 3, fy0 + 24), (fx0 + 20, fy0 + 20), (fx0 + 41, fy0 + 23), (fx0 + 41, fy0 + 27), (fx0 + 3, fy0 + 27)], fill=C('#7a9a4a'))
    for cx_ in (fx0 + 12, fx0 + 16, fx0 + 32):
        ellipse(d, (cx_ - 1, fy0 + 8, cx_ + 2, fy0 + 20), '#3e5a3a')
    rect(d, (fx0 + 22, fy0 + 14, fx0 + 27, fy0 + 18), '#e8d4b0')
    line(d, (fx0 + 21, fy0 + 14, fx0 + 28, fy0 + 14), '#b8644a')
    # 挂着的大蒜和辣椒
    hanging_string(d, 270, 12, 6, '#f4ecdc', '#ffffff', step=5, r=3)
    hanging_string(d, 282, 12, 8, '#d8302a', '#f06a5a', step=4, r=2)
    hanging_string(d, 132, 12, 5, '#f4ecdc', '#ffffff', step=5, r=3)
    # 酒架（300–356）
    rect(d, (300, 28, 356, 100), P['beam2'])
    for r in range(5):
        for c in range(4):
            x, y = 304 + c * 13, 32 + r * 13
            rect(d, (x, y, x + 10, y + 10), P['beam3'])
            if (r + c * 2) % 5:
                ellipse(d, (x + 2, y + 2, x + 8, y + 8), ['#3a5a2a', '#5a1e2a', '#2e3a20'][(r + c) % 3])
                px(d, x + 4, y + 4, '#a8c4a0')
    # ---------------- 右：吧台 + 出菜口 + 通后厨的弹簧门（圆窗）
    rect(d, (362, 50, 412, 76), P['beam'])                              # 出菜口
    rect(d, (365, 53, 409, 74), '#3a2e26')
    rect(d, (370, 58, 404, 74), '#d8d8dc')                              # 后厨里的不锈钢一角
    line(d, (370, 64, 404, 64), '#b8b8c0')
    rect(d, (380, 50, 394, 54), '#c83a2a')                              # 出菜灯
    rect(d, (384, 54, 390, 55), '#fff0b0')
    rect(d, (360, 76, 414, 80), '#8a5a3a')                              # 出菜口的台面 + 一盘等着上的菜
    line(d, (360, 76, 414, 76), '#b07a54')
    ellipse(d, (376, 71, 392, 77), '#ffffff')
    ellipse(d, (379, 70, 389, 75), '#e8a040')
    px(d, 382, 70, '#d8403a'); px(d, 386, 71, '#4a8a3a')
    rect(d, (358, 100, 416, 104), '#8a5a3a')                            # 吧台
    line(d, (358, 100, 416, 100), '#b07a54')
    rect(d, (360, 104, 414, G - 1), P['beam2'])
    for x in range(362, 412, 13):
        bevel(d, (x, 107, x + 10, G - 4), P['beam3'], '#9a6a48')
    rect(d, (366, 92, 370, 100), '#e8e4dc')                             # 收银机旁的小摆设：铃 + 花
    ellipse(d, (396, 94, 402, 100), '#c8a050')
    px(d, 399, 93, '#3a3a40')
    # 弹簧门（424–462）
    kx0, kx1 = 424, 462
    rect(d, (kx0 - 3, 30, kx1 + 3, G), P['beam'])
    for lx0, lx1 in ((kx0, (kx0 + kx1) // 2 - 1), ((kx0 + kx1) // 2 + 1, kx1)):
        rect(d, (lx0, 33, lx1, G - 1), '#8a5a3a')
        bevel(d, (lx0, 33, lx1, G - 1), '#a8784e', '#5a3a26')
        cx_ = (lx0 + lx1) // 2
        ellipse(d, (cx_ - 6, 48, cx_ + 6, 60), '#c8a050')
        ellipse(d, (cx_ - 5, 49, cx_ + 5, 59), '#e8eef0')
        line(d, (cx_ - 3, 52, cx_, 50), '#ffffff')
        rect(d, (lx0 + 3, 96, lx1 - 3, 100), '#c8a050')                 # 推板
    # ---------------- 地板：赤陶砖
    im = tile_floor(im, 0, W, G, '#b8684a', '#a85c40', '#7a3e2a', h0=4.0)
    d = ImageDraw.Draw(im)
    # ---------------- 三张桌子（格子桌布）+ 曲木椅；中间那张是亿泰的（摆着一副餐具和一杯水）
    yf = G + 8
    tables = [(96, False), (206, True), (296, False)]
    for tx, main in tables:
        tw = 44
        bentwood_chair(d, tx - 16, yf, face=1)
        bentwood_chair(d, tx + tw + 3, yf, face=-1)
        rect(d, (tx + tw // 2 - 1, yf - 18, tx + tw // 2 + 1, yf), '#3e2618')
        rect(d, (tx + tw // 2 - 8, yf - 1, tx + tw // 2 + 8, yf), '#3e2618')
        checker_cloth(d, tx, tx + tw, yf - 30, 12)
        chianti(d, tx + tw // 2, yf - 30)
        if main:
            ellipse(d, (tx + 4, yf - 33, tx + 18, yf - 29), '#ffffff')
            line(d, (tx + 2, yf - 32, tx + 2, yf - 30), '#c8ccd2')
            line(d, (tx + 20, yf - 32, tx + 20, yf - 30), '#c8ccd2')
            rect(d, (tx + 30, yf - 36, tx + 33, yf - 30), '#d8eef8')
            line(d, (tx + 30, yf - 37, tx + 33, yf - 37), '#ffffff')
        else:
            ellipse(d, (tx + 6, yf - 34, tx + 16, yf - 30), '#d8b060')    # 面包篮
            px(d, tx + 9, yf - 35, '#f4dca0'); px(d, tx + 12, yf - 35, '#e8c080')
    for tx, _ in tables:
        im = dither_fill(im, (tx - 18, yf, tx + 62, yf + 3), '#8a4a34', '#9a5440', .5)
    d = ImageDraw.Draw(im)
    # 盆栽的橄榄树（门和窗之间）
    tx_ = 56
    line(d, (tx_, 120, tx_ - 1, 84), '#6a5038')
    line(d, (tx_ - 1, 96, tx_ - 6, 88), '#6a5038')
    line(d, (tx_, 92, tx_ + 5, 84), '#6a5038')
    rr = np.random.RandomState(21)
    blobs = [(tx_ + rr.uniform(-10, 10), 82 + rr.uniform(-8, 8), rr.uniform(3, 5)) for _ in range(16)]
    for bx, by, r in blobs:
        ellipse(d, (bx - r, by - r * .8, bx + r, by + r * .8), '#5e6e44')
    for bx, by, r in blobs:
        ellipse(d, (bx - r * .9, by - r * .8, bx + r * .5, by + r * .3), '#7a8a5a')
    for bx, by, r in blobs[:6]:
        ellipse(d, (bx - r * .6, by - r * .7, bx, by - r * .2), '#a4b07a')
    rect(d, (tx_ - 7, 118, tx_ + 7, G + 4), '#c06a4a')
    line(d, (tx_ - 7, 118, tx_ + 7, 118), '#d88a68')
    line(d, (tx_ + 7, 119, tx_ + 7, G + 4), '#9a4e36')
    # ---------------- 吊灯（三盏）+ 光晕
    for lx in (118, 228, 318):
        line(d, (lx, 9, lx, 30), '#2a2a30')
        d.polygon([(lx - 7, 37), (lx, 30), (lx + 7, 37)], fill=C('#3e5a44'))
        line(d, (lx - 7, 37, lx + 7, 37), '#2a4030')
        rect(d, (lx - 2, 37, lx + 2, 38), '#fff4c8')
    glow = lamp_glow_img(W, 180, [(118, 40, 46, .9), (228, 40, 46, .9), (318, 40, 46, .9), (118, 112, 18, .5), (228, 112, 18, .5),
                                  (318, 112, 18, .5), (387, 56, 22, .6)])
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(entrance=[32, 148], window=[92, 60], menu=[168, 52], table=[228, 150], seat=[198, 152], seat2=[268, 152],
                             table_l=[118, 150], table_r=[318, 150], winerack=[328, 146], pass_window=[387, 64], counter=[387, 148],
                             kitchen_door=[443, 148], walk_x=[8, 472]),
                layers=[L_pano(key, 'room'), {'type': 'glow', 'image': f'bg/{key}/glow', 'k': 1, 'x': 0, 'y': 0, 'alpha': .7, 'flicker': .06}],
                fg=[])
    pv = im.copy()
    pv.alpha_composite(soften(glow, .7))
    preview(key, {'room': pv}, ['room'], W)
    return {key: save_layers(key, {'room': im, 'glow': glow}, meta)}


def steam_strip(w, h, n=8, puffs=6, seed=0, col='#ffffff'):
    """锅里冒的蒸汽：一团团往上飘、变大、变淡，n 帧循环"""
    rng = np.random.RandomState(seed)
    out = new(w * n, h)
    d = ImageDraw.Draw(out)
    P_ = [(rng.uniform(w * .3, w * .7), rng.uniform(0, 1)) for _ in range(puffs)]
    for f in range(n):
        for (x0, ph) in P_:
            u = (ph + f / n) % 1
            y = h - 2 - u * (h - 4)
            x = x0 + np.sin(u * 6 + ph * 6) * 3
            r = 1.5 + u * 3.5
            a = int(170 * (1 - u))
            d.ellipse((f * w + x - r, y - r, f * w + x + r, y + r), fill=C(col, a))
    return out


def fire_strip(w, h, n=6, seed=0):
    """烤炉口里的火：三层颜色的火舌高低起伏"""
    rng = np.random.RandomState(seed)
    out = new(w * n, h)
    d = ImageDraw.Draw(out)
    tongues = [(rng.uniform(2, w - 2), rng.uniform(0, 6.28), rng.uniform(.6, 1)) for _ in range(7)]
    for f in range(n):
        for (x, ph, s) in tongues:
            hh = h * s * (0.55 + 0.45 * np.sin(ph + f / n * 2 * np.pi))
            for k, (col, sc) in enumerate((('#c8301e', 1), ('#f07a28', .7), ('#ffd060', .4))):
                ht = hh * sc
                d.polygon([(f * w + x - 3 * sc - 1, h), (f * w + x, h - ht), (f * w + x + 3 * sc + 1, h)], fill=C(col))
    return out


def trattoria_kitchen():
    W, G = 480, 134
    key = 'trattoria_kitchen'
    im = new(W, 180, '#f4f2ec')
    d = ImageDraw.Draw(im)
    # 白瓷砖墙 + 一圈绿色腰线
    for y in range(10, G, 6):
        for x in range(((y // 6) % 2) * 3, W, 6):
            rect(d, (x, y, x + 5, y + 5), '#f4f2ec')
            line(d, (x, y + 5, x + 5, y + 5), '#d6d2c8')
            line(d, (x + 5, y, x + 5, y + 5), '#d6d2c8')
    rect(d, (0, 64, W, 67), '#3e8a5a')
    line(d, (0, 64, W, 64), '#5aaa72')
    rect(d, (0, 0, W, 9), '#c8c4b8')
    line(d, (0, 9, W, 9), '#a8a498')
    for x in (100, 260, 420):                                            # 日光灯
        rect(d, (x, 9, x + 40, 12), '#e8e8ec')
        line(d, (x + 2, 13, x + 38, 13), '#ffffff')
    # ---------------- 左：回前厅的弹簧门
    kx0, kx1 = 6, 42
    rect(d, (kx0 - 3, 30, kx1 + 3, G), TR['beam'])
    for lx0, lx1 in ((kx0, (kx0 + kx1) // 2 - 1), ((kx0 + kx1) // 2 + 1, kx1)):
        rect(d, (lx0, 33, lx1, G - 1), '#8a5a3a')
        bevel(d, (lx0, 33, lx1, G - 1), '#a8784e', '#5a3a26')
        cx_ = (lx0 + lx1) // 2
        ellipse(d, (cx_ - 6, 48, cx_ + 6, 60), '#c8a050')
        ellipse(d, (cx_ - 5, 49, cx_ + 5, 59), '#f4c890')
        rect(d, (lx0 + 3, 96, lx1 - 3, 100), '#c8a050')
    # ---------------- 洗手池（56–104）：水龙头、肥皂、毛巾，上面贴着“先洗手”的标识
    sx0, sx1 = 56, 104
    rect(d, (sx0, 96, sx1, 100), '#c8ccd2')
    line(d, (sx0, 96, sx1, 96), '#eef0f4')
    rect(d, (sx0 + 6, 97, sx1 - 6, 99), '#7a7e86')
    rect(d, (sx0 + 2, 100, sx1 - 2, 118), '#b8bcc4')
    line(d, (sx0 + 2, 118, sx1 - 2, 118), '#8a8e96')
    for lx in (sx0 + 4, sx1 - 6):
        rect(d, (lx, 118, lx + 2, G - 1), '#9a9ea6')
    rect(d, (79, 80, 81, 96), '#d8dce2')                                 # 鹅颈龙头
    d.arc((79, 76, 89, 86), 180, 360, fill=C('#d8dce2'))
    rect(d, (88, 81, 89, 84), '#d8dce2')
    rect(d, (74, 90, 77, 92), '#c83a3a'); rect(d, (83, 90, 86, 92), '#3a6ac8')
    rect(d, (60, 90, 66, 96), '#f4f0e6')                                 # 肥皂液瓶
    rect(d, (62, 87, 64, 90), '#3e8a5a')
    rect(d, (92, 100, 102, 116), '#f4f0e6')                              # 挂着的毛巾
    line(d, (92, 104, 102, 104), '#d8403a'); line(d, (92, 106, 102, 106), '#3e8a5a')
    rect(d, (68, 40, 92, 58), '#ffffff')                                 # “先洗手”标识（手 + 水滴）
    bevel(d, (68, 40, 92, 58), '#ffffff', '#c8c4b8')
    rect(d, (70, 42, 90, 45), '#3e8a5a')
    ellipse(d, (73, 47, 81, 55), '#f0c8a0')
    for k in range(3):
        rect(d, (76 + k * 2, 45, 77 + k * 2, 49), '#f0c8a0')
    px(d, 85, 49, '#4a9ae0'); px(d, 86, 52, '#4a9ae0'); px(d, 84, 54, '#4a9ae0')
    # ---------------- 操作台（112–244）：砧板、番茄、罗勒、芝士；上面一层搁板摆罐子，挂铜锅
    cx0, cx1 = 112, 244
    rect(d, (cx0, 100, cx1, 104), '#c8ccd2')
    line(d, (cx0, 100, cx1, 100), '#eef0f4')
    rect(d, (cx0 + 2, 104, cx1 - 2, G - 1), '#b8bcc4')
    for x in range(cx0 + 4, cx1 - 6, 32):
        bevel(d, (x, 108, x + 28, G - 6), '#d8dce2', '#8a8e96')
        rect(d, (x + 12, 110, x + 16, 111), '#7a7e86')
    rect(d, (130, 96, 166, 100), '#c89a62')                              # 砧板
    line(d, (130, 96, 166, 96), '#e0b880')
    for k, xx in enumerate((136, 144, 152)):
        ellipse(d, (xx - 3, 91 - k % 2, xx + 3, 97 - k % 2), '#d8302a')
        px(d, xx - 1, 92 - k % 2, '#f06a5a'); px(d, xx, 90 - k % 2, '#3e8a3a')
    line(d, (158, 95, 168, 92), '#c8ccd2'); rect(d, (156, 95, 159, 97), '#3a2a20')
    ellipse(d, (176, 92, 188, 100), '#f8f4e8')                           # 马苏里拉芝士
    for j in range(5):
        ellipse(d, (198 + j * 3, 92 - (j % 2) * 2, 202 + j * 3, 97), '#4a9a3a' if j % 2 else '#6aba4a')   # 一盆罗勒
    rect(d, (198, 96, 214, 100), '#c06a4a')
    rect(d, (222, 86, 230, 100), '#e8d870')                              # 橄榄油瓶
    rect(d, (224, 80, 228, 86), '#3e6a3a')
    rect(d, (cx0, 46, cx1, 48), '#9a9ea6')                               # 搁板
    for k, xx in enumerate(range(cx0 + 4, cx1 - 8, 14)):
        rect(d, (xx, 34, xx + 9, 46), ['#e8c070', '#d8403a', '#f4f0e6', '#7a9a4a', '#c8a050'][k % 5])
        rect(d, (xx - 1, 32, xx + 10, 34), '#7a7e86')
        line(d, (xx + 1, 36, xx + 1, 44), '#ffffff')
    line(d, (cx0, 70, cx1, 70), '#7a7e86')                               # 挂锅的横杆 + 铜锅
    for k, xx in enumerate((124, 150, 178, 204, 230)):
        line(d, (xx, 70, xx, 74), '#5a5e66')
        r = 6 + (k % 2) * 2
        ellipse(d, (xx - r, 74, xx + r, 74 + r * 1.4), '#c87a4a')
        ellipse(d, (xx - r + 2, 76, xx, 74 + r), '#e8a070')
    # ---------------- 灶台（252–340）+ 大汤锅 + 抽油烟机
    gx0, gx1 = 252, 340
    rect(d, (gx0 - 4, 14, gx1 + 4, 40), '#c8ccd2')
    d.polygon([(gx0 - 4, 40), (gx1 + 4, 40), (gx1 - 6, 52), (gx0 + 6, 52)], fill=C('#b8bcc4'))
    line(d, (gx0 - 4, 14, gx1 + 4, 14), '#eef0f4')
    line(d, (gx0 + 6, 52, gx1 - 6, 52), '#8a8e96')
    rect(d, (gx0, 100, gx1, G - 1), '#3a3a40')
    rect(d, (gx0, 96, gx1, 100), '#5a5a62')
    line(d, (gx0, 96, gx1, 96), '#7a7a82')
    for x in range(gx0 + 6, gx1 - 6, 20):
        ellipse(d, (x, 104, x + 6, 110), '#c8ccd2')
        px(d, x + 3, 106, '#3a3a40')
    rect(d, (gx0 + 4, 114, gx1 - 4, G - 4), '#2a2a30')
    bevel(d, (gx0 + 4, 114, gx1 - 4, G - 4), '#4a4a52', '#1a1a1e')
    rect(d, (gx0 + 30, 116, gx1 - 30, 118), '#c8ccd2')
    rect(d, (262, 70, 300, 96), '#b8bcc4')                               # 大汤锅
    ellipse(d, (261, 66, 301, 74), '#d8dce2')
    ellipse(d, (264, 68, 298, 72), '#c8742a')                            # 汤（番茄色）
    line(d, (264, 76, 264, 94), '#e0e4ea')
    rect(d, (256, 76, 261, 79), '#8a8e96'); rect(d, (301, 76, 306, 79), '#8a8e96')
    line(d, (290, 66, 300, 52), '#a07a52')                               # 汤勺柄
    rect(d, (312, 84, 334, 96), '#3a3a40')                               # 平底锅
    line(d, (312, 84, 334, 84), '#5a5a62')
    line(d, (334, 88, 344, 86), '#3a2a20')
    for x in range(256, 300, 6):                                         # 灶火（小小的蓝色）
        px(d, x, 97, '#4a8ae0')
    # ---------------- 烤炉（348–400）：砖砌拱门，里面是火
    ox0, ox1 = 348, 402
    rect(d, (ox0, 30, ox1, G - 1), '#a85a42')
    for r, y in enumerate(range(30, G, 5)):
        for x in range(ox0 + (r % 2) * 5, ox1, 10):
            line(d, (x, y, x, y + 4), '#8a4434')
        line(d, (ox0, y + 4, ox1, y + 4), '#8a4434')
    line(d, (ox0, 30, ox1, 30), '#c87a5a')
    ax0, ax1, ay0, ay1 = 358, 392, 70, 100
    d.pieslice((ax0 - 4, ay0 - 4, ax1 + 4, ay0 + 30), 180, 360, fill=C('#6a2e22'))
    rect(d, (ax0 - 4, ay0 + 13, ax1 + 4, ay1), '#6a2e22')
    d.pieslice((ax0, ay0, ax1, ay0 + 26), 180, 360, fill=C('#1e1210'))
    rect(d, (ax0, ay0 + 13, ax1, ay1), '#1e1210')
    rect(d, (ax0 - 6, ay1, ax1 + 6, ay1 + 4), '#5a5a62')
    line(d, (ax0 - 6, ay1, ax1 + 6, ay1), '#7a7a82')
    rect(d, (ox0 + 4, 104, ox1 - 4, G - 4), '#8a4434')                   # 下面的柴堆
    for k in range(8):
        xx = ox0 + 8 + (k % 4) * 11
        yy = 110 + (k // 4) * 9
        ellipse(d, (xx, yy, xx + 9, yy + 7), '#8a5a36')
        ellipse(d, (xx + 3, yy + 2, xx + 6, yy + 5), '#c89a62')
    line(d, (404, 70, 418, 54), '#a07a52')                               # 披萨铲靠在一边
    d.polygon([(416, 56), (424, 46), (430, 50), (422, 60)], fill=C('#c8a070'))
    # ---------------- 冰箱（430–478，双开门不锈钢）
    fx0, fx1 = 430, 478
    rect(d, (fx0, 22, fx1, G - 1), '#c8ccd2')
    line(d, (fx0, 22, fx1, 22), '#eef0f4')
    line(d, (fx0, 22, fx0, G - 1), '#e0e4ea')
    line(d, (fx1, 22, fx1, G - 1), '#8a8e96')
    line(d, ((fx0 + fx1) // 2, 24, (fx0 + fx1) // 2, G - 4), '#8a8e96')
    for hx in ((fx0 + fx1) // 2 - 4, (fx0 + fx1) // 2 + 3):
        rect(d, (hx, 50, hx + 1, 90), '#7a7e86')
    for xx in range(fx0 + 4, fx1 - 4, 6):
        line(d, (xx, 26, xx + 3, 32), '#e8ecf0')
    rect(d, (fx0 + 6, 40, fx0 + 16, 50), '#f8f4c8')                     # 门上贴的菜单
    line(d, (fx0 + 8, 43, fx0 + 14, 43), '#8a8aa0'); line(d, (fx0 + 8, 46, fx0 + 13, 46), '#8a8aa0')
    rect(d, (fx0, G - 4, fx1, G - 1), '#7a7e86')
    # ---------------- 地板：红褐色防滑砖
    im = tile_floor(im, 0, W, G, '#a85a42', '#984e38', '#6e3424', h0=5.0)
    d = ImageDraw.Draw(im)
    for x0_, x1_ in ((sx0, sx1), (cx0, cx1), (gx0, gx1), (ox0, ox1), (fx0, fx1)):
        im = dither_fill(im, (x0_, G, x1_, G + 3), '#6e3424', '#844430', .5)
    steam = steam_strip(40, 36, n=8, puffs=7, seed=4)
    fire = fire_strip(ax1 - ax0 - 2, 16, n=6, seed=2)
    glow = lamp_glow_img(W, 180, [(375, 92, 40, .9), (281, 70, 26, .35)], col='#ff8a40')
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(door=[24, 148], sink=[80, 148], faucet=[84, 82], sign=[80, 48], counter=[178, 148], board=[148, 94],
                             stove=[296, 148], pot=[281, 70], oven=[375, 148], oven_mouth=[375, 86], fridge=[454, 148],
                             patrol_x=[200, 370], walk_x=[8, 472]),
                layers=[L_pano(key, 'room'),
                        {'type': 'strip', 'image': f'bg/{key}/fire', 'n': 6, 'fps': 8, 'k': 1, 'x': ax0 + 1, 'y': ay1 - 16,
                         'w': ax1 - ax0 - 2, 'h': 16},
                        {'type': 'glow', 'image': f'bg/{key}/glow', 'k': 1, 'x': 0, 'y': 0, 'alpha': .8, 'flicker': .25},
                        {'type': 'strip', 'image': f'bg/{key}/steam', 'n': 8, 'fps': 6, 'k': 1, 'x': 261, 'y': 32, 'w': 40, 'h': 36,
                         'alpha': .85}],
                fg=[])
    pv = im.copy()
    pv.alpha_composite(fire.crop((0, 0, ax1 - ax0 - 2, 16)), (ax0 + 1, ay1 - 16))
    pv.alpha_composite(soften(glow, .8))
    pv.alpha_composite(steam.crop((0, 0, 40, 36)), (261, 32))
    preview(key, {'room': pv}, ['room'], W)
    return {key: save_layers(key, {'room': im, 'fire': fire, 'glow': glow, 'steam': steam}, meta)}


SCENES = {'trattoria': trattoria, 'trattoria_kitchen': trattoria_kitchen, 'seaside_villa': seaside_villa, 'cape_cliff': cape_cliff, 'budogaoka_classroom': budogaoka_classroom, 'seaside_villa_out': seaside_villa_out}


def main(keys):
    meta = LIB.load_json(META, {}) or {}
    for k in keys or SCENES:
        r = SCENES[k]()
        meta.update(r)
        print('背景', k)
    LIB.save_json(META, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
