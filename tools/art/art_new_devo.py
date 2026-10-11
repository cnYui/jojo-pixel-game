"""devo：独立角色注册，人体关节与绘制工具共用。

devo_doll（黑檀木恶魔附身的玩偶）2026-10-11 重画（原来在 art_later_creatures.py，是个戴帽子的小人、一点不吓人）：
  诡异的木头 / 布娃娃——大脑袋（约占身高 6 成）、乱糟糟的黑毛线头发 + 头顶一道十字缝线、黑圈圆瞪的白眼珠 + 红针尖瞳孔、
  咧到耳根的嘴 + 一排尖牙（说话 / 扑脸时木偶式下巴整个掉下来，上下两排獠牙交错）、细胳膊细腿（1 px 木色 + 黑边，
  肘 / 膝是亮一点的木球关节）、暗紫红小罩衫 + 白褶领 + 锯齿下摆、黑色小圆头鞋；
  手里一把打开的直柄剃刀（2 px 厚的银白刀片 + 纯白反光点 + 暗红木柄）。原创像素，不照描任何官方图。
  做法：每个部件单独画在一层上、各自描 1 px 黑边再按前后叠（远侧肢体压暗），最后所有帧按同一个脚点裁成同一块画布，
  所以 9 个动作的 cell / pivot 一致（数值见烘焙报告）。站立身高 21 px（承太郎 47 px），在人的大腿中段。
  动作：idle 2、walk 4、run 4（快速小碎步、身子前倾、剃刀往前端）、slash 2（举刀 / 劈下 + 月牙刀光）、hurt 1、
  down 1（散架：罩衫瘫在地上、头滚到一边叉叉眼、一条胳膊掉了；剃刀不画在里面——掉在地上的剃刀是道具 doll_razor）、
  talk 2（咧嘴笑 / 下巴掉下来大笑）、jump 2（蹲下蓄力 / 腾空扑脸：剃刀举过头顶、下巴张开、眼睛发亮）、
  peek 2（藏身：只从家具底下露出上半个脑袋，脸在阴影里、两只眼睛发亮；帧 1 再往上冒 2 px、露出一排反光的牙）。
"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from art_later_people import register, PEOPLE
from engine import sprite

NEW = register('devo',{'idle':2,'walk':4,'talk':2,'hurt':1,'down':1,'portrait':2,'slash':2})

# ============================================================================ devo_doll
DOLL = 'devo_doll'
DOLL_ZH = '恶魔娃娃'
DOLL_ACTIONS = {'idle': 2, 'walk': 4, 'run': 4, 'slash': 2, 'hurt': 1, 'down': 1, 'talk': 2, 'jump': 2, 'peek': 2}
DOLL_FPS = {'run': 10, 'walk': 6, 'jump': 6, 'slash': 6, 'peek': 2}

K = (20, 18, 30)
WOOD, WOOD_D, WOOD_H = (218, 178, 130), (164, 118, 84), (244, 216, 172)
HAIR, HAIR_H = (40, 28, 38), (92, 60, 66)
EYE, PUP = (252, 250, 238), (214, 24, 36)
GLOW, GLOW_P = (255, 236, 120), (255, 64, 32)
MOUTH, TOOTH = (88, 14, 30), (252, 250, 238)
THREAD = (206, 186, 150)
TUNIC, TUNIC_D, TUNIC_H = (124, 36, 78), (78, 20, 52), (170, 66, 108)
COLLAR, COLLAR_D = (238, 232, 214), (180, 170, 156)
SHOE, SHOE_H = (34, 26, 34), (96, 80, 96)
BLADE, BLADE_H, BLADE_D = (212, 224, 236), (255, 255, 255), (132, 148, 168)
HANDLE, HANDLE_H = (70, 36, 30), (136, 82, 58)
FLASH, FLASH_D = (255, 255, 236), (168, 232, 255)

# 头 14×13（朝右；后脑在左边，头发往后炸）。
# K 描边 H 头发 h 头发亮丝 S 缝线 F 木脸 f 脸暗 E 眼白 P 瞳孔 M 嘴里 T 牙
HEAD = [
    "...K.K..K.K...",
    "..KHKHKKHKHK..",
    ".KHHHHSHSHHHK.",
    "KHHhHHHSHHhHHK",
    "KHHHKKKHKKKHHK",
    "KHHKEEEKEEEKFK",
    "KHHKEPEKEPEKFK",
    "KHfKEEEKEEEKFK",
    "KHMFKKKFKKKFMK",
    "KfMMMMMMMMMMMK",
    "KfMTTTTTTTTTMK",
    ".KfMTMTMTMTMK.",
    "..KKKKKKKKKK..",
]
# 木偶下巴掉下来（说话 / 大笑 / 扑脸）：上排獠牙朝下、下排獠牙朝上交错，下巴往下掉 2 px
HEAD_OPEN = HEAD[:9] + [
    "KfMMMMMMMMMMMK",
    "KfMTMTMTMTMTMK",
    ".KMMMMMMMMMMK.",
    ".KTMTMTMTMTMK.",
    ".KfFFFFFFFFfK.",
    "..KKKKKKKKKK..",
]
assert all(len(r) == 14 for r in HEAD + HEAD_OPEN)
HEAD_W = 14

PAL = {'K': K, 'H': HAIR, 'h': HAIR_H, 'S': THREAD, 'F': WOOD, 'f': WOOD_D,
       'E': EYE, 'P': PUP, 'M': MOUTH, 'T': TOOTH}

# 工作画布：脚点 (PX, GY)，地面最后一行 = GY-1；画完所有帧后统一按并集裁剪
WC, HC, PX, GY = 52, 44, 22, 40


def _layer():
    return Image.new('RGBA', (WC, HC))


def _put(im, x, y, c):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), tuple(c[:3]) + (255,))


def _line(im, x0, y0, x1, y1, c):
    """整数 Bresenham，像素干净（不用 PIL 的粗线）。"""
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        _put(im, x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _outlined(layer):
    """层内不透明像素外面一圈 4 邻接黑边。"""
    a = np.array(layer)
    m = a[..., 3] > 0
    g = np.zeros_like(m)
    g[1:, :] |= m[:-1, :]
    g[:-1, :] |= m[1:, :]
    g[:, 1:] |= m[:, :-1]
    g[:, :-1] |= m[:, 1:]
    a[g & ~m] = K + (255,)
    return Image.fromarray(a, 'RGBA')


def _grid(rows, pal):
    im = Image.new('RGBA', (len(rows[0]), len(rows)))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal:
                im.putpixel((x, y), tuple(pal[ch][:3]) + (255,))
    return im


def _dark(c, k=.72):
    return tuple(int(v * k) for v in c[:3])


def head_img(open_=False, eyes='normal'):
    """eyes: normal / hurt（瞳孔缩成黑针尖、往后看）/ ko（叉叉）/ glow（发亮）/ shadow（脸在阴影里、只有眼睛发亮）。"""
    pal = dict(PAL)
    if eyes in ('glow', 'shadow'):
        pal['E'], pal['P'] = GLOW, GLOW_P
    if eyes == 'shadow':
        for k in ('F', 'f', 'S', 'H', 'h', 'M'):
            pal[k] = _dark(pal[k], .4)
        pal['T'] = (226, 222, 210)
    im = _grid(HEAD_OPEN if open_ else HEAD, pal)
    if eyes == 'hurt':
        for x0 in (4, 8):
            im.putpixel((x0 + 1, 6), EYE + (255,))
            im.putpixel((x0, 6), K + (255,))
    elif eyes == 'ko':
        for x0 in (4, 8):
            for dx in range(3):
                for dy in range(3):
                    hit = (dx, dy) in ((0, 0), (2, 0), (1, 1), (0, 2), (2, 2))
                    im.putpixel((x0 + dx, 5 + dy), (K if hit else WOOD) + (255,))
    return im


def _limb(parts, pts, c, joint=True):
    """细胳膊细腿：1 px 木色 + 自己的黑边；中间那个点画成亮一点的木球关节。"""
    L = _layer()
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        _line(L, x0, y0, x1, y1, c)
    if joint and len(pts) > 2:
        x, y = pts[1]
        _put(L, x, y, WOOD_H if c == WOOD else WOOD)
    parts.append(_outlined(L))


def _shoe(parts, x, y, back=False, dx=1):
    """小圆头鞋：脚底那一行 3 px，鞋头朝前；自己不描边（颜色本来就深），只在上沿补一个亮点。"""
    L = _layer()
    c = _dark(SHOE, .7) if back else SHOE
    for xx in range(x - 1, x + 2):
        _put(L, xx, y, c)
    if not back:
        _put(L, x + dx, y, SHOE_H)
    parts.append(L)


def _tunic(parts, cx, top, lean=0):
    """小罩衫：上窄下宽，锯齿下摆，白褶领；左上亮、右边暗。top = 下巴那一行（被头挡住）。"""
    L = _layer()
    hem = top + 3
    ImageDraw.Draw(L).polygon([(cx - 3 + lean, top), (cx + 2 + lean, top), (cx + 4, hem), (cx - 4, hem)],
                              fill=TUNIC + (255,))
    for x in range(cx - 4, cx + 5):                     # 锯齿下摆
        if (x - cx) % 2 == 0:
            _put(L, x, hem + 1, TUNIC_D if x > cx else TUNIC)
    _line(L, cx - 3 + lean, top + 1, cx - 4, hem, TUNIC_H)
    _line(L, cx + 3 + lean, top + 2, cx + 4, hem, TUNIC_D)
    for i, x in enumerate(range(cx - 3 + lean, cx + 3 + lean)):   # 褶领（下巴下面一行）
        _put(L, x, top + 1, COLLAR if i % 2 == 0 else COLLAR_D)
    parts.append(_outlined(L))


# 剃刀：手 (hx, hy) 握着刀柄与刀片的接口；blade = 刀片朝向（8 方向里的一个），刀柄朝反方向。
#   刀片 2 px 厚：一条亮银主线 + 刀背一侧暗银，主线中间一个纯白反光点；刀柄 2 px 暗红木。
_PERP = {(1, 0): (0, -1), (-1, 0): (0, -1), (0, 1): (1, 0), (0, -1): (-1, 0),
         (1, -1): (0, -1), (-1, -1): (0, -1), (1, 1): (0, -1), (-1, 1): (0, -1)}


def _razor(parts, hx, hy, blade, length=5, glint=True, handle=None):
    L = _layer()
    bx, by = blade
    hdx, hdy = handle if handle else (-bx, -by)
    _put(L, hx + hdx, hy + hdy, HANDLE_H)
    _put(L, hx + 2 * hdx, hy + 2 * hdy, HANDLE)
    px, py = _PERP[blade]
    for k in range(1, length + 1):
        x, y = hx + bx * k, hy + by * k
        _put(L, x + px, y + py, BLADE_D if k > 1 else BLADE)
        _put(L, x, y, BLADE)
    if glint:
        k = (length + 1) // 2
        _put(L, hx + bx * k, hy + by * k, BLADE_H)
        _put(L, hx + bx * (k + 1) + px, hy + by * (k + 1) + py, BLADE)
    parts.append(_outlined(L))


def _compose(parts):
    im = _layer()
    for p in parts:
        im.alpha_composite(p)
    return im


def _head(parts, cx, top, open_=False, eyes='normal', dx=0):
    L = _layer()
    L.alpha_composite(head_img(open_, eyes), (cx - HEAD_W // 2 + dx, top))
    parts.append(L)


def doll_frame(act, i):
    cx, g = PX, GY - 1                 # g = 脚底那一行
    parts = []
    if act == 'peek':
        # 只从家具底下露出上半个脑袋：头在阴影里（压暗），只有眼睛发亮；帧 1 再冒 2 px，露出一排反光的牙
        cut = 9 if i == 0 else 11
        part = head_img(False, 'shadow').crop((0, 0, HEAD_W, cut))
        L = _layer()
        L.alpha_composite(part, (cx - HEAD_W // 2, g + 1 - cut))
        a = np.array(L)
        glow = np.all(a[..., :3] == GLOW, axis=-1) & (a[..., 3] > 0)
        halo = np.zeros_like(glow)                      # 眼圈外沿一圈很淡的黄光（只染头发 / 脸，不染黑圈）
        halo[:, 1:] |= glow[:, :-1]
        halo[:, :-1] |= glow[:, 1:]
        halo[1:, :] |= glow[:-1, :]
        halo2 = np.zeros_like(halo)
        halo2[:, 1:] |= halo[:, :-1]
        halo2[:, :-1] |= halo[:, 1:]
        halo2[1:, :] |= halo[:-1, :]
        ring = halo2 & ~halo & (a[..., 3] > 0) & ~np.all(a[..., :3] == K, axis=-1)
        a[ring, :3] = (a[ring, :3].astype(int) * 2 + np.array(GLOW)) // 3
        return Image.fromarray(a, 'RGBA')
    if act == 'down':
        # 散架：罩衫瘫在地上（两条腿朝右伸着），头滚到左边侧躺、叉叉眼；一条胳膊掉在更右边
        _limb(parts, [(cx + 1, g - 1), (cx + 5, g - 1), (cx + 8, g - 1)], WOOD_D)
        _shoe(parts, cx + 9, g, back=True)
        _limb(parts, [(cx + 1, g - 3), (cx + 4, g - 4), (cx + 7, g - 3)], WOOD)
        _shoe(parts, cx + 8, g - 2)
        L = _layer()
        ImageDraw.Draw(L).polygon([(cx - 4, g - 4), (cx + 1, g - 5), (cx + 2, g - 1), (cx - 5, g - 1)], fill=TUNIC + (255,))
        _line(L, cx - 4, g - 4, cx, g - 5, TUNIC_H)
        for y in range(g - 4, g):
            _put(L, cx + 2 + (y % 2), y, TUNIC_D)
        _put(L, cx - 4, g - 3, COLLAR)
        _put(L, cx - 4, g - 1, COLLAR_D)
        parts.append(_outlined(L))
        _limb(parts, [(cx + 13, g - 1), (cx + 15, g - 2), (cx + 17, g - 1)], WOOD)       # 掉下来的胳膊
        hd = head_img(False, 'ko').transpose(Image.Transpose.ROTATE_90)      # 头顶朝左、脸朝上
        L = _layer()
        L.alpha_composite(hd, (cx - 20, g + 1 - hd.height))
        parts.append(L)
        return _compose(parts)

    bob = i % 2 if act in ('idle', 'walk', 'run', 'talk') else 0
    lean = {'run': 1, 'hurt': -1}.get(act, 0)
    lift = (1 if i == 0 else -6) if act == 'jump' else 0      # jump 帧 0 蹲下（低 1 px），帧 1 腾空 6 px
    top = g - 8 + lift + bob          # 下巴 / 罩衫顶那一行
    hip = top + 3
    head_top = top - 12

    # ---- 腿（远侧先画、压暗）+ 鞋
    if act in ('walk', 'run'):
        st = (-2, 0, 2, 0)[i % 4] if act == 'walk' else (-3, 0, 3, 0)[i % 4]
        lift_b = 2 if act == 'run' and i % 4 == 1 else 0       # 小碎步：轮流把一只脚抬起来
        lift_f = 2 if act == 'run' and i % 4 == 3 else 0
        fb = (cx - 1 - st, g - lift_b)
        ff = (cx + 2 + st, g - lift_f)
        _limb(parts, [(cx - 1, hip), (cx - 1 - st // 2 + (1 if lift_b else 0), hip + 2), (fb[0], fb[1] - 1)], WOOD_D)
        _shoe(parts, fb[0], fb[1], back=True)
        _limb(parts, [(cx + 1, hip), (cx + 1 + st // 2 + (1 if lift_f else 0), hip + 2), (ff[0], ff[1] - 1)], WOOD)
        _shoe(parts, ff[0], ff[1])
    elif act == 'jump' and i == 1:
        # 腾空：两条腿往后收、脚尖朝下
        _limb(parts, [(cx - 1, hip), (cx - 3, hip + 2), (cx - 5, hip + 4)], WOOD_D)
        _shoe(parts, cx - 5, hip + 5, back=True)
        _limb(parts, [(cx + 1, hip), (cx, hip + 3), (cx - 2, hip + 5)], WOOD)
        _shoe(parts, cx - 2, hip + 6)
    elif act == 'jump':
        # 蹲：膝盖往前顶
        _limb(parts, [(cx - 1, hip), (cx + 1, hip + 2), (cx - 1, g - 1)], WOOD_D)
        _shoe(parts, cx - 1, g, back=True)
        _limb(parts, [(cx + 1, hip), (cx + 4, hip + 2), (cx + 2, g - 1)], WOOD)
        _shoe(parts, cx + 2, g)
    else:
        sp = 1 if act in ('slash', 'hurt') else 0
        _limb(parts, [(cx - 2, hip), (cx - 2 - sp, hip + 2), (cx - 2 - sp, g - 1)], WOOD_D)
        _shoe(parts, cx - 2 - sp, g, back=True)
        _limb(parts, [(cx + 1, hip), (cx + 1 + sp, hip + 2), (cx + 1 + sp, g - 1)], WOOD)
        _shoe(parts, cx + 1 + sp, g)

    # ---- 远侧胳膊（压暗）
    sh_b = (cx - 3 + lean, top + 2)
    if act == 'walk':
        sw = (1, 0, -1, 0)[i % 4]
        _limb(parts, [sh_b, (cx - 5 + sw, top + 4), (cx - 5 + 2 * sw, top + 6)], WOOD_D)
    elif act in ('slash', 'jump', 'hurt'):
        _limb(parts, [sh_b, (cx - 6, top + 1), (cx - 7, top - 1)], WOOD_D)
    elif act == 'run':
        _limb(parts, [sh_b, (cx - 5, top + 3), (cx - 7, top + 2 + bob)], WOOD_D)
    else:
        _limb(parts, [sh_b, (cx - 5, top + 4), (cx - 5, top + 6 - bob)], WOOD_D)

    _tunic(parts, cx, top, lean)

    # ---- 头（压在罩衫上面）
    if act == 'hurt':
        _head(parts, cx, head_top - 1, open_=True, eyes='hurt', dx=-2)
    elif act == 'talk':
        _head(parts, cx, head_top, open_=bool(i))
    elif act == 'jump':
        _head(parts, cx, head_top, open_=bool(i), eyes='glow' if i else 'normal', dx=1 if i else 0)
    elif act == 'slash':
        _head(parts, cx, head_top, open_=bool(i), dx=1 if i else 0)
    elif act == 'run':
        _head(parts, cx, head_top, dx=1)
    else:
        _head(parts, cx, head_top)

    # ---- 近侧胳膊 + 剃刀
    sh = (cx + 3 + lean, top + 2)
    if act == 'slash' and i == 0:            # 举刀：手举到脸旁边，刀片竖着朝上
        hand = (cx + 9, top - 2)
        _limb(parts, [sh, (cx + 7, top + 1), hand], WOOD)
        _razor(parts, hand[0], hand[1], (0, -1), length=6, handle=(0, 1))
    elif act == 'slash':                     # 劈下：手伸到前面，刀片水平朝前；前面一道月牙刀光
        hand = (cx + 8, top + 3)
        _limb(parts, [sh, (cx + 6, top + 2), hand], WOOD)
        _razor(parts, hand[0], hand[1], (1, 0), length=6, handle=(-1, 1))
        L = _layer()
        arc = [(cx + 4, top - 11), (cx + 8, top - 10), (cx + 11, top - 8), (cx + 13, top - 5), (cx + 15, top - 1),
               (cx + 15, top + 3), (cx + 14, top + 6)]
        for (x0, y0), (x1, y1) in zip(arc, arc[1:]):
            _line(L, x0, y0, x1, y1, FLASH)
        for (x0, y0), (x1, y1) in zip(arc[1:-1], arc[2:-1]):
            _line(L, x0 - 1, y0 + 1, x1 - 1, y1, FLASH_D)
        parts.insert(0, L)
    elif act == 'jump':                      # 剃刀举过头顶，刀片朝前上
        hand = (cx + 8, head_top + (2 if i else 4))
        _limb(parts, [sh, (cx + 7, top - 1), hand], WOOD)
        _razor(parts, hand[0], hand[1], (1, -1), length=5)
    elif act == 'hurt':                      # 被打：胳膊甩起来，剃刀还攥着
        hand = (cx + 5, top - 3)
        _limb(parts, [sh, (cx + 5, top), hand], WOOD)
        _razor(parts, hand[0], hand[1], (1, -1), length=4, glint=False)
    elif act == 'run':                       # 往前端着刀，刀片朝前
        hand = (cx + 7, top + 3)
        _limb(parts, [sh, (cx + 5, top + 4), hand], WOOD)
        _razor(parts, hand[0], hand[1], (1, 0), length=5, glint=i % 2 == 0, handle=(-1, 1))
    else:                                    # 手垂在身前、刀片朝前下；反光点隔帧换位置
        sw = (-1, 0, 1, 0)[i % 4] if act == 'walk' else 0
        hand = (cx + 5 + sw, top + 4 - bob)
        _limb(parts, [sh, (cx + 5, top + 3), hand], WOOD)
        _razor(parts, hand[0], hand[1], (1, 1) if act != 'talk' else (1, 0), length=3 if act != 'talk' else 4,
               glint=(i % 2 == 0), handle=(-1, 0) if act != 'talk' else (-1, 1))
    return _compose(parts)


def _doll_frames():
    frames = {a: [doll_frame(a, i) for i in range(n)] for a, n in DOLL_ACTIONS.items()}
    # 所有帧统一裁成并集大小 → 每个动作同一块画布、同一个脚点
    x0, y0, x1, y1 = WC, HC, 0, 0
    for fs in frames.values():
        for f in fs:
            bb = f.getbbox()
            x0, y0, x1, y1 = min(x0, bb[0]), min(y0, bb[1]), max(x1, bb[2]), max(y1, bb[3])
    assert y1 <= GY, f'有像素画到地面以下：y1={y1}'
    x0, x1, y1 = min(x0, PX - 1), max(x1, PX + 1), GY
    box = (x0, y0, x1, y1)
    return {a: [f.crop(box) for f in fs] for a, fs in frames.items()}, (PX - x0, GY - y0)


def _register_doll():
    frames, anchor = _doll_frames()
    names = []
    for act, fs in frames.items():
        name = DOLL + '.' + act
        sprite.define(name, fs, anchor=anchor, fps=DOLL_FPS.get(act, 3), desc=DOLL_ZH + '：' + act)
        names.append(name)
    return names


NEW += _register_doll()
ONESHOT = {'hurt','down','slash','attack','grab','reveal','punch','shock','beg','hide','angry','jump'}
STATIC_STATES = {'true_form'}
CHAR_INFO = {'devo': dict(zh=PEOPLE['devo'][0],en='devo',cat='人物',typ='人物'),
             DOLL: dict(zh=DOLL_ZH, en=DOLL, cat='非人形', typ='角色')}
