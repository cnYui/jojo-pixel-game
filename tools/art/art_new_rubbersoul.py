"""rubbersoul：独立角色注册，人体关节与绘制工具共用。

黏液铠甲形态（皮肤 armor，2026-10-11）：黄色节制裹在拉巴索身上的一层黄色黏液，拳头打上去被吸收。
  身体就是原来的拉巴索（art_later_people.body 的同一套帧），外面按身体轮廓往外鼓 1–4 px（平滑噪声控制厚薄、
  脸上薄一点）的一层黏液：亮黄底 + 左上亮边 + 右下暗边 + 深黄褐描边（不用纯黑，和人物的黑描边区分开），
  几个白色高光点和气泡（逐帧往上浮），下沿往下滴、脚边一小滩。盖在身上的部分把原来的颜色往黄色混 40%（脸 30%），
  黑描边混成深黄——看起来像隔着一层半透明黄胶，脸还认得出是他。全不透明像素（没有半透明 alpha）。
  armor_idle 2 / armor_walk 4（照原 walk 的步子）/ armor_attack 2（手臂甩出一条黏液鞭：帧 0 往后上方卷起、帧 1 往前抽出去）/
  armor_hurt 1（他本人还是待机姿势、没事，胸前的黏液被打得凹进去一个坑 + 波纹 + 飞溅的黏液点）/
  armor_engulf 2（帧 0 黏液从背后鼓起一大坨举过头顶，帧 1 张开成一大片月牙形往前扑，上下两片之间拉着黏丝、前沿往下滴）。
  这些帧按脚点对齐（anchor 写成脚点坐标），图集 cell 会跟着变大，pivot 仍是脚底。
  原来的 slime_idle / slime_attack（一坨）在 art_later_creatures.py，不动。
"""
import sys
sys.dont_write_bytecode = True
import math
import numpy as np
from PIL import Image, ImageDraw
from art_later_people import register, PEOPLE, body
from engine import sprite

NEW = register('rubbersoul',{'idle':2,'walk':4,'talk':2,'hurt':1,'down':1,'portrait':2,'beg':1})

# ============================================================================ 黏液铠甲
CID = 'rubbersoul'
ARMOR = {'armor_idle': 2, 'armor_walk': 4, 'armor_attack': 2, 'armor_hurt': 1, 'armor_engulf': 2}
ARMOR_FPS = {'armor_idle': 3, 'armor_walk': 6, 'armor_attack': 6, 'armor_hurt': 1, 'armor_engulf': 4}

K = (20, 18, 30)
SL = (240, 206, 52)           # 黏液主色
SL_L = (255, 234, 112)        # 亮边
SL_H = (255, 252, 216)        # 高光 / 气泡
SL_D = (200, 152, 26)         # 暗边
SL_O = (120, 80, 16)          # 描边（深黄褐）
BODY_W, BODY_H = 36, 48       # art_later_people.body 的帧尺寸（mb 锚点 = (18, 48)）
HEAD_ROWS = 21                # 帧里头部占的行数（hh）

# 工作画布：脚点 (PX, GY)；所有铠甲帧画完后统一按并集裁剪 → 同一块画布、同一个脚点
WC, HC, PX, GY = 124, 90, 46, 84
_gy, _gx = np.mgrid[0:HC, 0:WC]


def _noise(seed, sx=.55, sy=.42):
    """平滑噪声 [0, 1]：几组正弦叠加（固定，每次烘出来一样）。"""
    n = (np.sin(_gx * sx + seed * 1.3) + np.sin(_gy * sy + seed * 2.1)
         + np.sin((_gx + _gy) * .37 + seed * .7) + np.sin((_gx - _gy) * .29 - seed))
    return (n + 4) / 8


def _dist(mask):
    """每个像素到 mask 的欧氏距离（numpy 暴力，画布小）。"""
    ys, xs = np.nonzero(mask)
    d = np.full((HC, WC), 1e9, np.float32)
    for k in range(0, len(xs), 192):
        dx = _gx[..., None] - xs[None, None, k:k + 192]
        dy = _gy[..., None] - ys[None, None, k:k + 192]
        d = np.minimum(d, np.sqrt(dx * dx + dy * dy).min(-1))
    return d


def _shift(m, dx, dy):
    out = np.zeros_like(m)
    ys0, ys1 = max(0, dy), min(HC, HC + dy)
    xs0, xs1 = max(0, dx), min(WC, WC + dx)
    out[ys0:ys1, xs0:xs1] = m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def _ring(m):
    return (_shift(m, 1, 0) | _shift(m, -1, 0) | _shift(m, 0, 1) | _shift(m, 0, -1)) & ~m


def _disk(cx, cy, r):
    return (_gx - cx) ** 2 + (_gy - cy) ** 2 <= r * r


def _tube(pts, r0, r1, tip=0):
    """沿折线画一条由粗到细的黏液管（鞭子 / 黏丝）；tip>0 时尾端一个圆球。"""
    m = np.zeros((HC, WC), bool)
    dense = []                                   # 点之间按 0.5 px 加密，细管也不断
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(xb - xa, yb - ya) * 2))
        dense += [(xa + (xb - xa) * t / n, ya + (yb - ya) * t / n) for t in range(n)]
    dense.append(pts[-1])
    n = len(dense)
    for k, (x, y) in enumerate(dense):
        m |= _disk(x, y, r0 + (r1 - r0) * k / max(1, n - 1))
    if tip:
        m |= _disk(pts[-1][0], pts[-1][1], tip)
    return m


def _bezier(p0, p1, p2, n=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]


def _h(*a):
    """确定性整数哈希（挑滴落 / 高光的位置）。"""
    v = 2166136261
    for x in a:
        v = ((v ^ (int(x) & 0xffffffff)) * 16777619) & 0xffffffff
    return v


def _base(action, fi):
    """原来的拉巴索那一帧，按脚点贴到工作画布上。"""
    im = Image.new('RGBA', (WC, HC))
    im.alpha_composite(body(CID, action, fi), (PX - BODY_W // 2, GY - BODY_H))
    return im


def _slime(base, seed, extra=None, dent=None, thick=1.0, drips=True, puddle=True, bubbles=3):
    """base（人）外面裹一层黏液。extra = 额外并进来的黏液形状（鞭子、大片）；dent = (cx, cy, r) 被打凹的坑。"""
    a = np.array(base)
    bodyA = a[..., 3] > 0
    head_top = GY - BODY_H
    d = _dist(bodyA)
    nz = _noise(seed)
    r = (2.4 + 2.8 * nz) * thick
    r = np.where(_gy < head_top + HEAD_ROWS - 4, 1.4 + 1.6 * nz, r)         # 脸 / 头上薄一点
    E = bodyA | (d <= r)
    if extra is not None:
        E |= extra
    if dent is not None:
        E &= ~_disk(*dent)
    E[GY:, :] = False
    if puddle:                                                               # 脚边一小滩
        feet = np.nonzero(bodyA[GY - 1])[0]
        if len(feet):
            x0, x1 = feet.min() - 6, feet.max() + 7
            E[GY - 1, max(0, x0):x1] = True
            E[GY - 2, max(0, x0 + 2):x1 - 2] = True
    if drips:                                                                # 下沿往下滴：挑几列往下拉 2–5 px，末端一个小球
        bottom = E & ~_shift(E, 0, -1)
        ys, xs = np.nonzero(bottom)
        for y, x in zip(ys, xs):
            sparse = extra is not None and extra[y, x] and d[y, x] > 6     # 鞭子 / 大片上滴得稀一点，不然像一排梳子齿
            if y >= GY - 4 or _h(x, seed) % (11 if sparse else 4):
                continue
            L = 2 + _h(x, y, seed) % 4
            for k in range(1, L + 1):
                if y + k < GY - 1:
                    E[y + k, x] = True
            if y + L < GY - 1:
                E[y + L, x + 1 if _h(x) % 2 else x - 1] = True
    E[GY:, :] = False

    out = np.zeros((HC, WC, 4), np.uint8)
    ringE = E & ~bodyA
    out[ringE] = SL + (255,)
    # 身上：原颜色往黄色混（脸 30%、身子 40%），黑描边混成深黄
    k_head = (_gy < head_top + HEAD_ROWS)
    rgb = a[..., :3].astype(np.float32)
    isK = np.all(a[..., :3] == K, axis=-1)
    amt = np.where(k_head, .30, .40)[..., None]
    tint = rgb * (1 - amt) + np.array(SL, np.float32) * amt
    tint = np.where(isK[..., None], (rgb * .35 + np.array(SL_O, np.float32) * .65), tint)
    out[bodyA, :3] = tint[bodyA].astype(np.uint8)
    out[bodyA, 3] = 255
    # 黏液自己的明暗：右下暗边、左上亮边（只在黏液上，不压人）
    dark_edge = ringE & (~_shift(E, -1, 0) | ~_shift(E, 0, -1))
    lite_edge = ringE & (~_shift(E, 1, 0) | ~_shift(E, 0, 1))
    out[dark_edge, :3] = SL_D
    out[lite_edge & ~dark_edge, :3] = SL_L
    # 高光：左上边缘往里 1 px 隔几个点一个白点
    inner = ringE & ~lite_edge & ~dark_edge & _shift(lite_edge, 1, 1)
    ys, xs = np.nonzero(inner)
    for y, x in zip(ys, xs):
        if _h(x, y, seed) % 4 == 0:
            out[y, x, :3] = SL_H
    # 气泡：黏液里几个小泡（帧之间往上浮）
    ys, xs = np.nonzero(E & _shift(E, 1, 1) & _shift(E, -1, -1) & (_gy < GY - 3))
    if len(xs):
        for b in range(bubbles):
            j = _h(b, 7) % len(xs)
            y, x = ys[j], xs[j]
            y = max(head_top, y - (seed % 4))
            if E[y, x] and E[y + 1, x + 1]:
                out[y, x, :3] = SL_H
                out[y + 1, x + 1, :3] = SL_D
    # 描边：深黄褐
    out[_ring(E), :3] = SL_O
    out[_ring(E), 3] = 255
    out[GY:, :, 3] = 0
    return Image.fromarray(out, 'RGBA'), E


def _hand_pos(fi):
    """art_later_people.body 的 attack 姿势：手在 (w-4, top+2+(fi%2)*7)；换算到工作画布。"""
    top = 21 - 3
    return PX - BODY_W // 2 + BODY_W - 4, GY - BODY_H + top + 2 + (fi % 2) * 7


def armor_frame(act, i):
    if act == 'armor_idle':
        return _slime(_base('idle', i), seed=i * 3)[0]
    if act == 'armor_walk':
        return _slime(_base('walk', i), seed=i * 3 + 1)[0]
    if act == 'armor_hurt':
        # 他本人没事（待机姿势），胸前的黏液被打出一个坑：坑沿亮、波纹两道、往前溅几滴
        cx, cy = PX + 14, GY - BODY_H + 28
        im, E = _slime(_base('idle', 0), seed=5, thick=1.1, dent=(cx, cy, 6.2))
        a = np.array(im)
        for (x, y, r) in ((cx + 8, cy - 7, 1.6), (cx + 11, cy, 1.3), (cx + 8, cy + 6, 1.0), (cx + 14, cy - 4, .8)):
            m = _disk(x, y, r)                               # 往前溅的黏液点：圆点 + 深黄描边 + 左上一个高光
            a[_ring(m) & (a[..., 3] == 0)] = SL_O + (255,)
            a[m] = SL + (255,)
            ys, xs = np.nonzero(m)
            a[ys.min(), xs.min() + (1 if len(xs) > 2 else 0), :3] = SL_H
        rim = E & _ring(_disk(cx, cy, 6.2))
        a[rim, :3] = SL_H
        for rr in (8, 10):                                   # 波纹：坑外两圈亮弧（只画在黏液上）
            arc = E & (np.abs(np.sqrt((_gx - cx) ** 2 + (_gy - cy) ** 2) - rr) < .5) & (_gx < cx) & (a[..., 3] > 0)
            arc &= ~np.all(a[..., :3] == SL_O, axis=-1)
            a[arc, :3] = SL_L
        return Image.fromarray(a, 'RGBA')
    if act == 'armor_attack':
        # 手臂甩出一条黏液鞭：帧 0 往后上方卷起（蓄力），帧 1 往前抽出去（末端一个大球 + 两道速度线）
        hx, hy = _hand_pos(i)
        if i == 0:
            pts = _bezier((hx, hy), (hx + 10, hy - 22), (hx - 10, hy - 20))
            whip = _tube(pts, 2.6, 1.2, tip=2.2)
        else:
            pts = _bezier((hx, hy), (hx + 20, hy - 9), (hx + 40, hy + 1))
            whip = _tube(pts, 2.8, 1.4, tip=3.0)
        im, E = _slime(_base('attack', i), seed=11 + i, extra=whip)
        if i == 1:
            d = ImageDraw.Draw(im)
            for dy, x0, x1 in ((-7, hx + 14, hx + 28), (-4, hx + 22, hx + 36)):
                d.line((x0, hy + dy, x1, hy + dy + 2), fill=SL_H)
        return im
    if act == 'armor_engulf':
        head_top = GY - BODY_H
        if i == 0:
            # 黏液从背后鼓起一大坨，举过头顶、往前探
            blob = _disk(PX - 2, head_top - 6, 12) | _disk(PX + 9, head_top - 10, 10) | _disk(PX - 9, head_top + 6, 8)
            blob |= _tube([(PX - 8, head_top + 18), (PX - 6, head_top + 4), (PX + 2, head_top - 8)], 6, 8)
            im, E = _slime(_base('idle', 0), seed=21, extra=blob, thick=1.4)
            a = np.array(im)                                   # 大坨的“透明”感：左上一道弧形反光 + 中间几个气泡
            rr = np.sqrt((_gx - (PX + 3)) ** 2 + (_gy - (head_top - 8)) ** 2)
            arc = E & (np.abs(rr - 8) < .6) & (_gx < PX + 4) & (_gy < head_top - 6)
            a[arc, :3] = SL_H
            arc2 = E & (np.abs(rr - 6.5) < .5) & (_gx < PX) & (_gy < head_top - 9)
            a[arc2, :3] = SL_L
            for x, y in ((PX + 6, head_top - 14), (PX + 10, head_top - 7), (PX - 3, head_top - 2)):
                a[y, x, :3] = SL_H
                a[y + 1, x + 1, :3] = SL_D
            return Image.fromarray(a, 'RGBA')
        # 帧 1：张开成一大片月牙往前扑：上片从后脑拱到前上方、下片从腰往前伸，中间是空的“嘴”，拉几条黏丝
        upper = _tube(_bezier((PX - 8, head_top + 10), (PX + 6, head_top - 26), (PX + 46, head_top - 8), 30), 6.5, 3.5,
                      tip=4)
        lower = _tube(_bezier((PX + 6, head_top + 30), (PX + 26, head_top + 34), (PX + 44, head_top + 22), 24), 5, 3,
                      tip=3.5)
        strands = np.zeros((HC, WC), bool)
        for x0, top_y, bot_y in ((PX + 30, head_top - 10, head_top + 29), (PX + 39, head_top - 7, head_top + 25)):
            strands |= _tube([(x0, top_y), (x0 + 1, (top_y + bot_y) / 2), (x0, bot_y)], .7, .5)
        im, E = _slime(_base('attack', 0), seed=27, extra=upper | lower | strands, thick=1.3, bubbles=5)
        a = np.array(im)
        inside = (upper | lower) & ~(np.array(_base('attack', 0))[..., 3] > 0)
        # 片的内侧（朝嘴的一面）压暗，看出是凹进去的一张膜
        inner_side = inside & _shift(~E, 0, -2) & (_gy > head_top - 10) & (_gy < head_top + 6)
        a[inner_side & (a[..., 3] > 0), :3] = SL_D
        return Image.fromarray(a, 'RGBA')
    raise ValueError(act)


def _armor_frames():
    frames = {a: [armor_frame(a, i) for i in range(n)] for a, n in ARMOR.items()}
    x0, y0, x1, y1 = WC, HC, 0, 0
    for fs in frames.values():
        for f in fs:
            bb = f.getbbox()
            x0, y0, x1, y1 = min(x0, bb[0]), min(y0, bb[1]), max(x1, bb[2]), max(y1, bb[3])
    assert y1 <= GY and x0 > 0 and y0 > 0 and x1 < WC, f'黏液画出工作画布或画到地面以下：{(x0, y0, x1, y1)}'
    box = (x0, y0, x1, GY)
    return {a: [f.crop(box) for f in fs] for a, fs in frames.items()}, (PX - x0, GY - y0)


def _register_armor():
    frames, anchor = _armor_frames()
    names = []
    for act, fs in frames.items():
        name = CID + '.' + act
        sprite.define(name, fs, anchor=anchor, fps=ARMOR_FPS[act], desc=PEOPLE[CID][0] + '·黏液铠甲：' + act)
        names.append(name)
    return names


NEW += _register_armor()


# ============================================================================ 假花京院（皮肤 fake）
# 花京院是原作角色，不重画：只从原图集的 kakyoin.idle / walk / cherry 复制帧（形状、比例、配色全不动），
#   1) 头部（前 22 行）里的眼白 (255,255,255) → 淡黄、紫色瞳孔 (154,76,224) → 黄色（cherry 两帧是闭眼，没有瞳孔像素）；
#   2) 外套下摆最左、最右两个角的黑描边下面各挂 1–2 px 黄色黏液滴（逐帧 1 px / 2 px 交替，像在往下滴）。
# 存成 kakyoin.fake_idle / fake_walk / fake_cherry（锚点 / 帧率同原动作）。fake_talk 在 amap 里指到 fake_idle
# （原图集也没有 talk 帧，talk 本来就是 idle；帧完全相同会被烘焙去重成别名，amap 不能指别名）。
KAKYOIN_FAKE = {'fake_idle': 'kakyoin.idle', 'fake_walk': 'kakyoin.walk', 'fake_cherry': 'kakyoin.cherry'}
KAK_EYE_W, KAK_EYE_P = (255, 255, 255), (154, 76, 224)
FAKE_EYE_W, FAKE_EYE_P = (255, 244, 168), (236, 196, 24)
KAK_K = (26, 16, 32)            # 原工程描边色（art_common.OUTLINE_RGB）
KAK_COAT = {(47, 158, 86), (26, 96, 56), (98, 200, 116), (15, 64, 40), (255, 216, 60), (200, 154, 32)}


def fake_kakyoin(frame, fi):
    a = np.array(frame.convert('RGBA'))
    head = np.zeros(a.shape[:2], bool)
    head[:22] = True
    op = a[..., 3] > 0
    for src, dst in ((KAK_EYE_W, FAKE_EYE_W), (KAK_EYE_P, FAKE_EYE_P)):
        m = head & op & np.all(a[..., :3] == src, axis=-1)
        a[m, :3] = dst
    # 下摆的两个角：透明像素，正上方是黑描边、再上面是外套色（绿 / 金边），行在 28–42 之间
    h, w = a.shape[:2]
    cand = []
    for y in range(28, min(43, h - 2)):
        for x in range(w):
            if (not op[y, x] and op[y - 1, x] and tuple(a[y - 1, x, :3]) == KAK_K
                    and op[y - 2, x] and tuple(a[y - 2, x, :3]) in KAK_COAT):
                cand.append((x, y))
    if cand:
        picks = {min(cand), max(cand)}
        for k, (x, y) in enumerate(sorted(picks)):
            n = 1 + (fi + k) % 2
            for j in range(n):
                if y + j < h and not op[y + j, x]:
                    a[y + j, x] = (SL if j == 0 else SL_D) + (255,)
    return Image.fromarray(a, 'RGBA')


def _register_fake_kakyoin():
    names = []
    for act, src in KAKYOIN_FAKE.items():
        sd = sprite.get(src)
        name = 'kakyoin.' + act
        sprite.define(name, [fake_kakyoin(f, i) for i, f in enumerate(sd.frames)], anchor=sd.anchor, fps=sd.fps,
                      desc='假花京院（黄色节制伪装）：' + act + '（' + src + ' 换黄眼 + 下摆滴黏液）')
        names.append(name)
    return names


if 'kakyoin.idle' in sprite._REG:          # 烘焙时原工程精灵已注册；单独 import 本文件预览时没有，跳过
    NEW += _register_fake_kakyoin()
ONESHOT = {'hurt','down','slash','attack','grab','reveal','punch','shock','beg','hide','angry',
           'armor_attack','armor_hurt','armor_engulf'}
STATIC_STATES = {'true_form'}
CHAR_INFO = {'rubbersoul': dict(zh=PEOPLE['rubbersoul'][0],en='rubbersoul',cat='人物',typ='人物')}
