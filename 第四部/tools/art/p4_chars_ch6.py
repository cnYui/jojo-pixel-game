# 第6章的新角色：矢安宫重清 / 丰收、吉良吉影（西装）/ 杀手皇后、杉本铃美、阿诺德（第四部/docs/第6章_开发脚本.md §4）。
#   做法和 p4_chars.py 一样：拿第三部的全尺寸图集换色、改发型，再用第三部的 shrink.py 缩成游戏尺寸。配色照 TV 动画第四部（JoJo Wiki 配色表）。
#   另有几张临时图（tmp6_*）：乔瑟夫由第4章画（露伴第5章、亿泰第2章已经画好，合进来了），那边合进来之前本章先用这几张顶着，合进来以后删掉。
#   用法：python3 第四部/tools/art/p4_chars_ch6.py [cid ...]      输出 assets/chars/<cid>.png、assets/heads/<cid>/…、assets/_meta/chars_ch6.json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402
import p4_heads as HD  # noqa: E402

O = C.O


def widen(f, k, cx):
    """横向拉宽（重清矮胖）：以脚点 cx 为中心最近邻放大 k 倍，裁回原格子大小"""
    w, h = f.size
    nw = int(round(w * k))
    g = f.resize((nw, h), Image.NEAREST)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.alpha_composite(g.crop((int(round(cx * k - cx)), 0, int(round(cx * k - cx)) + w, h)))
    return out


def scale(f, k, cell, pivot):
    """整体放大（阿诺德比伊奇大一圈）：脚点不动"""
    w, h = f.size
    g = f.resize((int(round(w * k)), int(round(h * k))), Image.NEAREST)
    out = Image.new('RGBA', tuple(cell), (0, 0, 0, 0))
    out.alpha_composite(g, (int(round(pivot[0] - pivot[0] * k)) + (cell[0] - w) // 2, int(round(pivot[1] - pivot[1] * k)) + (cell[1] - h)))
    return out


def three_heads(nm):
    if len(nm) == 1:
        nm = nm * 2
    return {'normal': nm, 'smile': [HD.smile(f) for f in nm], 'shock': [HD.shock(f, i) for i, f in enumerate(nm)], 'rage': nm}


# ============================================================ 矢安宫重清：小孩的身子拉宽、光头、绿校服黄滚边
SHIGE = {'#e49436': '#3e9a52', '#a46a26': '#226a36', '#ffbd4c': '#62c072',          # 上衣：绿
         '#525e68': '#2c7a40', '#3b434a': '#1c5a2e', '#394148': '#1c5a2e',          # 裤子：同一套绿校服
         '#702830': '#3a5ad0', '#725c44': '#2a3e9a'}                                 # 鞋：蓝
SKIN_K = [(230, 174, 126), (164, 104, 82)]


def shigechi_fix(f, big=True):
    fb = C.face_box(f, 24, SKIN_K)
    a = np.array(f.convert('RGBA'))
    if fb:
        fx0, fy0, fx1, fy1 = fb
        # 头发（深棕）全换成头皮：光头；头顶隔一个像素点一颗深一点的点，像剃短的刺
        # 小孩的头发是近黑的 #14121e（和描边同色）：头部里面“四周都不透明”的那些才是头发，换掉；外圈留着当描边
        dk = C.comp(f, ['#14121e', '#2c1e18'], (0, 0, f.width, fy1 - 2))
        op = a[..., 3] > 0
        inner = op.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            inner &= np.roll(np.roll(op, dy, 0), dx, 1)
        hair = dk & inner
        ys, xs = np.nonzero(hair)
        for y, x in zip(ys, xs):
            a[y, x] = (*C.rgb('#b07a58'), 255) if (x % 3 == 0 and y % 3 == 0) else (*C.rgb('#e6ae7e'), 255)
        f = Image.fromarray(a, 'RGBA')
    f = C.recolor(f, SHIGE)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        cx = (fx0 + fx1) // 2
        # 胸前两排 V 形黄珠（校服的滚边）
        pts = [(cx - 4, fy1 + 3), (cx - 3, fy1 + 5), (cx - 2, fy1 + 7), (cx + 2, fy1 + 7), (cx + 3, fy1 + 5), (cx + 4, fy1 + 3)]
        a = np.array(f)
        g = C.comp(f, ['#3e9a52', '#226a36', '#62c072'])
        for x, y in pts:
            if 0 <= y < a.shape[0] and 0 <= x < a.shape[1] and g[y, x]:
                a[y, x] = (*C.rgb('#ffd83c'), 255)
        f = Image.fromarray(a, 'RGBA')
    if big:
        f = widen(f, 1.22, 21)
    return C.reoutline(C.strip_outline(f))


def crawl_frames():
    """爬：躺倒的那一帧，前后挪一个像素、手一伸一缩（两帧）"""
    d = C.frames('npc_kid', 'down')[0]
    out = []
    for dx in (0, 2):
        g = Image.new('RGBA', d.size, (0, 0, 0, 0))
        g.alpha_composite(d, (dx, 0))
        out.append(shigechi_fix(g, big=False))
    return out


def build_shigechi():
    im, m = C.base('npc_kid')
    sh = C.Sheet('shigechi', '矢安宫重清', m['cell'], m['pivot'])
    for a, na, fps, kind in [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('run', 'run', 10, 'loop'),
                             ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'), ('talk', 'talk', 4, 'loop')]:
        sh.add(na, [shigechi_fix(f) for f in C.frames('npc_kid', a)], fps, kind)
    sh.add('crawl', crawl_frames(), 4, 'loop')
    sh.add('cry', [shigechi_fix(f) for f in C.frames('npc_kid', 'hurt')], 1, 'static')
    hd = C.heads('npc_kid')
    nm = []
    for f in (hd.get('portrait') or next(iter(hd.values()))):
        g = C.recolor(f, SHIGE)
        a = np.array(g)
        hair = C.comp(g, ['#2c1e18'], (0, 0, 32, 16))
        ys, xs = np.nonzero(hair)
        for y, x in zip(ys, xs):
            a[y, x] = (*C.rgb('#c88c64'), 255) if (x % 4 == 1 and y % 4 == 1) else (*C.rgb('#e6ae7e'), 255)
        nm.append(Image.fromarray(a, 'RGBA'))
    sh.heads = three_heads(nm)
    return C.save(sh, amap={'talk': 'talk', 'shock': 'hurt', 'hurt': 'hurt', 'down': 'down', 'run': 'run', 'cmd': 'talk', 'special': 'talk'}, bodyW=4)


# ============================================================ 丰收：自己画（黄身紫纹、品红眼，蜂一样的小人）
HV = dict(o=(40, 22, 40), y=(250, 214, 60), Y=(255, 240, 150), d=(196, 150, 30), p=(110, 60, 150), P=(70, 34, 100), e=(230, 40, 150), w=(255, 255, 255),
          c=(240, 200, 60), C=(170, 120, 30))


def harvest_frame(t=0, carry=False, hurt=False, step=0):
    W, H = 22, 26
    a = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    bob = 1 if t else 0
    cx, hy = 11, 9 - bob
    head = ((xx - cx) / 4.6) ** 2 + ((yy - hy) / 4.2) ** 2 <= 1
    body = ((xx - cx) / 5.2) ** 2 + ((yy - (hy + 8)) / 4.6) ** 2 <= 1
    m = head | body
    # 两对小手
    for dx, dy in ((-6, 6), (6, 6), (-6, 9), (6, 9)):
        if carry and dy == 6:
            dy, dx = 2, dx * 0.7
        m |= ((xx - (cx + dx)) / 1.3) ** 2 + ((yy - (hy + dy)) / 1.6) ** 2 <= 1
    # 腿：走路时一前一后
    for i, dx in enumerate((-2, 2)):
        off = (1 if (i + step) % 2 else -1) if step else 0
        m |= (np.abs(xx - (cx + dx + off)) <= 0.8) & (yy >= hy + 11) & (yy <= hy + 15)
    a[m] = (*HV['y'], 255)
    hl = m & (((xx - (cx - 1.6)) / 2.2) ** 2 + ((yy - (hy - 1.6)) / 1.8) ** 2 <= 1)
    a[hl] = (*HV['Y'], 255)
    # 身子上的紫色横纹
    for k in (hy + 6, hy + 9, hy + 12):
        s = body & (np.abs(yy - k) <= 0.6)
        a[s] = (*HV['p'], 255)
    sh = body & (xx > cx + 2.5)
    a[sh & ~(a[..., 0] == HV['p'][0])] = (*HV['d'], 255)
    # 头顶两根触角、尖鼻子
    for dx in (-2, 2):
        for k in range(3):
            y, x = int(hy - 4 - k), int(cx + dx + (dx // 2) * k)
            if 0 <= y < H and 0 <= x < W:
                a[y, x] = (*HV['P'], 255)
    # 眼睛：半圆的品红眼
    for dx in (-2, 1):
        a[int(hy), int(cx + dx):int(cx + dx) + 2] = (*HV['e'], 255)
        a[int(hy) - 1, int(cx + dx)] = (*HV['w'], 255)
    a[int(hy) + 2, int(cx)] = (*HV['d'], 255)
    img = Image.fromarray(a, 'RGBA')
    if carry:
        # 头顶扛着一枚硬币
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ca = np.array(c)
        coin = ((xx - cx) / 3.2) ** 2 + ((yy - (hy - 7)) / 1.6) ** 2 <= 1
        ca[coin] = (*HV['c'], 255)
        ca[coin & (yy > hy - 7)] = (*HV['C'], 255)
        c = Image.fromarray(ca, 'RGBA')
        c.alpha_composite(img)
        img = c
    if hurt:
        img = img.rotate(-25, resample=Image.NEAREST, center=(cx, H - 6))
    return C.reoutline(img, HV['o'])


def build_harvest():
    sh = C.Sheet('harvest', '丰收', (22, 26), (11, 25))
    sh.add('idle', [harvest_frame(0), harvest_frame(1)], 4, 'loop')
    sh.add('walk', [harvest_frame(0, step=1), harvest_frame(1, step=2)], 10, 'loop')
    sh.add('carry', [harvest_frame(0, True, step=1), harvest_frame(1, True, step=2)], 10, 'loop')
    sh.add('hurt', [harvest_frame(0, hurt=True)], 1, 'static')
    big = harvest_frame(0).resize((88, 104), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((28, 18, 60, 50)))
    sh.heads = {'normal': [face, face]}
    e = C.save(sh, amap={'talk': 'idle', 'run': 'walk', 'hurt': 'hurt', 'down': 'hurt', 'shock': 'hurt', 'cmd': 'carry', 'punch': 'walk',
                         'special': 'walk', 'guard': 'idle', 'dodge': 'walk'}, kind='stand', bodyW=2)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 吉良吉影（西装）：迪奥的身子 → 淡紫西装、绿条纹衬衫、深棕骷髅领带、蓝灰眼
KIRA = {'#f8b418': '#c4b0e4', '#ffc21c': '#d6c6ee', '#b4640c': '#8c76b8', '#a4600c': '#7a64a6', '#6e3606': '#4c3a74',
        '#2e2840': '#a894cc', '#4a4266': '#bcaade', '#17121f': '#6a5890',
        '#2c4a36': '#3e9a62', '#15261c': '#246a40',
        '#ff2438': '#6e7f9c', '#5a3486': '#4a3a2a'}


KIRA_HEAD = {'#f8b418': '#ffdc70', '#ffc21c': '#fff07a', '#6e3606': '#dcae3c', '#2c4a36': '#dca184', '#249040': '#dca184', '#15261c': '#dca184', '#a4600c': '#dcae3c', '#b4640c': '#dcae3c'}


def kira_fix(f):
    fb = C.face_box(f, 26, [(251, 214, 180), (220, 161, 132)])
    if fb:
        # 迪奥的绿嘴唇、额头的心形发带：在头部换回皮肤色、发色（吉良没有这些）
        f = C.recolor(f, KIRA_HEAD, (fb[0] - 14, 0, fb[2] + 8, fb[3] + 1))
    f = C.recolor(f, KIRA)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        cx = (fx0 + fx1) // 2
        a = np.array(f)
        shirt = C.comp(f, ['#3e9a62', '#246a40'], (fx0 - 6, fy1, fx1 + 6, fy1 + 20))
        ys, xs = np.nonzero(shirt)
        for y, x in zip(ys, xs):
            if x % 2 == 0:
                a[y, x] = (*C.rgb('#e8f4ec'), 255)        # 白条纹
        # 领带：衬衫中线一条深棕，中间一个小白点（骷髅）
        col = [x for x in range(cx - 2, cx + 3) if shirt[:, x].any()] if shirt.any() else []
        tx = int(np.median(np.nonzero(shirt)[1])) if shirt.any() else cx
        for y in range(fy1 + 2, fy1 + 13):
            if 0 <= y < a.shape[0] and a[y, tx][3]:
                a[y, tx] = (*C.rgb('#4a2e1e'), 255)
                if 0 <= tx + 1 < a.shape[1] and a[y, tx + 1][3] and y < fy1 + 11:
                    a[y, tx + 1] = (*C.rgb('#5e3a26'), 255)
        y = fy1 + 7
        if 0 <= y < a.shape[0]:
            a[y, tx] = (*C.rgb('#f0ece0'), 255)
        void = col
        f = Image.fromarray(a, 'RGBA')
    return f


def build_kira():
    im, m = C.base('dio')
    sh = C.Sheet('kira', '吉良吉影', m['cell'], m['pivot'])
    for a, na, fps, kind in [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('punch', 'point', 6, 'oneshot'), ('pose', 'pose', 3, 'oneshot'),
                             ('laugh', 'laugh', 4, 'loop'), ('hurt', 'hurt', 1, 'static'), ('throw', 'throw', 6, 'oneshot')]:
        sh.add(na, [kira_fix(f) for f in C.frames('dio', a)], fps, kind)
    hd = C.heads('dio')
    kh = lambda f: C.recolor(C.recolor(f, KIRA_HEAD, (0, 0, 32, 25)), KIRA)
    nm = [kh(f) for f in hd['portrait']]
    rg = [kh(f) for f in (hd.get('portrait_rage') or hd['portrait'])]
    if len(nm) == 1:
        nm = nm * 2
    if len(rg) == 1:
        rg = rg * 2
    sh.heads = {'normal': nm, 'smile': [HD.smile(f) for f in nm], 'shock': [HD.shock(f, i) for i, f in enumerate(nm)], 'rage': rg}
    e = C.save(sh, amap={'talk': 'idle', 'shock': 'hurt', 'run': {'a': 'walk', 'f': 1.6}, 'cmd': 'point', 'special': 'pose', 'down': 'hurt'}, bodyW=4)
    e['headAlias'] = {}
    return e


# ============================================================ 杀手皇后：世界的身子 → 浅粉、深紫手套腰布、金骷髅扣、猫耳
KQ = {'#f6c63a': '#f2c4d2', '#b8841a': '#cc8ca4', '#fff6c0': '#fff0f4', '#7a520e': '#8a4a66', '#ffe070': '#f8dce6', '#e8a820': '#e0a8bc',
      '#3cc46a': '#6c3c8e', '#1b7040': '#44225e', '#0e3a24': '#26102f', '#a8f080': '#9a6ac2',
      '#801020': '#c89a30', '#d02838': '#f0c850'}


def cat_ears(f):
    """头顶两只三角耳：最上面几行的不透明范围就是头，左右两端各竖起一只"""
    a = np.array(f.convert('RGBA'))
    op = a[..., 3] > 0
    rows = np.nonzero(op.any(1))[0]
    if not len(rows):
        return f
    y0 = rows[0]
    xs = np.nonzero(op[y0 + 3])[0] if y0 + 3 < a.shape[0] else np.nonzero(op[y0])[0]
    if not len(xs):
        return f
    xl, xr = xs.min(), xs.max()
    if xr - xl > 22:          # 头低下去 / 伸手的帧：最上面不是头，就不画
        return f
    pink, dark = C.rgb('#f2c4d2'), C.rgb('#cc8ca4')
    for k in range(4):
        y = y0 + 1 - k
        for x in range(xl + 1, xl + 4 - k):
            if 0 <= y < a.shape[0]:
                a[y, x] = (*(dark if x == xl + 1 else pink), 255)
        for x in range(xr - 3 + k, xr):
            if 0 <= y < a.shape[0]:
                a[y, x] = (*(dark if x == xr - 1 else pink), 255)
    return C.reoutline(Image.fromarray(a, 'RGBA'))


def build_killerqueen():
    im, m = C.base('theworld')
    sh = C.Sheet('killerqueen', '杀手皇后', m['cell'], m['pivot'])
    for anim, a in m['animations'].items():
        if anim.startswith('portrait'):
            continue
        sh.add(anim, [cat_ears(C.recolor(f, KQ)) for f in C.frames('theworld', anim)], a.get('fps', 6), a.get('kind', 'loop'))
    hd = C.heads('theworld')
    nm = [C.recolor(f, KQ) for f in hd['portrait']]
    sh.heads = {'normal': nm}
    e = C.save(sh, amap={'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'kick', 'rush': 'rush', 'block': 'pose', 'hurt': 'hurt',
                         'special': 'pose', 'finger': 'punch'}, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 杉本铃美：女学生的身子 → 粉色短发、黄发箍、浅粉无袖裙
REIMI = {'#1e1a22': '#f2a0c4', '#0e0c12': '#c86a96', '#3e3846': '#ffd0e2',                 # 头发：粉
         '#2c3462': '#fad2e0', '#181d3e': '#dca0b8', '#e0303c': '#e8689c', '#9a2a44': '#b04878',
         '#6a4228': '#f0a8c4', '#5a361e': '#c87898', '#3a2a22': '#a05a7a'}


def reimi_fix(f):
    fb = C.face_box(f, 24)
    f = C.recolor(f, REIMI)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        a = np.array(f)
        y = fy0 - 2
        hair = C.comp(f, ['#f2a0c4', '#c86a96', '#ffd0e2'], (fx0 - 6, y, fx1 + 6, y + 1))
        for x in np.nonzero(hair[y])[0] if 0 <= y < a.shape[0] else []:
            a[y, x] = (*C.rgb('#f6d84a'), 255)                 # 黄发箍
        f = Image.fromarray(a, 'RGBA')
    return f


def build_reimi():
    im, m = C.base('npc_student_f_a')
    sh = C.Sheet('reimi', '杉本铃美', m['cell'], m['pivot'])
    for a, fps, kind in [('idle', 2, 'loop'), ('walk', 8, 'loop'), ('cheer', 4, 'loop'), ('down', 1, 'static')]:
        sh.add(a, [reimi_fix(f) for f in C.frames('npc_student_f_a', a)], fps, kind)
    hd = C.heads('npc_student_f_a')
    nm = [C.recolor(f, REIMI) for f in (hd.get('portrait') or next(iter(hd.values())))]
    sh.heads = three_heads(nm)
    e = C.save(sh, amap={'talk': 'idle', 'shock': 'idle', 'hurt': 'idle', 'run': 'walk', 'cmd': 'cheer'}, bodyW=3)
    e['headAlias'] = {}
    return e


# ============================================================ 阿诺德：伊奇的身子放大一圈 → 浅棕色的大狗
ARNOLD = {'#36313f': '#d2a66a', '#221e2a': '#a87c46', '#0c0a10': '#5e3e22', '#5c566e': '#e6c08a',
          '#f4f2f8': '#f2dcae', '#b8b8ca': '#cfae7c', '#d8708e': '#2a2026', '#f07888': '#3a2a2a', '#f2c65a': '#8a5a2a'}


def build_arnold():
    im, m = C.base('iggy')
    cell, piv = [48, 44], [24, 44]
    sh = C.Sheet('arnold', '阿诺德', cell, piv)
    for a, na, fps, kind in [('idle', 'idle', 2, 'loop'), ('run', 'run', 10, 'loop'), ('sit', 'sit', 1, 'static')]:
        sh.add(na, [scale(C.recolor(f, ARNOLD), 1.35, cell, piv) for f in C.frames('iggy', a)], fps, kind)
    hd = C.heads('iggy')
    nm = [C.recolor(f, ARNOLD) for f in hd['portrait']]
    sh.heads = {'normal': nm * (2 if len(nm) == 1 else 1)}
    e = C.save(sh, amap={'talk': 'idle', 'walk': 'run', 'shock': 'sit', 'hurt': 'sit', 'down': 'sit'}, bodyW=5)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 临时图（别章的人合进来之前顶着用，合进来以后删）
def build_tmp_joseph():
    # 第4章画正式的：第三部乔瑟夫，头发、胡子换白
    cmap = {'#4e3018': '#d8d8dc', '#6a3e20': '#b8b8c0', '#8e5a30': '#ececf0'}
    return C.build_recolor('tmp6_joseph', '乔瑟夫·乔斯达', 'joseph',
                           [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 6, 'loop'), ('point', 'point', 4, 'loop'), ('shock', 'shock', 1, 'static'),
                            ('hurt', 'hurt', 1, 'static')],
                           cmap=cmap, amap={'talk': 'idle', 'run': 'walk', 'cmd': 'point'}, bodyW=4)


BUILDERS = {'shigechi': build_shigechi, 'harvest': build_harvest, 'kira': build_kira, 'killerqueen': build_killerqueen,
            'reimi': build_reimi, 'arnold': build_arnold,
            'tmp6_joseph': build_tmp_joseph}

HEROES = {
    'shigechi': dict(cid='shigechi', cn='矢安宫重清', short='重清', rn='YANGU SHIGEKIYO', stand='harvest',
                     burst=['#2a6a2a', '#4a9a3a', '#ffd83c'], panel='#0e200a', accent='#ffd83c', nameColor='#5a9a3a', blipHz=700, grunt=None),
    'harvest': dict(cid='harvest', cn='丰收', short='丰收', rn='HARVEST', stand=None,
                    burst=['#6a4a10', '#c89a20', '#ffe070'], panel='#2a1e06', accent='#ffd83c', nameColor='#c8a020', blipHz=1100, grunt=None),
}
SPEAKERS = {
    'reimi': dict(short='铃美', nameColor='#d870a0', blipHz=820),
    'arnold': dict(short='阿诺德', nameColor='#b08850', blipHz=300),
    'kira': dict(short='吉良', nameColor='#8c76b8', blipHz=420),
    'killerqueen': dict(short='杀手皇后', nameColor='#d48aa6', blipHz=460),
    'tmp6_joseph': dict(short='乔瑟夫', nameColor='#6a8a5a', blipHz=360),
}
STANDS = {
    'harvest': dict(cn='丰收', en='HARVEST', owner='shigechi', aura='#ffd83c', card='#ffe070', ghost='#fff0a0',
                    impact='pink', kind='humanoid', idle={'dx': -8, 'z': 0}, link=None, summonSfx=None, fist=False),
    'killerqueen': dict(cn='杀手皇后', en='KILLER QUEEN', owner='kira', aura='#e8a0c0', card='#f2c4d2', ghost='#f8dce6',
                        impact='pink', kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx='stand_summon_star', fist=True),
}


def main(ids):
    path = os.path.join(L.META, 'chars_ch6.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', list(meta['chars'][cid]['animations']), '表情', list(meta['chars'][cid]['heads']))
    meta['heroes'] = HEROES
    meta['speakers'] = SPEAKERS
    meta['stands'] = STANDS
    L.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
