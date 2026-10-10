"""audit_heads -- 头身对位审计（用户 2026-10-09 晚：“这里角色的头和身体还是错位的，你全部检查一下，这些配角 NPC 还有没有这些情况？”）。

读游戏实际用的合并图集（assets\\chars\\<cid>.png + tools\\_meta\\chars.json，= build_assets chars 步的产物），
对每个角色逐帧量（角色一律朝右）：
  头中心   = 身高最上面 HEAD_FRAC（帽子 / 头发 / 上半张脸）那几行不透明像素的左右中点（bbox 中点）和质心；
  躯干中心 = 身高 42%–62% 那几行里“包含枢轴 x 的那一段”的中点，逐行取中位数（避开甩开的手臂）；
  脚中心   = 最下面 15% 的左右中点；枢轴 x = 图集 pivot。
  头偏 = 头中心 − 躯干中心（正 = 头在前，负 = 头落在身体后面）。|头偏| ≥ 2 列为“要看”。
  帧间跳动 = 同一动作里各帧头偏的最大 − 最小（走路时头在身上晃来晃去）。
另外查漂浮部件：8 邻接连通块里主块以外 ≥ 4 像素、上沿落在头部区域的块（帽子 / 发饰离开了头）。
动作：idle / walk / talk（按 amap 解析，talk 和 idle 同一行时不重复）为“判定动作”；其余站立动作只列数（不判定）。

输出 <out>\\：report.json、report.md、sheets\\<cid>.png（6 倍联系表：青 = 头中心、黄 = 躯干中心、洋红 = 枢轴）、
overview_NN.png（全部角色 idle[0] / walk[0] 4 倍并排，抽查用）。
用法：python -B tools\\art\\audit_heads.py [--atlas-dir 目录] [--meta chars.json] [--out 目录] [--only cid,cid] [--no-sheets]
      python -B tools\\art\\audit_heads.py --compare <旧 chars 目录> --only cid,cid --out <目录>   （前后对比联系表）
"""
import sys
sys.dont_write_bytecode = True

import os
import json
import time
import argparse
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import art_common as AC          # noqa: E402  （只用预览小工具；不 import 原工程）

HEAD_FRAC = 0.22
TORSO = (0.42, 0.62)
FEET_FRAC = 0.15
FLAG = 2.0
JUDGE = ('idle', 'walk', 'talk')
SKIP_ACTS = ('portrait', 'float', 'lie', 'down', 'bed', 'faint', 'seated', 'slump', 'kneel', 'sit', 'swim', 'car')


# ============================================================================ 读图集
def load_meta(path):
    return json.load(open(path, encoding='utf-8'))['chars']


def resolve(meta, logical):
    """amap → animations → aliases（atlas.js 前三步）；返回 (真名, 定格帧 | None) 或 None。"""
    v = (meta.get('amap') or {}).get(logical)
    if v is not None:
        if isinstance(v, dict):
            return v['a'], v.get('f')
        return v, None
    if logical in meta['animations']:
        return logical, None
    al = (meta.get('aliases') or {}).get(logical)
    if al and al in meta['animations']:
        return al, None
    return None


def cells(img, meta, real):
    a = meta['animations'][real]
    cw, ch = meta['cell']
    out = []
    for f in range(a['frames']):
        out.append(img.crop((f * cw, a['row'] * ch, (f + 1) * cw, (a['row'] + 1) * ch)))
    return out


# ============================================================================ 量
def _runs(row):
    xs = np.flatnonzero(row)
    if not len(xs):
        return []
    br = np.flatnonzero(np.diff(xs) > 1)
    starts = np.r_[xs[0], xs[br + 1]]
    ends = np.r_[xs[br], xs[-1]]
    return list(zip(starts.tolist(), ends.tolist()))


def components(mask):
    """8 邻接连通块：[(像素数, (x0, y0, x1, y1))]，按大小降序。"""
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    comps = []
    n = 0
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys.tolist(), xs.tolist()):
        if lab[y, x]:
            continue
        n += 1
        q = deque([(y, x)])
        lab[y, x] = n
        cnt, x0, y0, x1, y1 = 0, x, y, x, y
        while q:
            cy, cx = q.popleft()
            cnt += 1
            x0, y0, x1, y1 = min(x0, cx), min(y0, cy), max(x1, cx), max(y1, cy)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        q.append((ny, nx))
        comps.append((cnt, (x0, y0, x1, y1)))
    comps.sort(key=lambda c: -c[0])
    return comps


def measure(im, pivot):
    a = np.asarray(im.convert('RGBA'))
    m = a[..., 3] > 0
    if not m.any():
        return None
    ys = np.flatnonzero(m.any(1))
    y0, y1 = int(ys[0]), int(ys[-1])
    H = y1 - y0 + 1
    px = pivot[0]
    hb = max(4, int(round(HEAD_FRAC * H)))
    head = m[y0:y0 + hb]
    hx = np.flatnonzero(head.any(0))
    head_mid = (hx[0] + hx[-1]) / 2.0
    hy_idx, hx_idx = np.nonzero(head)
    head_mass = float(hx_idx.mean())
    t0, t1 = y0 + int(round(TORSO[0] * H)), y0 + int(round(TORSO[1] * H))
    cs = []
    for y in range(t0, max(t0 + 1, t1)):
        rs = _runs(m[y])
        if not rs:
            continue
        inside = [r for r in rs if r[0] <= px <= r[1]]
        r = inside[0] if inside else min(rs, key=lambda r: abs((r[0] + r[1]) / 2 - px))
        cs.append((r[0] + r[1]) / 2.0)
    torso = float(np.median(cs)) if cs else float(px)
    fb = max(2, int(round(FEET_FRAC * H)))
    fx = np.flatnonzero(m[y1 - fb + 1:y1 + 1].any(0))
    feet = (fx[0] + fx[-1]) / 2.0
    comps = components(m)
    loose = []
    for cnt, (bx0, by0, bx1, by1) in comps[1:]:
        if cnt >= 4 and by0 < y0 + max(hb, int(0.40 * H)):
            loose.append({'px': cnt, 'box': [bx0, by0, bx1, by1]})
    return {
        'top': y0, 'bottom': y1, 'height': H, 'head_band': [y0, y0 + hb - 1], 'torso_band': [t0, t1 - 1],
        'head_mid': round(float(head_mid), 1), 'head_mass': round(head_mass, 1),
        'torso': round(torso, 1), 'feet': round(float(feet), 1), 'pivot_x': px,
        'd_head': round(float(head_mid) - torso, 1), 'd_mass': round(head_mass - torso, 1),
        'd_torso': round(torso - px, 1), 'loose': loose,
    }


def audit_cid(cid, meta, img):
    out = {'cid': cid, 'kind': meta.get('kind'), 'name': meta.get('name'), 'cell': meta['cell'],
           'pivot': meta['pivot'], 'judge': {}, 'other': {}}
    seen = set()
    for logical in JUDGE:
        r = resolve(meta, logical)
        if not r or r[0] not in meta['animations']:
            continue
        real, fz = r
        key = (real, fz)
        if key in seen:
            continue
        seen.add(key)
        fr = cells(img, meta, real)
        if fz is not None:
            fr = [fr[min(fz, len(fr) - 1)]]
        out['judge'][logical + ('' if logical == real else '→' + real)] = [measure(f, meta['pivot']) for f in fr]
    judged_reals = {k[0] for k in seen}
    for real in meta['animations']:
        if real in judged_reals or any(real.startswith(s) for s in SKIP_ACTS):
            continue
        fr = cells(img, meta, real)
        out['other'][real] = [measure(f, meta['pivot']) for f in fr]
    # 汇总
    vals = [x for fs in out['judge'].values() for x in fs if x]
    out['worst'] = max((abs(x['d_head']) for x in vals), default=0.0)
    out['worst_signed'] = max((x['d_head'] for x in vals), key=abs, default=0.0)
    out['worst_mass'] = max((x['d_mass'] for x in vals), key=abs, default=0.0)
    out['swim'] = max((max(x['d_head'] for x in fs if x) - min(x['d_head'] for x in fs if x)
                       for fs in out['judge'].values() if any(fs)), default=0.0)
    out['torso_off'] = max((x['d_torso'] for x in vals), key=abs, default=0.0)
    out['loose'] = sorted({(k, i) for k, fs in out['judge'].items() for i, x in enumerate(fs) if x and x['loose']})
    out['flag'] = bool(out['worst'] >= FLAG or out['swim'] >= FLAG or out['loose'])
    return out


# ============================================================================ 画
def _guides(big, mm, s, ox=0, oy=0):
    d = ImageDraw.Draw(big)
    if not mm:
        return
    px = ox + mm['pivot_x'] * s + s // 2
    d.line((px, oy, px, oy + big.height), fill=(255, 0, 140))
    hy0, hy1 = mm['head_band']
    hx = ox + int(mm['head_mid'] * s) + s // 2
    d.line((hx, oy + hy0 * s, hx, oy + (hy1 + 1) * s), fill=(0, 230, 255), width=2)
    ty0, ty1 = mm['torso_band']
    tx = ox + int(mm['torso'] * s) + s // 2
    d.line((tx, oy + ty0 * s, tx, oy + (ty1 + 1) * s), fill=(255, 220, 0), width=2)
    for lo in mm['loose']:
        x0, y0, x1, y1 = lo['box']
        d.rectangle((ox + x0 * s - 1, oy + y0 * s - 1, ox + (x1 + 1) * s, oy + (y1 + 1) * s), outline=(255, 60, 60))


def _crop_box(frames, meta):
    """所有帧的并集 bbox（含枢轴列），左右各留 2 px。"""
    cw, ch = meta['cell']
    xs0, xs1 = [meta['pivot'][0]], [meta['pivot'][0]]
    for im in frames:
        bb = im.getbbox()
        if bb:
            xs0.append(bb[0])
            xs1.append(bb[2])
    return max(0, min(xs0) - 2), min(cw, max(xs1) + 2)


def sheet(cid, meta, img, rep, path, s=6, extra_rows=()):
    rows = []
    for key, ms in list(rep['judge'].items()) + [(k, rep['other'][k]) for k in extra_rows if k in rep['other']]:
        real = key.split('→')[-1]
        fr = cells(img, meta, real)
        if len(ms) == 1 and len(fr) > 1:          # 定格帧
            fz = resolve(meta, key.split('→')[0])[1]
            fr = [fr[min(fz or 0, len(fr) - 1)]]
        rows.append((key, fr, ms))
    allf = [f for _, fr, _ in rows for f in fr]
    x0, x1 = _crop_box(allf, meta)
    ch = meta['cell'][1]
    tops = [m['top'] for _, _, ms in rows for m in ms if m]
    y0 = max(0, min(tops) - 2) if tops else 0
    cw = x1 - x0
    lab_h = 30
    W = max(420, max(len(fr) for _, fr, _ in rows) * (cw * s + 12) + 160)
    Hh = 44 + len(rows) * ((ch - y0) * s + lab_h + 12)
    out = AC.checker(W, Hh, sq=s * 4).convert('RGB')
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, W, 36), fill=(36, 34, 48))
    d.text((10, 8), f"{cid}  {meta.get('name', '')}  cell {meta['cell']}  pivot {meta['pivot']}  "
                    f"最大头偏 {rep['worst_signed']:+.1f}  帧间跳动 {rep['swim']:.1f}  ×{s}",
           font=AC.font(16), fill=(255, 236, 160))
    y = 44
    for key, fr, ms in rows:
        d.text((8, y + 6), key, font=AC.font(14), fill=(30, 28, 50))
        x = 150
        for im, mm in zip(fr, ms):
            c = im.crop((x0, y0, x1, ch))
            big = c.resize((c.width * s, c.height * s), Image.NEAREST)
            tile = Image.new('RGBA', big.size, (0, 0, 0, 0))
            tile.alpha_composite(big)
            if mm:
                mm2 = dict(mm, pivot_x=mm['pivot_x'] - x0, head_mid=mm['head_mid'] - x0, torso=mm['torso'] - x0,
                           head_band=[mm['head_band'][0] - y0, mm['head_band'][1] - y0],
                           torso_band=[mm['torso_band'][0] - y0, mm['torso_band'][1] - y0],
                           loose=[{'box': [b['box'][0] - x0, b['box'][1] - y0, b['box'][2] - x0, b['box'][3] - y0]}
                                  for b in mm['loose']])
                _guides(tile, mm2, s)
            out.paste(tile.convert('RGB'), (x, y + lab_h), tile)
            if mm:
                col = (200, 20, 40) if abs(mm['d_head']) >= FLAG else (30, 28, 50)
                d.text((x, y + 8), f"头偏{mm['d_head']:+.1f} 质{mm['d_mass']:+.1f}", font=AC.font(13), fill=col)
            x += c.width * s + 12
        y += (ch - y0) * s + lab_h + 12
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path, optimize=True)
    return path


def overview(items, path, title, s=4, per_row=12):
    """items = [(标签, PIL 帧, 测量)]：并排（同一行地面对齐）+ 参考线。"""
    tiles = []
    for lab, im, mm in items:
        bb = im.getbbox() or (0, 0, im.width, im.height)
        x0, x1 = max(0, min(bb[0], mm['pivot_x']) - 2), min(im.width, max(bb[2], mm['pivot_x'] + 1) + 2)
        y0 = max(0, bb[1] - 2)
        c = im.crop((x0, y0, x1, im.height))
        big = c.resize((c.width * s, c.height * s), Image.NEAREST)
        tile = Image.new('RGBA', big.size, (0, 0, 0, 0))
        tile.alpha_composite(big)
        mm2 = dict(mm, pivot_x=mm['pivot_x'] - x0, head_mid=mm['head_mid'] - x0, torso=mm['torso'] - x0,
                   head_band=[mm['head_band'][0] - y0, mm['head_band'][1] - y0],
                   torso_band=[mm['torso_band'][0] - y0, mm['torso_band'][1] - y0],
                   loose=[{'box': [b['box'][0] - x0, b['box'][1] - y0, b['box'][2] - x0, b['box'][3] - y0]}
                          for b in mm['loose']])
        _guides(tile, mm2, s)
        tiles.append((lab, tile, mm))
    rows = [tiles[i:i + per_row] for i in range(0, len(tiles), per_row)]
    W = max(sum(t.width + 14 for _, t, _ in r) for r in rows) + 16
    Hs = [max(t.height for _, t, _ in r) + 40 for r in rows]
    out = AC.checker(W, sum(Hs) + 44, sq=s * 4).convert('RGB')
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, W, 36), fill=(36, 34, 48))
    d.text((10, 8), title, font=AC.font(16), fill=(255, 236, 160))
    y = 44
    for r, hh in zip(rows, Hs):
        x = 8
        for lab, t, mm in r:
            col = (200, 20, 40) if abs(mm['d_head']) >= FLAG else (30, 28, 50)
            d.text((x, y), lab, font=AC.font(12), fill=(30, 28, 50))
            d.text((x, y + 14), f"{mm['d_head']:+.1f}", font=AC.font(12), fill=col)
            out.paste(t.convert('RGB'), (x, y + hh - 6 - t.height), t)
            x += t.width + 14
        y += hh
    out.save(path, optimize=True)
    return path


# ============================================================================ 前后对比
def compare_sheet(cid, meta_new, img_new, meta_old, img_old, path, acts=None, s=6):
    """同一角色：上排旧、下排新（每个动作的全部帧），同一地面线，参考线同上。"""
    acts = acts or [a for a in meta_new['animations'] if not a.startswith('portrait')]
    blocks = []
    for real in acts:
        if real not in meta_new['animations']:
            continue
        new = cells(img_new, meta_new, real)
        old = cells(img_old, meta_old, real) if (meta_old and real in meta_old['animations']) else []
        blocks.append((real, old, new))
    lab_h = 22
    pv_new, pv_old = meta_new['pivot'], (meta_old or meta_new)['pivot']

    def crop(im, pv):
        bb = im.getbbox() or (0, 0, im.width, im.height)
        return bb, pv

    up = max(max([pv_new[1] - (f.getbbox() or (0, pv_new[1], 0, 0))[1] for _, _, n in blocks for f in n] + [1]),
             max([pv_old[1] - (f.getbbox() or (0, pv_old[1], 0, 0))[1] for _, o, _ in blocks for f in o] + [1]))
    dn = max([meta_new['cell'][1] - pv_new[1]] + ([meta_old['cell'][1] - pv_old[1]] if meta_old else [0]))
    row_h = (up + dn + 2) * s + lab_h
    tiles_w = []
    for real, old, new in blocks:
        w = 0
        for f, pv in [(f, pv_new) for f in new] + [(f, pv_old) for f in old]:
            bb = f.getbbox() or (pv[0], 0, pv[0] + 1, 1)
            w = max(w, (max(bb[2], pv[0] + 1) - min(bb[0], pv[0]) + 4))
        tiles_w.append(w)
    W = 120 + sum(max(len(n), len(o)) * (w * s + 8) + 24 for (r, o, n), w in zip(blocks, tiles_w))
    W = max(W, 600)
    H = 44 + 2 * row_h + 20
    out = AC.checker(W, H, sq=s * 4).convert('RGB')
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, W, 36), fill=(36, 34, 48))
    d.text((10, 8), f'{cid}  上 = 改前  下 = 改后  ×{s}（洋红 = 枢轴，青 = 头中心，黄 = 躯干中心）',
           font=AC.font(16), fill=(255, 236, 160))
    d.text((8, 44 + lab_h + 10), '改前', font=AC.font(16), fill=(30, 28, 50))
    d.text((8, 44 + row_h + lab_h + 10), '改后', font=AC.font(16), fill=(30, 28, 50))
    x = 120
    for (real, old, new), w in zip(blocks, tiles_w):
        d.text((x, 44), real, font=AC.font(13), fill=(30, 28, 50))
        for ri, (fr, pv, meta) in enumerate(((old, pv_old, meta_old), (new, pv_new, meta_new))):
            xx = x
            base = 44 + ri * row_h + lab_h + (up + 1) * s
            for f in fr:
                c0 = pv[0] - w // 2
                c = Image.new('RGBA', (w, up + dn + 2), (0, 0, 0, 0))
                c.alpha_composite(f, (-c0, up + 1 - pv[1]))
                big = c.resize((c.width * s, c.height * s), Image.NEAREST)
                mm = measure(f, pv)
                if mm and real not in SKIP_ACTS and not any(real.startswith(sk) for sk in SKIP_ACTS):
                    dy = up + 1 - pv[1]
                    mm2 = dict(mm, pivot_x=mm['pivot_x'] - c0, head_mid=mm['head_mid'] - c0, torso=mm['torso'] - c0,
                               head_band=[mm['head_band'][0] + dy, mm['head_band'][1] + dy],
                               torso_band=[mm['torso_band'][0] + dy, mm['torso_band'][1] + dy], loose=[])
                    _guides(big, mm2, s)
                out.paste(big.convert('RGB'), (xx, base - (up + 1) * s), big)
                xx += w * s + 8
        x += max(len(new), len(old)) * (w * s + 8) + 24
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path, optimize=True)
    return path


# ============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--atlas-dir', default=os.path.join(GAME, 'assets', 'chars'))
    ap.add_argument('--meta', default=os.path.join(GAME, 'tools', '_meta', 'chars.json'))
    ap.add_argument('--out', default=os.path.join(GAME, 'tools', '_playtest', 'art_heads_' + time.strftime('%Y%m%d-%H%M%S')))
    ap.add_argument('--only', default='')
    ap.add_argument('--no-sheets', action='store_true')
    ap.add_argument('--all-sheets', action='store_true')
    ap.add_argument('--compare', default='', help='旧 chars 目录（含 <cid>.png）；配 --compare-meta 用旧元数据')
    ap.add_argument('--compare-meta', default='')
    ap.add_argument('--acts', default='', help='--compare 时只画这些动作（cid:act+act;cid:act 或 act+act 对所有角色）')
    ap.add_argument('--stitch', default='', help='--compare 时把各角色的对比图竖着拼成这个文件')
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    metas = load_meta(args.meta)
    only = [c for c in args.only.split(',') if c]
    cids = only or sorted(metas)
    os.makedirs(args.out, exist_ok=True)
    if args.compare:
        old_metas = load_meta(args.compare_meta) if args.compare_meta else metas
        acts_all, acts_by = None, {}
        for part in [p for p in args.acts.split(';') if p]:
            if ':' in part:
                c, a = part.split(':', 1)
                acts_by[c] = a.split('+')
            else:
                acts_all = part.split('+')
        paths = []
        for cid in cids:
            img_new = Image.open(os.path.join(args.atlas_dir, cid + '.png')).convert('RGBA')
            p_old = os.path.join(args.compare, cid + '.png')
            img_old = Image.open(p_old).convert('RGBA') if os.path.exists(p_old) else None
            p = compare_sheet(cid, metas[cid], img_new, old_metas.get(cid) if img_old else None, img_old,
                              os.path.join(args.out, f'compare_{cid}.png'), acts=acts_by.get(cid, acts_all))
            paths.append(p)
            print(p)
        if args.stitch:
            ims = [Image.open(p).convert('RGB') for p in paths]
            W = max(i.width for i in ims)
            out = Image.new('RGB', (W, sum(i.height for i in ims) + 6 * len(ims)), (36, 34, 48))
            y = 0
            for i in ims:
                out.paste(i, (0, y))
                y += i.height + 6
            out.save(args.stitch, optimize=True)
            print(args.stitch, out.size)
        return
    reps = []
    ov = []
    for cid in cids:
        meta = metas[cid]
        img = Image.open(os.path.join(args.atlas_dir, cid + '.png')).convert('RGBA')
        rep = audit_cid(cid, meta, img)
        reps.append(rep)
        for key, ms in rep['judge'].items():
            if key.startswith('idle') or key.startswith('walk'):
                real = key.split('→')[-1]
                fr = cells(img, meta, real)
                if ms and ms[0]:
                    ov.append((f'{cid}.{key.split("→")[0]}', fr[0] if len(ms) == len(fr) else
                               fr[min(resolve(meta, key.split('→')[0])[1] or 0, len(fr) - 1)], ms[0]))
        if not args.no_sheets and (rep['flag'] or args.all_sheets):
            sheet(cid, meta, img, rep, os.path.join(args.out, 'sheets', cid + '.png'))
    if not args.no_sheets:
        per = 24
        for i in range(0, len(ov), per):
            overview(ov[i:i + per], os.path.join(args.out, f'overview_{i // per + 1:02d}.png'),
                     f'idle[0] / walk[0] 抽查 {i // per + 1}（数字 = 头偏，红 = |头偏| ≥ {FLAG:g}）', per_row=12)
    reps.sort(key=lambda r: -r['worst'])
    with open(os.path.join(args.out, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump({'built': time.strftime('%Y-%m-%dT%H:%M:%S'), 'atlas_dir': args.atlas_dir, 'meta': args.meta,
                   'method': {'head_frac': HEAD_FRAC, 'torso_band': TORSO, 'flag': FLAG, 'judge': JUDGE},
                   'chars': reps}, f, ensure_ascii=False, indent=1)
    md = ['# 头身对位审计', '', f'图集：`{args.atlas_dir}`；{len(reps)} 个角色；判定动作 idle / walk / talk；'
          f'头偏 = 头部区（最上 {HEAD_FRAC:.0%}）左右中点 − 躯干中心（正 = 头在前）。', '',
          '|角色|类|最大头偏|质心偏|帧间跳动|躯干−枢轴|漂浮块|要看|', '|---|---|---:|---:|---:|---:|---|---|']
    for r in reps:
        md.append(f"|{r['cid']}|{r['kind']}|{r['worst_signed']:+.1f}|{r['worst_mass']:+.1f}|{r['swim']:.1f}|"
                  f"{r['torso_off']:+.1f}|{len(r['loose'])}|{'是' if r['flag'] else ''}|")
    with open(os.path.join(args.out, 'report.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    for r in reps:
        print(f"{r['cid']:22s} {r['kind']:6s} head {r['worst_signed']:+5.1f} mass {r['worst_mass']:+5.1f} "
              f"swim {r['swim']:4.1f} torso {r['torso_off']:+5.1f} loose {len(r['loose'])} {'FLAG' if r['flag'] else ''}")
    print('out:', args.out)


if __name__ == '__main__':
    main()
