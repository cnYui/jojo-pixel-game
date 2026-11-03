# 第1章的道具：弓与箭、飞出去的箭、砖头、木箱里的碎纸、拼好的全家福、导弹碎片。游戏比例直接画，格式照 p4_props.py。
#   飞起来的花盆沿用序章的 pot（0 好的 / 1 碎的）。元数据写 _meta/props_ch1.json（build_p4.py 深合并进 props）。
#   用法：python3 第四部/tools/art/p4_props_ch1.py
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as P  # noqa: E402
from p4_bglib import C, ellipse, line, px, rect  # noqa: E402

PAL = dict(w='#8a5a2e', W='#b88446', d='#5a3618', s='#e8e0c8', S='#c8bfa8', g='#d8b040', G='#a07a20', r='#c04030', R='#e86a4a',
           k='#3a3a40', K='#6a6a72', o='#7a8a4a', O='#a8b468', y='#ffe070', b='#b85a3a', B='#d8805a', c='#8a3a2a',
           p='#ece4d0', P='#c8bea8', m='#5a5048')


def bow_arrow():
    # 弓（竖着的弧 + 弦）和斜插的一支箭：箭头是金色的古旧箭头，箭杆木色
    return P.grid([".......Ww.....",
                   "......W..ws...",
                   ".....W....s...",
                   "....W.....s.g.",
                   "....w.....sgG.",
                   "...w......gG..",
                   "...w.....wd...",
                   "...w....wd.s..",
                   "....w..wd..s..",
                   "....w.wd...s..",
                   ".....wd....s..",
                   "....wdW...s...",
                   "...ss..W.ws...",
                   "..ss....Ww...."], PAL)


def arrow(lit=False):
    # 飞出去的箭（朝右）：金箭头 + 木杆 + 白羽
    row = ["s.s.........", ".sswwwwwwwgG", "s.s.......gy"] if lit else ["s.s.........", ".sswwwwwwwgG", "s.s.......g."]
    return P.grid(row, PAL)


def brick():
    return P.grid(["RRRRRr", "RbbbBr", "rcccrr"], PAL)


def scraps():
    return P.grid(["..p.P....p..", ".pPp.p.P.Pp.", "pPpPpPpPpPPp"], PAL)


def debris(blink=False):
    k = 'y' if blink else 'K'
    return P.grid(["..k" + k + "..", ".kOok.", "kooOkk"], PAL)


def family_photo():
    """拼好的全家福（40×32，S.photo 放大显示）：年轻的父亲、母亲、两个小男孩。碎纸拼回去的痕迹留几道浅裂纹"""
    w, h = 40, 32
    im = Image.new('RGBA', (w, h), C('#d8c8a0'))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, w, 20), '#e8dcb8')
    rect(d, (0, 20, w, h), '#b8a478')
    for y in range(22, h, 3):
        line(d, (0, y, w, y), '#ac9870')

    def person(x, top, hh, hair, shirt, skin='#e8c4a0'):
        ellipse(d, (x - 3, top, x + 3, top + 6), skin)
        rect(d, (x - 3, top - 1, x + 3, top + 2), hair)
        rect(d, (x - 4, top + 7, x + 4, top + hh), shirt)
        px(d, x - 1, top + 3, '#3a2a20')
        px(d, x + 1, top + 3, '#3a2a20')
        line(d, (x - 1, top + 5, x + 1, top + 5), '#a06050')
    person(10, 6, 22, '#4a3424', '#5a6a8a')          # 父亲（年轻时）
    person(29, 8, 21, '#2a1a14', '#c07a8a')          # 母亲
    person(17, 15, 13, '#d8b860', '#3a3a44')         # 哥哥（形兆，金发）
    person(23, 17, 12, '#2a2420', '#3a4a6a')         # 弟弟（亿泰）
    # 拼回去的裂纹（疯狂钻石修得很干净，只剩极浅的几道）
    for a, b in (((0, 11), (15, 13)), ((15, 13), (22, 31)), ((22, 0), (26, 13)), ((26, 13), (40, 17))):
        line(d, (*a, *b), '#c8b890')
    return im


def main():
    P.PROPS.clear()
    P.save('bow_arrow', [bow_arrow()], pivot=None)
    P.save('arrow', [arrow(), arrow(True)], pivot=None, fps=8, kind='loop', align='center')
    P.save('brick', [brick()], align='center')
    P.save('photo_torn', [scraps()])
    P.save('missile_debris', [debris(), debris(True)], fps=4, kind='loop')
    ph = family_photo()
    os.makedirs(P.OUT, exist_ok=True)
    ph.save(os.path.join(P.OUT, 'photo_family.png'))
    P.PROPS['photo_family'] = dict(image='props/photo_family', frames=1, size=[ph.width, ph.height], pivot=[20, 16], fps=1, kind='static', k=1.0)
    path = os.path.join(LIB.META, 'props_ch1.json')
    LIB.save_json(path, {'props': dict(P.PROPS)})
    print('道具：', ', '.join(P.PROPS))


if __name__ == '__main__':
    main()
