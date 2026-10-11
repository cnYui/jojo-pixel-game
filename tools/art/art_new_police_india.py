"""npc_police 的“皮肤”india：印度警察（第4章 瓦拉纳西 / 加尔各答，2026-10-11）。

和原来的日本狱警 npc_police（art_npc.police，花京院 _ka 骨架 + 部件网格）用同一副骨架、同一套腿 / 手臂 / 身体部件和走路摆法，
只换调色板和几个新画的部件，所以身高、比例、走路节奏和原狱警一模一样；**原 npc_police 的帧一帧都不动**（只 import 不改）。
  脸   南亚肤色（深一点的棕）、黑短发、一撇浓黑的八字胡；
  帽   深藏青贝雷帽（往脑后一侧耷拉）+ 一枚小铜帽徽；
  衣   卡其色短袖制服（领口敞开、不打领带），铜扣；斜挎一条棕色武装带（萨姆·布朗带）到腰带上，棕色腰带 + 铜扣；卡其长裤、黑皮鞋；
  手   近侧手里一根 lathi（印度警察的细长竹棍，约 26 px 长，黄褐色、两头包铜）。
动作（都叫 india_*，引擎 actor.skin = 'india' 时 atlas.js 先查 india_<逻辑名>）：
  india_idle 2（棍子斜拄在身前）/ india_walk 4（同原狱警 walk 的步子，棍子跟着手摆）/
  india_run 4（追人：身子前倾、步子迈大、把棍子举过头顶，张嘴喊）/ india_shock 1（同原 shock 的姿势，手里还攥着棍子）/
  portrait_india 2（对话头像：贝雷帽、八字胡、卡其领口；剧情里 S.say('npc_police', …, { expr: 'india' }) 用它）。
  india_talk / india_hurt / india_getup 等逻辑名在 amap 里接到 india_idle / india_shock。
"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import art_npc as N
from art_npc import ka2, ext_legs, legs_of, male_walk, rc, P_TORSO, P_TAIL, P_ARM, SHORT, MALE_HEAD, MALE_HEAD_SHOCK
from assets import sprites_crew as sc
from assets import sprites_jojo as SJ

NEW = []
ONESHOT = {'npc_police.india_shock'}
STATIC_STATES = set()
CHAR_INFO = {}           # npc_police 是 art_npc 登记的已有角色，这里不改名字

INDIA_PAL = dict(N.POLICE_PAL, **{
    's': '#b77a50', 'S': '#8a5434', 'D': '#5e3420', 'f': '#7a3e2e',          # 南亚肤色
    'g': '#b49a62', 'G': '#866c40', 'l': '#d4bd86', 'N': '#5c4a2c',          # 卡其制服
    'p': '#22264a', 'P': '#121430',                                           # 藏青贝雷帽
    'j': '#6e4426', 'J': '#46281a',                                           # 棕色武装带 / 腰带
    't': '#d6b06a', 'T': '#9a7238', 'Y': '#c8962a', 'y': '#f0c84a',           # 竹棍 / 铜扣、铜帽徽
    'R': '#5a1a22',
})


def _ed(grid, *ops):
    g = grid.copy()
    for x, y, s in ops:
        for i, ch in enumerate(s):
            if ch != '.':
                g[y, x + i] = ch
    return g


# 八字胡：鼻子下面一行（嘴上面），4 格浓黑
INDIA_HEAD = _ed(MALE_HEAD, (10, 10, 'aaaa'), (9, 11, 'a'))
INDIA_HEAD_SHOCK = _ed(MALE_HEAD_SHOCK, (8, 9, 'aaaa'))
# 追人时张嘴喊：眉头压低、嘴张开
INDIA_HEAD_SHOUT = _ed(INDIA_HEAD, (8, 6, 'kkk'), (12, 6, 'kk'), (10, 11, 'kkk'), (10, 12, 'kRk'))

# 贝雷帽（16×5，ka2 的整格坐标，头在 (8, 6)）：帽顶往后（左）耷拉、前面一枚铜帽徽、下沿一道深色帽圈
BERET_AT = (6, 4)
BERET = sc.G("""
.....pppppppp....
..ppppppppppppp..
.pppppppppppyypp.
pppPPPPPPPPPPPPP.
PPP..............
""")

# 卡其上衣：领口敞开（原来浅蓝衬衫 + 红领带的地方换成卡其领 + 一小块 V 字皮肤），铜扣照旧；
# 武装带从近侧（右）肩斜挎到左腰
INDIA_TORSO = rc(P_TORSO, {'u': 'l', 'r': 's'})
for _i, (_x, _y) in enumerate([(20, 2), (19, 3), (18, 4), (17, 5), (16, 6), (15, 7), (14, 8), (13, 9), (12, 10), (11, 11)]):
    if INDIA_TORSO[_y, _x] != '.':
        INDIA_TORSO[_y, _x] = 'j'
        if INDIA_TORSO[_y, _x - 1] not in '.':
            INDIA_TORSO[_y, _x - 1] = 'J'
INDIA_TAIL = rc(P_TAIL, {'K': 'j', 'y': 'Y'})            # 棕色腰带 + 铜扣

# 近侧手在各手臂网格里的位置（手掌中心，网格内坐标）+ 手臂网格放在哪（同 art_npc.police）
FARM = {'down': (P_ARM['down'], 20, 21, (2, 9.5)), 'fwd': (P_ARM['fwd'], 20, 21, (3, 9.5)),
        'back': (P_ARM['back'], 19, 21, (1, 9.5)), 'fling': (P_ARM['fling'], 19, 14, (10.5, 0.5))}
FIST = sc.G("""
sss
sSs
""")


def _stick(x0, y0, x1, y1):
    """lathi：2 px 宽的黄褐竹棍，左上一侧亮边、两头包铜。返回 (网格, 左上角 x, y)。"""
    xs, ys = sorted((x0, x1)), sorted((y0, y1))
    ox, oy = int(np.floor(xs[0])) - 1, int(np.floor(ys[0])) - 1
    w, h = int(np.ceil(xs[1])) - ox + 3, int(np.ceil(ys[1])) - oy + 3
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).line((x0 - ox, y0 - oy, x1 - ox, y1 - oy), fill=1, width=2)
    a = np.array(m) > 0
    g = np.full((h, w), '.', dtype='<U1')
    g[a] = 'T'
    up = np.zeros_like(a)
    up[1:, :] = a[:-1, :]
    left = np.zeros_like(a)
    left[:, 1:] = a[:, :-1]
    g[a & ~(up & left)] = 't'                                   # 左上一侧亮边
    for ex, ey in ((x0, y0), (x1, y1)):                          # 两头包铜
        ix, iy = int(round(ex - ox)), int(round(ey - oy))
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
            if 0 <= iy + dy < h and 0 <= ix + dx < w and a[iy + dy, ix + dx]:
                g[iy + dy, ix + dx] = 'Y'
    return g, ox, oy


def _hand_xy(farm, dy):
    grid, ax, ay, (cx, cy) = FARM[farm]
    return ax + cx, ay + cy + dy + 1                            # ka2 里 dy 先 +1（脚落在最底行）


def india(legs='stand', farm='down', dy=0, head=INDIA_HEAD, hdx=0, hdy=0, stick='low'):
    """一帧印度警察（32×48 名义画布，compose 带边距）。stick：low = 棍子从拳头里往前下方斜伸（下端离地 1–2 px）；
    up = 举过头顶往后斜；none = 不拿。"""
    L = ext_legs(legs_of(legs))
    grid, ax, ay, _ = FARM[farm]
    hx, hy = _hand_xy(farm, dy)
    extra = []
    if stick != 'none':
        if stick == 'low':
            st = _stick(hx - 1, hy - 4, hx + 8, min(hy + 14, 46))
        else:
            st = _stick(hx + 4, hy + 6, hx - 8, hy - 13)
        # ka2 给 extra 的坐标还会再加 dy + 1，这里先减掉（hx, hy 已经是画布上的绝对坐标）
        extra.append((st[0], st[1], st[2] - dy - 1, 'k'))
        extra.append((FIST, int(round(hx - 1.5)), int(round(hy - 0.5)) - dy - 1))
    return ka2(head=head, torso=INDIA_TORSO, tail=INDIA_TAIL, legs=L, farm=(grid, ax, ay),
               barm=(P_ARM['bdown'], 8, 21), dy=dy, hdx=hdx, hdy=hdy, hats=[(BERET,) + BERET_AT], extra=extra, **SHORT)


def _lean(fr, k):
    """上身前倾（同 art_npc.studm_bow 的做法：SJ.lean 行剪切，头整体平移不变形）。fr 是 compose 的带边距网格。"""
    g = SJ.G(fr.shape[1], fr.shape[0])
    g.stamp(sc.S(fr), 0, 0)
    hip = sc.PAD + 35                                           # 名义坐标第 35 行 = 腰带下沿（腿从这里起）
    SJ.lean(g, k, hip, rigid=sc.PAD + 20)
    return sc.G(g.s())


def india_frames():
    idle = [india(), india(dy=1)]
    walk = male_walk(lambda lg, fa, dy, s: india(lg, fa, dy))
    run = [_lean(india(lg, 'fling', dy, head=INDIA_HEAD_SHOUT, stick='up'), .14)
           for lg, dy in (('strideA', 0), ('passA', -2), ('strideB', 0), ('passB', -2))]
    shock = india('brace', 'fling', head=INDIA_HEAD_SHOCK, hdx=-1, hdy=-1, dy=-1, stick='up')
    return idle, walk, run, [shock]


INDIA_POR_OPS = [(8, 1, 'pppppppppp'), (6, 2, 'pppppppppppppp'), (4, 3, 'ppppppppppppppppp'),
                 (3, 4, 'ppppppppppppppyyppp'), (3, 5, 'PPPPpppppppppppppppp'),
                 (4, 6, 'PPPPPPPPPPPPPPPPPPPP'), (3, 7, 'PP'),
                 (16, 18, 'aaaaa'), (15, 19, 'a'),                                    # 八字胡
                 (10, 22, 'GGGllllslllGG'), (10, 23, 'lgGGlssslGgg'), (17, 24, 's'), (17, 25, 'G'),
                 (13, 26, 'jj'), (14, 27, 'jj'), (15, 28, 'jj'), (16, 29, 'jj'), (17, 30, 'jj'), (18, 31, 'jj')]


def register():
    idle, walk, run, shock = india_frames()
    defs = [('india_idle', idle, 2, 'Indian police (skin india): khaki uniform, navy beret, moustache, lathi held low; 2f bob'),
            ('india_walk', walk, 8, 'Indian police walk (same steps as npc_police.walk), lathi swings with the hand'),
            ('india_run', run, 10, 'Indian police running after someone: leaning forward, lathi raised overhead, shouting'),
            ('india_shock', shock, 1, 'Indian police startled: eyes wide, arm flung up still gripping the lathi')]
    for act, frames, fps, desc in defs:
        sc.define('npc_police.' + act, frames, INDIA_PAL, desc, fps=fps)
        NEW.append('npc_police.' + act)
    por = [N.male_por(INDIA_POR_OPS), N.male_por(INDIA_POR_OPS, True)]
    from engine import sprite
    sprite.define('npc_police.portrait_india', por, pal=INDIA_PAL, anchor='mb',
                  desc='bust: Indian police (navy beret, moustache, khaki collar, cross strap); f1 talking', fps=8)
    NEW.append('npc_police.portrait_india')


if 'npc_police.idle' in __import__('engine.sprite', fromlist=['_REG'])._REG:
    register()
