# 对任意源图裁切和可选补画模块做独立验收，测试产物均留在被忽略的_out内。
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bg_p5 import crop_source
import export_p5 as export
import cast5_heroes


def main():
    checks = []
    source = Image.new('RGB', (320, 1000), 'blue')
    draw = ImageDraw.Draw(source)
    draw.rectangle((0, 0, 319, 199), fill='red')
    draw.rectangle((0, 800, 319, 999), fill='green')
    center = crop_source(source, 320)
    down = crop_source(source, 320, 500)
    clamped = crop_source(source, 320, 10000)
    assert center.size == (320, 180) and center.convert('RGB').getpixel((0, 0)) == (0, 0, 255)
    assert down.convert('RGB').getpixel((0, 0)) == (0, 128, 0)
    assert down.tobytes() == clamped.tobytes()
    checks.append('源图纵向裁切偏移和越界夹紧')
    noise = Image.effect_noise((1501, 777), 60).convert('RGB')
    result = crop_source(noise, 960, sharpen=True)
    assert result.size == (960, 180) and len(result.getcolors()) <= 64
    checks.append('任意尺寸源图与锐化后64色限制')
    out = Path(__file__).resolve().parent / '_out'
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out, prefix='optional-') as temporary:
        home = Path(temporary)
        art = home / 'tools/art'
        art.mkdir(parents=True)
        for name in ('cast5_extra', 'props5'):
            (art / (name + '.py')).touch()
        extra = SimpleNamespace(CAST={'luca': ('补画卢卡接口', None)}, build=lambda cid: cast5_heroes.build('giorno'))
        props = SimpleNamespace(PROPS={'frog': lambda: export.px.Cv(11, 7, '#12c850')})
        assets = home / 'assets'
        with patch.multiple(export, P5=home, ASSETS=assets, META=assets / '_meta'), \
                patch.object(export.portrait, 'ASSETS', str(assets)), \
                patch.dict(sys.modules, {'cast5_extra': extra, 'props5': props}), \
                contextlib.redirect_stdout(io.StringIO()):
            export.main()
        cm = json.loads((assets / '_meta/chars.json').read_text(encoding='utf-8'))
        pm = json.loads((assets / '_meta/props.json').read_text(encoding='utf-8'))
        assert cm['chars']['luca']['name'] == cast5_heroes.build('giorno').name
        assert not cm['chars']['luca'].get('placeholder')
        assert cm['chars']['police']['placeholder']
        assert not pm['props']['frog']['placeholder'] and pm['props']['frog']['size'] == [11, 7]
        assert pm['props']['suitcase']['placeholder']
        assert (assets / 'heads/luca/normal_0.png').is_file()
        checks.append('补画模块自动替换真实人物及头像，未补画id仍占位')
        checks.append('props5返回px.Cv自动替换，未补画道具仍占位')
    (out / 'pipeline.json').write_text(json.dumps(dict(ok=True, checks=checks), ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'PASS：{len(checks)}项源图与补画模块验收')


if __name__ == '__main__':
    main()
