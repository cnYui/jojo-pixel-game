# -*- coding: utf-8 -*-
r"""第5章到终章背景重画（2026-10-15）的预览 / 前后对照：照 late_preview.py，按章换 key 表、可走带和输出目录。
只写 tools\bg_new\_preview\<章>\（不碰 assets\、data\），几个人分头画不同的章也不会互相覆盖。

    python -B tools\bg_new\chapter_preview.py ch6 before  [key ...]   # 现在正式构建出来的样子（assets\bg + _meta\bg.json）
    python -B tools\bg_new\chapter_preview.py ch6 after   [key ...]   # 走 bg_jojo 的正式导出入口（tools\bg_new\<key>.py 在就用它）
    python -B tools\bg_new\chapter_preview.py ch6 compare [key ...]   # 改前 / 改后上下对照

after 的产物：_preview\<章>\after\<key>.png（镜头 0 / 中间 / 最右）、<key>_people.png（可走带上下沿摆人物）、
<key>_state.png（所有 key 状态打开）、<key>_anim.png（t = 0 / 0.5 / 1 / 1.5）、<key>_anchors.png（整张地图 + 剧情锚点）。
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

# 每章用到的背景和地图的可走带（story\stages_ch02_05.js / stages_ch06_09.js / stages_late.js；改地图时两边一起改）
CHAPTERS = {
    'ch5': {'desert_highway': (152, 168), 'mountain_road': (148, 176), 'fog_town': (146, 176), 'enya_inn': (148, 176),
            'karachi_street': (148, 176), 'brain_inside': (130, 176)},
    'ch6': {'desert_noon': (148, 176), 'yaprin_village': (148, 176), 'cessna_cabin': (154, 172), 'dream_carnival': (140, 176),
            'desert_night': (148, 176)},
    'ch7': {'redsea_island': (148, 176), 'submarine': (150, 176), 'seabed_mouth': (150, 174), 'egypt_coast': (148, 176)},
    'ch8': {'egypt_coast': (148, 176), 'desert_day': (148, 178), 'aswan_town': (148, 176)},
    'ch9': {'egypt_temple': (148, 176), 'nile_bank': (148, 176), 'luxor_town': (148, 176), 'egypt_rail': (148, 178),
            'luxor_house': (146, 176)},
    'ch10': {'cafe_interior': (150, 172), 'cairo_day': (150, 176), 'cairo_sewer': (148, 172), 'mansion_hall': (148, 174),
             # 2026-10-19 插画背景（全屏静态，没有可走带；这里的值只给“带人”预览图用）
             'poker_table': (150, 176), 'cairo_map': (150, 176)},
    'ch11': {'mansion_exterior': (150, 172), 'mansion_corridor': (150, 174), 'game_room': (150, 172),
             'illusion_corridor': (150, 174), 'mansion_hall': (148, 174), 'mansion_tower': (150, 172),
             'crt_baseball': (150, 176)},
    'final': {'mansion_stairs': (146, 174), 'cairo_street_night': (148, 176), 'cairo_rooftops': (145, 176),
              'cairo_street_dawn': (148, 176), 'kujo_bedroom_morning': (150, 176), 'airport': (150, 176)},
}


def main():
    args = sys.argv[1:]
    if not args or args[0] not in CHAPTERS:
        print(__doc__)
        print('章：', ', '.join(CHAPTERS))
        return 2
    ch = args.pop(0)
    LP.KEYS = list(CHAPTERS[ch])
    LP.STAGE_WALK = dict(CHAPTERS[ch])
    LP.OUT = os.path.join(HERE, '_preview', ch)
    sys.argv = [sys.argv[0]] + args
    return LP.main() or 0


if __name__ == '__main__':
    sys.exit(main())
