# 第五部替身（二）：非人形的几个——性感手枪、航空史密斯、金属制品、沙滩男孩、娃娃脸、冲突、传话头。
import math

from stand5 import special

DIGITS = {1: ('.k.', 'kk.', '.k.', '.k.', 'kkk'), 2: ('kkk', '..k', 'kkk', 'k..', 'kkk'), 3: ('kkk', '..k', 'kkk', '..k', 'kkk'),
          5: ('kkk', 'k..', 'kkk', '..k', 'kkk'), 6: ('kkk', 'k..', 'kkk', 'k.k', 'kkk'), 7: ('kkk', '..k', '..k', '..k', '..k')}

# ====================================================================== 性感手枪：六个金色小家伙，编号 1 2 3 5 6 7（没有 4）
PISTOL = """
......k......
.....kak.....
....kayyk....
...kayyyyk...
..kayiiiyyk..
..kyyiiiyyk..
..kyyiiiyYk..
..kyyiiiyYk..
..kyyiiiyYk..
..kywwywwYk..
..kywekweYk..
..kyyyyyyyk..
..kYkrrrkYk..
...kYkkkYk...
.kkykYYYkykk.
.kykkyyykkyk.
..k.kykyk.k..
....kk.kk....
"""
SPEC_PAL = dict(a='#fff8c8', i='#ffe884', y='#f0bc30', Y='#b4780c', w='#ffffff', e='#201020', r='#d83048', m='#fff0a0',
                o='#ff8c20', s='#c8ccd8', S='#7c8298')


def pistol(p, x, y, n, mouth=False, lean=0):
    g = [r for r in PISTOL.strip('\n').split('\n')]
    d = DIGITS[n]
    for j in range(5):
        row = list(g[4 + j])
        for i in range(3):
            if d[j][i] == 'k':
                row[5 + i] = 'k'
        g[4 + j] = ''.join(row)
    if mouth:
        g[12] = '..kYrrrrrYk..'
        g[13] = '...kYrrrYk...'
    if lean:
        g = [('.' * lean + r) if j < 7 else r + '.' * lean for j, r in enumerate(g)]
    p.stamp('\n'.join(g), x, y)


HOME = [(2, 8, 1), (18, 4, 2), (35, 8, 3), (7, 30, 5), (23, 27, 6), (40, 30, 7)]


def sp_idle(ph):
    def fn(p):
        for k, (x, y, n) in enumerate(HOME):
            pistol(p, x, y + [0, 1, 2, 1][(ph + k) % 4], n, mouth=(k + ph) % 5 == 0)
    return fn


def bullet(p, x, y, trail):
    p.paint(p.poly([(x, y - 2), (x + 5, y - 2), (x + 8, y), (x + 5, y + 2), (x, y + 2)]), 'ayY', hi=0.3, sh=0.6)
    for dy, L in ((-3, trail), (0, trail + 5), (3, trail - 3)):
        if L > 0:
            p.line([(x - L, y + dy), (x - 2, y + dy)], 's')


def sp_attack(step):
    def fn(p):
        # 三号上前踢子弹，其他人喊加油
        pos = [(0, 4, 1), (14, 1, 2), None, (0, 36, 5), (15, 37, 6), (0, 20, 7)]
        for k, q in enumerate(pos):
            if q:
                pistol(p, q[0], q[1] - (step + k) % 2, q[2], mouth=True)
        kx = (22, 30, 28)[step]
        pistol(p, kx, 18, 3, mouth=True, lean=2 if step else 0)
        bx_, trail = ((36, 0), (46, 8), (58, 16))[step]
        if step:
            m = p.ell(kx + 15, 31, 3, 3)
            p.paint(m, 'amo', outline='o', hi=0.5, sh=0.7)
        bullet(p, bx_, 30 if step else 31, trail)
    return fn


def sp_pose(ph):
    def fn(p):
        for k, (n, x, y) in enumerate(((1, 0, 28), (2, 10, 20), (3, 20, 14), (5, 32, 14), (6, 42, 20), (7, 52, 28))):
            pistol(p, x, y - ((k + ph) % 2) * 2, n, mouth=ph % 2 == 0)
    return fn


def sex_pistols():
    return special(SPEC_PAL, [('idle', [sp_idle(i) for i in range(4)], 6, 'loop', 56),
                              ('attack', [sp_attack(i) for i in range(3)], 10, 'oneshot', 68),
                              ('pose', [sp_pose(i) for i in range(2)], 4, 'loop', 64)], bx=28)


# ====================================================================== 航空史密斯：小型螺旋桨战斗机
AERO_PAL = dict(a='#a8e0ff', v='#4c94e4', V='#2858a8', x='#16346c', w='#ffffff', q='#c8d4e8', z='#7884a4', y='#ffd43c',
                Y='#b4840c', r='#e83844', R='#8c1828', c='#8cf4f0', C='#2c9ca8', g='#58606c', G='#2c303c', f='#fff4a0', o='#ff8c20')


def plane(p, ph, tilt=0.0, fire=False, dx=0, dy=0):
    def P(x, y):
        return (x + dx, y + dy - (x - 26) * tilt)

    def poly(pts):
        return p.poly([P(x, y) for x, y in pts])

    def cap(a, b, r0, r1=None):
        A, B = P(*a), P(*b)
        return p.cap(A[0], A[1], B[0], B[1], r0, r1)
    # 远侧机翼
    p.paint(poly([(22, 28), (34, 28), (22, 19), (17, 19)]), 'vVx', hi=0.3, sh=0.55)
    # 垂尾、平尾
    p.paint(poly([(7, 30), (3, 18), (9, 18), (18, 29)]), 'avVx', hi=0.3, sh=0.6)
    p.paint(poly([(3, 20), (9, 20), (11, 23), (5, 23)]), 'wqz', hi=0.3, sh=0.7)
    # 机身
    p.paint(cap((8, 31), (24, 32), 2.6, 6.4) | cap((24, 32), (38, 32), 6.4, 5.4), 'avVx', hi=0.24, sh=0.66)
    p.paint(cap((38, 32), (42, 32), 5.4, 3.8), 'iyY' if 'i' in p.c else 'fyY', hi=0.3, sh=0.6)
    p.line([P(13, 35), P(36, 36)], 'q', only='avVx')
    # 座舱和雷达眼
    p.paint(p.ell(*P(24, 26), 5.0, 3.2), 'wcC', hi=0.3, sh=0.6)
    p.line([P(24, 24), P(24, 28)], 'z', only='wcC')
    for ox, ch in ((15, 'r'), (16, 'r'), (15, 'R')):
        p.px(*P(ox, 31 + (ch == 'R')), ch)
    # 近侧机翼和机枪
    p.paint(poly([(20, 33), (35, 33), (25, 45), (17, 45)]), 'avVx', hi=0.3, sh=0.58)
    p.paint(p.ell(*P(24, 40), 2.4, 2.4), 'wqz', hi=0.3, sh=0.6)
    p.px(*P(24, 40), 'r')
    for gy in (37, 43):
        p.paint(cap((28, gy), (35, gy), 1.0), 'qgG', hi=0.3, sh=0.6)
    # 起落架
    for wx in (20, 34):
        p.line([P(wx, 38), P(wx - 1, 46)], 'z')
        p.paint(p.ell(*P(wx - 1, 47), 2.2, 2.2), 'qgG', hi=0.3, sh=0.6)
    # 螺旋桨（三个相位）
    hub = P(44, 32)
    blade = ph % 3
    if blade == 0:
        p.paint(cap((45, 20), (45, 44), 0.8), 'wqz', hi=0.4, sh=0.7)
    elif blade == 1:
        p.paint(cap((43, 23), (47, 41), 0.8), 'wqz', hi=0.4, sh=0.7)
        p.line([P(46, 22), P(46, 26)], 'q')
    else:
        p.paint(cap((45, 26), (45, 38), 1.2), 'wqz', hi=0.4, sh=0.7)
        p.line([P(46, 21), P(46, 24)], 'q')
        p.line([P(46, 40), P(46, 43)], 'q')
    p.paint(p.ell(hub[0], hub[1], 2.0, 2.0), 'fyY', hi=0.4, sh=0.6)
    if fire:
        for gy in (37, 43):
            m = p.poly([P(36, gy), P(39, gy - 2), P(38, gy), P(41, gy), P(38, gy + 1), P(39, gy + 2)])
            p.paint(m, 'ffo', outline='o', hi=0.4, sh=0.7)
            for k, off in enumerate((10, 22)):
                x0 = 38 + off + (ph % 2) * 5 + (gy > 40) * 3
                p.line([P(x0, gy), P(x0 + 5, gy)], 'f')
                p.px(*P(x0 + 6, gy), 'w')


def aerosmith():
    return special(AERO_PAL, [
        ('idle', [(lambda i: (lambda p: plane(p, i, dy=[-4, -3, -2, -3][i])))(i) for i in range(4)], 10, 'loop', 52),
        ('attack', [(lambda i: (lambda p: plane(p, i, tilt=-0.06, fire=True, dy=-3, dx=-(i % 2))))(i) for i in range(3)], 14, 'loop', 72),
        ('pose', [(lambda i: (lambda p: plane(p, i, tilt=0.24, dy=-6 - i)))(i) for i in range(2)], 8, 'loop', 52)], bx=24)


# ====================================================================== 金属制品：一大群住在体内的小东西，把铁分变成刀片
MET_PAL = dict(a='#e0eef8', v='#94acc4', V='#566c8c', x='#2c3c5c', e='#101020', m='#7c2c40', w='#ffffff', q='#c4ccd8',
               z='#6c7488', r='#e02c40', R='#80101c')
IMP = """
..kkk..
.kaaak.
kakvkvk
kakvkvk
kavvvvk
.kvmvk.
..kvk..
.kvkVk.
.k...k.
"""
IMP2 = """
..kkk..
.kaaak.
kavkvkk
kavkvkk
kavvvvk
.kvmvk.
.kkvkk.
..kvk..
..k.k..
"""
SWARM = [(4, 14), (15, 8), (28, 11), (40, 17), (9, 25), (21, 21), (33, 23), (2, 38), (14, 35), (27, 34), (39, 31), (46, 40),
         (8, 46), (21, 45), (34, 46)]
RAZOR = """
.kkkkkkk.
kwwwwwwqk
kqkzzzkqk
kwqqqqqzk
.kkkkkkk.
"""
NAIL = """
kkkkkkk..
kwwqqqqkk
kkkkkkk..
"""


def met_idle(ph):
    def fn(p):
        for k, (x, y) in enumerate(SWARM):
            jx = [0, 1, 0, -1][(ph + k) % 4]
            jy = [0, -1, -1, 0][(ph + k * 3) % 4]
            p.stamp(IMP if (k + ph // 2) % 3 else IMP2, x + jx, y + jy)
    return fn


def met_attack(step):
    def fn(p):
        for k, (x, y) in enumerate(SWARM[:9]):
            p.stamp(IMP if k % 2 else IMP2, x - 2, y + (step + k) % 2)
        spots = [(40, 12), (48, 24), (38, 33), (52, 40), (34, 22)]
        for k, (x, y) in enumerate(spots[:2 + step * 2]):
            grid = RAZOR if k % 2 == 0 else NAIL
            p.stamp(grid, x + step * 4, y + (k % 2) * 2)
            p.line([(x + step * 4 - 7, y + 2), (x + step * 4 - 2, y + 2)], 'r')
    return fn


def met_pose(ph):
    def fn(p):
        # 叠成一座小塔，顶上那只举着刀片
        rows = [[(10, 45), (18, 45), (26, 45), (34, 45)], [(14, 36), (22, 36), (30, 36)], [(18, 27), (26, 27)], [(22, 18)]]
        for j, row in enumerate(rows):
            for k, (x, y) in enumerate(row):
                p.stamp(IMP if (j + k + ph) % 2 else IMP2, x, y - ((j + k + ph) % 2))
        p.stamp(RAZOR, 21, 10 - ph)
    return fn


def metallica():
    return special(MET_PAL, [('idle', [met_idle(i) for i in range(4)], 6, 'loop', 54),
                             ('attack', [met_attack(i) for i in range(3)], 10, 'oneshot', 68),
                             ('pose', [met_pose(i) for i in range(2)], 4, 'loop', 52)], bx=26)


# ====================================================================== 沙滩男孩：一根会自己咬钩的钓竿
BB_PAL = dict(a='#f4f8ff', v='#b4c0d4', V='#6c7894', x='#38405c', w='#ffffff', q='#d4dcec', r='#e8303c', R='#841420',
              b='#7c4c2c', B='#4c2c18', n='#b07844', y='#ffd43c', Y='#a87c10')


def rod(p, grip, tip, bend, line_pts, hook=True):
    gx, gy = grip
    tx_, ty_ = tip
    mx, my = (gx + tx_) / 2 + bend[0], (gy + ty_) / 2 + bend[1]
    pts = []
    for i in range(13):
        u = i / 12
        pts.append(((1 - u) ** 2 * gx + 2 * (1 - u) * u * mx + u * u * tx_,
                    (1 - u) ** 2 * gy + 2 * (1 - u) * u * my + u * u * ty_))
    shaft = p.empty()
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        shaft |= p.cap(a[0], a[1], b[0], b[1], max(0.7, 2.0 - i * 0.13))
    p.paint(shaft, 'avVx', hi=0.35, sh=0.6)
    # 握把
    a, b = pts[0], pts[3]
    p.paint(p.cap(a[0], a[1], b[0], b[1], 2.6), 'nbB', hi=0.3, sh=0.6)
    p.paint(p.ell(a[0], a[1], 2.4, 2.4), 'qvV', hi=0.3, sh=0.6)
    # 绕线轮（中间一只红眼睛）
    rx, ry = pts[4]
    p.paint(p.ell(rx + 2, ry + 4, 4.2, 4.2), 'avVx', hi=0.3, sh=0.6)
    p.paint(p.ell(rx + 2, ry + 4, 2.0, 2.0), 'wrR', hi=0.3, sh=0.6)
    p.line([(rx + 5, ry + 6), (rx + 8, ry + 8)], 'V')
    # 导线环
    for i in (6, 8, 10):
        x, y = pts[i]
        p.px(x + 1, y + 1.6, 'y')
        p.px(x + 2, y + 2.2, 'Y')
    path = [(tx_, ty_)] + line_pts
    p.line(path, 'q')
    if hook:
        hx, hy = path[-1]
        p.stamp("""
        .y..
        .y..
        .y.y
        .y.y
        ..Y.
        """, hx - 1, hy)


def beach_boy():
    idle = [(lambda i: (lambda p: rod(p, (8, 48), (40 + [0, 1, 2, 1][i], 14 + [0, 0, 1, 0][i]), (-4, -8),
                                      [(44 + [0, 1, 2, 1][i], 24), (43 + [0, 1, 0, -1][i], 38)])))(i) for i in range(4)]
    cast = [lambda p: rod(p, (14, 46), (4, 10), (14, -6), [(0, 22), (6, 34)]),
            lambda p: rod(p, (6, 44), (40, 18), (-2, -14), [(52, 20), (64, 30)]),
            lambda p: rod(p, (6, 44), (42, 28), (0, -16), [(54, 40), (68, 42)])]
    pose = [(lambda i: (lambda p: rod(p, (22, 50), (28, 6), (-8 - i, 0),
                                      [(40, 12 + i), (44, 28), (32, 38 - i), (20, 30), (26, 20 + i), (36, 24)])))(i) for i in range(2)]
    return special(BB_PAL, [('idle', idle, 6, 'loop', 52), ('attack', cast, 10, 'oneshot', 74), ('pose', pose, 4, 'loop', 52)],
                   bx=24)


# ====================================================================== 娃娃脸：装在笔记本电脑里、能分解重组的“儿子”
BF_PAL = dict(a='#b8e4ff', v='#4c9ce0', V='#2460a8', x='#123470', w='#ffffff', q='#c4c8d8', z='#80889c', Z='#484e64',
              c='#78f4dc', C='#1c8c84', d='#103c44', y='#ffe040', Y='#b88c10', e='#101428', m='#f0486c')


def laptop(p, oy, flick):
    p.paint(p.poly([(10, 14 + oy), (34, 12 + oy), (36, 29 + oy), (12, 31 + oy)]), 'qzZ', hi=0.2, sh=0.7)
    p.paint(p.poly([(13, 16 + oy), (32, 15 + oy), (33, 27 + oy), (14, 28 + oy)]), 'd', outline='k')
    for j, (x0, x1) in enumerate(((16, 25), (16, 29), (18, 23), (16, 28))):
        yy = 18 + oy + j * 2.6 + (flick % 2)
        p.line([(x0, yy), (x1 - (j + flick) % 3, yy - 0.5)], 'c' if (j + flick) % 2 else 'C', only='d')
    p.paint(p.ell(29, 22 + oy, 2.2, 2.2), 'wcC', hi=0.3, sh=0.6)
    p.paint(p.poly([(12, 31 + oy), (36, 29 + oy), (46, 36 + oy), (20, 39 + oy)]), 'qzZ', hi=0.25, sh=0.65)
    for j in range(3):
        for i in range(8):
            x, y = 18 + i * 3 + j * 2.4, 32.5 + oy + j * 2.0 - i * 0.2
            p.px(x, y, 'w')
            p.px(x + 1, y, 'Z')


def baby_head(p, cx, cy, mouth=False):
    p.paint(p.ell(cx, cy, 9, 7.2), 'avVx', hi=0.28, sh=0.64)
    for dx in (-4, 4):
        p.paint(p.ell(cx + dx + 1, cy - 1, 2.6, 2.0), 'wyY', hi=0.3, sh=0.6)
        p.px(cx + dx + 2, cy - 1, 'e')
    if mouth:
        p.paint(p.ell(cx + 2, cy + 4, 3.0, 2.2), 'm')
    else:
        p.line([(cx - 1, cy + 4), (cx + 5, cy + 3.4)], 'e')
    for dx in (-8, 8):
        p.paint(p.ell(cx + dx, cy + 6, 2.6, 2.2), 'avVx', hi=0.3, sh=0.6)


def bf_idle(i):
    def fn(p):
        oy = [0, 1, 2, 1][i]
        baby_head(p, 25, 43 + oy)
        laptop(p, oy - 1, i)
    return fn


def cube(p, x, y, s=3):
    p.paint(p.rect(x, y, x + s, y + s), 'avV', hi=0.4, sh=0.6)


def bf_attack(i):
    def fn(p):
        laptop(p, 0, i)
        # 分解成方块飞出去，在前面拼回人形
        for k in range(10 + i * 3):
            x = 40 + (k * 7) % (10 + i * 9)
            y = 14 + (k * 13) % 30
            if i < 2 or k % 3:
                cube(p, x, y, 2 if k % 2 else 3)
        if i:
            cx = 56 + i * 4
            p.paint(p.cap(cx, 34, cx - 1, 42, 4.0, 3.0), 'avVx')
            for s in (-1, 1):
                p.paint(p.cap(cx, 42, cx + 4 * s, 51, 1.8, 1.4), 'avVx')
                p.paint(p.cap(cx, 34, cx + (7 if s > 0 else -5), 36 - 5 * (s > 0) * (i - 1), 1.6, 1.2), 'avVx')
            baby_head(p, cx, 26, mouth=True)
    return fn


def bf_pose(i):
    def fn(p):
        laptop(p, 6 + i, i)
        baby_head(p, 27, 12 + i * 2, mouth=i == 1)
        for k in range(5):
            cube(p, 6 + k * 9, 4 + (k * 11 + i * 3) % 12, 2)
    return fn


def baby_face():
    return special(BF_PAL, [('idle', [bf_idle(i) for i in range(4)], 6, 'loop', 52),
                            ('attack', [bf_attack(i) for i in range(3)], 9, 'oneshot', 76),
                            ('pose', [bf_pose(i) for i in range(2)], 4, 'loop', 52)], bx=26)


# ====================================================================== 冲突：藏在任何液体里的鲨鱼
CL_PAL = dict(a='#b4c4e8', v='#6478ac', V='#3a4876', x='#1e2648', w='#ffffff', q='#d8e0f0', z='#8c98bc', y='#ffd028',
              Y='#a87400', m='#7c1830', r='#c8304c', c='#b4f0ff', C='#4cb4e4', B='#2870b0')


def shark(p, ph, open_=0, dx=0, dy=0):
    w = [0, 2, 0, -2][ph % 4]

    def poly(pts):
        return p.poly([(x + dx, y + dy) for x, y in pts])
    # 尾巴
    p.paint(poly([(12, 32), (2, 20 + w), (8, 31 + w / 2), (3, 44 + w), (13, 36)]), 'avVx', hi=0.3, sh=0.6)
    # 背鳍、胸鳍
    p.paint(poly([(18, 27), (23, 12), (28, 17), (31, 26)]), 'avVx', hi=0.3, sh=0.6)
    body = (p.cap(11 + dx, 34 + dy, 27 + dx, 32 + dy, 2.8, 9.6) | p.cap(27 + dx, 32 + dy, 40 + dx, 30 + dy, 9.6, 6.4)
            | poly([(34, 22), (52, 27), (40, 33)]))
    p.paint(body, 'avVx', hi=0.22, sh=0.68)
    p.paint(p.ell(27 + dx, 38 + dy, 12, 3.4) & body, 'qqz', outline=None, hi=0.2, sh=0.7)
    # 嘴和牙
    jaw = 3 + open_ * 3
    p.paint(poly([(33, 34), (51, 29), (47, 33 + jaw), (37, 37 + jaw / 2)]), 'm')
    p.paint(poly([(34, 37), (47, 34 + jaw), (40, 40 + jaw), (33, 40)]), 'avVx', hi=0.3, sh=0.6)
    for k in range(5):
        x = 36 + k * 3
        p.px(x + dx, 33 - k * 0.9 + dy + 1, 'w')
        p.px(x + dx, 34 - k * 0.9 + dy + 1, 'q')
        p.px(x + dx + 1, 37 + jaw / 2 - k * 0.4 + dy, 'w')
    p.paint(p.ell(39 + dx, 27 + dy, 2.6, 2.0), 'wyY', hi=0.3, sh=0.6)
    p.px(40 + dx, 27 + dy, 'k')
    for k in range(3):
        p.line([(25 + k * 3 + dx, 29 + dy), (24 + k * 3 + dx, 35 + dy)], 'x', only='avV')
    p.paint(poly([(25, 38), (16, 49), (23, 47), (33, 39)]), 'avVx', hi=0.3, sh=0.6)
    for x, y in ((16, 30), (22, 26), (31, 24)):
        p.px(x + dx, y + dy, 'q')


def splash(p, ph, y=50, big=False):
    base = p.ell(26, y + 2, 24 if big else 18, 3.4)
    p.paint(base, 'cCB', hi=0.3, sh=0.6)
    for k, x in enumerate((4, 11, 19, 33, 42, 49)):
        h = (6 if big else 3) + (k + ph) % 3 * 2
        p.paint(p.cap(x, y, x + (-2 if x < 26 else 2), y - h, 1.5, 0.6), 'cCB', hi=0.4, sh=0.6)
        p.px(x + (-3 if x < 26 else 3), y - h - 3, 'c')


def clash():
    idle = [(lambda i: (lambda p: shark(p, i, dy=[-4, -3, -2, -3][i])))(i) for i in range(4)]
    atk = [(lambda i: (lambda p: shark(p, i, open_=(0, 2, 1)[i], dx=(-2, 10, 16)[i], dy=(-2, -6, -3)[i])))(i) for i in range(3)]

    def pose(i):
        def fn(p):
            shark(p, i, open_=i, dy=2 - i * 2)
            splash(p, i, 49, big=True)
        return fn
    return special(CL_PAL, [('idle', idle, 8, 'loop', 56), ('attack', atk, 10, 'oneshot', 72),
                            ('pose', [pose(0), pose(1)], 4, 'loop', 56)], bx=27)


# ====================================================================== 传话头：附在舌头上的红色小怪物
TH_PAL = dict(a='#ff9c84', v='#e0463c', V='#9c1c24', x='#5c0a18', w='#ffffff', y='#ffe040', Y='#c08c10', q='#c8ccdc',
              z='#7c8098', p='#ff8cb0', P='#c8406c', Q='#84203c')


def imp(p, ph, oy=0, tongue=0, dx=0):
    sw = [0, 2, 0, -2][ph % 4]
    cx, cy = 20 + dx, 24 + oy
    # 尾巴
    tail = (p.cap(cx, cy + 14, cx - 6, cy + 22, 2.8, 1.8) | p.cap(cx - 6, cy + 22, cx + 2, cy + 27, 1.8, 1.2)
            | p.cap(cx + 2, cy + 27, cx + 9 + sw, cy + 22, 1.2, 0.7))
    p.paint(tail, 'avVx', hi=0.3, sh=0.6)
    # 头上卷着的触角
    for (ax, ay), (bx_, by_), (ex, ey) in (((-7, -4), (-15, -10 + sw), (-12, -17)), ((-3, -8), (-6, -17), (1 + sw, -20)),
                                           ((4, -8), (10, -16 - sw), (6, -20)), ((-9, 1), (-17, 2 - sw), (-18, -5))):
        m = p.cap(cx + ax, cy + ay, cx + bx_, cy + by_, 2.4, 1.6) | p.cap(cx + bx_, cy + by_, cx + ex, cy + ey, 1.6, 0.8)
        p.paint(m, 'avVx', hi=0.3, sh=0.6)
    # 身子和手
    p.paint(p.cap(cx, cy + 6, cx, cy + 15, 4.6, 3.0), 'avVx')
    for s in (-1, 1):
        m = p.cap(cx + 3 * s, cy + 9, cx + 11 * s, cy + 13 - sw * s, 1.7, 1.2)
        p.paint(m, 'avVx', hi=0.3, sh=0.6)
        p.paint(p.ell(cx + 12 * s, cy + 13 - sw * s, 1.8, 1.8), 'avVx', hi=0.3, sh=0.6)
    p.paint(p.ell(cx, cy, 10, 9), 'avVx', hi=0.24, sh=0.66)
    for ex_, ey_ in ((0, -1), (7, -1)):
        p.paint(p.ell(cx + ex_, cy + ey_, 2.8, 2.2), 'wyY', hi=0.3, sh=0.6)
        p.px(cx + ex_ + 1, cy + ey_, 'k')
    p.line([(cx - 3, cy - 5), (cx + 2, cy - 3)], 'x')
    p.line([(cx + 9, cy - 5), (cx + 5, cy - 3)], 'x')
    p.paint(p.ell(cx + 4, cy + 5, 3.6, 1.6), 'x')
    for k in (1, 4, 7):
        p.px(cx + k, cy + 4, 'w')
    p.paint(p.ell(cx, cy - 6, 1.6, 1.6), 'wqz', hi=0.4, sh=0.6)
    if tongue:
        L = tongue
        m = p.cap(cx + 5, cy + 6, cx + 5 + L * 0.6, cy + 10 + (ph % 2) * 2, 2.0, 2.6) | p.cap(
            cx + 5 + L * 0.6, cy + 10 + (ph % 2) * 2, cx + 5 + L, cy + 6, 2.6, 1.4)
        p.paint(m, 'pPQ', hi=0.3, sh=0.6)
        p.line([(cx + 7, cy + 7), (cx + 3 + L, cy + 8)], 'Q', only='pP')


def talking_head():
    idle = [(lambda i: (lambda p: imp(p, i, oy=[-2, -1, 0, -1][i])))(i) for i in range(4)]
    atk = [(lambda i: (lambda p: imp(p, i, tongue=(8, 22, 34)[i], dx=i)))(i) for i in range(3)]
    pose = [(lambda i: (lambda p: imp(p, i * 2, oy=-4 - i * 2, tongue=6 + i * 4)))(i) for i in range(2)]
    return special(TH_PAL, [('idle', idle, 6, 'loop', 48), ('attack', atk, 10, 'oneshot', 66), ('pose', pose, 4, 'loop', 48)],
                   bx=22)


STANDS = {
    'sexpistols': ('性感手枪', sex_pistols),
    'aerosmith': ('航空史密斯', aerosmith),
    'metallica': ('金属制品', metallica),
    'beachboy': ('沙滩男孩', beach_boy),
    'babyface': ('娃娃脸', baby_face),
    'clash': ('冲突', clash),
    'talkinghead': ('传话头', talking_head),
}
