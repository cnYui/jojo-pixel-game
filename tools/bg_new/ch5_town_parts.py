# -*- coding: utf-8 -*-
r"""ch5_town_parts —— 第5章 ch5-town 组（fog_town / enya_inn / karachi_street）共用零件（2026-10-18 第二轮背景重画）。

不是背景 key（文件名不和任何 key 重名，tools\bg_jojo.py 不会把它当背景导出）；三个 key 模块在加载时按路径引用它
（同 ganges_ghat.py 引用 varanasi_street.py 的写法：importlib 按路径加载，不改 sys.path 顺序）。

里面放：
  · 小工具：dk / lt / hl / vl / px / rect / mul_box / cast_shadow / mottle / haze / opaque …直接用 varanasi_street 的，
    窗 / 檐口 / 铁阳台 / 木阳台 / 招牌 / 铁皮雨棚 / 铺子里压暗用 calcutta_street 的——和第4章同一套线条、明暗习惯
    （光从左上来：左沿亮、右沿暗、影子往右下）
  · fog_band：横向首尾相接的雾带（噪声 × 纵向轮廓，透明度分几档 + Bayer 抖动，像素风，不是软糊糊的渐变）
  · add_light：椭圆衰减、分档 + 抖动的灯光，直接烘进底图（bg_jojo.ref_render 不认识 glow 图层，用了预览会报错）
  · ink：单独一层画好的物件外面描 1 px 深色线（第4章近景的墨线）
  · 点阵字（HOTEL / WC / P）与 urdu_line（像乌尔都文 Nastaliq 的笔画：从右往左、一个词往左下斜、点、竖笔、尾巴；读不出字）
  · 场景框架：图层表（static / wrap / pano / strip / clouds / tint / pick）→ compose（直接拼一帧，照 §3.6 公式）、
    export（ex.img / ex.bake → stage dict），以及通用自检（露黑、透明度、strip 闭合 / 每帧在动 / 框外、wrap 闭合、
    锚点、可走带平整、导出 vs 直接拼）。图层表只写一次，导出和直接拼走同一张表，参数不会两边写岔。
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

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402,F401
from engine import bg_asia as A  # noqa: E402


def _load(name):
    """第4章的模块按 bg_jojo.bg_new 同一个模块名加载（同一进程里被别的背景用到时直接复用，不重复执行）。"""
    key = 'bg_new_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


V = _load('varanasi_street')
K = _load('calcutta_street')

W, H = 320, 180
C = A._c4
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, cast_shadow = V.mul_box, V.mul_mask, V.poly_mask, V.cast_shadow
mottle, haze, opaque, wire, garland_pts = V.mottle, V.haze, V.opaque, V.wire, V.garland_pts
SHADOW_MUL, SOFT_MUL = V.SHADOW_MUL, V.SOFT_MUL


def layer_w(pw, k):
    """视差 k 的全景层要多宽：镜头走到最右（camX = pw − 320）时这一层也刚好铺满屏幕。"""
    return W + int(math.ceil((pw - W) * k))


def frame_of(t, fps, n):
    """strip 帧号（同 engine/bg.js：floor(t·fps + 1e-6) mod n）。帧函数只认帧号，t = i/fps 时取第 i 帧。"""
    return int(math.floor(t * fps + 1e-6)) % n


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


# ============================================================ 雾
def fog_band(w, h, seed, amax, prof=None, center=None, half=None, cell=32, stretch=4,
             levels=(0, 30, 58, 86, 116, 146), col=(150, 162, 166), lo=0.3, span=0.5):
    """横向首尾相接（w 宽一圈）的雾带：横着拉长的 fbm 噪声 × 纵向轮廓 prof（h 长的数组；不给就用 center / half 的钟形），
    透明度量化成 levels 几档，档和档之间用 Bayer 抖动过渡（像素风）。返回 RGBA（颜色恒为 col，只有透明度在变）。"""
    n = A._fbm_wrap(w, h * stretch, cell, seed=seed, octaves=3)[::stretch][:h]
    if prof is None:
        yy = np.arange(h, dtype=np.float32)
        prof = np.clip(1 - ((yy - center) / half) ** 2, 0, 1)
    prof = np.asarray(prof, np.float32).reshape(h, 1)
    a = np.clip((n - lo) / span, 0, 1) * prof * amax
    lv = np.array(levels, np.float32)
    idx = np.clip(np.searchsorted(lv, a) - 1, 0, len(lv) - 2)
    lo_, hi_ = lv[idx], lv[idx + 1]
    frac = (a - lo_) / np.maximum(1, hi_ - lo_)
    bay = A._bayer(w, h)
    out_a = np.where(frac > bay, hi_, lo_)
    out_a[a <= 1] = 0
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., :3] = col
    arr[..., 3] = np.clip(out_a, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def ramp(h, pts):
    """纵向轮廓：pts = [(y, 值), …]，线性插值成 h 长的数组（雾的浓淡按高度走）。"""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return np.interp(np.arange(h, dtype=np.float32), xs, ys).astype(np.float32)


def fog_wash(im, amt, col, mask=None):
    """把不透明像素往雾色混 amt（标量 / H×1 / H×W 数组）；mask 为 True 的像素不混（亮着的窗、灯）。原地改。"""
    a = np.array(im).astype(np.float32)
    m = a[..., 3] > 0
    if mask is not None:
        m &= ~mask
    amt = np.asarray(amt, np.float32)
    if amt.ndim == 0:
        amt = np.full((a.shape[0], 1), float(amt), np.float32)
    if amt.ndim == 2 and amt.shape[1] == 1:
        amt = np.broadcast_to(amt, a.shape[:2])
    hz = np.array(col, np.float32)
    a[..., :3] = np.where(m[..., None], a[..., :3] * (1 - amt[..., None]) + hz * amt[..., None], a[..., :3])
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


# ============================================================ 灯光（烘进底图）
def add_light(im, cx, cy, rx, ry, col, amt, steps=4, box=None, mask=None, power=1.4, mode='mul'):
    """椭圆衰减的灯光：f = (1 − r)^power 分成 steps 档，档和档之间 Bayer 抖动；
    mode 'mul'：像素 × (1 + amt·f·col/255)（暗面被照亮、保留材质）；'mix'：往 col 混 amt·f（雾里的光晕）。
    box 限制范围（右下含），mask（H×W bool）只照这些像素。原地改。"""
    x0 = int(max(0, math.floor(cx - rx)))
    x1 = int(min(im.width - 1, math.ceil(cx + rx)))
    y0 = int(max(0, math.floor(cy - ry)))
    y1 = int(min(im.height - 1, math.ceil(cy + ry)))
    if box is not None:
        x0, y0 = max(x0, box[0]), max(y0, box[1])
        x1, y1 = min(x1, box[2]), min(y1, box[3])
    if x1 < x0 or y1 < y0:
        return
    a = np.array(im.crop((x0, y0, x1 + 1, y1 + 1))).astype(np.float32)
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1].astype(np.float32)
    r = np.sqrt(((xs + 0.5 - cx) / max(0.5, rx)) ** 2 + ((ys + 0.5 - cy) / max(0.5, ry)) ** 2)
    f = np.clip(1 - r, 0, 1) ** power
    q = f * steps
    base = np.floor(q)
    bay = A._bayer(im.width, im.height)[y0:y1 + 1, x0:x1 + 1]
    lv = (base + ((q - base) > bay)) / steps
    m = a[..., 3] > 0
    if mask is not None:
        m &= mask[y0:y1 + 1, x0:x1 + 1]
    lv = np.where(m, lv, 0)[..., None]
    c = np.array(col, np.float32)
    if mode == 'mul':
        a[..., :3] = a[..., :3] * (1 + amt * lv * c / 255.0)
    else:
        a[..., :3] = a[..., :3] * (1 - amt * lv) + c * amt * lv
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'), (x0, y0))


def halo_dots(d, cx, cy, r, col, seed, density=0.5, ring=(0.35, 1.0)):
    """雾里一圈零散的亮点（光晕的“颗粒”）：在 r 圈里按距离越远越稀地点几个像素。"""
    n = int(r * r * density)
    for i in range(n):
        ang = hrange(0, math.tau, seed, i, 1)
        u = hrange(ring[0], ring[1], seed, i, 2) ** 0.7
        if hash01(seed, i, 3) > 1.05 - u:
            continue
        px(d, round(cx + math.cos(ang) * r * u), round(cy + math.sin(ang) * r * u * 0.8), col)


# ============================================================ 墨线
def ink(lay, col=(34, 34, 40), sides='all', inner=False):
    """lay（透明底、只画了一个 / 几个物件）外面描一圈 1 px 线（4 邻接）。sides：'all' 一圈 / 'br' 只描下沿和右沿
    （受光的左上不描，读起来更立体）。inner=True 改成描在物件最外一圈像素上（不变大）。原地改，返回 lay。"""
    a = np.array(lay)
    m = a[..., 3] > 0
    up = np.zeros_like(m)
    up[1:] = m[:-1]
    dn = np.zeros_like(m)
    dn[:-1] = m[1:]
    lf = np.zeros_like(m)
    lf[:, 1:] = m[:, :-1]
    rt = np.zeros_like(m)
    rt[:, :-1] = m[:, 1:]
    if inner:
        if sides == 'all':
            e = m & ~(up & dn & lf & rt)
        else:
            e = m & ~(dn & rt)
    else:
        if sides == 'all':
            e = ~m & (up | dn | lf | rt)
        else:
            e = ~m & (up | lf)                         # 物件的下面一行 / 右边一列
    a[e, :3] = col
    a[e, 3] = 255
    lay.paste(Image.fromarray(a, 'RGBA'))
    return lay


def ground_shadow(im, x0, x1, y, depth=3, slant=3, mul=None):
    """立在地上的东西往右下的一小片影子（压在地面最上面几行）。"""
    cast_shadow(im, [(x0 + 1, y), (x1, y), (x1 + slant, y + depth), (x0 + 1 + slant, y + depth)], mul=mul or SOFT_MUL)


def compress_band(im, y0, y1, k, ref, ramp_rows=8):
    """可走带后面那一条压对比：y0..y1（含）的不透明像素往 ref 色收 (1 − k)，从 y0 起 ramp_rows 行渐变。原地改。"""
    a = np.array(im).astype(np.float32)
    mid = np.array(ref, np.float32)
    for y in range(max(0, y0), min(im.height - 1, y1) + 1):
        kk = 1.0 - (1.0 - k) * min(1.0, (y - y0 + 1) / max(1, ramp_rows))
        m = a[y, :, 3] > 0
        a[y, m, :3] = mid + (a[y, m, :3] - mid) * kk
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


# ============================================================ 字（只画图形，读不出完整的字也没关系）
FONT5 = {   # 5×7
    'H': ('10001', '10001', '10001', '11111', '10001', '10001', '10001'),
    'O': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    'T': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'E': ('11111', '10000', '10000', '11110', '10000', '10000', '11111'),
    'L': ('10000', '10000', '10000', '10000', '10000', '10000', '11111'),
    'P': ('11110', '10001', '10001', '11110', '10000', '10000', '10000'),
}
FONT3 = {   # 小牌子用（3–5 宽 × 5 高）
    'W': ('10001', '10001', '10101', '11011', '10001'),
    'C': ('0110', '1000', '1000', '1000', '0110'),
    'P': ('110', '101', '110', '100', '100'),
    '0': ('111', '101', '101', '101', '111'),
    '1': ('010', '110', '010', '010', '111'),
    '2': ('110', '001', '010', '100', '111'),
    '3': ('110', '001', '010', '001', '110'),
    '4': ('101', '101', '111', '001', '001'),
    '5': ('111', '100', '110', '001', '110'),
    '6': ('011', '100', '110', '101', '010'),
    '7': ('111', '001', '010', '010', '010'),
    '8': ('010', '101', '010', '101', '010'),
    '9': ('010', '101', '011', '001', '110'),
}


def text_px(d, x, y, s, col, font=FONT5, gap=1, shadow=None):
    """点阵字：逐个字母画（shadow = 往右下错 1 的影子色）。返回写完的 x。"""
    for ch in s:
        g = font.get(ch)
        if g is None:
            x += 3
            continue
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == '1':
                    if shadow:
                        px(d, x + c + 1, y + r + 1, shadow)
                    px(d, x + c, y + r, col)
        x += len(g[0]) + gap
    return x


def urdu_line(d, x_right, x_left, y_base, col, seed, h=5, dots=True, dot_col=None):
    """从右往左写一行“像乌尔都文（Nastaliq）”的笔画（读不出字）：每个词从右上开始往左下斜着落到基线（Nastaliq 的阶梯），
    中间插几根竖笔（alif / lam），词尾有时一条往右回扫的长尾（ے）或一个小碗（ں），上下点几个点（nuqta）。
    h = 字高（竖笔从基线往上多高）；y_base = 基线。"""
    dc = dot_col or col
    x = x_right
    k = 0
    while x > x_left + 3:
        wl = int(hrange(4, 10, seed, k, 1))
        wl = min(wl, x - x_left - 1)
        if wl < 3:
            break
        drop = min(h - 2, max(1, wl // 3))
        pts = []
        for i in range(wl):                                       # 往左下斜的一笔：每 3 px 落一行
            yy = y_base - drop + min(drop, i // 3)
            pts.append((x - i, yy))
            px(d, x - i, yy, col)
        for i in range(1, wl - 1):                                 # 竖笔（alif / lam / kaf 的斜杠）
            if hash01(seed, k, i, 2) < 0.16:
                xx, yy = pts[i]
                L = int(hrange(2, h, seed, k, i, 3))
                lean = 1 if hash01(seed, k, i, 4) < 0.3 else 0
                for j in range(1, L + 1):
                    px(d, xx + (j // 3) * lean, yy - j, col)
        xe, ye = pts[-1]
        r = hash01(seed, k, 5)
        if r < 0.28:                                               # ے：往左下一点再往右回扫的长尾
            px(d, xe - 1, ye + 1, col)
            for j in range(min(wl + 2, 8)):
                px(d, xe + j, ye + 2, col)
        elif r < 0.48:                                             # ں：小碗
            px(d, xe - 1, ye, col)
            px(d, xe - 1, ye + 1, col)
            hl(d, xe, xe + 2, ye + 2, col)
            px(d, xe + 3, ye + 1, col)
        elif r < 0.6:                                              # ه / م：一个小圈
            rect(d, xe - 2, ye - 1, xe - 1, ye, col)
        if dots:
            for j in range(int(hrange(0, 3.2, seed, k, 6))):
                dx = int(hrange(1, wl - 1, seed, k, j, 7))
                above = hash01(seed, k, j, 8) < 0.65
                xx, yy = pts[min(dx, len(pts) - 1)]
                yd = yy - h + int(hrange(0, 2, seed, k, j, 9)) if above else yy + 2
                px(d, xx, yd, dc)
                if hash01(seed, k, j, 10) < 0.3:
                    px(d, xx - 2, yd, dc)
        x -= wl + int(hrange(2, 4, seed, k, 11))
        k += 1


# ============================================================ 场景框架：图层表 → 直接拼 / 导出
def tile_wrap(img, period, minw):
    """同 bg_jojo.tile_to：周期 period 的图横向重复到宽 ≥ minw 且是 period 的整数倍。"""
    n = max(1, -(-minw // period))
    out = A._new(period * n, img.height)
    for i in range(n):
        out.paste(img.crop((0, 0, period, img.height)), (i * period, 0))
    return out


def _crop_rows(img, y):
    bb = img.getchannel('A').getbbox()
    if not bb:
        return img, y
    return img.crop((0, bb[1], img.width, bb[3])), y + bb[1]


def L_static(name, img, x=0, y=0, key=None):
    return dict(t='static', name=name, img=img, x=x, y=y, key=key)


def L_wrap(name, img, period, k, y, vx, key=None):
    """img 至少 period 宽（只取前 period 列当一圈）；导出时铺到 ≥ period + 320，JS 一次贴完。"""
    return dict(t='wrap', name=name, img=tile_wrap(img, period, period + W), period=period, k=k, y=y, vx=vx, key=key)


def L_pano(name, img, k, x=0, y=0, key=None, crop=True):
    if crop:
        img, y = _crop_rows(img, y)
    return dict(t='pano', name=name, img=img, k=k, x=x, y=y, key=key)


def L_strip(name, box, n, fps, fn, k=1.0, key=None, screen=False):
    """fn(t) → 这一层坐标系里的整张 RGBA（世界层宽 / 屏幕 320），导出时裁 box、烘 n 帧。"""
    return dict(t='strip', name=name, box=tuple(int(v) for v in box), n=n, fps=fps, fn=fn, k=k, key=key, screen=screen)


def L_clouds(name, items, span):
    """items = [(图, x0, y, vx, k)]：同 bg.js clouds（x = (x0 + t·vx − camX·k) mod span − 100）。"""
    return dict(t='clouds', name=name, items=items, span=span, key=None)


def L_tint(color, alpha, key=None):
    return dict(t='tint', color=color, alpha=alpha, key=key)


def L_pick(name, key, values, images, x, y, k):
    return dict(t='pick', name=name, key=key, values=list(values), images=images, x=x, y=y, k=k)


def _hexrgb(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def compose(layers, fg, camX, t=0.5, state=None, with_fg=True):
    """直接拼一帧（不经导出）：照 bg_jojo.ref_render 的公式和取整，自检“导出 vs 直接拼”用。"""
    st = state or {}
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for L in layers + (fg if with_fg else []):
        typ = L['t']
        if L.get('key') and typ != 'pick' and not st.get(L['key']):
            continue
        if typ == 'static':
            paste(out, L['img'], L['x'], L['y'])
        elif typ == 'wrap':
            im, P = L['img'], L['period']
            o = int(math.floor(camX * L['k'] + t * L['vx'])) % P
            paste(out, im.crop((o, 0, o + W, im.height)), 0, L['y'])
        elif typ == 'pano':
            paste(out, L['img'], L['x'] - math.floor(camX * L['k']), L['y'])
        elif typ == 'strip':
            b = L['box']
            x = b[0] if L['screen'] else b[0] - math.floor(camX * L['k'])
            paste(out, L['fn'](t).crop(b), x, b[1])
        elif typ == 'clouds':
            for (im, x0, y, vx, k) in L['items']:
                x = (x0 + t * vx - camX * k) % L['span'] - 100
                paste(out, im, math.floor(x), y)
        elif typ == 'tint':
            out.alpha_composite(Image.new('RGBA', (W, H), _hexrgb(L['color']) + (int(255 * L['alpha']),)))
        elif typ == 'pick':
            v = st.get(L['key'], 0) or 0
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
        elif typ == 'wrap':
            d = dict(type='wrap', image=ex.img(L['name'], L['img']), period=L['period'], k=L['k'], y=L['y'], vx=L['vx'])
        elif typ == 'pano':
            d = dict(type='pano', image=ex.img(L['name'], L['img']), k=L['k'], x=L['x'], y=L['y'])
        elif typ == 'strip':
            d = ex.bake(L['name'], L['box'], L['n'], L['fps'], L['fn'], screen=L['screen'],
                        k=None if L['screen'] else L['k'])
        elif typ == 'clouds':
            d = dict(type='clouds', span=L['span'],
                     clouds=[dict(image=ex.img('%s%d' % (L['name'], i), im), x0=float(x0), y=y, vx=vx, k=k)
                             for i, (im, x0, y, vx, k) in enumerate(L['items'])])
        elif typ == 'tint':
            d = dict(type='tint', color=L['color'], alpha=L['alpha'])
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


def keys_of(layers, fg):
    return sorted({L['key'] for L in layers + fg if L.get('key')})


def strips_of(layers, fg):
    return [L for L in layers + fg if L['t'] == 'strip']


# ============================================================ 通用自检
def check_no_black(ex, BJ, st, pw, label, states, times=(0.0, 0.75, 1.5, 7.0), step=40):
    bad = 0
    cams = sorted(set(list(range(0, max(1, pw - W + 1), step)) + [max(0, pw - W)]))
    for state in states:
        for camX in cams:
            for t in times:
                im = np.array(BJ.ref_render(st, ex.images, camX, t, state).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('%s 镜头 0–%d（每 %d）× %d 个时刻 × %d 种状态 整屏都有画（没有露黑）' %
               (label, cams[-1], step, len(times), len(states)), bad)


def check_alpha01(ex, img, label):
    a = np.array(img)[..., 3]
    ex.checked('%s 只有 0 / 255 两种透明度' % label, int(((a > 0) & (a < 255)).sum()))


def check_opaque(ex, img, box, label):
    x0, y0, x1, y1 = box
    a = np.array(img)[y0:y1, x0:x1, 3]
    ex.checked('%s（x %d–%d，y %d–%d）整片不透明' % (label, x0, x1 - 1, y0, y1 - 1), int((a != 255).sum()))


def check_strips(ex, BJ, strips):
    for L in strips:
        name, box, n, fps, fn = L['name'], L['box'], L['n'], L['fps'], L['fn']
        T = n / fps
        ex.checked('strip %s %.2f s 闭合（t=0 vs t=%.2f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
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
                m[b[1]:b[3], b[0]:b[2]] = False
            lost += int(m.sum())
        ex.checked('strip %s 每帧画的东西都在框里（框外的像素）' % '+'.join(L['name'] for L in items), lost)


def check_wraps(ex, BJ, st):
    for L in [L for L in st['layers'] + st['fg'] if L['type'] == 'wrap']:
        T = L['period'] / abs(L['vx'])
        t0 = 0.5 / abs(L['vx'])                     # t·vx 落在两个整数正中间，浮点误差不会跨格
        one = dict(st, layers=[L], fg=[])
        s = {L['key']: True} if L.get('key') else {}
        g0 = BJ.ref_render(one, ex.images, 0, t0, s)
        g1 = BJ.ref_render(one, ex.images, 0, t0 + T, s)
        ex.checked('wrap %s 一圈 %.1f s 闭合' % (L['image'].split('/')[-1], T), BJ.ndiff(g0, g1))


def check_anchors(ex, anchors, pw, walk, stand, walk_x=None):
    """所有点 / 框都在地图里；stand 里的锚点（人站的点）y 在可走带里、x 在 walk_x 里。"""
    out = 0
    wx = walk_x or [0, pw]
    num = lambda q: isinstance(q, (int, float)) and not isinstance(q, bool)  # noqa: E731

    def visit(name, v):
        nonlocal out
        if isinstance(v, dict):
            for k2, v2 in v.items():
                visit(name + '.' + k2, v2)
        elif isinstance(v, (list, tuple)):
            if len(v) == 2 and all(num(q) for q in v):
                out += not (0 <= v[0] <= pw and 0 <= v[1] <= H)
            elif len(v) == 4 and all(num(q) for q in v):
                out += not (0 <= v[0] < v[2] <= pw and 0 <= v[1] < v[3] <= H)
            elif all(isinstance(q, (list, tuple)) for q in v):
                for i, q in enumerate(v):
                    visit('%s[%d]' % (name, i), q)
    for k, v in anchors.items():
        if k == 'walk_x':                                          # 范围 [x0, x1]，不是点
            out += not (0 <= v[0] < v[1] <= pw)
            continue
        visit(k, v)
    for k in stand:
        v = anchors[k]
        out += not (walk[0] <= v[1] <= walk[1] and wx[0] <= v[0] <= wx[1])
    return out


def check_walk_flat(ex, near, walk, label, thr=34, limit_frac=0.01, skip=()):
    """可走带（near 层 walk[0]..walk[1] 行）只是平整的地面：和每一行的中位亮度差 > thr 的像素占比 ≤ limit_frac
    （skip = 要排除的框，如排水沟、停车线这种画在地上的平东西）；顺带记一下亮度标准差。"""
    a = np.array(near)[..., :3].astype(np.float32)
    L = lum(a)
    m = np.zeros(L.shape, bool)
    y0, y1 = walk[0], min(H, walk[1] + 1)
    m[y0:y1] = True
    for (x0, yy0, x1, yy1) in skip:
        m[yy0:yy1, x0:x1] = False
    dev = 0
    tot = int(m.sum())
    for y in range(y0, y1):
        row = L[y][m[y]]
        if row.size == 0:
            continue
        med = np.median(row)
        dev += int((np.abs(row - med) > thr).sum())
    frac = dev / max(1, tot)
    ex.checked('%s 可走带 y %d–%d 只有平整的地面（离行中位亮度 > %d 的像素 %.2f%% ≤ %.1f%%）' %
               (label, walk[0], walk[1], thr, frac * 100, limit_frac * 100), 0 if frac <= limit_frac else dev)
    sel = L[m]
    return float(sel.mean()), float(sel.std())


def check_export_vs_compose(ex, BJ, st, layers, fg, label, cams, times, states):
    for state in states:
        for camX in cams:
            for t in times:
                got = BJ.ref_render(st, ex.images, camX, t, state)
                want = compose(layers, fg, camX, t, state)
                tag = ','.join(sorted(k for k, v in state.items() if v)) or '无'
                ex.checked('%s camX=%d t=%.2f 状态[%s] 导出 vs 直接拼' % (label, camX, t, tag), BJ.ndiff(got, want))
