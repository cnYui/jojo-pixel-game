"""kennyg：独立角色注册，人体关节与绘制工具共用。"""
import sys
sys.dont_write_bytecode = True
from PIL import ImageDraw
from art_later_people import register, PEOPLE, body, limb, K, S, GOLD
from engine import sprite
NEW = register('kennyg',{'idle':2,'walk':4,'talk':2,'hurt':1,'down':1,'portrait':2,'attack':2})


def sax_frame(fi):
    im = body('kennyg', 'idle', 0)
    # 吹奏时嘴、双手和乐器形成闭合轮廓；两帧按键变化而不是挪动整张站姿。
    im.paste((0, 0, 0, 0), (24, 20, 36, 41))
    im.paste((0, 0, 0, 0), (7, 23, 13, 36))
    d = ImageDraw.Draw(im)
    d.polygon([(24, 20), (25, 20), (25, 34), (24, 34)], fill=(112, 80, 114), outline=K)
    limb(d, [(12, 22), (10, 26), (24, 28 + fi)], (118, 84, 119), 3)
    limb(d, [(24, 22), (30, 23 + fi), (27, 26 + fi)], (164, 118, 166), 3)
    d.line([(23, 17), (28, 20), (28, 31), (25, 35), (29, 38)], fill=K, width=5)
    d.line([(23, 17), (28, 20), (28, 31), (25, 35), (29, 38)], fill=GOLD, width=3)
    d.line((28, 21, 28, 31), fill=(255, 230, 142), width=1)
    d.polygon([(29, 34), (34, 32), (35, 36), (29, 39), (27, 37)], fill=GOLD, outline=K)
    d.line((32, 33, 33, 36), fill=(116, 78, 42), width=2)
    for y in (24, 27, 30):
        d.point((29, y), fill=(250, 240, 194))
    d.rectangle((23, 27 + fi, 26, 29 + fi), fill=S, outline=K)
    d.rectangle((26, 24 + fi, 29, 26 + fi), fill=S, outline=K)
    d.line((20, 17, 23, 17), fill=(144, 78, 74), width=1)
    d.point((22, 16), fill=S)
    return im


sprite.define('kennyg.sax', [sax_frame(i) for i in range(2)], anchor='mb', fps=6, desc='肯尼G：吹奏萨克斯')
NEW.append('kennyg.sax')
ONESHOT = {'hurt','down','slash','attack','grab','reveal','punch','shock','beg','hide','angry'}
STATIC_STATES = {'true_form'}
CHAR_INFO = {'kennyg': dict(zh=PEOPLE['kennyg'][0],en='kennyg',cat='人物',typ='人物')}
