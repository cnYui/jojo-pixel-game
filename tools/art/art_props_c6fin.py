"""第6章到终章的新道具（2026-10-19，素材总表 §二）。

画法：先用整数像素铺色块（亮面 / 本色 / 暗面三阶 + 局部高光），最后 `_outline` 给整个剪影描一圈原工程的墨线色；
“长在世界里”的道具按设计尺寸画（约是最终大小的 1.6 倍），构建时跟人物一起按 0.625 缩（build_assets._shrink_ok）；
小游戏 / 插画里用的（筹码、记招图标、漫画格、电视框、赛车、棒球小人）按最终尺寸画、登记在 SHRINK_PROP_KEEP 里不缩。
"""
import sys
sys.dont_write_bytecode = True

import math

import numpy as np
from PIL import Image, ImageDraw

K = (26, 16, 32)            # 原工程描边色
HI = (255, 255, 255)

# 名字：(帧数, 宽, 高, 说明)
SPECS = {
    'spw_jeep': (2, 60, 30, 'SPW 财团的白色吉普（朝右）：帧 0 / 1 轮毂转半格（开动时交替）。第5、8、11章、终章'),
    'mirror_dome': (5, 42, 28, '阿拉伯·法兹的镜子穹顶：0 平时（映着沙色，几乎看不见）/ 1 反光一闪 / 2 裂了一道缝 / 3、4 裂开后长出两条小腿跑（交替）。第6章'),
    'carousel_horse': (3, 50, 42, '旋转木马的木马（朝右，金杆穿过马背）：3 帧奔跑。第6章梦二'),
    'horse': (4, 52, 40, '拉马车的马（朝右）：0、1 原地刨蹄 / 2、3 奔跑。第8章阿斯旺预言 2'),
    'carriage': (2, 64, 44, '两轮马车（朝右，车辕伸向右边接马）：0 正常 / 1 缰绳割断、车辕垂地。第8章阿斯旺'),
    'motorbike': (2, 56, 32, '承太郎骑的摩托（朝右）：0 停着 / 1 发动（车身抬 1 px + 排气）。终章'),
    'soul_chip': (2, 9, 9, '灵魂筹码：金色筹码上一张小脸（0 波鲁纳雷夫 / 1 乔瑟夫）。第10章赌局'),
    'anubis_icons': (6, 9, 9, '阿努比斯记招的小图标：0 J1 / 1 J2 / 2 J3 / 3 连打 / 4 U / 5 精准格挡后的反击。第9章 HUD'),
    'comic_panel': (13, 68, 56, '托特神漫画格（黑白网点）：0–5 第8章预言 1a 1b 2a 2b 3a 3b，6–11 第10章 4a 4b 5a 5b 6a 6b，12 大问号'),
    'crt_bezel': (1, 320, 180, '老电视机外框（屏幕区 [40,18]–[252,162] 透明，四角弧边 + 一层扫描线）：第11章赛车 / 棒球画面盖在上面'),
    'race_car': (4, 26, 16, 'F-MEGA 赛车（从后面看）：0、1 花京院的绿车（排气闪）/ 2、3 泰伦斯的灰车。第11章'),
    'race_sign': (2, 16, 22, 'F-MEGA 赛道路边的标牌：0 黄黑箭头 / 1 彩色广告牌。剧情按透视缩放。第11章'),
    'bb_sprites': (5, 16, 22, 'CRT 棒球的 8 位小人：0 投手（承太郎）站 / 1 投出 / 2 打者（泰伦斯）站 / 3 挥棒 / 4 球。第11章'),
}

# 不缩的（最终尺寸画）：build_assets.SHRINK_PROP_KEEP 里要登记这些名字
NO_SHRINK = ('soul_chip', 'anubis_icons', 'comic_panel', 'crt_bezel', 'race_car', 'race_sign', 'bb_sprites')


# =================================================================== 小工具
def _canvas(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def _outline(im, col=K):
    """不透明区域外面一圈描边（4 邻接），画在透明格上：剪影的墨线统一在最后加，色块之间不用逐条描。"""
    a = np.array(im)
    op = a[..., 3] > 0
    ring = np.zeros_like(op)
    ring[1:, :] |= op[:-1, :]
    ring[:-1, :] |= op[1:, :]
    ring[:, 1:] |= op[:, :-1]
    ring[:, :-1] |= op[:, 1:]
    ring &= ~op
    a[ring] = list(col) + [255]
    return Image.fromarray(a, 'RGBA')


def _wheel(d, cx, cy, r, fi, tire=(58, 56, 72), rim=(214, 222, 234), hub=(124, 124, 144), spokes=4):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tire)
    rr = max(1, r - 2)
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=rim)
    for i in range(spokes):
        a = math.pi * i / spokes + (math.pi / (2 * spokes) if fi % 2 else 0)
        dx, dy = math.cos(a) * (rr - 0.5), math.sin(a) * (rr - 0.5)
        d.line((round(cx - dx), round(cy - dy), round(cx + dx), round(cy + dy)), fill=hub)
    d.point((cx, cy), fill=(74, 74, 92))


def _star(d, x, y, r, col=HI):
    d.line((x - r, y, x + r, y), fill=col)
    d.line((x, y - r, x, y + r), fill=col)
    if r >= 3:
        d.point((x - 1, y - 1), fill=col); d.point((x + 1, y + 1), fill=col)
        d.point((x - 1, y + 1), fill=col); d.point((x + 1, y - 1), fill=col)


# =================================================================== 世界道具（按设计尺寸画，构建时缩 0.625）
def draw_spw_jeep(fi):
    w, h = 60, 30
    im, d = _canvas(w, h)
    W1, W2, W3 = (240, 242, 246), (206, 212, 224), (160, 168, 186)
    GL, GLH = (111, 176, 255), (232, 244, 255)
    BLUE = (46, 92, 196)
    # 车顶行李架 + 一个帆布包（SPW 的人常年跑野外）
    d.rectangle((15, 3, 44, 4), fill=(74, 74, 92))
    for x in (16, 24, 32, 40):
        d.line((x, 4, x, 6), fill=(74, 74, 92))
    d.rectangle((25, 0, 36, 2), fill=(150, 132, 92)); d.line((25, 0, 36, 0), fill=(190, 172, 124))
    # 车厢（方头四驱）：顶 y6、前窗斜一点
    d.polygon([(10, 7), (44, 7), (49, 13), (10, 13)], fill=W1)
    d.line((10, 7, 44, 7), fill=HI)
    # 车窗
    d.rectangle((12, 9, 22, 13), fill=GL)
    d.rectangle((25, 9, 35, 13), fill=GL)
    d.polygon([(38, 9), (43, 9), (47, 13), (38, 13)], fill=GL)
    for x0 in (14, 27, 40):
        d.line((x0, 12, x0 + 3, 9), fill=GLH)
    d.line((23, 8, 23, 13), fill=W3); d.line((36, 8, 36, 13), fill=W3)
    # 车身：前面（右）是发动机盖
    d.polygon([(4, 13), (49, 13), (57, 15), (58, 22), (3, 22)], fill=W1)
    d.line((5, 14, 56, 14), fill=HI)
    d.rectangle((3, 20, 58, 22), fill=W2)
    # 蓝色腰线 + 车门上的 SPW 圆标
    d.rectangle((4, 17, 57, 17), fill=BLUE)
    d.ellipse((27, 15, 32, 20), fill=BLUE); d.point((29, 17), fill=HI); d.point((30, 17), fill=HI)
    d.line((24, 14, 24, 21), fill=W3); d.line((37, 14, 37, 21), fill=W3)
    # 车灯、保险杠、门把手
    d.rectangle((56, 15, 58, 16), fill=(255, 216, 60)); d.point((58, 15), fill=(255, 243, 160))
    d.rectangle((3, 15, 4, 16), fill=(224, 48, 60))
    d.rectangle((1, 22, 7, 23), fill=(124, 124, 144)); d.rectangle((52, 22, 59, 23), fill=(124, 124, 144))
    for x in (20, 33):
        d.line((x, 16, x + 1, 16), fill=W3)
    # 车尾的备胎
    d.ellipse((0, 11, 7, 19), fill=(58, 56, 72)); d.ellipse((2, 13, 5, 17), fill=(124, 124, 144))
    # 车身下沿一层沙尘
    for x in range(6, 56, 3):
        d.point((x, 21 + (x // 3) % 2), fill=(186, 160, 120))
    # 轮子
    _wheel(d, 16, 23, 5, fi)
    _wheel(d, 46, 23, 5, fi)
    return _outline(im)


def draw_mirror_dome(fi):
    w, h = 42, 28
    im, d = _canvas(w, h)
    lift = 4 if fi >= 3 else 0
    base = h - 2 - lift
    if fi <= 1:
        # 平时：镜面映着四周的沙地和天——上浅（天）、中（远沙丘）、下（近处的沙），边缘只有一圈很淡的亮边，几乎看不出来
        for y in range(base - 22, base + 1):
            k = (y - (base - 22)) / 22
            half = math.sqrt(max(0.0, 1 - (1 - k) ** 2)) * 20
            col = (240, 238, 228) if k < .35 else (232, 216, 180) if k < .7 else (224, 204, 162)
            d.line((round(21 - half), y, round(20 + half), y), fill=col + (255,))
        d.arc((1, base - 22, 40, base + 22), 180, 360, fill=(250, 246, 234))
        d.line((6, base - 9, 35, base - 9), fill=(222, 206, 170))          # 映出来的“地平线”：直得过分
        d.line((2, base, 39, base), fill=(200, 178, 140, 160))              # 底边一丝影子
        if fi == 1:
            _star(d, 12, base - 15, 4)
            _star(d, 18, base - 18, 1, (255, 248, 200))
        return im
    # 2 以后：镜子裂了、露出银色的本体，描墨线
    for y in range(base - 22, base + 1):
        k = (y - (base - 22)) / 22
        half = math.sqrt(max(0.0, 1 - (1 - k) ** 2)) * 20
        col = (226, 234, 244) if k < .25 else (201, 214, 230) if k < .6 else (156, 168, 186)
        d.line((round(21 - half), y, round(20 + half), y), fill=col + (255,))
    d.line((8, base - 13, 14, base - 18), fill=HI); d.line((10, base - 10, 15, base - 14), fill=HI)
    # 裂缝：从顶上往右下的折线，两侧一点亮边
    crack = [(19, base - 21), (22, base - 15), (20, base - 11), (25, base - 6), (23, base - 1)]
    d.line(crack, fill=(40, 34, 54), width=1)
    d.line([(x + 1, y) for x, y in crack], fill=(240, 246, 255))
    d.line((22, base - 15, 28, base - 13), fill=(40, 34, 54))
    if fi >= 3:
        # 两条小腿（阿拉伯·法兹在里面扛着跑）：深褐裤腿 + 黑鞋，两帧交替迈步
        lx, rx = (12, 27) if fi == 3 else (15, 24)
        for x, fwd in ((lx, -2), (rx, 2)):
            d.line((x, base + 1, x + fwd, h - 2), fill=(76, 54, 44), width=2)
            d.rectangle((x + fwd - 1, h - 2, x + fwd + 2, h - 1), fill=(30, 26, 34))
    return _outline(im)


def _horse_body(d, ox, oy, pal, gait, mane_col, white=False):
    """侧面的马（朝右）：躯干椭圆 + 颈 + 头 + 四条腿；gait 给每条腿的 (前后摆 dx, 抬起 dy)。"""
    B1, B2, B3 = pal
    # 躯干
    d.ellipse((ox + 8, oy + 12, ox + 36, oy + 26), fill=B2)
    d.ellipse((ox + 9, oy + 12, ox + 35, oy + 21), fill=B1)
    # 颈往前斜（不是竖着长：竖着会看成骆驼 / 羊驼），头朝右下、口鼻宽一点
    d.polygon([(ox + 29, oy + 17), (ox + 33, oy + 8), (ox + 39, oy + 3), (ox + 42, oy + 8), (ox + 37, oy + 19)], fill=B2)
    d.polygon([(ox + 38, oy + 2), (ox + 43, oy + 1), (ox + 49, oy + 7), (ox + 49, oy + 11), (ox + 45, oy + 12),
               (ox + 41, oy + 8)], fill=B1)
    d.line((ox + 44, oy + 11, ox + 48, oy + 11), fill=B3)                      # 下颌线
    d.point((ox + 43, oy + 4), fill=K)                                         # 眼睛
    d.point((ox + 48, oy + 9), fill=B3)                                        # 鼻孔
    d.polygon([(ox + 39, oy + 1), (ox + 40, oy - 2), (ox + 42, oy + 1)], fill=B2)  # 耳朵
    # 鬃毛（沿着颈的后沿）+ 尾巴
    d.line((ox + 38, oy + 1, ox + 30, oy + 15), fill=mane_col, width=2)
    d.line((ox + 9, oy + 15, ox + 3, oy + 22), fill=mane_col, width=2)
    d.line((ox + 4, oy + 21, ox + 2, oy + 27), fill=mane_col, width=1)
    # 四条腿：后腿两条在 x 12 / 16，前腿两条在 x 28 / 32
    for (x, (dx, dy)), shade in zip(((12, gait[0]), (16, gait[1]), (28, gait[2]), (32, gait[3])), (B3, B2, B3, B2)):
        top = oy + 22
        foot = oy + 37 - dy
        d.line((ox + x, top, ox + x + dx, foot), fill=shade, width=3)
        d.rectangle((ox + x + dx - 1, foot, ox + x + dx + 1, foot + 1), fill=(60, 48, 46) if not white else (236, 194, 76))
    # 肚子底下一道暗
    d.line((ox + 12, oy + 25, ox + 32, oy + 25), fill=B3)


def draw_carousel_horse(fi):
    w, h = 50, 42
    im, d = _canvas(w, h)
    GOLD, GOLD_D = (236, 194, 76), (178, 132, 48)
    gaits = (((-4, 0), (-2, 2), (5, 5), (3, 2)), ((0, 2), (2, 0), (1, 1), (-1, 3)), ((3, 3), (4, 1), (-3, 0), (-4, 4)))
    _horse_body(d, 1, 3, ((248, 246, 240), (226, 220, 214), (192, 184, 184)), gaits[fi % 3], (236, 128, 170), white=True)
    # 红鞍 + 金边、蓝色马具
    d.rectangle((17, 13, 27, 16), fill=(204, 48, 64)); d.line((17, 16, 27, 16), fill=GOLD)
    d.line((38, 8, 46, 9), fill=(70, 110, 200)); d.line((33, 15, 39, 9), fill=(70, 110, 200))
    # 穿过马背的金杆（上下都伸出画面边缘一点，表示连着转盘）
    d.rectangle((21, 0, 22, h - 1), fill=GOLD); d.line((21, 0, 21, h - 1), fill=(255, 236, 150))
    d.line((22, 0, 22, h - 1), fill=GOLD_D)
    return _outline(im)


def draw_horse(fi):
    w, h = 52, 40
    im, d = _canvas(w, h)
    pal = ((176, 124, 80), (142, 94, 58), (104, 68, 44))
    gaits = (
        ((0, 0), (0, 0), (0, 0), (2, 3)),            # 站着，右前蹄抬起刨地
        ((0, 0), (0, 0), (0, 0), (-1, 0)),
        ((-5, 1), (-3, 3), (6, 4), (4, 1)),          # 跑
        ((3, 2), (5, 0), (-3, 1), (-5, 3)),
    )
    _horse_body(d, 1, 2, pal, gaits[fi], (52, 36, 30))
    # 白鼻梁、马具（颈圈 + 往左的缰绳头）
    d.line((45, 4, 48, 8), fill=(240, 236, 226))
    d.line((33, 10, 37, 19), fill=(40, 32, 36), width=2)
    d.line((40, 6, 47, 8), fill=(40, 32, 36))
    if fi < 2:
        d.line((30, 16, 18, 15), fill=(40, 32, 36))          # 套在车辕上的皮带（跑掉时就没有了）
    return _outline(im)


def draw_carriage(fi):
    w, h = 64, 44
    im, d = _canvas(w, h)
    BODY, BODY_D, BODY_L = (44, 34, 46), (28, 22, 30), (86, 70, 90)
    ROOF, ROOF_D = (236, 226, 200), (190, 176, 144)
    GOLD, WOOD = (226, 184, 70), (120, 84, 52)
    # 车辕：正常时水平伸向右边（接马）；割断以后一头垂到地上
    if fi == 0:
        d.line((40, 29, 63, 27), fill=WOOD, width=2)
    else:
        d.line((40, 29, 61, 41), fill=WOOD, width=2)
    # 平顶车篷（hantour）：白顶 + 一排流苏，四根细柱撑着
    d.rectangle((4, 4, 38, 7), fill=ROOF); d.line((4, 4, 38, 4), fill=(250, 246, 232))
    for x in range(5, 38, 3):
        d.line((x, 8, x, 9), fill=(204, 60, 70) if (x // 3) % 2 else GOLD)
    for x in (6, 20, 36):
        d.line((x, 8, x, 20), fill=BODY_L)
    # 车厢：方座斗 + 金色描线 + 侧面一盏小灯
    d.rectangle((4, 20, 38, 30), fill=BODY)
    d.line((5, 21, 37, 21), fill=BODY_L); d.line((4, 30, 38, 30), fill=BODY_D)
    d.rectangle((7, 23, 35, 27), outline=GOLD)
    d.rectangle((38, 16, 40, 19), fill=GOLD); d.point((39, 17), fill=(255, 243, 160))
    # 车夫座（前面高一截）+ 踏板
    d.rectangle((38, 18, 48, 21), fill=BODY); d.line((38, 18, 48, 18), fill=BODY_L)
    d.line((46, 21, 46, 29), fill=BODY_D); d.rectangle((44, 29, 50, 30), fill=WOOD)
    # 大车轮（黄色辐条）
    cx, cy, r = 22, 33, 10
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(52, 36, 34))
    d.ellipse((cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), fill=(0, 0, 0, 0))
    for i in range(8):
        a = math.pi * i / 4
        d.line((cx, cy, round(cx + math.cos(a) * (r - 1)), round(cy + math.sin(a) * (r - 1))), fill=GOLD)
    d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(150, 112, 52))
    return _outline(im)


def draw_motorbike(fi):
    w, h = 56, 32
    im, d = _canvas(w, h)
    up = 1 if fi else 0
    CH, CH_D = (214, 222, 234), (124, 124, 144)
    TANK, TANK_L, RED = (40, 38, 54), (86, 84, 110), (204, 48, 60)
    # 轮子（辐条轮）
    for cx in (12, 44):
        d.ellipse((cx - 9, 13, cx + 9, 31), fill=(46, 44, 58))
        d.ellipse((cx - 6, 16, cx + 6, 28), fill=(0, 0, 0, 0))
        for i in range(6):
            a = math.pi * i / 3 + (0.3 if fi else 0)
            d.line((cx, 22, round(cx + math.cos(a) * 6), round(22 + math.sin(a) * 6)), fill=CH_D)
        d.ellipse((cx - 1, 21, cx + 1, 23), fill=CH)
    # 车架、发动机、排气管
    d.line((12, 22 - up, 26, 14 - up), fill=TANK, width=2)
    d.line((26, 14 - up, 44, 22 - up), fill=TANK, width=2)
    d.rectangle((22, 16 - up, 32, 22 - up), fill=CH_D); d.rectangle((23, 17 - up, 31, 18 - up), fill=CH)
    d.line((14, 26 - up, 30, 25 - up), fill=CH, width=2)
    # 油箱 + 红色条纹、座椅
    d.polygon([(24, 8 - up), (36, 8 - up), (38, 13 - up), (24, 13 - up)], fill=TANK)
    d.line((25, 9 - up, 35, 9 - up), fill=TANK_L); d.line((25, 11 - up, 37, 11 - up), fill=RED)
    d.rectangle((12, 10 - up, 24, 12 - up), fill=(30, 26, 34)); d.line((12, 10 - up, 24, 10 - up), fill=(74, 70, 90))
    # 前叉、车把、大灯
    d.line((44, 22 - up, 40, 6 - up), fill=CH, width=2)
    d.line((37, 4 - up, 43, 3 - up), fill=TANK, width=2)
    d.ellipse((43, 6 - up, 48, 11 - up), fill=(255, 216, 60)); d.point((45, 7 - up), fill=(255, 243, 160))
    # 后挡泥板
    d.arc((2, 12 - up, 22, 30 - up), 200, 300, fill=TANK, width=2)
    if fi:
        # 排气的一小团烟
        d.ellipse((2, 22, 7, 26), fill=(196, 196, 206)); d.ellipse((0, 19, 4, 23), fill=(220, 220, 228))
    return _outline(im)


# =================================================================== 小游戏 / 插画道具（最终尺寸画，不缩）
def draw_soul_chip(fi):
    im, d = _canvas(9, 9)
    d.ellipse((0, 0, 8, 8), fill=(214, 168, 64)); d.ellipse((1, 1, 7, 7), fill=(240, 204, 96))
    d.arc((0, 0, 8, 8), 200, 300, fill=(255, 238, 170))
    # 小脸：两只眼睛 + 嘴；0 号头上一撮竖起的白发（波鲁纳雷夫）、1 号一顶棕色帽子（乔瑟夫）
    d.point((3, 5), fill=K); d.point((5, 5), fill=K); d.line((3, 7, 5, 7), fill=(150, 90, 40))
    if fi == 0:
        d.line((4, 1, 4, 3), fill=(250, 250, 250)); d.point((3, 2), fill=(250, 250, 250)); d.point((5, 2), fill=(250, 250, 250))
    else:
        d.rectangle((2, 2, 6, 3), fill=(150, 98, 60)); d.line((1, 4, 7, 4), fill=(118, 74, 46))
    d.ellipse((0, 0, 8, 8), outline=(140, 98, 36))
    return im


def draw_anubis_icons(fi):
    im, d = _canvas(9, 9)
    PUR, PUR_L = (120, 64, 170), (200, 150, 255)
    d.rectangle((0, 0, 8, 8), fill=(30, 20, 44)); d.rectangle((0, 0, 8, 8), outline=PUR)
    W = (240, 236, 255)
    if fi in (0, 1):                     # 拳头（J2 两个）
        xs = (3,) if fi == 0 else (2, 5)
        for x in xs:
            d.rectangle((x - 1, 3, x + 1, 6), fill=W); d.point((x - 1, 3), fill=PUR_L)
    elif fi == 2:                        # J3：星形冲击
        d.line((4, 2, 4, 6), fill=W); d.line((2, 4, 6, 4), fill=W); d.point((3, 3), fill=W); d.point((5, 5), fill=W)
        d.point((5, 3), fill=PUR_L); d.point((3, 5), fill=PUR_L)
    elif fi == 3:                        # 连打：三道速度线 + 拳
        for y in (3, 5, 7):
            d.line((1, y - 1, 3, y - 1), fill=PUR_L)
        d.rectangle((5, 3, 7, 6), fill=W)
    elif fi == 4:                        # U：闪电
        d.line((5, 1, 3, 4), fill=(255, 224, 80)); d.line((3, 4, 6, 4), fill=(255, 224, 80)); d.line((6, 4, 3, 7), fill=(255, 224, 80))
    else:                                # 反击：盾 + 箭头
        d.polygon([(2, 2), (5, 2), (5, 5), (3, 7), (2, 5)], fill=W)
        d.line((5, 4, 7, 4), fill=(255, 224, 80)); d.point((6, 3), fill=(255, 224, 80)); d.point((6, 5), fill=(255, 224, 80))
    return im


# ------------------------------------------------------------------- 漫画格
def _tone(d, box, step=3, col=(150, 150, 150)):
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1, step):
        for x in range(x0 + (y // step) % 2 * (step // 2 + 1), x1 + 1, step):
            d.point((x, y), fill=col)


def _speed_lines(d, cx, cy, n=14, r0=10, r1=40, col=(40, 40, 40)):
    for i in range(n):
        a = _TAU_I * i / n
        d.line((round(cx + math.cos(a) * r0), round(cy + math.sin(a) * r0),
                round(cx + math.cos(a) * r1), round(cy + math.sin(a) * r1)), fill=col)


_TAU_I = 2 * math.pi
INK, PAPER, GREY = (20, 18, 26), (250, 248, 240), (170, 168, 176)


def _head(d, x, y, kind):
    """漫画里的人头（朝右，侧脸剪影 + 几笔特征）：cap 承太郎（假）/ hat 乔瑟夫 / pol 波鲁纳雷夫 / cowboy 荷尔·荷斯 / plain。"""
    d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=PAPER, outline=INK)
    d.point((x + 3, y - 1), fill=INK)
    d.line((x + 2, y + 3, x + 4, y + 3), fill=INK)
    if kind == 'cap':
        d.polygon([(x - 7, y - 3), (x - 6, y - 9), (x + 5, y - 9), (x + 9, y - 4)], fill=INK)
        d.line((x + 2, y - 4, x + 10, y - 2), fill=INK)
    elif kind == 'hat':
        d.rectangle((x - 5, y - 11, x + 5, y - 5), fill=INK); d.line((x - 9, y - 5, x + 9, y - 5), fill=INK)
    elif kind == 'pol':
        d.polygon([(x - 4, y - 5), (x - 2, y - 20), (x + 3, y - 20), (x + 4, y - 5)], fill=PAPER, outline=INK)
        for yy in range(y - 18, y - 6, 3):
            d.line((x - 2, yy, x + 2, yy), fill=GREY)
    elif kind == 'cowboy':
        d.polygon([(x - 10, y - 5), (x - 5, y - 6), (x - 4, y - 12), (x + 4, y - 12), (x + 5, y - 6), (x + 10, y - 5)], fill=INK)


def _body(d, x, y, h=14):
    d.polygon([(x - 6, y), (x + 6, y), (x + 8, y + h), (x - 8, y + h)], fill=PAPER, outline=INK)


def draw_comic_panel(fi):
    w, h = 68, 56
    im, d = _canvas(w, h)
    d.rectangle((0, 0, w - 1, h - 1), fill=PAPER)
    if fi == 0:      # 第8章 1a：假承太郎往茶杯里丢东西
        _tone(d, (1, 1, 66, 20))
        _head(d, 22, 22, 'cap'); _body(d, 22, 28, 26)
        d.line((28, 32, 40, 30), fill=INK, width=2)                       # 伸出去的手
        d.rectangle((44, 38, 54, 47), fill=PAPER, outline=INK); d.arc((52, 40, 58, 46), 270, 90, fill=INK)  # 茶杯
        d.ellipse((46, 28, 48, 30), fill=INK); d.line((47, 31, 47, 35), fill=GREY)                         # 掉下去的药丸
        d.ellipse((45, 37, 53, 40), fill=GREY)
    elif fi == 1:    # 1b：乔瑟夫端起茶喝
        _tone(d, (1, 30, 66, 54), 2)
        _head(d, 30, 20, 'hat'); _body(d, 30, 26, 26)
        d.rectangle((38, 16, 44, 22), fill=PAPER, outline=INK)
        for i in range(3):
            d.arc((46 + i * 4, 10, 52 + i * 4, 18), 300, 60, fill=INK)     # “咕嘟”的弧线
    elif fi == 2:    # 2a：马受惊抬起前腿（借道具马第 2 帧，转成漫画的黑白三阶、往后仰）
        _speed_lines(d, 34, 28, 18, 18, 44, GREY)
        hz = draw_horse(2).rotate(28, expand=True, resample=Image.NEAREST)
        a = np.array(hz)
        lum = a[..., :3].astype(int).mean(-1)
        op = a[..., 3] > 0
        out = np.zeros_like(a)
        out[op & (lum < 70)] = INK + (255,)
        out[op & (lum >= 70) & (lum < 130)] = GREY + (255,)
        out[op & (lum >= 130)] = PAPER + (255,)
        hz = Image.fromarray(out, 'RGBA')
        im.alpha_composite(hz, (34 - hz.width // 2, 54 - hz.height))
    elif fi == 3:    # 2b：马车撞上波鲁纳雷夫（星星）
        _tone(d, (1, 1, 66, 54), 4)
        _head(d, 44, 30, 'pol'); _body(d, 44, 36, 14)
        d.rectangle((6, 26, 30, 44), fill=PAPER, outline=INK); d.ellipse((10, 38, 22, 50), fill=PAPER, outline=INK)
        for sx, sy in ((52, 12), (60, 20), (40, 8)):
            _star(d, sx, sy, 3, INK)
        _speed_lines(d, 34, 34, 10, 4, 12, INK)
    elif fi == 4:    # 3a：一只手递来一颗橘子
        _tone(d, (1, 1, 66, 54), 3, (200, 198, 204))
        d.polygon([(4, 40), (30, 34), (34, 40), (8, 48)], fill=PAPER, outline=INK)
        d.ellipse((30, 22, 46, 38), fill=GREY, outline=INK); d.line((38, 22, 40, 18), fill=INK)
        d.arc((33, 25, 41, 33), 180, 270, fill=PAPER)
    elif fi == 5:    # 3b：“承太郎”的脸炸开
        _speed_lines(d, 34, 30, 20, 8, 40, INK)
        _head(d, 34, 32, 'cap')
        d.polygon([(20, 18), (28, 24), (30, 12), (36, 22), (44, 10), (42, 24), (54, 20), (44, 30)], fill=INK)
    elif fi == 6:    # 第10章 4a：镜子前，一颗子弹飞来
        d.rectangle((40, 10, 56, 40), fill=GREY, outline=INK); d.line((44, 14, 50, 22), fill=PAPER)
        d.line((48, 40, 44, 52), fill=INK); d.line((48, 40, 52, 52), fill=INK)
        d.line((4, 26, 38, 26), fill=INK); d.polygon([(30, 23), (38, 26), (30, 29)], fill=INK)
        for x in range(6, 28, 4):
            d.point((x, 24), fill=GREY)
    elif fi == 7:    # 4b：子弹擦过帽子
        _head(d, 34, 32, 'cowboy'); _body(d, 34, 38, 14)
        d.line((4, 20, 62, 20), fill=INK); _star(d, 34, 20, 4, INK)
    elif fi == 8:    # 5a：油桶旁边，有人滑倒
        d.rectangle((44, 26, 56, 44), fill=GREY, outline=INK); d.line((44, 32, 56, 32), fill=INK)
        d.ellipse((20, 44, 50, 50), fill=INK)
        _head(d, 22, 22, 'plain'); d.line((22, 28, 30, 40), fill=INK, width=2); d.line((30, 40, 40, 36), fill=INK, width=2)
        d.arc((8, 16, 36, 44), 200, 260, fill=GREY)
    elif fi == 9:    # 5b：倒下的人被子弹擦到
        _tone(d, (1, 40, 66, 54), 2)
        _head(d, 20, 38, 'plain'); d.line((26, 40, 50, 42), fill=INK, width=3)
        d.line((60, 10, 26, 32), fill=INK); _star(d, 26, 32, 3, INK)
    elif fi == 10:   # 6a：路口正中，画一个叉
        d.rectangle((0, 22, 67, 34), fill=GREY); d.rectangle((28, 0, 40, 55), fill=GREY)
        d.line((30, 24, 38, 32), fill=INK, width=2); d.line((38, 24, 30, 32), fill=INK, width=2)
    elif fi == 11:   # 6b：路口正中的人影中弹
        d.rectangle((0, 22, 67, 34), fill=GREY); d.rectangle((28, 0, 40, 55), fill=GREY)
        _head(d, 34, 16, 'cowboy'); _body(d, 34, 22, 16)
        _speed_lines(d, 34, 20, 12, 10, 18, INK)
    else:            # 12：大问号（命运拐弯：留给玩家）
        _tone(d, (1, 1, 66, 54), 3, (210, 208, 214))
        d.arc((22, 8, 46, 32), 180, 60, fill=INK, width=4)
        d.line((40, 28, 34, 34), fill=INK, width=4); d.line((34, 34, 34, 38), fill=INK, width=4)
        d.rectangle((32, 44, 36, 48), fill=INK)
    d.rectangle((0, 0, w - 1, h - 1), outline=INK)
    return im


def draw_crt_bezel(fi):
    w, h = 320, 180
    im, d = _canvas(w, h)
    sx0, sy0, sx1, sy1 = 40, 18, 252, 162
    CAB, CAB_L, CAB_D = (64, 52, 46), (98, 82, 70), (40, 32, 30)
    d.rounded_rectangle((20, 4, 300, 176), radius=10, fill=CAB)
    d.rounded_rectangle((22, 6, 298, 174), radius=9, outline=CAB_L)
    # 屏幕外圈的黑色塑料框
    d.rounded_rectangle((sx0 - 8, sy0 - 8, sx1 + 8, sy1 + 8), radius=12, fill=(22, 20, 26))
    # 挖出屏幕：圆角矩形透明
    hole = Image.new('L', (w, h), 0)
    ImageDraw.Draw(hole).rounded_rectangle((sx0, sy0, sx1, sy1), radius=14, fill=255)
    a = np.array(im)
    a[np.array(hole) > 0] = (0, 0, 0, 0)
    # 屏幕四角的暗角 + 扫描线（半透明，叠在游戏画面上）
    ys, xs = np.mgrid[0:h, 0:w]
    inside = np.array(hole) > 0
    cx, cy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
    r = np.sqrt(((xs - cx) / ((sx1 - sx0) / 2)) ** 2 + ((ys - cy) / ((sy1 - sy0) / 2)) ** 2)
    vig = np.clip((r - 0.8) / 0.6, 0, 1) * 150
    scan = ((ys % 2) == 1) * 36
    alpha = np.clip(vig + scan, 0, 200).astype(np.uint8)
    a[inside, 0:3] = (8, 10, 18)
    a[inside, 3] = alpha[inside]
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    # 右边的旋钮、喇叭网、电源灯
    for y in (40, 70):
        d.ellipse((268, y, 286, y + 18), fill=(30, 26, 26)); d.ellipse((271, y + 3, 283, y + 15), fill=(150, 140, 128))
        d.line((277, y + 4, 277, y + 9), fill=(40, 34, 30))
    for y in range(102, 150, 4):
        d.line((268, y, 288, y), fill=CAB_D)
    d.ellipse((274, 158, 279, 163), fill=(220, 60, 60))
    d.text((60, 166), 'SONIQ', fill=(170, 150, 120))
    return im


def draw_race_car(fi):
    im, d = _canvas(26, 16)
    green = fi < 2
    B1, B2 = ((70, 200, 110), (36, 130, 70)) if green else ((172, 176, 186), (106, 110, 124))
    d.rectangle((2, 4, 23, 7), fill=B2); d.rectangle((1, 3, 24, 4), fill=B1)          # 尾翼
    d.polygon([(5, 6), (20, 6), (23, 11), (2, 11)], fill=B1)
    d.rectangle((9, 5, 16, 8), fill=(40, 40, 54))                                       # 驾驶座
    d.ellipse((10, 4, 15, 8), fill=(250, 220, 90) if green else (230, 230, 230))        # 头盔
    d.rectangle((0, 9, 5, 15), fill=(30, 28, 36)); d.rectangle((20, 9, 25, 15), fill=(30, 28, 36))  # 后轮
    d.rectangle((6, 11, 8, 12), fill=(255, 70, 70)); d.rectangle((17, 11, 19, 12), fill=(255, 70, 70))
    if fi % 2:
        d.rectangle((11, 13, 14, 15), fill=(255, 200, 80))                              # 排气火
    return _outline(im)


def draw_race_sign(fi):
    im, d = _canvas(16, 22)
    d.rectangle((7, 12, 8, 21), fill=(120, 120, 136))
    if fi == 0:
        d.rectangle((0, 0, 15, 11), fill=(250, 210, 40))
        for x in (2, 7, 12):
            d.polygon([(x - 1, 2), (x + 2, 5), (x - 1, 9), (x - 3, 9), (x, 5), (x - 3, 2)], fill=(20, 18, 26))
    else:
        for i, c in enumerate(((230, 70, 90), (250, 210, 40), (80, 170, 240))):
            d.rectangle((0, i * 4, 15, i * 4 + 3), fill=c)
    return _outline(im)


def draw_bb_sprites(fi):
    im, d = _canvas(16, 22)
    if fi in (0, 1):     # 投手：承太郎（黑帽黑衣），1 = 手臂甩下来
        d.rectangle((5, 2, 10, 4), fill=(30, 30, 50)); d.line((4, 4, 12, 4), fill=(30, 30, 50))
        d.rectangle((6, 5, 9, 8), fill=(240, 200, 160))
        d.rectangle((5, 9, 10, 15), fill=(40, 40, 70))
        d.line((6, 16, 5, 21), fill=(40, 40, 70), width=2); d.line((9, 16, 10, 21), fill=(40, 40, 70), width=2)
        if fi == 0:
            d.line((10, 10, 13, 7), fill=(240, 200, 160)); d.point((13, 6), fill=HI)
        else:
            d.line((10, 10, 14, 13), fill=(240, 200, 160))
    elif fi in (2, 3):   # 打者：泰伦斯（马甲），3 = 挥棒
        d.rectangle((6, 1, 9, 4), fill=(70, 50, 40)); d.rectangle((6, 5, 9, 8), fill=(240, 200, 160))
        d.rectangle((5, 9, 10, 15), fill=(120, 30, 40))
        d.line((6, 16, 5, 21), fill=(30, 30, 40), width=2); d.line((9, 16, 10, 21), fill=(30, 30, 40), width=2)
        if fi == 2:
            d.line((10, 10, 14, 2), fill=(200, 160, 100), width=2)
        else:
            d.line((10, 11, 15, 12), fill=(200, 160, 100), width=2)
    else:                # 球
        d.ellipse((6, 9, 10, 13), fill=HI); d.point((7, 10), fill=(220, 60, 60)); d.point((9, 12), fill=(220, 60, 60))
    return _outline(im) if fi < 4 else _outline(im, (60, 60, 70))


# =================================================================== 重画的旧道具（10-18 版是平涂色块，和原工程的 car / heli 不在一个精度上）
#  尺寸照 art_props_later.SPECS（剧情已经按这个大小摆位），art_props.py 安装完 later 以后用这里的 draw_* 覆盖。
def draw_truck_v2(fi):
    w, h = 64, 36
    im, d = _canvas(w, h)
    B1, B2, B3 = (204, 112, 76), (166, 84, 60), (120, 58, 44)
    GL, GLH = (111, 176, 255), (232, 244, 255)
    # 货斗（左）：栏板 + 里面一块帆布、一只油桶
    d.rectangle((3, 15, 31, 25), fill=B2); d.line((3, 15, 31, 15), fill=B1)
    d.rectangle((4, 11, 30, 14), fill=(176, 150, 104)); d.line((5, 11, 29, 11), fill=(206, 182, 132))
    d.rectangle((20, 8, 26, 14), fill=(74, 102, 140)); d.line((20, 10, 26, 10), fill=(110, 140, 176))
    d.rectangle((2, 14, 3, 25), fill=B3)
    # 驾驶室 + 车窗
    d.polygon([(31, 7), (44, 7), (49, 15), (31, 15)], fill=B1)
    d.line((31, 7, 44, 7), fill=(236, 150, 110))
    d.polygon([(34, 9), (43, 9), (47, 15), (34, 15)], fill=GL); d.line((37, 14, 40, 9), fill=GLH)
    # 发动机盖（右）+ 车身
    d.polygon([(31, 15), (49, 15), (61, 17), (62, 25), (31, 25)], fill=B2)
    d.line((32, 16, 60, 17), fill=B1)
    d.rectangle((3, 23, 62, 25), fill=B3)
    d.line((31, 15, 31, 25), fill=B3); d.line((44, 16, 44, 24), fill=B3)
    d.rectangle((59, 17, 62, 19), fill=(255, 216, 60)); d.point((62, 17), fill=(255, 243, 160))
    d.rectangle((1, 18, 2, 20), fill=(224, 48, 60))
    d.rectangle((0, 25, 6, 26), fill=(150, 150, 166)); d.rectangle((56, 25, 63, 26), fill=(150, 150, 166))
    # 锈斑
    for x, y in ((8, 20), (12, 22), (52, 22), (28, 19)):
        d.point((x, y), fill=B3); d.point((x + 1, y), fill=(140, 84, 52))
    _wheel(d, 15, 27, 6, fi)
    _wheel(d, 50, 27, 6, fi)
    return _outline(im)


def draw_senator_car_v2(fi):
    w, h = 72, 28
    im, d = _canvas(w, h)
    B1, B2, B3 = (64, 70, 90), (38, 42, 58), (24, 26, 38)
    CH, CH_D = (214, 222, 234), (140, 146, 162)
    GL = (54, 70, 96)
    # 长车身（三厢）：车顶低、车尾长
    d.polygon([(22, 6), (46, 6), (53, 12), (22, 12), (16, 12)], fill=B1)
    d.line((23, 6, 45, 6), fill=(110, 118, 140))
    d.polygon([(24, 8), (33, 8), (33, 12), (20, 12)], fill=GL); d.polygon([(35, 8), (45, 8), (50, 12), (35, 12)], fill=GL)
    d.line((26, 11, 28, 9), fill=(120, 140, 170)); d.line((38, 11, 40, 9), fill=(120, 140, 170))
    d.polygon([(2, 12), (66, 12), (70, 15), (70, 21), (2, 21)], fill=B2)
    d.line((3, 13, 68, 13), fill=B1)
    d.line((3, 16, 69, 16), fill=CH)                                # 镀铬腰线
    d.rectangle((2, 19, 70, 21), fill=B3)
    d.line((34, 13, 34, 20), fill=B3); d.line((48, 13, 48, 20), fill=B3)
    d.rectangle((67, 14, 70, 15), fill=(255, 230, 140)); d.rectangle((68, 17, 70, 19), fill=CH_D)   # 大灯 + 格栅
    d.rectangle((2, 14, 3, 15), fill=(200, 40, 50))
    d.rectangle((0, 21, 8, 22), fill=CH); d.rectangle((62, 21, 71, 22), fill=CH)
    # 前翼子板上一面小三角旗
    d.line((60, 8, 60, 12), fill=CH_D); d.polygon([(61, 8), (65, 9), (61, 10)], fill=(220, 60, 70))
    # 白边轮胎
    for cx in (16, 56):
        d.ellipse((cx - 5, 18, cx + 5, 27), fill=(30, 30, 40))
        d.ellipse((cx - 3, 20, cx + 3, 25), fill=(236, 236, 236)); d.ellipse((cx - 1, 21, cx + 1, 24), fill=CH_D)
    return _outline(im)


def draw_cessna_v2(fi):
    w, h = 64, 24
    im, d = _canvas(w, h)
    W1, W2, W3 = (246, 246, 242), (214, 216, 220), (170, 174, 184)
    RED = (210, 56, 60)
    GL = (111, 176, 255)
    # 机身（朝右，机头在右）+ 尾翼
    d.polygon([(3, 9), (14, 11), (50, 10), (57, 12), (58, 16), (52, 18), (14, 16), (4, 14)], fill=W1)
    d.line((14, 11, 50, 10), fill=HI)
    d.line((8, 14, 56, 16), fill=W2)
    d.polygon([(2, 3), (7, 3), (12, 11), (4, 11)], fill=W1); d.line((3, 4, 10, 10), fill=RED)    # 垂直尾翼
    d.rectangle((2, 11, 12, 12), fill=W2)                                                        # 水平尾翼
    d.line((12, 14, 52, 15), fill=RED)                                                           # 红腰线
    # 上单翼（从机身顶上伸出，前视角压成一条）+ 撑杆
    d.rectangle((22, 6, 46, 8), fill=W1); d.line((22, 6, 46, 6), fill=HI); d.line((24, 8, 44, 8), fill=W3)
    d.line((30, 9, 33, 14), fill=W3)
    # 驾驶舱窗
    d.polygon([(38, 9), (46, 9), (50, 11), (38, 12)], fill=GL); d.line((41, 11, 43, 9), fill=(232, 244, 255))
    # 机头整流罩 + 螺旋桨
    d.ellipse((55, 11, 60, 17), fill=W3)
    if fi == 0:
        d.line((61, 4, 61, 22), fill=(74, 74, 92), width=2); d.point((61, 13), fill=RED)
    else:
        # 坠毁后：螺旋桨弯了、机身一片焦黑
        d.line((61, 9, 61, 15), fill=(74, 74, 92), width=2); d.line((61, 15, 58, 21), fill=(74, 74, 92), width=2)
        d.line((61, 9, 63, 5), fill=(74, 74, 92), width=2)
        for x, y in ((30, 13), (34, 12), (44, 15), (48, 14)):
            d.ellipse((x - 2, y - 1, x + 2, y + 1), fill=(74, 70, 72))
    # 起落架
    d.line((44, 17, 46, 21), fill=(74, 74, 92)); d.line((20, 16, 20, 21), fill=(74, 74, 92))
    for cx in (46, 20):
        d.ellipse((cx - 2, 20, cx + 2, 23), fill=(40, 40, 52))
    return _outline(im)


def draw_mirror_stand_v2(fi):
    w, h = 18, 32
    im, d = _canvas(w, h)
    WOOD, WOOD_D, WOOD_L = (142, 96, 58), (96, 62, 40), (186, 132, 82)
    # 立镜（落地穿衣镜）：两根木架 + 中间能转的椭圆镜面
    d.line((2, 6, 2, 31), fill=WOOD, width=2); d.line((15, 6, 15, 31), fill=WOOD, width=2)
    d.line((1, 31, 5, 31), fill=WOOD_D); d.line((13, 31, 17, 31), fill=WOOD_D)
    d.ellipse((4, 1, 13, 24), fill=WOOD_L); d.ellipse((5, 2, 12, 23), fill=(150, 196, 214))
    d.line((7, 18, 10, 6), fill=(236, 248, 255)); d.line((6, 15, 8, 9), fill=(200, 230, 240))
    d.rectangle((2, 12, 4, 13), fill=WOOD_D); d.rectangle((13, 12, 15, 13), fill=WOOD_D)   # 转轴
    return _outline(im)


REDRAW = {'truck': draw_truck_v2, 'senator_car': draw_senator_car_v2, 'cessna': draw_cessna_v2,
          'mirror_stand': draw_mirror_stand_v2}


# =================================================================== 登记
def draw(pid, fi):
    return globals()['draw_' + pid](fi)


def install(ns, spec):
    # 重画的旧道具：覆盖 art_props_later 装进来的同名 draw_*（尺寸不变，剧情摆位不受影响）
    for pid, fn in REDRAW.items():
        ns['draw_' + pid] = fn
    out = []
    for pid, (n, w, h, desc) in SPECS.items():
        e = spec(pid, n, w, h, desc)
        if pid == 'crt_bezel':
            e['pivot'] = [0, 0]
        out.append(e)
        ns['draw_' + pid] = (lambda f, p=pid: draw(p, f))
    return out
