# 第4章新画的角色（第四部/docs/第4章_开发脚本.md §4）：乔瑟夫 79 岁、隐者之紫、音石明 / 辣妹、静、SPW 的人和船员、码头渔民，
#   外加亿泰 / 轰炸空间的临时占位（正式图归第2章；合进来以后剧情自动换成 okuyasu / thehand，这里的占位删掉）。
#   做法照 p4_chars.py：拿第三部全尺寸图集换配色 / 加东西，再用第三部 shrink.py 缩成游戏尺寸；辣妹和静自己画。
#   配色以 TV 动画为准（JoJo Wiki 动画配色表，开发脚本 §0）。只写 assets/_meta/chars_ch4.json，不碰 chars.json。
#   用法：python3 第四部/tools/art/p4_chars_ch4.py [cid ...]
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402
import p4_chars as C  # noqa: E402
import p4_heads as HD  # noqa: E402

O = C.O


def hx(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def mask_of(img, cols, box=None):
    return C.comp(img, [hx(c) if isinstance(c, str) else c for c in cols], box)


def paint(img, mask, col):
    a = np.array(img.convert('RGBA'))
    a[mask] = (*hx(col), 255) if isinstance(col, str) else (*col, 255)
    return Image.fromarray(a, 'RGBA')


def vline(img, x, y0, y1, col, edge=O):
    """竖线（拐杖）：中间一列 col，两边描边"""
    a = np.array(img.convert('RGBA'))
    h, w = a.shape[:2]
    for y in range(max(0, y0), min(h, y1 + 1)):
        for dx, c in ((-1, edge), (0, col), (1, edge)):
            xx = x + dx
            if 0 <= xx < w and (dx == 0 or a[y, xx][3] == 0):
                a[y, xx] = (*(hx(c) if isinstance(c, str) else c), 255)
    if 0 <= y1 + 1 < h and 0 <= x < w:
        a[y1 + 1, x] = (*edge, 255)
    return Image.fromarray(a, 'RGBA')


# ============================================================ 乔瑟夫·乔斯达（79 岁）
# 第三部乔瑟夫：帽 B/C/D + 帽带、卡其衬衫 L/M/N、裤子 R/S、靴子、白胡子
J_HAT = {'#a07c44': '#b0861e', '#dcbc78': '#ecc63a', '#f2dca0': '#fbe27a'}     # 黄底（棕点另外点）
J_COAT = {'#b9a66a': '#8a2a36', '#dccb8e': '#b24a54', '#857444': '#5c1824'}    # 栗红风衣
J_PANTS = {'#6e6a3c': '#b08a5c', '#48452a': '#80603c'}                        # 浅棕裤子
SPOT = hx('#7a4a1a')
GLOVE = (244, 244, 238)
GLOVE2 = (196, 196, 206)
CANE = '#5a3418'
PINK = (246, 198, 206)


def joseph_frame(f, cane=True, bundle=False):
    fb = C.face_box(f)
    hat = mask_of(f, list(J_HAT.keys()), (0, 0, f.width, fb[1] + 1) if fb else None)
    f = C.recolor(f, J_HAT, (0, 0, f.width, fb[1] + 1) if fb else None)
    # 帽子上的棕点：亮黄的地方隔一个点一个（格子错开，像毛线帽的花点）
    a = np.array(f)
    ys, xs = np.nonzero(hat)
    for y, x in zip(ys, xs):
        if (x + 2 * y) % 5 == 0 and tuple(a[y, x][:3]) == hx('#ecc63a'):
            a[y, x] = (*SPOT, 255)
    f = Image.fromarray(a, 'RGBA')
    f = C.recolor(f, J_COAT)
    f = C.recolor(f, J_PANTS)
    if fb:
        fx0, fy0, fx1, fy1 = fb
        # 下巴下面露出来的那一小块皮肤 = 浅粉衬衫领口；再往下的皮肤都是手 → 白手套
        a = np.array(f)
        sk = C.comp(f, C.SKIN)
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        collar = sk & (yy > fy1 + 1) & (yy <= fy1 + 4) & (xx >= fx0 - 1) & (xx <= fx1 + 1)
        a[collar] = (*PINK, 255)
        hand = C.comp(Image.fromarray(a, 'RGBA'), C.SKIN) & (yy > fy1 + 4)
        light = hand & (np.array(f)[..., 0] == C.SKIN[0][0])
        a[hand] = (*GLOVE2, 255)
        a[light] = (*GLOVE, 255)
        # 夹鼻小眼镜：眼睛上面一行描一道细框（只点两个点，chibi 尺寸里看得出就行）
        f = Image.fromarray(a, 'RGBA')
        if cane:
            g = C.comp(f, [GLOVE, GLOVE2])
            gy, gx = np.nonzero(g)
            bb = f.getbbox()
            if len(gx):
                # 朝右的图：最前面那只手拄拐杖
                xm = gx.max()
                yh = int(gy[gx >= xm - 1].min())
                f = vline(f, int(xm) + 2, yh - 1, bb[3] - 2, CANE)
        if bundle:
            # 抱着看不见的静：胸口一团浅蓝的襁褓（里面是空的，剧情里会动一动）
            d = ImageDraw.Draw(f)
            cx, cy = fx1 + 2, fy1 + 9
            d.ellipse((cx - 7, cy - 4, cx + 6, cy + 4), fill=(206, 226, 246, 255), outline=O + (255,))
            d.line((cx - 4, cy - 1, cx + 3, cy - 1), fill=(160, 190, 226, 255))
            d.point((cx + 4, cy - 2), fill=(255, 255, 255, 255))
    return f


def joseph_head(f):
    f = C.recolor(f, J_HAT, (0, 0, 32, 14))
    a = np.array(f)
    for y in range(0, 14):
        for x in range(32):
            if (x + 2 * y) % 5 == 0 and tuple(a[y, x][:3]) == hx('#ecc63a') and a[y, x][3]:
                a[y, x] = (*SPOT, 255)
    f = Image.fromarray(a, 'RGBA')
    f = C.recolor(f, J_COAT)
    return f


def build_joseph_old():
    im, m = C.base('joseph')
    sh = C.Sheet('joseph_old', '乔瑟夫·乔斯达', m['cell'], m['pivot'])
    fr = lambda a: C.frames('joseph', a)
    sh.add('idle', [joseph_frame(f) for f in fr('idle')], 2, 'loop')
    # 走路：79 岁，拄着拐杖慢慢走（走路帧 + 拐杖）
    sh.add('walk', [joseph_frame(f) for f in fr('walk')], 5, 'loop')
    sh.add('point', [joseph_frame(f, cane=False) for f in fr('point')], 1, 'static')
    sh.add('camera', [joseph_frame(f, cane=False) for f in fr('camera')], 4, 'oneshot')
    sh.add('shock', [joseph_frame(f, cane=False) for f in fr('shock')], 4, 'loop')
    sh.add('hurt', [joseph_frame(f, cane=False) for f in fr('hurt')], 1, 'static')
    sh.add('hold', [joseph_frame(f, cane=False, bundle=True) for f in fr('idle')], 2, 'loop')
    sh.add('lie', [joseph_frame(f, cane=False) for f in fr('lie')], 1, 'static')
    hd = C.heads('joseph')
    nm = [joseph_head(f) for f in hd['portrait']]
    sk = [joseph_head(f) for f in hd['portrait_shock']]
    sh.heads = {'normal': nm, 'smile': [HD.smile(f) for f in nm], 'shock': sk, 'rage': sk}
    e = C.save(sh, amap={'talk': 'idle', 'run': 'walk', 'cmd': 'point', 'special': 'camera', 'guard': 'idle', 'dodge': 'hurt',
                          'down': 'lie', 'win': 'idle'}, bodyW=4)
    e['headAlias'] = {}
    return e


# ============================================================ 隐者之紫：第三部的藤图集原样拷过来（藤蔓本身是特效画的）
def build_hermit():
    s = open(os.path.join(L.REPO, 'data', 'data_meta.js'), encoding='utf-8').read()
    gd = json.loads(s[s.index('{'):s.rindex('}') + 1])
    e = dict(gd['chars']['hermit'])
    src = os.path.join(L.REPO, 'assets', 'chars', 'hermit.png')
    dst = os.path.join(L.ASSETS, 'chars', 'hermit.png')
    L.ensure(dst)
    shutil.copyfile(src, dst)
    e['image'] = 'chars/hermit'
    e['heads'] = {}
    return e


# ============================================================ 音石明：花京院的身子 → 淡紫长卷发、藏青外套（金饰）、橙色裤子
OTO_HAIR = {'#b8402e': '#a690c8', '#e8734c': '#d4c2ee', '#78221e': '#6a5490'}
OTO_COAT = {'#2f9e56': '#2e3c70', '#62c874': '#4c5ea0', '#1a6038': '#1c2448', '#0f4028': '#10142c', '#50b848': '#3e4e88'}
OTO_EYE = {'#9a4ce0': '#d02a3a'}
ORANGE = ('#e8842c', '#b05816')


def oto_frame(f, long_hair=True):
    fb = C.face_box(f)
    bb = f.getbbox()
    f = C.recolor(f, OTO_EYE)
    # 腿：外套下摆以下的深绿 → 橙色裤子（脚上的鞋不动）
    if bb:
        legs = (0, bb[3] - 11, f.width, bb[3] - 2)
        f = C.recolor(f, {'#1a6038': ORANGE[1], '#0f4028': ORANGE[1], '#2f9e56': ORANGE[0], '#62c874': ORANGE[0]}, legs)
    f = C.recolor(f, OTO_COAT)
    f = C.recolor(f, OTO_HAIR)
    if fb and long_hair:
        fx0, fy0, fx1, fy1 = fb
        a = np.array(f)
        h, w = a.shape[:2]
        hair = C.comp(f, [hx(c) for c in OTO_HAIR.values()])
        # 后脑的头发往下垂到肩膀下面：脸后方 6 px 宽、从额头一直到下巴下 7 px，波浪的下沿
        for x in range(fx0 - 7, fx0 + 1):
            for y in range(fy0, fy1 + 8 - (1 if (x % 2) else 0)):
                if 0 <= x < w and 0 <= y < h:
                    a[y, x] = (*hx('#a690c8' if (x + y) % 3 else '#6a5490'), 255)
        a = np.array(C.reoutline(Image.fromarray(a, 'RGBA')))
        # 左脸的闪电纹（朝右的图里是靠后的那半边脸）：一道暗紫色折线 2 px
        ex = fx0 + 2
        for dx, dy in ((0, 2), (1, 3), (0, 4)):
            if 0 <= fy0 + dy < h:
                a[fy0 + dy, ex + dx] = (*hx('#6a3a8a'), 255)
        f = Image.fromarray(a, 'RGBA')
        del hair
    return f


def oto_head(f):
    f = C.recolor(f, OTO_EYE)
    f = C.recolor(f, OTO_COAT)
    f = C.recolor(f, OTO_HAIR)
    a = np.array(f)
    # 头像两边的头发往下补长
    for x in list(range(4, 9)) + list(range(23, 28)):
        for y in range(16, 28):
            if a[y, x][3] == 0 or tuple(a[y, x][:3]) in (hx('#2e3c70'), hx('#4c5ea0')):
                a[y, x] = (*hx('#a690c8' if (x + y) % 3 else '#6a5490'), 255)
    return C.reoutline(Image.fromarray(a, 'RGBA'))


def build_otoishi():
    im, m = C.base('kakyoin')
    sh = C.Sheet('otoishi', '音石明', m['cell'], m['pivot'])
    fr = lambda a: C.frames('kakyoin', a)
    sh.add('idle', [oto_frame(f) for f in fr('idle')], 2, 'loop')
    sh.add('walk', [oto_frame(f) for f in fr('walk')], 8, 'loop')
    sh.add('run', [oto_frame(f) for f in fr('walk')], 12, 'loop')
    sh.add('guitar', [oto_frame(f) for f in fr('cast')], 6, 'oneshot')
    sh.add('hurt', [oto_frame(f) for f in fr('hurt')], 1, 'static')
    sh.add('down', [oto_frame(f, long_hair=False) for f in fr('down')], 1, 'static')
    sh.add('guard', [oto_frame(f) for f in fr('guard')], 1, 'static')
    sh.add('dodge', [oto_frame(f) for f in fr('dodge')], 1, 'static')
    hd = C.heads('kakyoin')
    nm = [oto_head(f) for f in hd['portrait']]
    hu = [oto_head(f) for f in hd['portrait_hurt']] * 2
    sh.heads = {'normal': nm, 'smile': [HD.smile(f) for f in nm], 'shock': hu, 'rage': [HD.shock(f, i) for i, f in enumerate(nm)]}
    e = C.save(sh, amap={'talk': 'idle', 'shock': 'hurt', 'cmd': 'guitar', 'punch': 'guitar', 'special': 'guitar', 'win': 'idle',
                          'guard': 'guard', 'dodge': 'dodge', 'down': 'down', 'hurt': 'hurt', 'run': 'run'}, bodyW=4)
    e['headAlias'] = {}
    return e


# ============================================================ 船员们：第三部水手 / SPW / 镇民换色
def npc(cid, name, src, cmap, hair=None, extra=None):
    anims = [('idle', 'idle', 2, 'loop'), ('walk', 'walk', 8, 'loop'), ('talk', 'talk', 4, 'loop'), ('hurt', 'hurt', 1, 'static')]
    return C.build_recolor(cid, name, src, anims, cmap=cmap, hair=hair,
                           amap=dict({'shock': 'hurt', 'run': 'walk', 'down': 'hurt'}, **(extra or {})), bodyW=4)


# 水手：藏青制服 #223054 #2c4484 #161e38 #405684 #1f305f，白帽 #eae8dc，头发 #503624 #3c2a1e
CREW_WORK = {'#223054': '#3a4a5a', '#2c4484': '#56687a', '#161e38': '#232c36', '#405684': '#6a7e90', '#1f305f': '#2e3a48'}


def build_crew(cid, name, hair_to, skin=None):
    cmap = dict(CREW_WORK)
    cmap.update({'#503624': hair_to[0], '#3c2a1e': hair_to[1]})
    return npc(cid, name, 'npc_sailor', cmap)


def build_crew_oto():
    # 混在船员里的音石明：船员帽和工作服，帽檐下面露出一点淡紫色的头发（细心的人能看出来）
    cmap = dict(CREW_WORK)
    cmap.update({'#503624': '#a690c8', '#3c2a1e': '#6a5490'})
    return npc('crew_oto', '船员', 'npc_sailor', cmap)


def build_captain():
    cmap = {'#223054': '#e8e6de', '#2c4484': '#ffffff', '#161e38': '#a8a49a', '#405684': '#ffffff', '#1f305f': '#c8c4ba',
            '#503624': '#d8d8e0', '#3c2a1e': '#a8a8b4'}
    return npc('captain', '船长', 'npc_sailor', cmap)


def build_spw():
    return npc('spw_a', 'SPW 工作人员', 'npc_spw', {})


def build_fisher():
    cmap = {'#9a8a60': '#c8a040', '#6e6345': '#8a6a24', '#c4b17f': '#e8c86a', '#685d41': '#7a5c20',
            '#52645e': '#3a5a78', '#3b4843': '#263c54', '#394641': '#24384c'}
    return npc('fisher', '渔民', 'npc_townsfolk', cmap)


# ============================================================ 辣妹：自己画（金黄身子、铜色喙、鲑红眼睛、尾巴、背刺、电光）
RH = dict(o=(40, 22, 10), d=(176, 120, 14), m=(240, 192, 40), l=(255, 232, 120), x=(255, 250, 210),
          b=(200, 116, 50), bd=(130, 68, 24), e=(255, 140, 120), k=(30, 14, 8), sp=(150, 230, 255), sw=(255, 255, 255))
RUST = {RH['d']: (110, 64, 30), RH['m']: (150, 92, 44), RH['l']: (180, 120, 66), RH['x']: (200, 150, 96)}


def rh_frame(kind='idle', t=0, W=56, H=50):
    """朝右。kind: idle / dash / punch1 / punch2 / hurt / hand；t 用来让电光闪"""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    gx = 26                                   # 脚的中心 x
    lean = {'dash': 6, 'punch1': 2, 'punch2': 4, 'hurt': -4}.get(kind, 0)
    bob = (1 if t % 2 else 0) if kind == 'idle' else 0
    m, dk, lt, x = RH['m'], RH['d'], RH['l'], RH['x']
    if kind == 'hand':
        # 只有一只手从下面伸出来（电视、插座、轮胎裂口里）：前臂 + 三根爪子
        d.rectangle((24, 22, 30, 49), fill=m)
        d.rectangle((24, 22, 25, 49), fill=dk)
        d.ellipse((20, 12, 34, 26), fill=m)
        d.ellipse((22, 13, 29, 19), fill=lt)
        for i, cx in enumerate((21, 27, 33)):
            d.polygon([(cx - 2, 14), (cx + 2, 14), (cx + (i - 1), 5)], fill=x)
        for i in range(6):
            px, py = 18 + (i * 7) % 20, 10 + (i * 11 + t * 5) % 36
            d.point((px, py), fill=RH['sp'])
        return C.reoutline(im, RH['o'])
    # 尾巴（身子后面，弯上去）
    tail = [(gx - 4 - lean, 38), (gx - 12 - lean, 40), (gx - 19 - lean, 36 - bob), (gx - 22 - lean, 30 - bob), (gx - 20 - lean, 27 - bob)]
    d.line(tail, fill=dk, width=4)
    d.line(tail[2:], fill=m, width=2)
    # 腿：粗大腿 + 爪
    for dx in (-4, 4):
        d.rectangle((gx + dx - 2 + (lean // 2), 36, gx + dx + 2 + (lean // 2), 46), fill=dk if dx < 0 else m)
        d.rectangle((gx + dx - 3 + (lean // 2), 46, gx + dx + 4 + (lean // 2), 48), fill=RH['b'])
    # 身子：竖着的椭圆，肚子上一格格鳞片，腰上一圈环 + 前面垂下的一片
    bx, by = gx + lean, 28 - bob
    d.ellipse((bx - 8, by - 10, bx + 8, by + 10), fill=m)
    d.ellipse((bx - 8, by - 10, bx - 1, by + 10), fill=dk)
    for i in range(4):
        d.line((bx - 1, by - 5 + i * 3, bx + 5, by - 5 + i * 3), fill=lt)
    d.rectangle((bx - 8, by + 5, bx + 8, by + 7), fill=RH['bd'])
    d.polygon([(bx + 1, by + 7), (bx + 6, by + 7), (bx + 4, by + 13)], fill=RH['b'])
    # 背刺：后背一排小三角
    for i in range(4):
        sx, sy = bx - 8 + i, by - 8 + i * 4
        d.polygon([(sx, sy), (sx - 4, sy + 1), (sx, sy + 3)], fill=x)
    # 头：肿头龙一样的圆顶 + 往前伸的铜色喙
    hx0, hy0 = bx + 3 + (2 if kind == 'dash' else 0), by - 15
    d.ellipse((hx0 - 8, hy0 - 8, hx0 + 7, hy0 + 6), fill=m)
    d.ellipse((hx0 - 6, hy0 - 8, hx0 + 4, hy0 - 3), fill=lt)
    for i in range(4):                       # 圆顶后面一圈小骨突
        d.point((hx0 - 8 + i, hy0 - 6 + i * 2), fill=x)
    d.polygon([(hx0 + 4, hy0 - 1), (hx0 + 14, hy0 + 2), (hx0 + 4, hy0 + 5)], fill=RH['b'])
    d.line((hx0 + 5, hy0 + 2, hx0 + 12, hy0 + 2), fill=RH['bd'])
    d.rectangle((hx0 + 1, hy0 - 2, hx0 + 3, hy0), fill=RH['e'])
    d.point((hx0 + 2, hy0 - 1), fill=RH['k'])
    # 手臂
    if kind in ('punch1', 'punch2'):
        reach = 10 if kind == 'punch1' else 18
        d.line((bx + 3, by - 4, bx + 3 + reach, by - 6), fill=m, width=4)
        d.ellipse((bx + reach, by - 10, bx + reach + 7, by - 3), fill=lt)
    elif kind == 'hurt':
        d.line((bx + 2, by - 4, bx + 8, by - 12), fill=m, width=3)
    else:
        d.line((bx + 2, by - 3, bx + 8, by + 2), fill=m, width=3)
        d.ellipse((bx + 6, by, bx + 10, by + 4), fill=lt)
    d.line((bx - 6, by - 3, bx - 9, by + 3), fill=dk, width=3)
    im = C.reoutline(im, RH['o'])
    # 电光：身子周围几道折线（每帧位置不一样，看起来在闪）
    if kind != 'hurt':
        rng = np.random.RandomState(7 + t * 13 + len(kind))
        d = ImageDraw.Draw(im)
        for i in range(3 if kind == 'idle' else 4):
            sx, sy = int(rng.randint(6, W - 8)), int(rng.randint(6, H - 10))
            pts = [(sx, sy)]
            for k in range(3):
                pts.append((pts[-1][0] + int(rng.randint(-4, 5)), pts[-1][1] + int(rng.randint(2, 5))))
            d.line(pts, fill=RH['sp'] if i % 2 else RH['sw'], width=1)
    return im


def rust(img):
    return C.recolor(img, {k: v for k, v in RUST.items()})


def build_rhcp():
    sh = C.Sheet('rhcp', '辣妹', (56, 50), (26, 48))
    sh.add('idle', [rh_frame('idle', t) for t in range(4)], 8, 'loop')
    sh.add('dash', [rh_frame('dash', t) for t in range(2)], 12, 'loop')
    sh.add('punch', [rh_frame('punch1', 0), rh_frame('punch2', 1), rh_frame('punch1', 2)], 14, 'oneshot')
    sh.add('hurt', [rh_frame('hurt', 0)], 1, 'static')
    sh.add('hand', [rh_frame('hand', t) for t in range(2)], 10, 'loop')
    sh.add('rust', [rust(rh_frame('hurt', 0))], 1, 'static')
    big = rh_frame('idle', 0).resize((112, 100), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((44, 8, 76, 40)))
    big2 = rh_frame('idle', 1).resize((112, 100), Image.NEAREST)
    face2 = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face2.alpha_composite(big2.crop((44, 8, 76, 40)))
    sh.heads = {'normal': [face, face2]}
    e = C.save(sh, amap={'talk': 'idle', 'walk': 'dash', 'run': 'dash', 'hurt': 'hurt', 'down': 'rust', 'shock': 'hurt',
                         'cmd': 'punch', 'punch': 'punch', 'punch2': 'punch', 'punch_heavy': 'punch', 'rush': 'dash',
                         'special': 'dash', 'guard': 'idle', 'dodge': 'dash', 'block': 'idle', 'win': 'idle'}, kind='stand', bodyW=4)
    e['headAlias'] = {'smile': 'normal', 'rage': 'normal', 'shock': 'normal'}
    return e


# ============================================================ 静：婴儿（显形的时候才看得见；平时剧情把 alpha 设成 0）
SZ = dict(o=(60, 40, 40), s=(250, 214, 186), s2=(224, 170, 140), h=(236, 206, 150), cl=(246, 206, 222), cl2=(214, 160, 186),
          e=(40, 30, 40), m=(190, 90, 90), t=(150, 210, 255))


def sz_frame(cry=False, t=0):
    im = Image.new('RGBA', (34, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # 坐着：圆身子（连体衣）+ 大头
    d.ellipse((8, 15, 25, 28), fill=SZ['cl'])
    d.ellipse((8, 20, 15, 28), fill=SZ['cl2'])
    d.ellipse((5, 22, 12, 28), fill=SZ['s'])      # 脚
    d.ellipse((21, 22, 28, 28), fill=SZ['s'])
    arm = -2 if (cry and t % 2) else 0
    d.ellipse((4, 15 + arm, 10, 21 + arm), fill=SZ['s'])
    d.ellipse((23, 15 + arm, 29, 21 + arm), fill=SZ['s'])
    d.ellipse((9, 2, 25, 17), fill=SZ['s'])
    d.ellipse((9, 2, 25, 8), fill=SZ['h'])
    d.point((17, 1), fill=SZ['h'])
    d.ellipse((10, 10, 13, 13), fill=SZ['s2'])
    d.ellipse((21, 10, 24, 13), fill=SZ['s2'])
    if cry:
        d.line((12, 9, 15, 10), fill=SZ['e'])
        d.line((19, 10, 22, 9), fill=SZ['e'])
        d.ellipse((15, 12, 19, 15 + (t % 2)), fill=SZ['m'])
        d.point((12, 12 + t % 2), fill=SZ['t'])
        d.point((22, 12 + (t + 1) % 2), fill=SZ['t'])
    else:
        d.point((13, 10), fill=SZ['e'])
        d.point((21, 10), fill=SZ['e'])
        d.line((16, 13, 18, 13), fill=SZ['m'])
    return C.reoutline(im, SZ['o'])


def build_shizuka():
    sh = C.Sheet('shizuka', '乔斯达·静', (34, 30), (17, 29))
    sh.add('idle', [sz_frame(False, 0), sz_frame(False, 1)], 2, 'loop')
    sh.add('cry', [sz_frame(True, t) for t in range(2)], 6, 'loop')
    big = sz_frame(False).resize((68, 60), Image.NEAREST)
    face = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    face.alpha_composite(big.crop((18, 2, 50, 34)))
    bigc = sz_frame(True, 1).resize((68, 60), Image.NEAREST)
    fc = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    fc.alpha_composite(bigc.crop((18, 2, 50, 34)))
    sh.heads = {'normal': [face, face], 'shock': [fc, fc]}
    e = C.save(sh, amap={'talk': 'idle', 'walk': 'idle', 'run': 'idle', 'shock': 'cry', 'hurt': 'cry', 'down': 'idle'}, bodyW=3)
    e['headAlias'] = {'smile': 'normal', 'rage': 'shock'}
    return e


BUILDERS = {
    'joseph_old': build_joseph_old, 'hermit': build_hermit, 'otoishi': build_otoishi, 'crew_oto': build_crew_oto,
    'rhcp': build_rhcp, 'shizuka': build_shizuka, 'spw_a': build_spw, 'captain': build_captain, 'fisher': build_fisher,
    'crew_a': lambda: build_crew('crew_a', '船员', ('#2a2420', '#1a1410')),
    'crew_b': lambda: build_crew('crew_b', '船员', ('#6a4a2a', '#4a321a')),
    'crew_c': lambda: build_crew('crew_c', '船员', ('#3a3a44', '#26262e')),
}

HEROES = {
    'joseph_old': dict(cid='joseph_old', cn='乔瑟夫·乔斯达', short='乔瑟夫', rn='JOSEPH JOESTAR', stand='hermit',
                       burst=['#4a1a2a', '#7a2a3e', '#c080ff'], panel='#1a0814', accent='#c080ff', nameColor='#8a3a5a',
                       blipHz=360, grunt=None),
}
SPEAKERS = {
    'otoishi': dict(short='音石明', nameColor='#8a6ab8', blipHz=560),
    'rhcp': dict(short='辣妹', nameColor='#d0a020', blipHz=900),
    'shizuka': dict(short='静', nameColor='#d08aa8', blipHz=980),
    'spw_a': dict(short='SPW', nameColor='#8a7a50', blipHz=460),
    'captain': dict(short='船长', nameColor='#6a7a9a', blipHz=380),
    'crew_a': dict(short='船员', nameColor='#5a6a7a', blipHz=420),
    'crew_b': dict(short='船员', nameColor='#5a6a7a', blipHz=470),
    'crew_c': dict(short='船员', nameColor='#5a6a7a', blipHz=440),
    'crew_oto': dict(short='船员', nameColor='#5a6a7a', blipHz=560),
    'fisher': dict(short='渔民', nameColor='#9a7a3a', blipHz=400),
}
STANDS = {
    'hermit': dict(cn='隐者之紫', en='HERMIT PURPLE', owner='joseph_old', aura='#c080ff', card='#c890ff', ghost='#d0a0ff',
                   impact='purple', kind='vine', idle=None, link=None, summonSfx='stand_summon_purple', fist=False),
    'rhcp': dict(cn='辣妹', en='RED HOT CHILI PEPPER', owner='otoishi', aura='#ffd040', card='#ffe070', ghost='#fff0a0',
                 impact='yellow', kind='humanoid', idle={'dx': 0, 'z': 4}, link=None, summonSfx=None, fist=False),
}


def main(ids):
    path = os.path.join(L.META, 'chars_ch4.json')
    meta = L.load_json(path, {}) or {}
    meta.setdefault('chars', {})
    for cid in ids or BUILDERS:
        meta['chars'][cid] = BUILDERS[cid]()
        e = meta['chars'][cid]
        print('角色', cid, e['cell'], '动作', list(e['animations']), '表情', list(e.get('heads', {})))
    meta['heroes'] = HEROES
    meta['speakers'] = SPEAKERS
    meta['stands'] = STANDS
    L.save_json(path, meta)


if __name__ == '__main__':
    main(sys.argv[1:])
