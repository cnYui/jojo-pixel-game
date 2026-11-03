# 第6章的 UI 字：名牌、替身卡、地点卡、VS 卡、小卡（第四部/docs/第6章_开发脚本.md §4）。
#   全部调 p4_ui 现成的画法，写 assets/_meta/ui_ch6.json（不跑 p4_ui.py 的 main：那个会整份重画序章的 UI）。
#   用法：python3 第四部/tools/art/p4_ui_ch6.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import p4lib as LIB  # noqa: E402
import p4_ui as U  # noqa: E402


def stamp(month):
    # 和 p4_ui.map_parts 的 1999年4月 红章同一个画法，只换月份
    t1 = U.big('1999年', 14, ('#d82a2a', '#d82a2a'), edge='#d82a2a', shadow=None, edge_w=0)
    t2 = U.big(month, 20, ('#d82a2a', '#d82a2a'), edge='#d82a2a', shadow=None, edge_w=0)
    W = max(t1.width, t2.width) + 14
    H = t1.height + t2.height + 12
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=5, outline=LIB.hexc('#d82a2a'), width=2)
    im.alpha_composite(t1, ((W - t1.width) // 2, 5))
    im.alpha_composite(t2, ((W - t2.width) // 2, 6 + t1.height))
    a = np.array(im)
    rng = np.random.RandomState(9)
    on = a[..., 3] > 0
    drop = (rng.rand(*on.shape) < .12) & on
    a[drop, 3] = 0
    a[on & ~drop, 3] = 225
    return Image.fromarray(a, 'RGBA').rotate(-8, resample=Image.NEAREST, expand=True)


def main():
    namecards = {
        'shigechi': U.namecard('shigechi', '矢安宫重清', '#5a9a3a', '葡萄丘中学一年级｜替身：丰收'),
        'reimi': U.namecard('reimi', '杉本铃美', '#d870a0', '幽灵小路的少女｜十五年前遇害'),
        'kira': U.namecard('kira', '吉良吉影', '#8c76b8', '33 岁｜龟友连锁店职员｜只想安静地生活'),
    }
    standcards = {
        'harvest': U.standcard('harvest', '『丰收』', 'HARVEST', ('#fff6c0', '#ffd83c'), '#ffe070', '#2a1e06'),
        'killerqueen': U.standcard('killerqueen', '『杀手皇后』', 'KILLER QUEEN', ('#fff0f4', '#f2a8c4'), '#f2c4d2', '#24081c'),
    }
    locations = {
        'ghost_alley': U.location('ghost_alley', '幽灵小路', 'GHOST ALLEY · 杜王町'),
        'bank': U.location('bank', '葡萄丘银行', 'BUDOUGAOKA BANK · 杜王町'),
        'jhs': U.location('jhs', '葡萄丘中学', 'BUDOUGAOKA JUNIOR HIGH · 杜王町'),
    }
    vs = {
        'harvest': U.vs_card('harvest', '丰收', 'HARVEST', 'VS 矢安宫重清 / 杜王町·大楼外墙', ('#fff6c0', '#ffd83c', '#c89a20'), '#e0b030',
                             ['#6a4a10', '#2a1e06']),
        'killerqueen': U.vs_card('killerqueen', '杀手皇后', 'KILLER QUEEN', 'VS 吉良吉影 / 葡萄丘中学', ('#fff0f4', '#f2a8c4', '#c86a96'),
                                 '#d870a0', ['#4c2a5a', '#1a0a20']),
    }
    titles = {
        'days_later': U.save('title/days_later', U.big('几天后', 30, ('#fff4d6', '#f0c870'), edge='#2a1a0a', edge_w=2)),
        'one_noon': U.save('title/one_noon', U.big('某个中午', 30, ('#fff4d6', '#f0c870'), edge='#2a1a0a', edge_w=2)),
        'kira_pov': U.save('title/kira_pov', U.big('吉良视角', 24, ('#f0e4ff', '#b8a0e0'), edge='#1a0a24', edge_w=2)),
        'three_days': U.save('title/three_days', U.big('三天后', 30, ('#fff4d6', '#f0c870'), edge='#2a1a0a', edge_w=2)),
    }
    mp = {'stamp_199906': U.save('map/stamp_199906', stamp('6月'))}
    U.chapter_ui('ch6', map=mp, namecards=namecards, standcards=standcards, locations=locations, vs=vs, titles=titles)
    print('第6章 UI：名牌', len(namecards), '替身卡', len(standcards), '地点卡', len(locations), 'VS', len(vs), '小卡', len(titles))


if __name__ == '__main__':
    main()
