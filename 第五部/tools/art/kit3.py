# 第三部重画：敌方和路人共用的躯干花样、小道具、变色（泥偶）等零件。
from px import Cv, OUTLINE, rgba, shade, rows
from rig import Body, Sheet, draw, poses, variants, grid_part, chain, X, Y, CW, CH, OX, OY
from castlib import P_, raw_frame

HEIGHT = {195: (10, 11), 190: (10, 10), 185: (10, 9), 180: (9, 9), 175: (9, 8), 170: (8, 8), 165: (8, 7),
          160: (7, 7), 155: (7, 6), 140: (6, 5), 125: (5, 5), 110: (5, 4)}


def torso(TH, tw=8, kind='plain'):
    """躯干字符稿（上到下）：j 主色、q 背侧暗边、t 内衬、k 领带 / 项链、g 扣子、y 腰带、Y 带扣、J 亮面、p 配色块"""
    out = []
    for r in range(TH):                      # r = 0 在最上
        row = ['q'] + ['j'] * (tw - 1)
        c = tw // 2
        if kind in ('suit', 'suit_belt'):
            n = max(0, 4 - r)
            for i in range(c - (n + 1) // 2 + 1, c + n // 2 + 1):
                if 0 < i < tw:
                    row[i] = 't'
            if 1 <= r <= 4:
                row[c] = 'k'
        elif kind in ('open', 'open_belt'):
            row[c - 1] = row[c] = 't'
        elif kind == 'buttons':
            if r % 2 == 1:
                row[c + 1] = 'g'
        elif kind in ('collar', 'collar_belt'):
            if r == 0:
                row[c - 1] = row[c] = row[c + 1] = 't'
            elif r == 1:
                row[c] = 't'
        elif kind == 'stripes':
            if r % 2 == 1:
                row = ['q'] + ['t'] * (tw - 1)
        elif kind == 'apron':
            if r >= 3:
                row = ['q', 'j'] + ['t'] * (tw - 3) + ['j']
            elif r >= 1:
                row[2] = row[tw - 2] = 't'
        elif kind == 'sash':
            if 0 <= c + 2 - r < tw:
                row[max(1, c + 2 - r)] = 'p'
                row[max(1, c + 3 - r) if c + 3 - r < tw else tw - 1] = 'p'
        elif kind == 'sailor':
            if r == 0:
                row = ['q'] + ['t'] * (tw - 1)
                row[c] = 'j'
            elif r == 1:
                row[c - 1] = row[c + 1] = 't'
                row[c] = 'k'
            elif r == 2:
                row[c] = 'k'
        elif kind == 'vest':
            if r < TH - 2:
                row = ['q', 'j', 't', 't'] + ['j'] * (tw - 4)
                row = ['q', 'j'] + ['t'] * 3 + ['j'] * (tw - 5)
                if r % 2 == 1:
                    row[5 if tw > 6 else tw - 2] = 'g'
        if kind.endswith('belt') and r == TH - 3:
            row = ['y'] * tw
            row[c + 1] = 'Y'
        out.append(''.join(row))
    return out


def body(height, head, pal, kind='plain', top=None, pants='#33334a', shoe='#3a2a2a', tw=8, hax=8, TH=None, LH=None, **kw):
    th, lh = HEIGHT[height]
    TH = TH or th
    LH = LH or lh
    top = top or pal.get('j', '#555566')
    pal.setdefault('j', top)
    pal.setdefault('q', shade(pal['j'], -0.3))
    pal.setdefault('J', shade(pal['j'], 0.25))
    pal.setdefault('t', '#ece8e0')
    pal.setdefault('k', '#b03040')
    pal.setdefault('g', '#ffd040')
    pal.setdefault('y', '#4a2e1e')
    pal.setdefault('Y', '#ffd040')
    pal.setdefault('p', '#d8a040')
    tor = kw.pop('torso_rows', None) or torso(TH, tw, kind)
    return Body(variants(head, pal), TH=TH, LH=LH, tw=tw, arm_w=kw.pop('arm_w', 3 if tw >= 8 else 2),
                leg_w=kw.pop('leg_w', 3), pal=pal, torso=tor, top=top, pants=pants, shoe=shoe, hax=hax,
                skin=kw.pop('skin', pal.get('s', '#f6c49a')), **kw)


STD = ['idle', 'walk', 'hurt', 'down', 'talk']


def std(B, names=None, extra=None):
    P = poses(B)
    if extra:
        P.update(extra(B, P))
    return B, P, names or STD


def at_hand(txt, pal_key_pal, dx=0, dy=0, hand='handF'):
    """手里拿的小东西：字符稿左上角放在手的位置 + (dx, dy)"""
    return grid_part(txt, dx, dy, hand)


def clay(B_fn, over=None, ramp=('#3a2014', '#6e442a', '#98683e', '#c49468')):
    """泥偶：同一套造型，调色板和衣服颜色按亮度换成四档泥色；over = 指定某些字符用哪一档"""
    def tone(c):
        r, g, b, _ = rgba(c)
        lum = r * 0.3 + g * 0.59 + b * 0.11
        return ramp[0] if lum < 45 else ramp[1] if lum < 110 else ramp[2] if lum < 185 else ramp[3]

    def make():
        B, P, names = B_fn()
        pal = {k: (tone(v) if v else v) for k, v in B.pal.items()}
        pal.update({'e': ramp[0], 'w': ramp[1], 'b': ramp[0], 'm': ramp[1], 'M': ramp[0], 's': ramp[3], 'S': ramp[3], 'd': ramp[2]})
        for k, i in (over or {}).items():
            pal[k] = ramp[i]
        B.pal = pal
        B.top, B.pants, B.shoe = ramp[1], ramp[2], ramp[0]
        B.skin, B.hand = ramp[3], ramp[3]
        B.sleeve = ramp[3] if B.sleeve in ('#f6c49a',) else ramp[1]
        B.cuff = ramp[2] if B.cuff else None
        for part in (B.coat, B.skirt):
            if part:
                part['col'] = ramp[1]
                if part.get('trim'):
                    part['trim'] = ramp[0]
        old = B.front

        def front(cv, B_, P_in, ctx):
            if old:
                old(cv, B_, P_in, ctx)
            if P_in.get('lie'):
                return
            for x, y in ((-1, 14), (0, 13), (0, 12), (1, 11), (3, 6), (2, 5), (-2, 20), (-2, 19)):
                if cv.solid(X(x), Y(y)):
                    cv.put(X(x), Y(y), ramp[0])
        B.front = front
        return B, P, names
    return make
