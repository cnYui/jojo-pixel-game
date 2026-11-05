# 第3章的新角色图集（第四部/docs/分章开发约定.md：新角色写在自己的文件里，复用 p4_chars 的 Sheet / save / recolor）：
#   yukako     山岸由花子（底子：第三部的水手服女生 npc_student_f_a；加腰长的黑卷发，配色照 TV 动画：青绿上衣、长春花蓝裙、淡紫领结、紫眼、深蓝鞋），
#              头发随 HP 变灰、变白：同一张图集里多两套 grey_ / white_ 前缀的动作（引擎按 actor.skin 找 skin_动作）
#   echoes2    回音 ACT2（自己画：橄榄绿装甲、黄眼、白护膝白靴、长尾巴上亮下深灰）
#   tonio      东尼欧·特拉萨迪（底子：第三部的厨师 npc_hk_owner；棕发、白色厨师服、红领带、黄徽章、高帽）
#   pearljam   珍珠果酱（一群蔬菜一样的小家伙）
#   亿泰、回音 ACT1 用第2章画的（okuyasu / echoes1）
#   用法：python3 第四部/tools/art/p4_chars_ch3.py [cid ...]   → 元数据写 assets/_meta/chars_ch3.json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402

O = C.O


def rgb(c):
    return C.rgb(c)


def arr(img):
    return np.array(img.convert('RGBA'))


def img(a):
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


# ============================================================ 山岸由花子
# 头发：黑里带一点紫（动画里的黑发高光偏紫）；灰、白两套给“被炸以后一档档变白”
HAIR = {
    'black': dict(d=(20, 14, 30), m=(38, 28, 56), l=(70, 56, 104), x=(118, 98, 160)),
    'grey': dict(d=(84, 80, 96), m=(120, 116, 132), l=(160, 156, 172), x=(200, 198, 212)),
    'white': dict(d=(176, 176, 190), m=(212, 212, 222), l=(236, 236, 244), x=(255, 255, 255)),
}
SRC_HAIR = ['#1e1a22', '#0e0c12', '#3e3846']          # 底子里的短发（中、暗、亮）
# 制服：底子的藏青一件式 → 上衣青绿、裙子长春花蓝；红领巾 → 淡紫领结；棕鞋 → 深蓝
TOP = {'#2c3462': '#2a8a86', '#181d3e': '#16585a'}
SKIRT = {'#2c3462': '#7c84d6', '#181d3e': '#4a52a0'}
BOW = {'#e0303c': '#c8a6ee', '#9a2a44': '#8a68c0'}
SHOE = {'#6a4228': '#2a3266', '#5a361e': '#1a2048', '#3a2a22': '#141838'}
EYE_PURPLE = (120, 70, 170)


def _bbox(mask):
    ys, xs = np.where(mask)
    if not len(xs):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def yk_recolor(f, waist):
    """制服换色：waist 行以下的藏青算裙子"""
    a = arr(f)
    h = a.shape[0]
    f = img(a)
    f = C.recolor(f, TOP, (0, 0, f.width, waist))
    f = C.recolor(f, SKIRT, (0, waist, f.width, h))
    f = C.recolor(f, BOW)
    f = C.recolor(f, SHOE)
    return f


def paint_hair(f, style='down', pal='black', lying=False):
    """在人后面画腰长的波浪黑发（只画在透明处，再描边）。人朝右：后背在左边。
    style='up'：头发竖起来往后上方飘（甩头发、发怒）"""
    a = arr(f)
    h, w = a.shape[:2]
    P = HAIR[pal]
    src = C.comp(f, SRC_HAIR)
    bb = _bbox(src)
    if not bb:
        return f
    hx0, hy0, hx1, hy1 = bb
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    opaque = a[..., 3] > 0
    body = _bbox(opaque)
    if lying:
        # 躺着（头在左）：头发铺在地上往左散开
        cy = (hy0 + hy1) / 2
        m = (xx <= hx0 + 2) & (xx >= max(0, hx0 - 10)) & (np.abs(yy - cy - 1) <= 3 + np.sin(xx * 0.9))
        m |= (xx <= hx1) & (yy >= hy1 - 1) & (yy <= hy1 + 1) & (xx >= hx0)
    elif style == 'up':
        # 竖起来：从后脑往左上方炸开几束
        m = np.zeros((h, w), bool)
        ox, oy = hx0 + 3, hy0 + 4
        for k, ang in enumerate(np.deg2rad([150, 165, 182, 200, 125, 110])):
            L_ = 13 + (k % 3) * 3
            for t in np.linspace(0, 1, 40):
                px = ox + np.cos(ang) * L_ * t + np.sin(t * 9 + k) * 1.2
                py = oy - np.sin(ang) * L_ * t * 1.1 + 2
                r = 2.2 * (1 - t) + 0.6
                m |= (xx - px) ** 2 + (yy - py) ** 2 <= r * r
        m |= (xx >= hx0 - 3) & (xx <= hx0 + (hx1 - hx0) * 0.45) & (yy >= hy0 + 2) & (yy <= hy1 + 6)
    else:
        bottom = hy1 + int((body[3] - hy1) * 0.62) if body else hy1 + 14
        wave = 1.6 * np.sin(yy * 0.7)
        left = hx0 - 2 - (yy - hy1).clip(0) * 0.12 + wave
        right = hx0 + (hx1 - hx0) * 0.42 + 0.6 * np.sin(yy * 0.7 + 1.5)
        m = (yy >= hy0 + 2) & (yy <= bottom) & (xx >= left) & (xx <= right)
        # 发梢一卷一卷的
        tip = (yy > bottom) & (yy <= bottom + 2) & (((xx - hx0) % 3) < 1.6) & (xx >= hx0 - 3) & (xx <= right)
        m |= tip
        # 前面一缕垂到胸口（脸前面那一侧）
        fr = (xx >= hx1 - 2) & (xx <= hx1) & (yy >= hy1 - 1) & (yy <= hy1 + 5)
        m |= fr
    put = m & ~opaque
    # 明暗：外缘暗，中间一条亮（往下流的高光）
    shade = np.full((h, w), 1)
    shade[(xx + yy * 0.3) % 5 < 1] = 2
    shade[(yy % 7 == 0)] = 0
    pal_ = {0: P['d'], 1: P['m'], 2: P['l']}
    for k, c in pal_.items():
        sel = put & (shade == k)
        a[sel] = (*c, 255)
    out = C.reoutline(img(a))
    # 原来的短发也换成这一套的颜色
    out = C.recolor(out, {SRC_HAIR[0]: P['m'], SRC_HAIR[1]: P['d'], SRC_HAIR[2]: P['l']})
    return out


def yk_eyes(f):
    """动画里由花子是紫眼：脸上最深的眼珠像素换成紫"""
    fb = C.face_box(f, 24, [(246, 196, 154), (216, 148, 108)])
    if not fb:
        return f
    fx0, fy0, fx1, fy1 = fb
    return C.recolor(f, {'#1a1020': EYE_PURPLE}, (fx0 + 1, fy0 + 1, fx1, fy1 - 2))


def yk_frame(f, pal='black', style='down', lying=False):
    waist = 30
    f = yk_recolor(f, waist if not lying else 0)
    if not lying:
        f = yk_eyes(f)
    return paint_hair(f, style, pal, lying)


def yk_portrait(f, pal='black', rage=False):
    """头像 32×32：两侧加垂到底的长发，制服换色"""
    f = C.recolor(f, TOP)
    f = C.recolor(f, BOW)
    a = arr(f)
    P = HAIR[pal]
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    # 左边一大片（后背的头发），右边窄一条
    left = (xx <= 6 + (np.sin(yy * 0.8) * 1.2).astype(int)) & (yy >= 8)
    right = (xx >= 27 - (np.sin(yy * 0.8 + 1) * 1.0).astype(int)) & (yy >= 10) & (yy <= 26)
    m = left | right
    sel = m & ~((a[..., 3] > 0) & ~C.comp(f, SRC_HAIR + ['#1a1020']))
    a[sel] = (*P['m'], 255)
    a[sel & (yy % 4 == 0)] = (*P['d'], 255)
    a[sel & ((xx + yy) % 6 == 0)] = (*P['l'], 255)
    f = C.recolor(img(a), {SRC_HAIR[0]: P['m'], SRC_HAIR[1]: P['d'], SRC_HAIR[2]: P['l']})
    if rage:
        # 发怒：眼睛上面压一道阴影（只压皮肤），头发竖起几根
        a = arr(f)
        sk = C.comp(f, ['#f6c49a', '#d8946c', '#f08888'])
        band = sk & (yy >= 9) & (yy <= 11)
        a[band] = (168, 110, 96, 255)
        for x in (3, 6, 26, 29):
            for y in range(1, 6):
                if a[y, x][3] == 0 and (x + y) % 2 == 0:
                    a[y, x] = (*P['d'], 255)
        f = img(a)
    return f


def yk_smile(f):
    a = arr(f)
    # 闭眼笑：眼睛那两行里深色像素往上抬成弧（简单做法：眼睛最下一行换成皮肤）
    ys, xs = np.where((a[..., 0] < 50) & (a[..., 1] < 50) & (a[..., 3] > 0) & (np.mgrid[0:32, 0:32][0] >= 12) & (np.mgrid[0:32, 0:32][0] <= 15)
                      & (np.mgrid[0:32, 0:32][1] >= 10) & (np.mgrid[0:32, 0:32][1] <= 24))
    if len(ys):
        yb = ys.max()
        for x, y in zip(xs, ys):
            if y == yb:
                a[y, x] = (246, 196, 154, 255)
    return img(a)


def yk_shock(f, i):
    a = arr(f)
    # 嘴张圆
    for (x, y) in ((16, 20), (17, 20), (16, 21), (17, 21)):
        a[y, x] = (90, 20, 40, 255)
    if i:
        a[22, 16] = a[22, 17] = (90, 20, 40, 255)
    return img(a)


def build_yukako():
    src = 'npc_student_f_a'
    im, m = C.base(src)
    sh = C.Sheet('yukako', '山岸由花子', m['cell'], m['pivot'])
    idle = C.frames(src, 'idle')
    walk = C.frames(src, 'walk')
    cheer = C.frames(src, 'cheer')
    down = C.frames(src, 'down')
    for pal in ('black', 'grey', 'white'):
        pre = '' if pal == 'black' else pal + '_'
        sh.add(pre + 'idle', [yk_frame(f, pal) for f in idle], 2, 'loop')
        sh.add(pre + 'walk', [yk_frame(f, pal) for f in walk], 8, 'loop')
        sh.add(pre + 'run', [yk_frame(f, pal) for f in walk], 13, 'loop')
        sh.add(pre + 'cmd', [yk_frame(f, pal, 'up') for f in idle], 6, 'loop')
        # 挨打：往后仰一点
        sh.add(pre + 'hurt', [yk_frame(f, pal).rotate(10, resample=Image.NEAREST, center=(24, 46)) for f in idle[:1]], 1, 'static')
        sh.add(pre + 'down', [yk_frame(f, pal, lying=True) for f in down], 1, 'static')
        sh.add(pre + 'blush', [yk_frame(f, pal) for f in cheer], 4, 'loop')
    hd = C.heads(src)
    pf = hd['portrait']
    nm = [yk_portrait(f) for f in pf]
    rg = [yk_portrait(f, rage=True) for f in pf]
    wn = [yk_portrait(f, 'white') for f in pf]
    sh.heads = {'normal': nm, 'smile': [yk_smile(f) for f in nm], 'shock': [yk_shock(f, i) for i, f in enumerate(nm)], 'rage': rg,
                'wnormal': wn, 'wshock': [yk_shock(f, i) for i, f in enumerate(wn)]}
    amap = {'talk': 'idle', 'shock': 'hurt', 'special': 'cmd', 'win': 'cmd', 'pose': 'cmd', 'guard': 'cmd', 'dodge': 'run', 'getup': 'hurt'}
    e = C.save(sh, amap=amap, bodyW=4)
    return e


# ============================================================ 回音 ACT2（自己画）
EC2 = dict(o=(22, 30, 14), d=(70, 84, 30), m=(112, 128, 52), l=(156, 170, 84), x=(196, 208, 124), sf=(240, 170, 40), sf2=(196, 120, 20),
           wh=(244, 244, 236), gr=(70, 70, 78), ey=(255, 230, 60))


def echoes2_frame(t=0.0, pose='idle', w=46, h=46):
    """朝右。身子：圆头 + 高领 + 胸甲；尾巴从屁股往后绕一圈，尖上是苦无形的尾尖"""
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    bob = np.sin(t * 2 * np.pi) * 1.0
    cx, cy = 26, 17 + bob
    lean = {'punch': 3, 'cast': -1, 'hurt': -3, 'block': 0}.get(pose, 0)
    cx += lean
    m = {}

    def ell(x0, y0, rx, ry):
        return ((xx - x0) / rx) ** 2 + ((yy - y0) / ry) ** 2 <= 1
    head = ell(cx, cy, 6.0, 5.5)
    collar = ell(cx - 1, cy + 3, 8.0, 3.2) & (yy >= cy + 1)
    torso = ell(cx - 1, cy + 10, 5.2, 6.0)
    arm_f = ell(cx + 5 + (4 if pose == 'punch' else 0), cy + 9 - (2 if pose == 'cast' else 0), 2.2, 3.6)
    arm_b = ell(cx - 6, cy + 9, 2.0, 3.4)
    leg1 = ell(cx + 2, cy + 18, 2.2, 4.0)
    leg2 = ell(cx - 3, cy + 18, 2.2, 4.0)
    boots = (ell(cx + 2, cy + 21.5, 2.6, 1.6) | ell(cx - 3, cy + 21.5, 2.6, 1.6))
    knees = (ell(cx + 2, cy + 17, 1.6, 1.2) | ell(cx - 3, cy + 17, 1.6, 1.2))
    # 尾巴：从腰后往左绕到头顶上方（Bezier），越往尖越细
    tail = np.zeros((h, w), bool)
    tail_top = np.zeros((h, w), bool)
    sway = np.sin(t * 2 * np.pi + 0.6) * 2
    if pose == 'punch':
        pts = [(cx - 4, cy + 12), (cx - 16, cy + 2), (cx + 18, cy - 8 + sway)]
    else:
        pts = [(cx - 4, cy + 12), (cx - 22, cy + 10), (cx - 16, cy - 10 + sway)]
    tipx = tipy = 0
    for u in np.linspace(0, 1, 60):
        v = 1 - u
        px = v * v * pts[0][0] + 2 * v * u * pts[1][0] + u * u * pts[2][0]
        py = v * v * pts[0][1] + 2 * v * u * pts[1][1] + u * u * pts[2][1]
        r = 2.3 * (1 - u) + 0.8
        tail |= (xx - px) ** 2 + (yy - py) ** 2 <= r * r
        tail_top |= (xx - px) ** 2 + (yy - py + r * 0.5) ** 2 <= (r * 0.6) ** 2
        tipx, tipy = px, py
    tip = ell(tipx, tipy, 2.6, 2.6) | ((np.abs(xx - tipx) + np.abs(yy - tipy - 1)) <= 3.2)
    body = head | collar | torso | arm_f | arm_b | leg1 | leg2 | boots
    a[tail] = (*EC2['gr'], 255)
    a[tail_top & tail] = (*EC2['l'], 255)
    a[tip] = (*EC2['sf'], 255)
    a[body] = (*EC2['m'], 255)
    a[body & (xx < cx - 2)] = (*EC2['d'], 255)
    a[(head | collar) & (yy < cy - 2) & (xx > cx - 3)] = (*EC2['l'], 255)
    a[collar] = (*EC2['d'], 255)
    a[collar & (yy < cy + 2)] = (*EC2['l'], 255)
    a[(arm_f | arm_b) & (yy > cy + 10)] = (*EC2['sf'], 255)          # 前臂内侧：藏红花色
    a[boots | knees] = (*EC2['wh'], 255)
    # 胸甲上的条纹
    for k in range(3):
        a[int(cy + 8 + k * 2), int(cx - 3):int(cx + 2)] = (*EC2['x'], 255)
    # 眼睛：一道黄色的横条（有条纹的金属眼）+ 小嘴
    ey = int(round(cy - 0.5))
    a[ey, int(cx):int(cx + 5)] = (*EC2['ey'], 255)
    a[ey, int(cx + 2)] = (*EC2['o'], 255)
    a[ey + 3, int(cx + 3):int(cx + 5)] = (*EC2['gr'], 255)
    if pose == 'hurt':
        a[ey, int(cx):int(cx + 5)] = (*EC2['o'], 255)
    out = C.reoutline(img(a), EC2['o'])
    return out


def build_echoes2():
    sh = C.Sheet('echoes2', '回音 ACT2', (46, 46), (24, 44))
    sh.add('idle', [echoes2_frame(t / 4) for t in range(4)], 6, 'loop')
    sh.add('punch', [echoes2_frame(0.1, 'punch'), echoes2_frame(0.3, 'punch')], 12, 'oneshot')
    sh.add('cast', [echoes2_frame(t / 2, 'cast') for t in range(2)], 6, 'loop')
    sh.add('block', [echoes2_frame(0, 'block')], 1, 'static')
    sh.add('hurt', [echoes2_frame(0, 'hurt')], 1, 'static')
    big = echoes2_frame(0.1).resize((92, 92), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((36, 10, 68, 42)))
    sh.heads = {'normal': [face, face]}
    e = C.save(sh, amap={'talk': 'idle', 'walk': 'idle', 'rush': 'punch', 'punch2': 'punch', 'punch_heavy': 'punch', 'special': 'cast',
                         'reach': 'cast', 'pose': 'cast', 'down': 'hurt', 'shock': 'hurt', 'guard': 'block', 'dodge': 'idle', 'cmd': 'cast'},
               kind='stand', bodyW=4)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 东尼欧·特拉萨迪（底子 npc_hk_owner：厨师）
TONIO = {'#242024': '#7a4a2a', '#221e28': '#5a341e', '#121014': '#3a2012', '#44404a': '#9a6a40',     # 头发 → 棕
         '#8a8a94': '#ececf2', '#b8b8c8': '#fafafe', '#5e5e6c': '#c4c4d0'}                         # 灰围裙 → 白
SK_T = [(246, 196, 154), (216, 148, 108)]


def tonio_frame(f, plate=False, rage=False):
    f = C.recolor(f, TONIO)
    fb = C.face_box(f, 24, SK_T)
    a = arr(f)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        # 高帽：头顶上方一截白圆筒 + 蓬起来的顶
        bb = _bbox(a[..., 3] > 0)
        top = bb[1]
        hx0, hx1 = fx0 - 2, fx1 + 1
        for y in range(max(0, top - 9), top + 2):
            for x in range(hx0, hx1 + 1):
                if 0 <= x < a.shape[1]:
                    a[y, x] = (248, 248, 252, 255)
        for x in range(hx0 - 1, hx1 + 2):
            y = max(0, top - 10)
            a[y, x] = (236, 236, 244, 255)
        for x in range(hx0, hx1 + 1):
            a[top + 1, x] = (200, 200, 214, 255)            # 帽檐的阴影
        # 帽子上的半圆徽章
        a[max(0, top - 5), (hx0 + hx1) // 2] = (240, 200, 60, 255)
        # 红领带（下巴下面正中 3 格）+ 两颗黄色 T 徽章
        tx = (fx0 + fx1) // 2
        for y in range(fy1 + 2, fy1 + 6):
            a[y, tx] = (200, 30, 40, 255)
        a[fy1 + 2, tx - 1] = a[fy1 + 2, tx + 1] = (200, 30, 40, 255)
        a[fy1 + 8, tx - 3] = (240, 200, 60, 255)
        a[fy1 + 8, tx + 3] = (240, 200, 60, 255)
        if rage:
            sk = C.comp(img(a), SK_T, (fx0, fy0, fx1 + 1, fy1 + 1))
            a[sk] = (236, 120, 100, 255)
        if plate:
            # 端着盘子：身前手的高度放一只白盘子（盘上一点红）
            py = fy1 + 10
            for x in range(fx1 + 1, fx1 + 9):
                a[py, x] = (250, 250, 250, 255)
                a[py + 1, x] = (200, 200, 210, 255)
            a[py - 1, fx1 + 4] = a[py - 1, fx1 + 5] = (220, 60, 40, 255)
    out = C.reoutline(img(a))
    return out


def tonio_portrait(f, rage=False):
    f = C.recolor(f, TONIO)
    a = arr(f)
    for y in range(0, 5):
        for x in range(7, 25):
            a[y, x] = (248, 248, 252, 255)
    for x in range(7, 25):
        a[5, x] = (200, 200, 214, 255)
    a[2, 16] = (240, 200, 60, 255)
    for y in range(26, 32):
        a[y, 16] = (200, 30, 40, 255)
    if rage:
        sk = C.comp(img(a), SK_T)
        yy = np.mgrid[0:32, 0:32][0]
        a[sk & (yy >= 9) & (yy <= 12)] = (220, 110, 90, 255)
    return C.reoutline(img(a))


def build_tonio():
    src = 'npc_hk_owner'
    im, m = C.base(src)
    sh = C.Sheet('tonio', '东尼欧·特拉萨迪', (m['cell'][0], m['cell'][1] + 10), (m['pivot'][0], m['pivot'][1] + 10))

    def pad(f):
        c = Image.new('RGBA', (f.width, f.height + 10), (0, 0, 0, 0))
        c.alpha_composite(f, (0, 10))
        return c
    idle = [pad(f) for f in C.frames(src, 'idle')]
    walk = [pad(f) for f in C.frames(src, 'walk')]
    sh.add('idle', [tonio_frame(f) for f in idle], 2, 'loop')
    sh.add('walk', [tonio_frame(f) for f in walk], 8, 'loop')
    sh.add('cmd', [tonio_frame(f, plate=True) for f in idle], 2, 'loop')
    hop = []
    for f in idle[:1]:
        c = Image.new('RGBA', f.size, (0, 0, 0, 0))
        c.alpha_composite(f.crop((0, 2, f.width, f.height)), (0, 0))
        hop.append(tonio_frame(c))
    sh.add('shock', hop, 1, 'static')
    sh.add('rage', [tonio_frame(f, rage=True) for f in idle], 6, 'loop')
    hd = C.heads(src)
    pf = hd.get('portrait')
    nm = [tonio_portrait(f) for f in pf]
    if len(nm) == 1:
        nm = nm * 2
    sh.heads = {'normal': nm, 'smile': nm, 'shock': [yk_shock(f, i) for i, f in enumerate(nm)], 'rage': [tonio_portrait(f, True) for f in pf] * (2 // len(pf))}
    e = C.save(sh, amap={'talk': 'idle', 'run': 'walk', 'hurt': 'shock', 'down': 'shock', 'special': 'cmd', 'pose': 'cmd', 'win': 'cmd',
                         'guard': 'idle', 'dodge': 'walk'}, bodyW=4)
    return e


# ============================================================ 珍珠果酱：蔬菜一样的小家伙（三只一组，一蹦一蹦）
def pj_frame(t):
    w, h = 30, 16
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cols = [((236, 80, 60), (170, 40, 40)), ((120, 200, 80), (60, 140, 50)), ((250, 200, 70), (200, 140, 40))]
    for i, (c1, c2) in enumerate(cols):
        cx = 5 + i * 10
        jump = abs(np.sin((t + i / 3) * np.pi)) * 3
        cy = 10 - jump
        b = ((xx - cx) / 3.6) ** 2 + ((yy - cy) / 3.2) ** 2 <= 1
        a[b] = (*c1, 255)
        a[b & (yy > cy + 1)] = (*c2, 255)
        # 叶子帽 + 两只小眼睛
        a[int(cy - 4):int(cy - 2), int(cx) - 1:int(cx) + 1] = (70, 160, 60, 255)
        a[int(cy), int(cx) - 1] = a[int(cy), int(cx) + 1] = (26, 16, 32, 255)
    return C.reoutline(img(a))


def build_pearljam():
    sh = C.Sheet('pearljam', '珍珠果酱', (30, 16), (15, 15))
    sh.add('idle', [pj_frame(t / 4) for t in range(4)], 6, 'loop')
    big = pj_frame(0).resize((60, 32), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((14, 0, 46, 32)))
    sh.heads = {'normal': [face, face]}
    e = C.save(sh, amap={'talk': 'idle', 'walk': 'idle', 'punch': 'idle', 'cast': 'idle', 'hurt': 'idle', 'block': 'idle', 'reach': 'idle',
                         'pose': 'idle', 'cmd': 'idle'}, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 康一的战斗附加帧（从游戏尺寸的 chars/koichi.png 派生）
BUILDERS = {'yukako': build_yukako, 'echoes2': build_echoes2, 'tonio': build_tonio, 'pearljam': build_pearljam}

# 说话人 / 替身表（第3章新加的人）
HEROES = {}
SPEAKERS = {
    'yukako': dict(short='由花子', nameColor='#8a5ac0', blipHz=700),
    'tonio': dict(short='东尼欧', nameColor='#c05a3a', blipHz=520),
    'echoes2': dict(short='回音', nameColor='#8a9a3a', blipHz=880),
    'operator': dict(short='电话里的声音', nameColor='#6a7a8a', blipHz=600),
}
STANDS = {
    'echoes2': dict(cn='回音 ACT2', en='ECHOES ACT2', owner='koichi', aura='#b0c060', card='#d0e080', ghost='#e0f0a0',
                    impact='green', kind='humanoid', idle={'dx': -10, 'z': 10}, link=None, summonSfx='stand_summon_star', fist=False),
    'pearljam': dict(cn='珍珠果酱', en='PEARL JAM', owner='tonio', aura='#f0a060', card='#ffc890', ghost='#ffe0c0',
                     impact='orange', kind='humanoid', idle={'dx': 10, 'z': 0}, link=None, summonSfx=None, fist=False),
}


def main(ids):
    path = os.path.join(L.META, 'chars_ch3.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    for old in ('okuyasu_tmp', 'echoes1_tmp', 'koichi_x'):   # 康一的战斗帧第2章已补进本体（chars/koichi_ex）
        meta['chars'].pop(old, None)
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', len(meta['chars'][cid]['animations']), '表情', list(meta['chars'][cid]['heads']))
    meta['heroes'] = dict(HEROES)
    meta['speakers'] = dict(SPEAKERS)
    meta['stands'] = dict(STANDS)
    L.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
