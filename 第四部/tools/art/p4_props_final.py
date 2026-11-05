# 终章的道具：猫草、花瓶碎片、打火机、吉良吉广的照片、乔瑟夫的钱包。游戏比例直接画，格式照 p4_props.py（横向帧条 + size + pivot）。
#   用法：python3 第四部/tools/art/p4_props_final.py     → assets/props/<id>.png + _meta/props_final.json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as P  # noqa: E402


# ---------------------------------------------------------------- 猫草：一盆草，中间长着一张猫脸（0 闭眼 / 1 睁眼 / 2 鼓腮吹泡泡）
CAT = dict(G='#5ab04a', g='#2e7a34', L='#9ae070', P='#c8783a', p='#8a4a22', Y='#f0e0a0', y='#c8b070', k='#1a1020', w='#ffffff',
           e='#e0c020', n='#e07090', b='#bfe8ff')


def straycat():
    base = ['.....L..L.....',
            '....LGG.GL....',
            '..L.GYYYYG.L..',
            '..GGYYYYYYGG..',
            '.LGYYYYYYYYGL.',
            '.GGYyYYYYyYGG.',
            '.GYYEEYYEEYYG.',
            '.GYYYYnnYYYYG.',
            '..GYYYYYYYYG..',
            '.LGGyYYYYyGGL.',
            'GGgGGGGGGGGgGG',
            '.gGgGgGgGgGgG.',
            '..PPPPPPPPPP..',
            '..pPPPPPPPPp..',
            '...pPPPPPPp...',
            '...pppppppp...']
    frames = []
    for i in range(3):
        rows = list(base)
        if i == 0:
            rows[6] = '.GYYkkYYkkYYG.'
        else:
            rows[6] = '.GYYekYYkeYYG.'
        if i == 2:
            rows[7] = '.GYYYYbbYYYYG.'
            rows[8] = '..GYYYbbYYYG..'
        frames.append(P.grid(rows, dict(CAT, E='#e0c020')))
    P.save('fin_straycat', frames)


def shard():
    rows = ['..w.',
            '.wbw',
            'wbbb',
            '.bb.']
    P.save('fin_shard', [P.grid(rows, dict(w='#ffffff', b='#a8d8f0'))])


def lighter():
    off = ['.mm.',
           'mMMm',
           'RRRR',
           'RrrR',
           'RrrR',
           'RRRR']
    on = ['.F..',
          'FfF.',
          '.f..',
          '.mm.',
          'mMMm',
          'RRRR',
          'RrrR',
          'RrrR',
          'RRRR']
    pal = dict(m='#a0a0b0', M='#d0d0dc', R='#c03040', r='#e05060', F='#ff9a30', f='#fff0a0')
    P.save('fin_lighter', [P.grid(off, pal), P.grid(on, pal)])


def photo():
    """吉良吉广的照片：白边相纸，里面一个秃头老人的上半身（0 平静 / 1 张嘴喊）"""
    frames = []
    for i in range(2):
        im = Image.new('RGBA', (16, 20), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 15, 19), fill=LIB.hexc('#f4f0e6'))
        d.rectangle((2, 2, 13, 15), fill=LIB.hexc('#9aa4b0'))
        d.rectangle((3, 10, 12, 15), fill=LIB.hexc('#5a4a5a'))                 # 衣服
        d.ellipse((5, 4, 10, 10), fill=LIB.hexc('#e8c0a0'))                    # 秃头
        d.point((5, 7), fill=LIB.hexc('#c8c8d0'))
        d.point((10, 7), fill=LIB.hexc('#c8c8d0'))
        d.point((6, 7), fill=LIB.hexc('#1a1020'))
        d.point((9, 7), fill=LIB.hexc('#1a1020'))
        if i == 1:
            d.rectangle((7, 9, 8, 10), fill=LIB.hexc('#6a1020'))
        else:
            d.line((7, 9, 8, 9), fill=LIB.hexc('#8a5a4a'))
        frames.append(im)
    P.save('fin_photo', frames, pivot=[9, 11])


def wallet():
    rows = ['bbbbbbbb',
            'bBBBBBBb',
            'bBBBBgBb',
            'bBBBBBBb',
            'bbbbbbbb']
    P.save('fin_wallet', [P.grid(rows, dict(b='#5a3420', B='#8a5a34', g='#f0c040'))])


def main():
    P.PROPS.clear()
    for f in (straycat, shard, lighter, photo, wallet):
        f()
    path = os.path.join(LIB.META, 'props_final.json')
    meta = LIB.load_json(path, {}) or {}
    meta.setdefault('props', {}).update(P.PROPS)
    LIB.save_json(path, meta)
    print('道具', ' '.join(P.PROPS))


if __name__ == '__main__':
    main()
