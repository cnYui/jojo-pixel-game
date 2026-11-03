# 第10章的新角色：钢田一丰大（Superfly 是铁塔本身，不画替身）、宫本辉之辅（谜靠纸道具，不画人形替身）；
#   外加第9章那边要画的未起隆、喷上裕也 / 公路之星的临时版（cid 带 _tmp）：第9章的正式图集合进来以前先顶着用，
#   剧情里先查 G.D.chars 有没有正式 cid，有就用正式的（第四部/docs/分章开发约定.md 第 5 节：一个人只由第一次出场那章画）。
#   配色照 TV 动画（JoJo Wiki 配色表，2026-11-03 查）：
#     丰大  姜黄色头发、青眼、绿帽、绿配紫的短上衣 + 背带、深绿裤、金色饰物
#     辉之辅 白色往上翘的头发、浅褐皮肤、青到紫的眼睛、白配棕的外套、里面黑衣、棕皮带、黑红鞋
#   用法：python3 第四部/tools/art/p4_chars_ch10.py [cid ...] → assets/chars/<cid>.png、assets/heads/<cid>/…、assets/_meta/chars_ch10.json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402
import p4_heads as HD  # noqa: E402

META = os.path.join(L.META, 'chars_ch10.json')


# ============================================================ 钢田一丰大：第三部 devo 的身子（短上衣、斜挎带、帽子），换动画配色
def toyo_frame(f):
    # devo 的描边是 #14121e，和第四部统一的 #1a1020 差一点：统一一下，缩小时描边优先才认得出来
    return C.recolor(f, {'#14121e': '#1a1020'})


def build_toyohiro():
    cmap = {
        # 上衣：绿色主体，暗部换紫（动画里是绿配紫两色）
        '#4e7466': '#4ea050', '#699786': '#7cc870', '#385349': '#5a3a86', '#354e45': '#3e2868',
        # 斜挎带 → 金色背带
        '#b88e5e': '#f0c040', '#b8845e': '#d8946c',
        # 裤子 → 深绿
        '#4e3448': '#2e5236', '#382533': '#1e3a26',
        '#743a38': '#a0602c', '#a43a3a': '#c8782c',
    }
    # 帽子（devo 头上那顶深色的）换绿色、露出来的头发换姜黄：只在头部换
    hair = {(50, 34, 42): (70, 150, 70), (56, 37, 51): (40, 110, 52), (56, 44, 40): (226, 130, 40), (164, 104, 82): (240, 160, 60)}
    e = C.build_recolor('toyohiro', '钢田一丰大', 'devo',
                        [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'),
                         ('down', 'down', 1, 'static'), ('slash', 'kick', 6, 'oneshot'), ('talk', 'talk', 4, 'loop')],
                        cmap=cmap, hair=hair, skin=[(184, 132, 94), (164, 104, 82)],
                        amap={'shock': 'hurt', 'run': {'a': 'walk', 'f': 1.6}, 'cmd': 'kick', 'cmd2': 'kick', 'punch': 'kick',
                              'guard': 'idle', 'dodge': 'walk', 'special': 'kick'},
                        bodyW=5, frame_fn=toyo_frame)
    return e


# ============================================================ 宫本辉之辅：第三部 kakyoin（瘦高、长外套）换白发、白棕外套
TERU_EYE = (64, 192, 208)


def build_terunosuke():
    cmap = {
        # 外套：白（主）+ 棕（暗部、下摆）
        '#2f9e56': '#ece6da', '#62c874': '#ffffff', '#50b848': '#f6f2ea', '#1a6038': '#8a6440', '#0f4028': '#5a3e26',
        # 金边 → 棕色皮带色
        '#ffd83c': '#b07a3c', '#c89a20': '#7a5028', '#ecc418': '#b07a3c', '#fff4a8': '#d8a868',
        # 皮肤：浅褐
        '#f6c49a': '#d9a77c', '#d8946c': '#b07850',
        # 眼睛：青紫
        '#9a4ce0': '#40c0d0',
        # 鞋：黑红
        '#5a361e': '#2a1a20', '#8a5a34': '#a02a34',
    }
    hair = {(184, 64, 46): (232, 232, 242), (232, 115, 76): (255, 255, 255), (120, 34, 30): (168, 168, 188)}
    e = C.build_recolor('terunosuke', '宫本辉之辅', 'kakyoin',
                        [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('cast', 'point', 4, 'loop'), ('hurt', 'hurt', 1, 'static'),
                         ('down', 'down', 1, 'static'), ('dodge', 'dodge', 1, 'static'), ('guard', 'guard', 1, 'static')],
                        cmap=cmap, hair=hair, skin=[(246, 196, 154), (216, 148, 108)],
                        amap={'talk': 'idle', 'shock': 'hurt', 'run': {'a': 'walk', 'f': 1.6}, 'cmd': 'point', 'cmd2': 'point',
                              'punch': 'point', 'special': 'point'},
                        bodyW=4)
    # 闭一只眼的头像（他害怕时的小动作）：右眼那一块换成皮肤 + 一道眼线
    path = os.path.join(L.ASSETS, 'heads', 'terunosuke')
    nm = [Image.open(os.path.join(L.ASSETS, k + '.png')).convert('RGBA') for k in e['heads']['normal']]
    winks = []
    for i, f in enumerate(nm):
        a = np.array(f)
        eye = (a[..., 0] == TERU_EYE[0]) & (a[..., 1] == TERU_EYE[1]) & (a[..., 2] == TERU_EYE[2])
        ys, xs = np.where(eye)
        if len(xs):
            right = xs >= np.median(xs)
            for y, x in zip(ys[right], xs[right]):
                a[y, x] = (217, 167, 124, 255)
            # 眼白也挖掉：同一行、靠近瞳孔的白像素
            yc = int(ys[right].mean())
            for x in range(int(xs[right].min()) - 2, int(xs[right].max()) + 3):
                if 0 <= x < a.shape[1]:
                    for y in (yc - 1, yc, yc + 1):
                        if tuple(a[y, x][:3]) == (255, 255, 255):
                            a[y, x] = (217, 167, 124, 255)
                    a[yc, x] = (*C.O, 255) if abs(x - xs[right].mean()) <= 2 else a[yc, x]
        w = Image.fromarray(a, 'RGBA')
        key = f'heads/terunosuke/wink_{i}'
        p = os.path.join(L.ASSETS, key + '.png')
        L.ensure(p)
        w.save(p)
        winks.append(key)
    e['heads']['wink'] = winks
    void = path
    del void
    return e


# ============================================================ 临时版：未起隆、裕也、公路之星（第9章交图后删）
def build_mikitaka_tmp():
    # 第三部 telence（矮个、黑发）：西装换成蓝紫色外套，领带换浅色
    cmap = {'#22222e': '#3a3a7a', '#101018': '#22224e', '#3a3a4e': '#5a5aa0', '#8a58b4': '#e8e8f0', '#6c5488': '#b0b0c8',
            '#3e2c52': '#1c1c2a', '#1e1430': '#101018'}
    return C.build_recolor('mikitaka_tmp', '支仓未起隆', 'telence',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('punch', 'point', 4, 'oneshot'),
                            ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'hurt', 'run': {'a': 'walk', 'f': 1.6}, 'cmd': 'point', 'cmd2': 'point',
                                            'guard': 'idle', 'dodge': 'walk', 'special': 'point', 'punch': 'point'}, bodyW=4)


def build_yuya_tmp():
    # 第三部 polnareff：竖起来的白发换金色，白裤子换深紫
    hair = {(216, 220, 242): (250, 214, 90), (214, 220, 236): (240, 200, 70), (158, 162, 204): (196, 150, 40), (246, 248, 255): (255, 240, 160),
            (144, 152, 182): (170, 124, 30)}
    cmap = {'#d6dcec': '#5a3a7a', '#d8dcf2': '#6a4a8a', '#9098b6': '#3a2454', '#9ea2cc': '#4a2e66', '#f6f8ff': '#7a5a9a',
            '#2a2632': '#d04880', '#4e4860': '#a02a5a'}
    return C.build_recolor('yuya_tmp', '喷上裕也', 'polnareff',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('fight', 'fight', 4, 'loop'), ('kick', 'kick', 8, 'oneshot'),
                            ('shock', 'shock', 4, 'loop'), ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'),
                            ('dodge', 'dodge', 1, 'static'), ('guard', 'guard', 1, 'static')],
                           cmap=cmap, hair=hair, heads_from='portrait',
                           amap=dict(C.AMAP_HUMAN, kick='kick', run={'a': 'walk', 'f': 1.6}, cmd='kick', cmd2='kick', special='fight',
                                     win='fight', shock='shock'), bodyW=4)


def build_highway_tmp():
    # 公路之星：白金之星的身子换成粉黑两色（动画里是粉色系、身上一格格的花纹）
    cmap = {'#bab2ff': '#ffb8d8', '#8a80ec': '#f070a8', '#5242ae': '#b03a78', '#33257a': '#6a1a48',
            '#5a56a0': '#3a2a3a', '#2c2852': '#24182a', '#17132e': '#140c18',
            '#ff8a78': '#ffe0f0', '#ec3040': '#f8a0c8', '#98182c': '#a04878',
            '#fff6b4': '#ffffff', '#ffd83c': '#f0f0f8', '#c08a18': '#a0a0b8', '#b69ec6': '#f8c8e0'}
    im, m = C.base('starplat')
    sh = C.Sheet('highway_tmp', '公路之星', m['cell'], m['pivot'])
    for anim, a in m['animations'].items():
        if anim.startswith('portrait'):
            continue
        sh.add(anim, [C.recolor(f, cmap) for f in C.frames('starplat', anim)], a.get('fps', 6), a.get('kind', 'loop'))
    hd = C.heads('starplat')
    sh.heads = {'normal': [C.recolor(f, cmap) for f in hd['portrait']]}
    e = C.save(sh, amap={'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'upper', 'rush': 'rush', 'block': 'block', 'hurt': 'hurt',
                         'special': 'rush', 'kick': 'punch'}, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


BUILDERS = {'toyohiro': build_toyohiro, 'terunosuke': build_terunosuke, 'mikitaka_tmp': build_mikitaka_tmp,
            'yuya_tmp': build_yuya_tmp, 'highway_tmp': build_highway_tmp}

HEROES = {
    'mikitaka_tmp': dict(cid='mikitaka_tmp', cn='支仓未起隆', short='未起隆', rn='HAZEKURA MIKITAKA', stand=None,
                         burst=['#1a2a5a', '#3a4a9a', '#80a0f0'], panel='#0a1028', accent='#a0e0e0', nameColor='#4a6ab0',
                         blipHz=560, grunt=None),
    'yuya_tmp': dict(cid='yuya_tmp', cn='喷上裕也', short='裕也', rn='FUNGAMI YUYA', stand='highway_tmp',
                     burst=['#5a1a3a', '#a03070', '#ff70a0'], panel='#200a18', accent='#ff70a0', nameColor='#c04a80',
                     blipHz=520, grunt=None),
}
SPEAKERS = {
    'toyohiro': dict(short='丰大', nameColor='#4e9a4a', blipHz=380),
    'terunosuke': dict(short='辉之辅', nameColor='#9a7a5a', blipHz=600),
    'mikitaka_tmp': dict(short='未起隆', nameColor='#4a6ab0', blipHz=560),
    'yuya_tmp': dict(short='裕也', nameColor='#c04a80', blipHz=520),
    'hirose_mom_voice': dict(short='康一的妈妈', nameColor='#a07a5a', blipHz=700),
}
STANDS = {
    'highway_tmp': dict(cn='公路之星', en='HIGHWAY STAR', owner='yuya_tmp', aura='#ff70a0', card='#ffb0d0', ghost='#ffd0e4',
                        impact='pink', kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx='stand_summon_star', fist=False),
}


def main(ids):
    meta = L.load_json(META, {}) or {}
    meta.setdefault('chars', {})
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', list(meta['chars'][cid]['animations']), '表情', list(meta['chars'][cid]['heads']))
    meta['heroes'] = dict(HEROES)
    meta['speakers'] = dict(SPEAKERS)
    meta['stands'] = dict(STANDS)
    L.save_json(META, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
