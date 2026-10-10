"""定向重烘五位角色的落水形象，并从正式图集生成验收预览。"""
import sys
sys.dont_write_bytecode = True

import importlib
import json
import os
from pathlib import Path
import shutil

from PIL import Image

GAME = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(GAME / 'tools' / 'art'))
import art_common as AC
import bake_art
import bake_characters as B
import amap

HEROES = {'jotaro': '承太郎', 'joseph': '乔瑟夫', 'avdol': '阿布德尔',
          'kakyoin': '花京院', 'polnareff': '波鲁纳雷夫'}


def atlas_frames(folder, cid):
    meta = json.loads((folder / cid / (cid + '.json')).read_text(encoding='utf-8'))
    atlas = Image.open(folder / cid / (cid + '.png')).convert('RGBA')
    w, h = meta['cell']
    frames = {act: [atlas.crop((i * w, a['row'] * h, (i + 1) * w, (a['row'] + 1) * h))
                    for i in range(a['frames'])] for act, a in meta['animations'].items()}
    return meta, frames


def aligned_pixels(im, pivot):
    box = im.getbbox()
    return (box[0] - pivot[0], box[1] - pivot[1], im.crop(box).size, im.crop(box).tobytes()) if box else None


def main():
    folder = Path(AC.CHARS_NEW)
    before = {cid: atlas_frames(folder, cid) for cid in HEROES}
    backup = GAME / 'tools' / 'art' / '_旧稿' / '20261009-200046' / 'chars_new'
    for cid in HEROES:
        if not (backup / cid).exists():
            shutil.copytree(folder / cid, backup / cid)

    original, _, _ = bake_art.original_names()
    cwd = os.getcwd()
    try:
        B.load_registry(AC.SRC, with_scene=False)
    finally:
        os.chdir(cwd)
    from engine import sprite
    modules = [importlib.import_module(name) for name in bake_art.ART_MODULES]
    new = {name for module in modules for name in module.NEW}
    for module in modules:
        B.ONESHOT |= bake_art.playback_names(module, 'ONESHOT')
        B.STATIC_STATES |= bake_art.playback_names(module, 'STATIC_STATES')
        B.ACTION_ZH.update(getattr(module, 'ACTION_ZH', {}))
    selected = sorted(name for name in original | new if name.split('.')[0] in HEROES)
    chars, _ = B.build_actions({name: B.Spr(name, sprite.get(name), 'game.sea_half_head') for name in selected})
    baked = [B.bake_character(cid, *chars[cid], [], str(folder), AC.SCALE) for cid in HEROES]
    errors, frame_count = B.verify(str(folder), baked, [], {}, [], {})
    engine_count, engine_errors, engine_skip = B.verify_engine(baked)
    if errors or engine_errors or engine_skip:
        raise RuntimeError(f'图集校验失败：回读 {errors}、引擎 {engine_errors}、跳过 {engine_skip}')

    items, checked = [], 0
    for cid, name in HEROES.items():
        meta, frames = atlas_frames(folder, cid)
        old_meta, old_frames = before[cid]
        for act, old in old_frames.items():
            if act == 'float':
                continue
            current = frames[act]
            if len(old) != len(current) or any(aligned_pixels(a, old_meta['pivot']) != aligned_pixels(b, meta['pivot'])
                                               for a, b in zip(old, current)):
                raise RuntimeError(f'本次范围外的动作发生变化：{cid}.{act}')
            checked += len(old)
        for logical, target in amap.AMAP[cid].items():
            if amap.target(target) not in meta['animations']:
                raise RuntimeError(f'动作映射不存在：{cid}.{logical}')
        for i, im in enumerate(frames['float']):
            cropped, pivot = AC.crop_keep_pivot(im, tuple(meta['pivot']))
            items.append((f'{name} 第{i + 1}帧', cropped, pivot))
            items.append((f'{name} 第{i + 1}帧 向左', cropped.transpose(Image.Transpose.FLIP_LEFT),
                          (cropped.width - pivot[0], pivot[1])))
    AC.preview_items(items, str(OUT / '五人落水_双帧与翻转.png'), '海面只露半个头：五位角色、两帧、两个朝向',
                     scale=6, bg_ground=False)
    report = {'角色': list(HEROES), '图集回读帧数': frame_count, '引擎比对次数': engine_count,
              '引擎错误': engine_errors, '其他动作未变帧数': checked, '预览': '五人落水_双帧与翻转.png'}
    (OUT / '图集验收.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
