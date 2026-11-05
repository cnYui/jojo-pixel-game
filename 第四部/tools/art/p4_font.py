# 第四部的对话字库：文泉驿点阵正黑（WQY Zen Hei Sharp，自带 12 / 16 px 点阵）烘成两张白字图集。
#   字表 = 第三部字库的全部字 + 第四部游戏代码里出现的所有字（剧情改了台词就重跑：build_p4.py 会自动调这个）。
#   格式照第三部 tools/_meta/font.json：{ '12': { image, lh, asc, glyphs: { 字: [x, y, 宽] } }, '16': {...} }
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402

SIZES = {12: dict(lh=13, asc=11, cell=13), 16: dict(lh=17, asc=14, cell=17)}
COLS = 64


def charset():
    p3 = L.load_json(os.path.join(L.REPO, 'tools', '_meta', 'font.json'), {})
    chars = set((p3.get('12') or {}).get('glyphs', {}).keys())
    game = os.path.join(L.P4, '游戏')
    files = [os.path.join(game, 'main.js')] + glob.glob(os.path.join(game, 'engine', '*.js')) + glob.glob(os.path.join(game, 'story', '*.js'))
    for fp in files:
        with open(fp, encoding='utf-8') as fh:
            for ch in fh.read():
                o = ord(ch)
                if o >= 0x80 and ch not in '﻿' and not (0xD800 <= o <= 0xDFFF):
                    chars.add(ch)
    chars |= set(chr(c) for c in range(0x20, 0x7f))
    return sorted(chars)


def build():
    chars = charset()
    meta = {}
    for size, cfg in SIZES.items():
        f = L.ImageFont.truetype(L.WQY, size, index=1)
        cell, lh, asc = cfg['cell'], cfg['lh'], cfg['asc']
        rows = (len(chars) + COLS - 1) // COLS
        atlas = Image.new('RGBA', (COLS * cell, rows * lh), (0, 0, 0, 0))
        glyphs = {}
        missing = []
        for i, ch in enumerate(chars):
            x, y = (i % COLS) * cell, (i // COLS) * lh
            adv = int(round(f.getlength(ch))) if ch != ' ' else size // 2
            if ord(ch) >= 0x2E80 and adv < size:
                adv = size
            g = Image.new('L', (cell, lh), 0)
            d = ImageDraw.Draw(g)
            d.fontmode = '1'
            d.text((0, asc), ch, font=f, fill=255, anchor='ls')
            if ch.strip() and not g.getbbox():
                missing.append(ch)
            white = Image.new('RGBA', (cell, lh), (255, 255, 255, 255))
            atlas.paste(white, (x, y), g)
            glyphs[ch] = [x, y, min(adv, cell)]
        name = f'font/p4_{size}'
        out = os.path.join(L.ASSETS, name + '.png')
        L.ensure(out)
        atlas.save(out)
        meta[str(size)] = dict(image=name, lh=lh, asc=asc, glyphs=glyphs)
        print(f'字库 {size}px：{len(chars)} 字，{atlas.size}，点阵里没有的字 {len(missing)} 个', ''.join(missing[:40]))
    L.save_json(os.path.join(L.META, 'font.json'), meta)


if __name__ == '__main__':
    build()
