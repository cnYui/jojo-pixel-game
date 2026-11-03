# 第四部第5章的 UI：露伴的名牌、天堂之门 / Ratt 的替身卡、露伴宅 / 牧场的地点卡、两张 VS 卡、两张小卡。
#   用法：python3 第四部/tools/art/p4_ui_ch5.py      输出 第四部/assets/ui/** + _meta/ui_ch5.json（build_p4.py 深合并进 ui）
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_ui as U  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

LIB = U.LIB


def stamp(month):
    """日历地图的红章（照 p4_ui.map_parts 的画法，换月份）"""
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
    rng = np.random.RandomState(15)
    on = a[..., 3] > 0
    drop = (rng.rand(*on.shape) < .12) & on
    a[drop, 3] = 0
    a[on & ~drop, 3] = 225
    im = Image.fromarray(a, 'RGBA').rotate(-8, resample=Image.NEAREST, expand=True)
    return im


def main():
    namecards = {
        'rohan': U.namecard('rohan', '岸边露伴', '#3a8a5a', '漫画家｜替身：天堂之门'),
    }
    standcards = {
        'heavensdoor': U.standcard('heavensdoor', '『天堂之门』', "HEAVEN'S DOOR", ('#fff6dc', '#f0d070'), '#f0d070', '#1a1408'),
        'ratt': U.standcard('ratt', '『Ratt』', 'RATT', ('#f4e8f0', '#d8a0c8'), '#c890b8', '#1a0a18'),
    }
    locations = {
        'rohan_house': U.location('rohan_house', '露伴宅', 'ROHAN KISHIBE · 杜王町'),
        'farm': U.location('farm', '杜王町郊外·牧场', 'FARM · MORIOH OUTSKIRTS'),
    }
    vs = {
        'heavensdoor': U.vs_card('heavensdoor', '天堂之门', "HEAVEN'S DOOR", 'VS 岸边露伴 / 露伴宅·工作室', ('#fff8e4', '#f0d070', '#c09a30'),
                                 '#f0d070', ['#4a3a10', '#1a1206']),
        'ratt': U.vs_card('ratt', 'Ratt', 'RATT', 'VS 老鼠 / 杜王町郊外·牧场', ('#fbeef6', '#d8a0c8', '#a0608a'), '#c890b8',
                          ['#4a1a3a', '#1a0814']),
    }
    titles = {
        'next_day': U.save('title/next_day', U.big('第二天', 30, ('#fff4e0', '#e8c890'), edge='#1a1006', edge_w=2)),
        'days_later': U.save('title/days_later', U.big('几天后', 30, ('#f0f8e8', '#b0d098'), edge='#0a140a', edge_w=2)),
        'snow_memory': U.save('title/snow_memory', U.big('那年冬天，大雪', 30, ('#f4f8ff', '#b8c8e8'), edge='#0a0e1a', edge_w=2)),
    }
    # 这一章用到的拟声字（墨水金、纸白、溶解的粉紫）
    gold, paper, melt = ('#fff6dc', '#f0d070', '#c09a30'), ('#ffffff', '#e8e0d0'), ('#fbeef6', '#d8a0c8', '#a0608a')
    words = {'叮': paper, '锵': paper, '锵！': paper, '唰': gold, '唰！': gold, '啪啦': paper, '啪啦啪啦': paper,
             '天堂之门！': gold, '滋……': melt}
    sfx = {}
    for i, (w, col) in enumerate(words.items()):
        im = U.big(w, 26, col, edge='#1a0a24', shadow='#0a0412', edge_w=2, shadow_d=(2, 2))
        sfx[w] = U.save('sfx/ch5_%d' % i, im)
    mp = {'stamp_ch5': U.save('map/stamp_199906', stamp('6月'))}
    U.chapter_ui('ch5', map=mp, namecards=namecards, standcards=standcards, locations=locations, vs=vs, titles=titles, sfx=sfx)
    print('ui_ch5：', len(namecards), len(standcards), len(locations), len(vs), len(titles))


if __name__ == '__main__':
    main()
