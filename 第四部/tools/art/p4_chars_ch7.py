# 第7章的人物和替身图集（第四部/docs/分章开发约定.md 第 5 节：本章负责画回音 ACT3、辻彩 / 灰姑娘、枯萎穿心攻击、川尻浩作（换脸后的吉良））。
#   写法照 p4_chars.py：拿第三部的全尺寸图集换色再缩成 chibi；枯萎穿心攻击自己画（第三部没有坦克一样的身体）。
#   元数据写 _meta/chars_ch7.json（build_p4.py 自动深合并）。配色以 TV 动画为准（docs/第7章_开发脚本.md 第 0 节）。
#   ph7_* 是临时占位：亿泰（第2章）、由花子（第3章）、吉良和杀手皇后（第6章）还没合进来时第7章先用，
#   story/p4_ch7.js 只在 G.D.chars 里没有正式 cid 时才用占位，正式图一合并就自动换掉。
#   用法：python3 第四部/tools/art/p4_chars_ch7.py [cid ...]
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402

HUMAN = {'talk': 'idle', 'shock': 'hurt', 'run': 'walk'}


def scaled(f, k):
    """全尺寸帧整体缩小（脚点不动）：ACT3 只有康一那么高，第三部的人形替身都比他高一大截"""
    w, h = f.size
    s = f.resize((max(1, int(round(w * k))), max(1, int(round(h * k)))), Image.NEAREST)
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    c.alpha_composite(s, ((w - s.width) // 2, h - s.height))
    return c


# ============================================================ 辻彩：棕发（白发带）、浅粉连衣裙、黑色宽腰带 + 紫色细带（TV 配色）
AYA_DRESS = {'#d29e5e': '#f2c4d4', '#977143': '#c88aa4', '#9d7646': '#d89ab2', '#f2c656': '#ffffff', '#ffc97c': '#fbe4ec'}


def aya_frame(f):
    f = C.recolor(f, AYA_DRESS)
    a = np.array(f)
    # 腰带：连衣裙颜色的最上面往下 40% 那一行起画 3 行黑 + 1 行紫（只画在裙子像素上）
    dress = C.comp(f, ['#f2c4d4', '#c88aa4', '#d89ab2'])
    ys = np.where(dress.any(1))[0]
    if len(ys):
        y0 = int(ys.min() + (ys.max() - ys.min()) * 0.32)
        for y, col in ((y0, (30, 24, 34)), (y0 + 1, (30, 24, 34)), (y0 + 2, (110, 60, 140))):
            row = dress[y]
            a[y, row] = (*col, 255)
    # 白发带：头发最上面一行往下 3 行处横着一条
    hair = C.comp(f, ['#462e22', '#744834', '#533325', '#513224'])
    hy = np.where(hair.any(1))[0]
    if len(hy):
        y = int(hy.min() + 3)
        a[y, hair[y]] = (246, 244, 240, 255)
    return Image.fromarray(a, 'RGBA')


def build_aya():
    e = C.build_recolor('aya', '辻彩', 'npc_villager_f',
                        [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('talk', 'talk', 4, 'loop'),
                         ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static')],
                        cmap={}, frame_fn=aya_frame, head_edit=lambda f: C.recolor(f, {'#d29e5e': '#f2c4d4', '#977143': '#c88aa4'}),
                        amap={'talk': 'talk', 'shock': 'hurt', 'run': 'walk', 'cmd': 'talk'}, bodyW=3)
    return e


# ============================================================ 枯萎穿心攻击：自己画。蓝球装甲 + 两侧履带 + 正面浅灰猫骷髅脸（额头金匕首）+ 顶上苔绿 / 金色小钮
SH = dict(o=(18, 14, 30), b1=(40, 70, 170), b2=(70, 110, 214), b3=(140, 176, 240), b0=(22, 40, 104),
          t1=(52, 52, 60), t2=(24, 24, 30), t3=(96, 96, 108), s1=(214, 214, 220), s2=(160, 160, 172), s3=(250, 250, 252),
          g1=(240, 196, 60), g2=(168, 124, 28), m1=(96, 118, 60), k=(14, 10, 20))


def sha_frame(roll=0, jaw=0, sink=0, w=30, h=24):
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cx, cy = 15, 12 + sink
    ball = ((xx - cx) / 9.5) ** 2 + ((yy - cy) / 8.5) ** 2 <= 1
    a[ball] = (*SH['b1'], 255)
    a[ball & ((xx - (cx - 3)) ** 2 + (yy - (cy - 4)) ** 2 <= 16)] = (*SH['b2'], 255)
    a[ball & ((xx - (cx - 4)) ** 2 + (yy - (cy - 5)) ** 2 <= 3)] = (*SH['b3'], 255)
    a[ball & (yy > cy + 4)] = (*SH['b0'], 255)
    # 装甲的接缝
    for x in range(int(cx - 9), int(cx + 10)):
        y = int(cy - 1)
        if ball[y, x]:
            a[y, x] = (*SH['b0'], 255)
    # 顶上的钮
    for (x, y, c) in ((cx, cy - 10, 'm1'), (cx - 1, cy - 9, 'g1'), (cx, cy - 9, 'g1'), (cx + 1, cy - 9, 'g2'), (cx, cy - 11, 'm1')):
        if 0 <= y < h:
            a[int(y), int(x)] = (*SH[c], 255)
    # 履带（两侧下半，朝右看时前面一条）：滚动的齿
    ty0 = int(cy + 3)
    for y in range(ty0, min(h, ty0 + 6)):
        for x in range(int(cx - 12), int(cx + 13)):
            if y == ty0 or y == ty0 + 5 or x in (int(cx - 12), int(cx + 12)):
                col = SH['t2']
            else:
                col = SH['t3'] if (x + roll) % 3 == 0 else SH['t1']
            if 0 <= x < w:
                a[y, x] = (*col, 255)
    # 骷髅脸（朝右：画在球的右前方）
    fx, fy = cx + 4, cy - 2
    skull = ((xx - fx) / 4.6) ** 2 + ((yy - fy) / 4.0) ** 2 <= 1
    a[skull] = (*SH['s1'], 255)
    a[skull & (xx < fx - 2)] = (*SH['s2'], 255)
    # 猫耳
    for (x, y) in ((fx - 3, fy - 4), (fx - 3, fy - 5), (fx + 2, fy - 4), (fx + 3, fy - 5)):
        a[int(y), int(x)] = (*SH['s1'], 255)
    # 眼窝、鼻刺
    for (x, y) in ((fx - 2, fy - 1), (fx - 1, fy - 1), (fx + 2, fy - 1), (fx + 3, fy - 1), (fx + 1, fy + 1)):
        a[int(y), int(x)] = (*SH['k'], 255)
    # 额头金匕首
    a[int(fy - 3), int(fx)] = (*SH['g1'], 255)
    a[int(fy - 2), int(fx)] = (*SH['g2'], 255)
    # 下颚：jaw 0 合着 / 1 张开
    my = int(fy + 2 + jaw)
    for x in range(int(fx - 2), int(fx + 4)):
        a[my, x] = (*SH['s3'], 255)
        if jaw:
            a[my - 1, x] = (*SH['k'], 255)
    for x in range(int(fx - 1), int(fx + 4), 2):
        a[my - (1 if jaw else 0), x] = (*SH['s3'], 255)
    if sink:
        a[h - sink:, :, :] = 0
    img = Image.fromarray(a, 'RGBA')
    return C.reoutline(img, SH['o'])


def build_sha():
    sh = C.Sheet('sha', '枯萎穿心攻击', (34, 28), (17, 26))
    pad = lambda f: (lambda c: (c.alpha_composite(f, (2, 3)), c)[1])(Image.new('RGBA', (34, 28), (0, 0, 0, 0)))
    sh.add('idle', [pad(sha_frame(0)), pad(sha_frame(0))], 2, 'loop')
    sh.add('walk', [pad(sha_frame(r)) for r in range(3)], 10, 'loop')
    sh.add('boom', [pad(sha_frame(0, 1)), pad(sha_frame(1, 1))], 8, 'loop')
    sh.add('hurt', [pad(sha_frame(0, 1))], 1, 'static')
    sh.add('stuck', [pad(sha_frame(0, 0, 3)), pad(sha_frame(0, 1, 5))], 3, 'loop')
    big = sha_frame(0, 1).resize((60, 48), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((20, 4, 52, 36)))
    sh.heads = {'normal': [face, face]}
    e = C.save(sh, amap={'talk': 'boom', 'run': 'walk', 'cmd': 'boom', 'punch': 'boom', 'special': 'boom', 'shock': 'hurt',
                         'down': 'stuck', 'guard': 'idle', 'dodge': 'walk', 'lunge': 'walk'}, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 回音 ACT3：浅灰身体、翠绿条纹和头冠、金指节（TV 配色）。第三部“世界”的人形身体换色、缩到 0.62
ACT3 = {'#f6c63a': '#d6d8dc', '#b8841a': '#9a9ea8', '#fff6c0': '#f4f6f8', '#7a520e': '#62666e', '#ffe070': '#e8eaee', '#e8a820': '#b8bcc4',
        '#3cc46a': '#1ec080', '#1b7040': '#14a868', '#0e3a24': '#4a4e58', '#a8f080': '#7af0b8',
        '#801020': '#e0a040', '#d02838': '#f0c050', '#ffffff': '#fff4c0'}


def build_echoes3():
    im, m = C.base('theworld')
    sh = C.Sheet('echoes3', '回音 ACT3', m['cell'], m['pivot'])
    for anim in ('idle', 'punch', 'rush', 'pose', 'hurt', 'fist', 'kick'):
        a = m['animations'][anim]
        sh.add(anim, [scaled(C.recolor(f, ACT3), 0.8) for f in C.frames('theworld', anim)], a.get('fps', 6), a.get('kind', 'loop'))
    hd = C.heads('theworld')
    nm = [C.recolor(f, ACT3) for f in hd['portrait']]
    sh.heads = {'normal': nm if len(nm) > 1 else nm * 2}
    e = C.save(sh, amap={'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'kick', 'upper': 'kick', 'rush': 'rush', 'block': 'pose',
                         'hurt': 'hurt', 'special': 'fist', 'reach': 'punch', 'finger': 'pose'}, kind='stand', bodyW=4)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 灰姑娘：粉白的细长人形、长手指（原著配色资料里没写，先按辻彩的粉色画）。第三部法皇的身体换色
CIN = {'#4cd66a': '#f4b8d0', '#1f8a44': '#c86a96', '#8cf0a0': '#fde0ec', '#0e4a2a': '#7a2e58', '#b4ff8c': '#ffffff',
       '#40ffb0': '#ffd0e4', '#c8fff0': '#ffffff', '#10a868': '#e08ab0', '#fff27a': '#ffe080', '#ffae3c': '#f0a040'}


def build_cinderella():
    im, m = C.base('hiero')
    sh = C.Sheet('cinderella', '灰姑娘', m['cell'], m['pivot'])
    for anim in ('idle', 'cast', 'block', 'hurt'):
        a = m['animations'][anim]
        sh.add(anim, [scaled(C.recolor(f, CIN), 0.8) for f in C.frames('hiero', anim)], a.get('fps', 6), a.get('kind', 'loop'))
    e = C.save(sh, amap={'cmd': 'cast', 'punch': 'cast', 'reach': 'cast', 'special': 'cast', 'block': 'block', 'hurt': 'hurt', 'talk': 'idle'},
               kind='stand', bodyW=4)
    e['heads'] = {}
    return e


# ============================================================ 吉良的西装身体（第三部 DIO 的身体：夹克换成淡紫西装、内衬白衬衫、裤子深紫）
SUIT = {'#fff07a': '#c8b4e4', '#f8b418': '#9a84c4', '#ffc21c': '#ab96d2', '#b4640c': '#6a5494', '#dcae3c': '#8a76b6',
        '#a4600c': '#5e4a86', '#ffdc70': '#d8c8ee', '#fff6c8': '#ece4f8', '#6e3606': '#3e3060', '#2c4a36': '#f0eef4', '#15261c': '#b8b4c4',
        '#2e2840': '#3c3258', '#17121f': '#241c38', '#140b1e': '#1a1428', '#ff2438': '#3a2a4a'}
HAIR_BLACK = {'#fff07a': '#3a3644', '#f8b418': '#1e1a24', '#ffc21c': '#2a2632', '#b4640c': '#121016', '#dcae3c': '#2a2632',
              '#a4600c': '#121016', '#ffdc70': '#4a4656', '#fff6c8': '#5a5666', '#6e3606': '#0e0c12', '#fffde2': '#5a5666'}
HAIR_KIRA = {'#fff07a': '#efe6c4', '#f8b418': '#c8b88a', '#ffc21c': '#ddd0a6', '#b4640c': '#8a7a56', '#dcae3c': '#c8b88a',
             '#a4600c': '#8a7a56', '#ffdc70': '#f6f0d8', '#fff6c8': '#fffbe8', '#6e3606': '#6a5c40', '#fffde2': '#fffbe8'}
DIO_ANIMS = [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('punch', 'punch', 8, 'oneshot'), ('throw', 'throw', 8, 'oneshot'),
             ('pose', 'pose', 3, 'oneshot'), ('laugh', 'laugh', 4, 'loop'), ('hurt', 'hurt', 1, 'static')]


def suit_man(cid, name, hair):
    e = C.build_recolor(cid, name, 'dio', DIO_ANIMS, cmap=SUIT, hair=hair, skin=[(251, 214, 180), (220, 161, 132)],
                        amap={'talk': 'idle', 'shock': 'hurt', 'run': 'walk', 'cmd': 'throw', 'down': 'hurt', 'guard': 'pose', 'dodge': 'walk'},
                        bodyW=4)
    return e


def build_kawajiri():
    return suit_man('kawajiri', '川尻浩作', HAIR_BLACK)


# ============================================================ 裁缝店老板：第三部镇民的身体，灰发、米色背心
def build_tailor():
    hair = {'#5e4836': '#b8b4b0', '#3b4843': '#8a8682'}
    cmap = {'#9a8a60': '#d8c8a0', '#6e6345': '#a89870', '#c4b17f': '#ece0c0', '#685d41': '#988860'}
    return C.build_recolor('tailor', '裁缝店老板', 'npc_townsfolk',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'),
                            ('talk', 'talk', 4, 'loop')],
                           cmap=cmap, hair=hair, amap={'shock': 'hurt', 'run': 'walk'}, bodyW=4)


# ============================================================ 临时占位（正式图由别章画）
def build_ph_kira():
    return suit_man('ph7_kira', '吉良吉影（占位）', HAIR_KIRA)


def build_ph_killerqueen():
    # 第6章画正式的杀手皇后：这里只是白金之星换成粉紫
    cmap = {'#bab2ff': '#f4c8e8', '#8a80ec': '#d898c8', '#5242ae': '#a8609a', '#33257a': '#6e3466',
            '#5a56a0': '#f0e8f0', '#2c2852': '#c0a8c0', '#17132e': '#6a506a',
            '#ff8a78': '#f8e0f0', '#ec3040': '#c080b0', '#98182c': '#80406e', '#fff6b4': '#ffffff', '#ffd83c': '#e8d0e8', '#c08a18': '#a87aa0',
            '#b69ec6': '#e8c0dc'}
    im, m = C.base('starplat')
    sh = C.Sheet('ph7_killerqueen', '杀手皇后（占位）', m['cell'], m['pivot'])
    for anim in ('idle', 'punch', 'rush', 'block', 'pose', 'hurt', 'reach', 'upper'):
        a = m['animations'][anim]
        sh.add(anim, [C.recolor(f, cmap) for f in C.frames('starplat', anim)], a.get('fps', 6), a.get('kind', 'loop'))
    nm = [C.recolor(f, cmap) for f in C.heads('starplat')['portrait']]
    sh.heads = {'normal': nm}
    e = C.save(sh, amap={'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'upper', 'rush': 'rush', 'block': 'block', 'hurt': 'hurt',
                         'special': 'rush', 'finger': 'reach'}, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


def build_ph_yukako():
    # 第3章画正式的由花子：这里是第三部玛莉亚的身体（长黑发），黑裙换成深藏青的校服
    cmap = {'#262034': '#2a2c4e', '#3a2238': '#3c3e6a', '#6a4064': '#5a5e94', '#463e60': '#20223e', '#e0304a': '#c03040'}
    return C.build_recolor('ph7_yukako', '山岸由花子（占位）', 'mariah',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'hurt', 'run': 'walk', 'blush': 'idle'}, bodyW=3)


def build_ph_okuyasu():
    # 第2章画正式的亿泰：这里是花京院的身体，黑校服、灰发
    cmap = {'#2f9e56': '#2c2c3a', '#1a6038': '#1c1c26', '#62c874': '#4c4c62', '#0f4028': '#111118', '#50b848': '#3c3c4e',
            '#b8402e': '#9a9aa6', '#e8734c': '#c8c8d2', '#78221e': '#5a5a66', '#9a4ce0': '#3a2a2a'}
    return C.build_recolor('ph7_okuyasu', '虹村亿泰（占位）', 'kakyoin',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'),
                            ('cast', 'point', 4, 'loop'), ('guard', 'guard', 1, 'static')],
                           cmap=cmap, amap={'talk': 'idle', 'shock': 'hurt', 'run': 'walk', 'cmd': 'point'}, bodyW=4)


BUILDERS = {'aya': build_aya, 'sha': build_sha, 'echoes3': build_echoes3, 'cinderella': build_cinderella, 'kawajiri': build_kawajiri,
            'tailor': build_tailor, 'ph7_kira': build_ph_kira, 'ph7_killerqueen': build_ph_killerqueen, 'ph7_yukako': build_ph_yukako,
            'ph7_okuyasu': build_ph_okuyasu}

SPEAKERS = {
    'aya': dict(short='辻彩', nameColor='#c86a96', blipHz=700),
    'cinderella': dict(short='灰姑娘', nameColor='#c86a96', blipHz=760),
    'echoes3': dict(short='ACT3', nameColor='#1ec080', blipHz=600),
    'sha': dict(short='枯萎穿心攻击', nameColor='#4a6ad0', blipHz=900),
    'kawajiri': dict(short='吉良', nameColor='#7a5a9a', blipHz=420),
    'tailor': dict(short='裁缝店老板', nameColor='#9a8a60', blipHz=420),
    'ph7_kira': dict(short='吉良', nameColor='#7a5a9a', blipHz=420),
    'ph7_yukako': dict(short='由花子', nameColor='#5a5e94', blipHz=760),
    'ph7_okuyasu': dict(short='亿泰', nameColor='#6a6a8a', blipHz=420),
    'ph7_killerqueen': dict(short='杀手皇后', nameColor='#c080b0', blipHz=500),
}
STANDS = {
    'echoes3': dict(cn='回音 ACT3', en='ECHOES ACT3', owner='koichi', aura='#7af0b8', card='#a0f0c8', ghost='#d0fff0',
                    impact='green', kind='humanoid', idle={'dx': -8, 'z': 2}, link=None, summonSfx='stand_summon_star', fist=True),
    'cinderella': dict(cn='灰姑娘', en='CINDERELLA', owner='aya', aura='#f4b8d0', card='#ffd0e4', ghost='#ffe8f2',
                       impact='pink', kind='humanoid', idle={'dx': -10, 'z': 8}, link=None, summonSfx=None, fist=False),
    'sha': dict(cn='枯萎穿心攻击', en='SHEER HEART ATTACK', owner='kira', aura='#6a8ae0', card='#a0b8f0', ghost='#c8d8ff',
                impact='blue', kind='humanoid', idle={'dx': 0, 'z': 0}, link=None, summonSfx=None, fist=False),
    'ph7_killerqueen': dict(cn='杀手皇后', en='KILLER QUEEN', owner='kira', aura='#e080c0', card='#f4c8e8', ghost='#ffe0f4',
                            impact='pink', kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx='stand_summon_star', fist=True),
}


def main(ids):
    path = os.path.join(L.META, 'chars_ch7.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', list(meta['chars'][cid]['animations']))
    meta['speakers'] = SPEAKERS
    meta['stands'] = STANDS
    L.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
