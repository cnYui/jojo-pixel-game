# 第五部《黄金之风》反派：迪亚波罗 / 多比欧、暗杀小队七人、史克亚罗和提查诺、乔可拉特和塞可、祖凯罗、萨雷、波尔波。
from px import Cv, OUTLINE, shade, rows
from rig import Sheet, draw, grid_part, chain, fill_pinholes, X, Y, CW, CH, OX, OY
from castlib import P_, make_build, main
from kit5 import (b5, std, prop, line_prop, gun, guns_poses, stab_poses, pinstripe, bands, dots, VIL,
                  GUN_PAL, KNIFE)

KNIFE_PAL = dict(G='#e4e8f4', g='#8c92a8', k='#3a2418')


def knife():
    return prop('knife', KNIFE, 0, -2, KNIFE_PAL)


def stance(**kw):
    d = dict(lN=(-2, 0), lF=(2, 0))
    d.update(kw)
    return d


# ---------------------------------------------------------------- 迪亚波罗（191 cm）：粉色长发带墨绿斑点、绿瞳、紫唇、网衫、纹身、紫裤
def diavolo():
    pal = P_(F='#fa98c0', P='#e8609c', r='#a42c68', g='#1c5c46', e='#36a452', m='#8a46a6', s='#eec0a0', d='#bc8668',
             k='#1c1228', x='#3aa862', G='#e6c446', p='#62469e', j='#eec0a0', q='#bc8668')
    head = '''
......rrrrrr......
....rrFFPPPPrr....
...rPFPPgPPPPPr...
..rPPPPPPPPgPPPr..
.rPgPPPPPPPPPPgPr.
.rPPPPrPPPPrPPPPr.
.rPPrssbbbssbbbPr.
rPgPssswesssweSPr.
rPPPrdswesssweSPr.
rPPPrddsssssssSgr.
rgPPrdsssmmmssrPr.
rPPPr.dddssssd.Pr.
rPPgr...ddddd..Pr.
rPPPr..........gr.
rgPPr..........Pr.
.rPPr.........rr..
.rPr..............
'''
    torso = rows('''
dkssskssk
sskskssks
sssksssks
sskskskss
dksssksss
sssssssss
dssdsssds
xGxGxGxGx
qpppppppp
qpppppppp
''')
    hair = grid_part('''
rPPPr
rPgPr
rPPPr
.rgPr
.rPPr
..rr.
''', -1, 13)
    B = b5(191, head, pal, torso, '#eec0a0', '#62469e', '#2c2250', back=hair, skin='#eec0a0', sleeve='#eec0a0',
           wrist='#3aa862', shoulder=1, pat_arm=lambda k, i, n: '#2a5c60' if (k in (2, 3) and i >= 1) else None)

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([stance(lean=-1, head='n', aN=((-4, -1), (-7, -3)), aF=((5, -1), (8, -3)), hy=-1),
                      stance(lean=-1, dy=-1, head='r', aN=((-4, 0), (-7, -1)), aF=((5, 0), (8, -1)), hy=-1)], 2, 'loop'),
            'laugh': P['laugh'],
        }
    return std(B, ['idle', 'walk', 'pose', 'laugh', 'attack', 'hurt', 'down'], extra)


# ---------------------------------------------------------------- 威尼加·多比欧（170 cm）：粉发长辫、雀斑、紫色针织衫露腰、绿腰带，把青蛙当电话
def doppio():
    pal = P_(F='#fc9cc0', P='#ee70a2', r='#ac3c70', e='#8c5c18', f='#cc7c5c', J='#c47cda', G='#e8c24a', y='#3c9058',
             p='#56489e', j='#9448b2', q='#642c80')
    head = '''
.......rrrrr......
.....rrPPPPPrr....
....rPFFPPPPPPr...
...rPFPPPPPPrPPr..
..rPPPPPPPPrPPPr..
..rPPPPrrrrsPPPr..
..rPPrsbbbssbbbs..
..rPrsswesssweSs..
...rrdswesssweS...
....dsfsssssfsf...
....ddssssssmss...
.....dddsssssd....
.......dddd.......
'''
    torso = '''
qjjsssj
qJjjsjJ
qjJjjJj
qjjJJjj
qJjjjjJ
dssssss
yyyGyyy
qpppppp
'''
    braid = grid_part('''
...rP
..rPr
.rPr.
.rFr.
.rPr.
.rr..
.rPr.
..rFr
..rPr
.rPr.
.rr..
rr...
''', -2, 2)
    frog = prop('frog', '''
.g.g.
gwgwg
gGGGg
.ggg.
''', -2, -3, dict(g='#2c7c34', G='#6cd45c', w='#ffffff'))
    B = b5(170, head, pal, torso, '#9448b2', '#56489e', '#6a4eae', back=braid, front=frog, arm_w=2, cuff='#c47cda')

    def extra(B_, P):
        A = B_.arm_len
        return {
            # “嘟噜噜噜……喂？”把青蛙贴到耳边
            'call': ([dict(aF_front=True, aF=((5, -4), (4, 2)), aN=((-2, -2), (-1, -A + 2)), item='frog', head='t'),
                      dict(aF_front=True, aF=((5, -4), (4, 3)), aN=((-2, -2), (-1, -A + 2)), item='frog', head='n', dy=-1),
                      dict(aF_front=True, aF=((5, -4), (4, 2)), aN=((-2, -2), (-1, -A + 2)), item='frog', head='t', lean=1)], 5, 'loop'),
            'pose': ([dict(head='s', lean=-1, aF_front=True, aF=((6, -2), (7, 1)), aN=((-3, -2), (-4, 1)), lN=(-1, 0), lF=(1, 0)),
                      dict(head='s', lean=-1, dy=-1, aF_front=True, aF=((6, -1), (7, 3)), aN=((-3, -1), (-4, 3)), lN=(-1, 0), lF=(1, 0))], 6, 'loop'),
            'attack': P['kick'],
        }
    return std(B, ['idle', 'walk', 'call', 'pose', 'attack', 'hurt', 'down'], extra)


# ---------------------------------------------------------------- 里苏特·涅罗（185 cm）：黑兜帽挂金坠、银发、黑眼白红瞳、胸前交叉皮带、黑长衣、黑白横纹裤
def risotto():
    pal = P_(K='#342c3c', k='#18141e', S='#ccd2e2', v='#8c94ac', w='#14101c', e='#e82434', G='#e8a834', g='#9c641c',
             y='#6a4420', s='#e4b490', d='#ac7c60', j='#2c2634', q='#18141e')
    pal['S'] = '#ccd2e2'
    head = '''
......kkkkkkk.....
....kkKKKKKKKkk...
...kKKKKKKKKKKKk..
..kKKKKSSSSSSKKKk.
..kKKSSSvSSSSSSKk.
.kKKSSvSSSvSSSSSk.
.kKKSsbbbSssbbbSk.
.kKKKsswesssweSkk.
.kKKKdswesssweSk..
.kKKKddsssssssk...
.kKKkddssssmmsk...
.kKkG.dddssssd....
.Gkg....ddddd.....
GgG...........G...
'''
    torso = '''
qkssssskj
qjksssksj
qjsksksjj
qjsskssjj
qjsksksjj
qjksdsksj
qjsssssjj
qyyGGGyyy
qjwwwwwjj
qjkkkkkjj
'''
    pal.setdefault('x', '#000000')
    blades = prop('blades', '''
..G.....
.g...GG.
....g...
G.......
..gG..g.
.....G..
''', 3, -4, dict(G='#e8ecf8', g='#c4283c'))
    B = b5(185, head, pal, torso, '#2c2634', '#ece8f0', '#2a2430', chin=12, skin='#e4b490', front=blades,
           pat_leg=bands('#242028', 4, 2), coat=dict(len=8, col='#2c2634', flare=2, open=(-3, 2), trim='#463c52'),
           cuff='#463c52', shoulder=1)

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([stance(lean=-1, aF_front=True, aF=((5, -2), (5, 3)), aN=((-2, -2), (-1, -A + 2)), head='n'),
                      stance(lean=-1, dy=-1, aF_front=True, aF=((5, -1), (5, 4)), aN=((-2, -2), (-1, -A + 2)), head='r')], 2, 'loop'),
            # 金属制品：张开手，铁片凭空浮起
            'attack': ([stance(aF=(A + 3, 1), aN=((-2, -2), (-3, -2))),
                        stance(aF=(A + 3, 1), aN=((-2, -2), (-3, -2)), item='blades', head='r'),
                        stance(aF=(A + 3, 2), aN=((-2, -2), (-3, -2)), item='blades', head='r', lean=1)], 7, 'oneshot'),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 霍尔马吉欧（178 cm）：蓝灰短发、铆钉红背心、绿色系带内衫、酒红条纹裤
def formaggio():
    pal = P_(H='#6674a4', h='#363e66', y='#e8a848', e='#2c8c4a', J='#e06a44', j='#c04630', t='#3a9462', g='#a8e0b8',
             n='#5a3020', Z='#e8c048', p='#8c3444', q='#822c24', s='#f0b88c', d='#c08060')
    head = '''
......hhhhhh......
....hhHHHHHHhh....
...hHHHhHHHhHHHy..
..hHHhHHHhHHHHHy..
..hHHHHhhHHHhHhy..
..hHHhsssssssssh..
..hHhssbbbssbbbs..
..hhsssswesssweS..
...dddsswesssweS..
...ddsssssssssd...
....ddsssmmmss....
.....dddsssssd....
.......ddddd......
'''
    head = head.replace('..hhsssswesssweS..', '..hhssswesssweSs..').replace('...dddsswesssweS..', '...ddsswesssweS...')
    torso = '''
qJtttJJj
qJgtgtJj
qJtgtgJj
qJgtgtJj
qJJttJJj
dsstsssd
dssdssds
nnnnZnnn
qppppppp
'''
    B = b5(178, head, pal, torso, '#c04630', '#8c3444', '#3a62c0', skin='#f0b88c', sleeve_len=3, wrist='#3a9462',
           pat_leg=pinstripe('#c06676'), front=knife())

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([stance(drop=2, lean=1, head='t', aF=((3, -2), (5, 2)), aN=((-3, -2), (-1, -A + 3)), item='knife'),
                      stance(drop=2, lean=1, head='r', dy=-1, aF=((3, -1), (5, 3)), aN=((-3, -2), (-1, -A + 3)), item='knife')], 4, 'loop'),
            'attack': stab_poses(B_, P),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 伊鲁佐（188 cm）：深棕长发扎成几束（紫发绳）、红瞳、白短外套露腰、绿腰带、棕裤
def illuso():
    pal = P_(H='#6a4a3c', K='#422c2a', k='#201418', u='#9458c4', t='#f2c4a0', e='#d02434', J='#eef0f6', j='#d4d8e6', G='#3c9458',
             y='#1e5430', p='#9a5c30', q='#9ca2ba', s='#f2c4a0', d='#c08c6c')
    head = '''
......kkkkkk......
....kkHHHHHHkk....
...kHHKKKKHHHHk...
..kHKKKKKKKKKKHk..
..kKKKKKHKKKKKKKk.
.kKKKHssssKKsssKk.
.kKKsssbbbssbbbsk.
.kKKssswesssweSKk.
.kKKdsswesssweSk..
.kKKddssssssssK...
.uuK.ddsssmmsk....
.kKk..dddsssd.....
uukk...ddddd......
kKk.k.............
.k..k.............
'''
    torso = '''
qJuttuJj
qJJutJJj
qJJuuJJj
qJuJJuJj
uuuuuuuu
dsssssss
dssdssds
dsssssss
yGGGGGGy
qppppppp
'''
    mirror = prop('mirror', '''
.yyy.
yMMwy
yMwMy
yMMMy
.yyy.
..y..
''', 1, -4, dict(y='#d8a838', M='#78c8e8', w='#ffffff'))
    B = b5(188, head, pal, torso, '#d4d8e6', '#9a5c30', '#468c44', skin='#f2c4a0', cuff='#9458c4', front=mirror)

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([stance(lean=-1, head='t', aF_front=True, aF=((6, -3), (8, 0)), aN=((-3, -2), (-1, -A + 2))),
                      stance(lean=-1, head='r', dy=-1, aF_front=True, aF=((6, -2), (8, 2)), aN=((-3, -2), (-1, -A + 2)))], 4, 'loop'),
            # 镜中人：举起镜子
            'attack': ([stance(aF=((3, -2), (6, 0)), aN=((-2, -2), (-3, -2)), item='mirror'),
                        stance(aF=(A + 2, 1), aN=((-2, -2), (-3, -2)), item='mirror', head='r', lean=1),
                        stance(aF=(A + 3, 1), aN=((-2, -2), (-3, -2)), item='mirror', head='t', lean=1)], 7, 'oneshot'),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 普罗修特（178 cm）：金发扎髻、深蓝细格西装、黄领、敞胸挂金坠
def prosciutto():
    pal = P_(F='#fff4b0', L='#eed878', y='#b49438', e='#2c62cc', Y='#f6d232', u='#5c2c78', g='#f0bc34',
             l='#7c74ac', j='#2a2446', q='#161230', x='#120e24', s='#f4c8a4', d='#c49070')
    head = '''
......yyyyy.......
....yyFFFFFyyy....
...yFFLLLLLLLLy...
yyyLLyLLLyLLLyLy..
yLLyLsyssssyssLy..
yLyyLsssssssssss..
.yFLsssbbbssbbbs..
yLyLssswesssweSs..
yLyyddswesssweS...
.yy.ddsssssssss...
....ddsssssmmss...
......ddsssssd....
.......ddddd......
'''
    torso = '''
qjYuuuYj
qjYsssYj
qljYsYlj
qljYgYlj
qljjgjlj
qljjgjlj
qljjgglj
xxxxggxx
qljjjjlj
'''
    B = b5(178, head, pal, torso, '#2a2446', '#2a2446', '#1c1830', skin='#f4c8a4', pat_leg=pinstripe('#6a629a'),
           pat_arm=pinstripe('#6a629a'), coat=dict(len=2, col='#2a2446', flare=1, open=(0, 0)), cuff='#f6d232')

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([stance(lean=-1, aF_front=True, aF=((3, -4), (0, -1)), aN=((-3, -2), (0, -A + 2))),
                      stance(lean=-1, dy=-1, aF_front=True, aF=((3, -4), (0, 0)), aN=((-3, -2), (0, -A + 2)), head='t')], 3, 'loop'),
            # 壮烈成仁：伸手抓住对方
            'attack': ([stance(lean=-1, aF=((-1, -2), (2, 0)), aN=((-2, -2), (-3, -2))),
                        stance(lean=2, bx=1, head='r', aF=(A + 4, 1), fistF=3, aN=((-3, -1), (-5, 0)), drop=1),
                        stance(lean=1, head='r', aF=(A + 3, 0), fistF=3, aN=((-2, -2), (-4, -1)))], 9, 'oneshot'),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 贝西（165 cm）：光头顶一撮菠萝叶、没下巴、毛领、黄长背心、黑底粉心紧身衣、钓竿
def pesci():
    pal = P_(g='#2c8434', G='#68cc50', e='#2c6c44', F='#7c4a40', f='#4c2a28', c='#d8a860', P='#e862a8', k='#241c2c',
             y='#8c6030', Y='#f0c848', j='#d8a860', q='#9c7438', s='#f2c8a6', d='#c4906e')
    head = '''
......g..gg.......
.....gGg.gGGg.g...
......gGGGGGgGg...
.......gGGGGGg....
.....dsssgGsssd...
....dssssssssssd..
...dsssssssssssd..
...dssssbbssssbbd.
..ddssswesssweSsd.
..ddsssssssssssd..
..dddsssssmmmssd..
..ddddsssssssssd..
...ddddssssssdd...
'''
    torso = '''
FFFFFFFFFF
fFFFFFFFFf
FFfkPkkfFF
cckPPPkPcc
cckkPkkkcc
cckPkkkPcc
cyyyYyyycc
cckkPkkkcc
cckkkkkPcc
'''
    def rod_draw(cv, B_, P, ctx, which):
        h = ctx.get('handF')
        it = P.get('item')
        if not h or it not in which:
            return
        hx, hy = h
        if it == 'rod_back':
            tip = (hx - 13, hy + 9)
            line = [tip, (tip[0] - 3, tip[1] - 6), (tip[0] - 2, tip[1] - 11)]
        elif it == 'rod':
            tip = (hx + 13, hy + 7)
            line = [tip, (tip[0] + 8, tip[1] - 5), (tip[0] + 11, 2)]
        else:
            tip = (hx + 9, hy + 12)
            line = [tip, (tip[0] + 12, 3)]
        cv.line(X(hx), Y(hy), X(tip[0]), Y(tip[1]), '#7c4c24')
        cv.line(X(hx), Y(hy) + 1, X(tip[0]), Y(tip[1]) + 1, '#3c2412')
        pts = line
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            cv.line(X(x0), Y(y0), X(x1), Y(y1), '#dce4f4')
        ex, ey = pts[-1]
        cv.put(X(ex), Y(ey) + 1, '#c8ccd8')
        cv.put(X(ex) - 1, Y(ey) + 1, '#c8ccd8')
        cv.put(X(ex) - 1, Y(ey), '#c8ccd8')
    def rod_behind(cv, B_, P, ctx):
        # 手的位置要先算出来才能画：这一层在手臂之前，用姿势里的手位推
        if P.get('item') != 'rod_back':
            return
        sh = ctx['shF']
        spec = P['aF'][-1]
        ctx2 = dict(ctx, handF=(sh[0] + spec[0], sh[1] + spec[1]))
        rod_draw(cv, B_, P, ctx2, ('rod_back',))

    def rod_front(cv, B_, P, ctx):
        rod_draw(cv, B_, P, ctx, ('rod', 'rod_pull'))
    B = b5(165, head, pal, torso, '#d8a860', '#241c2c', '#3a2a24', TH=9, LH=6, skin='#f2c8a6', sleeve='#f2c8a6',
           wrist='#241c2c', pat_leg=dots('#e862a8', 3, 2, 6, 2), coat=dict(len=3, col='#d8a860', flare=1, open=(-1, 1)),
           back=rod_behind, front=rod_front, shoulder=0)

    def extra(B_, P):
        A = B_.arm_len
        return {
            'idle': ([dict(drop=1, lean=1), dict(drop=1, lean=1, dy=-1)], 2, 'loop'),
            # 缩着脖子叫“大哥！”
            'pose': ([dict(drop=2, lean=1, head='s', aF_front=True, aF=((5, -3), (5, 0)), aN=((-2, -3), (1, -1))),
                      dict(drop=2, lean=1, dy=-1, head='h', aF_front=True, aF=((5, -3), (5, -1)), aN=((-2, -3), (1, -2)))], 5, 'loop'),
            # 沙滩男孩：甩竿
            'attack': ([stance(lean=-1, aF=((-1, 1), (-2, 3)), aN=((-1, -3), (1, -2)), item='rod_back'),
                        stance(lean=1, head='r', aF=((4, -1), (7, 1)), aN=((-1, -3), (2, -2)), item='rod'),
                        stance(lean=-1, head='r', drop=1, aF=((3, -3), (5, -1)), aN=((-1, -3), (3, -3)), item='rod_pull')], 5, 'oneshot'),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 梅洛尼（174 cm）：淡紫长发盖半张脸、紫色眼罩、紫黑露腰紧身衣、长手套、笔记本电脑
def melone():
    pal = P_(F='#ead8fc', L='#c8a6ee', v='#8a68b8', M='#5c3484', e='#2cb0a8', u='#8c4cb4', y='#5c3484', Y='#c8a6ee',
             j='#2e2044', q='#1a1028', s='#f6ccac', d='#c89478')
    head = '''
......vvvvvv......
....vvLLFFLLvv....
...vLLFLLLLLLLv...
..vLLFLLLvLLLLLv..
..vLFLLLvLLLLLLLv.
.vLLLLLvsLLLLLLLv.
.vLLLLvssssLLLLLv.
.vLLLMMMMMMMLLLLv.
.vLLLMMweMMMLLLLv.
.vLLLddssssLLLLv..
.vLLvddsssmmLLv...
.vLLv.ddssdLLv....
..vLv..ddd.vLv....
..vv........v.....
'''
    torso = '''
ssqjjqss
qjjuujjj
qjujjujj
qjjuujjj
dssjjssd
dssjjssd
yyyyYyyy
qjjjjjjj
qjujjujj
'''
    laptop = prop('laptop', '''
kkkkkk.
kccCck.
kcCcck.
kccCck.
kkkkkkk
.KKKKKKK
''', -1, -6, dict(k='#2c2c3c', K='#5c5c74', c='#58d8c8', C='#c8fff4'))
    B = b5(174, head, pal, torso, '#2e2044', '#2e2044', '#1c1430', chin=12, skin='#f6ccac', sleeve='#f6ccac', glove='#34244c',
           pat_arm=lambda k, i, n: '#34244c' if k >= 3 else None, pat_leg=dots('#8c4cb4', 2, 3, 8, 3), front=laptop)

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([stance(lean=-1, aF_front=True, aF=((6, -3), (7, 1)), aN=((-3, -2), (0, -A + 2)), head='t'),
                      stance(lean=-1, dy=-1, aF_front=True, aF=((6, -2), (8, 3)), aN=((-3, -2), (0, -A + 2)), head='r')], 3, 'loop'),
            # 敲电脑指挥“娃娃脸”
            'attack': ([dict(aF=((2, -3), (5, -2)), aN=((1, -4), (5, -4)), item='laptop'),
                        dict(aF=((2, -3), (5, -2)), aN=((1, -4), (6, -3)), item='laptop', head='t'),
                        dict(aF=((2, -3), (5, -2)), aN=((1, -4), (5, -3)), item='laptop', head='r', lean=1)], 7, 'loop'),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 加丘（171 cm）：浅蓝卷发、红框眼镜、浅色高领衫、深色条纹裤、红鞋
def ghiaccio():
    pal = P_(C='#a6e8fc', t='#4ca8d8', R='#e02c5c', e='#2c3c9c', j='#e2eef6', J='#b4ccdc', y='#2c2c48', Y='#b4bccc',
             q='#a4bcd0', s='#f4c8a8', d='#c49072')
    head = '''
......tttttt......
....ttCCtCCCtt....
...tCtttCCtttCCt..
..tCtCCtCtCCCtCCt.
..tCtCttCtCtttCCt.
.tCCttCCCttCCCCCt.
.tCtsssssssssssCt.
.tCtsRRRRssRRRRt..
.tCdsRweRRRRweRs..
..tddRRRRssRRRRs..
...ddsssssmmsss...
.....ddssssssd....
.......dddddd.....
'''
    torso = '''
qjJJJJjj
qjjjJjjj
qjjjJjjj
qjjjJjjj
qjjjJjjj
qjjjJjjj
qjjjjjjj
yyyyYyyy
qyyyyyyy
'''
    B = b5(171, head, pal, torso, '#e2eef6', '#2c2c48', '#b82c3c', skin='#f4c8a8', pat_leg=pinstripe('#6c6c94'),
           cuff='#b4ccdc')

    def extra(B_, P):
        A = B_.arm_len
        return {
            # 暴躁：跺脚大吼
            'pose': ([stance(head='r', lean=1, aF_front=True, aF=((6, -2), (8, 2)), aN=((-4, -1), (-6, 2)), lF=((2, -4), (3, 3))),
                      stance(head='r', lean=2, drop=1, aF_front=True, aF=((6, -4), (7, -2)), aN=((-4, -2), (-6, -1)))], 8, 'loop'),
            'attack': P['kick'],
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 史克亚罗（182 cm）：橘红卷发扎深蓝头巾、深蓝条纹无袖连身衣、护腕
def squalo():
    pal = P_(O='#f27048', o='#b03c28', n='#323a7c', N='#54609c', e='#2c52c4', j='#34407c', q='#1e2450', y='#a8acc4',
             Y='#e4e8f4', s='#eab088', d='#ba7c5c')
    head = '''
......oOOo.oo.....
....oOOOOOOOOOo...
...oOnnNNnnnnnOo..
..oOnnnnnnnnnnnOo.
.oOOnnnnnnnnnnnOOo
.oOOnssssssssssOo.
.oOoOssbbbssbbbOo.
oOOoOsswesssweSOo.
oOoOddswesssweSo..
.oOoddsssssssss...
..o.ddssssmmss....
.....dddsssssd....
.......dddd.......
'''
    torso = '''
sjjsssjs
sjjjsjjs
qjNjjNjj
qjNjjNjj
qjNjjNjj
qjNjjNjj
yyyyYyyy
qjNjjNjj
qjNjjNjj
'''
    B = b5(182, head, pal, torso, '#34407c', '#34407c', '#26244c', skin='#eab088', sleeve='#eab088', wrist='#a8acc4',
           pat_leg=pinstripe('#6c78b0'), pat_arm=lambda k, i, n: '#a8acc4' if k == 2 else None, front=knife())

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([stance(drop=2, lean=2, head='r', aF=((3, -2), (6, 0)), aN=((-3, -2), (-4, -4))),
                      stance(drop=2, lean=2, dy=-1, head='n', aF=((3, -2), (6, 1)), aN=((-3, -2), (-4, -4)))], 3, 'loop'),
            'attack': stab_poses(B_, P),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 提查诺（182 cm）：褐色皮肤、浅金长直发、深色发带、米白无袖衣、深色手套
def tiziano():
    pal = P_(L='#f6e4b6', y='#c0a060', n='#3c3254', e='#dc7c1c', m='#8c3c30', s='#ba7a4e', d='#88502e', w='#fff4e4',
             j='#eee8d8', k='#8c3050', q='#bcb2a0', x='#6c3c2c')
    head = '''
......yyyyyy......
....yyLLLLLLyy....
...yLnnnnnnnnLy...
..yLLnnnnnnnnLLy..
..yLLLLLLssLLLLy..
.yLLLLsssssssLLy..
.yLLLssbbbssbbbLy.
.yLLLsswesssweSLy.
.yLLLdswesssweSLy.
.yLLLddsssssssLy..
.yLLyddssssmmsLy..
.yLLy.dddssssdLy..
.yLLy..ddddd..Ly..
.yLLy..........y..
.yLy..............
..y...............
'''
    torso = '''
sjkssksj
sjjkkjjs
qjjjjjjj
qjjjjjjj
qjjjjjjj
qkjjjjkj
qjkkkkjj
qjjjjjjj
qjjjjjjj
'''
    B = b5(182, head, pal, torso, '#eee8d8', '#eee8d8', '#8c5c34', skin='#ba7a4e', sleeve='#ba7a4e', glove='#4c2c2c',
           pat_arm=lambda k, i, n: '#4c2c2c' if k >= 5 else None, boot=('#c8c0ac', 1))

    def extra(B_, P):
        A = B_.arm_len
        return {
            # 食指抵唇（堵住舌头说真话）
            'pose': ([stance(lean=-1, aF_front=True, aF=((6, -4), (4, 0)), aN=((-3, -2), (0, -A + 2))),
                      stance(lean=-1, dy=-1, aF_front=True, aF=((6, -4), (4, 1)), aN=((-3, -2), (0, -A + 2)), head='t')], 3, 'loop'),
            'attack': P['punch'],
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 乔可拉特（185 cm）：亮绿卷发束、脸上绿纹、灰白衣胸口蓝色晶纹、紫唇、摄像机
def cioccolata():
    pal = P_(G='#6ee462', l='#2c9c40', g='#58b048', e='#1c7c54', m='#6c3c8c', z='#f0c038', j='#e6e6ee', B='#3c54c4',
             y='#8c8ca4', Y='#d8d8e4', q='#acacc0', s='#e6b896', d='#b0846a')
    head = '''
....ll.lll.ll.....
...lGGlGGGlGGll...
..lGGlGGlGGGlGGl..
.lGlGGGGGGlGGGlGl.
lGGlGGgggggggsGGl.
lGlGGsssssssssGl..
.lGlsssbbbssbbbs..
lGGlssswesssweSs..
.lGddsswesssweS...
..lddgsssssssgs...
...ddgssssmmmss...
..z..ddsssssssd...
.......ddddd......
'''
    torso = '''
qjjyyyjj
qjjjyjjj
qjjBjBjj
qjjjBjjj
qjjBBBjj
qjjjBjjj
qjjBjBjj
qjjjjjjj
yyyyYyyy
qjjjjjjj
'''
    cam = prop('cam', '''
kkkkkk..
kKKKKkkk
kKrKKkcC
kKKKKkkk
kkkkkk..
.kk.....
''', -1, -4, dict(k='#17141e', K='#464256', r='#f03040', c='#8cc4e8', C='#e4f4ff'))
    B = b5(185, head, pal, torso, '#e6e6ee', '#dcdce6', '#8c8ca4', skin='#e6b896', cuff='#3c54c4', front=cam,
           coat=dict(len=4, col='#e6e6ee', flare=1, open=(0, 1), trim='#3c54c4'))

    def extra(B_, P):
        A = B_.arm_len
        return {
            # 架起摄像机偷拍
            'pose': ([stance(aF_front=True, aF=((6, -4), (6, 0)), aN=((-1, -3), (3, -2)), item='cam', head='t'),
                      stance(drop=1, aF_front=True, aF=((6, -4), (6, 0)), aN=((-1, -3), (3, -2)), item='cam', head='r', lean=1)], 3, 'loop'),
            'attack': P['punch'],
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 塞可（蹲着走）：连头的土黄紧身衣、橙色纹、蓝色缝线，只露眼睛
def secco():
    pal = P_(O='#b49a54', n='#6c5828', o='#e46c2c', B='#2c7cb4', e='#8c44c4', j='#a88c48', q='#786030', y='#6c5828',
             s='#e8c09c', d='#b8906c')
    head = '''
.....nnnnnnnn.....
...nnOOOOOOOOnn...
..nOOOOOOOOOOoOn..
..nOoooOOOOOOOOn..
.nOOOOOOOOOOOooOn.
.nOOOOOOOOOOOOOOn.
.nOOBOOBOOOBOOBn..
.nOOOsswesssweOn..
.nOOOdswesssweOn..
.nOOBOOBOOOBOOBn..
..nOOOOOOOOOOOn...
...nnOOOOOOOnn....
.....nnnnnnn......
'''
    torso = '''
qjjjjjjj
qooojjjj
qjjjjooj
qjooojjj
qjjjjooj
qooojjjj
qjjjjooj
qjjjjjjj
'''
    B = b5(170, head, pal, torso, '#a88c48', '#a88c48', '#786030', chin=11, skin='#e8c09c', glove='#a88c48',
           pat_leg=bands('#e46c2c', 4, 1), pat_arm=bands('#e46c2c', 3, 1))
    LH, A = B.LH, B.arm_len
    gd = LH - 4

    def extra(B_, P):
        low = dict(drop=gd, lean=3, hx=1, lN=((3, 0), (2, 0)), lF=((4, 0), (3, 0)), aN=((1, -3), (3, -6)), aF=((2, -3), (4, -6)))

        def L(**kw):
            d = dict(low)
            d.update(kw)
            return d
        return {
            'idle': ([L(), L(dy=1, aN=((1, -3), (3, -7)), aF=((2, -3), (4, -7)))], 2, 'loop'),
            'walk': ([L(aF=((3, -2), (7, -5)), aN=((0, -3), (0, -6)), lN=((4, 0), (4, 0)), lF=((2, 0), (1, 0))),
                      L(dy=1), L(aN=((3, -2), (6, -5)), aF=((0, -3), (1, -6)), lF=((5, 0), (5, 0)), lN=((2, 0), (0, 0))),
                      L(dy=1)], 8, 'loop'),
            # 讨方糖：仰头跳起
            'pose': ([L(head='r', aF_front=True, aF=((6, -1), (8, 3))), L(head='t', drop=0, lean=1, dy=3, aF_front=True, aF=((6, 1), (8, 6)),
                                                                   aN=((-3, 1), (-5, 5)), lN=((2, -3), (-1, 3)), lF=((3, -3), (2, 3)))], 5, 'loop'),
            'attack': ([L(aF=((-1, -1), (-2, 3))), L(head='r', bx=2, aF=((6, -1), (11, -3)), fistF=4),
                        L(head='r', bx=1, aF=((5, -3), (8, -7)), fistF=4)], 9, 'oneshot'),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 马里奥·祖凯罗（182 cm）：浅绿背头扎小辫、米色泡肩上衣、墨绿紧身裤、细剑
def zucchero():
    pal = P_(F='#e8fcac', L='#bede66', y='#7c9c34', e='#1c9ca8', j='#e8ecd0', J='#fbfce8', n='#8c9470', q='#b4ba98',
             p='#2c5c44', s='#f2caaa', d='#c29476')
    head = '''
......yyyyy.......
....yyFFFFFyy.....
...yFLLLLLLLLyy...
..yLLLLLLLLLLLLy..
..yLLLLsssssssLy..
.yLLLssssssssssy..
yyLLssbbbssbbbss..
yLyLssswesssweSs..
yy.yddswesssweS...
....dddsssssss....
....ddssssmmss....
.....dddsssssd....
.......dddd.......
'''
    torso = '''
JJjsssJJ
qJjjsjJj
qjjjjjjj
qjjjnjjj
qjjjnjjj
qjjjnjjj
qjjjjjjj
nnnnnnnn
qjjjjjjj
'''

    def sword(cv, B_, P, ctx):
        h = ctx.get('handF')
        if not h or P.get('item') != 'sword':
            return
        cv.line(X(h[0] + 1), Y(h[1]), X(h[0] + 13), Y(h[1] + 1), '#e8ecf8')
        cv.line(X(h[0] + 1), Y(h[1] - 1), X(h[0] + 8), Y(h[1]), '#8c92a8')
        cv.vline(X(h[0] + 1), Y(h[1] + 2), Y(h[1] - 2), '#e8c048')
    B = b5(182, head, pal, torso, '#e8ecd0', '#2c5c44', '#1c3c2c', skin='#f2caaa', shoulder=1, front=sword,
           boot=('#24462f', 3), coat=dict(len=3, col='#e8ecd0', flare=2, open=(0, 0), trim='#b4ba98'))

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([stance(lean=-1, aF=((3, -3), (6, -1)), aN=((-3, -2), (-4, 2)), item='sword'),
                      stance(lean=-1, dy=-1, aF=((3, -3), (6, 0)), aN=((-3, -1), (-4, 3)), item='sword', head='t')], 3, 'loop'),
            'attack': stab_poses(B_, P, 'sword'),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 萨雷（182 cm）：橘色后梳长发、粉色无袖长衫、蓝裤绿星纹、手枪
def sale():
    pal = P_(F='#ffbc60', O='#ee8830', o='#a8501c', e='#d82c5c', j='#e4a4c4', J='#f8cce0', n='#6c3c24', Z='#d8dce4',
             q='#ac6c8c', p='#34448c', s='#f0be98', d='#be886a')
    head = '''
......ooooo.......
....ooOFFFOOoo....
...oOFOOOOOOOOo...
..oOOOoOOOOOoOOo..
.oOOoOOsssoOOOsOo.
.oOoOOsssssssssss.
oOOoossbbbssbbbs..
oOoOssswesssweSs..
oOooddswesssweS...
oOo.dddssssssss...
.oOo.ddsssmmss....
..oo..ddsssssd....
..o....dddd.......
'''
    torso = '''
sjjsssjs
sjjjsjjs
qjJjjJjj
qjjjjjjj
qjjjjjjj
qjjjjjjj
nnnnZnnn
qjjjjjjj
qjjjjjjj
'''
    B = b5(182, head, pal, torso, '#e4a4c4', '#34448c', '#7c4c2c', skin='#f0be98', sleeve='#f0be98', wrist='#34448c',
           pat_leg=lambda k, i, n: '#78e49c' if (k % 4 == 2 and i == 1) else None, front=gun(),
           coat=dict(len=2, col='#e4a4c4', flare=1, open=(0, 0), trim='#ac6c8c'))

    def extra(B_, P):
        A = B_.arm_len
        return {
            'pose': ([stance(lean=-1, aF_front=True, aF=((6, -3), (7, 0)), aN=((-3, -2), (0, -A + 2))),
                      stance(lean=-1, dy=-1, aF_front=True, aF=((6, -2), (8, 2)), aN=((-3, -2), (0, -A + 2)), head='t')], 3, 'loop'),
            'attack': guns_poses(B_, P),
        }
    return std(B, VIL, extra)


# ---------------------------------------------------------------- 波尔波：监狱里的巨胖干部，坐着吃东西，紫红头发插满针、黄色大袍
POLPO_HEAD = '''
......z..z..z.......
...z..a..a..a..z....
...a.rRRRRRRRr.a....
..z.rRRRRRRRRRRr.z..
..arRRRRRRRRRRRRra..
...rRRRrrrrrrrrRr...
...rRrsssssssssss...
..rRrssbbbssssbbbs..
..rRrsssweSsssweSs..
..rrdssssssssssssss.
...ddssssssssssdsss.
..dddsssmmmmmmssssd.
..ddssssssssssssssd.
...dddsssssssssssd..
....ddddsssssssdd...
'''


def polpo():
    pal = P_(R='#a83454', r='#6c1c38', z='#d4dce8', a='#8c94a8', e='#2c8c3c', s='#f0c09c', d='#c08c6c', m='#8c3030')
    pal['b'] = '#3c1c2c'

    def frame(dy=0, mouth=False, eyes=False, food=None, laugh=0):
        cv = Cv(CW, CH)
        yel, yd, yl = '#e8c444', '#a8842c', '#fce47c'
        # 摊开坐着的腿和鞋
        cv.ellipse(OX - 11, OY - 4, 9, 4, '#4c3430')
        cv.ellipse(OX + 13, OY - 4, 9, 4, '#5e423a')
        cv.ellipse(OX + 21, OY - 2, 4, 2.6, '#241c24')
        cv.ellipse(OX - 19, OY - 2, 4, 2.6, '#1c161e')
        # 大肚子和黄袍
        body = Cv(CW, CH)
        body.ellipse(OX, OY - 15 - dy * 0.5, 18, 13.4 + dy * 0.5, yd)
        body.ellipse(OX + 1.5, OY - 16 - dy * 0.5, 15.5, 12, yel)
        body.ellipse(OX + 8, OY - 20 - dy * 0.5, 5, 4, yl)
        cv.blit(body)
        for x, y in ((-9, 8), (-3, 7), (3, 6), (9, 7), (-12, 14), (13, 13)):
            cx, cy = OX + x, OY - y - dy
            for ax, ay in ((0, 0), (1, 1), (-1, 1), (0, 2)):
                cv.put(cx + ax, cy + ay, '#5c3c24')
        cv.line(OX + 2, OY - 26 - dy, OX + 4, OY - 8, yd)
        for k in range(4):
            cv.rect(OX + 4, OY - 22 + k * 4 - dy, OX + 5, OY - 21 + k * 4 - dy, '#3c9458')
        # 手臂
        arm = Cv(CW, CH)
        arm.ellipse(OX - 15, OY - 18 - dy, 5, 7, yel)
        arm.ellipse(OX - 14, OY - 11 - dy, 3.4, 2.8, pal['s'])
        cv.blit(arm)
        # 头
        head = [r for r in rows(POLPO_HEAD)]
        if eyes:
            head = [r.replace('we', 'bb') for r in head]
        if mouth:
            head = list(head)
            head[11] = head[11].replace('mmmmmm', 'MMMMMM')
            head[12] = head[12][:8] + 'MMMMMM' + head[12][14:]
        p = dict(pal)
        p['M'] = '#6c1c2c'
        hp = Cv(CW, CH)
        hp.grid(head, OX - 9, OY - 40 - dy - laugh, p)
        cv.blit(hp)
        # 拿东西的手
        if food is not None:
            hx, hy = (OX + 19, OY - 15) if food == 0 else (OX + 12, OY - 27)
            f = Cv(CW, CH)
            f.line(OX + 14, OY - 19 - dy, hx, hy, yel)
            f.line(OX + 14, OY - 18 - dy, hx, hy + 1, yel)
            f.line(OX + 14, OY - 17 - dy, hx, hy + 2, yd)
            f.ellipse(hx + 1, hy, 2.6, 2.4, pal['s'])
            f.ellipse(hx + 2, hy - 3, 3, 2.6, '#d89440')
            f.put(hx + 1, hy - 4, '#fcd484')
            cv.blit(f)
        else:
            f = Cv(CW, CH)
            f.ellipse(OX + 16, OY - 17 - dy, 4.4, 6, yel)
            f.ellipse(OX + 18, OY - 12 - dy, 3.2, 2.6, pal['s'])
            f.rect(OX + 19, OY - 17 - dy, OX + 22, OY - 15 - dy, '#a82c44')
            f.rect(OX + 19, OY - 19 - dy, OX + 22, OY - 18 - dy, '#e4f0f8')
            f.vline(OX + 20, OY - 14 - dy, OY - 12 - dy, '#e4f0f8')
            cv.blit(f)
        cv.outline(OUTLINE)
        fill_pinholes(cv)
        return cv

    sh = Sheet('', '', kind='char')
    sh.add('idle', [frame(), frame(1)], 2, 'loop')
    sh.add('pose', [frame(food=0), frame(food=1, mouth=True), frame(food=1, eyes=True), frame(1, food=1)], 5, 'loop')
    sh.add('laugh', [frame(mouth=True, eyes=True), frame(1, mouth=True, eyes=True, laugh=1)], 6, 'loop')
    return sh


CAST = {
    'diavolo': ('迪亚波罗', diavolo),
    'doppio': ('多比欧', doppio),
    'risotto': ('里苏特', risotto),
    'formaggio': ('霍尔马吉欧', formaggio),
    'illuso': ('伊鲁佐', illuso),
    'prosciutto': ('普罗修特', prosciutto),
    'pesci': ('贝西', pesci),
    'melone': ('梅洛尼', melone),
    'ghiaccio': ('加丘', ghiaccio),
    'squalo': ('史克亚罗', squalo),
    'tiziano': ('提查诺', tiziano),
    'cioccolata': ('乔可拉特', cioccolata),
    'secco': ('塞可', secco),
    'zucchero': ('祖凯罗', zucchero),
    'sale': ('萨雷', sale),
    'polpo': ('波尔波', polpo),
}
HEIGHTS = {'diavolo': 191, 'doppio': 170, 'risotto': 185, 'formaggio': 178, 'illuso': 188, 'prosciutto': 178, 'pesci': 165,
           'melone': 174, 'ghiaccio': 171, 'squalo': 182, 'tiziano': 182, 'cioccolata': 185, 'zucchero': 182, 'sale': 182}
build = make_build(CAST)

if __name__ == '__main__':
    import sys
    main(CAST, build, sys.argv)
