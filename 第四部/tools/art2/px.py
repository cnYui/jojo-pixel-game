# 第四部重画（2026-11）用的像素画布：一格一格写像素，不缩放、不抗锯齿。
#   人物、替身、头像、背景都用这一套；颜色一律 '#rrggbb'（或 RGBA 元组），坐标是图像坐标（左上为原点）。
#   字符稿：一行字符串 = 一行像素，'.' 或空格 = 透明，其余字符查调色板。
import os

import numpy as np
from PIL import Image

OUTLINE = '#1a1020'          # 全游戏精灵统一的描边色（和第三部一样）
HERE = os.path.dirname(os.path.abspath(__file__))
P4 = os.path.normpath(os.path.join(HERE, '..', '..'))
ASSETS = os.path.join(P4, 'assets')
META = os.path.join(ASSETS, '_meta')


def rgba(c, a=255):
    if c is None:
        return (0, 0, 0, 0)
    if isinstance(c, str):
        s = c.lstrip('#')
        if len(s) == 8:
            return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4, 6))
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)
    c = tuple(int(v) for v in c)
    return c if len(c) == 4 else c + (a,)


def mix(a, b, k):
    a, b = rgba(a), rgba(b)
    return '#%02x%02x%02x' % tuple(int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))


def shade(c, k):
    """k < 0 变暗、k > 0 变亮（-1 … 1）；暗的时候往蓝紫偏一点，像素画的阴影不发灰"""
    return mix(c, '#140c24', -k) if k < 0 else mix(c, '#fff8e8', k)


def rows(text):
    """多行字符串 → 行列表（去掉首尾空行，保留行内的 '.'）"""
    out = [r for r in text.split('\n')]
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    w = max(len(r) for r in out) if out else 0
    return [r.ljust(w, '.') for r in out]


class Cv:
    """RGBA 画布"""

    def __init__(self, w, h, fill=None):
        self.w, self.h = int(w), int(h)
        self.a = np.zeros((self.h, self.w, 4), np.uint8)
        if fill:
            self.a[:, :] = rgba(fill)

    @classmethod
    def of(cls, img):
        im = img.convert('RGBA')
        c = cls(im.width, im.height)
        c.a = np.array(im)
        return c

    def copy(self):
        c = Cv(self.w, self.h)
        c.a = self.a.copy()
        return c

    def img(self):
        return Image.fromarray(self.a, 'RGBA')

    def inb(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def put(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            self.a[y, x] = rgba(c)

    def get(self, x, y):
        return tuple(self.a[y, x]) if self.inb(x, y) else (0, 0, 0, 0)

    def solid(self, x, y):
        return self.inb(x, y) and self.a[y, x, 3] > 0

    def clear(self, x, y):
        if self.inb(x, y):
            self.a[y, x] = (0, 0, 0, 0)

    def rect(self, x0, y0, x1, y1, c):
        """含两端"""
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w - 1, x1), min(self.h - 1, y1)
        if x1 >= x0 and y1 >= y0:
            self.a[y0:y1 + 1, x0:x1 + 1] = rgba(c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def line(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        e = dx + dy
        while True:
            self.put(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * e
            if e2 >= dy:
                e += dy
                x0 += sx
            if e2 <= dx:
                e += dx
                y0 += sy

    def ellipse(self, cx, cy, rx, ry, c):
        col = rgba(c)
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                if self.inb(x, y) and ((x - cx) / max(rx, .01)) ** 2 + ((y - cy) / max(ry, .01)) ** 2 <= 1.0:
                    self.a[y, x] = col

    def grid(self, rws, x, y, pal, flip=False):
        """贴一块字符稿；调色板里没有的字符报错（免得悄悄漏画）"""
        for j, r in enumerate(rws):
            n = len(r)
            for i, ch in enumerate(r):
                if ch in '. ':
                    continue
                if ch not in pal:
                    raise KeyError('调色板里没有字符 %r（第 %d 行：%s）' % (ch, j, r))
                c = pal[ch]
                if c is None:
                    continue
                self.put(x + (n - 1 - i if flip else i), y + j, c)

    def blit(self, other, x=0, y=0):
        """把 other 的不透明像素盖上来"""
        x, y = int(x), int(y)
        sx0, sy0 = max(0, -x), max(0, -y)
        sx1, sy1 = min(other.w, self.w - x), min(other.h, self.h - y)
        if sx1 <= sx0 or sy1 <= sy0:
            return
        src = other.a[sy0:sy1, sx0:sx1]
        dst = self.a[y + sy0:y + sy1, x + sx0:x + sx1]
        m = src[..., 3] > 0
        dst[m] = src[m]

    def under(self, other, x=0, y=0):
        """把 other 垫在下面（只填自己透明的地方）"""
        tmp = Cv(self.w, self.h)
        tmp.blit(other, x, y)
        m = (self.a[..., 3] == 0) & (tmp.a[..., 3] > 0)
        self.a[m] = tmp.a[m]

    def mask(self):
        return self.a[..., 3] > 0

    def outline(self, c=OUTLINE, diag=False):
        """给剪影外面描 1 px（只描在透明处）"""
        op = self.mask()
        nb = np.zeros_like(op)
        nb[1:, :] |= op[:-1, :]
        nb[:-1, :] |= op[1:, :]
        nb[:, 1:] |= op[:, :-1]
        nb[:, :-1] |= op[:, 1:]
        if diag:
            nb[1:, 1:] |= op[:-1, :-1]
            nb[1:, :-1] |= op[:-1, 1:]
            nb[:-1, 1:] |= op[1:, :-1]
            nb[:-1, :-1] |= op[1:, 1:]
        self.a[nb & ~op] = rgba(c)
        return self

    def flipx(self):
        c = Cv(self.w, self.h)
        c.a = self.a[:, ::-1].copy()
        return c

    def rot90(self, k=1):
        """逆时针转 k 个 90°"""
        c = Cv(1, 1)
        c.a = np.rot90(self.a, k).copy()
        c.h, c.w = c.a.shape[:2]
        return c

    def bbox(self):
        ys, xs = np.nonzero(self.mask())
        if not len(xs):
            return None
        return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())

    def recolor(self, mp):
        out = self.copy()
        for s, d in mp.items():
            s4, d4 = rgba(s), rgba(d)
            hit = (self.a[..., 0] == s4[0]) & (self.a[..., 1] == s4[1]) & (self.a[..., 2] == s4[2]) & (self.a[..., 3] > 0)
            out.a[hit] = d4
        return out


def scale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def ensure(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path
