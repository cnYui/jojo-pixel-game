# 第9章的道具：未起隆变的运动鞋、蜡烛、公路之星的脚印、国道上的车（小轿车、卡车、锥桶）、猫草的空气弹、牛奶碟、病房的花束。
#   画法照 p4_props.py（字符图 + 自动描边）；骰子和碗在小游戏的 UI 层里直接画，不做成道具。
#   用法：python3 第四部/tools/art/p4_props_ch9.py   → assets/props/<id>.png + _meta/props_ch9.json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as P  # noqa: E402


def sneaker():
    im = P.grid(["......WWW...",
                 ".....WbbW...",
                 "....WbbbWWW.",
                 "WWWWbbbbbbbW",
                 "WbbbbbbbbbbW",
                 "RRRRRRRRRRRR",
                 "wwwwwwwwwwww"], dict(W='#e8e8f0', b='#2c3a78', R='#a8203a', w='#d0ccc4'))
    P.save('ch9_sneaker', [im])


def candle():
    fr = []
    for k in range(2):
        rows = ["..y..", ".yOy.", ".yOy." if k else "..O..", "..k..", ".WWW.", ".WWW.", ".WWW.", ".WWW.", "GGGGG"]
        fr.append(P.grid(rows, dict(y='#ffd040', O='#ff8020', k='#2a1a10', W='#f4ecd8', G='#c8a040')))
    fr.append(P.grid([".....", ".....", ".....", ".....", ".....", ".....", "..WWW", ".WWWW", "GGGGG"],
                     dict(W='#f4ecd8', G='#c8a040')))         # 倒了
    P.save('ch9_candle', fr, fps=6, kind='loop')


def footprint():
    im = P.grid([".pp.....",
                 "pppp....",
                 "pppp..pp",
                 ".pp..ppp",
                 "......pp",
                 "........"], dict(p='#e0507a'))
    P.save('ch9_foot', [im], outline=False)


def car(col, dark):
    return P.grid(["......GGGGGGGG..........",
                   ".....GsssssssssG........",
                   "....GsssGssssssGG.......",
                   "CCCCCCCCCCCCCCCCCCCCCCC.",
                   "CccCCCCCCCCCCCCCCCCCCCyy",
                   "CCCCCCCCCCCCCCCCCCCCCCCC",
                   "ddddddddddddddddddddddd.",
                   "...kkk...........kkk....",
                   "...kwk...........kwk....",
                   "...kkk...........kkk...."],
                  dict(G='#2a2a3a', s='#9ad0f0', C=col, c='#ffffff', d=dark, y='#ffe070', k='#1a1a20', w='#a0a0a8'))


def truck():
    return P.grid(["..........SSSSSSSSSSSSSSSSSSSSSS",
                   "..GGGGG...SssssssssssssssssssssS",
                   ".GsssG....SssssssssssssssssssssS",
                   "GsssssG...SssssssssssssssssssssS",
                   "CCCCCCCC..SssssssssssssssssssssS",
                   "CCCCCCCCCCSSSSSSSSSSSSSSSSSSSSSS",
                   "CyCCCCCCCCdddddddddddddddddddddd",
                   "dddddddddddddddddddddddddddddddd",
                   "..kkk...........kkk....kkk......",
                   "..kwk...........kwk....kwk......",
                   "..kkk...........kkk....kkk......"],
                  dict(G='#2a2a3a', s='#d8d8d0', S='#a0a098', C='#3a6ad0', y='#ffe070', d='#3a3a44', k='#1a1a20', w='#a0a0a8'))


def vehicles():
    P.save('ch9_car', [car('#d84040', '#8a2020'), car('#e8e8e8', '#9a9aa4'), car('#3a8a5a', '#1e4a30')])
    P.save('ch9_truck', [truck()])
    cone = P.grid(["..O..", "..O..", ".WWW.", ".OOO.", "OOOOO", "KKKKK"], dict(O='#f07020', W='#ffffff', K='#3a3a3a'))
    P.save('ch9_cone', [cone])


def bubble():
    fr = []
    for r in (3, 4):
        im = Image.new('RGBA', (2 * r + 3, 2 * r + 3), (0, 0, 0, 0))
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                d = ((x - r - 1) ** 2 + (y - r - 1) ** 2) ** 0.5
                if r - 0.8 <= d <= r + 0.4:
                    px[x, y] = LIB.hexc('#c8eaff')
        px[r - 1, r - 1] = LIB.hexc('#ffffff')
        fr.append(im)
    P.save('ch9_bubble', fr, fps=8, kind='loop', outline=False, align='center')


def small_things():
    dish = P.grid([".WWWWWW.", "WwwwwwwW", ".WWWWWW."], dict(W='#d8d8e0', w='#ffffff'))
    P.save('ch9_dish', [dish])
    flowers = P.grid(["R.Y.P", "RRYPP", ".gGg.", "..g..", ".BBB.", ".BBB."],
                     dict(R='#e04050', Y='#ffd040', P='#d070d0', g='#3a8a3a', G='#5ab04a', B='#7aa0d8'))
    P.save('ch9_flowers', [flowers])


def main():
    for f in (sneaker, candle, footprint, vehicles, bubble, small_things):
        f()
    path = os.path.join(LIB.META, 'props_ch9.json')
    meta = LIB.load_json(path, {}) or {}
    meta.setdefault('props', {}).update(P.PROPS)
    LIB.save_json(path, meta)
    print('道具', ' '.join(P.PROPS))


if __name__ == '__main__':
    main()
