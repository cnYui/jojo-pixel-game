# 将已生成的道具表裁成游戏像素图；保留源文件，所有输出均相对当前克隆。
from collections import deque

from PIL import Image, ImageChops, ImageFilter

from p5_paths import ASSETS, META, load_json, save_json

TARGETS = dict(taxi=(74, 34), taxi_hit=(74, 34), suitcase=(14, 12), shovel=(7, 16),
               frog=(11, 9), frog_hop=(11, 9), ladybug=(7, 6), butterfly=(11, 9),
               vine=(24, 40), zipper=(28, 10), banknote=(9, 5), insect_light=(5, 5))
SHEETS = [('props_sheet.png', 4, 3, dict(TARGETS)),
          ('props_sheet2.png', 3, 1, dict(gravel=(14, 7), bench=(34, 14), key=(11, 5)))]
TARGETS.update(SHEETS[1][3])
SOURCES = {cid: 'props_src/' + name for name, _, _, targets in SHEETS for cid in targets}
ALPHA = 128
OUTLINE = (26, 16, 32, 255)


def subject(cell):
    mask = cell.getchannel('A').point(lambda a: 255 if a >= ALPHA else 0)
    w, h = cell.size
    pixels = bytearray(mask.tobytes())
    components = []
    for start in range(w * h):
        if not pixels[start]:
            continue
        pixels[start] = 0
        pending, component = deque([start]), []
        while pending:
            i = pending.popleft()
            component.append(i)
            x, y = i % w, i // w
            for yy in range(max(0, y - 1), min(h, y + 2)):
                for xx in range(max(0, x - 1), min(w, x + 2)):
                    j = yy * w + xx
                    if pixels[j]:
                        pixels[j] = 0
                        pending.append(j)
        components.append(component)
    if not components:
        return None, None
    components.sort(key=len, reverse=True)
    keep = Image.new('L', cell.size)
    kp = keep.load()
    for i in components.pop(0):
        kp[i % w, i // w] = 255
    # 触须、叶片和青蛙脚可能断开；只收离主体约一个源像素块的小块，排除远处杂点。
    remaining = [c for c in components if len(c) >= 4]
    while remaining:
        near = keep.filter(ImageFilter.MaxFilter(25)).load()
        attached = [c for c in remaining if any(near[i % w, i // w] for i in c)]
        if not attached:
            break
        for c in attached:
            for i in c:
                kp[i % w, i // w] = 255
            remaining.remove(c)
    box = keep.getbbox()
    clean = cell.copy()
    clean.putalpha(keep)
    return clean.crop(box), box


def fit(image, target, pad=0):
    scale = min((target[0] - pad * 2) / image.width, (target[1] - pad * 2) / image.height, 1)
    size = tuple(max(1, round(v * scale)) for v in image.size)
    small = image.resize(size, Image.Resampling.BOX)
    small.putalpha(small.getchannel('A').point(lambda a: 255 if a >= ALPHA else 0))
    # 独立量化不透明颜色，透明像素不占调色板；关闭抖动避免小道具出现噪点。
    visible = [rgb for *rgb, a in small.getdata() if a]
    palette_source = Image.new('RGB', (len(visible), 1))
    palette_source.putdata([tuple(rgb) for rgb in visible])
    palette = palette_source.quantize(colors=24, method=Image.Quantize.MEDIANCUT)
    colour = small.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE).convert('RGBA')
    colour.putalpha(small.getchannel('A'))
    return colour


def pixelate(image, target, add_outline=True):
    small = fit(image, target)
    mask = small.getchannel('A')
    padded = Image.new('L', (small.width + 2, small.height + 2))
    padded.paste(mask, (1, 1))
    edge = ImageChops.subtract(padded, padded.filter(ImageFilter.MinFilter(3))).crop((1, 1, small.width + 1, small.height + 1))
    colours = [rgb for (*rgb, a), e in zip(small.getdata(), edge.getdata()) if a and e]
    dark = sum(max(rgb) < 100 for rgb in colours) / max(1, len(colours))
    outlined = add_outline and dark < .5
    if outlined:
        small = fit(image, target, 1)
        mask = Image.new('L', (small.width + 2, small.height + 2))
        mask.paste(small.getchannel('A'), (1, 1))
        ring = Image.new('RGBA', mask.size, OUTLINE)
        ring.putalpha(mask.filter(ImageFilter.MaxFilter(3)))
        ring.alpha_composite(small, (1, 1))
        small = ring
    canvas = Image.new('RGBA', target)
    canvas.alpha_composite(small, ((target[0] - small.width) // 2, target[1] - small.height))
    return canvas, outlined


def build(assets=ASSETS):
    props = {}
    for name, cols, rows, targets in SHEETS:
        source = assets / 'props_src' / name
        if not source.exists():
            continue
        sheet = Image.open(source).convert('RGBA')
        for index, (cid, size) in enumerate(targets.items()):
            col, row = index % cols, index // cols
            cell = (sheet.width * col // cols, sheet.height * row // rows,
                    sheet.width * (col + 1) // cols, sheet.height * (row + 1) // rows)
            cropped, box = subject(sheet.crop(cell))
            if cropped is None:
                continue
            # 钥匙仅高5像素，保留源图深色边；额外外描边会挤掉齿和匙环。
            image, outlined = pixelate(cropped, size, add_outline=cid != 'key')
            target = assets / f'props/{cid}.png'
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target)
            props[cid] = dict(image=f'props/{cid}', frames=1, size=list(size), pivot=[size[0] // 2, size[1]],
                              fps=1, kind='static', k=1, placeholder=False, source=SOURCES[cid],
                              sourceCell=list(cell), sourceBox=list(box), alphaThreshold=ALPHA, outlined=outlined)
    return props


def main():
    generated = build()
    meta = load_json(META / 'props.json', dict(props={}, scene={}))
    meta.setdefault('props', {}).update(generated)
    save_json(META / 'props.json', meta)
    print(f'生图道具：{len(generated)}个，二值透明、BOX缩小、24色量化')


if __name__ == '__main__':
    main()
