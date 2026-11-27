# 验证实际图集边界和只读复用结果，避免仅靠浏览器走动掩盖数据缺项。
import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from p5_paths import P5, GAME, BACKGROUNDS, SHARED_ART, SHARED_CAST, load_json
from build_p5 import read_gd, read_pack
from p5_font import charset
from props_p5 import TARGETS, SOURCES


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
        if key.startswith('p5_') and key != 'p5_title':
            assert not meta['placeholder'], (key, '正篇背景不能用占位图')
        with Image.open(P5 / f'assets/bg/{key}/base.png') as image:
            assert image.size == (width, 180)
            assert len(image.convert('RGB').getcolors(maxcolors=65) or []) in range(1, 65)
        checks.append(map_id + ' 背景规格')
    p4 = load_json(SHARED_ART / 'characters.json')
    for cid in SHARED_CAST:
        original = p4['chars'][cid]
        actual = gd['chars'][cid]
        assert actual['cell'] == original['cell'] and actual['animations'] == original['animations']
        for key in [original['image'], *(k for frames in original['heads'].values() for k in frames)]:
            assert base64.b64decode(images[key].split(',', 1)[1]) == (SHARED_ART / (key + '.png')).read_bytes()
    checks.append('第四部3个复用角色的图与头像逐字节一致')
    for size in ('12', '16'):
        assert set(charset()) <= gd['font'][size]['glyphs'].keys()
    checks.append('字表覆盖当前代码与开发脚本')
    assert 'title_song' not in gd['audio']['music']
    assert sorted(p.stem for p in (data / 'music').glob('*.js')) == sorted(gd['audio']['music'])
    checks.append('用户音频排除')
    for cid, size in TARGETS.items():
        meta = gd['props'][cid]
        assert meta['source'] == SOURCES[cid] and not meta['placeholder'], cid
        assert meta['size'] == list(size) and meta['pivot'] == [size[0] // 2, size[1]], cid
        raw = (P5 / 'assets' / (meta['image'] + '.png')).read_bytes()
        assert base64.b64decode(images[meta['image']].split(',', 1)[1]) == raw, cid
        with Image.open(io.BytesIO(raw)) as image:
            assert image.size == size and image.getbbox(), cid
            assert set(image.getchannel('A').getdata()) <= {0, 255}, cid
            assert len({p[:3] for p in image.getdata() if p[3]}) <= 25, cid
            assert image.getbbox()[3] == size[1], (cid, '底边未对齐')
        checks.append(cid + ' 生图优先、像素规格和运行包一致')
    for key in ('prologue', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'final'):
        chapter = gd['ui']['chapters'][key]
        assert chapter['image'] in images
        assert gd['packs']['bg_' + key]['bg'], key
        checks.append(key + ' 篇章卡及背景分包')
    chariot = gd['props']['chariot_requiem']
    with Image.open(P5 / 'assets/props/chariot_requiem.png') as image:
        assert list(image.size) == chariot['size'] and image.getbbox()[3] == chariot['pivot'][1]
        assert image.getchannel('A').getextrema() == (0, 255) and not chariot['placeholder']
    checks.append('银色战车镇魂曲透明剪影与脚底锚点')
    result = dict(ok=True, checks=checks, images=len(images), chars=len(gd['chars']), backgrounds=len(gd['bg']))
    out = Path(__file__).resolve().parent / '_out'
    out.mkdir(exist_ok=True)
    (out / 'contract.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'PASS：{len(checks)}项资源合同检查')


if __name__ == '__main__':
    main()
