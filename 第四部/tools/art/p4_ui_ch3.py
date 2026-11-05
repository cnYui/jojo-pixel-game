# 第3章的 UI：名牌（由花子、东尼欧）、替身卡（爱的豪华、回音 ACT2、珍珠果酱）、地点卡（海边别墅、意大利餐厅）、
#   VS 卡（lovedeluxe）、日历地图的红章「1999年5月」。写 _meta/ui_ch3.json（build_p4.py 深合并进 ui）。
#   红章不能盖掉序章的 ui.map.stamp（那是四月的），放在 ui.map_ch3 下面，第3章的日历自己读。
#   用法：python3 第四部/tools/art/p4_ui_ch3.py
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_ui as U  # noqa: E402


def stamp(month):
    """和序章同样画法的红章（圆角方框 + 两行字 + 故意没盖实），只换月份"""
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
    im = Image.fromarray(a, 'RGBA').rotate(-6, resample=Image.NEAREST, expand=True)
    return U.save('map/stamp_199905', im)


def main():
    namecards = {
        'yukako': U.namecard('yukako', '山岸由花子', '#8a5ac0', '葡萄丘高中一年级｜认定了康一'),
        'tonio': U.namecard('tonio', '东尼欧·特拉萨迪', '#c05a3a', '意大利餐厅的厨师｜客人的身体他一摸就知道'),
    }
    standcards = {
        'lovedeluxe': U.standcard('lovedeluxe', '『爱的豪华』', 'LOVE DELUXE', ('#f4e8ff', '#c8a0f0'), '#b890e8', '#1a0c2a'),
        'echoes2': U.standcard('echoes2', '『回音 ACT2』', 'ECHOES ACT2', ('#f4ffd8', '#c8e070'), '#c0d870', '#141c08'),
        'pearljam': U.standcard('pearljam', '『珍珠果酱』', 'PEARL JAM', ('#fff0dc', '#ffb070'), '#ffb878', '#2a1408'),
    }
    locations = {
        'villa': U.location('villa', '海边别墅', 'SEASIDE VILLA · 杜王町'),
        'trattoria': U.location('trattoria', '意大利餐厅', 'TRATTORIA · 杜王町'),
    }
    vs = {'lovedeluxe': U.vs_card('lovedeluxe', '爱的豪华', 'LOVE DELUXE', 'VS 山岸由花子 / 杜王町·海边别墅',
                                  ('#f8eeff', '#c8a0f0', '#8a5ac0'), '#a070e0', ['#4a2a7a', '#1a0c34'])}
    map_ch3 = {'stamp': stamp('5月')}
    U.chapter_ui('ch3', namecards=namecards, standcards=standcards, locations=locations, vs=vs, map_ch3=map_ch3)
    print('第3章 UI：', ' '.join(list(namecards) + list(standcards) + list(locations) + list(vs) + ['stamp_199905']))


if __name__ == '__main__':
    main()
