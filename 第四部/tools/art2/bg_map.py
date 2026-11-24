# 杜王町地图 morioh_map 重画（2026-11-24）：各章开头日历地图的底图。
#   320×180，游戏里 2 倍放大；上面落图钉（各章写的坐标）、东南海面盖红章（固定在 x 250–284, y 118–145）、
#   右上角贴「M县S市 杜王町」小字（x 273–313, y 6–14）。
#   旧图（tools/art/p4_bg.py 的 morioh_map）是旧纸上几笔线 + 色块房子；这里换成一张俯视的町内绘地图：
#     山：高度图 + 西北光晕渲 + 一颗颗树冠；海：按离岸距离分深浅、浪纹、岸边白浪；河：堤岸、桥；
#     铁路：碎石道床、枕木、铁桥、隧道口、车站月台；路网：国道、杜王大道、商店街、住宅区小路、斑马线；
#     每栋房子：屋顶分坡面明暗 + 南墙窗户 + 往东南的影子；行道树、林子、田、牧场、港口、海岬灯塔、别墅区。
#   每章写死的图钉坐标都对着画好的建筑（PINS 表），红章那块留成空海面。
#   用法：python 第四部/tools/art2/bg_map.py [核对图目录]   （写 assets/bg/morioh_map/map.png 和元数据锚点）
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

W, H = 320, 180
HERE = os.path.dirname(os.path.abspath(__file__))
P4 = os.path.normpath(os.path.join(HERE, '..', '..'))
ASSETS = os.path.join(P4, 'assets')
META = os.path.join(ASSETS, '_meta')

B4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16.0
BAY = np.tile(B4, (H // 4 + 1, W // 4 + 1))[:H, :W]
YY, XX = np.mgrid[0:H, 0:W]
STAMP = (250, 118, 284, 145)          # 红章落的地方（不画东西）
PLACE = (270, 5, 315, 16)             # 右上角地名牌

# ------------------------------------------------------------------ 各章图钉（剧情里的坐标）：画的时候对准
PINS = {
    'school': (170, 70), 'home': (118, 126), 'station': (203, 62), 'nijimura': (70, 140), 'hirose_home': (150, 150),
    'trattoria': (146, 98), 'rohan_house': (228, 48), 'farm': (58, 70), 'alley': (190, 96), 'bank': (222, 82),
    'jhs': (138, 58), 'salon': (214, 86), 'tailor': (188, 100), 'kira_old': (130, 104), 'tower': (46, 44),
    'miyamoto': (140, 100), 'fin_home': (140, 104),
    # 下面几处剧情里没写死（或写的点落在海里），这次按画好的建筑定，写进元数据锚点：
    'villa': (288, 46), 'harbor': (281, 90), 'kawajiri': (112, 146), 'rock': (238, 117), 'market': (94, 116),
}


# ------------------------------------------------------------------ 颜色
def rgb(c):
    c = c.lstrip('#')
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)


def mixc(a, b, k):
    a, b = rgb(a).astype(float), rgb(b).astype(float)
    v = a + (b - a) * k
    return '#%02x%02x%02x' % tuple(int(round(x)) for x in np.clip(v, 0, 255))


def shade(c, k):
    """k < 0 变暗（往蓝紫偏）、k > 0 变亮（往暖白偏）"""
    return mixc(c, '#1a1230', -k) if k < 0 else mixc(c, '#fffbea', k)


# ------------------------------------------------------------------ 画布和遮罩
class Cv:
    def __init__(self, c):
        self.a = np.zeros((H, W, 3), np.uint8)
        self.a[:] = rgb(c)

    def fill(self, m, c):
        self.a[m] = rgb(c)

    def dith(self, m, c, k):
        """在遮罩 m 上按比例 k（数或逐像素数组）抖动撒颜色 c"""
        kk = np.broadcast_to(np.asarray(k, float), (H, W))
        self.a[m & (kk > BAY)] = rgb(c)

    def px(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H and c is not None:
            self.a[y, x] = rgb(c)

    def rect(self, x0, y0, x1, y1, c):
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W - 1, x1), min(H - 1, y1)
        if x1 >= x0 and y1 >= y0:
            self.a[y0:y1 + 1, x0:x1 + 1] = rgb(c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def darken(self, m, k=(0.72, 0.74, 0.86)):
        a = self.a[m].astype(float) * np.array(k)
        self.a[m] = np.clip(a, 0, 255).astype(np.uint8)

    def lighten(self, m, k=0.25, to='#fff8e0'):
        a = self.a[m].astype(float)
        self.a[m] = np.clip(a + (rgb(to).astype(float) - a) * k, 0, 255).astype(np.uint8)

    def img(self):
        return Image.fromarray(self.a, 'RGB').convert('RGBA')


def pmask(pts):
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    return np.array(im) > 0


def lmask(pts, w=1):
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    pts = [(float(x), float(y)) for x, y in pts]
    if w <= 1:
        for (x, y) in pixpath(pts):
            if 0 <= x < W and 0 <= y < H:
                im.putpixel((x, y), 255)
    else:
        d.line(pts, fill=255, width=int(w), joint='curve')
    return np.array(im) > 0


def rmask(x0, y0, x1, y1):
    m = np.zeros((H, W), bool)
    x0, x1 = sorted((int(x0), int(x1)))
    y0, y1 = sorted((int(y0), int(y1)))
    m[max(0, y0):max(0, y1 + 1), max(0, x0):max(0, x1 + 1)] = True
    return m


def emask(cx, cy, rx, ry):
    return ((XX - cx) / max(rx, .5)) ** 2 + ((YY - cy) / max(ry, .5)) ** 2 <= 1.0


def shift(m, dx, dy):
    out = np.zeros_like(m)
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def inner_edge(m):
    return m & ~ndi.binary_erosion(m, border_value=1)


def outer_edge(m, diag=False):
    st = np.ones((3, 3), bool) if diag else None
    return ndi.binary_dilation(m, structure=st) & ~m


def spline(pts, step=0.4):
    """Catmull-Rom 过控制点的密点列"""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (np.array(P[j], float) for j in (i - 1, i, i + 1, i + 2))
        n = max(2, int(np.linalg.norm(p2 - p1) / step))
        for t in np.linspace(0, 1, n, endpoint=False):
            q = 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
            out.append((q[0], q[1]))
    out.append(tuple(map(float, pts[-1])))
    return out


def pixpath(curve):
    """密点列 → 8 连通、不带直角拐的单像素路径"""
    pts = []
    for x, y in curve:
        p = (int(round(x)), int(round(y)))
        if pts and p == pts[-1]:
            continue
        if pts and max(abs(p[0] - pts[-1][0]), abs(p[1] - pts[-1][1])) > 1:
            x0, y0 = pts[-1]
            n = max(abs(p[0] - x0), abs(p[1] - y0))
            for k in range(1, n):
                pts.append((int(round(x0 + (p[0] - x0) * k / n)), int(round(y0 + (p[1] - y0) * k / n))))
        pts.append(p)
    out = []
    for p in pts:
        if len(out) >= 2 and abs(p[0] - out[-2][0]) <= 1 and abs(p[1] - out[-2][1]) <= 1:
            out[-1] = p
        else:
            out.append(p)
    return out


def frames(curve):
    """密点列 → [(x, y, 切向 tx, ty, 弧长 s)]"""
    out, s = [], 0.0
    for i, (x, y) in enumerate(curve):
        a = curve[max(0, i - 2)]
        b = curve[min(len(curve) - 1, i + 2)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1.0
        if i:
            s += math.hypot(x - curve[i - 1][0], y - curve[i - 1][1])
        out.append((x, y, tx / L, ty / L, s))
    return out


def fbm(seed, base=24, octaves=4, gain=0.5):
    rng = np.random.RandomState(seed)
    out = np.zeros((H, W))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(1.0, base / 2 ** o)
        gh, gw = int(H / s) + 4, int(W / s) + 4
        grid = rng.rand(gh, gw)
        up = ndi.zoom(grid, s, order=3, mode='nearest')[:H, :W]
        out += amp * up
        tot += amp
        amp *= gain
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-9)


def along(curve, x):
    """折线在某个 x 上的 y"""
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        if (x0 - x) * (x1 - x) <= 0 and x0 != x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


def across(curve, y):
    """折线在某个 y 上的 x"""
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return None


# ================================================================== 地理
COAST = [(282, -3), (281, 8), (283, 18), (288, 26), (295, 31), (302, 35), (307, 40), (305, 45), (298, 48), (290, 51), (284, 56),
         (281, 64), (279, 72), (277, 80), (276, 88), (274, 96), (270, 103), (262, 110), (253, 116), (245, 122), (238, 130),
         (233, 138), (229, 146), (226, 155), (223, 165), (221, 174), (220, 183)]
RIVER = [(149, -3), (151, 8), (150, 18), (152, 28), (155, 38), (155, 48), (154, 58), (155, 68), (157, 78), (160, 88), (163, 98),
         (166, 108), (170, 118), (176, 127), (185, 134), (196, 139), (208, 142), (219, 145), (232, 148)]
RAIL = [(15, 60), (30, 58), (60, 54), (90, 50), (120, 46.5), (155, 47), (180, 50), (203, 54), (224, 57), (238, 54), (248, 45),
        (253, 32), (256, 16), (257, -3)]
# 路：(名字, 控制点, 宽, 等级)  等级 3 = 国道 / 大道，2 = 干道，1 = 小路，0 = 窄巷
ROADS = [
    ('main', [(84, 91), (110, 91), (130, 91), (160, 90.5), (190, 90), (206, 90), (240, 90.5), (271, 91)], 4, 2),
    ('avenue', [(205, 68), (206, 80), (206.5, 90), (208, 112), (210, 130), (211, 146), (212, 163)], 5, 3),
    ('coast', [(281, -3), (279, 10), (278, 24), (276, 40), (275, 56), (273, 70), (271, 84), (270, 96), (264, 106), (254, 113),
               (245, 119), (237, 126), (231, 134), (226, 143), (222, 153), (218, 163), (216, 172), (215, 183)], 4, 2),
    ('national', [(-3, 163), (40, 163), (80, 164), (120, 164), (160, 164), (190, 163.5), (217, 164)], 5, 3),
    ('res_y112', [(104, 112), (120, 112), (161, 112)], 2, 1),
    ('res_y134', [(80, 134), (120, 134), (170, 134), (190, 131.5), (209, 130)], 2, 1),
    ('res_x104', [(104, 91), (104, 163)], 2, 1),
    ('res_x124', [(124, 63), (124, 91), (124, 163)], 2, 1),
    ('res_x158', [(158, 91), (158, 134), (158, 163)], 2, 1),
    ('east_x236', [(236, 90), (236, 70), (236, 57), (233, 48), (230, 46)], 2, 1),
    ('east_y112', [(208, 112), (240, 112), (256, 111)], 2, 1),
    ('station_w', [(205, 71), (195, 72), (184, 72)], 2, 1),
    ('farm', [(84, 91), (75, 86), (67, 79), (61, 73)], 2, 1),
    ('tower', [(61, 73), (55, 65), (51, 57), (49, 50), (47, 45)], 1, 1),
    ('niji', [(104, 134), (93, 137), (83, 140)], 2, 1),
    ('west_lane', [(84, 91), (84, 118), (82, 138), (78, 163)], 1, 1),
    ('villa', [(277, 33), (284, 38), (288, 41)], 1, 1),
    ('east_y128', [(210, 124), (226, 124), (236, 125)], 1, 1),
    ('alley', [(190, 92), (190, 98), (191, 104), (190, 111)], 1, 0),
]


# ================================================================== 房子
ROOFS = ['#c45a42', '#b04a3e', '#4f6f9e', '#5d7fa8', '#5f8d64', '#8a6a4e', '#9a8f86', '#d6893f', '#3f7f86', '#7a5a7e',
         '#6a6e80', '#a0584a']
WALLS = ['#f3eee2', '#ebe1cc', '#e2d8c6', '#f6e9d2', '#ddd6ca', '#efe6d8']


class Town:
    """房子清单：先登记，最后统一画影子、再从北往南画（南边的盖住北边的影子）"""

    def __init__(self):
        self.items = []
        self.occ = np.zeros((H, W), bool)

    def free(self, x0, y0, x1, y1, pad=0):
        if x0 - pad < 0 or y0 - pad < 0 or x1 + pad >= W or y1 + pad >= H:
            return False
        return not self.occ[y0 - pad:y1 + pad + 1, x0 - pad:x1 + pad + 1].any()

    def add(self, x, y, w, d, h, roof, wall=None, kind='gable', sh=None, **kw):
        it = dict(x=int(x), y=int(y), w=int(w), d=int(d), h=int(h), roof=roof, wall=wall or '#efe7d6', kind=kind,
                  sh=sh if sh is not None else (1 if h <= 2 else 2 if h <= 4 else 3 if h <= 7 else 4), **kw)
        self.items.append(it)
        self.occ[it['y']:it['y'] + it['d'] + it['h'], it['x']:it['x'] + it['w']] = True
        return it


def draw_roof(cv, it):
    x, y, w, d, c, k = it['x'], it['y'], it['w'], it['d'], it['roof'], it['kind']
    x1, y1 = x + w - 1, y + d - 1
    if k in ('gable', 'hip', 'kawara'):
        nr = max(0, (d - 2) // 3)
        cv.rect(x, y, x1, y1, c)
        if nr:
            cv.rect(x, y, x1, y + nr - 1, shade(c, 0.16))
        cv.hline(x, x1, y + nr, shade(c, 0.34))                      # 屋脊
        if k == 'kawara':                                               # 瓦：一行行的横纹
            for yy in range(y + nr + 2, y1, 2):
                cv.hline(x, x1, yy, shade(c, -0.14))
        cv.hline(x, x1, y1, shade(c, -0.38))                          # 檐口
        if k == 'hip' and w >= 5:                                      # 四坡：两头的三角面
            for i in range(nr + 1, d - 1):
                t = i - nr
                cv.rect(x, y + i, x + min(t, w // 3) - 1, y + i, shade(c, 0.08)) if t > 0 else None
                cv.rect(x1 - min(t, w // 3) + 1, y + i, x1, y + i, shade(c, -0.2)) if t > 0 else None
        cv.vline(x, y, y1 - 1, shade(c, 0.22))
        cv.vline(x1, y, y1 - 1, shade(c, -0.24))
    elif k == 'gable_ns':
        mid = x + w // 2
        cv.rect(x, y, mid - 1, y1, shade(c, 0.14))
        cv.rect(mid + 1, y, x1, y1, shade(c, -0.16))
        cv.vline(mid, y, y1, shade(c, 0.36))
        cv.hline(x, x1, y, shade(c, 0.22))
        cv.hline(x, x1, y1, shade(c, -0.4))
    elif k == 'arch':                                                   # 拱顶仓库 / 体育馆：横向的筒形明暗
        for i in range(d):
            t = i / max(1, d - 1)
            v = 0.32 - 0.62 * t
            cv.hline(x, x1, y + i, shade(c, v))
        cv.vline(x, y, y1, shade(c, 0.1))
        cv.vline(x1, y, y1, shade(c, -0.3))
        for xx in range(x + 2, x1, 3):
            cv.vline(xx, y + 1, y1 - 1, shade(c, -0.06))
    else:                                                               # flat：平屋顶 + 女儿墙 + 屋顶设备
        cv.rect(x, y, x1, y1, c)
        cv.hline(x, x1, y, shade(c, 0.28))
        cv.vline(x, y, y1, shade(c, 0.18))
        cv.hline(x, x1, y1, shade(c, -0.3))
        cv.vline(x1, y, y1, shade(c, -0.26))
        r = np.random.RandomState(x * 31 + y)
        if w >= 6 and d >= 4:
            for _ in range(1 + (w * d) // 30):
                ax, ay = x + 1 + r.randint(max(1, w - 3)), y + 1 + r.randint(max(1, d - 3))
                cv.px(ax, ay, shade(c, -0.35))
                cv.px(ax + 1, ay, shade(c, 0.2))
        if it.get('tank') and w >= 6:
            tx, ty = x + w - 4, y + 1
            cv.rect(tx, ty, tx + 1, ty + 1, '#c8ccd4')
            cv.px(tx, ty, '#eef0f4')
            cv.px(tx + 1, ty + 1, '#8a8e9a')
    if it.get('sign'):
        sx, sc = it['sign']
        cv.hline(x + sx, x + sx + 1, y + d - 2, sc)


def draw_wall(cv, it):
    x, y, w, d, h, c = it['x'], it['y'] + it['d'], it['w'], it['d'], it['h'], it['wall']
    if h <= 0:
        return
    x1, y1 = x + w - 1, y + h - 1
    cv.rect(x, y, x1, y1, c)
    cv.vline(x, y, y1, shade(c, 0.12))
    cv.vline(x1, y, y1, shade(c, -0.22))
    glass, glass2 = it.get('glass', '#5d7590'), '#a7c6dc'
    r = np.random.RandomState(it['x'] * 7 + it['y'])
    if h <= 2:
        for xx in range(x + 1, x1, 2):
            cv.px(xx, y, glass if r.rand() < 0.85 else glass2)
        door = it.get('door', x + w // 2 if w > 3 else None)
        if door is not None:
            cv.px(door, y1, it.get('door_c', '#6a4630'))
    else:
        floors = it.get('floors') or h - 1
        for f in range(floors):
            yy = y + f
            if yy >= y1:
                break
            step = it.get('wstep', 2)
            for xx in range(x + 1, x1, step):
                cv.px(xx, yy, glass if r.rand() < 0.8 else glass2)
            if it.get('band') and f % 2 == 1:
                cv.hline(x + 1, x1 - 1, yy, shade(c, -0.1))
        # 一楼：店面 / 门
        if it.get('shop'):
            cv.hline(x + 1, x1 - 1, y1, it['shop'])
            for xx in range(x + 1, x1, 2):
                cv.px(xx, y1, shade(it['shop'], 0.3))
        else:
            door = it.get('door', x + w // 2)
            if door is not None:
                cv.px(door, y1, it.get('door_c', '#6a4630'))
                if it.get('door2'):
                    cv.px(door + 1, y1, it.get('door_c', '#6a4630'))
    if it.get('awning'):
        cols = it['awning']
        for i, xx in enumerate(range(x, x1 + 1)):
            cv.px(xx, y + h - 2 if h >= 3 else y, cols[i % len(cols)])
    cv.hline(x, x1, y1, shade(c, -0.3)) if it.get('base') else None


def draw_town(cv, T, ground_mask):
    # 影子：往东南斜着落（不落到别的房子顶上）
    occ = np.zeros((H, W), bool)
    for it in T.items:
        occ[it['y']:it['y'] + it['d'] + it['h'], it['x']:it['x'] + it['w']] = True
    sh_all = np.zeros((H, W), bool)
    for it in T.items:
        m = rmask(it['x'], it['y'], it['x'] + it['w'] - 1, it['y'] + it['d'] + it['h'] - 1)
        s = np.zeros((H, W), bool)
        for k in range(1, it['sh'] + 1):
            s |= shift(m, k, k if k <= 1 else (k + 1) // 2 + (k > 2))
        sh_all |= s
    sh_all &= ~occ & ground_mask
    cv.darken(sh_all)
    for it in sorted(T.items, key=lambda i: (i['y'] + i['d'] + i['h'], i['x'])):
        draw_roof(cv, it)
        draw_wall(cv, it)
        if it.get('post'):
            it['post'](cv, it)


# ================================================================== 树
def tree(cv, x, y, kind='round', c=None, big=False):
    """单棵树（树冠 + 西北高光 + 东南暗边），影子另画"""
    x, y = int(x), int(y)
    if kind == 'pine':
        c = c or '#3f6e48'
        cv.px(x, y - 1, shade(c, 0.25))
        cv.rect(x - 1, y, x + 1, y, c)
        cv.px(x - 1, y, shade(c, 0.18))
        cv.px(x + 1, y, shade(c, -0.25))
        cv.px(x, y + 1, shade(c, -0.3))
        return
    c = c or '#5f9a52'
    if big:
        cv.rect(x - 1, y - 2, x + 1, y + 2, c)
        cv.rect(x - 2, y - 1, x + 2, y + 1, c)
        cv.px(x - 1, y - 1, shade(c, 0.3))
        cv.px(x - 1, y - 2, shade(c, 0.18))
        cv.px(x - 2, y - 1, shade(c, 0.18))
        cv.px(x, y - 1, shade(c, 0.12))
        cv.px(x + 2, y + 1, shade(c, -0.3))
        cv.px(x + 1, y + 2, shade(c, -0.3))
        cv.px(x + 1, y + 1, shade(c, -0.14))
    else:
        cv.px(x, y - 1, shade(c, 0.16))
        cv.px(x - 1, y, shade(c, 0.2))
        cv.px(x, y, c)
        cv.px(x + 1, y, shade(c, -0.2))
        cv.px(x, y + 1, shade(c, -0.32))
        cv.px(x - 1, y - 1, shade(c, 0.34)) if kind == 'round2' else None


def tree_shadow(m, x, y, big=False):
    x, y = int(x), int(y)
    if big:
        for dx, dy in ((2, 2), (3, 1), (3, 2), (2, 3), (1, 3), (3, 0)):
            if 0 <= x + dx < W and 0 <= y + dy < H:
                m[y + dy, x + dx] = True
    else:
        for dx, dy in ((1, 1), (2, 1), (1, 2)):
            if 0 <= x + dx < W and 0 <= y + dy < H:
                m[y + dy, x + dx] = True


def canopy(cv, mask, light, seed, tones=('#2f5638', '#3f6b45', '#4f7f4d', '#66955a', '#80ad68', '#9cc27a'), spacing=2.2,
           under='#2c4d36'):
    """一片林子：先铺暗底，再一颗颗画树冠（光照决定色调），从北往南画"""
    cv.fill(mask, under)
    r = np.random.RandomState(seed)
    pts = []
    for gy in np.arange(0, H, spacing):
        for gx in np.arange(0, W, spacing):
            x = int(gx + r.rand() * spacing)
            y = int(gy + r.rand() * spacing)
            if 0 <= x < W and 0 <= y < H and mask[y, x]:
                pts.append((y, x))
    pts.sort()
    for y, x in pts:
        v = light[y, x] + (r.rand() - 0.5) * 0.25
        i = int(np.clip(v * (len(tones) - 1) + 0.5, 1, len(tones) - 1))
        c = tones[i]
        hi = tones[min(len(tones) - 1, i + 1)]
        lo = tones[max(0, i - 2)]
        for dx, dy, cc in ((0, -1, hi), (-1, 0, hi), (0, 0, c), (1, 0, c), (0, 1, lo), (1, 1, lo), (-1, -1, None)):
            xx, yy = x + dx, y + dy
            if cc and 0 <= xx < W and 0 <= yy < H and mask[yy, xx]:
                cv.a[yy, xx] = rgb(cc)
        if r.rand() < 0.35 and 0 <= y - 1 < H and 0 <= x - 1 < W and mask[y - 1, x - 1]:
            cv.a[y - 1, x - 1] = rgb(tones[min(len(tones) - 1, i + 2)])


# ================================================================== 主流程
def base():
    cv = Cv('#b9d08f')

    # -------------------------------------------------------------- 海陆
    coast = spline(COAST)
    sea = pmask(coast + [(340, 190), (340, -10)])
    land = ~sea
    dsea = ndi.distance_transform_edt(sea)
    dland = ndi.distance_transform_edt(land)

    # 高度图：西北大山 + 北边丘陵 + 东北海岬的小山（光从西北来）
    n1, n2 = fbm(7, 28, 5), fbm(11, 10, 3)
    hgt = np.zeros((H, W))
    for cx, cy, rx, ry, a in ((28, 6, 66, 44, 1.0), (86, 2, 44, 32, .85), (6, 44, 26, 24, .62), (128, -2, 40, 22, .55),
                              (190, 2, 50, 28, .5), (238, 14, 26, 20, .42), (296, 40, 13, 9, .30), (2, 174, 24, 14, .32)):
        hgt += a * np.exp(-(((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2) * 1.6)
    hgt = hgt * (0.78 + 0.44 * n1) + 0.08 * n2 * (hgt > 0.08)
    hgt[sea] = 0
    gy, gx = np.gradient(ndi.gaussian_filter(hgt, 1.0))
    light = np.clip(0.52 + (gx + gy) * 12.0, 0, 1)                    # 朝西北的坡亮
    hill = (hgt > 0.17) & land

    # -------------------------------------------------------------- 地面：草地（底色 + 斑驳）
    g = fbm(3, 14, 4)
    cv.dith(land, '#aec784', np.clip((g - 0.45) * 2.2, 0, 1))
    cv.dith(land, '#c4d99a', np.clip((0.42 - g) * 2.4, 0, 1))
    cv.dith(land & (hgt > 0.09) & ~hill, '#9dbe78', 0.5)               # 山脚

    # -------------------------------------------------------------- 田：水田（西南）、旱田 / 牧场（西北）
    fields = np.zeros((H, W), bool)

    def paddies(x0, y0, x1, y1, seed, cols=('#9fc46f', '#b2cf7c', '#a7c977', '#c2d58a', '#93bd68'), cw=(7, 12), ch=(5, 8)):
        r = np.random.RandomState(seed)
        y = y0
        while y < y1:
            hh = r.randint(*ch)
            x = x0 - r.randint(0, 5)
            while x < x1:
                ww = r.randint(*cw)
                c = cols[r.randint(len(cols))]
                m = rmask(max(x0, x), y, min(x1, x + ww - 2), min(y1, y + hh - 2)) & land & ~hill
                cv.fill(m, c)
                cv.dith(m, shade(c, 0.14), 0.16)
                if r.rand() < 0.4:                                     # 秧苗的行
                    for yy in range(y + 1, min(y1, y + hh - 2), 2):
                        cv.dith(m & (YY == yy), shade(c, -0.1), 0.5)
                fields[m] = True
                cv.fill(rmask(x + ww - 1, y, x + ww - 1, min(y1, y + hh - 1)) & land & ~hill & (XX >= x0), '#d8d0a0')
                x += ww
            cv.fill(rmask(x0, y + hh - 1, x1, y + hh - 1) & land & ~hill, '#d8d0a0')
            y += hh

    paddies(6, 85, 80, 129, 31)
    paddies(6, 147, 76, 161, 32)
    paddies(6, 167, 100, 176, 35)
    paddies(26, 60, 50, 70, 34, cols=('#cdb768', '#d8c47a', '#bfc070', '#c9bd6c'), cw=(5, 9), ch=(3, 5))   # 麦田
    # 用水路（田中间的直水沟）
    ditch = (rmask(6, 128, 80, 128) | rmask(44, 85, 44, 128)) & land
    cv.fill(ditch, '#6aaed6')
    cv.fill(shift(ditch, 0, 1) & land & ~ditch, '#a9b87e')

    # -------------------------------------------------------------- 山：林冠（一颗颗树）+ 山顶岩石
    canopy(cv, hill, light, 5)
    # 山脊线：亮暗交界处点一点亮色
    ridge = hill & (light > 0.62) & shift(light < 0.45, 1, 1)
    cv.dith(ridge, '#b6d48a', 0.6)

    # -------------------------------------------------------------- 葡萄园（葡萄丘这个名字的由来）：林子和铁路之间的坡上
    vine = (pmask([(92, 30), (150, 26), (150, 43), (96, 46)]) | pmask([(160, 30), (208, 27), (210, 44), (162, 46)])) & land & ~hill
    vine &= ~lmask(spline(RIVER), 9)
    cv.fill(vine, '#cdbd8c')
    cv.dith(vine, '#c2b07e', 0.3)
    for y in range(24, 48, 2):
        row = vine & (YY == y)
        cv.fill(row, '#5f8a4a')
        cv.dith(row & ((XX + y) % 4 == 0), '#7a4a8a', 1.0)             # 一串串葡萄
        cv.dith(row & ((XX + y * 3) % 7 == 0), '#86b060', 1.0)
    cv.fill(inner_edge(vine) & (shift(~vine, 0, 1) | shift(~vine, 1, 0)), '#a89a70')
    fields |= vine

    # -------------------------------------------------------------- 牧场
    pasture = pmask([(60, 58), (94, 56), (96, 82), (62, 82)]) & land & ~hill & ~fields
    cv.fill(pasture, '#bfd890')
    cv.dith(pasture, '#aecd84', np.clip(fbm(5, 4, 2) - 0.35, 0, 1))
    fence = inner_edge(pasture)
    cv.dith(fence, '#8a6e4e', 0.6)

    # -------------------------------------------------------------- 市区地面
    town = (pmask([(98, 86), (166, 85), (172, 120), (178, 132), (200, 140), (214, 160), (98, 162)])
            | pmask([(158, 56), (252, 56), (268, 78), (270, 100), (262, 108), (236, 124), (222, 150), (210, 160), (184, 140),
                     (166, 108), (160, 88)])
            | pmask([(210, 30), (246, 30), (250, 52), (210, 52)])
            | pmask([(272, 26), (300, 34), (296, 50), (276, 52)])
            | pmask([(160, 150), (222, 150), (218, 176), (100, 176), (100, 166)]))
    town &= land & ~hill
    tex = fbm(9, 3, 2)
    cv.fill(town, '#e0d8c2')
    cv.dith(town, '#d5ccb4', np.clip((tex - 0.55) * 3, 0, 1))
    cv.dith(town, '#e9e2cf', np.clip((0.4 - tex) * 3, 0, 1))
    cv.dith(outer_edge(town) & land & ~hill, '#cfd0a6', 0.6)

    # -------------------------------------------------------------- 海
    depth = np.clip(dsea / 44.0, 0, 1)
    sea_cols = ['#8fd0e6', '#72bde2', '#5aa8d8', '#4b95cb', '#4083be', '#3872b1']
    cv.fill(sea, sea_cols[0])
    for i, c in enumerate(sea_cols[1:], 1):
        lo = (i - 0.5) / (len(sea_cols) - 1) * 0.9
        cv.dith(sea, c, np.clip((depth - lo) * 6, 0, 1))
    wr = np.random.RandomState(77)
    for _ in range(460):
        x, y = wr.randint(196, W), wr.randint(0, H)
        if not sea[y, x] or dsea[y, x] < 3:
            continue
        if STAMP[0] - 3 <= x <= STAMP[2] + 3 and STAMP[1] - 3 <= y <= STAMP[3] + 3 and wr.rand() < 0.7:
            continue
        L = wr.randint(2, 5)
        c = '#b4e2f3' if dsea[y, x] < 16 else '#7fbde2' if dsea[y, x] < 32 else '#5d9fd0'
        for k in range(L):
            if 0 <= x + k < W and sea[y, x + k]:
                cv.px(x + k, y, c)
        if L >= 4 and 0 <= y - 1:
            cv.px(x + 1, y - 1, c)
    shallow = sea & (dsea <= 2.5)
    cv.dith(shallow, '#a8dff0', 0.6)
    cv.dith(sea & (dsea <= 1.0), '#effafd', 0.8)
    cv.dith(sea & (dsea > 2.5) & (dsea <= 4.2), '#d2eff9', np.clip(fbm(41, 3, 2) - 0.45, 0, 1) * 2)

    # 沙滩（海岬南边到港口北边、南边海岸一线）、岩岸（海岬一圈）
    beach = land & (dland <= 4.5) & (YY > 52) & (YY < 80)
    beach |= land & (dland <= 2.4) & (YY >= 112) & (YY < 180)
    cv.fill(beach, '#eedba4')
    cv.dith(beach, '#f7eabf', np.clip(fbm(13, 3, 2) - 0.45, 0, 1) * 2)
    cv.dith(beach & (dland <= 1.2), '#d8c38b', 0.65)
    rocky = land & (dland <= 2.6) & (YY <= 52) & (XX > 276)
    cv.fill(rocky, '#958671')
    cv.dith(rocky, '#bcae94', np.clip(0.7 - dland / 4, 0, 1))
    cv.dith(rocky & (dland <= 1.2), '#6c6052', 0.55)
    cliff = land & (dland <= 1.6) & (YY > 36) & (YY < 52) & (XX > 290)
    cv.fill(cliff, '#6a5b4b')
    cv.fill(cliff & shift(~cliff, 0, -1) & land, '#8a7a64')
    # 岸边的礁石
    for x, y in ((309, 43), (306, 49), (287, 22), (289, 54), (310, 38), (284, 12)):
        if sea[y, x]:
            cv.px(x, y, '#6c6052')
            cv.px(x - 1, y, '#9a8a74')
            cv.px(x, y + 1, '#eef9fd')

    # -------------------------------------------------------------- 河：堤岸 + 水面
    rc = spline(RIVER)
    widths = np.interp(np.linspace(0, 1, len(rc)), [0, 0.45, 1], [3.0, 4.0, 6.5])
    bank = np.zeros((H, W), bool)
    water = np.zeros((H, W), bool)
    rcore = np.zeros((H, W), bool)
    for (x, y), w in zip(rc[::2], widths[::2]):
        bank |= emask(x, y, w / 2 + 2.4, w / 2 + 2.4)
        water |= emask(x, y, w / 2, w / 2)
        rcore |= emask(x, y, max(0.6, w / 2 - 1.5), max(0.6, w / 2 - 1.5))
    bank &= land & ~water
    water &= land | (dsea < 4)
    fb = bank & ~hill
    cv.fill(fb, '#bfcc92')
    cv.dith(fb, '#a6c17e', 0.4)
    cv.fill(inner_edge(bank | water) & fb, '#d0c8a0')                 # 堤顶的小路
    cv.fill(water, '#5ea7d5')
    cv.dith(rcore & water, '#7cbfe3', 0.55)
    cv.fill(water & shift(~water & land, -1, -1), '#4a8fc0')           # 东南岸的暗边（水面看不见那边）
    cv.fill(water & shift(~water & land, 1, 1) & ~rcore, '#87c6e6')
    for i in range(12, len(rc) - 6, 19):
        x, y = rc[i]
        cv.px(x, y, '#d0eefa')
    # 河口的沙洲
    cv.dith(land & (dland <= 2) & emask(226, 149, 8, 5) & ~water, '#e4d29a', 0.7)

    # -------------------------------------------------------------- 路
    roads = {}
    allroad = np.zeros((H, W), bool)
    for name, pts, w, lvl in ROADS:
        c = spline(pts)
        m = lmask(c, w)
        m &= ~sea
        roads[name] = (m, lvl, c, w)
        allroad |= m
    bridge = allroad & (water | (sea & (dsea < 3)))
    road_land = allroad & ~bridge
    edge_c = '#a89a7c'
    cv.fill(outer_edge(allroad) & land & ~water & ~bridge, edge_c)
    for lvl, c in ((0, '#c9bc9c'), (1, '#f1ebdc'), (2, '#fbf7ec'), (3, '#f6e6ae')):
        for name, (m, lv, cc, w) in roads.items():
            if lv == lvl:
                cv.fill(m, c)
    # 桥：桥面 + 两边栏杆 + 水上的影子
    br = bridge
    cv.fill(br, '#efe9da')
    rail_px = outer_edge(br) & (water | sea)
    cv.fill(rail_px, '#7a6e62')
    cv.darken(shift(br | rail_px, 1, 2) & water & ~br & ~rail_px, (0.6, 0.66, 0.8))
    # 大道 / 国道的中线（虚线）
    for name in ('avenue', 'national'):
        m, lv, cc, w = roads[name]
        for i, (x, y) in enumerate(pixpath(cc)):
            if i % 4 < 2 and 0 <= x < W and 0 <= y < H and m[y, x] and not br[y, x]:
                cv.px(x, y, '#ffffff')
    # 斑马线
    for x0, x1, y in ((204, 209, 86), (204, 209, 94), (205, 209, 108)):
        for x in range(x0, x1 + 1):
            if (x - x0) % 2 == 0:
                cv.px(x, y, '#ffffff')
    for y0, y1, x in ((88, 92, 202), (88, 92, 211), (161, 166, 207), (88, 92, 156)):
        for y in range(y0, y1 + 1):
            if (y - y0) % 2 == 0:
                cv.px(x, y, '#ffffff')

    # -------------------------------------------------------------- 铁路：道床 + 枕木 + 两条轨 + 铁桥 + 隧道口
    rl = spline(RAIL, 0.2)
    fr = frames(rl)
    bed = lmask(rl, 5) & ~sea
    over_water = bed & water
    cv.fill(bed & ~over_water, '#bdb5a4')
    cv.dith(bed & ~over_water, '#a8a090', 0.3)
    cv.darken(outer_edge(bed) & shift(bed, 1, 1) & land & ~water & ~allroad, (0.82, 0.84, 0.9))
    for x, y, tx, ty, s in fr:
        nx, ny = -ty, tx
        if int(s) % 3 == 0:                                             # 枕木（每 3 px 一根）
            for t in (-1.5, -0.75, 0, 0.75, 1.5):
                cv.px(x + nx * t, y + ny * t, '#8a6e54')
    for x, y, tx, ty, s in fr:
        nx, ny = -ty, tx
        cv.px(x + nx * 1.05, y + ny * 1.05, '#56505c')
        cv.px(x - nx * 1.05, y - ny * 1.05, '#625c68')
    # 铁桥：桁架（两边一明一暗交替）+ 水上的影子
    for x, y, tx, ty, s in fr:
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < W and 0 <= yi < H and water[yi, xi]:
            nx, ny = -ty, tx
            for t, c in ((2.3, '#3c3a48' if int(s) % 2 else '#8c8a98'), (-2.3, '#3c3a48' if int(s) % 2 == 0 else '#9a98a6')):
                cv.px(x + nx * t, y + ny * t, c)
    cv.darken(shift(over_water, 1, 3) & water & ~over_water, (0.6, 0.66, 0.8))
    # 隧道口（铁路从西边山里钻出来）
    tx0, ty0 = 15, 60
    cv.rect(tx0 - 3, ty0 - 4, tx0, ty0 + 3, '#7a7466')
    cv.rect(tx0 - 2, ty0 - 3, tx0, ty0 + 2, '#2a2430')
    cv.hline(tx0 - 3, tx0, ty0 - 4, '#a8a292')
    cv.px(tx0 - 3, ty0 + 3, '#5a5448')

    S = dict(cv=cv, sea=sea, land=land, hill=hill, hgt=hgt, light=light, water=water, bank=bank, dsea=dsea, dland=dland,
             river=rc, town=town, roads=roads, allroad=allroad, bridge=bridge, bed=bed, fields=fields, pasture=pasture,
             beach=beach, rail=fr)
    return S


# ================================================================== 地面上的东西：车站月台和站前广场、操场、泳池、停车场、院子、码头、防波堤
def ground(S):
    cv, sea, land, water = S['cv'], S['sea'], S['land'], S['water']
    rl = S['railc']

    def paved(x0, y0, x1, y1, c='#e8e2d3', edge='#b1a68c'):
        cv.rect(x0, y0, x1, y1, c)
        m = rmask(x0, y0, x1, y1)
        cv.fill(outer_edge(m) & ~S['allroad'] & ~S['bed'] & land & ~water, edge)

    # ---- 车站：北侧月台（顺着铁路弯）+ 雨棚、南面站前广场（环岛）
    for x in range(186, 219):
        c = along(rl, x)
        yc = int(round(c))
        cv.px(x, yc - 4, '#d8d3c6')
        cv.px(x, yc - 3, '#ece8dc')
        cv.px(x, yc - 5, '#8e887a')
        if 191 <= x <= 213:
            cv.px(x, yc - 4, '#7f9c8a' if x % 6 else '#5f7c6a')       # 雨棚
    paved(191, 63, 216, 70, '#ebe5d6')
    isl = emask(202.5, 66.5, 4.6, 2.2)
    cv.fill(isl, '#9cc77a')
    cv.fill(inner_edge(isl), '#d8d0b8')
    for x in (193, 195, 197):                                         # 公交站的候车棚
        cv.px(x, 63, '#6f8fa8')
    # ---- 高中操场（土）+ 跑道 + 球门、泳池
    yard = rmask(160, 74, 192, 86)
    cv.fill(yard, '#d8c19c')
    cv.dith(yard, '#ceb590', np.clip(fbm(61, 3, 2) - 0.4, 0, 1) * 1.6)
    trk = emask(176, 80, 13, 4.6) & ~emask(176, 80, 11.6, 3.4)
    cv.fill(trk & yard, '#f3ede0')
    cv.fill(inner_edge(yard), '#a89272')
    for y in (78, 81):
        cv.px(164, y, '#ffffff')
        cv.px(188, y, '#ffffff')
    paved(194, 73, 203, 80, '#e7e3d8')
    pool = rmask(195, 74, 202, 79)
    cv.fill(pool, '#5bb7e2')
    cv.fill(rmask(195, 74, 202, 74), '#3f97c8')
    for x in (197, 199, 201):
        cv.vline(x, 75, 79, '#bfe8f6')
    # ---- 中学操场 + 棒球场
    yard2 = rmask(127, 61, 150, 84)
    cv.fill(yard2, '#d8c19c')
    cv.dith(yard2, '#ceb590', np.clip(fbm(62, 3, 2) - 0.4, 0, 1) * 1.6)
    cv.fill(inner_edge(yard2), '#a89272')
    dia = pmask([(138, 66), (145, 73), (138, 80), (131, 73)])
    cv.fill(dia, '#c9a77c')
    cv.fill(inner_edge(dia), '#f3ede0')
    cv.dith(rmask(133, 69, 143, 77) & dia & ~inner_edge(dia), '#b9cf86', 0.0)
    cv.hline(136, 140, 81, '#6a6470')                                  # 挡球网
    # ---- 超市停车场
    paved(86, 118, 102, 131, '#bdb9b0', '#8e887c')
    for x in range(88, 102, 3):
        cv.vline(x, 119, 121, '#f2f0ea')
        cv.vline(x, 127, 129, '#f2f0ea')
    # ---- 东方家院子、吉良家旧宅的院墙和池子、虹村家的荒院和铁栅栏
    gard = rmask(106, 114, 122, 131)
    cv.fill(gard, '#a9ca7e')
    cv.dith(gard, '#9cc072', 0.3)
    cv.fill(inner_edge(gard), '#4f7f4d')
    cv.rect(117, 127, 118, 132, '#ece6d6')                             # 车道
    kira = rmask(125, 97, 135, 110)
    cv.fill(kira, '#b7c98c')
    cv.fill(inner_edge(kira), '#b5a78c')
    cv.rect(127, 106, 129, 107, '#5ea7d5')                             # 院子里的池子
    cv.px(127, 106, '#8fcbea')
    niji = rmask(57, 124, 84, 152)
    cv.fill(niji, '#7f9b5e')
    cv.dith(niji, '#6a8650', np.clip(fbm(71, 3, 2) - 0.3, 0, 1) * 1.5)
    cv.dith(niji, '#9aa66a', np.clip(0.35 - fbm(72, 3, 2), 0, 1) * 2)
    fen = inner_edge(niji)
    cv.dith(fen, '#3a3640', 0.75)
    cv.rect(83, 139, 84, 141, '#c9bc9c')                               # 门口
    # ---- 露伴家的院子、别墅区的院子
    for x0, y0, x1, y1 in ((216, 35, 241, 52), (279, 36, 297, 50), (270, 25, 281, 34), (289, 27, 300, 35)):
        m = rmask(x0, y0, x1, y1) & land & ~S['allroad'] & ~S['bed']
        cv.fill(m, '#a6c87c')
        cv.dith(m, '#b8d48c', 0.3)
        cv.fill(inner_edge(m), '#c9c1a6')
    cv.rect(295, 44, 298, 46, '#5bb7e2')                               # 别墅的泳池
    cv.hline(295, 298, 44, '#3f97c8')
    # ---- 河边公园（池塘一圈小路）
    park = pmask([(173, 119), (180, 117), (198, 121), (201, 129), (190, 132), (178, 129)]) & land & ~water & ~S['bank']
    cv.fill(park, '#b2d08a')
    cv.dith(park, '#a3c67e', 0.3)
    ring = emask(186, 125, 7.5, 4.6) & ~emask(186, 125, 6.4, 3.6) & park
    cv.fill(ring, '#e2d6b4')
    cv.fill(S['pond'], '#69b1da')
    cv.fill(inner_edge(S['pond']) & shift(S['pond'], -1, -1), '#4a8fc0')
    cv.px(184, 124, '#d2f0fb')
    cv.px(185, 124, '#d2f0fb')
    # ---- 天使岩的小广场
    cv.fill(emask(238, 117, 4.5, 2.6) & land, '#e6dfcc')
    # ---- 神社（林子里一块空地）
    cl = emask(74, 34, 6.5, 4.8)
    cv.fill(cl, '#cdbf98')
    cv.dith(cl, '#bfb088', 0.3)
    cv.vline(74, 38, 47, '#cdbf98')
    cv.vline(75, 40, 47, '#bfb088')
    # ---- 港口：码头场地、三道栈桥、两道防波堤
    yard3 = pmask([(256, 76), (278, 75), (277, 88), (275, 96), (271, 104), (262, 107), (256, 104)]) & land
    cv.fill(yard3, '#cbc5b6')
    cv.dith(yard3, '#bdb7a8', 0.25)
    piers = rmask(276, 86, 297, 92) | rmask(276, 77, 291, 80) | rmask(270, 98, 289, 101)
    cv.darken(shift(piers, 1, 1) & sea & ~piers, (0.62, 0.68, 0.82))
    cv.fill(piers, '#cdc6b6')
    cv.fill(inner_edge(piers) & shift(~piers, 0, -1), '#e6e0d2')
    cv.fill(inner_edge(piers) & (shift(~piers, 0, 1) | shift(~piers, 1, 0)), '#8f877a')
    for x in range(278, 297, 3):                                       # 系船柱
        cv.px(x, 86, '#5a5662')
        cv.px(x, 92, '#5a5662')
    bw1 = lmask(spline([(288, 56), (295, 62), (299, 69), (301, 77)]), 2) & sea
    bw2 = lmask(spline([(274, 106), (285, 107.5), (297, 106)]), 2) & sea
    for bw in (bw1, bw2):
        cv.darken(shift(bw, 1, 1) & sea & ~bw, (0.62, 0.68, 0.82))
        cv.fill(bw, '#b9b2a4')
        cv.dith(bw, '#8d8678', 0.4)
        cv.dith(outer_edge(bw) & sea, '#e9f7fc', 0.5)
    S['piers'] = piers


# ================================================================== 房子：地标（对准图钉）+ 各街区成片的住家 / 商店
def town(S):
    T = Town()
    blocked = S['allroad'] | S['water'] | S['bed'] | S['sea'] | S['bank'] | S['hill'] | S['pond']
    blocked |= ndi.binary_dilation(S['allroad'] | S['water'] | S['bed'], iterations=1)
    T.occ |= blocked
    trees = []
    A = T.add

    def post_bank(cv, it):
        x, y = it['x'], it['y'] + it['d']
        for xx in range(x + 1, x + it['w'] - 1, 2):                   # 列柱
            cv.vline(xx, y + 2, y + 4, '#f6f2e8')
            cv.vline(xx + 1, y + 2, y + 4, '#bdb5a6')
        cv.rect(x + 5, y + 3, x + 7, y + 4, '#5d7590')                 # 大门
        for dx, dy in ((5, 2), (6, 2), (7, 2), (5, 3), (6, 3), (6, 4)):  # 屋顶的葡萄招牌
            cv.px(it['x'] + dx, it['y'] + dy - 1, '#7a4a9a' if (dx + dy) % 2 else '#9a6abc')
        cv.px(it['x'] + 6, it['y'], '#5f8d4a')

    def post_station(cv, it):
        cv.px(it['x'] + 9, it['y'] + 1, '#ffffff')                     # 钟
        cv.px(it['x'] + 9, it['y'] + 2, '#3a3a48')
        cv.rect(it['x'] + 8, it['y'] + it['d'] + 1, it['x'] + 10, it['y'] + it['d'] + 2, '#3e4a5e')   # 进站口

    def post_niji(cv, it):
        x, y = it['x'], it['y'] + it['d']
        for xx, yy in ((x + 3, y), (x + 9, y + 2), (x + 15, y), (x + 12, y + 1)):
            cv.px(xx, yy, '#1e1c26')                                   # 破窗
        cv.vline(x + 10, it['y'] - 1, it['y'] + 1, '#4a4c5c')          # 小塔楼的尖
        cv.px(x + 10, it['y'] - 2, '#6a6c7c')

    def post_hotel(cv, it):
        x, y = it['x'], it['y']
        cv.rect(x + 2, y + 1, x + 8, y + 2, '#c8403a')                 # 屋顶招牌
        cv.hline(x + 2, x + 8, y + 1, '#e0605a')

    def post_hosp(cv, it):
        x, y = it['x'], it['y']
        hp = emask(x + 14, y + 3, 2.6, 1.7)
        cv.fill(hp, '#9fb59a')
        cv.px(x + 14, y + 3, '#ffffff')
        cv.px(x + 13, y + 3, '#ffffff')
        cv.px(x + 15, y + 3, '#ffffff')

    # ---- 地标（坐标见文件头 PINS）
    A(194, 57, 19, 3, 3, '#c8503c', '#f1ead8', kind='hip', door=None, sh=1, post=post_station, floors=1)        # 杜王站 (203,62)
    A(159, 61, 23, 5, 5, '#cfc9be', '#f1ece0', kind='flat', floors=4, wstep=2, door=169, door2=True, tank=True)   # 葡萄丘高中 (170,70)
    A(184, 61, 9, 6, 2, '#5f8f72', '#e9e2d0', kind='arch', door=188)                                               # 体育馆
    A(128, 50, 21, 4, 5, '#d2ccc0', '#efe9dc', kind='flat', floors=4, door=137, door2=True, tank=True)            # 葡萄丘中学 (138,58)
    A(114, 52, 8, 5, 2, '#6a8fa0', '#e6dfcf', kind='arch', door=117)                                               # 中学体育馆
    A(216, 73, 13, 5, 5, '#d6cfc2', '#ece6da', kind='flat', door=None, floors=1, post=post_bank, sh=2)            # 葡萄丘银行 (222,82)
    A(208, 81, 7, 3, 3, '#c8789a', '#f6ece6', kind='gable', awning=['#e88ab0', '#ffffff'], door=212)               # 灰姑娘美容院 (214,86)
    A(182, 95, 7, 3, 3, '#6a6e80', '#eee6d6', kind='gable', awning=['#4f6fa8', '#ffffff'], door=186)               # 裁缝店 (188,100)
    A(143, 93, 8, 3, 3, '#c8603a', '#f3e9d6', kind='kawara', awning=['#3f8f4a', '#ffffff', '#c8403a'], door=147)   # 意大利餐厅 (146,98)
    A(136, 95, 7, 3, 3, '#8a6a4e', '#e9dfcc', kind='gable', door=139)                                              # 宫本的屋子 (140,100)
    A(137, 101, 7, 2, 2, '#4f6f9e', '#efe6d8', kind='gable', door=140)                                             # 住宅区 (140,104)
    A(125, 99, 10, 3, 3, '#5c6170', '#ebe3cf', kind='kawara', door=130)                                            # 吉良家旧宅 (130,104)
    A(110, 118, 13, 5, 4, '#56688a', '#f2ede2', kind='hip', door=118, sh=2)                                        # 东方家 (118,126)
    A(107, 139, 11, 4, 4, '#5d7fa8', '#efe6d8', kind='hip', door=112)                                              # 川尻家 (112,146)
    A(145, 143, 10, 4, 4, '#b04a3e', '#f3eee2', kind='gable', door=150)                                            # 康一家 (150,150)
    A(86, 107, 16, 5, 5, '#d9d3c6', '#f2eee4', kind='flat', shop='#5d7590', floors=3, sign=(5, '#e07a2a'))        # 超市 (94,116)
    A(60, 130, 20, 6, 5, '#565b6b', '#c4b9a6', kind='hip', glass='#3a3a48', door=70, door2=True, post=post_niji, sh=2)  # 虹村家 (70,140)
    A(221, 40, 14, 5, 4, '#4f7f86', '#f2ece0', kind='gable', door=228, sh=2)                                       # 露伴宅 (228,48)
    A(282, 39, 12, 4, 4, '#b8503e', '#f6f2ea', kind='hip', door=288, sh=2)                                         # 海边别墅 (288,46)
    A(272, 28, 8, 3, 3, '#4f6f9e', '#f2ede2', kind='hip', door=275)
    A(291, 29, 8, 3, 3, '#5f8d64', '#f6efe2', kind='hip', door=294)
    A(53, 63, 10, 5, 3, '#a8483e', '#d8c6a8', kind='gable_ns', door=57, door_c='#5a3a2a', door2=True)            # 牧场的仓库 (58,70)
    A(66, 71, 8, 4, 2, '#5c6170', '#e3d8c0', kind='kawara', door=69)                                               # 牧场主家
    A(174, 112, 11, 4, 3, '#5f8d64', '#e9dfcc', kind='gable', door=179, door2=True)                                # 图书馆
    A(226, 95, 18, 6, 6, '#e6e4de', '#f4f2ec', kind='flat', floors=5, door=234, door2=True, post=post_hosp)        # 医院
    A(244, 60, 11, 5, 12, '#d4cec2', '#ebe5d8', kind='flat', floors=11, door=249, door2=True, tank=True, post=post_hotel, band=True)  # 杜王大酒店
    A(259, 80, 12, 4, 2, '#8aa0b4', '#dcd6c8', kind='arch', door=264, door2=True)                                  # 港口仓库
    A(258, 92, 11, 4, 2, '#b48a6a', '#dcd6c8', kind='arch', door=262, door2=True)
    A(70, 30, 9, 3, 2, '#4a4a58', '#d8c8a8', kind='kawara', door=74, door2=True)                                               # 神社

    T.occ[112:121, 232:245] = True                                    # 天使岩的小广场
    # ---- 成片的房子：按街区一排排紧挨着放（每次只挪 1 px 找空位），放不下的空当种树
    def lots(x0, y0, x1, y1, seed, roofs, walls=None, d=(3, 4), h=(2, 3), w=(5, 8), gap=(1, 1), kinds=('gable', 'gable', 'hip', 'gable_ns'),
             flat=False, shops=0.0, tall=None, tree_p=0.35, gardens=True):
        r = np.random.RandomState(seed)
        walls = walls or WALLS
        y = y0
        while y <= y1:
            dd, hh = r.randint(d[0], d[1] + 1), r.randint(h[0], h[1] + 1)
            if tall and r.rand() < tall[0]:
                hh = r.randint(tall[1][0], tall[1][1] + 1)
            if y + dd + hh - 1 > y1:
                dd, hh = d[0], h[0]
                if y + dd + hh - 1 > y1:
                    break
            x = x0
            while x <= x1:
                ww = min(r.randint(w[0], w[1] + 1), x1 - x + 1)
                if ww < w[0]:
                    break
                done = False
                for dy in (0, 1, -1):
                    yy = y + dy
                    if yy < y0 or yy + dd + hh - 1 > y1:
                        continue
                    if T.free(x, yy, x + ww - 1, yy + dd + hh - 1):
                        kw = {}
                        if shops and r.rand() < shops:
                            kw['awning'] = [['#c8403a', '#ffffff'], ['#3f6fa8', '#ffffff'], ['#3f8f4a', '#f6e6ae'],
                                            ['#e08a3a', '#ffffff'], ['#8a5a9a', '#f4e6f0']][r.randint(5)]
                        kind = 'flat' if flat else kinds[r.randint(len(kinds))]
                        A(x, yy, ww, dd, hh, roofs[r.randint(len(roofs))], walls[r.randint(len(walls))], kind=kind, **kw)
                        x += ww + r.randint(gap[0], gap[1] + 1)
                        if r.rand() < tree_p * 0.5 and T.free(x, yy + 1, x + 2, yy + 3):
                            trees.append((x + 1, yy + 2, 'round', None, False))
                            x += 3
                        done = True
                        break
                if not done:
                    x += 1
            y += dd + hh + 1
        if gardens:
            garden_blocks.append((x0, y0, x1, y1))

    PAL_RES = ['#c45a42', '#b04a3e', '#4f6f9e', '#5d7fa8', '#5f8d64', '#8a6a4e', '#9a8f86', '#6a6e80', '#a0584a', '#3f7f86',
               '#c06a48', '#56688a']
    FLATS = ['#d4cec2', '#cbc5ba', '#dcd6ca', '#c4c0b8', '#d8d0c0', '#bfc4c8', '#d0cabc']
    garden_blocks = []
    # 西岸住宅区（街区内边界：路宽 + 1 px）
    lots(107, 95, 122, 110, 101, PAL_RES)
    lots(127, 94, 156, 110, 102, PAL_RES)
    lots(107, 115, 122, 132, 103, PAL_RES)
    lots(127, 115, 156, 132, 104, PAL_RES)
    lots(107, 137, 122, 159, 105, PAL_RES)
    lots(127, 137, 156, 159, 106, PAL_RES)
    lots(161, 94, 172, 132, 107, PAL_RES, w=(5, 7))
    lots(86, 95, 102, 105, 108, PAL_RES)
    lots(86, 133, 102, 159, 109, PAL_RES)
    lots(86, 58, 112, 86, 110, PAL_RES, tree_p=0.6)                 # 中学西边一片新住宅
    # 河南岸、国道南
    lots(161, 137, 206, 159, 111, PAL_RES)
    lots(100, 168, 215, 175, 112, PAL_RES + ['#d6893f'], d=(3, 3), h=(2, 2), tree_p=0.25)
    # 东岸：商店街、闹市（平顶为主，夹几栋高的）
    lots(193, 81, 203, 87, 113, FLATS, flat=True, d=(3, 3), h=(3, 3), shops=0.9, gardens=False)
    lots(162, 94, 203, 110, 114, FLATS + PAL_RES, kinds=('gable', 'flat', 'flat'), shops=0.6, w=(5, 8), gardens=False)
    lots(209, 58, 243, 71, 115, FLATS, flat=True, d=(4, 5), h=(4, 6), w=(6, 11), tall=(0.3, (7, 9)), tree_p=0.15, gardens=False)
    lots(230, 72, 272, 87, 116, FLATS, flat=True, d=(3, 5), h=(3, 6), w=(5, 10), shops=0.7, tree_p=0.15, gardens=False)
    lots(211, 94, 268, 110, 117, FLATS, flat=True, d=(3, 5), h=(3, 6), w=(5, 10), shops=0.5, tree_p=0.15, gardens=False)
    lots(211, 115, 252, 123, 118, FLATS + PAL_RES, kinds=('flat', 'gable', 'hip'), d=(3, 4), h=(2, 4))
    lots(212, 127, 236, 147, 119, PAL_RES, d=(3, 4), h=(2, 3))
    lots(256, 58, 274, 74, 120, FLATS, flat=True, d=(3, 4), h=(3, 5), w=(5, 9), gardens=False)
    lots(196, 74, 204, 79, 121, FLATS, flat=True, d=(3, 3), h=(2, 2), w=(5, 8), gardens=False)
    # 北边坡上的大房子（露伴家一带）、别墅区
    lots(212, 33, 246, 52, 122, PAL_RES, d=(4, 4), h=(3, 3), w=(8, 11), gap=(3, 5), tree_p=0.9)
    lots(268, 34, 281, 50, 123, PAL_RES, d=(3, 3), h=(3, 3), w=(6, 8), gap=(2, 4), tree_p=0.9)
    S['garden_blocks'] = garden_blocks
    # 西边田里零星的农家（瓦顶）
    for x, y in ((16, 131), (40, 145), (60, 156), (18, 98), (64, 112), (8, 162)):
        if T.free(x, y, x + 7, y + 5):
            A(x, y, 7, 3, 2, ['#5c6170', '#6a5a4e', '#4e5a6e'][x % 3], '#e3d8c0', kind='kawara')
            trees.append((x - 2, y + 1, 'round', '#3f7444', True))
            trees.append((x + 9, y + 2, 'round', '#4f8a4a', False))
    S['T'] = T
    S['trees'] = trees
    S['blocked'] = blocked
    return T


# ================================================================== 树
def plant(S):
    T, trees = S['T'], S['trees']
    occ = T.occ.copy()
    occ |= S['allroad'] | S['water'] | S['bed'] | S['sea'] | S['pond'] | S['piers']
    cv = S['cv']

    def ok(x, y, big=False):
        r = 2 if big else 1
        x, y = int(x), int(y)
        if x - r < 0 or y - r < 0 or x + r >= W or y + r >= H:
            return False
        return not occ[y - r:y + r + 1, x - r:x + r + 1].any()

    out = []
    for x, y, k, c, big in trees:
        if ok(x, y, big):
            out.append((x, y, k, c, big))
            occ[int(y) - 1:int(y) + 2, int(x) - 1:int(x) + 2] = True
    # 行道树：大道两边、干道一边
    for name, side, step, c in (('avenue', (-4.0, 4.0), 5, '#5a9450'), ('main', (-3.5,), 6, '#5f9a52'),
                                ('national', (-4.0, 4.0), 7, '#5f9a52'), ('coast', (-3.5,), 6, '#3f6e48')):
        m, lvl, cc, w = S['roads'][name]
        fr = frames(cc)
        for off in side:
            last = -99
            for x, y, tx, ty, s in fr:
                if s - last < step:
                    continue
                nx, ny = -ty, tx
                px_, py_ = x + nx * off, y + ny * off
                if ok(px_, py_):
                    out.append((int(round(px_)), int(round(py_)), 'pine' if name == 'coast' else 'round', c, False))
                    occ[int(py_) - 1:int(py_) + 2, int(px_) - 1:int(px_) + 2] = True
                    last = s
    # 河堤上的一排樱树（绿）
    fr = frames(S['river'])
    last = -99
    for x, y, tx, ty, s in fr:
        if s - last < 4 or y < 52:
            continue
        for off in (-4.2, 4.2):
            px_, py_ = x - ty * off, y + tx * off
            if ok(px_, py_):
                out.append((int(round(px_)), int(round(py_)), 'round2', '#6aa65a', False))
                occ[int(py_) - 1:int(py_) + 2, int(px_) - 1:int(px_) + 2] = True
        last = s
    # 指定的树：操场边、公园、别墅区的松、虹村家的枯树、牧场防风林
    fixed = []
    for x in range(162, 192, 4):
        fixed.append((x, 72, 'round', '#d89ab0', False))               # 高中的樱花（序章四月）
    for y in range(63, 85, 4):
        fixed.append((125, y, 'round', '#5f9a52', False))
    for x, y in ((176, 121), (196, 123), (192, 130), (180, 130), (199, 127), (178, 118)):
        fixed.append((x, y, 'round', '#5a9a50', True))
    for x, y in ((276, 44), (279, 49), (298, 38), (296, 27), (300, 31), (286, 33), (270, 38), (268, 46), (289, 49)):
        fixed.append((x, y, 'pine', '#35603f', False))
    for x, y in ((59, 126), (81, 127), (58, 148), (80, 149), (63, 145)):
        fixed.append((x, y, 'dead', None, False))
    for x, y in ((48, 62), (48, 66), (48, 70), (49, 74), (66, 66), (75, 60)):
        fixed.append((x, y, 'round', '#3f7444', True))
    for x, y in ((107, 116), (107, 128), (120, 129)):
        fixed.append((x, y, 'round', '#4f8a4a', True))
    for x, y in ((218, 37), (239, 38), (240, 49), (217, 50)):
        fixed.append((x, y, 'round', '#4f8a4a', True))
    for x, y in ((66, 33), (82, 32), (67, 40), (81, 40)):
        fixed.append((x, y, 'round', '#3f6b45', True))
    for x, y, k, c, big in fixed:
        if ok(x, y, big) or k in ('dead', 'pine'):
            out.append((x, y, k, c, big))
            occ[int(y) - 1:int(y) + 2, int(x) - 1:int(x) + 2] = True
    # 影子先画，再从北往南画树
    sh = np.zeros((H, W), bool)
    for x, y, k, c, big in out:
        tree_shadow(sh, x, y, big)
    sh &= ~T.occ & ~S['sea']
    cv.darken(sh, (0.7, 0.74, 0.84))
    for x, y, k, c, big in sorted(out, key=lambda t: t[1]):
        if k == 'dead':
            cv.px(x, y, '#6a5a4a')
            cv.px(x - 1, y - 1, '#7a6a58')
            cv.px(x + 1, y - 1, '#5a4a3c')
            cv.px(x, y - 1, '#7a6a58')
            continue
        tree(cv, x, y, k, c, big)
    S['tree_occ'] = occ


# ================================================================== 小东西：火车、车、船、灯塔、吊车、铁塔、鸟居、天使岩、伞、牛
def objects(S):
    cv, sea = S['cv'], S['sea']
    fr = S['rail']
    # ---- 停在车站的电车（两节：奶白车身 + 绿色腰线）
    cars = [(f, i) for i, f in enumerate(fr) if 188 <= f[0] <= 214]
    if cars:
        s0 = cars[0][1][4] if False else cars[0][0][4]
        for x, y, tx, ty, s in (c[0] for c in cars):
            nx, ny = -ty, tx
            gapc = int(s - s0) % 13 == 12
            cv.px(x - nx * 1.1, y - ny * 1.1, '#f6f2e6' if not gapc else '#3a3a48')
            cv.px(x, y, '#e2dccb' if not gapc else '#3a3a48')
            cv.px(x + nx * 1.1, y + ny * 1.1, '#4f9a62' if not gapc else '#2a2a38')
        for x, y, tx, ty, s in (c[0] for c in cars[::9]):
            cv.px(x, y, '#9a968c')                                     # 车顶的空调
    # ---- 天桥（站房跨过铁路到北月台）
    for y in range(49, 58):
        cv.px(208, y, '#ece8de')
        cv.px(209, y, '#c9c3b6')
    cv.px(210, 56, '#8a8478')
    # ---- 车
    r = np.random.RandomState(404)
    cols = ['#d04a3c', '#3f6fb0', '#f4f2ec', '#2c2c34', '#e8c040', '#5aa060', '#f4f2ec', '#9a9aa6']
    for name, n in (('main', 7), ('avenue', 6), ('national', 7), ('coast', 6), ('res_y134', 2), ('east_y112', 2)):
        m, lvl, cc, w = S['roads'][name]
        f = frames(cc)
        picks = r.choice(len(f), size=min(n, len(f)), replace=False)
        for i in picks:
            x, y, tx, ty, s = f[i]
            lane = (1 if r.rand() < 0.5 else -1) * (1.0 if w >= 4 else 0)
            x, y = x - ty * lane, y + tx * lane
            xi, yi = int(round(x)), int(round(y))
            if not (0 <= xi < W - 2 and 0 <= yi < H - 2) or S['bridge'][yi, xi]:
                continue
            c = cols[r.randint(len(cols))]
            if abs(tx) >= abs(ty):
                if m[yi, xi] and m[yi, xi + 1]:
                    cv.px(xi, yi, c)
                    cv.px(xi + 1, yi, shade(c, -0.25))
                    cv.px(xi, yi + 1, mixc(cv_get(cv, xi, yi + 1), '#3a3550', 0.35)) if not m[yi + 1, xi] else None
            else:
                if m[yi, xi] and m[yi + 1, xi]:
                    cv.px(xi, yi, shade(c, 0.15))
                    cv.px(xi, yi + 1, shade(c, -0.2))
    # 东方家门口的警车（爷爷是警察）、超市停车场里的车
    cv.px(117, 129, '#f4f2ec')
    cv.px(118, 129, '#2c2c34')
    for x, y, c in ((88, 120, '#d04a3c'), (94, 120, '#f4f2ec'), (97, 128, '#3f6fb0'), (91, 128, '#e8c040'), (100, 120, '#2c2c34')):
        cv.px(x, y, c)
        cv.px(x, y + 1, shade(c, -0.25))
    # 站前的公交、出租
    cv.rect(193, 64, 196, 65, '#4f9a62')
    cv.hline(193, 196, 64, '#f2f0ea')
    for x, y in ((209, 64), (212, 64), (209, 69)):
        cv.px(x, y, '#e8c040')
        cv.px(x + 1, y, '#c8a030')

    # ---- 船：码头边的渔船、海上的渔船（带尾迹）、SPW 的船
    def boat(x, y, c='#f4f2ec', stripe='#3f6fb0', L=4, wake=0, cabin=True):
        cv.darken(rmask(x + 1, y + 1, x + L, y + 2) & sea, (0.62, 0.68, 0.82))
        cv.rect(x, y, x + L - 1, y + 1, c)
        cv.hline(x, x + L - 1, y + 1, stripe)
        cv.px(x + L - 1, y, shade(c, -0.2))
        if cabin:
            cv.px(x + 1, y, '#8a9ab0')
        for k in range(wake):
            if 0 <= x - 1 - k < W:
                cv.px(x - 1 - k, y + (k % 2), '#e9f7fc' if k < 3 else '#b4e2f3')

    for x, y in ((279, 82), (285, 82), (279, 94), (285, 94), (276, 103), (282, 103)):
        boat(x, y, stripe=['#3f6fb0', '#c8403a', '#3f8f4a'][x % 3])
    for x, y, w_ in ((242, 142, 4), (300, 118, 5), (236, 160, 3), (305, 70, 4), (262, 152, 5)):
        boat(x, y, wake=w_)
    # SPW 的船（白船、深蓝船底、红烟囱）靠在主栈桥头
    sx, sy = 298, 87
    cv.darken(rmask(sx + 1, sy + 1, sx + 13, sy + 5) & sea, (0.6, 0.66, 0.8))
    cv.rect(sx, sy, sx + 11, sy + 4, '#f6f6f2')
    cv.hline(sx, sx + 11, sy + 4, '#2f3f6a')
    cv.px(sx + 12, sy + 2, '#f6f6f2')
    cv.px(sx + 12, sy + 3, '#2f3f6a')
    cv.rect(sx + 3, sy + 1, sx + 7, sy + 2, '#dfe3ea')
    cv.hline(sx + 3, sx + 7, sy + 2, '#6a7a96')
    cv.px(sx + 6, sy, '#c8403a')
    cv.px(sx + 6, sy - 1, '#c8403a')
    cv.hline(sx, sx + 11, sy, '#ffffff')

    # ---- 集装箱、吊车
    r2 = np.random.RandomState(9)
    ccols = ['#c0483c', '#3f6fa8', '#4f8a5a', '#d6893f', '#8a5a9a', '#c8b04a']
    for yy in (88, 90):
        for xx in range(281, 293, 2):
            c = ccols[r2.randint(len(ccols))]
            cv.px(xx, yy, shade(c, 0.12))
            cv.px(xx + 1, yy, shade(c, -0.15))
    cv.vline(294, 85, 91, '#c8702a')
    cv.vline(297, 85, 91, '#c8702a')
    cv.hline(292, 300, 85, '#e0903a')
    cv.hline(292, 300, 84, '#f0b060')
    cv.darken(rmask(295, 92, 298, 93) & ~S['piers'], (0.62, 0.68, 0.82))

    # ---- 灯塔：海岬（白身红顶）、防波堤头（红 / 白）
    def lighthouse(x, y, body='#f6f4ee', top='#c8403a', h=6):
        cv.darken(lmask([(x + 1, y + 1), (x + h, y + 1 + h // 3)], 1) & ~S['T'].occ, (0.7, 0.74, 0.84))
        cv.rect(x - 1, y - h + 1, x, y, body)
        cv.vline(x, y - h + 1, y, shade(body, -0.18))
        cv.rect(x - 1, y - h - 1, x, y - h, top)
        cv.px(x - 1, y - h + 1, '#ffe8a0')
        cv.px(x - 1, y - h - 2, shade(top, -0.2))

    lighthouse(302, 40, h=6)
    lighthouse(301, 76, body='#d8403a', top='#f4f2ec', h=4)
    lighthouse(297, 105, h=4, top='#3a3a48')
    # 海岬灯塔的光（白天只是一点暖光）
    cv.px(300, 33, '#fff4c8')

    # ---- 送电铁塔 (46,44) + 电线
    tx, ty = 46, 44
    TWR = ['...X...', '..XXX..', '.XXXXX.', '..X.X..', 'XXXXXXX', '..X.X..', '..XXX..', '.X...X.', '.XXXXX.', '.X...X.', 'X.....X', 'X.....X']
    sh = lmask([(tx + 1, ty), (tx + 9, ty - 4)], 1) | lmask([(tx + 3, ty), (tx + 10, ty - 3)], 1)
    cv.darken(sh & ~S['allroad'], (0.7, 0.74, 0.84))
    for i, row in enumerate(TWR):
        for j, ch in enumerate(row):
            if ch == 'X':
                cv.px(tx - 3 + j, ty - len(TWR) + 1 + i, '#c4c4d2' if j <= 2 else '#5c5c6c')
    for (x0, y0), (x1, y1) in (((43, 37), (5, 31)), ((49, 37), (60, 5))):
        n = int(max(abs(x1 - x0), abs(y1 - y0)))
        for k in range(n + 1):
            t = k / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t + math.sin(t * math.pi) * 2.0
            if k % 2 == 0:
                cv.px(x, y, '#4a4656')
    for x, y in ():                                                    # （远处的小铁塔不画了）
        cv.vline(x, y, y + 5, '#5c5c6c')
        cv.hline(x - 1, x + 1, y + 1, '#8a8a9a')
        cv.px(x - 1, y + 5, '#5c5c6c')
        cv.px(x + 1, y + 5, '#5c5c6c')

    # ---- 鸟居（神社前）
    cv.hline(71, 77, 41, '#e0503a')
    cv.hline(72, 76, 42, '#b83a2a')
    cv.vline(72, 42, 44, '#c8402c')
    cv.vline(76, 42, 44, '#a8301e')
    cv.hline(70, 78, 40, '#3a3236')

    # ---- 天使岩 (238,117)
    ROCK = ['.aab.', 'aabbc', 'abbcc', '.ccd.']
    pal = {'a': '#d8d4cc', 'b': '#a8a49c', 'c': '#7e7a76', 'd': '#5a5660'}
    cv.darken(rmask(239, 115, 241, 118), (0.75, 0.78, 0.88))
    for i, row in enumerate(ROCK):
        for j, ch in enumerate(row):
            if ch in pal:
                cv.px(236 + j, 114 + i, pal[ch])
    cv.px(238, 115, '#4a4650')                                          # 石头上那张脸

    # ---- 海水浴场的伞
    for x, y, c in ((282, 60, '#e0503a'), (280, 66, '#3f6fb0'), (283, 70, '#e8c040'), (279, 74, '#e0503a'), (281, 56, '#4f9a62')):
        if S['beach'][y, x]:
            cv.px(x + 1, y + 1, '#c8b47e')
            cv.px(x, y, c)
            cv.px(x - 1, y, shade(c, 0.3))
            cv.px(x, y - 1, shade(c, 0.2))
    # ---- 牛、筒仓
    for x, y in ((76, 62), (83, 66), (89, 60), (86, 73), (78, 76), (91, 69)):
        cv.px(x, y, '#f6f4ee')
        cv.px(x + 1, y, '#2c2c34' if (x + y) % 2 else '#f6f4ee')
        cv.px(x + 1, y + 1, '#8aa86a')
    sxo, syo = 64, 62
    cv.rect(sxo, syo + 1, sxo + 2, syo + 5, '#c8c4bc')
    cv.vline(sxo, syo + 1, syo + 5, '#e6e2da')
    cv.vline(sxo + 2, syo + 1, syo + 5, '#9a968e')
    cv.hline(sxo, sxo + 2, syo, '#8a5a4a')
    cv.px(sxo + 1, syo - 1, '#a86a58')
    cv.darken(rmask(sxo + 3, syo + 3, sxo + 4, syo + 6), (0.72, 0.76, 0.86))


def gardens(S):
    """住宅街区里房子之间空着的地：铺点绿（小院子），偶尔一格花"""
    cv, T = S['cv'], S['T']
    houses = np.zeros((H, W), bool)
    for it in T.items:
        houses[it['y']:it['y'] + it['d'] + it['h'], it['x']:it['x'] + it['w']] = True
    near = ndi.binary_dilation(houses, iterations=2) & ~houses
    r = np.random.RandomState(55)
    for x0, y0, x1, y1 in S.get('garden_blocks', []):
        blk = rmask(x0 - 1, y0 - 1, x1 + 1, y1 + 1) & ~S['allroad'] & ~S['water'] & ~S['bank'] & S['town']
        free = blk & ~houses
        g = fbm(81, 2, 2)
        cv.dith(free & near, '#b4c98c', np.clip(g * 1.2 - 0.2, 0, 1) * 0.8)
        cv.dith(free & ~near, '#c2cf98', 0.25)
        ys, xs = np.where(free & near)
        for k in r.choice(len(ys), size=min(len(ys), (x1 - x0) * (y1 - y0) // 60), replace=False) if len(ys) else []:
            cv.px(xs[k], ys[k], ['#e8a0b8', '#f4e070', '#ffffff', '#e86a50'][r.randint(4)])


def cv_get(cv, x, y):
    if 0 <= x < W and 0 <= y < H:
        return '#%02x%02x%02x' % tuple(int(v) for v in cv.a[y, x])
    return '#000000'


# ================================================================== 图框、地名牌、指北针、比例尺、旧纸
def finish(S):
    cv = S['cv']
    ink, paper = '#4e3e2c', '#f1e6c8'
    # 指北针（东南海面）
    cx, cy = 300, 161
    ring = (np.hypot(XX - cx, YY - cy) <= 8.6) & (np.hypot(XX - cx, YY - cy) >= 7.6)
    cv.darken(shift(ring, 1, 1) & ~ring, (0.62, 0.68, 0.82))
    cv.fill(ring, '#f4ead2')
    for ang, L, c1, c2 in ((90, 9, '#d8483c', '#8a2a26'), (270, 7, '#f4ead2', '#a89a7a'), (0, 7, '#f4ead2', '#a89a7a'),
                           (180, 7, '#f4ead2', '#a89a7a')):
        a = math.radians(ang)
        tipx, tipy = cx + math.cos(a) * L, cy - math.sin(a) * L
        px_, py_ = -math.sin(a), -math.cos(a)
        left = pmask([(cx, cy), (tipx, tipy), (cx + px_ * 2.2 + math.cos(a) * 1.5, cy + py_ * 2.2 - math.sin(a) * 1.5)])
        right = pmask([(cx, cy), (tipx, tipy), (cx - px_ * 2.2 + math.cos(a) * 1.5, cy - py_ * 2.2 - math.sin(a) * 1.5)])
        cv.fill(left, c1)
        cv.fill(right, c2)
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        for k in range(2, 6):
            cv.px(cx + math.cos(a) * k, cy - math.sin(a) * k, '#e8dcc0' if k < 5 else '#b8a888')
    cv.px(cx, cy, '#4e3e2c')
    NG = ['X..X', 'XX.X', 'X.XX', 'X..X', 'X..X']
    for i, row in enumerate(NG):
        for j, ch in enumerate(row):
            if ch == 'X':
                cv.px(cx - 2 + j, cy - 16 + i, '#f8f0dc')
                cv.px(cx - 1 + j, cy - 15 + i, '#2a3a5a') if False else None
    # 地名牌（右上角，挂在图框上）
    x0, y0, x1, y1 = PLACE
    cv.darken(rmask(x0 + 1, y1 + 1, x1 + 1, y1 + 1) | rmask(x1 + 1, y0 + 1, x1 + 1, y1 + 1), (0.7, 0.72, 0.84))
    cv.rect(x0, y0, x1, y1, '#f6eed8')
    cv.rect(x0, y1, x1, y1, ink)
    cv.vline(x0, y0, y1, ink)
    cv.vline(x1, y0, y1, ink)
    cv.hline(x0 + 2, x1 - 2, y1 - 2, '#d8c8a0')
    # 比例尺（左下，田上压一块小纸片）
    bx, by = 10, 170
    cv.rect(bx - 2, by - 3, bx + 33, by + 2, '#f6eed8')
    cv.fill(outer_edge(rmask(bx - 2, by - 3, bx + 33, by + 2)), '#8a7a5a')
    for k in range(4):
        cv.rect(bx + k * 8, by - 1, bx + k * 8 + 7, by, ink if k % 2 == 0 else '#f6eed8')
    cv.rect(bx, by - 1, bx + 31, by - 1, ink)
    for k in range(5):
        cv.vline(bx + k * 8 - (1 if k == 4 else 0), by - 2, by, ink)
    # 图框：外线、纸边、黑白相间的经纬格带、内线
    cv.rect(0, 0, W - 1, 4, paper)
    cv.rect(0, H - 5, W - 1, H - 1, paper)
    cv.rect(0, 0, 4, H - 1, paper)
    cv.rect(W - 5, 0, W - 1, H - 1, paper)
    for x in range(5, W - 5):
        if (x // 10) % 2 == 0:
            cv.px(x, 2, ink)
            cv.px(x, H - 3, ink)
    for y in range(5, H - 5):
        if (y // 10) % 2 == 0:
            cv.px(2, y, ink)
            cv.px(W - 3, y, ink)
    for v in (0, ):
        cv.hline(0, W - 1, v, ink)
        cv.hline(0, W - 1, H - 1 - v, ink)
        cv.vline(v, 0, H - 1, ink)
        cv.vline(W - 1 - v, 0, H - 1, ink)
    cv.hline(4, W - 5, 4, ink)
    cv.hline(4, W - 5, H - 5, ink)
    cv.vline(4, 4, H - 5, ink)
    cv.vline(W - 5, 4, H - 5, ink)
    for x, y in ((1, 1), (W - 4, 1), (1, H - 4), (W - 4, H - 4)):     # 四个角的小方块
        cv.rect(x, y, x + 2, y + 2, ink)
        cv.px(x + 1, y + 1, '#c8a050')
    # 地名牌压在图框上：重画一遍上边那段
    cv.rect(x0 + 1, 4, x1 - 1, y1 - 1, '#f6eed8')
    cv.hline(x0 + 2, x1 - 2, y1 - 2, '#d8c8a0')
    # 旧纸：四周压暗一点（只动画面，不动图框）
    a = cv.a.astype(float)
    v = ((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2
    k = np.clip((v - 0.9) * 0.08, 0, 0.07)
    inner = rmask(5, 5, W - 6, H - 6)
    a[inner] *= (1 - k[inner][:, None] * np.array([1, 1.1, 1.4]))
    cv.a = np.clip(a, 0, 255).astype(np.uint8)


# ================================================================== 存盘 + 元数据
ANCHORS = {k: list(v) for k, v in {
    'school': PINS['school'], 'gate': PINS['school'], 'home': PINS['home'], 'station': PINS['station'], 'sea': PINS['harbor'],
    'market': PINS['market'], 'rock': PINS['rock'], 'nijimura': PINS['nijimura'], 'hirose_home': PINS['hirose_home'],
    'villa': PINS['villa'], 'rohan_house': PINS['rohan_house'], 'farm': PINS['farm'],
    'ch7_salon': PINS['salon'], 'ch7_tailor': PINS['tailor'],
    'c11_kawajiri': PINS['kawajiri'], 'c11_rohan': PINS['rohan_house'], 'c11_alley': PINS['alley'], 'fin_home': PINS['fin_home'],
}.items()}


def render():
    S = base()
    S['railc'] = spline(RAIL, 0.5)
    S['pond'] = emask(186, 125, 5.5, 3.2)
    ground(S)
    town(S)
    gardens(S)
    draw_town(S['cv'], S['T'], S['land'] & ~S['water'])
    plant(S)
    objects(S)
    finish(S)
    return S


def save(S):
    im = S['cv'].img()
    fp = os.path.join(ASSETS, 'bg', 'morioh_map', 'map.png')
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    im.save(fp)
    path = os.path.join(META, 'bg.json')
    with open(path, encoding='utf-8') as fh:
        d = json.load(fh)
    e = d['morioh_map']
    e.setdefault('anchors', {}).update(ANCHORS)
    e['layers'] = [{'type': 'static', 'image': 'bg/morioh_map/map'}, {'type': 'stars', 'k': 0, 'list': glints(S)}]
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    return im


def glints(S):
    """海面、河面上一闪一闪的反光（背景图层 stars：[x, y, 速度, 相位, 大, 颜色]），躲开红章、指北针、船"""
    r = np.random.RandomState(2024)
    sea, dsea, water = S['sea'], S['dsea'], S['water']
    out, taken = [], np.zeros((H, W), bool)
    tries = 0
    while len(out) < 44 and tries < 5000:
        tries += 1
        x, y = r.randint(200, W - 6), r.randint(6, H - 6)
        if not sea[y, x] or dsea[y, x] < 3 or taken[y, x]:
            continue
        if STAMP[0] - 4 <= x <= STAMP[2] + 4 and STAMP[1] - 4 <= y <= STAMP[3] + 4:
            continue
        if math.hypot(x - 300, y - 161) < 13 or (PLACE[0] - 2 <= x <= PLACE[2] + 2 and y <= PLACE[3] + 2):
            continue
        if not (S['cv'].a[y, x].astype(int).sum() < 600):          # 已经是白浪 / 船的地方不放
            continue
        big = dsea[y, x] > 14 and r.rand() < 0.3
        col = '#ffffff' if dsea[y, x] < 12 or big else '#d6f0ff'
        out.append([int(x), int(y), round(1.6 + r.rand() * 2.4, 2), round(r.rand() * 6.28, 2), bool(big), col])
        taken[max(0, y - 3):y + 4, max(0, x - 3):x + 4] = True
    ys, xs = np.where(water & ~sea)
    for k in r.choice(len(ys), size=8, replace=False):
        out.append([int(xs[k]), int(ys[k]), round(2.5 + r.rand() * 2, 2), round(r.rand() * 6.28, 2), False, '#f0fbff'])
    return out


def preview(S, out_dir, name='map'):
    os.makedirs(out_dir, exist_ok=True)
    im = S['cv'].img()
    im.resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(out_dir, name + '_x4.png'))
    # 图钉核对：每个图钉位置画个小十字
    k = 4
    big = im.resize((W * k, H * k), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for key, (x, y) in PINS.items():
        cx, cy = x * k + k // 2, y * k + k // 2
        d.line((cx - 6, cy, cx + 6, cy), fill=(255, 0, 255, 255), width=1)
        d.line((cx, cy - 6, cx, cy + 6), fill=(255, 0, 255, 255), width=1)
        d.text((cx + 4, cy - 12), key, fill=(255, 0, 255, 255))
    big.save(os.path.join(out_dir, name + '_pins_x4.png'))


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_map_preview')
    S = render()
    preview(S, out)
    if '--save' in sys.argv:
        save(S)
        print('已写 assets/bg/morioh_map/map.png 和 _meta/bg.json 的锚点')
    print('ok')
