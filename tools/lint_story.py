"""检查真实脚本语法、剧情接口、静态资源引用和字库覆盖。"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parent.parent
LEX = re.compile(r'(?P<skip>\s+|//[^\n]*|/\*[\s\S]*?\*/)|(?P<string>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`)|(?P<id>[$\w]+)|(?P<punct>.)', re.UNICODE)
API = set('run actor wait until free mark cid exists killFx sfx cue music stopMusic ambient shake bump flash impact fadeOut fadeIn letterbox insert insertUI filter zoom punchIn camera fx lightning state nameCard standCard location title chapterCard sfxText word menacing emote hint notice vs cutin tbc panel crash photo eyeStrip memory route say narrate choice spawn remove face follow prop unprop animate walk arc pose unpose act setStage runner party join leave setLeader lockLeader leadable nameOf setPlayer summon recall standAct timestop qte mash timing rhythm clash press pluck aim video fight'.split())
FORBIDDEN = set('►◄♪・♡♥〜⟵')


@dataclass
class Token:
    kind: str
    value: str
    line: int


def lex(text):
    result, line = [], 1
    for match in LEX.finditer(text):
        kind, raw = match.lastgroup, match.group()
        if kind != 'skip':
            value = raw
            if kind == 'string':
                value = raw[1:-1]
                value = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1], 16)), value)
                value = re.sub(r'\\([nrt\\\'"`])', lambda m: {'n': '\n', 'r': '\r', 't': '\t'}.get(m[1], m[1]), value)
            result.append(Token(kind, value, line))
        line += raw.count('\n')
    return result


def arguments(tokens, start):
    args, current, level = [], [], []
    pairs = {')': '(', ']': '[', '}': '{'}
    for token in tokens[start:]:
        if token.kind == 'punct':
            if token.value == ')' and not level:
                args.append(current)
                return args
            if token.value == ',' and not level:
                args.append(current); current = []; continue
            if token.value in ('(', '[', '{'):
                level.append(token.value)
            elif token.value in pairs and level and level[-1] == pairs[token.value]:
                level.pop()
        current.append(token)
    return []


def literal(argument):
    return argument[0].value if len(argument) == 1 and argument[0].kind == 'string' and '${' not in argument[0].value else None


def property_value(tokens, key):
    for i in range(len(tokens) - 2):
        if tokens[i].value == key and tokens[i + 1].value == ':' and tokens[i + 2].kind == 'string':
            return tokens[i + 2].value
    return None


def calls(tokens):
    for i in range(len(tokens) - 3):
        if tokens[i].kind == 'id' and tokens[i + 1].value == '.' and tokens[i + 2].kind == 'id' and tokens[i + 3].value == '(':
            yield i, tokens[i].value, tokens[i + 2].value, arguments(tokens, i + 4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=GAME / 'tools/_playtest/lint_story.json')
    args = parser.parse_args()
    errors, files = [], sorted((GAME / 'engine').glob('*.js')) + sorted((GAME / 'story').glob('*.js')) + [GAME / 'main.js']
    def fail(path, line, kind, detail):
        errors.append({'file': str(path.relative_to(GAME)), 'line': line, 'kind': kind, 'detail': detail})
    meta = {}
    for name in ('chars', 'props', 'bg', 'ui', 'img_index', 'audio'):
        meta[name] = json.loads((GAME / 'tools/_meta' / (name + '.json')).read_text(encoding='utf-8'))
    chars, ui = meta['chars']['chars'], meta['ui']
    ids = set(chars) | set(meta['chars'].get('speakers', {}))
    def char_exists(cid):
        if cid is None: return True
        if cid.startswith('scene:'): return cid[6:] in meta['props']['scene']
        if cid.startswith('prop:'): return cid[5:] in meta['props']['props']
        return cid in ids
    sfx = set(meta['audio']['sfx'])
    sfx.update(v.get('group') for v in meta['audio']['sfx'].values() if v.get('group'))
    tokens_by_file, declared_stages = {}, set()
    for path in files:
        text = path.read_text(encoding='utf-8-sig')
        syntax = subprocess.run(['node', '--check', str(path)], capture_output=True, text=True, encoding='utf-8', errors='replace')
        if syntax.returncode: fail(path, 1, 'syntax', syntax.stderr.strip())
        tokens_by_file[path] = lex(text)
        if re.search(r'\.filter\s*=', text): fail(path, 1, 'canvas_filter', '禁止 canvas filter 赋值')
        if path.parent.name == 'story':
            declared_stages.update(re.findall(r'\b(?:ST|STAGES)\.([A-Za-z0-9_]+)\s*=', text))
            declared_stages.update(re.findall(r"(?:id\s*:\s*|['\"])([A-Za-z0-9_]+_(?:pro|fin|ch\d+[a-z]?))['\"]?\s*[:,]", text))
    html = GAME / 'index.html'
    if re.search(r'(?<![-\w])filter\s*:', html.read_text(encoding='utf-8-sig')):
        fail(html, 1, 'css_filter', '禁止 CSS filter')
    from fontTools.ttLib import TTFont
    with TTFont('C:/Windows/Fonts/simsun.ttc', fontNumber=0) as font:
        glyphs = set(font.getBestCmap())
    glyph_count, call_count = 0, 0
    for path, tokens in tokens_by_file.items():
        variables = {}
        for i, receiver, method, argv in calls(tokens):
            script = bool(re.fullmatch(r'S\d*', receiver))
            if script:
                call_count += 1
                if method not in API: fail(path, tokens[i].line, 'script_api', method)
            if not argv: continue
            first = literal(argv[0])
            def exists(table, key, kind):
                if key is not None and key not in table: fail(path, tokens[i].line, kind, key)
            if script and method in ('spawn', 'setPlayer', 'join', 'leave', 'setLeader', 'leadable', 'say', 'eyeStrip', 'actor'):
                if first and first != 'player' and not char_exists(first): fail(path, tokens[i].line, 'character', first)
                if method in ('spawn', 'actor', 'setPlayer') and first and i >= 2 and tokens[i - 1].value == '=':
                    variables[tokens[i - 2].value] = first
            if script and method == 'party':
                for t in argv[0]:
                    if t.kind == 'string' and not char_exists(t.value): fail(path, t.line, 'party_character', t.value)
            if script and method in ('sfx', 'cue', 'ambient'): exists(sfx, first, 'sfx')
            if script and method == 'music': exists(meta['audio']['music'], first, 'music')
            if script and method == 'setStage':
                exists(declared_stages, first, 'stage')
                if first and not re.search(r'_(pro|fin|ch\d+[a-z]?)$', first): fail(path, tokens[i].line, 'stage_suffix', first)
            if script and method in ('nameCard', 'standCard', 'location', 'title', 'chapterCard', 'panel'):
                table = {'nameCard': 'namecards', 'standCard': 'standcards', 'location': 'locations', 'title': 'titles', 'chapterCard': 'chapters', 'panel': 'panels'}[method]
                exists(ui.get(table, {}), first, 'ui_' + table)
            if script and method in ('sfxText', 'word'): exists(ui.get('sfx', {}), first, 'sfx_text')
            if script and method == 'fight' and not property_value(argv[0], 'id'): fail(path, tokens[i].line, 'fight_id', 'S.fight 必须声明稳定 id')
            if receiver == 'G' and method == 'image': exists(meta['img_index'], first, 'image')
            if receiver == 'G' and method == 'atlas' and first and not char_exists(first): fail(path, tokens[i].line, 'atlas', first)
            if script and method == 'say' and first:
                expr = property_value(argv[2], 'expr') if len(argv) > 2 else None
                char = chars.get(first, {})
                if '__' in first and not char.get('heads'): char = chars.get(first.split('__')[0], {})
                heads = char.get('heads', {})
                if expr and heads and expr not in heads and char.get('headAlias', {}).get(expr) not in heads:
                    fail(path, tokens[i].line, 'head_expression', first + '.' + expr)
            if script and method in ('pose', 'act', 'walk') and len(argv) > 1:
                cid = first or variables.get(argv[0][0].value) if len(argv[0]) == 1 else None
                anim = literal(argv[1]) if method != 'walk' else None
                char = chars.get(cid, {})
                if anim and char:
                    available = set(char.get('anims', {})) | set(char.get('amap', {}))
                    if anim not in available: fail(path, tokens[i].line, 'animation', cid + '.' + anim)
        for token in tokens:
            if token.kind != 'string': continue
            for c in set(token.value) & FORBIDDEN: fail(path, token.line, 'forbidden_glyph', c)
            if not re.search(r'[\u3040-\u30ff\u3400-\u9fff]', token.value): continue
            missing = sorted({c for c in token.value if not c.isspace() and ord(c) not in glyphs})
            glyph_count += len(token.value)
            if missing: fail(path, token.line, 'font_glyph', ''.join(missing))
    result = {'ok': not errors, 'files': len(files), 'script_calls': call_count, 'glyphs_checked': glyph_count,
              'declared_stages': sorted(declared_stages), 'errors': errors}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    for error in errors: print(f"{error['file']}:{error['line']} {error['kind']} {error['detail']}")
    print(json.dumps({'ok': result['ok'], 'files': len(files), 'script_calls': call_count, 'errors': len(errors), 'out': str(args.out)}, ensure_ascii=False))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
