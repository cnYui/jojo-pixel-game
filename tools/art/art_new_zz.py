"""ZZ 的小身躯与粗壮手臂独立绘制，车外现形时仍能辨认角色轮廓。"""
import sys
sys.dont_write_bytecode = True

from PIL import Image, ImageDraw
from engine import sprite

INK = (34, 25, 32)
SKIN = (211, 153, 106)
SHADE = (157, 99, 72)
COAT = (121, 83, 58)
HAIR = (62, 42, 36)
NEW = []
ONESHOT = {'hurt', 'down'}
STATIC_STATES = set()
CHAR_INFO = {'zz': dict(zh='ZZ', en='zz', cat='人物', typ='人物')}


def head(mouth=False, scared=False):
    im = Image.new('RGBA', (19, 18))
    d = ImageDraw.Draw(im)
    d.polygon([(4, 3), (13, 2), (17, 7), (17, 13), (12, 17), (6, 16), (2, 10)], fill=SKIN, outline=INK)
    for x, y in ((3, 2), (6, 1), (9, 1), (12, 2), (2, 6)):
        d.ellipse((x-2, y, x+3, y+4), fill=HAIR, outline=INK)
    d.line((7, 7, 11, 7), fill=INK, width=2)
    d.line((13, 6, 16, 7), fill=INK)
    d.rectangle((8, 9, 10, 10), fill=(242, 230, 202))
    d.point((10, 9), fill=INK)
    d.line((14, 9, 17, 11, 13, 11), fill=SHADE)
    d.line((10, 13, 15, 13), fill=INK)
    if mouth or scared:
        d.rectangle((11, 13, 14, 15), fill=INK)
        d.line((11, 13, 14, 13), fill=(239, 228, 196))
    if scared:
        d.line((17, 2, 18, 5), fill=(160, 210, 220))
    return im


def arm(d, x, y, lift=0):
    d.ellipse((x, y-lift, x+11, y+11-lift), fill=SKIN, outline=INK)
    d.polygon([(x+3, y+8-lift), (x+12, y+6-lift), (x+15, y+16-lift), (x+8, y+18-lift), (x+1, y+13-lift)], fill=SKIN, outline=INK)
    d.line((x+3, y+9-lift, x+7, y+11-lift), fill=SHADE)
    d.line((x+9, y+9-lift, x+12, y+15-lift), fill=(237, 180, 128))
    d.ellipse((x+7, y+13-lift, x+15, y+19-lift), fill=SKIN, outline=INK)


def body(action, i):
    if action == 'down':
        # 偶数宽度让底部中心落在整数像素，保证图集与原引擎绘制一致。
        im = Image.new('RGBA', (48, 19))
        d = ImageDraw.Draw(im)
        im.alpha_composite(head(scared=True).transpose(Image.Transpose.ROTATE_90), (0, 1))
        d.rectangle((15, 7, 30, 15), fill=COAT, outline=INK)
        d.line((28, 10, 42, 9), fill=INK, width=6)
        d.line((28, 10, 42, 9), fill=(88, 75, 66), width=4)
        d.ellipse((13, 1, 28, 11), fill=SKIN, outline=INK)
        d.ellipse((21, 10, 34, 18), fill=SKIN, outline=INK)
        return im
    im = Image.new('RGBA', (46, 40))
    d = ImageDraw.Draw(im)
    bob = i%2 if action in ('idle', 'talk') else 0
    stride = (-2, 0, 2, 0)[i%4] if action == 'walk' else 0
    d.line((21, 29, 19-stride, 37), fill=INK, width=7)
    d.line((29, 29, 31+stride, 37), fill=INK, width=7)
    d.line((21, 29, 19-stride, 36), fill=(101, 87, 75), width=4)
    d.line((29, 29, 31+stride, 36), fill=(101, 87, 75), width=4)
    d.rectangle((15-stride, 36, 23-stride, 39), fill=INK)
    d.rectangle((28+stride, 36, 36+stride, 39), fill=INK)
    arm(d, 6, 17+bob, 2 if action == 'hurt' else 0)
    d.polygon([(17, 17+bob), (30, 17+bob), (31, 30), (17, 30)], fill=COAT, outline=INK)
    d.line((22, 18+bob, 24, 27), fill=(190, 144, 92), width=2)
    arm(d, 28, 17+bob, 4 if action == 'hurt' else 0)
    im.alpha_composite(head(mouth=action=='talk' and i%2, scared=action=='hurt'), (15, bob))
    return im


for action, n in {'idle': 2, 'walk': 4, 'talk': 2, 'hurt': 1, 'down': 1, 'portrait': 2}.items():
    frames = [head(scared=bool(i)).resize((57, 54), Image.Resampling.NEAREST) if action=='portrait' else body(action, i) for i in range(n)]
    name = 'zz.'+action
    sprite.define(name, frames, anchor='mm' if action=='portrait' else 'mb', fps=6 if action=='walk' else 3, desc='ZZ：'+action)
    NEW.append(name)
