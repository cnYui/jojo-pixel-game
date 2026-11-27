# 逐帧检查图：把一个 Sheet 的每个动作每一帧放大排开（带脚底线、动作名、帧号），人眼逐帧看有没有错位、缺腿、手画坏。
import os

from PIL import Image, ImageDraw, ImageFont

from rig import CW, CH, OX, OY

FONT = None
for fp in (r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simhei.ttf', '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'):
    if os.path.exists(fp):
        FONT = fp
        break


def font(sz):
    return ImageFont.truetype(FONT, sz) if FONT else ImageFont.load_default()


def _abs(crop):
    """crop 写成相对骨架原点（脚底中点）的 (左, 上, 右, 下)，换成工作画布坐标"""
    return OX + crop[0], OY + crop[1], OX + crop[2], OY + crop[3]


def sheet_view(sh, k=5, bg='#3a3c50', crop=(-24, -44, 36, 4), cols=None, title=None):
    """sh = rig.Sheet；crop = 每帧截哪一块（相对脚底中点）"""
    x0, y0, x1, y1 = _abs(crop)
    fw, fh = (x1 - x0) * k, (y1 - y0) * k
    n = cols or max(len(r[1]) for r in sh.rows)
    lab = 84
    W = lab + n * (fw + 4) + 4
    H = (22 if title else 0) + len(sh.rows) * (fh + 4) + 4
    im = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(im)
    top = 0
    if title:
        d.text((6, 2), title, fill='#ffe070', font=font(14))
        top = 22
    for r, (anim, frs, fps, kind) in enumerate(sh.rows):
        y = top + 4 + r * (fh + 4)
        d.text((4, y + 4), anim, fill='#ffffff', font=font(13))
        d.text((4, y + 22), '%d 帧 @%s %s' % (len(frs), fps, kind), fill='#a0a4c0', font=font(10))
        for i, f in enumerate(frs):
            x = lab + i * (fw + 4)
            cell = Image.new('RGB', (fw, fh), '#50546c' if (i + r) % 2 else '#4a4e66')
            cd = ImageDraw.Draw(cell)
            gy = (OY + 1 - y0) * k
            cd.line((0, gy, fw, gy), fill='#8a8ea8')
            gx = (OX - x0) * k
            cd.line((gx, gy - 3, gx, gy + 3), fill='#8a8ea8')
            sub = f.img().crop((x0, y0, x1, y1)).resize((fw, fh), Image.NEAREST)
            cell.paste(sub, (0, 0), sub)
            im.paste(cell, (x, y))
    return im


def compact(sh, k=6, per_row=8, crop=(-20, -38, 20, 3), bg='#3a3c50', title=None):
    """所有帧挨个排（每格左上角写 动作名#帧号），一张图看完一个人物的全部帧"""
    x0, y0, x1, y1 = _abs(crop)
    fw, fh = (x1 - x0) * k, (y1 - y0) * k
    cells = [(a, i, f) for a, frs, _, _ in sh.rows for i, f in enumerate(frs)]
    nrow = (len(cells) + per_row - 1) // per_row
    top = 22 if title else 0
    im = Image.new('RGB', (per_row * (fw + 3) + 3, top + nrow * (fh + 3) + 3), bg)
    d = ImageDraw.Draw(im)
    if title:
        d.text((6, 2), title, fill='#ffe070', font=font(14))
    last = None
    for n, (a, i, f) in enumerate(cells):
        x, y = 3 + (n % per_row) * (fw + 3), top + 3 + (n // per_row) * (fh + 3)
        cell = Image.new('RGB', (fw, fh), '#50546c' if a != last and i == 0 else '#474b63')
        cd = ImageDraw.Draw(cell)
        gy = (OY + 1 - y0) * k
        cd.line((0, gy, fw, gy), fill='#8a8ea8')
        sub = f.img().crop((x0, y0, x1, y1)).resize((fw, fh), Image.NEAREST)
        cell.paste(sub, (0, 0), sub)
        cd.text((3, 1), '%s#%d' % (a, i), fill='#ffffff', font=font(12))
        im.paste(cell, (x, y))
        last = a
    return im


def lineup(frames, names=None, k=4, bg='#4a4e66', gap=4, ref_h=None, crop=(-18, -40, 22, 2)):
    """几个人站一排比身高；ref_h = [(px, 标注)…] 画参考高度线"""
    x0, y0, x1, y1 = _abs(crop)
    fw, fh = (x1 - x0) * k, (y1 - y0) * k
    W = len(frames) * (fw // 2 + gap) + fw // 2 + 60
    H = fh + 24
    im = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(im)
    gy = (OY + 1 - y0) * k
    d.line((0, gy, W, gy), fill='#c0c4d8')
    for px, lab in (ref_h or []):
        yy = gy - px * k
        d.line((0, yy, W, yy), fill='#7a7e98')
        d.text((2, yy - 12), lab, fill='#c0c4d8', font=font(10))
    for i, f in enumerate(frames):
        sub = f.img().crop((x0, y0, x1, y1)).resize((fw, fh), Image.NEAREST)
        x = 50 + i * (fw // 2 + gap)
        im.paste(sub, (x, 0), sub)
        if names:
            d.text((x + fw // 4, H - 20), names[i], fill='#ffffff', font=font(11))
    return im
