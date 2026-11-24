# 第1章以后的替身（重画）：轰炸空间、回音 ACT1 / ACT2 / ACT3、珍珠果酱、辣妹、天堂之门、丰收、杀手皇后、枯萎穿心攻击、
#   灰姑娘、公路之星、猫草、Cheap Trick。全部照官方设定（JoJo Wiki 的 Infobox_Anime 图）单独画，不再拿白金之星换色。
#   人形的共用 rig 骨架和 poses.stand_poses；不是人形的整帧手画。动作名、帧数、fps 和旧图集一致。
from px import Cv, mix, shade, OUTLINE, rows
from castlib import (H, Body, Sheet, draw, variants, grid_part, chain, X, Y, CW, CH, OX, OY, raw_frame, make_build, main, stand_poses)
from stands_pro import stand_fx

BASE = {'w': '#ffffff', 'b': '#1a1438', 'M': '#7a2030'}
STD = ['idle', 'punch', 'rush', 'block', 'pose', 'hurt', 'finger', 'fist', 'reach', 'upper']


def P_(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


def pads(c, cd, spike=None):
    """肩甲（挂到 front）"""
    def fn(cv, B, P, ctx):
        for key, dark in (('shF', True), ('shN', False)):
            sx, sy = ctx[key]
            x, y = X(sx), Y(sy)
            cv.rect(x - 1, y - 2, x + 1, y, cd if dark else c)
            cv.put(x, y - 2, shade(c, 0.3) if not dark else c)
            if spike:
                d = -1 if not dark else 1
                cv.put(x + d, y - 3, spike)
                cv.put(x + d, y - 4, spike)
    return fn


# ---------------------------------------------------------------- 轰炸空间：白底蓝纹的机械人形，肩上有刺，身上 ¥ $
def thehand():
    pal = P_(W='#e8ecf4', s='#e8ecf4', d='#a8b0c8', u='#3a5ad0', U='#24368a', e='#60d0f0', y='#f0c040', m='#24368a', p='#e8ecf4')
    head = H('''
...WWWWWW...
..WWWWWWWW..
.dWuWWWWuWW.
.dWuWWWWuWW.
.dWWWWWWWWW.
.dbbbWWbbbW.
.dWweWWweWW.
.dWWWWWWWWW.
..dWuuuuuW..
..dWummuW...
...dWWWWW...
.....dWW....
''')
    torso = '''
UWWWWWWWWW
UWyWWWWyWW
UWWWuuWWWW
UWWuWWuWWW
UWWWWWWWWW
UWWuWWuWWW
UWWWWWWWWW
UWWuWWuWWW
UuuuuyuuuU
UWWWWWWWW.
.UWWWWWW..
'''
    B = Body(variants(head, pal), TH=11, LH=11, tw=10, arm_w=3, leg_w=4, pal=pal, torso=torso, top='#e8ecf4', pants='#e8ecf4',
             shoe='#24368a', skin='#e8ecf4', sleeve='#e8ecf4', glove='#3a5ad0', sleeve_len=5, hax=6, shoulder=1,
             bare=dict(top=4, skin='#3a5ad0'), front=chain(pads('#3a5ad0', '#24368a', '#1a1a2a'), stand_fx('#78a6ff')), kind='stand')
    P = stand_poses(B)
    return B, P, STD + ['erase', 'pull']


# ---------------------------------------------------------------- 杀手皇后：浅粉色、猫耳猫眼、骷髅徽记、黑手套黑腰带
def killerqueen():
    pal = P_(P='#f4d0dc', p='#d8a0b4', s='#f4d0dc', d='#c088a0', k='#2a2030', K='#4a3a54', w='#f0e890', e='#3a2a30', W='#ffffff',
             m='#c088a0', n='#b07890')
    head = H('''
.pp......pp.
.pPp....pPp.
.pPPppppPPp.
.pPPPPPPPPp.
.pPPPPPPPPp.
.pbbPPPPbbp.
.pwePPPwePp.
.pPPPPPPPPp.
..pPPPPPPp..
..dPPnnPPp..
...dPPPPp...
.....dPP....
''')
    torso = '''
kPPPPPPPPk
dPPPPPPPPP
dPPdPPPdPP
dPPPPPPPPP
dPPdPPPdPP
dPPPPPPPPP
dPPdPPPdPP
dPPPPPPPPP
kkkkWkkkkk
kKkkkkkkk.
.kkkkkkk..
'''
    B = Body(variants(head, pal), TH=11, LH=11, tw=10, arm_w=3, leg_w=4, pal=pal, torso=torso, top='#f4d0dc', pants='#f4d0dc',
             shoe='#2a2030', skin='#f4d0dc', sleeve='#f4d0dc', glove='#2a2030', sleeve_len=5, hax=6, shoulder=1,
             bare=dict(top=5, skin='#2a2030'), front=chain(pads('#2a2030', '#1a1420'), stand_fx('#e898c0')), kind='stand')
    P = stand_poses(B)
    # 一张图集放下各章用到的全部动作（第6章、第7章占位、第11章占位、终章都用这一张）
    return B, P, ['idle', 'punch', 'rush', 'pose', 'hurt', 'crack', 'fist', 'kick', 'block', 'reach', 'upper']


# ---------------------------------------------------------------- 公路之星：紫色人形，全身一节一节的深色横纹，黄眼睛
def highway():
    pal = P_(p='#8a5ad0', s='#8a5ad0', d='#5a3a98', k='#2e2050', e='#f0e040', w='#f0e040', m='#2e2050', l='#b08af0')
    head = H('''
...pppppp...
..pplllppp..
.dpppppppp..
.dkkkkkkkkp.
.dpppppppp..
.dbbppppbbp.
.dweppppwep.
.dkkkkkkkkp.
..dpppppp...
..dppmmpp...
...dkkkk....
.....dpp....
''')
    torso = '''
dppppppppp
dkkkkkkkkk
dppppppppp
dppppppppp
dkkkkkkkkk
dppppppppp
dppppppppp
dkkkkkkkkk
dppppppppp
dkkkkkkkk.
.dpppppp..
'''

    def stripes(cv, B, P, ctx):
        # 手脚上的横纹：沿肢体每隔两格压一道深色
        k = pal['k']
        a = cv.a
        import numpy as np
        col = np.array([0x8a, 0x5a, 0xd0])
        for y in range(Y(B.LH + B.TH), Y(0) + 1):
            if (y % 3) != 0:
                continue
            for x in range(CW):
                if tuple(a[y, x][:3]) == tuple(col) and (x < X(-B.tw // 2) or x > X(B.tw // 2 - 1) or y > Y(B.LH - 2)):
                    cv.put(x, y, k)

    B = Body(variants(head, pal), TH=11, LH=11, tw=10, arm_w=3, leg_w=4, pal=pal, torso=torso, top='#8a5ad0', pants='#8a5ad0',
             shoe='#5a3a98', skin='#8a5ad0', sleeve='#8a5ad0', glove='#8a5ad0', hax=6, shoulder=1,
             front=chain(stripes, stand_fx('#ff70a0')), kind='stand')
    P = stand_poses(B)
    return B, P, STD


# ---------------------------------------------------------------- 回音 ACT3：小个子（一米出头）、白绿相间、额头和腰带上一个 3
def echoes3():
    pal = P_(W='#eef4e8', s='#eef4e8', d='#b4c4b0', g='#5ab060', G='#2e6a3a', e='#2e6a3a', m='#2e6a3a', y='#f0d040')
    head = H('''
...gggggg...
..gWWWWWWg..
.gWWWgWWWWg.
.gWWWWgWWWg.
.gWWWgWWWWg.
.GbbWWWWbbW.
.GweWWWweWW.
.GWWWWWWWWW.
..GWWWWWWW..
..dWWmmWW...
...dWWWW....
''')
    torso = '''
GWWWWWWW
GWgWWWgW
GWWWWWWW
GWWgWgWW
GWWWWWWW
GggggygG
GWWWWWW.
.GWWWW..
'''
    B = Body(variants(head, pal), TH=8, LH=8, tw=8, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#eef4e8', pants='#eef4e8',
             shoe='#5ab060', skin='#eef4e8', sleeve='#eef4e8', glove='#5ab060', sleeve_len=4, hax=6,
             bare=dict(top=3, skin='#5ab060'), front=stand_fx('#60e0a0'), kind='stand')
    P = stand_poses(B)
    return B, P, ['idle', 'punch', 'rush', 'pose', 'hurt', 'fist', 'kick', 'block', 'finger', 'reach', 'upper']


# ---------------------------------------------------------------- 天堂之门：戴帽子的小男孩模样（《粉红黑少年》的主角），白衣、黄色点缀
def heavensdoor():
    pal = P_(W='#f6f2e6', s='#f8e8d0', d='#d8c0a0', y='#f0c040', Y='#c89420', e='#3a8a5a', m='#a05a4a', k='#3a3a44', g='#7ac070')
    head = H('''
....WWWWWW....
..WWWWWWWWWW..
.WWWWWWWWWWWW.
.yyyyyyyyyyyy.
YYYYYYYYYYYYYY
..gsssssssss..
..gsbbsssbbs..
..gsweSssweS..
...sweSssweS..
...dssssssss..
....dsssmss...
.....ddss.....
''')
    torso = '''
dWWyWWW
dWWyWWW
dWWWWWW
dWyWWyW
dWWWWWW
dWWWWWW
dyyyyyy
'''
    B = Body(variants(head, pal), TH=7, LH=6, tw=7, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#f6f2e6', pants='#f6f2e6',
             shoe='#f0c040', skin='#f8e8d0', sleeve='#f6f2e6', hax=7, front=stand_fx('#ffd060'), kind='stand')
    P = stand_poses(B)
    P['punch'] = (P['punch'][0], 10, 'oneshot')
    P['upper'] = (P['upper'][0], 10, 'oneshot')
    P['rush'] = (P['rush'][0], 14, 'loop')
    return B, P, ['idle', 'punch', 'upper', 'rush', 'block', 'hurt', 'write']


# ---------------------------------------------------------------- 灰姑娘：女性机械人形，洋红 + 白，头顶一圈高冠
def cinderella():
    pal = P_(r='#d0407a', R='#f070a0', q='#8a2450', W='#f4f0f4', s='#f4f0f4', d='#c8c0d0', e='#5a3ad0', m='#d0407a', k='#3a2a44')
    head = H('''
...rWrWrW...
...rWrWrW...
..rRWRWRWr..
..rrrrrrrr..
.rWWWWWWWWr.
.rWWWWWWWWr.
.rbbWWWbbWr.
.rweWWWweWr.
..WWWWWWWW..
..dWWmmWW...
...dWWWW....
.....dW.....
''')
    torso = '''
qrrrrrrr
qrWrrWrr
qrrrrrrr
qWWrrWWr
.qWWWWr.
.qWWWWr.
.qrrrrr.
qrrrrrrr
qWWWWWWW
qWWWWWWW
'''
    B = Body(variants(head, pal), TH=10, LH=10, tw=8, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#d0407a', pants='#f4f0f4',
             shoe='#d0407a', skin='#f4f0f4', sleeve='#f4f0f4', glove='#d0407a', sleeve_len=4, hax=6,
             skirt=dict(len=3, col='#f4f0f4', flare=1, trim='#d0407a'), front=stand_fx('#ff90c0'), kind='stand')
    P = stand_poses(B)
    P['idle'] = ([P['idle'][0][0], P['idle'][0][2]], 5, 'loop')
    return B, P, ['idle', 'cast', 'block', 'hurt']


# ---------------------------------------------------------------- 辣妹（Red Hot Chili Pepper）：金黄色，鸟喙一样的尖嘴，浑身带电
def rhcp():
    pal = P_(y='#f8d030', Y='#fff090', s='#f8d030', d='#c89a18', k='#8a6410', e='#2a2a30', w='#ffffff', m='#8a3a10', o='#f08a20')
    head = H('''
...yyyyyy....
..yYYYYYyy...
.yYyyyyyyyy..
.dyyyyyyyyy..
.dybbyyybby..
.dyweyyyweyoo
.dyyyyyyyoooo
..dyyyyyyoo..
..dyymmyy....
...dyyyy.....
.....dy......
''')
    torso = '''
dyyyyyyy
dyYyyyyy
dyyykyyy
dyykykyy
dyyyyyyy
dyykykyy
dyyyyyyy
dkkkkkkk
dyyyyyy.
'''

    def sparks(cv, B, P, ctx):
        # 身边的小电火花（每帧位置不同）
        seed = (hash(str(sorted(P.items(), key=lambda kv: kv[0])[:3])) % 5)
        for i, (dx, dy) in enumerate(((-8, 20), (9, 24), (-6, 8), (8, 12), (0, 30))):
            if (i + seed) % 2 == 0:
                x, y = X(dx + ctx['bx']), Y(dy + ctx['by'])
                cv.put(x, y, '#ffffff')
                cv.put(x + 1, y - 1, '#a0e8ff')
                cv.put(x - 1, y + 1, '#a0e8ff')

    B = Body(variants(head, pal), TH=9, LH=9, tw=8, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#f8d030', pants='#f8d030',
             shoe='#c89a18', skin='#f8d030', sleeve='#f8d030', glove='#f8d030', hax=6,
             front=chain(sparks, stand_fx('#fff060')), kind='stand')
    P = stand_poses(B)
    A = B.arm_len
    fl = P['idle'][0][0]
    P['idle'] = (P['idle'][0], 8, 'loop')
    P['dash'] = ([dict(fl, lean=3, bx=1, aN=((-2, -1), (-5, 0)), aF=((2, -2), (6, -1))), dict(fl, lean=3, bx=2, dy=1, aN=((-2, -1), (-5, 1)), aF=((2, -2), (6, 0)))], 12, 'loop')
    P['punch'] = (P['punch'][0], 14, 'oneshot')
    P['hand'] = ([dict(fl, lean=1, aF=(A + 3, 0), fistF=3, item='palm'), dict(fl, lean=2, aF=(A + 5, 1), fistF=3, item='palm')], 10, 'loop')
    P['rust'] = ([dict(fl, head='h', lean=-1, drop=2, aN=(0, -A + 2), aF=(1, -A + 2))], 1, 'static')
    sheet_names = ['idle', 'dash', 'punch', 'hurt', 'hand', 'rust']
    return B, P, sheet_names


def rhcp_sheet():
    B, P, names = rhcp()
    sh = Sheet('rhcp', '辣妹', kind='stand')
    for n in names:
        frs, fps, kind = P[n]
        fr = [draw(B, f) for f in frs]
        if n == 'rust':
            # 生锈、没电：整个压成锈褐色
            fr = [f.recolor({'#f8d030': '#9a6a3a', '#fff090': '#b8864a', '#c89a18': '#6a4424', '#8a6410': '#4a2e18'}) for f in fr]
        sh.add(n, fr, fps, kind)
    sh.body = B
    return sh


# ---------------------------------------------------------------- 回音 ACT1：绿色、大脑袋带一根尖角、长尾巴尖上一个钩、身后两个小轮子
E1 = dict(g='#3aa66a', G='#74d090', D='#1e6a44', y='#e8c040', Y='#b08a20', e='#ffffff', k='#1a1a24', r='#d04a4a', w='#f4f4e0')
E1_A = '''
.......................GGG....
..........D...........GgggG...
.........DgD.........Ggg.ggG..
........DgGgDD.......gg...gg..
......DDgGGggggD.....gg...gg..
....DDggGGggggggD....gg...Dg..
...DggGGgggeekgggD...Dg...Dg..
..DggGgggggeekggggD...Dg..yY..
..DgggggggggggggggD...Dgg.Yy..
..DgggggggyyyyyggggDDDDgg.....
...DgggggyYYYYYygggggggg......
....DDgggggyyygggggggDD.......
......DDggggggggDDDDD.........
.......kkDgD..DgDkk...........
.......kk.g....g.kk...........
'''
E1_SHOOT = '''
..............................GGG..........
..........D..............GGGGGgggy.........
.........DgD.........GGGGggggggggYy........
........DgGgDD....GGGgggggDDDD.............
......DDgGGggggDGGggggDDDD.................
....DDggGGggggggggggDD.....................
...DggGGgggeekggggDD.......................
..DggGgggggeekggggD........................
..DgggggggggggggggD........................
..DgggggggrrrrrggggD.......................
...DgggggrkkkkkrgggD.......................
....DDgggggrrrgggDD........................
......DDggggggggD..........................
.......kkDgD..DgDkk........................
.......kk.g....g.kk........................
'''
EGG = dict(W='#f4f0e0', w='#d8d0b8', k='#3a3428', g='#3aa66a', G='#74d090', D='#1e6a44', e='#ffffff', b='#1a1a24')
EGG_FR = ['''
....WWWW....
..WWWWWWWW..
.WWWWWWWWWW.
.WWWWWWWWWw.
WWWWWWWWWWww
WWWWWWWWWWww
WWWWWWWWWwww
WWWWWWWWWwww
.WWWWWWWwww.
.wWWWWWwwww.
..wwwwwwww..
....wwww....
''', '''
....WWWW....
..WWWWkWWW..
.WWWWkWWWWW.
.WWWWWkWWWw.
WWWWWWkWWWww
WWWWWkWWWWww
WWWWWWWWWwww
WWWWWWWWWwww
.WWWWWWWwww.
.wWWWWWwwww.
..wwwwwwww..
....wwww....
''', '''
....WWWW....
..WWkWkWWW..
.WWWWkWWkWW.
.WWkWWkWkWw.
WWWWkWkWWWww
WWWWWkWWkWww
WWWWWWkWWwww
WWWWWWWWWwww
.WWWWWWWwww.
.wWWWWWwwww.
..wwwwwwww..
....wwww....
''', '''
...W......W.
..WW..DD..WW
.WWW.DggD.WW
.....DgGgD..
W..DDgGeebgD
WW.DgggeebgD
WWWkDggggDkw
WWWWkkDDkkww
.WWWWWWwwww.
.wWWWWWwwww.
..wwwwwwww..
....wwww....
''', '''
.....DD.....
....DggD....
...DDgGgD...
..DggGGeebD.
..DgggGeebgD
W.DggggggggD
WWkDggggggDw
WWWkkDDDDkww
.WWWWWWwwww.
.wWWWWWwwww.
..wwwwwwww..
....wwww....
''']


def echoes1():
    sh = Sheet('echoes1', '回音 ACT1', kind='stand')
    sh.add('idle', [raw_frame(E1_A, E1, 0, d) for d in (0, 1, 2, 1)], 6, 'loop')
    sh.add('shoot', [raw_frame(E1_A, E1, -1, 1), raw_frame(E1_SHOOT, E1, 6, 1), raw_frame(E1_SHOOT, E1, 5, 1)], 12, 'oneshot')
    sh.add('block', [raw_frame(E1_A, E1, -2, 0)], 1, 'static')
    sh.add('hurt', [raw_frame(E1_A, dict(E1, e='#1a1a24'), -3, 2)], 1, 'static')
    sh.add('hatch', [raw_frame(EGG_FR[i], EGG, 0, 0) for i in (0, 1, 2, 3, 4)] + [raw_frame(E1_A, E1, 0, 0)], 8, 'oneshot')
    sh.face = (OX - 13, OY - 14)
    return sh


# ---------------------------------------------------------------- 回音 ACT2：浅绿、宽扁的脑袋像蝠鲼、尾巴尖是个箭头
E2 = dict(g='#8ad060', G='#c0f090', D='#3a7a30', k='#1e2a1a', y='#e8c040', e='#f0e060', b='#1a1a24', w='#ffffff')
E2_A = '''
..........DDDD..........
.....DDDDDggggDDDDD.....
..DDDgGGGgggggggGGgDDD..
.DgGGGggggyggggggGGGgD..
DgGggggbbggggbbggggGgD..
.DggggbeebggbeebgggggD..
..DDggggggggggggggDD....
....DDDgggggggDDD.......
......DgggggggD.........
.....DgDggggDgD.........
....Dg.DggggD.gD........
....D..DggggD..D........
.......DgDDgD...........
......DgD..DgD..........
......kk....kkk.........
.............kkkk.......
...............kkk......
................kkyy....
.................yyyy...
..................yy....
'''


def echoes2():
    sh = Sheet('echoes2', '回音 ACT2', kind='stand')
    sh.add('idle', [raw_frame(E2_A, E2, 0, d) for d in (0, 1, 2, 1)], 6, 'loop')
    sh.add('punch', [raw_frame(E2_A, E2, 2, 1), raw_frame(E2_A, E2, 5, 0)], 12, 'oneshot')
    sh.add('cast', [raw_frame(E2_A, E2, 0, 2), raw_frame(E2_A, dict(E2, e='#ffffff', y='#fff8a0'), 1, 3)], 6, 'loop')
    sh.add('block', [raw_frame(E2_A, E2, -2, 0)], 1, 'static')
    sh.add('hurt', [raw_frame(E2_A, dict(E2, e='#1a1a24'), -3, 2)], 1, 'static')
    sh.face = (OX - 9, OY - 19)
    return sh


# ---------------------------------------------------------------- 珍珠果酱：番茄模样的小东西（一小群）
PJ = dict(r='#e04a30', R='#f8905a', y='#f0d050', g='#4a9a3a', G='#2e6a28', e='#ffffff', k='#1a1a24')
PJ_A = '''
...g.........g......
..GgG...g...GgG.....
.rrRrr.GgG.rrRrr....
rRekerrrRrrrekeRr...
ryyyyrrekerryyyyr...
.rkkr.ryyyr.rkkr....
.g..g..rkr..g..g....
'''


def pearljam():
    sh = Sheet('pearljam', '珍珠果酱', kind='stand')
    sh.add('idle', [raw_frame(PJ_A, PJ, 0, d) for d in (0, 1, 0, -0)], 6, 'loop')
    sh.face = (OX - 9, OY - 12)
    return sh


# ---------------------------------------------------------------- 丰收：巴掌大，金黄 + 紫的条纹身子，白色面罩，四条细腿
HV = dict(y='#f0c840', Y='#fff0a0', p='#7a4ab0', W='#f4f4f0', u='#3a7ad0', k='#1a1a24', d='#b08a20')
HV_A = '''
..ypypy..
.yYpypyy.
.WWWWWWy.
.WuWWuWp.
.WWWWWWy.
.dypypyd.
..k...k..
.k.....k.
'''
HV_B = '''
..ypypy..
.yYpypyy.
.WWWWWWy.
.WuWWuWp.
.WWWWWWy.
.dypypyd.
...k.k...
...k.k...
'''
HV_C = '''
...ggg...
..ypypy..
.yYpypyy.
.WWWWWWy.
.WuWWuWp.
.WWWWWWy.
.dypypyd.
..k...k..
'''


def harvest():
    pal = dict(HV, g='#f0d050')
    sh = Sheet('harvest', '丰收', kind='stand')
    sh.add('idle', [raw_frame(HV_A, pal), raw_frame(HV_A, pal, 0, 1)], 4, 'loop')
    sh.add('walk', [raw_frame(HV_A, pal), raw_frame(HV_B, pal)], 10, 'loop')
    sh.add('carry', [raw_frame(HV_C, pal), raw_frame(HV_C, pal, 0, 1)], 10, 'loop')
    sh.add('hurt', [raw_frame(HV_B, dict(pal, u='#1a1a24'), -1, 2)], 1, 'static')
    sh.face = (OX - 8, OY - 12)
    return sh


# ---------------------------------------------------------------- 枯萎穿心攻击：蓝绿色的小坦克，正面一张银色骷髅脸
SH = dict(t='#3a8aa0', T='#6ac0d0', D='#1e5266', W='#e8ecf0', w='#a8b0bc', k='#1a1a24', r='#d04040', g='#4a4a54', G='#2a2a30')
SH_A = '''
......tttttt........
....ttTTTTTTtt......
...tTTTttttttttD....
..tTTttttttttttWW...
..ttttttttttttWWWW..
.DtttttttttttWkWkW..
.DttttttttttDWWWWW..
.DDttttttttDDwkwkw..
gGgGgGgGgGgGgGgGgG..
GgGgGgGgGgGgGgGgGg..
.gGgGgGgGgGgGgGgG...
'''
SH_BOOM = '''
......tttttt........
....ttTTTTTTtt......
...tTTTttttttttD....
..tTTttttttttttrr...
..ttttttttttttrrrr..
.DtttttttttttrkrkW..
.DttttttttttDrrrrW..
.DDttttttttDDwkwkw..
gGgGgGgGgGgGgGgGgG..
GgGgGgGgGgGgGgGgGg..
.gGgGgGgGgGgGgGgG...
'''


def sha():
    sh = Sheet('sha', '枯萎穿心攻击', kind='stand')
    alt = dict(SH, g='#2a2a30', G='#4a4a54')
    sh.add('idle', [raw_frame(SH_A, SH), raw_frame(SH_A, SH, 0, 1)], 2, 'loop')
    sh.add('walk', [raw_frame(SH_A, SH), raw_frame(SH_A, alt, 1, 0), raw_frame(SH_A, SH, 0, 1)], 10, 'loop')
    sh.add('boom', [raw_frame(SH_BOOM, SH), raw_frame(SH_BOOM, dict(SH, t='#c05a4a', T='#f09a70'), 0, 1)], 8, 'loop')
    sh.add('hurt', [raw_frame(SH_A, SH, -2, 2)], 1, 'static')
    sh.add('stuck', [raw_frame(SH_A, SH, 0, -2), raw_frame(SH_A, alt, 0, -2)], 3, 'loop')
    sh.face = (OX - 4, OY - 13)
    return sh


# ---------------------------------------------------------------- 猫草：花盆里一株长着猫脸的植物（灰紫色的花瓣是猫头，青绿的叶子是爪）
SC = dict(p='#8a82a8', P='#b8b0d0', D='#5a5478', y='#f0e060', k='#1a1a24', g='#3aa08a', G='#6ad0b0', d='#1e6a5a',
          o='#b0603a', O='#d08050', r='#e89ab0', w='#ffffff')
SC_A = '''
....DD.....DD....
...DpPD...DPpD...
...DpPPDDDPPpD...
..DppPPPPPPPppD..
..DpykppppykppD..
..DpyyppppyyppD..
...DppprrpppD....
....DDppppDD.....
.gg...dggd...gg..
gGGg..dggd..gGGg.
.gGGggdggdggGGg..
..ggGGgggGGGgg...
....ddgggdd......
....OOOOOOOO.....
....oOooooOo.....
.....oooooo......
'''
SC_SLEEP = '''
.................
.................
....DD.....DD....
...DpPDDDDDPpD...
..DppPPPPPPPppD..
..DpkkppppkkppD..
..DpppprrppppD...
...DDppppppDD....
.gg...dggd...gg..
gGGg..dggd..gGGg.
.gGGggdggdggGGg..
..ggGGgggGGGgg...
....ddgggdd......
....OOOOOOOO.....
....oOooooOo.....
.....oooooo......
'''
SC_PUFF = '''
....DD.....DD....
...DpPD...DPpD...
...DpPPDDDPPpD...
..DppPPPPPPPppD..
..DpykppppykppD..
..DpyyppppyyppD....ww
...DpppkkpppD....wwwww
....DDpkkpDD......www
.gg...dggd...gg..
gGGg..dggd..gGGg.
.gGGggdggdggGGg..
..ggGGgggGGGgg...
....ddgggdd......
....OOOOOOOO.....
....oOooooOo.....
.....oooooo......
'''


def straycat():
    sh = Sheet('straycat', '猫草', kind='stand')
    sh.add('idle', [raw_frame(SC_A, SC), raw_frame(SC_A, SC, 0, 0), raw_frame(SC_A, SC, 1, 0), raw_frame(SC_A, SC, 0, 0)], 4, 'loop')
    sh.add('puff', [raw_frame(SC_A, SC), raw_frame(SC_PUFF, SC, 2, 0)], 6, 'oneshot')
    sh.add('shoot', [raw_frame(SC_PUFF, SC, 2, 0)], 1, 'static')
    sh.add('sleep', [raw_frame(SC_SLEEP, SC)], 1, 'static')
    sh.face = (OX - 8, OY - 15)
    return sh


# ---------------------------------------------------------------- Cheap Trick：趴在人背上的小鬼，土黄色的大脑袋、蓝眼睛、一口尖牙
CT = dict(o='#a88a4a', O='#d0b470', D='#6a5428', u='#4a6ae0', w='#ffffff', k='#1a1a24', r='#8a2a2a', g='#5a6a3a')
CT_A = '''
...DDDDDD....
..DoOOOooD...
.DoOoooooD...
.DouuoouuoD..
.DoukooukoD..
.DooooooooD..
.DkwkwkwkwD..
.DrrrrrrrrD..
..DwkwkwkD...
..DooooooD...
.gDooggooDg..
g.DogggoD..g.
..DD...DD....
'''
CT_TALK = '''
...DDDDDD....
..DoOOOooD...
.DoOoooooD...
.DouuoouuoD..
.DoukooukoD..
.DooooooooD..
.DkwkwkwkwD..
.DrrrrrrrrD..
.DrrrrrrrrD..
..DwkwkwkD...
.gDooggooDg..
g.DogggoD..g.
..DD...DD....
'''
CT_LOOK = '''
...DDDDDD....
..DoOOOooD...
.DoOoooooD...
.DoouuoouuD..
.DooukooukD..
.DooooooooD..
.DkwkwkwkwD..
.DrrrrrrrrD..
..DwkwkwkD...
..DooooooD...
.gDooggooDg..
g.DogggoD..g.
..DD...DD....
'''


def cheaptrick():
    sh = Sheet('cheaptrick', 'Cheap Trick', kind='stand')
    sh.add('idle', [raw_frame(CT_A, CT), raw_frame(CT_A, CT, 0, 1)], 3, 'loop')
    sh.add('talk', [raw_frame(CT_A, CT), raw_frame(CT_TALK, CT)], 6, 'loop')
    sh.add('look', [raw_frame(CT_LOOK, CT)], 1, 'static')
    sh.face = (OX - 8, OY - 14)
    return sh


CAST = {
    'thehand': ('轰炸空间', thehand), 'echoes1': ('回音 ACT1', echoes1), 'echoes2': ('回音 ACT2', echoes2), 'pearljam': ('珍珠果酱', pearljam),
    'rhcp': ('辣妹', rhcp_sheet), 'heavensdoor': ('天堂之门', heavensdoor), 'harvest': ('丰收', harvest),
    'killerqueen': ('杀手皇后', killerqueen), 'sha': ('枯萎穿心攻击', sha), 'echoes3': ('回音 ACT3', echoes3),
    'cinderella': ('灰姑娘', cinderella), 'highway': ('公路之星', highway), 'straycat': ('猫草', straycat),
    'cheaptrick': ('Cheap Trick', cheaptrick),
}
build = make_build(CAST, kind='stand')

if __name__ == '__main__':
    import sys
    main(CAST, build, sys.argv)
