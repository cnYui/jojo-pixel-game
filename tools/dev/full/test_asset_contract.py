"""全章资源契约审查：比对实际图像、动作、头像、音频、特效与字库，不用运行时回退掩盖缺项。"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
META = GAME / 'tools' / '_meta'
STR = r'''(?:'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`)'''
VALUE = rf'(?P<value>{STR})(?!\s*\+)'


def read_json(name):
    return json.loads((META / (name + '.json')).read_text(encoding='utf-8'))


def literal(s):
    # 模板插值属于运行时表达式，静态审查不猜其结果。
    if s.startswith('`') and '${' in s:
        return None
    return re.sub(r'\\([\\\'"`])', r'\1', s[1:-1])


def strip_comments(s):
    return re.sub(rf'{STR}|//[^\n]*|/\*[\s\S]*?\*/',
                  lambda m: m[0] if m[0][0] in "'\"`" else
                  ''.join('\n' if c == '\n' else ' ' for c in m[0]), s)


def balanced(s, start):
    """s[start] 是 '{'：返回到配对 '}' 为止的整段（跳过字符串里的括号）；配不上就返回到文件尾。"""
    depth, i, n = 0, start, len(s)
    while i < n:
        c = s[i]
        if c in "'\"`":
            m = re.match(STR, s[i:])
            i += len(m[0]) if m else 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return s[start:i + 1]
        i += 1
    return s[start:]


def top_level(obj):
    """只留对象字面量最外一层的文字（内层 {...} 整段换成空格），字符串原样保留。"""
    out, depth, i, n = [], 0, 0, len(obj)
    while i < n:
        c = obj[i]
        if c in "'\"`":
            m = re.match(STR, obj[i:])
            tok = m[0] if m else c
            if depth <= 1:
                out.append(tok)
            i += len(tok)
            continue
        if c == '{':
            depth += 1
            out.append(c if depth == 1 else ' ')
        elif c == '}':
            out.append(c if depth == 1 else ' ')
            depth -= 1
        else:
            out.append(c if depth <= 1 else ' ')
        i += 1
    return ''.join(out)


def image_refs(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('image', 'images'):
                if isinstance(v, str):
                    yield v
                elif isinstance(v, list):
                    yield from (x for x in v if isinstance(x, str))
            elif isinstance(v, (dict, list)):
                yield from image_refs(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from image_refs(v)


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(GAME / 'tools' / 'dev' / 'full' / 'asset_contract_report.json'))
    args = parser.parse_args()
    chars_meta, props_meta = read_json('chars'), read_json('props')
    chars, props, scene = chars_meta['chars'], props_meta['props'], props_meta.get('scene', {})
    bg, ui, font, audio, idx = [read_json(n) for n in ('bg', 'ui', 'font', 'audio', 'img_index')]
    errors, warnings, counts, refs = [], [], {}, []
    seen = set()

    def issue(kind, key, where, detail='', warning=False):
        record = dict(kind=kind, key=key, where=where, detail=detail)
        unique = (kind, key, where, detail, warning)
        if unique not in seen:
            seen.add(unique)
            (warnings if warning else errors).append(record)

    def where(path, text, off):
        return str(path.relative_to(GAME)).replace('\\', '/') + ':' + str(text.count('\n', 0, off) + 1)

    def check_ref(kind, value, location):
        counts[kind] = counts.get(kind, 0) + 1
        refs.append(dict(kind=kind, key=value, where=location))
        exists = True
        if kind in ('角色', '说话人'):
            if value.startswith('prop:'):
                exists = value[5:] in props
            elif value.startswith('scene:'):
                exists = value[6:] in scene
            else:
                exists = value in chars
        elif kind == '道具':
            exists = value[6:] in scene if value.startswith('scene:') else value.removeprefix('prop:') in props
        elif kind == '背景':
            exists = value in bg or value in ('black', 'menace', 'radial') or value.startswith('#')
        elif kind == '特效':
            exists = value in fx_names
        elif kind == '音效':
            exists = value in sfx_names
        elif kind == '配乐':
            exists = value in audio['music']
        elif kind == '地图':
            exists = value in stage_names
        elif kind.startswith('界面:'):
            exists = value in ui.get(kind[3:], {})
        if not exists:
            issue(kind, value, location)

    def check_action(cid, action, location, frame=None):
        if cid not in chars:
            return
        m = chars[cid]
        target = m.get('amap', {}).get(action, action)
        fixed = target.get('f') if isinstance(target, dict) else None
        real = target['a'] if isinstance(target, dict) else target
        real = m.get('aliases', {}).get(real, real)
        a = m['animations'].get(real)
        counts['动作'] = counts.get('动作', 0) + 1
        if a is None:
            issue('动作', cid + '.' + action, location, '不能经实际 amap / animations / aliases 解析')
        elif fixed is not None and not 0 <= fixed < a['frames']:
            issue('动作帧', cid + '.' + action, location, str(fixed))
        elif frame is not None and not 0 <= frame < a['frames']:
            issue('显式动作帧', cid + '.' + action, location, str(frame))

    def check_head(cid, expression, location):
        if cid not in chars:
            return
        m = chars[cid]
        target = m.get('headAlias', {}).get(expression, expression)
        if not m.get('heads', {}).get(target):
            issue('头像', cid + ':' + expression, location)

    sources = [(p, strip_comments(p.read_text(encoding='utf-8'))) for folder in ('story', 'engine')
               for p in sorted((GAME / folder).glob('*.js'))]
    sources += [(GAME / 'main.js', strip_comments((GAME / 'main.js').read_text(encoding='utf-8')))]
    fx_names = set()
    for p, s in sources:
        if p.name.startswith('fx'):
            fx_names.update(re.findall(r'\b(?:FX|F)\.([A-Za-z_]\w*)\s*=', s))
    sfx_names = set(audio['sfx']) | {m['group'] for m in audio['sfx'].values() if m.get('group')}
    stage_names = set()
    for p, s in sources:
        if p.name.startswith('stages'):
            stage_names.update(re.findall(r'\b(?:ST|STAGES|G\.STAGES)\.([\w]+)\s*=', s))
            stage_names.update(re.findall(rf'\b(?:stage|add)\(\s*({STR})', s))
    stage_names = {literal(n) if n[:1] in "'\"`" else n for n in stage_names}
    # 地图是纯数据注册，真实求值可以覆盖循环登记与 Object.assign；章节流程不在此执行。
    stage_files = [str(p) for p, _ in sources if p.name.startswith('stages')]
    stage_js = '''const fs=require('fs'),vm=require('vm');
const G={STAGES:{},NAMES:{}},context=vm.createContext({window:{G}});
for(const p of JSON.parse(process.argv[1]))vm.runInContext(fs.readFileSync(p,'utf8'),context,{filename:p,timeout:1000});
process.stdout.write(JSON.stringify(G.STAGES));'''
    stage_result = subprocess.run(['node', '-e', stage_js, json.dumps(stage_files)], cwd=GAME,
                                  capture_output=True, text=True, encoding='utf-8', timeout=10)
    if stage_result.returncode:
        issue('地图注册执行', 'stages', 'story/stages*.js', stage_result.stderr.strip())
    else:
        stage_registry = json.loads(stage_result.stdout)
        stage_names.update(stage_registry)
        for sid, m in stage_registry.items():
            if m.get('bg'):
                check_ref('背景', m['bg'], '地图注册:' + sid)
            if m.get('music'):
                check_ref('配乐', m['music'], '地图注册:' + sid)
            ambient = m.get('ambient')
            if isinstance(ambient, str):
                check_ref('音效', ambient, '地图注册:' + sid)
            elif isinstance(ambient, dict) and ambient.get('name'):
                check_ref('音效', ambient['name'], '地图注册:' + sid)

    patterns = [
        ('角色', rf'\b(?:cid|lead)\s*:\s*{VALUE}'),
        ('角色', rf'(?<!fx)\.spawn\(\s*{VALUE}'),
        ('说话人', rf'\.say\(\s*{VALUE}'),
        ('道具', rf'\.prop\(\s*\w+\s*,\s*{VALUE}'),
        ('背景', rf'\bbg\s*:\s*{VALUE}'),
        ('特效', rf'\.(?:fx|fxAt)\(\s*{VALUE}'),
        ('特效', rf'\bFX\(\s*{VALUE}'),
        ('音效', rf'(?<!uifx)\.sfx\(\s*{VALUE}'),
        ('音效', rf'\b(?:G\.audio|A)\.loop\(\s*{VALUE}'),
        ('音效', rf'(?<![\w.])sfx\(\s*{VALUE}'),
        ('音效', rf'\b(?:sfxHit|sfx|summonSfx|ambient)\s*:\s*{VALUE}'),
        ('配乐', rf'\.music\(\s*{VALUE}'),
        ('配乐', rf'\bmusic\s*:\s*{VALUE}'),
        ('地图', rf'\.setStage\(\s*{VALUE}'),
        ('界面:titles', rf'\.title\(\s*{VALUE}'),
        ('界面:chapters', rf'\.chapterCard\(\s*{VALUE}'),
        ('界面:namecards', rf'\.nameCard\(\s*{VALUE}'),
        ('界面:standcards', rf'\.standCard\(\s*{VALUE}'),
        ('界面:locations', rf'\.location\(\s*{VALUE}'),
        ('界面:locations', rf'\blocation\s*:\s*{VALUE}'),   # L.explore 的 o.location（进图后放地点卡）
        ('界面:vs', rf'\bvs\s*:\s*{VALUE}'),
        # 拟声字：G.uifx.sfx / S.sfxText / combat.js 的 word() 都查 ui.sfx 的预渲染图
        ('界面:sfx', rf'\buifx\.sfx\(\s*{VALUE}'),
        ('界面:sfx', rf'\.sfxText\(\s*{VALUE}'),
        ('界面:sfx', rf'(?<![\w.])word\(\s*{VALUE}'),
    ]
    for path, s in sources:
        # 资源定义自身不算调用，内部同名变量不能误判为图集/音效。
        scan = not (path.name in ('atlas.js', 'audio.js', 'fx.js', 'fx_mid.js', 'ui_cards.js'))
        if scan:
            for kind, pattern in patterns:
                for m in re.finditer(pattern, s):
                    value = literal(m['value'])
                    if value is not None:
                        # tape/duck/none 是时停音乐处理策略，由 audio.timestop 消费，不是配乐 key。
                        if kind == '配乐' and value in ('tape', 'duck', 'none') and not '.music(' in m[0]:
                            continue
                        check_ref(kind, value, where(path, s, m.start()))
            for m in re.finditer(rf'\bmap\(\s*{STR}\s*,\s*{VALUE}', s):
                value = literal(m['value'])
                if value is not None:
                    check_ref('背景', value, where(path, s, m.start()))
            # —— 运行时动态取的界面图（以前只在实际跑到时才记 missingImg）——
            # 时停台词：G.time.stop(by, { lines: { start, end } }) → timestop.js 用 G.uifx.title 放 ui.titles
            for m in re.finditer(r'\blines\s*:\s*\{([^{}]*)\}', s):
                for k in re.finditer(rf'\b(?:start|end)\s*:\s*{VALUE}', m[1]):
                    value = literal(k['value'])
                    if value is not None:
                        check_ref('界面:titles', value, where(path, s, m.start()))
            # 时停里的「チク…」「タク…」这类三元表达式拟声字
            for m in re.finditer(rf'\buifx\.sfx\(\s*[^,()]*\?\s*({STR})\s*:\s*({STR})', s):
                for g in (1, 2):
                    value = literal(m[g])
                    if value is not None:
                        check_ref('界面:sfx', value, where(path, s, m.start()))
            # W6 敌人切入：warn: { tier: 'W6', title } → ui.titles
            for m in re.finditer(r'\bwarn\s*:\s*\{([^{}]*)\}', s):
                if re.search(r"\btier\s*:\s*['\"]W6['\"]", m[1]):
                    t = re.search(rf'\btitle\s*:\s*{VALUE}', m[1])
                    if t and literal(t['value']) is not None:
                        check_ref('界面:titles', literal(t['value']), where(path, s, m.start()))
            # 切入：敌人（enemy: true / bossCutin）查 ui.titles，主角查 ui.specials
            for m in re.finditer(r'\b(cutin|bossCutin)\(\s*\{', s):
                top = top_level(balanced(s, m.end() - 1))
                t = re.search(rf'\btitle\s*:\s*{VALUE}', top)
                if t and literal(t['value']) is not None:
                    enemy = m[1] == 'bossCutin' or re.search(r'\benemy\s*:\s*true', top)
                    check_ref('界面:titles' if enemy else '界面:specials', literal(t['value']), where(path, s, m.start()))
            # 必杀 / 剧情专用 U：切入大字 = title || name（combat.special），title 写 null 时退到 name；getter 是运行时值，跳过
            for m in re.finditer(r'\bspecial\s*:\s*\{', s):
                top = top_level(balanced(s, m.end() - 1))
                if re.search(r'\bget\s+title\s*\(', top):
                    continue
                t = re.search(rf'\btitle\s*:\s*({STR}|null)', top)
                n = re.search(rf'\bname\s*:\s*({STR})(?!\s*\+)', top)
                key = literal(t[1]) if t and t[1] != 'null' else literal(n[1]) if n else None
                if key:
                    check_ref('界面:specials', key, where(path, s, m.start()))
            # 剧情里直接放的 VS 卡：S.vs({ key })
            for m in re.finditer(r'\.vs\(\s*\{', s):
                top = top_level(balanced(s, m.end() - 1))
                k = re.search(rf'\bkey\s*:\s*{VALUE}', top)
                if k and literal(k['value']) is not None:
                    check_ref('界面:vs', literal(k['value']), where(path, s, m.start()))
            for m in re.finditer(rf'\.sprite\(\s*\w+\s*,\s*({STR})\s*,\s*({STR})(?:\s*,\s*(\d+))?', s):
                cid, action = literal(m[1]), literal(m[2])
                if cid is not None and action is not None:
                    check_ref('角色', cid, where(path, s, m.start()))
                    check_action(cid, action, where(path, s, m.start()), int(m[3]) if m[3] else None)
            for m in re.finditer(rf'\.(pose|standAct)\(\s*({STR})\s*,\s*({STR})', s):
                cid, action = literal(m[2]), literal(m[3])
                if cid is None or action is None:
                    continue
                if m[1] == 'standAct':
                    cid = chars_meta.get('heroes', {}).get(cid, {}).get('stand')
                if cid in chars:
                    check_action(cid, action, where(path, s, m.start()))
            # 同一叶对象的 cid/anim/expr 配对；嵌套对象和变量 cid 留给实际运行快照。
            for m in re.finditer(r'\{[^{}]*\}', s):
                obj = m[0]
                c = re.search(rf'\bcid\s*:\s*({STR})(?!\s*\+)', obj)
                if not c:
                    # 战斗 spec 有 cid 时 actor 是身份ID；没有 cid 才用 actor 建角色。
                    actor = re.search(rf'\bactor\s*:\s*({STR})(?!\s*\+)', obj)
                    if actor and literal(actor[1]) is not None:
                        check_ref('角色', literal(actor[1]), where(path, s, m.start()))
                    continue
                cid = literal(c[1])
                if cid is None:
                    continue
                act = re.search(rf'\banim\s*:\s*({STR})', obj)
                if act:
                    action = literal(act[1])
                    if action is not None:
                        check_action(cid, action, where(path, s, m.start()))
                expr = re.search(rf'\bexpr\s*:\s*({STR})', obj)
                if expr:
                    expression = literal(expr[1])
                    if expression is not None:
                        check_head(cid, expression, where(path, s, m.start()))
            for m in re.finditer(rf'\.say\(\s*({STR})\s*,\s*{STR}\s*(?:,\s*\{{([^{{}}]*)\}})?', s):
                cid = literal(m[1])
                options = m[2] or ''
                if cid is not None and not re.search(r'\bportrait\s*:\s*false', options):
                    ex = re.search(rf'\bexpr\s*:\s*({STR})', options)
                    check_head(cid, literal(ex[1]) if ex else 'normal', where(path, s, m.start()))
            # 台词数组由 lines 助手逐行调用 say，必须和直接 say 一样审查头像。
            for m in re.finditer(rf'\[\s*({STR})\s*,\s*({STR})\s*[,\]]', s):
                cid = literal(m[1])
                if cid is not None and cid in chars:
                    check_ref('说话人', cid, where(path, s, m.start()))
                    check_head(cid, 'normal', where(path, s, m.start()))

    # 所有实际图像均须可读，元数据边界不能越出图集；仅存在登记项不构成通过。
    from PIL import Image
    for key, m in idx.items():
        fp = GAME / 'assets' / m['file']
        if not fp.is_file():
            issue('图片文件', key, 'tools/_meta/img_index.json', str(fp))
    for group, obj in [('角色', chars), ('道具', props), ('场景', scene), ('背景', bg), ('界面', ui), ('字库', font)]:
        for image in image_refs(obj):
            if image not in idx:
                issue('图片登记', image, group)
    for cid, m in chars.items():
        im = idx.get(m['image'])
        if not im or not (GAME / 'assets' / im['file']).is_file():
            continue
        with Image.open(GAME / 'assets' / im['file']) as image:
            for a, spec in m['animations'].items():
                if spec['frames'] * m['cell'][0] > image.width or (spec['row'] + 1) * m['cell'][1] > image.height:
                    issue('图集越界', cid + '.' + a, 'tools/_meta/chars.json')
        for logical in m.get('amap', {}):
            check_action(cid, logical, 'tools/_meta/chars.json')
        for expression, keys in m.get('heads', {}).items():
            for key in keys:
                if key not in idx:
                    issue('头像图片', cid + ':' + expression, 'tools/_meta/chars.json', key)
    for name, music in audio['music'].items():
        f = music.get('file')
        if f and not (GAME / f).is_file():
            issue('配乐文件', name, 'tools/_meta/audio.json', f)

    # 与构建器使用同一收字范围，独立对照实际两档 glyph 表；不会因漏扫新章节而误报通过。
    sys.path.insert(0, str(GAME / 'tools'))
    spec = importlib.util.spec_from_file_location('jojo_build_font_audit', GAME / 'tools' / 'build_assets.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    B = SimpleNamespace(game=str(GAME), registry=str(GAME / 'tools' / 'registry'),
                        load_meta=lambda n, default=None: read_json(n), warn=lambda msg: issue('收字', msg, '构建器'))
    used = builder.collect_font_chars(B)
    for size in ('12', '16'):
        glyphs = font.get(size, {}).get('glyphs', {})
        for ch, source in used.items():
            if ch not in '\n\r\t' and (ch.isprintable() or ch == '\u3000') and ch not in glyphs:
                issue('字库' + size, ch, source, 'U+' + format(ord(ch), '04X'))

    chapters = ['prologue'] + ['ch' + str(n).zfill(2) for n in range(1, 12)] + ['final']
    for name in chapters:
        p = GAME / 'story' / (name + '.js')
        if not p.is_file():
            issue('章节文件', name, 'story')
        elif not re.search(r'G\.STORY\s*\[|G\.STORY\.', strip_comments(p.read_text(encoding='utf-8'))):
            issue('章节注册', name, 'story/' + name + '.js')
    report = dict(ok=not errors, errors=errors, warnings=warnings, counts=counts, refs=refs,
                  assets=dict(chars=len(chars), props=len(props), scene=len(scene), bg=len(bg),
                              images=len(idx), fx=len(fx_names), sfx=len(sfx_names), music=len(audio['music']),
                              glyphs={size:len(font.get(size, {}).get('glyphs', {})) for size in ('12','16')}),
                  chapters=chapters,
                  boundary='静态字面量及实际元数据；变量、拼接、模板插值、嵌套对象动作归属需实际运行验收。未把动作、头像或声音回退算作资源存在。')
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('ok','counts','assets')}, ensure_ascii=False))
    for e in errors[:90]:
        print(e['where'] + ' | ' + e['kind'] + ' | ' + e['key'] + (' | ' + e['detail'] if e['detail'] else ''))
    print('错误', len(errors), '警告', len(warnings), '报告', out)
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(run())
