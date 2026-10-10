# -*- coding: utf-8 -*-
r"""JoJo 游戏 · 背景导出（包 7B，技术约定 §5.5 / §3.6 / §3.14 D）。

build_all(stages, c)   给 tools\build_assets.py 的 bg 步调用：往 stages[key] 写 §3.6 的结构，
                       图片用 c['save_png'](img, 'bg/<key>/<layer>', pack) 存。
单独运行（预览 + 自检，不写 assets\bg\）：
    $env:PYTHONDONTWRITEBYTECODE = 1
    python -B tools\bg_jojo.py                 # 全部 M1 背景
    python -B tools\bg_jojo.py jail_cell cockpit   # 只导这几个
    python -B tools\bg_jojo.py --no-check      # 跳过逐像素自检
  图层 PNG → tools\bg_new\_preview\layers\，预览 → tools\bg_new\_preview\<key>.png，
  元数据 → tools\bg_new\_preview\_stages.json，自检结果 → tools\bg_new\_preview\_report.json。

做法（报告 06 §7）：
  · 横卷背景（香港夜街、天空、校门、黄昏门口）分层导出，JS 按 §3.6 公式拼：
      wrap   o = floor(camX·k + t·vx) mod period，从图的第 o 列取 320 宽（不够宽就分两段接）
      pano   画在 x − floor(camX·k)
      strip  帧 floor(t·fps) mod n，画在 (x − floor(camX·k), y)（screen 时不减）
    逐帧画的东西（霓虹、路面标线）一律按“世界坐标 + 镜头往右为正”放，顺带修好原片 bg_asia
    scroll≠0 时霓虹和灯箱错位的 bug（报告 06 §1.3 / §7.7）。
  · 单屏背景 = 静态底图 + 会动的小块烘成 strip（真循环：频率按循环长度取整，见各函数注释）。
  · 新画的背景在 tools\bg_new\<key>.py（school_infirmary / tatami_top / plane_cabin_side），
    这里 import 进来走同一套导出。
自检（技术约定 §5.5 末条，必须）：本文件里的 ref_render() 是 §3.6 公式的 Python 版（和 JS 同一套
取整），对每个背景在 3–5 个镜头位置拿“导出层重建”和“原函数输出”逐像素比；strip 打印
“末帧→首帧”的差异像素数（接缝）、相邻帧的典型差异、以及 t = n/fps 时和第 0 帧的差（闭合）。
"""
import sys
sys.dont_write_bytecode = True                      # 必须在 import 原工程之前（技术约定 §0.2）

import functools  # noqa: E402
import importlib  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))   # 游戏\tools
GAME = os.path.dirname(HERE)
WORK = os.path.dirname(GAME)
SRC = os.path.join(WORK, '源码')
BG_NEW = os.path.join(HERE, 'bg_new')
PREVIEW = os.path.join(BG_NEW, '_preview')
REGISTRY = os.path.join(HERE, 'registry')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import (Frame, W, H, FPS, paste, hash01, hrange, mix, gradient,  # noqa: E402
                         clamp, lerp, ease, prog, blink)
from engine import bg_asia as A, bg_egypt as E  # noqa: E402

STRIP_SOFT_W = 4096     # 帧条宽度超过就打印提醒（手机 GPU 贴图上限，银魂坑 A11）
STRIP_HARD_W = 8192     # 超过就报错

# §3.14 D 的 pack 列（tools\registry\packs.json 读不到时用）
DEFAULT_PACK = {
    'title_pyramids': 'title',
    'world_map': 'common', 'sky_day': 'common', 'sea_day': 'common',
    'jail_cell': 'prologue', 'kujo_house_day': 'prologue', 'kujo_house_night': 'prologue',
    'kujo_house_morning': 'prologue', 'kujo_bedroom_dusk': 'prologue', 'school_gate': 'prologue',
    'school_infirmary': 'prologue', 'dusk_gate': 'prologue', 'tatami_top': 'prologue', 'school_stairs': 'prologue',
    'plane_cabin_side': 'ch1', 'plane_cabin': 'ch1', 'cockpit': 'ch1', 'hongkong_night': 'ch1',
    'hk_garden_night': 'ch1',
}
ORDER = list(DEFAULT_PACK)


# ============================================================ 小工具
def frame(t=0.0):
    """原函数调用约定（技术约定 §5.5）：Frame(t, int(t*FPS), 60.0, 'bake')。"""
    return Frame(t, int(t * FPS), 60.0, 'bake')


def blank(w=W, h=H):
    return Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))


class FakeFr:
    """只带 t / img / d 的假 Frame：把原工程画“会动的小东西”的函数画到透明图上（得到叠加层）。"""

    def __init__(self, t, img=None):
        self.t = t
        self.img = img if img is not None else blank()
        self.d = ImageDraw.Draw(self.img)


def crop_rows(im):
    """宽度不变、上下裁到不透明行：返回 (图, y0)。全透明返回 (原图, 0)。"""
    bb = im.getchannel('A').getbbox()
    if not bb:
        return im, 0
    return im.crop((0, bb[1], im.width, bb[3])), bb[1]


def roll_x(im, dx):
    """横向循环平移（图片列 c → c − dx），用来把原图的“起点偏移”烘进图里。"""
    a = np.array(im)
    return Image.fromarray(np.roll(a, -int(dx), axis=1), im.mode)


def tile_to(im, period, minw):
    """周期 period 的图横向重复到宽度 ≥ minw 且是 period 的整数倍（wrap 层 period < 320 时用）。"""
    n = max(1, -(-minw // period))
    out = blank(period * n, im.height)
    for i in range(n):
        out.paste(im.crop((0, 0, period, im.height)), (i * period, 0))
    return out


def ndiff(a, b, box=None, mask=None, tol=0):
    """两张图（RGB 部分）不同的像素数；box 只比这个框，mask（H×W bool，True = 要比）只比这些点。"""
    if box is not None:
        a, b = a.crop(box), b.crop(box)
    x = np.asarray(a.convert('RGB'), np.int16)
    y = np.asarray(b.convert('RGB'), np.int16)
    d = np.abs(x - y).max(-1) > tol
    if mask is not None:
        m = mask if box is None else mask[box[1]:box[3], box[0]:box[2]]
        d &= m
    return int(d.sum())


def ndiff_rgba(a, b):
    x = np.asarray(a.convert('RGBA'), np.int16)
    y = np.asarray(b.convert('RGBA'), np.int16)
    return int((np.abs(x - y).max(-1) > 0).sum())


def rect_mask(rects, keep=True):
    """rects = [(x0,y0,x1,y1)]（右下不含）→ H×W bool；keep=False 时取反（= 排除这些框）。"""
    m = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in rects:
        m[max(0, int(y0)):max(0, int(y1)), max(0, int(x0)):max(0, int(x1))] = True
    return m if keep else ~m


def pt(p):
    return [int(round(p[0])), int(round(p[1]))]


def import_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_SCENES = {}


def scene(mod):
    """场景模块（s05 / s06）：导入前先 assets.load_all()（报告 06 §8 第 7 条）。"""
    if mod not in _SCENES:
        import assets
        assets.load_all()
        _SCENES[mod] = importlib.import_module('scenes.' + mod)
    return _SCENES[mod]


def bg_new(name):
    """tools\\bg_new\\<name>.py（新画的背景）。"""
    key = 'bg_new_' + name
    if key not in sys.modules:
        import_path(key, os.path.join(BG_NEW, name + '.py'))
    return sys.modules[key]


# ============================================================ §3.6 公式的 Python 版（自检 / 预览用）
def _comp(dst, im, x, y):
    """alpha 合成，越界自动裁（同 canvas drawImage 的 source-over）。"""
    paste(dst, im, int(x), int(y))


def _lighter(dst, row_img, x, y, alpha):
    """'lighter' 混合（逐分量相加，canvas globalCompositeOperation='lighter' + globalAlpha）。"""
    a = np.array(dst).astype(np.float32)
    s = np.array(row_img).astype(np.float32)
    h, w = s.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sub = s[y0 - y:y1 - y, x0 - x:x1 - x]
    a[y0:y1, x0:x1, :3] += sub[..., :3] * (sub[..., 3:4] / 255.0) * alpha
    dst.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def ref_layer(dst, L, images, camX, t, state):
    typ = L['type']
    if L.get('key') and typ != 'pick' and not state.get(L['key']):
        return
    im = images.get(L.get('image')) if L.get('image') else None
    k = L.get('k', 1.0)
    if typ == 'static':
        _comp(dst, im, L.get('x', 0), L.get('y', 0))
    elif typ == 'wrap':
        P = L['period']
        o = int(math.floor(camX * k + t * L.get('vx', 0.0))) % P
        h = min(L.get('h') or im.height, im.height)
        y = L.get('y', 0)
        if o + W <= im.width:
            _comp(dst, im.crop((o, 0, o + W, h)), 0, y)
        else:
            w1 = im.width - o
            _comp(dst, im.crop((o, 0, im.width, h)), 0, y)
            _comp(dst, im.crop((0, 0, W - w1, h)), w1, y)
    elif typ == 'pano':
        _comp(dst, im, L.get('x', 0) - math.floor(camX * k), L.get('y', 0))
    elif typ == 'image':
        x = L['x'] if L.get('screen') else L['x'] - math.floor(camX * k)
        _comp(dst, im, x, L['y'])
    elif typ == 'strip':
        n, fw, fh = L['n'], L['w'], L['h']
        f = int(math.floor(t * L['fps'])) % n
        x = L['x'] if L.get('screen') else L['x'] - math.floor(camX * k)
        _comp(dst, im.crop((f * fw, 0, f * fw + fw, fh)), x, L['y'])
    elif typ == 'pick':
        ims = L['images']
        v = state.get(L['key'], 0) or 0
        if L.get('values'):
            vals = L['values']
            i = min(range(len(vals)), key=lambda j: abs(vals[j] - v))
        else:
            i = int(round(clamp(v) * (len(ims) - 1)))
        k = L.get('k', 0.0)
        _comp(dst, images[ims[i]], L.get('x', 0) - math.floor(camX * k), L.get('y', 0))
    elif typ == 'clouds':
        span = L['span']
        for c in L['clouds']:
            x = (c['x0'] + t * c['vx'] - camX * c.get('k', 0.0)) % span - 100
            _comp(dst, images[c['image']], math.floor(x), c['y'])
    elif typ == 'neon':
        for s in L['signs']:          # 自检时全部当“亮着”（flick 的闪烁 JS 自己随机）
            _comp(dst, images[s['image']], s['x'] - math.floor(camX * k), s['y'])
    elif typ == 'reflect':
        ref_reflect(dst, L, images, camX, t)
    elif typ == 'tint':
        a = L.get('alpha', 0.3)
        lay = Image.new('RGBA', (W, H), tuple(int(L['color'][i:i + 2], 16) for i in (1, 3, 5)) + (int(255 * a),))
        dst.alpha_composite(lay)
    elif typ == 'petals':
        ref_petals(dst, L, camX, t)
    else:
        raise ValueError('ref_render 不认识的图层类型 ' + typ)


def ref_reflect(dst, L, images, camX, t):
    """湿路面倒影（香港，原片 hongkong_night 2996–3013 行）：
    第 r 行（r = 0..n−1）= 源图屏幕第 (y−2−2r) 和 (y−3−2r) 行的平均（源图已经减过 30；源图第 0 行 = 屏幕第
    srcY 行），列按 o = floor(camX·k) mod period 循环取；横移 dx = round(amp·sin(rk·r + freq·t)·(0.3 + r/n))
    （正数往右）；'lighter' 叠到 y + r 行，强度 a = a0 + (a1−a0)·r/n，r % 4 == 3 的行再 × wet。"""
    im = images[L['image']]
    P, y, n = L['period'], L['y'], L['n']
    sy = L.get('srcY', 0)
    o = int(math.floor(camX * L.get('k', 1.0))) % P
    src = np.array(im).astype(np.float32)
    cols = (np.arange(W) + o) % im.width
    for r in range(n):
        ra, rb = y - 2 - 2 * r - sy, y - 3 - 2 * r - sy
        row = (src[ra, cols] + src[rb, cols]) * 0.5
        dx = int(round(L.get('amp', 1.8) * math.sin(L.get('rk', 1.3) * r + L.get('freq', 6.0) * t)
                       * (0.3 + r / n)))
        row = np.roll(row, dx, axis=0)
        a = L['a0'] + (L['a1'] - L['a0']) * r / n
        if r % 4 == 3:
            a *= L.get('wet', 0.8)
        lay = Image.fromarray(np.clip(row[None], 0, 255).astype(np.uint8), 'RGBA')
        _lighter(dst, lay, 0, y + r, a)


def ref_petals(dst, L, camX, t):
    """校门飘落花瓣（原片 school_gate 2609–2619 行；JS 照这个写，种子 / 随机数自己定）。"""
    d = ImageDraw.Draw(dst)
    cols = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in L['colors']]
    s = camX
    for i in range(L['n']):
        per = hrange(L['per'][0], L['per'][1], i, 31)
        u = ((t + hash01(i, 32) * per) % per) / per
        x0 = hrange(L['x0'][0], L['x0'][1], i, 33)
        x = x0 - u * L['drift'] + math.sin(t * L['swayW'] + i) * L['sway'] - (s * L['k']) % L['wrapX']
        yy = L['y0'] + u * (L['y1'] - L['y0'])
        if -2 <= x < W and 0 <= yy < H:
            c = cols[1] if i % 2 else cols[0]
            d.point((round(x), round(yy)), fill=c + (255,))
            if int(t * 6 + i) % 3 == 0:
                d.point((round(x) + 1, round(yy)), fill=c + (255,))


def ref_render(stage, images, camX=0.0, t=0.0, state=None, fg=True, only=None):
    """导出层按 §3.6 公式重建一帧（黑底）。only = 只画这些类型（自检时排除 JS 自画的东西）。"""
    st = state or {}
    dst = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for L in stage['layers'] + (stage.get('fg', []) if fg else []):
        if only is not None and L['type'] not in only:
            continue
        ref_layer(dst, L, images, camX, t, st)
    return dst


# ============================================================ 导出上下文
class Ex:
    def __init__(self, c, check=True, preview=False, log=print):
        self.c = c
        self.check_on = check
        self.preview = preview
        self.log = log
        self.images = {}
        self.report = {}
        self.key = None
        self.packs = {}
        p = c.get('packs') if isinstance(c, dict) else None
        if not p:
            try:
                with open(os.path.join(REGISTRY, 'packs.json'), encoding='utf-8') as fh:
                    p = json.load(fh)
            except Exception:
                p = None
        if isinstance(p, dict):
            for short, v in p.items():
                for k in (v or {}).get('bg', []):
                    self.packs[k] = short

    def begin(self, key):
        self.key = key
        self.pack = self.packs.get(key) or DEFAULT_PACK.get(key) or 'common'
        self.report[key] = dict(pack=self.pack, checks=[], strips=[], notes=[])

    def img(self, name, im):
        k = 'bg/%s/%s' % (self.key, name)
        im = im.convert('RGBA')
        self.c['save_png'](im, k, self.pack)
        self.images[k] = im.copy()
        return k

    def strip(self, name, frames):
        w = frames[0].width * len(frames)
        if w > STRIP_HARD_W:
            raise ValueError('%s/%s 帧条 %d px 宽，超过 %d' % (self.key, name, w, STRIP_HARD_W))
        if w > STRIP_SOFT_W:
            self.note('帧条 %s 宽 %d px（> %d，手机上可能慢）' % (name, w, STRIP_SOFT_W))
        im = blank(w, frames[0].height)
        for i, f in enumerate(frames):
            im.paste(f, (i * f.width, 0))
        return self.img(name, im)

    def note(self, msg):
        self.report[self.key]['notes'].append(msg)
        self.log('    · ' + msg)

    def checked(self, label, n, limit=0, extra=''):
        ok = n <= limit
        self.report[self.key]['checks'].append(dict(label=label, diff=n, limit=limit, ok=ok, extra=extra))
        self.log('    %s %-46s 差 %5d px%s%s' % ('OK ' if ok else 'NG!', label, n,
                                                  ('（容许 %d）' % limit) if limit else '',
                                                  ('  ' + extra) if extra else ''))
        return ok

    def bake(self, name, box, n, fps, render, screen=True, key=None, k=None):
        """render(t) → 320×180 RGBA（叠加层或整帧）→ 裁 box → n 帧 strip。打印接缝 / 闭合指标。"""
        x0, y0, x1, y1 = [int(v) for v in box]
        frames = [render(i / fps).crop((x0, y0, x1, y1)) for i in range(n)]
        steps = [ndiff_rgba(frames[i], frames[i + 1]) for i in range(n - 1)]
        seam = ndiff_rgba(frames[-1], frames[0])
        close = ndiff_rgba(render(n / fps).crop((x0, y0, x1, y1)), frames[0])
        typ = int(np.median(steps)) if steps else 0
        mx = max(steps) if steps else 0
        self.report[self.key]['strips'].append(dict(name=name, n=n, fps=round(fps, 4), box=[x0, y0, x1, y1],
                                                    seam=seam, step_median=typ, step_max=mx, closure=close))
        self.log('    strip %-14s %3d 帧 @%6.3f fps  %3d×%-3d  接缝(末→首) %4d px  相邻帧中位 %4d / 最大 %4d  '
                 '闭合(t=n/fps vs 第0帧) %d' % (name, n, fps, x1 - x0, y1 - y0, seam, typ, mx, close))
        L = dict(type='strip', image=self.strip(name, frames), x=x0, y=y0, w=x1 - x0, h=y1 - y0, n=n,
                 fps=round(fps, 6))
        if screen:
            L['screen'] = True
        if k is not None:
            L['k'] = k
        if key:
            L['key'] = key
        return L

    def stage(self, w, ground, walk, layers, fg=None, anchors=None):
        st = dict(pack=self.pack, w=int(w), ground=int(ground), walk=[int(walk[0]), int(walk[1])],
                  anchors=anchors or {}, layers=layers, fg=fg or [])
        return st


# ============================================================ 各背景
# ---------------------------------------------------------------- title_pyramids
def exp_title_pyramids(ex):
    """标题底图：bg_egypt.pyramids(time='sunrise')，320 视窗、scroll 0。
    天空 + 太阳（static）→ 2 朵云（clouds，原片在沙丘后面，所以拆成“天空 / 云 / 地面”三层）→ 地面（static，
    远沙丘 + 金字塔 + 中沙丘 + 狮身人面像 + 近沙地，上半透明）。"""
    t2 = 'sunrise'
    sky = frame(0)
    info = E._sky_and_sun(sky, t2)
    land = FakeFr(0)
    E._scroll(land.img, E._desert_far(t2, seed=5), 0, E._HORIZON - 40 + 4)
    E._scroll(land.img, E._pyramid_layer(t2), 0, E._HORIZON + 6 - 100)
    E._scroll(land.img, E._desert_mid(t2, seed=13), 0, 138 - 70 + 14)
    sph = E._sphinx_img(t2)
    paste(land.img, sph, 22, 132 - sph.height)
    near, ny = E._desert_near(t2, seed=17)
    E._scroll(land.img, near, 0, ny)
    land_im, ly = crop_rows(land.img)
    # 云：原式 xx = (x + t·speed·(0.6+0.4·hash01(seed,i))) % (W + w) − w；JS clouds 同银魂：
    # x = mod(x0 + t·vx − camX·k, span) − 100 → span 取 440（≥ 420 才不会在屏幕里突然消失），x0 = 原片 t=0 的 x + 100
    p = E._tod(t2)
    cl, cs = p['cloud']
    clouds = []
    for i, (x, y, w, h) in enumerate(((20, 22, 50, 7), (220, 36, 34, 6))):
        im = E._cloud_img(41 + i, int(w), int(h), tuple(E.rgb(cl)), tuple(E.rgb(cs)))
        span0 = W + im.width
        x_t0 = x % span0 - im.width
        vx = 1.2 * (0.6 + 0.4 * hash01(41, i))
        clouds.append(dict(image=ex.img('cloud%d' % i, im), x0=round(x_t0 + 100, 3), y=y, vx=round(vx, 4), k=0))
    layers = [dict(type='static', image=ex.img('sky', sky.img)),
              dict(type='clouds', span=440, clouds=clouds),
              dict(type='static', image=ex.img('land', land_im), y=ly)]
    st = ex.stage(320, 150, (148, 178), layers,
                  anchors=dict(sun=pt(info['sun']), horizon=E._HORIZON, sphinx=[22 + sph.width // 2, 132]))
    if ex.check_on:
        fr = frame(0)
        E.pyramids(fr, 0, time=t2)
        ex.checked('t=0 整帧 vs pyramids(sunrise)', ndiff(ref_render(st, ex.images, 0, 0), fr.img))
        fr = frame(3.0)
        E.pyramids(fr, 0, time=t2)
        ex.checked('t=3 地面 y≥56（云会差 1 px 取整）', ndiff(ref_render(st, ex.images, 0, 3.0), fr.img,
                                                         box=(0, 56, W, H)))
    return st


# ---------------------------------------------------------------- world_map
def exp_world_map(ex):
    """旅行地图：bg_asia._map_layer(0/1) 两相位，每 0.6 s 换一张（strip 2 帧、fps 1/0.6）。
    城市坐标（CITIES）、标签偏移（_LABEL）、投影分段表（_LONK）进 anchors，S.route 用。"""
    frames = [A._map_layer(0), A._map_layer(1)]
    L = dict(type='strip', image=ex.strip('phase', frames), x=0, y=0, w=W, h=H, n=2, fps=round(1 / 0.6, 6),
             screen=True)
    extra = {'阿布扎比': pt(A.map_xy(54.4, 24.5)), '康翁波': pt(A.map_xy(32.93, 24.47)),
             '埃德富': pt(A.map_xy(32.87, 24.98))}
    anchors = dict(cities={k: list(v) for k, v in A.CITIES.items()}, extra=extra,
                   labels={k: list(v) for k, v in A._LABEL.items()}, compass=[292, 124],
                   lonk=[list(p) for p in A._LONK], lat=[A._LAT_TOP, A._LAT_BOT, A._Y_TOP, A._Y_BOT])
    st = ex.stage(320, 150, (140, 176), [L], anchors=anchors)
    if ex.check_on:
        for t in (0.0, 0.7, 1.3):
            fr = frame(t)
            A.world_map(fr)
            ex.checked('t=%.1f 整帧 vs world_map' % t, ndiff(ref_render(st, ex.images, 0, t), fr.img))
    return st


# ---------------------------------------------------------------- sky_day
SKY_SPEED = 30.0


def exp_sky_day(ex):
    """机外蓝天：_sky_grad('day')（static）+ _sky_layers() 4 层 wrap，画序 far → mid → sea → near。
    原式偏移 (scroll + t·speed)·k（bg_asia 的 _wrap_paste，scroll 越大画面越往右）。
    游戏里飞机机头朝右（驾驶舱 s06 就是朝右），云统一往左漂：vx = speed·k（正数 = 内容往左），
    和客舱窗外“云海向左卷”（规划 1-2）一致；原片这里是往右漂（报告 06 §1.3），属于有意改正。
    剧情要俯冲时加速：stage.state.speed（倍率，同银魂 wrap 的写法）或者直接改镜头 camX。"""
    far, mid, near, sea = A._sky_layers()
    layers = [dict(type='static', image=ex.img('grad', A._sky_grad('day')))]
    for name, im, k in (('far', far, 0.15), ('mid', mid, 0.4), ('sea', sea, 0.7), ('near', near, 1.0)):
        cim, y = crop_rows(im)
        layers.append(dict(type='wrap', image=ex.img(name, cim), period=im.width, k=k, y=y,
                           vx=round(SKY_SPEED * k, 4)))
    st = ex.stage(320, 150, (140, 176), layers, anchors=dict(cloud_top=152, sun=[40, 30]))
    if ex.check_on:
        for camX in (0, 20, 100, 200, 400):
            fr = frame(0)
            A.sky_day(fr, scroll=-camX, speed=SKY_SPEED)
            ex.checked('t=0 camX=%d vs sky_day(scroll=-camX)' % camX,
                       ndiff(ref_render(st, ex.images, camX, 0), fr.img))
    return st


# ---------------------------------------------------------------- sea_day
SEA_GLINT_N = 11


def exp_sea_day(ex):
    """平静海面（island=True，1-9 坠海后）：_sea_day_static(True)（static）
    + 云带 640×96（wrap，原式 t·2 + scroll·0.1 → k 0.1、vx −2，保持原片往右漂）
    + 22 行浪花：原片按行算（第 r 行周期 per = 18+3r、速度 4+1.5r px/s、视差 0.3+0.04r），
      每行就是一条 1 px 高的 wrap（period = per，vx = −(4+1.5r) 往右，k = 0.3+0.04r）——
      这样浪是真循环、帧条也不会太宽；原片 8 fps 跳帧，这里 floor 取整本来就是整像素跳（偏离见交付说明）
    + 太阳下的 36 个闪光：周期都是 1/2.2 s → strip 11 帧 @24.2 fps（严格闭合）。"""
    island = True
    layers = [dict(type='static', image=ex.img('static', A._sea_day_static(island)))]
    cim, cy = crop_rows(A._sea_day_clouds())
    layers.append(dict(type='wrap', image=ex.img('clouds', cim), period=640, k=0.1, y=cy, vx=-2.0))
    HZ = A._SEA_HZ
    for row in range(22):
        y = HZ + 2 + int((row / 21.0) ** 1.6 * 76)
        per = 18 + row * 3
        ln = 2 + row // 3
        light = mix((120, 180, 226), (80, 150, 210), row / 21)
        dark = mix((40, 110, 180), (10, 50, 110), row / 21)
        col = light if row % 2 == 0 else dark
        off0 = (hash01(row, 5) * per) % per
        c0 = round(-per + off0) % per                     # t=0 时原片短线的起点（屏幕 x ≡ c0）
        one = blank(per, 1)
        ImageDraw.Draw(one).line((0, 0, ln, 0), fill=col + (255,))
        one = roll_x(one, -c0)                            # 起点挪到第 c0 列
        layers.append(dict(type='wrap', image=ex.img('wave%02d' % row, tile_to(one, per, per + W)), period=per,
                           k=round(0.3 + row * 0.04, 4), y=y, vx=-(4 + row * 1.5)))

    def glints(t):
        f = FakeFr(t)
        d = f.d
        for i in range(36):
            gy = HZ + 2 + int(hash01(i, 90) ** 1.3 * 70)
            spread = 6 + (gy - HZ) * 0.45
            gx = 236 + hrange(-spread, spread, i, 91)
            ph = (t * 2.2 + hash01(i, 92)) % 1.0
            if ph < 0.45:
                c = (255, 255, 240) if ph < 0.2 else (200, 230, 250)
                d.point((round(gx), gy), fill=c + (255,))
                if ph < 0.12 and gy > HZ + 30:
                    d.point((round(gx) - 1, gy), fill=c + (255,))
                    d.point((round(gx) + 1, gy), fill=c + (255,))
        return f.img
    bb = None
    for i in range(SEA_GLINT_N):
        b = glints(i / (2.2 * SEA_GLINT_N)).getbbox()
        bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    layers.append(ex.bake('glint', bb, SEA_GLINT_N, 2.2 * SEA_GLINT_N, glints))
    st = ex.stage(320, 150, (140, 176), layers, anchors=dict(horizon=HZ, sun=[236, 34]))
    if ex.check_on:
        fr = frame(0)
        A.sea_day(fr, island=island)
        ex.checked('t=0 整帧 vs sea_day(island)', ndiff(ref_render(st, ex.images, 0, 0), fr.img))
        fr = frame(2.5)                      # t·2 取整数时 floor 和原片的 −floor 一致（其余时刻差 1 列，看不出来）
        A.sea_day(fr, island=island)
        ex.checked('t=2.5 天空 + 云 y<100', ndiff(ref_render(st, ex.images, 0, 2.5), fr.img, box=(0, 0, W, 100)))
    return st


# ---------------------------------------------------------------- jail_cell
JAIL_CX = 182          # 规划 §5.1 地图表：jail_bars(bend, cx=182)
JAIL_BULB_N = 50       # 12 fps × 50 帧 = 4.17 s；原片 k = int(t·12) 的 0..49 里第 10、30 帧灯泡暗下去


def exp_jail_cell(ex):
    """拘留所：静态底图（_jail_static + 窗口光束 + 灯泡亮着）+ 灯泡闪 strip（50 帧 @12 fps，
    逐帧用原函数渲、裁灯泡那一块，原片 hash01(k,77)<0.04 的帧照搬）+ 收音机 LED（2 帧 @2 fps）
    + 前景铁栏 pick（_bars_layer bq 0,10,…,50 = bend 0,0.2,…,1.0，cx 182，key 'bend'）。"""
    def full(t):
        fr = frame(t)
        A.jail_cell(fr)
        return fr.img
    base = full(0.0)                          # k=0 灯泡亮、t<0.5 LED 灭
    layers = [dict(type='static', image=ex.img('static', base))]
    layers.append(ex.bake('bulb', (129, 14, 192, 68), JAIL_BULB_N, 12.0, full))
    layers.append(ex.bake('led', (224, 109, 225, 110), 2, 2.0, full))
    bars = [ex.img('bars%d' % i, A._bars_layer(bq, 6, 314, JAIL_CX, 0, 146).crop((0, 0, W, 147)))
            for i, bq in enumerate((0, 10, 20, 30, 40, 50))]
    fg = [dict(type='pick', images=bars, key='bend', x=0, y=0, k=0)]
    anchors = dict(cell_ground=130, cell_walk=[122, 138], cell_x=[96, 236], corridor_walk=[150, 176],
                   bunk=[148, 97], bunk_feet=[148, 124], bars=[6, 314, 0, 145], bars_cx=JAIL_CX,
                   window=[206, 38, 236, 56], radio=[208, 98], bulb=[160, 41])
    st = ex.stage(320, 166, (122, 138), layers, fg, anchors)
    if ex.check_on:
        for k_ in (0, 10, 13, 30, 47):
            t = k_ / 12.0
            fr = frame(t)
            A.jail_cell(fr)
            A.jail_bars(fr, bend=0.0, cx=JAIL_CX)
            ex.checked('t=%.3f(k=%d) 整帧+铁栏 vs 原函数' % (t, k_),
                       ndiff(ref_render(st, ex.images, 0, t, dict(bend=0)), fr.img))
        for bend in (0.2, 0.6, 1.0):
            fr = frame(0)
            A.jail_cell(fr)
            A.jail_bars(fr, bend=bend, cx=JAIL_CX)
            ex.checked('bend=%.1f 铁栏 vs jail_bars' % bend,
                       ndiff(ref_render(st, ex.images, 0, 0, dict(bend=bend)), fr.img))
    return st


# ---------------------------------------------------------------- kujo_house_*
FURIN_L, FURIN_FPS = 12.0, 12.0          # 风铃：0.25·sin(2.1t)+0.1·sin(3.7t+1) → 12 s 里取整 4 / 7 周
FURIN_W1, FURIN_W2 = 2 * math.pi * 4 / FURIN_L, 2 * math.pi * 7 / FURIN_L       # 2.094 / 3.665
LEAF_L, LEAF_FPS = 1 / 0.12, 4.8         # 落叶：u = t·0.12 周期 8.33 s；左右摆 sin(2t) 取整成 3 周
LEAF_W = 2 * math.pi * 3 / LEAF_L        # 2.262
BEAM_N = 16                              # 晨光呼吸 sin(0.8t)：16 帧一周 7.85 s


def _furin_loop(f, x, y, t):
    """原 _furin（2322 行），两个频率换成 12 s 闭合的 FURIN_W1 / FURIN_W2（差 0.3% / 0.9%）。"""
    d = f.d
    c4 = A._c4
    ang = 0.25 * math.sin(t * FURIN_W1) + 0.1 * math.sin(t * FURIN_W2 + 1)
    col = (150, 210, 240)
    d.line((x, y - 6, x, y), fill=c4((60, 50, 40)))
    d.ellipse((x - 3, y, x + 3, y + 5), fill=c4(col), outline=c4((60, 90, 110)))
    d.point((x - 1, y + 1), fill=c4((255, 255, 255)))
    ex_ = x + math.sin(ang) * 10
    ey = y + 5 + math.cos(ang) * 10
    d.line((x, y + 5, ex_, ey), fill=c4((200, 200, 200)))
    d.rectangle((round(ex_) - 1, round(ey), round(ex_) + 1, round(ey) + 5), fill=c4((230, 90, 90)))


def exp_kujo(ex, variant):
    """空条家和室（_kujo_static(variant)）：白天的固定斜光烘进底图；风铃 strip（12 s / 144 帧，
    频率取整成真循环）；两片落叶 strip（8.33 s / 40 帧 @4.8 fps，只在庭院那一块）；
    早晨的两道斜光呼吸 strip（16 帧一周，半透明叠加层）。黄昏版（乌鸦）M1 不导出。"""
    P = A._KJ[variant]
    base = A._kujo_static(variant).copy()
    if variant == 'day':
        A._blend_poly(base, [(206, 134), (206, 140), (150, 180), (110, 180)], P['light'], 30)
    layers = [dict(type='static', image=ex.img('static', base))]
    if variant in ('morning', 'dusk'):
        def beams(t):
            img = blank()
            a = int(P['la'] * (0.85 + 0.15 * math.sin(t * 0.8)))
            A._blend_poly(img, [(206, 60), (206, 134), (120, 180), (60, 180)], P['light'], a)
            A._blend_poly(img, [(206, 36), (206, 58), (40, 180), (10, 180)], P['light'], a // 2)
            return img
        layers.append(ex.bake('beams', (10, 36, 207, 180), BEAM_N, BEAM_N * 0.8 / (2 * math.pi), beams))

    def furin(t):
        f = FakeFr(t)
        _furin_loop(f, 262, 40, t)
        return f.img
    layers.append(ex.bake('furin', (255, 33, 270, 62), int(FURIN_L * FURIN_FPS), FURIN_FPS, furin))
    leaf_col = (110, 150, 70) if variant == 'day' else (250, 190, 200)

    def leaves(t):
        f = FakeFr(t)
        for i in range(2):
            u = ((t * 0.12 + i * 0.5) % 1.0)
            lx = 300 - u * 80 + math.sin(t * LEAF_W + i) * 4
            ly = 50 + u * 80
            f.d.point((round(lx), round(ly)), fill=A._c4(leaf_col))
        return f.img
    layers.append(ex.bake('leaves', (214, 49, 306, 131), int(round(LEAF_L * LEAF_FPS)), LEAF_FPS, leaves))
    anchors = dict(garden=[206, 34, 318, 134], table=[48, 154], table_box=[14, 146, 82, 170], walk_x=[90, 300],
                   furin=[262, 40], alcove=[14, 35, 86, 128], fusuma=[90, 35, 204, 134])
    st = ex.stage(320, 160, (148, 176), layers, anchors=anchors)
    if ex.check_on:
        fr = frame(0)
        A.kujo_house(fr, variant=variant)
        ex.checked('t=0 整帧 vs kujo_house(%s)' % variant, ndiff(ref_render(st, ex.images, 0, 0), fr.img))
        fr = frame(2.5)
        A.kujo_house(fr, variant=variant)
        m = rect_mask([(255, 33, 270, 62), (214, 49, 306, 131), (10, 36, 207, 180)], keep=False)
        ex.checked('t=2.5 除风铃/落叶/光束外 vs 原函数', ndiff(ref_render(st, ex.images, 0, 2.5), fr.img, mask=m))
    return st


# ---------------------------------------------------------------- kujo_bedroom_dusk
ANDON_K, ANDON_FPS = 12, 12.0            # 行灯 noise1(3t, 5)：做成 12 个结点的周期噪声（4 s 闭合）


def _noise_loop(x, seed, K):
    """原 core.noise1（182 行）的周期版：结点 i 取 hash01(i mod K, seed)，x 在 [0, K) 循环。"""
    i = math.floor(x)
    f = x - i
    a = hash01(i % K, seed) * 2 - 1
    b = hash01((i + 1) % K, seed) * 2 - 1
    u = f * f * (3 - 2 * f)
    return a + (b - a) * u


def exp_kujo_bedroom_dusk(ex):
    """荷莉的卧室（黄昏）：_bedroom_static('dusk') + 行灯闪 strip（光晕 + 灯罩，48 帧 @12 fps）。"""
    base = A._bedroom_static('dusk')

    def andon(t):
        img = blank()
        fl = 0.85 + 0.15 * _noise_loop(t * 3, 5, ANDON_K)
        A._glow(img, 305, 144, 40, 28, (255, 190, 100), int(70 * fl), rings=4)
        d = ImageDraw.Draw(img)
        d.rectangle((298, 134, 312, 154), fill=A._c4(mix((240, 200, 130), (255, 236, 170), fl)))
        d.line((305, 134, 305, 154), fill=A._c4((90, 56, 32)))
        d.line((298, 144, 312, 144), fill=A._c4((90, 56, 32)))
        return img
    layers = [dict(type='static', image=ex.img('static', base)),
              ex.bake('andon', (265, 116, 320, 173), int(ANDON_K / 3 * ANDON_FPS), ANDON_FPS, andon)]
    anchors = dict(futon=[150, 166], window=[118, 38, 300, 112], andon=[305, 144], walk_x=[40, 290],
                   shelf=[256, 124, 296, 142], tray=[222, 152, 252, 164])
    st = ex.stage(320, 158, (150, 176), layers, anchors=anchors)
    if ex.check_on:
        fr = frame(0)
        A.kujo_bedroom(fr, variant='dusk')
        ex.checked('t=0 整帧 vs kujo_bedroom(dusk)', ndiff(ref_render(st, ex.images, 0, 0), fr.img))
        fr = frame(1.7)
        A.kujo_bedroom(fr, variant='dusk')
        ex.checked('t=1.7 除行灯外 vs 原函数', ndiff(ref_render(st, ex.images, 0, 1.7), fr.img,
                                                 mask=rect_mask([(265, 116, 320, 173)], keep=False)))
    return st


# ---------------------------------------------------------------- school_gate
def exp_school_gate(ex):
    """春天的校门：_school_layers() 远层 400 宽（pano k 0.5）+ 近层 480 宽（pano k 1），不循环；
    26 片飘落花瓣 = petals 层（JS 照原式画，字段把原式的常数都带上）。"""
    far, near = A._school_layers()
    petals = dict(type='petals', n=26, colors=['#f4a0be', '#ffd6e4'], seed=31, y0=-6, y1=184,
                  vx=-12.7, vy=34.5, per=[4.0, 7.0], x0=[-20, W + 60], drift=70, sway=6, swayW=2.3,
                  k=0.2, wrapX=40)
    layers = [dict(type='pano', image=ex.img('far', far), k=0.5, x=0, y=0),
              dict(type='pano', image=ex.img('near', near), k=1.0, x=0, y=0),
              petals]
    anchors = dict(gate=[206, 294], walk_x=[16, 464], clock=[205, 29], building_door=[205, 104],
                   trees=[[40, 62], [150, 54], [350, 58], [446, 66]])
    st = ex.stage(480, 150, (140, 176), layers, anchors=anchors)
    if ex.check_on:
        for camX in (0, 40, 80, 120, 160):
            for t in (0.0, 1.9):
                fr = frame(t)
                A.school_gate(fr, scroll=camX)
                got = ref_render(st, ex.images, camX, t)
                ex.checked('camX=%d t=%.1f 整帧（含花瓣）vs school_gate' % (camX, t), ndiff(got, fr.img))
    return st


# ---------------------------------------------------------------- dusk_gate (s05)
DG_GLINT_L, DG_GLINT_FPS = 3.0, 12.0     # 路面反光：闪 0.5 s 一周；左右晃 sin(2t) 取整成 3 s 一周
DG_GLINT_W = 2 * math.pi / DG_GLINT_L


def exp_dusk_gate(ex):
    """空条家门口的黄昏（s05 自绘 dusk_gate，序-18 出发过场）：
    天空 + 落日（static）→ 细云条（wrap k 0，往左 3 px/s；原片 320 一跳，这里按 640 真循环）
    → 远处东京（pano k 0.25）→ 三只乌鸦（clouds，原片 11 s 一趟，这里 13.3 s）
    → 中景屋顶（pano k 0.6）→ 电线杆 + 电线（pano k 0.8，原片每帧画，这里烘成一张）
    → 近景院墙 + 门 + 松（pano k 1，x −40）→ 路面反光（strip，screen）。
    镜头 camX −40…100（地图 0…420）。"""
    s05 = scene('s05_holly')
    T_F = s05.T_F
    sky = s05._dusk_sky()
    clouds = roll_x(s05._dusk_clouds(), 40)          # 原片 t=0 时从第 40 列开始看
    cim, cy = crop_rows(clouds)
    layers = [dict(type='static', image=ex.img('sky', sky)),
              dict(type='wrap', image=ex.img('streaks', cim), period=640, k=0.0, y=cy, vx=3.0)]
    far = s05._dusk_far()
    layers.append(dict(type='pano', image=ex.img('far', far), k=0.25, x=0, y=0))
    # 乌鸦：原式 u = ((t−T_F)·0.09 + 0.13i) % 1，bx = 330 − 360u + 7i；JS clouds：x = mod(x0 + vx·t, span) − 100
    crows = []
    c = (30, 12, 34, 255)
    bird = blank(7, 3)
    ImageDraw.Draw(bird).line((0, 0, 3, 2, 6, 0), fill=c)
    kbird = ex.img('crow', bird)
    for i in range(3):
        u0 = ((0 - T_F) * 0.09 + i * 0.13) % 1.0
        bx0 = 330 - u0 * 360 + i * 7
        by = 64 + i * 7
        crows.append(dict(image=kbird, x0=round(bx0 - 3 + 100, 3), y=by - 2, vx=-0.09 * 360, k=0))
    layers.append(dict(type='clouds', span=430, clouds=crows))
    layers.append(dict(type='pano', image=ex.img('mid', s05._dusk_mid()), k=0.6, x=0, y=0))
    # 电线杆：_poles(fr, 0) 画到透明图上，左边那根“从屏幕左缘拉过来的线”改成从世界 x −48 拉过来
    POX = 48
    poles = blank(W + 200 + POX, H)
    pf = FakeFr(0, poles)
    _poles_world(pf, POX)
    pb = poles.getbbox()
    pim = poles.crop((pb[0], 0, pb[2], H))
    layers.append(dict(type='pano', image=ex.img('poles', pim), k=0.8, x=-POX + pb[0], y=0))
    layers.append(dict(type='pano', image=ex.img('near', s05._dusk_near()), k=1.0, x=-s05.NEAR_OX, y=0))

    def glitter(t):
        f = FakeFr(t)
        for i in range(10):
            x = 212 + hrange(-40, 40, i, 41) + math.sin(t * DG_GLINT_W + i) * 2
            y = 152 + i * 2
            if blink(t + hash01(i, 42), 0.5, 0.6):
                f.d.line((round(x), y, round(x) + int(hrange(2, 7, i, 43)), y), fill=(200, 96, 80, 255))
        return f.img
    layers.append(ex.bake('glitter', (168, 152, 262, 171), int(DG_GLINT_L * DG_GLINT_FPS), DG_GLINT_FPS, glitter))
    anchors = dict(gate=[39, 101, 85, 147], gate_posts=[[30, 38], [86, 94]], door_x=62, sun=[212, 120],
                   cam=[-40, 100], wall_end=128, walk_x=[0, 420])
    st = ex.stage(420, 152, (148, 172), layers, anchors=anchors)
    if ex.check_on:
        excl = [(0, 58, W, 86)]                       # 乌鸦飞过的那一带（clouds 层，不逐帧比）
        for camX in (-40, 0, 40, 100):
            fr = frame(0)
            s05.dusk_gate(fr, camX)
            m = rect_mask(excl + ([(0, 50, 150 - int(0.8 * camX) - 6, 80)] if camX else []), keep=False)
            ex.checked('t=0 camX=%d 除乌鸦带 vs s05.dusk_gate' % camX,
                       ndiff(ref_render(st, ex.images, camX, 0), fr.img, mask=m), limit=0,
                       extra='（camX≠0 时左缘那根电线另算）' if camX else '')
    return st


def _poles_world(fr, ox):
    """s05._poles(fr, scroll=0) 的同款，整体右移 ox（图里 x = 世界 x + ox）；左缘电线从世界 −ox 拉到第一根杆。"""
    d = fr.d
    col = (30, 12, 34, 255)
    pxs = [p + ox for p in (150, 300, 450)]
    for p in pxs:
        d.rectangle((p, 52, p + 2, 150), fill=col)
        d.rectangle((p - 8, 58, p + 10, 59), fill=col)
        d.rectangle((p - 6, 66, p + 8, 66), fill=col)
        d.point((p - 7, 57), fill=col)
        d.point((p + 9, 57), fill=col)
    for a_, b_ in zip(pxs, pxs[1:]):
        for k, (yo, sag) in enumerate(((57, 12), (57, 10), (65, 9))):
            xa = a_ + (-7 if k == 0 else 9 if k == 1 else -5)
            xb = b_ + (-7 if k == 0 else 9 if k == 1 else -5)
            prev = None
            for s in np.linspace(0, 1, 40):
                xx = xa + (xb - xa) * s
                yy = yo + sag * 4 * s * (1 - s)
                if prev:
                    d.line((prev[0], prev[1], round(xx), round(yy)), fill=col)
                prev = (round(xx), round(yy))
    x0 = pxs[0] - 7
    # 原片：(0,70) → (143,57)；同一条直线往左延长到世界 −ox
    y_left = 70 + (57 - 70) * (0 - ox - 0) / (143 - 0)
    d.line((0, round(y_left), ox, 70), fill=col)
    d.line((ox, 70, x0, 57), fill=col)


# ---------------------------------------------------------------- cockpit (s06)
CK_L, CK_FPS = 2.0, 12.0                 # 驾驶舱：挡风玻璃 / 警报都做成 2 s 闭合
CK_BANK0, CK_HY = -16.0, 66.0            # 机身侧倾（原片 −26 → −12 之间取中）、地平线高度
CK_RZ, CK_RU, CK_WB = 1.5, 2.5, 2 * math.pi * 3 / CK_L     # 原 1.7 / 2.3 / 9.0 → 取整成 2 s 里 3 / 5 / 3 周
CK_DIAL1, CK_DIAL2 = -2 * math.pi * 4 / CK_L, 2 * math.pi * 2 / CK_L    # 原 −14 / 5 rad/s


def _ws_view_loop(s06, img, t):
    """s06._ws_view（526 行）的循环版：浪花 / 云絮 / 侧倾抖动的速率换成 2 s 闭合的 CK_RZ / CK_RU / CK_WB。"""
    vw, vh = 176, 150
    v = Image.new('RGBA', (vw, vh), (0, 0, 0, 255))
    d = ImageDraw.Draw(v)
    hy = int(CK_HY)
    bank = CK_BANK0 + 2.5 * math.sin(t * CK_WB)
    gradient(v, (0, 0, vw, hy), ['#7ab4f8', '#d8ecff'], bands=4)
    gradient(v, (0, hy, vw, vh), ['#6aaeea', '#3a7ccc', '#2658a8'], bands=5)
    d.line((0, hy, vw, hy), fill='#e8f4ff')
    d.polygon([(96, hy), (106, hy - 4), (114, hy - 3), (124, hy)], fill='#5a7890')
    for i in range(34):
        z = (hash01(i, 5) + t * CK_RZ) % 1.0
        yy = hy + 2 + (vh - hy - 2) * z * z
        xx = (hash01(i, 6) - 0.5) * vw * (0.6 + 1.4 * z) + vw / 2
        L = 2 + 14 * z
        col = (255, 255, 255) if hash01(i, 7) < 0.5 else (170, 214, 255)
        d.line((round(xx - L / 2), round(yy), round(xx + L / 2), round(yy)), fill=col)
    for i in range(3):
        u = (hash01(i, 9) + t * CK_RU) % 1.0
        cx = vw * hash01(i, 10)
        cy = vh * (1.2 - 1.6 * u)
        d.ellipse((cx - 14, cy - 5, cx + 14, cy + 5), fill=(236, 244, 255))
    v = v.rotate(bank, resample=Image.NEAREST)
    full = blank()
    full.paste(v, (s06._WS_C[0] - vw // 2, s06._WS_C[1] - vh // 2))
    img.paste(full, (0, 0), s06._ws_mask())
    img.alpha_composite(s06._ws_overlay())


def _ck_panel(d, t, needles_only_rest=False):
    """s06.shot_cockpit 593–606 行：6 个红色警告灯（3 Hz）、主警告（2 Hz）、两个表的指针。"""
    if not needles_only_rest:
        for i in range(6):
            on = int(t * 6 + i * 0.5) % 2 == 0
            c = (255, 48, 48) if on else (90, 20, 26)
            d.rectangle((210 + i * 7, 113, 214 + i * 7, 116), fill=c)
        if int(t * 4) % 2 == 0:
            d.rectangle((258, 112, 272, 118), fill=(255, 60, 40))
            d.line((265, 113, 265, 115), fill=(255, 255, 255))
            d.point((265, 117), fill=(255, 255, 255))
    ang = t * CK_DIAL1
    d.line((244, 126, round(244 + 5 * math.cos(ang)), round(126 + 5 * math.sin(ang))), fill=(255, 255, 255))
    ang2 = t * CK_DIAL2
    d.line((266, 126, round(266 + 5 * math.cos(ang2)), round(126 + 5 * math.sin(ang2))), fill=(255, 216, 60))


def _ck_yoke(d, gx):
    """s06._yoke（558 行），不画抖杆灯。"""
    y = 124
    d.rectangle((gx, y - 2, 204, y + 2), fill='#15161f')
    d.line((gx, y - 1, 204, y - 1), fill='#5a6078')
    d.rectangle((gx - 3, y - 12, gx + 1, y + 11), fill='#15161f')
    d.line((gx - 2, y - 11, gx - 2, y + 10), fill='#4a5068')
    d.rectangle((gx - 5, y - 14, gx + 1, y - 11), fill='#15161f')


def exp_cockpit(ex):
    """驾驶舱（s06 自绘，侧视、机头朝右）：_cockpit_bg() + 操纵杆（gx 176）+ 两个表的指针（静止）
    → 挡风玻璃 strip（_ws_view 的循环版 + 玻璃框 / 反光，24 帧 @12 fps）
    → 警报 strip ×2（key 'alarm'：面板警告灯 + 表针乱转；门上方的红色旋转警灯光晕），剧情 stage.state.alarm = true 打开
    → 操纵杆 pick（key 'yoke'：0 = 原位，1 = 乔瑟夫拉到底 gx 171）。
    原片的整屏红闪、机舱倾斜、震屏是镜头效果，交给剧情（G.flash / G.cam），不烘进背景。"""
    s06 = scene('s06_plane')
    fx = importlib.import_module('engine.fx')
    base = s06._cockpit_bg().copy()
    d = ImageDraw.Draw(base)
    _ck_yoke(d, 176)
    _ck_panel(d, 0, needles_only_rest=True)
    d.rectangle((26, 18, 34, 23), fill=(110, 26, 34))              # 警灯灯罩（不亮）

    def ws(t):
        img = base.copy()
        _ws_view_loop(s06, img, t)
        return img

    def panel(t):
        img = s06._cockpit_bg().copy()
        dd = ImageDraw.Draw(img)
        _ck_yoke(dd, 176)
        _ck_panel(dd, t)
        return img

    def beacon(t):
        f = FakeFr(t, s06._cockpit_bg().copy())
        f.d = ImageDraw.Draw(f.img)
        pulse = 0.5 + 0.5 * math.cos(t * 2 * math.pi * 2.5)
        fx.glow(f, 30, 20, 18 + 16 * pulse, '#ff2030', alpha=0.55, add=True)
        f.d.rectangle((26, 18, 34, 23), fill=(255, 64, 64) if pulse > 0.5 else (170, 30, 40))
        return f.img
    n = int(CK_L * CK_FPS)
    layers = [dict(type='static', image=ex.img('static', base)),
              ex.bake('windshield', (196, 13, 320, 102), n, CK_FPS, ws),
              ex.bake('alarm_panel', (208, 110, 274, 133), n, CK_FPS, panel, key='alarm'),
              ex.bake('alarm_beacon', (0, 0, 66, 56), n, CK_FPS, beacon, key='alarm')]
    yk = []
    for gx in (176, 171):                         # 0 = 原位（和底图一样），1 = 拉到底（原片 CK_GRAB 之后 gx 171）
        img = s06._cockpit_bg().copy()
        dd = ImageDraw.Draw(img)
        _ck_panel(dd, 0, needles_only_rest=True)
        _ck_yoke(dd, gx)
        yk.append(ex.img('yoke%d' % len(yk), img.crop((164, 108, 206, 138))))
    layers.append(dict(type='pick', images=yk, key='yoke', x=164, y=108, k=0))
    anchors = dict(windshield=[list(p) for p in s06._WS_POLY], seat=[116, 150], yoke=[176, 124],
                   doorway=[4, 24, 46, 168], beacon=[30, 20], panel=[204, 110, 320, 170], walk_x=[60, 196])
    st = ex.stage(320, s06.G_CK, (160, 178), layers, anchors=anchors)
    if ex.check_on:
        ref0 = s06._cockpit_bg().copy()
        dd = ImageDraw.Draw(ref0)
        f0 = FakeFr(0, ref0)
        s06._ws_view(f0, 0, CK_BANK0, CK_HY)
        ref0.alpha_composite(s06._ws_overlay())
        _ck_yoke(ImageDraw.Draw(ref0), 176)
        m = rect_mask([(208, 110, 274, 133), (26, 18, 35, 24)], keep=False)
        ex.checked('t=0 底图+挡风玻璃 vs _cockpit_bg+_ws_view+_yoke', ndiff(ref_render(st, ex.images, 0, 0), ref0,
                                                                           mask=m))
        fr = frame(0)
        fr.img.paste(s06._cockpit_bg(), (0, 0))
        f1 = FakeFr(0, fr.img)
        _ck_yoke(f1.d, 176)
        ImageDraw.Draw(fr.img)
        dd = ImageDraw.Draw(fr.img)
        for i in range(6):
            on = int(0 * 6 + i * 0.5) % 2 == 0
            dd.rectangle((210 + i * 7, 113, 214 + i * 7, 116), fill=(255, 48, 48) if on else (90, 20, 26))
        dd.rectangle((258, 112, 272, 118), fill=(255, 60, 40))
        dd.line((265, 113, 265, 115), fill=(255, 255, 255))
        dd.point((265, 117), fill=(255, 255, 255))
        dd.line((244, 126, 249, 126), fill=(255, 255, 255))
        dd.line((266, 126, 271, 126), fill=(255, 216, 60))
        fx.glow(FakeFr(0, fr.img), 30, 20, 34, '#ff2030', alpha=0.55, add=True)
        dd.rectangle((26, 18, 34, 23), fill=(255, 64, 64))
        got = ref_render(st, ex.images, 0, 0, dict(alarm=True))
        ex.checked('t=0 警报两块 vs shot_cockpit 同款画法', ndiff(got, fr.img, box=(0, 0, 66, 56))
                   + ndiff(got, fr.img, box=(208, 110, 274, 133)))
    return st


# ---------------------------------------------------------------- hongkong_night
HK_W = A._HK_W          # 640


def _hk_shopfronts():
    """照 _hk_layers 近景楼面的循环（2900–2938 行）重算每家店的 x 范围 → [(x, w, k)]。"""
    edges = [0]
    for g0, g1 in A._HK_GAPS:
        edges += [g0, g1]
    edges.append(HK_W)
    out, k = [], 0
    for seg in range(0, len(edges), 2):
        sx0, sx1 = edges[seg], edges[seg + 1]
        x = sx0
        while x < sx1:
            w = min(int(hrange(44, 70, k, 21)), sx1 - x)
            if sx1 - (x + w) < 20:
                w = sx1 - x
            out.append((x, w, k))
            x += w
            k += 1
    return out


def exp_hongkong_night(ex):
    """香港夜街（地图宽 960，近景 640 循环）：
    天空 + 星星 + 湿路面底色（static，y 153 以下是路面渐变 + 每 4 行一条暗线）
    → 远处天际线（wrap k 0.25、vx −0.5，天线红灯常亮烘进图里）→ 唐楼（wrap k 0.6）→ 临街楼面（wrap k 1）
    → 17 块亮霓虹（neon，按世界坐标放，640 以后的再放一份；5 块 flick）
    → 湿路面倒影（reflect，源图 = 近景压在中 / 远景上、减 30；'lighter' 叠加，同原式）
    → 路面黄线（wrap period 40，世界坐标，修原片标线反着走的 bug）。"""
    sky, far, mid, near = A._hk_layers()
    rows = H - 153
    # --- static：天空 + 路面底色
    st_img = sky.copy()
    a = np.array(st_img).astype(np.float32)
    yy = np.arange(rows, dtype=np.float32)
    street = np.zeros((rows, W, 3), np.float32)
    street[:] = np.array((22, 18, 34), np.float32)
    street += (yy / rows * 12)[:, None, None]
    wet = (yy.astype(int) % 4 == 3)
    street[wet] *= 0.8
    a[153:, :, :3] = street
    st_img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    # --- 远景：天线红灯常亮（原片 int(t·1.5)%2 闪；wrap 层不能闪，见交付说明）
    far2 = far.copy()
    fd = ImageDraw.Draw(far2)
    for i in range(0, 22, 4):
        ax = (i * 29 + hrange(-5, 5, i, 1) + hrange(14, 24, i, 2) // 2) % HK_W
        top = int(hrange(30, 80, i, 3)) - 8
        fd.point((round(ax), top), fill=A._c4((255, 60, 60)))
    layers = [dict(type='static', image=ex.img('sky', st_img))]
    for name, im, k, vx in (('far', far2, 0.25, -0.5), ('mid', mid, 0.6, 0.0), ('near', near, 1.0, 0.0)):
        cim, y = crop_rows(im)
        L = dict(type='wrap', image=ex.img(name, cim), period=HK_W, k=k, y=y)
        if vx:
            L['vx'] = vx
        layers.append(L)
    # --- 霓虹（亮版），世界坐标：x = sx − pad（+640 再放一份，覆盖到 960 + 余量）
    signs = []
    for idx, (sx, sy, kind, n, ci, sd, fl) in enumerate(A._HK_SIGNS):
        pad = 7 if kind in ('V', 'H') else 5
        k_img = ex.img('neon%02d' % idx, A._neon_sign(kind, n, ci, sd, True))
        for dx in (0, HK_W):
            if sx + dx - pad < 960 + 40:
                signs.append(dict(image=k_img, x=sx + dx - pad, y=sy - pad, flick=bool(fl)))
    layers.append(dict(type='neon', signs=signs, k=1.0))
    # --- 倒影源图：近景压在中景 / 远景 / 天空上（都按 0 偏移）再减 30
    comp = blank(HK_W, H)
    for x in range(0, HK_W, W):
        comp.paste(sky, (x, 0))
    comp.alpha_composite(far2)
    comp.alpha_composite(mid)
    comp.alpha_composite(near)
    ca = np.array(comp).astype(np.float32)
    ca[..., :3] = np.maximum(ca[..., :3] - 30, 0)
    ca[..., 3] = 255
    refl = Image.fromarray(ca.astype(np.uint8), 'RGBA').crop((0, 96, HK_W, 153))
    # 倒影层读源图的第 (y−2−2r, y−3−2r) 行；裁掉上面以后源图在 y0 = 96 起，JS 里 image 行号 = 屏幕行 − 96
    layers.append(dict(type='reflect', image=ex.img('reflect_src', refl), y=153, n=rows, a0=0.62, a1=0.27,
                       period=HK_W, k=1.0, blend='lighter', srcY=96, amp=1.8, rk=1.3, freq=6.0, wet=0.8))
    road = blank(40, 1)
    ImageDraw.Draw(road).line((0, 0, 16, 0), fill=A._c4((170, 150, 60)))
    layers.append(dict(type='wrap', image=ex.img('road', tile_to(road, 40, 40 + W)), period=40, k=1.0, y=170))
    # --- 锚点：橱窗（规划 1-11 的 (230,120)）、小巷、霓虹
    shop = None
    for x, w, k in _hk_shopfronts():
        if x + 6 <= 230 <= x + w - 6:
            shop = [x + 6, 112, x + w - 6, 146]
    anchors = dict(curb=152, shopwindow=shop, alleys=[list(g) for g in A._HK_GAPS],
                   alleys2=[[g0 + HK_W, g1 + HK_W] for g0, g1 in A._HK_GAPS if g0 + HK_W < 960],
                   neon=[[sx, sy] for (sx, sy, *_r) in A._HK_SIGNS], period=HK_W, walk_x=[0, 960])
    st = ex.stage(960, 154, (150, 176), layers, anchors=anchors)
    if ex.check_on:
        # 排除：flick 的霓虹（原片 t=0 可能是灭的）；camX≠0 时全部霓虹（原片放错位置——就是要修的 bug）；
        # 天线红灯那几行（原片 t=0 时灭，这里常亮）
        sbox = []
        for (sx, sy, kind, n, ci, sd, fl) in A._HK_SIGNS:
            im = A._neon_sign(kind, n, ci, sd, True)
            pad = 7 if kind in ('V', 'H') else 5
            sbox.append((fl, sx, sy - pad, im.width, im.height, pad))
        for camX in (0, 100, 250, 640, 900):
            fr = frame(0)
            A.hongkong_night(fr, scroll=-camX)
            boxes = []
            for fl, sx, y0, w_, h_, pad in sbox:
                if not fl and camX % HK_W == 0:
                    continue
                xo = (sx + camX) % HK_W                 # 原片画的位置：x = (sx − off) % 640，off = scroll = −camX
                if xo > W + 20:
                    xo -= HK_W
                xw = sx - camX                          # 世界坐标的位置
                for x in (xo, xw, xw + HK_W, xw - HK_W, xw + 2 * HK_W):
                    boxes.append((x - pad, y0, x - pad + w_, y0 + h_))
            for i in range(0, 22, 4):
                top = int(hrange(30, 80, i, 3)) - 8
                boxes.append((0, top, W, top + 1))
            m = rect_mask(boxes, keep=False)
            got = ref_render(st, ex.images, camX, 0)
            ex.checked('camX=%d y<153 除霓虹/天线 vs hongkong_night' % camX,
                       ndiff(got, fr.img, box=(0, 0, W, 153), mask=m))
            if camX == 0:
                ex.checked('camX=0 路面倒影 y≥153（分量差 > 3 的像素）', ndiff(got, fr.img, box=(0, 153, W, H), tol=3),
                           limit=W * rows // 50, extra='倒影源图先减 30 再平均，取整有出入')
    return st


# ---------------------------------------------------------------- hk_garden_night
def exp_hk_garden_night(ex):
    """虎豹别墅（夜，第 2 战场地）：_hk_garden_static(True)（static）+ 两只飞鸟（clouds 层，滑翔；
    原片 14 px/s、380 一趟，这里 span 440）。锚点：虎像 (44,132)、白塔、两只金狮、台阶。"""
    base = A._hk_garden_static(True)
    birds = []
    bird = blank(5, 2)
    ImageDraw.Draw(bird).line((0, 1, 2, 0, 4, 1), fill=A._c4((40, 40, 50)))
    kb = ex.img('bird', bird)
    for i in range(2):
        by = round(30 + i * 12 + math.sin(i) * 2)
        bx0 = (0 * 14 + i * 90) % 380 - 30
        birds.append(dict(image=kb, x0=round(bx0 - 2 + 100, 3), y=by, vx=14.0, k=0))
    layers = [dict(type='static', image=ex.img('static', base)), dict(type='clouds', span=440, clouds=birds)]
    anchors = dict(tiger=[44, 132], pagoda=[250, 104], lions=[[212, 118], [288, 118]], stairs=[226, 104, 274, 129],
                   balustrade=[0, 112, W, 131], grotto=[0, 58, 100, 118], arena_x=[16, 304])
    st = ex.stage(320, 150, (140, 176), layers, anchors=anchors)
    if ex.check_on:
        fr = frame(0)
        A.hk_garden(fr, night=True)
        ex.checked('t=0 整帧 vs hk_garden(night)', ndiff(ref_render(st, ex.images, 0, 0), fr.img))
        fr = frame(4.0)
        A.hk_garden(fr, night=True)
        ex.checked('t=4 y≥60（鸟在 y 28–46）', ndiff(ref_render(st, ex.images, 0, 4.0), fr.img, box=(0, 60, W, H)))
    return st


# ---------------------------------------------------------------- plane_cabin（兜底）
def exp_plane_cabin(ex):
    """客舱一点透视（兜底：plane_cabin_side 做不好时用，固定竞技场，过道 x 112–208）：
    窗外天空 wrap（vx 60，左右两排窗同一个方向卷——原片左右反向，wrap 层没法分半屏，见交付说明）
    + 舱内 static（窗户是透明洞）。"""
    cab, lm, rm = A._cabin_static()
    sky = A._cabin_sky()
    layers = [dict(type='wrap', image=ex.img('sky', sky), period=640, k=0.0, y=0, vx=60.0),
              dict(type='static', image=ex.img('cabin', cab))]
    anchors = dict(aisle=[112, 208], door=[148, 58, 172, 83], vp=[160, 66])
    st = ex.stage(320, 156, (150, 170), layers, anchors=anchors)
    if ex.check_on:
        fr = frame(0)
        A.plane_cabin(fr)
        ex.checked('t=0 整帧 vs plane_cabin', ndiff(ref_render(st, ex.images, 0, 0), fr.img))
    return st


# ---------------------------------------------------------------- 新画的三张（tools\bg_new\）
def exp_new(ex, name):
    """新背景模块约定：export(ex, helpers) → stage dict（自己调 ex.img / ex.bake / ex.checked）。"""
    mod = bg_new(name)
    return mod.export(ex, sys.modules[__name__])


EXPORTERS = {
    'title_pyramids': exp_title_pyramids,
    'world_map': exp_world_map,
    'sky_day': exp_sky_day,
    'sea_day': exp_sea_day,
    # 2026-10-10 main：牢房按用户要求重画物品细节（tools\bg_new\jail_cell.py，布局 / 锚点 / 铁栏不变；原 exp_jail_cell 留着不用）
    'jail_cell': lambda ex: exp_new(ex, 'jail_cell'),
    # 2026-10-10 bg-pro：序章背景加细节（tools\bg_new\kujo_house.py / kujo_bedroom_dusk.py / school_gate.py / dusk_gate.py；
    #   尺寸、纵深带、锚点、图层和动画不变；原 exp_kujo / exp_kujo_bedroom_dusk / exp_school_gate / exp_dusk_gate 留着不用）
    'kujo_house_day': lambda ex: bg_new('kujo_house').export(ex, sys.modules[__name__], 'day'),
    'kujo_house_night': lambda ex: bg_new('kujo_house').export(ex, sys.modules[__name__], 'night'),
    'kujo_house_morning': lambda ex: bg_new('kujo_house').export(ex, sys.modules[__name__], 'morning'),
    'kujo_bedroom_dusk': lambda ex: exp_new(ex, 'kujo_bedroom_dusk'),
    'school_gate': lambda ex: exp_new(ex, 'school_gate'),
    'school_infirmary': lambda ex: exp_new(ex, 'school_infirmary'),
    'dusk_gate': lambda ex: exp_new(ex, 'dusk_gate'),
    'tatami_top': lambda ex: exp_new(ex, 'tatami_top'),
    # 2026-10-10 scenes-early：序-8 上学路的长石阶（新）；驾驶舱按人的比例重画（tools\bg_new\cockpit.py，原 exp_cockpit 留着不用）
    'school_stairs': lambda ex: exp_new(ex, 'school_stairs'),
    'plane_cabin_side': lambda ex: exp_new(ex, 'plane_cabin_side'),
    'plane_cabin': exp_plane_cabin,
    'cockpit': lambda ex: exp_new(ex, 'cockpit'),
    # 2026-10-10 bg-hk：第1章香港夜街 / 虎豹别墅加细节（tools\bg_new\hongkong_night.py / hk_garden_night.py；
    #   尺寸、纵深带、锚点、剧情调查点位置不变；原 exp_hongkong_night / exp_hk_garden_night 留着不用）
    'hongkong_night': lambda ex: exp_new(ex, 'hongkong_night'),
    'hk_garden_night': lambda ex: exp_new(ex, 'hk_garden_night'),
}

# 后续章节在同一资源管线导出，兼容key只服务已写好的剧情名称。
_LATER_PACKS = {
 'common': ['underwater'],
 'ch2': ['yacht_deck','freighter_deck','freighter_corridor'],
 'ch3': ['singapore_street','singapore_hotel','cable_car','train_interior'],
 'ch4': ['calcutta_street','india_alley','ganges_ghat','varanasi_street'],
 'ch5': ['desert_highway','mountain_road','fog_town','enya_inn','inn','karachi_street','brain_inside'],
 'ch6': ['desert_noon','yaprin_village','cessna_cabin','dream_carnival','desert_night'],
 'ch7': ['redsea_island','submarine','seabed_mouth','egypt_coast'],
 'ch8': ['desert_day','aswan_town'],
 'ch9': ['egypt_temple','nile_bank','egypt_rail','luxor_town','luxor_house'],
 'ch10': ['cafe_interior','cairo_day','cairo_sewer'],
 'ch11': ['mansion_exterior','mansion_corridor','game_room','mansion_illusion','illusion_corridor','mansion_hall','coffin_tower','mansion_tower'],
 'final': ['mansion_stairs','cairo_night','cairo_street_night','cairo_rooftops','cairo_dawn','cairo_street_dawn','cairo_sunrise','kujo_bedroom_morning','airport'],
}
for _pack,_keys in _LATER_PACKS.items():
    for _key in _keys:
        DEFAULT_PACK[_key]=_pack
        EXPORTERS[_key]=lambda ex,_k=_key:bg_new('later_stages').export(ex,sys.modules[__name__],_k)
ORDER=list(DEFAULT_PACK)


# ============================================================ 入口
def build_all(stages, c, keys=None, check=True, log=print):
    """build_assets.py 的 bg 步调用（技术约定 §5.5）。keys = 只导这些（默认全部 M1）。"""
    ex = Ex(c, check=check, log=log)
    t0 = time.time()
    for key in (keys or ORDER):
        ex.begin(key)
        log('  [bg] %s（pack %s）' % (key, ex.pack))
        t1 = time.time()
        st = EXPORTERS[key](ex)
        st['pack'] = ex.pack
        stages[key] = st
        ex.report[key]['sec'] = round(time.time() - t1, 2)
    bad = [(k, ch['label']) for k, r in ex.report.items() for ch in r['checks'] if not ch['ok']]
    log('  [bg] %d 张，%.1f s；自检 %s' % (len(stages), time.time() - t0,
                                       '全部通过' if not bad else ('%d 项没过：%s' % (len(bad), bad))))
    build_all.last = ex
    if bad:
        raise RuntimeError('背景自检未通过：%s' % bad)
    return stages


def _safe_seg(seg):
    return re.sub(r'[^0-9A-Za-z_.\-]', lambda m: '~%04x' % ord(m.group()), seg)


def standalone_c(out_dir):
    """单独运行时的最小 c：图层存到 tools\\bg_new\\_preview\\layers\\（不写 assets\\bg\\）。"""
    index = {}

    def save_png(img, key, pack, sub=None):
        segs = key.split('/')
        path = os.path.join(out_dir, 'layers', *[_safe_seg(s) for s in segs[:-1]], _safe_seg(segs[-1]) + '.png')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path, optimize=True)
        index[key] = dict(file=os.path.relpath(path, out_dir).replace('\\', '/'), pack=pack,
                          bytes=os.path.getsize(path), size=list(img.size))
        return key
    return dict(save_png=save_png, packs=None, W=W, H=H, FPS=FPS, Frame=Frame, index=index)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--no-check' not in sys.argv
    os.makedirs(PREVIEW, exist_ok=True)
    c = standalone_c(PREVIEW)
    stages = {}
    build_all(stages, c, keys=args or None, check=check)
    ex = build_all.last
    pv = import_path('bg_new_pv', os.path.join(BG_NEW, '_pv.py'))
    pv.write_previews(stages, ex, c, PREVIEW, sys.modules[__name__])
