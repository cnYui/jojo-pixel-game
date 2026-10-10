r"""bg-pro 的改前 / 改后对比预览（2026-10-10，序章背景加细节）。只写 tools\bg_new\_preview\bg_pro\。

    python -B tools\bg_new\bgpro_preview.py                       # 全部（有新模块的才出“改后”）
    python -B tools\bg_new\bgpro_preview.py kujo_house_day school_gate

每个 key：原导出函数（bg_jojo.exp_*）和新模块（tools\bg_new\<模块>.py 的 export）各跑一遍（带自检），
按 §3.6 公式（bg_jojo.ref_render）在几个镜头位置、t = 1.0 拼成 2 倍图：
  第 1 行 改前，第 2 行 改后，第 3 行 改后 + 纵深带（青线）+ 锚点（红）。
输出 <key>.png 和 sheet.png；契约对比（w / ground / walk / anchors / 图层名和类型）打印出来。
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import os  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
OUT = os.path.join(HERE, '_preview', 'bg_pro')


def _load_bj():
    name = 'bg_jojo'
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, 'bg_jojo.py'))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


BJ = _load_bj()

OLD = {
    'kujo_house_day': lambda ex: BJ.exp_kujo(ex, 'day'),
    'kujo_house_night': lambda ex: BJ.exp_kujo(ex, 'night'),
    'kujo_house_morning': lambda ex: BJ.exp_kujo(ex, 'morning'),
    'kujo_bedroom_dusk': BJ.exp_kujo_bedroom_dusk,
    'school_gate': BJ.exp_school_gate,
    'dusk_gate': BJ.exp_dusk_gate,
    'tatami_top': None,          # 旧版就是 tools\bg_new\_旧稿 里的 tatami_top（见 OLD_MOD）
}
MOD = {
    'kujo_house_day': 'kujo_house', 'kujo_house_night': 'kujo_house', 'kujo_house_morning': 'kujo_house',
    'kujo_bedroom_dusk': 'kujo_bedroom_dusk', 'school_gate': 'school_gate', 'dusk_gate': 'dusk_gate',
    'tatami_top': 'tatami_top',
}
OLD_MOD = {'tatami_top': os.path.join(HERE, '_旧稿', 'tatami_top_20261010前.py')}
CAMS = {'school_gate': [0, 80, 160], 'dusk_gate': [-40, 30, 100]}


def _import(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(key, which):
    c = BJ.standalone_c(os.path.join(OUT, '_layers_' + which))
    ex = BJ.Ex(c, check=True, log=lambda *a: None)
    ex.begin(key)
    if which == 'old':
        if OLD.get(key):
            st = OLD[key](ex)
        elif key in OLD_MOD and os.path.exists(OLD_MOD[key]):
            st = _import('old_' + key, OLD_MOD[key]).export(ex, BJ)
        else:
            return None, ex
    else:
        path = os.path.join(HERE, MOD[key] + '.py')
        if not os.path.exists(path):
            return None, ex
        st = _import('new_' + MOD[key], path).export(ex, BJ)
    return st, ex


def guides(im, st, camX):
    im = im.copy()
    d = ImageDraw.Draw(im)
    y0, y1 = st['walk']
    for y in (y0, y1):
        d.line((0, y, 319, y), fill=(0, 255, 255, 255))
    for k, v in st.get('anchors', {}).items():
        if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(q, (int, float)) for q in v):
            x, y = v[0] - camX, v[1]
            d.line((x - 2, y, x + 2, y), fill=(255, 0, 0, 255))
            d.line((x, y - 2, x, y + 2), fill=(255, 0, 0, 255))
        elif isinstance(v, (list, tuple)) and len(v) == 4 and all(isinstance(q, (int, float)) for q in v) and v[2] > v[0] and v[3] > v[1]:
            d.rectangle((v[0] - camX, v[1], v[2] - camX, v[3]), outline=(255, 60, 60, 255))
    return im


def contract(old, new):
    out = []
    for f in ('w', 'ground', 'walk'):
        if old.get(f) != new.get(f):
            out.append('%s: %s → %s' % (f, old.get(f), new.get(f)))
    if old.get('anchors') != new.get('anchors'):
        out.append('anchors 不同：%s' % sorted(set(map(str, old['anchors'].items())) ^ set(map(str, new['anchors'].items()))))

    def sig(st):
        return [(L['type'], L.get('key'), L.get('image', '').split('/')[-1], L.get('n'), L.get('fps'), L.get('x'), L.get('y'),
                 L.get('w'), L.get('h'), L.get('k'), L.get('screen')) for L in st['layers'] + st.get('fg', [])]
    if sig(old) != sig(new):
        out.append('图层不同：\n      旧 %s\n      新 %s' % (sig(old), sig(new)))
    return out


def main(keys):
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for key in keys:
        old, exo = run(key, 'old')
        new, exn = run(key, 'new')
        cams = CAMS.get(key, [0])
        S = 2
        im = Image.new('RGB', (320 * S * len(cams), 180 * S * 3), (20, 20, 20))
        for j, cx in enumerate(cams):
            if old:
                im.paste(BJ.ref_render(old, exo.images, cx, 1.0).convert('RGB').resize((320 * S, 180 * S), Image.NEAREST), (j * 320 * S, 0))
            if new:
                a = BJ.ref_render(new, exn.images, cx, 1.0)
                im.paste(a.convert('RGB').resize((320 * S, 180 * S), Image.NEAREST), (j * 320 * S, 180 * S))
                im.paste(guides(a, new, cx).convert('RGB').resize((320 * S, 180 * S), Image.NEAREST), (j * 320 * S, 360 * S))
        im.save(os.path.join(OUT, key + '.png'))
        if new:
            BJ.ref_render(new, exn.images, cams[0], 1.0).convert('RGB').save(os.path.join(OUT, key + '_after_1x.png'))
        if old:
            BJ.ref_render(old, exo.images, cams[0], 1.0).convert('RGB').save(os.path.join(OUT, key + '_before_1x.png'))
        rows.append(im)
        print('==', key, '改后' if new else '（还没有新模块）')
        for which, ex in (('旧', exo), ('新', exn)):
            r = ex.report.get(key)
            if not r:
                continue
            bad = [c['label'] for c in r['checks'] if not c['ok']]
            print('   %s 自检 %d 项%s；strip %s' % (which, len(r['checks']), ('，没过 %s' % bad) if bad else ' 全过',
                                                ['%s 闭合%d 接缝%d' % (s['name'], s['closure'], s['seam']) for s in r['strips']]))
        if old and new:
            diff = contract(old, new)
            print('   契约：' + ('一致' if not diff else '\n   '.join(diff)))
    if rows:
        wmax = max(r.width for r in rows)
        sheet = Image.new('RGB', (wmax, sum(r.height for r in rows)), (20, 20, 20))
        y = 0
        for r in rows:
            sheet.paste(r, (0, y))
            y += r.height
        sheet.save(os.path.join(OUT, 'sheet.png'))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    main(args or list(MOD))
