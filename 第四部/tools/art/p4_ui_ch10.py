# 第10章的 UI 字图：名牌（丰大、辉之辅、未起隆和裕也的临时版）、替身卡（Superfly、谜、地球风与火、公路之星）、
#   地点卡（送电铁塔、宫本的屋子、杜王町图书馆）、VS 卡（丰大、辉之辅）、日历地图的红章「1999年7月」和右上地点小字。
#   日历的红章在 ui.map 里只有序章那一枚（4 月），各章不能改 ui.map（会把序章也换掉），所以本章的放在 ui.map_ch10。
#   未起隆、裕也的名牌和替身卡也带 _tmp：第9章的正式版合进来以后剧情会优先用正式 cid 的。
#   用法：python3 第四部/tools/art/p4_ui_ch10.py → assets/ui/**、assets/_meta/ui_ch10.json（不要跑 p4_ui.py 的 main）
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_ui as U  # noqa: E402


def stamp(month):
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
    rng = np.random.RandomState(10)
    on = a[..., 3] > 0
    drop = (rng.rand(*on.shape) < .12) & on
    a[drop, 3] = 0
    a[on & ~drop, 3] = 225
    return Image.fromarray(a, 'RGBA').rotate(-8, resample=Image.NEAREST, expand=True)


def main():
    namecards = {
        'toyohiro': U.namecard('toyohiro', '钢田一丰大', '#4ea050', '住在送电铁塔上的男人'),
        'terunosuke': U.namecard('terunosuke', '宫本辉之辅', '#b07a3c', '收集“害怕的样子”的少年'),
        'mikitaka_tmp': U.namecard('mikitaka_tmp', '支仓未起隆', '#4a6ab0', '自称宇宙人，什么都能变'),
        'yuya_tmp': U.namecard('yuya_tmp', '喷上裕也', '#c04a80', '鼻子比谁都灵的飙车族'),
    }
    standcards = {
        'superfly': U.standcard('superfly', '『Superfly』', 'SUPERFLY', ('#e8ffe4', '#8cd88c'), '#7cc870', '#0a1a0c'),
        'enigma': U.standcard('enigma', '『谜』', 'ENIGMA', ('#fffaf0', '#e0d0b0'), '#d8b878', '#1a120a'),
        'earthwind_tmp': U.standcard('earthwind_tmp', '『地球风与火』', 'EARTH WIND AND FIRE', ('#e4f6ff', '#a0e0e0'), '#a0e0e0', '#081a2a'),
        'highway_tmp': U.standcard('highway_tmp', '『公路之星』', 'HIGHWAY STAR', ('#ffe4f0', '#ff8cbc'), '#ff70a0', '#24081a'),
    }
    locations = {
        'tower': U.location('tower', '郊外的送电铁塔', 'POWER TOWER · 杜王町郊外'),
        'miyamoto': U.location('miyamoto', '宫本的屋子', 'MIYAMOTO\'S ROOM · 杜王町'),
        'library': U.location('library', '杜王町图书馆', 'MORIOH LIBRARY · 几天后'),
    }
    vs = {
        'superfly': U.vs_card('superfly', 'Superfly', 'SUPERFLY', 'VS 钢田一丰大 / 杜王町·送电铁塔', ('#f0fff0', '#8cd88c', '#3a8a3a'),
                              '#4ea050', ['#1e5a2a', '#0a2a12']),
        'enigma': U.vs_card('enigma', '谜', 'ENIGMA', 'VS 宫本辉之辅 / 杜王町·宫本的屋子', ('#fffaf0', '#e8d4a8', '#b08a4a'),
                            '#d8b878', ['#5a3a1a', '#24140a']),
    }
    mp = {'stamp': U.save('map/stamp_199907', stamp('7月')),
          'place': U.save('map/place_ch10', U.small('杜王町 郊外', color='#5a4a34', edge='#f4ead2'))}
    # 拟声字（S.sfxText / 招式的 word 都查 ui.sfx 里的字图）：金属声灰绿、谜的纸白黄、公路之星粉、喊声红
    W = {
        '锵': 'm', '锵！': 'm', '锵！！': 'm', '咔咔咔': 'm', '融进铁架': 'm', '弹回来了！': 'm', '砰！': 'm', '磁铁！': 'c', '嘀嘀——': 'c',
        '嗡——': 'c', '火！': 'r', '蝎子！': 'p', '电！': 'p', '唰': 'p', '嗅': 'h', '吸养分': 'h', '咚': 'h', '咚！': 'h', '咚!!': 'h',
        'DORARARA': 'd', '（咬住嘴唇）': 's', '（抓住书包带）': 's',
    }
    COL = {'m': (('#f4fff0', '#a8d8a0', '#5a8a5a'), '#0a1a0c'), 'c': (('#f0ffff', '#a0e0e0', '#4aa0b0'), '#081a2a'),
           'r': (('#fff4c0', '#ffa040', '#e04a1a'), '#2a0a04'), 'p': (('#fffaf0', '#f0e0b0', '#c0a060'), '#1a120a'),
           'h': (('#ffe8f4', '#ff9ccc', '#e05aa0'), '#2a0a34'), 'd': (('#ffe8f4', '#ff9ccc', '#e05aa0'), '#2a0a34'),
           's': (('#ffffff', '#e0e0f0'), '#1a1a2a')}
    sfx = {}
    for i, (w, k) in enumerate(W.items()):
        cols, edge = COL[k]
        size = 14 if k == 's' else 22 if len(w) >= 4 else 28
        sfx[w] = U.save('sfx/ch10_%02d' % i, U.big(w, size, cols, edge=edge, shadow='#12041a', edge_w=3, shadow_d=(2, 2)))
    U.chapter_ui('ch10', sfx=sfx, namecards=namecards, standcards=standcards, locations=locations, vs=vs, map_ch10=mp)
    print('第10章 UI：名牌', list(namecards), '替身卡', list(standcards), '地点', list(locations), 'VS', list(vs))


if __name__ == '__main__':
    main()
