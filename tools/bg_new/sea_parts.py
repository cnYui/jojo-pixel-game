# -*- coding: utf-8 -*-
r"""sea_parts —— 第7章「红海」四张背景（redsea_island / submarine / seabed_mouth / egypt_coast）共用的零件。
2026-10-18 第二轮背景重画（sea 组）新建。这个文件不是背景 key（名字不和任何 key 重名），四个 key 模块加载时按路径引用这里
（同 ganges_ghat.py 引用 varanasi_street.py 的写法：importlib 按路径加载、不改 sys.path 顺序）。

内容：
  · 小工具：直接用 varanasi_street.py 的 dk / lt / hl / vl / px / rect / mul_box / mul_mask / poly_mask / cast_shadow /
    mottle / haze / opaque / wire / _canopy（同一个模块实例 'bg_new_varanasi_street'，bg_jojo 的 bg_new() 也复用它），
    underwater.py 的 blob / shade（高度场打光的石头，红海的礁石 / 岩丘都用它）——两份都是已经验收的第2、4章零件，
    这里只引用不改。
  · 图层表（spec）：每个 key 先把图层写成一张表（static / wrap / pano / strip / pick / clouds / tint），
    再由 export_layers() 导出成 stage 的 layers / fg，direct() 按同一张表直接拼一帧（自检“导出 vs 直接拼”用），
    std_checks() 跑通用自检（不露黑、可走带不透明、近景只有 0 / 255、strip 闭合 / 每帧在动 / 不出框、wrap 闭合、
    锚点在地图 / 可走带里、导出 vs 直接拼）。
  · 海边的零件：天空、云、海面浪花带、太阳波光、海鸥、三角帆船（dhow）、浮标、椰枣树（树干 + 会摇的树冠）、
    礁石、沙面（白沙的风纹 / 贝壳 / 碎珊瑚）、灌木。
所有颜色都避开纯黑 (0,0,0)：自检用“RGB 全 0”判断露黑。
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

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _load(name):
    """按路径加载 tools\\bg_new\\<name>.py（模块名和 bg_jojo.bg_new() 一致，已经加载过就直接复用）。"""
    key = 'bg_new_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


V = _load('varanasi_street')
UW = _load('underwater')

W, H = 320, 180
C = A._c4
dk, lt, hl, vl, px, rect = V.dk, V.lt, V.hl, V.vl, V.px, V.rect
mul_box, mul_mask, poly_mask, cast_shadow = V.mul_box, V.mul_mask, V.poly_mask, V.cast_shadow
mottle, haze, opaque, wire, canopy = V.mottle, V.haze, V.opaque, V.wire, V._canopy
SHADOW_MUL, SOFT_MUL = V.SHADOW_MUL, V.SOFT_MUL
blob, shade, uw_comp = UW.blob, UW.shade, UW.comp
N_ANIM, FPS_ANIM = 8, 4.0                 # 默认 strip：8 帧 @4 fps = 2 s 一圈


def frame_no(t, n=N_ANIM, fps=FPS_ANIM):
    """strip 第几帧（和 JS 的 floor(t·fps + 1e-6) mod n 一致）。"""
    return int(math.floor(t * fps + 1e-6)) % n


def hexc(c):
    return '#%02x%02x%02x' % tuple(int(v) for v in c[:3])


def rgbh(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def tile_w(im, w):
    """横向重复到宽度 ≥ w（wrap 层直接拼时用）。"""
    out = A._new(w, im.height)
    for x in range(0, w, im.width):
        out.paste(im, (x, 0))
    return out


def outline(im, col, sides=('r', 'b'), only_on=None):
    """给透明底上的东西描 1 px 墨线（默认只描右 / 下两边：光从左上来，暗边落在右下）。返回新图。"""
    a = np.array(im)
    m = a[..., 3] > 0
    add = np.zeros_like(m)
    if 'r' in sides:
        add[:, 1:] |= m[:, :-1] & ~m[:, 1:]
    if 'b' in sides:
        add[1:, :] |= m[:-1, :] & ~m[1:, :]
    if 'l' in sides:
        add[:, :-1] |= m[:, 1:] & ~m[:, :-1]
    if 't' in sides:
        add[:-1, :] |= m[1:, :] & ~m[:-1, :]
    if only_on is not None:
        add &= only_on
    a[add, :3] = col
    a[add, 3] = 255
    return Image.fromarray(a, 'RGBA')


def auto_box(fn, n, fps, region, pad=0):
    """strip 的框按 n 帧实际画到的范围算（region 里），框不切掉东西、也不带一大片空白。"""
    x0, y0, x1, y1 = region
    acc = None
    for i in range(n):
        a = np.array(fn(i / fps))[y0:y1, x0:x1, 3] > 0
        acc = a if acc is None else (acc | a)
    ys, xs = np.nonzero(acc)
    if not len(xs):
        return (x0, y0, x0 + 1, y0 + 1)
    return (max(0, x0 + int(xs.min()) - pad), max(0, y0 + int(ys.min()) - pad),
            x0 + int(xs.max()) + 1 + pad, y0 + int(ys.max()) + 1 + pad)


# ============================================================ 图层表 → 导出 / 直接拼
def export_layers(ex, BJ, specs):
    """图层表 → (layers, fg)。static / pano / wrap 都先裁掉上下的空行（省字节）；wrap 横向铺到 ≥ period + 320。"""
    layers, fg = [], []
    for L in specs:
        t = L['t']
        if t == 'static':
            im, y = BJ.crop_rows(L['img'])
            d = dict(type='static', image=ex.img(L['name'], im), x=L.get('x', 0), y=L.get('y', 0) + y)
        elif t == 'wrap':
            im, y = BJ.crop_rows(L['img'])
            P = L['period']
            d = dict(type='wrap', image=ex.img(L['name'], BJ.tile_to(im, P, P + W)), period=P, k=L['k'],
                     y=L.get('y', 0) + y, vx=L.get('vx', 0.0))
        elif t == 'pano':
            im, y = BJ.crop_rows(L['img'])
            d = dict(type='pano', image=ex.img(L['name'], im), k=L['k'], x=L.get('x', 0), y=L.get('y', 0) + y)
        elif t == 'strip':
            scr = L.get('screen', False)
            d = ex.bake(L['name'], L['box'], L['n'], L['fps'], L['fn'], screen=scr, key=L.get('key'),
                        k=None if scr else L.get('k', 1.0))
        elif t == 'pick':
            ims = [ex.img('%s%d' % (L['name'], i), im) for i, im in enumerate(L['imgs'])]
            d = dict(type='pick', images=ims, key=L['key'], values=list(L['values']), x=L.get('x', 0),
                     y=L.get('y', 0), k=L.get('k', 1.0))
        elif t == 'clouds':
            items = [dict(image=ex.img('%s%d' % (L['name'], i), it['img']), x0=float(it['x0']), y=it['y'],
                          vx=it['vx'], k=it['k']) for i, it in enumerate(L['items'])]
            d = dict(type='clouds', span=L['span'], clouds=items)
        elif t == 'tint':
            d = dict(type='tint', color=L['color'], alpha=L['alpha'])
        else:
            raise ValueError(t)
        if L.get('key') and t not in ('strip', 'pick'):
            d['key'] = L['key']
        (fg if L.get('fg') else layers).append(d)
    return layers, fg


def _pick_index(L, v):
    v = 1.0 if v is True else (0.0 if not v else float(v))
    vals = L['values']
    return min(range(len(vals)), key=lambda j: abs(vals[j] - v))


def direct(specs, camX, t, state=None, fg=True):
    """不经导出，按图层表直接拼一帧（黑底）：公式同 engine/bg.js / bg_jojo.ref_render。"""
    st = state or {}
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for L in specs:
        if L.get('fg') and not fg:
            continue
        typ, key = L['t'], L.get('key')
        if key and typ != 'pick' and not st.get(key):
            continue
        if typ == 'static':
            paste(out, L['img'], L.get('x', 0), L.get('y', 0))
        elif typ == 'wrap':
            P = L['period']
            o = int(math.floor(camX * L['k'] + t * L.get('vx', 0.0))) % P
            big = tile_w(L['img'].crop((0, 0, P, L['img'].height)), P * 2 + W)
            paste(out, big.crop((o, 0, o + W, big.height)), 0, L.get('y', 0))
        elif typ == 'pano':
            paste(out, L['img'], L.get('x', 0) - math.floor(camX * L['k']), L.get('y', 0))
        elif typ == 'strip':
            n, fps = L['n'], L['fps']
            f = int(math.floor(t * fps)) % n
            fr = L['fn'](f / fps).crop(L['box'])
            x = L['box'][0] if L.get('screen') else L['box'][0] - math.floor(camX * L.get('k', 1.0))
            paste(out, fr, x, L['box'][1])
        elif typ == 'pick':
            im = L['imgs'][_pick_index(L, st.get(key, 0))]
            paste(out, im, L.get('x', 0) - math.floor(camX * L.get('k', 1.0)), L.get('y', 0))
        elif typ == 'clouds':
            for it in L['items']:
                x = (it['x0'] + t * it['vx'] - camX * it['k']) % L['span'] - 100
                paste(out, it['img'], math.floor(x), it['y'])
        elif typ == 'tint':
            lay = Image.new('RGBA', (W, H), rgbh(L['color']) + (int(255 * L['alpha']),))
            out.alpha_composite(lay)
    return out


def _lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def std_checks(ex, BJ, st, specs, cfg):
    """通用自检（照 ganges_ghat._checks）。cfg：
         name     图名（打印用）            pw / walk   地图宽 / 可走带
         states   要查的 state 组合（列表）  times       时刻
         opaque   [(说明, 图, (x0, y0, x1, y1))]：框里必须整片不透明
         binary   [(说明, 图)]：只能有 0 / 255 两种透明度
         stand    站人的锚点名（点或点列表：y 在可走带里、x 在 walk_x 里）
         inside   其余要查“在地图里”的锚点名
         clear    [(说明, 图, (x0, y0, x1, y1), 基准色, 容差)]：框里不能有大物件（和基准色差太多的像素数）
         notes    额外打印的话
    """
    imgs = ex.images
    pw, walk = cfg['pw'], cfg['walk']
    name = cfg.get('name', '')
    states = cfg.get('states', [{}])
    cams = sorted(set(list(range(0, max(1, pw - W + 1), 40)) + [max(0, pw - W)]))
    bad = 0
    for camX in cams:
        for t in cfg.get('times', (0.0, 0.75, 1.5, 7.0)):
            for s in states:
                im = np.array(BJ.ref_render(st, imgs, camX, t, s).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('%s 镜头 0–%d（每 40）× 时刻 × %d 种状态 整屏都有画（没有露黑）' % (name, pw - W, len(states)), bad)
    for (lab, im, box) in cfg.get('opaque', []):
        a = np.array(im)
        x0, y0, x1, y1 = box
        ex.checked(lab, int((a[y0:y1, x0:x1, 3] != 255).sum()))
    for (lab, im) in cfg.get('binary', []):
        a = np.array(im)
        ex.checked(lab, int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum()))
    # strip：闭合 / 帧条宽 / 每一帧都在动 / 画的东西都在框里
    strips = [L for L in specs if L['t'] == 'strip']
    for L in strips:
        nm, box, n, fps, fn = L['name'], L['box'], L['n'], L['fps'], L['fn']
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (nm, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (nm, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (nm, moving, n), n - moving)
    fns = {}
    for L in strips:
        fns.setdefault(L['fn'], []).append(L)
    for fn, items in fns.items():
        lost = 0
        n, fps = items[0]['n'], items[0]['fps']
        for i in range(n):
            m = np.array(fn(i / fps))[..., 3] > 0
            for L in items:
                x0, y0, x1, y1 = L['box']
                m[y0:y1, x0:x1] = False
            lost += int(m.sum())
        ex.checked('strip %s 每帧画的东西都在框里（框外的像素）' % '+'.join(L['name'] for L in items), lost)
    # wrap 闭合
    for L in [L for L in st['layers'] + st['fg'] if L['type'] == 'wrap' and L.get('vx')]:
        T = L['period'] / abs(L['vx'])
        one = dict(st, layers=[L], fg=[])
        g0 = BJ.ref_render(one, imgs, 0, 0.1, {})
        g1 = BJ.ref_render(one, imgs, 0, 0.1 + T, {})
        ex.checked('wrap %s 一圈 %.1f s 闭合' % (L['image'].split('/')[-1], T), BJ.ndiff(g0, g1))
    # pick：同一层的几张尺寸一致
    for L in st['layers'] + st['fg']:
        if L['type'] == 'pick':
            sizes = {imgs[k].size for k in L['images']}
            ex.checked('pick %s 几张尺寸一致 %s' % (L['key'], sorted(sizes)), len(sizes) - 1)
    # 锚点
    an = st['anchors']
    wx = an.get('walk_x', [0, pw])
    out = int(not (0 <= wx[0] < wx[1] <= pw))
    miss = []

    def pts(v):
        if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(q, (int, float)) for q in v):
            return [v]
        if isinstance(v, (list, tuple)) and len(v) == 4 and all(isinstance(q, (int, float)) for q in v):
            return [v[:2], v[2:]]
        return [q for q in v]
    for k in cfg.get('stand', []):
        if k not in an:
            miss.append(k)
            continue
        for v in pts(an[k]):
            out += not (walk[0] <= v[1] <= walk[1] and wx[0] <= v[0] <= wx[1])
    for k in cfg.get('inside', []):
        if k not in an:
            miss.append(k)
            continue
        for v in pts(an[k]):
            out += not (0 <= v[0] <= pw and 0 <= v[1] <= H)
    ex.checked('%s 规格要求的锚点都导出了（缺 %s）' % (name, miss or '无'), len(miss))
    ex.checked('%s 锚点都在地图里、站人的锚点在可走带里（不满足的条数）' % name, out)
    for (lab, im, box, base, tol) in cfg.get('clear', []):
        a = np.array(im).astype(np.float32)
        x0, y0, x1, y1 = box
        sub = a[y0:y1, x0:x1, :3]
        ex.checked(lab, int((np.abs(sub - np.array(base, np.float32)).max(-1) > tol).sum()))
    # 导出 vs 直接拼
    for camX in sorted(set([0, (pw - W) // 2, pw - W])):
        for t in (0.0, 1.25, 9.0):
            for s in states[:3]:
                got = BJ.ref_render(st, imgs, camX, t, s)
                ex.checked('%s camX=%d t=%.2f %s 导出 vs 直接拼' % (name, camX, t, ','.join(k for k in s if s[k]) or '常态'),
                           BJ.ndiff(got, direct(specs, camX, t, s)))
    for msg in cfg.get('notes', []):
        ex.note(msg)


def walk_stats(im, walk, x0=0, x1=None):
    """可走带的亮度均值 / 标准差（自检 note 用：对比压低了没有）。"""
    a = np.array(im.convert('RGB')).astype(np.float32)
    x1 = x1 or a.shape[1]
    lum = _lum(a[walk[0]:walk[1], x0:x1])
    return float(lum.mean()), float(lum.std())


# ============================================================ 天空 / 云
def sky_img(h, stops, sun=None, bands=12, w=W):
    """天空（不透明）：渐变 + 太阳（屏幕固定的 static 层）。sun = (x, y, r)。"""
    im = A._new(w, h)
    gradient(im, (0, 0, w, h), stops, bands=bands)
    if sun:
        sx, sy, r = sun
        A._glow(im, sx, sy, r * 6, r * 5, (255, 244, 214), 70, rings=5)
        d = ImageDraw.Draw(im)
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=C((255, 246, 220)))
        d.ellipse((sx - r + 2, sy - r + 2, sx + r - 2, sy + r - 2), fill=C((255, 253, 242)))
    return im


def clouds_img(period, h, n_big, n_small, seed, base_y, pal=None, pal2=None):
    """period 循环的云：地平线上一排平底积云 + 上面几朵小的（照 yacht_deck.clouds_img）。"""
    im = A._new(period, h)
    pal = pal or ((255, 255, 255), (240, 245, 250), (212, 226, 240), (190, 208, 230))
    pal2 = pal2 or ((255, 255, 255), (234, 241, 250), (206, 221, 240), (184, 203, 230))
    for i in range(n_big):
        w = hrange(40, 86, seed, i, 1)
        cl = A._cloud_sprite(w, w * hrange(0.26, 0.34, seed, i, 2), seed * 10 + i, pal)
        cx = (i + hrange(0.15, 0.85, seed, i, 3)) * period / n_big
        y = base_y - cl.height + int(hrange(-3, 2, seed, i, 4))
        for dx in (-period, 0, period):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    for i in range(n_small):
        w = hrange(14, 32, seed, i, 11)
        cl = A._cloud_sprite(w, w * 0.32, seed * 10 + 50 + i, pal2)
        cx = (i + hrange(0.1, 0.9, seed, i, 12)) * period / n_small
        y = int(hrange(4, base_y - 26, seed, i, 13))
        for dx in (-period, 0, period):
            paste(im, cl, int(cx + dx - cl.width / 2), y)
    return im


# ============================================================ 海面
def sea_color_fn(stops, hz, y1):
    """海面底色 y → 颜色（stops 从海平线到 y1 均匀分布）。"""
    def f(y):
        u = max(0.0, min(1.0, (y - hz) / float(y1 - hz))) * (len(stops) - 1)
        i = min(len(stops) - 2, int(u))
        return mix(stops[i], stops[i + 1], u - i)
    return f


def sea_band_img(period, y0, y1, hz, ybot, color_at, seed, density=1.0, lite_col=(236, 248, 250)):
    """一条海面浪花（透明底，period 循环）：远处是短亮线，近处是“亮弧 + 下面一道暗线”的小浪（照 yacht_deck）。"""
    im = A._new(period, y1 - y0)
    d = ImageDraw.Draw(im)

    def seg(x, y, L, col):
        for xx in range(x, x + L):
            d.point((xx % period, y - y0), fill=C(col))
    for y in range(y0, y1):
        u = max(0.0, min(1.0, (y - hz) / float(ybot - hz)))
        sea = color_at(y)
        lite = mix(sea, lite_col, 0.36 + 0.1 * (1 - u))
        dark = dk(sea, 0.86)
        if (y - hz) < 3:
            n = int(26 * density * period / 640)
        else:
            gap = 1 + int(u * 3)
            if (y - hz) % (gap + 1):
                continue
            n = int((26 - 12 * u) * density * period / 640)
        for j in range(max(1, n)):
            x = int(hrange(0, period, seed, y, j, 11))
            L = max(1, int(round((1 + u * 7) * hrange(0.5, 1.25, seed, y, j, 12))))
            if hash01(seed, y, j, 13) < 0.7:
                seg(x, y, L, lite)
                if u > 0.3 and y + 1 < y1:
                    seg(x + 1, y + 1, max(1, L - 1), dark)
            else:
                seg(x, y, L, dark)
    return im


def gull_img(dark=False):
    """滑翔的海鸥（7×3）：一字形的翅膀、中间白身子、翅尖一点灰。"""
    g = A._new(7, 3)
    d = ImageDraw.Draw(g)
    wc = (232, 236, 240) if not dark else (150, 154, 166)
    for (x, y) in ((0, 1), (1, 0), (2, 0), (4, 0), (5, 0), (6, 1)):
        px(d, x, y, wc)
    px(d, 3, 1, (250, 250, 250) if not dark else (176, 180, 190))
    px(d, 0, 2, (96, 100, 112))
    px(d, 6, 2, (96, 100, 112))
    return g


def gull(d, x, y, pose, col=(246, 248, 250), tip=(90, 94, 108)):
    """一只海鸥（会扇翅膀的版本，pose 0..3：上 / 平 / 下 / 平）。x, y = 身子。"""
    px(d, x, y, col)
    px(d, x + 1, y, (200, 204, 212))
    if pose == 0:
        for (dx, dy) in ((-1, -1), (-2, -2), (2, -1), (3, -2)):
            px(d, x + dx, y + dy, col)
        px(d, x - 3, y - 2, tip)
        px(d, x + 4, y - 2, tip)
    elif pose == 2:
        for (dx, dy) in ((-1, 0), (-2, 1), (2, 0), (3, 1)):
            px(d, x + dx, y + dy, col)
        px(d, x - 3, y + 1, tip)
        px(d, x + 4, y + 1, tip)
    else:
        for (dx, dy) in ((-1, -1), (-2, -1), (2, -1), (3, -1)):
            px(d, x + dx, y + dy, col)
        px(d, x - 3, y, tip)
        px(d, x + 4, y, tip)


def dhow_img(L, sail=(240, 232, 214), hull=(96, 66, 46), haze_col=None, amt=0.0, two=False):
    """三角帆船（dhow，侧面）：船头往左翘的木船身 + 一根斜桁挂的三角帆（lateen）。L = 船身长。"""
    hgt = int(L * 0.95) + 4
    g = A._new(L + 6, hgt + 3)
    d = ImageDraw.Draw(g)
    by = hgt
    for x in range(L):
        u = x / max(1, L - 1)
        lift = int(round(2.4 * (1 - u) ** 3 + 0.8 * u ** 4))
        vl(d, x + 2, by - 2 - lift, by, hull)
        px(d, x + 2, by - 2 - lift, lt(hull, 0.25))
    hl(d, 3, L, by + 1, dk(hull, 0.7))
    mx = 2 + int(L * 0.55)
    vl(d, mx, by - int(L * 0.7), by - 2, dk(hull, 0.85))
    # 斜桁：从船头上方斜到桅顶后面；帆挂在斜桁下面，是一个往后上翘的三角
    ax, ay = 2 + int(L * 0.08), by - int(L * 0.32)
    bx, by2 = 2 + int(L * 0.86), by - int(L * 0.92)
    pts = [(ax, ay), (bx, by2), (mx + 1, by - 3)]
    d.polygon(pts, fill=C(sail))
    d.line((ax, ay, bx, by2), fill=C(dk(sail, 0.7)))
    d.line((ax + 2, ay + 1, mx, by - 4), fill=C(dk(sail, 0.86)))
    if two:
        px2 = 2 + int(L * 0.2)
        d.polygon([(px2 - 2, by - int(L * 0.25)), (px2 + 3, by - int(L * 0.55)), (px2 + 2, by - 3)], fill=C(dk(sail, 0.94)))
    if haze_col is not None and amt > 0:
        g = haze(g, amt, haze_col)
    return g


def buoy(d, x, y, dy=0, col=(214, 52, 44)):
    """红白浮标（锥顶 + 一圈白带 + 顶上小旗杆）：x, y = 水线中心。"""
    y = y + dy
    hl(d, x - 3, x + 3, y, dk(col, 0.6))
    hl(d, x - 3, x + 3, y - 1, col)
    hl(d, x - 2, x + 2, y - 2, (240, 240, 236))
    hl(d, x - 2, x + 2, y - 3, col)
    hl(d, x - 1, x + 1, y - 4, col)
    px(d, x - 2, y - 1, lt(col, 0.3))
    px(d, x - 1, y - 3, lt(col, 0.3))
    px(d, x + 2, y - 2, (200, 200, 196))
    px(d, x + 3, y - 1, dk(col, 0.7))
    vl(d, x, y - 8, y - 5, (60, 56, 60))
    px(d, x, y - 9, (250, 220, 90))


# ============================================================ 椰枣树 / 椰子树
PALM_PAL = dict(
    leaf=((30, 74, 50), (44, 104, 58), (72, 140, 66), (118, 178, 82), (168, 208, 108)),
    trunk=((182, 156, 116), (148, 122, 88), (114, 92, 66), (80, 64, 50)),
    nut=((126, 120, 56), (92, 84, 40), (164, 112, 58)),
)


def palm_trunk(d, x0, y0, x1, y1, bend, w0=4, w1=3, pal=None):
    """树干：从 (x0, y0)（根）到 (x1, y1)（树冠），往右弯 bend；左边亮右边暗，每 3 行一圈深色的叶痕环，根部稍微张开。"""
    p = pal or PALM_PAL['trunk']
    n = max(2, int(abs(y0 - y1)))
    for i in range(n + 1):
        u = i / n
        x = x0 + (x1 - x0) * u + bend * math.sin(math.pi * u * 0.9)
        y = y0 + (y1 - y0) * u
        w = int(round(w0 + (w1 - w0) * u + (2 if u < 0.04 else 1 if u < 0.09 else 0)))
        xl = int(round(x - w / 2))
        for k in range(w):
            c = p[0] if k == 0 else (p[1] if k < w - 1 else p[2])
            if i % 3 == 0:
                c = p[2] if k < w - 1 else p[3]
            elif i % 3 == 1 and k == w - 1:
                c = p[3]
            px(d, xl + k, round(y), c)
        px(d, xl + w, round(y), p[3])


def palm_crown(d, cx, cy, L, sway, seed, pal=None, nuts=True, back=True):
    """椰子 / 椰枣树冠：十来片羽状叶从中心放射、往下垂；朝上（受光）的叶亮、垂下去的暗；中间一串果子。
    sway −1..1：风从左边来，叶子整体往右偏、右边的叶子垂得多一点。"""
    pal = pal or PALM_PAL['leaf']
    fr = [(14, 1.0), (36, 0.92), (60, 0.8), (84, 0.66), (106, 0.78), (130, 0.9), (154, 1.0), (176, 0.96),
          (198, 0.82), (-14, 0.86), (226, 0.6), (-40, 0.62)]
    order = sorted(range(len(fr)), key=lambda i: -math.sin(math.radians(fr[i][0])))   # 先画往下垂的（在后面）
    for i in order:
        phi0, lk = fr[i]
        phi = math.radians(phi0 + 6 * sway + hrange(-6, 6, seed, i))
        Li = L * lk * hrange(0.86, 1.1, seed, i, 2)
        droop = 0.5 + 0.26 * (1 - math.sin(phi)) + 0.12 * sway * math.cos(phi)
        up = math.sin(phi) > 0.3
        left = math.cos(phi) < -0.2
        hi_c = pal[4] if (up and left) else (pal[3] if up else pal[2])
        lo_c = pal[2] if up else pal[1]
        rach = pal[3] if up else pal[1]
        n = max(4, int(Li))
        pts = []
        for k in range(n + 1):
            s = k / n
            pts.append((cx + math.cos(phi) * Li * s, cy - math.sin(phi) * Li * s + droop * Li * s * s))
        for k in range(2, n + 1):
            x, y = pts[k]
            s = k / n
            ll = max(1, round((1 - abs(s - 0.42) * 1.55) * L * 0.2))
            dx, dy = pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]
            nrm = math.hypot(dx, dy) or 1
            for side in (-1, 1):
                ox = -dy / nrm * side
                oy = dx / nrm * side
                if oy < 0:
                    oy = -oy * 0.45 + 0.55
                ex = x + ox * ll - dx / nrm * ll * 0.35
                ey = y + oy * ll + 0.75 * ll
                d.line((round(x), round(y), round(ex), round(ey)), fill=C(hi_c if side < 0 else lo_c))
                if ll > 2 and k % 2 == 0:
                    px(d, round(ex), round(ey), pal[0])
        d.line([(round(x), round(y)) for (x, y) in pts], fill=C(rach))
    if nuts:
        for (dx, dy, c) in ((-2, 2, 0), (1, 2, 1), (-1, 4, 0), (2, 4, 2), (0, 3, 1)):
            d.ellipse((cx + dx - 1, cy + dy - 1, cx + dx + 1, cy + dy + 1), fill=C(PALM_PAL['nut'][c]))
    px(d, cx, cy, pal[0])
    px(d, cx - 1, cy + 1, pal[1])


# ============================================================ 礁石 / 灌木
ROCK_PAL = [(62, 54, 56), (100, 86, 80), (138, 120, 102), (176, 158, 130), (210, 196, 166)]     # 珊瑚石灰岩（偏暖的灰褐）
ROCK_INK = (40, 36, 44)


def rock_img(w, h, balls, seed, pal=None, ink=ROCK_INK, wet=0, bump=0.5):
    """一块石头（透明底）：几个椭球的并 → 高度场打光（左上来光）；wet = 底下几行是湿的（深一点、偏绿）。"""
    m, z = blob(w, h, balls, seed, noise=0.14, cell=5, base=h - 1)
    rgba, q = shade(m, z, pal or ROCK_PAL, seed, bump=bump, facet=0.18, fcell=6, dither=0.4, seam=0.4,
                    outline=ink, speck=0.02)
    if wet:
        ys = np.arange(h)[:, None]
        wm = m & (ys >= h - wet)
        a = rgba.astype(np.float32)
        a[wm, :3] *= np.array((0.72, 0.8, 0.78), np.float32)
        rgba = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA'), m


def barnacle_dots(d, m, seed, n, y0, y1, ox=0, oy=0):
    """石头水线附近的藤壶 / 小贝壳（白点 + 暗口）。"""
    h, w = m.shape
    k = 0
    for i in range(n * 6):
        x = int(hrange(1, w - 2, seed, i, 1))
        y = int(hrange(y0, y1, seed, i, 2))
        if 0 < y < h - 1 and m[y, x] and m[y - 1, x] and m[y, x + 1]:
            px(d, ox + x, oy + y, (226, 220, 200))
            px(d, ox + x + 1, oy + y, (150, 144, 128))
            px(d, ox + x, oy + y - 1, (70, 64, 66))
            k += 1
            if k >= n:
                break


BUSH_PAL = ((44, 72, 44), (64, 100, 52), (94, 130, 62), (136, 160, 82))
DRY_BUSH = ((86, 80, 52), (116, 108, 64), (148, 138, 78), (184, 172, 104))


def bush(d, cx, base, rx, ry, seed, pal=BUSH_PAL):
    """贴地的一丛灌木：树冠零件（一堆疙瘩）压扁、底边平在 base 上。"""
    canopy(d, cx, base - ry * 0.8, rx, ry, seed, pal=pal)


# ============================================================ 沙面
def sand_surface(im, box, base, shade_c, light, seed, cell=6, lo=0.25, hi=0.75):
    """一片沙：底色 + 大块的明暗（fbm，只在块的边上抖），x1 / y1 含。"""
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    rect(d, x0, y0, x1, y1, base)
    mottle(im, box, base, shade_c, light, seed, cell=cell, lo=lo, hi=hi)


def sand_ripples(d, box, col, hi_col, seed, n, ok=None, Lr=(3, 7)):
    """风吹出来的沙纹：一道道短弧（下面一行暗、上面一点亮），越往前（y 大）越长越疏。ok(x, y) → 能不能画。"""
    x0, y0, x1, y1 = box
    for i in range(n):
        y = int(hrange(y0, y1, seed, i, 1))
        x = int(hrange(x0, x1, seed, i, 2))
        u = (y - y0) / max(1, y1 - y0)
        L = int(hrange(Lr[0], Lr[1], seed, i, 3) * (0.8 + 0.6 * u))
        if ok is not None and not all(ok(x + k, y) for k in range(-1, L + 1)):
            continue
        for k in range(L):
            yy = y - (1 if 0 < k < L - 1 and L > 4 else 0)
            px(d, x + k, yy, col)
        px(d, x + 1, y - 1 - (1 if L > 4 else 0), hi_col)


def ripple_field(d, box, col, hi_col, seed, ok=None, sp0=3, sp1=5, dash=(4, 10), gap=(2, 7)):
    """整片风纹：一行行很缓的波浪线（一段段虚线，下面暗、上面隔一格亮），后面（y 小）密、前面疏。
    颜色只比沙色差一点点——可走带上要有质感，但不能抢人物。"""
    x0, y0, x1, y1 = box
    y = y0
    k = 0
    while y <= y1:
        x = x0 + int(hrange(0, 8, seed, k, 1))
        j = 0
        while x < x1:
            L = int(hrange(dash[0], dash[1], seed, k, j, 2))
            ph = hrange(0, 6.28, seed, k, j, 3)
            for i in range(L):
                xx = x + i
                yy = y + int(round(0.9 * math.sin(xx / 5.1 + ph)))
                if xx >= x1 or (ok is not None and not ok(xx, yy)):
                    continue
                px(d, xx, yy, col)
                if i % 2 == 0 and (ok is None or ok(xx, yy - 1)):
                    px(d, xx, yy - 1, hi_col)
            x += L + int(hrange(gap[0], gap[1], seed, k, j, 4))
            j += 1
        u = (y - y0) / max(1, y1 - y0)
        y += int(round(sp0 + (sp1 - sp0) * u))
        k += 1


def shell(d, x, y, kind, seed):
    """小贝壳 / 碎珊瑚 / 海星（2–4 px）。"""
    if kind == 0:                                                  # 扇贝（粉白）
        px(d, x, y, (246, 214, 206))
        px(d, x + 1, y, (226, 180, 172))
        px(d, x, y - 1, (252, 236, 228))
        px(d, x + 1, y + 1, (170, 140, 132))
    elif kind == 1:                                                # 螺（黄褐）
        px(d, x, y, (214, 176, 120))
        px(d, x + 1, y, (176, 136, 90))
        px(d, x + 1, y - 1, (236, 206, 150))
    elif kind == 2:                                                # 碎珊瑚（白）
        hl(d, x, x + 2, y, (244, 240, 230))
        px(d, x + 1, y - 1, (250, 248, 242))
        px(d, x + 2, y + 1, (190, 184, 172))
    else:                                                          # 小海星（橙）
        px(d, x, y, (230, 120, 70))
        px(d, x - 1, y, (214, 100, 60))
        px(d, x + 1, y, (214, 100, 60))
        px(d, x, y - 1, (246, 150, 90))
        px(d, x, y + 1, (190, 86, 52))
