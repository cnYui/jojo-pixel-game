# 第7章的 UI 图：名牌、替身卡、地点卡、VS 卡的字、大字标题、必杀切入字、「1999年7月」红章。
#   用 p4_ui 现成的画法，元数据写 _meta/ui_ch7.json（不跑 p4_ui.py 的 main：那个会整份重画序章的 UI）。
#   吉良（第6章）、亿泰（第2章）、由花子（第3章）、川尻浩作（第8章画了“川尻浩作？”那张）的名牌归别章，这里不画。
#   用法：python3 第四部/tools/art/p4_ui_ch7.py
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_ui as U  # noqa: E402


def stamp(month):
    """红章：照 p4_ui.map_parts 的画法，只换月份"""
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
    rng = np.random.RandomState(17)
    on = a[..., 3] > 0
    drop = (rng.rand(*on.shape) < .12) & on
    a[drop, 3] = 0
    a[on & ~drop, 3] = 225
    im = Image.fromarray(a, 'RGBA').rotate(-8, resample=Image.NEAREST, expand=True)
    return U.save('map/stamp_199907', im)


def main():
    namecards = {
        'aya': U.namecard('aya', '辻彩', '#c86a96', '灰姑娘美容院的美容师｜能改变一个人的“恋爱运”'),
        'tailor': U.namecard('tailor', '裁缝店老板', '#9a8a60', '杜王町唯一一家做西装的店'),
    }
    standcards = {
        'cinderella': U.standcard('cinderella', '『灰姑娘』', 'CINDERELLA', ('#fff0f6', '#f4b8d0'), '#f4b8d0', '#2a0c1c'),
        'echoes3': U.standcard('echoes3', '『回音 ACT3』', 'ECHOES ACT3', ('#f0fff8', '#7af0b8'), '#1ec080', '#06241a'),
        'sha': U.standcard('sha', '『枯萎穿心攻击』', 'SHEER HEART ATTACK', ('#e8f0ff', '#8cacf0'), '#4a6ad0', '#0a1030'),
        'ph7_killerqueen': U.standcard('ph7_killerqueen', '『杀手皇后』', 'KILLER QUEEN', ('#fff0fa', '#f0a8d8'), '#e080c0', '#240a1e'),
    }
    locations = {
        'salon': U.location('salon', '灰姑娘美容院', 'BEAUTY SALON CINDERELLA · 杜王町'),
        'ch7_cafe': U.location('ch7_cafe', '杜王大酒店旁的咖啡馆', 'MORIOH GRAND HOTEL · 杜王町'),
        'tailor': U.location('tailor', '裁缝店', 'TAILOR SHOP · 杜王町 商店街'),
    }
    vs = {
        'sha': U.vs_card('sha', '枯萎穿心攻击', 'SHEER HEART ATTACK', 'VS ？？？ / 杜王町·裁缝店外',
                         ('#e8f0ff', '#8cacf0', '#3a5ac0'), '#4a6ad0', ['#4a0a14', '#14040a']),
        'kira': U.vs_card('kira', '杀手皇后', 'KILLER QUEEN', 'VS 吉良吉影 / 杜王町·商店街',
                          ('#fff0fa', '#f0a8d8', '#c05a9a'), '#e080c0', ['#4a0a14', '#14040a']),
    }
    titles = {
        'days_later': U.save('title/days_later', U.big('几天后', 30, ('#fff4e0', '#e8c890'), edge='#20140a', edge_w=2)),
        'kira_pov': U.save('title/kira_pov', U.big('——同一时刻', 30, ('#e8ecff', '#a8b4e8'), edge='#0a0a20', edge_w=2)),
        'next_day': U.save('title/next_day', U.big('第二天', 30, ('#fff4e0', '#e8c890'), edge='#20140a', edge_w=2)),
    }
    specials = {
        'koichi_act3': U.save('special/koichi_act3', U.big('3 FREEZE！', 42, ('#f0fff8', '#7af0b8', '#1ec080'),
                                                           edge='#06241a', shadow='#020c08', edge_w=3, shadow_d=(3, 3))),
    }
    U.chapter_ui('ch7', namecards=namecards, standcards=standcards, locations=locations, vs=vs, titles=titles, specials=specials,
                 map={'stamp_199907': stamp('7月')})
    print('第7章 UI：', ' '.join(list(namecards) + list(standcards) + list(locations) + list(vs) + list(titles) + list(specials)))


if __name__ == '__main__':
    main()
