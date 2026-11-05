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
import p4_portraits as PT  # noqa: E402

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
    if sh.cid in PT.HEADS:       # 手画头像（p4_portraits.py）优先于换色出来的头像
        sh.heads = PT.heads(sh.cid)
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
               (28, 28, 52): (34, 30, 66), (48, 48, 78): (58, 54, 98),
               (74, 63, 102): (222, 186, 62), (51, 42, 74): (164, 126, 34)}      # 里面的衬衫：动画里是黄的
SHOE_L, SHOE_D = (138, 90, 52), (90, 54, 30)


def shoes(f, light, dark):
    """鞋：亮棕全换；暗棕只换挨着亮棕（2 格内）的——腰带也是暗棕，别换到"""
    a = np.array(f.convert('RGBA'))
    lm = comp(f, [SHOE_L])
    near = lm.copy()
    for _ in range(2):
        n = near.copy()
        n[1:, :] |= near[:-1, :]
        n[:-1, :] |= near[1:, :]
        n[:, 1:] |= near[:, :-1]
        n[:, :-1] |= near[:, 1:]
        near = n
    dm = comp(f, [SHOE_D]) & near
    a[lm] = (*light, 255)
    a[dm] = (*dark, 255)
    return Image.fromarray(a, 'RGBA')


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
    f = shoes(f, (118, 74, 150), (72, 42, 98))          # 鞋：动画里是紫的
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
        f = shoes(f, (118, 74, 150), (72, 42, 98))
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
         (74, 63, 102): (98, 62, 136), (51, 42, 74): (64, 38, 94)}      # 里面的衬衫：动画第一套是紫的
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


# 疯狂钻石：动画配色——皮肤三文鱼粉（漫画是艳粉）、眼睛深蓝；头盔和护甲浅蓝两边一样
def build_crazyd():
    cmap = {'#bab2ff': '#ffc4c4', '#8a80ec': '#f2909a', '#5242ae': '#c45a72', '#33257a': '#7c2c4a',
            '#5a56a0': '#9ae6f8', '#2c2852': '#4cacdc', '#17132e': '#225e90',
            '#ff8a78': '#a8eaff', '#ec3040': '#56b8e6', '#98182c': '#2c6ea2',
            '#fff6b4': '#f0fcff', '#ffd83c': '#9ee4f4', '#c08a18': '#3e92c0',
            '#b69ec6': '#f6c0c8', '#40f0e0': '#3a5ad0'}
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


# 康一：照 TV 动画第四部的配色——灰白（略带冷色的银灰）头发、绿色立领校服配金扣、棕鞋、蓝眼睛；
#   发型是第四部前段“往后梳、微微带卷”的样子：前额露出来，头顶前沿翘起一道浪，后脑几道弯的发缕。
K_HAIR = {'L': (236, 238, 244), 'B': (198, 200, 212), 'S': (154, 156, 174), 'M': (174, 176, 192)}
GREY = {(28, 26, 34): K_HAIR['B'], (12, 10, 16): K_HAIR['S'], (58, 54, 68): K_HAIR['L'], (18, 19, 24): K_HAIR['M']}
K_UNI = {'#22242e': '#3d5c47', '#3a3e4e': '#5a7f62', '#121318': '#22362a'}
K_EYE = {'#2a1e1a': '#2e4c8c'}
K_SKIN, K_SKIN2 = (246, 196, 154), (216, 148, 108)

# 全尺寸身体帧的头发（相对“发顶描边那一行的上一行、头左缘描边”这个锚点；. 不动，o 描边，D/F 皮肤）
K_BODY_HAIR = [
    '........ooo.....',
    '.....oooLLLoo...',
    '...ooBBLLBBBBo..',
    '..oBBLLBBSBBBBo.',
    '.oBLLBBSBBBBBBBo',
    'oBBBSBBBBSBBBBBo',
    'oSBBSBBBSBBDDDDo',
    'oSBBBBBSDDDDDDDo',
]


def _paint(a, x0, y0, rows):
    pal = {'o': (26, 16, 32), 'D': K_SKIN, 'F': K_SKIN2}
    pal.update(K_HAIR)
    h, w = a.shape[:2]
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            x, y = x0 + i, y0 + j
            if ch == '.' or not (0 <= x < w and 0 <= y < h):
                continue
            a[y, x] = (*pal[ch], 255)


def koichi_hair(f):
    """身体帧：找到头发块，按模板重画成往后梳的微卷发；低头（bow）帧头发是歪的，只换色加两道发缕"""
    a = np.array(f.convert('RGBA'))
    hair = np.zeros(a.shape[:2], bool)
    for c in K_HAIR.values():
        hair |= (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
    ys, xs = np.nonzero(hair)
    if not len(ys):
        return f
    top = ys.min()
    row = xs[ys == top + 3]
    if len(row) and xs[ys == top].min() - row.min() >= 4:     # 正常站姿：发顶在头中间偏右
        x0 = row.min() - 1
        _paint(a, x0, top - 2, K_BODY_HAIR)
    else:
        for (dy, dx) in ((2, 3), (3, 6), (4, 2)):
            y, x = top + dy, xs[ys == top].min() + dx
            if hair[y, x]:
                a[y, x] = (*K_HAIR['S'], 255)
    return Image.fromarray(a, 'RGBA')


def koichi_portrait(f):
    """头像 32×32：前额再露出一点、前沿翘起往后梳，后脑加几道弯发缕"""
    a = np.array(f.convert('RGBA'))
    L_, B_, S_, M_ = (K_HAIR[k] for k in 'LBSM')
    sk = K_SKIN
    o = (26, 16, 32)

    def px(x, y, c):
        a[y, x] = (*c, 255)
    # 发际线往后、前沿往后梳：额头露到第 6 行，头顶前方是一道往后翻的浪（亮面在上、暗面在下）
    for y, xs in ((6, range(15, 22)), (7, range(13, 23)), (8, range(13, 24))):
        for x in xs:
            px(x, y, sk)
    for x in range(14, 22):
        px(x, 5, B_)
    for x, y in ((17, 4), (18, 4), (19, 4), (20, 4), (21, 4), (22, 5), (23, 5)):
        px(x, y, L_)
    for x, y in ((22, 6), (23, 6), (24, 6), (24, 7)):
        px(x, y, B_)
    for x, y in ((14, 5), (15, 5), (24, 8)):
        px(x, y, S_)
    for x, y in ((24, 5), (25, 6), (25, 7), (25, 8)):
        px(x, y, o)
    # 往后梳的弯发缕（暗线，带一点 S 形）
    for pts in (((14, 3), (13, 4), (12, 5), (11, 6), (11, 7), (10, 8)),
                ((19, 2), (18, 3), (16, 3), (15, 4), (14, 5)),
                ((8, 6), (7, 7), (7, 8)),
                ((10, 10), (11, 11), (12, 12))):
        for x, y in pts:
            if a[y, x][3]:
                px(x, y, S_)
    for x, y in ((9, 4), (10, 3), (12, 2), (13, 2), (20, 3), (21, 3)):
        px(x, y, M_)
    # 后脑的卷：描边做两个小弧
    for x, y in ((3, 8), (3, 9), (3, 10)):
        px(x, y, o)
    for x, y in ((4, 8), (4, 9), (4, 10)):
        px(x, y, B_)
    px(4, 9, S_)
    return Image.fromarray(a, 'RGBA')


def build_koichi():
    def fix_head(f):
        return head_recolor(f, K_EYE, None, 24)
    e = build_recolor('koichi', '广濑康一', 'npc_student_m',
                      [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('bow', 'bow', 1, 'static')],
                      cmap=K_UNI, hair=GREY, frame_fn=lambda f: koichi_hair(fix_head(f)),
                      head_edit=lambda f: koichi_portrait(recolor(f, K_EYE, (0, 0, 32, 18))),
                      amap={'talk': 'idle', 'shock': 'bow', 'hurt': 'bow', 'run': 'walk'}, bodyW=3)
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


# 朋子：动画第一套——黑发带紫色高光、齐下巴直发、白发带；红外套、浅蓝 / 深蓝的连衣裙、浅灰丝袜；眼睛棕色
TOMOKO_HAIR = [(48, 38, 58), (96, 74, 128), (28, 20, 36)]       # 中、亮、暗


def tomoko_frame(f, portrait=False):
    a = np.array(f.convert('RGBA'))
    hm = comp(f, TOMOKO_HAIR)
    ys, xs = np.nonzero(hm)
    if len(ys):
        top = ys.min()
        # 白发带：头发顶往下第 2 行（头像第 3 行），沿着头发横过去，下沿一行浅灰做阴影
        by = top + (3 if portrait else 2)
        band = hm[by].copy()
        a[by][band] = (244, 244, 250, 255)
        sh = hm[by + 1] & band
        if portrait:
            a[by + 1][sh] = (200, 202, 214, 255)
    out = Image.fromarray(a, 'RGBA')
    if not portrait:
        # 丝袜：裙摆（白边）以下的腿换成浅灰
        b = np.array(out)
        hem = comp(out, [(255, 255, 255)])
        hy = np.nonzero(hem.any(axis=1))[0]
        if len(hy):
            y0 = hy.max() + 1
            leg = comp(out, SKIN)
            leg[:y0, :] = False
            b[leg & comp(out, [SKIN[0]])] = (206, 208, 218, 255)
            b[leg & comp(out, [SKIN[1]])] = (164, 166, 180, 255)
            out = Image.fromarray(b, 'RGBA')
    return out


def build_tomoko():
    cmap = {'#f8e08e': '#30263a', '#fff6cc': '#604a80', '#d2a650': '#1c1424',
            '#c6daf4': '#d84a4a', '#8ea8d6': '#a02c38', '#a6c6ea': '#c03a42', '#6f93c9': '#7a1e2a', '#e4eefa': '#ec7a6e',
            '#f592be': '#3e6ab8', '#c95f8f': '#26407a', '#e0506a': '#3a3a4a', '#ffc8de': '#7aa6e0', '#3c8ad8': '#6a4030'}
    return build_recolor('tomoko', '东方朋子', 'holly',
                         [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('wave', 'wave', 4, 'loop'), ('faint', 'faint', 2, 'oneshot')],
                         cmap=cmap, frame_fn=tomoko_frame, head_edit=lambda f: tomoko_frame(f, True),
                         amap={'talk': 'idle', 'shock': 'wave', 'special': 'wave', 'run': 'walk'}, bodyW=4)


def ryohei_head(f):
    # 两鬓白发（头像 32×32 的固定位置）；官方没有胡子，不画
    a = np.array(f.convert('RGBA'))
    for y, x in ((15, 12), (16, 13), (9, 15), (9, 16)):
        a[y, x] = (216, 148, 108, 255)
    return Image.fromarray(a, 'RGBA')


def ryohei_frame(f):
    """动画配色：制服扣子银色（帽徽保持金色）、领带蓝色"""
    fb = face_box(f)
    y0 = fb[3] + 1 if fb else 0
    f = recolor(f, {'#ffd83c': '#dfe2ea', '#c89a20': '#a4a8b6'}, (0, y0, f.width, f.height))
    return recolor(f, {'#7a1c28': '#2c4c9c'})


def build_ryohei():
    grey = {(28, 26, 32): (150, 150, 160), (12, 10, 16): (112, 112, 124), (56, 52, 62): (196, 196, 206)}
    return build_recolor('ryohei', '东方良平', 'npc_police',
                         [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('shock', 'shock', 1, 'static'), ('read', 'read', 2, 'loop')],
                         cmap={}, hair=grey, frame_fn=ryohei_frame, head_edit=lambda f: ryohei_frame(ryohei_head(f)),
                         amap={'talk': 'idle', 'hurt': 'shock', 'run': 'walk'}, bodyW=4)


# 安杰罗（扮成送奶工）：动画配色——灰发、白皙皮肤、淡紫衬衫、青绿色背带工装裤和棒球帽、红灰色鞋
A_SKIN = [(198, 142, 98), (146, 96, 68)]
A_HAT = ['#e6e8ee', '#ffffff', '#a6aab8', '#6ab0e0', '#c2c6d2']
A_TEAL = {'#e6e8ee': '#3a9490', '#ffffff': '#6cc4bc', '#a6aab8': '#246a68', '#6ab0e0': '#f0ecd6', '#c2c6d2': '#2e807c'}
A_SHIRT = {'#e6e8ee': '#c8b4e2', '#ffffff': '#e6dcf6', '#a6aab8': '#9a86ba', '#c2c6d2': '#b0a0cc', '#6ab0e0': '#e6dcf6'}
A_PANTS = {'#1c1b26': '#2e7a78', '#242230': '#246260', '#3a78b0': '#1e5654', '#c2c6d2': '#4a9e98'}
A_BODY = {'#1e1a22': '#9a9aa8', '#464254': '#c4c4d0', '#c68e62': '#f2d4bc', '#926044': '#d4a48c'}


ANGELO_FACE = {
    6:  '        ohhhhhhhhhhhho        ',
    7:  '        ohhHhhhhhhhhhhho      ',
    8:  '      oohHhhhhhhosssssso.     ',
    9:  '      oohhhhhhhosssssssso     ',
    10: '      oohhhhhhossssssssso     ',
    11: '      oohhhhhhsoooossooooo    ',
    12: '      oohhhhhhsswossswosso    ',
    13: '      oohhhhoossssssssssso    ',
    14: '      ooooooddssssssssssso.   ',
    15: '        odddossssssssssssoo.  ',
    16: '        odddsssssssssssssso.  ',
    17: '        odddssssssssssssso..  ',
    18: '         oddssssssssommmso..  ',
    19: '          osssssssssssssso..  ',
    20: '          ossssssssssssoo..   ',
    21: '          oosssssoooooo...    ',
}


def angelo_frame(f, portrait=False):
    fb = face_box(f, 24 if not portrait else 32, A_SKIN)
    if not fb:
        return recolor(f, A_BODY)
    fx0, fy0, fx1, fy1 = fb
    a = np.array(f.convert('RGBA'))
    h, w = a.shape[:2]
    # 1) 帽子：脸顶以上的白帽子 → 青绿棒球帽；原来是高高的筒帽，削掉上面三行，前面加帽檐
    hat = comp(f, A_HAT, (0, 0, w, fy0 - 1))
    ys, xs = np.nonzero(hat)
    out = Image.fromarray(a, 'RGBA')
    if len(ys):
        top, bot = ys.min(), ys.max()
        if bot - top >= 3:
            cut = bot - 3
            x0, x1 = xs.min() - 1, xs.max() + 1
            a[:cut + 1, x0:x1 + 1] = (0, 0, 0, 0)
            a[cut, x0 + 1:x1] = (26, 16, 32, 255)
            ex = xs[ys == bot].max()
            for k in range(1, 4):                               # 帽檐往前伸 3 格
                a[bot, ex + k] = (*rgb('#246a68'), 255)
                a[bot + 1, ex + k] = (26, 16, 32, 255)
            a[bot - 1, ex + 1:ex + 4] = (26, 16, 32, 255)
            a[bot, ex + 4] = (26, 16, 32, 255)
        out = recolor(Image.fromarray(a, 'RGBA'), A_TEAL, (0, 0, w, fy0 - 1))
    # 2) 衬衫淡紫；裤子、腰带、裤缝青绿
    out = recolor(out, A_PANTS, (0, fy1 + 1, w, h))
    out = recolor(out, A_SHIRT, (0, fy1 + 1, w, h))
    if not portrait:
        # 背带裤的护胸：腰带往上 5 行、躯干中间一块；两条背带到肩
        b = np.array(out)
        belt = comp(out, ['#1e5654'], (0, fy1 + 1, w, h))
        by = np.nonzero(belt.sum(axis=1) >= 4)[0]
        if len(by):
            y1 = by.min()
            bx = np.nonzero(belt[y1])[0]
            cx0, cx1 = bx.min() + 2, bx.max() - 2
            shirt = comp(out, list(A_SHIRT.values()))
            for y in range(y1 - 5, y1):
                for x in range(cx0, cx1 + 1):
                    if shirt[y, x]:
                        b[y, x] = (*rgb('#3a9490' if x > cx0 else '#2e807c'), 255)
            for y in range(fy1 + 2, y1 - 5):
                for x in (cx0, cx1):
                    if shirt[y, x]:
                        b[y, x] = (*rgb('#2e807c'), 255)
        out = Image.fromarray(b, 'RGBA')
        # 鞋：最底下两行的深色换成红灰
        bb = out.getbbox()
        out = recolor(out, {'#2e7a78': '#8a5454', '#246260': '#6a3c40', '#5c5c70': '#a06a6a'}, (0, bb[3] - 2, w, bb[3]))
    out = recolor(out, A_BODY)
    if portrait:
        # 原图是戴墨镜、留胡子的门童脸，安杰罗没有胡子：头像的脸整块重画（x 从 1 起）
        b = np.array(out)
        pal = {'o': (20, 18, 30), 'h': rgb('#9a9aa8'), 'H': rgb('#c4c4d0'), 's': rgb('#f2d4bc'), 'd': rgb('#d4a48c'),
               'w': rgb('#f0ecd6'), 'm': rgb('#c08a80')}
        for y, r in ANGELO_FACE.items():
            for i, ch in enumerate(r):
                x = 1 + i
                if ch == ' ':
                    continue
                b[y, x] = (0, 0, 0, 0) if ch == '.' else (*pal[ch], 255)
        out = Image.fromarray(b, 'RGBA')
    return out


def build_angelo():
    cmap = {'#c0262e': '#e6e8ee', '#801622': '#a6aab8', '#e8544e': '#ffffff', '#961e28': '#c2c6d2', '#702830': '#8a8e9e',
            '#f4c852': '#6ab0e0', '#b0802c': '#3a78b0'}
    return build_recolor('angelo', '片桐安十郎（送奶工）', 'npc_bellhop',
                         [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('hurt', 'hurt', 1, 'static'), ('down', 'down', 1, 'static'),
                          ('talk', 'talk', 4, 'loop')],
                         cmap=cmap, skin=A_SKIN, frame_fn=angelo_frame, head_edit=lambda f: angelo_frame(f, True),
                         amap={'shock': 'hurt', 'run': {'a': 'walk', 'f': 1.6}}, bodyW=4)


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
