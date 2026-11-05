# 第11章的道具（游戏比例直接画，格式照 p4_props.py：横向帧条 + size + pivot）。元数据写 _meta/props_ch11.json（build_p4.py 自动深合并）。
#   camcorder11 早人的小摄像机、tape11 录像带、roll11 乙雅三的图纸筒、photo11 露伴拍的照片（0 川尻浩作的背影 / 1 正脸 / 2 角落里举着摄像机的男孩）、
#   yphoto11 浮在窗外的旧照片（吉良吉广，第8章的人；这里只画相框和一团灰影）、arrow11 箭、bubble11 猫草吐的空气弹、
#   ph11_straycat 猫草（第9章画正式的；这里是花盆里一株长着猫脸的草，正式图合进来后剧情自动换成 straycat）。
#   用法：python3 第四部/tools/art/p4_props_ch11.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as P  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

CAM = dict(k='#2a2a34', K='#4a4a58', g='#7a7a88', l='#9ac8f0', L='#d8f0ff', r='#e83a3a', s='#c8c8d0')


def camcorder():
    f0 = ["..kkkkkkk..",
          ".kKKKKKKKkk",
          "kKggKKKKKlL",
          "kKKKKKKKKll",
          "kKKKrKKKKkk",
          ".kkkkkkkk..",
          "...ss......"]
    f1 = [r.replace('r', 'K') for r in f0]
    P.save('camcorder11', [P.grid(f0, CAM), P.grid(f1, CAM)], align='center')


TAPE = dict(k='#1e1e26', K='#3a3a46', w='#f0ece0', t='#8a6a4a')


def tape():
    P.save('tape11', [P.grid(["kkkkkkkkkk",
                              "kwwwwwwwwk",
                              "kKtKKKKtKk",
                              "kKKKKKKKKk",
                              "kkkkkkkkkk"], TAPE)], align='center')


ROLL = dict(b='#4a78c0', B='#2e528a', w='#eef2fa', c='#c8b890')


def roll():
    P.save('roll11', [P.grid(["wwbbbbbbbbbbww",
                              "wbBBBBBBBBBBbw",
                              "wwbbbbbbbbbbww"], ROLL)], align='center')


ARR = dict(m='#c8c0a8', M='#8a8270', h='#e8d870', H='#a89430', f='#d84a3a')


def arrow():
    P.save('arrow11', [P.grid([".......h.",
                               "fMMMMMMHh",
                               ".......h."], ARR)], align='center')


BUB = dict(w='#f4fbff', b='#bfe4f8', B='#86c2e6')


def bubble():
    P.save('bubble11', [P.grid(["..bbb..",
                                ".bwwbb.",
                                "bwbbbBb",
                                "bbbbbBb",
                                "bbbbBBb",
                                ".bBBBb.",
                                "..bbb.."], BUB)], align='center', outline=False)


SC = dict(G='#5aa848', g='#357a32', l='#9ad870', p='#b86a3a', P='#7e4422', y='#f0e060', k='#1a1020', w='#ffffff', n='#e89aa8')


def straycat():
    rows = ["..l...l..",
            ".lGl.lGl.",
            ".GGGGGGG.",
            "GGyGGGyGG",
            "GGkGnGkGG",
            ".GGGwGGG.",
            "..gGGGg..",
            "g..gGg..g",
            ".g.gGg.g.",
            "..ggGgg..",
            ".ppppppp.",
            ".pPPPPPp.",
            "..pPPPp..",
            "..ppppp.."]
    f1 = [r.replace('y', 'k') if i == 3 else r for i, r in enumerate(rows)]
    P.save('ph11_straycat', [P.grid(rows, SC), P.grid(f1, SC)])


def photo_img(kind):
    """露伴拍的照片（42×50，白边）：0 浩作的背影 / 1 浩作的侧脸 / 2 远处举着摄像机的男孩"""
    W, H = 40, 48
    im = Image.new('RGBA', (W, H), LIB.hexc('#f4f0e4'))
    d = ImageDraw.Draw(im)
    d.rectangle((3, 3, W - 4, H - 10), fill=LIB.hexc('#8aa2b8'))
    d.rectangle((3, 26, W - 4, H - 10), fill=LIB.hexc('#9a9490'))
    d.rectangle((3, 14, 12, 26), fill=LIB.hexc('#c8bca0'))
    d.rectangle((28, 10, W - 4, 26), fill=LIB.hexc('#b0a890'))
    suit, hair, skin = LIB.hexc('#6a5e7a'), LIB.hexc('#b08a5a'), LIB.hexc('#f0c49a')
    if kind in (0, 1):
        d.rectangle((16, 21, 24, 36), fill=suit)
        d.ellipse((16, 13, 24, 21), fill=hair if kind == 0 else skin)
        if kind == 1:
            d.rectangle((16, 13, 24, 15), fill=hair)
            d.point((22, 17), fill=LIB.hexc('#2a1a2a'))
    else:
        d.rectangle((26, 27, 30, 35), fill=LIB.hexc('#a8c83a'))
        d.ellipse((26, 22, 30, 27), fill=LIB.hexc('#c8682e'))
        d.rectangle((23, 25, 26, 27), fill=LIB.hexc('#2a2a34'))
        d.rectangle((10, 22, 16, 36), fill=suit)
        d.ellipse((10, 16, 16, 22), fill=hair)
    d.rectangle((0, 0, W - 1, H - 1), outline=LIB.hexc('#c8c0ac'))
    return im


def photos():
    P.save('photo11', [photo_img(0), photo_img(1), photo_img(2)], pivot=[21, 25], align='center')


def yphoto():
    W, H = 16, 20
    im = Image.new('RGBA', (W, H), LIB.hexc('#6a4a2a'))
    d = ImageDraw.Draw(im)
    d.rectangle((2, 2, W - 3, H - 3), fill=LIB.hexc('#d8ccb0'))
    d.ellipse((5, 5, 10, 10), fill=LIB.hexc('#8a8070'))
    d.rectangle((4, 10, 11, 16), fill=LIB.hexc('#8a8070'))
    P.save('yphoto11', [im], align='center')


def main():
    for f in (camcorder, tape, roll, arrow, bubble, straycat, photos, yphoto):
        f()
    path = os.path.join(LIB.META, 'props_ch11.json')
    meta = LIB.load_json(path, {}) or {}
    meta.setdefault('props', {}).update(P.PROPS)
    LIB.save_json(path, meta)
    print('道具', ' '.join(P.PROPS))


if __name__ == '__main__':
    main()
