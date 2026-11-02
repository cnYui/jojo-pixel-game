# 第四部的数据构建：把 第四部/assets 里的图和元数据，加上第三部已经构建好的通用部件（特效贴图、拟声字、VS 标、白金之星、音效），
#   合成 第四部/游戏/data/ 下的运行时文件（格式和第三部 data/ 完全一样：window.GAME_DATA + 按包分的 img_*.js）。
#   用法：python3 第四部/tools/build_p4.py        （先重烘字库，再合成）
#         python3 第四部/tools/build_p4.py --no-font
import base64
import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'art'))
import p4lib as L  # noqa: E402

GAME = os.path.join(L.P4, '游戏')
DATA = os.path.join(GAME, 'data')
P3DATA = os.path.join(L.REPO, 'data')

# 从第三部直接拿来用的图（前缀匹配）
P3_REUSE = ['fx/', 'ui/sfx/', 'ui/menace/', 'ui/vs/mark', 'ui/tbc', 'ui/title/stand', 'chars/starplat', 'heads/starplat/',
            'ui/standcard/starplat', 'ui/special/jotaro_ts', 'ui/title/jotaro_ts', 'ui/title/jotaro_resume']
P3_CHARS = ['starplat']
P3_STANDS = ['starplat']
MUSIC = ['title', 'daily', 'tension', 'battle', 'sad', 'victory']
# 引擎里的 VS 卡、插入画、眼睛特写会按第三部的表情名要头像（angry / glare / surprise …），
#   第四部只画了 normal / rage / smile / shock 四种，所以构建时给每个角色补一份别名，缺的表情落到最像的那张上
HEAD_ALIAS = {'angry': 'rage', 'glare': 'rage', 'surprise': 'shock', 'hurt': 'shock', 'happy': 'smile',
              'sad': 'normal', 'serious': 'normal', 'portrait': 'normal', 'portrait_angry': 'rage'}


def read_gd(path):
    s = open(path, encoding='utf-8').read()
    return json.loads(s[s.index('=') + 1:s.rindex(';')])


def read_pack(path):
    s = open(path, encoding='utf-8').read()
    a = s.index('Object.assign(D.img,') + len('Object.assign(D.img,')
    b = s.index(');D.packKeys')
    return json.loads(s[a:b])


def write_text(path, s):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(s)
    os.replace(tmp, path)


def deep_merge(a, b):
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def main():
    if '--no-font' not in sys.argv:
        import p4_font
        p4_font.build()
    p3 = read_gd(os.path.join(P3DATA, 'data_meta.js'))
    p3img = read_pack(os.path.join(P3DATA, 'img_core.js'))
    meta = lambda n, d=None: L.load_json(os.path.join(L.META, n + '.json'), d)
    cm = meta('chars', {})
    pm = meta('props', {})
    bgm = meta('bg', {})
    uim = meta('ui', {})
    font = meta('font', {})

    gd = dict(v=1, built=time.strftime('%Y-%m-%dT%H:%M:%S'), img={}, packsLoaded={}, packKeys={})
    groups = {'core': []}
    # 1) 第三部通用部件
    for k, uri in p3img.items():
        if any(k == p or k.startswith(p) for p in P3_REUSE):
            gd['img'][k] = uri
            groups['core'].append(k)
    # 2) 第四部的图（同名时第四部覆盖）
    for fp in sorted(glob.glob(os.path.join(L.ASSETS, '**', '*.png'), recursive=True)):
        rel = os.path.relpath(fp, L.ASSETS).replace(os.sep, '/')
        if rel.startswith('_') or '/_' in rel or rel.startswith('preview/') or rel.startswith('chars_full/'):
            continue
        key = rel[:-4]
        pack = 'core'
        if key.startswith('bg/'):
            bk = key.split('/')[1]
            pack = 'bg_' + (bgm.get(bk, {}).get('pack') or 'prologue')
        with open(fp, 'rb') as fh:
            gd['img'][key] = 'data:image/png;base64,' + base64.b64encode(fh.read()).decode('ascii')
        for g in groups.values():
            if key in g:
                g.remove(key)
        groups.setdefault(pack, []).append(key)
    # 3) 元数据
    gd['ck'] = p3['ck']
    gd['chars'] = {k: p3['chars'][k] for k in P3_CHARS}
    gd['chars'].update(cm.get('chars', {}))
    for cid, c in cm.get('chars', {}).items():
        heads = c.get('heads') or {}
        if not heads:
            continue
        alias = dict(c.get('headAlias') or {})
        for k, v in HEAD_ALIAS.items():
            if k not in heads and k not in alias:
                alias[k] = v if v in heads else 'normal'
        gd['chars'][cid] = dict(c, headAlias=alias)
    gd['heroes'] = dict(cm.get('heroes', {}))
    gd['speakers'] = dict(cm.get('speakers', {}))
    gd['stands'] = {k: p3['stands'][k] for k in P3_STANDS}
    gd['stands'].update(cm.get('stands', {}))
    gd['props'] = pm.get('props', {})
    gd['scene'] = pm.get('scene', {})
    gd['bg'] = bgm
    ui = {k: p3['ui'][k] for k in ('sfx', 'menace', 'tbc') if k in p3['ui']}
    ui['vs'] = {'mark': p3['ui']['vs']['mark']}
    ui['standcards'] = {'starplat': p3['ui']['standcards']['starplat']}
    ui['titles'] = {k: v for k, v in p3['ui'].get('titles', {}).items() if k in ('stand', 'jotaro_ts', 'jotaro_resume')}
    ui['specials'] = {k: v for k, v in p3['ui'].get('specials', {}).items() if k in ('jotaro_ts',)}
    ui = deep_merge(ui, uim)
    gd['ui'] = ui
    gd['font'] = font
    gd['fxtex'] = p3['fxtex']
    gd['audio'] = {'music': {k: v for k, v in p3['audio']['music'].items() if k in MUSIC}, 'sfx': p3['audio']['sfx']}
    gd['video'] = {}
    # 4) 分包
    packs = {'core': {'file': 'data/img_core.js'}}
    shorts = sorted({(st.get('pack') or 'prologue') for st in bgm.values()} | {'common', 'title', 'prologue'})
    for short in shorts:
        packs['bg_' + short] = {'file': f'data/img_bg_{short}.js',
                                'bg': sorted(k for k, st in bgm.items() if (st.get('pack') or 'prologue') == short)}
        groups.setdefault('bg_' + short, [])
    packs['bg_title']['music'] = ['title']
    packs['bg_prologue']['music'] = ['daily', 'tension', 'battle', 'sad', 'victory']
    gd['packs'] = packs
    # 5) 校验：元数据里提到的图都要在
    want = set()
    for c in gd['chars'].values():
        want.add(c['image'])
        for fr in (c.get('heads') or {}).values():
            want.update(fr)
    for sec in ('namecards', 'standcards', 'locations', 'chapters', 'titles', 'sfx', 'specials'):
        for m in (ui.get(sec) or {}).values():
            if isinstance(m, dict) and m.get('image'):
                want.add(m['image'])
    for p in list(gd['props'].values()) + list(gd['scene'].values()):
        if isinstance(p, dict) and p.get('image'):
            want.add(p['image'])
    miss = sorted(k for k in want if k not in gd['img'])
    if miss:
        print('！元数据里提到、但没有图：', miss[:30], '…' if len(miss) > 30 else '')
    # 6) 写文件
    os.makedirs(DATA, exist_ok=True)
    data_keys = {k: v for k, v in gd.items() if k != 'img'}
    data_keys['img'] = {}
    js = 'window.GAME_DATA = ' + json.dumps(data_keys, ensure_ascii=False, separators=(',', ':')) + ';\n'
    write_text(os.path.join(DATA, 'data_meta.js'), js)
    sizes = {'data_meta.js': len(js.encode('utf-8'))}
    for rp, keys in sorted(groups.items()):
        fname = 'img_core.js' if rp == 'core' else f'img_{rp}.js'
        parts = [json.dumps(k, ensure_ascii=False) + ':' + json.dumps(gd['img'][k]) for k in keys]
        tail = f'D.packKeys[{json.dumps(rp)}]={json.dumps(keys, ensure_ascii=False)};D.packsLoaded[{json.dumps(rp)}]=true;'
        js = '(function(){var D=window.GAME_DATA;Object.assign(D.img,{' + ','.join(parts) + '});' + tail + '})();\n'
        write_text(os.path.join(DATA, fname), js)
        sizes[fname] = len(js.encode('utf-8'))
    # 旧的、已经不用的背景包删掉
    for fp in glob.glob(os.path.join(DATA, 'img_bg_*.js')):
        if os.path.basename(fp)[4:-3] not in groups:
            os.remove(fp)
    for k, v in sorted(sizes.items()):
        print(f'  {k:28s} {v / 1024:8.1f} KB')
    print('图片', len(gd['img']), '张；角色', len(gd['chars']), '；背景', len(bgm))


if __name__ == '__main__':
    main()
