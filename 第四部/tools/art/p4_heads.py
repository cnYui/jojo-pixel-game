# 第四部的说话头像（32×32，不缩小）：拿第三部同一个底子的头像改。表情只做 normal / smile / rage / shock 四种，
#   每种 2 帧（0 闭嘴、1 张嘴，对话框打字时来回切）。
import numpy as np
from PIL import Image

import p4_chars as C


def shift(img, dx, dy):
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.alpha_composite(img, (dx, dy)) if dx >= 0 and dy >= 0 else out.paste(img, (dx, dy), img)
    return out


def edit(img, pix):
    """pix = {(x, y): 颜色或 None}"""
    a = np.array(img.convert('RGBA'))
    for (x, y), c in pix.items():
        if 0 <= x < a.shape[1] and 0 <= y < a.shape[0]:
            a[y, x] = (0, 0, 0, 0) if c is None else (*C.rgb(c), 255)
    return Image.fromarray(a, 'RGBA')


SK, SK2 = (246, 196, 154), (216, 148, 108)
MOUTH = (138, 90, 52)
RED = (120, 24, 40)
WHITE = (255, 255, 255)


def josuke():
    """仗助的头像：承太郎头像的脸往下挪 3 行，上面 13 行全给飞机头（手调的椭圆 + 明暗带，不是从帽子改）"""
    hd = C.heads('jotaro')
    out = {}
    nm = [josuke_portrait(f) for f in hd['portrait']]
    rg = [josuke_portrait(f, angry=True) for f in hd['portrait_angry']]
    out['normal'] = nm
    out['rage'] = rg
    out['smile'] = [josuke_smile(f) for f in nm]
    out['shock'] = [josuke_shock(f, i) for i, f in enumerate(nm)]
    return out


JP = dict(K=(18, 14, 26), k=(34, 28, 50), h=(56, 48, 84), H=(92, 84, 136), W=(146, 138, 196))
JEYE = (92, 94, 224)          # 仗助的眼睛：蓝紫


def josuke_portrait(f, angry=False):
    D = 3                     # 脸往下挪 3 行
    a0 = np.array(f.convert('RGBA'))
    a = np.zeros_like(a0)
    a[D:, :] = a0[:-D, :]
    H, W = a.shape[:2]
    col = lambda c: (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    navy1, navy2, back = (43, 49, 96), (84, 98, 168), (24, 26, 56)
    # 旧帽子侧面、后面的长发去掉（领子留着：只动脸那几行）
    head_rows = yy < 10 + D + 4
    for c in (navy1, navy2, back):
        a[col(c) & head_rows] = 0
    a[col(back)] = 0
    a[col(C.O) & (yy < 10 + D) ] = 0
    a[col(C.O) & (xx < 9) & (yy < 21 + D)] = 0
    # 帽檐阴影（额头那一行深肤色）换回正常肤色
    sk2 = col((216, 148, 108)) & (yy == 10 + D) & (xx > 10)
    a[sk2] = (*SK, 255)
    # 眼睛换成蓝紫
    a[col((44, 196, 168))] = (*JEYE, 255)
    # 头发形状
    ang = np.deg2rad(-9)
    cx, cy = 20.0, 6.6
    u = ((xx - cx) * np.cos(ang) + (yy - cy) * np.sin(ang)) / 12.2
    v = (-(xx - cx) * np.sin(ang) + (yy - cy) * np.cos(ang)) / 5.4
    roll = u * u + v * v <= 1
    curl = (xx - 29.0) ** 2 + (yy - 4.2) ** 2 <= 2.7 ** 2
    skull = ((xx - 8.5) / 9.0) ** 2 + ((yy - 11.0) / 8.6) ** 2 <= 1
    skull &= ~((yy > 12 + D - 1) & (xx > 10.5))
    skull &= yy <= 19.5 + D
    side = (xx >= 8) & (xx <= 10) & (yy >= 10 + D) & (yy <= 13 + D)
    hair = roll | curl | skull | side
    face = col(SK) | col((216, 148, 108)) | col((239, 230, 210)) | col(JEYE) | col((255, 255, 255)) | col((110, 62, 36)) | col((144, 24, 40))
    lash = col(C.O) & (yy >= 10 + D) & (yy <= 13 + D) & (xx >= 13)
    hair &= ~(face & (yy >= 10 + D)) & ~lash
    # 明暗
    shade = np.full((H, W), 'h', object)
    rv = v
    shade[roll & (rv < -0.58) & (u > -0.75) & (u < 0.82)] = 'W'
    shade[roll & (rv >= -0.58) & (rv < -0.12)] = 'H'
    shade[roll & (rv >= 0.38) & (rv < 0.72)] = 'k'
    shade[roll & (rv >= 0.72)] = 'K'
    shade[curl & ~roll] = 'H'
    shade[curl & (yy < 3.2)] = 'W'
    sk_only = skull & ~roll & ~curl
    shade[sk_only] = 'k'
    shade[sk_only & (((xx - 8.5) / 9.0) ** 2 + ((yy - 10.0) / 8.6) ** 2 > 0.62) & (yy < 12)] = 'h'
    shade[sk_only & (yy > 15 + D - 3)] = 'K'
    shade[side] = 'K'
    # 卷和后脑之间的那道缝：贴着卷后沿的后脑像素压暗
    rim = np.zeros_like(roll)
    rim[:, 1:] |= roll[:, :-1]
    shade[sk_only & ~roll & np.roll(roll, -1, axis=1)] = 'K'
    # 梳出来的发丝：卷上两道弧线
    for off in (0.05, 0.42):
        line = roll & (np.abs(rv - off) < 0.09) & (u > -0.55) & (u < 0.6)
        shade[line & (shade != 'W')] = 'k'
    for k_, c in JP.items():
        a[hair & (shade == k_)] = (*c, 255)
    img = Image.fromarray(a, 'RGBA')
    img = C.reoutline(img)
    b = np.array(img)
    # 额头和发际线之间描一道（只在卷的下沿）
    hb = hair.copy()
    edge = np.zeros_like(hb)
    edge[1:, :] = hb[:-1, :] & ~hb[1:, :]
    fc = (b[..., 0] == SK[0]) & (b[..., 1] == SK[1]) & (b[..., 2] == SK[2])
    b[edge & fc & (yy <= 10 + D)] = (*C.O, 255)
    # 眉毛（不生气时）：粗、平
    if not angry:
        for x in range(14, 20):
            b[10 + D, x] = (*C.O, 255)
        for x in range(23, 28):
            b[10 + D, x] = (*C.O, 255)
    img = Image.fromarray(b, 'RGBA')
    # 领口：金链换心形徽章
    img = C.recolor(img, {(255, 216, 60): C.JOSUKE_COAT[(43, 49, 96)], (200, 154, 32): C.JOSUKE_COAT[(24, 26, 56)]}, (20, 22, 32, 32))
    img = C.recolor(img, C.JOSUKE_COAT)
    img = C.heart_badge(img, 24, 27)
    img = C.put(img, [(25, 27)], (255, 140, 190))
    return img


def josuke_smile(f):
    y = 18 + 3
    pix = {(x, y): SK for x in range(17, 23)}
    pix.update({(18, y): MOUTH, (19, y): MOUTH, (20, y): MOUTH, (21, y): MOUTH, (17, y - 1): MOUTH, (22, y - 1): MOUTH})
    # 眼睛下半行换成皮肤：笑起来眯一点
    a = np.array(f.convert('RGBA'))
    for x in range(15, 29):
        c = tuple(a[13 + 3, x][:3])
        if c in ((239, 230, 210), JEYE, (255, 255, 255)):
            pix[(x, 13 + 3)] = SK
    return edit(f, pix)


def josuke_shock(f, i):
    a = np.array(f.convert('RGBA'))
    eye = (a[..., 0] == JEYE[0]) & (a[..., 1] == JEYE[1]) & (a[..., 2] == JEYE[2])
    ys, xs = np.where(eye)
    a[eye] = (*WHITE, 255)
    for side in (xs < 22, xs >= 22):
        if side.any():
            a[int(round(ys[side].mean())), int(round(xs[side].mean()))] = (*C.O, 255)
    f = Image.fromarray(a, 'RGBA')
    y = 18 + 3
    pix = {(x, y): SK for x in range(17, 23)}
    pix.update({(18, y): C.O, (19, y): C.O, (20, y): C.O, (18, y + 1): C.O, (19, y + 1): RED, (20, y + 1): C.O, (19, y + 2): C.O})
    if i == 1:
        pix.update({(17, y + 1): C.O, (21, y + 1): C.O, (18, y + 1): RED, (20, y + 1): RED, (18, y + 2): C.O, (20, y + 2): C.O})
    # 汗
    pix.update({(29, 15): (180, 220, 255), (29, 16): (120, 180, 240), (30, 16): C.O, (28, 16): C.O, (29, 17): C.O})
    return edit(f, pix)


def find(img, color):
    a = np.array(img.convert('RGBA'))
    c = C.rgb(color)
    ys, xs = np.where((a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0))
    return list(zip(xs.tolist(), ys.tolist()))


def smile(f):
    """笑：嘴角往上翘（嘴那一行两头抬一格），眼睛眯一点（眼白最下一行换成皮肤）"""
    pts = find(f, MOUTH)
    if pts:
        xs = sorted(set(x for x, _ in pts))
        y = max(y for _, y in pts)
        pix = {(x, y): SK for x in xs}
        pix.update({(xs[0], y - 1): MOUTH, (xs[-1], y - 1): MOUTH})
        pix.update({(x, y): MOUTH for x in xs[1:-1]})
        f = edit(f, pix)
    return f


def shock(f, i):
    """吃惊：瞳孔缩成小点（青色换成眼白）、嘴张开"""
    a = np.array(f.convert('RGBA'))
    teal = (a[..., 0] == 44) & (a[..., 1] == 196) & (a[..., 2] == 168)
    ys, xs = np.where(teal)
    a[teal] = (*WHITE, 255)
    # 每只眼留一个深色小瞳孔
    if len(xs):
        for side in (xs < 22, xs >= 22):
            if side.any():
                cx, cy = int(np.round(xs[side].mean())), int(np.round(ys[side].mean()))
                a[cy, cx] = (*C.O, 255)
    f = Image.fromarray(a, 'RGBA')
    pts = find(f, MOUTH)
    if pts:
        xs2 = sorted(set(x for x, _ in pts))
        y = max(y for _, y in pts)
        mid = (xs2[0] + xs2[-1]) // 2
        pix = {(x, y): SK for x in xs2}
        pix.update({(mid - 1, y): C.O, (mid, y): C.O, (mid + 1, y): C.O, (mid - 1, y + 1): C.O, (mid, y + 1): RED, (mid + 1, y + 1): C.O,
                    (mid, y + 2): C.O})
        if i == 1:
            pix.update({(mid, y + 1): RED, (mid - 1, y + 2): C.O, (mid + 1, y + 2): C.O, (mid, y + 2): RED, (mid, y + 3): C.O})
        f = edit(f, pix)
    return f


def jotaro4():
    hd = C.heads('jotaro')
    nm = [C.jotaro4_body(f) for f in hd['portrait']]
    rg = [C.jotaro4_body(f) for f in hd['portrait_angry']]
    return {'normal': nm, 'rage': rg, 'smile': [smile(f) for f in nm], 'shock': [shock(f, i) for i, f in enumerate(nm)]}
