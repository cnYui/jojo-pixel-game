"""art_heroes -- 主角团本体补帧（技术约定 §3.14 A；规划 §5.1.6 / §5.2.5 / §7.1）。

每个角色用它**自己的**骨架（报告 08 §2 / §5.3）：
  承太郎 = sprites_jojo 的 class G + j_frame；花京院 / 阿布德尔 / 波鲁纳雷夫 = sprites_crew 的部件网格 + compose。
新动作名都是新名字（D12），不重新 define 任何原有名字。
import 即注册；单独运行（python -B art_heroes.py）出 4 倍预览到 tools\\art\\_preview\\。
"""
import sys
sys.dont_write_bytecode = True
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art_common as AC                       # noqa: E402  （设好 sys.path）

from engine import sprite                     # noqa: E402
from engine.sprite import g_lines, g_join     # noqa: E402
from assets import sprites_jojo as SJ         # noqa: E402
from assets import sprites_crew as sc         # noqa: E402

NEW = []          # 本模块注册的新精灵名（预览 / 自检用）
ONESHOT = set()
STATIC_STATES = set()
CHAR_INFO = {}
ACTION_ZH = {'guard': '格挡', 'dodge': '闪避'}


def _def(name, frames, pal, desc, fps=None, anchor='mb'):
    sprite.define(name, frames, pal=pal, anchor=anchor, desc=desc, fps=fps)
    NEW.append(name)


def _cdef(name, frames, pal, desc, fps=None, size=None):
    sc.define(name, frames, pal, desc, fps=fps, size=size)
    NEW.append(name)


# =====================================================================================
#  承太郎（SJ.j_frame，36×52）
# =====================================================================================
G, j_frame = SJ.G, SJ.j_frame
FIST, HAND_OPEN, SLEEVE_H, JPAL = SJ.FIST, SJ.HAND_OPEN, SJ.SLEEVE_H, SJ.JPAL

# L：帽檐压低（J_HEAD_LOW，只露一点眼光）+ 双前臂交叉护在下巴前，弓步稳住，外套下摆外张
J_GUARD = j_frame(head=SJ.J_HEAD_LOW,
                  arm_n=dict(pts=[(12, 23), (16, 30), (25, 22)], hand=FIST),
                  arm_f=dict(pts=[(26, 23), (31, 28), (29, 21)], hand=FIST),
                  legs=([(16, 35), (12, 47), 'flat'], [(22, 35), (26, 47), 'flat']),
                  coat=dict(back=2, front=2), k=-0.04, dy=1)
_def('jotaro.guard', [J_GUARD], JPAL, 'guard (L): forearms crossed in front of the chin, cap pulled low, braced stance')

# K：后撤步、整个人后仰、双手张开保持平衡、外套后摆飞起
J_DODGE = j_frame(arm_n=dict(pts=[(12, 23), (7, 27), (3, 30)], hand=HAND_OPEN),
                  arm_f=dict(pts=[(26, 23), (30, 25), (33, 23)], hand=HAND_OPEN),
                  legs=([(16, 35), (9, 46), 'toe'], [(22, 35), (23, 41), (21, 47), 'flat']),
                  coat=dict(tail=(0, 39), front=1), k=-0.20, dy=1)
_def('jotaro.dodge', [J_DODGE], JPAL, 'dodge (K): quick back-step, leaning back, coat tail flying')


def _j_down():
    """58×22：仰躺、头朝左、闭眼咬牙；锚点 mb = 地面（报告 08 §6.1 原型，按 §3.14 改成 22 高）。"""
    g = G(58, 22)
    gy = 20
    g.limb((33, gy - 4), (43, gy - 7), 'XxxX')                      # 远腿屈膝
    g.limb((43, gy - 7), (52, gy - 4), 'XxxX')
    g.stamp('hh.|hhh|hhh|HHh'.replace('|', '\n'), 52, gy - 8)
    g.limb((33, gy - 1), (51, gy - 1), 'xxxX', sep='k')            # 近腿平放
    g.stamp('hh|hh|hh|hh|HH'.replace('|', '\n'), 52, gy - 4, sep='k')
    g.poly([(30, gy - 9), (38, gy - 8), (42, gy), (28, gy)], 'n', top='q', bottom='N')        # 下摆铺地
    g.poly([(15, gy - 10), (31, gy - 9), (31, gy), (15, gy)], 'n', top='q', bottom='N', sep='k')   # 躯干
    g.poly([(19, gy - 9), (29, gy - 8), (29, gy - 6), (19, gy - 7)], 'j')                   # 内衫
    g.limb((29, gy - 8), (29, gy - 1), 'H')
    g.put(29, gy - 5, 'y')                                          # 腰带扣
    for x, y in ((18, gy - 9), (19, gy - 8), (21, gy - 8), (22, gy - 7)):
        g.put(x, y, 'y')                                            # 金链
    head = SJ.rot_ccw(g_join(r[3:23] for r in g_lines(SJ.J_HEAD_HURT)))   # 去掉发尾 3 列 → 旋转后 16×20
    g.stamp(head, 1, gy - 19, sep='k')
    g.limb((19, gy - 4), (29, gy - 3), 'qnnN', sep='k')             # 手臂贴身
    g.stamp(FIST, 29, gy - 5, sep='k')
    return g.outline().s()


_def('jotaro.down', [_j_down()], JPAL, 'knocked down on his back, head LEFT, eyes shut (58x22); anchor = ground')


# =====================================================================================
#  crew 公用：在名义画布上用 class G 的粗线画手臂，转成 crew 的 numpy 部件
# =====================================================================================
def _crew_part(draw, w=32, h=48):
    """draw(g) 在 G(w,h) 上画；返回 numpy 部件（'.' 透明），放在 (0,0)。"""
    g = G(w, h)
    draw(g)
    return sc.G(g.s())


# =====================================================================================
#  花京院（sc._ka，32×48）
# =====================================================================================
KA_SLEEVE = 'lgggG'        # 前臂袖子：左高光、右阴影（同 KA_ARM_F_DOWN）
KA_SLEEVE_H = 'lggG'       # 横向时从上到下
KA_BACK = 'GGG'            # 后臂整条用阴影色


def _ka_guard_arms():
    """双前臂交叉在胸前（X 字），拳在下巴前方；后臂（暗）在前臂后面。坐标 = _ka 的名义画布（未加 dy）。"""
    def back(g):
        g.limb((11, 23), (14, 30), 'GGG')           # 后上臂
        g.limb((14, 30), (23, 23), 'GGG')           # 前臂斜着往上、往前（X 的一笔）
        g.stamp('YY|YY'.replace('|', '\n'), 22, 22)
        g.stamp('.SS|SSS|.S.'.replace('|', '\n'), 23, 20)

    def front(g):
        g.limb((21, 23), (24, 30), 'lggG')          # 前上臂往下
        g.limb((24, 30), (15, 23), 'lggG')          # 前臂往上、斜过胸前（X 的另一笔）
        g.stamp('YYY|YYY'.replace('|', '\n'), 14, 22)
        g.stamp('.ss|sss|sS.'.replace('|', '\n'), 13, 20)
    return _crew_part(back), _crew_part(front)


_KB, _KF = _ka_guard_arms()
KA_GUARD = sc._ka(farm=None, barm=None, legs=sc.KA_LEGS_BRACE, tail=sc.KA_TAIL_STRIDE, dx=-1,
                  extra=[(_KB, 0, -1, 'k'), (_KF, 0, -1, 'k')])
_cdef('kakyoin.guard', [KA_GUARD], sc.KA_PAL, 'guard (L): forearms crossed in an X before the chest, braced')

# K（报告 08 §6.3 原型，零新像素）：后撤步、甩手、下摆被风掀起
KA_DODGE = sc._ka(dx=-2, hdx=-1, hdy=1, farm=(sc.KA_ARM_F_FLING, 18, 14),
                  legs=sc.KA_LEGS_STRIDE_A, tail=sc.KA_TAIL_WIND)
_cdef('kakyoin.dodge', [KA_DODGE], sc.KA_PAL, 'dodge (K): back-step, arm flung, coat tail blown back')


# =====================================================================================
#  阿布德尔（sc._av，32×48）
# =====================================================================================
def _av_guard_arms():
    """宽袖长袍：前臂竖在身前、掌心朝前（火墙起手），后臂握拳收在胸口。"""
    def back(g):
        g.limb((12, 20), (15, 26), 'AAAA')
        g.limb((15, 26), (20, 24), 'AAA')
        g.stamp('DDD|DDD'.replace('|', '\n'), 19, 23)

    def front(g):
        g.limb((21, 20), (25, 26), 'qaaaA')         # 上臂往前下
        g.limb((25, 27), (27, 19), 'qaaA')          # 前臂竖起
        g.stamp('d.d.|dddd|dddD|.dD.'.replace('|', '\n'), 26, 14)   # 张开的手掌朝前
    return _crew_part(back), _crew_part(front)


_AB, _AF = _av_guard_arms()
AV_GUARD = sc._av(farm=None, barm=None, legs=sc.AV_LEGS_BRACE, hem=sc.AV_HEM_STRIDE,
                  braids=sc.AV_BRAIDS_WIND, bdx=-2, bdy=-1, dx=-1,
                  extra=[(_AB, -1, 0, 'k'), (_AF, -1, 0, 'k')])
_cdef('avdol.guard', [AV_GUARD], sc.AV_PAL, 'guard (L): forearms crossed before the chest, palms out, braids blown')

# K：后仰后撤（AV_LEGS_STRIDE_B），前臂甩起，辫子和下摆被风掀起
AV_DODGE = sc._av(head=sc.AV_HEAD, hdx=-2, hdy=1, dx=-2, braids=sc.AV_BRAIDS_WIND, bdx=-3, bdy=-1,
                  farm=(sc.AV_ARM_F_FLING, 18, 11), legs=sc.AV_LEGS_STRIDE_B, hem=sc.AV_HEM_WIND)
_cdef('avdol.dodge', [AV_DODGE], sc.AV_PAL, 'dodge (K): leaning back-step, arm flung up, braids and hem blown')


# =====================================================================================
#  波鲁纳雷夫（sc._po；倒地 60×22，报告 08 §6.3 原型）
# =====================================================================================
PO_LYING = sc.G("""
...................................HH
..ssss.............................hH
.TTtttttttttsssshhppppppppppppppp..hH
TTtttttttttttsssshhpppppppppppppppphH
ttttttttttttttSSShhppppppppppppppppHH
tttttsstttttttSSShhpppppppppppppppp..
ttttsSsttttttttSShhPPPPPPPPPPPPPPPP..
tttttttttttttttttthPPPPPPPPPPPPPPP...
.ttttttttttttttttthPPPPPPPPPPPPPPP...
""")


def _po_down():
    face = sc.PO_FACE_PAIN.copy()
    face[3, 5:8] = list('sss')
    face[4, 5:8] = list('kkk')          # 闭眼
    face[3, 12:15] = list('sss')
    face[4, 12:15] = list('kkk')
    head = sc.put(sc.put(sc.blank(16, 21), sc.PO_HAIR, 0, 0), face, 0, 11)
    head = sc.rot_ccw(sc.crop(head))    # 发柱朝左平放、脸朝上
    d = sc.put(sc.put(sc.blank(60, 22), PO_LYING, 21, 11), head, 1, 3)
    return sc.outline(d)


_cdef('polnareff.down', [_po_down()], sc.PO_PAL, 'knocked down on his back, head LEFT, eyes shut (60x22); anchor = ground')


# =====================================================================================
#  伊奇（sc._ig，28×22）：K 沙翻滚（2026-10-10，抽帧审查：原来是一张剪切过的待机图，一帧不动）
#  缩成一团的波士顿梗（黑毛、白口鼻、白爪、粉耳朵、琥珀眼，原工程 IG_PAL）→ 逆时针转一圈的 4 帧（像素格直接转 90°，不变形）；
#  默认闪避往后退，面朝右时往左滚 = 逆时针。球心在名义画布中线、贴地，锚点 mb 同 iggy.idle
# =====================================================================================
IG_BALL = sc.G("""
.....xxxxxx.....
...xxXXXXXxxxm..
..xXXxxxxxxxxmmx
.xXxxxxxxxxxxxmx
.xXxxxxxxxxxxxx.
xXxxxxxxxxxKKKx.
xxxxxxxxxxxooKxx
xxxxxxxxxxwwwxxx
xxxxxxxxxwwwwwKK
xxxxxxxxwww1wwKx
yxxxxxxxw1111wx.
yyxxxxxxxw11wyy.
.yyxwwxxxxxxyy..
..yywwyyxwwyy...
...yyyyyyyyyy...
.....yyyyyy.....
""")


def _ig_roll():
    import numpy as np
    return [sc.compose(28, 22, [(np.rot90(IG_BALL, k).copy(), 6, 6)]) for k in range(4)]


_cdef('iggy.dodge', _ig_roll(), sc.IG_PAL,
      'dodge (K): sand roll - curled up into a ball, 4 frames turning counter-clockwise (rolls backward when facing right)', fps=16)
ONESHOT.add('iggy.dodge')


# =====================================================================================
if __name__ == '__main__':
    out = AC.PREVIEW
    AC.preview_names(['jotaro.guard', 'jotaro.dodge', 'jotaro.down', 'jotaro.point', 'jotaro.hurt'],
                     os.path.join(out, 'dev_jotaro.png'), 'jotaro 新帧（对照 idle / point / hurt）',
                     compare=['jotaro.idle'])
    AC.preview_names(['kakyoin.guard', 'kakyoin.dodge', 'kakyoin.cast', 'kakyoin.hurt'],
                     os.path.join(out, 'dev_kakyoin.png'), 'kakyoin', compare=['kakyoin.idle'])
    AC.preview_names(['avdol.guard', 'avdol.dodge', 'avdol.cast', 'avdol.hurt'],
                     os.path.join(out, 'dev_avdol.png'), 'avdol', compare=['avdol.idle'])
    AC.preview_names(['polnareff.down', 'polnareff.hurt'], os.path.join(out, 'dev_polnareff.png'),
                     'polnareff', compare=['polnareff.idle', 'kakyoin.down'])
    print('new:', NEW)
