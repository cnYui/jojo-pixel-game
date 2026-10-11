"""npc_bellhop：新加坡酒店门童（第3章，2026-10-11 新画）。

照 art_new_npc_sailor.py 的写法：人体骨架（头位、肩、胯、膝、步幅、摆臂、受击后仰、倒地姿势）逐项照抄
art_later_people.body / portrait 的关节公式，帧尺寸和其他后续 NPC 一样（身体 36×44、倒地 56×22、头像 32×32）
→ 图集 cell 56×60、pivot (28,44)，和 npc_sailor 等身高一致。
  头   东南亚面孔：小麦肤色、黑发梳得服帖（后脑 + 鬓角露一点），眼睛一条线 + 高光（同其他后续人物），
       头顶戴一顶红色圆筒小帽（金色帽箍 + 顶上金边 + 一颗金扣；帽带在 44 px 身高里只会糊成脸上一道黑线，不画）；
  上身 红色短款门童制服外套（到腰）：金色立领、胸前两排金扣、金色袖口，左上亮右边暗；
  手   白手套；
  下身 黑裤 + 裤缝一道红线，黑皮鞋。
动作：idle 2、walk 4、talk 2、hurt 1、down 1、portrait 2（和其他后续 NPC 同一套）。
"""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
from art_later_people import K, WHITE, limb
from engine import sprite

CID = 'npc_bellhop'
ZH = '酒店门童'
ACTIONS = {'idle': 2, 'walk': 4, 'talk': 2, 'hurt': 1, 'down': 1, 'portrait': 2}
H = 44

SKIN = (198, 142, 98)           # 东南亚小麦肤色
SKIN_D = (146, 96, 68)
HAIR = (30, 26, 34)
HAIR_H = (70, 66, 84)
RED = (192, 38, 46)             # 门童制服红
RED_D = (128, 22, 34)
RED_H = (232, 84, 78)
GOLD = (244, 200, 82)
GOLD_D = (176, 128, 44)
PANTS = (36, 34, 48)
STRIPE = (150, 30, 40)
GLOVE = (244, 242, 234)
GLOVE_D = (196, 196, 204)
SHOE = (24, 22, 30)
SHOE_H = (92, 92, 112)


def _dark(c, k=.72):
    return tuple(int(v * k) for v in c[:3])


def head(mouth=False, scared=False):
    """24×24 头：脸型 / 眼 / 嘴 / 耳的像素和其他后续人物同一套，发型、圆筒帽、帽带是门童自己的。"""
    im = Image.new('RGBA', (24, 24))
    d = ImageDraw.Draw(im)
    d.ellipse((6, 5, 18, 18), fill=SKIN, outline=K)
    d.polygon([(16, 10), (21, 12), (18, 14), (17, 17), (10, 19), (7, 15)], fill=SKIN, outline=K)
    # 梳得服帖的黑发：后脑一片 + 帽檐下一道整齐的发际线（额头留出 2 行皮肤，不压眼睛）+ 鬓角
    d.polygon([(5, 12), (5, 7), (8, 5), (16, 5), (17, 6), (11, 7), (11, 10), (9, 12)], fill=HAIR, outline=K)
    d.line((7, 7, 9, 6), fill=HAIR_H)
    d.rectangle((7, 13, 9, 15), fill=SKIN_D)                       # 耳
    # 眼 / 嘴（同其他后续人物）
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
    # 红色圆筒小帽，歪戴在头顶偏后：帽身 + 金帽箍 + 顶上金边 + 一颗金扣
    d.rectangle((7, 0, 15, 4), fill=RED, outline=K)
    d.line((8, 1, 14, 1), fill=GOLD)
    d.line((8, 2, 8, 3), fill=RED_H)
    d.line((14, 2, 14, 3), fill=RED_D)
    d.rectangle((6, 4, 16, 5), fill=GOLD_D, outline=K)
    d.line((7, 4, 15, 4), fill=GOLD)
    d.point((11, 2), fill=GOLD)
    return im


def _jacket(d, x, top, hip, bob):
    """红色短外套：上宽下略收，金立领，两排金扣，左上亮右边暗，下摆到腰。"""
    d.polygon([(x - 6, top + bob), (x + 6, top + bob), (x + 7, hip - 2), (x - 7, hip - 2)], fill=RED, outline=K)
    d.line((x - 5, top + 2 + bob, x - 5, hip - 4), fill=RED_H)
    d.line((x + 5, top + 3 + bob, x + 5, hip - 3), fill=RED_D)
    d.polygon([(x - 3, top + bob), (x + 4, top + bob), (x + 3, top + 2 + bob), (x - 2, top + 2 + bob)], fill=GOLD, outline=K)
    for yy in range(top + 4 + bob, hip - 3, 3):                    # 两排金扣
        d.point((x - 1, yy), fill=GOLD)
        d.point((x + 2, yy), fill=GOLD)
    d.line((x - 6, hip - 2, x + 6, hip - 2), fill=GOLD_D)          # 下摆金边


def body(action='idle', fi=0):
    w = 36
    im = Image.new('RGBA', (w, H))
    d = ImageDraw.Draw(im)
    hx = w // 2
    head_y = 1
    hh = 21
    top = hh - 3
    hip = H - 14
    ground = H - 2
    bob = (fi % 2) if action in ('idle', 'walk', 'run', 'talk') else 0
    leaning = -3 if action == 'hurt' else 0
    x = hx + leaning

    if action == 'down':
        # 倒地：和其他后续人物同一个姿势（头朝左、腰膝重画）
        out = Image.new('RGBA', (H + 12, 22))
        q = ImageDraw.Draw(out)
        limb(q, [(23, 14), (35, 16), (H + 2, 18)], PANTS, 5)
        limb(q, [(26, 12), (38, 9), (H + 3, 15)], _dark(PANTS, .7), 4)
        q.line((28, 16, H, 18), fill=STRIPE)
        q.rectangle((H + 1, 14, H + 8, 19), fill=SHOE, outline=K)
        q.line((H + 2, 15, H + 7, 15), fill=SHOE_H)
        q.polygon([(12, 10), (28, 10), (30, 18), (12, 19)], fill=RED, outline=K)
        for xx in range(16, 28, 3):
            q.point((xx, 13), fill=GOLD)
            q.point((xx, 16), fill=GOLD)
        q.line((27, 11, 29, 18), fill=GOLD_D)
        limb(q, [(17, 12), (21, 18), (29, 17)], RED, 3)
        q.rectangle((28, 16, 31, 19), fill=GLOVE, outline=K)
        hd = head(scared=True).crop((0, 0, 24, 24)).transpose(Image.Transpose.ROTATE_90)
        out.alpha_composite(hd, (0, -2))
        return out

    stride = (-3, 0, 3, 0)[fi % 4] if action in ('walk', 'run') else 0
    near = (x + 3, hip, x + 3 + stride, ground - 1)
    far = (x - 4, hip, x - 4 - stride, ground - 2)
    limb(d, [(far[0], far[1]), (far[2], far[3])], _dark(PANTS, .8), 4)
    limb(d, [(near[0], near[1]), (near[2], near[3])], PANTS, 4)
    d.line((near[0] + 1, near[1] + 1, near[2] + 1, near[3] - 1), fill=STRIPE)       # 裤缝红线
    for i, (xx, yy) in enumerate(((far[2], far[3]), (near[2], near[3]))):
        d.rectangle((xx - 2, yy, xx + 4, yy + 1), fill=_dark(SHOE, .9) if i == 0 else SHOE, outline=K)
        if i == 1:
            d.point((xx + 2, yy), fill=SHOE_H)
    _jacket(d, x, top, hip, bob)

    ay = top + 4 + bob
    arm_end = hip - 1
    if action in ('hurt', 'shock'):
        limb(d, [(x + 6, ay), (x + 10, ay + 4), (x + 7, top - 1)], RED, 4)
        d.rectangle((x + 6, top - 3, x + 9, top), fill=GLOVE, outline=K)
    else:
        swing = -stride // 2
        limb(d, [(x + 6, ay), (x + 8, ay + 5), (x + 7 + swing, arm_end - 1)], RED, 4)
        d.line((x + 5 + swing, arm_end - 2, x + 9 + swing, arm_end - 2), fill=GOLD)    # 金袖口
        d.rectangle((x + 6 + swing, arm_end - 1, x + 9 + swing, arm_end + 2), fill=GLOVE, outline=K)
        d.point((x + 8 + swing, arm_end + 1), fill=GLOVE_D)
    limb(d, [(x - 6, ay), (x - 8, ay + 6), (x - 8 + stride // 2, arm_end - 1)], RED_D, 3)
    d.rectangle((x - 9 + stride // 2, arm_end - 1, x - 7 + stride // 2, arm_end + 1), fill=GLOVE_D, outline=K)
    hd = head(mouth=action == 'talk', scared=action in ('hurt', 'shock'))
    im.alpha_composite(hd, (x - hd.width // 2, head_y + bob))
    return im


def portrait(fi=0, expression='portrait'):
    out = Image.new('RGBA', (32, 32))
    d = ImageDraw.Draw(out)
    d.polygon([(1, 31), (6, 23), (14, 21), (24, 23), (30, 31)], fill=RED, outline=K)
    d.line((5, 25, 3, 31), fill=RED_H)
    d.polygon([(11, 21), (20, 21), (19, 24), (12, 24)], fill=GOLD, outline=K)      # 金立领
    for yy in (27, 30):
        d.point((14, yy), fill=GOLD)
        d.point((18, yy), fill=GOLD)
    hd = head(mouth=bool(fi), scared=expression in ('portrait_scared', 'portrait_reveal'))
    out.alpha_composite(hd.resize((30, 30), Image.Resampling.NEAREST), (1, -1))
    return out


def register():
    """和 art_later_people.register 同样的名字 / 锚点 / 帧率 / 说明，帧是本文件画的。"""
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
ONESHOT = {'hurt', 'down', 'shock'}
STATIC_STATES = set()
CHAR_INFO = {CID: dict(zh=ZH, en='bellhop', cat='人物', typ='人物')}
