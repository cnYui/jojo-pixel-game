// 用真实第5章战斗的失败流程验证广告分支；测试副本与报告由调用者放在临时目录。
'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { serve } = require('../dev/serve');
const root = path.resolve(process.argv[2]);
const out = path.resolve(process.argv[3]);
fs.mkdirSync(out, { recursive: true });
const results = [];

async function tick(page, n = 12) {
  await page.evaluate(async n => {
    const ch = new MessageChannel();
    for (let i = 0; i < n; i++) {
      G.dbg.tick(1);
      await new Promise(r => { ch.port1.onmessage = r; ch.port2.postMessage(0); });
    }
    ch.port1.close(); ch.port2.close();
  }, n);
}
async function until(page, predicate, label, max = 1800) {
  for (let i = 0; i < max; i++) {
    if (await page.evaluate(predicate)) return;
    await tick(page);
  }
  throw new Error('等待超时：' + label + ' ' + JSON.stringify(await page.evaluate(() => G.dbg.snapshot())));
}
async function choose(page, index) {
  for (let i = 0; i < index; i++) { await page.keyboard.press('ArrowDown'); await tick(page, 2); }
  await page.keyboard.press('Enter'); await tick(page, 2);
}
async function boot(browser, url, mode) {
  const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(url + 'index.html?autotest=1&adMock=' + mode);
  await page.waitForFunction(() => window.G && G.booted && G.ui.menu);
  await page.evaluate(() => {
    G.dbg.hold = true; window.__notices = [];
    const original = G.ui.notice;
    G.ui.notice = function (o) { window.__notices.push(o.text); return original.apply(this, arguments); };
    window.__botCfg = { read: 0.1, assist: false, titleWait: 0, chapter: 'ch5' };
  });
  await page.addScriptTag({ path: path.resolve(__dirname, '../dev/p4_bot.js') });
  await page.addScriptTag({ path: path.resolve(__dirname, '../dev/p4_bot_ch5.js') });
  await page.evaluate(() => { window.__bot.started = true; G.playFrom(5); });
  await until(page, () => G.world.combat && G.world.fight && !G.world.cine, '第5章剧情战斗');
  assert.strictEqual(await page.evaluate(() => G.world.fight.id), 'b07_heavensdoor');
  assert.strictEqual(await page.evaluate(() => G.world.fight.spec.losable), true);
  await page.evaluate(() => { window.__bot.manual = true; });
  await tick(page, 2);
  return { page, errors };
}
async function lose(page) {
  // 只置零主角 HP，由生产战斗 tick 走正常的失败判定，不替换菜单或 failed()。
  await page.evaluate(() => { G.world.player.hp = 0; });
  await until(page, () => G.ui.menu && G.ui.menu.options[0] === '再来一次', '失败菜单');
}
async function assistMenu(page) {
  await lose(page);
  assert.deepStrictEqual(await page.evaluate(() => G.ui.menu.options), ['再来一次', '回到标题']);
  await choose(page, 0);
  await until(page, () => G.world.combat && G.world.fight.attempt === 1, '普通重试');
  await lose(page);
}
async function assertRetry(page, assist) {
  await until(page, () => G.world.combat && G.world.fight.attempt === 2, '广告后继续战斗');
  assert.strictEqual(await page.evaluate(() => G.world.fight.assist), assist);
  await tick(page, 60);
  assert.strictEqual(await page.evaluate(() => G.world.combat && G.world.fight.attempt === 2), true);
}

(async () => {
  const { srv, url } = await serve(root);
  let browser;
  try {
    browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
    for (const mode of ['ok', 'closed', 'skipped', 'fail', 'timeout', 'unsupported']) {
      const { page, errors } = await boot(browser, url, mode);
      try {
        await assistMenu(page);
        const label = await page.evaluate(() => G.ui.menu.options[2]);
        assert.strictEqual(label, mode === 'unsupported' ? '放水再来' : '看广告·放水再来');
        await choose(page, 2);
        const dismissed = mode === 'closed' || mode === 'skipped';
        if (dismissed) {
          await until(page, () => G.ui.menu && G.ui.menu.options[0] === '再来一次', '关闭后重新选择');
          assert.strictEqual(await page.evaluate(() => G.world.fight.assist), false);
          assert.strictEqual(await page.evaluate(() => G.world.fight.attempt), 1);
          assert.strictEqual(await page.evaluate(() => G.ui.menu.options[2]), label);
          await choose(page, 0);
        }
        await assertRetry(page, !dismissed);
        const notices = await page.evaluate(() => window.__notices);
        assert.deepStrictEqual(await page.evaluate(() => Array.from(G.dbg.missingGlyph)), []);
        const expected = dismissed ? '广告没有看完，没有放水' :
          mode === 'fail' || mode === 'timeout' ? '广告暂时无法播放，本次免费放水' : null;
        if (expected) assert(notices.includes(expected));
        else assert(!notices.some(n => /广告/.test(n) && !/验收/.test(n)));
        assert.deepStrictEqual(errors, []);
        results.push({ mode, label, assist: !dismissed, notices, errors });
        console.log('通过 页面广告分支 ' + mode);
      } finally { await page.close(); }
    }
    // 技术故障使用真封装和假 SDK，timeout 不等待默认的 120 秒。
    for (const fault of ['sdk_missing', 'exception', 'callback_failure', 'timeout']) {
      const { page, errors } = await boot(browser, url, '');
      try {
        await page.evaluate(() => { window.MetaH5Ad = { isAdSupport(t, cb) { cb({ code: 0, data: 1 }); } }; });
        await assistMenu(page);
        assert.strictEqual(await page.evaluate(() => G.ui.menu.options[2]), '看广告·放水再来');
        await page.evaluate(fault => {
          if (fault === 'sdk_missing') delete window.MetaH5Ad;
          if (fault === 'exception') MetaH5Ad.showAd = () => { throw new Error('测试异常'); };
          if (fault === 'callback_failure') MetaH5Ad.showAd = (t, cb) => cb({ code: 1 });
          if (fault === 'timeout') {
            MetaH5Ad.showAd = () => {};
            const original = G.ads.watch;
            G.ads.watch = scene => original(scene, { timeoutMs: 25 });
          }
        }, fault);
        await choose(page, 2);
        await assertRetry(page, true);
        assert((await page.evaluate(() => window.__notices)).includes('广告暂时无法播放，本次免费放水'));
        assert.deepStrictEqual(errors, []);
        results.push({ fault, ok: true });
        console.log('通过 页面技术故障 ' + fault);
      } finally { await page.close(); }
    }
    // 在查询 / 播放期间分别回标题和仅清掉战斗，迟到奖励不能改动下一轮。
    for (const phase of ['support', 'watch']) for (const action of ['title', 'cancelFight']) {
      const { page, errors } = await boot(browser, url, '');
      try {
        await page.evaluate(phase => {
          window.MetaH5Ad = {
            isAdSupport(t, cb) { if (phase === 'support') window.__late = cb; else cb({ code: 0, data: 1 }); },
            showAd(t, cb) { window.__late = cb; }
          };
        }, phase);
        // 第一轮没有放水项，所以不会查询 SDK。
        await lose(page); await choose(page, 0);
        await until(page, () => G.world.combat && G.world.fight.attempt === 1, '普通重试');
        await page.evaluate(() => { G.world.player.hp = 0; });
        if (phase === 'watch') {
          await until(page, () => G.ui.menu && G.ui.menu.options[2] === '看广告·放水再来', '广告菜单');
          await choose(page, 2);
        }
        await until(page, () => typeof window.__late === 'function', 'SDK 等待中');
        await page.evaluate(action => {
          window.__oldFight = G.world.fight;
          if (action === 'title') G.goTitle(); else G.world.fight = null;
        }, action);
        await until(page, () => G.scene.name === 'title' && G.ui.menu && !G.ads.busy, '取消返回标题');
        await page.evaluate(() => { window.__late({ code: 0, data: { status: 4 } }); });
        await tick(page, 30);
        assert.strictEqual(await page.evaluate(() => window.__oldFight.assist), false);
        assert.strictEqual(await page.evaluate(() => G.ads.busy), false);
        assert.deepStrictEqual(errors, []);
        // 新一轮广告可以正常获得一次奖励，旧播放已释放 busy。
        const next = await page.evaluate(async () => { G.ads.setMock('ok'); return G.ads.watch('next'); });
        assert.strictEqual(next.success, true);
        results.push({ phase, action, cancelled: true, nextAd: true });
        console.log('通过 取消 ' + phase + '/' + action);
      } finally { await page.close(); }
    }
    // 直接验证多次回调、过程态、重复点击及只认 status=4。
    const { page, errors } = await boot(browser, url, '');
    try {
      const unit = await page.evaluate(async () => {
        const eventCount = () => G.dbg.events.filter(e => e.type === 'ad_settle').length;
        const before = eventCount();
        window.MetaH5Ad = { showAd(t, cb) { window.__callback = cb; } };
        const p = G.ads.watch('once', { timeoutMs: 1000 });
        let done = false; p.then(() => { done = true; });
        const busy = await G.ads.watch('twice');
        __callback({ code: 0, data: { status: 0 } });
        __callback({ code: 0, data: { status: 3 } });
        __callback({ code: 0, data: { rewarded: true } });
        await Promise.resolve(); const premature = done;
        __callback({ response: JSON.stringify({ code: 0, data: { status: 4 } }) });
        __callback({ code: 0, data: { status: 4 } });
        __callback({ code: 0, data: { status: -1 } });
        const result = await p;
        return { busy: busy.reason, premature, result, settlements: eventCount() - before, playing: G.ads.busy };
      });
      assert.strictEqual(unit.busy, 'busy'); assert.strictEqual(unit.premature, false);
      assert.strictEqual(unit.result.status, 4); assert.strictEqual(unit.result.success, true);
      assert.strictEqual(unit.settlements, 1); assert.strictEqual(unit.playing, false);
      const support = await page.evaluate(async () => {
        MetaH5Ad.isAdSupport = () => { throw new Error('支持查询异常'); };
        const exception = await G.ads.supported();
        MetaH5Ad.isAdSupport = () => {};
        const start = performance.now();
        const timeout = await G.ads.supported();
        const ms = performance.now() - start;
        MetaH5Ad.isAdSupport = (type, cb) => cb({ response: JSON.stringify({ code: 0, data: 1 }) });
        return { exception, timeout, ms, wrapped: await G.ads.supported() };
      });
      assert.strictEqual(support.exception, false); assert.strictEqual(support.timeout, false);
      assert(support.ms >= 2900 && support.ms < 6000); assert.strictEqual(support.wrapped, true);
      assert.deepStrictEqual(errors, []);
      results.push({ sdkCallbacks: unit, support });
      console.log('通过 SDK 多回调与一次性奖励');
    } finally { await page.close(); }
    // 正式页面不能仅凭 adMock 参数进入模拟模式。
    const live = await browser.newPage();
    try {
      await live.goto(url + 'index.html?adMock=ok');
      await live.waitForFunction(() => window.G && G.booted);
      assert.strictEqual(await live.evaluate(() => G.ads.setMock('ok')), false);
      assert.strictEqual(await live.evaluate(() => G.ads.supported()), false);
      results.push({ productionMockRejected: true });
    } finally { await live.close(); }
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => srv.close(resolve));
    fs.writeFileSync(path.join(out, 'ads-report.json'), JSON.stringify(results, null, 2));
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
