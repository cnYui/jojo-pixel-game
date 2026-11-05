# 第四部序章的道具：游戏比例直接画（不缩小），格式照第三部 GAME_DATA.props（横向帧条 + size + pivot）。
#   小件用字符图（一个字母一种颜色，外面自动描 1 px 深色边，和第三部道具一样）；岩石、照片这类大件用程序画。
#   用法：python3 第四部/tools/art/p4_props.py      输出 第四部/assets/props/<id>.png + _meta/props.json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
from p4_bglib import C, ellipse, line, mix, px, rect  # noqa: E402

OUT = os.path.join(LIB.ASSETS, 'props')
PREV = os.path.join(LIB.ASSETS, 'preview')


def grid(rows, pal):
    h = len(rows)
    w = max(len(r) for r in rows)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    a = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch not in '. ':
                a[x, y] = LIB.hexc(pal[ch])
    return im


def strip(frames, outline=True, pad=1, align='bottom'):
    """几帧拼成横向帧条：每格一样大，底边对齐、左右居中；outline 时每格单独描边"""
    W = max(f.width for f in frames) + 2 * pad
    H = max(f.height for f in frames) + 2 * pad
    out = Image.new('RGBA', (W * len(frames), H), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        cell = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        y = H - pad - f.height if align == 'bottom' else (H - f.height) // 2
        cell.alpha_composite(f, ((W - f.width) // 2, y))
        if outline:
            cell = LIB.outline(cell)
        out.alpha_composite(cell, (i * W, 0))
    return out, (W, H)


PROPS = {}


def save(pid, frames, pivot=None, fps=1, kind='static', outline=True, align='bottom'):
    im, (w, h) = strip(frames, outline=outline, align=align)
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, pid + '.png'))
    PROPS[pid] = dict(image='props/' + pid, frames=len(frames), size=[w, h], pivot=pivot or [w // 2, h], fps=fps, kind=kind, k=1.0)
    return im


# ---------------------------------------------------------------- 花盆（0 好的，在窗台上；1 摔碎在地上）
POT = dict(R='#ee5a6a', r='#b83448', y='#ffd84a', G='#68b050', g='#3e7c3a', T='#cc6a40', t='#9a4a2c', U='#e8946a',
           s='#5a3a26', S='#7a5236')


def pot():
    ok = grid(["..R....R..",
               ".RyR..RyR.",
               "..r.R..r..",
               "..g.RyR.g.",
               "..gg.r.gg.",
               "...g.g.g..",
               "...ggggg..",
               "UTTTTTTTTt",
               ".tttttttt.",
               ".UTTTTTTt.",
               "..UTTTTt..",
               "..tttttt.."], POT)
    broken = grid(["........R...",
                   ".......RyR..",
                   "..UT...gr...",
                   ".sUTts.g.UTt",
                   "ssTttsssUTt.",
                   ".ssssss.ttt."], POT)
    save('pot', [ok, broken])


# ---------------------------------------------------------------- 加湿器（0 关、1 开、2 打碎）
HUM = dict(W='#f4f2ea', w='#c4bfb2', x='#e2ded2', v='#5a5e68', B='#6aaee0', b='#a8d8f8', g='#4a9a4a', r='#8a8a90', R='#ff5a4a',
           k='#55555c', c='#2a2a30', e='#3a3e48', m='#ffffff')


def humidifier():
    base = ["...xxxxxx...",
            "..xWWWWWWw..",
            "..WvWvWvWw..",
            "..xWWWWWWw..",
            ".xWWWWWWWWw.",
            ".xWBBBBBWWw.",
            ".xWBbbbBWWw.",
            ".xWBbbBBWWw.",
            ".xWBBBBBWWw.",
            ".xWWWWWWWWw.",
            ".xWWgWrWWWw.",
            ".xWWWWWWWWw.",
            ".wwwwwwwwww.",
            "..kk....kk.."]
    on = [r.replace('r', 'R') for r in base]
    on[0] = "..m.xxxxx.m."
    broken = ["............",
              "............",
              "....xx.c....",
              "..xWWWcW.w..",
              ".xWWWWcWWWw.",
              ".xWBBBcBWWw.",
              ".xWBeecBWWw.",
              ".xWBeeecWWw.",
              ".xWBBBBcWWw.",
              ".xWWWWWWcWw.",
              ".xWWgWrWcWw.",
              ".xWWWWWWWWw.",
              ".wwwwwwwwww.",
              "..kk..c.kk.."]
    save('humidifier', [grid(base, HUM), grid(on, HUM), grid(broken, HUM)])


# ---------------------------------------------------------------- 墙上的洞（客厅打墙放汽；不描边，贴在墙上）
def wallhole():
    w, h = 24, 22
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.RandomState(3)
    cx, cy = w / 2, h / 2
    outer, inner = [], []
    for i in range(16):
        a = i / 16 * 2 * math.pi
        r1 = rng.uniform(.82, 1.0)
        r2 = r1 * rng.uniform(.62, .76)
        outer.append((cx + math.cos(a) * 11.5 * r1, cy + math.sin(a) * 10.5 * r1))
        inner.append((cx + math.cos(a) * 11.5 * r2, cy + math.sin(a) * 10.5 * r2))
    d.polygon(outer, fill=C('#cbbd9c'))                      # 碎掉的墙纸边
    d.polygon([(x + .6, y + .8) for x, y in outer], fill=C('#b8a682'))
    d.polygon(inner, fill=C('#3a3a48'))                      # 墙里面
    ins = [(cx + (x - cx) * .78, cy + (y - cy) * .78 + 1) for x, y in inner]
    d.polygon(ins, fill=C('#6e7a8c'))                         # 洞外面：雨天的灰蓝
    for x in (cx - 4, cx + 3):                                # 露出来的木条
        line(d, (x, cy - 8, x, cy + 8), '#7a5a3c')
    a = np.array(im)
    msk = (a[..., 0] == 0x6e) & (a[..., 1] == 0x7a) & (a[..., 3] > 0)
    ys, xs = np.where(msk)
    for x, y in zip(xs, ys):                                  # 飘进来的雨丝
        if (x * 7 + y * 3) % 11 == 0:
            a[y, x] = (200, 212, 228, 255)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    for x, y in outer[::3]:                                   # 几块翘起来的墙纸
        px(d, x, y, '#eadfc6')
    save('wallhole', [im], pivot=[w // 2, h // 2], outline=False, align='center')


# ---------------------------------------------------------------- 乳胶手套盒（0 有手套、1 拿走了）+ 手套图标（头像旁）
GLV = dict(P='#f2f2f6', p='#c4c4cc', L='#4a8ad8', Y='#f6eca8', y='#d8c878', w='#fffbe0', k='#6a6a74')


def gloves():
    full = grid(["...Yy....",
                 "..YYYy...",
                 "PPPPPPPPp",
                 "PLLLLLLLp",
                 "PPPPPPPPp",
                 "PPPPPPPPp",
                 "ppppppppp"], GLV)
    empty = grid([".........",
                  ".........",
                  "PkkkkkkPp",
                  "PLLLLLLLp",
                  "PPPPPPPPp",
                  "PPPPPPPPp",
                  "ppppppppp"], GLV)
    save('glovebox', [full, empty])
    icon = grid([".w.w.w.w...",
                 ".Y.Y.Y.Y...",
                 ".Y.Y.Y.Y...",
                 ".YYYYYYY...",
                 ".YYYYYYY.w.",
                 ".wYYYYYYYY.",
                 ".YYYYYYYy..",
                 "..YYYYYy...",
                 "..YYYYY....",
                 "..yyyyy....",
                 "..YYYYY....",
                 "..YYYYY...."], GLV)
    save('glove_icon', [icon], align='center', pivot=None)


# ---------------------------------------------------------------- 牛奶瓶（0 普通；1 里面有东西在游）
MILK = dict(c='#e8484a', C='#f4f0e6', g='#a8bcc8', G='#d4e2ea', M='#f8f6ee', H='#ffffff', a='#bcd8ec', e='#4a7a9a')


def milk():
    f0 = ["..CC..",
          ".cCCc.",
          "..GG..",
          ".gMMg.",
          "gMMMMg",
          "gHMMMg",
          "gHMMMg",
          "gMMMMg",
          "gMMMMg",
          "gMMMMg",
          ".gggg."]
    f1 = ["..CC..",
          ".cCCc.",
          "..GG..",
          ".gaag.",
          "gMaaMg",
          "gHeaeg",
          "gHaaMg",
          "gMMaMg",
          "gMMMMg",
          "gMMMMg",
          ".gggg."]
    save('milk', [grid(f0, MILK), grid(f1, MILK)])


# ---------------------------------------------------------------- 警帽（良平）
CAP = dict(N='#2e3e68', n='#1e2a4a', h='#4a5e90', y='#f0c840', k='#16161c', K='#3a3a44')


def cap():
    save('cap', [grid(["..hhhhhh..",
                       ".hNNNNNNN.",
                       ".NNNNyNNNn",
                       ".nnnnnnnnn",
                       "kkkkkkkk..",
                       ".KKKK....."], CAP)])


# ---------------------------------------------------------------- 小学生的黄伞（把手底下是 pivot）
UMB = dict(Y='#ffd23a', y='#e0a820', w='#fff2a0', k='#7a6a4a', r='#d86a2a', o='#c88a18')


def umbrella():
    rows = [".........r.........",
            ".......YYYYY.......",
            ".....YwwYYYYYy.....",
            "...YwwYYYYYYYYyy...",
            "..YwYYYYYYYYYYYyy..",
            ".YwYYYYYYYYYYYYYyy.",
            "YYYYYYYYYYYYYYYYYyy",
            "oYo.oYYo.k.oYYo.oyo",
            ".........k.........",
            ".........k.........",
            ".........k.........",
            ".........k.........",
            ".........k.........",
            ".........k.........",
            ".......k.k.........",
            "........k.........."]
    save('umbrella', [grid(rows, UMB)], pivot=None)


# ---------------------------------------------------------------- 垃圾桶（0 立着；1 被踢翻、垃圾撒出来）
TR = dict(B='#4a7ab8', b='#345a8a', L='#7aa4d8', k='#2a2a34', p='#e8e4d8', o='#d88a3a', g='#6a9a5a', w='#f4f4f4')


def trash():
    up = grid(["LLLLLLLLLL",
               "BBBBBBBBBb",
               ".bbbbbbbb.",
               ".LBBBBBBb.",
               ".LBwwwBBb.",
               ".LBBBBBBb.",
               ".LBBBBBBb.",
               ".LBBBBBBb.",
               ".LBBBBBBb.",
               ".LBBBBBBb.",
               ".LBBBBBBb.",
               ".bbbbbbbb."], TR)
    down = grid(["..............p.",
                 ".LLLLLLLLb..o...",
                 "LBBBBBBBBbb.p.g.",
                 "LBwwwBBBBbkpp...",
                 "LBBBBBBBBbkkop..",
                 "bbbbbbbbbbb.p.g.",
                 ".bbbbbbbbb......"], TR)
    save('trash', [up, down])


# ---------------------------------------------------------------- 自行车（0 立着；1 倒在地上）、警用自行车（良平推着）
def bike_img(frame_col, light=False, box=False, basket=True):
    w, h = 26, 16
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for wx in (5, 20):                                        # 车轮
        ellipse(d, (wx - 5, h - 11, wx + 5, h - 1), '#2a2a30')
        ellipse(d, (wx - 4, h - 10, wx + 4, h - 2), (0, 0, 0, 0))
        for k in range(4):
            a = k * math.pi / 4
            line(d, (wx - math.cos(a) * 3.5, h - 6 - math.sin(a) * 3.5, wx + math.cos(a) * 3.5, h - 6 + math.sin(a) * 3.5), '#b8b8c0')
        px(d, wx, h - 6, '#5a5a60')
    fc, fc2 = frame_col, mix(frame_col, '#000000', .3)
    line(d, (5, h - 6, 11, h - 6), fc)                        # 车架
    line(d, (11, h - 6, 9, h - 12), fc)
    line(d, (9, h - 11, 17, h - 11), fc)
    line(d, (11, h - 6, 17, h - 11), fc2)
    line(d, (17, h - 11, 20, h - 6), fc)
    line(d, (5, h - 6, 9, h - 11), fc2)
    rect(d, (7, h - 14, 11, h - 13), '#2a2a30')               # 座
    line(d, (17, h - 11, 18, h - 14), '#8a8a90')              # 车把
    line(d, (17, h - 14, 21, h - 14), '#8a8a90')
    if basket:
        rect(d, (19, h - 13, 24, h - 9), '#c8ccd2')
        line(d, (19, h - 11, 24, h - 11), '#8a8e96')
    if box:
        rect(d, (0, h - 16, 6, h - 11), '#f4f4f0')
        line(d, (0, h - 11, 6, h - 11), '#a8a8a0')
    if light:
        rect(d, (24, h - 10, 25, h - 9), '#fff4a0')
    return im


def bike_fallen(frame_col):
    w, h = 26, 9
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for wx in (6, 19):
        ellipse(d, (wx - 6, h - 5, wx + 6, h - 1), '#2a2a30')
        ellipse(d, (wx - 4, h - 4, wx + 4, h - 2), '#6a6a70')
    line(d, (6, h - 4, 19, h - 4), frame_col)
    line(d, (9, h - 4, 12, h - 7), mix(frame_col, '#000000', .3))
    rect(d, (10, h - 8, 13, h - 7), '#2a2a30')
    line(d, (19, h - 4, 22, h - 8), '#8a8a90')
    rect(d, (21, h - 9, 24, h - 7), '#c8ccd2')
    return im


def bikes():
    save('bike', [bike_img('#3a6ab8'), bike_fallen('#3a6ab8')])
    save('police_bike', [bike_img('#e8e8ec', light=True, box=True, basket=False)])


# ---------------------------------------------------------------- 路边的大岩石（0 普通；1 安杰罗岩：隐约一张脸）
def rock_img(face):
    w, h = 40, 28
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(1, 27), (2, 18), (6, 10), (12, 5), (20, 2), (28, 4), (34, 9), (38, 17), (39, 27)]
    d.polygon(pts, fill=C('#7a7468'))
    d.polygon([(4, 18), (8, 11), (13, 6), (20, 3), (27, 5), (22, 9), (15, 12), (9, 17)], fill=C('#9a9486'))
    d.polygon([(10, 10), (15, 6), (21, 4), (18, 7)], fill=C('#b8b2a2'))
    d.polygon([(28, 6), (34, 10), (37, 18), (38, 26), (30, 26), (32, 16)], fill=C('#625d54'))
    line(d, (1, 27, 39, 27), '#4e4a42')
    for x0, y0, x1, y1 in ((14, 14, 18, 22), (26, 9, 24, 15), (30, 18, 35, 24)):
        line(d, (x0, y0, x1, y1), '#5a554c')
    for x, y in ((5, 24), (7, 25), (33, 25), (36, 24), (22, 26)):           # 青苔
        px(d, x, y, '#6a7a4a')
        px(d, x + 1, y, '#7a8a5a')
    if face:
        # 很淡：闭着的眼睛、鼻梁、嘴角往下一道（不画表情细节）
        for ex in (14, 23):
            line(d, (ex, 12, ex + 3, 13), '#5e594f')
            px(d, ex + 1, 11, '#8a8478')
        line(d, (19, 13, 20, 17), '#6a655a')
        px(d, 21, 17, '#5e594f')
        line(d, (16, 20, 23, 20), '#5a554c')
        px(d, 15, 21, '#5a554c')
        px(d, 24, 21, '#5a554c')
        line(d, (12, 9, 16, 9), '#6a655a')
        line(d, (22, 9, 26, 9), '#6a655a')
    return LIB.outline(im, color=LIB.hexc('#2a2622'))


def rocks():
    save('rock', [rock_img(False), rock_img(True)], outline=False)


# ---------------------------------------------------------------- 劫匪的喜剧刀（0 整把；1 只剩刀柄：修进额头像一只角）
KN = dict(S='#e8eef4', s='#a8b4c0', H='#ffffff', h='#8a4a2a', d='#5a2e1a', y='#e8c060')


def knife():
    full = grid(["..........y...",
                 "HHSSSSSSSsyhhh",
                 ".sSSSSSSSsyhdd",
                 "..ssssssssy..."], KN)
    horn = grid([".h.",
                 "hhd",
                 "hhd",
                 "hhd",
                 "yyy"], KN)
    save('knife', [full, horn])


# ---------------------------------------------------------------- 承太郎的拍立得：安杰罗 + 身边一团有脸的水（3 帧：显影中）
def photo():
    w, h = 40, 48
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, w, h), '#5e636e')                          # 背景：小巷的墙
    for y in range(0, h, 6):
        line(d, (0, y, w, y), '#565a64')
    rect(d, (0, 34, w, h), '#4a4e58')
    line(d, (0, 34, w, 34), '#6a707c')
    # 安杰罗（半身，左边）：往后梳的金褐头发、发尖在额头中间、细眼、嘴角咧开
    rect(d, (4, 34, 26, h), '#2e2e36')                        # 深色上衣
    d.polygon([(10, 34), (15, 40), (20, 34)], fill=C('#e8e4dc'))
    line(d, (15, 36, 15, h), '#1e1e24')
    rect(d, (11, 27, 19, 34), '#e2c2a2')                      # 脖子
    ellipse(d, (7, 10, 23, 30), '#ecccaa')                    # 脸
    d.polygon([(6, 18), (7, 9), (12, 5), (18, 5), (23, 9), (24, 18), (21, 12), (15, 15), (9, 12)], fill=C('#c8a060'))
    d.polygon([(9, 12), (15, 15), (21, 12), (15, 11)], fill=C('#c8a060'))
    line(d, (8, 9, 14, 6), '#e0bc78')
    line(d, (16, 6, 21, 8), '#e0bc78')
    line(d, (10, 19, 13, 19), '#2a2020')                      # 细眼
    line(d, (17, 19, 20, 18), '#2a2020')
    line(d, (10, 17, 13, 18), '#8a6a3a')
    line(d, (17, 17, 20, 16), '#8a6a3a')
    line(d, (15, 20, 15, 23), '#c8a080')
    line(d, (12, 25, 18, 25), '#7a3a3a')                      # 咧嘴
    px(d, 18, 24, '#7a3a3a')
    px(d, 19, 23, '#7a3a3a')
    # 眉毛往中间压下来：看着就不是好人
    line(d, (9, 16, 13, 17), '#6a4a2a')
    line(d, (17, 17, 21, 15), '#6a4a2a')
    px(d, 11, 20, '#c8a080')
    px(d, 19, 20, '#c8a080')
    # 右边：一团不规则的水（往下滴），水里隐约一张脸：斜着的细眼、咧开的嘴
    blob = [(26, 18), (27, 13), (30, 10), (34, 11), (37, 15), (38, 21), (37, 27), (35, 30), (33, 29), (31, 31), (29, 29), (27, 27)]
    d.polygon(blob, fill=C('#4a8ac0'))
    d.polygon([(x + (1 if x < 32 else -1), y + (1 if y < 20 else -1)) for x, y in blob], fill=C('#6ab4e0'))
    d.polygon([(28, 14), (31, 11), (34, 12), (31, 14), (29, 17)], fill=C('#a8dcf8'))
    px(d, 30, 12, '#ffffff')
    for x0, y0, x1, y1 in ((28, 19, 31, 21), (36, 19, 33, 21)):
        line(d, (x0, y0, x1, y1), '#1e4a78')
    line(d, (28, 24, 36, 24), '#1e4a78')
    line(d, (29, 25, 35, 25), '#1e4a78')
    for k in range(4):
        px(d, 29 + k * 2, 24, '#e8f6ff')
    px(d, 27, 23, '#1e4a78')
    px(d, 37, 23, '#1e4a78')
    for x, y in ((31, 32), (31, 33), (35, 31), (26, 30), (38, 9)):
        px(d, x, y, '#6ab4e0')
    full = im
    # 显影：先几乎全暗，再一半
    dark = Image.new('RGBA', (w, h), C('#2e2a2a'))
    f0 = Image.blend(dark, full, .12)
    f1 = Image.blend(dark, full, .5)
    save('photo', [f0, f1, full], outline=False, pivot=[w // 2, h // 2])


# ---------------------------------------------------------------- 超市清单的小图标：酱油、豆腐、洗洁精、零食
ITM = dict(k='#3a2a22', K='#5a3a2a', r='#d84a3a', w='#f4f0e6', W='#ffffff', c='#e8e2d0', g='#58b068', G='#3a8a4a', b='#4a90d8',
           B='#2a6ab0', y='#f0c040', Y='#ffe080', o='#e07a2a', p='#e85a8a', s='#c8ccd2')


def items():
    soy = grid([".rr.",
                ".kk.",
                "kKKk",
                "kwwk",
                "kwrk",
                "kwwk",
                "kKKk",
                "kKKk",
                ".kk."], ITM)
    tofu = grid(["......",
                 "ssssss",
                 "sWWWWs",
                 "sWccWs",
                 "sWWWWs",
                 "bbbbbb"], ITM)
    soap = grid([".gg..",
                 ".G...",
                 "gggg.",
                 "gWWg.",
                 "gWgg.",
                 "gggg.",
                 "gGGg.",
                 "gggg."], ITM)
    snack = grid(["ssssss",
                  "pppppp",
                  "pyYypp",
                  "pYoYpp",
                  "pyYypp",
                  "pppppp",
                  "ssssss"], ITM)
    for pid, im in (('item_soy', soy), ('item_tofu', tofu), ('item_soap', soap), ('item_snack', snack)):
        save(pid, [im], align='center')


def preview_all():
    ims = []
    for pid in PROPS:
        ims.append(Image.open(os.path.join(OUT, pid + '.png')).convert('RGBA'))
    W = sum(i.width for i in ims) + 6 * len(ims) + 6
    H = max(i.height for i in ims) + 12
    can = Image.new('RGBA', (W, H), (120, 136, 156, 255))
    x = 6
    for im in ims:
        can.alpha_composite(im, (x, 6))
        x += im.width + 6
    os.makedirs(PREV, exist_ok=True)
    can.resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(PREV, 'props.png'))


def main():
    for f in (pot, humidifier, wallhole, gloves, milk, cap, umbrella, trash, bikes, rocks, knife, photo, items):
        f()
    path = os.path.join(LIB.META, 'props.json')
    meta = LIB.load_json(path, {}) or {}
    meta.setdefault('props', {}).update(PROPS)
    meta.setdefault('scene', {})
    LIB.save_json(path, meta)
    preview_all()
    print('道具', len(PROPS), '个：', ' '.join(PROPS))


if __name__ == '__main__':
    main()
