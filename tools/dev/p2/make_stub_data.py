# -*- coding: utf-8 -*-
r"""包 2 自测用的最小数据（桩）：tools\dev\p2\_out\stub_data.js（window.GAME_DATA 的子集，格式同技术约定 §3）。

- chars：几个角色 / 替身图集（只读 角色图集\<cid>\<cid>.json + .png）→ data URI
- props：coin / knife / bat / map_plane / map_ship（只读 角色图集\道具\）
- fxtex：fx/noise0..3、fx/ankh34/38/40/44（只读 import 源码 engine.fx，算法同包 6 的 tools\fx_tex.py）
- stands：tools\registry\stands.json（包 8 的登记表，只读）
- 测试背景：源码 bg_asia 画的 jail / 香港夜街 / 虎豹别墅夜 / 世界地图（key test/bg_<名>）

包 6 的 tools\dev\fixture\ 出来以后可以换成那个；格式一样。
用法：PYTHONDONTWRITEBYTECODE=1 python tools\dev\p2\make_stub_data.py
"""
import sys
sys.dont_write_bytecode = True

import base64  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
JOJO = os.path.dirname(GAME)
SRC = os.path.join(JOJO, '源码')
ATLAS = os.path.join(JOJO, '角色图集')
OUT = os.path.join(HERE, '_out')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

CIDS = ['jotaro', 'starplat', 'theworld', 'hiero', 'chariot', 'magred', 'kakyoin', 'avdol', 'polnareff', 'towergray', 'fool']
PROPS = ['coin', 'knife', 'bat', 'map_plane', 'map_ship']
BGS = ['jail', 'hkn', 'hkg', 'map', 'gray']


def uri(im):
    b = io.BytesIO()
    im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode('ascii')


def file_uri(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('ascii')


def render_bgs():
    """测试背景（320×180）：原工程背景函数画一帧。"""
    import assets
    assets.load_all()
    from engine.core import Frame
    from engine import bg_asia
    out = {}
    jobs = {
        'jail': lambda fr: bg_asia.jail_cell(fr, scroll=0),
        'hkn': lambda fr: bg_asia.hongkong_night(fr, scroll=0),
        'hkg': lambda fr: bg_asia.hk_garden(fr, night=True),
        'map': lambda fr: bg_asia.world_map(fr),
    }
    for name, fn in jobs.items():
        fr = Frame(0.0)
        fn(fr)
        out[name] = fr.img.convert('RGBA')
    g = Image.new('RGBA', (320, 180), (70, 66, 86, 255))
    a = np.array(g)
    a[120:, :, :3] = (50, 46, 60)
    out['gray'] = Image.fromarray(a, 'RGBA')
    return out


def fxtex():
    from engine import fx as FX
    meta = dict(noise=[], ankh={}, ankhPad={}, ankhScale={})
    img = {}
    for s in range(4):
        a = FX._noise_tex(s, 64, 64)
        im = Image.fromarray(np.clip(np.round(a * 255), 0, 255).astype(np.uint8), 'L').convert('RGBA')
        img[f'fx/noise{s}'] = uri(im)
        meta['noise'].append(f'fx/noise{s}')
    for S in (34, 38, 40, 44):
        field, pad = FX._ankh_field(S)
        core, up = field[0], field[1]
        k = float(max(1.0, core.max(), up.max()))
        h, w = core.shape
        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[..., 0] = np.clip(np.round(core / k * 255), 0, 255)
        rgba[..., 1] = np.clip(np.round(up / k * 255), 0, 255)
        rgba[..., 3] = 255
        img[f'fx/ankh{S}'] = uri(Image.fromarray(rgba, 'RGBA'))
        meta['ankh'][str(S)] = f'fx/ankh{S}'
        meta['ankhPad'][str(S)] = int(pad)
        meta['ankhScale'][str(S)] = round(k, 4)
    return meta, img


def main():
    os.makedirs(OUT, exist_ok=True)
    D = dict(v=1, built='p2-stub', img={}, packsLoaded={'core': True}, packKeys={'core': []}, chars={}, props={}, scene={},
             stands={}, fxtex={}, bg={})
    for cid in CIDS:
        jp = os.path.join(ATLAS, cid, cid + '.json')
        if not os.path.exists(jp):
            print('skip', cid)
            continue
        with open(jp, encoding='utf-8') as f:
            j = json.load(f)
        key = 'chars/' + cid
        D['img'][key] = file_uri(os.path.join(ATLAS, cid, j['image']))
        D['chars'][cid] = dict(name=j.get('name', cid), image=key, cell=j['cell'], pivot=j['pivot'],
                               animations={k: dict(row=v['row'], frames=v['frames'], fps=v.get('fps', 1), kind=v.get('kind', 'loop'))
                                           for k, v in j['animations'].items()},
                               aliases=j.get('aliases', {}), kind='char')
    with open(os.path.join(ATLAS, '道具', '道具目录.json'), encoding='utf-8') as f:
        pc = json.load(f)
    for p in pc['sprites']:
        if p['id'] not in PROPS:
            continue
        key = 'props/' + p['id']
        D['img'][key] = file_uri(os.path.join(ATLAS, '道具', p['file']))
        D['props'][p['id']] = dict(image=key, frames=p['frames'], size=p['size'], pivot=p['pivot'], fps=p.get('fps', 1), kind=p.get('kind', 'static'))
    reg = os.path.join(GAME, 'tools', 'registry', 'stands.json')
    if os.path.exists(reg):
        with open(reg, encoding='utf-8') as f:
            st = json.load(f)
        D['stands'] = st.get('stands', st) if isinstance(st, dict) else {}
        for k in D['stands']:
            if k in D['chars']:
                D['chars'][k]['kind'] = 'stand'
    meta, img = fxtex()
    D['fxtex'] = meta
    D['img'].update(img)
    for name, im in render_bgs().items():
        D['img']['test/bg_' + name] = uri(im)
        im.save(os.path.join(OUT, f'bg_{name}.png'))
    D['bg']['world_map'] = dict(pack='common', w=320, anchors={})
    D['packKeys']['core'] = list(D['img'].keys())
    js = 'window.GAME_DATA = ' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + ';\n'
    with open(os.path.join(OUT, 'stub_data.js'), 'w', encoding='utf-8') as f:
        f.write(js)
    print('stub_data.js', len(js) // 1024, 'KB;', len(D['chars']), 'chars,', len(D['props']), 'props,', len(D['img']), 'images')


if __name__ == '__main__':
    main()
