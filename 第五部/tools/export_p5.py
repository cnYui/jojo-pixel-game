# 按既有 Sheet 接口导出运行图集；只调整输出位置和元数据，不改画法或原始帧。
import importlib
import sys

from PIL import Image, ImageDraw

from p5_paths import P5, ASSETS, META, save_json

sys.path.insert(0, str(P5 / 'tools' / 'art'))
import px

# portrait 按值导入 ASSETS，所以先绑定 px，再导入 portrait，避免写到旧暂存目录。
px.ASSETS, px.META = str(ASSETS), str(META)
import portrait

portrait.ASSETS = str(ASSETS)
EMOTIONS = ('normal', 'smile', 'rage', 'shock')
EXTRAS = {'luca': '泪眼卢卡', 'police': '机场警官', 'passer_m': '男路人', 'passer_f': '女路人'}
PROPS = {'suitcase': (12, 10), 'frog': (8, 6), 'taxi': (73, 23), 'ladybug': (5, 4), 'shovel': (8, 26)}
OWNERS = dict(zip(
    ['goldexp', 'stickyfingers', 'moodyblues', 'sexpistols', 'aerosmith', 'purplehaze', 'spicegirl', 'requiem',
     'kingcrimson', 'metallica', 'littlefeet', 'mirrorman', 'gratefuldead', 'beachboy', 'babyface', 'whitealbum',
     'clash', 'talkinghead', 'greenday', 'oasis', 'softmachine', 'kraftwork', 'blacksabbath'],
    ['giorno', 'bucciarati', 'abbacchio', 'mista', 'narancia', 'fugo', 'trish', 'giorno',
     'diavolo', 'risotto', 'formaggio', 'illuso', 'prosciutto', 'pesci', 'melone', 'ghiaccio',
     'squalo', 'tiziano', 'cioccolata', 'secco', 'zucchero', 'sale', 'polpo']))
HERO_STANDS = {owner: sid for sid, owner in OWNERS.items() if sid != 'requiem'}

# 逻辑动作到最近的原画动作，按顺序选择；实际已画出的同名动作永远优先。
# 占位角色只有 idle / walk；其余动作最终落回 idle，保证后续脚本先接线时可运行。
ACTION_CANDIDATES = {
    'idle': ['pose'], 'walk': ['idle'], 'run': ['walk', 'idle'], 'talk': ['idle'],
    'cmd': ['point', 'pose', 'attack'], 'cmd2': ['point', 'pose', 'attack'], 'cmd_hold': ['pose'],
    'guard': ['block', 'pose'], 'block': ['guard', 'pose'], 'dodge': ['run', 'walk', 'hurt'],
    'hurt': ['shock', 'idle'], 'getup': ['hurt'], 'down': ['hurt'], 'fly': ['hurt', 'down'],
    'special': ['dream', 'pose', 'attack'], 'win': ['pose'], 'pose': ['idle'], 'shock': ['hurt'],
    'punch': ['attack', 'shoot'], 'punch2': ['punch', 'attack'], 'punch_heavy': ['upper', 'kick', 'punch', 'attack'],
    'upper': ['kick', 'punch', 'attack'], 'rush': ['punch', 'attack', 'shoot'], 'windup': ['pose', 'attack'],
    'attack': ['punch', 'shoot', 'pose'], 'attack2': ['attack', 'punch'], 'shoot': ['attack', 'punch'],
    'reach': ['punch', 'attack', 'pose'], 'finger': ['pose', 'punch'], 'kick': ['attack', 'punch'],
    'fist': ['punch', 'attack', 'pose'], 'float': ['idle'],
}


def action_map(anims):
    if 'idle' not in anims:
        raise ValueError('图集必须提供 idle 动作')
    return {key: next((a for a in choices if a in anims), 'idle')
            for key, choices in ACTION_CANDIDATES.items() if key not in anims}


def write_image(key, image):
    path = ASSETS / (key + '.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def heads_for(cid, sheet):
    if sheet.body is not None:
        return portrait.export_heads(cid, sheet.body, EMOTIONS)
    if sheet.face is not None:
        return portrait.export_face(cid, sheet.rows[0][1][0], sheet.face, EMOTIONS)
    # 非人形替身没有脸的位置定义时，使用待机全貌作头像，避免错误裁空。
    im = sheet.rows[0][1][0].img()
    box = im.getbbox()
    im = im.crop(box) if box else Image.new('RGBA', (16, 16), '#a080c0')
    im.thumbnail((30, 30), Image.Resampling.NEAREST)
    face = Image.new('RGBA', (32, 32))
    face.alpha_composite(im, ((32 - im.width) // 2, 32 - im.height))
    heads = {}
    for emo in EMOTIONS:
        heads[emo] = [f'heads/{cid}/{emo}_{i}' for i in range(2)]
        for key in heads[emo]:
            write_image(key, face)
    return heads


def export_sheet(cid, sheet):
    im, cell, pivot = sheet.pack()
    write_image('chars/' + cid, im)
    animations = sheet.anims()
    return dict(name=sheet.name, image='chars/' + cid, cell=cell, pivot=pivot, animations=animations,
                aliases={}, heads=heads_for(cid, sheet), headAlias=dict(portrait.ALIAS), headSize={},
                amap=action_map(animations), top=sheet.top(), bodyW=4, kind=sheet.kind, k=1)


def placeholder(cid, name, colour):
    # 只标记身体色块和头部色块，高度30像素，不伪装成已完成的人物美术。
    image = Image.new('RGBA', (20, 32))
    draw = ImageDraw.Draw(image)
    draw.rectangle((3, 1, 16, 13), fill='#f6c49a', outline='#1a1020')
    draw.rectangle((4, 14, 15, 30), fill=colour, outline='#1a1020')
    write_image('chars/' + cid, image)
    head = image.crop((2, 0, 18, 16)).resize((32, 32), Image.Resampling.NEAREST)
    heads = {}
    for emo in EMOTIONS:
        heads[emo] = [f'heads/{cid}/{emo}_{i}' for i in range(2)]
        for key in heads[emo]:
            write_image(key, head)
    animations = {a: dict(row=0, frames=1, fps=1, kind='static') for a in ('idle', 'walk')}
    return dict(name=name, image='chars/' + cid, cell=[20, 32], pivot=[10, 31], animations=animations,
                aliases={}, heads=heads, headAlias=dict(portrait.ALIAS), headSize={}, amap=action_map(animations),
                top=30, bodyW=4, kind='char', k=1, placeholder=True)


def main():
    meta = dict(chars={}, heroes={}, speakers={}, stands={})
    for mod_name in ('cast5_heroes', 'cast5_villains', 'cast5_stands', 'cast5_extra'):
        if mod_name == 'cast5_extra' and not (P5 / 'tools/art/cast5_extra.py').exists():
            continue
        mod = importlib.import_module(mod_name)
        for cid in mod.CAST:
            sheet = mod.build(cid)
            meta['chars'][cid] = export_sheet(cid, sheet)
            name = sheet.name
            meta['speakers'][cid] = dict(short=name, nameColor='#b89450', blipHz=540)
            if mod_name == 'cast5_heroes':
                meta['heroes'][cid] = dict(cid=cid, cn=name, short=name.split('·')[0], rn=cid.upper(),
                                          stand=HERO_STANDS.get(cid), burst=['#57336b', '#a47b36', '#edc862'],
                                          panel='#24172d', accent='#edc862', nameColor='#ad8038', blipHz=540, grunt=None)
            if sheet.kind == 'stand':
                meta['stands'][cid] = dict(cn=name, en=cid.upper(), owner=OWNERS.get(cid), aura='#edc862',
                                          card='#ffe29c', ghost='#fff3c8', impact='gold', kind='humanoid',
                                          idle=dict(dx=-8, z=6), link=None, summonSfx='stand_summon_star', fist=True)
            print(f'导出 {cid}: {len(sheet.rows)} 个动作')
    for (cid, name), colour in zip(EXTRAS.items(), ['#9b7251', '#536880', '#77935a', '#a8729a']):
        if cid not in meta['chars']:
            meta['chars'][cid] = placeholder(cid, name, colour)
            meta['speakers'][cid] = dict(short=name, nameColor=colour, blipHz=500)
            print('占位人物', cid)
    real = importlib.import_module('props5').PROPS if (P5 / 'tools/art/props5.py').exists() else {}
    props = {}
    for cid in dict.fromkeys([*PROPS, *real]):
        if cid in real:
            cv = real[cid]()
            if not isinstance(cv, px.Cv):
                raise TypeError(f'props5.PROPS[{cid!r}] 必须返回 px.Cv')
            im = cv.img()
        else:
            im = Image.new('RGBA', PROPS[cid], '#c89a50')
            ImageDraw.Draw(im).rectangle((0, 0, im.width - 1, im.height - 1), outline='#1a1020')
        write_image('props/' + cid, im)
        props[cid] = dict(image='props/' + cid, frames=1, size=list(im.size), pivot=[im.width // 2, im.height],
                          fps=1, kind='static', k=1, placeholder=cid not in real)
    save_json(META / 'chars.json', meta)
    save_json(META / 'props.json', dict(props=props, scene={}))
    save_json(META / 'action_aliases.json', {cid: c['amap'] for cid, c in meta['chars'].items()})
    print(f'完成：{len(meta["chars"])} 个图集，{len(props)} 个道具')


if __name__ == '__main__':
    main()
