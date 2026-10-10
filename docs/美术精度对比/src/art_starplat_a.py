"""方案 A：白金之星 idle 第 0 帧，2 倍分辨率重画（100x114，脚点 (54, 116)，和原图一样脚点在图外 = 浮空）。
画法：原图 xBR 2 倍（只用原色）定剪影 → 2px 描边削成 1px → 手画脸（头带、眉弓、发光的眼、鼻、嘴、下颌）
→ 手画肌肉分界线（胸大肌下沿、腹白线、三排腹肌、肩、大腿股四头肌、膝盖）和头发发束线
→ 按“光从左上来”给每种材质做一次受光边 / 背光边（凸起的肌肉：上沿亮、下沿暗）→ 金饰 / 围巾点高光 → 自动描边。"""
import sys
sys.dont_write_bytecode = True
from pixart import Canvas, base2x
from palettes import STARPLAT
from common import frame

PIVOT = (54, 116)

# 材质：明暗阶（暗 → 亮）和“分界线”色
RAMPS = {
    'skin': ['D', 'V', 'u', 'v', 'l', 'L'],
    'hair': ['A', 'a', 'c'],
    'red': ['R', 'r', 'f'],
    'gold': ['Y', 'y', 'o'],
}
MAT = {ch: m for m, r in RAMPS.items() for ch in r}
LINE = {'skin': 'D', 'hair': 'A', 'red': 'R', 'gold': 'Y'}

# ------------------------------------------------------------------ 脸（16..31 行），逐段手写
FACE = {
    16: [(61, 'yyyyyyyy')],
    17: [(58, 'yoooooooyyyY')],
    18: [(58, 'yyyyyyyyyyYY')],
    19: [(57, 'YYYYYYYYYYYYY')],
    20: [(56, 'lLllllllllvvvv')],
    21: [(56, 'lLllDDDllDDDv')],
    22: [(55, 'lllkkkkkllkkkk')],
    23: [(55, 'lllkwEEklLkwEEk')],
    24: [(55, 'lllkEEeklllVkEekv')],
    25: [(55, 'llllluuullVuuuuv')],
    26: [(55, 'llLlvvvvvlVDvvvvv')],
    27: [(55, 'lllvvvvvvvVvvvvvV')],
    28: [(55, 'lllvvvvVDDDDDVVV')],
    29: [(55, 'VVvvvvvvVVVVvVV')],
    30: [(56, 'DDVVVVVV')],
}
FACE_BOX = (54, 15, 73, 31)   # 这块不参与自动明暗

# ------------------------------------------------------------------ 手画的线（折线），只画在指定材质上
STROKES = [
    # 头发：从头顶往后（左）飘的几束
    ('hair', 'A', [(60, 9), (52, 12), (44, 16), (38, 19)]),
    ('hair', 'A', [(63, 10), (56, 15), (49, 20), (41, 24), (34, 26)]),
    ('hair', 'A', [(55, 19), (48, 24), (41, 29)]),
    ('hair', 'A', [(66, 8), (70, 12), (72, 17)]),
    ('hair', 'A', [(52, 27), (46, 31), (40, 32)]),
    ('hair', 'A', [(57, 6), (51, 9), (45, 10)]),
    # 头发受光的发束（贴在暗线上沿）
    ('hair', 'c', [(59, 8), (52, 11), (46, 14)]),
    ('hair', 'c', [(62, 9), (56, 13), (50, 17), (44, 21)]),
    ('hair', 'c', [(54, 18), (48, 22)]),
    ('hair', 'c', [(51, 26), (46, 29)]),
    ('hair', 'c', [(56, 5), (50, 8)]),
    ('hair', 'c', [(40, 12), (36, 14)]),
    ('hair', 'c', [(37, 21), (33, 23)]),
    # 胸大肌下沿
    ('skin', 'D', [(47, 50), (49, 51), (53, 51), (55, 50)]),
    ('skin', 'D', [(57, 49), (60, 50), (65, 50), (69, 48)]),
    # 腹白线
    ('skin', 'D', [(56, 49), (56, 71)]),
    # 三排腹肌
    ('skin', 'D', [(47, 56), (55, 56)]),
    ('skin', 'D', [(57, 56), (67, 55)]),
    ('skin', 'D', [(46, 62), (55, 62)]),
    ('skin', 'D', [(57, 62), (66, 61)]),
    ('skin', 'D', [(47, 67), (55, 67)]),
    ('skin', 'D', [(57, 67), (65, 66)]),
    # 侧腹（前锯肌）
    ('skin', 'D', [(68, 52), (70, 56)]),
    ('skin', 'D', [(67, 58), (69, 62)]),
    # 近侧三角肌 / 肱二头肌分界
    ('skin', 'D', [(32, 48), (36, 50), (42, 49)]),
    # 远侧小臂 / 拳头
    ('skin', 'D', [(83, 41), (88, 44)]),
    ('skin', 'D', [(76, 60), (82, 62)]),
    # 大腿：股四头肌分界 + 膝盖
    ('skin', 'D', [(43, 81), (42, 87), (40, 92)]),
    ('skin', 'D', [(36, 95), (39, 97), (43, 96)]),
    ('skin', 'D', [(67, 81), (66, 87), (64, 93)]),
    ('skin', 'D', [(60, 96), (63, 98), (67, 97)]),
    # 围巾：两道褶
    ('red', 'R', [(9, 37), (17, 34), (26, 33), (33, 33)]),
    ('red', 'R', [(44, 37), (52, 36), (60, 37)]),
]

# 最后手点的高光（坐标, 字母）
SPECKS = [
    ((36, 41), 'L'), ((37, 41), 'L'), ((36, 42), 'L'),           # 近侧肩头
    ((48, 45), 'L'), ((49, 44), 'L'), ((50, 44), 'L'),           # 近侧胸
    ((58, 45), 'l'), ((59, 44), 'l'),
    ((33, 82), 'L'), ((34, 82), 'L'), ((32, 85), 'L'),           # 近侧大腿
    ((59, 82), 'L'), ((60, 82), 'L'),
    ((66, 38), 'o'), ((67, 38), 'o'), ((68, 39), 'o'),           # 远侧护肩
    ((30, 57), 'o'), ((31, 57), 'o'), ((30, 58), 'o'),           # 近侧护腕
    ((77, 47), 'o'), ((78, 47), 'o'),                            # 远侧护腕
    ((84, 38), 'L'), ((85, 38), 'L'),                            # 拳头
]


def _line(c, pts, ch, mat):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            if MAT.get(c.get(x, y)) == mat:
                c.put(x, y, ch)


def bevel(c, mats=('skin', 'hair'), box=None):
    """光从左上：左 / 上邻是边界（描边、分界线、别的材质、透明）→ 亮一级；右 / 下邻是边界 → 暗一级。"""
    src = [r[:] for r in c.a]

    def boundary(x, y, m):
        ch = src[y][x] if 0 <= x < c.w and 0 <= y < c.h else '.'
        return MAT.get(ch) != m or ch == LINE[m]

    for y in range(c.h):
        for x in range(c.w):
            ch = src[y][x]
            m = MAT.get(ch)
            if m not in mats or ch == LINE[m]:
                continue
            if box and box[0] <= x <= box[2] and box[1] <= y <= box[3]:
                continue
            r = RAMPS[m]
            i = r.index(ch)
            lit = boundary(x - 1, y, m) or boundary(x, y - 1, m)
            shd = boundary(x + 1, y, m) or boundary(x, y + 1, m)
            if lit and not shd:
                i = min(i + 1, len(r) - 1 if m != 'skin' else len(r) - 2)   # 自动只到 l，L 留给手点
            elif shd and not lit:
                i = max(i - 1, 0)
            c.a[y][x] = r[i]


def build():
    fr, _ = frame('starplat')
    c, box = base2x(fr, STARPLAT)
    for y, segs in FACE.items():
        for x0, s in segs:
            for i, ch in enumerate(s):
                if ch != '.':
                    c.put(x0 + i, y, ch)
    for mat, ch, pts in STROKES:
        _line(c, pts, ch, mat)
    bevel(c, box=FACE_BOX)
    for (x, y), ch in SPECKS:
        if c.get(x, y) not in ('.', 'k'):
            c.put(x, y, ch)
    c.outline()
    return c


def check_rows():
    return []
