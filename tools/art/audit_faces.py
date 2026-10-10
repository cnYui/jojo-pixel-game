"""audit_faces -- 游戏里的脸 vs 对话框头像（用户 2026-10-09 晚：“为什么他左下角的脸和游戏里出现的脸不一样呢？五官是不是也拼错了？”）。

读合并图集（assets\\chars + tools\\_meta\\chars.json），每个有头像的角色一行：
  游戏 idle[0] 的头部（最上面到下巴，8 倍） | 对话框头像 normal_0（6 倍） | 头像缩到精灵头宽的参考（8 倍）
输出 <out>\\faces_NN.png（每张 8 个角色）+ faces.json（每个角色头像 key、头部框）。
用法：python -B tools\\art\\audit_faces.py [--out 目录] [--only cid,cid] [--atlas-dir 目录 --meta chars.json]
"""
import sys
sys.dont_write_bytecode = True
import os
import json
import time
import argparse
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import art_common as AC          # noqa: E402


def head_crop(cell, frac=0.46):
    a = np.asarray(cell)[..., 3] > 0
    ys, xs = np.nonzero(a)
    if not len(ys):
        return None, None
    top, bot = ys.min(), ys.max()
    h = int(round((bot - top + 1) * frac)) + 2
    rows = a[top:top + h]
    cx = np.nonzero(rows.any(0))[0]
    box = (max(0, cx.min() - 1), max(0, top - 1), min(cell.width, cx.max() + 2), min(cell.height, top + h))
    return cell.crop(box), box


def portrait_of(meta, chars_dir):
    heads = meta.get('heads') or {}
    keys = heads.get('normal') or (next(iter(heads.values())) if heads else None)
    if not keys:
        return None, None
    k = keys[0]                                   # heads/<cid>/<emotion>_<i>
    _, cid, em = k.split('/')
    p = os.path.join(chars_dir, cid + '_heads', em + '.png')
    return (Image.open(p).convert('RGBA') if os.path.exists(p) else None), k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(GAME, 'tools', '_playtest', 'art_faces_' + time.strftime('%Y%m%d-%H%M%S')))
    ap.add_argument('--only', default='')
    ap.add_argument('--atlas-dir', default=os.path.join(GAME, 'assets', 'chars'))
    ap.add_argument('--meta', default=os.path.join(GAME, 'tools', '_meta', 'chars.json'))
    ap.add_argument('--per', type=int, default=8)
    ap.add_argument('--anim', default='idle')
    args = ap.parse_args()
    metas = json.load(open(args.meta, encoding='utf-8'))['chars']
    only = [c for c in args.only.split(',') if c]
    os.makedirs(args.out, exist_ok=True)
    rows, info = [], {}
    for cid in (only or sorted(metas)):
        m = metas[cid]
        por, key = portrait_of(m, args.atlas_dir)
        if por is None:
            continue
        anim = (m.get('amap') or {}).get(args.anim, args.anim)
        anim = anim['a'] if isinstance(anim, dict) else anim
        if anim not in m['animations']:
            anim = next(iter(m['animations']))
        a = m['animations'][anim]
        sheet = Image.open(os.path.join(args.atlas_dir, cid + '.png')).convert('RGBA')
        cw, ch = m['cell']
        cell = sheet.crop((0, a['row'] * ch, cw, (a['row'] + 1) * ch))
        head, box = head_crop(cell)
        if head is None:
            continue
        pb = por.getbbox() or (0, 0, por.width, por.height)
        pc = por.crop(pb)
        sw = max(1, head.width)
        small = pc.resize((sw, max(1, round(pc.height * sw / pc.width))), Image.NEAREST)
        rows.append((cid, m.get('name', ''), head, pc, small))
        info[cid] = {'portrait': key, 'anim': anim, 'head_box': [int(v) for v in box]}
    for i in range(0, len(rows), args.per):
        chunk = rows[i:i + args.per]
        S1, S2, S3 = 8, 6, 8
        cw_ = max(r[2].width for r in chunk) * S1
        pw_ = max(r[3].width for r in chunk) * S2
        sw_ = max(r[4].width for r in chunk) * S3
        rh = [max(r[2].height * S1, r[3].height * S2, r[4].height * S3) + 26 for r in chunk]
        W = cw_ + pw_ + sw_ + 60
        img = AC.checker(W, sum(rh) + 40, sq=16).convert('RGB')
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, W, 32), fill=(36, 34, 48))
        d.text((8, 6), '左 = 游戏 idle[0] 头部 ×8 ｜ 中 = 对话框头像 ×6 ｜ 右 = 头像缩到精灵头宽 ×8', font=AC.font(15), fill=(255, 236, 160))
        y = 40
        for (cid, name, head, pc, small), h in zip(chunk, rh):
            d.text((8, y), f'{cid} {name}', font=AC.font(14), fill=(20, 20, 40))
            for im, s, x in ((head, S1, 10), (pc, S2, 20 + cw_), (small, S3, 40 + cw_ + pw_)):
                big = im.resize((im.width * s, im.height * s), Image.NEAREST)
                img.paste(big.convert('RGB'), (x, y + 22), big)
            y += h
        img.save(os.path.join(args.out, f'faces_{i // args.per + 1:02d}.png'), optimize=True)
    json.dump(info, open(os.path.join(args.out, 'faces.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(args.out, len(rows), '个角色有头像')


if __name__ == '__main__':
    main()
