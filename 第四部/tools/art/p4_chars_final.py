# 终章的人物：女急救员（终章自己的），以及前面各章还没画好的人的暂代版（cid 都以 fin_ 开头，和正式版错开）。
#   做法和 p4_chars.py 一样：拿第三部的全尺寸图集换色（配色照 TV 动画，见 第四部/docs/终章_开发脚本.md 0.1 节），再缩成游戏尺寸。
#   正式版（kira、okuyasu、hayato……）由负责的那一章画；剧情代码按“正式版有就用正式版”取人，这里的暂代版到时候自然不用了。
#   用法：python3 第四部/tools/art/p4_chars_final.py [cid ...]     → assets/chars/<cid>.png、heads/<cid>/…、_meta/chars_final.json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402

O = C.O


# ============================================================ 小工具
def cat_ears(f, col=(244, 184, 204), dark=(200, 122, 154)):
    """杀手皇后的猫耳：在头顶最高一行的左右两端各立一个小三角（全尺寸图上 4 px 高）"""
    a = np.array(f.convert('RGBA'))
    op = np.where(a[..., 3] > 0)
    if not len(op[0]):
        return f
    y0 = int(op[0].min())
    xs = np.where(a[y0 + 1, :, 3] > 0)[0] if y0 + 1 < a.shape[0] else np.where(a[y0, :, 3] > 0)[0]
    if not len(xs):
        return f
    for cx in (int(xs.min()) + 1, int(xs.max()) - 1):
        for k in range(4):
            y = y0 - k
            if y < 0:
                continue
            for x in range(cx - (3 - k) // 2, cx + (3 - k) // 2 + 1):
                if 0 <= x < a.shape[1]:
                    a[y, x] = (*(col if k < 3 else dark), 255)
    return C.reoutline(Image.fromarray(a, 'RGBA'))


def shrink_frame(f, k):
    """整格缩小（底边居中对齐）：回音 ACT3 比别的替身小一圈"""
    w, h = f.size
    s = f.resize((max(1, int(w * k)), max(1, int(h * k))), Image.NEAREST)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.alpha_composite(s, ((w - s.width) // 2, h - s.height - int(h * (1 - k) * 0.25)))
    return out


def stand_sheet(cid, name, src, cmap, frame_fn=None, skip=('portrait',)):
    im, m = C.base(src)
    sh = C.Sheet(cid, name, m['cell'], m['pivot'])
    for anim, a in m['animations'].items():
        if anim.startswith(skip):
            continue
        frs = [C.recolor(f, cmap) for f in C.frames(src, anim)]
        if frame_fn:
            frs = [frame_fn(f) for f in frs]
        sh.add(anim, frs, a.get('fps', 6), a.get('kind', 'loop'))
    hd = C.heads(src)
    pf = hd.get('portrait') or next(iter(hd.values()), None)
    if pf:
        sh.heads = {'normal': [C.recolor(f, cmap) for f in pf]}
    return sh


STAND_AMAP = {'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'punch', 'rush': 'rush', 'block': 'pose', 'hurt': 'hurt',
              'special': 'rush', 'reach': 'punch', 'finger': 'punch', 'upper': 'punch'}


# ============================================================ 吉良吉影（川尻浩作的脸）：黑发黑眼，白西装 + 淡紫衬衫
WHITE_SUIT = {'#22222e': '#e4e0ec', '#40405a': '#ffffff', '#3a3a4e': '#f2eef8', '#1f1a2e': '#bab2ca', '#101018': '#a098b4',
              '#1e1430': '#8c84a4', '#08080c': '#6e6888', '#20182a': '#8c84a4',
              # 领带（原来的紫）→ 黑绿白，衬衫领口淡紫
              '#9a4868': '#2e5a4a', '#ffffff': '#e6d8f4'}
KIRA_HAIR = {(62, 44, 82): (30, 28, 36), (138, 88, 180): (78, 74, 90), (108, 84, 136): (52, 48, 62), (94, 57, 120): (40, 37, 48)}


def build_kira():
    # 第三部丹尼尔的弟弟（游戏手柄）当底子：手柄只出现在待机、走路、挨打三行的右半边，挖掉
    def no_pad(f):
        f = C.recolor(f, {'#c4c4d4': None, '#e0303c': None, '#3c64dc': None, '#7c7c90': None}, box=(30, 0, 70, 52))
        return C.strip_outline(f)
    e = C.build_recolor('fin_kira', '吉良吉影', 'telence',
                        [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('punch', 'point', 6, 'oneshot'),
                         ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static')],
                        cmap=WHITE_SUIT, hair=KIRA_HAIR, skin=[(246, 196, 154), (216, 148, 108)], frame_fn=no_pad,
                        amap={'talk': 'idle', 'shock': 'hurt', 'cmd': 'point', 'cmd2': 'point', 'cmd_hold': 'point', 'guard': 'hurt',
                              'dodge': 'walk', 'special': 'point', 'win': 'idle', 'run': {'a': 'walk', 'f': 1.6}, 'getup': 'hurt',
                              'pose': 'point', 'kneel': 'hurt'}, bodyW=4)
    return e


# ============================================================ 杀手皇后：浅粉身体，深紫手套靴子腰布，银钉金片，猫耳
KQ_MAP = {'#f6c63a': '#f4b8cc', '#b8841a': '#c87a9a', '#7a520e': '#8a4a6a', '#fff6c0': '#ffe4ee', '#ffe070': '#ffd0e0',
          '#e8a820': '#d890b0', '#3cc46a': '#6a3a8a', '#1b7040': '#46245e', '#0e3a24': '#2a1238', '#a8f080': '#9a6ac0',
          '#801020': '#c8c8d8', '#d02838': '#ffffff'}


def build_kq():
    sh = stand_sheet('fin_kq', '杀手皇后', 'theworld', KQ_MAP, frame_fn=cat_ears)
    e = C.save(sh, amap=STAND_AMAP, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 轰炸空间（动画配色没查到：浅蓝白身体、深蓝、金色）
HAND_MAP = {'#bab2ff': '#f0f8ff', '#8a80ec': '#c8e0f2', '#5242ae': '#7ea4c8', '#33257a': '#4a6a90', '#2c2852': '#2c4a6c',
            '#17132e': '#1a2c44', '#5a56a0': '#2c3a5a', '#ec3040': '#2a3a78', '#98182c': '#1a2450', '#ff8a78': '#4a5aa8',
            '#b69ec6': '#d8e4f0'}


def build_thehand():
    sh = stand_sheet('fin_thehand', '轰炸空间', 'starplat', HAND_MAP)
    e = C.save(sh, amap=STAND_AMAP, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 回音 ACT3：浅灰身体、翠绿条纹、金色指节，比别的替身小一圈
ACT3_MAP = {'#bab2ff': '#eceef2', '#8a80ec': '#bcc0c8', '#5242ae': '#80868f', '#33257a': '#565c66', '#2c2852': '#3e434c',
            '#17132e': '#24272e', '#5a56a0': '#1ea86a', '#ec3040': '#22b874', '#98182c': '#127048', '#ff8a78': '#7ae0a8',
            '#b69ec6': '#d4d8de', '#fff6b4': '#fff0a0'}


def build_echoes3():
    sh = stand_sheet('fin_echoes3', '回音 ACT3', 'starplat', ACT3_MAP, frame_fn=lambda f: shrink_frame(f, 0.62))
    e = C.save(sh, amap=STAND_AMAP, kind='stand', bodyW=4)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 花京院的身体换校服 / 发色：亿泰、形兆、露伴
KAK_ANIMS = [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('cast', 'point', 6, 'oneshot'), ('hurt', 'hurt', 1, 'static'),
             ('down', 'down', 1, 'static'), ('dodge', 'dodge', 1, 'static'), ('guard', 'guard', 1, 'static')]
KAK_AMAP = {'talk': 'idle', 'shock': 'hurt', 'cmd': 'point', 'cmd2': 'point', 'cmd_hold': 'point', 'special': 'point', 'win': 'point',
            'run': {'a': 'walk', 'f': 1.6}, 'getup': 'hurt', 'pose': 'point', 'kneel': 'down', 'sit': 'down'}
KAK_HAIR = ('#b8402e', '#e8734c', '#78221e')


def build_kak(cid, name, uni, hair, eyes):
    cmap = dict(uni)
    cmap.update(dict(zip(KAK_HAIR, hair)))
    cmap['#9a4ce0'] = eyes
    return C.build_recolor(cid, name, 'kakyoin', KAK_ANIMS, cmap=cmap, amap=KAK_AMAP, bodyW=4)


BLUE_UNI = {'#2f9e56': '#3a58a8', '#1a6038': '#24366e', '#62c874': '#6a88d0', '#0f4028': '#141e44', '#50b848': '#5070c0'}


def build_okuyasu():
    return build_kak('fin_okuyasu', '虹村亿泰', BLUE_UNI, ('#2a2630', '#8a8894', '#121016'), '#8a8a98')


def build_keicho():
    return build_kak('fin_keicho', '虹村形兆', C.BLACK_UNI, ('#d8bc5c', '#fff0a8', '#9a7a30'), '#3aa860')


def build_rohan():
    vest = {'#2f9e56': '#a8d890', '#1a6038': '#6c9c58', '#62c874': '#d0f0b8', '#0f4028': '#44703a', '#50b848': '#90c878',
            '#ffd83c': '#c8a8e0', '#c89a20': '#9a7ab8'}
    return build_kak('fin_rohan', '岸边露伴', vest, ('#2a5a3c', '#4c8a5c', '#163424'), '#3aa860')


# ============================================================ 早人、铃美、忍、急救员、阿诺德、乔瑟夫
def hayato_head(f):
    # 第三部那个小孩的头像是墨镜眼 + 一撮小胡子，早人是小学生：墨镜那一行改回皮肤只留两个眼珠，胡子改成皮肤
    a = np.array(f.convert('RGBA'))
    sk, ink = (230, 174, 126, 255), (20, 18, 30, 255)
    if a.shape[0] >= 32:
        for x in range(17, 24):
            a[12, x] = ink if x in (18, 22) else sk
        for x in range(18, 23):
            a[19, x] = sk
        a[20, 19] = ink
    return Image.fromarray(a, 'RGBA')


def build_hayato():
    cmap = {'#2c1e18': '#c8742c', '#e49436': '#c49a6a', '#a46a26': '#8a6440', '#ffbd4c': '#e0c098',
            '#525e68': '#3a5aa0', '#3b434a': '#26407a', '#394148': '#2a4480'}
    return C.build_recolor('fin_hayato', '川尻早人', 'npc_kid',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('run', 'run', 10, 'loop'),
                            ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'), ('talk', 'talk', 4, 'loop')],
                           cmap=cmap, skin=[(230, 174, 126), (164, 104, 82)], head_edit=hayato_head, amap={'shock': 'hurt', 'cry': 'hurt'}, bodyW=3)


def build_reimi():
    cmap = {'#1e1a22': '#f08cb4', '#0e0c12': '#b85482', '#3e3846': '#ffc0d8', '#2c3462': '#f4c4d4', '#181d3e': '#d898b0',
            '#e0303c': '#f0d040', '#9a2a44': '#c0a020'}
    return C.build_recolor('fin_reimi', '杉本铃美', 'npc_student_f_a',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('cheer', 'wave', 4, 'loop')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'idle', 'smile': 'wave'}, bodyW=3)


def build_shinobu():
    cmap = {'#462e22': '#c85a74', '#744834': '#e888a0', '#533325': '#a84860', '#513224': '#a44a5e',
            '#d29e5e': '#f2eee8', '#977143': '#b8b4c8', '#9d7646': '#c4c0d2', '#8e6b3f': '#a8a4b8', '#ffc97c': '#ffffff',
            '#f2c656': '#8a9ad8'}
    return C.build_recolor('fin_shinobu', '川尻忍', 'npc_villager_f',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('talk', 'talk', 4, 'loop')],
                           cmap=cmap, skin=[(230, 174, 126), (164, 104, 82)], amap={'shock': 'idle'}, bodyW=3)


def build_paramedic():
    cmap = {'#f6f6fa': '#c8d4e4', '#bcc0d2': '#8e9cb4', '#a8c8ee': '#7c94c0', '#6e90c8': '#4e6494', '#f2f2f6': '#d4dcea',
            '#f8c6d6': '#f4f4f8', '#d88ea8': '#c4c8d4', '#d8e8fb': '#e6ecf4'}
    return C.build_recolor('paramedic', '女急救员', 'npc_nurse',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'idle', 'run': {'a': 'walk', 'f': 1.7}}, bodyW=3)


def build_arnold():
    cmap = {'#36313f': '#ece8f0', '#221e2a': '#b8b4c4', '#5c566e': '#ffffff', '#0c0a10': '#8a8698', '#b8b8ca': '#d0ccd8'}
    return C.build_recolor('fin_arnold', '阿诺德', 'iggy',
                           [('idle', 'idle', 2, 'loop'), ('run', 'walk', 10, 'loop'), ('sit', 'sit', 1, 'static'), ('bite', 'bite', 6, 'oneshot')],
                           cmap=cmap, amap={'talk': 'idle', 'run': 'walk', 'shock': 'idle'}, bodyW=4)


def build_joseph():
    return C.build_recolor('fin_joseph', '乔瑟夫·乔斯达', 'joseph',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 6, 'loop'), ('shock', 'shock', 1, 'static'), ('point', 'point', 4, 'oneshot')],
                           cmap={}, amap={'talk': 'idle', 'run': 'walk', 'hurt': 'shock'}, bodyW=4)


BUILDERS = {'fin_kira': build_kira, 'fin_kq': build_kq, 'fin_thehand': build_thehand, 'fin_echoes3': build_echoes3,
            'fin_okuyasu': build_okuyasu, 'fin_keicho': build_keicho, 'fin_rohan': build_rohan, 'fin_hayato': build_hayato,
            'fin_reimi': build_reimi, 'fin_shinobu': build_shinobu, 'paramedic': build_paramedic, 'fin_arnold': build_arnold,
            'fin_joseph': build_joseph}

# 主角表 / 说话人 / 替身表（格式照 p4_cast.py）
HEROES = {
    'fin_okuyasu': dict(cid='fin_okuyasu', cn='虹村亿泰', short='亿泰', rn='NIJIMURA OKUYASU', stand='fin_thehand',
                        burst=['#1a2a5a', '#2c4a9a', '#6a8ae0'], panel='#0a1230', accent='#8ab0ff', nameColor='#3a5ab0',
                        blipHz=380, grunt='grunt_jotaro'),
}
SPEAKERS = {
    'fin_kira': dict(short='吉良', nameColor='#a090c0', blipHz=420),
    'fin_kq': dict(short='杀手皇后', nameColor='#d080a0', blipHz=420),
    'fin_hayato': dict(short='早人', nameColor='#c8742c', blipHz=860),
    'fin_okuyasu': dict(short='亿泰', nameColor='#3a5ab0', blipHz=380),
    'fin_rohan': dict(short='露伴', nameColor='#3a8a5a', blipHz=520),
    'fin_reimi': dict(short='铃美', nameColor='#e070a0', blipHz=760),
    'fin_keicho': dict(short='形兆', nameColor='#b89a40', blipHz=400),
    'fin_shinobu': dict(short='忍', nameColor='#c85a74', blipHz=700),
    'paramedic': dict(short='急救员', nameColor='#5a74a8', blipHz=720),
    'fin_arnold': dict(short='阿诺德', nameColor='#9a98a8', blipHz=900),
    'fin_joseph': dict(short='乔瑟夫', nameColor='#8a6a3a', blipHz=360),
    'yoshihiro': dict(short='吉广', nameColor='#8a7a6a', blipHz=560),
    'neighbor': dict(short='邻居', nameColor='#7a7a6a', blipHz=600),
}
STANDS = {
    'fin_kq': dict(cn='杀手皇后', en='KILLER QUEEN', owner='fin_kira', aura='#e080b0', card='#f4b8cc', ghost='#ffd0e4',
                   impact='pink', kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx='stand_summon_star', fist=True),
    'fin_thehand': dict(cn='轰炸空间', en='THE HAND', owner='fin_okuyasu', aura='#8ab0ff', card='#c8e0f2', ghost='#e0f0ff',
                        impact='blue', kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx='stand_summon_star', fist=True),
    'fin_echoes3': dict(cn='回音 ACT3', en='ECHOES ACT3', owner='koichi', aura='#40d890', card='#a0f0c8', ghost='#c8ffe0',
                        impact='green', kind='humanoid', idle={'dx': -8, 'z': 10}, link=None, summonSfx='stand_summon_star', fist=True),
}


def main(ids):
    path = os.path.join(L.META, 'chars_final.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', list(meta['chars'][cid]['animations']))
    meta['heroes'] = dict(HEROES)
    meta['speakers'] = dict(SPEAKERS)
    meta['stands'] = dict(STANDS)
    L.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
