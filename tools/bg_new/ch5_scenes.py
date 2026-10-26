"""第5章的分层像素场景；交互锚点与画面共用坐标，避免剧情站在空白处。"""
import sys
sys.dont_write_bytecode = True

import math
import random
from functools import lru_cache
from PIL import Image, ImageDraw

W, H = 320, 180
INK = (31, 29, 42)
SAND = (205, 170, 118)
LIGHT = (243, 217, 165)


def canvas(w=W, colour=None):
    return Image.new('RGBA', (w, H), colour or (0, 0, 0, 0))


def gradient(top, bottom):
    im = canvas()
    d = ImageDraw.Draw(im)
    for y in range(H):
        d.line((0, y, W, y), fill=tuple(round(a + (b-a)*y/(H-1)) for a, b in zip(top, bottom)))
    return im


def texture(d, box, colours, count, seed=5):
    rng = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(count):
        x, y = rng.randrange(x0, x1), rng.randrange(y0, y1)
        d.line((x, y, min(x+2, x1-1), y), fill=rng.choice(colours))


def window(d, x, y, w=16, h=24, colour=(56, 75, 83), arch=False):
    d.rectangle((x-2, y-2, x+w+2, y+h+2), fill=(113, 93, 81), outline=INK)
    d.rectangle((x, y, x+w, y+h), fill=colour)
    if arch:
        d.pieslice((x, y-w//2, x+w, y+w//2), 180, 360, fill=colour, outline=INK)
    d.line((x+w//2, y, x+w//2, y+h), fill=(182, 156, 117))
    d.line((x, y+h//2, x+w, y+h//2), fill=INK)
    d.line((x+2, y+3, x+2, y+h-2), fill=(135, 150, 149))


def door(d, x, y, w=22, h=40):
    d.rectangle((x-3, y-3, x+w+3, y+h), fill=(165, 126, 94), outline=INK)
    d.rectangle((x, y, x+w, y+h), fill=(57, 61, 66), outline=INK)
    for xx in (x+3, x+w//2+2):
        d.rectangle((xx, y+4, xx+w//2-5, y+h-5), outline=(102, 106, 100))
    d.rectangle((x+w-5, y+h//2, x+w-3, y+h//2+1), fill=(232, 194, 110))


def street_floor(im, w, colour):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 142, w, H), fill=colour)
    d.line((0, 142, w, 142), fill=INK)
    d.line((0, 145, w, 145), fill=tuple(min(255, c+16) for c in colour))
    for y in range(153, H, 8):
        d.line((0, y, w, y), fill=tuple(max(0, c-9) for c in colour))
        for x in range((y//8%2)*17, w, 34):
            d.line((x, y-7, x-2, y), fill=tuple(max(0, c-16) for c in colour))
    texture(d, (0, 146, w, H), [(161, 140, 112), (185, 163, 130)], w//2)


def mountains(w=640, cool=False):
    im = canvas(w)
    d = ImageDraw.Draw(im)
    col = (137, 158, 161) if cool else (170, 157, 154)
    for x, peak in ((-30, 68), (100, 46), (240, 74), (400, 58), (570, 73)):
        d.polygon([(x, 123), (x+90, peak), (x+210, 123)], fill=col)
        d.polygon([(x+90, peak), (x+119, peak+41), (x+162, 123), (x+101, 112)],
                  fill=(123, 144, 146) if cool else (151, 135, 139))
        d.line((x+90, peak, x+117, peak+44), fill=(197, 184, 170))
    return im


def highway():
    sky = gradient((79, 137, 184), (240, 219, 172))
    sd = ImageDraw.Draw(sky)
    sd.ellipse((249, 19, 266, 36), fill=(255, 240, 193))
    far = mountains()
    near = canvas(640)
    d = ImageDraw.Draw(near)
    d.rectangle((0, 118, 640, H), fill=(182, 142, 93))
    d.polygon([(0, 128), (110, 108), (212, 127), (366, 115), (480, 123), (640, 111), (640, H), (0, H)], fill=SAND)
    texture(d, (0, 127, 640, 144), [(175, 138, 95), (224, 190, 134)], 380)
    for x in (29, 166, 315, 510):
        d.line((x, 130, x, 113), fill=(73, 93, 60), width=3)
        d.line((x, 120, x-5, 117, x-5, 112), fill=(73, 93, 60), width=3)
        d.line((x, 125, x+5, 122, x+5, 117), fill=(73, 93, 60), width=3)
        d.line((x+1, 113, x+1, 129), fill=(127, 139, 77))
    d.rectangle((0, 143, 640, H), fill=(79, 77, 76))
    d.line((0, 146, 640, 146), fill=(224, 197, 137), width=2)
    for y in (156, 166):
        for x in range(0, 640, 48):
            d.rectangle((x, y, x+22, y+1), fill=(224, 215, 183))
    texture(d, (0, 148, 640, H), [(90, 84, 78), (67, 65, 66)], 430, 9)
    for x in range(50, 640, 160):
        d.rectangle((x, 130, x+2, 145), fill=(228, 217, 183), outline=INK)
        d.rectangle((x, 132, x+2, 136), fill=(109, 68, 51))
    return dict(w=320, ground=160, walk=(152, 168), layers=[
        dict(type='static', src=sky, name='sky'),
        dict(type='wrap', src=far, name='hills', period=640, k=.2, vx=24),
        dict(type='wrap', src=near, name='road', period=640, k=1, vx=360)], fg=[],
        anchors={'party_car': [80, 160], 'lanes': [152, 160, 168]})


def cliff():
    base = gradient((87, 139, 178), (244, 213, 159))
    base.alpha_composite(mountains(320))
    d = ImageDraw.Draw(base)
    d.polygon([(0, 14), (43, 7), (68, 30), (93, 31), (122, 76), (116, 145), (0, 145)], fill=(136, 92, 70), outline=INK)
    d.polygon([(0, 14), (30, 17), (46, 51), (61, 64), (79, 118), (60, 145), (0, 145)], fill=(186, 132, 86))
    d.polygon([(50, 32), (68, 30), (94, 73), (91, 111), (115, 145), (79, 118)], fill=(103, 75, 67))
    for y, x in ((36, 12), (57, 35), (89, 4), (111, 38), (130, 77)):
        d.line((x, y, x+24, y-3, x+37, y+1), fill=(93, 70, 59), width=2)
        d.line((x, y-2, x+20, y-5), fill=(223, 172, 110))
    d.rectangle((0, 144, W, H), fill=(188, 155, 108))
    d.polygon([(0, 148), (320, 151), (320, 174), (0, 174)], fill=(151, 131, 108))
    texture(d, (0, 150, W, 174), [(172, 150, 119), (136, 117, 100)], 230)
    for x in range(8, W, 32):
        d.rectangle((x, 146, x+2, 154), fill=(229, 218, 174), outline=INK)
    d.line((0, 148, W, 148), fill=(107, 95, 79), width=2)
    d.polygon([(0, 175), (70, 178), (131, 175), (206, 179), (261, 174), (320, 177), (320, H), (0, H)], fill=(109, 84, 66))
    return dict(w=320, ground=160, walk=(148, 176), layers=[dict(type='static', src=base, name='cliff')], fg=[],
                anchors={'arrive': [110, 162], 'wheel': [230, 160], 'tunnel': [128, 169]})


def fog_frame(i):
    im = canvas(480)
    d = ImageDraw.Draw(im)
    for n in range(9):
        x = (n*71+int(11*math.sin((i%8)/8*math.tau+n))) % 540-70
        y = 99+(n%4)*13
        d.ellipse((x, y, x+100, y+15), fill=(173, 195, 195, 27))
        d.ellipse((x+22, y-3, x+70, y+6), fill=(195, 210, 209, 18))
    return im.crop((0, 0, W, H))


def fogtown():
    sky = gradient((32, 52, 64), (114, 139, 144))
    far = canvas(400)
    fd = ImageDraw.Draw(far)
    for x in range(-10, 400, 43):
        y = 57+(x*13%35)
        fd.rectangle((x, y, x+38, 145), fill=(64, 91, 100))
        fd.polygon([(x-2, y), (x+18, y-15), (x+40, y)], fill=(52, 77, 90))
        for yy in (y+17, y+40):
            fd.rectangle((x+10, yy, x+15, yy+8), fill=(110, 136, 133))
    near = canvas(480)
    d = ImageDraw.Draw(near)
    blocks = [(0, 72, 78, (106, 110, 100)), (81, 135, 57, (92, 108, 104)),
              (200, 268, 78, (101, 109, 104)), (300, 408, 37, (119, 113, 100)), (418, 480, 65, (81, 104, 105))]
    for x0, x1, y, col in blocks:
        d.rectangle((x0, y, x1, 145), fill=col, outline=INK)
        d.rectangle((x0-2, y-4, x1+2, y+2), fill=(74, 89, 85), outline=INK)
        d.line((x0+4, y+5, x1-4, y+5), fill=(149, 148, 120))
        for x in range(x0+10, x1-12, 28):
            window(d, x, y+17, 13, 22, (41, 68, 74), arch=True)
        texture(d, (x0+2, y+38, x1-1, 137), [(82, 94, 87), (123, 121, 101)], (x1-x0)//2, x0+4)
    door(d, 48, 106, 19, 37)
    door(d, 227, 102, 20, 41)
    door(d, 357, 99, 25, 44)
    d.rectangle((326, 77, 391, 93), fill=(55, 55, 61), outline=INK)
    # 像素字牌使用固定小点阵，字体资源不参与背景构建。
    for j, glyph in enumerate(('101111101101101', '111101101101111', '111010010010010', '111100110100111', '100100100100111')):
        for k, bit in enumerate(glyph):
            if bit == '1':
                x, y = 335+j*10+(k%3)*2, 81+(k//3)*2
                d.rectangle((x, y, x+1, y+1), fill=(221, 204, 145))
    street_floor(near, 480, (109, 123, 119))
    for x, y, width in ((148, 131, 12), (167, 124, 10), (186, 134, 13)):
        d.rounded_rectangle((x-width//2, y-17, x+width//2, y), radius=3, fill=(149, 151, 126), outline=INK)
        d.line((x-2, y-11, x+2, y-11), fill=(94, 105, 96))
        d.polygon([(x-width, y), (x+width, y), (x+width+2, y+4), (x-width-2, y+4)], fill=(76, 93, 86))
    d.line((31, 73, 31, 144), fill=INK, width=3)
    d.rectangle((24, 69, 38, 76), fill=(206, 189, 116), outline=INK)
    d.rectangle((27, 71, 35, 75), fill=(240, 219, 163))
    for x in (260, 282):
        d.line((x, 101, x+3, 130), fill=(45, 75, 76), width=2)
    return dict(w=480, ground=160, walk=(146, 176), layers=[
        dict(type='static', src=sky, name='sky'), dict(type='pano', src=far, name='far', k=.5, x=0, y=0),
        dict(type='pano', src=near, name='town', k=1, x=0, y=0)],
        fg=[dict(type='strip', fn=fog_frame, name='mist')],
        anchors={'arrive': [63, 163], 'resident': [96, 160], 'graves': [169, 151], 'lamp': [31, 149],
                 'inn': [366, 160], 'inn_sign': [362, 91], 'guest': [294, 162]})


def inn():
    base = canvas(colour=(93, 94, 85, 255))
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, W, 16), fill=(41, 48, 48))
    d.line((0, 16, W, 16), fill=(158, 137, 101), width=2)
    for x in range(0, W, 32):
        d.line((x, 18, x, 131), fill=(77, 82, 77))
        d.line((x+1, 18, x+1, 131), fill=(106, 104, 89))
    texture(d, (0, 18, W, 129), [(111, 108, 91), (80, 85, 80)], 280)
    door(d, 18, 75, 31, 57)
    window(d, 70, 45, 35, 49, (34, 53, 62))
    for y in range(50, 90, 5):
        d.line((71, y, 104, y), fill=(67, 87, 87))
    d.rectangle((129, 47, 173, 82), fill=(43, 47, 46), outline=(190, 159, 111), width=2)
    for x in range(134, 170, 8):
        d.line((x, 54, x+4, 54), fill=(141, 145, 110))
        d.line((x, 65, x+3, 65), fill=(100, 110, 95))
    d.rectangle((223, 30, 300, 96), fill=(53, 65, 60), outline=(165, 142, 99), width=2)
    for y in (49, 72):
        d.line((226, y, 297, y), fill=(178, 145, 92), width=2)
    for x in range(230, 297, 10):
        d.line((x, 37, x, 44), fill=(194, 161, 98))
        d.ellipse((x-2, 43, x+2, 47), outline=(194, 161, 98))
    street_floor(base, W, (113, 101, 81))
    d.rectangle((193, 109, 313, 144), fill=(98, 67, 51), outline=INK)
    d.rectangle((189, 106, 316, 112), fill=(169, 130, 82), outline=INK)
    for x in (201, 239, 277):
        d.rectangle((x, 117, x+28, 138), outline=(158, 110, 68))
    d.rectangle((210, 99, 226, 105), fill=(218, 209, 178), outline=INK)
    d.line((213, 101, 223, 101), fill=(92, 90, 79))
    d.rectangle((283, 89, 297, 105), fill=(59, 70, 64), outline=INK)
    d.ellipse((287, 87, 293, 92), fill=(215, 179, 103), outline=INK)
    d.rectangle((80, 125, 154, 132), fill=(73, 67, 62), outline=INK)
    for x in (83, 146):
        d.line((x, 131, x, 144), fill=INK, width=3)
    return dict(w=320, ground=160, walk=(148, 176), layers=[dict(type='static', src=base, name='room')],
                fg=[dict(type='strip', fn=fog_frame, name='mist')],
                anchors={'door': [38, 162], 'counter': [270, 161], 'skull': [230, 77], 'guest': [120, 164]})


def karachi():
    sky = gradient((116, 164, 186), (244, 222, 178))
    far = canvas(480)
    fd = ImageDraw.Draw(far)
    for x in range(-8, 480, 36):
        y = 48+(x*7%25)
        fd.rectangle((x, y, x+32, 135), fill=(175, 164, 141))
        fd.line((x, y, x+32, y), fill=(146, 145, 130))
        fd.rectangle((x+12, y-10, x+22, y), fill=(162, 155, 134))
    fd.rectangle((363, 43, 369, 112), fill=(190, 182, 152))
    fd.polygon([(359, 42), (366, 30), (373, 42)], fill=(112, 153, 143))
    near = canvas(640)
    d = ImageDraw.Draw(near)
    for x0, x1, y, col in ((0, 99, 62, (196, 169, 116)), (104, 197, 40, (195, 179, 148)),
                            (202, 313, 58, (180, 142, 115)), (320, 437, 36, (202, 180, 128)),
                            (442, 539, 67, (155, 164, 142)), (544, 640, 43, (209, 184, 143))):
        d.rectangle((x0, y, x1, 143), fill=col, outline=INK)
        d.rectangle((x0-2, y-4, x1+2, y+2), fill=(133, 115, 88), outline=INK)
        d.line((x0+3, y+6, x1-3, y+6), fill=LIGHT)
        for x in range(x0+12, x1-15, 30):
            window(d, x, y+18, 14, 24, (63, 104, 107), arch=True)
        d.rectangle((x0+6, y+51, x1-6, y+58), fill=(95, 84, 73), outline=INK)
        for x in range(x0+9, x1-7, 9):
            d.line((x, y+52, x, y+58), fill=(165, 139, 98))
        texture(d, (x0+3, y+63, x1-2, 139), [(164, 138, 109), (215, 190, 144)], (x1-x0)//2, x0+3)
    street_floor(near, 640, (193, 167, 124))
    for x, width, colour in ((40, 81, (73, 118, 103)), (239, 90, (145, 68, 76)), (465, 80, (94, 107, 119))):
        d.polygon([(x-5, 101), (x+width+5, 101), (x+width+12, 112), (x-12, 112)], fill=colour, outline=INK)
        for xx in range(x-8, x+width+6, 12):
            d.rectangle((xx, 110, xx+5, 115), fill=LIGHT)
        for xx in (x, x+width):
            d.line((xx, 112, xx, 144), fill=INK, width=2)
        d.rectangle((x+5, 131, x+width-5, 143), fill=(111, 83, 58), outline=INK)
        d.line((x+5, 130, x+width-5, 130), fill=(229, 199, 137), width=2)
    for x in range(257, 313, 8):
        d.ellipse((x, 125, x+5, 130), outline=(238, 207, 104))
        d.point((x+2, 126), fill=(255, 241, 182))
    for x in range(57, 107, 8):
        d.ellipse((x, 125, x+6, 129), fill=(219, 157, 57), outline=(142, 99, 46))
    for x, y in ((25, 34), (215, 28), (425, 30)):
        d.line((x, y, x+168, y+8), fill=INK)
        d.line((x+20, y+6, x+150, y+2), fill=(71, 66, 65))
    # 停车位置留给剧情道具，不在底图烘一辆无法开走的车。
    d.rectangle((557, 146, 633, 171), outline=(219, 201, 151))
    return dict(w=640, ground=160, walk=(148, 176), layers=[dict(type='static', src=sky, name='sky'),
        dict(type='pano', src=far, name='roofs', k=.5, x=0, y=0), dict(type='pano', src=near, name='street', k=1, x=0, y=0)], fg=[],
        anchors={'arrive': [148, 163], 'dan': [194, 162], 'fruit': [86, 153], 'bracelet': [281, 155],
                 'command': [80, 162], 'vendor': [294, 162], 'jeep': [596, 161]})


def neurons(i):
    im = canvas()
    d = ImageDraw.Draw(im)
    phase = (i%8)/8
    for n, (x, y) in enumerate(((21, 40), (90, 27), (149, 79), (248, 28), (287, 101))):
        u = (phase+n*.17)%1
        xx, yy = round(x+u*34), round(y+u*19)
        d.line((xx-4, yy-2, xx, yy), fill=(218, 166, 161, 120))
        d.rectangle((xx-1, yy-1, xx+1, yy+1), fill=(255, 225, 162, 230))
    return im


def brain():
    base = gradient((69, 36, 71), (111, 57, 99))
    d = ImageDraw.Draw(base)
    for x, y, r in ((-20, 68, 75), (68, -10, 78), (179, -20, 85), (308, 25, 89), (327, 113, 67)):
        d.ellipse((x-r, y-r, x+r, y+r), fill=(148, 77, 116), outline=(47, 31, 56), width=3)
        d.arc((x-r+8, y-r+8, x+r-8, y+r-8), 13, 250, fill=(204, 128, 152), width=3)
        d.arc((x-r+17, y-r+18, x+r-19, y+r-15), 36, 220, fill=(116, 60, 105), width=2)
    d.polygon([(0, 136), (54, 129), (110, 142), (169, 131), (236, 143), (320, 133), (320, H), (0, H)], fill=(130, 73, 112))
    for y in (148, 166):
        d.line([(0, y), (34, y-5), (76, y+3), (111, y-2), (156, y+4), (209, y-4), (263, y+3), (320, y-2)], fill=(179, 109, 138), width=2)
    for x, y in ((26, 35), (111, 51), (210, 28), (264, 85), (58, 107)):
        d.ellipse((x-5, y-5, x+5, y+5), fill=(216, 145, 159), outline=(103, 60, 102))
        for dx, dy in ((-18, -14), (23, 12), (-13, 21)):
            d.line((x, y, x+dx//2, y+dy//2, x+dx, y+dy), fill=(208, 137, 157), width=2)
            d.line((x+dx, y+dy, x+dx+9, y+dy-4), fill=(169, 110, 138))
    return dict(w=320, ground=150, walk=(130, 176), layers=[dict(type='static', src=base, name='tunnel'),
                dict(type='strip', fn=neurons, name='signals')], fg=[], anchors={'arrive': [80, 150], 'center': [160, 150]})


SCENES = {'desert_highway': highway, 'mountain_road': cliff, 'fog_town': fogtown,
          'enya_inn': inn, 'karachi_street': karachi, 'brain_inside': brain}


@lru_cache(None)
def make(key):
    return SCENES[key]()


def export(ex, helpers, key=None):
    key = key or ex.key
    spec = make(key)
    stage = helpers.bg_new('later_stages').export(ex, helpers, key, spec=spec)
    if ex.check_on:
        points = [v for k, v in spec['anchors'].items() if k != 'lanes']
        ex.checked('剧情锚点都在地图内', sum(not (0 <= x <= spec['w'] and 0 <= y < H) for x, y in points))
    return stage
