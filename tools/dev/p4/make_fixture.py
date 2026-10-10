import sys
sys.dont_write_bytecode = True
# 包 4 自测用的数据包（格式照技术约定 §3.1–§3.6）。包 6 的 tools\dev\fixture.py 出来以后可以换掉。
# 产物：tools\dev\p4\_fixture\data_meta.js、img_core.js、img_bg_fixture.js（只给 world_demo.html 用）。
# 用法：PYTHONDONTWRITEBYTECODE=1 python -B tools\dev\p4\make_fixture.py
# 只读：角色图集\、源码\（import engine.bg_asia 取背景层；不写任何受保护目录）。
import base64
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
JOJO = os.path.normpath(os.path.join(GAME, '..'))
SRC = os.path.join(JOJO, '源码')
ATLAS = os.path.join(JOJO, '角色图集')
OUT = os.path.join(HERE, '_fixture')

sys.path.insert(0, SRC)
from PIL import Image, ImageDraw  # noqa: E402

IMG_CORE = {}
IMG_BG = {}


def png_uri(im):
    b = io.BytesIO()
    im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode('ascii')


def reg(key, im, bg=False):
    (IMG_BG if bg else IMG_CORE)[key] = png_uri(im)
    return key


# ------------------------------------------------------------------ amap / bodyW（包 7A 的 tools\art\amap.py 有就用它）
AMAP_DEFAULT = {   # 技术约定 §3.14 A / B 的最少条目（指向还没画的真名时，atlas.js 会往下走回退）
    'jotaro': {'cmd': 'point', 'cmd2': 'point', 'cmd_hold': 'point', 'guard': 'guard', 'dodge': 'dodge',
               'down': 'down', 'hurt': 'hurt', 'special': 'pose', 'win': 'pose', 'talk': 'idle'},
    'starplat': {'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'upper', 'rush': 'rush', 'block': 'block',
                 'hurt': 'hurt', 'special': 'rush'},
    'kakyoin': {'cmd': 'cast', 'cmd2': 'cast', 'cmd_hold': 'cast', 'special': 'cast', 'guard': 'guard',
                'dodge': 'dodge', 'hurt': 'hurt', 'down': 'down'},
    'hiero': {'punch': 'cast', 'punch2': 'cast', 'rush': 'cast', 'special': 'cast', 'punch_heavy': 'whip',
              'block': 'block', 'hurt': 'hurt'},
    'avdol': {'cmd': 'cast', 'cmd2': 'cast', 'cmd_hold': 'cast', 'special': 'cast', 'win': 'yes', 'guard': 'guard',
              'dodge': 'dodge', 'hurt': 'hurt', 'down': 'down'},
    'magred': {'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'cast', 'rush': 'cast', 'special': 'cast',
               'block': 'block', 'hurt': 'hurt'},
    'polnareff': {'cmd': 'fight', 'cmd2': 'fight', 'down': 'down', 'hurt': 'hurt'},
    'chariot': {'punch': 'thrust', 'punch2': 'thrust', 'punch_heavy': 'thrust', 'rush': 'thrust', 'attack': 'thrust',
                'slash': 'slash', 'block': 'parry', 'hurt': 'hurt', 'bare_idle': 'bare_idle',
                'bare_punch': 'bare_thrust', 'bare_punch2': 'bare_thrust', 'bare_punch_heavy': 'bare_thrust',
                'bare_rush': 'bare_thrust', 'bare_attack': 'bare_thrust', 'bare_block': 'bare_idle'},
    'towergray': {'idle': 'fly', 'attack': 'needle'},
    'joseph': {'cmd': 'point', 'cmd2': 'point', 'down': {'a': 'lie', 'flip': True}},
}
BODYW_DEFAULT = {'jotaro': 7, 'joseph': 7, 'avdol': 7, 'kakyoin': 6, 'polnareff': 6, 'iggy': 5}


def load_amap():
    p = os.path.join(GAME, 'tools', 'art', 'amap.py')
    if os.path.exists(p):
        try:
            sys.path.insert(0, os.path.dirname(p))
            import amap  # noqa
            print('[fixture] 用包 7A 的 tools\\art\\amap.py')
            return dict(getattr(amap, 'AMAP', {})) or AMAP_DEFAULT, dict(getattr(amap, 'BODYW', {})) or BODYW_DEFAULT
        except Exception as e:  # noqa
            print('[fixture] amap.py 读不了，用默认表：', e)
    return AMAP_DEFAULT, BODYW_DEFAULT


SCENE_HEADS = {
    's04_kak_evil': ('kakyoin', 'evil'), 's04_kak_face': ('kakyoin', 'faint'),
    's05_avdol_grave': ('avdol', 'grave'), 's05_joseph_grave': ('joseph', 'grave'),
    's05_jotaro_talk': ('jotaro', 'glare'), 's12_telence_shock': ('telence', 'shock'),
    's14_face': ('polnareff', 'shock_big'), 's15_kak_look': ('kakyoin', 'weak'),
    's15_kak_rest': ('kakyoin', 'rest'), 's15_kak_smile': ('kakyoin', 'weak_smile'),
    's18_final2_dio_shock': ('dio', 'shock'), 's18_final2_dio_shock_tall': ('dio', 'shock_tall'),
    's18_final2_dio_smug_tall': ('dio', 'smug_tall'), 's19_jp_closed': ('joseph', 'closed_tall'),
    's19_jp_evil': ('joseph', 'evil_tall'), 's19_jp_open': ('joseph', 'open_tall'),
    's20_jotaro_smile': ('jotaro', 'smile'),
}


def load_stands():
    p = os.path.join(GAME, 'tools', 'registry', 'stands.json')
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    raise SystemExit('缺 tools\\registry\\stands.json')


def build_chars(stands):
    amap, bodyw = load_amap()
    chars = {}
    scene_cat = json.load(open(os.path.join(ATLAS, '场景专用', '场景专用目录.json'), encoding='utf-8'))
    scene_by_id = {s['id']: s for s in scene_cat['sprites']}
    for cid in sorted(os.listdir(ATLAS)):
        jp = os.path.join(ATLAS, cid, cid + '.json')
        if not os.path.exists(jp):
            continue
        d = json.load(open(jp, encoding='utf-8'))
        if 'cell' not in d:
            continue
        im = Image.open(os.path.join(ATLAS, cid, d['image'])).convert('RGBA')
        reg('chars/' + cid, im)
        anims = {k: {'row': v['row'], 'frames': v['frames'], 'fps': v.get('fps', 6), 'kind': v.get('kind', 'loop')}
                 for k, v in d['animations'].items()}
        cw, ch = d['cell']
        px, py = d['pivot']
        heads, alias, hsize = {}, {}, {}
        for e in d.get('expressions', []):
            keys = []
            for i, f in enumerate(e['files']):
                hi = Image.open(os.path.join(ATLAS, cid, f)).convert('RGBA')
                keys.append(reg('heads/%s/%s_%d' % (cid, e['emotion'], i), hi))
                if hi.size != (32, 32):
                    hsize[e['emotion']] = list(hi.size)
            heads[e['emotion']] = keys
            alias[e['id']] = e['emotion']
        for sid, (hc, emo) in SCENE_HEADS.items():
            if hc != cid or sid not in scene_by_id:
                continue
            s = scene_by_id[sid]
            sim = Image.open(os.path.join(ATLAS, '场景专用', s['file'])).convert('RGBA')
            fw, fh = s['size']
            keys = []
            for i in range(s['frames']):
                keys.append(reg('heads/%s/%s_%d' % (cid, emo, i), sim.crop((i * fw, 0, (i + 1) * fw, fh))))
            heads[emo] = keys
            alias[sid] = emo
            if (fw, fh) != (32, 32):
                hsize[emo] = [fw, fh]
        # top / bodyW：idle 第 0 帧（没有 idle 用第一个动作）
        a0 = anims.get('idle') or list(anims.values())[0]
        cell = im.crop((0, a0['row'] * ch, cw, a0['row'] * ch + ch))
        bb = cell.getbbox() or (0, 0, cw, ch)
        top = py - bb[1]
        bw = bodyw.get(cid) or max(3, round((bb[2] - bb[0]) * 0.3))
        kind = 'stand' if cid in stands else 'char'
        chars[cid] = {'name': d.get('name', cid), 'image': 'chars/' + cid, 'cell': [cw, ch], 'pivot': [px, py],
                      'animations': anims, 'aliases': d.get('aliases') or {}, 'heads': heads, 'headAlias': alias,
                      'headSize': hsize, 'amap': amap.get(cid, {}), 'top': top, 'bodyW': bw, 'kind': kind}
    return chars


def build_props():
    props = {}
    pd = json.load(open(os.path.join(ATLAS, '道具', '道具目录.json'), encoding='utf-8'))
    for p in pd['sprites']:
        im = Image.open(os.path.join(ATLAS, '道具', p['file'])).convert('RGBA')
        reg('props/' + p['id'], im)
        props[p['id']] = {'image': 'props/' + p['id'], 'frames': p['frames'], 'size': p['size'], 'pivot': p['pivot'],
                          'fps': p.get('fps', 1), 'kind': p.get('kind', 'static')}
    # 自测用的“新道具”（包 7A 没交之前顶一下）：jail_pipe 2 帧（完好 / 爆开）
    pnew = os.path.join(GAME, 'assets', 'props_new', 'props_new.json')
    if os.path.exists(pnew):
        for p in json.load(open(pnew, encoding='utf-8')).get('props', []):
            im = Image.open(os.path.join(os.path.dirname(pnew), p['file'])).convert('RGBA')
            reg('props/' + p['id'], im)
            props[p['id']] = {'image': 'props/' + p['id'], 'frames': p['frames'], 'size': p['size'],
                              'pivot': p['pivot'], 'fps': p.get('fps', 0), 'kind': p.get('kind', 'static'),
                              'isNew': True}
    if 'jail_pipe' not in props:
        im = Image.new('RGBA', (32, 48), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for f in range(2):
            ox = f * 16
            if f == 0:
                d.rectangle((ox + 5, 0, ox + 10, 47), fill=(120, 120, 130, 255), outline=(40, 40, 50, 255))
                d.line((ox + 7, 2, ox + 7, 45), fill=(170, 170, 180, 255))
            else:
                d.rectangle((ox + 5, 0, ox + 10, 20), fill=(120, 120, 130, 255), outline=(40, 40, 50, 255))
                d.rectangle((ox + 5, 30, ox + 10, 47), fill=(120, 120, 130, 255), outline=(40, 40, 50, 255))
                d.polygon([(ox + 2, 22), (ox + 14, 21), (ox + 12, 29), (ox + 3, 28)], fill=(90, 160, 230, 255))
        reg('props/jail_pipe', im)
        props['jail_pipe'] = {'image': 'props/jail_pipe', 'frames': 2, 'size': [16, 48], 'pivot': [8, 48], 'fps': 0,
                              'kind': 'static', 'isNew': True}
    scene = {}
    sc = json.load(open(os.path.join(ATLAS, '场景专用', '场景专用目录.json'), encoding='utf-8'))
    for s in sc['sprites']:
        im = Image.open(os.path.join(ATLAS, '场景专用', s['file'])).convert('RGBA')
        reg('scene/' + s['id'], im)
        scene[s['id']] = {'image': 'scene/' + s['id'], 'frames': s['frames'], 'size': s['size'], 'pivot': s['pivot'],
                          'fps': s.get('fps', 1), 'kind': s.get('kind', 'static'), 'character': s.get('character'),
                          'category': s.get('category'), 'scene': s.get('scene')}
    return props, scene


HEROES = {
    'jotaro': ('空条承太郎', '承太郎', 'starplat', '#3a4a9a', 440),
    'joseph': ('乔瑟夫·乔斯达', '乔瑟夫', 'hermit', '#6a8a3a', 520),
    'avdol': ('穆罕默德·阿布德尔', '阿布德尔', 'magred', '#c0402a', 400),
    'kakyoin': ('花京院典明', '花京院', 'hiero', '#2a9a5a', 560),
    'polnareff': ('让·皮埃尔·波鲁纳雷夫', '波鲁纳雷夫', 'chariot', '#6a7ab0', 620),
    'iggy': ('伊奇', '伊奇', 'fool', '#707070', 900),
}


# ------------------------------------------------------------------ 背景（只读 import 原工程）
def build_bg():
    from engine import bg_asia as A
    from engine.core import W, H
    bg = {}

    # 香港夜街：天空 static + far/mid/near wrap + 17 块亮霓虹（世界坐标）+ 倒影
    sky, far, mid, near = A._hk_layers()
    reg('bg/hongkong_night/sky', sky, True)
    reg('bg/hongkong_night/far', far, True)
    reg('bg/hongkong_night/mid', mid, True)
    reg('bg/hongkong_night/near', near, True)
    signs = []
    comp = Image.new('RGBA', (A._HK_W, H), (0, 0, 0, 255))
    for x0 in range(0, A._HK_W, W):
        comp.alpha_composite(sky.crop((0, 0, min(W, A._HK_W - x0), H)), (x0, 0))
    comp.alpha_composite(far)
    comp.alpha_composite(mid)
    comp.alpha_composite(near)
    for i, (sx, sy, kind, n, ci, sd, fl) in enumerate(A._HK_SIGNS):
        im = A._neon_sign(kind, n, ci, sd, True)
        pad = 7 if kind in ('V', 'H') else 5
        key = reg('bg/hongkong_night/neon%02d' % i, im, True)
        signs.append({'image': key, 'x': sx - pad, 'y': sy - pad, 'flick': bool(fl)})
        comp.alpha_composite(im, (max(0, sx - pad), max(0, sy - pad)))
    reg('bg/hongkong_night/reflect_src', comp, True)
    bg['hongkong_night'] = {
        'pack': 'fixture', 'w': 960, 'ground': 154, 'walk': [150, 176],
        'anchors': {'shopwindow': [400, 108, 452, 150]},
        'layers': [
            {'type': 'static', 'image': 'bg/hongkong_night/sky'},
            {'type': 'wrap', 'image': 'bg/hongkong_night/far', 'period': 640, 'k': 0.25, 'vx': 0.5},
            {'type': 'wrap', 'image': 'bg/hongkong_night/mid', 'period': 640, 'k': 0.6},
            {'type': 'wrap', 'image': 'bg/hongkong_night/near', 'period': 640, 'k': 1},
            {'type': 'neon', 'signs': signs, 'k': 1, 'period': 640},
            {'type': 'reflect', 'image': 'bg/hongkong_night/reflect_src', 'y': 152, 'n': 27, 'a0': 0.62,
             'a1': 0.27, 'period': 640, 'k': 1},
        ],
        'fg': [],
    }

    # 拘留所：底图 + 前景铁栏 6 张（pick，key bend）
    reg('bg/jail_cell/base', A._jail_static(), True)
    bars = []
    for i, bq in enumerate([0, 10, 20, 30, 40, 50]):
        bars.append(reg('bg/jail_cell/bars%d' % i, A._bars_layer(bq, 6, 314, 182, 0, 146), True))
    bg['jail_cell'] = {'pack': 'fixture', 'w': 320, 'ground': 166, 'walk': [124, 134],
                       'anchors': {'bunk': [148, 97]},
                       'layers': [{'type': 'static', 'image': 'bg/jail_cell/base'}],
                       'fg': [{'type': 'pick', 'images': bars, 'key': 'bend'}]}

    # 校门：两层 pano + 花瓣
    sfar, snear = A._school_layers()
    reg('bg/school_gate/far', sfar, True)
    reg('bg/school_gate/near', snear, True)
    bg['school_gate'] = {'pack': 'fixture', 'w': 480, 'ground': 150, 'walk': [146, 170], 'anchors': {},
                         'layers': [{'type': 'pano', 'image': 'bg/school_gate/far', 'k': 0.5},
                                    {'type': 'pano', 'image': 'bg/school_gate/near', 'k': 1},
                                    {'type': 'petals', 'n': 26, 'colors': ['#ffd6e4', '#f4a0be'], 'seed': 0,
                                     'y0': -6, 'y1': 184, 'vx': -70, 'k': 0.2}],
                         'fg': []}

    # 空条家（单屏）：static
    reg('bg/kujo_house_day/base', A._kujo_static('day'), True)
    bg['kujo_house_day'] = {'pack': 'fixture', 'w': 320, 'ground': 166, 'walk': [148, 172], 'anchors': {},
                            'layers': [{'type': 'static', 'image': 'bg/kujo_house_day/base'}], 'fg': []}

    # 图层类型自测图：strip / image(flicker) / glow / stars / clouds / tint(key) / wrap(h) / pick(values)
    base = Image.new('RGBA', (W, H), (30, 34, 60, 255))
    dd = ImageDraw.Draw(base)
    dd.rectangle((0, 150, W, H), fill=(60, 50, 44, 255))
    for x in range(0, W, 16):
        dd.line((x, 150, x, H), fill=(70, 60, 52, 255))
    reg('bg/p4_types/base', base, True)
    strip = Image.new('RGBA', (16 * 4, 16), (0, 0, 0, 0))
    ds = ImageDraw.Draw(strip)
    for f in range(4):
        ds.ellipse((f * 16 + 2 + f, 2, f * 16 + 10 + f, 10), fill=(255, 220, 80, 255))
    reg('bg/p4_types/strip', strip, True)
    lamp = Image.new('RGBA', (8, 20), (0, 0, 0, 0))
    ImageDraw.Draw(lamp).rectangle((2, 0, 5, 19), fill=(200, 200, 210, 255))
    reg('bg/p4_types/lamp', lamp, True)
    glow = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r, a in ((19, 30), (14, 60), (9, 110), (4, 180)):
        gd.ellipse((20 - r, 20 - r, 20 + r, 20 + r), fill=(255, 190, 90, a))
    reg('bg/p4_types/glow', glow, True)
    cloud = Image.new('RGBA', (40, 12), (0, 0, 0, 0))
    ImageDraw.Draw(cloud).ellipse((0, 0, 39, 11), fill=(200, 210, 240, 255))
    reg('bg/p4_types/cloud', cloud, True)
    band = Image.new('RGBA', (200, 30), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for x in range(0, 200, 20):
        bd.rectangle((x, 0, x + 12, 29), fill=(90, 70, 130, 255))
    reg('bg/p4_types/band', band, True)
    pk = []
    for i, c in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
        im = Image.new('RGBA', (12, 12), c + (255,))
        pk.append(reg('bg/p4_types/pick%d' % i, im, True))
    bg['p4_types'] = {'pack': 'fixture', 'w': 640, 'ground': 160, 'walk': [152, 176], 'anchors': {},
                      'layers': [
                          {'type': 'static', 'image': 'bg/p4_types/base'},
                          {'type': 'stars', 'list': [[20, 10, 3, 0, 1, '#ffffff'], [60, 22, 2, 1, 0, '#ffe0a0'],
                                                     [140, 14, 4, 2, 1, '#a0c0ff'], [250, 30, 2.5, 3, 0, '#ffffff']]},
                          {'type': 'clouds', 'span': 520, 'clouds': [{'image': 'bg/p4_types/cloud', 'x0': 0, 'y': 40,
                                                                      'vx': 6, 'k': 0.1},
                                                                     {'image': 'bg/p4_types/cloud', 'x0': 260,
                                                                      'y': 56, 'vx': 9, 'k': 0.2}]},
                          {'type': 'wrap', 'image': 'bg/p4_types/band', 'period': 200, 'k': 0.5, 'y': 100, 'h': 30},
                          {'type': 'strip', 'image': 'bg/p4_types/strip', 'x': 100, 'y': 130, 'w': 16, 'h': 16,
                           'n': 4, 'fps': 6},
                          {'type': 'image', 'image': 'bg/p4_types/lamp', 'x': 200, 'y': 130, 'flicker': 0.4},
                          {'type': 'glow', 'image': 'bg/p4_types/glow', 'x': 184, 'y': 110, 'flicker': True},
                          {'type': 'pick', 'images': pk, 'key': 'p', 'values': [0, 0.3, 1], 'x': 300, 'y': 120},
                          {'type': 'tint', 'color': '#203060', 'alpha': 0.5, 'key': 'night'},
                      ],
                      'fg': [{'type': 'image', 'image': 'bg/p4_types/lamp', 'x': 420, 'y': 150}]}
    return bg


def main():
    os.makedirs(OUT, exist_ok=True)
    stands = load_stands()
    chars = build_chars(stands)
    props, scene = build_props()
    bg = build_bg()
    heroes = {c: {'cid': c, 'cn': v[0], 'short': v[1], 'stand': v[2], 'nameColor': v[3], 'blipHz': v[4],
                  'grunt': 'grunt_' + c} for c, v in HEROES.items()}
    meta = {
        'v': 1, 'built': 'p4-fixture', 'img': {}, 'packsLoaded': {}, 'packKeys': {},
        'packs': {'core': {'file': 'data/img_core.js'}, 'bg_fixture': {'file': 'img_bg_fixture.js', 'bg': list(bg)}},
        'chars': chars, 'props': props, 'scene': scene, 'heroes': heroes,
        'speakers': {'holly': {'short': '荷莉', 'nameColor': '#d0608a', 'blipHz': 800}},
        'stands': stands, 'bg': bg, 'ui': {}, 'font': {}, 'fxtex': {}, 'audio': {'music': {}, 'sfx': {}}, 'video': {},
    }
    with open(os.path.join(OUT, 'data_meta.js'), 'w', encoding='utf-8') as f:
        f.write('window.GAME_DATA = ' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + ';\n')

    def img_file(name, pack, table):
        with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
            f.write('(function(){var D=window.GAME_DATA;Object.assign(D.img,')
            f.write(json.dumps(table, separators=(',', ':')))
            f.write(');D.packKeys[%s]=%s;D.packsLoaded[%s]=true;})();\n'
                    % (json.dumps(pack), json.dumps(list(table)), json.dumps(pack)))
    img_file('img_core.js', 'core', IMG_CORE)
    img_file('img_bg_fixture.js', 'bg_fixture', IMG_BG)
    for n in ('data_meta.js', 'img_core.js', 'img_bg_fixture.js'):
        print('%-18s %8.1f KB' % (n, os.path.getsize(os.path.join(OUT, n)) / 1024))
    print('chars %d, props %d, scene %d, bg %d' % (len(chars), len(props), len(scene), len(bg)))


if __name__ == '__main__':
    main()
