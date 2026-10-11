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
 # 力量的 walk / attack / hurt / down 不走通用 action()，按原部件重摆，见下面 _strength_frames（2026-10-10）
 'darkbluemoon':{'attack':2,'hurt':1},
 # J·凯尔的 walk 不走通用 action()（同力量：腰以下整片清空、腿只剩两根细线），见下面 _geil_frames（2026-10-11）
 'hangedman':{'attack':2}, 'holhorse':{'hurt':1,'down':1},
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


# =====================================================================================
#  力量（猩猩）walk / attack / hurt / down（2026-10-10 重画）
# =====================================================================================
# 通用 action() 是照人形写的：走路把腰以下整片清空再画两根细腿（身体在腰那一行被横着切断）、攻击清掉半张脸再贴一根
# 细线手臂、倒地是人形躺姿加黑皮鞋。这里改用原工程 sprites_enemies._strength 的同一套 _Pix 部件（头、脸盘、毛色、
# 自动明暗、描边都照原函数），只挪四肢、让身体起伏、换表情；_ST_IDLE 原样传进去能逐格复现原 idle 两帧（下面自检）。
# 画布 = 图集 cell 70×44、锚点 = pivot (29, 42)：idle（40×40、'mb'）的左上角落在 (9, 2)，所以烘出来 cell / pivot 不变。
from assets import sprites_enemies as SE    # noqa: E402

_ST_W, _ST_H, _ST_O = 70, 44, (9, 2)
_ST_IDLE = dict(body=(0, 0), head=(0, 0), face='calm',
                arm_b=[(11, 17), (6, 27), (6, 35)], hand_b=(3, 34, 8, 38),        # 远侧手臂（在身体后面）
                arm_f=[(25, 19), (31, 27), (32, 35)], hand_f=(29, 34, 35, 38),    # 近侧手臂（最上层）
                leg_b=[(12, 30), (10, 36)], foot_b=(8, 36, 13, 38),
                leg_f=[(20, 31), (22, 36)], foot_f=(20, 36, 25, 38))
_ST_FRINGE = [(4, 22), (5, 28), (7, 32), (12, 34), (16, 35), (26, 32), (6, 15), (9, 11), (14, 9)]


def _st_face(fc, kind, o):
    """脸盘：calm / grin 照原图；roar 张嘴龇牙（眉心压低）、hurt 眼睛挤成 > < 张嘴、ko 叉叉眼吐舌。"""
    X = lambda x: x + o[0]
    Y = lambda y: y + o[1]
    fc.ell(X(22), Y(4), X(37), Y(19), 'a')
    fc.shade('a', 'A', d=(1, 1))
    fc.ell(X(26), Y(11), X(36), Y(18), 'b')
    if kind == 'hurt':
        fc.rect(X(27), Y(6), X(34), Y(7), 'A')
        fc.dot([(X(28), Y(8)), (X(29), Y(9)), (X(28), Y(10)), (X(33), Y(8)), (X(32), Y(9)), (X(33), Y(10))], 'k')
    elif kind == 'ko':
        fc.rect(X(27), Y(7), X(34), Y(7), 'A')
        for cx in (28, 34):                     # 叉叉眼（比原眼距各开 1 格，转 90° 后两只不糊成一团）
            fc.dot([(X(cx - 1), Y(8)), (X(cx + 1), Y(8)), (X(cx), Y(9)), (X(cx - 1), Y(10)), (X(cx + 1), Y(10))], 'k')
    else:
        fc.rect(X(27), Y(7), X(34), Y(8), 'A')                                    # 浓眉
        if kind == 'roar':
            fc.dot([(X(30), Y(9)), (X(31), Y(9)), (X(34), Y(9))], 'A')            # 眉心压下来
        fc.dot([(X(28), Y(9)), (X(32), Y(9))], 'k')
        fc.dot([(X(29), Y(9)), (X(33), Y(9))], 'y')
    fc.dot([(X(31), Y(12)), (X(32), Y(12))], 'A')                                 # 鼻孔
    if kind == 'calm':
        fc.line([(X(28), Y(15)), (X(35), Y(15))], 'k')
        fc.dot([(X(27), Y(14)), (X(36), Y(14))], 'k')
    elif kind == 'grin':
        fc.rect(X(28), Y(14), X(35), Y(16), 'k')
        fc.rect(X(29), Y(14), X(34), Y(15), 'w')
        fc.dot([(X(30), Y(15)), (X(32), Y(15))], 'k')
    elif kind == 'roar':
        fc.rect(X(28), Y(13), X(35), Y(17), 'k')
        fc.rect(X(29), Y(14), X(34), Y(14), 'w')
        fc.rect(X(30), Y(15), X(33), Y(15), 'M')
        fc.rect(X(29), Y(16), X(34), Y(16), 'w')
        fc.dot([(X(31), Y(14)), (X(32), Y(16))], 'k')
    elif kind == 'hurt':
        fc.rect(X(29), Y(14), X(34), Y(17), 'k')
        fc.rect(X(30), Y(15), X(33), Y(16), 'M')
    elif kind == 'ko':
        fc.line([(X(28), Y(15)), (X(35), Y(15))], 'k')
        fc.dot([(X(33), Y(16)), (X(34), Y(16)), (X(33), Y(17)), (X(34), Y(17))], 'f')
    return fc


def _st_head(W, H, o, face):
    hd = SE._Pix(W, H)
    hd.ell(19 + o[0], 2 + o[1], 33 + o[0], 18 + o[1], 'O')
    hd.dot([(x + o[0], y + o[1]) for x, y in ((22, 1), (24, 0), (26, 1), (21, 3))], 'O')
    hd.shade('O', 'R', d=(1, 1))
    hd.shade('O', 'o', d=(-1, -1))
    hd.paste(_st_face(SE._Pix(W, H), face, o), ring='k')
    return hd


def _st_pose(W=_ST_W, H=_ST_H, o=_ST_O, **kw):
    """原 _strength 的图层顺序：远侧手臂 → 身体（含腿）→ 头 → 近侧手臂；坐标都写 idle 坐标，整体平移 o。"""
    q = dict(_ST_IDLE, **kw)
    mv = lambda pts: [(x + o[0], y + o[1]) for x, y in pts]
    bx = lambda b: (b[0] + o[0], b[1] + o[1], b[2] + o[0], b[3] + o[1])
    bd = (q['body'][0] + o[0], q['body'][1] + o[1])
    P, fur, ab, af = (SE._Pix(W, H) for _ in range(4))
    fur.ell(5 + bd[0], 11 + bd[1], 28 + bd[0], 33 + bd[1], 'O')
    fur.seg(mv(q['leg_b']), 2.2, 'O')
    fur.seg(mv(q['leg_f']), 2.2, 'O')
    for x, y in _ST_FRINGE:
        fur.dot([(x + bd[0], y + bd[1]), (x - 1 + bd[0], y + 1 + bd[1])], 'O')
    fur.shade('O', 'R', d=(1, 1), n=2)
    fur.shade('O', 'o', d=(-1, -1))
    fur.ell(*bx(q['foot_b']), 'A')
    fur.ell(*bx(q['foot_f']), 'A')
    ab.seg(mv(q['arm_b']), 2.0, 'O')
    ab.shade('O', 'R', d=(1, 1))
    ab.ell(*bx(q['hand_b']), 'A')
    af.seg(mv(q['arm_f']), 2.0, 'O')
    af.ell(*bx(q['hand_f']), 'A')
    af.shade('O', 'R', d=(1, 1))
    af.shade('O', 'o', d=(-1, -1))
    P.paste(ab)
    P.paste(fur, ring='k')
    P.paste(_st_head(W, H, (q['head'][0] + o[0], q['head'][1] + o[1]), q['face']), ring='k')
    P.paste(af, ring='k')
    P.outline('k')
    return P


def _st_walk(f):
    """指关节撑地走：近侧手臂 + 后腿 / 远侧手臂 + 前腿两对交替（对角步态）。每个肢体 4 个相位：
    前伸着地 → 正下方 → 后蹬 → 抬起往前摆；抬起那一对的帧身体（连头）上浮 1 px。"""
    ph = {'hf': f % 4, 'fb': f % 4, 'hb': (f + 2) % 4, 'ff': (f + 2) % 4}
    amp = {'hf': 4, 'hb': 3, 'fb': 2, 'ff': 2}
    lift_px = {'hf': 3, 'hb': 2, 'fb': 2, 'ff': 2}
    dx = {k: (amp[k], 0, -amp[k], 0)[p] for k, p in ph.items()}
    up = {k: lift_px[k] if p == 3 else 0 for k, p in ph.items()}
    by = (0, -1, 0, -1)[f]
    d, l = dx['hb'], up['hb']
    q = dict(arm_b=[(11, 17 + by), (6 + round(d / 2) + (1 if l else 0), 27 + by - l // 2), (6 + d, 35 - l)],
             hand_b=(3 + d, 34 - l, 8 + d, 38 - l))
    d, l = dx['hf'], up['hf']
    q.update(arm_f=[(25, 19 + by), (31 + round(d / 2) + (1 if l else 0), 27 + by - l // 2), (32 + d, 35 - l)],
             hand_f=(29 + d, 34 - l, 35 + d, 38 - l))
    d, l = dx['fb'], up['fb']
    q.update(leg_b=[(12, 30 + by), (10 + d, 36 - l)], foot_b=(8 + d, 36 - l, 13 + d, 38 - l))
    d, l = dx['ff'], up['ff']
    q.update(leg_f=[(20, 31 + by), (22 + d, 36 - l)], foot_f=(20 + d, 36 - l, 25 + d, 38 - l))
    return _st_pose(body=(0, by), head=(0, by), **q)


def _st_down():
    """仰面倒地、头朝左（同 avdol / kakyoin 的 down）：头部图层（叉叉眼吐舌）逆时针转 90° = 头顶朝左、脸朝上，
    肚皮朝天、两腿翘起、远侧手臂甩在头后、近侧手臂瘫在身前地上；最低像素在 pivot 上一行。"""
    W, H, (ox, oy) = _ST_W, _ST_H, _ST_O
    head = _st_head(40, 40, (0, 0), 'ko').a[0:20, 19:38]             # 原头 + 脸盘的包围盒
    rot = np.rot90(head, 1)
    hp = SE._Pix(W, H)
    hp.a[19 + oy:19 + oy + rot.shape[0], -4 + ox:-4 + ox + rot.shape[1]] = rot
    P, fur, ab, af = (SE._Pix(W, H) for _ in range(4))
    mv = lambda pts: [(x + ox, y + oy) for x, y in pts]
    fur.ell(12 + ox, 23 + oy, 38 + ox, 38 + oy, 'O')
    fur.seg(mv([(32, 29), (38, 23)]), 2.2, 'O')
    fur.seg(mv([(35, 33), (43, 29)]), 2.2, 'O')
    for x, y in ((15, 22), (21, 21), (28, 21), (34, 23)):
        fur.dot(mv([(x, y), (x - 1, y - 1)]), 'O')
    fur.shade('O', 'R', d=(1, 1), n=2)
    fur.shade('O', 'o', d=(-1, -1))
    fur.ell(36 + ox, 18 + oy, 41 + ox, 23 + oy, 'A')
    fur.ell(42 + ox, 26 + oy, 46 + ox, 31 + oy, 'A')
    ab.seg(mv([(13, 28), (5, 32), (-3, 35)]), 2.0, 'O')
    ab.shade('O', 'R', d=(1, 1))
    ab.ell(-8 + ox, 33 + oy, -3 + ox, 37 + oy, 'A')
    af.seg(mv([(16, 30), (23, 35), (31, 36)]), 2.0, 'O')
    af.ell(30 + ox, 34 + oy, 35 + ox, 38 + oy, 'A')
    af.shade('O', 'R', d=(1, 1))
    af.shade('O', 'o', d=(-1, -1))
    P.paste(ab)
    P.paste(fur, ring='k')
    P.paste(hp, ring='k')
    P.paste(af, ring='k')
    P.outline('k')
    return P


def _strength_frames():
    walk = [_st_walk(f) for f in range(4)]
    attack = [
        # 0 蓄力：身子往后一仰、近侧手臂把拳头抡到头顶后面、张嘴吼
        _st_pose(body=(-1, -1), head=(-2, -1), face='roar', arm_f=[(23, 18), (15, 12), (17, 3)], hand_f=(14, -1, 20, 4),
                 arm_b=[(10, 16), (5, 26), (5, 35)], hand_b=(2, 34, 7, 38)),
        # 1 出拳：身子前扑、前脚踏出半步、拳头砸到身前（拳心约在 pivot 右边 28 px、离地 16 px）
        _st_pose(body=(2, 0), head=(4, 1), face='roar', arm_f=[(28, 20), (38, 22), (46, 24)], hand_f=(44, 21, 51, 27),
                 leg_f=[(22, 31), (25, 36)], foot_f=(23, 36, 28, 38), arm_b=[(13, 17), (8, 27), (7, 35)], hand_b=(4, 34, 9, 38)),
    ]
    # 受击：上身后仰、头甩到后面、眼睛挤成 > < 张嘴，远侧手臂甩上去、近侧手臂往前甩，前脚离地 1 px
    hurt = [_st_pose(body=(-2, -1), head=(-5, -1), face='hurt', arm_f=[(22, 19), (29, 24), (37, 24)], hand_f=(36, 21, 41, 26),
                     arm_b=[(10, 16), (4, 10), (2, 3)], hand_b=(-1, 0, 4, 5), leg_b=[(10, 29), (9, 36)], foot_b=(7, 36, 12, 38),
                     leg_f=[(18, 30), (21, 35)], foot_f=(19, 35, 24, 37))]
    return {'walk': walk, 'attack': attack, 'hurt': hurt, 'down': [_st_down()]}


# 自检：原部件原样传进去 = 原 idle 两帧（40×40 画布、不平移）——保证头、脸、毛色、明暗、描边和原图是同一套
if _st_pose(40, 40, (0, 0)).grid() != SE._strength(0).grid() or \
        _st_pose(40, 40, (0, 0), face='grin', arm_f=[(24, 20), (18, 14), (17, 5)], hand_f=(15, 1, 20, 6)).grid() != SE._strength(1).grid():
    raise ValueError('力量部件复现不出原 idle（sprites_enemies._strength 变了？）')
_ST_DESC = {
    'walk': '指关节撑地走 4 帧：近侧手臂 + 后腿 / 远侧手臂 + 前腿成对交替，抬起那一对的帧身体上浮 1 px（身体、头、毛色照 idle）',
    'attack': '0 蓄力：后仰、拳头抡到头顶后面、张嘴吼；1 出拳：前扑、拳头砸到身前（拳心约 pivot 右 28 px、离地 16 px）',
    'hurt': '受击后仰：头甩到后面、眼睛挤成 > <、张嘴，两臂一上一前甩开',
    'down': '仰面倒地、头朝左（头部转 90°：叉叉眼吐舌），肚皮朝天、两腿翘起',
}
for _act, _frames in _strength_frames().items():
    _name = 'strength.' + _act
    if _name in sprite._REG: raise ValueError('新动作与原注册冲突：' + _name)
    sprite.define(_name, [p.grid() for p in _frames], pal=SE.PAL_STR, anchor=(29, 42),
                  fps=6 if _act == 'walk' else 8, desc=_ST_DESC[_act])
    NEW.append(_name)


# =====================================================================================
#  J·凯尔 walk / kick / throw / down（2026-10-11 第4章）
# =====================================================================================
# 原来的 walk 走通用 action()：腰以下整片清空、只画两根 4 px 的细腿（身体在腰那一行被切断，同力量的毛病）。
# 这里照原工程 sprites_enemies._geil 的同一套 _Pix 部件（头、刘海、眼、咧嘴、长发、橄榄色大衣、脏衬衫、两只右手 _RHAND、
# 裤腿、皮鞋，调色板 PAL_GEIL）重新摆姿势；_GE_IDLE 原样传进去能逐格复现原 idle 两帧（下面自检）。
# 两只手都是右手：每只手都用同一个 _RHAND（拇指在右边），转向时两只手一起转、拇指始终朝同一边。
# 坐标都写原 36×52 的坐标；新画布更大时整体平移 o，锚点 = 原脚点 (18, 52) + o，所以烘出来 pivot 仍是脚底。
def _ge_rot(grid, k):
    """_RHAND 这类字符网格逆时针转 k×90°（k=-1 = 顺时针）。"""
    a = np.array([list(r) for r in SE.sp.g_lines(grid)])
    return '\n'.join(''.join(r) for r in np.rot90(a, k))


_GE_HAND = {'up': SE._RHAND, 'fwd': _ge_rot(SE._RHAND, -1), 'down': _ge_rot(SE._RHAND, 2), 'back': _ge_rot(SE._RHAND, 1)}
# 抓了一把沙土的拳头（手背朝外、拇指压在上面，指缝漏出两粒土）
_GE_FIST = """
.sss.
sssss
sSsss
sssSs
.SSS.
"""
_GE_IDLE = dict(sway=0, hy=0, up=(0, 0), lean=0.0, squash=1.0, head=(0, 0), face='grin', legs=None, coat=None)


def _ge_head(face, W=36, H=52):
    """原 _geil 的头图层（36×52 坐标，画布可以更大，坐标不变）。face：grin = 原 idle；hurt = 原 hurt；ko = 叉叉眼 + 张着嘴（倒地，不画血）；
    grit = 咧嘴更大、眼睛瞪圆（出招）。"""
    hd = SE._Pix(W, H)
    hd.ell(15, 7, 25, 18, 's')
    hd.poly([(16, 14), (26, 13), (26, 17), (23, 21), (18, 20)], 's')
    hd.dot([(26, 11), (27, 12), (27, 13)], 's')
    hd.shade('s', 'S', d=(1, 1))
    hd.poly([(14, 5), (22, 3), (26, 7), (24, 8), (22, 7), (21, 10), (19, 8), (18, 12), (17, 9), (15, 14)], 'n')
    hd.shade('n', 'N', d=(-1, -1))
    hd.rect(22, 10, 24, 11, 'w')
    hd.dot([(23, 11)], 'e')
    hd.dot([(22, 9), (23, 9), (24, 9)], 'k')
    hd.dot([(19, 11)], 'e')
    if face == 'hurt':
        hd.rect(21, 9, 24, 12, 'w')
        hd.dot([(22, 10)], 'e')
        hd.dot([(21, 8), (22, 8), (23, 8)], 'k')
        hd.rect(18, 14, 25, 19, 'k')
        hd.rect(19, 14, 25, 14, 'w')
        hd.rect(20, 17, 24, 18, 'r')
        hd.dot([(17, 13), (26, 13)], 'k')
    elif face == 'ko':
        hd.rect(22, 9, 24, 12, 's')
        hd.dot([(22, 10), (24, 10), (23, 11), (22, 12), (24, 12)], 'k')      # 叉叉眼（比原眼低 1 px，躺下转 90° 后不贴着头发）
        hd.dot([(19, 11)], 'k')
        hd.rect(19, 15, 23, 17, 'k')                                          # 张着嘴（下巴松了；不画红色，免得像血）
        hd.rect(20, 15, 23, 15, 'w')
    else:
        grin_y = 15
        if face == 'grit':
            hd.rect(21, 9, 24, 11, 'w')                                       # 眼睛瞪圆
            hd.dot([(23, 10)], 'e')
            hd.dot([(21, 8), (22, 8), (23, 8), (24, 8)], 'k')
            hd.rect(17, grin_y - 1, 25, grin_y + 2, 'w')                      # 咧到耳根
            hd.dot([(18, grin_y - 1), (20, grin_y - 1), (22, grin_y - 1), (24, grin_y - 1),
                    (19, grin_y + 2), (21, grin_y + 2), (23, grin_y + 2)], 'x')
            hd.rect(18, grin_y, 25, grin_y + 1, 'k')
            hd.dot([(19, grin_y), (21, grin_y), (23, grin_y)], 'w')
            hd.line([(16, grin_y - 2), (17, grin_y + 3), (25, grin_y + 3), (26, grin_y - 1)], 'k')
        else:
            hd.rect(18, grin_y, 25, grin_y + 1, 'w')
            hd.dot([(20, grin_y), (22, grin_y), (24, grin_y), (19, grin_y + 1), (21, grin_y + 1), (23, grin_y + 1)], 'x')
            hd.line([(17, grin_y - 1), (18, grin_y + 2), (25, grin_y + 2), (26, grin_y)], 'k')
            hd.dot([(17, grin_y - 1)], 'k')
    return hd


def _ge_arm(up, pts, hand, hxy, mv):
    """一条手臂（橄榄色袖子，粗 1.3）+ 手：up = 朝上张开的右手（原 idle），fwd / down / back = 同一只右手转 90° / 180° / 270°，
    fist = 抓着沙土的拳头。"""
    arm = SE._Pix(up.w, up.h)
    arm.seg(mv(pts), 1.3, 'o')
    arm.shade('o', 'O', d=(1, 1))
    up.paste(arm, ring='k')
    if hand:
        g = _GE_FIST if hand == 'fist' else _GE_HAND[hand]
        up.paste(SE._Pix(up.w, up.h).stamp(g, *mv([hxy])[0]), ring='k')


def _ge_legs(lo, legs, mv):
    """legs = [(髋→膝→踝 的点列, 鞋 dict), …]：先画的那条在后面（远侧），后画的贴分隔线。
    鞋 = 原 _geil 的皮鞋多边形：lx = 踝处 4 px 裤腿的左列，y = 鞋底行（原 50），tilt = 鞋尖下压 / 上翘的像素。"""
    for i, (pts, shoe) in enumerate(legs):
        L = SE._Pix(lo.w, lo.h)
        L.seg(mv(pts), 2.0, 'q')
        L.shade('q', 'Q', d=(1, 0))
        if shoe:
            lx, y, tilt = shoe['lx'], shoe.get('y', 50), shoe.get('tilt', 0)
            L.poly(mv([(lx - 1, y - 4 + max(0, -tilt)), (lx + 3, y - 4), (lx + 5, y - 2 + tilt), (lx + 5, y + tilt),
                       (lx - 1, y)]), 'h')
            L.shade('h', 'H', d=(1, 1))
        lo.paste(L, ring='k' if i else None)


def _ge_pose(W=36, H=52, o=(0, 0), **kw):
    """原 _geil 的图层顺序：腿 → 长发 → 大衣 → 衬衫 → 头 → 远侧手臂 + 手 → 近侧手臂 + 手 → 描边。
    up = 上身整体平移；lean = 以腰线 y=41 为轴的行剪切（正 = 往前弯，头比腰多挪 lean×高度）；squash = 上身竖向压缩。
    arms = [(点列, 手型, 手的左上角)]；默认照原 idle（hy = 两手一上一下的 1 px 晃动）。"""
    q = dict(_GE_IDLE, **kw)
    ox, oy = o
    mv = lambda pts: [(x + ox, y + oy) for x, y in pts]
    ux, uy = q['up']

    def T(x, y):                                          # 上身（大衣、长发、肩）的变形：剪切 + 压缩 + 平移
        h = 41 - y
        return (x + ux + q['lean'] * h, 41 - h * q['squash'] + uy)
    Tm = lambda pts: [T(x, y) for x, y in pts]
    lo = SE._Pix(W, H)
    if q['legs'] is None:                                 # 原 idle：两条直的裤腿 + 皮鞋
        lo.rect(12 + ox, 37 + oy, 15 + ox, 47 + oy, 'q')
        lo.rect(18 + ox, 37 + oy, 21 + ox, 47 + oy, 'q')
        lo.shade('q', 'Q', d=(1, 0))
        lo.poly(mv([(11, 46), (15, 46), (17, 48), (17, 50), (11, 50)]), 'h')
        lo.poly(mv([(18, 46), (21, 46), (23, 48), (23, 50), (18, 50)]), 'h')
        lo.shade('h', 'H', d=(1, 1))
    else:
        _ge_legs(lo, q['legs'], mv)
    up = SE._Pix(W, H)
    up.poly(mv(Tm(q.get('hair') or [(12, 5), (20, 3), (22, 8), (17, 10), (16, 16), (17, 24), (16, 34), (14, 37),
                                     (12, 34), (10, 37), (8, 33), (6, 35), (5, 28), (6, 18), (8, 9)])), 'n')
    sway = q['sway']
    up.poly(mv(Tm(q.get('hair_tip') or [(6, 30), (5, 36 + sway), (8, 33)])), 'n')
    up.shade('n', 'N', d=(-1, -1))
    up.dot([(round(x), round(y)) for x, y in mv(Tm([(9, 14), (9, 15), (10, 22), (10, 23), (8, 26), (12, 28), (12, 29)]))], 'N')
    up.poly(mv(Tm(q['coat'] or [(12, 21), (21, 20), (23, 30), (25, 41), (9, 41), (8, 30)])), 'o')
    up.shade('o', 'O', d=(1, 1))
    up.poly(mv(Tm([(18, 21), (22, 21), (21, 29), (19, 29)])), 'W')
    up.shade('W', 'x', d=(1, 0))
    up.line(mv(Tm(q.get('coat_line') or [(10, 33), (9, 41)])), 'O')
    hx, hy0 = q['head']
    up.paste(_ge_head(q['face'], W, H).shift(ox + hx, oy + hy0), ring='k')
    hy = q['hy']
    arms = q.get('arms') or [([(20, 24), (24, 32), (29, 28 - hy)], 'up', (27, 21 - hy)),
                             ([(13, 24), (15, 31), (19, 29 + hy)], 'up', (17, 23 + hy))]
    for arm in arms:
        pts, hand, hxy = arm[:3]
        sx, sy = T(*pts[0])
        sx, sy = int(round(sx)), int(round(sy))
        if len(arm) > 3 and arm[3] == 'abs':                 # 只把肩膀挪到变形后的位置，肘、手是写死的画面坐标
            pts = [(sx, sy)] + list(pts[1:])
        else:                                                # 整条手臂跟着肩膀平移（走路起伏、出招时的轻微后仰）
            dx, dy = sx - pts[0][0], sy - pts[0][1]
            pts = [(x + dx, y + dy) for x, y in pts]
            hxy = (hxy[0] + dx, hxy[1] + dy)
        _ge_arm(up, pts, hand, hxy, mv)
    lo.paste(up)
    for x, y, c in q.get('dots', ()):                     # 扬起的沙土团（画在描边之前，自带描边）
        lo.dot(mv([(x, y)]), c)
    lo.outline('k')
    for x, y, c in q.get('dots_after', ()):               # 细沙粒（描边之后画，不描边）
        lo.dot(mv([(x, y)]), c)
    return lo


def _ge_walk(f):
    """4 帧：0 右脚（近侧）在前着地 → 1 收腿过身（近侧腿直立撑地、远侧腿屈膝抬起往前摆，上身抬 1 px）→
    2 远侧脚在前着地 → 3 近侧腿抬起往前摆。上身、头、大衣、长发照 idle；两只右手跟着步子一上一下晃 1 px，
    发梢在过身的帧甩一下。裤腿 4 px 宽、从大衣下摆底下出来，皮鞋照原形状。"""
    by = (0, -1, 0, -1)[f]
    hy = (0, 0, -1, -1)[f]
    hip_f, hip_n = (13.5, 38 + by), (19.5, 38 + by)     # 远侧 / 近侧髋（原两条裤腿的中线）
    if f == 0:      # 近侧在前、远侧在后
        far = ([hip_f, (12.5, 43), (10.5, 46)], dict(lx=9, tilt=0))
        near = ([hip_n, (21.5, 43), (23.5, 46)], dict(lx=22, tilt=0))
    elif f == 1:    # 近侧撑地、远侧抬腿往前
        far = ([hip_f, (16.5, 42), (15.5, 45)], dict(lx=14, y=48, tilt=1))
        near = ([hip_n, (19.5, 43), (19.5, 46)], dict(lx=18))
    elif f == 2:    # 远侧在前、近侧在后
        far = ([hip_f, (15.5, 43), (17.5, 46)], dict(lx=16))
        near = ([hip_n, (17.5, 43), (15.5, 46)], dict(lx=14))
    else:           # 远侧撑地、近侧抬腿往前
        far = ([hip_f, (13.5, 43), (13.5, 46)], dict(lx=12))
        near = ([hip_n, (22.5, 42), (21.5, 45)], dict(lx=20, y=48, tilt=1))
    return _ge_pose(up=(0, by), head=(0, by), hy=hy, sway=(0, 1, 0, 1)[f], legs=[far, near])


_GE_W, _GE_H, _GE_O = 76, 56, (14, 4)       # 出招的大画布：原 36×52 平移 (14, 4)，锚点 = (32, 56)


def _ge_kick(f):
    """JG_KICK（W1 低踢）：0 提膝蓄力——近侧腿大腿抬平、小腿垂下，上身往后仰，一只右手举在脸前、一只甩到身后保持平衡
    （两只都是掌心朝外、拇指朝右）；1 踢出——近侧腿伸直往前蹬到腰高（鞋底朝前，鞋在脚点右 19–24 px、离地 11–19 px），
    大衣前襟被腿掀开，上身仰得更厉害，两手都甩到身后。远侧腿撑地微屈。"""
    if f == 0:
        coat = [(12, 21), (21, 20), (23, 30), (27, 37), (24, 40), (9, 41), (8, 30)]
        legs = [([(13.5, 38), (13.5, 43), (12.5, 46)], dict(lx=11)),
                ([(19.5, 37), (25.5, 37), (25.5, 43)], dict(lx=24, y=47, tilt=1))]
        arms = [([(20, 24), (6, 22), (4, 17)], 'up', (2, 11)),
                ([(13, 24), (24, 25), (29, 20)], 'up', (27, 14))]
        return _ge_pose(_GE_W, _GE_H, _GE_O, up=(-1, 0), lean=-0.08, head=(-3, 0), face='grit',
                        coat=coat, legs=legs, arms=arms, sway=1)
    coat = [(12, 21), (21, 20), (23, 30), (29, 35), (25, 40), (9, 41), (8, 30)]
    legs = [([(13.5, 38), (12.5, 43), (11.5, 46)], dict(lx=10)),
            ([(19.5, 37), (27.5, 37), (35.5, 37)], None)]
    arms = [([(20, 24), (14, 22), (8, 19)], 'back', (1, 14)),
            ([(13, 24), (8, 29), (3, 27)], 'back', (-4, 23))]
    pose = _ge_pose(_GE_W, _GE_H, _GE_O, up=(-2, 0), lean=-0.12, head=(-6, 0), face='grit',
                    coat=coat, legs=legs, arms=arms, sway=2)
    # 蹬出去的鞋：鞋底朝前竖着（原皮鞋转 90°），贴在伸直的裤腿末端
    shoe = SE._Pix(_GE_W, _GE_H)
    ox, oy = _GE_O
    shoe.poly([(37 + ox, 33 + oy), (41 + ox, 33 + oy), (41 + ox, 40 + oy), (39 + ox, 41 + oy), (37 + ox, 40 + oy)], 'h')
    shoe.shade('h', 'H', d=(1, 1))
    pose.paste(shoe, ring='k')
    pose.outline('k')
    return pose


def _ge_dust():
    """扇形沙土（JG_DUST 扬尘）：从手掌往右前方散开，越远越散越稀；土团（2 px，自带描边）+ 细沙粒（1 px，不描边）。"""
    import random
    rnd = random.Random(41)
    clumps, grains = [], []
    for i in range(70):
        t = rnd.random()
        x = 39 + t * 19 + rnd.uniform(-1, 1)               # 最远到原坐标 x≈59（画布 76 宽，不出界）
        y = 15 - t * 5 + rnd.gauss(0, 1) * (1.5 + 7 * t)
        c = 'T' if rnd.random() < .5 else 't'
        if t < .45 and rnd.random() < .5:
            clumps += [(int(x), int(y), c), (int(x) + 1, int(y), c), (int(x), int(y) + 1, 'T')]
        else:
            grains.append((int(round(x)), int(round(y)), c))
    return clumps, grains


def _ge_throw(f):
    """JG_DUST（W4 扬尘致盲）：0 弯腰——两膝弯下、上身往前压低（头低到腰高），近侧那只右手伸到脚尖前的地上抓一把沙土（握拳），
    远侧那只右手垂在膝前；1 扬起——上身直起前倾，近侧手臂往前上方一甩、手掌张开（同一只右手转 90°，手指朝前），
    一把沙土呈扇形往前飞（脚点右 20–40 px、离地 26–51 px），远侧手往后甩。"""
    if f == 0:
        legs = [([(13.5, 40), (18.5, 43), (14.5, 46)], dict(lx=13)),
                ([(19.5, 40), (25.5, 43), (22.5, 46)], dict(lx=21))]
        arms = [([(20, 24), (34, 37), (33, 41)], 'down', (29, 41), 'abs'),
                ([(13, 24), (28, 38), (32, 44)], 'fist', (30, 44), 'abs')]
        return _ge_pose(_GE_W, _GE_H, _GE_O, up=(2, 3), lean=0.6, squash=0.7, head=(19, 12), face='grit',
                        legs=legs, arms=arms, sway=1)
    legs = [([(13.5, 38), (11.5, 43), (10.5, 46)], dict(lx=9)),
            ([(19.5, 38), (22.5, 43), (23.5, 46)], dict(lx=22))]
    arms = [([(20, 24), (15, 30), (10, 33)], 'back', (3, 29)),
            ([(13, 24), (22, 25), (31, 16)], 'fwd', (31, 13))]
    clumps, grains = _ge_dust()
    return _ge_pose(_GE_W, _GE_H, _GE_O, up=(1, 0), lean=0.1, head=(3, 0), face='grit', legs=legs, arms=arms,
                    sway=1, dots=clumps, dots_after=grains)


_GE_DW, _GE_DH = 60, 24                    # 倒地画布，锚点 = 底边中点 (30, 24)


def _ge_down():
    """被刺倒地（不画血）：仰面躺平、头朝左（同 avdol / kakyoin / 力量的 down），头部图层（叉叉眼 + 张着嘴）
    逆时针转 90°（头顶朝左、脸朝上），油腻的长发在头后面的地上铺开；大衣平躺、两腿往右伸、鞋尖朝上；
    两只右手手指都朝右摊着（同一只右手转 90°，拇指都朝下）：远侧那只搭在肚子上、近侧那只摊在身边的地上。最低像素在脚点上一行。"""
    W, H = _GE_DW, _GE_DH
    lo = SE._Pix(W, H)
    lo.rect(38, 15, 51, 21, 'q')                           # 两条裤腿叠在一起平放
    lo.shade('q', 'Q', d=(0, 1))
    lo.line([(39, 18), (50, 18)], 'Q')
    for x0, y0 in ((51, 9), (49, 14)):                     # 皮鞋：鞋尖朝上（原皮鞋转 90°）
        lo.poly([(x0, y0 + 8), (x0, y0 + 2), (x0 + 2, y0), (x0 + 4, y0), (x0 + 4, y0 + 8)], 'h')
    lo.shade('h', 'H', d=(1, 1))
    up = SE._Pix(W, H)
    up.poly([(0, 22), (1, 17), (4, 14), (8, 13), (12, 15), (14, 22)], 'n')     # 长发铺在头后面
    up.poly([(0, 22), (0, 19), (3, 21)], 'n')
    up.shade('n', 'N', d=(-1, -1))
    up.dot([(3, 18), (4, 20), (7, 16), (9, 19), (11, 17)], 'N')
    up.poly([(17, 13), (39, 14), (41, 22), (17, 22)], 'o')                     # 大衣平躺
    up.shade('o', 'O', d=(1, 1))
    up.poly([(17, 14), (22, 14), (22, 17), (17, 17)], 'W')                     # 领口的脏衬衫
    up.shade('W', 'x', d=(0, 1))
    up.line([(27, 21), (39, 21)], 'O')
    hd = _ge_head('ko')
    g = hd.a[3:22, 14:28]                                  # 头 + 刘海的包围盒（y 3–21、x 14–27）
    r = np.rot90(g, 1)                                     # 逆时针：头顶朝左、脸朝上、下巴朝右
    hp = SE._Pix(W, H)
    hp.a[H - 2 - r.shape[0]:H - 2, 4:4 + r.shape[1]] = r
    up.paste(hp, ring='k')
    ident = lambda p: p
    _ge_arm(up, [(24, 15), (27, 12), (29, 12)], 'fwd', (29, 9), ident)          # 远侧：搭在肚子上
    _ge_arm(up, [(22, 18), (27, 21), (32, 21)], 'fwd', (32, 16), ident)         # 近侧：摊在身边的地上
    lo.paste(up)
    lo.outline('k')
    return lo


def _geil_frames():
    return {'walk': [_ge_walk(f) for f in range(4)], 'kick': [_ge_kick(f) for f in range(2)],
            'throw': [_ge_throw(f) for f in range(2)], 'down': [_ge_down()]}


# 自检：原部件原样传进去 = 原 idle 两帧（36×52 画布、不平移）
if _ge_pose().grid() != SE._geil(0).grid() or _ge_pose(hy=-1, sway=1).grid() != SE._geil(1).grid():
    raise ValueError('J·凯尔部件复现不出原 idle（sprites_enemies._geil 变了？）')
_GE_DESC = {
    'walk': '佝偻着走 4 帧：两腿交替迈步（近侧在前 → 过身抬腿 → 远侧在前 → 过身抬腿），过身的帧上身抬 1 px；'
            '上身、头、两只右手照 idle（手跟着步子一上一下），裤腿从大衣下摆底下出来',
    'kick': '0 提膝蓄力（大腿抬平、上身后仰、一只右手举在脸前一只甩到身后）；1 往前蹬直（鞋底朝前，鞋在脚点右 19–23 px、离地 11–19 px），两手甩到身后',
    'throw': '0 弯腰屈膝、近侧右手在脚前地上抓一把沙土；1 直起身往前上方一甩、张开手掌，扇形沙土往前飞（脚点右 20–40 px、离地 26–51 px）',
    'down': '被刺倒地（不画血）：仰面、头朝左（叉叉眼张着嘴），长发铺在地上，两只右手（手指都朝右）一只搭在肚子上一只摊在身边，鞋尖朝上',
}
_GE_ANCHOR = {'walk': (18, 52), 'kick': (18 + _GE_O[0], 52 + _GE_O[1]), 'throw': (18 + _GE_O[0], 52 + _GE_O[1]),
              'down': (_GE_DW // 2, _GE_DH)}
for _act, _frames in _geil_frames().items():
    _name = 'jgeil.' + _act
    if _name in sprite._REG: raise ValueError('新动作与原注册冲突：' + _name)
    sprite.define(_name, [p.grid() for p in _frames], pal=SE.PAL_GEIL, anchor=_GE_ANCHOR[_act],
                  fps={'walk': 6, 'kick': 6, 'throw': 5, 'down': 1}[_act], desc=_GE_DESC[_act])
    NEW.append(_name)
ONESHOT.add('jgeil.throw')                  # 扬尘只播一遍、停在扬出去那一帧（kick / down 已在上面的 ONESHOT 里）

# 规划使用原cid的形态动作；专用cid仍有全套走路和受击供世界实体使用。
for cid,act,source in [('polnareff','kid','polnareff_kid.idle'),('jotaro','kid','jotaro_kid.idle'),('polnareff','possessed','polnareff_possessed.idle')]:
    sd=sprite.get(source); name=cid+'.'+act
    sprite.define(name,sd.frames,anchor=sd.anchor,fps=3,desc='剧情形态：'+act); NEW.append(name)
