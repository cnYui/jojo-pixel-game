// 第9章　国道隧道 / 宇宙人、公路之星与猫草：战斗和小游戏（开发脚本 §3）。
//   骰子小游戏 b_ch9_dice（露伴宅）、第 14 战 公路之星三段：b14a_tunnel（隧道救露伴）、b14b_road（海边国道三车道追车）、b14c_ward（病房 Boss）。
//   四段都走 S.fight（重来、放水、HUD 都现成）；骰子和追车不是打架：给队长挂一个 script 接管输入（world.js：有 script 就不走 updatePlayer），
//   打完还原。剧情节拍在 story/p4_ch9.js。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const R = (G.P4CH9 = {});
  const M = G.MOVES, K = G.KITS;
  const player = () => G.world.player;
  const text = (g, s, x, y, col, size, align) => P4().text(g, s, x, y, col || '#fff4d6', size || 12, align || 'left');
  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-ch9' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  const lockPlayer = (fnScript) => { const p = player(); if (p) { p.script = fnScript || (() => {}); p.state = 'idle'; } };
  // 打完那一帧队长可能还在连打：拳声循环要收掉（不然过场里一直响）
  const stopRush = () => { const p = player(); if (p && G.combat && G.combat.stopRush) G.combat.stopRush(p); };
  const unlockPlayer = () => { const p = player(); if (p) { p.script = null; p.state = 'idle'; p.play(p.idleAnim || 'idle'); } };

  // =====================================================================================================================
  // 骰子小游戏（b_ch9_dice）：简化的 Chinchirorin。露伴先摇，仗助摇两颗真骰子 + 未起隆变的第三颗（←→ 选点数，J 定）。
  //   赢就行，别赢太多：赢得越多、越快、越漂亮，露伴的怀疑涨得越多（开发脚本 §3）
  // =====================================================================================================================
  function hand(ds) {
    const s = ds.slice().sort((a, b) => a - b);
    if (s[0] === s[2]) return { v: 10 + s[0], name: '豹子 ' + s[0] };
    if (s[0] === 4 && s[1] === 5 && s[2] === 6) return { v: 9, name: '4-5-6' };
    if (s[0] === 1 && s[1] === 2 && s[2] === 3) return { v: -1, name: '1-2-3（输）' };
    if (s[0] === s[1]) return { v: s[2], name: s[2] + ' 点' };
    if (s[1] === s[2]) return { v: s[0], name: s[0] + ' 点' };
    return { v: 0, name: '无役' };
  }
  R.hand = hand;
  const roll = () => 1 + Math.floor(Math.random() * 6);
  // 露伴的牌：至少要有个点数（摇到无役重摇，最多三次，和规矩一样）
  function rohanRoll() {
    let ds;
    for (let i = 0; i < 3; i++) { ds = [roll(), roll(), roll()]; if (hand(ds).v !== 0) break; }
    return ds;
  }
  // 选这一面会让怀疑涨多少
  function suspicion(d, face) {
    const mine = hand([d.mine[0], d.mine[1], face]).v, his = hand(d.rohan).v;
    let s = 0;
    if (mine > his) { s = 12 + (mine - his) * 4; if (mine >= 9) s += 30; }
    else s = -6;
    return Math.round(s * (d.assist ? 0.6 : 1));
  }
  R.suspicion = suspicion;
  function diceDraw(ctx) {
    return P4().overlay((g) => {
      const d = ctx.data;
      if (!d.phase || G.world.fight !== ctx) return;
      const x0 = 150, y0 = 120, x1 = 490, y1 = 300;
      G.ui.box(g, x0, y0, x1, y1, { fill: 'rgba(30,18,10,0.92)' });
      text(g, '第 ' + (d.round + 1) + ' 局　仗助 ' + d.wins + ' 胜　露伴 ' + d.losses + ' 胜', 320, y0 + 8, '#ffe9a8', 12, 'center');
      // 碗
      g.fillStyle = '#5a3a1e'; g.fillRect(x0 + 40, y0 + 40, 260, 70);
      g.fillStyle = '#7a5230'; g.fillRect(x0 + 44, y0 + 44, 252, 62);
      g.fillStyle = '#3a2410'; g.fillRect(x0 + 52, y0 + 98, 236, 6);
      const showRohan = d.phase !== 'rohanRoll';
      const rv = showRohan ? d.rohan : [1 + (Math.floor(G.clk.ui * 12) % 6), 1 + (Math.floor(G.clk.ui * 9 + 2) % 6), 1 + (Math.floor(G.clk.ui * 11 + 4) % 6)];
      text(g, d.phase === 'rohanRoll' || d.phase === 'rohanShow' ? '露伴' : '仗助', x0 + 14, y0 + 34, d.phase === 'rohanRoll' || d.phase === 'rohanShow' ? '#d8c8ff' : '#ffd0e8', 12);
      if (d.phase === 'rohanRoll' || d.phase === 'rohanShow') rv.forEach((v, i) => die(g, x0 + 110 + i * 44, y0 + 56, v, false));
      else {
        text(g, '露伴：' + hand(d.rohan).name, x0 + 170, y0 + 22, '#d8c8ff', 12, 'center');
        const sp = d.phase === 'pick';
        const mine = sp && d.t < 0.6 ? [1 + (Math.floor(G.clk.ui * 13) % 6), 1 + (Math.floor(G.clk.ui * 7 + 3) % 6)] : d.mine;
        die(g, x0 + 110, y0 + 56, mine[0], false);
        die(g, x0 + 154, y0 + 56, mine[1], false);
        die(g, x0 + 198, y0 + 56, d.face, true);
        const h = hand([d.mine[0], d.mine[1], d.face]);
        text(g, '仗助：' + (sp && d.t < 0.6 ? '……' : h.name), x0 + 170, y0 + 116, '#ffd0e8', 16, 'center');
        if (sp) {
          text(g, '← → 选未起隆停在几点　J 确定', 320, y1 - 34, '#fff4d6', 12, 'center');
          const s = suspicion(d, d.face);
          text(g, '露伴的怀疑 ' + (s >= 0 ? '+' : '') + s + '　剩 ' + Math.max(0, d.limit - d.t).toFixed(1) + ' 秒', 320, y1 - 18, s > 25 ? '#ff8a8a' : '#c8f0c8', 12, 'center');
        } else if (d.msg) text(g, d.msg, 320, y1 - 26, '#ffe070', 16, 'center');
      }
    }, { z: 2 });
  }
  function die(g, x, y, v, mk) {
    const s = 32;
    g.fillStyle = '#1a1020'; g.fillRect(x - 1, y - 1, s + 2, s + 2);
    g.fillStyle = mk ? '#fff6dc' : '#f4f0e8'; g.fillRect(x, y, s, s);
    if (mk) { g.fillStyle = 'rgba(200,170,90,0.5)'; g.fillRect(x, y, s, 2); g.fillRect(x, y, 2, s); }
    const P = { 1: [[1, 1]], 2: [[0, 0], [2, 2]], 3: [[0, 0], [1, 1], [2, 2]], 4: [[0, 0], [2, 0], [0, 2], [2, 2]],
      5: [[0, 0], [2, 0], [1, 1], [0, 2], [2, 2]], 6: [[0, 0], [2, 0], [0, 1], [2, 1], [0, 2], [2, 2]] }[v] || [];
    g.fillStyle = v === 1 ? '#d02030' : '#1a1020';
    for (const [i, j] of P) g.fillRect(x + 6 + i * 8 + (v === 1 ? -1 : 0), y + 6 + j * 8 + (v === 1 ? -1 : 0), v === 1 ? 8 : 6, v === 1 ? 8 : 6);
  }
  function diceNext(S, ctx) {
    const d = ctx.data;
    d.phase = 'rohanRoll'; d.t = 0; d.msg = null; d.rohan = rohanRoll(); d.mine = [roll(), roll()]; d.face = 1 + Math.floor(Math.random() * 6);
    S.sfx('clang', 0.5);
  }
  function diceTick(S, ctx, dt) {
    const d = ctx.data, I = G.input, rh = S.actor('rohan');
    if (!d.init) {
      d.init = true; d.round = 0; d.wins = 0; d.losses = 0; d.assist = ctx.assist || ctx.attempt >= 1; d.limit = 4;
      if (d.h) d.h.close();
      d.h = diceDraw(ctx);
      lockPlayer();
      diceNext(S, ctx);
      S.hint('三颗骰子比大小，先赢 2 局。别赢太多：露伴会起疑！', 6);
      return;
    }
    d.t += dt;
    if (d.phase === 'rohanRoll' && d.t > 1.1) { d.phase = 'rohanShow'; d.t = 0; S.sfx('clang', 0.7); S.emote(rh, hand(d.rohan).name, 1.2); }
    else if (d.phase === 'rohanShow' && d.t > 0.9) { d.phase = 'pick'; d.t = 0; d.picked = false; S.sfx('clang', 0.7); }
    else if (d.phase === 'pick') {
      if (d.t < 0.6) return;
      if (I.hit('left')) { I.consume('left'); d.face = d.face === 1 ? 6 : d.face - 1; S.sfx('blip', 0.4); }
      if (I.hit('right')) { I.consume('right'); d.face = d.face === 6 ? 1 : d.face + 1; S.sfx('blip', 0.4); }
      const go = I.hit('attack') || I.hit('ok');
      if (go || d.t > d.limit + 0.6) {
        if (go) { I.consume('attack'); I.consume('ok'); }
        const late = d.t > 3.1;
        const s = suspicion(d, d.face) + (late ? 8 : 0);
        const mine = hand([d.mine[0], d.mine[1], d.face]).v, his = hand(d.rohan).v;
        if (ctx.gauge) ctx.gauge.add(s);
        if (mine > his) { d.wins++; d.msg = '仗助赢了这一局！'; S.sfx('coin', 0.8); }
        else if (mine < his) { d.losses++; d.msg = '露伴赢了这一局。'; S.sfx('thud', 0.5); }
        else d.msg = '平局。';
        if (late) S.emote(rh, '……那颗骰子刚才动了？', 1.4);
        else if (s > 25) S.emote(rh, '……运气真好啊。', 1.4);
        d.phase = 'result'; d.t = 0;
      }
    } else if (d.phase === 'result' && d.t > 1.6) {
      if (ctx.gauge && ctx.gauge.value >= ctx.gauge.max) { ctx.fail('露伴：「……你在作弊吧，东方仗助。」'); return; }
      if (d.losses >= 3) { ctx.fail('露伴：「输了就要守规矩。来，让我读一读。」'); return; }
      if (d.wins >= 2) { d.done = true; return; }
      d.round++;
      diceNext(S, ctx);
    }
  }
  R.dice = async function (S) {
    S.hint(null);
    S.mark('b_dice_start');
    let h = null;
    try {
      await S.fight({
        id: 'b_ch9_dice', lead: 'josuke', swap: false, lockMsg: '这一局只能仗助来', music: 'daily', after: null, losable: true,
        waves: [], energy: { start: 0 },
        gauge: { max: 100, value: 0, label: '露伴的怀疑', color: '#c8a0ff' },
        testHint: (ctx) => ({ phase: ctx.data.phase, round: ctx.data.round, wins: ctx.data.wins, losses: ctx.data.losses, sus: ctx.gauge ? ctx.gauge.value : null }),
        tick: (c, dt) => { diceTick(S, c, dt); h = c.data.h; },
        endWhen: (c) => !!c.data.done,
      });
    } finally { if (h) h.close(); unlockPlayer(); }
    S.mark('b_dice_win');
  };

  // =====================================================================================================================
  // 公路之星的招式和 brain
  // =====================================================================================================================
  M.HS_PUNCH = {
    slot: 'enemy', body: 'punch', stand: null, warn: { tier: 'W1', dur: 0.35 }, dur: 0.35 + f(24), active: [0.35, 0.35 + f(8)],
    melee: false, dash: { dist: 40, time: f(8), w: 8 }, dmg: 10, push: 12, guard: 'normal',
    sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light', accent: '#ff9cbc', shake: [1, f(6)],
  };
  M.HS_LUNGE = Object.assign({}, M.HS_PUNCH, { warn: { tier: 'W1', dur: 0.4 }, dur: 0.4 + f(24), active: [0.4, 0.4 + f(10)], dash: { dist: 60, time: f(10), w: 8 }, dmg: 6 });
  // 抓人：红圈 0.6 s，抓中由剧情接（连按 J 挣开）；伤害只有 1，吸养分在 tick 里算
  M.HS_GRAB = {
    slot: 'enemy', body: 'reach', stand: null, warn: { tier: 'W3', dur: 0.6 }, dur: 0.6 + f(24), active: [0.6, 0.6 + f(10)],
    melee: false, dash: { dist: 44, time: f(8), w: 10 }, dmg: 1, push: 0, guard: 'normal', grab: true,
    sfx: 'whoosh', sfxHit: 'drain', fxHit: 'light', accent: '#ff9cbc',
  };
  // 隧道里的脚印形态：一直贴着追，偶尔扑一下；被打散时（m.scatter）不动
  K.e_highway_feet = {
    hp: 999, speed: 56, moves: ['HS_LUNGE'], koStyle: 'none', idle: 'idle', armor: true,
    brain(e, dt, ctx) {
      const m = e.mem, p = G.world.player;
      if (!p || m.scatter > 0 || m.hold) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      const dx = p.x - e.x;
      if (Math.abs(dx) > 12 || Math.abs(p.y - e.y) > 4) G.combat.walkTo(e, p.x - Math.sign(dx || 1) * 8, p.y, dt, e.speed * (ctx && ctx.assist ? 0.85 : 1));
      e.facing = dx > 0 ? 1 : -1;
      m.gap = (m.gap == null ? 3 : m.gap) - dt;
      if (m.gap <= 0 && Math.abs(dx) < 70 && Math.abs(dx) > 24 && Math.abs(p.y - e.y) < 8) { G.AI.tele(e, 'HS_LUNGE'); m.gap = 3 + Math.random() * 2; }
      return true;
    },
  };
  K.e_highway = {
    hp: 420, speed: 48, moves: ['HS_PUNCH', 'HS_GRAB'], koStyle: 'none', idle: 'idle',
    brain(e, dt, ctx) {
      const m = e.mem, p = G.world.player;
      if (!p || m.hold || (m.stun || 0) > 0) { m.stun = Math.max(0, (m.stun || 0) - dt); return true; }
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      const dx = p.x - e.x;
      e.facing = dx > 0 ? 1 : -1;
      if (Math.abs(dx) > 34 || Math.abs(p.y - e.y) > 5) G.AI.approach(e, p, 28, dt);
      else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
      m.gap = (m.gap == null ? 1.6 : m.gap) - dt;
      if (m.gap > 0 || Math.abs(dx) > 56 || Math.abs(p.y - e.y) > 10) return true;
      m.n = (m.n || 0) + 1;
      G.AI.tele(e, m.n % 3 === 0 ? 'HS_GRAB' : 'HS_PUNCH');
      m.gap = (ctx && ctx.assist ? 2.4 : 1.8) + Math.random() * 0.6;
      return true;
    },
  };
  function scatter(S, e, sec) {
    if (!e || e.mem.scatter > 0) return;
    e.mem.scatter = sec; e.atk = null; e.tele = null; e.state = 'idle';
    G.AI.hide(e, true, { alpha: 0 });
    for (let i = 0; i < 4; i++) {
      const fp = T().prop(S, 'ch9_foot', e.x + (i - 1.5) * 10, e.y + (i % 2) * 4, { id: 'scat' + T().count('scat') });
      if (fp) G.defer(sec, () => { fp.remove = true; });
    }
    S.sfx('footstep2', 0.7);
  }
  function drain(S, p, n) {
    p.hp = Math.max(0, p.hp - n); p.flash = 1;
    S.sfx('drain', 0.5);
    S.sfxText('吸', p, { dur: 0.5 });
  }

  // =====================================================================================================================
  // 段 1 隧道（b14a_tunnel）：走到房间门口按 E 把露伴拖出来，再跑到出口
  // =====================================================================================================================
  const TUN = { arena: [10, 950], room: 494, exit: 912 };
  function tunnelTick(S, c, dt) {
    const d = c.data, p = player(), hs = S.actor('highway');
    if (!p || !hs) return;
    if (!d.init) { d.init = true; S.hint('走到墙上的房间门口按 E：把露伴老师拖出来！（J 打散脚印）', 7); }
    if (hs.mem.scatter > 0) { hs.mem.scatter -= dt; if (hs.mem.scatter <= 0) { G.AI.hide(hs, false); hs.alpha = 0.7; hs.x = G.clamp(p.x - p.facing * 70, TUN.arena[0] + 10, TUN.arena[1] - 10); } }
    else if (Math.abs(hs.x - p.x) < 14 && Math.abs(hs.y - p.y) < 6 && !hs.atk) {
      d.drainT = (d.drainT || 0) + dt;
      if (d.drainT >= 0.5) { d.drainT = 0; drain(S, p, Math.round(5 * 1.1)); if (!d.drainTold) { d.drainTold = true; S.hint('被它贴上会吸养分！J 打散它，或者 K 闪开', 5); } }
    }
    // 露伴跟在后面
    const rh = S.actor('rohan');
    if (d.rohan && rh) { const tx = p.x - p.facing * 20; if (Math.abs(rh.x - tx) > 2) G.combat.walkTo(rh, tx, p.y + 4, dt, 80); }
    if (!d.rohan && Math.abs(p.x - TUN.room) < 22 && G.input.hit('ok')) {
      G.input.consume('ok');
      d.pulling = true;
      cine(c, async () => {
        const ok = await S.mash({ need: 8, time: 2.5, label: '连按 J！把露伴拖出来！' });
        if (!ok) { await S.say('josuke', '……再来！拉不动！', { expr: 'shock' }); d.pulling = false; return; }
        const a = G.P4CH9_cast(S, 'rohan', TUN.room, 150, { facing: 1 });
        a.team = 'npc';
        S.sfx('door', 0.7);
        S.state('room', 0);
        await S.say('rohan', '……东方仗助？被你救了，真是一辈子的耻辱……', { name: '露伴' });
        S.mark('b14a_rohan');
        d.rohan = true; d.pulling = false;
        p.speed = Math.round(p.speed * 0.8);
        S.hint('带着露伴老师往右跑，跑出隧道！', 5);
      });
    }
    if (d.rohan && p.x >= TUN.exit) d.out = true;
  }
  R.tunnel = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b14a_tunnel', arena: TUN.arena, lead: 'josuke', swap: false, lockMsg: '只有仗助在', music: 'battle', after: null,
      dmgScale: 1.1, losable: true, energy: { start: 0 }, steps: { n: 2, label: '救出露伴、跑出隧道' },
      waves: [[{ kit: 'e_highway_feet', cid: 'highway', id: 'highway', name: '公路之星', x: 640, y: 160, boss: true, hp: 999, minHp: 1, alpha: 0.7 }]],
      onWave: async (S2, wi, sp, att, ctx) => { const hs = sp[0]; if (hs) { hs.alpha = 0.7; hs.mem.scatter = 0; } S2.state('room', 1); },
      onRetry: async (S2) => { const rh = S2.actor('rohan'); if (rh) rh.remove = true; },
      testHint: (ctx) => ({ rohan: !!ctx.data.rohan, out: !!ctx.data.out, px: player() ? Math.round(player().x) : null }),
      tick: (c, dt) => {
        tunnelTick(S, c, dt);
        if (c.data.rohan && G.hud.steps) c.step(1);
        if (!c.data.hitOn) { c.data.hitOn = true; c.on('hit', (e) => { const hs = S.actor('highway'); if (e.t === hs) scatter(S, hs, 1.5); }); }
      },
      endWhen: (c) => !!c.data.out,
    });
    stopRush();
    S.mark('b14a_exit');
    return res;
  };

  // =====================================================================================================================
  // 段 2 海边国道（b14b_road）：原地跑、背景卷；↑↓ 换车道躲车；「距离」槽到 0 被抓住；撑 35 s 抓住卡车
  // =====================================================================================================================
  const LANES = [144, 158, 172];
  function roadTick(S, c, dt) {
    const d = c.data, p = player(), st = G.world.stage;
    if (!p) return;
    if (!d.init) {
      d.init = true; d.lane = 1; d.spawnT = 1.5; d.obs = []; d.goal = c.assist || c.attempt >= 1 ? 28 : 35;
      st.camX = 320; st.camTarget = 320; G.world.focus = { x: 480 };
      p.x = 520; p.y = LANES[1]; p.facing = 1;
      S.state('speed', 1.4);
      lockPlayer((pdt) => {
        const I = G.input;
        if (I.hit('up')) { I.consume('up'); d.lane = Math.max(0, d.lane - 1); }
        if (I.hit('down')) { I.consume('down'); d.lane = Math.min(2, d.lane + 1); }
        const ty = LANES[d.lane];
        p.y += G.clamp(ty - p.y, -160 * pdt, 160 * pdt);
        p.x = 520; p.facing = 1;
        p.play('run');
      });
      let hs = S.actor('hs_chase');
      if (!hs) { hs = S.spawn('highway', 360, 158, { id: 'hs_chase', facing: 1, name: '公路之星' }); hs.team = 'npc'; }
      hs.alpha = 0.75;
      d.warnH = P4().overlay((g) => {
        if (G.world.fight !== c) return;
        for (const o of d.obs) {
          if (o.x < 660) continue;
          const u = G.cam.w2u(640, o.y - 20, 0);
          const blink = Math.floor(G.clk.ui * 8) % 2;
          if (blink) text(g, '！', 618, Math.round(u.y), '#ff5050', 16, 'center');
        }
      }, { z: 2 });
      S.hint('↑ ↓ 换车道躲开车子！别被公路之星追上', 6);
      return;
    }
    // 公路之星：距离槽越小离得越近
    const hs = S.actor('hs_chase');
    const gap = c.gauge ? c.gauge.value : 60;
    if (hs) { hs.x = p.x - 22 - gap * 1.6; hs.y += G.clamp(p.y - hs.y, -60 * dt, 60 * dt); hs.facing = 1; hs.play(gap < 25 ? 'punch' : 'idle'); }
    // 出车
    d.spawnT -= dt;
    if (d.spawnT <= 0 && c.t < d.goal - 1.5) {
      d.spawnT = (c.assist || c.attempt >= 1 ? 2.4 : 1.25) + Math.random() * 0.6;
      const lane = Math.floor(Math.random() * 3), kind = Math.random() < 0.2 ? 'ch9_cone' : 'ch9_car';
      const a = T().prop(S, kind, 840, LANES[lane] + 1, { id: 'ob' + T().count('ob'), frame: Math.floor(Math.random() * 3) % (kind === 'ch9_car' ? 3 : 1) });
      if (a) { a.facing = -1; a.scale = 2; d.obs.push({ a, x: 840, y: LANES[lane], lane, v: kind === 'ch9_car' ? 230 : 180, hit: false }); S.sfx('car_engine', 0.3); }
    }
    for (const o of d.obs) {
      o.x -= o.v * dt; o.a.x = o.x;
      if (!o.hit && p.iframe <= 0 && Math.abs(o.x - p.x) < (o.a.scale > 1 ? 24 : 12) && Math.abs(o.y - p.y) < 7) {
        o.hit = true; p.hp = Math.max(0, p.hp - 11); p.flash = 1; p.iframe = 0.8;
        if (c.gauge) c.gauge.add(-25);
        S.sfx('crash', 0.8); S.shake(3, 0.3); S.sfxText('砰！', p, { dur: 0.6 });
      }
      if (o.x < 300) { o.a.remove = true; o.dead = true; }
    }
    d.obs = d.obs.filter((o) => !o.dead);
    if (c.gauge && c.gauge.value <= 0 && !d.grabbed) {
      d.grabbed = true;
      cine(c, async () => {
        S.sfxText('抓住了', p, { dur: 0.8 }); S.sfx('drain', 0.8);
        const ok = await S.mash({ need: 10, time: 2.2, label: '连按 J！挣开！' });
        if (!ok) drain(S, p, 15);
        if (c.gauge) c.gauge.value = 30;
        d.grabbed = false;
      });
    }
    if (c.t >= d.goal && !d.truck) {
      d.truck = true;
      cine(c, async () => {
        S.state('speed', 0.6);
        const tr = T().prop(S, 'ch9_truck', 300, p.y + 2, { id: 'truck' });
        if (tr) tr.scale = 2;
        if (tr) await S.animate(0.8, (k) => { tr.x = 300 + (p.x - 300 + 4) * k; });
        S.sfx('car_engine', 0.7);
        for (let i = 0; ; i++) {
          const r = await S.press({ key: 'attack', window: 0.9, label: '按 J 抓住卡车！' });
          if (r !== 'miss' || i >= 2) break;
          await S.say('josuke', '差一点！……再来！', { expr: 'shock' });
        }
        S.mark('b14b_truck');
        p.z = 16;
        if (tr) await S.animate(1.0, (k) => { tr.x = p.x + 4 + 300 * k; p.x = 520 + 300 * k; });
        d.done = true;
      });
    }
  }
  R.road = async function (S) {
    S.hint(null);
    await S.setStage('highway_ch9', { x: 520, y: 158, facing: 1, music: 'battle' });
    S.mark('b14b_start');
    let c0 = null;
    try {
      await S.fight({
        id: 'b14b_road', arena: [300, 940], lead: 'josuke', swap: false, lockMsg: '只有仗助在', music: 'battle', after: null,
        dmgScale: 1.1, losable: true, waves: [], energy: { start: 0 },
        gauge: { max: 100, value: 60, label: '距离', color: '#a0e0ff', rate: () => 2 },
        timer: { label: '甩掉它：', until: 35 },
        onRetry: async () => { for (const a of G.world.stage.actors) if (a.id && /^ob\d|^truck/.test(a.id)) a.remove = true; const p = player(); if (p) p.z = 0; },
        testHint: (ctx) => ({ lane: ctx.data.lane, t: Math.round(ctx.t), gap: ctx.gauge ? Math.round(ctx.gauge.value) : null }),
        tick: (c, dt) => {
          c0 = c; roadTick(S, c, dt);
          if (G.hud.timer && c.data.goal) G.hud.timer.until = c.data.goal;
        },
        endWhen: (c) => !!c.data.done,
      });
    } finally {
      if (c0 && c0.data.warnH) c0.data.warnH.close();
      unlockPlayer();
      const p = player(); if (p) p.z = 0;
      S.state('speed', 0);
    }
    await S.say('josuke', '它追人只能跑 60 公里。……而且是闻着气味追的。');
    await S.fadeOut(0.5);
  };

  // =====================================================================================================================
  // 段 3 病房（b14c_ward）：公路之星本体形态 Boss；抓住要连按 J 挣开；半血以后会散开绕到背后
  // =====================================================================================================================
  function wardTick(S, c, dt) {
    const d = c.data, p = player(), hs = S.actor('highway');
    if (!p || !hs) return;
    if (!d.init) {
      d.init = true;
      c.on('hit', (e) => {
        if (e.att === hs && e.t === p && e.move && e.move.grab && !d.grab) {
          d.grab = true;
          cine(c, async () => {
            hs.mem.hold = true;
            S.hint('被抓住了！连按 J 挣开！', 3);
            let t = 0;
            const tick = G.world.ticks;
            const fn = (dt2) => { t += dt2; if (t >= 0.4) { t = 0; drain(S, p, 4); } return !d.grab || G.world.fight !== c; };
            tick.push(fn);
            const ok = await S.mash({ need: c.assist ? 8 : 12, time: 3, label: '连按 J！挣开！' });
            d.grab = false;
            hs.mem.hold = false;
            if (ok) { hs.mem.stun = 1.0; S.sfxText('挣开了！', p, { dur: 0.7 }); }
            else drain(S, p, 8);
          });
        }
      });
      S.hint('公路之星：红圈是抓人，K 闪开；被抓住就连按 J', 6);
    }
    // 半血以后：每 8 s 散成脚印绕到背后
    if (hs.hp <= hs.maxHp * 0.5 && !d.grab) {
      d.wrapT = (d.wrapT || 0) + dt;
      if (d.wrapT >= 8 && !hs.atk && !hs.tele) {
        d.wrapT = 0;
        const bx = G.clamp(p.x - p.facing * 34, 62, 304);
        G.AI.blink(hs, bx, p.y, { word: null });
        S.flash(0.12, 0.5, '#ffd0e0');
        S.sfx('footstep3', 0.8);
        if (!d.wrapTold) { d.wrapTold = true; S.hint('它散开绕到你背后了！', 3); }
      }
    }
  }
  R.ward = async function (S) {
    S.hint(null);
    S.mark('b14c_start');
    await S.fight({
      id: 'b14c_ward', arena: [56, 310], lead: 'josuke', swap: false, lockMsg: '只有仗助在', music: 'battle', after: null,
      dmgScale: 1.1, losable: true, energy: { start: 30 },
      waves: [[{ kit: 'e_highway', cid: 'highway', id: 'highway', name: '公路之星', x: 240, y: 158, boss: true, hp: 420, minHp: 1 }]],
      testHint: (ctx) => { const hs = G.S.actor('highway'); return { hp: hs ? hs.hp : null, grab: !!ctx.data.grab }; },
      tick: (c, dt) => wardTick(S, c, dt),
      endWhen: (c) => { const hs = G.S.actor('highway'); return !!hs && hs.hp <= 1 && !c.data.grab; },
    });
    stopRush();
  };
})();
