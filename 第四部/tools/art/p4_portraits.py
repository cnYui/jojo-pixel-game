# 第四部手画说话头像（32×32）：对照 TV 动画角色设定和 JoJo Wiki 配色表逐格画的，取代“第三部头像换色”那一版。
#   p4_chars.save() 存头像前查这里：HEADS 里有的 cid 就用这里的图（normal / smile / shock / rage 各 2 帧，0 闭嘴 1 张嘴）。
#   网格里每个字母是调色板里的一种颜色，'.' 透明。表情由同一张底图改嘴、眼、眉生成：
#   嘴 = 'm' 像素那一行；眼 = 'E'/'e' 像素；眉 = 'B' 像素（每段眉毛靠脸中间的一头是“内端”）。
#   单独看效果：python3 第四部/tools/art/p4_portraits.py [输出目录]  → 每个角色一张放大预览
import os
import sys

from PIL import Image

DEFS = {}

# 吉良吉影（西装）：TV 动画第一套——金发松松往一边梳、盖住耳朵；灰蓝眼、眼皮半垂；淡紫西装、白条纹绿衬衫、深棕骷髅领带
DEFS['kira'] = dict(
    pal=dict(o='#1a1020', H='#fbefb4', h='#e8cc72', d='#b8923e', B='#8a6a2c', S='#f6c49a', s='#d8946c', W='#ffffff', E='#7a92b4', e='#34445e', m='#6e3e24', L='#d2c2ec', l='#a894cc', k='#6c5898', G='#3e9a62', g='#e8f4ec', T='#4a2e1e', X='#efe8d8'),
    grid='''
................................
...........oooooooo.............
.........ooHHHHHHHHoo...........
........oHHHHHHHHHHHHoo.........
.......oHHhHHHHHHHHHHHHo........
......oHhHHHHHHHhHHHHHHHo.......
.....ohHhHHHHHHhHHHHHhHHHo......
.....ohhHHHHHHhHHHHHhHHHHHo.....
....ohdhHHHHHhHHHHHhHHHHhHHo....
....ohdhHHHHhHHHHHhHHhHHHhHHo...
....ohdhHHHhHHhhHhSShhHHHhHHo...
...ohddhHHhhSShSShSSSShhHHhHo...
...ohdhhHhsSSBBBBSSSSSSBBBhHHo..
...ohdhHhssSoooooSSSSSooooHHHo..
...ohdhHhsSSSWEEeSSSSSWEEeShho..
...ohddhhsSSSSEeSSSSSSSEeShhHo..
...ohdhhhssSSSSSSSSSsSSSSShhho..
....ohdhhosSSSSSSSSSSsSSSSSdho..
....ohddho.osSSSSSSSssSSSSSoo...
.....ohdho..osSSSSSSSSSSSSo.....
.....ohddo...osSSSSmmmSSSso.....
......oddo....ossSSSSSSSso......
.......oo....ooossSSSSsoo.......
.........oooLLLosssssssoLLoo....
........oLLLLLLoGgGTTgGoLLLLo...
.......oLLLLLLLloGgTXTgoLLLLLo..
......oLLLLLLLLLloGTTTolLLLLLko.
.....oLLLLLLLLLLLloGTGolLLLLLko.
....oLLLLLLLLLLLLLloTolLLLLLLkko
...olLLLLLLLLLLLLLLloolLLLLLLkko
..olLLLLLLLLLLLLLLLLlolLLLLLLLko
..olLLLLLLLLLLLLLLLLLllLLLLLLLko
''')

# 吉良顶着川尻浩作的脸：黑色刺头、瘦脸、大而深的黑眼珠；TV 动画第一套：泛紫的白西装、粉条纹深洋红衬衫、青绿领带
DEFS['kawajiri'] = dict(
    pal=dict(o='#1a1020', H='#5a5468', h='#38343f', d='#24202c', S='#f6c49a', s='#d8946c', W='#ffffff', E='#3a3040', e='#120e18', m='#6e3e24', B='#24202c', L='#ece6f6', l='#c4bad8', k='#8e80aa', G='#7a2a5e', g='#e890b8', T='#2aa0a0', X='#d8c08a'),
    grid='''
................................
........o.....o...o.............
.......oho...oho.oho..o.........
....o..ohho.ohhoohhho.oho.......
....oho.ohhoohhhHhhhoohho.......
....ohhoohhhhhhHhhhhhhhhhoo.....
..ooohhhhhhhhHhhhhhhhHhhhhhoo...
...ohhhhhhhHhhhhhhhhHhhhhhhhho..
.oohhhhhhhhhhhhhhhhhhhhhhhhhho..
..ohhhhdhhhhhhhhhhhhhhhhhhhhho..
...ohhhdhhhhhdhhhdhhhhhdhhhhho..
..ohhhddhhhhsdhSdhSShdhSSdhho...
...ohhdhhhsSSShSSShSSSShSSdho...
...ohdhhhssSBBBBSSSSSSBBBBSho...
...ohdhhssSoooooSSSSSooooSho....
...ohddhssSWEWEeSSSSWEWEeSho....
...ohdhsssSSEEeSSSSSSEEeSSo.....
....ohdossSSSSSSSSSSSSSSSSo.....
....ohdosssSSSSSSSSSsSSSSso.....
.....oho.osSSSSSSSSSssSSso......
.....ohho.osSSSSSSSSSSSso.......
......oo...osSSSSmmmSSSo........
............osSSSSSSSSo.........
............oooossSSsoo.........
.........oooLLLosssssoLLoo......
........oLLLLLLoGgGTTgGoLLLo....
.......oLLLLLLLloGgTXTgoLLLLo...
......oLLLLLLLLLloGTTTolLLLLko..
.....oLLLLLLLLLLLloGTGolLLLLLko.
....oLLLLLLLLLLLLLloTolLLLLLLkko
...olLLLLLLLLLLLLLLloolLLLLLLkko
..olLLLLLLLLLLLLLLLLlolLLLLLLLko
''')

# 虹村亿泰：小号黑飞机头、两侧灰色、后脑两根小辫尖；脸上两道弧线经过内眼角；灰眼；蓝校服白滚边、紫内衫、金色 $ 徽章
DEFS['okuyasu'] = dict(
    pal=dict(o='#1a1020', K='#3a3448', k='#22202c', j='#5c5670', A='#a8a8b8', a='#80808f', S='#f2bc8e', s='#d08a62', W='#ffffff', E='#8a8e9c', e='#3a3c48', m='#6e3e24', B='#22202c', R='#a03040', U='#3a5ab8', u='#2a4088', V='#d8dce8', P='#7a4aa0', Y='#ffd83c', y='#c89a20'),
    grid='''
................................
..............ooooooo...........
...........oooKKKjjjKoooo.......
.........ooKKKKjjjjKKKKKKoo.....
........oKKKKjjKKKKKKKKKKKKKoo..
.......oKKKKKKKKKKKKKKKKKKjjKKo.
......oAKKKKKKKKKKKKKKKKKKKKKKko
.....oAAAkKKKKKKKKKKKKKKKKkkkoo.
.....oAAAAkkkKKKKKKKkkkkkoo.....
....oAAaAAAASkkkkkkkkSSSSo......
....oAaAAAAsSSSSsSSSSSSSSSo.....
....oAAaAAsSSSSsSSSSSsSSSSSo....
....oAaAAAsSSBBBBsSSSsBBBBSSo...
....oAAaAsSSSSoooosSSsoooSSSo...
....oaAaoSSSSSWEEesSSsWEeSSSo...
...ooAAoSsSSSSSEesSSSSsEeSSSSo..
..oAaoAosSoSSSSSsSSSSSSsSSSSSo..
...oaoAossoSSSSsSSSSSsSSSSSSo...
....ooaoossSSSSSSSSSSssSSSSSo...
......ooo.osSSSSSSSSSSSSSSSo....
..........osSSSSSmmmmmmSSSSo....
...........osSSSSSSSSSSSSSo.....
...........ooossSSSSSSSsoo......
.........ooVUUoosssssssoUVoo....
........oUUVUUUoPPPPPPPoUUVUo...
.......oUUUVUUUUoPPPPPoUUVUUUo..
......oUUUUVUUUUUoPPPoUUVUUUUuo.
.....oUUUUUUVUUUUUoPoUUVUUUUUuo.
....oUUUUUUUUVUUUUUoUUVUUYYUUuuo
...ouUUUUUUUUUVUUUUVUVUUUYyUUuuo
..ouUUUUUUUUUUUVUUUUVUUUUYYUUUuo
..ouUUUUUUUUUUUUVUUUVUUUUUUUUUuo
''')

# 矢安宫重清：光头一层短刺、大圆脑袋、细眉高挑、小青绿眼、厚耳垂、缺门牙；绿校服黄滚边和钉珠
DEFS['shigechi'] = dict(
    pal=dict(o='#1a1020', S='#f8d0aa', s='#dca07a', t='#c08a66', W='#ffffff', E='#2aa89a', e='#145a54', m='#6e3e24', B='#1a1020', R='#a03040', G='#3e9a50', g='#26703a', Y='#f0c838', D='#2c3a8a'),
    grid='''
..........o.o.o.o.o.o...........
.........ototototototoo.........
.......ootSsSsssSsSsSsSoo.......
......otSSSsSSSSsSSSSsSSSoo.....
.....otSsSSSSsSSSSsSSSSsSSSo....
....otSSSSsSSSSsSSSSsSSSSsSSo...
....osSsSSSSsSSSSsSSSSsSSSSso...
...osSSSSsSSSSsSSSSsSSSSsSSSSo..
...osSsSSSSsSSSSsSSSSsSSSSsSSo..
...osSSSSSSSSSBBBSSSSSSBBBSSSo..
..oossSSSSSSSSSSSSSSSSSSSSSSSSo.
.osSsSSSSSSSSSSSSSSSSSSSSSSSSSo.
.osSsoSSSSSSSSSoooSSSSSoooSSSSo.
.osSssSSSSSSSSSWEoSSSSSWEoSSSSo.
.osSsSSSSSSSSSSSeoSSSSSSeoSSSSo.
.ossSsSSSSSSSSSSSSSSSSSSSSSSSSo.
.ossSSSSSSSSSSSSSSSsSSSSSSSSSSo.
..ossSSSSSSSSSSSSSSssSSSSSSSSSo.
..osssSSSSSSSSSSSSSSSSSSSSSSSo..
...ossSSSSSSSSSSoooooooSSSSSSo..
...ossSSSSSSSSSoWoWWWWWoSSSSso..
....ossSSSSSSSSSoooooooSSSSso...
.....ossSSSSSSSSSSSSSSSSSSso....
......oossSSSSSSSSSSSSSSsoo.....
.......oGoosssssssssssooGo......
......oGGGGooooooooooooGGGo.....
.....oGGGGGYGGGGGGGGGYGGGGGo....
....oGGGGGGGYGGGGGGGYGGGGGGgo...
...oGGGGGGGGGYGGGGGYGGGGGGGggo..
..ogGGGGGGGGGGYGGGYGGGGGGGGGggo.
..ogGGGGGGGGGGGYGYGGGGGGGGGGggo.
..ogGGGGGGGGGGGGYGGGGGGGGGGGggo.
''')

# 杀手皇后：浅粉身体、平头顶两只猫耳、红眼白竖瞳、没有鼻子、嘴闭着；肩上骷髅纹
DEFS['killerqueen'] = dict(
    pal=dict(o='#1a1020', P='#f4cada', p='#d496ae', q='#a86484', L='#fff0f6', R='#e0485a', W='#ffffff', m='#8a4a66', D='#4a2462', d='#2c1440', Y='#f0c850', y='#b8902a'),
    grid='''
.......oo...............oo......
.......oPo.............oPPo.....
.......oPPo...........oPpPo.....
.......oPpPo.........oPppPo.....
.......oPppPoooooooooPpppPo.....
.......oPPPPPPPPPPPPPPPPPPPo....
......oPPPPPPPPPPPPPPPPPPPPPo...
......oPPLLPPPPPPPPPPPPPPPPPo...
......oPPLPPPPPPPPPPPPPPPPPPo...
......opPPPPPPPPPPPPPPPPPPPPPo..
......opPPPPPPPPPPPPPPPPPPPPPo..
......opPPPPPPPPPPPPPPPPPPPPPo..
......oppPPPPPPooooPPPPPoooPPo..
......oppPPPPPoRRWRRoPPPoRWRoo..
......oppPPPPPoRRWRRoPPPoRWRpo..
......oqpPPPPPPooooopPPPPoooPo..
......oqppPPPPPPPPPpPPPPPPPPPo..
......oqqpPPPPPPPPpPPPPPPPPPPo..
.......oqppPPPPPPPPPPPPPPPPPo...
.......oqqpPPPPPPPPPPPPPPPPpo...
........oqppPPPPPPPmmmmPPPpo....
.........oqqpPPPPPPPPPPPPpo.....
..........ooqqppPPPPPPppoo......
.........ooPPooqqppppqooPPoo....
.......ooPPPPPPooppppooPPPPPoo..
.....ooPPPPPPPPPPPoopoPPPPPPPPo.
....oPPPLLPPPPPPPPPPpPPPPPPPPPPo
...oPPLLLLLPPPPPPPPPpPPPPPPPPPPo
..oPPLooLooLPPPPPPPpPPPPPPPPPPpo
..oPPLLLLLLLPPPPPPPpPPPPPPPPPPpo
..oPPPLoLoLPPPPPPPPPpPPPPPPPPPpo
..opPPPLLLPPPPPPPPPPpPPPPPPPPppo
''')

# 岸边露伴（第一套）：深绿头发侧梳、绿色锯齿边发带、钢笔尖耳环；绿眼；浅绿马甲、浅紫衬衫
DEFS['rohan'] = dict(
    pal=dict(o='#1a1020', H='#4a8a5a', h='#2c5a3c', d='#1a3626', A='#3c6a4a', N='#6ad07a', n='#2e8a44', S='#f8d0b0', s='#dca07e', W='#ffffff', E='#3aa860', e='#1a5a34', m='#8a4a3a', B='#1a3626', Y='#f0c850', L='#b4e0a8', l='#82b878', k='#5a8a50', G='#d0b8e8', g='#a890c8'),
    grid='''
................................
...........oooooo...............
........oooHHHHHHoooo...........
.......ohHHHHHHHHHHHHoo.........
......ohhHHhhhHHHHHHHHHoo.......
.....ohhhhhHHHhhhHHHHHHHHo......
.....ohhhhhhhhhHHHhhhhHHHHo.....
....ononononononononononononoo..
....oNNNNNNNNNNNNNNNNNNNNNNNNNo.
....onNnNnNnNnNnNnNnNnNnNnNnNno.
....oAoAnAnAnAnAnAnAnAnAnAnAo...
....oAAAAhSSSSSSSSSSSSSSShhHo...
...oAAAAsSSSBBBBBSSSSSBBBBShHo..
...oAAAssSSSSoooooSSSSSooooSho..
...oAAosSSSSSSWEEeSSSSSWEEeSho..
...oAsSoSSSSSSSEeSSSSSSSEeSSo...
...osSSsoSSSSSSSSSSSSSSSSSSSo...
....osSoSSSSSSSSSSSSSsSSSSSSo...
....oYoosSSSSSSSSSSSSsSSSSSo....
....oYo.osSSSSSSSSSSssSSSSo.....
.....o...osSSSSSSSSSSSSSSo......
.........osSSSSSSmmmSSSSo.......
..........ossSSSSSSSSSSo........
...........ooossSSSSsoo.........
.........oooLLosssssoLLoo.......
........oLLLLLoGGgsgGGoLLLo.....
.......oLLLLLLoGGGgGGGoLLLLo....
......oLLLLLLLloGGGGGolLLLLko...
.....oLLLLLLLLLloGGGolLLLLLLko..
....oLLLLLLLLLLLLoGolLLLLLLLkko.
...olLLLLLLLLLLLLLoolLLLLLLLLkko
..olLLLLLLLLLLLLLLLlLLLLLLLLLLko
''')

# 喷上裕也：底切发型——黑色顶发往后梳、两侧浅灰；浅蓝眼；深灰校服、白色领结、金色扣饰
DEFS['yuya'] = dict(
    pal=dict(o='#1a1020', K='#2e2a38', k='#1a1822', j='#504a60', A='#b8bcc8', a='#8a8e9c', S='#f6c49a', s='#d8946c', W='#ffffff', E='#8ac8f0', e='#3a6a9a', m='#6e3e24', B='#1a1822', U='#4a4a56', u='#30303a', V='#ffffff', Y='#ffd83c'),
    grid='''
................................
................................
..........oooooooooo............
........ooKKKjjjjKKKoooo........
.......oKKKKKKjjjjKKKKKKoo......
......oKKKKKKKKKKKKKKKKKKKoo....
......oAKKKKKKKKKKKKKKKKKKKKo...
.....oAAAkKKKKKKKKKKKKKKKkkko...
.....oAAAAkkKKKKKKKKKkkkkoo.....
....oAAaAAAAkkkkkkkkkSSSSo......
....oAaAAAAsSSSSSSSSSSSSSSo.....
....oAAaAAsSSSSSSSSSSSSSSSSo....
....oAaAAAsSSSBBBBSSSSSBBBBSo...
....oAAaAsSSSSoooooSSSSooooSo...
....oaAaosSSSSWEEeSSSSSWEEeSo...
.....oAosSSSSSSEeSSSSSSSEeSSo...
.....oaosSSSSSSSSSSSSSSSSSSSo...
......oossSSSSSSSSSSSsSSSSSSo...
.......oosSSSSSSSSSSsSSSSSSo....
.........osSSSSSSSSSSSSSSSo.....
..........osSSSSSSmmmSSSSo......
...........osSSSSSSSSSSSo.......
...........ooossSSSSSsoo........
.........ooUUUoosssssooUUoo.....
........oUUUUUUUoVVoVVoUUUUo....
.......oUUUUUUUUUoVVVoUUUUUUo...
......oUUUUUUUUUUUoVoUUUUUUUuo..
.....oUUUUUUUUUUUUoUoUUUUUUUuo..
....oUUUUUUUUUUUUUoUoUUUYUUUuuo.
...ouUUUUUUUUUUUUUoUoUUUUUUUuuo.
..ouUUUUUUUUUUUUUUoYoUUUUUUUUuo.
..ouUUUUUUUUUUUUUUoUoUUUUUUUUuo.
''')


SKIN, OUT, RED, WHITE = 'S', 'o', 'R', 'W'
EXTRA = dict(o='#1a1020', R='#a03040', W='#ffffff')
ONLY_NORMAL = {'killerqueen'}     # 替身：只有 normal，别的表情走 headAlias


def hexc(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def grid(cid):
    rows = [list(r) for r in DEFS[cid]['grid'].strip('\n').split('\n')]
    assert len(rows) == 32 and all(len(r) == 32 for r in rows), cid
    return rows


def render(cid, g):
    pal = dict(EXTRA)
    pal.update(DEFS[cid]['pal'])
    im = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    for y, row in enumerate(g):
        for x, ch in enumerate(row):
            if ch != '.':
                im.putpixel((x, y), (*hexc(pal[ch]), 255))
    return im


def find(g, chars):
    return [(x, y) for y, r in enumerate(g) for x, c in enumerate(r) if c in chars]


def mouth(g):
    pts = find(g, 'm')
    if not pts:
        return None
    y = max(p[1] for p in pts)
    xs = sorted(x for x, yy in pts if yy == y)
    return xs[0], xs[-1], y


def copy(g):
    return [r[:] for r in g]


def open_mouth(g, inner=RED, big=False):
    g = copy(g)
    mo = mouth(g)
    if not mo:
        return g
    x0, x1, y = mo
    if x1 - x0 < 2:
        x0, x1 = x0 - 1, x1 + 1
    for x in range(x0, x1 + 1):
        g[y][x] = OUT
    for x in range(x0, x1 + 1):
        g[y + 1][x] = OUT if x in (x0, x1) else inner
    if big:
        for x in range(x0, x1 + 1):
            g[y + 2][x] = OUT if x in (x0, x1) else inner
        for x in range(x0 + 1, x1):
            g[y + 3][x] = OUT
    else:
        for x in range(x0 + 1, x1):
            g[y + 2][x] = OUT
    return g


def smile_mouth(g):
    g = copy(g)
    mo = mouth(g)
    if not mo:
        return g
    x0, x1, y = mo
    for x in range(x0, x1 + 1):
        g[y][x] = SKIN
    for x in range(x0, x1 + 1):
        g[y][x] = 'm'
    g[y][x0] = SKIN
    g[y][x1] = SKIN
    g[y - 1][x0 - 1] = 'm'
    g[y][x0] = 'm'
    g[y - 1][x1 + 1] = 'm'
    g[y][x1] = 'm'
    g[y][x0 - 1] = SKIN if g[y][x0 - 1] == 'm' else g[y][x0 - 1]
    return g


def eyes(g):
    """按 x 分成左右两只眼"""
    pts = find(g, 'Ee')
    if not pts:
        return []
    mid = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    return [[p for p in pts if p[0] < mid], [p for p in pts if p[0] >= mid]]


def squint(g):
    """笑眯眼：每只眼最下面一行换成皮肤"""
    g = copy(g)
    for eye in eyes(g):
        ys = [p[1] for p in eye]
        if len(set(ys)) > 1:
            for x, y in eye:
                if y == max(ys):
                    g[y][x] = SKIN
    return g


def pinpoint(g):
    """吃惊：眼珠变眼白，正中留一个小黑点"""
    g = copy(g)
    for eye in eyes(g):
        for x, y in eye:
            g[y][x] = WHITE
        cx = round(sum(p[0] for p in eye) / len(eye))
        cy = min(p[1] for p in eye)
        g[cy][cx] = OUT
    return g


def frown(g):
    """生气：每段眉毛的内端压低一行"""
    g = copy(g)
    pts = find(g, 'B')
    ex = [p[0] for e in eyes(g) for p in e]
    cx = sum(ex) / len(ex) if ex else 16
    rows = {}
    for x, y in pts:
        rows.setdefault(y, []).append(x)
    for y, xs in rows.items():
        xs.sort()
        segs, cur = [], [xs[0]]
        for x in xs[1:]:
            if x == cur[-1] + 1:
                cur.append(x)
            else:
                segs.append(cur)
                cur = [x]
        segs.append(cur)
        for s in segs:
            inner = s[-1] if abs(s[-1] - cx) < abs(s[0] - cx) else s[0]
            outer = s[0] if inner == s[-1] else s[-1]
            g[y][inner] = SKIN
            g[y + 1][inner] = 'B'
            if len(s) > 2:
                g[y - 1][outer] = 'B' if g[y - 1][outer] == SKIN else g[y - 1][outer]
    return g


def shigechi_open(g):
    """重清：平时就龇着缺门牙的牙，张嘴帧把下面一行掏成嘴里的红"""
    g = copy(g)
    pts = find(g, 'W')
    y = max(p[1] for p in pts)
    xs = sorted(p[0] for p in pts if p[1] == y)
    for x in range(xs[0], xs[-1] + 1):
        g[y + 1][x] = RED
    for x in range(xs[0], xs[-1] + 1):
        g[y + 2][x] = OUT
    return g


def heads(cid):
    """cid → {表情: [Image, Image]}"""
    g = grid(cid)
    if cid in ONLY_NORMAL:
        im = render(cid, g)
        return {'normal': [im, im]}
    if cid == 'shigechi':
        op = shigechi_open
        sm = [g, op(g)]
        return {'normal': [render(cid, g), render(cid, op(g))],
                'smile': [render(cid, squint(x)) for x in sm],
                'shock': [render(cid, pinpoint(x)) for x in (op(g), op(g))],
                'rage': [render(cid, frown(x)) for x in sm]}
    sm = smile_mouth(g)
    return {'normal': [render(cid, g), render(cid, open_mouth(g))],
            'smile': [render(cid, squint(sm)), render(cid, squint(open_mouth(g)))],
            'shock': [render(cid, pinpoint(open_mouth(g))), render(cid, pinpoint(open_mouth(g, big=True)))],
            'rage': [render(cid, frown(g)), render(cid, frown(open_mouth(g, inner=WHITE)))]}


HEADS = set(DEFS)


def preview(out_dir, S=8):
    os.makedirs(out_dir, exist_ok=True)
    order = ['normal', 'smile', 'shock', 'rage']
    for cid in DEFS:
        hd = heads(cid)
        cols = [(e, i) for e in order if e in hd for i in range(len(hd[e]))]
        im = Image.new('RGB', (len(cols) * (32 * S + 8), 32 * S + 8), (58, 58, 70))
        for k, (e, i) in enumerate(cols):
            f = hd[e][i].resize((32 * S, 32 * S), Image.NEAREST)
            im.paste(f, (k * (32 * S + 8) + 4, 4), f)
        im.save(os.path.join(out_dir, cid + '.png'))


if __name__ == '__main__':
    preview(sys.argv[1] if len(sys.argv) > 1 else '.')
