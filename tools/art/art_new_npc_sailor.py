"""npc_sailor：普通甲板水手（第 2 章包船船员、第 9 章渔夫共用）。

2026-10-11 重画：原来套用 art_later_people 的 'sailor' 样式 = 船长去掉胡子（同一顶金边白船长帽、同一身白制服），
和冒牌船长 fake_tennille 同站甲板时分不出谁是船长。现在单独画成普通水手：
  头   深蓝针织水手帽（圆顶 + 翻边罗纹，无帽檐、无金边），后脑露一点深棕发，下巴一层胡茬（不是船长那种大胡子），晒黑肤色；
  上身 蓝白横条纹短袖水手衫（袖口卷到上臂，前臂露肤色），圆领，棕色腰带；
  下身 卡其工装裤 + 高帮棕色工作靴。
人体骨架（头位、肩、胯、膝、步幅、摆臂、受击后仰、倒地姿势）逐项照抄 art_later_people.body / portrait 的关节公式，
帧尺寸不变（身体 36×44、倒地 56×22、头像 32×32）→ 图集 cell 56×60、pivot (28,44) 不变；动作和原来一样。
配色主值登记在 art_later_people.PEOPLE['npc_sailor']（衣 = 条纹底色、裤、发、身高），条纹 / 帽 / 靴等细节色在本文件。
"""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
from art_later_people import PEOPLE, K, WHITE, limb
from engine import sprite

CID = 'npc_sailor'
ACTIONS = {'idle': 2, 'walk': 4, 'talk': 2, 'hurt': 1, 'down': 1, 'portrait': 2}

ZH, _STYLE, SHIRT, PANTS, HAIR, H = PEOPLE[CID]
NAVY = (44, 68, 132)            # 条纹
SKIN = (204, 146, 102)          # 晒黑
SKIN_D = (150, 98, 72)          # 耳 / 阴影
STUBBLE = (168, 122, 94)        # 胡茬（比肤色略暗略灰，远浅于船长胡子）
CAP = (34, 48, 84)              # 针织帽
CAP_HI = (64, 86, 132)
CAP_RIB = (22, 30, 56)
BELT = (92, 60, 36)
BOOT = (80, 54, 36)


def _dark(c, k=.72):
    return tuple(int(v * k) for v in c[:3])


def _striped(im, poly, stripe, horizontal=True, base=SHIRT, shade_from=None):
    """多边形内填蓝白条纹（stripe(坐标) 为真 = 蓝条），shade_from 之后的列压暗做体积，最后补描边。"""
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    px, mp = im.load(), m.load()
    for yy in range(im.size[1]):
        for xx in range(im.size[0]):
            if mp[xx, yy]:
                c = NAVY if stripe(yy if horizontal else xx) else base
                if shade_from is not None and xx >= shade_from:
                    c = _dark(c, .78)
                px[xx, yy] = c + (255,)
    ImageDraw.Draw(im).polygon(poly, outline=K)


def head(mouth=False, scared=False):
    """24×24 头：脸型 / 眼 / 嘴 / 耳的像素和其他后续人物同一套，帽子和胡茬是水手自己的。"""
    im = Image.new('RGBA', (24, 24))
    d = ImageDraw.Draw(im)
    d.ellipse((6, 5, 18, 18), fill=SKIN, outline=K)
    d.polygon([(16, 10), (21, 12), (18, 14), (17, 17), (10, 19), (7, 15)], fill=SKIN, outline=K)
    d.rectangle((7, 12, 9, 15), fill=SKIN_D)
    # 胡茬：下颌一层比肤色略暗的阴影，上沿隔点过渡（只落在肤色上）；船长是整块深棕大胡子
    px = im.load()
    for x in range(9, 19):
        for y in range(15, 20):
            if px[x, y][:3] == SKIN and (y >= 16 or x % 2 == 0):
                px[x, y] = STUBBLE + (255,)
    d.line((13, 10, 17, 10), fill=K)
    d.point((16, 11), fill=WHITE)
    d.line((14, 16, 18, 16), fill=K)
    if mouth:
        d.rectangle((14, 16, 18, 17), fill=(112, 40, 48))
        d.line((14, 16, 17, 16), fill=WHITE)
    if scared:
        d.rectangle((13, 10, 18, 12), fill=WHITE)
        d.point((17, 11), fill=K)
        d.rectangle((15, 15, 17, 18), fill=K)
    # 后脑露出的短发
    d.rectangle((5, 9, 7, 12), fill=HAIR)
    d.line((5, 9, 5, 12), fill=K)
    # 深蓝针织帽：圆顶 + 翻边罗纹，没有帽檐、没有金边（船长是平顶白帽 + 前伸帽檐 + 金帽徽）
    d.polygon([(5, 7), (5, 4), (8, 1), (12, 0), (16, 1), (19, 4), (19, 7)], fill=CAP, outline=K)
    d.line((8, 3, 11, 2), fill=CAP_HI)
    d.point((7, 4), fill=CAP_HI)
    d.rectangle((4, 6, 20, 9), fill=CAP_RIB, outline=K)
    for x in range(6, 20, 2):
        d.line((x, 7, x, 8), fill=CAP)
    return im


def _sleeve(d, x0, y0, color, flip=False):
    """卷到上臂的短袖：一小块条纹布，中间一道蓝条，下沿是描边（袖口）。"""
    if not flip:
        poly = [(x0 - 2, y0 - 3), (x0 + 2, y0 - 3), (x0 + 4, y0 + 2), (x0 - 1, y0 + 3)]
    else:
        poly = [(x0 - 2, y0 - 3), (x0 + 2, y0 - 3), (x0 + 2, y0 + 2), (x0 - 3, y0 + 2)]
    d.polygon(poly, fill=color, outline=K)
    nav = NAVY if color == SHIRT else _dark(NAVY)
    d.line((poly[0][0] + 1, y0, poly[1][0] + (2 if not flip else 0), y0), fill=nav)


def body(action='idle', fi=0):
    h = H
    w = 36
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    hx = w // 2
    head_y = 1
    hh = 21
    top = hh - 3
    hip = h - 14
    ground = h - 2
    bob = (fi % 2) if action in ('idle', 'walk', 'run', 'talk') else 0
    leaning = -3 if action == 'hurt' else 0
    x = hx + leaning

    if action == 'down':
        # 倒地：和其他后续人物同一个姿势（头朝左、腰膝重画），条纹随躯干转成竖条
        out = Image.new('RGBA', (h + 12, 22))
        q = ImageDraw.Draw(out)
        limb(q, [(23, 14), (35, 16), (h + 2, 18)], PANTS, 5)
        limb(q, [(26, 12), (38, 9), (h + 3, 15)], tuple(int(c * .7) for c in PANTS), 4)
        q.rectangle((h - 1, 12, h + 8, 19), fill=BOOT, outline=K)
        q.line((h + 2, 18, h + 7, 18), fill=K)
        _striped(out, [(12, 10), (28, 10), (32, 18), (12, 19)], lambda v: (v - 12) % 3 == 1, horizontal=False)
        q.line((27, 11, 30, 18), fill=BELT)
        limb(q, [(17, 12), (21, 18), (29, 17)], SKIN, 3)
        q.polygon([(15, 10), (19, 10), (21, 15), (16, 15)], fill=SHIRT, outline=K)
        q.line((17, 12, 19, 12), fill=NAVY)
        hd = head(scared=True).crop((0, 0, 24, 24)).transpose(Image.Transpose.ROTATE_90)
        out.alpha_composite(hd, (0, -2))
        return out

    stride = (-3, 0, 3, 0)[fi % 4] if action in ('walk', 'run') else 0
    near = (x + 3, hip, x + 3 + stride, ground - 1)
    far = (x - 4, hip, x - 4 - stride, ground - 2)
    limb(d, [(far[0], far[1]), (far[2], far[3])], tuple(int(c * .72) for c in PANTS), 4)
    limb(d, [(near[0], near[1]), (near[2], near[3])], PANTS, 4)
    for i, (xx, yy) in enumerate(((far[2], far[3]), (near[2], near[3]))):
        # 高帮工作靴：比皮鞋高两行，近腿亮、远腿暗
        d.rectangle((xx - 2, yy - 2, xx + 4, yy + 1), fill=_dark(BOOT, .8) if i == 0 else BOOT, outline=K)
    # 躯干：蓝白横条纹（条纹按胯固定，呼吸起伏只动领口那一行），右侧压暗
    poly = [(x - 6, top + bob), (x + 6, top + bob), (x + 7, hip), (x - 7, hip)]
    _striped(im, poly, lambda v: (hip - v) % 3 == 0 and v < hip, shade_from=x + 5)
    d.polygon([(x - 2, top + bob), (x + 3, top + bob), (x + 1, top + bob + 2)], fill=SKIN)   # 圆领露脖子
    d.line((x - 6, hip - 1, x + 6, hip - 1), fill=BELT)
    d.point((x + 2, hip - 1), fill=(196, 170, 96))                                          # 皮带扣

    ay = top + 4 + bob
    arm_end = hip - 1
    if action in ('hurt', 'shock'):
        limb(d, [(x + 6, ay), (x + 10, ay + 4), (x + 7, top - 1)], SKIN, 3)
    else:
        swing = -stride // 2
        limb(d, [(x + 6, ay), (x + 8, ay + 5), (x + 7 + swing, arm_end)], SKIN, 4)
        d.rectangle((x + 6 + swing, arm_end - 1, x + 8 + swing, arm_end + 1), fill=SKIN, outline=K)
    _sleeve(d, x + 6, ay, SHIRT)
    limb(d, [(x - 6, ay), (x - 8, ay + 6), (x - 8 + stride // 2, arm_end)], _dark(SKIN, .82), 3)
    _sleeve(d, x - 7, ay, _dark(SHIRT), flip=True)
    hd = head(mouth=action == 'talk', scared=action in ('hurt', 'shock'))
    im.alpha_composite(hd, (x - hd.width // 2, head_y + bob))
    return im


def portrait(fi=0, expression='portrait'):
    out = Image.new('RGBA', (32, 32))
    d = ImageDraw.Draw(out)
    _striped(out, [(1, 31), (6, 23), (14, 21), (24, 23), (30, 31)], lambda v: v % 3 == 0)
    d.polygon([(12, 21), (19, 21), (16, 25)], fill=SKIN, outline=K)
    d.line((13, 21, 18, 21), fill=SKIN)
    hd = head(mouth=bool(fi), scared=expression in ('portrait_scared', 'portrait_reveal'))
    out.alpha_composite(hd.resize((30, 30), Image.Resampling.NEAREST), (1, -1))
    return out


def register():
    """和 art_later_people.register 同样的名字 / 锚点 / 帧率 / 说明，只是帧换成本文件画的。"""
    names = []
    for action, n in ACTIONS.items():
        if action.startswith('portrait'):
            frames = [portrait(i, action) for i in range(n)]
        else:
            frames = [body(action, i) for i in range(n)]
        name = CID + '.' + action
        sprite.define(name, frames, anchor='mm' if action.startswith('portrait') else 'mb',
                      fps=6 if action in ('walk', 'run') else 3, desc=ZH + '：' + action)
        names.append(name)
    return names


NEW = register()
ONESHOT = {'hurt', 'down', 'slash', 'attack', 'grab', 'reveal', 'punch', 'shock', 'beg', 'hide', 'angry'}
STATIC_STATES = {'true_form'}
CHAR_INFO = {CID: dict(zh=ZH, en=CID, cat='人物', typ='人物')}
