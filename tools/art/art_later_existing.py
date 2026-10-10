"""后续已有角色补帧：保留各自头身和配色，攻击重画关节，道具按角色独立绘制。"""
import sys
sys.dont_write_bytecode=True
from PIL import Image, ImageDraw
import numpy as np
import art_common as AC
from art_enemies import auto_hurt, auto_lunge
from engine import sprite

NEW=[]
ONESHOT={'whip','guard','dodge','finger','attack','hurt','down','climb','spray','cast','swing','claw','slam','wall','scared','kick','axe','beg','dive','stomp','punch','push'}
STATIC_STATES={'kid','possessed','kneel'}
CHAR_INFO={}
K=(26,16,32)
SKIN=(216,166,126)
METAL=(200,214,224)


def base_def(cid):
    for act in ('idle','swim','float','car','walk','fly'):
        if cid+'.'+act in sprite._REG: return sprite.get(cid+'.'+act)
    raise ValueError('角色没有基础帧：'+cid)


def first(cid):
    return base_def(cid).frames[0].copy()


def color(im,box,fallback):
    a=np.asarray(im.crop(box).convert('RGBA')); p=a[a[:,:,3]>0][:,:3]
    if not len(p): return fallback
    u,n=np.unique(p,axis=0,return_counts=True)
    ok=(u.sum(1)>110)&(u.sum(1)<650)
    return tuple(map(int,u[ok][np.argmax(n[ok])])) if ok.any() else fallback


def limb(d,pts,col,width=4):
    d.line(pts,fill=K,width=width+2); d.line(pts,fill=col,width=width)


def action(cid,act,fi=0):
    src=first(cid); w,h=src.size
    coat=color(src,(0,h//3,w,h*2//3),(112,108,130))
    # 脚底皮鞋的深色不能替代裤腿颜色；长袍人物的腿另取原设定色。
    pants=color(src,(0,h*2//3,w,max(h*2//3+1,h-7)),(92,90,114))
    pants={'polnareff':(154,154,176),'avdol':(218,202,170),'jotaro':(38,40,54)}.get(cid,pants)
    if act=='hurt': return auto_hurt(src)
    if act=='dodge': return auto_hurt(src,k=-.45)
    if act=='down':
        # 只转头部，横卧身体独立重画，使轮廓有腰线和屈膝。
        out=Image.new('RGBA',(h+18,24)); d=ImageDraw.Draw(out)
        head=src.crop((0,0,w,min(h//3+2,20)))
        bb=head.getbbox(); head=head.crop(bb).transpose(Image.Transpose.ROTATE_90) if bb else head
        out.alpha_composite(head,(0,max(0,23-head.height)))
        hx=min(19,head.width-2)
        d.polygon([(hx,10),(hx+17,9),(hx+22,18),(hx,21)],fill=coat,outline=K)
        limb(d,[(hx+16,17),(hx+29,12),(h+11,19)],pants,5)
        limb(d,[(hx+18,20),(h+7,20)],pants,5)
        limb(d,[(hx+5,13),(hx+9,20),(hx+18,19)],coat,3)
        d.rectangle((h+8,18,h+15,22),fill=K); return out
    if act=='float':
        # 各人的眼线高度不同；水线切在眼睛附近，帽子和发型保留，身体完全在水下。
        cut={'jotaro':17,'joseph':15,'avdol':10,'kakyoin':15,'polnareff':18}[cid]
        return AC.half_submerged_head(src.crop((0,0,w,cut)),fi)
    if act=='kneel':
        # 悼念和献身必须是屈膝姿态；复用本人的上身能保持发型与衣纹，不借用倒地帧。
        hip=h*3//5; top=src.crop((0,0,w,hip))
        out=Image.new('RGBA',(w+20,hip+16)); out.alpha_composite(top,(4,0))
        d=ImageDraw.Draw(out); x=w//2+4
        d.polygon([(x-7,hip-3),(x+7,hip-3),(x+12,hip+6),(x+4,hip+10),(x-6,hip+5)],fill=coat,outline=K)
        limb(d,[(x-4,hip+2),(x-8,hip+11),(x+4,hip+12)],pants,5)
        limb(d,[(x+4,hip+2),(x+13,hip+9),(x+22,hip+12)],pants,5)
        d.line((x+1,hip+13,x+8,hip+13),fill=K,width=3)
        d.line((x+19,hip+13,x+25,hip+13),fill=K,width=3)
        out.paste((0,0,0,0),(x+7,h//3+3,w+4,hip-4))
        d=ImageDraw.Draw(out)
        limb(d,[(x+3,h//3+2),(x+10,hip-3),(x+5,hip+2)],coat,3)
        d.rectangle((x+3,hip,x+7,hip+4),fill=SKIN,outline=K)
        return out
    if act=='push':
        # 阿布德尔推开同伴时双臂前伸、前腿踏出，避免看成普通施法或攻击。
        out=Image.new('RGBA',(w+30,h+4)); out.alpha_composite(src,(5,2))
        d=ImageDraw.Draw(out); x=w//2+5; shoulder=h//3+3
        out.paste((0,0,0,0),(x+5,shoulder,w+5,h*2//3))
        d=ImageDraw.Draw(out); ex=w+22+fi*3
        for oy in (0,7):
            limb(d,[(x+3,shoulder+oy),(x+15,shoulder+oy+2),(ex,shoulder+oy+1)],coat,3)
            d.rectangle((ex-1,shoulder+oy-2,ex+3,shoulder+oy+4),fill=SKIN,outline=K)
            d.line((ex+4,shoulder+oy-3,ex+4,shoulder+oy+4),fill=SKIN)
        out.paste((0,0,0,0),(x-8,h*2//3,w+12,h+4)); d=ImageDraw.Draw(out)
        limb(d,[(x-3,h*2//3),(x-8,h-7),(x-13,h+1)],pants,4)
        limb(d,[(x+4,h*2//3),(x+15,h-10),(x+23,h+1)],pants,4)
        d.line((x-16,h+1,x-9,h+1),fill=K,width=3)
        d.line((x+20,h+1,x+28,h+1),fill=K,width=3)
        return out
    if act=='walk':
        # 头和躯干沿用自己的部件，腿按四个步态重新绘制，不能整张站姿平移。
        out=src.copy(); out.paste((0,0,0,0),(0,h*2//3,w,h))
        d=ImageDraw.Draw(out); x=w//2; hip=h*2//3; stride=(-4,0,4,0)[fi%4]
        limb(d,[(x-4,hip),(x-5-stride,h-3)],pants,4); limb(d,[(x+4,hip),(x+4+stride,h-2)],pants,4)
        d.line((x-7-stride,h-2,x-2-stride,h-2),fill=K,width=2); d.line((x+2+stride,h-1,x+8+stride,h-1),fill=K,width=2)
        return out
    if cid in ('iggy','fool'):
        out=src.copy(); d=ImageDraw.Draw(out); x=w//2
        if act=='limp_walk':
            out.paste((0,0,0,0),(0,h-8,w,h)); d=ImageDraw.Draw(out)
            for xx in (x-8,x+9): limb(d,[(xx,h-9),(xx+(-2 if fi else 2),h-2)],coat,3)
            limb(d,[(x+3,h-8),(x+9,h-5),(x+12,h-4)],coat,2)
        elif act in ('claw','slam'):
            limb(d,[(x+4,h//2),(w-3,h//2-5+fi*10),(w-1,h-3 if fi else 1)],coat,5)
            for dx in (0,3,6): d.line((w-8+dx,h-7 if fi else 5,w-6+dx,h-2 if fi else 0),fill=METAL,width=2)
        elif act=='wall':
            out=Image.new('RGBA',(56,40)); d=ImageDraw.Draw(out)
            d.polygon([(0,39),(7,17),(9,6),(18,0),(27,4),(36,1),(47,13),(55,39)],fill=(198,178,126),outline=K)
            for x,y in ((12,17),(21,8),(36,12),(44,25),(27,30)): d.line((x,y,x+4,y-4),fill=(236,214,154),width=2)
        return out
    if cid=='starplat' and act=='finger':
        reach=sprite.get('starplat.reach'); base=reach.frames[0]
        out=Image.new('RGBA',(max(110,base.width+36),base.height)); out.alpha_composite(base)
        d=ImageDraw.Draw(out); bb=base.getbbox(); y=max(3,base.height//3)
        for oy in (0,3): limb(d,[(bb[2]-6,y+oy),(out.width-3,y+oy)],(182,158,198),2)
        return out
    if cid=='petshop' and act=='dive':
        out=src.transpose(Image.Transpose.ROTATE_270)
        return out
    if cid=='wheel':
        out=src.copy(); d=ImageDraw.Draw(out)
        if act=='climb': return out.transpose(Image.Transpose.ROTATE_90)
        out=Image.new('RGBA',(w+18,h)); out.alpha_composite(src); d=ImageDraw.Draw(out)
        d.line((w-5,h//2,w+12,h//2-5),fill=(172,120,72),width=3)
        for y in range(h//2-8,h//2+7,3): d.line((w-8,y,w-1,y+2),fill=(218,166,74))
        return out
    if act in ('fly','command','scared','beg'):
        out=auto_lunge(src,k=.12) if act=='command' else auto_hurt(src,k=-.12)
        d=ImageDraw.Draw(out)
        if act=='fly':
            d.line((w//2,2,w//2+7,7,w//2-6,13),fill=(244,208,110),width=2)
        if act=='scared':
            for xx in (w//2-5,w//2+4): d.line((xx,3,xx+2,0),fill=(244,232,180),width=2)
        if act=='beg': limb(d,[(w//2,h//2),(w//2+5,h//3),(w//2+1,h//3-3)],SKIN,3)
        return out
    # 躯干与腿保留角色身份；前臂区域留空重画，挥砍、踢击有不同的关节终点。
    extra=26 if act in ('whip','swing','axe','attack','punch','claw','kick') else 12
    out=Image.new('RGBA',(w+extra,h+4)); out.alpha_composite(src,(5,2)); d=ImageDraw.Draw(out)
    x=w//2+5; shoulder=(x+4,h//3+4); hip=h*2//3
    # 原前臂通常落在躯干右侧，清掉后重画可避免新攻击多出一只手。
    if act not in ('kick','stomp'):
        out.paste((0,0,0,0),(x+7,h//3+4,w+5,hip+2)); d=ImageDraw.Draw(out)
    if cid=='telence' and act=='punch':
        # 游戏手柄只属于待机；受控拳击重画衣襟，不能让第三只手继续抱着手柄。
        out.paste((0,0,0,0),(x-4,h//3+4,w+5,hip+2)); d=ImageDraw.Draw(out)
        d.polygon([(x-5,h//3+3),(x+7,h//3+4),(x+5,hip),(x-5,hip)],fill=(31,26,46),outline=K)
        d.line((x-1,h//3+4,x-1,hip-5),fill=(94,57,120),width=2)
        d.line((x-5,hip,x+5,hip),fill=(178,154,166),width=2)
    if act in ('kick','stomp'):
        out.paste((0,0,0,0),(x,hip,w+extra,h+4)); d=ImageDraw.Draw(out)
        end=(w+extra-3,hip-7 if not fi else h-3)
        limb(d,[(x+2,hip),(x+10,hip-8 if not fi else hip+2),end],pants,5)
        d.line((end[0]-4,end[1],end[0]+2,end[1]+2),fill=K,width=4)
    elif act=='guard':
        limb(d,[shoulder,(x+10,h//2),(x+1,h//3)],coat,4)
        limb(d,[(x-7,h//3+5),(x-10,h//2),(x+7,h//3)],coat,3)
    else:
        ty=h//3-2 if not fi else h//2+5; end=(w+extra-10,ty)
        limb(d,[shoulder,(x+12,h//2-3),end],coat,5)
        d.rectangle((end[0]-2,ty-2,end[0]+3,ty+2),fill=SKIN if cid in ('joseph','jgeil','enya','zombie','steelydan','vanilla','dio','telence') else coat,outline=K)
        if act=='whip':
            d.line((end[0],ty,end[0]+7,ty-7,end[0]+11,ty+5,end[0]+16,ty-3),fill=K,width=3)
            d.line((end[0],ty,end[0]+7,ty-7,end[0]+11,ty+5,end[0]+16,ty-3),fill=(178,92,198),width=2)
        elif act=='axe':
            d.line((end[0],ty,end[0]-4,1 if not fi else h),fill=K,width=3)
            qy=1 if not fi else h-10
            d.polygon([(end[0]-11,qy),(end[0]+5,qy+1),(end[0]+6,qy+7),(end[0]-11,qy+8)],fill=METAL,outline=K)
        elif act=='swing':
            d.line((end[0],ty,end[0]-5,0 if not fi else h),fill=(150,90,72),width=3)
            qy=2 if not fi else h-10; d.arc((end[0]-18,qy,end[0]+10,qy+12),175,355,fill=METAL,width=3)
        elif cid=='hangedman':
            d.line((end[0],ty,out.width-2,ty-9 if not fi else ty+9),fill=METAL,width=3)
        elif cid=='darkbluemoon':
            for xx in range(end[0]-3,end[0]+4,2): d.line((xx,ty,xx+5,ty-7 if not fi else ty+6),fill=(126,202,212),width=2)
        elif cid=='highpriestess':
            d.polygon([(end[0]-3,ty),(out.width-2,ty-6),(out.width-3,ty+5)],fill=(220,228,222),outline=K)
        elif act=='cast':
            for i in range(3): d.line((end[0]-1+i,ty,end[0]+7+i,ty-8),fill=(170,132,172))
    return out


NEEDED={
 'jotaro':{'float':2,'kick':2}, 'avdol':{'float':2,'push':2}, 'kakyoin':{'float':2},
 # 二乔的 whip / guard 改由 art_joseph 按原工程画法重画（2026-10-09 晚：通用拉线手臂没有分段、躯干右半边被挖掉）
 'joseph':{'dodge':1,'float':2}, 'polnareff':{'guard':1,'dodge':1,'float':2,'kneel':1,'kick':2},
 # 伊奇闪避改由 art_heroes 按原工程部件画 4 帧翻滚、愚者的 claw / slam 改由 art_stands 照 _fool_frame 重画（2026-10-10：
 # 这里的通用画法 dodge 是一张剪切的待机图，claw 是待机图上贴一根线段手臂，slam 和 claw 帧 0 一模一样）
 'iggy':{'hurt':1,'limp_walk':2}, 'starplat':{'finger':1},
 'darkbluemoon':{'attack':2,'hurt':1}, 'strength':{'walk':4,'attack':2,'hurt':1,'down':1},
 'hangedman':{'attack':2}, 'holhorse':{'hurt':1,'down':1}, 'jgeil':{'walk':4},
 'wheel':{'climb':1,'spray':1}, 'enya':{'cast':1,'hurt':1,'down':1}, 'zombie':{'attack':1},
 'steelydan':{'hurt':1,'down':1,'fly':1,'command':2}, 'death13':{'swing':2,'hurt':1},
 'judgement':{'attack':2}, 'highpriestess':{'attack':2}, 'fool':{'wall':1},
 'ndoul':{'hurt':1,'down':1}, 'boingo':{'scared':1}, 'mariah':{'walk':4,'kick':2,'hurt':1,'down':1},
 'alessi':{'walk':4,'axe':2,'hurt':1,'down':1,'beg':1}, 'petshop':{'dive':1},
 'vanilla':{'walk':4,'kick':2,'stomp':2,'hurt':1,'kneel':1}, 'theworld':{'hurt':1,'kick':2}, 'dio':{'punch':2},
 'telence':{'walk':4,'punch':2,'hurt':1,'down':1},
}
for cid,acts in NEEDED.items():
    for act,n in acts.items():
        name=cid+'.'+act
        if name in sprite._REG: raise ValueError('新动作与原注册冲突：'+name)
        frames=[action(cid,act,i) for i in range(n)]
        sd=base_def(cid); src=sd.frames[0]
        ax,ay=sprite._anchor_px(sd.anchor,*src.size)
        if name=='starplat.finger': anchor=sprite.get('starplat.reach').anchor
        elif act=='float': anchor=(20,21)
        elif act in ('down','kneel') or (cid=='fool' and act=='wall'): anchor='mb'
        elif (cid=='petshop' and act=='dive') or (cid=='wheel' and act=='climb'):
            anchor='mm' if sd.anchor=='mm' else 'mb'
        elif frames[0].height==src.height+4: anchor=(ax+5,ay+2)
        else: anchor=(ax,ay)
        sprite.define(name,frames,anchor=anchor,fps=3 if act=='float' else 6 if act in ('walk','limp_walk') else 8,desc='后续补帧：'+name)
        NEW.append(name)

# 规划使用原cid的形态动作；专用cid仍有全套走路和受击供世界实体使用。
for cid,act,source in [('polnareff','kid','polnareff_kid.idle'),('jotaro','kid','jotaro_kid.idle'),('polnareff','possessed','polnareff_possessed.idle')]:
    sd=sprite.get(source); name=cid+'.'+act
    sprite.define(name,sd.frames,anchor=sd.anchor,fps=3,desc='剧情形态：'+act); NEW.append(name)
