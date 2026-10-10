r"""保健室（2026-10-10 主代理重画；旧版在 _旧稿\school_infirmary_20261010前.py）。

用户：“医务室的这个门，你也没有做”——门原来被画面右边切掉一半。现在：
  右边一扇完整的推拉门（门框、上导轨、磨砂玻璃窗、凹把手、踢脚板）+ 门上「保健室」门牌；
  门是 pick 层（key 'door'：0 关 / 1 开，开的时候门板滑出画面右边、露出走廊）。
  桌子、药柜往左挪给门让位；墙上加视力表、急救海报、挂钟；桌上文件夹、急救箱、台灯；桌下圆凳、门口地垫。
床、窗、布帘的位置和旧版一样（剧情坐标：床 100 / 180、窗 180、布帘 48、校医 230、药柜 263、门 299）。
花瓣（窗外）和台灯呼吸 4 秒闭合。
"""
import sys
sys.dont_write_bytecode = True

import math
import os
from functools import lru_cache

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from engine import bg_asia as A, bg_egypt as E

W, H = 320, 180
N, FPS = 32, 8
WINDOW = (153, 43, 208, 88)
LAMP = (213, 94, 255, 151)
DOOR_BOX = (280, 44, 320, 152)
C = A._c4
FONT = r'C:\Windows\Fonts\simsun.ttc'


def rect(d, box, fill, outline=None, width=1):
    d.rectangle(box, fill=C(fill) if fill else None, outline=C(outline) if outline else None, width=width)


def line(d, pts, fill, width=1):
    d.line(pts, fill=C(fill), width=width)


def px(d, x, y, fill):
    d.point((x, y), fill=C(fill))


def bed(d, x0, x1):
    d.rectangle((x0 + 5, 142, x0 + 7, 151), fill=C((102, 112, 126)))
    d.rectangle((x1 - 7, 142, x1 - 5, 151), fill=C((102, 112, 126)))
    d.rectangle((x0, 133, x1, 143), fill=C((186, 194, 198)), outline=C((100, 112, 126)))
    d.polygon([(x0 + 2, 130), (x1 - 4, 130), (x1 - 1, 140), (x0 + 2, 140)], fill=C((246, 246, 240)), outline=C((158, 168, 184)))
    d.line((x0 + 5, 132, x1 - 7, 132), fill=C((255, 255, 250)))
    for x in range(x0 + 18, x1 - 7, 12):
        d.line((x, 134, x + 1, 138), fill=C((218, 226, 232)))
    d.rounded_rectangle((x0 + 3, 129, x0 + 17, 135), radius=2, fill=C((140, 178, 218)), outline=C((86, 120, 166)))
    d.line((x0 + 5, 130, x0 + 15, 130), fill=C((180, 208, 236)))
    d.line((x0, 126, x0, 147), fill=C((128, 142, 154)), width=2)
    d.line((x1, 129, x1, 147), fill=C((128, 142, 154)), width=2)
    d.line((x0 + 1, 126, x0 + 1, 132), fill=C((176, 188, 198)))
    # 床脚的小轮子
    for x in (x0 + 6, x1 - 6):
        d.ellipse((x - 2, 150, x + 1, 152), fill=C((60, 66, 76)))


def room(im):
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, W, 10), (226, 226, 214))                       # 天花板一线 + 顶角线
    line(d, (0, 10, W, 10), (196, 196, 186))
    line(d, (0, 11, W, 11), (250, 250, 242))
    rect(d, (0, 120, W, 140), (182, 208, 186))                    # 墙裙
    line(d, (0, 120, W, 120), (116, 152, 138))
    line(d, (0, 121, W, 121), (206, 226, 210))
    rect(d, (0, 138, W, 140), (150, 176, 158))                    # 踢脚线
    rect(d, (0, 141, W, H), (200, 204, 202))                      # 地面
    for y in (146, 155, 166, 179):
        line(d, (0, y, W, y), (172, 180, 182))
    for row, (ya, yb) in enumerate(((141, 146), (146, 155), (155, 166), (166, 180))):
        for x in range(-20 + row * 9, W, 40):
            line(d, (x, ya, x + 2, yb), (180, 186, 188))
    A._tex_noise(im, (0, 12, W, 140), 0.04, 79)
    d = ImageDraw.Draw(im)
    # 窗下地面的一块亮光
    A._blend_poly(im, [(152, 141), (210, 141), (222, 160), (148, 160)], (255, 250, 230), 26)
    return ImageDraw.Draw(im)


def wall_items(im):
    d = ImageDraw.Draw(im)
    # 窗：窗外是校门那边的樱花
    far, near = A._school_layers()
    outside = far.copy()
    outside.alpha_composite(near.crop((0, 0, 400, 180)))
    view = outside.crop((112, 28, 182, 92)).resize((55, 45), Image.Resampling.NEAREST)
    im.alpha_composite(view, (153, 43))
    d = ImageDraw.Draw(im)
    rect(d, (150, 40, 210, 90), None, (92, 112, 126), 3)
    line(d, (180, 42, 180, 88), (226, 230, 222), 2)
    line(d, (152, 68, 208, 68), (226, 230, 222), 2)
    rect(d, (148, 90, 212, 93), (182, 190, 184), (130, 144, 144))
    line(d, (149, 90, 211, 90), (226, 232, 226))
    # 布帘（轨道 + 褶子）
    rect(d, (20, 20, 64, 150), (240, 242, 232), (172, 184, 188))
    line(d, (18, 19, 68, 19), (104, 120, 134), 2)
    for x in range(23, 65, 7):
        line(d, (x, 22, x, 147), (208, 216, 212))
        line(d, (x + 2, 23, x + 2, 145), (252, 252, 240))
        rect(d, (x, 18, x + 2, 21), (114, 130, 146))
    line(d, (21, 146, 63, 146), (214, 220, 216))
    # 视力表（白底、一行行 C 字越来越小）
    rect(d, (84, 30, 101, 74), (250, 250, 246), (150, 156, 160))
    line(d, (86, 32, 99, 32), (210, 60, 60))
    rows = ((36, 5, 1), (44, 4, 2), (51, 3, 3), (57, 2, 4), (62, 2, 4), (67, 1, 5))
    for y, s, n in rows:
        gap = (14 - n * s) // (n + 1) if n > 1 else (14 - s) // 2
        x = 86 + gap
        for i in range(n):
            if s >= 3:
                d.rectangle((x, y, x + s - 1, y + s - 1), outline=C((30, 30, 36)))
                px(d, x + s - 1 if i % 2 == 0 else x, y + s // 2, (250, 250, 246))
            else:
                rect(d, (x, y, x + s - 1, y + s - 1), (30, 30, 36))
            x += s + gap
    # 急救海报（绿十字 + 几行字）
    rect(d, (106, 40, 124, 64), (244, 246, 236), (150, 160, 150))
    rect(d, (113, 43, 117, 53), (60, 160, 90))
    rect(d, (110, 46, 120, 50), (60, 160, 90))
    for y in (56, 59, 62):
        line(d, (109, y, 121 - (y % 3), y), (120, 130, 124))
    for (x, y) in ((106, 40), (124, 40)):
        px(d, x, y, (200, 60, 60))
    # 挂钟
    d.ellipse((221, 39, 235, 53), fill=C((250, 250, 244)), outline=C((60, 64, 70)))
    d.ellipse((222, 40, 234, 52), outline=C((180, 184, 190)))
    for a in range(12):
        ang = a * math.tau / 12
        px(d, round(228 + 5 * math.sin(ang)), round(46 - 5 * math.cos(ang)), (90, 94, 100))
    line(d, (228, 46, 228, 42), (30, 30, 36))
    line(d, (228, 46, 231, 47), (30, 30, 36))
    px(d, 228, 46, (200, 50, 50))
    return d


def desk_and_cabinet(im):
    d = ImageDraw.Draw(im)
    wood, dark, hi = (182, 140, 100), (102, 86, 80), (210, 172, 128)
    # 桌下的圆凳（在桌子后面）
    d.ellipse((216, 136, 230, 140), fill=C((70, 110, 150)), outline=C((44, 70, 100)))
    line(d, (223, 140, 223, 150), (120, 126, 134), 2)
    line(d, (218, 150, 228, 150), (120, 126, 134))
    # 桌子：桌面、抽屉、桌腿
    rect(d, (212, 124, 246, 127), wood, dark)
    line(d, (213, 124, 245, 124), hi)
    rect(d, (214, 128, 232, 135), (176, 140, 104), (108, 94, 82))
    line(d, (221, 131, 225, 131), (70, 76, 82))
    for x in (214, 242):
        rect(d, (x, 128, x + 2, 150), (144, 114, 86), (92, 86, 86))
    rect(d, (234, 128, 242, 131), (166, 130, 96), (108, 94, 82))
    # 桌上：三本竖着的文件夹、急救箱、一叠纸
    for i, col in enumerate(((70, 110, 180), (200, 70, 70), (220, 190, 70))):
        x = 213 + i * 3
        rect(d, (x, 112, x + 2, 123), col, (40, 40, 50))
        line(d, (x + 1, 114, x + 1, 116), (250, 250, 240))
    rect(d, (223, 117, 232, 123), (246, 246, 240), (150, 150, 150))
    rect(d, (227, 118, 228, 122), (210, 50, 50))
    rect(d, (225, 119, 230, 120), (210, 50, 50))
    line(d, (226, 116, 229, 116), (120, 120, 126))
    d.polygon([(233, 122), (240, 121), (241, 123), (234, 123)], fill=C((240, 234, 210)), outline=C((156, 158, 158)))
    # 药柜（玻璃门、三层药瓶、下面两个抽屉、顶上一个纸箱）
    rect(d, (248, 50, 278, 130), (184, 198, 194), (90, 112, 122), 2)
    rect(d, (251, 54, 275, 108), (150, 180, 188), (112, 140, 146))
    for y in (70, 89, 107):
        line(d, (251, y, 275, y), (210, 222, 214))
        for i, x in enumerate(range(253, 273, 5)):
            col = ((158, 110, 70), (212, 224, 206), (86, 142, 126), (200, 120, 140))[(i + y) % 4]
            rect(d, (x, y - 12, x + 3, y - 1), col, (90, 108, 114))
            rect(d, (x, y - 14, x + 3, y - 12), (216, 218, 206))
            line(d, (x + 1, y - 8, x + 2, y - 8), (240, 240, 226))
    line(d, (253, 56, 253, 106), (188, 212, 214))
    line(d, (263, 54, 263, 108), (122, 146, 150))
    rect(d, (265, 79, 266, 86), (92, 106, 118))
    for y0 in (111, 120):
        rect(d, (251, y0, 275, y0 + 7), (168, 184, 180), (110, 128, 128))
        line(d, (260, y0 + 3, 266, y0 + 3), (92, 106, 118))
    for x in (250, 275):
        rect(d, (x, 130, x + 2, 150), (120, 134, 136), (80, 94, 98))
    rect(d, (252, 42, 272, 50), (196, 168, 120), (130, 108, 80))   # 顶上纸箱
    line(d, (252, 46, 272, 46), (170, 142, 100))
    rect(d, (259, 44, 265, 48), (246, 246, 240))
    px(d, 262, 46, (210, 50, 50))
    # 门口地垫
    d.polygon([(284, 150), (314, 150), (317, 155), (281, 155)], fill=C((96, 120, 110)), outline=C((70, 90, 82)))
    for x in range(286, 314, 4):
        line(d, (x, 151, x + 1, 154), (110, 136, 124))
    return d


def plate(im):
    """门上「保健室」门牌。"""
    d = ImageDraw.Draw(im)
    rect(d, (280, 29, 318, 44), (246, 246, 238), (70, 76, 84))
    line(d, (281, 30, 317, 30), (255, 255, 252))
    line(d, (281, 43, 317, 43), (196, 196, 188))
    try:
        f = ImageFont.truetype(FONT, 12)
        d.fontmode = '1'
        d.text((281, 30), '保健室', font=f, fill=C((40, 44, 56)))
    except OSError:                                               # 没有宋体就画三块灰条
        for x in (283, 295, 307):
            rect(d, (x, 33, x + 9, 41), (90, 94, 104))
    for x in (283, 315):
        line(d, (x, 26, x, 29), (110, 116, 124))


def door(im, opened):
    """门框 + 门板（开：门板滑出画面右边，露出走廊）。"""
    d = ImageDraw.Draw(im)
    fx0, fy0, fx1, fy1 = 280, 44, 318, 151
    rect(d, (fx0, fy0, fx1, fy1), (122, 96, 72), (80, 60, 46))
    line(d, (fx0 + 1, fy0 + 1, fx1 - 1, fy0 + 1), (160, 128, 96))
    ox0, oy0, ox1, oy1 = 283, 47, 315, 149
    if opened:
        # 走廊：对面墙、窗户的光、走廊地面、远处的告示板
        rect(d, (ox0, oy0, ox1, oy1), (196, 198, 190))
        rect(d, (ox0, 118, ox1, 136), (160, 186, 168))
        line(d, (ox0, 118, ox1, 118), (120, 150, 132))
        rect(d, (ox0, 137, ox1, oy1), (176, 180, 176))
        for y in (141, 146):
            line(d, (ox0, y, ox1, y), (160, 164, 160))
        rect(d, (ox0 + 4, 60, ox0 + 20, 92), (206, 228, 240), (140, 150, 156))
        line(d, (ox0 + 12, 60, ox0 + 12, 92), (150, 160, 166))
        rect(d, (ox0 + 22, 70, ox1 - 2, 84), (190, 160, 110), (120, 100, 70))
        for y in (73, 76, 79):
            line(d, (ox0 + 24, y, ox1 - 4, y), (246, 240, 220))
        A._blend_poly(im, [(ox0 + 4, 137), (ox0 + 20, 137), (ox0 + 26, 149), (ox0 + 2, 149)], (255, 250, 230), 40)
        d = ImageDraw.Draw(im)
        # 门板只剩左边一条（滑到右边去了）
        rect(d, (ox1 - 4, oy0, ox1, oy1), (214, 200, 166), (120, 100, 76))
        line(d, (ox1 - 3, oy0 + 2, ox1 - 3, oy1 - 2), (236, 224, 196))
    else:
        rect(d, (ox0, oy0, ox1, oy1), (214, 200, 166), (120, 100, 76))
        rect(d, (ox0 + 2, oy0 + 2, ox1 - 2, oy1 - 2), None, (186, 170, 136))
        rect(d, (288, 56, 310, 94), (204, 216, 220), (120, 112, 96))   # 磨砂玻璃
        A._dither_rect(im, (289, 57, 310, 94), (204, 216, 220), (228, 236, 238), 0.35)
        d = ImageDraw.Draw(im)
        line(d, (299, 57, 299, 93), (150, 140, 120))
        line(d, (289, 75, 309, 75), (150, 140, 120))
        line(d, (290, 58, 296, 58), (250, 252, 252))
        rect(d, (285, 100, 287, 109), (110, 92, 70))                 # 凹把手
        line(d, (286, 101, 286, 108), (60, 48, 38))
        rect(d, (ox0, 140, ox1, 148), (170, 176, 182), (110, 116, 124))   # 踢脚板
        line(d, (ox0 + 1, 141, ox1 - 1, 141), (214, 220, 226))
        line(d, (ox0 + 1, 98, ox0 + 1, 112), (236, 224, 196))
    line(d, (fx0, fy0 + 2, fx1, fy0 + 2), (70, 54, 42))                 # 上导轨
    return d


@lru_cache(maxsize=2)
def static(opened=False):
    im = A._new(W, H, (238, 238, 228))
    room(im)
    wall_items(im)
    bed(ImageDraw.Draw(im), 70, 130)
    bed(ImageDraw.Draw(im), 150, 210)
    desk_and_cabinet(im)
    plate(im)
    door(im, opened)
    return im


def render(t, opened=False):
    # 与浏览器 strip 采样时钟一致，闭合不会因浮点三角函数跨像素而偏一格。
    fi = int(math.floor(t * FPS + 1e-8)) % N
    im = static(opened).copy()
    petal = Image.new('RGBA', (WINDOW[2] - WINDOW[0], WINDOW[3] - WINDOW[1]))
    pd = ImageDraw.Draw(petal)
    for i in range(6):
        phase = (fi + i * 5) % N
        x = 3 + (i * 9 + round(3 * math.sin(math.tau * phase / N))) % 49
        y = 1 + (phase * 43 // N)
        pd.point((x, y), fill=C((250, 190, 214)))
        pd.point((x + 1, y), fill=C((255, 228, 234)))
    im.alpha_composite(petal, (WINDOW[0], WINDOW[1]))
    d = ImageDraw.Draw(im)
    d.line((180, 42, 180, 88), fill=C((226, 230, 222)), width=2)
    d.line((152, 68, 208, 68), fill=C((226, 230, 222)), width=2)
    E._glow_at(im, 240, 116, 14, (255, 236, 156), 0.10 + 0.025 * math.sin(math.tau * fi / N), ry=18, levels=3)
    d = ImageDraw.Draw(im)
    d.line((241, 124, 241, 112, 237, 107), fill=C((96, 126, 120)), width=2)
    d.polygon([(233, 106), (240, 106), (244, 111), (229, 111)], fill=C((94, 142, 132)), outline=C((58, 94, 92)))
    d.line((232, 112, 241, 112), fill=C((255, 240, 178)))
    d.ellipse((237, 123, 245, 125), fill=C((106, 132, 124)), outline=C((68, 94, 96)))
    return im


def door_img(opened):
    return static(opened).crop(DOOR_BOX)


def export(ex, BJ):
    layers = [dict(type='static', image=ex.img('static', render(0)))]
    layers.append(ex.bake('petals', WINDOW, N, FPS, render))
    layers.append(ex.bake('lamp', LAMP, N, FPS, render))
    doors = [ex.img('door%d' % i, door_img(o)) for i, o in enumerate((False, True))]
    layers.append(dict(type='pick', images=doors, key='door', x=DOOR_BOX[0], y=DOOR_BOX[1], k=0))
    st = ex.stage(320, 156, (148, 176), layers,
                  anchors=dict(bed1=[100, 152], bed2=[180, 152], desk=[230, 156], cabinet=[263, 152], door=[299, 156], walk_x=[40, 304]))
    if ex.check_on:
        for t in (0, 0.125, 1.75, 3.875, 4, 12.25):
            ex.checked('保健室 t=%.3f 导出与直接绘制一致（门关）' % t,
                       BJ.ndiff_rgba(BJ.ref_render(st, ex.images, 0, t, dict(door=0)), render(t)))
        ex.checked('保健室 门开 导出与直接绘制一致',
                   BJ.ndiff_rgba(BJ.ref_render(st, ex.images, 0, 1.0, dict(door=1)), render(1.0, opened=True)))
        a = np.array(render(0))
        ex.checked('整幅保健室不透明且没有露黑', int((a[:, :, 3] != 255).sum() + (a[:, :, :3].sum(-1) == 0).sum()))
        ex.checked('花瓣与台灯四秒严格闭合', BJ.ndiff_rgba(render(0), render(4)))
    return st


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '_preview')
    os.makedirs(out, exist_ok=True)
    a, b = render(0), render(0, opened=True)
    sheet = Image.new('RGBA', (W * 2 + 4, H), (16, 16, 20, 255))
    sheet.paste(a, (0, 0))
    sheet.paste(b, (W + 4, 0))
    p = os.path.join(out, 'school_infirmary_solo.png')
    sheet.resize((sheet.width * 3, H * 3), Image.Resampling.NEAREST).save(p)
    print(p)
