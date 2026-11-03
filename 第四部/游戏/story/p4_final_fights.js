// 终章　杜王町 / 钻石是不会碎的：第 19 战「杀手皇后 + 猫草」五段（开发脚本 第四部/docs/终章_开发脚本.md §3）。
//   段 A 雨中的街口、段 B 空房子、段 C 碎片与电话、段 D 近身战用 S.fight（各是重来点）；段 E 救护车旁是目标段，用 QTE 写在剧情里（p4_final.js）。
//   吉良的 kit（e_fin_kira）、亿泰的 kit（fin_okuyasu）、空气弹、触爆、泡泡护盾都在这里；剧情节拍在 story/p4_final.js（G.P4FIN 共用）。
//   人物：正式版（kira、okuyasu……）进了 G.D.chars 就用正式版，没有就用终章的暂代版 fin_*（R.cast）。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const R = (G.P4FIN = G.P4FIN || {});

  // ================================================================ 取人：正式版优先
  const CAST = {
    kira: ['kira', 'fin_kira'], kq: ['killerqueen', 'fin_kq'], okuyasu: ['okuyasu', 'fin_okuyasu'], thehand: ['thehand', 'fin_thehand'],
    hayato: ['hayato', 'fin_hayato'], echoes3: ['echoes3', 'fin_echoes3'], rohan: ['rohan', 'fin_rohan'], reimi: ['reimi', 'fin_reimi'],
    arnold: ['arnold', 'fin_arnold'], keicho: ['keicho', 'fin_keicho'], shinobu: ['shinobu', 'fin_shinobu'], joseph: ['joseph4', 'fin_joseph'],
  };
  R.cast = (k) => {
    const cs = CAST[k] || [k], ch = (G.D && G.D.chars) || {};
    return cs.find((c) => ch[c]) || cs[cs.length - 1];
  };
  // 名牌 / 替身卡：正式版那一章画了就用它的，没有就用终章画的
  R.card = (kind, k) => {
    const ui = (G.D && G.D.ui && G.D.ui[kind]) || {}, cs = CAST[k] || [k];
    return cs.find((c) => ui[c]) || cs[cs.length - 1];
  };

  // 战斗里插一段演出（照序章 p4_pro_fights.js 的 cine）
  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-fight' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  R.cine = cine;
  const player = () => G.world.player;
  const clk = () => (G.clk ? G.clk : { ui: 0, world: 0 });
  // J 打出去的这一招正在判定中（一招只算一次：a !== mem）
  const swingNow = (p, slots) => {
    const a = p && p.atk;
    if (!a || a.slot === 'enemy' || (slots && slots.indexOf(a.slot) < 0)) return null;
    return p.atkT >= a.active[0] && p.atkT <= a.active[1] + f(2) ? a : null;
  };
  R.swingNow = swingNow;
  // 按住 L 的同时按了 J（照序章修墙的写法：看 lastPress 有没有变）
  function guardJ(d, p) {
    const lp = G.input.lastPress('attack');
    if (lp === d.lastAtkPress) return false;
    d.lastAtkPress = lp;
    return !!p && (p.state === 'guard' || G.input.isDown('guard'));
  }
  // E：自由按的确认键（战斗里 E 只做剧情里的事）
  function eHit() { if (G.input.hit('ok')) { G.input.consume('ok'); return true; } return false; }

  // ================================================================ 亿泰 · 轰炸空间（终章暂代 kit：数值照仗助，伤害略高、走速慢一点）
  const HAND = '#8ab0ff', HAND2 = '#4a70d0';
  M.TH_J1 = Object.assign({}, M.SP_J1, { accent: HAND });
  M.TH_J2 = Object.assign({}, M.SP_J2, { accent: HAND });
  M.TH_J3 = Object.assign({}, M.SP_J3, { accent: HAND2, dmg: 22, guard: 'pierce', word: '削！' });
  M.TH_FIN = Object.assign({}, M.SP_FIN, { accent: HAND2, word: '削！！' });
  M.TH_U_FIN = Object.assign({}, M.SP_U_FIN, { accent: HAND2, word: '削掉！！' });
  K.fin_okuyasu = {
    hp: 140, speed: 62, standId: 'fin_thehand',
    combo: ['TH_J1', 'TH_J2', 'TH_J3'],
    rush: { tick: f(4), dmg: 4, push: 1, reach: [6, 52], depth: 10, loop: 'ora_loop', word: 'ORA', fx: 'fists', fist: 'fin_thehand',
      accent: '#c8e0f2', hitSfx: 'punch', finisher: 'TH_FIN' },
    guard: { pose: 'block' }, guardAttack: null, chords: {}, parry: { effect: 'reflect' }, dodge: {},
    special: { name: '削掉吧', title: 'fin_okuyasu', bg: 'radial', colours: ['#1a2a5a', '#0a1230', '#2c4a9a'], run: spOkuyasu, pose: 'cmd' },
    explore: { pose: 'punch' }, grunt: 'grunt_jotaro',
  };
  // 削掉吧：连削三次，每次把对手拉到面前再一抹
  async function spOkuyasu(p, C) {
    for (let i = 0; i < 3; i++) {
      const t = C.target(200);
      if (t) { t.x = p.x + p.facing * 30; t.y = p.y; }
      G.audio.sfx('void_eat', { vol: 0.8 });
      C.stand('punch', { dx: 22, seq: [[2, 99]] });
      const hit = C.hitArea(C.front(0, 60, 14), 'TH_U_FIN');
      if (hit.length) C.shake(4, f(12));
      await C.wait(0.3);
    }
  }
  R.okuyasuKit = () => K.fin_okuyasu;

  // ================================================================ 吉良吉影 · 杀手皇后（敌方）
  //   冲拳：杀手皇后往前一扑（预警 0.45 s）。触爆：杀手皇后摸一下地面，那里亮一圈粉光，2 s 后炸（ctx.data.addBomb 由各段的 tick 管）
  M.KQ_PUNCH = {
    slot: 'enemy', body: 'point', stand: 'punch', standSeq: [[1, f(3)], [2, 99]], standDx: 18,
    warn: { tier: 'W1', dur: 0.45 }, dur: 0.45 + f(26), active: [0.45, 0.45 + f(10)],
    melee: false, dash: { dist: 56, time: f(9), w: 8 }, dmg: 14, push: 14, guard: 'normal',
    sfx: 'whoosh', sfxHit: 'punch_heavy', fxHit: 'light', accent: '#f4b8cc', shake: [1, f(6)],
  };
  M.KQ_TOUCH = {
    slot: 'enemy', body: 'point', stand: 'punch', standSeq: [[2, 99]], standDx: 14,
    warn: { tier: 'W1', dur: 0.35 }, dur: 0.35 + f(30), active: [0.35, 0.35 + f(4)], melee: false, dmg: 0, guard: 'normal',
    sfx: 'whoosh', accent: '#f4b8cc',
    onStart(e, ctx) {
      if (ctx && ctx.data.addBomb) ctx.data.addBomb(e.x + e.facing * 30, e.y);
    },
  };
  K.e_fin_kira = {
    hp: 1500, speed: 44, moves: ['KQ_PUNCH', 'KQ_TOUCH'], koStyle: 'none', idle: 'idle',
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player, st = G.world.stage;
      if (!p || !st || m.hold || d.kiraHold) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      e.facing = p.x > e.x ? 1 : -1;
      const dx = Math.abs(p.x - e.x), keep = d.kiraKeep || 46;
      if (dx > keep + 10 || Math.abs(p.y - e.y) > 6) G.AI.approach(e, p, keep, dt);
      else if (dx < 24) G.combat.walkTo(e, G.clamp(p.x + (e.x < p.x ? -keep : keep), st.x0 + 10, st.x1 - 10), e.y, dt, e.speed);
      else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
      m.gap = (m.gap == null ? 1.4 : m.gap) - dt;
      if (m.gap > 0 || G.combat.tokens() >= 2) return true;
      if (d.addBomb && (d.bombs || []).length < (d.maxBombs || 1) && Math.random() < 0.35) { G.AI.tele(e, 'KQ_TOUCH'); m.gap = 2.4; }
      else if (dx <= 72 && Math.abs(p.y - e.y) <= 10) { G.AI.tele(e, 'KQ_PUNCH'); m.gap = d.kiraGap || 1.9; }
      return true;
    },
  };

  // ================================================================ 画在 UI 层的东西（世界坐标 → UI 坐标）
  const w2u = (x, y, z) => (G.cam && G.cam.w2u ? G.cam.w2u(x, y, z || 0) : { x: x * 2, y: y * 2 });
  function ring(g, cx, cy, r, col, alpha, dots) {
    g.save();
    g.globalAlpha = alpha;
    g.fillStyle = col;
    const n = dots || Math.max(10, Math.round(r * 1.6));
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      g.fillRect(Math.round(cx + Math.cos(a) * r) - 1, Math.round(cy + Math.sin(a) * r * 0.9) - 1, 2, 2);
    }
    g.restore();
  }

  // ================================================================ 触爆：地上一圈粉光，2 s 后炸（段 A）
  function bombs(S, ctx, owner) {
    const d = ctx.data, list = (d.bombs = []);
    d.addBomb = (x, y) => {
      const st = G.world.stage;
      list.push({ x: G.clamp(x, st.x0 + 10, st.x1 - 10), y, t: 0, dead: false });
      S.sfx('glint', 0.6);
      if (!d.bombTold) { d.bombTold = true; S.hint('杀手皇后碰过的地方亮了粉光：2 秒后会炸，离远点！', 5); }
    };
    const h = P4().overlay((g) => {
      if (G.world.fight !== ctx) return;
      for (const b of list) {
        if (b.dead) continue;
        const u = w2u(b.x, b.y), k = b.t / 2;
        ring(g, u.x, u.y, 18 + 6 * Math.sin(b.t * 14), '#ff70c0', 0.5 + 0.5 * k, 24);
        ring(g, u.x, u.y, 80 * (1 - k) + 8, '#ffb0d8', 0.35, 30);
      }
    });
    const tick = (dt) => {
      for (const b of list) {
        if (b.dead) continue;
        b.t += dt;
        if (b.t < 2) continue;
        b.dead = true;
        S.sfx('explosion', 0.9); S.shake(3, 0.3);
        S.fx('explosion', { x: b.x, y: b.y - 8, size: 1.1 }, { life: 0.6 });
        const p = player();
        if (p && Math.hypot(p.x - b.x, (p.y - b.y) * 2) <= 40) G.combat.hit(owner && !owner.remove ? owner : null, p, { slot: 'enemy', dmg: 18, push: 26, guard: 'normal', sfxHit: 'thud', fxHit: 'heavy' });
      }
      d.bombs = list.filter((b) => !b.dead);
      list.length = 0; list.push(...d.bombs);
      d.bombs = list;
    };
    return { h, tick, list };
  }

  // ================================================================ 空气弹（猫草的泡泡，被杀手皇后变成炸弹）
  //   style：'rain' 雨里只看得到一圈绕开的雨线；'ash' 平时看不见，撒了烟灰的 4 s 里显形；'sun' 雨停以后看得见反光
  function bubbles(S, ctx, o) {
    const d = ctx.data, list = [];
    const man = { list, style: o.style, revealUntil: -1, parried: 0, blown: 0, owner: o.owner || null };
    man.spawn = (x, y, z) => {
      const b = { x, y, z: z == null ? 18 : z, t: 0, dead: false, trail: [], speed: o.speed || 32, homing: o.homing || 0, vx: 0, vy: 0 };
      list.push(b);
      return b;
    };
    man.visible = () => man.style === 'sun' || clk().world < man.revealUntil;
    man.pop = (b, how) => {
      if (b.dead) return;
      b.dead = true;
      if (how === 'cut') {
        S.sfx('void_eat', 0.8);
        S.fx('glint', { x: b.x, y: b.y - b.z, size: 10 }, { life: 0.3 });
        S.sfxText('削！', { wx: b.x, wy: b.y, wz: b.z + 6 }, { dur: 0.6 });
        return;
      }
      man.blown++;
      S.sfx('explosion', 0.8); S.shake(2.5, 0.25);
      S.flash(0.12, 0.5, '#ffffff');
      S.fx('explosion', { x: b.x, y: b.y - b.z, size: 0.9 }, { life: 0.5 });
    };
    man.h = P4().overlay((g, t) => {
      if (G.world.fight !== ctx) return;
      const vis = man.visible();
      for (const b of list) {
        if (b.dead) continue;
        const u = w2u(b.x, b.y, b.z), r = 13;
        if (vis) {
          g.save();
          g.globalAlpha = man.style === 'ash' ? 0.75 : 0.55;
          g.fillStyle = man.style === 'ash' ? '#8a8490' : '#bfe8ff';
          ring(g, u.x, u.y, r, man.style === 'ash' ? '#5a5460' : '#e8f8ff', 0.9, 26);
          g.fillStyle = '#ffffff';
          g.fillRect(Math.round(u.x - 5), Math.round(u.y - 7), 3, 2);
          g.restore();
        } else if (man.style === 'rain') {
          // 雨滴在泡泡表面绕开：只有一圈淡淡的水线
          ring(g, u.x, u.y, r + Math.sin(t * 9 + b.t) * 1.2, '#a8c8e8', 0.42, 14);
        }
        if (man.style === 'ash' && vis) for (const q of b.trail) { const v = w2u(q[0], q[1], q[2]); g.fillStyle = '#6a6470'; g.fillRect(Math.round(v.x), Math.round(v.y), 2, 2); }
      }
    }, { z: 1 });
    man.tick = (dt) => {
      const p = player();
      for (const b of list) {
        if (b.dead || !p) continue;
        b.t += dt;
        const tx = p.x, ty = p.y, tz = 16;
        const dx = tx - b.x, dy = ty - b.y, dz = tz - b.z, dd = Math.hypot(dx, dy * 1.4, dz) || 1;
        if (b.homing) {
          // 会拐弯地追：速度方向慢慢转向仗助
          const want = Math.atan2(dy, dx), cur = b.vx || b.vy ? Math.atan2(b.vy, b.vx) : want;
          let da = Math.atan2(Math.sin(want - cur), Math.cos(want - cur));
          da = G.clamp(da, -b.homing * dt, b.homing * dt);
          b.vx = Math.cos(cur + da) * b.speed; b.vy = Math.sin(cur + da) * b.speed * 0.6;
          b.x += b.vx * dt; b.y += b.vy * dt; b.z += G.clamp(dz, -20 * dt, 20 * dt);
        } else {
          b.x += (dx / dd) * b.speed * dt; b.y += (dy / dd) * b.speed * dt * 0.6; b.z += (dz / dd) * b.speed * dt;
        }
        if (man.style === 'ash' && man.visible() && (b.trail.length === 0 || b.t - (b.lastTrail || 0) > 0.12)) { b.lastTrail = b.t; b.trail.push([b.x, b.y, b.z]); if (b.trail.length > 24) b.trail.shift(); }
        // 被 J 打中：仗助打中会炸（离得近会挨一点），亿泰的削能直接削掉
        const sw = swingNow(p);
        if (sw && sw !== b.swung) {
          const fx = (b.x - p.x) * p.facing;
          if (fx >= 2 && fx <= 46 && Math.abs(b.y - p.y) <= 12) {
            b.swung = sw;
            if (p.kit === K.fin_okuyasu || p.cid === R.cast('okuyasu')) { man.pop(b, 'cut'); if (o.onCut) o.onCut(b); continue; }
            man.pop(b, 'boom');
            if (fx < 30) G.combat.hit(null, p, { slot: 'enemy', dmg: 10, push: 18, guard: 'normal', sfxHit: 'thud', fxHit: 'light' });
            if (o.onPop) o.onPop(b);
            continue;
          }
        }
        // 碰到人：炸。按着 L 是普通格挡（伤害照引擎的格挡倍率），碰到前一瞬间按 L 是精准格挡（弹开，不扣血）
        if (Math.abs(b.x - p.x) <= 9 && Math.abs(b.y - p.y) <= 8 && Math.abs(b.z - 16) <= 14) {
          const rr = G.combat.hit(null, p, { slot: 'enemy', dmg: o.dmg || 25, push: 24, guard: 'normal', sfxHit: 'thud', fxHit: 'heavy' });
          if (rr && (rr.invuln || rr.evade)) continue;
          man.pop(b, 'boom');
          if (rr && rr.parry) man.parried++;
          if (o.onTouch) o.onTouch(b, rr || {});
        }
      }
      for (let i = list.length - 1; i >= 0; i--) if (list[i].dead) list.splice(i, 1);
    };
    man.close = () => { man.h.close(); list.length = 0; };
    return man;
  }
  R.bubbles = bubbles;

  // =====================================================================================================================
  // 段 A 雨中的街口（b19_kq_a）：仗助 + 亿泰 AI。猫草出场后撑 40 s
  // =====================================================================================================================
  let segH = [];
  const closeSeg = () => { for (const h of segH) { try { h.close(); } catch (e) { /* 已关 */ } } segH = []; };
  function aSetup(S, ctx, kira) {
    closeSeg();
    const d = ctx.data;
    d.bm = bombs(S, ctx, kira);
    segH.push(d.bm.h);
    d.pullT = 0; d.cat = false; d.catEnd = null; d.done = false;
    const oku = S.actor(R.cast('okuyasu'));
    if (oku) { oku.kit = K.fin_okuyasu; oku.dmgOut = 0.8; oku.energy = 0; }
    kira.minHp = 1;
    // 猫草已经出过场：重来时直接从猫草那段开始（前面 300 血不用再打一遍）
    if (R.catSeen) { kira.hp = 1200; return; }
    S.hint('J 三连 / 连打，K 闪避，L 格挡。亿泰会把吉良拽到你面前！', 6);
  }
  async function catPhase(S, ctx, kira) {
    const d = ctx.data;
    d.cat = true;
    kira.atk = null; kira.tele = null; kira.state = 'idle'; kira.play('idle');
    const again = !!R.catSeen;
    if (!again) await S.say(R.cast('kira'), '……是时候请你出场了，猫草。', { expr: 'normal' });
    const cat = T().prop(S, 'fin_straycat', kira.x + kira.facing * 10, kira.y + 1, { id: 'straycat_a', frame: 1, z: 22 });
    S.sfx('pop', 0.7);
    if (!again) S.standCard(R.card('standcards', 'fin_straycat'), { y: 100 });
    await S.wait(again ? 0.2 : 0.6);
    if (cat) {
      await S.animate(0.35, (k) => { cat.scale = 1 - 0.6 * k; cat.alpha = 1 - k; cat.z = 22 + 6 * k; });
      cat.remove = true;
    }
    if (!again) await S.say(R.cast('kira'), '空气做成的炸弹。在雨里，你看得见吗？', { expr: 'smile' });
    S.mark('b19a_cat');
    R.catSeen = true;
    d.bub = bubbles(S, ctx, { style: 'rain', speed: 28, dmg: 18 });
    segH.push(d.bub);
    d.bubT = 1.5;
    d.catEnd = ctx.t + 40;
    G.hud.timer = { label: '撑住：', until: d.catEnd, t: ctx.t, left: 40 };
    kira.minHp = 1000;
    d.kiraGap = 2.6;
    S.hint('雨滴在半空绕开了……那一圈里有看不见的泡泡！别碰到它', 7);
  }
  function aTick(S, ctx, dt) {
    const d = ctx.data, p = player(), kira = S.actor('kira'), oku = S.actor(R.cast('okuyasu'));
    if (!p || !kira) return;
    d.bm.tick(dt);
    // 亿泰（AI）每 9 s 拉近一次：吉良被拽到仗助面前
    d.pullT += dt;
    if (oku && !oku.remove && d.pullT >= 9 && Math.abs(kira.x - oku.x) < 160 && !kira.atk && !kira.tele) {
      d.pullT = 0;
      S.standAct(oku, 'punch', { dx: 18, z: 4, dur: 0.5 });
      S.sfx('void_eat', 0.8);
      S.emote(oku, '过来！', 0.9, '#bfd8ff');
      const st = G.world.stage;
      kira.x = G.clamp(p.x + p.facing * 22, st.x0 + 10, st.x1 - 10); kira.y = p.y; kira.stunT = 0.5; kira.state = 'hurt'; kira.play('hurt');
      S.fx('glint', { x: kira.x, y: kira.y - 20, size: 10 }, { life: 0.3 });
      if (!d.pullTold) { d.pullTold = true; S.hint('亿泰把吉良拽过来了！J 连段！', 4); }
    }
    if (!d.cat && kira.hp <= 1200) { cine(ctx, () => catPhase(S, ctx, kira)); return; }
    if (d.cat) {
      d.bub.tick(dt);
      d.bubT -= dt;
      if (d.bubT <= 0 && d.bub.list.length < 2) {
        d.bubT = 3.5;
        d.bub.spawn(kira.x + kira.facing * 16, kira.y, 22);
        S.sfx('bubbles', 0.35);
      }
      if (G.hud.timer) G.hud.timer.until = d.catEnd;
      if (ctx.t >= d.catEnd) d.done = true;
    }
  }
  R.fightA = async function (S, kira) {
    S.hint(null);
    const oku = R.cast('okuyasu');
    const res = await S.fight({
      id: 'b19_kq_a', arena: [20, 620], lead: 'josuke', swap: false, lockMsg: '仗助迎上去！亿泰在旁边帮手', allies: [oku],
      music: 'battle', after: null, dmgScale: 1.2, losable: true, energy: { start: 0 }, steps: null,
      waves: [[{ kit: 'e_fin_kira', actor: 'kira', cid: kira.cid, id: 'kira', name: '吉良吉影', x: kira.x, y: kira.y, boss: true, hp: 1500, minHp: 1 }]],
      testHint: (ctx) => { const k = G.S.actor('kira'), d = ctx.data; return { kiraHp: k ? k.hp : null, cat: !!d.cat, left: d.catEnd ? Math.round(d.catEnd - ctx.t) : null, bubbles: d.bub ? d.bub.list.length : 0 }; },
      onWave: async (S2, wi, spawned, attempt, ctx) => { aSetup(S2, ctx, spawned[0]); },
      tick: (c, dt) => aTick(S, c, dt),
      endWhen: (c) => !!c.data.done,
    });
    closeSeg();
    R.kiraHp = Math.max(1000, (S.actor('kira') || {}).hp || 1000);
    return res;
  };

  // =====================================================================================================================
  // 段 B 空房子（b19_kq_b）：一颗看不见的空气弹从窗口钻进来追仗助；E 撒烟灰显形；挡过 3 颗
  // =====================================================================================================================
  const EH = { arena: [12, 468], fire: 103, win: [271, 150], vase: 339, phone: 420 };
  function bSetup(S, ctx) {
    closeSeg();
    const d = ctx.data;
    d.ash = 3; d.ashRegen = 0; d.blocked = 0; d.lastAtkPress = G.input.lastPress('attack');
    S.state('ash', 0);
    d.bub = bubbles(S, ctx, {
      style: 'ash', speed: 40, homing: 1.6, dmg: 25,
      onTouch: (b, rr) => {
        if (rr.parry || rr.guard) {
          d.blocked++;
          ctx.step(Math.min(3, d.blocked));
          S.sfx('ding', 0.6);
          S.hint(rr.parry ? '精准格挡！泡泡被弹开了（' + d.blocked + ' / 3）' : '挡住了！（' + d.blocked + ' / 3）', 3);
        }
      },
      onPop: () => {},
    });
    segH.push(d.bub);
    d.nextT = 2.5;
    S.hint('E：在壁炉前撒烟灰，看清泡泡。泡泡贴上来时按住 L 挡住（一瞬间按 L 更好）', 8);
  }
  function bTick(S, ctx, dt) {
    const d = ctx.data, p = player();
    if (!p) return;
    d.bub.tick(dt);
    if (!d.bub.list.length) {
      d.nextT -= dt;
      if (d.nextT <= 0 && d.blocked < 3) {
        d.nextT = 2.2;
        d.bub.spawn(EH.win[0], EH.win[1], 46);
        S.sfx('glass_break', 0.25);
        S.sfxText('……', { wx: EH.win[0], wy: EH.win[1], wz: 60 }, { dur: 0.6 });
      }
    }
    // 壁炉前按 E 撒烟灰
    const near = Math.abs(p.x - EH.fire) <= 26 && Math.abs(p.y - 150) <= 12;
    if (near && !d.fireHint) { d.fireHint = true; S.hint(d.ash > 0 ? '壁炉里有烟灰：按 E 撒出去' : '烟灰撒光了……等一会儿会再落下来一些', 3); }
    if (!near) d.fireHint = false;
    if (near && eHit()) {
      if (d.ash > 0) {
        d.ash--;
        S.state('ash', 3 - d.ash);
        d.bub.revealUntil = clk().world + 4;
        S.sfx('sand', 0.7);
        S.fx('smoke', { x: EH.fire, y: 128, n: 14, rise: 40, life: 1.2, spread: 60, colour: '#8a8490' }, { life: 1.6 });
        S.mark('b19b_ash');
        S.hint('看见了！泡泡沾上了灰（4 秒）', 3);
      } else S.emote(p, '没灰了……', 1);
    }
    if (d.ash < 3) { d.ashRegen += dt; if (d.ashRegen >= 10) { d.ashRegen = 0; d.ash++; S.state('ash', 3 - d.ash); } }
  }
  R.fightB = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b19_kq_b', arena: EH.arena, lead: 'josuke', swap: false, lockMsg: '只有仗助能挡', music: 'battle', after: null,
      dmgScale: 1.2, losable: true, energy: { start: 0 }, steps: { n: 3, label: '挡下空气弹' }, waves: [],
      kitOverride: { josuke: { parryWin: f(12) } },
      testHint: (ctx) => { const d = ctx.data, b = d.bub && d.bub.list[0], p = player(); return { blocked: d.blocked, ash: d.ash, dist: b && p ? Math.round(Math.hypot(b.x - p.x, b.y - p.y)) : null }; },
      onWave: async () => {},
      onRetry: async (S2, attempt, ctx) => { void ctx; },
      tick: (c, dt) => { if (!c.data.bub) bSetup(S, c); bTick(S, c, dt); },
      endWhen: (c) => (c.data.blocked || 0) >= 3,
    });
    closeSeg();
    S.state('ash', 3);
    S.mark('b19b_done');
    return res;
  };

  // =====================================================================================================================
  // 段 C 碎片与电话（b19_kq_c）：步骤式，没有失败
  // =====================================================================================================================
  async function cThrow(S, ctx) {
    const p = player(), d = ctx.data;
    S.face(p, -1);
    const sh = T().prop(S, 'fin_shard', p.x, p.y, { id: 'shard', frame: 0, z: 16 });
    S.sfx('whoosh', 0.8);
    await S.say('josuke', '……从窗外看着我们是吧。接着！', { expr: 'rage' });
    if (sh) await S.arc(sh, 236, 148, 60, 0.4, { z1: 70, spin: 8 });
    S.state('glass', 1);
    S.sfx('glass_break', 0.9);
    S.sfx('punch_heavy', 0.7);
    S.sfxText('啪！', { wx: 236, wy: 150, wz: 76 }, { dur: 0.8 });
    if (sh) sh.remove = true;
    await S.say(R.cast('kira'), '（窗外）……扔一片玻璃？无聊。', { expr: 'smile' });
    d.st = 2;
    d.lastAtkPress = G.input.lastPress('attack');
    S.hint('那片玻璃上沾着你的血。按住 L 按 J：把碎片修回来！', 8);
  }
  async function cFix(S, ctx) {
    const p = player(), d = ctx.data;
    S.standAct(p, 'reach', { dx: 18, z: 6, dur: 0.8 });
    P4().fixGlow(S, 236, 70, { n: 9 });
    S.sfx('sparkle', 0.9);
    await S.wait(0.4);
    S.sfx('whoosh', 0.8);
    S.sfxText('嗖——', { wx: 250, wy: 150, wz: 70 }, { dur: 0.7 });
    await S.wait(0.35);
    S.sfx('punch_heavy', 0.9); S.shake(3, 0.3);
    S.fx('sparkles', { x: 240, y: 64, n: 10, radius: 14, colour: '#ffb0d8', period: 0.5, size: 3 }, { life: 0.9 });
    R.kiraHp = Math.max(1, (R.kiraHp || 1000) - 150);
    S.mark('b19c_shard_hit');
    await S.say(R.cast('kira'), '（窗外）——！？从、从背后……', { expr: 'shock' });
    await S.say('josuke', '修好的东西会回到原来的地方。……比如，我的血。', { expr: 'normal' });
    ctx.step(1);
    d.st = 3;
    S.hint('对早人按 E', 6);
  }
  async function cLighter(S, ctx) {
    const p = player(), d = ctx.data, hy = S.actor(R.cast('hayato'));
    const hc = R.cast('hayato');
    if (hy) S.face(p, hy);
    await S.say('josuke', '早人，你身上带着打火机吧？借我用一下。');
    await S.say(hc, '……诶？这、这个是……', { expr: 'shock' });
    const lt = hy ? T().prop(S, 'fin_lighter', hy.x + 6, hy.y + 1, { id: 'lighter', frame: 1, z: 18 }) : null;
    S.sfx('lighter', 0.9);
    await S.wait(0.4);
    S.mark('b19c_lighter');
    if (hy) S.fx('smoke', { x: hy.x, y: hy.y - 8, n: 8, rise: 26, life: 1.0, colour: '#9a949c' }, { life: 1.4 });
    await S.say('josuke', '对不住，烧一下你的外套。……里面藏着什么东西。');
    if (lt) lt.remove = true;
    const ph = hy ? T().prop(S, 'fin_photo', hy.x, hy.y + 1, { id: 'photo', frame: 1, z: 20 }) : null;
    S.sfx('whoosh', 0.7);
    await S.say('yoshihiro', '吉影！吉影！他们在——', { name: '照片里的老人' });
    if (ph) await S.arc(ph, EH.phone - 4, 150, 30, 0.8, { z1: 44 });
    await S.say(hc, '是那个照片里的人……他一直藏在我衣服里？', { expr: 'shock' });
    ctx.step(2);
    d.st = 4; d.ringT = 0; d.rings = 0; d.lastAtkPress = G.input.lastPress('attack');
    S.state('ring', 1);
    S.mark('b19c_phone');
  }
  async function cPhone(S, ctx) {
    const d = ctx.data, p = player();
    S.state('ring', 0);
    S.sfx('pop', 0.8);
    await S.walk(p, EH.phone - 14, 150, { speed: 90 });
    S.face(p, 1);
    const i = await S.choice(['他在二楼窗边', '……'], '对着话筒说什么？');
    if (i === 0) await S.say('josuke', '（压着嗓子）爸爸……他在二楼窗边。');
    else { await S.say('josuke', '……你打错了。'); await S.say('yoshihiro', '吉影！他就在电话旁边！', { name: '照片里的老人' }); }
    await S.say('yoshihiro', '……好、好的，吉影，就在——', { name: '照片里的老人' });
    S.sfx('glass_break', 0.6);
    await S.wait(0.4);
    const ph = S.actor('photo');
    S.flash(0.25, 0.9, '#ffffff');
    S.sfx('explosion', 1); S.shake(4, 0.4);
    S.fx('explosion', { x: EH.phone, y: 110, size: 1.0 }, { life: 0.6 });
    if (ph) ph.remove = true;
    S.mark('b19c_photo_boom');
    await S.say(R.cast('kira'), '（窗外）……老爸？！', { expr: 'shock' });
    S.sfx('whoosh', 0.8);
    S.fx('sparkles', { x: 240, y: 64, n: 10, radius: 14, colour: '#ffb0d8', period: 0.5, size: 3 }, { life: 0.9 });
    S.sfx('punch_heavy', 0.9); S.shake(3, 0.3);
    R.kiraHp = Math.max(1, (R.kiraHp || 1000) - 150);
    await S.say('josuke', '第二片。……你的空气弹，炸到自己人了。', { expr: 'rage' });
    ctx.step(3);
    d.done = true;
  }
  function cTick(S, ctx, dt) {
    const d = ctx.data, p = player();
    if (!p || d.busy) return;
    const run = (fn) => { d.busy = true; cine(ctx, async () => { await fn(S, ctx); d.busy = false; }); };
    if (d.st === 0) {
      if (Math.abs(p.x - EH.vase) <= 46 && !d.vaseHint) { d.vaseHint = true; S.hint('J3（第三下）打碎花瓶', 4); }
      const sw = swingNow(p, ['J3', 'fin']);
      if (sw && Math.abs(p.x - EH.vase) <= 34 && Math.abs(p.y - 150) <= 12) {
        d.st = 1;
        S.state('vase', 1);
        S.sfx('glass_break', 1); S.shake(2, 0.2);
        S.fx('burst', { x: EH.vase, y: 136, n: 12, speed: 34, colours: ['#e8f4ff', '#a8d8f0'], gravity: 140, life: 0.7 });
        S.mark('b19c_vase');
        S.hint('E：捡一片碎玻璃', 5);
      }
    } else if (d.st === 1) {
      if (Math.abs(p.x - EH.vase) <= 30 && eHit()) run(cThrow);
    } else if (d.st === 2) {
      if (guardJ(d, p)) run(cFix);
    } else if (d.st === 3) {
      const hy = S.actor(R.cast('hayato'));
      if (hy && Math.abs(p.x - hy.x) <= 30 && Math.abs(p.y - hy.y) <= 14 && eHit()) run(cLighter);
    } else if (d.st === 4) {
      d.ringT += dt;
      if (Math.floor(d.ringT * 3) !== Math.floor((d.ringT - dt) * 3)) S.sfx('blip', 0.5);
      if (!d.ringHint) { d.ringHint = true; S.hint('电话响了！3 秒内按 J 抢话筒！', 3); }
      if (G.input.lastPress('attack') !== d.lastAtkPress) { d.lastAtkPress = G.input.lastPress('attack'); run(cPhone); return; }
      if (d.ringT > 3) {
        d.rings++; d.ringT = 0; d.ringHint = false;
        S.hint('没抢到……照片在喊！电话又响了，按 J！', 3);
      }
    }
  }
  R.fightC = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b19_kq_c', arena: EH.arena, lead: 'josuke', swap: false, lockMsg: '只有仗助能动', music: 'battle', after: null,
      dmgScale: 1.2, losable: false, energy: { start: 0 }, steps: { n: 3, label: '碎片 · 打火机 · 电话' }, waves: [],
      testHint: (ctx) => ({ st: ctx.data.st, kiraHp: R.kiraHp }),
      onWave: async () => {},
      tick: (c, dt) => { if (c.data.st == null) { c.data.st = 0; S.hint('J3（第三下）打碎花瓶', 6); } cTick(S, c, dt); },
      endWhen: (c) => !!c.data.done,
    });
    S.state('ring', 0);
    return res;
  };

  // =====================================================================================================================
  // 段 D 近身战（b19_kq_d）：吉良 1800，猫草的泡泡护盾；亿泰中途归来，能 Q 换他削空气弹、把猫草拉开
  // =====================================================================================================================
  const SHIELD_ON = (d) => !(d.shieldOff > 0) && !(d.shieldBreak > 0);
  function dSetup(S, ctx, kira) {
    closeSeg();
    const d = ctx.data;
    d.shieldOff = 0; d.shieldBreak = 0; d.bubT = 2; d.pullCd = 0; d.lastAtkPress = G.input.lastPress('attack');
    d.back = !!R.okuBack;
    kira.minHp = 1;
    // 重来时亿泰已经回来了：他不在开战时的队伍快照里，引擎不会替他复位，这里自己来
    if (d.back) {
      const oku = G.party._actor(R.cast('okuyasu')), p = player(), st = G.world.stage;
      oku.kit = K.fin_okuyasu;
      if (G.party.members.indexOf(oku) < 0) G.party.add(R.cast('okuyasu'));
      if (G.world.player !== oku) {
        Object.assign(oku, { team: 'ally', visible: true, remove: false, dead: false, hp: oku.maxHp, state: 'idle', follow: null, hold: false });
        oku.x = G.clamp(p.x - 26, st.x0 + 10, st.x1 - 10); oku.y = p.y;
        if (G.combat.resetActor) { G.combat.resetActor(oku); oku.team = 'ally'; }
      }
      S.leadable(R.cast('okuyasu'), true);
    }
    // 护盾在：J1、J2、连打只有 0.15；猫草被拉开 / 护盾打破的空档里吉良露出破绽，挨打 ×1.6（1800 血实测太长，见开发脚本 §3 段 D）
    kira.dmgMul = (t, att, m) => (SHIELD_ON(d) ? (['J3', 'fin', 'special', 'shot'].indexOf(m.slot) < 0 ? 0.15 : 1) : 1.6);
    d.bub = bubbles(S, ctx, { style: 'sun', speed: 30, dmg: 20 });
    segH.push(d.bub);
    // 泡泡护盾：吉良身边一圈淡蓝光圈；护盾掉了的倒计时
    segH.push(P4().overlay((g, t) => {
      if (G.world.fight !== ctx) return;
      const k = S.actor('kira');
      if (!k || k.remove) return;
      const u = w2u(k.x, k.y, 18);
      if (SHIELD_ON(d)) ring(g, u.x, u.y, 30 + Math.sin(t * 4) * 1.5, '#bfe8ff', 0.6, 36);
      if (d.shieldOff > 0) P4().text(g, '泡泡护盾消失：' + Math.ceil(d.shieldOff) + ' 秒', 320, 70, '#bfe8ff', 12, 'center');
    }));
    ctx.on('hit', (e) => {
      if (e.t !== S.actor('kira')) return;
      if (SHIELD_ON(d)) {
        if (['J3', 'fin', 'special'].indexOf(e.slot) >= 0) { d.shieldBreak = 4; S.sfx('pop', 0.9); S.sfxText('啪！', e.t, { dur: 0.6 }); S.hint('护盾破了！4 秒内快打！', 3); }
        else if (G.clk.world - (d.slideT || -9) > 1.2) { d.slideT = G.clk.world; S.sfxText('滑开了……', e.t, { dur: 0.6 }); if (!d.slideTold) { d.slideTold = true; S.hint('拳头在泡泡上滑开了：J3（第三下）才打得破', 5); } }
      }
    });
    S.hint('猫草的泡泡护着他：J3 打破护盾再打！', 6);
  }
  async function okuyasuBack(S, ctx, b) {
    const d = ctx.data, p = player(), oc = R.cast('okuyasu');
    d.back = true; R.okuBack = true;
    G.hitStopAll(0.5);
    S.sfx('freeze', 0.6);
    await S.wait(0.5, 'ui');
    S.sfx('void_eat', 1);
    d.bub.pop(b, 'cut');
    S.fx('glint', { x: p.x + p.facing * 12, y: p.y - 24, size: 14 }, { life: 0.4 });
    const oku = G.party._actor(oc);
    oku.kit = K.fin_okuyasu;
    const st = G.world.stage;
    await G.party.add(oc, { x: G.clamp(p.x - p.facing * 26, st.x0 + 10, st.x1 - 10), y: p.y });
    oku.visible = true; oku.team = 'ally'; oku.facing = p.facing; oku.hp = oku.maxHp; oku.dead = false; oku.state = 'idle'; oku.play('idle');
    S.mark('b19d_okuyasu_back');
    await S.say(oc, '……我回来了。', { expr: 'normal' });
    await S.say('josuke', '亿泰！？你……', { expr: 'shock' });
    S.hint(null);
    await R.dream(S);
    await S.say('josuke', '亿泰！你醒了！', { expr: 'smile' });
    await S.say(oc, '睡得真香。……那家伙就是吉良吉影？', { expr: 'rage' });
    S.nameCard(R.card('namecards', 'okuyasu'), { y: 100 });
    S.standCard(R.card('standcards', 'fin_thehand'), { y: 100 });
    S.leadable(oc, true);
    G.party.locked = false;
    S.hint('按 Q 换成亿泰：他的削能削掉空气弹；按住 L 按 J 把猫草从杀手皇后身边拉开', 8);
  }
  async function pullCat(S, ctx) {
    const d = ctx.data, p = player(), kira = S.actor('kira');
    S.standAct(p, 'punch', { dx: 22, z: 4, dur: 0.6 });
    S.sfx('void_eat', 1);
    S.fx('glint', { x: kira.x, y: kira.y - 26, size: 12 }, { life: 0.4 });
    const cat = T().prop(S, 'fin_straycat', kira.x, kira.y + 1, { id: 'straycat_d', frame: 0, z: 26 });
    if (cat) { await S.arc(cat, p.x + p.facing * 18, p.y, 20, 0.4, { z1: 0 }); }
    S.mark('b19d_pull');
    d.shieldOff = 15;
    await S.say(R.cast('okuyasu'), '这盆草，我削过来了！', { expr: 'rage' });
    await S.say(R.cast('kira'), '……猫草！', { expr: 'shock' });
    if (cat) { await S.wait(0.4); cat.remove = true; }
    S.hint('护盾没了 15 秒！上！', 4);
  }
  function dTick(S, ctx, dt) {
    const d = ctx.data, p = player(), kira = S.actor('kira');
    if (!p || !kira) return;
    d.bub.tick(dt);
    d.shieldOff = Math.max(0, d.shieldOff - dt);
    d.shieldBreak = Math.max(0, d.shieldBreak - dt);
    d.pullCd = Math.max(0, d.pullCd - dt);
    d.bubT -= dt;
    if (d.bubT <= 0 && d.bub.list.length < 2) { d.bubT = 4; d.bub.spawn(kira.x + kira.facing * 16, kira.y, 22); S.sfx('bubbles', 0.35); }
    // 第一颗空气弹贴到仗助面前：亿泰归来
    if (!d.back && !d.busy) {
      for (const b of d.bub.list) {
        if (!b.dead && Math.abs(b.x - p.x) <= 26 && Math.abs(b.y - p.y) <= 10) { d.busy = true; cine(ctx, async () => { await okuyasuBack(S, ctx, b); d.busy = false; }); return; }
      }
    }
    // 亿泰：按住 L 按 J，把猫草拉开
    const isOku = p.cid === R.cast('okuyasu');
    if (guardJ(d, p) && isOku && !d.busy) {
      if (d.pullCd > 0) S.emote(p, '再等等……', 0.8);
      else if (Math.abs(kira.x - p.x) <= 140 && Math.abs(kira.y - p.y) <= 20) { d.pullCd = 6; d.busy = true; cine(ctx, async () => { await pullCat(S, ctx); d.busy = false; }); }
      else S.emote(p, '太远了！', 0.8);
    }
    if (kira.hp <= 1) d.done = true;
  }
  R.fightD = async function (S, kira) {
    S.hint(null);
    const res = await S.fight({
      id: 'b19_kq_d', arena: [20, 940], lead: 'josuke', swap: true, lockMsg: '亿泰还没醒', music: 'battle', after: null,
      dmgScale: 1.3, losable: true, energy: { start: 40 },
      allies: [R.cast('okuyasu')],
      waves: [[{ kit: 'e_fin_kira', actor: 'kira', cid: kira.cid, id: 'kira', name: '吉良吉影', x: kira.x, y: kira.y, boss: true, hp: 1800, minHp: 1 }]],
      testHint: (ctx) => { const k = G.S.actor('kira'), d = ctx.data; return { kiraHp: k ? k.hp : null, back: !!d.back, shield: SHIELD_ON(d), off: Math.round(d.shieldOff || 0), lead: player() && player().cid }; },
      onWave: async (S2, wi, spawned, attempt, ctx) => { dSetup(S2, ctx, spawned[0]); },
      tick: (c, dt) => dTick(S, c, dt),
      endWhen: (c) => !!c.data.done,
    });
    closeSeg();
    const k = S.actor('kira');
    if (k) k.dmgMul = null;
    return res;
  };
  R.closeSeg = closeSeg;
})();
