# 第四部重画：对话头像（32 × 32）。从人物小人的头放大 2 倍（Scale2x，斜边自动补顺），再把眼睛、眉毛、嘴按表情重新点一遍。
#   这样头像和小人永远是同一个造型；以前小孩和路人的头像是把小人直接放大裁出来的，一格一格的马赛克。
#   表情：normal / rage / smile / shock（和旧元数据里的键一致，别的键照旧元数据的 headAlias 落到这四个上），每个表情两帧 = 闭嘴 / 张嘴。
import os

import numpy as np
from PIL import Image

from px import Cv, OUTLINE, rgba, shade, ASSETS, ensure
from rig import draw, X, Y, CW, CH

SIZE = 32


def scale2x(a):
    """EPX / Scale2x：RGBA 数组放大 2 倍，斜线不出锯齿块"""
    h, w = a.shape[:2]
    key = (a[..., 0].astype(np.int64) << 24) | (a[..., 1].astype(np.int64) << 16) | (a[..., 2].astype(np.int64) << 8) | a[..., 3]
    P = np.pad(key, 1, mode='edge')
    A, B_, C, D = P[:-2, 1:-1], P[1:-1, 2:], P[1:-1, :-2], P[2:, 1:-1]      # 上 右 左 下
    out = np.repeat(np.repeat(key, 2, 0), 2, 1)
    ok = (C != B_) & (A != D)
    e0 = np.where(ok & (C == A), A, key)
    e1 = np.where(ok & (A == B_), B_, key)
    e2 = np.where(ok & (D == C), C, key)
    e3 = np.where(ok & (B_ == D), D, key)
    out[0::2, 0::2], out[0::2, 1::2], out[1::2, 0::2], out[1::2, 1::2] = e0, e1, e2, e3
    r = np.zeros((h * 2, w * 2, 4), np.uint8)
    r[..., 0], r[..., 1], r[..., 2], r[..., 3] = (out >> 24) & 255, (out >> 16) & 255, (out >> 8) & 255, out & 255
    return r


def _groups(cells):
    """把同一只眼 / 一张嘴的格子按相邻归组"""
    cells = set(cells)
    out = []
    while cells:
        st = [cells.pop()]
        g = set(st)
        while st:
            x, y = st.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in cells:
                        cells.remove(n)
                        g.add(n)
                        st.append(n)
        out.append(g)
    return sorted(out, key=lambda g: min(x for x, _ in g))


def portraits(B, emos=('normal', 'rage', 'smile', 'shock')):
    """返回 {表情: [闭嘴帧, 张嘴帧]}（PIL Image 32 × 32）"""
    hd = B.heads['n']
    pal = B.pal
    hx0 = X(-B.hax + B.hx)
    hy0 = Y(B.hy) - (len(hd) - 1)
    base = draw(B, {}, outline=False)
    # 头 + 肩膀：从头顶裁到领口下 3 行
    y0 = hy0
    y1 = min(CH - 1, Y(B.LH + B.TH - 4))
    eyes = [(i, j) for j, r in enumerate(hd) for i, ch in enumerate(r) if ch in 'ew']
    brows = [(i, j) for j, r in enumerate(hd) for i, ch in enumerate(r) if ch == 'b']
    mouth = [(i, j) for j, r in enumerate(hd) for i, ch in enumerate(r) if ch == 'm']
    face = [(i, j) for j, r in enumerate(hd) for i, ch in enumerate(r) if ch in 'sdewm']
    fcx = hx0 + (sum(i for i, _ in face) / len(face) if face else len(hd[0]) / 2)
    x0 = int(round(fcx - 8 - 0.5))
    # 头太宽（飞机头、大帽檐）时尽量把整个头装进去
    hw0, hw1 = hx0, hx0 + len(hd[0]) - 1
    if hw1 - x0 > 15:
        x0 = min(hw0, hw1 - 15)
    if hw0 < x0:
        x0 = max(hw0, hw1 - 15)
    sub = base.a[y0:y1 + 1, x0:x0 + 16].copy()
    big = scale2x(sub)
    H2 = big.shape[0]
    skin = rgba(pal.get('s', '#f6c49a'))
    dark = rgba(pal.get('b', '#1a1438'))
    white = rgba(pal.get('w', '#ffffff'))
    iris = rgba(pal.get('e', '#2a2a40'))
    mcol = rgba(pal.get('m', '#a04e44'))
    mdark = rgba(pal.get('M', '#7a2030'))
    red = (208, 86, 96, 255)

    def to2(i, j):
        return (hx0 + i - x0) * 2, (j) * 2

    eye_g = _groups(eyes)
    # 眼睛上面紧挨着的 b 才算眉毛（别把头发里的深色、墨镜算进去）
    brow_cells = [(i, j) for (i, j) in brows if any((i + d, j + 1) in eyes for d in (-1, 0, 1))]
    brow_g = _groups(brow_cells)
    mouth_g = _groups(mouth)
    out = {}
    for emo in emos:
        frames = []
        for talk in (0, 1):
            a = big.copy()

            def put(x, y, c):
                if 0 <= x < 32 and 0 <= y < H2:
                    a[y, x] = c

            # ---- 眼睛
            for gi, g in enumerate(eye_g):
                ci, cj = min(i for i, _ in g), min(j for _, j in g)
                wi, hj = max(i for i, _ in g) - ci + 1, max(j for _, j in g) - cj + 1
                ox, oy = to2(ci, cj)
                w2, h2 = wi * 2, hj * 2
                for yy in range(h2):
                    for xx in range(w2):
                        put(ox + xx, oy + yy, skin)
                if emo == 'smile':
                    for xx in range(1, w2 - 1):
                        put(ox + xx, oy + h2 // 2 - 1, dark)
                    put(ox, oy + h2 // 2, dark)
                    put(ox + w2 - 1, oy + h2 // 2, dark)
                    continue
                top = 1 if emo == 'rage' else 0
                for yy in range(top, h2):
                    for xx in range(w2):
                        put(ox + xx, oy + yy, white)
                if emo == 'shock':
                    put(ox + w2 // 2, oy + h2 // 2 - 1, iris)
                    put(ox + w2 // 2, oy + h2 // 2, dark)
                else:
                    for yy in range(top, h2):
                        for xx in range(w2 // 2, w2):
                            put(ox + xx, oy + yy, iris)
                    for yy in range(max(top, 1), h2 - 1):
                        put(ox + w2 - 1, oy + yy, dark)
                    put(ox + w2 // 2, oy + top, white)                  # 高光
                    put(ox, oy + h2 - 1, skin)                          # 下眼角收圆
                if emo == 'rage':
                    for xx in range(w2):
                        put(ox + xx, oy, dark)
                else:
                    for xx in range(w2):                                # 上眼线
                        put(ox + xx, oy - 0, dark if emo == 'shock' else a[oy, ox + xx] if False else a[oy, ox + xx])
            # ---- 眉毛
            for gi, g in enumerate(brow_g):
                ci, cj = min(i for i, _ in g), min(j for _, j in g)
                wi = max(i for i, _ in g) - ci + 1
                ox, oy = to2(ci, cj)
                w2 = wi * 2
                for yy in range(2):
                    for xx in range(w2):
                        put(ox + xx, oy + yy, skin)
                inner_right = gi == 0                      # 朝右的 3/4 脸：左边那只眼的眉头在右端，右边那只在左端
                for xx in range(w2):
                    t = xx / max(1, w2 - 1)
                    k = t if inner_right else 1 - t         # 0 = 眉尾，1 = 眉头
                    if emo == 'rage':
                        yy = int(round(k * 1.6))
                    elif emo == 'shock':
                        yy = -1
                    elif emo == 'smile':
                        yy = 0
                    else:
                        yy = 1 if k > 0.8 else 0
                    put(ox + xx, oy + yy, dark)
                    if emo != 'shock':
                        put(ox + xx, oy + yy + 1, dark if emo == 'rage' or wi >= 3 else a[min(H2 - 1, oy + yy + 1), ox + xx])
            # ---- 鼻子：两眼之间偏前、眼和嘴中间的一小撇暗皮肤色
            if len(eye_g) >= 2 and mouth_g:
                ex = max(i for i, _ in eye_g[-1])
                ey = max(j for g in eye_g for _, j in g)
                my = min(j for _, j in mouth_g[0])
                nx, ny = to2(ex - 1, ey + 1)
                if my - ey >= 2:
                    put(nx - 1, ny + 0, rgba(pal.get('d', '#d8946c')))
                    put(nx - 1, ny + 1, rgba(pal.get('d', '#d8946c')))
            # ---- 嘴
            for g in mouth_g:
                ci, cj = min(i for i, _ in g), min(j for _, j in g)
                wi = max(i for i, _ in g) - ci + 1
                ox, oy = to2(ci, cj)
                w2 = wi * 2
                for yy in range(2):
                    for xx in range(w2):
                        put(ox + xx, oy + yy, skin)
                if emo == 'smile':
                    for xx in range(w2):
                        put(ox + xx, oy + 1, mdark if talk else mcol)
                    put(ox - 1, oy, mcol)
                    put(ox + w2, oy, mcol)
                    if talk:
                        for xx in range(1, w2 - 1):
                            put(ox + xx, oy + 2, red)
                elif emo == 'rage':
                    for xx in range(w2):
                        put(ox + xx, oy, mdark)
                        put(ox + xx, oy + 1, white if not talk else red)
                        put(ox + xx, oy + 2, mdark)
                    if talk:
                        for xx in range(w2):
                            put(ox + xx, oy + 1, mdark if xx in (0, w2 - 1) else red)
                elif emo == 'shock':
                    for yy in range(3 if talk else 2):
                        for xx in range(1, w2 - 1):
                            put(ox + xx, oy + yy, mdark)
                    put(ox + w2 // 2 - 1, oy + 1, red)
                else:
                    for xx in range(w2):
                        put(ox + xx, oy, mdark if talk else mcol)
                    if talk:
                        for xx in range(1, w2 - 1):
                            put(ox + xx, oy + 1, red)
            cv = Cv(SIZE, SIZE)
            hh = min(SIZE - 1, H2)
            # 底边对齐画面底，上面留空
            cv.a[SIZE - hh:SIZE, 0:32] = a[H2 - hh:H2, 0:32]
            cv.outline(OUTLINE)
            frames.append(cv.img())
        out[emo] = frames
    return out


ALIAS = {'angry': 'rage', 'glare': 'rage', 'surprise': 'shock', 'hurt': 'shock', 'happy': 'smile', 'blush': 'smile', 'cry': 'shock',
         'sad': 'normal', 'serious': 'normal', 'portrait': 'normal', 'portrait_angry': 'rage', 'grey': 'normal', 'white': 'normal'}


def export_heads(cid, B, emos):
    """写 assets/heads/<cid>/<表情>_<帧>.png；返回 {表情: [图名…]}。旧元数据里四种以外的表情名落到最像的那张上"""
    res = {}
    ps = portraits(B)
    for emo in emos:
        frs = ps.get(emo) or ps.get(ALIAS.get(emo, 'normal')) or ps['normal']
        keys = []
        for i, f in enumerate(frs):
            key = 'heads/%s/%s_%d' % (cid, emo, i)
            f.save(ensure(os.path.join(ASSETS, key + '.png')))
            keys.append(key)
        res[emo] = keys
    return res


def export_face(cid, frame, box, emos):
    """整帧手画的角色（水中项链、小动物……）：从待机帧上裁 16 × 16 的脸放大 2 倍当头像（各表情同一张）"""
    x0, y0 = box
    sub = frame.a[y0:y0 + 16, x0:x0 + 16].copy()
    big = scale2x(sub)
    cv = Cv(SIZE, SIZE)
    cv.a[:, :] = big
    im = cv.img()
    res = {}
    for emo in emos:
        keys = []
        for i in range(2):
            key = 'heads/%s/%s_%d' % (cid, emo, i)
            im.save(ensure(os.path.join(ASSETS, key + '.png')))
            keys.append(key)
        res[emo] = keys
    return res
