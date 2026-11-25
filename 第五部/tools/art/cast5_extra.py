# 第五部序章、第1章补画的角色：泪眼卢卡、机场警官、两个路人。画法同主角团（kit5 / rig）。
from px import shade
from rig import grid_part, chain
from castlib import P_, make_build, main
from kit5 import b5, std, prop, stab_poses

HANKY_PAL = dict(W='#f4f6fc', q='#b4bcd4')


# ---------------------------------------------------------------- 泪眼卢卡：红棕色尖刘海、总拿手帕擦眼睛、深蓝低领背心、肩上刺青、铲子
def luca():
    pal = P_(H='#a4582c', h='#c87c40', k='#542a14', e='#3c6cc4', s='#e8ac7c', d='#b87c54', t='#8cc4fc',
             j='#27386c', q='#17224a', y='#3a2a1c', Y='#d8b040', p='#3c3448')
    head = '''
......kkkkk.......
....kkHHHhHHkk....
...kHHhhHHhHHHkk..
..kHHhHHHHHHHHHHk.
..kHHHHkHHHkHHHHk.
.kHHHkksHHksHHkHk.
.kHHksssksssskkk..
.kHksssbbbssbbbs..
..kkssswesssweSs..
...kddswesssweS...
....ddsstssssst...
....ddssssmmss....
.....dddsssssd....
.......dddd.......
'''
    torso = '''
sjsssssj
sjjsssjj
qjjjsjjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
yyyyYyyy
qppppppp
'''
    hanky = prop('hanky', '''
.WW.
WWqW
WqWq
.q..
''', -2, -2, HANKY_PAL)

    def shovel(cv, B, P, ctx):
        from rig import X, Y
        it = P.get('item')
        h = ctx.get('handF')
        if not h or it not in ('shovel_up', 'shovel_hit'):
            return
        hx, hy = h
        tip = (hx - 5, hy + 11) if it == 'shovel_up' else (hx + 11, hy - 6)
        cv.line(X(hx), Y(hy), X(tip[0]), Y(tip[1]), '#8c5c2c')
        cv.line(X(hx) + 1, Y(hy), X(tip[0]) + 1, Y(tip[1]), '#4c2c14')
        cv.rect(X(tip[0]) - 2, Y(tip[1]) - 2, X(tip[0]) + 3, Y(tip[1]) + 2, '#a8b0c0')
        cv.hline(X(tip[0]) - 2, X(tip[0]) + 3, Y(tip[1]) - 2, '#e4e8f0')
        cv.hline(X(tip[0]) - 2, X(tip[0]) + 3, Y(tip[1]) + 2, '#6c7488')
    tattoo = lambda k, i, n: '#58a454' if (k in (1, 2) and i >= 1) else None

    def shovel_behind(cv, B, P, ctx):
        # 举过头顶那一帧画在头后面（手的位置按姿势推）
        if P.get('item') != 'shovel_up':
            return
        sh, spec = ctx['shF'], P['aF'][-1]
        shovel(cv, B, P, dict(ctx, handF=(sh[0] + spec[0], sh[1] + spec[1])))

    def shovel_front(cv, B, P, ctx):
        if P.get('item') == 'shovel_hit':
            shovel(cv, B, P, ctx)
    B = b5(178, head, pal, torso, '#27386c', '#3c3448', '#2a2028', chin=13, skin='#e8ac7c', sleeve='#e8ac7c',
           pat_arm=tattoo, back=shovel_behind, front=chain(hanky, shovel_front))

    def extra(B_, P):
        A = B_.arm_len
        wipe = dict(aF_front=True, aF=((5, -4), (4, 3)), aN=((-2, -2), (-1, -A + 2)), item='hanky')
        return {
            'cry': ([dict(wipe, head='h'), dict(wipe, head='t', aF=((5, -4), (3, 3)))], 4, 'loop'),
            'attack': ([dict(lean=-2, head='r', aF=((-1, 1), (-3, 4)), aN=((-2, -2), (1, -1)), item='shovel_up', lN=(-2, 0), lF=(2, 0)),
                        dict(lean=2, bx=1, head='r', aF=(A + 2, -1), aN=((-2, -2), (-3, -1)), item='shovel_hit', lN=(-3, 0),
                             lF=((2, -4), (3, 0)), drop=1),
                        dict(lean=1, aF=(A + 1, -3), aN=((-2, -2), (-3, -2)), item='shovel_hit', lF=(2, 0))], 9, 'oneshot'),
        }
    return std(B, ['idle', 'walk', 'talk', 'cry', 'attack', 'hurt', 'down'], extra)


# ---------------------------------------------------------------- 机场警官：深蓝大檐帽、浅蓝衬衫、黑皮带
def police():
    pal = P_(N='#232c58', n='#141a38', G='#f0c040', H='#3a2820', e='#3c2c20', s='#e4a878', d='#b47850',
             j='#8cb4e4', J='#b8d4f4', q='#5c80b4', k='#1c2446', y='#201c24', Y='#e0c050', p='#232c58')
    head = '''
.......nnnnnn.....
....nnNNNNNNNnn...
...nNNNNNNGGNNNn..
..nNNNNNNNGGNNNNn.
..nnnnnnnnnnnnnnnn
..HHsssssssssssn..
..HHsssbbbssbbbs..
..HHssswesssweSs..
...Hddswesssweds..
....ddsssssssss...
....ddsssHHHHs....
.....dddsssssd....
.......dddd.......
'''
    torso = '''
qJjkkjJj
qjjjkjjj
qjGjkjjj
qjjjkjjj
qjjjkjjj
qjjjkjjj
qjjjjjjj
yyyyYyyy
qppppppp
'''
    B = b5(178, head, pal, torso, '#8cb4e4', '#232c58', '#17141e', skin='#e4a878', cuff='#5c80b4')

    def extra(B_, P):
        A = B_.arm_len
        return {'cmd': ([dict(aF_front=True, aF=((6, -2), (9, 0)), aN=((-2, -2), (-1, -A + 2))),
                         dict(aF_front=True, aF=((6, -1), (9, 2)), aN=((-2, -2), (-1, -A + 2)), head='t')], 5, 'loop')}
    return std(B, ['idle', 'walk', 'talk', 'cmd', 'shock', 'hurt', 'down'], extra)


# ---------------------------------------------------------------- 路人（男）：棕色短发、米色夹克、深色长裤
def passer_m():
    pal = P_(H='#6c4428', h='#8c5c34', k='#3c2414', e='#34241c', s='#eab08a', d='#bc825c',
             j='#c8a874', q='#94784c', t='#e8e4dc', y='#4c3424', p='#44485c')
    head = '''
......kkkkk.......
....kkHHhhHHkk....
...kHHhhHHHHHHk...
..kHHHHHHHHHHHHk..
..kHHHHsssssssHk..
..kHHssssssssss...
..kHsssbbbssbbbs..
...kssswesssweSs..
....ddswesssweS...
....ddsssssssss...
....ddssssmmss....
.....dddsssssd....
.......dddd.......
'''
    torso = '''
qjjtttjj
qjjttjjj
qjjtjjjj
qjjtjjjj
qjjtjjjj
qjjtjjjj
qjjjjjjj
yyyyyyyy
qppppppp
'''
    B = b5(175, head, pal, torso, '#c8a874', '#44485c', '#4c2c1c', TH=9, LH=8, skin='#eab08a',
           coat=dict(len=2, col='#c8a874', flare=1, open=(0, 0)))
    return std(B, ['idle', 'walk', 'talk', 'shock', 'hurt', 'down'])


# ---------------------------------------------------------------- 路人（女）：深棕长发、珊瑚色连衣裙
def passer_f():
    pal = P_(H='#5c3420', h='#8c5430', k='#2c180c', e='#34402c', m='#c8505c', s='#f4c4a0', d='#cc906c',
             j='#e4706c', q='#ac4c4c', t='#fce8dc', y='#fcf0e4', p='#e4706c')
    head = '''
......kkkkk.......
....kkHHhhHHkk....
...kHHhhHHHHHHk...
..kHHHHHHHhHHHHk..
.kHHHHHssHsssHHHk.
.kHHHssssssssssHk.
.kHHsssbbbssbbbsk.
.kHHssswesssweSsk.
.kHHddswesssweSk..
.kHkddsssssssskk..
.kHHkddsssmmsk....
..kHk.dddsssd.....
..kk....ddd.......
'''
    torso = '''
sjjttjjs
qjjjtjjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
yyyyyyyy
qjjjjjjj
qjjjjjjj
'''
    B = b5(164, head, pal, torso, '#e4706c', '#f4c4a0', '#8c3c34', TH=8, LH=7, skin='#f4c4a0', sleeve='#f4c4a0', arm_w=2,
           skirt=dict(len=4, col='#e4706c', flare=2, pleat=3, trim='#ac4c4c'))
    return std(B, ['idle', 'walk', 'talk', 'shock', 'hurt', 'down'])


CAST = {'luca': ('泪眼卢卡', luca), 'police': ('警官', police), 'passer_m': ('路人', passer_m), 'passer_f': ('路人', passer_f)}
HEIGHTS = {'luca': 178, 'police': 178, 'passer_m': 175, 'passer_f': 164}
build = make_build(CAST)

if __name__ == '__main__':
    import sys
    main(CAST, build, sys.argv)
