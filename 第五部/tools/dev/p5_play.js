// 照第四部的逐帧试玩方式加速时钟；输入经过真正的键盘事件，截图和报告仅写本部_out。
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
process.env.NODE_PATH ||= 'D:/CodeWorkSpace/honglou-juan2/node_modules';
require('node:module').Module._initPaths();
const { chromium } = require('playwright');
const { P5Bot } = require('./p5_bot');
const out = path.join(__dirname, '_out/play');
const report = { ok: false, errors: [], requests: [], marks: [], dialogs: [], fights: [], shots: [] };

const read = () => {
  const s = G.dbg.snapshot(), c = G.world.fight, d = c?.data;
  const h = d?.charge?.h;
  return { ...s, cine: !!G.world.cine, attempt: c?.attempt,
    taxi: c ? { x: G.S.actor('taxi')?.x, z: G.S.actor('taxi')?.z, warnLeft: h && h.phase === 'warn' ? h.warn - h.t : -1,
      active: h?.phase === 'active', ...c.spec.testHint(c) } : null,
    marks: window.__p5marks.splice(0), tbc: G.uifx.misc.some(x => x.kind === 'tbc' && x.t >= x.hit),
    errors: G.dbg.events.filter(e => /error|api_missing/.test(e.type)),
  };
};
async function main() {
  fs.mkdirSync(out, { recursive: true });
  const server = spawn(process.env.PYTHON || 'python', [path.join(__dirname, 'p5_serve.py'), '--port', '0'], {
    windowsHide: true, env: { ...process.env, PYTHONUTF8: '1', PYTHONDONTWRITEBYTECODE: '1' }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  let browser, page, stderr = '';
  server.stderr.on('data', b => { stderr += b; });
  const ready = new Promise((resolve, reject) => {
    let text = '';
    const timer = setTimeout(() => reject(new Error('服务启动超时 ' + stderr)), 15000);
    server.once('error', reject);
    server.stdout.on('data', b => {
      text += b;
      if (text.includes('\n')) { clearTimeout(timer); resolve(JSON.parse(text.split('\n')[0]).url); }
    });
  });
  try {
    const url = await ready;
    browser = await chromium.launch({ headless: !process.argv.includes('--headed') });
    page = await browser.newPage({ viewport: { width: 960, height: 540 } });
    page.on('pageerror', e => report.errors.push(e.stack || String(e)));
    page.on('console', m => { if (m.type() === 'error') report.errors.push(m.text()); });
    page.on('requestfailed', r => report.requests.push(r.url() + ' ' + r.failure()?.errorText));
    page.on('response', r => { if (r.status() >= 400) report.requests.push(r.status() + ' ' + r.url()); });
    await page.goto(url + '?autotest=1');
    await page.waitForFunction(() => window.G?.booted && G.ui.menu?.t > .2);
    await page.keyboard.press('Shift');
    await page.evaluate(() => {
      G.dbg.hold = true; window.__p5marks = [];
      const old = G.S.mark;
      G.S.mark = function (mark) { window.__p5marks.push({ mark, t: G.clk.ui }); return old.call(this, mark); };
      const channel = new MessageChannel();
      const yieldTask = () => new Promise(r => { channel.port1.onmessage = r; channel.port2.postMessage(0); });
      window.__p5step = async frames => {
        const n0 = window.__p5marks.length;
        for (let n = 0; n < frames; n++) {
          G.dbg.tick(1); await yieldTask();
          if (window.__p5marks.length !== n0) break;
        }
      };
    });
    const bot = new P5Bot(page), seen = new Set();
    const shot = async name => {
      if (seen.has(name)) return;
      seen.add(name); await bot.step(/card/.test(name) ? 30 : name === 'p5_taxi_freeze' ? 20 : 4);
      const file = String(report.shots.length + 1).padStart(2, '0') + '_' + name + '.png';
      await page.screenshot({ path: path.join(out, file) }); report.shots.push(file);
    };
    await shot('title');
    const t0 = Date.now();
    for (let i = 0; i < 14000; i++) {
      const s = await page.evaluate(read);
      report.last = s;
      if (i % 250 === 0) console.log('进度', i, s.stage, s.px, s.py, s.hp, s.fightId, s.attempt, bot.hallWait.toFixed(1), s.free, s.busy);
      for (const m of s.marks) {
        report.marks.push(m);
        if (!['p5_taxi_hit', 'p5_taxi_collision'].includes(m.mark)) { console.log(m.mark); await shot(m.mark); }
      }
      if (s.chapter) await shot('chapter_card');
      if (s.tbc) await shot('to_be_continued');
      if (s.hint?.includes('出租车在右边')) await shot('hall_45s_arrow');
      if (s.dlg && !report.dialogs.some(d => d.text === s.dlg)) report.dialogs.push({ who: s.dwho, text: s.dlg, pages: s.dlen });
      if (s.fightId) {
        report.fights.push({ attempt: s.attempt, hp: s.hp, ...s.taxi });
        if (s.hp <= 0) { report.idleLoss = s; await shot('idle_loss'); }
        if (s.attempt === 1 && !report.retryStart && s.combat) report.retryStart = s;
      }
      if (s.errors.length || report.errors.length) throw new Error('游戏运行报错');
      if (await bot.act(s)) break;
      await bot.step(8);
      if (Date.now() - t0 > 240000) throw new Error('试玩超过四分钟');
    }
    const end = await page.evaluate(read);
    assert.equal(end.stage, 'street_ch1'); assert.equal(end.leader, 'giorno');
    assert(bot.failed && bot.retry && report.idleLoss, '不操作应输并走重试');
    assert.equal(report.retryStart.hp, 100, '重试满血');
    assert.equal(report.retryStart.taxi.durability, 280, '重试恢复耐久');
    assert(bot.arrowSeen, '45秒后出现出口箭头');
    for (const id of ['info', 'flight', 'passer_m', 'passer_f', 'belt'])
      assert(report.marks.some(m => m.mark === 'p5_inspect_' + id), '未调查 ' + id);
    for (const mark of ['p5_map_stamp', 'p5_luggage_stolen', 'p5_echoes_card', 'p5_taxi_freeze',
      'p5_taxi_win', 'p5_banknote', 'p5_goldexp_card', 'p5_suitcase', 'p5_frog', 'p5_frog_hop', 'p5_prologue_end'])
      assert(report.marks.some(m => m.mark === mark), '缺关键节拍 ' + mark);
    assert(report.fights.some(f => f.attempt === 1 && f.dodges > 0 && f.collisions === 0 && f.warnings > 0), 'K闪开倒车');
    assert(report.fights.some(f => f.attempt === 1 && f.freezes > 0 && f.hits > 1), 'J和U真实造成耐久削减');
    const frozen = report.fights.filter(f => f.attempt === 1 && f.freeze > 0 && f.z === -4);
    assert(frozen.length > 5 && new Set(frozen.map(f => f.x)).size === 1, '冻结时车下沉并停住');
    assert(report.marks.some(m => m.mark === 'p5_taxi_thaw'), '四秒后解除冻结');
    for (const field of ['missingImg', 'missingGlyph', 'missingHead', 'missingSfx', 'fallbacks']) assert.deepEqual(end[field], [], field);
    assert(report.dialogs.every(d => d.pages === 1), '对话不应拆页');
    assert.deepEqual(report.errors, []); assert.deepEqual(report.requests, []);
    report.save = await page.evaluate(() => G.store.get('p5-progress', null));
    assert.equal(report.save.max, 1); assert.equal(report.save.last, 1);
    await shot('chapter1_entry');
    // 重载页面读同一份存档，再用标题「继续」验证入口，避免把内存进度当持久存档。
    await page.reload();
    await page.waitForFunction(() => G.booted && G.ui.menu?.t > .3);
    assert.equal(await page.evaluate(() => G.ui.menu.options[0]), '继续');
    await page.keyboard.press('Enter', { delay: 70 });
    await page.waitForFunction(() => G.world.stage?.id === 'street_ch1' && G.world.free);
    report.resume = await page.evaluate(() => ({ stage: G.world.stage.id, cid: G.world.player.cid, p4: G.store.get('p4-progress', null) }));
    assert.equal(report.resume.cid, 'giorno'); assert.equal(report.resume.p4, null);
    report.ok = true;
    const stale = path.join(out, 'failure.png');
    if (fs.existsSync(stale)) fs.unlinkSync(stale);
    console.log('PASS：真实键盘从标题到第1章；45秒箭头与五处调查；不操作失败、满血重试、K闪避、J连打、U冻结；存档继续；控制台0错误。');
  } catch (e) {
    report.failure = e.stack || String(e);
    if (page) { report.last = await page.evaluate(() => window.G?.dbg?.snapshot()).catch(() => null);
      await page.screenshot({ path: path.join(out, 'failure.png') }).catch(() => {}); }
    throw e;
  } finally {
    fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
    if (browser) await browser.close();
    if (server.exitCode === null) { const closed = new Promise(r => server.once('exit', r)); server.kill(); await closed; }
  }
}
main().catch(e => { console.error(e); process.exitCode = 1; });
