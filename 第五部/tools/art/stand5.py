# 第五部替身画笔：画法照第三部、第四部原版替身（沿用当年 sprites_stands 的字符网格画笔：
#   椭圆 / 胶囊 / 多边形打底，左上受光的 3–4 阶明暗，深色描边；浮空、肌肉身体、比人物大一圈，和 Q 版人物拉开）。
#   一帧 = 逻辑画布上的字符网格；body 中线 bx、脚底基准 y = 56，最后贴到 rig 的工作画布（和人物同一个原点）。
import math

import numpy as np
from PIL import Image, ImageDraw

from px import Cv, OUTLINE, rgba
from rig import Sheet, CW, CH, OX, OY, fill_pinholes

M = 8          # 画布四周留的余量
FLOOR = 56     # 逻辑画布里对应脚底基准线的 y
SCALE = 0.76   # 人形替身：形状坐标按这个比例缩着直接画（不缩像素），站起来约 40 px，比人物（30 px）高一头


def g_lines(grid):
    return [r.strip() for r in grid.strip('\n').split('\n') if r.strip()]


def _dil(m):
    g = m.copy()
    g[1:, :] |= m[:-1, :]
    g[:-1, :] |= m[1:, :]
    g[:, 1:] |= m[:, :-1]
    g[:, :-1] |= m[:, 1:]
    return g


def _runs_u(mask):
    h, w = mask.shape
    u = np.zeros((h, w), np.float32)
    L = np.zeros((h, w), np.float32)
    for y in range(h):
        row = mask[y]
        x = 0
        while x < w:
            if row[x]:
                x0 = x
                while x < w and row[x]:
                    x += 1
                n = x - x0
                u[y, x0:x] = (np.arange(n) + 0.5) / n
                L[y, x0:x] = n
            else:
                x += 1
    return u, L


class Pix:
    """字符网格画布，从后往前画。坐标用逻辑坐标（左上 0,0），四周另有 M 格余量。"""

    def __init__(self, w, h=FLOOR, m=M, s=1.0, ax=22):
        self.s, self.ax = s, ax
        self.m = m
        self.lw, self.lh = w, h
        self.w, self.h = w + 2 * m, h + 2 * m
        self.c = np.full((self.h, self.w), '.', dtype='<U1')
        Y, X = np.mgrid[0:self.h, 0:self.w]
        self.X = (X - m).astype(np.float32)
        self.Y = (Y - m).astype(np.float32)

    def tx(self, x):
        return self.ax + (x - self.ax) * self.s

    def ty(self, y):
        return FLOOR + (y - FLOOR) * self.s

    def _pt(self, a, b):
        return (float(self.tx(a)) + self.m, float(self.ty(b)) + self.m)

    # ---------- 形状
    def ell(self, cx, cy, rx, ry):
        cx, cy, rx, ry = self.tx(cx), self.ty(cy), rx * self.s, ry * self.s
        return ((self.X - cx) / rx) ** 2 + ((self.Y - cy) / ry) ** 2 <= 1.0

    def cap(self, x0, y0, x1, y1, r0, r1=None):
        r1 = r0 if r1 is None else r1
        x0, y0, x1, y1 = self.tx(x0), self.ty(y0), self.tx(x1), self.ty(y1)
        r0, r1 = r0 * self.s, r1 * self.s
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1e-6
        t = np.clip(((self.X - x0) * dx + (self.Y - y0) * dy) / L2, 0, 1)
        px, py = x0 + t * dx, y0 + t * dy
        r = r0 + (r1 - r0) * t
        return (self.X - px) ** 2 + (self.Y - py) ** 2 <= r * r

    def poly(self, pts):
        im = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon([self._pt(a, b) for a, b in pts], fill=1)
        return np.array(im) > 0

    def rect(self, x0, y0, x1, y1):
        return ((self.X >= self.tx(x0) - 0.01) & (self.X <= self.tx(x1) + 0.01)
                & (self.Y >= self.ty(y0) - 0.01) & (self.Y <= self.ty(y1) + 0.01))

    def lmask(self, pts, width=1):
        im = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(im).line([self._pt(a, b) for a, b in pts], fill=1, width=width)
        return np.array(im) > 0

    def empty(self):
        return np.zeros((self.h, self.w), bool)

    # ---------- 上色
    def paint(self, mask, tones, outline='k', hi=0.26, sh=0.64, rim=True):
        """tones: 1 个字符 = 平涂；3 个 = 高光 / 主色 / 阴影；4 个 = 再加右下边缘的深影。光从左上来。"""
        if outline:
            ring = _dil(mask) & ~mask
            self.c[ring] = outline
        if len(tones) == 1:
            self.c[mask] = tones
            return mask
        uh, Lh = _runs_u(mask)
        uvT, LvT = _runs_u(mask.T)
        uv, Lv = uvT.T, LvT.T
        tot = np.maximum(Lh + Lv, 1)
        u = (uh * Lv + uv * Lh) / tot
        hic, bc, shc = tones[0], tones[1], tones[2]
        out = np.where(u > sh, shc, bc)
        if rim:
            e_l = mask & ~np.roll(mask, 1, 1)
            e_t = mask & ~np.roll(mask, 1, 0)
            e_l[:, 0] = mask[:, 0]
            e_t[0, :] = mask[0, :]
            near = e_l | e_t | np.roll(e_l, 1, 1) & (u < hi * 0.7)
            hl = mask & (u < hi) & near
        else:
            hl = mask & (u < hi)
        out = np.where(hl, hic, out)
        if len(tones) > 3:
            e_r = mask & ~np.roll(mask, -1, 1)
            e_b = mask & ~np.roll(mask, -1, 0)
            out = np.where((e_r | e_b) & (u > sh + 0.12), tones[3], out)
        self.c[mask] = out[mask]
        return mask

    def fill(self, mask, ch):
        self.c[mask] = ch

    def keep(self, mask, ch, only):
        m = mask & np.isin(self.c, list(only))
        self.c[m] = ch

    def swap(self, mask, src, dst):
        """把 mask 里的一套色阶换成另一套（护腕、护膝这类跟着身体明暗走的装饰）"""
        old = self.c.copy()
        for s, d in zip(src, dst):
            self.c[mask & (old == s)] = d

    def px(self, x, y, ch):
        x, y = int(round(self.tx(x))) + self.m, int(round(self.ty(y))) + self.m
        if 0 <= x < self.w and 0 <= y < self.h:
            self.c[y, x] = ch

    def get(self, x, y):
        x, y = int(round(self.tx(x))) + self.m, int(round(self.ty(y))) + self.m
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.c[y, x]
        return '.'

    def dot(self, x, y, ch, only=None):
        if only is None or self.get(x, y) in only:
            self.px(x, y, ch)

    def line(self, pts, ch, width=1, only=None):
        m = self.lmask(pts, width)
        if only:
            m &= np.isin(self.c, list(only))
        self.c[m] = ch

    def stamp(self, grid, x, y, flip=False):
        ls = g_lines(grid)
        if flip:
            ls = [r[::-1] for r in ls]
        # 贴图中心跟着缩放后的位置走，字符稿本身不缩
        w, h = max(len(r) for r in ls), len(ls)
        x = int(round(self.tx(x + w / 2) - w / 2))
        y = int(round(self.ty(y + h / 2) - h / 2))
        for j, row in enumerate(ls):
            yy = y + j + self.m
            if not 0 <= yy < self.h:
                continue
            for i, ch in enumerate(row):
                xx = x + i + self.m
                if ch != '.' and 0 <= xx < self.w:
                    self.c[yy, xx] = ch

    def blit_grid(self, ls, x, y):
        """按画布坐标（不缩放）贴字符稿"""
        for j, row in enumerate(ls):
            yy = y + j + self.m
            if not 0 <= yy < self.h:
                continue
            for i, ch in enumerate(row):
                xx = x + i + self.m
                if ch != '.' and 0 <= xx < self.w:
                    self.c[yy, xx] = ch

    def clean(self, oc='k'):
        """去掉四邻没有实色的孤立描边点"""
        solid = (self.c != '.') & (self.c != oc)
        near = np.zeros_like(solid)
        near[1:, :] |= solid[:-1, :]
        near[:-1, :] |= solid[1:, :]
        near[:, 1:] |= solid[:, :-1]
        near[:, :-1] |= solid[:, 1:]
        self.c[(self.c == oc) & ~near] = '.'
        return self

    def to_cv(self, pal, bx):
        """贴到 rig 工作画布：逻辑 (bx, FLOOR) 对到脚底中点"""
        cv = Cv(CW, CH)
        offx, offy = OX - (bx + self.m), OY + 1 - (FLOOR + self.m)
        lut = {'k': OUTLINE}
        lut.update(pal)
        ys, xs = np.nonzero(self.c != '.')
        for y, x in zip(ys, xs):
            ch = self.c[y, x]
            if ch not in lut:
                raise KeyError('替身调色板里没有字符 %r' % ch)
            cv.put(x + offx, y + offy, lut[ch])
        fill_pinholes(cv)
        return cv


# ====================================================================== 人形替身
# 姿势：坐标相对 (cx, ty) = 胸口中线 / 躯干顶。far / near = (肩 x,y, 肘 x,y, 拳 x,y)；legs = (远腿, 近腿)，每条 (胯, 膝, 脚)
LEGS_IDLE = ((3, 19, 6, 26, 3, 35), (-3, 19, -6, 27, -10, 34))
POSES = {
    'idle': dict(lean=0, far=(8, 3, 12, 10, 16, 3), near=(-8, 4, -12, 10, -7, 15), legs=LEGS_IDLE),
    'punch0': dict(lean=-2, far=(8, 3, 11, 10, 13, 4), near=(-8, 4, -13, 8, -10, 1),
                   legs=((3, 19, 7, 25, 5, 34), (-3, 19, -5, 27, -9, 34)), sy=1),
    'punch1': dict(lean=2, far=(8, 3, 17, 3, 27, 3), near=(-8, 4, -12, 10, -7, 15),
                   legs=((3, 19, 4, 27, 0, 35), (-3, 19, -8, 25, -14, 30)), shout=True, w=64),
    'punch2': dict(lean=3, far=(8, 3, 13, 10, 15, 4), near=(-7, 4, 4, 7, 24, 6),
                   legs=((3, 19, 5, 27, 1, 35), (-3, 19, -8, 25, -14, 30)), shout=True, near_front=True, w=64),
    'rush': dict(lean=3, far=(8, 3, 17, 1, 27, 0), near=(-7, 4, 5, 8, 25, 9),
                 legs=((3, 19, 3, 27, -1, 35), (-3, 19, -9, 24, -16, 28)), shout=True, near_front=True, w=64),
    'block': dict(lean=0, far=(8, 3, 14, 11, 14, -1), near=(-8, 4, 3, 13, 7, 0),
                  legs=((3, 19, 7, 25, 5, 34), (-3, 19, -6, 26, -10, 33)), sy=1),
    'pose': dict(lean=0, far=(8, 3, 11, 9, -4, 8), near=(-8, 4, -11, 12, 7, 13),
                 legs=((3, 19, 7, 26, 5, 35), (-3, 19, -5, 27, -7, 35)), far_front=True, far_fist=False,
                 near_fist=False),
    'hurt': dict(lean=-3, far=(8, 3, 14, 7, 20, 3), near=(-8, 4, -15, 6, -19, 2),
                 legs=((3, 19, 7, 26, 9, 34), (-3, 19, -7, 27, -12, 35)), sy=1, shout=True),
}

# 连打残影：(哪边的肩, 拳 dx, dy)
GHOSTS = [[('f', 30, -6), ('n', 33, 3), ('f', 35, 12), ('n', 27, 17), ('f', 24, -9)],
          [('n', 34, -3), ('f', 29, 6), ('n', 33, 14), ('f', 36, -9), ('f', 25, 19)]]
TIPS = [[(40, -2), (41, 9), (37, 21), (36, -11)], [(41, 3), (39, -8), (40, 17), (35, 23)]]


class Stand:
    """人形替身的定义。tones = 身体 4 阶（高光 主色 阴影 深影）；各部位的花样用回调叠上去。"""

    def __init__(self, pal, tones, head, shout=None, **kw):
        self.pal = pal
        self.tones = tones
        self.head = head
        self.shout = shout or head
        self.chest = kw.get('chest', (9.4, 6.2))          # 胸椭圆半径
        self.waist = kw.get('waist', (8, 5, 18))           # 腰上半宽、下半宽、底边高度
        self.arm = kw.get('arm', (3.3, 2.7, 2.8, 2.2))    # 肩、肘（上臂端）、肘（前臂端）、腕
        self.fist = kw.get('fist', 3.0)
        self.leg = kw.get('leg', (3.7, 2.8, 1.5))
        self.arm_tones = kw.get('arm_tones', tones)
        self.leg_tones = kw.get('leg_tones', tones)
        self.fist_tones = kw.get('fist_tones', tones[:3])
        self.pecs = kw.get('pecs', True)
        self.shoulder = kw.get('shoulder', 0)             # 肩比默认再宽几格
        self.hdx, self.hdy = kw.get('hdx', 0), kw.get('hdy', 0)
        self.poses = {k: dict(v) for k, v in POSES.items()}
        for k, v in (kw.get('poses') or {}).items():
            self.poses.setdefault(k, {}).update(v)
        # 回调
        self.back = kw.get('back')              # (p, S, hx, hy, cx, ty, ph, P)
        self.torso = kw.get('torso')            # 整个换掉默认躯干 (p, S, cx, ty)
        self.torso_deco = kw.get('torso_deco')  # (p, cx, ty)
        self.arm_deco = kw.get('arm_deco')      # (p, 肩, 肘, 拳, near)
        self.leg_deco = kw.get('leg_deco')      # (p, 胯, 膝, 脚, near)
        self.legs = kw.get('legs', True)
        self.lower = kw.get('lower')            # 没有腿时画下半身 (p, cx, ty, ph, P)
        self.pad = kw.get('pad')                # (p, x, y, near)
        self.belt = kw.get('belt')              # (p, x, y, ph)
        self.neck = kw.get('neck')              # (p, x, y)
        self.front = kw.get('front')            # (p, cx, ty, ph, P)
        self.neck_r = kw.get('neck_r', 3.0)
        self.ghost = kw.get('ghost', ('w', tones[2]))     # 连打残影 (亮色, 描边色)

    # ---------- 部件
    def draw_arm(self, p, s, e, f, near, fist=True, tones=None, outline='k', fr=None):
        a0, a1, a2, a3 = self.arm
        tones = tones or self.arm_tones
        m = p.cap(s[0], s[1], e[0], e[1], a0, a1) | p.cap(e[0], e[1], f[0], f[1], a2, a3)
        p.paint(m, tones, outline=outline)
        if self.arm_deco and outline == 'k':
            self.arm_deco(p, s, e, f, near)
        if fist:
            dx, dy = f[0] - e[0], f[1] - e[1]
            L = max(1e-3, math.hypot(dx, dy))
            ux, uy = dx / L, dy / L
            r = fr or self.fist
            fm = p.ell(f[0] + ux * 0.5, f[1] + uy * 0.5, r, r * 0.92)
            p.paint(fm, self.fist_tones, hi=0.35, sh=0.62, outline=outline)
            kx, ky = f[0] + ux * 1.6, f[1] + uy * 1.6
            p.line([(kx - uy * 1.2, ky + ux * 1.2), (kx + uy * 1.2, ky - ux * 1.2)], self.fist_tones[2])

    def draw_leg(self, p, hip, knee, foot, near):
        r0, r1, r2 = self.leg
        m = p.cap(hip[0], hip[1], knee[0], knee[1], r0, r1) | p.cap(knee[0], knee[1], foot[0], foot[1], r1, r2)
        p.paint(m, self.leg_tones)
        if self.leg_deco:
            self.leg_deco(p, hip, knee, foot, near)

    def draw_torso(self, p, cx, ty):
        if self.torso:
            self.torso(p, self, cx, ty)
            return
        rx, ry = self.chest
        wt, wb, hb = self.waist
        m = p.ell(cx, ty + 6, rx, ry) | p.poly([(cx - wt, ty + 7), (cx + wt, ty + 7), (cx + wb, ty + hb), (cx - wb, ty + hb)])
        p.paint(m, self.tones, hi=0.24, sh=0.68)
        t = self.tones
        if self.pecs:
            sh = t[2]
            p.line([(cx - 7, ty + 9), (cx - 3, ty + 11), (cx, ty + 10)], sh, only=t[:2])
            p.line([(cx, ty + 10), (cx + 3, ty + 11), (cx + 7, ty + 9)], sh, only=t[:2])
            p.line([(cx, ty + 4), (cx, ty + 10)], sh, only=t[:2])
            for yy in (ty + 13, ty + 15):
                p.line([(cx - 3, yy), (cx + 3, yy)], sh, only=t[:2])
            p.line([(cx, ty + 11), (cx, ty + 17)], sh, only=t[:2])

    def frame(self, pose='idle', ph=0, bob=0):
        P = self.poses[pose]
        W = P.get('w', 48)
        bx = P.get('bx', 22)
        p = Pix(W, s=SCALE, ax=bx)
        oy = bob + P.get('sy', 0)
        lean = P['lean']
        cx = bx + lean
        ty = 17 + oy
        hx = cx - 5 + (1 if lean > 0 else 0) + self.hdx
        hy = 2 + oy + P.get('hy', 0) + self.hdy
        if self.back:
            self.back(p, self, hx, hy, cx, ty, ph, P)
        sw = self.shoulder

        def arm(a, near, **kw):
            d = sw if not near else -sw
            self.draw_arm(p, (cx + a[0] + d, ty + a[1]), (cx + a[2] + d, ty + a[3]), (cx + a[4], ty + a[5]), near, **kw)
        far, near = P['far'], P['near']
        if not P.get('far_front'):
            arm(far, False, fist=P.get('far_fist', True))
        if self.legs:
            for i, leg in enumerate(P['legs']):
                hip = (bx + leg[0] + lean // 2, ty + leg[1])
                knee = (bx + leg[2], ty + leg[3])
                foot = (bx + leg[4], ty + leg[5])
                self.draw_leg(p, hip, knee, foot, i == 1)
        elif self.lower:
            self.lower(p, cx, ty, ph, P)
        self.draw_torso(p, cx, ty)
        if self.torso_deco:
            self.torso_deco(p, cx, ty)
        if self.belt:
            self.belt(p, cx - (1 if lean > 1 else 0), ty + 18, ph)
        if self.pad:
            self.pad(p, cx + 8 + sw, ty + 2, False)
        if P.get('far_front'):
            arm(far, False, fist=P.get('far_fist', True))
        p.paint(p.cap(cx + 1, ty - 3, cx + 1, ty + 1, self.neck_r), self.tones)
        hd = g_lines(self.shout if P.get('shout') else self.head)
        hw, hh = len(hd[0]), len(hd)
        # 头底边落在躯干顶往下 1 格，中心对着胸口偏前
        left = int(round(p.tx(hx + 7.5) - hw / 2))
        top = int(round(p.ty(hy + 15) - hh))
        p.blit_grid(hd, left, top)
        if self.neck:
            self.neck(p, cx + 1, ty)
        if pose == 'rush':
            g_hi, g_out = self.ghost
            for side, dx, dy in GHOSTS[ph % 2]:
                sx, sy = (cx + 8, ty + 3) if side == 'f' else (cx - 4, ty + 5)
                fx, fy = cx + dx, ty + dy
                e = ((sx + fx) / 2 - 1, (sy + fy) / 2 + 2)
                self.draw_arm(p, (sx, sy), e, (fx, fy), False, tones=g_hi + self.tones[1] + self.tones[2],
                              outline=g_out)
        if self.pad:
            self.pad(p, cx - 8 - sw, ty + 2, True)
        arm(near, True, fist=P.get('near_fist', True))
        if pose == 'rush':
            g_hi, g_out = self.ghost
            for dx, dy in TIPS[ph % 2]:
                x, y = cx + dx, ty + dy
                p.line([(x - 12, y), (x - 5, y)], g_hi)
                p.line([(x - 9, y - 2), (x - 5, y - 2)], g_hi)
                p.paint(p.ell(x, y, 2.6, 2.4), self.fist_tones, outline=g_out, hi=0.4, sh=0.7)
        if self.front:
            self.front(p, cx, ty, ph, P)
        p.clean()
        return p.to_cv(self.pal, bx)

    def sheet(self, extra=None, drop=()):
        sh = Sheet('', '', kind='stand')
        anims = [('idle', [('idle', 0, 0), ('idle', 1, 1), ('idle', 2, 2), ('idle', 3, 1)], 6, 'loop'),
                 ('punch', [('punch0', 3, 0), ('punch1', 0, 0), ('punch2', 1, 0)], 12, 'oneshot'),
                 ('rush', [('rush', 0, 0), ('rush', 1, 0)], 16, 'loop'),
                 ('pose', [('pose', 0, 0), ('pose', 1, 1)], 4, 'loop'),
                 ('block', [('block', 0, 0)], 1, 'static'),
                 ('hurt', [('hurt', 1, 0)], 1, 'static')]
        for name, frames, fps, kind in anims + list(extra or []):
            if name in drop:
                continue
            sh.add(name, [self.frame(*f) for f in frames], fps, kind)
        return sh


def special(pal, anims, bx=22):
    """非人形替身：anims = [(动作名, [画一帧的函数(p)…], fps, kind, 画布宽)]"""
    sh = Sheet('', '', kind='stand')
    for name, fns, fps, kind, *rest in anims:
        w = rest[0] if rest else 48
        frames = []
        for fn in fns:
            p = Pix(w)
            fn(p)
            p.clean()
            frames.append(p.to_cv(pal, bx))
        sh.add(name, frames, fps, kind)
    return sh
