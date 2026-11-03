# 第四部第2章的新角色、替身和道具（第四部/docs/第2章_开发脚本.md 第四节素材清单）。
#   亿泰 / 轰炸空间、回音的蛋第1章也要用：按分章开发约定第 5 节，后面几章反复出现的人由第2章画，第1章直接借用。
#   画法和序章一样：拿第三部的全尺寸图集改发型、换配色（p4_chars 里的工具），再用第三部 shrink.py 缩成游戏尺寸；
#   配色照 TV 动画第四部（用户认定的“官方形象”，见 p4_chars 开头的说明和 PR #6）。
#   只写自己的元数据文件：_meta/chars_ch2.json、props_ch2.json、ui_ch2.json（build_p4.py 自动合并），不动 chars.json。
#   用法：python3 第四部/tools/art/p4_chars_ch2.py [okuyasu thehand echoes_egg …]   不写 = 全部
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402
import p4_heads as HD  # noqa: E402
import p4_props as PR  # noqa: E402
import p4_ui as UI  # noqa: E402

O = C.O
SK, SK2 = (246, 196, 154), (216, 148, 108)
NAVY_L, NAVY, NAVY_M, NAVY_D, NAVY_X = (84, 98, 168), (43, 49, 96), (48, 48, 78), (24, 26, 56), (28, 28, 52)
SHIRT, SHIRT_D = (74, 63, 102), (51, 42, 74)
BROWN, BROWN_D = (138, 90, 52), (90, 54, 30)
GOLD, GOLD_D = (255, 216, 60), (200, 154, 32)
TEAL_EYE = (44, 196, 168)


def mgrid(h, w):
    yy, xx = np.mgrid[0:h, 0:w]
    return yy.astype(float), xx.astype(float)


def seg_mask(h, w, p0, p1, r0, r1):
    """从 p0 到 p1 的一根尖刺：粗细从 r0 收到 r1（像素），返回 bool 蒙版"""
    yy, xx = mgrid(h, w)
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    ll = dx * dx + dy * dy or 1.0
    t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / ll, 0, 1)
    d = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
    return d <= r0 + (r1 - r0) * t


# ============================================================ 虹村亿泰：承太郎的骨架 + 短发、蓝色双排扣校服
# 动画：黑发，前面一小撮往上翘，两侧和后脑剃得短（发青灰），后颈两小撮尖尾巴；灰眼，皮肤比仗助黑一点；
#   蓝色双排扣长校服，金扣金饰，领口左 $ 右 ¥；里面紫衬衫；绿腰带；深绿鞋
OKU_SKIN = {SK: (236, 182, 140), SK2: (204, 138, 100)}
OKU_EYE = (118, 122, 136)
OKU_COAT = {NAVY_L: (104, 146, 228), NAVY: (54, 94, 190), NAVY_M: (40, 70, 148), NAVY_D: (28, 46, 110), NAVY_X: (20, 32, 80)}
OKU_SHIRT = {SHIRT: (134, 80, 164), SHIRT_D: (92, 52, 118)}
OKU_BELT = ((172, 220, 70), (110, 156, 40))
OKU_SHOE = ((56, 104, 66), (32, 64, 40))
# 头发：K 最暗 / k 暗 / h 中 / H 亮（顶上那撮是黑的）；G / g 是剃短的两侧和后脑（动画色板“黑发、两侧灰”；太亮了像戴了顶灰帽子）
OKH = dict(K=(14, 14, 18), k=(30, 30, 38), h=(52, 52, 64), H=(88, 88, 106), G=(70, 74, 90), g=(92, 98, 116))


def oku_hair_mask(w, h, fx0, fy0, fx1, fy1, s=1.0):
    """亿泰的头发形状（朝右）。返回 (mask, shade)，shade 是 OKH 的键"""
    yy, xx = mgrid(h, w)
    cx, cy = fx0 + 2.6 * s, fy0 - 0.4 * s
    skull = ((xx - cx) / (7.6 * s)) ** 2 + ((yy - cy) / (5.4 * s)) ** 2 <= 1
    skull &= yy <= fy0 + 0.5 * s
    # 前面那撮：比仗助的飞机头小得多，往前上翘
    px, py = fx1 - 2.2 * s, fy0 - 3.4 * s
    ang = np.deg2rad(-22)
    u = ((xx - px) * np.cos(ang) + (yy - py) * np.sin(ang)) / (5.4 * s)
    v = (-(xx - px) * np.sin(ang) + (yy - py) * np.cos(ang)) / (2.9 * s)
    tuft = u * u + v * v <= 1
    # 后脑和后颈：剃短，贴着头
    back = (xx >= fx0 - 4.6 * s) & (xx <= fx0 + 1.5 * s) & (yy >= fy0 - 1) & (yy <= fy1 - 3.0 * s)
    back &= ((xx - (fx0 - 1.2 * s)) / (4.2 * s)) ** 2 + ((yy - (fy0 + 0.5 * s)) / (fy1 - fy0 + 1.0)) ** 2 <= 1
    # 后颈两小撮尖尾巴
    tails = (seg_mask(h, w, (fx0 - 2.8 * s, fy1 - 5.4 * s), (fx0 - 6.2 * s, fy1 - 1.6 * s), 1.2 * s, 0.35 * s)
             | seg_mask(h, w, (fx0 - 1.2 * s, fy1 - 4.2 * s), (fx0 - 3.8 * s, fy1 - 0.2 * s), 1.1 * s, 0.35 * s))
    side = (xx >= fx0 + 0.5 * s) & (xx <= fx0 + 2.8 * s) & (yy >= fy0 - 0.5) & (yy <= fy0 + 2.6 * s)
    mask = skull | tuft | back | tails | side
    shade = np.full((h, w), 'h', object)
    up = np.zeros_like(mask)
    up[1:, :] = mask[:-1, :]
    rim = mask & ~up
    shade[rim] = 'H'
    shade[tuft & (v < -0.35)] = 'H'
    shade[tuft & (v > 0.45)] = 'k'
    # 剃短的地方：头顶往后、往下的那一圈和两侧
    shaved = (skull | back | side) & ~tuft & ((xx < fx0 + 1.8 * s) | (yy > fy0 - 1.6 * s))
    shade[shaved] = 'G'
    shade[shaved & ((xx < fx0 - 1.0 * s) & (yy < fy0 + 1.5 * s))] = 'g'
    shade[tails] = 'k'
    return mask, shade


def okuyasu_head(img, s=1.0, top_rows=24):
    fb = C.face_box(img, top_rows)
    if not fb:
        return img
    fx0, fy0, fx1, fy1 = fb
    a = np.array(img.convert('RGBA'))
    h, w = a.shape[:2]
    # 1) 挖掉承太郎的帽子和长发（要在换校服颜色之前做：按原来的藏青色找）
    box = (int(fx0 - 13 * s), 0, int(fx1 + 4 * s), fy1 + 1)
    old = C.comp(img, C.NAVY + C.GOLD + [O], box)
    yy, xx = mgrid(h, w)
    old &= ~((xx > fx1) & (yy > fy0))
    a[old] = (0, 0, 0, 0)
    # 2) 画头发
    mask, shade = oku_hair_mask(w, h, fx0, fy0, fx1, fy1, s)
    skin = C.comp(Image.fromarray(a, 'RGBA'), C.SKIN + C.EYES)
    mask &= ~(skin & (yy >= fy0))
    for k, c in OKH.items():
        a[mask & (shade == k)] = (*c, 255)
    img2 = C.reoutline(Image.fromarray(a, 'RGBA'))
    b = np.array(img2)
    face = C.comp(img2, C.SKIN + C.EYES)
    below = np.zeros_like(mask)
    below[1:, :] = mask[:-1, :]
    edge = face & below & (yy == fy0) & (xx < fx0 + (fx1 - fx0) * 0.45)
    b[edge] = (*O, 255)
    return Image.fromarray(b, 'RGBA')


def oku_body(f, collar=True):
    fb = C.face_box(f)
    f = okuyasu_head(f)
    bb = f.getbbox()
    f = C.recolor(f, OKU_COAT)
    f = C.recolor(f, OKU_SHIRT)
    f = C.recolor(f, OKU_SKIN)
    f = C.recolor(f, {TEAL_EYE: OKU_EYE})
    if bb:
        # 腰带和鞋都是承太郎的棕色：脚下 7 行算鞋，再往上算腰带
        foot = bb[3] - 7
        f = C.recolor(f, {BROWN: OKU_SHOE[0], BROWN_D: OKU_SHOE[1]}, (0, foot, f.width, f.height))
        f = C.recolor(f, {BROWN: OKU_BELT[0], BROWN_D: OKU_BELT[1]}, (0, 0, f.width, foot))
    if fb and collar:
        fx0, fy0, fx1, fy1 = fb
        # 承太郎领口的金链子去掉，换成领口两颗金徽章（$ ¥ 缩到这么小只剩金点）和胸口一块金色的 $
        box = (fx0, fy1 + 1, fx1 + 4, fy1 + 12)
        f = C.recolor(f, {GOLD: OKU_COAT[NAVY], GOLD_D: OKU_COAT[NAVY_D]}, box)
        f = C.put(f, [(fx0 + 1, fy1 + 2), (fx1, fy1 + 2)], GOLD)
        f = C.put(f, [(fx1 - 2, fy1 + 6), (fx1 - 1, fy1 + 6), (fx1 - 2, fy1 + 7)], GOLD)
        f = C.put(f, [(fx1 - 1, fy1 + 7)], GOLD_D)
    return f


def dizzy(frs):
    """晕：shock 那一帧左右各晃 1 px"""
    out = []
    for dx in (-1, 1):
        c = Image.new('RGBA', frs[0].size, (0, 0, 0, 0))
        c.alpha_composite(frs[0], (max(0, dx), 0)) if dx > 0 else c.paste(frs[0], (dx, 0), frs[0])
        out.append(c)
    return out


def build_okuyasu():
    im, m = C.base('jotaro')
    sh = C.Sheet('okuyasu', '虹村亿泰', m['cell'], m['pivot'])
    for anim, fps, kind in [('idle', 2, 'loop'), ('walk', 8, 'loop'), ('run', 10, 'loop'), ('point', 4, 'loop'), ('pose', 3, 'oneshot'),
                            ('shock', 1, 'static'), ('hurt', 1, 'static'), ('dodge', 1, 'static'), ('guard', 1, 'static'),
                            ('kick', 8, 'oneshot'), ('sit', 1.5, 'loop')]:
        sh.add(anim, [oku_body(f) for f in C.frames('jotaro', anim)], fps, kind)
    sh.add('dizzy', dizzy([oku_body(f) for f in C.frames('jotaro', 'shock')]), 4, 'loop')
    down = []
    for f in C.frames('jotaro', 'down'):
        r = f.rotate(-90, expand=True)
        r = okuyasu_head(r, top_rows=30)
        r = r.rotate(90, expand=True).crop((0, 0, f.width, f.height))
        r = C.recolor(C.recolor(C.recolor(r, OKU_COAT), OKU_SHIRT), OKU_SKIN)
        down.append(C.recolor(r, {BROWN: OKU_SHOE[0], BROWN_D: OKU_SHOE[1], TEAL_EYE: OKU_EYE}))
    sh.add('down', down, 1, 'static')
    sh.heads = okuyasu_heads()
    return C.save(sh, amap=dict(C.AMAP_HUMAN, kick='kick', sit='sit', run='run', dizzy='dizzy'), bodyW=4)


# ---------------------------------------------------------------- 亿泰的头像（32×32）：承太郎的头像去帽子，换短发
def okuyasu_portrait(f, angry=False):
    D = 2
    a0 = np.array(f.convert('RGBA'))
    a = np.zeros_like(a0)
    a[D:, :] = a0[:-D, :]
    H, W = a.shape[:2]
    yy, xx = mgrid(H, W)
    col = lambda c: (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
    head_rows = yy < 10 + D + 4
    for c in (NAVY, NAVY_L, NAVY_D):
        a[col(c) & head_rows] = 0
    a[col(NAVY_D)] = 0
    a[col(O) & (yy < 10 + D)] = 0
    a[col(O) & (xx < 9) & (yy < 21 + D)] = 0
    a[col(SK2) & (yy == 10 + D) & (xx > 10)] = (*SK, 255)          # 帽檐压在额头上的阴影
    a[col(TEAL_EYE)] = (*OKU_EYE, 255)
    for c in (GOLD, GOLD_D):                                         # 帽徽的金色（不去掉会在头发右上角留一颗金点）
        a[col(c) & (yy < 12 + D)] = 0
    # 头发：头顶一圈 + 前面一撮往上翘 + 剃短的两侧和后脑 + 后颈两小撮尖尾巴
    skull = ((xx - 11.5) / 10.2) ** 2 + ((yy - (8.6 + D)) / 7.6) ** 2 <= 1
    skull &= ~((yy > 10 + D - 1) & (xx > 11.5))
    skull &= yy <= 18.5 + D
    ang = np.deg2rad(-20)
    cx, cy = 20.5, 4.6 + D
    u = ((xx - cx) * np.cos(ang) + (yy - cy) * np.sin(ang)) / 7.6
    v = (-(xx - cx) * np.sin(ang) + (yy - cy) * np.cos(ang)) / 3.6
    tuft = u * u + v * v <= 1
    # 后颈两小撮尖尾巴（jojowiki：“two spiked rattails in the back”）：短一点、用中间色，不然像披着长发
    tails = seg_mask(H, W, (4.6, 15.6 + D), (2.2, 18.6 + D), 1.1, 0.35) | seg_mask(H, W, (6.6, 16.8 + D), (5.0, 20.0 + D), 1.0, 0.35)
    side = (xx >= 8) & (xx <= 11) & (yy >= 10 + D) & (yy <= 13 + D)
    hair = skull | tuft | tails | side
    face = col(SK) | col(SK2) | col((239, 230, 210)) | col(OKU_EYE) | col((255, 255, 255)) | col((110, 62, 36)) | col((144, 24, 40))
    lash = col(O) & (yy >= 10 + D) & (yy <= 13 + D) & (xx >= 13)
    hair &= ~(face & (yy >= 10 + D)) & ~lash
    shade = np.full((H, W), 'h', object)
    shade[tuft & (v < -0.4)] = 'H'
    shade[tuft & (v > 0.5)] = 'k'
    top = ((xx - 11.5) / 10.2) ** 2 + ((yy - (8.6 + D)) / 7.6) ** 2
    shade[skull & ~tuft & (top > 0.72) & (yy < 6 + D)] = 'H'
    shaved = (skull | side) & ~tuft & ((xx < 9.5) | (yy > 7.5 + D))
    shade[shaved] = 'G'
    shade[shaved & (xx < 5.5)] = 'g'
    shade[tails] = 'h'
    for k, c in OKH.items():
        a[hair & (shade == k)] = (*c, 255)
    img = C.reoutline(Image.fromarray(a, 'RGBA'))
    b = np.array(img)
    edge = np.zeros_like(hair)
    edge[1:, :] = hair[:-1, :] & ~hair[1:, :]
    fc = (b[..., 0] == SK[0]) & (b[..., 1] == SK[1]) & (b[..., 2] == SK[2])
    b[edge & fc & (yy <= 10 + D)] = (*O, 255)
    if not angry:
        # 粗短的眉毛，比仗助的往上挑一点（大大咧咧）
        for x in range(14, 19):
            b[10 + D - (1 if x == 18 else 0), x] = (*O, 255)
        for x in range(23, 28):
            b[10 + D - (1 if x == 23 else 0), x] = (*O, 255)
    img = Image.fromarray(b, 'RGBA')
    # 领口：金链去掉，左右两颗金徽章（$ ¥）
    img = C.recolor(img, {GOLD: OKU_COAT[NAVY], GOLD_D: OKU_COAT[NAVY_D]}, (20, 22, 32, 32))
    img = C.recolor(img, OKU_COAT)
    img = C.recolor(img, OKU_SHIRT)
    img = C.recolor(img, OKU_SKIN)
    img = C.put(img, [(13, 27), (14, 27), (26, 27), (27, 27)], GOLD)
    img = C.put(img, [(13, 28), (27, 28)], GOLD_D)
    return img


def okuyasu_heads():
    hd = C.heads('jotaro')
    nm = [okuyasu_portrait(f) for f in hd['portrait']]
    rg = [okuyasu_portrait(f, angry=True) for f in hd['portrait_angry']]
    sk = OKU_SKIN[SK]

    def smile(f):
        y = 18 + 2
        pix = {(x, y): sk for x in range(17, 23)}
        pix.update({(18, y): (138, 90, 52), (19, y): (138, 90, 52), (20, y): (138, 90, 52), (21, y): (138, 90, 52),
                    (17, y - 1): (138, 90, 52), (22, y - 1): (138, 90, 52)})
        return HD.edit(f, pix)

    def shock(f, i):
        a = np.array(f.convert('RGBA'))
        eye = (a[..., 0] == OKU_EYE[0]) & (a[..., 1] == OKU_EYE[1]) & (a[..., 2] == OKU_EYE[2])
        a[eye] = (255, 255, 255, 255)
        img = Image.fromarray(a, 'RGBA')
        y = 19 + 2
        return HD.edit(img, {(19, y): O, (20, y): O, (19, y + 1): (120, 24, 40) if i else O, (20, y + 1): O})
    return {'normal': nm, 'rage': rg, 'smile': [smile(f) for f in nm], 'shock': [shock(f, i) for i, f in enumerate(nm)]}


# ============================================================ 轰炸空间：白金之星的骨架，照动画配色
# 动画（官方设定的 TV 配色）：白色身体、蓝色护甲（护肩带金刺、腰甲）、头是机器人一样的头盔，脸两边像马的眼罩，黄眼睛；
#   金手镯、金护膝，领子两头是 $ 和 ¥。没有头发、没有围巾：白金之星的长发剪成贴头的头盔，飘在身后的围巾剪掉
TH_BODY = {'#bab2ff': '#ffffff', '#8a80ec': '#e4e6f2', '#5242ae': '#a8aecb', '#33257a': '#626a92', '#b69ec6': '#d6d8e8'}
TH_HELM = {'#5a56a0': '#78a6ff', '#2c2852': '#3462d0', '#17132e': '#1c3588'}
TH_ARMOR = {'#ff8a78': '#8cb6ff', '#ec3040': '#3c70e2', '#98182c': '#22439e'}
TH_EYE = {'#40f0e0': '#fff27a'}


def _cols(a, hexes):
    m = np.zeros(a.shape[:2], bool)
    for hx in hexes:
        c = C.rgb(hx)
        m |= (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
    return m


def thehand_frame(f, top_rows=22):
    """一帧白金之星 → 轰炸空间：换色，再把头发剪成头盔、把飘在身后的围巾剪掉"""
    g = C.recolor(f, TH_BODY)
    g = C.recolor(g, TH_HELM)
    g = C.recolor(g, TH_ARMOR)
    g = C.recolor(g, TH_EYE)
    a = np.array(g)
    bb = g.getbbox()
    if not bb:
        return g
    body = _cols(a, TH_BODY.values()) | _cols(a, TH_EYE.values())
    yy, xx = mgrid(*a.shape[:2])
    # 头：包围盒顶上 top_rows 行里的身体色（脸）
    head = body & (yy < bb[1] + top_rows)
    if head.any():
        hy, hx = np.where(head)
        hx0, hx1, hy0 = hx.min(), hx.max(), hy.min()
        helm = _cols(a, TH_HELM.values())
        keep = (xx >= hx0 - 3) & (xx <= hx1 + 2) & (yy >= hy0 - 4)
        a[helm & ~keep] = 0
    # 围巾：每一行只留身体最左边那一列往右的（领子、腰甲），身后飘着的剪掉
    armor = _cols(a, TH_ARMOR.values())
    left = np.full(a.shape[0], 10 ** 6)
    for y in range(a.shape[0]):
        xs = np.where(body[y])[0]
        if xs.size:
            left[y] = xs.min()
    a[armor & (xx < left[:, None] - 1)] = 0
    g = C.strip_outline(Image.fromarray(a, 'RGBA'))
    return C.reoutline(C.strip_outline(g))


def build_thehand():
    _, m = C.base('starplat')
    sh = C.Sheet('thehand', '轰炸空间', m['cell'], m['pivot'])
    fr = {anim: [thehand_frame(f) for f in C.frames('starplat', anim)]
          for anim in m['animations'] if not anim.startswith('portrait')}
    for anim, frs in fr.items():
        a = m['animations'][anim]
        sh.add(anim, frs, a.get('fps', 6), a.get('kind', 'loop'))
    # 削：右手往后收 → 张开手掌一抹 → 收回（设计文档 3.3「右手掌一抹」）；拉近：一抹再往回带
    sh.add('erase', [fr['punch'][0], fr['reach'][0], fr['punch'][1]], 12, 'oneshot')
    sh.add('pull', [fr['reach'][0], fr['punch'][0]], 10, 'oneshot')
    hd = C.heads('starplat')
    sh.heads = {'normal': [thehand_frame(f, top_rows=20) for f in hd['portrait']]}
    e = C.save(sh, amap={'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'erase', 'rush': 'rush', 'block': 'block',
                         'hurt': 'hurt', 'special': 'erase', 'finger': 'finger', 'swipe': 'erase'}, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 回音 ACT1（程序画，全尺寸再缩小，和水中项链一样）
# 动画配色（jojowiki 的 TV 色板）：三节的“外星幼虫”。大头上盖着祖母绿的壳，壳顶一根金刺；脸几乎被金色眼罩盖住，只露出一个小尖嘴；
#   头下两只带壳的小手；第二节是带壳的身子、黑肚皮；第三节底下一对小轮子，拖一条长尾巴：背上浅绿带黑色涡纹、内侧乌黑，尾巴尖是金色的响铃
EC = dict(o=(20, 26, 22), sh=(34, 168, 110), sH=(98, 220, 160), sd=(18, 104, 70), b=(178, 236, 150), bl=(222, 252, 200),
          bd=(120, 186, 104), k=(26, 28, 30), kk=(46, 50, 54), y=(255, 214, 72), yd=(196, 146, 34), yl=(255, 246, 170))
EGG = dict(w=(246, 242, 226), l=(255, 255, 248), m=(222, 214, 190), d=(176, 164, 136), g=(40, 160, 104), G=(20, 100, 64))


def _ell(xx, yy, cx, cy, rx, ry):
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1


def _thick(h, w, pts, r0, r1):
    m = np.zeros((h, w), bool)
    n = len(pts) - 1
    for i in range(n):
        a0 = r0 + (r1 - r0) * i / n
        a1 = r0 + (r1 - r0) * (i + 1) / n
        m |= seg_mask(h, w, pts[i], pts[i + 1], a0, a1)
    return m


def _bez(p0, p1, p2, n=10):
    out = []
    for i in range(n + 1):
        u = i / n
        out.append(((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
                    (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]))
    return out


def echoes1_frame(t=0.0, flick=0.0, curl=0.0, w=60, h=46, rise=0.0):
    """t：漂浮相位（0–1）；flick：尾巴甩到头顶往前射字（0–1）；curl：缩成一团挡（0–1）；rise：整体往下沉多少（孵化时从蛋里钻出来用）"""
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = mgrid(h, w)
    bob = np.sin(t * 2 * np.pi) * 1.2
    hx, hy = 38 - 3 * curl, 15 + bob + rise + 4 * curl
    head = _ell(xx, yy, hx, hy, 9.5 - curl, 8.2 - curl * 0.6)
    torso = _ell(xx, yy, hx - 9, hy + 10, 6.2, 5.0)
    seg3 = _ell(xx, yy, hx - 17 + 5 * curl, hy + 14, 5.4, 4.2)
    # 尾巴：从第三节后面起，平时往后再往上卷；flick 时甩过头顶指向前方；curl 时绕到身子前面
    t0 = (hx - 21 + 5 * curl, hy + 12)
    sway = np.sin(t * 2 * np.pi + 1.2) * 1.5
    end_rest, ctrl_rest = (hx - 30 + sway, hy - 9), (hx - 36, hy + 8)
    end_fl, ctrl_fl = (hx + 8, hy - 15), (hx - 26, hy - 26)
    end_cu, ctrl_cu = (hx + 4, hy + 18), (hx - 26, hy + 26)
    def lerp(p, q, u):
        return (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
    end = lerp(lerp(end_rest, end_fl, flick), end_cu, curl)
    ctrl = lerp(lerp(ctrl_rest, ctrl_fl, flick), ctrl_cu, curl)
    pts = _bez(t0, ctrl, end, 12)
    tail = _thick(h, w, pts, 2.8, 1.3)
    rattle = _ell(xx, yy, end[0], end[1], 2.6, 2.6)
    arms = _ell(xx, yy, hx + 3, hy + 8.5, 2.0, 2.8) | _ell(xx, yy, hx - 2.5, hy + 9.5, 1.8, 2.6)
    wheels = [(hx - 20 + 5 * curl, hy + 18.2), (hx - 14 + 5 * curl, hy + 18.2)]
    wh = np.zeros((h, w), bool)
    for wx, wy in wheels:
        wh |= _ell(xx, yy, wx, wy, 1.9, 1.9)
    spike = seg_mask(h, w, (hx - 1.5, hy - 6.5), (hx - 3.5, hy - 12.5), 1.6, 0.3)
    beak = seg_mask(h, w, (hx + 7.5, hy + 2.2), (hx + 11.5, hy + 3.4), 1.3, 0.3)
    body = head | torso | seg3 | tail | rattle | arms | wh | spike | beak
    put = lambda m, c: a.__setitem__(m, (*c, 255))
    # 尾巴、第三节：背上浅绿，内侧乌黑
    put(tail, EC['b'])
    under = np.zeros((h, w), bool)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        nx, ny = -(y1 - y0), (x1 - x0)
        ln = np.hypot(nx, ny) or 1
        nx, ny = nx / ln, ny / ln
        if ny < 0:
            nx, ny = -nx, -ny
        under |= seg_mask(h, w, (x0 + nx * 1.4, y0 + ny * 1.4), (x1 + nx * 1.4, y1 + ny * 1.4), 1.0, 0.7)
    put(tail & under, EC['k'])
    put(seg3, EC['b'])
    put(seg3 & (yy > hy + 14.5), EC['k'])
    put(seg3 & (yy < hy + 12), EC['bl'])
    # 黑色涡纹点：尾巴背上几颗、第三节两颗
    for i in (3, 6, 9):
        sx, sy = pts[i]
        put(_ell(xx, yy, sx, sy - 0.6, 1.0, 0.9) & tail & ~under, EC['k'])
    put(_ell(xx, yy, hx - 18 + 5 * curl, hy + 12.5, 1.2, 1.0) & seg3, EC['k'])
    put(_ell(xx, yy, hx - 15 + 5 * curl, hy + 13.5, 0.9, 0.8) & seg3, EC['k'])
    put(wh, EC['kk'])
    # 第二节：祖母绿的壳 + 黑肚皮
    put(torso, EC['sh'])
    put(torso & (yy > hy + 11.5), EC['k'])
    put(torso & _ell(xx, yy, hx - 10.5, hy + 7.5, 3.0, 1.6), EC['sH'])
    # 头：壳盖在上半个头，脸前面一大片金色眼罩，只露小尖嘴
    put(head, EC['b'])
    shell = head & (yy < hy + 1.5 - (xx - hx) * 0.25)
    put(shell, EC['sh'])
    put(shell & _ell(xx, yy, hx - 2.5, hy - 4.5, 4.2, 2.2), EC['sH'])
    put(head & (yy > hy + 5.5), EC['bd'])
    visor = head & (xx > hx + 1.5) & (yy > hy - 3.5 + (xx - hx) * 0.1) & (yy < hy + 3.6)
    put(visor, EC['y'])
    put(visor & (yy > hy + 2.4), EC['yd'])
    put(visor & (yy < hy - 1.8), EC['yl'])
    put(spike, EC['y'])
    put(beak, EC['k'])
    put(arms, EC['sh'])
    put(arms & (yy > hy + 10), EC['sd'])
    put(rattle, EC['y'])
    put(rattle & _ell(xx, yy, end[0] + 0.8, end[1] + 0.8, 1.6, 1.6), EC['yd'])
    put(_ell(xx, yy, end[0] - 0.8, end[1] - 0.8, 0.9, 0.9) & rattle, EC['yl'])
    img = Image.fromarray(a, 'RGBA')
    return C.reoutline(img, EC['o'])


def egg_frame(crack=0, w=60, h=46, shards=None):
    """回音的蛋（全尺寸）：上半白、下半盖满祖母绿的涡纹。crack 0 完整 / 1 细裂纹 / 2 大裂缝 / 3 顶上碎开"""
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = mgrid(h, w)
    cx, cy, rx, ry = w / 2, h - 16, 11.5, 14.5
    egg = _ell(xx, yy, cx, cy, rx, ry) & ~((yy < cy) & ~_ell(xx, yy, cx, cy - 1, rx * 0.86, ry + 1))
    if crack >= 3:
        jag = cy - 3 + 2.2 * np.sin(xx * 1.7)
        egg &= yy > jag
    put = lambda m, c: a.__setitem__(m, (*c, 255))
    put(egg, EGG['w'])
    put(egg & _ell(xx, yy, cx - 4, cy - 7, 4.0, 5.0), EGG['l'])
    put(egg & (xx > cx + 5), EGG['m'])
    # 下半的涡纹：几个弯月形的斑
    rng = np.random.RandomState(7)
    for i in range(9):
        ang = rng.uniform(0, 2 * np.pi)
        sx, sy = cx + rng.uniform(-8.5, 8.5), cy + rng.uniform(1, 11)
        r = rng.uniform(1.8, 3.0)
        ring = _ell(xx, yy, sx, sy, r, r * 0.8) & ~_ell(xx, yy, sx + np.cos(ang) * 1.1, sy + np.sin(ang) * 0.9, r * 0.62, r * 0.5)
        put(egg & ring, EGG['g'] if i % 3 else EGG['G'])
    put(egg & (yy > cy + ry - 3), EGG['d'])
    if 1 <= crack <= 2:
        pts = [(cx - 6, cy - 6), (cx - 2, cy - 9), (cx + 1, cy - 5), (cx + 5, cy - 8)]
        if crack == 2:
            pts += [(cx + 8, cy - 4)]
        for p0, p1 in zip(pts, pts[1:]):
            a[seg_mask(h, w, p0, p1, 0.5, 0.5) & egg] = (*EC['o'], 255)
    if crack >= 3:
        rim = egg & ~np.roll(egg, -2, axis=0)
        put(rim & (yy < cy + 2), EGG['d'])
    img = Image.fromarray(a, 'RGBA')
    img = C.reoutline(img, EC['o'])
    if shards:
        d = np.array(img)
        for sx, sy in shards:
            m = _ell(xx, yy, sx, sy, 2.2, 1.6)
            d[m] = (*EGG['w'], 255)
        img = C.reoutline(Image.fromarray(d, 'RGBA'), EC['o'])
    return img


def build_echoes1():
    W, H = 60, 46
    sh = C.Sheet('echoes1', '回音 ACT1', (W, H), (W // 2, H - 2))
    sh.add('idle', [echoes1_frame(t / 4) for t in range(4)], 6, 'loop')
    sh.add('shoot', [echoes1_frame(0, 0.35), echoes1_frame(0, 1.0), echoes1_frame(0.25, 0.6)], 12, 'oneshot')
    sh.add('block', [echoes1_frame(0, 0, 1.0)], 1, 'static')
    sh.add('hurt', [echoes1_frame(0.5, 0, 0.5)], 1, 'static')
    # 孵化：蛋完整 → 裂纹 → 大裂缝 → 顶上碎开、头探出来 → 钻出来 → 浮起来，脚下留着半个蛋壳
    def over(base, top):
        c = base.copy()
        c.alpha_composite(top)
        return c
    def under(top, base):
        c = top.copy()
        c.alpha_composite(base)
        return c
    hatch = [egg_frame(0), egg_frame(1), egg_frame(2),
             under(echoes1_frame(0, 0, 0.6, rise=14), egg_frame(3, shards=[(W / 2 - 13, 16), (W / 2 + 12, 13)])),
             under(echoes1_frame(0.2, 0.2, 0, rise=7), egg_frame(3, shards=[(W / 2 - 17, 22), (W / 2 + 16, 19)])),
             over(egg_frame(3), echoes1_frame(0.4, 0, 0, rise=-2))]
    sh.add('hatch', hatch, 8, 'oneshot')
    big = echoes1_frame(0.1).resize((W * 2, H * 2), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((50, 2, 82, 34)))
    sh.heads = {'normal': [face]}
    e = C.save(sh, amap={'talk': 'idle', 'walk': 'idle', 'run': 'idle', 'cmd': 'shoot', 'punch': 'shoot', 'punch2': 'shoot',
                         'punch_heavy': 'shoot', 'cast': 'shoot', 'rush': 'shoot', 'special': 'shoot', 'guard': 'block',
                         'down': 'hurt', 'shock': 'hurt', 'reach': 'shoot'}, kind='stand', bodyW=4)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 元数据：队长、说话人、替身（build_p4.py 深合并进 heroes / speakers / stands）
# ============================================================ 小林玉美：波鲁那雷夫的骨架（捂头、哭、跪、爬、倒地这些动作现成），压矮，换发型和配色
# 动画配色（jojowiki 的 TV 配色表）：黑发带蓝灰高光，往前梳成一顶厚头盔似的飞机头；黑眼睛；皮肤白；
#   长春花色（淡蓝紫）的 POLO 衫，领尖和左胸是小国旗；棕色宽裤，黄皮鞋；耳钉；左嘴角下一道十字小疤。
#   动画里的玉美一直是矮个子（153 cm，和康一差不多高）：腿和身子各抽掉几行，头不动
POL_HAIR = ['#d6dcec', '#9098b6', '#f6f8ff', '#60688a']
TMH = dict(K=(10, 10, 16), k=(24, 26, 36), h=(46, 52, 72), H=(88, 102, 134), X=(140, 156, 188))
TM_SKIN = {'#f6c49a': '#f8d4b4', '#d8946c': '#dca486', '#d8a67e': '#e6b896'}
TM_TOP = {'#2a2632': '#8c96d8', '#4e4860': '#b4bcf0'}
TM_TOP_D = (96, 102, 170)
TM_COLLAR = (214, 220, 252)
TM_PANTS = {'#d8dcf2': '#98643e', '#9ea2cc': '#6c4228', '#9a9ab0': '#98643e', '#7a7eaa': '#6c4228'}
TM_SHOE = ((246, 206, 64), (194, 146, 30))
TM_BELT = (60, 38, 24)
TM_EYE = {'#3c78e0': '#1c1820'}
TM_EAR = {'#f05890': '#ffd83c'}
P_SKIN = [(246, 196, 154), (216, 148, 108), (216, 166, 126)]


def _hex(c):
    return C.rgb(c)


def _colmask(a, cols):
    m = np.zeros(a.shape[:2], bool)
    for c in cols:
        c = _hex(c)
        m |= (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
    return m


def _grow(m, r=1, diag=False):
    out = m.copy()
    for _ in range(r):
        n = out.copy()
        n[1:, :] |= out[:-1, :]
        n[:-1, :] |= out[1:, :]
        n[:, 1:] |= out[:, :-1]
        n[:, :-1] |= out[:, 1:]
        if diag:
            n[1:, 1:] |= out[:-1, :-1]
            n[1:, :-1] |= out[:-1, 1:]
            n[:-1, 1:] |= out[1:, :-1]
            n[:-1, :-1] |= out[1:, 1:]
        out = n
    return out


def tm_hair_mask(w, h, fx0, fy0, fx1, fy1, s=1.0):
    """玉美的头发（朝右）：一顶厚头盔，前面鼓出一大坨往前梳的飞机头。返回 (mask, shade)，shade 是 TMH 的键"""
    yy, xx = mgrid(h, w)
    cx, cy = fx0 + 2.6 * s, fy0 + 0.8 * s
    dome = ((xx - cx) / (8.2 * s)) ** 2 + ((yy - cy) / (6.6 * s)) ** 2 <= 1
    dome &= yy <= fy0 + 0.5 * s
    # 后脑：一直盖到耳朵下面，后沿圆
    bk = ((xx - (fx0 + 0.5 * s)) / (6.4 * s)) ** 2 + ((yy - (fy0 + 0.5 * s)) / ((fy1 - fy0) * 0.5)) ** 2 <= 1
    back = bk & (xx <= fx0 + 2.0 * s) & (yy >= fy0 - 1)
    # 鬓角：耳朵前面一小条
    side = (xx >= fx0 + 1.5 * s) & (xx <= fx0 + 2.6 * s) & (yy >= fy0) & (yy <= fy0 + 3.4 * s)
    # 前面的飞机头：一大坨往前、略往上鼓，前沿压在额头上方
    px, py = fx1 - 2.2 * s, fy0 - 3.6 * s
    ang = np.deg2rad(-16)
    u = ((xx - px) * np.cos(ang) + (yy - py) * np.sin(ang)) / (7.0 * s)
    v = (-(xx - px) * np.sin(ang) + (yy - py) * np.cos(ang)) / (4.7 * s)
    pomp = u * u + v * v <= 1
    mask = dome | back | side | pomp
    shade = np.full((h, w), 'k', object)
    up = np.zeros_like(mask)
    up[1:, :] = mask[:-1, :]
    rim = mask & ~up
    shade[rim] = 'h'
    # 高光：顺着头盔往后梳的两道蓝灰（前面那坨最亮）
    d_dome = ((xx - cx) / (8.2 * s)) ** 2 + ((yy - cy) / (6.6 * s)) ** 2
    shade[dome & ~pomp & (d_dome > 0.5) & (d_dome < 0.72) & (yy < cy - 2.5 * s)] = 'H'
    shade[dome & ~pomp & (d_dome > 0.25) & (d_dome < 0.36) & (yy < cy - 3.5 * s) & (xx > cx - 4 * s)] = 'h'
    shade[pomp & (v < -0.3) & (v > -0.8) & (u > -0.55)] = 'H'
    shade[pomp & (v < -0.45) & (v > -0.75) & (u > -0.05) & (u < 0.6)] = 'X'
    shade[pomp & (v > 0.45)] = 'K'
    shade[(back | side) & ~pomp & (yy > fy0 + 1.5 * s)] = 'K'
    shade[back & ~pomp & (yy <= fy0 + 1.5 * s) & (yy > fy0 - 2.5 * s) & (xx < fx0 - 1.5 * s)] = 'h'
    return mask, shade


def tm_face_box(img):
    """波鲁那雷夫的头发是一整块竖着的：按旧头发的包围盒推脸的位置（捂脸、哭的帧手和脸连成一块，按皮肤找会找偏）"""
    a = np.array(img.convert('RGBA'))
    m = _colmask(a, POL_HAIR)
    if m.sum() < 12:
        return None
    ys, xs = np.nonzero(m)
    hx0, hy0, hx1 = int(xs.min()), int(ys.min()), int(xs.max())
    return hx0 + 2, hy0 + 12, hx1 + 2, hy0 + 23


def tm_head(img, s=1.0, top_rows=24):
    fb = tm_face_box(img)
    if not fb:
        return img
    fx0, fy0, fx1, fy1 = fb
    a = np.array(img.convert('RGBA'))
    h, w = a.shape[:2]
    yy, xx = mgrid(h, w)
    old = _colmask(a, POL_HAIR)
    a[old] = 0
    # 旧头发的描边：只留挨着皮肤（脸、举到头上的手）和别的颜色的那些
    isO = _colmask(a, [O])
    body = (a[..., 3] > 0) & ~isO
    a[isO & ~_grow(body, 1) & (yy < fy1)] = 0
    mask, shade = tm_hair_mask(w, h, fx0, fy0, fx1, fy1, s)
    free = a[..., 3] == 0
    isO = _colmask(a, [O])
    skin = _colmask(a, P_SKIN)
    # 头发只画在空的地方和“只挨着旧头发”的描边上；手和脸不盖
    mask &= free | (isO & ~_grow(skin, 1))
    for k, c in TMH.items():
        a[mask & (shade == k)] = (*c, 255)
    img2 = C.reoutline(Image.fromarray(a, 'RGBA'))
    b = np.array(img2)
    face = _colmask(b, P_SKIN + [(60, 120, 224), (42, 30, 26)])
    below = np.zeros_like(mask)
    below[1:, :] = mask[:-1, :]
    edge = face & below & (yy <= fy0 + 1) & (xx < fx0 + (fx1 - fx0) * 0.5)
    b[edge] = (*O, 255)
    return Image.fromarray(b, 'RGBA')


def tm_clothes(f):
    """换配色、POLO 衫的短袖和领子；f 是已经换好头发的帧"""
    a = np.array(f.convert('RGBA'))
    h, w = a.shape[:2]
    yy, xx = mgrid(h, w)
    top = _colmask(a, list(TM_TOP))
    skin = _colmask(a, P_SKIN)
    if top.any():
        ty = int(np.nonzero(top)[0].min())
        tx = np.nonzero(top[ty])[0]
        # 脖子：衫最上面一行正上方的皮肤
        neck = skin & (yy < ty + 1) & (xx >= tx.min()) & (xx <= tx.max())
        # 短袖：贴着衫、在脖子以下的皮肤（胳膊根）
        sleeve = skin & _grow(top, 3, diag=True) & (yy >= ty) & (yy <= ty + 4) & ~neck
        # 袖子不往下拖太长：每个连通块只要离衫最近的 4 行
        a[sleeve] = (*_hex(TM_TOP['#2a2632']), 255)
        # 波鲁那雷夫的背心是露腰的：衫下摆到腰带之间露出来的那条肚皮补成衫
        tb = int(np.nonzero(top.any(1))[0].max())
        belt = _colmask(a, ['#8a5a34', '#ffd83c', '#c89a20']) & (yy > tb)
        if belt.any():
            by = int(np.nonzero(belt.any(1))[0].min())
            bx = np.nonzero(top[tb])[0]
            gap = skin & (yy > tb) & (yy < by) & (xx >= bx.min()) & (xx <= bx.max())
            a[gap] = (*_hex(TM_TOP['#2a2632']), 255)
            a[gap & (yy == by - 1)] = (*TM_TOP_D, 255)
        # 袖口一圈暗面
        cuff = sleeve & _grow(skin & ~sleeve, 1)
        a[cuff] = (*TM_TOP_D, 255)
        # 领子：脖子两边各翻出一个浅色领尖
        nx = np.nonzero(neck[ty - 1])[0] if ty > 0 else []
        if len(nx):
            x0, x1 = int(nx.min()), int(nx.max())
            for (x, y) in ((x0 - 1, ty), (x0 - 2, ty), (x0 - 1, ty + 1), (x1 + 1, ty), (x1 + 2, ty), (x1 + 1, ty + 1)):
                if 0 <= x < w and top[y, x]:
                    a[y, x] = (*TM_COLLAR, 255)
            # 领尖上的小国旗（右领瑞士：红底白点；左领荷兰：红白蓝）、门襟
            if top[ty + 1, x1 + 2] if x1 + 2 < w else False:
                a[ty + 1, x1 + 2] = (214, 40, 48, 255)
            if 0 <= x0 - 2 < w and top[ty + 1, x0 - 2]:
                a[ty + 1, x0 - 2] = (40, 64, 168, 255)
            cxn = (x0 + x1) // 2
            for y in (ty + 1, ty + 2):
                if top[y, cxn]:
                    a[y, cxn] = (*TM_TOP_D, 255)
    img = Image.fromarray(a, 'RGBA')
    img = C.recolor(img, TM_TOP)
    img = C.recolor(img, TM_PANTS)
    img = C.recolor(img, TM_EYE)
    img = C.recolor(img, TM_EAR)
    # 腰带和鞋都是 #8a5a34 / #5a361e：脚下 6 行算鞋
    bb = img.getbbox()
    if bb:
        foot = bb[3] - 6
        img = C.recolor(img, {'#5a361e': TM_SHOE[1], '#8a5a34': TM_SHOE[0]}, (0, foot, w, h))
        img = C.recolor(img, {'#8a5a34': TM_BELT, '#5a361e': TM_BELT}, (0, 0, w, foot))
    img = C.recolor(img, TM_SKIN)
    return img


def squash_rows(f, rows):
    """抽掉 rows 这些行，上面的整体往下挪（脚不动）"""
    a = np.array(f.convert('RGBA'))
    keep = [y for y in range(a.shape[0]) if y not in set(rows)]
    b = np.zeros_like(a)
    k = a[keep]
    b[a.shape[0] - len(keep):] = k
    return Image.fromarray(b, 'RGBA')


def squash_cols(f, cols):
    a = np.array(f.convert('RGBA'))
    keep = [x for x in range(a.shape[1]) if x not in set(cols)]
    b = np.zeros_like(a)
    b[:, :len(keep)] = a[:, keep]
    return Image.fromarray(b, 'RGBA')


def tm_squash(f):
    """站着的帧：裤子抽 4 行、上身抽 2 行"""
    a = np.array(f.convert('RGBA'))
    top = _colmask(a, ['#2a2632', '#4e4860'])
    pants = _colmask(a, ['#d8dcf2', '#9ea2cc', '#9a9ab0', '#7a7eaa'])
    rows = []
    if pants.any():
        py = np.nonzero(pants.any(1))[0]
        p0, p1 = int(py.min()) + 2, int(py.max()) - 2
        if p1 - p0 >= 8:
            rows += [int(round(p0 + (p1 - p0) * t)) for t in (0.15, 0.4, 0.65, 0.9)]
    if top.any():
        ty = np.nonzero(top.any(1))[0]
        t0, t1 = int(ty.min()) + 2, int(ty.max()) - 1
        if t1 - t0 >= 5:
            rows += [int(round(t0 + (t1 - t0) * t)) for t in (0.3, 0.75)]
    return squash_rows(f, rows)


def tm_frame(f, squash=True):
    if squash:
        f = tm_squash(f)
    return tm_clothes(tm_head(f))


def tm_portrait(f, mode='normal'):
    """头像 32×32：波鲁那雷夫的头像去掉竖起来的银发，换黑色头盔飞机头；眼睛压成一条缝（动画里玉美是细长眼）；
    背心换成 POLO 衫（领尖小国旗、左胸英国旗）；左嘴角下一道十字小疤"""
    a = np.array(f.convert('RGBA'))
    H, W = a.shape[:2]
    yy, xx = mgrid(H, W)
    hair_old = _colmask(a, ['#d6dcec', '#9098b6', '#60688a']) | (_colmask(a, ['#f6f8ff']) & (yy <= 12))
    a[hair_old] = 0
    isO = _colmask(a, [O])
    body = (a[..., 3] > 0) & ~isO
    a[isO & ~_grow(body, 1) & (yy <= 21)] = 0
    a[isO & (yy <= 9)] = 0
    dome = ((xx - 14.5) / 11.0) ** 2 + ((yy - 11.0) / 9.6) ** 2 <= 1
    dome &= (yy <= 10.5) | (xx <= 9.5)
    dome &= yy <= 17.5
    ang = np.deg2rad(-14)
    cx, cy = 21.0, 5.8
    u = ((xx - cx) * np.cos(ang) + (yy - cy) * np.sin(ang)) / 9.6
    v = (-(xx - cx) * np.sin(ang) + (yy - cy) * np.cos(ang)) / 5.4
    pomp = u * u + v * v <= 1
    hair = dome | pomp
    skin = _colmask(a, P_SKIN + [(255, 224, 192)])
    hair &= (a[..., 3] == 0) | (skin & (yy <= 10)) | (_colmask(a, [O]) & (yy <= 12))
    shade = np.full((H, W), 'k', object)
    up = np.zeros_like(hair)
    up[1:, :] = hair[:-1, :]
    shade[hair & ~up] = 'h'
    dd = ((xx - 14.5) / 11.0) ** 2 + ((yy - 11.0) / 9.6) ** 2
    shade[dome & ~pomp & (dd > 0.5) & (dd < 0.68) & (yy < 8)] = 'H'
    shade[pomp & (v < -0.28) & (v > -0.78) & (u > -0.6)] = 'H'
    shade[pomp & (v < -0.42) & (v > -0.72) & (u > -0.1) & (u < 0.55)] = 'X'
    shade[pomp & (v > 0.5)] = 'K'
    shade[dome & ~pomp & (yy > 12)] = 'K'
    shade[dome & ~pomp & (xx < 6) & (yy > 6) & (yy <= 12)] = 'h'
    for k, c in TMH.items():
        a[hair & (shade == k)] = (*c, 255)
    img = C.reoutline(Image.fromarray(a, 'RGBA'))
    b = np.array(img)
    sk = _colmask(b, P_SKIN)
    edge = np.zeros_like(hair)
    edge[1:, :] = hair[:-1, :] & ~hair[1:, :]
    b[edge & sk & (xx <= 13)] = (*O, 255)
    px = lambda x, y, c: b.__setitem__((y, x), (*_hex(c), 255))
    SKC, SKD = (246, 196, 154), (216, 148, 108)
    if mode in ('normal', 'smile', 'rage'):
        # 细长眼：下半只眼睛合上
        for x in range(9, 24):
            if tuple(b[17, x, :3]) in ((246, 248, 255), (60, 120, 224)):
                b[17, x] = (*SKC, 255)
    if mode == 'rage':
        for x in range(9, 24):
            if tuple(b[13, x, :3]) == (42, 30, 26):
                b[13, x] = (*SKC, 255)
        for (x, y) in ((10, 12), (11, 12), (12, 13), (13, 14), (22, 12), (21, 12), (20, 13), (19, 14)):
            px(x, y, (42, 30, 26))
    if mode == 'smile':
        for x in range(13, 19):
            if tuple(b[21, x, :3]) == O:
                b[21, x] = (*SKC, 255)
        for (x, y) in ((13, 20), (14, 21), (15, 21), (16, 21), (17, 21), (18, 20)):
            px(x, y, O)
    # 十字小疤：左嘴角下面
    for (x, y) in ((13, 22), (12, 23), (13, 23), (14, 23), (13, 24)):
        if b[y, x, 3] and tuple(b[y, x, :3]) != O:
            px(x, y, (184, 104, 88))
    # POLO 衫：背心和露出来的肩膀都换成衫，脖子两边翻出领尖
    sk2 = _colmask(b, P_SKIN) & (yy >= 26)
    neck = (xx >= 14) & (xx <= 15)
    b[sk2 & ~neck] = (*_hex(TM_TOP['#2a2632']), 255)
    for (x, y) in ((12, 26), (13, 26), (13, 27), (16, 26), (17, 26), (16, 27)):
        px(x, y, TM_COLLAR)
    px(12, 27, (214, 40, 48))
    px(17, 27, (214, 40, 48))
    px(17, 28, (246, 246, 246))
    px(17, 29, (40, 64, 168))
    for (x, y, c) in ((20, 29, (40, 64, 168)), (21, 29, (214, 40, 48)), (22, 29, (40, 64, 168)), (20, 30, (214, 40, 48)),
                      (21, 30, (214, 40, 48)), (22, 30, (214, 40, 48))):
        px(x, y, c)
    for y in (28, 29, 30, 31):
        px(14, y, TM_TOP_D)
    img = Image.fromarray(b, 'RGBA')
    img = C.recolor(img, TM_TOP)
    img = C.recolor(img, TM_EYE)
    img = C.recolor(img, TM_EAR)
    img = C.recolor(img, TM_SKIN)
    return img


def tamami_heads():
    hd = C.heads('polnareff')
    nm = hd['portrait']
    return {'normal': [tm_portrait(f) for f in nm], 'smile': [tm_portrait(f, 'smile') for f in nm],
            'rage': [tm_portrait(f, 'rage') for f in nm], 'shock': [tm_portrait(f, 'shock') for f in hd['portrait_shock']]}


def tm_down(f):
    """躺着的帧：转成头朝上处理（压矮、换头发、换衣服），再转回去"""
    r = f.rotate(-90, expand=True)
    r = tm_clothes(tm_head(tm_squash(r)))
    return r.rotate(90, expand=True).crop((0, 0, f.width, f.height))


def tm_crawl(f):
    """爬 / 跪趴：身子是横的，裤子和身子各抽两列（头在右边，往左挪）"""
    a = np.array(f.convert('RGBA'))
    pants = _colmask(a, ['#d8dcf2', '#9ea2cc', '#9a9ab0', '#7a7eaa'])
    top = _colmask(a, ['#2a2632', '#4e4860'])
    cols = []
    for m in (pants, top):
        if m.any():
            xs = np.nonzero(m.any(0))[0]
            x0, x1 = int(xs.min()) + 2, int(xs.max()) - 2
            if x1 - x0 >= 6:
                cols += [int(round(x0 + (x1 - x0) * t)) for t in (0.3, 0.7)]
    g = squash_cols(f, cols)
    # 往右挪回去，脚的位置不变
    out = Image.new('RGBA', g.size, (0, 0, 0, 0))
    out.alpha_composite(g, (0, 0))
    return tm_clothes(tm_head(out))


def tm_bow(f, deg):
    """点头哈腰：腰带以上整块往前（右）转 deg 度"""
    a = np.array(f.convert('RGBA'))
    belt = _colmask(a, [TM_BELT])
    if not belt.any():
        return f
    ys, xs = np.nonzero(belt)
    by, bx = int(ys.min()), int(round(xs.mean()))
    up = a.copy()
    up[by:] = 0
    lo = a.copy()
    lo[:by] = 0
    upi = C.strip_outline(Image.fromarray(up, 'RGBA'))
    ua = np.array(upi)
    isO = _colmask(ua, [O])
    ua[isO] = 0
    upi = Image.fromarray(ua, 'RGBA').rotate(-deg, resample=Image.NEAREST, center=(bx, by))
    lo_i = Image.fromarray(lo, 'RGBA')
    lo_i.alpha_composite(upi)
    return C.reoutline(lo_i)


def build_tamami():
    im, m = C.base('polnareff')
    sh = C.Sheet('tamami', '小林玉美', m['cell'], m['pivot'])
    fr = lambda an: [tm_frame(f) for f in C.frames('polnareff', an)]
    idle = fr('idle')
    walk = fr('walk')
    sh.add('idle', idle, 2, 'loop')
    sh.add('walk', walk, 8, 'loop')
    sh.add('run', walk, 13, 'loop')
    sh.add('cover_ears', fr('shock'), 6, 'loop')
    sh.add('cry', fr('cry'), 4, 'loop')
    sh.add('hurt', fr('hurt'), 1, 'static')
    sh.add('wave', fr('wave'), 4, 'loop')
    sh.add('fall', [tm_down(f) for f in C.frames('polnareff', 'down')], 1, 'static')
    crawl = [tm_crawl(f) for f in C.frames('polnareff', 'crawl')]
    sh.add('crawl', crawl, 4, 'loop')
    sh.add('kneel', crawl[:1], 1, 'static')
    sh.add('bow', [tm_bow(idle[0], 12), tm_bow(idle[0], 28)], 3, 'loop')
    sh.heads = tamami_heads()
    amap = dict(C.AMAP_HUMAN, shock='cover_ears', down='fall', hurt='hurt', run='run', guard='cover_ears', dodge='hurt',
                special='wave', win='wave', cmd='wave', cmd2='wave', cmd_hold='wave', getup='hurt')
    return C.save(sh, amap=amap, bodyW=4)


# ============================================================ 间田敏和：花京院的骨架，照动画配色
# 动画配色（jojowiki 的 TV 配色表）：皮肤苍白；黑色直长发；黑眼睛、上眼皮深；青绿色（teal）校服，
#   胸前几条竖着的皮带（像拘束衣），动画里是黄色和品红；棕鞋。动画里个子一直矮（和康一差不多）。
#   花京院垂在脸侧的那绺卷发剪到下巴，樱桃耳坠去掉
HZ_HAIR = {'#b8402e': '#26222e', '#e8734c': '#4c4a60', '#78221e': '#121016'}
HZ_SKIN = {'#f6c49a': '#fae2d2', '#d8946c': '#e2bcac'}
HZ_UNI = {'#2f9e56': '#2c9a98', '#1a6038': '#1a6468', '#62c874': '#5cc4bc', '#0f4028': '#0e4046', '#50b848': '#2c9a98'}
HZ_BELT_Y, HZ_BELT_M = (240, 208, 64), (208, 60, 140)
HZ_EYE = {'#9a4ce0': '#1c1820'}
KK_HAIR = ['#b8402e', '#e8734c', '#78221e']
KK_EAR = ['#e8243c', '#50b848', '#8a1024']


def hz_body(f, portrait=False):
    a = np.array(f.convert('RGBA'))
    h, w = a.shape[:2]
    yy, xx = mgrid(h, w)
    hair = _colmask(a, KK_HAIR)
    # 樱桃耳坠：换成头发的暗色（耳坠挂在头发那一侧）
    a[_colmask(a, KK_EAR)] = (*_hex('#78221e'), 255)
    # 附身帧头顶的粉色青筋去掉
    pink = _colmask(a, ['#f058b4', '#a02878'])
    near = np.zeros_like(pink)
    for dx in (-2, -1, 1, 2):
        near |= np.roll(hair, dx, 1)
    inside = pink & near & np.roll(hair | pink, 1, 0)
    a[inside] = (*_hex('#b8402e'), 255)
    a[pink & ~inside] = 0
    hair = _colmask(a, KK_HAIR)
    if not portrait:
        fb = C.face_box(Image.fromarray(a, 'RGBA'))
        if fb:
            fx0, fy0, fx1, fy1 = fb
            # 下巴以下还垂着的那绺头发：剪掉，补成校服
            lock = hair & (yy > fy1 + 1)
            a[lock] = (*_hex('#2f9e56'), 255)
    img = C.strip_outline(Image.fromarray(a, 'RGBA'))
    a = np.array(img)
    # 竖皮带：前襟那条金线换黄色，左边隔 3 格再加一条品红（只到腰带那一行为止）
    gold = _colmask(a, ['#ffd83c'])
    dgold = _colmask(a, ['#c89a20'])
    coat = _colmask(a, ['#2f9e56', '#62c874', '#1a6038'])
    both = gold | dgold
    collar = int(np.nonzero(both.any(1))[0].min()) if both.any() else 0
    rows = [y for y in range(collar + 3, h) if dgold[y].sum() >= 3]
    waist = rows[0] if rows else h
    ys, xs = np.nonzero(gold & (yy < waist) & (yy > collar + 1))
    for y, x in zip(ys, xs):
        for dx in ((-3, 3) if portrait else (-3,)):
            if 0 <= x + dx < w and coat[y, x + dx]:
                a[y, x + dx] = (*HZ_BELT_M, 255)
    img = Image.fromarray(a, 'RGBA')
    img = C.recolor(img, {'#ffd83c': HZ_BELT_Y, '#c89a20': HZ_BELT_M})
    img = C.recolor(img, HZ_HAIR)
    img = C.recolor(img, HZ_SKIN)
    img = C.recolor(img, HZ_UNI)
    img = C.recolor(img, HZ_EYE)
    return img


def hz_portrait(f, mode='normal'):
    img = hz_body(f, portrait=True)
    b = np.array(img)
    SKC = _hex(HZ_SKIN['#f6c49a'])
    px = lambda x, y, c: b.__setitem__((y, x), (*_hex(c), 255))
    # 衣领那条金边换成深青（领子上本来有个“间”字，32 格里画不下，留一个白点）
    for x in range(10, 25):
        if tuple(b[22, x, :3]) in (HZ_BELT_Y, HZ_BELT_M):
            b[22, x] = (*_hex(HZ_UNI['#1a6038']), 255)
    px(20, 22, (236, 240, 240))
    mouth = [(x, 19) for x in range(15, 23) if tuple(b[19, x, :3]) == (240, 136, 136)]
    if mode == 'smile':
        for x, y in mouth:
            px(x, y, SKC)
        for x, y in ((16, 19), (17, 19), (18, 19), (19, 19), (20, 18), (21, 17)):
            px(x, y, O)
    elif mode == 'rage':
        for x in range(14, 22):
            if tuple(b[10, x, :3]) == O:
                px(x, 10, SKC)
        for x, y in ((15, 9), (16, 9), (17, 10), (18, 10), (19, 11), (25, 11), (26, 10), (27, 10)):
            px(x, y, O)
        for x, y in mouth:
            px(x, y, (120, 24, 40))
    elif mode == 'shock':
        for y in (13, 14):
            for x in range(13, 28):
                if tuple(b[y, x, :3]) == (28, 24, 32):
                    px(x, y, (255, 255, 255))
        px(16, 14, O)
        px(25, 14, O)
        for x, y in mouth:
            px(x, y, O)
        for x, y in ((17, 20), (18, 20), (19, 20)):
            px(x, y, (120, 24, 40))
        for x, y in ((16, 20), (20, 20), (17, 21), (18, 21), (19, 21)):
            px(x, y, O)
    return Image.fromarray(b, 'RGBA')


def hazamada_heads():
    hd = C.heads('kakyoin')
    nm = hd['portrait']
    return {'normal': [hz_portrait(f) for f in nm], 'smile': [hz_portrait(f, 'smile') for f in nm],
            'rage': [hz_portrait(f, 'rage') for f in nm], 'shock': [hz_portrait(f, 'shock') for f in nm]}


def build_hazamada():
    im, m = C.base('kakyoin')
    sh = C.Sheet('hazamada', '间田敏和', m['cell'], m['pivot'])
    fr = lambda an: [hz_body(f) for f in C.frames('kakyoin', an)]
    sh.add('idle', fr('idle'), 2, 'loop')
    sh.add('walk', fr('walk'), 8, 'loop')
    sh.add('run', fr('walk'), 13, 'loop')
    sh.add('smirk', fr('possessed'), 3, 'loop')
    sh.add('point', fr('cast'), 4, 'loop')
    sh.add('shock', fr('hurt'), 1, 'static')
    sh.add('knocked', fr('down'), 1, 'static')
    sh.heads = hazamada_heads()
    amap = dict(C.AMAP_HUMAN, shock='shock', down='knocked', hurt='shock', run='run', guard='shock', dodge='shock',
                special='point', win='smirk', cmd='point', cmd2='point', cmd_hold='point', getup='shock')
    return C.save(sh, amap=amap, bodyW=4)


# ============================================================ 表面：间田的木偶。本体是一个和人一样大的木头人偶，碰到谁就变成谁
# surface_doll：仗助的身形挖掉头发、五官，整个换成木色（按明暗分四档），脖子、腰、膝盖画上关节缝
# surface：变成仗助以后的样子——仗助的全套帧，描边换成深木色、颜色往暖里偏一点（细看能看出是假的）
# surface_cut：段 B 被酒瓶夹断右手以后：前面那只手换成一截木头断面
WOOD = dict(l=(234, 196, 142), m=(206, 160, 104), d=(162, 114, 68), g=(122, 80, 46), o=(74, 44, 26))
J_HAIR = [(18, 14, 26), (36, 30, 54), (66, 58, 100), (122, 114, 176)]
J_SKIN = [(246, 196, 154), (216, 148, 108)]


def jfull(anim):
    m = L.load_json(os.path.join(C.FULL, 'josuke.json'))
    im = Image.open(os.path.join(C.FULL, 'josuke.png')).convert('RGBA')
    a = m['animations'][anim]
    cw, ch = m['cell']
    return [im.crop((i * cw, a['row'] * ch, (i + 1) * cw, (a['row'] + 1) * ch)) for i in range(a['frames'])]


def wood_tint(f):
    """假仗助：描边换深木色，别的颜色往暖里偏"""
    a = np.array(f.convert('RGBA')).astype(int)
    isO = (a[..., 0] == O[0]) & (a[..., 1] == O[1]) & (a[..., 2] == O[2]) & (a[..., 3] > 0)
    a[..., 0] = np.clip(a[..., 0] * 1.04 + 6, 0, 255)
    a[..., 1] = np.clip(a[..., 1] * 0.97, 0, 255)
    a[..., 2] = np.clip(a[..., 2] * 0.86, 0, 255)
    a[isO, :3] = WOOD['o']
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def cut_hand(f):
    """前面（最右边）那只手换成木头断面：手腕往外都去掉，留一截木头、断口一圈亮色"""
    a = np.array(f.convert('RGBA'))
    h, w = a.shape[:2]
    fb = C.face_box(f, 24, J_SKIN)
    if not fb:
        return f
    sk = _colmask(a, J_SKIN)
    yy, xx = mgrid(h, w)
    sk &= yy > fb[3] + 2
    bl = C.blobs(sk)
    if not bl:
        return f
    best = max(bl, key=lambda b: b[2].mean())
    _, ys, xs = best
    a[ys, xs] = 0
    hand = np.zeros((h, w), bool)
    hand[ys, xs] = True
    # 断口：手腕那一端（离身子近的一边）留两格木头
    keep = hand & (xx <= xs.min() + 1)
    a[keep] = (*WOOD['m'], 255)
    edge = keep & (xx == xs.min() + 1)
    a[edge] = (*WOOD['l'], 255)
    img = C.strip_outline(Image.fromarray(a, 'RGBA'), WOOD['o'])
    return C.reoutline(img, WOOD['o'])


def doll_frame(f):
    a = np.array(f.convert('RGBA'))
    h, w = a.shape[:2]
    yy, xx = mgrid(h, w)
    fb = C.face_box(f, 24, J_SKIN)
    head = np.zeros((h, w), bool)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        # 下巴以上、头附近的东西全清掉（头发、五官、描边），举起来的手（脸框外的皮肤）留着
        zone = (yy <= fy1) & (xx >= fx0 - 12) & (xx <= fx1 + 12)
        sk = _colmask(a, J_SKIN)
        facebox = (xx >= fx0) & (xx <= fx1) & (yy >= fy0)
        a[zone & ~(sk & ~facebox)] = 0
        a[_colmask(a, J_HAIR) & (yy <= fy1 + 2)] = 0
        # 木偶的头：一个比脸大一圈的蛋形，亮面在右上
        cx, cy = (fx0 + fx1) / 2 - 0.5, (fy0 + fy1) / 2 - 1.0
        rx, ry = (fx1 - fx0) / 2 + 1.6, (fy1 - fy0) / 2 + 3.2
        e = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        head = e <= 1
        lit = (xx - cx) / rx - (yy - cy) / ry
        a[head] = (*WOOD['m'], 255)
        a[head & (lit > 0.35)] = (*WOOD['l'], 255)
        a[head & (lit < -0.75)] = (*WOOD['d'], 255)
        # 脖子：头和身子之间补两格木头
        for y in (fy1 + 1, fy1 + 2):
            for x in range(int(cx) - 1, int(cx) + 2):
                if a[y, x, 3] == 0 or _colmask(a[y:y + 1, x:x + 1], [O])[0, 0]:
                    a[y, x] = (*WOOD['d'], 255)
    img = C.strip_outline(Image.fromarray(a, 'RGBA'))
    img = C.reoutline(img)
    a = np.array(img)
    isO = _colmask(a, [O])
    op = (a[..., 3] > 0) & ~isO
    wood = _colmask(a, list(WOOD.values()))
    lum = 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
    out = a.copy()
    body = op & ~wood
    out[body & (lum >= 150)] = (*WOOD['l'], 255)
    out[body & (lum < 150) & (lum >= 90)] = (*WOOD['m'], 255)
    out[body & (lum < 90) & (lum >= 45)] = (*WOOD['d'], 255)
    out[body & (lum < 45)] = (*WOOD['g'], 255)
    out[isO] = (*WOOD['o'], 255)
    # 关节缝：腰、膝盖各一道（只画在木头中间，不碰描边）
    bb = img.getbbox()
    if bb and fb:
        top, bot = bb[1], bb[3]
        for y in (int(top + (bot - top) * 0.56), int(top + (bot - top) * 0.80)):
            row = op[y] & np.roll(op[y], 1) & np.roll(op[y], -1) & ~head[y]
            out[y, row] = (*WOOD['g'], 255)
    return Image.fromarray(out, 'RGBA')


def build_surface_doll():
    m = L.load_json(os.path.join(C.FULL, 'josuke.json'))
    sh = C.Sheet('surface_doll', '表面', m['cell'], m['pivot'])
    sh.add('idle', [doll_frame(f) for f in jfull('idle')], 2, 'loop')
    sh.add('walk', [doll_frame(f) for f in jfull('walk')], 8, 'loop')
    sh.add('jump', [doll_frame(f) for f in jfull('dodge')], 1, 'static')
    # 躺着的帧转成头朝上再处理，处理完转回去
    sh.add('fall', [doll_frame(f.rotate(-90, expand=True)).rotate(90, expand=True).crop((0, 0, f.width, f.height))
                    for f in jfull('down')], 1, 'static')
    sh.add('hurt', [doll_frame(f) for f in jfull('hurt')], 1, 'static')
    return C.save(sh, amap={'talk': 'idle', 'run': 'walk', 'down': 'fall', 'hurt': 'hurt', 'dodge': 'jump', 'shock': 'hurt'}, bodyW=4)


def _surface_sheet(cid, name, cut=False):
    m = L.load_json(os.path.join(C.FULL, 'josuke.json'))
    sh = C.Sheet(cid, name, m['cell'], m['pivot'])
    for anim, a in m['animations'].items():
        frs = [wood_tint(f) for f in jfull(anim)]
        if cut:
            frs = [cut_hand(f) for f in frs]
        sh.add(anim, frs, a['fps'], a['kind'])
    heads = {}
    for emo in ('normal', 'rage', 'smile', 'shock'):
        fs = sorted(f for f in os.listdir(os.path.join(L.ASSETS, 'heads', 'josuke')) if f.startswith(emo + '_'))
        heads[emo] = [wood_tint(Image.open(os.path.join(L.ASSETS, 'heads', 'josuke', f)).convert('RGBA')) for f in fs]
    sh.heads = heads
    amap = dict(C.AMAP_HUMAN, kick='kick', sit='sit', run='run')
    return C.save(sh, amap=amap, bodyW=4)


def build_surface():
    return _surface_sheet('surface', '表面')


def build_surface_cut():
    return _surface_sheet('surface_cut', '表面', cut=True)


# ============================================================ 康一的妈妈、姐姐广濑绫那
# 妈妈（动画）：棕色短发；奶油色和橙色横条纹的上衣、白裙子、棕色拖鞋。用荷莉的骨架（短发、长开衫的家庭主妇）
# 绫那（动画）：棕色及肩发；粉色连衣裙、蓝色领结、白腰带、粉鞋。用女学生 A 的骨架（及肩的短发）
TEAR = (120, 200, 250)
MOM_HAIR = {'#fff6cc': '#c08a5c', '#f8e08e': '#9a6640', '#d2a650': '#6c4428'}
MOM_EYE = {'#3c8ad8': '#4a3226'}
MOM_SHOE = {'#e0506a': '#a06a40', '#9a2a44': '#6a4228'}
STRIPE = ((250, 238, 210), (236, 150, 84))         # 奶油、橙
STRIPE_D = ((222, 204, 176), (198, 118, 60))
SKIRT, SKIRT_D = (246, 246, 242), (206, 208, 212)
AYA_HAIR = {'#3e3846': '#c08a5c', '#1e1a22': '#8e5e3c', '#0e0c12': '#5e3c24'}
AYA_DRESS = {'#2c3462': '#ee8cae', '#181d3e': '#c45a84', '#e0303c': '#4a78d4'}
AYA_SHOE = {'#6a4228': '#ec7898', '#5a361e': '#b8506e'}


def stripes(f, waist, light_cols, dark_cols, y0=0):
    """上衣画横条纹（2 行奶油 1 行橙），waist 以下是白裙子"""
    a = np.array(f.convert('RGBA'))
    h, w = a.shape[:2]
    lm = _colmask(a, light_cols)
    dm = _colmask(a, dark_cols)
    for y in range(h):
        k = 1 if (y - y0) % 3 == 2 else 0
        if y <= waist:
            a[y][lm[y]] = (*STRIPE[k], 255)
            a[y][dm[y]] = (*STRIPE_D[k], 255)
        else:
            a[y][lm[y]] = (*SKIRT, 255)
            a[y][dm[y]] = (*SKIRT_D, 255)
    return Image.fromarray(a, 'RGBA')


def tears(f, iris, closed=True):
    """哭：眼睛闭成一条线（可选），眼睛下面挂两行眼泪"""
    a = np.array(f.convert('RGBA'))
    m = _colmask(a, iris)
    eyes = C.blobs(m)
    for _, ys, xs in eyes[:2]:
        yb = int(ys.max())
        xl = int(xs.min())
        if closed:
            for y, x in zip(ys, xs):
                a[y, x] = (*O, 255) if y == yb else a[y, x]
        for dy in (1, 2, 3):
            y = yb + dy
            if y < a.shape[0] and a[y, xl, 3] and tuple(a[y, xl, :3]) != O:
                a[y, xl] = (*TEAR, 255)
    return Image.fromarray(a, 'RGBA')


def mom_body(f):
    a = np.array(f.convert('RGBA'))
    band = _colmask(a, ['#c95f8f'])
    rows = [y for y in range(a.shape[0]) if band[y].sum() >= 4]
    waist = rows[0] if rows else int(a.shape[0] * 0.6)
    img = stripes(f, waist, ['#c6daf4', '#f592be', '#ffc8de'], ['#8ea8d6', '#c95f8f'], y0=waist - 8)
    img = C.recolor(img, MOM_HAIR)
    img = C.recolor(img, MOM_EYE)
    img = C.recolor(img, MOM_SHOE)
    return img


def _face_edit(f, mode, iris, mouth_red=(154, 42, 68)):
    b = np.array(f.convert('RGBA'))
    SKC = (246, 196, 154)
    px = lambda x, y, c: b.__setitem__((y, x), (*c, 255))
    if mode == 'smile':
        for x in range(15, 19):
            px(x, 18, mouth_red)
            px(x, 19, O)
    elif mode == 'shock':
        for x in range(14, 20):
            for y in (17, 18):
                if tuple(b[y, x, :3]) == O:
                    px(x, y, SKC)
        for x, y in ((16, 17), (17, 17), (15, 18), (18, 18), (16, 19), (17, 19)):
            px(x, y, O)
        px(16, 18, mouth_red)
        px(17, 18, mouth_red)
        ic = _hex(iris)
        for y in (11, 12):
            for x in range(13, 27):
                if tuple(b[y, x, :3]) == ic:
                    px(x, y, (255, 255, 255))
        px(15, 12, O)
        px(24, 12, O)
    elif mode == 'cry':
        ic = _hex(iris)
        for y in (11, 12):
            for x in range(13, 27):
                if tuple(b[y, x, :3]) in (ic, (255, 255, 255)):
                    px(x, y, SKC if y == 11 else O)
        for x in (14, 23):
            for y in (13, 14, 15):
                px(x, y, TEAR)
    return Image.fromarray(b, 'RGBA')


def mom_head(f, mode='normal'):
    img = _face_edit(f, mode, '#3c8ad8')
    a = np.array(img)
    band = 28
    img = stripes(img, 99, ['#c6daf4', '#f592be', '#ffc8de'], ['#8ea8d6', '#c95f8f'], y0=22)
    img = C.recolor(img, MOM_HAIR)
    img = C.recolor(img, MOM_EYE)
    return img


def build_hirose_mom():
    im, m = C.base('holly')
    sh = C.Sheet('hirose_mom', '康一的妈妈', m['cell'], m['pivot'])
    sh.add('idle', [mom_body(f) for f in C.frames('holly', 'idle')], 2, 'loop')
    sh.add('walk', [mom_body(f) for f in C.frames('holly', 'walk')], 8, 'loop')
    sh.add('cry', [mom_body(tears(f, ['#3c8ad8', '#ffffff'])) for f in C.frames('holly', 'faint')[:1]], 1, 'static')
    sh.add('wave', [mom_body(f) for f in C.frames('holly', 'wave')], 4, 'loop')
    hp = C.heads('holly')['portrait']
    sh.heads = {'normal': [mom_head(f) for f in hp], 'smile': [mom_head(f, 'smile') for f in hp],
                'shock': [mom_head(f, 'shock') for f in hp], 'rage': [mom_head(f, 'cry') for f in hp]}
    e = C.save(sh, amap={'talk': 'idle', 'run': 'walk', 'shock': 'cry', 'hurt': 'cry', 'down': 'cry'}, bodyW=4)
    return e


def aya_body(f):
    a = np.array(f.convert('RGBA'))
    # 腰带：腰上那一行深色换成白
    band = _colmask(a, ['#181d3e'])
    rows = [y for y in range(20, a.shape[0]) if band[y].sum() >= 6]
    if rows:
        y = rows[0]
        a[y][band[y]] = (240, 240, 238, 255)
    img = Image.fromarray(a, 'RGBA')
    img = C.recolor(img, AYA_HAIR)
    img = C.recolor(img, AYA_DRESS)
    img = C.recolor(img, AYA_SHOE)
    return img


def aya_head(f, mode='normal'):
    img = _face_edit(f, mode, '#3a2a22')
    img = C.recolor(img, AYA_HAIR)
    return C.recolor(img, AYA_DRESS)


def build_ayana():
    im, m = C.base('npc_student_f_a')
    sh = C.Sheet('ayana', '广濑绫那', m['cell'], m['pivot'])
    sh.add('idle', [aya_body(f) for f in C.frames('npc_student_f_a', 'idle')], 2, 'loop')
    sh.add('walk', [aya_body(f) for f in C.frames('npc_student_f_a', 'walk')], 8, 'loop')
    sh.add('cry', [aya_body(tears(f, ['#3a2a22', '#ffffff'])) for f in C.frames('npc_student_f_a', 'idle')], 3, 'loop')
    sh.add('cheer', [aya_body(f) for f in C.frames('npc_student_f_a', 'cheer')], 4, 'loop')
    hp = C.heads('npc_student_f_a')['portrait']
    sh.heads = {'normal': [aya_head(f) for f in hp], 'smile': [aya_head(f, 'smile') for f in hp],
                'shock': [aya_head(f, 'shock') for f in hp], 'rage': [aya_head(f, 'cry') for f in hp]}
    return C.save(sh, amap={'talk': 'idle', 'run': 'walk', 'shock': 'cry', 'hurt': 'cry', 'down': 'cry'}, bodyW=3)


# ============================================================ 飙车族 A / B：仗助的骨架（飞机头本来就是不良少年的标配），换成特攻服的配色
# A：白色特攻服、黑内衫、金色飞机头；B：黑色特攻服、红内衫、暗红飞机头、墨镜。原作没给配色，按 80 年代暴走族的常见样子定
J_COAT = ['#6866c8', '#363476', '#3a3662', '#1e1c46', '#221e42']
BIKER = {
    'biker_a': dict(name='飙车族A', coat=['#fafaf6', '#e2e2de', '#d2d2d0', '#a8a8ac', '#96969c'], shirt=['#242228', '#16141a'],
                    hair=['#ecc860', '#b08834', '#fae496', '#fff6ce'], shoe=['#28242c', '#16141a'], badge=['#dc2828', '#961420'],
                    hair2='#c8a040', shades=False),
    'biker_b': dict(name='飙车族B', coat=['#54486e', '#2c263c', '#363048', '#181422', '#1e1a28'], shirt=['#c42830', '#821820'],
                    hair=['#6e2c28', '#401818', '#964638', '#c46e5a'], shoe=['#dcdcdc', '#aaaab0'], badge=['#ffd83c', '#c89a20'],
                    hair2='#562220', shades=True),
}


def biker_map(cfg):
    mp = dict(zip(J_COAT, cfg['coat']))
    mp.update(zip(['#deba3e', '#a47e22'], cfg['shirt']))
    mp.update(zip(['#241e36', '#120e1a', '#423a64', '#7a72b0'], cfg['hair']))
    mp.update(zip(['#764a96', '#482a62'], cfg['shoe']))
    mp.update(zip(['#ffd83c', '#c89a20'], cfg['badge']))
    return mp


def biker_frame(f, cfg, head=False):
    mp = biker_map(cfg)
    if head:
        # 头像的头发是另一套色（p4_heads 的 JP）：最暗、暗、中、亮、最亮
        h = cfg['hair']
        mp.update({'#120e1a': h[1], '#221c32': cfg['hair2'], '#383054': h[0], '#5c5488': h[2], '#928ac4': h[3]})
    img = C.recolor(f, mp)
    if cfg['shades']:
        # 墨镜：眼睛（蓝紫的眼珠和眼白）全涂黑，镜片上留一格反光
        a = np.array(img)
        eye = _colmask(a, ['#5c5ee0', '#efe6d2', '#ffffff', '#5c5ee0'])
        if head:
            eye |= _colmask(a, [(239, 230, 210), (92, 94, 224), (255, 255, 255)])
        a[eye] = (20, 20, 26, 255)
        ys, xs = np.nonzero(eye)
        if len(xs):
            a[ys.min(), xs.max()] = (120, 140, 170, 255)
        img = Image.fromarray(a, 'RGBA')
    return img


def build_biker(cid):
    cfg = BIKER[cid]
    m = L.load_json(os.path.join(C.FULL, 'josuke.json'))
    sh = C.Sheet(cid, cfg['name'], m['cell'], m['pivot'])
    for anim, fps, kind in (('idle', 2, 'loop'), ('walk', 8, 'loop'), ('run', 11, 'loop'), ('point', 4, 'loop'),
                            ('hurt', 1, 'static'), ('kick', 8, 'oneshot'), ('down', 1, 'static')):
        sh.add(anim, [biker_frame(f, cfg) for f in jfull(anim)], fps, kind)
    heads = {}
    for emo in ('normal', 'rage'):
        fs = sorted(f for f in os.listdir(os.path.join(L.ASSETS, 'heads', 'josuke')) if f.startswith(emo + '_'))
        heads[emo] = [biker_frame(Image.open(os.path.join(L.ASSETS, 'heads', 'josuke', f)).convert('RGBA'), cfg, head=True) for f in fs]
    sh.heads = heads
    return C.save(sh, amap=dict(C.AMAP_HUMAN, kick='kick', run='run', shock='hurt'), bodyW=4)


def build_biker_a():
    return build_biker('biker_a')


def build_biker_b():
    return build_biker('biker_b')


# ============================================================ 由花子（剪影）：第2章只在走廊拐角站 1 秒、脸红，不出名牌；正式的人物第3章画
SIL, SIL_O, SIL_HL = (44, 34, 58), (22, 16, 30), (70, 58, 92)


def build_yukako_sil():
    im, m = C.base('npc_student_f_a')
    sh = C.Sheet('yukako_sil', '？？？', m['cell'], m['pivot'])
    frs = []
    for f in C.frames('npc_student_f_a', 'idle'):
        a = np.array(f.convert('RGBA'))
        h, w = a.shape[:2]
        hair = _colmask(a, ['#3e3846', '#1e1a22', '#0e0c12'])
        ys, xs = np.nonzero(hair)
        # 长发：从后脑一直垂到腰下
        x0 = int(xs.min())
        y0 = int(ys.min()) + 6
        for y in range(y0, int(h * 0.78)):
            for x in range(x0, x0 + 6 - (1 if y > h * 0.7 else 0)):
                if a[y, x, 3] == 0 or not _colmask(a[y:y + 1, x:x + 1], [O])[0, 0]:
                    a[y, x] = (*SIL, 255)
        op = a[..., 3] > 0
        isO = _colmask(a, [O])
        a[op & ~isO] = (*SIL, 255)
        a[hair & (np.arange(h)[:, None] == ys.min() + 1)] = (*SIL_HL, 255)
        img = C.reoutline(Image.fromarray(a, 'RGBA'), SIL_O)
        b = np.array(img)
        b[_colmask(b, [O])] = (*SIL_O, 255)
        # 脸红：脸上两格粉色
        fb = C.face_box(f)
        if fb:
            for x in (fb[2] - 3, fb[2] - 2):
                b[fb[1] + 6, x] = (240, 120, 150, 255)
        frs.append(Image.fromarray(b, 'RGBA'))
    sh.add('idle', frs, 2, 'loop')
    e = C.save(sh, amap={'talk': 'idle'}, bodyW=3)
    e['heads'] = {}
    return e


# ============================================================ 康一骑新自行车（第2章开头）：康一的上半身坐在车上，两帧蹬车
BIKE_RED, BIKE_RED_D, BIKE_RED_L = (214, 52, 56), (150, 30, 40), (250, 120, 110)
TIRE, RIM, SPOKE = (30, 30, 38), (176, 178, 190), (214, 216, 226)
K_UNI_C = ((61, 92, 71), (34, 54, 42), (90, 127, 98))


def _line(dr, p0, p1, c, w=1):
    dr.line([p0, p1], fill=(*c, 255), width=w)


def bike_frame(phase, rider=True):
    from PIL import ImageDraw
    W, H = 56, 48
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    rear, front, crank = (11, 38), (43, 38), (25, 37)
    for cx, cy in (rear, front):
        dr.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=(*TIRE, 255), width=2)
        dr.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=(*RIM, 255), width=1)
        for k in range(4):
            ang = np.pi * k / 4 + phase * np.pi / 8
            dx, dy = int(round(5 * np.cos(ang))), int(round(5 * np.sin(ang)))
            _line(dr, (cx - dx, cy - dy), (cx + dx, cy + dy), SPOKE)
        im.putpixel((cx, cy), (*RIM, 255))
    seat, stem = (19, 24), (37, 22)
    _line(dr, seat, (36, 25), BIKE_RED, 2)           # 上管
    _line(dr, (36, 25), crank, BIKE_RED, 2)          # 下管
    _line(dr, seat, crank, BIKE_RED, 2)              # 立管
    _line(dr, crank, rear, BIKE_RED_D, 1)            # 后下叉
    _line(dr, (seat[0], seat[1] + 1), rear, BIKE_RED_D, 1)
    _line(dr, stem, front, BIKE_RED, 2)              # 前叉
    _line(dr, (35, 20), (40, 20), TIRE, 2)           # 车把
    _line(dr, (16, 22), (22, 22), TIRE, 2)           # 车座
    _line(dr, (21, 25), (33, 24), BIKE_RED_L, 1)     # 上管高光
    dr.ellipse([crank[0] - 2, crank[1] - 2, crank[0] + 2, crank[1] + 2], fill=(*RIM, 255))
    ped = []
    for k in (0, 1):
        ang = phase * np.pi / 2 + k * np.pi
        ped.append((crank[0] + int(round(4 * np.cos(ang))), crank[1] + int(round(4 * np.sin(ang)))))
    if rider:
        kf = Image.open(os.path.join(C.FULL, 'koichi.png')).convert('RGBA').crop((0, 0, 32, 48))
        bb = kf.getbbox()
        # 上半身：头顶到腰（身高的 58%），往前倾一点，屁股坐在车座上
        cut = bb[1] + int((bb[3] - bb[1]) * 0.58)
        up = kf.crop((0, 0, 32, cut))
        up = up.rotate(-8, resample=Image.NEAREST, center=(16, cut - 1), expand=False)
        hip = (19, 23)
        # 腿：大腿到膝盖、小腿到脚蹬（深色那条腿在后面）
        for i, (px_, py_) in enumerate(ped):
            col = K_UNI_C[1] if i == 1 else K_UNI_C[0]
            kx, ky = (hip[0] + px_) // 2 + 4, min(hip[1] + 4, py_ - 6)
            _line(dr, hip, (kx, ky), col, 3)
            _line(dr, (kx, ky), (px_, py_ - 1), col, 3)
            _line(dr, (px_ - 1, py_), (px_ + 2, py_), (110, 62, 36), 2)
        im.alpha_composite(up, (hip[0] - 16, hip[1] - cut + 3))
        # 胳膊：肩膀到车把
        _line(dr, (21, 18), (34, 20), K_UNI_C[0], 2)
        dr.rectangle([35, 19, 36, 20], fill=(246, 196, 154, 255))
    else:
        for (px_, py_) in ped:
            _line(dr, (px_ - 1, py_), (px_ + 1, py_), TIRE, 1)
    return C.reoutline(im)


def build_koichi_bike():
    sh = C.Sheet('koichi_bike', '广濑康一', (56, 48), (27, 47))
    sh.add('ride', [bike_frame(0), bike_frame(1), bike_frame(2), bike_frame(3)], 10, 'loop')
    sh.add('idle', [bike_frame(0)], 1, 'static')
    e = C.save(sh, amap={'talk': 'idle', 'walk': 'ride', 'run': 'ride'}, bodyW=6)
    e['heads'] = {}
    return e


# ============================================================ 康一补动作：第2章起康一能操作（第 3、4 战），原来的图只有 idle / walk / bow
# 在康一的全尺寸图（p4_chars.build_koichi 的产物，配色已按动画改过）上补：cmd（伸手指挥回音）、hurt（往后仰）、
#   down（仰面倒地）、dodge（压低身子往前冲）、guard（胳膊挡在脸前）。格子从 32 宽放到 48 宽（躺下的帧放得下），
#   元数据写进 chars_ch2.json 的 koichi 条目（深合并：换成 chars/koichi_ex 这张图，头像还用原来的）
KX_L, KX_M, KX_D = (61, 92, 71), (90, 127, 98), (34, 54, 42)
KX_SK, KX_SK2 = (246, 196, 154), (216, 148, 108)


def kfull(anim):
    m = L.load_json(os.path.join(C.FULL, 'koichi.json'))
    im = Image.open(os.path.join(C.FULL, 'koichi.png')).convert('RGBA')
    a = m['animations'][anim]
    cw, ch = m['cell']
    out = []
    for i in range(a['frames']):
        f = im.crop((i * cw, a['row'] * ch, (i + 1) * cw, (a['row'] + 1) * ch))
        c = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
        c.alpha_composite(f, (8, 0))
        out.append(c)
    return out


def _kline(dr, p0, p1, col, w):
    dr.line([p0, p1], fill=(*col, 255), width=w)


def kx_noarm(f):
    """去掉前面那只胳膊（身子右边、x ≥ 28 那一块），身子右沿补描边"""
    a = np.array(f)
    a[22, 29:] = 0
    a[23:33, 28:] = 0
    for y in range(23, 33):
        if a[y, 27, 3]:
            a[y, 28] = (*O, 255)
    return a


def kx_cmd(f, reach=0):
    from PIL import ImageDraw
    a = kx_noarm(f)
    img = Image.fromarray(a, 'RGBA')
    dr = ImageDraw.Draw(img)
    y0 = 24
    _kline(dr, (27, y0), (36 + reach, y0 - 1), KX_M, 1)
    _kline(dr, (27, y0 + 1), (36 + reach, y0), KX_L, 1)
    _kline(dr, (27, y0 + 2), (36 + reach, y0 + 1), KX_D, 1)
    dr.rectangle([37 + reach, y0 - 2, 39 + reach, y0 + 1], fill=(*KX_SK, 255))
    dr.point((37 + reach, y0 + 1), fill=(*KX_SK2, 255))
    dr.point((40 + reach, y0 - 2), fill=(*KX_SK, 255))
    return C.reoutline(img)


def kx_guard(f):
    from PIL import ImageDraw
    a = kx_noarm(f)
    img = Image.fromarray(a, 'RGBA')
    dr = ImageDraw.Draw(img)
    _kline(dr, (27, 25), (32, 24), KX_L, 3)        # 上臂往前
    _kline(dr, (32, 24), (31, 15), KX_L, 3)        # 小臂竖在脸前
    _kline(dr, (33, 23), (32, 16), KX_D, 1)
    dr.rectangle([30, 12, 32, 14], fill=(*KX_SK, 255))
    return C.reoutline(img)


def kx_tilt(f, deg, cut=34, squash=0):
    """腰以上整块转 deg 度（正数往后仰，负数往前倾）；squash 是腿抽掉几行"""
    a = np.array(f)
    up = a.copy()
    up[cut:] = 0
    lo = a.copy()
    lo[:cut] = 0
    ua = np.array(C.strip_outline(Image.fromarray(up, 'RGBA')))
    ua[_colmask(ua, [O])] = 0
    upi = Image.fromarray(ua, 'RGBA').rotate(deg, resample=Image.NEAREST, center=(24, cut))
    loi = Image.fromarray(lo, 'RGBA')
    loi.alpha_composite(upi)
    img = C.reoutline(loi)
    if squash:
        rows = [cut + 2 + i * 2 for i in range(squash)]
        img = squash_rows(img, rows)
    return img


def kx_shock_eyes(f):
    a = np.array(f)
    iris = _colmask(a, ['#2e4c8c'])
    a[iris] = (255, 255, 255, 255)
    ys, xs = np.nonzero(iris)
    if len(xs):
        for bx in (int(xs.min()), int(xs.max())):
            a[int(ys.min()), bx] = (*O, 255)
    return Image.fromarray(a, 'RGBA')


def kx_down(f):
    g = C.strip_outline(f)
    r = g.rotate(90, expand=True)              # 头朝左、仰面
    bb = r.getbbox()
    r = r.crop(bb)
    c = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    c.alpha_composite(r, ((48 - r.width) // 2, 47 - r.height))
    return C.reoutline(c)


def build_koichi_ex():
    idle = kfull('idle')
    sh = C.Sheet('koichi_ex', '广濑康一', (48, 48), (24, 48))
    sh.add('idle', idle, 2, 'loop')
    sh.add('walk', kfull('walk'), 8, 'loop')
    sh.add('bow', kfull('bow'), 1, 'static')
    sh.add('cmd', [kx_cmd(idle[0]), kx_cmd(idle[1], 1)], 6, 'loop')
    sh.add('hurt', [kx_shock_eyes(kx_tilt(idle[0], 12))], 1, 'static')
    sh.add('down', [kx_down(idle[0])], 1, 'static')
    sh.add('dodge', [kx_tilt(idle[0], -16, squash=3)], 1, 'static')
    sh.add('guard', [kx_guard(kx_tilt(idle[0], -5))], 1, 'static')
    e = C.save(sh, amap={'talk': 'idle', 'run': 'walk', 'shock': 'hurt', 'hurt': 'hurt', 'down': 'down', 'getup': 'hurt',
                         'dodge': 'dodge', 'guard': 'guard', 'block': 'guard', 'cmd': 'cmd', 'cmd2': 'cmd', 'cmd_hold': 'cmd',
                         'special': 'cmd', 'win': 'cmd', 'shoot': 'cmd'}, bodyW=3)
    e['name'] = '广濑康一'
    for k in ('heads', 'headAlias', 'headSize'):
        e.pop(k, None)
    return e


HEROES = {
    'okuyasu': dict(cid='okuyasu', cn='虹村亿泰', short='亿泰', rn='NIJIMURA OKUYASU', stand='thehand',
                    burst=['#14286a', '#3462d0', '#78a6ff'], panel='#0a1430', accent='#78a6ff', nameColor='#3a5ab0', blipHz=400,
                    grunt='grunt_jotaro'),
    # 序章的康一还没有替身（stand null）；第2章孵出回音以后才有。前面的章不让康一当队长，所以直接改这一条
    'koichi': dict(stand='echoes1'),
}
SPEAKERS = {
    'thehand': dict(short='轰炸空间', nameColor='#3a6ad0', blipHz=380),
    'echoes1': dict(short='回音', nameColor='#2a9a6a', blipHz=900),
    'tamami': dict(short='玉美', nameColor='#6a74c0', blipHz=360),
    'thelock': dict(short='锁', nameColor='#8a90a8', blipHz=300),
    'hazamada': dict(short='间田', nameColor='#2a8a88', blipHz=480),
    'surface': dict(short='表面', nameColor='#a8783c', blipHz=440),
    'surface_cut': dict(short='表面', nameColor='#a8783c', blipHz=440),
    'surface_doll': dict(short='表面', nameColor='#a8783c', blipHz=440),
    'hirose_mom': dict(short='康一妈妈', nameColor='#d07a4a', blipHz=700),
    'ayana': dict(short='绫那', nameColor='#e0709a', blipHz=820),
    'biker_a': dict(short='飙车族A', nameColor='#9a9aa4', blipHz=360),
    'biker_b': dict(short='飙车族B', nameColor='#7a4a8a', blipHz=340),
    'yukako_sil': dict(short='？？？', nameColor='#5a4a7a', blipHz=760),
    'koichi_bike': dict(short='康一', nameColor='#4a8a5a', blipHz=640),
    'phone_voice': dict(short='电话里的声音', nameColor='#9aa0b4', blipHz=300),
    'hotel_front': dict(short='酒店前台', nameColor='#8a7a5a', blipHz=740),
    'classmate': dict(short='同学', nameColor='#6a8aa0', blipHz=560),
}
STANDS = {
    'thehand': dict(cn='轰炸空间', en='THE HAND', owner='okuyasu', aura='#78a6ff', card='#a8c8ff', ghost='#d0e0ff', impact='blue',
                    kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx='stand_summon_star', fist=True),
    # ACT1 个子小，浮在康一肩膀后面（z 高一点），没有拳头：连打特效不用
    'echoes1': dict(cn='回音 ACT1', en='ECHOES ACT1', owner='koichi', aura='#60e0a0', card='#a0f0c8', ghost='#d0ffe4', impact='green',
                    kind='humanoid', idle={'dx': -10, 'z': 14}, link=None, summonSfx='stand_summon_star', fist=False),
    # 锁不是站在旁边的替身，是挂在别人胸口的道具（props lock_s / lock_m / lock_l）；这里只给替身卡、说话名用
    'thelock': dict(cn='锁', en='THE LOCK', owner='tamami', aura='#a0a8c8', card='#c8d0e8', ghost='#e0e4f0', impact='blue',
                    kind='object', idle={'dx': 0, 'z': 0}, link=None, summonSfx=None, fist=False),
    # 表面本身就是一个人偶（surface_doll / surface / surface_cut 是角色），不另外召唤
    'surface': dict(cn='表面', en='SURFACE', owner='hazamada', aura='#d8a868', card='#e8c890', ghost='#f4e0c0', impact='orange',
                    kind='object', idle={'dx': 0, 'z': 0}, link=None, summonSfx=None, fist=False),
}


# ============================================================ 道具（游戏比例，写 _meta/props_ch2.json）
def prop_echoes_egg():
    """回音的蛋：0 完整 / 1 细裂纹 / 2 大裂缝 / 3 顶上碎开只剩半个壳。全尺寸画好再用 shrink 缩成游戏比例（和人物同一套缩法）"""
    W, H = 60, 46
    full = Image.new('RGBA', (W * 4, H), (0, 0, 0, 0))
    for i in range(4):
        full.alpha_composite(egg_frame(i), (i * W, 0))
    small, cell, pivot = C.SH.shrink_sheet(full, (W, H), (W // 2, H - 2), C.SH.CK)
    frs = [small.crop((i * cell[0], 0, (i + 1) * cell[0], cell[1])) for i in range(4)]
    frs = [f.crop(f.getbbox()) for f in frs]
    PR.save('echoes_egg', frs, outline=False)
    return PR.PROPS['echoes_egg']


PROP_BUILDERS = {'echoes_egg': prop_echoes_egg}


# ============================================================ 第2章的道具（游戏比例直接画，PR.save 每帧外面自动描一圈边）
STEEL = dict(H=(246, 248, 255), S=(214, 218, 230), s=(160, 166, 186), d=(104, 108, 132), K=(20, 16, 30), c=(52, 44, 66))


def _cv(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def _c(col):
    return (*_hex(col), 255) if isinstance(col, str) else (*col, 255)


def lock_img(W, state=0):
    """锁：W 是宽。state 0 锁上 / 1 锁梁弹开 / 2 锁梁落下一半 / 3 裂纹 / 4 裂成两半 / 5 碎片 / 6 碎渣"""
    H = W + W // 2
    im, d = _cv(W + 6, H + 4)
    ox, oy = 3, 2
    bh = int(round(W * 0.78))
    by = oy + H - bh
    t = 1 if W < 12 else 2
    if state <= 4:
        # 锁梁：倒 U，开的时候整根往上抬、右腿离开锁身
        lift = {1: W // 3 + 1, 2: W // 6 + 1}.get(state, 0)
        sx0, sx1 = ox + t + 1, ox + W - t - 2
        top = oy + lift
        col = STEEL['S']
        for k in range(t):
            d.line([(sx0 + k, by - 1), (sx0 + k, top + 2)], fill=_c(col))
            d.line([(sx1 - k, by - 1 - (lift if state == 1 else 0)), (sx1 - k, top + 2)], fill=_c(STEEL['s']))
        d.arc([sx0, top, sx1, top + (sx1 - sx0)], 180, 360, fill=_c(col), width=t)
    if state <= 3:
        d.rounded_rectangle([ox, by, ox + W - 1, oy + H - 1], radius=max(1, W // 6), fill=_c(STEEL['s']))
        d.rectangle([ox + 1, by + 1, ox + W - 2, by + 1 + max(1, bh // 5)], fill=_c(STEEL['S']))
        d.line([(ox + W - 2, by + 2), (ox + W - 2, oy + H - 2)], fill=_c(STEEL['d']))
        d.line([(ox + 1, oy + H - 2), (ox + W - 2, oy + H - 2)], fill=_c(STEEL['d']))
        d.point((ox + 1, by + 1), fill=_c(STEEL['H']))
        kx, ky = ox + W // 2, by + bh // 2
        d.ellipse([kx - 1, ky - 2, kx, ky - 1], fill=_c(STEEL['K']))
        d.line([(kx, ky - 1), (kx, ky + max(1, bh // 5))], fill=_c(STEEL['K']))
        if state == 3:
            pts = [(ox + 1, by + bh // 3), (ox + W // 3, by + bh // 2), (ox + W // 2 - 1, by + bh // 3 + 1), (ox + W - 3, by + bh - 2)]
            d.line(pts, fill=_c(STEEL['c']), width=1)
    elif state == 4:
        half = W // 2
        d.rounded_rectangle([ox - 1, by + 1, ox + half - 2, oy + H], radius=1, fill=_c(STEEL['s']))
        d.rounded_rectangle([ox + half + 1, by - 1, ox + W, oy + H - 2], radius=1, fill=_c(STEEL['s']))
        d.line([(ox - 1, by + 1), (ox + half - 2, by + 1)], fill=_c(STEEL['S']))
        d.line([(ox + half + 1, by - 1), (ox + W, by - 1)], fill=_c(STEEL['S']))
    else:
        n = 6 if state == 5 else 4
        rng = np.random.RandomState(W * 10 + state)
        for i in range(n):
            x = ox + int(rng.uniform(-2, W + 1))
            y = by + int(rng.uniform(-3 if state == 5 else 2, bh))
            s = 2 if state == 5 else 1
            d.polygon([(x, y), (x + s, y - s // 2), (x + s, y + s)], fill=_c(STEEL['S'] if i % 2 else STEEL['s']))
    return im


def prop_locks():
    out = {}
    for pid, W in (('lock_s', 9), ('lock_m', 11), ('lock_l', 14)):
        PR.save(pid, [lock_img(W, k) for k in range(7)], fps=10, kind='static')
        out[pid] = PR.PROPS[pid]
    return out


def prop_bike_koichi():
    PR.save('bike_koichi', [PR.bike_img('#d63438', basket=False), PR.bike_fallen('#d63438')])
    return PR.PROPS['bike_koichi']


def prop_paper_bag():
    """纸袋：0 立着 / 1 被压扁、底下渗出黑墨水"""
    a, d = _cv(10, 12)
    d.polygon([(1, 2), (8, 2), (9, 11), (0, 11)], fill=_c('#d6b07a'))
    d.line([(1, 2), (8, 2)], fill=_c('#ad8650'))
    d.polygon([(2, 0), (7, 0), (8, 2), (1, 2)], fill=_c('#c49a62'))
    d.line([(6, 4), (7, 10)], fill=_c('#ad8650'))
    d.line([(2, 5), (4, 5)], fill=_c('#8a6236'))
    b, d = _cv(16, 6)
    d.ellipse([0, 2, 15, 5], fill=_c('#16141c'))
    d.point((4, 3), fill=_c('#3c3a4c'))
    d.polygon([(2, 1), (12, 0), (13, 3), (3, 4)], fill=_c('#c49a62'))
    d.line([(3, 2), (11, 1)], fill=_c('#8a6236'))
    d.point((9, 3), fill=_c('#16141c'))
    PR.save('paper_bag', [a, b])
    return PR.PROPS['paper_bag']


def prop_ink():
    """墨水：小 / 中 / 大（一点点洇开）"""
    frs = []
    for w in (6, 11, 16):
        im, d = _cv(w, 4)
        d.ellipse([0, 0, w - 1, 3], fill=_c('#16141c'))
        d.point((w // 3, 1), fill=_c('#3c3a4c'))
        frs.append(im)
    PR.save('ink', frs, outline=False)
    return PR.PROPS['ink']


def prop_toy_cat():
    """玩具猫：白底灰斑的布偶，湿了（颜色暗一点、身上一道墨迹）"""
    im = PR.grid(["..g.....g.",
                  ".gWg...gWg",
                  ".WWWWWWWWW",
                  ".WkWWWWkWW",
                  ".WWWpWWWWw",
                  "..WWwWWWw.",
                  ".wWWWggWWw",
                  ".WWgggWWWw",
                  "..ww..ww.."], dict(W='#dcd6cc', w='#a8a196', g='#8c8a94', k='#1a1020', p='#e88aa0'))
    a = np.array(im)
    a[6, 3] = (22, 20, 28, 255)
    a[7, 2] = (22, 20, 28, 255)
    PR.save('toy_cat', [Image.fromarray(a, 'RGBA')])
    return PR.PROPS['toy_cat']


def prop_small():
    out = {}
    wallet = PR.grid(["LLLLLLL",
                      "LlllllL",
                      "LltttlL",
                      "LLLLLLL"], dict(L='#6e4226', l='#9a6438', t='#e8c890'))
    photo = PR.grid(["wwwwwwwwwww",
                     "wpppppppppw",
                     "wpppkkppppw",
                     "wpppkfkpppw",
                     "wppptttpppw",
                     "wpptttttppw",
                     "wpptttttppw",
                     "wwwwwwwwwww"], dict(w='#f4f2ea', p='#b8c4cc', k='#24202c', f='#f6dccb', t='#2c9a98'))
    pen = PR.grid(["kBBBBBBbw"], dict(k='#1a1a24', B='#3a64c8', b='#8ab0f0', w='#d8d8e0'))
    cutter = PR.grid(["YYYYyss",
                      "YyyyySS"], dict(Y='#f0c830', y='#b8901a', s='#e8eef4', S='#a8b4c0'))
    bottle = PR.grid([".kk.",
                      ".YY.",
                      ".YY.",
                      "YYhY",
                      "YyhY",
                      "YwwY",
                      "YrwY",
                      "YwwY",
                      "YyyY",
                      "YyyY"], dict(k='#3a2a22', Y='#9a6430', y='#7a4a20', h='#f0d8a8', w='#e8e0c8', r='#d83a3a'))
    shard = [PR.grid([".c", "cC"], dict(c='#d8f0f0', C='#8ab8c0')), PR.grid(["C.", "cc"], dict(c='#ffffff', C='#8ab8c0'))]
    phone = PR.grid([".GGGGGG.",
                     "GgggggGG",
                     "GkkkkkgG",
                     "GgwgwggG",
                     "GgwgwggG",
                     "GgwgwggG",
                     "GGGGGGGG",
                     "GgggggGG",
                     "GGGGGGGG",
                     "...ss...",
                     "...ss...",
                     "...ss...",
                     "...ss...",
                     "...ss...",
                     "..ssss..",
                     ".ssssss."], dict(G='#2e9a5e', g='#5ad08a', k='#1a1a24', w='#e8f4ec', s='#8a8e9a'))
    for pid, frs in (('wallet', [wallet]), ('photo_hz', [photo]), ('pen', [pen]), ('cutter', [cutter]), ('bottle', [bottle]),
                     ('glass_shard', shard), ('payphone', [phone])):
        PR.save(pid, frs, fps=6, kind='loop' if len(frs) > 1 else 'static')
        out[pid] = PR.PROPS[pid]
    return out


def motorbike_img(tank, tank_d, stain=False):
    im, d = _cv(34, 20)
    for wx in (6, 27):
        d.ellipse([wx - 6, 8, wx + 6, 19], fill=_c('#18161e'))
        d.ellipse([wx - 3, 11, wx + 3, 16], fill=_c('#9aa0b0'))
        d.point((wx, 13), fill=_c('#d8dce6'))
    d.polygon([(8, 10), (24, 10), (27, 13), (8, 14)], fill=_c('#3a3844'))        # 车架和引擎
    d.rectangle([12, 12, 20, 15], fill=_c('#9aa0b0'))
    d.line([(12, 15), (20, 15)], fill=_c('#5a5e6c'))
    d.polygon([(14, 6), (22, 6), (24, 10), (13, 10)], fill=_c(tank))            # 油箱
    d.line([(15, 7), (21, 7)], fill=_c('#ffffff'))
    d.line([(13, 10), (24, 10)], fill=_c(tank_d))
    d.rectangle([4, 7, 13, 9], fill=_c('#2a2030'))                               # 座
    d.line([(3, 1), (3, 8)], fill=_c('#d8dce6'))                                 # 靠背杆（暴走族的高靠背）
    d.line([(1, 1), (5, 1)], fill=_c('#d8dce6'))
    d.line([(24, 6), (26, 1)], fill=_c('#d8dce6'))                               # 竖起来的车把
    d.line([(25, 1), (29, 1)], fill=_c('#d8dce6'))
    d.line([(24, 9), (27, 13)], fill=_c('#9aa0b0'))                              # 前叉
    d.rectangle([28, 4, 30, 6], fill=_c('#fff0a0'))                              # 车灯
    d.line([(2, 13), (8, 12)], fill=_c('#c8ccd6'))                               # 排气管
    if stain:
        d.ellipse([5, 6, 12, 8], fill=_c('#7a4a1e'))
        d.point((7, 6), fill=_c('#c08040'))
        d.point((10, 9), fill=_c('#7a4a1e'))
    return im


def prop_motorbikes():
    out = {}
    for pid, t, td in (('motorbike_a', '#f4f4f0', '#c83030'), ('motorbike_b', '#5a3a8a', '#2a1a48')):
        PR.save(pid, [motorbike_img(t, td), motorbike_img(t, td, True)])
        out[pid] = PR.PROPS[pid]
    return out


def ambulance_img(flash):
    im, d = _cv(52, 26)
    d.rectangle([2, 6, 50, 21], fill=_c('#f6f6f2'))
    d.polygon([(38, 6), (46, 6), (51, 13), (51, 21), (38, 21)], fill=_c('#f6f6f2'))
    d.polygon([(40, 8), (45, 8), (49, 13), (40, 13)], fill=_c('#7aa8d0'))        # 前窗
    d.rectangle([28, 8, 35, 13], fill=_c('#7aa8d0'))
    d.line([(2, 16), (51, 16)], fill=_c('#d83a3a'))
    d.line([(2, 17), (51, 17)], fill=_c('#d83a3a'))
    d.rectangle([12, 8, 14, 14], fill=_c('#d83a3a'))                              # 红十字
    d.rectangle([10, 10, 16, 12], fill=_c('#d83a3a'))
    d.line([(2, 21), (51, 21)], fill=_c('#c8ccd2'))
    for wx in (11, 42):
        d.ellipse([wx - 4, 18, wx + 4, 25], fill=_c('#18161e'))
        d.ellipse([wx - 2, 20, wx + 2, 23], fill=_c('#9aa0b0'))
    d.rectangle([20, 3, 30, 5], fill=_c('#ff4a4a' if flash else '#8a2020'))      # 警灯
    d.rectangle([22, 3, 23, 4], fill=_c('#ffffff' if flash else '#c04040'))
    return im


def prop_ambulance():
    PR.save('ambulance', [ambulance_img(True), ambulance_img(False)], fps=4, kind='loop')
    return PR.PROPS['ambulance']


def prop_wire_glow():
    """电线上的发光小影子（辣妹的剪影，第4章前只给剪影）：两帧一闪"""
    frs = []
    for k in (0, 1):
        im, d = _cv(12, 10)
        glow = '#e8ff7a' if k else '#c8e050'
        d.ellipse([1, 1, 10, 9], fill=(232, 255, 122, 70 if k else 40))
        d.polygon([(4, 3), (7, 2), (8, 4), (7, 7), (5, 8), (3, 6)], fill=_c(glow))
        d.point((7, 1), fill=_c(glow))
        d.point((8, 2), fill=_c(glow))
        d.point((6, 4), fill=_c('#ffffff' if k else '#fff8c0'))
        frs.append(im)
    PR.save('wire_glow', frs, fps=3, kind='loop', outline=False)
    return PR.PROPS['wire_glow']


PROP_BUILDERS.update({'locks': prop_locks, 'bike_koichi': prop_bike_koichi, 'paper_bag': prop_paper_bag, 'ink': prop_ink,
                  'toy_cat': prop_toy_cat, 'small': prop_small, 'motorbikes': prop_motorbikes, 'ambulance': prop_ambulance,
                  'wire_glow': prop_wire_glow})


# ============================================================ UI（名牌、替身卡、必杀切入字，写 _meta/ui_ch2.json）
def ui_ch2():
    UI.chapter_ui('ch2',
                  namecards={'okuyasu': UI.namecard('okuyasu', '虹村亿泰', '#3a5ab0', '葡萄丘高中一年级｜脑子转得慢，讲义气'),
                             'tamami': UI.namecard('tamami', '小林玉美', '#6a74c0', '自称“正义的使者”｜专挑软柿子敲诈'),
                             'hazamada': UI.namecard('hazamada', '间田敏和', '#2a9a98', '葡萄丘高中三年级｜跟谁都合不来')},
                  standcards={'thehand': UI.standcard('thehand', '『轰炸空间』', 'THE HAND', ('#eef4ff', '#8cb6ff'), '#a8c8ff', '#0a1430'),
                              'echoes1': UI.standcard('echoes1', '『回音』', 'ECHOES ACT1', ('#e8fff0', '#7ce0a6'), '#a0f0c8', '#08261a'),
                              'thelock': UI.standcard('thelock', '『锁』', 'THE LOCK', ('#f2f4fa', '#a8b0c8'), '#c8d0e8', '#10121e'),
                              'surface': UI.standcard('surface', '『表面』', 'SURFACE', ('#fff4e0', '#e0b070'), '#e8c890', '#241608')},
                  specials={'okuyasu': UI.save('special/okuyasu', UI.big('轰炸空间！', 42, ('#f4f8ff', '#9cc0ff', '#3a6ae0'),
                                                                         edge='#0a1438', shadow='#04081a', edge_w=3, shadow_d=(3, 3))),
                            'koichi': UI.save('special/koichi', UI.big('回音！', 42, ('#f0fff4', '#90f0b8', '#28b070'),
                                                                     edge='#06281a', shadow='#02120a', edge_w=3, shadow_d=(3, 3)))},
                  locations={'hirose': UI.location('hirose', '广濑家', 'HIROSE RESIDENCE · 杜王町'),
                             'grand_hotel': UI.location('grand_hotel', '杜王大酒店', 'MORIOH GRAND HOTEL · 杜王町'),
                             'shopping': UI.location('shopping', '商店街', 'SHOPPING STREET · 杜王町')},
                  vs={'thelock': UI.vs_card('thelock', '锁', 'THE LOCK', 'VS 小林玉美 / 杜王町·广濑家', ('#f4f6ff', '#b0b8d8', '#6a74c0'),
                                            '#8a94d0', ['#2a2e5a', '#10122a']),
                      'surface': UI.vs_card('surface', '表面', 'SURFACE', 'VS 间田敏和 / 葡萄丘高中·走廊', ('#fff4e0', '#e8b878', '#a8783c'),
                                            '#d0a060', ['#5a3a18', '#24160a'])},
                  sfx=echo_words())


# 回音贴的拟声字（贴纸样式：绿字、深绿描边、外面再一圈白边）。J 射出去的弹体就是这几张图，word() 也能直接用
ECHO_WORDS = ['咚！', '嗡——', '叮铃铃', '啪！']
# 剧情里康一贴的几句（第3战收尾、第4战段 A 的笔、段 B 的蛋糕店和道口）：同样的贴纸样式
ECHO_EXTRA = {'puchi': '噗嗤', 'trust': '相信我！', 'here': '仗助君在这边～', 'bell': '当当当当'}


def echo_sticker(w, size=18):
    im = UI.big(w, size, ('#f4fff6', '#9cf0c0', '#3cc884'), edge='#06281a', shadow=None, edge_w=2)
    pad = Image.new('RGBA', (im.width + 2, im.height + 2), (0, 0, 0, 0))
    pad.alpha_composite(im, (1, 1))
    a = np.array(pad)
    op = a[..., 3] > 0
    ring = np.zeros_like(op)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ring |= np.roll(np.roll(op, dy, 0), dx, 1)
    a[ring & ~op] = (250, 255, 250, 255)
    return Image.fromarray(a, 'RGBA')


def echo_words():
    out = {}
    for i, w in enumerate(ECHO_WORDS):
        out[w] = UI.save('sfx/echo_%d' % i, echo_sticker(w))
    for k, w in ECHO_EXTRA.items():
        out[w] = UI.save('sfx/echo_' + k, echo_sticker(w, 16 if len(w) > 4 else 18))
    return out


# ============================================================ 预览
def preview(cids):
    D = os.path.join(L.ASSETS, 'preview')
    os.makedirs(D, exist_ok=True)
    rows = []
    for cid in cids:
        full = Image.open(os.path.join(L.ASSETS, 'chars_full', cid + '.png')).convert('RGBA')
        small = Image.open(os.path.join(L.ASSETS, 'chars', cid + '.png')).convert('RGBA')
        rows.append((full, small))
    W = max(max(f.width, s.width * 2) for f, s in rows) + 8
    H = sum(f.height + s.height * 2 + 12 for f, s in rows)
    can = Image.new('RGBA', (W, H), (116, 132, 116, 255))
    y = 0
    for f, s in rows:
        can.alpha_composite(f, (4, y))
        y += f.height + 4
        can.alpha_composite(s.resize((s.width * 2, s.height * 2), Image.NEAREST), (4, y))
        y += s.height * 2 + 8
    can = can.resize((can.width * 3, can.height * 3), Image.NEAREST)
    can.save(os.path.join(D, 'ch2_chars.png'))


BUILDERS = {
    'okuyasu': build_okuyasu,
    'thehand': build_thehand,
    'echoes1': build_echoes1,
    'tamami': build_tamami,
    'hazamada': build_hazamada,
    'surface_doll': build_surface_doll,
    'surface': build_surface,
    'surface_cut': build_surface_cut,
    'hirose_mom': build_hirose_mom,
    'ayana': build_ayana,
    'biker_a': build_biker_a,
    'biker_b': build_biker_b,
    'yukako_sil': build_yukako_sil,
    'koichi_bike': build_koichi_bike,
    # 康一补动作：条目写在 koichi 名下（深合并盖掉 chars.json 里的图和动作表，头像不动）
    'koichi_ex': build_koichi_ex,
}
SAVE_AS = {'koichi_ex': 'koichi'}


def main(ids):
    path = os.path.join(L.META, 'chars_ch2.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    chars = [i for i in (ids or BUILDERS) if i in BUILDERS]
    for cid in chars:
        key = SAVE_AS.get(cid, cid)
        meta['chars'][key] = BUILDERS[cid]()
        e = meta['chars'][key]
        print('角色', cid, e['cell'], '动作', len(e['animations']), '表情', list(e.get('heads') or {}))
    meta['heroes'], meta['speakers'], meta['stands'] = HEROES, SPEAKERS, STANDS
    L.save_json(path, meta)
    props = [i for i in (ids or PROP_BUILDERS) if i in PROP_BUILDERS]
    if props:
        ppath = os.path.join(L.META, 'props_ch2.json')
        pm = L.load_json(ppath, {}) or {}
        pm.setdefault('props', {})
        for pid in props:
            r = PROP_BUILDERS[pid]()
            got = {pid: r} if 'image' in r else r
            pm['props'].update(got)
            for k, v in got.items():
                print('道具', k, v['frames'], '帧', v['size'])
        L.save_json(ppath, pm)
    if not ids or 'ui' in ids:
        ui_ch2()
        print('UI：第2章名牌、替身卡、必杀字')
    if chars:
        preview([c for c in chars if c not in SAVE_AS] + [c for c in chars if c in SAVE_AS])


if __name__ == '__main__':
    main(sys.argv[1:])
