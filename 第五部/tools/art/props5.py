# 第五部序章、第1章的道具：行李箱、青蛙、出租车、瓢虫、铲子。尺度照比例标准（1 px ≈ 6 cm），底边是落地线。
#   PROPS = {id: 无参函数 → px.Cv}
from px import Cv, OUTLINE, rows


def sprite(txt, pal):
    g = rows(txt)
    cv = Cv(len(g[0]) + 2, len(g) + 2)
    cv.grid(g, 1, 1, pal)
    return cv.outline(OUTLINE)


def suitcase():
    return sprite('''
....kkkk....
...k....k...
.rRRRRRRRRr.
rRrRRRRRRrRr
rRrRRyyRRrRr
rRrRRyyRRrRr
rRrRRRRRRrRr
rRrRRRRRRrRr
.rrrrrrrrrr.
..k......k..
''', dict(R='#d8483c', r='#8c241c', y='#f0c850', k='#2c2430'))


def _frog(txt):
    return sprite(txt, dict(G='#68c84c', g='#3c8c2c', L='#c8f088', w='#ffffff', e='#141020', d='#245c1c', m='#7c2c30'))


def frog():
    return _frog('''
.ww..ww..
.we..we..
.GGGGGGG.
GLGGGGGLG
GGmmmmmGG
gGLLLLLGg
gg.ggg.gg
''')


def frog_hop():
    return _frog('''
.ww..ww..
.we..we..
GGGGGGGG.
GLGGGGGGG
GGmmmmGGg
.gLLLLgg.
g.g...g..
g.....g..
''')


def ladybug():
    return sprite('''
.kk..
kRkRk
RRkRRk
.RkR.
''', dict(k='#181420', R='#e03438'))


def shovel():
    return sprite('''
.BBB..
..B...
..B...
..B...
..B...
..B...
..B...
..B...
..B...
..B...
.SSS..
SSSSS.
sSSSs.
.sss..
''', dict(B='#8c5c2c', S='#c4ccdc', s='#747c90'))


def _taxi(hit=False):
    W, H = 74, 34
    cv = Cv(W, H)
    body, bd, bl = '#f2f0e8', '#b8b8c8', '#ffffff'
    glass, gl = '#5c8cb4', '#a8d4ec'
    # 车顶灯
    cv.rect(30, 1, 40, 4, '#f4c430')
    cv.hline(31, 39, 1, '#fce480')
    cv.hline(33, 37, 3, '#a8781c')
    # 车舱
    for y in range(5, 15):
        x0 = 22 - (y - 5)
        x1 = 50 + int((y - 5) * 0.9)
        cv.hline(x0, x1, y, body)
        cv.put(x0, y, bd)
    cv.hline(22, 50, 5, bl)
    for y in range(7, 14):
        x0 = 23 - (y - 7)
        cv.hline(x0, 34, y, glass)
        cv.hline(37, 49 + int((y - 7) * 0.9), y, glass)
    cv.line(20, 12, 25, 7, gl)
    cv.line(40, 12, 44, 8, gl)
    # 车身
    cv.rect(3, 15, 70, 25, body)
    cv.hline(5, 68, 15, bl)
    cv.rect(2, 18, 71, 24, body)
    cv.hline(3, 70, 21, '#e8b820')
    cv.hline(3, 70, 22, '#1c1a24')
    cv.rect(2, 24, 71, 26, bd)
    cv.vline(35, 15, 24, bd)
    cv.hline(30, 32, 18, '#68687c')
    cv.hline(51, 53, 18, '#68687c')
    # 车灯、保险杠
    cv.rect(68, 17, 71, 19, '#fff0a0')
    cv.rect(2, 17, 4, 20, '#d8342c')
    cv.rect(0, 25, 4, 27, '#8c90a4')
    cv.rect(69, 25, 73, 27, '#8c90a4')
    # 车轮
    for cx in (17, 56):
        cv.ellipse(cx, 27, 7, 6.4, OUTLINE)
        cv.ellipse(cx, 27, 5.4, 5.0, '#2c2834')
        cv.ellipse(cx, 27, 2.6, 2.4, '#b4b8c8')
        cv.put(cx - 1, 26, '#ffffff')
    if hit:
        for x, y in ((58, 17), (59, 18), (58, 19), (60, 20), (46, 9), (47, 10), (46, 11), (48, 12), (12, 19), (13, 20)):
            cv.put(x, y, '#4c4858')
        cv.rect(66, 17, 71, 19, '#6c6878')
    return cv.outline(OUTLINE)


def taxi():
    return _taxi()


def taxi_hit():
    return _taxi(True)


PROPS = {'suitcase': suitcase, 'frog': frog, 'frog_hop': frog_hop, 'ladybug': ladybug, 'shovel': shovel, 'taxi': taxi,
         'taxi_hit': taxi_hit}

if __name__ == '__main__':
    import sys
    from PIL import Image
    ims = [f().img() for f in PROPS.values()]
    W = sum(i.width + 4 for i in ims)
    H = max(i.height for i in ims)
    sheet = Image.new('RGBA', (W, H), '#50546c')
    x = 0
    for i in ims:
        sheet.alpha_composite(i, (x, H - i.height))
        x += i.width + 4
    sheet.resize((W * 8, H * 8), Image.NEAREST).save(sys.argv[1])
