# 第1章的新角色：虹村形兆（第三部承太郎的身体换色 + 金发）、坏公司的三种兵（游戏尺寸直接画）、虹村家的父亲（剪影）。
#   亿泰 / 轰炸空间 / 回音的蛋归第2章画（p4_chars_ch2.py），这里不画。元数据写 _meta/chars_ch1.json（build_p4.py 深合并）。
#   配色照 TV 动画（JoJo Wiki 配色表）：形兆金发、绿眼、黑色校服 + 浅灰滚边、青色里衬、金色饰物、品红腰带、酒红鞋。
#   用法：python3 第四部/tools/art/p4_chars_ch1.py [cid ...]
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402
import p4_heads as HD  # noqa: E402

O = C.O

# ============================================================ 虹村形兆
# 承太郎的帽子形状本来就是“头顶平、后面垂下来”：头部范围里的藏青换成金色，正好是形兆的平头 + 脑后的头发
HAIR = {(84, 98, 168): (250, 232, 150), (43, 49, 96): (226, 192, 96), (48, 48, 78): (200, 160, 74),
        (24, 26, 56): (164, 124, 54), (28, 28, 52): (132, 98, 44), (255, 216, 60): (250, 232, 150), (200, 154, 32): (226, 192, 96)}
# 校服：黑，最亮的那层当浅灰滚边
COAT = {(84, 98, 168): (150, 150, 162), (43, 49, 96): (36, 34, 44), (48, 48, 78): (48, 46, 58),
        (24, 26, 56): (22, 20, 28), (28, 28, 52): (26, 24, 32),
        (74, 63, 102): (52, 128, 148), (51, 42, 74): (34, 92, 110),          # 里衬：青
        (138, 90, 52): (128, 38, 56), (90, 54, 30): (84, 22, 36)}          # 鞋：酒红
EYE = {(44, 196, 168): (70, 190, 90)}                                       # 绿眼


def keicho_frame(f, top_rows=24):
    fb = C.face_box(f, top_rows)
    f = C.recolor(f, EYE)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        f = C.recolor(f, HAIR, (0, 0, f.width, fy1 + 1))
        # 前额一绺卷：脸前上角补 3 个金色像素（动画里那一绺往前翘的头发）
        f = C.put(f, [(fx1 + 1, fy0), (fx1 + 2, fy0 - 1), (fx1 + 1, fy0 - 1)], (250, 232, 150))
        f = C.put(f, [(fx1 + 3, fy0 - 1)], O)
    return C.recolor(f, COAT)


def keicho_head(f):
    a = np.array(f.convert('RGBA'))
    H = a.shape[0]
    top = Image.fromarray(a[:22], 'RGBA')
    bot = Image.fromarray(a[22:], 'RGBA')
    top = C.recolor(C.recolor(top, EYE), HAIR)
    out = Image.new('RGBA', f.size, (0, 0, 0, 0))
    out.alpha_composite(top, (0, 0))
    out.alpha_composite(C.recolor(bot, COAT), (0, 22))
    return C.recolor(out, COAT)


def build_keicho():
    im, m = C.base('jotaro')
    sh = C.Sheet('keicho', '虹村形兆', m['cell'], m['pivot'])
    for anim, fps, kind in [('idle', 2, 'loop'), ('walk', 8, 'loop'), ('run', 10, 'loop'), ('point', 4, 'loop'), ('pose', 3, 'oneshot'),
                            ('shock', 1, 'static'), ('hurt', 1, 'static'), ('dodge', 1, 'static'), ('guard', 1, 'static'), ('sit', 1.5, 'loop')]:
        sh.add(anim, [keicho_frame(f) for f in C.frames('jotaro', anim)], fps, kind)
    down = []
    for f in C.frames('jotaro', 'down'):
        r = f.rotate(-90, expand=True)
        r = keicho_frame(r, top_rows=30)
        down.append(r.rotate(90, expand=True).crop((0, 0, f.width, f.height)))
    sh.add('down', down, 1, 'static')
    hd = C.heads('jotaro')
    nm = [keicho_head(f) for f in hd['portrait']]
    rg = [keicho_head(f) for f in hd['portrait_angry']]
    sh.heads = {'normal': nm, 'rage': rg, 'smile': [HD.smile(f) for f in nm], 'shock': [HD.shock(f, i) for i, f in enumerate(nm)]}
    e = C.save(sh, amap=dict(C.AMAP_HUMAN, sit='sit', run='run'), bodyW=4)
    e['headAlias'] = {}
    return e


# ============================================================ 坏公司：游戏尺寸直接画（一个兵 7×9 像素，朝右）
OL = (44, 58, 30)          # 橄榄绿：亮 / 中 / 暗
OM = (88, 106, 52)
OH = (128, 146, 74)
DK = (34, 34, 30)
SKN = (232, 180, 132)
FLASH = (255, 240, 150)
FL2 = (255, 170, 60)


def grid(rows, pal):
    """rows：字符画（'.' 透明），pal：字符 → 颜色"""
    h, w = len(rows), max(len(r) for r in rows)
    a = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and ch in pal:
                a[y, x] = (*pal[ch], 255)
    return Image.fromarray(a, 'RGBA')


def cell(img, cw, ch, px, py, ax, ay):
    """把小图 img 的锚点 (ax, ay) 放到格子的脚点 (px, py)"""
    c = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    c.alpha_composite(img, (px - ax, py - ay))
    return c


PAL = {'o': O, 'h': OH, 'm': OM, 'l': OL, 'd': DK, 's': SKN, 'f': FLASH, 'r': FL2, 'g': (90, 90, 96), 'w': (220, 220, 210)}

SOLDIER = {
    'idle0': ['..hm...', '.hmmm..', '.lsso..', '..ll...', '.lmmdd.', '.lmm...', '..ll...', '..l.l..', '.dd.dd.'],
    'idle1': ['.......', '..hm...', '.hmmm..', '.lsso..', '..ll...', '.lmmdd.', '.lmm...', '..l.l..', '.dd.dd.'],
    'walk0': ['..hm...', '.hmmm..', '.lsso..', '..ll...', '.lmmdd.', '.lmm...', '..ll...', '.l..l..', 'dd...d.'],
    'walk1': ['..hm...', '.hmmm..', '.lsso..', '..ll...', '.lmmdd.', '.lmm...', '..ll...', '..ll...', '..ddd..'],
    'aim': ['..hm.....', '.hmmm....', '.lsso....', '..lldddd.', '.lmm.....', '.lmm.....', '..ll.....', '..l.l....', '.dd.dd...'],
    'shot': ['..hm.....', '.hmmm....', '.lsso..f.', '..lldddfr', '.lmm...f.', '.lmm.....', '..ll.....', '..l.l....', '.dd.dd...'],
    'hurt': ['...hm..', '..hmmm.', '..lsso.', '...ll..', '..lmm..', '.dlmm..', '...ll..', '..l..l.', '.dd..dd'],
    'down': ['.........', '.........', '.........', '.........', '.........', '.........', '.........', 'dlllmmshh', '.d.l.mmh.'],
}


def build_units():
    out = {}
    # 兵：格子 12×12，脚点 (5, 11)
    sh = C.Sheet('badco_soldier', '坏公司·步兵', (12, 12), (5, 11))
    sp = lambda k: cell(grid(SOLDIER[k], PAL), 12, 12, 5, 11, 3, 8)
    sh.add('idle', [sp('idle0'), sp('idle1')], 3, 'loop')
    sh.add('walk', [sp('walk0'), sp('walk1')], 8, 'loop')
    sh.add('aim', [sp('aim')], 1, 'static')
    sh.add('fire', [sp('shot'), sp('aim')], 12, 'oneshot')
    sh.add('hurt', [sp('hurt')], 1, 'static')
    sh.add('down', [sp('down')], 1, 'static')
    out['badco_soldier'] = save_small(sh, {'cmd': 'aim', 'attack': 'fire', 'run': 'walk', 'talk': 'idle', 'guard': 'idle', 'dodge': 'walk',
                                          'shock': 'hurt', 'pose': 'idle'}, bodyW=3, top=9)
    # 坦克：格子 22×12，脚点 (10, 11)
    T0 = ['......hhm.......', '.....lmmmm......', '....lmmmmmdddddd', '..hhhhhhhhhh....', '.lmmmmmmmmmml...', 'oddgdgdgdgdgddo.', '.odgdgdgdgdgdo..']
    T1 = ['......hhm.......', '.....lmmmm.....f', '....lmmmmmddddrf', '..hhhhhhhhhh...f', '.lmmmmmmmmmml...', 'odgdgdgdgdgdgdo.', '.ogdgdgdgdgdgo..']
    TU = ['......hhm.......', '.....lmmmm..dd..', '....lmmmmmdd....', '..hhhhhhhhhh....', '.lmmmmmmmmmml...', 'oddgdgdgdgdgddo.', '.odgdgdgdgdgdo..']
    tk = lambda r: cell(grid(r, PAL), 22, 12, 10, 11, 7, 6)
    sh = C.Sheet('badco_tank', '坏公司·坦克', (22, 12), (10, 11))
    sh.add('idle', [tk(T0), tk([r.replace('dg', 'gd') for r in T0])], 4, 'loop')
    sh.add('aim', [tk(TU)], 1, 'static')
    sh.add('fire', [tk(T1), tk(T0)], 10, 'oneshot')
    sh.add('hurt', [tk([r.replace('m', 'l') for r in T0])], 1, 'static')
    sh.add('down', [tk(['................', '................', '.......ddd......', '..dlldlldldl....', '.ldlmdmmdmdl....', 'oddgdgdgdgdgddo.', '.odgdgdgdgdgdo..'])], 1, 'static')
    out['badco_tank'] = save_small(sh, {'cmd': 'aim', 'attack': 'fire', 'walk': 'idle', 'run': 'idle', 'talk': 'idle', 'shock': 'hurt'},
                                   bodyW=6, top=8)
    # 直升机（阿帕奇）：格子 24×12，悬停高度由战斗里的 z 管，脚点在机身下沿
    H0 = ['gggggggggggggggg...', '.......d..........', '..lmmmmmmhw.......', 'lmmmmmmmmmmhh.....', '.l..ldmmmmmmd.....', '.....d...d........']
    H1 = ['....gggggggg.......', '.......d..........', '..lmmmmmmhw.......', 'lmmmmmmmmmmhh.....', '.l..ldmmmmmmd.....', '.....d...d........']
    HF = ['gggggggggggggggg...', '.......d..........', '..lmmmmmmhw.......', 'lmmmmmmmmmmhh.....', '.l..ldmmmmmmdfr...', '.....d...d....f...']
    hc = lambda r: cell(grid(r, PAL), 24, 12, 11, 10, 8, 5)
    sh = C.Sheet('badco_heli', '坏公司·直升机', (24, 12), (11, 10))
    sh.add('idle', [hc(H0), hc(H1)], 14, 'loop')
    sh.add('aim', [hc(H0), hc(H1)], 14, 'loop')
    sh.add('fire', [hc(HF), hc(H1)], 12, 'oneshot')
    sh.add('hurt', [hc([r.replace('m', 'l') for r in H0])], 1, 'static')
    sh.add('down', [hc(['...................', '...................', '...................', '..dlldllldd........', 'ldldmdmdmdldd......', '.d..ldmdmdd.d......'])], 1, 'static')
    out['badco_heli'] = save_small(sh, {'cmd': 'aim', 'attack': 'fire', 'walk': 'idle', 'run': 'idle', 'talk': 'idle', 'shock': 'hurt'},
                                   bodyW=6, top=7)
    return out


def save_small(sh, amap, bodyW=3, top=None, kind='char'):
    """游戏尺寸的图集直接存（不经 shrink）"""
    full = sh.image()
    out = os.path.join(L.ASSETS, 'chars', sh.cid + '.png')
    L.ensure(out)
    full.save(out)
    anims = sh.anims()
    if top is None:
        bb = full.crop((0, 0, sh.cell[0], sh.cell[1])).getbbox() or (0, 0, 0, 0)
        top = sh.pivot[1] - bb[1]
    return dict(name=sh.name, image='chars/' + sh.cid, cell=list(sh.cell), pivot=list(sh.pivot), animations=anims, aliases={}, heads={},
                headAlias={}, headSize={}, k=1.0, amap={k: v for k, v in amap.items() if v in anims}, top=int(top), bodyW=bodyW, kind=kind)


# ============================================================ 虹村家的父亲：只给剪影（深绿的轮廓 + 一点边光 + 脖子上的链子）
def dad_frame(t=0, hug=False):
    w, h = 30, 28
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    body = ((xx - 14) / 10.5) ** 2 + ((yy - 17) / 9.0) ** 2 <= 1                    # 圆滚滚的背
    head = ((xx - (20 + t)) / 5.2) ** 2 + ((yy - 8.5) / 4.8) ** 2 <= 1              # 往前探的头
    mohawk = (np.abs(xx - (19 + t)) <= 1.2) & (yy >= 2.5) & (yy <= 5.5)
    legs = ((xx >= 8) & (xx <= 11) | (xx >= 16) & (xx <= 19)) & (yy >= 24) & (yy <= 27)
    if hug:
        arm = ((xx - 21) / 4.5) ** 2 + ((yy - 17) / 3.0) ** 2 <= 1
    else:
        arm = ((xx - (23 + 2 * t)) / 4.0) ** 2 + ((yy - (19 - 2 * t)) / 2.2) ** 2 <= 1
    m = body | head | mohawk | legs | arm
    a = np.zeros((h, w, 4), np.uint8)
    a[m] = (18, 34, 24, 255)
    # 边光：左上方向的一圈亮绿（窗口的光照到背上）
    up = np.zeros_like(m)
    up[1:, :] = m[:-1, :]
    lf = np.zeros_like(m)
    lf[:, 1:] = m[:, :-1]
    rim = m & (~up | ~lf) & (yy < 18)
    a[rim] = (64, 110, 70, 255)
    # 两只发黄的眼睛（不画五官）
    ey = 8
    a[ey, int(21 + t)] = (220, 210, 120, 255)
    a[ey, int(23 + t)] = (220, 210, 120, 255)
    # 链子：脖子到地上
    for i in range(10):
        x, y = int(15 - i * 1.3), int(12 + i * 1.5)
        if 0 <= x < w and 0 <= y < h and not m[y, x]:
            a[y, x] = (90, 90, 98, 255) if i % 2 else (130, 130, 140, 255)
    img = Image.fromarray(a, 'RGBA')
    return L.outline(img, (8, 12, 10, 255))


def build_dad():
    sh = C.Sheet('nijimura_dad', '虹村兄弟的父亲', (32, 30), (15, 29))
    sh.add('idle', [dad_frame(0), dad_frame(1)], 3, 'loop')
    sh.add('hug', [dad_frame(0, True)], 1, 'static')
    return save_small(sh, {'talk': 'idle', 'walk': 'idle', 'shock': 'idle', 'hurt': 'idle', 'pose': 'hug'}, bodyW=8, top=27)


# ============================================================ 说话人 / 替身表（格式照 p4_cast.py）
SPEAKERS = {
    'keicho': dict(short='形兆', nameColor='#c0a040', blipHz=420),
    'nijimura_dad': dict(short='？？？', nameColor='#5a8a5a', blipHz=300),
    'rhcp': dict(short='电线里的声音', nameColor='#e0c040', blipHz=900),
}
STANDS = {
    'badcompany': dict(cn='坏公司', en='BAD COMPANY', owner='keicho', aura='#b0c070', card='#c8d890', ghost='#e0ecc0',
                       impact='green', kind='object', idle={'dx': 0, 'z': 0}, link=None, summonSfx=None, fist=False),
}


def main(ids):
    path = os.path.join(L.META, 'chars_ch1.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    want = set(ids)
    if not want or 'keicho' in want:
        meta['chars']['keicho'] = build_keicho()
    if not want or want & {'badco', 'badco_soldier', 'badco_tank', 'badco_heli'}:
        meta['chars'].update(build_units())
    if not want or 'nijimura_dad' in want:
        meta['chars']['nijimura_dad'] = build_dad()
    meta['speakers'] = SPEAKERS
    meta['stands'] = STANDS
    L.save_json(path, meta)
    for cid, c in meta['chars'].items():
        print('角色', cid, c['cell'], '动作', list(c['animations']))


if __name__ == '__main__':
    main(sys.argv[1:])
