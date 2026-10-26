r"""存档功能检查（2026-10-20）：本机浏览器存档、旧存档兼容、小红书容器 Storage 双写 / 回读 / 卡死 / 报错、清除存档、游玩时长。

    python -B tools\dev\full\test_save.py [--out tools\_playtest\save_check]
    python -B tools\dev\full\test_save.py --root <小红书包文件夹，如 小红书小工具\dist-silent>     # 对打好的发布包再跑一遍

菜单全用真实键盘；“打完一章”这一步用开发钩子把该章剧情换成空函数（只测写档，不算通关证据，整章路线另跑各章 test_*.py）。
小红书容器用假的 window.xhs.miniTool 代替：存档数据放在 Python 这边（expose_function），页面刷新 / 本机 localStorage 清空后还在，
就像容器真的把数据存在页面之外。不是平台模拟器、也不是真机——真机还得用户扫码确认一次。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

GAME = Path(__file__).resolve().parents[3]
SNAP = "() => { const s = G.dbg.snapshot(); return { scene: s.scene, menuItems: s.menuItems, notice: s.notice," \
       " menuTitle: G.ui.menu ? G.ui.menu.title : null, max: G.progress.max, info: G.progress.info(), status: G.store.status() }; }"

# 假的小红书容器接口。mode：ok 正常 / hangget 读不返回 / hangset 写不返回 / rejectget 读报“key 不存在” / throw 写读都报错 / syncthrow 同步抛错
XHS_INIT = r"""
(() => {
  const mode = %r;
  const calls = (window.__xhsCalls = { get: 0, set: 0 });
  const never = () => new Promise(() => {});
  const api = {
    getStorage(o) {
      calls.get++;
      if (mode === 'hangget') return never();
      if (mode === 'rejectget') return Promise.reject({ errMsg: 'getStorage:fail key not exist' });
      if (mode === 'throw') return Promise.reject({ errMsg: 'getStorage:fail' });
      if (mode === 'syncthrow') throw new Error('bridge gone');
      return window.__xhsGet(o.key).then(d => ({ errMsg: 'getStorage:ok', data: d }));
    },
    setStorage(o) {
      calls.set++;
      if (mode === 'hangset') return never();
      if (mode === 'throw') return Promise.reject({ errMsg: 'setStorage:fail' });
      if (mode === 'syncthrow') throw new Error('bridge gone');
      return window.__xhsSet(o.key, o.data).then(() => ({ errMsg: 'setStorage:ok' }));
    },
  };
  window.xhs = { miniTool: api };
})();
"""

# 本机 localStorage 写不进去（隐私模式）
LS_BROKEN = r"""
(() => {
  const bad = () => { throw new DOMException('quota', 'QuotaExceededError'); };
  Storage.prototype.setItem = bad;
})();
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', help='发布包文件夹（不给 = 开发目录 + ?demo=1）')
    ap.add_argument('--csp', action='store_true', help='配合 --root：用小红书容器同款 CSP 的本地服务打开（脚本只许外链、不许 eval）')
    ap.add_argument('--out', default=str(GAME / 'tools' / '_playtest' / 'save_check'))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    root = Path(a.root) if a.root else GAME
    url = (root / 'index.html').as_uri() + ('?autotest=1' if a.root else '?autotest=1&demo=1')
    if a.csp:
        sys.path.insert(0, str(GAME.parent / '小红书小工具'))
        import xhs_common as X  # noqa: E402
        _srv, base, _bad = X.serve(str(root))
        url = base + 'index.html?autotest=1'
    errors, checks, shots = [], [], []
    xhs_store = {}

    from playwright.sync_api import sync_playwright

    def check(ok, what, **kw):
        checks.append({'ok': bool(ok), 'what': what, **kw})
        print(('ok  ' if ok else 'BAD ') + what + ('  ' + json.dumps(kw, ensure_ascii=False) if kw and not ok else ''), flush=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])

        def new_page(case, mode=None, ls_broken=False, keep_ctx=None):
            ctx = keep_ctx or browser.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
            page = ctx.new_page()
            page.on('console', lambda m: errors.append({'case': case, 'kind': 'console_' + m.type, 'text': m.text}) if m.type in ('error', 'warning') else None)
            page.on('pageerror', lambda e: errors.append({'case': case, 'kind': 'pageerror', 'text': str(e)}))
            if mode:
                page.expose_function('__xhsGet', lambda k: xhs_store.get(k))
                page.expose_function('__xhsSet', lambda k, d: xhs_store.__setitem__(k, d))
                page.add_init_script(XHS_INIT % mode)
            if ls_broken:
                page.add_init_script(LS_BROKEN)
            return ctx, page

        def st(page):
            return page.evaluate(SNAP)

        def shot(page, name):
            p = out / f'{len(shots) + 1:02d}_{name}.png'
            page.screenshot(path=str(p))
            shots.append(str(p))

        def key(page, k, wait=90):
            page.keyboard.down(k); page.wait_for_timeout(40); page.keyboard.up(k); page.wait_for_timeout(wait)

        def boot(page, case):
            t0 = time.time()
            page.goto(url, wait_until='load')
            page.wait_for_function('() => G.booted && G.ui.menu', timeout=60000)
            page.wait_for_timeout(500)
            return time.time() - t0

        def pick(page, label):
            page.wait_for_timeout(150)
            items = st(page).get('menuItems') or []
            hit = [i for i, v in enumerate(items) if label in (v or '')]
            if not hit:
                check(False, 'menu_item_missing', label=label, items=items)
                return False
            idx = page.evaluate('() => G.ui.menu ? G.ui.menu.idx : 0') or 0
            for _ in range(abs(hit[0] - idx)):
                key(page, 'ArrowDown' if hit[0] > idx else 'ArrowUp', 70)
            key(page, 'Enter', 260)
            return True

        def dismiss_notice(page):
            page.wait_for_function('() => G.ui.noticeBox && G.ui.noticeBox.t >= 0.7', timeout=10000)
            key(page, 'Enter', 120)
            page.wait_for_function('() => !G.ui.noticeBox', timeout=10000)

        def finish_chapter(page, idx):
            # 开发钩子：该章剧情换成空函数，走完正式的“开始 → 打完 → 记进度”流程；章末菜单出来后回标题
            page.evaluate('(i) => { G.CHAPTERS[i].run = async () => {}; G.playFrom(i); }', idx)
            page.wait_for_function('() => G.ui.menu && /完/.test(G.ui.menu.title || "")', timeout=30000)
            page.evaluate('() => { G.goTitle(); }')
            page.wait_for_function('() => G.scene && G.scene.name === "title" && G.ui.menu', timeout=20000)
            page.wait_for_timeout(500)

        def ls(page, k):
            return page.evaluate('(k) => { try { return localStorage.getItem(k); } catch (e) { return "ERR"; } }', k)

        # ================================================================ A. 本机浏览器（没有小红书接口）
        ctx, page = new_page('A')
        boot(page, 'A')
        s = st(page)
        check(not any(v.startswith('继续') or v.startswith('重温') for v in s['menuItems']), 'A1 新玩家没有「继续」', items=s['menuItems'])
        check('存档' not in s['menuItems'], 'A1 新玩家没有「存档」入口', items=s['menuItems'])
        check(s['status']['local'] is True and not s['status']['hasXhs'], 'A1 本机存储可用、没有容器接口', status=s['status'])

        finish_chapter(page, 0)
        raw = json.loads(ls(page, 'jojo-progress') or 'null')
        check(raw and raw['v'] == 1 and raw['done'] == [0] and raw['max'] == 1 and raw['at'] > 0, 'A2 打完序章：localStorage 里记了 done=[0]、max=1、时间', raw=raw)
        s = st(page)
        check((s['menuItems'] or [])[:1] == ['继续：第1章　香港'], 'A2 标题「继续：第1章　香港」', items=s['menuItems'])
        check('存档' in s['menuItems'], 'A2 有「存档」入口', items=s['menuItems'])
        shot(page, 'title_with_save')
        pick(page, '选择章节')
        s = st(page)
        check((s['menuItems'] or [])[:2] == ['序章　东京　★', '第1章　香港'], 'A2 选章菜单：序章标了 ★、第1章没有', items=s['menuItems'])
        shot(page, 'chapter_menu_star')
        pick(page, '返回')

        # 查看存档
        pick(page, '存档')
        pick(page, '查看存档')
        page.wait_for_timeout(500)
        s = st(page)
        shot(page, 'save_info')
        n = s['notice'] or ''
        total = page.evaluate('() => G.DEMO ? G.DEMO.last + 1 : 13')
        check('最远：第1章' in n and ('通关：1 / %d 章' % total) in n and '存放：本机浏览器' in n, 'A3 存档信息：最远 / 通关 / 存放位置', notice=n)
        dismiss_notice(page)

        # 清除存档：先选取消，进度还在；再选清除
        pick(page, '清除存档')
        page.wait_for_timeout(300)
        shot(page, 'erase_confirm')
        check(st(page)['menuTitle'] == '清除存档？', 'A4 清除前有二次确认', title=st(page)['menuTitle'])
        key(page, 'Enter', 260)     # 默认选中“取消”
        check(ls(page, 'jojo-progress') is not None, 'A4 选「取消」进度还在')
        page.evaluate('() => { G.settings.musicVol = 0.3; G.settings.save(); }')
        pick(page, '清除存档')
        pick(page, '清除进度、收藏和成就')
        page.wait_for_timeout(500)
        check('已清除' in (st(page)['notice'] or ''), 'A4 清除后提示「存档已清除」', notice=st(page)['notice'])
        dismiss_notice(page)      # 清除后直接回到标题菜单（存档子菜单已退出）
        page.wait_for_timeout(300)
        s = st(page)
        check(ls(page, 'jojo-progress') is None, 'A4 localStorage 里的进度删掉了')
        check(not any(v.startswith('继续') for v in s['menuItems']) and '存档' not in s['menuItems'], 'A4 标题没有「继续」「存档」了', items=s['menuItems'])
        check(s['info']['done'] == [] and s['info']['max'] == 0, 'A4 内存里的进度也清空了', info=s['info'])
        check(json.loads(ls(page, 'jojo-settings') or 'null')['musicVol'] == 0.3, 'A4 设置没被清掉')
        ctx.close()

        # 旧存档（只有 v/max/last/clear）照样读，不乱猜 done
        ctx, page = new_page('A5')
        page.add_init_script("localStorage.setItem('jojo-progress', JSON.stringify({ v: 1, max: 1, last: 1, clear: false }));")
        boot(page, 'A5')
        s = st(page)
        check((s['menuItems'] or [])[:1] == ['继续：第1章　香港'] and s['info']['done'] == [], 'A5 旧版存档能读、done 补空', items=s['menuItems'], info=s['info'])
        ctx.close()

        # 坏存档（不是对象 / max 越界）退回空存档，不报错
        for bad in ['"junk"', '{"v":1,"max":99}', '{"v":2,"max":1}', 'not json']:
            ctx, page = new_page('A6')
            page.add_init_script("localStorage.setItem('jojo-progress', %s);" % json.dumps(bad))
            boot(page, 'A6')
            s = st(page)
            check(s['info']['max'] == 0 and not any(v.startswith('继续') for v in s['menuItems']), 'A6 坏存档 %s 退回空存档' % bad, info=s['info'])
            ctx.close()

        # 游玩时长：世界在走才累计，暂停 / 标题不算；切后台补写
        ctx, page = new_page('A7')
        boot(page, 'A7')
        page.evaluate('() => { G.CHAPTERS[0].run = async () => { await new Promise(r => setTimeout(r, 6000)); }; G.playFrom(0); }')
        page.wait_for_function('() => G.scene && G.scene.name === "world"', timeout=30000)
        page.wait_for_timeout(3500)
        p1 = page.evaluate('() => G.progress.info().play')
        page.evaluate('() => { window.dispatchEvent(new Event("pagehide")); }')
        raw = json.loads(ls(page, 'jojo-progress') or 'null')
        check(p1 >= 2 and raw and raw['play'] >= 2, 'A7 玩了几秒：play 累计，切后台 / 关页面补写', play=p1, raw=raw)
        key(page, 'Escape', 400)     # 暂停菜单
        page.wait_for_timeout(300)
        q1 = page.evaluate('() => G.progress.info().play')
        page.wait_for_timeout(1500)
        q2 = page.evaluate('() => G.progress.info().play')
        check(q2 == q1, 'A7 暂停时不累计游玩时长', before=q1, after=q2)
        ctx.close()

        # 本机 localStorage 写不进去（隐私模式）：不报错、能玩、存档界面老实说“失败”
        ctx, page = new_page('A8', ls_broken=True)
        boot(page, 'A8')
        finish_chapter(page, 0)
        s = st(page)
        check(s['status']['local'] is False and (s['menuItems'] or [])[:1] == ['继续：第1章　香港'], 'A8 localStorage 写不进去：这次的进度还在内存里', status=s['status'], items=s['menuItems'])
        pick(page, '存档'); pick(page, '查看存档'); page.wait_for_timeout(500)
        shot(page, 'save_info_failed')
        check('存放：失败' in (st(page)['notice'] or ''), 'A8 存档界面写“存放：失败”', notice=st(page)['notice'])
        ctx.close()

        # ================================================================ B. 小红书容器 Storage
        # B1 双写：打完一章 → 容器里有 jojo-save；清空本机 localStorage（容器被清）再开 → 从容器恢复
        xhs_store.clear()
        ctx, page = new_page('B1', 'ok')
        boot(page, 'B1')
        check(st(page)['status']['hasXhs'], 'B1 认出容器接口')
        finish_chapter(page, 0)
        page.wait_for_timeout(900)
        blob = json.loads(xhs_store.get('jojo-save') or 'null')
        check(blob and blob['v'] == 1 and 'progress' in blob['keys'] and json.loads(blob['keys']['progress'])['done'] == [0], 'B1 容器里写了存档（jojo-save.keys.progress.done=[0]）', blob=blob)
        s = st(page)
        check(s['status']['xhs'] is True and s['status']['local'] is True, 'B1 两条通道状态都是成功', status=s['status'])
        pick(page, '存档'); pick(page, '查看存档'); page.wait_for_timeout(500)
        shot(page, 'save_info_xhs')
        check('小红书小工具存储 + 本机浏览器' in (st(page)['notice'] or ''), 'B1 存档界面写两处存放位置', notice=st(page)['notice'])
        dismiss_notice(page)
        page.evaluate('() => { localStorage.clear(); }')
        page.close()
        _, page = new_page('B1b', 'ok', keep_ctx=ctx)
        boot(page, 'B1b')
        s = st(page)
        check((s['menuItems'] or [])[:1] == ['继续：第1章　香港'], 'B1 本机清空后从容器恢复「继续」', items=s['menuItems'])
        check(json.loads(ls(page, 'jojo-progress') or 'null') is not None, 'B1 恢复后回写到本机 localStorage')
        ctx.close()

        # B2 容器里的更新：以容器为准（另一台设备 / 本机落后）
        newer = {'v': 1, 't': int(time.time() * 1000) + 10000, 'keys': {'progress': json.dumps({'v': 1, 'max': 1, 'last': 1, 'clear': False, 'done': [0], 'play': 600, 'at': 1})}}
        xhs_store.clear(); xhs_store['jojo-save'] = json.dumps(newer)
        ctx, page = new_page('B2', 'ok')
        page.add_init_script("localStorage.setItem('jojo-progress', JSON.stringify({ v: 1, max: 0, last: 0, clear: false })); localStorage.setItem('jojo-save-t', '5');")
        boot(page, 'B2')
        s = st(page)
        check(s['info']['max'] == 1 and s['info']['play'] == 600, 'B2 容器里的存档更新：以容器为准', info=s['info'])
        ctx.close()

        # B3 本机更新（容器里的旧）：保留本机并补写容器
        older = {'v': 1, 't': 5, 'keys': {'progress': json.dumps({'v': 1, 'max': 0, 'last': 0, 'clear': False})}}
        xhs_store.clear(); xhs_store['jojo-save'] = json.dumps(older)
        ctx, page = new_page('B3', 'ok')
        page.add_init_script("localStorage.setItem('jojo-progress', JSON.stringify({ v: 1, max: 1, last: 1, clear: false, done: [0] })); localStorage.setItem('jojo-save-t', '99999');")
        boot(page, 'B3')
        page.wait_for_timeout(1200)
        s = st(page)
        blob = json.loads(xhs_store['jojo-save'])
        check(s['info']['max'] == 1 and blob['t'] >= 99999 and json.loads(blob['keys']['progress'])['max'] == 1, 'B3 本机的更新：保留本机、补写进容器', info=s['info'], t=blob['t'])
        ctx.close()

        # B4 容器读接口永远不返回：游戏照常 ≤ 4 s 进标题，用本机的存档
        xhs_store.clear()
        ctx, page = new_page('B4', 'hangget')
        page.add_init_script("localStorage.setItem('jojo-progress', JSON.stringify({ v: 1, max: 1, last: 1, clear: false, done: [0] }));")
        dt = boot(page, 'B4')
        s = st(page)
        check(dt < 8 and (s['menuItems'] or [])[:1] == ['继续：第1章　香港'], 'B4 容器读卡死：照常进标题，用本机存档', seconds=round(dt, 1), items=s['menuItems'])
        ctx.close()

        # B5 容器写接口永远不返回：游戏照常玩，存档界面里只算本机
        xhs_store.clear()
        ctx, page = new_page('B5', 'hangset')
        boot(page, 'B5')
        finish_chapter(page, 0)
        page.wait_for_timeout(900)
        s = st(page)
        check((s['menuItems'] or [])[:1] == ['继续：第1章　香港'] and ls(page, 'jojo-progress'), 'B5 容器写卡死：本机照常保存', items=s['menuItems'])
        ctx.close()

        # B6 容器读 / 写都报错（含同步抛错）：不抛到页面，存档界面只写本机
        for mode in ('throw', 'syncthrow'):
            xhs_store.clear()
            ctx, page = new_page('B6-' + mode, mode)
            boot(page, 'B6')
            finish_chapter(page, 0)
            page.wait_for_timeout(1200)
            pick(page, '存档'); pick(page, '查看存档'); page.wait_for_timeout(500)
            n = st(page)['notice'] or ''
            check('存放：本机浏览器' in n and '小红书' not in n, 'B6 容器接口 %s：存档界面只写本机浏览器' % mode, notice=n, status=st(page)['status'])
            ctx.close()

        # B7 读“key 不存在”当成空，随后补写成功
        xhs_store.clear()
        ctx, page = new_page('B7', 'rejectget')
        page.add_init_script("localStorage.setItem('jojo-progress', JSON.stringify({ v: 1, max: 1, last: 1, clear: false, done: [0] }));")
        boot(page, 'B7')
        page.wait_for_timeout(1200)
        check(bool(xhs_store.get('jojo-save')), 'B7 读到“key 不存在”：把本机存档补写进容器')
        ctx.close()

        # B8 清除存档同步到容器，重开不会又从容器“复活”
        xhs_store.clear()
        ctx, page = new_page('B8', 'ok')
        boot(page, 'B8')
        finish_chapter(page, 0)
        page.wait_for_timeout(900)
        pick(page, '存档'); pick(page, '清除存档'); pick(page, '清除进度、收藏和成就'); page.wait_for_timeout(400)
        dismiss_notice(page)
        page.wait_for_timeout(900)
        blob = json.loads(xhs_store['jojo-save'])
        check('progress' not in blob['keys'], 'B8 清除存档同步到容器', keys=list(blob['keys']))
        page.close()
        _, page = new_page('B8b', 'ok', keep_ctx=ctx)
        boot(page, 'B8b')
        s = st(page)
        check(not any(v.startswith('继续') for v in s['menuItems']), 'B8 重开后没有“复活”出继续', items=s['menuItems'])
        ctx.close()

        browser.close()

    bad = [c for c in checks if not c['ok']]
    res = {'ok': not bad and not errors, 'url': url, 'checks': checks, 'errors': errors, 'shots': shots}
    (out / 'result.json').write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': res['ok'], 'bad': len(bad), 'errors': len(errors), 'out': str(out)}, ensure_ascii=False))
    return 0 if res['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
