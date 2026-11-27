# 第四部重画：Q 版小人的“纸娃娃骨架”。原生分辨率直接画（不再从大图缩小），一格一格落像素。
#   坐标：骨架空间以两脚中间的落地点为原点，+x = 人物面朝的方向（右），+y = 向上；画到画布时翻成图像坐标。
#   一个人物 = 头（手写字符稿，可带表情变体）+ 躯干（手写字符稿或纯色）+ 四肢（按姿势用粗线画）+ 衣摆 / 裙子 / 额外部件。
#   姿势表（poses.py）所有人共用：只写“手脚放哪、身体怎么歪”，身高不同的人按自己的躯干长、腿长套进去。
#   比例标准见 第四部/docs/比例标准.md。
import numpy as np
from PIL import Image

from px import Cv, OUTLINE, rgba, shade, rows, mix

CW, CH = 112, 80           # 工作画布
OX, OY = 44, 66            # 骨架原点落在画布的哪一格（OY = 脚底那一行）


def X(x):
    return OX + int(round(x))


def Y(y):
    return OY - int(round(y))


class Body:
    """一个人物的身体定义。尺寸单位都是像素（站着的高度 1 px ≈ 6 cm，见比例标准）。"""

    def __init__(self, heads, TH=9, LH=8, tw=8, arm_w=2, leg_w=3, pal=None, torso=None, top='#3a3a6a', pants='#2a2a48',
                 shoe='#5a3a22', skin='#f6c49a', sleeve=None, hand=None, coat=None, skirt=None, back=None, front=None,
                 hax=6, hy=None, hx=0, bare=None, cuff=None, arm_len=None, shoulder=0, sleeve_len=None,
                 hip=0, shoe_w=None, shoe_h=2, glove=None, far_dark=True, arm_y=1, kind='human', extra=None, mid=None,
                 pat_leg=None, pat_arm=None, boot=None, wrist=None):
        self.heads = heads if isinstance(heads, dict) else {'n': heads}
        self.heads = {k: (rows(v) if isinstance(v, str) else v) for k, v in self.heads.items()}
        self.TH, self.LH, self.tw, self.arm_w, self.leg_w = TH, LH, tw, arm_w, leg_w
        self.pal = dict(pal or {})
        self.torso = rows(torso) if isinstance(torso, str) else torso
        self.top, self.pants, self.shoe, self.skin = top, pants, shoe, skin
        self.sleeve = sleeve or top          # 袖子颜色（短袖的人把 sleeve_len 设小，剩下的是皮肤）
        self.hand = hand or skin
        self.coat, self.skirt = coat, skirt
        self.back, self.mid, self.front = back, mid, front    # 额外部件：最底下 / 躯干之后头之前 / 最上面
        self.hax = hax                       # 头的字符稿里哪一列对着身体中线
        self.hy = hy if hy is not None else LH + TH - 1    # 头最下面一行落在骨架的哪个高度（默认压住领口一行）
        self.hx = hx
        self.bare = bare                     # 光腿：dict(top=上面几格是短裤 / 裙下, sock=袜色, sock_h=袜高, skin=腿色)
        self.cuff = cuff                     # 袖口颜色（一格）
        self.arm_len = arm_len if arm_len is not None else max(4, TH - 1)
        self.shoulder = shoulder             # 肩比躯干再宽出几格（替身、壮汉）
        self.sleeve_len = sleeve_len         # None = 长袖
        self.hip = hip
        self.shoe_w = shoe_w if shoe_w is not None else leg_w + 1
        self.shoe_h = shoe_h
        self.glove = glove
        self.far_dark = far_dark
        self.arm_y = arm_y                   # 肩关节比躯干顶低几格
        self.kind = kind
        self.extra = extra or {}
        # 第五部加的：腿 / 袖子上的花纹 fn(沿肢体第几格, 横截面第几列, 总长) -> 颜色或 None；靴子 (颜色, 高几格)；手腕一圈的颜色
        self.pat_leg, self.pat_arm, self.boot, self.wrist = pat_leg, pat_arm, boot, wrist

    # 关节位置（骨架坐标）
    def hipN(self):
        return (-self.tw // 2 + 1 + (self.leg_w - 1) // 2 + self.hip, self.LH - 1)

    def hipF(self):
        return (self.tw // 2 - 1 - self.leg_w // 2 - self.hip, self.LH - 1)

    def shN(self):
        return (-self.tw // 2 - self.shoulder, self.LH + self.TH - 1 - self.arm_y)

    def shF(self):
        return (self.tw // 2 - 1 + self.shoulder, self.LH + self.TH - 1 - self.arm_y)


def _lum(c):
    r, g, b, _ = rgba(c)
    return 0.3 * r + 0.59 * g + 0.11 * b


def _seg_cols(base, w, dark=False):
    """一条肢体横截面的颜色：背 / 下侧一格暗，其余主色；远侧肢体整体压暗（浅色衣服压得少，免得发灰）"""
    if _lum(base) > 165:
        # 白 / 浅色：阴影往冷灰蓝走，不往黑走
        b = mix(base, '#8088a8', 0.2) if dark else base
        d = mix(base, '#8088a8', 0.42 if dark else 0.28)
    else:
        b = shade(base, -0.26) if dark else base
        d = shade(base, -(0.48 if dark else 0.3))
    return [d] + [b] * (w - 1)


def _pattern(fn, k, total, cols, dark):
    """把花纹盖到一条肢体横截面上；远侧肢体的花纹跟着压暗"""
    if not fn:
        return cols
    out = list(cols)
    for i in range(len(out)):
        c = fn(k, i, total)
        if c:
            out[i] = shade(c, -0.26) if dark else c
    return out


def _trace(pts):
    full = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = int(max(abs(x1 - x0), abs(y1 - y0), 1))
        vert = abs(y1 - y0) >= abs(x1 - x0)
        for i in range(n + 1):
            full.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n, vert))
    return full


def _stamp(cv, x, y, vert, w, cols):
    for i in range(w):
        c = cols[min(i, len(cols) - 1)]
        if vert:       # 竖着的一段：w 格横排，i = 0 在背面（左）
            cv.put(X(x) - (w - 1) // 2 + i, Y(y), c)
        else:          # 横着的一段：w 格竖排，i = 0 在下面
            cv.put(X(x), Y(y) + (w - 1) // 2 - i, c)


def _arm(cv, B, sh, spec, far, fist=None):
    """spec = (hx, hy) 手相对肩的位置；或 ((ex, ey), (hx, hy)) 带肘。返回手的位置（骨架坐标）"""
    w = B.arm_w
    if spec is None:
        spec = (0, -B.arm_len)
    pts = [sh]
    if isinstance(spec[0], (tuple, list)):
        for p in spec:
            pts.append((sh[0] + p[0], sh[1] + p[1]))
    else:
        pts.append((sh[0] + spec[0], sh[1] + spec[1]))
    dark = far and B.far_dark
    sl = _seg_cols(B.sleeve, w, dark)
    sk = _seg_cols(B.glove or B.hand, w, dark)
    full = _trace(pts)
    total = len(full)
    hand_n = 2 if w <= 3 else 3
    slen = total - hand_n if B.sleeve_len is None else min(B.sleeve_len, total - hand_n)
    for k, (x, y, vert) in enumerate(full):
        cols = sl if k < slen else sk
        if B.cuff and B.sleeve_len is None and k == slen - 1:
            cols = _seg_cols(B.cuff, w, dark)
        if B.pat_arm:
            cols = _pattern(B.pat_arm, k, total, cols, dark)
        if B.wrist and k == total - hand_n - 1:
            cols = _seg_cols(B.wrist, w, dark)
        _stamp(cv, x, y, vert, w, cols)
    hx, hy, vert = full[-1]
    if fist:
        # 拳头：比手臂大一圈的方块（替身出拳、角色出拳时用）
        s = fist
        c0 = B.glove or B.hand
        x0, y0 = X(hx) - (s - 1) // 2, Y(hy) - (s - 1) // 2
        cv.rect(x0, y0, x0 + s - 1, y0 + s - 1, shade(c0, -0.26) if dark else c0)
        cv.hline(x0, x0 + s - 1, y0 + s - 1, shade(c0, -0.48 if dark else -0.3))
        if s >= 4:
            cv.put(x0 + s - 1, y0, shade(c0, 0.25))
    return hx, hy


def _leg(cv, B, hip, spec, far, hipdrop=0):
    """spec = (dx, lift) 脚相对默认落点；或 ((kx, ky), (dx, lift)) 带膝（膝相对胯）。返回脚踝位置"""
    w = B.leg_w
    hx, hy = hip[0], hip[1] + hipdrop
    if spec is None:
        spec = (0, 0)
    pts = [(hx, hy)]
    if isinstance(spec[0], (tuple, list)):
        knee, foot = spec
        pts.append((hx + knee[0], max(B.shoe_h, hy + knee[1])))
    else:
        foot = spec
    fx, fy = hip[0] + foot[0], foot[1] + B.shoe_h
    pts.append((fx, fy))
    dark = far and B.far_dark
    pc = _seg_cols(B.pants, w, dark)
    full = _trace(pts)
    total = len(full)
    for k, (x, y, vert) in enumerate(full):
        cols = pc
        if B.bare:
            top_n = B.bare.get('top', 0)
            sock_h = B.bare.get('sock_h', 0)
            if k >= top_n:
                base = B.bare.get('sock', B.skin) if k >= total - sock_h else B.bare.get('skin', B.skin)
                cols = _seg_cols(base, w, dark)
        cols = _pattern(B.pat_leg, k, total, cols, dark)
        if B.boot and k >= total - B.boot[1]:
            cols = _seg_cols(B.boot[0], w, dark)
        _stamp(cv, x, y, vert, w, cols)
    # 鞋：脚踝往下 shoe_h 行，往前多伸一格；最后一段是横着的（踢腿、坐着伸腿）就把鞋立在腿的末端
    sc = shade(B.shoe, -0.26) if dark else B.shoe
    sd = shade(B.shoe, -0.48 if dark else -0.3)
    vert = full[-1][2]
    if not vert:
        sgn = 1 if full[-1][0] >= full[0][0] else -1
        for r in range(B.shoe_h):
            xx = X(fx) + sgn * (1 + r)
            cv.vline(xx, Y(fy) - (w - 1) // 2 - 1, Y(fy) + (w - 1) // 2, sd if r == B.shoe_h - 1 else sc)
    else:
        x0 = X(fx) - (w - 1) // 2
        for r in range(B.shoe_h):
            yy = Y(fy) + 1 + r
            ext = 1 if r == B.shoe_h - 1 or B.shoe_h == 1 else 0
            cv.hline(x0, x0 + w - 1 + ext + (B.shoe_w - w - 1), yy, sd if r == B.shoe_h - 1 else sc)
    return fx, fy


def _sep(dst, part, col):
    """part 盖到 dst 上之前，在 part 外沿、dst 已经有东西的地方压一圈分隔线（同色暗调），部件之间才分得开"""
    op = part.mask()
    nb = np.zeros_like(op)
    nb[1:, :] |= op[:-1, :]
    nb[:-1, :] |= op[1:, :]
    nb[:, 1:] |= op[:, :-1]
    nb[:, :-1] |= op[:, 1:]
    ring = nb & ~op & dst.mask()
    if col is not None:
        dst.a[ring] = rgba(col)
    dst.blit(part)


DEFAULT_POSE = dict(dy=0, lean=0, bx=0, head='n', hx=0, hy=0, aN=None, aF=None, lN=None, lF=None, drop=0,
                    fistN=None, fistF=None, aF_front=False, aN_back=False, lie=None, item=None, no_legs=False)


def draw(B, pose=None, outline=True):
    """按姿势画一帧，返回工作画布（原点 OX, OY）"""
    P = dict(DEFAULT_POSE)
    P.update(pose or {})
    cv = Cv(CW, CH)
    dy, lean, bx, drop = P['dy'], P['lean'], P['bx'], P['drop']
    by = dy - drop                        # 躯干 + 头的整体升降
    TH, LH, tw = B.TH, B.LH, B.tw

    def tx(r):                            # 躯干第 r 行（0 = 最下）的横向偏移
        return bx + (int(round(lean * r / max(1, TH - 1))) if lean else 0)

    shN = (B.shN()[0] + tx(TH - 1 - B.arm_y), B.shN()[1] + by)
    shF = (B.shF()[0] + tx(TH - 1 - B.arm_y), B.shF()[1] + by)
    hipN = (B.hipN()[0] + bx, B.hipN()[1])
    hipF = (B.hipF()[0] + bx, B.hipF()[1])
    hd = B.heads.get(P['head']) or B.heads['n']
    hx0 = X(-B.hax + B.hx + tx(TH - 1) + P['hx'])
    hy0 = Y(B.hy + by + P['hy']) - (len(hd) - 1)
    ctx = dict(tx=tx, by=by, bx=bx, shN=shN, shF=shF, hipN=hipN, hipF=hipF, hx0=hx0, hy0=hy0, hrows=len(hd), X=X, Y=Y)

    if B.back:
        B.back(cv, B, P, ctx)
    # 远侧手臂（多数姿势在躯干后面）
    if not P['aF_front']:
        ctx['handF'] = _arm(cv, B, shF, P['aF'], True, P['fistF'])
    if not P['no_legs']:
        ctx['footF'] = _leg(cv, B, hipF, P['lF'], True, by)
        part = Cv(CW, CH)
        ctx['footN'] = _leg(part, B, hipN, P['lN'], False, by)
        _sep(cv, part, shade(B.pants if not B.bare else B.bare.get('skin', B.skin), -0.62))
    # 近侧手臂放到躯干后面（背手之类）
    if P['aN_back']:
        ctx['handN'] = _arm(cv, B, shN, P['aN'], False, P['fistN'])
    # 躯干
    part = Cv(CW, CH)
    for r in range(TH):
        yy = Y(LH + r + by)
        x0 = X(-tw // 2 + tx(r))
        if B.torso:
            row = B.torso[TH - 1 - r]
            for i, ch in enumerate(row):
                if ch not in '. ':
                    part.put(x0 + i, yy, B.pal[ch])
        else:
            part.hline(x0, x0 + tw - 1, yy, B.top)
            part.put(x0, yy, shade(B.top, -0.3))
    _sep(cv, part, shade(B.top, -0.6))
    # 衣摆 / 裙子（盖住大腿）
    if B.coat or B.skirt:
        part = Cv(CW, CH)
        for s, is_coat in ((B.coat, True), (B.skirt, False)):
            if not s:
                continue
            n = s['len']
            for k in range(n):
                yy = Y(LH - 1 - k + by)
                fl = int(round(s.get('flare', 0 if is_coat else 1) * (k + 1) / n))
                x0, x1 = X(-tw // 2 + bx) - fl, X(-tw // 2 + bx) + tw - 1 + fl
                part.hline(x0, x1, yy, s['col'])
                part.put(x0, yy, shade(s['col'], -0.3))
                if s.get('pleat') and k > 0:
                    for xx in range(x0 + 2, x1, s['pleat']):
                        part.put(xx, yy, shade(s['col'], -0.22))
                if s.get('trim') and k == n - 1:
                    part.hline(x0, x1, yy, s['trim'])
                if s.get('line') is not None:
                    part.put(X(s['line'] + bx), yy, shade(s['col'], -0.45))
                if s.get('dots') and k % 2 == 1:
                    part.put(X(s['dots'][0] + bx), yy, s['dots'][1])
                if s.get('open') is not None:
                    for xx in range(X(s['open'][0] + bx), X(s['open'][1] + bx) + 1):
                        part.clear(xx, yy)
        _sep(cv, part, shade((B.coat or B.skirt)['col'], -0.6))
    if B.mid:
        B.mid(cv, B, P, ctx)
    if P['aF_front']:
        part = Cv(CW, CH)
        ctx['handF'] = _arm(part, B, shF, P['aF'], False, P['fistF'])
        _sep(cv, part, shade(B.sleeve, -0.62))
    # 头
    part = Cv(CW, CH)
    part.grid(hd, hx0, hy0, B.pal)
    cv.blit(part)
    # 近侧手臂（在最前）
    if not P['aN_back']:
        part = Cv(CW, CH)
        ctx['handN'] = _arm(part, B, shN, P['aN'], False, P['fistN'])
        _sep(cv, part, shade(B.sleeve if B.sleeve_len is None or B.sleeve_len > 1 else B.hand, -0.62))
    if B.front:
        B.front(cv, B, P, ctx)
    if P.get('lie'):
        cv = lie(cv, P['lie'])
    if outline:
        cv.outline(OUTLINE)
        fill_pinholes(cv)
    return cv


def fill_pinholes(cv):
    """四面都是实心的单个透明格（胳膊和身体之间漏出的一点底色）补成描边色"""
    m = cv.mask()
    hole = np.zeros_like(m)
    hole[1:-1, 1:-1] = ~m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:]
    cv.a[hole] = rgba(OUTLINE)


def lie(cv, mode='back'):
    """把站姿放倒。back = 仰面（头朝左、脸朝上）；front = 趴着（头朝右、脸朝下）"""
    bb = cv.bbox()
    if not bb:
        return cv
    x0, y0, x1, y1 = bb
    sub = Cv(x1 - x0 + 1, y1 - y0 + 1)
    sub.a = cv.a[y0:y1 + 1, x0:x1 + 1].copy()
    r = sub.rot90(1 if mode == 'back' else 3)
    out = Cv(CW, CH)
    out.blit(r, OX - r.w // 2, OY - r.h + 1)
    return out


def grid_part(txt, dx, dy, where='head'):
    """额外部件（长发、背包、手里的东西）：一块字符稿，贴在相对头 / 躯干 / 手的位置。
    where = 'head'：相对头字符稿的左上角；'torso'：相对躯干左上角；'handF' / 'handN'：相对手。返回可挂到 back / mid / front 的函数"""
    g = rows(txt)

    def fn(cv, B, P, ctx):
        if where == 'head':
            x, y = ctx['hx0'] + dx, ctx['hy0'] + dy
        elif where == 'torso':
            x, y = X(-B.tw // 2 + ctx['tx'](B.TH - 1)) + dx, Y(B.LH + B.TH - 1 + ctx['by']) + dy
        else:
            h = ctx.get(where)
            if not h:
                return
            x, y = X(h[0]) + dx, Y(h[1]) + dy
        cv.grid(g, x, y, B.pal)
    return fn


def chain(*fns):
    def fn(cv, B, P, ctx):
        for f in fns:
            if f:
                f(cv, B, P, ctx)
    return fn


from poses import poses, variants  # noqa: E402,F401  （姿势表和表情变体在 poses.py）


# ------------------------------------------------------------------ 图集
class Sheet:
    def __init__(self, cid, name, kind='char'):
        self.cid, self.name, self.kind = cid, name, kind
        self.rows = []                    # (动作名, [Cv 工作画布…], fps, kind)
        self.body = None
        self.face = None                  # 整帧手画的角色：头像从待机帧的哪一块裁（左上角，16 × 16）

    def add(self, anim, frames, fps=6, kind='loop'):
        self.rows.append((anim, list(frames), fps, kind))
        return self

    def add_pose(self, B, P, names):
        for n in names:
            if isinstance(n, tuple):      # (图集里的名字, 姿势表里的名字)
                frs, fps, kind = P[n[1]]
                self.add(n[0], [draw(B, f) for f in frs], fps, kind)
            else:
                frs, fps, kind = P[n]
                self.add(n, [draw(B, f) for f in frs], fps, kind)
        return self

    def pack(self, pad=1):
        """所有帧按同一个原点裁成等大的格子；返回 (图集 Image, cell, pivot)"""
        x0 = y0 = 10 ** 6
        x1 = y1 = -1
        for _, frs, _, _ in self.rows:
            for f in frs:
                bb = f.bbox()
                if bb:
                    x0, y0, x1, y1 = min(x0, bb[0]), min(y0, bb[1]), max(x1, bb[2]), max(y1, bb[3])
        x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, max(y1, OY + 1)
        cw, ch = x1 - x0 + 1, y1 - y0 + 1
        n = max(len(r[1]) for r in self.rows)
        im = Image.new('RGBA', (cw * n, ch * len(self.rows)), (0, 0, 0, 0))
        for r, (_, frs, _, _) in enumerate(self.rows):
            for i, f in enumerate(frs):
                im.alpha_composite(f.img().crop((x0, y0, x1 + 1, y1 + 1)), (i * cw, r * ch))
        return im, [cw, ch], [OX - x0, OY + 1 - y0]

    def anims(self):
        return {a: dict(row=r, frames=len(frs), fps=fps, kind=kind) for r, (a, frs, fps, kind) in enumerate(self.rows)}

    def top(self):
        """待机第 0 帧最高的像素到脚底的高度"""
        bb = self.rows[0][1][0].bbox()
        return OY + 1 - bb[1] if bb else 30
