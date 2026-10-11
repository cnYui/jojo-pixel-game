# -*- coding: utf-8 -*-
r"""第3章背景重画（2026-10-11，第3章按体验版的精度重做）的预览 / 前后对照：照 late_preview.py，只换 key 表、可走带和输出目录。
只写 tools\bg_new\_preview\ch3\（不碰 assets\、data\）。

    python -B tools\bg_new\ch3_preview.py before  [key ...]   # 现在正式构建出来的样子
    python -B tools\bg_new\ch3_preview.py after   [key ...]   # 跑 tools\bg_new\<key>.py（不经 bg_jojo 路由）出图层 + 预览 + 自检
    python -B tools\bg_new\ch3_preview.py compare [key ...]   # 改前 / 改后上下对照

after 的产物：_preview\ch3\after\<key>.png（镜头 0 / 中间 / 最右）、<key>_people.png（可走带上下沿摆人物）、
<key>_state.png（所有 key 状态打开）、<key>_anim.png（t = 0 / 0.5 / 1 / 1.5）。
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('late_preview', os.path.join(HERE, 'late_preview.py'))
LP = importlib.util.module_from_spec(_spec)
sys.modules['late_preview'] = LP
_spec.loader.exec_module(LP)

# 第3章的地图（story\stages_ch02_05.js）：sg_street_ch3 = singapore_street（960）、sg_hotel_ch3 = singapore_hotel、
#   cable_ch3 = cable_car（车厢 x 40–280）、cable_view（新：缆车外景，过场用）、train_ch3 = train_interior；
#   sea_ch3 用第2章重画过的 underwater
LP.KEYS = ['singapore_street', 'singapore_hotel', 'cable_car', 'cable_view', 'train_interior']
LP.STAGE_WALK = {'singapore_street': (150, 176), 'singapore_hotel': (148, 176), 'cable_car': (150, 170), 'cable_view': (150, 170),
                 'train_interior': (156, 174)}
LP.OUT = os.path.join(HERE, '_preview', 'ch3')

if __name__ == '__main__':
    sys.exit(LP.main() or 0)
