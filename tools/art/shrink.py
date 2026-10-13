# -*- coding: utf-8 -*-
"""像素画整体缩小（2026-10-11：把 JoJo 的人物比例收到和《银魂》一样）。

为什么不用最近邻 / 双线性：
  最近邻缩 0.625 会随机丢点（脸、手指、描边断掉），双线性会把像素风糊成渐变。
  这里的做法 = “多数色 + 描边优先”：每个目标像素看它覆盖的那一小块源像素，
  按重叠面积给每种颜色投票（最深的那圈描边色权重 ×OUTLINE_W），票数最多的颜色就是结果；
  源像素不透明的面积占比不到 THR，目标像素透明。
  输出的每个颜色都是原图里已经有的颜色（不引入新色），轮廓和描边都保持 1 像素。

对齐：以 pivot 为不动点（pivot → 取整后的 pivot'），每一帧都按同一个映射缩，
所以帧与帧之间不会因为取整抖动。

用法：
    new_sheet, new_cell, new_pivot = shrink_sheet(sheet_img, cell, pivot, k)
    new_img, new_pivot = shrink_image(img, pivot, k)          # 单张（道具 / 场景小图）
"""
import math
import sys

sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

CK = 0.625          # 全游戏统一的“人物缩小系数”（5/8）：承太郎 47 px → 29 px，约占画布高 16%，《银魂》是 15.7%
THR = 0.42          # 目标像素里不透明面积占比 ≥ 这个才算不透明
OUTLINE_W = 1.8     # 最深那圈描边色的投票权重（1 像素细线不被邻居吞掉）
OUTLINE_BAND = 14   # 亮度比整张图最暗色亮不超过这个，都算“描边色”


def _dims(cw, ch, px, py, k):
    opx = int(math.ceil(px * k - 1e-6))
    opy = int(math.ceil(py * k - 1e-6))
    ow = opx + int(math.ceil((cw - px) * k - 1e-6))
    oh = opy + int(math.ceil((ch - py) * k - 1e-6))
    return ow, oh, opx, opy


def _palette(rgba):
    """整张图的不透明颜色表 → (颜色数组 P×3, 每个像素的色号 H×W（透明 -1）)"""
    a = rgba[..., 3] > 127
    rgb = rgba[..., :3].astype(np.int64)
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    uniq, inv = np.unique(key[a], return_inverse=True)
    idx = np.full(a.shape, -1, np.int32)
    idx[a] = inv.astype(np.int32)
    cols = np.stack([(uniq >> 16) & 255, (uniq >> 8) & 255, uniq & 255], axis=1).astype(np.uint8)
    return cols, idx


def _shrink_idx(idx, imp, px, py, k, ow, oh, opx, opy, thr):
    """idx：色号图（-1 透明）；imp：每个色号的投票权重。返回 (oh×ow 色号，-1 透明)。"""
    h, w = idx.shape
    P = len(imp)
    n = int(math.ceil(1.0 / k)) + 1
    # 每个目标像素在源图里的区间
    xs = (np.arange(ow) - opx) / k + px
    xe = (np.arange(ow) + 1 - opx) / k + px
    ys = (np.arange(oh) - opy) / k + py
    ye = (np.arange(oh) + 1 - opy) / k + py
    bx = np.floor(xs + 1e-9).astype(np.int64)
    by = np.floor(ys + 1e-9).astype(np.int64)
    votes = np.zeros((oh, ow, P), np.float64)
    cover = np.zeros((oh, ow), np.float64)
    tot = ((xe - xs)[None, :] * (ye - ys)[:, None])
    for dy in range(n):
        yy = by + dy
        oy = np.clip(np.minimum(ye, yy + 1) - np.maximum(ys, yy), 0, None)
        yok = (yy >= 0) & (yy < h)
        yyc = np.clip(yy, 0, h - 1)
        for dx in range(n):
            xx = bx + dx
            ox = np.clip(np.minimum(xe, xx + 1) - np.maximum(xs, xx), 0, None)
            xok = (xx >= 0) & (xx < w)
            xxc = np.clip(xx, 0, w - 1)
            wgt = oy[:, None] * ox[None, :]
            wgt = wgt * (yok[:, None] & xok[None, :])
            ci = idx[yyc[:, None], xxc[None, :]]
            op = ci >= 0
            wgt = wgt * op
            cover += wgt
            if P:
                np.add.at(votes, (np.broadcast_to(np.arange(oh)[:, None], ci.shape)[op],
                                  np.broadcast_to(np.arange(ow)[None, :], ci.shape)[op], ci[op]),
                          (wgt * imp[np.clip(ci, 0, P - 1)])[op])
    out = np.full((oh, ow), -1, np.int32)
    if P:
        best = votes.argmax(axis=2).astype(np.int32)
        keep = cover / tot >= thr
        out[keep] = best[keep]
    return out


def _imp_table(cols):
    if not len(cols):
        return np.ones(0)
    lum = cols[:, 0] * .3 + cols[:, 1] * .59 + cols[:, 2] * .11
    dmin = lum.min()
    return np.where(lum <= dmin + OUTLINE_BAND, OUTLINE_W, 1.0)


def _to_rgba(idx, cols):
    oh, ow = idx.shape
    out = np.zeros((oh, ow, 4), np.uint8)
    m = idx >= 0
    if m.any():
        out[m, :3] = cols[idx[m]]
        out[m, 3] = 255
    return out


def shrink_sheet(sheet, cell, pivot, k=CK, thr=THR):
    """整张图集：每格 cell 宽×高，按行 / 列排布。返回 (新图, 新 cell, 新 pivot)。"""
    rgba = np.array(sheet.convert("RGBA"))
    cw, ch = cell
    px, py = pivot
    ow, oh, opx, opy = _dims(cw, ch, px, py, k)
    cols, idx = _palette(rgba)
    imp = _imp_table(cols)
    nrows, ncols = rgba.shape[0] // ch, rgba.shape[1] // cw
    out = np.zeros((nrows * oh, ncols * ow, 4), np.uint8)
    for r in range(nrows):
        for f in range(ncols):
            sub = idx[r * ch:(r + 1) * ch, f * cw:(f + 1) * cw]
            if (sub >= 0).sum() == 0:
                continue
            o = _shrink_idx(sub, imp, px, py, k, ow, oh, opx, opy, thr)
            out[r * oh:(r + 1) * oh, f * ow:(f + 1) * ow] = _to_rgba(o, cols)
    return Image.fromarray(out, "RGBA"), [ow, oh], [opx, opy]


def shrink_image(img, pivot, k=CK, thr=THR):
    """单张图（道具横向帧条请用 shrink_strip）。返回 (新图, 新 pivot)。"""
    rgba = np.array(img.convert("RGBA"))
    h, w = rgba.shape[:2]
    ow, oh, opx, opy = _dims(w, h, pivot[0], pivot[1], k)
    cols, idx = _palette(rgba)
    o = _shrink_idx(idx, _imp_table(cols), pivot[0], pivot[1], k, ow, oh, opx, opy, thr)
    return Image.fromarray(_to_rgba(o, cols), "RGBA"), [opx, opy]


def shrink_strip(strip, size, pivot, frames, k=CK, thr=THR):
    """道具 / 场景小图的横向帧条：frames 格，每格 size 宽×高。返回 (新图, 新 size, 新 pivot)。"""
    rgba = np.array(strip.convert("RGBA"))
    cw, ch = size
    ow, oh, opx, opy = _dims(cw, ch, pivot[0], pivot[1], k)
    cols, idx = _palette(rgba)
    imp = _imp_table(cols)
    out = np.zeros((oh, frames * ow, 4), np.uint8)
    for f in range(frames):
        sub = idx[:, f * cw:(f + 1) * cw]
        o = _shrink_idx(sub, imp, pivot[0], pivot[1], k, ow, oh, opx, opy, thr)
        out[:, f * ow:(f + 1) * ow] = _to_rgba(o, cols)
    return Image.fromarray(out, "RGBA"), [ow, oh], [opx, opy]
