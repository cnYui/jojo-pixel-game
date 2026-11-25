# 验证实际图集边界和只读复用结果，避免仅靠浏览器走动掩盖数据缺项。
import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from p5_paths import REPO, P5, GAME, BACKGROUNDS
from build_p5 import read_gd, read_pack, merge
from p5_font import charset


def main():
    data = GAME / 'data'
    gd = read_gd(data / 'data_meta.js')
    images = {}
    for path in data.glob('img_*.js'):
        images.update(read_pack(path))
    checks = []
    for cid, char in gd['chars'].items():
        with Image.open(io.BytesIO(base64.b64decode(images[char['image']].split(',', 1)[1]))) as image:
            cw, ch = char['cell']
            for name, anim in char['animations'].items():
                assert anim['row'] >= 0 and anim['frames'] > 0, (cid, name)
                assert (anim['row'] + 1) * ch <= image.height, (cid, name, '图集行越界')
                assert anim['frames'] * cw <= image.width, (cid, name, '图集列越界')
        for name, target in char.get('amap', {}).items():
            assert (target if isinstance(target, str) else target['a']) in char['animations'], (cid, name, target)
        for frames in char.get('heads', {}).values():
            for key in frames:
                assert key in images, key
        checks.append(cid + ' 图集与头像')
    for map_id, key, width, _, pack in BACKGROUNDS:
        meta = gd['bg'][key]
        assert meta['w'] == width and meta['walk'] == [142, 176] and meta['ground'] == 150
        assert meta['pack'] == pack
        with Image.open(P5 / f'assets/bg/{key}/base.png') as image:
            assert image.size == (width, 180)
            assert len(image.convert('RGB').getcolors(maxcolors=65) or []) in range(1, 65)
        checks.append(map_id + ' 背景规格')
    p4 = {}
    for path in sorted((REPO / '第四部/assets/_meta').glob('chars*.json')):
        p4 = merge(p4, json.loads(path.read_text(encoding='utf-8')))
    for cid in ('koichi', 'jotaro4', 'echoes3'):
        original = p4['chars'][cid]
        actual = gd['chars'][cid]
        assert actual['cell'] == original['cell'] and actual['animations'] == original['animations']
        for key in [original['image'], *(k for frames in original['heads'].values() for k in frames)]:
            assert base64.b64decode(images[key].split(',', 1)[1]) == (REPO / '第四部/assets' / (key + '.png')).read_bytes()
    checks.append('第四部3个复用角色的图与头像逐字节一致')
    for size in ('12', '16'):
        assert set(charset()) <= gd['font'][size]['glyphs'].keys()
    checks.append('字表覆盖当前代码与开发脚本')
    assert 'title_song' not in gd['audio']['music']
    assert sorted(p.stem for p in (data / 'music').glob('*.js')) == sorted(gd['audio']['music'])
    checks.append('用户音频排除')
    result = dict(ok=True, checks=checks, images=len(images), chars=len(gd['chars']), backgrounds=len(gd['bg']))
    out = Path(__file__).resolve().parent / '_out'
    out.mkdir(exist_ok=True)
    (out / 'contract.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'PASS：{len(checks)}项资源合同检查')


if __name__ == '__main__':
    main()
