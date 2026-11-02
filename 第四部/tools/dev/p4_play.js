// 第四部序章整章自动试玩（Node + Playwright，用容器里预装的 Chromium）：标题 → 序章 → 「序章　完」。
//   默认“快进”模式：G.dbg.hold 停住主循环，一帧一帧 G.dbg.tick 推进，每帧之间让出一次事件循环（剧情的 await 照常接上），
//   所以几分钟就能跑完一整章，结果和实时玩一样。--record 换成实时模式，同时注入录屏脚本录下画面和声音。
//   用法：
//     node 第四部/tools/dev/p4_play.js --out 输出目录 [--read 0.25] [--fail-chase 2] [--size 960x540]
//     node 第四部/tools/dev/p4_play.js --record 输出目录/序章.webm --size 1920x1080 --read 1
//   输出：剧情标记截图（编号_标记.png）、report.json（标记、战斗、机器人日志、报错、缺图缺字）。
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { serve } = require('./serve');

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const flag = (k) => argv.indexOf(k) >= 0;
const RECORD = opt('--record', null);
const OUT = path.resolve(opt('--out', RECORD ? path.dirname(RECORD) : 'p4_play_out'));
const READ = parseFloat(opt('--read', RECORD ? '1' : '0.25'));
const FAIL_CHASE = parseInt(opt('--fail-chase', '0'), 10);
const [VW, VH] = opt('--size', RECORD ? '1920x1080' : '960x540').split('x').map(Number);
const MAX_GAME_MIN = parseFloat(opt('--max-min', '45'));
const SHOTS = !flag('--no-shots');
const TITLE_WAIT = parseFloat(opt('--title-wait', RECORD ? '4' : '0.5'));
const STOP_AFTER = parseFloat(opt('--stop-after', '0'));      // 试录用：实时模式下录这么多秒就停
const DLG_SHOTS = parseInt(opt('--dlg-shots', '0'), 10);        // 每隔几句对白截一张（看对白框的排版）
const REC_JS = path.resolve(__dirname, '..', '..', '..', 'tools', 'dev', 'record', 'recorder.js');

fs.mkdirSync(OUT, { recursive: true });
const report = { started: new Date().toISOString(), mode: RECORD ? 'record' : 'fast', read: READ, failChase: FAIL_CHASE,
  marks: [], stages: [], fights: [], notes: [], errors: [], console: [], missing: {}, end: null };
const log = (...a) => console.log('[' + ((Date.now() - T0) / 1000).toFixed(1) + 's]', ...a);
const T0 = Date.now();

// 页面里的小工具：标记钩子 + 快进推进器
const PAGE_HELPERS = () => {
  window.__marks = [];
  const om = G.S.mark;
  G.S.mark = function (n) { window.__marks.push([Math.round(G.clk.ui * 10) / 10, n]); return om.apply(this, arguments); };
  const ch = new MessageChannel();
  const yieldTask = () => new Promise((r) => { ch.port1.onmessage = () => r(); ch.port2.postMessage(0); });
  // 推进 frames 帧；途中出了新的剧情标记就提前停（好让外面截图截到那一刻）
  window.__run = async (frames) => {
    G.dbg.hold = true;
    const n0 = window.__marks.length;
    for (let i = 0; i < frames; i++) {
      G.dbg.tick(1);
      await yieldTask();
      if (window.__marks.length !== n0) return i + 1;
    }
    return frames;
  };
};
const STATE = () => {
  const s = G.dbg.snapshot(), b = window.__bot || {};
  return {
    clk: Math.round(G.clk.ui * 10) / 10, scene: s.scene, stage: s.stage, free: s.free, busy: s.busy, combat: s.combat,
    fightId: s.fightId, fightHint: s.fightHint, hp: s.hp, leader: s.leader, px: s.px, py: s.py, dlg: s.dlg, ddone: s.ddone, narr: s.narr, notice: s.notice,
    menu: s.menu, menuItems: s.menuItems, qte: s.qte && s.qte.type, hint: s.hint, timer: s.timer, gauge: s.gauge,
    missingImg: s.missingImg, missingGlyph: s.missingGlyph, missingHead: s.missingHead, missingSfx: s.missingSfx, fallbacks: s.fallbacks,
    evTotals: s.evTotals, loopErrors: (G.dbg.events || []).filter((e) => /error/.test(e.type)).map((e) => e.type + ':' + (e.msg || e.where || '')),
    marks: window.__marks.splice(0), botNotes: (b.notes || []).splice(0), botErr: b.err || null, finished: !!b.finished, fps: s.fps,
  };
};

(async () => {
  const { srv, url } = await serve();
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage({ viewport: { width: VW, height: VH } });
  page.on('console', (m) => { if (m.type() === 'error') { report.console.push(m.text()); log('[console.error]', m.text()); } });
  page.on('pageerror', (e) => { report.errors.push(String(e.stack || e.message)); log('[pageerror]', e.message); });
  let recFiles = null;
  if (RECORD) {
    recFiles = {};
    await page.exposeFunction('__recSave', (k, b64) => {
      const fp = k === 'full' ? RECORD : RECORD.replace(/\.webm$/, '') + '_' + k + '.webm';
      recFiles[k] = fp;
      fs.appendFileSync(fp, Buffer.from(b64, 'base64'));
    });
    for (const fp of [RECORD, RECORD.replace(/\.webm$/, '') + '_bgm.webm', RECORD.replace(/\.webm$/, '') + '_sfx.webm']) if (fs.existsSync(fp)) fs.unlinkSync(fp);
  }
  await page.goto(url + 'index.html?autotest=1');
  await page.waitForFunction(() => window.G && G.booted && G.ui.menu, null, { timeout: 60000 });
  // 声音要一次真的按键才解锁（input.js 在 keydown 里 unlock）：按一下 Shift，不对应任何动作
  await page.keyboard.press('Shift');
  await page.waitForTimeout(300);
  await page.evaluate(PAGE_HELPERS);
  await page.evaluate((c) => { window.__botCfg = c; }, { read: READ, failChase: FAIL_CHASE, assist: true, titleWait: TITLE_WAIT });
  await page.addScriptTag({ path: path.join(__dirname, 'p4_bot.js') });
  if (RECORD) {
    await page.evaluate(() => { window.__recCleanUI = false; });
    await page.addScriptTag({ path: REC_JS });
    log('录屏开始', RECORD);
  }
  let shotN = 0, lastStage = null, lastFight = null, lastProgress = 0, lastProgressT = 0;
  const shot = async (name) => {
    if (!SHOTS) return;
    const fp = path.join(OUT, String(++shotN).padStart(2, '0') + '_' + name.replace(/[^\w一-龥-]/g, '_') + '.png');
    await page.screenshot({ path: fp });
  };
  if (!RECORD) await shot('title');
  const t0 = Date.now();
  for (;;) {
    if (RECORD) await page.waitForTimeout(250);
    else await page.evaluate((n) => window.__run(n), 30);
    const s = await page.evaluate(STATE);
    for (const n of s.botNotes) { report.notes.push(n); if (!/^(menu|task|task_done)$/.test(n.k)) log('bot', JSON.stringify(n)); }
    if (s.botErr && !report.botErr) { report.botErr = s.botErr; log('BOT ERROR', s.botErr); }
    for (const [t, m] of s.marks) {
      report.marks.push({ t, mark: m, stage: s.stage });
      log('mark', m, '@', t);
      lastProgress = s.clk; await shot(m);
    }
    if (s.stage !== lastStage) { lastStage = s.stage; report.stages.push({ t: s.clk, stage: s.stage }); log('stage', s.stage); lastProgress = s.clk; }
    if (s.fightId !== lastFight) {
      if (s.fightId) { report.fights.push({ t: s.clk, id: s.fightId }); log('fight', s.fightId); await shot(s.fightId + '_start'); }
      lastFight = s.fightId; lastProgress = s.clk;
    }
    if (RECORD && Date.now() - (report.fpsT || 0) > 10000) { report.fpsT = Date.now(); (report.fpsLog = report.fpsLog || []).push([s.clk, s.fps]); log('fps', JSON.stringify(s.fps), 'stage', s.stage); }
    if (s.fightId && s.clk - lastProgressT > 10) { lastProgressT = s.clk; log('  ', s.fightId, JSON.stringify(s.fightHint), 'hp', s.hp, 'gauge', JSON.stringify(s.gauge), 'timer', s.timer); }
    if (s.dlg || s.narr) lastProgress = Math.max(lastProgress, s.clk - 0);   // 对话在走也算进展
    if (DLG_SHOTS && s.dlg && s.ddone && s.dlg !== report.lastDlg) {
      report.lastDlg = s.dlg; report.dlgN = (report.dlgN || 0) + 1;
      if (report.dlgN % DLG_SHOTS === 1) await shot('dlg' + report.dlgN);
    }
    // 拟声字没有专门的图时引擎用字库画（ui_cards.js drawWord），不算缺图
    for (const k of ['missingImg', 'missingGlyph', 'missingHead', 'missingSfx', 'fallbacks']) {
      const v = (s[k] || []).filter((x) => !/^ui\/sfx\//.test(x));
      if (v.length) report.missing[k] = v;
    }
    if (s.loopErrors.length) report.loopErrors = s.loopErrors;
    if (s.finished && s.scene === 'title') { report.end = { ok: true, t: s.clk }; log('结束：回到标题'); break; }
    if (STOP_AFTER && (Date.now() - t0) / 1000 > STOP_AFTER) { report.end = { ok: false, why: 'stop_after', t: s.clk }; log('试录到点'); break; }
    if (s.clk > MAX_GAME_MIN * 60) { report.end = { ok: false, why: 'max_time', state: s }; log('超时'); break; }
    if (s.clk - lastProgress > 150) { report.end = { ok: false, why: 'stall', state: s }; log('卡住', JSON.stringify(s)); await shot('stall'); break; }
  }
  report.gameSeconds = (await page.evaluate(() => G.clk.ui));
  report.realSeconds = (Date.now() - t0) / 1000;
  if (RECORD) {
    await page.waitForTimeout(1500);
    await page.evaluate(() => window.__recStop());
    await page.waitForFunction(() => window.__recPending === 0, null, { timeout: 120000 });
    report.recFiles = recFiles;
    log('录屏结束', JSON.stringify(recFiles));
  }
  report.hair = await page.evaluate(() => G.store.get('p4-hair', []));
  fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
  log('报告', path.join(OUT, 'report.json'), '标记', report.marks.length, '报错', report.errors.length + report.console.length);
  await browser.close();
  srv.close();
})().catch((e) => { console.error(e); process.exit(1); });
