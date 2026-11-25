// 用真实键盘进入序章并移动；自行启动和关闭静态服务，验收无需预先开服务器。
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
// 使用用户指定的已有依赖，整个验收不安装任何包。
process.env.NODE_PATH = process.env.NODE_PATH || 'D:/CodeWorkSpace/honglou-juan2/node_modules';
require('node:module').Module._initPaths();
const { chromium } = require('playwright');
const out = path.join(__dirname, '_out');

async function main() {
  fs.mkdirSync(out, { recursive: true });
  const errors = [], requests = [];
  const server = spawn(process.env.PYTHON || 'python', [path.join(__dirname, 'p5_serve.py'), '--port', '0'], {
    env: { ...process.env, PYTHONUTF8: '1', PYTHONDONTWRITEBYTECODE: '1' }, windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let browser, page, serverLog = '';
  server.stderr.on('data', data => { serverLog += data.toString(); });
  const ready = new Promise((resolve, reject) => {
    let buffer = '';
    const timer = setTimeout(() => reject(new Error('本地服务器启动超时：' + serverLog)), 15000);
    server.once('error', error => { clearTimeout(timer); reject(error); });
    server.once('exit', code => { clearTimeout(timer); reject(new Error(`服务器提前退出 ${code}：${serverLog}`)); });
    server.stdout.on('data', data => {
      buffer += data.toString();
      if (!buffer.includes('\n')) return;
      try { const value = JSON.parse(buffer.split('\n')[0]); clearTimeout(timer); resolve(value.url); }
      catch (error) { clearTimeout(timer); reject(error); }
    });
  });
  const report = { ok: false, errors, requests };
  try {
    const url = await ready;
    browser = await chromium.launch({ headless: true });
    page = await browser.newPage({ viewport: { width: 960, height: 540 } });
    page.on('pageerror', error => errors.push(error.stack || error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('requestfailed', request => requests.push(request.url() + ' ' + request.failure()?.errorText));
    page.on('response', response => { if (response.status() >= 400) requests.push(`${response.status()} ${response.url()}`); });
    const press = async key => {
      if (key === 'Enter') await page.waitForFunction(() => !G.ui.menu || G.ui.menu.t > .12);
      await page.keyboard.press(key, { delay: 70 });
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    };
    await page.goto(url, { waitUntil: 'load' });
    await page.waitForFunction(() => window.G?.booted && G.scene?.name === 'title' && G.ui.menu?.t > .4);
    assert.equal(await page.title(), 'JoJo的奇妙冒险 黄金之风 · 像素游戏');
    assert.deepEqual(await page.evaluate(() => G.CHAPTERS.filter(c => c.run).map(c => c.key)), ['prologue', 'ch1']);
    await page.screenshot({ path: path.join(out, '01-title.png') });
    await press('Enter');
    await page.waitForFunction(() => window.G?.S.cardOn === true);
    report.chapterCard = await page.evaluate(() => G.uifx.chapter.key);
    // 正式序章在自由走动前有地图与电话对白，必须实际确认，不能再等空壳直接交还操作。
    for (let n = 0; n < 100; n++) {
      if (await page.evaluate(() => G.world.stage?.id === 'airin_pro' && G.world.free && G.fadeA < .01)) break;
      if (await page.evaluate(() => !!(G.ui.dlg || G.ui.narr))) await press('Enter');
      await page.waitForTimeout(100);
    }
    await page.waitForFunction(() => G.world.stage?.id === 'airin_pro' && G.world.free && G.fadeA < .01);
    report.before = await page.evaluate(() => ({ cid: G.world.player.cid, x: G.world.player.x, y: G.world.player.y }));
    assert.equal(report.before.cid, 'koichi');
    await page.keyboard.down('ArrowRight');
    try { await page.waitForFunction(x => G.world.player.x > x + 45, report.before.x); }
    finally { await page.keyboard.up('ArrowRight'); }
    await page.keyboard.down('ArrowDown');
    try { await page.waitForFunction(y => G.world.player.y > y + 8, report.before.y); }
    finally { await page.keyboard.up('ArrowDown'); }
    report.after = await page.evaluate(() => ({ x: G.world.player.x, y: G.world.player.y }));
    await page.screenshot({ path: path.join(out, '02-airport.png') });
    assert(report.after.y <= 176);
    // 从暂停菜单返回标题再选择章节，验证空壳流程可被取消，且灰章不能确认。
    await press('Escape');
    await page.waitForFunction(() => G.ui.menu?.title === '暂停');
    await press('ArrowUp');
    await press('Enter');
    await page.waitForFunction(() => G.scene?.name === 'title' && G.ui.menu);
    await press('ArrowDown');
    await press('Enter');
    await page.waitForFunction(() => G.ui.menu?.title?.startsWith('选择章节'));
    assert.deepEqual(await page.evaluate(() => G.ui.menu.disabled), [2, 3, 4]);
    await press('ArrowDown');
    await press('ArrowDown');
    await press('Enter');
    await page.waitForFunction(() => G.ui.menu?.t > .2);
    assert(await page.evaluate(() => G.ui.menu?.title?.startsWith('选择章节')));
    await press('ArrowUp');
    await press('Enter');
    // 第1章已有开场旁白，和序章一样先真实确认，再检查自由移动。
    for (let n = 0; n < 100; n++) {
      if (await page.evaluate(() => G.world.stage?.id === 'street_ch1' && G.world.free && G.fadeA < .01)) break;
      if (await page.evaluate(() => !!(G.ui.dlg || G.ui.narr))) await press('Enter');
      await page.waitForTimeout(100);
    }
    await page.waitForFunction(() => G.world.stage?.id === 'street_ch1' && G.world.free && G.fadeA < .01);
    assert.equal(await page.evaluate(() => G.world.player.cid), 'giorno');
    const x = await page.evaluate(() => G.world.player.x);
    await page.keyboard.down('ArrowRight');
    try { await page.waitForFunction(before => G.world.player.x > before + 20, x); }
    finally { await page.keyboard.up('ArrowRight'); }
    report.snapshot = await page.evaluate(() => G.dbg.snapshot());
    report.save = await page.evaluate(() => ({ p5: G.store.get('p5-progress', null), p4: G.store.get('p4-progress', null) }));
    assert(report.save.p5);
    assert.equal(report.save.p4, null);
    for (const key of ['missingImg', 'missingHead', 'missingGlyph', 'missingSfx']) assert.deepEqual(report.snapshot[key], [], key);
    assert.deepEqual(errors, [], '浏览器控制台错误');
    assert.deepEqual(requests, [], '网络资源错误');
    report.ok = true;
    console.log('PASS：标题 → 序章篇章卡 → airin_pro真实键盘移动 → 暂停回标题 → 灰章不可选 → 第1章移动；控制台0错误，截图2张。');
  } catch (error) {
    report.failure = error.stack || String(error);
    if (page) report.snapshot = await page.evaluate(() => window.G?.dbg?.snapshot()).catch(() => null);
    throw error;
  } finally {
    fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
    if (browser) await browser.close();
    if (server.exitCode === null) {
      const closed = new Promise(resolve => server.once('exit', resolve));
      server.kill();
      await closed;
    }
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
