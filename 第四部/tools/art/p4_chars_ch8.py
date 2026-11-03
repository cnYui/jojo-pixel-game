# 第8章的人物图集（第四部/docs/分章开发约定.md 第 5 节：本章负责画吉良吉广、大柳贤 / Boy II Man、川尻忍）。
#   写法照 p4_chars.py：拿第三部的全尺寸图集换色、换发型，再缩成 chibi；元数据写 _meta/chars_ch8.json（build_p4.py 自动深合并）。
#   另外三个 ph8_* 是临时占位：露伴（第5章画）、乔瑟夫（第4章画）、川尻浩作（第7章画）还没合进来时第8章先用它们，
#   story/p4_ch8.js 只在 G.D.chars 里没有正式 cid（rohan / joseph_old / kawajiri）时才用占位，正式图一合并就自动换掉。
#   配色以 TV 动画第四部为准；原著细节没逐格核的地方写在 docs/第8章_开发脚本.md 的待核里。
#   用法：python3 第四部/tools/art/p4_chars_ch8.py [cid ...]
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402

HUMAN = {'talk': 'idle', 'shock': 'hurt', 'run': 'walk'}


# ============================================================ 吉良吉广：照片里的老人。白发（头顶秃）、灰褐色开衫；进游戏后剧情再罩一层旧照片的褐色
def build_yoshihiro():
    cmap = {'#22463e': '#6a5a48', '#2a4e44': '#7a6a56', '#1e3830': '#4e4234', '#1d362f': '#4a3e30',
            '#aa2e32': '#8a6a4a', '#702830': '#5a4430'}
    hair = {'#402a22': '#d6d4d0', '#725c44': '#a8a6a2'}
    return C.build_recolor('yoshihiro', '吉良吉广', 'npc_dealer',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'),
                            ('down', 'down', 1, 'static'), ('deal', 'throw', 6, 'oneshot'), ('talk', 'talk', 4, 'loop')],
                           cmap=cmap, hair=hair, skin=[(230, 174, 126), (164, 104, 82)],
                           amap={'shock': 'hurt', 'run': 'walk', 'cmd': 'throw', 'punch': 'throw'}, bodyW=4)


# ============================================================ 大柳贤：小学生，深色头发、蓝紫上衣（Boy II Man 的本体）
def build_oyanagi():
    cmap = {'#e49436': '#7a68c8', '#a46a26': '#4e3e94', '#ffbd4c': '#a898ec', '#525e68': '#3a3a4a', '#3b434a': '#26262e', '#394148': '#24242c'}
    e = C.build_recolor('oyanagi', '大柳贤', 'npc_kid',
                        [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('run', 'run', 10, 'loop'),
                         ('hurt', 'hurt', 1, 'static'), ('talk', 'talk', 4, 'loop')],
                        cmap=cmap, amap={'shock': 'hurt'}, bodyW=3)
    # 头像不用 npc_kid 的（那张鼻子下面一撇像胡子）：换成男学生的脸，黑发、蓝紫上衣，看着更像小学生
    hair = {(28, 26, 34): (40, 30, 26), (12, 10, 16): (20, 14, 12), (58, 54, 68): (74, 56, 46), (18, 19, 24): (30, 22, 18)}
    shirt = {'#22242e': '#4e3e94', '#3a3e4e': '#7a68c8', '#121318': '#2e2460'}
    nm = [C.recolor(C.head_recolor(f, hair, None, 32), shirt) for f in C.heads('npc_student_m')['portrait']]
    if len(nm) == 1:
        nm = nm * 2
    hd = {'normal': nm, 'smile': [C.HD.smile(f) for f in nm], 'shock': [C.HD.shock(f, i) for i, f in enumerate(nm)], 'rage': nm}
    for emo, frs in hd.items():
        for i, f in enumerate(frs):
            f.save(os.path.join(L.ASSETS, 'heads', 'oyanagi', f'{emo}_{i}.png'))
    return e


# ============================================================ 川尻忍：浅褐色短卷发，米色连衣裙 + 粉色开衫（holly 的身体）
def build_shinobu():
    cmap = {'#f8e08e': '#b8845a', '#fff6cc': '#d8a878', '#d2a650': '#7c5434',
            '#c6daf4': '#efe0c4', '#8ea8d6': '#c4ac88', '#a6c6ea': '#dcc8a6', '#6f93c9': '#a08a66', '#e4eefa': '#fbf2de',
            '#f592be': '#e88a9a', '#c95f8f': '#b85a6a', '#e0506a': '#d06a7a', '#ffc8de': '#f6b8c0'}
    return C.build_recolor('shinobu', '川尻忍', 'holly',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('wave', 'wave', 4, 'loop')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'wave', 'run': 'walk'}, bodyW=4)


# ============================================================ 临时占位（正式图由别章画）
def build_ph_rohan():
    # 第5章画正式的露伴：这里只是绿发 + 黑上衣的同学身体
    cmap = {'#b8402e': '#2e6a4e', '#e8734c': '#4a8e68', '#78221e': '#16402c',
            '#2f9e56': '#2a2a34', '#1a6038': '#1a1a22', '#62c874': '#46464f', '#0f4028': '#101016', '#50b848': '#38383f'}
    return C.build_recolor('ph8_rohan', '岸边露伴（占位）', 'kakyoin',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('cast', 'point', 4, 'loop'),
                            ('hurt', 'hurt', 1, 'static'), ('guard', 'guard', 1, 'static'), ('dodge', 'dodge', 1, 'static')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'hurt', 'run': 'walk', 'pose': 'point'}, bodyW=4)


def build_ph_joseph():
    # 第4章画正式的 79 岁乔瑟夫：这里用第三部乔瑟夫的身体，大衣换成灰绿
    cmap = {'#b9a66a': '#8a8a7a', '#dcbc78': '#aaa898', '#a07c44': '#6a6a5c', '#857444': '#5a5a4e'}
    return C.build_recolor('ph8_joseph', '乔瑟夫（占位）', 'joseph',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 6, 'loop'), ('point', 'point', 1, 'static'),
                            ('camera', 'camera', 4, 'loop'), ('shock', 'shock', 2, 'loop'), ('hurt', 'hurt', 1, 'static')],
                           cmap=cmap, amap={'talk': 'idle', 'run': 'walk'}, bodyW=4)


def build_ph_kosaku():
    # 第7章画正式的川尻浩作（换脸后的吉良）：这里是浅褐发、灰紫西装的上班族
    cmap = {'#eeeef2': '#f2f0ea', '#8a8a94': '#6a5e7a', '#5e5e6c': '#4e4460', '#44404a': '#3a3248', '#3a3440': '#2e2838'}
    hair = {'#242024': '#b08a5a', '#221e28': '#8a6a42', '#121014': '#5a4228'}
    return C.build_recolor('ph8_kosaku', '川尻浩作（占位）', 'npc_hk_owner',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop')],
                           cmap=cmap, hair=hair, amap={'talk': 'idle', 'shock': 'idle', 'run': 'walk'}, bodyW=3)


BUILDERS = {'yoshihiro': build_yoshihiro, 'oyanagi': build_oyanagi, 'shinobu': build_shinobu,
            'ph8_rohan': build_ph_rohan, 'ph8_joseph': build_ph_joseph, 'ph8_kosaku': build_ph_kosaku}

SPEAKERS = {
    'yoshihiro': dict(short='吉广', nameColor='#9a7a5a', blipHz=360),
    'oyanagi': dict(short='大柳', nameColor='#7a68c8', blipHz=880),
    'shinobu': dict(short='忍', nameColor='#c86a7a', blipHz=740),
    'hayato': dict(short='早人', nameColor='#6a7a9a', blipHz=700),
    'kawajiri': dict(short='吉良', nameColor='#7a5a9a', blipHz=420),
    'ph8_kosaku': dict(short='吉良', nameColor='#7a5a9a', blipHz=420),
    'rohan': dict(short='露伴', nameColor='#3e8a62', blipHz=580),
    'ph8_rohan': dict(short='露伴', nameColor='#3e8a62', blipHz=580),
    'joseph_old': dict(short='乔瑟夫', nameColor='#8a6ab0', blipHz=360),
    'ph8_joseph': dict(short='乔瑟夫', nameColor='#8a6ab0', blipHz=360),
    'boyiiman': dict(short='Boy II Man', nameColor='#7a68c8', blipHz=880),
    'atomheart': dict(short='原子心之父', nameColor='#9a7a5a', blipHz=360),
}
# 占位的露伴 / 乔瑟夫要能当队长（第 13 战、车站自由走动）：heroes 里登记占位 cid；正式的 rohan / joseph_old 由第5 / 第4章登记
HEROES = {
    'ph8_rohan': dict(cid='ph8_rohan', cn='岸边露伴', short='露伴', rn='KISHIBE ROHAN', stand=None,
                      burst=['#1a4a32', '#2e6a4e', '#f0d070'], panel='#0a2016', accent='#f0d070', nameColor='#3e8a62', blipHz=580, grunt=None),
    'ph8_joseph': dict(cid='ph8_joseph', cn='乔瑟夫·乔斯达', short='乔瑟夫', rn='JOSEPH JOESTAR', stand=None,
                       burst=['#3a1a5a', '#6a3a9a', '#c080ff'], panel='#160a24', accent='#c080ff', nameColor='#8a6ab0', blipHz=360, grunt=None),
}


def main(ids):
    path = os.path.join(L.META, 'chars_ch8.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', list(meta['chars'][cid]['animations']))
    meta['speakers'] = SPEAKERS
    meta['heroes'] = HEROES
    L.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
