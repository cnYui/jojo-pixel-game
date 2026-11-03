# 终章的 UI 图：名牌、替身卡、VS 卡「杀手皇后 + 猫草」（黑红底）、两枚红章（7月16日 / 夏末）、小卡标题。
#   全部调 p4_ui 现成的画法，只写本章的 _meta/ui_final.json（不跑 p4_ui.py 的 main，那会整份重画序章的 UI）。
#   用法：python3 第四部/tools/art/p4_ui_final.py
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_ui as U  # noqa: E402


def stamp(key, line1, line2, size2=20):
    """红章：和序章「1999年4月」同一个画法（圆角方框、两行字、故意没盖实）"""
    t1 = U.big(line1, 14, ('#d82a2a', '#d82a2a'), edge='#d82a2a', shadow=None, edge_w=0)
    t2 = U.big(line2, size2, ('#d82a2a', '#d82a2a'), edge='#d82a2a', shadow=None, edge_w=0)
    W = max(t1.width, t2.width) + 14
    H = t1.height + t2.height + 12
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=5, outline=LIB.hexc('#d82a2a'), width=2)
    im.alpha_composite(t1, ((W - t1.width) // 2, 5))
    im.alpha_composite(t2, ((W - t2.width) // 2, 6 + t1.height))
    a = np.array(im)
    rng = np.random.RandomState(len(key) * 7 + 3)
    on = a[..., 3] > 0
    drop = (rng.rand(*on.shape) < .12) & on
    a[drop, 3] = 0
    a[on & ~drop, 3] = 225
    im = Image.fromarray(a, 'RGBA').rotate(-8, resample=Image.NEAREST, expand=True)
    return U.save('map/' + key, im)


def main():
    namecards = {
        'fin_kira': U.namecard('fin_kira', '吉良吉影', '#a070c0', '杀人魔｜现在顶着川尻浩作的脸'),
        'fin_okuyasu': U.namecard('fin_okuyasu', '虹村亿泰', '#3a5ab0', '仗助的同学｜脑子不好使，讲义气'),
        'fin_hayato': U.namecard('fin_hayato', '川尻早人', '#c8742c', '小学五年级｜知道“爸爸”是谁的孩子'),
        'fin_rohan': U.namecard('fin_rohan', '岸边露伴', '#3a8a5a', '漫画家｜今天早上本该死在家门口'),
        'fin_reimi': U.namecard('fin_reimi', '杉本铃美', '#e070a0', '幽灵小路的幽灵｜等了十五年'),
        'paramedic': U.namecard('paramedic', '女急救员', '#5a74a8', '杜王町消防署｜第一个赶到的人'),
    }
    standcards = {
        'fin_kq': U.standcard('fin_kq', '『杀手皇后』', 'KILLER QUEEN', ('#ffe4ee', '#f08cb4'), '#e080b0', '#1a0610'),
        'fin_straycat': U.standcard('fin_straycat', '『猫草』', 'STRAY CAT', ('#f4ffe0', '#9ae070'), '#7ac860', '#0a1a08'),
        'fin_echoes3': U.standcard('fin_echoes3', '『回音 ACT3』', 'ECHOES ACT3', ('#e8fff0', '#70e0a8'), '#40d890', '#06180e'),
        'fin_thehand': U.standcard('fin_thehand', '『轰炸空间』', 'THE HAND', ('#f0f8ff', '#8ab0ff'), '#8ab0ff', '#0a1230'),
    }
    vs = {'kq_final': U.vs_card('kq_final', '杀手皇后 + 猫草', 'KILLER QUEEN & STRAY CAT', 'VS 吉良吉影 / 杜王町·住宅区',
                                ('#ffe8f0', '#f08cb4', '#c04a7a'), '#c02a3a', ['#3a0810', '#0a0204'])}
    maps = {'stamp_0716': stamp('stamp_19990716', '1999年', '7月16日', 18), 'stamp_late': stamp('stamp_1999late', '1999年', '夏末')}
    titles = {
        'fin_late': U.save('title/fin_late', U.big('1999年 夏末', 30, ('#fff4d6', '#f0c890'), edge='#20100a', edge_w=2)),
        'fin_end': U.save('title/fin_end', U.big('完', 64, ('#fff4d6', '#ffd040', '#f0902a'), edge='#20100a', edge_w=3)),
    }
    meta = U.chapter_ui('final', namecards=namecards, standcards=standcards, vs=vs, map=maps, titles=titles)
    print('UI：', {k: list(v) for k, v in meta.items()})


if __name__ == '__main__':
    main()
