# 序章背景（重画）：东方家客厅、上学路、校门、超市、东方家门口（傍晚 / 夜 / 雨）、海边路（雨 / 雨后）。
#   每张图的宽度、可走带、地面落点的锚点和旧图一样（剧情脚本按这些坐标走位）；
#   家具和门窗按 第四部/docs/比例标准.md 重新定尺寸；室内画成剖面：一楼切开，上面是二楼外墙、屋顶和天空。
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from px import Cv, mix, shade  # noqa: E402
import bgkit as K  # noqa: E402
from bgkit import FLOOR, CEIL  # noqa: E402


def rain_view(cols=('#5a6478', '#77839a')):
    def fn(cv, x0, y0, x1, y1):
        K.vgrad(cv, x0, y0, x1, y1, [cols[0], cols[1]])
        # 院子里的树篱和邻家屋顶的影子
        cv.rect(x0, y1 - 6, x1, y1, '#3a5a4a')
        K.dither(cv, x0, y1 - 8, x1, y1 - 7, '#3a5a4a', 0.5)
        cv.rect(x0 + (x1 - x0) // 2, y0 + 8, x1, y0 + 12, '#4a5468')
    return fn


def higashikata_living():
    W, H = 480, 180
    cv = Cv(W, H)
    F, C = FLOOR, FLOOR - CEIL          # 墙脚线 138、天花线 94
    # ---- 上半截：雨天的天空、二楼外墙、屋顶
    K.sky(cv, 0, W - 1, C - 4, K.SKY_RAIN)
    K.roof_hip(cv, 36, 380, C - 44, C - 70, '#3c4658', inset=40)
    K.siding(cv, 42, C - 42, 374, C - 5, '#d8cdb8')
    for wx in (86, 196, 306):
        K.window_ext(cv, wx - 12, C - 33, wx + 12, C - 15, lit='#f6d98a' if wx == 196 else None, nx=2, rail='#8a8478' if wx == 196 else None)
    K.roof_shed(cv, 374, 479, C - 8, C - 22, '#3c4658', 'left')      # 厨房的披檐
    K.roof_shed(cv, 0, 42, C - 8, C - 20, '#3c4658', 'right')        # 玄关的披檐
    K.darken(cv, 0, 0, W - 1, C - 5, 0.86)
    K.ceiling_slab(cv, 0, W - 1, C, 4, '#6a4e36')
    # ---- 一楼：后墙、地板
    K.wall(cv, 11, 361, '#f0e4c8', stripes=(8, '#e8dab8'), wains=(13, '#b89060'), crown='#8a6a44')
    K.wall(cv, 365, 469, '#f4eede', base='#b0a890', crown='#8a6a44')
    K.floor_wood(cv, 0, 363, c='#c49660')
    K.floor_tile(cv, 364, W - 1)
    # 两头剖开的外墙 + 屋外
    for x in (8, 470):
        K.cut_wall(cv, x, C, 179, 3)
    cv.rect(0, C, 7, 179, '#4a5a58')
    cv.rect(473, C, W - 1, 179, '#4a5a58')
    K.dither(cv, 0, F - 10, 7, 179, '#3a4a44', 0.5)
    K.dither(cv, 473, F - 10, W - 1, 179, '#3a4a44', 0.5)
    # ---- 客厅
    K.calendar(cv, 22, F - 27)
    K.phone_stand(cv, 22, F)
    K.door(cv, 48, F, c='#a87a4c', frame='#6a4a2c', side=-1)        # 通走廊的门（204 cm）
    K.window(cv, 68, F - 34, 128, F - 1, frame='#e8dcc4', nx=2, ny=1, sill=False, view=rain_view(), curtain='#d8847a', rod='#7a5a3c')
    K.switch(cv, 146, F - 21)
    K.bookshelf(cv, 174, 198, F, 30, '#8a6240', seed=7)
    K.sofa(cv, 231, F, w=48, c='#7a6ab8', cushion='#e8a0b8')
    # 良平的照片（警帽、蓝制服）
    x0, y0, x1, y1 = K.picture(cv, 229, F - 28, 9, 11, '#3a2a1e', ('#b8c8d8', '#2a3660', '#f0c8a0'))
    cv.rect(x0 + 3, y0 + 2, x0 + 5, y0 + 3, '#2a3660')
    cv.rect(x0 + 3, y0 + 4, x0 + 5, y0 + 5, '#f0c8a0')
    K.clock(cv, 262, F - 33, 3)
    K.cabinet(cv, 268, 296, F, 12, '#9a7248', doors=2)
    K.plant(cv, 276, F - 12, 9, seed=4)
    cv.rect(286, F - 15, 291, F - 13, '#e8e4d8')          # 相框
    K.tv_crt(cv, 325, F, stand_h=8)
    K.picture(cv, 325, F - 31, 14, 9, '#6a4a2a')
    K.bookshelf(cv, 343, 358, F, 30, '#9a7248', seed=11, empty=0.4)
    K.plant(cv, 302, F, 16, pot='#8a8a94', seed=9)
    K.lamp_ceiling(cv, 200, C + 2, w=12)
    # 客厅和厨房之间：柱 + 垂壁
    cv.rect(362, C + 2, 364, F, '#8a6a44')
    cv.vline(362, C + 2, F, shade('#8a6a44', 0.25))
    # ---- 厨房
    K.wall_cabinet(cv, 372, 446, C + 3, F - 24, '#e8dcc0')
    K.kitchen_counter(cv, 372, 446, F, '#e8dcc0', sink_x=400, stove_x=431)
    K.range_hood(cv, 431, F - 29, 16)
    K.kettle(cv, 431, F - 16)
    cv.rect(368, F - 23, 380, F - 22, '#b89060')          # 放手套盒的小搁板
    K.fridge(cv, 450, F, 13, 28)
    K.rug(cv, 180, 290, 152, 166)
    K.lamp_ceiling(cv, 416, C + 2, w=8)
    return cv


def build_higashikata_living():
    cv = higashikata_living()
    F = FLOOR
    OB = K.old_lib()
    # 窗里的雨（8 帧循环）：落地窗玻璃 59 × 32
    winrain = OB.rain_strip(59, 32, n=8, near=12, far=9, length=(5, 3), slant=-0.18, cols=('#c8d2e0', '#9aa6b8'), alpha=(200, 150), seed=21)
    K.save_layers('higashikata_living', {'room': cv, 'winrain': winrain})
    K.update_meta('higashikata_living',
                  anchors=dict(kettle=[431, F - 18], wallhole=[159, 116], window=[98, F - 17], glovebox=[374, F - 23],
                               photo=[229, F - 28], tv=[325, F - 14]),
                  layers={'winrain': dict(x=69, y=F - 33, w=59, h=32)})
    return cv


BUILD = {'higashikata_living': build_higashikata_living}


if __name__ == '__main__':
    out = sys.argv[1]
    import cast_pro
    for key in (sys.argv[2:] or list(BUILD)):
        cv = BUILD[key]()
        w = cv.w
        figs = [(cast_pro.build(c), x, y) for c, x, y in (('josuke', w * 0.3, 158), ('jotaro4', w * 0.4, 150), ('koichi', w * 0.6, 160),
                                                          ('tomoko', w * 0.5, 146), ('kid', w * 0.8, 156))]
        K.people_check(cv.img(), figs, 3).save('%s/bg_%s.png' % (out, key))
        print(key, cv.w)
