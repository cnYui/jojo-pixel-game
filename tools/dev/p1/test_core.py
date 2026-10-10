"""包 1 自测（技术约定 §7.1）：Playwright 无头 Chromium 打开 tools\\dev\\p1\\_gen\\test_page.html
（= index.html 原样 + 包 1 的引擎文件 + tools\\dev\\p1\\stubs.js 里别的包的桩）。

    python -B tools\\dev\\p1\\test_core.py                 # 全部（core / audio / touch）
    python -B tools\\dev\\p1\\test_core.py --part touch    # 只跑触屏部分（规划写的 touchtest 就是这个）
    python -B tools\\dev\\p1\\test_core.py --real          # 集成后：用真的 index.html 跑触屏 DOM / 输入检查（需要 data_meta.js、main.js 都在）
    python -B tools\\dev\\p1\\test_core.py --headed        # 开窗口看

输出：tools\\dev\\p1\\_out\\test_core.json + 截图 *.png；控制台 warning / error / pageerror 一条都不许有（故意制造的那一条除外）。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
GAME = HERE.parents[2]
SRC = GAME.parent / '源码'
OUT = HERE / '_out'
PAGE = HERE / '_gen' / 'test_page.html'
EXPECTED_ERR = 'p1-expected-loop-error'

results = []
console_bad = []


def check(name, ok, detail=''):
    results.append({'name': name, 'ok': bool(ok), 'detail': detail})
    print(('  ok   ' if ok else '  FAIL ') + name + (('  — ' + str(detail)) if detail != '' else ''), flush=True)


def watch(page, tag):
    def on_console(m):
        if m.type in ('warning', 'error'):
            console_bad.append({'page': tag, 'type': m.type, 'text': m.text})

    def on_err(e):
        txt = str(e)
        if EXPECTED_ERR in txt:
            results.append({'name': 'expected-error-seen', 'ok': True, 'detail': ''})
            return
        console_bad.append({'page': tag, 'type': 'pageerror', 'text': txt})
    page.on('console', on_console)
    page.on('pageerror', on_err)


def open_page(ctx, tag, query=''):
    page = ctx.new_page()
    watch(page, tag)
    page.goto(PAGE.as_uri() + query)
    page.wait_for_function('window.__p1ready === true', timeout=30000)
    return page


JS_TICK = '(n) => { G.dbg.tick(n); }'


def tick(page, n=1):
    page.evaluate(JS_TICK, n)


# ================================================================ core
def py_ref():
    """源码 engine/core.py 的 hash01 / ease，作对照（只读 import）。"""
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from engine import core  # noqa: E402
    vecs = [[1], [3, 7], [12345, 7, 1], [0.37], [-5, 2], [1.5, 2.25, 9], [40, 7, 2], [2 ** 31 + 5, 3]]
    hashes = [core.hash01(*v) for v in vecs]
    kinds = ['linear', 'in', 'out', 'io', 'in3', 'out3', 'back', 'bounce', 'elastic', 'step']
    us = [0.0, 0.13, 0.5, 0.77, 1.0]
    eases = {k: [core.ease(u, k) for u in us] for k in kinds}
    noise = [core.noise1(x, s) for x, s in [(0.3, 0), (5.7, 3), (-2.2, 1)]]
    kv = core.keys(0.75, [(0, 0.0), (0.5, 10.0), (1.0, 30.0)])
    return vecs, hashes, kinds, us, eases, noise, kv


def test_core(browser, shots):
    print('[core] 画布 / 时钟 / 输入 / 资源')
    ctx = browser.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
    page = open_page(ctx, 'core', '?touch=0')

    # ---- 1. 缩放：四个视口
    for (w, h, bw, bh, cw, ch) in [(1280, 720, 1280, 720, 1280, 720), (1366, 657, 960, 540, 960, 540),
                                   (640, 360, 640, 360, 640, 360), (500, 300, 640, 360, 500, 281.25)]:
        page.set_viewport_size({'width': w, 'height': h})
        page.wait_for_timeout(120)
        r = page.evaluate('() => ({ w: G.screen.width, h: G.screen.height, s: G.scale, cw: parseFloat(G.screen.style.width), ch: parseFloat(G.screen.style.height) })')
        check(f'缩放 {w}×{h} → 位图 {bw}×{bh}', r['w'] == bw and r['h'] == bh and abs(r['cw'] - cw) < 0.01 and abs(r['ch'] - ch) < 0.01, r)
    page.set_viewport_size({'width': 1280, 'height': 720})
    page.wait_for_timeout(120)

    # ---- 2. 清晰度：s=4 时世界层 1 像素 = 4×4 屏幕像素，棋盘格边界只在 32 的倍数上
    r = page.evaluate('''() => {
        G.cam.x = 0; G.cam.y = 0; G.cam.zoom = null; G.cam.shakeT = G.cam.shakeDur; G.cam.bumpT = G.cam.bumpDur;
        G.testScene.marker = null; G.dbg.tick(1);
        const c = G.mkCanvas(G.screen.width, G.screen.height, true); c.g.drawImage(G.screen, 0, 0);
        const d = c.g.getImageData(0, 0, c.width, c.height).data, W = c.width;
        const bad = [];
        for (const y of [5, 101, 333]) {
          let prev = -1;
          for (let x = 0; x < W; x++) { const i = (y * W + x) * 4, v = d[i] * 65536 + d[i + 1] * 256 + d[i + 2];
            if (prev >= 0 && v !== prev && x % 32 !== 0) bad.push([x, y]); prev = v; }
        }
        return { bad: bad.slice(0, 5), n: bad.length };
    }''')
    check('清晰：s=4 时棋盘格只在 32 px 边界换色（最近邻、无平滑）', r['n'] == 0, r)
    page.screenshot(path=str(OUT / 'core_1280x720.png'))
    shots.append('core_1280x720.png')

    # ---- 3. w2u：推近 2 倍 + 震屏时，世界里一个像素在屏幕上的位置 = w2u 算的位置
    r = page.evaluate('''() => {
        G.cam.x = 100; G.cam.y = 0; G.cam.zoom = { k: 2, x: 260, y: 100 };
        G.shake(3, 100, { decay: false });
        G.testScene.marker = { sx: 150, sy: 95 };          // 世界坐标 (250, 95)
        G.dbg.tick(1);
        const u = G.cam.w2u(250, 95, 0), b = G.cam.box(), s = G.scale;
        const c = G.mkCanvas(G.screen.width, G.screen.height, true); c.g.drawImage(G.screen, 0, 0);
        const d = c.g.getImageData(0, 0, c.width, c.height).data, W = c.width, H = c.height;
        let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const i = (y * W + x) * 4;
          if (d[i] > 200 && d[i + 1] < 40 && d[i + 2] < 40) { if (x < x0) x0 = x; if (y < y0) y0 = y; if (x > x1) x1 = x; if (y > y1) y1 = y; } }
        const k = 320 / b.w;
        const res = { u, b, s, k, found: [x0, y0, x1, y1], want: [u.x * s / 2, u.y * s / 2, k * s] };
        G.cam.zoom = null; G.cam.shakeT = G.cam.shakeDur; G.cam.x = 0; G.testScene.marker = null;
        return res;
    }''')
    fx0, fy0, fx1, fy1 = r['found']
    wx, wy, ww = r['want']
    check('w2u：推近 2 倍 + 震屏 3 时像素落点一致', abs(fx0 - wx) <= 1 and abs(fy0 - wy) <= 1 and abs((fx1 - fx0 + 1) - ww) <= 1, r)

    # ---- 4. 全局顿帧 0.3 s 期间按 J，顿帧结束后 take('attack', 0.25) 仍为真
    page.evaluate('() => { G.input.clear(); G.dbg.tick(2); G.hitStopAll(0.3); G.dbg.tick(5); window.__w0 = G.clk.world; }')
    page.keyboard.down('j')
    page.keyboard.up('j')
    r = page.evaluate('''() => { const w0 = window.__w0; G.dbg.tick(13); const frozen = Math.abs(G.clk.world - w0) < 1e-12;
        G.dbg.tick(1); return { frozen, hs: G.hitStopAll_t, take: G.input.take('attack', 0.25), dw: G.clk.world - w0 }; }''')
    check('顿帧 0.3 s 期间 world 时钟不走', r['frozen'], r)
    check('顿帧中按的 J：顿帧结束后 take(attack, 0.25) 为真（顿帧不吞键）', r['take'], r)
    # 对照：没有顿帧时按 J、过 0.3 s 世界时间，take(0.25) 应该为假
    page.keyboard.down('j')
    page.keyboard.up('j')
    r = page.evaluate('() => { G.dbg.tick(18); return G.input.take("attack", 0.25); }')
    check('对照：没有顿帧时 0.3 s 后 take(attack, 0.25) 为假', r is False, r)

    # ---- 5. 顿帧前 0.05 s 按 L，顿帧 0.1 s 结束后 clk.world − lastPress(guard) ≤ 0.1
    page.evaluate('() => { G.input.clear(); G.dbg.tick(1); }')
    page.keyboard.down('l')
    r = page.evaluate('''() => { G.dbg.tick(3); G.hitStopAll(0.1); G.dbg.tick(6); const frozen = G.hitStopAll_t; G.dbg.tick(1);
        return { d: G.clk.world - G.input.lastPress('guard'), down: G.input.isDown('guard'), frozen }; }''')
    page.keyboard.up('l')
    check('顿帧前 0.05 s 按 L：顿帧结束后 clk.world − lastPress(guard) ≤ 0.1（精准窗口不过期）', r['d'] <= 0.1 + 1e-9 and r['down'], r)

    # ---- 6. slowAll(0.3, 0.5)：clk.world 走得是 ui 的 0.3 倍，0.5 s 后恢复
    r = page.evaluate('''() => { G.dbg.tick(1); const u0 = G.clk.ui, w0 = G.clk.world; G.slowAll(0.3, 0.5); G.dbg.tick(15);
        const ratio = (G.clk.world - w0) / (G.clk.ui - u0); G.dbg.tick(16); const k = G.slowAllK;
        const w1 = G.clk.world; G.dbg.tick(1); return { ratio, k, after: (G.clk.world - w1) * 60 }; }''')
    check('slowAll(0.3, 0.5)：world / ui = 0.3', abs(r['ratio'] - 0.3) < 1e-6, r)
    check('slowAll 0.5 s（ui 时钟）后自动回 1', r['k'] == 1 and abs(r['after'] - 1) < 1e-6, r)

    # ---- 7. J 不触发 okHit；Enter 触发；lockOk(0.8) 期间 Enter 无效
    page.evaluate('''() => { window.__probe = []; G.testScene.probe = () => { const I = G.input;
        if (I.hit('attack') || I.hit('ok')) window.__probe.push({ t: G.clk.ui, atk: I.hit('attack'), ok: I.okHit(), mash: I.mashHit() }); }; }''')
    page.keyboard.press('j')
    tick(page, 1)
    page.keyboard.press('Enter')
    tick(page, 1)
    page.evaluate('() => { G.input.lockOk(0.8); G.dbg.tick(18); }')
    page.keyboard.press('Enter')
    tick(page, 1)
    page.evaluate('() => { G.dbg.tick(32); }')
    page.keyboard.press('Space')
    tick(page, 1)
    pr = page.evaluate('() => { G.testScene.probe = null; return window.__probe; }')
    ok = (len(pr) == 4 and pr[0]['atk'] and not pr[0]['ok'] and pr[0]['mash'] and pr[1]['ok']
          and not pr[2]['ok'] and pr[3]['ok'])
    check('J 不推进（okHit 假、mashHit 真）；Enter 推进；lockOk(0.8) 期间 Enter 无效、过后空格有效', ok, pr)

    # ---- 8. 组合键 chord / fresh（§4.3.3）
    r = page.evaluate('''() => { const I = G.input; I.clear(); G.dbg.tick(1);
        I.press('dodge', 't'); G.dbg.tick(2); const fresh1 = I.fresh('dodge'); I.press('attack', 't'); G.dbg.tick(1);
        const c1 = I.chord('dodge', 'attack'); const again = I.buffered('dodge') || I.buffered('attack');
        I.release('dodge', 't'); I.release('attack', 't'); I.press('dodge', 't'); G.dbg.tick(8); I.press('attack', 't'); G.dbg.tick(1);
        const c2 = I.chord('dodge', 'attack'); const fresh2 = I.fresh('attack', 4/60);
        I.release('dodge', 't'); I.release('attack', 't'); G.dbg.tick(1);
        return { fresh1, c1, again, c2, fresh2 }; }''')
    check('chord：相差 2/60 s 的 K+J 算组合键并消耗两个缓冲；相差 8/60 s 不算', r['fresh1'] and r['c1'] and not r['again'] and not r['c2'], r)

    # ---- 9. 按键日志 count、repeat 不算新按下
    r = page.evaluate('''() => { const I = G.input; I.clear(); G.dbg.tick(1);
        for (let i = 0; i < 5; i++) { I.press('attack', 't'); I.release('attack', 't'); G.dbg.tick(5); }
        return { c: I.count('attack', 1.0), c2: I.count('attack', 0.1) }; }''')
    check('按键日志：1 s 内 5 次、0.1 s 内 1 次', r['c'] == 5 and r['c2'] == 1, r)
    page.keyboard.down('k')
    page.evaluate('() => { G.dbg.tick(1); }')
    for _ in range(3):
        page.evaluate('''() => window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyK', key: 'k', repeat: true, cancelable: true }))''')
    page.evaluate('() => { G.dbg.tick(1); }')
    page.keyboard.up('k')
    r = page.evaluate('() => { G.dbg.tick(1); return G.input.count("dodge", 1.0); }')
    check('系统按键重复（e.repeat）不算新按下', r == 1, r)

    # ---- 10. G.wait：world 时钟顿帧时不走、ui 时钟照走；G.until；G.fade
    r = page.evaluate('''async () => { const fl = async () => { for (let i = 0; i < 3; i++) await new Promise((r) => setTimeout(r, 0)); };
        let a = false, b = false, c = false, f = false;
        G.wait(0.05).then(() => { a = true; }); G.wait(0.05, 'ui').then(() => { b = true; });
        G.hitStopAll(0.2); G.dbg.tick(6); await fl(); const mid = { a, b };
        G.dbg.tick(12); G.dbg.tick(4); await fl(); const end = { a, b };
        let flag = false; G.until(() => flag).then(() => { c = true; }); G.dbg.tick(2); await fl(); const c0 = c; flag = true; G.dbg.tick(1); await fl();
        G.fade(1, 0.2).then(() => { f = true; }); G.dbg.tick(11); await fl(); const f0 = f; G.dbg.tick(2); await fl();
        const fa = G.fadeA; G.fade(0, 0); return { mid, end, c0, c, f0, f, fa }; }''')
    check('G.wait 世界时钟：顿帧中不 resolve；ui 时钟照走', (not r['mid']['a']) and r['mid']['b'] and r['end']['a'], r)
    check('G.until / G.fade(1, 0.2) 按时 resolve', (not r['c0']) and r['c'] and (not r['f0']) and r['f'] and r['fa'] == 1, r)

    # ---- 11. 工具函数和 core.py 一致
    vecs, hashes, kinds, us, eases, noise, kv = py_ref()
    r = page.evaluate('''([vecs, kinds, us]) => ({
        h: vecs.map((v) => G.hash01(...v)), e: Object.fromEntries(kinds.map((k) => [k, us.map((u) => G.ease(u, k))])),
        n: [[0.3, 0], [5.7, 3], [-2.2, 1]].map(([x, s]) => G.noise1(x, s)),
        kv: G.keys(0.75, [[0, 0], [0.5, 10], [1, 30]]), tw: G.tw(0.5, 0, 1, 10, 20, 'linear'), st: G.stepped(0.26, 12),
        mix: G.mixHex('#000000', '#ffffff', 0.5), rgb: G.rgbOf('menace'), rgb2: G.rgbOf('#abc'),
        alias: [G.ease.out(0.5), G.ease.in(0.5), G.ease.outBack(0.5)] })''', [vecs, kinds, us])
    hok = all(abs(a - b) < 1e-12 for a, b in zip(r['h'], hashes))
    eok = all(abs(r['e'][k][i] - eases[k][i]) < 1e-9 for k in kinds for i in range(len(us)))
    nok = all(abs(a - b) < 1e-12 for a, b in zip(r['n'], noise))
    check('hash01 和 core.py 逐位一致（整数 / 非整数参数）', hok, {'js': r['h'], 'py': hashes})
    check('ease 10 种 / noise1 / keys 和 core.py 一致', eok and nok and abs(r['kv'] - kv) < 1e-9, {'kv': [r['kv'], kv]})
    check('tw / stepped / mixHex / rgbOf / 银魂别名', abs(r['tw'] - 15) < 1e-9 and abs(r['st'] - 3 / 12) < 1e-12 and r['mix'] == '#808080'
          and r['rgb'] == [170, 60, 220] and r['rgb2'] == [170, 187, 204] and abs(r['alias'][0] - 0.875) < 1e-9
          and abs(r['alias'][1] - 0.125) < 1e-9, r)

    # ---- 12. 资源：loadScript / loadPack / preloadPack / G.pix / 缺图
    r = page.evaluate('''async () => {
        await G.res.preloadPack('core');
        const red = G.pix('test/core_red');
        const p1 = G.res.loadScript('tools/dev/p1/_gen/img_bg_p1test.js'), p2 = G.res.loadScript('tools/dev/p1/_gen/img_bg_p1test.js');
        await p1; const same = p1 === p2;
        await G.res.loadPack('bg_p1test');
        const a = G.image('bg/p1test/a'), pa = G.pix('bg/p1test/a'), pb = G.pix('bg/p1test/b');
        const miss = G.image('nope/none'); const inMiss = G.dbg.missingImg.has('nope/none'); G.dbg.missingImg.delete('nope/none');
        let threw = false; try { await G.res.loadScript('tools/dev/p1/_gen/does_not_exist.js'); } catch (e) { threw = true; }
        return { red: red && red.u32[0] >>> 0, same, loaded: G.res.loaded('bg_p1test'), ready: G.ready(a),
                 pa: pa && [pa.w, pa.h, pa.u32[0] >>> 0], pb: pb && (pb.u32[0] >>> 0), miss, inMiss, threw,
                 keys: G.D.packKeys.bg_p1test }; }''')
    check('preloadPack(core) + G.pix 读出 0xff0000ff', r['red'] == 0xff0000ff, r)
    check('loadScript 同 src 只插一次、loadPack 按需加载并解码', r['same'] and r['loaded'] and r['ready'] and r['pa'] == [6, 3, 0xff1ec80a] and r['pb'] == 0x80ff0000, r)
    check('缺图返回 null 并记 missingImg；脚本加载失败 reject', r['miss'] is None and r['inMiss'] and r['threw'], r)
    # 那次故意的 404 浏览器会打一条 “Failed to load resource”——是测试自己造的，从报错名单里去掉
    for c in list(console_bad):
        if 'does_not_exist.js' in c['text'] or ('Failed to load resource' in c['text'] and c['page'] == 'core'):
            console_bad.remove(c)

    # ---- 13. 像素会话 + 钩子顺序 + willReadFrequently（反复读世界层像素不该有警告）
    r = page.evaluate('''() => { G.fx.on = true; G.post.on = true; G.fx.calls = { mid: 0, over: 0 }; G.post.calls = { mid: 0, final: 0 };
        G.dbg.tick(1); for (let i = 0; i < 30; i++) G.dbg.tick(1);
        for (let i = 0; i < 20; i++) { G.pix('test/core_grad'); }
        const d = G.wg.getImageData(3, 3, 1, 1).data;
        const r = { fx: G.fx.calls, post: G.post.calls, inv: [d[0], d[1], d[2]] };
        G.fx.on = false; G.post.on = false; return r; }''')
    check('render：像素会话 mid → over → final 每帧各一次，特效画进世界层', r['fx']['mid'] == 31 and r['fx']['over'] == 31 and r['post']['mid'] == 31
          and r['post']['final'] == 31 and r['inv'][0] > 150, r)

    # ---- 14. 场景钩子：hasOver / drawOver / drawTop / drawScreen / 闪色 / 黑幕
    r = page.evaluate('''() => { const calls = [];
        const sc = Object.assign({}, G.testScene, { hasOver: () => true, drawOver: (g) => calls.push('over'), drawTop: (g) => calls.push('top'),
          drawPixel: (P, l) => calls.push('px:' + l) });
        G.fx.calls = { mid: 0, over: 0 }; G.post.calls = { mid: 0, final: 0 };
        G.setScene(sc); G.dbg.tick(1); G.setScene(G.testScene);
        const fxc = Object.assign({}, G.fx.calls), postc = Object.assign({}, G.post.calls);
        const vid = { name: 'video', drawScreen: (s, w, h) => { calls.push('screen:' + w + 'x' + h); s.fillStyle = '#00ff00'; s.fillRect(0, 0, w, h); } };
        G.setScene(vid); G.dbg.tick(1);
        const c = G.mkCanvas(G.screen.width, G.screen.height, true); c.g.drawImage(G.screen, 0, 0); const px = c.g.getImageData(640, 360, 1, 1).data;
        G.setScene(G.testScene);
        G.flash(0.25, 1, '#ffffff'); G.dbg.tick(1); const fa = G.flashA; G.dbg.tick(20); const fb = G.flashA;
        return { calls, fx: fxc, post: postc, green: [px[0], px[1], px[2]], fa, fb }; }''')
    want = ['px:mid', 'over', 'top', 'screen:1280x720']
    check('时停 over pass：drawPixel(mid) → drawOver → over 层特效 / final 各一次；drawTop；视频 drawScreen 铺满', r['calls'] == want
          and r['fx'] == {'mid': 1, 'over': 1} and r['post'] == {'mid': 1, 'final': 1} and r['green'][1] > 200 and r['fa'] > 0.8 and r['fb'] == 0, r)

    # ---- 15. 主循环出错：同一条只报一次、循环不停
    r = page.evaluate('''async () => { let n = 0; const sc = Object.assign({}, G.testScene, { update() { n++; throw new Error('p1-expected-loop-error'); } });
        G.setScene(sc); G.dbg.hold = false; await new Promise((r) => setTimeout(r, 400)); G.dbg.hold = true; G.setScene(G.testScene);
        return { n, ev: G.dbg.counts.loop_error || 0 }; }''')
    page.wait_for_timeout(100)
    seen = sum(1 for x in results if x['name'] == 'expected-error-seen')
    check('主循环异常：循环照走（多步都执行了）、只往外抛一次', r['n'] > 5 and seen == 1, {'steps': r['n'], 'thrown': seen})

    # ---- 16. 实时跑 1.5 s：帧率、ui 时钟
    r = page.evaluate('''async () => { const u0 = G.clk.ui; G.dbg.hold = false; await new Promise((r) => setTimeout(r, 1500)); G.dbg.hold = true;
        return { du: G.clk.ui - u0, fps: G.dbg.fps }; }''')
    check('实时主循环：1.5 s 内 ui 时钟走了约 1.5 s、fps 统计在更新', 1.2 < r['du'] < 1.8 and r['fps']['avg'] > 20, r)

    # ---- 17. 设置 / 存储
    r = page.evaluate('''() => { const keys = Object.keys(G.settings); G.settings.musicVol = 0.5; G.settings.save();
        const raw = localStorage.getItem('jojo-settings'); G.store.set('p1-test', { a: 1 });
        const back = G.store.get('p1-test', null); localStorage.removeItem('jojo-p1-test'); G.settings.musicVol = 0.8; G.settings.save();
        return { keys, raw: JSON.parse(raw), back, def: G.store.get('none-such', 42) }; }''')
    check('settings 字段齐全、save 写 jojo-settings；store 前缀 jojo-、读不到给默认值',
          r['keys'] == ['reduceFlash', 'musicVol', 'sfxVol', 'grunts', 'mashHold', 'touchSize'] and r['raw']['musicVol'] == 0.5
          and r['back'] == {'a': 1} and r['def'] == 42, r)
    ctx.close()


# ================================================================ audio
def test_audio(browser, shots):
    print('[audio] 解码 / 播放 / 循环 / 时停 / 压低 / 内存')
    ctx = browser.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
    page = open_page(ctx, 'audio', '?touch=0&audioinit=1')
    # ---- 1. 解锁前请求音乐：先解码、挂起；unlock 后补放
    r = page.evaluate('''async () => { const A = G.audio; const ctx0 = !!A.ctx, act0 = window.__p1act;
        await A.music('daily', { fade: 0.05 }); const before = A.current(); A.unlock();
        await new Promise((r) => setTimeout(r, 200)); return { ctx0, act0, before, after: A.current(), unlocked: A.unlocked, state: A.ctx && A.ctx.state,
          sr: A.ctx && A.ctx.sampleRate }; }''')
    check('载入时（没有用户手势）init：不建 AudioContext（只建离线解码上下文，免得 Chrome 打“not allowed to start”警告）', r['ctx0'] is False and r['act0'] is False, r)
    check('解锁前 music() 挂起、unlock() 后补放', r['before'] is None and r['after'] and r['after']['name'] == 'daily' and r['unlocked'], r)
    check('AudioContext 44100 Hz', r['sr'] == 44100, r)

    # ---- 2. 解码全部音效，长度 = 原样本数
    r = page.evaluate('''async () => { const A = G.audio; const t0 = performance.now(); let prog = 0;
        await A.loadSfx((d, n) => { prog = d / n; }); const ms = performance.now() - t0;
        const sm = G.D.audio.sfx, names = Object.keys(sm);
        const diff = names.map((n) => { const i = A.info(n); return [n, i ? i.length - sm[n].samples : null, sm[n].loop, i && i.loopStart]; });
        const missing = diff.filter((d) => d[1] === null).map((d) => d[0]);
        const loopBad = diff.filter((d) => d[2] && (d[1] !== 0 || d[3] !== 0));
        const tail = diff.filter((d) => !d[2] && d[1] !== 0);
        const left = Object.keys(window.JOJO_AUDIO.sfx).length;
        return { n: names.length, missing, loopBad, tail, ms: Math.round(ms), prog, left }; }''')
    tail_ok = all(0 < d[1] <= 16 for d in r['tail'])
    check(f'解码全部 {r["n"]} 个音效、解码完删 base64', r['n'] >= 122 and not r['missing'] and r['prog'] == 1 and r['left'] == 0, {'ms': r['ms'], 'missing': r['missing']})
    check('循环音效解码长度 = samples、循环起点 0（无缝）；一次性音效最多多出 16 个样本（尾部）', not r['loopBad'] and tail_ok, {'loopBad': r['loopBad'], 'tail': r['tail']})
    # 循环点规则：多出 2–9 个样本不算“没认 gapless 头”；多出一个编码延迟才跳过开头
    r = page.evaluate('''() => { const ctx = G.audio.ctx, m = { samples: 44100, encDelay: 1105 };
        return [0, 9, 1105, 1105 + 600].map((extra) => { const lp = G.audio.loopPoints(ctx.createBuffer(2, 44100 + extra, 44100), m);
          return [extra, Math.round(lp.s * 44100), Math.round(lp.e * 44100)]; }); }''')
    check('循环点规则：多 0 / 9 个样本 → 0..samples；多一个编码延迟（1105 / 1705）→ 跳过开头 1105', r == [[0, 0, 44100], [9, 0, 44100], [1105, 1105, 45205], [1705, 1105, 45205]], r)

    # ---- 3. 每首配乐解码长度 = samples；解码 6 首后 mem ≤ 80 MB；LRU 最多 5 首
    r = page.evaluate('''async () => { const A = G.audio, mm = G.D.audio.music; const out = {}; let mem6 = null; let k = 0;
        for (const n of Object.keys(mm)) { if (mm[n].stream) continue; const t0 = performance.now(); await A.prefetch([n]);
          const i = A.info(n); out[n] = [i && i.length, mm[n].samples, Math.round(performance.now() - t0), i && i.loopEnd];
          k++; if (k === 6) mem6 = A.mem(); }
        return { out, mem6, memEnd: A.mem(), base64Left: Object.keys(window.JOJO_AUDIO.music) }; }''')
    bad = {k: v for k, v in r['out'].items() if v[0] != v[1]}
    check(f'{len(r["out"])} 首配乐解码长度 = samples、循环点 = 全长', not bad and all(abs(v[3] - v[1] / 44100) < 1e-6 for v in r['out'].values()), r['out'])
    check('解码 6 首配乐后 mem().pcmMB ≤ 80、同时最多 5 首', r['mem6']['pcmMB'] <= 80 and len(r['mem6']['tracks']) <= 5
          and len(r['memEnd']['tracks']) <= 5, {'mem6': r['mem6'], 'memEnd': r['memEnd']})
    check('配乐解码完立刻删 base64', not r['base64Left'], r['base64Left'])

    # ---- 4. 播放有声音（AnalyserNode 接在 musicOut 上读 RMS）：普通配乐 + 标题曲流式
    r = page.evaluate('''async () => { const A = G.audio; G.dbg.hold = false;
        const an = A.ctx.createAnalyser(); an.fftSize = 2048; A.musicOut.connect(an); const buf = new Float32Array(2048);
        const rms = async (ms) => { let best = 0; const t0 = performance.now(); while (performance.now() - t0 < ms) {
          an.getFloatTimeDomainData(buf); let s = 0; for (const v of buf) s += v * v; best = Math.max(best, Math.sqrt(s / buf.length));
          await new Promise((r) => setTimeout(r, 30)); } return best; };
        await A.music('battle', { fade: 0.05 }); await new Promise((r) => setTimeout(r, 300)); const rBattle = await rms(500);
        const b1 = A.beat(); await A.music('battle'); await new Promise((r) => setTimeout(r, 200)); const b2 = A.beat();
        const t0 = performance.now(); await A.music('title_song', { fade: 0.05 }); const tLoad = performance.now() - t0;
        await new Promise((r) => setTimeout(r, 800)); const rTitle = await rms(900); const cur = A.current();
        const memT = A.mem(); A.stopMusic(0.1); await new Promise((r) => setTimeout(r, 300)); const rStop = await rms(300);
        an.disconnect(); return { rBattle, rTitle, rStop, cur, b1, b2, tLoad: Math.round(tLoad), memT, el: A.current() }; }''')
    check('普通配乐（AudioBuffer）有声音：RMS > 0.05', r['rBattle'] > 0.05, round(r['rBattle'], 3))
    check('同名音乐不重开（播放位置继续走）', r['b2']['t'] > r['b1']['t'] and r['b1']['beat'] > 0, {'b1': r['b1'], 'b2': r['b2']})
    check('标题曲流式（<audio> → WebAudio）有声音：RMS > 0.05，且不占 PCM', r['rTitle'] > 0.05 and r['cur']['kind'] == 'stream'
          and 'title_song' not in r['memT']['tracks'], {'rms': round(r['rTitle'], 3), 'cur': r['cur'], 'mem': r['memT'], 'load_ms': r['tLoad']})
    check('stopMusic 后静音', r['rStop'] < 0.01, round(r['rStop'], 4))

    # ---- 5. 音效 API：变体组、缺名、喊声开关、cue、时停、loop、duck、releaseExcept、voice
    r = page.evaluate('''async () => { const A = G.audio; const s1 = A.sfx('punch', { seed: 1 }), s6 = A.sfx('punch', { seed: 6 }), sr = A.sfx('punch');
        const miss = A.sfx('no_such_sfx'); const inMiss = G.dbg.missingSfx.has('no_such_sfx'); G.dbg.missingSfx.delete('no_such_sfx');
        const g0 = A.sfx('grunt_jotaro'), g1 = A.sfx('grunt_jotaro', { force: true }), ov = A.sfx('ora_voice');
        G.settings.grunts = true; const g2 = A.sfx('grunt_kakyoin'); G.settings.grunts = false;
        const compat = A.sfx('whoosh', 0.5, 1.2); const ui = []; for (let i = 0; i < 8; i++) ui.push(A.sfx('menu_move'));
        const many = []; for (let i = 0; i < 7; i++) many.push(A.sfx('punch0'));
        const manyLive = many.map((h) => !h.ended);
        const c1 = A.cue('timestop', { vol: 0.2 }), c2 = A.cue('timestop', { rate: 2, vol: 0.2 }), c3 = A.cue('timestop_sp', { vol: 0.2 }), c4 = A.cue('sting_reveal', { vol: 0.2 });
        await A.music('tension', { fade: 0.05 }); await new Promise((r) => setTimeout(r, 200));
        A.timeStop(true); const ts1 = A.sfx('punch0').rate, tsUi = A.sfx('menu_move').rate; await new Promise((r) => setTimeout(r, 900));
        A.timeStop(false); const ts2 = A.sfx('punch0').rate; await new Promise((r) => setTimeout(r, 300));
        const lp = A.loop('ora_loop', { vol: 0.4, fade: 0.05 }); await new Promise((r) => setTimeout(r, 400)); lp.setRate(1.1); lp.stop(0.1);
        const fl = A.loop('fire_loop', { x: 300 }); fl.stop(); const dm = A.loop('nope_loop'); G.dbg.missingSfx.delete('nope_loop');
        A.duck(0.35, 0.3); await new Promise((r) => setTimeout(r, 100)); const dk = A.duckGain.gain.value; await new Promise((r) => setTimeout(r, 600));
        const dk2 = A.duckGain.gain.value; A.duck(0.5, Infinity); A.duck(false);
        A.lowpass(800); A.lowpass(null); A.setRate(1.06); A.setRate(1); A.lowHp(true); A.lowHp(false);
        const memB = A.mem(); A.releaseExcept(['battle']); const memA = A.mem();
        return { s1: s1 && s1.name, s6: s6 && s6.name, sr: sr && sr.name, miss, inMiss, g0, g1: g1 && g1.name, ov, g2: g2 && g2.name,
          compat: compat && [compat.name, compat.rate], ui: ui.filter(Boolean).length, many: manyLive,
          c1: c1.hitIn, c2: c2.hitIn, c3: c3.hitIn, c4: c4.hitIn, ts1, tsUi, ts2, dm: !!dm.dummy, dk, dk2,
          memB, memA, voice: [A.voice('jotaro'), A.voice('holly'), A.voice('npc_x'), A.voice(330)], cur: A.current() }; }''')
    check("sfx('punch', {seed:1}) = punch1、seed 6 → punch2、不给 seed 随机挑组里的", r['s1'] == 'punch1' and r['s6'] == 'punch2' and (r['sr'] or '').startswith('punch'), r)
    check('缺名 → null + missingSfx', r['miss'] is None and r['inMiss'], r)
    check('喊声默认关：grunt / ora_voice 不播；force 或 settings.grunts 开着才播', r['g0'] is None and r['ov'] is None and r['g1'] == 'grunt_jotaro' and r['g2'] == 'grunt_kakyoin', r)
    check('兼容写法 sfx(name, vol, rate)；UI 音不限并发；同名最多 4 个（第 5 个起掐最老的）', r['compat'] == ['whoosh', 1.2] and r['ui'] == 8
          and r['many'] == [False, False, False, True, True, True, True], {'compat': r['compat'], 'ui': r['ui'], 'many': r['many']})
    check('cue 的 hitIn = hit / rate（timestop 0.85、rate 2 → 0.425、timestop_sp 0.924、sting_reveal 0.26）',
          abs(r['c1'] - 0.85) < 1e-6 and abs(r['c2'] - 0.425) < 1e-6 and abs(r['c3'] - 0.924) < 2e-3 and abs(r['c4'] - 0.26) < 1e-6, r)
    check('时停中音效 rate ×0.9（UI 音不变），结束后复原', abs(r['ts1'] - 0.9) < 1e-9 and r['tsUi'] == 1 and r['ts2'] == 1, r)
    check('duck(0.35, 0.3) 压下去、0.3 s（ui 时钟）后回来；缺的循环音效给空 handle', r['dk'] < 0.5 and r['dk2'] > 0.95 and r['dm'], r)
    check('releaseExcept：只留 keep 和正在播的', set(r['memA']['tracks']) <= {'battle', r['cur']['name'] if r['cur'] else ''}, {'before': r['memB'], 'after': r['memA']})
    check('voice：blipHz / 660（jotaro 440、holly 800、没有的 600、直接给 Hz）', [round(v, 6) for v in r['voice']] == [round(440 / 660, 6), round(800 / 660, 6), round(600 / 660, 6), 0.5], r['voice'])

    # ---- 6. 释放后再放：重新插 <script> 加载（again）
    r = page.evaluate('''async () => { const A = G.audio; A.stopMusic(0.05); await new Promise((r) => setTimeout(r, 200)); A.releaseExcept([]);
        const m0 = A.mem(); await A.music('sad', { fade: 0.05 }); await new Promise((r) => setTimeout(r, 200));
        const c = A.current(); A.stopMusic(0.05); await new Promise((r) => setTimeout(r, 300)); A.releaseExcept([]);
        await A.music('sad', { fade: 0.05 }); const c2 = A.current(); A.stopMusic(0.05);
        await A.music('title_song', { fade: 0.05 }); await new Promise((r) => setTimeout(r, 300)); const c3 = A.current();
        A.stopMusic(0.05); await new Promise((r) => setTimeout(r, 200)); G.dbg.hold = true;
        return { m0, c, c2, c3, m1: A.mem() }; }''')
    check('释放后再 music()：重新加载解码照常播；标题曲第二次直接用留着的 Blob', r['c'] and r['c']['name'] == 'sad' and r['c2'] and r['c2']['name'] == 'sad'
          and r['c3'] and r['c3']['kind'] == 'stream', r)
    ctx.close()


# ================================================================ touch
TOUCH_SIZES = [(844, 390), (640, 360), (1024, 768), (667, 375), (915, 412)]
SHOW = {   # 技术约定 §4.3.5 的表（u / swap 的动态规则单独测）
    'explore': {'pad': 1, 'j': 0.6, 'k': 0, 'l': 0, 'u': 1, 'e': 1, 'swap': 1, 'pause': 1},
    'combat': {'pad': 1, 'j': 1, 'k': 1, 'l': 1, 'u': 0.4, 'e': 0.4, 'swap': 0, 'pause': 1},
    'menu': {'pad': 1, 'j': 0, 'k': 0, 'l': 0, 'u': 0, 'e': 1, 'swap': 0, 'pause': 1},
    'qte': {'pad': 0, 'j': 1, 'k': 0, 'l': 0, 'u': 0, 'e': 1, 'swap': 0, 'pause': 1},
    'story': {'pad': 0, 'j': 0, 'k': 0, 'l': 0, 'u': 0, 'e': 0, 'swap': 0, 'pause': 1},
    'title': {'pad': 1, 'j': 0, 'k': 0, 'l': 0, 'u': 0, 'e': 1, 'swap': 0, 'pause': 0},
    'end': {'pad': 0, 'j': 0, 'k': 0, 'l': 0, 'u': 0, 'e': 0, 'swap': 0, 'pause': 0},
}
JS_SETCTX = '''(c) => { const U = G.ui, W = G.world; U.dlg = U.menu = U.qte = U.choiceBox = null; W.combat = false; W.fight = null; W.near = null;
    W.player.energy = 0; G.party._ready = true; G.party._swap = true; W._look = null;
    if (c === 'title' || c === 'end' || c === 'video') G.setScene({ name: c, mode: 'main' }); else G.setScene(G.testScene);
    if (c === 'menu') U.menu = { items: [] }; if (c === 'qte') U.qte = { type: 'mash', need: 999, m: 0, t: 0, state: 'run', res() {} };
    if (c === 'story') U.dlg = { text: 'x', t: 0, shown: 0, all: false, pages: 1, page: 0, res() {} };
    if (c === 'combat') W.combat = true; }'''
JS_READ = '''() => { const v = (sel) => { const e = document.querySelector(sel); if (!e) return null; return e.classList.contains('tc-off') ? 0 :
      e.classList.contains('tc-dim') ? 'dim' : 1; };
    const sel = { pad: '#tc-pad', j: '.tc-j', k: '.tc-k', l: '.tc-l', u: '.tc-u', e: '.tc-e', swap: '#tc-swap', pause: '#tc-pause' };
    const o = {}; for (const k in sel) o[k] = v(sel[k]);
    o._ctx = G.touch.ctx; o._uReady = document.querySelector('.tc-u').classList.contains('ready');
    o._uGold = document.querySelector('.tc-u').classList.contains('gold'); o._ePulse = document.querySelector('.tc-e').classList.contains('pulse');
    o._uCaption = document.querySelector('.tc-u i').textContent;
    return o; }'''


def center(page, sel):
    b = page.locator(sel).bounding_box()
    return b['x'] + b['width'] / 2, b['y'] + b['height'] / 2


def test_touch(browser, shots):
    print('[touch] 844×390 手机视口：U / 换人钮、显隐、按下写进 G.input、点屏推进、QTE 后狂点不跳台词')
    ctx = browser.new_context(viewport={'width': 844, 'height': 390}, has_touch=True, is_mobile=True, device_scale_factor=1)
    page = open_page(ctx, 'touch')
    r = page.evaluate('''() => ({ on: G.touch.on, body: document.body.classList.contains('tc-on'), u: !!document.querySelector('.tc-u[data-key=special]'),
        swap: !!document.querySelector('#tc-swap[data-key=swap]'), k: document.querySelector('.tc-k').dataset.key, kTxt: document.querySelector('.tc-k i').textContent,
        safe: G.touch.safe, s: G.scale, susp: G.suspended })''')
    check('手机视口自动开触屏；U 钮（special）、换人钮（swap）存在；K = 闪避', r['on'] and r['body'] and r['u'] and r['swap'] and r['k'] == 'dodge' and r['kTxt'] == '闪避', r)
    sf = r['safe']
    check('G.touch.safe 是 UI 坐标（l < r ≤ 640、0 < top < 360、sys < 640）', 0 < sf['l'] < sf['r'] <= 640 and 0 < sf['top'] < 360 and 0 < sf['sys'] < 640, sf)

    # ---- 显隐：七种场景
    for c, want in SHOW.items():
        page.evaluate(JS_SETCTX, c)
        page.wait_for_timeout(130)
        got = page.evaluate(JS_READ)
        exp = {k: ('dim' if 0 < v < 1 else v) for k, v in want.items()}
        diff = {k: (got[k], exp[k]) for k in exp if got[k] != exp[k]}
        check(f'显隐 {c}', not diff and got['_ctx'] == c, diff or got['_ctx'])
    # 动态规则
    page.evaluate(JS_SETCTX, 'explore')
    page.evaluate('() => { G.party._ready = false; G.party._swap = false; }')
    page.wait_for_timeout(130)
    g1 = page.evaluate(JS_READ)
    page.evaluate('() => { G.party._ready = true; G.party._swap = true; G.world._look = { id: "h" }; G.world.near = { label: "x" }; }')
    page.wait_for_timeout(130)
    g2 = page.evaluate(JS_READ)
    page.evaluate('() => { document.getElementById("tc-toast").classList.remove("show"); }')
    page.screenshot(path=str(OUT / 'touch_844x390_explore.png'))
    shots.append('touch_844x390_explore.png')
    check('explore：替身调查冷却中 U 暗、不能换人时换人钮藏起来；附近有对得上的调查点 U 跳动、能互动 E 跳动',
          g1['u'] == 'dim' and g1['swap'] == 0 and g2['u'] == 1 and g2['_uReady'] and g2['swap'] == 1 and g2['_ePulse']
          and g2['_uCaption'] == '替身调查', {'g1': g1, 'g2': g2})
    page.evaluate(JS_SETCTX, 'combat')
    page.evaluate('() => { G.world.player.energy = 100; G.world.fight = { swap: true }; }')
    page.wait_for_timeout(130)
    g3 = page.evaluate(JS_READ)
    page.evaluate('() => { G.world.player.energy = 10; G.world.fight = { swap: false, storyU: true }; }')
    page.wait_for_timeout(130)
    g4 = page.evaluate(JS_READ)
    check('combat：能量满 U 跳动、swap 战显示换人钮；剧情专用 U 窗口金色光圈',
          g3['u'] == 1 and g3['_uReady'] and g3['swap'] == 1 and g4['_uGold'] and g4['_uReady'] and g4['swap'] == 0
          and g3['_uCaption'] == g4['_uCaption'] == '必杀', {'g3': g3, 'g4': g4})
    page.screenshot(path=str(OUT / 'touch_844x390_combat.png'))
    shots.append('touch_844x390_combat.png')

    # 机关需要独立控制输入，否则探索层会藏起格挡、闪避和小游戏专用 U。
    page.evaluate(JS_SETCTX, 'explore')
    page.evaluate('''() => { G.lateGame = { type: 'regression', touch: {
        buttons: ['pad', 'j', 'l', 'u'], captions: { j: '加速', l: '刹车', u: '反射' }
    } }; }''')
    page.wait_for_timeout(130)
    g5 = page.evaluate(JS_READ)
    captions = page.evaluate('() => ["j", "l", "u"].map(n => document.querySelector(".tc-" + n + " i").textContent)')
    check('机关只显示声明的按钮，L/U 不继承探索冷却和调查提示',
          g5['_ctx'] == 'late' and g5['pad'] == g5['j'] == g5['l'] == g5['u'] == 1
          and g5['k'] == g5['e'] == g5['swap'] == 0 and captions == ['加速', '刹车', '反射'],
          {'visible': g5, 'captions': captions})
    page.evaluate('() => { G.lateGame.touch = { buttons: ["e"], captions: { e: "投牌" } }; }')
    page.wait_for_timeout(130)
    g6 = page.evaluate(JS_READ)
    e_caption = page.locator('.tc-e i').text_content()
    check('同一个机关切换阶段即时更新按钮及提示',
          g6['_ctx'] == 'late' and g6['e'] == 1 and g6['pad'] == g6['j'] == g6['l'] == g6['u'] == 0
          and e_caption == '投牌', {'visible': g6, 'caption': e_caption})
    page.evaluate('() => { G.ui.menu = {}; }')
    page.wait_for_timeout(130)
    g7 = page.evaluate(JS_READ)
    check('暂停菜单优先于机关按键上下文', g7['_ctx'] == 'menu' and g7['e'] == 1 and g7['j'] == 0, g7)
    page.evaluate('() => { G.lateGame = null; G.ui.menu = null; }')
    page.wait_for_timeout(130)
    g8 = page.evaluate(JS_READ)
    restored = page.evaluate('() => ["j", "l", "u"].map(n => document.querySelector(".tc-" + n + " i").textContent)')
    check('离开机关恢复探索层按钮和原提示',
          g8['_ctx'] == 'explore' and g8['l'] == 0 and g8['_uCaption'] == '替身调查'
          and restored[0] != '加速' and restored[1] != '刹车', {'visible': g8, 'captions': restored})

    # ---- 按下写进 G.input（U、换人、J、方向盘）
    page.evaluate('''() => { window.__probe = []; G.testScene.probe = () => { const I = G.input;
        const h = ['special', 'swap', 'attack', 'right', 'ok'].filter((a) => I.hit(a)); if (h.length) window.__probe.push(h.join(',')); }; }''')
    page.evaluate(JS_SETCTX, 'combat')
    page.evaluate('() => { G.world.fight = { swap: true }; G.world.player.energy = 100; }')
    page.wait_for_timeout(130)
    for sel, act in [('.tc-u', 'special'), ('#tc-swap', 'swap'), ('.tc-j', 'attack'),
                     ('.tc-k', 'dodge'), ('.tc-l', 'guard')]:
        x, y = center(page, sel)
        page.locator(sel).dispatch_event('pointerdown', {'pointerId': 7, 'pointerType': 'touch', 'isPrimary': True, 'clientX': x, 'clientY': y, 'bubbles': True})
        d1 = page.evaluate(f'() => {{ G.dbg.tick(1); return G.input.isDown("{act}"); }}')
        page.locator(sel).dispatch_event('pointerup', {'pointerId': 7, 'pointerType': 'touch', 'isPrimary': True, 'clientX': x, 'clientY': y, 'bubbles': True})
        d2 = page.evaluate(f'() => {{ G.dbg.tick(1); return G.input.isDown("{act}"); }}')
        check(f'触屏 {sel} 按下 → G.input.{act} 按住、松开 → 放开', d1 and not d2, [d1, d2])
    b = page.locator('#tc-pad').bounding_box()
    px, py = b['x'] + b['width'] * 0.92, b['y'] + b['height'] / 2
    page.locator('#tc-pad').dispatch_event('pointerdown', {'pointerId': 9, 'pointerType': 'touch', 'isPrimary': True, 'clientX': px, 'clientY': py, 'bubbles': True})
    d1 = page.evaluate('() => { G.dbg.tick(1); return [G.input.isDown("right"), G.input.isDown("left")]; }')
    page.locator('#tc-pad').dispatch_event('pointerup', {'pointerId': 9, 'pointerType': 'touch', 'isPrimary': True, 'clientX': px, 'clientY': py, 'bubbles': True})
    d2 = page.evaluate('() => { G.dbg.tick(1); return G.input.isDown("right"); }')
    check('方向盘按右侧 → right 按住、松开 → 放开', d1 == [True, False] and d2 is False, [d1, d2])
    # 真的触摸点按（touchscreen.tap 走浏览器的触摸 → 指针事件）
    x, y = center(page, '.tc-u')
    page.touchscreen.tap(x, y)
    page.evaluate('() => { G.dbg.tick(1); }')
    pr = page.evaluate('() => window.__probe')
    check('touchscreen.tap 点 U 钮：这一步 hit(special)', any('special' in s for s in pr), pr)

    # ---- 点画布推进对话（0.12 s 内点无效）
    page.evaluate(JS_SETCTX, 'explore')
    cx, cy = 422, 150
    page.evaluate('() => { window.__said = false; G.ui.say("测试台词：点屏幕推进对话。").then(() => { window.__said = true; }); G.dbg.tick(3); }')
    page.touchscreen.tap(cx, cy)
    s1 = page.evaluate('() => { G.dbg.tick(1); return { all: G.ui.dlg && G.ui.dlg.all, t: G.ui.dlg && G.ui.dlg.t }; }')
    page.evaluate('() => { G.dbg.tick(6); }')
    page.touchscreen.tap(cx, cy)
    s2 = page.evaluate('() => { G.dbg.tick(1); return { all: G.ui.dlg && G.ui.dlg.all }; }')
    page.touchscreen.tap(cx, cy)
    s3 = page.evaluate('async () => { G.dbg.tick(1); await new Promise((r) => setTimeout(r, 0)); return { dlg: !!G.ui.dlg, said: window.__said }; }')
    check('点画布推进对话：0.12 s 内点无效 → 再点显示整页 → 再点结束', (not s1['all']) and s2['all'] and (not s3['dlg']) and s3['said'], [s1, s2, s3])

    # ---- 连打 QTE 结束后狂点 0.5 s，下一句不被跳过（§4.3.4）
    page.evaluate('() => { window.__qd = false; G.ui.startQte({ type: "mash", need: 3 }).then(() => { window.__qd = true; G.ui.say("第一句：这句不应该被狂点跳过，后面还有字。"); }); G.dbg.tick(1); }')
    jx, jy = center(page, '.tc-j')
    for _ in range(3):
        page.touchscreen.tap(jx, jy)
        page.evaluate('() => { G.dbg.tick(2); }')
    page.evaluate('async () => { await new Promise((r) => setTimeout(r, 0)); G.dbg.tick(1); }')
    for _ in range(15):          # 0.5 s：每 2 步点一下画面
        page.touchscreen.tap(cx, cy)
        page.evaluate('() => { G.dbg.tick(2); }')
    r = page.evaluate('() => ({ qd: window.__qd, dlg: G.ui.dlg && { all: G.ui.dlg.all, page: G.ui.dlg.page, shown: G.ui.dlg.shown }, lock: G.input.okLocked() })')
    check('连打 QTE 后狂点 0.5 s：下一句还在第一页、没被“显示全部”', r['qd'] and r['dlg'] and not r['dlg']['all'] and r['dlg']['page'] == 0, r)
    page.evaluate('() => { G.ui.dlg = null; G.testScene.probe = null; }')

    # ---- 五个尺寸：按钮不重叠、不出屏
    page.evaluate(JS_SETCTX, 'combat')
    page.evaluate('() => { G.world.fight = { swap: true }; }')
    for (w, h) in TOUCH_SIZES:
        page.set_viewport_size({'width': w, 'height': h})
        page.wait_for_timeout(200)
        r = page.evaluate('''() => { const R = (s) => { const b = document.querySelector(s).getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
            const ids = { pad: '#tc-pad', j: '.tc-j', k: '.tc-k', l: '.tc-l', e: '.tc-e', u: '.tc-u', swap: '#tc-swap', pause: '#tc-pause', full: '#tc-full' };
            const o = {}; for (const k in ids) o[k] = R(ids[k]); return { r: o, vw: innerWidth, vh: innerHeight, susp: G.suspended, b: getComputedStyle(document.getElementById('tc')).getPropertyValue('--b') }; }''')
        rects, bad = r['r'], []
        names = list(rects)
        for i in range(len(names)):
            a = rects[names[i]]
            if a[0] < -0.5 or a[1] < -0.5 or a[2] > r['vw'] + 0.5 or a[3] > r['vh'] + 0.5:
                bad.append(f'{names[i]} 出屏')
            for j in range(i + 1, len(names)):
                bb = rects[names[j]]
                ca, cb = ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2), ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)
                ra, rb = (a[2] - a[0]) / 2, (bb[2] - bb[0]) / 2
                if ((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2) ** 0.5 < ra + rb - 0.5:
                    bad.append(f'{names[i]}×{names[j]} 重叠')
        check(f'{w}×{h}：按钮不重叠、不出屏', not bad and not r['susp'], {'bad': bad, 'b': r['b']})
    page.set_viewport_size({'width': 390, 'height': 844})
    page.wait_for_timeout(200)
    p1 = page.evaluate('() => [G.suspended, document.body.classList.contains("tc-portrait")]')
    page.set_viewport_size({'width': 844, 'height': 390})
    page.wait_for_timeout(200)
    p2 = page.evaluate('() => [G.suspended, document.body.classList.contains("tc-portrait")]')
    check('竖着拿：停住游戏 + 横屏提示；横过来恢复', p1 == [True, True] and p2 == [False, False], [p1, p2])
    # 接实体键盘就收起；按键大小
    r = page.evaluate('() => { const n0 = G.touch.sizeName(); G.touch.cycleSize(); const n1 = G.touch.sizeName(); const ts = G.settings.touchSize; G.touch.cycleSize(); G.touch.cycleSize(); return [n0, n1, ts, G.touch.sizeName()]; }')
    check('按键大小循环 中 → 大 → 小 → 中，写进 settings.touchSize', r == ['中', '大', 1.22, '中'], r)
    page.keyboard.press('j')
    page.wait_for_timeout(100)
    r = page.evaluate('() => [G.touch.on, document.body.classList.contains("tc-on")]')
    check('按实体键盘的游戏键：屏幕按键收起', r == [False, False], r)
    ctx.close()


def test_real(browser, shots):
    """集成后用真的 index.html 跑：触屏 DOM、标题场景的显隐、按钮写进 G.input。"""
    print('[real] 真 index.html 的触屏检查')
    need = [GAME / 'data' / 'data_meta.js', GAME / 'main.js', GAME / 'engine' / 'ui.js']
    miss = [str(p.relative_to(GAME)) for p in need if not p.exists()]
    if miss:
        check('真 index.html：缺文件，跳过（并行阶段正常）', True, miss)
        return
    ctx = browser.new_context(viewport={'width': 844, 'height': 390}, has_touch=True, is_mobile=True, device_scale_factor=1)
    page = ctx.new_page()
    watch(page, 'real')
    page.goto((GAME / 'index.html').as_uri() + '?touch=1&autotest=1')
    page.wait_for_function('window.G && G.scene && G.scene.name', timeout=60000)
    page.wait_for_timeout(500)
    r = page.evaluate('() => ({ scene: G.scene.name, ctx: G.touch.ctx, u: !!document.querySelector(".tc-u"), swap: !!document.querySelector("#tc-swap") })')
    check('真 index.html：开到标题、触屏上下文 title、U / 换人钮存在', r['scene'] == 'title' and r['ctx'] == 'title' and r['u'] and r['swap'], r)
    page.screenshot(path=str(OUT / 'real_title_844x390.png'))
    shots.append('real_title_844x390.png')
    ctx.close()


def main():
    ap = argparse.ArgumentParser(description='包 1 自测（技术约定 §7.1）')
    ap.add_argument('--part', choices=['all', 'core', 'audio', 'touch'], default='all')
    ap.add_argument('--real', action='store_true', help='集成后：真 index.html 的触屏检查')
    ap.add_argument('--headed', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    subprocess.run([sys.executable, '-B', str(HERE / 'gen_fixture.py')], check=True, env=env)
    from playwright.sync_api import sync_playwright  # noqa: E402
    shots = []
    t0 = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not a.headed, args=['--autoplay-policy=no-user-gesture-required'])
        if a.real:
            test_real(browser, shots)
        else:
            if a.part in ('all', 'core'):
                test_core(browser, shots)
            if a.part in ('all', 'audio'):
                test_audio(browser, shots)
            if a.part in ('all', 'touch'):
                test_touch(browser, shots)
        browser.close()
    real_results = [x for x in results if x['name'] != 'expected-error-seen']
    fails = [x for x in real_results if not x['ok']]
    check('控制台 0 warning / 0 error / 0 pageerror', not console_bad, console_bad[:10])
    fails = [x for x in results if not x['ok']]
    out = {'ok': not fails, 'n': len(real_results) + 1, 'fails': fails, 'console': console_bad, 'results': results,
           'shots': shots, 'sec': round(time.time() - t0, 1)}
    with open(OUT / 'test_core.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'\n{"全部通过" if not fails else "有失败"}：{len(real_results) + 1 - len(fails)} / {len(real_results) + 1}，用时 {out["sec"]} s；结果 {OUT / "test_core.json"}')
    sys.exit(0 if not fails else 1)


if __name__ == '__main__':
    main()
