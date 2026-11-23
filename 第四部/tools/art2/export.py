# 第四部重画：把人物 / 替身的图集写进 assets/chars/，并更新 assets/_meta/chars*.json 里对应条目。
#   只换图和图集几何（cell / pivot / animations / top），其余字段（amap、别名、头像表、bodyW、名字……）原样保留：
#   剧情脚本、招式表、HUD 都是按这些名字和字段用的，重画不动玩法。
#   用法：python 第四部/tools/art2/export.py cast_pro stands_pro …        （模块名；每个模块有 CAST 和 build(cid)）
#         python 第四部/tools/art2/export.py cast_pro:josuke,koichi        （只导其中几个）
import glob
import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from px import ASSETS, META, P4, ensure  # noqa: E402

REPO = os.path.normpath(os.path.join(P4, '..'))


def load(fp):
    with open(fp, encoding='utf-8') as fh:
        return json.load(fh)


def save(fp, obj):
    with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write('\n')


def p3_char(cid):
    s = open(os.path.join(REPO, 'data', 'data_meta.js'), encoding='utf-8').read()
    d = json.loads(s[s.index('=') + 1:s.rindex(';')])
    return d['chars'].get(cid)


def find_entries(cid, files):
    """同一个 cid 可能在几份元数据里都有（chars.json 里一份旧的、chars_chN.json 里一份全的，构建时后者盖前者）：全都更新"""
    return [(fp, d['chars'][cid]) for fp, d in files.items() if cid in d.get('chars', {})]


# 各章的占位 / 换章复用的角色：同一个人只画一张图集，别名条目指过去（名字、amap、各自的 fps / kind 保留）
ALIASES = {
    'ph7_kira': 'kira', 'ph7_killerqueen': 'killerqueen', 'ph7_yukako': 'yukako', 'ph7_okuyasu': 'okuyasu',
    'ph8_rohan': 'rohan', 'ph8_joseph': 'joseph_old', 'ph8_kosaku': 'kawajiri', 'tmp6_joseph': 'joseph_old',
    'mikitaka_tmp': 'mikitaka', 'yuya_tmp': 'yuya', 'highway_tmp': 'highway',
    'ph11_hayato': 'hayato', 'ph11_kosaku': 'kawajiri', 'ph11_shinobu': 'shinobu', 'ph11_rohan': 'rohan', 'ph11_okuyasu': 'okuyasu',
    'ph11_reimi': 'reimi', 'ph11_killerq': 'killerqueen',
    'fin_kq': 'killerqueen', 'fin_thehand': 'thehand', 'fin_echoes3': 'echoes3', 'fin_okuyasu': 'okuyasu', 'fin_keicho': 'keicho',
    'fin_rohan': 'rohan', 'fin_hayato': 'hayato', 'fin_reimi': 'reimi', 'fin_shinobu': 'shinobu', 'fin_arnold': 'arnold',
    'fin_joseph': 'joseph_old',
}
ALL = ['cast_pro', 'stands_pro', 'cast_ch1_3', 'stands_all', 'cast_ch4_6', 'cast_ch7_fin']


def apply_aliases():
    files = {fp: load(fp) for fp in sorted(glob.glob(os.path.join(META, 'chars*.json')))}
    canon = {}
    for fp, d in files.items():          # 后面的文件盖前面的（和 build_p4 的合并顺序一样）
        for cid, e in d.get('chars', {}).items():
            canon[cid] = e
    n = 0
    for alias, cid in ALIASES.items():
        c = canon.get(cid)
        if not c:
            print('  ！别名 %s 指向的 %s 还没有' % (alias, cid))
            continue
        for fp, e in find_entries(alias, files):
            anims = {}
            for a, old in (e.get('animations') or {}).items():
                if a not in c['animations']:
                    print('  ！%s 要的动作 %s 在 %s 的图集里没有' % (alias, a, cid))
                    continue
                anims[a] = dict(c['animations'][a], fps=old.get('fps', c['animations'][a]['fps']), kind=old.get('kind', c['animations'][a]['kind']))
            e.update(image=c['image'], cell=c['cell'], pivot=c['pivot'], top=c['top'], animations=anims)
            if e.get('heads') and c.get('heads'):
                e['heads'] = {k: (c['heads'].get(k) or c['heads'].get('normal')) for k in e['heads']}
                e['headSize'] = {}
            e['amap'] = {k: v for k, v in (e.get('amap') or {}).items() if (v if isinstance(v, str) else v.get('a')) in anims}
            n += 1
        # 别名自己的旧图不再用
        for rel in ('chars/%s.png' % alias,):
            p = os.path.join(ASSETS, rel)
            if os.path.exists(p):
                os.remove(p)
        hd = os.path.join(ASSETS, 'heads', alias)
        if os.path.isdir(hd):
            for f in os.listdir(hd):
                os.remove(os.path.join(hd, f))
            os.rmdir(hd)
    for fp in files:
        save(fp, files[fp])
    print('别名条目', n)


def export(mod_name, only=None, home='chars.json'):
    mod = importlib.import_module(mod_name)
    files = {fp: load(fp) for fp in sorted(glob.glob(os.path.join(META, 'chars*.json')))}
    touched = set()
    for cid in mod.CAST:
        if only and cid not in only:
            continue
        sh = mod.build(cid)
        im, cell, pivot = sh.pack()
        out = ensure(os.path.join(ASSETS, 'chars', cid + '.png'))
        im.save(out)
        found = find_entries(cid, files)
        if not found:
            # 以前直接借第三部图集的（白金之星）：把第三部的条目搬过来当底，图换成第四部自己的
            fp = os.path.join(META, getattr(mod, 'HOME', home))
            base = p3_char(cid) or dict(name=sh.name, aliases={}, heads={}, headAlias={}, headSize={}, amap={}, bodyW=4, kind=sh.kind)
            e = dict(base)
            files[fp].setdefault('chars', {})[cid] = e
            found = [(fp, e)]
        new = sh.anims()
        top = sh.top()
        heads = None
        if (sh.body is not None or getattr(sh, 'face', None)) and '--no-heads' not in sys.argv:
            # 对话头像跟着新造型重出：表情键照旧元数据（没有头像的角色不加）
            emos = []
            for _, e in found:
                for k in (e.get('heads') or {}):
                    if k not in emos:
                        emos.append(k)
            if emos:
                import portrait
                if sh.body is not None:
                    heads = portrait.export_heads(cid, sh.body, emos)
                else:
                    heads = portrait.export_face(cid, sh.rows[0][1][0], sh.face, emos)
        for fp, e in found:
            lost = sorted(set(e.get('animations', {})) - set(new))
            if lost:
                print('  ！%s 少了旧图集里有的动作（%s）：%s' % (cid, os.path.basename(fp), lost))
            oldan = e.get('animations') or {}
            anims = {a: dict(v, fps=oldan[a]['fps'], kind=oldan[a]['kind']) if a in oldan and oldan[a].get('frames') == v['frames'] else v
                     for a, v in new.items()}       # 帧数没变的动作沿用旧的 fps / kind（招式表按时间卡帧）
            e.update(image='chars/' + cid, cell=cell, pivot=pivot, animations=anims, top=top)
            if heads and e.get('heads'):
                e['heads'] = {k: heads[k] for k in e['heads'] if k in heads}
                e['headSize'] = {}
            e['amap'] = {k: v for k, v in (e.get('amap') or {}).items() if (v if isinstance(v, str) else v.get('a')) in new}
            touched.add(fp)
        print('  %-14s cell %s pivot %s top %d  %d 行 %d 帧' % (cid, cell, pivot, top, len(new), sum(a['frames'] for a in new.values())))
    for fp in touched:
        save(fp, files[fp])


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    for arg in (ALL if args == ['all'] else args):
        name, _, ids = arg.partition(':')
        print(name)
        export(name, set(ids.split(',')) if ids else None)
    if args == ['all'] or '--aliases' in sys.argv:
        apply_aliases()
