# 第五部《黄金之风》人物共用零件：按身高定躯干 / 腿长、动作清单、手里的道具、衣服花纹。
#   比例标准沿用第四部：站着 1 px ≈ 6 cm，180 cm = 30 px；头一样大，身高差放在躯干和腿上。
from px import Cv, rows, shade
from rig import Body, draw, poses, variants, grid_part, chain, X, Y
from castlib import P_

# cm → (躯干高, 腿长)
HEIGHT = {191: (10, 10), 188: (10, 9), 185: (10, 9), 182: (9, 9), 180: (9, 9), 179: (9, 9), 178: (9, 9), 175: (9, 8),
          174: (9, 8), 172: (9, 8), 171: (9, 8), 170: (8, 8), 165: (8, 7), 164: (8, 7), 163: (8, 7)}

HERO = ['idle', 'walk', 'run', 'pose', 'attack', 'hurt', 'guard', 'down']
VIL = ['idle', 'walk', 'pose', 'attack', 'hurt', 'down']


def b5(cm, head, pal, torso, top, pants, shoe, chin=12, tw=None, hax=9, arm_w=3, leg_w=3, shut=(), **kw):
    """chin = 头的字符稿里下巴那一行的序号（头发 / 帽子超出下巴的行数自动换算成头的高度）"""
    TH, LH = HEIGHT[cm]
    TH, LH = kw.pop('TH', TH), kw.pop('LH', LH)
    tor = rows(torso) if isinstance(torso, str) else torso
    tw = tw or len(tor[0])
    assert len(tor) == TH and all(len(r) == tw for r in tor), ('躯干尺寸不对', cm, TH, tw, [len(r) for r in tor], len(tor))
    hd = rows(head)
    pal.setdefault('q', shade(top, -0.3))
    pal.setdefault('j', top)
    heads = variants(hd, pal)
    for ch in shut:                      # 眼睛里除了 e / w 以外的颜色，闭眼时一起抹掉
        heads['h'] = [r.replace(ch, 's') for r in heads['h']]
    return Body(heads, TH=TH, LH=LH, tw=tw, arm_w=arm_w, leg_w=leg_w, pal=pal, torso=tor, top=top, pants=pants,
                shoe=shoe, hax=hax, hy=kw.pop('hy', LH + TH - 1 - (len(hd) - 1 - chin)),
                skin=kw.pop('skin', pal.get('s', '#f6c49a')), **kw)


def std(B, names=None, extra=None):
    """extra = fn(B, P) -> {动作名: (帧, fps, kind)}；attack 默认是出拳"""
    P = poses(B)
    if extra:
        P.update(extra(B, P))
    return B, P, list(names or HERO)


# ------------------------------------------------------------------ 道具（只在姿势带 item=名字 的帧里画）
def prop(item, txt, dx, dy, pal, hand='handF'):
    g = rows(txt)

    def fn(cv, B, P, ctx):
        it = P.get('item')
        if not it or item not in it.split('+'):
            return
        h = ctx.get(hand)
        if h:
            cv.grid(g, X(h[0]) + dx, Y(h[1]) + dy, pal)
    return fn


def line_prop(item, pts_fn, col):
    """从手拉出去的细线（鱼线、拉链）：pts_fn(手x, 手y) -> [(x, y)…]（骨架坐标）"""
    def fn(cv, B, P, ctx):
        it = P.get('item')
        h = ctx.get('handF')
        if not h or not it or item not in it.split('+'):
            return
        pts = pts_fn(h[0], h[1])
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            cv.line(X(x0), Y(y0), X(x1), Y(y1), col)
    return fn


GUN_PAL = dict(G='#c4c8d8', g='#7a8096', k='#3a2418', K='#6a4428', F='#fff8c0', f='#ffc830', o='#f07820')
GUN = '''
gGGGGg
.KKg..
.Kk...
'''
FLASH = '''
..o...
.ofo..
ofFFfo
.ofo..
..o...
'''
KNIFE = '''
...GG
.GGg.
kg...
k....
'''


def gun(extra_flash=True):
    return chain(prop('gun', GUN, 0, -1, GUN_PAL), prop('flash', FLASH, 6, -3, GUN_PAL))


# ------------------------------------------------------------------ 花纹（fn(沿肢体第几格, 横截面第几列, 总长)）
def pinstripe(col):
    return lambda k, i, n: col if i == 1 else None


def bands(col, every=4, wide=2):
    return lambda k, i, n: col if k % every < wide else None


def dots(col, a=2, b=3, mod=7, at=3):
    return lambda k, i, n: col if (k * a + i * b) % mod == at else None


# ------------------------------------------------------------------ 常用姿势片段
def guns_poses(B, P):
    """持枪：attack = 举枪射击，两发"""
    A = B.arm_len
    aim = dict(aF=(A + 2, 0), aN=((-1, -3), (2, -2)), item='gun', lN=(-2, 0), lF=(2, 0))
    return ([dict(aim), dict(aim, item='gun+flash', head='r', lean=-1, aF=(A + 1, 1)), dict(aim, lean=0),
             dict(aim, item='gun+flash', head='r', lean=-1, aF=(A + 1, 1))], 8, 'oneshot')


def stab_poses(B, P, item='knife'):
    A = B.arm_len
    return ([dict(lean=-1, aF=((-2, -3), (0, -2)), aN=((-1, -3), (2, -3)), item=item, lN=(-1, 0)),
             dict(lean=1, bx=1, head='r', aF=(A + 3, 0), aN=((-2, -2), (-4, -1)), item=item, lN=(-2, 0), lF=((2, -4), (3, 0)), drop=1),
             dict(lean=1, aF=(A + 1, -1), aN=((-2, -2), (-3, -2)), item=item, lF=(2, 0))], 10, 'oneshot')
