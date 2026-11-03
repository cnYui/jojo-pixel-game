# 第7章的道具（纽扣第6章先出场，归 p4_props_ch6.py 画）：口红、硬币炸弹、烟头、爱心、修复光的金线头，以及灰姑娘解谜的六张脸大特写。
#   画法照 p4_props.py（字符图 + 自动描边）；六张脸直接调第7章背景脚本 p4_bg_ch7.face_mask 画（和墙上那排脸是同一套五官），再放大 4 倍，
#   这样特写和背景对得上，换正确答案只改背景脚本的 FACES / YUKAKO_FACE。元数据写 _meta/props_ch7.json（build_p4.py 自动深合并）。
#   用法：python3 第四部/tools/art/p4_props_ch7.py
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as P  # noqa: E402
import p4_bg_ch7 as BG7  # noqa: E402

LIPSTICK = dict(R='#e02a3a', r='#a01828', G='#d8b05a', g='#a8823a', W='#ffd0d0')
COIN = dict(Y='#e8c858', y='#b0902a', W='#fff4b0', R='#ff4040')
CIG = dict(W='#f4f0e6', w='#c8c0b0', O='#e88a3a', R='#ff5a2a', y='#f0d070')
HEART = dict(R='#ff6a9a', r='#d03a6a', W='#ffd0e0')
GOLD = dict(Y='#fff0a0', y='#ffd060', o='#f0a030', W='#ffffff')


def main():
    P.PROPS.clear()
    # 纽扣（button）第6章先出场，归第6章画（p4_props_ch6.py），这里不再存，免得两章各画一颗、合并时互相覆盖
    P.save('lipstick', [P.grid(['.W.', 'RRr', 'RRr', 'GGg', 'GGg', 'GGg', 'ggg'], LIPSTICK)])
    # 硬币炸弹：0 普通 / 1 要炸了（红边闪）
    P.save('coin_bomb', [P.grid(['.yYy.', 'yYWYy', 'YWYYY', 'yYYYy', '.yYy.'], COIN),
                         P.grid(['.RRR.', 'RYWYR', 'RWYYR', 'RYYYR', '.RRR.'], COIN)], fps=8, kind='loop')
    P.save('cig', [P.grid(['WWWWwOR'], CIG), P.grid(['WWWWwOy'], CIG)], fps=6, kind='loop')
    P.save('heart', [P.grid(['.RR.RR.', 'RWRRRRr', 'RRRRRRr', '.RRRRr.', '..RRr..', '...r...'], HEART)])
    P.save('gold_trail', [P.grid(['..y..', '.yYy.', 'yYWYy', '.yYy.', '..y..'], GOLD),
                          P.grid(['..o..', '.yYy.', 'oYWYo', '.yYy.', '..o..'], GOLD)], fps=10, kind='loop', outline=False, align='center')
    # 六张脸的大特写：18×24 → 72×96，底下垫一块酒红丝绒（和脸墙同色），外面金框
    faces = []
    for spec in BG7.FACES:
        c = Image.new('RGBA', (22, 28), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        d.rectangle((0, 0, 21, 27), fill=LIB.hexc(BG7.SAL['velvet']))
        d.rectangle((0, 0, 21, 27), outline=LIB.hexc(BG7.SAL['gold']))
        BG7.face_mask(d, 2, 2, spec)
        faces.append(c.resize((88, 112), Image.NEAREST))
    P.save('face_big', faces, outline=False, align='center')
    path = os.path.join(LIB.META, 'props_ch7.json')
    LIB.save_json(path, {'props': dict(P.PROPS)})
    print('第7章道具：', ' '.join(P.PROPS))


if __name__ == '__main__':
    main()
