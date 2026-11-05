# 第11章的 UI 图：名牌、替身卡、地点卡、VS 卡的字、过场标题、日历红章「1999年7月」。
#   用 p4_ui 的 namecard / standcard / location / vs_card / big 画，元数据写 _meta/ui_ch11.json（不跑 p4_ui.py 的 main）。
#   ph11_* 的名牌是给临时占位人物用的：正式的早人、露伴等由他们第一次出场的那章画名牌。
#   用法：python3 第四部/tools/art/p4_ui_ch11.py
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_ui as U  # noqa: E402


def stamp(month):
    """日历地图的红章（照 p4_ui.map_parts 的画法，只换月份）"""
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
    rng = np.random.RandomState(11)
    on = a[..., 3] > 0
    drop = (rng.rand(*on.shape) < .12) & on
    a[drop, 3] = 0
    a[on & ~drop, 3] = 225
    im = Image.fromarray(a, 'RGBA').rotate(-8, resample=Image.NEAREST, expand=True)
    return U.save('map/stamp_199907', im)


def title(key, text, fill=('#e8ecff', '#a8b4e8'), edge='#0a0a20'):
    return U.save('title/' + key, U.big(text, 30, fill, edge=edge, edge_w=2))


def main():
    namecards = {
        'kinoto': U.namecard('kinoto', '乙雅三', '#b8704e', '建筑师 · 来修露伴家的房子｜不让人看他的背'),
        'ph11_hayato': U.namecard('ph11_hayato', '川尻早人', '#c8682e', '杜王町的小学五年级生｜爸爸好像变了个人'),
        'ph11_rohan': U.namecard('ph11_rohan', '岸边露伴', '#3e8a62', '漫画家｜替身：天堂之门'),
        'ph11_kosaku': U.namecard('ph11_kosaku', '川尻浩作', '#7a5a9a', '早人的爸爸……？'),
        'ph11_reimi': U.namecard('ph11_reimi', '杉本铃美', '#d080a0', '幽灵小路里的女孩｜十五年前的事她还记得'),
    }
    standcards = {
        'cheaptrick': U.standcard('cheaptrick', '『Cheap Trick』', 'CHEAP TRICK', ('#f0ecff', '#b8acd8'), '#c8c0e8', '#120c22'),
        'btd': U.standcard('btd', '『败者食尘』', 'BITES THE DUST', ('#fff0f6', '#e898c0'), '#f8c0dc', '#1c0812'),
        'ph11_killerq': U.standcard('ph11_killerq', '『杀手皇后』', 'KILLER QUEEN', ('#fff0f6', '#e898c0'), '#f8c0dc', '#1c0812'),
    }
    locations = {
        'kawajiri': U.location('kawajiri', '川尻家', 'KAWAJIRI RESIDENCE · 杜王町'),
        'rohanhouse': U.location('rohanhouse', '露伴宅', 'ROHAN KISHIBE · 杜王町 住宅区'),
        'alley11': U.location('alley11', '幽灵小路', 'GHOST ALLEY · 杜王町'),
        'corner11': U.location('corner11', '早上的街口', 'MORNING · 杜王町 住宅区'),
    }
    vs = {'cheaptrick': U.vs_card('cheaptrick', 'Cheap Trick', 'CHEAP TRICK', 'VS 乙雅三 / 杜王町·露伴宅',
                                  ('#f0ecff', '#b8acd8', '#7a6aa8'), '#9a88d0', ['#3a2a6a', '#140c2a'])}
    titles = {
        'c11_night': title('c11_night', '那天夜里'),
        'c11_loop1': title('c11_loop1', '第二天早上　7:00', ('#fff4e0', '#f0c890'), '#2a1408'),
        'c11_loop2': title('c11_loop2', '……又是 7:00', ('#fff4e0', '#f0c890'), '#2a1408'),
        'c11_loop3': title('c11_loop3', '第三次的 7:00', ('#fff4e0', '#f0c890'), '#2a1408'),
        'c11_loop4': title('c11_loop4', '最后一次的 7:00', ('#fff0f0', '#f0a0a0'), '#2a0808'),
    }
    # 拟声字（S.sfxText 用）：天堂之门、手表挡住空气弹的「叮」、幽灵小路里背后的人声（淡紫、小一号）
    sfx = {
        '天堂之门': U.save('sfx/c11_hd', U.big('天堂之门！', 26, ('#fff8e0', '#f0d070', '#c89a30'), edge='#2a1a04', edge_w=3)),
        '叮': U.save('sfx/c11_ding', U.big('叮！', 28, ('#ffffff', '#d8e8ff', '#90a8d0'), edge='#101828', edge_w=3)),
    }
    for i, v in enumerate(['露伴老师——', '掉东西了哦——', '岸边先生？', '回头看看嘛……', '你的速写本……']):
        sfx[v] = U.save('sfx/c11_voice%d' % i, U.big(v, 16, ('#f0e8ff', '#b8a8e0'), edge='#140c22', edge_w=2))
    LIB.save_json(os.path.join(LIB.META, 'ui_ch11.json'), {})
    U.chapter_ui('ch11', namecards=namecards, standcards=standcards, locations=locations, vs=vs, titles=titles,
                 map={'stamp_ch11': stamp('7月')}, sfx=sfx)
    print('第11章 UI：名牌', len(namecards), '替身卡', len(standcards), '地点卡', len(locations), '标题', len(titles))


if __name__ == '__main__':
    main()
