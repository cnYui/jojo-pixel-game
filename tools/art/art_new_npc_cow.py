"""npc_cow：加尔各答街头的圣牛（第4章，2026-10-11 新画）。

白色瘤牛，侧视、朝右。造型和配色照原工程 s09_india._cow_frame（原片里那只 48×30 的小瘤牛：奶白身子 W / 白高光 w /
浅灰肚皮 1、灰嘴套 2、深灰蹄子 3、黄褐角 t / T、橙黄万寿菊花环 o / y，都是原工程全局调色板的字母），
按第4章的要求放大成成年瘤牛：背高 33 px、肩峰顶 41 px、角尖 47 px（承太郎 idle 高 47 px：背到他胸口、肩峰到肩），
身子从脚点左 28 px 到右 28 px。
  身子 = 原 _cow_frame 的几块椭圆（身躯、肩峰、脖子、垂皮）放大，肚皮下沿压浅灰、背脊一道白高光；
  头 = 长脸 + 灰嘴套 + 鼻孔 + 下垂的耳朵（里面粉色）+ 一只眼（上眼睑一道黑线），额头点一颗红色吉祥痣；
  角 = 两只长角往上往后弯（近侧黄褐 t、远侧暗一点 T），角上涂了红色和蓝色的圈（印度节庆给牛角上色）；
  脖子上挂一圈橙黄相间的万寿菊花环，最下面吊一只小铜铃；
  尾巴细长、末端一撮深灰的毛；腿细长、近侧两条奶白、远侧两条浅灰，蹄子深灰。
动作：idle 2（尾巴甩）、walk 4（对角步：近前腿 + 远后腿一组、另两条一组）、lick 2（抬头伸长脖子、舌头伸出来往上卷——
剧情里舔波鲁纳雷夫一脸；舌头在脚点右 29–37 px、离地 30–44 px）、hurt 1（受惊：头往后一仰、瞪眼张嘴、尾巴翘起）、
down 1（趴下：四条腿折在身子底下、头还抬着、闭眼）。talk 在 amap 里指 idle。
所有帧画在同一块 76×54 画布上、锚点 = 脚点 (36, 54)（前后蹄中间、地面线），烘出来 pivot 就是脚底。
"""
import sys
sys.dont_write_bytecode = True
from assets import sprites_enemies as SE
from engine import sprite

CID = 'npc_cow'
ZH = '圣牛'
W, H = 76, 54
OY = 8                           # 画布顶上多留 8 行（抬头舔的时候角不出画布）；下面的坐标都按 46 高写，画的时候整体下移 OY
GY = 44                          # 蹄底那一行（下面一行是描边；画布上是 GY + OY）
ANCHOR = (36, 54)
ACTIONS = {'idle': 2, 'walk': 4, 'lick': 2, 'hurt': 1, 'down': 1}
FPS = {'idle': 3, 'walk': 6, 'lick': 4, 'hurt': 1, 'down': 1}


class _C(SE._Pix):
    """原工程 _Pix，所有画图坐标往下挪 OY（坐标照 46 高的画布写）。"""

    def __init__(self, w=W, h=H):
        super().__init__(w, h)

    def rect(self, x0, y0, x1, y1, c, only=None):
        return super().rect(x0, y0 + OY, x1, y1 + OY, c, only)

    def ell(self, x0, y0, x1, y1, c, only=None):
        return super().ell(x0, y0 + OY, x1, y1 + OY, c, only)

    def poly(self, pts, c, only=None):
        return super().poly([(x, y + OY) for x, y in pts], c, only)

    def line(self, pts, c, only=None):
        return super().line([(x, y + OY) for x, y in pts], c, only)

    def seg(self, pts, r, c, only=None):
        return super().seg([(x, y + OY) for x, y in pts], r, c, only)

    def dot(self, pts, c):
        return super().dot([(x, y + OY) for x, y in pts], c)


def _leg(P, pts, col, hoof):
    """细长的腿（粗 3 px）+ 蹄子。pts = 髋 → 膝 / 跗 → 蹄（蹄底）。"""
    P.seg(pts[:-1] + [(pts[-1][0], pts[-1][1] - 2)], 1.45, col)
    x, y = pts[-1]
    P.rect(int(x) - 1, int(y) - 2, int(x) + 2, int(y), hoof)


def _legs(f_far_rear, f_far_front, n_near_rear, n_near_front, by=0):
    """四条腿：每条给 (膝 / 跗的偏移 dx, 蹄的 x 偏移, 蹄抬起的高度)。返回 (远侧图层, 近侧图层)。"""
    far, near = _C(), _C()

    def one(P, hip, knee, hoof_x, spec, col, hoof_col, hind):
        kdx, hdx, lift = spec
        hx, hy = hip
        kx, ky = knee
        foot = (hoof_x + hdx, GY - lift)
        mid = (kx + kdx + (1 if lift and not hind else 0) - (1 if lift and hind else 0), ky + by - lift // 2)
        _leg(P, [(hx, hy + by), mid, foot], col, hoof_col)
    one(far, (20, 29), (17, 36), 18, f_far_rear, '1', '3', True)
    one(far, (47, 30), (47, 37), 47, f_far_front, '1', '3', False)
    one(near, (24, 30), (21, 37), 22, n_near_rear, 'W', '2', True)
    one(near, (43, 31), (43, 38), 43, n_near_front, 'W', '2', False)
    for P in (far, near):
        P.shade('W', '1', d=(1, 0))
    return far, near


def _tail(kind):
    t = _C()
    pts = {'hang': [(15, 17), (12, 24), (11, 33)],
           'swish': [(15, 17), (9, 21), (5, 27)],
           'up': [(15, 16), (9, 12), (5, 14)],
           'down': [(15, 30), (9, 37), (4, 41)]}[kind]
    t.seg(pts, 0.75, 'W')
    ex, ey = pts[-1]
    t.ell(ex - 2, ey - 1, ex + 1, ey + 3, '3')
    return t


def _body(by=0, lying=False):
    """身躯 + 肩峰 + 后臀 + 脖子根 + 垂皮（原 _cow_frame 的几块椭圆放大）。"""
    b = _C()
    o = 12 if lying else 0
    b.ell(14, 14 + by + o, 50, 32 + by + o, 'W')            # 身躯
    b.ell(14, 12 + by + o, 28, 28 + by + o, 'W')            # 后臀（略高）
    b.ell(38, 6 + by + o, 49, 18 + by + o, 'W')             # 肩峰
    b.ell(44, 11 + by + o, 55, 27 + by + o, 'W')            # 脖子
    b.ell(46, 22 + by + o, 53, 34 + by + o, 'W')            # 垂皮
    if lying:
        b.rect(0, GY + 1, W - 1, GY + 1, '.')
    # 肚皮下沿压浅灰（原图 y 17–21 的那几行），背脊一道白高光
    b.shade('W', '1', d=(0, 1), n=3)
    b.shade('W', '1', d=(1, 1))
    b.shade('W', 'w', d=(0, -1))
    if not lying:                                            # 肩胛和胯骨的两道浅灰（不然身子是一整块白）
        b.line([(41, 17 + by), (42, 21 + by), (41, 25 + by)], '1')
        b.line([(22, 16 + by), (24, 19 + by)], '1')
    return b


def _head(pose, by=0, i=0):
    """头（朝右）：长脸、灰嘴套、鼻孔、耳朵、眼、吉祥痣、两只涂了色的角、花环 + 小铜铃。
    pose：normal / lick（抬头伸舌）/ hurt（后仰张嘴）/ down（趴着，头低一点、闭眼）。"""
    hd = _C()
    dx, dy = {'normal': (0, by), 'lick': (3, -8), 'hurt': (-3, -3), 'down': (-1, 9)}[pose]
    X = lambda x: x + dx
    Y = lambda y: y + dy
    # 远侧的角（暗一点，先画）
    hd.seg([(X(58), Y(12)), (X(61), Y(7)), (X(62), Y(3))], 1.0, 'T')
    hd.dot([(X(60), Y(7)), (X(61), Y(7))], 'b')                         # 蓝圈
    hd.dot([(X(62), Y(3)), (X(62), Y(2))], 'r')                         # 红角尖
    # 脸
    hd.ell(X(52), Y(11), X(61), Y(25), 'W')
    hd.ell(X(57), Y(20), X(63), Y(26), '2')                              # 嘴套
    hd.shade('W', '1', d=(1, 1))
    hd.shade('2', '3', d=(0, 1))
    # 近侧的角：往上往后弯，红圈 + 蓝角尖
    hd.seg([(X(55), Y(12)), (X(54), Y(6)), (X(51), Y(1))], 1.1, 't')
    hd.dot([(X(54), Y(7)), (X(55), Y(7)), (X(54), Y(8))], 'r')
    hd.dot([(X(51), Y(1)), (X(52), Y(1)), (X(51), Y(2))], 'b')
    # 下垂的耳朵（往后）
    hd.poly([(X(53), Y(13)), (X(47), Y(16)), (X(48), Y(18)), (X(53), Y(16))], 'W')
    hd.dot([(X(49), Y(16)), (X(50), Y(16)), (X(51), Y(15))], 'f')
    hd.dot([(X(61), Y(13))], 'r')                                        # 吉祥痣
    # 眼
    if pose == 'hurt':
        hd.rect(X(57), Y(14), X(59), Y(16), 'w')
        hd.dot([(X(58), Y(15))], 'e')
        hd.dot([(X(57), Y(13)), (X(58), Y(13)), (X(59), Y(13))], 'k')
    elif pose in ('lick', 'down'):
        hd.line([(X(57), Y(16)), (X(59), Y(15))], 'k')                   # 眯着 / 闭着
    else:
        hd.dot([(X(58), Y(15)), (X(58), Y(16))], 'e')
        hd.line([(X(57), Y(14)), (X(59), Y(14))], 'k')
    hd.dot([(X(63), Y(21)), (X(62), Y(22))], 'k')                         # 鼻孔
    if pose == 'hurt':                                                   # 张嘴“哞——”
        hd.rect(X(60), Y(24), X(64), Y(26), 'k')
        hd.dot([(X(61), Y(25)), (X(62), Y(25))], 'R')
    return hd, (dx, dy)


def _tongue(stage, d):
    """舔：0 舌头伸出一截往上翘；1 伸到最长、舌尖往回卷（粉色 m + 浅粉 f 高光）。"""
    dx, dy = d
    t = _C()
    pts = [(63 + dx, 24 + dy), (67 + dx, 22 + dy), (68 + dx, 18 + dy)] if stage == 0 else \
          [(63 + dx, 24 + dy), (68 + dx, 22 + dy), (70 + dx, 16 + dy), (68 + dx, 11 + dy), (66 + dx, 11 + dy)]
    t.seg(pts, 1.2, 'm')
    t.shade('m', 'M', d=(1, 1))
    t.dot([(x, y) for x, y in pts[1:-1]], 'f')
    return t


def _garland(d, by=0):
    """万寿菊花环：从肩峰前沿绕过脖子前面垂到垂皮上，橙黄相间（原 _cow_frame 的 o / y），最下面一只小铜铃。"""
    dx, dy = d
    g = _C()
    pts = [(46, 13), (47, 16), (48, 19), (49, 22), (50, 25), (52, 27), (54, 26), (55, 24), (56, 22)]
    k = 0 if dx == 0 and dy == by else 1                 # 头抬起 / 后仰时花环跟着脖子挪一半
    for j, (x, y) in enumerate(pts):
        x2, y2 = x + (dx // 2) * k, y + by + ((dy - by) // 2) * k
        g.dot([(x2, y2), (x2 + 1, y2)], 'o' if j % 2 == 0 else 'y')
    bx, byy = 52 + (dx // 2) * k, 28 + by + ((dy - by) // 2) * k
    g.rect(bx, byy, bx + 1, byy + 2, 'Y')                # 小铜铃
    g.dot([(bx, byy)], 'y')
    return g


def cow(act, fi=0):
    P = _C()
    if act == 'down':
        far, near = _C(), _C()
        # 四条腿折在身子底下：只露出前面一截前腿（往前折）和后腿的蹄子
        far.seg([(45, 38), (51, 41), (55, 42)], 1.45, '1')
        far.rect(54, 41, 57, 43, '3')
        near.seg([(41, 39), (47, 42), (52, 43)], 1.45, 'W')
        near.rect(51, 42, 54, 44, '2')
        near.seg([(22, 38), (29, 42), (33, 43)], 1.45, 'W')
        near.rect(32, 42, 35, 44, '2')
        near.shade('W', '1', d=(0, 1))
        P.paste(_tail('down'))
        P.paste(far)
        P.paste(_body(lying=True), ring='k')
        P.paste(near, ring='k')
        hd, d = _head('down')
        P.paste(hd, ring='k')
        P.paste(_garland(d, 0))
        P.outline('k')
        return P.grid()
    by = 0
    tail = 'hang'
    if act == 'idle':
        far, near = _legs((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
        tail = ('hang', 'swish')[fi]
        pose = 'normal'
    elif act == 'walk':
        # 对角步：A 组 = 近前腿 + 远后腿，B 组 = 远前腿 + 近后腿；0 A 在前 / 1 B 抬起往前摆 / 2 B 在前 / 3 A 抬起往前摆
        s = 4
        A = [(1, s, 0), (0, 0, 0), (-1, -s, 0), (2, 0, 3)][fi]
        B = [(-1, -s, 0), (2, 0, 3), (1, s, 0), (0, 0, 0)][fi]
        by = (0, -1, 0, -1)[fi]
        far, near = _legs(A, B, B, A, by)
        tail = ('hang', 'swish', 'hang', 'hang')[fi]
        pose = 'normal'
    elif act == 'lick':
        far, near = _legs((0, 0, 0), (-1, 2, 0), (0, 0, 0), (-1, 2, 0))
        pose = 'lick'
        tail = ('swish', 'hang')[fi]
    else:   # hurt
        far, near = _legs((1, -2, 0), (1, -3, 0), (1, -2, 0), (1, -3, 0))
        pose = 'hurt'
        tail = 'up'
        by = -1
    P.paste(_tail(tail))
    P.paste(far)
    P.paste(_body(by), ring='k')
    P.paste(near, ring='k')
    hd, d = _head(pose, by, fi)
    if pose == 'lick':
        # 伸长的脖子：从肩峰前面往上接到抬起来的头
        nk = _C()
        nk.poly([(44, 12 + by), (52, 4), (58, 8), (56, 22), (48, 26)], 'W')
        nk.shade('W', '1', d=(1, 1))
        nk.shade('W', 'w', d=(0, -1))
        P.paste(nk)
    P.paste(hd, ring='k')
    if pose == 'lick':
        P.paste(_tongue(fi, d), ring='k')
    P.paste(_garland(d, by))
    P.outline('k')
    return P.grid()


def register():
    names = []
    for act, n in ACTIONS.items():
        name = CID + '.' + act
        sprite.define(name, [cow(act, i) for i in range(n)], anchor=ANCHOR, fps=FPS[act], desc=ZH + '：' + act)
        names.append(name)
    return names


NEW = register()
ONESHOT = {'hurt', 'down'}
STATIC_STATES = set()
CHAR_INFO = {CID: dict(zh=ZH, en='Sacred cow', cat='NPC', typ='动物')}
ACTION_ZH = {'lick': '舔'}
