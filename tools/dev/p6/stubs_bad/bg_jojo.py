# -*- coding: utf-8 -*-
# 包 6 自测用的坏桩：world_map 完整导出 → sky_day 存了一张图、图层还没写 → 抛错。
# bg 步应保留 world_map（完整的），丢掉 sky_day 半截登记的图，sky_day 和其余 key 用兜底快照。
from PIL import Image


def build_all(stages, c):
    k = c["save_png"](Image.new("RGB", (320, 180), (20, 60, 90)), "bg/world_map/stub", "common")
    stages["world_map"] = dict(pack="common", w=320, ground=150, walk=[140, 176], anchors={},
                               layers=[dict(type="static", image=k)], fg=[])
    c["save_png"](Image.new("RGB", (320, 180), (255, 0, 255)), "bg/sky_day/half_done", "common")
    stages["sky_day"] = dict(pack="common", layers=[])
    raise ValueError("桩：bg_jojo 导出到一半出错")
