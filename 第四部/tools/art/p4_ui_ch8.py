# 第8章的 UI 图：名牌、替身卡、地点卡、VS 卡的字、大字标题。用 p4_ui 现成的画法，元数据写 _meta/ui_ch8.json
#   （不跑 p4_ui.py 的 main：那个会整份重画序章的 UI）。露伴、乔瑟夫的名牌归第5 / 第4章画，这里不画。
#   用法：python3 第四部/tools/art/p4_ui_ch8.py
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_ui as U  # noqa: E402


def stamp(y, m, rel):
    t1 = U.big(y, 14, ('#d82a2a', '#d82a2a'), edge='#d82a2a', shadow=None, edge_w=0)
    t2 = U.big(m, 20, ('#d82a2a', '#d82a2a'), edge='#d82a2a', shadow=None, edge_w=0)
    W = max(t1.width, t2.width) + 14
    H = t1.height + t2.height + 12
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=5, outline=U.LIB.hexc('#d82a2a'), width=2)
    im.alpha_composite(t1, ((W - t1.width) // 2, 5))
    im.alpha_composite(t2, ((W - t2.width) // 2, 6 + t1.height))
    a = np.array(im)
    rng = np.random.RandomState(17)
    on = a[..., 3] > 0
    drop = (rng.rand(*on.shape) < .12) & on
    a[drop, 3] = 0
    a[on & ~drop, 3] = 225
    im = Image.fromarray(a, 'RGBA').rotate(-8, resample=Image.NEAREST, expand=True)
    return U.save(rel, im)


def main():
    namecards = {
        'yoshihiro': U.namecard('yoshihiro', '吉良吉广', '#9a7a5a', '吉良吉影的父亲｜十几年前就去世了'),
        'oyanagi': U.namecard('oyanagi', '大柳贤', '#7a68c8', '小学生｜猜拳从来没输过'),
        'shinobu': U.namecard('shinobu', '川尻忍', '#c86a7a', '川尻浩作的妻子｜对丈夫早就没兴趣了'),
        'kawajiri': U.namecard('kawajiri', '川尻浩作？', '#7a5a9a', '换了一张脸的吉良吉影'),
    }
    standcards = {
        'atomheart': U.standcard('atomheart', '『原子心之父』', 'ATOM HEART FATHER', ('#fff4e0', '#d8b888'), '#c8a070', '#20160c'),
        'boyiiman': U.standcard('boyiiman', '『Boy II Man』', 'BOY II MAN', ('#f0ecff', '#a898ec'), '#9a88e0', '#140c28'),
    }
    locations = {
        'kira_house': U.location('kira_house', '吉良家旧宅', 'THE KIRA HOUSE · 杜王町'),
        'kawajiri': U.location('kawajiri', '川尻家', 'KAWAJIRI RESIDENCE · 杜王町'),
        'station': U.location('station', '杜王站前', 'MORIOH STATION · 杜王町'),
    }
    vs = {
        'atomheart': U.vs_card('atomheart', '原子心之父', 'ATOM HEART FATHER', 'VS 吉良吉广 / 杜王町·吉良家旧宅',
                               ('#fff4e0', '#e0c090', '#a07840'), '#c8a070', ['#5a4a32', '#20180c']),
        'boyiiman': U.vs_card('boyiiman', 'Boy II Man', 'BOY II MAN', 'VS 大柳贤 / 杜王站前',
                              ('#f0ecff', '#a898ec', '#6a58c8'), '#9a88e0', ['#3a2a7a', '#140c30']),
    }
    titles = {
        'kira_life': U.save('title/kira_life', U.big('吉良吉影的新生活', 30, ('#f0e8ff', '#b8a0e0'), edge='#160a24', edge_w=2)),
        'janken': U.save('title/janken', U.big('猜拳小子来了', 30, ('#f0ecff', '#a898ec'), edge='#140c28', edge_w=2)),
        'that_night': U.save('title/that_night', U.big('那天夜里', 30, ('#e8ecff', '#a8b4e8'), edge='#0a0a20', edge_w=2)),
    }
    specials = {'photo8': U.save('special/photo8', U.big('咔嚓！', 42, ('#ffffff', '#e8e0d0', '#b8a888'),
                                                        edge='#2a1a0a', shadow='#12080a', edge_w=3, shadow_d=(3, 3)))}
    # 第8章的日历红章是 7 月（序章那枚是 4 月）：照 p4_ui.map_parts 的画法另画一枚，挂在 map8 下面，本章自己的日历用
    map8 = {'stamp': stamp('1999年', '7月', 'map/stamp_199907')}
    # 拟声字（S.sfxText 用的图）：吉广摔出相框「砰」、川尻家报纸「沙沙」、透明的静「诶嘿」
    sfx = {
        '砰': U.save('sfx/ch8_pon', U.big('砰', 30, ('#fff4e0', '#e0c090', '#a07840'), edge='#20160c', edge_w=3, shadow_d=(2, 2))),
        '沙沙': U.save('sfx/ch8_shasha', U.big('沙沙', 22, ('#f0f0f0', '#c8c8c8'), edge='#202020', edge_w=2)),
        '诶嘿': U.save('sfx/ch8_ehe', U.big('诶嘿', 24, ('#f0f8ff', '#b8dcff', '#80b0e8'), edge='#102040', edge_w=2)),
    }
    U.chapter_ui('ch8', namecards=namecards, standcards=standcards, locations=locations, vs=vs, titles=titles,
                 specials=specials, map8=map8, sfx=sfx)
    print('第8章 UI：', ' '.join(list(namecards) + list(standcards) + list(locations) + list(vs) + list(titles)))


if __name__ == '__main__':
    main()
