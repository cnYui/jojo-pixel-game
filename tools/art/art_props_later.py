"""第三部后续道具：固定像素尺寸，伪装物件使用正常／眨眼状态。"""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

K=(26,16,32)
METAL=(142,162,178)
HI=(230,236,218)
GOLD=(236,194,76)

SPECS={
 'ship_eye_a':(2,12,8,'甲板的眼睛'), 'ship_eye_b':(2,10,10,'舱壁的眼睛'), 'ship_eye_c':(2,16,8,'水管的眼睛'),
 'shark':(2,40,16,'海中的鲨鱼'), 'barnacle':(2,6,6,'藤壶生长'), 'hook':(1,24,16,'货轮吊钩'),
 'slime_puddle':(1,20,6,'黄色黏液'), 'tar_barrel':(2,16,20,'焦油桶／倒出的焦油'), 'mirror_shard':(1,6,6,'反射用镜子碎片'),
 'fork':(1,10,4,'恋人刺入义手的叉子'), 'cessna':(2,64,24,'塞斯纳飞机／受损状态'),
 'toy_knife':(1,12,5,'梦境外的玩具刀'), 'toy_box':(1,18,14,'玩具盒'), 'genie_lamp':(1,24,16,'审判藏身的神灯'),
 'tooth':(2,24,20,'巨牙／碎牙'), 'dive_helmet':(1,16,16,'潜水头盔叠层'), 'joseph_hand':(1,14,9,'断落的机械义手'),
 'pebble':(1,5,4,'声音诱饵石子'), 'anubis_sword':(1,34,10,'阿努比斯神弯刀'),
 'socket':(1,10,12,'巴斯特女神磁力插座'), 'train':(2,96,44,'列车／轮组状态'), 'metal_junk':(4,16,16,'螺丝／钉子／剪刀／铁链'),
 'mirror_stand':(1,18,32,'太阳使者的镜面伪装'), 'oil_drum':(1,16,22,'地下通道油桶'),
 'atum_doll_a':(1,12,16,'波鲁纳雷夫灵魂人偶'), 'atum_doll_b':(1,12,16,'花京院灵魂人偶'), 'atum_doll_c':(1,12,16,'乔瑟夫灵魂人偶'),
 'sax':(1,16,26,'肯尼G的萨克斯'), 'road_sign':(1,12,40,'DIO使用的道路标志'),
 'magazine_vest':(1,24,28,'承太郎藏在制服内的杂志'), 'truck':(1,64,36,'乔瑟夫的皮卡'), 'senator_car':(1,72,28,'议员的豪华轿车'),
 'blanket':(2,56,14,'霍莉的薄被／掀开状态'), 'rock':(1,24,18,'沙漠中的独立岩石'),
 'baby_cradle':(2,36,24,'玛尼修男孩的摇篮／摆动状态'), 'ice_wall':(2,56,52,'荷鲁斯的冰墙／碎裂状态'),
 'upper_tooth':(2,30,42,'女教皇上颌巨牙／碎裂'), 'lower_tooth':(2,30,42,'女教皇下颌巨牙／碎裂'),
 'hide_wardrobe':(2,58,86,'藏点：衣柜关／开'), 'aquarium':(2,84,48,'藏点：鱼缸盖关／开'),
 'hide_bed':(2,122,47,'藏点：床单垂下／掀起'), 'hide_curtain':(2,80,86,'藏点：窗帘闭合／拉开'),
 'hide_crate':(2,40,36,'藏点：木箱盖关／开'), 'hide_cupboard':(2,50,76,'藏点：橱柜关／开'),
 'cane':(1,8,36,'恩多尔的白色手杖'), 'tea_cup':(1,12,10,'被盖布划穿的杯子'),
 'cake':(1,14,12,'伊奇藏在纸盒里的蛋糕'), 'cart':(1,54,36,'橙子商人的手推车'),
 'hat':(1,28,13,'荷尔·贺斯掉落的棕色牛仔帽'),
}
DISGUISES=('pressure_gauge','valve','wrench','metal_cup','razor','binoculars','pipe_elbow','radio','diving_boot','oxygen_tank','compass','hatch_handle')
for key in DISGUISES:
    SPECS['disguise_'+key]=(2,16,16,'女教皇伪装：'+key+'，正常／眨眼')


def draw(pid,fi):
    n,w,h,desc=SPECS[pid]
    im=Image.new('RGBA',(w,h)); d=ImageDraw.Draw(im)
    if pid=='hat':
        d.polygon([(0,8),(5,7),(7,1),(17,0),(22,6),(27,7),(25,11),(7,12),(1,10)],fill=(148,88,50),outline=K)
        d.polygon([(7,2),(11,1),(13,4),(17,1),(21,7),(6,7)],fill=(186,116,64),outline=K)
        d.line((8,3,10,2,13,5,16,2),fill=(226,162,88))
        d.rectangle((6,6,21,8),fill=(66,44,42),outline=K)
        d.line((3,9,7,10,23,9),fill=(218,150,76))
    elif pid=='cane':
        d.arc((0,0,7,7),180,360,fill=K,width=3); d.arc((0,0,7,7),180,360,fill=HI)
        d.line((7,4,7,35),fill=K,width=3); d.line((7,4,7,35),fill=(232,230,202)); d.rectangle((5,31,7,35),fill=(70,62,62))
    elif pid=='tea_cup':
        d.ellipse((0,6,10,9),fill=(222,222,200),outline=K); d.rectangle((2,2,8,7),fill=(238,234,204),outline=K)
        d.ellipse((2,0,8,3),fill=(92,64,52),outline=(240,232,206)); d.arc((7,2,11,7),265,95,fill=(220,220,190),width=2)
        d.line((3,3,3,5),fill=HI)
    elif pid=='cake':
        d.polygon([(1,4),(7,1),(12,4),(12,10),(1,10)],fill=(234,208,146),outline=K)
        d.rectangle((2,6,11,7),fill=(148,76,50)); d.polygon([(1,4),(7,1),(12,4),(6,6)],fill=(246,236,196),outline=K)
        d.ellipse((6,0,9,3),fill=(192,62,72),outline=K); d.rectangle((0,10,13,11),fill=(224,216,184),outline=K)
    elif pid=='cart':
        d.rectangle((4,12,43,25),fill=(148,94,62),outline=K); d.rectangle((2,9,45,13),fill=(194,138,76),outline=K)
        for x in (12,35): d.ellipse((x-7,21,x+7,35),fill=(56,48,46),outline=K); d.ellipse((x-3,25,x+3,31),fill=(166,130,82),outline=K)
        for y in (6,10):
            for x in range(8+(y%3)*2,42,8): d.ellipse((x,y-4,x+7,y+3),fill=(234,152,54),outline=(128,84,48)); d.point((x+2,y-2),fill=(250,206,94))
        d.line((42,15,53,8,53,5),fill=K,width=3); d.line((43,15,52,8),fill=(186,144,90))
    elif pid=='blanket':
        d.polygon([(0,10),(8,1),(42,0),(55,7),(55,13),(0,13)],fill=(162,196,182),outline=K)
        for x in range(8,52,10): d.line((x,3,x-4,12),fill=(110,156,144))
        d.line((8,2,41,1,51,6),fill=(222,230,204),width=2)
        if fi: d.polygon([(4,9),(25,8),(42,4),(46,9),(28,13),(4,13)],fill=(204,218,196),outline=(108,142,134))
    elif pid=='rock':
        d.polygon([(0,17),(3,5),(9,0),(19,2),(23,12),(21,17)],fill=(156,132,100),outline=K)
        d.polygon([(3,5),(9,0),(12,7),(8,15)],fill=(194,166,124)); d.line((12,7,19,2,17,12),fill=(96,86,76),width=2)
    elif pid=='baby_cradle':
        shift=fi; d.rectangle((2+shift,7,33+shift,19),fill=(140,102,72),outline=K)
        d.ellipse((4+shift,4,31+shift,13),fill=(238,218,172),outline=K)
        for x in range(6,32,6): d.line((x+shift,12,x+shift,19),fill=(86,62,56),width=2)
        for x in (5,29): d.line((x+shift,18,x+shift,22),fill=K,width=3)
        d.arc((0,13,35,25),0,180,fill=(178,136,90),width=3)
        d.line((5,7,29,7),fill=(248,236,198)); d.rectangle((7,6,15,10),fill=(246,234,198),outline=(184,166,134))
    elif pid=='ice_wall':
        for x,y in ((0,18),(12,7),(24,0),(37,13),(46,24)):
            points=[(x,51),(x+1,y+10),(x+6,y),(min(55,x+13),y+9),(min(55,x+15),51)]
            d.polygon(points,fill=(118,180,210),outline=K)
            d.line((x+5,y+5,x+4,44),fill=(226,242,232),width=2)
            d.line((x+9,y+12,x+13,47),fill=(62,114,160),width=2)
        if fi:
            for points in ([(5,20),(18,32),(11,48)],[(28,7),(25,22),(37,31),(29,48)],[(42,24),(50,32),(46,45)]): d.line(points,fill=K,width=2)
    elif pid in ('upper_tooth','lower_tooth'):
        d.polygon([(2,1),(10,0),(26,3),(29,11),(24,27),(17,41),(9,34),(1,13)],fill=(242,232,196),outline=K)
        d.line((9,3,7,14,14,33),fill=HI,width=2); d.line((25,8,22,22,17,34),fill=(184,160,134),width=2)
        if fi:
            d.line((3,12,13,17,24,12,21,24,12,28),fill=K,width=2)
            d.polygon([(6,30),(12,25),(16,30),(13,38)],fill=(0,0,0,0))
        if pid=='upper_tooth': im=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    elif pid=='hide_wardrobe':
        d.rectangle((3,2,54,82),fill=(118,78,60),outline=K); d.rectangle((0,0,57,5),fill=(174,120,76),outline=K)
        for x in (7,29):
            d.rectangle((x,8,x+20,79),fill=(152,100,66),outline=K); d.rectangle((x+3,12,x+17,71),outline=(190,134,84))
        if fi:
            d.rectangle((11,9,45,77),fill=(44,36,42),outline=K)
            d.polygon([(4,8),(13,12),(13,76),(4,80)],fill=(174,116,74),outline=K)
            d.polygon([(45,12),(54,8),(54,80),(45,76)],fill=(174,116,74),outline=K)
            d.line((17,17,39,17),fill=METAL); d.polygon([(21,20),(17,26),(22,50),(33,50),(36,25),(30,20)],fill=(102,136,142),outline=K)
        else:
            for x in (24,33): d.ellipse((x,40,x+2,43),fill=GOLD)
        for x in (7,48): d.rectangle((x,82,x+3,85),fill=(80,56,48),outline=K)
    elif pid=='aquarium':
        d.rectangle((2,17,81,35),fill=(62,132,162),outline=METAL,width=2)
        d.rectangle((5,19,78,33),fill=(104,180,194)); d.line((8,20,74,20),fill=(220,236,214))
        for x,y in ((15,28),(41,26),(64,30)):
            d.polygon([(x,y),(x+7,y-2),(x+11,y),(x+7,y+2)],fill=(226,152,78),outline=K)
            d.polygon([(x+10,y),(x+14,y-3),(x+14,y+3)],fill=(208,128,66)); d.point((x+3,y),fill=K)
        for x in (9,56): d.line((x,33,x+1,25,x-2,24),fill=(58,118,92),width=2)
        d.rectangle((0,35,83,40),fill=(128,86,66),outline=K)
        for x in (6,74): d.rectangle((x,40,x+4,47),fill=(88,62,54),outline=K)
        if fi: d.polygon([(0,16),(6,0),(80,0),(83,16)],fill=(174,148,104),outline=K); d.polygon([(9,3),(74,3),(78,12),(6,12)],fill=(38,58,66),outline=METAL)
        else: d.rectangle((0,14,83,18),fill=(160,120,78),outline=K)
    elif pid=='hide_bed':
        d.rectangle((2,19,118,40),fill=(154,106,74),outline=K); d.rectangle((0,13,121,27),fill=(232,214,176),outline=K)
        d.rectangle((5,9,33,18),fill=(248,238,204),outline=(168,146,124))
        for x in (5,112): d.rectangle((x,39,x+4,46),fill=(98,64,52),outline=K)
        if fi:
            d.rectangle((17,31,106,40),fill=(44,34,42),outline=K)
            d.polygon([(34,13),(108,13),(118,21),(53,23),(41,29),(34,24)],fill=(210,192,158),outline=(142,120,104))
        else:
            d.polygon([(34,14),(118,14),(119,40),(36,40)],fill=(184,160,126),outline=(130,106,90))
            for x in range(42,112,12): d.line((x,17,x+1,38),fill=(216,190,152))
    elif pid=='hide_curtain':
        d.line((0,2,79,2),fill=K,width=3); d.line((0,2,79,2),fill=GOLD)
        for x in (4,42):
            pts=[(x,4),(x+33,4),(x+29 if fi else x+35,83),(x+2,85)]
            if fi: pts=[(x,4),(x+33,4),(x+7 if x<30 else x+29,44),(x+11 if x<30 else x+33,83),(x-1 if x<30 else x+25,85),(x+1 if x<30 else x+26,44)]
            d.polygon(pts,fill=(172,92,78),outline=K)
            for xx in range(x+5,x+30,7): d.line((xx,6,xx-2 if x<30 else xx+2,40 if fi else 82),fill=(216,132,104))
        if fi:
            for x in (10,66): d.line((x-4,44,x+4,44),fill=GOLD,width=2)
    elif pid=='hide_crate':
        d.rectangle((2,17,37,34),fill=(160,114,72),outline=K)
        for y in (22,28): d.line((3,y,36,y),fill=(98,68,52))
        for x in (6,31): d.rectangle((x,17,x+2,34),fill=(192,146,92),outline=K)
        if fi:
            d.rectangle((6,18,33,23),fill=(42,34,40),outline=K)
            d.polygon([(1,16),(6,1),(35,0),(38,16)],fill=(190,142,90),outline=K)
            d.line((8,4,32,3),fill=(238,184,116)); d.line((7,9,33,8),fill=(110,76,54))
        else: d.polygon([(1,15),(5,10),(34,10),(39,15)],fill=(196,146,88),outline=K)
    elif pid=='hide_cupboard':
        d.rectangle((3,4,46,72),fill=(138,92,66),outline=K); d.rectangle((0,0,49,5),fill=(186,130,80),outline=K)
        d.rectangle((7,8,42,24),fill=(62,46,48),outline=K); d.line((7,16,42,16),fill=(182,126,84),width=2)
        for x in (11,24,34): d.ellipse((x,10,x+6,14),fill=(236,218,182),outline=K)
        d.rectangle((6,29,43,69),fill=(168,112,70),outline=K); d.line((25,29,25,69),fill=K)
        if fi:
            d.rectangle((13,32,36,66),fill=(44,34,40),outline=K)
            for x in (7,37): d.polygon([(x,29),(x+5,34),(x+5,67),(x,69)],fill=(196,138,84),outline=K)
        else:
            for x in (21,29): d.point((x,48),fill=GOLD)
        for x in (5,41): d.rectangle((x,72,x+3,75),fill=(92,58,48),outline=K)
    elif pid.startswith('ship_eye'):
        d.ellipse((0,1,w-1,h-2),fill=(164,106,122),outline=K)
        if not fi: d.ellipse((w//2-2,2,w//2+2,h-3),fill=(242,222,174),outline=K); d.point((w//2,3),fill=HI)
        else: d.line((1,h//2,w-2,h//2),fill=K)
    elif pid=='shark':
        d.polygon([(1,10),(8,4),(28,4),(35,8),(39,4),(37,11),(39,15),(33,12),(8,13)],fill=(84,132,160),outline=K)
        d.polygon([(13,6),(18,0),(21,6)],fill=(84,132,160),outline=K)
        d.polygon([(11,11),(18,9),(16,15-fi)],fill=(174,196,196),outline=K); d.point((6,7),fill=K)
        d.line((1,10,10,11),fill=(230,230,206)); d.line((25,6,24,11),fill=(54,94,122))
    elif pid=='barnacle':
        d.polygon([(0,5),(1,2),(3,0 if fi else 1),(5,3),(5,5)],fill=(176,158,134),outline=K); d.ellipse((2,2,4,4),fill=(76,68,78))
    elif pid=='hook':
        d.line((11,0,11,6),fill=K,width=4); d.line((11,0,11,6),fill=METAL,width=2)
        d.arc((5,4,20,15),0,255,fill=K,width=5); d.arc((5,4,20,15),0,255,fill=METAL,width=3); d.point((6,7),fill=HI)
    elif pid=='slime_puddle':
        d.polygon([(0,5),(1,3),(5,2),(7,0),(11,2),(17,2),(19,5)],fill=(226,198,58),outline=K); d.line((4,3,14,3),fill=(248,232,126))
    elif pid in ('tar_barrel','oil_drum'):
        d.rectangle((1,2,w-2,h-3),fill=(78,86,98),outline=K); d.ellipse((1,0,w-2,4),fill=METAL,outline=K)
        for y in (6,h-7): d.rectangle((0,y,w-1,y+2),fill=(116,132,142),outline=K)
        if fi: d.polygon([(3,h-3),(8,h-1),(15,h-1),(13,h-4)],fill=(24,24,38),outline=K)
    elif pid=='mirror_shard':
        d.polygon([(0,4),(4,0),(5,3),(3,5)],fill=(150,198,214),outline=K); d.line((1,4,4,2),fill=HI)
    elif pid in ('fork','toy_knife','anubis_sword'):
        if pid=='fork':
            d.line((0,2,7,2),fill=METAL,width=2)
            for y in (0,2,3): d.line((6,y,9,y),fill=HI)
        elif pid=='toy_knife':
            d.rectangle((0,2,4,4),fill=(152,80,64),outline=K); d.polygon([(4,2),(11,0),(9,3),(5,3)],fill=METAL,outline=K)
        else:
            d.polygon([(7,6),(21,4),(32,0),(33,2),(22,7),(8,8)],fill=(222,230,220),outline=K)
            d.line((10,6,30,2),fill=HI); d.line((6,3,8,9),fill=GOLD,width=2); d.line((1,7,6,6),fill=(118,70,52),width=3)
    elif pid=='cessna':
        d.polygon([(0,14),(16,9),(49,9),(60,11),(63,15),(16,18),(2,17)],fill=(226,222,190),outline=K)
        d.polygon([(22,11),(34,0),(42,0),(37,12),(51,23),(39,23),(27,16)],fill=(220,76,70),outline=K)
        d.polygon([(2,12),(5,2),(10,2),(12,13)],fill=(220,76,70),outline=K); d.rectangle((48,10,55,13),fill=(78,132,166),outline=K)
        d.line((62,6,62,20),fill=K,width=2)
        if fi: d.line((24,7,36,15),fill=K,width=2); d.polygon([(53,8),(50,4),(55,3),(57,0),(60,7)],fill=(102,102,106),outline=K)
    elif pid=='toy_box':
        d.rectangle((0,4,17,13),fill=(148,96,74),outline=K); d.polygon([(0,4),(3,0),(17,0),(17,4)],fill=(224,156,94),outline=K)
        d.rectangle((6,6,11,9),fill=(234,194,96),outline=K); d.line((2,11,15,11),fill=(92,62,58))
    elif pid=='genie_lamp':
        d.ellipse((4,7,19,13),fill=GOLD,outline=K); d.polygon([(6,8),(1,6),(0,9),(7,12)],fill=GOLD,outline=K)
        d.arc((15,3,23,12),250,100,fill=GOLD,width=3); d.ellipse((9,5,16,8),fill=(248,216,130),outline=K)
        d.rectangle((11,3,14,5),fill=GOLD,outline=K); d.rectangle((8,13,17,15),fill=(182,130,58),outline=K)
    elif pid=='tooth':
        if not fi:
            d.polygon([(1,1),(5,0),(20,0),(23,3),(21,13),(16,19),(11,14),(6,19),(2,12)],fill=(240,230,194),outline=K)
            d.line((5,2,4,10,7,15),fill=HI,width=2); d.line((18,2,18,9,15,14),fill=(174,156,140))
        else:
            for points in ([(1,16),(4,8),(9,12),(7,19)],[(10,18),(12,3),(18,7),(17,17)],[(18,18),(20,10),(23,17)]): d.polygon(points,fill=(240,230,194),outline=K)
    elif pid=='dive_helmet':
        d.ellipse((0,0,15,15),fill=(158,138,80),outline=K); d.ellipse((3,3,12,12),fill=(48,92,120),outline=HI)
        d.line((5,5,10,5),fill=(152,218,224)); d.rectangle((4,13,11,15),fill=(122,102,72),outline=K)
    elif pid=='joseph_hand':
        d.polygon([(1,4),(3,3),(4,0),(6,0),(6,3),(11,2),(13,4),(12,8),(4,8)],fill=(166,114,70),outline=K)
        for x in (7,9,11): d.line((x,3,x,6),fill=(100,64,54))
        d.rectangle((0,4,3,8),fill=METAL,outline=K)
    elif pid=='pebble':
        d.polygon([(0,3),(1,1),(3,0),(4,3)],fill=(172,158,124),outline=K); d.point((2,1),fill=HI)
    elif pid=='socket':
        d.rectangle((0,0,9,11),fill=(232,222,174),outline=K); d.ellipse((2,3,7,8),fill=(172,162,134),outline=K)
        d.rectangle((3,4,3,6),fill=K); d.rectangle((6,4,6,6),fill=K); d.point((5,8),fill=K)
    elif pid=='train':
        d.rectangle((1,3,95,35),fill=(90,116,142),outline=K); d.rectangle((4,0,91,5),fill=(56,74,96),outline=K)
        for x in range(9,88,17): d.rectangle((x,8,x+11,22),fill=(172,212,220),outline=K); d.line((x+1,9,x+9,9),fill=HI)
        d.rectangle((0,25,95,28),fill=(230,188,66)); d.rectangle((0,34,95,37),fill=(46,48,62),outline=K)
        for x in (13,31,62,80): d.ellipse((x,34,x+9,43),fill=(42,44,54),outline=K); d.line((x+2,37+fi,x+7,40-fi),fill=METAL)
    elif pid=='metal_junk':
        if fi==0: d.line((3,12,12,3),fill=METAL,width=3); d.line((8,1,14,7),fill=K,width=3)
        elif fi==1: d.line((3,14,11,4),fill=METAL,width=2); d.line((8,1,14,5),fill=HI,width=2)
        elif fi==2:
            d.ellipse((0,9,6,15),outline=METAL,width=2); d.ellipse((8,9,14,15),outline=METAL,width=2); d.line((3,10,13,0),fill=HI); d.line((11,10,2,0),fill=HI)
        else:
            for x in (1,5,9): d.ellipse((x,2+x//2,x+5,9+x//2),outline=METAL,width=2)
    elif pid=='mirror_stand':
        d.rectangle((0,0,17,24),fill=(112,172,192),outline=METAL,width=2); d.line((3,19,14,6),fill=HI,width=2)
        d.line((9,25,9,30),fill=K,width=3); d.line((4,31,14,31),fill=METAL,width=2)
    elif pid.startswith('atum_doll'):
        j=ord(pid[-1])-97; cols=((228,230,210),(74,130,92),(150,102,74)); c=cols[j]
        d.rectangle((3,6,8,12),fill=c,outline=K); d.rectangle((3,12,4,15),fill=c,outline=K); d.rectangle((7,12,8,15),fill=c,outline=K)
        d.ellipse((2,1,9,7),fill=(216,170,126),outline=K); d.rectangle((2,0,9,2),fill=cols[j],outline=K); d.point((7,4),fill=K)
    elif pid=='sax':
        d.line((5,2,10,5,8,18,11,22),fill=K,width=5); d.line((5,2,10,5,8,18,11,22),fill=GOLD,width=3)
        d.arc((7,17,15,25),0,250,fill=GOLD,width=3); d.ellipse((10,19,15,23),fill=(104,70,48),outline=GOLD)
        for y in (8,11,14): d.point((9,y),fill=HI)
    elif pid=='road_sign':
        d.line((6,10,6,39),fill=K,width=3); d.line((6,10,6,39),fill=METAL)
        d.polygon([(3,0),(8,0),(11,3),(11,8),(8,11),(3,11),(0,8),(0,3)],fill=(190,48,62),outline=HI)
        d.line((3,5,8,5),fill=HI,width=2)
    elif pid=='magazine_vest':
        for x,y in ((0,0),(11,3),(2,12),(12,15)):
            d.rectangle((x,y,x+10,y+11),fill=(228,220,190),outline=K); d.rectangle((x+2,y+2,x+8,y+4),fill=(190,66,74)); d.line((x+2,y+7,x+8,y+7),fill=(94,122,144))
    elif pid in ('truck','senator_car'):
        sedan=pid=='senator_car'; c=(42,52,68) if sedan else (166,84,60)
        d.polygon([(0,h-11),(2,h-18),(15,h-18),(25,2),(w-22,2),(w-13,h-17),(w-2,h-16),(w-1,h-8)],fill=c,outline=K)
        d.polygon([(19,h-18),(27,5),(w-23,5),(w-16,h-18)],fill=(100,152,172),outline=K)
        d.line((39,5,39,h-18),fill=K,width=2); d.line((3,h-10,w-4,h-10),fill=METAL)
        for x in (12,w-24): d.ellipse((x,h-15,x+13,h-1),fill=(24,24,34),outline=K); d.ellipse((x+4,h-11,x+9,h-6),fill=METAL)
        if not sedan: d.rectangle((1,4,21,h-18),fill=(146,74,54),outline=K); d.line((1,4,21,4),fill=(210,132,92))
    elif pid.startswith('disguise_'):
        key=pid[9:]
        if key in ('pressure_gauge','compass'):
            d.ellipse((1,1,14,14),fill=METAL,outline=K); d.ellipse((3,3,12,12),fill=(224,222,182),outline=K)
            d.line((8,8,11 if key=='pressure_gauge' else 5,4),fill=(180,60,62),width=2)
        elif key=='valve':
            d.ellipse((1,1,14,14),outline=(182,62,62),width=3); d.line((3,3,12,12),fill=METAL,width=2); d.line((3,12,12,3),fill=METAL,width=2)
        elif key=='wrench':
            d.line((2,14,11,4),fill=K,width=5); d.line((2,14,11,4),fill=METAL,width=3); d.arc((8,0,15,7),0,245,fill=METAL,width=3)
        elif key=='metal_cup':
            d.rectangle((2,3,11,13),fill=METAL,outline=K); d.ellipse((2,1,11,5),fill=(64,82,100),outline=HI); d.arc((9,4,15,11),260,105,fill=METAL,width=2)
        elif key=='razor':
            d.rectangle((1,1,14,5),fill=METAL,outline=K); d.rectangle((6,5,9,14),fill=(86,100,112),outline=K); d.line((2,2,13,2),fill=HI)
        elif key=='binoculars':
            for x in (1,9): d.rectangle((x,1,x+5,11),fill=METAL,outline=K); d.ellipse((x,9,x+5,14),fill=(46,72,90),outline=K)
            d.line((5,5,10,5),fill=METAL,width=3)
        elif key=='pipe_elbow':
            d.line((2,14,2,7,7,2,14,2),fill=K,width=5); d.line((2,14,2,7,7,2,14,2),fill=METAL,width=3)
        elif key=='radio':
            d.rectangle((1,4,14,14),fill=(74,94,110),outline=K); d.line((12,4,14,0),fill=METAL); d.rectangle((3,6,10,10),fill=(168,198,172),outline=K)
            for x in (4,7,10): d.point((x,12),fill=HI)
        elif key=='diving_boot':
            d.polygon([(3,0),(9,0),(9,9),(14,11),(15,15),(1,15),(1,11),(3,10)],fill=(68,88,106),outline=K); d.line((3,14,13,14),fill=METAL)
        elif key=='oxygen_tank':
            d.rounded_rectangle((3,3,12,15),radius=3,fill=METAL,outline=K); d.rectangle((6,0,9,3),fill=(102,132,146),outline=K); d.rectangle((4,8,11,10),fill=(220,184,68))
        elif key=='hatch_handle':
            d.arc((2,2,13,13),180,360,fill=K,width=5); d.arc((2,2,13,13),180,360,fill=METAL,width=3); d.rectangle((1,8,4,14),fill=METAL,outline=K); d.rectangle((11,8,14,14),fill=METAL,outline=K)
        if fi:
            d.ellipse((4,6,12,11),fill=(242,216,164),outline=K); d.rectangle((8,7,9,10),fill=(94,38,86)); d.point((8,7),fill=HI)
    else:
        raise ValueError('没有绘制函数：'+pid)
    return im


def install(ns,spec):
    out=[]
    for pid,(n,w,h,desc) in SPECS.items():
        out.append(spec(pid,n,w,h,desc))
        ns['draw_'+pid]=(lambda f,p=pid:draw(p,f))
    return out
