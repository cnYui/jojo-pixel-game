# 第4章的道具（第四部/docs/第4章_开发脚本.md §4）：电瓶摩托、纸箱、白色电吉他、快艇、婴儿手印、粉底盒、黏地、碎混凝土、
#   船员帽、装箭的箱子、电视（念写用）、两张念写照片（海星 / 纸箱里的婴儿轮廓）。
#   画法和格式照 p4_props.py（游戏比例直接画，横向帧条），只写 assets/_meta/props_ch4.json。
#   用法：python3 第四部/tools/art/p4_props_ch4.py
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as P  # noqa: E402
from p4_bglib import C, ellipse, line, px, rect  # noqa: E402

grid, save = P.grid, P.save


# ---------------------------------------------------------------- 电瓶摩托（0 平时 / 1 电瓶亮 / 2 散架）
BIKE = dict(k='#24202a', g='#5a5e6a', G='#8a909e', r='#c83a3a', R='#e86a5a', w='#d8dce4', y='#ffe060', Y='#fff8c0', b='#3a3e48', s='#9aa0ae')


def ebike():
    base = ["..........rrrr...",
            ".........rRRRRr..",
            "....gg..rrrrrrr..",
            "...gGGg.bbbbbb.w.",
            "..kkkk.bbYYbb.ww.",
            ".kk..kkbbbbbbkk..",
            "kk.ss.kkbbbbkk.kk",
            "k.sGGs.k....k.s.k",
            "k.sGGs.k...k.sGs.k",
            ".k.ss.k.....k.s.k",
            "..kkkk.......kkk."]
    ok = grid([r.replace('Y', 'b') for r in base], BIKE)
    lit = grid(base, BIKE)
    broken = grid([".................",
                   "...........rr....",
                   "..kk.....rRRr..w.",
                   ".k..k..bbbbbb.ww.",
                   "k.ss.k.bbbbbbkk.k",
                   "k.sGs.k.bkkb..sGk",
                   ".kkkkk.kk..kk.kkk"], BIKE)
    save('ebike', [ok, lit, broken])


# ---------------------------------------------------------------- 纸箱（0 合着 / 1 打开）
BOX = dict(t='#c89a5a', T='#e0b878', d='#8a6234', D='#6a4a26', l='#b08048')


def box():
    shut = grid(["TTTTTTTTTTTTTT",
                 "TttttttdtttttT",
                 "dddddddDdddddd",
                 "tttttttttttttl",
                 "tttttttttttttl",
                 "ttttTTTTTttttl",
                 "tttttttttttttl",
                 "tttttttttttttl",
                 "dddddddddddddD"], BOX)
    opn = grid(["T............T",
                "TT..........TT",
                ".TT........TT.",
                "dddddddddddddd",
                "tDDDDDDDDDDDDl",
                "tttttttttttttl",
                "ttttTTTTTttttl",
                "tttttttttttttl",
                "dddddddddddddD"], BOX)
    save('box', [shut, opn])


# ---------------------------------------------------------------- 白色电吉他（背在背上 / 拿在手里同一张）
GTR = dict(w='#f4f4f0', W='#ffffff', g='#c8c8d0', k='#2a2a30', n='#8a5a2a', N='#b07a3a', m='#c0c4cc')


def guitar():
    im = grid(["..........mm",
               ".........nn.",
               "........nn..",
               ".......nn...",
               "......nn....",
               "..www.n.....",
               ".wWwwwg.....",
               "wwkkwwww....",
               "wwwkkwwg....",
               ".wwwwwwg....",
               "..wwwgg.....",
               "...gg......."], GTR)
    save('guitar', [im])


# ---------------------------------------------------------------- 快艇（远景里的小船）
BOAT = dict(w='#f0f0ec', g='#a8acb4', k='#2a2e38', r='#c83a3a', b='#3a6a9a', B='#8ac0e8')


def boat():
    im = grid(["........kk..........",
               ".......kBBk.........",
               "......kBBBBk........",
               "rrrrrrrrrrrrrrrrrr..",
               "wwwwwwwwwwwwwwwwwwww",
               ".wwwwwwwwwwwwwwwwww.",
               "..gggggggggggggggg.."], BOAT)
    save('boat', [im])


# ---------------------------------------------------------------- 婴儿的小手印（压在落叶 / 水洼 / 地上）：0 地上 / 1 水洼里的
HAND = dict(d='#5a4a3a', D='#3a2e24', b='#2a4a6a', B='#4a7aa0')


def hand():
    a = grid([".d.d.d..",
              ".d.d.d.d",
              ".dddddd.",
              "dddddd..",
              ".dddd...",
              "..dd...."], HAND)
    b = grid([".b.b.b..",
              ".b.b.b.b",
              ".bbbbbb.",
              "bbBBbb..",
              ".bbbb...",
              "..bb...."], HAND)
    save('shizuka_hand', [a, b], outline=False)


# ---------------------------------------------------------------- 粉底盒（药妆店）
POW = dict(p='#f0c8d8', P='#ffe8f0', g='#d0a040', G='#ffe070', s='#f4d4b4')


def compact():
    im = grid([".gggggg.",
               "gGPPPPGg",
               "gPpppppg",
               "gssssssg",
               ".gggggg."], POW)
    save('compact', [im])


# ---------------------------------------------------------------- 碎混凝土（J3 打地面）和黏地（修回水泥、沙子、水）
def rubble():
    im = Image.new('RGBA', (22, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x, y, w, h, c in ((1, 4, 5, 3, '#8a8e96'), (6, 2, 6, 5, '#a8acb4'), (13, 3, 4, 4, '#7a7e86'), (17, 5, 4, 2, '#9a9ea6'), (9, 6, 3, 2, '#6a6e76')):
        rect(d, (x, y, x + w, y + h), c)
        line(d, (x, y, x + w - 1, y), '#c8ccd2')
    save('rubble', [im])


def sticky():
    frames = []
    for k in range(2):
        im = Image.new('RGBA', (52, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        ellipse(d, (0, 1, 51, 15), '#6a665c')
        ellipse(d, (3, 2, 48, 13), '#8a857a')
        ellipse(d, (8, 4, 30, 10), '#a49e90')
        for i in range(6):                      # 冒泡的小点
            px(d, 10 + (i * 7 + k * 3) % 32, 5 + (i * 5 + k) % 6, '#c8c2b2')
        frames.append(im)
    save('sticky', frames, fps=3, kind='loop', outline=False)


# ---------------------------------------------------------------- 船员帽（被轰炸空间削掉飞起来）
def crewcap():
    im = grid(["..wwww..",
               ".wWWWWw.",
               "wwwwwwww",
               "kkkkkkkk"], dict(w='#e8e6dc', W='#ffffff', k='#2a2e38'))
    save('crewcap', [im])


# ---------------------------------------------------------------- 装箭的箱子（交给 SPW）
def arrowcase():
    im = grid(["kkkkkkkkkkkkkkkk",
               "kbbbbbbbbbbbbbbk",
               "kbggggggggggggbk",
               "kbgGGGGGGGGGGgbk",
               "kbbbbbbyybbbbbbk",
               "kbbbbbbyybbbbbbk",
               "kkkkkkkkkkkkkkkk"], dict(k='#1e1a16', b='#5a3a22', g='#8a5a30', G='#b07a40', y='#ffd84a'))
    save('arrowcase', [im])


# ---------------------------------------------------------------- 电视（电器店橱窗里的，念写用）
def tv():
    im = grid(["kkkkkkkkkkkkkk",
               "kgggggggggggkk",
               "kgBBBBBBBBBgkk",
               "kgBbbbbbbbBgkk",
               "kgBbbWbbbbBgkk",
               "kgBbbbbbbbBgkk",
               "kgBBBBBBBBBgkk",
               "kggggggggggrgk",
               "kkkkkkkkkkkkkk",
               "..k........k.."], dict(k='#1a1a22', g='#5a5a66', B='#2a3a5a', b='#4a7ab0', W='#e0f0ff', r='#e04040'))
    save('tv', [im])


# ---------------------------------------------------------------- 念写照片（S.photo({ image }) 用，单帧）
def photo_starfish():
    w, h = 40, 48
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, w, 26), '#8ac8e8')
    rect(d, (0, 26, w, 34), '#3a8ac0')
    rect(d, (0, 34, w, h), '#e8d4a0')
    for y in range(36, h, 4):
        line(d, (0, y, w, y), '#d8c08a')
    # 沙滩上一只海星
    pts = []
    import math
    for i in range(10):
        r = 9 if i % 2 == 0 else 4
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((20 + r * math.cos(a), 40 + r * math.sin(a) * 0.7))
    d.polygon(pts, fill=C('#e8743a'))
    px(d, 20, 39, '#ffb070')
    # 远处一个白色的人影（承太郎蹲在海边看）
    rect(d, (30, 22, 33, 33), '#f4f4f0')
    rect(d, (30, 20, 33, 22), '#ffffff')
    save('photo_starfish', [im], outline=False)


def photo_baby():
    w, h = 40, 48
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, w, h), '#7a7a72')
    rect(d, (0, 30, w, h), '#5e5e58')
    # 纸箱
    rect(d, (7, 22, 33, 42), '#c89a5a')
    line(d, (7, 22, 33, 22), '#8a6234')
    rect(d, (7, 23, 33, 25), '#a87a40')
    # 箱子里一个婴儿的轮廓：只有一圈紫色的线（念写拍到的“看不见的人”）
    col = '#c080ff'
    for x, y in ((16, 12), (17, 11), (18, 10), (19, 10), (20, 10), (21, 10), (22, 11), (23, 12), (24, 13), (24, 14), (24, 15), (23, 16),
                 (22, 17), (21, 17), (20, 17), (19, 17), (18, 17), (17, 16), (16, 15), (15, 14), (15, 13),
                 (14, 18), (13, 19), (12, 20), (12, 21), (26, 18), (27, 19), (28, 20), (28, 21), (15, 18), (25, 18)):
        px(d, x, y, col)
    line(d, (13, 21, 27, 21), col)
    px(d, 18, 13, '#e0c0ff')
    px(d, 22, 13, '#e0c0ff')
    save('photo_baby', [im], outline=False)


def main():
    P.PROPS.clear()
    for f in (ebike, box, guitar, boat, hand, compact, rubble, sticky, crewcap, arrowcase, tv, photo_starfish, photo_baby):
        f()
    path = os.path.join(LIB.META, 'props_ch4.json')
    LIB.save_json(path, {'props': dict(P.PROPS)})
    print('第4章道具', len(P.PROPS), '个：', ' '.join(P.PROPS))


if __name__ == '__main__':
    main()
