# 沿用第四部12/16px文泉驿点阵烘焙法，额外收集开发脚本，后续剧情新增字也会进入字库。
import io
import os
import tarfile
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from p5_paths import P5, REPO, GAME, ASSETS, META, load_json, save_json

SIZES = {12: dict(lh=13, asc=11, cell=13), 16: dict(lh=17, asc=14, cell=17)}
FONT_URL = 'https://deb.debian.org/debian/pool/main/f/fonts-wqy-zenhei/fonts-wqy-zenhei_0.9.45.orig.tar.gz'


def font_path():
    configured = os.environ.get('P5_FONT')
    if configured:
        path = Path(configured)
        if not path.is_file():
            raise FileNotFoundError(f'P5_FONT不存在：{path}')
        return path
    path = P5 / 'tools/font_cache/wqy-zenhei.ttc'
    if path.exists():
        return path
    system = Path('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
    if system.exists():
        return system
    # Windows通常没有WQY；仅缓存字体数据，不安装软件，也不写第四部缓存。
    print('首次构建：下载文泉驿字体到第五部/tools/font_cache/')
    with urllib.request.urlopen(FONT_URL, timeout=60) as response:
        data = response.read()
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        member = next(m for m in archive.getmembers() if m.name.endswith('/wqy-zenhei.ttc'))
        font = archive.extractfile(member).read()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(font)
    return path


def charset():
    p3 = load_json(REPO / 'tools/_meta/font.json', {})
    chars = set(p3.get('12', {}).get('glyphs', {}))
    files = [GAME / 'main.js', *GAME.glob('engine/*.js'), *GAME.glob('story/*.js'), *P5.glob('docs/*.md')]
    for path in files:
        chars.update(ch for ch in path.read_text(encoding='utf-8')
                     if ord(ch) >= 0x80 and ch != '\ufeff' and not 0xD800 <= ord(ch) <= 0xDFFF)
    chars.update(chr(c) for c in range(0x20, 0x7f))
    return sorted(chars)


def build():
    chars, meta = charset(), {}
    path = font_path()
    for size, cfg in SIZES.items():
        font = ImageFont.truetype(str(path), size, index=1)
        cell, lh, asc = cfg['cell'], cfg['lh'], cfg['asc']
        atlas = Image.new('RGBA', (64 * cell, ((len(chars) + 63) // 64) * lh))
        glyphs, missing = {}, []
        for i, ch in enumerate(chars):
            x, y = (i % 64) * cell, (i // 64) * lh
            adv = round(font.getlength(ch)) if ch != ' ' else size // 2
            if ord(ch) >= 0x2E80 and adv < size:
                adv = size
            mask = Image.new('L', (cell, lh))
            draw = ImageDraw.Draw(mask)
            draw.fontmode = '1'
            draw.text((0, asc), ch, font=font, fill=255, anchor='ls')
            if ch.strip() and not mask.getbbox():
                missing.append(ch)
            atlas.paste(Image.new('RGBA', (cell, lh), 'white'), (x, y), mask)
            glyphs[ch] = [x, y, min(adv, cell)]
        key = f'font/p5_{size}'
        output = ASSETS / (key + '.png')
        output.parent.mkdir(parents=True, exist_ok=True)
        atlas.save(output)
        meta[str(size)] = dict(image=key, lh=lh, asc=asc, glyphs=glyphs)
        print(f'字库{size}px：{len(chars)}字，空字形{len(missing)}个')
    save_json(META / 'font.json', meta)
    return meta


if __name__ == '__main__':
    build()
