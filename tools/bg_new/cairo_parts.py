# -*- coding: utf-8 -*-
r"""cairo_parts —— cairo 组（cairo_day / cairo_street_night / cairo_street_dawn / cairo_rooftops）共用的零件。不是背景 key，
本身不导出。2026-10-19 第三轮背景重画（分工 docs/ai/context/20261019-095108-背景重画分工_第三轮.md）。

为什么三张开罗街共用一个函数：第10章白天、终章的夜和黎明是**同一条街、同一个布局、同名锚点**（素材总表 §一.3）。
街道只画一次“固有色”（street_albedo：每栋房子、每扇窗、每个摊子的位置和材质），再按时段出图：
  day   = 固有色 + 太阳在左上的地面投影
  night = 固有色压暗偏蓝（grade）+ 一半窗户亮灯、路灯光圈、开着的店里透出暖光（light_night）
  dawn  = 固有色压成冷紫（grade）+ 战后的破坏（卡车撞楼、路牌的坑、翻倒的水果摊）+ 几盏还亮着的路灯；
          天 / 远景 / 楼顶的晨光按 key rise（0 紫 → 1 橙）换图（pick）
这样房子、路牌、镜子摊空地在三张图里一个像素都不会错位；剧情 key（crashed / stand_wrecked / sign_gone）也是把同一个
固有色函数带上“破坏”再画一遍、和原图逐像素比出变化的框，裁下来做 pick——盖上去严丝合缝。

最底层的小工具（dk / lt / hl / vl / px / rect / plaster / mashrabiya / minaret / sign_ar / person …）直接借
egypt_town_parts.py（同一个国家的街，墙的抹灰、木格窗、宣礼塔是一个画法），用和 bg_jojo.bg_new 一样的模块名加载，不改它。

图层表：每层一个 dict（type / name / img / k / x / y / key …），compose（直接拼）和 export_layers（导出）走同一张表；
和 egypt_town_parts 的元组表不同，这里**任何层都能带 key**（bg.js 支持；夜景的撞墙、卡车逃亡的整屏卷动都要），
所以 compose / 自检也自己写一份（照 bg_jojo.ref_layer 的取整）。

街道（960 宽、ground 160、可走带 148–176）从左到右：
  x   0–66   A  赭黄四层楼：一楼报刊烟酒亭（挂报纸、汽水冰柜）+ 楼梯门；二楼铁阳台
  x  66–126  B  灰绿三层老楼：两个挑出的木格窗（mashrabiya）、一楼卷帘门半拉 + 木门（夜：卖卡车的人 truck_lot 120）
  x 126–192  C  面包店（bakery 150）：敞开的店面、架子上一摞摞圆饼、里面的炉口火光（strip）、门口晾饼的棕榈枝托盘架、
                 蓝白条纹遮阳棚（波浪边 strip）
  x 192–252  D  粉色五层高楼：一楼香料店（一袋袋堆成尖的红 / 黄 / 绿 / 棕香料、罐子、挂着的丝瓜络和篮子）；阳台晾衣（strip）
  x 252–346  E  旅馆（hotel 290）：奶白色的老式旅馆，一楼粗石面 + 拱门 + 两盏铜壁灯，二楼法式窗 + 铁阳台，三楼百叶窗，
                 檐口（hotel_roof：檐口顶 y 64，鸟停在这里）上一排栏杆 + 屋顶的 HOTEL 字架（夜里是霓虹）+ 国旗（strip）
  x 346–394  F  黄色两层：一楼咖啡馆（ahwa：吊灯、水烟壶、墙上的电视、两把靠墙的椅子）；屋顶鸽舍（鸽子 strip）+ 晾衣绳（strip）
  x 394–444  G  玫瑰色三层：一楼镜子店（墙上挂满大大小小的镜子、门边靠着几块玻璃；剧情的镜子架摆在 mirror_stand 410）
  x 444–502  H  灰色五层：一楼果汁店；门前的水果摊（fruit_stand 470）：绿白条纹布篷、木板车上堆成山的橘子 / 芒果、
                 挂着的香蕉和秤、一盏灯泡、车边一摞西瓜
  x 502–558  I  土棕两层：一楼修车铺（黑洞洞的车库、里面半辆旧车、墙上的扳手、门口一摞轮胎、地上的油渍）；
                 屋顶手绘的电影海报大广告牌；剧情的油桶摆在 oil_drum 520
  x 558–612  J  赭粉四层：一楼甜点铺（玻璃柜里一盘盘甜点）；门前人行道上立着路牌（road_sign 580：红圆禁行牌 +
                 蓝色街名牌，样子照道具 road_sign；顶 y 123 = 隼停的地方）
  x 612–668  X  十字路口（crossroad 640）：往里退的横街（两边的侧墙、尽头一栋小楼、头顶的三角彩旗 strip、晾衣绳），
                 路口地上褪了色的斑马线
  x 668–690  K  窄高的五层楼（修鞋小铺）
  x 690–710  AL 窄巷（alley 700）：两边墙往里收、巷底一扇门 + 台阶，很暗，头顶几根晾衣绳（strip）、一盏壁灯
  x 710–814  L  浅土黄四层长楼：一楼药房（绿十字灯箱 + PHARMACY）和收音机店（一摞摞收音机、录音机、电视）；
                 阳台晾衣、晾地毯；路上有排水栅（sewer_grate 760：伊奇钻进去的那个）；夜：上议员的车停 senator_stop 760
  x 814–906  M  转角楼（corner 860）：三层、屋顶边 y 70（rooftop 860：荷尔·荷斯和波因哥站的屋顶边，中间一段没有矮墙）；
                 一楼杂货铺（米袋、汽水箱、挂着的塑料桶）；右边削角 + 蓝色街名牌；key crashed：一楼被卡车撞开的大洞 + 碎砖
  x 906–920  N  转角后面的小横街（很暗）
  x 920–960  清真寺（exit 940 往城北）：红白相间的条纹石墙、阶梯垛口、尖拱大门 + 钟乳石檐、门里的灯、
                 后面的肋纹石穹顶、右上的宣礼塔
头顶：几根下垂的电线；路灯（铸铁灯杆）立在人行道后沿 x 98 / 238 / 376 / 548 / 802（脚 y 147）。
地面：y 146–152 人行道方砖（146 墙脚暗线）、153–154 路缘石（上亮下暗）、155–179 柏油路（低对比的斑驳、补丁、车辙）。
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import io  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402


def _load(name):
    """tools/bg_new/<name>.py，模块名和 bg_jojo.bg_new 一样（'bg_new_' + name），已经加载过就直接复用。"""
    key = 'bg_new_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _load('egypt_town_parts')
V = P.V
C = A._c4
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
mul_box, mul_mask, cast_shadow, mottle, haze = P.mul_box, P.mul_mask, P.cast_shadow, P.mottle, P.haze
SHADOW_MUL, SOFT_MUL = P.SHADOW_MUL, P.SOFT_MUL

W, H = 320, 180
N, FPS = 8, 4.0
INK = (58, 40, 40)
DARK_IN = (54, 42, 44)
IRON, IRON_HI = (46, 44, 50), (96, 94, 102)
WOOD_HI, WOOD, WOOD_D, WOOD_K = P.WOOD_HI, P.WOOD, P.WOOD_D, P.WOOD_K


# ============================================================ 图层表：compose / export / 自检（任何层都能带 key）
def frame_of(t, n=N, fps=FPS):
    return int(math.floor(t * fps + 1e-6)) % n


def cached(raw, n=N, fps=FPS):
    """raw(f) → 第 f 帧（世界坐标的整张画布）；包成 fn(t)，每帧只画一次（自检会把同一帧要很多次）。"""
    cache = {}

    def fn(t):
        f = frame_of(t, n, fps)
        if f not in cache:
            cache[f] = raw(f)
        return cache[f]
    fn.raw = raw
    return fn


def auto_box(fn, n=N, fps=FPS, pad=0):
    """strip 的框 = n 帧画到的像素的外接框（框是从画出来的东西算的，“每帧画的东西都在框里”天然成立）。"""
    bb = None
    for i in range(n):
        b = fn(i / fps).getchannel('A').getbbox()
        if b:
            bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    if bb is None:
        raise ValueError('strip 每一帧都是空的')
    return (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad)


def strip(name, fn, k=1.0, key=None, n=N, fps=FPS, box=None):
    return dict(type='strip', name=name, fn=fn, box=box or auto_box(fn, n, fps), n=n, fps=fps, k=k, key=key)


def blank1():
    return Image.new('RGBA', (1, 1), (0, 0, 0, 0))


def crop_rows(im):
    bb = im.getchannel('A').getbbox()
    if not bb:
        return im, 0
    return im.crop((0, bb[1], im.width, bb[3])), bb[1]


def _tile(im, w):
    out = Image.new('RGBA', (w, im.height), (0, 0, 0, 0))
    for x in range(0, w, im.width):
        out.paste(im, (x, 0))
    return out


def _hex(c):
    return '#%02x%02x%02x' % tuple(int(v) for v in c)


def compose(spec, camX, t=0.0, state=None):
    """照 bg_jojo.ref_layer 的取整把图层表直接拼成一帧（不经导出）：自检拿它和导出的层比。"""
    st = state or {}
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for L in spec:
        typ = L['type']
        if typ != 'pick' and L.get('key') and not st.get(L['key']):
            continue
        if typ == 'static':
            paste(out, L['img'], L.get('x', 0), L.get('y', 0))
        elif typ == 'wrap':
            Pp = L['period']
            o = int(math.floor(camX * L['k'] + t * L['vx'])) % Pp
            big = _tile(L['img'], Pp * (2 + W // Pp))
            paste(out, big.crop((o, 0, o + W, L['img'].height)), 0, L['y'])
        elif typ == 'pano':
            paste(out, L['img'], L.get('x', 0) - math.floor(camX * L['k']), L.get('y', 0))
        elif typ == 'strip':
            n, fps = L['n'], L['fps']
            f = int(math.floor(t * round(fps, 6))) % n
            fr = L['fn'](f / fps).crop(L['box'])
            paste(out, fr, L['box'][0] - math.floor(camX * L['k']), L['box'][1])
        elif typ == 'clouds':
            for (sub, im, x0, y, vx, k) in L['items']:
                x = (x0 + t * vx - camX * k) % L['span'] - 100
                paste(out, im, math.floor(x), y)
        elif typ == 'pick':
            v = st.get(L['key'], 0) or 0
            vals = L['values']
            i = min(range(len(vals)), key=lambda j: abs(vals[j] - v))
            paste(out, L['imgs'][i], L.get('x', 0) - math.floor(camX * L['k']), L.get('y', 0))
        elif typ == 'tint':
            lay = Image.new('RGBA', (W, H), tuple(L['color']) + (int(255 * L['alpha']),))
            out.alpha_composite(lay)
    return out


def export_layers(ex, BJ, spec):
    """图层表 → stage 的 layers（ex.img / ex.bake 存图）。"""
    layers = []
    for L in spec:
        typ, key = L['type'], L.get('key')
        if typ == 'static':
            d = dict(type='static', image=ex.img(L['name'], L['img']), x=L.get('x', 0), y=L.get('y', 0))
        elif typ == 'wrap':
            d = dict(type='wrap', image=ex.img(L['name'], BJ.tile_to(L['img'], L['period'], L['period'] + W)),
                     period=L['period'], k=L['k'], y=L['y'], vx=L['vx'])
        elif typ == 'pano':
            d = dict(type='pano', image=ex.img(L['name'], L['img']), k=L['k'], x=L.get('x', 0), y=L.get('y', 0))
        elif typ == 'strip':
            d = ex.bake(L['name'], L['box'], L['n'], L['fps'], L['fn'], screen=False, k=L['k'], key=key)
        elif typ == 'clouds':
            cl = [dict(image=ex.img(sub, im), x0=float(x0), y=y, vx=vx, k=k) for (sub, im, x0, y, vx, k) in L['items']]
            d = dict(type='clouds', span=L['span'], clouds=cl)
        elif typ == 'pick':
            names = [ex.img('%s%d' % (L['name'], i), im) for i, im in enumerate(L['imgs'])]
            d = dict(type='pick', key=key, values=list(L['values']), images=names, x=L.get('x', 0), y=L.get('y', 0),
                     k=L['k'])
        elif typ == 'tint':
            d = dict(type='tint', color=_hex(L['color']), alpha=L['alpha'])
        else:
            raise ValueError(typ)
        if key and typ not in ('pick', 'strip'):
            d['key'] = key
        layers.append(d)
    return layers


def png_bytes(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.tell()


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def std_checks(ex, BJ, st, spec, cfg):
    """各张图共用的自检（照 ganges_ghat._checks / egypt_town_parts.common_checks，改成 dict 图层表、任何层带 key）。
    cfg：title, PW, walk（地图的可走带）, near（近景整张：底图）, opaque_rows, sky, states, stand, required,
         size_limit, flat=(x0, x1, y0, y1, tol, frac), flat_skip=[框], cams_step。"""
    imgs = ex.images
    PW = cfg['PW']
    title = cfg['title']
    cams = list(range(0, max(1, PW - W + 1), cfg.get('cams_step', 40)))
    if PW > W and cams[-1] != PW - W:
        cams.append(PW - W)
    states = cfg.get('states') or [{}]
    bad = 0
    for camX in cams:
        for tt in (0.0, 0.75, 1.5, 7.0):
            for s in states:
                im = np.array(BJ.ref_render(st, imgs, camX, tt, s).convert('RGB'))
                bad += int((im.sum(-1) == 0).sum())
    ex.checked('%s 镜头 0–%d（每 %d）× 4 个时刻 × %d 种状态 整屏都有画（没有露黑）' %
               (title, PW - W, cfg.get('cams_step', 40), len(states)), bad)
    for (lab, im) in cfg['skies']:
        ex.checked('%s 整张不透明' % lab, int((np.array(im)[..., 3] != 255).sum()))
    a = np.array(cfg['near'])
    y0, y1 = cfg['opaque_rows']
    ex.checked('近景 y %d–%d（地面 + 可走带）整条不透明' % (y0, y1 - 1), int((a[y0:y1, :, 3] != 255).sum()))
    hard = 0
    for L in spec:
        ims = L['imgs'] if L['type'] == 'pick' else ([L['img']] if L['type'] in ('pano', 'static', 'wrap') else [])
        for im in ims:
            pa = np.array(im)
            hard += int(((pa[..., 3] > 0) & (pa[..., 3] < 255)).sum())
    ex.checked('static / wrap / pano / pick 的图只有 0 / 255 两种透明度', hard)
    strips = [L for L in spec if L['type'] == 'strip']
    for L in strips:
        name, box, n, fps, fn = L['name'], L['box'], L['n'], L['fps'], L['fn']
        T = n / fps
        ex.checked('strip %s %.1f s 闭合（t=0 vs t=%.1f）' % (name, T, T), BJ.ndiff_rgba(fn(0.0).crop(box), fn(T).crop(box)))
        ex.checked('strip %s 帧条宽 %d ≤ 4096' % (name, (box[2] - box[0]) * n), max(0, (box[2] - box[0]) * n - 4096))
        fr = [fn(i / fps).crop(box) for i in range(n)]
        moving = sum(BJ.ndiff_rgba(fr[i], fr[(i + 1) % n]) > 0 for i in range(n))
        ex.checked('strip %s 每一帧都在动（相邻帧不同的帧数 = %d / %d）' % (name, moving, n), n - moving)
        hd = sum(int(((np.array(f)[..., 3] > 0) & (np.array(f)[..., 3] < 255)).sum()) for f in fr)
        lost = 0
        for i in range(n):
            m = np.array(fn(i / fps))[..., 3] > 0
            m[box[1]:box[3], box[0]:box[2]] = False
            lost += int(m.sum())
        ex.checked('strip %s 只有 0 / 255 透明度、画的东西都在框里（半透明 %d / 框外 %d）' % (name, hd, lost), hd + lost)
    for L in [L for L in st['layers'] if L['type'] == 'wrap']:
        if not L.get('vx'):
            continue
        T = L['period'] / abs(L['vx'])
        one = dict(st, layers=[L], fg=[])
        s = {L['key']: 1} if L.get('key') else {}
        g0 = BJ.ref_render(one, imgs, 0, 0.1, s)
        g1 = BJ.ref_render(one, imgs, 0, 0.1 + T, s)
        ex.checked('wrap %s 一圈 %.2f s 闭合' % (L['image'].split('/')[-1], T), BJ.ndiff(g0, g1))
    anc = st['anchors']
    miss = [k for k in cfg['required'] if k not in anc]
    ex.checked('素材总表要求的锚点一个不少（缺：%s）' % (','.join(miss) or '无'), len(miss))
    want = cfg.get('values') or {}
    off = [k for k, v in want.items() if anc.get(k) != v]
    ex.checked('锚点的值和素材总表一致（不一致：%s）' % (','.join(off) or '无'), len(off))
    out = []
    wk = cfg['walk']

    def inside(v):
        if isinstance(v, (list, tuple)) and len(v) in (2, 3, 4) and all(isinstance(q, (int, float)) for q in v):
            if len(v) == 2:
                return 0 <= v[0] <= PW and 0 <= v[1] <= H
            if len(v) == 3:
                return 0 <= v[0] <= PW and 0 <= v[1] <= H
            return 0 <= v[0] < v[2] <= PW and 0 <= v[1] < v[3] <= H
        if isinstance(v, (list, tuple)):
            return all(inside(q) for q in v)
        if isinstance(v, dict):
            return all(inside(q) for q in v.values())
        return True
    for k, v in anc.items():
        if not inside(v):
            out.append(k)
    for k in cfg['stand']:
        v = anc.get(k)
        if v is None or not (wk[0] <= v[1] <= wk[1] and 4 <= v[0] <= PW - 4):
            out.append(k + '(站点)')
    ex.checked('锚点都在地图里、站人的点在可走带 %d–%d 里（不满足：%s）' % (wk[0], wk[1], ','.join(out) or '无'), len(out))
    if cfg.get('flat'):
        x0, x1, fy0, fy1, tol, frac = cfg['flat']
        L_ = lum(np.array(cfg.get('flatnear', cfg['near']))[..., :3].astype(np.float32))
        m = np.zeros(L_.shape, bool)
        m[fy0:fy1, x0:x1] = True
        for (sx0, sy0, sx1, sy1) in cfg.get('flat_skip', ()):
            m[sy0:sy1, sx0:sx1] = False
        n_bad, tot = 0, int(m.sum())
        for y in range(fy0, fy1):
            row = L_[y][m[y]]
            if row.size:
                n_bad += int((np.abs(row - np.median(row)) > tol).sum())
        ex.checked('可走带 y %d–%d 只有平整地面（和行中位亮度差 > %d 的像素 %.2f %% ≤ %.1f %%，排除 %d 个框）' %
                   (fy0, fy1 - 1, tol, 100.0 * n_bad / max(1, tot), frac * 100, len(cfg.get('flat_skip', ()))),
                   0 if n_bad <= frac * tot else n_bad)
    for camX in sorted(set([0, PW // 2 - W // 2, PW - W] if PW > W else [0])):
        for tt in (0.0, 1.25, 9.0):
            for s in states:
                got = BJ.ref_render(st, imgs, camX, tt, s)
                want_im = compose(spec, camX, tt, s)
                ex.checked('%s camX=%d t=%.2f %s 导出 vs 直接拼' % (title, camX, tt, s or '默认'), BJ.ndiff(got, want_im))
    tot = sum(png_bytes(im) for k, im in imgs.items() if k.startswith('bg/%s/' % ex.key))
    lim = cfg.get('size_limit', 250 * 1024)
    ex.checked('PNG 合计 %.1f KB ≤ %d KB' % (tot / 1024.0, lim // 1024), 0 if tot <= lim else int((tot - lim) // 1024) + 1)
    nm = lum(a[..., :3].astype(np.float32))
    ex.note('亮度：可走带 y%d–%d 均值 %.0f 标准差 %.1f；后沿 y%d–%d 均值 %.0f 标准差 %.1f' %
            (wk[0], wk[1], nm[wk[0]:wk[1] + 1].mean(), nm[wk[0]:wk[1] + 1].std(),
             wk[0] - 40, wk[0] - 1, nm[wk[0] - 40:wk[0]].mean(), nm[wk[0] - 40:wk[0]].std()))


def diff_pick(name, key, base, variant, pad=0):
    """把“带破坏”的近景和原近景逐像素比，变化的外接框裁下来做 pick（values 0 / 1：0 = 1 像素空图）。
    盖上去和原图严丝合缝（框里没变的像素本来就一样）。返回 (层 dict, 框)。"""
    a, b = np.array(base), np.array(variant)
    dif = np.any(a != b, axis=-1)
    ys, xs = np.nonzero(dif)
    if not len(xs):
        raise ValueError('%s：破坏版和原图一样' % name)
    box = (int(max(0, xs.min() - pad)), int(max(0, ys.min() - pad)), int(min(base.width, xs.max() + 1 + pad)),
           int(min(base.height, ys.max() + 1 + pad)))                 # 转成 int：stage 要写 JSON
    im = variant.crop(box)
    return dict(type='pick', name=name, key=key, values=[0, 1], imgs=[blank1(), im], x=box[0], y=box[1], k=1.0), box


# ============================================================ 时段：固有色 → 白天 / 夜 / 黎明
GRADE = {
    'day': None,
    # 夜：先降饱和再乘一个偏蓝的暗色（月光），加一点底（纯黑会被“露黑”自检当成漏画）
    'night': dict(sat=0.52, mul=(0.27, 0.31, 0.50), add=(7, 9, 22)),
    # 黎明：冷紫的阴面（太阳还在楼后面，楼的正面全在阴影里）
    'dawn': dict(sat=0.58, mul=(0.50, 0.43, 0.62), add=(14, 8, 26)),
}


def grade(im, tod):
    g = GRADE[tod]
    if not g:
        return im.copy()
    a = np.array(im).astype(np.float32)
    rgb = a[..., :3]
    lu = (rgb * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
    rgb = lu + (rgb - lu) * g['sat']
    a[..., :3] = rgb * np.array(g['mul'], np.float32) + np.array(g['add'], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def add_light(a, cx, cy, rx, ry, col, amt, rings=4, mask=None, seed=0):
    """a：近景的 float 数组（H×W×4）。以 (cx, cy) 为心、rx × ry 的椭圆光：分 rings 档、档和档之间 Bayer 抖开
    （像素画的硬边光圈，颜色数少、PNG 小），只加在不透明的像素上（mask 再限一个范围）。"""
    h, w = a.shape[:2]
    x0, x1 = max(0, int(cx - rx) - 1), min(w, int(cx + rx) + 2)
    y0, y1 = max(0, int(cy - ry) - 1), min(h, int(cy + ry) + 2)
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    r = np.sqrt(((xx - cx) / max(1e-3, rx)) ** 2 + ((yy - cy) / max(1e-3, ry)) ** 2)
    k = np.clip(1.0 - r, 0.0, 1.0)
    bay = A._bayer(x1 + 8, y1 + 8)[y0:y1, x0:x1]
    q = np.floor(k * rings + bay * 0.999) / rings
    q = np.where(k <= 0, 0.0, q)
    m = a[y0:y1, x0:x1, 3] > 0
    if mask is not None:
        m &= mask[y0:y1, x0:x1]
    add = np.array(col, np.float32)[None, None, :] * (amt * q)[..., None]
    a[y0:y1, x0:x1, :3] = np.where(m[..., None], a[y0:y1, x0:x1, :3] + add, a[y0:y1, x0:x1, :3])


def mul_rect_light(a, box, col, amt):
    """把框里不透明的像素往暖光色推（开着的店里、亮着的窗）：c' = c·(1−amt) + col·amt。"""
    x0, y0, x1, y1 = box
    sub = a[y0:y1 + 1, x0:x1 + 1]
    m = sub[..., 3] > 0
    c = np.array(col, np.float32)
    sub[..., :3] = np.where(m[..., None], sub[..., :3] * (1 - amt) + c * amt, sub[..., :3])


# ============================================================ 调色（固有色 = 白天的颜色，太阳在左上）
WALL = dict(ochre=(212, 168, 112), sand=(222, 198, 152), pink=(212, 160, 140), cream=(234, 222, 194),
            grey=(196, 188, 170), sage=(176, 182, 158), yellow=(228, 206, 146), brown=(188, 148, 106),
            rose=(214, 168, 130), stone=(208, 194, 158), lsand=(214, 194, 150))
SHUT = dict(green=(70, 122, 92), brown=(126, 86, 56), blue=(80, 110, 136), teal=(58, 126, 126), grey=(118, 126, 124),
            olive=(110, 116, 70))
CURTAIN = [(206, 80, 70), (232, 210, 160), (120, 150, 190), (214, 176, 96), (170, 120, 160), (236, 232, 222)]
GLASS = (150, 172, 188)
SIDE_C, SIDE_D, SIDE_HI = (198, 188, 168), (182, 172, 152), (210, 202, 184)
CURB_HI, CURB_MID, CURB_FACE = (218, 212, 196), (196, 190, 176), (146, 138, 124)
ROAD_C, ROAD_D, ROAD_HI = (166, 158, 146), (152, 144, 134), (178, 170, 158)
LIGHT_WARM = (255, 214, 140)
LIGHT_LAMP = (255, 226, 160)

# ============================================================ 街道：尺寸 / 坐标
PW = 960
GROUND = 160
WALK = (148, 176)
LANE = 146              # 墙脚 = 人行道后沿（房子画到 y 145）
CURB = 153              # 路缘石顶（亮）；154 是立面（暗）
ROAD0 = 155
GF = 104                # 一楼顶的腰线（一楼 104–145，门洞 113–145）
FH = 19                 # 楼上每层的高度


def floor_band(k):
    """第 k 层楼上（k = 1 是二楼）的 (上沿 y, 下沿 y)。"""
    yb = GF - 2 - (k - 1) * FH
    return yb - FH + 1, yb


def top_of(n):
    """n 层楼上的房子：檐口顶 y（最上一层的上沿再往上 3 px）。"""
    return floor_band(n)[0] - 3


CROSS = (612, 668)      # 横街（路口）
ALLEY = (690, 710)
SIDEST = (906, 920)     # 转角楼后面的小横街
MOSQUE = (920, 960)
VP_Y = 118              # 往里退的街的消失点高度
SIGN_X, SIGN_FOOT, SIGN_TOP = 580, 147, 123     # 路牌：杆脚 / 牌顶（道具 road_sign 8×25，同一个样子）
STAND = (446, 498)      # 水果摊（布篷 + 板车）
CRASH = (838, 886)      # 转角楼被撞开的洞（x）
CRASH_TOP = 112
LAMPS_X = (98, 238, 376, 548, 802)

ANCHORS = dict(arrive=[40, 164], bakery=[150, 152], asker=[230, 160], hotel=[290, 150], hotel_roof=[300, 64],
               kids=[360, 164], mirror_stand=[410, 160], fruit_stand=[470, 160], oil_drum=[520, 162],
               road_sign=[580, 150], crossroad=[640, 162], alley=[700, 152], sewer_grate=[760, 170],
               corner=[860, 150], rooftop=[860, 70], exit=[940, 162])
NIGHT_ANCHORS = dict(truck_lot=[120, 164], senator_stop=[760, 162], lanes=[154, 163, 172])
DAWN_ANCHORS = dict(clock_tower=[300, 40])
STAND_PTS = ('arrive', 'bakery', 'asker', 'hotel', 'kids', 'mirror_stand', 'fruit_stand', 'oil_drum', 'road_sign',
             'crossroad', 'alley', 'sewer_grate', 'corner', 'exit')

# 楼：x0, x1, 楼上几层, 墙色, 种子, 窗的位置（窗洞左沿 x）, 每层的窗（从二楼往上，字母见 window()）
BLD = [
    dict(id='A', x0=0, x1=66, n=3, col=WALL['ochre'], seed=11, bays=(9, 29, 49), floors=('oho', 'cbo', 'oco'),
         shut=SHUT['green']),
    dict(id='B', x0=66, x1=126, n=2, col=WALL['sage'], seed=12, bays=(73, 105), floors=('mm', 'oc'), shut=SHUT['brown']),
    dict(id='C', x0=126, x1=192, n=3, col=WALL['sand'], seed=13, bays=(134, 155, 176), floors=('oco', 'obo', 'hoc'),
         shut=SHUT['blue']),
    dict(id='D', x0=192, x1=252, n=4, col=WALL['pink'], seed=14, bays=(200, 218, 236), floors=('obo', 'oco', 'bob', 'coo'),
         shut=SHUT['green']),
    dict(id='F', x0=346, x1=394, n=1, col=WALL['yellow'], seed=16, bays=(355, 377), floors=('oh',), shut=SHUT['teal']),
    dict(id='G', x0=394, x1=444, n=2, col=WALL['rose'], seed=17, bays=(402, 428), floors=('bo', 'mo'), shut=SHUT['brown']),
    dict(id='H', x0=444, x1=502, n=4, col=WALL['grey'], seed=18, bays=(451, 470, 489), floors=('oco', 'bho', 'oco', 'cco'),
         shut=SHUT['olive']),
    dict(id='I', x0=502, x1=558, n=1, col=WALL['brown'], seed=19, bays=(514, 538), floors=('oo',), shut=SHUT['green']),
    dict(id='J', x0=558, x1=612, n=3, col=WALL['rose'], seed=20, bays=(564, 581, 598), floors=('obo', 'ooc', 'coo'),
         shut=SHUT['blue']),
    dict(id='K', x0=668, x1=690, n=4, col=WALL['cream'], seed=21, bays=(675,), floors=('o', 'b', 'o', 'c'),
         shut=SHUT['grey']),
    dict(id='L', x0=710, x1=814, n=3, col=WALL['lsand'], seed=22, bays=(717, 737, 757, 777, 797),
         floors=('obcbo', 'ocboc', 'oocco'), shut=SHUT['green']),
]
BLD_BY = {b['id']: b for b in BLD}


# ============================================================ 小工具
FONT3 = {
    'A': ('.1.', '1.1', '111', '1.1', '1.1'), 'C': ('.11', '1..', '1..', '1..', '.11'),
    'E': ('111', '1..', '11.', '1..', '111'), 'H': ('1.1', '1.1', '111', '1.1', '1.1'),
    'L': ('1..', '1..', '1..', '1..', '111'), 'M': ('1.1', '111', '111', '1.1', '1.1'),
    'O': ('111', '1.1', '1.1', '1.1', '111'), 'P': ('11.', '1.1', '11.', '1..', '1..'),
    'R': ('11.', '1.1', '11.', '1.1', '1.1'), 'T': ('111', '.1.', '.1.', '.1.', '.1.'),
    'Y': ('1.1', '1.1', '.1.', '.1.', '.1.'), 'I': ('111', '.1.', '.1.', '.1.', '111'),
    'S': ('.11', '1..', '.1.', '..1', '11.'), 'N': ('11.', '1.1', '1.1', '1.1', '1.1'),
    'D': ('11.', '1.1', '1.1', '1.1', '11.'), 'K': ('1.1', '1.1', '11.', '1.1', '1.1'),
    'U': ('1.1', '1.1', '1.1', '1.1', '111'), 'F': ('111', '1..', '11.', '1..', '1..'),
}


def text3(d, x, y, s, col, scale=1):
    """3×5 的小字（路牌 / 招牌上的英文，像素画里读得出就行）。返回宽度。"""
    cx = x
    for ch in s:
        g = FONT3.get(ch)
        if g:
            for r, row in enumerate(g):
                for c, v in enumerate(row):
                    if v == '1':
                        rect(d, cx + c * scale, y + r * scale, cx + c * scale + scale - 1, y + r * scale + scale - 1, col)
        cx += (4 if ch != ' ' else 3) * scale
    return cx - x


def cornice(im, x0, x1, y, col, depth=3, dent=False):
    """檐口线脚（x1 不含）：顶上一行亮（受光）、挑出墙面 1 px；下沿暗 + 墙上一道影（太阳在左上）。"""
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = P.wall_pal(col)
    hl(d, x0 - 1, x1, y, lt(col, 0.32))
    rect(d, x0 - 1, y + 1, x1, y + depth - 1, md)
    hl(d, x0 - 1, x1, y + depth - 1, sh)
    if dent:
        for xx in range(x0, x1, 3):
            px(d, xx, y + depth - 1, kk)
            px(d, xx, y + depth - 2, sh)
    mul_box(im, (x0, y + depth, x1 - 1, y + depth), SHADOW_MUL)
    mul_box(im, (x0 + 1, y + depth + 1, x1 - 1, y + depth + 1), SHADOW_MUL, level=0.5)


def window(im, reg, x, y, w, h, wall, kind, shc, seed):
    """一扇窗（(x, y) = 窗洞左上，w × h）。kind：
         o 开着（两扇百叶推开贴在墙上、玻璃窗 + 窗帘）  c 百叶关着  h 半开（左扇关）
         b 阳台门 + 铁栏杆小阳台（h 要高一点）        a 拱顶的开窗              m 挑出来的木格窗
    reg['win'] 记下窗洞（夜里按它点灯）。"""
    d = ImageDraw.Draw(im)
    fr = lt(wall, 0.3)
    if kind == 'm':
        P.mashrabiya(im, x - 2, y - 1, w + 4, h + 3, wood=dk(shc, 1.0) if shc else WOOD, seed=seed)
        reg['win'].append((x - 1, y + 1, w + 2, h, 'm', seed))
        return
    rect(d, x - 2, y - 2, x + w + 1, y + h + 1, fr)                 # 抹灰窗套
    hl(d, x - 3, x + w + 2, y - 3, lt(fr, 0.4))                     # 窗楣（顶上受光）
    hl(d, x - 2, x + w + 1, y - 2, dk(fr, 0.9))
    vl(d, x + w + 1, y - 1, y + h + 1, dk(fr, 0.84))
    rect(d, x, y, x + w - 1, y + h - 1, DARK_IN)
    if kind == 'a':                                                 # 拱顶：上面两个角剪掉
        for (xx, yy) in ((x, y), (x + w - 1, y), (x, y + 1), (x + w - 1, y + 1), (x + 1, y), (x + w - 2, y)):
            px(d, xx, yy, fr)
    hw = w // 2

    def leaf(a, b, yy0, yy1):
        rect(d, a, yy0, b, yy1, shc)
        for yy in range(yy0 + 1, yy1, 2):
            hl(d, a + 1, b - 1, yy, dk(shc, 0.72))
        vl(d, a, yy0, yy1, lt(shc, 0.25))
        vl(d, b, yy0, yy1, dk(shc, 0.6))

    def glass(a, b, yy0, yy1):
        cur = CURTAIN[int(hash01(seed, a, 3) * len(CURTAIN))]
        rect(d, a, yy0, b, yy1, DARK_IN)
        px(d, a + 1, yy0 + 1, GLASS)                               # 玻璃反光一道斜线
        px(d, a + 2, yy0 + 2, dk(GLASS, 0.8))
        vl(d, a, yy0, yy1, cur)                                     # 窗帘拢在两边
        vl(d, b, yy0, yy1, dk(cur, 0.8))
        if b - a > 3 and hash01(seed, a, 4) < 0.5:
            vl(d, a + 1, yy0 + 2, yy1, dk(cur, 0.9))
        hl(d, a, b, yy0, dk(DARK_IN, 0.7))

    if kind in ('o', 'a', 'b'):
        glass(x, x + w - 1, y, y + h - 1)
        vl(d, x + hw - 1 + (w % 2), y + 1, y + h - 1, (214, 206, 190))      # 中挺
        hl(d, x, x + w - 1, y + h // 3, (214, 206, 190))
        rect(d, x - 4, y, x - 3, y + h - 1, shc)                    # 推开贴在墙上的两扇百叶
        vl(d, x - 4, y, y + h - 1, lt(shc, 0.2))
        rect(d, x + w + 2, y, x + w + 3, y + h - 1, dk(shc, 0.8))
        for yy in range(y + 1, y + h - 1, 2):
            px(d, x - 3, yy, dk(shc, 0.7))
            px(d, x + w + 3, yy, dk(shc, 0.6))
    elif kind == 'c':
        leaf(x, x + hw - 1, y, y + h - 1)
        leaf(x + hw, x + w - 1, y, y + h - 1)
    elif kind == 'h':
        glass(x + hw, x + w - 1, y, y + h - 1)
        leaf(x, x + hw - 1, y, y + h - 1)
        rect(d, x + w + 2, y, x + w + 3, y + h - 1, dk(shc, 0.8))
    if kind == 'b':                                                 # 小阳台：板 + 铁栏杆 + 盆花
        sy = y + h
        rect(d, x - 5, sy, x + w + 4, sy + 1, lt(wall, 0.15))
        hl(d, x - 5, x + w + 4, sy, lt(wall, 0.4))
        hl(d, x - 5, x + w + 4, sy + 1, dk(wall, 0.7))
        for xx in range(x - 4, x + w + 4, 2):
            vl(d, xx, sy - 5, sy - 1, IRON)
        hl(d, x - 5, x + w + 4, sy - 6, IRON)
        hl(d, x - 5, x + w + 4, sy - 3, IRON)
        mul_box(im, (x - 4, sy + 2, x + w + 5, sy + 3), SHADOW_MUL)
        if hash01(seed, x, 8) < 0.6:                               # 一盆花
            pc = (196, 92, 70)
            rect(d, x - 4, sy - 3, x - 2, sy - 1, pc)
            px(d, x - 4, sy - 4, (60, 120, 60))
            px(d, x - 3, sy - 5, (80, 150, 70))
            px(d, x - 2, sy - 4, (60, 120, 60))
            px(d, x - 3, sy - 6, (220, 80, 110))
    else:
        hl(d, x - 3, x + w + 2, y + h + 1, lt(fr, 0.38))            # 窗台
        mul_box(im, (x - 2, y + h + 2, x + w + 3, y + h + 2), SHADOW_MUL)
    reg['win'].append((x, y, w, h, kind, seed))


def upper_floors(im, reg, b):
    """楼上：每层一道淡淡的层线 + 窗（按 b['floors'] 的字母）。"""
    d = ImageDraw.Draw(im)
    for k in range(1, b['n'] + 1):
        yt, yb = floor_band(k)
        if k > 1:
            hl(d, b['x0'], b['x1'] - 1, yb + 1, dk(b['col'], 0.9))
            hl(d, b['x0'], b['x1'] - 1, yb + 2, lt(b['col'], 0.12))
        row = b['floors'][k - 1]
        for i, x in enumerate(b['bays']):
            kind = row[i] if i < len(row) else 'o'
            if kind == '-':
                continue
            sd = b['seed'] * 31 + k * 7 + i
            if kind == 'b':
                window(im, reg, x, yt + 2, 8, 14, b['col'], 'b', b['shut'], sd)
            elif kind == 'm':
                window(im, reg, x - 2, yt + 2, 12, 12, b['col'], 'm', WOOD, sd)
            else:
                window(im, reg, x, yt + 3, 8, 11, b['col'], kind, b['shut'], sd)


def wall_block(im, b, top=None):
    """抹灰墙面（到一楼墙脚）+ 一楼顶的腰线 + 檐口。"""
    x0, x1 = b['x0'], b['x1']
    top = top if top is not None else top_of(b['n'])
    d = P.plaster(im, x0, x1, top, LANE - 1, b['col'], b['seed'], streaks=3, cell=4, damp=6, cracks=3)
    hl(d, x0, x1 - 1, GF - 1, lt(b['col'], 0.3))
    rect(d, x0, GF, x1 - 1, GF + 1, dk(b['col'], 0.93))
    hl(d, x0, x1 - 1, GF + 2, dk(b['col'], 0.8))
    cornice(im, x0, x1, top, b['col'], dent=b['n'] >= 3)
    return d


def antenna(d, x, base, h, seed=0, col=(92, 92, 100)):
    """80 年代的电视天线：一根细杆 + 两三根短横杆（鱼骨），顶上一点深色。画在描边之后（不然一圈墨线会把它描成一团）。返回顶点。"""
    vl(d, x, base - h, base, col)
    n = 2 + int(hash01(seed, 1) * 2)
    for i in range(n):
        y = base - h + 1 + i * 3
        L = 4 - i
        hl(d, x - L, x + L, y, col if i else lt(col, 0.2))
    px(d, x, base - h - 1, dk(col, 0.6))
    return (x, base - h - 1)


def water_tank(im, x, base, w=14, h=9, legs=4, col=(150, 156, 160)):
    """屋顶水箱：铁皮圆筒（横放的侧影：上下两道箍、左亮右暗）+ 角钢腿。返回 (x0, y0, x1, y1)。"""
    d = ImageDraw.Draw(im)
    top = base - legs - h
    for i in range(w):
        u = i / max(1, w - 1)
        c = lt(col, 0.25) if u < 0.2 else (dk(col, 0.72) if u > 0.75 else col)
        vl(d, x + i, top + 1, top + h - 1, c)
    hl(d, x + 1, x + w - 2, top, lt(col, 0.3))
    hl(d, x, x + w - 1, top + 2, dk(col, 0.8))
    hl(d, x, x + w - 1, top + h - 3, dk(col, 0.8))
    hl(d, x + 1, x + w - 2, top + h - 1, dk(col, 0.6))
    for xx in (x + 1, x + w - 2):
        vl(d, xx, top + h, base, IRON)
    hl(d, x + 1, x + w - 2, base - legs // 2, IRON)
    px(d, x + w // 2, top - 1, IRON)                                # 盖子把手
    for k in range(2):                                              # 锈迹往下淌
        sx = x + 3 + int(hash01(x, k, 5) * (w - 6))
        vl(d, sx, top + 3, top + 3 + int(hrange(1, h - 4, x, k)), (150, 100, 70))
    return (x, top, x + w, base)


def roof_hut(im, x0, x1, base, top, col, seed):
    """屋顶的楼梯间小屋：抹灰方盒 + 一扇小铁门 + 顶上一道檐。"""
    d = P.plaster(im, x0, x1, top, base, col, seed, streaks=1, cell=3, damp=2, cracks=1)
    cornice(im, x0, x1, top, col, depth=2)
    dx = x0 + 3
    rect(d, dx, base - 9, dx + 4, base, (90, 96, 104))
    vl(d, dx, base - 9, base, lt((90, 96, 104), 0.3))
    px(d, dx + 3, base - 5, (200, 190, 120))


def laundry(d, x0, x1, y, f, seed, sag=2, n=None, amp=1.0, cols=None):
    """一根晾衣绳 + 一排衣服（f 帧：衣服下摆左右摆 0 / 1 px、偶尔一件被风掀起来）。"""
    cols = cols or P.CLOTH
    P.wire(d, x0, y, x1, y, sag, col=(70, 64, 60))
    span = x1 - x0
    k = 0
    x = x0 + 2
    while x < x1 - 3:
        wv = 3 + int(hash01(seed, k, 1) * 3)
        if x + wv > x1 - 1:
            break
        u = (x + wv / 2 - x0) / max(1, span)
        yy = int(round(y + sag * 4 * u * (1 - u)))
        c = cols[int(hash01(seed, k, 2) * len(cols))]
        hgt = 4 + int(hash01(seed, k, 3) * 4)
        ph = math.tau * f / N + k * 1.3 + seed
        sw = math.sin(ph) * amp
        lift = 1 if sw > 0.6 else 0
        for r in range(hgt - lift):
            off = int(round(sw * r / max(1, hgt)))
            cc = c if r < hgt - 2 else dk(c, 0.82)
            hl(d, x + off, x + wv - 1 + off, yy + 1 + r, cc)
        hl(d, x, x + wv - 1, yy + 1, lt(c, 0.25))
        px(d, x, yy, (236, 236, 228))                               # 衣夹
        x += wv + 1 + int(hash01(seed, k, 4) * 3)
        k += 1


def pigeon_px(d, x, y, pose, col=(122, 126, 140)):
    """一只很小的鸽子（3–5 px）：pose 0 站着、1 低头啄、2 张翅膀、3 飞（翅膀往上）、4 飞（翅膀往下）。"""
    hd = lt(col, 0.2)
    if pose in (0, 1):
        hl(d, x - 1, x + 1, y, col)
        px(d, x + 2, y - (0 if pose == 1 else 1), hd)
        px(d, x - 2, y, dk(col, 0.7))
        px(d, x, y + 1, (200, 110, 90))
    elif pose == 2:
        hl(d, x - 2, x + 2, y - 1, lt(col, 0.1))
        hl(d, x - 1, x + 1, y, col)
        px(d, x + 2, y - 1, hd)
    elif pose == 3:
        px(d, x - 2, y - 2, col)
        px(d, x - 1, y - 1, col)
        px(d, x, y, col)
        px(d, x + 1, y - 1, col)
        px(d, x + 2, y - 2, col)
    else:
        hl(d, x - 1, x + 1, y, col)
        px(d, x - 2, y + 1, col)
        px(d, x + 2, y + 1, col)


def bracket_lamp(d, reg, x, y, face=1, col=(54, 58, 56)):
    """墙上的铸铁壁灯：一根弯出来的臂 + 四方灯罩。reg['lamp'] 记下灯心（夜里点亮）。"""
    hl(d, x, x + 3 * face, y, col)
    px(d, x + 4 * face, y + 1, col)
    lx = x + 4 * face
    rect(d, lx - 2, y + 2, lx + 2, y + 6, col)
    rect(d, lx - 1, y + 3, lx + 1, y + 5, (246, 236, 200))
    hl(d, lx - 3, lx + 3, y + 1, dk(col, 0.8))
    px(d, lx, y + 7, col)
    reg['lamp'].append((lx, y + 4, 'wall'))


def lamp_post(im, reg, x, base=SIGN_FOOT, top=100, col=(52, 62, 58)):
    """铸铁路灯（刷墨绿，开罗老城那种）：带线脚的底座、细杆、半腰一道箍、顶上弯出去的臂 + 四方灯。脚落在人行道后沿。"""
    d = ImageDraw.Draw(im)
    hi, md, sh = lt(col, 0.32), col, dk(col, 0.62)
    rect(d, x - 2, base - 6, x + 2, base, md)
    hl(d, x - 2, x + 2, base - 6, hi)
    hl(d, x - 3, x + 3, base, sh)
    hl(d, x - 3, x + 3, base - 1, md)
    for yy in range(top + 4, base - 6):
        px(d, x - 1, yy, hi)
        px(d, x, yy, md)
    hl(d, x - 1, x + 1, top + 20, hi)
    hl(d, x - 1, x + 1, top + 21, sh)
    vl(d, x + 1, top + 4, base - 7, sh)
    # 臂：往右弯出去 6 px，下面挂灯
    hl(d, x, x + 5, top + 3, md)
    px(d, x + 1, top + 4, md)
    px(d, x + 2, top + 5, md)
    px(d, x + 6, top + 4, md)
    lx = x + 6
    rect(d, lx - 2, top + 5, lx + 2, top + 10, md)
    rect(d, lx - 1, top + 6, lx + 1, top + 9, (246, 236, 200))
    hl(d, lx - 3, lx + 3, top + 5, sh)
    px(d, lx, top + 11, md)
    px(d, x, top + 2, hi)                                           # 杆顶的小球
    reg['lamp'].append((lx, top + 8, 'post'))
    return (lx, top + 8)


def bulb(d, reg, x, y):
    """一根电线吊着的灯泡（摊子上的）。"""
    vl(d, x, y - 4, y - 1, (60, 56, 52))
    px(d, x, y, (244, 236, 210))
    px(d, x, y + 1, (226, 214, 180))
    reg['lamp'].append((x, y, 'bulb'))


# ============================================================ 一楼的店面
def shop_opening(im, reg, x0, x1, top, base=LANE - 1, night_open=True, inner=(74, 58, 52), frame=None):
    """店面的门洞：里面暗（上 / 左沿再暗一道 = 墙厚挡住的光），返回 ImageDraw。reg['shop'] 记下（夜里亮灯）。"""
    d = ImageDraw.Draw(im)
    rect(d, x0, top, x1, base, inner)
    hl(d, x0, x1, top, dk(inner, 0.62))
    hl(d, x0, x1, top + 1, dk(inner, 0.8))
    vl(d, x0, top, base, dk(inner, 0.7))
    if frame:
        vl(d, x0 - 1, top - 1, base, frame)
        vl(d, x1 + 1, top - 1, base, dk(frame, 0.8))
        hl(d, x0 - 1, x1 + 1, top - 1, frame)
    reg['shop'].append((x0, top, x1, base, night_open))
    return d


def sign_board(d, x0, y0, x1, y1, bg, fg, seed, rows=1, latin=None, lcol=None):
    """店招：底板 + 阿拉伯文的样子（P.sign_ar）+ 可选的一行英文小字。"""
    P.sign_ar(d, x0, y0, x1, y1, bg, fg, seed=seed, rows=rows)
    if latin:
        w = len(latin) * 4 - 1
        text3(d, (x0 + x1) // 2 - w // 2, y1 - 6, latin, lcol or fg)


def shelves(d, x0, x1, y0, y1, seed, cols, step=5):
    """店里靠墙的架子：一层层木板 + 板上一排排小东西（罐子、盒子、瓶子，颜色随机）。"""
    for y in range(y0, y1, step):
        hl(d, x0, x1, y, WOOD_D)
        x = x0 + 1
        k = 0
        while x < x1 - 1:
            c = cols[int(hash01(seed, y, k, 1) * len(cols))]
            w = 1 + int(hash01(seed, y, k, 2) * 2)
            hh = 2 + int(hash01(seed, y, k, 3) * 2)
            rect(d, x, y - hh, min(x1 - 1, x + w - 1), y - 1, c)
            px(d, x, y - hh, lt(c, 0.35))
            x += w + 1
            k += 1


def draw_kiosk(im, reg):
    """A：报刊烟酒亭（一楼左半）+ 楼梯门（右半）。"""
    b = BLD_BY['A']
    d = ImageDraw.Draw(im)
    d = shop_opening(im, reg, 4, 38, 113, inner=(92, 70, 56), night_open=True)
    rect(d, 4, 133, 38, LANE - 1, (132, 92, 58))                     # 木柜台
    hl(d, 4, 38, 133, (176, 130, 84))
    for xx in range(6, 38, 5):
        vl(d, xx, 135, LANE - 1, (110, 76, 48))
    shelves(d, 6, 26, 118, 132, 101, [(220, 60, 50), (240, 240, 230), (60, 110, 190), (230, 190, 60), (40, 140, 90)], 4)
    rect(d, 28, 116, 37, 132, (196, 48, 46))                         # 汽水冰柜（红，白波浪）
    rect(d, 29, 118, 36, 125, (150, 190, 210))
    hl(d, 29, 36, 128, (246, 240, 236))
    px(d, 30, 129, (246, 240, 236))
    px(d, 35, 127, (246, 240, 236))
    vl(d, 28, 116, 132, (230, 110, 100))
    for i, xx in enumerate(range(5, 37, 4)):                         # 门楣上挂的一排报纸
        vl(d, xx + 1, 113, 114, (70, 60, 50))
        c = (236, 232, 220) if i % 3 else (226, 214, 180)
        rect(d, xx, 115, xx + 2, 120, c)
        hl(d, xx, xx + 2, 116, (60, 60, 70))
        px(d, xx + 1, 118, (200, 60, 50) if i % 2 else (60, 60, 70))
    sign_board(d, 3, 106, 39, 111, (204, 48, 44), (250, 246, 236), 102)
    # 楼梯门：双扇木门 + 门顶小气窗
    P.door(im, 46, LANE - 1, 12, 29, (120, 84, 56), frame=lt(b['col'], 0.3), arch=False, studs=False, seed=3)
    d = ImageDraw.Draw(im)
    rect(d, 46, 112, 57, 115, (60, 70, 80))
    for xx in range(47, 57, 2):
        vl(d, xx, 112, 115, (150, 140, 110))
    px(d, 44, 120, (60, 90, 160))                                    # 门牌
    px(d, 45, 120, (60, 90, 160))


def draw_b_ground(im, reg):
    """B：卷帘门（拉起来一半，下面黑）+ 小木门。"""
    d = ImageDraw.Draw(im)
    x0, x1 = 70, 104
    rect(d, x0, 113, x1, LANE - 1, (64, 52, 48))
    reg['shop'].append((x0, 131, x1, LANE - 1, False))
    for y in range(113, 131):                                        # 波纹铁皮卷帘
        c = (164, 166, 160) if y % 2 else (134, 136, 132)
        hl(d, x0, x1, y, c)
    hl(d, x0, x1, 131, (100, 100, 98))
    hl(d, x0 + 2, x1 - 2, 132, (40, 36, 36))
    rect(d, x0 - 1, 111, x1 + 1, 112, (110, 112, 108))               # 卷帘盒
    for i in range(6):                                               # 喷漆的涂鸦 / 锈
        xx = int(hrange(x0 + 2, x1 - 6, 7, i))
        yy = int(hrange(115, 128, 7, i, 1))
        px(d, xx, yy, (150, 110, 80))
        px(d, xx + 1, yy + 1, (150, 110, 80))
    P.sign_ar(d, x0 + 6, 120, x0 + 24, 124, None, (40, 90, 160), seed=12)
    P.door(im, 110, LANE - 1, 11, 30, (96, 70, 50), frame=lt(WALL['sage'], 0.25), studs=True, seed=4)


def draw_bakery(im, reg):
    """C：面包店。"""
    d = ImageDraw.Draw(im)
    x0, x1 = 132, 186
    d = shop_opening(im, reg, x0, x1, 114, inner=(104, 74, 56))
    rect(d, x0 + 1, 116, x1 - 1, 131, (122, 86, 60))                 # 后墙（被炉火熏黑的砖）
    for y in range(117, 131, 3):
        hl(d, x0 + 1, x1 - 1, y, (104, 70, 50))
        for xx in range(x0 + 2 + (y // 3) % 2 * 3, x1 - 1, 6):
            px(d, xx, y + 1, (104, 70, 50))
    # 炉口（拱形，火光在 strip 里）
    ox, ow = 160, 14
    rect(d, ox - 2, 118, ox + ow + 1, 131, (90, 62, 46))
    rect(d, ox, 121, ox + ow - 1, 129, (40, 24, 20))
    for i in range(ow):
        r = abs(i - ow / 2 + 0.5) / (ow / 2)
        if r > 0.7:
            px(d, ox + i, 121, (90, 62, 46))
    hl(d, ox - 2, ox + ow + 1, 118, (150, 110, 80))
    # 架子上的饼（左边一摞摞）
    for (sx, n) in ((136, 4), (144, 5), (152, 3)):
        for k in range(n):
            y = 129 - k * 3
            d.ellipse((sx - 3, y - 1, sx + 3, y + 1), fill=C((210, 160, 96)))
            hl(d, sx - 2, sx + 2, y - 1, (232, 196, 132))
            px(d, sx + 2, y + 1, (166, 112, 62))
    # 柜台 + 台面上一张张圆饼
    rect(d, x0, 132, x1, LANE - 1, (150, 110, 74))
    hl(d, x0, x1, 132, (196, 156, 108))
    hl(d, x0, x1, 133, (120, 84, 56))
    for xx in range(x0 + 3, x1 - 2, 6):
        vl(d, xx, 135, LANE - 2, (128, 92, 62))
    for i, xx in enumerate(range(x0 + 4, x1 - 4, 7)):
        hl(d, xx - 2, xx + 2, 131, (220, 172, 104))
        px(d, xx, 130, (238, 200, 140))
        px(d, xx + 1, 131, (180, 128, 72))
    # 遮阳棚（波浪边在 strip）
    P.awning(im, 128, 190, 108, 4, (52, 104, 168), (240, 240, 236), stripe=4, scallop=False, shadow=4)
    d = ImageDraw.Draw(im)
    sign_board(d, 140, 104, 178, 107, (40, 90, 150), (250, 246, 236), 103)
    # 门口晾饼的架子（棕榈枝托盘一层层，站在人行道后沿）
    for k in range(4):
        y = 134 + k * 3
        rect(d, 168, y, 189, y + 1, (176, 140, 84))
        for xx in range(169, 189, 3):
            px(d, xx, y, (206, 170, 110))
        for xx in range(170, 188, 5):
            hl(d, xx, xx + 2, y - 1, (214, 166, 100))
            px(d, xx + 1, y - 2, (232, 194, 132))
    vl(d, 168, 132, LANE, (120, 86, 52))
    vl(d, 189, 132, LANE, (100, 70, 44))
    reg['ground_shadow'].append((168, 189, LANE))


def draw_spices(im, reg):
    """D：香料店。"""
    d = ImageDraw.Draw(im)
    x0, x1 = 198, 246
    d = shop_opening(im, reg, x0, x1, 114, inner=(96, 72, 54), night_open=False)
    shelves(d, x0 + 2, x1 - 2, 120, 134, 104, [(200, 150, 80), (150, 90, 50), (226, 200, 120), (180, 60, 40),
                                                  (110, 130, 70), (230, 230, 220)], 4)
    for xx in range(x0 + 3, x1 - 2, 6):                              # 门楣上挂的丝瓜络 / 小篮子
        L = 3 + int(hash01(xx, 9) * 4)
        vl(d, xx, 114, 114 + L, (206, 190, 140) if xx % 4 else (176, 130, 80))
        px(d, xx, 115 + L, (226, 210, 160))
    piles = [((200, 60, 40), 0), ((236, 186, 40), 1), ((96, 130, 60), 2), ((150, 92, 52), 3), ((214, 120, 50), 4),
             ((120, 70, 40), 5), ((226, 210, 160), 6)]
    for i, (c, s) in enumerate(piles):                                # 一袋袋香料：麻袋口卷下来 + 堆成尖
        cx = x0 + 4 + i * 7
        rect(d, cx - 3, 137, cx + 3, LANE - 1, (196, 172, 124))
        hl(d, cx - 3, cx + 3, 137, (220, 200, 156))
        vl(d, cx + 3, 138, LANE - 1, (160, 136, 96))
        for r in range(4):
            hl(d, cx - 3 + r, cx + 3 - r, 136 - r, c if r else dk(c, 0.9))
        px(d, cx - 1, 134, lt(c, 0.3))
        px(d, cx, 133, lt(c, 0.2))
    sign_board(d, 200, 105, 244, 110, (60, 40, 30), (240, 200, 90), 105)


def draw_hotel(im, reg):
    """E：旅馆（x 252–346）。"""
    x0, x1 = 252, 346
    col = WALL['cream']
    hi, md, sh, kk = P.wall_pal(col)
    d = P.plaster(im, x0, x1, 64, LANE - 1, col, 15, streaks=2, cell=5, damp=5, cracks=2)
    # 一楼粗石面：横缝 + 错开的竖缝
    for y in range(108, LANE - 1, 5):
        hl(d, x0, x1 - 1, y, dk(col, 0.8))
        hl(d, x0, x1 - 1, y + 1, lt(col, 0.2))
        for xx in range(x0 + (6 if (y // 5) % 2 else 0), x1, 12):
            vl(d, xx, y - 4, y - 1, dk(col, 0.84))
    rect(d, x0, GF - 1, x1 - 1, GF + 1, lt(col, 0.18))
    hl(d, x0, x1 - 1, GF - 2, lt(col, 0.4))
    hl(d, x0, x1 - 1, GF + 2, dk(col, 0.74))
    # 壁柱（二楼、三楼）
    for xx in (253, 274, 296, 318, 343):
        rect(d, xx, 68, xx + 1, GF - 3, lt(col, 0.2))
        vl(d, xx + 2, 68, GF - 3, dk(col, 0.86))
    # 二楼：法式窗 + 铁阳台（F-03 众人从这一排窗户翻下来）
    for bx in (260, 282, 304, 326):
        x = bx
        rect(d, x - 2, 83, x + 11, 101, lt(col, 0.25))
        hl(d, x - 3, x + 12, 82, lt(col, 0.45))
        hl(d, x - 3, x + 12, 81, dk(col, 0.8))
        window(im, reg, x, 85, 10, 14, col, 'b', SHUT['green'], 151 + x)
    # 三楼：百叶窗
    for i, bx in enumerate((261, 283, 305, 327)):
        window(im, reg, bx, 70, 8, 10, col, 'oco h'[i % 4] if i != 3 else 'h', SHUT['green'], 171 + bx)
    d = ImageDraw.Draw(im)
    # 一楼：拱窗 + 铁花格
    for wx in (258, 314, 330):
        rect(d, wx - 2, 113, wx + 11, 137, lt(col, 0.28))
        rect(d, wx, 117, wx + 9, 135, DARK_IN)
        for xx in range(wx, wx + 10):
            r = abs(xx - wx - 4.5) / 5.0
            for yy in range(117, 117 + int(round(3 * (1 - math.sqrt(max(0.0, 1 - r * r)))))):
                px(d, xx, yy, lt(col, 0.28))
        for xx in range(wx + 1, wx + 9, 2):
            vl(d, xx, 118, 134, IRON)
        hl(d, wx, wx + 9, 126, IRON)
        for xx in range(wx + 1, wx + 9, 2):
            px(d, xx, 125, IRON_HI)
        hl(d, wx - 2, wx + 11, 138, lt(col, 0.42))
        mul_box(im, (wx - 1, 139, wx + 12, 139), SHADOW_MUL)
        reg['win'].append((wx, 118, 10, 17, 'g', 300 + wx))
    d = ImageDraw.Draw(im)
    # 正门：半圆拱 + 双扇木门（上半玻璃）+ 两级台阶
    ex0, ex1, spring = 282, 299, 120
    rect(d, ex0 - 3, 110, ex1 + 3, LANE - 1, lt(col, 0.3))
    for xx in range(ex0 - 3, ex1 + 4):
        r = (xx - (ex0 + ex1) / 2.0) / ((ex1 - ex0) / 2.0 + 3)
        top = spring - int(round(9 * math.sqrt(max(0.0, 1 - r * r))))
        vl(d, xx, top, spring, lt(col, 0.3))
    for xx in range(ex0, ex1 + 1):
        r = (xx - (ex0 + ex1) / 2.0) / ((ex1 - ex0) / 2.0)
        top = spring - int(round(7 * math.sqrt(max(0.0, 1 - r * r))))
        vl(d, xx, top, LANE - 3, (80, 56, 40))
        for yy in range(top, spring):                                 # 扇形气窗
            ang = math.atan2(spring - yy, xx - (ex0 + ex1) / 2.0)
            if abs(((math.degrees(ang) + 180) % 30) - 15) > 11:
                px(d, xx, yy, (226, 214, 180))
            else:
                px(d, xx, yy, (60, 70, 90))
    hl(d, ex0, ex1, spring, (226, 214, 180))
    mid = (ex0 + ex1) // 2
    for xx in range(ex0, ex1 + 1):
        for yy in range(spring + 1, LANE - 3):
            c = (120, 80, 50)
            if xx in (ex0, mid, mid + 1, ex1):
                c = (92, 60, 38)
            elif spring + 3 <= yy <= spring + 12 and xx not in (ex0 + 1, mid - 1, mid + 2, ex1 - 1):
                c = (70, 86, 100)                                    # 门上的玻璃
            elif yy in (spring + 2, spring + 13, LANE - 6):
                c = (150, 104, 66)
            px(d, xx, yy, c)
    px(d, mid - 2, spring + 16, (220, 180, 90))
    px(d, mid + 3, spring + 16, (220, 180, 90))
    reg['shop'].append((ex0 + 1, spring + 3, ex1 - 1, spring + 12, True))
    rect(d, ex0 - 4, LANE - 2, ex1 + 4, LANE - 1, (214, 206, 190))  # 台阶
    hl(d, ex0 - 4, ex1 + 4, LANE - 2, (236, 230, 216))
    rect(d, ex0 - 2, LANE - 4, ex1 + 2, LANE - 3, (204, 196, 180))
    hl(d, ex0 - 2, ex1 + 2, LANE - 4, (228, 222, 208))
    # 门楣的牌子 + 两盏铜壁灯
    rect(d, 279, 105, 302, 109, (40, 76, 60))
    hl(d, 279, 302, 105, (90, 130, 100))
    text3(d, 281, 105, 'HOTEL', (226, 196, 110))
    bracket_lamp(d, reg, 277, 112, face=-1, col=(150, 110, 50))
    bracket_lamp(d, reg, 304, 112, face=1, col=(150, 110, 50))
    # 檐口（顶 y 64 = hotel_roof：鸟停在这里）+ 栏杆
    cornice(im, x0, x1, 64, col, depth=4, dent=True)
    d = ImageDraw.Draw(im)
    hl(d, x0, x1 - 1, 58, lt(col, 0.3))
    hl(d, x0, x1 - 1, 59, md)
    for xx in range(x0 + 1, x1 - 1, 3):
        vl(d, xx, 60, 63, md)
        px(d, xx, 61, lt(col, 0.25))
        px(d, xx + 1, 60, sh)
    vl(d, x0, 58, 63, md)
    vl(d, x1 - 1, 58, 63, sh)
    # 屋顶的 HOTEL 字架（角钢架子 + 红字白边；夜里是霓虹，见 neon strip）
    for xx in (260, 276, 292):
        vl(d, xx, 54, 57, IRON)
    hl(d, 258, 296, 55, IRON)
    for i, ch in enumerate('HOTEL'):
        g = FONT3[ch]
        bx = 258 + i * 8
        for r, row in enumerate(g):
            for c_, v in enumerate(row):
                if v == '1':
                    rect(d, bx + c_ * 2, 43 + r * 2, bx + c_ * 2 + 1, 43 + r * 2 + 1, (206, 52, 48))
    hl(d, 336, 340, 57, (120, 120, 116))                             # 旗杆座（杆子在 draw_antennas）


def draw_cafe(im, reg):
    """F：咖啡馆（ahwa）。"""
    d = ImageDraw.Draw(im)
    x0, x1 = 350, 390
    d = shop_opening(im, reg, x0, x1, 113, inner=(92, 70, 54))
    rect(d, x0 + 1, 116, x1 - 1, 128, (110, 84, 62))                 # 后墙：上半刷绿、下半木墙裙
    rect(d, x0 + 1, 116, x1 - 1, 121, (70, 110, 90))
    hl(d, x0 + 1, x1 - 1, 122, (60, 44, 32))
    for xx in range(x0 + 3, x1 - 1, 4):
        vl(d, xx, 123, 128, (96, 72, 52))
    rect(d, 356, 117, 362, 121, (200, 180, 130))                     # 墙上的相框
    rect(d, 357, 118, 361, 120, (90, 70, 60))
    rect(d, 381, 116, 388, 121, (40, 40, 44))                        # 墙上架子上的电视（夜里闪，见 tv strip）
    rect(d, 382, 117, 387, 120, (90, 110, 120))
    px(d, 384, 122, (40, 40, 44))
    for (lx, ly) in ((365, 114), (376, 114)):                        # 吊着的铜灯笼
        vl(d, lx, ly, ly + 2, (70, 60, 50))
        rect(d, lx - 1, ly + 3, lx + 1, ly + 6, (200, 150, 70))
        px(d, lx, ly + 4, (250, 220, 150))
        reg['lamp'].append((lx, ly + 4, 'inner'))
    for (tx, sx) in ((358, 1), (372, 1), (384, -1)):                  # 店里的小桌 + 椅子 + 水烟壶
        hl(d, tx - 3, tx + 3, 134, (170, 170, 176))
        vl(d, tx, 135, LANE - 1, (110, 110, 116))
        hl(d, tx - 2, tx + 2, LANE - 1, (110, 110, 116))
        cx = tx - 6 * sx
        vl(d, cx, 133, LANE - 1, (120, 84, 52))
        hl(d, cx, cx + 2 * sx, 138, (140, 100, 62)) if sx > 0 else hl(d, cx - 2, cx, 138, (140, 100, 62))
    P.shisha(d, 366, LANE - 1)
    lay = A._new(PW, H)                                              # 两个坐着喝茶的背景人（压灰，读成背景）
    dl = ImageDraw.Draw(lay)
    P.person(dl, 362, 138, 'tea', 61, h=24, face=1, ground=LANE - 1)
    P.person(dl, 379, 138, 'smoke', 62, h=24, face=-1, ground=LANE - 1)
    lay = haze(A._grade(lay, sat=0.7), 0.22, (150, 120, 96))
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    sign_board(d, 350, 105, 390, 110, (40, 110, 80), (244, 240, 226), 106)
    for cx in (348, 392):                                            # 门外靠墙的两把木椅（人行道后沿）
        vl(d, cx, 136, LANE, (130, 90, 56))
        vl(d, cx + (2 if cx < 370 else -2), 140, LANE, (110, 76, 46))
        hl(d, min(cx, cx + (2 if cx < 370 else -2)), max(cx, cx + (2 if cx < 370 else -2)), 140, (156, 112, 70))
        reg['ground_shadow'].append((cx - 1, cx + 2, LANE))


def draw_mirrors(im, reg):
    """G：镜子店：墙上挂满镜子（反着天的颜色 + 一道白光），门边靠着几块玻璃。"""
    d = ImageDraw.Draw(im)
    x0, x1 = 405, 433
    d = shop_opening(im, reg, x0, x1, 114, inner=(84, 70, 64), night_open=False)
    for (mx, my, mw, mh, kind) in ((408, 118, 6, 9, 'r'), (417, 117, 5, 7, 'o'), (425, 119, 6, 8, 'r'),
                                    (410, 130, 4, 6, 'o'), (420, 128, 8, 6, 'r')):
        _mirror(d, mx, my, mw, mh, kind, inside=True)
    for (mx, my, mw, mh, kind) in ((397, 112, 5, 8, 'o'), (396, 123, 6, 10, 'r'), (436, 111, 6, 7, 'o'),
                                    (436, 121, 6, 11, 'r'), (398, 136, 4, 5, 'o')):
        _mirror(d, mx, my, mw, mh, kind)
    for (gx, gw, gh) in ((435, 6, 14), (439, 4, 11)):               # 门边靠墙的玻璃板（人行道后沿）
        for i in range(gw):
            yy0 = LANE - 1 - gh + i // 2
            vl(d, gx + i, yy0, LANE - 1, mix((150, 184, 196), (196, 220, 228), i / max(1, gw - 1)))
        vl(d, gx, LANE - 1 - gh, LANE - 1, (110, 130, 140))
        px(d, gx + 2, LANE - gh + 1, (250, 252, 252))
    sign_board(d, 403, 105, 435, 110, (230, 220, 190), (60, 50, 110), 107)


def _mirror(d, x, y, w, h, kind, inside=False):
    fr = (176, 136, 70) if kind == 'o' else (120, 80, 50)
    sky = (146, 186, 214) if not inside else (110, 130, 140)
    if kind == 'o':
        d.ellipse((x - 1, y - 1, x + w, y + h), fill=C(fr))
        d.ellipse((x, y, x + w - 1, y + h - 1), fill=C(sky))
    else:
        rect(d, x - 1, y - 1, x + w, y + h, fr)
        rect(d, x, y, x + w - 1, y + h - 1, sky)
    px(d, x + 1, y + 1, (246, 250, 252))
    px(d, x + 2, y + 2, (220, 236, 246))
    if h > 6:
        px(d, x + w - 2, y + h - 3, lt(sky, 0.3))


def draw_fruit_stand(im, reg, wrecked=False):
    """H 门前的水果摊。wrecked = 被卡车撞翻（板车翻倒、筐散了、水果滚了一地）。"""
    d = ImageDraw.Draw(im)
    # 后面的果汁店（被摊子挡住一半）
    d = shop_opening(im, reg, 450, 496, 114, inner=(88, 70, 58), night_open=False)
    rect(d, 451, 120, 495, 124, (230, 226, 210))                     # 墙上的果汁价目板
    P.sign_ar(d, 452, 120, 494, 124, None, (60, 90, 60), seed=108, rows=1)
    for xx in range(453, 494, 5):                                    # 吊着的网兜水果
        vl(d, xx, 114, 116, (90, 80, 60))
        px(d, xx, 117, (244, 160, 40) if xx % 2 else (120, 170, 60))
    sign_board(d, 452, 105, 494, 109, (240, 200, 60), (120, 40, 30), 109)
    # 布篷（钉在墙上，两根木杆撑着前沿）
    P.awning(im, STAND[0], STAND[1], 110, 5, (60, 140, 90), (240, 238, 228), stripe=4, scallop=True, shadow=3)
    d = ImageDraw.Draw(im)
    for xx in (STAND[0] + 1, STAND[1] - 1):
        vl(d, xx, 116, LANE, (130, 96, 60))
        vl(d, xx + 1, 116, LANE, (100, 72, 46))
    if not wrecked:
        for i, xx in enumerate(range(452, 466, 4)):                  # 挂着的香蕉
            vl(d, xx, 116, 118, (90, 70, 40))
            for k in range(4):
                hl(d, xx - 1, xx + 1, 119 + k, (236, 206, 70) if k % 2 else (214, 180, 50))
            px(d, xx + 1, 123, (120, 100, 40))
        vl(d, 478, 116, 119, (80, 80, 80))                           # 秤
        hl(d, 474, 482, 120, (80, 80, 80))
        rect(d, 473, 121, 476, 122, (170, 170, 170))
        rect(d, 480, 121, 483, 122, (170, 170, 170))
        # 板车：木板 + 两个轮子 + 车把
        rect(d, 452, 133, 492, 136, (150, 104, 62))
        hl(d, 452, 492, 133, (196, 150, 98))
        hl(d, 452, 492, 136, (100, 68, 42))
        for wx in (460, 484):
            d.ellipse((wx - 5, LANE - 10, wx + 5, LANE), outline=C((70, 50, 36)))
            d.ellipse((wx - 4, LANE - 9, wx + 4, LANE - 1), outline=C((110, 78, 50)))
            px(d, wx, LANE - 5, (70, 50, 36))
            for a_ in range(0, 360, 60):
                px(d, wx + int(round(3 * math.cos(math.radians(a_)))), LANE - 5 + int(round(3 * math.sin(math.radians(a_)))),
                   (110, 78, 50))
        d.line((452, 135, 446, 141), fill=C((130, 92, 56)))
        # 筐 + 堆成山的水果
        _fruit_heap(d, 455, 470, 132, 7, (255, 170, 50), 1)
        _fruit_heap(d, 472, 489, 132, 6, (232, 200, 60), 2)
        _fruit_heap(d, 466, 477, 127, 4, (250, 130, 40), 3)
        for i in range(3):                                           # 车边一摞西瓜
            cx = 494 + (i % 2) * 2
            cy = LANE - 3 - i * 4
            d.ellipse((cx - 3, cy - 2, cx + 3, cy + 2), fill=C((60, 120, 60)))
            px(d, cx - 1, cy - 1, (120, 170, 90))
            px(d, cx + 1, cy, (40, 90, 40))
        reg['ground_shadow'].append((452, 494, LANE))
        bulb(d, reg, 470, 118)
    else:
        bulb(d, reg, 470, 118)
        # 翻倒的板车：整辆车往前翻、侧躺着，车板竖起来（看得见底下的横档），一个轮子朝天、一个压在下面；车把翘起来
        wood, wood_d, wood_hi = (150, 104, 62), (100, 68, 42), (196, 150, 98)
        d.polygon([(452, LANE - 1), (458, 124), (464, 124), (460, LANE - 1)], fill=C(wood))
        d.line((452, LANE - 1, 458, 124), fill=C(wood_hi))
        d.line((460, LANE - 1, 464, 124), fill=C(wood_d))
        for k in range(3):                                           # 车板底下的横档
            y = 130 + k * 5
            hl(d, 455 + (LANE - y) // 6, 461 + (LANE - y) // 6, y, wood_d)
        d.line((462, 124, 476, 116), fill=C(wood_d))                 # 翘起来的车把
        d.line((462, 125, 476, 117), fill=C(wood))
        for (wx, wy, r) in ((470, 128, 5), (466, LANE - 4, 4)):       # 一个轮子朝天（悬着）、一个压在下面
            d.ellipse((wx - r, wy - r, wx + r, wy + r), outline=C((70, 50, 36)))
            d.ellipse((wx - r + 1, wy - r + 1, wx + r - 1, wy + r - 1), outline=C((110, 78, 50)))
            px(d, wx, wy, (70, 50, 36))
            for a_ in range(0, 360, 60):
                px(d, wx + int(round((r - 2) * math.cos(math.radians(a_)))), wy + int(round((r - 2) * math.sin(math.radians(a_)))),
                   (110, 78, 50))
        for (cx, up) in ((478, False), (490, True)):                 # 摔散的木筐（一个扣着、一个散了架）
            if up:
                rect(d, cx - 4, LANE - 6, cx + 4, LANE - 1, (176, 136, 88))
                for xx in range(cx - 3, cx + 4, 2):
                    vl(d, xx, LANE - 5, LANE - 1, (140, 104, 64))
                hl(d, cx - 4, cx + 4, LANE - 6, (206, 170, 120))
            else:
                d.line((cx - 5, LANE - 1, cx + 1, LANE - 6), fill=C((176, 136, 88)))
                d.line((cx - 2, LANE - 1, cx + 5, LANE - 4), fill=C((150, 112, 70)))
                hl(d, cx - 6, cx + 6, LANE - 1, (140, 104, 64))
        for i in range(46):                                          # 滚了一地的橘子 / 芒果（2 px 一颗，越靠摊子越密）
            u = hash01(i, 43) ** 1.6
            x = int(440 + u * 90 + hrange(-6, 6, 41, i))
            y = int(hrange(LANE, 167, 42, i))
            if CURB <= y <= CURB + 1:
                y += 2
            c = (255, 156, 36) if i % 3 else (232, 204, 64)
            rect(d, x, y, x + 1, y + 1, c)
            px(d, x, y, lt(c, 0.4))
            px(d, x + 1, y + 1, dk(c, 0.72))
        for (x, y) in ((500, 150), (507, 156), (494, 160)):          # 摔碎的西瓜
            hl(d, x, x + 4, y, (226, 56, 66))
            hl(d, x + 1, x + 3, y - 1, (240, 90, 96))
            hl(d, x, x + 4, y + 1, (52, 116, 56))
            px(d, x + 2, y, (40, 30, 30))


def _fruit_heap(d, x0, x1, base, hgt, col, seed):
    for r in range(hgt):
        a = x0 + r
        b = x1 - r
        for x in range(a, b + 1):
            c = col if (x + r) % 2 else dk(col, 0.86)
            if hash01(seed, x, r) < 0.18:
                c = lt(col, 0.35)
            px(d, x, base - r, c)
    hl(d, x0 - 1, x1 + 1, base + 1, (120, 84, 50))


def draw_garage(im, reg):
    """I：修车铺。"""
    d = ImageDraw.Draw(im)
    x0, x1 = 508, 552
    d = shop_opening(im, reg, x0, x1, 112, inner=(56, 50, 50), night_open=False)
    rect(d, x0 + 1, 114, x1 - 1, 128, (70, 64, 62))
    for i, xx in enumerate(range(x0 + 4, x1 - 6, 5)):                # 墙上挂的扳手
        vl(d, xx, 116, 121 + (i % 3), (150, 150, 156))
        px(d, xx - 1, 116, (150, 150, 156))
        px(d, xx + 1, 116, (150, 150, 156))
    rect(d, 540, 115, 547, 121, (220, 216, 200))                     # 挂历
    rect(d, 541, 116, 546, 118, (200, 80, 70))
    # 修了一半的旧车（只露出车尾，车里暗）
    d.polygon([(511, 140), (511, 131), (516, 127), (530, 127), (533, 131), (533, 140)], fill=C((176, 60, 50)))
    hl(d, 516, 529, 127, (214, 110, 96))
    rect(d, 518, 129, 528, 131, (60, 66, 76))
    hl(d, 511, 533, 136, (120, 40, 36))
    rect(d, 511, 134, 513, 135, (250, 190, 80))
    d.ellipse((514, 139, 520, LANE - 1), fill=C((34, 32, 34)))
    d.ellipse((526, 139, 532, LANE - 1), fill=C((34, 32, 34)))
    px(d, 517, 142, (140, 140, 140))
    px(d, 529, 142, (140, 140, 140))
    vl(d, 540, 130, LANE - 1, (120, 120, 60))                        # 千斤顶 + 工具箱
    rect(d, 542, 138, 549, LANE - 1, (180, 60, 40))
    hl(d, 542, 549, 138, (220, 100, 70))
    sign_board(d, 510, 105, 550, 109, (240, 210, 60), (40, 40, 40), 110)
    d.ellipse((544, 104, 549, 109), fill=C((40, 40, 40)))            # 招牌上的轮胎
    px(d, 546, 106, (240, 210, 60))
    for k in range(4):                                               # 门口一摞旧轮胎
        y = LANE - 1 - k * 4
        d.ellipse((502, y - 3, 511, y), fill=C((40, 38, 40)))
        hl(d, 504, 509, y - 3, (80, 78, 80))
        px(d, 506, y - 2, (24, 24, 26))
    reg['ground_shadow'].append((502, 511, LANE))


def draw_sweets(im, reg):
    """J：甜点铺（玻璃柜里一盘盘甜点）。"""
    d = ImageDraw.Draw(im)
    x0, x1 = 563, 607
    d = shop_opening(im, reg, x0, x1, 114, inner=(96, 70, 60))
    shelves(d, x0 + 2, x1 - 2, 121, 128, 111, [(240, 230, 210), (220, 170, 80), (200, 80, 80), (240, 200, 120)], 4)
    rect(d, x0, 130, x1, LANE - 1, (170, 180, 186))                  # 玻璃柜
    rect(d, x0 + 1, 131, x1 - 1, LANE - 4, (150, 176, 186))
    for y, c in ((133, (226, 170, 80)), (137, (240, 210, 150)), (141, (200, 130, 60))):
        for xx in range(x0 + 2, x1 - 2, 6):
            hl(d, xx, xx + 4, y, c)
            px(d, xx + 1, y - 1, lt(c, 0.3))
            px(d, xx + 3, y - 1, (90, 150, 70) if y == 133 else lt(c, 0.2))
    hl(d, x0 + 1, x1 - 1, 131, (226, 236, 240))
    hl(d, x0, x1, LANE - 3, (120, 100, 80))
    sign_board(d, 563, 105, 607, 110, (170, 40, 40), (240, 210, 110), 112)


def draw_k_ground(im, reg):
    d = ImageDraw.Draw(im)
    d = shop_opening(im, reg, 672, 686, 115, inner=(80, 66, 60), night_open=False)
    for i, xx in enumerate(range(673, 686, 3)):                      # 修鞋小铺：挂着的鞋
        vl(d, xx, 115, 117, (70, 60, 50))
        rect(d, xx - 1, 118, xx, 121, ((130, 70, 40), (40, 40, 44), (170, 120, 80))[i % 3])
    rect(d, 673, 136, 685, LANE - 1, (120, 84, 56))
    hl(d, 673, 685, 136, (160, 120, 80))
    rect(d, 670, 105, 688, 110, (240, 236, 220))
    P.sign_ar(d, 670, 105, 688, 110, None, (40, 40, 120), seed=113)


def draw_l_ground(im, reg):
    """L：药房 + 收音机店。"""
    d = ImageDraw.Draw(im)
    # 药房：白框玻璃门面
    x0, x1 = 714, 757
    rect(d, x0 - 1, 113, x1 + 1, LANE - 1, (236, 236, 230))
    d = shop_opening(im, reg, x0, x1, 114, inner=(150, 176, 180))
    rect(d, x0 + 1, 116, x1 - 1, LANE - 2, (176, 200, 204))
    shelves(d, x0 + 2, x1 - 2, 120, 140, 114, [(240, 240, 240), (200, 80, 80), (80, 140, 200), (240, 220, 120),
                                                  (120, 190, 140)], 4)
    for xx in (x0 + 14, x0 + 29):
        vl(d, xx, 114, LANE - 1, (236, 236, 230))
    hl(d, x0, x1, 132, (236, 236, 230))
    px(d, x0 + 3, 117, (250, 252, 252))
    px(d, x0 + 4, 118, (230, 240, 244))
    rect(d, 716, 104, 724, 112, (240, 240, 236))                     # 绿十字灯箱
    rect(d, 719, 105, 721, 111, (40, 160, 90))
    rect(d, 717, 107, 723, 109, (40, 160, 90))
    rect(d, 726, 105, 757, 111, (240, 240, 236))
    text3(d, 727, 106, 'PHARMACY', (40, 140, 80))
    # 收音机店
    x0, x1 = 764, 808
    d = shop_opening(im, reg, x0, x1, 114, inner=(70, 60, 58), night_open=False)
    for (rx, ry, rw, rh, c) in ((766, 120, 10, 6, (150, 110, 70)), (778, 119, 8, 7, (60, 60, 64)),
                                 (788, 121, 9, 5, (170, 160, 150)), (799, 118, 7, 8, (110, 80, 56)),
                                 (767, 128, 12, 8, (50, 50, 54)), (781, 129, 8, 7, (180, 170, 160)),
                                 (791, 128, 14, 9, (60, 56, 56))):
        rect(d, rx, ry, rx + rw - 1, ry + rh - 1, c)
        hl(d, rx, rx + rw - 1, ry, lt(c, 0.3))
        if rw >= 9:                                                   # 喇叭网 / 屏幕
            rect(d, rx + 1, ry + 2, rx + rw // 2, ry + rh - 2, dk(c, 0.7) if c[0] > 100 else (90, 110, 120))
        px(d, rx + rw - 2, ry + 2, (220, 200, 120))
    rect(d, x0 + 1, 138, x1 - 1, LANE - 1, (110, 80, 56))
    hl(d, x0 + 1, x1 - 1, 138, (150, 112, 76))
    for xx in range(x0 + 3, x1 - 3, 3):                              # 柜台上一排磁带
        rect(d, xx, 136, xx + 1, 137, ((200, 60, 60), (60, 60, 200), (230, 230, 230), (230, 180, 60))[xx % 4])
    sign_board(d, 764, 105, 808, 110, (40, 70, 140), (244, 244, 236), 115)


def draw_corner(im, reg, crashed=False, truck=False):
    """M：转角楼（x 814–906），屋顶边 y 70；右边削角。crashed = 一楼被撞开的洞；truck = 黎明：洞里扎着那辆卡车。"""
    x0, x1 = 814, 906
    col = WALL['stone']
    hi, md, sh, kk = P.wall_pal(col)
    d = P.plaster(im, x0, x1 - 8, 70, LANE - 1, col, 23, streaks=3, cell=4, damp=6, cracks=4)
    P.plaster(im, x1 - 8, x1, 72, LANE - 1, dk(col, 0.84), 24, streaks=1, cell=3, damp=6, cracks=1, edges=False)
    d = ImageDraw.Draw(im)
    for y in range(74, LANE - 1, 4):                                 # 削角上的隅石
        hl(d, x1 - 8, x1 - 1 - (2 if (y // 4) % 2 else 0), y, dk(col, 0.7))
    vl(d, x1 - 8, 72, LANE - 1, lt(col, 0.25))
    vl(d, x1 - 1, 72, LANE - 1, dk(col, 0.55))
    rect(d, x1 - 7, 96, x1 - 2, 100, (40, 80, 150))                  # 蓝色搪瓷街名牌
    hl(d, x1 - 7, x1 - 2, 96, (220, 230, 240))
    px(d, x1 - 5, 98, (240, 240, 240))
    px(d, x1 - 3, 98, (240, 240, 240))
    hl(d, x0, x1 - 9, GF - 1, lt(col, 0.3))
    rect(d, x0, GF, x1 - 9, GF + 1, dk(col, 0.93))
    hl(d, x0, x1 - 9, GF + 2, dk(col, 0.8))
    # 屋顶边 y 70：中间一段（846–880）没有矮墙，人站在檐口上；两头一小段矮墙
    cornice(im, x0, x1 - 8, 70, col, depth=3, dent=True)
    d = ImageDraw.Draw(im)
    for (a, b_) in ((x0, 830), (884, x1 - 9)):
        rect(d, a, 66, b_, 69, md)
        hl(d, a, b_, 66, lt(col, 0.3))
        vl(d, b_, 66, 69, sh)
    hl(d, x1 - 8, x1 - 1, 71, lt(col, 0.2))
    # 两层窗（层高 15–16）
    for k, (yt, kinds) in enumerate(((88, 'ocbo'), (73, 'hooc'))):
        if k == 0:
            hl(d, x0, x1 - 9, yt - 1, dk(col, 0.9))
        for i, bx in enumerate((822, 842, 862, 882)):
            kind = kinds[i]
            if kind == 'b':
                window(im, reg, bx, yt + 1, 8, 12, col, 'b', SHUT['brown'], 230 + i + k * 10)
            else:
                window(im, reg, bx, yt + 2, 8, 9, col, kind, SHUT['brown'], 230 + i + k * 10)
    d = ImageDraw.Draw(im)
    # 一楼：杂货铺
    gx0, gx1 = 818, 896
    d = shop_opening(im, reg, gx0, gx1, 113, inner=(90, 74, 60), night_open=not (crashed or truck))   # 撞了就断电
    shelves(d, gx0 + 2, gx1 - 2, 119, 134, 116, [(220, 200, 150), (200, 60, 50), (60, 120, 190), (240, 220, 90),
                                                    (130, 160, 80), (240, 240, 230), (150, 90, 50)], 5)
    for i, xx in enumerate(range(gx0 + 3, gx1 - 2, 7)):              # 门楣上挂的塑料桶 / 扫帚
        vl(d, xx, 113, 115, (70, 60, 50))
        c = ((220, 60, 60), (60, 140, 220), (240, 200, 60), (90, 180, 90))[i % 4]
        rect(d, xx - 1, 116, xx + 1, 119, c)
        hl(d, xx - 1, xx + 1, 116, lt(c, 0.3))
    for i, cx in enumerate(range(gx0 + 4, gx1 - 3, 7)):              # 门口一排米袋 / 豆子袋
        c = ((236, 226, 200), (200, 150, 80), (220, 190, 120), (170, 110, 60))[i % 4]
        rect(d, cx - 3, 138, cx + 3, LANE - 1, (200, 180, 136))
        hl(d, cx - 3, cx + 3, 138, (226, 210, 170))
        hl(d, cx - 2, cx + 2, 137, c)
        px(d, cx, 136, lt(c, 0.2))
    rect(d, gx1 - 6, 128, gx1 - 1, LANE - 1, (200, 60, 50))          # 汽水箱
    for yy in range(130, LANE - 1, 4):
        hl(d, gx1 - 5, gx1 - 2, yy, (60, 40, 30))
        px(d, gx1 - 4, yy - 1, (90, 140, 90))
    sign_board(d, 820, 105, 894, 110, (230, 200, 60), (180, 40, 30), 117, rows=1)
    # 屋顶：左边水箱、右边天线（中间留空：rooftop 站人）
    water_tank(im, 816, 66, w=14, h=9, legs=3)
    if crashed or truck:
        _crash_hole(im, truck)


def _crash_hole(im, truck):
    """转角楼一楼被卡车撞开的洞：参差的墙洞（里面黑、断砖、垂下来的电线、断木梁）+ 地上散的碎砖、玻璃。
    truck = 黎明：洞里扎着那辆卡车（车头没进墙里，只露出后半截，样子照道具 truck：棕色车身、蓝窗）。"""
    d = ImageDraw.Draw(im)
    x0, x1 = CRASH
    rng = [(x, int(CRASH_TOP + 4 * hash01(x // 2, 71) + (3 if x0 + 6 < x < x1 - 6 else 8) *
                   (abs(x - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 2)) for x in range(x0, x1 + 1)]
    for (x, top) in rng:
        vl(d, x, top, LANE - 1, (34, 28, 30))
        vl(d, x, top - 1, top - 1, (120, 96, 80))                    # 断口：抹灰下露出的砖
        if hash01(x, 72) < 0.5:
            px(d, x, top - 2, (160, 110, 84))
    for (x, top) in rng[::5]:
        if x0 + 2 < x < x1 - 2:
            vl(d, x, top, top + int(hrange(2, 7, x, 73)), (70, 56, 50))
    d.line((x0 + 6, CRASH_TOP + 8, x0 + 20, CRASH_TOP + 20), fill=C((96, 70, 46)))    # 断木梁
    d.line((x1 - 10, CRASH_TOP + 6, x1 - 4, CRASH_TOP + 22), fill=C((96, 70, 46)))
    P.wire(d, x0 + 14, CRASH_TOP + 3, x0 + 30, CRASH_TOP + 3, 9, col=(20, 20, 22))   # 垂下来的电线
    for i in range(36):                                              # 洞边墙面的裂纹
        a = hrange(0, math.tau, 74, i)
        r = hrange(2, 9, 75, i)
        x = int((x0 + x1) / 2 + math.cos(a) * ((x1 - x0) / 2 + r))
        y = int(CRASH_TOP + 16 + math.sin(a) * (16 + r * 0.6))
        if CRASH_TOP - 8 < y < LANE - 2:
            px(d, x, y, (120, 104, 90))
    for i in range(90):                                              # 碎砖 / 灰块（平的，落在人行道和路上）
        x = int(hrange(x0 - 16, x1 + 18, 76, i))
        y = int(hrange(LANE - 6, 166, 77, i))
        if y < LANE and x0 + 2 < x < x1 - 2:
            continue
        c = (176, 112, 84) if i % 3 else (206, 196, 170)
        px(d, x, y, c)
        if i % 4 == 0:
            px(d, x + 1, y, dk(c, 0.8))
            px(d, x, y - 1, lt(c, 0.2))
    for i in range(10):                                              # 碎玻璃的亮点
        x = int(hrange(x0 - 10, x1 + 10, 78, i))
        y = int(hrange(LANE + 1, 160, 79, i))
        px(d, x, y, (220, 236, 240))
    # 洞口的一堆碎砖（人行道上，低于 8 px）
    for k in range(5):
        hl(d, x0 + 4 + k, x1 - 4 - k, LANE - 1 - k // 2, (150, 104, 80) if k % 2 else (186, 170, 146))
    if truck:
        _truck_crashed(im)


def _truck_crashed(im):
    """黎明：撞进转角楼的卡车（道具 truck 的样子：棕色车身、货斗、蓝色车窗）——车头扎进墙洞，后半截斜着露在外面，
    后轮离地一点；车身上的凹痕、碎掉的尾灯。"""
    d = ImageDraw.Draw(im)
    body, body_d, body_hi = (168, 92, 52), (120, 62, 36), (204, 132, 84)
    x0, x1 = 822, 868                                                # 露在外面的后半截
    for x in range(x0, x1):
        u = (x - x0) / (x1 - x0)
        top = int(round(126 - 4 * u))
        bot = int(round(139 - 3 * u))
        vl(d, x, top, bot, body)
        px(d, x, top, body_hi)
        px(d, x, bot, body_d)
        if x % 6 == 0:
            vl(d, x, top + 2, bot - 2, body_d)                       # 货斗的木板缝
    hl(d, x0, x0 + 3, 128, (230, 60, 40))                             # 碎尾灯
    px(d, x0 + 1, 127, (250, 120, 90))
    vl(d, x0, 126, 139, body_d)
    for (wx, wy) in ((832, 141), (858, 138)):                        # 轮子
        d.ellipse((wx - 5, wy - 5, wx + 5, wy + 5), fill=C((36, 34, 36)))
        d.ellipse((wx - 2, wy - 2, wx + 2, wy + 2), fill=C((150, 150, 150)))
        px(d, wx, wy, (80, 80, 80))
    rect(d, 862, 116, 868, 124, (70, 110, 150))                       # 驾驶室的后窗（一半在墙里）
    hl(d, 862, 868, 116, (130, 170, 200))
    d.line((863, 118, 866, 122), fill=C((210, 230, 240)))
    for i in range(6):                                               # 车身上的凹痕
        px(d, int(hrange(x0 + 4, x1 - 4, 81, i)), int(hrange(128, 136, 82, i)), body_d)
    # 墙洞右边的断墙压在车头上（车头看不见）
    for y in range(CRASH_TOP + 2, LANE - 1):
        w_ = 2 + int(3 * hash01(y // 2, 83))
        hl(d, 868, 868 + w_, y, (180, 168, 140) if y % 3 else (150, 110, 84))
        px(d, 868, y, (90, 70, 60))


def draw_cross_street(im, reg):
    """X：路口往里退的横街（x 612–668）。一点透视：消失点 (640, VP_Y)；左墙（J 的侧面，背光）、右墙（K 的侧面，受光）、
    尽头一栋小楼（罩一点雾）、街面。"""
    d = ImageDraw.Draw(im)
    xa, xb = CROSS
    vx = (xa + xb) / 2.0
    fl, fr_ = 628, 652                                               # 尽头小楼的左右（远处的街宽）

    def yat(y_near, x_near, x):
        return VP_Y + (y_near - VP_Y) * (x - vx) / (x_near - vx)
    jt, kt = top_of(3), top_of(4)
    far_top = int(round(yat(jt, xa, fl))) + 1
    far_base = int(round(yat(LANE - 1, xa, fl)))
    # 尽头小楼（远，罩雾）
    fc = mix(WALL['sand'], (226, 214, 194), 0.35)
    rect(d, fl, far_top, fr_, far_base, fc)
    for y in range(far_top + 4, far_base - 8, 9):
        for xx in range(fl + 2, fr_ - 2, 6):
            rect(d, xx, y, xx + 2, y + 4, mix(DARK_IN, fc, 0.35))
            reg['win'].append((xx, y, 3, 5, 'f', xx * 7 + y))
    rect(d, fl + 4, far_base - 8, fr_ - 4, far_base, mix((90, 70, 60), fc, 0.3))   # 一楼小店
    rect(d, fl + 3, far_base - 11, fr_ - 3, far_base - 9, mix((200, 60, 50), fc, 0.3))
    hl(d, fl, fr_, far_top, lt(fc, 0.2))
    # 街面（梯形）
    for y in range(far_base + 1, LANE):
        u = (y - far_base) / max(1, LANE - 1 - far_base)
        a = int(round(fl - (fl - xa) * u))
        b_ = int(round(fr_ + (xb - fr_) * u))
        hl(d, a, b_, y, mix(mix(ROAD_C, (226, 214, 194), 0.3), ROAD_C, u))
        if y % 4 == 0:
            px(d, int(vx), y, (200, 196, 184))                        # 褪色的中线
    # 两边的侧墙（每一列从顶线画到底线）
    for (x_near, top_near, col, lit, seed) in ((xa, jt, WALL['rose'], False, 51), (xb, kt, WALL['cream'], True, 52)):
        xf = fl if x_near == xa else fr_
        step = 1 if xf > x_near else -1
        cc = col if lit else dk(col, 0.72)
        for x in range(x_near, xf + step, step):
            t_ = int(round(yat(top_near, x_near, x)))
            bt = int(round(yat(LANE - 1, x_near, x)))
            vl(d, x, t_, bt, cc)
            px(d, x, t_, lt(cc, 0.3) if lit else dk(cc, 0.8))
            u = (x - x_near) / float(xf - x_near)
            for k in range(1, 6):                                    # 层线（往消失点收）
                yy = int(round(yat(GF + 1 - (k - 1) * FH, x_near, x)))
                if t_ < yy < bt:
                    px(d, x, yy, dk(cc, 0.86))
            # 窗：每层两扇，越远越窄
            for k in range(1, 5):
                yt_, yb_ = floor_band(k)
                if yt_ < top_near + 3:
                    continue
                for (ua, ub) in ((0.12, 0.3), (0.5, 0.64)):
                    if ua <= u <= ub:
                        wy0 = int(round(yat(yt_ + 3, x_near, x)))
                        wy1 = int(round(yat(yt_ + 13, x_near, x)))
                        vl(d, x, wy0, wy1, DARK_IN if not lit else dk(DARK_IN, 1.0))
                        if abs(u - ua) < 0.03 or abs(u - ub) < 0.03:
                            vl(d, x, wy0, wy1, (60, 100, 76) if lit else (40, 60, 50))
            if 0.2 <= u <= 0.75:                                    # 一楼的店门
                gy0 = int(round(yat(116, x_near, x)))
                vl(d, x, gy0, bt - 1, (70, 56, 50) if lit else (50, 40, 38))
    reg['xs'] = (fl, fr_, far_top, far_base)


def draw_alley(im, reg):
    """AL：窄巷（x 690–710）：两边墙往里收、巷底一扇门 + 两级台阶，很暗；头顶的晾衣绳在 strip。"""
    d = ImageDraw.Draw(im)
    xa, xb = ALLEY
    vx = (xa + xb) / 2.0
    fl, fr_ = 697, 703

    def yat(y_near, x_near, x):
        return VP_Y + (y_near - VP_Y) * (x - vx) / (x_near - vx)
    kt, lt_ = top_of(4), top_of(3)
    far_top = int(round(yat(kt, xa, fl)))
    far_base = int(round(yat(LANE - 1, xa, fl)))
    rect(d, fl, far_top, fr_, far_base, (96, 82, 76))                # 巷底的墙
    rect(d, fl + 1, far_base - 9, fr_ - 1, far_base - 2, (52, 40, 38))   # 门
    hl(d, fl, fr_, far_base - 1, (130, 120, 108))
    hl(d, fl - 1, fr_ + 1, far_base, (110, 100, 90))
    rect(d, fl + 2, far_top + 6, fr_ - 2, far_top + 10, (70, 60, 56))
    reg['win'].append((fl + 2, far_top + 6, 3, 5, 'f', 7001))
    for y in range(far_base + 1, LANE):
        u = (y - far_base) / max(1, LANE - 1 - far_base)
        a = int(round(fl - (fl - xa) * u))
        b_ = int(round(fr_ + (xb - fr_) * u))
        hl(d, a, b_, y, mix((96, 88, 80), (150, 140, 126), u))
        for xx in range(a, b_ + 1, 3):
            if (xx + y) % 2:
                px(d, xx, y, mix((80, 72, 66), (130, 120, 108), u))   # 石板缝
    for (x_near, top_near, col, seed) in ((xa, kt, WALL['cream'], 53), (xb, lt_, WALL['lsand'], 54)):
        xf = fl - 1 if x_near == xa else fr_ + 1
        step = 1 if xf > x_near else -1
        for x in range(x_near, xf + step, step):
            t_ = int(round(yat(top_near, x_near, x)))
            bt = int(round(yat(LANE - 1, x_near, x)))
            cc = dk(col, 0.5 if x_near == xa else 0.6)
            vl(d, x, t_, bt, cc)
            px(d, x, t_, dk(cc, 0.8))
            for k in range(1, 5):
                yy = int(round(yat(GF + 1 - (k - 1) * FH, x_near, x)))
                if t_ < yy < bt:
                    px(d, x, yy, dk(cc, 0.85))
    bracket_lamp(d, reg, 692, 104, face=1, col=(44, 46, 46))
    # 巷口睡着一只猫（人行道后沿）
    cat = (196, 150, 96)
    hl(d, 711, 716, LANE - 2, cat)
    hl(d, 712, 715, LANE - 3, lt(cat, 0.2))
    px(d, 716, LANE - 3, cat)
    px(d, 717, LANE - 4, cat)
    px(d, 716, LANE - 4, dk(cat, 0.7))
    hl(d, 708, 710, LANE - 1, dk(cat, 0.8))


def draw_side_street(im, reg):
    """N：转角楼后面的小横街（x 906–920，很暗）。"""
    d = ImageDraw.Draw(im)
    xa, xb = SIDEST
    vx = (xa + xb) / 2.0
    fl, fr_ = 911, 915

    def yat(y_near, x_near, x):
        return VP_Y + (y_near - VP_Y) * (x - vx) / (x_near - vx)
    far_top = int(round(yat(72, xa, fl)))
    far_base = int(round(yat(LANE - 1, xa, fl)))
    rect(d, fl, far_top, fr_, far_base, (120, 104, 92))
    for y in range(far_base + 1, LANE):
        u = (y - far_base) / max(1, LANE - 1 - far_base)
        hl(d, int(round(fl - (fl - xa) * u)), int(round(fr_ + (xb - fr_) * u)), y, mix((110, 100, 90), ROAD_C, u))
    for (x_near, top_near, col) in ((xa, 72, dk(WALL['stone'], 0.62)), (xb, 78, dk((226, 214, 186), 0.7))):
        xf = fl - 1 if x_near == xa else fr_ + 1
        step = 1 if xf > x_near else -1
        for x in range(x_near, xf + step, step):
            t_ = int(round(yat(top_near, x_near, x)))
            bt = int(round(yat(LANE - 1, x_near, x)))
            vl(d, x, t_, bt, col)
            px(d, x, t_, dk(col, 0.8))


def draw_mosque(im, reg):
    """清真寺（x 920–960）：红白相间的条纹石墙（ablaq）、阶梯垛口、尖拱大门 + 钟乳石檐、门里的灯、后面的肋纹石穹顶、
    右上的宣礼塔（P.minaret）。"""
    x0, x1 = MOSQUE
    stone = (226, 212, 180)
    red = (186, 104, 76)
    d = ImageDraw.Draw(im)
    # 穹顶（在墙后面，先画）：鼓座 + 肋纹石穹顶 + 顶上的新月
    cx, base, r = 932, 76, 11
    rect(d, cx - r - 1, base - 6, cx + r + 1, base, dk(stone, 0.9))
    for xx in range(cx - r - 1, cx + r + 2, 3):
        vl(d, xx, base - 5, base - 2, dk(stone, 0.6))
    for xx in range(cx - r, cx + r + 1):
        u = (xx - cx) / float(r)
        top = base - 6 - int(round(r * 1.25 * math.sqrt(max(0.0, 1 - u * u))))
        for yy in range(top, base - 6):
            c = stone if u < 0.2 else dk(stone, 0.8)
            if u < -0.5:
                c = lt(stone, 0.2)
            if (xx - cx + 40 + (yy // 2)) % 4 == 0:                   # 肋纹
                c = dk(c, 0.82)
            px(d, xx, yy, c)
    vl(d, cx, base - 6 - int(r * 1.25) - 5, base - 6 - int(r * 1.25), (200, 170, 90))
    px(d, cx - 1, base - 6 - int(r * 1.25) - 6, (220, 190, 90))
    px(d, cx + 1, base - 6 - int(r * 1.25) - 6, (220, 190, 90))
    # 宣礼塔
    P.minaret(im, 951, 78, 6, 10, stone, seed=5)
    d = ImageDraw.Draw(im)
    # 墙：上半素石、下半红白条纹；顶上阶梯垛口
    top = 78
    rect(d, x0, top, x1 - 1, LANE - 1, stone)
    for y in range(GF - 6, LANE - 1):
        if ((y - (GF - 6)) // 3) % 2:
            hl(d, x0, x1 - 1, y, red)
    for y in range(top + 2, LANE - 1, 3):
        for xx in range(x0 + ((y // 3) % 2) * 4, x1, 8):
            px(d, xx, y, dk(stone, 0.86) if y < GF - 6 else dk(red, 0.8))
    for xx in range(x0, x1, 6):                                      # 阶梯垛口
        rect(d, xx + 1, top - 4, xx + 4, top - 1, stone)
        rect(d, xx + 2, top - 6, xx + 3, top - 5, stone)
        px(d, xx + 1, top - 4, lt(stone, 0.3))
        vl(d, xx + 4, top - 4, top - 1, dk(stone, 0.75))
    hl(d, x0, x1 - 1, top, lt(stone, 0.3))
    hl(d, x0, x1 - 1, top + 1, dk(stone, 0.8))
    vl(d, x0, top, LANE - 1, lt(stone, 0.2))
    # 尖拱大门：凹进去的门龛（暗）+ 钟乳石檐 + 木门（铁钉）+ 门里一盏灯
    gx0, gx1, spring = 926, 946, 106
    for xx in range(gx0, gx1 + 1):
        u = abs(xx - (gx0 + gx1) / 2.0) / ((gx1 - gx0) / 2.0)
        apex = spring - int(round(14 * (1 - u) ** 0.8))
        vl(d, xx, apex, LANE - 1, dk(stone, 0.62))
        px(d, xx, apex, lt(stone, 0.2) if u > 0.3 else dk(stone, 0.5))
    for k in range(3):                                               # 钟乳石（一层层往下的小龛）
        y = spring - 6 + k * 3
        for xx in range(gx0 + 3 + k, gx1 - 2 - k, 3):
            px(d, xx, y, lt(stone, 0.3))
            px(d, xx + 1, y + 1, dk(stone, 0.5))
    rect(d, 931, 120, 941, LANE - 1, (96, 64, 40))
    for xx in range(931, 942, 2):
        vl(d, xx, 120, LANE - 1, (110, 76, 48))
    for yy in range(122, LANE - 1, 4):
        for xx in (932, 935, 938, 940):
            px(d, xx, yy, (180, 160, 110))
    vl(d, 936, 120, LANE - 1, (70, 46, 30))
    vl(d, 936, spring - 4, 111, (60, 50, 40))
    rect(d, 935, 112, 937, 115, (200, 160, 70))
    px(d, 936, 113, (250, 230, 160))
    reg['lamp'].append((936, 113, 'inner'))
    rect(d, gx0 - 1, LANE - 2, gx1 + 1, LANE - 1, (214, 206, 186))  # 门槛石
    for (wx, wy) in ((923, 116), (950, 116)):                       # 两扇小尖窗（铜格）
        rect(d, wx, wy, wx + 4, wy + 9, DARK_IN)
        px(d, wx, wy, stone)
        px(d, wx + 4, wy, stone)
        vl(d, wx + 2, wy + 1, wy + 9, (150, 120, 60))
        hl(d, wx, wx + 4, wy + 5, (150, 120, 60))
        reg['win'].append((wx, wy + 1, 5, 9, 'g', wx))


def draw_ground(im):
    """人行道（146–152 方砖）+ 路缘石（153 亮 / 154 暗）+ 柏油路（155–179）。横街那段没有人行道（路面接进横街）。"""
    d = ImageDraw.Draw(im)
    rect(d, 0, LANE, PW - 1, CURB - 1, SIDE_C)
    for y in (LANE + 3, CURB - 1):                                   # 方砖缝（横）
        hl(d, 0, PW - 1, y, SIDE_D)
    for band, (ya, yb) in enumerate(((LANE, LANE + 2), (LANE + 4, CURB - 2))):
        off = 4 * band
        for x in range(off, PW, 8):
            vl(d, x, ya, yb, SIDE_D)
            k = hash01(x, band, 31)
            if k < 0.12:
                rect(d, x + 1, ya, x + 7, yb, mix(SIDE_C, (170, 150, 120), 0.35))   # 补过的 / 脏的砖
            elif k > 0.9:
                rect(d, x + 1, ya, x + 7, yb, SIDE_HI)
            elif 0.5 < k < 0.53:
                d.line((x + 2, ya, x + 5, yb), fill=C(SIDE_D))          # 裂缝
    hl(d, 0, PW - 1, LANE, mix(SIDE_C, (90, 76, 70), 0.35))          # 墙脚的暗线
    hl(d, 0, PW - 1, LANE + 1, mix(SIDE_C, (90, 76, 70), 0.12))
    for x in range(PW):                                              # 路缘石：一段段长石条，顶亮立面暗
        seg = x // 9
        hl(d, x, x, CURB, CURB_HI if seg % 2 else CURB_MID)
        px(d, x, CURB + 1, CURB_FACE)
        if x % 9 == 0:
            px(d, x, CURB, mix(CURB_MID, CURB_FACE, 0.5))
    rect(d, 0, ROAD0, PW - 1, H - 1, ROAD_C)
    mottle(im, (0, ROAD0, PW - 1, H - 1), ROAD_C, ROAD_D, ROAD_HI, 301, cell=9, lo=0.26, hi=0.74)
    d = ImageDraw.Draw(im)
    hl(d, 0, PW - 1, ROAD0, mix(ROAD_C, (90, 84, 80), 0.25))          # 路缘石脚的影
    for i in range(26):                                              # 柏油补丁（深一点的不规则块）
        x = int(hrange(0, PW - 30, 302, i))
        y = int(hrange(ROAD0 + 3, H - 4, 303, i))
        w = int(hrange(8, 26, 304, i))
        h_ = int(hrange(2, 4, 305, i))
        for yy in range(y, min(H, y + h_)):
            a = x + int(hash01(i, yy, 306) * 3)
            hl(d, a, a + w - int(hash01(i, yy, 307) * 4), yy, mix(ROAD_C, (120, 114, 108), 0.4))
    for i in range(40):                                              # 细裂缝
        x = int(hrange(0, PW, 308, i))
        y = int(hrange(ROAD0 + 2, H - 3, 309, i))
        for k in range(int(hrange(3, 9, 310, i))):
            px(d, x + k, y + (1 if hash01(i, k, 311) < 0.3 else 0), mix(ROAD_C, (100, 94, 90), 0.3))
    for ty in (163, 171):                                            # 车辙（淡淡的两道）
        for x in range(PW):
            if hash01(x // 11, ty, 312) < 0.7:
                px(d, x, ty + (1 if math.sin(x * 0.02 + ty) > 0.6 else 0), mix(ROAD_C, ROAD_D, 0.6))
    for i in range(70):                                              # 路上的小纸片 / 石子
        x = int(hrange(0, PW, 313, i))
        y = int(hrange(ROAD0 + 1, H - 1, 314, i))
        px(d, x, y, mix(ROAD_C, (214, 208, 196), 0.6) if i % 3 else mix(ROAD_C, (130, 120, 110), 0.6))
    # 横街：人行道和路缘石断开，路面接进去；路口地上褪色的斑马线
    xa, xb = CROSS
    rect(d, xa, LANE, xb, CURB + 1, ROAD_C)
    mottle(im, (xa, LANE, xb, CURB + 1), ROAD_C, ROAD_D, ROAD_HI, 315, cell=7, lo=0.3, hi=0.7)
    d = ImageDraw.Draw(im)
    for (x, s) in ((xa, 1), (xb, -1)):                               # 路缘石转进横街的那个角
        vl(d, x, LANE, CURB + 1, CURB_FACE)
        px(d, x - s, CURB, CURB_HI)
    for y in range(157, H - 1, 4):
        for x in range(xa + 4, xb - 3):
            if hash01(x // 3, y, 316) < 0.82:
                px(d, x, y, mix(ROAD_C, (226, 222, 210), 0.45))
                px(d, x, y + 1, mix(ROAD_C, (226, 222, 210), 0.3))
    # 修车铺门口的油渍（平的）
    for i in range(8):                                              # 剧情放油桶（x 515–525）的地方不画，免得和剧情的油混
        cx = int(hrange(504, 556, 317, i))
        if 510 <= cx <= 530:
            cx += 22
        cy = int(hrange(LANE + 1, CURB - 2, 318, i))
        rx = int(hrange(2, 5, 319, i))
        for yy in range(cy - 1, cy + 2):
            for xx in range(cx - rx, cx + rx + 1):
                if hash01(xx, yy, 320) < 0.7:
                    c = im.getpixel((xx, yy))[:3]
                    px(d, xx, yy, dk(c, 0.86))
    # 排水栅（sewer_grate 760,170：伊奇钻进去的那个）
    gx, gy = ANCHORS['sewer_grate']
    rect(d, gx - 9, gy - 3, gx + 9, gy + 2, (96, 86, 78))
    rect(d, gx - 8, gy - 2, gx + 8, gy + 1, (28, 26, 28))
    for xx in range(gx - 7, gx + 8, 2):
        vl(d, xx, gy - 2, gy + 1, (110, 92, 76))
    hl(d, gx - 9, gx + 9, gy - 3, (150, 140, 128))
    px(d, gx - 3, gy - 1, (150, 100, 70))
    px(d, gx + 4, gy, (150, 100, 70))
    # 一个井盖
    d.ellipse((182, 166, 196, 170), fill=C((128, 122, 116)))
    hl(d, 185, 193, 168, (110, 104, 100))
    hl(d, 185, 193, 166, (150, 144, 136))


def draw_road_sign(im, reg, gone=False):
    """路牌（road_sign 580）：红圆禁行牌（白横杠）+ 杆子上一块蓝色街名牌（阿拉伯文 + 英文的样子）。样子照道具 road_sign
    （8×25：红圆在顶、深灰杆），DIO 拔走它时剧情换成道具。gone = 拔走了：人行道上一个坑 + 掀起来的砖。"""
    d = ImageDraw.Draw(im)
    x = SIGN_X
    if gone:
        rect(d, x - 3, LANE, x + 3, LANE + 3, (60, 50, 44))
        rect(d, x - 2, LANE + 1, x + 2, LANE + 3, (34, 28, 26))
        for (dx, dy, c) in ((-5, 0, (170, 150, 120)), (5, 1, (186, 170, 146)), (-4, 4, (150, 130, 104)),
                            (6, 4, (196, 186, 166)), (8, 2, (120, 100, 80))):
            px(d, x + dx, LANE + dy, c)
            px(d, x + dx + 1, LANE + dy, dk(c, 0.8))
        hl(d, x - 4, x + 4, LANE + 4, mix(SIDE_C, (90, 76, 70), 0.4))
        px(d, x + 12, LANE + 2, (150, 150, 156))                      # 坑边掉的一颗螺丝（纪念品在 road_sign+12）
        px(d, x + 13, LANE + 2, (96, 96, 104))
        return
    pole = (66, 66, 72)
    vl(d, x, SIGN_TOP + 7, SIGN_FOOT, pole)
    vl(d, x + 1, SIGN_TOP + 8, SIGN_FOOT, dk(pole, 0.7))
    d.ellipse((x - 4, SIGN_TOP, x + 3, SIGN_TOP + 7), fill=C((206, 40, 40)), outline=C((120, 20, 24)))
    hl(d, x - 2, x + 1, SIGN_TOP + 3, (246, 244, 240))
    hl(d, x - 2, x + 1, SIGN_TOP + 4, (246, 244, 240))
    px(d, x - 3, SIGN_TOP + 1, (236, 110, 100))
    rect(d, x - 6, SIGN_TOP + 10, x + 6, SIGN_TOP + 15, (40, 84, 150))     # 蓝色街名牌
    hl(d, x - 6, x + 6, SIGN_TOP + 10, (220, 230, 240))
    hl(d, x - 6, x + 6, SIGN_TOP + 15, (220, 230, 240))
    for k in range(5):
        px(d, x - 4 + k * 2, SIGN_TOP + 12, (240, 240, 240))
    hl(d, x - 4, x + 4, SIGN_TOP + 13, (200, 210, 230))
    hl(d, x - 1, x + 2, SIGN_FOOT, (110, 110, 116))
    reg['ground_shadow'].append((x - 1, x + 1, SIGN_FOOT + 1))


def draw_wires(im):
    """头顶的电线（近景层，y 20–70，在对白框后面也不要紧）。"""
    d = ImageDraw.Draw(im)
    for (x0, y0, x1, y1, sag) in ((0, 40, 130, 36, 8), (126, 38, 258, 46, 7), (250, 34, 350, 64, 5),
                                  (394, 58, 520, 40, 9), (512, 44, 640, 36, 12), (640, 34, 760, 50, 10),
                                  (760, 46, 818, 57, 4), (600, 54, 700, 50, 14)):
        P.wire(d, x0, y0, x1, y1, sag, col=(64, 60, 64))


ANTENNAS = ((52, top_of(3), 14, 1), (118, top_of(2), 18, 2), (138, top_of(3), 12, 3), (206, top_of(4), 13, 4),
            (494, top_of(4), 12, 5), (434, top_of(2), 15, 6), (604, top_of(3), 16, 7), (680, top_of(4), 12, 8),
            (800, top_of(3), 15, 10), (898, 70, 16, 9))


def draw_roofs(im):
    """楼顶的东西：水箱、楼梯间小屋（天线在 draw_antennas，描边之后画）。"""
    water_tank(im, 6, top_of(3), w=13, h=8)
    roof_hut(im, 70, 88, top_of(2) - 1, top_of(2) - 11, WALL['sage'], 61)
    water_tank(im, 160, top_of(3), w=15, h=9)
    water_tank(im, 226, top_of(4), w=13, h=8)
    water_tank(im, 452, top_of(4), w=14, h=9)
    water_tank(im, 566, top_of(3), w=13, h=8)
    water_tank(im, 720, top_of(3), w=14, h=9)
    water_tank(im, 772, top_of(3), w=12, h=8)


def draw_antennas(im):
    d = ImageDraw.Draw(im)
    for (x, base, h, sd) in ANTENNAS:
        antenna(d, x, base, h, seed=sd)
    vl(d, 338, 30, 57, (200, 200, 196))                              # 旅馆的旗杆（旗子在 strip）
    px(d, 338, 29, (230, 200, 90))
    vl(d, 375, 34, top_of(1) - 3, (176, 150, 96))                      # 鸽舍边的竹竿 + 破布
    rect(d, 376, 35, 380, 38, (200, 60, 60))
    px(d, 380, 39, (170, 50, 50))


def draw_pigeon_loft(im):
    """F 屋顶的鸽舍（木条搭的塔 + 网 + 顶上一根挂破布的竹竿）。鸽子在 strip。"""
    d = ImageDraw.Draw(im)
    x0, x1, base, top = 353, 371, top_of(1), 52
    for xx in (x0, x1):
        vl(d, xx, top + 6, base, (120, 90, 60))
    vl(d, x0 + 1, top + 6, base, (150, 116, 78))
    for y in range(top + 10, base - 6, 6):                           # 横木（鸽子落脚）
        hl(d, x0, x1, y, (140, 104, 66))
        hl(d, x0, x1, y + 1, (100, 72, 46))
    rect(d, x0 + 2, top + 12, x1 - 2, base - 8, (110, 90, 70))       # 网笼（暗）
    for y in range(top + 12, base - 8, 2):
        for xx in range(x0 + 2 + (y // 2) % 2, x1 - 1, 2):
            px(d, xx, y, (150, 130, 100))
    d.polygon([(x0 - 2, top + 7), ((x0 + x1) // 2, top), (x1 + 2, top + 7)], fill=C((150, 100, 64)))   # 小尖顶
    hl(d, x0 - 2, x1 + 2, top + 7, (100, 68, 44))
    # 屋顶矮墙
    rect(d, 346, base - 3, 393, base - 1, WALL['yellow'])
    hl(d, 346, 393, base - 3, lt(WALL['yellow'], 0.3))


def draw_billboard(im):
    """I 屋顶的手绘电影海报（80 年代开罗街头那种：一张大脸 + 女主角 + 红黄的片名）。"""
    d = ImageDraw.Draw(im)
    x0, x1, y0, y1 = 507, 553, 42, 74
    base = top_of(1)
    for xx in (510, 530, 550):                                       # 铁架
        vl(d, xx, y1, base, IRON)
    d.line((510, y1 + 2, 530, base - 1), fill=C(IRON))
    d.line((530, y1 + 2, 550, base - 1), fill=C(IRON))
    rect(d, x0, y0, x1, y1, (60, 40, 40))
    gradient(im, (x0 + 1, y0 + 1, x1, y1), [(250, 170, 60), (220, 80, 50), (110, 30, 50)], bands=6)
    d = ImageDraw.Draw(im)
    d.ellipse((513, 47, 531, 70), fill=C((214, 150, 110)))           # 男主角的大脸（墨镜）
    rect(d, 515, 55, 530, 58, (30, 26, 30))
    hl(d, 516, 529, 54, (60, 50, 50))
    d.pieslice((511, 44, 533, 60), 180, 360, fill=C((40, 30, 30)))
    hl(d, 518, 526, 64, (150, 70, 60))
    d.ellipse((534, 52, 547, 68), fill=C((236, 180, 150)))           # 女主角
    d.pieslice((532, 48, 549, 66), 180, 360, fill=C((70, 40, 30)))
    vl(d, 532, 56, 70, (70, 40, 30))
    px(d, 538, 60, (40, 30, 30))
    px(d, 543, 60, (40, 30, 30))
    hl(d, 539, 542, 64, (200, 60, 70))
    P.sign_ar(d, x0 + 3, y1 - 6, x1 - 3, y1 - 1, None, (250, 230, 90), seed=121)
    rect(d, x0, y0, x1, y1, None, outline=(240, 230, 200))
    hl(d, x0, x1, y0, (255, 246, 220))


def ac_unit(d, x, y):
    """窗式空调（80 年代开罗楼上已经有不少）：米色铁盒 + 格栅 + 底下一道滴水的水渍。(x, y) = 左上，9 × 6。"""
    c = (214, 206, 186)
    rect(d, x, y, x + 8, y + 5, c)
    hl(d, x, x + 8, y, lt(c, 0.3))
    vl(d, x + 8, y, y + 5, dk(c, 0.75))
    for xx in range(x + 1, x + 5):
        vl(d, xx, y + 1, y + 4, dk(c, 0.8) if xx % 2 else c)
    rect(d, x + 5, y + 1, x + 7, y + 4, dk(c, 0.88))
    hl(d, x, x + 8, y + 5, dk(c, 0.6))
    vl(d, x + 6, y + 6, y + 11, (170, 150, 120))                      # 滴水的水渍


def clinic_sign(d, x0, y0, x1, y1, seed, col=(40, 90, 160)):
    """挂在阳台栏杆上的诊所牌子（白底蓝字 + 一道红线），开罗街上很常见。"""
    rect(d, x0, y0, x1, y1, (244, 242, 236), outline=(150, 150, 150))
    P.sign_ar(d, x0 + 1, y0, x1 - 1, y1 - 2, None, col, seed=seed)
    hl(d, x0 + 1, x1 - 1, y1 - 1, (200, 50, 50))
    vl(d, x0 + 2, y0 - 2, y0, IRON)
    vl(d, x1 - 2, y0 - 2, y0, IRON)


def birdcage(d, x, y):
    """窗边挂的鸟笼：小穹顶 + 竖条 + 里面一只黄色的金丝雀。(x, y) = 挂钩。"""
    vl(d, x, y, y + 1, IRON)
    hl(d, x - 2, x + 2, y + 2, (200, 170, 90))
    for xx in range(x - 3, x + 4, 2):
        vl(d, xx, y + 3, y + 8, (200, 170, 90))
    hl(d, x - 3, x + 3, y + 8, (170, 140, 70))
    px(d, x, y + 6, (250, 220, 60))
    px(d, x + 1, y + 5, (250, 220, 60))


def carpet(d, x0, x1, y0, y1, seed):
    """搭在阳台栏杆上晾的地毯：红底、深蓝边、中间一个菱形花、底下一排穗子。"""
    rect(d, x0, y0, x1, y1, (170, 44, 48))
    rect(d, x0, y0, x1, y1, None, outline=(40, 50, 100))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for k in range(4):
        hl(d, cx - k, cx + k, cy - 3 + k, (230, 190, 100))
        hl(d, cx - k, cx + k, cy + 3 - k, (230, 190, 100))
    for xx in range(x0 + 2, x1 - 1, 4):
        px(d, xx, y0 + 2, (230, 190, 100))
        px(d, xx, y1 - 2, (230, 190, 100))
    for xx in range(x0, x1 + 1, 2):
        px(d, xx, y1 + 1, (236, 226, 200))


def sill_plant(d, x, y, seed):
    """窗台上一小盆花（罗勒 / 天竺葵）。(x, y) = 盆底。"""
    pc = (190, 96, 66) if hash01(seed, 1) < 0.5 else (230, 230, 220)
    rect(d, x, y - 2, x + 2, y, pc)
    px(d, x, y - 3, (60, 120, 60))
    px(d, x + 1, y - 4, (80, 150, 70))
    px(d, x + 2, y - 3, (60, 120, 60))
    if hash01(seed, 2) < 0.6:
        px(d, x + 1, y - 5, (220, 70, 90))


def wall_cable(d, x, y0, y1, boxes=()):
    """顺着墙走的黑电线 + 几个接线盒。"""
    vl(d, x, y0, y1, (50, 46, 46))
    for y in boxes:
        rect(d, x - 1, y, x + 1, y + 2, (150, 150, 140))
        px(d, x, y + 1, (60, 60, 60))


def draw_life(im):
    """楼上的生活小物件：窗式空调、诊所牌子、鸟笼、晾的地毯、窗台花盆、墙上的电线。"""
    d = ImageDraw.Draw(im)
    for (x, k) in ((154, 1), (489, 2), (797, 1), (581, 3), (218, 4), (28, 2)):
        yt, yb = floor_band(k)
        ac_unit(d, x - 1, yt + 9)
    clinic_sign(d, 732, 92, 750, 99, 131)
    clinic_sign(d, 772, 92, 788, 99, 132, col=(30, 110, 60))
    clinic_sign(d, 398, 73, 414, 80, 133)
    birdcage(d, 40, floor_band(1)[0] + 2)
    birdcage(d, 591, floor_band(2)[0] + 2)
    yt, yb = floor_band(2)
    carpet(d, 752, 768, yb, yb + 11, 134)
    for (x, k, sd) in ((10, 3, 1), (450, 1, 2), (564, 2, 3), (718, 3, 4), (200, 2, 5), (680, 1, 6), (843, 0, 7)):
        if k:
            yt, yb = floor_band(k)
            sill_plant(d, x + 2, yt + 15, sd)
    wall_cable(d, 65, top_of(3) + 4, GF - 3, boxes=(70, 96))
    wall_cable(d, 344, 66, GF - 3, boxes=(90,))
    wall_cable(d, 709, top_of(3) + 6, GF - 3, boxes=(60, 88))


def ground_shadows(im, reg):
    """白天：太阳在左上，人行道后沿的东西往右下落一道短影；楼脚一条窄影。"""
    for (a, b, y) in reg['ground_shadow']:
        P.soft_shadow(im, a, b, y, depth=2, slant=3, mul=SHADOW_MUL)
    for x in LAMPS_X:
        cast_shadow(im, [(x + 1, LANE + 1), (x + 3, LANE + 1), (x + 11, CURB - 1), (x + 9, CURB - 1)], mul=SOFT_MUL)
    cast_shadow(im, [(SIGN_X + 1, LANE + 2), (SIGN_X + 2, LANE + 2), (SIGN_X + 9, CURB - 1), (SIGN_X + 8, CURB - 1)],
                mul=SOFT_MUL)


@lru_cache(maxsize=8)
def street_albedo(dmg=()):
    """整条街的固有色（不带太阳的地面投影）+ 记下来的窗 / 灯 / 店面。dmg ⊂ {'wrecked', 'sign_gone', 'crashed', 'truck'}。"""
    reg = dict(win=[], lamp=[], shop=[], ground_shadow=[])
    im = A._new(PW, H)
    draw_cross_street(im, reg)
    draw_alley(im, reg)
    draw_side_street(im, reg)
    for b in BLD:
        wall_block(im, b)
        upper_floors(im, reg, b)
    draw_hotel(im, reg)
    draw_corner(im, reg, crashed='crashed' in dmg, truck='truck' in dmg)
    draw_mosque(im, reg)
    draw_kiosk(im, reg)
    draw_b_ground(im, reg)
    draw_bakery(im, reg)
    draw_spices(im, reg)
    draw_cafe(im, reg)
    draw_mirrors(im, reg)
    draw_garage(im, reg)
    draw_sweets(im, reg)
    draw_k_ground(im, reg)
    draw_l_ground(im, reg)
    draw_life(im)
    draw_roofs(im)
    draw_pigeon_loft(im)
    draw_billboard(im)
    draw_ground(im)
    draw_fruit_stand(im, reg, wrecked='wrecked' in dmg)
    draw_road_sign(im, reg, gone='sign_gone' in dmg)
    for x in LAMPS_X:
        lamp_post(im, reg, x)
    if 'crashed' in dmg or 'truck' in dmg:
        # 撞墙的碎砖要盖在地面上（draw_corner 时地面还没画）
        _crash_debris_ground(im)
    im = P.outer_rim(im, INK, y1=LANE)
    draw_antennas(im)
    draw_wires(im)
    P.compress_band(im, 112, LANE, (150, 130, 112), amt=0.1, ramp=10)
    return im, reg


def _crash_debris_ground(im):
    d = ImageDraw.Draw(im)
    x0, x1 = CRASH
    for i in range(90):
        x = int(hrange(x0 - 16, x1 + 18, 76, i))
        y = int(hrange(LANE, 166, 77, i))
        c = (176, 112, 84) if i % 3 else (206, 196, 170)
        px(d, x, y, c)
        if i % 4 == 0:
            px(d, x + 1, y, dk(c, 0.8))
    for i in range(10):
        px(d, int(hrange(x0 - 10, x1 + 10, 78, i)), int(hrange(LANE + 1, 160, 79, i)), (220, 236, 240))
    for k in range(4):
        hl(d, x0 + 6 + k * 2, x1 - 6 - k * 2, LANE + 1 - k, (150, 104, 80) if k % 2 else (186, 170, 146))
    for i in range(14):                                              # 冲出来的大块碎砖（≤ 3 px 高）
        x = int(hrange(x0 - 6, x1 + 14, 84, i))
        y = int(hrange(LANE + 2, 162, 85, i))
        rect(d, x, y, x + 2, y + 1, (170, 110, 84))
        hl(d, x, x + 2, y, (206, 150, 116))


# ============================================================ 夜：点灯
LIT_P = 0.5
DAWN_OPEN = ((132, 186), (283, 298))      # 黎明还开着的：面包店（烤早上的饼）、旅馆门厅
DAWN_LAMPS_OFF = (98 + 6, 238 + 6, 548 + 6)   # 黎明已经关了 / 坏了的路灯（238 那盏在 lamp_flicker strip 里闪）


def light_night(g, alb, reg, tod='night', lit_p=LIT_P, ground_light=True):
    """夜 / 黎明（g = 已经压暗的近景，alb = 固有色）：窗户一部分亮（暖黄 + 窗帘的影）、开着的店里用固有色 × 暖光
    （货架、饼、药瓶的细节都在）、路灯 / 壁灯的光圈（灯头最亮、墙上一圈、地上一片）。ground_light = False 时
    不画地上的光（自检拿这一版量可走带平不平：光圈是光，不是东西）。"""
    a = np.array(g).astype(np.float32)
    al = np.array(alb).astype(np.float32)
    wl = LIGHT_WARM
    for (x, y, w, h, kind, seed) in reg['win']:
        q = hash01(seed, 77)
        if q >= lit_p:
            continue
        if kind == 'f':
            a[y:y + h, x:x + w, :3] = np.array(mix(wl, (200, 140, 80), 0.3), np.float32)
            continue
        hot = mix(wl, (255, 240, 200), 0.3) if q < lit_p * 0.4 else mix(wl, (230, 160, 90), 0.35)
        if kind in ('o', 'a', 'b', 'g'):
            for yy in range(y, y + h):
                u = (yy - y) / max(1, h - 1)
                row = a[yy, x:x + w]
                keep = row[..., 3] > 0
                row[keep, :3] = np.array(mix(hot, dk(hot, 0.82), u), np.float32)
            cur = np.array(mix(hot, (150, 80, 50), 0.55), np.float32)
            a[y:y + h, x, :3] = cur
            a[y:y + h, x + w - 1, :3] = cur
            if kind != 'g':
                a[y + 1:y + h, x + w // 2, :3] = np.array(mix(hot, (120, 70, 40), 0.6), np.float32)
            else:
                for xx in range(x + 1, x + w - 1, 2):
                    a[y + 1:y + h, xx, :3] = np.array((60, 44, 40), np.float32)
            if hash01(seed, 78) < 0.18 and h >= 10:                 # 窗里一个人影
                cx = x + w // 2 - 1
                a[y + h - 6:y + h, cx:cx + 3, :3] = np.array((70, 44, 36), np.float32)
                a[y + h - 8:y + h - 6, cx + 1, :3] = np.array((70, 44, 36), np.float32)
        elif kind == 'h':
            hw = w // 2
            a[y:y + h, x + hw:x + w, :3] = np.array(hot, np.float32)
            for yy in range(y + 1, y + h - 1, 2):
                a[yy, x + 1:x + hw - 1, :3] = np.array(mix(hot, (90, 60, 40), 0.45), np.float32)
        elif kind == 'c':
            for yy in range(y + 1, y + h - 1, 2):
                a[yy, x + 1:x + w - 1, :3] = np.array(mix(hot, (90, 60, 40), 0.5), np.float32)
        elif kind == 'm':                                            # 木格窗：格子的孔里透出暖光
            sub = a[y:y + h, x:x + w]
            lu = lum(sub[..., :3])
            dark = (lu < np.percentile(lu, 45)) & (sub[..., 3] > 0)
            sub[dark, :3] = np.array(mix(hot, (200, 120, 60), 0.3), np.float32)
    shops = [s_ for s_ in reg['shop'] if (s_[4] if tod == 'night' else any(abs(s_[0] - o[0]) < 3 for o in DAWN_OPEN))]
    warm = np.array((1.0, 0.84, 0.6), np.float32)
    for (x0, y0, x1, y1, _) in shops:
        sub_a = a[y0:y1 + 1, x0:x1 + 1]
        sub_l = al[y0:y1 + 1, x0:x1 + 1]
        m = sub_a[..., 3] > 0
        sub_a[m, :3] = sub_l[m, :3] * warm * (0.92 if tod == 'night' else 0.8) + np.array((10, 4, 0), np.float32)
    lamps = [l_ for l_ in reg['lamp'] if not (tod == 'dawn' and l_[2] == 'post' and l_[0] in DAWN_LAMPS_OFF)]
    for (x, y, kind) in lamps:
        if kind == 'post':
            add_light(a, x, y + 4, 22, 26, (110, 84, 46), 1.0, rings=4)
            if ground_light:
                add_light(a, x, CURB - 2, 30, 8, (84, 66, 36), 1.0, rings=3)
        elif kind == 'wall':
            add_light(a, x, y + 2, 14, 16, (110, 84, 46), 1.0, rings=3)
            if ground_light:
                add_light(a, x, LANE + 3, 16, 4, (70, 56, 30), 1.0, rings=3)
        elif kind == 'bulb':
            add_light(a, x, y + 6, 18, 14, (120, 92, 46), 1.0, rings=3)
        elif kind == 'inner':
            add_light(a, x, y + 4, 10, 10, (100, 74, 36), 1.0, rings=3)
    if ground_light:
        for (x0, y0, x1, y1, _) in shops:                            # 开着的店门口地上的一片光
            if y1 >= LANE - 2:
                add_light(a, (x0 + x1) / 2.0, LANE + 2, (x1 - x0) * 0.6 + 4, 5, (80, 60, 30), 1.0, rings=3)
    np.clip(a, 0, 255, out=a)
    for (x, y, kind) in lamps:                                       # 灯芯最亮（盖在光圈上）
        if kind in ('post', 'wall'):
            a[y - 2:y + 2, x - 1:x + 2, :3] = np.array((255, 246, 214), np.float32)
        elif kind == 'bulb':
            a[y:y + 2, x, :3] = np.array((255, 250, 220), np.float32)
        else:
            a[y, x, :3] = np.array((255, 240, 190), np.float32)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def street_near(tod, dmg=(), ground_light=True):
    """一张近景：tod = day / night / dawn。"""
    im, reg = street_albedo(tuple(sorted(dmg)))
    im = im.copy()
    if tod == 'day':
        ground_shadows(im, reg)
        return im
    g = grade(im, tod)
    if tod == 'night':
        return light_night(g, im, reg, 'night', LIT_P, ground_light)
    return light_night(g, im, reg, 'dawn', 0.2, ground_light)


# ============================================================ 天 / 云 / 远景 / 中景
FAR_K, MID_K, CLOUD_K = 0.3, 0.6, 0.08
FARW = W + int(math.ceil((PW - W) * FAR_K))      # 512
MIDW = W + int(math.ceil((PW - W) * MID_K))      # 704
SKY_DAY = [(80, 142, 208), (104, 160, 216), (140, 182, 222), (184, 204, 220), (224, 218, 202)]
HAZE_DAY = (224, 214, 196)
RISE = (0.0, 0.25, 0.5, 0.75, 1.0)
DAWN_SKY0 = [(26, 22, 60), (52, 40, 92), (104, 66, 124), (170, 100, 140), (214, 140, 150)]
DAWN_SKY1 = [(64, 92, 150), (120, 128, 172), (222, 150, 130), (252, 178, 104), (255, 214, 146)]
NIGHT_SKY = [(6, 10, 30), (12, 18, 46), (22, 30, 70), (38, 48, 96), (56, 64, 112)]
CLOCK_X = 244            # 中景层里钟楼的中线：镜头 140（人在 x 300）时正好在世界 x 300 的上面（k 0.6）
CLOCK_FACE_Y = 40


@lru_cache(maxsize=1)
def sky_day():
    return P.sun_sky(SKY_DAY, (40, 22), sun_r=6)


def moon(im, cx, cy, r, glow=True):
    """满月：外面几圈淡光、月面的环形山（深一点的斑）、右下一圈暗边。"""
    if glow:
        A._glow(im, cx, cy, r * 3.2, r * 3.2, (120, 140, 200), 46, rings=4)
    d = ImageDraw.Draw(im)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C((236, 232, 214)))
    d.ellipse((cx - r + 1, cy - r + 1, cx + r - 2, cy + r - 2), fill=C((248, 246, 232)))
    for (dx, dy, rr) in ((-3, -2, 2), (3, 1, 3), (-1, 4, 2), (4, -4, 1), (-5, 3, 1)):
        d.ellipse((cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr), fill=C((214, 208, 190)))
    for a_ in range(0, 360, 4):
        if 10 < a_ < 140:
            px(d, int(round(cx + (r - 0.5) * math.cos(math.radians(a_)))),
               int(round(cy + (r - 0.5) * math.sin(math.radians(a_)))), (200, 194, 178))


@lru_cache(maxsize=1)
def sky_night():
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), NIGHT_SKY, bands=10)
    A._stars(im, (0, 0, W, 120), 90, 401)
    A._stars(im, (0, 0, W, 90), 30, 402, cols=((255, 240, 200), (200, 220, 255)))
    moon(im, 262, 30, 10)
    return im


@lru_cache(maxsize=8)
def sky_dawn(r):
    """黎明的天：r 0 = 紫（天快亮），1 = 橙（太阳刚到楼后面）。地平线附近一团亮光（太阳在楼后、偏右），
    几条被从下面照亮的层云（r 越大越金）。"""
    stops = [mix(a, b, r) for a, b in zip(DAWN_SKY0, DAWN_SKY1)]
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), stops, bands=12)
    A._glow(im, 214, 132, 150, 70, mix((220, 120, 140), (255, 210, 130), r), int(40 + 60 * r), rings=6)
    A._stars(im, (0, 0, W, 50), int(40 * (1 - r)) + 1, 403)
    d = ImageDraw.Draw(im)
    top = mix((66, 48, 96), (150, 112, 146), r)
    mid_ = mix((110, 70, 120), (226, 150, 130), r)
    lit = mix((200, 120, 150), (255, 206, 130), r)
    for i, (cy, cx, L, th) in enumerate(((24, 40, 70, 4), (20, 150, 46, 3), (34, 236, 84, 5), (46, 96, 60, 3),
                                         (56, 286, 50, 3), (62, 18, 40, 2), (40, 330, 40, 3))):
        # 被下面的太阳照亮的层云：上沿起伏（一个个小鼓包）、下沿平一点、两头收尖；底下一道亮边，身子暗
        for k in range(L):
            x = cx - L // 2 + k
            u = k / max(1, L - 1)
            env = math.sin(math.pi * u) ** 0.6
            hgt = th * env + 1.6 * env * math.sin(k * 0.5 + i * 1.7) + hash01(i, k // 3, 404) * env
            if hgt < 0.8:
                continue
            y0 = int(round(cy - hgt))
            y1 = int(round(cy + 0.4 * env))
            vl(d, x, y0, y1, top)
            if y1 - y0 >= 2:
                px(d, x, y1 - 1, mid_)
            px(d, x, y1, lit)
            if hash01(i, k, 405) < 0.25 and y0 < y1 - 1:
                px(d, x, y0, mix(top, lit, 0.25))
    return im


def clouds_img(tod):
    if tod == 'day':
        return P.wisps_img(640, 60, seed=5)
    pal = ((70, 80, 120), (52, 62, 100), (40, 48, 86), (30, 38, 74))
    return P.wisps_img(640, 60, seed=6, pal=pal)


def mini_minaret(d, x, base, top, w, col, ring=None):
    """远景的小宣礼塔：柱身 + 两圈阳台 + 尖顶；ring = 阳台上的灯（夜里的绿灯）。"""
    rect(d, x - w // 2, top + 4, x + w // 2, base, col)
    for yy in (top + int((base - top) * 0.35), top + int((base - top) * 0.6)):
        hl(d, x - w // 2 - 1, x + w // 2 + 1, yy, col)
        if ring:
            hl(d, x - w // 2 - 1, x + w // 2 + 1, yy - 1, ring)
    vl(d, x, top, top + 4, col)
    px(d, x - 1, top + 3, col)
    px(d, x + 1, top + 3, col)


FAR_MINARETS = ((30, 70, 3), (64, 84, 3), (118, 66, 4), (150, 80, 3), (262, 72, 3), (300, 60, 4), (338, 78, 3),
                (384, 70, 3), (470, 76, 3), (500, 86, 3))


@lru_cache(maxsize=1)
def far_albedo():
    """远景（k 0.3，512 宽）：一片很远的城——方块楼、穹顶、很多宣礼塔、中间偏左一座山岗上的城堡清真寺
    （大穹顶 + 两根铅笔一样细的宣礼塔）、后面一道不规则的石崖（台面平、有断口，不是光滑三角）、右边一座莲花顶的电视塔。"""
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    base = 136
    rid = []
    for x in range(FARW):
        y = 104 + 5 * math.sin(x * 0.021) + 3 * math.sin(x * 0.067 + 1.3) + 2 * hash01(x // 6, 406)
        step = 3 if (x // 23) % 3 == 0 else 0
        rid.append(int(y + step))
    for x in range(FARW):
        vl(d, x, rid[x], base, (196, 176, 146))
        if hash01(x, 407) < 0.35:
            px(d, x, rid[x] + 2, (176, 156, 128))
    cx = 200
    rect(d, cx - 28, 92, cx + 28, 106, (214, 202, 180))
    d.ellipse((cx - 11, 74, cx + 11, 96), fill=C((206, 196, 176)))
    for (sx, r) in ((cx - 16, 6), (cx + 16, 6)):
        d.ellipse((sx - r, 86, sx + r, 98), fill=C((200, 190, 170)))
    vl(d, cx, 68, 74, (200, 190, 170))
    for mx in (cx - 24, cx + 24):
        rect(d, mx - 1, 52, mx + 1, 104, (214, 204, 184))
        px(d, mx, 50, (214, 204, 184))
        px(d, mx, 51, (214, 204, 184))
        hl(d, mx - 2, mx + 2, 70, (214, 204, 184))
        hl(d, mx - 2, mx + 2, 84, (214, 204, 184))
    x = 0
    k = 0
    while x < FARW:
        w = int(hrange(10, 26, k, 408))
        top = int(hrange(102, 122, k, 409))
        if 168 < x < 232:
            top = max(top, 110)
        c = mix((206, 188, 160), (226, 214, 190), hash01(k, 410))
        rect(d, x, top, min(FARW - 1, x + w - 1), base, c)
        if hash01(k, 411) < 0.3:
            wx = x + int(w * 0.3)
            rect(d, wx, top - 3, wx + 3, top - 1, dk(c, 0.85))
        for yy in range(top + 3, base - 3, 5):
            for xx in range(x + 2, x + w - 2, 4):
                if hash01(xx, yy, 412) < 0.55:
                    px(d, xx, yy, dk(c, 0.78))
        x += w + (1 if hash01(k, 413) < 0.3 else 0)
        k += 1
    for (mx, top, w) in FAR_MINARETS:
        mini_minaret(d, mx, 118, top, w, (214, 200, 172))
    for (dx_, dy_, r) in ((86, 112, 7), (250, 110, 6), (322, 112, 8), (410, 114, 6), (482, 112, 5)):
        d.ellipse((dx_ - r, dy_ - r, dx_ + r, dy_ + r // 2), fill=C((214, 200, 174)))
        vl(d, dx_, dy_ - r - 3, dy_ - r, (214, 200, 174))
    tx = 444
    rect(d, tx - 1, 58, tx + 1, base, (200, 196, 186))
    for yy in range(62, 118, 3):
        px(d, tx, yy, (176, 172, 164))
    d.polygon([(tx - 5, 52), (tx + 5, 52), (tx + 3, 60), (tx - 3, 60)], fill=C((196, 192, 180)))
    vl(d, tx, 42, 52, (190, 186, 176))
    return im


def far_img(tod, r=0.0):
    im = far_albedo()
    if tod == 'day':
        return haze(im, 0.5, HAZE_DAY)
    if tod == 'night':
        a = np.array(im)
        g = grade(im, 'night')
        g = haze(g, 0.35, (26, 32, 66))
        d = ImageDraw.Draw(g)
        op = a[..., 3] > 0
        for i in range(260):                                         # 满城的灯（暖黄 / 白的小点）
            x = int(hrange(0, FARW, 414, i))
            y = int(hrange(96, 134, 415, i))
            if op[y, x]:
                px(d, x, y, (255, 214, 140) if i % 4 else (240, 240, 220))
        for (mx, top, w) in FAR_MINARETS + ((176, 52, 3), (224, 52, 3)):
            yy = top + int((118 - top) * 0.35) - 1                    # 宣礼塔阳台上的绿灯
            hl(d, mx - 2, mx + 2, yy, (90, 230, 140))
            px(d, mx, top - 1, (120, 255, 170))
        px(d, 444, 41, (255, 60, 60))                                # 电视塔顶的红灯
        hl(d, 440, 448, 54, (200, 220, 255))
        return g
    g = grade(im, 'dawn')
    hz = mix((150, 104, 150), (250, 176, 130), r)
    return haze(g, 0.45 + 0.1 * r, hz)


def mid_house(d, x0, x1, top, base, col, seed):
    rect(d, x0, top, x1, base, col)
    hl(d, x0, x1, top, lt(col, 0.25))
    vl(d, x1, top, base, dk(col, 0.82))
    for yy in range(top + 4, base - 4, 8):
        for xx in range(x0 + 3, x1 - 2, 6):
            k = hash01(xx, yy, seed)
            rect(d, xx, yy, xx + 1, yy + 3, dk(col, 0.62) if k < 0.7 else (70, 110, 90))


def clock_tower(im, cx, base, top, face_y, r, state='ok', col=(214, 196, 160), tod='day', hands='both'):
    """钟楼：方柱身（左亮右暗、几道线脚、细长窗）→ 钟面那一节 → 檐 + 小尖顶 + 顶上的小旗杆。
    state：ok 完好（白钟面 + 时针分针）/ broken 钟面碎了（裂纹 + 掉了几块露出里面的黑，分针没了）。"""
    d = ImageDraw.Draw(im)
    hi, md, sh, kk = P.wall_pal(col)
    w = r + 4
    rect(d, cx - w, face_y - r - 4, cx + w, base, md)
    vl(d, cx - w, face_y - r - 4, base, hi)
    vl(d, cx + w, face_y - r - 4, base, sh)
    for yy in range(face_y + r + 6, base, 14):
        hl(d, cx - w, cx + w, yy, lt(col, 0.2))
        hl(d, cx - w, cx + w, yy + 1, sh)
        rect(d, cx - 1, yy + 4, cx + 1, yy + 9, kk)
    hl(d, cx - w - 1, cx + w + 1, face_y - r - 5, lt(col, 0.3))
    hl(d, cx - w - 1, cx + w + 1, face_y + r + 4, lt(col, 0.3))
    hl(d, cx - w - 1, cx + w + 1, face_y + r + 5, sh)
    d.polygon([(cx - w - 1, face_y - r - 5), (cx, face_y - r - 15), (cx + w + 1, face_y - r - 5)], fill=C(dk(col, 0.86)))
    d.line((cx - w - 1, face_y - r - 5, cx, face_y - r - 15), fill=C(hi))
    vl(d, cx, face_y - r - 21, face_y - r - 15, (90, 90, 90))
    face = (244, 240, 226) if tod != 'night' else (250, 236, 180)
    d.ellipse((cx - r - 1, face_y - r - 1, cx + r + 1, face_y + r + 1), fill=C((60, 50, 44)))
    d.ellipse((cx - r, face_y - r, cx + r, face_y + r), fill=C(face))
    for a_ in range(0, 360, 30):
        px(d, int(round(cx + (r - 1) * math.cos(math.radians(a_)))), int(round(face_y + (r - 1) * math.sin(math.radians(a_)))),
           (60, 50, 44))
    if state == 'ok':
        d.line((cx, face_y, cx + 2, face_y - 2), fill=C((30, 26, 24)))      # 时针
        if hands == 'both':                                             # 屋顶那张的分针由剧情画（会跳一格），背景只画时针
            d.line((cx, face_y, cx, face_y - r + 1), fill=C((30, 26, 24)))
        px(d, cx, face_y, (90, 70, 50))
    else:
        for (a0, L) in ((20, 1.0), (100, 0.9), (200, 1.0), (290, 0.8), (330, 0.6)):
            ex_ = cx + L * r * math.cos(math.radians(a0))
            ey_ = face_y + L * r * math.sin(math.radians(a0))
            d.line((cx + 1, face_y, ex_, ey_), fill=C((70, 60, 54)))
        d.polygon([(cx + 1, face_y - 1), (cx + r - 1, face_y - 3), (cx + r - 2, face_y + 2)], fill=C((30, 24, 24)))
        d.polygon([(cx - 1, face_y + 1), (cx - 3, face_y + r - 1), (cx - r + 2, face_y + 2)], fill=C((30, 24, 24)))
        px(d, cx, face_y, (60, 50, 44))
        d.line((cx - 1, face_y, cx - 1, face_y - 3), fill=C((30, 26, 24)))


@lru_cache(maxsize=4)
def mid_albedo(clock_state='ok', tod='day'):
    """中景（k 0.6，704 宽）：街后面一排楼的房顶（高低错落、小窗）、水箱、天线、晾衣、一座清真寺（穹顶 + 宣礼塔）、
    钟楼（花京院最后打碎的那座：x CLOCK_X）、几棵海枣树冠。"""
    im = A._new(MIDW, H)
    d = ImageDraw.Draw(im)
    base = 140
    x = 0
    k = 0
    while x < MIDW:
        w = int(hrange(18, 40, k, 420))
        top = int(hrange(56, 96, k, 421))
        c = mix((196, 172, 136), (222, 204, 170), hash01(k, 422))
        mid_house(d, x, min(MIDW - 1, x + w - 1), top, base, c, 423 + k)
        q = hash01(k, 424)
        if q < 0.35:
            rect(d, x + 3, top - 5, x + 9, top - 1, (150, 154, 158))
            hl(d, x + 3, x + 9, top - 5, (190, 194, 198))
        elif q < 0.6:
            vl(d, x + w - 4, top - 9, top - 1, (110, 110, 118))
            hl(d, x + w - 7, x + w - 1, top - 8, (110, 110, 118))
            hl(d, x + w - 6, x + w - 2, top - 6, (110, 110, 118))
        elif q < 0.75:
            for j in range(4):
                c2 = P.CLOTH[int(hash01(k, j, 425) * len(P.CLOTH))]
                rect(d, x + 3 + j * 4, top - 5, x + 5 + j * 4, top - 2, c2)
            hl(d, x + 2, x + 18, top - 6, (90, 84, 80))
        x += w
        k += 1
    rect(d, 404, 84, 462, base, (226, 214, 186))
    d.ellipse((414, 60, 446, 96), fill=C((214, 200, 170)))
    vl(d, 430, 52, 60, (200, 170, 90))
    P.minaret(im, 456, 86, 14, 8, (226, 214, 186), seed=7)
    clock_tower(im, CLOCK_X, base, 12, CLOCK_FACE_Y, 5, state=clock_state, tod=tod)
    d = ImageDraw.Draw(im)
    for (cx, cy) in ((120, 70), (560, 76), (640, 66)):
        vl(d, cx, cy, base, (130, 100, 70))
        for a_ in range(0, 360, 30):
            L = 9
            ex_ = cx + L * math.cos(math.radians(a_))
            ey_ = cy + L * 0.55 * math.sin(math.radians(a_)) + (3 if 0 < a_ < 180 else 0)
            d.line((cx, cy, ex_, ey_), fill=C((70, 110, 60)))
    return im


def mid_img(tod):
    im = mid_albedo('broken' if tod == 'dawn' else 'ok', tod)
    if tod == 'day':
        return haze(im, 0.22, HAZE_DAY)
    if tod == 'night':
        a = np.array(im)
        g = grade(im, 'night')
        d = ImageDraw.Draw(g)
        win = (a[..., 3] > 0) & (a[..., 0] == 70) & (a[..., 1] == 110) & (a[..., 2] == 90)
        ys, xs = np.nonzero(win)
        for (y, x) in zip(ys, xs):
            if hash01(int(x) // 2, int(y) // 4, 426) < 0.6:
                px(d, int(x), int(y), (240, 196, 120))
        for x in range(0, MIDW, 3):
            for y in range(58, 136, 8):
                if a[y, x, 3] and hash01(x, y, 427) < 0.06:
                    px(d, x, y, (250, 210, 140))
        hl(d, 452, 460, 50, (90, 230, 140))
        hl(d, 452, 460, 32, (90, 230, 140))
        return haze(g, 0.12, (30, 36, 70))
    g = grade(im, 'dawn')
    return haze(g, 0.25, (120, 90, 140))


# ============================================================ 动的小东西（strip，k 1）
def _canvas():
    return A._new(PW, H)


def _graded(fn_raw, tod):
    """固有色画的帧 → 按时段压暗（夜 / 黎明）。"""
    def raw(f):
        im = fn_raw(f)
        return im if tod == 'day' else grade(im, tod)
    return raw


def raw_valance(f):
    im = _canvas()
    P.valance(ImageDraw.Draw(im), 128, 190, 112, (52, 104, 168), (240, 240, 236), f, stripe=4)
    return im


def raw_laundry_d(f):
    im = _canvas()
    laundry(ImageDraw.Draw(im), 196, 244, 51, f, 31, sag=3)
    return im


def raw_laundry_roof(f):
    im = _canvas()
    d = ImageDraw.Draw(im)
    vl(d, 374, 62, top_of(1) - 3, (150, 120, 80))
    vl(d, 393, 62, top_of(1) - 3, (120, 96, 64))
    laundry(d, 374, 393, 63, f, 32, sag=2)
    return im


def raw_alley_laundry(f):
    im = _canvas()
    d = ImageDraw.Draw(im)
    for i, y in enumerate((60, 77, 94)):
        laundry(d, ALLEY[0] + 1, ALLEY[1] - 1, y, f, 33 + i, sag=2, amp=0.8)
    return im


def raw_bunting(f):
    """横街上空一串三角彩旗（风吹得一面面翘）。"""
    im = _canvas()
    d = ImageDraw.Draw(im)
    pts = P.garland_pts(CROSS[0], 64, CROSS[1], 60, 7)
    P.wire(d, CROSS[0], 64, CROSS[1], 60, 7, col=(70, 64, 60))
    cols = [(206, 52, 64), (240, 240, 230), (40, 40, 44), (52, 140, 90), (240, 190, 50)]
    for i in range(2, len(pts) - 2, 5):
        x, y = pts[i]
        x, y = int(round(x)), int(round(y))
        c = cols[(i // 5) % len(cols)]
        sw = math.sin(math.tau * f / N + i * 0.7)
        L = 4 if sw < 0.5 else 3
        dx = 1 if sw > 0.2 else 0
        for r in range(L):
            hw = (L - r) // 2
            o = dx if r > 1 else 0
            hl(d, x - hw + o, x + hw + o, y + 1 + r, c)
    return im


def raw_oven(f):
    """面包店炉口里的火（光源：白天 / 夜里一样亮）。"""
    im = _canvas()
    d = ImageDraw.Draw(im)
    x0, x1, yb = 161, 172, 129
    for x in range(x0, x1 + 1):
        h_ = 2 + int(3 * hash01(x, f, 430) + 2 * math.sin(f * 0.8 + x))
        for k in range(max(1, h_)):
            c = (255, 240, 170) if k == 0 else ((255, 190, 70) if k < 3 else (220, 90, 30))
            px(d, x, yb - k, c)
    for x in range(x0, x1 + 1, 2):
        px(d, x, yb, (255, 120, 40) if (x + f) % 3 else (255, 220, 120))
    return im


PIGEONS = ((357, 61), (364, 61), (368, 67), (356, 73), (362, 73))


def raw_pigeons(f):
    """鸽舍横木上的几只鸽子：轮流啄一下、张一下翅膀；一只绕着鸽舍飞一圈。"""
    im = _canvas()
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate(PIGEONS):
        ph = (f + i * 3) % N
        pose = 1 if ph == 2 else (2 if ph == 5 and i % 2 else 0)
        pigeon_px(d, x, y, pose, (126, 128, 144) if i % 2 else (180, 180, 186))
    a_ = math.tau * f / N
    fx, fy = 362 + 16 * math.cos(a_), 48 + 6 * math.sin(a_)
    pigeon_px(d, int(round(fx)), int(round(fy)), 3 if f % 2 else 4, (150, 150, 162))
    return im


def raw_flag(f):
    im = _canvas()
    P.egypt_flag(ImageDraw.Draw(im), 339, 30, f, N, L=11, hgt=7)
    return im


def raw_neon(f):
    """屋顶 HOTEL 字架的红霓虹：字发亮、外面一圈暗红光；T 那个字坏了一半，一闪一闪。"""
    im = _canvas()
    d = ImageDraw.Draw(im)
    lv = (0.55, 0.8, 1.0, 0.85, 0.6, 0.95, 0.7, 0.9)[f]
    on = (255, 120, 120)
    halo = mix((60, 20, 40), (200, 50, 70), lv)
    for i, ch in enumerate('HOTEL'):
        g = FONT3[ch]
        bx = 258 + i * 8
        dead = (ch == 'T' and f in (1, 2, 5))
        cells = [(bx + c_ * 2, 43 + r * 2) for r, row in enumerate(g) for c_, v in enumerate(row) if v == '1']
        cs = set()
        for (x, y) in cells:
            cs |= {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)}
        for (x, y) in cells:
            for (ddx, ddy) in ((-1, 0), (2, 0), (0, -1), (0, 2), (1, -1), (1, 2), (-1, 1), (2, 1)):
                if (x + ddx, y + ddy) not in cs:
                    px(d, x + ddx, y + ddy, halo if not dead else (70, 30, 40))
        for (x, y) in cells:
            rect(d, x, y, x + 1, y + 1, on if not dead else (120, 50, 60))
            px(d, x, y, (255, 230, 230) if not dead else (140, 60, 70))
    return im


def raw_cross(f):
    """药房的绿十字灯箱（一闪一闪）+ 咖啡馆招牌的绿霓虹边。"""
    im = _canvas()
    d = ImageDraw.Draw(im)
    lv = (1.0, 0.75, 0.95, 0.6, 0.9, 0.8, 1.0, 0.55)[f]
    g = mix((30, 90, 50), (120, 255, 170), lv)
    rect(d, 719, 105, 721, 111, g)
    rect(d, 717, 107, 723, 109, g)
    px(d, 720, 108, (220, 255, 230))
    rect(d, 349, 104, 391, 111, None, outline=mix((30, 80, 60), (110, 250, 190), max(0.0, 1.6 - lv)))
    return im


def raw_tv(f):
    im = _canvas()
    d = ImageDraw.Draw(im)
    c = ((150, 190, 230), (200, 220, 250), (120, 160, 220), (230, 240, 255), (140, 180, 210), (180, 210, 240),
         (110, 150, 200), (210, 230, 250))[f]
    rect(d, 382, 117, 387, 120, c)
    px(d, 383 + f % 4, 118, lt(c, 0.4))
    return im


def raw_moths(f):
    """548 那盏路灯边绕着飞的几只飞虫。"""
    im = _canvas()
    d = ImageDraw.Draw(im)
    lx, ly = 554, 108
    for i in range(4):
        a_ = math.tau * (f / N) * (1 if i % 2 else -1) + i * 1.6
        x = lx + (6 + i * 2) * math.cos(a_)
        y = ly + (4 + i) * math.sin(a_ + i)
        px(d, int(round(x)), int(round(y)), (255, 240, 200) if i % 2 else (230, 220, 190))
    return im


def raw_smoke(f):
    """撞进楼里的卡车还在冒的烟：一团团从洞口往上飘、往右散、变淡（hard_alpha 抖成 0 / 255）。"""
    im = _canvas()
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    for i in range(5):
        u = ((f / N) + i / 5.0) % 1.0
        x = 852 + 6 * math.sin(i * 2.1) + u * 14
        y = 114 - u * 46
        r = 3 + u * 6
        a_ = int(200 * (1 - u) ** 1.2)
        c = mix((110, 100, 110), (170, 160, 170), u)
        d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=tuple(c) + (a_,))
    lay = P.hard_alpha(lay)
    im.alpha_composite(lay)
    return im


def raw_dawn_pigeons(f):
    """旅馆屋顶上空绕圈的一小群鸽子（天亮了）。"""
    im = _canvas()
    d = ImageDraw.Draw(im)
    for i in range(6):
        a_ = math.tau * (f / N) + i * 1.05
        x = 300 + 26 * math.cos(a_) + (i % 3) * 3
        y = 40 + 8 * math.sin(a_) + (i % 2) * 3
        pigeon_px(d, int(round(x)), int(round(y)), 3 if (f + i) % 2 else 4, (70, 66, 90))
    return im


def raw_lamp_flicker(f):
    """238 那盏路灯快坏了：一闪一闪。"""
    im = _canvas()
    d = ImageDraw.Draw(im)
    lx, ly = 244, 108
    on = f in (0, 1, 3, 4, 6)
    c = (255, 246, 214) if on else (120, 110, 100)
    rect(d, lx - 1, ly - 2, lx + 1, ly + 1, c)
    if on:
        for (dx, dy) in ((-2, -1), (2, -1), (-2, 0), (2, 0), (0, -3), (0, 2)):
            px(d, lx + dx, ly + dy, (240, 200, 140) if f % 3 else (220, 180, 120))
    else:
        px(d, lx, ly - 3, (90, 84, 80) if f % 2 else (100, 94, 86))
    return im


def street_strips(tod):
    """(名字, 帧函数) 列表，帧函数已按时段压暗。"""
    out = []
    for (name, raw) in (('valance', raw_valance), ('laundry_d', raw_laundry_d), ('laundry_roof', raw_laundry_roof),
                        ('alley_laundry', raw_alley_laundry), ('bunting', raw_bunting), ('pigeons', raw_pigeons),
                        ('flag', raw_flag)):
        if tod == 'dawn' and name == 'pigeons':
            continue
        out.append((name, cached(_graded(raw, tod))))
    out.append(('oven', cached(raw_oven)))
    if tod == 'night':
        out += [('neon', cached(raw_neon)), ('cross', cached(raw_cross)), ('tv', cached(raw_tv)),
                ('moths', cached(raw_moths))]
    if tod == 'dawn':
        out += [('smoke', cached(raw_smoke)), ('flock', cached(raw_dawn_pigeons)),
                ('lamp_flicker', cached(raw_lamp_flicker))]
    return out


# ============================================================ 卡车逃亡（key scroll）：整屏三层往左卷
SCROLL_P = 640
SCROLL_VX = dict(far=14.0, mid=64.0, road=240.0)
LANES = (154, 163, 172)


@lru_cache(maxsize=1)
def scroll_far_img():
    """远景：夜里一片很远的城（剪影 + 满城的小灯 + 宣礼塔的绿灯），640 循环。"""
    im = A._new(SCROLL_P, H)
    d = ImageDraw.Draw(im)
    base = 128
    k = 0
    x = 0
    while x < SCROLL_P:
        w = int(hrange(10, 24, k, 440))
        if x + w > SCROLL_P:
            w = SCROLL_P - x
        top = int(hrange(84, 112, k, 441))
        c = mix((28, 34, 64), (40, 46, 80), hash01(k, 442))
        rect(d, x, top, x + w - 1, base, c)
        for yy in range(top + 3, base - 2, 4):
            for xx in range(x + 2, x + w - 2, 3):
                if hash01(xx, yy, 443) < 0.25:
                    px(d, xx, yy, (250, 210, 140) if hash01(xx, yy, 444) < 0.8 else (230, 236, 255))
        x += w
        k += 1
    for (mx, top) in ((60, 56), (210, 62), (330, 50), (470, 60), (590, 58)):
        rect(d, mx - 1, top + 4, mx + 1, 112, (34, 40, 74))
        vl(d, mx, top, top + 4, (34, 40, 74))
        for yy in (top + 14, top + 26):
            hl(d, mx - 2, mx + 2, yy, (34, 40, 74))
            hl(d, mx - 2, mx + 2, yy - 1, (90, 230, 140))
    for (cx, r) in ((130, 9), (400, 7), (540, 8)):
        d.ellipse((cx - r, 104 - r, cx + r, 104 + r // 2), fill=C((34, 40, 74)))
    rect(d, 0, base, SCROLL_P - 1, base + 4, (30, 36, 66))
    return im


@lru_cache(maxsize=1)
def scroll_mid_img():
    """中景：一路掠过去的楼（夜：亮窗、霓虹招牌、一楼开着的店 / 拉下的卷帘门），640 循环。"""
    im = A._new(SCROLL_P, H)
    d = ImageDraw.Draw(im)
    base = 147
    x = 0
    k = 0
    cols = list(WALL.values())
    while x < SCROLL_P:
        w = int(hrange(34, 70, k, 450))
        if SCROLL_P - x - w < 30:
            w = SCROLL_P - x
        top = int(hrange(30, 80, k, 451))
        col = cols[int(hash01(k, 452) * len(cols))]
        c = grade(Image.new('RGBA', (1, 1), C(col)), 'night').getpixel((0, 0))[:3]
        rect(d, x, top, x + w - 1, base, c)
        hl(d, x, x + w - 1, top, lt(c, 0.2))
        vl(d, x + w - 1, top, base, dk(c, 0.7))
        for yy in range(top + 5, 100, 15):
            for xx in range(x + 4, x + w - 8, 12):
                lit = hash01(xx, yy, 453) < 0.5
                rect(d, xx, yy, xx + 5, yy + 8, (250, 206, 130) if lit else dk(c, 0.6))
                if lit:
                    vl(d, xx + 2, yy, yy + 8, (190, 120, 70))
                hl(d, xx - 1, xx + 6, yy + 9, lt(c, 0.15))
        sx0, sx1 = x + 4, x + w - 5
        if hash01(k, 454) < 0.6:
            rect(d, sx0, 112, sx1, base, (150, 104, 60))
            rect(d, sx0 + 1, 114, sx1 - 1, base, (230, 170, 100))
            ncol = (90, 230, 160) if k % 2 else (255, 90, 110)
            hl(d, sx0, sx1, 110, ncol)
            hl(d, sx0, sx1, 111, dk(ncol, 0.6))
        else:
            for yy in range(112, base):
                hl(d, sx0, sx1, yy, (60, 64, 76) if yy % 2 else (46, 50, 62))
        x += w
        k += 1
    return im


@lru_cache(maxsize=1)
def scroll_road_img():
    """近景：人行道（y 138–147）+ 路缘石 + 三车道的柏油路（车道中线 y 154 / 163 / 172，车道线在 158 / 167），
    路灯（脚在人行道上，每 160 px 一盏）和它们落在路上的光，640 循环。"""
    im = A._new(SCROLL_P, H)
    d = ImageDraw.Draw(im)
    side = grade(Image.new('RGBA', (1, 1), C(SIDE_C)), 'night').getpixel((0, 0))[:3]
    road = (40, 42, 58)
    rect(d, 0, 138, SCROLL_P - 1, 147, side)
    for x in range(0, SCROLL_P, 8):
        vl(d, x, 138, 147, dk(side, 0.85))
    hl(d, 0, SCROLL_P - 1, 142, dk(side, 0.85))
    hl(d, 0, SCROLL_P - 1, 148, (110, 108, 116))
    hl(d, 0, SCROLL_P - 1, 149, (60, 60, 72))
    rect(d, 0, 150, SCROLL_P - 1, H - 1, road)
    for i in range(160):
        x = int(hrange(0, SCROLL_P, 455, i))
        y = int(hrange(151, H, 456, i))
        if y in LANES:
            continue
        px(d, x, y, (52, 54, 70) if i % 2 else (34, 36, 50))
    for ly in (158, 167):
        for x in range(0, SCROLL_P, 24):
            hl(d, x, x + 11, ly, (200, 200, 190))
            hl(d, x, x + 11, ly + 1, (120, 120, 120))
    hl(d, 0, SCROLL_P - 1, 177, (150, 140, 90))
    a = np.array(im).astype(np.float32)
    for lx in range(40, SCROLL_P, 160):
        add_light(a, lx + 6, 160, 44, 22, (110, 86, 46), 1.0, rings=4)
        add_light(a, lx + 6, 144, 30, 6, (110, 86, 46), 1.0, rings=3)
    np.clip(a, 0, 255, out=a)
    im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    reg = dict(lamp=[])
    for lx in range(40, SCROLL_P, 160):
        lamp_post(im, reg, lx, base=146, top=98, col=(30, 36, 40))
    d = ImageDraw.Draw(im)
    for (x, y, kind) in reg['lamp']:
        rect(d, x - 1, y - 2, x + 1, y + 1, (255, 246, 214))
    return im


def scroll_layers():
    return [dict(type='static', name='scroll_sky', img=sky_night(), key='scroll'),
            dict(type='wrap', name='scroll_far', img=scroll_far_img(), period=SCROLL_P, k=0.0, y=0,
                 vx=SCROLL_VX['far'], key='scroll'),
            dict(type='wrap', name='scroll_mid', img=scroll_mid_img(), period=SCROLL_P, k=0.0, y=0,
                 vx=SCROLL_VX['mid'], key='scroll'),
            dict(type='wrap', name='scroll_road', img=scroll_road_img(), period=SCROLL_P, k=0.0, y=0,
                 vx=SCROLL_VX['road'], key='scroll')]


# ============================================================ 黎明：楼顶的晨光（key rise）
def sun_rim(near, r):
    """楼的轮廓逆光：每一列最上面的不透明像素（屋顶 / 天线 / 宣礼塔尖）和下面 1–2 px 往暖光推（r 越大越亮、越宽）。
    只画变了的像素，其余透明（pick 盖在近景上）。"""
    a = np.array(near)
    out = np.zeros_like(a)
    hot = np.array(mix((230, 130, 150), (255, 200, 120), r), np.float32)
    op = a[..., 3] > 0
    n = 1 + int(round(r * 2))
    for x in range(a.shape[1]):
        ys = np.nonzero(op[:LANE, x])[0]
        if not len(ys):
            continue
        y = ys[0]
        for k in range(n):
            yy = y + k
            if yy < LANE and op[yy, x]:
                c = a[yy, x, :3].astype(np.float32)
                amt = (0.75 if k == 0 else 0.4) * (0.5 + 0.5 * r)
                out[yy, x, :3] = np.clip(c * (1 - amt) + hot * amt, 0, 255).astype(np.uint8)
                out[yy, x, 3] = 255
    return Image.fromarray(out, 'RGBA')


# ============================================================ 图层表 / 锚点 / 导出
def street_dmg(tod):
    return ('sign_gone', 'truck', 'wrecked') if tod == 'dawn' else ()


@lru_cache(maxsize=3)
def street_spec(tod):
    L = []
    if tod == 'day':
        L.append(dict(type='static', name='sky', img=sky_day()))
        L.append(dict(type='wrap', name='clouds', img=clouds_img('day'), period=640, k=CLOUD_K, y=4, vx=1.2))
    elif tod == 'night':
        L.append(dict(type='static', name='sky', img=sky_night()))
        L.append(dict(type='wrap', name='clouds', img=clouds_img('night'), period=640, k=CLOUD_K, y=12, vx=0.8))
    else:
        L.append(dict(type='pick', name='sky', key='rise', values=list(RISE), imgs=[sky_dawn(r) for r in RISE],
                      x=0, y=0, k=0.0))
    if tod == 'dawn':
        fulls = [far_img('dawn', r) for r in (0.0, 0.5, 1.0)]
        _, y0 = crop_rows(fulls[0])
        hh = crop_rows(fulls[0])[0].height
        L.append(dict(type='pick', name='far', key='rise', values=[0.0, 0.5, 1.0],
                      imgs=[im.crop((0, y0, FARW, y0 + hh)) for im in fulls], x=0, y=y0, k=FAR_K))
    else:
        fim, fy = crop_rows(far_img(tod))
        L.append(dict(type='pano', name='far', img=fim, k=FAR_K, x=0, y=fy))
    if tod == 'day':
        bird = V.kite_bird_img()
        L.append(dict(type='clouds', name='birds', span=460,
                      items=[('bird%d' % i, bird, x0, y, vx, k) for i, (y, vx, k, x0) in
                             enumerate(((16, 3.0, 0.15, 60), (28, -2.2, 0.15, 300)))]))
    mim, my = crop_rows(mid_img(tod))
    L.append(dict(type='pano', name='mid', img=mim, k=MID_K, x=0, y=my))
    near = street_near(tod, street_dmg(tod))
    nim, ny = crop_rows(near)
    L.append(dict(type='pano', name='near', img=nim, k=1.0, x=0, y=ny))
    if tod == 'dawn':
        rims = [sun_rim(near, r) for r in (0.5, 1.0)]
        bb = rims[1].getchannel('A').getbbox()
        L.append(dict(type='pick', name='sunrim', key='rise', values=[0.0, 0.5, 1.0],
                      imgs=[blank1()] + [im.crop(bb) for im in rims], x=bb[0], y=bb[1], k=1.0))
    if tod == 'night':
        for (name, key, dmg) in (('crashed', 'crashed', ('crashed',)), ('wrecked', 'stand_wrecked', ('wrecked',)),
                                 ('signgone', 'sign_gone', ('sign_gone',))):
            pk, box = diff_pick(name, key, near, street_near('night', dmg))
            L.append(pk)
    for (name, fn) in street_strips(tod):
        L.append(strip(name, fn, k=1.0))
    if tod == 'night':
        L.append(strip('dust', cached(raw_smoke), k=1.0, key='crashed'))
        L.append(dict(type='tint', name='dark', key='dark', color=(18, 12, 44), alpha=0.4))
        L += scroll_layers()
    return tuple(L)


def street_anchors(tod):
    anc = {k: list(v) for k, v in ANCHORS.items()}
    if tod == 'night':
        anc.update({k: list(v) for k, v in NIGHT_ANCHORS.items()})
    if tod == 'dawn':
        anc.update({k: list(v) for k, v in DAWN_ANCHORS.items()})
    anc.update(
        road_sign_top=[SIGN_X, SIGN_TOP],                            # 隼停的地方（路牌红圆的顶）
        sign_hole=[SIGN_X, LANE],
        stand_box=[STAND[0], 110, STAND[1], LANE],
        crash_box=[CRASH[0], CRASH_TOP, CRASH[1] + 1, LANE],
        truck_crash=[862, LANE],                                     # 夜：卡车道具（pivot 20,23）摆这里就像扎进墙洞
        cross_box=[CROSS[0], 60, CROSS[1], CURB + 2],
        alley_box=[ALLEY[0], 60, ALLEY[1], LANE],
        hotel_windows=[[265, 99], [287, 99], [309, 99], [331, 99]],   # 旅馆二楼法式窗的脚（F-03 翻窗）
        hotel_door=[290, LANE - 1],
        lamps=[[x + 6, 108] for x in LAMPS_X],
        mosque_door=[936, LANE - 1],
        lane_back=LANE, curb=CURB)
    return anc


def street_export(ex, BJ, tod):
    spec = street_spec(tod)
    layers = export_layers(ex, BJ, spec)
    st = ex.stage(PW, GROUND, WALK, layers, [], street_anchors(tod))
    if ex.check_on:
        street_checks(ex, BJ, st, spec, tod)
    return st


PROPS_ON_GROUND = dict(mirror_stand=(12, 20), oil_drum=(10, 14), truck_lot=(40, 23), senator_stop=(46, 18))


def street_checks(ex, BJ, st, spec, tod):
    anc = st['anchors']
    req = dict(ANCHORS)
    if tod == 'night':
        req.update(NIGHT_ANCHORS)
    if tod == 'dawn':
        req.update(DAWN_ANCHORS)
    near = street_near(tod, street_dmg(tod))
    flatnear = street_near(tod, street_dmg(tod), ground_light=False)   # 量平整用：地上的灯光是光，不是东西
    states = {'day': [{}],
              'night': [{}, {'crashed': 1, 'stand_wrecked': 1, 'sign_gone': 1, 'dark': 1}, {'scroll': 1}],
              'dawn': [{'rise': 0}, {'rise': 0.5}, {'rise': 1}]}[tod]
    walk = (150, 176) if tod == 'day' else (148, 176)
    skies = [('天底图', sky_day() if tod == 'day' else sky_night())] if tod != 'dawn' else \
        [('天 rise=%.2f' % r, sky_dawn(r)) for r in RISE]
    gx = ANCHORS['sewer_grate'][0]
    skip = [(CROSS[0], LANE, CROSS[1] + 1, CURB + 2), (gx - 10, 165, gx + 11, 174), (180, 164, 198, 172)]
    if tod == 'dawn':
        skip += [(CRASH[0] - 18, LANE, CRASH[1] + 20, 168), (STAND[0] - 8, LANE, 530, 168),
                 (SIGN_X - 6, LANE, SIGN_X + 15, LANE + 6)]
    stand = STAND_PTS + (('truck_lot', 'senator_stop') if tod == 'night' else ())
    cfg = dict(title={'day': '开罗白天', 'night': '开罗夜街', 'dawn': '开罗黎明'}[tod], PW=PW, walk=walk, near=near,
               opaque_rows=(LANE, H), skies=skies, states=states, stand=stand, flatnear=flatnear,
               required=tuple(req), values={k: list(v) for k, v in req.items()}, size_limit=350 * 1024, cams_step=40,
               flat=(0, PW, walk[0], walk[1] + 1, 24, 0.015), flat_skip=skip)
    std_checks(ex, BJ, st, spec, cfg)
    a = np.array(flatnear).astype(np.float32)
    L_ = lum(a[..., :3])
    use = {'day': ('mirror_stand', 'oil_drum'), 'night': ('truck_lot', 'senator_stop'), 'dawn': ()}[tod]
    for name, (w, h) in PROPS_ON_GROUND.items():
        if name not in use:                                          # 只查这一张图里剧情真的会摆的道具
            continue
        x, y = anc[name]
        bad = 0
        for yy in range(max(LANE + 3, y - h), y + 1):                 # 人行道后沿两行是后面东西的影子，被道具挡住，不算
            row = L_[yy]
            med = np.median(row)
            seg = row[x - w // 2:x + w // 2 + 1]
            bad += int((np.abs(seg - med) > 26).sum())
        ex.checked('%s (%d,%d) 摆 %d×%d 道具的地方只有平地（离整行中位亮度太远的像素）' % (name, x, y, w, h), bad)
    if tod == 'dawn':
        bad = 0
        for yy in range(ROAD0 + 1, 171):
            row = L_[yy]
            bad += int((np.abs(row[600:700] - np.median(row)) > 30).sum())
        ex.checked('路口 x 600–700 y %d–170（SPW 吉普停的地方）只有路面' % (ROAD0 + 1), bad)
    if tod != 'dawn':
        x, y = anc['road_sign_top']
        r, g_, b_, al = near.getpixel((x, y))
        r2, g2, b2, _ = near.getpixel((x, y - 1))
        red = (r > g_ + 60) if tod == 'day' else (r > g_ + 8)
        ex.checked('road_sign_top (%d,%d) 正好是路牌红圆的顶（这一点红、上面一点不是）' % (x, y),
                   0 if (red and not (r2 > g2 + 60)) else 1)
    a8 = np.array(near)
    hx, hy = anc['hotel_roof']
    ex.checked('hotel_roof (%d,%d) 是檐口顶（不透明）' % (hx, hy), 0 if a8[hy, hx, 3] == 255 else 1)
    rx, ry = anc['rooftop']
    seg = a8[ry - 18:ry - 1, rx - 14:rx + 15, 3]                      # ry−1 是屋顶边外沿的墨线
    ex.checked('rooftop (%d,%d) 屋顶边那一行实、上面 17 行 × 29 列没有矮墙 / 杂物' % (rx, ry),
               int((seg > 0).sum()) + (0 if a8[ry, rx, 3] == 255 else 1))
    if tod == 'night':
        sonly = dict(st, layers=[L for L in st['layers'] if L.get('key') == 'scroll'], fg=[])
        leak = 0
        for camX in (0, 320, 640):
            for t in (0.0, 1.3, 5.7):
                for extra in ({}, {'crashed': 1, 'stand_wrecked': 1, 'sign_gone': 1, 'dark': 1}):
                    s = dict(extra, scroll=1)
                    leak += BJ.ndiff(BJ.ref_render(st, ex.images, camX, t, s), BJ.ref_render(sonly, ex.images, camX, t, s))
        ex.checked('scroll = 1 时整屏只有卡车逃亡的四层（3 个镜头 × 3 个时刻 × 2 种 key 组合，露出来的像素）', leak)
        ri = np.array(scroll_road_img()).astype(int)
        white = (lum(ri[..., :3].astype(np.float32)) > 170) & (np.abs(ri[..., 0] - ri[..., 2]) < 40)
        lane_rows = sum(int(white[y].sum()) for y in LANES)
        ex.checked('三条车道的中线 y %s 上没有车道线（车道线在 158 / 167）' % (LANES,), lane_rows)
        vxs = sorted(L['vx'] for L in st['layers'] if L.get('key') == 'scroll' and L['type'] == 'wrap')
        ok = len(vxs) == 3 and vxs[0] > 0 and vxs[0] < vxs[1] < vxs[2]
        ex.checked('scroll 三层 wrap 都往左卷、越近越快（vx = %s）' % vxs, 0 if ok else 1)
        boxes = {L['key']: (L['x'], L['y'], L['x'] + L['imgs'][1].width, L['y'] + L['imgs'][1].height)
                 for L in spec if L['type'] == 'pick'}
        okb = (boxes['crashed'][0] >= 800 and boxes['crashed'][2] <= 912 and 420 <= boxes['stand_wrecked'][0] and
               boxes['stand_wrecked'][2] <= 540 and 560 <= boxes['sign_gone'][0] and boxes['sign_gone'][2] <= 600)
        ex.note('pick 框：%s' % boxes)
        ex.checked('三个剧情 key 的盖图只盖在自己那一块（转角楼 / 水果摊 / 路牌）', 0 if okb else 1)
