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
# l0–l2 照旧；l3（最大一级）原来和 idle 是同一张 24×24（烘焙去重成别名），2026-10-11 第4章改由 empress_l3 单独画
define('empress','女帝',{**{f'l{s}_idle':2 for s in range(3)},**{f'l{s}_bite':1 for s in range(3)},'idle':2,'walk':2,'talk':2,'hurt':1,'down':1,'bite':1},empress)


# =====================================================================================
#  女帝 l3（第4章：成长到 3 级，2026-10-11）
# =====================================================================================
# 从乔瑟夫左臂上长出来的女帝上半身：和 l2 / idle 同一个造型（粉色皮肤、右边一块浅色脸、深紫的尖角耳、短手臂），
# 只是更大、更狰狞——一对尖耳、斜吊的怒眼（带一点反光）、咧到耳根的嘴和两颗獠牙、带爪的两只手。
# 尺寸按 l0 8 → l1 12 → l2 18（每级约 ×1.5）往下排：l3 含描边 30 px 高、32 px 宽（画布 32×30，锚点 (14, 30) = 长在手臂上的根）。
# 原尺寸贴在乔瑟夫（idle 高 48 px）手上约半个多人高；剧情按 scale .34+级×.06 缩到 0.52 倍时约 16 px（见 _preview\ch4_女帝缩放对照.png）。
# 用原工程 sprites_enemies._Pix 的画法（填色 + 自动明暗 + 自动 1 px 描边），描边色同其他几级（K）。
from assets import sprites_enemies as SE    # noqa: E402

EMP_PAL = {'k': '#14121e', 'm': '#ca6c8a', 'M': '#9a4a74', 'l': '#e29096', 'L': '#ca6c8a',
           'P': '#80365e', 'Q': '#5c2446', 'v': '#442248', 'V': '#7a4a82', 'e': '#14121e', 'y': '#f8e4c4',
           'w': '#f8e4c4', 'W': '#c8b49c', 'r': '#5a1428'}
_L3_W, _L3_H, _L3_ROOT = 32, 30, 14          # 根（底边）中点 x = 14 → 锚点 (14, 30)


def _l3_claw(P, x, y, up, spread=0):
    """三根带爪的手指：up=True 朝上，False 朝右（往前抓）。"""
    if up:
        for dx in (-2, 0, 2 + spread):
            P.seg([(x, y), (x + dx, y - 3)], 0.6, 'm')
            P.dot([(x + dx, y - 4)], 'v')
    else:
        for dy in (-2, 0, 2 + spread):
            P.seg([(x, y), (x + 3, y + dy)], 0.6, 'm')
            P.dot([(x + 4, y + dy)], 'v')


def empress_l3(act, i):
    bite = act.endswith('bite')
    bob = 0 if bite else i % 2                 # idle 第 1 帧整个上身往下沉 1 px（呼吸）
    hx, hy = (3, -1) if bite else (0, bob)     # 咬的时候头往前探
    W, H = _L3_W, _L3_H
    P = SE._Pix(W, H)
    # 根：从手臂上鼓起来的一团肉（深色），往上收成腰
    root = SE._Pix(W, H)
    root.ell(9, 21, 20, 33, 'M')
    root.ell(6, 26, 12, 32, 'M')
    root.ell(17, 25, 23, 32, 'M')
    root.shade('M', 'P', d=(1, 1), n=2)
    root.dot([(9, 27), (13, 25), (16, 27), (20, 28)], 'P')
    root.rect(0, 29, W - 1, H - 1, '.')
    # 远侧手臂（头后面）：举起来，爪子朝上
    far = SE._Pix(W, H)
    if bite:
        far.seg([(11, 17 + bob), (16, 13), (24, 11)], 1.3, 'm')
        _l3_claw(far, 25, 11, False, 1)
    else:
        far.seg([(10, 18 + bob), (5, 19 + bob), (3, 15 + bob)], 1.3, 'm')
        _l3_claw(far, 3, 14 + bob, True)
    far.shade('m', 'M', d=(1, 1))
    # 躯干
    body = SE._Pix(W, H)
    body.poly([(9, 17 + bob), (21, 17 + bob), (20, 23), (11, 23)], 'm')
    body.shade('m', 'M', d=(1, 1))
    body.dot([(13, 20 + bob), (14, 21), (18, 19 + bob)], 'M')          # 几道青筋似的暗纹
    # 头：大圆脑袋 + 右边浅色的脸；两只尖耳（深紫）从头顶两侧竖起来
    head = SE._Pix(W, H)
    X = lambda x: x + hx
    Y = lambda y: y + hy
    head.poly([(X(7), Y(9)), (X(2), Y(1)), (X(10), Y(5))], 'v')
    head.poly([(X(17), Y(4)), (X(22), Y(0)), (X(21), Y(6))], 'v')
    head.shade('v', 'V', d=(-1, -1))
    head.ell(X(6), Y(3), X(24), Y(19), 'm')
    head.shade('m', 'M', d=(1, 1))
    head.ell(X(12), Y(5), X(25), Y(17), 'l')
    head.shade('l', 'L', d=(1, 1))
    # 怒眼：两只往里斜吊的黑眼 + 一点反光
    head.poly([(X(13), Y(8)), (X(17), Y(10)), (X(16), Y(12)), (X(13), Y(10))], 'e')
    head.poly([(X(20), Y(10)), (X(24), Y(7)), (X(24), Y(10)), (X(21), Y(12))], 'e')
    head.dot([(X(14), Y(9)), (X(22), Y(9))], 'y')
    head.dot([(X(18), Y(8)), (X(19), Y(9))], 'M')                     # 眉心皱起
    head.dot([(X(22), Y(13)), (X(23), Y(14))], 'M')                   # 鼻子
    if bite:
        # 张到最大：上下两排尖牙，嘴里暗红
        head.rect(X(14), Y(14), X(25), Y(20), 'e')
        head.rect(X(15), Y(15), X(24), Y(19), 'r')
        for x in range(15, 25, 2):
            head.dot([(X(x), Y(15)), (X(x + 1), Y(19))], 'w')
        head.dot([(X(16), Y(16)), (X(23), Y(16))], 'w')               # 两颗长獠牙
    else:
        # 咧到耳根的笑：一条嘴缝往两边翘，两颗獠牙从上唇垂下来
        head.line([(X(13), Y(14)), (X(15), Y(16)), (X(23), Y(16)), (X(25), Y(14))], 'e')
        head.dot([(X(16), Y(17)), (X(22), Y(17))], 'w')
        head.dot([(X(16), Y(18)), (X(22), Y(18))], 'W')
    # 近侧手臂：往前伸，爪子朝前抓
    near = SE._Pix(W, H)
    if bite:
        near.seg([(20, 18), (25, 21), (28, 19)], 1.3, 'm')
        _l3_claw(near, 28, 19, False, 1)
    else:
        near.seg([(20, 18 + bob), (24, 22), (27, 20 + bob)], 1.3, 'm')
        _l3_claw(near, 27, 20 + bob, False)
    near.shade('m', 'M', d=(1, 1))
    P.paste(far)
    P.paste(root, ring='k')
    P.paste(body, ring='k')
    P.paste(head, ring='k')
    P.paste(near, ring='k')
    P.outline('k')
    return P.grid()


for _act, _n in (('l3_idle', 2), ('l3_bite', 1)):
    _name = 'empress.' + _act
    sprite.define(_name, [empress_l3(_act, _i) for _i in range(_n)], pal=EMP_PAL, anchor=(_L3_ROOT, _L3_H),
                  fps=3, desc='女帝：' + _act + '（第 3 级，最大：尖耳、怒眼、獠牙、带爪的两只手，含描边 32×30）')
    NEW.append(_name)
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
