// 打击感“改前 / 改后”对比录制（第四部）：同一份输入脚本、固定随机种子、60 Hz 逐步推进，每帧导出游戏的真实画面（G.screen，1280×720）并记统计。
//   场景：借序章的水中项链战当场地（机器人快进到开打，然后关掉机器人，同 p4_kit_smoke.js），仗助对一个不动的木桩：
//     J1 → J2 → J3 重击 → 连按 J 进连打 → 停手收尾（连打终结）→ 把木桩打到撞墙。
//   用法：
//     node 第四部/tools/dev/p4_hitfeel_record.js --out 输出目录 --tag before|after [--root 要录的 worktree，默认本脚本所在的] [--frames 600]
//                                              [--seed 20261124] [--explore]（只跑场景、打印命中表，不导出画面）
//   输出：<out>/frames_<tag>/f00000.png …、<out>/stats_<tag>.json（逐帧世界时间倍率 / 顿帧剩余 / 木桩 x / 闪白 alpha / 抖动 / 压扁 + 命中表）
//   视频和帧条由 tools/dev/p4_hitfeel_encode.py 拼。
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { serve } = require('./serve');

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const flag = (k) => argv.indexOf(k) >= 0;
const ROOT = path.resolve(opt('--root', path.resolve(__dirname, '..', '..', '..')));
const OUT = path.resolve(opt('--out', 'hitfeel_out'));
const TAG = opt('--tag', 'run');
const FRAMES = parseInt(opt('--frames', '600'), 10);
const SEED = parseInt(opt('--seed', '20261124'), 10);
const EXPLORE = flag('--explore');
const DX0 = parseInt(opt('--gap-from-wall', '150'), 10);       // 仗助站位离右墙多远（调场景用）
const T0 = Date.now();
const log = (...a) => console.log('[' + ((Date.now() - T0) / 1000).toFixed(1) + 's]', ...a);

// 输入脚本（逻辑帧，每一轮从自己的 start 帧起算；两边完全一样）：
//   一轮 = J1、J2、J3（重击）→ 每 4 帧点一下 J 进连打 → 停手（连打终结）→ 木桩被打到撞墙；
//   二轮 = 必杀 U（先把能量加满；演出走完后最后一击把木桩打飞）；三轮 = 和一轮一样。每轮开头把仗助和木桩放回右墙边的老位置。
const ROUNDS = [
  { start: 0, taps: [20, 31, 44], mash: [80, 118, 4] },
  { start: 175, taps: [], special: 20, energy: true },
  { start: 395, taps: [20, 31, 44], mash: [80, 118, 4] },
];
const INPUT = { rounds: ROUNDS };
const VARIANTS = [];

const PAGE_SETUP = (seed) => {
  const ch = new MessageChannel();
  const yieldTask = () => new Promise((r) => { ch.port1.onmessage = () => r(); ch.port2.postMessage(0); });
  window.__run = async (frames) => { G.dbg.hold = true; for (let i = 0; i < frames; i++) { G.dbg.tick(1); await yieldTask(); } };
};

// 场景准备（页面里跑）：仗助当队长，木桩放在右墙边，其余敌人藏起来；返回场景几何
const PREP = async (cfg) => {
  const I = G.input, W = () => G.world, P = () => G.world.player, run = window.__run;
  const ready = async () => { for (let i = 0; i < 90; i++) { const p = P(); if (W().combat && !W().cine && !G.ui.menu && p && ['idle', 'walk'].includes(p.state) && !p.atk) return true; await run(5); } return false; };
  G.party.add('josuke');
  W().fight.setLead('josuke');
  await run(10);
  await ready();
  const p = P();
  if (cfg.again) { G.combat.resetActor(p); await run(2); await ready(); }
  p.hp = p.maxHp; p.minHp = 1;
  const st = W().stage, y0 = Math.round((st.yMin + st.yMax) / 2), [lo, hi] = st.bounds();
  // 其余敌人（水中项链等）藏起来、不出招
  for (const e of W().fight.enemies()) { if (e.cid === 'thug_a') continue; e.mem.hold = true; e.atk = null; e.tele = null; e.minHp = 1; e.brain = () => true; G.AI.hide(e, true); }
  let dummy = W().fight.enemies().find((e) => e.cid === 'thug_a');
  if (!dummy) dummy = W().fight.spawn({ cid: 'thug_a', x: hi - 60, y: y0, hp: 999, kit: { hp: 999, speed: 0, moves: [], koStyle: 'none', brain: () => true } });
  dummy.brain = () => true; dummy.mem.hold = true; dummy.atk = null; dummy.tele = null; dummy.minHp = 1; dummy.hp = dummy.maxHp = 99999; dummy.stunT = 0; dummy.poiseMax = 0; dummy.poise = 0;
  G.AI.hide(dummy, false);
  const px = hi - cfg.gapFromWall;
  window.__place = { px, y0 };
  p.x = px; p.y = y0; p.facing = 1; p.energy = 0;
  dummy.x = px + 26; dummy.y = y0; dummy.facing = -1;
  await run(4);
  return { lead: P().cid, lo, hi, x0: st.x0, x1: st.x1, px: p.x, dx: dummy.x, y: y0, screen: [G.screen.width, G.screen.height], enemies: W().fight.enemies().map((e) => [e.cid, e.untargetable]) };
};

// 每帧（页面里跑）：按脚本给输入，推一步，记这一帧的画面输入。window.__hf 在 INSTALL 里装
const INSTALL = (input) => {
  const W = () => G.world, P = () => G.world.player;
  window.__input = input;
  const dummy = W().fight.enemies().find((e) => e.cid === 'thug_a');
  if (window.__hf && window.__hf.dummy === dummy) { Object.assign(window.__hf, { i: 0, hits: [], sfx: [], frames: [] }); return; }
  const cur = { target: dummy, atlases: [dummy.atlas].concat(dummy.alt || []), last: null };
  for (const at of cur.atlases) {
    if (!at || at.__hf) continue;
    const od = at.draw; at.__hf = true;
    at.draw = function (g, logical, frame, x, y, o) {
      if (cur.atlases.indexOf(this) >= 0) cur.last = { x, y, flash: (o && o.flash) || 0, onScreen: g === G.wg };
      return od.apply(this, arguments);
    };
  }
  const hf = window.__hf = { i: 0, hits: [], sfx: [], frames: [], dummy };
  // 命中表：战斗事件 hit（combat.hit 末尾 emit）
  const fight = W().fight, oe = fight.emit;
  fight.emit = function (type, data) {
    if ((type === 'hit') && data && data.t === dummy) {
      hf.hits.push({ frame: hf.i, round: hf.round, slot: data.slot, dmg: data.dmg, guard: !!data.guard, rushHits: data.rushHits || 0, stopAll: (data.move && data.move.stopAll) || 0, push: (data.move && data.move.push) || 0, flashTarget: (data.move && data.move.flashTarget) || 0, x: dummy.x });
    }
    return oe.apply(this, arguments);
  };
  const os = G.audio.sfx;
  G.audio.sfx = function (name) { if (name === 'wall_slam') hf.sfx.push({ frame: hf.i, name }); return os.apply(this, arguments); };
  window.__frame = (i, wantPng) => {
    hf.i = i;
    const I = G.input, input = window.__input;
    let rd = input.rounds[0], ri = 0;
    for (let k = 0; k < input.rounds.length; k++) if (i >= input.rounds[k].start) { rd = input.rounds[k]; ri = k; }
    const rel = i - rd.start;
    hf.round = ri;
    if (rel === 0 && ri > 0) {
      // 新一轮：人和木桩放回老位置，状态清干净（脚本动作，两边一样）；能量加满留给必杀
      const p = P(), pl = window.__place;
      I.clear();
      G.combat.resetActor(p); p.hp = p.maxHp; p.minHp = 1;
      p.x = pl.px; p.y = pl.y0; p.facing = 1; p.hold = false;
      Object.assign(dummy, { x: pl.px + 26, y: pl.y0, facing: -1, _push: null, atk: null, tele: null, stunT: 0, stopT: 0, flash: 0, _flashFx: null, _squash: null, _shakeUntil: 0, invuln: 0, iframe: 0, hp: 99999, rootT: 0, breakT: 0, chainT: 0 });
      dummy.state = 'idle'; dummy.stateT = 0; dummy.play(dummy.idleAnim || 'idle');
      if (rd.energy) G.combat.gainEnergy(p, 100, 'story');
    }
    let press = false;
    if (rd.taps.indexOf(rel) >= 0) press = true;
    if (rd.mash && rel >= rd.mash[0] && rel <= rd.mash[1] && (rel - rd.mash[0]) % rd.mash[2] === 0) press = true;
    if (press) I.inject('attack');
    if (rd.special != null && rel === rd.special) I.inject('special');
    const w0 = G.clk.world, hs0 = G.hitStopAll_t, x0 = dummy.x, p0 = P();
    cur.last = null;
    G.dbg.tick(1);
    const d = cur.last, p = P();
    const rec = {
      i, round: hf.round, press, wm: Math.round((G.clk.world - w0) * 60 * 1e4) / 1e4, hs: Math.round(hs0 * 60 * 1e3) / 1e3,
      x: Math.round(dummy.x * 1e3) / 1e3, dx: Math.round((dummy.x - x0) * 1e3) / 1e3, st: dummy.state, hp: Math.round(dummy.hp),
      flash: d ? Math.round(d.flash * 1e3) / 1e3 : null,
      shake: d && d.onScreen ? Math.round((d.x - dummy.x + (G.cam.x || 0)) * 1e3) / 1e3 : null,
      squash: d ? !d.onScreen : null,
      px: Math.round(p.x * 100) / 100, pst: p.state, atk: p.atk ? p.atk.slot : null, atkT: p.atk ? Math.round(p.atkT * 60) : null,
      sx: dummy.x - (G.cam.x || 0), sy: dummy.y - (dummy.z || 0) - (G.cam.y || 0),
    };
    hf.frames.push(rec);
    return { rec, png: wantPng ? G.screen.toDataURL('image/png') : null };
  };
};

(async () => {
  const { srv, url } = await serve(path.join(ROOT, '第四部', '游戏'));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => { errors.push(String(e.message)); log('[pageerror]', e.message); });
  page.on('console', (m) => { if (m.type() === 'error') { errors.push(m.text()); log('[console.error]', m.text()); } });
  // 固定随机种子：mulberry32 顶掉 Math.random（粒子、AI 的随机都走它）
  await page.addInitScript((seed) => {
    let s = seed >>> 0;
    Math.random = () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }, SEED);
  await page.goto(url + 'index.html?autotest=1');
  await page.waitForFunction(() => window.G && G.booted && G.ui.menu, null, { timeout: 60000 });
  await page.keyboard.press('Shift');
  await page.waitForTimeout(300);
  await page.evaluate(PAGE_SETUP, SEED);
  await page.evaluate((c) => { window.__botCfg = c; }, { read: 0.25, failChase: 0, assist: true, titleWait: 0.3 });
  await page.addScriptTag({ path: path.join(ROOT, '第四部', 'tools', 'dev', 'p4_bot.js') });
  let reached = false;
  for (let i = 0; i < 4000 && !reached; i++) {
    await page.evaluate((n) => window.__run(n), 30);
    reached = await page.evaluate(() => { const s = G.dbg.snapshot(); return s.fightId === 'b_pro2_aqua' && !!s.combat && !G.world.cine; });
  }
  if (!reached) throw new Error('没走到水中项链战');
  await page.evaluate(() => { window.__bot.manual = true; });
  log('到了水中项链战，机器人已关');
  const runs = [0];
  let geo = null;
  for (let vi = 0; vi < runs.length; vi++) {
    geo = await page.evaluate(PREP, { gapFromWall: DX0, again: vi > 0 });
    log('场景', JSON.stringify(geo));
    if (geo.lead !== 'josuke') throw new Error('队长不是仗助：' + geo.lead);
    if (!EXPLORE && (geo.screen[0] !== 1280 || geo.screen[1] !== 720)) throw new Error('画面不是 1280×720：' + geo.screen);
    await page.evaluate(INSTALL, INPUT);
    const fdir = path.join(OUT, 'frames_' + TAG);
    if (!EXPLORE) fs.mkdirSync(fdir, { recursive: true });
    for (let i = 0; i < FRAMES; i++) {
      const r = await page.evaluate(([n, png]) => window.__frame(n, png), [i, !EXPLORE]);
      if (r.png) fs.writeFileSync(path.join(fdir, 'f' + String(i).padStart(5, '0') + '.png'), Buffer.from(r.png.split(',')[1], 'base64'));
      if (i % 100 === 99) log('帧', i + 1);
    }
    if (runs.length > 1) {
      const d = await page.evaluate(() => ({ hits: window.__hf.hits, sfx: window.__hf.sfx }));
      console.log('变体 mashTo=' + runs[vi], '命中帧', JSON.stringify(d.hits.map((h) => h.slot + '@' + h.frame)), '撞墙', JSON.stringify(d.sfx.map((s) => s.frame)));
    }
  }
  const data = await page.evaluate(() => ({ frames: window.__hf.frames, hits: window.__hf.hits, sfx: window.__hf.sfx }));
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, 'stats_' + TAG + '.json'), JSON.stringify({ tag: TAG, root: ROOT, seed: SEED, input: INPUT, geo, frames: data.frames, hits: data.hits, sfx: data.sfx, errors }, null, 1));
  for (const h of data.hits) console.log('命中', JSON.stringify(h));
  console.log('撞墙', JSON.stringify(data.sfx));
  console.log('错误', JSON.stringify(errors));
  await browser.close(); srv.close();
  process.exit(errors.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
