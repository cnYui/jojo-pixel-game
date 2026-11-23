# 序章的替身（重画）：疯狂钻石、白金之星（第四部配色）、水中项链。
#   以前疯狂钻石等人形替身是拿第三部白金之星的图集换色改的，这次全部照官方设定（JoJo Wiki 的 Infobox_Anime 图）单独画。
#   人形替身共用 rig 的骨架和 poses.stand_poses；非人形的（水中项链）整帧手画。
from px import Cv, mix, shade, OUTLINE
from rig import Body, Sheet, draw, variants, grid_part, chain, X, Y, CW, CH, OX, OY
from poses import stand_poses

BASE = {'w': '#ffffff', 'b': '#1a1438', 'M': '#7a2030'}


def P_(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


def H(txt):
    return txt.replace('S', 's')


def stand_fx(col, light=None):
    """人形替身通用的手部小特效：连打残影、指尖、张开的手掌、抹除的弧线、引爆的火花"""
    light = light or mix(col, '#ffffff', 0.55)

    def fn(cv, B, P, ctx):
        hF, hN = ctx.get('handF'), ctx.get('handN')
        it = P.get('item')
        if P.get('blur') is not None and hF and hN:
            offs = [(-4, 4), (1, -5), (3, 3), (-2, -2), (5, -1)] if P['blur'] == 0 else [(-3, -4), (2, 5), (4, -2), (-1, 2), (5, 2)]
            for i, (dx, dy) in enumerate(offs):
                x, y = X(max(hF[0], hN[0]) + dx), Y((hF[1] + hN[1]) / 2 + dy)
                c = light if i % 2 else mix(col, '#ffffff', 0.25)
                cv.rect(x - 1, y - 1, x + 1, y + 1, c)
                cv.hline(x - 5 - (i % 3), x - 2, y, mix(c, '#ffffff', 0.3))
        if not hF:
            return
        x, y = X(hF[0]), Y(hF[1])
        if it == 'finger':
            cv.hline(x + 2, x + 4, y - 1, B.glove or B.hand)
        elif it == 'palm':
            cv.vline(x + 2, y - 2, y + 1, B.glove or B.hand)
            cv.put(x + 3, y - 2, B.glove or B.hand)
            cv.put(x + 3, y, B.glove or B.hand)
        elif it == 'swipe':
            for k in range(6):
                cv.put(x + 3 + k // 2, y - 5 + k, light)
        elif it == 'swipe2':
            for k in range(9):
                cv.put(x + 5 - k // 3, y - 9 + k, light)
                if k % 2:
                    cv.put(x + 6 - k // 3, y - 9 + k, mix(light, col, 0.5))
        elif it == 'click':
            for dx, dy in ((3, -3), (4, -1), (3, 1), (5, -4)):
                cv.put(x + dx, y + dy, '#fff0a0')
    return fn


# ---------------------------------------------------------------- 疯狂钻石：粉色身体、浅蓝铠甲、头顶心形、肩上黑刺、颈后的管子
def crazyd():
    pal = P_(c='#58b4e0', C='#b4ecfa', n='#2a6ea0', p='#f29aa6', s='#f29aa6', d='#c45a72', e='#5a3ad0', k='#2a2a3a',
             m='#8a2a4a', h='#ffd0e0')
    head = H('''
....CC.CC.....
...CccCccC....
...CcccccC....
..ccCCCCCCc...
.ccCCCCCCCCc..
.ncccccccccccn
kncpppppppppc.
kkpbbbppbbbp..
k.ppwepppwep..
kk.ppppppppp..
.k.dppmmmpp...
....dpppppp...
......dpp.....
''')
    torso = '''
nppppppppp
dpppcpcppp
dppppcpppp
dppppppppp
dppdpppdpp
dppppppppp
dppdpppdpp
dppppppppp
ncccchcccc
nccccccccc
.ncccccc..
'''
    pads = None

    def pad(cv, B, P, ctx):
        # 肩甲：浅蓝的圆块 + 一根黑刺
        for key, dark in (('shF', True), ('shN', False)):
            sx, sy = ctx[key]
            x, y = X(sx), Y(sy)
            c = '#3e92c0' if dark else '#58b4e0'
            cv.rect(x - 1, y - 2, x + 1, y, c)
            cv.put(x, y - 2, '#b4ecfa' if not dark else '#58b4e0')
            cv.put(x - (1 if not dark else -1), y - 3, '#2a2a3a')
            cv.put(x - (1 if not dark else -1), y - 4, '#2a2a3a')

    B = Body(variants(head, pal), TH=11, LH=11, tw=10, arm_w=3, leg_w=4, pal=pal, torso=torso, top='#f29aa6', pants='#f29aa6',
             shoe='#3e92c0', skin='#f29aa6', sleeve='#f29aa6', glove='#58b4e0', sleeve_len=5, hax=7, shoulder=1,
             bare=dict(top=4, skin='#58b4e0'), front=chain(pad, stand_fx('#ff8ac0')), kind='stand')
    P = stand_poses(B)
    return B, P, ['idle', 'punch', 'rush', 'block', 'pose', 'hurt', 'finger', 'fist', 'reach', 'upper']


# ---------------------------------------------------------------- 白金之星（第四部配色）：紫色皮肤、黑长发、金色肩甲和护手、浅色腰布
def starplat():
    pal = P_(p='#8a7ad8', s='#8a7ad8', d='#5a4aa8', k='#1c1830', K='#3a3460', e='#f0e060', g='#f0c040', G='#b08a20',
             m='#3a2a70', r='#b04ad0', L='#e8e0f4', l='#b8acd8')
    head = H('''
...kk.kkk.....
..kkkkkkkkk...
.kkKkkKkkkkk..
kkkkkkkkkkkkk.
kkkkkggggggggk
kkkkkpppppppp.
kkkkpbbbppbbb.
.kkkppweppwep.
.kkkdpppppppp.
kkkkddpmmmpp..
kk.k.dppppp...
k......dpp....
''')
    torso = '''
drrrrrrppp
dprrrrpppp
dpppdppppp
dppdpppdpp
dppppppppp
dppdppdppp
dppppppppp
dppdppdppp
GggggGgggg
lLLLLLLLL.
.lLLLLLL..
'''

    def pad(cv, B, P, ctx):
        for key, dark in (('shF', True), ('shN', False)):
            sx, sy = ctx[key]
            x, y = X(sx), Y(sy)
            c = '#b08a20' if dark else '#f0c040'
            cv.rect(x - 1, y - 2, x + 1, y, c)
            cv.put(x, y - 1, '#fff0a0' if not dark else '#f0c040')

    B = Body(variants(head, pal), TH=11, LH=11, tw=10, arm_w=3, leg_w=4, pal=pal, torso=torso, top='#8a7ad8', pants='#8a7ad8',
             shoe='#3a3070', skin='#8a7ad8', sleeve='#8a7ad8', glove='#f0c040', sleeve_len=5, hax=7, shoulder=1,
             bare=dict(top=5, skin='#4a3e90'), coat=dict(len=3, col='#e8e0f4', open=(2, 3)),
             front=chain(pad, stand_fx('#a080ff')), kind='stand')
    P = stand_poses(B)
    P['portrait'] = ([P['pose'][0][0], P['pose'][0][1]], 8, 'loop')
    return B, P, ['idle', 'punch', 'rush', 'block', 'pose', 'hurt', 'finger', 'fist', 'reach', 'upper', 'portrait']


# ---------------------------------------------------------------- 水中项链：水做的小人，浑身是眼睛，咧着一口牙；从水汽里探出来，后半截是水流
AQ = dict(A='#7fd0f4', a='#3a8ed0', D='#1e4e8e', L='#d8f6ff', t='#12665e', w='#ffffff', k='#0e2a4a')
AQ_BODY = '''
..........aaaa........
........aaALLAaa......
.......aALAAAAAAa.....
.......aAwtAAwtAa.....
......aaAAAAAAAAa.....
......aAAkkkkkkAa.....
......aAAwkwkwkAa.aa..
.......aAAAAAAAAaaAAa.
.....aaaAAAtAAAAAAaa..
....aAAAAAAAAAAaa.....
...aAALAAtAAAaa.......
..aAAAAAAAaaa.........
.aAAtAAaaa............
aAAAaaa...............
.aaa..................
'''
AQ_LUNGE = '''
............................aaaa..
....................aaaaaaaAALLAa.
..............aaaaaaAAAAAAAAwtAAAa
.........aaaaaAAAAAAAtAAAAAAAAkkka
....aaaaaAAAAAAAAtAAAAAAAAAAwkwkwa
aaaaAAAAtAAAAAAAAAAAAAAaaaaAAAAAa.
.aaaAAAAAAAaaaaaaaaaaaa....aaaaa..
....aaaaaaa.......................
'''
AQ_HURT = '''
....a.........a.....
.a....aaaaa.....a...
....aaALLAAaa.......
...aAAAAAAAAAa...a..
...aAkAAAkAAAa......
a..aAAkAkAAAAa......
...aAAkkkkkAAa..a...
....aAAAAAAAa.......
.a...aaAAaaa........
........a....a......
'''


def aqua():
    from px import rows as _rows

    def frame(txt, dx=0, dy=0):
        g = _rows(txt)
        cv = Cv(CW, CH)
        cv.grid(g, OX - len(g[0]) // 2 + dx, OY - len(g) + 1 + dy, AQ)
        return cv.outline(OUTLINE)

    sh = Sheet('aqua', '水中项链', kind='stand')
    sh.add('idle', [frame(AQ_BODY, 0, 0), frame(AQ_BODY, 0, -1), frame(AQ_BODY, 1, -2), frame(AQ_BODY, 0, -1)], 6, 'loop')
    sh.add('lunge', [frame(AQ_LUNGE, 4, -3), frame(AQ_LUNGE, 6, -4)], 10, 'loop')
    sh.add('hurt', [frame(AQ_HURT, 0, -2)], 1, 'static')
    return sh


CAST = {'crazyd': ('疯狂钻石', crazyd), 'starplat': ('白金之星', starplat), 'aqua': ('水中项链', aqua)}


def build(cid):
    name, fn = CAST[cid]
    r = fn()
    if isinstance(r, Sheet):
        return r
    B, P, names = r
    sh = Sheet(cid, name, kind='stand')
    sh.add_pose(B, P, names)
    sh.body = B
    return sh


if __name__ == '__main__':
    import sys
    from view import compact
    out = sys.argv[1]
    for cid in (sys.argv[2:] or list(CAST)):
        sh = build(cid)
        compact(sh, k=6, per_row=6, crop=(-22, -44, 34, 4), title=cid + ' ' + sh.name).save('%s/z_%s.png' % (out, cid))
