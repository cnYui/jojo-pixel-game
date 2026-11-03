# 第四部第8章（吉良家旧宅 / 原子心之父）的背景：4 张，全部程序绘制，画法和零件沿用序章（p4_bg.py / p4_bglib.py）。
#   输出 第四部/assets/bg/<key>/<层>.png + 第四部/assets/_meta/bg_ch8.json（build_p4.py 会把 _meta/bg_*.json 并进 bg.json）。
#   用法：python3 第四部/tools/art/p4_bg_ch8.py [key ...]      预览图：第四部/assets/preview/bg_<key>.png（不进游戏包）
#   图层 pack 一律 'ch8'（打包成 data/img_bg_ch8.js，进第8章时才加载）。
#   kira_house_out 吉良家旧宅外（480）、kira_house 旧宅室内（640，含第 12 战照片白框）、
#   kawajiri_house 川尻家（640，第9、11章和终章也用；早上 / 傍晚 / 夜三种开关）、morioh_station 杜王车站前广场（960）。
#   锚点和开关层的说明在 第四部/docs/第8章_背景.md。
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import *  # noqa: F401,F403,E402
from p4_bg import liv_floor, liv_kitchen_floor, preview, save_layers, sky_far  # noqa: E402

PACK = 'ch8'
H = 180

# ------------------------------------------------------------ 小工具（第2章脚本里也有同名的，各章各写一份，互不依赖）
LET = {'A': ['010', '101', '111', '101', '101'], 'E': ['111', '100', '110', '100', '111'], 'H': ['101', '101', '111', '101', '101'],
       'I': ['111', '010', '010', '010', '111'], 'M': ['10001', '11011', '10101', '10001', '10001'],
       'N': ['1001', '1101', '1011', '1001', '1001'], 'O': ['010', '101', '101', '101', '010'], 'R': ['110', '101', '110', '101', '101'],
       'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'], 'X': ['101', '101', '010', '101', '101'],
       'J': ['001', '001', '001', '101', '010'], 'K': ['101', '101', '110', '101', '101'], 'C': ['011', '100', '100', '100', '011'],
       'P': ['110', '101', '110', '100', '100'], 'R2': ['110', '101', '110', '101', '101'], ' ': ['000'] * 5,
       ':': ['0', '1', '0', '1', '0'], '-': ['000', '000', '111', '000', '000']}


def letters(d, x, y, text, col, gap=1):
    cx = x
    for ch in text:
        g = LET.get(ch) or DIG.get(ch) or ['000'] * 5
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == '1':
                    px(d, cx + c, y + r, col)
        cx += len(g[0]) + gap
    return cx - x - gap


def text_w(text, gap=1):
    return sum(len((LET.get(ch) or DIG.get(ch) or ['000'])[0]) + gap for ch in text) - gap


def kanji(im, x, y, text, col, vertical=False, size=12):
    """文泉驿点阵正黑 12 px（ttc index=1）；vertical = 竖排。返回 (宽, 高)"""
    if vertical:
        cy, w = y, 0
        for ch in text:
            m = LIB.text_mask(ch, LIB.WQY, size, index=1)
            im.paste(C(col), (int(x + (size - m.width) // 2), int(cy)), m)
            cy += m.height + 2
            w = max(w, m.width)
        return w, cy - y - 2
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    im.paste(C(col), (int(x), int(y)), m)
    return m.width, m.height


def kanji_size(text, size=12):
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    return m.width, m.height


def clock_face(d, cx, cy, r, hh, mm, rim='#7a5434', face='#f6f0e0', hand='#2a2a30', tick='#a8a090'):
    ellipse(d, (cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), rim)
    ellipse(d, (cx - r, cy - r, cx + r, cy + r), face)
    for i in range(12):
        a = i * math.pi / 6
        px(d, cx + (r - 1) * math.sin(a), cy - (r - 1) * math.cos(a), tick if i % 3 else hand)
    am = mm / 60 * 2 * math.pi
    ah = (hh % 12 + mm / 60) / 12 * 2 * math.pi
    line(d, (cx, cy, cx + (r - 2) * math.sin(am), cy - (r - 2) * math.cos(am)), hand)
    line(d, (cx, cy, cx + (r - 4) * math.sin(ah), cy - (r - 4) * math.cos(ah)), hand)
    px(d, cx, cy, '#c83a34')


def poly(d, pts, col):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=C(col))


def glow_from_field(f, col, levels=6):
    """强度场 → lighter 叠加用的光晕图（颜色即亮度），4×4 抖动量化"""
    h, w = f.shape
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    fq = np.clip(np.floor(f * levels + bay) / levels, 0, 1)
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = np.clip(fq[..., None] * np.array(c3(col), float), 0, 255).astype(np.uint8)
    a[..., 3] = np.where(fq > 0, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def radial(w, h, cx, cy, rx, ry, power=1.6, peak=1.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(1 - r, 0, 1) ** power * peak


def only(im, box):
    """整张图里只留 box 那一块（开关层用：和底图同尺寸、同坐标）"""
    out = new(im.width, im.height)
    x0, y0, x1, y1 = [int(v) for v in box]
    out.paste(im.crop((x0, y0, x1, y1)), (x0, y0))
    return out


def comp(*ims):
    out = ims[0].copy()
    for im in ims[1:]:
        out.alpha_composite(im)
    return out


def green_tree(im, cx, g, h=96, w=70, seed=0):
    """夏天的绿树（借樱花树的画法，换一套绿色）"""
    pal = dict(d='#2e5a34', m='#467a44', l='#6a9c56', x='#94c070', trunk='#4a3a2a', trunk2='#2e2418')
    return sakura(im, cx, g, h, w, seed=seed, pal=pal, petals=False)


def wood_floor(im, x0, x1, G, tones=('#8a6440', '#7e5a3a', '#94704a', '#84603e'), seam='#5e4028'):
    """老房子的木地板（比序章的深一点）：越往下木条越宽"""
    d = ImageDraw.Draw(im)
    y, h, row = G, 3.0, 0
    rng = np.random.RandomState(x0 + 7)
    while y < H:
        yb = min(H, int(round(y + h)))
        rect(d, (x0, int(y), x1, yb - 1), tones[row % 4])
        line(d, (x0, yb - 1, x1, yb - 1), seam)
        plank = int(36 + h * 6)
        off = rng.randint(0, plank)
        for x in range(x0 - off, x1, plank):
            if x > x0:
                line(d, (x, int(y), x, yb - 2), seam)
        y += h
        h = min(9.0, h * 1.18)
        row += 1
    return im


def tatami_floor(im, x0, x1, G, base='#c4bc84', dark='#aaa270', heri='#2e3a2a'):
    """榻榻米：一排排草席（越近越宽），席边是深绿的布边；席面上细细的织纹"""
    d = ImageDraw.Draw(im)
    rect(d, (x0, G, x1, H - 1), base)
    y, h, row = G, 6.0, 0
    while y < H:
        yb = min(H, int(round(y + h)))
        for yy in range(int(y) + 1, yb - 1, 2):
            line(d, (x0, yy, x1, yy), dark)
        line(d, (x0, int(y), x1, int(y)), heri)
        mw = int(64 + h * 4)
        off = (row % 2) * mw // 2
        for x in range(x0 - off, x1, mw):
            if x > x0:
                rect(d, (x, int(y), x + 1, yb - 1), heri)
        y += h
        h = min(16.0, h * 1.45)
        row += 1
    return im


def pillar(d, x, top, bot, w=6, col='#5a3e2c', hi='#7a5640', lo='#3e2a1e'):
    rect(d, (x, top, x + w - 1, bot), col)
    line(d, (x, top, x, bot), hi)
    line(d, (x + w - 1, top, x + w - 1, bot), lo)


def grayed(im, desat=.85, lift=.25):
    """照片空间外面那圈：褪色、发白"""
    a = np.array(im).astype(float)
    g = a[..., :3].mean(axis=2, keepdims=True)
    rgb = a[..., :3] * (1 - desat) + g * desat
    rgb = rgb * (1 - lift) + 235 * lift
    a[..., :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def save(key, layers, meta, pv):
    preview(key, {'room': pv}, ['room'], meta['w'])
    save_layers(key, layers, meta)
    return meta


def layer(bg, name, **kw):
    L = {'type': 'image', 'image': f'bg/{bg}/{name}', 'k': 1, 'x': 0, 'y': 0}
    L.update(kw)
    return L


ROOF = ('#4a4e56', '#363a42', '#6a6e78', '#24262c')        # 旧宅的黑瓦（偏灰，有年头）


# ============================================================ 吉良家旧宅外 kira_house_out（480 宽，七月午后）
#   左：邻居家的水泥砖墙和电线杆 → 吉良家：白灰泥围墙 + 瓦顶的木门（能开：key 'gate'），门右边挂「吉良」的木门牌和信箱；
#   墙后是两层的老式日本住宅（黑瓦、深色木板墙、二楼一排木格窗），院子里两棵松树探出墙头 → 右：另一家的砖墙、自动贩卖机。
#   人走在墙外的马路上（y 138 起是人行道，146 起是柏油路）。
KHO_G = 138          # 墙脚 / 人行道起点


def kho_house(im):
    d = ImageDraw.Draw(im)
    # 二楼
    rect(d, (172, 38, 372, 74), '#e6dece')
    for x in range(172, 373, 40):
        pillar(d, x, 38, 74, 4)
    line(d, (172, 56, 372, 56), '#5a3e2c')
    for i, wx in enumerate((184, 250, 318)):
        wb = (wx, 44, wx + 40, 70)
        rect(d, wb, '#4a3426')
        rect(d, (wx + 2, 46, wx + 38, 68), '#55708a')
        for gx in range(wx + 2, wx + 38, 6):                       # 木格
            line(d, (gx, 46, gx, 68), '#4a3426')
        line(d, (wx + 2, 57, wx + 38, 57), '#4a3426')
        for gx in range(wx + 3, wx + 37, 9):                        # 玻璃反光
            px(d, gx, 48, '#a8c0d4')
            px(d, gx + 1, 47, '#a8c0d4')
        if i == 1:                                                  # 中间那扇拉着发黄的窗帘（吉良的房间在里面）
            rect(d, (wx + 2, 46, wx + 14, 68), '#d8c8a0')
            for yy in range(47, 68, 3):
                px(d, wx + 8, yy, '#c4b084')
    im = tiled_roof(im, 160, 384, 22, 38, ROOF, overhang=8)
    d = ImageDraw.Draw(im)
    # 一楼（大半被围墙挡住）
    rect(d, (120, 80, 424, 120), '#e2dacb')
    for x in range(120, 425, 38):
        pillar(d, x, 80, 120, 4)
    rect(d, (120, 104, 424, 120), '#5e4634')                       # 腰板
    for x in range(122, 424, 3):
        line(d, (x, 104, x, 120), '#523c2c')
    for wx in (130, 280, 340):                                      # 一楼的拉窗（只露上半截）
        rect(d, (wx, 86, wx + 44, 104), '#4a3426')
        rect(d, (wx + 2, 88, wx + 42, 104), '#f0e8d4')
        for gx in range(wx + 2, wx + 42, 8):
            line(d, (gx, 88, gx, 104), '#b8a888')
    im = tiled_roof(im, 112, 432, 70, 84, ROOF, overhang=6)
    d = ImageDraw.Draw(im)
    # 玄关：小坡屋檐 + 格子拉门 + 门灯（只从大门看得见）
    rect(d, (206, 86, 248, 120), '#5a3e2c')
    rect(d, (210, 90, 244, 120), '#d8ccb0')
    for gx in range(210, 245, 4):
        line(d, (gx, 90, gx, 120), '#6a4a34')
    for gy in range(90, 120, 6):
        line(d, (210, gy, 244, gy), '#6a4a34')
    line(d, (227, 90, 227, 120), '#3e2a1e')
    rect(d, (248, 92, 252, 98), '#f4e0a0')
    return im


def kho_yard(im):
    """墙后面的院子：碎石、踏脚石小路（从大门一直铺到玄关）、石灯笼"""
    d = ImageDraw.Draw(im)
    im = dither_fill(im, (110, 118, 432, KHO_G), '#b4ac9c', '#a09888', .35)
    d = ImageDraw.Draw(im)
    for k, (sx, sy, sw) in enumerate(((221, 120, 12), (219, 125, 14), (218, 130, 16), (216, 135, 18))):
        ellipse(d, (sx - sw // 2 + 6, sy, sx + sw // 2 + 6, sy + 3), '#8a8478')
        line(d, (sx - sw // 2 + 8, sy, sx + sw // 2 + 4, sy), '#a8a294')
    # 石灯笼（大门里右手边）
    rect(d, (240, 122, 243, 134), '#8a8a84')
    rect(d, (236, 116, 247, 122), '#9a9a92')
    rect(d, (238, 117, 245, 120), '#3a3a36')
    poly(d, [(234, 116), (241, 110), (249, 116)], '#7a7a74')
    return im


def kho_gate_closed(d):
    rect(d, (202, 90, 250, KHO_G), '#6a4e38')
    for x in range(204, 250, 5):
        line(d, (x, 90, x, KHO_G), '#5a4030')
    line(d, (226, 90, 226, KHO_G), '#3a2a1e')
    for y in (100, 126):
        line(d, (202, y, 250, y), '#4a3426')
        for x in (208, 220, 232, 244):
            px(d, x, y, '#a89a7a')
    rect(d, (222, 112, 225, 116), '#a89a7a')
    rect(d, (227, 112, 230, 116), '#a89a7a')


def kira_house_out():
    W = 480
    far = sky_far(400, seed=21, sea=False, cols=('#5c9ce8', '#80b4ee', '#a8ccf2', '#d0e4f6'))
    fd = ImageDraw.Draw(far)
    for i, (cx, top, w) in enumerate(((60, 30, 70), (300, 22, 90))):   # 夏天的积雨云（高高的一团）
        for k in range(4):
            cloud(far, cx - w // 2 + k * 4, top + 44 - k * 10, w - k * 14, seed=40 + i * 4 + k,
                  cols=('#ffffff', '#eef2f8', '#c8d4e4'))
    near = new(W, H)
    # 左邻：二层民宅 + 水泥砖墙 + 树篱
    near = house(near, 0, 112, w=82, h=66, wall='#ece2cc', wall2='#cfc4ac', seed=3, roof=('#7a4a3e', '#5e382e', '#9a6250', '#3e241e'))
    near = hedge(near, 0, 92, 96, 112, seed=4)
    near = block_wall(near, 0, 92, 108, KHO_G)
    # 吉良家：房子 → 院子 → 松树
    near = kho_house(near)
    near = kho_yard(near)
    near = pine(near, 146, 118, h=78, seed=5)
    near = pine(near, 398, 118, h=66, seed=6)
    gate_view = near.crop((202, 86, 250, KHO_G))                       # 门开着时从门洞里看到的
    d = ImageDraw.Draw(near)
    # 白灰泥围墙（92–440，大门 202–250 留空）
    for x0, x1 in ((92, 196), (256, 440)):
        rect(d, (x0, 100, x1, KHO_G), '#e8e2d4')
        rect(d, (x0, KHO_G - 7, x1, KHO_G), '#8e8a80')            # 石头墙基
        for x in range(x0 + 3, x1, 9):
            line(d, (x, KHO_G - 7, x, KHO_G), '#76726a')
        line(d, (x0, KHO_G - 7, x1, KHO_G - 7), '#a8a49a')
        line(d, (x1, 100, x1, KHO_G - 8), '#c8c0b0')
    near = noise_specks(near, (92, 102, 440, KHO_G - 8), ['#d4ccba', '#ccc4b0', '#dcd6c6'], 260, seed=8)   # 旧墙的斑
    near = noise_specks(near, (92, KHO_G - 9, 440, KHO_G - 6), ['#6e8a52', '#5a7444'], 50, seed=9)          # 墙根的青苔
    d = ImageDraw.Draw(near)
    for x0, x1 in ((92, 196), (256, 440)):                           # 墙头的小瓦顶
        near = tiled_roof(near, x0 + 2, x1 - 2, 94, 100, ROOF, overhang=2)
    d = ImageDraw.Draw(near)
    for x in range(120, 190, 13):                                    # 雨水流下来的印子
        for y in range(101, 112):
            if (x + y) % 3:
                px(d, x, y, '#d4ccbc')
    # 大门：两根门柱 + 瓦顶 + 两扇木门
    pillar(d, 196, 84, KHO_G, 6)
    pillar(d, 250, 84, KHO_G, 6)
    rect(d, (196, 84, 256, 88), '#4a3426')
    near = tiled_roof(near, 194, 258, 72, 84, ROOF, overhang=6)
    d = ImageDraw.Draw(near)
    kho_gate_closed(d)
    # 门牌「吉良」+ 信箱
    rect(d, (259, 103, 274, 133), '#3e2a1e')
    rect(d, (260, 104, 273, 132), '#d2b484')
    line(d, (260, 104, 273, 104), '#e6cc9c')
    kanji(near, 261, 105, '吉良', '#2a1e18', vertical=True)
    rect(d, (180, 112, 193, 124), '#3e5a4a')
    rect(d, (180, 112, 193, 114), '#4e6e5a')
    line(d, (182, 117, 191, 117), '#24342a')
    # 右邻：砖墙 + 自动贩卖机
    near = block_wall(near, 440, W, 106, KHO_G)
    near = hedge(near, 440, W, 94, 106, seed=12)
    near = vending(near, 452, KHO_G + 4)
    # 地面：人行道 + 柏油路（路边白线）
    near = sidewalk(near, 0, W, KHO_G, 146)
    near = asphalt(near, 0, W, 146, H, dash=False)
    d = ImageDraw.Draw(near)
    line(d, (0, KHO_G, W, KHO_G), '#6e6a62')
    line(d, (0, 150, W, 150), '#e8e4d8')
    for x in range(0, W, 3):                                          # 墙的影子落在人行道上一条
        px(d, x, KHO_G + 1, '#94908a')
    # 电线杆（左邻门口）+ 电线
    near = pole(near, 64, 146, h=134)
    near = wires(near, [(-10, 20), (66, 16), (W + 10, 30)], sag=8)
    # 开着的门：门洞里是院子小路和玄关，两扇门板朝里推开只露一条边
    go = new(W, H)
    go.paste(gate_view, (202, 86))
    gd = ImageDraw.Draw(go)
    for x0 in (202, 245):
        rect(gd, (x0, 90, x0 + 4, KHO_G), '#5a4030')
        line(gd, (x0 + (4 if x0 == 202 else 0), 90, x0 + (4 if x0 == 202 else 0), KHO_G), '#3a2a1e')
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(gate=[226, 146], gate_in=[226, 132], nameplate=[266, 118], mailbox=[186, 118],
                             window2=[270, 57], genkan=[227, 116], pine_l=[146, 90], pine_r=[398, 96], pole=[64, 146],
                             vending=[460, 146], walk_x=[8, 472]),
                layers=[{'type': 'pano', 'image': 'bg/kira_house_out/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/kira_house_out/near', 'k': 1, 'x': 0, 'y': 0},
                        layer('kira_house_out', 'gate_open', key='gate'),
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = comp(far.resize((W, H), Image.NEAREST), near)
    return save('kira_house_out', {'far': far, 'near': near, 'gate_open': go}, meta, pv)



# ============================================================ 旧宅室内 kira_house（640 宽，一层的剖面，夏天午后、屋里昏昏的）
#   左起：吉良的房间（窗下书桌和本子、书架、墙上三张奖状、奖杯柜：全是第三名）→ 和室（佛坛、长押上挂着父亲的遗照、
#   矮桌上的相框和相册、老电视）→ 走廊（吉广飞出去的那扇窗，能开：key 'window'）→ 储物间（坏了锁的长木箱，能开：key 'box'）。
#   第 12 战的照片空间：key 'photo' = 白框（x 150–510）外面全部褪成灰白，只剩框里有颜色。
KH_G = 134
KH_FRAME = (150, 510)


def garden_view(w, h, seed=0):
    """窗外：夏天的天、院子里的树（只画窗框里那一块）"""
    v = grad(new(w, h), (0, 0, w, h), ('#a8ccec', '#d4e6f2'))
    v = green_tree(v, w // 2 + 4, h + 30, int(h * 1.4), int(w * 1.2), seed=seed)
    d = ImageDraw.Draw(v)
    for gx in range(2, w - 2, 7):
        line(d, (gx, 2, gx + 3, 5), '#e8f2fa')
    return v


def kh_room():
    W = 640
    im = new(W, H, '#d8cbad')
    d = ImageDraw.Draw(im)
    # 墙：吉良的房间和走廊是米色灰泥，和室是土墙（沙色、带细点），储物间是没刷的旧板墙
    rect(d, (0, 8, 200, KH_G), '#e0d4b8')
    rect(d, (206, 8, 430, KH_G), '#cdb88e')
    im = noise_specks(im, (206, 44, 430, KH_G), ['#c0aa80', '#d6c49c', '#b8a278'], 900, seed=21)
    d = ImageDraw.Draw(im)
    rect(d, (436, 8, 500, KH_G), '#e0d4b8')
    rect(d, (506, 8, W, KH_G), '#8e7656')
    for x in range(506, W, 11):
        line(d, (x, 8, x, KH_G), '#7a6448')
        px(d, x + 3, 30 + (x * 7) % 60, '#6e5a40')
    # 天花板：木板条
    rect(d, (0, 0, W, 8), '#9a7a58')
    for x in range(0, W, 12):
        line(d, (x, 0, x, 7), '#86684a')
    line(d, (0, 8, W, 8), '#5a3e2c')
    # 长押（门楣横木）
    rect(d, (0, 40, W, 43), '#6a4a34')
    line(d, (0, 40, W, 40), '#8a6448')
    line(d, (0, 44, W, 44), '#4a3426')
    # 踢脚
    rect(d, (0, KH_G - 3, W, KH_G), '#5a3e2c')

    # ---------------- A 吉良的房间（0–200）
    wx0, wy0, wx1, wy1 = 12, 50, 64, 100                     # 窗：外面是院子里的绿
    rect(d, (wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), '#6a4a34')
    im.paste(garden_view(wx1 - wx0 + 1, wy1 - wy0 + 1, seed=3), (wx0, wy0))
    d = ImageDraw.Draw(im)
    rect(d, (37, wy0, 39, wy1), '#6a4a34')
    rect(d, (wx0 - 6, wy0 - 6, wx0 + 6, wy1 + 2), '#c8b890')     # 发黄的窗帘
    rect(d, (wx1 - 6, wy0 - 6, wx1 + 6, wy1 + 2), '#c8b890')
    for x in (wx0 - 4, wx0, wx0 + 4, wx1 - 4, wx1, wx1 + 4):
        line(d, (x, wy0 - 6, x, wy1 + 2), '#b4a47a')
    # 书桌（窗下）+ 摊开的本子 + 台灯
    rect(d, (8, 104, 70, 107), '#7a5434')
    line(d, (8, 104, 70, 104), '#9a7050')
    rect(d, (10, 107, 13, KH_G - 1), '#6a4a30')
    rect(d, (44, 107, 68, 128), '#6e4c32')
    for y in (114, 121):
        line(d, (44, y, 68, y), '#5a3e2a')
        rect(d, (54, y - 4, 58, y - 3), '#c8b070')
    rect(d, (65, 128, 68, KH_G - 1), '#6a4a30')
    rect(d, (22, 100, 31, 103), '#f4f0e4')                      # 本子（左页、右页）
    rect(d, (32, 100, 41, 103), '#ece6d6')
    line(d, (31, 100, 31, 103), '#a8a090')
    for yy in (101, 102):
        line(d, (23, yy, 29, yy), '#9a9aa8')
        line(d, (33, yy, 39, yy), '#9a9aa8')
    line(d, (58, 103, 58, 88), '#3a3a3e')                       # 台灯
    poly(d, [(53, 84), (61, 84), (63, 90), (51, 90)], '#4e6a5a')
    rect(d, (55, 102, 61, 103), '#3a3a3e')
    # 书架（76–112）
    kx0, kx1 = 76, 112
    rect(d, (kx0, 46, kx1, KH_G - 1), '#6a4a30')
    line(d, (kx1, 46, kx1, KH_G - 1), '#4a3222')
    rng = np.random.RandomState(31)
    books = ['#7a3a32', '#3a4a6a', '#5a5a42', '#8a7a5a', '#4a3a4a', '#2e3e3a', '#a89a7a']
    for sy in (50, 72, 94):
        rect(d, (kx0 + 2, sy, kx1 - 2, sy + 19), '#3a2a1e')
        x = kx0 + 3
        while x < kx1 - 4:
            bw, bh = rng.randint(2, 5), rng.randint(13, 19)
            c = books[rng.randint(len(books))]
            rect(d, (x, sy + 19 - bh, x + bw - 1, sy + 18), c)
            px(d, x, sy + 19 - bh, mix(c, '#ffffff', .3))
            x += bw
        rect(d, (kx0 + 2, sy + 19, kx1 - 2, sy + 20), '#8a6644')
    rect(d, (kx0 + 2, 116, kx1 - 2, KH_G - 4), '#5a3e28')
    bevel(d, (kx0 + 3, 117, kx1 - 3, KH_G - 5), '#7a5a3c', '#3e2a1c')
    # 三张奖状（118–192）
    for i, x in enumerate((118, 143, 168)):
        rect(d, (x, 48, x + 22, 70), '#a8843a')
        rect(d, (x + 1, 49, x + 21, 69), '#f2ecd8')
        rect(d, (x + 3, 51, x + 19, 53), '#c8a040')
        for yy in range(56, 66, 2):
            line(d, (x + 4, yy, x + 18 - (yy % 4) * 2, yy), '#8a8478')
        ellipse(d, (x + 15, 63, x + 19, 67), '#c83a34')
    # 奖杯柜（118–196）+ 柜顶四座铜色奖杯（底座小牌上都是 3）
    rect(d, (118, 100, 196, KH_G - 1), '#6e4c32')
    rect(d, (120, 103, 194, 124), '#4a4a44')
    im = dither_fill(im, (121, 104, 194, 124), '#5a6064', '#6a7074', .3)
    d = ImageDraw.Draw(im)
    for mx in (128, 142, 156, 170, 184):                        # 柜里的奖牌（铜）
        line(d, (mx, 105, mx, 112), '#7a3a3a')
        ellipse(d, (mx - 3, 112, mx + 3, 118), '#b87a3a')
        px(d, mx - 1, 113, '#e0a868')
    line(d, (157, 103, 157, 124), '#6e4c32')
    rect(d, (120, 126, 194, KH_G - 2), '#5e4028')
    rect(d, (154, 129, 160, 130), '#c8b070')
    for k, tx in enumerate((126, 146, 166, 186)):
        th = (18, 14, 16, 12)[k]
        rect(d, (tx - 5, 96, tx + 5, 100), '#3e2a1e')
        rect(d, (tx - 3, 97, tx + 1, 99), '#c8a868')
        digits(d, tx - 1, 96, '3', '#3e2a1e') if False else None
        rect(d, (tx - 1, 100 - th + 8, tx + 1, 96), '#a86a32')
        ellipse(d, (tx - 5, 100 - th, tx + 5, 100 - th + 9), '#b87a3a')
        rect(d, (tx - 5, 100 - th, tx + 5, 100 - th + 3), '#b87a3a')
        line(d, (tx - 3, 100 - th + 1, tx - 3, 100 - th + 5), '#e8b070')
        line(d, (tx - 7, 100 - th + 2, tx - 6, 100 - th + 5), '#a86a32')
        line(d, (tx + 7, 100 - th + 2, tx + 6, 100 - th + 5), '#a86a32')
    pillar(d, 200, 8, KH_G, 6)

    # ---------------- B 和室（206–430）
    # 佛坛（216–262）：黑漆柜、门开着，里面金色
    bx0, bx1, by0 = 216, 262, 76
    rect(d, (bx0, by0, bx1, KH_G - 1), '#1e1a1a')
    line(d, (bx0, by0, bx1, by0), '#4a4040')
    rect(d, (bx0 + 6, by0 + 4, bx1 - 6, 112), '#8a6a24')
    rect(d, (bx0 + 8, by0 + 6, bx1 - 8, 110), '#c8a040')
    im = dither_fill(im, (bx0 + 8, by0 + 6, bx1 - 8, by0 + 16), '#c8a040', '#e8c860', .4)
    d = ImageDraw.Draw(im)
    rect(d, (237, 84, 241, 96), '#8a6a24')                       # 佛像的剪影（小小的）
    ellipse(d, (236, 81, 242, 87), '#8a6a24')
    rect(d, (bx0 + 10, 100, bx1 - 10, 104), '#6a4a1e')          # 供台
    for cx in (bx0 + 13, bx1 - 13):                              # 蜡烛
        rect(d, (cx - 1, 93, cx + 1, 100), '#f4f0e4')
        px(d, cx, 91, '#f8c860')
        px(d, cx, 92, '#f0a040')
    rect(d, (235, 98, 243, 100), '#5a5a5a')                     # 香炉
    line(d, (239, 92, 239, 98), '#a89a8a')
    for x0 in (bx0 - 4, bx1 - 2):                                # 两扇门板（开着，贴着两边）
        rect(d, (x0, by0, x0 + 6, 112), '#2a2424')
        line(d, (x0 + 1, by0 + 2, x0 + 1, 110), '#c8a040')
    rect(d, (bx0 + 2, 114, bx1 - 2, KH_G - 3), '#2a2424')
    for y in (118, 126):
        line(d, (bx0 + 4, y, bx1 - 4, y), '#3e3636')
        rect(d, (238, y - 2, 240, y), '#c8a040')
    # 长押上挂着父亲的遗照（黑框、两角黑缎带）：第 12 战吉广从这里进出
    rect(d, (226, 47, 252, 71), '#16141a')
    rect(d, (229, 50, 249, 68), '#a8a49c')
    im = grad(im, (229, 50, 250, 69), ('#bcb8b0', '#9a968e'))
    d = ImageDraw.Draw(im)
    ellipse(d, (234, 53, 244, 63), '#d8d0c4')                    # 老人：秃顶、圆眼镜、和服领
    line(d, (236, 58, 242, 58), '#3a3a3a')
    px(d, 237, 58, '#5a5a5a'); px(d, 241, 58, '#5a5a5a')
    poly(d, [(231, 68), (239, 63), (247, 68)], '#4a4a52')
    line(d, (239, 63, 239, 68), '#e8e4dc')
    for cx in (226, 252):
        poly(d, [(cx - 3 if cx == 226 else cx - 6, 47), (cx + 6 if cx == 226 else cx + 3, 47), (cx, 53)], '#000000')
    line(d, (230, 47, 239, 43), '#3a3a3a')
    line(d, (248, 47, 239, 43), '#3a3a3a')
    # 挂轴
    rect(d, (276, 48, 292, 100), '#e8e0c8')
    rect(d, (275, 47, 293, 49), '#6a4a34')
    rect(d, (275, 99, 293, 101), '#6a4a34')
    for yy in range(54, 96, 5):
        line(d, (284, yy, 284, yy + 3), '#3a3a3a')
    poly(d, [(278, 92), (284, 84), (290, 92)], '#8aa0a8')
    # 吊灯（圆形日光灯罩）
    line(d, (330, 8, 330, 14), '#3a3a3a')
    ellipse(d, (316, 13, 344, 20), '#e8e4d8')
    line(d, (318, 19, 342, 19), '#bcb6a6')
    line(d, (330, 14, 336, 26), '#9a9a9a')
    # 矮桌：立着的相框、相册、茶杯
    rect(d, (296, 120, 354, 123), '#5e3e2a')
    line(d, (296, 120, 354, 120), '#7e5a40')
    for lx in (300, 348):
        rect(d, (lx, 123, lx + 3, KH_G - 1), '#4e3424')
    rect(d, (302, 109, 313, 120), '#c8a868')                     # 相框
    rect(d, (304, 111, 311, 118), '#a8b4b8')
    ellipse(d, (306, 112, 309, 115), '#d8c8b0')
    line(d, (312, 115, 315, 120), '#8a6a44')
    rect(d, (322, 116, 340, 120), '#7a3a2e')                     # 相册
    line(d, (322, 116, 340, 116), '#9a5040')
    line(d, (322, 118, 340, 118), '#e8e0cc')
    rect(d, (344, 116, 348, 120), '#4e6a7a')                     # 茶杯
    # 老电视（370–418）
    rect(d, (368, 124, 418, KH_G - 1), '#6a4a30')
    line(d, (368, 124, 418, 124), '#8a6648')
    rect(d, (372, 128, 414, 131), '#5a3e28')
    rect(d, (372, 94, 414, 124), '#3a3836')
    line(d, (372, 94, 414, 94), '#5a5856')
    rect(d, (375, 98, 404, 120), '#1e2422')
    rect(d, (376, 99, 403, 119), '#2e3a36')
    line(d, (378, 101, 384, 101), '#4e5e58')
    line(d, (378, 102, 381, 102), '#4e5e58')
    for ky in (100, 106):
        ellipse(d, (406, ky, 411, ky + 4), '#6a6866')
    rect(d, (406, 113, 411, 118), '#2a2826')
    line(d, (384, 94, 378, 84), '#8a8a8a')                       # 天线
    line(d, (394, 94, 402, 82), '#8a8a8a')
    pillar(d, 430, 8, KH_G, 6)

    # ---------------- C 走廊（436–500）：吉广飞出去的那扇窗
    WX0, WY0, WX1, WY1 = 446, 50, 490, 104
    rect(d, (WX0 - 3, WY0 - 3, WX1 + 3, WY1 + 3), '#6a4a34')
    outside = garden_view(WX1 - WX0 + 1, WY1 - WY0 + 1, seed=9)
    im.paste(outside, (WX0, WY0))
    d = ImageDraw.Draw(im)
    rect(d, (467, WY0, 469, WY1), '#6a4a34')                    # 两扇拉窗的中梃
    rect(d, (WX0 - 5, WY1 + 4, WX1 + 5, WY1 + 6), '#7a5434')
    # 电话台
    rect(d, (452, 116, 484, 119), '#6a4a30')
    rect(d, (454, 119, 456, KH_G - 1), '#5a3e28')
    rect(d, (480, 119, 482, KH_G - 1), '#5a3e28')
    rect(d, (462, 110, 476, 116), '#2a2a2e')
    rect(d, (463, 108, 475, 110), '#3a3a3e')
    pillar(d, 500, 8, KH_G, 6)

    # ---------------- D 储物间（506–640）
    for sy in (58, 88):                                            # 层架
        rect(d, (512, sy, 560, sy + 2), '#6a5038')
    rect(d, (512, 58, 514, KH_G - 1), '#5a4430')
    rect(d, (558, 58, 560, KH_G - 1), '#5a4430')
    rng = np.random.RandomState(41)
    for sy in (58, 88):
        x = 516
        while x < 554:
            bw, bh = rng.randint(8, 14), rng.randint(10, 22)
            col = ['#b8986a', '#a88a5e', '#c8a878', '#8a7a6a'][rng.randint(4)]
            rect(d, (x, sy - bh, min(556, x + bw), sy - 1), col)
            line(d, (x, sy - bh + 3, min(556, x + bw), sy - bh + 3), mix(col, '#000000', .2))
            x += bw + 2
    rect(d, (516, 102, 556, 132), '#d8d0c0')                     # 叠好的被褥
    for y in range(106, 132, 6):
        line(d, (516, y, 556, y), '#b8b0a0')
    rect(d, (612, 96, 636, KH_G - 1), '#b8986a')                 # 纸箱
    rect(d, (616, 80, 634, 96), '#a88a5e')
    line(d, (612, 110, 636, 110), '#9a7a50')
    line(d, (625, 80, 625, 96), '#8a6a44')
    line(d, (590, 0, 590, 22), '#3a3a3a')                        # 光秃秃的灯泡
    ellipse(d, (586, 22, 594, 30), '#f4ecc8')
    rect(d, (588, 19, 592, 22), '#6a6a6a')
    # 长木箱（568–608）：铁角、坏了的挂锁斜挂着
    cx0, cx1, ct = 566, 610, 110
    rect(d, (cx0, ct, cx1, KH_G - 1), '#7a5434')
    line(d, (cx0, ct, cx1, ct), '#9a7050')
    rect(d, (cx0, ct, cx1, ct + 5), '#6a4a2c')
    for x in (cx0, cx1 - 4):
        rect(d, (x, ct, x + 4, ct + 4), '#3a3a3a')
        rect(d, (x, KH_G - 5, x + 4, KH_G - 1), '#3a3a3a')
    line(d, (cx0, 122, cx1, 122), '#5a3e24')
    rect(d, (585, ct + 4, 591, ct + 9), '#3a3a3a')
    ellipse(d, (588, ct + 9, 595, ct + 16), '#8a7a5a')            # 挂锁（歪着）
    line(d, (589, ct + 10, 590, ct + 7), '#6a6a6a')
    im = wood_floor(im, 0, W, KH_G)
    im = tatami_floor(im, 206, 430, KH_G)
    # 储物间压暗一点
    a = np.array(im).astype(float)
    a[:, 506:, :3] *= .82
    im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    for x in (206, 430):                                            # 榻榻米和走廊地板的分界
        line(d, (x, KH_G, x, H), '#3e2a1e')
    return im, outside, (WX0, WY0, WX1, WY1), (cx0, cx1, ct)


def kira_house():
    W = 640
    room, outside, (WX0, WY0, WX1, WY1), (cx0, cx1, ct) = kh_room()
    # 窗开着：右扇推到左扇后面，右半边直接看到外面
    wo = new(W, H)
    wo.paste(outside.crop((22, 0, outside.width, outside.height)), (WX0 + 22, WY0))
    wd = ImageDraw.Draw(wo)
    rect(wd, (WX0 + 20, WY0, WX0 + 23, WY1), '#6a4a34')
    rect(wd, (WX0 + 2, WY0, WX0 + 4, WY1), '#5a3e2c')
    # 箱子开着：盖子往后翻起来，箱口是黑的
    bo = new(W, H)
    bd = ImageDraw.Draw(bo)
    rect(bd, (cx0, ct - 18, cx1, ct - 1), '#6a4a2c')
    line(bd, (cx0, ct - 18, cx1, ct - 18), '#8a6440')
    rect(bd, (cx0, ct - 18, cx0 + 4, ct - 14), '#3a3a3a')
    rect(bd, (cx1 - 4, ct - 18, cx1, ct - 14), '#3a3a3a')
    rect(bd, (cx0 + 1, ct, cx1 - 1, ct + 5), '#1e1610')
    rect(bd, (cx0 + 8, ct + 1, cx1 - 8, ct + 3), '#2e2218')
    ellipse(bd, (594, KH_G - 6, 601, KH_G + 1), '#8a7a5a')          # 锁掉在地上
    # 电视雪花（4 帧）
    sx0, sy0, sw, sh = 376, 99, 28, 21
    tv = new(sw * 4, sh)
    rng = np.random.RandomState(5)
    ta = np.array(tv)
    for f in range(4):
        v = rng.randint(0, 4, (sh, sw))
        cols = np.array([(40, 48, 46), (110, 120, 116), (180, 190, 186), (230, 236, 232)])
        ta[:, f * sw:(f + 1) * sw, :3] = cols[v]
        ta[:, f * sw:(f + 1) * sw, 3] = 255
        ta[rng.randint(sh), f * sw:(f + 1) * sw, :3] = (240, 244, 240)
    tv = Image.fromarray(ta, 'RGBA')
    # 钉在墙上的那张对折照片（胶带封住）
    pin = new(W, H)
    pd = ImageDraw.Draw(pin)
    rect(pd, (352, 60, 366, 74), '#f4f2ea')
    rect(pd, (354, 62, 364, 70), '#9a9690')
    line(pd, (352, 67, 366, 67), '#c8c4b8')
    for x0, y0 in ((349, 58), (363, 71)):
        rect(pd, (x0, y0, x0 + 5, y0 + 3), '#e8dca0')
    rect(pd, (357, 64, 361, 71), '#e8dca0')
    px(pd, 359, 59, '#c83a34')
    # 照片空间：白框外全部褪色发白，框是拍立得那种白边
    fx0, fx1 = KH_FRAME
    full = comp(room)
    gr = grayed(full)
    ga = np.array(gr)
    ga[4:174, fx0:fx1, 3] = 0
    gr = Image.fromarray(ga, 'RGBA')
    gd = ImageDraw.Draw(gr)
    rect(gd, (fx0 - 4, 0, fx0 - 1, H), '#f4f2ea')
    rect(gd, (fx1, 0, fx1 + 3, H), '#f4f2ea')
    rect(gd, (fx0 - 4, 0, fx1 + 3, 3), '#f4f2ea')
    rect(gd, (fx0 - 4, 174, fx1 + 3, H), '#f4f2ea')
    line(gd, (fx0, 4, fx1 - 1, 4), '#c8c4b8')
    line(gd, (fx0, 4, fx0, 173), '#c8c4b8')
    line(gd, (fx0 - 5, 0, fx0 - 5, H), '#9a968c')
    line(gd, (fx1 + 4, 0, fx1 + 4, H), '#9a968c')
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(window_room=[38, 75], desk=[40, 146], notebook=[32, 101], bookshelf=[94, 146],
                             awards=[155, 59], trophies=[156, 146], altar=[239, 146], portrait=[239, 59],
                             scroll=[284, 74], table=[325, 146], table_frame=[307, 114], album=[331, 118], tea=[346, 118],
                             tv=[393, 146], tv_screen=[390, 109], pinned=[359, 67], window=[468, 146], window_glass=[468, 77],
                             phone=[469, 146], storeroom=[540, 146], box=[588, 146], box_lid=[588, ct],
                             photo_x=[fx0, fx1], room_x=[0, 200], washitsu_x=[206, 430], hall_x=[436, 500], store_x=[506, 640],
                             walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/kira_house/room', 'k': 1, 'x': 0, 'y': 0},
                        layer('kira_house', 'window_open', key='window'),
                        layer('kira_house', 'box_open', key='box'),
                        layer('kira_house', 'pinned', key='pinned'),
                        {'type': 'strip', 'image': 'bg/kira_house/tv', 'n': 4, 'fps': 12, 'x': sx0, 'y': sy0, 'k': 1, 'key': 'tv'},
                        {'type': 'tint', 'color': '#6a4a2a', 'alpha': 0.08},
                        layer('kira_house', 'photo', key='photo')],
                fg=[])
    pv = comp(room, wo, bo, pin)
    pv.alpha_composite(tv.crop((0, 0, sw, sh)), (sx0, sy0))
    preview('kira_house_photo', {'room': comp(room, gr)}, ['room'], W)
    return save('kira_house', {'room': room, 'window_open': wo, 'box_open': bo, 'pinned': pin, 'tv': tv, 'photo': gr}, meta, pv)



# ============================================================ 川尻家 kawajiri_house（640 宽，一层剖面；第8、9、11章和终章都用）
#   左起：玄关和走廊（大门、鞋柜）→ 客厅（大窗、挂钟停在 8:30、沙发、电视柜；天花板右角藏着摄像机：key 'cam'）→
#   餐厅厨房（冰箱、流理台、餐桌和吊灯）→ 早人的房间（书桌、录像带、床）。
#   时间用开关：key 'morning' 早上的淡暖光；'dusk' 傍晚（窗外橙红 + 橙色罩色）；'night' 夜里（窗外深蓝 + 压暗 + 三盏灯的光晕）。
KW_G = 134
KW_WINDOWS = [(126, 46, 196, 108), (452, 52, 488, 84), (596, 48, 630, 96)]
KW_LAMPS = [(244, 14, 70, 46, .9), (432, 30, 46, 40, .95), (562, 92, 30, 26, .8)]   # 客厅吊灯、餐桌吊灯、早人的台灯：x, y, rx, ry, 强度


def kw_view(w, h, mode, seed=0):
    """窗外：邻居家的屋顶和电线（day / dusk / night）"""
    sky = {'day': ('#8cbcec', '#b8d6f2', '#dcecf8'), 'dusk': ('#6a5a9a', '#e0785a', '#f8b070'),
           'night': ('#0e1430', '#1a2448', '#26305a')}[mode]
    v = grad(new(w, h), (0, 0, w, h), sky)
    d = ImageDraw.Draw(v)
    rng = np.random.RandomState(seed)
    roof = {'day': '#6a7488', 'dusk': '#4a3a4a', 'night': '#0a0c18'}[mode]
    wall = {'day': '#e4dccc', 'dusk': '#8a6a6a', 'night': '#141a2c'}[mode]
    x = -6
    while x < w:
        bw = rng.randint(22, 34)
        top = int(h * .55) + rng.randint(-4, 6)
        rect(d, (x, top + 6, x + bw, h), wall)
        poly(d, [(x - 3, top + 7), (x + bw // 2, top), (x + bw + 3, top + 7)], roof)
        for wx in range(x + 4, x + bw - 4, 9):
            lit = mode == 'night' and rng.rand() < .5
            rect(d, (wx, top + 12, wx + 4, top + 16), '#f8d880' if lit else mix(wall, '#000000', .25))
        x += bw + rng.randint(2, 8)
    line(d, (0, int(h * .3), w, int(h * .3) + 3), '#2a2a30' if mode != 'night' else '#04060c')
    if mode == 'night':
        for _ in range(w * h // 120):
            px(d, rng.randint(w), rng.randint(int(h * .5)), '#c8d0f0')
        ellipse(d, (w - 14, 4, w - 6, 12), '#f4f0d8')
    return v


def kw_room(mode='day'):
    W = 640
    im = new(W, H, '#efe6d4')
    d = ImageDraw.Draw(im)
    for x in range(0, 520, 8):                                    # 墙纸的细竖纹
        line(d, (x, 10, x, KW_G), '#e8dfcc')
    rect(d, (528, 8, W, KW_G), '#d6e0e8')                         # 早人的房间：浅蓝墙纸
    for y in range(14, KW_G, 10):
        for x in range(530 + (y // 10) % 2 * 5, W, 10):
            px(d, x, y, '#c4d0dc')
    rect(d, (0, 0, W, 8), '#f6f2ea')                              # 天花板 + 顶角线
    line(d, (0, 8, W, 8), '#d8d0c0')
    line(d, (0, 9, W, 9), '#c8bea8')
    rect(d, (0, KW_G - 4, W, KW_G), '#b8a888')                    # 踢脚线
    line(d, (0, KW_G - 4, W, KW_G - 4), '#d0c2a4')
    # 窗（三扇；窗外按 mode 画）
    for i, (x0, y0, x1, y1) in enumerate(KW_WINDOWS):
        rect(d, (x0 - 3, y0 - 3, x1 + 3, y1 + 3), '#f6f4ee')
        bevel(d, (x0 - 3, y0 - 3, x1 + 3, y1 + 3), '#ffffff', '#c8c4b8')
        im.paste(kw_view(x1 - x0 + 1, y1 - y0 + 1, mode, seed=3 + i), (x0, y0))
        d = ImageDraw.Draw(im)
        mx = (x0 + x1) // 2
        rect(d, (mx - 1, y0, mx, y1), '#f6f4ee')
        rect(d, (x0 - 6, y1 + 4, x1 + 6, y1 + 6), '#e8e0d0')
        line(d, (x0 - 6, y1 + 4, x1 + 6, y1 + 4), '#ffffff')
    # ---------------- A 玄关 + 走廊（0–112）
    rect(d, (10, 54, 52, KW_G), '#6a5040')                        # 大门（深木色，竖条磨砂玻璃）
    rect(d, (14, 58, 48, KW_G), '#8a6a50')
    bevel(d, (14, 58, 48, KW_G), '#a08060', '#6a5040')
    rect(d, (20, 64, 28, 118), '#d8dcd8' if mode != 'night' else '#4a5068')
    for yy in range(65, 118, 3):
        line(d, (21, yy, 27, yy), '#e8ece8' if mode != 'night' else '#5a6078')
    rect(d, (40, 92, 44, 100), '#d8c070')
    rect(d, (64, 104, 98, KW_G - 1), '#c8b49a')                  # 鞋柜 + 花瓶 + 钥匙盘
    rect(d, (62, 101, 100, 104), '#a89070')
    line(d, (62, 101, 100, 101), '#d8c4a4')
    line(d, (81, 106, 81, KW_G - 3), '#a89070')
    for hx in (78, 84):
        rect(d, (hx, 116, hx + 1, 120), '#8a7458')
    rect(d, (68, 90, 74, 101), '#5a7aa8')
    for k, (fx, fy) in enumerate(((68, 84), (71, 81), (75, 85))):
        line(d, (71, 90, fx, fy + 2), '#4e8a52')
        ellipse(d, (fx - 2, fy - 1, fx + 2, fy + 3), ('#f4e070', '#f0f0f0', '#f4a0b0')[k])
    ellipse(d, (86, 98, 96, 101), '#b8b0a0')
    rect(d, (68, 58, 94, 80), '#8a6a4a')                         # 走廊墙上的小画
    rect(d, (70, 60, 92, 78), '#d8e8f0')
    poly(d, [(70, 78), (78, 66), (86, 74), (92, 70), (92, 78)], '#6a9a6a')
    rect(d, (106, 10, 112, KW_G), '#d8ccb4')                     # 门框
    line(d, (106, 10, 106, KW_G), '#e8decc')
    line(d, (112, 10, 112, KW_G), '#b8ac94')
    # ---------------- B 客厅（112–372）
    cx0, cy0, cx1, cy1 = KW_WINDOWS[0]
    rect(d, (cx0 + 2, cy0, cx1 - 2, cy1), (255, 255, 255))     # 蕾丝窗帘（半透）用抖动叠上去
    im.paste(kw_view(cx1 - cx0 + 1, cy1 - cy0 + 1, mode, seed=3), (cx0, cy0))
    a = np.array(im)
    for y in range(cy0, cy1 + 1):
        for x in range(cx0, cx1 + 1):
            if (x + y) % 3 == 0 or (y % 6 == 0 and x % 2 == 0):
                a[y, x, :3] = (a[y, x, :3] * .5 + np.array(c3('#f4f0e8')) * .5).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    rect(d, (159, cy0, 162, cy1), '#f6f4ee')
    for x0 in (cx0 - 10, cx1 - 2):                                # 两边的布窗帘
        rect(d, (x0, cy0 - 6, x0 + 12, cy1 + 10), '#c88a6a')
        for x in range(x0 + 2, x0 + 12, 4):
            line(d, (x, cy0 - 6, x, cy1 + 10), '#b0745a')
    rect(d, (cx0 - 14, cy0 - 9, cx1 + 14, cy0 - 7), '#b8a888')
    # 挂钟 8:30
    clock_face(d, 250, 58, 9, 8, 30, rim='#5a4a3e')
    line(d, (250, 47, 250, 48), '#5a4a3e')
    # 吊灯（扁圆）
    line(d, (244, 9, 244, 12), '#8a8a8a')
    ellipse(d, (230, 11, 258, 18), '#f8f4e8')
    line(d, (232, 17, 256, 17), '#d8d0c0')
    # 沙发（灰蓝）
    sx0, sx1 = 202, 292
    rect(d, (sx0 + 6, 92, sx1 - 6, 114), '#6a7e9a')
    line(d, (sx0 + 6, 92, sx1 - 6, 92), '#8ea0ba')
    for k in range(3):
        bx = sx0 + 8 + k * 25
        rect(d, (bx, 96, bx + 23, 112), '#748aa6')
        line(d, (bx + 23, 96, bx + 23, 112), '#5a6c86')
    rect(d, (sx0 + 6, 112, sx1 - 6, 122), '#7e94b0')
    line(d, (sx0 + 6, 112, sx1 - 6, 112), '#9cb0c8')
    rect(d, (sx0 + 4, 122, sx1 - 4, 128), '#5a6c86')
    for ax in (sx0, sx1 - 10):
        rect(d, (ax, 102, ax + 10, 128), '#6a7e9a')
        line(d, (ax + 1, 103, ax + 9, 103), '#8ea0ba')
    for lx in (sx0 + 4, sx1 - 7):
        rect(d, (lx, 128, lx + 3, KW_G - 1), '#4e3a2a')
    rect(d, (sx0 + 30, 102, sx0 + 42, 112), '#e8d0a0')          # 靠垫
    # 小边几 + 盆栽
    rect(d, (296, 112, 312, 114), '#8a6a4a')
    rect(d, (302, 114, 305, KW_G - 1), '#6a4e36')
    rect(d, (299, 104, 309, 112), '#c87a5a')
    for k in range(6):
        ellipse(d, (296 + k * 2, 90 + (k % 3) * 3, 304 + k * 2, 100 + (k % 3) * 3), ('#3e7a46', '#5a9a5a')[k % 2])
    # 电视柜 + 电视 + 录像机
    rect(d, (318, 106, 368, KW_G - 1), '#8a6a4a')
    line(d, (318, 106, 368, 106), '#aa8a66')
    line(d, (343, 108, 343, KW_G - 2), '#6a4e36')
    rect(d, (322, 118, 340, 124), '#2a2a2e')                     # 录像机
    for xx in range(324, 334, 3):
        px(d, xx, 121, '#6aa8e8')
    rect(d, (322, 80, 364, 106), '#b8bcc0')
    line(d, (322, 80, 364, 80), '#d8dce0')
    rect(d, (326, 84, 354, 102), '#1e2428')
    rect(d, (327, 85, 353, 101), '#2a343a')
    line(d, (329, 87, 336, 87), '#4a5860')
    for ky in (86, 92):
        rect(d, (357, ky, 361, ky + 3), '#8a8e92')
    # 地毯
    ellipse(d, (150, 146, 330, 172), '#b8806a')
    ellipse(d, (154, 148, 326, 170), '#c89478')
    ellipse(d, (180, 152, 300, 166), '#b8806a')
    rect(d, (372, 10, 380, KW_G), '#d8ccb4')                     # 客厅和餐厅之间的门框
    line(d, (372, 10, 372, KW_G), '#e8decc')
    line(d, (380, 10, 380, KW_G), '#b8ac94')
    # ---------------- C 餐厅厨房（380–520）
    rect(d, (384, 62, 410, KW_G - 1), '#e8e4d8')                 # 冰箱
    bevel(d, (384, 62, 410, KW_G - 1), '#f8f6ee', '#bcb8ac')
    line(d, (384, 88, 410, 88), '#bcb8ac')
    rect(d, (406, 70, 407, 82), '#9a968c')
    rect(d, (406, 94, 407, 112), '#9a968c')
    rect(d, (390, 72, 396, 78), '#e87a5a')                       # 冰箱贴、便条
    rect(d, (396, 96, 402, 104), '#f8f0a0')
    for x0, x1 in ((414, 448), (492, 516)):                      # 吊柜
        rect(d, (x0, 46, x1, 74), '#e0d4bc')
        bevel(d, (x0, 46, x1, 74), '#f0e6d0', '#b8ac94')
        mx = (x0 + x1) // 2
        line(d, (mx, 46, mx, 74), '#b8ac94')
        rect(d, (mx - 3, 68, mx - 2, 72), '#9a8a6a')
        rect(d, (mx + 2, 68, mx + 3, 72), '#9a8a6a')
    rect(d, (414, 100, 516, KW_G - 1), '#e0d4bc')                 # 流理台
    rect(d, (412, 97, 518, 100), '#b8b4ac')
    line(d, (412, 97, 518, 97), '#d8d4cc')
    for x in range(414, 516, 17):
        rect(d, (x + 1, 103, x + 15, KW_G - 4), '#e8dcc4')
        bevel(d, (x + 1, 103, x + 15, KW_G - 4), '#f4ead6', '#bcae92')
        rect(d, (x + 6, 106, x + 10, 107), '#9a8a6a')
    rect(d, (458, 94, 482, 97), '#9aa0a8')                       # 水槽 + 水龙头
    line(d, (470, 86, 470, 94), '#a8acb4')
    line(d, (470, 86, 474, 86), '#a8acb4')
    rect(d, (494, 93, 512, 97), '#3a3a3e')                       # 灶台 + 锅
    rect(d, (498, 86, 508, 93), '#8a9aa8')
    line(d, (508, 88, 514, 87), '#3a3a3e')
    line(d, (432, 9, 432, 24), '#6a6a6a')                        # 餐桌吊灯
    poly(d, [(424, 24), (440, 24), (444, 32), (420, 32)], '#e8c890')
    line(d, (420, 32, 444, 32), '#c8a870')
    rect(d, (392, 110, 474, 113), '#9a7454')                     # 餐桌 + 两把椅子
    line(d, (392, 110, 474, 110), '#ba9472')
    for lx in (396, 468):
        rect(d, (lx, 113, lx + 3, KW_G - 1), '#7a5a40')
    for chx in (384, 476):
        rect(d, (chx, 98, chx + 3, KW_G - 1), '#7a5a40')
        rect(d, (chx, 98, chx + 10, 101), '#8a6a4a')
        rect(d, (chx, 118, chx + 12, 120), '#8a6a4a')
        rect(d, (chx + 10, 120, chx + 12, KW_G - 1), '#7a5a40')
    rect(d, (430, 104, 448, 110), '#f4f0e6')                     # 桌上的报纸
    line(d, (432, 106, 446, 106), '#9a9a9e')
    rect(d, (520, 10, 528, KW_G), '#d8ccb4')                     # 早人房间的门框
    line(d, (520, 10, 520, KW_G), '#e8decc')
    line(d, (528, 10, 528, KW_G), '#b8ac94')
    # ---------------- D 早人的房间（528–640）
    rect(d, (534, 60, 578, 62), '#9a7a5a')                       # 墙上的搁板 + 录像带
    for k, x in enumerate(range(536, 576, 5)):
        rect(d, (x, 50, x + 3, 59), '#1e1e22')
        rect(d, (x, 52, x + 3, 55), '#f4f0e4' if k % 3 else '#e8c860')
    rect(d, (540, 70, 568, 92), '#3a5a8a')                       # 海报（星空）
    for k in range(10):
        px(d, 543 + (k * 7) % 22, 73 + (k * 5) % 16, '#f4f0d8')
    ellipse(d, (556, 78, 564, 86), '#e8d8a0')
    rect(d, (534, 102, 578, 105), '#c8a878')                     # 书桌
    line(d, (534, 102, 578, 102), '#e0c498')
    rect(d, (536, 105, 540, KW_G - 1), '#a8885e')
    rect(d, (556, 105, 576, 128), '#b89868')
    line(d, (556, 116, 576, 116), '#9a7a50')
    rect(d, (574, 128, 576, KW_G - 1), '#a8885e')
    line(d, (562, 101, 566, 88), '#3a5a8a')                      # 台灯
    poly(d, [(560, 86), (570, 86), (572, 92), (558, 92)], '#4a7ab8')
    rect(d, (544, 96, 554, 102), '#2a2a30')                      # 小摄像机（早人的）
    rect(d, (540, 97, 544, 101), '#4a4a50')
    px(d, 552, 97, '#e83a34')
    rect(d, (584, 112, 640, 124), '#e8e4dc')                     # 床
    rect(d, (584, 108, 640, 120), '#4a7ab8')
    line(d, (584, 108, 640, 108), '#6a9ad0')
    for x in range(590, 640, 8):
        line(d, (x, 110, x + 4, 110), '#5a8ac4')
    rect(d, (626, 102, 640, 110), '#f4f0e6')
    rect(d, (584, 124, 640, KW_G - 1), '#a8885e')
    rect(d, (582, 100, 586, KW_G - 1), '#a8885e')
    x0, y0, x1, y1 = KW_WINDOWS[2]
    for xc in (x0 - 6, x1 - 4):                                  # 早人房间的蓝窗帘
        rect(d, (xc, y0 - 4, xc + 10, y1 + 6), '#5a7ab0')
        line(d, (xc + 4, y0 - 4, xc + 4, y1 + 6), '#4a6a9c')
    # 地面：玄关是瓷砖（低一阶），其余木地板，厨房是地砖
    im = liv_floor(im, 0, W, KW_G)
    im = liv_kitchen_floor(im, 380, 520, KW_G)
    d = ImageDraw.Draw(im)
    rect(d, (0, KW_G, 58, H), '#9a968c')
    for y in range(KW_G + 4, H, 8):
        line(d, (0, y, 58, y), '#86827a')
    for x in range(8, 58, 14):
        line(d, (x, KW_G, x - 4, H), '#86827a')
    rect(d, (58, KW_G, 62, H), '#7a5a40')                         # 上がり框（玄关和走廊的台阶）
    line(d, (62, KW_G, 62, H), '#5a3e2c')
    for x in (380, 520):
        line(d, (x, KW_G, x, H), '#8a7a62')
    rect(d, (14, 140, 26, 146), '#2a2a2e')                       # 玄关的一双皮鞋
    rect(d, (28, 141, 40, 146), '#2a2a2e')
    line(d, (14, 140, 26, 140), '#4a4a4e')
    return im


def kw_cam():
    """天花板右角的小摄像机（机身）+ 红灯闪（2 帧）"""
    cam = new(640, H)
    d = ImageDraw.Draw(cam)
    rect(d, (362, 9, 370, 11), '#5a5a5e')
    rect(d, (360, 11, 370, 16), '#2a2a2e')
    line(d, (360, 11, 370, 11), '#4a4a50')
    rect(d, (357, 12, 360, 15), '#1a1a1e')
    px(d, 358, 13, '#6a8ab8')
    led = new(6, 3)
    ld = ImageDraw.Draw(led)
    px(ld, 1, 1, '#ff3a30')
    px(ld, 0, 1, '#a82a24'); px(ld, 2, 1, '#a82a24'); px(ld, 1, 0, '#a82a24'); px(ld, 1, 2, '#a82a24')
    return cam, led


def kawajiri_house():
    W = 640
    day = kw_room('day')
    win = lambda im: comp(*[only(im, (x0 - 14, y0 - 9, x1 + 15, y1 + 11)) for x0, y0, x1, y1 in KW_WINDOWS])
    dusk = win(kw_room('dusk'))
    nroom = kw_room('night')
    night = comp(win(nroom), only(nroom, (10, 54, 53, KW_G)))
    f = np.zeros((H, W))
    for x, y, rx, ry, k in KW_LAMPS:
        f = np.maximum(f, radial(W, H, x, y, rx, ry, 1.4, k))
    glow = glow_from_field(f * .55, '#ffd28a', levels=6)
    cam, led = kw_cam()
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(front_door=[32, 146], door_glass=[24, 90], genkan=[30, 158], step_x=60, shoe_rack=[81, 146],
                             hall=[84, 146], hall_wall=[80, 70], living_door=[109, 146], window=[161, 146],
                             window_glass=[161, 77], clock=[250, 58], ceiling_lamp=[244, 15], sofa=[247, 146],
                             plant=[304, 146], tv=[343, 146], tv_screen=[340, 93], vcr=[331, 121], cam=[364, 13],
                             cam_corner=[370, 9], kitchen_door=[376, 146], fridge=[397, 146], dining_table=[433, 146],
                             tea=[440, 108], sink=[470, 146], stove=[503, 146], kitchen_window=[470, 68],
                             hayato_door=[524, 146], hayato_desk=[556, 146], hayato_tapes=[556, 55], hayato_cam=[548, 99],
                             hayato_bed=[612, 146], hayato_window=[613, 72],
                             hall_x=[0, 106], living_x=[112, 372], kitchen_x=[380, 520], hayato_x=[528, 640],
                             walk_x=[8, 632]),
                layers=[{'type': 'pano', 'image': 'bg/kawajiri_house/room', 'k': 1, 'x': 0, 'y': 0},
                        layer('kawajiri_house', 'win_dusk', key='dusk'),
                        layer('kawajiri_house', 'win_night', key='night'),
                        layer('kawajiri_house', 'cam', key='cam'),
                        {'type': 'tint', 'color': '#fff2d8', 'alpha': 0.10, 'key': 'morning'},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.18, 'key': 'dusk'},
                        {'type': 'tint', 'color': '#0c1430', 'alpha': 0.50, 'key': 'night'},
                        {'type': 'glow', 'image': 'bg/kawajiri_house/glow', 'k': 1, 'x': 0, 'y': 0, 'key': 'night'},
                        {'type': 'strip', 'image': 'bg/kawajiri_house/led', 'n': 2, 'fps': 1.5, 'x': 362, 'y': 12, 'k': 1,
                         'key': 'cam'}],
                fg=[])
    # 预览：白天一张；傍晚、夜各拼一张（罩色在预览里用简单混色近似）
    def tinted(base, col, a):
        arr = np.array(base).astype(float)
        arr[..., :3] = arr[..., :3] * (1 - a) + np.array(c3(col)) * a
        return Image.fromarray(arr.astype(np.uint8), 'RGBA')
    pd = tinted(comp(day, dusk, cam), '#ff8a3a', .18)
    pn = tinted(comp(day, night, cam), '#0c1430', .5)
    pa, ga = np.array(pn).astype(int), np.array(glow).astype(int)
    pa[..., :3] = np.clip(pa[..., :3] + ga[..., :3], 0, 255)
    pn = Image.fromarray(pa.astype(np.uint8), 'RGBA')
    preview('kawajiri_house_dusk', {'room': pd}, ['room'], W)
    preview('kawajiri_house_night', {'room': pn}, ['room'], W)
    return save('kawajiri_house', {'room': day, 'win_dusk': dusk, 'win_night': night, 'glow': glow, 'cam': cam, 'led': led},
                meta, comp(day, cam))



# ============================================================ 杜王车站前广场 morioh_station（960 宽，七月白天）
#   左：出租车站（站牌 + 一辆等客的出租车）→ 车站楼（「杜王駅」大招牌、钟、玻璃门里一排自动检票机和售票机）→
#   广场（两张长椅、绿树、广场钟、电话亭、公交站）→ 一栋带咖啡馆的三层楼（楼上的窗：第 13 战掉玻璃的地方）→
#   右：路口（人行横道、红绿灯；第 13 战结尾少年冲上马路，卡车从这条路开过来）。
MS_G = 134


def ms_far(w):
    far = sky_far(w, seed=33, sea=False, cols=('#5c9ce8', '#80b4ee', '#a8ccf2', '#d0e4f6'))
    d = ImageDraw.Draw(far)
    rng = np.random.RandomState(34)
    x = 0
    while x < w:                                                    # 远处的楼（比序章的屋顶高一些：车站一带是镇中心）
        bw, bh = rng.randint(18, 40), rng.randint(20, 56)
        col = ['#c8ccd4', '#d8d4cc', '#b8c0cc', '#e0dcd4'][rng.randint(4)]
        rect(d, (x, 120 - bh, x + bw, 130), col)
        line(d, (x, 120 - bh, x + bw, 120 - bh), mix(col, '#ffffff', .3))
        for wy in range(120 - bh + 4, 118, 6):
            for wx in range(x + 3, x + bw - 3, 5):
                px(d, wx, wy, '#8ea4b8')
                px(d, wx + 1, wy, '#8ea4b8')
        x += bw + rng.randint(0, 6)
    return far


def taxi(im, x, g, body='#e8c030'):
    """出租车（侧面，车头朝右）"""
    d = ImageDraw.Draw(im)
    rect(d, (x, g - 14, x + 50, g - 5), body)
    poly(d, [(x + 10, g - 14), (x + 15, g - 23), (x + 36, g - 23), (x + 42, g - 14)], body)
    poly(d, [(x + 13, g - 14), (x + 17, g - 21), (x + 25, g - 21), (x + 25, g - 14)], '#5a7088')
    poly(d, [(x + 27, g - 14), (x + 27, g - 21), (x + 35, g - 21), (x + 39, g - 14)], '#5a7088')
    line(d, (x, g - 10, x + 50, g - 10), mix(body, '#000000', .25))
    rect(d, (x + 22, g - 27, x + 30, g - 23), '#f4f0e4')
    rect(d, (x + 48, g - 13, x + 50, g - 11), '#f8f0c0')
    rect(d, (x, g - 13, x + 2, g - 11), '#d84a3a')
    for wx in (x + 10, x + 40):
        ellipse(d, (wx - 5, g - 10, wx + 5, g), '#1e1e22')
        ellipse(d, (wx - 2, g - 7, wx + 2, g - 3), '#8a8a90')
    return im


def bench(im, x, g):
    d = ImageDraw.Draw(im)
    rect(d, (x, g - 10, x + 30, g - 8), '#8a5a3a')
    rect(d, (x, g - 18, x + 30, g - 16), '#8a5a3a')
    rect(d, (x, g - 14, x + 30, g - 13), '#7a4e32')
    for lx in (x + 2, x + 26):
        rect(d, (lx, g - 18, lx + 2, g), '#4a4a50')
    line(d, (x, g - 10, x + 30, g - 10), '#a87450')
    return im


def traffic_light(im, x, g):
    d = ImageDraw.Draw(im)
    rect(d, (x, g - 78, x + 2, g), '#6a6a70')
    rect(d, (x - 2, g - 80, x + 24, g - 72), '#3a3a40')
    for k, c in enumerate(('#4ac8a0', '#5a5a4a', '#5a3a3a')):
        ellipse(d, (x + k * 8 - 1, g - 79, x + k * 8 + 5, g - 73), c)
    rect(d, (x + 4, g - 52, x + 12, g - 38), '#3a3a40')               # 行人灯
    rect(d, (x + 6, g - 50, x + 10, g - 46), '#5a3a3a')
    rect(d, (x + 6, g - 44, x + 10, g - 40), '#4ac8a0')
    return im


def ms_near():
    W = 960
    im = new(W, H)
    d = ImageDraw.Draw(im)
    # ---------------- 车站楼（96–440）
    S0, S1, ST = 96, 440, 30
    rect(d, (S0, ST, S1, MS_G), '#e8e2d6')
    for yy in range(ST + 3, MS_G, 4):
        line(d, (S0, yy, S1, yy), '#ddd6c8')
    rect(d, (S0 - 2, ST - 4, S1 + 2, ST), '#8a9098')
    line(d, (S0 - 2, ST - 4, S1 + 2, ST - 4), '#b0b6be')
    for wx in range(S0 + 10, S1 - 20, 30):                            # 二楼的窗
        window(d, (wx, ST + 4, wx + 22, ST + 16), frame='#f4f2ec', glass=('#8cb4d0', '#bcd6e6'))
    rect(d, (S0 + 20, 50, S1 - 20, 66), '#1e3a6a')                    # 大招牌
    line(d, (S0 + 20, 50, S1 - 20, 50), '#3a5a8a')
    line(d, (S0 + 20, 66, S1 - 20, 66), '#142a50')
    tw, th = kanji_size('杜王駅')
    kanji(im, 200 - tw // 2, 52, '杜王駅', '#ffffff')
    d = ImageDraw.Draw(im)
    letters(d, 300 - text_w('MORIOH STATION') // 2, 55, 'MORIOH STATION', '#e8eef8')
    rect(d, (S0 + 20, 70, S1 - 20, 73), '#c8c2b4')                    # 雨棚
    for x in range(S0 + 20, S1 - 20, 6):
        px(d, x, 73, '#a8a294')
    # 一楼：玻璃立面，里面是检票口
    rect(d, (S0 + 8, 76, S1 - 8, MS_G - 1), '#3a4a5a')
    im = grad(im, (S0 + 8, 76, S1 - 8, MS_G - 1), ('#8aa4b8', '#6e889c', '#5a7286'))
    d = ImageDraw.Draw(im)
    rect(d, (S0 + 12, 82, S0 + 60, 96), '#2a3240')                    # 运费表（线路图）
    line(d, (S0 + 14, 88, S0 + 58, 88), '#e8c040')
    line(d, (S0 + 14, 91, S0 + 58, 91), '#4ab4e8')
    for x in range(S0 + 16, S0 + 58, 6):
        px(d, x, 88, '#ffffff')
    for k in range(4):                                                 # 售票机
        x = S0 + 12 + k * 12
        rect(d, (x, 104, x + 10, MS_G - 2), '#d8dce0')
        rect(d, (x + 2, 107, x + 8, 113), '#2a4a5a')
        rect(d, (x + 2, 116, x + 8, 117), '#e8a040')
    for k in range(6):                                                 # 自动检票机
        x = 192 + k * 22
        rect(d, (x, 112, x + 8, MS_G - 2), '#c8ccd4')
        rect(d, (x, 110, x + 8, 112), '#e8b040' if k % 2 else '#4a8ad8')
        line(d, (x, 112, x, MS_G - 2), '#e8ecf0')
        rect(d, (x + 2, 114, x + 6, 116), '#2a3a48')
    rect(d, (186, 84, 330, 94), '#2a3240')                             # 改札上面的电子屏
    letters(d, 192, 87, 'JR', '#4ac860')
    for x in range(204, 326, 8):
        rect(d, (x, 87, x + 5, 91), '#e8a040' if x % 3 else '#e8e0d0')
    rect(d, (350, 88, 420, MS_G - 2), '#4a5a6a')                       # 站台方向的通道（深处）
    line(d, (350, 88, 420, 88), '#8aa0b4')
    for x in range(S0 + 8, S1 - 8, 48):                                # 玻璃立面的竖框
        rect(d, (x, 76, x + 2, MS_G - 1), '#c8ccd4')
    for x in range(S0 + 10, S1 - 10, 9):
        line(d, (x, 78, x + 4, 82), '#c8dcec')
    clock_face(d, 418, 42, 8, 2, 40, rim='#5a6068', face='#f8f8f4')    # 车站的钟（下午 2:40）
    # ---------------- 出租车站（0–96）
    rect(d, (0, 84, 96, MS_G), '#d4cfc4')                              # 车站楼侧翼（矮）
    rect(d, (0, 80, 96, 84), '#8a9098')
    for wx in (10, 50):
        window(d, (wx, 92, wx + 28, 108), frame='#f4f2ec', glass=('#8cb4d0', '#bcd6e6'))
    rect(d, (80, 98, 82, MS_G), '#6a6a70')                             # 出租车站牌
    rect(d, (70, 88, 92, 98), '#e8e8e4')
    rect(d, (70, 88, 92, 90), '#d84a3a')
    letters(d, 73, 92, 'TAXI', '#2a2a30')
    # ---------------- 广场（440–700）：树、长椅、广场钟、电话亭、公交站
    im = green_tree(im, 500, MS_G - 4, 96, 70, seed=36)
    im = green_tree(im, 640, MS_G - 4, 88, 64, seed=37)
    d = ImageDraw.Draw(im)
    for tx in (500, 640):                                              # 树池
        rect(d, (tx - 14, MS_G - 6, tx + 14, MS_G), '#a8a49a')
        line(d, (tx - 14, MS_G - 6, tx + 14, MS_G - 6), '#c8c4ba')
    rect(d, (568, 52, 571, MS_G), '#5a6068')                          # 广场钟
    clock_face(d, 569, 60, 7, 2, 40, rim='#5a6068', face='#f8f8f4')
    im = phone_booth(im, 680, MS_G)
    im = bus_stop(im, 448, MS_G, roof_col='#3a6a9a')
    # 背景墙：广场后面是一排低矮的店（只到 y 90）
    # ---------------- 三层楼 + 咖啡馆（700–792）
    B0, B1 = 702, 792
    rect(d, (B0, 20, B1, MS_G), '#d8c8b0')
    for yy in range(23, MS_G, 3):
        line(d, (B0, yy, B1, yy), '#cfbea4')
    rect(d, (B0 - 2, 16, B1 + 2, 20), '#9a8a74')
    for fy in (26, 54):                                                # 二三楼的大玻璃窗
        for wx in (B0 + 6, B0 + 36, B0 + 64):
            rect(d, (wx, fy, wx + 22, fy + 20), '#f4f0e8')
            rect(d, (wx + 1, fy + 1, wx + 21, fy + 19), '#8cb4d0')
            for gx in range(wx + 2, wx + 20, 5):
                line(d, (gx, fy + 2, gx + 3, fy + 5), '#c8e0f0')
            line(d, (wx + 11, fy, wx + 11, fy + 20), '#f4f0e8')
    rect(d, (B0, 82, B1, 94), '#2e5a3a')                              # 咖啡馆招牌 + 遮阳篷
    tw, th = kanji_size('喫茶')
    kanji(im, (B0 + B1) // 2 - tw // 2, 82, '喫茶', '#f4e8c8')
    d = ImageDraw.Draw(im)
    for i in range(8):
        for x in range(B0 - i // 3, B1 + i // 3 + 1):
            px(d, x, 95 + i, ('#2e5a3a', '#f4f0e6')[((x - B0) // 6) % 2])
    rect(d, (B0 + 6, 104, B1 - 22, MS_G - 2), '#6a5a48')
    rect(d, (B0 + 8, 106, B1 - 24, MS_G - 4), '#a8c4d0')
    line(d, (B0 + 8, 116, B1 - 24, 116), '#6a5a48')
    rect(d, (B1 - 18, 104, B1 - 4, MS_G - 1), '#5a3e2c')
    px(d, B1 - 7, 120, '#e8c860')
    # ---------------- 路口（792–960）：对面的人行道和楼、红绿灯
    rect(d, (796, 112, W, 124), '#b8b4ac')                             # 对面的人行道（远）
    for k, (x, bw, bh, col) in enumerate(((800, 46, 64, '#e4dccc'), (850, 52, 80, '#c8ccd4'), (906, 54, 58, '#e8d8c0'))):
        rect(d, (x, 112 - bh, x + bw, 112), col)
        rect(d, (x - 1, 112 - bh - 3, x + bw + 1, 112 - bh), mix(col, '#000000', .3))
        for wy in range(112 - bh + 6, 104, 12):
            for wx in range(x + 5, x + bw - 6, 11):
                rect(d, (wx, wy, wx + 6, wy + 6), '#8cb4d0')
        rect(d, (x + 6, 98, x + bw - 6, 112), mix(col, '#000000', .2))
    rect(d, (796, 124, W, MS_G), '#5a5a62')                            # 横着的车道（远处那一段）
    for x in range(796, W, 16):
        rect(d, (x, 128, x + 8, 129), '#e8e4d8')
    # ---------------- 地面：广场铺砖 + 出租车道 + 右边路口的柏油路和人行横道
    im = paving(im, 0, 796, MS_G, H)
    im = asphalt(im, 0, 64, MS_G + 6, H, dash=False)
    im = asphalt(im, 796, W, MS_G, H, dash=False)
    d = ImageDraw.Draw(im)
    rect(d, (0, MS_G + 4, 64, MS_G + 6), '#a8a49c')                   # 出租车道的路缘
    rect(d, (64, MS_G + 4, 66, H), '#a8a49c')
    for y in range(MS_G + 10, H, 12):                                  # 出租车道的停车格
        line(d, (4, y, 60, y), '#e8e4d8')
    rect(d, (792, MS_G, 796, H), '#b8b4ac')                            # 路缘石
    line(d, (796, MS_G, 796, H), '#7a7670')
    for k, x in enumerate(range(808, 950, 14)):                        # 人行横道（往画面里伸）
        rect(d, (x, MS_G + 4, x + 7, H), '#ecead8')
    line(d, (796, MS_G + 2, W, MS_G + 2), '#e8e4d8')
    im = traffic_light(im, 800, MS_G + 2)
    im = taxi(im, 8, H - 18)
    im = bench(im, 470, 158)
    im = bench(im, 600, 158)
    return im


def paving(im, x0, x1, y0, y1):
    """广场的交错铺砖（越往下砖越大）"""
    d = ImageDraw.Draw(im)
    y, h, row = y0, 4.0, 0
    while y < y1:
        yb = min(y1, int(round(y + h)))
        tw = int(10 + h * 2)
        for i, x in enumerate(range(x0 - (row % 2) * tw // 2, x1, tw)):
            col = ('#c8beb0', '#bcb2a2', '#d2c8ba')[(i + row) % 3]
            rect(d, (max(x0, x), int(y), min(x1 - 1, x + tw - 1), yb - 1), col)
            line(d, (max(x0, x), int(y), max(x0, x), yb - 1), '#a49a8a')
        line(d, (x0, yb - 1, x1 - 1, yb - 1), '#a49a8a')
        y += h
        h = min(11.0, h * 1.2)
        row += 1
    return im


def morioh_station():
    W = 960
    far = ms_far(640)
    near = ms_near()
    meta = dict(pack=PACK, w=W, ground=150, walk=[142, 176],
                anchors=dict(taxi=[34, 160], taxi_sign=[81, 146], station_door=[268, 146], gates=[248, 146],
                             ticket_machines=[126, 146], sign=[268, 58], station_clock=[418, 42], bus_stop=[460, 146],
                             bench1=[485, 158], bench2=[615, 158], tree1=[500, 146], tree2=[640, 146], plaza_clock=[569, 60],
                             phone=[688, 146], cafe=[730, 146], cafe_door=[781, 146], glass=[747, 64], glass_drop=[747, 150],
                             curb_x=794, crosswalk=[880, 160], road=[880, 160], signal=[801, 146],
                             plaza_x=[96, 792], walk_x=[8, 952]),
                layers=[{'type': 'pano', 'image': 'bg/morioh_station/far', 'k': 0.5, 'x': 0, 'y': 0},
                        {'type': 'pano', 'image': 'bg/morioh_station/near', 'k': 1, 'x': 0, 'y': 0},
                        {'type': 'tint', 'color': '#ff8a3a', 'alpha': 0.16, 'key': 'pm'}],
                fg=[])
    pv = comp(far.resize((W, H), Image.NEAREST), near)
    return save('morioh_station', {'far': far, 'near': near}, meta, pv)


SCENES = {'kira_house_out': kira_house_out, 'kira_house': kira_house, 'kawajiri_house': kawajiri_house, 'morioh_station': morioh_station}


def main(keys):
    path = os.path.join(LIB.META, 'bg_ch8.json')
    meta = LIB.load_json(path, {}) or {}
    for k in keys or SCENES:
        meta[k] = SCENES[k]()
        print('背景', k)
    LIB.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
