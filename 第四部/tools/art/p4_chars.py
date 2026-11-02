# 第四部角色图集：拿第三部的全尺寸图集（assets/chars_new，只读）当底子改——换发型、换配色、换徽章，
#   保证和第三部同一套画风、同一套动作帧；改好的全尺寸图集存 第四部/assets/chars_full/，
#   再用第三部的 shrink.py（多数色 + 描边优先）缩成游戏尺寸，存 第四部/assets/chars/，元数据写进 _meta/chars.json。
#   用法：python3 第四部/tools/art/p4_chars.py [cid ...]
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_heads as HD  # noqa: E402

sys.path.insert(0, os.path.join(L.REPO, 'tools', 'art'))
import shrink as SH  # noqa: E402

O = (26, 16, 32)          # 描边
FULL = os.path.join(L.ASSETS, 'chars_full')


# ============================================================ 读底图
def base(name):
    m = L.load_json(os.path.join(L.P3_CHARS, name, name + '.json'))
    im = Image.open(os.path.join(L.P3_CHARS, name, m['image'])).convert('RGBA')
    return im, m


def frames(name, anim, n=None):
    im, m = base(name)
    a = m['animations'][anim]
    cw, ch = m['cell']
    k = a['frames'] if n is None else n
    return [im.crop((i * cw, a['row'] * ch, (i + 1) * cw, (a['row'] + 1) * ch)) for i in range(k)]


def heads(name):
    """第三部的说话头像（头像/xxx_0.png …）→ {表情 id: [Image…]}"""
    _, m = base(name)
    out = {}
    for ex in m.get('expressions', []):
        out[ex['id']] = [Image.open(os.path.join(L.P3_CHARS, name, f)).convert('RGBA') for f in ex['files']]
    return out


# ============================================================ 像素工具
def rgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) if isinstance(c, str) else tuple(c[:3])


def recolor(img, mapping, box=None, keep=None):
    """按颜色精确换色；box = (x0, y0, x1, y1) 只换这个框里的；mapping 的值可以是 None（挖掉）。"""
    a = np.array(img.convert('RGBA'))
    h, w = a.shape[:2]
    x0, y0, x1, y1 = box if box else (0, 0, w, h)
    sub = a[max(0, y0):min(h, y1), max(0, x0):min(w, x1)]
    for src, dst in mapping.items():
        s = rgb(src)
        hit = (sub[..., 0] == s[0]) & (sub[..., 1] == s[1]) & (sub[..., 2] == s[2]) & (sub[..., 3] > 0)
        if dst is None:
            sub[hit] = (0, 0, 0, 0)
        else:
            d = rgb(dst)
            sub[hit, 0], sub[hit, 1], sub[hit, 2] = d
    return Image.fromarray(a, 'RGBA')


def comp(img, color_set, box=None):
    """属于 color_set 的像素蒙版（bool 数组）"""
    a = np.array(img.convert('RGBA'))
    h, w = a.shape[:2]
    m = np.zeros((h, w), bool)
    for c in color_set:
        c = rgb(c)
        m |= (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
    if box:
        x0, y0, x1, y1 = box
        keep = np.zeros_like(m)
        keep[max(0, y0):y1, max(0, x0):x1] = True
        m &= keep
    return m


def blobs(mask):
    """4 连通块（不依赖 scipy）：返回 [(像素数, ys, xs)…]，大的在前"""
    h, w = mask.shape
    seen = np.zeros_like(mask)
    out = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                st = [(y, x)]
                seen[y, x] = True
                ys, xs = [], []
                while st:
                    cy, cx = st.pop()
                    ys.append(cy)
                    xs.append(cx)
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            st.append((ny, nx))
                out.append((len(ys), np.array(ys), np.array(xs)))
    out.sort(key=lambda t: -t[0])
    return out


def reoutline(img, color=O):
    """透明像素挨着不透明像素（4 邻）就描成描边色"""
    a = np.array(img.convert('RGBA'))
    op = a[..., 3] > 0
    nb = np.zeros_like(op)
    nb[1:, :] |= op[:-1, :]
    nb[:-1, :] |= op[1:, :]
    nb[:, 1:] |= op[:, :-1]
    nb[:, :-1] |= op[:, 1:]
    add = nb & ~op
    a[add] = (*color, 255)
    return Image.fromarray(a, 'RGBA')


def strip_outline(img, color=O):
    """去掉“孤立在外面”的描边：描边像素四周没有非描边的不透明像素就挖掉（换发型以后旧帽子的描边残留）"""
    a = np.array(img.convert('RGBA'))
    c = rgb(color)
    isO = (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
    body = (a[..., 3] > 0) & ~isO
    nb = np.zeros_like(body)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nb |= np.roll(np.roll(body, dy, 0), dx, 1)
    a[isO & ~nb] = (0, 0, 0, 0)
    return Image.fromarray(a, 'RGBA')


def put(img, pts, color):
    a = np.array(img.convert('RGBA'))
    h, w = a.shape[:2]
    c = rgb(color)
    for x, y in pts:
        if 0 <= x < w and 0 <= y < h:
            a[y, x] = (*c, 255)
    return Image.fromarray(a, 'RGBA')


def flipx(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


# ============================================================ 图集组装
class Sheet:
    def __init__(self, cid, name, cell, pivot):
        self.cid, self.name, self.cell, self.pivot = cid, name, list(cell), list(pivot)
        self.rows = []          # (anim, [frames], fps, kind)
        self.heads = {}         # emotion → [Image 32×32 …]

    def add(self, anim, frs, fps=6, kind='loop'):
        cw, ch = self.cell
        fixed = []
        for f in frs:
            if f.size != (cw, ch):
                c = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
                c.alpha_composite(f.crop((0, 0, min(cw, f.width), min(ch, f.height))), (0, 0))
                f = c
            fixed.append(f)
        self.rows.append((anim, fixed, fps, kind))

    def image(self):
        cw, ch = self.cell
        n = max(len(r[1]) for r in self.rows)
        im = Image.new('RGBA', (cw * n, ch * len(self.rows)), (0, 0, 0, 0))
        for r, (_, frs, _, _) in enumerate(self.rows):
            for i, f in enumerate(frs):
                im.alpha_composite(f, (i * cw, r * ch))
        return im

    def anims(self):
        return {a: dict(row=r, frames=len(frs), fps=fps, kind=kind) for r, (a, frs, fps, kind) in enumerate(self.rows)}


AMAP_HUMAN = {'cmd': 'point', 'cmd2': 'point', 'cmd_hold': 'point', 'guard': 'guard', 'dodge': 'dodge', 'down': 'down',
              'hurt': 'hurt', 'special': 'pose', 'win': 'pose', 'talk': 'idle', 'getup': 'hurt'}


def save(sh, amap=None, kind='char', bodyW=None, top_anim='idle'):
    """存全尺寸图集 + 缩小后的游戏图集 + 头像；返回 chars.json 里这个角色的条目"""
    os.makedirs(FULL, exist_ok=True)
    full = sh.image()
    full.save(os.path.join(FULL, sh.cid + '.png'))
    L.save_json(os.path.join(FULL, sh.cid + '.json'), dict(id=sh.cid, name=sh.name, image=sh.cid + '.png', cell=sh.cell,
                                                           pivot=sh.pivot, animations=sh.anims()))
    small, cell, pivot = SH.shrink_sheet(full, sh.cell, sh.pivot, SH.CK)
    out = os.path.join(L.ASSETS, 'chars', sh.cid + '.png')
    L.ensure(out)
    small.save(out)
    hk = {}
    for emo, frs in sh.heads.items():
        keys = []
        for i, f in enumerate(frs):
            key = f'heads/{sh.cid}/{emo}_{i}'
            p = os.path.join(L.ASSETS, key + '.png')
            L.ensure(p)
            f.save(p)
            keys.append(key)
        hk[emo] = keys
    anims = sh.anims()
    # top：待机第 0 帧的不透明包围盒顶到脚点的高度（缩小后的像素）
    a = anims.get(top_anim) or next(iter(anims.values()))
    fr = small.crop((0, a['row'] * cell[1], cell[0], (a['row'] + 1) * cell[1]))
    bb = fr.getbbox() or (0, 0, cell[0], cell[1])
    names = set(anims)
    am = {k: v for k, v in (amap or {}).items() if (v if isinstance(v, str) else v.get('a')) in names}
    return dict(name=sh.name, image='chars/' + sh.cid, cell=cell, pivot=pivot, animations=anims, aliases={}, heads=hk,
                headAlias={}, headSize={}, k=SH.CK, amap=am, top=int(pivot[1] - bb[1]),
                bodyW=bodyW if bodyW else max(3, int(round((bb[2] - bb[0]) * 0.3))), kind=kind)


# ============================================================ 东方仗助：承太郎的身体 + 飞机头
SKIN = [(246, 196, 154), (216, 148, 108)]
EYES = [(239, 230, 210), (44, 196, 168), (255, 255, 255), (92, 94, 224)]
NAVY = [(43, 49, 96), (24, 26, 56), (84, 98, 168), (28, 28, 52), (48, 48, 78)]
GOLD = [(255, 216, 60), (200, 154, 32)]
# 仗助的头发：近黑的深紫，高光偏蓝紫（动画里的颜色）
JH = dict(o=O, d=(18, 14, 26), m=(36, 30, 54), l=(66, 58, 100), x=(122, 114, 176))
# 校服：比承太郎的藏青更亮一点、更偏蓝紫
JOSUKE_COAT = {(84, 98, 168): (104, 102, 200), (43, 49, 96): (54, 52, 118), (24, 26, 56): (30, 28, 70),
               (28, 28, 52): (34, 30, 66), (48, 48, 78): (58, 54, 98)}


def face_box(img, top_rows=24, skin=None):
    """脸 = 包围盒顶上 top_rows 行里最大的一块皮肤色连通块；返回 (x0, y0, x1, y1)（含）或 None"""
    bb = img.getbbox()
    if not bb:
        return None
    m = comp(img, (skin or SKIN) + EYES, (0, bb[1], img.width, bb[1] + top_rows))
    bl = blobs(m)
    if not bl or bl[0][0] < 12:
        return None
    _, ys, xs = bl[0]
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def pompadour_mask(w, h, fx0, fy0, fx1, fy1, s=1.0):
    """飞机头 + 后脑的头发形状（朝右）。返回 (mask, shade)：shade 0 暗 / 1 中 / 2 亮 / 3 最亮。
    卷是一个往前上方翘 12° 的椭圆：前端高、后端低，下沿是斜的（平的下沿看起来像帽檐）。"""
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cx, cy = fx0 + 2.5 * s, fy0 - 0.5 * s
    skull = ((xx - cx) / (8.0 * s)) ** 2 + ((yy - cy) / (6.0 * s)) ** 2 <= 1
    skull &= yy <= fy0 + 0.5 * s
    px, py = fx1 - 1.2 * s, fy0 - 5.0 * s
    ang = np.deg2rad(-12)
    u = ((xx - px) * np.cos(ang) + (yy - py) * np.sin(ang)) / (8.0 * s)
    v = (-(xx - px) * np.sin(ang) + (yy - py) * np.cos(ang)) / (4.2 * s)
    roll = u * u + v * v <= 1
    tip = ((xx - (fx1 + 4.6 * s)) / (2.4 * s)) ** 2 + ((yy - (fy0 - 7.4 * s)) / (2.4 * s)) ** 2 <= 1
    back = (xx >= fx0 - 5.5 * s) & (xx <= fx0 + 1.5 * s) & (yy >= fy0 - 1) & (yy <= fy1 - 2.5 * s)
    nape = ((xx - (fx0 - 1.0 * s)) / (4.5 * s)) ** 2 + ((yy - (fy1 - 3.5 * s)) / (2.6 * s)) ** 2 <= 1
    back = back & ((yy <= fy1 - 4.5 * s) | nape)
    side = (xx >= fx0 + 1.5 * s) & (xx <= fx0 + 2.5 * s) & (yy >= fy0) & (yy <= fy0 + 2.5 * s)
    mask = skull | roll | tip | back | side
    shade = np.ones((h, w), int)
    up = np.zeros_like(mask)
    up[1:, :] = mask[:-1, :]
    rim = mask & ~up
    shade[rim & (xx > fx0 - 4 * s)] = 2
    shade[(roll | tip) & (v < -0.45) & (u > -0.5)] = 2
    shine = (roll | tip) & (v < -0.55) & (u > 0.15) & (u < 0.75)
    shade[shine] = 3
    shade[tip & ~roll & (yy < fy0 - 8.2 * s)] = 3
    under = roll & (v > 0.5) & (u > -0.35)
    shade[under] = 0
    shade[back & (yy > fy0 + 1.5 * s)] = 0
    shade[side] = 0
    return mask, shade


def josuke_head(img, s=1.0, top_rows=24, extra_clear=None):
    fb = face_box(img, top_rows)
    if not fb:
        return img
    fx0, fy0, fx1, fy1 = fb
    a = np.array(img.convert('RGBA'))
    h, w = a.shape[:2]
    # 1) 挖掉旧帽子和长发：脸上方、脸后方、下巴以上的藏青 / 金色 / 描边像素
    box = (int(fx0 - 13 * s), 0, int(fx1 + 4 * s), fy1 + 1)
    old = comp(img, NAVY + GOLD + [O], box)
    # 脸前面（x > fx1）只挖下巴以上、脸顶以上的部分（别挖到伸到前面的手）
    yy, xx = np.mgrid[0:h, 0:w]
    old &= ~((xx > fx1) & (yy > fy0))
    if extra_clear is not None:
        old |= extra_clear
    a[old] = (0, 0, 0, 0)
    # 2) 画新头发
    mask, shade = pompadour_mask(w, h, fx0, fy0, fx1, fy1, s)
    skin = comp(Image.fromarray(a, 'RGBA'), SKIN + EYES)
    mask &= ~(skin & (yy >= fy0))          # 脸露出来
    pal = {0: JH['d'], 1: JH['m'], 2: JH['l'], 3: JH['x']}
    for k, c in pal.items():
        sel = mask & (shade == k)
        a[sel] = (*c, 255)
    img2 = Image.fromarray(a, 'RGBA')
    # 3) 描边：头发外缘 + 头发和脸之间（额头那一条）
    img2 = reoutline(img2)
    b = np.array(img2)
    hair = mask
    face = comp(img2, SKIN + EYES)
    below = np.zeros_like(hair)
    below[1:, :] = hair[:-1, :]
    edge = face & below & (yy == fy0)
    # 额头只描一半：前额那几格保留皮肤（不然整条眉毛压黑）
    edge &= xx < fx0 + (fx1 - fx0) * 0.45
    b[edge] = (*O, 255)
    return Image.fromarray(b, 'RGBA')


def heart_badge(img, x, y, c1=(255, 216, 60), c2=(200, 154, 32)):
    return put(put(img, [(x, y), (x + 2, y), (x, y + 1), (x + 1, y + 1), (x + 2, y + 1)], c1), [(x + 1, y + 2)], c2)


JEYE = (92, 94, 224)


def josuke_body(f, collar=True):
    f = recolor(f, JOSUKE_COAT)
    f = recolor(f, {(44, 196, 168): JEYE})
    fb = face_box(f)
    f = josuke_head(f)
    if fb and collar:
        fx0, fy0, fx1, fy1 = fb
        # 承太郎领口的金链子换成心形徽章：下巴下面那一段的金色先抹成校服色
        box = (fx0, fy1 + 1, fx1 + 4, fy1 + 12)
        f = recolor(f, {(255, 216, 60): (54, 52, 118), (200, 154, 32): (30, 28, 70)}, box)
        f = heart_badge(f, fx1 - 2, fy1 + 3)
    return f


def build_josuke():
    im, m = base('jotaro')
    sh = Sheet('josuke', '东方仗助', m['cell'], m['pivot'])
    for anim, fps, kind in [('idle', 2, 'loop'), ('walk', 8, 'loop'), ('run', 10, 'loop'), ('point', 4, 'loop'), ('pose', 3, 'oneshot'),
                            ('shock', 1, 'static'), ('hurt', 1, 'static'), ('dodge', 1, 'static'), ('guard', 1, 'static'),
                            ('kick', 8, 'oneshot'), ('sit', 1.5, 'loop')]:
        sh.add(anim, [josuke_body(f) for f in frames('jotaro', anim)], fps, kind)
    # 躺倒：转成站姿处理头发再转回去
    down = []
    for f in frames('jotaro', 'down'):
        f = recolor(f, JOSUKE_COAT)
        f = recolor(f, {(44, 196, 168): JEYE})
        r = f.rotate(-90, expand=True)
        r = josuke_head(r, top_rows=30)
        down.append(r.rotate(90, expand=True).crop((0, 0, f.width, f.height)))
    sh.add('down', down, 1, 'static')
    sh.heads = HD.josuke()
    return save(sh, amap=dict(AMAP_HUMAN, kick='kick', sit='sit', run='run'), bodyW=4)


# ============================================================ 空条承太郎（第四部白衣版）
WHITE = {(84, 98, 168): (255, 255, 250), (43, 49, 96): (236, 232, 222), (48, 48, 78): (206, 200, 190),
         (24, 26, 56): (168, 162, 156), (28, 28, 52): (140, 134, 132),
         (74, 63, 102): (40, 64, 70), (51, 42, 74): (26, 42, 48)}      # 里面的衬衫：深青
HAIR_BLACK = {(24, 26, 56): (30, 26, 34), (28, 28, 52): (22, 18, 26)}


def jotaro4_body(f):
    fb = face_box(f)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        # 帽子后面露出来的头发保持黑色：脸后方、下巴以上的暗藏青先换成黑
        f = recolor(f, HAIR_BLACK, (0, 0, fx0, fy1 + 1))
    return recolor(f, WHITE)


def build_jotaro4():
    im, m = base('jotaro')
    sh = Sheet('jotaro4', '空条承太郎', m['cell'], m['pivot'])
    for anim, fps, kind in [('idle', 2, 'loop'), ('walk', 8, 'loop'), ('run', 10, 'loop'), ('point', 4, 'loop'), ('pose', 3, 'oneshot'),
                            ('shock', 1, 'static'), ('hurt', 1, 'static'), ('dodge', 1, 'static'), ('guard', 1, 'static'),
                            ('kick', 8, 'oneshot'), ('down', 1, 'static')]:
        sh.add(anim, [jotaro4_body(f) for f in frames('jotaro', anim)], fps, kind)
    sh.heads = HD.jotaro4()
    return save(sh, amap=dict(AMAP_HUMAN, kick='kick', run='run'), bodyW=4)


# ============================================================ 通用：换色改出来的角色
def head_recolor(f, cmap, skin=None, top_rows=24, below=0):
    """只在头部（脸的包围盒往上、往两边扩出去，到下巴为止）换色：头发换色用"""
    fb = face_box(f, top_rows, skin)
    if not fb:
        return f
    fx0, fy0, fx1, fy1 = fb
    return recolor(f, cmap, (fx0 - 14, 0, fx1 + 8, fy1 + 1 + below))


def build_recolor(cid, name, src, anims, cmap, hair=None, skin=None, heads_from=None, head_edit=None, amap=None,
                  bodyW=None, frame_fn=None, top_rows=24):
    """anims = [(第三部动作名, 新动作名, fps, kind)…]；cmap 全身换色；hair 只在头部换色"""
    im, m = base(src)
    sh = Sheet(cid, name, m['cell'], m['pivot'])

    def fix(f):
        if hair:
            f = head_recolor(f, hair, skin, top_rows)
        f = recolor(f, cmap)
        if frame_fn:
            f = frame_fn(f)
        return f
    for a in anims:
        sa, na, fps, kind = a
        sh.add(na, [fix(f) for f in frames(src, sa)], fps, kind)
    hd = heads(src)
    pf = hd.get(heads_from or 'portrait') or next(iter(hd.values()))

    def fixh(f):
        if hair:
            f = head_recolor(f, hair, skin, 32)
        f = recolor(f, cmap)
        if head_edit:
            f = head_edit(f)
        return f
    nm = [fixh(f) for f in pf]
    if len(nm) == 1:
        nm = nm * 2
    sh.heads = {'normal': nm, 'smile': [HD.smile(f) for f in nm], 'shock': [HD.shock(f, i) for i, f in enumerate(nm)], 'rage': nm}
    e = save(sh, amap=amap if amap is not None else {'talk': 'idle'}, bodyW=bodyW)
    e['headAlias'] = {}
    return e


def build_crazyd():
    cmap = {'#bab2ff': '#ffc8e6', '#8a80ec': '#f08cc4', '#5242ae': '#bc5292', '#33257a': '#7c2a64',
            '#5a56a0': '#9ae6f8', '#2c2852': '#4cacdc', '#17132e': '#225e90',
            '#ff8a78': '#a8eaff', '#ec3040': '#56b8e6', '#98182c': '#2c6ea2',
            '#fff6b4': '#f0fcff', '#ffd83c': '#9ee4f4', '#c08a18': '#3e92c0',
            '#b69ec6': '#f4bcd8'}
    im, m = base('starplat')
    sh = Sheet('crazyd', '疯狂钻石', m['cell'], m['pivot'])
    for anim, a in m['animations'].items():
        if anim.startswith('portrait'):
            continue
        sh.add(anim, [recolor(f, cmap) for f in frames('starplat', anim)], a.get('fps', 6), a.get('kind', 'loop'))
    hd = heads('starplat')
    nm = [recolor(f, cmap) for f in hd['portrait']]
    sh.heads = {'normal': nm}
    e = save(sh, amap={'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'upper', 'rush': 'rush', 'block': 'block', 'hurt': 'hurt',
                       'special': 'rush', 'finger': 'finger'}, kind='stand', bodyW=6)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


BLOND = {(28, 26, 34): (222, 210, 150), (12, 10, 16): (170, 150, 92), (58, 54, 68): (246, 238, 196), (18, 19, 24): (190, 172, 110)}


def build_koichi():
    e = build_recolor('koichi', '广濑康一', 'npc_student_m',
                      [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('bow', 'bow', 1, 'static')],
                      cmap={'#22242e': '#262a40', '#3a3e4e': '#3e4462', '#121318': '#151726'},
                      hair=BLOND, amap={'talk': 'idle', 'shock': 'bow', 'hurt': 'bow', 'run': 'walk'}, bodyW=3)
    return e


def build_thug(cid, name, uni, hair_c):
    cmap = dict(uni)
    cmap.update(hair_c)
    cmap.update({'#9a4ce0': '#3a2a2a'})
    return build_recolor(cid, name, 'kakyoin',
                         [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'),
                          ('down', 'down', 1, 'static'), ('dodge', 'dodge', 1, 'static'), ('guard', 'guard', 1, 'static')],
                         cmap=cmap, amap={'talk': 'idle', 'shock': 'hurt', 'run': 'walk'}, bodyW=4)


BLACK_UNI = {'#2f9e56': '#2c2c3a', '#1a6038': '#1c1c26', '#62c874': '#4c4c62', '#0f4028': '#111118', '#50b848': '#3c3c4e'}
NAVY_UNI = {'#2f9e56': '#2e2c52', '#1a6038': '#1c1a36', '#62c874': '#4a4882', '#0f4028': '#100f20', '#50b848': '#3a386a'}


def build_tomoko():
    cmap = {'#f8e08e': '#5c3a2a', '#fff6cc': '#86583e', '#d2a650': '#3c2418',
            '#c6daf4': '#d4a2c8', '#8ea8d6': '#9e6a9a', '#a6c6ea': '#bc88b4', '#6f93c9': '#7c4c7c', '#e4eefa': '#ecc8e4',
            '#f592be': '#3e4468', '#c95f8f': '#2a2e4c', '#e0506a': '#525a88', '#ffc8de': '#6a729c', '#3c8ad8': '#6a4a8a'}
    return build_recolor('tomoko', '东方朋子', 'holly',
                         [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('wave', 'wave', 4, 'loop'), ('faint', 'faint', 2, 'oneshot')],
                         cmap=cmap, amap={'talk': 'idle', 'shock': 'wave', 'special': 'wave', 'run': 'walk'}, bodyW=4)


def ryohei_head(f):
    # 白胡子 + 两鬓白发（头像 32×32 的固定位置）
    a = np.array(f.convert('RGBA'))
    for x in range(15, 23):
        a[18, x] = (196, 196, 204, 255)
    for x in range(16, 22):
        a[19, x] = (150, 150, 162, 255) if a[19, x][3] else a[19, x]
    a[17, 20] = (216, 148, 108, 255)
    for y, x in ((15, 12), (16, 13), (9, 15), (9, 16)):
        a[y, x] = (216, 148, 108, 255)
    return Image.fromarray(a, 'RGBA')


def build_ryohei():
    grey = {(28, 26, 32): (150, 150, 160), (12, 10, 16): (112, 112, 124), (56, 52, 62): (196, 196, 206)}
    return build_recolor('ryohei', '东方良平', 'npc_police',
                         [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('shock', 'shock', 1, 'static'), ('read', 'read', 2, 'loop')],
                         cmap={}, hair=grey, head_edit=ryohei_head, amap={'talk': 'idle', 'hurt': 'shock', 'run': 'walk'}, bodyW=4)


def build_angelo():
    cmap = {'#c0262e': '#e6e8ee', '#801622': '#a6aab8', '#e8544e': '#ffffff', '#961e28': '#c2c6d2', '#702830': '#8a8e9e',
            '#f4c852': '#6ab0e0', '#b0802c': '#3a78b0'}
    return build_recolor('angelo', '片桐安十郎（送奶工）', 'npc_bellhop',
                         [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'),
                          ('talk', 'talk', 4, 'loop')],
                         cmap=cmap, skin=[(198, 142, 98), (146, 96, 68)], amap={'shock': 'hurt', 'run': {'a': 'walk', 'f': 1.6}}, bodyW=4)


def build_robber():
    cmap = {'#4a7c72': '#4c4a56', '#203e4a': '#26242e', '#172c35': '#18171e', '#355952': '#38364a', '#64a094': '#6e6c80',
            '#162b33': '#141318', '#32544d': '#302e3c'}
    return build_recolor('robber', '劫匪', 'nukesaku',
                         [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'),
                          ('attack', 'attack', 6, 'oneshot'), ('talk', 'talk', 4, 'loop')],
                         cmap=cmap, skin=[(230, 174, 126), (196, 144, 96)], amap={'shock': 'hurt', 'run': 'walk'}, bodyW=4)


def build_clerk():
    cmap = {'#26305c': '#2f8a5a', '#141a3a': '#1c5a3a', '#3e3846': '#44a070', '#f0a030': '#f0c040'}
    return build_recolor('clerk', '店员', 'npc_stewardess',
                         [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop')],
                         cmap=cmap, amap={'talk': 'idle', 'shock': 'idle', 'hurt': 'idle', 'down': 'idle'}, bodyW=3)


def build_copy(cid, name, src, anims, cmap=None, amap=None):
    return build_recolor(cid, name, src, anims, cmap=cmap or {}, amap=amap or {'talk': 'idle'})


# ============================================================ 水中项链：自己画（水做的、咧嘴笑的脸 + 一串珠子一样的身体）
AQ = dict(o=(16, 30, 70), d=(28, 70, 150), m=(60, 140, 214), l=(130, 206, 244), x=(214, 246, 255), w=(255, 255, 255), k=(10, 16, 40))


def aqua_frame(t=0.0, stretch=0.0, splash=False, w=52, h=42):
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    hx, hy = 31 + 6 * stretch, 15 + np.sin(t * 2 * np.pi) * 1.0
    shapes = []
    head = ((xx - hx) / 7.5) ** 2 + ((yy - hy) / 6.4) ** 2 <= 1
    jaw = ((xx - (hx + 1.5)) / 6.4) ** 2 + ((yy - (hy + 3.2)) / 3.6) ** 2 <= 1
    body = head | jaw
    beads = []
    for i in range(5):
        k = (i + 1) / 5.5
        bx = hx - 6 - i * (5.2 + 2.5 * stretch) - (0 if stretch else 2 * np.sin(t * 2 * np.pi + i * 0.9))
        by = hy + 7 + i * (3.4 - 2.2 * stretch) + (0 if stretch else 1.4 * np.sin(t * 2 * np.pi + i * 1.3))
        r = 3.6 - i * 0.55
        bm = (xx - bx) ** 2 + (yy - by) ** 2 <= r * r
        beads.append((bm, bx, by, r))
        body |= bm
    # 珠子之间连一根细水线
    for (b1, x1, y1, _), (b2, x2, y2, _) in zip(beads, beads[1:]):
        for u in np.linspace(0, 1, 12):
            X, Y = int(round(x1 + (x2 - x1) * u)), int(round(y1 + (y2 - y1) * u))
            if 0 <= X < w and 0 <= Y < h:
                body[Y, X] = True
    # 两只小手
    for dx, dy in ((-2, 9), (5, 8)):
        arm = ((xx - (hx + dx)) / 1.6) ** 2 + ((yy - (hy + dy)) / 2.6) ** 2 <= 1
        body |= arm
    if splash:
        body = head | jaw
        rng = np.random.RandomState(3)
        for i in range(14):
            ang = rng.uniform(0, 2 * np.pi)
            d = rng.uniform(9, 18)
            bx, by, r = hx + np.cos(ang) * d, hy + 4 + np.sin(ang) * d * 0.7, rng.uniform(1.0, 2.2)
            body |= (xx - bx) ** 2 + (yy - by) ** 2 <= r * r
    a[body] = (*AQ['m'], 255)
    # 明暗：左上亮、右下暗
    lit = body & (((xx - (hx - 2.5)) / 5.0) ** 2 + ((yy - (hy - 2.5)) / 3.6) ** 2 <= 1)
    a[lit] = (*AQ['l'], 255)
    dark = body & ~head & (yy > hy + 3)
    a[dark] = (*AQ['d'], 255)
    for bm, bx, by, r in beads:
        hl = bm & ((xx - (bx - r * 0.35)) ** 2 + (yy - (by - r * 0.35)) ** 2 <= (r * 0.45) ** 2)
        if not splash:
            a[hl] = (*AQ['l'], 255)
    gl = ((xx - (hx - 3.5)) ** 2 + (yy - (hy - 3.5)) ** 2 <= 1.2)
    a[gl & body] = (*AQ['x'], 255)
    # 脸：眯起来的眼睛 + 咧到耳根的笑
    ex, ey = int(round(hx + 1)), int(round(hy - 1))
    for x0 in (ex - 1, ex + 4):
        a[ey, x0:x0 + 2] = (*AQ['k'], 255)
        a[ey - 1, x0 + 1] = (*AQ['k'], 255)
    my = int(round(hy + 3))
    mx0, mx1 = int(round(hx - 3)), int(round(hx + 6))
    for x in range(mx0, mx1 + 1):
        a[my, x] = (*AQ['w'], 255)
        a[my + 1, x] = (*AQ['k'], 255)
    for x in range(mx0 + 1, mx1, 2):
        a[my, x] = (*AQ['k'], 255)
    a[my - 1, mx0] = (*AQ['k'], 255)
    a[my - 1, mx1] = (*AQ['k'], 255)
    a[my + 2, mx0 + 2:mx1 - 1] = (*AQ['k'], 255)
    img = Image.fromarray(a, 'RGBA')
    return reoutline(img, AQ['o'])


def build_aqua():
    sh = Sheet('aqua', '水中项链', (52, 42), (26, 40))
    sh.add('idle', [aqua_frame(t / 4) for t in range(4)], 6, 'loop')
    sh.add('lunge', [aqua_frame(0, 0.6), aqua_frame(0.25, 1.0)], 10, 'loop')
    sh.add('hurt', [aqua_frame(0, 0, True)], 1, 'static')
    # 头像：脸部特写（从放大的帧里裁）
    big = aqua_frame(0.1).resize((104, 84), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((44, 6, 76, 38)))
    big2 = aqua_frame(0.35).resize((104, 84), Image.NEAREST)
    face2 = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face2.alpha_composite(big2.crop((44, 6, 76, 38)))
    sh.heads = {'normal': [face, face2]}
    e = save(sh, amap={'talk': 'idle', 'walk': 'idle', 'run': 'lunge', 'hurt': 'hurt', 'down': 'hurt', 'shock': 'hurt',
                       'cmd': 'lunge', 'punch': 'lunge', 'special': 'lunge', 'guard': 'idle', 'dodge': 'lunge'}, kind='stand', bodyW=4)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


BUILDERS = {'josuke': build_josuke, 'jotaro4': build_jotaro4, 'crazyd': build_crazyd, 'koichi': build_koichi,
            'thug_a': lambda: build_thug('thug_a', '学长A', BLACK_UNI, {'#b8402e': '#c4782e', '#e8734c': '#eca452', '#78221e': '#7a4216'}),
            'thug_b': lambda: build_thug('thug_b', '学长B', NAVY_UNI, {'#b8402e': '#2c2632', '#e8734c': '#4c4458', '#78221e': '#16121c'}),
            'aqua': build_aqua, 'tomoko': build_tomoko, 'ryohei': build_ryohei, 'angelo': build_angelo, 'robber': build_robber, 'clerk': build_clerk,
            'fan_a': lambda: build_copy('fan_a', '女生', 'npc_student_f_a', [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('cheer', 'cheer', 4, 'loop')]),
            'fan_b': lambda: build_copy('fan_b', '女生', 'npc_student_f_b', [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('cheer', 'cheer', 4, 'loop')]),
            'flirt': lambda: build_copy('flirt', '搭讪的男人', 'npc_townsfolk', [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static')],
                                        {'#9a8a60': '#c8607e', '#6e6345': '#8e3a5a', '#c4b17f': '#ec8ea8', '#685d41': '#7e3450'}, {'talk': 'idle', 'shock': 'hurt', 'run': 'walk'}),
            'kid': lambda: build_copy('kid', '小学生', 'npc_kid', [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('run', 'run', 10, 'loop'), ('hurt', 'hurt', 1, 'static')],
                                      {'#e49436': '#f0d040', '#a46a26': '#b89820', '#ffbd4c': '#fff07a'}, {'talk': 'idle', 'shock': 'hurt'}),
            }



def main(ids):
    path = os.path.join(L.META, 'chars.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        print('角色', cid, meta['chars'][cid]['cell'], '动作', len(meta['chars'][cid]['animations']), '表情', list(meta['chars'][cid]['heads']))
    import p4_cast
    p4_cast.fill(meta)
    L.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
