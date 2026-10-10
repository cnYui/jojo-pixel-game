"""包 1 自测用的最小数据（只写进 tools\\dev\\p1\\_gen\\，不碰别人的文件）。

    python -B tools\\dev\\p1\\gen_fixture.py

产出：
  _gen/meta.js            window.GAME_DATA：audio = tools\\_meta\\audio.json（包 1 的构建结果）、一个测试图片包的登记、heroes 的 blipHz
  _gen/img_core.js        假的“常驻图片包”（2 张小图，packKeys.core）
  _gen/img_bg_p1test.js   假的“背景包”（按需 loadPack 测试用，2 张小图）
  _gen/test_page.html     测试页：index.html 原样 + 包 1 的脚本和桩（<base href="../../../../"> 指到游戏根目录，
                          所以这里写的路径都相对游戏根目录）
"""
import sys

sys.dont_write_bytecode = True

import base64  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402

from PIL import Image  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(HERE, '_gen')
AUDIO_META = os.path.join(GAME, 'tools', '_meta', 'audio.json')


def png_uri(w, h, fill):
    """fill(x, y) -> (r, g, b, a)"""
    im = Image.new('RGBA', (w, h))
    im.putdata([fill(x, y) for y in range(h) for x in range(w)])
    b = io.BytesIO()
    im.save(b, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode('ascii')


def pack_js(name, imgs):
    body = json.dumps(imgs, ensure_ascii=False, separators=(',', ':'))
    keys = json.dumps(list(imgs), ensure_ascii=False, separators=(',', ':'))
    return ('(function(){var D=window.GAME_DATA;Object.assign(D.img,' + body + ');'
            'D.packKeys[' + json.dumps(name) + ']=' + keys + ';D.packsLoaded[' + json.dumps(name) + ']=true;})();\n')


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


TEST_SCRIPTS = [
    'tools/dev/p1/_gen/meta.js', 'tools/dev/p1/_gen/img_core.js', 'data/sfx.js',
    'engine/core.js', 'engine/res.js', 'engine/input.js', 'engine/audio.js',
    'tools/dev/p1/stubs.js', 'engine/touch.js', 'tools/dev/p1/boot.js',
]


def test_page():
    """测试页 = index.html 原样（画布、触屏 DOM / CSS 都是真的），只把脚本列表换成 包1 的文件 + 桩，并加 <base> 指到游戏根目录。"""
    with open(os.path.join(GAME, 'index.html'), encoding='utf-8') as f:
        html = f.read()
    head, sep, _rest = html.partition('<!-- 脚本顺序')
    if not sep:
        raise SystemExit('gen_fixture: index.html 里找不到脚本列表的注释')
    html = head.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="../../../../">', 1)
    html = html.replace('<title>', '<title>[包1自测] ', 1)
    return html + '\n'.join(f'<script src="{s}"></script>' for s in TEST_SCRIPTS) + '\n</body>\n</html>\n'


def main():
    with open(AUDIO_META, encoding='utf-8') as f:
        audio = json.load(f)
    meta = {
        'v': 1, 'built': 'p1-fixture', 'img': {}, 'packsLoaded': {}, 'packKeys': {},
        'packs': {'core': {'file': 'tools/dev/p1/_gen/img_core.js'},
                  'bg_p1test': {'file': 'tools/dev/p1/_gen/img_bg_p1test.js', 'bg': ['p1test']}},
        'heroes': {'jotaro': {'cid': 'jotaro', 'short': '承太郎', 'blipHz': 440},
                   'kakyoin': {'cid': 'kakyoin', 'short': '花京院', 'blipHz': 560}},
        'speakers': {'holly': {'short': '荷莉', 'blipHz': 800}},
        'audio': audio,
    }
    write(os.path.join(OUT, 'meta.js'), 'window.GAME_DATA=' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + ';\n')
    core = {
        'test/core_red': png_uri(4, 4, lambda x, y: (255, 0, 0, 255)),
        'test/core_grad': png_uri(8, 2, lambda x, y: (x * 32, y * 255, 100, 255 if x < 7 else 0)),
    }
    write(os.path.join(OUT, 'img_core.js'), pack_js('core', core))
    bg = {
        'bg/p1test/a': png_uri(6, 3, lambda x, y: (10, 200, 30, 255)),
        'bg/p1test/b': png_uri(3, 6, lambda x, y: (0, 0, 255, 128)),
    }
    write(os.path.join(OUT, 'img_bg_p1test.js'), pack_js('bg_p1test', bg))
    write(os.path.join(OUT, 'test_page.html'), test_page())
    print('gen_fixture: 写好', os.path.relpath(OUT, GAME), '（音效', len(audio['sfx']), '个、音乐', len(audio['music']), '首）')


if __name__ == '__main__':
    main()
