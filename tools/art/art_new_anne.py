"""anne：独立角色注册，人体关节与绘制工具共用。"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from engine import sprite
from art_later_people import register, PEOPLE
NEW = register('anne',{'idle':2,'walk':4,'talk':2,'hurt':1,'down':1,'portrait':2,'run':4,'shock':1,'wave':2,'angry':1,'portrait_angry':1})
ONESHOT = {'hurt','down','slash','attack','grab','reveal','punch','shock','beg','hide','angry'}
STATIC_STATES = {'true_form'}
CHAR_INFO = {'anne': dict(zh=PEOPLE['anne'][0],en='anne',cat='人物',typ='人物')}


# angry 原来和 idle 帧 0 一模一样（通用 body() 没有 angry 分支）。2026-10-10 改成看得出生气：在 idle 帧 0 上
# 擦掉垂着的近侧手臂、眉头压到眼睛上、咬牙，上身按行前倾（头 2 px、胸 1 px、腰以下不动），拳头攥着往前伸，头顶右边加一个青筋记号。
_K, _COAT, _SKIN, _WHITE = (20, 18, 30), (222, 154, 78), (230, 174, 126), (240, 236, 214)


def _lean(im, steps=((0, 9, 2), (10, 17, 1))):
    a = np.array(im)
    out = a.copy()
    for y0, y1, dx in steps:
        out[y0:y1 + 1] = 0
        out[y0:y1 + 1, dx:] = a[y0:y1 + 1, :a.shape[1] - dx]
    return Image.fromarray(out, 'RGBA')


def _angry(base):
    a = np.array(base.copy())
    if a.shape[:2] != (32, 36):
        raise ValueError('anne.idle 尺寸变了（应为 36×32），angry 的像素坐标要重对')
    a[19:27, 24:30] = 0                          # 擦掉垂着的近侧手臂
    a[19:22, 23] = _K + (255,)                   # 躯干右边补描边
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    d.point((22, 9), fill=_K)                    # 眉头压到眼睛上（眼白只剩左边一格）
    d.point((22, 10), fill=_K)
    d.line((20, 13, 23, 13), fill=_K)            # 咬牙
    d.point((21, 13), fill=_WHITE)
    im = _lean(im)
    d = ImageDraw.Draw(im)
    pts = [(24, 18), (27, 20), (29, 21)]         # 握拳往前下方攥着
    d.line(pts, fill=_K, width=5, joint='curve')
    d.line(pts, fill=_COAT, width=3, joint='curve')
    d.rectangle((28, 18, 32, 22), fill=_K)
    d.rectangle((29, 19, 31, 21), fill=_SKIN)
    d.point((30, 20), fill=(196, 136, 96))
    for p in ((29, 0), (29, 1), (28, 1), (31, 0), (31, 1), (32, 1), (28, 3), (29, 3), (29, 4), (32, 3), (31, 3), (31, 4)):
        d.point(p, fill=(232, 52, 60))           # 青筋记号
    return im


sprite.define('anne.angry', [_angry(sprite.get('anne.idle').frames[0])], anchor='mb', fps=3,
              desc='安：生气（上身前倾、攥拳往前、眉头压低、咬牙、头顶青筋记号）')
