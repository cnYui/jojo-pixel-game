# 序章雨天河堤那一幕：撑黄伞的小学生（kid_umb）。
#   原来的做法是 kid 站着、伞是另一个道具悬在他头顶 24 格高的地方，伞柄够不着头顶、手也没举起来，看上去伞是飘着的。
#   现在伞画进人物图集里：近侧手向后抬、握住伞柄，伞柄斜着从手伸到头顶，被头和帽子挡住中间一段，
#   伞面罩在头上方（不压住脸）。伞跟着身体起伏走，不会再和人错开。
#   小学生在第 6 章 / 第 11 章还是原来的 kid（不撑伞），这里只给序章这一幕用。
import sys

from px import rows
from rig import Sheet, draw
from cast_pro import kid

# 伞：黄伞（小学生标配）。伞面 19 格宽、8 行，比头（15 格宽）宽一圈，儿童伞的比例
UMB = dict(Y='#ffd23a', y='#e0a820', w='#fff2a0', k='#b8a47a', r='#d86a2a', o='#c88a18')
CANOPY = rows('''
.........r.........
.......YYYYY.......
.....YwwYYYYYy.....
...YwwYYYYYYYYyy...
..YwYYYYYYYYYYYyy..
.YwYYYYYYYYYYYYYyy.
YYYYYYYYYYYYYYYYYyy
oYo.oYYo.k.oYYo.oyo
''')
CW_ = len(CANOPY[0])          # 19，伞面中线在第 9 列
HAND = (-5, 0)                # 手相对近侧肩（骨架坐标：+x 朝前、+y 朝上）：向后伸到书包后面，伞柄露在脑袋后面，看得见手握着
BOTTOM = 22                   # 伞面最下一行离地多高（头顶 20，留 2 格空隙，伞面不压帽子）
CX = -4                       # 伞面中线落在身体中线往后 4 格（伞往后倾、扛在肩上的样子，伞柄从手斜着伸到伞面中央）


def umbrella(cv, B, P, ctx):
    """画在最底下（头、躯干都盖在它前面），近侧手最后画、握在伞柄上"""
    Xf, Yf = ctx['X'], ctx['Y']
    sx, sy = ctx['shN']
    hx, hy = sx + HAND[0], sy + HAND[1]
    by = ctx['by']
    top = BOTTOM + by                                  # 身体起伏时伞跟着升降
    # 伞面
    x0, y0 = Xf(CX) - 9, Yf(top + len(CANOPY) - 1)
    cv.grid(CANOPY, x0, y0, UMB)
    # 伞柄：从伞面下沿中线斜到手下面两格，末端带一个小弯钩（柄露在头后面，手握在中段）
    cv.line(Xf(CX), Yf(top - 1), Xf(hx), Yf(hy - 2), UMB['k'])
    cv.put(Xf(hx) + 1, Yf(hy - 3), UMB['k'])


def build_kid_umb():
    B, P, _ = kid()
    B.back = _chain_back(B.back)
    hold = dict(aN=((-2, -2), HAND), aN_back=True)      # 近侧手臂放到躯干后面，只露出伸到背后的小臂和手
    frames = {}
    for name in ('idle', 'walk', 'hurt'):
        frs, fps, kind = P[name]
        out = []
        for f in frs:
            g = dict(f)
            g.update(hold)
            out.append(g)
        frames[name] = (out, fps, kind)
    return B, frames


def _chain_back(pack):
    def fn(cv, B, P, ctx):
        umbrella(cv, B, P, ctx)
        if pack:
            pack(cv, B, P, ctx)
    return fn


CAST = {'kid_umb': ('小学生（撑伞）', build_kid_umb)}


def build(cid):
    name, fn = CAST[cid]
    B, frames = fn()
    sh = Sheet(cid, name)
    for n in ('idle', 'walk', 'hurt'):
        frs, fps, kind = frames[n]
        sh.add(n, [draw(B, f) for f in frs], fps, kind)
    sh.body = None           # 头像沿用 kid 的，不在这里重出
    return sh


if __name__ == '__main__':
    from view import compact
    out = sys.argv[1]
    sh = build('kid_umb')
    compact(sh, k=8, title='kid_umb ' + sh.name).save(out + '/z_kid_umb.png')
