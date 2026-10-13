# -*- coding: utf-8 -*-
r"""特效纹理烘焙（包 6，技术约定 §3.9 / §5.7）。

JS 复现不了 numpy 的随机数（_noise_tex）和 scipy 的高斯模糊（_ankh_field），所以构建时用原工程函数算好存 PNG：
    fx/noise0..3   fx._noise_tex(seed, 64, 64)，灰度 L 图（aura_flame、fire 用）
    fx/ankh34/38/40/44   fx._ankh_field(S)：R 通道 = core、G 通道 = up（归一化到 0–255，B = 0，A = 255）（fire_ankh 用）

被 build_assets.py 的 fx 步调用：build(c) → fxtex 元数据
    { noise: ['fx/noise0', …], ankh: { '34': 'fx/ankh34', … },
      ankhPad: { '34': pad, … },          # _ankh_field 返回的 pad（图里的 ankh 离边缘的像素数；fire_ankh 定位用）
      ankhScale: { '34': k, … } }         # 解码：core = R / 255 × k（原值最大约 1，k 一般就是 1.0）

单独跑（只出预览，不写 assets）：python -B tools\fx_tex.py --preview C:\...\fx_preview.png
"""
import sys
sys.dont_write_bytecode = True

import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
from source_workspace import SRC as SOURCE_SRC
SRC = str(SOURCE_SRC)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

NOISE_SEEDS = (0, 1, 2, 3)
ANKH_SIZES = (34, 38, 40, 44)


def noise_img(seed):
    from engine import fx as FX
    a = FX._noise_tex(seed, 64, 64)
    return Image.fromarray(np.clip(np.round(a * 255), 0, 255).astype(np.uint8), "L")


def ankh_img(S):
    """→ (RGBA 图, pad, scale)。"""
    from engine import fx as FX
    field, pad = FX._ankh_field(S)
    core, up = field[0], field[1]
    k = float(max(1.0, core.max(), up.max()))
    h, w = core.shape
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 0] = np.clip(np.round(core / k * 255), 0, 255)
    rgba[..., 1] = np.clip(np.round(up / k * 255), 0, 255)
    rgba[..., 3] = 255
    return Image.fromarray(rgba, "RGBA"), int(pad), round(k, 4)


def build(c):
    save = c["save_png"]
    meta = dict(noise=[], ankh={}, ankhPad={}, ankhScale={})
    for s in NOISE_SEEDS:
        meta["noise"].append(save(noise_img(s), f"fx/noise{s}", "core", sub="fx"))
    for S in ANKH_SIZES:
        im, pad, k = ankh_img(S)
        meta["ankh"][str(S)] = save(im, f"fx/ankh{S}", "core", sub="fx")
        meta["ankhPad"][str(S)] = pad
        meta["ankhScale"][str(S)] = k
    return meta


def _preview(path):
    ims = [noise_img(s).convert("RGBA").resize((128, 128), Image.NEAREST) for s in NOISE_SEEDS]
    for S in ANKH_SIZES:
        im, _pad, _k = ankh_img(S)
        ims.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
    W_ = sum(i.width for i in ims) + 8 * (len(ims) + 1)
    H_ = max(i.height for i in ims) + 16
    sheet = Image.new("RGBA", (W_, H_), (40, 44, 60, 255))
    x = 8
    for i in ims:
        sheet.alpha_composite(i, (x, 8))
        x += i.width + 8
    sheet.convert("RGB").save(path)
    print(f"→ {path}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", required=True)
    _preview(ap.parse_args().preview)
