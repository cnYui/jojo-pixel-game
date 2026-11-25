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


def magenta(rgb, green=False):
    r, g, b = rgb[:3]
    # 小孔里的幕布会混入暗树色；按幕布占比而非亮度识别，避开高绿或偏红的樱花。
    excess = min(r, b) - g
    limit = 100 if green and g < 100 else 64
    ratio = (0.45 if green else 0.5) if g < 100 else 0.78
    return -64 <= r - b <= limit and excess > 25 and excess >= (255 - g) * ratio


def original_pink(pixel, original):
    # 真正的纯洋红始终是幕布；旧图紫红物件只在原位置且颜色相近时豁免。
    r, g, b = original[:3]
    return (original[3] >= 128 and min(r, b) - g > 35 and abs(r - b) <= 32 and
            sum(abs(c - k) for c, k in zip(original[:3], (255, 0, 255))) >= 60 and
            sum(abs(a - b) for a, b in zip(pixel[:3], (255, 0, 255))) >= 60 and
            max(abs(a - b) for a, b in zip(pixel[:3], original[:3])) <= 24)


def key_and_despill(crop, reference):
    """只在原始分辨率的幕布边界三像素内去溢色，保留花瓣和细线轮廓。"""
    pixels, originals = list(crop.getdata()), list(reference.getdata())
    # 绿树缝隙的混色会明显偏红；只在旧绿色植被附近放宽色相，樱花区仍用保粉门槛。
    foliage = Image.new('L', crop.size)
    foliage.putdata([255 if o[3] >= 128 and o[1] - o[0] >= 8 and o[1] - o[2] >= 5
                     else 0 for o in originals])
    foliage = foliage.filter(ImageFilter.MaxFilter(7))
    greens = list(foliage.getdata())
    removed = Image.new('L', crop.size)
    removed.putdata([255 if magenta(p, green) and not original_pink(p, o) else 0
                     for p, o, green in zip(pixels, originals, greens)])
    border = removed.filter(ImageFilter.MaxFilter(7))
    result = []
    for p, o, cut, edge, green in zip(pixels, originals, removed.getdata(), border.getdata(), greens):
        r, g, b, a = p
        if cut:
            result.append((0, 0, 0, 0))
            continue
        # 高绿粉色和红蓝差大的樱花不去色；原生紫红物件仍按同位置颜色匹配保护。
        if (edge and a and g < (130 if green else 100) and min(r, b) - g > 25 and
                -64 <= r - b <= (100 if green else 64) and not original_pink(p, o)):
            excess = min(r, b) - g
            if excess >= (255 - g) * 0.8:
                result.append((0, 0, 0, 0))
                continue
            r, b = r - excess, b - excess
        result.append((r, g, b, a) if a else (0, 0, 0, 0))
    keyed = Image.new('RGBA', crop.size)
    keyed.putdata(result)
    return keyed


def seamless_wrap(image):
    """在右端重叠带找最小误差缝，整像素接到左端镜像，不混色也不模糊 alpha。"""
    image = image.copy()
    w, h = image.size
    if w < 2:
        return image
    band = min(w // 2, max(2, min(16, w // 16)))
    if band < 2:
        image.paste(image.crop((0, 0, 1, h)), (w - 1, 0))
        return image
    pixels = image.load()
    costs, parents = [], []
    for y in range(h):
        row, prev = [], []
        for x in range(band - 1):
            a, b = pixels[w - band + x, y], pixels[band - 1 - x, y]
            # 透明 RGB 不影响观感；alpha 差异也纳入误差，避免缝穿过轮廓。
            error = sum(abs(a[c] * a[3] - b[c] * b[3]) // 255 for c in range(3)) + abs(a[3] - b[3]) * 3
            parent = min(range(max(0, x - 1), min(band - 1, x + 2)),
                         key=lambda k: (costs[-1][k], k)) if y else x
            row.append(error + (costs[-1][parent] if y else 0))
            prev.append(parent)
        costs.append(row)
        parents.append(prev)
    seam = min(range(band - 1), key=lambda x: (costs[-1][x], x))
    for y in range(h - 1, -1, -1):
        for x in range(seam, band):
            pixels[w - band + x, y] = pixels[band - 1 - x, y]
        seam = parents[y][seam]
    return image


def convert(raw_path, original_path, size, near=False, wrap=False):
    with Image.open(original_path) as im:
        original = im.convert('RGBA')
    if original.size != tuple(size):
        raise ValueError(f'原图尺寸 {original.size} 与清单 {size} 不同')
    with Image.open(raw_path) as im:
        crop = crop_band(im.convert('RGBA'), size)
    if near:
        opaque = original.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
        reference = original.resize(crop.size, Image.Resampling.NEAREST)
        crop = key_and_despill(crop, reference)
    # 显式预乘 alpha，完全透明的幕布 RGB 不得进入 BOX 的颜色平均。
    small = crop.convert('RGBa').resize(tuple(size), Image.Resampling.BOX).convert('RGBA')
    alpha = small.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    if near:
        # 允许新增顶面和侧面伸出四个游戏像素，仅用旧轮廓限制远处杂点。
        alpha = ImageChops.multiply(alpha, opaque.filter(ImageFilter.MaxFilter(9)))
    # 保留 BOX 的真彩色：按面积训练的调色板会把长椅、路牌等稀少暖色并入灰绿。
    result = small
    result.putalpha(alpha)
    result.putdata([p if p[3] else (0, 0, 0, 0) for p in result.getdata()])
    return seamless_wrap(result) if wrap else result


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
    planned = {job['image'] for job in jobs}
    overlays = {key: sorted({l.get('image', l['type']) for l in layers(spec)
                            if l.get('key') and l.get('image') not in planned})
                for key, spec in sorted(bg.items())}
    overlays = {key: value for key, value in overlays.items() if value}
    report = dict(mode='partial' if partial else 'complete', enabled=[], baked_clouds=[], incomplete={}, errors={},
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
                image = convert(path, assets / relative_image(job['image']), job['size'],
                                job['kind'] == 'near', job.get('wrap', False))
                images[relative_image(job['image']).as_posix()] = image
        except (OSError, ValueError) as exc:
            report['errors'][key] = str(exc)
            continue
        if images:
            report['enabled'].append(key)
            # 当前远景成图已包含天空云层；只有实际接入 far 的背景才撤下程序云。
            if any(j['kind'] == 'far' and relative_image(j['image']).as_posix() in images for j in group):
                report['baked_clouds'].append(key)
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
