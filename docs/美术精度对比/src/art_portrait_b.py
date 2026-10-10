"""方案 B：承太郎高清像素立绘（128x128，半身，远侧手压帽檐）。
画法：大块面用手定的多边形（帽顶、帽檐、头发 4 束、脸、耳、脖子、立领、外套、袖子），
五官 / 手指 / 金链 / 帽徽用逐像素补丁，最后按光从左上做受光边 / 背光边，再描外轮廓（底边敞开，接对话框）。
调色板 = palettes.JOTARO + 两级更深的皮肤阴影（帽檐投影用）。"""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
from pixart import Canvas
from palettes import JOTARO
from common import grid_to_img

S = 128
PAL = dict(JOTARO)
PAL.update({
    'T': '#7e4838',   # 新：皮肤最深阴影（帽檐压下来的投影）
    'P': '#4a2c3e',   # 新：投影里最暗的一级（眼窝）
    'g': '#9ff0dc',   # 新：瞳孔里的光（眼睛在阴影里发亮）
})

RAMPS = {
    'navy': ['N', 'n', 'm', 'q', 'Q'],
    'skin': ['P', 'T', 't', 'S', 's', 'w'],
    'shirt': ['J', 'j', 'i'],
    'gold': ['Y', 'y', 'o'],
}
MAT = {ch: m for m, r in RAMPS.items() for ch in r}


def poly(c, pts, ch, only=None):
    m = Image.new('1', (c.w, c.h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=1, outline=1)
    px = m.load()
    for y in range(c.h):
        for x in range(c.w):
            if px[x, y] and (only is None or c.a[y][x] in only):
                c.a[y][x] = ch


def ellipse(c, box, ch, only=None):
    m = Image.new('1', (c.w, c.h), 0)
    ImageDraw.Draw(m).ellipse(box, fill=1, outline=1)
    px = m.load()
    for y in range(c.h):
        for x in range(c.w):
            if px[x, y] and (only is None or c.a[y][x] in only):
                c.a[y][x] = ch


def line(c, pts, ch, only=None, w=1):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            for dy in range(w):
                if 0 <= x < c.w and 0 <= y + dy < c.h and (only is None or c.a[y + dy][x] in only):
                    c.a[y + dy][x] = ch


def bevel(c, mats, lines='k', top_only=False):
    """光从左上：左 / 上邻是边界 → 亮一级；右 / 下邻是边界 → 暗一级。边界 = 描边色、别的材质、透明。"""
    src = [r[:] for r in c.a]

    def bd(x, y, m):
        ch = src[y][x] if 0 <= x < c.w and 0 <= y < c.h else '.'
        return ch in lines or MAT.get(ch) != m

    for y in range(c.h):
        for x in range(c.w):
            ch = src[y][x]
            m = MAT.get(ch)
            if m not in mats:
                continue
            r = RAMPS[m]
            i = r.index(ch)
            lit = bd(x - 1, y, m) or bd(x, y - 1, m)
            shd = bd(x + 1, y, m) or bd(x, y + 1, m)
            if lit and not shd:
                i = min(i + 1, len(r) - 1)
            elif shd and not lit and not top_only:
                i = max(i - 1, 0)
            c.a[y][x] = r[i]


# ------------------------------------------------------------------ 形状（坐标都是手定的）
HAIR = [(34, 30), (22, 31), (8, 37), (1, 41), (13, 46), (5, 54), (3, 58), (16, 60), (9, 69), (8, 73),
        (21, 72), (15, 81), (16, 85), (28, 80), (27, 89), (31, 92), (41, 84), (46, 72), (47, 52), (40, 44)]
CROWN = [(20, 41), (21, 29), (27, 18), (37, 10), (51, 6), (70, 5), (85, 9), (95, 16), (100, 26),
         (102, 37), (101, 46), (64, 49), (34, 47)]
VISOR_TOP = [(58, 47), (100, 43), (114, 43), (121, 46), (116, 50), (98, 52), (64, 52)]
VISOR_UNDER = [(62, 51), (98, 51), (117, 49), (114, 53), (96, 56), (66, 55)]
FACE = [(46, 50), (100, 50), (101, 58), (102, 65), (106, 72), (103, 76), (101, 79), (101, 86), (99, 92),
        (94, 97), (84, 100), (71, 99), (61, 94), (53, 86), (48, 76), (46, 64)]
NECK = [(57, 86), (90, 95), (93, 110), (58, 110)]
COAT = [(0, 113), (12, 105), (38, 98), (58, 108), (98, 112), (112, 103), (127, 106), (127, 127), (0, 127)]
COLLAR_L = [(36, 97), (54, 91), (62, 100), (64, 114), (42, 112), (34, 104)]
COLLAR_F = [(60, 103), (94, 106), (100, 99), (106, 101), (106, 113), (94, 118), (62, 116)]
SHIRT = [(64, 117), (93, 119), (86, 127), (70, 127)]
SLEEVE = [(107, 61), (121, 57), (127, 62), (127, 127), (112, 127), (108, 96)]
CUFF = [(105, 58), (120, 54), (123, 60), (107, 65)]

# 手：四根手指搭在帽檐上（从近到远一节一节），拇指在帽檐下
# 手背在帽檐上方、四根手指弯下来扣住帽檐前沿（一节手背 + 指节 + 指尖）
HAND = r"""
.........kkkkkkkkkkkk.......
.......kkswwssssssssSkk.....
......kswwsssssssssssSSk....
.....kswssssssSsssssSSSSk...
....ksssssSssssSsssssSSStk..
....kssssSksssSksssSkSSStk..
...ksssssSkssSSkssSSkSSttk..
...kSsssSSkSsSSkSsSSkSStk...
...kSSssStkSSStkSSStkStk....
....kSSStk.kSStk.kStkkk.....
.....kkkk...kkk...kkk.......
"""
THUMB = r"""
...kkkkkkk...
..kssssssSk..
.kswssssSSSk.
kSsssssSSStk.
.kSSSSStttk..
..kkkkkkkk...
"""

# 眼睛在帽檐阴影里：上眼皮粗黑线、眼白一窄条、青绿瞳孔带高光、黑瞳仁
EYE_NEAR = r"""
..kkkkkkkkkkkk.
.kkPWWgEEEekkkk
kTPWWEEkkEeePk.
.kTtWWEEEEeTk..
...kttttttttk..
"""
EYE_FAR = r"""
.kkkkkkkkk.
kkWgEEekkkk
kTWEkkEePk.
.kTWEEeTk..
..ktttttk..
"""


def stamp(c, x0, y0, text):
    rows = [r for r in text.strip('\n').split('\n')]
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                c.put(x0 + i, y0 + j, ch)


def build():
    c = Canvas(S, S)
    # 后层：外套肩膀、头发
    poly(c, COAT, 'n')
    poly(c, SHIRT, 'j')
    poly(c, HAIR, 'N')
    # 头发发束：每束上沿亮线、束间暗缝
    for pts, ch in (
        ([(30, 33), (18, 36), (6, 40)], 'm'), ([(31, 34), (19, 37), (8, 41)], 'n'),
        ([(34, 44), (22, 49), (8, 55)], 'm'), ([(34, 45), (22, 50), (9, 56)], 'n'),
        ([(38, 55), (26, 61), (12, 69)], 'm'), ([(38, 56), (26, 62), (13, 70)], 'n'),
        ([(40, 66), (30, 73), (19, 80)], 'm'), ([(40, 67), (30, 74), (20, 81)], 'n'),
        ([(43, 76), (36, 82), (29, 88)], 'm'),
        ([(36, 39), (24, 44), (14, 46)], 'k'), ([(40, 50), (28, 56), (16, 60)], 'k'),
        ([(42, 62), (32, 67), (21, 72)], 'k'), ([(44, 72), (36, 77), (28, 80)], 'k'),
    ):
        line(c, pts, ch, only='Nnm')
    # 脖子、立领
    poly(c, NECK, 't')
    poly(c, COLLAR_L, 'n')
    poly(c, COLLAR_F, 'n')
    line(c, [(37, 98), (54, 92), (61, 101)], 'q', only='n')        # 立领上沿（受光）
    line(c, [(61, 104), (94, 107), (100, 100), (105, 102)], 'm', only='n')
    line(c, [(62, 115), (94, 117)], 'k')                           # 立领下沿
    line(c, [(64, 114), (60, 108), (58, 104)], 'k')
    # 外套：翻领边、肩线、褶
    line(c, [(64, 117), (70, 127)], 'q')
    line(c, [(93, 119), (86, 127)], 'k')
    line(c, [(12, 106), (36, 99)], 'q', only='n')
    line(c, [(6, 110), (30, 103)], 'm', only='n')
    line(c, [(22, 118), (40, 112), (52, 116)], 'N', only='n')
    line(c, [(10, 124), (26, 119)], 'N', only='n')
    # 脸
    poly(c, FACE, 's')
    # 耳朵
    ellipse(c, (44, 62, 55, 81), 's')
    line(c, [(47, 66), (50, 64), (53, 67), (53, 74), (51, 78)], 'S', only='s')
    line(c, [(49, 68), (51, 70), (50, 74)], 't', only='sS')
    line(c, [(44, 66), (44, 77)], 'k')
    # 鬓角：耳朵前面一绺头发
    poly(c, [(46, 50), (58, 50), (56, 58), (52, 64), (47, 63)], 'N')
    line(c, [(48, 52), (55, 52), (52, 60)], 'n', only='N')
    # 帽子
    poly(c, CROWN, 'n')
    poly(c, VISOR_UNDER, 'N')
    poly(c, VISOR_TOP, 'q')
    line(c, [(60, 48), (100, 44), (114, 44), (120, 46)], 'Q', only='q')      # 帽檐前沿高光
    line(c, [(64, 51), (98, 51), (115, 49)], 'm', only='q')                 # 帽檐上面往下变暗
    line(c, [(27, 19), (40, 12), (56, 9), (72, 9), (86, 13), (94, 19)], 'q', only='n')   # 帽顶棱线
    line(c, [(28, 20), (40, 13), (56, 10), (72, 10), (86, 14), (93, 20)], 'm', only='n')
    line(c, [(34, 15), (42, 11)], 'Q', only='qm')
    # 帽子后沿撕开、和头发连在一起
    for x0, y0 in ((22, 34), (26, 40), (31, 44), (37, 47)):
        poly(c, [(x0 - 3, y0 + 4), (x0, y0 - 3), (x0 + 3, y0 + 4)], 'N')
    # 帽徽（金牌）
    poly(c, [(80, 21), (92, 20), (95, 24), (94, 33), (82, 34), (79, 30)], 'y')
    line(c, [(81, 22), (91, 21)], 'o')
    line(c, [(80, 23), (80, 29)], 'o')
    line(c, [(83, 33), (93, 32), (94, 25)], 'Y')
    stamp(c, 84, 24, "..Y..\n.YyY.\nYyoyY\n.YyY.\n..Y..")
    line(c, [(81, 35), (94, 34)], 'N', only='n')
    # 帽檐投影压在脸上（上半张脸进阴影）
    poly(c, [(46, 50), (101, 50), (102, 60), (90, 62), (70, 63), (54, 61), (47, 58)], 'T', only='sS')
    poly(c, [(46, 50), (101, 50), (100, 54), (70, 56), (48, 54)], 'P', only='sST')
    line(c, [(54, 62), (70, 64), (90, 63), (102, 61)], 't', only='s')
    # 眉：粗、压低、往鼻梁斜
    line(c, [(62, 57), (70, 58), (78, 60)], 'k', w=2)
    line(c, [(87, 59), (94, 57), (99, 57)], 'k', w=2)
    # 眼睛
    stamp(c, 62, 59, EYE_NEAR)
    stamp(c, 88, 60, EYE_FAR)
    # 鼻子：右侧一道暗线、鼻尖一点高光、鼻底投影 + 鼻孔
    line(c, [(90, 69), (92, 72), (93, 74)], 'S', only='sw')
    c.put(91, 74, 'w'); c.put(90, 74, 'w'); c.put(89, 73, 'w')
    poly(c, [(86, 76), (94, 75), (96, 77), (89, 78)], 't')
    line(c, [(91, 77), (93, 77)], 'T')
    line(c, [(103, 70), (106, 72), (103, 76)], 'S', only='s')
    # 颧骨高光、脸颊阴影
    line(c, [(64, 70), (68, 70)], 'w', only='s')
    line(c, [(65, 71), (67, 71)], 'w', only='s')
    poly(c, [(54, 74), (62, 78), (66, 90), (60, 92), (53, 85)], 'S', only='s')
    # 嘴：紧闭、嘴角往下
    line(c, [(78, 85), (81, 84), (92, 84), (95, 85)], 'T')
    line(c, [(82, 87), (91, 87)], 'S', only='s')
    line(c, [(84, 89), (89, 89)], 'w', only='s')
    # 下巴 / 下颌线
    line(c, [(62, 94), (72, 99), (84, 100), (94, 97)], 't', only='sS')
    line(c, [(86, 95), (93, 94)], 'S', only='s')
    # 远侧的手（压帽檐）：袖子 + 袖口 + 手腕 + 手指 + 拇指
    poly(c, SLEEVE, 'n')
    line(c, [(104, 70), (112, 96), (116, 127)], 'N', only='n')
    line(c, [(108, 66), (122, 64)], 'N', only='n')
    poly(c, CUFF, 'm')
    line(c, [(99, 60), (117, 55)], 'q')
    poly(c, [(106, 51), (118, 48), (121, 56), (108, 60)], 'S')          # 手腕
    stamp(c, 93, 33, HAND)
    stamp(c, 102, 50, THUMB)
    # 金链：从右边立领往下
    chain = [(101, 104), (100, 107), (99, 110), (98, 113), (98, 116), (99, 119), (100, 122), (101, 125), (102, 127)]
    for i, (x, y) in enumerate(chain):
        c.put(x, y, 'oyYy'[i % 4])
        if i % 2 == 0:
            c.put(x + 1, y, 'Y')
    # 统一受光 / 背光（衣服帽子按材质；脸手已手画，不再自动）
    bevel(c, ('navy', 'shirt'))
    c.outline()
    # 底边敞开（立绘接对话框）
    for x in range(S):
        if c.a[S - 1][x] == 'k' and c.a[S - 2][x] not in '.k':
            c.a[S - 1][x] = c.a[S - 2][x]
    return grid_to_img(c.rows(), PAL)


def check_rows():
    return []
