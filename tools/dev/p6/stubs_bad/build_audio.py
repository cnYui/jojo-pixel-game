# -*- coding: utf-8 -*-
# 包 6 自测用的坏桩：run 抛错 → audio 步应跳过、构建继续。
def run(args, c):
    raise OSError("桩：build_audio 故意抛错")
