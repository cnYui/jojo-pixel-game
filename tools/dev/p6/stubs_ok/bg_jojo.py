# -*- coding: utf-8 -*-
# 包 6 自测用的桩（不是包 7B 的真 bg_jojo.py）：只导出 sky_day（两层 wrap）和一个没在 packs.json 登记的 test_extra，
# 其余 §3.14 D 的 key 应由 build_assets 的兜底快照补上。
from PIL import Image


def build_all(stages, c):
    a = Image.new("RGBA", (640, 120), (90, 150, 230, 255))
    b = Image.new("RGBA", (640, 60), (240, 240, 255, 180))
    ka = c["save_png"](a, "bg/sky_day/far", "common")
    kb = c["save_png"](b, "bg/sky_day/cloud", "common")
    stages["sky_day"] = dict(pack="common", w=320, ground=150, walk=[140, 176], anchors={},
                             layers=[dict(type="wrap", image=ka, period=640, k=0.2),
                                     dict(type="wrap", image=kb, period=640, k=0.5, vx=-12, y=30)], fg=[])
    k = c["save_png"](Image.new("RGB", (320, 180), (30, 30, 40)), "bg/test_extra/base", "common")
    stages["test_extra"] = dict(w=320, ground=150, walk=[140, 176], anchors={}, layers=[dict(type="static", image=k)],
                                fg=[])
