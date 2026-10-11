"""后续非人类：寄生替身、婴儿和猫分别使用独立比例及动作（恶魔娃娃 devo_doll 已移到 art_new_devo.py）。"""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
from engine import sprite

NEW=[]
ONESHOT={'slash','bite','split','attack','hurt','down'}
STATIC_STATES=set()
CHAR_INFO={}
K=(20,18,30,255)


def egypt_stand(cid,act,i):
    horus=cid=='horus'; im=Image.new('RGBA',(48,52)); d=ImageDraw.Draw(im)
    light=(178,218,226) if horus else (170,126,174)
    dark=(76,130,164) if horus else (72,50,100)
    edge=(230,244,230) if horus else (238,198,104)
    bob=i%2 if act in ('idle','fly','walk') else 0
    if act=='down':
        d.polygon([(3,45),(7,31),(19,35),(34,37),(43,47)],fill=dark,outline=K)
        d.ellipse((2,30,16,42),fill=light,outline=K); d.line((6,35,11,38),fill=K); return im
    d.polygon([(15,22+bob),(32,22+bob),(35,39),(14,39)],fill=light,outline=K)
    for x in (16,29):
        d.line((x,37,x-2 if x<20 else x+2,49),fill=K,width=7)
        d.line((x,37,x-2 if x<20 else x+2,49),fill=dark,width=5)
    d.rectangle((11,48,20,51),fill=dark,outline=K); d.rectangle((28,48,38,51),fill=dark,outline=K)
    if horus:
        # 荷鲁斯用鸟喙、分叉冰冠和翼形前臂，不能沿用人类换色轮廓。
        d.polygon([(16,20+bob),(12,10+bob),(15,3+bob),(20,8+bob),(24,bob),(28,8+bob),(34,4+bob),(33,16+bob),(28,22+bob)],fill=light,outline=K)
        d.polygon([(30,11+bob),(43,15+bob),(30,19+bob)],fill=(116,160,182),outline=K)
        d.line((28,10+bob,33,10+bob),fill=K,width=2); d.point((30,10+bob),fill=(236,80,72))
        for x,y in ((16,9),(21,4),(29,9)): d.line((x,y+bob,x+1,y+5+bob),fill=edge)
        d.polygon([(15,24),(5,18 if i%2 else 13),(0,29),(6,26),(4,34),(14,35)],fill=dark,outline=K)
        d.polygon([(32,24),(43,14 if i%2 else 21),(47,33),(40,28),(43,39),(33,35)],fill=dark,outline=K)
        for y in (26,30,34): d.line((19,y,29,y-3),fill=edge)
        if act in ('attack','cast'):
            for x,y in ((4,8),(42,6),(40,39)):
                d.polygon([(x,y-5),(x+3,y),(x,y+8),(x-3,y)],fill=light,outline=edge)
    else:
        # 奥西里斯保留头盔、胸口圆纹和勾取灵魂的张掌手势，与阿图姆的心形面甲区分。
        d.polygon([(13,16+bob),(14,5+bob),(20,1+bob),(31,4+bob),(35,13+bob),(30,22+bob),(19,21+bob)],fill=light,outline=K)
        d.polygon([(13,8+bob),(15,bob),(30,bob),(36,8+bob)],fill=dark,outline=K)
        d.rectangle((18,9+bob,29,12+bob),fill=(38,30,58),outline=edge)
        d.line((21,16+bob,29,16+bob),fill=K); d.rectangle((23,18+bob,25,20+bob),fill=edge)
        d.ellipse((19,25,29,35),fill=dark,outline=edge); d.ellipse((22,28,26,32),fill=edge)
        for x,sgn in ((14,-1),(33,1)):
            d.line((x,25,x+sgn*7,34-i%2*6),fill=K,width=7)
            d.line((x,25,x+sgn*7,34-i%2*6),fill=dark,width=5)
            yy=33-i%2*6; xx=x+sgn*7
            d.ellipse((xx-4,yy-3,xx+4,yy+4),fill=(122,172,146),outline=K)
            if act=='attack':
                for j in range(4): d.line((xx-3+j*2,yy,xx-4+j*2,yy-8),fill=(122,172,146),width=2)
    if act=='hurt': d.line((18,9,31,16),fill=edge,width=2)
    return im


def define(cid,zh,actions,draw,anchor='mb'):
    CHAR_INFO[cid]=dict(zh=zh,en=cid,cat='非人形',typ='替身' if cid in ('empress','lovers') else '角色')
    for act,n in actions.items():
        name=cid+'.'+act
        sprite.define(name,[draw(act,i) for i in range(n)],anchor='mm' if act.startswith('portrait') else anchor,fps=6 if act in ('run','walk') else 3,desc=zh+'：'+act)
        NEW.append(name)


def empress(act,i):
    stage=int(act[1]) if act.startswith('l') else 3
    w,h=((8,8),(12,12),(18,18),(24,24))[stage]
    im=Image.new('RGBA',(w,h)); d=ImageDraw.Draw(im)
    skin=(202,108,138); shade=(128,54,94)
    d.ellipse((1,1+i%2,w-2,h-3),fill=skin,outline=K)
    d.polygon([(2,h-3),(w//2,h-1),(w-3,h-3)],fill=shade,outline=K)
    if stage>0:
        d.ellipse((w//3,2,w-3,h//2+1),fill=(226,144,150),outline=K)
        d.point((w-5,4),fill=K); d.line((w-7,6,w-3,6),fill=K)
        if act.endswith('bite'): d.rectangle((w-7,6,w-3,8),fill=K); d.line((w-6,7,w-4,7),fill=(248,228,188))
    if stage>1:
        d.line((4,h//2,1,h-7),fill=K,width=4); d.line((w-5,h//2,w-1,h-7),fill=K,width=4)
        d.line((4,h//2,1,h-7),fill=skin,width=2); d.line((w-5,h//2,w-1,h-7),fill=skin,width=2)
        d.line((4,2,3,0),fill=(68,34,72),width=2); d.line((w-5,2,w-3,0),fill=(68,34,72),width=2)
    if act=='hurt':
        d.line((w//2,4,w-4,8),fill=(248,234,194),width=2)
        d.line((w//2,8,w-4,4),fill=K)
    if act=='down':
        out=Image.new('RGBA',(28,10)); od=ImageDraw.Draw(out)
        od.ellipse((0,3,17,9),fill=shade,outline=K)
        od.ellipse((13,0,26,9),fill=skin,outline=K)
        od.line((19,3,23,6),fill=K); od.line((19,6,23,3),fill=K)
        return out
    return im


def lovers(act,i):
    im=Image.new('RGBA',(8,8)); d=ImageDraw.Draw(im)
    d.ellipse((2,1,5,4),fill=(226,194,114),outline=K)
    d.line((3,4,2,7),fill=K); d.line((4,4,5,7),fill=K)
    d.line((2,4,0,3+i),fill=(230,202,130)); d.line((5,4,7,3-i),fill=(230,202,130))
    d.point((4,2),fill=(240,58,68))
    if act=='split': d.point((0,0),fill=(242,202,144)); d.point((7,0),fill=(242,202,144))
    elif act=='walk':
        d.line((3,4,1+i,7),fill=(230,202,130)); d.line((4,4,6-i,7),fill=(230,202,130))
    elif act=='hurt': d.line((1,1,6,6),fill=(248,236,208))
    elif act=='down':
        im=Image.new('RGBA',(8,5)); d=ImageDraw.Draw(im)
        d.ellipse((0,1,4,4),fill=(226,194,114),outline=K); d.line((4,3,7,4),fill=K)
    return im


def baby(act,i):
    portrait=act=='portrait'; w,h=(32,32) if portrait else (20,16)
    im=Image.new('RGBA',(20,16)); d=ImageDraw.Draw(im)
    d.ellipse((2,7,17,15),fill=(230,220,166),outline=K)
    d.rectangle((7,11,15,14),fill=(242,236,206),outline=(140,118,96))
    d.ellipse((3,0,15,11),fill=(230,182,132),outline=K)
    d.line((8,1,9,0,11,1),fill=(126,72,48))
    d.line((6,5,8,5),fill=K); d.line((11,5,13,5),fill=K)
    if act=='laugh' or portrait and i:
        d.rectangle((8,7,12,9),fill=(104,40,46)); d.line((8,7,11,7),fill=(248,234,202))
    elif act=='cry':
        d.line((6,5,8,4),fill=K); d.line((11,4,13,5),fill=K)
        d.line((6,6,5,9+i),fill=(116,204,232)); d.line((13,6,14,9+i),fill=(116,204,232))
        d.ellipse((8,7,11,10),fill=(94,44,52))
    else: d.line((9,8,12,8+i%2),fill=K)
    d.ellipse((0,10+i%2,4,13+i%2),fill=(230,182,132),outline=K)
    if act=='walk': d.rectangle((4+i*5,12,9+i*5,15),fill=(230,182,132),outline=K)
    elif act=='hurt': d.line((6,4,8,6),fill=K); d.line((11,6,13,4),fill=K)
    elif act=='down':
        out=Image.new('RGBA',(22,12)); od=ImageDraw.Draw(out)
        od.ellipse((8,3,21,11),fill=(230,220,166),outline=K)
        od.ellipse((0,0,12,10),fill=(230,182,132),outline=K); od.line((4,3,8,6),fill=K)
        return out
    if portrait:
        out=Image.new('RGBA',(32,32)); out.alpha_composite(im.resize((32,26),Image.Resampling.NEAREST),(0,3)); return out
    return im


def slime(act,i):
    w=40 if act=='slime_attack' else 28
    im=Image.new('RGBA',(w,20)); d=ImageDraw.Draw(im)
    pts=[(1,18),(4,11),(7,13),(9,7+i),(15,3),(20,9),(24,11),(w-2,18)]
    d.polygon(pts,fill=(234,206,70),outline=K)
    d.line((5,16,9,10,13,8),fill=(255,238,122),width=2)
    d.line((14,14,18,8,22,13),fill=(166,126,32),width=2)
    if act=='slime_attack': d.polygon([(20,11),(29,6-i*3),(38,2+i*6),(33,10),(w-3,16),(25,17)],fill=(234,206,70),outline=K)
    d.ellipse((14,9,18,12),fill=(122,70,36)); d.point((16,10),fill=(236,236,166))
    return im


def cat(act,i):
    im=Image.new('RGBA',(24,20)); d=ImageDraw.Draw(im)
    d.ellipse((3,9,17,18),fill=(206,174,108),outline=K)
    d.line((4,15,1,10,2,5),fill=K,width=3); d.line((4,15,1,10,2,5),fill=(172,130,80))
    d.polygon([(13,8),(12,2),(16,5),(20,2),(22,10),(19,14),(14,12)],fill=(224,194,122),outline=K)
    d.point((16,8),fill=(104,156,70)); d.point((20,8),fill=(104,156,70)); d.point((18,10),fill=(146,74,70))
    d.rectangle((14,16,16,19),fill=(206,174,108),outline=K)
    if act=='eat': d.line((18,13,19,15+i),fill=(154,62,72)); d.ellipse((17,17,23,19),fill=(126,108,84),outline=K)
    elif act=='walk':
        im.paste((0,0,0,0),(4,15,18,20)); d=ImageDraw.Draw(im)
        d.line((6,14,4+i*4,19),fill=K,width=3); d.line((14,14,18-i*4,19),fill=K,width=3)
        d.line((6,14,4+i*4,18),fill=(206,174,108)); d.line((14,14,18-i*4,18),fill=(206,174,108))
    elif act=='hurt': d.line((15,7,21,10),fill=K); d.line((15,10,21,7),fill=K)
    elif act=='down':
        out=Image.new('RGBA',(26,10)); od=ImageDraw.Draw(out)
        od.ellipse((0,2,18,9),fill=(206,174,108),outline=K)
        od.polygon([(17,0),(20,2),(24,0),(25,8),(18,9)],fill=(224,194,122),outline=K)
        od.line((19,5,23,5),fill=K); return out
    return im


def midler(act,i):
    im=Image.new('RGBA',(32,48)); d=ImageDraw.Draw(im)
    d.polygon([(12,18),(22,18),(23,31),(25,44),(21,47),(16,33),(11,46),(7,45),(10,30)],fill=(34,24,52),outline=K)
    d.polygon([(7,25),(5,7),(10,1),(20,1),(25,8),(23,29),(20,17),(16,20),(12,17)],fill=(30,24,50),outline=(110,74,128))
    d.line((22,22,27,27,29,19),fill=(86,50,100),width=2)
    return im


# devo_doll（恶魔娃娃）2026-10-11 起在 art_new_devo.py 里画和注册（重画成诡异木偶 + 新动作 jump / peek）
define('empress','女帝',{**{f'l{s}_idle':2 for s in range(4)},**{f'l{s}_bite':1 for s in range(4)},'idle':2,'walk':2,'talk':2,'hurt':1,'down':1,'bite':1},empress)
define('lovers','恋人',{'idle':2,'walk':2,'talk':2,'hurt':1,'down':1,'split':1},lovers,'mm')
define('mannish','玛尼修男孩',{'idle':2,'walk':2,'talk':2,'hurt':1,'down':1,'laugh':2,'cry':2,'portrait':2},baby)
define('npc_cat','咖啡馆的猫',{'idle':2,'walk':2,'talk':2,'hurt':1,'down':1,'eat':2},cat)
define('midler_back','蜜朵拉背影',{'idle':1,'walk':1,'talk':1,'hurt':1,'down':1},midler)
for cid,zh in [('osiris','奥西里斯神'),('horus','荷鲁斯神')]:
    define(cid,zh,{'idle':2,'walk':2,'attack':2,'hurt':1,'down':1},lambda act,i,c=cid:egypt_stand(c,act,i))
    CHAR_INFO[cid].update(cat='替身',typ='替身')
for act,n in {'slime_idle':2,'slime_attack':2}.items():
    name='rubbersoul.'+act
    sprite.define(name,[slime(act,i) for i in range(n)],anchor='mb',fps=4,desc='黄色节制黏液：'+act)
    NEW.append(name)
