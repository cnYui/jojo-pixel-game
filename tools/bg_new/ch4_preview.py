# -*- coding: utf-8 -*-
r"""第4章背景重画（2026-10-11，第4章按体验版的精度重做）的预览 / 前后对照：照 late_preview.py，只换 key 表、可走带和输出目录。
只写 tools\bg_new\_preview\ch4\（不碰 assets\、data\）。

    python -B tools\bg_new\ch4_preview.py before  [key ...]   # 现在正式构建出来的样子
    python -B tools\bg_new\ch4_preview.py after   [key ...]   # 跑 tools\bg_new\<key>.py（不经 bg_jojo 路由）出图层 + 预览 + 自检
    python -B tools\bg_new\ch4_preview.py compare [key ...]   # 改前 / 改后上下对照

after 的产物：_preview\ch4\after\<key>.png（镜头 0 / 中间 / 最右）、<key>_people.png（可走带上下沿摆人物）、
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

# 第4章的地图（story\stages_ch02_05.js）：calcutta_ch4 = calcutta_street（1280）、alley_ch4 = india_alley（第 7 战）、
#   varanasi_ch4 = ganges_ghat（640，第 8 战）、varanasi_st_ch4 = varanasi_street（640，乔瑟夫一个人逛；原来借 calcutta_street）
LP.KEYS = ['calcutta_street', 'india_alley', 'ganges_ghat', 'varanasi_street']
LP.STAGE_WALK = {'calcutta_street': (148, 176), 'india_alley': (146, 176), 'ganges_ghat': (148, 176), 'varanasi_street': (148, 176)}
LP.OUT = os.path.join(HERE, '_preview', 'ch4')

if __name__ == '__main__':
    sys.exit(LP.main() or 0)
