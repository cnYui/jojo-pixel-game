"""美术精度对比：共用工具（读游戏图集、像素放大算法、点阵网格、UI 框和点阵字）。
只读游戏文件，只往 docs\\美术精度对比\\ 写。"""
import sys
sys.dont_write_bytecode = True
import json
import os
import numpy as np
from PIL import Image

GAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(GAME, 'docs', '美术精度对比')
SRC = os.path.join(OUT, 'src')
WORK = os.path.join(OUT, '_work')
os.makedirs(WORK, exist_ok=True)

_META = None


def meta():
    global _META
    if _META is None:
        with open(os.path.join(GAME, 'tools', '_meta', 'chars.json'), encoding='utf-8') as f:
            _META = json.load(f)
    return _META


def frame(cid, anim='idle', f=0):
    """游戏图集（assets\\chars\\<cid>.png）里的一帧 + pivot。返回 (RGBA Image, (px, py))。"""
    m = meta()['chars'][cid]
    a = m['animations'][anim]
    cw, ch = m['cell']
    im = Image.open(os.path.join(GAME, 'assets', m['image'] + '.png')).convert('RGBA')
    fr = im.crop((f * cw, a['row'] * ch, f * cw + cw, a['row'] * ch + ch))
    return fr, tuple(m['pivot'])


def bg_school(scale=1):
    """校门背景（school_gate：base + far + near，镜头 x = 0），320x180。"""
    d = os.path.join(GAME, 'assets', 'bg', 'school_gate')
    out = Image.new('RGBA', (320, 180), (0, 0, 0, 255))
    for l in ('base', 'far', 'near'):
        im = Image.open(os.path.join(d, l + '.png')).convert('RGBA')
        out.alpha_composite(im.crop((0, 0, 320, 180)))
    return out


# ------------------------------------------------------------------ 放大算法
def _a(img):
    return np.array(img.convert('RGBA'), dtype=np.int32)


def _pad(a, n):
    return np.pad(a, ((n, n), (n, n), (0, 0)), mode='edge')


def _key(a):
    """RGBA → 单个整数（透明统一成 0），用来判断“同色”。"""
    k = (a[..., 0] << 24) | (a[..., 1] << 16) | (a[..., 2] << 8) | a[..., 3]
    return np.where(a[..., 3] == 0, 0, k)


def scale2x(img):
    """Scale2x / EPX（AdvMAME2x）：只复制邻居颜色，不产生新颜色。"""
    a = _a(img)
    k = _key(a)
    kp = np.pad(k, 1, mode='edge')
    B, D, F, H = kp[:-2, 1:-1], kp[1:-1, :-2], kp[1:-1, 2:], kp[2:, 1:-1]
    ap = _pad(a, 1)
    cB, cD, cF, cH = ap[:-2, 1:-1], ap[1:-1, :-2], ap[1:-1, 2:], ap[2:, 1:-1]
    h, w = k.shape
    out = np.zeros((h * 2, w * 2, 4), np.int32)
    c0 = (D == B) & (B != F) & (D != H)
    c1 = (B == F) & (B != D) & (F != H)
    c2 = (D == H) & (D != B) & (H != F)
    c3 = (H == F) & (D != H) & (B != F)
    out[0::2, 0::2] = np.where(c0[..., None], cD, a)
    out[0::2, 1::2] = np.where(c1[..., None], cF, a)
    out[1::2, 0::2] = np.where(c2[..., None], cD, a)
    out[1::2, 1::2] = np.where(c3[..., None], cF, a)
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def _yuv_dist(p, q):
    """xBR 用的 YUV 加权距离；透明和不透明之间给大距离。"""
    pr, pg, pb, pa = p[..., 0], p[..., 1], p[..., 2], p[..., 3]
    qr, qg, qb, qa = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    dr, dg, db = pr - qr, pg - qg, pb - qb
    y = np.abs(0.299 * dr + 0.587 * dg + 0.114 * db)
    u = np.abs(-0.169 * dr - 0.331 * dg + 0.5 * db)
    v = np.abs(0.5 * dr - 0.419 * dg - 0.081 * db)
    d = 48 * y + 7 * u + 6 * v
    both0 = (pa == 0) & (qa == 0)
    d = np.where(both0, 0, d)
    d = np.where((pa == 0) != (qa == 0), 48 * 255, d)
    return d


def _xbr_corner(a, blend):
    """2xBR（Hyllian）右下角规则；返回 (是否改, 新颜色)。a 已 pad 2。"""
    def P(dx, dy):
        h, w = a.shape[0] - 4, a.shape[1] - 4
        return a[2 + dy:2 + dy + h, 2 + dx:2 + dx + w]
    E = P(0, 0); B = P(0, -1); C = P(1, -1); D = P(-1, 0); F = P(1, 0)
    G = P(-1, 1); H = P(0, 1); I = P(1, 1)
    F4 = P(2, 0); I4 = P(2, 1); H5 = P(0, 2); I5 = P(1, 2)
    d = _yuv_dist
    wd_hf = d(E, C) + d(E, G) + d(I, F4) + d(I, H5) + 4 * d(H, F)
    wd_ei = d(H, D) + d(H, I5) + d(F, I4) + d(F, B) + 4 * d(E, I)
    edge = (wd_hf < wd_ei) & (_key(E) != _key(F)) & (_key(E) != _key(H))
    pick_f = d(E, F) <= d(E, H)
    newc = np.where(pick_f[..., None], F, H)
    if blend:
        newc = (E + newc) // 2
    return edge, newc


def xbr2x(img, blend=True):
    """2xBR：沿斜边把角上的子像素换成邻色（blend=True 时取一半，产生过渡色）。"""
    a = _a(img)
    h, w = a.shape[:2]
    out = np.zeros((h * 2, w * 2, 4), np.int32)
    out[0::2, 0::2] = a; out[0::2, 1::2] = a; out[1::2, 0::2] = a; out[1::2, 1::2] = a
    # 四个角：把图旋转，套右下角规则，再转回来
    # np.rot90(a, k)：k=1 时旋转后图的右下角 = 原图左下角，k=3 时 = 原图右上角
    for rot, (oy, ox) in ((0, (1, 1)), (1, (1, 0)), (2, (0, 0)), (3, (0, 1))):
        r = np.rot90(a, rot)
        edge, newc = _xbr_corner(_pad(r, 2), blend)
        edge = np.rot90(edge, -rot)
        newc = np.rot90(newc, -rot)
        sub = out[oy::2, ox::2]
        sub[edge] = newc[edge]
        out[oy::2, ox::2] = sub
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')


def nearest(img, s):
    return img.resize((img.width * s, img.height * s), Image.NEAREST)


# ------------------------------------------------------------------ 点阵网格（文本 ↔ 图）
def parse_grid(text):
    rows = [r.rstrip('\n') for r in text.strip('\n').split('\n')]
    rows = [r for r in rows if not r.startswith('#')]
    w = max(len(r) for r in rows)
    return [r.ljust(w, '.') for r in rows]


def grid_to_img(rows, pal):
    h, w = len(rows), len(rows[0])
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in '. ':
                continue
            c = pal[ch]
            px[x, y] = hexrgb(c) + (255,)
    return im


def img_to_grid(im, pal):
    inv = {hexrgb(v): k for k, v in pal.items() if v}
    rows = []
    px = im.convert('RGBA').load()
    for y in range(im.height):
        r = ''
        for x in range(im.width):
            p = px[x, y]
            if p[3] == 0:
                r += '.'
            else:
                r += inv.get(p[:3], '?')
        rows.append(r)
    return rows


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_grid_file(path):
    with open(path, encoding='utf-8') as f:
        return parse_grid(f.read())


# ------------------------------------------------------------------ 合成
def put(canvas, spr, pivot, x, y, flip=False, alpha=1.0):
    """把精灵按 pivot 贴到 (x, y)（脚点），alpha < 1 时整体半透明。"""
    s = spr.transpose(Image.FLIP_LEFT_RIGHT) if flip else spr
    px, py = pivot
    if flip:
        px = spr.width - px
    if alpha < 1:
        s = s.copy()
        a = np.array(s)
        a[..., 3] = (a[..., 3].astype(np.float32) * alpha).astype(np.uint8)
        s = Image.fromarray(a, 'RGBA')
    canvas.alpha_composite(s, (int(round(x - px)), int(round(y - py))))


def aura(spr, color, grow=1, alpha=0.55):
    """光环剪影：4 邻域膨胀 grow 像素，填光环色（同 atlas.js _auraCanvas）。"""
    a = np.array(spr.convert('RGBA'))
    m = a[..., 3] > 0
    m = np.pad(m, grow)
    for _ in range(grow):
        n = m.copy()
        n[1:] |= m[:-1]; n[:-1] |= m[1:]; n[:, 1:] |= m[:, :-1]; n[:, :-1] |= m[:, 1:]
        m = n
    r, g, b = hexrgb(color)
    out = np.zeros(m.shape + (4,), np.uint8)
    out[m] = (r, g, b, int(255 * alpha))
    return Image.fromarray(out, 'RGBA')


# ------------------------------------------------------------------ 点阵字 + UI 框（照 engine\\ui.js / font.js）
class Font:
    def __init__(self, size=16):
        with open(os.path.join(GAME, 'tools', '_meta', 'font.json'), encoding='utf-8') as f:
            m = json.load(f)
        m = m.get(str(size)) or m['font'][str(size)]
        self.m = m
        self.lh = m['lh']
        self.size = size
        self.img = Image.open(os.path.join(GAME, 'assets', m['image'] + '.png')).convert('RGBA')
        self.mask = np.array(self.img)[..., 3] > 0
        self.missing = set()

    def adv(self, ch):
        gl = self.m['glyphs'].get(ch)
        if gl:
            return gl[2]
        return self.size // 2 if ord(ch) < 128 else self.size

    def width(self, s):
        return sum(self.adv(c) for c in s)

    def raw(self, im, s, x, y, color):
        r, g, b = hexrgb(color)
        cx = x
        for ch in s:
            gl = self.m['glyphs'].get(ch)
            if gl:
                gx, gy, gw = gl
                m = self.mask[gy:gy + self.lh, gx:gx + gw]
                ys, xs = np.nonzero(m)
                px = im.load()
                for yy, xx in zip(ys, xs):
                    X, Y = cx + xx, y + yy
                    if 0 <= X < im.width and 0 <= Y < im.height:
                        px[X, Y] = (r, g, b, 255)
            elif ch not in ' 　':
                self.missing.add(ch)
            cx += self.adv(ch)
        return cx

    def draw(self, im, s, x, y, color='#ffffff', outline=None, align='left'):
        w = self.width(s)
        if align == 'center':
            x -= w // 2
        elif align == 'right':
            x -= w
        if outline:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
                self.raw(im, s, x + dx, y + dy, outline)
        self.raw(im, s, x, y, color)
        return w


def rect(im, x, y, w, h, rgba):
    if w <= 0 or h <= 0:
        return
    layer = Image.new('RGBA', (w, h), rgba)
    if rgba[3] == 255:
        im.paste(layer, (x, y))
    else:
        im.alpha_composite(layer, (x, y))


def ui_box(im, x0, y0, x1, y1, fill=(16, 14, 40, 224), border=(255, 255, 255, 255)):
    """engine\\ui.js box()：投影、2px 黑边、2px 白框、1px 暗线。"""
    w, h = x1 - x0 + 1, y1 - y0 + 1
    rect(im, x1 + 1, y0 + 4, 4, h, (0, 0, 0, 160))
    rect(im, x0 + 4, y1 + 1, w - 4, 4, (0, 0, 0, 160))
    K = (0, 0, 0, 255)
    rect(im, x0, y0, w, 2, K); rect(im, x0, y1 - 1, w, 2, K)
    rect(im, x0, y0 + 2, 2, h - 4, K); rect(im, x1 - 1, y0 + 2, 2, h - 4, K)
    rect(im, x0 + 2, y0 + 2, w - 4, h - 4, fill)
    rect(im, x0 + 2, y0 + 2, w - 4, 2, border); rect(im, x0 + 2, y1 - 3, w - 4, 2, border)
    rect(im, x0 + 2, y0 + 2, 2, h - 4, border); rect(im, x1 - 3, y0 + 2, 2, h - 4, border)
    sh = (0, 0, 0, 120)
    rect(im, x0 + 4, y0 + 4, w - 8, 1, sh); rect(im, x0 + 4, y1 - 4, w - 8, 1, sh)
    rect(im, x0 + 4, y0 + 5, 1, h - 10, sh); rect(im, x1 - 4, y0 + 5, 1, h - 10, sh)


def glyph_next(im, x, y, color=(255, 255, 255, 255)):
    for r in range(5):
        rect(im, x + r, y + r, 9 - 2 * r, 1, color)
