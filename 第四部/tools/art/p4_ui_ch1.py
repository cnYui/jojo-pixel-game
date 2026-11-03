# 第1章的 UI：形兆的名牌、坏公司的替身卡、地点卡「虹村家」、两张 VS 卡的字、标题字「十年前」。
#   全部调 p4_ui 的画法函数，写 _meta/ui_ch1.json（不跑 p4_ui.py 的 main，它会整份重画序章的 UI）。
#   亿泰的名牌、轰炸空间的替身卡归第2章（第四部/docs/分章开发约定.md）。
#   用法：python3 第四部/tools/art/p4_ui_ch1.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_ui as U  # noqa: E402


def main():
    nc = {'keicho': U.namecard('keicho', '虹村形兆', '#c0a040', '亿泰的哥哥｜手里有一张弓和一支箭')}
    sc = {'badcompany': U.standcard('badcompany', '『坏公司』', 'BAD COMPANY', ('#f0f6dc', '#b8cc78'), '#c8d890', '#141c08')}
    loc = {'nijimura': U.location('nijimura', '虹村家', 'NIJIMURA RESIDENCE · 杜王町')}
    vs = {
        'thehand': U.vs_card('thehand', '轰炸空间', 'THE HAND', 'VS 虹村亿泰 / 杜王町·虹村家前院', ('#f0f4ff', '#9ab0e8', '#4a64b8'), '#5a78d8',
                             ['#1a2a6a', '#0a1238']),
        'badcompany': U.vs_card('badcompany', '坏公司', 'BAD COMPANY', 'VS 虹村形兆 / 虹村家·一楼走廊', ('#f4f8e0', '#c0d080', '#6a8a30'), '#8aa040',
                                ['#2a3a10', '#101806']),
    }
    titles = {
        'ch1_past': U.save('title/ch1_past', U.big('十年前', 30, ('#e8f0e0', '#a0b898'), edge='#0a140a', edge_w=2)),
        'ch1_home': U.save('title/ch1_home', U.big('那天傍晚', 30, ('#ffe8d0', '#e0a878'), edge='#1a0a04', edge_w=2)),
    }
    U.chapter_ui('ch1', namecards=nc, standcards=sc, locations=loc, vs=vs, titles=titles)
    print('UI：名牌 keicho、替身卡 badcompany、地点 nijimura、VS thehand / badcompany、标题 2 张')


if __name__ == '__main__':
    main()
