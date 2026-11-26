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
    def test_overlay_crop_mask_offset_and_size_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for box in ([10, 5, 30, 20], [10, 5, 20, 23]):
                original = Image.new('RGBA', (48, 32))
                original.paste((40, 90, 30, 255), (box[0] + 4, box[1] + 4, box[2] - 2, box[3] - 2))
                original.save(root / 'original.png')
                scene = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (255, 0, 255, 255))
                scene.paste((60, 130, 70, 255), (0, 0, scene.width, scene.height))
                scene.putpixel((5, 5), (255, 0, 255, 255))
                save_raw(scene, root / 'raw.png')
                job = dict(size=[48, 32], crop=box)
                result = pipe.convert_overlay(root / 'raw.png', root / 'original.png', job)
                self.assertEqual(result.size, original.size)
                self.assertEqual(result.getpixel((box[0] + 2, box[1] + 2)), (60, 130, 70, 255))
                self.assertEqual(result.getpixel((box[0] + 1, box[1] + 2)), (0, 0, 0, 0))
                self.assertEqual(result.getpixel((box[0] + 5, box[1] + 5)), (0, 0, 0, 0))
                self.assertEqual(result.getpixel((0, 0)), (0, 0, 0, 0))
                with self.assertRaises(ValueError):
                    pipe.convert_overlay(root / 'raw.png', root / 'original.png', dict(size=[1, 1], crop=box))
                for invalid in ([-1, 0, 10, 10], [0, 0, 49, 32], [4, 0, 4, 3]):
                    with self.assertRaises(ValueError):
                        pipe.convert_overlay(root / 'raw.png', root / 'original.png', dict(size=[48, 32], crop=invalid))

    def test_optional_pick_fallback_pack_and_stale_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets, src, output = root / 'assets', root / 'src', root / 'assets/bg_gpt'
            (assets / '_meta').mkdir(parents=True)
            (assets / 'bg/demo').mkdir(parents=True)
            (src / 'raw').mkdir(parents=True)
            (src / 'raw_ovl').mkdir()
            spec = {'demo': {'layers': [dict(type='pano', image='bg/demo/room'),
                dict(type='pick', images=['bg/demo/open', 'bg/demo/closed'], key='gate')]}}
            (assets / '_meta/bg.json').write_text(json.dumps(spec), encoding='utf-8')
            (src / 'jobs.json').write_text(json.dumps([dict(name='demo__room', key='demo',
                image='bg/demo/room', size=[32, 16], kind='base')]), encoding='utf-8')
            jobs = [dict(name=f'demo__{n}', key='demo', image=f'bg/demo/{n}', size=[32, 16],
                         crop=[4, 2, 24, 14]) for n in ('open', 'closed')]
            (src / 'overlays.json').write_text(json.dumps(jobs), encoding='utf-8')
            old = Image.new('RGBA', (32, 16), (20, 30, 40, 255))
            new = Image.new('RGBA', (32, 16), (80, 120, 70, 255))
            for n in ('room', 'open', 'closed'):
                old.save(assets / f'bg/demo/{n}.png')
            save_raw(new, src / 'raw/demo__room.png')
            save_raw(new.crop((4, 2, 24, 14)), src / 'raw_ovl/demo__open.png')
            report = pipe.run(src, assets=assets, output=output)
            self.assertEqual(report['enabled'], ['demo'])
            self.assertEqual(report['overlays']['enabled'], ['demo__open'])
            self.assertEqual(report['overlays']['missing'], ['demo__closed'])
            self.assertEqual(report['retained_overlays'], {'demo': ['bg/demo/closed']})
            data = root / 'data'
            with patch.multiple(build.L, ASSETS=str(assets), META=str(assets / '_meta')), \
                 patch.object(build, 'DATA', str(data)), patch.object(sys, 'argv', ['build_p4.py', '--no-font']), \
                 redirect_stdout(StringIO()):
                build.main()
            pack = build.read_pack(data / 'img_bg_prologue.js')
            self.assertEqual(base64.b64decode(pack['bg/demo/open'].split(',')[1]), (output / 'bg/demo/open.png').read_bytes())
            self.assertEqual(base64.b64decode(pack['bg/demo/closed'].split(',')[1]), (assets / 'bg/demo/closed.png').read_bytes())
            # 损坏或移除可选层时只撤下该层，完整背景继续启用。
            (src / 'raw_ovl/demo__open.png').write_bytes(b'incomplete PNG')
            report = pipe.run(src, assets=assets, output=output)
            self.assertEqual(report['enabled'], ['demo'])
            self.assertIn('demo__open', report['overlays']['errors'])
            self.assertFalse((output / 'bg/demo/open.png').exists())
            (src / 'raw_ovl/demo__open.png').unlink()
            report = pipe.run(src, assets=assets, output=output)
            self.assertEqual(report['enabled'], ['demo'])
            self.assertEqual(report['overlays']['missing'], ['demo__open', 'demo__closed'])

    def test_derived_pots_ship_photo_and_missing_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = Image.new('RGBA', (16, 12), (80, 120, 60, 255))
            source.putpixel((6, 6), (0, 0, 0, 0))
            converted = {f'bg/{p}.png': source.copy() for p in (
                'nijimura_yard/pots_0', 'morioh_harbor/ship', 'kira_house/room')}
            originals = {}
            paths = ['nijimura_yard/pots_' + str(n) for n in range(1, 6)] + [
                'morioh_harbor/ship', 'morioh_harbor_late/ship', 'kira_house/photo']
            for p in paths:
                original = Image.new('RGBA', source.size)
                original.paste((120, 130, 140, 255), (4, 4, 10, 10))
                if p == 'kira_house/photo':
                    original.putpixel((4, 4), (244, 242, 234, 255))
                target = root / ('bg/' + p + '.png')
                target.parent.mkdir(parents=True, exist_ok=True)
                original.save(target)
                originals[p] = original
            report = {}
            pipe.add_overlays(root, root, {}, converted, report)
            self.assertEqual(report['overlays']['errors'], {})
            self.assertEqual(len(converted), 10)
            for n in range(1, 6):
                result = converted[f'bg/nijimura_yard/pots_{n}.png']
                self.assertEqual(result.getpixel((3, 3)), source.getpixel((3, 3)))
                self.assertEqual(result.getpixel((2, 3)), (0, 0, 0, 0))
            self.assertEqual(converted['bg/morioh_harbor_late/ship.png'].tobytes(), source.tobytes())
            self.assertTrue(report['overlays']['comparisons']['bg/morioh_harbor_late/ship']['same_alpha'])
            result = converted['bg/kira_house/photo.png']
            self.assertEqual(result.getpixel((0, 0)), (0, 0, 0, 0))
            self.assertEqual(result.getpixel((4, 4)), (244, 242, 234, 255))
            gray = source.convert('L').getpixel((5, 5))
            self.assertEqual(result.getpixel((5, 5)), (gray, gray, gray, 255))
            self.assertEqual(result.getpixel((6, 6)), (0, 0, 0, 0))
            empty = {}
            pipe.add_overlays(root, root, {}, empty, report)
            self.assertEqual(empty, {})
            self.assertTrue(all(v['status'] == 'missing_source' for v in report['overlays']['derived'].values()))
            changed_shape = originals['morioh_harbor_late/ship'].copy()
            changed_shape.putpixel((0, 0), (1, 2, 3, 255))
            changed_shape.save(root / 'bg/morioh_harbor_late/ship.png')
            pipe.add_overlays(root, root, {}, {'bg/morioh_harbor/ship.png': source}, report)
            self.assertFalse(report['overlays']['comparisons']['bg/morioh_harbor_late/ship']['same_alpha'])
            self.assertIn('note', report['overlays']['derived']['bg/morioh_harbor_late/ship'])
            Image.new('RGBA', (12, 12)).save(root / 'bg/morioh_harbor_late/ship.png')
            converted = {'bg/morioh_harbor/ship.png': source}
            pipe.add_overlays(root, root, {}, converted, report)
            self.assertIn('bg/morioh_harbor_late/ship', report['overlays']['errors'])
            self.assertFalse(report['overlays']['comparisons']['bg/morioh_harbor_late/ship']['same_size'])

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
            cloud = dict(type='clouds', clouds=[], span=520)
            spec = {'demo': {'layers': [cloud, layer('far'), layer('near'), layer('lit', key='lamp'),
                                       layer('keyed', key='switch'),
                                       dict(type='group', layers=[cloud, layer('nested')]),
                                       layer('spark', key='spark')], 'fg': [cloud, layer('front')]},
                    'untouched': {'layers': [cloud]}}
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
            self.assertEqual(report['baked_clouds'], ['demo'])
            self.assertEqual(report['outputs'], sorted(f'bg/demo/{n}.png' for n, _ in names))
            self.assertEqual(report['retained_overlays'], {'demo': ['bg/demo/spark']})
            data = root / 'data'
            with patch.multiple(build.L, ASSETS=str(assets), META=str(assets / '_meta')), \
                 patch.object(build, 'DATA', str(data)), patch.object(sys, 'argv', ['build_p4.py', '--no-font']), \
                 redirect_stdout(StringIO()):
                build.main()
            pack = build.read_pack(data / 'img_bg_prologue.js')
            runtime = build.read_gd(data / 'data_meta.js')['bg']
            self.assertFalse(any(l['type'] == 'clouds' for l in pipe.layers(runtime['demo'])))
            self.assertEqual(runtime['untouched'], spec['untouched'])
            self.assertEqual(build.generated_background(spec['demo']), spec['demo'])
            self.assertEqual(sum(l['type'] == 'clouds' for l in pipe.layers(spec['demo'])), 3)
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
            with patch.multiple(build.L, ASSETS=str(assets), META=str(assets / '_meta')), \
                 patch.object(build, 'DATA', str(data)), patch.object(sys, 'argv', ['build_p4.py', '--no-font']), \
                 redirect_stdout(StringIO()):
                build.main()
            self.assertEqual(build.read_gd(data / 'data_meta.js')['bg'], spec)
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
            self.assertEqual(result.getpixel((7, 9))[3], 255)
            self.assertEqual(result.getpixel((22, 16)), (212, 22, 212, 255))
            self.assertEqual(result.getpixel((23, 16))[3], 0)
            self.assertNotIn((180, 110, 40, 255), set(result.getdata()))
            for p in result.getdata():
                if not p[3]:
                    self.assertEqual(p, (0, 0, 0, 0))
            self.assertEqual(set(result.getchannel('A').getdata()), {0, 255})

    def test_rare_warm_accents_survive_gray_green_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            size = (256, 64)
            scene = Image.new('RGBA', size)
            # 数千种灰绿占据几乎全部像素，避免少数纯色的简单夹具掩盖调色板丢色。
            scene.putdata([(35 + (x * 7 + y * 3) % 110,
                            45 + (x * 3 + y * 11) % 120,
                            35 + (x * 13 + y * 5) % 100, 255)
                           for y in range(size[1]) for x in range(size[0])])
            accents = [(231, 34, 26, 255), (228, 126, 27, 255),
                       (245, 197, 32, 255), (248, 130, 218, 255)]
            for x, color in enumerate(accents, 20):
                scene.putpixel((x, 30), color)
            scene.save(root / 'original.png')
            raw = scene.resize((512, 128), Image.Resampling.NEAREST)
            raw.save(root / 'raw.png')
            for near in (False, True):
                with self.subTest(near=near):
                    with patch.object(pipe, 'crop_band', return_value=raw):
                        result = pipe.convert(root / 'raw.png', root / 'original.png', size, near=near)
                    for x, color in enumerate(accents, 20):
                        pixel = result.getpixel((x, 30))
                        self.assertEqual(pixel[3], 255)
                        self.assertLessEqual(max(abs(a - b) for a, b in zip(pixel[:3], color[:3])), 2)

    def test_dim_screen_holes_without_bright_seed_and_warm_edges(self):
        raw = Image.new('RGBA', (32, 24), (40, 80, 45, 255))
        # 整个小孔都低于旧亮度门槛，内部也远离任何纯洋红种子。
        raw.paste((190, 20, 185, 255), (2, 2, 15, 15))
        raw.paste((192, 34, 165, 255), (18, 12, 23, 17))
        raw.putpixel((25, 20), (234, 136, 231, 255))
        original = Image.new('RGBA', raw.size)
        original.paste((30, 58, 46, 255), (18, 12, 23, 17))
        raw.putpixel((20, 14), (218, 35, 152, 255))
        colors = [(231, 34, 26, 255), (228, 126, 27, 255),
                  (245, 197, 32, 255), (248, 130, 218, 255),
                  (240, 40, 175, 255), (205, 105, 195, 255)]
        for y, color in enumerate(colors, 3):
            raw.putpixel((15, y), color)
        original.putpixel((8, 8), (188, 20, 188, 255))
        raw.putpixel((8, 8), (190, 22, 190, 255))
        result = pipe.key_and_despill(raw, original)
        for point in [(3, 3), (7, 7), (14, 14), (20, 14), (25, 20)]:
            self.assertEqual(result.getpixel(point), (0, 0, 0, 0))
        self.assertEqual(result.getpixel((8, 8)), (190, 22, 190, 255))
        for y, color in enumerate(colors, 3):
            self.assertEqual(result.getpixel((15, y)), color)

        # 同样偏红的真实花瓣由旧樱花区保护，绿树去混色不得扩散到整张图。
        original.paste((0, 0, 0, 0), (17, 11, 24, 18))
        original.putpixel((20, 14), (240, 100, 180, 255))
        raw.putpixel((20, 14), (240, 40, 175, 255))
        self.assertEqual(pipe.key_and_despill(raw, original).getpixel((20, 14)), (240, 40, 175, 255))

    def test_narrow_key_preserves_pink_and_raw_three_pixel_despill(self):
        raw = Image.new('RGBA', (16, 8), (70, 35, 60, 255))
        raw.paste((253, 1, 252, 255), (0, 0, 4, 8))
        for x, color in [(4, (220, 8, 215, 255)), (5, (125, 30, 120, 255)),
                         (7, (90, 25, 85, 255)), (8, (90, 25, 85, 255))]:
            raw.putpixel((x, 0), color)
        # 两类正常粉色都紧挨幕布；内部紫色不应因整图去色而变灰。
        pinks = [(248, 130, 218, 255), (240, 40, 175, 255), (205, 105, 195, 255)]
        for y, pink in enumerate(pinks, 1):
            raw.putpixel((4, y), pink)
            self.assertFalse(pipe.magenta(pink))
        raw.putpixel((4, 4), (103, 35, 146, 255))
        original = Image.new('RGBA', raw.size)
        original.putpixel((4, 5), (210, 20, 210, 255))
        raw.putpixel((4, 5), (212, 22, 212, 255))
        result = pipe.key_and_despill(raw, original)
        self.assertEqual(result.getpixel((3, 0)), (0, 0, 0, 0))
        self.assertEqual(result.getpixel((4, 0)), (0, 0, 0, 0))
        self.assertEqual(result.getpixel((5, 0)), (35, 30, 30, 255))
        self.assertEqual(result.getpixel((7, 0)), (30, 25, 25, 255))
        self.assertEqual(result.getpixel((8, 0)), raw.getpixel((8, 0)))
        self.assertEqual(result.getpixel((4, 4)), (35, 35, 78, 255))
        self.assertEqual(result.getpixel((4, 5)), (212, 22, 212, 255))
        for y, pink in enumerate(pinks, 1):
            self.assertEqual(result.getpixel((4, y)), pink)

    def test_box_ignores_transparent_rgb_and_keeps_thin_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = Image.new('RGBA', (2, 1), (40, 30, 20, 255))
            original.save(root / 'original.png')
            raw = Image.new('RGBA', (4, 2), (253, 1, 252, 255))
            raw.putpixel((0, 0), (40, 30, 20, 255))
            raw.putpixel((0, 1), (40, 30, 20, 255))
            raw.putpixel((1, 1), (255, 0, 255, 0))
            raw.putpixel((2, 0), (125, 30, 120, 255))
            raw.putpixel((2, 1), (125, 30, 120, 255))
            raw.save(root / 'raw.png')
            with patch.object(pipe, 'crop_band', return_value=raw):
                result = pipe.convert(root / 'raw.png', root / 'original.png', [2, 1], near=True)
            for point, expected in [((0, 0), (40, 30, 20)), ((1, 0), (35, 30, 30))]:
                pixel = result.getpixel(point)
                self.assertEqual(pixel[3], 255)
                self.assertLessEqual(max(abs(a - b) for a, b in zip(pixel[:3], expected)), 2)

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
