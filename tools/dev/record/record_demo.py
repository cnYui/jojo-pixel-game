r"""边打边录：测试器用真实键盘把一章从头打到尾，页面里同时录画面 + 混音、BGM、音效三条（recorder.js）。

    python -B tools\dev\record\record_demo.py prologue --out <目录>
    python -B tools\dev\record\record_demo.py ch1 --out <目录>

输出：<目录>\full.webm（画面 + 混音）、bgm.webm、sfx.webm（三条同一时刻开录）、run.json（marks：剧情标记 / 战斗开始 /
必杀 / 连打 / 弹反……的时间，单位秒，**已换算成从开录算起**）。画面上不画对话框、操作提示、目标箭头（recorder.js）。
用本机 http 服务打开游戏；录的时候别跑转码之类的重活（会掉帧）。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import base64  # noqa: E402
import functools  # noqa: E402
import http.server  # noqa: E402
import json  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
GAME = HERE.parents[2]
sys.path.insert(0, str(GAME / 'tools'))
sys.path.insert(0, str(GAME / 'tools' / 'dev' / 'full'))
import playtest  # noqa: E402

COUNT_KEYS = ('special', 'rushStart', 'parry', 'qte_start', 'party_join', 'koBlocked', 'dodge_perfect', 'graze')


def tester_class(chapter):
    if chapter == 'prologue':
        import test_jail_shots
        return test_jail_shots.JailTester
    import test_ch1
    return test_ch1.Ch1Tester


def make_recording_tester(base):
    class Rec(base):
        """多记几种“好看的时刻”：计数一涨就记一条 mark（必杀、连打开始、弹反、QTE……）。"""
        def st(self):
            s = super().st()
            c = s.get('counts') or {}
            prev = getattr(self, '_prev_counts', {})
            for k in COUNT_KEYS:
                if (c.get(k) or 0) > (prev.get(k) or 0):
                    self.marks.append([self.elapsed(), k, 'event', s.get('fightId'), s.get('stage')])
            self._prev_counts = dict(c)
            ins = bool(s.get('insert'))
            if ins and not getattr(self, '_prev_insert', False):
                self.marks.append([self.elapsed(), 'insert', 'event', s.get('fightId'), s.get('stage')])
            self._prev_insert = ins
            return s
    return Rec


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('chapter', choices=['prologue', 'ch1'])
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--keep-ui', action='store_true', help='画面上保留对话框和提示')
    a = ap.parse_args()
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    for k in ('full', 'bgm', 'sfx'):
        p = out / f'{k}.webm'
        if p.exists():
            raise SystemExit(f'{p} 已存在，换个目录')

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(GAME)))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    targs = playtest.parser().parse_args([a.chapter, '--out', str(out / 'tester'), '--shots-off'])
    (out / 'tester').mkdir(exist_ok=True)
    files = {k: open(out / f'{k}.webm', 'ab') for k in ('full', 'bgm', 'sfx')}

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
        page.expose_function('__recSave', lambda k, b64: files[k].write(base64.b64decode(b64)) and None)
        T = make_recording_tester(tester_class(a.chapter))
        errors = []
        page.on('pageerror', lambda e: errors.append({'kind': 'pageerror', 'text': str(e)}))
        page.goto(f'http://127.0.0.1:{port}/index.html?autotest=1', wait_until='load')
        page.wait_for_function('() => G.booted && G.ui.menu', timeout=60000)
        page.keyboard.press('Shift')                         # 第一次按键 = 解锁声音（建 AudioContext）
        page.wait_for_function('() => G.audio && G.audio.ctx && G.audio.master', timeout=20000)
        page.wait_for_timeout(1200)                          # 标题曲起来
        if a.keep_ui:
            page.evaluate('() => { window.__recCleanUI = false; }')
        page.evaluate((HERE / 'recorder.js').read_text(encoding='utf-8'))
        rec0 = time.monotonic()
        page.wait_for_timeout(2500)                          # 标题画面先录 2.5 s
        t = T(page, targs, out / 'tester')
        offset = t.started - rec0
        try:
            t.run()
        except Exception as e:
            errors.append({'kind': 'tester_error', 'text': str(e)})
        page.wait_for_timeout(2500)
        rec_len = time.monotonic() - rec0
        page.evaluate('() => window.__recStop()')
        page.wait_for_function('() => window.__recPending === 0', timeout=120000)
        page.wait_for_timeout(500)
        fps = page.evaluate('() => G.dbg && G.dbg.snapshot ? G.dbg.snapshot().fps : null')
        browser.close()
    for f in files.values():
        f.close()
    srv.shutdown()
    marks = [[round(m[0] + offset, 2)] + list(m[1:]) for m in t.marks]
    trace = [dict(x, t=round(x['t'] + offset, 2)) for x in t.trace]
    run = {'chapter': a.chapter, 'offset': round(offset, 3), 'length': round(rec_len, 2), 'fps': fps,
           'marks': marks, 'trace': trace, 'errors': errors + t.errors, 'notes': t.notes}
    (out / 'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({'len': run['length'], 'marks': len(marks), 'errors': len(run['errors']), 'fps': fps}, ensure_ascii=False))


if __name__ == '__main__':
    main()
