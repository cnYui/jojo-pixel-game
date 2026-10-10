"""补齐剧情实际说话角色的近景头像，保留各自原造型而不借用其他角色。"""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
from engine import sprite

NEW = []
CHAR_INFO = {}
K = (26, 16, 32)

# 裁区分别保留发型、头饰与肩部；不把全身缩图当成对话头像。
HEADS = {
    'alessi': ('idle', (5, 0, 28, 28), (19, 15, 23, 17)),
    'boingo': ('idle', (4, 10, 24, 35), (17, 30, 20, 32)),
    'judgement': ('idle', (9, 0, 31, 28), None),
    'npc_hk_passer_a': ('idle', (7, 6, 26, 30), (20, 20, 22, 21)),
    # 妇人的头随 art_npc.NPC_HEAD_DX 往前挪了 2 px（头身对位，2026-10-09 晚）：裁框跟着挪；
    # 说话帧的嘴以前画在 (19..21, 21..22) 衣领上，改到真正的嘴（头格第 10 行第 9 列 → 帧 (16, 19)）
    'npc_hk_passer_b': ('idle', (6, 8, 28, 31), (15, 19, 17, 20)),
    'npc_passenger_a': ('seated', (0, 0, 16, 18), (10, 11, 12, 13)),
    'steelydan': ('idle', (6, 0, 28, 26), (19, 17, 23, 19)),
    'death13': ('float', (10, 0, 34, 29), (18, 17, 25, 19)),
    'ndoul': ('idle', (7, 11, 27, 34), (16, 23, 19, 24)),
    'oingo': ('idle', (6, 0, 23, 30), (11, 17, 15, 19)),
    'mariah': ('idle', (7, 3, 27, 29), (17, 15, 20, 16)),
}


def closeup(cid, frame):
    act, box, mouth = HEADS[cid]
    src = sprite.get(cid + '.' + act).frames[0].copy()
    if frame and mouth:
        d = ImageDraw.Draw(src)
        d.rectangle(mouth, fill=K)
        d.line((mouth[0] + 1, mouth[1], mouth[2] - 1, mouth[1]), fill=(248, 228, 196))
    elif frame and cid == 'judgement':
        # 金属栅格不长出人类嘴唇，说话帧用眼灯和栅格内光表达。
        d = ImageDraw.Draw(src)
        d.rectangle((16, 8, 25, 9), fill=(180, 248, 255))
        d.line((16, 18, 26, 18), fill=(176, 216, 236))
    crop = src.crop(box)
    scale = min(30 / crop.width, 30 / crop.height)
    crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.Resampling.NEAREST)
    im = Image.new('RGBA', (32, 32))
    im.alpha_composite(crop, ((32 - crop.width) // 2, 32 - crop.height))
    return im


def empress_head(frame):
    # 女帝是寄生替身，保留双角、粉色皮肤和嘲笑的尖牙脸；不用人类头像模板。
    im = Image.new('RGBA', (32, 32)); d = ImageDraw.Draw(im)
    skin, light, shade = (202, 108, 138), (226, 144, 150), (128, 54, 94)
    d.polygon([(6, 10), (4, 3), (7, 5), (10, 9), (22, 9), (25, 2), (27, 1), (26, 11)], fill=shade, outline=K)
    d.ellipse((4, 7, 28, 29), fill=skin, outline=K)
    d.ellipse((11, 8, 28, 24), fill=light, outline=K)
    d.polygon([(15, 12), (20, 13), (18, 15), (15, 14)], fill=K)
    d.polygon([(22, 12), (26, 11), (26, 14), (23, 15)], fill=K)
    d.point((17, 13), fill=(248, 228, 196)); d.point((24, 13), fill=(248, 228, 196))
    d.line((21, 15, 23, 17), fill=shade, width=2)
    d.arc((13, 15, 27, 23 + frame * 2), 0, 175, fill=K, width=2)
    if frame:
        d.rectangle((16, 19, 25, 23), fill=K)
        for x in (17, 20, 23): d.line((x, 19, x, 20), fill=(248, 228, 196))
    d.polygon([(4, 27), (9, 24), (15, 28), (22, 27), (29, 30), (29, 31), (3, 31)], fill=shade, outline=K)
    return im


for cid in [*HEADS, 'empress']:
    name = cid + '.portrait'
    if name in sprite._REG:
        raise ValueError('补充头像和已注册精灵重名：' + name)
    frames = [empress_head(i) if cid == 'empress' else closeup(cid, i) for i in range(2)]
    sprite.define(name, frames, anchor='mm', fps=8, desc='剧情近景对话头像：静态 / 说话')
    NEW.append(name)
