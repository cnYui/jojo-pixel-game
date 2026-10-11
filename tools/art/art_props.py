"""M1 新道具：只使用整数像素，状态帧由剧情选择，不自动播放。"""
import sys
sys.dont_write_bytecode = True

import math
import numpy as np
from PIL import Image, ImageDraw
import art_common as AC
from engine import bg_asia as A

K = AC.OUTLINE_RGB


def spec(pid, frames, w, h, desc):
    return dict(id=pid, frames=frames, size=[w, h], pivot=[w // 2, h],
                fps=0, kind='static', desc=desc)


PROPS = [
    spec('magazine', 1, 10, 7, '漫画周刊，保留独立名字供序章调查'),
    spec('jail_pipe', 2, 16, 48, '完好的水管与阀门 / 管口爆开；水流由像素特效叠加'),
    spec('tissue', 1, 10, 8, '花京院递出的皱纸巾'),
    spec('pen', 1, 9, 3, '校医使用的钢笔'),
    spec('pinky', 1, 4, 5, '乔瑟夫皮手套色义手小指'),
    spec('hk_table', 2, 48, 20, '圆桌与四凳 / 桌面时钟；火焰由像素特效叠加'),
    spec('mr_statue', 3, 24, 40, '虎像 / 红色魔术师像 / 碎石；虎像从原画等比缩至24像素宽'),
    spec('chariot_armor', 4, 8, 8, '肩甲 / 胸甲 / 头盔 / 护腿'),
    spec('dish', 3, 8, 5, '青蛙 / 整鱼 / 不明食物'),
    spec('kite', 1, 8, 8, '香港街头的小风筝'),
]


def canvas(w, h):
    im = Image.new('RGBA', (w, h))
    return im, ImageDraw.Draw(im)


def draw_magazine(frame):
    im, d = canvas(10, 7)
    d.rectangle((0, 0, 9, 6), fill=(248, 230, 176), outline=K)
    d.rectangle((2, 1, 8, 2), fill=(204, 48, 66))
    d.rectangle((3, 3, 6, 5), fill=(60, 108, 156))
    d.line((1, 1, 1, 5), fill=(164, 132, 100))
    d.point((7, 4), fill=(250, 244, 210))
    return im


def draw_jail_pipe(frame):
    im, d = canvas(16, 48)
    d.rectangle((6, 1, 10, 47), fill=(104, 122, 136), outline=K)
    d.line((7, 2, 7, 46), fill=(192, 202, 204))
    for y in (8, 36):
        d.rectangle((4, y, 12, y + 3), fill=(132, 144, 152), outline=K)
        d.line((5, y + 1, 11, y + 1), fill=(210, 212, 208))
    d.line((9, 22, 13, 22), fill=(140, 148, 154), width=2)
    d.ellipse((10, 18, 15, 25), fill=(136, 52, 54), outline=K)
    d.line((12, 19, 12, 24), fill=(204, 84, 70))
    d.line((11, 21, 14, 21), fill=(204, 84, 70))
    if frame == 1:
        d.rectangle((5, 11, 11, 17), fill=(0, 0, 0, 0))
        d.polygon([(5, 11), (2, 9), (4, 15), (7, 17), (8, 14)], fill=(164, 182, 192), outline=K)
        d.polygon([(9, 14), (13, 11), (14, 15), (10, 18), (8, 17)], fill=(136, 158, 172), outline=K)
        d.line((6, 17, 10, 17), fill=(26, 36, 48))
    return im


def draw_tissue(frame):
    im, d = canvas(10, 8)
    d.polygon([(1, 1), (5, 0), (8, 2), (9, 6), (6, 7), (3, 6), (0, 4)],
              fill=(244, 244, 236), outline=(136, 144, 160))
    d.line((2, 2, 4, 4, 2, 5), fill=(190, 196, 210))
    d.line((6, 2, 5, 5, 7, 6), fill=(204, 208, 220))
    return im


def draw_pen(frame):
    im, d = canvas(9, 3)
    d.line((0, 1, 7, 1), fill=K, width=3)
    d.line((2, 0, 6, 0), fill=(72, 82, 114))
    d.point((1, 0), fill=(238, 200, 104))
    d.point((8, 1), fill=(220, 210, 168))
    return im


def draw_pinky(frame):
    im, d = canvas(4, 5)
    d.rounded_rectangle((0, 0, 3, 4), radius=1, fill=(158, 112, 68), outline=K)
    d.line((1, 1, 1, 3), fill=(212, 166, 110))
    d.point((2, 3), fill=(98, 64, 50))
    return im


def draw_hk_table(frame):
    im, d = canvas(48, 20)
    for x, y in ((2, 8), (36, 8), (8, 14), (31, 14)):
        d.rectangle((x + 1, y + 2, x + 2, 19), fill=(122, 36, 40), outline=K)
        d.rectangle((x + 6, y + 2, x + 7, 19), fill=(122, 36, 40), outline=K)
        d.ellipse((x, y, x + 9, y + 4), fill=(222, 74, 62), outline=K)
        d.line((x + 2, y + 1, x + 6, y + 1), fill=(248, 118, 84))
    d.rectangle((20, 6, 27, 18), fill=(112, 102, 94), outline=K)
    d.ellipse((14, 16, 32, 19), fill=(90, 86, 88), outline=K)
    d.ellipse((6, 0, 41, 11), fill=(220, 216, 192), outline=K)
    d.arc((8, 1, 39, 9), 185, 350, fill=(250, 246, 220))
    if frame:
        import math
        d.ellipse((9, 1, 38, 10), fill=(126, 84, 58), outline=(62, 44, 46))
        for i in range(12):
            a = i * math.tau / 12
            x, y = round(23.5 + math.sin(a) * 12), round(5.5 - math.cos(a) * 3.5)
            d.point((x, y), fill=(248, 166, 66))
        d.line((23, 6, 23, 2), fill=(250, 224, 154))
        d.line((23, 6, 32, 7), fill=(250, 224, 154))
        d.point((23, 6), fill=K)
    return im


def draw_mr_statue(frame):
    im, d = canvas(24, 40)
    stone, dark = (166, 136, 110), (84, 70, 70)
    if frame == 0:
        original = Image.new('RGBA', (57, 45))
        A._tiger_statue(ImageDraw.Draw(original), 26, 44)
        # 原虎像宽57px；等比缩小保留全身轮廓，不裁掉头尾。
        fitted = original.resize((24, 19), Image.Resampling.NEAREST)
        im.alpha_composite(fitted, (0, 21))
    elif frame == 1:
        d.polygon([(2, 39), (4, 33), (19, 33), (22, 39)], fill=stone, outline=K)
        d.polygon([(7, 33), (7, 21), (4, 17), (6, 13), (10, 15), (17, 14), (20, 19), (17, 24), (17, 33)],
                  fill=(180, 70, 50), outline=K)
        d.rectangle((8, 24, 10, 34), fill=(206, 106, 68), outline=K)
        d.rectangle((14, 24, 17, 34), fill=(150, 58, 48), outline=K)
        d.polygon([(7, 15), (8, 8), (11, 3), (17, 2), (20, 7), (18, 12), (15, 15)],
                  fill=(220, 108, 60), outline=K)
        d.polygon([(16, 5), (22, 7), (18, 9), (18, 12), (13, 12)], fill=(238, 194, 100), outline=K)
        d.line((9, 5, 12, 2, 17, 1), fill=(244, 176, 86), width=2)
        d.point((17, 5), fill=(250, 238, 166))
        d.line((8, 17, 7, 23), fill=(238, 152, 82), width=2)
        d.line((17, 18, 19, 22), fill=(112, 44, 44), width=2)
        d.line((11, 17, 14, 21), fill=(242, 188, 112))
    else:
        for points, col in [([(1,39),(3,34),(9,37),(8,39)], stone),
                            ([(11,39),(10,32),(14,30),(17,37)], (190,84,58)),
                            ([(17,39),(19,34),(23,36),(22,39)], dark),
                            ([(5,32),(6,27),(11,28),(9,33)], (212,120,72)),
                            ([(16,29),(18,26),(21,29),(18,32)], stone)]:
            d.polygon(points, fill=col, outline=K)
        d.point((2, 31), fill=dark)
        d.point((14, 36), fill=(240, 166, 100))
    return im


def draw_chariot_armor(frame):
    im, d = canvas(8, 8)
    silver, shade, hi = (168, 182, 202), (92, 110, 140), (236, 240, 246)
    shapes = [[(0,4),(2,1),(5,0),(7,3),(6,6),(2,7)],
              [(1,0),(6,0),(7,4),(5,7),(2,7),(0,4)],
              [(1,5),(1,2),(3,0),(5,0),(7,3),(6,6),(3,7)],
              [(2,0),(5,0),(5,4),(7,6),(6,7),(1,7),(1,5)]]
    d.polygon(shapes[frame], fill=silver, outline=K)
    d.line((2, 2, 5, 2), fill=hi)
    d.line((5, 3, 5, 5), fill=shade)
    if frame == 2:
        d.line((2, 4, 6, 4), fill=K)
    elif frame == 1:
        d.line((3, 3, 4, 6), fill=hi)
    return im


def draw_dish(frame):
    im, d = canvas(8, 5)
    d.ellipse((0, 2, 7, 4), fill=(238, 232, 212), outline=(110, 112, 130))
    if frame == 0:
        d.ellipse((2, 1, 5, 3), fill=(100, 144, 58), outline=K)
        d.point((2, 0), fill=(140, 184, 80))
        d.point((5, 0), fill=(140, 184, 80))
    elif frame == 1:
        d.ellipse((1, 1, 5, 3), fill=(110, 154, 174), outline=K)
        d.polygon([(5,2),(7,0),(7,3)], fill=(108, 144, 162))
        d.point((2, 2), fill=(244, 234, 200))
    else:
        d.polygon([(1,2),(2,0),(4,1),(5,0),(6,3),(3,3)], fill=(158, 100, 56), outline=K)
        d.point((3, 1), fill=(218, 164, 78))
    return im


def draw_kite(frame):
    im, d = canvas(8, 8)
    d.polygon([(3,0),(6,3),(3,6),(0,3)], fill=(220, 66, 72), outline=K)
    d.polygon([(3,1),(5,3),(3,5)], fill=(246, 194, 72))
    d.line((1,3,5,3), fill=(244, 226, 166))
    d.line((3,1,3,5), fill=(244, 226, 166))
    d.line((3,6,4,7,6,7), fill=(140, 160, 194))
    return im


import art_props_later
PROPS += art_props_later.install(globals(), spec)


# =====================================================================================
#  第2章（南海：冒牌船长 / 暗蓝之月、无人货轮 / 力量）新道具（2026-10-10）
# =====================================================================================
# 船都朝右、pivot = 底边中点。lifeboat / rusty_boat 只画近侧船身：人物画在船后面（先画人、后画船），船身挡住腰以下。
PROPS += [
    dict(spec('lifeboat', 1, 112, 22,
              '救生艇近侧船身（白舷缘 + 橙船身 + 下垂护舷绳 + 2 个桨架、2 支桨斜插进水）。pivot = 船底中点 = 吃水线；'
              '舷缘上沿 y≈3（中）/ 1（两头）。坐人：前排脚底 = 船y−3、后排 = 船y−9，x 在 pivot ±40 内（再往外船底上翘、脚会露出来）；'
              '6 人约 16 px 一个；水面波纹画在船y−3；整体起伏请人和船一起挪 y'), name='救生艇'),
    dict(spec('rusty_boat', 1, 120, 34,
              '货轮缩回原形后的小破船（配色同 rusty_freighter：灰船身 + 暗红褐船底，锈、补丁、破洞都是不透明深色），'
              '船尾歪掉的小驾驶室（x 3–30）、船头一根弯掉的小黄吊杆。pivot = 船底中点 = 吃水线；船舷上沿 y≈13（中）/ 9（船头）。'
              '坐人：座位区 pivot x−28 … x+44（驾驶室后面会被挡住），前排脚底 = 船y−3、后排 = 船y−8'), name='生锈小破船'),
    dict(spec('rusty_freighter', 1, 120, 48,
              '远景无人货轮（力量的替身船）整船侧视：灰 / 暗红褐锈船身 + 流锈 + 铆钉线、船尾脏白舰桥（黑窗、碎窗、黑烟囱褪色红道）、'
              '褪色黄吊车、几个褪色集装箱；比 ship 暗、旧。吃水线 y=38（同 ship：底边往上 10 px，下面 10 行是水下部分）；'
              '轮廓描黑边，缩到 0.2 倍仍是“左舰桥 / 中吊车 / 右船头上翘”'), name='无人货轮'),
    dict(spec('cigarette', 1, 6, 3, '甲板上掐灭的烟头：白滤嘴 + 烧黑的头 + 一点烟灰，横放；pivot = 底边中点'), name='烟头'),
    dict(spec('bomb_box', 2, 20, 16,
              '舱底定时炸弹：木箱 + 红蓝电线缠两道 + 小计时器（红色数码）；帧 0 小红灯亮 / 帧 1 灭。'
              'kind=loop、2 fps：当演员（prop:bomb_box）放着会自己闪；要定住就按帧号取'), name='定时炸弹木箱', kind='loop', fps=2),
    dict(spec('photo_ape_helm', 1, 40, 36,
              '念写照片：舰桥里猩猩（力量同造型）双手握船舵、窗外海平线；紫褐 7 阶单色 + 颗粒 + 暗角，不透明。'
              'S.photo({image}) 放大倍数 = floor(min(120/40, 140/36)) = 3 → 120×108（48 宽只会放大 2 倍 = 96 px，所以做 40 宽）；'
              'pivot = 中心（同原 photo）'), name='念写照片·猩猩掌舵', pivot=[20, 18]),
]


def _outline(im, col=K):
    """不透明区域外面一圈描边（4 邻接），画在透明格上。"""
    a = np.array(im)
    a[_ring(a[..., 3] > 0)] = tuple(col) + (255,)
    return Image.fromarray(a, 'RGBA')


def _ring(mask):
    g = np.zeros_like(mask)
    g[1:, :] |= mask[:-1, :]
    g[:-1, :] |= mask[1:, :]
    g[:, 1:] |= mask[:, :-1]
    g[:, :-1] |= mask[:, 1:]
    return g & ~mask


def _noise(w, h, seed, cell=6):
    """平滑值噪声 [0, 1]（固定种子，每次烘出来一样）。"""
    g = np.random.default_rng(seed).random((h // cell + 2, w // cell + 2))
    ys, xs = np.mgrid[0:h, 0:w]
    fx, fy = xs / cell, ys / cell
    ix, iy = fx.astype(int), fy.astype(int)
    tx, ty = fx - ix, fy - iy
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    top = g[iy, ix] * (1 - tx) + g[iy, ix + 1] * tx
    bot = g[iy + 1, ix] * (1 - tx) + g[iy + 1, ix + 1] * tx
    return top * (1 - ty) + bot * ty


def _ell_mask(w, h, cx, cy, rx, ry):
    ys, xs = np.mgrid[0:h, 0:w]
    return ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2 <= 1.0


def _seg_mask(w, h, pts, r):
    ys, xs = np.mgrid[0:h, 0:w]
    m = np.zeros((h, w), bool)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        l2 = dx * dx + dy * dy or 1e-9
        u = np.clip(((xs - x0) * dx + (ys - y0) * dy) / l2, 0, 1)
        m |= (xs - (x0 + u * dx)) ** 2 + (ys - (y0 + u * dy)) ** 2 <= r * r
    return m


def _edge(mask, d):
    """mask 里朝 d 方向一步就走出 mask 的像素（同原工程 _Pix.shade：光从左上来，d=(1,1) 是暗边、(-1,-1) 是亮边）。"""
    h, w = mask.shape
    nb = np.zeros_like(mask)
    ys0, ys1 = max(0, -d[1]), min(h, h - d[1])
    xs0, xs1 = max(0, -d[0]), min(w, w - d[0])
    nb[ys0:ys1, xs0:xs1] = mask[ys0 + d[1]:ys1 + d[1], xs0 + d[0]:xs1 + d[0]]
    return mask & ~nb


def draw_lifeboat(frame):
    W, H = 112, 22
    a = np.zeros((H, W, 4), np.uint8)
    ORG, ORG_HI, ORG_SH, ORG_DK = (232, 100, 30), (246, 142, 58), (184, 72, 24), (128, 48, 22)
    WHITE, WHITE_SH = (244, 240, 230), (196, 196, 212)
    prof, c = [], (W - 3) / 2                   # 双头船：每列 (上沿, 下沿)，两头 22% 的船底往上弯
    for i in range(W - 2):
        u = abs(i - c) / c
        yt = round(4 - 3 * u ** 4)
        t = (u - 0.78) / 0.22
        yb = H - 2 if u <= 0.78 else round(H - 2 - (H - 3 - yt) * (1 - math.sqrt(max(0.0, 1 - t * t))))
        prof.append((yt, yb))
        for y in range(yt, yb + 1):
            r = y - yt
            col = (WHITE if r == 0 else WHITE_SH) if r <= 1 else (60, 52, 66) if r == 2 else \
                ORG_DK if y >= yb - 1 else ORG_SH if y >= yb - 4 else ORG_HI if r == 3 else ORG
            a[y, i + 1] = col + (255,)
    im = _outline(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    xs = list(range(9, W - 8, 13))              # 护舷绳：每 13 px 一个挂点，中间垂 3 px
    for x0, x1 in zip(xs, xs[1:]):
        pts = [(x, round(6 + 3 * math.sin(math.pi * (x - x0) / (x1 - x0)))) for x in range(x0, x1 + 1)]
        for x, y in pts:
            if a[min(H - 1, y + 1), x, 3]:
                d.point((x, y + 1), fill=(150, 112, 70))
        for x, y in pts:
            d.point((x, y), fill=(236, 214, 150))
    for x in xs:
        d.rectangle((x, 5, x, 6), fill=(74, 74, 92))
    for ox in (40, 80):                         # 桨架 + 斜插进水里的桨（往船尾拖）
        yt = prof[ox - 1][0]
        d.line((ox - 1, yt - 2, ox - 1, yt), fill=K)
        d.line((ox + 1, yt - 2, ox + 1, yt), fill=K)
        d.point((ox, yt), fill=(110, 110, 126))
        x1, y1 = ox - 15, H - 3
        d.line((ox, yt - 1, x1, y1), fill=K, width=3)
        d.line((ox, yt - 1, x1, y1), fill=(216, 168, 96))
        d.polygon([(x1 + 2, y1 - 3), (x1 - 3, y1 - 1), (x1 - 4, y1 + 2), (x1 + 1, y1 + 2)], fill=(200, 144, 72), outline=K)
        d.point((x1 - 1, y1), fill=(216, 168, 96))
    return im


def _rust_hull(W, H, top, bot, rust_seed, pal, cell=5, bias=None):
    """灰 / 暗红褐锈船身的底色 + 噪声锈斑（rusty_boat / rusty_freighter 共用一套颜色）。返回 (RGBA 数组, 船身 mask, ys)。"""
    GREY, GREY_DK, GREY_HI, RB, RB_DK = pal
    hull = np.zeros((H, W), bool)
    for x in top:
        hull[top[x]:bot[x] + 1, x] = True
    ys = np.arange(H)[:, None]
    yt = np.array([top.get(x, 99) for x in range(W)])[None, :]
    yb = np.array([bot.get(x, -99) for x in range(W)])[None, :]
    a = np.zeros((H, W, 4), np.uint8)
    a[hull] = GREY + (255,)
    a[hull & (ys >= yb - 5)] = RB + (255,)
    a[hull & (ys >= yb - 1)] = RB_DK + (255,)
    a[hull & (ys == yt)] = GREY_HI + (255,)
    a[hull & (ys == yt + 1)] = GREY_DK + (255,)
    r = _noise(W, H, rust_seed, cell) * 0.75 + _noise(W, H, rust_seed + 1, 2) * 0.25
    if bias is not None:
        r = r + bias(ys, yt, yb)
    zone = hull & (ys > yt + 1)
    a[zone & (r > 0.64), :3] = (148, 74, 36)
    a[zone & (r > 0.74), :3] = (96, 46, 28)
    a[zone & (r > 0.60) & (r <= 0.64), :3] = (186, 104, 52)
    return a, hull, ys


def _rust_streaks(a, top, bot, xs, seed, n=16):
    """从舷边往下流的锈水痕，长短不一，四成带一道深色边。"""
    rg = np.random.default_rng(seed)
    for x in sorted(rg.choice(np.array(xs), n, replace=False)):
        y, ln = top[x] + 2, int(rg.integers(3, 11))
        for yy in range(y, min(bot[x] - 2, y + ln)):
            a[yy, x, :3] = (148, 74, 36) if yy < y + ln - 2 else (186, 104, 52)
        if rg.random() < 0.4:
            for yy in range(y, min(bot[x] - 2, y + ln // 2)):
                a[yy, x + 1, :3] = (96, 46, 28)


def draw_rusty_boat(frame):
    W, H = 120, 34
    GREY = (88, 86, 96)
    top, bot = {}, {}
    for x in range(3, 117):
        u = (x - 3) / 113
        yt = 14 - round(1.2 * math.sin(u * math.pi))                    # 中间略塌（老船）
        if u > 0.80:
            yt -= round(((u - 0.80) / 0.20) ** 1.5 * 5)                  # 船头往上翘
        yb = H - 2
        if u > 0.84:                                                     # 往外鼓的船首柱
            t = (u - 0.84) / 0.16
            yb = round(H - 2 - (H - 3 - yt) * (1 - math.sqrt(max(0.0, 1 - t ** 2.2))))
        elif u < 0.05:                                                   # 方船尾，底角圆一点
            yb = round(H - 2 - 4 * (1 - u / 0.05) ** 2)
        top[x], bot[x] = yt, yb
    bias = lambda ys, yt, yb: (np.clip((ys - (yb - 10)) / 5.0, 0, 1) * 0.10 - np.clip((ys - (yb - 3)) / 3.0, 0, 1) * 0.10
                               + (np.arange(W)[None, :] > 92) * 0.08)
    a, hull, ys = _rust_hull(W, H, top, bot, 11, (GREY, (58, 56, 66), (118, 116, 124), (98, 46, 40), (68, 32, 30)), 5, bias)
    for x in range(8, 110, 3):                                          # 铆钉线
        y = top[x] + 4
        if hull[y, x] and a[y, x, 0] == GREY[0]:
            a[y, x, :3] = (118, 116, 124)
    _rust_streaks(a, top, bot, list(range(6, 112)), 5)
    for px, py, pw, ph in ((52, 18, 11, 6), (83, 19, 8, 7), (11, 18, 7, 5)):      # 补丁钢板 + 铆钉，下沿流锈
        for y in range(py, py + ph):
            for x in range(px, px + pw):
                if hull[y, x]:
                    a[y, x, :3] = (128, 126, 132) if (y in (py, py + ph - 1) or x in (px, px + pw - 1)) else (106, 104, 112)
        for x in range(px + 1, px + pw - 1, 2):
            for y in (py, py + ph - 1):
                if hull[y, x]:
                    a[y, x, :3] = (44, 42, 52)
        for y in range(py + ph, min(H - 3, py + ph + 3)):
            if hull[y, px + 2]:
                a[y, px + 2, :3] = (148, 74, 36)
    for pts in ([(38, 23), (41, 21), (44, 22), (43, 25), (40, 26)], [(74, 27), (78, 26), (79, 29), (75, 29)],
                [(100, 18), (103, 18), (103, 21), (100, 21)], [(64, 15), (66, 15), (66, 17), (64, 17)]):
        mm = Image.new('L', (W, H))
        ImageDraw.Draw(mm).polygon(pts, fill=1)
        hm = np.array(mm) > 0                                            # 破洞：深色不透明 + 一圈深锈
        a[_ring(hm) & hull, :3] = (96, 46, 28)
        a[hm & hull, :3] = (22, 16, 22)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    for x in range(12, 106):                                             # 船舷上沿几处凹下去
        if x % 11 in (3, 4, 5):
            d.point((x, top[x]), fill=(58, 56, 66))
    WALL, WALL_SH = (186, 176, 158), (146, 136, 120)
    sk = lambda x, y: (x - round((14 - y) * 0.25), y)                    # 驾驶室越高越往左歪
    cab = Image.new('RGBA', (W, H))
    cd = ImageDraw.Draw(cab)
    cd.polygon([sk(8, 14), sk(8, 4), sk(27, 4), sk(27, 14)], fill=WALL)
    cd.polygon([sk(8, 14), sk(8, 4), sk(10, 4), sk(10, 14)], fill=WALL_SH)
    cd.polygon([sk(6, 4), sk(6, 2), sk(30, 0), sk(30, 3)], fill=(70, 66, 74))             # 歪屋顶
    cd.polygon([sk(13, 6), sk(13, 9), sk(24, 9), sk(24, 6)], fill=(30, 26, 34))           # 窗
    cd.line([sk(19, 6), sk(19, 9)], fill=WALL_SH)
    cd.line([sk(21, 6), sk(23, 8), sk(22, 9)], fill=(132, 146, 156))                      # 玻璃裂纹
    for xx, l in ((12, 3), (17, 2), (23, 4), (26, 3)):
        cd.line([sk(xx, 10), sk(xx, 10 + l)], fill=(150, 96, 62))
    im.alpha_composite(cab)
    d = ImageDraw.Draw(im)
    d.polygon([(18, 1), (22, 0), (23, 4), (19, 5)], fill=(44, 40, 48))                   # 小烟囱：黑 + 褪色红道
    d.line((19, 2, 22, 1), fill=(120, 42, 44))
    d.line((10, 1, 9, -1), fill=(110, 108, 120))                                         # 弯掉的天线
    d.line((108, 11, 108, 4), fill=(172, 146, 60))                                       # 船头弯掉的小黄吊杆
    d.line((108, 4, 111, 2, 113, 3), fill=(172, 146, 60))
    d.line((113, 4, 113, 6), fill=(70, 66, 74))
    return _outline(im)


def draw_rusty_freighter(frame):
    W, H, WL = 120, 48, 38
    GREY = (84, 82, 92)
    top, bot = {}, {}
    for x in range(3, 119):
        u = (x - 3) / 115
        yt = 25 - round(((u - 0.80) / 0.20) ** 1.3 * 9) if u > 0.80 else 23 if u < 0.05 else 25   # 船首楼上翘
        yb = H - 1
        if u > 0.86:
            yb = round(H - 1 - (H - 3 - yt) * ((u - 0.86) / 0.14) ** 1.25)                     # 斜船首
        elif u < 0.06:
            yb = round(H - 1 - 7 * (1 - u / 0.06) ** 1.5)                                      # 船尾往里收
        top[x], bot[x] = yt, yb
    RUST_L, RUST, RUST_DK = (176, 98, 50), (138, 70, 36), (92, 46, 30)
    hull = np.zeros((H, W), bool)
    for x in top:
        hull[top[x]:bot[x] + 1, x] = True
    ys = np.arange(H)[:, None]
    tops = np.array([top.get(x, 99) for x in range(W)])[None, :]
    a = np.zeros((H, W, 4), np.uint8)
    a[hull] = GREY + (255,)
    a[hull & (ys >= 33)] = (96, 44, 38, 255)                             # 吃水线以上 5 行暗红褐
    a[hull & (ys >= WL - 1) & (ys <= WL)] = (70, 32, 30, 255)
    a[hull & (ys > WL)] = (52, 26, 28, 255)                              # 水下部分（更暗）
    a[hull & (ys == tops)] = (112, 110, 118, 255)
    a[hull & (ys == tops + 1)] = (56, 54, 64, 255)
    r = _noise(W, H, 21, 6) * 0.7 + _noise(W, H, 22, 2) * 0.3 \
        + (np.arange(W)[None, :] > 98) * 0.10 + ((ys >= 30) & (ys <= WL)) * 0.06   # 船首、吃水线附近锈更重
    zone = hull & (ys <= WL) & (ys > tops + 1)
    a[zone & (r > 0.66), :3] = RUST
    a[zone & (r > 0.75), :3] = RUST_DK
    a[zone & (r > 0.62) & (r <= 0.66), :3] = RUST_L
    for y in (28, 32):                                                   # 铆钉线
        for x in range(7, 112, 3):
            if hull[y, x] and a[y, x, 0] == GREY[0]:
                a[y, x, :3] = (112, 110, 118)
    rg = np.random.default_rng(9)                                        # 流锈
    for x in sorted(rg.choice(np.arange(7, 110), 22, replace=False)):
        y, ln = top[x] + 2, int(rg.integers(4, 13))
        for yy in range(y, min(WL, y + ln)):
            a[yy, x, :3] = RUST if yy < y + ln - 2 else RUST_L
    a[hull & (ys > WL) & (np.arange(W)[None, :] % 7 == 3) & (ys < WL + 4), :3] = RUST_DK
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    d.ellipse((104, 25, 107, 28), fill=(28, 20, 26))                     # 锚链孔 + 一道长锈痕
    d.line((105, 29, 105, 36), fill=RUST)
    d.line((106, 29, 106, 33), fill=RUST_DK)
    up = Image.new('RGBA', (W, H))                                      # 甲板上的东西单独一层，一起描边
    u = ImageDraw.Draw(up)
    WHITE, WHITE_SH, WIN = (176, 168, 152), (138, 130, 118), (26, 22, 30)
    u.rectangle((7, 13, 33, 24), fill=WHITE)                             # 舰桥：下层 + 驾驶台 + 翼桥
    u.rectangle((9, 5, 31, 13), fill=WHITE)
    u.rectangle((5, 5, 35, 7), fill=WHITE_SH)
    u.rectangle((7, 13, 9, 24), fill=WHITE_SH)
    u.rectangle((9, 5, 11, 13), fill=WHITE_SH)
    for x in range(12, 31, 3):
        u.rectangle((x, 9, x + 1, 11), fill=WIN)
    for x in range(11, 33, 4):
        u.point((x, 16), fill=WIN)
        u.point((x, 20), fill=WIN)
    u.line((18, 9, 19, 11), fill=(120, 132, 140))                        # 碎窗反光
    u.line((27, 10, 28, 9), fill=(120, 132, 140))
    for x, l in ((13, 5), (22, 7), (30, 4), (16, 3), (26, 5)):            # 舰桥锈水痕
        u.line((x, 14, x, 14 + l), fill=(132, 96, 70))
    u.line((20, 7, 20, 8), fill=(132, 96, 70))
    u.polygon([(13, 5), (13, 0), (21, 0), (20, 5)], fill=(44, 40, 48))    # 烟囱：黑 + 褪色红道
    u.line((13, 2, 20, 2), fill=(112, 40, 42))
    u.line((28, 5, 28, 0), fill=(70, 68, 78))
    u.line((26, 1, 30, 1), fill=(70, 68, 78))
    for bx, by, bw, col in ((38, 18, 11, (70, 98, 96)), (38, 12, 11, (108, 58, 50)), (51, 18, 11, (76, 82, 100)),
                            (72, 18, 12, (104, 60, 48)), (72, 12, 12, (78, 92, 104)), (85, 18, 12, (82, 100, 84))):
        u.rectangle((bx, by, bx + bw - 1, by + 5), fill=col)             # 褪色集装箱
        for xx in range(bx + 2, bx + bw - 1, 2):
            u.line((xx, by + 1, xx, by + 4), fill=tuple(max(0, v - 22) for v in col))
        u.point((bx + bw - 3, by + 4), fill=RUST)
        u.point((bx + 1, by + 1), fill=RUST_L)
    YEL, YEL_DK = (176, 148, 60), (110, 92, 44)                          # 褪色黄吊车：立柱 + 吊臂 + 吊钩
    u.rectangle((64, 9, 67, 24), fill=YEL)
    u.line((66, 9, 66, 24), fill=YEL_DK)
    u.rectangle((62, 8, 69, 11), fill=YEL)
    u.line((66, 9, 92, 1), fill=YEL, width=2)
    u.line((92, 2, 92, 12), fill=(60, 56, 64))
    u.line((90, 12, 93, 12), fill=(60, 56, 64))
    u.point((90, 11), fill=(60, 56, 64))
    u.line((112, 16, 112, 6), fill=(118, 116, 126))                      # 船首细桅 + 横桁
    u.line((110, 9, 114, 9), fill=(118, 116, 126))
    im.alpha_composite(_outline(up))
    return _outline(im)


def draw_cigarette(frame):
    im, d = canvas(6, 3)
    d.line((1, 0, 4, 0), fill=K)
    d.line((1, 2, 4, 2), fill=K)
    d.point((0, 1), fill=K)
    d.line((1, 1, 2, 1), fill=(246, 242, 232))          # 白滤嘴
    d.point((3, 1), fill=(210, 204, 192))              # 捏扁的烟纸
    d.point((4, 1), fill=(64, 58, 66))                 # 烧黑的头
    d.point((5, 1), fill=(150, 146, 152))              # 一点烟灰
    d.point((5, 2), fill=(120, 116, 124))
    return im


def draw_bomb_box(frame):
    im, d = canvas(20, 16)
    d.rectangle((0, 3, 19, 15), fill=(166, 114, 64), outline=K)
    for y in (7, 11):
        d.line((1, y, 18, y), fill=(90, 58, 38))
    for y in (4, 8, 12):
        d.line((3, y, 16, y), fill=(200, 148, 88))
    for x in (1, 17):
        d.rectangle((x, 4, x + 1, 14), fill=(126, 84, 48))
        d.point((x, 5), fill=(60, 52, 54))
        d.point((x, 13), fill=(60, 52, 54))
    RED_W, BLUE_W = (214, 46, 46), (66, 104, 214)       # 红、蓝电线各缠一道
    d.line((0, 12, 6, 13, 13, 12, 19, 13), fill=RED_W)
    d.line((0, 10, 5, 9, 14, 10, 19, 9), fill=BLUE_W)
    d.rectangle((6, 2, 14, 8), fill=(54, 54, 66), outline=K)          # 计时器
    d.rectangle((7, 4, 12, 6), fill=(30, 18, 22))
    for x in (7, 8, 10, 11):
        d.point((x, 4), fill=(236, 70, 60))
        d.point((x, 6), fill=(236, 70, 60))
    d.point((7, 5), fill=(236, 70, 60))
    d.point((11, 5), fill=(236, 70, 60))
    d.point((9, 5), fill=(160, 40, 40))
    d.line((6, 6, 4, 9), fill=BLUE_W)
    d.line((14, 6, 15, 12), fill=RED_W)
    if frame == 0:                                      # 小红灯：亮（带一圈光）/ 灭
        d.point((13, 1), fill=(255, 190, 180))
        d.point((13, 2), fill=(255, 60, 52))
        d.point((12, 1), fill=(255, 120, 110))
        d.point((14, 1), fill=(255, 120, 110))
    else:
        d.point((13, 2), fill=(96, 30, 34))
    return im


PHOTO_PAL = [(30, 16, 28), (58, 34, 50), (90, 58, 74), (124, 86, 96), (160, 120, 120), (198, 160, 148), (234, 210, 190)]


def draw_photo_ape_helm(frame):
    """直接按明暗档画（0 最暗 … 6 最亮：窗外最亮、头毛中亮、脸盘暗、舵轮亮木色压在暗身子前面），
    再加暗角 + 颗粒（固定种子），量化成 7 阶紫褐 = 念写照片的单色调。"""
    W, H = 40, 36
    ys, xs = np.mgrid[0:H, 0:W]
    t = np.full((H, W), 1.6)                                           # 舰桥里面
    t[1:9] = 5.6                                                        # 窗：天
    t[6:9] = 6.0
    t[9] = 5.0                                                          # 海平线
    t[10:16] = 3.4                                                      # 海
    rg = np.random.default_rng(3)
    for _ in range(10):
        y, x = int(rg.integers(11, 16)), int(rg.integers(1, 36))
        t[y, x:x + 3] = 4.6
    t[0] = 0.8
    for x0 in (0, 13, 25, 38):
        t[1:16, x0:x0 + 2] = 1.0                                        # 窗框竖条
    t[16:18] = 1.2
    t[16] = 2.6                                                         # 窗台亮边
    t[18:] = 2.0                                                        # 仪表台

    def fill(mask, v, sh, hi):
        t[_ring(mask)] = 0
        t[mask] = v
        t[_edge(mask, (1, 1))] = sh
        t[_edge(mask, (-1, -1))] = hi
    fill(_ell_mask(W, H, 20, 29, 14.5, 9.5), 3.2, 2.4, 4.0)             # 肩背（背光，比头毛暗一档）
    hair = _ell_mask(W, H, 20, 11, 9.2, 8.6)
    for x, y in ((16, 1), (20, 0), (24, 1)):                              # 头顶三撮毛（同精灵）
        hair[y, x] = hair[y + 1, x] = True
    fill(hair, 4.0, 3.0, 5.0)
    face = _ell_mask(W, H, 20, 12.3, 7.2, 6.6)                           # 大颊垫脸盘
    t[face] = 2.0
    t[_edge(face, (1, 1))] = 1.4
    t[_ring(face) & hair] = 0.6
    t[_ell_mask(W, H, 20, 15.2, 4.2, 2.9)] = 3.0                         # 口鼻
    t[8:10, 15:26] = 0.8                                                 # 浓眉
    t[10, 16], t[10, 17], t[10, 23], t[10, 24] = 0, 6, 6, 0             # 黄眼
    t[13, 19] = t[13, 21] = 1.2                                          # 鼻孔
    t[15:18, 17:24] = 0                                                  # 龇牙笑（同 idle 帧 1）
    t[15:17, 18:23] = 6
    t[16, 19] = t[16, 21] = 0.5
    cx, cy = 20, 31                                                      # 船舵：轮缘 2 px + 8 根辐条伸出去当把手
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    spokes = np.zeros((H, W), bool)
    knobs = np.zeros((H, W), bool)
    for k in range(8):
        ang = k * math.pi / 4 + math.pi / 8                              # 把手错开正上方，不顶到下巴
        spokes |= _seg_mask(W, H, [(cx, cy), (cx + math.sin(ang) * 11.0, cy - math.cos(ang) * 11.0)], 0.55)
        knobs |= _ell_mask(W, H, cx + math.sin(ang) * 11.6, cy - math.cos(ang) * 11.6, 1.2, 1.2)
    rim = (dist >= 7.3) & (dist <= 9.2)
    wheel = spokes | rim | knobs | (dist <= 2.3)
    t[(dist < 7.3) & ~wheel] = 2.0                                       # 轮子里面露出来的身子压暗，辐条才跳得出来
    t[_ring(wheel)] = 1.0
    t[wheel] = 4.4
    t[rim] = 5.0
    t[rim & (ys < cy - 1) & (xs < cx + 1)] = 6.0                          # 轮缘左上反光
    t[rim & (ys > cy + 1) & (xs > cx - 1)] = 4.0
    t[knobs] = 5.0
    t[dist <= 2.3] = 3.0
    t[dist <= 1.2] = 6.0                                                 # 铜轴心
    for side in (-1, 1):                                                 # 两只手（暗）抓住左右两个把手，手臂从肩膀下来
        ang = math.pi / 2 - math.pi / 8
        hx, hy = cx + side * math.sin(ang) * 11.6, cy - math.cos(ang) * 11.6
        arm = _seg_mask(W, H, [(cx + side * 12.5, 21.5), (hx, hy - 0.5)], 2.0) & ~wheel
        t[_ring(arm) & ~wheel] = 0.6
        t[arm] = 3.4
        hand = _ell_mask(W, H, hx, hy, 2.1, 1.8)
        t[_ring(hand)] = 0.4
        t[hand] = 1.2
    vig = ((xs - (W - 1) / 2) / (W / 2)) ** 2 + ((ys - (H - 1) / 2) / (H / 2)) ** 2
    t = t - 1.1 * np.clip(vig - 0.45, 0, 1.2) + np.random.default_rng(17).normal(0, 0.2, (H, W))
    idx = np.clip(np.floor(t + 0.5), 0, len(PHOTO_PAL) - 1).astype(int)
    out = np.array(PHOTO_PAL, np.uint8)[idx]
    return Image.fromarray(np.dstack([out, np.full((H, W), 255, np.uint8)]), 'RGBA')


# =====================================================================================
#  第3章（新加坡：酒店里的黑檀木恶魔、缆车里的黄色节制）新道具（2026-10-11）
# =====================================================================================
# 已有同名道具不能覆盖：slime_puddle（20×6 一帧）和 mirror_shard（6×6 一帧，第4章倒吊人在用）在 art_props_later.py，
# 所以第3章的黏液滩叫 slime_pool、镜子碎片叫 mirror_piece。黏液配色和 art_new_rubbersoul.py 的黏液铠甲一致。
PROPS += [
    dict(spec('slime_pool', 2, 22, 7,
              '地上的一滩黄色黏液（黄色节制）：扁平的一滩 + 中间偏左一个鼓包，深黄褐描边、左上亮边、右下暗边。'
              '帧 0 表面一道高光 / 帧 1 高光挪开、右边鼓起一个小气泡。kind=loop、2 fps：放着会自己冒泡；'
              '“吞掉”垃圾桶 = 在垃圾桶的 pivot 上叠这一滩（同一个 x、y+1）再把垃圾桶删掉；pivot = 底边中点'),
         name='黄色黏液滩', kind='loop', fps=2),
    dict(spec('trash_can', 1, 14, 18,
              '新加坡路边的金属垃圾桶：墨绿桶身 + 竖向压筋 + 圆顶桶盖（中间一个提手）、底下一圈深色桶脚，黑描边；'
              'pivot = 底边中点（放在人行道上，和人物同一条地面线）'), name='路边垃圾桶'),
    dict(spec('mirror_piece', 2, 12, 14,
              '镜子碎片（地上 / 柜门上，竖着放）：不规则尖角碎片，深灰蓝边 + 浅蓝灰镜面；左上亮边、右下暗边。'
              '中间留一块平的镜面（x 3–8、y 5–10，全是同一个颜色）给剧情画倒影。帧 0 不反光 / '
              '帧 1 两道白色反光斜着扫过（绕开中间平的那块）+ 两个尖角闪一下（按帧号取：glint ? 1 : 0）；pivot = 底边中点'), name='镜子碎片（第3章）'),
    dict(spec('doll_razor', 1, 10, 4,
              '玩偶散架后掉在地上的那把剃刀：打开的直柄剃刀横放，左边暗红木柄、右边银白刀片 + 一个白反光点，'
              '和 devo_doll 手里的剃刀同色；pivot = 底边中点'), name='玩偶的剃刀'),
]

SLIME, SLIME_L, SLIME_H, SLIME_D, SLIME_O = (240, 206, 52), (255, 234, 112), (255, 252, 216), (200, 152, 26), (120, 80, 16)


def _paint_blob(mask, base, lite, dark, outline):
    """mask 内填 base，左上边 lite、右下边 dark，外面一圈 outline（4 邻接）。"""
    H, W = mask.shape
    a = np.zeros((H, W, 4), np.uint8)
    a[mask] = base + (255,)
    a[_edge(mask, (-1, -1)) | _edge(mask, (0, -1))] = lite + (255,)
    a[_edge(mask, (1, 1)) | _edge(mask, (0, 1))] = dark + (255,)
    a[_ring(mask)] = outline + (255,)
    return a


def draw_slime_pool(frame):
    W, H = 22, 7
    m = _ell_mask(W, H, 10.5, 4.6, 9.6, 1.7) | _ell_mask(W, H, 8.5, 3.2, 4.2, 1.6)
    m |= _ell_mask(W, H, 16.5, 4.8, 3.2, 1.2)
    if frame == 1:
        m |= _ell_mask(W, H, 15.5, 2.6, 2.1, 2.1)               # 右边鼓起一个小气泡（帧 0 是平的）
    m[0, :] = m[-1, :] = False
    m[:, 0] = m[:, -1] = False
    a = _paint_blob(m, SLIME, SLIME_L, SLIME_D, SLIME_O)
    if frame == 0:
        for x, y in ((5, 3), (6, 3), (7, 2), (11, 4)):            # 表面一道高光
            a[y, x] = SLIME_H + (255,)
    else:
        for x, y in ((8, 2), (9, 2), (4, 4)):
            a[y, x] = SLIME_H + (255,)
        a[2, 15] = SLIME_H + (255,)                              # 气泡上的亮点 + 右下一圈暗
        a[2, 14] = SLIME_L + (255,)
        a[3, 17] = SLIME_D + (255,)
    return Image.fromarray(a, 'RGBA')


def draw_trash_can(frame):
    im, d = canvas(14, 18)
    G, GD, GH, GDD = (60, 122, 84), (36, 80, 56), (110, 168, 118), (24, 52, 40)
    d.rectangle((2, 5, 11, 16), fill=G, outline=K)              # 桶身
    for x in (4, 7, 10):                                         # 竖向压筋
        d.line((x, 6, x, 15), fill=GD)
    d.line((3, 6, 3, 15), fill=GH)                               # 左亮
    d.line((5, 6, 5, 15), fill=GH)
    d.line((11, 6, 11, 15), fill=GDD)                            # 右暗
    d.line((2, 9, 11, 9), fill=GD)                               # 腰箍
    d.line((3, 9, 10, 9), fill=GDD)
    d.rectangle((1, 16, 12, 17), fill=(84, 88, 96))             # 桶脚（灰色底箍，只描左右和底）
    d.line((1, 17, 12, 17), fill=K)
    d.point((1, 16), fill=K)
    d.point((12, 16), fill=K)
    d.line((2, 16, 5, 16), fill=(132, 138, 146))
    d.ellipse((0, 2, 13, 7), fill=GD, outline=K)                 # 圆顶桶盖
    d.line((2, 4, 6, 3), fill=GH)
    d.line((1, 5, 12, 5), fill=G)
    d.line((1, 6, 12, 6), fill=GDD)
    d.rectangle((5, 0, 8, 2), fill=(150, 156, 160), outline=K)  # 提手
    d.line((6, 1, 7, 1), fill=GD)
    return im


def draw_mirror_piece(frame):
    W, H = 12, 14
    poly = [(2, 13), (0, 9), (1, 4), (4, 0), (6, 4), (9, 1), (11, 5), (10, 10), (7, 13)]   # 上沿两个尖角
    mi = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mi).polygon(poly, fill=255)
    m = np.array(mi) > 0
    inner = m & ~_ring(~m)                                       # 往里缩 1 px 的镜面
    a = np.zeros((H, W, 4), np.uint8)
    a[m] = (40, 46, 66, 255)                                     # 深灰蓝边（兼描边）
    a[inner] = (160, 182, 204, 255)                              # 浅蓝灰镜面
    a[inner & (_edge(inner, (-1, -1)) | _edge(inner, (0, -1)))] = (206, 222, 236, 255)
    a[inner & (_edge(inner, (1, 1)) | _edge(inner, (0, 1)))] = (112, 132, 160, 255)
    flat = np.zeros((H, W), bool)                                # 中间那块平的（剧情画倒影）：全同色
    flat[5:11, 3:9] = True
    a[flat & inner] = (178, 198, 216, 255)
    if frame == 1:                                               # 白色反光：一宽一窄两道斜带从左下扫到右上（绕开中间平的那块）
        for x in range(W):
            for y in range(H):
                if inner[y, x] and not flat[y, x] and x + y in (6, 7, 10):
                    a[y, x] = (255, 255, 255, 255) if x + y != 10 else (230, 242, 255, 255)
        a[0, 4] = a[1, 9] = (255, 255, 255, 255)                 # 两个尖角各闪一下
    return Image.fromarray(a, 'RGBA')


def draw_doll_razor(frame):
    rows = ["....KKKKKK",
            "KKKKBWBBBK",
            "KhHHKDDDDK",
            "KKKK.KKKK."]
    pal = {'K': (20, 18, 30), 'B': (212, 224, 236), 'W': (255, 255, 255), 'D': (132, 148, 168),
           'H': (70, 36, 30), 'h': (136, 82, 58)}
    im = Image.new('RGBA', (10, 4))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal:
                im.putpixel((x, y), pal[ch] + (255,))
    return im


# =====================================================================================
#  第4章（印度：加尔各答 / 瓦拉纳西）新道具（2026-10-11）
# =====================================================================================
# 原来的 tar_barrel（art_props_later，16×20：灰色平涂圆桶，帧 1 只在桶脚多一摊黑）看不出是铁皮桶、柏油也看不出来，
# 所以另画 tar_drum：两帧外形完全一样（三只桶摆在一起分不出哪只是柏油桶），帧 1 是念写指到时柏油从桶沿溢出来。
# wood_barrel 和它同高、同一套光照（左上亮、右边暗）和描边，摆在一起不穿帮。
# jgeil_hat 不画：J·凯尔的原图（sprites_enemies._geil：idle / hurt / 头像）不戴帽子；原片 s09 里落地的帽子是荷尔·荷斯的牛仔帽（已有 hat）。
PROPS += [
    dict(spec('tar_drum', 2, 18, 22,
              '路边的铁皮油桶（藏青漆 + 锈斑 + 两道滚箍，左边亮右边暗）。帧 0 = 普通桶：盖着盖子、盖上一个小桶塞；'
              '帧 1 = 柏油桶：盖子没了，黑亮的柏油从桶口鼓出来、顺着桶壁淌下四道（带紫白高光）。两帧桶身一模一样，'
              '按帧号取（剧情里念写指到那只 = 1，其他 = 0）；pivot = 底边中点'), name='铁皮桶 / 柏油桶'),
    dict(spec('wood_barrel', 1, 18, 22,
              '木桶：中间鼓、两头收的木板桶身 + 竖向板缝 + 上下两道铁箍 + 木盖，和 tar_drum 同高、同光照、同描边，'
              '可以和它摆在一起；pivot = 底边中点'), name='木桶'),
    dict(spec('fruit_basket', 2, 20, 12,
              '水果摊上的一筐水果：竹编筐（编织纹）里堆着芒果、香蕉、青柠、石榴。帧 0 = 满的；'
              '帧 1 = 被女帝啃掉一块：右上角的芒果和香蕉没了，剩下的芒果缺一个半圆、露出黄色果肉；pivot = 底边中点'),
         name='水果筐'),
]


def _ramp(t, cols):
    """t ∈ [0, 1] 从左到右 → 四阶色（亮、底、暗、最暗）。"""
    return cols[0] if t < .2 else cols[1] if t < .58 else cols[2] if t < .84 else cols[3]


def draw_tar_drum(frame):
    W, H = 18, 22
    a = np.zeros((H, W, 4), np.uint8)
    PAINT = [(96, 140, 162), (58, 98, 122), (40, 68, 90), (26, 44, 62)]
    HOOP = [(178, 204, 214), (118, 160, 182), (78, 112, 134), (52, 78, 98)]
    BASE = [(88, 124, 146), (52, 86, 108), (36, 60, 80), (24, 40, 56)]
    RUST, RUST_D = (156, 92, 52), (108, 60, 36)
    x0, x1, top, bot = 1, 16, 3, 20
    nz = _noise(W, H, 23, cell=3)
    for x in range(x0, x1 + 1):
        t = (x - x0) / (x1 - x0)
        for y in range(top, bot + 1):
            c = _ramp(t, PAINT)
            if y >= 10 and nz[y, x] > .62:                           # 下半截的锈斑
                c = RUST if nz[y, x] < .74 else RUST_D
            a[y, x] = c + (255,)
    for y in (8, 14):                                                # 两道滚箍：上面一行亮、下面一行暗
        for x in range(x0, x1 + 1):
            a[y, x] = _ramp(max(0, (x - x0) / (x1 - x0) - .1), HOOP) + (255,)
            a[y + 1, x] = (24, 36, 50, 255)
    for x in range(x0, x1 + 1):                                      # 桶底一圈
        a[bot, x] = (30, 44, 58, 255)
        a[bot - 1, x] = _ramp((x - x0) / (x1 - x0), BASE) + (255,)
    lid = _ell_mask(W, H, 8.5, 3.0, 7.6, 2.3)
    rim = lid & ~_ell_mask(W, H, 8.5, 3.0, 6.4, 1.4)
    if frame == 0:
        a[lid] = (112, 152, 172, 255)                                # 盖子
        a[_ell_mask(W, H, 8.5, 3.4, 5.6, 1.0) & lid] = (86, 124, 146, 255)
        a[rim] = (150, 184, 198, 255)
        a[rim & _edge(lid, (1, 1))] = (48, 78, 98, 255)
        a[2, 12] = a[2, 13] = (196, 214, 222, 255)                   # 小桶塞
        a[3, 12] = a[3, 13] = (60, 90, 110, 255)
    else:
        TAR, TAR_M, TAR_H, TAR_W = (20, 16, 26), (54, 44, 70), (128, 116, 158), (232, 228, 246)
        a[rim] = (150, 184, 198, 255)
        blob = _ell_mask(W, H, 8.5, 2.6, 6.6, 2.4)                  # 柏油从桶口鼓出来
        a[blob] = TAR + (255,)
        for dx, y0, y1 in ((3, 4, 8), (8, 4, 6), (12, 4, 11), (14, 4, 7)):   # 顺着桶壁往下淌
            for y in range(y0, y1 + 1):
                a[y, dx] = TAR + (255,)
                if y < y1 - 1:
                    a[y, dx + 1] = TAR + (255,)
            a[y1, dx] = TAR_M + (255,)
        for x, y in ((5, 1), (6, 1), (7, 1), (4, 2)):                # 亮面一道高光
            a[y, x] = TAR_H + (255,)
        a[1, 6] = TAR_W + (255,)
        a[6, 3] = a[5, 8] = TAR_H + (255,)
        a[3, 12] = a[3, 13] = TAR_M + (255,)
    return _outline(Image.fromarray(a, 'RGBA'))


def draw_wood_barrel(frame):
    W, H = 18, 22
    a = np.zeros((H, W, 4), np.uint8)
    WOOD = [(206, 152, 92), (164, 110, 62), (122, 78, 42), (88, 54, 30)]
    IRON = [(150, 150, 166), (96, 96, 112), (66, 66, 80), (44, 44, 56)]
    IRON_D = [(96, 96, 112), (66, 66, 80), (44, 44, 56), (34, 34, 44)]
    cx, top, bot = 8.5, 3, 20
    m = np.zeros((H, W), bool)
    for y in range(top, bot + 1):
        hw = 6.6 + 1.5 * math.sin(math.pi * (y - top) / (bot - top))   # 中间鼓、两头收
        for x in range(W):
            if abs(x - cx) <= hw:
                m[y, x] = True
                a[y, x] = _ramp((x - (cx - hw)) / (2 * hw), WOOD) + (255,)
        for u in (-.62, -.22, .2, .6):                               # 竖向板缝（跟着鼓肚子弯）
            x = int(round(cx + u * hw))
            if 0 <= x < W and m[y, x]:
                a[y, x] = (96, 60, 32, 255)
    for y0 in (6, 15):                                               # 上下两道铁箍
        for y, cols in ((y0, IRON), (y0 + 1, IRON_D)):
            xs = np.where(m[y])[0]
            for x in xs:
                a[y, x] = _ramp((x - xs[0]) / max(1, xs[-1] - xs[0]), cols) + (255,)
    for x in np.where(m[bot])[0]:
        a[bot, x] = (70, 42, 24, 255)
    lid = _ell_mask(W, H, 8.5, 3.0, 6.9, 2.1)
    a[lid] = (184, 134, 80, 255)
    a[lid & _edge(lid, (1, 1))] = (110, 70, 38, 255)
    a[lid & _edge(lid, (-1, -1))] = (222, 178, 118, 255)
    for x in (5, 9, 12):                                             # 盖板的缝
        if lid[3, x]:
            a[3, x] = (138, 92, 50, 255)
    return _outline(Image.fromarray(a, 'RGBA'))


def draw_fruit_basket(frame):
    W, H = 20, 12
    a = np.zeros((H, W, 4), np.uint8)
    WICK, WICK_D, WICK_H = (200, 152, 88), (148, 100, 52), (232, 192, 124)
    for y in range(6, 12):                                           # 竹筐：上宽下窄，编织纹
        inset = (y - 6) // 3
        for x in range(1 + inset, W - 1 - inset):
            a[y, x] = (WICK_D if (x + (y // 2) * 2) % 4 < 2 and y % 2 == 0 else WICK) + (255,)
        xs = np.where(a[y, :, 3] > 0)[0]
        a[y, xs[-1]] = WICK_D + (255,)                               # 右边暗
    for x in range(0, W):                                            # 筐沿
        a[5, x] = WICK_H + (255,)

    def fruit(cx, cy, rx, ry, base, lite, dark):
        mm = _ell_mask(W, H, cx, cy, rx, ry) & (np.arange(H)[:, None] <= 5)
        a[mm] = base + (255,)
        a[mm & _edge(mm, (1, 1))] = dark + (255,)
        a[mm & _edge(mm, (-1, -1))] = lite + (255,)
        return mm
    MANGO = ((246, 180, 52), (255, 222, 120), (214, 110, 40))
    LIME = ((118, 178, 62), (170, 214, 104), (70, 120, 40))
    POME = ((206, 46, 58), (246, 112, 112), (140, 24, 40))
    BANANA = ((250, 222, 84), (255, 246, 170), (196, 160, 40))
    fruit(3.5, 4.0, 2.4, 1.8, *LIME)
    fruit(7.0, 3.5, 2.6, 2.2, *POME)
    fruit(15.5, 4.0, 2.4, 1.8, *LIME)
    fruit(10.5, 3.0, 3.0, 2.4, *MANGO)
    if frame == 0:
        fruit(14.0, 2.4, 3.0, 2.2, *MANGO)
        for x, y in ((11, 1), (12, 0), (13, 0), (14, 0), (15, 0), (16, 1), (17, 2)):   # 一挂香蕉搭在上面
            a[y, x] = BANANA[0] + (255,)
            a[y + 1, x] = BANANA[2] + (255,)
        a[0, 12] = BANANA[1] + (255,)
        a[2, 17] = (110, 80, 30, 255)
    else:
        # 被啃掉一块：右上的芒果和香蕉没了，剩下的芒果缺一个半圆、露出黄色果肉
        bite = _ell_mask(W, H, 14.0, 1.2, 3.8, 3.4)
        for x, y in ((10, 1), (11, 3), (13, 4), (16, 3)):            # 牙印：咬口边缘一排锯齿
            bite[y, x] = True
        hit = (a[..., 3] > 0) & bite & (np.arange(H)[:, None] <= 4)
        a[hit] = 0
        fruit_px = (a[..., 3] > 0) & (np.arange(H)[:, None] <= 4)
        a[_ring(hit) & fruit_px] = (255, 236, 160, 255)              # 咬开的地方露出果肉
        for x, y in ((15, 5), (17, 5)):                              # 掉在筐沿上的碎渣
            a[y, x] = (255, 214, 120, 255)
    return _outline(Image.fromarray(a, 'RGBA'))
