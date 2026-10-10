"""游戏层成年承太郎重画：小头、宽肩、高腰长腿，共用骨架保持所有动作一致。"""
import sys
sys.dont_write_bytecode = True

from PIL import ImageColor
import numpy as np
from assets import sprites_jojo as SJ
from engine import sprite

G = SJ.G
PAL = dict(SJ.JPAL, n='#242426', N='#101316', q='#484746',
           j='#9c2447', J='#581d33', x='#29282a', X='#141719',
           h='#252628', H='#0e1115', s='#e9bb91', S='#b98260',
           y='#e7bd55', Y='#917137', t='#45a895', r='#cd4b46')

# 帽脸总高九像素，肩宽约为脸宽的两倍；低帽檐保留承太郎的辨识度。
HEAD = '''
....nnnnnn...
..nqqnnnnyyn.
..nnnnnnnyYn.
.NNNNNNNNNNNn
..NNSSSSSSSS.
...NSskkSks..
...NSsssSsS..
....SSssSS...
.....SSSS....
'''
HEAD_LOW = SJ.edits(HEAD, (4, 4, 'NNNNNNNN'), (5, 5, 'SSSkSkS'))
HEAD_HURT = SJ.edits(HEAD, (5, 5, 'SSkkSkk'), (6, 7, 'SwkS'))
HEAD_SHOCK = SJ.edits(HEAD, (5, 5, 'SkWsSkW'), (11, 5, 'u'))
FIST = '.ss|ssS|.S.'.replace('|', '\n')
OPEN = '.s.s|sssS|.sS.'.replace('|', '\n')
POINT = '.ss....|sssssss|.SS....'.replace('|', '\n')
SHOE = '.hhhh.|hhhhhh|HHHHHH'.replace('|', '\n')
TOE = 'hh..|hhh.|hhhh|.HHH'.replace('|', '\n')


def arm(g, pts, hand=FIST, far=False, off=(0, 0)):
    SJ.arm(g, pts, 'nnNN' if far else 'qnnN', hand,
           hand_off=off, sep=None if far else 'k')


def torso(g, breath=0):
    g.poly([(18, 11), (23, 11), (24, 15), (17, 15)], 'S', left='s')
    g.poly([(14, 13), (25, 13), (29, 16), (26, 28), (14, 28), (10, 16)],
           'n', left='q', right='N')
    g.poly([(18, 14), (24, 14), (25, 18), (23, 27), (17, 27), (16, 18)],
           'j', left='J', right='J')
    g.limb((18, 18 + breath), (23, 18 + breath), 'J')
    g.limb((18, 24), (22, 25), 'J')
    g.poly([(14, 13), (18, 13), (17, 17), (14, 21), (12, 16)], 'n', left='q')
    g.poly([(24, 13), (27, 14), (28, 19), (25, 18)], 'q', right='N')
    for x, y in ((26, 14), (26, 15), (27, 16), (27, 17), (26, 18), (25, 19)):
        g.put(x, y, 'y' if y % 2 else 'Y')
    for x, y in ((12, 20), (13, 25), (26, 24)):
        g.put(x, y, 'y')
    g.limb((15, 28), (25, 28), 'H')
    for x in range(16, 26):
        g.put(x, 28, 'tyrY'[(x - 16) % 4])
    g.stamp('yy|yY'.replace('|', '\n'), 20, 28)


def coat(g, back=0, front=0, tail=None, ftail=None, hem=40):
    left = tail or (10 - back, hem)
    right = ftail or (28 + front, hem)
    g.poly([(12, 26), (16, 29), (16, hem - 1), left, (9, hem - 2)],
           'n', left='q', bottom='N')
    g.poly([(24, 28), (27, 26), right, (25, hem)], 'n', right='q', bottom='N')


def frame(legs=None, arm_n='pocket', arm_f='pocket', head=HEAD,
          dy=0, k=0, coat_args=None, breath=0):
    g = G(36, 52)
    near, far = legs or ([(17, 30), (15, 47), 'flat'],
                        [(23, 30), (24, 47), 'flat'])
    SJ.legs2(g, near, far, cols_n='qxxxX', cols_f='XxxXX', shoe=SHOE, shoe_toe=TOE)
    up = G(36, 52)
    coat(up, **(coat_args or {}))
    if arm_f == 'pocket':
        arm(up, [(27, 16), (29, 23), (26, 28)], hand=None, far=True)
    elif arm_f:
        arm(up, arm_f, far=True)
    torso(up, breath)
    up.stamp(head, 13, 3)
    if arm_n == 'pocket':
        arm(up, [(12, 16), (10, 23), (15, 28)], hand=None)
        up.limb((14, 27), (16, 27), 'N')
    elif arm_n:
        pts, hand, off = arm_n
        arm(up, pts, hand, off=off)
    # 头部保持刚性，前倾时不会把帽檐和五官剪切变形。
    if k:
        SJ.lean(up, k, 29, rigid=13)
    up.shift(0, dy)
    g.stamp(up.s(), 0, 0)
    if arm_n == 'pocket':
        for x, y, c in ((24, 30, 't'), (25, 31, 'y'), (26, 32, 'r'), (27, 33, 't')):
            g.put(x, y, c)
    return g.outline().s()


def seated(bob=0):
    g = G(40, 44)
    g.poly([(12, 24), (25, 26), (26, 39), (9, 39)], 'n', left='q', bottom='N')
    for hip, knee, ankle, cols in (((23, 27), (30, 29), (32, 39), 'XxxXX'),
                                   ((17, 28), (27, 31), (28, 39), 'qxxxX')):
        g.limb(hip, knee, cols, sep='k').limb(knee, ankle, cols)
        g.stamp(SHOE, ankle[0] - 2, 40, sep='k')
    up = G(40, 44)
    torso(up, bob)
    up.stamp(HEAD, 13, 3)
    arm(up, [(27, 16), (29, 21), (16, 23)], far=True)
    arm(up, [(12, 16), (10, 21), (24, 22)])
    up.shift(0, bob)
    g.stamp(up.s(), 0, 0)
    return g.outline().s()


def horizontal(swim=False, fi=0):
    g = G(68 if swim else 58, 28 if swim else 22)
    ground = 24 if swim else 19
    # 只旋转重画后的头部，横卧的躯干、屈膝和漂浮手臂分别绘制。
    head = HEAD if swim else HEAD_HURT
    g.stamp(SJ.rot_ccw(head), 1, ground - 13)
    g.poly([(10, ground - 8), (31, ground - 9), (35, ground), (10, ground)],
           'n', left='q', top='q', bottom='N')
    g.poly([(15, ground - 7), (29, ground - 7), (29, ground - 4), (15, ground - 4)], 'j')
    for x, y in ((13, ground - 8), (14, ground - 7), (16, ground - 7), (17, ground - 6)):
        g.put(x, y, 'y')
    g.limb((30, ground - 8), (30, ground - 1), 'H')
    for y in range(ground - 7, ground):
        g.put(30, y, 'tyrY'[y % 4])
    end = 61 if swim else 51
    g.limb((32, ground - 6), (43, ground - 10 + fi * 2), 'XxxXX')
    g.limb((43, ground - 10 + fi * 2), (end, ground - 4), 'XxxXX')
    g.limb((32, ground - 1), (end - 1, ground - 1 - fi), 'qxxxX', sep='k')
    for x, y in ((end, ground - 6), (end - 1, ground - 3 - fi)):
        g.stamp('hh|hh|hH|HH'.replace('|', '\n'), x, y, sep='k')
    if swim:
        arm(g, [(16, ground - 6), (23, 5 - fi), (34, 7 + fi)], far=True)
        arm(g, [(15, ground - 3), (21, ground + 1), (30, ground - 1)])
    else:
        arm(g, [(15, ground - 4), (21, ground - 2), (28, ground - 3)])
    return g.outline().s()


def actions():
    walk = []
    for near, far, bob in (
        ([(17, 30), (22, 47), 'flat'], [(23, 30), (12, 46), 'toe'], 0),
        ([(17, 29), (18, 47), 'flat'], [(23, 29), (22, 39), (20, 44), 'toe'], -1),
        ([(17, 30), (11, 46), 'toe'], [(23, 30), (26, 47), 'flat'], 0),
        ([(17, 29), (17, 39), (15, 44), 'toe'], [(23, 29), (23, 47), 'flat'], -1),
    ):
        walk.append(frame(legs=(near, far), dy=bob, coat_args=dict(back=2, front=1)))
    run = []
    for fi, (near, far) in enumerate((
        ([(17, 30), (23, 39), (27, 47), 'flat'], [(23, 30), (15, 39), (8, 39), 'toeb']),
        ([(17, 28), (18, 37), (16, 43), 'toe'], [(23, 28), (26, 37), (24, 42), 'toe']),
        ([(17, 30), (11, 38), (6, 39), 'toeb'], [(23, 30), (27, 40), (29, 47), 'flat']),
        ([(17, 28), (22, 37), (19, 43), 'toe'], [(23, 28), (21, 38), (19, 44), 'toe']),
    )):
        front = [(12, 16), (8, 22), (5, 25)] if fi < 2 else [(12, 16), (15, 23), (22, 20)]
        run.append(frame(legs=(near, far), arm_n=(front, FIST, (0, 0)),
                         arm_f=[(27, 16), (30, 23), (32, 20)] if fi < 2 else [(27, 16), (24, 23), (21, 25)],
                         k=.16, dy=-1 if fi % 2 else 0,
                         coat_args=dict(tail=(1, 36), ftail=(32, 38))))
    wide = ([(17, 30), (12, 47), 'flat'], [(23, 30), (27, 47), 'flat'])
    point = [frame(legs=wide, arm_n=([(12, 16), (20, 17), (28, 17)], POINT, (3, 0)),
                   coat_args=dict(back=2 + fi, front=2)) for fi in range(2)]
    pose = [frame(legs=wide, arm_n=([(12, 16), (7, 12), (21, 7)], FIST, (0, 0)),
                  arm_f=[(27, 16), (30, 23), (28, 28)], head=HEAD_LOW if fi else HEAD,
                  coat_args=dict(tail=(3 - fi, 39), front=2 + fi)) for fi in range(2)]
    return {
        'idle': [frame(), frame(breath=1, dy=1, coat_args=dict(hem=39))],
        'walk': walk, 'run': run, 'point': point, 'pose': pose,
        'sit': [seated(), seated(1)],
        'hurt': [frame(legs=wide, head=HEAD_HURT, k=-.18,
                       arm_n=([(12, 16), (15, 23), (21, 25)], FIST, (0, 0)),
                       arm_f=[(27, 16), (31, 21), (33, 25)], coat_args=dict(front=3))],
        'shock': [frame(head=HEAD_SHOCK, k=-.06,
                        arm_n=([(12, 16), (9, 23), (12, 27)], OPEN, (0, 0)),
                        arm_f=[(27, 16), (30, 22), (32, 25)])],
        'guard': [frame(legs=wide, head=HEAD_LOW,
                        arm_n=([(12, 16), (14, 22), (24, 14)], FIST, (0, 0)),
                        arm_f=[(27, 16), (27, 22), (17, 15)], coat_args=dict(back=2))],
        'dodge': [frame(legs=([(17, 30), (8, 46), 'toe'], [(23, 30), (22, 39), (21, 47), 'flat']),
                        arm_n=([(12, 16), (7, 21), (3, 24)], OPEN, (0, 0)),
                        arm_f=[(27, 16), (30, 20), (33, 17)], k=-.20,
                        coat_args=dict(tail=(1, 38), front=2))],
        'down': [horizontal()], 'float': [horizontal(True, fi) for fi in range(2)],
        'kick': [frame(legs=([(17, 30), (17, 47), 'flat'],
                             [(23, 30), (34, 25 + fi * 6), (49, 23 + fi * 11), None]),
                       arm_n=([(12, 16), (11, 23), (18, 21)], FIST, (0, 0)),
                       k=-.09, coat_args=dict(front=3)) for fi in range(2)],
    }


def apply():
    """冲突审计完成后显式替换成年形象，保留原动作契约与儿童形态。"""
    redrawn = actions()
    # 踢腿需要横向空间，重新使用同一个骨架而不截掉伸出的鞋尖。
    for fi in range(2):
        base = frame(legs=([(17, 30), (17, 47), 'flat'], [(23, 30), (30, 29), None]),
                     arm_n=([(12, 16), (11, 23), (18, 21)], FIST, (0, 0)), k=-.09,
                     coat_args=dict(front=3))
        g = G(62, 52)
        g.stamp(base, 0, 0)
        knee, ankle = (35, 24 + fi * 6), (55, 22 + fi * 11)
        g.limb((23, 30), knee, 'XxxXX', sep='k').limb(knee, ankle, 'qxxxX')
        g.stamp('hhh|hhH|hhH|HHH'.replace('|', '\n'), ankle[0], ankle[1] - 1, sep='k')
        redrawn['kick'][fi] = g.outline().s()
    names = []
    for act, frames in redrawn.items():
        name = 'jotaro.' + act
        old = sprite.get(name)
        if len(frames) != len(old.frames):
            raise ValueError(f'{name} 重画前后帧数不同')
        sprite.define(name, frames, pal=PAL, anchor=old.anchor, fps=old.fps,
                      desc='参考图重画成年承太郎：' + act)
        names.append(name)
    # 对话特写保持独立尺寸，仅同步帽子、大衣和内衫色，不套用全身的小头比例。
    colors = {ImageColor.getrgb(SJ.JPAL[k]): ImageColor.getrgb(PAL[k]) for k in SJ.JPAL if k in PAL}
    for name in sorted(sprite._REG):
        if not name.startswith('jotaro.portrait'):
            continue
        old = sprite.get(name)
        frames = []
        for im in old.frames:
            src = np.asarray(im)
            dst = src.copy()
            for before, after in colors.items():
                dst[np.all(src[:, :, :3] == before, axis=2), :3] = after
            from PIL import Image
            frames.append(Image.fromarray(dst, 'RGBA'))
        sprite.define(name, frames, anchor=old.anchor, fps=old.fps, desc=old.desc)
        names.append(name)
    return names
