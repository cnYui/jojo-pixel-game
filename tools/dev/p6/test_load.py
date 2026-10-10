# -*- coding: utf-8 -*-
r"""包 6 自测：Playwright（Chromium）打开 tools\dev\p6\load_test.html，检查 data\*.js（或 fixture）能完整加载。

    python -B tools\dev\p6\test_load.py               # 测 游戏\data\
    python -B tools\dev\p6\test_load.py --fixture     # 测 tools\dev\fixture\
    python -B tools\dev\p6\test_load.py --both

判定：页面里 0 错误；控制台 0 warning / 0 error（含 willReadFrequently 提示）；没有未捕获异常。返回码 0 = 通过。
"""
import sys
sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import pathlib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = pathlib.Path(HERE, "load_test.html").as_uri()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_one(pw, src):
    browser = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required", "--allow-file-access-from-files"])
    page = browser.new_page(viewport={"width": 900, "height": 700})
    console, pageerr = [], []
    page.on("console", lambda m: console.append((m.type, m.text)) if m.type in ("warning", "error") else None)
    page.on("pageerror", lambda e: pageerr.append(str(e)))
    page.goto(PAGE + "?src=" + src)
    page.wait_for_function("window.__RESULT && window.__RESULT.done", timeout=120000)
    res = page.evaluate("window.__RESULT")
    browser.close()
    ok = not res["errors"] and not console and not pageerr
    print(f"== {src}: {'通过' if ok else '失败'}")
    print(json.dumps(res["info"], ensure_ascii=False, indent=1))
    for e in res["errors"][:40]:
        print("  页面错误：" + e)
    for t, m in console[:40]:
        print(f"  控制台 {t}：{m}")
    for e in pageerr:
        print("  未捕获异常：" + e)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", action="store_true")
    ap.add_argument("--both", action="store_true")
    a = ap.parse_args()
    srcs = ["data", "fixture"] if a.both else (["fixture"] if a.fixture else ["data"])
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        oks = [run_one(pw, s) for s in srcs]
    return 0 if all(oks) else 1


if __name__ == "__main__":
    sys.exit(main())
