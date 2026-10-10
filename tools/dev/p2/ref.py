# -*- coding: utf-8 -*-
r"""包 2：原工程特效的参考联系表（只读 import 源码 engine.fx 和几个场景文件里的辅助函数）。

每个用例（cases.py）画 4 格：同一背景、同一参数、4 个时刻。输出 tools\dev\p2\_out\ref_sheet_NN.png（布局和 fx_sheet.html 完全一样，
run_tests.py 把两边逐行拼成 compare_NN.png 人工比对）。

用法：PYTHONDONTWRITEBYTECODE=1 python tools\dev\p2\ref.py
"""
import sys
sys.dont_write_bytecode = True

import os  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(os.path.dirname(GAME), '源码')
OUT = os.path.join(HERE, '_out')
if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import cases as CS  # noqa: E402

# 联系表布局（fx_sheet.html 照抄这几个数）
LABEL_W, CW, CH, GAP, ROWS = 150, 320, 180, 4, 10
SHEET_W = LABEL_W + 4 * (CW + GAP)


def font(size=14):
    for p in (r'C:\Windows\Fonts\simsun.ttc', r'C:\Windows\Fonts\msyh.ttc'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def sub(v, t, t1, col):
    if isinstance(v, str) and v.startswith('$'):
        return {'$t': t, '$t0': CS.T0, '$t1': t1, '$a': col.get('a'), '$i': col.get('i')}[v]
    if isinstance(v, list):
        return [sub(x, t, t1, col) for x in v]
    if isinstance(v, dict):
        return {k: sub(x, t, t1, col) for k, x in v.items()}
    return v


def adapters():
    import assets
    assets.load_all()
    from engine.core import paste
    from engine import bg_asia
    import scenes.s07_polnareff as s07
    import scenes.s04_kakyoin as s04
    import scenes.s02_jail as s02
    import scenes.s18_final2 as s18

    def sprite(fr, name, x, y, frame=0, flip=False, scale=1, alpha=1.0, **_):
        fr.spr(name, x, y, frame=frame, flip=flip, scale=scale, alpha=alpha)

    def stand_out(fr, cid, logical, x, y, t, t0, **kw):
        s07.stand_out(fr, f'{cid}.{logical}', x, y, t0, **kw)

    def cap_shadow(fr, x, y, t, t0, scale=3, **_):
        if t >= t0:
            im, ax, ay = s02._cap_shadow()
            paste(fr.img, im, round(x - ax), round(y - ay))

    def draw_route(fr, stops, t, t0, t1, **kw):
        bg_asia.draw_route(fr, stops, t=t, t0=t0, t1=t1, vehicle=kw.get('vehicle', 'plane'), labels=False)

    return dict(
        sprite=sprite, stand_out=stand_out, cap_shadow=cap_shadow, draw_route=draw_route,
        fireball=lambda fr, x, y, r, **kw: s07.fireball(fr.d, x, y, r, **kw),
        fire_jet=lambda fr, x0, x1, y, t, **kw: s07.fire_jet(fr, x0, x1, y, t, **kw),
        fire_chunks=lambda fr, x, y, t, t0, **kw: s07.fire_chunks(fr, x, y, t, t0, **kw),
        slash_arc=lambda fr, x, y, t, t0, **kw: s07.slash_arc(fr, x, y, t, t0, **kw),
        dim_bg=lambda fr, a, **kw: s07.dim_bg(fr, a, **kw),
        blade_ext=lambda fr, X, Y, **kw: s07.blade_ext(fr, X, Y),
        coin_on_blade=lambda fr, X, Y, i, **kw: s07.coin_on_blade(fr, X, Y, i),
        ora_bg=lambda fr, t, cx, cy, **kw: s04._ora_bg(fr, t, cx, cy),
        clash_sparks=lambda fr, t, t0, t1, cx, cy, **kw: s18.clash_sparks(fr, t, t0, t1, cx, cy, **kw),
    )


def render_cell(case, col, bgs, AD, fx):
    from engine.core import Frame
    t = CS.T0 + col.get('t', 0.1)
    t1 = CS.T0 + case.get('t1', 0)
    fr = Frame(t)
    fr.img.paste(bgs[case['bg']], (0, 0))
    note = None
    for k, call in enumerate(case['calls']):
        py = call.get('py')
        if py == '-':
            note = '原工程没有（JS 新增）'
            continue
        pos = sub(call.get('py_pos', call['pos']), t, t1, col)
        kw = dict(call.get('py_kw', call['kw']))
        main = call['fn'] == case['calls'][[c['fn'] for c in case['calls']].index(call['fn'])]['fn'] and call is _main(case)
        if main:
            kw.update(col.get('py_kw', col.get('kw', {})))
        kw = sub(kw, t, t1, col)
        kw.pop('logical', None)
        if py and py.startswith('adapter:'):
            AD[py[8:]](fr, *pos, **kw)
        else:
            getattr(fx, call['fn'])(fr, *pos, **kw)
    return fr.img.convert('RGB'), note


def _main(case):
    """主调用 = 不是先画 / 后画精灵的那一个（第一个 fn != 'sprite' 的调用）。"""
    for c in case['calls']:
        if c['fn'] != 'sprite':
            return c
    return case['calls'][0]


def columns(case):
    if 'cols' in case:
        return case['cols']
    return [dict(t=v) for v in case['times']]


def main():
    os.makedirs(OUT, exist_ok=True)
    AD = adapters()
    from engine import fx
    bgs = {n: Image.open(os.path.join(OUT, f'bg_{n}.png')).convert('RGBA') for n in ('jail', 'hkn', 'hkg', 'map', 'gray')}
    f14, f12 = font(14), font(12)
    cases = CS.CASES
    nsheet = (len(cases) + ROWS - 1) // ROWS
    timing = []
    for s in range(nsheet):
        rows = cases[s * ROWS:(s + 1) * ROWS]
        sheet = Image.new('RGB', (SHEET_W, len(rows) * (CH + GAP)), (24, 22, 32))
        d = ImageDraw.Draw(sheet)
        for r, case in enumerate(rows):
            y0 = r * (CH + GAP)
            d.text((6, y0 + 6), case['id'], font=f14, fill=(240, 232, 200))
            d.text((6, y0 + 26), '[%s] 原工程' % case.get('pri', ''), font=f12, fill=(150, 150, 170))
            cols = columns(case)
            for c, col in enumerate(cols):
                t0 = time.perf_counter()
                im, note = render_cell(case, col, bgs, AD, fx)
                timing.append((case['id'], c, (time.perf_counter() - t0) * 1000))
                x0 = LABEL_W + c * (CW + GAP)
                sheet.paste(im, (x0, y0))
                if note:
                    dd = ImageDraw.Draw(sheet)
                    dd.rectangle((x0 + 4, y0 + 4, x0 + 150, y0 + 22), fill=(0, 0, 0))
                    dd.text((x0 + 8, y0 + 6), note, font=f12, fill=(255, 200, 120))
                lab = ('t0+%.2f' % col['t']) if 't' in col else ' '.join('%s=%s' % kv for kv in (col.get('kw') or {'a': col.get('a', '')}).items())
                d.text((LABEL_W + c * (CW + GAP) + 2, y0 + CH - 14), lab[:40], font=f12, fill=(255, 255, 255))
        p = os.path.join(OUT, 'ref_sheet_%02d.png' % s)
        sheet.save(p)
        print('→', p)
    with open(os.path.join(OUT, 'ref_timing.txt'), 'w', encoding='utf-8') as f:
        for row in timing:
            f.write('%s\t%d\t%.2f ms\n' % row)


if __name__ == '__main__':
    main()
