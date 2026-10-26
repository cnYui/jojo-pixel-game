# -*- coding: utf-8 -*-
r"""cairo_day —— 开罗老城的那条街（day）。画法、布局、锚点全在 cairo_parts.py（三张开罗街共用一个函数，按时段出图）；
这个文件只按时段取图层表。说明见 cairo_parts.py 开头。"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _parts():
    key = 'bg_new_cairo_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'cairo_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


def export(ex, BJ):
    return _parts().street_export(ex, BJ, 'day')
