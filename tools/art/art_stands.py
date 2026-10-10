"""art_stands -- 替身补帧（技术约定 §3.14 A；规划 §5.1.6 / §5.2.5 / §7.1）。

用 sprites_stands 自己的 `_Pix` 画笔 + 姿势表（报告 08 §2.4）：
  白金之星 / 红色魔术师 = `_brute_frame` + 姿势表副本（不改原字典）；
  绿色法皇 / 银色战车 = 原 `_hg_frame` / `_ch_frame` 复制一份改写（原函数读模块级姿势表、不能传参，
  报告 08 §2.4 “复制函数改坐标”），只用原模块的画笔、调色板、部件；
  灰塔 = sprites_enemies 的 `_tower` 帧 0 + 新画的针（同一套 `_Pix`）。
所有替身帧用 `SS._register(..., anchor=(20, 56))`，和原动作在同一 (x, y) 互换不跳。
"""
import sys
sys.dont_write_bytecode = True
import os
import math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art_common as AC                       # noqa: E402

import numpy as np                            # noqa: E402
from PIL import Image                         # noqa: E402
from engine import sprite                     # noqa: E402
from assets import sprites_stands as SS       # noqa: E402
from assets import sprites_enemies as SE      # noqa: E402

NEW = []
ANC = (20, 56)
# 多帧但“放一遍停在最后一帧”的动作（bake_art 补进 B.ONESHOT；技术约定 §3.14 A 的播放方式）
#   2026-10-10：上勾拳、红色魔术师重拳、愚者沙爪 / 砸地补成多帧（战斗抽帧审查的精灵问题 ②③⑤），同样放一遍停在最后一帧
ONESHOT = {'hiero.whip', 'magred.punch', 'chariot.slash', 'chariot.bare_thrust',
           'starplat.upper', 'magred.heavy', 'fool.claw', 'fool.slam'}
STATIC_STATES = set()
CHAR_INFO = {}
ACTION_ZH = {'upper': '上勾拳', 'reach': '伸手', 'whip': '触须鞭', 'slash': '横斩', 'parry': '架剑/弹剑',
             'bare_idle': '卸甲·待机', 'bare_thrust': '卸甲·突刺', 'needle': '塔针',
             'heavy': '重拳·火球', 'claw': '沙爪', 'slam': '沙拳砸地'}


def _reg(name, grids, pal, desc, fps=None, anchor=ANC):
    SS._register(name, grids, pal=pal, anchor=anchor, desc=desc, fps=fps)
    width = {'starplat.reach': 74, 'magred.punch': 64}.get(name)
    if width:
        sd = sprite.get(name)
        if sd.size[0] > width:
            raise ValueError(f'{name} 的不透明内容超过约定画布')
        # 自动裁边会缩短约定的招式画布，保留身体锚点并补足右侧透明区域。
        frames = []
        for im in sd.frames:
            out = Image.new('RGBA', (width, im.height))
            out.paste(im, (0, 0))
            frames.append(out)
        sprite.define(name, frames, anchor=sd.anchor, desc=desc, fps=fps)
    NEW.append(name)


# =====================================================================================
#  白金之星：SP_POSES 副本加 upper / hurt / reach
# =====================================================================================
SP_POSES2 = {k: dict(v) for k, v in SS.SP_POSES.items()}
SP_POSES2['upper'] = dict(lean=1, far=(8, 3, 12, 9, 14, 3), near=(-7, 4, 6, 6, 15, -9),
                          legs=((3, 19, 6, 26, 4, 35), (-3, 19, -7, 26, -11, 33)),
                          shout=True, near_front=True, sy=-1, w=48)
# 上勾拳补成 3 帧（2026-10-10，抽帧审查：upper 只有 1 帧，代码拿 punch 帧 0 垫蓄力）：
#   0 下蹲蓄力（拳头沉到腰侧、远手护下巴）→ 1 上冲（原 upper 帧，拳头擦着脸往上）→ 2 收势（拳头冲过头顶、身子拔高、后脚蹬地）
SP_POSES2['upper0'] = dict(lean=-1, far=(8, 3, 13, 9, 12, 0), near=(-8, 5, -14, 11, -8, 18),
                           legs=((3, 19, 8, 25, 6, 35), (-3, 19, -8, 25, -12, 34)), sy=2, w=44)
SP_POSES2['upper2'] = dict(lean=2, far=(8, 3, 12, 9, 9, 15), near=(-7, 4, 9, 1, 14, -17),
                           legs=((3, 19, 4, 27, 1, 35), (-3, 19, -8, 25, -13, 30)), shout=True, sy=-2, w=48)
SP_POSES2['hurt'] = dict(lean=-3, far=(8, 3, 14, 7, 20, 3), near=(-8, 4, -15, 6, -19, 2),
                         legs=((3, 19, 7, 26, 9, 34), (-3, 19, -7, 27, -12, 35)), sy=1)
SP_POSES2['reach'] = dict(lean=3, far=(8, 3, 12, 10, 14, 5), near=(-7, 4, 12, 3, 34, 2),
                          legs=((3, 19, 5, 27, 1, 35), (-3, 19, -8, 25, -14, 30)),
                          near_front=True, near_fist=False, w=74, open_hand=(34, 2))


def _open_hand(p, x, y, tones='avV'):
    """张开的手（朝右）：掌心椭圆 + 四根手指 + 拇指，_Pix 自动明暗 + 描边。"""
    m = p.ell(x, y, 2.6, 2.3)
    for ang, L in ((28, 4.6), (9, 5.4), (-10, 5.2), (-28, 4.2)):
        dx, dy = math.cos(math.radians(ang)), -math.sin(math.radians(ang))
        m |= p.cap(x + dx * 1.5, y + dy * 1.5, x + dx * (1.5 + L), y + dy * (1.5 + L), 0.95, 0.75)
    m |= p.cap(x - 0.5, y - 1.5, x + 1.0, y - 4.8, 1.0, 0.8)          # 拇指朝上
    p.paint(m, tones, hi=0.35, sh=0.62)


def _sp_front(p, cx, ty, ph, P):
    if P.get('open_hand'):
        hx, hy = P['open_hand']
        _open_hand(p, cx + hx, ty + hy)


SP_SPEC2 = dict(SS.SP_SPEC, poses=SP_POSES2, front=_sp_front)

_reg('starplat.upper', [SS._brute_frame(SP_SPEC2, 'upper0', 3, 0), SS._brute_frame(SP_SPEC2, 'upper', 0, 0),
                        SS._brute_frame(SP_SPEC2, 'upper2', 1, 0)], SS.SP_PAL,
     'J3 rising uppercut: 0 crouch wind-up (fist sunk at the hip), 1 drive (fist up past the face, shouting), '
     '2 follow-through (fist above the head, body stretched)', fps=12)
_reg('starplat.hurt', [SS._brute_frame(SP_SPEC2, 'hurt', 1, 0)], SS.SP_PAL,
     'recoil: leaning back, arms flung behind')
_reg('starplat.reach', [SS._brute_frame(SP_SPEC2, 'reach', 2, 0)], SS.SP_PAL,
     'reach / grab: near arm shot straight out, hand open (74 wide, body x=20)')


# =====================================================================================
#  红色魔术师：MR_POSES 副本加 punch_a / punch_b / block / hurt（保留 _mr_arm_deco 的火拳）
# =====================================================================================
MR_POSES2 = {k: dict(v) for k, v in SS.MR_POSES.items()}
MR_POSES2['punch_a'] = dict(lean=-1, far=(8, 3, 13, 9, 15, 3), near=(-8, 4, -13, 9, -10, 2),
                            legs=((3, 19, 7, 25, 5, 34), (-3, 19, -6, 27, -10, 34)), sy=1, w=48)
MR_POSES2['punch_b'] = dict(lean=3, far=(8, 3, 13, 10, 15, 4), near=(-7, 4, 5, 7, 25, 6),
                            legs=((3, 19, 5, 27, 1, 35), (-3, 19, -8, 25, -14, 30)), near_front=True,
                            w=64, trail=(25, 6))
MR_POSES2['block'] = dict(lean=0, far=(8, 3, 14, 11, 14, -1), near=(-8, 4, 3, 13, 7, 0),
                          legs=((3, 19, 7, 25, 5, 34), (-3, 19, -6, 26, -10, 33)), sy=1, nofire=True,
                          wall=True)
MR_POSES2['hurt'] = dict(lean=-3, far=(8, 3, 14, 7, 20, 3), near=(-8, 4, -15, 6, -19, 2),
                         legs=((3, 19, 7, 26, 9, 34), (-3, 19, -7, 27, -12, 35)), sy=1, nofire=True)
# 重拳（2026-10-10，抽帧审查：红色魔术师没有重拳帧，J3 火球 / 连打终结借 cast）：
#   0 蓄火——近手往后上方收到脑后、拳里聚起一大团火，身子后仰下沉；
#   1 重拳——大步前冲、近手直拳打到替身身前 27 px（离替身脚底 34 px，= AV_J3 的火球出手点），拳前炸开一团火球，远手收在腰后
MR_POSES2['heavy0'] = dict(lean=-2, far=(8, 3, 14, 8, 18, 4), near=(-8, 4, -14, 4, -12, -4),
                           legs=((3, 19, 7, 25, 6, 34), (-3, 19, -7, 26, -11, 34)), sy=1, w=44, nofire=True, gather=(-12, -4))
MR_POSES2['heavy1'] = dict(lean=4, far=(8, 3, 5, 11, 0, 10), near=(-7, 4, 6, 6, 23, 5),
                           legs=((3, 19, 5, 27, 1, 35), (-3, 19, -10, 24, -16, 29)), w=80, nofire=True, blast=(23, 5))


def _mr_deco2(p, s, e, f, ph, P):
    if P.get('nofire'):
        return
    SS._mr_arm_deco(p, s, e, f, ph, P)


def _mr_front2(p, cx, ty, ph, P):
    if P.get('trail'):
        # 拳头后面拖一道火（往左飘），拳前一圈小火花：J1/J2 的“炎拳”
        hx, hy = cx + P['trail'][0], ty + P['trail'][1]
        m = (p.poly([(hx - 3, hy - 3), (hx - 16, hy - 5), (hx - 22, hy - 1), (hx - 15, hy + 1), (hx - 3, hy + 3)])
             | p.ell(hx - 4, hy, 3.0, 3.2))
        p.paint(m, 'yoor', outline='R', hi=0.3, sh=0.6)
        p.fill(p.ell(hx - 5, hy, 2.0, 1.4) & m, 'i')
        for dx, dy in ((5, -4), (6, 3), (3, -6), (7, 0)):
            p.px(hx + dx, hy + dy, 'y')
    if P.get('wall'):
        # 交叉双臂前一排小火苗（挡格时的火墙起手）
        for i, (dx, h) in enumerate(((10, 7), (13, 10), (16, 8))):
            SS._flame(p, cx + dx, ty + 16 - i, h, ph + i, lean=0.1, w=2.0)
    if P.get('gather'):
        # 重拳蓄火：收在脑后的拳头里聚起一大团火（比待机手上的小火苗大一圈），周围几颗火星往拳心收
        gx, gy = cx + P['gather'][0], ty + P['gather'][1]
        SS._flame(p, gx + 0.5, gy + 1, 14, ph + 1, lean=-0.08, w=4.4)
        p.fill(p.ell(gx + 0.3, gy - 1.5, 2.2, 2.0), 'i')
        for dx, dy, ch in ((6, -9, 'y'), (-6, -7, 'o'), (7, 1, 'o'), (-5, 3, 'y'), (3, -14, 'y')):
            p.px(gx + dx, gy + dy, ch)
    if P.get('blast'):
        # 重拳出火球：拳前炸开一团火球（亮芯 + 往前喷的火舌），沿前臂往回拖一道火
        hx, hy = cx + P['blast'][0], ty + P['blast'][1]
        m = (p.ell(hx + 8, hy, 7.0, 6.0) | p.ell(hx + 16, hy - 1, 5.5, 4.6)
             | p.poly([(hx + 16, hy - 6), (hx + 33, hy - 3), (hx + 17, hy + 1)])
             | p.poly([(hx + 15, hy + 1), (hx + 31, hy + 7), (hx + 14, hy + 6)])
             | p.poly([(hx + 5, hy - 5), (hx + 25, hy - 11), (hx + 13, hy - 3)]))
        p.paint(m, 'yoor', outline='R', hi=0.3, sh=0.6)
        p.fill(p.ell(hx + 8, hy, 4.2, 3.2) & m, 'i')
        p.fill(p.ell(hx + 16, hy - 1, 2.6, 1.8) & m, 'i')
        tr = p.poly([(hx - 2, hy - 3), (hx - 15, hy - 5), (hx - 21, hy - 1), (hx - 14, hy + 1), (hx - 2, hy + 3)])
        p.paint(tr & ~m, 'yoor', outline='R', hi=0.3, sh=0.6)
        for dx, dy, ch in ((26, -9, 'y'), (34, 2, 'o'), (22, 10, 'y'), (30, -6, 'o'), (12, 9, 'o')):
            p.px(hx + dx, hy + dy, ch)
    SS._mr_front(p, cx, ty, ph, P)


MR_SPEC2 = dict(SS.MR_SPEC, poses=MR_POSES2, arm_deco=_mr_deco2, front=_mr_front2)

_reg('magred.punch', [SS._brute_frame(MR_SPEC2, 'punch_a', 0, 0), SS._brute_frame(MR_SPEC2, 'punch_b', 1, 0)],
     SS.MR_PAL, 'J1/J2 flame punch: 0 wind-up (fists burning), 1 cross punch with fire trail (64 wide, body x=20)',
     fps=18)
_reg('magred.heavy', [SS._brute_frame(MR_SPEC2, 'heavy0', 0, 0), SS._brute_frame(MR_SPEC2, 'heavy1', 1, 0)],
     SS.MR_PAL, 'heavy punch: 0 wind-up, near fist cocked behind the head gathering a big fireball; '
     '1 lunging straight, fireball bursting in front of the fist (fist 27 px ahead of body x=20, 34 px up)', fps=10)
_reg('magred.block', [SS._brute_frame(MR_SPEC2, 'block', 1, 0)], SS.MR_PAL,
     'guard: forearms up before the beak, small fire wall rising in front')
_reg('magred.hurt', [SS._brute_frame(MR_SPEC2, 'hurt', 0, 0)], SS.MR_PAL,
     'recoil: leaning back, arms flung behind')


# =====================================================================================
#  绿色法皇：_hg_frame 复制改写（加 lean / 张开的手 / 甩出的触须）
# =====================================================================================
def _ribbon_r(p, x, y, length, amp, freq, phase, r0, r1, tones, dy=0.0, step=1.0):
    """SS._ribbon 的镜像：从 (x,y) 往右飘的波浪带子。"""
    m = np.zeros((p.h, p.w), bool)
    prev = None
    n = int(length / step)
    for i in range(n + 1):
        u = i / max(1, n)
        px_ = x + i * step
        py_ = y + dy * u + amp * u * math.sin(freq * u * 6.283 + phase)
        r = r0 + (r1 - r0) * u
        if prev is not None:
            m |= p.cap(prev[0], prev[1], px_, py_, prev[2], r)
        prev = (px_, py_, r)
    p.paint(m, tones, hi=0.32, sh=0.6)
    return m


HG_ARMS2 = dict(SS.HG_ARMS)
HG_ARMS2['whip0'] = ((6, 2, 11, 6, 14, 3), (-6, 3, 5, 4, 15, 2))      # 近臂甩出
HG_ARMS2['whip1'] = ((6, 2, 11, 7, 13, 9), (-6, 3, -1, 9, 8, 6))      # 收回
HG_ARMS2['block'] = ((6, 2, 12, 5, 15, 0), (-6, 3, 4, 6, 13, 3))      # 双手张开护前
HG_ARMS2['hurt'] = ((6, 2, 12, 5, 17, 2), (-6, 3, -12, 4, -16, 1))     # 两臂向两边甩开


def _hg_frame2(pose, ph=0, bob=0, lean=0, width=40):
    HG_SKIN = SS.HG_SKIN
    p = SS._Pix(width, 56, SS._M)
    cx0, ty = 20, 18 + bob
    cx = cx0 + lean
    phase = ph * math.pi
    # 腰、膝下的飘带（身后）
    SS._hg_tendril(p, cx0 - 2, ty + 15, 24, phase, 8, 1.1, 0.6)
    SS._hg_tendril(p, cx0 + 1, ty + 17, 20, phase + 2.0, 14, 1.0, 0.6)
    for (hx, kx, fx, fdy, ph2) in ((cx0 + 2, cx0 + 4, cx0 + 2, 0, 0.8), (cx0 - 2, cx0 - 4, cx0 - 7, 1, 2.4)):
        m = p.cap(hx + lean // 2, ty + 17, kx, ty + 24, 2.6, 2.1)
        p.paint(m, HG_SKIN)
        SS._melon(p, m)
        SS._ribbon(p, kx + 1, ty + 25, 13, 2.0, 1.1, phase + ph2, 1.9, 0.6, 'tgGG', dy=11 + fdy)
    chest = p.ell(cx, ty + 5, 6.8, 5.4)
    waist = p.poly([(cx - 5, ty + 6), (cx + 5, ty + 6), (cx0 + 3, ty + 17), (cx0 - 3, ty + 17)])
    tm = chest | waist
    p.paint(tm, HG_SKIN, hi=0.26, sh=0.66)
    SS._melon(p, tm)
    for yy in (ty + 11, ty + 13, ty + 15):
        p.line([(cx - 3 + (lean * (ty + 17 - yy)) // 17, yy), (cx + 3 + (lean * (ty + 17 - yy)) // 17, yy)],
               'N', only='lgG')
    arms = HG_ARMS2[pose]

    def arm(a, open_=False):
        sx, sy, ex, ey, fx, fy = [v + (cx if i % 2 == 0 else ty) for i, v in enumerate(a)]
        m = p.cap(sx, sy, ex, ey, 2.3, 1.9) | p.cap(ex, ey, fx, fy, 1.9, 1.5)
        p.paint(m, HG_SKIN)
        SS._melon(p, m)
        if open_:
            hm = p.ell(fx, fy, 1.9, 1.7)
            for ang in (35, 5, -25):
                dx, dy = math.cos(math.radians(ang)), -math.sin(math.radians(ang))
                hm |= p.cap(fx + dx, fy + dy, fx + dx * 4.2, fy + dy * 4.2, 0.8, 0.7)
            p.paint(hm, 'lgG', hi=0.4, sh=0.6)
        else:
            hm = p.ell(fx, fy, 2.0, 1.8)
            p.paint(hm, 'lgG', hi=0.4, sh=0.6)
        return fx, fy
    open_ = pose == 'block'
    arm(arms[0], open_)
    p.paint(p.ell(cx + 6, ty + 2, 2.8, 2.4), 'lgGN', hi=0.35, sh=0.6)
    hx_off = -2 if pose == 'hurt' else 0
    p.paint(p.cap(cx + 1, ty - 3, cx + 1, ty + 1, 2.2), HG_SKIN)
    p.stamp(SS.HG_HEAD, cx - 5 + hx_off, ty - 16 + (1 if pose == 'hurt' else 0))
    p.paint(p.ell(cx - 6, ty + 2, 3.0, 2.6), 'lgGN', hi=0.35, sh=0.6)
    fx, fy = arm(arms[1], open_)
    if pose == 'whip0':
        # 甩出去的触须：从手上往右抽出去，末端细成一根线
        _ribbon_r(p, fx + 1, fy, 30, 3.2, 1.25, phase + 0.5, 1.7, 0.6, 'ttgG', dy=-3)
        _ribbon_r(p, fx + 1, fy + 1, 18, 2.4, 1.6, phase + 2.4, 1.2, 0.5, 'tgGG', dy=5)
    elif pose == 'whip1':
        # 收回：触须卷成弧拉回手边
        _ribbon_r(p, fx + 1, fy, 16, 4.0, 0.9, phase + 1.0, 1.6, 0.7, 'ttgG', dy=-6)
        _ribbon_r(p, fx, fy + 1, 11, 3.0, 1.1, phase + 3.0, 1.2, 0.6, 'tgGG', dy=4)
    return SS._clean_outline(p.grid())


_reg('hiero.whip', [_hg_frame2('whip0', 0, 0, lean=2, width=64), _hg_frame2('whip1', 1, 0, lean=1, width=48)],
     SS.HG_PAL, 'tentacle whip: 0 near arm flung out, tendrils lash forward; 1 tendrils curl back (body x=20)', fps=12)
_reg('hiero.hurt', [_hg_frame2('hurt', 1, 0, lean=-3)], SS.HG_PAL, 'recoil: leaning back, arms flung behind')
_reg('hiero.block', [_hg_frame2('block', 0, 0, lean=1)], SS.HG_PAL,
     'guard: both hands spread open in front (the vertical threads are drawn at runtime)')


# =====================================================================================
#  银色战车：_ch_frame 复制改写（姿势直接传字典；bare=True 为卸甲形态）
# =====================================================================================
CH_POSES2 = {k: dict(v) for k, v in SS.CH_POSES.items()}
# 横斩：0 剑举过头顶往后（ang 100），1 斜劈到前下方（ang −35）+ 一道银色劈痕
CH_POSES2['slash0'] = dict(far=((7, 2), (8, -6), (5, -11)), near=((-6, 3), (-11, 2), (-14, 6)), lean=-2,
                           legs=(((2, 19), (8, 25), (10, 33)), ((-2, 19), (-7, 26), (-12, 33))),
                           ang=105, blade=20, w=44)
CH_POSES2['slash1'] = dict(far=((7, 2), (14, 6), (19, 10)), near=((-6, 3), (-12, 0), (-16, -4)), lean=3,
                           legs=(((2, 19), (10, 24), (13, 32)), ((-2, 19), (-9, 25), (-16, 31))),
                           ang=-35, blade=20, w=56, arc=True)
# 架剑：剑竖在身前（ang 88），剑柄在胸前
CH_POSES2['parry'] = dict(far=((7, 2), (11, 8), (10, 6)), near=((-6, 3), (-11, -1), (-9, -6)),
                          legs=(((2, 19), (8, 25), (9, 33)), ((-2, 19), (-6, 26), (-11, 33))),
                          ang=86, blade=22, w=40)
CH_POSES2['hurt'] = dict(far=((7, 2), (11, -2), (15, -5)), near=((-6, 3), (-12, 4), (-16, 1)), lean=-3,
                         legs=(((2, 19), (7, 26), (9, 34)), ((-2, 19), (-7, 27), (-12, 34))),
                         ang=-60, blade=16, w=44, head_dx=-2)
# 卸甲：更细的身体、更低更快的架势
CH_POSES2['bare_idle'] = dict(far=((6, 3), (12, 6), (18, 4)), near=((-5, 3), (-10, 0), (-8, -5)), lean=1,
                              legs=(((2, 18), (9, 25), (11, 33)), ((-2, 18), (-7, 26), (-13, 33))),
                              ang=22, blade=19, w=52)
CH_POSES2['bare_thrust0'] = dict(far=((6, 3), (3, 7), (9, 6)), near=((-5, 3), (-10, -1), (-8, -6)), lean=-2,
                                 legs=(((2, 18), (8, 25), (10, 33)), ((-2, 18), (-7, 26), (-13, 33))),
                                 ang=4, blade=17, w=52)
CH_POSES2['bare_thrust1'] = dict(far=((6, 3), (15, 3), (24, 3)), near=((-5, 3), (-12, 2), (-17, -1)), lean=4,
                                 legs=(((2, 18), (11, 24), (15, 32)), ((-2, 18), (-10, 25), (-18, 30))),
                                 ang=0, blade=28, w=72, lines=True)
CH_POSES2['bare_thrust2'] = dict(far=((6, 3), (15, 3), (23, 4)), near=((-5, 3), (-12, 2), (-17, -1)), lean=4,
                                 legs=(((2, 18), (11, 24), (15, 32)), ((-2, 18), (-10, 25), (-18, 30))),
                                 ang=4, blade=26, w=72, flurry=True)


def _bare_limb(p, a, b, r0, r1):
    m = p.cap(a[0], a[1], b[0], b[1], r0, r1)
    p.paint(m, 'wzZ3', hi=0.3, sh=0.6)
    return m


def _ch_frame2(pose, ph=0, bob=0, bare=False):
    P = CH_POSES2[pose]
    W_ = P.get('w', 40)
    p = SS._Pix(W_, 56, SS._M)
    lean = P.get('lean', 0)
    cx, ty = 20 + lean, 18 + bob
    limb = _bare_limb if bare else SS._ch_limb
    k = 0.66 if bare else 1.0           # 卸甲：四肢更细

    def O(v):
        return (cx + v[0], ty + v[1])
    p.stamp(SS.CH_PLUME, cx - 11 + (ph % 2), ty - 12 + (ph % 2))
    ns, ne, nh = O(P['near'][0]), O(P['near'][1]), O(P['near'][2])
    limb(p, ns, ne, 2.3 * k, 2.0 * k)
    limb(p, ne, nh, 2.0 * k, 1.6 * k)
    p.paint(p.ell(nh[0], nh[1], 1.8 * (0.85 if bare else 1), 1.8 * (0.85 if bare else 1)), 'zZ3')
    for (hip, knee, foot) in P['legs']:
        hip, knee, foot = O(hip), O(knee), O(foot)
        limb(p, (hip[0] - lean // 2, hip[1]), knee, 2.6 * k, 2.1 * k)
        limb(p, knee, foot, 2.2 * k, 1.6 * k)
        kx, ky = knee
        if bare:
            p.paint(p.ell(kx, ky, 1.3, 1.3), 'wZ3')          # 关节小球
        else:
            p.stamp("""
            .k..
            kwk.
            kzZk
            .kk.
            """, int(kx) - 1, int(ky) - 2)
        fx, fy = foot
        if bare:
            p.paint(p.poly([(fx - 1, fy), (fx + 4, fy + 1), (fx - 1, fy + 2)]), 'zZ3')
        else:
            p.paint(p.poly([(fx - 2, fy - 1), (fx + 4, fy + 1), (fx - 2, fy + 2)]), 'zZ3')
    if bare:
        # 细腰 + 一节一节的躯干（骨架感），没有护裙、没有肩甲
        pelvis = p.poly([(cx - 3, ty + 14), (cx + 3, ty + 14), (cx + 2, ty + 19), (cx - 2, ty + 19)])
        p.paint(pelvis, 'zZ3', hi=0.3, sh=0.6)
        spine = p.poly([(cx - 2, ty + 8), (cx + 2, ty + 8), (cx + 1, ty + 15), (cx - 1, ty + 15)])
        p.paint(spine, 'zZ3', hi=0.3, sh=0.6)
        chest = p.poly([(cx - 5, ty + 1), (cx + 5, ty + 1), (cx + 4, ty + 6), (cx + 1, ty + 9),
                        (cx - 1, ty + 9), (cx - 4, ty + 6)])
        p.paint(chest, 'wzZ3', hi=0.28, sh=0.64)
        for yy in (ty + 10, ty + 12, ty + 14):
            p.line([(cx - 1, yy), (cx + 1, yy)], '3', only='wzZ')
        p.line([(cx - 4, ty + 5), (cx - 1, ty + 7)], 'Z', only='wz')
        p.line([(cx + 4, ty + 5), (cx + 1, ty + 7)], 'Z', only='wz')
        p.stamp("""
        .k.
        kUk
        .k.
        """, cx - 1, ty + 3)
    else:
        sk = p.poly([(cx - 6, ty + 13), (cx + 6, ty + 13), (cx + 7, ty + 20), (cx + 2, ty + 18),
                     (cx - 1, ty + 21), (cx - 4, ty + 18), (cx - 7, ty + 20)])
        p.paint(sk, 'wzZ3', hi=0.3, sh=0.6)
        chest = p.poly([(cx - 7, ty + 1), (cx + 7, ty + 1), (cx + 6, ty + 8), (cx + 3, ty + 14),
                        (cx - 3, ty + 14), (cx - 6, ty + 8)])
        p.paint(chest, 'wzZ3', hi=0.28, sh=0.64)
        p.line([(cx, ty + 3), (cx + 1, ty + 12)], 'Z', only='wz')
        p.line([(cx - 5, ty + 8), (cx - 1, ty + 10)], 'Z', only='wz')
        p.line([(cx + 5, ty + 8), (cx + 2, ty + 10)], 'Z', only='wz')
        p.stamp("""
        .k.
        kUk
        .k.
        """, cx - 1, ty + 4)
    p.fill(p.rect(cx - 1, ty - 3, cx + 2, ty + 1), 'B')
    p.stamp(SS.CH_HEAD, cx - 4 + P.get('head_dx', 0), ty - 15)
    if not bare:
        pd = p.poly([(cx - 9, ty + 4), (cx - 11, ty - 3), (cx - 5, ty), (cx - 3, ty + 4)])
        p.paint(pd, 'wzZ3', hi=0.35, sh=0.6)
    fs, fe, fh = O(P['far'][0]), O(P['far'][1]), O(P['far'][2])
    limb(p, fs, fe, 2.4 * k, 2.0 * k)
    limb(p, fe, fh, 2.1 * k, 1.7 * k)
    if not bare:
        p.paint(p.poly([(cx + 4, ty + 4), (cx + 5, ty - 1), (cx + 11, ty - 3), (cx + 9, ty + 4)]),
                'wzZ3', hi=0.35, sh=0.6)
    else:
        p.paint(p.ell(cx + 6, ty + 2, 1.6, 1.6), 'wZ3')        # 肩关节
    if P.get('arc'):
        # 斜劈留下的银色劈痕：以肩为圆心、从头顶扫到前下方的一道月牙（外亮内暗三层）
        sx0, sy0 = fs
        for R, a0, a1, ch in ((25, 100, -28, 'w'), (23, 88, -22, 'z'), (21, 64, -12, 'Z')):
            pts = [(sx0 + R * math.cos(math.radians(a)), sy0 - R * math.sin(math.radians(a)))
                   for a in np.linspace(a0, a1, 24)]
            p.line(pts, ch)
    if P.get('flurry'):
        for kk, (ang, L) in enumerate(((14, 30), (-10, 32), (4, 38), (24, 26), (-20, 28), (-2, 34))):
            x0, y0 = fh
            dx, dy = math.cos(math.radians(ang)), -math.sin(math.radians(ang))
            p.line([(x0 + dx * 4, y0 + dy * 4), (x0 + dx * L, y0 + dy * L)], 'z' if kk % 2 else 'w')
            p.px(round(x0 + dx * (L + 1)), round(y0 + dy * (L + 1)), 'U')
    SS._ch_blade(p, fh[0], fh[1], P['ang'], P['blade'])
    p.paint(p.ell(fh[0], fh[1], 1.9 * (0.85 if bare else 1), 1.9 * (0.85 if bare else 1)), 'zZ3')
    if P.get('lines'):
        for yy, x0, x1 in ((fh[1] - 4, fh[0] - 10, fh[0] + 2), (fh[1] + 4, fh[0] - 6, fh[0] + 6),
                           (fh[1] - 8, fh[0] - 16, fh[0] - 6)):
            p.line([(x0, yy), (x1, yy)], 'Z')
    return SS._clean_outline(p.grid())


_reg('chariot.slash', [_ch_frame2('slash0', 0, 0), _ch_frame2('slash1', 1, 0)], SS.CH_PAL,
     'diagonal slash: 0 rapier raised overhead, 1 cut down-forward with a silver arc', fps=16)
_reg('chariot.parry', [_ch_frame2('parry', 0, 0)], SS.CH_PAL,
     'stance / parry: rapier held upright before the body (logical "block"; also the guard-stance pose)')
_reg('chariot.hurt', [_ch_frame2('hurt', 1, 0)], SS.CH_PAL, 'recoil: leaning back, rapier swung down')
_reg('chariot.bare_idle', [_ch_frame2('bare_idle', 0, 0, bare=True), _ch_frame2('bare_idle', 1, 1, bare=True)],
     SS.CH_PAL, 'armour OFF: slim skeletal silver body, low fast stance, 2f bob (use with skin "bare")', fps=4)
_reg('chariot.bare_thrust', [_ch_frame2('bare_thrust0', 0, 0, bare=True), _ch_frame2('bare_thrust1', 1, 0, bare=True),
                             _ch_frame2('bare_thrust2', 0, 0, bare=True)],
     SS.CH_PAL, 'armour OFF thrust: 0 draw back, 1 lightning lunge, 2 flurry of afterimage blades', fps=12)


# =====================================================================================
#  愚者：沙爪 / 沙拳砸地（2026-10-10，抽帧审查：原来由 art_later_existing 在待机图上贴一根通用线段手臂，
#  slam 和 claw 帧 0 一模一样）。照原工程 _fool_frame 的画法和部件（羽冠、尾羽、后腿爪、沙身体、轮子前腿、狗面具、沙粒）
#  重画，多一条沙子聚成的前肢：claw = 三根爪，slam = 一只大沙拳；身体、后腿、轮子的位置同 fool.idle，切换不跳
# =====================================================================================
FO_T = 12                                     # 画布顶上加的空行（举爪 / 举拳高过羽冠）；锚点 = (24, 40 + FO_T)


def _sand_limb(p, s, e, w, r=(3.2, 2.6, 2.2)):
    m = p.cap(s[0], s[1], e[0], e[1], r[0], r[1]) | p.cap(e[0], e[1], w[0], w[1], r[1], r[2])
    p.paint(m, 'WtTh', hi=0.3, sh=0.62)
    p.line([s, e], 'T', only='Wt')            # 沙纹（同身体上的暗线）
    return m


def _talons(p, x, y, angs, L=6.0):
    for ang in angs:
        dx, dy = math.cos(math.radians(ang)), -math.sin(math.radians(ang))
        p.paint(p.cap(x, y, x + dx * L, y + dy * L, 1.5, 0.6), 'tTh', hi=0.3, sh=0.55)
        p.px(round(x + dx * (L - 0.5)), round(y + dy * (L - 0.5)), '3')


def _sand_fist(p, x, y, rx=6.5, ry=5.6):
    m = p.ell(x, y, rx, ry)
    p.paint(m, 'WtTh', hi=0.3, sh=0.62)
    for k in (-2, 1):                         # 指节
        p.line([(x + 1, y + k), (x + rx - 1.5, y + k)], 'T', only='Wt')
    return m


def _sand_splash(p, x, y, ph, big=False):
    """落点扬沙：一圈往上、往外飞的沙块 + 贴地的沙尘。"""
    n = 9 if big else 6
    for i in range(n):
        ang = 22 + 136 * i / (n - 1)
        L = (11 if big else 7) + (i * 37 + ph * 11) % 5
        cx_, cy_ = x + math.cos(math.radians(ang)) * L, y - math.sin(math.radians(ang)) * L * 0.85
        r = (1.9 if big else 1.4) - (0.5 if i % 2 else 0)
        p.paint(p.ell(cx_, cy_, r + 0.3, r), 'WtT', hi=0.35, sh=0.6)
    p.paint(p.ell(x, y - 1, 9 if big else 6, 2.4), 'Wtt', outline='T', hi=0.3, sh=0.7)


def _fool_pose(hd=(0, 0), wheel=(31, 31), ph=0, limb=None, talons=None, fist=None, splash=None, limb_front=True):
    """_fool_frame 的副本（同部件、同坐标），T = FO_T 行；hd = 头和前半身的位移（后腿、尾巴不动）；
    limb = (肩, 肘, 腕) 沙前肢；talons = 爪的角度；fist = 大沙拳中心；splash = (x, y, big) 扬沙。"""
    T = FO_T
    p = SS._Pix(64, 40 + T, SS._M)
    hx, hy = hd
    for k, (ang, L) in enumerate(((158, 17), (140, 19), (122, 17), (104, 13))):
        SS._feather(p, 30 + hx, 14 + hy + T, ang + (ph % 2) * 3 * (1 if k % 2 else -1), L, 2.5)
    for ang, L in ((172, 10), (192, 9)):
        SS._feather(p, 15, 23 + T, ang, L, 1.9)
    lm = p.cap(18, 26 + T, 16, 33 + T, 3.4, 2.4) | p.cap(16, 33 + T, 18, 37 + T, 2.4, 1.8)
    p.paint(lm, 'WtTh')
    p.stamp("""
    kTkTk
    .k.k.
    """, 15, 38 + T)
    body = p.ell(23 + hx * 0.3, 24 + T + hy * 0.3, 8.5, 6) | p.ell(30 + hx * 0.6, 20 + T + hy * 0.6, 6, 6.5)
    p.paint(body, 'WtTh', hi=0.25, sh=0.64)
    p.line([(17, 22 + T), (22 + hx * 0.3, 20 + T + hy * 0.3), (27 + hx * 0.5, 21 + T + hy * 0.5)], 'T', only='Wt')
    p.line([(18, 26 + T), (24, 25 + T)], 'T', only='Wt')
    if wheel:
        SS._wheel(p, wheel[0], wheel[1] + T, 6.5, ph)

    def arm():
        if not limb:
            return
        s, e, w = [(x, y + T) for x, y in limb]
        _sand_limb(p, s, e, w)
        if talons:
            p.paint(p.ell(w[0], w[1], 2.8, 2.6), 'WtT', hi=0.35, sh=0.62)
            _talons(p, w[0], w[1], talons)
        if fist:
            _sand_fist(p, fist[0], fist[1] + T)
    if not limb_front:
        arm()
    p.stamp(SS.FO_MASK, 29 + hx, 4 + hy + T)
    p.line([(30 + hx, 10 + hy + T), (33 + hx, 8 + hy + T)], 'b')
    if splash:                                # 扬沙画在前肢后面：爪 / 拳砸进沙里还看得见
        _sand_splash(p, splash[0], splash[1] + T, ph, big=splash[2])
    if limb_front:
        arm()
    SS._sand_bits(p, ph, (1, 4 + T, 62, 36 + T), 10, seed=ph)
    return SS._clean_outline(p.grid())


FO_ANC = (24, 40 + FO_T)
# claw：0 举爪（头微抬、沙前肢从胸口举到面具右前上方、三根爪张开朝上）→ 1 落爪（头前探、爪子砸进身前地面 = 替身身前约 25 px、扬沙）
_reg('fool.claw', [_fool_pose(hd=(-1, -2), ph=0, limb=((34, 21), (45, 15), (51, 7)), talons=(25, 55, 85), limb_front=False),
                   _fool_pose(hd=(2, 1), ph=1, limb=((34, 22), (44, 25), (49, 34)), talons=(-30, -60, -90),
                              splash=(51, 40, False))],
     SS.FO_PAL, 'sand claw: 0 sand foreleg raised over the mask, three talons open; '
     '1 talons slammed into the ground ~25 px ahead, sand spray (body / wheel / hind leg as idle)', fps=8, anchor=FO_ANC)
# slam：0 人立蓄力（前半身抬高、轮子腿离地、一只大沙拳举过羽冠）→ 1 砸地（前半身压下、大沙拳砸进身前地面 = 替身身前约 29 px、大片扬沙）
_reg('fool.slam', [_fool_pose(hd=(0, -6), wheel=(34, 26), ph=0, limb=((34, 19), (40, 6), (43, -3)), fist=(44, -6), limb_front=False),
                   _fool_pose(hd=(3, 3), wheel=(33, 31), ph=1, limb=((35, 23), (46, 23), (51, 32)), fist=(53, 34),
                              splash=(53, 40, True))],
     SS.FO_PAL, 'sand slam: 0 rearing up, wheel leg lifted, a huge sand fist raised above the headdress; '
     '1 the fist smashed into the ground ~29 px ahead, big sand burst', fps=8, anchor=FO_ANC)


# =====================================================================================
#  灰塔：fly 帧 0 + 往前伸出的长针（26×12，锚点 = 原来的身体中心 (8, 6)）
# =====================================================================================
def _tower_needle():
    """SE._tower(0) 的同一套画法（翅膀上扬帧），只是画布加宽到 26、针舌伸到 x 24。"""
    P = SE._Pix(26, 12)
    wing = SE._Pix(26, 12)
    wing.poly([(3, 4), (0, 0), (3, 0), (6, 4)], 'u')
    wing.poly([(5, 4), (6, 0), (9, 0), (8, 4)], 'u')
    wing.shade('u', 'U', d=(1, 1))
    body = SE._Pix(26, 12)
    body.ell(1, 5, 8, 9, 'Z')
    body.ell(7, 4, 11, 8, 'z')
    body.shade('Z', 'X', d=(1, 1))
    body.shade('z', 'Z', d=(1, 1))
    body.dot([(3, 6), (4, 6)], 'z')
    body.dot([(9, 5)], 'r')
    body.dot([(11, 4), (12, 3), (13, 2), (14, 2), (15, 3)], 'z')      # 钳子
    body.dot([(11, 8), (12, 9), (13, 10), (14, 10), (15, 9)], 'z')
    body.dot([(x, 6) for x in range(12, 16)], 'm')                   # 针根（粉）
    body.dot([(x, 6) for x in range(16, 24)], 'z')                   # 针身（钢）
    body.dot([(24, 6)], 'w')                                          # 针尖亮点
    P.paste(body)
    P.paste(wing, ring='k')
    P.outline('k')
    P.dot([(3, 11), (5, 11), (7, 11)], 'X')
    return P.grid()


_PAL_T = dict(SE.PAL_TOWER, w='#ffffff')
sprite.define('towergray.needle', [_tower_needle()], pal=_PAL_T, anchor=(8, 6),
              desc='Tower of Gray strike: needle tongue shot out 10px (26x12, anchor = body centre like fly)')
NEW.append('towergray.needle')


# =====================================================================================
if __name__ == '__main__':
    out = AC.PREVIEW
    AC.preview_names(['starplat.upper', 'starplat.hurt', 'starplat.reach'], os.path.join(out, 'dev_starplat.png'),
                     'starplat', compare=['starplat.idle', 'starplat.punch'])
    AC.preview_names(['magred.punch', 'magred.block', 'magred.hurt'], os.path.join(out, 'dev_magred.png'),
                     'magred', compare=['magred.idle', 'magred.cast'])
    AC.preview_names(['hiero.whip', 'hiero.hurt', 'hiero.block'], os.path.join(out, 'dev_hiero.png'),
                     'hiero', compare=['hiero.idle', 'hiero.cast'])
    AC.preview_names(['chariot.slash', 'chariot.parry', 'chariot.hurt', 'chariot.bare_idle', 'chariot.bare_thrust'],
                     os.path.join(out, 'dev_chariot.png'), 'chariot', compare=['chariot.idle', 'chariot.thrust'])
    AC.preview_names(['towergray.needle'], os.path.join(out, 'dev_towergray.png'), 'towergray',
                     compare=['towergray.fly'], scale=8)
    print('new:', NEW)
