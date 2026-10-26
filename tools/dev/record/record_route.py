"""连续录制指定章节的真实键盘通关路线。

录制器只初始化一次；每章结束后从章末菜单进入章节选择，再进入下一章，
这样生成的 full.webm 是一条连续的通关视频，而不是五段重新回标题的录像。
"""
import sys

sys.dont_write_bytecode = True

import argparse
import base64
import functools
import http.server
import json
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAME = HERE.parents[2]
sys.path.insert(0, str(GAME / "tools"))
sys.path.insert(0, str(GAME / "tools" / "dev" / "full"))
sys.path.insert(0, str(HERE))

import playtest  # noqa: E402
import record_demo  # noqa: E402


DEFAULT_CHAPTERS = ("prologue", "ch1", "ch2", "ch3", "ch4")


def route_tester_class(chapter):
    """按章节使用对应的只读真实键盘测试器；录制器只包一层采样，不改变输入逻辑。"""
    if chapter in tuple(f"ch{i}" for i in range(5, 10)):
        import playtest_mid
        return playtest_mid.MidTester
    if chapter in ("ch10", "ch11", "final"):
        import test_late_routes
        return test_late_routes.LateTester
    return record_demo.tester_class(chapter)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def args_for(chapter, out):
    return playtest.parser().parse_args(
        [chapter, "--out", str(out / "tester" / chapter), "--shots-off"]
    )


def check_chapter(tester, chapter):
    """录制必须建立在真实路线成功的基础上，避免生成半截视频却误报完成。"""
    completed = any(n.get("kind") == "route_complete" for n in tester.notes)
    # MediaRecorder 会让无头浏览器的 FPS 采样变低，录制校验里的性能门槛
    # 可能因此留下警告；章节是否真的走到章末仍以 route_complete 为准。
    if not completed:
        raise RuntimeError(
            f"{chapter} 未完成：route_complete={completed}, errors={len(tester.errors)}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument(
        "--chapters",
        default=",".join(DEFAULT_CHAPTERS),
        help="逗号分隔的章节 ID；可用 ch5–ch11、final，默认序章到第4章",
    )
    parser.add_argument(
        "--keep-ui",
        action="store_true",
        default=True,
        help="保留对白、提示和章节菜单，便于观看者确认通关过程",
    )
    a = parser.parse_args()
    chapters = tuple(x.strip() for x in a.chapters.split(",") if x.strip())
    if not chapters:
        raise SystemExit("--chapters 不能为空")
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    for key in ("full", "bgm", "sfx"):
        path = out / f"{key}.webm"
        if path.exists():
            raise SystemExit(f"{path} 已存在，请换一个输出目录")

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(Quiet, directory=str(GAME))
    )
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    files = {
        key: open(out / f"{key}.webm", "ab") for key in ("full", "bgm", "sfx")
    }
    all_marks = []
    all_trace = []
    all_samples = []
    chapter_reports = []
    errors = []
    rec0 = None
    rec_len = 0.0

    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True, args=["--autoplay-policy=no-user-gesture-required"]
            )
            page = browser.new_page(
                viewport={"width": 1280, "height": 720}, device_scale_factor=1
            )
            page.expose_function(
                "__recSave",
                lambda key, b64: files[key].write(base64.b64decode(b64)) and None,
            )
            def on_pageerror(exc):
                # 换章时引擎会主动取消旧剧情 Promise；这是正常控制流，不能当成崩溃记入录制错误。
                if "这一轮剧情已结束" in str(exc):
                    return
                errors.append({"kind": "pageerror", "text": str(exc)})

            page.on("pageerror", on_pageerror)
            page.goto(
                f"http://127.0.0.1:{port}/index.html?autotest=1",
                wait_until="load",
            )
            page.wait_for_function("() => G.booted && G.ui.menu", timeout=60000)
            page.keyboard.press("Shift")
            page.wait_for_function(
                "() => G.audio && G.audio.ctx && G.audio.master", timeout=20000
            )
            page.wait_for_timeout(1200)
            if not a.keep_ui:
                page.evaluate("() => { window.__recCleanUI = true; }")
            page.evaluate((HERE / "recorder.js").read_text(encoding="utf-8"))
            rec0 = time.monotonic()
            page.wait_for_timeout(2500)

            previous = None
            for chapter in chapters:
                base = route_tester_class(chapter)
                Tester = record_demo.make_recording_tester(base)
                chapter_out = out / "tester" / chapter
                chapter_out.mkdir(parents=True, exist_ok=True)
                targs = args_for(chapter, out)
                targs.timeout = a.timeout
                tester = Tester(page, targs, chapter_out)

                if previous is not None:
                    # 章末菜单的“选择章节”会回到标题，再由新测试器选择下一章。
                    if not previous.menu("选择章节"):
                        raise RuntimeError(f"{chapter} 前无法打开章节选择")
                    # goTitle('chapters') 直接打开章节页，不再经过标题里的“选择章节”项。
                    idx = playtest.chapter_index(chapter)
                    for _ in range(idx // 5):
                        if not tester.menu("下一页"):
                            raise RuntimeError(f"{chapter} 前无法翻到章节页")
                    label = "终章" if idx == 12 else "第" + str(idx) + "章"
                    if not tester.menu(label):
                        raise RuntimeError(f"{chapter} 无法从章节选择进入")
                    # enter() 已经把当前章节启动；run() 再调用 enter 会重复进菜单。
                    tester.enter = lambda: True

                started_offset = tester.started - rec0
                try:
                    tester.run()
                    check_chapter(tester, chapter)
                except Exception as exc:
                    errors.append({"kind": "tester_error", "chapter": chapter, "text": str(exc)})
                    raise

                for mark in tester.marks:
                    all_marks.append([round(mark[0] + started_offset, 2), *mark[1:]])
                for row in tester.trace:
                    all_trace.append({**row, "t": round(row["t"] + started_offset, 2), "chapter": chapter})
                for row in tester.samples or []:
                    all_samples.append([round(row[0] + started_offset, 2), *row[1:]])
                chapter_reports.append(
                    {
                        "chapter": chapter,
                        "seconds": round(tester.elapsed(), 2),
                        "errors": tester.errors,
                        "notes": tester.notes,
                    }
                )
                previous = tester

            page.wait_for_timeout(2500)
            rec_len = time.monotonic() - rec0
            page.evaluate("() => window.__recStop()")
            page.wait_for_function("() => window.__recPending === 0", timeout=120000)
            page.wait_for_timeout(500)
            fps = page.evaluate("() => G.dbg && G.dbg.snapshot ? G.dbg.snapshot().fps : null")
            browser.close()
    finally:
        for handle in files.values():
            handle.close()
        server.shutdown()

    run = {
        "chapters": list(chapters),
        "length": round(rec_len, 2),
        "fps": fps if "fps" in locals() else None,
        "marks": all_marks,
        "trace": all_trace,
        "samples": all_samples,
        "chapter_reports": chapter_reports,
        "errors": errors,
        "input_boundary": "剧情、移动、攻击、QTE、失败重试和章节切换全部经真实键盘；只读公开快照。",
    }
    (out / "run.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "ok": not errors and len(chapter_reports) == len(chapters),
                "length": run["length"],
                "chapters": len(chapter_reports),
                "errors": len(errors),
                "out": str(out),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
