# 第五部《黄金之风》主角团：乔鲁诺、布加拉提、阿帕基、米斯达、纳兰迦、福葛、特里休。
#   画法同第四部 / 第三部重画：手写头和躯干的字符稿，四肢按共用骨架画；配色照动画版设定。
from px import shade, rows
from rig import grid_part, chain, X, Y
from castlib import P_, make_build, main
from kit5 import b5, std, prop, line_prop, gun, guns_poses, stab_poses, pinstripe, dots, GUN_PAL, KNIFE


# ---------------------------------------------------------------- 乔鲁诺·乔巴拿（172 cm）：金发前三个卷、脑后长辫、粉紫色制服、胸口心形开口、瓢虫胸针
def giorno():
    pal = P_(F='#fff09a', L='#f6cc40', Y='#cc9428', y='#8a5c14', o='#7a4a10', e='#1f9a82',
             J='#e486d0', G='#f8c838', B='#1c5c82', x='#5c2264', q='#8c3684', j='#c85cb4', p='#8c3a90')
    head = '''
......YYYYYYYY....
....YYLLFFFFLLYY..
...YLLFFLLLLLLLLY.
..YLLLFFFyFFFyFFF.
..YLLLFoFyFoFyFoF.
..yLLLYFYyYFYyYFY.
..yYLLssbbbssbbbs.
.yYYLsswesssweSs..
.yYLLdswesssweSs..
..yYddsssssssss...
...yddssssmmmss...
.....dddsssssd....
.......ddddsd.....
'''
    torso = '''
qjGGjGGj
qGssGssG
qGsssssG
qjGsssGj
qBjGsGjB
qjjjGjjj
qjjjjJjj
qxxxGxxx
qqjjjjjj
'''
    braid = grid_part('''
..YL
.YLy
.yY.
YLy.
yLLy
.yY.
.YL.
..y.
''', -1, 9)
    B = b5(172, head, pal, torso, '#c85cb4', '#8c3a90', '#2a2e70', back=braid, cuff='#f8c838',
           coat=dict(len=3, col='#c85cb4', flare=1, open=(0, 0), trim='#8c3684'))

    def extra(B_, P):
        A = B_.arm_len
        stance = dict(lN=(-2, 0), lF=(1, 0))
        return {
            # 招牌站姿：一手抚胸、一手后摆、上身后仰
            'pose': ([dict(stance, lean=-1, aF_front=True, aF=((3, -3), (0, 0)), aN=((-3, -1), (-5, 1))),
                      dict(stance, lean=-1, dy=-1, aF_front=True, aF=((3, -3), (0, 0)), aN=((-3, 0), (-5, 2)))], 3, 'loop'),
            # “我有一个梦想”：指向斜上方
            'dream': ([dict(stance, aF=((3, 1), (A + 1, 4)), aN=((-2, -2), (-1, -A + 2))),
                       dict(stance, aF=((3, 2), (A + 1, 5)), aN=((-2, -2), (-1, -A + 2)), head='t')], 4, 'loop'),
        }
    return std(B, ['idle', 'walk', 'run', 'pose', 'dream', 'attack', 'hurt', 'guard', 'down'], extra)


# ---------------------------------------------------------------- 布鲁诺·布加拉提（178 cm）：齐刘海黑色波波头、两个金发夹、蓝眼、白西装黑水滴纹、金拉链头
def bucciarati():
    pal = P_(K='#241f38', k='#100d1c', h='#4c4680', G='#f4bc3c', g='#a86c18', e='#2c5cd8',
             Z='#e4a82c', n='#3a2436', T='#a4808c', c='#2c2a38', x='#a29eac', j='#ebe7de', q='#bcb6bc')
    head = '''
......kkkkkkk.....
....kkKKKKKKKkk...
...kKGGKKhhKKKKk..
..kKGggKKKKKhGGk..
..kKKKKhhKKKKggKk.
.kKKKKKKKKKKKKKKKk
.kKKkkkkkkkkkkkkk.
.kKKksbbbbssbbbsk.
.kKKsswesssweSsKk.
.kKKdswesssweSsKk.
.kKKddssssssssdKk.
.kKKkddsssmmmsskk.
..kKk..ddssssd.k..
..kk.....dddd.....
'''
    torso = '''
qjZnnnZj
qjZnTnZj
qcjnnnjc
qjjTnTjj
qcjjnjcj
qjjcjjjj
qxxxxZxx
qjjjjjcj
qjcjjjjj
'''
    dot = dots('#34303e', 2, 3, 7, 3)

    def zip_fn(cv, B_, P, ctx):
        # 钢链手指：出拳时拳前拉开的一道拉链
        if P.get('item') != 'zip':
            return
        h = ctx.get('handF')
        if not h:
            return
        for i in range(9):
            x = h[0] + 2 + i
            cv.put(X(x), Y(h[1] + (1 if i % 2 else 0)), '#f4bc3c')
            cv.put(X(x), Y(h[1] - (1 if i % 2 == 0 else 0)), '#a86c18')
        cv.rect(X(h[0] + 11), Y(h[1] + 1), X(h[0] + 12), Y(h[1] - 1), '#f4bc3c')
    B = b5(178, head, pal, torso, '#ebe7de', '#e2ded6', '#36323e', chin=13, front=zip_fn, pat_leg=dot, pat_arm=dot,
           coat=dict(len=2, col='#ebe7de', flare=0, open=(0, 0)))

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([dict(lean=-1, aF_front=True, aF=((3, -1), (1, 5)), aN=((-3, -2), (0, -A + 3)), lN=(-2, 0), lF=(1, 0)),
                      dict(lean=-1, dy=-1, aF_front=True, aF=((3, -1), (1, 4)), aN=((-3, -2), (0, -A + 3)), lN=(-2, 0), lF=(1, 0))], 3, 'loop'),
            # “阿里阿里阿里……再见了”：两指一挥
            'arrive': ([dict(aF_front=True, aF=((5, -3), (7, 2)), aN=((-2, -2), (-1, -A + 2))),
                        dict(aF_front=True, aF=((6, -1), (10, 4)), aN=((-2, -2), (-1, -A + 2)), head='t')], 5, 'loop'),
            'attack': ([dict(lean=-1, aF=((-1, -1), (1, 0)), aN=((-1, -2), (1, -A + 2)), fistF=3),
                        dict(lean=1, head='r', aF=(A + 2, 0), fistF=3, aN=((-2, -2), (-3, -1)), lF=(1, 0)),
                        dict(lean=1, head='r', aF=(A + 2, 0), fistF=3, aN=((-2, -2), (-3, -1)), lF=(1, 0), item='zip')], 8, 'oneshot'),
        }
    return std(B, ['idle', 'walk', 'run', 'pose', 'arrive', 'attack', 'hurt', 'guard', 'down'], extra)


# ---------------------------------------------------------------- 雷欧·阿帕基（188 cm）：银紫长直发、深紫小帽、紫唇、紫金双色瞳、深蓝长大衣胸前交叉绑带、金色 A 字带扣
def abbacchio():
    pal = P_(W='#e8e0f4', V='#c0b2d8', v='#8c80ac', P='#34264e', p='#5c448a', e='#6c2480', z='#e8ac30',
             m='#7c3290', s='#f4cdb4', d='#c8967c', x='#ac54cc', y='#4c2a68', G='#f4b838', k='#6c4810',
             j='#2e2a56', q='#1c1a3a')
    head = '''
......PPPPPPP.....
....PPppppppPPP...
...WPPPPPPPPPPPW..
..WWWWWWWWWWWWWW..
.WWVWWWVWWWWVWWWW.
.WVWWVWWWWWWWVWWW.
.WVWsssbbbssbbbWW.
.WVWssswesssweSVW.
.WVWdsswzssswzSVW.
.WVWddsssssssssVW.
.WVWvdsssmmmssvVW.
.WVWv.ddsssssd.VW.
.WVWv...ddddd..VW.
.WVWv..........VW.
.WVv...........vW.
..Wv............v.
'''
    torso = '''
qjjsssjjj
qjjxsxjjj
qjjsxsjjj
qjjxsxjjj
qjjjxsjjj
qjjjsjjjj
qjjjjjjjj
qyyyGGGyy
qyyyGkGyy
qjjjGGGjj
'''
    hair = grid_part('''
VWWVv
WVWWv
VWWVv
.WVv.
.Wv..
..v..
''', 0, 12)
    B = b5(188, head, pal, torso, '#2e2a56', '#322c52', '#4a4282', back=hair, shut=('z',), skin='#f4cdb4',
           coat=dict(len=7, col='#2e2a56', flare=2, open=(0, 2), trim='#4c4490'), cuff='#4c4490')

    def extra(B_, P):
        A = B_.arm_len
        return {
            # 抱臂冷眼
            'pose': ([dict(aN=((-1, -3), (4, -3)), aF=((1, -4), (-4, -3)), aF_front=True, lN=(-2, 0), lF=(2, 0)),
                      dict(aN=((-1, -3), (4, -3)), aF=((1, -4), (-4, -3)), aF_front=True, lN=(-2, 0), lF=(2, 0), dy=-1, head='t')], 2, 'loop'),
            # 忧郁蓝调“回放”：抬手比划时间
            'rewind': ([dict(aF_front=True, aF=((6, -3), (9, 0)), aN=((-2, -2), (-1, -A + 2))),
                        dict(aF_front=True, aF=((6, -1), (9, 4)), aN=((-2, -2), (-1, -A + 2)), head='t'),
                        dict(aF_front=True, aF=((6, 0), (7, 8)), aN=((-2, -2), (-1, -A + 2)))], 4, 'loop'),
            'attack': P['kick'],
        }
    return std(B, ['idle', 'walk', 'run', 'pose', 'rewind', 'attack', 'hurt', 'guard', 'down'], extra)


# ---------------------------------------------------------------- 盖多·米斯达（179 cm）：红底白菱格帽（蓝箭头）、蓝色菱格短上衣露腰、虎纹裤、左轮
def mista():
    pal = P_(R='#c23a2c', r='#7a1c1e', T='#f4eee0', B='#2c70cc', e='#22162a', s='#e9ae7e', d='#ba7a52',
             y='#c83434', Z='#3a78c8', Y='#dce0ea', p='#a83a2c', j='#2668b8', q='#184680')
    head = '''
......rrrrrrr.....
....rrRRTRRRTrr...
...rRRTRTRTRTRRr..
..rRRTRRRTRRRTRRr.
..rRTRTRRBBBRTRTr.
.rRTRRRTRBBBTRRRTr
.rRRTRTRBBBBBRTRRr
.rRRRTRRRBBBRRTRr.
.rTTTTTTTTBTTTTTTr
.rRrsssbbbssbbbsT.
.rRrssswesssweSsT.
.rRrddswesssweSsT.
.rTrddsssssssss...
..TT.ddssssmmss...
.....ddddsssd.....
'''
    torso = '''
qTjjTjjT
qjTTjTTj
qjTTjTTj
qTjjTjjT
qjjjjjjj
dsssssss
dssdssds
yZZyyYyy
qppppppp
'''
    lattice = lambda k, i, n: '#f4eee0' if (k + i) % 4 == 0 else None
    tiger = lambda k, i, n: '#2c141c' if (k % 3 == 2 and i > 0) else None
    gunup = prop('gunup', '''
G.
Gg
Gg
KG
K.
''', 0, -4, GUN_PAL)
    B = b5(179, head, pal, torso, '#2668b8', '#c04a32', '#8c2420', chin=14, skin='#e9ae7e', pat_arm=lattice,
           pat_leg=tiger, boot=('#2a2434', 2), front=chain(gun(), gunup))

    def extra(B_, P):
        A = B_.arm_len
        return {
            # 举枪贴脸
            'pose': ([dict(lean=-1, aF_front=True, aF=((5, -4), (7, 1)), aN=((-3, -2), (0, -A + 3)), item='gunup', lN=(-3, 0), lF=(2, 0)),
                      dict(lean=-1, dy=-1, aF_front=True, aF=((5, -4), (7, 2)), aN=((-3, -2), (0, -A + 3)), item='gunup', lN=(-3, 0), lF=(2, 0), head='t')], 3, 'loop'),
            'attack': guns_poses(B_, P),
        }
    return std(B, ['idle', 'walk', 'run', 'pose', 'attack', 'hurt', 'guard', 'down'], extra)


# ---------------------------------------------------------------- 纳兰迦·吉尔卡（164 cm）：黑乱发、橙头巾、紫眼、黑紫背心、橙色格子围裙裤、小刀
def narancia():
    pal = P_(K='#2e2838', k='#141018', O='#fa9430', o='#c25a18', e='#7c3ccc', s='#f4bc8c', d='#c8825c',
             y='#e4781c', j='#33244a', q='#201634')
    head = '''
...k...kk..k......
..kKk.kKKkkKk.....
...kKKKKKKKKKKk...
..OOOOOOOOOOOOOO..
.OooooooooooooooO.
OOoKKKKKKKKKKKKKk.
Ok.kKKsKKsKKsKKKk.
.kKKkssbbbssbbbKk.
.kKKksswesssweSsk.
..kKkdswesssweSk..
..kkkddsssssssk...
...kkddsssmmss....
.....dddssssd.....
.......dddd.......
'''
    torso = '''
sjsssjs
sjjsjjs
qjjjjjj
qjjjjjj
qjjkjjj
qsssssd
yyyyyyy
qOOOOOO
'''
    pal['k'] = '#141018'
    B = b5(164, head, pal, torso, '#33244a', '#3c2e74', '#56428e', chin=13, skin='#f4bc8c', sleeve='#f4bc8c', wrist='#fa9430',
           arm_w=2, skirt=dict(len=3, col='#f6a830', flare=1, pleat=3, trim='#c25a18'),
           front=prop('knife', KNIFE, 0, -2, dict(G='#e4e8f4', g='#8c92a8', k='#3a2418')))

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([dict(aF_front=True, aF=((6, -2), (8, 3)), aN=((-3, -1), (-4, 1)), item='knife', head='t', lN=(-3, 0), lF=(2, 0)),
                      dict(dy=-1, aF_front=True, aF=((6, -1), (9, 5)), aN=((-3, 0), (-4, 2)), item='knife', head='r', lN=(-3, 0), lF=(2, 0))], 4, 'loop'),
            'cheer': ([dict(aF_front=True, aF=((6, 2), (8, A + 5)), aN=((-4, 2), (-6, A + 5)), head='t'),
                       dict(dy=1, aF_front=True, aF=((6, 3), (9, A + 4)), aN=((-4, 3), (-7, A + 4)), lN=(0, 1), lF=(0, 1), head='r')], 5, 'loop'),
            'attack': stab_poses(B_, P),
        }
    return std(B, ['idle', 'walk', 'run', 'pose', 'cheer', 'attack', 'hurt', 'guard', 'down'], extra)


# ---------------------------------------------------------------- 潘纳科达·福葛（178 cm）：橘金色卷发、草莓耳环、浅绿破洞西装、深蓝领带
def fugo():
    pal = P_(F='#ffd878', L='#f2ae42', Y='#c87e2a', y='#8a5016', e='#703cc4', x='#dc2c40', n='#586e2c', Z='#e8c048',
             k='#243276', o='#eab492', j='#abc65a', q='#78923c')
    head = '''
.......YYYY.......
....YYYLLLLYYY....
...YLFFLLLLLLLYY..
..YLFLLYLLFFLLLLY.
..YLLLYLLFLLYLLLY.
.YLLYLLYsYLLsYLLY.
.YLYLssbbbssbbbY..
YLLYssswesssweSsY.
.YLYddswesssweSs..
.yYyxddsssssssd...
..yyxddsssmmss....
.....dddsssssd....
.......dddd.......
'''
    torso = '''
qjjskssj
qjjskkjj
qojjkxjo
qjjjkkjj
qjojxkoj
qjsjkjsj
qjjjjjjj
qnnnZnnn
qjojjjoj
'''
    holes = lambda k, i, n: '#eab492' if (k in (2, 3, 8) and i == 1) else None
    fork = prop('fork', '''
...GG
gGGg.
...GG
''', 1, -1, dict(G='#e4e8f4', g='#8c92a8'))
    B = b5(178, head, pal, torso, '#abc65a', '#9eba50', '#2c4e96', front=fork, pat_leg=holes,
           pat_arm=lambda k, i, n: '#eab492' if (k == 3 and i == 1) else None,
           coat=dict(len=2, col='#abc65a', flare=1, open=(0, 0)))

    def extra(B_, P):
        A = B_.arm_len
        return {
            # 整理领带
            'pose': ([dict(aF_front=True, aF=((3, -4), (0, -1)), aN=((-3, -2), (0, -A + 2))),
                      dict(aF_front=True, aF=((3, -4), (0, 0)), aN=((-3, -2), (0, -A + 2)), head='t')], 3, 'loop'),
            # 暴怒
            'rage': ([dict(head='r', lean=2, aF=((3, 0), (6, 2)), aN=((-3, 0), (-5, 3)), lN=(-3, 0), lF=(3, 0), drop=1),
                      dict(head='r', lean=2, dy=1, aF=((3, 1), (5, 5)), aN=((-3, -1), (-6, 0)), lN=(-3, 0), lF=(3, 0), drop=1)], 8, 'loop'),
            'attack': stab_poses(B_, P, 'fork'),
        }
    return std(B, ['idle', 'walk', 'run', 'pose', 'rage', 'attack', 'hurt', 'guard', 'down'], extra)


# ---------------------------------------------------------------- 特莉休·乌娜（163 cm）：粉色卷短发、绿眼、黑色抹胸和斜带、粉黄格纹不对称短裙、棕靴
def trish():
    pal = P_(F='#ffa0c4', P='#f06aa0', r='#b63a70', e='#2a9e56', m='#d23e6c', p='#f29a96', s='#fcd2b2', d='#dc9c80',
             K='#2e1e40', x='#ecbc40', Q='#e25aa2', j='#2e1e40', q='#1c1028')
    head = '''
......rrrrr.......
....rrPPPPPrr.....
...rPPFFFFPPPrr...
..rPPPrrrrPPPPPr..
..rPPrFFFPrPPPPPr.
.rPPPrFrrPrPPrPPr.
.rPPPPrPPrssssPPr.
.rPPPssbbbssbbbPr.
rPPrssswesssweSsr.
rPrrddswesssweSs..
.rr.ddsssssssps...
..rr.ddssmmmss....
.....ddssssd......
.......dddd.......
'''
    torso = '''
ssKKKss
sssKsss
dKKsKKs
dKKKKKs
dssssKs
dsssKss
xxxKxxx
qQQQQQQ
'''

    def skirt(cv, B_, P, ctx):
        # 不对称短裙：后长前短，粉底配黄片，黑色格线
        x0, x1 = -B_.tw // 2 + ctx['bx'] - 1, -B_.tw // 2 + ctx['bx'] + B_.tw
        for k in range(6):
            yy = B_.LH - 1 - k + ctx['by']
            right = x1 if k < 3 else (x0 + 4 if k < 5 else x0 + 2)
            for x in range(x0, right + 1):
                c = '#f0c444' if x - x0 >= 5 else '#e25aa2'
                if k == 1 or (x - x0) % 3 == 2:
                    c = '#3a1c40'
                if x == x0:
                    c = '#9c3474'
                if k < B_.LH - 3:
                    cv.put(X(x), Y(yy), c)
    B = b5(163, head, pal, torso, '#2e1e40', '#fcd2b2', '#6a3418', chin=13, skin='#fcd2b2', sleeve='#fcd2b2', arm_w=2,
           bare=dict(top=0, skin='#fcd2b2'), boot=('#8c4e2c', 3), mid=skirt)

    def extra(B_, P):
        A = B_.arm_len
        return {
            # 叉腰撩头发
            'pose': ([dict(aN=((-3, -2), (0, -A + 2)), aF_front=True, aF=((6, -2), (7, 3)), lN=(-1, 0), lF=(2, 0), lean=-1),
                      dict(aN=((-3, -2), (0, -A + 2)), aF_front=True, aF=((6, -1), (8, 5)), lN=(-1, 0), lF=(2, 0), lean=-1, head='t')], 3, 'loop'),
            'cry': P['cry'],
        }
    return std(B, ['idle', 'walk', 'run', 'pose', 'cry', 'attack', 'hurt', 'guard', 'down'], extra)


CAST = {
    'giorno': ('乔鲁诺', giorno),
    'bucciarati': ('布加拉提', bucciarati),
    'abbacchio': ('阿帕基', abbacchio),
    'mista': ('米斯达', mista),
    'narancia': ('纳兰迦', narancia),
    'fugo': ('福葛', fugo),
    'trish': ('特莉休', trish),
}
HEIGHTS = {'giorno': 172, 'bucciarati': 178, 'abbacchio': 188, 'mista': 179, 'narancia': 164, 'fugo': 178, 'trish': 163}
build = make_build(CAST)

if __name__ == '__main__':
    import sys
    main(CAST, build, sys.argv)
