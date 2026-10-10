import sys
sys.dont_write_bytecode = True
# 包 3 自测用的最小数据包（格式照技术约定 §3.1–§3.8）。包 6 的 tools\dev\fixture.py 出来以后可以换掉。
# 产物：tools\dev\p3\_fixture\data_meta.js、img_core.js（只给 ui_demo.html 用）。
# 用法：PYTHONDONTWRITEBYTECODE=1 python -B tools\dev\p3\make_fixture.py
import base64
import glob
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
JOJO = os.path.normpath(os.path.join(GAME, '..'))
SRC = os.path.join(JOJO, '源码')
ATLAS = os.path.join(JOJO, '角色图集')
OUT = os.path.join(HERE, '_fixture')

sys.path.insert(0, SRC)
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from engine import text as tx  # noqa: E402
from engine import fx  # noqa: E402
from engine import bg as BG  # noqa: E402
from engine.core import Frame, C  # noqa: E402

IMG = {}


def png_uri(im):
    b = io.BytesIO()
    im.save(b, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode('ascii')


def reg(key, im):
    IMG[key] = png_uri(im)
    return key


def crop(im):
    bb = im.getbbox()
    if not bb:
        return im, 0, 0
    return im.crop(bb), bb[0], bb[1]


# ------------------------------------------------------------------ 角色图集 + 头像
SCENE_HEADS = {
    's04_kak_evil': ('kakyoin', 'evil'), 's04_kak_face': ('kakyoin', 'faint'),
    's05_avdol_grave': ('avdol', 'grave'), 's05_joseph_grave': ('joseph', 'grave'),
    's05_jotaro_talk': ('jotaro', 'glare'), 's14_face': ('polnareff', 'shock_big'),
    's15_kak_look': ('kakyoin', 'weak'), 's15_kak_rest': ('kakyoin', 'rest'),
    's15_kak_smile': ('kakyoin', 'weak_smile'), 's19_jp_closed': ('joseph', 'closed_tall'),
    's19_jp_evil': ('joseph', 'evil_tall'), 's19_jp_open': ('joseph', 'open_tall'),
    's20_jotaro_smile': ('jotaro', 'smile'),
}
CIDS = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff', 'iggy', 'holly', 'dio', 'jgeil',
        'starplat', 'hiero', 'magred', 'chariot', 'hermit', 'fool', 'towergray', 'theworld']
STAND_KIND = {'starplat': 'stand', 'hiero': 'stand', 'magred': 'stand', 'chariot': 'stand', 'hermit': 'stand',
              'fool': 'stand', 'towergray': 'stand', 'theworld': 'stand'}


def build_chars():
    chars = {}
    scene_cat = json.load(open(os.path.join(ATLAS, '场景专用', '场景专用目录.json'), encoding='utf-8'))
    scene_by_id = {s['id']: s for s in scene_cat['sprites']}
    for cid in CIDS:
        d = json.load(open(os.path.join(ATLAS, cid, cid + '.json'), encoding='utf-8'))
        im = Image.open(os.path.join(ATLAS, cid, d['image'])).convert('RGBA')
        reg('chars/' + cid, im)
        anims = {k: {'row': v['row'], 'frames': v['frames'], 'fps': v.get('fps', 1), 'kind': v.get('kind', 'loop')}
                 for k, v in d['animations'].items()}
        heads, alias, hsize = {}, {}, {}
        for e in d.get('expressions', []):
            keys = []
            for i, f in enumerate(e['files']):
                hi = Image.open(os.path.join(ATLAS, cid, f)).convert('RGBA')
                keys.append(reg('heads/%s/%s_%d' % (cid, e['emotion'], i), hi))
                if hi.size != (32, 32):
                    hsize[e['emotion']] = list(hi.size)
            heads[e['emotion']] = keys
            alias[e['id']] = e['emotion']
        for sid, (hc, emo) in SCENE_HEADS.items():
            if hc != cid or sid not in scene_by_id:
                continue
            s = scene_by_id[sid]
            strip = Image.open(os.path.join(ATLAS, '场景专用', s['file'])).convert('RGBA')
            w, h = s['size']
            keys = []
            for i in range(s['frames']):
                keys.append(reg('heads/%s/%s_%d' % (cid, emo, i), strip.crop((i * w, 0, (i + 1) * w, h))))
            heads[emo] = keys
            alias[sid] = emo
            if (w, h) != (32, 32):
                hsize[emo] = [w, h]
        # top / bodyW 粗算（真正的由包 6 算）
        cw, ch = d['cell']
        idle = anims.get('idle') or next(iter(anims.values()))
        fr0 = im.crop((0, idle['row'] * ch, cw, idle['row'] * ch + ch))
        bb = fr0.getbbox() or (0, 0, cw, ch)
        top = d['pivot'][1] - bb[1]
        chars[cid] = {'name': d['name'], 'image': 'chars/' + cid, 'cell': d['cell'], 'pivot': d['pivot'],
                      'animations': anims, 'aliases': d.get('aliases', {}), 'heads': heads, 'headAlias': alias,
                      'headSize': hsize, 'amap': {}, 'top': top, 'bodyW': max(3, round((bb[2] - bb[0]) * 0.3)),
                      'kind': STAND_KIND.get(cid, 'char')}
    return chars


def build_props():
    cat = json.load(open(os.path.join(ATLAS, '道具', '道具目录.json'), encoding='utf-8'))
    props = {}
    for p in cat['sprites']:
        if p['id'] not in ('photo', 'photo_crew', 'fleshbud', 'camera', 'coin'):
            continue
        im = Image.open(os.path.join(ATLAS, '道具', p['file'])).convert('RGBA')
        props[p['id']] = {'image': reg('props/' + p['id'], im), 'frames': p['frames'], 'size': p['size'],
                          'pivot': p['pivot'], 'fps': p['fps'], 'kind': p['kind']}
    scene_cat = json.load(open(os.path.join(ATLAS, '场景专用', '场景专用目录.json'), encoding='utf-8'))
    scene = {}
    for s in scene_cat['sprites']:
        if s['id'] not in ('s04_kak_face', 's04_sphand', 's02_note'):
            continue
        im = Image.open(os.path.join(ATLAS, '场景专用', s['file'])).convert('RGBA')
        scene[s['id']] = {'image': reg('scene/' + s['id'], im), 'frames': s['frames'], 'size': s['size'],
                          'pivot': s['pivot'], 'fps': s['fps'], 'kind': s['kind'], 'character': s.get('character'),
                          'category': s.get('category'), 'scene': s.get('scene')}
    return props, scene


# ------------------------------------------------------------------ 主角 / 说话人 / 替身
HEROES = {
    'jotaro': ('空条承太郎', '承太郎', 'KUJO JOTARO', 'starplat', ['#241c6a', '#3e32a8', '#5a4ad0'], '#3a4a9a', 440),
    'joseph': ('乔瑟夫·乔斯达', '乔瑟夫', 'JOSEPH JOESTAR', 'hermit', ['#3a1c5a', '#6a3a9a', '#8a5ac0'], '#6a8a3a', 520),
    'avdol': ('穆罕默德·阿布德尔', '阿布德尔', 'MUHAMMAD AVDOL', 'magred', ['#5a1010', '#a0301a', '#e05020'], '#c0402a', 400),
    'kakyoin': ('花京院典明', '花京院', 'KAKYOIN NORIAKI', 'hiero', ['#0a3a20', '#1c6a40', '#2a8a50'], '#2a9a5a', 560),
    'polnareff': ('让·皮埃尔·波鲁纳雷夫', '波鲁纳雷夫', 'J.P. POLNAREFF', 'chariot', ['#22284a', '#5a6aa0', '#8a9ad0'], '#6a7ab0', 620),
    'iggy': ('伊奇', '伊奇', 'IGGY', 'fool', ['#6e3614', '#9a5420', '#c88a40'], '#707070', 900),
}
SPEAKERS = {'holly': ('荷莉', '#d0608a', 800), 'dio': ('DIO', '#c89a20', 420), 'jgeil': ('J·凯尔', '#7a3a3a', 380)}
STANDS = {
    'starplat': ('白金之星', 'STAR PLATINUM', 'jotaro', '#b090ff', '#c8a8ff', '#d8d0ff', 'purple', 'humanoid', {'dx': -6, 'z': 6}, None),
    'hermit': ('隐者之紫', 'HERMIT PURPLE', 'joseph', '#c080ff', '#c890ff', '#d0a0ff', 'purple', 'vine', None, None),
    'magred': ("红色魔术师", "MAGICIAN'S RED", 'avdol', '#ff7a30', '#ff7040', '#ffb070', 'red', 'humanoid', {'dx': -6, 'z': 6}, None),
    'hiero': ('绿色法皇', 'HIEROPHANT GREEN', 'kakyoin', '#70ffb0', '#70ffb0', '#90ffc0', 'green', 'humanoid', {'dx': -4, 'z': 10}, 'tendril'),
    'chariot': ('银色战车', 'SILVER CHARIOT', 'polnareff', '#c8d8ff', '#d8e4ff', '#c8d8ff', 'blue', 'humanoid', {'dx': -6, 'z': 6}, None),
    'fool': ('愚者', 'THE FOOL', 'iggy', '#e8c070', '#ffe08a', '#fff0b0', 'yellow', 'sand', {'dx': -8, 'z': 4}, None),
    'towergray': ('灰塔', 'TOWER OF GRAY', 'grayfly', '#c8d8f0', '#c8d8f0', '#e0e8f8', 'bw', 'object', None, None),
    'theworld': ('世界', 'THE WORLD', 'dio', '#ffd040', '#ffd83c', '#fff2a0', 'yellow', 'humanoid', {'dx': -6, 'z': 6}, None),
}


def build_people():
    heroes = {k: {'cid': k, 'cn': v[0], 'short': v[1], 'rn': v[2], 'stand': v[3], 'burst': v[4], 'panel': '#0e0a2c',
                  'accent': '#ffe040', 'nameColor': v[5], 'blipHz': v[6], 'grunt': 'grunt_' + k} for k, v in HEROES.items()}
    speakers = {k: {'short': v[0], 'nameColor': v[1], 'blipHz': v[2]} for k, v in SPEAKERS.items()}
    stands = {k: {'cn': v[0], 'en': v[1], 'owner': v[2], 'aura': v[3], 'card': v[4], 'ghost': v[5], 'impact': v[6],
                  'fist': k in ('starplat', 'theworld'), 'kind': v[7], 'summonSfx': 'stand_summon_star',
                  'idle': v[8], 'link': v[9]} for k, v in STANDS.items()}
    return heroes, speakers, stands


# ------------------------------------------------------------------ UI 预渲染（照技术约定 §5.6，粗做）
def fr_ui():
    return Frame(1.0, 0, 10.0, 'fixture')


def build_ui(stands):
    ui = {}
    # 名牌
    ui['namecards'] = {}
    for cid, cn, sub, acc in [('jotaro', '空条承太郎', '不良高中生｜沉默寡言·身上有“恶灵”', '#3a4a9a'),
                              ('kakyoin', '花京院典明', '转学生｜DIO 的刺客？', '#2a9a5a'),
                              ('joseph', '乔瑟夫·乔斯达', '承太郎的外公｜从纽约连夜赶来', '#6a8a3a')]:
        fr = fr_ui()
        tx.name_card(fr, cn, sub, 0, 9, '#ffffff', acc)
        im, x, y = crop(fr.ui)
        ui['namecards'][cid] = {'image': reg('ui/namecard/' + cid, im), 'w': im.width, 'h': im.height, 'x': x, 'y': y}
    # 替身卡
    ui['standcards'] = {}
    for sid in ('starplat', 'hiero', 'magred', 'chariot', 'towergray'):
        s = stands[sid]
        fr = fr_ui()
        tx.stand_card(fr, s['cn'], s['en'], 0, 9, colour=s['card'], side='right')
        im, x, y = crop(fr.ui)
        ui['standcards'][sid] = {'image': reg('ui/standcard/' + sid, im), 'w': im.width, 'h': im.height, 'side': 'right', 'y': 40}
    # 地点卡
    ui['locations'] = {}
    for key, place, sub in [('tokyo', '1987年 日本·东京', 'TOKYO · JAPAN'), ('hongkong', '香港', 'HONG KONG')]:
        fr = fr_ui()
        tx.location(fr, place, sub, 0, 9)
        im, x, y = crop(fr.ui)
        ui['locations'][key] = {'image': reg('ui/location/' + key, im), 'w': im.width, 'h': im.height, 'x': x, 'y': y}
    # 篇章卡（整屏）
    ui['chapters'] = {}
    for key, no, title, name, en, cols in [('prologue', '序章', '东京', '替身之名', 'PROLOGUE · TOKYO', ('#402060', '#200830')),
                                           ('ch1', '第1章', '香港', '灰塔与银色战车', 'CHAPTER 1 · HONG KONG', ('#5a1a10', '#200808'))]:
        fr = fr_ui()
        fx.menace_bg(fr, 0.0, cols)
        base = fr.img.resize((640, 360), Image.NEAREST).convert('RGBA')
        fr2 = fr_ui()
        tx.title(fr2, no + '　' + title, 0, 9, y=150, size=48, pop=0)
        tx.title(fr2, name, 0, 9, y=206, size=30, colour='#ffffff', outline='#000000', pop=0)
        tx.text(fr2, 320, 240, en, 14, '#f0e0a0', kind='bold', outline=(0, 0, 0), anchor='mt')
        base.alpha_composite(fr2.ui)
        ui['chapters'][key] = {'image': reg('ui/chapter/' + key, base)}
    # 大标题
    ui['titles'] = {}
    for key, s, size, col, ol, ow in [('stand', '替身', 64, '#ffe040', '#2a0a3a', 3), ('egypt', '目标——埃及！', 48, '#ffe040', '#2a0a3a', 3),
                                      ('saiki', '再起不能', 40, '#ffffff', '#000000', 3), ('draw', '胜负已分', 40, '#ffffff', '#000000', 3),
                                      ('day50', '50', 64, '#ff3048', '#2a0008', 3), ('day_unit', '天', 40, '#ff3048', '#2a0008', 3),
                                      ('w6_hg_splash', '绿宝石水花——！', 40, '#90ffc0', '#062a14', 3)]:
        im = tx.text_img(s, 'bold', size, col, outline=ol, owidth=ow, shadow='#000000')
        ui['titles'][key] = {'image': reg('ui/title/' + key, im), 'w': im.width, 'h': im.height}
    # 拟声字
    ui['sfx'] = {}
    SFX = [('ORA', 40, '#ffe040', '#2a0a4a', 3), ('ORA!', 40, '#ffe040', '#2a0a4a', 3), ('ORA!!', 48, '#ffffff', '#3a0a5a', 3),
           ('ORA!!!', 56, '#ffffff', '#3a0a5a', 4), ('ドゴォ', 40, '#ffb040', '#2a0a0a', 3), ('バキィ', 40, '#ffe070', '#3a1a08', 3),
           ('キィン！', 36, '#d8e4ff', '#1a1a3a', 3), ('ガシッ', 36, '#90ffc0', '#062a14', 3), ('看穿！', 28, '#ffffff', '#2a58e0', 2),
           ('破绽！', 28, '#ffe040', '#3a1a00', 2), ('咚', 32, '#ffffff', '#000000', 2), ('U!', 32, '#ffd040', '#3a1a00', 3),
           ('ゴオオッ', 40, '#ffb040', '#3a0a00', 3), ('！？', 40, '#ffffff', '#000000', 3), ('ドドド', 40, '#fff2c8', '#3a1a08', 3)]
    for w, size, col, ol, ow in SFX:
        im = tx.text_img(w, 'bold', size, col, outline=ol, owidth=ow)
        ui['sfx'][w] = {'image': reg('ui/sfx/' + w, im), 'w': im.width, 'h': im.height, 'size': size}
    # ゴ / ド
    ui['menace'] = {}
    for ch in ('ゴ', 'ド'):
        im = tx.text_img(ch, 'bold', 36, C['menace'], outline='#1a0022', owidth=2)
        ui['menace'][ch] = {'image': reg('ui/menace/' + ch, im), 'w': im.width, 'h': im.height}
    # 必杀名
    ui['specials'] = {}
    for key, s, col, ol in [('jotaro', '欧拉欧拉欧拉！', '#ffe040', '#2a0a4a'), ('kakyoin', '绿宝石水花！', '#90ffc0', '#062a14'),
                            ('avdol', '十字火焰风暴！', '#ffd040', '#3a0a00'), ('jail_bars', '……别小看我。', '#ffffff', '#2a0a4a')]:
        im = tx.text_img(s, 'bold', 48, col, outline=ol, owidth=3, shadow='#000000')
        ui['specials'][key] = {'image': reg('ui/special/' + key, im), 'w': im.width, 'h': im.height}
    # VS
    vsim = tx.text_img('VS', 'bold', 40, '#ff3048', outline='#ffffff', owidth=3, shadow='#000000')
    ui['vs'] = {'mark': {'image': reg('ui/vs/mark', vsim), 'w': vsim.width, 'h': vsim.height}}
    for key, name, en, tag, cols in [('hiero', '绿色法皇', 'HIEROPHANT GREEN', 'VS 绿色法皇 / 东京·校门', ['#1c6a40', '#0a3a20']),
                                     ('towergray', '灰塔', 'TOWER OF GRAY', 'VS 灰塔 / 飞往开罗的客机', ['#5a6a80', '#2a3040']),
                                     ('chariot', '银色战车', 'SILVER CHARIOT', 'VS 银色战车 / 香港·虎豹别墅', ['#5a6aa0', '#22284a'])]:
        nm = tx.text_img(name, 'bold', 48, '#ffe040', outline='#2a0a3a', owidth=3)
        e = tx.text_img(en, 'bold', 14, '#ffffff', outline='#000000', owidth=1)
        t = tx.text_img(tag, 'bold', 16, '#ffffff', outline='#000000', owidth=1)
        tw_, th = t.width + 30, t.height + 8
        slab = Image.new('RGBA', (tw_, th), (0, 0, 0, 0))
        d = ImageDraw.Draw(slab)
        d.polygon([(8, 0), (tw_ - 1, 0), (tw_ - 9, th - 1), (0, th - 1)], fill=(14, 8, 26, 230), outline=cols[0])
        d.line([(9, 1), (tw_ - 2, 1)], fill=cols[0])
        slab.alpha_composite(t, (14, 4))
        ui['vs'][key] = {'name': {'image': reg('ui/vs/%s_name' % key, nm), 'w': nm.width, 'h': nm.height},
                         'en': {'image': reg('ui/vs/%s_en' % key, e), 'w': e.width, 'h': e.height},
                         'tag': {'image': reg('ui/vs/%s_tag' % key, slab), 'w': tw_, 'h': th},
                         'colours': cols}
    # 面板：纸巾
    pw, ph = 240, 120
    note = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(note)
    d.rounded_rectangle((3, 3, pw - 1, ph - 1), 4, fill=(0, 0, 0, 90))
    d.rounded_rectangle((0, 0, pw - 4, ph - 4), 4, fill=(244, 239, 226, 255), outline=(190, 180, 160, 255))
    yy = 24
    for ln in '空条承太郎。\n今天之内，我的替身会取你性命。'.split('\n'):
        im = tx.text_img(ln, 'bold', 18, '#2a1a40')
        note.alpha_composite(im, (16, yy))
        yy += im.height + 10
    ui['panels'] = {'tissue_note': {'image': reg('ui/panel/tissue_note', note), 'w': pw, 'h': ph}}
    # 坠毁章
    t = tx.text_img('乔瑟夫坠毁记录', 'bold', 16, '#3a2400')
    plw, plh = t.width + 70, 40
    plate = Image.new('RGBA', (plw, plh), (0, 0, 0, 0))
    d = ImageDraw.Draw(plate)
    d.rounded_rectangle((0, 0, plw - 1, plh - 1), 8, fill=(240, 192, 64, 255), outline=(255, 244, 192, 255), width=2)
    plate.alpha_composite(t, (12, (plh - t.height) // 2))
    digits = []
    dw = dh = 0
    for i in range(10):
        im = tx.text_img(str(i), 'bold', 24, '#3a2400', outline='#fff4c0', owidth=2)
        digits.append(reg('ui/crash/d%d' % i, im))
        dw, dh = max(dw, im.width), max(dh, im.height)
    ui['crash'] = {'plate': {'image': reg('ui/crash/plate', plate), 'w': plw, 'h': plh}, 'digits': digits, 'dw': dw, 'dh': dh}
    # TBC
    tbc = fx._tbc_img()
    ui['tbc'] = {'image': reg('ui/tbc', tbc), 'w': tbc.width, 'h': tbc.height}
    return ui


# ------------------------------------------------------------------ 演示用背景（静态快照）
def build_bg():
    out = {}
    for key, fn, kw in [('school_gate', 'school_gate', {}), ('hongkong_night', 'hongkong_night', {}), ('jail_cell', 'jail_cell', {})]:
        fr = Frame(0.5, 12, 10.0, 'fixture')
        try:
            getattr(BG, fn)(fr, scroll=0.0, **kw)
        except Exception as e:  # 背景失败就画一个渐变
            print('bg fail', key, e)
            d = ImageDraw.Draw(fr.img)
            for y in range(180):
                d.line([(0, y), (320, y)], fill=(20 + y // 3, 16, 50))
        out[key] = reg('bg/demo/' + key, fr.img.convert('RGBA'))
    # 俯视榻榻米（拔肉芽演示用）
    fr = Frame(0.0, 0, 1.0, 'fixture')
    try:
        from engine import bg_asia
        bg_asia._tatami(fr.img) if hasattr(bg_asia, '_tatami') else None
    except Exception as e:
        print('tatami fail', e)
    out['tatami'] = reg('bg/demo/tatami', fr.img.convert('RGBA'))
    return out


# ------------------------------------------------------------------ 字库
PUNCT = '…—「」『』（）！？，。、：；“”‘’·～＋－×÷■□▼▲★☆　'


def collect_chars(extra):
    chars = set()
    files = glob.glob(os.path.join(GAME, 'engine', '*.js')) + glob.glob(os.path.join(HERE, '*.js'))
    for f in files:
        chars.update(c for c in open(f, encoding='utf-8').read() if ord(c) > 127)
    for s in extra:
        chars.update(s)
    chars.update(chr(i) for i in range(32, 127))
    chars.update(PUNCT)
    return chars


def build_font(chars):
    from fontTools.ttLib import TTCollection
    cmap = TTCollection('C:/Windows/Fonts/simsun.ttc').fonts[0].getBestCmap()
    keep = sorted(c for c in chars if c == '　' or (c.isprintable() and ord(c) in cmap))
    miss = sorted(c for c in chars if c not in keep and not c.isspace() and c.isprintable())
    if miss:
        print('字库里没有（跳过）：', ''.join(miss))
    meta = {}
    for size in (12, 16):
        f = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', size)
        asc, desc = f.getmetrics()
        lh = asc + desc
        cols, cell = 64, size + 1
        rows = (len(keep) + cols - 1) // cols
        atlas = Image.new('RGBA', (cols * cell, rows * (lh + 1)), (0, 0, 0, 0))
        d = ImageDraw.Draw(atlas)
        d.fontmode = '1'
        glyphs = {}
        for i, ch in enumerate(keep):
            r, c = divmod(i, cols)
            x, y = c * cell, r * (lh + 1)
            adv = int(round(f.getlength(ch))) or size // 2
            d.text((x, y + asc), ch, font=f, fill=(255, 255, 255, 255), anchor='ls')
            glyphs[ch] = [x, y, adv]
        meta[str(size)] = {'image': reg('font/simsun%d' % size, atlas), 'lh': lh, 'asc': asc, 'glyphs': glyphs}
    return meta


def main():
    os.makedirs(OUT, exist_ok=True)
    chars = build_chars()
    props, scene = build_props()
    heroes, speakers, stands = build_people()
    ui = build_ui(stands)
    bgs = build_bg()
    names = [c['name'] for c in chars.values()] + [h['short'] for h in heroes.values()] + \
            [s['short'] for s in speakers.values()] + [s['cn'] for s in stands.values()]
    font = build_font(collect_chars(names))
    meta = {'v': 1, 'built': 'fixture-p3', 'img': {}, 'packsLoaded': {}, 'packKeys': {},
            'packs': {'core': {'file': 'img_core.js'}}, 'chars': chars, 'heroes': heroes, 'speakers': speakers,
            'stands': stands, 'props': props, 'scene': scene, 'bg': {}, 'ui': ui, 'font': font,
            'fxtex': {}, 'audio': {'music': {}, 'sfx': {}}, 'video': {}, 'demoBg': bgs}
    with open(os.path.join(OUT, 'data_meta.js'), 'w', encoding='utf-8') as f:
        f.write('window.GAME_DATA = ' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + ';\n')
    with open(os.path.join(OUT, 'img_core.js'), 'w', encoding='utf-8') as f:
        f.write('(function(){var D=window.GAME_DATA;Object.assign(D.img,' +
                json.dumps(IMG, ensure_ascii=False, separators=(',', ':')) + ');D.packKeys.core=' +
                json.dumps(sorted(IMG), ensure_ascii=False) + ';D.packsLoaded.core=true;})();\n')
    total = sum(os.path.getsize(os.path.join(OUT, n)) for n in os.listdir(OUT))
    print('fixture ok: %d images, %d glyphs, %.1f MB' % (len(IMG), len(font['16']['glyphs']), total / 1e6))


if __name__ == '__main__':
    main()
