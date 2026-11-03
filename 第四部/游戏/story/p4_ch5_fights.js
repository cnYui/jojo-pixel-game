// 第5章　露伴宅 / 漫画家与猎鼠：战斗（开发脚本 第四部/docs/第5章_开发脚本.md §3）。剧情节拍在 story/p4_ch5.js。
//   第 7 战「天堂之门」（b07_heavensdoor）：仗助闭着眼睛打。整场世界层罩黑，只把声音画成波纹（脚步、笔帽、翻页、说话），
//     露伴 HP 40% 时故意说发型的坏话 → 发型记录 4 → 强制暴走：画面“睁眼”，暴走槽和“变成书”槽比快。
//   第 8 战「Ratt」：段 1（b08a_ratt）牧场屋内，仗助的 J 换成弹钢珠，老鼠躲在家具后面，拿平底锅挡飞镖，最后对射；
//     段 2（b08b_hill）山坡，两发步枪子弹的狙击。
//   另外：露伴当队长用的招式组 G.KITS.rohan（设计文档 3.3：甩墨、翻页把人变成书、写命令、U 全场变书）也写在这里，
//     第6、8、9、11章露伴当队长时直接用（这个文件开局就载入）。
'use strict';
(function () {
  const G = window.G;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const R = (G.P4CH5 = {});
  const UW = 640, UH = 360;
  const clk = () => (G.clk ? G.clk : { ui: 0, world: 0 });
  const player = () => G.world.player;
  const text = (g, s, x, y, col, size, align, outline) => P4().text(g, s, x, y, col, size, align, outline);

  // 在战斗里插一段演出：把 W.cine 占住（玩家、敌人、战斗 tick 都停），演完还回去（同序章 p4_pro_fights.js 的 cine）
  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-fight' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  R.cine = cine;

  // =====================================================================================================================
  // “变成书”：被天堂之门翻开的人头顶一本打开的书，书页一张张翻（只是图标 + 纸片，不画脸被撕开）
  // =====================================================================================================================
  const books = new Set();
  function bookOn(a, dur) { if (!a) return; a.mem = a.mem || {}; a.mem.bookUntil = clk().world + dur; books.add(a); }
  R.bookOn = bookOn;
  function drawBookIcon(g, x, y, t, k) {
    // 一本摊开的书（两页 + 书脊），右页在翻
    g.fillStyle = '#3a2a1a'; g.fillRect(x - 13, y - 1, 26, 12);
    g.fillStyle = '#fff8e6'; g.fillRect(x - 12, y, 11, 10); g.fillRect(x + 1, y, 11, 10);
    g.fillStyle = '#c8b898';
    for (let i = 0; i < 3; i++) { g.fillRect(x - 10, y + 2 + i * 3, 8, 1); g.fillRect(x + 3, y + 2 + i * 3, 8, 1); }
    const u = (t * 3) % 1, w = Math.round(11 * Math.cos(u * Math.PI));
    g.fillStyle = '#ffffff';
    if (w >= 0) g.fillRect(x + 1, y - 1, Math.max(1, w), 10); else g.fillRect(x + 1 + w, y - 1, -w, 10);
    if (k != null) { g.fillStyle = 'rgba(255,240,180,0.9)'; g.fillRect(x - 13, y + 13, Math.round(26 * k), 2); }
  }
  function bookLayer() {
    return P4().overlay((g, t) => {
      if (!G.cam || !G.cam.w2u) return;
      const now = clk().world;
      for (const a of [...books]) {
        if (a.remove || !a.mem || !(a.mem.bookUntil > now)) { books.delete(a); continue; }
        const p = G.cam.w2u(a.x, a.headY ? a.headY() - 8 : a.y - 40, 0);
        drawBookIcon(g, Math.round(p.x), Math.round(p.y - 12), t, null);
      }
    }, { z: 2 });
  }
  let bookH = null;
  R.ensureBooks = () => { if (!bookH || bookH.dead || bookH.run !== G.runId) bookH = bookLayer(); };

  // =====================================================================================================================
  // 岸边露伴 · 天堂之门（队长用，设计文档 3.3 中距离控制型）
  // =====================================================================================================================
  const INK = '#2a1e3a';
  const drawInk = (P, x, y, s) => {
    const px = G.px, sp = Math.hypot(s.vx, s.vy) || 1;
    px.rect(P, x - 1, y - 1, 3, 3, INK, 1);
    px.line(P, x, y, x - (s.vx / sp) * 6, y - (s.vy / sp) * 6, '#5a4a7a', 0.7, 1);
  };
  // J1 / J2 钢笔甩墨：80 px 的小墨弹，伤害 6
  M.HD_J1 = {
    slot: 'J1', body: 'point', stand: 'write', standDx: 6, standZ: 10, dur: f(16), active: [f(6), f(8)], melee: false, from: 'stand',
    fireAt: [f(6)], link: f(8), cancel: f(8), shotAhead: 10, shotZ: 26,
    shot: { kind: 'ink', speed: 300, life: 0.5, range: 80, hitR: [4, 7, 20], dmg: 6, push: 3, energy: 2, stop: f(2), slot: 'shot', draw: drawInk },
    sfx: 'whoosh', sfxRate: 1.4, energy: 0, accent: '#b8e070',
  };
  M.HD_J2 = Object.assign({}, M.HD_J1, { slot: 'J2' });
  // J3 翻页：天堂之门的小人扑上去，命中就把对方变成书 1.2 s（Boss 0.6 s，之后 4 s 免疫）
  M.HD_J3 = {
    slot: 'J3', body: 'point', stand: 'punch', standSeq: [[0, f(6)], [1, f(14)], [2, 99]], standDx: 26, dur: f(28), active: [f(9), f(14)],
    from: 'body', reach: [6, 52], depth: 9, dmg: 10, push: 4, energy: 3, root: 1.2, rootBoss: 0.6, rootImmune: 4,
    link: f(14), cancel: f(14), sfx: 'card_flip', sfxHit: 'card_flip', fxHit: 'light', accent: '#ffe8a0', word: '啪啦',
    onHit: (a, t) => { if (t.rootT > 0) bookOn(t, t.rootT); R.ensureBooks(); },
  };
  // 连打终结：甩出一页原稿
  M.HD_FIN = Object.assign({}, M.SP_FIN, { body: 'point', stand: 'punch', accent: '#ffe8a0', word: '唰！', sfxHit: 'card_flip' });
  M.HD_U_FIN = Object.assign({}, M.SP_U_FIN, { body: 'point', stand: 'punch', accent: '#ffe8a0', word: '天堂之门！' });
  // 按住 L 按 J：对“变成书”的敌人写一行命令（方向键：上「不能攻击岸边露伴」6 s、前「往后飞」、下「睡觉」2 s；每场每条一次）
  async function hdWrite(S, p, ctx) {
    const now = clk().world;
    const t = (ctx ? ctx.enemies() : []).filter((e) => e.mem && e.mem.bookUntil > now && Math.abs(e.x - p.x) < 70 && Math.abs(e.y - p.y) < 14)[0];
    if (!t) { S.emote(p, '……先把它翻开。', 0.9); return; }
    const used = (ctx.data.hdWritten = ctx.data.hdWritten || {});
    const I = G.input;
    let k = I.isDown('up') ? 'up' : I.isDown('down') ? 'down' : 'fwd';
    if (used[k]) { S.emote(p, '这一条写过了。', 0.9); return; }
    used[k] = true;
    p.play('write');
    if (p.stand) p.stand.act('write', { dx: 12, dur: 0.5 });
    S.sfx('card_flip', 0.8);
    const line = { up: '不能攻击岸边露伴', fwd: '往后飞', down: '睡觉' }[k];
    S.sfxText('「' + line + '」', t, { dur: 1.2 });
    if (k === 'up') { t.mem.noAtkUntil = now + 6; t.atk = null; t.tele = null; }
    else if (k === 'down') { t.stunT = Math.max(t.stunT || 0, 2); t.atk = null; t.tele = null; bookOn(t, 2); }
    else G.combat.hit(p, t, { slot: 'special', dmg: 12, push: 90, guard: 'none', sfxHit: 'wall_slam', fxHit: 'heavy' });
  }
  async function spRohan(p, C) {
    // 切入后：露伴在空中画出天堂之门 → 全场敌人变成书 3 s，期间受到的伤害 ×1.5
    const ctx = C.ctx;
    C.stand('write', { dx: 10, dur: 1.0 });
    C.sfx('card_flip', { vol: 1 });
    C.fx('sparkles', { x: p.x + p.facing * 20, y: p.y - 40, n: 12, radius: 26, colour: '#ffe8a0', period: 0.5, size: 3 });
    await C.wait(0.5);
    for (const e of ctx ? ctx.enemies() : []) {
      if (e.hp <= 0) continue;
      e.rootT = Math.max(e.rootT || 0, 3); e.atk = null; e.tele = null; e.mem.hdMulUntil = clk().world + 3;
      bookOn(e, 3);
    }
    R.ensureBooks();
    C.flash('#fff4c8', 0.3);
    await C.wait(0.4);
  }
  K.rohan = {
    hp: 110, speed: 62, standId: 'heavensdoor',
    combo: ['HD_J1', 'HD_J2', 'HD_J3'],
    rush: {
      tick: f(5), dmg: 3, push: 1, reach: [6, 50], depth: 10, loop: null, word: '唰', fx: 'fists', fist: 'heavensdoor',
      accent: '#ffe8a0', hitSfx: 'card_flip', finisher: 'HD_FIN',
    },
    guard: { pose: 'block' }, guardAttack: null, chords: { 'guard+attack': { run: hdWrite } }, parry: { effect: 'reflect' }, dodge: {},
    special: { name: '天堂之门', title: 'rohan', bg: 'radial', colours: ['#1e4a2a', '#0c2010', '#3a7a44'], run: spRohan, pose: 'point' },
    explore: { pose: 'point' }, grunt: null,
  };

  // =====================================================================================================================
  // 第 7 战 天堂之门（b07_heavensdoor）：仗助一个人，闭着眼睛
  // =====================================================================================================================
  const S7 = { arena: [44, 472], josuke: [120, 160], rohan: [380, 156] };
  // 声音波纹：{ x, y（世界）, t0, col, r, dur, label }
  let ripples = [];
  function ripple(x, y, col, o = {}) {
    ripples.push({ x, y, t0: clk().world, col, r: o.r || 34, dur: o.dur || 0.9, label: o.label || null, rings: o.rings || 2 });
    if (ripples.length > 40) ripples.shift();
  }
  R.ripple = ripple;
  function darkLayer(ctx) {
    return P4().overlay((g) => {
      const W = G.world;
      if (W.fight !== ctx || !ctx.data.dark || !G.cam || !G.cam.w2u) return;
      const now = clk().world;
      ripples = ripples.filter((r) => now - r.t0 < r.dur);
      for (const r of ripples) {
        const u = (now - r.t0) / r.dur, p = G.cam.w2u(r.x, r.y - 14, 0);
        g.save();
        for (let k = 0; k < r.rings; k++) {
          const uu = u - k * 0.18;
          if (uu <= 0) continue;
          g.globalAlpha = Math.max(0, 1 - uu) * 0.9;
          g.strokeStyle = r.col; g.lineWidth = 2;
          g.beginPath(); g.ellipse(Math.round(p.x), Math.round(p.y), 4 + r.r * uu * 2, (4 + r.r * uu * 2) * 0.55, 0, 0, Math.PI * 2); g.stroke();
        }
        if (r.label && u < 0.7) { g.globalAlpha = 1 - u; text(g, r.label, Math.round(p.x), Math.round(p.y - 30 - u * 10), r.col, 12, 'center', '#000000'); }
        g.restore();
      }
      // 仗助自己：脚下一圈淡淡的粉光（闭着眼也知道自己站在哪）
      const pl = player();
      if (pl) {
        const p = G.cam.w2u(pl.x, pl.y, 0);
        g.save(); g.globalAlpha = 0.55; g.strokeStyle = '#ff9ccc'; g.lineWidth = 2;
        g.beginPath(); g.ellipse(Math.round(p.x), Math.round(p.y), 14, 6, 0, 0, Math.PI * 2); g.stroke();
        g.fillStyle = '#ff9ccc'; g.fillRect(Math.round(p.x + pl.facing * 14) - 2, Math.round(p.y) - 2, 4, 4);
        g.restore();
      }
      if (ctx.data.slowUntil > now) text(g, '半本书：走不快！', 320, 300, '#ffe8a0', 12, 'center', '#000000');
    }, { z: 1 });
  }
  // 露伴的招：笔尖突刺（笔帽“咔”一声 0.4 s → 冲过来刺，12）、天堂之门（翻页声从一个方向逼近 0.6 s → 小人扑上来，碰到就“半本书”3 s）
  M.RH_PEN = {
    slot: 'enemy', body: 'point', stand: null, warn: { tier: 'W1', dur: 0.4 }, dur: 0.4 + f(24), active: [0.4, 0.4 + f(10)],
    melee: false, dash: { dist: 64, time: f(9), w: 8 }, dmg: 12, push: 10, guard: 'normal',
    sfx: 'whoosh', sfxHit: 'stab', fxHit: 'light', accent: '#c8b0ff',
  };
  const drawDoor = (P, x, y, s) => {
    // 黑暗里看不见：画是为了睁眼那一下和测试截图
    const px = G.px; px.rect(P, x - 3, y - 5, 6, 8, '#fff4dc', 0.8); px.rect(P, x - 4, y - 7, 8, 2, '#f0c860', 0.8);
  };
  M.RH_DOOR = {
    slot: 'enemy', body: 'point', stand: 'punch', standDx: 16, warn: { tier: 'W2', dur: 0.6 }, dur: 0.6 + f(20), active: [0.6, 0.6 + f(4)],
    melee: false, from: 'body', fireAt: [0.6], shotAhead: 14, shotZ: 18,
    shot: { kind: 'door', speed: 150, life: 2.6, range: 380, hitR: [6, 8, 26], dmg: 4, push: 2, guard: 'none', reflect: false, tag: 'door', draw: drawDoor },
    sfx: 'card_flip',
  };
  K.e_rohan = {
    hp: 500, speed: 44, standId: 'heavensdoor', moves: ['RH_PEN', 'RH_DOOR'], koStyle: 'none', idle: 'idle', armor: false,
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player;
      if (!p || !dt) return true;
      if (d.raceOn) { e.play('pose'); return true; }
      if (e.rootT > 0) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      // 走动：和仗助保持 70–120 px；每 0.42 s 一步，木地板吱呀一声（声源 = 波纹位置）
      const dx = p.x - e.x, adx = Math.abs(dx);
      e.facing = dx > 0 ? 1 : -1;
      m.side = m.side || (Math.random() < 0.5 ? -1 : 1);
      m.re = (m.re == null ? 3 : m.re) - dt;
      if (m.re <= 0) { m.re = 3 + Math.random() * 2; m.side = -m.side; m.ty = G.clamp(p.y + (Math.random() * 24 - 12), 146, 174); }
      const want = d.heard ? 40 : 90;
      const tx = G.clamp(p.x - Math.sign(dx || 1) * want, S7.arena[0] + 10, S7.arena[1] - 10), ty = m.ty || p.y;
      const moving = Math.abs(e.x - tx) > 6 || Math.abs(e.y - ty) > 3;
      if (moving) G.combat.walkTo(e, tx, ty, dt, e.speed * (d.heard ? 1.6 : 1));
      else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
      if (moving) {
        m.step = (m.step || 0) - dt;
        if (m.step <= 0) { m.step = 0.42; G.audio.sfx(Math.random() < 0.35 ? 'creak' : 'footstep' + (Math.floor(Math.random() * 4)), { vol: 0.5, x: e.x }); ripple(e.x, e.y, '#b0b8d0', { r: 16, dur: 0.7, rings: 1 }); }
      }
      if (m.noAtkUntil > clk().world) return true;
      m.gap = (m.gap == null ? 2.2 : m.gap) - dt;
      if (m.gap > 0 || G.combat.tokens() >= 1) return true;
      // 听见纸响：马上冲过去刺
      if (d.heard && adx < 80) { d.heard = false; G.AI.tele(e, 'RH_PEN'); m.gap = 1.2; return true; }
      if (adx < 70 && Math.abs(p.y - e.y) < 10) { G.AI.tele(e, 'RH_PEN'); m.gap = 1.8 + Math.random(); }
      else if (Math.abs(p.y - e.y) < 18) { G.AI.tele(e, 'RH_DOOR'); m.gap = 2.6 + Math.random(); }
      return true;
    },
    // 预警开始的那一刻发出声音：笔帽“咔”/ 翻页“哗啦”
    onWarnTick(e, u) {
      if (!e.tele || e.tele._snd) return;
      e.tele._snd = true;
      if (e.tele.move === 'RH_PEN') { G.audio.sfx('clang', { vol: 0.5, rate: 1.8, x: e.x }); ripple(e.x, e.y, '#ffb050', { r: 22, dur: 0.6, label: '咔', rings: 3 }); }
      else { G.audio.sfx('card_flip', { vol: 0.9, x: e.x }); ripple(e.x, e.y, '#ffe8a0', { r: 26, dur: 0.8, label: '哗啦', rings: 3 }); }
    },
  };
  const DOOR_HINT = '翻页声从哪边来，就往另一边 K 闪开';
  function hdSetup(S, ctx) {
    const d = ctx.data, rh = S.actor('rohan');
    d.dark = true; d.papers = []; d.paperT = 9; d.slowUntil = 0;
    ripples = [];
    S.filter('tint', 1, { colour: '#04030a' });
    S.state('pages', 0); S.state('hole', 0);
    if (d.h) d.h.close();
    d.h = darkLayer(ctx);
    if (R.checkpoint7 && rh) { rh.hp = Math.round(rh.maxHp * 0.42); }
    // 打中露伴：一圈红色波纹（拳头打到人的闷响）
    ctx.on('hit', (e) => { if (e.t && e.t.cid === 'rohan') ripple(e.t.x, e.t.y, '#ff6080', { r: 20, dur: 0.6, label: '咚' }); if (e.t === player()) ripple(e.t.x, e.t.y, '#ff4040', { r: 14, dur: 0.5 }); });
    S.hint('闭着眼睛打：看声音的波纹。「咔」= 笔尖要刺过来（K 闪 / L 挡），「哗啦」= 天堂之门扑过来（K 闪）', 9);
  }
  function hdTick(S, c, dt) {
    const d = c.data, p = player(), rh = S.actor('rohan');
    if (!p || !rh) return;
    const now = clk().world;
    // 半本书：走速 ×0.5
    p.speed = d.slowUntil > now ? 33 : 66;
    // 天堂之门的小人：飞行中一路“哗啦哗啦”
    for (const s of G.world.shots) if (s.tag === 'door' && !s.dead) {
      s._rip = (s._rip || 0) - dt;
      if (s._rip <= 0) { s._rip = 0.18; ripple(s.x, s.y, '#ffe8a0', { r: 10, dur: 0.5, rings: 1 }); }
      if (!s._hook) {
        s._hook = true;
        s.onHit = (sh, t) => {
          if (t !== player()) return;
          d.slowUntil = clk().world + 3; bookOn(t, 3); R.ensureBooks();
          S.sfx('card_flip', 1); S.sfxText('啪啦啪啦', t, { dur: 0.8 });
          if (!d.doorTold) { d.doorTold = true; S.hint(DOOR_HINT, 6); }
        };
      }
    }
    // 撒原稿：每 14 s 一次，地上铺三张纸；仗助踩上去就“沙”一声，露伴听见了会马上冲过来
    d.paperT -= dt;
    if (d.paperT <= 0 && !d.raceOn) {
      d.paperT = 14;
      S.sfx('card_flip', 0.9); S.sfx('wind', 0.3);
      ripple(rh.x, rh.y, '#ffffff', { r: 40, dur: 1.0, label: '哗——', rings: 3 });
      d.papers = [0, 1, 2].map((i) => ({ x: G.clamp(p.x + (i - 1) * 50 + (Math.random() * 20 - 10), 60, 460), y: G.clamp(p.y + (Math.random() * 20 - 10), 148, 172), cd: 0 }));
      S.state('pages', 1);
      if (!d.paperTold) { d.paperTold = true; S.hint('地上撒满了纸：走上去会发出声音，露伴就知道你在哪', 6); }
    }
    for (const q of d.papers) {
      q.cd = Math.max(0, q.cd - dt);
      if (q.cd <= 0 && p.state === 'walk' && Math.abs(p.x - q.x) < 18 && Math.abs(p.y - q.y) < 7) {
        q.cd = 0.8; d.heard = true;
        S.sfx('card_flip', 0.5); ripple(p.x, p.y, '#ffffff', { r: 18, dur: 0.6, label: '沙', rings: 2 });
      }
    }
  }
  // 发型挑衅（HP ≤ 40%）→ 发型记录 4 → 强制暴走：睁眼，暴走槽（连按 J）和“变成书”槽比快
  async function hairTaunt(S, ctx) {
    const d = ctx.data, p = player(), rh = S.actor('rohan');
    R.checkpoint7 = true;
    rh.atk = null; rh.tele = null; rh.state = 'idle'; rh.play('idle');
    S.hint(null);
    S.mark('b07_taunt');
    await S.say('rohan', '闭着眼睛也打得这么准……真是好素材。', { expr: 'smile' });
    await S.say('rohan', '可惜啊。顶着那种过时的发型，画进漫画里只会被当成笑料。', { expr: 'smile' });
    await P4().hair.show(S, 4);
    S.mark('ch5_hair4');
    await S.say('josuke', '……你说谁的发型是笑料？', { expr: 'rage' });
    // 睁眼
    d.dark = false;
    S.filter('tint', null);
    S.flash(0.2, 0.9, '#ffffff');
    S.sfx('sting_shock', 0.9);
    S.state('pages', 1);
    S.face(p, rh); S.face(rh, p);
    S.pose(rh, 'pose');
    await S.say('rohan', '你睁眼了。——天堂之门！', { expr: 'rage' });
    S.unpose(rh);
    R.hairRage(S, true);
    d.raceOn = true; d.rage = 0; d.book = 0; d.lastJ = G.input.lastPress('attack'); d.raceT = 0;
    S.hint('发型暴走！连按 J 冲上去打，赶在脸变成书之前！', 8);
  }
  function raceLayer(ctx) {
    return P4().overlay((g, t) => {
      const d = ctx.data;
      if (G.world.fight !== ctx || !d.raceOn) return;
      const bar = (y, label, k, col) => {
        G.ui.box(g, 170, y, 470, y + 26);
        text(g, label, 180, y + 6, '#fff4d6', 12, 'left');
        g.fillStyle = '#20182c'; g.fillRect(266, y + 8, 194, 10);
        g.fillStyle = col; g.fillRect(266, y + 8, Math.round(194 * Math.min(1, k)), 10);
      };
      bar(70, '发型暴走', d.rage / 100, '#d070e0');
      bar(100, '变成书', d.book / 100, '#f0e0b0');
      const pl = player();
      if (pl && G.cam && G.cam.w2u) { const q = G.cam.w2u(pl.x, pl.headY() - 6, 0); drawBookIcon(g, Math.round(q.x), Math.round(q.y - 12), t, d.book / 100); }
    }, { z: 3 });
  }
  function raceTick(S, c, dt) {
    const d = c.data;
    if (!d.raceOn || d.raceDone) return;
    d.raceT += dt;
    // 连按 J：每下 +4.6（按得再快也按 7 下/秒封顶）；变书槽 5 s 满
    const lp = G.input.lastPress('attack');
    if (lp !== d.lastJ) {
      if (lp - (d.lastCount || -9) >= 1 / 7) { d.lastCount = lp; d.rage = Math.min(100, d.rage + 4.6); }
      d.lastJ = lp;
    }
    const book = c.assist ? 100 / 6.5 : 100 / 5;
    d.book = Math.min(100, d.book + book * dt);
    if (d.rage >= 100) { d.raceDone = 'win'; cine(c, () => raceWin(S, c)); }
    else if (d.book >= 100) { d.raceDone = 'lose'; R.hairRage(S, false); c.fail('仗助变成了一本书……'); }
  }
  async function raceWin(S, ctx) {
    const d = ctx.data, p = player(), rh = S.actor('rohan');
    d.raceOn = false;
    S.hint(null);
    S.face(p, rh);
    await S.walk(p, rh.x - p.facing * 30, rh.y, { speed: 160, anim: 'run' });
    await S.summon(p, { dur: 0.08, rise: 4 });
    S.standAct(p, 'rush', { dx: 18, z: 4, hold: true, jitter: 1 });
    rh.play('hurt');
    for (let i = 0; i < 12; i++) G.defer(i * 0.07, () => { S.sfx('punch', 0.55); if (i % 4 === 0) S.sfxText('DORA', rh, { dur: 0.5, dx: i % 8 ? 10 : -10 }); });
    S.shake(3, 0.9);
    await S.wait(0.9);
    S.standAct(p, 'punch', { dx: 22, z: 4, dur: 0.5 });
    S.sfx('punch_heavy', 1); S.sfxText('DORA!!', rh, { dur: 0.9 });
    S.impact('invert', f(2));
    await S.arc(rh, 440, rh.y, 18, 0.45, { anim: 'hurt' });
    S.sfx('wall_slam', 1); S.sfx('crash', 0.8);
    S.state('hole', 1);
    S.shake(5, 0.4);
    S.pose(rh, 'down');
    S.recall(p);
    R.hairRage(S, false);
    S.mark('b07_win');
    await S.wait(0.6);
    d.won = true;
  }
  R.hairRage = (S, on) => { if (G.P4PRO && G.P4PRO.hairRage) G.P4PRO.hairRage(S, on); };
  R.fightHeavensDoor = async function (S) {
    S.hint(null);
    R.checkpoint7 = false;
    R.ensureBooks();
    const res = await S.fight({
      id: 'b07_heavensdoor', arena: S7.arena, lead: 'josuke', swap: false, lockMsg: '这一战只有仗助', music: 'battle', after: null,
      dmgScale: 1.0, losable: true, energy: { start: 0 },
      waves: [[{ kit: 'e_rohan', actor: 'rohan', cid: 'rohan', id: 'rohan', name: '岸边露伴', x: S7.rohan[0], y: S7.rohan[1], boss: true, hp: 500, minHp: 1 }]],
      testHint: (ctx) => { const rh = G.S.actor('rohan'), d = ctx.data; return { rohanHp: rh ? rh.hp : null, dark: !!d.dark, race: !!d.raceOn, rage: Math.round(d.rage || 0), book: Math.round(d.book || 0), cp: !!R.checkpoint7 }; },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const p = player();
        p.x = S7.josuke[0]; p.y = S7.josuke[1]; p.facing = 1;
        hdSetup(S2, ctx);
        if (ctx.data.rh) ctx.data.rh.close();
        ctx.data.rh = raceLayer(ctx);
        S2.mark('b07_start');
      },
      events: [{
        when: (t, ctx) => { const rh = G.S.actor('rohan'); return !!rh && rh.hp <= rh.maxHp * 0.4; },
        run: async (S2, es, attempt, ctx) => { await hairTaunt(S2, ctx); },
      }],
      tick: (c, dt) => { hdTick(S, c, dt); raceTick(S, c, dt); },
      endWhen: (c) => !!c.data.won,
    });
    S.filter('tint', null);
    R.hairRage(S, false);
    return res;
  };

  // =====================================================================================================================
  // 第 8 战 段 1 牧场屋内（b08a_ratt）：仗助弹钢珠打老鼠
  // =====================================================================================================================
  const S8 = { arena: [44, 472], josuke: [80, 160], stove: [171, 152],
    hides: [{ x: 340, y: 150, name: '桌子底下' }, { x: 292, y: 156, name: '左边椅子后面' }, { x: 388, y: 156, name: '右边椅子后面' },
      { x: 410, y: 166, name: '倒下的椅子后面' }, { x: 258, y: 148, name: '冰箱底下' }] };
  // 钢珠：疯狂钻石弹出去（远程，有一点散布）
  const drawBall = (P, x, y) => { const px = G.px; px.rect(P, x - 1, y - 1, 3, 3, '#c8d0e0', 1); px.rect(P, x - 1, y - 1, 1, 1, '#ffffff', 1); };
  M.CD_BALL = {
    slot: 'J1', body: 'cmd', stand: 'finger', standDx: 12, standZ: 4, dur: f(18), active: [f(6), f(8)], melee: false, from: 'stand',
    fireAt: [f(6)], link: f(12), cancel: f(12), shotAhead: 12, shotZ: 22,
    shot: { kind: 'ball', speed: 340, life: 1.2, range: 360, hitR: [3, 7, 22], dmg: 8, push: 2, energy: 2, slot: 'shot', reflect: false, tag: 'ball', draw: drawBall },
    shotMod: (a) => ({ ang: (a.facing < 0 ? Math.PI : 0) + (Math.random() - 0.5) * 0.07 }),
    sfx: 'ricochet', sfxVol: 0.4, sfxRate: 1.6, energy: 0, accent: '#ffc8e4',
  };
  const drawDart = (P, x, y, s) => {
    const px = G.px, dir = Math.sign(s.vx) || 1;
    px.line(P, x, y, x - dir * 6, y, '#d8dce8', 1, 1); px.rect(P, x + dir * 0 - 1, y - 1, 2, 2, '#8a3a6a', 1);
  };
  const DART = { kind: 'dart', speed: 230, life: 2.0, range: 420, hitR: [3, 6, 20], dmg: 30, push: 6, guard: 'none', reflect: false, tag: 'dart', draw: drawDart };
  M.RAT_AIM = {
    slot: 'enemy', body: 'aim', stand: null, warn: { tier: 'W4', dur: 0.5, path: (e) => { const p = G.world.player; return [[e.x, e.y], [p ? p.x : e.x + e.facing * 160, p ? p.y : e.y]]; } },
    dur: 0.5 + 0.3, active: [0.5, 0.52], melee: false, sfx: null,
  };
  K.e_rat = {
    hp: 1, speed: 120, moves: [], koStyle: 'down', idle: 'idle', bodyW: 4,
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player;
      if (!p || !dt) return true;
      if (d.duel || e.hp <= 0) return true;
      m.mode = m.mode || 'hide';
      m.t = (m.t || 0) + dt;
      const spot = S8.hides[m.spot || 0];
      if (m.mode === 'run') {
        e.untargetable = false; e.alpha = 1;
        G.combat.walkTo(e, spot.x, spot.y, dt, e.speed);
        if (Math.abs(e.x - spot.x) < 3 && Math.abs(e.y - spot.y) < 2) { m.mode = 'hide'; m.t = 0; m.wait = 1.6 + Math.random() * 1.6; }
        return true;
      }
      if (m.mode === 'hide') {
        e.untargetable = true; e.alpha = 0.28; e.play('idle'); e.state = 'idle';
        if (m.t >= (m.wait || 2)) { m.mode = 'aim'; m.t = 0; e.untargetable = false; e.alpha = 1; e.facing = p.x > e.x ? 1 : -1; e.play('aim'); m.fired = false; }
        return true;
      }
      if (m.mode === 'aim') {
        // 枪从背上翻出来 0.5 s（红色细线）→ 开火 → 跑去下一个藏身处
        e.facing = p.x > e.x ? 1 : -1;
        if (!m.fired && m.t >= 0.5) {
          m.fired = true; e.play('fire');
          const ang = Math.atan2(p.y - e.y, p.x - e.x);
          G.combat.shoot(e, Object.assign({}, DART, { ang }), { x: e.x + e.facing * 8, y: e.y, z: 10 });
          G.audio.sfx('knife_throw', { vol: 0.7, rate: 1.4, x: e.x });
        }
        if (m.t >= 0.85) { let n; do { n = Math.floor(Math.random() * S8.hides.length); } while (n === (m.spot || 0)); m.spot = n; m.mode = 'run'; m.t = 0; e.play('walk'); }
        return true;
      }
      return true;
    },
  };
  function ratLayer(ctx) {
    return P4().overlay((g) => {
      const d = ctx.data, p = player();
      if (G.world.fight !== ctx) return;
      if (d.melt && p) {
        text(g, '溶解中 −2/秒', 92, 76, '#ffb0e0', 12, 'left');
      }
      // 瞄准时的红色细线（世界层那条在黑屋里也看得见，这里只在枪口加一个亮点）
      const rat = G.S.actor('rat_a');
      if (rat && rat.mem && rat.mem.mode === 'aim' && !rat.mem.fired && G.cam) {
        const q = G.cam.w2u(rat.x + rat.facing * 6, rat.y - 10, 0);
        g.fillStyle = Math.floor(clk().ui * 12) % 2 ? '#ff3030' : '#ffd0d0'; g.fillRect(Math.round(q.x) - 2, Math.round(q.y) - 2, 4, 4);
      }
    }, { z: 1 });
  }
  function ratSetup(S, ctx) {
    const d = ctx.data;
    d.pan = false; d.melt = false; d.deflects = 0; d.duel = false; d.ratDown = false; d.meltFx = 0;
    S.state('pan', 0);
    if (d.h) d.h.close();
    d.h = ratLayer(ctx);
    ctx.on('hit', (e) => {
      const p = player();
      if (e.t === p && e.move && e.move.tag === 'dart') {
        if (!d.melt) { d.melt = true; S.hint('飞镖打中了：被打中的地方在“溶解”，每秒 −2。仗助治不了自己！', 6); }
        S.sfxText('滋……', p, { dur: 0.8 });
      }
      if (e.t && e.t.cid === 'rat_a' && e.t.hp <= 0) d.ratDown = true;
    });
    S.hint('J 弹钢珠（远程）。老鼠躲在家具后面，探出头瞄准时才打得到。灶台上有只平底锅（走过去按 E）', 9);
  }
  function ratTick(S, c, dt) {
    const d = c.data, p = player(), rat = S.actor('rat_a');
    if (!p) return;
    // 溶解：这一段里不会好
    if (d.melt) {
      p.hp = Math.max(1, p.hp - 2 * dt * (c.assist ? 0.5 : 1));
      d.meltFx -= dt;
      if (d.meltFx <= 0) { d.meltFx = 0.8; S.fx('smoke', { x: p.x + 3, y: p.y - 22, n: 3, rise: 10, life: 0.6, colour: '#e0a0d0' }, { life: 0.7 }); }
    }
    // 平底锅：灶台前按 E
    if (!d.pan && Math.abs(p.x - S8.stove[0]) < 22 && Math.abs(p.y - S8.stove[1]) < 12) {
      if (!d.panHint) { d.panHint = true; S.hint('灶台上的平底锅：按 E 拿起来', 4); }
      if (G.input.hit('ok')) {
        G.input.consume('ok');
        d.pan = true; d.panT = c.t; S.state('pan', 1);
        S.sfx('clang', 0.8); S.sfxText('锵', p, { dur: 0.7 });
        S.hint('拿着平底锅按住 L：能把飞镖弹开（空手挡不住）', 6);
        S.mark('b08a_pan');
      }
    }
    if (d.pan && !p.mem.panProp) {
      p.mem.panProp = true;
    }
    // 平底锅弹开飞镖
    for (const s of G.world.shots) if (s.tag === 'dart' && !s.dead) {
      if (d.pan && p.state === 'guard' && Math.sign(s.x - p.x) === p.facing && Math.abs(s.x - p.x) < 18 && Math.abs(s.y - p.y) < 9) {
        s.dead = true; d.deflects++;
        S.sfx('clang', 1); S.sfxText('锵！', p, { dur: 0.6 });
        S.fx('hit_spark', { x: p.x + p.facing * 12, y: p.y - 18, size: 10, accent: '#ffffff' });
      }
    }
    // 最后的对射：拿着锅、弹开过一次（或者拿锅以后 10 s）→ 它跳上桌子正面对射
    if (rat && rat.hp > 0 && d.pan && !d.duel && (d.deflects >= 1 || c.t - d.panT > 10) && rat.mem.mode === 'hide') {
      d.duel = true;
      cine(c, () => ratDuel(S, c, rat));
    }
  }
  async function ratDuel(S, ctx, rat) {
    const d = ctx.data, p = player();
    S.hint(null);
    rat.untargetable = false; rat.alpha = 1; rat.atk = null; rat.tele = null;
    S.sfx('creak', 0.7);
    await S.arc(rat, 340, 150, 26, 0.35, { z1: 14 });
    rat.z = 14;
    S.face(rat, p); S.face(p, rat);
    if (Math.abs(p.y - rat.y) > 4) await S.walk(p, p.x, rat.y, { speed: 60 });
    S.face(p, rat);
    rat.play('aim');
    S.mark('b08a_duel');
    S.sfx('heartbeat', 0.6);
    await S.narrate('它把枪口对准了我。……我也一样。', { pos: 'top' });
    for (let tries = 0; ; tries++) {
      // 它和仗助同时开火：L 用平底锅弹开飞镖，紧接着 J
      const r1 = await S.press({ key: 'guard', window: 0.6, label: 'L！用平底锅挡！' });
      S.sfx('knife_throw', 0.8);
      if (r1 === 'miss' && tries < 3) {
        S.sfx('stab', 0.8); p.hp = Math.max(1, p.hp - 20); p.flash = 1; d.melt = true;
        S.sfxText('滋……', p, { dur: 0.8 });
        await S.say('josuke', '……可恶，再来！', { expr: 'rage' });
        continue;
      }
      S.sfx('clang', 1); S.sfxText('锵！', p, { dur: 0.6 }); S.fx('hit_spark', { x: p.x + p.facing * 12, y: p.y - 18, size: 12, accent: '#ffffff' });
      const r2 = await S.press({ key: 'attack', window: 0.6, label: 'J！' });
      if (r2 === 'miss' && tries < 3) { await S.say('josuke', '慢了一步……再来！', { expr: 'rage' }); continue; }
      break;
    }
    await S.summon(p, { dur: 0.06, rise: 2 });
    S.standAct(p, 'finger', { dx: 12, dur: 0.4 });
    S.sfx('ricochet', 0.8, 1.5);
    S.fx('hit_spark', { x: rat.x, y: rat.y - 18, size: 10, accent: '#c8d0e0' });
    S.sfx('punch', 0.7);
    rat.hp = 0;
    await S.arc(rat, rat.x + 16, 156, 10, 0.3, { anim: 'hurt' });
    rat.z = 0; S.pose(rat, 'down');
    S.recall(p);
    d.ratDown = true;
    S.mark('b08a_rat_down');
  }
  R.fightRattA = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b08a_ratt', arena: S8.arena, lead: 'josuke', swap: false, lockMsg: '仗助一个人', music: 'battle', after: null,
      dmgScale: 1.0, losable: true, energy: { start: 0 }, bench: { mode: 'hide' },
      kitOverride: { josuke: { combo: ['CD_BALL', 'CD_BALL', 'CD_BALL'], rush: null } },
      waves: [[{ kit: 'e_rat', cid: 'rat_a', id: 'rat_a', name: '老鼠', x: S8.hides[0].x, y: S8.hides[0].y, hp: 1, bodyW: 4 }]],
      testHint: (ctx) => { const r = G.S.actor('rat_a'), d = ctx.data; return { pan: !!d.pan, melt: !!d.melt, deflects: d.deflects || 0, duel: !!d.duel, rat: r ? r.mem.mode : null, hp: Math.round(player().hp) }; },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const p = player();
        p.x = S8.josuke[0]; p.y = S8.josuke[1]; p.facing = 1; p.mem.panProp = false;
        const rat = spawned[0];
        if (rat) { rat.mem.spot = 0; rat.mem.mode = 'hide'; rat.mem.wait = 2.4; }
        ratSetup(S2, ctx);
        S2.mark('b08a_start');
      },
      tick: (c, dt) => ratTick(S, c, dt),
      endWhen: (c) => !!c.data.ratDown,
    });
    return res;
  };

  // =====================================================================================================================
  // 第 8 战 段 2 山坡（b08b_hill）：两发步枪子弹。承太郎往坡上走当诱饵，玩家握狙击准星（随呼吸晃）
  // =====================================================================================================================
  const HILL = { cam: 700, rat: [778, 85], rock: [668, 112], josuke: [560, 168] };
  function scopeLayer(ctx) {
    return P4().overlay((g, t) => {
      const d = ctx.data;
      if (G.world.fight !== ctx || !d.scope || !G.cam) return;
      const q = G.cam.w2u(d.aimX, d.aimY, 0), x = Math.round(q.x), y = Math.round(q.y);
      // 暗角 + 准星
      g.save();
      g.fillStyle = 'rgba(0,0,0,0.55)';
      g.beginPath(); g.rect(0, 0, UW, UH); g.arc(x, y, 70, 0, Math.PI * 2, true); g.fill();
      g.strokeStyle = '#101010'; g.lineWidth = 3; g.beginPath(); g.arc(x, y, 70, 0, Math.PI * 2); g.stroke();
      g.strokeStyle = '#ff4a4a'; g.lineWidth = 1;
      g.beginPath(); g.moveTo(x - 60, y + 0.5); g.lineTo(x - 6, y + 0.5); g.moveTo(x + 6, y + 0.5); g.lineTo(x + 60, y + 0.5);
      g.moveTo(x + 0.5, y - 60); g.lineTo(x + 0.5, y - 6); g.moveTo(x + 0.5, y + 6); g.lineTo(x + 0.5, y + 60); g.stroke();
      g.fillStyle = '#ff4a4a'; g.fillRect(x - 1, y - 1, 2, 2);
      g.restore();
      // 子弹数和屏息
      for (let i = 0; i < 2; i++) { g.fillStyle = i < d.ammo ? '#f0c860' : '#3a3a3a'; g.fillRect(560 + i * 14, 300, 8, 22); g.fillStyle = '#20180a'; g.fillRect(560 + i * 14, 300, 8, 3); }
      text(g, '子弹', 548, 326, '#fff4d6', 12, 'left');
      G.ui.box(g, 20, 300, 160, 330);
      text(g, '屏住呼吸（按住 L）', 28, 304, '#fff4d6', 12, 'left');
      g.fillStyle = '#20182c'; g.fillRect(28, 320, 124, 5);
      g.fillStyle = d.breathOut ? '#a04040' : '#80d0ff'; g.fillRect(28, 320, Math.round(124 * d.breath), 5);
      if (d.flashRock > 0) { const r = G.cam.w2u(HILL.rock[0], HILL.rock[1], 0); g.fillStyle = 'rgba(255,255,255,' + Math.min(1, d.flashRock * 3) + ')'; g.fillRect(Math.round(r.x) - 4, Math.round(r.y) - 4, 8, 8); }
      if (d.reveal) {
        const r = G.cam.w2u(HILL.rat[0], HILL.rat[1] - 4, 0);
        if (Math.floor(t * 8) % 2) { g.fillStyle = '#ffffff'; g.fillRect(Math.round(r.x) - 1, Math.round(r.y) - 5, 2, 10); g.fillRect(Math.round(r.x) - 5, Math.round(r.y) - 1, 10, 2); }
        // 枪口对准仗助的红线（仗助在画面左下）
        const j = G.cam.w2u(HILL.josuke[0], HILL.josuke[1] - 20, 0);
        g.strokeStyle = 'rgba(255,48,48,0.8)'; g.setLineDash([4, 4]); g.beginPath(); g.moveTo(r.x, r.y); g.lineTo(j.x, j.y); g.stroke(); g.setLineDash([]);
      }
    }, { z: 2 });
  }
  function hillSetup(S, ctx) {
    const d = ctx.data, p = player();
    d.scope = true; d.ammo = 2; d.reveal = false; d.breath = 1; d.breathOut = false; d.flashRock = 0; d.decoyT = 3.5; d.won = false;
    d.aimX = 640; d.aimY = 120; d.lastJ = G.input.lastPress('attack');
    p.x = HILL.josuke[0]; p.y = HILL.josuke[1]; p.facing = 1; p.hold = true; p.play('idle');
    G.world.focus = { x: HILL.cam }; G.world.snapCamera();
    const jt = S.actor('jotaro4');
    if (jt) { Object.assign(jt, { x: 600, y: 150, facing: 1, visible: true, follow: null, team: 'npc' }); jt.play('walk'); }
    d.jtPath = [[600, 150], [680, 140], [740, 128], [820, 112]]; d.jtI = 0;
    const rat = S.actor('mushikui');
    if (rat) { Object.assign(rat, { x: HILL.rat[0], y: HILL.rat[1] + 60, z: 60, alpha: 0, facing: -1, visible: true }); }
    if (d.h) d.h.close();
    d.h = scopeLayer(ctx);
    S.hint('方向键移动准星，按住 L 屏住呼吸（准星不晃），J 开枪。只有两发！', 9);
  }
  function hillTick(S, c, dt) {
    const d = c.data, I = G.input, p = player();
    if (!d.scope) return;
    // 准星：方向键移动 + 呼吸晃动（屏住呼吸时几乎不晃，最多屏 3 s）
    const sp = 70;
    if (I.isDown('left')) d.aimX -= sp * dt; if (I.isDown('right')) d.aimX += sp * dt;
    if (I.isDown('up')) d.aimY -= sp * 0.7 * dt; if (I.isDown('down')) d.aimY += sp * 0.7 * dt;
    d.aimX = G.clamp(d.aimX, HILL.cam - 150, HILL.cam + 150); d.aimY = G.clamp(d.aimY, 20, 172);
    const holding = I.isDown('guard') && !d.breathOut && d.breath > 0;
    d.breath = G.clamp(d.breath + (holding ? -dt / 3 : dt / 4), 0, 1);
    if (d.breath <= 0) d.breathOut = true;
    if (d.breathOut && d.breath >= 0.5) d.breathOut = false;
    const amp = holding ? 0.6 : (d.breathOut ? 9 : 6);
    d.swayX = Math.sin(c.t * 1.7) * amp; d.swayY = Math.cos(c.t * 1.1) * amp * 0.6;
    const ax = d.aimX + d.swayX, ay = d.aimY + d.swayY;
    // 显示用的准星位置 = 带晃动的
    d.showX = ax; d.showY = ay;
    // 承太郎往坡上走（诱饵）
    const jt = S.actor('jotaro4');
    if (jt && d.jtI < d.jtPath.length) {
      const [tx, ty] = d.jtPath[d.jtI];
      const dx = tx - jt.x, dy = ty - jt.y, dd = Math.hypot(dx, dy);
      if (dd < 2) d.jtI++; else { jt.x += dx / dd * 16 * dt; jt.y += dy / dd * 16 * dt; jt.facing = dx >= 0 ? 1 : -1; jt.play('walk'); }
    } else if (jt) jt.play('idle');
    // 飞镖从岩石上跳弹打中承太郎：岩石那里一闪（那只是反射点）
    if (!d.reveal) {
      d.decoyT -= dt;
      if (d.decoyT <= 0) {
        d.decoyT = 5.5; d.flashRock = 0.4;
        S.sfx('ricochet', 0.8); S.sfx('knife_hit', 0.6);
        if (jt) { S.sfxText('叮', { wx: HILL.rock[0], wy: HILL.rock[1], wz: 0 }, { dur: 0.6 }); S.emote(jt, '……', 0.8); jt.flash = 1; }
        if (!d.decoyTold) { d.decoyTold = true; S.hint('岩石那里一闪……飞镖是从哪儿打来的？', 5); }
      }
    }
    d.flashRock = Math.max(0, d.flashRock - dt);
    // 暴露以后：它 4 s 内就会开枪打仗助（放水再来 6 s）
    if (d.reveal) {
      d.revealT += dt;
      if (d.revealT > (c.assist ? 6 : 4) && !d.won) { d.scope = false; c.fail('虫食先开了枪……'); return; }
    }
    // J 开枪
    const lp = I.lastPress('attack');
    if (lp !== d.lastJ) { d.lastJ = lp; if (d.ammo > 0 && !d.firing) cine(c, () => fire(S, c, ax, ay)); }
    void p;
  }
  async function fire(S, ctx, ax, ay) {
    const d = ctx.data;
    d.firing = true;
    d.ammo--;
    S.sfx('gunshot', 1); S.shake(3, 0.2); S.flash(0.06, 0.6, '#ffffff');
    S.fx('smoke', { x: ax, y: ay, n: 5, rise: 6, life: 0.5, colour: '#d8d0c0' }, { life: 0.6 });
    const hitRat = Math.hypot(ax - HILL.rat[0], (ay - HILL.rat[1]) * 1.2) <= (d.reveal ? 9 : 6);
    await S.wait(0.3);
    if (hitRat) { d.firing = false; await killRat(S, ctx); return; }
    if (d.ammo === 1) {
      // 第一发：打在哪都一样，老鼠都会转身把枪口对准仗助，露出藏身处
      S.mark('b08b_shot1');
      if (Math.hypot(ax - HILL.rock[0], ay - HILL.rock[1]) < 12) await S.say('josuke', '……岩石后面什么都没有！那只是反射点！', { expr: 'shock' });
      else await S.say('josuke', '没打中……！', { expr: 'shock' });
      const rat = S.actor('mushikui');
      if (rat) { rat.alpha = 1; rat.z = 60; rat.facing = -1; rat.play('aim'); }
      S.sfx('sting_shock', 0.8);
      d.reveal = true; d.revealT = 0;
      S.mark('b08b_reveal');
      await S.say('jotaro4', '它转过来了。……对着你。', {});
      S.hint('草丛里一闪——就是那里！最后一发！', 5);
      d.firing = false;
      return;
    }
    d.firing = false;
    d.scope = false;
    ctx.fail('两发都没打中……');
  }
  async function killRat(S, ctx) {
    const d = ctx.data, rat = S.actor('mushikui');
    d.scope = false;
    S.sfx('punch', 0.8);
    if (rat) { rat.alpha = 1; S.fx('hit_spark', { x: rat.x, y: rat.y - rat.z - 6, size: 12, accent: '#ffffff' }); S.pose(rat, 'down'); }
    S.mark('b08b_kill');
    await S.wait(0.8);
    d.won = true;
  }
  R.fightHill = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b08b_hill', arena: [8, 952], lead: 'josuke', swap: false, lockMsg: '仗助在瞄准', music: 'tension', after: null,
      dmgScale: 1.0, losable: true, energy: { start: 0 }, bench: { mode: 'stay' },
      waves: [],
      testHint: (ctx) => { const d = ctx.data; return { ammo: d.ammo, reveal: !!d.reveal, aim: [Math.round(d.showX || 0), Math.round(d.showY || 0)], breath: Math.round((d.breath || 0) * 100) }; },
      onRetry: async (S2) => { await S2.say('jotaro4', '……再来。这次稳住。'); },
      tick: (c, dt) => {
        if (!c.data.setup) { c.data.setup = true; hillSetup(S, c); S.mark('b08b_start'); }
        hillTick(S, c, dt);
      },
      endWhen: (c) => !!c.data.won,
    });
    const p = player();
    if (p) p.hold = false;
    G.world.focus = null;
    return res;
  };
})();
