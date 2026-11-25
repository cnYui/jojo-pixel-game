"""回归整组撤回、开关保护、画布换算和 near 紫红物件保护。"""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bg_gpt_p4 as pipe


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

    def test_group_rollback_and_protected_variant(self):
        out_root = HERE / '_out'
        out_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=out_root) as tmp:
            root = Path(tmp)
            assets, src, output = root / 'assets', root / 'src', root / 'assets/bg_gpt'
            (assets / '_meta').mkdir(parents=True)
            (assets / 'bg/demo').mkdir(parents=True)
            (src / 'raw').mkdir(parents=True)
            spec = {'demo': {'layers': [dict(type='pano', image='bg/demo/far'),
                                       dict(type='pano', image='bg/demo/near'),
                                       dict(type='pano', image='bg/demo/lit', key='lamp')]}}
            (assets / '_meta/bg.json').write_text(json.dumps(spec), encoding='utf-8')
            jobs = [dict(name=f'demo__{name}', key='demo', image=f'bg/demo/{name}',
                         size=[16, 8], kind=kind) for name, kind in
                    [('far', 'far'), ('near', 'near'), ('lit', 'variant')]]
            (src / 'jobs.json').write_text(json.dumps(jobs), encoding='utf-8')
            near = Image.new('RGBA', (16, 8))
            near.paste((210, 20, 210, 255), (4, 2, 12, 7))
            near.save(assets / 'bg/demo/near.png')
            for name in ['far', 'lit']:
                Image.new('RGB', (16, 8), '#123456').save(assets / f'bg/demo/{name}.png')
            original_bytes = {p: p.read_bytes() for p in (assets / 'bg/demo').glob('*.png')}
            raw = Image.new('RGB', (768, 512), (255, 0, 255))
            for name in ['far', 'near']:
                raw.save(src / f'raw/demo__{name}.png')
            near_raw = raw.copy()
            foreground = near.resize((768, 384), Image.Resampling.NEAREST)
            near_raw.paste(foreground, (0, 64), foreground)
            near_raw.save(src / 'raw/demo__near.png')
            self.assertEqual(pipe.run(src, assets=assets, output=output)['enabled'], [])
            preview = pipe.run(src, partial=True, assets=assets, output=output)
            self.assertEqual(preview['enabled'], ['demo'])
            raw.save(src / 'raw/demo__lit.png')
            report = pipe.run(src, assets=assets, output=output)
            self.assertEqual(report['enabled'], ['demo'])
            self.assertFalse((output / 'bg/demo/lit.png').exists())
            self.assertIn('bg/demo/lit', report['retained_overlays']['demo'])
            with Image.open(output / 'bg/demo/near.png') as image:
                self.assertEqual(image.getpixel((0, 0))[3], 0)
                self.assertEqual(image.getpixel((8, 4))[3], 255)
                self.assertEqual(image.getpixel((8, 4))[:3], (210, 20, 210))
                self.assertEqual(image.getpixel((4, 3)), (210, 20, 210, 255))
                self.assertLessEqual(len(set(image.convert('RGB').getdata())), 97)
                self.assertEqual(set(image.getchannel('A').getdata()), {0, 255})
            snapshot = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
            pipe.run(src, assets=assets, output=output)
            self.assertEqual(snapshot, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})
            # 用夹具删除 raw，不改动仓库外用户的只读输入。
            (src / 'raw/demo__lit.png').unlink()
            self.assertEqual(pipe.run(src, assets=assets, output=output)['enabled'], [])
            self.assertEqual(list(output.rglob('*.png')), [])
            (src / 'raw/demo__lit.png').write_bytes(b'incomplete PNG')
            bad = pipe.run(src, assets=assets, output=output)
            self.assertIn('demo', bad['errors'])
            self.assertEqual(list(output.rglob('*.png')), [])
            self.assertTrue(all(p.read_bytes() == data for p, data in original_bytes.items()))


if __name__ == '__main__':
    unittest.main()
