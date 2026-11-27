# 第五部替身（一·续）：忧郁蓝调、紫烟、辣妹、黄金体验镇魂曲。
import math

import numpy as np

from px import Cv
from rig import OX, OY
from stand5 import Stand, POSES
from stands_a import pal, knob, band_on

# ====================================================================== 忧郁蓝调
MB_HEAD = """
....kkkk....
..kkaaaakk..
.kaaavvvvvk.
.kavvvvvvvvk
kavkkkkkkkkk
kavkGkGGkGGk
kavkkkkkkkkk
kvvvvvvvvvvk
kVvvkkvvkkk.
.kVvvvvvvvk.
..kVVvkkk...
...kkkkk....
"""
MB_SHOUT = MB_HEAD.replace('.kVvvvvvvvk.\n..kVVvkkk...', '.kVvkkkkkvk.\n..kVkggkk...')


def speaker(p, x, y, r):
    """身上的圆形喇叭：外圈深色、里面两个小点"""
    p.paint(p.ell(x, y, r, r), 'vVx', hi=0.3, sh=0.6)
    p.px(x - 1.3, y, 'x')
    p.px(x + 1.3, y, 'x')
    p.px(x, y - 1.3, 'a')


def mb_torso_deco(p, cx, ty):
    speaker(p, cx - 5, ty + 6, 3.0)
    speaker(p, cx + 6, ty + 6, 3.0)
    for yy in (ty + 12, ty + 15):
        p.line([(cx - 4, yy), (cx + 4, yy)], 'x', only='avV')


def mb_pad(p, x, y, near):
    speaker(p, x, y, 4.0 if near else 3.4)


def mb_belt(p, x, y, ph):
    p.paint(p.rect(x - 6, y - 1, x + 6, y), 'yYk', hi=0.3, sh=0.7)
    cloth = p.poly([(x - 4, y + 2), (x + 4, y + 2), (x + 1, y + 6), (x - 1, y + 6)])
    p.paint(cloth, 'vVx', hi=0.3, sh=0.6)


def mb_leg_deco(p, hip, knee, foot, near):
    speaker(p, knee[0], knee[1], 2.6)
    band_on(p, knee, foot, 0.6, 0.12, 'avVx', 'yYkk', 3.0)


def moody_blues():
    S = Stand(pal(a='#e4dcff', v='#a898ec', V='#6c58b8', x='#403080', G='#58f47c', g='#c8506c', y='#e8c458', Y='#a87c24'),
              'avVx', MB_HEAD, MB_SHOUT, chest=(9.0, 6.0), waist=(7, 4.4, 18), arm=(3.0, 2.4, 2.5, 2.0), leg=(3.4, 2.5, 1.4),
              torso_deco=mb_torso_deco, pad=mb_pad, belt=mb_belt, leg_deco=mb_leg_deco, ghost=('a', 'V'),
              poses={'idle': dict(far=(8, 3, 14, 11, 13, 19), near=(-8, 4, -13, 12, -11, 19)),
                     'pose': dict(far=(8, 3, 15, 4, 8, -8), near=(-8, 4, -14, 10, -7, 15), far_front=True, far_fist=True,
                                  near_fist=True, w=52)})
    sh = S.sheet()
    # “回放”：身后拖出两层回放残像
    rows = {r[0]: r[1] for r in sh.rows}
    frames = []
    for i in range(3):
        base = rows['idle'][i]
        out = base.copy()
        for k, dx in ((1, -6 - i), (0, -11 - i * 2)):
            a = base.a.copy()
            m = a[..., 3] > 0
            a[..., :3][m] = (176, 160, 244) if k == 1 else (128, 108, 208)
            chk = (np.indices(m.shape).sum(axis=0) + i + k) % 2 == 0
            a[..., 3][~(m & chk)] = 0
            ghost = Cv(base.w, base.h)
            ghost.a = np.roll(a, dx, axis=1)
            out.under(ghost)
        frames.append(out)
    sh.add('rewind', frames, 6, 'loop')
    return sh


# ====================================================================== 紫烟
PH_HEAD = """
....kkkk....
..kkvvvvkk..
.kavVwVwVvk.
.kavVwVwVvvk
kavvvVvVvvvk
kvvkkkvvkkkk
kvkrrkvkrrkk
kVvkkvvvkkk.
kVvvvvvvvvk.
.kVkwkwkwkk.
.kVVkwkwkk..
..kkkkkkk...
"""
PH_SHOUT = PH_HEAD.replace('.kVkwkwkwkk.\n.kVVkwkwkk..', '.kVkxxxxxkk.\n.kVkwkwkkk..')


def checker(p, mask, size=3):
    """菱形格：白紫相间"""
    ys, xs = mask.nonzero()
    for y, x in zip(ys, xs):
        c = p.c[y, x]
        if c in 'avV' and (((x + y) // size) + ((x - y) // size)) % 2 == 0:
            p.c[y, x] = {'a': 'w', 'v': 'w', 'V': 'q'}[c]


def ph_torso_deco(p, cx, ty):
    checker(p, p.rect(cx - 12, ty + 2, cx + 12, ty + 17))


def ph_arm_deco(p, s, e, f, near):
    checker(p, p.cap(s[0], s[1], e[0], e[1], 4.2))
    band_on(p, e, f, 0.7, 0.12, 'avVx', 'yYkk', 3.4)


def ph_leg_deco(p, hip, knee, foot, near):
    checker(p, p.cap(hip[0], hip[1], knee[0], knee[1], 4.6))
    knob(p, knee[0], knee[1], 2.6, 'wqz')


def ph_pad(p, x, y, near):
    knob(p, x, y, 4.4 if near else 3.8, 'avVx')
    checker(p, p.ell(x, y, 4.4, 4.0), 2)


def ph_belt(p, x, y, ph):
    p.paint(p.rect(x - 7, y - 1, x + 7, y + 1), 'wqz', hi=0.3, sh=0.7)
    cloth = p.poly([(x - 5, y + 2), (x + 5, y + 2), (x + 1, y + 7), (x - 1, y + 7)])
    p.paint(cloth, 'vVx', hi=0.3, sh=0.6)


def ph_front(p, cx, ty, ph, P):
    # 拳背上的病毒胶囊：每只拳头三颗
    for arm in (P['far'], P['near']):
        fx, fy = cx + arm[4], ty + arm[5]
        for ox, oy in ((-3.2, -3.2), (0.4, -4.4), (3.8, -2.8)):
            p.paint(p.ell(fx + ox, fy + oy, 1.5, 1.5), 'iyY', hi=0.4, sh=0.6)


def purple_haze():
    hunch = {}
    for name, P in POSES.items():
        q = dict(P)
        q['hy'] = P.get('hy', 0) + 3
        if name == 'idle':
            q.update(lean=3, far=(8, 4, 14, 12, 19, 9), near=(-8, 5, -13, 13, -6, 17), sy=1)
        if name == 'pose':
            q.update(far=(8, 3, 16, 2, 21, -6), near=(-8, 4, -15, 2, -20, -5), far_front=False, far_fist=True, near_fist=True,
                     shout=True, w=60, bx=30)
        hunch[name] = q
    S = Stand(pal(a='#e0bcf8', v='#9c4ec8', V='#5e2888', x='#341258', w='#f6f0fa', q='#bcaed0', z='#7c6c94', r='#f03048',
                  i='#fff6b4', y='#f0c83c', Y='#a87414'),
              'avVx', PH_HEAD, PH_SHOUT, chest=(10.4, 6.8), waist=(8, 5, 18), arm=(3.8, 3.0, 3.1, 2.4), fist=3.4,
              leg=(4.1, 3.0, 1.7), shoulder=1, torso_deco=ph_torso_deco, arm_deco=ph_arm_deco, leg_deco=ph_leg_deco,
              pad=ph_pad, belt=ph_belt, front=ph_front, neck_r=3.4, ghost=('w', 'V'), poses=hunch)
    return S.sheet()


# ====================================================================== 辣妹
SG_HEAD = """
....kkkk....
..kkaaaakk..
.kaavkvvkvk.
.kavvvvvvvvk
kavkvvkvvkvk
kvvvvvvvvvvk
kvvkyykvkyyk
kVvkkkvvkkk.
.kVvvvvvvvk.
.kVvvvrrrk..
..kVVvkkk...
...kkkkk....
"""
SG_SHOUT = SG_HEAD.replace('.kVvvvrrrk..\n..kVVvkkk...', '.kVvvkxxxk..\n..kVVkrrk...')


def diamonds(p, mask, step=4):
    ys, xs = mask.nonzero()
    for y, x in zip(ys, xs):
        c = p.c[y, x]
        if c in 'av' and ((x + y) % step == 0 or (x - y) % step == 0):
            p.c[y, x] = 'V'


def sg_torso(p, S, cx, ty):
    m = p.poly([(cx - 7, ty + 1), (cx + 7, ty + 1), (cx + 6, ty + 7), (cx + 3, ty + 12), (cx + 6, ty + 18), (cx - 6, ty + 18),
                (cx - 3, ty + 12), (cx - 6, ty + 7)])
    p.paint(m, 'avVx', hi=0.24, sh=0.68)
    diamonds(p, m)
    for dx in (-3.5, 4.0):
        p.paint(p.ell(cx + dx, ty + 7, 3.4, 2.9), 'avVx', hi=0.4, sh=0.62)
    p.paint(p.rect(cx - 1, ty + 2, cx + 1, ty + 4), 'iyY', hi=0.3, sh=0.7)


def sg_pad(p, x, y, near):
    knob(p, x, y, 3.2 if near else 2.8, 'wqz')


def sg_belt(p, x, y, ph):
    p.paint(p.poly([(x - 7, y - 1), (x + 7, y - 1), (x + 5, y + 2), (x, y + 5), (x - 5, y + 2)]), 'wqz', hi=0.3, sh=0.6)
    knob(p, x, y + 1, 1.6, 'iyY')


def sg_arm_deco(p, s, e, f, near):
    diamonds(p, p.cap(s[0], s[1], e[0], e[1], 3.6))
    band_on(p, e, f, 0.55, 0.35, 'avVx', 'wqzz', 3.0)


def sg_leg_deco(p, hip, knee, foot, near):
    diamonds(p, p.cap(hip[0], hip[1], knee[0], knee[1], 4.0))
    knob(p, knee[0], knee[1], 2.2, 'wqz')
    band_on(p, knee, foot, 0.65, 0.35, 'avVx', 'wqzz', 2.8)


def spice_girl():
    S = Stand(pal(a='#ffe2f2', v='#f492c6', V='#c4508e', x='#842862', w='#ffffff', q='#d4c8e4', z='#948cb4', y='#58d0b0',
                  r='#d8284c', i='#fff6b4', Y='#a87414'),
              'avVx', SG_HEAD, SG_SHOUT, arm=(2.6, 2.0, 2.1, 1.7), fist=2.5, leg=(3.2, 2.2, 1.2), shoulder=-1, neck_r=2.2,
              torso=sg_torso, pad=sg_pad, belt=sg_belt, arm_deco=sg_arm_deco, leg_deco=sg_leg_deco, ghost=('w', 'V'),
              poses={'idle': dict(far=(8, 3, 15, 10, 6, 15), near=(-8, 4, -15, 8, -18, 0), far_front=True),
                     'pose': dict(far=(8, 3, 15, 6, 20, -2), near=(-8, 4, -14, 10, -6, 16), far_front=False, far_fist=True,
                                  near_fist=True, w=52)})
    return S.sheet()


# ====================================================================== 黄金体验镇魂曲
GER_HEAD = """
.....kk.....
....kaak....
...kaoovk...
..kaoaaovk..
.kaoaooaovk.
.kvoaoaaovk.
.kvvooooVVk.
.kvvvkkkkkkk
.kVvkppkkppk
.kVvvkkaakk.
..kVVaaaak..
...kkkkkk...
"""
GER_SHOUT = GER_HEAD.replace('..kVVaaaak..', '..kVVakkkk..')


def ger_torso_deco(p, cx, ty):
    for dx in (-5, 5):
        knob(p, cx + dx, ty + 6, 3.0, 'ppP')
    for yy in (ty + 12, ty + 14, ty + 16):
        p.line([(cx - 4, yy), (cx + 4, yy)], 'o', only='avV')
    knob(p, cx, ty + 2, 1.8, 'ioO')


def ger_pad(p, x, y, near):
    knob(p, x, y, 3.8 if near else 3.3, 'avVx')
    knob(p, x, y, 1.6, 'ioO')


def ger_belt(p, x, y, ph):
    p.paint(p.rect(x - 6, y - 1, x + 6, y), 'ioO', hi=0.3, sh=0.7)
    p.paint(p.poly([(x - 4, y + 2), (x + 4, y + 2), (x, y + 7)]), 'ppP', hi=0.3, sh=0.6)


def ger_limb(p, a, b, n=2):
    for k in range(1, n + 1):
        band_on(p, a, b, k / (n + 1), 0.08, 'avVx', 'ooOO', 4.4)


def ger_arm_deco(p, s, e, f, near):
    ger_limb(p, e, f)


def ger_leg_deco(p, hip, knee, foot, near):
    ger_limb(p, hip, knee)
    knob(p, knee[0], knee[1], 2.4, 'ppP')
    ger_limb(p, knee, foot)


def gold_requiem():
    S = Stand(pal(a='#fffcec', v='#f8e0a4', V='#d0a254', x='#906420', i='#ffd890', o='#f0842c', O='#b04c14', p='#f06c9c',
                  P='#a83064'),
              'avVx', GER_HEAD, GER_SHOUT, chest=(9.2, 6.2), waist=(7, 4.4, 18), arm=(3.1, 2.4, 2.5, 2.0), leg=(3.4, 2.5, 1.4),
              torso_deco=ger_torso_deco, pad=ger_pad, belt=ger_belt, arm_deco=ger_arm_deco, leg_deco=ger_leg_deco,
              ghost=('a', 'V'),
              poses={'idle': dict(far=(8, 3, 15, 9, 19, 13), near=(-8, 4, -15, 10, -17, 15),
                                  legs=((3, 19, 5, 27, 3, 36), (-3, 19, -5, 27, -6, 35))),
                     'pose': dict(far=(8, 3, 15, 8, 20, 13), near=(-8, 4, -15, 8, -20, 13), far_front=False, far_fist=True,
                                  near_fist=True, w=60, bx=30, legs=((3, 19, 5, 27, 3, 36), (-3, 19, -5, 27, -4, 36)))})
    sh = S.sheet()
    # “归零”：身周一圈圈金环向外扩开
    base = [r for r in sh.rows if r[0] == 'pose'][0][1][0]
    bb = base.bbox()
    mx, my = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    frames = []
    for i in range(3):
        out = base.copy()
        for k, col in ((0, '#ffd860'), (1, '#fff4c0')):
            r = 13 + i * 3 + k * 6
            ring = Cv(out.w, out.h)
            for deg in range(0, 360, 3):
                if (deg // 15 + i + k) % 3 == 0:
                    continue
                y = my + r * math.sin(math.radians(deg))
                if y <= OY:
                    ring.put(mx + r * math.cos(math.radians(deg)), y, col)
            out.under(ring)
        frames.append(out)
    sh.add('zero', frames, 8, 'loop')
    return sh


STANDS = {
    'moodyblues': ('忧郁蓝调', moody_blues),
    'purplehaze': ('紫烟', purple_haze),
    'spicegirl': ('辣妹', spice_girl),
    'requiem': ('黄金体验镇魂曲', gold_requiem),
}
ACTION_NAMES = {'rewind': '回放', 'zero': '归零'}
