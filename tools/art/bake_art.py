"""bake_art -- 包 7A 的烘焙配方（技术约定 §5.2；规划里写的 bake_game_chars.py 就是它）。

    run(out_dir=None, c=None, force=False) -> report(dict)

1. 读原 166 个精灵名（从只读的 角色图集\\*\\*.json + 道具\\道具目录.json 算，和 CATALOG 一致），
   `B.load_registry(SRC, with_scene=False)` 导入原工程全部精灵（会 chdir，前后保存 / 恢复 cwd）；
2. import 我们的 art_* 模块（import 即注册新精灵；每个模块的 NEW 列表 = 它注册的名字），
   **断言新名字不和原 166 个重名**（D12），新动作的播放方式补进 B.ONESHOT / B.STATIC_STATES，
   新角色名补进 B.CHAR_INFO（只改内存里的字典）；
3. 对受影响的 cid 用 `B.bake_character(cid, acts, portraits, [], chars_dir, 4)` 烘成和 角色图集 同格式
   （<cid>\\<cid>.png / .json / 头像\\*.png / <cid>_预览.png），`B.verify` 回读逐像素 + `B.verify_engine`
   与原引擎 sprite.draw（含翻转）逐像素比对，都必须 0 错；
4. 新道具：art_props.PROPS + draw_<id>(frame) → assets\\props_new\\<id>.png（横向帧条）+ 一个 props_new.json
   （格式同 道具目录.json；同时写 `sprites` 和 `props` 两个键，内容相同），回读核对，断言不和原 35 个重名；
   场景专用替换图：art_joseph.scene_overrides → assets\\props_new\\scene\\<原文件名>（二乔三张场景图换新脸，
   build_assets 的 props 步优先用它；原图只读不动）；
5. 核对 amap.AMAP 的每个真名都在该图集的 animations 里；
6. 4 倍预览：tools\\art\\_preview\\<cid>.png（新动作和 idle 并排）、props_new.png。

out_dir：None = 游戏\\assets；目录名是 chars_new 时直接当角色输出目录（道具写同级的 props_new）；
否则角色写 out_dir\\chars_new、道具写 out_dir\\props_new。
缓存：输出都在、且比全部输入（tools\\art\\*.py、bake_characters.py、源码 assets\\*.py、engine\\sprite.py）新，
就直接返回上一次的报告（c['force'] 或 force=True 时全做）。

单独运行：  $env:PYTHONDONTWRITEBYTECODE=1; python -B tools\\art\\bake_art.py [--force] [--no-preview]
"""
import sys
sys.dont_write_bytecode = True               # 必须在 import 原工程之前

import os
import json
import time
import glob
import hashlib
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import art_common as AC                       # noqa: E402  （设好 sys.path：ART、烘焙脚本、源码）

import numpy as np                            # noqa: E402
from PIL import Image, ImageDraw              # noqa: E402

# import 顺序 = 注册顺序；不存在的模块跳过（并行阶段可能还没写），存在但出错 = 直接抛出
ART_MODULES = ['art_heroes', 'art_stands', 'art_enemies', 'art_npc', 'art_new_grayfly'] + [
    'art_new_' + cid for cid in (
        'fake_tennille', 'anne', 'devo', 'rubbersoul', 'nena', 'zz', 'cameo', 'chaka', 'khan',
        'kennyg', 'nukesaku', 'wilson', 'npc_sailor', 'npc_kid', 'npc_townsfolk', 'npc_villager_f',
        'npc_islander', 'npc_dealer', 'polnareff_kid', 'jotaro_kid', 'polnareff_possessed',
        'clay_sherry', 'clay_gold', 'clay_pol', 'atum','npc_spw','npc_merchant')
] + ['art_later_creatures', 'art_later_existing', 'art_dialogue_heads', 'art_joseph']
PROPS_MODULE = 'art_props'
JOTARO_ADULT = False          # True = 用 art_jotaro_redraw 的成年小头承太郎（用户 2026-10-09 晚要回卡通大头，关掉）
REPORT_PATH = os.path.join(AC.PREVIEW, 'bake_report.json')


class BakeError(RuntimeError):
    pass


def playback_names(module, field):
    """局部动作声明只影响本模块注册的精灵，避免攻击被烘成循环或串改其他角色。"""
    declared = set(getattr(module, field, ()))
    full = {name for name in declared if '.' in name}
    short = declared - full
    return full | {name for name in getattr(module, 'NEW', ())
                   if name.split('.', 1)[-1] in short}


# ============================================================================ 原名单（只读）
def original_names():
    """原 166 个精灵名：角色图集 每个 cid 的 animations + aliases，加 道具目录 的 35 个 prop.*。"""
    names, props = set(), set()
    cat = json.load(open(os.path.join(AC.ATLAS_DIR, 'catalog.json'), encoding='utf-8'))
    for c in cat:
        m = json.load(open(os.path.join(AC.ATLAS_DIR, c['id'], c['id'] + '.json'), encoding='utf-8'))
        for k in list(m['animations']) + list(m['aliases']):
            names.add(f"{c['id']}.{k}")
    pc = json.load(open(os.path.join(AC.ATLAS_DIR, '道具', '道具目录.json'), encoding='utf-8'))
    for s in pc['sprites']:
        names.add(s['sprite'])
        props.add(s['id'])
    return names, props, [c['id'] for c in cat]


def original_atlas(cid):
    p = os.path.join(AC.ATLAS_DIR, cid, cid + '.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


# ============================================================================ 缓存
def _inputs():
    files = glob.glob(os.path.join(HERE, '*.py'))
    files.append(os.path.join(AC.BAKE_DIR, 'bake_characters.py'))
    files += glob.glob(os.path.join(AC.SRC, 'assets', '*.py'))
    files.append(os.path.join(AC.SRC, 'engine', 'sprite.py'))
    return [f for f in files if os.path.exists(f)]


def _cached(chars_dir, props_dir):
    if not os.path.exists(REPORT_PATH):
        return None
    try:
        rep = json.load(open(REPORT_PATH, encoding='utf-8'))
    except Exception:
        return None
    outs = [REPORT_PATH, os.path.join(props_dir, 'props_new.json')]
    outs += [os.path.join(chars_dir, cid, cid + '.json') for cid in rep.get('chars', {})]
    outs += [os.path.join(props_dir, 'scene', f) for f in rep.get('scene_overrides', [])]
    if not all(os.path.exists(o) for o in outs):
        return None
    if rep.get('chars_dir') != os.path.abspath(chars_dir) or rep.get('props_dir') != os.path.abspath(props_dir):
        return None
    if min(os.path.getmtime(o) for o in outs) <= max(os.path.getmtime(i) for i in _inputs()):
        return None
    rep['cached'] = True
    return rep


# ============================================================================ 主流程
def _dirs(out_dir):
    if out_dir is None:
        out_dir = os.path.join(AC.GAME, 'assets')
    out_dir = os.path.abspath(out_dir)
    if os.path.basename(out_dir).lower() == 'chars_new':
        return out_dir, os.path.join(os.path.dirname(out_dir), 'props_new')
    return os.path.join(out_dir, 'chars_new'), os.path.join(out_dir, 'props_new')


def _guard_out(path):
    """绝不往受保护目录写。"""
    p = os.path.abspath(path).lower()
    for bad in (AC.SRC, AC.ATLAS_DIR, AC.BAKE_DIR, os.path.join(AC.ROOT, '剧情分镜'), os.path.join(AC.ROOT, '音频'),
                r'D:\大疆\游戏素材\银魂', r'D:\CodeWorkSpace\gintama-pixel-game'):
        b = os.path.abspath(bad).lower()
        if p == b or p.startswith(b + os.sep):
            raise BakeError(f'输出目录落在受保护目录里：{path}')


def run(out_dir=None, c=None, force=False, previews=True):
    c = c or {}
    log = c.get('log') or print
    force = force or bool(c.get('force'))
    chars_dir, props_dir = _dirs(out_dir)
    for d in (chars_dir, props_dir, AC.PREVIEW):
        _guard_out(d)
    if not force:
        rep = _cached(chars_dir, props_dir)
        if rep:
            log(f'[art] 缓存有效，跳过（{len(rep["chars"])} 个图集、{len(rep["props"])} 个道具）')
            return rep
    t0 = time.time()
    os.makedirs(chars_dir, exist_ok=True)
    os.makedirs(props_dir, exist_ok=True)

    orig, orig_props, orig_cids = original_names()
    if len(orig) != 166:
        raise BakeError(f'原精灵名单应为 166 个，读到 {len(orig)}')

    # ---- 1. 原工程精灵（load_registry 会 chdir）
    import bake_characters as B
    cwd = os.getcwd()
    try:
        B.load_registry(AC.SRC, with_scene=False)
    finally:
        os.chdir(cwd)
    from engine import sprite
    missing = [n for n in orig if n not in sprite._REG]
    if missing:
        raise BakeError(f'原工程精灵没有全部注册：{sorted(missing)[:8]}…')

    # ---- 2. 我们的模块
    mods, new, owner = [], [], {}
    for mn in ART_MODULES:
        if not os.path.exists(os.path.join(HERE, mn + '.py')):
            log(f'[art] 跳过不存在的模块 {mn}.py')
            continue
        m = importlib.import_module(mn)
        mods.append(m)
        for n in getattr(m, 'NEW', []):
            if n in owner:
                raise BakeError(f'{n} 被 {owner[n]} 和 {mn} 重复注册')
            owner[n] = mn
            new.append(n)
    clash = sorted(set(new) & orig)
    if clash:
        raise BakeError(f'新精灵名和原 166 个重名（D12）：{clash}')
    bad = [n for n in new if n.count('.') != 1 or n.startswith('prop.') or n not in sprite._REG]
    if bad:
        raise BakeError(f'新精灵名不合规（应为 <cid>.<动作>、已注册、不是 prop.*）：{bad}')
    for m in mods:
        B.ONESHOT |= playback_names(m, 'ONESHOT')
        B.STATIC_STATES |= playback_names(m, 'STATIC_STATES')
        for cid, info in getattr(m, 'CHAR_INFO', {}).items():
            B.CHAR_INFO[cid] = dict(info)
        B.ACTION_ZH.update(getattr(m, 'ACTION_ZH', {}))
    affected = []
    for n in new:
        cid = n.split('.')[0]
        if cid not in affected:
            affected.append(cid)
    new_cids = [cid for cid in affected if cid not in orig_cids]
    unnamed = [cid for cid in new_cids if cid not in B.CHAR_INFO]
    if unnamed:
        raise BakeError(f'新角色没有在模块的 CHAR_INFO 里登记名字：{unnamed}')

    # 用户指定的成年形象重画在新增名审计之后进行，避免放宽 D12 的原名保护。
    #   2026-10-09 晚用户改回：“承太郎修改为重绘之前的卡通大头形象”——JOTARO_ADULT 关掉，art_jotaro_redraw.py 留着不删；
    #   落水只露半个头的 jotaro.float 由 art_later_existing 用原来的大头生成，不受影响
    redrawn = []
    if JOTARO_ADULT:
        import art_jotaro_redraw
        redrawn = art_jotaro_redraw.apply()
    # 荷莉的头往前挪（用户 2026-10-09）：同样在审计之后显式替换；荷莉原来没有新动作，要手动加进受影响的 cid
    import art_holly_fix
    redrawn += art_holly_fix.apply()
    # 二乔的脸照对话框头像、指人手臂分段（用户 2026-10-09 晚）：原图集的 idle / walk / run / camera / point 同样在审计之后替换，
    # 再用新 idle 重算 float / dodge（新动作 vine_* / whip / guard 在 art_joseph import 时已注册）
    import art_joseph
    redrawn += art_joseph.apply()
    for n in redrawn:
        if n.split('.')[0] not in affected:
            affected.append(n.split('.')[0])
    # 二乔的三张场景专用图（序章荷莉病床跪坐 / 伸手、终章挥手）跟着换新脸（2026-10-10）：用原场景脚本的生成函数按新 idle 重做，
    # 写到 props_new\scene\（原图只读；先断言用原 idle 复现得出原图）。build_assets 的 props 步见到同名替换图就用它
    scene_files = art_joseph.scene_overrides(os.path.join(props_dir, 'scene'))

    # ---- 3. 烘焙受影响的 cid（原有全部动作 + 新动作）
    names = sorted(n for n in (orig | set(new)) if n.split('.')[0] in affected)
    base2 = {n: B.Spr(n, sprite.get(n), 'game.' + owner.get(n, 'orig')) for n in names}
    chars, _ = B.build_actions(base2)
    baked = []
    for cid in affected:
        acts, portraits = chars[cid]
        b = B.bake_character(cid, acts, portraits, [], chars_dir, AC.SCALE)
        baked.append(b)
        if max(b['cell'][0] * b['cols'], b['cell'][1] * b['rows']) > 4096:
            raise BakeError(f'{cid} 图集超过 4096 px（银魂坑 A11）')
    errors, n_frames = B.verify(chars_dir, baked, [], {}, [], {})
    eng_n, eng_bad, eng_skip = B.verify_engine(baked)
    if errors or eng_bad:
        raise BakeError(f'校验失败：回读 {errors} 错、与引擎比对 {eng_bad} 不一致')

    # ---- 4. 新道具
    props_rep, prop_frames = bake_props(props_dir, orig_props, log)

    # ---- 5. amap 核对
    amap_errors = check_amap(chars_dir, affected)
    if amap_errors:
        raise BakeError('amap 指向不存在的动作：' + '；'.join(amap_errors))

    # ---- 6. 预览
    prev = []
    if previews:
        for b in baked:
            prev.append(preview_cid(b, set(new), b['id'] in new_cids))
        if prop_frames:
            prev.append(preview_props(prop_frames))

    rep = {
        'built': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'chars_dir': os.path.abspath(chars_dir), 'props_dir': os.path.abspath(props_dir),
        'new_names': sorted(new), 'new_cids': new_cids, 'redrawn_names': redrawn, 'scene_overrides': scene_files,
        'chars': {b['id']: {'cell': b['cell'], 'pivot': b['pivot'], 'animations': b['animations'],
                            'expressions': b['expressions'], 'aliases': b['aliases'],
                            'new': sorted(n.split('.', 1)[1] for n in new if n.split('.')[0] == b['id'])}
                  for b in baked},
        'props': props_rep,
        'verify': {'frames': n_frames, 'errors': errors, 'engine_draws': eng_n, 'engine_bad': eng_bad,
                   'engine_skipped_half_px_flips': eng_skip},
        'amap_errors': amap_errors, 'previews': prev,
        'seconds': round(time.time() - t0, 2),
    }
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    log(f'[art] {len(new)} 个新精灵 → {len(baked)} 个图集（新角色 {len(new_cids)}）；'
        f'新道具 {len(props_rep)}；场景专用替换图 {len(scene_files)}；回读 {n_frames} 帧 0 错，引擎比对 {eng_n} 次 0 不一致；{rep["seconds"]} s')
    return rep


# ============================================================================ 道具
def bake_props(props_dir, orig_props, log=print):
    path = os.path.join(HERE, PROPS_MODULE + '.py')
    if not os.path.exists(path):
        log('[art] 还没有 art_props.py，跳过新道具')
        return [], []
    P = importlib.import_module(PROPS_MODULE)
    entries, frames_all, seen = [], [], set()
    for spec in P.PROPS:
        pid = spec['id']
        if pid in orig_props:
            raise BakeError(f'新道具 {pid} 和原 35 个道具重名')
        if pid in seen:
            raise BakeError(f'新道具 {pid} 重复')
        seen.add(pid)
        fn = getattr(P, 'draw_' + pid)
        w, h = spec['size']
        frames = [fn(i).convert('RGBA') for i in range(spec['frames'])]
        for i, f in enumerate(frames):
            if f.size != (w, h):
                raise BakeError(f'道具 {pid} 帧 {i} 尺寸 {f.size} ≠ 声明的 {(w, h)}')
            if not f.getbbox():
                raise BakeError(f'道具 {pid} 帧 {i} 是空的')
        strip = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
        for i, f in enumerate(frames):
            strip.paste(f, (i * w, 0))
        file = f'{pid}.png'
        strip.save(os.path.join(props_dir, file), optimize=True)
        back = np.array(Image.open(os.path.join(props_dir, file)).convert('RGBA'))
        for i, f in enumerate(frames):
            if not np.array_equal(back[:, i * w:(i + 1) * w], np.array(f)):
                raise BakeError(f'道具 {pid} 帧 {i} 回读不一致')
        px, py = spec['pivot']
        e = {'id': pid, 'name': spec.get('name', pid), 'sprite': 'prop_new.' + pid, 'file': file,
             'frames': len(frames), 'size': [w, h],
             'anchor': spec.get('anchor', [px, py]), 'anchor_semantic': spec.get('anchor_semantic', ''),
             'pivot': [px, py], 'fps': spec.get('fps', 1), 'kind': spec.get('kind', 'static'),
             'desc': spec.get('desc', '')}
        if len(frames) > 1 and e['kind'] == 'static':
            e['note'] = '多帧为不同状态（按序号取帧，不自动播放），见 desc'
        entries.append(e)
        frames_all.append((e, frames))
    note = ('包 7A 新画的道具（tools\\art\\art_props.py）。file 是横向帧条（帧从左到右紧挨，每帧 size 大小）；'
            'pivot=锚点在单帧内的像素坐标；kind=static 且 frames>1 表示多个状态（按序号取帧）。'
            '格式同 角色图集\\道具\\道具目录.json；props 和 sprites 两个键内容相同。')
    with open(os.path.join(props_dir, 'props_new.json'), 'w', encoding='utf-8') as f:
        json.dump({'work': 'JoJo', 'note': note, 'props': entries, 'sprites': entries}, f,
                  ensure_ascii=False, indent=1)
    return entries, frames_all


# ============================================================================ amap 核对
def atlas_meta(chars_dir, cid, affected):
    if cid in affected:
        p = os.path.join(chars_dir, cid, cid + '.json')
        if os.path.exists(p):
            return json.load(open(p, encoding='utf-8'))
    return original_atlas(cid)


def check_amap(chars_dir, affected):
    import amap
    errs = []
    for cid, table in amap.AMAP.items():
        meta = atlas_meta(chars_dir, cid, affected)
        if meta is None:
            errs.append(f'{cid}: 没有这个图集')
            continue
        anims = meta['animations']
        for logical, v in table.items():
            real = amap.target(v)
            if real not in anims:
                errs.append(f'{cid}.{logical} → {real}（{"在 aliases 里" if real in meta["aliases"] else "不存在"}）')
                continue
            if isinstance(v, dict) and v.get('f') is not None and not (0 <= v['f'] < anims[real]['frames']):
                errs.append(f'{cid}.{logical} → {real} 帧 {v["f"]} 越界')
    return errs


# ============================================================================ 预览
def _frames_from_atlas(b, action):
    """从 bake_character 的结果里取某动作的 cell 帧（已按 pivot 对齐）。"""
    for a, placed in b['kept']:
        if a['action'] == action:
            return placed
    return None


def preview_cid(b, new_names, is_new):
    """新动作和 idle 并排的 4 倍预览：每格都是图集 cell（按 pivot 对齐，洋红十字 = pivot）。"""
    cid = b['id']
    pv = tuple(b['pivot'])
    items = []
    if is_new:
        show = [a['action'] for a, _ in b['kept']]
    else:
        new_acts = [n.split('.', 1)[1] for n in sorted(new_names) if n.split('.')[0] == cid]
        first = 'idle' if _frames_from_atlas(b, 'idle') else b['kept'][0][0]['action']
        show = [first] + [a for a in new_acts if a != first]
    for act in show:
        placed = _frames_from_atlas(b, act)
        if placed is None:
            continue
        mark = '' if (is_new or f'{cid}.{act}' in new_names) else ' (原)'
        for i, im in enumerate(placed):
            items.append((f'{act}[{i}]{mark}', AC.crop_keep_pivot(im, pv)))
    path = os.path.join(AC.PREVIEW, f'{cid}.png')
    title = f"{cid}  {b['info']['zh']}  cell {b['cell'][0]}x{b['cell'][1]}  pivot {pv}  ×{AC.SCALE}"
    AC.preview_items([(lab, im, anc) for lab, (im, anc) in items], path, title)
    return path


def preview_props(prop_frames):
    items = []
    for e, frames in prop_frames:
        for i, f in enumerate(frames):
            items.append((f"{e['id']}[{i}]", f, tuple(e['pivot'])))
    path = os.path.join(AC.PREVIEW, 'props_new.png')
    AC.preview_items(items, path, f'新道具 {len(prop_frames)} 个（×{AC.SCALE}，洋红十字 = pivot）', bg_ground=False)
    return path


# ============================================================================
if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    args = sys.argv[1:]
    rep = run(force='--force' in args, previews='--no-preview' not in args)
    print(json.dumps({k: rep[k] for k in ('new_cids', 'verify', 'amap_errors', 'seconds')}, ensure_ascii=False))
    print('图集：', ', '.join(f"{k} {v['cell'][0]}x{v['cell'][1]}" for k, v in rep['chars'].items()))
    print('道具：', ', '.join(e['id'] for e in rep['props']))
