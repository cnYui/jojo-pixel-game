# 第五部替身（三）：敌方的人形替身——小脚、镜中人、壮烈成仁、白色相簿、绿日、绿洲、软机器、工艺品、黑色安息日。
import math

from stand5 import Stand, POSES
from stands_a import pal, knob, band_on


def ground_poses(spread=7):
    """脚踩地的架势（穿在身上的替身）：脚落到基准线"""
    legs = ((3, 19, 6, 29, 5, 38), (-3, 19, -spread, 29, -spread - 1, 38))
    out = {}
    for name, P in POSES.items():
        q = dict(P)
        q['sy'] = 0
        if name.startswith('punch') or name == 'rush':
            q['legs'] = ((3, 19, 8, 28, 9, 38), (-3, 19, -9, 28, -13, 38))
        elif name == 'hurt':
            q['legs'] = ((3, 19, 7, 29, 8, 38), (-3, 19, -8, 28, -12, 38))
        else:
            q['legs'] = legs
        out[name] = q
    return out


# ====================================================================== 小脚：紫圆盔、铁嘴、一根长刀指
LF_HEAD = """
....kkkk....
..kkuuuukk..
.kuuiiuuuuk.
.kuiuuuuuUk.
kuuuuuuuuUUk
kUUUUUUUUUUk
kvkkkvvkkkvk
kvkeekvkeekk
kVvvvvvvvvk.
.kkwkwkwkwk.
.kkwkwkwkk..
..kkkkkkk...
"""
LF_SHOUT = LF_HEAD.replace('.kkwkwkwkk..\n..kkkkkkk...', '.kkkkkkkkk..\n..kkwkwkk...')


def lf_torso_deco(p, cx, ty):
    p.swap(p.ell(cx, ty + 7, 6.0, 4.4), 'avVx', 'iuUU')
    knob(p, cx, ty + 7, 2.0, 'wqz')
    for yy in (ty + 13, ty + 15):
        p.line([(cx - 4, yy), (cx + 4, yy)], 'x', only='avV')


def lf_pad(p, x, y, near):
    knob(p, x, y, 5.2 if near else 4.6, 'iuU')
    knob(p, x, y, 1.6, 'wqz')


def lf_belt(p, x, y, ph):
    p.paint(p.rect(x - 6, y - 1, x + 6, y + 1), 'qzz', hi=0.3, sh=0.7)
    for dx in (-4, 0, 4):
        p.px(x + dx, y, 'w')


def lf_leg_deco(p, hip, knee, foot, near):
    knob(p, knee[0], knee[1], 3.2, 'iuU')
    band_on(p, knee, foot, 0.7, 0.3, 'avVx', 'qzzk', 3.4)


def lf_front(p, cx, ty, ph, P):
    # 右手食指上的长刀片
    a = P['far']
    ex, ey, fx, fy = cx + a[2], ty + a[3], cx + a[4], ty + a[5]
    dx, dy = fx - ex, fy - ey
    L = max(1e-3, math.hypot(dx, dy))
    ux, uy = dx / L, dy / L
    if uy > 0.3:
        ux, uy = 0.8, -0.6
    tip = (fx + ux * 13, fy + uy * 13)
    m = p.poly([(fx + ux * 2 - uy * 1.6, fy + uy * 2 + ux * 1.6), (tip[0], tip[1]),
                (fx + ux * 2 + uy * 1.6, fy + uy * 2 - ux * 1.6)])
    p.paint(m, 'wqz', hi=0.45, sh=0.6)


def little_feet():
    S = Stand(pal(a='#ffffff', v='#dadeee', V='#969eba', x='#50586e', w='#ffffff', q='#c4cadc', z='#767e96', i='#cdb4ff',
                  u='#8c64dc', U='#4c3094', e='#ffd028'),
              'avVx', LF_HEAD, LF_SHOUT, chest=(9.4, 6.4), waist=(7, 5, 18), arm=(2.7, 2.0, 3.2, 2.8), fist=3.2,
              leg=(2.8, 2.2, 2.6), shoulder=1, torso_deco=lf_torso_deco, pad=lf_pad, belt=lf_belt, leg_deco=lf_leg_deco,
              front=lf_front, neck_r=2.2,
              poses={'pose': dict(far=(8, 3, 16, 0, 19, -9), near=(-8, 4, -14, 10, -7, 15), far_front=False, far_fist=True,
                                  near_fist=True, shout=True, w=60, bx=26)})
    return S.sheet(drop=('rush',))


# ====================================================================== 镜中人
MM_HEAD = """
....kkkk....
..kkvvvvkk..
.kavyyyyyvk.
.kavvvvvvvvk
kavkkkkkkkkk
kvkcckvkcckk
kvkkkvvvkkk.
kVwwwwwwwwk.
.kVwwwkkwk..
.kVVwwwwk...
..kkVVVkk...
...kkkkk....
"""
MM_SHOUT = MM_HEAD.replace('.kVwwwkkwk..\n.kVVwwwwk...', '.kVwwkkkkk..\n.kVVwkkkk...')


def mm_torso_deco(p, cx, ty):
    p.swap(p.poly([(cx - 6, ty + 10), (cx + 6, ty + 10), (cx + 5, ty + 18), (cx - 5, ty + 18)]), 'avVx', 'wwqz')
    p.line([(cx - 7, ty + 2), (cx, ty + 10), (cx + 7, ty + 2)], 'y', only='avVx')
    p.line([(cx, ty + 10), (cx, ty + 17)], 'y', only='wqz')
    for dx, dy in ((-5, 7), (5, 7), (0, 4)):
        knob(p, cx + dx, ty + dy, 1.4, 'iyY')


def mm_pad(p, x, y, near):
    knob(p, x, y, 4.0 if near else 3.5, 'avVx')
    p.line([(x - 3, y), (x + 3, y)], 'y', only='avVx')


def mm_belt(p, x, y, ph):
    p.paint(p.rect(x - 6, y - 1, x + 6, y), 'iyY', hi=0.3, sh=0.7)


def mm_arm_deco(p, s, e, f, near):
    band_on(p, e, f, 0.55, 0.14, 'avVx', 'iyYY', 3.4)
    band_on(p, e, f, 0.69, 0.31, 'avVx', 'wwqz', 3.2)


def mm_leg_deco(p, hip, knee, foot, near):
    knob(p, knee[0], knee[1], 2.4, 'iyY')
    band_on(p, knee, foot, 0.25, 0.75, 'avVx', 'wwqz', 3.4)


def mirror_man():
    S = Stand(pal(a='#c49cec', v='#7446a8', V='#482074', x='#26083e', w='#f4f0fc', q='#bcb0d8', z='#7c70a0', c='#8cf8f4',
                  i='#fff4b4', y='#e8bc3c', Y='#9c7414'),
              'avVx', MM_HEAD, MM_SHOUT, chest=(9.2, 6.2), waist=(7, 4.6, 18), arm=(3.1, 2.4, 2.6, 2.1), leg=(3.5, 2.6, 1.4),
              torso_deco=mm_torso_deco, pad=mm_pad, belt=mm_belt, arm_deco=mm_arm_deco, leg_deco=mm_leg_deco,
              ghost=('a', 'x'),
              poses={'idle': dict(far=(8, 3, 16, 5, 10, -3), near=(-8, 4, -13, 11, -9, 17), far_front=True),
                     'pose': dict(far=(8, 3, 15, 8, 21, 1), near=(-8, 4, -15, 8, -21, 1), far_front=False, far_fist=True,
                                  near_fist=True, w=60, bx=30)})
    return S.sheet()


# ====================================================================== 壮烈成仁：没有腿，浑身是眼睛，拖着肠子一样的须，散发衰老的雾
GD_HEAD = """
..k......k..
..kk....kk..
..kakkkkvk..
.kaaavvvvvk.
kaavkkvvkkvk
kavkwrkkwrkk
kvvkwwkkwwkk
kvvvkkvvkkk.
kVvvvvvvvvk.
.kVkwkwkwkk.
.kVVkxxxkk..
..kkkkkkk...
"""
GD_SHOUT = GD_HEAD.replace('.kVkwkwkwkk.\n.kVVkxxxkk..', '.kVkxxxxxkk.\n.kVVkwkwkk..')
EYE = """
.kkk.
kwwwk
kwrkk
.kkk.
"""


def gd_torso_deco(p, cx, ty):
    for dx, dy in ((-8, 4), (1, 3), (-2, 11), (4, 9), (-6, 14)):
        p.stamp(EYE, cx + dx, ty + dy)


def gd_arm_deco(p, s, e, f, near):
    p.stamp(EYE, (s[0] + e[0]) / 2 - 2, (s[1] + e[1]) / 2 - 2)


def gd_pad(p, x, y, near):
    knob(p, x, y, 4.4 if near else 3.8, 'avVx')
    p.stamp(EYE, x - 2, y - 2)


def gd_lower(p, cx, ty, ph, P):
    sw = [0, 2, 0, -2][ph % 4]
    for k, (ox, ex, ey, r) in enumerate(((-4, -14, 33, 2.6), (0, -2, 38, 3.0), (4, 9, 34, 2.4), (-1, -9, 38, 1.8))):
        s = sw if k % 2 else -sw
        mx, my = cx + (ox + ex) / 2 + s, ty + 25
        m = p.cap(cx + ox, ty + 15, mx, my, r + 1.4, r) | p.cap(mx, my, cx + ex - s, ty + ey, r, 0.8)
        p.paint(m, 'avVx', hi=0.3, sh=0.6)
        p.px(mx, my, 'w')
        p.px(mx + 1, my, 'r')


def gd_mist(p, cx, ty, ph, big):
    n = 12 if big else 5
    for k in range(n):
        x = cx - 22 + (k * 17 + ph * 5) % 48
        y = ty + 6 + (k * 11 + ph * 3) % 34
        r = 2.0 + (k % 3) * (1.0 if big else 0.4)
        m = p.ell(x, y, r, r * 0.8) & (p.c == '.')
        ys, xs = m.nonzero()
        for yy, xx in zip(ys, xs):
            if (yy + xx + ph) % 2 == 0:
                p.c[yy, xx] = 'm' if k % 2 else 'M'


def gd_front(p, cx, ty, ph, P):
    if P.get('mist'):
        gd_mist(p, cx, ty, ph, True)
    else:
        gd_mist(p, cx, ty, ph, False)


def grateful_dead():
    poses = {'pose': dict(far=(8, 3, 15, 2, 20, -4), near=(-8, 4, -15, 3, -19, -3), far_front=False, far_fist=True,
                          near_fist=True, shout=True, mist=True, w=60, bx=30)}
    S = Stand(pal(a='#dcbcf4', v='#9a68c4', V='#5e348c', x='#36145c', w='#ffffff', r='#e82c44', m='#c8b8e4', M='#8c7cb0'),
              'avVx', GD_HEAD, GD_SHOUT, chest=(10.2, 6.6), waist=(8, 5, 18), arm=(3.5, 2.7, 2.8, 2.0), fist=3.2,
              legs=False, lower=gd_lower, torso_deco=gd_torso_deco, arm_deco=gd_arm_deco, pad=gd_pad, front=gd_front,
              ghost=('a', 'V'), poses=poses)
    return S.sheet()


# ====================================================================== 白色相簿：穿在加丘身上的冰甲，脚下冰刀
WA_HEAD = """
.kk......kk.
.kak....kvk.
.kaakkkkvvk.
kaaaaavvvvvk
kaaavvvvvvvk
kavvkkkkkkkk
kvvkrrrkrrrk
kvvkrwekrwek
kVvvkkkvkkkk
.kVvvvvvvvk.
..kVVkkkkk..
...kkkkkk...
"""
WA_SHOUT = WA_HEAD.replace('..kVVkkkkk..\n...kkkkkk...', '..kVkxxxkk..\n...kkkkkk...')


def wa_torso_deco(p, cx, ty):
    p.line([(cx - 8, ty + 5), (cx, ty + 9), (cx + 8, ty + 5)], 'b', only='avV')
    p.line([(cx, ty + 9), (cx, ty + 17)], 'b', only='avV')
    for dx, dy in ((-5, 12), (5, 12), (-4, 3), (5, 2)):
        p.px(cx + dx, ty + dy, 'w')
        p.px(cx + dx + 1, ty + dy + 1, 'b')


def wa_pad(p, x, y, near):
    knob(p, x, y, 4.6 if near else 4.0, 'avVx')
    spike = p.poly([(x - 2, y - 3), (x + (-5 if near else 5), y - 8), (x + 2, y - 3)])
    p.paint(spike, 'wbB', hi=0.5, sh=0.6)


def wa_belt(p, x, y, ph):
    p.paint(p.rect(x - 6, y - 1, x + 6, y + 1), 'wbB', hi=0.3, sh=0.6)


def wa_arm_deco(p, s, e, f, near):
    band_on(p, e, f, 0.5, 0.18, 'avVx', 'wbBB', 3.6)


def wa_leg_deco(p, hip, knee, foot, near):
    knob(p, knee[0], knee[1], 3.0, 'wbB')
    x, y = foot
    p.paint(p.poly([(x - 4, y), (x + 4, y), (x + 5, y + 1.6), (x - 3, y + 1.6)]), 'avV', hi=0.3, sh=0.6)
    p.line([(x - 5, y + 3.4), (x + 6, y + 3.4)], 'w')
    p.line([(x + 6, y + 3.4), (x + 8, y + 2)], 'w')


def wa_front(p, cx, ty, ph, P):
    if P.get('ice'):
        for k in range(11):
            x = cx - 24 + (k * 19 + ph * 7) % 52
            y = ty - 8 + (k * 13 + ph * 4) % 42
            if p.get(x, y) == '.':
                for dx, dy, ch in ((0, 0, 'w'), (-1.4, 0, 'b'), (1.4, 0, 'b'), (0, -1.4, 'b'), (0, 1.4, 'b')):
                    p.dot(x + dx, y + dy, ch, only='.')


def white_album():
    poses = ground_poses(7)
    poses['pose'] = dict(poses['pose'], ice=True, far=(8, 3, 15, 6, 21, 0), near=(-8, 4, -15, 8, -20, 3), far_front=False,
                         far_fist=True, near_fist=True, shout=True, w=60, bx=30)
    poses['block'] = dict(poses['block'], ice=True)
    S = Stand(pal(a='#ffffff', v='#d4ecfc', V='#8cb8e4', x='#4c74ac', w='#ffffff', b='#7cd4f8', B='#3484c4', r='#e8305c',
                  e='#202850'),
              'avVx', WA_HEAD, WA_SHOUT, chest=(9.8, 6.6), waist=(7.6, 5.4, 18), arm=(3.6, 3.0, 3.2, 2.6), fist=3.3,
              leg=(4.0, 3.2, 2.4), torso_deco=wa_torso_deco, pad=wa_pad, belt=wa_belt, arm_deco=wa_arm_deco,
              leg_deco=wa_leg_deco, front=wa_front, neck_r=3.2, ghost=('w', 'B'), poses=poses)
    return S.sheet()


# ====================================================================== 绿日：魁梧的绿色身体，胸口一排排肋条，小头圆眼，撒霉菌孢子
GR_HEAD = """
....kkkk....
..kkvvvvkk..
.kavVVVVVvk.
.kavvvvvvvvk
kavkkkvvkkkk
kvkrrkvkrrkk
kvkkkvvvkkk.
kVvVvVvVvVk.
.kVkkkkkkk..
.kVVVVVVk...
..kkkkkk....
...kkkk.....
"""
GR_SHOUT = GR_HEAD.replace('.kVkkkkkkk..\n.kVVVVVVk...', '.kVkxxxxkk..\n.kVkkkkkk...')


def gr_torso_deco(p, cx, ty):
    p.swap(p.ell(cx, ty + 10, 5.6, 8.0), 'avVx', 'vVxx')
    for dx in (-4, -2, 0, 2, 4):
        p.line([(cx + dx, ty + 4), (cx + dx, ty + 17)], 'a' if dx % 4 == 0 else 'x', only='vVx')


def gr_pad(p, x, y, near):
    knob(p, x, y, 5.6 if near else 5.0, 'avVx')
    for dx, dy in ((-2, -1), (2, 1), (0, 3)):
        p.px(x + dx, y + dy, 'x')


def gr_belt(p, x, y, ph):
    p.paint(p.rect(x - 7, y - 1, x + 7, y + 1), 'lgG', hi=0.3, sh=0.7)


def gr_arm_deco(p, s, e, f, near):
    for t in (0.35, 0.55, 0.75):
        band_on(p, e, f, t, 0.07, 'avVx', 'vVxx', 5.0)


def gr_leg_deco(p, hip, knee, foot, near):
    knob(p, knee[0], knee[1], 3.0, 'lgG')


def gr_front(p, cx, ty, ph, P):
    if P.get('spore'):
        for k in range(16):
            x = cx - 26 + (k * 23 + ph * 6) % 60
            y = ty - 6 + (k * 17 + ph * 5) % 46
            if p.get(x, y) == '.':
                p.paint(p.ell(x, y, 1.0 + k % 2 * 0.6, 1.0), 'm', outline=None)
                p.dot(x - 1.3, y - 1.3, 'M', only='.')


def green_day():
    poses = {'idle': dict(far=(8, 4, 17, 11, 20, 17), near=(-8, 5, -15, 13, -13, 20), lean=2, hy=2),
             'pose': dict(far=(8, 3, 17, 8, 22, 3), near=(-8, 4, -16, 10, -20, 6), far_front=False, far_fist=True,
                          near_fist=True, shout=True, spore=True, w=60, bx=30)}
    S = Stand(pal(a='#bcf4a4', v='#58b462', V='#2c7842', x='#124628', r='#f0404c', l='#e8f87c', g='#a8c830', G='#6c8414',
                  m='#8cd848', M='#d8fc8c'),
              'avVx', GR_HEAD, GR_SHOUT, chest=(11.4, 7.2), waist=(8.4, 5.4, 18), arm=(4.0, 3.2, 4.4, 3.2), fist=4.0,
              leg=(4.4, 3.4, 2.2), shoulder=2, torso_deco=gr_torso_deco, pad=gr_pad, belt=gr_belt, arm_deco=gr_arm_deco,
              leg_deco=gr_leg_deco, front=gr_front, neck_r=3.2, ghost=('a', 'x'), poses=poses)
    return S.sheet()


# ====================================================================== 绿洲：穿在塞可身上的泥甲，蹲伏着在地里“游”
OA_HEAD = """
............
....kkkk....
..kkaaaakk..
.kaavvvvvvk.
.kavrvvvrvvk
kavvrvvvrvvk
kvvkkkvkkkkk
kvkwwekwwekk
kVvkkkvkkkk.
.kVvrrrrvk..
..kVkkkkk...
...kkkk.....
"""
OA_SHOUT = OA_HEAD.replace('..kVkkkkk...\n...kkkk.....', '..kVkxxkk...\n...kkkk.....')


def stripes(p, mask, step=4):
    ys, xs = mask.nonzero()
    for y, x in zip(ys, xs):
        if p.c[y, x] in 'av' and (y + x // 3) % step == 0:
            p.c[y, x] = 'r'


def oa_torso_deco(p, cx, ty):
    stripes(p, p.rect(cx - 12, ty + 2, cx + 12, ty + 17))


def oa_arm_deco(p, s, e, f, near):
    stripes(p, p.cap(e[0], e[1], f[0], f[1], 4.4), 3)


def oa_leg_deco(p, hip, knee, foot, near):
    stripes(p, p.cap(hip[0], hip[1], knee[0], knee[1], 4.4), 3)
    knob(p, knee[0], knee[1], 2.4, 'avV')


def oa_front(p, cx, ty, ph, P):
    base = 55.5
    # 身边融开的泥浆
    p.paint(p.ell(cx - 2, base, 22 + (ph % 2) * 2, 2.6), 'tTU', hi=0.3, sh=0.6)
    if P.get('splash'):
        for k, dx in enumerate((-24, -16, 14, 22, 29, 34)):
            h = 5 + (k + ph) % 3 * 3
            p.paint(p.cap(cx + dx * 0.8, base - 1, cx + dx, base - h, 1.8, 0.7), 'tTU', hi=0.4, sh=0.6)
            p.px(cx + dx + 1, base - h - 3, 't')


def oasis():
    crouch = ((3, 19, 11, 21, 9, 27), (-3, 19, -12, 21, -11, 27))
    poses = {}
    for name, P in POSES.items():
        q = dict(P)
        q.update(sy=11, hy=2, legs=crouch, lean=max(2, P['lean'] + 2))
        if name == 'idle':
            q.update(far=(8, 3, 15, 10, 18, 22), near=(-8, 4, -14, 12, -9, 23))
        if name.startswith('punch') or name == 'rush':
            q['splash'] = True
        if name == 'pose':
            q.update(far=(8, 3, 16, 2, 20, -7), near=(-8, 4, -14, 12, -9, 23), far_front=False, far_fist=True, near_fist=True,
                     splash=True, shout=True, w=60, bx=26)
        poses[name] = q
    S = Stand(pal(a='#e4d488', v='#b09c4c', V='#766428', x='#483a10', w='#ffffff', e='#8c3cc8', r='#d85c28', t='#c8ac74',
                  T='#8c7044', U='#54401c'),
              'avVx', OA_HEAD, OA_SHOUT, chest=(9.8, 6.4), waist=(7.6, 5.6, 18), arm=(3.5, 2.8, 3.0, 2.4), fist=3.4,
              leg=(3.9, 3.1, 2.0), torso_deco=oa_torso_deco, arm_deco=oa_arm_deco, leg_deco=oa_leg_deco, front=oa_front,
              neck_r=3.2, ghost=('a', 'x'), poses=poses)
    return S.sheet(drop=('block',))


# ====================================================================== 软机器：白身紫钉，手持细剑，扎中的人像气球一样瘪掉
SM_HEAD = """
...u..u..u..
..kukkukkuk.
..kaakkaakk.
.kaaaavvvvk.
kaaavvvvvvvk
kavkkkvvkkkk
kvkcckvkcckk
kvvkkvvvkkk.
kVvvvvuvvvk.
.kVvvkkkkk..
..kVVvvkk...
...kkkkk....
"""
SM_SHOUT = SM_HEAD.replace('.kVvvkkkkk..\n..kVVvvkk...', '.kVvkxxxkk..\n..kVVkkkk...')


def studs(p, pts):
    for x, y in pts:
        knob(p, x, y, 1.6, 'iuU')


def sm_torso_deco(p, cx, ty):
    studs(p, [(cx - 6, ty + 5), (cx - 3, ty + 9), (cx + 4, ty + 9), (cx + 7, ty + 5), (cx, ty + 13)])


def sm_pad(p, x, y, near):
    knob(p, x, y, 4.2 if near else 3.6, 'avVx')
    studs(p, [(x - 2.4, y - 2), (x + 2.4, y - 2), (x, y + 1.6)])


def sm_belt(p, x, y, ph):
    p.paint(p.rect(x - 6, y - 1, x + 6, y), 'iuU', hi=0.3, sh=0.7)


def sm_arm_deco(p, s, e, f, near):
    studs(p, [((e[0] + f[0]) / 2, (e[1] + f[1]) / 2)])


def sm_leg_deco(p, hip, knee, foot, near):
    studs(p, [(knee[0], knee[1]), ((hip[0] + knee[0]) / 2, (hip[1] + knee[1]) / 2)])


def sm_front(p, cx, ty, ph, P):
    a = P['far']
    ex, ey, fx, fy = cx + a[2], ty + a[3], cx + a[4], ty + a[5]
    dx, dy = fx - ex, fy - ey
    L = max(1e-3, math.hypot(dx, dy))
    ux, uy = dx / L, dy / L
    if uy > 0.2:
        ux, uy = 0.9, -0.44
    tip = (fx + ux * 17, fy + uy * 17)
    p.line([(fx + ux * 3, fy + uy * 3 + 1.4), (tip[0], tip[1] + 1)], 'z')
    p.line([(fx + ux * 3, fy + uy * 3), tip], 'w')
    p.line([(fx + ux * 3 - uy * 3.4, fy + uy * 3 + ux * 3.4), (fx + ux * 3 + uy * 3.4, fy + uy * 3 - ux * 3.4)], 'y')


def soft_machine():
    S = Stand(pal(a='#ffffff', v='#e0e0f0', V='#a0a0c4', x='#5c5c88', w='#ffffff', z='#767ea0', i='#d8b4ff', u='#9454d4',
                  U='#54248c', c='#5cf0c8', y='#f0c43c'),
              'avVx', SM_HEAD, SM_SHOUT, chest=(9.0, 6.0), waist=(6.8, 4.4, 18), arm=(2.9, 2.3, 2.4, 1.9), fist=2.7,
              leg=(3.3, 2.4, 1.3), torso_deco=sm_torso_deco, pad=sm_pad, belt=sm_belt, arm_deco=sm_arm_deco,
              leg_deco=sm_leg_deco, front=sm_front, ghost=('w', 'V'),
              poses={'pose': dict(far=(8, 3, 15, 1, 17, -8), near=(-8, 4, -14, 10, -7, 15), far_front=False, far_fist=True,
                                  near_fist=True, w=56, bx=24)})
    return S.sheet(drop=('rush',))


# ====================================================================== 工艺品：银白硬甲、头顶鳍冠、咧嘴铁牙，能把东西定在空中
KW_HEAD = """
.....kk.....
....kaak....
..kkkaakkk..
.kaakaakvvk.
kaaaakkvvvvk
kavkkkvvkkkk
kvkyykvkyykk
kvvkkvvvkkk.
kVkkkkkkkkk.
.kkwkwkwkwk.
.kkwkwkwkk..
..kkkkkkk...
"""
KW_SHOUT = KW_HEAD.replace('.kkwkwkwkk..\n..kkkkkkk...', '.kkkkkkkkk..\n..kwkwkwk...')


def kw_torso_deco(p, cx, ty):
    for dx, dy in ((-6, 3), (6, 3), (-4, 14), (4, 14)):
        knob(p, cx + dx, ty + dy, 1.3, 'wbB')
    knob(p, cx, ty + 7, 2.6, 'wbB')


def kw_pad(p, x, y, near):
    knob(p, x, y, 5.0 if near else 4.4, 'avVx')
    knob(p, x, y, 2.2, 'wbB')


def kw_belt(p, x, y, ph):
    p.paint(p.rect(x - 7, y - 1, x + 7, y + 1), 'wbB', hi=0.3, sh=0.6)
    p.paint(p.poly([(x - 4, y + 2), (x + 4, y + 2), (x, y + 6)]), 'avVx', hi=0.3, sh=0.6)


def kw_arm_deco(p, s, e, f, near):
    band_on(p, e, f, 0.45, 0.4, 'avVx', 'wbBB', 3.6)


def kw_leg_deco(p, hip, knee, foot, near):
    knob(p, knee[0], knee[1], 3.0, 'wbB')


def kw_front(p, cx, ty, ph, P):
    if P.get('frozen'):
        for k, (dx, dy) in enumerate(((22, -6), (27, 4), (21, 13), (30, 16))):
            x, y = cx + dx, ty + dy + (ph % 2 if k % 2 else 0)
            p.paint(p.poly([(x - 2, y - 1.6), (x + 1.4, y - 1.6), (x + 3.4, y), (x + 1.4, y + 1.6), (x - 2, y + 1.6)]),
                    'iyY', hi=0.4, sh=0.6)
            p.line([(x - 6, y), (x - 4, y)], 'b')


def kraft_work():
    poses = {'idle': dict(far=(8, 3, 17, 7, 16, -4), near=(-8, 4, -17, 8, -16, -2)),
             'pose': dict(far=(8, 3, 14, 9, 16, 3), near=(-8, 4, -13, 10, -8, 15), frozen=True, w=64),
             'block': dict(frozen=True, w=64)}
    S = Stand(pal(a='#ffffff', v='#c8d6e8', V='#8090b0', x='#445070', w='#ffffff', b='#8cb0e0', B='#4c6ca8', i='#fff4b4',
                  y='#f0c030', Y='#9c7410'),
              'avVx', KW_HEAD, KW_SHOUT, chest=(10.4, 6.8), waist=(8, 5.2, 18), arm=(3.8, 3.0, 3.2, 2.5), fist=3.5,
              leg=(4.2, 3.2, 1.7), shoulder=1, torso_deco=kw_torso_deco, pad=kw_pad, belt=kw_belt, arm_deco=kw_arm_deco,
              leg_deco=kw_leg_deco, front=kw_front, neck_r=3.4, ghost=('w', 'V'), poses=poses)
    return S.sheet()


# ====================================================================== 黑色安息日：宽檐帽、白面具、黑斗篷，嘴里叼着箭，只在影子里走
BS_HEAD = """
.......kkkk.......
.....kkaaaakk.....
....kaavvvvvvk....
...kyvyvyvyvyvk...
.kkkkkkkkkkkkkkkk.
kaavyvvyvvyvvyvvvk
.kkkkkkkkkkkkkkkk.
....kwwwwwwwwk....
....kwkkwwkkwk....
....kwkewwkewk....
.....kywwwwyk.....
.....kyywwyyk.....
......kkyykk......
"""
BS_SHOUT = BS_HEAD.replace('.....kyywwyyk.....', '.....kyykkyyk.....')


def bs_back(p, S, hx, hy, cx, ty, ph, P):
    sw = [0, 1, 0, -1][ph % 4]
    cloak = p.poly([(cx - 6, ty - 1), (cx + 7, ty - 1), (cx + 13, ty + 14), (cx + 12 + sw, ty + 39), (cx + 7, ty + 34),
                    (cx + 3 - sw, ty + 39), (cx - 2, ty + 33), (cx - 7 + sw, ty + 39), (cx - 11, ty + 33), (cx - 17 - sw, ty + 37),
                    (cx - 13, ty + 12)])
    p.paint(cloak, 'avVx', hi=0.3, sh=0.5)
    for dx in (-8, -2, 5):
        p.line([(cx + dx // 2, ty + 14), (cx + dx + sw, ty + 33)], 'x', only='avV')


def bs_lower(p, cx, ty, ph, P):
    pass


def bs_torso_deco(p, cx, ty):
    p.line([(cx - 8, ty + 1), (cx, ty + 12), (cx + 8, ty + 1)], 'y', only='avVx')
    for dy in (13, 16):
        knob(p, cx, ty + dy, 1.5, 'iyY')


def bs_pad(p, x, y, near):
    knob(p, x, y, 4.2 if near else 3.6, 'avVx')
    knob(p, x, y, 1.5, 'iyY')


def bs_arm_deco(p, s, e, f, near):
    band_on(p, e, f, 0.6, 0.12, 'avVx', 'iyYY', 3.4)


def bs_front(p, cx, ty, ph, P):
    # 嘴里叼着的箭
    ax, ay = cx + 5, ty - 3.4
    L = 20 if P.get('stab') else 11
    p.line([(ax, ay), (ax + L, ay + 1)], 'y')
    p.paint(p.poly([(ax + L, ay - 1.8), (ax + L + 6, ay + 1), (ax + L, ay + 3.8), (ax + L + 1.6, ay + 1)]), 'iyY', hi=0.4, sh=0.6)
    # 脚下的影子
    p.paint(p.ell(cx - 2, 55.6, 19, 2.0), 'x', outline=None)


def black_sabbath():
    poses = {}
    for name, P in POSES.items():
        q = dict(P)
        if name.startswith('punch') and name != 'punch0':
            q['stab'] = name == 'punch1'
        if name == 'pose':
            q.update(far=(8, 3, 16, 8, 21, 3), near=(-8, 4, -15, 9, -19, 5), far_front=False, far_fist=True, near_fist=True,
                     w=60, bx=30)
        poses[name] = q
    S = Stand(pal(a='#6c6288', v='#40385a', V='#241e38', x='#120e22', w='#f4f0e4', e='#c82c3c', i='#fff4b4', y='#e8b830',
                  Y='#946c10'),
              'avVx', BS_HEAD, BS_SHOUT, chest=(8.6, 6.0), waist=(7, 5, 18), arm=(3.0, 2.2, 2.4, 1.6), fist=2.8,
              fist_tones='wwy', legs=False, lower=bs_lower, back=bs_back, torso_deco=bs_torso_deco, pad=bs_pad,
              arm_deco=bs_arm_deco, front=bs_front, neck_r=2.4, ghost=('a', 'x'), poses=poses)
    return S.sheet(drop=('rush',))


STANDS = {
    'littlefeet': ('小脚', little_feet),
    'mirrorman': ('镜中人', mirror_man),
    'gratefuldead': ('壮烈成仁', grateful_dead),
    'whitealbum': ('白色相簿', white_album),
    'greenday': ('绿日', green_day),
    'oasis': ('绿洲', oasis),
    'softmachine': ('软机器', soft_machine),
    'kraftwork': ('工艺品', kraft_work),
    'blacksabbath': ('黑色安息日', black_sabbath),
}
