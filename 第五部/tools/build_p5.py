# 独立合成第五部运行包，第三部运行数据与已固定的跨部素材均为只读输入。
import argparse
import base64
import copy
import json
import shutil
import time

from PIL import Image

from p5_paths import REPO, GAME, ASSETS, META, SHARED_ART, SHARED_CAST, load_json, save_json

DATA = GAME / 'data'
MUSIC = ['title', 'daily', 'tension', 'battle', 'sad', 'victory']
REUSE = ['fx/', 'ui/sfx/', 'ui/menace/', 'ui/vs/mark', 'ui/tbc', 'ui/title/stand',
         'chars/starplat', 'heads/starplat/', 'ui/standcard/starplat', 'ui/special/jotaro_ts',
         'ui/title/jotaro_ts', 'ui/title/jotaro_resume']
HEAD_ALIAS = {'angry': 'rage', 'glare': 'rage', 'surprise': 'shock', 'hurt': 'shock', 'happy': 'smile',
              'sad': 'normal', 'serious': 'normal', 'portrait': 'normal', 'portrait_angry': 'rage'}


def read_gd(path):
    s = path.read_text(encoding='utf-8')
    return json.loads(s[s.index('=') + 1:s.rindex(';')])


def read_pack(path):
    s = path.read_text(encoding='utf-8')
    start = s.index('Object.assign(D.img,') + len('Object.assign(D.img,')
    return json.loads(s[start:s.index(');D.packKeys')])


def merge(a, b):
    out = copy.deepcopy(a)
    for key, value in b.items():
        out[key] = merge(out[key], value) if isinstance(value, dict) and isinstance(out.get(key), dict) else copy.deepcopy(value)
    return out


def image_uri(path):
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(text, encoding='utf-8', newline='\n')
    temp.replace(path)


def ui_images(font_meta):
    # 从同一份点阵图集排卡片，像素与对话字一致，避免另引入一套系统字体。
    atlas = Image.open(ASSETS / (font_meta['16']['image'] + '.png')).convert('RGBA')
    glyphs, lh = font_meta['16']['glyphs'], font_meta['16']['lh']

    def line(text, scale=1, colour='#ffe29c'):
        cells = [glyphs[c] for c in text]
        image = Image.new('RGBA', (sum(c[2] for c in cells), lh))
        x = 0
        for sx, sy, width in cells:
            mask = atlas.crop((sx, sy, sx + width, sy + lh)).getchannel('A')
            image.paste(Image.new('RGBA', (width, lh), colour), (x, 0), mask)
            x += width
        return image.resize((image.width * scale, lh * scale), Image.Resampling.NEAREST)

    ui = dict(chapters={}, logo={})
    logo = line('JoJo的奇妙冒险 黄金之风')
    target = ASSETS / 'ui/logo_main.png'
    target.parent.mkdir(parents=True, exist_ok=True)
    logo.save(target)
    ui['logo']['main'] = dict(image='ui/logo_main')
    # 主入口的章节顺序也用于篇章卡，新增章节不得出现空卡。
    main = (GAME / 'main.js').read_text(encoding='utf-8')
    chapters = json.loads(main.split('const names = ', 1)[1].split(';', 1)[0].strip())
    for key, title, sub in chapters:
        card = Image.new('RGBA', (640, 360), '#20142b')
        for text, scale, y in [(title, 2, 138), (sub, 1, 196)]:
            image = line(text, scale)
            card.alpha_composite(image, ((640 - image.width) // 2, y))
        target = ASSETS / f'ui/chapter/{key}.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        card.save(target)
        ui['chapters'][key] = dict(image=f'ui/chapter/{key}', w=640, h=360)
    save_json(META / 'ui_shell.json', ui)
    return ui


def main():
    parser = argparse.ArgumentParser(description='第五部公共素材、字库和背景分包构建，默认无用户音频。')
    parser.add_argument('--no-font', action='store_true', help='复用第五部已生成字库')
    parser.add_argument('--rebuild-art', action='store_true', help='重新导出已有道具及序章/第1章装饰卡；默认使用已检入图与元数据')
    args = parser.parse_args()
    if not args.no_font:
        import p5_font
        p5_font.build()
    font = load_json(META / 'font.json')
    if not font:
        raise RuntimeError('字库未生成，请移除--no-font重新构建')
    p3 = read_gd(REPO / 'data/data_meta.js')
    p3img = read_pack(REPO / 'data/img_core.js')

    def parts(name, base):
        for path in sorted(META.glob(name + '_*.json')):
            base = merge(base, load_json(path, {}))
        return base

    cm = parts('chars', load_json(META / 'chars.json', {}))
    pm = parts('props', load_json(META / 'props.json', {}))
    # 最后覆盖生图条目，避免旧的分章元数据或再次构建把它们换回代码版。
    if args.rebuild_art:
        from props_p5 import build as build_props
        pm.setdefault('props', {}).update(build_props())
        save_json(META / 'props.json', pm)
    bg = parts('bg', load_json(META / 'bg.json', {}))
    ui_images(font)
    if args.rebuild_art:
        import p5_ui
        p5_ui.build()
    uim = parts('ui', load_json(META / 'ui.json', {}))
    if not cm.get('chars') or len(bg) < 10:
        raise RuntimeError('缺少第五部素材，请先运行export_p5.py和bg_p5.py')
    gd = dict(v=1, built=time.strftime('%Y-%m-%dT%H:%M:%S'), img={}, packsLoaded={}, packKeys={}, ck=p3['ck'],
              chars={'starplat': copy.deepcopy(p3['chars']['starplat']), **cm['chars']},
              heroes=cm.get('heroes', {}), speakers=cm.get('speakers', {}),
              stands={'starplat': p3['stands']['starplat'], **cm.get('stands', {})},
              props=pm.get('props', {}), scene=pm.get('scene', {}), bg=bg, font=font, fxtex=p3['fxtex'], video={})
    images = {k: uri for k, uri in p3img.items() if any(k.startswith(prefix) for prefix in REUSE)}
    groups = {'core': set(images)}
    p4 = load_json(SHARED_ART / 'characters.json')
    for cid in SHARED_CAST:
        character = p4['chars'][cid]
        gd['chars'][cid] = copy.deepcopy(character)
        for section in ('heroes', 'speakers', 'stands'):
            if cid in p4.get(section, {}):
                gd[section][cid] = copy.deepcopy(p4[section][cid])
        for key in {character['image'], *(key for frames in character.get('heads', {}).values() for key in frames)}:
            images[key] = image_uri(SHARED_ART / (key + '.png'))
            groups['core'].add(key)
    gd['heroes']['koichi']['stand'] = 'echoes3'
    for char in gd['chars'].values():
        heads = char.get('heads', {})
        aliases = char.setdefault('headAlias', {})
        for key, target in HEAD_ALIAS.items():
            if key not in heads and key not in aliases:
                aliases[key] = target if target in heads else 'normal'
    ui = {key: p3['ui'][key] for key in ('sfx', 'menace', 'tbc') if key in p3['ui']}
    ui.update(vs={'mark': p3['ui']['vs']['mark']}, standcards={'starplat': p3['ui']['standcards']['starplat']},
              titles={k: v for k, v in p3['ui'].get('titles', {}).items() if k in ('stand', 'jotaro_ts', 'jotaro_resume')},
              specials={k: v for k, v in p3['ui'].get('specials', {}).items() if k == 'jotaro_ts'})
    gd['ui'] = merge(ui, uim)
    gd['audio'] = dict(music={k: p3['audio']['music'][k] for k in MUSIC}, sfx=p3['audio']['sfx'])
    # 只从明确的运行目录收图，bg_src与预览等仓库外输入不会被误打进包。
    for directory in ('chars', 'heads', 'props', 'scene', 'bg', 'font', 'ui'):
        for path in sorted((ASSETS / directory).rglob('*.png')):
            key = path.relative_to(ASSETS).as_posix()[:-4]
            pack = 'core'
            if key.startswith('bg/'):
                pack = 'bg_' + bg[key.split('/')[1]]['pack']
            elif key.startswith('ui/chapter/'):
                pack = 'bg_' + key.split('/')[2]
            for keys in groups.values():
                keys.discard(key)
            images[key] = image_uri(path)
            groups.setdefault(pack, set()).add(key)
    packs = dict(core={'file': 'data/img_core.js'})
    for short in sorted({m['pack'] for m in bg.values()} | {'common', 'title', 'prologue', 'ch1'}):
        key = 'bg_' + short
        packs[key] = dict(file=f'data/img_{key}.js', bg=sorted(k for k, m in bg.items() if m['pack'] == short))
        groups.setdefault(key, set())
    packs['bg_title']['music'] = ['title']
    for pack in ('bg_prologue', 'bg_ch1'):
        packs[pack]['music'] = MUSIC[1:]
    gd['packs'] = packs
    # 缺图作为构建错误处理，避免可启动但头像或卡片静默丢失。
    want = set()
    def refs(value):
        if isinstance(value, dict):
            if isinstance(value.get('image'), str):
                want.add(value['image'])
            for child in value.values():
                refs(child)
        elif isinstance(value, list):
            for child in value:
                refs(child)
    for section in ('chars', 'props', 'scene', 'bg', 'ui', 'font'):
        refs(gd[section])
    for char in gd['chars'].values():
        want.update(key for frames in char.get('heads', {}).values() for key in frames)
    missing = want - images.keys()
    if missing:
        raise RuntimeError('元数据缺图：' + ', '.join(sorted(missing)))
    DATA.mkdir(parents=True, exist_ok=True)
    write_text(DATA / 'data_meta.js', 'window.GAME_DATA = ' + json.dumps(gd, ensure_ascii=False, separators=(',', ':')) + ';\n')
    for name, keys in sorted(groups.items()):
        keys = sorted(keys)
        payload = json.dumps({k: images[k] for k in keys}, ensure_ascii=False, separators=(',', ':'))
        text = '(function(){var D=window.GAME_DATA;Object.assign(D.img,' + payload + ');D.packKeys[' + json.dumps(name) + ']=' + json.dumps(keys, ensure_ascii=False) + ';D.packsLoaded[' + json.dumps(name) + ']=true;})();\n'
        write_text(DATA / f'img_{name}.js', text)
    for old in DATA.glob('img_bg_*.js'):
        if old.stem[4:] not in groups:
            old.unlink()
    shutil.copyfile(REPO / 'data/sfx.js', DATA / 'sfx.js')
    (DATA / 'music').mkdir(exist_ok=True)
    for name in MUSIC:
        shutil.copyfile(REPO / f'data/music/{name}.js', DATA / f'music/{name}.js')
    # 默认包不仅不登记用户歌，也清理旧构建可能遗留的用户歌文件。
    for old in (DATA / 'music').glob('*.js'):
        if old.stem not in MUSIC:
            old.unlink()
    print(f'构建完成：{len(images)}张图片，{len(gd["chars"])}个角色，{len(bg)}个背景，{len(packs)}个包；无用户音频')


if __name__ == '__main__':
    main()
