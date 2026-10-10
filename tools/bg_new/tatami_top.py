"""拔肉芽插入画面的榻榻米底图（俯视 320×180，static）。

2026-10-10 bg-pro 重画（旧版在 _旧稿\\tatami_top_20261010前.py）：接缝位置照旧（横缝 y 90，上排竖缝 x 80 / 240，
下排竖缝 x 160），每张席子按自己的方向织：中间两张横放（织纹横向、长边上下镶边），左右两张竖放（织纹竖向、
长边左右镶边）；短边只有一条压缝。镶边布是深绿底 + 浅色小花纹；席面是两色交替的蔺草行 + 经线针脚 +
零星的草屑和旧色。左上来的窗光很淡；最后照旧压四档像素暗角（边上最多暗 50%），中间的脸和肉芽 (160,70) 不受影响。
"""
import sys
sys.dont_write_bytecode = True

import os
import numpy as np
from PIL import Image, ImageDraw

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from engine import bg_asia as A
from engine.core import hash01

W, H = 320, 180
STRAW, STRAW2, STITCH = (188, 180, 112), (174, 166, 100), (160, 152, 92)
HERI, HERI_HI, HERI_DK = (44, 60, 44), (86, 100, 70), (30, 40, 30)
SEAM = (120, 112, 66)
# (x0, y0, x1, y1, 方向)：'h' = 横放（织纹横、上下镶边），'v' = 竖放（织纹竖、左右镶边）
MATS = [(0, 0, 80, 90, 'v'), (80, 0, 240, 90, 'h'), (240, 0, 320, 90, 'v'),
        (0, 90, 160, 180, 'h'), (160, 90, 320, 180, 'h')]


def mat(a, x0, y0, x1, y1, ori):
    ys, xs = np.mgrid[y0:y1, x0:x1]
    along = xs if ori == 'v' else ys                 # 蔺草行沿长边：横放的按 y 交替，竖放的按 x 交替
    across = ys if ori == 'v' else xs
    col = np.where((along % 2)[..., None] == 0, np.array(STRAW), np.array(STRAW2))
    stitch = (across % 7 == 3) & (along % 2 == 1)     # 经线针脚
    col = np.where(stitch[..., None], np.array(STITCH), col)
    a[y0:y1, x0:x1, :3] = col
    # 镶边（长边）
    if ori == 'h':
        bands = [(y0, y0 + 3), (y1 - 3, y1)]
        for b0, b1 in bands:
            a[b0:b1, x0:x1, :3] = HERI
            a[b0 + 1, x0 + 1:x1:4, :3] = HERI_HI
            a[b0 if b0 == y0 else b1 - 1, x0:x1, :3] = HERI_DK
    else:
        bands = [(x0, x0 + 3), (x1 - 3, x1)]
        for b0, b1 in bands:
            a[y0:y1, b0:b1, :3] = HERI
            a[y0 + 1:y1:4, b0 + 1, :3] = HERI_HI
            a[y0:y1, b0 if b0 == x0 else b1 - 1, :3] = HERI_DK
    # 短边压缝
    if ori == 'h':
        a[y0:y1, x0, :3] = SEAM
        a[y0:y1, x1 - 1, :3] = SEAM
    else:
        a[y0, x0:x1, :3] = SEAM
        a[y1 - 1, x0:x1, :3] = SEAM


def build():
    a = np.zeros((H, W, 4), np.uint8)
    a[:, :, 3] = 255
    for m in MATS:
        mat(a, *m)
    im = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(im)
    for i in range(60):                                                         # 草屑 / 旧色斑
        x = int(hash01(i, 301) * W)
        y = int(hash01(i, 302) * H)
        if 120 <= x <= 200 and 30 <= y <= 120:
            continue
        if i % 3 == 0:
            d.line((x, y, x + 2, y + (1 if i % 2 else 0)), fill=(206, 196, 130, 255))
        else:
            d.point((x, y), fill=(150, 142, 84, 255))
    A._tex_noise(im, (0, 0, W, H), 0.05, 46, cell=2)
    A._blend_poly(im, [(0, 0), (120, 0), (40, 180), (0, 180)], (255, 246, 214), 18)   # 左上来的窗光
    a = np.array(im)
    ys, xs = np.mgrid[0:180, 0:320]
    radius = ((xs - 159.5) / 159.5) ** 2 + ((ys - 89.5) / 89.5) ** 2
    shade = 1 - np.minimum(1, np.floor(radius * 4) / 4) * 0.5                  # 四档暗角，边上最多暗 50%
    a[:, :, :3] = np.round(a[:, :, :3] * shade[:, :, None]).astype(np.uint8)
    a[:, :, 3] = 255
    return Image.fromarray(a, 'RGBA')


def export(ex, BJ):
    im = build()
    st = ex.stage(320, 156, (148, 176), [dict(type='static', image=ex.img('static', im))],
                  anchors=dict(center=[160, 90], fleshbud=[160, 70]))
    if ex.check_on:
        ex.checked('榻榻米导出 vs 直接绘制', BJ.ndiff_rgba(BJ.ref_render(st, ex.images, 0, 0), im))
        ex.checked('榻榻米全幅不透明', int((np.array(im)[:, :, 3] != 255).sum()))
    return st


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_preview', 'bg_pro', 'tatami_top_solo.png')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build().resize((1280, 720), Image.Resampling.NEAREST).save(out)
    print(out)
