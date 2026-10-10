# -*- coding: utf-8 -*-
r"""包 7B 预览工具（bg_jojo.py 单独运行时调用）：每个背景一张 320×180 预览、宽地图的整条预览、
新画三张的锚点预览、总览拼图、_stages.json / _report.json。全部写在 tools\bg_new\_preview\。"""
import sys
sys.dont_write_bytecode = True

import json  # noqa: E402
import os  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

W, H = 320, 180
NEW = ('school_infirmary', 'tatami_top', 'plane_cabin_side', 'school_stairs', 'cockpit', 'jail_cell')
# 预览时用的剧情状态 / 时间（默认 t = 1.0、state 空）
VARIANTS = {
    'jail_cell': [('', dict(bend=0)), ('_bend1', dict(bend=1.0))],
    'cockpit': [('', {}), ('_alarm', dict(alarm=True, yoke=1))],
}


def _font(sz=11):
    for p in (r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simsun.ttc'):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def _anchor_points(anchors):
    """anchors 里能画成点 / 框的东西 → [(label, kind, coords)]。"""
    out = []

    def add(label, v):
        if isinstance(v, (list, tuple)):
            if len(v) == 2 and all(isinstance(q, (int, float)) for q in v):
                out.append((label, 'pt', v))
            elif len(v) == 4 and all(isinstance(q, (int, float)) for q in v) and v[2] > v[0] and v[3] > v[1]:
                out.append((label, 'box', v))
            elif v and all(isinstance(q, (list, tuple)) for q in v):
                for i, q in enumerate(v):
                    add('%s%d' % (label, i), q)
    for k, v in anchors.items():
        add(k, v)
    return out


def write_previews(stages, ex, c, out_dir, BJ):
    os.makedirs(out_dir, exist_ok=True)
    f11 = _font(11)
    tiles = []
    for key, st in stages.items():
        for suf, state in VARIANTS.get(key, [('', {})]):
            im = BJ.ref_render(st, ex.images, 0, 1.0, state).convert('RGB')
            im.save(os.path.join(out_dir, key + suf + '.png'))
            tiles.append((key + suf, im))
        if st['w'] > W:
            xs = list(range(0, st['w'] - W + 1, W))
            if xs[-1] != st['w'] - W:
                xs.append(st['w'] - W)
            x0 = st.get('anchors', {}).get('cam', [0])[0] if key == 'dusk_gate' else 0
            wide = Image.new('RGB', (W * len(xs), H))
            for i, cx in enumerate(xs):
                wide.paste(BJ.ref_render(st, ex.images, cx + (x0 if i == 0 else 0), 1.0).convert('RGB'), (i * W, 0))
            wide.save(os.path.join(out_dir, key + '_wide.png'))
        if key in NEW:
            _anchor_preview(key, st, ex, BJ, out_dir, f11)
    # 总览
    cols = 4
    th = H + 16
    sheet = Image.new('RGB', (cols * (W + 6) + 6, ((len(tiles) + cols - 1) // cols) * (th + 6) + 6), (28, 28, 34))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(tiles):
        x = 6 + (i % cols) * (W + 6)
        y = 6 + (i // cols) * (th + 6)
        d.text((x, y), name, font=f11, fill=(255, 240, 140))
        sheet.paste(im, (x, y + 16))
    sheet.save(os.path.join(out_dir, '_sheet.png'))
    with open(os.path.join(out_dir, '_stages.json'), 'w', encoding='utf-8') as fh:
        json.dump(stages, fh, ensure_ascii=False, indent=1)
    rep = dict(report=ex.report, files=c.get('index', {}))
    tot = {}
    for k, v in c.get('index', {}).items():
        bk = k.split('/')[1]
        tot[bk] = tot.get(bk, 0) + v['bytes']
    rep['bytes_per_bg'] = tot
    rep['bytes_total'] = sum(tot.values())
    with open(os.path.join(out_dir, '_report.json'), 'w', encoding='utf-8') as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    print('  [pv] 预览 %d 张 → %s；图层合计 %.1f KB' % (len(tiles), out_dir, rep['bytes_total'] / 1024))
    for bk, b in sorted(tot.items()):
        print('       %-20s %7.1f KB' % (bk, b / 1024))


def _anchor_preview(key, st, ex, BJ, out_dir, font):
    """新画的三张：2 倍图 + 锚点（点 = 十字，框 = 矩形）+ 可走范围。"""
    w = st['w']
    big = Image.new('RGB', (w * 2, H * 2 + 40), (20, 20, 24))
    xs = list(range(0, max(1, w - W + 1), W)) or [0]
    if w > W and xs[-1] != w - W:
        xs.append(w - W)
    for cx in xs:
        im = BJ.ref_render(st, ex.images, cx, 1.0).convert('RGB').resize((W * 2, H * 2), Image.NEAREST)
        big.paste(im, (cx * 2, 0))
    d = ImageDraw.Draw(big)
    y0, y1 = st['walk']
    wx = st.get('anchors', {}).get('walk_x', [0, w])
    d.rectangle((wx[0] * 2, y0 * 2, wx[1] * 2 - 1, y1 * 2 - 1), outline=(80, 255, 120))
    d.line((0, st['ground'] * 2, w * 2, st['ground'] * 2), fill=(255, 220, 60))
    for label, kind, v in _anchor_points(st.get('anchors', {})):
        if label in ('walk_x',):
            continue
        if kind == 'pt':
            x, y = v[0] * 2, v[1] * 2
            d.line((x - 5, y, x + 5, y), fill=(255, 60, 200))
            d.line((x, y - 5, x, y + 5), fill=(255, 60, 200))
            d.text((x + 4, y + 2), label, font=font, fill=(255, 120, 230))
        else:
            d.rectangle((v[0] * 2, v[1] * 2, v[2] * 2 - 1, v[3] * 2 - 1), outline=(60, 200, 255))
            d.text((v[0] * 2 + 2, v[1] * 2 + 1), label, font=font, fill=(120, 220, 255))
    d.text((6, H * 2 + 6), '%s  ground %d  walk y %d–%d  x %s  （绿框 = 可走范围，黄线 = ground）'
           % (key, st['ground'], y0, y1, wx), font=font, fill=(240, 240, 240))
    big.save(os.path.join(out_dir, key + '_anchors.png'))
