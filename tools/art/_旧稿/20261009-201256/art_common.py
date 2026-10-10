"""art_common -- 包 7A 公共工具：路径、不写字节码、预览图、像素后处理小工具。

只读调用原工程（源码\\engine、源码\\assets、烘焙脚本\\bake_characters.py），不在受保护目录写任何东西。
本模块 import 时**不** import assets（bake_art 要先用 bake_characters.load_registry 拿到原 166 个精灵名，
再 import 我们的 art_* 模块；见 bake_art.py）。art_* 模块自己 `from assets import ...`。
"""
import sys
sys.dont_write_bytecode = True          # 必须在 import 原工程之前

import os

ROOT = r'D:\大疆\游戏素材\JoJo'
SRC = os.path.join(ROOT, '源码')
BAKE_DIR = os.path.join(ROOT, '烘焙脚本')
ATLAS_DIR = os.path.join(ROOT, '角色图集')
GAME = os.path.join(ROOT, '游戏')
ART = os.path.dirname(os.path.abspath(__file__))
PREVIEW = os.path.join(ART, '_preview')
CHARS_NEW = os.path.join(GAME, 'assets', 'chars_new')
PROPS_NEW = os.path.join(GAME, 'assets', 'props_new')

for _p in (ART, BAKE_DIR, SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np                       # noqa: E402
from PIL import Image, ImageDraw, ImageFont   # noqa: E402

OUTLINE_RGB = (0x1a, 0x10, 0x20)        # 原工程描边色 k
SCALE = 4


# =================================================================== 字体 / 底纹
_FONT = {}


def font(size):
    if size not in _FONT:
        for p in (r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simsun.ttc'):
            if os.path.exists(p):
                _FONT[size] = ImageFont.truetype(p, size)
                break
        else:
            _FONT[size] = ImageFont.load_default()
    return _FONT[size]


def checker(w, h, sq=16, c1=(218, 218, 224), c2=(196, 196, 206)):
    ys, xs = np.mgrid[0:h, 0:w]
    m = (((xs // sq) + (ys // sq)) % 2)[..., None]
    arr = np.where(m == 0, np.array(c1, np.uint8), np.array(c2, np.uint8)).astype(np.uint8)
    return Image.fromarray(arr, 'RGB')


# =================================================================== 精灵查询
def sprite_mod():
    from engine import sprite
    return sprite


def frames_of(name):
    return sprite_mod().get(name).frames


def anchor_of(name, fi=0):
    """精灵第 fi 帧的锚点像素坐标（同 engine.sprite._anchor_px，取整）。"""
    sp = sprite_mod()
    sd = sp.get(name)
    w, h = sd.frames[fi].size
    ax, ay = sp._anchor_px(sd.anchor, w, h)
    return int(ax), int(ay)


# =================================================================== 像素后处理（PIL RGBA）
def strip_outline(im, rgb=OUTLINE_RGB):
    """去掉最外圈的描边像素（只去和透明相邻的描边色像素）。"""
    a = np.array(im.convert('RGBA'))
    op = a[..., 3] > 0
    isk = op & (a[..., 0] == rgb[0]) & (a[..., 1] == rgb[1]) & (a[..., 2] == rgb[2])
    tr = ~op
    nb = np.zeros_like(tr)
    nb[1:, :] |= tr[:-1, :]
    nb[:-1, :] |= tr[1:, :]
    nb[:, 1:] |= tr[:, :-1]
    nb[:, :-1] |= tr[:, 1:]
    nb[0, :] = nb[-1, :] = True
    nb[:, 0] = nb[:, -1] = True
    edge = isk & nb
    a[edge] = 0
    return Image.fromarray(a, 'RGBA')


def add_outline(im, rgb=OUTLINE_RGB, pad=0):
    """所有和不透明像素 4 邻接的透明像素涂成描边色（pad>0 时先扩画布）。"""
    im = im.convert('RGBA')
    if pad:
        c = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        c.paste(im, (pad, pad))
        im = c
    a = np.array(im)
    m = a[..., 3] > 0
    g = np.zeros_like(m)
    g[1:, :] |= m[:-1, :]
    g[:-1, :] |= m[1:, :]
    g[:, 1:] |= m[:, :-1]
    g[:, :-1] |= m[:, 1:]
    ring = g & ~m
    a[ring] = list(rgb) + [255]
    return Image.fromarray(a, 'RGBA')


def crop_alpha(im):
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def crop_keep_pivot(im, pivot, margin=1):
    """裁掉透明边（留 margin），返回 (裁后的图, 裁后坐标里的 pivot)。预览用：pivot 不在图内也照样对齐。"""
    bb = im.getbbox()
    px, py = pivot
    if not bb:
        return im, (px, py)
    x0 = max(0, min(bb[0], px) - margin)
    y0 = max(0, min(bb[1], py) - margin)
    x1 = min(im.width, max(bb[2], px + 1) + margin)
    y1 = min(im.height, max(bb[3], py) + margin)
    return im.crop((x0, y0, x1, y1)), (px - x0, py - y0)


def shear_rows(im, k, pivot_y, rigid_y=None):
    """按行剪切（s13_vanilla._van_hurt 的配方）：pivot 行以上每行平移 round(k*(pivot-y))；
    rigid_y 以上整体平移（头不变形）。k>0 往右（前倾），k<0 往左（后仰）。画布左右各扩 |k|*pivot。"""
    a = np.array(im.convert('RGBA'))
    h, w = a.shape[:2]
    ext = int(abs(k) * pivot_y) + 2
    out = np.zeros((h, w + 2 * ext, 4), np.uint8)
    head_d = None if rigid_y is None else int(round(k * (pivot_y - rigid_y)))
    for y in range(h):
        if rigid_y is not None and y < rigid_y:
            d = head_d
        else:
            d = int(round(k * (pivot_y - y))) if y < pivot_y else 0
        out[y, ext + d:ext + d + w] = a[y]
    return Image.fromarray(out, 'RGBA'), ext


def recolor_im(im, mapping):
    """{(r,g,b): (r,g,b)} 精确换色（s09_india._recolor 的做法）。"""
    a = np.array(im.convert('RGBA')).copy()
    src = a.copy()
    for sc, dc in mapping.items():
        m = (src[..., 0] == sc[0]) & (src[..., 1] == sc[1]) & (src[..., 2] == sc[2]) & (src[..., 3] > 0)
        a[m, :3] = dc
    return Image.fromarray(a, 'RGBA')


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# =================================================================== 预览图
def _label(d, x, y, s, size=13, fill=(30, 28, 50)):
    d.text((x, y), s, font=font(size), fill=fill)


def preview_items(items, path, title='', scale=SCALE, gap=10, max_w=2200, bg_ground=True):
    """items = [(标签, PIL RGBA 帧, (ax, ay) 锚点)]；同一行里所有帧锚点对齐到同一条地面线（4 倍最近邻）。
    超宽自动折行。洋红小十字 = 锚点。"""
    rows, cur, cur_w = [], [], 0
    for it in items:
        lab, im, (ax, ay) = it
        w = max(im.width * scale, 60) + gap * 2
        if cur and cur_w + w > max_w:
            rows.append(cur)
            cur, cur_w = [], 0
        cur.append((lab, im, ax, ay, w))
        cur_w += w
    if cur:
        rows.append(cur)
    lay = []
    y = 40 if title else 8
    width = 0
    for r in rows:
        up = max(ay for _, _, _, ay, _ in r) * scale
        dn = max(im.height - ay for _, im, _, ay, _ in r) * scale
        lay.append((r, y, up, dn))
        y += 22 + up + dn + 18
        width = max(width, sum(w for *_, w in r) + 16)
    W = max(width, 400)
    img = checker(W, y + 4, sq=4 * scale)
    d = ImageDraw.Draw(img)
    if title:
        d.rectangle((0, 0, W, 32), fill=(36, 34, 48))
        _label(d, 10, 6, title, 17, (255, 236, 160))
    for r, y0, up, dn in lay:
        x = 8
        base = y0 + 22 + up
        if bg_ground:
            d.line((0, base, W, base), fill=(150, 150, 175))
        for lab, im, ax, ay, w in r:
            _label(d, x + 4, y0, lab, 12)
            big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
            px, py = x + gap, base - ay * scale
            cx = px + ax * scale
            img.paste(big, (px, py), big)
            d.line((cx - 5, base, cx + 5, base), fill=(255, 0, 120))
            d.line((cx, base - 5, cx, base + 5), fill=(255, 0, 120))
            x += w
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, optimize=True)
    return path


def preview_names(names, path, title='', compare=(), scale=SCALE, extra_items=()):
    """把若干精灵（每个全部帧）按锚点对齐画成预览；compare = 放在最前面做对照的原精灵名（只取第 0 帧）。"""
    items = []
    for n in compare:
        fr = frames_of(n)
        items.append((f'{n}[0] (原)', fr[0], anchor_of(n, 0)))
    for n in names:
        fr = frames_of(n)
        for i, im in enumerate(fr):
            items.append((f'{n}[{i}]', im, anchor_of(n, i)))
    items += list(extra_items)
    return preview_items(items, path, title, scale)


def zoom_image(im, scale=6, bgc=None):
    """单张图放大看细节（棋盘底）。"""
    big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    bg = checker(big.width, big.height, sq=scale * 2)
    bg.paste(big, (0, 0), big)
    return bg
