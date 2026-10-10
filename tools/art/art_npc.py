"""art_npc -- M1 的 NPC（技术约定 §3.14 B；规划 §5.1.6 / §5.2.5 / §7.1）。

每个 NPC 用它“借”的那个原角色自己的骨架（报告 08 §2 / §5.3），换调色板 + 少量新画部件：
  女性（校医 / 女生 / 空姐 / 阿婆 / 妇人）= sprites_jojo 荷莉的 h_frame 画法（G 类关节坐标 + legs2 + 胸衣/裙子多边形），
      这里复制成 h_frame2（多了“裙子颜色 / 要不要围裙 / 袖子 / 腿色 / 头上加东西”几个开关），只用原模块的部件和函数；
  男性（狱警 / 男生 / 大排档老板 / 路人 A）= sprites_crew 花京院的 _ka 部件网格 + compose；
  算命先生 = sprites_crew 阿布德尔的 _av（长袍）；
  乘客 a–d = 新画 16×18 头肩小图（G 类画笔 + 统一描边），发色取原工程客舱背景里乘客头的四种颜色。
配色变体 = 独立 cid（§3.3）。所有名字都是新名字（D12）。
"""
import sys
sys.dont_write_bytecode = True
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art_common as AC                       # noqa: E402

from engine import sprite                     # noqa: E402
from engine.sprite import g_lines, g_join, g_recolor   # noqa: E402
from assets import sprites_jojo as SJ         # noqa: E402
from assets import sprites_crew as sc         # noqa: E402

NEW = []
ONESHOT = {'npc_nurse.stab'}
STATIC_STATES = set()
CHAR_INFO = {
    'npc_nurse': dict(zh='校医', en='School nurse', cat='NPC', typ='人物'),
    'npc_passenger_a': dict(zh='乘客（上班族）', en='Passenger A', cat='NPC', typ='人物'),
    'npc_passenger_b': dict(zh='乘客（妈妈）', en='Passenger B', cat='NPC', typ='人物'),
    'npc_passenger_c': dict(zh='乘客（打呼的大叔）', en='Passenger C', cat='NPC', typ='人物'),
    'npc_passenger_d': dict(zh='乘客（老奶奶）', en='Passenger D', cat='NPC', typ='人物'),
}
ACTION_ZH = {'possessed': '被附身', 'stab': '举钢笔', 'faint': '昏倒', 'seated': '坐着', 'slump': '被刺昏倒',
             'read': '看漫画', 'cheer': '欢呼', 'bow': '鞠躬'}

G = SJ.G
lean = SJ.lean
edits = SJ.edits


def _def(name, frames, pal, desc, fps=None, anchor='mb'):
    sprite.define(name, frames, pal=pal, anchor=anchor, desc=desc, fps=fps)
    NEW.append(name)


def _cdef(name, frames, pal, desc, fps=None, size=None):
    # 头像是字符网格，身体是 compose 的带边距数组；原包装只接受后者。
    if isinstance(frames[0], str):
        sprite.define(name, frames, pal=pal, anchor='mb', desc=desc, fps=fps)
    else:
        sc.define(name, frames, pal, desc, fps=fps, size=size)
    NEW.append(name)


# =====================================================================================
#  荷莉的骨架：h_frame 复制一份，加几个开关（原函数写死了围裙和光腿）
# =====================================================================================
def h_frame2(legs=None, arm_n=None, arm_f=None, head=SJ.H_HEAD, dy=0, k=0.0, hem=0, w=32, ox=0,
             hand_n=None, hand_f=None, sep_n='S', bodice=SJ.H_BODICE, apron=True, skirt=('c', 'C'),
             skirt_bottom=38, skirt_w=0, arm_cols=('sss', 'ssS', 'ssS', 'sSS'), leg_cols=('ssS', 'sSS'),
             shoe=SJ.H_SHOE, shoe_toe=SJ.H_SHOE_TOE, puff=True, hats=(), props_back=(), props_front=(),
             head_xy=(5, 9), head_dx=0):
    """同 SJ.h_frame（32×48，脚在最底行，身体中线 x=16）。
    arm_cols = (近臂上臂, 近臂前臂, 远臂上臂, 远臂前臂) 的色带；hats = [(grid, x, y)] 盖在头上；
    props_back = [(grid, x, y)] 最先画（身后的头发 / 马尾）；props_front = [(grid, x, y)] 最后盖（带分隔线 'k'）。
    skirt_w = 裙摆额外外张。head_dx = 头往前挪几 px：头、hats、props_back 都是整格坐标，一起挪（头身对位，见 NPC_HEAD_DX）；
    默认 0 = 和原工程 SJ.h_frame 逐字相同（art_holly_fix 断言这一点）。"""
    g = G(w, 48)
    legs = legs or ([(14, 38), (14, 44), 'flat'], [(18, 38), (18, 44), 'flat'])
    L = [[(p[0] + ox, p[1]) if isinstance(p, tuple) else p for p in leg] for leg in legs]
    SJ.legs2(g, L[0], L[1], cols_n=leg_cols[0], cols_f=leg_cols[1], shoe=shoe, shoe_toe=shoe_toe)
    up = G(w, 48)
    arm_n = arm_n or [(12, 24), (10, 29), (10, 33)]
    arm_f = arm_f or [(21, 24), (23, 29), (22, 33)]
    for grid, x, y in props_back:
        up.stamp(grid, x + ox + head_dx, y)
    pf = [(x + ox, y) for x, y in arm_f]
    up.limb(pf[0], pf[1], arm_cols[2])
    up.limb(pf[1], pf[2], arm_cols[3])
    hf = hand_f or SJ.H_HAND
    up.stamp(hf, pf[2][0] - len(g_lines(hf)[0]) // 2, pf[2][1] - len(g_lines(hf)) // 2)
    if puff:
        up.stamp(SJ.PUFF_F, 19 + ox, 22)
    sb = skirt_bottom
    up.poly([(11 + ox, 29), (21 + ox, 29), (24 + ox + hem + skirt_w, sb), (8 + ox + hem - skirt_w, sb)], skirt[0],
            left=skirt[0], right=skirt[1], bottom=skirt[1])
    if apron:
        up.poly([(13 + ox, 30), (19 + ox, 30), (20 + ox + hem, sb - 1), (12 + ox + hem, sb - 1)], 'm',
                left='M', right='M', bottom='w', sep=skirt[1])
    up.stamp(bodice, 10 + ox, 21)
    up.stamp(head, head_xy[0] + ox + head_dx, head_xy[1])
    for grid, x, y in hats:
        up.stamp(grid, x + ox + head_dx, y)
    pn = [(x + ox, y) for x, y in arm_n]
    up.limb(pn[0], pn[1], arm_cols[0], sep=sep_n)
    up.limb(pn[1], pn[2], arm_cols[1], sep=sep_n)
    hn = hand_n or SJ.H_HAND
    up.stamp(hn, pn[2][0] - len(g_lines(hn)[0]) // 2, pn[2][1] - len(g_lines(hn)) // 2, sep=sep_n)
    if puff:
        up.stamp(SJ.PUFF_N, 9 + ox, 22)
    for grid, x, y in props_front:
        up.stamp(grid, x + ox, y, sep='k')
    if k:
        lean(up, k, 38, rigid=22)
    up.shift(0, dy)
    g.stamp(up.s(), 0, 0)
    return g.outline().s()


# 荷莉的待机 / 走路参数（同 SJ.H_WALK），给所有借 h_frame 的人用
H_IDLE = [dict(), dict(dy=1, arm_n=[(12, 24), (10, 29), (10, 32)], arm_f=[(21, 24), (23, 29), (22, 32)])]
H_WALK = SJ.H_WALK

# 头身对位（用户 2026-10-09 晚看校园路截图：“这里角色的头和身体还是错位的……这些配角 NPC 还有没有这些情况？”）：
#   原工程 h_frame 把 15 px 宽的头盖在 x 5（身体中线 x 16），头发团整体落在身体后面约 4 px；
#   荷莉已由 art_holly_fix 往前挪 2 px（用户认可），借 h_frame2 的女性 NPC（校医 / 女生 a b / 空姐 / 阿婆 / 妇人）
#   同样挪 NPC_HEAD_DX：帽子、发髻、背后的长发 / 马尾是整格坐标，h_frame2 让它们跟头一起挪（不会再像警帽那样飘走）。
#   审计：tools\art\audit_heads.py（改前头偏 −4.5 ~ −6.0 px）。倒地帧（lying_frame）和胸像头像不受影响。
NPC_HEAD_DX = 2


def h_lying2(g, x0=4, y0=36, head=None, skirt=('c', 'C'), apron=True, leg_cols=('sSS', 'ssS'),
             shoe_cols=('r', 'R'), arm_cols='sS', hats=()):
    """SJ.h_lying 的复制（仰躺、头朝左、脸朝上）；颜色可换、围裙可关。地面 = y0 + 11。"""
    gy = y0 + 10
    sh, sH = shoe_cols
    g.limb((x0 + 33, gy - 4), (x0 + 40, gy - 4), leg_cols[0])
    g.limb((x0 + 33, gy - 2), (x0 + 41, gy - 2), leg_cols[1], sep='k')
    g.stamp(f'.{sh}|{sh}{sh}|{sh}{sH}|{sh}{sH}'.replace('|', '\n'), x0 + 40, gy - 7)
    g.stamp(f'.{sh}|{sh}{sh}|{sh}{sH}|{sH}{sH}'.replace('|', '\n'), x0 + 42, gy - 4, sep='k')
    c, C = skirt
    g.poly([(x0 + 22, gy - 8), (x0 + 34, gy - 6), (x0 + 36, gy), (x0 + 22, gy)], c, bottom=C, right=C, sep='k')
    if apron:
        g.poly([(x0 + 22, gy - 8), (x0 + 32, gy - 6), (x0 + 32, gy - 5), (x0 + 22, gy - 6)], 'm', top='i')
    g.poly([(x0 + 11, gy - 8), (x0 + 23, gy - 8), (x0 + 23, gy), (x0 + 11, gy)], c, bottom=C, sep='k')
    if apron:
        g.poly([(x0 + 12, gy - 8), (x0 + 22, gy - 8), (x0 + 22, gy - 6), (x0 + 12, gy - 6)], 'm', top='i')
        g.limb((x0 + 22, gy - 8), (x0 + 22, gy), 'M')
    g.stamp(SJ.rot_ccw(head or SJ.H_PROFILE_R), x0, y0 - 1, sep='k')
    for grid, x, y in hats:
        g.stamp(grid, x0 + x, y0 + y, sep='k')
    g.limb((x0 + 14, gy - 3), (x0 + 22, gy - 2), arm_cols, sep=C)
    g.stamp('ss|sS'.replace('|', '\n'), x0 + 22, gy - 3, sep=C)


def lying_frame(**kw):
    """48×14 的仰躺帧（锚点 mb = 地面中点）。"""
    g = G(48, 14)
    h_lying2(g, 3, 2, **kw)
    return g.outline().s()


# =====================================================================================
#  校医 npc_nurse（P0）：白大褂（荷莉的连衣裙改白）+ 浅蓝内衬（围裙位）+ 深棕盘发 + 浅粉护士帽（新画 10×4）
# =====================================================================================
NURSE_PAL = dict(SJ.HPAL, **{
    'y': '#43302a', 'Y': '#271a15', 'a': '#6a4c3c',          # 深棕头发
    'U': '#6e4a36',                                           # 棕色眼睛
    'c': '#f6f6fa', 'C': '#bcc0d2',                           # 白大褂
    'm': '#a8c8ee', 'M': '#6e90c8', 'i': '#d8e8fb',           # 浅蓝内衬
    'x': '#f8c6d6', 'X': '#d88ea8',                           # 浅粉护士帽
    'r': '#f2f2f6', 'R': '#9a2a44',                           # r = 白护士鞋（R 留给嘴）
    'g': '#5cff8c', 'G': '#1e9a4a',                           # 被附身的绿眼睛
})
NURSE_SHOE = g_recolor(SJ.H_SHOE, {'R': '1'})
NURSE_SHOE_TOE = g_recolor(SJ.H_SHOE_TOE, {'R': '1'})

# 盘发：荷莉的波波头收短，后脑多一个发髻
NURSE_HEAD = edits(SJ.H_HEAD,
                   (0, 11, '..Y.'), (0, 12, '.....'), (1, 12, '.'),
                   (0, 9, '.y'), (0, 10, '..'))
NURSE_BUN = 'yyy.|yaYy|yYYy|.YY.'.replace('|', '\n')
NURSE_CAP = """
..xxxxx...
.xxxwxxx..
xxxwwwxxX.
.XXXXXXXXX
"""
NURSE_HATS = [(NURSE_BUN, 3, 13), (NURSE_CAP, 7, 6)]
NURSE_HEAD_POSS = edits(NURSE_HEAD,
                        (6, 5, 'Skk.Skk'), (7, 6, 'kSsskS'),
                        (7, 7, 'glssgl'), (7, 8, 'GGssGG'),
                        (6, 9, 'sSSssSS'), (9, 10, 'kk'))
NURSE_KW = dict(shoe=NURSE_SHOE, shoe_toe=NURSE_SHOE_TOE, hats=NURSE_HATS, head=NURSE_HEAD, head_dx=NPC_HEAD_DX)

PEN_UP = 'B|b|b|z'.replace('|', '\n')          # 竖握的钢笔（笔尖朝下）
PEN_FWD = 'Bbbz'


def nurse_frames():
    idle = [h_frame2(**NURSE_KW, **p) for p in H_IDLE]
    walk = [h_frame2(**NURSE_KW, **p) for p in H_WALK]
    stiff = dict(arm_n=[(12, 24), (12, 29), (12, 34)], arm_f=[(21, 24), (21, 29), (21, 34)])
    poss = [h_frame2(**dict(NURSE_KW, head=NURSE_HEAD_POSS), **stiff, k=0.04),
            h_frame2(**dict(NURSE_KW, head=NURSE_HEAD_POSS), **stiff, k=0.04, dy=1)]
    stab = [
        h_frame2(**dict(NURSE_KW, head=NURSE_HEAD_POSS), arm_n=[(12, 24), (12, 17), (16, 12)],
                 hand_n=SJ.FIST, props_front=[(PEN_UP, 16, 13)], k=-0.05),
        h_frame2(**dict(NURSE_KW, head=NURSE_HEAD_POSS), arm_n=[(12, 24), (17, 24), (23, 27)],
                 hand_n=SJ.FIST, props_front=[(PEN_FWD, 24, 27)], k=0.10, hem=1),
    ]
    faint = lying_frame(head=edits(SJ.H_PROFILE_R, (5, 5, 'kk'), (5, 6, 'ss')), shoe_cols=('r', '1'),
                        hats=[(SJ.rot_ccw(NURSE_CAP), -2, 0)])
    return idle, walk, poss, stab, [faint]


# 头像：荷莉的胸像改发色 + 护士帽（帽子盖在头顶上）
def _nurse_port(talk=False, poss=False):
    p = SJ.H_PORT_TALK if talk else SJ.H_PORT
    p = edits(p, (12, 1, 'xxxxxx'), (10, 2, 'xxxxwxxxx'), (9, 3, 'xxxwwwxxxX'), (9, 4, 'XXXXXXXXXX'))
    if poss:
        p = edits(p, (11, 9, 'kkkk'), (21, 9, 'kkkk'),
                  (12, 11, 'glgg'), (22, 11, 'glgg'), (12, 12, 'GGGG'), (22, 12, 'GGGG'),
                  (13, 14, 'SSSS'), (20, 14, 'SSSS'), (14, 17, 'ssssss'), (14, 18, 'skkkks'), (15, 19, 'ssss'))
    return SJ.port_outline(p)


# =====================================================================================
#  乘客 npc_passenger_a–d（P0）：座椅上只露头肩（16×18，新画）。发色 = 原工程客舱乘客头的四种颜色
# =====================================================================================
P_BASE = {'s': '#f6c49a', 'S': '#d8946c', 'u': '#9cd8ff', 'R': '#8a2a34'}   # R = 嘴（统一深红）
PASS_PAL = {
    # a 上班族：黑发三七分、藏青西装、白衬衫、红领带
    'a': dict(P_BASE, a='#2c2626', A='#161212', q='#4e4646', b='#3a4a7a', B='#222c50', n='#5a6ca0',
              w='#f4f4f8', r='#d03040', x='#8a1c2a'),
    # b 妈妈：棕色波波头、米色针织开衫
    'b': dict(P_BASE, a='#5a3c24', A='#3a2414', q='#7e5a3a', b='#e8c8a0', B='#b8946c', n='#f8e4c8',
              w='#f4f4f8', r='#e07890'),
    # c 打呼的大叔：深棕头发秃了一块、胡茬、棕色夹克
    'c': dict(P_BASE, a='#3e2c22', A='#22160f', q='#5e4434', b='#8a6a44', B='#5e4428', n='#a8875c',
              w='#e8e0c8', d='#c8987a'),
    # d 老奶奶：灰白发髻、淡紫开衫
    'd': dict(P_BASE, a='#968c82', A='#6a625a', q='#c4bab0', b='#9a86b8', B='#6a5a8a', n='#bcaad6',
              w='#f4f4f8', r='#c06080'),
}

# 12×11 的 3/4 侧脸（朝右）：近眼在第 6 列、远眼在第 10 列，鼻尖在右缘，嘴在第 9 行
PASS_HEAD = {
    'a': """
...aaaaaa...
.aaqqaaaaaa.
aaqaaaaqaaaa
aaaaaaaaaaaa
aaaaSssssssa
aaaASsaasaa.
.aaASskssks.
.aaSsssssssS
..ASsssssSss
...SssssRRs.
....SSssss..
""",
    'b': """
...aaaaaa....
.aaqqaaaaaa..
aaqaaaaaaaaa.
aaaaaaaaaaaaa
aaaaaSssssaaa
aaaaSsssssssa
aaaASskssksa.
aaaASsssssss.
aaaaSssssSss.
.aaaSsssRRsa.
.aaa.SSsssa..
""",
    'c': """
....aaaa....
..aassssaa..
.aasssSssaa.
aaasssssssaa
aaaSsssssssa
aaASskkskk..
.aASssssssss
.aSsssssssSs
..SsdssRRRd.
...SdsdRRds.
....SSdddd..
""",
    'd': """
.qaa.........
qaaaa.aaaa...
aqaaaaqqqaa..
.aaaqaaaaaaa.
.aaaSsssssaa.
.aaSssssssssa
.aASskksskks.
..ASsssssssss
..aSssssssSS.
...SssssSSss.
....SSssssS..
""",
}
PASS_HEAD_SLUMP = {
    'a': """
...aaaaaa...
.aaqqaaaaaa.
aaqaaaaqaaaa
aaaaaaaaaaaa
aaaaSssssssa
aaaASsaasaa.
.aaASkksskk.
.aaSsssssssS
..ASsssssSss
...SsssRRRs.
....SSsRRs..
""",
    'b': """
...aaaaaa....
.aaqqaaaaaa..
aaqaaaaaaaaa.
aaaaaaaaaaaaa
aaaaaSssssaaa
aaaaSsssssssa
aaaASkkskksa.
aaaASsssssss.
aaaaSssssSss.
.aaaSsssRRsa.
.aaa.SSsRRa..
""",
    'c': """
....aaaa....
..aassssaa..
.aasssSssaa.
aaasssssssaa
aaaSsssssssa
aaASskkskk..
.aASssssssss
.aSsssssssSs
..SsdssssSd.
...SdsdkkRs.
....SSdddd..
""",
    'd': """
.qaa.........
qaaaa.aaaa...
aqaaaaqqqaa..
.aaaqaaaaaaa.
.aaaSsssssaa.
.aaSssssssssa
.aASskksskks.
..ASsssssssss
..aSssssssSS.
...SssssRRss.
....SSssRRS..
""",
}
PASS_BODY = {
    'a': """
...BbbwrwbbB....
..BbbbwxwbbbB...
.BbbbbbwbbbbbB..
BbbbbbbbbbbbbbB.
BnbbbbbbbbbbbbB.
""",
    'b': """
...bbwwwbbbB....
..bbbwnwbbbbB...
.bbbbbbbbbbbbB..
bnbbbbbbbbbbbbB.
bnbbbbbbbbbbbbB.
""",
    'c': """
...BbbwwwbbB....
..BbbbwwwbbbB...
.BbbbbbbbbbbbB..
BnbbbbbbbbbbbbB.
BnbbbbbbbbbbbbB.
""",
    'd': """
...bbwrrwbbb....
..bbbwrrwbbbb...
.bbbbbbbbbbbbb..
bnbbbbbbbbbbbbB.
bnbbbbbbbbbbbbB.
""",
}
# 被灰塔刺中（slump）：头歪下去（往前下方）、眼睛闭成一条线、嘴张开、冒汗；
# c（打呼的大叔）坐着时就闭眼张嘴打呼，被刺后嘴闭上、汗直流


def passenger(k, slump=False):
    g = G(16, 18)
    g.stamp(PASS_BODY[k], 0, 13)
    head = PASS_HEAD_SLUMP[k] if slump else PASS_HEAD[k]
    hx, hy = 2, 2
    if slump:
        hx, hy = 3, 4
    g.stamp(head, hx, hy, sep='k')
    if slump:
        g.put(14, hy + 2, 'u')
        g.put(14, hy + 3, 'u')
        g.put(15, hy + 4, 'u')
    return g.outline().s()


# =====================================================================================
#  男性 NPC：花京院的 _ka 骨架（部件网格 + compose）
# =====================================================================================
import numpy as np                            # noqa: E402

KA = sc.KA_PAL


def ext_legs(grid, n=4):
    """腿往上加长 n 行（上衣变短时补裤腿）：重复第一行。"""
    return np.vstack([grid[0:1]] * n + [grid])


def rc(grid, mapping):
    return sc.recolor(grid, mapping)


# 短发男头（16×19，和 KA_HEAD 同尺寸同摆位；脸取花京院的，去掉长刘海和樱桃耳环，眼珠改深色）
MALE_HEAD = sc.G("""
.....aaaaaa.....
...aaqqqaaaaa...
..aqqaaaaaaaaa..
.aqaaaaaaaaaaaa.
.aaaaqqaaaaaaaa.
.aaaaaassssssaa.
.AaaaSsskkkskkk.
.AAaSssswesswes.
.AAaSssswesswes.
..AaSssssssssSs.
..ASSsssssssss..
...SSSsssssfss..
....SSSsssssss..
......SSSSss....
................
................
................
................
................
""")
MALE_HEAD_SHOCK = sc.G("""
.....aaaaaa.....
...aaqqqaaaaa...
..aqqaaaaaaaaa..
.aqaaaaaaaaaaaa.
.aaaaqqaaaaaaaa.
.aaaaaakkssskku.
.AaaaSskwwskwwu.
.AAaSsskwesskwe.
.AAaSssskkssskk.
..AaSssssssssSs.
..ASSsssskkkss..
...SSSssskRks...
....SSSsskkkss..
......SSSSss....
................
................
................
................
................
""")

# 警帽（新画 15×5）：藏青帽身 + 金帽徽 + 黑帽檐（朝右伸出）。
#   ka2 的 hats 坐标是整格坐标（头在 (8, 6)），不是相对头：以前写 (-1, -1) 帽子飘在格子左上角、离头 9 px（用户 2026-10-09 截图）。
#   (8, 5) = 帽子和头左缘对齐、帽檐压在额头上面一行
POLICE_CAP_AT = (8, 5)
POLICE_CAP = sc.G("""
....ppppppp....
..ppppppppppp..
.pppppppyypppp.
.ppppppppppppp.
..PPPPPPPPKKKKKK
""")
POLICE_PAL = dict(KA, **{
    'a': '#1c1a20', 'A': '#0c0a10', 'q': '#38343e',          # 黑短发
    'g': '#2e3a6a', 'G': '#1a2244', 'l': '#4a5a92', 'N': '#10162e',   # 藏青制服
    'p': '#26305a', 'P': '#141a36',                           # 帽
    'u': '#b4cdf0', 'r': '#7a1c28', 'e': '#2a1e1a', 'f': '#c87a64',
    'h': '#1e1a1c', 'H': '#0a080a', 'w': '#ffffff',
})
P_TORSO = sc.G("""
..............sSS...............
............Guuuruug............
...........lgGuurGggg...........
..........llggGrGgggg...........
.........lllgggGGyggggG.........
.........llggggggGgggGG.........
.........lgggggggGyggGGG........
.........lgggggggGggGG..........
..........ggggggGyggGG..........
..........ggggggGgggGG..........
..........ggggggGyggGG..........
..........ggggggGgggGG..........
""")
P_TAIL = sc.G("""
..........ggggggGggggG..........
.........lggggggGgggggG.........
.........KKKKKKKyKKKKKK.........
""")
P_ARM = {k: rc(v, {'Y': 'G', 'y': 'G'}) for k, v in
         (('down', sc.KA_ARM_F_DOWN), ('fwd', sc.KA_ARM_F_FWD), ('back', sc.KA_ARM_F_BACK),
          ('bdown', sc.KA_ARM_B_DOWN), ('fling', sc.KA_ARM_F_FLING), ('cast', sc.KA_ARM_F_CAST),
          ('bcast', sc.KA_ARM_B_CAST))}


def ka2(head=MALE_HEAD, torso=sc.KA_TORSO, tail=sc.KA_TAIL_STAND, legs=sc.KA_LEGS_STAND, farm=None, barm=None,
        dy=0, dx=0, hdx=0, hdy=0, hats=(), extra=(), legs_y=39, tail_y=31, back=()):
    """sc._ka 的同款摆位（32×48），多了自定义躯干 / 下摆 / 腿的位置和头上的东西。"""
    dy += 1
    parts = [(legs, 0, legs_y)]
    parts += [(g, x + dx, y + dy) + tuple(rest) for g, x, y, *rest in back]
    parts.append((tail, dx, tail_y + dy))
    if barm is not None:
        parts.append((barm[0], barm[1] + dx, barm[2] + dy))
    parts.append((torso, dx, 20 + dy))
    hy = 6 if head.shape[0] == 19 else 5
    parts.append((head, 8 + dx + hdx, hy + dy + hdy))
    for g, x, y in hats:
        parts.append((g, x + dx + hdx, y + dy + hdy, 'k'))
    if farm is not None:
        parts.append((farm[0], farm[1] + dx, farm[2] + dy, 'k'))
    parts += [(g, x + dx, y + dy) + tuple(rest) for g, x, y, *rest in extra]
    return sc.compose(32, 48, parts)


SHORT = dict(legs_y=35, tail_y=31)         # 短上衣：腿从第 35 行起（ext_legs 补 4 行）


def legs_of(kind, mapping=None):
    g = {'stand': sc.KA_LEGS_STAND, 'strideA': sc.KA_LEGS_STRIDE_A, 'strideB': sc.KA_LEGS_STRIDE_B,
         'passA': sc.KA_LEGS_PASS_A, 'passB': sc.KA_LEGS_PASS_B, 'brace': sc.KA_LEGS_BRACE}[kind]
    return rc(g, mapping) if mapping else g


def male_walk(make):
    """花京院走路四帧的摆法（同 build_kakyoin）。make(legs_kind, farm_kind, dy, stride) -> frame。"""
    return [make('strideA', 'back', 0, True), make('passA', 'down', -1, False),
            make('strideB', 'fwd', 0, True), make('passB', 'down', -1, False)]


# ---------------------------------------------------------------- 狱警 npc_police（P1）
def police(legs='stand', farm='down', dy=0, head=MALE_HEAD, extra=(), barm='bdown', hdx=0, hdy=0):
    L = ext_legs(legs_of(legs))
    fa = None
    if farm:
        fa = {'down': (P_ARM['down'], 20, 21), 'fwd': (P_ARM['fwd'], 20, 21), 'back': (P_ARM['back'], 19, 21),
              'fling': (P_ARM['fling'], 19, 14), 'cast': (P_ARM['cast'], 19, 22)}[farm]
    ba = {'bdown': (P_ARM['bdown'], 8, 21), 'bcast': (P_ARM['bcast'], 13, 21), None: None}[barm]
    return ka2(head=head, torso=P_TORSO, tail=P_TAIL, legs=L, farm=fa, barm=ba, dy=dy, hdx=hdx, hdy=hdy,
               hats=[(POLICE_CAP,) + POLICE_CAP_AT], extra=extra, **SHORT)


MAG_OPEN = [sc.G("""
WWWWkWWWWW
WkkWkWkkWW
WWWWkWWWWW
WkkWkWkkkW
WWWWkWWWWW
1111k11111
"""), sc.G("""
.WWWkWWWW.
WkkWkWWkkW
WWWWkWWWWW
WkWWkWkkWW
WWWWkWWWWW
.111k1111.
""")]
STOOL = sc.G("""
hhhhhhhhhhh
HHHHHHHHHHH
.H.......H.
.H.......H.
.H.......H.
.HHHHHHHHH.
.H.......H.
.H.......H.
""")


def _sit_legs(mapping=None):
    """坐姿腿：大腿水平朝前、小腿垂直（G 类粗线画，花京院的裤子色带）。"""
    def draw(g):
        g.limb((13, 37), (21, 37), 'GNN')
        g.limb((21, 37), (21, 44), 'GNN')
        g.stamp('HHHH.|HHHHH'.replace('|', '\n'), 19, 45)
        g.limb((16, 36), (24, 36), 'gGG', sep='k')
        g.limb((24, 36), (24, 44), 'gGG', sep='k')
        g.stamp('hhhhH|HHHHH'.replace('|', '\n'), 22, 45, sep='k')
    g = G(32, 48)
    draw(g)
    a = sc.G(g.s())
    return rc(a, mapping) if mapping else a


def police_read(k):
    """坐在小凳上看漫画（2 帧：翻页）。"""
    blank_legs = sc.blank(32, 1)
    fr = ka2(head=MALE_HEAD, torso=P_TORSO, tail=P_TAIL[:2], legs=blank_legs, dy=3,
             farm=(P_ARM['cast'], 19, 22), barm=(P_ARM['bcast'], 13, 21),
             hats=[(POLICE_CAP,) + POLICE_CAP_AT], hdy=1,
             back=[(STOOL, 8, 36), (_sit_legs(), 0, 0)],
             extra=[(MAG_OPEN[k], 21, 19, 'k')], **SHORT)
    return fr


def police_frames():
    idle = [police(), police(dy=1)]
    walk = male_walk(lambda lg, fa, dy, s: police(lg, fa, dy))
    read = [police_read(0), police_read(1)]
    shock = police('brace', 'fling', head=MALE_HEAD_SHOCK, hdx=-1, hdy=-1, dy=-1)
    return idle, walk, read, [shock]


# ---------------------------------------------------------------- 男生 npc_student_m（P2）：黑立领学生服
STUDM_PAL = dict(KA, **{
    'a': '#1c1a22', 'A': '#0c0a10', 'q': '#3a3644',
    'g': '#22242e', 'G': '#121318', 'l': '#3a3e4e', 'N': '#08090c',
    'e': '#2a1e1a', 'f': '#d88a74',
})
SM_TORSO = rc(sc.KA_TORSO, {'y': 'G'})
for _yy in (4, 6, 8, 10):
    SM_TORSO[_yy, 17] = 'y'
SM_TAIL = sc.G("""
..........gggggggGggggG.........
.........lgggggggGgggggG........
.........lggggggGGGgggggG.......
""")
SM_ARM = {k: rc(v, {'Y': 'G'}) for k, v in (('down', sc.KA_ARM_F_DOWN), ('fwd', sc.KA_ARM_F_FWD),
                                              ('back', sc.KA_ARM_F_BACK), ('bdown', sc.KA_ARM_B_DOWN))}


def studm(legs='stand', farm='down', dy=0, **kw):
    fa = {'down': (SM_ARM['down'], 20, 21), 'fwd': (SM_ARM['fwd'], 20, 21), 'back': (SM_ARM['back'], 19, 21)}[farm]
    return ka2(torso=SM_TORSO, tail=SM_TAIL, legs=ext_legs(legs_of(legs)), farm=fa,
               barm=(SM_ARM['bdown'], 8, 21), dy=dy, **SHORT, **kw)


def studm_bow():
    """鞠躬：上半身整体前倾（行剪切，同 SJ.lean 的思路），头低下去。"""
    fr = studm()
    g = G(fr.shape[1], fr.shape[0])
    g.stamp(sc.S(fr), 0, 0)
    lean(g, 0.45, 47 - 12, rigid=0)
    return sc.G(g.s())


# ---------------------------------------------------------------- 大排档老板 npc_hk_owner（P1）：白汗衫 + 灰围裙 + 深色裤
OWNER_PAL = dict(KA, **{
    'a': '#242024', 'A': '#121014', 'q': '#44404a',
    'g': '#eeeef2', 'G': '#b8b8c8', 'l': '#ffffff', 'N': '#8a8aa0',     # 白汗衫
    't': '#8a8a94', 'T': '#5e5e6c',                                     # 灰围裙
    'x': '#3a3440', 'X': '#221e28',                                     # 深色裤子
    'e': '#2a1e1a', 'f': '#c87a64', 'd': '#c8a084',                     # d = 胡茬
})
OWNER_HEAD = MALE_HEAD.copy()
OWNER_HEAD[11, 6:13] = list('Sdsdsdf')
OWNER_HEAD[12, 6:12] = list('SSdddd')
OWNER_TORSO = rc(sc.KA_TORSO, {'y': 'G', 'Y': 'G'})
OWNER_TORSO[5:12, 12:20] = np.where(OWNER_TORSO[5:12, 12:20] != '.', 't', '.')
OWNER_TORSO[5, 11] = 'T'
OWNER_TORSO[5, 20] = 'T'
OWNER_APRON = {k: rc(v, {'g': 't', 'G': 'T', 'l': 't', 'y': 'T', 'Y': 'T'})
               for k, v in (('stand', sc.KA_TAIL_STAND), ('stride', sc.KA_TAIL_STRIDE))}
OWNER_ARM = {k: rc(v, {'Y': 'G'}) for k, v in (('down', sc.KA_ARM_F_DOWN), ('fwd', sc.KA_ARM_F_FWD),
                                               ('back', sc.KA_ARM_F_BACK), ('bdown', sc.KA_ARM_B_DOWN))}
DARK_LEGS = {'g': 'x', 'G': 'X', 'N': 'X'}


def owner(legs='stand', farm='down', dy=0, stride=False):
    fa = {'down': (OWNER_ARM['down'], 20, 21), 'fwd': (OWNER_ARM['fwd'], 20, 21),
          'back': (OWNER_ARM['back'], 19, 21)}[farm]
    return ka2(head=OWNER_HEAD, torso=OWNER_TORSO, tail=OWNER_APRON['stride' if stride else 'stand'],
               legs=legs_of(legs, DARK_LEGS), farm=fa, barm=(OWNER_ARM['bdown'], 8, 21), dy=dy)


# ---------------------------------------------------------------- 路人 A npc_hk_passer_a（P1）：短袖衬衫 + 深色裤
PASSER_A_PAL = dict(KA, **{
    'a': '#2a2224', 'A': '#140f10', 'q': '#4a3c3e',
    'g': '#7ab0d8', 'G': '#4a7aa8', 'l': '#a8d0ee', 'N': '#2e5480',     # 浅蓝衬衫
    'x': '#4a4438', 'X': '#2e2a22',                                     # 卡其深裤
    'e': '#2a1e1a', 'f': '#c87a64', 'w': '#ffffff',
})
PA_TORSO = rc(sc.KA_TORSO, {'y': 'G', 'Y': 'l'})
PA_TAIL = sc.G("""
..........gggggggGggggG.........
.........lggggggggggggGG........
""")
PA_ARM = OWNER_ARM


def passer_a(legs='stand', farm='down', dy=0):
    fa = {'down': (PA_ARM['down'], 20, 21), 'fwd': (PA_ARM['fwd'], 20, 21), 'back': (PA_ARM['back'], 19, 21)}[farm]
    return ka2(torso=PA_TORSO, tail=PA_TAIL, legs=ext_legs(legs_of(legs, DARK_LEGS)), farm=fa,
               barm=(PA_ARM['bdown'], 8, 21), dy=dy, **SHORT)


# =====================================================================================
#  算命先生 npc_fortune（P1）：阿布德尔的 _av（长袍）换成灰蓝长衫 + 黑瓜皮帽 + 圆墨镜（新画 6×2）
# =====================================================================================
FORTUNE_PAL = dict(sc.AV_PAL, **{
    'a': '#4a5a74', 'A': '#2a3448', 'q': '#6e80a0',                     # 灰蓝长衫
    'j': '#2a2630', 'J': '#16131a', 'L': '#100e14',                     # 黑裤 / 内衬
    'd': '#f0c49c', 'D': '#c89070', 'n': '#f8d8b8',                     # 肤色（原 d/D 是阿布德尔的深肤色）
    'x': '#1a1820', 'X': '#3a3644',                                     # 瓜皮帽
    'z': '#c8c4cc', 'Z': '#8e8a96',                                     # 花白的山羊胡
    'y': '#c89a20', 'l': '#8a4a3a',
})
FORTUNE_HEAD = sc.G("""
.....xxxxxx.....
...xxXXXxxxxx...
..xXXxxxxxyxxx..
.xxxxxxxxxxxxxx.
.zZddddddddddd..
.zZddkkkkdkkkk..
.zZdDkKKkdkKKk..
.zZDdkkkkdkkkkd.
.zZDdddddddddDdd
..zDddddddddd...
..zZDdddzzzzd...
...ZDDdddzzZ....
.....DDDDzZ.....
.......Zz.......
""")
FORTUNE_HEAD_TALK = FORTUNE_HEAD.copy()
FORTUNE_HEAD_TALK[10, 7:12] = list('dkkkk')
FORTUNE_HEAD_TALK[11, 8:11] = list('kRk')


def fortune(k):
    return sc._av(head=FORTUNE_HEAD if k == 0 else FORTUNE_HEAD_TALK, braids=None, dy=k,
                  farm=(sc.AV_ARM_F_CAST, 19, 18) if k else (sc.AV_ARM_F_DOWN, 21, 19))


# =====================================================================================
#  女性 NPC：荷莉的骨架（h_frame2）
# =====================================================================================
# 水手服胸衣（13×9，和 H_BODICE 同尺寸同位置）：藏青上衣、大领子（v 领色 + 白线 w）、领巾 x
SAILOR_BODICE = """
......ss.....
..vvwwsswwv..
.vwvvcxxcvwCC
.vwvccxxxcvCC
.cvccxxxxcCCC
.Cccccxxcccc.
..cccccxccccC
..ccccccccccC
.cCCCCCCCCCcC
"""
STUD_PAL = {
    'a': dict(SJ.HPAL, **{'y': '#1e1a22', 'Y': '#0e0c12', 'a': '#3e3846', 'U': '#3a2a22',
                          'c': '#2c3462', 'C': '#181d3e', 'v': '#2c3462', 'V': '#181d3e',
                          'x': '#e0303c', 'X': '#901828', 'r': '#6a4228', 'R': '#9a2a44', 'h': '#6a4228'}),
    'b': dict(SJ.HPAL, **{'y': '#6a4430', 'Y': '#442a1c', 'a': '#8e6248', 'U': '#4a3020',
                          'c': '#2c3462', 'C': '#181d3e', 'v': '#1e5a3e', 'V': '#0e3a26',
                          'x': '#f4f4f8', 'X': '#b8bccc', 'r': '#6a4228', 'R': '#9a2a44', 'h': '#6a4228'}),
}
STUD_SHOE = g_recolor(SJ.H_SHOE, {'R': 'H', 'r': 'h'})
STUD_SHOE_TOE = g_recolor(SJ.H_SHOE_TOE, {'R': 'H', 'r': 'h'})
LONG_HAIR = 'yyyy|yYyy|yyYy|yYyy|yyYy|.yYy|..yY'.replace('|', '\n')       # a：长直发垂在背后
PONYTAIL = '.yyy|yyaY|yyYy|.yYy|.yY.|..Y.'.replace('|', '\n')                # b：马尾
STUD_HEAD = {
    'a': edits(SJ.H_HEAD, (9, 10, 'Rs')),
    'b': edits(SJ.H_HEAD, (9, 10, 'Rs')),
}
STUD_HAPPY = {k: edits(SJ.H_HEAD_HAPPY) for k in 'ab'}
STUD_BACK = {'a': [(LONG_HAIR, 5, 17)], 'b': [(PONYTAIL, 2, 11)]}
SLEEVES = ('ccc', 'ccC', 'cCC', 'cCC')


def student(k, **p):
    kw = dict(bodice=SAILOR_BODICE, apron=False, arm_cols=SLEEVES, shoe=STUD_SHOE, shoe_toe=STUD_SHOE_TOE,
              head=STUD_HEAD[k], props_back=STUD_BACK[k], puff=False, head_dx=NPC_HEAD_DX)
    kw.update(p)
    return h_frame2(**kw)


def student_frames(k):
    idle = [student(k, **p) for p in H_IDLE]
    walk = [student(k, **p) for p in H_WALK]
    clasp = dict(arm_n=[(12, 24), (13, 29), (17, 27)], arm_f=[(21, 24), (21, 29), (18, 27)],
                 hand_n=SJ.H_HAND, head=STUD_HAPPY[k])
    cheer = [student(k, **clasp), student(k, **clasp, dy=-1, hem=1)]
    head_l = SJ.H_PROFILE_R
    down = lying_frame(head=edits(head_l, (5, 5, 'kk'), (5, 6, 'ss')), skirt=('c', 'C'), apron=False,
                       shoe_cols=('h', 'H'), arm_cols='cC')
    return idle, walk, cheer, [down]


# ---------------------------------------------------------------- 空姐 npc_stewardess（P1）：藏青制服 + 白衬衫 + 小帽（新画 8×3）
STEW_PAL = dict(SJ.HPAL, **{
    'y': '#1e1a22', 'Y': '#0e0c12', 'a': '#3e3846', 'U': '#3a2a22',
    'c': '#26305c', 'C': '#141a3a', 'm': '#f4f4f8', 'M': '#c4c8d8', 'i': '#ffffff',
    'x': '#26305c', 'X': '#141a3a', 'o': '#f0a030', 'r': '#141a3a', 'R': '#9a2a44',
})
STEW_CAP = 'xxxxxx..|xxxxoxxX|.XXXXXX.'.replace('|', '\n')
STEW_BUN = 'yyy.|yaYy|yYYy|.YY.'.replace('|', '\n')
STEW_BODICE = """
......ss.....
..cccmosccc..
.ccccmoocccCC
.cccmmimmccCC
.ccccmmmcccCC
.Cccccmccccc.
..cccccccccC.
..ccccyccccC.
.cCCCCCCCCCcC
"""
STEW_SHOE = g_recolor(SJ.H_SHOE, {'r': 'C', 'R': 'k'})
STEW_SHOE_TOE = g_recolor(SJ.H_SHOE_TOE, {'r': 'C', 'R': 'k'})
STEW_HEAD = edits(SJ.H_HEAD, (0, 11, '..Y.'), (0, 12, '.....'), (0, 9, '.y'), (0, 10, '..'))
STEW_KW = dict(bodice=STEW_BODICE, apron=False, arm_cols=SLEEVES, shoe=STEW_SHOE, shoe_toe=STEW_SHOE_TOE,
               head=STEW_HEAD, hats=[(STEW_BUN, 3, 13), (STEW_CAP, 9, 7)], puff=False, head_dx=NPC_HEAD_DX)


# ---------------------------------------------------------------- 卖粥阿婆 npc_hk_granny（P1）：灰白发髻、深色唐装、黑裤
GRANNY_PAL = dict(SJ.HPAL, **{
    'y': '#d8d4d0', 'Y': '#a8a29c', 'a': '#f4f2f0', 'U': '#4a3428',
    's': '#e8bc98', 'S': '#b48664',
    'c': '#2a3a5a', 'C': '#16203a', 'W': '#e8dcae',
    'x': '#2a2630', 'X': '#16131a', 'r': '#1a1820', 'R': '#9a2a44',
})
GRANNY_HEAD = edits(SJ.H_HEAD,
                    (0, 11, '..Y.'), (0, 12, '.....'), (0, 9, '.y'), (0, 10, '..'),
                    (6, 6, 'sSsssSs'), (7, 7, 'kkssskk'), (7, 8, 'SsssSs'),
                    (6, 9, 'SsssssS'), (8, 10, 'SkkS'))
GRANNY_BUN = '.yyy.|yyaYy|yYyYy|.YYY.'.replace('|', '\n')
GRANNY_BODICE = """
......ss.....
..cccccsccc..
.ccccWcWcccCC
.cccccWccccCC
.ccccWcWcccCC
.CccccWcccCC.
..ccccWcccCC.
..ccccccccCC.
.cCCCCCCCCCcC
"""
GRANNY_SHOE = g_recolor(SJ.H_SHOE, {'r': 'r', 'R': 'k'})
GRANNY_SHOE_TOE = g_recolor(SJ.H_SHOE_TOE, {'r': 'r', 'R': 'k'})
GRANNY_KW = dict(bodice=GRANNY_BODICE, apron=False, arm_cols=SLEEVES, leg_cols=('xxX', 'xXX'),
                 shoe=GRANNY_SHOE, shoe_toe=GRANNY_SHOE_TOE, head=GRANNY_HEAD, skirt_bottom=34,
                 hats=[(GRANNY_BUN, 2, 10)], puff=False, k=0.07, head_dx=NPC_HEAD_DX)


# ---------------------------------------------------------------- 抬头看的妇人 npc_hk_passer_b（P1）：碎花上衣 + 深色裙
PASSER_B_PAL = dict(SJ.HPAL, **{
    'y': '#2a2026', 'Y': '#150f13', 'a': '#4a3a44', 'U': '#3a2a22',
    'c': '#d86a5a', 'C': '#a03e3a', 'm': '#3a3448', 'M': '#221e2c', 'i': '#5a5470',
    'W': '#f8e4a0', 'r': '#3a2a22', 'R': '#9a2a44',
})
PB_BODICE = """
......ss.....
..cccccsccc..
.cWccccccWcCC
.cccWcccccCCC
.cccccWccCcCC
.CcWcccccccC.
..ccccWccccC.
..ccccccWccC.
.cCCCCCCCCCcC
"""
PB_KW = dict(bodice=PB_BODICE, apron=False, skirt=('m', 'M'), shoe=g_recolor(SJ.H_SHOE, {'R': 'k'}),
             shoe_toe=g_recolor(SJ.H_SHOE_TOE, {'R': 'k'}), head=edits(SJ.H_HEAD, (9, 10, 'Rs')),
             head_dx=NPC_HEAD_DX)


# =====================================================================================
#  头像
# =====================================================================================
# 短发男性胸像（32×32，脸取花京院的 KA_POR，去掉长刘海，眼珠深色）；衣服用 g/G/l，领口 Y/y
MALE_POR = """
................................
..........aaaaaaaa..............
........aaqqqqaaaaaa............
.......aqqaaaaaaaaaaa...........
......aqaaaaaaaaaaaaaa..........
.....aqaaaaaqqaaaaaaaaa.........
.....aaaaaqqaaaaaaaaaaaa........
....aaaaaqqaaaasssaaaaaaa.......
....aaaaaaaaassssssssssaa.......
....aAaaaaaaasssssssssssa.......
....aAaaaaSssssskkkkssssskk.....
....AAaaaSSsssssssssssssss......
....AAaaSSsssskkkkkssssskkk.....
.....AaaSSssswweeesssssswwes....
.....AaSDSssswweeessssssweess...
.....ASSDSsssssssssssssssssss...
.....SSDSsSSsssssssssSssssss....
......SSS..SSssssssssSSssss.....
...........SSsssssssssssss......
.............SSssSkkSsssss......
..............SSSsssssss........
...............sSSSSSSSs........
..........YyyyyyyyyyyyyY........
..........lgGGGGGGGGGGggg.......
........llgggggggggggggggg......
.......lllgggggggyggggggggG.....
......llgggggggggyggggggggGG....
....llllgggggggggyggggggggggG...
...lllggggggggggggyggggggggGGG..
..lllgggggggggggggyggggggggGGGG.
..llgggggggggggggyYgggggggggGGG.
..lggggggggggggggyggggggggggGGG.
"""
MALE_POR_TALK = [(17, 19, 'kkkk'), (17, 20, 'kRRk')]


def male_por(ops=(), talk=False):
    p = edits(MALE_POR, *ops)
    if talk:
        p = edits(p, *MALE_POR_TALK)
    return SJ.port_outline(p)


POLICE_POR_OPS = [(9, 1, 'pppppppppp'), (7, 2, 'pppppppppppppp'), (6, 3, 'pppppppyyppppppp'),
                  (5, 4, 'pppppppyyyyppppppp'), (5, 5, 'ppppppppppppppppppp'),
                  (5, 6, 'PPPPPPPPPPPPPKKKKKKKK'), (14, 7, 'KKKKKKKKKKK'),
                  (10, 22, 'GGGuuuruuuGG'), (10, 23, 'lgGGuurruGgg'), (17, 24, 'r'), (17, 25, 'G'),
                  (17, 26, 'G'), (17, 27, 'y'), (18, 28, 'G'), (18, 29, 'G'), (17, 30, 'y'), (17, 31, 'G')]
STUDM_POR_OPS = [(10, 22, 'GGGGGGGGGGGGGG'), (17, 25, 'y'), (17, 26, 'G'), (17, 27, 'G'), (18, 28, 'y'),
                 (18, 29, 'G'), (17, 30, 'G'), (17, 31, 'y'), (17, 19, 'SkkS')]
OWNER_POR_OPS = [(11, 17, 'SSdsdsdsdsdsd'), (11, 18, 'SSdsdsdsdsds'), (13, 19, 'SSdsSkkSsdsd'),
                 (14, 20, 'SSSdsdsdsd'), (10, 22, 'GGGGGGGGGGGGGG'),
                 (13, 24, 'tt'), (21, 24, 'tt'), (12, 25, 'tt'), (21, 25, 'tt'), (12, 26, 'tttttttttt'),
                 (11, 27, 'tttttttttttt'), (11, 28, 'tttttttttttt'), (11, 29, 'ttttttttttttt'),
                 (11, 30, 'ttttttttttttt'), (11, 31, 'ttttttttttttt')]
FORTUNE_POR = """
................................
...........xxxxxxxx.............
.........xxXXXXxxxxxx...........
........xXXxxxxxxxyxxx..........
.......xxxxxxxxxxxxxxxx.........
.......xxxxxxxxxxxxxxxxx........
......zzddddddddddddddddd.......
.....zZddddddddddddddddd........
.....zZdddkkkkkkdddkkkkkkd......
.....zZddkKKKKKkkkkKKKKKkd......
.....zZDdkKKKKKkddkKKKKKkd......
.....zZDddkkkkkdddkkkkkkdd......
.....zZDdddddddddddDddddddd.....
......ZDdddddddddddDDddddddd....
......ZDDddddddddddddDDDddd.....
.......zDDdddkkkkkkkkkdddd......
.......zZDdddzzzzzzzzzdddd......
........ZDDddzzzzzzzzzddD.......
.........DDdddzzzzzzzddD........
.........aDDDddzzzzzzdDa........
.......aaaaaDDDzzzzzDaaaaa......
.....aaaaaaaaajjjjjjaaaaaaaa....
...aaqaaaaaaaaajjjjaaaaaaaaaAA..
..aqqqaaaaaaaaaayyaaaaaaaaaaAAA.
.aqqqqaaaaaaaaaaaaaaaaaaaaaaAAA.
.aqqqaaaaaaaaaayyaaaaaaaaaaaAAA.
.aqqaaaaaaaaaaaaaaaaaaaaaaaaAAA.
.aqqaaaaaaaaaaayyaaaaaaaaaaaAAA.
.aqaaaaaaaaaaaaaaaaaaaaaaaaaAAA.
.aqaaaaaaaaaaaaaaaaaaaaaaaaaAAA.
.aqaaaaaaaaaaaaaaaaaaaaaaaaaAAA.
.aqaaaaaaaaaaaaaaaaaaaaaaaaaAAA.
"""
FORTUNE_POR_TALK = [(13, 15, 'kkkkkkkkk'), (13, 16, 'zkRRRRRkz')]


def female_por(ops=(), talk=False, base=None):
    p = base or (SJ.H_PORT_TALK if talk else SJ.H_PORT)
    return SJ.port_outline(edits(p, *ops))


def _por_recolor(grid, mapping):
    return g_recolor(grid, mapping)


# 女生：荷莉胸像的围裙（m/i）换成藏青，加水手领白线 + 领巾
STUD_POR_OPS = [(9, 22, 'vvwvvvvvvvwvv'), (7, 23, 'vvwvvvxxxxxvvwvv'), (5, 24, 'vvwvvvcxxxxxcvvwvv'),
                (13, 25, 'xxxxxx'), (14, 26, 'xxxx'), (15, 27, 'xx')]
STEW_POR_OPS = [(12, 1, 'xxxxxx'), (11, 2, 'xxxxoxxx'), (11, 3, 'XXXXXXXX'),
                (13, 23, 'mmmooomm'), (13, 24, 'mmmmoomm'), (14, 25, 'mmmmmm'), (14, 26, 'mmmmm')]
GRANNY_POR_OPS = [(9, 10, 'ssskkksssssskkks'), (9, 11, 'ssskkkssssssskkk'), (9, 12, 'sssSSSssssssSSSs'),
                  (9, 13, 'SsssssssssssssS'), (10, 15, 'SssssssssssSs'), (13, 17, 'Skkkks'),
                  (14, 18, 'SSSS'), (15, 19, 'ssss'),
                  (9, 1, 'yyyyy'), (7, 0, '.yyyyyy'),
                  (13, 24, 'cWcWcc'), (14, 26, 'WcW'), (14, 28, 'WcW'), (15, 30, 'W')]


def _port_body_recolor(p, mapping):
    """只换胸像下半（衣服）的颜色，脸和头发不动。"""
    ls = g_lines(p)
    out = ls[:21] + [g_recolor(r, mapping) for r in ls[21:]]
    return g_join(out)


# =====================================================================================
#  注册
# =====================================================================================
def register_p1():
    # 狱警
    idle, walk, read, shock = police_frames()
    _cdef('npc_police.idle', idle, POLICE_PAL, 'jail guard: navy police uniform + cap, light-blue shirt, tie; 2f bob',
          fps=2)
    _cdef('npc_police.walk', walk, POLICE_PAL, 'walk cycle (contact, pass, contact, pass)', fps=8)
    _cdef('npc_police.read', read, POLICE_PAL, 'sitting on a stool reading a manga weekly; f1 page turn', fps=2)
    _cdef('npc_police.shock', shock, POLICE_PAL, 'startled: eyes wide, sweat, arm flung up')
    _cdef('npc_police.portrait', [male_por(POLICE_POR_OPS), male_por(POLICE_POR_OPS, True)], POLICE_PAL,
          'bust: police cap, navy uniform; f1 talking', size=None)
    # 女生 a / b
    for k in 'ab':
        cid = f'npc_student_f_{k}'
        idle, walk, cheer, down = student_frames(k)
        look = 'long black hair, navy sailor uniform, red scarf' if k == 'a' else \
            'brown ponytail, navy sailor uniform with dark-green collar, white scarf'
        _def(f'{cid}.idle', idle, STUD_PAL[k], f'schoolgirl {k.upper()}: {look}; 2f bob', fps=2)
        _def(f'{cid}.walk', walk, STUD_PAL[k], 'walk cycle (contact, pass, contact, pass)', fps=8)
        _def(f'{cid}.cheer', cheer, STUD_PAL[k], 'hands clasped, happy ^_^, little hop on f1', fps=4)
        _def(f'{cid}.down', down, STUD_PAL[k], 'fainted on the floor, head LEFT (48x14); anchor = ground')
        pops = STUD_POR_OPS
        if k == 'b':
            pops = pops + [(1, 18, 'yy'), (0, 19, 'yyY'), (0, 20, 'yY')]
        por = [_port_body_recolor(female_por(pops), {'m': 'c', 'i': 'c', 'M': 'C'}),
               _port_body_recolor(female_por(pops, True), {'m': 'c', 'i': 'c', 'M': 'C'})]
        por = [SJ.port_outline(g_join(g_lines(p))) for p in por]
        _def(f'{cid}.portrait', por, STUD_PAL[k], 'bust: sailor uniform; f1 talking')
    # 空姐
    _def('npc_stewardess.idle', [h_frame2(**STEW_KW, **p) for p in H_IDLE], STEW_PAL,
         'flight attendant: navy uniform, white blouse, orange scarf, little cap, black bun; 2f bob', fps=2)
    _def('npc_stewardess.walk', [h_frame2(**STEW_KW, **p) for p in H_WALK], STEW_PAL, 'walk cycle', fps=8)
    _def('npc_stewardess.portrait', [_port_body_recolor(female_por(STEW_POR_OPS), {'m': 'c', 'i': 'c', 'M': 'C'}),
                                     _port_body_recolor(female_por(STEW_POR_OPS, True),
                                                        {'m': 'c', 'i': 'c', 'M': 'C'})],
         STEW_PAL, 'bust: cap, navy uniform; f1 talking')
    # 阿婆
    _def('npc_hk_granny.idle', [h_frame2(**GRANNY_KW, **p) for p in H_IDLE], GRANNY_PAL,
         'congee granny: grey-white bun, dark-blue Chinese jacket, black trousers, slight stoop; 2f bob', fps=2)
    _def('npc_hk_granny.walk', [h_frame2(**GRANNY_KW, **p) for p in H_WALK], GRANNY_PAL, 'walk cycle', fps=6)
    _def('npc_hk_granny.portrait', [_port_body_recolor(female_por(GRANNY_POR_OPS), {'m': 'c', 'i': 'c', 'M': 'C'}),
                                    _port_body_recolor(female_por(GRANNY_POR_OPS, True),
                                                       {'m': 'c', 'i': 'c', 'M': 'C'})],
         GRANNY_PAL, 'bust: wrinkled smile, grey bun; f1 talking')
    # 妇人
    _def('npc_hk_passer_b.idle', [h_frame2(**PB_KW, **p) for p in H_IDLE], PASSER_B_PAL,
         'Hong Kong woman: coral floral blouse, dark skirt, black bob; 2f bob', fps=2)
    _def('npc_hk_passer_b.walk', [h_frame2(**PB_KW, **p) for p in H_WALK], PASSER_B_PAL, 'walk cycle', fps=8)
    # 大排档老板
    _cdef('npc_hk_owner.idle', [owner(), owner(dy=1)], OWNER_PAL,
          'dai pai dong owner: white undershirt, grey apron, stubble; 2f bob', fps=2)
    _cdef('npc_hk_owner.walk', male_walk(lambda lg, fa, dy, s: owner(lg, fa, dy, s)), OWNER_PAL, 'walk cycle',
          fps=8)
    _cdef('npc_hk_owner.portrait', [male_por(OWNER_POR_OPS), male_por(OWNER_POR_OPS, True)], OWNER_PAL,
          'bust: stubble, white undershirt + apron; f1 talking')
    # 路人 A
    _cdef('npc_hk_passer_a.idle', [passer_a(), passer_a(dy=1)], PASSER_A_PAL,
          'Hong Kong passer-by: light-blue shirt, dark trousers; 2f bob', fps=2)
    _cdef('npc_hk_passer_a.walk', male_walk(lambda lg, fa, dy, s: passer_a(lg, fa, dy)), PASSER_A_PAL,
          'walk cycle', fps=8)
    # 算命先生
    _cdef('npc_fortune.idle', [fortune(0), fortune(1)], FORTUNE_PAL,
          'fortune teller: grey-blue long gown, black skullcap, round dark glasses, wispy goatee; f1 hands out '
          '(beckoning)', fps=2)
    _cdef('npc_fortune.portrait', [SJ.port_outline(FORTUNE_POR), SJ.port_outline(edits(FORTUNE_POR,
                                                                                      *FORTUNE_POR_TALK))],
          FORTUNE_PAL, 'bust: skullcap, round dark glasses, goatee; f1 talking')
    # 男生（P2）
    _cdef('npc_student_m.idle', [studm(), studm(dy=1)], STUDM_PAL, 'schoolboy: black gakuran, short black hair; 2f',
          fps=2)
    _cdef('npc_student_m.walk', male_walk(lambda lg, fa, dy, s: studm(lg, fa, dy)), STUDM_PAL, 'walk cycle', fps=8)
    _cdef('npc_student_m.bow', [studm_bow()], STUDM_PAL, 'bowing politely ("good morning!")')
    _cdef('npc_student_m.portrait', [male_por(STUDM_POR_OPS)], STUDM_PAL, 'bust: black gakuran, nervous')


CHAR_INFO.update({
    'npc_police': dict(zh='狱警', en='Jail guard', cat='NPC', typ='人物'),
    'npc_student_f_a': dict(zh='女生（a 配色）', en='Schoolgirl A', cat='NPC', typ='人物'),
    'npc_student_f_b': dict(zh='女生（b 配色）', en='Schoolgirl B', cat='NPC', typ='人物'),
    'npc_stewardess': dict(zh='空姐', en='Flight attendant', cat='NPC', typ='人物'),
    'npc_hk_owner': dict(zh='大排档老板', en='Dai pai dong owner', cat='NPC', typ='人物'),
    'npc_hk_granny': dict(zh='卖粥阿婆', en='Congee granny', cat='NPC', typ='人物'),
    'npc_hk_passer_a': dict(zh='香港路人 A', en='HK passer-by A', cat='NPC', typ='人物'),
    'npc_hk_passer_b': dict(zh='抬头看的妇人', en='HK passer-by B', cat='NPC', typ='人物'),
    'npc_fortune': dict(zh='算命先生', en='Fortune teller', cat='NPC', typ='人物'),
    'npc_student_m': dict(zh='男生', en='Schoolboy', cat='NPC', typ='人物'),
})


# =====================================================================================
#  注册（P0）
# =====================================================================================
def register():
    idle, walk, poss, stab, faint = nurse_frames()
    _def('npc_nurse.idle', idle, NURSE_PAL, 'school nurse: white coat over pale-blue scrubs, dark bun, pink cap; 2f bob',
         fps=2)
    _def('npc_nurse.walk', walk, NURSE_PAL, 'walk cycle (contact, pass, contact, pass)', fps=8)
    _def('npc_nurse.possessed', poss, NURSE_PAL, 'possessed by Hierophant Green: glowing green eyes, stiff arms; 2f',
         fps=4)
    _def('npc_nurse.stab', stab, NURSE_PAL, 'possessed stab: 0 pen raised high, 1 lunging forward with the pen',
         fps=8)
    _def('npc_nurse.faint', faint, NURSE_PAL, 'fainted on the floor, head LEFT (48x14); anchor = ground')
    _def('npc_nurse.portrait', [_nurse_port(), _nurse_port(True)], NURSE_PAL, 'bust: kind smile; f1 talking')
    _def('npc_nurse.portrait_possessed', [_nurse_port(poss=True)], NURSE_PAL, 'bust: possessed, green eyes')
    for k in 'abcd':
        cid = f'npc_passenger_{k}'
        _def(f'{cid}.seated', [passenger(k)], PASS_PAL[k],
             'plane passenger, head and shoulders above the seat back (16x18), facing right'
             + ('; snoring with mouth open' if k == 'c' else ''))
        _def(f'{cid}.slump', [passenger(k, True)], PASS_PAL[k],
             'stung by Tower of Gray: head slumped forward, eyes shut, sweat (16x18)')


register()
register_p1()


if __name__ == '__main__':
    out = os.path.join(r'C:\Users\yui\AppData\Local\Temp\claude\D----\dd592801-8a86-495b-83a0-71d863169d18'
                       r'\scratchpad\m1\p7a', 'npc_dev.png')
    AC.preview_names([n for n in NEW], out, 'npc', compare=['holly.idle', 'kakyoin.idle'], scale=5)
    print(out)
