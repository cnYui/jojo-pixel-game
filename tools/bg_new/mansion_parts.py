# -*- coding: utf-8 -*-
r"""mansion_parts —— 第11章 / 终章「DIO 的馆」六张背景共用的零件、调色和打光（本身不是背景 key，不导出）。

用到它的六张：mansion_exterior、mansion_corridor、illusion_corridor、mansion_hall、mansion_tower、mansion_stairs。
同一座馆，墙纸、护墙板、石墙、烛台、肖像框、门、封死的窗、丝绒帘、地毯、蜡烛火苗、蝙蝠、乌鸦都从这里取，六张的风格才统一。
小工具（dk / lt / hl / vl / px / rect / mul_box / cast_shadow / mottle / haze / opaque）跟第4章 varanasi_street.py 共用
（同 ganges_ghat.py 的引用写法：importlib 按路径加载、模块名 bg_new_varanasi_street，不改 sys.path 的顺序）。

做法（照 singapore_hotel.py 的“albedo × 光照”，室内的压迫感主要靠它）：
  1. Canvas 上先画“满光”时的固有色（albedo：物件自己的亮面 / 暗面 / 1 px 墨线都画好）；会发光的东西（火苗位置的芯、
     窗缝漏进来的一线光、窗外的天、亮着的窗）同时记进 emissive 遮罩，打光时不压暗。
  2. Light 叠环境光 + 点光源（蜡烛 / 壁炉 / 吊灯）+ 光带（窗缝的一线光、阳光柱）；总亮度分档 + Bayer 抖一点 → 像素风的一圈圈
     光（可走带那几行分得更细，免得人脚下出现一道道光圈）；每个光源带自己的色调（烛光暖、月光冷、环境光偏紫）。
  3. apply() 出最终底图；火苗本身在 strip 里画（8 帧闪），底图只留烛台、烛芯和光晕。
不用 glow 图层的原因：bg_jojo.ref_render（预览 / 自检的 Python 版公式）不认识 glow；烘进底图后 JS 和 Python 拼出来逐像素一样。
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
from scipy import ndimage  # noqa: E402

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402
from engine import bg_egypt as E  # noqa: E402


def _street_mod():
    """小工具跟 varanasi_street.py 共用（同一个模块名，bg_jojo.bg_new('varanasi_street') 会直接复用）。"""
    key = 'bg_new_varanasi_street'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'varanasi_street.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


V = _street_mod()
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, cast_shadow, mottle, haze, opaque = (V.mul_box, V.mul_mask, V.poly_mask, V.cast_shadow,
                                                                  V.mottle, V.haze, V.opaque)
arch_rows = V.arch_mask_rows
C = A._c4
W, H = 320, 180
N8 = 8                          # 所有 strip：8 帧
FPS_FIRE = 8.0                  # 火苗 8 帧 @8 fps = 1 s 一圈
FPS_SLOW = 4.0                  # 其他 8 帧 @4 fps = 2 s 一圈

# ============================================================ 调色（六张共用）
INK = (20, 12, 24)              # 墨线（偏紫的黑，和馆的阴气一致）
STONE = dict(hi=(132, 124, 140), lt=(108, 100, 118), md=(88, 82, 100), dk=(66, 60, 78), dd=(42, 38, 52))
BLACK = dict(hi=(98, 92, 108), lt=(74, 70, 86), md=(56, 52, 68), dk=(40, 36, 50), dd=(24, 20, 32))   # 外墙的黑石
WOOD = dict(hi=(136, 90, 60), lt=(110, 70, 46), md=(86, 52, 34), dk=(62, 36, 24), dd=(38, 22, 16))
GOLD = dict(hi=(250, 222, 140), lt=(214, 172, 88), md=(170, 126, 54), dk=(116, 80, 32), dd=(70, 46, 20))
VELVET = dict(hi=(168, 46, 60), lt=(134, 30, 46), md=(104, 20, 38), dk=(76, 12, 30), dd=(46, 6, 20))
BLACKCLOTH = dict(hi=(70, 62, 78), lt=(52, 46, 60), md=(38, 34, 46), dk=(26, 22, 32), dd=(14, 12, 18))
PAPER = dict(base=(112, 30, 44), dk=(90, 20, 36), lt=(136, 46, 56), gold=(168, 114, 62))     # 暗红锦缎墙纸
MARBLE = dict(hi=(226, 220, 224), lt=(204, 198, 206), md=(176, 170, 182), dk=(138, 132, 148), vein=(108, 100, 120))
CARPET = dict(base=(140, 28, 40), lt=(164, 44, 52), dk=(98, 16, 32), dd=(66, 10, 24), gold=(184, 138, 62),
              gold_d=(128, 90, 42))
IRON = dict(hi=(100, 98, 112), md=(56, 54, 66), dk=(34, 32, 42), dd=(18, 16, 24))
WAX = dict(hi=(246, 240, 222), md=(226, 214, 186), dk=(186, 168, 138))
FLAME = ((255, 252, 226), (255, 224, 128), (250, 164, 60), (214, 96, 38))
SKIN = dict(hi=(240, 214, 190), md=(214, 176, 150), dk=(160, 120, 104))

# 光源色调（乘在 albedo 上；>1 的分量 = 被这种光提亮的颜色）
T_AMB = (0.70, 0.72, 1.16)      # 馆里的环境光：偏紫蓝、很暗
T_WARM = (1.34, 1.00, 0.62)     # 烛光
T_FIRE = (1.40, 0.92, 0.52)     # 壁炉
T_DAY = (1.22, 1.12, 0.92)      # 窗缝漏进来的白天（暖白）
T_SUN = (1.30, 1.10, 0.80)      # 阳光柱 / 夕阳
T_MOON = (0.74, 0.90, 1.38)     # 月光
T_DUSK = (1.36, 0.92, 0.70)     # 夕阳从窗里照进来


# ============================================================ 画布 + 打光
class Canvas:
    """albedo（RGBA，满光时的固有色）+ emissive（L，>0 = 自己发光，打光时不压暗）。"""

    def __init__(self, w, h, col=None):
        self.w, self.h = int(w), int(h)
        self.im = A._new(self.w, self.h, col)
        self.em = Image.new('L', (self.w, self.h), 0)

    @property
    def d(self):
        return ImageDraw.Draw(self.im)

    @property
    def e(self):
        return ImageDraw.Draw(self.em)

    def glow_px(self, x, y, c):
        """画一个发光的像素（同时记进 emissive）。"""
        px(self.d, x, y, c)
        self.e.point((x, y), fill=255)

    def glow_rect(self, x0, y0, x1, y1, c):
        rect(self.d, x0, y0, x1, y1, c)
        if x1 >= x0 and y1 >= y0:
            self.e.rectangle((x0, y0, x1, y1), fill=255)

    def paste_emissive(self, lay, x=0, y=0):
        """贴一张图，它不透明的像素都算发光的（窗外的天、亮窗）。"""
        paste(self.im, lay, x, y)
        a = np.array(lay)[..., 3] > 0
        m = Image.fromarray((a * 255).astype(np.uint8), 'L')
        self.em.paste(m, (int(x), int(y)), m)

    def arr(self):
        return np.array(self.im).astype(np.float32)

    def emis(self):
        return np.array(self.em) > 0


class Light:
    """环境光 + 点光源 + 光带 → 每个像素的乘数（H×W×3），分档 + Bayer 抖动。"""

    def __init__(self, w, h, amb=0.30, tint=T_AMB):
        self.w, self.h = int(w), int(h)
        self.yy, self.xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        self.base = np.full((self.h, self.w), float(amb), np.float32)
        self.base_t = np.array(tint, np.float32)
        self.terms = []

    def amb_add(self, arr):
        self.base = self.base + np.asarray(arr, np.float32)

    def point(self, x, y, r, k, tint=T_WARM, sy=1.0, power=1.6, clip=None):
        """点光源：k·(1 − d/r)^power；sy > 1 = 竖向压扁（贴着墙往两边铺开的烛光）。clip = 只照 (x0, y0, x1, y1) 里。"""
        d = np.hypot(self.xx - x, (self.yy - y) * sy)
        I = k * np.clip(1 - d / r, 0, 1) ** power
        if clip is not None:
            x0, y0, x1, y1 = clip
            m = np.zeros_like(I)
            m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = 1
            I = I * m
        self.terms.append((I.astype(np.float32), np.array(tint, np.float32)))
        return I

    def poly(self, pts, k, tint=T_DAY, soft=1.2, fade=None):
        """多边形光带（窗缝漏进来的光、阳光柱）：边缘高斯软一点；fade(yy, xx) 给出沿光走的衰减。"""
        m = poly_mask((self.w, self.h), pts).astype(np.float32)
        if soft:
            m = ndimage.gaussian_filter(m, soft)
        if fade is not None:
            m = m * fade(self.yy, self.xx)
        self.terms.append(((k * m).astype(np.float32), np.array(tint, np.float32)))
        return m

    def add(self, I, tint):
        self.terms.append((np.asarray(I, np.float32), np.array(tint, np.float32)))

    def total(self):
        return self.base + sum((I for I, _ in self.terms), np.zeros_like(self.base))

    def field(self, levels=14, fine=None, fine_levels=26, jitter=0.32):
        """乘数场。fine（H×W bool）里的像素分得更细（可走带 / 地面：免得人脚下一道道光圈）。"""
        tot = self.total()
        num = self.base[..., None] * self.base_t
        for I, t in self.terms:
            num = num + I[..., None] * t
        tint = num / np.maximum(tot, 1e-6)[..., None]
        bay = A._bayer(self.w, self.h)
        q = np.floor(tot * levels + 0.5 + (bay - 0.5) * jitter) / levels
        if fine is not None:
            qf = np.floor(tot * fine_levels + 0.5 + (bay - 0.5) * jitter * 0.6) / fine_levels
            q = np.where(fine, qf, q)
        return q[..., None] * tint


def apply(cv, field, floor=5.0):
    """albedo × 光照（发光的像素保留原色）→ 不透明 RGBA。cv.im 透明的地方结果也透明。"""
    a = cv.arr()
    rgb = a[..., :3]
    em = cv.emis()
    out = np.where(em[..., None], rgb, np.clip(rgb * field, 0, 255))
    out = np.maximum(out, floor)
    alpha = np.where(a[..., 3] > 0, 255, 0).astype(np.float32)
    return Image.fromarray(np.concatenate([out, alpha[..., None]], -1).round().astype(np.uint8), 'RGBA')


def lum(a):
    a = np.asarray(a, np.float32)
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


# ============================================================ 墙：锦缎墙纸 / 护墙板 / 线脚 / 石墙
FLEUR = ('...l...',
         '..lgl..',
         '...l...',
         '.l.l.l.',
         'lllglll',
         '.l.l.l.',
         '..lll..',
         '...l...')
ROSETTE = ('.l.',
           'lgl',
           '.l.')


def wallpaper(cv, box, seed=0, pal=PAPER, tile=16, ox=0, oy=0, motif=FLEUR, age=True, swap=False):
    """暗红锦缎墙纸：45° 的细菱格（暗线）+ 每个菱形中间一朵小百合纹（亮）+ 菱格交点一粒四瓣小花（金点）。
    低对比，远看是质感；age = 上沿烟熏发暗 + 很淡的斑驳。swap = 把百合纹和小花对调（幻觉走廊的假墙：纹样差一点点）。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    a = np.array(cv.im)
    hh, ww = y1 - y0 + 1, x1 - x0 + 1
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    u = (xs - ox) % tile
    v = (ys - oy) % tile
    half = tile // 2
    col = np.empty((hh, ww, 3), np.float32)
    col[:] = pal['base']
    ring = (np.abs(u - half) + np.abs(v - half)) == half
    col[ring] = pal['dk']
    big, small = (motif, ROSETTE) if not swap else (ROSETTE, motif)
    for (cx, cy, stamp) in ((half, half, big), (0, 0, small)):
        sh_, sw_ = len(stamp), len(stamp[0])
        for j, row in enumerate(stamp):
            for i, ch in enumerate(row):
                if ch == '.':
                    continue
                m = (u == (cx + i - sw_ // 2) % tile) & (v == (cy + j - sh_ // 2) % tile)
                col[m] = pal['gold'] if ch == 'g' else pal['lt']
    if age:
        nz = A._fbm(ww + 8, hh + 8, 14, seed=seed % 997)[4:4 + hh, 4:4 + ww]
        col *= (1 + 0.07 * (nz - 0.5))[..., None]
        top = np.clip(1 - (ys - y0) / 26.0, 0, 1)                     # 上沿烟熏
        col *= (1 - 0.16 * top)[..., None]
    a[y0:y1 + 1, x0:x1 + 1, :3] = np.clip(col, 0, 255).astype(np.uint8)
    a[y0:y1 + 1, x0:x1 + 1, 3] = 255
    cv.im.paste(Image.fromarray(a, 'RGBA'))


def soot(cv, x, y0, y1, w=5, k=0.72, seed=0):
    """烛台上方墙上一道熏黑的烟痕（往上散开、越往上越淡）。"""
    a = np.array(cv.im).astype(np.float32)
    for y in range(y0, y1 + 1):
        u = (y1 - y) / max(1, y1 - y0)                                 # 0 = 最下（烛火那）
        hw = w * (0.5 + 0.8 * u)
        for xx in range(int(x - hw - 1), int(x + hw + 2)):
            if not 0 <= xx < cv.w:
                continue
            e = 1 - abs(xx - x) / max(1.0, hw)
            if e <= 0:
                continue
            amt = (1 - k) * e * (1 - 0.8 * u)
            if hash01(seed, xx, y) < 0.85:
                a[y, xx, :3] *= (1 - amt)
    cv.im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def peel(cv, x, y, w, h, seed, under=(150, 130, 112)):
    """墙纸剥落一块：露出底下发黄的灰泥，卷起来的纸边（亮一道）+ 下沿一道暗。"""
    d = cv.d
    for r in range(h):
        uu = r / max(1, h - 1)
        s = math.sin(math.pi * uu)
        a_ = x + int(round((1 - s) * w * 0.35 + hrange(-1, 1, seed, r, 1)))
        b_ = x + w - 1 - int(round((1 - s) * w * 0.3 + hrange(-1, 1, seed, r, 2)))
        for xx in range(a_, b_ + 1):
            c = under if hash01(seed, xx, r, 3) > 0.18 else dk(under, 0.86)
            px(d, xx, y + r, c)
        if 0 < r < h - 1:
            px(d, a_ - 1, y + r, lt(PAPER['lt'], 0.12))               # 卷起来的纸边
            px(d, b_ + 1, y + r, PAPER['dk'])
    hl(d, x + int(w * 0.3), x + int(w * 0.7), y + h, dk(PAPER['dk'], 0.8))


def dado_rail(cv, x0, x1, y, pal=WOOD):
    """腰线：亮 / 中 / 小珠线 / 暗 四行（y..y+3）。"""
    d = cv.d
    hl(d, x0, x1, y, pal['hi'])
    hl(d, x0, x1, y + 1, pal['lt'])
    for x in range(x0, x1 + 1):
        px(d, x, y + 2, pal['md'] if x % 3 else pal['hi'])             # 珠线
    hl(d, x0, x1, y + 3, pal['dd'])


def wainscot(cv, x0, x1, y0, y1, pal=WOOD, panel=28, gap=5, seed=0, off=0):
    """护墙板（y0..y1，含）：一格格凸板 —— 外框 md、1 px 暗槽、斜面左上亮右下暗、板心带两三道木纹。
    off 让板缝错开（几张图的护墙板不完全一样）。"""
    d = cv.d
    rect(d, x0, y0, x1, y1, pal['md'])
    py0, py1 = y0 + 3, y1 - 3
    step = panel + gap
    for k, pxs in enumerate(range(x0 + gap - (off % step), x1, step)):
        a_, b_ = pxs, pxs + panel - 1
        if b_ < x0 or a_ > x1:
            continue
        aa, bb = max(a_, x0), min(b_, x1)
        # 槽
        hl(d, aa, bb, py0, pal['dd'])
        hl(d, aa, bb, py1, pal['hi'])
        if a_ >= x0:
            vl(d, a_, py0, py1, pal['dd'])
        if b_ <= x1:
            vl(d, b_, py0, py1, pal['lt'])
        # 斜面
        hl(d, max(aa, a_ + 1), min(bb, b_ - 1), py0 + 1, pal['lt'])
        hl(d, max(aa, a_ + 1), min(bb, b_ - 1), py1 - 1, pal['dk'])
        if a_ + 1 >= x0:
            vl(d, a_ + 1, py0 + 1, py1 - 1, pal['lt'])
        if b_ - 1 <= x1:
            vl(d, b_ - 1, py0 + 1, py1 - 1, pal['dk'])
        # 板心（稍亮）+ 木纹
        rect(d, max(aa, a_ + 2), py0 + 2, min(bb, b_ - 2), py1 - 2, lt(pal['md'], 0.04))
        for g in range(3):
            gy = int(hrange(py0 + 3, py1 - 2, seed, k, g, 1))
            gx = int(hrange(a_ + 3, b_ - 8, seed, k, g, 2))
            L_ = int(hrange(4, 10, seed, k, g, 3))
            for xx in range(gx, gx + L_):
                if aa <= xx <= bb and a_ + 2 <= xx <= b_ - 2:
                    px(d, xx, gy, pal['dk'] if g % 2 else lt(pal['md'], 0.1))


def skirting(cv, x0, x1, y, h=5, pal=WOOD):
    """踢脚板：上沿一道亮珠线 + 板面 + 下沿一道最暗（贴地）。y..y+h−1。"""
    d = cv.d
    hl(d, x0, x1, y, pal['lt'])
    hl(d, x0, x1, y + 1, pal['dk'])
    rect(d, x0, y + 2, x1, y + h - 2, pal['md'])
    hl(d, x0, x1, y + h - 1, pal['dd'])


def cornice(cv, x0, x1, y, pal=WOOD, dentil=True):
    """檐口线脚（y..y+7）：顶一道亮、阶梯形线脚（亮暗交替）、一排齿饰、下沿一道影子落在墙上。"""
    d = cv.d
    rows = [pal['dd'], pal['hi'], pal['lt'], pal['dk'], pal['md'], pal['lt'], pal['dk'], pal['dd']]
    for i, c in enumerate(rows):
        hl(d, x0, x1, y + i, c)
    if dentil:
        for x in range(x0, x1 + 1, 4):
            vl(d, x, y + 4, y + 5, pal['dd'])
            px(d, x + 1, y + 4, pal['hi'])
    mul_box(cv.im, (x0, y + 8, x1, y + 9), (0.7, 0.7, 0.78))
    mul_box(cv.im, (x0, y + 10, x1, y + 10), (0.82, 0.82, 0.88), level=0.5)


def ashlar(cv, box, pal=STONE, bw=24, bh=10, seed=0, chips=True, rough=0.06):
    """方整石墙：一层层错缝的石块，每块颜色略有出入；上沿 / 左沿亮一道、下沿 / 右沿暗一道（光从左上）；灰缝最暗；
    缺角、细裂缝、斑驳。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    a = np.array(cv.im)
    hh, ww = y1 - y0 + 1, x1 - x0 + 1
    out = np.empty((hh, ww, 3), np.float32)
    out[:] = pal['md']
    nz = A._fbm(ww + 8, hh + 8, 6, seed=seed % 997)[4:4 + hh, 4:4 + ww]
    for row, yy in enumerate(range(0, hh, bh)):
        off = (row % 2) * (bw // 2) + int(hrange(-3, 3, seed, row, 1))
        xs = list(range(-off - bw, ww + bw, bw))
        for k, xa in enumerate(xs):
            xb = xa + bw
            f = hrange(0.9, 1.08, seed, row, k, 2)
            ya_, yb_ = yy, min(hh, yy + bh)
            xa_, xb_ = max(0, xa), min(ww, xb)
            if xa_ >= xb_:
                continue
            blk = np.array(pal['md'], np.float32) * f
            out[ya_:yb_, xa_:xb_] = blk
            out[ya_:yb_, xa_:xb_] *= (1 + rough * 2 * (nz[ya_:yb_, xa_:xb_] - 0.5))[..., None]
            if ya_ + 1 < yb_:
                out[ya_ + 1, xa_:xb_] = np.array(pal['lt'], np.float32) * f
            if yb_ - 1 > ya_:
                out[yb_ - 1, xa_:xb_] = np.array(pal['dk'], np.float32) * f
            if 0 <= xa + 1 < ww:
                out[ya_ + 1:yb_ - 1, xa + 1] = np.array(pal['lt'], np.float32) * f
            if 0 <= xb - 1 < ww:
                out[ya_ + 1:yb_ - 1, xb - 1] = np.array(pal['dk'], np.float32) * f
            if 0 <= xa < ww:
                out[ya_:yb_, xa] = pal['dd']
        out[yy, :] = pal['dd']
    if chips:
        for i in range(int(ww * hh / 260)):
            x = int(hrange(1, ww - 2, seed, i, 5))
            y = int(hrange(1, hh - 2, seed, i, 6))
            r = hash01(seed, i, 7)
            if r < 0.4:
                out[y, x] = pal['dk']
                if x + 1 < ww:
                    out[y, x + 1] = pal['dd']
            elif r < 0.6:                                              # 细裂缝
                yy2 = y
                for kk in range(int(hrange(3, 7, seed, i, 8))):
                    xx2 = x + kk
                    if xx2 < ww and 0 <= yy2 < hh:
                        out[yy2, xx2] = pal['dd']
                    yy2 += 1 if hash01(seed, i, kk, 9) < 0.5 else 0
            else:
                out[y, x] = pal['lt']
    a[y0:y1 + 1, x0:x1 + 1, :3] = np.clip(out, 0, 255).astype(np.uint8)
    a[y0:y1 + 1, x0:x1 + 1, 3] = 255
    cv.im.paste(Image.fromarray(a, 'RGBA'))


# ============================================================ 地面：木地板 / 大理石棋盘格 / 地毯
def plank_floor(cv, x0, x1, y0, y1, pal=WOOD, seed=0, polish=True):
    """深色木地板（侧视的一条条板，越近越宽、板头错开、木纹、板缝），polish = 上过蜡：每块板随机亮一点。"""
    a = np.array(cv.im)
    ww = x1 - x0 + 1
    rows = [y0]
    hgt = 2
    while rows[-1] <= y1:
        rows.append(rows[-1] + hgt)
        hgt = min(7, hgt + (1 if len(rows) % 2 else 0))
    for i in range(len(rows) - 1):
        ya, yb = rows[i], min(y1 + 1, rows[i + 1])
        if ya > y1:
            break
        Lp = 24 + i * 8
        offx = int(hrange(0, Lp, seed, i, 3))
        for k, xa in enumerate(range(x0 - offx, x1 + 1, Lp)):
            f = hrange(0.88, 1.06, seed, i, k, 5)
            col = np.array(pal['md'], np.float32) * f
            xa0, xb = max(x0, xa), min(x1 + 1, xa + Lp)
            if xa0 >= xb:
                continue
            a[ya:yb, xa0:xb, :3] = np.clip(col, 0, 255).astype(np.uint8)
            for g in range(int(hrange(1, 3, seed, i, k, 6))):           # 木纹
                gy = int(hrange(ya + 1, max(ya + 2, yb), seed, i, k, g, 7))
                gx0 = int(hrange(xa0, xb, seed, i, k, g, 8))
                for x in range(gx0, min(xb, gx0 + int(hrange(5, 14, seed, i, k, g, 9)))):
                    if gy <= y1:
                        a[gy, x, :3] = np.clip(np.array(a[gy, x, :3], np.float32) * 0.9, 0, 255)
            if x0 <= xa <= x1:                                         # 板头缝
                a[ya:yb, xa, :3] = (np.array(a[ya:yb, xa, :3], np.float32) * 0.72).astype(np.uint8)
        a[ya, x0:x1 + 1, :3] = (np.array(a[ya, x0:x1 + 1, :3], np.float32) * 0.74).astype(np.uint8)   # 板缝
        if polish and ya + 1 < yb:
            a[ya + 1, x0:x1 + 1, :3] = np.clip(np.array(a[ya + 1, x0:x1 + 1, :3], np.float32) * 1.08, 0, 255).astype(np.uint8)
    a[y0:y1 + 1, x0:x1 + 1, 3] = 255
    cv.im.paste(Image.fromarray(a, 'RGBA'))
    _ = ww


def checker_floor(cv, x0, x1, y0, y1, c1, c2, vx, seed=0, K=2.4, F=150.0, veins=True):
    """大理石棋盘格地面（透视，消失点 x = vx）：超采样再抖动量化，远处的格子化成干净的中间色；veins = 白格上几道细纹。"""
    rows = y1 - y0 + 1
    ww = x1 - x0 + 1
    ss = 4
    yy = (np.arange(rows * ss, dtype=np.float32) + 0.5) / ss
    xs = (np.arange(ww * ss, dtype=np.float32) + 0.5) / ss + x0 - vx
    z = 1.0 / (yy[:, None] + 3.0)
    u = xs[None, :] * z * K
    v = z * F
    chk = ((np.floor(u) + np.floor(v)) % 2).astype(np.float32)
    cov = chk.reshape(rows, ss, ww, ss).mean(axis=(1, 3))
    q = cov * 4
    thr = A._bayer(ww + x0, rows + y0)[y0:y0 + rows, x0:x0 + ww]
    lv = (np.floor(q) + ((q - np.floor(q)) > thr)) / 4
    c1a, c2a = np.array(c1, np.float32), np.array(c2, np.float32)
    col = c2a + (c1a - c2a) * lv[..., None]
    if veins:                                                          # 白格上的细纹（大理石）
        nz = A._fbm(ww + 8, rows + 8, 5, seed=seed % 997)[4:4 + rows, 4:4 + ww]
        vein = (np.abs(nz - 0.5) < 0.018) & (lv > 0.6)
        col[vein] = col[vein] * 0.86
    a = np.array(cv.im)
    a[y0:y1 + 1, x0:x1 + 1, :3] = np.clip(col, 0, 255).astype(np.uint8)
    a[y0:y1 + 1, x0:x1 + 1, 3] = 255
    cv.im.paste(Image.fromarray(a, 'RGBA'))


def carpet(cv, x0, x1, y0, y1, pal=CARPET, seed=0, ends=False, pattern=True):
    """厚地毯 / 长条地毯（y0..y1）：上下两道金边（外侧一道暗线）、里面一道暗红细线、红底上很淡的菱形连续纹
    （可走带：对比压低）；绒毛的细小明暗；ends = 两头有流苏。"""
    a = np.array(cv.im).astype(np.float32)
    hh = y1 - y0 + 1
    for y in range(y0, y1 + 1):
        r = y - y0
        rb = y1 - y
        for x in range(x0, x1 + 1):
            if r == 0 or rb == 0:
                c = pal['dd']
            elif r in (1, 2) or rb in (1, 2):
                c = pal['gold'] if (r == 1 or rb == 2) else pal['gold_d']
                if (x + (r if r < 3 else rb)) % 6 == 0:
                    c = pal['dk']                                      # 金边上的小方块纹
            elif r == 3 or rb == 3:
                c = pal['dk']
            else:
                c = pal['base']
                if pattern:
                    uu = (x - x0) % 12 - 6
                    vv = (r - 4) % max(4, (hh - 8)) - (hh - 8) / 2
                    if abs(abs(uu) / 6.0 + abs(vv) / max(2.0, (hh - 8) / 2.0) - 1) < 0.09:
                        c = pal['lt'] if hh > 12 else mix(pal['base'], pal['lt'], 0.5)
                    elif abs(uu) <= 0 and abs(vv) <= 0.5:
                        c = mix(pal['base'], pal['gold'], 0.45)
            if hash01(seed, x, y) < 0.08:                              # 绒毛
                c = mix(c, pal['dk'], 0.35)
            a[y, x, :3] = c
            a[y, x, 3] = 255
    cv.im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))
    if ends:
        d = cv.d
        for y in range(y0 + 1, y1, 2):
            px(d, x0 - 1, y, (200, 184, 150))
            px(d, x1 + 1, y, (200, 184, 150))


# ============================================================ 肖像画
SUBJECTS = {
    # 头发、衣服、衣领 / 饰物、背景（清漆底）
    'noble': dict(hair=(52, 36, 30), coat=(40, 40, 54), trim=(232, 226, 210), bg=(58, 50, 34), mous=True),
    'lady': dict(hair=(96, 60, 40), coat=(132, 30, 44), trim=(236, 230, 214), bg=(44, 52, 46), pearls=True),
    'old': dict(hair=(214, 210, 204), coat=(30, 28, 34), trim=(200, 190, 170), bg=(60, 44, 34), beard=True),
    'dio': dict(hair=(250, 214, 92), coat=(214, 170, 56), trim=(40, 52, 40), bg=(36, 22, 30), red=True),
    'boy': dict(hair=(70, 46, 30), coat=(60, 70, 96), trim=(236, 230, 214), bg=(52, 56, 40)),
    'same': dict(hair=(30, 22, 28), coat=(28, 22, 30), trim=(70, 60, 70), bg=(44, 24, 54), red=True, pale=True),
}


def gilt_frame(cv, x0, y0, x1, y1, pal=GOLD, ornate=True):
    """金框（3 px）：外一道墨线、金色斜面（左上亮右下暗）、里面一道珠线；ornate = 四角和上沿正中一朵卷草饰。"""
    d = cv.d
    rect(d, x0, y0, x1, y1, None, outline=INK)
    for i, c in ((1, pal['lt']), (2, pal['md']), (3, pal['dk'])):
        hl(d, x0 + i, x1 - i, y0 + i, pal['hi'] if i == 1 else c)
        vl(d, x0 + i, y0 + i, y1 - i, pal['hi'] if i == 1 else c)
        hl(d, x0 + i, x1 - i, y1 - i, pal['dk'] if i < 3 else pal['dd'])
        vl(d, x1 - i, y0 + i, y1 - i, pal['dk'] if i < 3 else pal['dd'])
    for x in range(x0 + 2, x1 - 1, 2):                                 # 珠线
        px(d, x, y0 + 2, pal['hi'])
        px(d, x, y1 - 2, pal['md'])
    if ornate:
        for (cx, cy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            rect(d, cx - 1, cy - 1, cx + 1, cy + 1, pal['md'])
            px(d, cx - 1, cy - 1, pal['hi'])
            px(d, cx + 1, cy + 1, pal['dd'])
        mx = (x0 + x1) // 2
        rect(d, mx - 2, y0 - 2, mx + 2, y0, pal['md'])
        px(d, mx, y0 - 3, pal['lt'])
        hl(d, mx - 2, mx + 2, y0 - 2, pal['hi'])
        px(d, mx - 3, y0 - 1, pal['lt'])
        px(d, mx + 3, y0 - 1, pal['dk'])


def portrait(cv, x0, y0, x1, y1, subject='noble', seed=0, cord=True):
    """油画肖像：金框 + 清漆深底 + 半身像（头发 / 脸 / 眼睛 / 衣服 / 衣领），对角一道清漆反光；画框挂绳。
    返回 dict(eyes=[(x, y) 左眼, (x, y) 右眼], face=(cx, cy))：strip 里只重画眼珠（“眼睛跟着人转”）。"""
    S = SUBJECTS[subject]
    d = cv.d
    if cord:                                                           # 挂绳 + 钉
        mx = (x0 + x1) // 2
        top = y0 - 7
        d.line((mx, top, x0 + 3, y0), fill=C((70, 60, 50)))
        d.line((mx, top, x1 - 3, y0), fill=C((70, 60, 50)))
        px(d, mx, top, GOLD['hi'])
        px(d, mx, top + 1, GOLD['dk'])
    gilt_frame(cv, x0, y0, x1, y1)
    d = cv.d
    cx0, cy0, cx1, cy1 = x0 + 4, y0 + 4, x1 - 4, y1 - 4
    cw, ch = cx1 - cx0 + 1, cy1 - cy0 + 1
    for y in range(cy0, cy1 + 1):                                      # 清漆底（上亮下暗 + 一圈暗角）
        u = (y - cy0) / max(1, ch - 1)
        hl(d, cx0, cx1, y, mix(lt(S['bg'], 0.12), dk(S['bg'], 0.7), u))
    vl(d, cx0, cy0, cy1, dk(S['bg'], 0.6))
    vl(d, cx1, cy0, cy1, dk(S['bg'], 0.6))
    fx = (cx0 + cx1) // 2                                              # 脸的中心
    head_w = max(5, int(cw * 0.42)) | 1
    head_h = max(6, int(ch * 0.34))
    fy0 = cy0 + max(2, int(ch * 0.16))
    fy1 = fy0 + head_h
    skin = SKIN if not S.get('pale') else dict(hi=(226, 220, 226), md=(196, 186, 200), dk=(140, 128, 150))
    # 衣服（肩膀）
    sh_y = fy1 + 2
    for y in range(sh_y, cy1 + 1):
        k = y - sh_y
        hw = min(cw // 2, head_w // 2 + 2 + k * 2)
        hl(d, fx - hw, fx + hw, y, S['coat'] if k > 0 else lt(S['coat'], 0.2))
        px(d, fx - hw, y, lt(S['coat'], 0.25))
        px(d, fx + hw, y, dk(S['coat'], 0.6))
    # 衣领 / 领巾
    for k in range(min(5, cy1 - sh_y + 1)):
        hw = max(0, 2 - k // 2)
        hl(d, fx - hw, fx + hw, sh_y + k, S['trim'])
    if S.get('pearls'):
        for i in range(-3, 4):
            px(d, fx + i, sh_y + 1 + abs(i) // 2, (240, 236, 226))
    if S.get('red'):                                                   # DIO / 幻觉的脸：衣领上一点暗红宝石
        px(d, fx, sh_y + 2, (170, 30, 40))
    # 脖子 + 脸
    rect(d, fx - 1, fy1, fx + 1, sh_y, skin['dk'])
    d.ellipse((fx - head_w // 2, fy0, fx + head_w // 2, fy1), fill=C(skin['md']))
    for y in range(fy0 + 1, fy1):                                      # 光从左上：左半亮、右沿暗
        px(d, fx - head_w // 2 + 1, y, skin['hi'])
        px(d, fx + head_w // 2 - 1, y, skin['dk'])
    # 头发
    hair = S['hair']
    if subject == 'dio':                                               # 往上翘的金发（一缕缕）
        for i in range(-head_w // 2 - 1, head_w // 2 + 2):
            hgt = 2 + int(2 * abs(math.sin(i * 1.3)))
            vl(d, fx + i, fy0 - hgt + 1, fy0 + 1, hair if i % 2 else lt(hair, 0.3))
        vl(d, fx - head_w // 2, fy0 + 1, fy0 + head_h // 2 + 1, hair)
        vl(d, fx + head_w // 2, fy0 + 1, fy0 + head_h // 2 + 1, dk(hair, 0.8))
    elif subject == 'lady':
        d.ellipse((fx - head_w // 2 - 1, fy0 - 3, fx + head_w // 2 + 1, fy0 + 3), fill=C(hair))
        d.ellipse((fx - 2, fy0 - 5, fx + 2, fy0 - 1), fill=C(hair))
        vl(d, fx - head_w // 2 - 1, fy0, fy1 - 1, hair)
        vl(d, fx + head_w // 2 + 1, fy0, fy1 - 1, dk(hair, 0.8))
    elif subject == 'same':                                            # 幻觉：同一张脸，黑发贴着脸垂下来
        d.ellipse((fx - head_w // 2 - 1, fy0 - 2, fx + head_w // 2 + 1, fy0 + 3), fill=C(hair))
        rect(d, fx - head_w // 2 - 1, fy0, fx - head_w // 2, fy1 + 2, hair)
        rect(d, fx + head_w // 2, fy0, fx + head_w // 2 + 1, fy1 + 2, hair)
    else:
        d.ellipse((fx - head_w // 2, fy0 - 2, fx + head_w // 2, fy0 + 3), fill=C(hair))
        px(d, fx - head_w // 2, fy0 + 3, hair)
        px(d, fx + head_w // 2, fy0 + 3, hair)
    if S.get('beard'):
        for y in range(fy1 - 3, fy1 + 2):
            hw = 2 if y < fy1 else 1
            hl(d, fx - hw, fx + hw, y, hair)
    if S.get('mous'):
        hl(d, fx - 2, fx + 2, fy0 + head_h * 2 // 3 + 1, hair)
    # 眼睛（眼白 + 眼珠：strip 只重画这两处）
    ey = fy0 + head_h // 2 - 1
    eyes = [(fx - 2, ey), (fx + 1, ey)]
    eye_px(d, eyes, 0, subject)
    # 嘴
    px(d, fx, fy0 + head_h * 3 // 4 + 1, dk(skin['dk'], 0.8) if not S.get('red') else (150, 40, 50))
    # 清漆反光：对角一道很淡的亮线
    for k in range(min(cw, ch) // 2):
        x, y = cx0 + 1 + k, cy0 + ch // 2 - k
        if cy0 <= y <= cy1 and cx0 <= x <= cx1 and k % 3 != 2:
            c = np.array(cv.im.getpixel((x, y))[:3], np.float32)
            px(d, x, y, tuple(int(v) for v in np.clip(c * 1.12 + 10, 0, 255)))
    return dict(eyes=eyes, face=(fx, (fy0 + fy1) // 2), subject=subject)


EYE_LOOK = (0, 0, -1, -1, 0, 1, 1, 0)       # 8 帧里眼珠的横向位置（−1 左、0 正视、1 右）：慢慢扫过去又看回来


def eye_px(d, eyes, look, subject='noble', blink=False):
    """两只眼：眼白 2 px（左右各一）+ 眼珠 1 px；look −1 / 0 / 1 = 眼珠在左 / 中 / 右；blink = 闭上（一道暗线）。"""
    S = SUBJECTS[subject]
    white = (232, 226, 214) if not S.get('pale') else (240, 236, 244)
    iris = (40, 30, 30) if not S.get('red') else (200, 30, 40)
    for (x, y) in eyes:
        if blink:
            hl(d, x, x + 1, y, (90, 60, 60))
            continue
        hl(d, x, x + 1, y, white)
        ix = x + (0 if look < 0 else 1) if look != 0 else x + (1 if x % 2 else 0)
        px(d, ix, y, iris)


# ============================================================ 烛台 / 蜡烛 / 火苗
def candle(cv, x, y, h=5, drip=True, seed=0):
    """一根蜡烛：底 y（托盘上面一行），宽 2 px，高 h；左亮右暗、蜡泪；烛芯在 y − h。返回火苗底 (x, y − h − 1)。"""
    d = cv.d
    for yy in range(y - h + 1, y + 1):
        px(d, x, yy, WAX['hi'])
        px(d, x + 1, yy, WAX['dk'])
    px(d, x, y - h + 1, WAX['md'])
    if drip:
        if hash01(seed, 1) < 0.6:
            px(d, x - 1, y - h + 2 + int(hash01(seed, 2) * 2), WAX['md'])
        if hash01(seed, 3) < 0.5:
            px(d, x + 2, y - h + 3, WAX['dk'])
    px(d, x, y - h, (40, 30, 26))                                      # 烛芯
    return (x, y - h - 1)


def sconce(cv, x, y, arms=1, pal=GOLD, h=5, seed=0):
    """壁烛台（铜）：背板（椭圆、有亮边）+ 弯臂 + 接蜡泪的小托盘 + 蜡烛；y = 托盘那一行。
    arms = 1 / 2 / 3 根蜡烛（两三根的往两边伸开）。返回火苗底的坐标列表。"""
    d = cv.d
    # 背板
    by = y + 4
    d.ellipse((x - 2, by - 1, x + 2, by + 6), fill=C(pal['md']), outline=C(INK))
    vl(d, x - 1, by, by + 5, pal['hi'])
    vl(d, x + 1, by + 1, by + 5, pal['dk'])
    px(d, x, by + 2, pal['dd'])
    flames = []
    offs = {1: [0], 2: [-4, 4], 3: [-6, 0, 6]}[arms]
    for i, dx in enumerate(offs):
        cx = x + dx
        # 臂：从背板往外、往上弯
        if dx == 0:
            vl(d, x, y + 1, by - 1, pal['md'])
            px(d, x + 1, y + 2, pal['dk'])
        else:
            sgn = 1 if dx > 0 else -1
            for k in range(abs(dx) + 1):
                yy = by + 1 - int(round(3 * math.sin(k / max(1, abs(dx)) * math.pi * 0.5)))
                px(d, x + sgn * k, yy, pal['md'] if k % 2 else pal['lt'])
                px(d, x + sgn * k, yy + 1, pal['dk'])
            vl(d, cx, y + 1, by - 2, pal['md'])
        # 托盘
        hl(d, cx - 2, cx + 2, y, pal['lt'])
        hl(d, cx - 1, cx + 1, y + 1, pal['dk'])
        px(d, cx - 2, y, pal['hi'])
        flames.append(candle(cv, cx, y - 1, h=h, seed=seed * 7 + i))
    return flames


def candelabra(cv, x, base_y, h=26, arms=3, pal=GOLD, seed=0):
    """落地 / 台面烛台：三脚底座、带两节球饰的立杆、S 形横臂、托盘 + 蜡烛。返回火苗底列表。"""
    d = cv.d
    top = base_y - h
    # 底座
    hl(d, x - 4, x + 4, base_y, pal['dk'])
    hl(d, x - 3, x + 3, base_y - 1, pal['md'])
    px(d, x - 4, base_y - 1, pal['hi'])
    rect(d, x - 1, base_y - 4, x + 1, base_y - 2, pal['md'])
    # 立杆 + 球饰
    vl(d, x, top + 3, base_y - 4, pal['md'])
    vl(d, x - 1, top + 3, base_y - 4, pal['lt'])
    vl(d, x + 1, top + 3, base_y - 4, pal['dk'])
    for ky in (base_y - h // 3, top + h // 3):
        rect(d, x - 2, ky - 1, x + 2, ky + 1, pal['md'])
        px(d, x - 2, ky - 1, pal['hi'])
        px(d, x + 2, ky + 1, pal['dd'])
    flames = []
    offs = {1: [0], 3: [-7, 0, 7], 5: [-10, -5, 0, 5, 10]}[arms]
    for i, dx in enumerate(offs):
        cx = x + dx
        if dx:
            sgn = 1 if dx > 0 else -1
            for k in range(abs(dx) + 1):
                yy = top + 4 - int(round(3 * math.sin(k / abs(dx) * math.pi * 0.5)))
                px(d, x + sgn * k, yy, pal['lt'] if k % 2 else pal['md'])
                px(d, x + sgn * k, yy + 1, pal['dk'])
        cy = top + (1 if dx else -1)
        hl(d, cx - 2, cx + 2, cy, pal['lt'])
        hl(d, cx - 1, cx + 1, cy + 1, pal['dk'])
        flames.append(candle(cv, cx, cy - 1, h=4 + int(hash01(seed, i) * 3), seed=seed * 11 + i))
    return flames


FL_H = (3, 4, 4, 3, 4, 5, 4, 3)
FL_LEAN = (0, 0, 1, 0, -1, 0, 0, 1)


def flame(d, x, y, f, seed=0, down=False, big=False, pal=FLAME):
    """一朵烛火（f 帧，8 帧一圈）：y = 火苗最下面一行（烛芯上面）；最下面是白芯、往上黄、尖是橙；尖左右晃。
    down = 往下烧（幻觉走廊）：同样的颜色倒过来长在烛芯下面。big = 宽 2 px（落地烛台 / 吊灯的粗蜡烛）。"""
    ph = (f + seed * 3) % N8
    h = FL_H[ph] + (1 if big else 0)
    lean = FL_LEAN[(ph + seed) % N8]
    sg = 1 if down else -1
    for r in range(h):
        c = pal[0] if r == 0 else (pal[1] if r < h - 2 else (pal[2] if r < h - 1 else pal[3]))
        xx = x + (lean if r >= h - 2 and r > 0 else 0)
        px(d, xx, y + sg * r, c)
        if big and r < h - 2:
            px(d, xx + 1, y + sg * r, pal[1] if r else pal[0])
    if (ph % 4) == 1:                                                  # 偶尔跳一个小火星
        px(d, x + lean, y + sg * (h + 1), pal[2])


def flames_frame_fn(points, w, h, down=False, big=(), seed0=0):
    """返回一个 strip 帧函数：t → w×h 透明图上画 points 的火苗（points = [(x, y), …]，世界坐标）。"""
    def fn(t):
        im = A._new(w, h)
        d = ImageDraw.Draw(im)
        f = int(math.floor(t * FPS_FIRE + 1e-6)) % N8
        for i, (x, y) in enumerate(points):
            flame(d, x, y, f, seed=seed0 + i, down=down, big=(i in big))
        return im
    return fn


def flame_box(x, y, down=False, big=False):
    """一朵火苗 strip 的框（右下不含）：火苗最高 6 行 + 晃 1 px + 火星。"""
    if down:
        return (x - 1, y, x + 3 if big else x + 2, y + 9)
    return (x - 1, y - 8, x + 3 if big else x + 2, y + 1)


# ============================================================ 门 / 封死的窗 / 丝绒帘 / 蛛网
def gothic_door(cv, x0, y0, w, h, pal=WOOD, frame=STONE, kind='arch', seed=0, plaque=None, keyhole=True):
    """哥特式木门（关着）：石门套（尖拱 / 平顶 + 门楣三角），竖木板（板缝、木纹），三道铁合页（带卷头）、一圈铆钉、
    铁环拉手、锁孔，门下一道门槛石。(x0, y0) = 门洞左上（尖拱顶点那一行），w × h = 门洞宽高（不含门套）。
    plaque = (颜色, 标记) 门上的小铜牌（游戏室的门）。keyhole = False：把锁孔换成一块实心的铁板（“连钥匙孔都没有”的那扇门）。
    返回门洞框。"""
    d = cv.d
    x1, y1 = x0 + w - 1, y0 + h - 1
    rise = w // 2 + 1 if kind == 'arch' else 0
    top = arch_rows(w, rise, pointed=True) if rise else [0] * w
    # 门套（石）：外扩 3 px
    for i in range(-3, w + 3):
        if 0 <= i < w:
            yt = y0 + rise - int(round(top[i])) - 3
        else:
            j = 0 if i < 0 else w - 1
            yt = y0 + rise - int(round(top[j])) - 2 + (1 if rise else 0)
        c = frame['lt'] if i < 0 else (frame['dk'] if i >= w else frame['md'])
        vl(d, x0 + i, yt, y1, c)
        px(d, x0 + i, yt, frame['hi'] if i < w // 2 else frame['md'])
    vl(d, x0 - 3, y0 + rise - 2, y1, frame['hi'])
    vl(d, x1 + 3, y0 + rise - 2, y1, frame['dd'])
    if rise:                                                           # 拱心石
        rect(d, x0 + w // 2 - 1, y0 - 3, x0 + w // 2 + 1, y0, frame['lt'])
        px(d, x0 + w // 2 + 1, y0, frame['dk'])
    # 门板
    for i in range(w):
        yt = y0 + rise - int(round(top[i]))
        c = pal['md']
        if i % 5 == 0:
            c = pal['dd']                                             # 板缝
        elif i % 5 == 1:
            c = pal['lt']
        vl(d, x0 + i, yt, y1, c)
        px(d, x0 + i, yt, pal['dd'])
    for g in range(w // 2):                                           # 木纹
        gx = x0 + 2 + int(hrange(0, w - 4, seed, g, 1))
        gy = y0 + rise + int(hrange(2, h - rise - 6, seed, g, 2))
        if (gx - x0) % 5 not in (0, 1):
            vl(d, gx, gy, gy + int(hrange(2, 6, seed, g, 3)), pal['dk'])
    vl(d, x0, y0 + rise, y1, pal['dd'])
    vl(d, x1, y0 + rise, y1, pal['dd'])
    # 铁合页（三道横带，左边起、卷头朝右）
    for hy in (y0 + rise + 3, y0 + (h + rise) // 2, y1 - 6):
        hl(d, x0 + 1, x0 + w * 2 // 3, hy, IRON['md'])
        hl(d, x0 + 1, x0 + w * 2 // 3, hy + 1, IRON['dd'])
        px(d, x0 + w * 2 // 3 + 1, hy, IRON['md'])
        px(d, x0 + w * 2 // 3 + 1, hy - 1, IRON['hi'])
        for xx in range(x0 + 2, x0 + w * 2 // 3, 3):
            px(d, xx, hy, IRON['hi'])                                  # 铆钉
    # 铁环拉手 + 锁孔
    hx, hy = x1 - 4, y0 + (h + rise) // 2 + 4
    d.ellipse((hx - 2, hy - 1, hx + 2, hy + 3), outline=C(IRON['md']))
    px(d, hx - 1, hy - 1, IRON['hi'])
    px(d, hx, hy - 2, IRON['dk'])
    if keyhole:
        px(d, hx, hy + 6, (14, 10, 12))
        px(d, hx, hy + 7, (14, 10, 12))
    else:                                                              # 实心铁板：没有孔，只有板边的亮暗
        rect(d, hx - 1, hy + 5, hx + 1, hy + 8, IRON['md'], outline=IRON['dk'])
        px(d, hx - 1, hy + 5, IRON['hi'])
    if plaque:
        col, mark = plaque
        py = y0 + rise + 8
        rect(d, x0 + w // 2 - 4, py, x0 + w // 2 + 3, py + 4, col, outline=dk(col, 0.6))
        hl(d, x0 + w // 2 - 3, x0 + w // 2 + 2, py + 1, lt(col, 0.3))
        if mark == 'dice':
            for (mx, my) in ((-2, 2), (0, 2), (2, 2)):
                px(d, x0 + w // 2 + mx, py + my, (40, 20, 20))
    # 门槛
    hl(d, x0 - 3, x1 + 3, y1 + 1, frame['hi'])
    hl(d, x0 - 3, x1 + 3, y1 + 2, frame['dk'])
    # 门套在墙上的影子（右下）
    mul_box(cv.im, (x1 + 4, y0 + rise, x1 + 5, y1 + 1), (0.72, 0.72, 0.8))
    return (x0, y0, x1, y1)


def black_window(cv, x0, y0, w, h, slit='r', boards=True, seed=0, frame=STONE, light=(255, 240, 210)):
    """被黑布封住的高窗：尖拱窗洞（石套）里绷着黑布（竖褶、下沿松垂、四周一圈钉子），boards = 两块斜钉的木板；
    slit = 'l' / 'r' / None：黑布没贴严的那一边漏出 1 px 的一线光（发光像素）+ 中间一个小破洞。
    返回 dict(slit=[(x, y0, y1)], hole=(x, y))：光带 / 灰尘 strip 从这里出发。"""
    d = cv.d
    x1, y1 = x0 + w - 1, y0 + h - 1
    rise = w // 2 + 1
    top = arch_rows(w, rise, pointed=True)
    # 石窗套（外扩 2）+ 窗台
    for i in range(-2, w + 2):
        j = min(max(i, 0), w - 1)
        yt = y0 + rise - int(round(top[j])) - 2
        vl(d, x0 + i, yt, y1 + 1, frame['lt'] if i < 0 else (frame['dk'] if i >= w else frame['md']))
    rect(d, x0 - 3, y1 + 1, x1 + 3, y1 + 2, frame['lt'])
    hl(d, x0 - 3, x1 + 3, y1 + 1, frame['hi'])
    hl(d, x0 - 2, x1 + 2, y1 + 3, frame['dd'])
    # 黑布
    for i in range(w):
        yt = y0 + rise - int(round(top[i]))
        ph = ((i + seed) % 5)
        c = BLACKCLOTH['md'] if ph in (0, 1) else (BLACKCLOTH['lt'] if ph == 2 else BLACKCLOTH['dk'])
        sag = int(round(1.5 * math.sin(math.pi * i / max(1, w - 1))))
        vl(d, x0 + i, yt, y1 - 1 + sag if sag else y1, c)
        px(d, x0 + i, yt, BLACKCLOTH['dd'])
    for i in range(0, w, 3):                                           # 钉子
        px(d, x0 + i, y0 + rise - int(round(top[i])), GOLD['dk'])
        px(d, x0 + i, y1, GOLD['dk'])
    for yy in range(y0 + rise, y1, 4):
        px(d, x0, yy, GOLD['dk'])
        px(d, x1, yy, GOLD['dk'])
    info = dict(slit=[], hole=None)
    if slit:
        sx = x0 if slit == 'l' else x1
        ya = y0 + rise - int(round(top[0 if slit == 'l' else w - 1])) + 1
        for yy in range(ya, y1):
            if hash01(seed, yy, 4) < 0.88:
                cv.glow_px(sx, yy, light if (yy % 7) else lt(light, 0.3))
        info['slit'].append((sx, ya, y1 - 1))
    hx, hy = x0 + w // 2 + int(hrange(-2, 2, seed, 5)), y0 + rise + (h - rise) // 3
    cv.glow_px(hx, hy, light)
    info['hole'] = (hx, hy)
    if boards:                                                         # 两块斜钉的木板（X）
        for (ax, ay, bx, by) in ((x0 - 1, y0 + rise + 2, x1 + 1, y1 - 4), (x1 + 1, y0 + rise + 2, x0 - 1, y1 - 4)):
            d.line((ax, ay, bx, by), fill=C(WOOD['md']), width=3)
            d.line((ax, ay - 1, bx, by - 1), fill=C(WOOD['lt']))
            d.line((ax, ay + 1, bx, by + 1), fill=C(WOOD['dd']))
            px(d, ax + (1 if ax < bx else -1), ay, IRON['hi'])
            px(d, bx + (-1 if ax < bx else 1), by, IRON['hi'])
    return info


def velvet_curtain(cv, x0, x1, y0, y1, side='l', tie=None, pal=VELVET, seed=0):
    """丝绒落地帘：竖褶（亮 / 中 / 暗循环），tie = 绑带的 y（往绑带收窄、下面再散开），下摆一道暗。"""
    d = cv.d
    w = x1 - x0 + 1
    for y in range(y0, y1 + 1):
        if tie is not None:
            if y < tie:
                pinch = (y - y0) / max(1, tie - y0)
                shrink = int(round(pinch ** 2 * w * 0.35))
            else:
                shrink = int(round(max(0.0, 1 - (y - tie) / 16.0) * w * 0.35))
        else:
            shrink = 0
        xa, xb = (x0, x1 - shrink) if side == 'l' else (x0 + shrink, x1)
        n = xb - xa + 1
        for i in range(n):
            u = i / max(1, n - 1)
            ph = (u * (w / 3.6) + hash01(seed, 1) * 0.3) % 1.0
            c = pal['hi'] if ph < 0.16 else pal['lt'] if ph < 0.38 else pal['md'] if ph < 0.68 else pal['dk']
            if y > y1 - 2:
                c = dk(c, 0.78)
            px(d, xa + i, y, c)
        px(d, xb if side == 'l' else xa, y, pal['dd'])
    if tie is not None:
        xa, xb = (x0, x1 - int(w * 0.35)) if side == 'l' else (x0 + int(w * 0.35), x1)
        hl(d, xa, xb, tie, GOLD['lt'])
        hl(d, xa, xb, tie + 1, GOLD['dk'])
        tx = xb if side == 'l' else xa
        for k in range(5):
            px(d, tx, tie + 2 + k, GOLD['lt'] if k % 2 == 0 else GOLD['md'])
        px(d, tx - 1, tie + 6, GOLD['md'])
        px(d, tx + 1, tie + 6, GOLD['dk'])


def valance(cv, x0, x1, y, h=6, pal=VELVET, scallop=8):
    """帘头：金色帘杆 + 一排扇形下摆的丝绒 + 流苏。"""
    d = cv.d
    hl(d, x0 - 2, x1 + 2, y - 1, GOLD['hi'])
    hl(d, x0 - 2, x1 + 2, y, GOLD['md'])
    rect(d, x0 - 3, y - 2, x0 - 1, y + 1, GOLD['lt'])
    rect(d, x1 + 1, y - 2, x1 + 3, y + 1, GOLD['dk'])
    for x in range(x0, x1 + 1):
        u = ((x - x0) % scallop) / scallop
        dep = h - 2 + int(round(2 * math.sin(math.pi * u)))
        for yy in range(y + 1, y + 1 + dep):
            c = pal['lt'] if yy < y + 3 else pal['md']
            if (x - x0) % scallop == 0:
                c = pal['dk']
            px(d, x, yy, c)
        px(d, x, y + dep, GOLD['md'] if x % 2 else GOLD['dk'])


def cobweb(cv, x, y, r, corner='tl', col=(158, 152, 166), seed=0):
    """角落的蛛网：从角往外的 5 根放射丝 + 3 圈下垂的横丝（1 px，断断续续）。corner = 网贴着的角。"""
    d = cv.d
    sx = 1 if corner in ('tl', 'bl') else -1
    sy = 1 if corner in ('tl', 'tr') else -1
    angs = [0.04, 0.38, 0.78, 1.18, 1.52]
    ends = []
    for k, a in enumerate(angs):
        L_ = r * hrange(0.8, 1.05, seed, k)
        ex = x + sx * L_ * math.cos(a)
        ey = y + sy * L_ * math.sin(a)
        ends.append((a, L_))
        n = int(L_)
        for s in range(n):
            u = s / max(1, n - 1)
            if hash01(seed, k, s) < 0.86:
                px(d, round(x + (ex - x) * u), round(y + (ey - y) * u), col)
    for ring in (0.35, 0.62, 0.9):
        for k in range(len(angs) - 1):
            a0, a1 = angs[k], angs[k + 1]
            for s in range(7):
                u = s / 6
                a = a0 + (a1 - a0) * u
                rr = r * ring * (1 - 0.12 * math.sin(math.pi * u))
                if hash01(seed, ring, k, s) < 0.8:
                    px(d, round(x + sx * rr * math.cos(a)), round(y + sy * rr * math.sin(a)), dk(col, 0.9))


# ============================================================ 乌鸦 / 蝙蝠
def bat(d, x, y, f, col=(16, 10, 20)):
    """蝙蝠（7×4）：4 个姿势循环（翅膀上 / 平 / 下 / 平）。"""
    x, y = int(x), int(y)
    ph = f % 4
    px(d, x, y, col)
    px(d, x, y + 1, col)
    px(d, x - 1, y - 1, col)
    px(d, x + 1, y - 1, col)                                           # 耳朵
    if ph == 0:
        pts = [(-1, 0), (-2, -1), (-3, -2), (1, 0), (2, -1), (3, -2)]
    elif ph in (1, 3):
        pts = [(-1, 0), (-2, 0), (-3, 0), (1, 0), (2, 0), (3, 0), (-3, 1), (3, 1)]
    else:
        pts = [(-1, 1), (-2, 1), (-3, 2), (1, 1), (2, 1), (3, 2)]
    for (dx, dy) in pts:
        px(d, x + dx, y + dy, col)


def crow_fly(d, x, y, f, col=(18, 14, 22), hi=(70, 66, 84)):
    """飞着的乌鸦（9×5，朝左）：翅膀 4 个姿势。"""
    x, y = int(x), int(y)
    ph = f % 4
    hl(d, x - 2, x + 2, y, col)                                        # 身子
    px(d, x - 3, y, col)
    px(d, x - 4, y + (0 if ph else 1), (70, 60, 40))                   # 嘴
    px(d, x + 3, y, col)
    px(d, x + 4, y + 1, col)                                           # 尾
    if ph == 0:
        for (dx, dy) in ((-1, -1), (0, -2), (1, -3), (2, -3), (0, -1), (1, -2)):
            px(d, x + dx, y + dy, col)
        px(d, x + 1, y - 2, hi)
    elif ph in (1, 3):
        for (dx, dy) in ((-1, -1), (1, -1), (2, -1), (3, -1)):
            px(d, x + dx, y + dy, col)
    else:
        for (dx, dy) in ((0, 1), (1, 2), (2, 2), (1, 1)):
            px(d, x + dx, y + dy, col)


def crow_perch(d, x, y, pose=0, col=(20, 16, 24), hi=(78, 72, 92), eye=(220, 60, 40), face=-1):
    """站着的乌鸦（约 6×8，y = 脚），pose 0 站 / 1 转头 / 2 张嘴叫 / 3 抖翅膀；face −1 朝左、1 朝右。"""
    x, y = int(x), int(y)
    s = face
    px(d, x, y, (60, 50, 40))
    px(d, x + 1, y, (60, 50, 40))                                      # 脚
    for (dx, dy) in ((0, -1), (1, -1), (-1, -2), (0, -2), (1, -2), (2, -2), (-1, -3), (0, -3), (1, -3), (2, -3),
                     (0, -4), (1, -4), (-1, -4)):
        px(d, x + dx * -s if s > 0 else x + dx, y + dy, col)
    px(d, x + (3 if s < 0 else -2), y - 2, col)                        # 尾
    px(d, x + (3 if s < 0 else -2), y - 1, col)
    hx = x + (0 if pose != 1 else (1 if s < 0 else 0))
    hy = y - 5 - (1 if pose == 3 else 0)
    px(d, hx, hy, col)
    px(d, hx + 1, hy, col)
    px(d, hx, hy - 1, col)
    bx = hx - 1 if (s < 0) != (pose == 1) else hx + 2
    px(d, bx, hy, (90, 80, 60))                                        # 嘴
    if pose == 2:
        px(d, bx, hy + 1, (90, 80, 60))
        px(d, bx - (1 if bx < hx else -1), hy - 1, (60, 54, 44))
    px(d, hx + (0 if bx < hx else 1), hy - 1, eye)                     # 一点红眼
    px(d, x + 1, y - 3, hi)                                            # 翅膀反光
    if pose == 3:
        px(d, x - 1, y - 4, col)
        px(d, x + 2, y - 4, col)
        px(d, x - 2, y - 3, col)
        px(d, x + 3, y - 3, col)


# ============================================================ 天：月亮 / 星 / 夜空
def night_sky(w, h, seed=0, stops=None, stars=90, star_y=110):
    """夜空（不透明 RGBA）：深蓝紫渐变 + 星星（越往上越多、几颗大的十字星）。"""
    im = A._new(w, h)
    gradient(im, (0, 0, w, h), stops or [(8, 6, 20), (18, 14, 40), (34, 26, 62), (52, 36, 74)], bands=10)
    d = ImageDraw.Draw(im)
    for i in range(stars):
        x = int(hrange(0, w, seed, i, 1))
        y = int(star_y * hash01(seed, i, 2) ** 1.5)
        b = hash01(seed, i, 3)
        c = mix((230, 230, 255), (90, 84, 130), 0.7 - 0.6 * b)
        px(d, x, y, c)
        if b > 0.93:
            for (dx, dy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                px(d, x + dx, y + dy, mix(c, (40, 36, 80), 0.5))
    return im


def moon(im, cx, cy, r, col=(250, 242, 210), shade=(214, 204, 176), crater=(230, 220, 190), glow=(190, 190, 250),
         strength=0.32):
    """满月 + 一圈抖动的光晕（借原工程 bg_egypt._moon）。"""
    E._moon(im, cx, cy, r, col=col, shade=shade, crater=crater, glow=glow, strength=strength)


# ============================================================ 光带里的浮尘 / 雾
def motes_frame_fn(poly_pts, w, h, n=18, seed=0, col=(255, 246, 220), fps=FPS_SLOW, drift=(0.0, 1.0)):
    """光带里慢慢飘的浮尘（只画在 poly 里面）：每粒按自己的相位上下漂，8 帧回到原位。"""
    m = poly_mask((w, h), poly_pts)
    ys, xs = np.nonzero(m)
    pts = list(zip(xs.tolist(), ys.tolist()))
    pick = [pts[int(hash01(seed, i, 1) * len(pts))] for i in range(n)] if pts else []

    def fn(t):
        im = A._new(w, h)
        d = ImageDraw.Draw(im)
        f = int(math.floor(t * fps + 1e-6)) % N8
        for i, (x, y) in enumerate(pick):
            ph = (f / N8 + hash01(seed, i, 2)) % 1.0
            dx = int(round(drift[0] * math.sin(math.tau * ph)))
            dy = int(round(2 * drift[1] * math.sin(math.tau * ph + i)))
            xx, yy = x + dx, y + dy
            if 0 <= xx < w and 0 <= yy < h and m[yy, xx] and (i + f) % 3 != 0:
                px(d, xx, yy, col if (i % 2) else mix(col, (180, 160, 140), 0.4))
        return im
    return fn, m


def strip_bbox(fn, n=N8, fps=FPS_SLOW, pad=0):
    """把 fn 的 n 帧叠起来求外框（右下不含），strip 的框按实际画到的范围取，省体积。"""
    acc = None
    for i in range(n):
        a = np.array(fn(i / fps))[..., 3] > 0
        acc = a if acc is None else (acc | a)
    ys, xs = np.nonzero(acc)
    if not len(xs):
        return (0, 0, 1, 1)
    return (int(xs.min()) - pad, int(ys.min()) - pad, int(xs.max()) + 1 + pad, int(ys.max()) + 1 + pad)


# ============================================================ 自检的公共部分
def check_strips(ex, BJ, strips):
    """strips = [(name, box, n, fps, fn)]：闭合 / 帧条宽 / 每帧在动 / 画的东西都在框里（同一个帧函数合起来算）。"""
    for (name, box, n, fps, fn) in strips:
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
    fns = {}
    for (name, box, n, fps, fn) in strips:
        fns.setdefault(fn, []).append((name, box, n, fps))
    for fn, items in fns.items():
        lost = 0
        n, fps = items[0][2], items[0][3]
        for i in range(n):
            m = np.array(fn(i / fps))[..., 3] > 0
            for (_, box, _, _) in items:
                m[max(0, box[1]):box[3], max(0, box[0]):box[2]] = False
            lost += int(m.sum())
        ex.checked('strip %s 每帧画的东西都在框里（框外的像素）' % '+'.join(it[0] for it in items), lost)


def check_anchor_tree(v, w, h):
    """anchors 里的值（点 / 框 / 点的列表 / dict）都在地图里：返回不满足的个数。"""
    num = lambda q: isinstance(q, (int, float)) and not isinstance(q, bool)   # noqa: E731
    if isinstance(v, dict):
        return sum(check_anchor_tree(x, w, h) for x in v.values())
    if isinstance(v, (list, tuple)):
        if len(v) == 2 and all(num(q) for q in v):
            return int(not (0 <= v[0] <= w and 0 <= v[1] <= h))
        if len(v) == 4 and all(num(q) for q in v):
            return int(not (0 <= v[0] < v[2] <= w and 0 <= v[1] < v[3] <= h))
        if v and all(num(q) for q in v):
            return 0
        return sum(check_anchor_tree(x, w, h) for x in v)
    return 0


# ============================================================ 场景框架（2026-10-19 第三轮：六张图共用）
# 图层表 → 直接拼（compose，照 bg_jojo.ref_render 的公式和取整）/ 导出（export_stage）/ 自检（common_checks）。
# 照 ch5_town_parts.py 的写法自己存一份：本组的图不跟着别组的零件模块改动走（别组的文件只读不改）。
import io  # noqa: E402


def frame_of(t, fps, n=N8):
    """t 秒 → 第几帧（同 bg.js 的 floor(t·fps + 1e-6) mod n；+1e-6 免得 i/fps 乘回来差一点掉到上一帧）。"""
    return int(math.floor(t * fps + 1e-6)) % n


def crop_alpha(img, x=0, y=0):
    """裁到不透明像素的外接框（省 PNG 体积）：返回 (图, x, y)；整张透明时返回 1×1 透明图。"""
    bb = img.getchannel('A').getbbox()
    if not bb:
        return A._new(1, 1), x, y
    return img.crop(bb), x + bb[0], y + bb[1]


def L_static(name, img, x=0, y=0, key=None, crop=True):
    if crop:
        img, x, y = crop_alpha(img, x, y)
    return dict(t='static', name=name, img=img, x=x, y=y, key=key)


def L_pano(name, img, k=1.0, x=0, y=0, key=None, crop=True):
    if crop:
        img, x, y = crop_alpha(img, x, y)
    return dict(t='pano', name=name, img=img, k=k, x=x, y=y, key=key)


def L_strip(name, box, n, fps, fn, k=1.0, key=None):
    """fn(t) → 这一层坐标系里的整张 RGBA（世界层宽），导出时裁 box、烘 n 帧。"""
    return dict(t='strip', name=name, box=tuple(int(v) for v in box), n=n, fps=fps, fn=fn, k=k, key=key)


def L_pick(name, key, values, images, x=0, y=0, k=1.0, crop=True):
    """按 state[key] 选图（值最接近的那张）。几张图共用一个左上角：crop 时按所有图的并集外接框一起裁。
    k 一定要写（bg.js 的 pick 默认 k = 0 = 贴屏幕）。"""
    if crop:
        bb = None
        for im in images:
            b = im.getchannel('A').getbbox()
            if b:
                bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
        if bb is None:
            bb = (0, 0, 1, 1)
        images = [im.crop(bb) for im in images]
        x, y = x + bb[0], y + bb[1]
    return dict(t='pick', name=name, key=key, values=list(values), images=list(images), x=x, y=y, k=k)


def compose(layers, fg, camX, t=0.5, state=None, with_fg=True):
    """直接拼一帧（不经导出）：照 bg_jojo.ref_render 的公式和取整，自检“导出 vs 直接拼”用。"""
    st = state or {}
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for L in list(layers) + (list(fg) if with_fg else []):
        typ = L['t']
        if L.get('key') and typ != 'pick' and not st.get(L['key']):
            continue
        if typ == 'static':
            paste(out, L['img'], L['x'], L['y'])
        elif typ == 'pano':
            paste(out, L['img'], L['x'] - math.floor(camX * L['k']), L['y'])
        elif typ == 'strip':
            b = L['box']
            f = int(math.floor(t * round(L['fps'], 6))) % L['n']
            paste(out, L['fn'](f / L['fps']).crop(b), b[0] - math.floor(camX * L['k']), b[1])
        elif typ == 'pick':
            v = st.get(L['key'], 0) or 0
            v = v if isinstance(v, (int, float)) else (1 if v else 0)
            vals = L['values']
            i = min(range(len(vals)), key=lambda j: abs(vals[j] - v))
            paste(out, L['images'][i], L['x'] - math.floor(camX * L['k']), L['y'])
    return out


def export_layers(ex, layers):
    out = []
    for L in layers:
        typ = L['t']
        if typ == 'static':
            d = dict(type='static', image=ex.img(L['name'], L['img']), x=L['x'], y=L['y'])
        elif typ == 'pano':
            d = dict(type='pano', image=ex.img(L['name'], L['img']), k=L['k'], x=L['x'], y=L['y'])
        elif typ == 'strip':
            d = ex.bake(L['name'], L['box'], L['n'], L['fps'], L['fn'], screen=False, k=L['k'])
        elif typ == 'pick':
            d = dict(type='pick', key=L['key'], values=L['values'],
                     images=[ex.img('%s%d' % (L['name'], i), im) for i, im in enumerate(L['images'])],
                     x=L['x'], y=L['y'], k=L['k'])
        else:
            raise ValueError(typ)
        if L.get('key') and typ != 'pick':
            d['key'] = L['key']
        out.append(d)
    return out


def export_stage(ex, pw, ground, walk, layers, fg, anchors):
    return ex.stage(pw, ground, walk, export_layers(ex, layers), export_layers(ex, fg), anchors)


def auto_box(fn, n=N8, fps=FPS_SLOW, pad=0, limit=None):
    """strip 的框 = n 帧画到的像素的外接框（+pad）：框从画出来的东西算，“每帧画的东西都在框里”天然成立。"""
    bb = None
    for i in range(n):
        b = fn(i / fps).getchannel('A').getbbox()
        if not b:
            continue
        bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    if bb is None:
        raise ValueError('strip 每一帧都是空的')
    x0, y0, x1, y1 = bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad
    if limit:
        x0, y0, x1, y1 = max(x0, limit[0]), max(y0, limit[1]), min(x1, limit[2]), min(y1, limit[3])
    return (x0, y0, x1, y1)


def frames_fn(frames, fps):
    """n 张整图 → fn(t)（同一个函数对象：几个 strip 共用时“框外像素”一起算）。"""
    n = len(frames)

    def fn(t):
        return frames[frame_of(t, fps, n)]
    return fn


def diff_frames(base, frames):
    """frames（和 base 同尺寸、不透明的整图）→ 跟 base 一样的像素抠成透明：strip 只留真的在变的像素，
    体积小，而且叠在 base 上逐像素和整图一样。注意：base 和 strip 之间不能再夹别的层（会从透明处露出来）。"""
    b = np.array(base)
    out = []
    for f in frames:
        a = np.array(f).copy()
        same = (a[..., :3] == b[..., :3]).all(-1) | (a[..., 3] == 0)
        a[same] = 0
        a[..., 3] = np.where(same, 0, 255)
        out.append(Image.fromarray(a, 'RGBA'))
    return out


def png_bytes(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.tell()


def common_checks(ex, BJ, st, layers, fg, cfg):
    """六张图共用的自检（照 ganges_ghat._checks / egypt_town_parts.common_checks）。cfg = dict(
        title, PW, walk（地图的可走带）, base（底图整张：必须不透明、可走带平整看它）, states（要测的状态组合）,
        stand（站人的锚点名）, required（素材总表要求的锚点名）, size_limit, flat=(x0, x1, y0, y1, tol, frac),
        flat_skip=[框], cams_step, export_states（导出 vs 直接拼要测的状态，默认 = states））。"""
    imgs = ex.images
    PW = cfg['PW']
    title = cfg['title']
    cams = sorted(set(list(range(0, max(1, PW - W + 1), cfg.get('cams_step', 40))) + [max(0, PW - W)]))
    states = cfg.get('states') or [{}]
    bad = 0
    for camX in cams:
        for tt in (0.0, 0.75, 1.5, 7.0):
            for s in states:
                im = np.array(BJ.ref_render(st, imgs, camX, tt, s).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('%s 镜头 0–%d（每 %d）× 4 个时刻 × %d 种状态 整屏都有画（没有露黑）' %
               (title, cams[-1], cfg.get('cams_step', 40), len(states)), bad)
    base = np.array(cfg['base'])
    ex.checked('底图整张（%d×%d）不透明' % (base.shape[1], base.shape[0]), int((base[..., 3] != 255).sum()))
    hard = 0
    for L in list(layers) + list(fg):
        ims = [L['img']] if L['t'] in ('static', 'pano') else (L['images'] if L['t'] == 'pick' else [])
        for im in ims:
            a = np.array(im)[..., 3]
            hard += int(((a > 0) & (a < 255)).sum())
    ex.checked('static / pano / pick 图层都只有 0 / 255 两种透明度（硬边像素）', hard)
    # strip：闭合 / 帧条宽 / 每帧在动 / 只有 0 / 255 透明度 / 画的东西都在框里
    strips = [L for L in list(layers) + list(fg) if L['t'] == 'strip']
    for L in strips:
        name, box, n, fps, fn = L['name'], L['box'], L['n'], L['fps'], L['fn']
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
        h2 = sum(int(((np.array(f)[..., 3] > 0) & (np.array(f)[..., 3] < 255)).sum()) for f in fr)
        ex.checked('strip %s 只有 0 / 255 透明度' % name, h2)
    fns = {}
    for L in strips:
        fns.setdefault(L['fn'], []).append(L)
    for fn, items in fns.items():
        lost = 0
        n, fps = items[0]['n'], items[0]['fps']
        for i in range(n):
            m = np.array(fn(i / fps))[..., 3] > 0
            for L in items:
                b = L['box']
                m[max(0, b[1]):b[3], max(0, b[0]):b[2]] = False
            lost += int(m.sum())
        ex.checked('strip %s 每帧画的东西都在框里（框外的像素）' % '+'.join(L['name'] for L in items), lost)
    # 锚点：素材总表要求的名字一个不少；都在地图里；站人的点在可走带里
    anc = st['anchors']
    miss = [k for k in cfg['required'] if k not in anc]
    ex.checked('素材总表要求的锚点一个不少（缺：%s）' % (','.join(miss) or '无'), len(miss))
    out = [k for k, v in anc.items() if check_anchor_tree(v, PW, H)]
    wk = cfg['walk']
    for k in cfg.get('stand', ()):
        v = anc.get(k)
        if v is None or not (wk[0] <= v[1] <= wk[1] and 0 <= v[0] <= PW):
            out.append(k + '(站点)')
    ex.checked('锚点都在地图里、站人的点在可走带里（不满足：%s）' % (','.join(out) or '无'), len(out))
    # 可走带平整：和该行中位亮度差太多的像素占比（flat_skip 里的框不算）
    lumb = lum(base[..., :3].astype(np.float32))
    if cfg.get('flat'):
        x0, x1, fy0, fy1, tol, frac = cfg['flat']
        m = np.zeros(lumb.shape, bool)
        m[fy0:fy1, x0:x1] = True
        for (sx0, sy0, sx1, sy1) in cfg.get('flat_skip', ()):
            m[sy0:sy1, sx0:sx1] = False
        n_bad, tot = 0, int(m.sum())
        for y in range(fy0, fy1):
            row = lumb[y][m[y]]
            if row.size:
                n_bad += int((np.abs(row - np.median(row)) > tol).sum())
        ex.checked('可走带 y %d–%d 只有平整地面（和行中位亮度差 > %d 的像素 %.2f %% ≤ %.1f %%，排除 %d 个框）' %
                   (fy0, fy1 - 1, tol, 100.0 * n_bad / max(1, tot), frac * 100, len(cfg.get('flat_skip', ()))),
                   0 if n_bad <= frac * tot else n_bad)
    # 导出 vs 直接拼
    ex_states = cfg.get('export_states') or states
    for camX in sorted(set([0, PW // 2 - W // 2, PW - W] if PW > W else [0])):
        for tt in (0.0, 1.25, 9.0):
            for s in ex_states:
                got = BJ.ref_render(st, imgs, camX, tt, s)
                want = compose(layers, fg, camX, tt, s)
                tag = ','.join('%s=%s' % (k, v) for k, v in sorted(s.items())) or '默认'
                ex.checked('%s camX=%d t=%.2f [%s] 导出 vs 直接拼' % (title, camX, tt, tag), BJ.ndiff(got, want))
    # 体积
    tot = 0
    for k, im in imgs.items():
        if k.startswith('bg/%s/' % ex.key):
            tot += png_bytes(im)
    lim = cfg.get('size_limit', 250 * 1024)
    ex.checked('PNG 合计 %.1f KB ≤ %d KB' % (tot / 1024.0, lim // 1024), 0 if tot <= lim else int((tot - lim) // 1024) + 1)
    ex.note('亮度：可走带 y%d–%d 均值 %.0f 标准差 %.1f；后沿 y%d–%d 均值 %.0f 标准差 %.1f' %
            (wk[0], wk[1], lumb[wk[0]:wk[1] + 1].mean(), lumb[wk[0]:wk[1] + 1].std(),
             wk[0] - 40, wk[0] - 1, lumb[wk[0] - 40:wk[0]].mean(), lumb[wk[0] - 40:wk[0]].std()))


# ============================================================ 走廊共用（mansion_corridor / illusion_corridor / mansion_hall 的家具）
# 走廊的竖向分层（世界 y，两张走廊图一样：幻觉走廊是“同一段走廊”，一眼要看得出来）：
#   0–8 天花、9–16 檐口、17–119 墙纸、120–123 腰线、124–143 护墙板、144–148 踢脚板、149–179 地板（地毯 153–177）
CORR = dict(ceil=(0, 8), cornice=9, wall=(17, 119), rail=120, wain=(124, 143), skirt=(144, 148), floor=149,
            rug=(153, 177), top=17)
STEEL = dict(hi=(198, 204, 218), lt=(152, 158, 176), md=(108, 114, 134), dk=(70, 74, 94), dd=(38, 40, 54))
CERAMIC = dict(hi=(236, 232, 222), md=(196, 200, 206), dk=(130, 136, 156), dd=(70, 76, 98))   # 青瓷花瓶（冷白）


def runner(cv, x0, x1, y0, y1, pal=CARPET, seed=0):
    """走廊的长条地毯（y0..y1）：和 carpet() 的区别是金边上的小方块只比金边暗一点点、绒毛更少——
    可走带上的对比压低（人站上去看得清），灯光也只照得出一层淡淡的菱形纹。"""
    a = np.array(cv.im).astype(np.float32)
    hh = y1 - y0 + 1
    for y in range(y0, y1 + 1):
        r, rb = y - y0, y1 - y
        for x in range(x0, x1 + 1):
            if r == 0 or rb == 0:
                c = pal['dd']
            elif r in (1, 2) or rb in (1, 2):
                outer = (r == 1 or rb == 1)
                c = pal['gold'] if outer else pal['gold_d']
                if (x + r + rb) % 6 == 0:                              # 金边上的小方块：只往另一档金偏 30 %（对比压低）
                    c = mix(c, pal['gold_d'] if outer else pal['gold'], 0.3)
            elif r == 3 or rb == 3:
                c = pal['dk']
            else:
                c = pal['base']
                uu = (x - x0) % 12 - 6
                vv = (r - 4) % max(4, (hh - 8)) - (hh - 8) / 2
                if abs(abs(uu) / 6.0 + abs(vv) / max(2.0, (hh - 8) / 2.0) - 1) < 0.09:
                    c = mix(pal['base'], pal['lt'], 0.38)
                elif abs(uu) <= 0 and abs(vv) <= 0.5:
                    c = mix(pal['base'], pal['gold'], 0.22)
            if hash01(seed, x, y) < 0.04 and 4 <= r <= hh - 5:         # 绒毛（只在毯心）
                c = mix(c, pal['dk'], 0.25)
            a[y, x, :3] = c
            a[y, x, 3] = 255
    cv.im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def corridor_shell(cv, x0, x1, paper=PAPER, wood=WOOD, rug=CARPET, seed=0, swap=False, ceil=(30, 24, 38), oy=0):
    """走廊的壳（x0..x1 含）：天花、檐口、墙纸、腰线、护墙板、踢脚板、木地板 + 长条地毯。
    先画墙纸、再画檐口（檐口下沿的影子压在已经画好的墙纸上）。"""
    d = cv.d
    c0, c1 = CORR['ceil']
    rect(d, x0, c0, x1, c1, ceil)
    for x in range(x0, x1 + 1, 64):                                    # 天花板的横梁（只看得到梁底的一道暗边）
        vl(d, x, c0, c1, dk(ceil, 0.7))
        vl(d, x + 1, c0, c1, lt(ceil, 0.06))
    hl(d, x0, x1, c1, dk(ceil, 0.8))
    wallpaper(cv, (x0, CORR['wall'][0], x1, CORR['wall'][1]), seed=seed, pal=paper, oy=oy, swap=swap)
    cornice(cv, x0, x1, CORR['cornice'], wood)
    dado_rail(cv, x0, x1, CORR['rail'], wood)
    wainscot(cv, x0, x1, CORR['wain'][0], CORR['wain'][1], wood, panel=28, gap=5, seed=seed)
    skirting(cv, x0, x1, CORR['skirt'][0], 5, wood)
    plank_floor(cv, x0, x1, CORR['floor'], cv.h - 1, wood, seed=seed)
    mul_box(cv.im, (x0, CORR['floor'], x1, CORR['floor'] + 2), (0.7, 0.7, 0.78))      # 墙脚的接触影
    runner(cv, x0, x1, CORR['rug'][0], CORR['rug'][1], rug, seed=seed)


def console_table(cv, x0, x1, yf=148, pal=WOOD, seed=0):
    """靠墙的条案（x0..x1，脚在 yf）：台面（厚 3 px、前沿一道亮）、牙板 + 两个抽屉（铜拉手）、两条弯腿 + 横档。
    返回台面上沿的 y（上面放东西）。"""
    d = cv.d
    top = yf - 26
    rect(d, x0 - 2, top, x1 + 2, top + 2, pal['lt'])
    hl(d, x0 - 2, x1 + 2, top, pal['hi'])
    hl(d, x0 - 2, x1 + 2, top + 2, pal['dd'])
    rect(d, x0, top + 3, x1, top + 9, pal['md'])                       # 牙板
    hl(d, x0, x1, top + 3, pal['dd'])
    hl(d, x0, x1, top + 9, pal['dk'])
    mid = (x0 + x1) // 2
    for (a_, b_) in ((x0 + 2, mid - 2), (mid + 2, x1 - 2)):            # 抽屉脸
        rect(d, a_, top + 4, b_, top + 8, pal['lt'], outline=pal['dk'])
        px(d, (a_ + b_) // 2, top + 6, GOLD['hi'])
        px(d, (a_ + b_) // 2 + 1, top + 6, GOLD['dk'])
    for (lx, s) in ((x0 + 1, 1), (x1 - 3, -1)):                        # 弯腿
        for k, yy in enumerate(range(top + 10, yf + 1)):
            off = int(round(1.4 * math.sin(k / 16.0 * math.pi)))
            rect(d, lx + off * s, yy, lx + off * s + 2, yy, pal['md'])
            px(d, lx + off * s, yy, pal['hi'])
            px(d, lx + off * s + 2, yy, pal['dd'])
    hl(d, x0 + 4, x1 - 4, yf - 8, pal['dk'])                           # 横档
    hl(d, x0 + 4, x1 - 4, yf - 9, pal['lt'])
    mul_box(cv.im, (x0 + 1, top + 10, x1 - 1, yf - 1), (0.74, 0.74, 0.82))             # 台下的暗（整块压暗，不抖：抖了像一张网）
    return top


def dead_flowers(cv, cx, y, seed=0):
    """青瓷花瓶（脚在 y）+ 一束枯死的玫瑰（花头垂着、暗红发黑，梗上有刺，掉了一片花瓣在台面上）。"""
    d = cv.d
    P = CERAMIC
    for k, (hw, yy) in enumerate(((3, y), (4, y - 1), (5, y - 2), (5, y - 3), (4, y - 4), (3, y - 5), (2, y - 6),
                                  (2, y - 7), (3, y - 8), (4, y - 9))):
        hl(d, cx - hw, cx + hw, yy, P['md'])
        px(d, cx - hw, yy, P['hi'])
        px(d, cx + hw, yy, P['dk'])
    hl(d, cx - 3, cx + 3, y - 10, P['dd'])
    for k in range(3):                                                 # 瓷上一圈青花纹
        px(d, cx - 2 + k * 2, y - 4, (86, 108, 172))
        px(d, cx - 1 + k * 2, y - 3, (86, 108, 172))
    heads = [(-6, -26, 0.9), (0, -29, 1.0), (6, -25, 0.8)]
    for i, (dx, dy, _) in enumerate(heads):
        x1_, y1_ = cx + dx, y + dy
        n = abs(dy) - 10
        for s in range(n + 1):
            u = s / max(1, n)
            xx = round(cx + (x1_ - cx) * u + (2 * (1 - u) * u * (-1 if dx > 0 else 1)))
            yy = round(y - 10 - (abs(dy) - 10) * u)
            px(d, xx, yy, (72, 76, 44))
            if s % 4 == 2:
                px(d, xx + 1, yy, (50, 54, 32))                        # 刺
        px(d, x1_, y1_ + 1, (28, 10, 16))                              # 垂着的枯花头
        rect(d, x1_ - 1, y1_ + 2, x1_ + 1, y1_ + 4, (84, 18, 30))
        px(d, x1_ - 1, y1_ + 2, (120, 30, 44))
        px(d, x1_ + 1, y1_ + 4, (30, 8, 14))
    px(d, cx + 7, y + 1, (84, 18, 30))                                 # 台面上掉的花瓣
    px(d, cx - 8, y + 1, (60, 12, 22))


def grandfather_clock(cv, cx, yf=148, h=70, pal=WOOD):
    """落地大摆钟（宽 18，脚在 yf）：尖顶冠 + 带表盘的钟头 + 玻璃门的钟身（摆在里面晃，strip）+ 基座。
    指针停在 12 点（馆里的时间是 DIO 的）。返回 dict(win=(x0, y0, x1, y1) 摆窗, pivot=(x, y) 摆的悬点, L=摆长)。"""
    d = cv.d
    x0, x1 = cx - 9, cx + 8
    top = yf - h
    # 基座
    rect(d, x0, yf - 12, x1, yf, pal['md'])
    hl(d, x0, x1, yf - 12, pal['hi'])
    rect(d, x0 + 3, yf - 9, x1 - 3, yf - 3, pal['lt'], outline=pal['dk'])
    hl(d, x0 - 1, x1 + 1, yf, pal['dd'])
    # 钟身
    bx0, bx1 = cx - 6, cx + 5
    rect(d, bx0, top + 24, bx1, yf - 13, pal['md'])
    vl(d, bx0, top + 24, yf - 13, pal['hi'])
    vl(d, bx1, top + 24, yf - 13, pal['dd'])
    wx0, wy0, wx1, wy1 = cx - 4, top + 28, cx + 3, yf - 17
    rect(d, wx0, wy0, wx1, wy1, (16, 12, 18), outline=pal['dd'])
    for k in range(5):                                                 # 玻璃上一道斜反光
        px(d, wx0 + 1 + k // 2, wy0 + 2 + k * 3, (58, 56, 74))
    # 钟头
    rect(d, x0, top + 6, x1, top + 23, pal['lt'])
    vl(d, x0, top + 6, top + 23, pal['hi'])
    vl(d, x1, top + 6, top + 23, pal['dk'])
    hl(d, x0 - 1, x1 + 1, top + 23, pal['dd'])
    hl(d, x0 - 1, x1 + 1, top + 24, pal['dd'])
    for i in range(-8, 9):                                             # 钟头顶上的弧
        yy = top + 6 - int(round(3 * math.cos(i / 8.0 * math.pi / 2)))
        vl(d, cx + i, yy, top + 6, pal['lt'] if i < 3 else pal['md'])
    vl(d, cx, top, top + 2, GOLD['lt'])                                # 顶上的小球
    px(d, cx, top - 1, GOLD['hi'])
    px(d, cx - 1, top + 1, GOLD['md'])
    px(d, cx + 1, top + 1, GOLD['dk'])
    # 表盘
    fcy = top + 14
    d.ellipse((cx - 6, fcy - 6, cx + 5, fcy + 5), fill=C((232, 224, 196)), outline=C(GOLD['dk']))
    for (ax, ay) in ((cx, fcy - 5), (cx + 5, fcy), (cx, fcy + 5), (cx - 5, fcy)):
        px(d, ax, ay, (40, 30, 30))
    vl(d, cx, fcy - 4, fcy, (30, 24, 28))                              # 分针 / 时针都指着 12
    vl(d, cx, fcy - 2, fcy, (30, 24, 28))
    px(d, cx, fcy, (150, 40, 40))
    return dict(win=(wx0, wy0, wx1, wy1), pivot=(cx, wy0 + 1), L=wy1 - wy0 - 5)


def pendulum_draw(d, clk, f, n=N8, col=None):
    """摆的第 f 帧（8 帧一周，对称地摆）：一根细杆 + 末端一个铜摆锤。"""
    col = col or GOLD
    ang = 0.30 * math.sin(math.tau * f / n)
    px0, py0 = clk['pivot']
    L = clk['L']
    bx, by = px0 + L * math.sin(ang), py0 + L * math.cos(ang)
    steps = int(L)
    for s in range(steps + 1):
        u = s / steps
        px(d, round(px0 + (bx - px0) * u), round(py0 + (by - py0) * u), col['md'])
    bx, by = int(round(bx)), int(round(by))
    rect(d, bx - 1, by - 1, bx + 1, by + 1, col['lt'])
    px(d, bx - 1, by - 1, col['hi'])
    px(d, bx + 1, by + 1, col['dk'])


def armor_stand(cv, cx, yf=148, with_halberd=True):
    """立在底座上的全身铠甲（宽约 18，高约 62，脚在 yf）：头盔（面甲缝 + 红缨）、护喉、双肩甲、胸甲（中脊亮）、
    双臂、裙甲、双腿；右手边立一杆长戟。钢的亮暗比墙纸大——烛光一照会闪。"""
    d = cv.d
    S = STEEL
    # 底座
    rect(d, cx - 9, yf - 4, cx + 9, yf, WOOD['md'])
    hl(d, cx - 9, cx + 9, yf - 4, WOOD['hi'])
    hl(d, cx - 9, cx + 9, yf, WOOD['dd'])
    # 腿
    for (a_, b_) in ((cx - 5, cx - 1), (cx + 1, cx + 5)):
        rect(d, a_, yf - 22, b_, yf - 5, S['md'])
        vl(d, a_, yf - 22, yf - 5, S['hi'])
        vl(d, b_, yf - 22, yf - 5, S['dk'])
        hl(d, a_ - 1, b_ + 1, yf - 6, S['lt'])                         # 脚甲
        hl(d, a_ - 1, b_ + 1, yf - 5, S['dd'])
        hl(d, a_, b_, yf - 14, S['dd'])                                # 膝甲的缝
        px(d, a_ + 1, yf - 15, S['hi'])
    # 裙甲
    for k in range(4):
        hw = 6 + k // 2
        hl(d, cx - hw, cx + hw, yf - 27 + k * 1, S['md'] if k % 2 == 0 else S['lt'])
    hl(d, cx - 7, cx + 7, yf - 23, S['dd'])
    # 胸甲
    for y in range(yf - 41, yf - 27):
        hw = 6 if y > yf - 37 else 7
        hl(d, cx - hw, cx + hw, y, S['md'])
        px(d, cx - hw, y, S['hi'])
        px(d, cx + hw, y, S['dk'])
        px(d, cx, y, S['hi'])                                          # 中脊
        px(d, cx - 1, y, S['lt'])
    hl(d, cx - 6, cx + 6, yf - 35, S['dk'])                            # 胸甲下的一道缝
    # 双臂
    for (a_, s) in ((cx - 10, -1), (cx + 9, 1)):
        rect(d, a_, yf - 37, a_ + 1, yf - 26, S['md'])
        px(d, a_, yf - 37, S['hi'])
        px(d, a_ + 1, yf - 26, S['dd'])
    # 肩甲（圆的）
    for (a_, b_) in ((cx - 10, cx - 6), (cx + 6, cx + 10)):
        rect(d, a_, yf - 43, b_, yf - 40, S['lt'])
        hl(d, a_, b_, yf - 43, S['hi'])
        hl(d, a_, b_, yf - 40, S['dk'])
    # 护喉 + 头盔
    rect(d, cx - 3, yf - 46, cx + 3, yf - 44, S['dk'])
    for y in range(yf - 57, yf - 46):
        hw = 4 if y > yf - 55 else 3
        hl(d, cx - hw, cx + hw, y, S['lt'])
        px(d, cx - hw, y, S['hi'])
        px(d, cx + hw, y, S['dk'])
    hl(d, cx - 3, cx + 3, yf - 52, S['dd'])                            # 面甲缝
    hl(d, cx - 3, cx + 3, yf - 51, (12, 8, 14))
    vl(d, cx, yf - 50, yf - 47, S['dd'])
    vl(d, cx, yf - 60, yf - 58, (150, 36, 44))                         # 红缨
    px(d, cx + 1, yf - 59, (112, 24, 34))
    px(d, cx - 1, yf - 58, (176, 54, 60))
    if with_halberd:
        hx = cx + 13
        vl(d, hx, yf - 66, yf - 1, WOOD['md'])
        vl(d, hx - 1, yf - 60, yf - 1, WOOD['hi'])
        for k in range(8):                                             # 斧刃
            hl(d, hx + 1, hx + 1 + (4 - abs(k - 3)), yf - 66 + k, S['lt'] if k % 2 else S['md'])
        vl(d, hx, yf - 70, yf - 67, S['hi'])
        px(d, hx, yf - 71, S['hi'])


def damp_stain(cv, x, y0, L, w=5, k=0.74, seed=0):
    """墙纸上从檐口往下洇开的一道水渍：偏暗偏蓝、边缘断断续续、越往下越淡（屋顶漏水的老房子）。"""
    a = np.array(cv.im).astype(np.float32)
    for y in range(y0, y0 + L):
        u = (y - y0) / float(L)
        hw = w * (0.55 + 0.6 * math.sin(math.pi * min(1.0, u * 1.4)) * 0.5 + 0.3 * u)
        for xx in range(int(x - hw - 1), int(x + hw + 2)):
            if not 0 <= xx < cv.w:
                continue
            e = 1 - abs(xx - x) / max(1.0, hw)
            if e <= 0:
                continue
            amt = (1 - k) * min(1.0, e * 1.6) * (1 - 0.75 * u)
            if hash01(seed, xx, y) < 0.9:
                a[y, xx, :3] *= (1 - amt, 1 - amt * 0.9, 1 - amt * 0.55)
    cv.im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def round_mirror(cv, cx, cy, r=9):
    """凸面镜（金圈 + 暗蓝的镜面，左上一道亮弧、右下映着一点烛光），顶上一片卷叶。"""
    d = cv.d
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C(GOLD['md']), outline=C(INK))
    ri = r - 2
    d.ellipse((cx - ri, cy - ri, cx + ri, cy + ri), fill=C((34, 40, 62)), outline=C(GOLD['dd']))
    for k in range(0, 360, 6):                                         # 金圈：左上亮、右下暗
        a = math.radians(k)
        x, y = round(cx + (r - 1) * math.cos(a)), round(cy - (r - 1) * math.sin(a))
        px(d, x, y, GOLD['hi'] if 20 < k < 200 else GOLD['dk'])
    for k in range(110, 190, 6):                                       # 镜面左上的亮弧
        a = math.radians(k)
        px(d, round(cx + (ri - 2) * math.cos(a)), round(cy - (ri - 2) * math.sin(a)), (118, 128, 164))
    px(d, cx + ri // 2, cy + ri // 2, (230, 170, 90))                  # 映着的烛光
    px(d, cx + ri // 2 + 1, cy + ri // 2, (150, 100, 60))
    px(d, cx, cy - r - 1, GOLD['lt'])                                  # 顶上的卷叶
    px(d, cx - 1, cy - r - 2, GOLD['hi'])
    px(d, cx + 1, cy - r - 2, GOLD['md'])
    px(d, cx, cy - r - 2, GOLD['md'])


def coat_of_arms(cv, cx, y0):
    """墙上的家徽：交叉的两把长剑 + 盾（红 / 靛蓝四分、一道金杠）+ 盾上的小冠。总高约 24。"""
    d = cv.d
    S = STEEL
    for (ax, ay, bx, by) in ((cx - 15, y0 + 3, cx + 15, y0 + 23), (cx + 15, y0 + 3, cx - 15, y0 + 23)):
        n = max(abs(bx - ax), abs(by - ay))
        for s in range(n + 1):
            u = s / n
            x, y = round(ax + (bx - ax) * u), round(ay + (by - ay) * u)
            px(d, x, y, S['lt'] if s % 3 else S['hi'])
            px(d, x, y + 1, S['dk'])
        px(d, ax, ay, GOLD['hi'])                                      # 剑柄末端的球
        px(d, ax, ay - 1, GOLD['md'])
    shield = [(cx - 8, y0 + 4), (cx + 8, y0 + 4), (cx + 8, y0 + 14), (cx, y0 + 23), (cx - 8, y0 + 14)]
    ImageDraw.Draw(cv.im).polygon(shield, fill=C(GOLD['md']), outline=C(INK))
    inner = [(cx - 6, y0 + 6), (cx + 6, y0 + 6), (cx + 6, y0 + 14), (cx, y0 + 20), (cx - 6, y0 + 14)]
    ImageDraw.Draw(cv.im).polygon(inner, fill=C((120, 24, 36)))
    for y in range(y0 + 6, y0 + 21):                                   # 右半涂靛蓝
        for x in range(cx + 1, cx + 7):
            if cv.im.getpixel((x, y))[:3] == (120, 24, 36):
                px(d, x, y, (40, 44, 92))
    hl(d, cx - 6, cx + 6, y0 + 11, GOLD['lt'])                          # 一道金杠
    vl(d, cx, y0 + 6, y0 + 20, GOLD['lt'])
    px(d, cx - 6, y0 + 6, GOLD['hi'])
    hl(d, cx - 3, cx + 3, y0 + 2, GOLD['lt'])                           # 小冠
    for dx in (-3, 0, 3):
        vl(d, cx + dx, y0 - 1, y0 + 1, GOLD['hi'] if dx == 0 else GOLD['md'])
