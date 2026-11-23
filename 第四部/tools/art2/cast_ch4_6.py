# 第4–6章人物（重画）：乔瑟夫（老年）、音石明、船上的人（SPW 工作人员、船长、渔民、船员）、静·乔斯达；
#   岸边露伴；矢安宫重清、吉良吉影（原本的样子）、杉本铃美、阿诺德。
#   头照 TV 动画第四部设定画；身高照 第四部/docs/比例标准.md。动作名、帧数、fps 和旧图集一致。
from px import Cv, OUTLINE, shade, rows
from castlib import (P_, H, GAKURAN8x9, Body, Sheet, draw, poses, variants, grid_part, chain, X, Y, CW, CH, OX, OY, raw_frame,
                     make_build, main)


# ---------------------------------------------------------------- 乔瑟夫·乔斯达（79 岁，驼背，约 172 cm）：卡其色礼帽、白胡子、黄毛衣、拄拐
def _joseph_items(cv, B, P, ctx):
    it = P.get('item', 'cane')
    hN, hF = ctx.get('handN'), ctx.get('handF')
    if it == 'cane' and hN:
        x, y = X(hN[0]) + 1, Y(hN[1])
        cv.vline(x, y, Y(0) + 1, '#6a4a2a')
        cv.hline(x - 1, x + 1, y, '#8a6a3a')
    elif it == 'camera' and hF:
        x, y = X(hF[0]), Y(hF[1])
        cv.rect(x - 1, y - 3, x + 4, y, '#2a2a30')
        cv.rect(x + 1, y - 2, x + 2, y - 1, '#8ab0d0')
        cv.put(x + 4, y - 4, '#d0d0d8')
    elif it == 'baby' and hF:
        x, y = X(hF[0]) - 3, Y(hF[1]) - 3
        cv.rect(x, y, x + 6, y + 4, '#f4b8c8')
        cv.rect(x + 4, y - 2, x + 7, y + 1, '#f8e0d0')
        cv.hline(x + 4, x + 7, y - 2, '#d8d8f0')
        cv.hline(x + 5, x + 7, y, '#1a1a24')


def joseph_old():
    pal = P_(t='#c8a868', T='#e0c488', k='#8a6e3a', W='#e8e8ec', G='#a8acb8', e='#3a8a8a',
             y='#e0c060', q='#a88a38', n='#6a4a2a', Y='#f0d880')
    head = H('''
....tttttttt....
...tTTTTTTTTt...
...tTTTTTTTTt...
...kkkkkkkkkk...
.tttttttttttttt.
ttttttttttttttttt
..GWssssssss....
..GWsbbbsbbbs...
..GWswesssweS...
..GWdsssssss....
...WWWWWmWWW....
....WWWWWWW.....
.....WWWWW......
''')
    torso = '''
qyysyyyy
qyyyyyyy
qyYyyYyy
qyyyyyyy
qyYyyYyy
qyyyyyyy
qyyyyyyy
qnnnnnnn
'''
    B = Body(variants(head, pal), TH=8, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#e0c060', pants='#7a5a34',
             shoe='#4a3020', hax=8, front=_joseph_items)
    P = poses(B)
    A = B.arm_len
    cane = dict(aN=((-1, -2), (1, -A + 2)))                    # 近手拄拐（手在身前）
    P['idle'] = ([dict(cane, lean=1), dict(cane, lean=1, dy=-1)], 2, 'loop')
    P['walk'] = ([dict(f, lean=1, aN=((-1, -2), (1 + (i % 2), -A + 2))) for i, f in enumerate(P['walk'][0])], 5, 'loop')
    P['point'] = ([dict(cane, lean=1, aF=(A + 1, 1))], 1, 'static')
    P['camera'] = ([dict(item='camera', lean=1, aF_front=True, aF=((2, -1), (3, 2)), aN=((1, -2), (3, 1))),
                    dict(item='camera', lean=1, aF_front=True, aF=((2, -1), (3, 3)), aN=((1, -2), (3, 2)), hy=-1)], 4, 'oneshot')
    P['shock'] = ([dict(cane, head='s', lean=-1, aF=((2, -1), (3, 2))), dict(cane, head='s', lean=-1, dy=1, aF=((2, 0), (3, 3)))], 4, 'loop')
    P['hurt'] = ([dict(P['hurt'][0][0], item='none')], 1, 'static')
    P['hold'] = ([dict(item='baby', lean=1, aF_front=True, aF=((2, -2), (3, -3)), aN=((1, -3), (3, -3))),
                  dict(item='baby', lean=1, dy=-1, aF_front=True, aF=((2, -2), (3, -3)), aN=((1, -3), (3, -3)))], 2, 'loop')
    P['lie'] = ([dict(head='h', lie='back', item='none')], 1, 'static')
    return B, P, ['idle', 'walk', 'point', 'camera', 'shock', 'hurt', 'hold', 'lie']


# ---------------------------------------------------------------- 音石明（约 175 cm）：紫色长发、脸上闪电纹、藏青外套钉金色十字、橙色裤子
def _guitar(cv, B, P, ctx):
    if P.get('item') != 'guitar':
        return
    h = ctx.get('handF')
    if not h:
        return
    x, y = X(h[0]), Y(h[1])
    cv.line(x - 2, y + 1, x + 8, y - 5, '#8a5a34')              # 琴颈
    cv.rect(x - 7, y, x - 1, y + 4, '#f4f0e0')                   # 琴身（白）
    cv.rect(x - 6, y + 1, x - 3, y + 3, '#2a2a30')
    cv.hline(x - 7, x - 1, y + 4, '#c8c4b0')
    cv.put(x + 8, y - 6, '#2a2a30')


def otoishi():
    pal = P_(v='#7a5ac0', V='#a888e8', k='#4a3488', e='#2a2a40', z='#e8c040', j='#28306a', q='#161c44', g='#ffd040',
             o='#e8782a', O='#b85a18')
    head = H('''
....vvvvvvv....
..vvVVVVVvvvv..
.vvvVvvvvvvvvv.
.vvvvvvvvvvvvv.
vvvvvvvvvvvvvv.
vvvvvvsvsvvvvv.
vvvvssssssssv..
vvvvsbbbsbbbs..
vvvkszeSsswes..
vvvkdsweSswes..
vvv.dsssssss...
vvv..dssmmss...
vv....ddsss....
''')
    torso = '''
qjjoojjj
qjgooggj
qjjoojjj
qjgjjjgj
qjjjjjjj
qjgjjjgj
qjjjjjjj
qjjjjjjj
qOOOOOOO
'''
    hair = grid_part('''
vvv
vvv
vVv
vvv
.vv
.vv
..v
''', -1, 12, 'head')
    B = Body(variants(head, pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#28306a', pants='#e8782a',
             shoe='#3a2a34', hax=8, back=hair, front=_guitar)
    P = poses(B)
    A = B.arm_len
    P['run'] = (P['run'][0], 12, 'loop')
    P['guitar'] = ([dict(item='guitar', lean=-1, aF=((2, -2), (4, -3)), aN=((-1, -2), (-2, -4))),
                    dict(item='guitar', lean=-1, head='r', aF=((2, -2), (4, -3)), aN=((-1, -3), (-1, -5)), dy=1)], 6, 'oneshot')
    return B, P, ['idle', 'walk', 'run', 'guitar', 'hurt', 'down', 'guard', 'dodge']


# ---------------------------------------------------------------- 船上的人（约 172 cm）：同一个身板，换帽子、衣服、肤色
def _crew(hat, hat2, top, top2, pants, skin=('#f6c49a', '#d8946c'), hair='#3a2a1e', beard=None, stripe=None, glasses=False, band=None):
    pal = P_(s=skin[0], d=skin[1], c=hat, C=hat2, k=hair, e='#2a2018', j=top, q=shade(top, -0.35), J=top2, u=beard or skin[0],
             G='#1a1a24', n=band or hat)
    eyes = '.kksGGGsGGGs...' if glasses else '.kksweSsswes...'
    head = H('''
....cccccccc....
..cccccccccccc..
.cCCCCCCCCCCCCc.
.nnnnnnnnnnnnnnn
.kkssssssssss...
.kksbbbssbbbs...
''' + eyes + '''
..kdsweSsswes...
..dduussssuu....
...duuummuus....
....duuuuuu.....
......dus.......
''')
    if stripe:
        torso = '\n'.join(('qJJJJJJJ' if i % 2 else 'qjjjjjjj') for i in range(8))
    else:
        torso = '''
qjjssjjj
qjjjsjjj
qjjjjjjj
qjJjjjJj
qjjjjjjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
'''
    B = Body(variants(head, pal), TH=8, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top=top, pants=pants,
             shoe='#3a2a22', skin=skin[0], hax=8)
    P = poses(B)
    return B, P, ['idle', 'walk', 'talk', 'hurt']


def crew_oto():
    return _crew('#3a4a7a', '#5a6aa0', '#3a4a7a', '#3a4a7a', '#2a3458')


def spw_a():
    # SPW 财团的工作人员：白色连体工作服、白帽、戴眼镜
    return _crew('#f0f0ea', '#ffffff', '#f0f0ea', '#d04040', '#e0e0d8', glasses=True)


def captain():
    # 船长：白制服、白大檐帽（黑帽檐）、灰白络腮胡
    return _crew('#f4f4ee', '#ffffff', '#f4f4ee', '#e8c040', '#2a3458', hair='#b8b8c0', beard='#c8c8d0', band='#1a1a24')


def fisher():
    # 渔民：晒黑、头上包白毛巾、深蓝背心
    return _crew('#f0f0ea', '#ffffff', '#2a4a6a', '#2a4a6a', '#5a5a44', skin=('#d89a68', '#a86a40'), beard='#b88050')


def crew_a():
    return _crew('#2a3458', '#3a4a7a', '#f0f0ea', '#3a5ab0', '#2a3458', stripe=True)


def crew_b():
    return _crew('#d04a3a', '#f07a5a', '#f0f0ea', '#d04a3a', '#3a3a44', stripe=True, skin=('#e8b088', '#c08058'))


def crew_c():
    return _crew('#3a8a5a', '#5ab07a', '#e8e0c0', '#e8e0c0', '#4a4a3a', hair='#1a1a20', beard='#8a6a48')


# ---------------------------------------------------------------- 静·乔斯达：透明的婴儿（看得见的只有帽子、墨镜和粉色连体衣）
SZ = dict(c='#d8d8f4', C='#f0f0ff', k='#1a1a24', p='#f4b8c8', P='#fcd8e0', q='#d090a4', s='#f8e0d0', m='#c8506a', g='#b8e8b0')
SZ_A = '''
....cCCc.....
...cCCCCc.c..
..cCCCCCCcc..
..ccccccccc..
..kkkkskkkk..
..kkkkskkkk..
...sssmsss...
..pppPPpppp..
.ppPPPPPPppp.
.sppPPPPppps.
..qppppppq...
..gg....gg...
'''
SZ_CRY = '''
....cCCc.....
...cCCCCc.c..
..cCCCCCCcc..
..ccccccccc..
..kkkkskkkk..
..kkkkskkkk..
...ssmmmss...
..pppmmmppp..
sppPPPPPPpps.
.pppPPPPppp..
..qppppppq...
..gg....gg...
'''


def shizuka():
    sh = Sheet('shizuka', '静·乔斯达')
    sh.add('idle', [raw_frame(SZ_A, SZ), raw_frame(SZ_A, SZ, 0, 1)], 2, 'loop')
    sh.add('cry', [raw_frame(SZ_CRY, SZ), raw_frame(SZ_CRY, SZ, 1, 0)], 6, 'loop')
    sh.face = (OX - 8, OY - 14)
    return sh


# ---------------------------------------------------------------- 岸边露伴（175 cm）：墨绿色头发、锯齿纹发带、笔尖耳环、紫上衣配绿背带
def _pen(cv, B, P, ctx):
    if P.get('item') != 'pen':
        return
    h = ctx.get('handF')
    if h:
        x, y = X(h[0]), Y(h[1])
        cv.line(x + 1, y, x + 3, y - 3, '#e8e8f0')
        cv.put(x + 1, y + 1, '#1a1a24')


def rohan():
    pal = P_(g='#2e6a48', G='#4a9a68', k='#1a4630', z='#b8e860', Z='#f4f4e0', e='#2a8a5a', y='#ffd040',
             v='#b060c0', V='#d088e0', q='#7a3a90', l='#8ad060', W='#f0f0ea')
    head = H('''
...g..g...g....
..gg.gGg.gg.g..
.gGggGGgGGgGg..
.ggGGGGGGGGgg..
.zZzZzZzZzZzZz.
.gzZzZzZzZzZz..
.gggssssssss...
.ggsbbbsbbbs...
.gysswesswes...
..gdswesswes...
..ddsssssss....
...dsssmmss....
....ddssss.....
......dds......
''')
    torso = '''
qvlvvlv
qvlvvlv
qvlvvlv
qvlllvv
qvvvvvv
qvVvvVv
qvvvvvv
qvvvvvv
qvvvvvv
'''
    B = Body(variants(head, pal), TH=9, LH=8, tw=7, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#b060c0', pants='#f0f0ea',
             shoe='#f0f0ea', hax=7, coat=dict(len=3, col='#b060c0'), cuff='#8ad060', front=_pen)
    P = poses(B)
    A = B.arm_len
    P['run'] = (P['run'][0], 12, 'loop')
    P['pose'] = ([dict(aN=((-2, -2), (-1, -A + 2)), aF=((2, 1), (1, 5)), lean=-1), dict(aN=((-2, -2), (-1, -A + 2)), aF=((2, 1), (1, 6)), lean=-1, dy=-1)], 3, 'loop')
    P['shock'] = ([P['shock'][0][0], dict(P['shock'][0][0], dy=1)], 4, 'loop')
    P['write'] = ([dict(item='pen', aF=((2, -1), (5, 1))), dict(item='pen', aF=((2, -1), (6, 3)), head='t'), dict(item='pen', aF=((2, -1), (4, 4)))], 6, 'loop')
    return B, P, ['idle', 'walk', 'run', 'point', 'pose', 'shock', 'hurt', 'dodge', 'guard', 'kneel', 'write', 'down']


# ---------------------------------------------------------------- 矢安宫重清（“重千”，矮胖，约 150 cm）：光头上一圈小疙瘩、圆滚滚的身子、绿校服镶金边
def shigechi():
    pal = P_(e='#1a1a24', g='#2f6a48', q='#1c4630', y='#e8c040', n='#d8946c')
    head = H('''
...n.n.n.n.n....
..nsssssssssn...
.nsssssssssssn..
.ssssssssssssss.
.sssssssssssssss
.ssbbbssssbbbsss
.ssweSssssweSsss
.dsssssssssssss.
.dssssmmmmsssss.
..dsssssssssss..
...ddsssssss....
''')
    torso = '''
qgggygggggg
qggygygggggg
qgggygggggg
qgyyyyyyygg
qgggggggggg
qggggggggg.
'''
    B = Body(variants(head, pal), TH=6, LH=5, tw=10, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#2f6a48', pants='#28583c',
             shoe='#4a3020', hax=8, hy=5 + 6 - 1, shoe_h=1, hip=1)
    P = poses(B)
    P['cry'] = ([P['cry'][0][0]], 1, 'static')
    return B, P, ['idle', 'walk', 'run', 'hurt', 'down', 'talk', 'crawl', 'cry']


# ---------------------------------------------------------------- 吉良吉影（原本的样子，175 cm）：金发后梳、淡紫西装、绿条纹衬衫、骷髅纹领带
def kira():
    pal = P_(y='#e8d070', Y='#fff0a8', k='#a88a38', e='#3a5aa0', v='#b8a0d8', V='#d8c8f0', q='#7a68a0', g='#5a9a5a', G='#3a6a3a',
             t='#2a2040', W='#f0f0f0')
    head = H('''
....yyyyyyyy...
..yyYYYYYYyyy..
.yyYyyYyyYyyy..
.yyyyyyyyyyyy..
.yyyykkkkkkyy..
.yykssssssss...
.yysbbbssbbbs..
.yksswesssweS..
..kdswesssweS..
..ddsssssssss..
...dssssmmss...
....ddsssss....
......dds......
''')
    torso = '''
qvvgtgvv
qvvgtgvv
qvvGtGvv
qvvgtgvv
qvvvtvvv
qvvvvvvv
qvVvvvVv
qvvvvvvv
qvvvvvvv
'''
    B = Body(variants(head, pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#b8a0d8', pants='#a890c8',
             shoe='#3a2a34', hax=8, cuff='#5a9a5a')
    P = poses(B)
    A = B.arm_len
    P['point'] = (P['point'][0], 6, 'oneshot')
    P['pose'] = ([dict(aN=((-2, -2), (-1, -A + 2)), aF=((2, -1), (4, 2))), dict(aN=((-2, -2), (-1, -A + 2)), aF=((2, -1), (4, 3)), head='t')], 3, 'oneshot')
    P['throw'] = (P['throw'][0], 6, 'oneshot')
    return B, P, ['idle', 'walk', 'point', 'pose', 'laugh', 'hurt', 'throw', 'punch', 'down']


# ---------------------------------------------------------------- 杉本铃美（16 岁，约 160 cm）：粉色短发、发带、粉色无袖连衣裙系蝴蝶结
def reimi():
    pal = P_(p='#f08aa8', P='#f8b4c8', k='#c05a7a', e='#b04a7a', m='#d0506a', y='#f8e070', r='#f8c8d8', R='#fce4ec', q='#d898ac',
             W='#ffffff')
    head = H('''
....ppppppp....
..ppPPPPPpppp..
.pyyyyyyyyyypp.
.ppppppppppppp.
pppppppppppppp.
ppppppspppsppp.
pppkssssssssp..
ppkksbbsssbbs..
ppkksweSsswes..
.pkkssssssss...
..k.dssssmss...
.....ddssss....
.......dds.....
''')
    torso = '''
qrrsrrr
qrrrrrr
qrRrrRr
qrrrrrr
qrrrrrr
qrrWWrr
qrrrrrr
'''
    B = Body(variants(head, pal), TH=7, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#f8c8d8', pants='#f8c8d8',
             shoe='#f8f8f8', hax=8, hip=1, sleeve_len=0, skirt=dict(len=4, col='#f8c8d8', flare=2, trim='#f08aa8'),
             bare=dict(sock='#f8c8d8', sock_h=3), cuff=None)
    P = poses(B)
    return B, P, ['idle', 'walk', 'cheer', 'down', 'wave']


# ---------------------------------------------------------------- 阿诺德：铃美的大狗（肩高约 70 cm）
AR = dict(b='#8a6a48', B='#a88860', D='#5a4228', k='#1a1a24', w='#ffffff', r='#b03a3a', n='#2a2018')
AR_STAND = '''
.................DD.....
................DbbDDD..
...............DbBbbbbD.
D..............DbbkbbbnD
bD............DbbbbbbbD.
.bD..DDDDDDDDDbbbbbDDD..
.DbDDbBBBBBBBbbbbbD.....
..DbbbBBBBBBbbbbbbD.....
..DbbbbbbbbbbbbbbD......
..DbbbbbbbbbbbbbD.......
..DbbDDDDDDDbbbD........
..DbD.Db....DbD.........
..DbD.Db....DbD.........
..DbD.Db....DbDb........
..DD..DD....DD.D........
'''
AR_RUN = '''
.................DD.....
................DbbDDD..
D..............DbBbbbbD.
bDD............DbbkbbbnD
.bbD..........DbbbbbbbD.
..DbDDDDDDDDDDbbbbbDDD..
..DbbbBBBBBBBbbbbbD.....
..DbbbBBBBBBbbbbbbD.....
..DbbbbbbbbbbbbbbD......
.DbbbbbbbbbbbbbbbD......
DbbDDDDDDDDDDbbbbbD.....
bD...........D..DbbD....
D................DbbD...
..................DD....
........................
'''
AR_SIT = '''
.............DD.........
............DbbDDD......
...........DbBbbbbD.....
...........DbbkbbbnD....
..........DbbbbbbbD.....
..........DbbbbbDD......
.........DbbbbbD........
........DbBBbbbD........
.......DbBBBbbbD........
......DbbBBbbbbD........
.....DbbbbbbDbbD........
D....DbbbbbbDbbD........
bD..DbbbbbbbDbbD........
.bDDbbbbbbDDDbbDb.......
..DDDDDDDDD.DDD.D.......
'''
AR_BITE = '''
.................DD.....
................DbbDDDD.
...............DbBbbbbbD
D..............DbbkbwwwD
bD............DbbbbbrrD.
.bD..DDDDDDDDDbbbbbwwwD.
.DbDDbBBBBBBBbbbbbDDDD..
..DbbbBBBBBBbbbbbbD.....
..DbbbbbbbbbbbbbbD......
..DbbbbbbbbbbbbbD.......
..DbbDDDDDDDbbbD........
..DbD.Db....DbD.........
..DbD.Db....DbD.........
..DbD.Db....DbDb........
..DD..DD....DD.D........
'''


def arnold():
    sh = Sheet('arnold', '阿诺德')
    sh.add('idle', [raw_frame(AR_STAND, AR), raw_frame(AR_STAND, AR, 0, 0)], 2, 'loop')
    sh.add('run', [raw_frame(AR_RUN, AR, 0, 1), raw_frame(AR_STAND, AR, 1, 0),
                   raw_frame(AR_RUN, AR, 1, 2), raw_frame(AR_STAND, AR, 0, 0)], 10, 'loop')
    sh.add('sit', [raw_frame(AR_SIT, AR)], 1, 'static')
    sh.add('bite', [raw_frame(AR_STAND, AR, 1, 0), raw_frame(AR_BITE, AR, 3, 0)], 6, 'loop')
    sh.add('walk', [raw_frame(AR_STAND, AR, 0, 0), raw_frame(AR_RUN, AR, 0, 0),
                    raw_frame(AR_STAND, AR, 1, 0), raw_frame(AR_RUN, AR, 1, 0)], 10, 'loop')
    sh.face = (OX - 2, OY - 15)
    return sh


CAST = {
    'joseph_old': ('乔瑟夫·乔斯达', joseph_old), 'otoishi': ('音石明', otoishi), 'crew_oto': ('船员', crew_oto),
    'spw_a': ('SPW 工作人员', spw_a), 'captain': ('船长', captain), 'fisher': ('渔民', fisher),
    'crew_a': ('船员', crew_a), 'crew_b': ('船员', crew_b), 'crew_c': ('船员', crew_c), 'shizuka': ('乔斯达·静', shizuka),
    'rohan': ('岸边露伴', rohan),
    'shigechi': ('矢安宫重清', shigechi), 'kira': ('吉良吉影', kira), 'reimi': ('杉本铃美', reimi), 'arnold': ('阿诺德', arnold),
}
build = make_build(CAST)

if __name__ == '__main__':
    import sys
    main(CAST, build, sys.argv)
