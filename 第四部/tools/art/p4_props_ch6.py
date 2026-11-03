# 第6章的道具（第四部/docs/第6章_开发脚本.md §4）：纸袋、硬币、彩票、汇票（整张 / 撕成两半）、100 日元硬币、纽扣、三明治、报纸。
#   画法照 p4_props.py：游戏比例直接画，一个字母一种颜色，外面自动描 1 px 深色边。
#   用法：python3 第四部/tools/art/p4_props_ch6.py      输出 assets/props/<id>.png + assets/_meta/props_ch6.json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as PR  # noqa: E402

PAL = dict(B='#c89a62', b='#9a6e3e', L='#e2bc84', W='#fff8ea', w='#d8d0c0', Y='#f2c440', y='#b8862a', G='#e8e8f0', g='#a8a8b8',
           R='#d84050', P='#6c5aa0', K='#3a2a20', T='#e8d8b0', t='#b8a070', V='#7a64a6', v='#4c3a74', N='#5a4030', n='#f4ecd8',
           E='#5aa860', S='#f0c8a0', C='#2a2a3a', c='#8a8aa0')


def paperbag():
    rows = ['..LLLLLLLL..',
            '.LBBBBBBBBL.',
            '.BBBBBBBBBb.',
            '.BBbBBBBBBb.',
            '.BBBBBBBBBb.',
            '.BBBBWWBBBb.',
            '.BBBBWWBBBb.',
            '.BBBBBBBBBb.',
            '.BBBBBBBBBb.',
            '.bbbbbbbbbb.']
    PR.save('paperbag', [PR.grid(rows, PAL)])


def coins():
    c10 = ['.yy.', 'yYYy', 'yYYy', '.yy.']
    c100 = ['.gg.', 'gGGg', 'gGcg', '.gg.']
    PR.save('coin', [PR.grid(c10, PAL)], align='center')
    PR.save('coin100', [PR.grid(c100, PAL)], align='center')


def ticket():
    rows = ['WWWWWWWWWW',
            'WRRWPPPPWW',
            'WWWWWWWWWW',
            'WKKWKKWKKW',
            'WWWWWWWWWW']
    back = ['wwwwwwwwww',
            'wKKKKwwwww',
            'wwwwwwwwww',
            'wKKKwKKKKw',
            'wwwwwwwwww']
    PR.save('lottery', [PR.grid(rows, PAL), PR.grid(back, PAL)], align='center')


def check():
    whole = ['TTTTTTTTTTTT',
             'TKKKTTTTTVVT',
             'TTTTTTTTTVVT',
             'TKKKKKKKTTTT',
             'TTTTTTTTTTTT',
             'ttttttttttt.']
    torn = ['TTTTT..TTTTT',
            'TKKKT.TTTVVT',
            'TTTT..TTTVVT',
            'TKKKK.KKTTTT',
            'TTTTT..TTTTT',
            'ttttt..tttt.']
    PR.save('check', [PR.grid(whole, PAL), PR.grid(torn, PAL)], align='center')


def button():
    rows = ['.vv.', 'vVVv', 'VnVn', 'vVVv', '.vv.']
    rows = ['.VVV.', 'VVnVV', 'VnVnV', 'VVnVV', '.VVV.']
    PR.save('button', [PR.grid(rows, PAL)], align='center')


def sandwich():
    rows = ['..TTTT..', '.TTTTTT.', 'EEEEEEEE', 'SSSSSSSS', 'tttttttt']
    PR.save('sandwich', [PR.grid(rows, PAL)])


def newspaper():
    rows = ['nnnnnnnnnn', 'nKKKKnCCCn', 'nnnnnnCCCn', 'nKKnKKnnnn', 'nnnnnnnnnn', 'nKKKnKKKnn', 'nnnnnnnnnn']
    PR.save('newspaper', [PR.grid(rows, PAL)])


def main():
    for f in (paperbag, coins, ticket, check, button, sandwich, newspaper):
        f()
    path = os.path.join(LIB.META, 'props_ch6.json')
    meta = LIB.load_json(path, {}) or {}
    meta.setdefault('props', {}).update(PR.PROPS)
    LIB.save_json(path, meta)
    print('道具', len(PR.PROPS), '个：', ' '.join(PR.PROPS))


if __name__ == '__main__':
    main()
