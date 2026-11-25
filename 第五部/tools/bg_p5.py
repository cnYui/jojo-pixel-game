# 大图只负责视觉，地图宽度和可走带固定在元数据中，换背景不会改变剧情坐标。
import argparse
from PIL import Image, ImageDraw, ImageFilter

from p5_paths import ASSETS, META, BACKGROUNDS, load_json, save_json


def crop_source(image, width, offset=0, sharpen=False):
    """等比居中裁切；offset为源图像素，正数往下，边界自动夹紧。"""
    image = image.convert('RGB')
    w, h = image.size
    ratio = width / 180
    if w / h > ratio:
        cw, ch = max(1, round(h * ratio)), h
    else:
        cw, ch = w, max(1, round(w / ratio))
    x = (w - cw) // 2
    y = max(0, min(h - ch, round((h - ch) / 2 + offset)))
    image = image.crop((x, y, x + cw, y + ch)).resize((width, 180), Image.Resampling.BOX)
    if sharpen:
        image = image.filter(ImageFilter.UnsharpMask(radius=.6, percent=80, threshold=3))
    return image.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)


def placeholder(map_id, width, indoor):
    im = Image.new('RGB', (width, 180), '#7698ad' if not indoor else '#76698b')
    d = ImageDraw.Draw(im)
    if indoor:
        d.rectangle((0, 0, width, 65), fill='#bcb0b6')
        d.line((0, 66, width, 66), fill='#574963')
        d.rectangle((0, 139, width, 179), fill='#6a5864')
        d.line((0, 138, width, 138), fill='#30273d')
    else:
        d.rectangle((0, 118, width, 149), fill='#8b9280')
        d.rectangle((0, 150, width, 179), fill='#9c8974')
    # 地面线与可走带端点在占位图上可见，方便检查脚底与背景的比例。
    d.line((0, 150, width, 150), fill='#443949')
    d.line((8, 176, width - 8, 176), fill='#b8a187')
    d.text((12, 78), map_id, fill='#fff2cd')
    return im.quantize(colors=64, dither=Image.Dither.NONE)


def build(offsets=None, sharpen=False):
    # 把已验收的构图保存在源图旁；命令行只覆盖本次指定的背景。
    offsets = {**load_json(ASSETS / 'bg_src/offsets.json', {}), **(offsets or {})}
    keys = {item[1] for item in BACKGROUNDS}
    if any(key not in keys or type(value) is not int for key, value in offsets.items()):
        raise ValueError('offsets.json 必须是背景键到整数裁切偏移的映射')
    meta = {}
    for map_id, key, width, indoor, pack in BACKGROUNDS:
        source = ASSETS / 'bg_src' / (key + '.png')
        out = ASSETS / 'bg' / key / 'base.png'
        out.parent.mkdir(parents=True, exist_ok=True)
        if source.exists():
            with Image.open(source) as im:
                result = crop_source(im, width, offsets.get(key, 0), sharpen)
        else:
            result = placeholder(map_id, width, indoor)
        result.save(out)
        anchors = dict(entrance=[24, 160], exit=[width - 24, 160], spawn=[80, 160],
                       exit_x=width - 24, walk_x=[8, width - 8], ground_y=150)
        if indoor:
            anchors['wall_y'] = 138
            anchors['ceiling_y'] = 66
        meta[key] = dict(pack=pack, w=width, h=180, ground=150, walk=[142, 176], anchors=anchors,
                         layers=[dict(type='pano', image=f'bg/{key}/base', k=1, x=0, y=0)], fg=[],
                         placeholder=not source.exists(), cropY=offsets.get(key, 0))
        print(f'{key}: {width}×180，' + ('源图裁切' if source.exists() else '占位图'))
    save_json(META / 'bg.json', meta)


def main():
    parser = argparse.ArgumentParser(description='第五部背景：BOX缩放后量化到64色；裁切偏移以源图像素计算。')
    parser.add_argument('--crop-y', action='append', nargs='+', default=[], metavar='键=偏移')
    parser.add_argument('--sharpen', action='store_true', help='量化前轻度锐化')
    args = parser.parse_args()
    offsets = {}
    keys = {item[1] for item in BACKGROUNDS}
    for group in args.crop_y:
        for value in group:
            try:
                key, amount = value.split('=', 1)
                if key not in keys:
                    raise ValueError('未知背景键')
                offsets[key] = int(amount)
            except ValueError:
                parser.error(f'裁切参数无效：{value}，应为背景键=整数偏移')
    build(offsets, args.sharpen)


if __name__ == '__main__':
    main()
