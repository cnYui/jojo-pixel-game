# 第11章的人物图集（第四部/docs/分章开发约定.md 第 5 节：本章负责画乙雅三 / Cheap Trick）。
#   写法照 p4_chars.py：拿第三部的全尺寸图集换色、换发型，再缩成 chibi；元数据写 _meta/chars_ch11.json（build_p4.py 自动深合并）。
#   配色以 TV 动画第四部为准（JoJo Wiki 的配色表）：乙雅三 浅赤褐色头发、浅米色外套、橄榄绿衬衫、棕色裤子。
#   Cheap Trick 原作里没有官方动画配色可对（它只给本体看），这里画成灰紫色的小怪物：大脑袋、尖耳朵、黄眼睛、咧着的嘴。
#
#   另外几个 ph11_* 是临时占位：早人（第9章画）、川尻浩作（第7章画）、川尻忍（第8章画）、露伴（第5章画）、
#   亿泰（第2章画）、铃美（第6章画）、杀手皇后（第6章画）、猫草（第9章画）。那几章的正式图还没合进来，
#   story/p4_ch11.js 只在 G.D.chars 里没有正式 cid（hayato / kawajiri / shinobu / rohan / okuyasu / reimi / killerq）时才用占位，
#   正式图一合并就自动换掉。占位也尽量照 TV 动画配色（早人：姜黄色头发、黄绿背心、橄榄色长袖、酒红短裤）。
#   用法：python3 第四部/tools/art/p4_chars_ch11.py [cid ...]
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402

HUMAN = {'talk': 'idle', 'shock': 'hurt', 'run': 'walk'}


# ============================================================ 乙雅三：修露伴家房子的建筑师
def build_kinoto():
    cmap = {'#eeeef2': '#dccca4', '#ffffff': '#efe4c6', '#b8b8c8': '#b4a47c',      # 白衬衫 → 浅米色外套
            '#8a8a94': '#7a5a3e', '#5e5e6c': '#5e4430', '#44404a': '#4a3424', '#3a3440': '#3a2a1e'}   # 灰围裙 → 棕裤子
    hair = {'#242024': '#b8704e', '#221e28': '#8e4e34', '#121014': '#5e3020'}
    e = C.build_recolor('kinoto', '乙雅三', 'npc_hk_owner', [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop')],
                        cmap=cmap, hair=hair, amap={'talk': 'idle', 'shock': 'idle', 'run': 'walk', 'hurt': 'idle', 'down': 'idle'}, bodyW=3)
    return e


# ============================================================ Cheap Trick：贴在背上的小怪物（全尺寸画，save 时缩成 0.625）
CT = dict(o=(30, 20, 40), d=(74, 64, 98), m=(124, 112, 150), l=(176, 168, 204), x=(214, 208, 232),
          eye=(244, 224, 80), pupil=(40, 20, 30), mouth=(46, 22, 40), tooth=(250, 246, 236))


def ct_frame(mouth=0, bob=0, look=False, W=26, H=30):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y0 = 2 + bob
    # 小身子（缩着，像趴在人背上）+ 两只短手
    d.ellipse((8, y0 + 15, 20, y0 + 27), fill=CT['m'])
    d.ellipse((10, y0 + 17, 18, y0 + 25), fill=CT['l'])
    d.rectangle((5, y0 + 18, 9, y0 + 21), fill=CT['d'])
    d.rectangle((19, y0 + 18, 23, y0 + 21), fill=CT['d'])
    # 大脑袋 + 尖耳朵
    d.polygon([(3, y0 + 6), (7, y0 + 2), (8, y0 + 9)], fill=CT['m'])
    d.polygon([(23, y0 + 6), (19, y0 + 2), (18, y0 + 9)], fill=CT['m'])
    d.ellipse((5, y0 + 1, 21, y0 + 17), fill=CT['m'])
    d.ellipse((7, y0 + 2, 19, y0 + 12), fill=CT['l'])
    d.point((9, y0 + 4), fill=CT['x'])
    if look:
        # 回头看：只看得见后脑勺和耳朵
        d.ellipse((7, y0 + 3, 19, y0 + 15), fill=CT['d'])
        d.ellipse((9, y0 + 4, 17, y0 + 11), fill=CT['m'])
    else:
        # 黄色的斜眼
        d.polygon([(8, y0 + 7), (12, y0 + 8), (11, y0 + 10), (8, y0 + 9)], fill=CT['eye'])
        d.polygon([(18, y0 + 7), (14, y0 + 8), (15, y0 + 10), (18, y0 + 9)], fill=CT['eye'])
        d.point((10, y0 + 9), fill=CT['pupil'])
        d.point((16, y0 + 9), fill=CT['pupil'])
        # 嘴：0 咧着笑 / 1 张开说话
        if mouth:
            d.ellipse((10, y0 + 11, 16, y0 + 16), fill=CT['mouth'])
            d.line((11, y0 + 12, 15, y0 + 12), fill=CT['tooth'])
        else:
            d.line((9, y0 + 12, 17, y0 + 12), fill=CT['mouth'])
            d.line((9, y0 + 12, 8, y0 + 11), fill=CT['mouth'])
            d.line((17, y0 + 12, 18, y0 + 11), fill=CT['mouth'])
            for x in (11, 13, 15):
                d.point((x, y0 + 13), fill=CT['tooth'])
    return C.reoutline(im, CT['o'])


def build_cheaptrick():
    sh = C.Sheet('cheaptrick', 'Cheap Trick', (26, 30), (13, 29))
    sh.add('idle', [ct_frame(0, 0), ct_frame(0, 1)], 3, 'loop')
    sh.add('talk', [ct_frame(1, 0), ct_frame(0, 0)], 6, 'loop')
    sh.add('look', [ct_frame(0, 0, True)], 1, 'static')
    big = [ct_frame(m, 0).resize((52, 60), Image.NEAREST) for m in (0, 1)]
    hd = []
    for b in big:
        face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        face.alpha_composite(b.crop((10, 2, 42, 34)))
        hd.append(face)
    sh.heads = {'normal': hd}
    e = C.save(sh, amap={'walk': 'idle', 'run': 'idle', 'hurt': 'look', 'down': 'look', 'shock': 'look', 'cmd': 'talk', 'punch': 'talk',
                         'special': 'talk', 'guard': 'idle', 'dodge': 'idle'}, kind='stand', bodyW=3)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 临时占位（正式图由别章画）
def kid_heads(cid, hair, shirt):
    """npc_kid 的头像鼻子下面一撇像胡子：换成男学生的脸（第8章大柳贤同样做法）"""
    nm = [C.recolor(C.head_recolor(f, hair, None, 32), shirt) for f in C.heads('npc_student_m')['portrait']]
    if len(nm) == 1:
        nm = nm * 2
    hd = {'normal': nm, 'smile': [C.HD.smile(f) for f in nm], 'shock': [C.HD.shock(f, i) for i, f in enumerate(nm)], 'rage': nm}
    out = os.path.join(L.ASSETS, 'heads', cid)
    os.makedirs(out, exist_ok=True)
    for emo, frs in hd.items():
        for i, f in enumerate(frs):
            f.save(os.path.join(out, f'{emo}_{i}.png'))


def build_ph_hayato():
    # TV 动画第一套：姜黄色头发、黄绿背心、橄榄色长袖、酒红短裤（第9章画正式的）
    cmap = {'#e49436': '#a8c83a', '#a46a26': '#6c8a26', '#ffbd4c': '#d2e86a', '#525e68': '#8a2a3a', '#3b434a': '#5e1a28', '#394148': '#5a1826',
            '#2c1e18': '#c8682e', '#725c44': '#e08a44'}     # 头发的颜色只在头发上出现，直接全身换（npc_kid 的脸框找不准）
    e = C.build_recolor('ph11_hayato', '川尻早人（占位）', 'npc_kid',
                        [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('run', 'run', 10, 'loop'),
                         ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'), ('talk', 'talk', 4, 'loop')],
                        cmap=cmap, amap={'shock': 'hurt', 'guard': 'down', 'dodge': 'run'}, bodyW=3)
    kid_heads('ph11_hayato', {(28, 26, 34): (200, 104, 46), (12, 10, 16): (140, 66, 26), (58, 54, 68): (226, 140, 72), (18, 19, 24): (170, 84, 34)},
              {'#22242e': '#6c8a26', '#3a3e4e': '#a8c83a', '#121318': '#46601a'})
    return e


def build_ph_kosaku():
    # 第7章画正式的川尻浩作（换脸后的吉良）：浅褐发、灰紫西装（和第8章的占位同一套配方）
    cmap = {'#eeeef2': '#f2f0ea', '#8a8a94': '#6a5e7a', '#5e5e6c': '#4e4460', '#44404a': '#3a3248', '#3a3440': '#2e2838'}
    hair = {'#242024': '#b08a5a', '#221e28': '#8a6a42', '#121014': '#5a4228'}
    return C.build_recolor('ph11_kosaku', '川尻浩作（占位）', 'npc_hk_owner', [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop')],
                           cmap=cmap, hair=hair, amap={'talk': 'idle', 'shock': 'idle', 'run': 'walk', 'hurt': 'idle', 'down': 'idle'}, bodyW=3)


def build_ph_shinobu():
    # 第8章画正式的川尻忍：浅褐色短卷发，米色连衣裙 + 粉色开衫（和第8章同一套配方）
    cmap = {'#f8e08e': '#b8845a', '#fff6cc': '#d8a878', '#d2a650': '#7c5434',
            '#c6daf4': '#efe0c4', '#8ea8d6': '#c4ac88', '#a6c6ea': '#dcc8a6', '#6f93c9': '#a08a66', '#e4eefa': '#fbf2de',
            '#f592be': '#e88a9a', '#c95f8f': '#b85a6a', '#e0506a': '#d06a7a', '#ffc8de': '#f6b8c0'}
    return C.build_recolor('ph11_shinobu', '川尻忍（占位）', 'holly', [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'idle', 'run': 'walk', 'hurt': 'idle'}, bodyW=4)


def build_ph_rohan():
    # 第5章画正式的露伴：这里只是绿发 + 黑上衣的同学身体（和第8章的占位同一套配方）
    cmap = {'#b8402e': '#2e6a4e', '#e8734c': '#4a8e68', '#78221e': '#16402c',
            '#2f9e56': '#2a2a34', '#1a6038': '#1a1a22', '#62c874': '#46464f', '#0f4028': '#101016', '#50b848': '#38383f'}
    return C.build_recolor('ph11_rohan', '岸边露伴（占位）', 'kakyoin',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('cast', 'point', 4, 'loop'),
                            ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'), ('guard', 'guard', 1, 'static'), ('dodge', 'dodge', 1, 'static')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'hurt', 'run': 'walk', 'pose': 'point'}, bodyW=4)


def build_ph_okuyasu():
    # 第2章画正式的亿泰：深灰学生服、灰黑头发
    cmap = {'#2f9e56': '#3c3c4a', '#1a6038': '#25252e', '#62c874': '#55556a', '#0f4028': '#16161c', '#50b848': '#4a4a5c',
            '#b8402e': '#4a4a52', '#e8734c': '#6a6a74', '#78221e': '#2a2a30', '#9a4ce0': '#3a2a2a'}
    return C.build_recolor('ph11_okuyasu', '虹村亿泰（占位）', 'kakyoin',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'hurt', 'run': 'walk'}, bodyW=4)


def build_ph_reimi():
    # 第6章画正式的铃美（幽灵小路里的女孩）：粉发、深蓝校服
    hair = {'#1e1a22': '#e4a0bc', '#0e0c12': '#b06a8a', '#3e3846': '#f6c8da'}
    return C.build_recolor('ph11_reimi', '杉本铃美（占位）', 'npc_student_f_a', [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop')],
                           cmap={}, hair=hair, amap={'talk': 'idle', 'shock': 'idle', 'run': 'walk', 'hurt': 'idle'}, bodyW=3)


def build_ph_killerq():
    # 第6章画正式的杀手皇后：粉白身子、深紫手套和腰带
    cmap = {'#bab2ff': '#f8d4e6', '#8a80ec': '#eaa6c8', '#5242ae': '#b86894', '#33257a': '#6e3460',
            '#5a56a0': '#f4e8f0', '#2c2852': '#c8a8c0', '#17132e': '#7a5a78',
            '#ff8a78': '#8a5ab0', '#ec3040': '#5e3a8a', '#98182c': '#3a2060',
            '#fff6b4': '#ffffff', '#ffd83c': '#d8c8e8', '#c08a18': '#8a7aa0', '#b69ec6': '#e8bcd4'}
    im, m = C.base('starplat')
    sh = C.Sheet('ph11_killerq', '杀手皇后（占位）', m['cell'], m['pivot'])
    for anim in ('idle', 'punch', 'block', 'pose', 'reach'):
        a = m['animations'][anim]
        sh.add(anim, [C.recolor(f, cmap) for f in C.frames('starplat', anim)], a.get('fps', 6), a.get('kind', 'loop'))
    sh.heads = {'normal': [C.recolor(f, cmap) for f in C.heads('starplat')['portrait']]}
    e = C.save(sh, amap={'punch': 'punch', 'block': 'block', 'hurt': 'block', 'special': 'pose', 'rush': 'punch'}, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


BUILDERS = {'kinoto': build_kinoto, 'cheaptrick': build_cheaptrick,
            'ph11_hayato': build_ph_hayato, 'ph11_kosaku': build_ph_kosaku, 'ph11_shinobu': build_ph_shinobu,
            'ph11_rohan': build_ph_rohan, 'ph11_okuyasu': build_ph_okuyasu, 'ph11_reimi': build_ph_reimi,
            'ph11_killerq': build_ph_killerq}

SPEAKERS = {
    'kinoto': dict(short='乙雅三', nameColor='#b8704e', blipHz=430),
    'cheaptrick': dict(short='Cheap Trick', nameColor='#8a80b0', blipHz=980),
    'ph11_kosaku': dict(short='爸爸', nameColor='#7a5a9a', blipHz=420),
    'ph11_shinobu': dict(short='妈妈', nameColor='#c86a7a', blipHz=740),
    'ph11_reimi': dict(short='铃美', nameColor='#d080a0', blipHz=800),
    'ph11_okuyasu': dict(short='亿泰', nameColor='#5a5a8a', blipHz=420),
    'ph11_killerq': dict(short='杀手皇后', nameColor='#c06a9a', blipHz=500),
}
# 占位的早人 / 露伴要能当队长（插曲、第 17、18 战）：heroes 里登记占位 cid；正式的 hayato / rohan 由第9 / 第5章登记
HEROES = {
    'ph11_hayato': dict(cid='ph11_hayato', cn='川尻早人', short='早人', rn='KAWAJIRI HAYATO', stand=None,
                        burst=['#5a3a0a', '#a86a2a', '#e8b860'], panel='#20140a', accent='#d2e86a', nameColor='#c8682e', blipHz=700, grunt=None),
    'ph11_rohan': dict(cid='ph11_rohan', cn='岸边露伴', short='露伴', rn='KISHIBE ROHAN', stand=None,
                       burst=['#1a4a32', '#2e6a4e', '#f0d070'], panel='#0a2016', accent='#f0d070', nameColor='#3e8a62', blipHz=580, grunt=None),
}
STANDS = {
    'cheaptrick': dict(cn='Cheap Trick', en='CHEAP TRICK', owner='kinoto', aura='#a898d0', card='#c8c0e8', ghost='#dcd6f0',
                       impact='blue', kind='humanoid', idle={'dx': -4, 'z': 18}, link=None, summonSfx=None, fist=False),
    'ph11_killerq': dict(cn='杀手皇后', en='KILLER QUEEN', owner='ph11_kosaku', aura='#e898c0', card='#f8c0dc', ghost='#fbe0ee',
                         impact='pink', kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx='stand_summon_star', fist=True),
}


def main(ids):
    path = os.path.join(L.META, 'chars_ch11.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', list(meta['chars'][cid]['animations']))
    meta['speakers'] = SPEAKERS
    meta['heroes'] = HEROES
    meta['stands'] = STANDS
    L.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
