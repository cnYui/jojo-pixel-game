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
        for fp, e in found:
            lost = sorted(set(e.get('animations', {})) - set(new))
            if lost:
                print('  ！%s 少了旧图集里有的动作（%s）：%s' % (cid, os.path.basename(fp), lost))
            e.update(image='chars/' + cid, cell=cell, pivot=pivot, animations=new, top=top)
            e['amap'] = {k: v for k, v in (e.get('amap') or {}).items() if (v if isinstance(v, str) else v.get('a')) in new}
            touched.add(fp)
        print('  %-14s cell %s pivot %s top %d  %d 行 %d 帧' % (cid, cell, pivot, top, len(new), sum(a['frames'] for a in new.values())))
    for fp in touched:
        save(fp, files[fp])


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        name, _, ids = arg.partition(':')
        print(name)
        export(name, set(ids.split(',')) if ids else None)
