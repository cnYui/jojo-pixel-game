"""第三部后续背景：原分层素材与新场景共用导出协议，宽地图保留真实世界坐标。"""
import sys
sys.dont_write_bytecode = True

import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
from engine import bg_asia as A, bg_egypt as E

W,H=320,180
K=(32,28,46,255)


def new(w=320,h=180,col=None):
    return Image.new('RGBA',(w,h),col or (0,0,0,0))


def sky(kind='day'):
    pal={
      'day':[(88,150,212),(154,204,234),(242,228,194)],
      'noon':[(116,174,222),(182,212,230),(250,232,192)],
      'night':[(8,8,26),(26,26,64),(56,42,82)],
      'dawn':[(28,22,60),(118,62,120),(246,164,124)],
      'sunrise':[(88,108,176),(236,146,118),(255,230,156)],
      'sea':[(96,172,216),(178,214,234),(230,230,214)]
    }[kind]
    im=new(col=pal[0]+(255,)); d=ImageDraw.Draw(im)
    for y in range(H):
        q=y/(H-1)*2; a=pal[min(1,int(q))]; b=pal[min(2,int(q)+1)]; u=q-int(q)
        c=tuple(round(a[i]+(b[i]-a[i])*u) for i in range(3))+(255,)
        d.line((0,y,W,y),fill=c)
    if kind=='night':
        for i in range(46): d.point(((i*59+31)%W,(i*23+11)%87),fill=(202,198,226))
        d.ellipse((255,16,273,34),fill=(240,224,188)); d.ellipse((251,13,268,31),fill=(16,16,42))
    elif kind in ('dawn','sunrise'):
        d.ellipse((251,77 if kind=='dawn' else 46,273,99 if kind=='dawn' else 68),fill=(255,220,136))
    else:
        d.ellipse((256,15,274,33),fill=(255,242,196))
    return im


def floor(im,y,col=(164,138,112),tile=24):
    d=ImageDraw.Draw(im); w=im.width
    d.rectangle((0,y,w,H),fill=col+(255,)); dark=tuple(max(0,c-24) for c in col)
    d.line((0,y,w,y),fill=dark)
    for yy in range(y+7,H,8):
        d.line((0,yy,w,yy),fill=dark)
        for xx in range((yy//8%2)*tile//2,w,tile): d.line((xx,yy-7,xx,yy),fill=dark)


def pillar(d,x,y,h,col=(182,160,122),width=14):
    d.rectangle((x,y,x+width,y+h),fill=col,outline=K)
    d.rectangle((x-3,y-2,x+width+3,y+3),fill=tuple(min(255,c+22) for c in col),outline=K)
    d.rectangle((x-3,y+h-3,x+width+3,y+h+2),fill=col,outline=K)
    d.line((x+3,y+4,x+3,y+h-5),fill=tuple(min(255,c+32) for c in col))


def window(d,x,y,w,h,col=(102,148,168),arch=False):
    d.rectangle((x,y,x+w,y+h),fill=col,outline=K,width=2)
    if arch: d.pieslice((x,y-w//2,x+w,y+w//2),180,360,fill=col,outline=K)
    d.line((x+w//2,y,x+w//2,y+h),fill=K)
    d.line((x,y+h//2,x+w,y+h//2),fill=K)


def door(d,x,y,w,h,col=(102,70,54)):
    d.rectangle((x,y,x+w,y+h),fill=col,outline=K,width=2)
    d.rectangle((x+4,y+5,x+w-4,y+h//2),outline=tuple(min(255,c+32) for c in col))
    d.point((x+w-5,y+h//2+8),fill=(234,204,112))


def waves(fi,color=(148,204,218),y0=103,region=None,blocked=()):
    im=new(); d=ImageDraw.Draw(im)
    for y in range(y0,134,5):
        for x in range(-24,W,32):
            xx=(x+fi*4+(y//5%2)*8)%344-24
            d.line((xx,y,xx+12,y),fill=color)
    if region:
        mask=Image.new('L',(W,H)); md=ImageDraw.Draw(mask)
        md.rectangle(region,fill=255)
        for box in blocked: md.rectangle(box,fill=0)
        im.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel('A')),np.array(mask))))
    return im


def wrap(im,k=1,y=0,vx=0,period=None,name='layer'):
    return dict(type='wrap',src=im,k=k,y=y,vx=vx,period=period or im.width,name=name)


def pano(im,k=1,x=0,y=0,name='layer'):
    return dict(type='pano',src=im,k=k,x=x,y=y,name=name)


def static(im,name='base'):
    return dict(type='static',src=im,name=name)


def strip(fn,name='motion',key=None):
    return dict(type='strip',fn=fn,name=name,key=key)


@lru_cache(maxsize=1)
def desert_parts():
    return {t:(E._desert_far(t).crop((0,0,640,90)),E._desert_mid(t).crop((0,0,640,64)),
               E._desert_near(t,top=150)[0].crop((0,0,640,38))) for t in ('day','noon','night')}


def desert(kind='day',speed=0):
    far,mid,near=desert_parts()[kind]
    return [static(sky(kind)),wrap(far,.12,66,speed*.12,name='far_dunes'),
            wrap(mid,.4,98,speed*.4,name='mid_dunes'),wrap(near,1,142,speed,name='near_sand')]


def town(seed,w=960,variant='egypt'):
    near=E._town_layers(seed).crop((0,0,w,H))
    ground=E._town_ground(seed).crop((0,0,w,40))
    if variant=='village':
        a=np.array(near); a[:,:,:3]=np.clip(a[:,:,:3]*[1.08,.97,.85],0,255); near=Image.fromarray(a)
        d=ImageDraw.Draw(near)
        for x in range(30,w,110):
            d.rectangle((x,95,x+32,151),fill=(174,122,70),outline=K)
            d.polygon([(x-8,95),(x+15,68),(x+41,95)],fill=(126,94,58),outline=K)
            door(d,x+10,115,13,36)
    return [static(sky()),wrap(E._town_far(seed+4).crop((0,0,640,116)),.3,name='distant_town'),
            pano(near,name='mudbrick_and_market'),pano(ground,y=140,name='street_floor')]


def city_street(w=960,variant='singapore'):
    im=new(w); d=ImageDraw.Draw(im)
    palettes={'singapore':[(246,226,170),(224,174,170),(164,206,190),(194,190,224)],
              'karachi':[(216,190,150),(176,186,142),(210,160,128),(170,190,200)],
              'varanasi':[(220,184,112),(180,146,134),(196,154,88),(206,182,160)]}
    pal=palettes[variant]
    for i,x in enumerate(range(0,w,92)):
        c=pal[i%4]; top=22+(i*17)%23
        d.rectangle((x,top,x+88,150),fill=c,outline=K)
        d.rectangle((x-1,top-4,x+89,top),fill=tuple(max(0,v-40) for v in c),outline=K)
        for yy in (top+10,top+42):
            for xx in (x+10,x+48):
                window(d,xx,yy,22,26,arch=variant=='singapore')
        door(d,x+33,109,24,41)
        d.rectangle((x+3,91,x+83,103),fill=(40,76,88),outline=K)
        for z in range(x+9,x+76,9): d.rectangle((z,95,z+3,98),fill=(242,228,170))
        d.polygon([(x+4,107),(x+84,107),(x+88,119),(x,119)],fill=(170,68,74),outline=K)
        for xx in range(x+8,x+84,12): d.line((xx,108,xx-2,118),fill=(238,200,140),width=3)
        if variant=='singapore':
            pillar(d,x+5,121,29,(218,202,180),4); pillar(d,x+76,121,29,(218,202,180),4)
        if i%3==0:
            d.line((x+86,148,x+90,78),fill=(88,74,54),width=3)
            for dx,dy in ((-18,4),(-12,-8),(12,-9),(22,1)):
                d.line((x+90,79,x+90+dx,79+dy),fill=(54,118,80),width=3)
    floor(im,150,(154,154,144),32)
    d=ImageDraw.Draw(im)
    for xx in range(0,w,48): d.line((xx,171,xx+21,171),fill=(228,220,176),width=2)
    far=E._town_far(17).crop((0,0,640,116))
    return [static(sky()),wrap(far,.2,name='far_city'),pano(im,name=variant+'_facades')]


def room(kind,w=320):
    colors={'hotel':((196,192,162),(130,94,76)), 'inn':((146,124,120),(92,66,68)),
            'corridor':((52,44,80),(58,46,68)), 'illusion':((76,36,104),(70,34,96)),
            'house':((218,196,164),(166,128,100)), 'tower':((44,38,62),(74,54,68)),
            'submarine':((104,144,140),(72,104,106)), 'freighter':((148,158,162),(92,112,116))}
    wall,fl=colors[kind]; im=new(w,col=wall+(255,)); d=ImageDraw.Draw(im)
    floor(im,144,fl)
    d=ImageDraw.Draw(im); d.rectangle((0,0,w,10),fill=tuple(max(0,c-24) for c in wall))
    d.line((0,131,w,131),fill=K,width=3)
    if kind=='hotel':
        window(d,190,24,82,63,(90,166,190)); d.rectangle((185,22,190,100),fill=(144,70,92))
        d.rectangle((272,22,277,100),fill=(144,70,92))
        d.rectangle((35,37,112,53),fill=(124,90,64),outline=K)
        d.rectangle((34,107,144,143),fill=(174,150,112),outline=K)
        d.polygon([(34,104),(135,99),(145,111),(35,119)],fill=(236,230,198),outline=K)
        d.rectangle((38,101,73,112),fill=(252,242,216),outline=(180,174,156))
        d.rectangle((164,111,226,119),fill=(116,78,60),outline=K); d.line((170,119,170,151),fill=K,width=3)
        d.line((220,119,220,151),fill=K,width=3); d.rectangle((248,114,286,142),fill=(68,54,64),outline=K)
        d.rectangle((252,110,282,115),fill=(118,78,54)); door(d,2,45,22,99)
    elif kind=='inn':
        for x in (22,100,182,260): door(d,x,42,36,96,(78,52,60))
        d.rectangle((104,109,210,120),fill=(96,66,60),outline=K)
        for x in (110,200): d.line((x,119,x,153),fill=K,width=3)
        for x in (75,233):
            d.rectangle((x,95,x+10,145),fill=(112,72,58),outline=K)
            d.rectangle((x-3,126,x+17,132),fill=(96,60,52),outline=K)
        d.rectangle((138,25,180,60),fill=(82,72,86),outline=(184,156,128),width=3)
    elif kind in ('corridor','illusion'):
        for i,x in enumerate(range(18,w,128)):
            pillar(d,x,19,125,(92,74,116),12); door(d,x+38,47,42,94,(40,32,62))
            d.pieslice((x+36,25,x+82,71),180,360,fill=(34,28,54),outline=(118,94,142))
            d.rectangle((x+25,23,x+28,30),fill=(236,208,116))
        d.rectangle((0,151,w,163),fill=(94,44,74)); d.line((0,151,w,151),fill=(172,112,112))
        if kind=='illusion': im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    elif kind=='tower':
        for x in range(0,w,32):
            for y in range(12,140,16): d.rectangle((x+(y//16%2)*16,y,x+30+(y//16%2)*16,y+14),outline=(74,64,96))
        window(d,135,26,50,74,(8,10,26),arch=True)
        d.polygon([(87,144),(100,112),(211,112),(230,144)],fill=(32,24,42),outline=(134,108,86),width=2)
        d.polygon([(94,142),(105,115),(206,115),(223,142)],fill=(92,46,52),outline=K)
        for x in (31,272):
            pillar(d,x,33,112,(96,82,110),14)
            d.line((x+6,33,x+6,24),fill=(224,202,148)); d.ellipse((x+3,18,x+9,25),fill=(250,210,118))
    elif kind=='submarine':
        for x in range(0,w,80):
            d.line((x,9,x,135),fill=(36,72,80),width=3)
            d.ellipse((x+19,36,x+59,76),fill=(30,70,100),outline=(184,192,166),width=4)
            for xx,yy in ((x+24,43),(x+51,43),(x+24,68),(x+51,68)): d.point((xx,yy),fill=K)
            d.line((x+15,11,x+15,27,x+62,27),fill=(54,82,86),width=4)
        d.rectangle((20,94,118,130),fill=(58,92,98),outline=K)
        for x in range(29,114,17):
            d.ellipse((x,100,x+10,110),fill=(184,194,172),outline=K)
            d.line((x+5,105,x+7,102),fill=K)
        for x in range(360,w,96):
            d.rectangle((x,116,x+62,143),fill=(70,100,100),outline=K)
            d.rectangle((x+6,119,x+56,135),fill=(134,166,150),outline=K)
        door(d,260,35,48,104,(58,90,94)); d.ellipse((273,81,297,105),outline=(202,206,178),width=3)
    elif kind=='freighter':
        for x in range(0,w,96):
            d.rectangle((x+4,20,x+80,138),outline=(64,84,90),width=2)
            door(d,x+16,43,42,98,(68,92,102))
            d.ellipse((x+27,58,x+47,78),fill=(26,58,72),outline=(172,186,182),width=3)
            d.line((x+2,14,x+90,14),fill=(52,74,84),width=3)
            d.rectangle((x+36,20,x+58,24),fill=(224,218,170))
    elif kind=='house':
        # 藏点使用独立开合道具；底图留空才能在打开时真实露出内部。
        window(d,26,34,64,64,(148,188,192))
        for y in range(17,130,14):
            for x in range((y//14%2)*30,w,60):
                d.line((x,y,x+27,y),fill=(206,181,150)); d.line((x+27,y,x+27,y+6),fill=(206,181,150))
        d.rectangle((108,24,139,43),fill=(114,76,64),outline=K)
        d.rectangle((111,27,136,40),fill=(216,176,122),outline=(232,204,156))
        d.polygon([(112,39),(121,30),(129,36),(136,31),(136,40)],fill=(106,134,108))
        d.rectangle((323,0,328,144),fill=(144,114,94)); door(d,297,43,21,101)
        if w>320:
            window(d,529,33,59,56,(144,184,194)); door(d,605,42,29,102)
            d.line((340,20,516,20),fill=(174,142,112)); d.line((340,23,516,23),fill=(238,214,180))
    return im


def rail_front(w=320):
    im=new(w); d=ImageDraw.Draw(im)
    d.line((0,145,w,145),fill=(70,86,104),width=3)
    d.line((0,151,w,151),fill=(184,196,188))
    for x in range(8,w,26): d.line((x,144,x,166),fill=(96,110,120),width=2)
    return im


def yacht():
    im=sky('sea'); d=ImageDraw.Draw(im)
    d.rectangle((0,93,320,128),fill=(62,130,166)); d.line((0,94,320,94),fill=(208,224,220))
    d.rectangle((0,127,320,180),fill=(204,176,130))
    for y in range(132,180,6): d.line((0,y,320,y),fill=(148,116,82))
    for x in range(0,320,40): d.line((x,128,x,180),fill=(172,140,100))
    d.polygon([(198,128),(205,58),(300,58),(317,128)],fill=(234,230,208),outline=K)
    window(d,214,71,76,38,(76,148,174)); d.rectangle((210,111,294,123),fill=(242,238,218),outline=K)
    d.line((167,18,167,129),fill=(88,100,102),width=3)
    d.polygon([(165,23),(165,97),(102,95)],fill=(250,244,212),outline=(172,172,164))
    d.ellipse((34,112,61,139),fill=(220,66,54),outline=K,width=3); d.ellipse((41,119,54,132),fill=(230,222,180))
    return im


def ghat():
    w=640; far=new(w); d=ImageDraw.Draw(far)
    for i,x in enumerate(range(0,w,62)):
        c=((194,144,106),(214,176,120),(164,138,134))[i%3]
        d.rectangle((x,65-(i%3)*11,x+59,126),fill=c,outline=K)
        d.polygon([(x+4,65-(i%3)*11),(x+28,22-(i%3)*8),(x+53,65-(i%3)*11)],fill=(188,124,86),outline=K)
        for xx in range(x+7,x+54,14): window(d,xx,82,8,17,(76,68,76))
        d.line((x+28,22-(i%3)*8,x+28,15-(i%3)*8),fill=(216,180,80))
    near=new(w); d=ImageDraw.Draw(near)
    for y in range(125,168,6):
        d.rectangle((0,y,w,y+5),fill=(180-(y-125)//3,146-(y-125)//3,108-(y-125)//3),outline=(108,86,74))
    d.rectangle((0,164,w,180),fill=(82,132,132))
    for x in range(13,w,110):
        d.polygon([(x,174),(x+12,169),(x+53,169),(x+65,174),(x+52,178),(x+10,178)],fill=(100,66,46),outline=K)
        d.line((x+34,169,x+34,147),fill=(96,76,60),width=2)
    return [static(sky()),pano(far,.45,name='ghat_temples'),pano(near,name='stone_steps_and_river')]


def brain():
    im=new(col=(60,28,60,255)); d=ImageDraw.Draw(im)
    for i in range(25):
        x=(i*83)%320; y=(i*29)%136
        d.ellipse((x-18,y-12,x+33,y+22),fill=(100+(i%3)*13,50+(i%2)*12,94),outline=(148,74,122),width=3)
        d.arc((x-12,y-8,x+27,y+17),20,280,fill=(64,34,74),width=2)
    d.rectangle((0,147,320,180),fill=(88,42,80)); d.line((0,149,320,149),fill=(164,84,122),width=2)
    for x in range(0,320,29): d.arc((x,138,x+36,169),180,360,fill=(182,96,126),width=3)
    return im


def temple():
    im=new(640); d=ImageDraw.Draw(im)
    d.rectangle((0,79,640,154),fill=(204,176,120),outline=(136,108,74))
    for y in range(83,154,14):
        for x in range((y//14%2)*20,640,40): d.rectangle((x,y,x+39,y+13),outline=(160,132,92))
    for x in (28,174,342,490):
        pillar(d,x,29,126,(214,192,144),31)
        d.rectangle((x+2,23,x+30,34),fill=(148,116,74),outline=K)
        for y in range(44,135,12):
            d.line((x+9,y,x+20,y+4),fill=(118,88,56),width=2)
            d.ellipse((x+13,y+2,x+17,y+7),outline=(118,88,56))
    door(d,232,74,63,80,(74,64,52)); door(d,554,72,49,82,(70,64,50))
    floor(im,153,(184,156,106))
    return [static(sky('noon')),wrap(E._desert_far('noon').crop((0,0,640,90)),.1,60,name='dune_horizon'),pano(im,name='temple_colonnade')]


def nile():
    far=new(640); d=ImageDraw.Draw(far)
    d.rectangle((0,100,640,148),fill=(52,126,150))
    for x in range(0,640,54):
        d.line((x,101,x+22,101),fill=(146,198,192))
        d.line((x+17,121,x+40,121),fill=(100,170,182))
    near=new(640); d=ImageDraw.Draw(near); floor(near,149,(190,166,118))
    d=ImageDraw.Draw(near)
    for x in range(20,640,91):
        d.line((x,149,x+5,95),fill=(116,82,58),width=3)
        for dx,dy in ((-20,0),(-13,-10),(13,-8),(23,2)):
            d.line((x+5,95,x+5+dx,95+dy),fill=(64,118,78),width=3)
        for xx in range(x+30,x+48,4): d.line((xx,152,xx-3,133),fill=(94,132,70))
    return [static(sky()),pano(E._town_far(25).crop((0,0,640,116)),.3,name='far_bank'),pano(far,.5,name='nile_water'),pano(near,name='bank_and_palms')]


def railway():
    near=new(640); d=ImageDraw.Draw(near); floor(near,146,(188,164,112))
    d=ImageDraw.Draw(near)
    for x in range(0,640,13): d.rectangle((x,157,x+5,179),fill=(98,78,56),outline=K)
    for y in (158,174): d.line((0,y,640,y),fill=(184,196,194),width=3); d.line((0,y+3,640,y+3),fill=(70,70,66))
    for x in (38,202,375,566):
        d.line((x,144,x,38),fill=(82,62,52),width=3); d.line((x-17,50,x+17,50),fill=(82,62,52),width=3)
        for xx in range(x-12,x+14,8): d.rectangle((xx,45,xx+3,51),fill=(182,190,174),outline=K)
    return desert()+[pano(near,name='rails_and_poles')]


def sewer():
    im=new(640,col=(30,40,44,255)); d=ImageDraw.Draw(im)
    for y in range(14,148,11):
        d.line((0,y,640,y),fill=(47,49,47))
        for x in range((y//11%2)*14,640,28): d.line((x,y-10,x,y),fill=(47,49,47))
    for i,x in enumerate(range(0,640,80)):
        d.pieslice((x-10,12,x+90,157),180,360,fill=(68,62,58),outline=(104,88,74),width=5)
        d.rectangle((x+4,78,x+70,144),fill=(28,36,40))
        pillar(d,x,52,102,(76,70,64),13)
        for y in range(62,145,12): d.line((x,y,x+13,y),fill=(50,48,48))
        d.rectangle((x+16,53,x+27,69),fill=(94,108,106),outline=K)
        d.ellipse((x+18,57,x+25,65),fill=(198,184,108))
    d.rectangle((0,148,640,180),fill=(38,74,72)); d.line((0,147,640,147),fill=(114,110,80),width=3)
    for x in range(0,640,26): d.line((x,165,x+11,165),fill=(62,104,98))
    d.rectangle((0,143,640,155),fill=(94,88,76)); d.rectangle((0,171,640,180),fill=(82,78,68))
    d.line((0,154,640,154),fill=(40,38,36)); d.line((0,171,640,171),fill=(124,116,90))
    return im


def beach(variant):
    im=E._beach_static('redsea' if variant=='island' else 'egypt').copy(); d=ImageDraw.Draw(im)
    # 岛屿与大陆海岸保留不同的礁石和入口标记。
    if variant=='island': d.rectangle((246,100,270,145),fill=(148,104,68),outline=K); d.polygon([(238,100),(258,81),(279,100)],fill=(108,84,58),outline=K)
    else: d.line((278,126,278,150),fill=(84,86,74),width=2); d.rectangle((278,126,300,137),fill=(220,206,170),outline=K)
    return im


def cairo(kind='day'):
    if kind=='day':
        main=E._street_day()[0].crop((0,0,960,H)); far=E._town_far(31).crop((0,0,640,116)); ground=E._street_ground('sunrise').crop((0,0,480,H))
    else:
        main=E._street_graded(kind).crop((0,0,960,H)); far=E._street_far(kind).crop((0,0,640,130)); ground=E._street_ground(kind).crop((0,0,480,H))
    return [static(sky(kind)),wrap(far,.3,name='cairo_far'),pano(main,name='cairo_buildings'),wrap(ground,name='cairo_road')]


def mouth():
    base,far,bed=A._uw_layers(); im=base.copy(); im.alpha_composite(far.crop((0,0,320,180))); im.alpha_composite(bed.crop((0,0,320,180)))
    d=ImageDraw.Draw(im); d.rectangle((0,155,320,180),fill=(136,74,104))
    for x in range(-5,320,27):
        d.polygon([(x,18),(x+21,17),(x+16,53),(x+9,57)],fill=(226,228,206),outline=(92,104,100))
        d.polygon([(x,164),(x+21,164),(x+17,132),(x+8,128)],fill=(236,236,214),outline=(92,104,100))
    d.arc((74,154,258,205),185,340,fill=(198,118,130),width=5)
    return im


def mountain():
    im=sky(); d=ImageDraw.Draw(im)
    for x,y in ((-40,64),(55,40),(160,57),(245,29)):
        d.polygon([(x,130),(x+48,y),(x+109,132)],fill=(130,126,128),outline=(74,88,106))
        d.polygon([(x+35,y+20),(x+48,y),(x+66,y+20)],fill=(208,218,218))
    d.polygon([(0,145),(72,133),(172,139),(320,156),(320,180),(0,180)],fill=(126,116,94))
    d.line((0,151,70,142,172,145,320,165),fill=(234,222,176),width=2)
    d.line((0,139,80,125,180,132,320,145),fill=(84,88,80),width=3)
    for x in range(20,320,35): d.line((x,132+x//30,x,148+x//30),fill=(138,144,128),width=3)
    return im


def cessna():
    im=sky(); d=ImageDraw.Draw(im)
    d.rectangle((0,0,320,24),fill=(226,218,188)); d.rectangle((0,98,320,152),fill=(128,142,130))
    d.rectangle((0,152,320,180),fill=(100,114,110))
    for x in (28,130,229):
        window(d,x,34,64,59,(158,198,216)); d.rectangle((x-7,121,x+65,145),fill=(124,96,74),outline=K)
        d.rectangle((x-6,99,x+10,133),fill=(144,114,84),outline=K)
    d.line((0,24,320,24),fill=(102,122,120),width=3); d.line((0,99,320,99),fill=(74,100,98),width=3)
    d.rectangle((282,67,319,133),fill=(66,86,92),outline=K)
    for x in (289,305): d.ellipse((x,80,x+10,90),fill=(204,216,198),outline=K)
    return im


def cablecar():
    im=sky('sea'); d=ImageDraw.Draw(im)
    d.rectangle((0,91,320,180),fill=(76,142,166))
    d.polygon([(0,102),(35,86),(59,113),(0,125)],fill=(66,116,94)); d.polygon([(261,106),(289,81),(320,91),(320,133)],fill=(54,106,82))
    d.rectangle((0,0,320,20),fill=(188,66,62)); d.rectangle((0,20,13,153),fill=(146,54,58))
    d.rectangle((305,20,320,153),fill=(146,54,58)); d.rectangle((151,20,164,153),fill=(170,58,60))
    d.rectangle((0,125,320,180),fill=(204,180,146)); d.rectangle((0,148,320,180),fill=(114,102,94))
    d.line((0,121,320,121),fill=(218,218,202),width=3); d.line((0,149,320,149),fill=K,width=3)
    for x in (28,186): d.rectangle((x,134,x+102,146),fill=(144,68,58),outline=K)
    d.rectangle((113,3,204,11),fill=(216,212,180),outline=K)
    return im


def train_layers():
    base,hills,mid,near=A._train_scenery()
    return [static(base),wrap(hills.crop((0,0,640,180)),.08,vx=8.8,name='outside_hills'),
            wrap(mid.crop((0,0,640,180)),.35,vx=38.5,name='outside_village'),
            wrap(near.crop((0,0,640,180)),1,vx=110,name='outside_fields'),static(A._train_static(),name='compartment')]


def bedroom_morning():
    # 保持空条宅既有像素画风，窗光在房间内独立重画。
    im=A._bedroom_static('morning').copy()
    light=new(); d=ImageDraw.Draw(light)
    d.polygon([(121,113),(192,113),(250,178),(82,178)],fill=(236,222,166,42))
    im.alpha_composite(light)
    return im


def motion(kind,fi):
    im=new(); d=ImageDraw.Draw(im)
    if kind=='bubbles':
        for i in range(11):
            x=18+i*27; y=(154-i*13-fi*5)%166+5; r=1+i%3
            d.ellipse((x-r,y-r,x+r,y+r),outline=(168,218,222,150))
    elif kind=='brain':
        for i in range(10):
            x=(31+i*43)%320; y=45+(i*29)%81
            d.line((x,y,x+8,y+2,x+13,y-3),fill=(216,138,182,90+fi*12),width=1)
    elif kind=='fog':
        for i in range(7):
            x=(i*53+fi*8)%410-70; y=108+i*9
            d.ellipse((x,y,x+100,y+17),fill=(170,162,186,24))
    elif kind=='flesh':
        for x in range(0,320,34):
            d.polygon([(x,32),(x+7,85),(x+3,121),(x+13,169)],fill=(130+fi*3,70,112,160))
            d.line((x+2,34,x+6,118,x+13,169),fill=(214,122,156,160),width=2)
    elif kind=='alarm':
        d.ellipse((147,8,173,24),fill=(242,74+fi*12,54,150))
    return im


def make(key):
    """返回图层配方及舞台坐标；每张新场景的结构和特征由专用绘制函数决定。"""
    g=152; w=320; anchors={}; fg=[]
    if key=='underwater':
        base,far,bed=A._uw_layers(); layers=[static(base),wrap(far,.3,name='far_rocks'),wrap(bed,name='seabed'),strip(lambda f:motion('bubbles',f),'bubbles')]
        w=640; g=156
    elif key=='yacht_deck':
        layers=[static(yacht()),strip(lambda f:waves(f,region=(0,95,196,125),blocked=((33,111,62,139),(164,18,170,129))),'sea_ripples')]
        fg=[pano(rail_front(),name='railing')]; anchors={'overboard':[90,155],'mast':[167,131]}
    elif key=='freighter_deck':
        layers=[static(sky('sea'),'sky'),static(A._freighter_static(),'freighter'),strip(lambda f:waves(f,region=(0,98,195,114),blocked=((0,104,70,130),(91,22,101,128),(149,109,163,123))),'sea_ripples')]
        fg=[pano(rail_front(),name='railing')]
    elif key=='freighter_corridor':
        layers=[pano(room('freighter',640),name='ship_passage'),strip(lambda f:motion('flesh',f),'living_ship','flesh')]; w=640; g=156
    elif key in ('singapore_street','karachi_street','varanasi_street'):
        variant={'singapore_street':'singapore','karachi_street':'karachi','varanasi_street':'varanasi'}[key]
        w=960 if key=='singapore_street' else 640; g=154; layers=city_street(w,variant)
    elif key=='singapore_hotel': layers=[static(room('hotel'))]; g=156; anchors={'bed':[86,143],'luggage':[267,143],'desk':[195,151]}
    elif key=='cable_car': layers=[static(cablecar())]; g=156; anchors={'window':[86,75],'door':[157,153]}
    elif key=='train_interior': layers=train_layers(); g=160; anchors={'seat_y':124,'bench_left':[80,124],'bench_right':[240,124]}
    elif key=='calcutta_street':
        w=1280; g=154; layers=city_street(w,'varanasi')
        # 后半段增加电车站与寺庙，宽1280世界不会重复一张640快照。
        near=layers[-1]['src']; d=ImageDraw.Draw(near)
        for x in (730,1100): d.line((x,145,x,25),fill=(82,72,64),width=3); d.line((x-32,30,x+32,30),fill=K,width=2)
        d.line((0,160,1280,160),fill=(106,114,112),width=2); d.line((0,169,1280,169),fill=(208,204,174))
    elif key=='india_alley': layers=[static(A._alley_static())]; g=156; anchors={'mirror':[48,100],'window':[249,105],'puddle':[125,162]}
    elif key=='ganges_ghat': layers=ghat(); w=640; g=158; anchors={'river':[365,171],'shrine':[169,134]}
    elif key=='desert_highway':
        layers=desert('day',360); road=new(640); d=ImageDraw.Draw(road)
        d.rectangle((0,142,640,180),fill=(70,68,68)); d.line((0,143,640,143),fill=(224,206,164),width=2)
        for x in range(0,640,48): d.rectangle((x,162,x+25,164),fill=(240,220,164))
        layers.append(wrap(road,vx=360,name='road')); w=640; g=160
    elif key=='mountain_road': layers=[static(mountain())]; g=160
    elif key=='fog_town': layers=[static(E._fog_town_static()),strip(lambda f:motion('fog',f),'mist')]; fg=[strip(lambda f:motion('fog',f),'fog_front')]
    elif key in ('enya_inn','inn'): layers=[static(room('inn'))]; g=156; anchors={'desk':[156,151],'door':[39,143]}
    elif key=='brain_inside': layers=[static(brain()),strip(lambda f:motion('brain',f),'neurons')]; g=150; anchors={'center':[160,150]}
    elif key in ('desert_noon','desert_night','desert_day'):
        kind={'desert_noon':'noon','desert_night':'night','desert_day':'day'}[key]; layers=desert(kind); w=640; g=150
    elif key=='yaprin_village': layers=town(11,640,'village'); w=640
    elif key=='cessna_cabin': layers=[static(cessna())]; g=160; anchors={'pilot':[283,160],'seat':[81,132]}
    elif key=='dream_carnival':
        layers=[static(sky('night'),'night_sky'),static(E._carnival_sky(0),'clouds'),static(E._carnival_static(),name='carnival')]
        ferris=new(); d=ImageDraw.Draw(ferris); d.ellipse((58,36,140,118),outline=(202,110,190),width=3)
        d.line((98,76,85,146),fill=(138,82,138),width=3); d.line((98,76,115,146),fill=(138,82,138),width=3)
        def wheel(fi):
            im=new(); dd=ImageDraw.Draw(im)
            for i in range(8):
                # 一轮八帧精确闭合；每辆车有独立颜色，旋转不是同色车的静态替换。
                a=math.tau*(i/8+fi/8); x=98+round(math.cos(a)*40); y=76+round(math.sin(a)*40)
                dd.line((98,76,x,y),fill=(172,120,180)); dd.rectangle((x-4,y-2,x+4,y+7),fill=(218,126+(i%3)*26,162),outline=K)
            return im
        layers.extend([static(ferris,name='ferris_support'),strip(wheel,'ferris_gondolas')]); anchors={'wheel':[98,151],'tent':[265,134]}
    elif key in ('redsea_island','egypt_coast'): layers=[static(beach('island' if key=='redsea_island' else 'beach')),strip(waves,'shore_motion')]
    elif key=='submarine': layers=[pano(room('submarine',640),name='pressure_hull'),strip(lambda f:motion('alarm',f),'warning_light','alarm')]; w=640; g=156; anchors={'periscope':[172,151],'hatch':[284,156]}
    elif key=='seabed_mouth': layers=[static(mouth()),strip(lambda f:motion('bubbles',f),'bubbles')]; g=160; anchors={'teeth_left':[46,139],'teeth_right':[273,139]}
    elif key in ('aswan_town','luxor_town'): layers=town(5 if key=='aswan_town' else 21); w=960
    elif key=='egypt_temple': layers=temple(); w=640; g=156; anchors={'sword':[270,153],'door':[579,156]}
    elif key=='nile_bank': layers=nile(); w=640; anchors={'water':[315,142]}
    elif key=='egypt_rail': layers=railway(); w=640; anchors={'tracks':[320,171]}
    elif key=='luxor_house':
        layers=[pano(room('house',640),name='living_room_and_bedroom')]; w=640; g=156
        anchors={'hide_aquarium':[249,144],'hide_wardrobe':[155,144],'hide_curtain':[58,112],
          'hide_bed':[418,144],'hide_crate':[506,144],'hide_cupboard':[570,144],
          'hide_sofa':[249,144],'hide_shelf':[506,144],'hide_vase':[570,144],
          'living_room':[160,156],'bedroom':[470,156]}
    elif key=='cafe_interior': layers=[static(E._cafe_static())]; g=156; fg=[pano(E._cafe_table_img(),name='table')]; anchors={'cafe_table':[160,132],'seat_left':[82,150],'seat_right':[238,150]}
    elif key in ('cairo_day','cairo_night','cairo_dawn','cairo_sunrise','cairo_street_night','cairo_street_dawn'):
        kind='day' if key=='cairo_day' else 'dawn' if 'dawn' in key else 'sunrise' if 'sunrise' in key else 'night'; layers=cairo(kind); w=960; g=160
    elif key=='cairo_sewer': layers=[pano(sewer(),name='brick_arches_and_channel')]; w=640
    elif key=='mansion_exterior':
        mansion,wins=E._mansion_img('night'); layers=[static(sky('night')),static(mansion,'mansion'),static(E._mansion_ground('night'),'garden')]; g=156; anchors={'door':[160,138],'gate':[160,142]}
    elif key in ('mansion_corridor','mansion_illusion','illusion_corridor'):
        illusion=key!='mansion_corridor'; layers=[pano(room('illusion' if illusion else 'corridor',640),name='arcaded_corridor')]; w=640; g=154
        if illusion: layers[-1]=wrap(layers[-1]['src'],name='illusion_loop'); anchors={'exit':[597,154]}
    elif key=='game_room': layers=[static(E._game_static())]; g=156; anchors={'screen':[159,84],'tv':[160,120],'player':[89,156],'opponent':[239,156]}
    elif key=='mansion_hall':
        layers=[static(E._hall_static())]; g=154; anchors={'pillar_a':[30,154],'pillar_b':[118,154],'pillar_c':[202,154],'pillar_d':[290,154]}
        breach=new(); bd=ImageDraw.Draw(breach); bd.polygon([(108,42),(136,30),(161,42),(175,27),(203,45),(198,92),(173,134),(126,117)],fill=(8,8,18),outline=(112,94,130),width=3)
        beam=new(); bd=ImageDraw.Draw(beam); bd.polygon([(121,33),(181,33),(264,180),(50,180)],fill=(166,142,206,42))
        layers.extend([dict(type='pano',src=breach,name='breach',k=0,key='breach'),dict(type='pano',src=beam,name='moonbeam',k=0,key='beam')])
    elif key in ('coffin_tower','mansion_tower'): layers=[static(room('tower'))]; g=160; anchors={'coffin':[160,144],'window':[160,85]}
    elif key=='mansion_stairs':
        layers=[static(E._stairs_static())]; g=166; steps=[list(p) for p in E._stairs_steps()]
        anchors={'steps':steps,'bottom':[18,166],'top':[266,76],'landing':[214,76],'exit':[267,76]}
        fg=[pano(E._rail_img(),name='stair_railing')]
    elif key=='cairo_rooftops':
        layers=[static(sky('night')),wrap(E._roof_far().crop((0,0,640,140)),.1,name='distant_skyline'),
          wrap(E._roof_mid().crop((0,0,640,150)),.35,name='middle_roofs'),pano(E._roof_near().crop((0,0,640,180)),name='roof_terrace')]
        clock,tower=E._roof_props(); layers.extend([pano(clock,x=139,y=20,name='clocktower'),pano(tower,x=474,y=84,name='water_tank')]); w=640; g=156; anchors={'clock':[155,105],'tank':[492,146]}
    elif key=='kujo_bedroom_morning': layers=[static(bedroom_morning())]; g=158; anchors={'bed':[193,153],'window':[209,74]}
    elif key=='airport': layers=[static(E._airport_static())]; g=156; anchors={'plane_door':[238,112],'gate':[276,156]}
    else: raise ValueError('未实现后续背景：'+key)
    return dict(w=w,ground=g,walk=(max(140,g-5),176),layers=layers,fg=fg,anchors=anchors)


def direct(spec,cam,t,state):
    """独立组合原始图层，核对导出后世界坐标和动画采样，不调用游戏重建器。"""
    out=new()
    for layer in spec['layers']+spec['fg']:
        if layer.get('key') and not state.get(layer['key']): continue
        typ=layer['type']; k=layer.get('k',1)
        if typ=='strip':
            im=layer['fn'](int(t*4)%8); out.alpha_composite(im); continue
        im=layer['src']; y=layer.get('y',0)
        if typ=='static': out.alpha_composite(im); continue
        if typ=='pano':
            x=layer.get('x',0)-math.floor(cam*k)
            # PIL alpha_composite 自动裁切，保留与Canvas一致的负世界坐标。
            out.alpha_composite(im,(x,y)); continue
        offset=math.floor(cam*k+t*layer.get('vx',0))%layer['period']
        tile=new(320,im.height)
        for x in range(-offset-2*layer['period'],320,layer['period']): tile.alpha_composite(im.crop((0,0,layer['period'],im.height)),(x,0))
        out.alpha_composite(tile,(0,y))
    return out


def export(ex,BJ,key=None):
    key=key or ex.key; spec=make(key); arrays={}
    def emit(L):
        typ=L['type']; name=L['name']
        if typ=='strip':
            # 八帧二秒周期使帧条2560宽，可在手机贴图限制内逐帧播放。
            render=lambda t:L['fn'](int(math.floor(t*4+1e-8))%8)
            result=ex.bake(name,(0,0,320,180),8,4,render,key=L.get('key'))
            if ex.check_on: ex.checked(name+' 二秒闭合',BJ.ndiff_rgba(render(0),render(2)))
            return result
        result={k:v for k,v in L.items() if k not in ('src','name','fn')}
        result['image']=ex.img(name,L['src']); return result
    layers=[emit(x) for x in spec['layers']]; fg=[emit(x) for x in spec['fg']]
    st=ex.stage(spec['w'],spec['ground'],spec['walk'],layers,fg,spec['anchors'])
    if ex.check_on:
        state={'flesh':True,'alarm':True,'breach':True,'beam':True}
        for cam in sorted(set((0,max(0,(spec['w']-320)//2),max(0,spec['w']-320)))):
            for t in (0,.25,1.75,2,7.25):
                a=BJ.ref_render(st,ex.images,cam,t,state); b=direct(spec,cam,t,state)
                ex.checked('镜头 %d 时刻 %.2f 导出分层一致'%(cam,t),BJ.ndiff_rgba(a,b))
                ex.checked('镜头 %d 时刻 %.2f 全画面不透明'%(cam,t),int((np.array(b)[:,:,3]!=255).sum()))
        if spec['w']>320 and key not in ('underwater','desert_noon','desert_day','desert_night','desert_highway','mansion_illusion','illusion_corridor'):
            a=direct(spec,0,0,{}); b=direct(spec,spec['w']-320,0,{})
            ex.checked('宽地图两端具有不同世界内容',0 if BJ.ndiff_rgba(a,b)>150 else 1)
    return st
