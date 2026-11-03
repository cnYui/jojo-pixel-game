# 第四部第2章的新角色、替身和道具（第四部/docs/第2章_开发脚本.md 第四节素材清单）。
#   亿泰 / 轰炸空间、回音的蛋第1章也要用：按分章开发约定第 5 节，后面几章反复出现的人由第2章画，第1章直接借用。
#   画法和序章一样：拿第三部的全尺寸图集改发型、换配色（p4_chars 里的工具），再用第三部 shrink.py 缩成游戏尺寸；
#   配色照 TV 动画第四部（用户认定的“官方形象”，见 p4_chars 开头的说明和 PR #6）。
#   只写自己的元数据文件：_meta/chars_ch2.json、props_ch2.json、ui_ch2.json（build_p4.py 自动合并），不动 chars.json。
#   用法：python3 第四部/tools/art/p4_chars_ch2.py [okuyasu thehand echoes_egg …]   不写 = 全部
import os
import sys

import numpy as np
from PIL import Image

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
}
STANDS = {
    'thehand': dict(cn='轰炸空间', en='THE HAND', owner='okuyasu', aura='#78a6ff', card='#a8c8ff', ghost='#d0e0ff', impact='blue',
                    kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx='stand_summon_star', fist=True),
    # ACT1 个子小，浮在康一肩膀后面（z 高一点），没有拳头：连打特效不用
    'echoes1': dict(cn='回音 ACT1', en='ECHOES ACT1', owner='koichi', aura='#60e0a0', card='#a0f0c8', ghost='#d0ffe4', impact='green',
                    kind='humanoid', idle={'dx': -10, 'z': 14}, link=None, summonSfx='stand_summon_star', fist=False),
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


# ============================================================ UI（名牌、替身卡、必杀切入字，写 _meta/ui_ch2.json）
def ui_ch2():
    UI.chapter_ui('ch2',
                  namecards={'okuyasu': UI.namecard('okuyasu', '虹村亿泰', '#3a5ab0', '葡萄丘高中一年级｜脑子转得慢，讲义气')},
                  standcards={'thehand': UI.standcard('thehand', '『轰炸空间』', 'THE HAND', ('#eef4ff', '#8cb6ff'), '#a8c8ff', '#0a1430'),
                              'echoes1': UI.standcard('echoes1', '『回音』', 'ECHOES ACT1', ('#e8fff0', '#7ce0a6'), '#a0f0c8', '#08261a')},
                  specials={'okuyasu': UI.save('special/okuyasu', UI.big('轰炸空间！', 42, ('#f4f8ff', '#9cc0ff', '#3a6ae0'),
                                                                         edge='#0a1438', shadow='#04081a', edge_w=3, shadow_d=(3, 3))),
                            'koichi': UI.save('special/koichi', UI.big('回音！', 42, ('#f0fff4', '#90f0b8', '#28b070'),
                                                                     edge='#06281a', shadow='#02120a', edge_w=3, shadow_d=(3, 3)))},
                  sfx=echo_words())


# 回音贴的拟声字（贴纸样式：绿字、深绿描边、外面再一圈白边）。J 射出去的弹体就是这几张图，word() 也能直接用
ECHO_WORDS = ['咚！', '嗡——', '叮铃铃', '啪！']


def echo_words():
    out = {}
    for i, w in enumerate(ECHO_WORDS):
        im = UI.big(w, 18, ('#f4fff6', '#9cf0c0', '#3cc884'), edge='#06281a', shadow=None, edge_w=2)
        pad = Image.new('RGBA', (im.width + 2, im.height + 2), (0, 0, 0, 0))
        pad.alpha_composite(im, (1, 1))
        a = np.array(pad)
        op = a[..., 3] > 0
        ring = np.zeros_like(op)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ring |= np.roll(np.roll(op, dy, 0), dx, 1)
        a[ring & ~op] = (250, 255, 250, 255)
        out[w] = UI.save('sfx/echo_%d' % i, Image.fromarray(a, 'RGBA'))
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
}


def main(ids):
    path = os.path.join(L.META, 'chars_ch2.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    chars = [i for i in (ids or BUILDERS) if i in BUILDERS]
    for cid in chars:
        meta['chars'][cid] = BUILDERS[cid]()
        e = meta['chars'][cid]
        print('角色', cid, e['cell'], '动作', len(e['animations']), '表情', list(e['heads']))
    meta['heroes'], meta['speakers'], meta['stands'] = HEROES, SPEAKERS, STANDS
    L.save_json(path, meta)
    props = [i for i in (ids or PROP_BUILDERS) if i in PROP_BUILDERS]
    if props:
        ppath = os.path.join(L.META, 'props_ch2.json')
        pm = L.load_json(ppath, {}) or {}
        pm.setdefault('props', {})
        for pid in props:
            pm['props'][pid] = PROP_BUILDERS[pid]()
            print('道具', pid, pm['props'][pid]['frames'], '帧')
        L.save_json(ppath, pm)
    if not ids or 'ui' in ids:
        ui_ch2()
        print('UI：第2章名牌、替身卡、必杀字')
    if chars:
        preview(chars)


if __name__ == '__main__':
    main(sys.argv[1:])
