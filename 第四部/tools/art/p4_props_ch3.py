# 第3章的道具（第四部/docs/分章开发约定.md：写自己的 props_ch3.json，复用 p4_props 的 grid / save）。
#   电椅、鞋柜直接从第3章背景线程画的图层裁出来（同一张图，剧情里要能挪动，所以另存一份道具）。
#   用法：python3 第四部/tools/art/p4_props_ch3.py
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as P  # noqa: E402

grid, save = P.grid, P.save


def from_layer(pid, layer):
    im = Image.open(os.path.join(LIB.ASSETS, 'bg', 'seaside_villa', layer + '.png')).convert('RGBA')
    im = im.crop(im.getbbox())
    save(pid, [im], outline=False)


def bento():
    pal = dict(P='#f088b0', p='#c05080', W='#fff4e8', w='#e0c8b8', R='#e04040', G='#60b050', Y='#ffd84a')
    box = grid(["PPPPPPPPPP",
                "PWWWWWWWWP",
                "PWRRWWGGWP",
                "PWWYYWWWWP",
                "pppppppppp"], pal)
    note = grid(["PPPPPPPPPP",
                 "PWWWwwWWWP",
                 "PWwWWWWwWP",
                 "PWWWWWWWWP",
                 "pppppppppp"], pal)
    save('bento', [box, note])


def tail_tip():
    pal = dict(O='#f0aa28', o='#c47814', L='#c0d070', g='#465030')
    a = grid(["...O..",
              "..OOO.",
              ".OOooO",
              "..Lo..",
              "..gL..",
              "...g.."], pal)
    save('tail_tip', [a])


def notebook():
    pal = dict(B='#7c84d6', b='#4a52a0', W='#fafaf4', w='#d8d8e0', K='#c8a6ee')
    a = grid(["BBBBBBBBBBBB",
              "BWWWWWWWWWWb",
              "BWKKKKKKWWWb",
              "BWWWWWWWWWWb",
              "BWwwwwwwwWWb",
              "BWWWWWWWWWWb",
              "bbbbbbbbbbbb"], pal)
    save('notebook', [a])


def dishes():
    """四道菜（0 矿泉水、1 番茄马苏里拉、2 番茄面、3 布丁），放在餐桌上"""
    pal = dict(W='#fafafa', w='#c8c8d4', B='#a0d8f8', b='#5aa0d0', R='#e0402e', r='#a82418', M='#fff8e8', G='#58a848',
               Y='#f8d060', y='#c89a30', C='#7a4a20')
    water = grid(["..BB..",
                  "..BB..",
                  ".BBBB.",
                  ".BbbB.",
                  ".BBBB.",
                  "wwwwww"], pal)
    caprese = grid(["..........",
                    ".RMRMRMG..",
                    "RMRMRMRMG.",
                    "WWWWWWWWWW",
                    ".wwwwwwww."], pal)
    pasta = grid(["...rRr....",
                  "..RYRYRR..",
                  ".RYRRYRYR.",
                  "WWWWWWWWWW",
                  ".wwwwwwww."], pal)
    pudding = grid(["...CC...",
                    "..YYYY..",
                    "..YYYY..",
                    ".YYyyYY.",
                    "WWWWWWWW",
                    ".wwwwww."], pal)
    save('dish', [water, caprese, pasta, pudding])


def tv_static():
    """电视雪花（12×9 的屏幕，2 帧）+ 第 2 帧里闪过一个发光的小人影"""
    import random
    frs = []
    for k in range(2):
        rnd = random.Random(k + 3)
        im = Image.new('RGBA', (14, 11), (40, 40, 48, 255))
        a = im.load()
        for y in range(1, 10):
            for x in range(1, 13):
                v = rnd.randint(90, 230)
                a[x, y] = (v, v, v + 10, 255)
        if k == 1:
            for x, y in ((6, 3), (7, 3), (6, 4), (7, 4), (5, 5), (6, 5), (7, 5), (8, 5), (6, 6), (7, 6), (5, 7), (8, 7)):
                a[x, y] = (255, 236, 120, 255)
        frs.append(im)
    save('tv_static', frs, outline=True)


def main():
    P.PROPS.clear()
    from_layer('echair', 'chair')
    from_layer('shoecab', 'shoebox')
    for f in (bento, tail_tip, notebook, dishes, tv_static):
        f()
    path = os.path.join(LIB.META, 'props_ch3.json')
    LIB.save_json(path, {'props': dict(P.PROPS)})
    print('道具', len(P.PROPS), '个：', ' '.join(P.PROPS))


if __name__ == '__main__':
    main()
