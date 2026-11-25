"""用游戏原背景渲染器生成四倍新旧对照，包含各开关及全部开关合成。"""
from __future__ import annotations

import argparse
import base64
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bg_gpt_p4 as pipe
from build_p4 import generated_background


def image_keys(value):
    if isinstance(value, dict):
        for key, val in value.items():
            if key == 'image' and isinstance(val, str):
                yield val
            elif key == 'images' and isinstance(val, list):
                yield from (v for v in val if isinstance(v, str))
            else:
                yield from image_keys(val)
    elif isinstance(value, list):
        for item in value:
            yield from image_keys(item)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE / '_out/bg_compare')
    args = parser.parse_args()
    report = json.loads((pipe.OUTPUT / '_report.json').read_text(encoding='utf-8'))
    bg = pipe.load_bg()
    payload = []
    for key in report['enabled']:
        spec, images = bg[key], {'old': {}, 'new': {}}
        for name in sorted(set(image_keys(spec))):
            rel = pipe.relative_image(name)
            original, replacement = pipe.ASSETS / rel, pipe.OUTPUT / rel
            for side in images:
                target = replacement if side == 'new' and rel.as_posix() in report['outputs'] else original
                images[side][name] = 'data:image/png;base64,' + base64.b64encode(target.read_bytes()).decode('ascii')
        toggles = sorted({l['key'] for l in pipe.layers(spec) if l.get('key')})
        states = [('off', {})] + [(t, {t: 1}) for t in toggles]
        if len(toggles) > 1:
            states.append(('all', dict.fromkeys(toggles, 1)))
        xmax = max(0, spec.get('w', 320) - 320)
        cams = sorted({0, round(xmax / 2), xmax})
        cy = spec.get('camY', [0, 0])
        ys = sorted({0, *cy}) if isinstance(cy, list) else [0]
        rows = [dict(label=f'{label} x={x} y={y}', state=state, x=x, y=y)
                for y in ys for x in cams for label, state in states]
        specs = {'old': spec, 'new': generated_background(spec, key in report.get('baked_clouds', []))}
        payload.append(dict(key=key, specs=specs, images=images, rows=rows))
    env = dict(os.environ)
    env.setdefault('NODE_PATH', 'D:/CodeWorkSpace/honglou-juan2/node_modules')
    proc = subprocess.run(['node', str(HERE / 'p4_bg_compare.js')], input=json.dumps(payload),
                          encoding='utf-8', capture_output=True, env=env, check=True)
    result = json.loads(proc.stdout)
    args.out.mkdir(parents=True, exist_ok=True)
    enabled = set(report['enabled'])
    for old in args.out.glob('*.png'):
        if old.stem not in enabled:
            old.unlink()
    for item in result:
        n = len(item['rows'])
        sheet = Image.new('RGB', (2560, 32 + n * 744), '#202027')
        draw = ImageDraw.Draw(sheet)
        draw.text((8, 8), f"{item['key']}   OLD (left) / GPT (right)   [{report['mode']}]", fill='white')
        for i, row in enumerate(item['rows']):
            y = 32 + i * 744
            draw.text((8, y + 4), row['label'], fill='white')
            for x, side in [(0, 'old'), (1280, 'new')]:
                im = Image.open(BytesIO(base64.b64decode(row[side])))
                sheet.paste(im.convert('RGB').resize((1280, 720), Image.Resampling.NEAREST), (x, y + 24))
        sheet.save(args.out / (item['key'] + '.png'))
        print(f"对照 {item['key']}：{n} 个镜头/开关组合")
    print(f'已输出 {len(result)} 个背景到 {args.out}')


if __name__ == '__main__':
    main()
