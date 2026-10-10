# -*- coding: utf-8 -*-
r"""第7章–终章背景重画（bg-late）的预览 / 前后对照工具。只写 tools\bg_new\_preview\late\（不碰 assets\、data\）。

    python -B tools\bg_new\late_preview.py before              # 用现在正式构建出来的 assets\bg + _meta\bg.json 拍“改前”
    python -B tools\bg_new\late_preview.py after  [key ...]     # 跑 tools\bg_new\<key>.py（不经 bg_jojo 路由）出图层 + 预览
    python -B tools\bg_new\late_preview.py compare [key ...]    # 改前 / 改后上下对照（每个 key 一张 + 总览）

预览都是 2 倍最近邻；宽地图按镜头 0 / 中间 / 最右各拍一张横着拼。after 另出一张“带人”的：
在可走带上下沿（地图定义的 yMin / yMax）摆承太郎 / 波鲁纳雷夫 / 伊奇 idle 第 0 帧，看人物和地面接触、是否看得清。
"""
import sys
sys.dont_write_bytecode = True

import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402
import importlib.util  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))           # tools\bg_new
TOOLS = os.path.dirname(HERE)
GAME = os.path.dirname(TOOLS)
OUT = os.path.join(HERE, '_preview', 'late')
W, H = 320, 180

KEYS = ['redsea_island', 'submarine', 'seabed_mouth', 'egypt_coast',
        'desert_day', 'aswan_town',
        'egypt_temple', 'nile_bank', 'egypt_rail', 'luxor_town', 'luxor_house',
        'cafe_interior', 'cairo_day', 'cairo_sewer',
        'mansion_exterior', 'mansion_corridor', 'game_room', 'mansion_illusion', 'illusion_corridor',
        'mansion_hall', 'coffin_tower', 'mansion_tower',
        'mansion_stairs', 'cairo_night', 'cairo_street_night', 'cairo_rooftops', 'cairo_dawn',
        'cairo_street_dawn', 'cairo_sunrise', 'kujo_bedroom_morning', 'airport']

# 地图定义里的可走带（story\stages_ch06_09.js / stages_late.js；没被地图用到的 key 用背景自己的 walk）
STAGE_WALK = {
    'redsea_island': (148, 176), 'submarine': (150, 176), 'seabed_mouth': (150, 174), 'egypt_coast': (148, 176),
    'desert_day': (148, 178), 'aswan_town': (148, 176), 'egypt_temple': (148, 176), 'nile_bank': (148, 176),
    'egypt_rail': (148, 178), 'luxor_town': (148, 176), 'luxor_house': (146, 176),
    'cafe_interior': (150, 172), 'cairo_day': (150, 176), 'cairo_sewer': (148, 172),
    'mansion_exterior': (150, 172), 'mansion_corridor': (150, 174), 'game_room': (150, 172),
    'illusion_corridor': (150, 174), 'mansion_hall': (148, 174), 'mansion_tower': (150, 172),
    'mansion_stairs': (146, 174), 'cairo_street_night': (148, 176), 'cairo_rooftops': (145, 176),
    'cairo_street_dawn': (148, 176), 'kujo_bedroom_morning': (150, 176), 'airport': (150, 176),
}


def import_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def bj():
    if 'bg_jojo' not in sys.modules:
        import_path('bg_jojo', os.path.join(TOOLS, 'bg_jojo.py'))
    return sys.modules['bg_jojo']


def _font(sz=11):
    from PIL import ImageFont
    for p in (r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simsun.ttc'):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def cams_for(w):
    if w <= W:
        return [0]
    xs = [0, (w - W) // 2, w - W]
    return sorted(set(xs))


def render_strip(BJ, st, images, t=1.0, state=None, scale=2):
    from PIL import Image
    cams = cams_for(st['w'])
    out = Image.new('RGB', (W * len(cams) * scale + (len(cams) - 1) * 4, H * scale), (16, 16, 20))
    for i, cx in enumerate(cams):
        im = BJ.ref_render(st, images, cx, t, state or {}).convert('RGB')
        out.paste(im.resize((W * scale, H * scale), Image.NEAREST), (i * (W * scale + 4), 0))
    return out, cams


# ---------------------------------------------------------------- 人物（看比例 / 接地）
_CH = {}


def char_frame(cid, anim='idle', frame=0):
    from PIL import Image
    if cid in _CH:
        return _CH[cid]
    meta = json.load(open(os.path.join(TOOLS, '_meta', 'chars.json'), encoding='utf-8'))['chars'][cid]
    idx = json.load(open(os.path.join(TOOLS, '_meta', 'img_index.json'), encoding='utf-8'))
    sheet = Image.open(os.path.join(GAME, 'assets', *idx[meta['image']]['file'].split('/'))).convert('RGBA')
    cw, ch = meta['cell']
    row = meta['animations'][anim]['row']
    im = sheet.crop((frame * cw, row * ch, frame * cw + cw, row * ch + ch))
    _CH[cid] = (im, meta['pivot'])
    return _CH[cid]


def with_people(BJ, st, images, key, scale=2, t=1.0, state=None):
    from PIL import Image, ImageDraw
    walk = STAGE_WALK.get(key, tuple(st['walk']))
    cams = cams_for(st['w'])
    out = Image.new('RGB', (W * len(cams) * scale + (len(cams) - 1) * 4, H * scale), (16, 16, 20))
    for i, cx in enumerate(cams):
        im = BJ.ref_render(st, images, cx, t, state or {}).convert('RGBA')
        for j, (cid, x, y) in enumerate((('jotaro', 70, walk[0]), ('polnareff', 160, (walk[0] + walk[1]) // 2),
                                          ('iggy', 205, walk[1] - 2), ('joseph', 255, walk[1]))):
            try:
                fr, (px, py) = char_frame(cid)
            except Exception:
                continue
            im.alpha_composite(fr, (int(x - px), int(y - py)))
        d = ImageDraw.Draw(im)
        for y in walk:
            for xx in range(0, W, 4):
                d.point((xx, y), fill=(80, 255, 120, 255))
        out.paste(im.convert('RGB').resize((W * scale, H * scale), Image.NEAREST), (i * (W * scale + 4), 0))
    return out


# ---------------------------------------------------------------- before
def cmd_before(keys):
    from PIL import Image
    BJ = bj()
    meta = json.load(open(os.path.join(TOOLS, '_meta', 'bg.json'), encoding='utf-8'))
    idx = json.load(open(os.path.join(TOOLS, '_meta', 'img_index.json'), encoding='utf-8'))
    od = os.path.join(OUT, 'before')
    os.makedirs(od, exist_ok=True)
    for key in keys:
        st = meta.get(key)
        if not st:
            print('  [before] 没有', key)
            continue
        images = {}
        for L in st['layers'] + st.get('fg', []):
            for k in [L.get('image')] + list(L.get('images') or []) + [s.get('image') for s in L.get('signs', [])] + \
                    [c.get('image') for c in L.get('clouds', [])]:
                if k and k not in images and k in idx:
                    images[k] = Image.open(os.path.join(GAME, 'assets', *idx[k]['file'].split('/'))).convert('RGBA')
        state = {'flesh': True, 'alarm': True, 'breach': True, 'beam': True}
        im, cams = render_strip(BJ, st, images, 1.0, {})
        im.save(os.path.join(od, key + '.png'))
        ppl = with_people(BJ, st, images, key)
        ppl.save(os.path.join(od, key + '_people.png'))
        im2, _ = render_strip(BJ, st, images, 1.0, state)
        im2.save(os.path.join(od, key + '_state.png'))
        print('  [before] %-22s w %4d  cams %s' % (key, st['w'], cams))


# ---------------------------------------------------------------- after
def cmd_after(keys):
    from PIL import Image
    BJ = bj()
    od = os.path.join(OUT, 'after')
    os.makedirs(od, exist_ok=True)
    c = BJ.standalone_c(os.path.join(OUT, 'after_layers'))
    ex = BJ.Ex(c, check=True)
    stages, times = {}, {}
    for key in keys:
        ex.begin(key)
        t0 = time.time()
        print('  [after] %s（pack %s）' % (key, ex.pack))
        st = BJ.exp_new(ex, key)
        st['pack'] = ex.pack
        stages[key] = st
        times[key] = round(time.time() - t0, 2)
        im, cams = render_strip(BJ, st, ex.images, 1.0, {})
        im.save(os.path.join(od, key + '.png'))
        with_people(BJ, st, ex.images, key).save(os.path.join(od, key + '_people.png'))
        keyed = sorted({L['key'] for L in st['layers'] + st['fg'] if L.get('key')})
        if keyed:
            im2, _ = render_strip(BJ, st, ex.images, 1.0, {k: True for k in keyed})
            im2.save(os.path.join(od, key + '_state.png'))
        # 动画抽帧：t = 0 / 0.5 / 1 / 1.5（只看第一个镜头）
        fr = Image.new('RGB', (W * 4 + 12, H), (16, 16, 20))
        for i, t in enumerate((0.0, 0.5, 1.0, 1.5)):
            fr.paste(BJ.ref_render(st, ex.images, 0, t, {}).convert('RGB'), (i * (W + 4), 0))
        fr.save(os.path.join(od, key + '_anim.png'))
    bad = [(k, ch['label']) for k, r in ex.report.items() for ch in r['checks'] if not ch['ok']]
    size = {}
    for k, v in c['index'].items():
        bk = k.split('/')[1]
        size[bk] = size.get(bk, 0) + v['bytes']
    rep = dict(report=ex.report, bytes=size, sec=times, bad=bad)
    with open(os.path.join(OUT, '_after_report.json'), 'w', encoding='utf-8') as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, '_after_stages.json'), 'w', encoding='utf-8') as fh:
        json.dump(stages, fh, ensure_ascii=False, indent=1)
    for k in keys:
        print('    %-22s %7.1f KB  %5.2f s' % (k, size.get(k, 0) / 1024, times.get(k, 0)))
    print('  [after] 自检 %s' % ('全部通过' if not bad else '没过 %d 项：%s' % (len(bad), bad)))
    return 0 if not bad else 1


# ---------------------------------------------------------------- compare
def cmd_compare(keys):
    from PIL import Image, ImageDraw
    f = _font(13)
    od = os.path.join(OUT, 'compare')
    os.makedirs(od, exist_ok=True)
    tiles = []
    for key in keys:
        b = os.path.join(OUT, 'before', key + '.png')
        a = os.path.join(OUT, 'after', key + '.png')
        ap = os.path.join(OUT, 'after', key + '_people.png')
        ims = [(lab, Image.open(p).convert('RGB')) for lab, p in (('改前', b), ('改后', a), ('改后 + 人物 / 可走带', ap))
               if os.path.exists(p)]
        if not ims:
            continue
        wmax = max(im.width for _, im in ims)
        sheet = Image.new('RGB', (wmax, sum(im.height + 22 for _, im in ims)), (22, 22, 28))
        d = ImageDraw.Draw(sheet)
        y = 0
        for lab, im in ims:
            d.text((6, y + 3), key + '　' + lab, font=f, fill=(255, 230, 140))
            sheet.paste(im, (0, y + 22))
            y += im.height + 22
        sheet.save(os.path.join(od, key + '.png'))
        tiles.append((key, sheet))
    print('  [compare] %d 张 → %s' % (len(tiles), od))


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 0
    cmd, keys = args[0], [a for a in args[1:] if not a.startswith('--')] or KEYS
    bad = [k for k in keys if k not in KEYS]
    if bad:
        print('不认识的 key：', bad)
        return 2
    if cmd == 'before':
        cmd_before(keys)
    elif cmd == 'after':
        return cmd_after(keys)
    elif cmd == 'compare':
        cmd_compare(keys)
    else:
        print(__doc__)
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
