# 第1–3章人物（重画）：虹村形兆、虹村家的父亲；虹村亿泰、小林玉美、间田敏和、表面（木偶 / 变成仗助）、康一的妈妈和姐姐、
#   飙车族 A/B、由花子的剪影、骑车的康一；山岸由花子（黑 / 灰 / 白发）、东尼欧。
#   头照 TV 动画第四部设定画；身高照 第四部/docs/比例标准.md。动作名、帧数、fps 和旧图集一致。
import numpy as np

from px import Cv, OUTLINE, shade, rows, rgba
from castlib import (P_, H, GAKURAN8x9, GAKURAN8x8, GAKURAN7x7, Body, Sheet, draw, poses, variants, grid_part, chain, X, Y, CW, CH,
                     OX, OY, raw_frame, make_build, main)
import cast_pro


# ---------------------------------------------------------------- 虹村形兆（185 cm）：金色高平头、鬓边一条辫子、黑色长校服、洋红皮带
def keicho():
    pal = P_(y='#e8c84a', Y='#fff09a', k='#a8842a', o='#c89a30', e='#2a2a40',
             j='#262634', q='#14141c', t='#c8ccd8', g='#ffd040', r='#b03a7a')
    head = H('''
...yyyyyyyyy...
..yYYYYYYYYYy..
..yYYYYYYYYYy..
..yyYYYYYYYyy..
..yyyyyyyyyyy..
.kyyyyyyyyyyy..
.kyykssssssss..
.oyksbbbsbbbs..
.oyksweSsswes..
.oydsweSsswes..
.o.dssssssss...
.o..dsssmmss...
....ddsssss....
......dds......
''')
    torso = '''
qjjjtjjj
qjgjtjjj
qjjjtjjj
qjjjtjjj
qjjjtjjj
qjjjtjjj
qjjjtjjj
qrrrgrrr
qjjjtjjj
qrrrgrrr
'''
    B = Body(variants(head, pal), TH=10, LH=9, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#262634', pants='#1e1e2a',
             shoe='#4a3020', hax=8, coat=dict(len=4, col='#262634', line=0), cuff='#c8ccd8')
    P = poses(B)
    return B, P, ['idle', 'walk', 'run', 'point', 'pose', 'shock', 'hurt', 'dodge', 'guard', 'sit', 'down']


# ---------------------------------------------------------------- 虹村家的父亲：绿色、一身肉瘤、锁着链子，缩成一团
DAD = dict(G='#5a8a4a', g='#3e6a38', D='#2a4a2a', L='#86b06a', e='#1a1a20', w='#e8e8d8', c='#8a8e98', C='#5a5e68', m='#2a1a1a')
DAD_IDLE = '''
........gggg.gggg.......
......ggGGGGgGGGGgg.....
....ggGLLGGGGGLLGGGg....
...gGGLGGGGgGGGGLGGGg...
..gGGGGGGgGGGGGGGGGGGg..
..gGGGGGGGGGGGewGGGGGg..
.gGGLGGGGGGGGGeeGGmGGg..
.gGGGGGgGGGGGGGGGmmmGg..
gGGGGGGGGGGGGGGGGGwwGg..
gGGLGGGGGGgGGGGGGGGGg...
gGGGGGGGGGGGGGGGGGGGg...
gGGGGcCcCcGGGGGGgGGGGg..
.gGGGGGGGGGGGGGGGGGGGg..
.gGGGGGGGGGGLGGGGGGGGg..
..gGGGgGGGGGGGGGGGGGg...
..gDGGGGGGDDGGGGGGDg....
...gDDDDDg.gDDDDDDg.....
'''
DAD_HUG = '''
........gggg.gggg.......
......ggGGGGgGGGGgg.....
....ggGLLGGGGGLLGGGg....
...gGGLGGGGgGGGGLGGGg...
..gGGGGGGgGGGGGGGGGGGg..
..gGGGGGGGGGGGbbGGGGGg..
.gGGLGGGGGGGGGGGGGmGGg..
.gGGGGGgGGGGGGGGGGmGGg..
gGGGGGGGGGGGGGGGGGGGGgg.
gGGLGGGGGGgGGGGGGGGGGGGg
gGGGGGGGGGGGGGGGGGGGGGGg
gGGGGcCcCcGGGGGGgGGGGGg.
.gGGGGGGGGGGGGGGGGGGGg..
.gGGGGGGGGGGLGGGGGGGGg..
..gGGGgGGGGGGGGGGGGGg...
..gDGGGGGGDDGGGGGGDg....
...gDDDDDg.gDDDDDDg.....
'''


def nijimura_dad():
    pal = dict(DAD, b='#1a1a20')
    sh = Sheet('nijimura_dad', '虹村兄弟的父亲')
    sh.add('idle', [raw_frame(DAD_IDLE, pal), raw_frame(DAD_IDLE, pal, 0, -1)], 3, 'loop')
    sh.add('hug', [raw_frame(DAD_HUG, pal)], 1, 'static')
    sh.face = (OX - 2, OY - 16)
    return sh


# ---------------------------------------------------------------- 虹村亿泰（178 cm）：两侧剃青的平头、脸上两道斜纹、藏青校服、胸口 $ ¥、绿皮带
def okuyasu():
    pal = P_(k='#22202c', K='#3c3a4c', g='#8a8a98', e='#2a2a40', x='#8a5a4a',
             j='#28306a', q='#161c44', y='#ffd040', r='#8ac040', R='#5a8a28')
    head = H('''
....kkkkkkkkk..
...kKKKKKKKKKk.
..kkkkkkkkkkkk.
..gkkkkkkkkkkk.
.gggkkkkkkkkk..
.ggggssssssss..
.gggsbbbsbbbs..
.ggdssweSswes..
..gdxsweSswes..
..ddsxssssss...
...dsssmmmss...
....ddsssss....
......dds......
''')
    torso = '''
qjjjjjjj
qjyjjyjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
qrrrryrr
qjRrrrrr
qjjjjjjj
'''
    B = Body(variants(head, pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#28306a', pants='#20265a',
             shoe='#4a3020', hax=8, coat=dict(len=2, col='#28306a'), cuff='#e8e8f0')
    P = poses(B)
    A = B.arm_len
    P['dizzy'] = ([dict(head='h', lean=-1, aN=(-1, -A + 1), aF=(1, -A + 1)), dict(head='h', lean=1, dy=-1, aN=(1, -A + 1), aF=(-1, -A + 1))], 4, 'loop')
    return B, P, ['idle', 'walk', 'run', 'point', 'pose', 'shock', 'hurt', 'dodge', 'guard', 'kick', 'sit', 'dizzy', 'down',
                  'sit_chair']


# ---------------------------------------------------------------- 小林玉美（153 cm）：一大团藏青飞机头、金耳环、粉色短袖、黑裤、锯齿纹皮带
def tamami():
    pal = P_(n='#2a2c5c', N='#4a4e8c', g='#ffd040', e='#1a1a24', p='#f4a8c0', q='#c8708e', z='#3a7ad0', k='#1c1c26')
    head = H('''
....nnnnnnnnn...
..nnNNNNNNNNnn..
.nnNNNNNNNNNNnn.
.nnnnnnnnnnnnnn.
nnnnnnnnnnnnnnn.
nnnnnnnnnnnnnnn.
.nnnssssssssss..
.nnsssssssssss..
.ngswessswesss..
..dswessswess...
..dssssssssss...
...dsssmmmss....
....ddsssss.....
......dds.......
''')
    torso = '''
qppsspp
qpppspp
qpppppp
qpppppp
qpppppp
zpzpzpz
kkkkkkk
'''
    B = Body(variants(head, pal), TH=7, LH=6, tw=7, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#f4a8c0', pants='#1c1c26',
             shoe='#3a2a22', hax=8, sleeve_len=2)
    P = poses(B)
    A = B.arm_len
    P['cover_ears'] = ([dict(head='h', aF_front=True, aF=((2, 1), (0, 4)), aN=((-1, 1), (1, 4)), drop=1),
                        dict(head='h', aF_front=True, aF=((2, 1), (0, 4)), aN=((-1, 1), (1, 4)), drop=1, lean=-1)], 6, 'loop')
    P['wave'] = ([dict(aF=((1, 2), (2, A)), head='t'), dict(aF=((2, 2), (4, A - 1)))], 4, 'loop')
    P['bow'] = ([dict(lean=2, dy=-1, hx=1, hy=-2, aN=(1, -A + 1), aF=(1, -A + 1)),
                 dict(lean=3, dy=-1, hx=2, hy=-3, head='h', aN=(1, -A + 1), aF=(1, -A + 1))], 3, 'loop')
    P['cry'] = ([dict(head='h', aF_front=True, aF=((2, -1), (0, 3)), aN=((0, -2), (3, 2)), dy=-1),
                 dict(head='h', aF_front=True, aF=((2, -1), (0, 2)), aN=((0, -2), (3, 1)), dy=-2)], 4, 'loop')
    P['run'] = (P['run'][0], 13, 'loop')
    return B, P, ['idle', 'walk', 'run', 'cover_ears', 'cry', 'hurt', 'wave', 'fall', 'crawl', 'kneel', 'bow']


# ---------------------------------------------------------------- 间田敏和（165 cm）：黑色蘑菇头、眯缝眼、藏青校服、胸前三道金扣
def hazamada():
    pal = P_(k='#22202c', K='#3e3c50', e='#1a1a24', j='#283660', q='#161e3e', g='#e8a030')
    head = H('''
....kkkkkkk....
..kkKKKKKkkkk..
.kkkkkkkkkkkkk.
.kkkkkkkkkkkkk.
kkkkkkkkkkkkkk.
kkkkkskkkskkkk.
kkkkssssssssk..
kkkksbbssbbsk..
kkkkswesswesk..
.kkkssssssssk..
.kk.dsssmmss...
.....ddssss....
.......dds.....
''')
    torso = '''
qjjjjjjj
qjjgggjj
qjjjjjjj
qjjgggjj
qjjjjjjj
qjjgggjj
qjjjjjjj
qjjjjjjj
'''
    B = Body(variants(head, pal), TH=8, LH=7, tw=8, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#283660', pants='#20294e',
             shoe='#3a2a22', hax=8)
    P = poses(B)
    A = B.arm_len
    P['smirk'] = ([dict(aF=((1, -3), (2, -1))), dict(head='t', aF=((1, -3), (3, 0)), dy=-1)], 3, 'loop')
    P['knocked'] = ([dict(head='h', lie='back')], 1, 'static')
    P['run'] = (P['run'][0], 13, 'loop')
    return B, P, ['idle', 'walk', 'run', 'smirk', 'point', 'shock', 'knocked']


# ---------------------------------------------------------------- 表面（木偶）：木头人台，额头一颗螺丝
def surface_doll():
    pal = P_(o='#c89a5a', O='#e8c080', k='#8a6230', n='#8a8e98', s='#c89a5a', d='#8a6230')
    head = '''
...oooooo..
..oOOOOooo.
.oOOoooooo.
.ooooonooo.
.oooooooook
.oooooooook
.oooooooook
.ooooooooko
..oooooooo.
..koooooo..
...kkooo...
'''
    torso = '''
kooooook
kooooooo
koooOooo
kooooooo
kkkkkkkk
kooooooo
kooooooo
kooooooo
'''
    B = Body({'n': head, 'h': head, 't': head, 's': head, 'r': head}, TH=8, LH=8, tw=8, arm_w=2, leg_w=3, pal=pal, torso=torso,
             top='#c89a5a', pants='#c89a5a', shoe='#8a6230', skin='#c89a5a', hax=6, shoe_h=1)
    P = poses(B)
    return B, P, ['idle', 'walk', 'jump', 'fall', 'hurt']


def _surface(cut):
    # 变成仗助的样子：就是仗助，只多额头一颗螺丝；cut = 被削过之后脸上留一道裂纹
    B, P, names = cast_pro.josuke()
    pal = B.pal
    pal['n'] = '#8a8e98'
    pal['x'] = '#7a5230'

    def mark(hd):
        g = [list(r) for r in hd]
        g[6][9] = 'n'
        if cut:
            g[9][11] = 'x'
            g[10][10] = 'x'
        return [''.join(r) for r in g]
    B.heads = {k: mark(v) for k, v in B.heads.items()}
    return B, P, names


def surface():
    return _surface(False)


def surface_cut():
    return _surface(True)


# ---------------------------------------------------------------- 康一的妈妈（约 160 cm）：棕色短发、黄条纹衫、长裙
def hirose_mom():
    pal = P_(h='#8a5a34', H='#b07a48', k='#5a3418', e='#2e5cb0', m='#d0606a', y='#f0c860', Y='#fff0b0', q='#c89a38', c='#70c8e0')
    head = H('''
....hhhhhhh....
..hhHHHHHhhhh..
.hhhhhhhhhhhhh.
.hhhhhhhhhhhhh.
hhhhhhhhhhhhhh.
hhhhhsshhsshh..
hhhhssssssssh..
hhkhsbbsssbbs..
.hkhsweSsswes..
.hkdssssssss...
..k.dssssmss...
.....ddssss....
.......dds.....
''')
    torso = '''
qyysyyy
qYYcYYY
qyyyyyy
qYYYYYY
qyyyyyy
qYYYYYY
qyyyyyy
'''
    B = Body(variants(head, pal), TH=7, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#f0c860', pants='#a89878',
             shoe='#5a4030', hax=8, hip=1, sleeve_len=3, skirt=dict(len=5, col='#b8a888', flare=1), bare=dict())
    P = poses(B)
    P['cry'] = ([P['cry'][0][0]], 1, 'static')
    return B, P, ['idle', 'walk', 'cry', 'wave']


# ---------------------------------------------------------------- 广濑绫那（康一的姐姐，约 163 cm）：黑长发、紫色连衣裙、白腰带
def ayana():
    pal = P_(k='#22202c', K='#444058', e='#3a3a70', m='#d0506a', v='#7a4ab0', V='#9a6ad0', q='#4a2a78', W='#f0f0f0', n='#2a2a60')
    head = H('''
....kkkkkkk....
..kkKKKKKkkkk..
.kkkKkkkkkkkkk.
.kkkkkkkkkkkkk.
kkkkkkkkkkkkkk.
kkkkkkskkskkkk.
kkkkssssssssk..
kkkksbbsssbbs..
kkkksweSsswes..
kkkkssssssss...
kkk.dssssmss...
kk...ddssss....
kk.....dds.....
''')
    torso = '''
qVVsVVV
qvvvvvv
qvvvvvv
qvvvvvv
qvvvvvv
WWWWWWW
qnnnnnn
'''
    hair = grid_part('''
kk
kk
kk
kk
.k
''', 0, 13, 'head')
    B = Body(variants(head, pal), TH=7, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#7a4ab0', pants='#2a2a60',
             shoe='#3a2a34', hax=8, hip=1, sleeve_len=2, skirt=dict(len=4, col='#2a2a60', flare=1), bare=dict(), back=hair)
    P = poses(B)
    P['cry'] = (P['cry'][0], 3, 'loop')
    return B, P, ['idle', 'walk', 'cry', 'cheer']


# ---------------------------------------------------------------- 飙车族 A / B（约 178 cm）：特攻服
def biker_a():
    # 金色飞机头、白色特攻服、红腰带
    pal = P_(y='#f0d050', Y='#fff4a0', k='#a8842a', e='#2a2a40', W='#f2f0e8', q='#b8b4a8', r='#c83030', n='#2a2a34')
    head = H('''
.........yyyyyy.
......yyYYYYYYyy
....yyyyyyyyyyy.
...yyyyyyyyyyy..
..yyyyyyykkkkk..
..yyykssssssss..
.yyyksbbbsbbbs..
.yyykssweSswes..
.ykkdssweSswes..
..kkdssssssss...
...kdsssmmmss...
....ddssssss....
......ddss......
''')
    torso = '''
qWWnnWWW
qWWnnWWW
qWWWnWWW
qWWWWWWW
qWWWWWWW
qWWWWWWW
qrrrrrrr
qrrrrrrr
qWWWWWWW
'''
    B = Body(variants(head, pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#f2f0e8', pants='#e4e0d4',
             shoe='#2a2a34', hax=8, coat=dict(len=5, col='#f2f0e8', open=(0, 1), trim='#c83030'))
    P = poses(B)
    P['run'] = (P['run'][0], 11, 'loop')
    return B, P, ['idle', 'walk', 'run', 'point', 'hurt', 'kick', 'down']


def biker_b():
    # 黑发扎红头带、黑色特攻服、口罩拉到下巴
    pal = P_(k='#22202c', K='#3e3c50', r='#d03a3a', e='#2a2a40', j='#2a2a34', q='#16161c', W='#e8e8e0', g='#e8c040')
    head = H('''
....kkkkkkkk....
..kkKKKKKKkkkk..
.kkkkkkkkkkkkk..
.rrrrrrrrrrrrrr.
rrkkkkkkkkkkkk..
r.kkkssssssss...
..kksbbbsbbbs...
..kkssweSswes...
..kdssweSswes...
..ddssssssss....
...dWWWWWWWs....
....dWWWWWW.....
......dds.......
''')
    torso = '''
qjjWWjjj
qjjWWjjj
qjjjWjjj
qjgjjjgj
qjjjjjjj
qjjjjjjj
qrrrrrrr
qjjjjjjj
qjjjjjjj
'''
    B = Body(variants(head, pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#2a2a34', pants='#22222c',
             shoe='#4a3020', hax=8, coat=dict(len=5, col='#2a2a34', open=(0, 1), trim='#d03a3a'))
    P = poses(B)
    P['run'] = (P['run'][0], 11, 'loop')
    return B, P, ['idle', 'walk', 'run', 'point', 'hurt', 'kick', 'down']


# ---------------------------------------------------------------- 山岸由花子（167 cm）：及腰的黑色大波浪、青绿水手服、淡紫领巾
def _yukako(hair=('#2a2438', '#4a4264', '#16121e'), want=None):
    pal = P_(k=hair[0], K=hair[1], D=hair[2], e='#3a4aa0', m='#c8506a', t='#2a8a7e', q='#1a5a54', l='#3aa698', v='#b89ae0', W='#f0f0f0')
    head = H('''
....kkkkkkk....
..kkKKKKKKkkk..
.kkkKkkkkkkkkk.
.kkkkkkkkkkkkk.
kkkkkkkkkkkkkk.
kkkkkkkskkkkkk.
kkkkkssssssskk.
kkkksbbsssbbsk.
kkkksweSsswesk.
kkkkssssssssk..
.kkkdssssmss...
.kkk.ddssss....
.kk....dds.....
''')
    torso = '''
qtlllWt
qttlltt
qttvttt
qttvttt
qtttttt
qtttttt
qtttttt
qtttttt
'''
    back = grid_part('''
.kkkk....
kkkkkk...
kkKkkkk..
kkkkkkk..
.kkkKkk..
kkkkkkkk.
kKkkkkkk.
kkkkkkk..
.kkkkKkk.
kkkkkkkk.
kkKkkkk..
.kkkkkk..
..kkkkk..
.kkkkk...
..kkk....
''', -2, 8, 'head')
    B = Body(variants(head, pal), TH=8, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#2a8a7e', pants='#2a8a7e',
             shoe='#4a3020', hax=8, hip=1, skirt=dict(len=5, col='#2a8a7e', flare=1, pleat=2), bare=dict(sock='#f4f4f4', sock_h=1),
             back=back)
    P = poses(B)
    A = B.arm_len
    P['run'] = (P['run'][0], 13, 'loop')
    P['blush'] = ([dict(head='t', aF_front=True, aF=((2, -1), (1, 3)), aN=((0, -2), (2, 2))),
                   dict(head='t', aF_front=True, aF=((2, -1), (1, 3)), aN=((0, -2), (2, 2)), dy=-1, lean=-1)], 4, 'loop')
    return B, P, want or ['idle', 'walk', 'run', 'cmd', 'hurt', 'down', 'blush']


YUKAKO_HAIR = {'': ('#2a2438', '#4a4264', '#16121e'), 'grey_': ('#8a8a98', '#b4b4c0', '#5e5e6c'), 'white_': ('#e8e8ee', '#ffffff', '#b0b0c0')}


def yukako():
    sh = Sheet('yukako', '山岸由花子')
    for pre, hair in YUKAKO_HAIR.items():
        B, P, names = _yukako(hair)
        for n in names:
            frs, fps, kind = P[n]
            sh.add(pre + n, [draw(B, f) for f in frs], fps, kind)
        if not pre:
            sh.body = B
    return sh


def yukako_sil():
    # 第2章只露一个影子：整个人压成深紫的剪影
    B, P, _ = _yukako()
    sh = Sheet('yukako_sil', '？？？')
    frs = []
    for f in P['idle'][0]:
        cv = draw(B, f, outline=False)
        cv.a[cv.mask()] = rgba('#241a36')
        frs.append(cv.outline(OUTLINE))
    sh.add('idle', frs, 2, 'loop')
    return sh


# ---------------------------------------------------------------- 东尼欧·特拉萨迪（约 180 cm）：高厨师帽、金发、白厨师服、红领巾
def tonio():
    pal = P_(W='#f6f6f0', V='#c8ccd0', y='#e8c860', k='#a8842a', e='#3a6ab0', r='#d03a3a', q='#c8ccd0', g='#e8c040', c='#b8bcc4')
    head = H('''
...WWWWWWWW....
..WWWWWWWWWW...
..WWWWWWWWWW...
..WWWWWWWWWW...
..VWWWWWWWWV...
...WWWWgWWW....
..yVVVVVVVVy...
.yyyssssssss...
.yysbbbssbbbs..
.yksswesssweS..
..kdswesssweS..
..ddsssssssss..
...dssssmmss...
....ddsssss....
......dds......
''')
    torso = '''
qWrrrWWW
qWWrrWWW
qWWWWWWW
qWcWWcWW
qWWWWWWW
qWcWWcWW
qWWWWWWW
qWWWWWWW
qVVVVVVV
'''
    B = Body(variants(head, pal), TH=9, LH=9, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#f6f6f0', pants='#e8e8e0',
             shoe='#3a3a44', hax=8, coat=dict(len=4, col='#f6f6f0', trim='#c8ccd0'))
    P = poses(B)
    A = B.arm_len
    P['cmd'] = ([dict(aF=((2, -2), (5, 0))), dict(aF=((2, -2), (5, 1)), head='t', dy=-1)], 2, 'loop')
    P['rage'] = ([dict(head='r', lean=1, aF=(A + 1, 2), aN=((-2, 1), (-3, 4))), dict(head='r', lean=1, aF=(A + 1, 3), aN=((-2, 1), (-3, 5)), dy=1)], 6, 'loop')
    return B, P, ['idle', 'walk', 'cmd', 'shock', 'rage']


# ---------------------------------------------------------------- 骑车的康一：自行车（高 17、长 28）+ 上半身
def koichi_bike():
    B, P, _ = cast_pro.koichi()

    def frame(ph, pedal=True):
        cv = Cv(CW, CH)
        # 车：两个轮子（半径 5）、车架、车把、车座
        for wx in (-9, 9):
            cx, cy = X(wx), Y(5)
            for a in range(0, 360, 12):
                import math
                cv.put(int(round(cx + math.cos(math.radians(a)) * 5)), int(round(cy + math.sin(math.radians(a)) * 5)), '#2a2a30')
            for k in range(2):
                import math
                a = math.radians(ph * 45 + k * 90)
                cv.line(cx - math.cos(a) * 4, cy - math.sin(a) * 4, cx + math.cos(a) * 4, cy + math.sin(a) * 4, '#9a9ea8')
            cv.put(cx, cy, '#5a5e68')
        fr = '#d04a4a'
        cv.line(X(-9), Y(5), X(-2), Y(5), fr)
        cv.line(X(-2), Y(5), X(4), Y(11), fr)
        cv.line(X(-9), Y(5), X(-4), Y(12), fr)
        cv.line(X(-4), Y(12), X(4), Y(11), fr)
        cv.line(X(9), Y(5), X(5), Y(14), fr)
        cv.hline(X(4), X(7), Y(15), '#2a2a30')              # 车把
        cv.hline(X(-6), X(-3), Y(13), '#2a2a30')            # 车座
        # 人：坐在车座上，手扶车把，脚踩踏板
        up = (ph % 2 == 0)
        pose = dict(bx=-3, dy=B.shoe_h + 13 - (B.LH - 1) + 0, lean=2, aF=((2, -2), (7, -1)), aN=((2, -3), (6, -2)),
                    lN=((2, -1), (3 if up else 1, 9 if up else 6)), lF=((2, -1), (1 if up else 3, 6 if up else 9)))
        body = draw(B, pose, outline=False)
        cv.blit(body)
        return cv.outline(OUTLINE)

    sh = Sheet('koichi_bike', '广濑康一')
    sh.add('ride', [frame(i) for i in range(4)], 10, 'loop')
    sh.add('idle', [frame(0)], 1, 'static')
    return sh


CAST = {
    'keicho': ('虹村形兆', keicho), 'nijimura_dad': ('虹村兄弟的父亲', nijimura_dad),
    'okuyasu': ('虹村亿泰', okuyasu), 'tamami': ('小林玉美', tamami), 'hazamada': ('间田敏和', hazamada),
    'surface_doll': ('表面', surface_doll), 'surface': ('表面', surface), 'surface_cut': ('表面', surface_cut),
    'hirose_mom': ('康一的妈妈', hirose_mom), 'ayana': ('广濑绫那', ayana), 'biker_a': ('飙车族A', biker_a), 'biker_b': ('飙车族B', biker_b),
    'yukako_sil': ('？？？', yukako_sil), 'koichi_bike': ('广濑康一', koichi_bike),
    'yukako': ('山岸由花子', yukako), 'tonio': ('东尼欧·特拉萨迪', tonio),
}
build = make_build(CAST)

if __name__ == '__main__':
    import sys
    main(CAST, build, sys.argv)
