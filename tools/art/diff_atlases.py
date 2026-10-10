"""diff_atlases -- 重烘后逐像素对比图集（和重烘前的快照比），列出变了的图集和变了的动作行。

用法：python -B tools\\art\\diff_atlases.py <快照目录> [--expect cid,cid,...] [--out diff.json]
  快照目录里有 chars\\（= assets\\chars 的拷贝）、chars_new\\（= assets\\chars_new）、chars_meta.json（= tools\\_meta\\chars.json）。
  --expect：这次本该变的图集；有别的图集变了 → 返回 1。
比 assets\\chars\\<cid>.png（游戏实际用的合并图集，按 chars_meta 的行号报动作名）和 assets\\chars_new\\<cid>\\<cid>.png。
"""
import sys
sys.dont_write_bytecode = True
import os
import json
import argparse
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(os.path.dirname(HERE))


def rows_changed(a, b, meta):
    ch = meta['cell'][1]
    out = []
    for name, v in meta['animations'].items():
        r = v['row']
        if not np.array_equal(a[r * ch:(r + 1) * ch], b[r * ch:(r + 1) * ch]):
            out.append(name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('snap')
    ap.add_argument('--expect', default='')
    ap.add_argument('--out', default='')
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    expect = {c for c in args.expect.split(',') if c}
    old_meta = json.load(open(os.path.join(args.snap, 'chars_meta.json'), encoding='utf-8'))['chars']
    new_meta = json.load(open(os.path.join(GAME, 'tools', '_meta', 'chars.json'), encoding='utf-8'))['chars']
    rep = {'built_chars': {}, 'chars_new': {}, 'same_built': 0, 'same_new': 0, 'unexpected': []}
    for cid in sorted(set(old_meta) | set(new_meta)):
        po = os.path.join(args.snap, 'chars', cid + '.png')
        pn = os.path.join(GAME, 'assets', 'chars', cid + '.png')
        if not (os.path.exists(po) and os.path.exists(pn)):
            rep['built_chars'][cid] = {'status': 'added' if os.path.exists(pn) else 'removed'}
            continue
        a = np.asarray(Image.open(pn).convert('RGBA'))
        b = np.asarray(Image.open(po).convert('RGBA'))
        mo, mn = old_meta.get(cid), new_meta.get(cid)
        same_meta = mo and mn and mo['cell'] == mn['cell'] and mo['pivot'] == mn['pivot'] and \
            {k: (v['row'], v['frames']) for k, v in mo['animations'].items()} == \
            {k: (v['row'], v['frames']) for k, v in mn['animations'].items()}
        if a.shape == b.shape and np.array_equal(a, b) and same_meta:
            rep['same_built'] += 1
            continue
        rows = rows_changed(a, b, mn) if (a.shape == b.shape and same_meta) else ['(尺寸 / 行布局变了)']
        rep['built_chars'][cid] = {'status': 'changed', 'rows': rows, 'shape_old': list(b.shape), 'shape_new': list(a.shape),
                                   'meta_same': bool(same_meta)}
        if cid not in expect:
            rep['unexpected'].append(cid)
    nd_old, nd_new = os.path.join(args.snap, 'chars_new'), os.path.join(GAME, 'assets', 'chars_new')
    for cid in sorted(set(os.listdir(nd_old)) | set(os.listdir(nd_new))):
        po, pn = os.path.join(nd_old, cid, cid + '.png'), os.path.join(nd_new, cid, cid + '.png')
        if not (os.path.exists(po) and os.path.exists(pn)):
            rep['chars_new'][cid] = {'status': 'added' if os.path.exists(pn) else 'removed'}
            continue
        if np.array_equal(np.asarray(Image.open(po).convert('RGBA')), np.asarray(Image.open(pn).convert('RGBA'))):
            rep['same_new'] += 1
        else:
            rep['chars_new'][cid] = {'status': 'changed'}
            if cid not in expect and cid not in rep['unexpected']:
                rep['unexpected'].append(cid)
    print(f"合并图集 assets\\chars：不变 {rep['same_built']}，变了 {len(rep['built_chars'])}")
    for cid, v in rep['built_chars'].items():
        print(f"  {cid}: {v['status']} {v.get('rows', '')}")
    print(f"chars_new：不变 {rep['same_new']}，变了 {len(rep['chars_new'])}：{' '.join(rep['chars_new'])}")
    print('意外变化：', rep['unexpected'] or '无')
    if args.out:
        json.dump(rep, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 1 if rep['unexpected'] else 0


if __name__ == '__main__':
    sys.exit(main())
