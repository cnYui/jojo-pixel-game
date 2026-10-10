# -*- coding: utf-8 -*-
# 包 6 自测用的坏桩：run 抛错 → art 步应打印原因、跳过、整个构建继续。
def run(out_dir, c):
    raise RuntimeError("桩：bake_art 故意抛错")
