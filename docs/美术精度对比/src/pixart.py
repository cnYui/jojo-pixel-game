"""方案 A 手绘用的小工具：字母网格画布 + 补丁（patch）+ 自动 1px 描边。
画法：先拿原图 xBR 2 倍（不混色）当底稿、把 2px 描边削成 1px，再用手写补丁逐块重画。"""
import sys
sys.dont_write_bytecode = True
from PIL import Image
from common import xbr2x, img_to_grid, grid_to_img

T = '.'


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = [[T] * w for _ in range(h)]

    @classmethod
    def from_rows(cls, rows):
        c = cls(len(rows[0]), len(rows))
        c.a = [list(r) for r in rows]
        return c

    def get(self, x, y):
        return self.a[y][x] if 0 <= x < self.w and 0 <= y < self.h else T

    def put(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y][x] = ch

    def patch(self, x0, y0, text):
        """text：多行字符串；'.' 跳过（保留下面的），'_' 擦成透明，其它字母照写。
        每行可以用 'NN:' 开头写行号（只是给人看的，会被去掉）。"""
        lines = text.split('\n')
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        for j, ln in enumerate(lines):
            ln = ln.strip()
            if ':' in ln[:4]:
                ln = ln.split(':', 1)[1]
            ln = ln.replace('|', '')
            for i, ch in enumerate(ln):
                if ch == '.':
                    continue
                self.put(x0 + i, y0 + j, T if ch == '_' else ch)
        return self

    def rows(self):
        return [''.join(r) for r in self.a]

    def outline(self, k='k', keep=''):
        """自动描边：贴着透明的不透明像素改成 k（'keep' 里的字母不改）。"""
        out = [r[:] for r in self.a]
        for y in range(self.h):
            for x in range(self.w):
                ch = self.a[y][x]
                if ch == T or ch in keep:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if self.get(x + dx, y + dy) == T:
                        out[y][x] = k
                        break
        self.a = out
        return self

    def thin_outline(self, k='k'):
        """把 2 倍放大后 2px 宽的黑线削成 1px：外描边留贴透明的那一圈；内部黑线留左 / 上那一列。"""
        def edge(x, y):
            return any(self.get(x + dx, y + dy) == T for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        out = [r[:] for r in self.a]
        for y in range(self.h):
            for x in range(self.w):
                if self.a[y][x] != k or edge(x, y):
                    continue
                # 贴着外描边的内圈：换成对面的颜色
                for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if self.get(nx, ny) == k and edge(nx, ny):
                        ox, oy = x - dx, y - dy
                        c = self.get(ox, oy)
                        if c not in (T, k):
                            out[y][x] = c
                            break
                else:
                    # 内部双线：左边 / 上边也是 k、右边 / 下边是颜色 → 换成右 / 下的颜色
                    r, d = self.get(x + 1, y), self.get(x, y + 1)
                    if self.get(x - 1, y) == k and r not in (T, k):
                        out[y][x] = r
                    elif self.get(x, y - 1) == k and d not in (T, k):
                        out[y][x] = d
        self.a = out
        return self

    def image(self, pal):
        return grid_to_img(self.rows(), pal)


def base2x(fr, pal, margin=2):
    """原图一帧 → 2 倍底稿（xBR 不混色，只用原色）+ 削描边。返回 (Canvas, 裁剪原点)。"""
    bb = fr.getbbox()
    box = (bb[0] - margin, bb[1] - margin, bb[2] + margin, bb[3])
    c = fr.crop(box)
    up = xbr2x(c, blend=False)
    cv = Canvas.from_rows(img_to_grid(up, pal))
    cv.thin_outline()
    return cv, box


def sheet(images, scale, bg=(150, 150, 160, 255), gap=8, labels=None):
    """几张图按同一放大倍数横排，方便自己 Read 检查。"""
    ims = [im.resize((im.width * s, im.height * s), Image.NEAREST) for im, s in zip(images, scale)]
    W = sum(i.width for i in ims) + gap * (len(ims) + 1)
    H = max(i.height for i in ims) + gap * 2
    out = Image.new('RGBA', (W, H), bg)
    x = gap
    for i in ims:
        out.alpha_composite(i, (x, gap))
        x += i.width + gap
    return out
