"""art_enemies -- 已有敌人补帧（技术约定 §5.2；报告 08 §2.5 / §6.4）。

M1 不需要给已有敌人补帧：序1 阿布德尔、序2 花京院、第 2 战波鲁纳雷夫用的是主角团自己的图集，
灰塔的 `towergray.needle` 按 §3.14 A 写在 art_stands.py。本模块先放好“只有 idle 的小怪”兜底用的
自动后处理（报告 08 §6.4：auto_hurt / auto_lunge / auto_down），后面章节补 hurt / 倒地时直接调用：

    from art_enemies import auto_hurt, auto_down
    sprite.define('holhorse.hurt', [auto_hurt(sprite.get('holhorse.idle').frames[0])], anchor='mb', ...)

规则：BOSS 的倒地 / 败北要手画或用运行时演出（报告 08 §6.4：自动倒地偏厚）。
"""
import sys
sys.dont_write_bytecode = True
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art_common as AC                       # noqa: E402

import numpy as np                            # noqa: E402
from PIL import Image                         # noqa: E402

NEW = []          # M1 没有新注册的精灵
ONESHOT = set()
STATIC_STATES = set()
CHAR_INFO = {}


def _shear_body(im, k, hip_frac=0.68):
    """髋线（默认 0.68×高）以上按行平移 round(k*(hip-y))，脚下不动；去描边 → 剪切 → 重新描边。"""
    base = AC.strip_outline(im)
    a = np.array(base)
    h, w = a.shape[:2]
    hip = int(h * hip_frac)
    ext = int(abs(k) * hip) + 2
    out = np.zeros((h, w + 2 * ext, 4), np.uint8)
    for y in range(h):
        d = int(round(k * (hip - y))) if y < hip else 0
        out[y, ext + d:ext + d + w] = a[y]
    res = AC.add_outline(Image.fromarray(out, 'RGBA'))
    # 裁回原宽（以原中线为轴），保证锚点 'mb' 不变
    return res.crop((ext, 0, ext + w, h)) if res.getbbox() and _fits(res, ext, w) else res


def _fits(im, ext, w):
    bb = im.getbbox()
    return bb[0] >= ext and bb[2] <= ext + w


def auto_hurt(im, k=-0.30):
    """后仰受击（s13_vanilla._van_hurt 的配方）。"""
    return _shear_body(im, k)


def auto_lunge(im, k=0.18):
    """前倾（攻击预兆）。"""
    return _shear_body(im, k)


def auto_down(im):
    """逆时针转 90°（头朝左）+ 重新描边；只适合小怪（报告 08 §6.4）。"""
    base = AC.strip_outline(im)
    rot = base.transpose(Image.ROTATE_90)
    return AC.add_outline(AC.crop_alpha(rot), pad=1)
