"""art_new_grayfly -- 新角色 格雷·弗莱（灰塔的替身使者；技术约定 §3.14 B，规划 §5.2.5）。

骨架 = sprites_dio 的“普通人体”部件和画法（报告 08 §2.3）：每个部件先用 SD._ol 描边再 SD._compose 拼，
腿用 SD.LEG 去掉金色护膝的那几行（同 泰伦斯 TEL_LEG 的做法）、手臂用 SD.ARM / ARM_LIMP 换色；
新画的只有驼背的西装躯干、秃顶白发的老人头、侧躺身体和头像（同一套字母：q/Q/i 头发、j/J/I/E 外套、
n/N 衬衫、x/X/L 裤子、s/S 皮肤）。西装灰蓝 = 名牌色 #8a9ab0（规划 §5.2 名牌表）。

动作（名义画布 32×44，身高约 40，脚在最底行）：
  idle 2（驼背、搓着手阴笑；f1 肩膀抖一下“嘿嘿”）、seated 1（座椅上只露头肩，16×18）、
  hurt 1（被打得后仰、惊恐）、down 1（仰面倒地、头朝左，翻白眼）；
  头像 portrait 2（咧嘴笑：闭嘴 / 张嘴说话）、portrait_scared 1（惊恐）。
"""
import sys
sys.dont_write_bytecode = True
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art_common as AC                       # noqa: E402

from engine import sprite                     # noqa: E402
from engine.sprite import g_new, g_stamp, g_recolor, g_lines, g_join, g_flip   # noqa: E402
from assets import sprites_dio as SD          # noqa: E402

NEW = []
ONESHOT = set()
STATIC_STATES = set()
CHAR_INFO = {'grayfly': dict(zh='格雷·弗莱', en='Gray Fly', cat='敌人·人物', typ='人物')}
ACTION_ZH = {'seated': '坐在座位上'}

GF_PAL = {
    'q': '#d4d2dc', 'Q': '#8e8ca0', 'i': '#f4f4f8',               # 稀疏的白发
    'j': '#7c8ca6', 'J': '#4e5a74', 'I': '#a6b4ca', 'E': '#323a4e',   # 灰蓝西装（名牌色 #8a9ab0）
    'n': '#ddd6c0', 'N': '#a8a08a',                                # 发黄的衬衫
    'r': '#a83a4a', 'R': '#6a1e2e',                                # 酒红领带 / 嘴里
    'x': '#4a4452', 'X': '#2a2632', 'L': '#6a6476',                # 深灰裤子
    'a': '#ddd6c0', 'A': '#a8a08a',                                # 原 ARM 的“金袖口”换成衬衫袖口
    's': '#e6bf9c', 'S': '#b4886a', 'D': '#8a6450',                # 发黄起皱的老人皮肤（D = 皱纹深处）
    'h': '#6a4630', 'H': '#3e281a',                                # 旧皮鞋
    'W': '#e8dcae',                                                # 发黄的牙
    'y': '#ffd83c',
    'u': '#9cd8ff',                                                # 汗
}

W_, H_ = 32, 44

# ------------------------------------------------------------------ 头（14×14，3/4 侧脸朝右）
# 秃顶、后脑勺和耳边一圈乱翘的白发、浓白眉压着小眼睛、鹰钩鼻、咧到耳根的笑（露一排黄牙）
GF_HEAD = """
.....ssssss....
...sssssssssi..
..qsssSSSssss..
.qqssssssSSss..
qqiqssssssssss.
qiqqsSsqqqsqqq.
qqqqSSsDkDsDk..
qQqqSsssssssSss
.qQqSDsssssssss
.qQqSsDkssSSSs.
.qQqSsDSkWWWWWk
..qQSssSRRRRRk.
..QqqSSsSSSSS..
...Q..SSSSS....
"""

GF_HEAD_SCARED = """
.....ssssss....
...sssssssssi..
..qsssSSSssss..
.qqssssssSSss..
qqiqsssqqqsqqq.
qiqqsSswwksww..
qqqqSSswekswe..
qQqqSsssssssSss
.qQqSDsssssssss
.qQqSsDssskkks.
.qQqSsDsskRRRk.
..qQSssskRRRk..
..QqqSSsskkkS..
...Q..SSSSS....
"""

GF_HEAD_BLANK = """
.....ssssss....
...sssssssssi..
..qsssSSSssss..
.qqssssssSSss..
qqiqssssssssss.
qiqqsSsqqqsqqq.
qqqqSSsWWWsWW..
qQqqSsssssssSss
.qQqSDsssssssss
.qQqSsDssskkks.
.qQqSsDsskRRk..
..qQSsssskkS...
..QqqSSssssS...
...Q..SSSSS....
"""

# ------------------------------------------------------------------ 驼背西装躯干（15×11）
# 背（左）拱起、胸口（右）往前塌；V 领里是发黄衬衫 + 酒红领带，前襟一排深色扣子
GF_TORSO = """
....IIjjjsnj...
..IIjjjjjnrnj..
.IIjjjjjjnrnjj.
.IjjjjjjjjrRjj.
IjjjjjjjjjjEjjJ
jjjjjjjjjjjjjJJ
jjjjjjjjjjjEjJJ
.jjjjjjjjjjjJJ.
.JjjjjjjjjjEJJ.
..JjjjjjjjjJJ..
..xxxxxxxxxxx..
"""

GF_LEG = g_recolor(SD._rows(SD.LEG, [0, 1, 2, 3, 4, 9, 10, 11, 12, 13, 14, 15]),
                   {'a': 'x', 'j': 'h', 'I': 'h', 'J': 'H'})

# 手：搓着的两只手（近手盖在远手上），袖口发黄
GF_HANDS = """
nnsss.
NsssSs
.sSsS.
"""

GF_FORE_N = """
.....Ij
...Ijjj
.Ijjjj.
Ijjjj..
jjJJ...
JJJ....
"""
GF_FORE_F = """
...jJ
.jjJE
jJJE.
"""


def _leg(kind, far=False):
    g = GF_LEG
    if kind == 'out_l':
        g = SD._shear(GF_LEG, [0] * 6 + [-1] * 6)
    elif kind == 'out_r':
        g = SD._shear(GF_LEG, [0] * 6 + [1] * 6)
    elif kind == 'back':
        g = SD._shear(GF_LEG, SD._steps(12, -3))
    elif kind == 'fwd':
        g = SD._shear(GF_LEG, SD._steps(12, 3))
    if far:
        g = g_recolor(g, SD.FAR)
    return g


def _hunch(grid, k):
    """躯干上半部往前（右）塌 k px（驼背）。"""
    n = len(g_lines(grid))
    offs = [round(k * max(0, (n - 4 - i)) / (n - 4)) for i in range(n)]
    return SD._shear(grid, offs)


def _gf_body(b=0, head=GF_HEAD, hx=0, hy=0, lean=0, hands=True, legs=('out_l', 'out_r'), arms='rub'):
    """lean > 0 = 后仰（受击），lean < 0 = 更驼。"""
    it = []
    hunch = max(0, 3 - lean)
    torso = _hunch(GF_TORSO, hunch) if lean <= 0 else SD._shear(GF_TORSO, SD._steps(11, lean))
    tx = 8 - (lean if lean > 0 else 0)
    if arms == 'rub':
        it.append((GF_FORE_F, 20 + hunch, 22 + b))          # 远侧小臂（在躯干后，只露一截）
    elif arms == 'fright':
        it.append((g_recolor(SD.ARM_UP, SD.FAR), 15 - lean, 8 + b))   # 远侧手臂举起（在身后）
    SD._place(it, _leg(legs[0], far=True), 10, 31)
    SD._place(it, _leg(legs[1]), 15, 31)
    it.append((SD.PELVIS, 9, 29))
    it.append((torso, tx, 18 + b))
    it.append((head, 13 + hunch + hx - (lean if lean > 0 else 0), 6 + b + hy))
    if arms == 'rub':
        it.append((GF_FORE_N, 15 + hunch, 21 + b))          # 近侧小臂斜着抬到胸前
        if hands:
            it.append((GF_HANDS, 20 + hunch, 20 + b))       # 两只手搓在一起
    elif arms == 'fright':
        it.append((SD.ARM_UP, 10 - lean, 11 + b))           # 近侧手臂护在脸前
    return SD._compose(W_, H_, it)


def gf_idle(k):
    if k == 0:
        return _gf_body(0)
    return _gf_body(1, hy=-1)                                    # 肩膀一沉、头一抬：“嘿嘿”


def gf_hurt():
    return _gf_body(1, head=GF_HEAD_SCARED, hx=-1, hy=1, lean=3, arms='fright', legs=('back', 'fwd'))


# ------------------------------------------------------------------ 倒地（侧面仰躺，头朝左）
GF_LYING = """
...............................hH.
..nnIIjjjjjjjjjjxxxxxxxxxxxxxxxhH.
.nnrrIjjjjjjjjjjLxxxxxxxxxxxxxxhHH
.IjjrjjjjjjjEjjjxxxxxxxxxxxxxxxHHH
IjjjjjjjjjjjjjjjxxxxxxxxxxxxxxxX..
jjjjjjjssssjjjjjxxxxxxxxxxxxxxxX..
jjjjjjSsSSsjjjjEXXXXXXXXXXXXXXXX..
.JjjjjjjjjjjjjJJXXXXXXXXXXXXXXXX..
..JJJJJJJJJJJJJJXXXXXXXXXXXXXXX...
"""


def gf_down():
    head = SD._ol(GF_HEAD_BLANK)
    # 头逆时针转 90°：头顶朝左、脸朝上（同 avdol.down / kakyoin.down 的处理）
    ls = g_lines(head)
    h, w = len(ls), len(ls[0])
    rot = g_join(''.join(ls[x][w - 1 - y] for x in range(h)) for y in range(w))
    rh = len(g_lines(rot))
    g = g_new(W_ + 20, 22)
    g = SD._st(g, GF_LYING, 14, 21 - 9)              # 身体 9 行，最底一行贴地（描边在第 21 行）
    g = g_stamp(g, rot, 0, 22 - rh)                   # 头也贴地
    return g


# ------------------------------------------------------------------ 座位上只露头肩（16×18）
def gf_seated():
    g = g_new(16, 18)
    sh = """
...IIjjjsnjj..
.IIjjjjjjnrnj.
IIjjjjjjjnrnjj
Ijjjjjjjjjrjjj
"""
    g = SD._st(g, sh, 1, 14)
    g = SD._st(g, GF_HEAD, 1, 1)
    return g


# ------------------------------------------------------------------ 头像 32×32（DIO 模块的 _portrait 画法）
GF_FACE = """
..........ssssssssss..........
.......ssssssssssssssis.......
.....sssssSSSSssssssssss......
....qsssssssssSSSSssssss......
...qqssssSSSssssssssSSsss.....
..qqqsssssssSSSSSsssssss......
..qiqqssssssssssssssssss......
.qqiqqsssqqqqqqssssqqqqqs.....
.qqqqqssqqQqqqqqsssqqqqqqs....
.qQqqSssDDDDDDDssssDDDDDDs....
qqQqqSsDWWWkkDsssssDWkkDss....
qqQqSSssDDDDDsssssssDDDsss....
qQqqSDsssssssssssssssssssss...
qQqqSDsSsssssssssSsssssssss...
qQqqSsDsSssssssssSSsssssssss..
.qQqSsDsssSssssssSSSSsssssssss
.qQqSssDssSsssssssSSSSSsssss..
.qQqSssDsssDsssssDssssSSSss...
..qQSsssDsskkkkkkkkkkkkkSs....
..qQSsssssskWWkWWWkWWkkS......
..qQqSssssssskkkkkkkkkS.......
...qQqSSssssssssssssSS........
...qQqqSSSssssssssSSS.........
....qQq..SSSSSSSSSS...........
....qQq.....ssssSS............
.....qQjjjjnnrrnnjjjjJ........
...IjjjjjjjjnrrnjjjjjjjJJ.....
..IjjjjjjjjjjnRnjjjjjjjjJJ....
.IjjjjjjjjjjjjEjjjjjjjjjjJJ...
"""
GF_FACE_TALK = {19: '..qQSsssssskWWkWWWkWWkkS......',
                20: '..qQqSsssssskRRRRRRRRkS.......',
                21: '...qQqSSsssskkkkkkkkSS........'}
GF_FACE_SCARED = {4: '...qqssssSSSssssssssSSsssu....',
                  5: '..qqqsssssssSSSSSssssssu......',
                  6: '..qiqqsqqqqqqsssssqqqqqqs.....',
                  7: '.qqiqqssssssssssssssssssss....',
                  8: '.qqqqqsskkkkkkssssskkkkkks....',
                  9: '.qQqqSsskwwwwwkssssskwwwwks...',
                  10: 'qqQqqSsskwwekwkssssskwewks....',
                  11: 'qqQqSSssskkkkksssssskkkkss....',
                  18: '..qQSsssDssssskkkkkkksSs......',
                  19: '..qQSssssssssskRRRRRkS........',
                  20: '..qQqSssssssssskRRRkS.........',
                  21: '...qQqSSsssssssskkkSS.........'}


def _face(rows):
    ls = g_lines(GF_FACE)
    for k, row in rows.items():
        ls[k] = row.ljust(len(ls[0]), '.')[:len(ls[0])]
    return g_join(ls)


def gf_portrait(rows=None):
    return SD._portrait(_face(rows or {}))


# ------------------------------------------------------------------ 注册
def _def(name, frames, desc, fps=None, anchor='mb'):
    sprite.define(name, frames, pal=GF_PAL, anchor=anchor, desc=desc, fps=fps)
    NEW.append(name)


_def('grayfly.idle', [gf_idle(0), gf_idle(1)],
     'Gray Fly: hunched old man in a grey-blue suit, bald with wild white tufts, rubbing his hands with a creepy '
     'grin; f1 shoulders twitch ("heh heh")', fps=3)
_def('grayfly.seated', [gf_seated()],
     'head and shoulders only, for the plane seat (16x18); anchor = bottom centre', )
_def('grayfly.hurt', [gf_hurt()], 'knocked back, terrified, arms flung out')
_def('grayfly.down', [gf_down()], 'collapsed on his back, head LEFT, eyes rolled white; anchor = ground')
_def('grayfly.portrait', [gf_portrait(), gf_portrait(GF_FACE_TALK)],
     'bust: ear-to-ear yellow-toothed grin; f0 mouth closed, f1 talking')
_def('grayfly.portrait_scared', [gf_portrait(GF_FACE_SCARED)], 'bust: terrified, eyes bulging, sweat')


if __name__ == '__main__':
    from assets import sprites_enemies  # noqa: F401  （对照用 enya）
    out = os.path.join(r'C:\Users\yui\AppData\Local\Temp\claude\D----\dd592801-8a86-495b-83a0-71d863169d18'
                       r'\scratchpad\m1\p7a', 'grayfly_dev.png')
    AC.preview_names(['grayfly.idle', 'grayfly.hurt', 'grayfly.down', 'grayfly.seated', 'grayfly.portrait',
                      'grayfly.portrait_scared'], out, 'grayfly', compare=['telence.idle', 'enya.idle'], scale=6)
    print(out)
