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


def layer_images(spec):
    for layer in layers(spec):
        if layer.get('image'):
            yield layer['image']
        yield from layer.get('images', [])


def relative_image(image):
    path = PurePosixPath(image)
    if not path.parts or '\\' in image or ':' in image or path.is_absolute() or '..' in path.parts or path.parts[0] != 'bg':
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


def finish_crop(crop, original, near=False, margin=4):
    size = original.size
    if near:
        opaque = original.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
        reference = original.resize(crop.size, Image.Resampling.NEAREST)
        crop = key_and_despill(crop, reference)
    # 显式预乘 alpha，完全透明的幕布 RGB 不得进入 BOX 的颜色平均。
    small = crop.convert('RGBa').resize(tuple(size), Image.Resampling.BOX).convert('RGBA')
    alpha = small.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    if near:
        # 用游戏像素限制外轮廓；小图层只放宽两像素，避免盖住相邻门框。
        alpha = ImageChops.multiply(alpha, opaque.filter(ImageFilter.MaxFilter(margin * 2 + 1)))
    # 保留 BOX 的真彩色：按面积训练的调色板会把长椅、路牌等稀少暖色并入灰绿。
    result = small
    result.putalpha(alpha)
    result.putdata([p if p[3] else (0, 0, 0, 0) for p in result.getdata()])
    return result


def convert(raw_path, original_path, size, near=False, wrap=False):
    with Image.open(original_path) as im:
        original = im.convert('RGBA')
    if original.size != tuple(size):
        raise ValueError(f'原图尺寸 {original.size} 与清单 {size} 不同')
    with Image.open(raw_path) as im:
        crop = crop_band(im.convert('RGBA'), size)
    result = finish_crop(crop, original, near)
    return seamless_wrap(result) if wrap else result


def convert_overlay(raw_path, original_path, job):
    with Image.open(original_path) as im:
        original = im.convert('RGBA')
    if original.size != tuple(job['size']):
        raise ValueError(f"原图尺寸 {original.size} 与清单 {job['size']} 不同")
    box = job['crop']
    if (len(box) != 4 or any(type(n) is not int for n in box) or
            not (0 <= box[0] < box[2] <= original.width and 0 <= box[1] < box[3] <= original.height)):
        raise ValueError(f'无效裁切框：{box}')
    reference = original.crop(box)
    with Image.open(raw_path) as im:
        crop = crop_band(im.convert('RGBA'), reference.size)
    small = finish_crop(crop, reference, near=True, margin=2)
    result = Image.new('RGBA', original.size)
    result.paste(small, box[:2])
    return result


def masked_image(image, original, margin=0):
    if image.size != original.size:
        raise ValueError(f'派生层尺寸不同：来源 {image.size}，原图 {original.size}')
    mask = original.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    if margin:
        mask = mask.filter(ImageFilter.MaxFilter(margin * 2 + 1))
    result = image.copy()
    result.putalpha(ImageChops.multiply(image.getchannel('A'), mask))
    result.putdata([p if p[3] else (0, 0, 0, 0) for p in result.getdata()])
    return result


def add_overlays(src, assets, bg, converted, report):
    manifest = src / 'overlays.json'
    jobs = json.loads(manifest.read_text(encoding='utf-8')) if manifest.is_file() else []
    status = report['overlays'] = dict(enabled=[], missing=[], errors={}, derived={}, comparisons={})
    seen, images = set(), set()
    for job in jobs:
        name = job['name']
        try:
            if (name in seen or not name or Path(name).name != name or
                    any(c in name for c in ('/', '\\', ':'))):
                raise ValueError(f'任务名重复或越界：{name}')
            seen.add(name)
            rel = relative_image(job['image']).as_posix()
            if rel in images or rel in converted:
                raise ValueError(f"重复图层：{job['image']}")
            images.add(rel)
            if job['key'] not in bg or job['image'] not in set(layer_images(bg[job['key']])):
                raise ValueError(f'任务与当前背景元数据不符：{name}')
            raw = src / 'raw_ovl' / (name + '.png')
            if not raw.is_file():
                status['missing'].append(name)
                continue
            converted[rel] = convert_overlay(raw, assets / rel, job)
            status['enabled'].append(name)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            # 小图层失败不能撤下所在背景组，也不能沿用上次的替换图。
            status['errors'][name] = str(exc)
    status['unrecognized_raw'] = sorted(p.name for p in (src / 'raw_ovl').glob('*.png') if p.stem not in seen)

    def derive(target, source, kind):
        rel, origin = relative_image(target).as_posix(), relative_image(source).as_posix()
        info = status['derived'][target] = dict(source=source, kind=kind, status='missing_source')
        if origin not in converted:
            return
        try:
            with Image.open(assets / rel) as im:
                original = im.convert('RGBA')
            image = converted[origin]
            if kind == 'reuse':
                with Image.open(assets / relative_image(source)) as im:
                    source_original = im.convert('RGBA')
                same_size = original.size == source_original.size
                same_alpha = same_size and ImageChops.difference(
                    original.getchannel('A'), source_original.getchannel('A')).getbbox() is None
                status['comparisons'][target] = dict(source_size=list(source_original.size),
                    target_size=list(original.size), same_size=same_size, same_alpha=same_alpha)
                if not same_size:
                    raise ValueError('两个原船层尺寸不同，不能原样复用')
                result = image.copy()
                if not same_alpha:
                    info['note'] = '两个原船层 alpha 形状不同；按要求复用来源处理结果'
            elif kind == 'pots_alpha_1':
                result = masked_image(image, original, margin=1)
            else:
                gray = image.convert('L').convert('RGBA')
                gray.putalpha(image.getchannel('A'))
                result = masked_image(gray, original)
                # 原生成脚本以这个暖白色画拍立得相框，保留边框像素而不复制旧房间。
                result.putdata([o if o[3] and o[:3] == (244, 242, 234) else p
                                for p, o in zip(result.getdata(), original.getdata())])
                info['preserved_frame_rgb'] = [244, 242, 234]
            converted[rel] = result
            info['status'] = 'enabled'
        except (OSError, ValueError) as exc:
            info['status'] = 'error'
            status['errors'][target] = str(exc)

    for n in range(1, 6):
        derive(f'bg/nijimura_yard/pots_{n}', 'bg/nijimura_yard/pots_0', 'pots_alpha_1')
    derive('bg/morioh_harbor_late/ship', 'bg/morioh_harbor/ship', 'reuse')
    derive('bg/kira_house/photo', 'bg/kira_house/room', 'photo_gray')


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
        if key not in bg or job['image'] not in set(layer_images(bg[key])):
            raise ValueError(f'任务与当前背景元数据不符：{name}')
        if len(job['size']) != 2 or any(type(n) is not int or n <= 0 for n in job['size']):
            raise ValueError(f'无效尺寸：{name}')
        if job['kind'] not in ('base', 'near', 'far', 'variant'):
            raise ValueError(f'无效任务类型：{name}')
        if not (assets / rel).is_file():
            raise ValueError(f'原图不存在：{rel}')
        groups[key].append(job)
    report = dict(mode='partial' if partial else 'complete', enabled=[], baked_clouds=[], incomplete={}, errors={},
                  outputs=[], retained_overlays={}, unplanned=sorted(set(bg) - set(groups)),
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
    add_overlays(src, assets, bg, converted, report)
    planned = {job['image'] for job in jobs}
    for key, spec in sorted(bg.items()):
        retained = set()
        for layer in layers(spec):
            if not layer.get('key'):
                continue
            paths = ([layer['image']] if layer.get('image') else []) + layer.get('images', [])
            retained.update(p for p in paths if p not in planned and relative_image(p).as_posix() not in converted)
            if not paths:
                retained.add(layer['type'])
        if retained:
            report['retained_overlays'][key] = sorted(retained)
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
    print(f"待补齐 {len(report['incomplete'])} 组；小图层接入 {len(report['overlays']['enabled'])} 项，待补齐 {len(report['overlays']['missing'])} 项；详见 assets/bg_gpt/_report.json")
    return bool(report['errors'] or report['overlays']['errors'])


if __name__ == '__main__':
    sys.exit(main())
