"""按完整背景组接入生图，保留原图供继续生成底图和随时回退。"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path, PurePosixPath
import sys

from PIL import Image, ImageChops, ImageFilter

P4 = Path(__file__).resolve().parents[1]
ASSETS = P4 / 'assets'
OUTPUT = ASSETS / 'bg_gpt'
DEFAULT_SRC = Path('D:/CodeWorkSpace/jojo5_art_out/p4bg')


def load_bg(assets=ASSETS):
    bg = {}
    for path in [assets / '_meta/bg.json', *sorted((assets / '_meta').glob('bg_*.json'))]:
        bg.update(json.loads(path.read_text(encoding='utf-8')))
    return bg


def layers(spec):
    for layer in spec.get('layers', []) + spec.get('fg', []):
        yield layer
        yield from layers(layer)


def relative_image(image):
    path = PurePosixPath(image)
    if '\\' in image or ':' in image or path.is_absolute() or '..' in path.parts or path.parts[0] != 'bg':
        raise ValueError(f'背景图路径越界：{image}')
    return Path(*path.parts).with_suffix('.png')


def crop_band(raw, size):
    w, h = size
    cw, ch = (1024, 1536) if h > w else (1536, 1024)
    k = min(cw / w, ch / h)
    x, y = round((cw - w * k) / 2), round((ch - h * k) / 2)
    # 与生成脚本的整数画布矩形一致，再分别换算到成图的实际横纵尺寸。
    box = (round(x * raw.width / cw), round(y * raw.height / ch),
           round((x + round(w * k)) * raw.width / cw),
           round((y + round(h * k)) * raw.height / ch))
    if box[2] <= box[0] or box[3] <= box[1]:
        raise ValueError('成图尺寸太小，无法裁出场景')
    return raw.crop(box)


def magenta(rgb):
    r, g, b = rgb[:3]
    return (255 - r) + g + (255 - b) < 150 or (r > 150 and b > 150 and g < 90)


def convert(raw_path, original_path, size, near=False):
    with Image.open(original_path) as im:
        original = im.convert('RGBA')
    if original.size != tuple(size):
        raise ValueError(f'原图尺寸 {original.size} 与清单 {size} 不同')
    with Image.open(raw_path) as im:
        crop = crop_band(im.convert('RGBA'), size)
    if near:
        opaque = original.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
        # 只在原透明区及一像素边界抠色，避免误删物件内部的正常紫红色。
        allowed = ImageChops.invert(opaque).filter(ImageFilter.MaxFilter(3))
        allowed = allowed.resize(crop.size, Image.Resampling.NEAREST)
        keyed = Image.new('L', crop.size)
        keyed.putdata([0 if magenta(p) and a else p[3]
                       for p, a in zip(crop.getdata(), allowed.getdata())])
        crop.putalpha(keyed)
    small = crop.resize(tuple(size), Image.Resampling.BOX)
    alpha = small.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    if near:
        alpha = ImageChops.multiply(alpha, opaque)
        edge = ImageChops.subtract(opaque, opaque.filter(ImageFilter.MinFilter(3)))
        pixels = list(small.getdata())
        # BOX 后的混色粉边用原边界色兜底，既不留下洋红线，也不扩大透明洞。
        repaired = [(o if e and (not a or magenta(p)) else p,
                     255 if e and not a else a)
                    for p, o, a, e in zip(pixels, original.getdata(), alpha.getdata(), edge.getdata())]
        pixels = [p for p, a in repaired]
        alpha.putdata([a for p, a in repaired])
        small.putdata(pixels)
    rgb = small.convert('RGB')
    visible = [p for p, a in zip(rgb.getdata(), alpha.getdata()) if a]
    if visible:
        training = Image.new('RGB', (len(visible), 1))
        training.putdata(visible)
        palette = training.quantize(colors=96, method=Image.Quantize.MEDIANCUT,
                                    dither=Image.Dither.NONE)
        result = rgb.quantize(palette=palette, dither=Image.Dither.NONE).convert('RGBA')
    else:
        result = Image.new('RGBA', tuple(size))
    result.putalpha(alpha)
    result.putdata([p if p[3] else (0, 0, 0, 0) for p in result.getdata()])
    return result


def run(src=DEFAULT_SRC, partial=False, assets=ASSETS, output=OUTPUT):
    src, assets, output = Path(src), Path(assets), Path(output)
    if output.is_symlink() or any(p.is_symlink() for p in output.rglob('*')):
        raise ValueError('输出目录不允许符号链接')
    bg = load_bg(assets)
    jobs = json.loads((src / 'jobs.json').read_text(encoding='utf-8'))
    groups = defaultdict(list)
    seen = set()
    for job in jobs:
        name, key = job['name'], job['key']
        if name in seen or Path(name).name != name or '/' in name or '\\' in name or ':' in name:
            raise ValueError(f'任务名重复或越界：{name}')
        seen.add(name)
        rel = relative_image(job['image'])
        if key not in bg or job['image'] not in {l.get('image') for l in layers(bg[key])}:
            raise ValueError(f'任务与当前背景元数据不符：{name}')
        if len(job['size']) != 2 or any(type(n) is not int or n <= 0 for n in job['size']):
            raise ValueError(f'无效尺寸：{name}')
        if job['kind'] not in ('base', 'near', 'far', 'variant'):
            raise ValueError(f'无效任务类型：{name}')
        if not (assets / rel).is_file():
            raise ValueError(f'原图不存在：{rel}')
        groups[key].append(job)
    overlays = {key: sorted({l.get('image', l['type']) for l in layers(spec) if l.get('key')})
                for key, spec in sorted(bg.items()) if any(l.get('key') for l in layers(spec))}
    protected = {l['image'] for spec in bg.values() for l in layers(spec) if l.get('key') and l.get('image')}
    report = dict(mode='partial' if partial else 'complete', enabled=[], incomplete={}, errors={},
                  outputs=[], retained_overlays=overlays, unplanned=sorted(set(bg) - set(groups)),
                  unrecognized_raw=sorted(p.name for p in (src / 'raw').glob('*.png') if p.stem not in seen))
    converted = {}
    for key, group in sorted(groups.items()):
        missing = [j['name'] for j in group if not (src / 'raw' / (j['name'] + '.png')).is_file()]
        if missing:
            report['incomplete'][key] = sorted(missing)
        if missing and not partial:
            continue
        images = {}
        try:
            for job in group:
                path = src / 'raw' / (job['name'] + '.png')
                if not path.is_file():
                    continue
                # 变体参与整组完整性检查，但 key 开关层始终保留原图。
                image = convert(path, assets / relative_image(job['image']), job['size'], job['kind'] == 'near')
                if job['image'] not in protected:
                    images[relative_image(job['image']).as_posix()] = image
        except (OSError, ValueError) as exc:
            report['errors'][key] = str(exc)
            continue
        if images:
            report['enabled'].append(key)
            converted.update(images)
    output.mkdir(parents=True, exist_ok=True)
    for rel, im in sorted(converted.items()):
        target = output / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_suffix('.tmp')
        im.save(temp, format='PNG', optimize=False)
        temp.replace(target)
    # 仅管理专用输出目录；raw 被移除或组不完整时，旧替换图必须一起撤下。
    for old in output.rglob('*.png'):
        if old.relative_to(output).as_posix() not in converted:
            old.unlink()
    for folder in sorted(output.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
    report['outputs'] = sorted(converted)
    temp = output / '_report.tmp'
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(output / '_report.json')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--src', type=Path, default=DEFAULT_SRC)
    parser.add_argument('--partial', action='store_true', help='预览已有层；默认要求整组全部成图')
    args = parser.parse_args()
    report = run(args.src, args.partial)
    print(json.dumps({k: report[k] for k in ('mode', 'enabled', 'errors')}, ensure_ascii=False))
    print(f"待补齐 {len(report['incomplete'])} 组；保留开关叠加层 {len(report['retained_overlays'])} 组；详见 assets/bg_gpt/_report.json")
    return bool(report['errors'])


if __name__ == '__main__':
    sys.exit(main())
