# -*- coding: utf-8 -*-
# 包 6 自测用的桩（不是包 1 的真 build_audio.py）：不写任何文件，只记一下被调用了。
CALLS = []


def run(args, c):
    CALLS.append(list(args))
    print("  （桩 build_audio.run 被调用：", args, "）")
