# 第5章的新角色：岸边露伴 / 天堂之门、老鼠（虫食）/ Ratt，外加本章的道具（平底锅、钢珠、飞镖、原稿、步枪子弹、照片……）。
#   露伴拿第三部波鲁纳雷夫的全尺寸图集当底子（瘦高、无袖上衣、白裤子，和露伴第一套衣服的剪裁最接近）：
#   挖掉银色高塔头，画露伴的深绿短发 + 锯齿边的绿头带，上衣换成浅绿背心 + 里面的浅紫衬衫，鞋换浅绿，眼睛换绿，
#   再按第三部 shrink.py 缩小。配色照 TV 动画第四部（JoJo Wiki 的配色表：深绿头发、绿眼、绿色锯齿头带、
#   浅紫衬衫外套浅绿背心、白裤子、浅绿鞋），耳朵上挂钢笔尖耳环（金色一格）。
#   天堂之门和老鼠都是自己画的（第三部没有相近的底子）。
#   元数据写 assets/_meta/chars_ch5.json（chars / heroes / speakers / stands）和 props_ch5.json，不碰 chars.json（分章开发约定 §2）。
#   用法：python3 第四部/tools/art/p4_chars_ch5.py
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402
import p4_heads as HD  # noqa: E402

O = C.O

# ============================================================ 岸边露伴
# 头发：深绿（动画里偏一点青）
RH = dict(d=(16, 44, 36), m=(30, 78, 60), l=(58, 120, 88), x=(112, 170, 124))
BAND = dict(l=(170, 222, 96), m=(118, 180, 62), d=(64, 112, 40))      # 头带：黄绿，锯齿边压暗
VEST = {(42, 38, 50): (150, 206, 124), (78, 72, 96): (104, 160, 92)}   # 波鲁的黑上衣 → 浅绿背心
SHIRT = (196, 168, 226)                                                # 里面的浅紫衬衫（领口那一条）
SHIRT_D = (150, 120, 190)
SHOES = {(90, 54, 30): (140, 206, 112), (138, 90, 52): (176, 230, 140), (42, 30, 26): (60, 112, 52)}
BELT = (74, 58, 90)
EYE = (52, 150, 96)
POL_HAIR = [(216, 220, 242), (214, 220, 236), (144, 152, 182), (158, 162, 204), (246, 248, 255), (96, 104, 138), (78, 72, 96)]
POL_SKIN = [(246, 196, 154), (216, 148, 108)]
POL_EYE = (60, 120, 224)
NIB = (255, 216, 60)


def rohan_hair(img, s=1.0, top_rows=24, band=True, portrait=False):
    """挖掉波鲁的高塔头，画露伴的头发和头带。人朝右：脸在右，后脑在左。"""
    fb = C.face_box(img, top_rows, POL_SKIN)
    if not fb:
        return img
    fx0, fy0, fx1, fy1 = fb
    a = np.array(img.convert('RGBA'))
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    # 1) 挖头发：脸的包围盒往上、往后一大块里所有银色 + 描边（脸前面只挖额头以上）
    box = (int(fx0 - 9 * s), 0, int(fx1 + 4 * s), int(fy1 + (0 if portrait else 1)))
    old = C.comp(img, POL_HAIR + [O], box)
    old &= ~((xx > fx1) & (yy > fy0))
    if portrait:
        old &= yy < fy1 - 1
    a[old] = (0, 0, 0, 0)
    # 2) 新头发的形状
    fw = fx1 - fx0
    cx, cy = fx0 + fw * 0.42, fy0 + 0.5 * s
    skull = ((xx - cx) / (fw * 0.5 + 3.2 * s)) ** 2 + ((yy - cy) / (5.6 * s)) ** 2 <= 1
    skull &= yy <= fy0 + 1.5 * s
    # 后脑垂到脖子（短发，外翘一点）
    back = (xx >= fx0 - 4.0 * s) & (xx <= fx0 + 1.8 * s) & (yy >= fy0) & (yy <= fy1 - 2.0 * s)
    flick = ((xx - (fx0 - 3.2 * s)) / (2.0 * s)) ** 2 + ((yy - (fy1 - 2.6 * s)) / (1.6 * s)) ** 2 <= 1
    # 头顶几撮翘起来的发尖（头带上面露出来的那一圈）
    tufts = np.zeros((h, w), bool)
    for k, (dx, hh, lean) in enumerate(((-0.25, 1.6, -0.5), (0.12, 2.2, -0.2), (0.45, 2.0, 0.3), (0.75, 1.4, 0.7))):
        tx, ty = fx0 + fw * dx, fy0 - 4.2 * s
        u = (ty + 1.0 - yy)
        tri = (yy <= ty + 1.0) & (yy >= ty - hh * s) & (np.abs(xx - tx - u * lean) <= (hh * s - u) * 0.6 + 0.4)
        tufts |= tri
    # 鬓角：耳朵前面一小条往下
    side = (xx >= fx0 + 1.5 * s) & (xx <= fx0 + 2.6 * s) & (yy >= fy0) & (yy <= fy0 + 3.5 * s)
    mask = skull | back | flick | tufts | side
    face = C.comp(Image.fromarray(a, 'RGBA'), POL_SKIN + [POL_EYE, (255, 255, 255), (239, 230, 210)])
    mask &= ~(face & (yy >= fy0 + 1) & ~side & ~back)
    shade = np.ones((h, w), int)
    up = np.zeros_like(mask)
    up[1:, :] = mask[:-1, :]
    shade[mask & ~up] = 2
    shade[tufts & ~skull] = 1
    shade[tufts & ~skull & ~np.roll(tufts, 1, axis=1)] = 0
    shade[back & (yy > fy0 + 1.5 * s)] = 0
    shade[side] = 0
    shade[flick] = 0
    pal = {0: RH['d'], 1: RH['m'], 2: RH['l'], 3: RH['x']}
    for k, c in pal.items():
        a[mask & (shade == k)] = (*c, 255)
    # 3) 头带：额头上两行（大图三行），从后脑一直绕到额前；上沿一格一格压暗 = 锯齿
    if band:
        bh = max(2, int(round(2 * s)))
        by0 = int(round(fy0 - 1 - bh + 1))
        bx0 = int(round(cx - (fw * 0.5 + 3.2 * s))) + 1
        bx1 = int(fx1 + 1)
        for y in range(by0, by0 + bh):
            for x in range(bx0, bx1 + 1):
                if 0 <= x < w and 0 <= y < h and (mask[y, x] or (x > fx0 and y >= fy0 - 1)):
                    a[y, x] = (*BAND['l' if y == by0 else 'm'], 255)
        for x in range(bx0, bx1 + 1, 2):
            if 0 <= x < w and 0 <= by0 < h:
                a[by0, x] = (*BAND['d'], 255)
        if portrait:
            for x in range(bx0 + 1, bx1 + 1, 2):
                y = by0 + bh
                if 0 <= x < w and y < h and a[y, x][3] and tuple(a[y, x][:3]) not in (tuple(SHIRT),):
                    a[y, x] = (*BAND['d'], 255)
    img2 = C.reoutline(Image.fromarray(a, 'RGBA'))
    # 眼睛：蓝 → 绿
    img2 = C.recolor(img2, {POL_EYE: EYE})
    # 钢笔尖耳环：后脑和脸交界、下巴往上 3 行
    ex, ey = int(fx0 + 1.5 * s), int(fy1 - 3 * s)
    img2 = C.put(img2, [(ex, ey)], NIB)
    if s > 1.4:
        img2 = C.put(img2, [(ex, ey + 1)], (200, 154, 32))
    return img2


def rohan_body(f, top_rows=24):
    f = C.recolor(f, VEST)
    f = C.recolor(f, {(90, 54, 30): BELT}, (0, 0, f.width, f.height - 9))
    f = C.recolor(f, SHOES)
    fb = C.face_box(f, top_rows, POL_SKIN)
    f = rohan_hair(f, top_rows=top_rows)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        # 背心敞着，中间露出一条浅紫衬衫（领口往下 6 行）
        a = np.array(f)
        cx = int(round((fx0 + fx1) / 2)) - 1
        vest = set(VEST.values())
        for y in range(fy1 + 2, fy1 + 9):
            for x in (cx, cx + 1):
                if 0 <= y < a.shape[0] and tuple(a[y, x][:3]) in vest:
                    a[y, x] = (*(SHIRT if x == cx else SHIRT_D), 255)
        f = Image.fromarray(a, 'RGBA')
    return f


def rohan_portrait(f):
    # 整张往下挪 2 行：头顶的发尖要有地方画（领口最下面两行切掉）
    g = Image.new('RGBA', f.size, (0, 0, 0, 0))
    g.alpha_composite(f.crop((0, 0, f.width, f.height - 2)), (0, 2))
    f = C.recolor(g, VEST)
    f = rohan_hair(f, s=1.6, top_rows=32, portrait=True)
    a = np.array(f)
    # 领口那一块：中间露浅紫衬衫
    vest = set(VEST.values())
    for y in range(26, 32):
        for x in range(13, 19):
            if tuple(a[y, x][:3]) in vest:
                a[y, x] = (*(SHIRT if x < 16 else SHIRT_D), 255)
    return Image.fromarray(a, 'RGBA')


def rohan_rage(f):
    """生气：眉毛压成往里斜的两道，嘴抿成一条"""
    a = np.array(f.convert('RGBA'))
    fb = C.face_box(f, 32, POL_SKIN)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        ey = None
        eye = (a[..., 0] == EYE[0]) & (a[..., 1] == EYE[1]) & (a[..., 2] == EYE[2])
        ys, xs = np.where(eye)
        if len(ys):
            ey = int(ys.min()) - 2
            for side in (xs < xs.mean(), xs >= xs.mean()):
                x0, x1 = int(xs[side].min()), int(xs[side].max())
                for i, x in enumerate(range(x0 - 1, x1 + 2)):
                    yy = ey + (i if side is not None and x0 < xs.mean() else (x1 + 1 - x)) // 2
                    if 0 <= yy < a.shape[0]:
                        a[min(yy, ey + 1), x] = (*O, 255)
    return Image.fromarray(a, 'RGBA')


def build_rohan():
    im, m = C.base('polnareff')
    sh = C.Sheet('rohan', '岸边露伴', m['cell'], m['pivot'])
    # 第三部动作 → 露伴的动作（fight 是伸直手臂的姿势，正好当“天堂之门！”的指）
    for src, anim, fps, kind in [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('walk', 'run', 12, 'loop'),
                                 ('fight', 'point', 4, 'loop'), ('wave', 'pose', 3, 'loop'), ('shock', 'shock', 4, 'loop'),
                                 ('hurt', 'hurt', 1, 'static'), ('dodge', 'dodge', 1, 'static'), ('guard', 'guard', 1, 'static'),
                                 ('kneel', 'kneel', 1, 'static')]:
        sh.add(anim, [rohan_body(f) for f in C.frames('polnareff', src)], fps, kind)
    # 写字：伸手那一帧 + 收回一点（笔尖在空中划）
    pf = C.frames('polnareff', 'fight')
    sh.add('write', [rohan_body(pf[0]), rohan_body(pf[1]), rohan_body(pf[0])], 6, 'loop')
    down = []
    for f in C.frames('polnareff', 'down'):
        f = C.recolor(f, VEST)
        f = C.recolor(f, SHOES)
        r = f.rotate(-90, expand=True)
        r = rohan_hair(r, top_rows=30)
        down.append(r.rotate(90, expand=True).crop((0, 0, f.width, f.height)))
    sh.add('down', down, 1, 'static')
    hd = C.heads('polnareff')
    nm = [rohan_portrait(f) for f in hd['portrait']]
    sk = [rohan_portrait(f) for f in hd['portrait_shock']]
    sh.heads = {'normal': nm, 'smile': [HD.smile(f) for f in nm], 'shock': sk, 'rage': [rohan_rage(f) for f in nm]}
    e = C.save(sh, amap=dict(C.AMAP_HUMAN, cmd='point', cmd2='point', cmd_hold='write', special='point', win='pose', run='run',
                             kneel='kneel', write='write', shock='shock'), bodyW=4)
    e['headAlias'] = {}
    return e


# ============================================================ 天堂之门（小小的、像露伴笔下的少年：宽檐帽 + 披风，米白和金色）
HDC = dict(o=(40, 24, 30), w=(255, 250, 236), c=(240, 226, 196), s=(204, 182, 146), g=(246, 206, 92), G=(196, 150, 50),
           p=(238, 150, 176), k=(30, 20, 30), b=(120, 196, 120))


def hd_frame(pose='idle', t=0.0, w=40, h=46):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bob = int(round(np.sin(t * 2 * np.pi) * 1))
    cx, base = 18, 40 + bob
    lean = {'idle': 0, 'punch': 3, 'rush': 2, 'block': -1, 'hurt': -2, 'write': 1}.get(pose, 0)
    c = lambda k: HDC[k]
    # 披风
    d.polygon([(cx - 6 + lean, base - 18), (cx + 4 + lean, base - 18), (cx + 6, base - 2), (cx - 9, base - 1)], fill=c('c'))
    d.polygon([(cx - 6 + lean, base - 18), (cx - 2 + lean, base - 18), (cx - 4, base - 1), (cx - 9, base - 1)], fill=c('s'))
    # 腿（短）
    d.rectangle((cx - 3, base - 3, cx - 2, base), fill=c('s'))
    d.rectangle((cx + 1, base - 3, cx + 2, base), fill=c('s'))
    # 身子：胸前一颗金扣
    d.rectangle((cx - 4 + lean, base - 17, cx + 3 + lean, base - 6), fill=c('w'))
    d.point((cx + lean, base - 13), fill=c('g'))
    d.point((cx + lean, base - 10), fill=c('g'))
    # 头
    hx, hy = cx + lean + 1, base - 22
    d.ellipse((hx - 4, hy - 4, hx + 4, hy + 4), fill=c('w'))
    d.point((hx + 2, hy), fill=c('k'))
    d.point((hx + 2, hy + 2), fill=c('p'))
    # 宽檐帽：檐一条 + 帽顶，金色帽带
    d.rectangle((hx - 7, hy - 4, hx + 7, hy - 3), fill=c('g'))
    d.rectangle((hx - 4, hy - 9, hx + 3, hy - 4), fill=c('c'))
    d.rectangle((hx - 4, hy - 5, hx + 3, hy - 5), fill=c('G'))
    d.point((hx + 4, hy - 10), fill=c('b'))
    d.point((hx + 5, hy - 11), fill=c('b'))
    # 手
    if pose in ('punch', 'write'):
        d.line((cx + 3 + lean, base - 14, cx + 11 + lean, base - 15), fill=c('w'), width=2)
        if pose == 'write':
            d.line((cx + 11 + lean, base - 16, cx + 15 + lean, base - 19), fill=c('k'))
            d.point((cx + 15 + lean, base - 19), fill=c('g'))
        else:
            # 指尖翻开的一页纸
            d.polygon([(cx + 12 + lean, base - 19), (cx + 18 + lean, base - 17), (cx + 17 + lean, base - 11), (cx + 12 + lean, base - 12)],
                      fill=c('w'))
            d.line((cx + 13 + lean, base - 16, cx + 16 + lean, base - 15), fill=c('s'))
    elif pose == 'rush':
        for k in range(3):
            y = base - 17 + k * 3
            d.line((cx + 3 + lean, y, cx + 10 + lean + (k % 2) * 3, y - 1), fill=c('w'), width=1)
    elif pose == 'block':
        d.rectangle((cx + 2, base - 18, cx + 6, base - 8), fill=c('c'))
        d.line((cx + 3, base - 16, cx + 5, base - 16), fill=c('s'))
        d.line((cx + 3, base - 13, cx + 5, base - 13), fill=c('s'))
    else:
        d.line((cx + 3 + lean, base - 14, cx + 5 + lean, base - 8), fill=c('w'), width=2)
    return L.outline(im, (*HDC['o'], 255))


def build_heavensdoor():
    sh = C.Sheet('heavensdoor', '天堂之门', (40, 46), (18, 44))
    sh.add('idle', [hd_frame('idle', t / 4) for t in range(4)], 6, 'loop')
    sh.add('punch', [hd_frame('idle'), hd_frame('punch'), hd_frame('punch')], 10, 'oneshot')
    sh.add('upper', [hd_frame('idle'), hd_frame('punch'), hd_frame('punch')], 10, 'oneshot')
    sh.add('rush', [hd_frame('rush', 0), hd_frame('rush', 0.5)], 14, 'loop')
    sh.add('block', [hd_frame('block')], 1, 'static')
    sh.add('hurt', [hd_frame('hurt')], 1, 'static')
    sh.add('write', [hd_frame('write', 0), hd_frame('write', 0.5)], 8, 'loop')
    big = hd_frame('idle').resize((80, 92), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((22, 6, 54, 38)))
    sh.heads = {'normal': [face, face]}
    e = C.save(sh, amap={'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'upper', 'rush': 'rush', 'block': 'block', 'hurt': 'hurt',
                         'special': 'write', 'finger': 'punch', 'write': 'write'}, kind='stand', bodyW=4)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 老鼠（虫食）+ Ratt
#   灰褐色的田鼠，背上一门“枪”（替身 Ratt：灰金属的小炮管，开火前从背上翻起来）。虫食的左耳有个缺口（ear_nick=True）。
RT = dict(o=(30, 20, 22), d=(84, 66, 60), m=(124, 104, 92), l=(166, 146, 128), x=(206, 190, 170), p=(232, 150, 160),
          k=(14, 10, 12), e=(220, 40, 40), g=(110, 116, 128), G=(160, 168, 182), D=(60, 64, 76))


def rat_frame(gun=0.0, step=0, nick=False, flat=False, w=36, h=22):
    """gun 0 = 炮管趴在背上、1 = 翻起来对准前方；朝右"""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = lambda k: RT[k]
    base = h - 3
    by = base - (2 if flat else 6)
    # 尾巴
    d.line((4, base - 3, 10, by + 2), fill=c('p'))
    d.line((2, base - 2, 4, base - 3), fill=c('p'))
    # 身子
    d.ellipse((8, by - 4, 24, by + 4), fill=c('m'))
    d.ellipse((10, by - 4, 22, by), fill=c('l'))
    d.ellipse((9, by + 1, 23, by + 4), fill=c('d'))
    # 头 + 鼻子
    d.ellipse((19, by - 4, 28, by + 3), fill=c('m'))
    d.polygon([(26, by - 2), (31, by + 1), (26, by + 2)], fill=c('l'))
    d.point((31, by + 1), fill=c('p'))
    d.point((25, by - 1), fill=c('e'))      # 红眼睛（被箭射过）
    # 耳朵（虫食：左耳缺一口）
    d.ellipse((19, by - 7, 23, by - 3), fill=c('p'))
    d.ellipse((20, by - 6, 22, by - 4), fill=c('l'))
    if nick:
        d.point((21, by - 7), fill=(0, 0, 0, 0))
        d.point((22, by - 7), fill=(0, 0, 0, 0))
    # 脚（走路两帧）
    for fx in ((11, 20) if step == 0 else (13, 18)):
        d.rectangle((fx, base - 1, fx + 1, base), fill=c('d'))
    # Ratt：背上的炮管
    if gun > 0:
        ang = np.deg2rad(-8 + (1 - gun) * 70)
        gx, gy = 15, by - 4
        tx, ty = gx + np.cos(ang) * 9, gy - np.sin(ang) * 9 * (1 if gun < 1 else 0.3)
        d.line((gx, gy, tx, ty), fill=c('g'), width=3)
        d.line((gx, gy - 1, tx, ty - 1), fill=c('G'))
        d.rectangle((gx - 2, gy - 1, gx + 2, gy + 1), fill=c('D'))
        d.point((int(round(tx)), int(round(ty))), fill=c('k'))
    else:
        d.line((11, by - 4, 19, by - 5), fill=c('g'), width=2)
        d.line((11, by - 5, 19, by - 6), fill=c('G'))
    return L.outline(im, (*RT['o'], 255))


def build_rat(cid, name, nick):
    sh = C.Sheet(cid, name, (36, 22), (18, 20))
    sh.add('idle', [rat_frame(0, 0, nick), rat_frame(0, 0, nick, flat=True)], 2, 'loop')
    sh.add('walk', [rat_frame(0, 0, nick), rat_frame(0, 1, nick)], 12, 'loop')
    sh.add('aim', [rat_frame(0.5, 0, nick), rat_frame(1.0, 0, nick)], 8, 'oneshot')
    sh.add('fire', [rat_frame(1.0, 0, nick, flat=True)], 1, 'static')
    sh.add('hurt', [rat_frame(0, 0, nick, flat=True)], 1, 'static')
    sh.add('down', [rat_frame(0, 0, nick, flat=True).rotate(180).transpose(Image.FLIP_LEFT_RIGHT)], 1, 'static')
    e = C.save(sh, amap={'talk': 'idle', 'run': 'walk', 'cmd': 'aim', 'attack': 'fire', 'shock': 'hurt', 'guard': 'idle', 'dodge': 'walk',
                         'special': 'aim', 'pose': 'aim', 'point': 'aim'}, kind='char', bodyW=4)
    e['headAlias'] = {}
    return e


# ============================================================ 角色表（chars_ch5.json）
HEROES = {
    'rohan': dict(cid='rohan', cn='岸边露伴', short='露伴', rn='KISHIBE ROHAN', stand='heavensdoor',
                  burst=['#1e4a2a', '#3a7a44', '#8ad070'], panel='#0c2010', accent='#b8e070', nameColor='#4a9a5a',
                  blipHz=560, grunt=None),
}
SPEAKERS = {
    'heavensdoor': dict(short='天堂之门', nameColor='#d0a040', blipHz=700),
    'mushikui': dict(short='虫食', nameColor='#8a6a5a', blipHz=900),
    'rat_a': dict(short='老鼠', nameColor='#8a6a5a', blipHz=900),
    'spw_phone': dict(short='SPW 财团', nameColor='#6a8ab0', blipHz=420),
}
STANDS = {
    'heavensdoor': dict(cn='天堂之门', en="HEAVEN'S DOOR", owner='rohan', aura='#f0d070', card='#ffe8a0', ghost='#fff2c8',
                        impact='yellow', kind='humanoid', idle={'dx': -8, 'z': 10}, link=None, summonSfx='stand_summon_star', fist=False),
}


def main():
    meta = {'chars': {}}
    for cid, fn in [('rohan', build_rohan), ('heavensdoor', build_heavensdoor),
                    ('mushikui', lambda: build_rat('mushikui', '虫食', True)), ('rat_a', lambda: build_rat('rat_a', '老鼠', False))]:
        meta['chars'][cid] = fn()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', len(meta['chars'][cid]['animations']), '表情', list(meta['chars'][cid]['heads']))
    meta['heroes'] = HEROES
    meta['speakers'] = SPEAKERS
    meta['stands'] = STANDS
    L.save_json(os.path.join(L.META, 'chars_ch5.json'), meta)


if __name__ == '__main__':
    main()
