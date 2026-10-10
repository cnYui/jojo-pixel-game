# -*- coding: utf-8 -*-
r"""包 7B 自测：把角色精灵按剧情的站位叠到新背景上，看比例 / 可走范围对不对（只出图，人工看）。
用法：python -B tools\dev\p7b\scale_test.py   → tools\dev\p7b\_out\scale_<key>.png（2 倍）
需要先跑过 python -B tools\bg_jojo.py（读 tools\bg_new\_preview\ 里的图层和 _stages.json）。"""
import sys
sys.dont_write_bytecode = True

import json  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(os.path.dirname(HERE))
GAME = os.path.dirname(TOOLS)
ATLAS = os.path.join(os.path.dirname(GAME), '角色图集')
PREV = os.path.join(TOOLS, 'bg_new', '_preview')
OUT = os.path.join(HERE, '_out')
sys.path.insert(0, TOOLS)

from PIL import Image, ImageDraw  # noqa: E402

import bg_jojo as BJ  # noqa: E402


def sprite(cid, anim='idle', f=0, flip=False):
    meta = json.load(open(os.path.join(ATLAS, cid, cid + '.json'), encoding='utf-8'))
    sheet = Image.open(os.path.join(ATLAS, cid, cid + '.png')).convert('RGBA')
    cw, ch = meta['cell']
    row = meta['animations'][anim]['row']
    im = sheet.crop((f * cw, row * ch, f * cw + cw, row * ch + ch))
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im, meta['pivot']


def put(dst, cid, x, y, camX=0, **kw):
    im, (px, py) = sprite(cid, **kw)
    BJ.paste(dst, im, x - camX - px, y - py)


def passenger(dst, x, top, camX=0):
    """16×18 乘客头肩的占位（包 7A 的 npc_passenger 还没画好时）。"""
    d = ImageDraw.Draw(dst)
    x = x - camX
    d.ellipse((x - 4, top, x + 4, top + 9), fill=(60, 40, 30, 255))
    d.ellipse((x - 3, top + 3, x + 4, top + 10), fill=(230, 190, 160, 255))
    d.rectangle((x - 7, top + 10, x + 7, top + 17), fill=(120, 110, 150, 255))


def main():
    os.makedirs(OUT, exist_ok=True)
    stages = json.load(open(os.path.join(PREV, '_stages.json'), encoding='utf-8'))
    rep = json.load(open(os.path.join(PREV, '_report.json'), encoding='utf-8'))
    images = {}
    for k, v in rep['files'].items():
        images[k] = Image.open(os.path.join(PREV, v['file'])).convert('RGBA')
    shots = []
    if 'plane_cabin_side' in stages:
        st = stages['plane_cabin_side']
        for camX in (0, 160, 320):
            im = BJ.ref_render(st, images, camX, 1.0, fg=False)
            for s in st['anchors']['seats'] + [st['anchors']['grayfly_seat']]:
                passenger(im, s, st['anchors']['seat_head_y'], camX)
            for i, (cid, x, y) in enumerate((('jotaro', 230, 162), ('kakyoin', 200, 160), ('joseph', 260, 158),
                                             ('avdol', 380, 164), ('jotaro', 600, 160))):
                put(im, cid, x, y, camX)
            for L in st['fg']:
                BJ.ref_layer(im, L, images, camX, 1.0, {})
            shots.append(('plane_cabin_side_cam%d' % camX, im))
    if 'school_infirmary' in stages:
        st = stages['school_infirmary']
        im = BJ.ref_render(st, images, 0, 1.0, fg=False)
        put(im, 'jotaro', 140, 166)
        put(im, 'kakyoin', 250, 160, flip=True)
        put(im, 'holly', 60, 158)
        for L in st['fg']:
            BJ.ref_layer(im, L, images, 0, 1.0, {})
        shots.append(('school_infirmary', im))
    if 'tatami_top' in stages:
        shots.append(('tatami_top', BJ.ref_render(stages['tatami_top'], images, 0, 1.0)))
    if 'hongkong_night' in stages:
        st = stages['hongkong_night']
        im = BJ.ref_render(st, images, 120, 1.0)
        put(im, 'jotaro', 230, 164, 120)
        put(im, 'polnareff', 330, 160, 120, flip=True)
        shots.append(('hongkong_night', im))
    for name, im in shots:
        im.convert('RGB').resize((640, 360), Image.NEAREST).save(os.path.join(OUT, 'scale_%s.png' % name))
        print('  →', os.path.join(OUT, 'scale_%s.png' % name))


if __name__ == '__main__':
    main()
