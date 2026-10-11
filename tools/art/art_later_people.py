"""后续人物的像素绘制：复用人体关节，头部、服装、轮廓与配件按角色独立绘制。"""
import sys
sys.dont_write_bytecode = True

import math
from PIL import Image, ImageDraw
import art_common as AC
from engine import sprite

K = (20, 18, 30, 255)
S = (230, 174, 126, 255)
SD = (164, 104, 82, 255)
WHITE = (240, 236, 214, 255)
GOLD = (242, 198, 86, 255)

# 衣服和头形都独立；共用的只有走路关节与像素描边约定。
PEOPLE = {
    'fake_tennille': ('伪提尼尔船长', 'captain', (230,230,220), (42,64,104), (30,34,48), 48),
    'anne': ('安', 'girlcap', (222,154,78), (100,110,154), (122,64,38), 32),
    'devo': ('诅咒的迪波', 'devo', (78,116,102), (78,52,72), (50,34,42), 46),
    'rubbersoul': ('拉巴索', 'rubber', (228,214,172), (164,126,42), (60,46,38), 48),
    'nena': ('妮娜', 'nena', (212,70,118), (134,42,92), (66,32,64), 46),
    'zz': ('ZZ', 'zz', (216,178,106), (98,62,48), (72,48,38), 34),
    'cameo': ('卡蜜欧', 'turban', (184,104,78), (104,44,48), (54,32,36), 46),
    'chaka': ('恰卡', 'chaka', (206,172,118), (102,78,72), (40,32,28), 46),
    'khan': ('可汗', 'khan', (228,212,176), (112,96,90), (56,46,34), 44),
    'kennyg': ('肯尼G', 'kenny', (164,118,166), (82,42,114), (52,30,54), 48),
    'nukesaku': ('努凯萨克', 'vampire', (74,124,114), (32,62,74), (114,84,56), 44),
    'wilson': ('威尔逊·菲利普斯议员', 'senator', (94,106,132), (44,52,76), (168,154,132), 44),
    'npc_sailor': ('水手', 'deckhand', (234,232,220), (164,136,88), (60,42,30), 44),   # 条纹衫底色 / 卡其裤；由 art_new_npc_sailor.py 自己画（2026-10-11 不再套船长样式）
    'npc_kid': ('印度少年', 'kid', (228,148,54), (82,94,104), (44,30,24), 30),
    'npc_townsfolk': ('小镇居民', 'town', (154,138,96), (82,100,94), (94,72,54), 44),
    'npc_villager_f': ('亚普林村民', 'village', (210,158,94), (116,72,52), (70,46,34), 44),
    'npc_islander': ('岛上老人', 'islander', (178,142,88), (96,80,70), (206,198,174), 42),
    'npc_dealer': ('咖啡馆发牌员', 'dealer', (238,230,202), (42,78,68), (64,42,34), 44),
    'npc_spw': ('SPW财团工作人员', 'spw', (236,224,184), (112,98,74), (62,46,38), 46),
    'npc_merchant': ('埃及水果商人', 'merchant', (226,182,116), (100,120,104), (68,42,34), 44),
    'polnareff_kid': ('幼年波鲁纳雷夫', 'polkid', (206,206,200), (118,146,164), (234,230,208), 28),
    'jotaro_kid': ('幼年承太郎', 'jotkid', (66,82,92), (40,50,66), (28,28,40), 30),
    'polnareff_possessed': ('被阿努比斯控制的波鲁纳雷夫', 'possessed', (214,214,208), (76,94,110), (234,230,208), 48),
    'clay_sherry': ('泥偶雪莉', 'claysherry', (164,116,82), (104,70,58), (122,80,54), 44),
    'clay_gold': ('泥偶阿布德尔', 'claygold', (164,116,82), (104,70,58), (122,80,54), 48),
    'clay_pol': ('泥偶波鲁纳雷夫', 'claypol', (164,116,82), (104,70,58), (122,80,54), 48),
    'atum': ('阿图姆神', 'atum', (216,112,132), (142,58,86), (220,126,148), 50),
}


def limb(d, pts, color, width=4):
    d.line(pts, fill=K, width=width+2)
    d.line(pts, fill=color, width=width)
    for x,y in pts:
        r=width//2
        d.rectangle((x-r,y-r,x+r,y+r),fill=color)


def head(style, hair, size=14, mouth=False, scared=False):
    im=Image.new('RGBA',(24,24)); d=ImageDraw.Draw(im)
    skin=(184,132,94,255) if style in ('devo','chaka','town','islander') else S
    if style.startswith('clay'): skin=(174,126,92,255)
    d.ellipse((6,5,18,18),fill=skin,outline=K)
    d.polygon([(16,10),(21,12),(18,14),(17,17),(10,19),(7,15)],fill=skin,outline=K)
    d.rectangle((7,12,9,15),fill=SD if not style.startswith('clay') else (112,76,58))
    d.line((13,10,17,10),fill=K); d.point((16,11),fill=WHITE)
    d.line((14,16,18,16),fill=K)
    if mouth: d.rectangle((14,16,18,17),fill=(112,40,48)); d.line((14,16,17,16),fill=WHITE)
    if scared: d.rectangle((13,10,18,12),fill=WHITE); d.point((17,11),fill=K); d.rectangle((15,15,17,18),fill=K)
    if style in ('captain','sailor','jotkid'):
        d.rectangle((4,3,18,8),fill=WHITE if style!='jotkid' else (24,30,42),outline=K)
        d.rectangle((4,7,20,9),fill=(32,48,70),outline=K)
        d.rectangle((10,4,13,6),fill=GOLD); d.line((16,9,22,9),fill=K,width=2)
        if style=='captain': d.rectangle((8,14,11,17),fill=(82,60,44)); d.rectangle((11,18,17,19),fill=(82,60,44))
    elif style=='girlcap':
        d.polygon([(4,7),(6,2),(13,0),(19,3),(20,8)],fill=(212,148,80),outline=K)
        d.rectangle((2,7,21,9),fill=(242,190,110),outline=K)
        d.polygon([(4,10),(7,10),(8,18),(5,22),(3,18)],fill=hair,outline=K)
    elif style in ('polkid','possessed','claypol'):
        d.polygon([(5,8),(4,0),(16,0),(19,7),(17,9)],fill=hair,outline=K)
        for x in range(6,18,3): d.line((x,1,x+1,7),fill=(156,152,156) if style!='claypol' else (104,72,58))
        if style=='possessed': d.line((13,11,18,11),fill=(236,76,66))
    elif style=='turban':
        d.polygon([(4,8),(5,2),(10,0),(17,1),(20,6),(18,9)],fill=(242,218,166),outline=K)
        for y in (3,5,7): d.line((6,y,18,y+1),fill=(168,116,78))
        d.polygon([(5,8),(7,10),(5,22),(2,23)],fill=(224,194,142),outline=K)
        d.line((12,17,17,18),fill=(52,34,34),width=2)
    elif style=='devo':
        d.polygon([(4,7),(3,3),(8,1),(14,3),(19,5),(17,8)],fill=hair,outline=K)
        d.line((7,12,12,16),fill=(116,58,56),width=2)
        d.line((13,9,17,12),fill=(164,58,58)); d.line((8,16,13,18),fill=(56,44,40),width=2)
    elif style=='rubber':
        d.polygon([(4,8),(3,3),(7,0),(10,3),(13,0),(16,2),(20,2),(18,8)],fill=(224,194,62),outline=K)
        d.rectangle((11,10,19,12),fill=(80,54,54)); d.line((12,10,18,10),fill=(204,168,84))
    elif style in ('nena','village','claysherry'):
        d.polygon([(3,18),(3,7),(5,2),(11,0),(18,3),(20,10),(18,21),(16,18),(17,9),(12,6),(8,10),(7,22)],fill=hair,outline=K)
        d.ellipse((5,14,7,17),fill=GOLD)
        d.line((13,10,18,10),fill=K); d.line((14,16,18,16),fill=(164,36,74))
    elif style in ('zz','kenny'):
        d.polygon([(3,7),(3,2),(7,4),(9,0),(12,3),(17,1),(20,5),(18,8)],fill=hair,outline=K)
        if style=='kenny':
            d.rectangle((10,10,19,13),fill=(92,130,158),outline=K); d.line((10,10,18,10),fill=(180,214,214))
        else: d.line((12,15,19,15),fill=K,width=2)
    elif style=='chaka':
        d.polygon([(3,8),(4,3),(8,1),(16,1),(19,5),(17,8),(12,6),(7,10)],fill=hair,outline=K)
        d.rectangle((4,8,6,18),fill=hair)
    elif style=='khan':
        d.rectangle((4,3,18,7),fill=(232,224,198),outline=K)
        d.line((11,16,19,16),fill=hair,width=3); d.line((7,8,9,8),fill=hair)
    elif style=='vampire':
        d.polygon([(4,8),(3,2),(10,0),(17,2),(20,7),(17,8)],fill=hair,outline=K)
        d.line((13,10,19,10),fill=(228,74,74)); d.point((14,17),fill=WHITE); d.point((17,17),fill=WHITE)
        d.rectangle((4,12,7,15),fill=(196,144,96),outline=K)
    elif style=='senator':
        d.arc((5,4,18,17),175,270,fill=hair,width=2)
        d.rectangle((9,10,13,12),outline=(118,120,132)); d.rectangle((15,10,19,12),outline=(118,120,132))
        d.line((13,11,15,11),fill=(118,120,132))
    elif style=='islander':
        d.polygon([(0,7),(12,0),(23,7)],fill=(198,170,104),outline=K)
        d.line((3,6,20,6),fill=(130,102,66)); d.polygon([(10,17),(18,17),(14,23)],fill=WHITE,outline=K)
    elif style=='claygold':
        for x in (2,4,6): d.line((x,6,x-1,20),fill=hair,width=2)
        d.rectangle((6,5,18,7),fill=(106,72,58)); d.line((13,11,18,11),fill=(74,42,36))
    elif style=='atum':
        d.polygon([(4,8),(5,2),(9,0),(19,1),(20,8),(18,18),(10,20),(5,14)],fill=(218,130,150),outline=K)
        d.rectangle((8,5,18,8),fill=(224,220,176),outline=K); d.ellipse((13,9,18,14),fill=(160,184,188),outline=K)
        d.line((8,12,11,15),fill=(248,190,196)); d.line((12,17,18,17),fill=(112,50,76))
    elif style=='spw':
        d.rectangle((5,2,18,7),fill=(234,220,176),outline=K); d.polygon([(1,7),(21,7),(23,9),(0,9)],fill=(186,166,118),outline=K)
        d.line((8,5,18,5),fill=(84,100,96)); d.rectangle((10,10,18,12),outline=K)
        d.line((13,10,13,12),fill=K); d.line((5,15,9,18),fill=(82,58,42),width=2)
    elif style=='merchant':
        d.polygon([(3,7),(5,1),(16,0),(20,6),(18,9),(4,9)],fill=(240,222,176),outline=K)
        d.line((5,3,17,3),fill=(154,128,90)); d.line((4,6,19,6),fill=(190,164,118))
        d.polygon([(9,17),(17,16),(15,22),(10,23)],fill=(72,46,38),outline=K)
    else:
        d.polygon([(5,8),(5,3),(9,1),(16,2),(18,6),(13,7),(8,9)],fill=hair,outline=K)
    return im


def body(cid, action='idle', fi=0):
    zh,style,coat,pants,hair,h=PEOPLE[cid]
    w=40 if style in ('zz','claygold') else 36
    im=Image.new('RGBA',(w,h)); d=ImageDraw.Draw(im)
    child=h<=32; hx=w//2; head_y=0 if child else 1
    hh=17 if child else 21
    top=hh-3; hip=h-14; ground=h-2
    # 矮个子（三个小孩、安、ZZ）：hip = h−14 落在肩线上甚至更高，躯干只剩 0–2 行被头整个盖住、腿直接挂在下巴下面、
    # 手臂终点比肩还高（折成 V 形）。头身审计（2026-10-09 晚，audit_heads.py）后给躯干留至少 6 行；高个子不受影响。
    short=hip<top+6
    if short: hip=top+6
    bob=(fi%2) if action in ('idle','walk','run','talk') else 0
    leaning=-3 if action=='hurt' else (3 if action in ('slash','attack','grab','punch') else 0)
    x=hx+leaning
    skin=(184,132,94) if style in ('devo','chaka','town','islander') else S
    if style.startswith('clay'): skin=(174,126,92)
    if style=='nena' and action=='true_form':
        # 真面目用独立的肥硕剪影，不能让揭露镜头仍然是普通女性站姿。
        out=Image.new('RGBA',(48,46)); q=ImageDraw.Draw(out)
        q.ellipse((7,7,40,40),fill=(28,20,34),outline=K)
        q.polygon([(10,15),(4,20),(1,33),(8,35),(14,25),(35,25),(43,35),(47,32),(43,20),(38,15)],fill=(28,20,34),outline=K)
        q.ellipse((13,0,35,20),fill=(28,20,34)); q.polygon([(12,3),(6,6),(12,10),(35,10),(41,5),(33,2)],fill=(28,20,34))
        q.rectangle((12,34,20,44),fill=(28,20,34)); q.rectangle((28,34,37,44),fill=(28,20,34))
        q.line((20,9,24,9),fill=(248,226,176)); q.line((29,9,32,9),fill=(248,226,176))
        q.line((22,15,30,15),fill=(226,182,124)); return out
    if action=='down':
        # 倒地重新画腰、膝和衣襟，保留头朝左的读图方向；不把站立全身旋转成厚砖。
        out=Image.new('RGBA',(h+12,22)); q=ImageDraw.Draw(out)
        limb(q,[(23,14),(35,16),(h+2,18)],pants,5)
        limb(q,[(26,12),(38,9),(h+3,15)],tuple(int(c*.7) for c in pants),4)
        q.rectangle((h+1,14,h+8,19),fill=K); q.line((h+2,15,h+7,15),fill=(114,92,68))
        q.polygon([(12,10),(28,10),(32,18),(12,19)],fill=coat,outline=K)
        limb(q,[(17,12),(21,18),(29,17)],skin,3)
        hd=head(style,hair,scared=True).crop((0,0,24,24)).transpose(Image.Transpose.ROTATE_90)
        out.alpha_composite(hd,(0,-2))
        return out
    stride=(-3,0,3,0)[fi%4] if action in ('walk','run') else 0
    if action=='run': stride*=2
    near=(x+3,hip,x+3+stride,ground-1); far=(x-4,hip,x-4-stride,ground-2)
    limb(d,[(far[0],far[1]),(far[2],far[3])],tuple(int(c*.72) for c in pants),3 if child else 4)
    limb(d,[(near[0],near[1]),(near[2],near[3])],pants,3 if child else 4)
    for xx,yy in ((far[2],far[3]),(near[2],near[3])):
        d.rectangle((xx-2,yy,xx+4,yy+1),fill=(54,44,42),outline=K)
    broad=8 if style in ('zz','devo','claygold') else 6
    d.polygon([(x-broad,top+bob),(x+broad,top+bob),(x+7,hip),(x-7,hip)],fill=coat,outline=K)
    d.line((x-broad+2,top+2+bob,x-4,hip-2),fill=tuple(min(255,int(c*1.2+12)) for c in coat))
    d.line((x+5,top+3+bob,x+5,hip-1),fill=tuple(int(c*.68) for c in coat))
    if style in ('captain','sailor','dealer','senator','spw'):
        d.polygon([(x-3,top),(x+4,top),(x,top+8)],fill=WHITE,outline=K)
        if style=='senator': d.line((x,top+2,x+1,hip-3),fill=(164,58,66),width=2)
        if style=='dealer': d.rectangle((x-6,top+5,x+6,hip),fill=(34,70,62),outline=K)
        if style=='spw':
            d.rectangle((x+1,top+7,x+5,top+11),fill=(242,236,204),outline=K)
            d.line((x-4,top+3,x-4,hip-1),fill=(124,114,84),width=2)
        if style=='captain':
            for yy in range(top+9,hip,4): d.point((x+1,yy),fill=GOLD); d.point((x+4,yy),fill=GOLD)
            d.line((x-7,top+1,x-3,top+1),fill=GOLD,width=2)
    elif style in ('nena','village','claysherry'):
        d.polygon([(x-5,hip-5),(x+5,hip-5),(x+10,hip+6),(x-9,hip+6)],fill=coat,outline=K)
        for xx in range(x-6,x+7,4): d.line((xx,hip,xx+1,hip+4),fill=tuple(int(c*.75) for c in coat))
        if style=='nena': d.line((x-3,top+4,x+4,top+4),fill=GOLD,width=2)
    elif style in ('turban','chaka','islander','merchant'):
        d.polygon([(x-6,hip-6),(x+6,hip-6),(x+8,hip+4),(x-8,hip+4)],fill=coat,outline=K)
        d.line((x-5,hip-6,x+6,hip-6),fill=(214,184,126),width=2)
    elif style in ('possessed','claypol','polkid'):
        d.line((x-5,top+2,x-5,hip-2),fill=(70,84,96),width=2); d.line((x+4,top+2,x+4,hip-2),fill=(70,84,96),width=2)
    elif style=='kenny':
        for yy in range(top+4,hip,5): d.rectangle((x-5,yy,x+5,yy+1),fill=(80,46,112))
    elif style=='devo':
        d.line((x-5,top+2,x+5,hip-1),fill=(184,142,94),width=3); d.line((x-5,top+2,x+5,hip-1),fill=K)
    elif style=='atum':
        d.ellipse((x-4,top+3,x+4,top+11),fill=(226,216,164),outline=K)
        d.ellipse((x-2,top+5,x+2,top+9),fill=(142,72,100))
        for xx in (x-7,x+7): d.ellipse((xx-2,top-1,xx+2,top+3),fill=(236,206,150),outline=K)
    arms_width=7 if style=='zz' else (4 if not child else 3)
    ay=top+4+bob; arm_end=hip-1
    if short: arm_end=max(arm_end,ay+6)      # 手垂到大腿，不再往上折回肩膀
    attacking=action in ('attack','slash','grab','punch','wave','deal')
    if attacking:
        ty=top+2+(fi%2)*7
        limb(d,[(x+6,ay),(x+11,ay+3),(w-4,ty)],coat if style not in ('zz','nena','devo','possessed') else skin,arms_width)
        d.rectangle((w-5,ty-2,w-2,ty+1),fill=skin,outline=K)
        if action=='slash' or style in ('chaka','khan','possessed') and action=='attack':
            d.line((w-3,ty,w-2,2 if fi%2==0 else hip),fill=K,width=3)
            d.line((w-3,ty,w-2,2 if fi%2==0 else hip),fill=(222,224,214),width=1)
        if action=='deal': d.rectangle((w-8,ty-2,w-2,ty+2),fill=WHITE,outline=K); d.point((w-5,ty),fill=(170,46,50))
    elif action in ('hurt','shock','beg','hide'):
        limb(d,[(x+6,ay),(x+10,ay+4),(x+7,top-1)],skin,3)
    else:
        swing=-stride//2
        limb(d,[(x+6,ay),(x+8,ay+5),(x+7+swing,arm_end)],coat if style not in ('zz','nena','devo','possessed','polkid') else skin,arms_width)
        d.rectangle((x+6+swing,arm_end-1,x+8+swing,arm_end+1),fill=skin,outline=K)
    limb(d,[(x-6,ay),(x-8,ay+6),(x-8+stride//2,arm_end)],tuple(int(c*.72) for c in coat),max(2,arms_width-1))
    hd=head(style,hair,mouth=action=='talk' or (fi%2==1 and action=='portrait'),scared=action in ('hurt','shock'))
    if child: hd=hd.resize((20,20),Image.Resampling.NEAREST)
    im.alpha_composite(hd,(x-hd.width//2,head_y+bob))
    if style=='vampire' and action=='reverse':
        # 背后的女性脸有独立发型、眼睛和嘴，区别于把吸血鬼脸镜像翻转。
        rev=head('nena',(120,80,48),mouth=bool(fi)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        im.alpha_composite(rev,(x-12,head_y+bob))
    if action=='reveal' and style=='captain':
        q=ImageDraw.Draw(im); q.rectangle((x-4,head_y+6,x+4,head_y+8),fill=(30,34,48)); q.line((x+1,head_y+13,x+6,head_y+13),fill=(240,226,188))
    if action=='beg':
        q=ImageDraw.Draw(im); q.line((x-3,top+6,x+5,top+9),fill=skin,width=3); q.line((x+5,top+9,x+7,top+5),fill=skin,width=3)
    if action=='hide':
        q=ImageDraw.Draw(im); q.line((x-4,top+3,x+2,head_y+9),fill=skin,width=3); q.line((x+6,top+3,x+5,head_y+9),fill=skin,width=3)
    if style=='kenny':
        # 乐器是辨认肯尼G的轮廓，不只通过衣服颜色区分。
        d=ImageDraw.Draw(im); d.line((x+8,top+4,x+12,hip-1,x+9,hip+2),fill=K,width=5)
        d.line((x+8,top+4,x+12,hip-1,x+9,hip+2),fill=GOLD,width=3)
        d.arc((x+6,hip-2,x+14,hip+4),0,170,fill=GOLD,width=3)
    return im


def portrait(cid,fi=0,expression='portrait'):
    _,style,coat,pants,hair,h=PEOPLE[cid]
    out=Image.new('RGBA',(32,32)); d=ImageDraw.Draw(out)
    d.polygon([(1,31),(6,23),(14,21),(24,23),(30,31)],fill=coat,outline=K)
    face='nena' if expression=='portrait_reverse' and style=='vampire' else style
    hd=head(face,hair,mouth=bool(fi),scared=expression in ('portrait_scared','portrait_reveal')).resize((30,30),Image.Resampling.NEAREST)
    out.alpha_composite(hd,(1,-1))
    if expression=='portrait_angry':
        d=ImageDraw.Draw(out); d.line((16,11,22,14),fill=K,width=2); d.line((18,20,24,19),fill=K)
    return out


def register(cid, actions=None):
    actions=actions or {'idle':2,'walk':4,'talk':2,'hurt':1,'down':1,'portrait':2}
    names=[]
    for action,n in actions.items():
        fn=portrait if action.startswith('portrait') else body
        frames=[fn(cid,i,action) if action.startswith('portrait') else fn(cid,action,i) for i in range(n)]
        name=cid+'.'+action
        sprite.define(name,frames,anchor='mm' if action.startswith('portrait') else 'mb',fps=6 if action in ('walk','run') else 3,desc=PEOPLE[cid][0]+'：'+action)
        names.append(name)
    return names
