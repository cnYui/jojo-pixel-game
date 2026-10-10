"""M1 新道具：只使用整数像素，状态帧由剧情选择，不自动播放。"""
import sys
sys.dont_write_bytecode = True

from PIL import Image, ImageDraw
import art_common as AC
from engine import bg_asia as A

K = AC.OUTLINE_RGB


def spec(pid, frames, w, h, desc):
    return dict(id=pid, frames=frames, size=[w, h], pivot=[w // 2, h],
                fps=0, kind='static', desc=desc)


PROPS = [
    spec('magazine', 1, 10, 7, '漫画周刊，保留独立名字供序章调查'),
    spec('jail_pipe', 2, 16, 48, '完好的水管与阀门 / 管口爆开；水流由像素特效叠加'),
    spec('tissue', 1, 10, 8, '花京院递出的皱纸巾'),
    spec('pen', 1, 9, 3, '校医使用的钢笔'),
    spec('pinky', 1, 4, 5, '乔瑟夫皮手套色义手小指'),
    spec('hk_table', 2, 48, 20, '圆桌与四凳 / 桌面时钟；火焰由像素特效叠加'),
    spec('mr_statue', 3, 24, 40, '虎像 / 红色魔术师像 / 碎石；虎像从原画等比缩至24像素宽'),
    spec('chariot_armor', 4, 8, 8, '肩甲 / 胸甲 / 头盔 / 护腿'),
    spec('dish', 3, 8, 5, '青蛙 / 整鱼 / 不明食物'),
    spec('kite', 1, 8, 8, '香港街头的小风筝'),
]


def canvas(w, h):
    im = Image.new('RGBA', (w, h))
    return im, ImageDraw.Draw(im)


def draw_magazine(frame):
    im, d = canvas(10, 7)
    d.rectangle((0, 0, 9, 6), fill=(248, 230, 176), outline=K)
    d.rectangle((2, 1, 8, 2), fill=(204, 48, 66))
    d.rectangle((3, 3, 6, 5), fill=(60, 108, 156))
    d.line((1, 1, 1, 5), fill=(164, 132, 100))
    d.point((7, 4), fill=(250, 244, 210))
    return im


def draw_jail_pipe(frame):
    im, d = canvas(16, 48)
    d.rectangle((6, 1, 10, 47), fill=(104, 122, 136), outline=K)
    d.line((7, 2, 7, 46), fill=(192, 202, 204))
    for y in (8, 36):
        d.rectangle((4, y, 12, y + 3), fill=(132, 144, 152), outline=K)
        d.line((5, y + 1, 11, y + 1), fill=(210, 212, 208))
    d.line((9, 22, 13, 22), fill=(140, 148, 154), width=2)
    d.ellipse((10, 18, 15, 25), fill=(136, 52, 54), outline=K)
    d.line((12, 19, 12, 24), fill=(204, 84, 70))
    d.line((11, 21, 14, 21), fill=(204, 84, 70))
    if frame == 1:
        d.rectangle((5, 11, 11, 17), fill=(0, 0, 0, 0))
        d.polygon([(5, 11), (2, 9), (4, 15), (7, 17), (8, 14)], fill=(164, 182, 192), outline=K)
        d.polygon([(9, 14), (13, 11), (14, 15), (10, 18), (8, 17)], fill=(136, 158, 172), outline=K)
        d.line((6, 17, 10, 17), fill=(26, 36, 48))
    return im


def draw_tissue(frame):
    im, d = canvas(10, 8)
    d.polygon([(1, 1), (5, 0), (8, 2), (9, 6), (6, 7), (3, 6), (0, 4)],
              fill=(244, 244, 236), outline=(136, 144, 160))
    d.line((2, 2, 4, 4, 2, 5), fill=(190, 196, 210))
    d.line((6, 2, 5, 5, 7, 6), fill=(204, 208, 220))
    return im


def draw_pen(frame):
    im, d = canvas(9, 3)
    d.line((0, 1, 7, 1), fill=K, width=3)
    d.line((2, 0, 6, 0), fill=(72, 82, 114))
    d.point((1, 0), fill=(238, 200, 104))
    d.point((8, 1), fill=(220, 210, 168))
    return im


def draw_pinky(frame):
    im, d = canvas(4, 5)
    d.rounded_rectangle((0, 0, 3, 4), radius=1, fill=(158, 112, 68), outline=K)
    d.line((1, 1, 1, 3), fill=(212, 166, 110))
    d.point((2, 3), fill=(98, 64, 50))
    return im


def draw_hk_table(frame):
    im, d = canvas(48, 20)
    for x, y in ((2, 8), (36, 8), (8, 14), (31, 14)):
        d.rectangle((x + 1, y + 2, x + 2, 19), fill=(122, 36, 40), outline=K)
        d.rectangle((x + 6, y + 2, x + 7, 19), fill=(122, 36, 40), outline=K)
        d.ellipse((x, y, x + 9, y + 4), fill=(222, 74, 62), outline=K)
        d.line((x + 2, y + 1, x + 6, y + 1), fill=(248, 118, 84))
    d.rectangle((20, 6, 27, 18), fill=(112, 102, 94), outline=K)
    d.ellipse((14, 16, 32, 19), fill=(90, 86, 88), outline=K)
    d.ellipse((6, 0, 41, 11), fill=(220, 216, 192), outline=K)
    d.arc((8, 1, 39, 9), 185, 350, fill=(250, 246, 220))
    if frame:
        import math
        d.ellipse((9, 1, 38, 10), fill=(126, 84, 58), outline=(62, 44, 46))
        for i in range(12):
            a = i * math.tau / 12
            x, y = round(23.5 + math.sin(a) * 12), round(5.5 - math.cos(a) * 3.5)
            d.point((x, y), fill=(248, 166, 66))
        d.line((23, 6, 23, 2), fill=(250, 224, 154))
        d.line((23, 6, 32, 7), fill=(250, 224, 154))
        d.point((23, 6), fill=K)
    return im


def draw_mr_statue(frame):
    im, d = canvas(24, 40)
    stone, dark = (166, 136, 110), (84, 70, 70)
    if frame == 0:
        original = Image.new('RGBA', (57, 45))
        A._tiger_statue(ImageDraw.Draw(original), 26, 44)
        # 原虎像宽57px；等比缩小保留全身轮廓，不裁掉头尾。
        fitted = original.resize((24, 19), Image.Resampling.NEAREST)
        im.alpha_composite(fitted, (0, 21))
    elif frame == 1:
        d.polygon([(2, 39), (4, 33), (19, 33), (22, 39)], fill=stone, outline=K)
        d.polygon([(7, 33), (7, 21), (4, 17), (6, 13), (10, 15), (17, 14), (20, 19), (17, 24), (17, 33)],
                  fill=(180, 70, 50), outline=K)
        d.rectangle((8, 24, 10, 34), fill=(206, 106, 68), outline=K)
        d.rectangle((14, 24, 17, 34), fill=(150, 58, 48), outline=K)
        d.polygon([(7, 15), (8, 8), (11, 3), (17, 2), (20, 7), (18, 12), (15, 15)],
                  fill=(220, 108, 60), outline=K)
        d.polygon([(16, 5), (22, 7), (18, 9), (18, 12), (13, 12)], fill=(238, 194, 100), outline=K)
        d.line((9, 5, 12, 2, 17, 1), fill=(244, 176, 86), width=2)
        d.point((17, 5), fill=(250, 238, 166))
        d.line((8, 17, 7, 23), fill=(238, 152, 82), width=2)
        d.line((17, 18, 19, 22), fill=(112, 44, 44), width=2)
        d.line((11, 17, 14, 21), fill=(242, 188, 112))
    else:
        for points, col in [([(1,39),(3,34),(9,37),(8,39)], stone),
                            ([(11,39),(10,32),(14,30),(17,37)], (190,84,58)),
                            ([(17,39),(19,34),(23,36),(22,39)], dark),
                            ([(5,32),(6,27),(11,28),(9,33)], (212,120,72)),
                            ([(16,29),(18,26),(21,29),(18,32)], stone)]:
            d.polygon(points, fill=col, outline=K)
        d.point((2, 31), fill=dark)
        d.point((14, 36), fill=(240, 166, 100))
    return im


def draw_chariot_armor(frame):
    im, d = canvas(8, 8)
    silver, shade, hi = (168, 182, 202), (92, 110, 140), (236, 240, 246)
    shapes = [[(0,4),(2,1),(5,0),(7,3),(6,6),(2,7)],
              [(1,0),(6,0),(7,4),(5,7),(2,7),(0,4)],
              [(1,5),(1,2),(3,0),(5,0),(7,3),(6,6),(3,7)],
              [(2,0),(5,0),(5,4),(7,6),(6,7),(1,7),(1,5)]]
    d.polygon(shapes[frame], fill=silver, outline=K)
    d.line((2, 2, 5, 2), fill=hi)
    d.line((5, 3, 5, 5), fill=shade)
    if frame == 2:
        d.line((2, 4, 6, 4), fill=K)
    elif frame == 1:
        d.line((3, 3, 4, 6), fill=hi)
    return im


def draw_dish(frame):
    im, d = canvas(8, 5)
    d.ellipse((0, 2, 7, 4), fill=(238, 232, 212), outline=(110, 112, 130))
    if frame == 0:
        d.ellipse((2, 1, 5, 3), fill=(100, 144, 58), outline=K)
        d.point((2, 0), fill=(140, 184, 80))
        d.point((5, 0), fill=(140, 184, 80))
    elif frame == 1:
        d.ellipse((1, 1, 5, 3), fill=(110, 154, 174), outline=K)
        d.polygon([(5,2),(7,0),(7,3)], fill=(108, 144, 162))
        d.point((2, 2), fill=(244, 234, 200))
    else:
        d.polygon([(1,2),(2,0),(4,1),(5,0),(6,3),(3,3)], fill=(158, 100, 56), outline=K)
        d.point((3, 1), fill=(218, 164, 78))
    return im


def draw_kite(frame):
    im, d = canvas(8, 8)
    d.polygon([(3,0),(6,3),(3,6),(0,3)], fill=(220, 66, 72), outline=K)
    d.polygon([(3,1),(5,3),(3,5)], fill=(246, 194, 72))
    d.line((1,3,5,3), fill=(244, 226, 166))
    d.line((3,1,3,5), fill=(244, 226, 166))
    d.line((3,6,4,7,6,7), fill=(140, 160, 194))
    return im


import art_props_later
PROPS += art_props_later.install(globals(), spec)
