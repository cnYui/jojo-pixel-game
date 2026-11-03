# 第10章的道具：谜的纸（折着 / 打开 / 纸里有人）、陷阱纸冒出来的东西（火、纸蝎子、电光）、铁塔上的铆钉和碎铁、丰大扔的螺栓、
#   康一的书包、裕也闻到的气味脚印、未起隆变的磁铁和小喇叭、章末那本《谜》。游戏比例直接画，写法照 p4_props.py（字符图 + 自动描边）。
#   用法：python3 第四部/tools/art/p4_props_ch10.py → assets/props/<id>.png、assets/_meta/props_ch10.json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as P  # noqa: E402

PAL = dict(W='#fbf8ef', w='#ddd6c4', c='#b8ae98', k='#2a2030', Y='#f0d070', y='#b89a40', B='#6a4a2a', b='#4a301c',
           J='#2a2238', j='#4a3e68', S='#e8b48a', s='#c08860', T='#5a3a2a', P='#c890c8',
           O='#ff9a2a', o='#e04a1a', R='#ffe060', r='#c03020', D='#5a3020', d='#3a2014', E='#fff6a0', e='#ffd040',
           G='#9aa0ac', g='#6a7080', H='#c8ccd8', N='#ff70a0', n='#c04a80', M='#e03a3a', m='#9a2020', A='#e0b050', a='#a07a30',
           V='#4a2a5a', v='#2a1838', X='#e8e0ff')

PAPER_FOLD = ['WWWWWWWWWW', 'WWWWWWWWWw', 'wwwwwwwwww', 'WWWWWWWWWw', 'WWWWWWWWWw', 'wcccccccccw'[:10]]
PAPER_OPEN = ['WWWWWWWwWWWWWWWW', 'WWWWWWWwWWWWWWWW', 'WWWWWWWwWWWWWWWW', 'WWWWWWWwWWWWWWWW', 'WWWWWWWwWWWWWWWW',
              'wwwwwwwcwwwwwwww', 'WWWWWWWwWWWWWWWW', 'WWWWWWWwWWWWWWWW', 'WWWWWWWwWWWWWWWW', 'WWWWWWWwWWWWWWWW', 'ccccccccccccccc.']


def face_paper(hair, hl):
    """纸上印着一张小脸（谁被关在里面）：hair 头发色、hl 高光"""
    rows = [r for r in PAPER_OPEN]
    face = ['....' + hair * 6 + '......', '...' + hair * 2 + hl * 3 + hair * 3 + '.....', '...' + hair + 'SSSSSS' + hair + '.....',
            '...' + 'SkSSkS'.rjust(7, 'S') + '.....', '....SSsSSS......', '.....SSSS.......']
    out = []
    for y, r in enumerate(rows):
        if 2 <= y < 2 + len(face):
            f = face[y - 2].ljust(16, '.')
            out.append(''.join(fc if fc != '.' else rc for fc, rc in zip(f, r)))
        else:
            out.append(r)
    return out


FIRE = ['....O.....', '...OO..O..', '..ORO.OO..', '..ORRO.O..', '.ORRRRO...', '.OREERRO..', 'OREEEERO.', 'ORREEERRO', '.oRRRRRo.',
        '..ooooo..', 'WWWWWWWWWW']
SCORP = ['.d...d..', 'dDd.dDd.', '.DDDDD.D', '..DDD..D', '.D.D.DD.', 'D...D...']
SPARK = ['..E.......E.....', '.EeE.....EeE...E', 'Ee.eE...Ee.eE.Ee', 'e...eE.Ee...eEe.', '.....eEe.....e..']
RIVET = ['.GGGG.', 'GHHHGg', 'GHgHGg', 'GHHHGg', '.gggg.']
DEBRIS = ['G......g..', '.g..H.....', '...G...Gg.', 'gH...g...G', '..G..H.g..']
BOLT = ['.HG.', 'HGGg', 'GGgg', '.gg.']
BAG = ['...bbbbbb...', '..b......b..', 'BBBBBBBBBBBB', 'BbbbbbbbbbbB', 'BBBBByBBBBBB', 'BBBBBBBBBBBB', 'BBBBBBBBBBBB', 'bbbbbbbbbbbb']
SCENT = ['.NN....NN.', 'NNNn..NNNn', 'NNn...NNn.', '.n.....n..']
MAGNET = ['MMM..MMM', 'MMm..MMm', 'MMm..MMm', 'HHm..HHm', 'MMMmMMMm', '.MMMMMm.', '..mmmm..']
HORN = ['......AA', '....AAAA', 'aaaAAEAA', 'aaaAAEAA', '....AAAA', '......AA']
BOOK = ['VVVVVVVVVV', 'VXXXXXXXvW', 'VXvvvvvXvW', 'VXvXXXvXvW', 'VXvvvvvXvW', 'VXXXXXXXvW', 'VXXvvvXXvW', 'VXXXXXXXvW', 'VVVVVVVVvW',
        'vvvvvvvvvW']


def main():
    P.PROPS.clear()
    g = lambda rows: P.grid(rows, PAL)
    P.save('paper', [g(PAPER_FOLD), g(PAPER_OPEN), g(face_paper('Y', 'E')), g(face_paper('B', 'y')), g(face_paper('J', 'j'))])
    P.save('paper_trap', [g(FIRE), g(SCORP), g(SPARK)])
    P.save('rivet', [g(RIVET), g(DEBRIS)])
    P.save('bolt', [g(BOLT)], pivot=None)
    P.save('koichi_bag', [g(BAG)])
    P.save('scent', [g(SCENT)])
    P.save('magnet', [g(MAGNET)])
    P.save('horn', [g(HORN)])
    P.save('enigma_book', [g(BOOK)])
    path = os.path.join(LIB.META, 'props_ch10.json')
    LIB.save_json(path, {'props': dict(P.PROPS)})
    print('道具', list(P.PROPS))


if __name__ == '__main__':
    main()
