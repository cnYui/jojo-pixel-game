r"""G.ads 激励视频封装冒烟：mock 六种结果、busy、没有 SDK、SDK 多次回调的状态序列。

    python -B tools\dev\full\test_ads.py
    python -B tools\dev\full\test_ads.py --root <发布包文件夹>

测试页用 file:// + ?autotest=1；CDN 请求全部拦掉，保证“没有 SDK”和假 SDK 用例可控。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

GAME = Path(__file__).resolve().parents[3]

MOCK_CASES = {
    'ok': ('rewarded', False, 4),   # 看完广告是正常结算，不属于技术故障
    'closed': ('closed', False, 1),
    'skipped': ('skipped', False, 2),
    'fail': ('failed', True, -1),
    'timeout': ('timeout', True, None),
    'unsupported': ('unsupported', True, None),
}

# 假 SDK：按 seq 里的状态依次回调；code 默认 0。
INSTALL_FAKE = """({ seq, delay, code }) => {
  window.MetaH5Ad = {
    isAdSupport: function (type, cb) { setTimeout(function () { cb({ code: 0, data: 1 }); }, 0); },
    showAd: function (type, cb) {
      const list = seq || [];
      list.forEach(function (status, i) {
        setTimeout(function () {
          cb({ adType: 1, code: code == null ? 0 : code, message: 'fake', data: { type: 1, status: status } });
        }, delay * (i + 1));
      });
    }
  };
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=str(GAME), help='发布包文件夹（默认开发目录）')
    ap.add_argument('--out', default=str(GAME / 'tools' / '_playtest' / 'ads_check'))
    a = ap.parse_args()
    root = Path(a.root)
    # 广告封装是 233 线独有的（用户 2026-10-25：小红书线无广告，ads.js 不在游戏源码里），源码目录没有 G.ads，别白等 60 秒超时。
    if not (root / 'engine' / 'ads.js').exists():
        raise SystemExit('%s 里没有 engine/ads.js：游戏源码不带广告封装。先 python -B 233乐园\\overlay.py --make-dev 做一份 233 变体，再 --root <那份变体>' % root)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    base = (root / 'index.html').as_uri()
    checks, page_errors = [], []

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        def open_page(query=''):
            page = browser.new_page(viewport={'width': 1280, 'height': 720})
            # 不让真 SDK 干扰；顺带验证 CDN 加载失败时游戏照样能启动到 G.ads 就绪。
            page.route('https://cdn.233xyx.com/**', lambda route: route.abort())
            page.on('pageerror', lambda e: page_errors.append(str(e)))
            page.goto(base + query, wait_until='load')
            page.wait_for_function('() => !!(window.G && G.ads)', timeout=60000)
            return page

        def check(ok, what, **kw):
            checks.append({'ok': bool(ok), 'what': what, **kw})
            line = ('PASS ' if ok else 'FAIL ') + what
            if kw:
                line += '  ' + json.dumps(kw, ensure_ascii=False)
            print(line, flush=True)

        def brief(r):
            return {k: r.get(k) for k in ('success', 'reason', 'technical', 'status', 'mocked') if k in r}

        # ---- 没有 SDK：supported() 必须 false，watch 报 sdk_missing ----
        page = open_page('?autotest=1')
        sdk_type = page.evaluate('() => typeof window.MetaH5Ad')
        check(sdk_type == 'undefined', 'CDN 失败时没有 window.MetaH5Ad', actual=sdk_type)
        check(page.evaluate('() => G.ads.supported()') is False, '没有 SDK 时 supported() 为 false')
        r = page.evaluate('() => G.ads.watch("no_sdk")')
        check(r.get('reason') == 'sdk_missing' and r.get('technical') is True and r.get('success') is False,
              '没有 SDK 时 watch 返回 sdk_missing/technical', result=brief(r))
        check(page.evaluate('() => G.ads.busy') is False, 'sdk_missing 后 busy 复位')

        # ---- 六种 mock 结果 ----
        for mode, (reason, technical, status) in MOCK_CASES.items():
            check(page.evaluate('m => G.ads.setMock(m)', mode) is True, f'mock {mode}: setMock 生效')
            supported = page.evaluate('() => G.ads.supported()')
            check(supported is (mode != 'unsupported'), f'mock {mode}: supported() 结果', supported=supported)
            t0 = time.monotonic()
            r = page.evaluate('async m => await G.ads.watch("mock_" + m)', mode)
            elapsed = time.monotonic() - t0
            ok = (r.get('reason') == reason and r.get('technical') is technical and
                  r.get('success') is (mode == 'ok') and (status is None or r.get('status') == status) and
                  elapsed < 2.0)
            check(ok, f'mock {mode}: watch 返回正确且不等待', result=brief(r), elapsed=round(elapsed, 3))
            check(page.evaluate('() => G.ads.busy') is False, f'mock {mode}: 结束后 busy=false')

        # ---- busy 保护（mock 也有 50 ms 窗口） ----
        page.evaluate('() => G.ads.setMock("ok")')
        ev = page.evaluate("""async () => {
          const first = G.ads.watch('busy_first');
          const during = G.ads.busy;
          const second = await G.ads.watch('busy_second');
          const firstResult = await first;
          return { during, second, first: firstResult, after: G.ads.busy };
        }""")
        check(ev['during'] is True, '播放中 G.ads.busy=true')
        check(ev['second'].get('reason') == 'busy' and ev['second'].get('technical') is False,
              '播放中再 watch 返回 busy/technical=false', result=brief(ev['second']))
        check(ev['first'].get('success') is True, 'busy 被拒绝不影响第一次播放')
        check(ev['after'] is False, '第一次播放结束后 busy=false')

        # ---- URL 参数 mock ----
        page_url = open_page('?autotest=1&adMock=closed')
        r = page_url.evaluate('() => G.ads.watch("url_mock")')
        check(r.get('reason') == 'closed' and r.get('technical') is False,
              '?adMock=closed 生效', result=brief(r))

        # ---- 正式环境：setMock 无效 ----
        page_formal = open_page('')
        check(page_formal.evaluate('() => G.ads.setMock("ok")') is False, '正式环境 setMock 返回 false')
        check(page_formal.evaluate('() => G.ads.supported()') is False, '正式环境 setMock 后 supported() 仍为 false')
        r = page_formal.evaluate('() => G.ads.watch("formal")')
        check(r.get('reason') == 'sdk_missing' and r.get('mocked') is None,
              '正式环境 setMock 后 watch 仍走真 SDK 分支', result=brief(r))

        # ---- 假 SDK：状态序列 ----
        page_sdk = open_page('?autotest=1')

        page_sdk.evaluate(INSTALL_FAKE, {'seq': [0, 3, 4, 4], 'delay': 30, 'code': 0})
        r = page_sdk.evaluate('async () => await G.ads.watch("seq_ok")')
        settles = page_sdk.evaluate("() => (G.dbg.events || []).filter(e => e.type === 'ad_settle' && e.scene === 'seq_ok').length")
        check(r.get('success') is True and r.get('reason') == 'rewarded' and r.get('status') == 4 and
              r.get('technical') is False and settles == 1,
              '0→3→4（含重复 4）只成功结算一次', result=brief(r), settles=settles)

        page_sdk.evaluate(INSTALL_FAKE, {'seq': [0, 3, 1], 'delay': 30, 'code': 0})
        r = page_sdk.evaluate('async () => await G.ads.watch("seq_closed")')
        check(r.get('success') is False and r.get('reason') == 'closed' and r.get('status') == 1 and
              r.get('technical') is False, '0→3→1 返回 closed/technical=false', result=brief(r))

        # 只来 status=0：过程态不能提前结算；用 timeoutMs 参数把 120 s 缩到 0.6 s。
        page_sdk.evaluate(INSTALL_FAKE, {'seq': [0], 'delay': 30, 'code': 0})
        ev = page_sdk.evaluate("""async () => {
          const t0 = performance.now();
          const p = G.ads.watch('seq_stall', { timeoutMs: 600 });
          const busy = G.ads.busy;
          const result = await p;
          return { result, busy, elapsed: performance.now() - t0, after: G.ads.busy };
        }""")
        check(ev['busy'] is True, '只收到 status=0 时仍在等待（busy=true）')
        check(ev['result'].get('reason') == 'timeout' and ev['result'].get('technical') is True,
              'status=0 不提前结算，最终 timeout', result=brief(ev['result']), elapsed=round(ev['elapsed']))
        check(ev['elapsed'] >= 500 and ev['elapsed'] < 3000,
              'timeoutMs 参数生效（约 600 ms，而不是 120 s）', elapsed=round(ev['elapsed']))
        check(ev['after'] is False, 'timeout 后 busy 复位')

        # 播放期间 busy + 第一次照常成功
        page_sdk.evaluate(INSTALL_FAKE, {'seq': [4], 'delay': 300, 'code': 0})
        ev = page_sdk.evaluate("""async () => {
          const p = G.ads.watch('fake_busy');
          const during = G.ads.busy;
          const second = await G.ads.watch('fake_busy_second');
          const first = await p;
          return { during, second, first, after: G.ads.busy };
        }""")
        check(ev['during'] is True and ev['second'].get('reason') == 'busy',
              '真 SDK 播放中再 watch 返回 busy', second=brief(ev['second']))
        check(ev['first'].get('success') is True and ev['after'] is False,
              '真 SDK 播放完成后的结果和 busy 复位', first=brief(ev['first']))

        # showAd 抛异常
        page_sdk.evaluate("() => { window.MetaH5Ad = { showAd: function () { throw new Error('boom'); } }; }")
        r = page_sdk.evaluate('async () => await G.ads.watch("boom")')
        check(r.get('reason') == 'exception' and r.get('technical') is True,
              'showAd 抛异常返回 exception/technical=true', result=brief(r))

        # code != 0 是失败
        page_sdk.evaluate(INSTALL_FAKE, {'seq': [0], 'delay': 10, 'code': 7})
        r = page_sdk.evaluate('async () => await G.ads.watch("code_fail")')
        check(r.get('reason') == 'failed' and r.get('technical') is True,
              'code!=0 返回 failed/technical=true', result=brief(r))

        # ---- supported()：SDK 正常 / 不支持 / 3 秒不回调 ----
        page_sdk.evaluate("() => { window.MetaH5Ad = { isAdSupport: function (t, cb) { cb({ code: 0, data: 1 }); } }; }")
        check(page_sdk.evaluate('() => G.ads.supported()') is True, 'SDK 返回 code=0/data=1 时 supported()=true')
        page_sdk.evaluate("() => { window.MetaH5Ad.isAdSupport = function (t, cb) { cb({ code: 0, data: 0 }); }; }")
        check(page_sdk.evaluate('() => G.ads.supported()') is False, 'SDK 返回 data=0 时 supported()=false')
        page_sdk.evaluate("() => { window.MetaH5Ad.isAdSupport = function () {}; }")
        t0 = time.monotonic()
        supported = page_sdk.evaluate('() => G.ads.supported()')
        elapsed = time.monotonic() - t0
        check(supported is False and 2.8 <= elapsed < 5,
              'isAdSupport 不回调时 3 秒后回 false', supported=supported, elapsed=round(elapsed, 3))

        for e in page_errors:
            check(False, '页面未捕获异常', error=e)
        browser.close()

    bad = [c for c in checks if not c['ok']]
    res = {'ok': not bad, 'url': base, 'checks': checks, 'pageErrors': page_errors}
    (out / 'result.json').write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': res['ok'], 'pass': len(checks) - len(bad), 'fail': len(bad), 'out': str(out)},
                     ensure_ascii=False), flush=True)
    return 0 if res['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
