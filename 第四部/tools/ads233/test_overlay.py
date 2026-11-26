"""验证副本补丁的范围、换行、漂移拒绝与 zip 注入合同；只写系统临时目录。"""
import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

import overlay


class OverlayTests(unittest.TestCase):
    def fixture(self, root, nl='\n'):
        (root / 'engine').mkdir()
        for rel in overlay.PATCHES:
            text = (overlay.SOURCE / rel).read_text(encoding='utf-8')
            (root / rel).write_bytes(text.replace('\n', nl).encode('utf-8'))

    def test_apply_newlines_and_scope(self):
        for nl in ('\n', '\r\n'):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root, nl)
                extra = root / 'engine/combat.js'
                extra.write_bytes(b'unchanged\r\n')
                overlay.apply(root)
                self.assertEqual(extra.read_bytes(), b'unchanged\r\n')
                self.assertEqual((root / 'engine/ads.js').read_bytes(), (overlay.HERE / 'ads.js').read_bytes())
                for rel, pairs in overlay.PATCHES.items():
                    patched = (root / rel).read_bytes().decode('utf-8')
                    for old, new in pairs:
                        self.assertEqual(patched.count(new.replace('\n', nl)), 1)
                        patched = patched.replace(new.replace('\n', nl), old.replace('\n', nl))
                    original = (overlay.SOURCE / rel).read_text(encoding='utf-8').replace('\n', nl)
                    self.assertEqual(patched, original)
                before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                with self.assertRaises(ValueError):
                    overlay.apply(root)
                self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_drift_is_read_only(self):
        for rel, pairs in overlay.PATCHES.items():
            for count in (0, 2):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    self.fixture(root)
                    (root / rel).write_text(pairs[0][0] * count, encoding='utf-8')
                    before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                    with self.assertRaises(ValueError):
                        overlay.apply(root)
                    self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
                    self.assertFalse((root / 'engine/ads.js').exists())
        with self.assertRaises(ValueError):
            overlay.apply(overlay.SOURCE)

    def test_sdk(self):
        for nl in ('\n', '\r\n'):
            with tempfile.TemporaryDirectory() as tmp:
                src, dst = Path(tmp) / 'in.zip', Path(tmp) / 'out.zip'
                html = '<html><head>' + nl + '<meta charset="utf-8">' + nl + '</head></html>'
                with zipfile.ZipFile(src, 'w', zipfile.ZIP_DEFLATED) as z:
                    z.comment = b'archive comment'
                    z.writestr('engine/opaque.bin', bytes(range(256)))
                    z.writestr('index.html', html)
                    z.writestr('folder/', b'')
                overlay.inject_sdk(src, dst)
                with zipfile.ZipFile(src) as a, zipfile.ZipFile(dst) as b:
                    self.assertEqual(b.namelist(), ['index.html', 'engine/opaque.bin', 'folder/'])
                    self.assertEqual(b.read('index.html').decode(), html.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + nl + overlay.SDK_TAG))
                    self.assertEqual(a.comment, b.comment)
                    for name in a.namelist():
                        if name == 'index.html':
                            continue
                        self.assertEqual(hashlib.sha256(a.read(name)).digest(), hashlib.sha256(b.read(name)).digest())
                        for field in ('date_time', 'compress_type', 'external_attr', 'extra', 'comment'):
                            self.assertEqual(getattr(a.getinfo(name), field), getattr(b.getinfo(name), field))
                with self.assertRaises(ValueError):
                    overlay.inject_sdk(dst, src)
                with self.assertRaises(ValueError):
                    overlay.inject_sdk(src, src)

    def test_sdk_bad_head(self):
        for html in ('<head></head>', '<head><meta charset="utf-8"><meta charset="utf-8"></head>', '<meta charset="utf-8">'):
            with tempfile.TemporaryDirectory() as tmp:
                src, dst = Path(tmp) / 'in.zip', Path(tmp) / 'out.zip'
                with zipfile.ZipFile(src, 'w') as z:
                    z.writestr('index.html', html)
                with self.assertRaises(ValueError):
                    overlay.inject_sdk(src, dst)
                self.assertFalse(dst.exists())


if __name__ == '__main__':
    unittest.main()
