# 第五部替身（一）：主角团和老板的人形替身。黄金体验、钢链手指、忧郁蓝调、紫烟、辣妹、绯红之王、黄金体验镇魂曲。
from stand5 import Stand, Pix

GOLD = {'a': '#fff4b4', 'v': '#f2c844', 'V': '#c0861c', 'x': '#7c500e'}


def pal(*ds, **kw):
    out = {}
    for d in ds:
        out.update(d)
    out.update(kw)
    return out


def knob(p, x, y, r, tones, outline='k'):
    p.paint(p.ell(x, y, r, r * 0.92), tones, outline=outline, hi=0.36, sh=0.62)


def band_on(p, a, b, frac, wide, src, dst, r=4.0):
    """在 a→b 这段肢体靠 frac 处套一圈宽 wide 的装饰（跟着身体明暗换色）"""
    x0, y0 = a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac
    x1, y1 = a[0] + (b[0] - a[0]) * min(1, frac + wide), a[1] + (b[1] - a[1]) * min(1, frac + wide)
    p.swap(p.cap(x0, y0, x1, y1, r), src, dst)


# ====================================================================== 黄金体验
GE_HEAD = """
....kkkkk...
..kkaaaavk..
.kaavVVVvvk.
.kavVaaVvvk.
.kvVavvaVVk.
.kvVvaaVVkk.
.kvVVVVkaak.
.kvVvkkaaaak
..kVkUUaaUUk
..kVkauaaauk
...kkaaappk.
.....kkkkk..
"""
GE_SHOUT = """
....kkkkk...
..kkaaaavk..
.kaavVVVvvk.
.kavVaaVvvk.
.kvVavvaVVk.
.kvVvaaVVkk.
.kvVVVVkaak.
.kvVvkkaaaak
..kVkUUaaUUk
..kVkauaaauk
...kkaakkkk.
.....kkppk..
"""


def ge_torso_deco(p, cx, ty):
    # 橙色胸甲（分节的横纹）+ 两枚瓢虫胸针
    top = p.rect(cx - 11, ty - 1, cx + 11, ty + 7)
    p.swap(top, 'avVx', 'ioOO')
    for yy in (ty + 3, ty + 6):
        for x0 in (-8, -3, 4):
            p.line([(cx + x0, yy), (cx + x0 + 2, yy)], 'O', only='iaoO')
    for bx, by in ((-6, 8), (5, 7)):
        knob(p, cx + bx, ty + by, 2.0, 'MuU')
        p.px(cx + bx, ty + by, 'k')


def ge_pad(p, x, y, near):
    # 肩上的小翅膀：往后上方翘，里面一个涡纹
    s = -1 if near else 1
    p.paint(p.ell(x, y + 1, 3.4, 2.8), 'avVx', hi=0.34, sh=0.62)
    wing = p.poly([(x - 2, y + 1), (x + 2, y + 1), (x + 3 * s + 1, y - 2), (x + 5 * s, y - 6), (x + 1 * s, y - 4), (x - 2 * s, y - 1)])
    p.paint(wing, 'wqz', hi=0.4, sh=0.66)
    p.line([(x, y - 1), (x + 2 * s, y - 2), (x + 2 * s, y - 3)], 'z', only='wq')


def ge_belt(p, x, y, ph):
    p.paint(p.rect(x - 6, y - 1, x + 6, y), 'wqz', hi=0.3, sh=0.7)
    w = [0, 1, 0, -1][ph % 4]
    for s, tip in ((-1, (x - 12, y + 7 + w)), (1, (x + 11, y + 5 - w))):
        m = p.cap(x + 5 * s, y, x + 9 * s, y + 4, 1.1) | p.cap(x + 9 * s, y + 4, tip[0], tip[1], 1.1, 0.7)
        p.paint(m, 'wqz', hi=0.4, sh=0.6)
    knob(p, x + 1, y + 2, 2.2, 'ioO')


def ge_arm_deco(p, s, e, f, near):
    band_on(p, e, f, 0.66, 0.1, 'avVx', 'MuUU', 2.9)


def ge_leg_deco(p, hip, knee, foot, near):
    knob(p, knee[0], knee[1], 2.5, 'MuU')
    p.px(knee[0], knee[1], 'k')
    band_on(p, knee, foot, 0.72, 0.28, 'avVx', 'ioOO', 2.6)


def gold_experience():
    pose = dict(far=(8, 3, 14, 9, 22, 6), near=(-8, 4, -15, 9, -7, 15), far_front=False, far_fist=True, near_fist=True,
                legs=((3, 19, 8, 25, 6, 35), (-3, 19, -6, 27, -9, 35)), w=56, bx=24)
    S = Stand(pal(GOLD, i='#ffe0a0', o='#f4962c', O='#bc5a12', M='#e8c0ff', u='#b062dc', U='#5c2c94', w='#ffffff',
                  q='#ccd4ec', z='#8c94bc', p='#c25870'),
              'avVx', GE_HEAD, GE_SHOUT, chest=(9.0, 6.0), waist=(7, 4.4, 18), arm=(3.0, 2.4, 2.5, 2.0), leg=(3.4, 2.5, 1.4),
              torso_deco=ge_torso_deco, pad=ge_pad, belt=ge_belt, arm_deco=ge_arm_deco, leg_deco=ge_leg_deco,
              poses={'pose': pose})
    return S.sheet()


# ====================================================================== 钢链手指
SF_HEAD = """
....kkkk....
..kkbbBBkk..
.kbbBByiBBk.
.kbBBByiBnk.
kbBBnnyynnk.
kBBnkaayavk.
kBnkaakyakk.
kBnkeayaeak.
.kBnkvvyvvk.
.knnkvvyvk..
..knkkvvkk..
...kkkkkk...
"""
SF_SHOUT = """
....kkkk....
..kkbbBBkk..
.kbbBByiBBk.
.kbBBByiBnk.
kbBBnnyynnk.
kBBnkaayavk.
kBnkaakyakk.
kBnkeayaeak.
.kBnkvvyvvk.
.knnkvkkkk..
..knkkvakk..
...kkkkkk...
"""


def zipper(p, pts, only):
    """沿折线打一条拉链：金色和暗金一格一换"""
    m = p.lmask(pts)
    ys, xs = m.nonzero()
    for y, x in zip(ys, xs):
        if p.c[y, x] in only:
            p.c[y, x] = 'y' if (x + y) % 2 else 'Y'


def sf_torso_deco(p, cx, ty):
    chest = p.poly([(cx - 11, ty - 1), (cx - 2, ty - 1), (cx, ty + 9), (cx - 7, ty + 11), (cx - 11, ty + 6)])
    chest |= p.poly([(cx + 2, ty - 1), (cx + 11, ty - 1), (cx + 11, ty + 6), (cx + 7, ty + 11), (cx, ty + 9)])
    p.swap(chest, 'avVx', 'bBnN')
    zipper(p, [(cx, ty + 2), (cx, ty + 17)], 'avVxbBnN')
    zipper(p, [(cx - 8, ty + 2), (cx - 3, ty + 8)], 'bBnN')
    knob(p, cx, ty + 3, 1.5, 'iyY')
    p.stamp("""
    .y.
    yiy
    .Y.
    """, cx - 1, ty + 12)


def sf_pad(p, x, y, near):
    knob(p, x, y, 4.4 if near else 3.8, 'bBn')
    knob(p, x, y, 1.4, 'iyY')


def sf_belt(p, x, y, ph):
    p.paint(p.rect(x - 6, y - 1, x + 6, y + 1), 'iyY', hi=0.3, sh=0.7)
    cod = p.poly([(x - 5, y + 2), (x + 5, y + 2), (x + 1, y + 6), (x - 1, y + 6)])
    p.paint(cod, 'bBnN', hi=0.3, sh=0.6)
    knob(p, x, y, 1.8, 'iyY')


def sf_arm_deco(p, s, e, f, near):
    band_on(p, e, f, 0.62, 0.38, 'avVx', 'bBnN', 3.2)
    zipper(p, [(s[0], s[1]), (e[0], e[1]), (f[0], f[1])], 'avVx')
    band_on(p, e, f, 0.54, 0.08, 'avVx', 'iyYY', 3.0)


def sf_leg_deco(p, hip, knee, foot, near):
    knob(p, knee[0], knee[1], 2.7, 'bBn')
    band_on(p, knee, foot, 0.55, 0.5, 'avVx', 'bBnN', 3.0)
    zipper(p, [hip, knee], 'avVx')


def sticky_fingers():
    S = Stand(pal(a='#ffffff', v='#dfe6f6', V='#9aa6d2', x='#5a628e', b='#8cc4ff', B='#3c74dc', n='#2348a0', N='#162c68',
                  i='#fff4b4', y='#f6c63a', Y='#a87414', e='#142048', w='#ffffff'),
              'avVx', SF_HEAD, SF_SHOUT, chest=(9.6, 6.4), waist=(7.6, 4.8, 18), arm=(3.3, 2.6, 2.8, 2.2), leg=(3.7, 2.7, 1.5),
              torso_deco=sf_torso_deco, pad=sf_pad, belt=sf_belt, arm_deco=sf_arm_deco, leg_deco=sf_leg_deco,
              fist_tones='bBn', ghost=('w', 'n'),
              poses={'pose': dict(far=(8, 3, 17, 5, 24, -3), near=(-8, 4, -15, 8, -10, -2), far_front=False, far_fist=True,
                                  near_fist=True, w=56, bx=24)})
    return S.sheet()


# ====================================================================== 绯红之王
KC_HEAD = """
....kkkk....
..kkaaaakk..
.kaavkkkvvk.
.kavkpppkvk.
kaavkkpkkvvk
kavvkppPkvvk
kvvvvkkkvvvk
kvkggkvkggkk
kVvkGGkkGGk.
.kVvvvvvvvk.
.kVkwkwkwk..
..kkkkkkk...
"""
KC_SHOUT = """
....kkkk....
..kkaaaakk..
.kaavkkkvvk.
.kavkpppkvk.
kaavkkpkkvvk
kavvkppPkvvk
kvvvvkkkvvvk
kvkggkvkggkk
kVvkGGkkGGk.
.kVvvvvvvvk.
.kVkkkkkkk..
..kkwkwkk...
"""


def lattice(p, mask, step=4, off=0):
    """身上的白色网格：横线和斜线交错，只画在红色皮肤上"""
    ys, xs = mask.nonzero()
    for y, x in zip(ys, xs):
        c = p.c[y, x]
        if c not in 'avV':
            continue
        if (y + off) % step == 0 or (x + y // 2) % step == 0:
            p.c[y, x] = 'w' if c in 'av' else 'q'


def kc_torso_deco(p, cx, ty):
    lattice(p, p.rect(cx - 12, ty + 1, cx + 12, ty + 17), 4, 1)
    # 胸口的暗色护颈
    p.paint(p.poly([(cx - 4, ty - 1), (cx + 6, ty - 1), (cx + 1, ty + 5)]), 'dDD', hi=0.3, sh=0.5)


def kc_pad(p, x, y, near):
    knob(p, x, y, 4.8 if near else 4.2, 'avV')
    lattice(p, p.ell(x, y, 4.8, 4.4), 3, 0)
    spike = p.poly([(x - 2, y - 3), (x + (-6 if near else 6), y - 8), (x + 2, y - 3)])
    p.paint(spike, 'wqz', hi=0.4, sh=0.6)


def kc_belt(p, x, y, ph):
    p.paint(p.rect(x - 7, y - 1, x + 7, y + 1), 'wqz', hi=0.3, sh=0.7)
    cloth = p.poly([(x - 5, y + 2), (x + 5, y + 2), (x + 2, y + 7), (x - 2, y + 7)])
    p.paint(cloth, 'dDD', hi=0.3, sh=0.5)
    for dx in (-4, 0, 4):
        p.px(x + dx, y, 'D')


def kc_arm_deco(p, s, e, f, near):
    lattice(p, p.cap(s[0], s[1], e[0], e[1], 4.2), 4, 0)
    band_on(p, e, f, 0.62, 0.3, 'avVx', 'wqzz', 3.4)


def kc_leg_deco(p, hip, knee, foot, near):
    lattice(p, p.cap(hip[0], hip[1], knee[0], knee[1], 4.6), 4, 2)
    knob(p, knee[0], knee[1], 2.4, 'wqz')
    band_on(p, knee, foot, 0.6, 0.4, 'avVx', 'wqzz', 3.0)


def king_crimson():
    S = Stand(pal(a='#ff968c', v='#dc2c42', V='#96122c', x='#56081c', w='#fdf2f4', q='#d0b4c0', z='#8c6478',
                  g='#6cf4a0', G='#1c9456', p='#f8bccc', P='#b4607c', d='#4c2434', D='#26101c'),
              'avVx', KC_HEAD, KC_SHOUT, chest=(10.6, 7.0), waist=(8.6, 5.4, 18), arm=(3.9, 3.0, 3.2, 2.5), fist=3.5,
              leg=(4.3, 3.1, 1.7), shoulder=1, torso_deco=kc_torso_deco, pad=kc_pad, belt=kc_belt, arm_deco=kc_arm_deco,
              leg_deco=kc_leg_deco, neck_r=3.4, ghost=('q', 'V'),
              poses={'idle': dict(far=(8, 3, 16, 9, 15, 17), near=(-8, 4, -15, 10, -13, 18)),
                     'pose': dict(far=(8, 3, 15, -1, 20, -8), near=(-8, 4, -15, 0, -20, -7), far_front=False, far_fist=True,
                                  near_fist=True, shout=True, w=60, bx=30,
                                  legs=((3, 19, 7, 26, 6, 35), (-3, 19, -7, 27, -6, 35)))})
    return S.sheet()


STANDS = {
    'goldexp': ('黄金体验', gold_experience),
    'stickyfingers': ('钢链手指', sticky_fingers),
    'kingcrimson': ('绯红之王', king_crimson),
}
