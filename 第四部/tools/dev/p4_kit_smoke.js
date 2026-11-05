// 共用招式组的冒烟测试：亿泰·轰炸空间、康一·回音 ACT1（engine/p4_moves.js）真按一遍键，看招式能不能出、有没有报错。
//   借序章的水中项链战当场地（机器人快进到开打，然后关掉机器人），放一个不动的木桩，把亿泰、康一拉进队伍换成队长，按键走 G.input 同一条路径：
//     亿泰：J ×3 → 连按 J 进连打 → 按住 L 按 J 拉近 → K 削步 → 攒满能量按 U
//     康一：J ×3（射拟声字）→ 攒满能量按 U（大音量）
//   判据：每一项都要看到对应的状态 / 位移 / 伤害，页面不能报错。
//   用法：node 第四部/tools/dev/p4_kit_smoke.js [--out 输出目录]   有一项没过或报错时退出码 1
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { serve } = require('./serve');

const argv = process.argv.slice(2);
const OUT = path.resolve(argv.indexOf('--out') >= 0 ? argv[argv.indexOf('--out') + 1] : 'p4_kit_smoke_out');
fs.mkdirSync(OUT, { recursive: true });
const T0 = Date.now();
const log = (...a) => console.log('[' + ((Date.now() - T0) / 1000).toFixed(1) + 's]', ...a);

const PAGE_SETUP = () => {
  const ch = new MessageChannel();
  const yieldTask = () => new Promise((r) => { ch.port1.onmessage = () => r(); ch.port2.postMessage(0); });
  window.__run = async (frames) => { G.dbg.hold = true; for (let i = 0; i < frames; i++) { G.dbg.tick(1); await yieldTask(); } };
};

// 页面里跑：换成 cid 当队长，对着一个不动的木桩（学长A 的样子、血 999、不出招）按键，记下结果。
//   序章这个房间只有 320 宽：每一项开始前把队长挪到左边、木桩放在右边，项链挪到最右边定住（它有自己的剧情机关，别让它掺和）
const DRIVE = async (cid) => {
  const I = G.input, W = () => G.world, P = () => G.world.player, run = window.__run;
  const out = { cid, checks: {} };
  const tap = async (k, hold = 3) => { I.press(k); await run(hold); I.release(k); await run(2); };
  const ready = async () => { for (let i = 0; i < 90; i++) { const p = P(); if (W().combat && !W().cine && !G.ui.menu && p && ['idle', 'walk'].includes(p.state) && !p.atk) return true; await run(5); } return false; };
  G.party.add(cid);
  W().fight.setLead(cid);
  await run(10);
  const p = P();
  out.lead = p && p.cid;
  if (!p || p.cid !== cid) return out;
  p.hp = p.maxHp; p.minHp = 1;
  const st = W().stage, x0 = st.x0, y0 = Math.round((st.yMin + st.yMax) / 2);
  const aq = G.S.actor('aqua');
  const parkAqua = () => { if (!aq) return; aq.mem.hold = true; aq.atk = null; aq.tele = null; aq.minHp = 1; aq.x = st.x1 - 6; aq.y = st.yMin; };
  let dummy = W().fight.enemies().find((e) => e.cid === 'thug_a');
  if (!dummy) dummy = W().fight.spawn({ cid: 'thug_a', x: x0 + 80, y: y0, hp: 999, kit: { hp: 999, speed: 0, moves: [], koStyle: 'none', brain: () => true } });
  const place = async (gap) => {
    parkAqua();
    await ready();
    P().x = x0 + 30; P().y = y0; P().facing = 1;
    dummy.x = x0 + 30 + gap; dummy.y = y0; dummy.hp = 999; dummy.stunT = 0;
    await run(2);
  };
  await place(28);
  const hp0 = dummy.hp;
  for (let i = 0; i < 3; i++) await tap('attack', 3), await run(8);
  await run(30);
  out.checks.combo = hp0 - dummy.hp;
  if (cid === 'okuyasu') {
    await place(30);
    let rushSeen = false;
    for (let i = 0; i < 3; i++) await tap('attack', 3), await run(6);
    for (let i = 0; i < 40; i++) { I.press('attack'); await run(2); I.release('attack'); await run(2); if (P().state === 'rush') rushSeen = true; }
    await run(80);
    out.checks.rush = rushSeen;
    // 拉近：木桩放在 100 px 外，按住 L 再按 J
    await place(100);
    const d0 = Math.round(Math.abs(dummy.x - P().x));
    I.press('guard'); await run(6); I.press('attack'); await run(3); I.release('attack'); await run(12);
    out.checks.pull = [d0, Math.round(Math.abs(dummy.x - P().x))];
    I.release('guard'); await run(10);
    // 削步：往右按 K，位移 ≈ 64
    await place(200);
    const px0 = P().x;
    I.press('right'); await run(1); I.press('dodge'); await run(3); I.release('dodge'); await run(1); I.release('right'); await run(12);
    out.checks.dodge = Math.round(P().x - px0);
  }
  // U：攒满能量
  await place(30);
  G.combat.gainEnergy(P(), 100, 'story');
  const hp1 = dummy.hp;
  let specialSeen = false;
  I.press('special'); await run(3); I.release('special');
  for (let i = 0; i < 60; i++) { await run(5); if (P().state === 'special') specialSeen = true; }
  out.checks.special = specialSeen;
  out.checks.specialDmg = hp1 - dummy.hp;
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
  let reached = false;
  for (let i = 0; i < 4000 && !reached; i++) {
    await page.evaluate((n) => window.__run(n), 30);
    reached = await page.evaluate(() => { const s = G.dbg.snapshot(); return s.fightId === 'b_pro2_aqua' && !!s.combat && !G.world.cine; });
  }
  if (!reached) throw new Error('没走到水中项链战');
  await page.evaluate(() => { window.__bot.manual = true; });
  log('到了水中项链战，机器人已关');
  const results = [];
  for (const cid of ['okuyasu', 'koichi']) {
    const r = await page.evaluate(DRIVE, cid);
    results.push(r);
    log(JSON.stringify(r));
    await page.screenshot({ path: path.join(OUT, cid + '.png') });
  }
  const bad = [];
  for (const r of results) {
    const c = r.checks;
    if (r.lead !== r.cid) bad.push(r.cid + ' 没当上队长');
    if (!(c.combo > 0)) bad.push(r.cid + ' J 没打中');
    if (!c.special) bad.push(r.cid + ' U 没放出来');
    if (r.cid === 'okuyasu') {
      if (!c.rush) bad.push('亿泰 没进连打');
      if (!c.pull || !(c.pull[1] < 40)) bad.push('亿泰 拉近没把人拉过来 ' + JSON.stringify(c.pull));
      if (!(c.dodge >= 50 && c.dodge <= 76)) bad.push('亿泰 削步位移 ' + c.dodge);
    }
  }
  fs.writeFileSync(path.join(OUT, 'result.json'), JSON.stringify({ results, bad, errors }, null, 2));
  log(bad.length || errors.length ? '没通过：' + bad.concat(errors).join('；') : '通过');
  await browser.close(); srv.close();
  process.exit(bad.length || errors.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
