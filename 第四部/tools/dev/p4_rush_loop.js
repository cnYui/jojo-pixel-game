// 连打拳声（ora_loop）会不会漏停。用户实测：欧拉 / 多拉连打以后，拳头的声音一直响、停不下来。
//   拳声循环由 combat.js 的 startRush 开出来，只在 rushTick 里到点才停；连打被别的事打断、或者 rushTick 不再被调用，循环就没人停了。
//   这里把会打断连打的几件事挨个真按一遍（键盘同一条输入路径），看打断以后还有没有拳声循环在响：
//     guard   连打中按住 L 格挡
//     swap    连打中按 Q 换人（水中项链战能换承太郎）
//     special 连打中按 U 放必杀
//     pause   连打中按 Esc 暂停（暂停菜单开着时拳声还在不在响），再选「继续」
//     trap    水中项链战的正式结局：含着手套、在它旁边连打，它钻进嘴里被兜住 → 战斗在连打中结束
//   判据：包住 G.audio.loop，每条循环记着有没有被 stop 过；打断后不再按 J，等 4 秒，还没 stop 的拳声循环就是漏的。
//   前四个场景把项链定在远处、不让它钻嘴：它扑过来打中仗助的话，挨打本身会顺手收掉连打，就看不出打断有没有漏。
//   场景之间不清账：漏下的连打会被下一次连打覆盖、旧循环句柄丢失，最后一行列出到结束都没停的循环。
//   用法：node 第四部/tools/dev/p4_rush_loop.js [--out 输出目录]   有漏停或报错时退出码 1
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { serve } = require('./serve');

const argv = process.argv.slice(2);
const OUT = path.resolve(argv.indexOf('--out') >= 0 ? argv[argv.indexOf('--out') + 1] : 'p4_rush_loop_out');
fs.mkdirSync(OUT, { recursive: true });
const T0 = Date.now();
const log = (...a) => console.log('[' + ((Date.now() - T0) / 1000).toFixed(1) + 's]', ...a);

const PAGE_SETUP = () => {
  const ch = new MessageChannel();
  const yieldTask = () => new Promise((r) => { ch.port1.onmessage = () => r(); ch.port2.postMessage(0); });
  window.__run = async (frames) => { G.dbg.hold = true; for (let i = 0; i < frames; i++) { G.dbg.tick(1); await yieldTask(); } };
  // 记下每一条循环音效：谁开的（开的时候的主控角色）、有没有被 stop
  window.__loops = [];
  const orig = G.audio.loop;
  G.audio.loop = function (name) {
    const h = orig.apply(this, arguments);
    const rec = { name: String(name), t: G.clk.ui, stopped: false, dummy: !!(h && h.dummy), owner: G.world.player ? G.world.player.cid : null };
    window.__loops.push(rec);
    if (h && h.stop) { const os = h.stop; h.stop = function () { if (!rec.stopped) rec.by = (new Error().stack || '').split('\n').slice(2, 6).map((x) => x.trim().replace(/\(?https?:\/\/[^/]+\//, '(')).join(' < '); rec.stopped = true; return os.apply(this, arguments); }; }
    return h;
  };
  window.__liveOra = () => window.__loops.filter((l) => /ora_loop/.test(l.name) && !l.stopped);
};

// 页面里跑的一个场景：打出连打 → 连按 J 保持住 → 打断 → 不再按 J，等着 → 看循环
const SCENARIO = async (name) => {
  const I = G.input, W = () => G.world, P = () => G.world.player, run = window.__run;
  const out = { name };
  const actors = () => (W().stage ? W().stage.actors : []);
  const stale = () => actors().filter((a) => a.rush && a.state !== 'rush').map((a) => a.cid + ':' + a.state);
  const aq = () => G.S.actor('aqua');
  // 等到能动：战斗中、没有演出、没有菜单、仗助在前面站着
  for (let i = 0; i < 120; i++) {
    const p = P();
    if (W().fight && p && p.cid !== 'josuke' && !W().cine) W().fight.setLead('josuke');
    if (W().combat && !W().cine && !G.ui.menu && p && p.cid === 'josuke' && ['idle', 'walk'].includes(p.state) && !p.atk) break;
    await run(10);
  }
  const c = W().fight;
  if (!c || c.id !== 'b_pro2_aqua') { out.skip = '不在水中项链战'; return out; }
  const a0 = aq();
  if (name === 'trap') {
    // 结局条件：拿着手套、它的血在 30% 以下。先把它挪到场地另一头，免得 J3 打中把它打散
    c.data.glove = true; c.data.entryCd = 0; a0.mem.hold = false;
    a0.hp = Math.min(a0.hp, Math.floor(a0.maxHp * 0.25));
  } else {
    // 别的场景要单看“打断”这一件事：项链定住、挪远、不让它钻嘴。不然它扑过来打中仗助，挨打本身会顺手把连打收掉，测不出来
    a0.mem.hold = true; c.data.entryCd = 99;
  }
  a0.x = P().x < 240 ? 450 : 30; a0.atk = null; a0.tele = null;
  const loops0 = window.__loops.length;
  // 打出连打：三下连招接着快速连按
  let got = false;
  for (let tries = 0; tries < 8 && !got; tries++) {
    for (let k = 0; k < 3; k++) { I.inject('attack'); await run(14); }
    for (let k = 0; k < 40 && P().state !== 'rush'; k++) { I.inject('attack'); await run(4); }
    got = P().state === 'rush' && !!P().rush;
    if (!got) await run(60);
  }
  out.gotRush = got;
  if (!got) return out;
  // 连按 J 把连打撑住（不按的话 12 帧后连打自己收尾，测不到打断）
  for (let k = 0; k < 5; k++) { I.inject('attack'); await run(4); }
  const p0 = P();
  out.rushingBefore = p0.state === 'rush' && !!p0.rush;
  out.loopLiveBefore = !!(p0.rush && p0.rush.loop && window.__liveOra().length);
  // —— 打断 ——
  if (name === 'guard') { I.press('guard', 'rl'); await run(20); I.release('guard', 'rl'); }
  else if (name === 'swap') { I.inject('swap'); await run(10); out.leaderAfterSwap = P().cid; }
  else if (name === 'special') { G.combat.gainEnergy(P(), 100); I.inject('special'); await run(10); out.specialStarted = P().state === 'special' || !!W().cine; }
  else if (name === 'pause') {
    I.inject('pause'); await run(30);
    out.pauseMenu = !!(G.ui.menu && G.ui.menu.title === '暂停');
    out.liveDuringPause = window.__liveOra().filter((l) => window.__loops.indexOf(l) >= loops0).map((l) => l.owner + '@' + l.t.toFixed(1));
    I.inject('ok'); await run(10);
    out.resumed = !G.ui.menu;
  } else if (name === 'trap') {
    // 连打中把它摆到面前：张着嘴、48 px 内亮红圈 0.35 s → 钻进来，被手套兜住，战斗结束
    const a = aq();
    if (a.hidden && G.AI.hide) G.AI.hide(a, false);
    a.mem.scatter = 0; a.atk = null; a.tele = null; a.visible = true;
    a.x = P().x + P().facing * 26; a.y = P().y;
    // 钻嘴开始（战斗 tick 写 inMouth = true）的那一刻仗助是不是在连打：修好以后连打会在演出一开始就收掉，事后看 P().rush 已经是空的
    let v = c.data.inMouth, rushAtEntry = null;
    Object.defineProperty(c.data, 'inMouth', { configurable: true, enumerable: true, get: () => v, set: (x) => { if (x && rushAtEntry === null) rushAtEntry = P().state === 'rush' && !!P().rush; v = x; } });
    for (let k = 0; k < 60 && !c.data.trapped; k++) { I.inject('attack'); await run(4); }
    out.trapped = !!c.data.trapped;
    out.trappedWhileRush = out.trapped && rushAtEntry === true;
  }
  // 不再按 J：正常的连打 12 帧内就收尾了。等 4 秒（必杀的演出也走完）
  await run(240);
  const p1 = P();
  out.after = { leader: p1 && p1.cid, state: p1 && p1.state, atk: p1 && p1.atk ? p1.atk.slot : null, anim: p1 && p1.anim, rush: !!(p1 && p1.rush), combat: !!W().combat, cine: !!W().cine, fight: W().fight ? W().fight.id : null };
  out.loopsOpened = window.__loops.length - loops0;
  out.liveOra = window.__liveOra().filter((l) => window.__loops.indexOf(l) >= loops0).map((l) => l.owner + '@' + l.t.toFixed(1));
  out.staleRush = stale();
  out.stoppedBy = window.__loops.slice(loops0).filter((l) => l.by).map((l) => l.by);
  out.leak = out.liveOra.length > 0 || (out.liveDuringPause || []).length > 0;
  if (name !== 'trap' && aq()) { aq().mem.hold = false; c.data.entryCd = 0; }
  return out;
};

(async () => {
  const { srv, url } = await serve();
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
  const errors = [];
  page.on('pageerror', (e) => { errors.push(String(e.message)); log('[pageerror]', e.message); });
  page.on('console', (m) => { if (m.type() === 'error') { errors.push(m.text()); log('[console.error]', m.text()); } });
  await page.goto(url + 'index.html?autotest=1');
  await page.waitForFunction(() => window.G && G.booted && G.ui.menu, null, { timeout: 60000 });
  await page.keyboard.press('Shift');
  await page.waitForTimeout(300);
  await page.evaluate(PAGE_SETUP);
  await page.evaluate((c) => { window.__botCfg = c; }, { read: 0.25, failChase: 0, assist: true, titleWait: 0.3 });
  await page.addScriptTag({ path: path.join(__dirname, 'p4_bot.js') });

  // 机器人快进到水中项链战，开打就把机器人关掉，换这里按键
  let reached = false;
  for (let i = 0; i < 4000 && !reached; i++) {
    await page.evaluate((n) => window.__run(n), 30);
    reached = await page.evaluate(() => { const s = G.dbg.snapshot(); return s.fightId === 'b_pro2_aqua' && !!s.combat; });
  }
  if (!reached) throw new Error('没走到水中项链战');
  await page.evaluate(() => { window.__bot.manual = true; });
  log('到了水中项链战，机器人已关，开始测');

  const results = [];
  for (const name of ['guard', 'swap', 'special', 'pause', 'trap']) {
    const r = await page.evaluate(SCENARIO, name);
    results.push(r);
    log(JSON.stringify(r));
  }
  // 整个过程开过、到最后都没人停的拳声循环（场景之间不清账：漏下的连打被下一次连打覆盖时，旧循环的句柄就丢了，再也停不掉）
  const neverStopped = await page.evaluate(() => window.__liveOra().map((l) => l.owner + '@' + l.t.toFixed(1)));
  log('到最后还在响的拳声循环：', neverStopped.length ? neverStopped.join(' ') : '无');

  fs.writeFileSync(path.join(OUT, 'result.json'), JSON.stringify({ results, neverStopped, errors }, null, 2));
  const leaks = results.filter((r) => r.leak);
  const untested = results.filter((r) => !r.gotRush || r.skip || (r.name === 'trap' && !r.trappedWhileRush));
  log('漏停：', leaks.map((r) => r.name).join(',') || '无', '｜没测成：', untested.map((r) => r.name).join(',') || '无', '｜报错', errors.length);
  await browser.close(); srv.close();
  process.exit(leaks.length || neverStopped.length || untested.length || errors.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
