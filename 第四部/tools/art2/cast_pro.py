# 序章人物（重画）：东方仗助、空条承太郎（第四部）、广濑康一、学长 A/B、朋子、良平、安杰罗、劫匪、店员、女生 A/B、搭讪男、小学生。
#   头照 TV 动画第四部的设定画（JoJo Wiki 的 Infobox_Anime 图）；身高照 第四部/docs/比例标准.md。
#   每个函数返回 (Body, 姿势表, 动作清单)；动作名、帧数、fps 和旧图集保持一致（剧情脚本和招式表按名字用）。
from px import shade
from rig import Body, Sheet, draw, poses, variants, grid_part, chain, X, Y

SKIN, SKIN_D = '#f6c49a', '#d8946c'
BASE = {'s': SKIN, 'd': SKIN_D, 'w': '#ffffff', 'm': '#a04e44', 'b': '#1a1438'}


def P_(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


def H(txt):
    """头的字符稿里用大写 S 标“这格本来是皮肤、留着对齐用”，这里换回 s"""
    return txt.replace('S', 's')


# ---------------------------------------------------------------- 东方仗助（180 cm；飞机头另算）
def josuke():
    pal = P_(h='#2e2660', H='#4c40a0', L='#8a7ee0', k='#1a1438', e='#2a48b8',
             j='#362c84', J='#5448b8', q='#221a58', p='#e0507a', g='#ffd040')
    head = H('''
.........HHHHHH..
......HHLLLLLLHH.
....hHHHHHHHHHHHH
...hhhhhhhhhhhhhH
..hhhhhhhhhhhhhhk
..hhhhhhkkkkkkkk.
.hhhhhkssssssss..
.hhhhkssbbssbbs..
.hhhhsswesssweS..
.khhdsswesssweS..
..kkdssssssssss..
...kdsssssmmss...
....ddsssssss....
......dddss......
''')
    torso = '''
qjjppjjj
qjgppjgj
qjjjpjjj
qjjjjgjj
qjjjjjjj
qjjjjgjj
qjjjjjjj
qjjjjgjj
qjjjjjjj
'''
    B = Body(variants(head, pal), TH=9, LH=9, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#362c84', pants='#2a2262',
             shoe='#6a4a9a', hax=9, coat=dict(len=3, col='#362c84', line=1))
    P = poses(B)
    A = B.arm_len
    # 招牌动作：抬手拢飞机头
    P['pose'] = ([dict(aN=((-2, -2), (-1, -A + 2)), aF=((3, 2), (2, 7)), lean=-1),
                  dict(aN=((-2, -2), (-1, -A + 2)), aF=((3, 2), (3, 8)), lean=-1, head='t')], 3, 'oneshot')
    return B, P, ['idle', 'walk', 'run', 'point', 'pose', 'shock', 'hurt', 'dodge', 'guard', 'kick', 'sit', 'down']


# ---------------------------------------------------------------- 空条承太郎（第四部，195 cm）：白帽白长外套、黑内衬
def jotaro4():
    pal = P_(W='#f4f4ec', V='#c4c8c8', k='#1c1826', K='#34304a', g='#ffd040', G='#c89420', e='#2a9a8a',
             c='#c4c8c8', n='#24202e', p='#7a5ac0', y='#b08a30', q='#dcdcd4')
    head = H('''
.....WWWWWWWW...
...WWWWWWWWWWW..
..WWWWWWWWWgGWW.
.kkWWWWWWWWggWW.
kkkKWWWWWWWWWWWV
kkkkVVVVVVVVVVVV
kkkkkbbbssbbbs..
.kkksswesssweS..
.kkkdswesssweS..
..kkdsssssssss..
..kkdssssmmss...
...kddsssssss...
.....dddsss.....
''')
    torso = '''
cWWnnnWWW
cWWnnnWgW
cWWnpnWWW
cWWnnnWWW
cWWnpnWWW
cWWnnnWWW
cWWnnnWWW
cWWyyyWWW
cWWqqqWWW
cWWqqqWWW
'''
    B = Body(variants(head, pal), TH=10, LH=11, tw=9, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#f4f4ec', pants='#e4e4dc',
             shoe='#8a8c98', hax=9, coat=dict(len=6, col='#f4f4ec', open=(-2, 0), trim='#c4c8c8'), cuff='#7a5ac0')
    P = poses(B)
    A = B.arm_len
    # 招牌动作：压帽檐
    P['pose'] = ([dict(aN=((-2, -2), (-1, -A + 2)), aF=((3, 3), (4, 8))),
                  dict(aN=((-2, -2), (-1, -A + 2)), aF=((3, 3), (4, 7)), hy=-1)], 3, 'oneshot')
    return B, P, ['idle', 'walk', 'run', 'point', 'pose', 'shock', 'hurt', 'dodge', 'guard', 'kick', 'down']


# ---------------------------------------------------------------- 广濑康一（157 cm；前期：灰色刺猬头、绿色校服）
def koichi():
    pal = P_(G='#d4d8e6', g='#9a9eb8', k='#6a6e88', e='#2e5cb0',
             j='#2f5a40', J='#3f7654', q='#1e3c2a', y='#ffd040')
    head = H('''
....G..G...G...
...GG.GG..GG.G.
..gGGGGGgGGGGG.
.gGGGGGGGGGGGGg
.gGGGGGGGGGGGg.
gGGGGGGggggGGg.
gGGGgsssssssg..
gGGgssssssssss.
.gGgswesssweSs.
.kgsswesssweSs.
..kdssssssssss.
...dsssssmmss..
....ddsssss....
......dds......
''')
    torso = '''
qjjjjjj
qjjjyjj
qjjjjjj
qjjjyjj
qjjjjjj
qjjjyjj
qjjjjjj
'''
    B = Body(variants(head, pal), TH=7, LH=6, tw=7, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#2f5a40', pants='#264a34',
             shoe='#7a4e2c', hax=8)
    P = poses(B)
    return B, P, ['idle', 'walk', 'bow', 'cmd', 'hurt', 'down', 'dodge', 'guard']


# ---------------------------------------------------------------- 不良学长 A / B（高三，约 178 cm）
GAKURAN = '''
qjjjjjjj
qjjjjgjj
qjjjjjjj
qjjjjgjj
qjjjjjjj
qjjjjgjj
qjjjjjjj
qjjjjgjj
qjjjjjjj
'''


def thug_a():
    # 橙棕色飞机头（比仗助的尖、往前戳）、黑色长校服、一脸横
    pal = P_(o='#9a5226', O='#d08a44', k='#52280e', e='#3a2a1a', j='#2c2c3c', q='#18181f', g='#c8b060')
    head = H('''
.........oooooo.
......ooOOOOOOoo
....ooooooooooo.
...ooooooooooo..
..oooooookkkkk..
..oooksssssss...
.oooksbbbsbbbs..
.oookssweSswes..
.okkdssweSswes..
..kkdssssssss...
...kdsssmmmss...
....ddssssss....
......ddss......
''')
    B = Body(variants(head, pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=GAKURAN, top='#2c2c3c', pants='#22222e',
             shoe='#3a2a2a', hax=8, coat=dict(len=4, col='#2c2c3c', line=1))
    P = poses(B)
    return B, P, ['idle', 'walk', 'hurt', 'down', 'dodge', 'guard']


def thug_b():
    # 寸头、墨镜、藏青短校服敞着怀露白 T 恤
    pal = P_(k='#2a2630', K='#3e3a48', G='#16141c', l='#6a7088', j='#2e2c54', q='#1a1832', t='#e8e4dc', g='#c8b060')
    head = H('''
................
....kkkkkkkk....
..kkKKKKKKkkkk..
.kkkkkkkkkkkkk..
.kkkssssssssss..
.kksssssssssss..
.kksGGGGGGGGGGs.
.kdsGlGGsGlGGs..
..dssssssssss...
..ddsssssssss...
...dssssmmss....
....ddsssss.....
......dds.......
''')
    torso = '''
qjjttjjj
qjjttjjj
qjjttjjj
qjjttjjj
qjjttjjj
qjjttjjj
qjjttjjj
qjjttjjj
qjjjjjjj
'''
    B = Body(variants(head, pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#2e2c54', pants='#24223e',
             shoe='#3a2a2a', hax=8)
    P = poses(B)
    return B, P, ['idle', 'walk', 'hurt', 'down', 'dodge', 'guard']


# ---------------------------------------------------------------- 东方朋子（约 165 cm）：齐下巴黑发带紫光、白发带、红外套、蓝上衣
def tomoko():
    pal = P_(h='#30263e', H='#5c4a84', k='#1c1426', W='#f4f0f4', e='#6a3a1a', m='#d0506a',
             r='#d0404a', q='#8a2430', u='#3a6ac0', U='#2a4a94', y='#ffd040')
    head = H('''
....hhhhhhh....
..hhHHHHHhhhh..
.hWWWWWWWWWWWh.
.hhhhhhhhhhhhh.
hhhhhhhhhhhhhh.
hhhhhhhsshhhhh.
hhhhhsssssssshh
hhhhsbbsssbbshh
hhhhsweSssweshh
.hhhsssssssssh.
.hhkdssssmssk..
..hk.ddssss....
.......dds.....
''')
    torso = '''
qrruurr
qrruurr
qrruurr
qrruurr
qrruurr
qrryUrr
qrruurr
qrrUUrr
'''
    B = Body(variants(head, pal), TH=8, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#d0404a', pants='#3a6ac0',
             shoe='#3a2a34', hax=8, hip=1, skirt=dict(len=4, col='#3a6ac0', flare=1), bare=dict(skin='#d8c8c8'))
    P = poses(B)
    A = B.arm_len
    # 晕倒：先仰一下，再倒地
    P['faint'] = ([dict(head='h', lean=-2, bx=-1, aN=((-2, -1), (-3, 1)), aF=((1, -1), (3, 1))), dict(head='h', lie='back')], 2, 'oneshot')
    return B, P, ['idle', 'walk', 'wave', 'faint']


# ---------------------------------------------------------------- 东方良平（55 岁警察，约 170 cm）
def _paper(cv, B, P, ctx):
    if P.get('item') != 'paper':
        return
    h = ctx.get('handF')
    if not h:
        return
    x, y = X(h[0]) - 1, Y(h[1]) - 5
    cv.rect(x, y, x + 6, y + 7, '#ecebe2')
    cv.vline(x + 3, y, y + 7, '#c8c6ba')
    for yy in (y + 1, y + 3, y + 5):
        cv.hline(x + 1, x + 2, yy, '#8a8a90')
        cv.hline(x + 4, x + 5, yy, '#8a8a90')


def ryohei():
    pal = P_(n='#2a3660', N='#1a2242', g='#ffd040', y='#b4b6c2', Y='#84869a', e='#3a2a1a',
             j='#2a3660', q='#1a2242', c='#a8c4e8', t='#1a2242', B='#16161e')
    head = H('''
....nnnnnnnn...
..nnnnnnngnnnn.
.nnnnnnnnggnnn.
.NNNNNNNNNNNNNN
.yyNNNNNNNNNNNNN
.yyysssssssss..
.yysbbbssbbbs..
.yYsswesssweS..
..YdswesssweS..
..ddsssssssss..
...dssyyyyss...
....ddsssss....
......dds......
''')
    torso = '''
qjjctjjj
qjjctjjj
qjjjtjjj
qjjjgjjj
qjjjjjjj
qjjjgjjj
qBBBBBBB
qjjjjjjj
'''
    B = Body(variants(head, pal), TH=8, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#2a3660', pants='#222c50',
             shoe='#1a1a22', hax=8, front=_paper)
    P = poses(B)
    A = B.arm_len
    P['read'] = ([dict(item='paper', aF=((1, -3), (4, -2)), aN=((0, -3), (3, -3))),
                  dict(item='paper', aF=((1, -3), (4, -2)), aN=((0, -3), (3, -3)), dy=-1, hy=-1)], 2, 'loop')
    return B, P, ['idle', 'walk', 'shock', 'read']


# ---------------------------------------------------------------- 片桐安十郎（扮成送奶工）：灰发、肤色白、淡紫衬衫、青绿背带裤和棒球帽
def angelo():
    pal = P_(s='#f2d4bc', d='#d0a488', T='#3a9490', t='#246a68', C='#f0ecd6', y='#9a9aa8', Y='#6e6e80', e='#2a2030',
             m='#b05a5a', l='#c8b4e2', L='#9a86ba', o='#3a9490', q='#246a68')
    head = H('''
....TTTTTTTT....
..TTTTTTTTTTTT..
.TTTTTTTTCCTTTT.
.tTTTTTTTTTTTTTt
.yytttttttttttttt
.yyysssssssss...
.yysbbssssbbs...
.yYsswessswes...
..YdsweSsswes...
..ddssssssss....
...dsssmmmms....
....ddsssss.....
......dds.......
''')
    torso = '''
Lloooll
LloTool
Lloooll
Loooooo
qoooooo
qoooooo
qoooooo
qoooooo
'''
    B = Body(variants(head, pal), TH=8, LH=8, tw=7, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#3a9490', pants='#2e807c',
             shoe='#8a4a4a', skin='#f2d4bc', sleeve='#c8b4e2', hax=8)
    P = poses(B)
    return B, P, ['idle', 'walk', 'hurt', 'down', 'talk']


# ---------------------------------------------------------------- 劫匪：毛线帽、胡茬、灰夹克，手里一把刀
def _knife(cv, B, P, ctx):
    if P.get('item') != 'knife':
        return
    h = ctx.get('handF')
    if not h:
        return
    x, y = X(h[0]) + 1, Y(h[1])
    cv.hline(x, x + 3, y - 1, '#e8ecf4')
    cv.hline(x, x + 2, y, '#a8b0c0')
    cv.put(x - 1, y, '#4a3a2a')


def robber():
    pal = P_(c='#3a3a4a', C='#56566a', k='#2a2018', u='#c89a78', e='#2a2018',
             j='#5a5a66', q='#3a3a46', t='#8a3a3a')
    head = H('''
....cccccccc....
..cccccccccccc..
.cccccccccccccc.
.CCCCCCCCCCCCCC.
.kkCCCCCCCCCCC..
.kkssssssssss...
.kksbbbssbbbs...
.kkssweSsswes...
..kdsweSsswes...
..ddssssssss....
...duuummuus....
....duuuuuu.....
......dus.......
''')
    torso = '''
qjjttjjj
qjjttjjj
qjjjtjjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
'''
    B = Body(variants(head, pal), TH=8, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#5a5a66', pants='#34384a',
             shoe='#2a2a30', hax=8, front=_knife)
    P = poses(B)
    A = B.arm_len
    P['attack'] = ([dict(item='knife', lean=-1, aF=((-1, -1), (1, 0)), aN=((-1, -2), (1, -A + 2))),
                    dict(item='knife', lean=1, head='r', aF=(A + 2, 0), aN=((-2, -2), (-3, -1)), lF=(1, 0))], 6, 'oneshot')
    P['idle'] = ([dict(item='knife', aF=((1, -3), (3, -2))), dict(item='knife', dy=-1, aF=((1, -3), (3, -1)), aN=(0, -A + 1))], 2, 'loop')
    P['talk'] = ([dict(item='knife', aF=((1, -3), (3, -2))), dict(item='knife', head='t', aF=((1, -2), (4, 0)))], 4, 'loop')
    return B, P, ['idle', 'walk', 'hurt', 'down', 'attack', 'talk']


# ---------------------------------------------------------------- 超市店员（女，约 160 cm）：绿围裙、白衬衫、棕发马尾
def clerk():
    pal = P_(h='#7a4a2a', H='#a86e3e', k='#4a2a14', e='#3a2a1a', m='#d0506a', c='#f0f0f0', C='#c8c8d0',
             a='#2f8a5a', q='#1c5a3a', y='#f0c040')
    head = H('''
....hhhhhhh....
..hhHHHHhhhhh..
.hhhhhhhhhhhhh.
.hhhhhhhhhhhhh.
hhhhhhhhhhhhhh.
hhhhhhsshsshh..
hhhhssssssssh..
hhkhsbbsssbbs..
hhkhsweSsswes..
.hkkssssssss...
.hh.dssssmss...
.h...ddssss....
.......dds.....
''')
    torso = '''
Cccaacc
Ccaaaac
Ccaayac
Ccaaaac
Caaaaaa
qaaaaaa
qaaaaaa
'''
    B = Body(variants(head, pal), TH=7, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#f0f0f0', pants='#3a4a6a',
             shoe='#3a2a2a', hax=8, hip=1, skirt=dict(len=4, col='#2f8a5a', flare=0), bare=dict(top=4, skin='#3a4a6a'))
    P = poses(B)
    return B, P, ['idle', 'walk']


# ---------------------------------------------------------------- 葡萄丘高中女生 A / B（约 160 cm）：青绿水手服、淡紫领巾
SAILOR = '''
qtlllwt
qttlltt
qttvttt
qtttttt
qtttttt
qtttttt
qtttttt
'''


def _fan(hair, hair_l, hair_k, head):
    pal = P_(h=hair, H=hair_l, k=hair_k, e='#3a2a4a', m='#d0506a', t='#2a8a7e', q='#1a5a54', l='#3aa698', w='#ffffff',
             v='#b89ae0', r='#e04a5a')
    B = Body(variants(H(head), pal), TH=7, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=SAILOR, top='#2a8a7e', pants='#2a8a7e',
             shoe='#4a3020', hax=8, hip=1, skirt=dict(len=4, col='#2a8a7e', flare=1, pleat=2),
             bare=dict(sock='#f4f4f4', sock_h=2))
    P = poses(B)
    return B, P, ['idle', 'walk', 'cheer']


def fan_a():
    # 棕色高马尾
    return _fan('#8a5226', '#b87a3e', '#52280e', '''
..........hh...
....hhhhhhhhh..
..hhHHHHhhhhhh.
.hhhhhhhhhhhhhh
.hhhhhhhhhhhhhh
hhhhhhshhshhhh.
hhhhssssssssh..
hhhhsbbsssbbs..
hhhhsweSsswes..
hhkkssssssss...
hh..dssssmss...
h....ddssss....
.......dds.....
''')


def fan_b():
    # 黑色齐肩短发、红发夹
    return _fan('#2a2636', '#4a4660', '#16141e', '''
....hhhhhhh....
..hhHHHHhhhhh..
.hhhhhhhhhrrhh.
.hhhhhhhhhhhhh.
hhhhhhhhhhhhhh.
hhhhhshhhshhhh.
hhhhssssssssh..
hhhhsbbsssbbsh.
hhhhsweSssweshh
hhhkssssssssh..
.hhkdssssmss...
..h..ddssss....
.......dds.....
''')


# ---------------------------------------------------------------- 搭讪的男人（约 175 cm）：棕色卷发、粉衬衫、白裤、头上顶副墨镜
def flirt():
    pal = P_(h='#6a3e22', H='#9a623a', k='#3e2010', G='#18161e', e='#3a2a1a', p='#f08aa8', q='#c05a7a', c='#ffd040',
             W='#f0ece0')
    head = H('''
....hhhhhhhh....
..hhHhHhHhhhhh..
.hhGGGGhGGGGhh..
.hhhhhhhhhhhhh..
.hhhhsssssssh...
.hhhssssssssss..
.hhksbbsssbbss..
.hhksweSssweSs..
..kdsweSssweSs..
..ddsssssssss...
...dssssmmmss...
....ddsssss.....
......dds.......
''')
    torso = '''
qppsspp
qppcspp
qpppspp
qpppppp
qpppppp
qpppppp
qpppppp
qpppppp
'''
    B = Body(variants(head, pal), TH=8, LH=9, tw=7, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#f08aa8', pants='#f0ece0',
             shoe='#8a5a34', hax=8)
    P = poses(B)
    return B, P, ['idle', 'walk', 'hurt', 'down']


# ---------------------------------------------------------------- 小学生（约 125 cm）：黄帽子、红书包、短裤
def kid():
    pal = P_(y='#f8d040', Y='#c89a20', k='#3a2a1e', e='#2a2018', t='#f4f4f4', q='#c8c8d0', r='#d03a3a', R='#8a2020',
             n='#3a4a7a')
    head = H('''
...yyyyyyyy....
..yyyyyyyyyy...
.yyyyyyyyyyyy..
YYYYYYYYYYYYYYY
.kkkssssssss...
.kkssssssssss..
.kksweSssweSs..
.kksweSssweSs..
..kssssssssss..
..dssssmmsss...
...ddsssss.....
.....dds.......
''')
    torso = '''
qtttttt
qtttttt
qtttttt
qtttttt
nnnnnnn
'''
    pack = grid_part('''
RRR
RrR
RrR
RRR
''', -3, 1, 'torso')
    B = Body(variants(head, pal), TH=5, LH=5, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#f4f4f4', pants='#3a4a7a',
             shoe='#f4f4f4', hax=7, hip=1, bare=dict(top=2, sock='#f4f4f4', sock_h=1), back=pack, shoe_h=1)
    P = poses(B)
    return B, P, ['idle', 'walk', 'run', 'hurt']


CAST = {
    'josuke': ('东方仗助', josuke), 'jotaro4': ('空条承太郎', jotaro4), 'koichi': ('广濑康一', koichi),
    'thug_a': ('学长A', thug_a), 'thug_b': ('学长B', thug_b), 'tomoko': ('东方朋子', tomoko), 'ryohei': ('东方良平', ryohei),
    'angelo': ('片桐安十郎（送奶工）', angelo), 'robber': ('劫匪', robber), 'clerk': ('店员', clerk),
    'fan_a': ('女生', fan_a), 'fan_b': ('女生', fan_b), 'flirt': ('搭讪的男人', flirt), 'kid': ('小学生', kid),
}


def build(cid):
    name, fn = CAST[cid]
    B, P, names = fn()
    sh = Sheet(cid, name)
    sh.add_pose(B, P, names)
    sh.body = B
    return sh


if __name__ == '__main__':
    import sys
    from view import compact, lineup
    out = sys.argv[1]
    ids = sys.argv[2:] or list(CAST)
    stand = []
    for cid in ids:
        sh = build(cid)
        compact(sh, k=6, title=cid + ' ' + sh.name).save('%s/z_%s.png' % (out, cid))
        stand.append(sh.rows[0][1][0])
    lineup(stand, ids, k=6, ref_h=[(30, '180cm'), (34, '门 204'), (15, '窗台 90')]).save(out + '/lineup.png')
