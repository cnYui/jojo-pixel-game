"""独立资源交付核对：读取烘焙产物，列动作/道具真值，并画关键场景组合预览。"""
import sys
sys.dont_write_bytecode = True

import json
import re
from pathlib import Path
from PIL import Image, ImageDraw
import art_common as AC
import amap

HERE = Path(__file__).resolve().parent
GAME = HERE.parent.parent
OUT = HERE / '_preview'
BAKED = HERE / '_later_verified'
ORIGINAL = Path(AC.ATLAS_DIR)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def meta(cid):
    fresh = BAKED / 'chars_new' / cid / (cid + '.json')
    path = fresh if fresh.exists() else ORIGINAL / cid / (cid + '.json')
    return path, read(path)


def action_frame(cid, logical, index=0):
    path, m = meta(cid)
    real = amap.target(amap.AMAP[cid][logical])
    a = m['animations'][real]
    cw, ch = m['cell']
    f = min(index, a['frames'] - 1)
    atlas = Image.open(path.with_suffix('.png')).convert('RGBA')
    return atlas.crop((cw * f, ch * a['row'], cw * (f + 1), ch * (a['row'] + 1))), m['pivot']


def prop_entries():
    old = read(ORIGINAL / '道具' / '道具目录.json')['sprites']
    new = read(BAKED / 'props_new' / 'props_new.json')['props']
    return [(e, ORIGINAL / '道具', '原图集') for e in old] + [(e, BAKED / 'props_new', '新画') for e in new]


def prop_frame(e, folder, frame=0):
    im = Image.open(folder / e['file']).convert('RGBA')
    w, h = e['size']
    return im.crop((w * frame, 0, w * (frame + 1), h))


def save_preview(items, filename, title):
    AC.preview_items(items, str(OUT / filename), title, bg_ground=False)


def previews(props):
    heroes = ('jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff')
    floats = []
    for cid in heroes:
        for f in range(2):
            im, pivot = action_frame(cid, 'float', f)
            floats.append((cid + '.float[' + str(f) + ']', *AC.crop_keep_pivot(im, tuple(pivot))))
    save_preview(floats, 'floating_heroes.png', '五位同伴的水面姿势：躯干和四肢独立绘制')
    ids = ('blanket', 'rock', 'baby_cradle', 'ice_wall', 'upper_tooth', 'lower_tooth',
           'hide_wardrobe', 'aquarium', 'hide_bed', 'hide_curtain', 'hide_crate', 'hide_cupboard',
           'cane', 'tea_cup', 'cake', 'cart', 'hat')
    items = []
    for pid in ids:
        e, folder, _ = props[pid]
        for f in range(e['frames']):
            items.append((pid + '[' + str(f) + ']', prop_frame(e, folder, f), tuple(e['pivot'])))
    save_preview(items, 'later_key_props.png', '新增道具：家具 0=关闭 1=打开；冰墙和牙齿 1=碎裂')

    bgdir = GAME / 'tools' / 'bg_new' / '_preview'
    stages = read(bgdir / '_stages.json')
    for frame in (0, 1):
        im = Image.open(bgdir / 'luxor_house_wide.png').convert('RGBA')
        for pid in ('hide_wardrobe', 'aquarium', 'hide_curtain', 'hide_bed', 'hide_crate', 'hide_cupboard'):
            e, folder, _ = props[pid]
            x, y = stages['luxor_house']['anchors']['hide_aquarium' if pid == 'aquarium' else pid]
            px, py = e['pivot']
            im.alpha_composite(prop_frame(e, folder, frame), (round(x - px), round(y - py)))
        im.resize((1280, 360), Image.Resampling.NEAREST).save(OUT / ('luxor_furniture_' + str(frame) + '.png'))
    stair = Image.open(bgdir / 'mansion_stairs.png').convert('RGBA')
    d = ImageDraw.Draw(stair)
    for x, y in stages['mansion_stairs']['anchors']['steps']:
        d.line((x - 2, y, x + 2, y), fill=(255, 48, 168))
        d.line((x, y - 2, x, y + 2), fill=(255, 48, 168))
    stair.resize((1280, 720), Image.Resampling.NEAREST).save(OUT / 'mansion_stairs_anchors.png')


def literal_refs(char_ids, prop_ids):
    found, missing = [], []
    paths = list((GAME / 'story').glob('*.js')) + list((GAME / 'engine').glob('moves*.js'))
    patterns = [re.compile(r"\bcid\s*:\s*['\"]([a-z_][a-z0-9_:]*)['\"]"),
                re.compile(r"\b(?:[A-Za-z_]\w*\.)?prop\([^,]+,\s*['\"]([a-z_][a-z0-9_]*)['\"]")]
    for path in paths:
        content = path.read_text(encoding='utf-8-sig')
        for i, pat in enumerate(patterns):
            for match in pat.finditer(content):
                name = match.group(1)
                # 拼接表达式只有片段，不能把它当成完整引用证明已覆盖。
                tail = content[match.end():].lstrip()
                if tail.startswith('+'):
                    continue
                if name.startswith('scene:'):
                    continue
                prop = i == 1 or name.startswith('prop:')
                actual = name.removeprefix('prop:')
                row = {'file': str(path.relative_to(GAME)), 'line': content[:match.start()].count('\n') + 1,
                       'kind': '道具' if prop else '角色', 'id': actual}
                found.append(row)
                if actual not in (prop_ids if prop else char_ids):
                    missing.append(row)
    return {'literal_refs': found, 'missing': missing,
            'scope': '仅角色/道具的静态 cid 字面量和 prop 调用字面量；scene 名称、动态拼接、变量、动作名由主代理联调检查。'}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    props = {e['id']: (e, folder, src) for e, folder, src in prop_entries()}
    actions = []
    for cid, table in sorted(amap.AMAP.items()):
        path, m = meta(cid)
        for logical, target in sorted(table.items()):
            real = amap.target(target)
            a = m['animations'][real]
            actions.append({'cid': cid, 'logical': logical, 'real': real,
                            'frames': a['frames'], 'kind': a['kind'],
                            'frame': target.get('f') if isinstance(target, dict) else None,
                            'source': '新烘焙' if '_later_verified' in str(path) else '原图集'})
    prop_rows = [{**e, 'source': src} for e, _, src in props.values()]
    refs = literal_refs(set(amap.AMAP), set(props))
    data = {'actions': actions, 'props': prop_rows, 'references': refs}
    (OUT / 'later_asset_inventory.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    md = ['# 后续资源真实清单', '', '该清单由独立产物读取；正式 assets 由主代理统一构建。', '',
          '## 角色动作映射', '', '|角色|逻辑动作|真动作|帧数|播放方式|来源|', '|---|---|---|---:|---|---|']
    md += [f"|{r['cid']}|{r['logical']}|{r['real']}|{r['frames']}|{r['kind']}|{r['source']}|" for r in actions]
    md += ['', '## 道具', '', '|ID|尺寸|帧数|来源|说明|', '|---|---|---:|---|---|']
    md += [f"|{r['id']}|{r['size'][0]}×{r['size'][1]}|{r['frames']}|{r['source']}|{r.get('desc','')}|" for r in prop_rows]
    md += ['', '## 字面量引用抽查', '', refs['scope'], '', f"抽取 {len(refs['literal_refs'])} 条，发现 {len(refs['missing'])} 条缺失。"]
    md += [f"- {r['file']}:{r['line']} — {r['kind']} {r['id']}" for r in refs['missing']]
    (OUT / '后续资源真实清单.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    previews(props)
    print(json.dumps({'characters': len(amap.AMAP), 'actions': len(actions), 'props': len(props),
                      'literal_refs': len(refs['literal_refs']), 'missing': refs['missing']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
