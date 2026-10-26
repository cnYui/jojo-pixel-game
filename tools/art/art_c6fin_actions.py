"""第6章到终章补的角色动作（2026-10-19，素材总表 §三）。

  joseph / avdol / kakyoin / polnareff .sit   坐在椅子上（侧身、大腿水平、小腿垂到地上）：第6章机舱、第8章茶馆、第10章赌桌。
                                              照 jotaro.sit 的姿势：脚踩地、锚点在脚下，剧情把人放在椅子前的地面上（z = 0）。
  kakyoin.cover_eyes                          跪着、双手捂眼（第8章被盖布神划伤眼睛；不画伤口）。
  steelydan.walk                              走路 4 帧（第5章街头命令：踩着承太郎走过去）。
  dio.sit_back                                背对镜头坐在台阶上（第10章荷尔·荷斯的回忆：只看得见金发和背影）。
  fake_jotaro（新角色）                       奥因哥变的承太郎：照承太郎的帧，帽顶多出一个尖、帽檐上的金扣换成一颗橘子，
                                              头像咧嘴笑——玩家仔细看能认出来，粗看又像（第8章阿斯旺）。
二乔的新脸是 art_joseph.apply() 在审计之后才换上去的，这里直接用 art_joseph 的同一套参数现做新脸 idle 再派生坐姿，
所以本模块要排在 ART_MODULES 里 art_joseph 之后。
"""
import sys
sys.dont_write_bytecode = True

import numpy as np
from PIL import Image, ImageDraw

import art_common as AC                     # noqa: F401  （设好 sys.path）
from engine import sprite
import art_later_existing as LE
import art_joseph as AJ
from assets import sprites_jojo as SJ

NEW = []
ONESHOT = set()
STATIC_STATES = {'sit', 'cover_eyes', 'sit_back'}
CHAR_INFO = {'fake_jotaro': dict(zh='承太郎？', en='fake_jotaro', cat='人物', typ='人物')}

K = (26, 16, 32)
SKIN = (216, 166, 126)

# 每个人的腰线（idle 第 0 帧里大腿开始的那一行）、裤子 / 外套颜色、是不是长外套（坐下时下摆盖住大腿）、鞋色
SIT = {
    'joseph': dict(hip=34, pants=(98, 104, 58), coat=(176, 160, 104), long=False, shoe=(90, 54, 30)),
    'avdol': dict(hip=31, pants=(218, 202, 170), coat=(196, 48, 40), long=True, shoe=(120, 84, 52)),
    'kakyoin': dict(hip=30, pants=(40, 132, 64), coat=(46, 150, 72), long=True, shoe=(70, 50, 40)),
    'polnareff': dict(hip=37, pants=(206, 210, 232), coat=(40, 36, 44), long=False, shoe=(110, 70, 40)),
    'dio': dict(hip=34, pants=(40, 34, 46), coat=(228, 176, 40), long=False, shoe=(60, 40, 36)),
}


def _define(name, frames, anchor, fps=3):
    if name in sprite._REG:
        raise ValueError('新动作与已有注册冲突：' + name)
    sprite.define(name, frames, anchor=anchor, fps=fps, desc='第6章到终章补帧：' + name)
    NEW.append(name)


def _idle0(cid):
    if cid == 'joseph':
        # 新脸版 idle（和 art_joseph.apply 换上去的逐像素一致）：jo_frame 出来的是字符格子，按二乔的调色板转成图
        grid = AJ._orig_frame(AJ._orig_params()['joseph.idle'][0], AJ.JO_FACE2)
        pal = dict(sprite.PAL)
        pal.update(SJ.JOPAL)
        return sprite._parse(grid, pal)
    return sprite.get(cid + '.idle').frames[0].copy()


def _anchor_x(cid, src):
    sd = sprite.get(cid + '.idle')
    ax, _ = sprite._anchor_px(sd.anchor, *src.size)
    return ax


def sit_frame(cid, src=None):
    """上身照 idle 原样保留（发型、脸、衣纹都是本人的），腰以下重画成坐姿：两条大腿往前（右）水平伸出、小腿垂直落地。"""
    o = SIT[cid]
    src = src if src is not None else _idle0(cid)
    w, h = src.size
    hip, shin = o['hip'], 12
    out = Image.new('RGBA', (w + 12, hip + shin))
    out.alpha_composite(src.crop((0, 0, w, hip)), (0, 0))
    d = ImageDraw.Draw(out)
    cx = w // 2
    far = tuple(max(0, c - 34) for c in o['pants'])
    foot = hip + shin - 1
    # 远侧腿（深一档）先画，近侧腿压在上面、往右多伸 2 px
    for dx, dy, col in ((0, 1, far), (2, 3, o['pants'])):
        kx = cx + 9 + dx
        LE.limb(d, [(cx - 3 + dx, hip + dy), (kx, hip + dy + 1)], col, 5)
        LE.limb(d, [(kx, hip + dy + 1), (kx, foot - 2)], col, 4)
        d.rectangle((kx - 1, foot - 2, kx + 4, foot), fill=o['shoe'], outline=K)
    if o['long']:
        # 长外套 / 长袍：下摆从腰往前盖住大腿根，后摆垂在椅子后面
        d.polygon([(cx - 7, hip - 3), (cx + 6, hip - 3), (cx + 12, hip + 4), (cx + 9, hip + 7), (cx - 6, hip + 6)],
                  fill=o['coat'], outline=K)
        d.polygon([(cx - 8, hip - 1), (cx - 3, hip - 1), (cx - 4, hip + 9), (cx - 10, hip + 9)], fill=o['coat'], outline=K)
    return out, (_anchor_x(cid, src), out.height)


def cover_eyes_frame():
    """跪姿（art_later_existing 的 kneel）+ 两只手捂在眼睛上：前臂从胸前竖着折到脸前，两只手掌并排盖住两只眼睛。
    坐标按花京院 idle（32×48：眼睛在 y 14–15、x 16 / 20，肩在 y 22）；kneel 把上身贴在 (4, 0)。"""
    out = LE.action('kakyoin', 'kneel')
    d = ImageDraw.Draw(out)
    ox = 4
    coat = SIT['kakyoin']['coat']
    for (ex, ey), (hx0, hx1) in (((ox + 11, 25), (ox + 13, ox + 17)), ((ox + 23, 25), (ox + 18, ox + 22))):
        LE.limb(d, [(ex, ey), ((hx0 + hx1) // 2, 17)], coat, 3)
        d.rectangle((hx0, 13, hx1, 16), fill=SKIN, outline=K)
        d.line((hx0 + 1, 13, hx1 - 1, 13), fill=(236, 196, 160))        # 指尖的亮边
    return out


def _hair_over_face(im, top_rows=22):
    """把脸部的皮肤 / 眼睛 / 唇色换成头发色：坐着背对镜头时只看得到后脑勺的金发。"""
    a = np.array(im)
    H = min(top_rows, a.shape[0])
    rgb = a[:H, :, :3].astype(int)
    op = a[:H, :, 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    skin = op & (r > 170) & (g > 110) & (g < 200) & (b > 70) & (b < 170) & (r - b > 40)
    eye = op & (r > 150) & (g < 90) & (b < 90)
    lip = op & (g > r + 20) & (g > b)
    m = skin | eye | lip
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        a[y, x, :3] = (250, 214, 84) if (x + y) % 4 else (214, 164, 52)
    return Image.fromarray(a, 'RGBA')


# ------------------------------------------------------------------- 假承太郎
ORANGE, ORANGE_D = (245, 144, 42), (196, 96, 28)


def _fake_hat(im, portrait=False):
    """帽顶加一个尖（上面要留 3 行空）、帽檐金扣换成橘子色：在原帧上直接改，其他像素一个不动。"""
    a = np.array(im)
    pad = 0 if portrait else 3          # 头像不加高（对话框头像格是固定的），帽尖画在原有的空行里，画不下就不画
    out = np.zeros((a.shape[0] + pad, a.shape[1], 4), np.uint8)
    out[pad:] = a
    op = out[..., 3] > 0
    rows = np.nonzero(op.any(1))[0]
    top = rows[0]
    xs = np.nonzero(op[top])[0]
    mx = int(xs[len(xs) // 2]) - (1 if not portrait else 3)
    hat = tuple(int(v) for v in out[top + 2, mx, :3]) if out[top + 2, mx, 3] else (40, 44, 92)
    im2 = Image.fromarray(out, 'RGBA')
    d = ImageDraw.Draw(im2)
    s = 3 if not portrait else 4
    if top >= s:
        d.polygon([(mx - s, top + 1), (mx, top - s + 1), (mx + s, top + 1)], fill=hat, outline=K)
        d.line((mx - s + 1, top + 1, mx + s - 1, top + 1), fill=hat)
    a2 = np.array(im2)
    rgb = a2[..., :3].astype(int)
    gold = (a2[..., 3] > 0) & (rgb[..., 0] > 200) & (rgb[..., 1] > 150) & (rgb[..., 2] < 110)
    gold[int(a2.shape[0] * (0.45 if not portrait else 0.6)):, :] = False     # 只改帽子上的扣，衣领上的金链不动
    ys, xs = np.nonzero(gold)
    for y, x in zip(ys, xs):
        a2[y, x, :3] = ORANGE if (y + x) % 3 else ORANGE_D
    return Image.fromarray(a2, 'RGBA')


def _fake_grin(im):
    """头像的嘴换成奥因哥式的咧嘴笑：一道白牙 + 上下深色边。"""
    d = ImageDraw.Draw(im)
    w, h = im.size
    y = int(h * 0.66)
    x0, x1 = w // 2 - 2, w // 2 + 5
    d.rectangle((x0, y, x1, y + 2), fill=K)
    d.line((x0 + 1, y + 1, x1 - 1, y + 1), fill=(250, 248, 240))
    d.point((x1, y - 1), fill=K)
    return im


def _register():
    for cid in ('joseph', 'avdol', 'kakyoin', 'polnareff'):
        fr, anchor = sit_frame(cid)
        _define(cid + '.sit', [fr], anchor)
    _define('kakyoin.cover_eyes', [cover_eyes_frame()], 'mb')
    walk = [LE.action('steelydan', 'walk', i) for i in range(4)]
    sd = sprite.get('steelydan.idle')
    _define('steelydan.walk', walk, sprite._anchor_px(sd.anchor, *sd.frames[0].size), fps=6)
    fr, anchor = sit_frame('dio')
    _define('dio.sit_back', [_hair_over_face(fr)], anchor)
    # 假承太郎：每个动作都照承太郎的帧改帽子；锚点往下挪 3 行（帽尖多出来的空行）
    for act in ('idle', 'walk', 'hurt', 'sit'):
        src = sprite.get('jotaro.' + act)
        frames = [_fake_hat(f) for f in src.frames]
        ax, ay = sprite._anchor_px(src.anchor, *src.frames[0].size)
        _define('fake_jotaro.' + act, frames, (ax, ay + 3), fps=src.fps or (6 if act == 'walk' else 3))
    por = sprite.get('jotaro.portrait')
    frames = [_fake_grin(_fake_hat(f, portrait=True)) for f in por.frames]
    _define('fake_jotaro.portrait', frames, 'mm')


_register()
