# 第8章的 UI 图：名牌、替身卡、地点卡、VS 卡的字、大字标题。用 p4_ui 现成的画法，元数据写 _meta/ui_ch8.json
#   （不跑 p4_ui.py 的 main：那个会整份重画序章的 UI）。露伴、乔瑟夫的名牌归第5 / 第4章画，这里不画。
#   用法：python3 第四部/tools/art/p4_ui_ch8.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_ui as U  # noqa: E402


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
    U.chapter_ui('ch8', namecards=namecards, standcards=standcards, locations=locations, vs=vs, titles=titles)
    print('第8章 UI：', ' '.join(list(namecards) + list(standcards) + list(locations) + list(vs) + list(titles)))


if __name__ == '__main__':
    main()
