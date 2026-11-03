# 第4章的 UI 卡片（第四部/docs/第4章_开发脚本.md §4）：名牌、替身卡、地点卡、VS 卡、过场字。
#   只写 assets/_meta/ui_ch4.json（build_p4.py 深合并进 ui），不跑 p4_ui.main。
#   用法：python3 第四部/tools/art/p4_ui_ch4.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_ui as U  # noqa: E402


def main():
    namecards = {
        'otoishi': U.namecard('otoishi', '音石明', '#e07a2a', '19 岁 · 自称天才吉他手｜替身：辣妹'),
        'joseph_old': U.namecard('joseph_old', '乔瑟夫·乔斯达', '#8a2a3a', '79 岁 · 仗助的亲生父亲｜替身：隐者之紫'),
        'shizuka': U.namecard('shizuka', '静·乔斯达', '#c080ff', '捡来的婴儿｜会让自己和碰到的东西透明'),
    }
    standcards = {
        'rhcp': U.standcard('rhcp', '『辣妹』', 'RED HOT CHILI PEPPER', ('#fff8c0', '#ffd040'), '#ffd040', '#2a1a04'),
        'hermit': U.standcard('hermit', '『隐者之紫』', 'HERMIT PURPLE', ('#f4e4ff', '#c080ff'), '#b070f0', '#1a0828'),
        'achtung': U.standcard('achtung', '『透明宝宝』', 'ACHTUNG BABY', ('#ffffff', '#d8c8ff'), '#c8b8f8', '#140c24'),
    }
    locations = {
        'field': U.location('field', '郊外的空地', 'OPEN FIELD · 杜王町郊外'),
        'harbor': U.location('harbor', '杜王港', 'MORIOH PORT · 杜王町'),
        'ship': U.location('ship', 'SPW 财团的船', 'SPEEDWAGON FOUNDATION · 杜王港外'),
        'park': U.location('park', '杜王町公园', 'MORIOH PARK · 池塘边'),
    }
    vs = {
        'rhcp': U.vs_card('rhcp', '辣妹', 'RED HOT CHILI PEPPER', 'VS 音石明 / 杜王港', ('#fff8d0', '#ffd040', '#e09020'),
                          '#ffc020', ['#8a5a0a', '#2a1804']),
    }
    titles = {
        'days_later': U.save('title/days_later', U.big('几天后', 30, ('#fff4e0', '#f0c890'), edge='#20140a', edge_w=2)),
        'night_tv': U.save('title/night_tv', U.big('那天深夜', 30, ('#e8ecff', '#a8b4e8'), edge='#0a0a20', edge_w=2)),
        # 引擎的 Boss 收尾演出（combat.bossFinish）找 ui.titles.saiki：第四部第一次用到，在这里补（照第三部的「再起不能」）
        'saiki': U.save('title/saiki', U.big('再起不能', 44, ('#fff4c0', '#ffd040', '#f0902a'), edge='#3a0a0a', shadow='#12041a', edge_w=3,
                                             shadow_d=(3, 3))),
    }
    # 拟声字（S.sfxText 用；金黄 = 辣妹的电，蓝 = 水，白 = 其他）
    words = [('削', 30, ('#e8f0ff', '#8cb6ff', '#3462d0')), ('1/3', 24, ('#e8f0ff', '#8cb6ff', '#3462d0')),
             ('2/3', 24, ('#e8f0ff', '#8cb6ff', '#3462d0')), ('3/3', 26, ('#e8f0ff', '#8cb6ff', '#3462d0')),
             ('咔', 28, ('#ffffff', '#e0e0e8', '#a0a0b0')), ('×1.5', 22, ('#fff8c0', '#ffd040', '#e09020')),
             ('电力回满！', 24, ('#fff8c0', '#ffd040', '#e09020')), ('夹住了！', 26, ('#ffffff', '#f0e0c0', '#c0a070')),
             ('砰！', 32, ('#fff4e0', '#ffb060', '#e05a20')), ('哇——', 24, ('#ffffff', '#ffe0f0', '#e0a0c0')),
             ('啊嚏！', 24, ('#ffffff', '#ffe0f0', '#e0a0c0')), ('扑通', 28, ('#e8f8ff', '#7ccaf4', '#3a8ac8'))]
    sfx = {w: U.save('sfx/ch4_%d' % i, U.big(w, size, fill, edge='#130b20', shadow='#0a0412', edge_w=2, shadow_d=(2, 2)))
           for i, (w, size, fill) in enumerate(words)}
    U.chapter_ui('ch4', namecards=namecards, standcards=standcards, locations=locations, vs=vs, titles=titles, sfx=sfx)
    print('第4章 UI：', len(namecards), len(standcards), len(locations), len(vs), len(titles))


if __name__ == '__main__':
    main()
