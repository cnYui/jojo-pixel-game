"""用临时假成图回归整组撤回、开关变体、near 抠色与循环接缝。"""
import base64
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bg_gpt_p4 as pipe
import build_p4 as build


def save_raw(scene, target):
    # 按正式 band 布局放大原图再加扰动，所有夹具只写临时目录。
    w, h = scene.size
    cw, ch = (1024, 1536) if h > w else (1536, 1024)
    k = min(cw / w, ch / h)
    x, y = round((cw - w * k) / 2), round((ch - h * k) / 2)
    raw = Image.new('RGBA', (cw, ch), (255, 0, 255, 255))
    enlarged = scene.resize((round(w * k), round(h * k)), Image.Resampling.NEAREST)
    raw.paste(enlarged, (x, y), enlarged)
    raw.save(target)


class PipelineTests(unittest.TestCase):
    def test_scaled_band_landscape_and_portrait(self):
        for size in [(480, 180), (120, 360), (320, 180)]:
            w, h = size
            cw, ch = (1024, 1536) if h > w else (1536, 1024)
            k = min(cw / w, ch / h)
            x, y = round((cw - w * k) / 2), round((ch - h * k) / 2)
            raw = Image.new('RGBA', (cw // 2, ch // 2), 'gray')
            box = (round(x / 2), round(y / 2), round((x + round(w * k)) / 2), round((y + round(h * k)) / 2))
            raw.paste((20, 90, 130, 255), box)
            self.assertEqual(set(pipe.crop_band(raw, size).getdata()), {(20, 90, 130, 255)})

    def test_group_variants_nested_foreground_and_runtime_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets, src, output = root / 'assets', root / 'src', root / 'assets/bg_gpt'
            (assets / '_meta').mkdir(parents=True)
            (assets / 'bg/demo').mkdir(parents=True)
            (src / 'raw').mkdir(parents=True)
            names = [('far', 'far'), ('near', 'near'), ('lit', 'variant'),
                     ('keyed', 'far'), ('nested', 'far'), ('front', 'near')]
            layer = lambda name, **kw: dict(type='pano', image=f'bg/demo/{name}', **kw)
            spec = {'demo': {'layers': [layer('far'), layer('near'), layer('lit', key='lamp'),
                                       layer('keyed', key='switch'),
                                       dict(type='group', layers=[layer('nested')]),
                                       layer('spark', key='spark')], 'fg': [layer('front')]}}
            (assets / '_meta/bg.json').write_text(json.dumps(spec), encoding='utf-8')
            jobs = [dict(name=f'demo__{name}', key='demo', image=f'bg/demo/{name}',
                         size=[32, 16], kind=kind) for name, kind in names]
            (src / 'jobs.json').write_text(json.dumps(jobs), encoding='utf-8')
            original = Image.new('RGBA', (32, 16), '#123456')
            changed = original.copy()
            ImageDraw.Draw(changed).rectangle((0, 0, 31, 15), fill=(40, 130, 60, 255))
            for name in [n for n, _ in names] + ['spark']:
                original.save(assets / f'bg/demo/{name}.png')
                if name not in ['lit', 'spark']:
                    save_raw(changed, src / f'raw/demo__{name}.png')
            before = {p: p.read_bytes() for p in (assets / 'bg/demo').glob('*.png')}
            self.assertEqual(pipe.run(src, assets=assets, output=output)['enabled'], [])
            self.assertEqual(pipe.run(src, partial=True, assets=assets, output=output)['enabled'], ['demo'])
            save_raw(changed, src / 'raw/demo__lit.png')
            report = pipe.run(src, assets=assets, output=output)
            self.assertEqual(report['enabled'], ['demo'])
            self.assertEqual(report['outputs'], sorted(f'bg/demo/{n}.png' for n, _ in names))
            self.assertEqual(report['retained_overlays'], {'demo': ['bg/demo/spark']})
            data = root / 'data'
            with patch.multiple(build.L, ASSETS=str(assets), META=str(assets / '_meta')), \
                 patch.object(build, 'DATA', str(data)), patch.object(sys, 'argv', ['build_p4.py', '--no-font']), \
                 redirect_stdout(StringIO()):
                build.main()
            pack = build.read_pack(data / 'img_bg_prologue.js')
            for name, _ in names:
                self.assertEqual(base64.b64decode(pack[f'bg/demo/{name}'].split(',')[1]),
                                 (output / f'bg/demo/{name}.png').read_bytes())
            self.assertEqual(base64.b64decode(pack['bg/demo/spark'].split(',')[1]), before[assets / 'bg/demo/spark.png'])
            snapshot = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
            pipe.run(src, assets=assets, output=output)
            self.assertEqual(snapshot, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})
            (src / 'raw/demo__lit.png').unlink()
            self.assertEqual(pipe.run(src, assets=assets, output=output)['enabled'], [])
            self.assertEqual(list(output.rglob('*.png')), [])
            (src / 'raw/demo__lit.png').write_bytes(b'incomplete PNG')
            self.assertIn('demo', pipe.run(src, assets=assets, output=output)['errors'])
            self.assertEqual(list(output.rglob('*.png')), [])
            self.assertTrue(all(p.read_bytes() == content for p, content in before.items()))

    def test_near_expansion_holes_fringe_and_genuine_pink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = Image.new('RGBA', (40, 24))
            original.paste((180, 110, 40, 255), (10, 8, 26, 22))
            original.paste((210, 20, 210, 255), (21, 15, 24, 18))
            original.save(root / 'original.png')
            scene = original.copy()
            scene.paste((30, 140, 80, 255), (7, 5, 29, 24))
            scene.paste((212, 22, 212, 255), (21, 15, 24, 18))
            scene.putpixel((23, 16), (255, 0, 255, 255))
            scene.paste((255, 0, 255, 255), (16, 12, 19, 15))
            scene.paste((205, 105, 195, 255), (7, 8, 8, 12))
            scene.paste((30, 140, 80, 255), (0, 0, 2, 2))
            scene.putpixel((5, 10), (30, 140, 80, 255))
            save_raw(scene, root / 'raw.png')
            # 高分辨率边缘再掺入幕布与粉色，覆盖缩小时的混色路径。
            with Image.open(root / 'raw.png') as image:
                image = image.convert('RGBA')
            band = pipe.crop_band(image, scene.size)
            self.assertGreater(band.width, scene.width)
            k = min(1536 / scene.width, 1024 / scene.height)
            y = round((1024 - scene.height * k) / 2)
            x = round(8 * k) + 1
            ImageDraw.Draw(image).line((x, y + round(8 * k), x, y + round(12 * k)),
                                       fill=(255, 0, 255, 255), width=2)
            image.save(root / 'raw.png')
            result = pipe.convert(root / 'raw.png', root / 'original.png', scene.size, near=True)
            for point in [(8, 6), (28, 20)]:
                pixel = result.getpixel(point)
                self.assertEqual(pixel[3], 255)
                self.assertLessEqual(max(abs(a - b) for a, b in zip(pixel[:3], (30, 140, 80))), 2)
            self.assertEqual(result.getpixel((17, 13))[3], 0)
            self.assertEqual(result.getpixel((0, 0))[3], 0)
            self.assertEqual(result.getpixel((5, 10))[3], 0)
            self.assertEqual(result.getpixel((7, 9))[3], 0)
            self.assertEqual(result.getpixel((22, 16)), (212, 22, 212, 255))
            self.assertEqual(result.getpixel((23, 16))[3], 0)
            self.assertNotIn((180, 110, 40, 255), set(result.getdata()))
            for p, o in zip(result.getdata(), original.getdata()):
                if p[3]:
                    self.assertTrue(not pipe.pink_fringe(p) or pipe.original_pink(p, o))
                else:
                    self.assertEqual(p, (0, 0, 0, 0))
            self.assertEqual(set(result.getchannel('A').getdata()), {0, 255})
            self.assertLessEqual(len({p[:3] for p in result.getdata() if p[3]}), 96)

    def test_wrap_manifest_seams_rgb_alpha_and_pixel_palette(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets, src = root / 'assets', root / 'src'
            (assets / '_meta').mkdir(parents=True)
            (assets / 'bg/loop').mkdir(parents=True)
            (src / 'raw').mkdir(parents=True)
            original = Image.new('RGBA', (64, 24))
            original.paste((30, 120, 80, 255), (0, 8, 64, 24))
            original.save(assets / 'bg/loop/near.png')
            scene = original.copy()
            scene.paste((50, 90, 160, 255), (32, 8, 64, 24))
            scene.paste((30, 120, 80, 255), (0, 5, 4, 8))
            scene.paste((255, 0, 255, 255), (60, 8, 64, 11))
            save_raw(scene, src / 'raw/loop__near.png')
            (assets / '_meta/bg.json').write_text(json.dumps({'loop': {'layers': [
                dict(type='wrap', image='bg/loop/near')]}}), encoding='utf-8')
            (src / 'jobs.json').write_text(json.dumps([dict(name='loop__near', key='loop',
                image='bg/loop/near', size=[64, 24], kind='near', wrap=True)]), encoding='utf-8')
            plain = pipe.convert(src / 'raw/loop__near.png', assets / 'bg/loop/near.png', [64, 24], near=True)
            output = assets / 'bg_gpt'
            self.assertEqual(pipe.run(src, assets=assets, output=output)['enabled'], ['loop'])
            with Image.open(output / 'bg/loop/near.png') as im:
                result = im.convert('RGBA')
            self.assertNotEqual(plain.crop((0, 0, 1, 24)).tobytes(), plain.crop((63, 0, 64, 24)).tobytes())
            self.assertEqual(result.crop((0, 0, 1, 24)).tobytes(), result.crop((63, 0, 64, 24)).tobytes())
            self.assertEqual(result.crop((0, 0, 60, 24)).tobytes(), plain.crop((0, 0, 60, 24)).tobytes())
            self.assertLessEqual(set(result.getdata()), set(plain.getdata()))
            for width in [1, 2, 3, 4, 16]:
                small = scene.resize((width, 24), Image.Resampling.NEAREST)
                loop = pipe.seamless_wrap(small)
                self.assertEqual(loop.crop((0, 0, 1, 24)).tobytes(), loop.crop((width - 1, 0, width, 24)).tobytes())


if __name__ == '__main__':
    unittest.main()
