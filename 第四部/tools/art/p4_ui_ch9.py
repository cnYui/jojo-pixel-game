# 第9章的 UI 图：名牌（未起隆、裕也、早人）、替身卡（公路之星）、地点卡、VS 卡、小标题。
#   全部调 p4_ui 的画法，元数据写 _meta/ui_ch9.json（p4_ui.chapter_ui），不跑 p4_ui.py 的 main。
#   用法：python3 第四部/tools/art/p4_ui_ch9.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_ui as U  # noqa: E402


def main():
    namecards = {
        'mikitaka': U.namecard('mikitaka', '支仓未起隆', '#6a7ac0', '自称从麦哲伦星云来的宇宙人｜216 岁'),
        'yuya': U.namecard('yuya', '喷上裕也', '#c0507a', '摩托摔伤住院的高中生｜替身：公路之星'),
        'hayato': U.namecard('hayato', '川尻早人', '#b06a2a', '小学五年级｜最近总觉得爸爸不对劲'),
    }
    standcards = {'highway': U.standcard('highway', '『公路之星』', 'HIGHWAY STAR', ('#ffe4ec', '#ff9cbc'), '#ffb0c8', '#24081a')}
    locations = {
        'rohan9': U.location('rohan9', '岸边露伴宅', 'KISHIBE ROHAN RESIDENCE · 杜王町'),
        'tunnel9': U.location('tunnel9', '国道隧道', 'ROUTE TUNNEL · 杜王町郊外'),
        'hospital9': U.location('hospital9', '杜王综合医院', 'MORIOH GENERAL HOSPITAL'),
        'kawajiri9': U.location('kawajiri9', '川尻家', 'KAWAJIRI RESIDENCE · 杜王町'),
    }
    vs = {
        'dice9': U.vs_card('dice9', '骰子对决', 'CHINCHIRORIN', 'VS 岸边露伴 / 露伴宅·客厅', ('#fff4d8', '#f0c860', '#c08a20'), '#e0b040',
                           ['#5a3a10', '#2a1806']),
        'highway': U.vs_card('highway', '公路之星', 'HIGHWAY STAR', 'VS 喷上裕也 / 杜王综合医院', ('#ffe8f0', '#ff90b8', '#d04a80'), '#f07a9c',
                             ['#7a1a3e', '#2a0814']),
    }
    titles = {
        'days9': U.save('title/days9', U.big('几天后', 30, ('#e8ecff', '#a8b4e8'), edge='#0a0a20', edge_w=2)),
        'interlude9': U.save('title/interlude9', U.big('插曲　阁楼的猫草', 30, ('#fff0d8', '#e0b878'), edge='#1a0a04', edge_w=2)),
    }
    U.chapter_ui('ch9', namecards=namecards, standcards=standcards, locations=locations, vs=vs, titles=titles)
    print('ui_ch9 写好了')


if __name__ == '__main__':
    main()
