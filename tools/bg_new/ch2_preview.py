# -*- coding: utf-8 -*-
r"""第2章背景重画（2026-10-10 晚，第2章按体验版的精度重做）的预览 / 前后对照：照 late_preview.py，只换 key 表、可走带和输出目录。
只写 tools\bg_new\_preview\ch2\（不碰 assets\、data\）。

    python -B tools\bg_new\ch2_preview.py before  [key ...]   # 现在正式构建出来的样子（sea_fog 是新 key，没有改前）
    python -B tools\bg_new\ch2_preview.py after   [key ...]   # 跑 tools\bg_new\<key>.py（不经 bg_jojo 路由）出图层 + 预览 + 自检
    python -B tools\bg_new\ch2_preview.py compare [key ...]   # 改前 / 改后上下对照

after 的产物：_preview\ch2\after\<key>.png（镜头 0 / 中间 / 最右）、<key>_people.png（可走带上下沿摆人物）、
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

# 第2章的地图（story\stages_ch02_05.js）：boat_ch2 = yacht_deck、dinghy_ch2 = sea_fog、freighter_ch2 = freighter_deck、
#   hold_ch2 = freighter_corridor、underwater_ch2 = underwater（第3章 sea_ch3 也用 underwater，320 宽、可走带 150–176）
LP.KEYS = ['yacht_deck', 'sea_fog', 'freighter_deck', 'freighter_corridor', 'underwater']
LP.STAGE_WALK = {'yacht_deck': (146, 172), 'sea_fog': (150, 170), 'freighter_deck': (146, 172),
                 'freighter_corridor': (148, 176), 'underwater': (158, 178)}
LP.OUT = os.path.join(HERE, '_preview', 'ch2')

if __name__ == '__main__':
    sys.exit(LP.main() or 0)
