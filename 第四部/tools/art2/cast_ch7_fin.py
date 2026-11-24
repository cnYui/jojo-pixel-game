# 第7章–终章人物（重画）：辻彩、川尻浩作（换脸后的吉良）、裁缝店老板；吉良吉广、大柳贤、川尻忍；
#   支仓未起隆、喷上裕也、川尻早人、护士；钢田一丰大、宫本辉之辅；乙雅三；终章的吉良（头发后梳的最终样子）、女急救员。
#   头照 TV 动画第四部设定画；身高照 第四部/docs/比例标准.md。动作名、帧数、fps 和旧图集一致。
from px import Cv, OUTLINE, shade, rows
from castlib import (P_, H, GAKURAN8x9, Body, Sheet, draw, poses, variants, grid_part, chain, X, Y, CW, CH, OX, OY, raw_frame,
                     make_build, main)


# ---------------------------------------------------------------- 辻彩（约 165 cm）：金色长发低马尾、粉色连衣裙、宽腰封
def aya():
    pal = P_(y='#e8c870', Y='#fff0a8', k='#b08a3a', e='#3a8a8a', m='#d03a5a', p='#f4b8d0', P='#fcd8e4', q='#c888a4', n='#4a2a44',
             r='#8a3a5a')
    head = H('''
....yyyyyyy....
..yyYYYYYyyyy..
.yyyYyyyyyyyyy.
.yyyyyyyyyyyyy.
yyyyyyyyyyyyyy.
yyyyyysyysyyy..
yyykssssssssy..
yykksbbsssbbs..
yykksweSsswes..
.ykkssssssss...
.yk.dssssmss...
.y...ddssss....
.y.....dds.....
''')
    torso = '''
qppsspp
qpppspp
qpPpppp
qpppppp
nnnrnnn
nrnnnrn
nnnrnnn
qpppppp
'''
    tail = grid_part('''
yy
yy
yY
yy
yy
.y
.y
''', -1, 13, 'head')
    B = Body(variants(head, pal), TH=8, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#f4b8d0', pants='#f4b8d0',
             shoe='#d03a5a', hax=8, hip=1, sleeve_len=2, skirt=dict(len=5, col='#f4b8d0', flare=2), bare=dict(), back=tail)
    P = poses(B)
    return B, P, ['idle', 'walk', 'talk', 'hurt', 'down']


# ---------------------------------------------------------------- 川尻浩作的脸的吉良（175 cm）：黑发几绺垂下来、白西装、青绿条纹衬衫、紫领带
def _kira_body(hair, hair_l, hair_k, head, suit='#f2f0ea', suit_d='#b8b8c0', shirt='#3aa08a', shirt_d='#247060', tie='#5a3a90',
               eye='#2a2a40', want=None):
    pal = P_(h=hair, H=hair_l, k=hair_k, e=eye, v=suit, V=shade(suit, 0.3), q=suit_d, g=shirt, G=shirt_d, t=tie)
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
    B = Body(variants(H(head), pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top=suit, pants=shade(suit, -0.06),
             shoe='#3a2a34', hax=8, cuff=shirt)
    P = poses(B)
    A = B.arm_len
    P['point'] = (P['point'][0], 6, 'oneshot')
    P['pose'] = ([dict(aN=((-2, -2), (-1, -A + 2)), aF=((2, -1), (4, 2))), dict(aN=((-2, -2), (-1, -A + 2)), aF=((2, -1), (4, 3)), head='t')], 3, 'oneshot')
    P['throw'] = (P['throw'][0], 8, 'oneshot')
    return B, P, want or ['idle', 'walk', 'punch', 'throw', 'pose', 'laugh', 'hurt', 'point', 'down']


def kawajiri():
    return _kira_body('#2a2634', '#4a4660', '#16141e', '''
....hhhhhhhh...
..hhHHHHHHhhh..
.hhHhhHhhHhhh..
.hhhhhhhhhhhh..
.hhhhhhkhkhhh..
.hhkshsshsshs..
.hhsbbbssbbbs..
.hksswesssweS..
..kdswesssweS..
..ddsssssssss..
...dssssmmss...
....ddsssss....
......dds......
''')


def fin_kira():
    # 终章：头发往后梳起、鬓角带灰白条纹的最终样子；衬衫换深色
    return _kira_body('#3a3038', '#8a8490', '#1c161e', '''
...hhhhhhhhh...
.hhHhHhHhHhhh..
hhhHhHhHhHhhh..
hhhhhhhhhhhhh..
.hhhhkkkkkkhh..
.hHkssssssss...
.hHsbbbssbbbs..
.hksswesssweS..
..kdswesssweS..
..ddsssssssss..
...dssssmmss...
....ddsssss....
......dds......
''', shirt='#4a4660', shirt_d='#2a2634', tie='#8a3a5a', want=['idle', 'walk', 'point', 'hurt', 'down', 'pose', 'laugh', 'punch', 'throw'])


# ---------------------------------------------------------------- 裁缝店老板（约 165 cm）：谢顶、两边灰发、眼镜、背心、脖子上搭一条皮尺
def tailor():
    pal = P_(g='#a8a8b4', G='#787888', e='#2a2a30', L='#c8e0f0', W='#f0f0ea', q='#c8c8c0', n='#6a4a34', N='#8a6448', y='#f0d040')
    head = H('''
................
....ssssssss....
..ssssssssssss..
.gssssssssssss..
.ggsssssssssss..
.ggsssssssssss..
.ggsbbbssbbbs...
.gGsLeLssLeLs...
..GdsLssssLss...
..ddssssssss....
...dsssmmmss....
....ddsssss.....
......dds.......
''')
    torso = '''
qWynnyWW
qWynnyWW
qWynnnWW
qWnnnnWW
qWnNnnWW
qWnnnnWW
qWnNnnWW
qWnnnnWW
'''
    B = Body(variants(head, pal), TH=8, LH=7, tw=8, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#f0f0ea', pants='#4a4a54',
             shoe='#3a2a22', hax=8)
    P = poses(B)
    return B, P, ['idle', 'walk', 'hurt', 'down', 'talk']


# ---------------------------------------------------------------- 吉良吉广（照片里的幽灵，小个子老人）：谢顶、两鬓白发翘起、山羊胡、茶色和服外褂
def yoshihiro():
    pal = P_(W='#f0f0f4', G='#b8bcc8', e='#5a8ab0', u='#5a5a66', o='#a8884a', O='#c8a868', q='#6a5428', g='#5a8a5a', t='#3a4a7a')
    head = H('''
................
....ssssssss....
.WWssssssssss.W.
WWWsssssssssssWW
.WGsssssssssss..
.WGsbbbssbbbs...
..GsweSsswes....
..dsweSsswes....
..ddssssssss....
...dssummuss....
....ddsuuss.....
......dus.......
''')
    torso = '''
qogWtWgo
qoogtgoo
qooogooo
qooooooo
qoOooOoo
qooooooo
qooooooo
'''
    B = Body(variants(head, pal), TH=7, LH=6, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#a8884a', pants='#5a5a66',
             shoe='#3a2a22', hax=8, coat=dict(len=3, col='#a8884a', trim='#5a8a5a'))
    P = poses(B)
    return B, P, ['idle', 'walk', 'hurt', 'down', 'throw', 'talk']


# ---------------------------------------------------------------- 大柳贤（11 岁，约 140 cm）：灰白头发别绿色发夹、黑色无袖上衣、短裤
def oyanagi():
    pal = P_(g='#c8ccd8', G='#eef0f6', k='#8a8ea0', c='#5ab060', e='#3a3a44', n='#2a2a34', q='#16161c', r='#c8ccd8')
    head = H('''
....ggggggg....
..ggGGGGGgggg..
.gggGcgcggggg..
.ggggggggggg...
gggggggggggg...
ggggssgsgssg...
.ggsssssssss...
.gksweSssweS...
.gksweSssweS...
..ksssssssss...
..dssssmmss....
...ddsssss.....
.....dds.......
''')
    torso = '''
qnnsnnn
qnnnnnn
qnrnnrn
qnnnnnn
qnnnnnn
qnnnnnn
'''
    B = Body(variants(head, pal), TH=6, LH=5, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#2a2a34', pants='#3a3a48',
             shoe='#e8e8ee', hax=7, hip=1, sleeve_len=0, bare=dict(top=2, sock='#e8e8ee', sock_h=1), shoe_h=1)
    P = poses(B)
    return B, P, ['idle', 'walk', 'run', 'hurt', 'talk']


# ---------------------------------------------------------------- 川尻忍（约 160 cm）：红棕色头发侧扎马尾、白上衣、长裙
def shinobu():
    pal = P_(r='#a8483a', R='#d0705a', k='#6a2a22', v='#7a5ab0', e='#6a4a3a', m='#d0606a', W='#f4f0ea', q='#c8c4bc', n='#5a6a8a')
    head = H('''
....rrrrrrr....
..rrRRRRRrrrr..
.rrrRrrrrrrrrr.
.rrrrrrrrrrrrr.
rrrrrrrrrrrrrr.
rrrrrrsrrsrrr..
rrrkssssssssr..
rrkksbbsssbbs..
rvkksweSsswes..
rr.kssssssss...
rr..dssssmss...
.r...ddssss....
.r.....dds.....
''')
    torso = '''
qWWsWWW
qWWsWWW
qWWWWWW
qWWWWWW
qWWWWWW
qWWWWWW
qnnnnnn
'''
    B = Body(variants(head, pal), TH=7, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#f4f0ea', pants='#5a6a8a',
             shoe='#3a2a34', hax=8, hip=1, skirt=dict(len=5, col='#5a6a8a', flare=1), bare=dict())
    P = poses(B)
    return B, P, ['idle', 'walk', 'wave', 'talk']


# ---------------------------------------------------------------- 支仓未起隆（约 175 cm）：淡金色长发、尖耳朵、藏青制服、胸前一串金饰
def mikitaka():
    pal = P_(y='#f0e8b8', Y='#fffce0', k='#b8ac78', e='#8a6ac0', j='#28306a', q='#161c44', g='#e8a030', v='#7a5ab0')
    head = H('''
....yyyyyyy....
..yyYYYYYyyyy..
.yyyYyyyyyyyyy.
.yyyyyyyyyyyyy.
yyyyyyyyyyyyyy.
yyyyyssyssyyy..
yyykssssssssy..
yysksbbbsbbbs..
yyykssweSswes..
yyykdsweSswes..
yyy.dsssssss...
yyy..dssmmss...
yy....ddsss....
''')
    torso = '''
qjjjgjjj
qjjjgjjj
qjjgggjj
qjjjgjjj
qjjjgjjj
qvvvvvvv
qvvvvvvv
qjjjgjjj
qjjjjjjj
'''
    hair = grid_part('''
yyy
yyy
yYy
yyy
yyy
.yy
.yy
.yy
..y
''', -1, 12, 'head')
    B = Body(variants(head, pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#28306a', pants='#20265a',
             shoe='#3a2a34', hax=8, back=hair, cuff='#e8a030')
    P = poses(B)
    A = B.arm_len
    P['float'] = ([dict(dy=2, lN=(0, 1), lF=(1, 2), aN=((-2, -1), (-3, 1)), aF=((2, -1), (3, 1))),
                   dict(dy=3, lN=(0, 1), lF=(1, 2), aN=((-2, -1), (-3, 2)), aF=((2, -1), (3, 2)))], 3, 'loop')
    P['cmd'] = (P['cmd'][0], 4, 'loop')
    P['point'] = (P['point'][0], 4, 'oneshot')
    return B, P, ['idle', 'walk', 'hurt', 'down', 'dodge', 'guard', 'float', 'cmd', 'point']


# ---------------------------------------------------------------- 喷上裕也（约 178 cm）：黑色刺头、下巴上两道纹、白色长围巾、黑夹克
def yuya():
    pal = P_(k='#22202c', K='#444058', g='#8a8a98', e='#2a2a40', x='#5a5a70', W='#f4f4f0', q='#c0c0c8', j='#2a2a34', J='#16161c',
             y='#e8c040')
    head = H('''
...k..k..k.k...
..kk.kk.kkkk...
.kkkkKkkKkkkk..
.kkkkkkkkkkkk..
.gkkkkkkkkkkk..
.ggkksssssss...
.ggksbbbsbbbs..
.gkdssweSswes..
..gdssweSswes..
..ddssssssss...
...dsssmmmss...
....dxsxsss....
......dxs......
''')
    torso = '''
JjWWWWjj
JjjWWWjj
JjjWWjjj
JjyWWjyj
JjjWWjjj
JjjWWjjj
JjjjWjjj
Jjjjjjjj
Jjjjjjjj
'''
    B = Body(variants(head, pal), TH=9, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#2a2a34', pants='#22222c',
             shoe='#3a2a22', hax=8)
    P = poses(B)
    A = B.arm_len
    P['cmd'] = (P['cmd'][0], 4, 'loop')
    P['fight'] = ([dict(drop=1, aF=((2, -2), (4, 0)), aN=((0, -3), (3, -2)), fistF=3, lN=(-1, 0), lF=(2, 0)),
                   dict(drop=1, dy=-1, aF=((2, -2), (4, 1)), aN=((0, -3), (3, -1)), fistF=3, lN=(-1, 0), lF=(2, 0))], 4, 'loop')
    P['shock'] = ([P['shock'][0][0], dict(P['shock'][0][0], dy=1)], 4, 'loop')
    return B, P, ['idle', 'walk', 'hurt', 'down', 'dodge', 'guard', 'cmd', 'fight', 'kick', 'shock']


# ---------------------------------------------------------------- 川尻早人（11 岁，约 140 cm）：橙棕色齐耳短发、绿外套配橙背心、蓝短裤、背着书包
def hayato():
    pal = P_(o='#c8703a', O='#e89a5a', k='#8a4418', e='#6a3a2a', g='#5a9a5a', q='#3a6a3a', v='#f0a040', u='#3a6ac0', n='#2a6a4a',
             N='#1c4a34')
    head = H('''
....ooooooo....
..ooOOOOOoooo..
.oooOoooooooo..
.ooooooooooooo.
oooooooooooooo.
ooooossosooooo.
ooooosssssssoo.
oookswesssweso.
oookswesssweso.
.ookssssssssk..
.oo.dssssmss...
.....ddssss....
.......dds.....
''')
    torso = '''
qgvsvgg
qgvvvgg
qgvvvgg
qgvvvgg
qggvggg
uuuuuuu
'''
    pack = grid_part('''
nnn
nNn
nNn
nNn
nnn
''', -3, 1, 'torso')
    B = Body(variants(head, pal), TH=6, LH=5, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#5a9a5a', pants='#3a6ac0',
             shoe='#f0f0f0', hax=7, hip=1, bare=dict(top=2, sock='#f4f4f4', sock_h=1), back=pack, shoe_h=1)
    P = poses(B)
    return B, P, ['idle', 'walk', 'run', 'hurt', 'down', 'talk']


# ---------------------------------------------------------------- 护士（约 160 cm）
def nurse9():
    pal = P_(k='#3a2a24', K='#5a443a', e='#3a2a24', m='#d0606a', W='#f6f6f2', q='#c8ccd0', r='#d04a5a', c='#a8d0e8')
    head = H('''
.....WWWWWW....
....WWWrWWWW...
...kWWWWWWWWk..
..kkkkkkkkkkkk.
.kkkkkkkkkkkkk.
.kkkkksskssskk.
.kkkssssssssk..
.kkksbbsssbbs..
.kkksweSsswes..
..kkssssssss...
..k.dssssmss...
.....ddssss....
.......dds.....
''')
    torso = '''
qWWsWWW
qWWWWWW
qWWWcWW
qWWWWWW
qWWWWWW
qWWWWWW
qWWWWWW
'''
    B = Body(variants(head, pal), TH=7, LH=7, tw=7, arm_w=2, leg_w=2, pal=pal, torso=torso, top='#f6f6f2', pants='#f6f6f2',
             shoe='#f6f6f2', hax=8, hip=1, sleeve_len=3, skirt=dict(len=4, col='#f6f6f2', flare=0), bare=dict(skin='#f0e0d8'))
    P = poses(B)
    return B, P, ['idle', 'walk']


def paramedic():
    # 女急救员：白头盔、浅蓝灰的救护服、胸口红十字
    pal = P_(k='#3a2a24', e='#3a2a24', m='#d0606a', W='#f4f4f0', V='#c8ccd0', u='#b8c8d8', q='#8a9aac', r='#d03a3a')
    head = H('''
....WWWWWWW....
..WWWWWWWWWWW..
.WWWWWWWWWWWWW.
.WWWWWrWWWWWWW.
.VVVVVVVVVVVVVV
.kkkksskssskk..
.kkkssssssssk..
.kkksbbsssbbs..
.kkksweSsswes..
..kkssssssss...
..k.dssssmss...
.....ddssss....
.......dds.....
''')
    torso = '''
quususu
quuuuuu
quuruuu
qurrruu
quuruuu
quuuuuu
quuuuuu
'''
    B = Body(variants(head, pal), TH=7, LH=7, tw=7, arm_w=2, leg_w=3, pal=pal, torso=torso, top='#b8c8d8', pants='#a8b8c8',
             shoe='#3a3a44', hax=8)
    P = poses(B)
    return B, P, ['idle', 'walk']


# ---------------------------------------------------------------- 钢田一丰大（住在铁塔上，约 180 cm）：绿帽子、黑眼罩、绿背带裤、紫护肩、光着上身
def toyohiro():
    pal = P_(g='#6ab04a', G='#8ad068', k='#3e7a2a', q='#3e7a2a', n='#1a1a24', l='#f0e860', e='#f0e860', y='#e8c060', v='#7a4ab0', V='#9a6ad0',
             p='#d05a9a')
    head = H('''
....gggggggg....
..ggGGGGGGgggg..
.ggGggggggggggg.
.kkkkkkkkkkkkkkk
.yyssssssssss...
.yysssssssssss..
.yynnnnnnnnnns..
.ydnlnnnnnlnns..
..dssssssssss...
..ddssssssss....
...dsssmmmss....
....ddsssss.....
......dds.......
''')
    torso = '''
VggssggV
vgsssssg
qgsssssg
qggsdsgg
qggssggg
qggggpgg
qggggggg
qggggggg
qggggggg
'''
    B = Body(variants(head, pal), TH=9, LH=9, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#6ab04a', pants='#5a9a3e',
             shoe='#4a3020', hax=8, sleeve_len=0)
    P = poses(B)
    P['kick'] = (P['kick'][0], 6, 'oneshot')
    return B, P, ['idle', 'walk', 'hurt', 'down', 'kick', 'talk']


# ---------------------------------------------------------------- 宫本辉之辅（约 172 cm）：白色长发、深色皮肤、白外套棕护肩、黑衣上几道金链
def terunosuke():
    pal = P_(s='#a8704a', d='#7a4a2c', W='#eef0f4', V='#c0c4d0', k='#9a9eb0', e='#f0f0f0', w='#f0f0f0', m='#5a2a1a',
             c='#f4f2ec', q='#b8b6b0', o='#8a5a34', n='#22222c', g='#e8c040')
    head = H('''
....WWWWWWW....
..WWWWWWWWWWW..
.WWWVWWWWWWWWW.
.WWWWWWWWWWWWW.
WWWWWWWWWWWWWW.
WWWWWssWssWWW..
WWWkssssssssW..
WWkksbbbsbbbs..
WWkkssbesssbe..
WWkkssssssss...
WW..dsssmmss...
.W...ddssss....
.W.....dds.....
''')
    torso = '''
qocnnnco
qocngnco
qccnnncc
qccngncc
qccnnncc
qccngncc
qccnnncc
qccnnncc
'''
    hair = grid_part('''
WW
WW
WV
WW
.W
''', 0, 13, 'head')
    B = Body(variants(head, pal), TH=8, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#f4f2ec', pants='#22222c',
             shoe='#f4f2ec', skin='#a8704a', hax=8, coat=dict(len=5, col='#f4f2ec', open=(-1, 1), trim='#22222c'), back=hair)
    P = poses(B)
    return B, P, ['idle', 'walk', 'point', 'hurt', 'down', 'dodge', 'guard']


# ---------------------------------------------------------------- 乙雅三（约 173 cm）：橙棕色头发中间一条、两侧剃短留点、灰夹克、橄榄绿衬衫
def kinoto():
    pal = P_(o='#c8703a', O='#e89a5a', k='#8a4418', x='#b89a80', e='#5a4ab0', c='#b8b4ac', q='#8a867e', v='#7a8a4a')
    head = H('''
.....ooooo.....
....oOOOOoo....
...oooooooo....
..xsoooooooss..
.xsxssoooossss.
.sxsxsssssssss.
.xsxsbbbssbbbs.
.sxdsweSssweSs.
..xdsweSssweSs.
..ddssssssssss.
...dsswwwwwss..
....ddsssss....
......dds......
''')
    torso = '''
qccvvccc
qccvvccc
qcccvccc
qccccccc
qccccccc
qccccccc
qccccccc
qccccccc
'''
    B = Body(variants(head, pal), TH=8, LH=8, tw=8, arm_w=3, leg_w=3, pal=pal, torso=torso, top='#b8b4ac', pants='#5a5a66',
             shoe='#3a2a22', hax=8)
    P = poses(B)
    return B, P, ['idle', 'walk', 'talk']


CAST = {
    'aya': ('辻彩', aya), 'kawajiri': ('川尻浩作', kawajiri), 'tailor': ('裁缝店老板', tailor),
    'yoshihiro': ('吉良吉广', yoshihiro), 'oyanagi': ('大柳贤', oyanagi), 'shinobu': ('川尻忍', shinobu),
    'mikitaka': ('支仓未起隆', mikitaka), 'yuya': ('喷上裕也', yuya), 'hayato': ('川尻早人', hayato), 'nurse9': ('护士', nurse9),
    'toyohiro': ('钢田一丰大', toyohiro), 'terunosuke': ('宫本辉之辅', terunosuke), 'kinoto': ('乙雅三', kinoto),
    'fin_kira': ('吉良吉影', fin_kira), 'paramedic': ('女急救员', paramedic),
}
build = make_build(CAST)

if __name__ == '__main__':
    import sys
    main(CAST, build, sys.argv)
