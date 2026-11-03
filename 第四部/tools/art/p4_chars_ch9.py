# 第9章的新角色：支仓未起隆、喷上裕也 / 公路之星、川尻早人、猫草（分工见 第四部/docs/分章开发约定.md 第 5 节）。
#   做法和 p4_chars.py 一样：拿第三部全尺寸图集换色（发色、校服按 TV 动画配色），再缩成游戏尺寸；猫草没有合适的底子，程序画。
#   配色依据 JoJo Wiki 的 TV 动画配色表（2026-11-03 查）：
#     未起隆 浅金色直长发、浅绿眼、藏青改造校服 + 暗金 / 深红饰物、紫色腰带
#     喷上裕也 黑发（两侧浅灰）、浅蓝眼、深灰校服、蓝腰带
#     公路之星 玫红色人形（TV 版），这里用白金之星的身体换色
#     川尻早人 姜黄色头发、黄绿背心 + 橄榄色长袖、酒红短裤
#     猫草 蓝灰色两片大花瓣、红花蕊、绿茎和叶、黄眼睛
#   用法：python3 第四部/tools/art/p4_chars_ch9.py [cid ...]   → assets/chars/<cid>.png、heads/<cid>/…、_meta/chars_ch9.json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402
import p4_heads as HD  # noqa: E402

META = os.path.join(L.META, 'chars_ch9.json')

# 花京院的绿校服 → 藏青；红发 → 浅金色；耳坠的紫保留成腰带那种紫
KAK_UNI = ['#2f9e56', '#1a6038', '#62c874', '#0f4028', '#50b848']


def uni(cols):
    return dict(zip(KAK_UNI, cols))


def build_mikitaka():
    cmap = uni(['#2c3a78', '#1a2248', '#4a5aa8', '#0e1430', '#3a4890'])
    cmap.update({'#ffd83c': '#c8a040', '#ecc418': '#b08a30', '#fff4a8': '#e8cc78', '#c89a20': '#8a6a24',
                 '#e8243c': '#a8203a', '#9a4ce0': '#7a3aa8'})
    hair = {'#b8402e': '#e6dcb4', '#e8734c': '#fff6dc', '#78221e': '#b8aa7c'}
    return C.build_recolor('mikitaka', '支仓未起隆', 'kakyoin',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'),
                            ('down', 'down', 1, 'static'), ('dodge', 'dodge', 1, 'static'), ('guard', 'guard', 1, 'static'),
                            ('float', 'float', 3, 'loop'),
                            # 花京院指挥法皇的 cast → cmd：第10章第15战未起隆当队友，比划（MK_POKE 的 body 是 cmd）、变形时要这个动作
                            ('cast', 'cmd', 4, 'loop')],
                           cmap=dict(cmap, **hair), amap={'talk': 'idle', 'shock': 'hurt', 'run': {'a': 'walk', 'f': 1.6},
                                                          'point': 'cmd', 'punch': 'cmd'}, bodyW=4)


def build_yuya():
    cmap = uni(['#55565e', '#33343a', '#7c7e88', '#1e1f24', '#686a72'])
    cmap.update({'#ffd83c': '#d8b850', '#c89a20': '#9a7a2a', '#e8243c': '#3a6ad0', '#9a4ce0': '#f4f4fa'})
    hair = {'#b8402e': '#2a2632', '#e8734c': '#8a8a96', '#78221e': '#141018'}
    return C.build_recolor('yuya', '喷上裕也', 'kakyoin',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'),
                            ('down', 'down', 1, 'static'), ('dodge', 'dodge', 1, 'static'), ('guard', 'guard', 1, 'static'),
                            # 花京院指挥法皇的 cast → cmd：第10章裕也当队友，公路之星踢人时本体摆指挥的样子（招式 body 是 cmd）
                            ('cast', 'cmd', 4, 'loop')],
                           cmap=dict(cmap, **hair), amap={'talk': 'idle', 'shock': 'hurt', 'run': {'a': 'walk', 'f': 1.6}, 'bed': 'down',
                                                          'point': 'cmd'},
                           bodyW=4)


def build_hayato():
    # 第三部小孩：橙色是上衣、深褐是头发、灰蓝是短裤
    cmap = {'#e49436': '#a6c63a', '#a46a26': '#6e8a26', '#ffbd4c': '#cce466', '#2c1e18': '#c46a28',
            '#525e68': '#8a2a3c', '#3b434a': '#64182a', '#394148': '#5a1626'}
    return C.build_recolor('hayato', '川尻早人', 'npc_kid',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('run', 'run', 10, 'loop'),
                            ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'hurt'}, bodyW=3)


def build_highway():
    cmap = {'#bab2ff': '#ffc4d4', '#8a80ec': '#f07a9c', '#5242ae': '#c4406c', '#33257a': '#80203e',
            '#5a56a0': '#a03058', '#2c2852': '#60142e', '#17132e': '#3a0a1c',
            '#ff8a78': '#86a6ff', '#ec3040': '#3e5ed4', '#98182c': '#1e2a7a',
            '#fff6b4': '#ffffff', '#ffd83c': '#eceaf6', '#c08a18': '#9a98b4', '#b69ec6': '#f4b4c8'}
    im, m = C.base('starplat')
    sh = C.Sheet('highway', '公路之星', m['cell'], m['pivot'])
    for anim, a in m['animations'].items():
        if anim.startswith('portrait'):
            continue
        sh.add(anim, [feet(C.recolor(f, cmap)) for f in C.frames('starplat', anim)], a.get('fps', 6), a.get('kind', 'loop'))
    hd = C.heads('starplat')
    sh.heads = {'normal': [C.recolor(f, cmap) for f in hd['portrait']]}
    e = C.save(sh, amap={'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'upper', 'rush': 'rush', 'block': 'block', 'hurt': 'hurt',
                         'special': 'rush', 'finger': 'finger', 'walk': 'idle', 'talk': 'idle', 'down': 'hurt', 'cmd': 'punch', 'reach': 'reach'}, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


def feet(img):
    """公路之星身上的脚印纹：在玫红色的身体上每隔几行点一对深色的小脚印"""
    a = np.array(img.convert('RGBA'))
    body = np.zeros(a.shape[:2], bool)
    for c in ('#f07a9c', '#c4406c'):
        r = C.rgb(c)
        body |= (a[..., 0] == r[0]) & (a[..., 1] == r[1]) & (a[..., 2] == r[2]) & (a[..., 3] > 0)
    h, w = body.shape
    dark = C.rgb('#5a1a3a')
    for y in range(4, h - 3, 7):
        for x in range((y // 7) % 2 * 4 + 2, w - 3, 9):
            pts = [(x, y), (x, y + 1), (x + 2, y + 2), (x + 2, y + 3)]
            if all(body[py, px] for px, py in pts):
                for px, py in pts:
                    a[py, px, :3] = dark
    return Image.fromarray(a, 'RGBA')


# ============================================================ 猫草（程序画：两片蓝灰花瓣夹着一张猫脸，绿茎，种在小花盆里）
SC = dict(o=(26, 16, 32), p=(150, 168, 196), pd=(96, 112, 146), pl=(198, 212, 232), s=(70, 150, 70), sd=(40, 100, 50),
          r=(210, 50, 60), y=(250, 220, 70), k=(20, 14, 24), pot=(176, 96, 60), potd=(120, 60, 40), w=(250, 250, 250))


def cat_frame(puff=0.0, sleep=False, shoot=False, t=0.0, w=34, h=40):
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cx, cy = 17, 14 + np.sin(t * 2 * np.pi) * 0.6
    def fill(m, c):
        a[m] = (*c, 255)
    # 花盆
    potm = (yy >= 31) & (yy <= 39) & (np.abs(xx - cx) <= 7 - (yy - 31) * 0.3)
    fill(potm, SC['pot'])
    fill(potm & (yy >= 37), SC['potd'])
    fill((yy >= 30) & (yy <= 31) & (np.abs(xx - cx) <= 8), SC['potd'])
    # 茎和两片叶
    fill((np.abs(xx - cx) <= 1) & (yy >= cy + 7) & (yy < 30), SC['s'])
    for sgn in (-1, 1):
        leaf = ((xx - (cx + sgn * 5)) / 4.2) ** 2 + ((yy - 25) / 1.8) ** 2 <= 1
        fill(leaf, SC['s'])
        fill(leaf & (yy > 25), SC['sd'])
    # 两片大花瓣（左右包着脸）
    for sgn in (-1, 1):
        pet = ((xx - (cx + sgn * 8)) / 6.0) ** 2 + ((yy - (cy - 1)) / 10.0) ** 2 <= 1
        fill(pet, SC['p'])
        fill(pet & (xx * sgn > (cx + sgn * 10) * sgn), SC['pd'])
        fill(pet & (yy < cy - 7), SC['pl'])
    # 脸（鼓腮时变大）
    r = 6.2 + 1.8 * puff
    face = ((xx - cx) / r) ** 2 + ((yy - (cy + 1)) / (r * 0.85)) ** 2 <= 1
    fill(face, SC['pl'])
    # 耳朵
    for sgn in (-1, 1):
        for d in range(3):
            for k in range(3 - d):
                X, Y = int(cx + sgn * (3 + k)), int(cy - 5 - d)
                if 0 <= X < w and 0 <= Y < h:
                    a[Y, X] = (*SC['pl'], 255)
    # 眼睛
    ey = int(round(cy))
    for sgn in (-1, 1):
        ex = int(cx + sgn * 3)
        if sleep:
            a[ey, ex - 1:ex + 2] = (*SC['k'], 255)
        else:
            a[ey - 1:ey + 1, ex - 1:ex + 1] = (*SC['y'], 255)
            a[ey - 1:ey + 1, ex] = (*SC['k'], 255)
    # 嘴 / 花蕊
    my = int(round(cy + 3))
    if shoot:
        a[my - 1:my + 2, int(cx) - 1:int(cx) + 2] = (*SC['k'], 255)
    else:
        a[my, int(cx) - 1:int(cx) + 2] = (*SC['r'], 255)
    img = Image.fromarray(a, 'RGBA')
    return C.reoutline(img, SC['o'])


def build_straycat():
    sh = C.Sheet('straycat', '猫草', (34, 40), (17, 39))
    sh.add('idle', [cat_frame(t=i / 4) for i in range(4)], 4, 'loop')
    sh.add('puff', [cat_frame(0.5), cat_frame(1.0)], 6, 'oneshot')
    sh.add('shoot', [cat_frame(0.2, shoot=True)], 1, 'static')
    sh.add('sleep', [cat_frame(sleep=True)], 1, 'static')
    big = cat_frame().resize((68, 80), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((18, 6, 50, 38)))
    big2 = cat_frame(1.0).resize((68, 80), Image.NEAREST)
    face2 = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face2.alpha_composite(big2.crop((18, 6, 50, 38)))
    sh.heads = {'normal': [face, face], 'rage': [face2, face2]}
    e = C.save(sh, amap={'talk': 'idle', 'walk': 'idle', 'run': 'idle', 'hurt': 'sleep', 'down': 'sleep', 'shock': 'puff',
                         'cmd': 'shoot', 'special': 'shoot', 'guard': 'idle', 'dodge': 'idle'}, bodyW=4)
    e['headAlias'] = {'smile': 'normal', 'shock': 'rage'}
    e['shadow'] = False
    return e


HEROES = {
    'hayato': dict(cid='hayato', cn='川尻早人', short='早人', rn='KAWAJIRI HAYATO', stand=None,
                   burst=['#4a3a1a', '#8a6a2a', '#d0a050'], panel='#1a1408', accent='#d4782e', nameColor='#b06a2a', blipHz=820, grunt=None),
    'mikitaka': dict(cid='mikitaka', cn='支仓未起隆', short='未起隆', rn='HAZEKURA MIKITAKA', stand=None,
                     burst=['#1a2248', '#2c3a78', '#c8a040'], panel='#0e1430', accent='#e6dcb4', nameColor='#6a7ac0', blipHz=560, grunt=None),
    'yuya': dict(cid='yuya', cn='喷上裕也', short='裕也', rn='FUNGAMI YUYA', stand='highway',
                 burst=['#3a1a2a', '#80203e', '#f07a9c'], panel='#1a0a14', accent='#f07a9c', nameColor='#c0507a', blipHz=500, grunt=None),
}
SPEAKERS = {
    'straycat': dict(short='猫草', nameColor='#8aa0c4', blipHz=900),
    'nurse9': dict(short='护士', nameColor='#d08aa8', blipHz=780),
    'highway': dict(short='公路之星', nameColor='#e0608a', blipHz=520),
}
STANDS = {
    'highway': dict(cn='公路之星', en='HIGHWAY STAR', owner='yuya', aura='#f07a9c', card='#ffb0c8', ghost='#ffd0dc',
                    impact='pink', kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx=None, fist=True),
}
def build_nurse():
    return C.build_copy('nurse9', '护士', 'npc_nurse', [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop')])


BUILDERS = {'nurse9': build_nurse, 'mikitaka': build_mikitaka, 'yuya': build_yuya, 'hayato': build_hayato, 'highway': build_highway, 'straycat': build_straycat}


def preview():
    """全部新人的待机第 0 帧排一排（4 倍），给用户看配色"""
    ims = []
    for cid in [c for c in BUILDERS if c != 'nurse9']:
        m = L.load_json(META)['chars'][cid]
        im = Image.open(os.path.join(L.ASSETS, m['image'] + '.png')).convert('RGBA')
        a = m['animations']['idle']
        cw, ch = m['cell']
        ims.append(im.crop((0, a['row'] * ch, cw, (a['row'] + 1) * ch)))
    W = sum(i.width + 8 for i in ims) + 8
    H = max(i.height for i in ims) + 16
    can = Image.new('RGBA', (W, H), (150, 160, 176, 255))
    x = 8
    for i in ims:
        can.alpha_composite(i, (x, H - 8 - i.height))
        x += i.width + 8
    out = os.path.join(L.ASSETS, 'preview', 'chars_ch9.png')
    L.ensure(out)
    can.resize((W * 4, H * 4), Image.NEAREST).save(out)
    return out


def main(ids):
    meta = L.load_json(META, {}) or {}
    meta.setdefault('chars', {})
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', list(meta['chars'][cid]['animations']))
    meta['heroes'] = HEROES
    meta['speakers'] = SPEAKERS
    meta['stands'] = STANDS
    L.save_json(META, meta)
    print('预览', preview())


if __name__ == '__main__':
    main(sys.argv[1:])
