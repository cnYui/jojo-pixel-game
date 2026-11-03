// 第1章　虹村家 / 弓与箭：两场战斗（开发脚本 第四部/docs/第1章_开发脚本.md §2）。剧情节拍在 story/p4_ch1.js；规矩见 第四部/docs/分章开发约定.md
//   第 1 战 轰炸空间（b01_thehand）：亿泰的削 / 拉近 / 扔砖 + 花盆机关（站在亿泰和花盆架的连线上，拉近会把花盆一起拉过来，K 闪开就砸他自己）。
//   第 2 战 坏公司：段 1 走廊（b02_badcompany_a，护住躺着的康一，三波：步兵齐射 / 地雷 / 坦克和直升机）、
//     段 2 楼梯（b02_badcompany_b，形兆在二楼平台打不到；三阶段“腿 → 手 → 头”，最后把落地的导弹碎片修好，让导弹飞回去打形兆）。
//   敌人的招式和 brain 写在这里（不改 engine/p4_moves.js），G.MOVES / G.KITS 里的 id 都带 OK_ / BC_ / e_ 前缀，和别章不撞。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const R = (G.P4CH1 = {});
  const UW = 640;

  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-fight' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  R.cine = cine;
  const player = () => G.world.player;
  const clk = () => (G.clk ? G.clk.ui : 0);
  // 世界坐标 → UI 层（640×360）坐标
  const w2u = (x, y, z) => (G.cam && G.cam.w2u ? G.cam.w2u(x, y, z || 0) : { x: x * 2, y: y * 2 });
  const setDown = (a, sec) => { a.atk = null; a.tele = null; a.state = 'down'; a.stateT = 0; a.downT = sec; a.play('down'); };
  // “按住 L 按 J”：这一帧有没有新按下的 J，而且人在格挡
  function fixPress(d, p) {
    const lp = G.input.lastPress('attack');
    if (lp === d.lastAtkPress) return false;
    d.lastAtkPress = lp;
    return p.cid === 'josuke' && p.state === 'guard';
  }

  // =====================================================================================================================
  // 第 1 战 轰炸空间（b01_thehand）
  // =====================================================================================================================
  const Y1 = { arena: [130, 620], ok: [430, 158], jo: [300, 160], rack: [264, 146], wall: [204, 140] };
  const LOW = 0.3, FLOOR = 0.25;
  // 削：右手举过头 0.5 s（地上一道白色竖裂），往前一抹。不能格挡
  const erase = (warn) => ({
    slot: 'enemy', body: 'cmd', stand: 'erase', standDx: 14, warn: { tier: 'W1', dur: warn }, dur: warn + f(22), active: [warn, warn + f(8)],
    reach: [0, 76], depth: 12, dmg: 18, push: 14, guard: 'none', sfx: 'whoosh', sfxHit: 'void_eat', fxHit: 'heavy', accent: '#9ab0ff',
    shake: [3, f(10)], word: null,
  });
  M.OK_ERASE = erase(0.5);
  M.OK_ERASE_FAST = erase(0.35);
  // 拉近：两人之间地上一道黑缝 0.4 s；判定那一刻仗助不在闪避里，就被拉到亿泰面前（onStart 处理），接一次快的削
  M.OK_PULL = {
    slot: 'enemy', body: 'cmd', stand: 'pull', standDx: 14, warn: { tier: 'W3', dur: 0.4 }, dur: f(20), active: [0, f(2)], melee: false, dmg: 0,
    sfx: 'void_eat', onStart: (a) => pullStart(a),
  };
  // 扔砖：削掉墙角，砖头从墙角飞向亿泰（tick 里飞）
  M.OK_BRICK = {
    slot: 'enemy', body: 'cmd', stand: 'erase', standDx: 14, warn: { tier: 'W3', dur: 0.5 }, dur: f(24), active: [0, f(2)], melee: false, dmg: 0,
    sfx: 'void_eat', onStart: (a) => brickStart(a),
  };
  let F1 = null;                 // 这一次尝试的战斗上下文（onStart 拿不到 ctx.data 以外的东西）
  K.e_okuyasu = {
    hp: 700, speed: 54, standId: 'thehand', moves: [], koStyle: 'none', idle: 'idle', poiseMax: 60,
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = player();
      if (!p || d.won) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      e.facing = p.x > e.x ? 1 : -1;
      if (m.chain) { const id = m.chain; m.chain = null; G.AI.tele(e, id, { target: p }); return true; }
      const dx = Math.abs(p.x - e.x), low = e.hp <= e.maxHp * LOW;
      // 保持 40 px 左右：近了削得到，远了用拉近和扔砖
      if (dx > 46 || Math.abs(p.y - e.y) > 6) G.AI.approach(e, p, 38, dt);
      else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
      m.gap = (m.gap == null ? 1.4 : m.gap) - dt;
      if (m.gap > 0 || G.combat.tokens() >= 1) return true;
      const al = aligned(e, p, d);
      let id;
      if (low) id = 'OK_PULL';                                  // 开发脚本：低血时只用拉近
      else if (al && Math.random() < 0.7) id = 'OK_PULL';       // 脑子不好使：看见人站在前面就想拉
      else if (dx < 56) { const r = Math.random(); id = r < 0.62 ? 'OK_ERASE' : r < 0.82 ? 'OK_PULL' : 'OK_BRICK'; }
      else id = Math.random() < 0.55 ? 'OK_PULL' : 'OK_BRICK';
      G.AI.tele(e, id, { target: p });
      m.gap = (low ? 1.6 : 1.5) + Math.random() * 0.8;
      return true;
    },
  };
  const potsLeft = () => 6 - ((G.world.stage.state || {}).pots_gone || 0);
  // 花盆架、仗助、亿泰在一条线上（花盆架在仗助背后、亿泰在仗助前面），y 差不超过 14
  function aligned(e, p, d) {
    if (!e || !p || potsLeft() <= 0 || (d && d.pot)) return false;
    const rx = Y1.rack[0];
    const between = (p.x - rx) * (e.x - p.x) > 0 && Math.abs(p.x - rx) >= 10 && Math.abs(e.x - p.x) >= 10;
    return between && Math.abs(p.y - e.y) <= 14 && Math.abs(p.y - Y1.rack[1]) <= 22;
  }
  R.aligned1 = () => { const c = F1; return !!c && aligned(G.S.actor('okuyasu'), player(), c.data); };
  function potSpot(n) {
    const an = (G.D.bg.nijimura_yard && G.D.bg.nijimura_yard.anchors) || {};
    return an['pot_' + n] || [Y1.rack[0], Y1.rack[1] - 10 - n * 4];
  }
  function pullStart(e) {
    const c = F1, p = player();
    if (!c || G.world.fight !== c || !p) return;
    const d = c.data, S = G.S;
    d.pulls = (d.pulls || 0) + 1;
    if (p.iframe > 0 || p.state === 'dodge') {
      S.sfxText('躲开了', p, { dur: 0.6 });
      return;
    }
    const al = aligned(e, p, d);
    // 仗助“咻”地被拉过去（0.12 s，带残影）
    const x0 = p.x, y0 = p.y, tgtX = G.clamp(e.x + (p.x < e.x ? -24 : 24), c.spec.arena[0] + 8, c.spec.arena[1] - 8);
    p.atk = null; if (p.rush) G.combat.stopRush(p);
    p.state = 'hurt'; p.stateT = 0; p._hurtDur = f(10); p.play('hurt');
    G.combat.ghostBurst(p, 3);
    S.sfx('whoosh', 0.9);
    S.animate(0.12, (k) => { p.x = G.lerp(x0, tgtX, k); p.y = G.lerp(y0, e.y, k); }).catch(G.cancelIgnore);
    if (al) {
      // 花盆跟着一起被拉过来：从架子上最上面那一个飞起，0.75 s 后到亿泰面前
      const n = ((G.world.stage.state || {}).pots_gone || 0) + 1;
      S.state('pots_gone', n);
      const [sx, sy] = potSpot(n);
      const pot = T().prop(S, 'pot', sx, Y1.rack[1] + 2, { id: 'ch1_pot', frame: 0, z: Math.max(4, Y1.rack[1] + 2 - sy) });
      d.pot = { a: pot, t: 0, dur: 0.75, x0: sx, y0: Y1.rack[1] + 2, z0: pot ? pot.z : 20, dodged: false, told: false };
      if (!d.potTold) { d.potTold = true; S.hint('花盆飞过来了！按 K 闪开！', 2.5); }
      S.sfx('void_eat', 0.6);
      e.mem.chain = 'OK_ERASE_FAST';
    } else e.mem.chain = 'OK_ERASE_FAST';
  }
  function brickStart(e) {
    const c = F1;
    if (!c || G.world.fight !== c) return;
    const S = G.S, d = c.data;
    S.sfx('crash', 0.6);
    S.fx('burst', { x: Y1.wall[0], y: Y1.wall[1] - 4, n: 8, speed: 26, colours: ['#c04030', '#8a3a2a'], gravity: 120, life: 0.5 });
    const b = T().prop(S, 'brick', Y1.wall[0], Y1.wall[1] + 6, { id: 'ch1_brick' + (d.brickN = (d.brickN || 0) + 1), frame: 0, z: 10 });
    if (b) (d.bricks = d.bricks || []).push({ a: b, x: Y1.wall[0], y: Y1.wall[1] + 6, hitP: false });
  }
  function hitEnemy(e, dmg, o = {}) {
    // 不算任何人的招（花盆 / 砖头 / 导弹是“东西”）：直接扣血，照样有火花、音效、受击
    e.hp = Math.max(o.min != null ? o.min : 1, e.hp - dmg);
    e.flash = 1;
    G.combat.fxAt('hit_spark', { x: e.x, y: e.y - 18, size: 16, accent: o.accent || '#ffe080' }, e, 0.3);
    G.S.sfx(o.sfx || 'punch_heavy', 0.9);
    if (o.down) setDown(e, o.down);
    else if (!e.atk && !e.tele) { e.state = 'hurt'; e.stateT = 0; e._hurtDur = f(16); e.play('hurt'); }
  }
  function okTick(S, c, dt) {
    const d = c.data, p = player(), e = S.actor('okuyasu');
    if (!p || !e) return;
    // 花盆在飞
    if (d.pot) {
      const q = d.pot;
      q.t += dt;
      if (p.state === 'dodge' || p.iframe > 0) q.dodged = true;
      const k = Math.min(1, q.t / q.dur);
      if (q.a) { q.a.x = G.lerp(q.x0, e.x, k); q.a.y = G.lerp(q.y0, e.y + 1, k); q.a.z = q.z0 + 18 * Math.sin(Math.PI * k); q.a.rot = k * 8; }
      if (k >= 1) {
        d.pot = null;
        if (q.a) { q.a.remove = true; }
        const bx = e.x, by = e.y;
        S.fx('burst', { x: bx, y: by - 26, n: 12, speed: 34, colours: ['#cc6a40', '#9a4a2c', '#68b050'], gravity: 140, life: 0.6 });
        S.sfx('glass_break', 0.7);
        if (q.dodged) {
          const low = e.hp <= e.maxHp * LOW;
          S.sfxText('咚！', e, { dur: 0.8 });
          S.shake(4, 0.3);
          S.mark('ch1_pot_hit');
          d.potHits = (d.potHits || 0) + 1;
          if (low) { d.won = true; e.atk = null; e.tele = null; return; }
          hitEnemy(e, 60, { min: 1, down: 2, sfx: 'thud' });
          e.mem.chain = null;
          if (!d.potHitTold) { d.potHitTold = true; S.hint('砸中了！花盆用完了就站到架子前，按住 L 按 J 修好', 5); }
        } else {
          // 没闪开：砸在仗助背上
          G.combat.hit(null, p, { slot: 'enemy', dmg: 10, push: 12, guard: 'none', sfxHit: 'thud', fxHit: 'light' });
          S.sfxText('咚', p, { dur: 0.6 });
        }
      }
    }
    // 砖头：从墙角飞向亿泰，路上的人也挨一下
    for (const b of d.bricks || []) {
      if (b.done || !b.a) continue;
      const dx = e.x - b.x, dy = e.y - b.y, dist = Math.hypot(dx, dy);
      const sp = 150 * dt;
      if (dist <= sp + 4) {
        b.done = true; b.a.remove = true;
        hitEnemy(e, 8, { min: Math.round(e.maxHp * FLOOR), sfx: 'thud' });
        S.sfxText('咣', e, { dur: 0.5 });
        if (!d.brickTold) { d.brickTold = true; S.hint('砖头砸到他自己了……', 3); }
        continue;
      }
      b.x += dx / dist * sp; b.y += dy / dist * sp;
      b.a.x = b.x; b.a.y = b.y; b.a.rot = (b.a.rot || 0) + dt * 10;
      if (!b.hitP && p.iframe <= 0 && p.invuln <= 0 && Math.abs(p.x - b.x) < 8 && Math.abs(p.y - b.y) < 7) {
        b.hitP = true;
        G.combat.hit(e, p, { slot: 'enemy', dmg: 8, push: 10, guard: 'normal', sfxHit: 'thud', fxHit: 'light' });
      }
    }
    if (d.bricks) d.bricks = d.bricks.filter((b) => !b.done);
    // 修花盆：花盆架前按住 L 按 J
    if (fixPress(d, p) && Math.abs(p.x - Y1.rack[0]) <= 28 && Math.abs(p.y - Y1.rack[1]) <= 20) {
      const n = (G.world.stage.state || {}).pots_gone || 0;
      if (n > 0) {
        const [sx, sy] = potSpot(n);
        S.state('pots_gone', n - 1);
        S.standAct(p, 'reach', { dx: 16, z: 6, dur: 0.6 });
        P4().fixGlow(S, sx, sy);
        d.fixes = (d.fixes || 0) + 1;
      }
    }
    // 提示：25 s 还没用过花盆，或者亿泰进了低血
    const low = e.hp <= e.maxHp * LOW;
    if (!d.potHint && ((c.t > 25 && !d.potHits) || low)) {
      d.potHint = true;
      S.hint('站到亿泰和花盆架中间（地上亮虚线），等他拉你的时候按 K', 8);
    }
    if (low && !d.lowTold) { d.lowTold = true; S.emote(e, '可、可恶……！', 1.2); }
    if (potsLeft() <= 0 && !d.emptyTold) { d.emptyTold = true; S.hint('花盆都碎了：站到花盆架前，按住 L 按 J 修好', 6); }
    d.aligned = aligned(e, p, d);
  }
  // 地上的东西：拉近的黑缝、削的空间裂纹、花盆连线的虚线（画在 UI 层，按世界坐标换算）
  let fx1H = null;
  function okOverlay() {
    return P4().overlay((g) => {
      const c = G.world.fight;
      if (!c || c !== F1 || G.world.insert) return;
      const e = G.S.actor('okuyasu'), p = player();
      if (!e || !p) return;
      const t = clk();
      if (e.tele && e.tele.move === 'OK_PULL') {
        // 两人之间的黑缝：从亿泰脚下往仗助那边裂开
        const k = Math.min(1, e.tele.t / e.tele.dur);
        const a = w2u(e.x, e.y + 1), b = w2u(G.lerp(e.x, p.x, k), G.lerp(e.y, p.y, k) + 1);
        g.fillStyle = '#0a0612';
        const n = 14;
        for (let i = 0; i < n; i++) {
          const u = i / n, x = G.lerp(a.x, b.x, u), y = G.lerp(a.y, b.y, u) + ((i % 2) ? 1 : -1);
          g.fillRect(Math.round(x) - 3, Math.round(y) - 1, 7, 3);
        }
        g.fillStyle = '#6a5aa0';
        g.fillRect(Math.round(b.x) - 2, Math.round(b.y) - 3, 4, 2);
      }
      if (e.tele && (e.tele.move === 'OK_ERASE' || e.tele.move === 'OK_ERASE_FAST')) {
        // 空间裂纹：亿泰前方地上一道白色竖裂，越来越亮
        const k = Math.min(1, e.tele.t / e.tele.dur);
        const q = w2u(e.x + e.facing * 30, e.y);
        g.save(); g.globalAlpha = 0.4 + 0.6 * k;
        g.fillStyle = '#ffffff';
        for (let i = 0; i < 10; i++) g.fillRect(Math.round(q.x + ((i % 3) - 1) * 2), Math.round(q.y - 6 - i * 6), 2, 6);
        g.fillStyle = '#9ab0ff';
        for (let i = 0; i < 10; i += 2) g.fillRect(Math.round(q.x + ((i % 3) - 1) * 2) + 2, Math.round(q.y - 6 - i * 6), 1, 6);
        g.restore();
      }
      if (c.data.aligned && Math.floor(t * 6) % 3 !== 2) {
        // 花盆架 → 仗助 → 亿泰 的连线：地上一条黄色虚线
        const a = w2u(Y1.rack[0], Y1.rack[1] + 6), b = w2u(e.x, e.y + 1);
        g.fillStyle = '#ffd84a';
        const L = Math.hypot(b.x - a.x, b.y - a.y), n = Math.floor(L / 12);
        for (let i = 0; i < n; i++) {
          const u = (i + 0.5) / n;
          g.fillRect(Math.round(G.lerp(a.x, b.x, u)) - 3, Math.round(G.lerp(a.y, b.y, u)), 6, 2);
        }
      }
    }, { z: -1 });
  }
  R.fightOkuyasu = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b01_thehand', arena: Y1.arena, lead: 'josuke', swap: false, lockMsg: '这一战只能由仗助应战',
      music: 'battle', after: null, dmgScale: 0.9, losable: true, energy: { start: 0 }, bench: { mode: 'stay' },
      waves: [[{ kit: 'e_okuyasu', actor: 'okuyasu', cid: 'okuyasu', id: 'okuyasu', name: '虹村亿泰', x: Y1.ok[0], y: Y1.ok[1], boss: true, hp: 700 }]],
      testHint: (ctx) => {
        const e = G.S.actor('okuyasu'), d = ctx.data;
        return { hp: e ? e.hp : null, max: e ? e.maxHp : null, pots: potsLeft(), potHits: d.potHits || 0, pulls: d.pulls || 0, aligned: !!d.aligned,
          pot: !!d.pot, fixes: d.fixes || 0, won: !!d.won };
      },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        F1 = ctx;
        const e = spawned[0], p = player();
        e.minHp = Math.round(e.maxHp * FLOOR);
        e.mem.gap = 1.2;
        S2.state('pots_gone', 0);
        p.x = Y1.jo[0]; p.y = Y1.jo[1]; p.facing = 1;
        ctx.data.lastAtkPress = G.input.lastPress('attack');
        if (fx1H) fx1H.close();
        fx1H = okOverlay();
        S2.hint('削（裂纹）不能挡：按 K 闪开。地上出现黑缝也按 K', 7);
      },
      tick: (c, dt) => okTick(S, c, dt),
      endWhen: (c) => !!c.data.won,
    });
    if (fx1H) { fx1H.close(); fx1H = null; }
    for (const a of G.world.stage.actors) if (a.id && (a.id === 'ch1_pot' || a.id.indexOf('ch1_brick') === 0)) a.remove = true;
    F1 = null;
    return res;
  };

  // =====================================================================================================================
  // 坏公司的兵：步兵 / 坦克 / 直升机（两段共用）
  // =====================================================================================================================
  const shotAt = (a, tg, speed) => {
    const t = tg || player();
    const ang = t ? Math.atan2((t.y - a.y), (t.x - a.x)) : (a.facing < 0 ? Math.PI : 0);
    return { ang, speed };
  };
  // 子弹 / 炮弹 / 导弹自己画（px 层）：小、亮、看得清方向
  const drawBullet = (P, x, y, s) => { const px = G.px; px.rect(P, x - 1, y - 1, 2, 2, '#fff0a0', 1); px.line(P, x, y, x - s.vx * 0.03, y - s.vy * 0.03, '#ffb040', 0.7, 1); };
  const drawShell = (P, x, y, s) => { const px = G.px; px.rect(P, x - 2, y - 2, 4, 4, '#3a3a30', 1); px.rect(P, x - 1, y - 1, 2, 2, '#e0c060', 1); px.line(P, x, y, x - s.vx * 0.05, y - s.vy * 0.05, '#c0b090', 0.5, 2); };
  const drawMissile = (P, x, y, s) => {
    const px = G.px, sp = Math.hypot(s.vx, s.vy) || 1, ux = s.vx / sp, uy = s.vy / sp;
    px.line(P, x - ux * 5, y - uy * 5, x + ux * 2, y + uy * 2, '#d8dccc', 1, 2);
    px.rect(P, Math.round(x + ux * 2) - 1, Math.round(y + uy * 2) - 1, 2, 2, '#e04030', 1);
    for (let i = 1; i <= 3; i++) px.rect(P, Math.round(x - ux * (5 + i * 3)), Math.round(y - uy * (5 + i * 3)), 2, 2, i === 1 ? '#ffb040' : '#a0a098', 0.8 - i * 0.2);
  };
  const BULLET = { kind: 'bc', r: 1, dmg: 2, push: 2, speed: 170, life: 3, hitR: [4, 5, 22], guard: 'normal', sfxHit: 'punch', fxHit: 'light', accent: '#ffe080', draw: drawBullet };
  M.BC_VOLLEY = {
    slot: 'enemy', body: 'aim', stand: null, warn: { tier: 'W3', dur: 0.5 }, dur: 0.6, active: [0, f(2)], melee: false,
    fireAt: [0.02], shot: BULLET, shotMod: (a) => shotAt(a, a.mem.tgt, 170), fireSfx: { name: 'gunshot', vol: 0.25, rate: 1.6 },
  };
  // 贴地扫射（段 2 ①）：贴着地面飞（z 低，按住 L 照样挡得住；跳不过去，只能 K 或挡）
  M.BC_SWEEP = Object.assign({}, M.BC_VOLLEY, { shotMod: (a) => ({ ang: a.facing < 0 ? Math.PI : 0, speed: 150 }) });
  M.BC_SHELL = {
    slot: 'enemy', body: 'aim', stand: null, warn: { tier: 'W3', dur: 0.6 }, dur: 0.8, active: [0, f(2)], melee: false,
    fireAt: [0.02], shot: { kind: 'bc', r: 2, dmg: 10, push: 16, speed: 130, life: 4, hitR: [5, 6, 24], guard: 'normal', sfxHit: 'explosion', fxHit: 'heavy',
      explodeFx: 0.6, accent: '#ffb040', draw: drawShell },
    shotMod: (a) => shotAt(a, a.mem.tgt, 130), fireSfx: { name: 'explosion', vol: 0.35, rate: 1.4 },
  };
  M.BC_MISSILE = {
    slot: 'enemy', body: 'aim', stand: null, warn: { tier: 'W3', dur: 0.5 }, dur: 0.7, active: [0, f(2)], melee: false,
    fireAt: [0.02], shot: { kind: 'bc', tag: 'missile', r: 2, dmg: 14, push: 18, speed: 62, homing: 1.1, life: 5, hitR: [5, 6, 26], guard: 'normal',
      sfxHit: 'explosion', fxHit: 'heavy', explodeFx: 0.7, accent: '#ff8040', draw: drawMissile, reflect: false },
    shotMod: (a) => shotAt(a, a.mem.tgt, 62), fireSfx: { name: 'whoosh', vol: 0.5, rate: 0.7 },
  };
  // 直升机点射（段 2 ②）：快、准，打中手臂 → J 伤害 −30% 5 s
  M.BC_SNIPE = {
    slot: 'enemy', body: 'aim', stand: null, warn: { tier: 'W3', dur: 0.45 }, dur: 0.6, active: [0, f(2)], melee: false,
    fireAt: [0.02], shot: Object.assign({}, BULLET, { dmg: 5, speed: 220, tag: 'snipe' }), shotMod: (a) => shotAt(a, player(), 220),
    fireSfx: { name: 'gunshot', vol: 0.35, rate: 1.3 },
  };
  // 一个兵的 brain：走到自己的位置（mem.home），开火由战斗 tick 统一下令（mem.order = 招式 id）
  const unitBrain = (e, dt) => {
    const m = e.mem, p = player();
    if (!p) return true;
    if (e.state !== 'idle' && e.state !== 'walk') return true;
    if (e.fly) e.z = e.fly.z + Math.round(Math.sin(G.clk.world * 3 + e.uid) * 2);
    const h = m.home;
    if (h && Math.hypot(h[0] - e.x, h[1] - e.y) > 2) G.combat.walkTo(e, h[0], h[1], dt, e.speed);
    else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
    const tg = m.tgt || p;
    e.facing = tg.x > e.x ? 1 : -1;
    if (m.order) { const id = m.order; m.order = null; G.AI.tele(e, id, { target: tg }); }
    return true;
  };
  K.e_bc_soldier = { hp: 6, speed: 34, moves: [], koStyle: 'fly', idle: 'idle', brain: unitBrain };
  K.e_bc_tank = { hp: 40, speed: 22, moves: [], koStyle: 'fly', idle: 'idle', armor: true, brain: unitBrain };
  K.e_bc_heli = { hp: 30, speed: 30, moves: [], koStyle: 'fly', idle: 'idle', fly: { z: 22 }, brain: unitBrain };
  K.e_keicho = { hp: 500, speed: 0, moves: [], koStyle: 'none', idle: 'point', brain: (e) => { const p = player(); if (p) e.facing = p.x > e.x ? 1 : -1; return true; } };
  let uN = 0;
  const unit = (kind, x, y, home, o = {}) => Object.assign({
    kit: 'e_bc_' + kind, cid: 'badco_' + kind, id: 'bc_' + kind + '_' + (++uN), name: { soldier: '步兵', tank: '坦克', heli: '直升机' }[kind],
    x, y, z: kind === 'heli' ? 22 : 0, hp: { soldier: 6, tank: 40, heli: 30 }[kind], koStyle: 'fly', mem0: { home },
  }, o);
  // 一排排的步兵：cols 列 × rows 排，从 x0 往右，每列间隔 12，每排间隔 6
  function formation(x0, y0, cols, rows, o = {}) {
    const out = [];
    for (let r = 0; r < rows; r++) for (let cI = 0; cI < cols; cI++) {
      const hx = x0 + cI * 12 + (r % 2) * 6, hy = y0 + r * 6;
      out.push(unit('soldier', hx + 120, hy, [hx, hy], o));
    }
    return out;
  }
  function armHomes(spawned) {
    for (const a of spawned) {
      const sp = a._enemySpec || {};
      if (sp.mem0) a.mem.home = sp.mem0.home;
      if (a.fly) a.z = a.fly.z;
    }
  }
  const units = (c) => c.enemies().filter((a) => !a.dead && a.cid && a.cid.indexOf('badco_') === 0);
  // 开火的调度：每 gap 秒挑一批（步兵一排 / 坦克一辆 / 直升机一架）开火，目标一半是仗助、一半是康一（vip 时）
  function volleyTick(S, c, dt, o) {
    const d = c.data;
    d.vT = (d.vT == null ? 1.2 : d.vT) - dt;
    if (d.vT > 0) return;
    const all = units(c).filter((a) => a.state === 'idle' || a.state === 'walk');
    if (!all.length) { d.vT = 0.5; return; }
    const ko = o.vip ? S.actor('koichi') : null;
    const pick = all[Math.floor(Math.random() * all.length)];
    const kind = pick.cid.replace('badco_', '');
    let group = [pick];
    if (kind === 'soldier') {
      // 同一排（y 差 3 以内）的一起开火
      group = all.filter((a) => a.cid === 'badco_soldier' && Math.abs(a.y - pick.y) <= 3).slice(0, 6);
    }
    const tgt = ko && Math.random() < 0.5 ? ko : player();
    for (const a of group) {
      a.mem.tgt = tgt;
      a.mem.order = kind === 'soldier' ? (o.sweep ? 'BC_SWEEP' : 'BC_VOLLEY') : kind === 'tank' ? 'BC_SHELL' : (o.snipe ? 'BC_SNIPE' : 'BC_MISSILE');
      if (kind === 'soldier') S.fx('glint', { x: a.x + a.facing * 5, y: a.y - 6, size: 4 }, { life: 0.3 });
    }
    d.vT = (o.gap || 1.6) * (kind === 'soldier' ? 1 : 1.2) * (0.8 + Math.random() * 0.4);
  }
  // 导弹被 J 打下来：碎在地上（段 1 只是一点碎片特效；段 2 留下可以修的碎片）
  function swatMissiles(S, c, onDown) {
    const p = player(), at = p && p.atk;
    if (!at || p.atkT < at.active[0] || p.atkT > at.active[1] + f(2)) return;
    for (const s of G.world.shots) {
      if (s.dead || s.tag !== 'missile' || s.side !== 'enemy') continue;
      const dx = (s.x - p.x) * p.facing;
      if (dx >= -6 && dx <= 44 && Math.abs(s.y - p.y) <= 14 && s.z <= 44) {
        s.dead = true;
        S.sfx('metal_crunch', 0.8);
        S.sfxText('咔', { wx: s.x, wy: s.y, wz: s.z }, { dur: 0.5 });
        S.fx('burst', { x: s.x, y: s.y - s.z, n: 8, speed: 26, colours: ['#d8dccc', '#7a8a4a'], gravity: 160, life: 0.5 });
        if (onDown) onDown(s.x, G.clamp(s.y, 142, 176));
      }
    }
  }
  // 地雷：地上一闪一闪的小点；踩到 12；J3 / 终结砸在旁边 40 px 内连锁引爆（炸到的兵也死）
  function mineTick(S, c, dt) {
    const d = c.data, p = player();
    if (!d.mines || !p) return;
    const boom = (mn) => {
      if (mn.gone) return;
      mn.gone = true;
      S.fx('explosion', { x: mn.x, y: mn.y - 4, size: 0.5 }, { life: 0.4 });
      S.sfx('explosion', 0.4);
      for (const a of units(c)) if (Math.hypot(a.x - mn.x, (a.y - mn.y) * 1.5) < 26) G.combat.hit(p, a, { slot: 'J3', dmg: 99, push: 30, guard: 'none', sfxHit: 'thud' });
      for (const m2 of d.mines) if (!m2.gone && Math.hypot(m2.x - mn.x, m2.y - mn.y) < 40) G.defer(0.12, () => boom(m2));
    };
    const at = p.atk, heavy = at && (at.slot === 'J3' || at.slot === 'fin') && p.atkT >= at.active[0] && p.atkT <= at.active[1];
    for (const mn of d.mines) {
      if (mn.gone) continue;
      if (heavy && at !== d.mineAtk && Math.hypot(mn.x - (p.x + p.facing * 16), (mn.y - p.y) * 1.5) < 40) { d.mineAtk = at; d.chains = (d.chains || 0) + 1; boom(mn); continue; }
      if (p.iframe <= 0 && p.invuln <= 0 && Math.abs(p.x - mn.x) < 6 && Math.abs(p.y - mn.y) < 5) {
        boom(mn);
        G.combat.hit(null, p, { slot: 'enemy', dmg: 12, push: 20, guard: 'none', sfxHit: 'explosion', fxHit: 'heavy' });
      }
    }
    d.mines = d.mines.filter((m) => !m.gone);
  }
  function placeMines(c, n, x0, x1) {
    const d = c.data;
    d.mines = d.mines || [];
    for (let i = 0; i < n; i++) d.mines.push({ x: Math.round(x0 + (x1 - x0) * (i + 0.5) / n + (Math.random() * 16 - 8)), y: Math.round(146 + Math.random() * 28) });
  }
  // 地雷、碎片、“手臂中弹”的小图标画在 UI 层
  let fx2H = null;
  function bcOverlay(getCtx) {
    return P4().overlay((g) => {
      const c = getCtx();
      if (!c || G.world.fight !== c || G.world.insert) return;
      const d = c.data, t = clk();
      for (const mn of d.mines || []) {
        const q = w2u(mn.x, mn.y);
        g.fillStyle = '#2a2a24'; g.fillRect(Math.round(q.x) - 3, Math.round(q.y) - 1, 6, 3);
        if (Math.floor(t * 4 + mn.x) % 2) { g.fillStyle = '#ff3030'; g.fillRect(Math.round(q.x) - 1, Math.round(q.y) - 2, 2, 2); }
      }
      if (d.armT > 0) {
        const p = player();
        if (p) { const q = w2u(p.x, p.headY() - 6); P4().text(g, '手臂中弹', Math.round(q.x), Math.round(q.y) - 16, '#ff9a80', 12, 'center'); }
      }
      for (const db of d.debris || []) {
        if (db.gone) continue;
        const q = w2u(db.x, db.y);
        if (Math.floor(t * 3) % 2) { g.fillStyle = 'rgba(255,224,112,0.55)'; g.fillRect(Math.round(q.x) - 8, Math.round(q.y) + 2, 16, 2); }
      }
      for (const rm of d.rain || []) {
        if (rm.done) continue;
        const q = w2u(rm.x, rm.y), k = Math.min(1, rm.t / rm.warn);
        g.save(); g.globalAlpha = Math.floor(t * 12) % 2 ? 0.85 : 0.45;
        g.strokeStyle = '#ff3030'; g.lineWidth = 2;
        g.beginPath(); g.ellipse(Math.round(q.x), Math.round(q.y), 16, 6, 0, 0, Math.PI * 2); g.stroke();
        g.restore();
        // 导弹从天上掉下来
        const top = w2u(rm.x, rm.y, 120 * (1 - k));
        g.fillStyle = '#d8dccc'; g.fillRect(Math.round(top.x) - 1, Math.round(top.y) - 8, 3, 8);
        g.fillStyle = '#ffb040'; g.fillRect(Math.round(top.x) - 1, Math.round(top.y) - 11, 3, 3);
      }
    }, { z: -1 });
  }

  // =====================================================================================================================
  // 第 2 战 段 1 走廊（b02_badcompany_a）：护住康一（vip），三波
  // =====================================================================================================================
  const H1 = { arena: [30, 620], ko: [64, 156], jo: [96, 158] };
  let F2a = null;
  R.fightCompanyA = async function (S) {
    S.hint(null);
    uN = 0;
    const res = await S.fight({
      id: 'b02_badcompany_a', arena: H1.arena, lead: 'josuke', swap: false, lockMsg: '康一动不了：只能仗助挡在前面',
      music: 'battle', after: null, dmgScale: 0.9, losable: true, energy: { start: 0 }, vip: 'koichi', vipHp: 60,
      waves: [
        formation(380, 146, 5, 4),
        formation(400, 148, 5, 2),
        [unit('tank', 560, 150, [470, 150]), unit('tank', 580, 162, [500, 164]), unit('tank', 600, 172, [440, 174]),
          unit('heli', 600, 146, [420, 148]), unit('heli', 620, 166, [520, 166])],
      ],
      testHint: (ctx) => {
        const ko = G.S.actor('koichi'), d = ctx.data;
        return { wave: ctx.wave, left: units(ctx).length, koHp: ko ? ko.hp : null, mines: (d.mines || []).length, chains: d.chains || 0 };
      },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        F2a = ctx;
        armHomes(spawned);
        const ko = S2.actor('koichi'), p = player();
        if (wi === 0) {
          if (ko) { Object.assign(ko, { x: H1.ko[0], y: H1.ko[1], facing: 1 }); S2.pose(ko, 'down'); }
          p.x = H1.jo[0]; p.y = H1.jo[1]; p.facing = 1;
          if (fx2H) fx2H.close();
          fx2H = bcOverlay(() => F2a);
          S2.hint('康一躺在你身后：站在他前面按住 L，子弹就打不到他。小兵一拳一个', 8);
        } else if (wi === 1) {
          placeMines(ctx, 8, 160, 460);
          await S2.say('keicho', '地雷。……踩一脚试试？', { name: '形兆' });
          S2.hint('地上闪红点的是地雷：别踩。在它旁边打出 J3（第三下），会连着一起炸掉', 8);
        } else {
          ctx.data.mines = [];
          await S2.say('keicho', '坦克、直升机，上。', { name: '形兆' });
          S2.hint('导弹会追着人飞：在它飞到面前时按 J 把它打下来', 7);
        }
        ctx.data.vT = 1.4;
      },
      tick: (c, dt) => { volleyTick(S, c, dt, { vip: true, gap: c.wave === 0 ? 1.3 : 1.7 }); mineTick(S, c, dt); swatMissiles(S, c, null); },
    });
    if (fx2H) { fx2H.close(); fx2H = null; }
    clearUnits();
    const ko = S.actor('koichi');
    if (ko) S.unpose(ko);
    F2a = null;
    S.mark('ch1_wave_clear');
    return res;
  };
  function clearUnits() {
    for (const a of G.world.stage.actors) if (a.cid && a.cid.indexOf('badco_') === 0) a.remove = true;
    G.world.shots = [];
  }

  // =====================================================================================================================
  // 第 2 战 段 2 楼梯（b02_badcompany_b）：形兆在二楼平台（打不到），三阶段 → 修导弹碎片让导弹飞回去
  // =====================================================================================================================
  const H2 = { arena: [20, 470], kc: [400, 80], jo: [250, 160], ko: [214, 162] };
  const PH = [20, 40];               // 阶段 ② 从 20 s 开始，③ 从 40 s 开始
  let F2b = null;
  function phaseOf(c) { return c.t < PH[0] ? 1 : c.t < PH[1] ? 2 : 3; }
  function stairsTick(S, c, dt) {
    const d = c.data, p = player(), kc = S.actor('keicho');
    if (!p || !kc) return;
    const ph = phaseOf(c);
    if (d.ph !== ph) {
      d.ph = ph;
      cine(c, () => phaseCue(S, c, ph)).catch(G.cancelIgnore);
      return;
    }
    // 援军：每阶段补兵，场上保持一定数量
    d.reT = (d.reT || 0) - dt;
    if (d.reT <= 0) {
      d.reT = ph === 3 ? 4 : 5;
      const alive = units(c);
      const want = ph === 1 ? 8 : ph === 2 ? 4 : 8;
      const sol = alive.filter((a) => a.cid === 'badco_soldier').length;
      for (let i = sol; i < want; i++) c.spawn((unit('soldier', 470, 146 + Math.round(Math.random() * 28), [330 + Math.round(Math.random() * 120), 146 + Math.round(Math.random() * 28)])));
      if (ph === 2 && alive.filter((a) => a.cid === 'badco_heli').length < 2) c.spawn((unit('heli', 470, 150, [300 + Math.round(Math.random() * 140), 150 + Math.round(Math.random() * 20)])));
      if (ph === 3 && alive.filter((a) => a.cid === 'badco_tank').length < 2) c.spawn((unit('tank', 470, 160, [380 + Math.round(Math.random() * 60), 150 + Math.round(Math.random() * 24)])));
    }
    volleyTick(S, c, dt, { sweep: ph === 1, snipe: ph === 2, gap: ph === 3 ? 1.3 : 1.6 });
    mineTick(S, c, dt);
    // ② 手臂中弹：J 伤害 −30% 5 s
    if (d.armT > 0) { d.armT -= dt; if (d.armT <= 0) p.dmgOut = 1; }
    // ③ 导弹雨：每 2.5 s 一发，落点红圈 0.7 s；落地留碎片（最多 6 个）
    if (ph === 3) {
      d.rainT = (d.rainT == null ? 0.8 : d.rainT) - dt;
      if (d.rainT <= 0) {
        d.rainT = 2.5;
        const x = G.clamp(p.x + (Math.random() * 120 - 60), H2.arena[0] + 20, H2.arena[1] - 20), y = G.clamp(p.y + Math.round(Math.random() * 20 - 10), 146, 174);
        (d.rain = d.rain || []).push({ x, y, t: 0, warn: 0.7 });
      }
      for (const rm of d.rain || []) {
        if (rm.done) continue;
        rm.t += dt;
        if (rm.t >= rm.warn) {
          rm.done = true;
          S.fx('explosion', { x: rm.x, y: rm.y - 6, size: 0.8 }, { life: 0.45 });
          S.sfx('explosion', 0.6); S.shake(2, 0.2);
          if (p.iframe <= 0 && p.invuln <= 0 && Math.pow((p.x - rm.x) / 18, 2) + Math.pow((p.y - rm.y) / 8, 2) <= 1)
            G.combat.hit(null, p, { slot: 'enemy', dmg: 14, push: 20, guard: 'none', sfxHit: 'explosion', fxHit: 'heavy' });
          addDebris(S, c, rm.x, rm.y);
        }
      }
      d.rain = (d.rain || []).filter((r) => !r.done);
      // 卡住 40 s 没修过一枚：康一提醒
      d.stuck = (d.stuck || 0) + dt;
      if (!d.fixedN && d.stuck > 40 && !d.koTold) {
        d.koTold = true;
        cine(c, async () => {
          await S.say('koichi', '仗助君，地上的碎片！……你的替身，不是能把东西修好吗？', { expr: 'shock' });
          S.hint('站到导弹碎片旁边，按住 L 按 J：修好的导弹会按原路飞回去', 8);
        });
      }
    }
    swatMissiles(S, c, (x, y) => { if (ph === 3) addDebris(S, c, x, y); });
    // 修碎片：碎片 20 px 内按住 L 按 J → 导弹飞回去打形兆
    if (fixPress(d, p)) {
      const db = (d.debris || []).filter((q) => !q.gone).sort((a, b) => Math.hypot(a.x - p.x, a.y - p.y) - Math.hypot(b.x - p.x, b.y - p.y))[0];
      if (db && Math.abs(db.x - p.x) <= 22 && Math.abs(db.y - p.y) <= 12) fixDebris(S, c, db);
    }
    G.hud.boss = kc;
  }
  function addDebris(S, c, x, y) {
    const d = c.data;
    d.debris = (d.debris || []).filter((q) => !q.gone);
    if (d.debris.length >= 6) return;
    const a = T().prop(S, 'missile_debris', x, y, { id: 'ch1_debris' + (d.dbN = (d.dbN || 0) + 1), frame: 0 });
    if (a) { a.hold = false; a.frozen = null; }
    d.debris.push({ x, y, a, gone: false });
    if (!d.debrisTold) { d.debrisTold = true; S.hint('导弹的碎片留在地上了……', 3); }
  }
  function fixDebris(S, c, db) {
    const d = c.data, p = player(), kc = S.actor('keicho');
    db.gone = true;
    if (db.a) db.a.remove = true;
    d.fixedN = (d.fixedN || 0) + 1;
    S.standAct(p, 'reach', { dx: 16, z: 4, dur: 0.6 });
    P4().fixGlow(S, db.x, db.y - 4);
    if (d.fixedN === 1) S.mark('ch1_debris_fixed');
    // 修好的导弹沿弧线飞回二楼平台
    const x0 = db.x, y0 = db.y, run = G.runId;
    const ms = { x: x0, y: y0, z: 4, vx: 0, vy: 0 };
    const h = P4().overlay((g) => {
      if (run !== G.runId) return;
      const q = w2u(ms.x, ms.y, ms.z);
      g.fillStyle = '#d8dccc'; g.fillRect(Math.round(q.x) - 4, Math.round(q.y) - 1, 8, 3);
      g.fillStyle = '#e04030'; g.fillRect(Math.round(q.x) + (ms.vx > 0 ? 4 : -6), Math.round(q.y) - 1, 2, 3);
      g.fillStyle = '#ffb040'; g.fillRect(Math.round(q.x) + (ms.vx > 0 ? -7 : 5), Math.round(q.y), 3, 2);
    }, { z: 2 });
    S.sfx('whoosh', 0.8);
    S.animate(0.8, (k) => {
      const nx = G.lerp(x0, kc.x, k), ny = G.lerp(y0, kc.y + 60, k), nz = 4 + 70 * k * k + 30 * Math.sin(Math.PI * k);
      ms.vx = nx - ms.x; ms.x = nx; ms.y = ny; ms.z = nz;
    }).then(() => {
      h.close();
      if (run !== G.runId || G.world.fight !== c) return;
      kc.hp = Math.max(0, kc.hp - 120);
      kc.flash = 1;
      S.fx('explosion', { x: kc.x, y: kc.y - 16, size: 1.1 }, { life: 0.5 });
      S.sfx('explosion', 1); S.shake(5, 0.35);
      S.sfxText('轰！', kc, { dur: 0.8 });
      if (kc.hp <= 0) d.done = true;
      else S.emote(kc, ['……什么？！', '我的导弹……！', '不可能……'][Math.min(2, d.fixedN - 1)], 1.0);
    }, () => h.close());
  }
  // 段 2 的援军是中途 c.spawn 的：mem.home 由战斗 tick 从 _enemySpec.mem0 补上（onWave 只处理第一批）
  async function phaseCue(S, c, ph) {
    if (ph === 1) return;
    if (ph === 2) {
      await S.say('keicho', '腿打完了。……接下来是手。', { name: '形兆' });
      S.hint('直升机在点射：被打中手臂，J 的伤害会变低（5 秒）。躲开或者挡住', 7);
    } else {
      await S.say('keicho', '最后是头。全军，突击！', { name: '形兆', expr: 'rage' });
      S.hint('导弹雨！看地上的红圈躲开。落下来的导弹会留下碎片……', 7);
    }
  }
  R.fightCompanyB = async function (S) {
    S.hint(null);
    uN = 100;
    const res = await S.fight({
      id: 'b02_badcompany_b', arena: H2.arena, lead: 'josuke', swap: false, lockMsg: '康一躲在仗助身后',
      music: 'battle', after: null, dmgScale: 0.9, losable: true, energy: { start: 0 },
      waves: [[
        { kit: 'e_keicho', actor: 'keicho', cid: 'keicho', id: 'keicho', name: '虹村形兆', x: H2.kc[0], y: H2.kc[1], boss: true, hp: 500, minHp: 0, untargetable: true, koStyle: 'none' },
        ...formation(330, 150, 4, 2),
      ]],
      testHint: (ctx) => {
        const kc = G.S.actor('keicho'), d = ctx.data;
        return { ph: d.ph || 1, kcHp: kc ? kc.hp : null, debris: (d.debris || []).filter((q) => !q.gone).length, fixed: d.fixedN || 0, units: units(ctx).length };
      },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        F2b = ctx;
        armHomes(spawned);
        const kc = S2.actor('keicho'), p = player();
        if (kc) { kc.play('point'); kc.shadow = false; }
        p.x = H2.jo[0]; p.y = H2.jo[1]; p.facing = 1;
        ctx.data.lastAtkPress = G.input.lastPress('attack');
        ctx.data.ph = 1;
        placeMines(ctx, 6, 170, 420);
        onSnipeHit(ctx);
        if (fx2H) fx2H.close();
        fx2H = bcOverlay(() => F2b);
        S2.hint('形兆在二楼平台上，打不到他。先撑过他的“腿、手、头”三轮进攻', 8);
      },
      tick: (c, dt) => {
        // 中途补的兵：把 mem.home 补上
        for (const a of c.enemies()) if (a._enemySpec && a._enemySpec.mem0 && !a.mem.home) a.mem.home = a._enemySpec.mem0.home;
        stairsTick(S, c, dt);
      },
      // 形兆是“打不到的 boss”：敌人清空也不算赢，只看导弹把他打到 0
      endWhen: (c) => !!c.data.done,
    });
    if (fx2H) { fx2H.close(); fx2H = null; }
    const p = player();
    if (p) p.dmgOut = 1;
    clearUnits();
    for (const a of G.world.stage.actors) if (a.id && a.id.indexOf('ch1_debris') === 0) a.remove = true;
    F2b = null;
    return res;
  };
  // 直升机点射打中：手臂中弹（看子弹 tag）
  function onSnipeHit(c) {
    c.on('hurt', (e) => {
      if (!e || !e.move || e.move.tag !== 'snipe') return;
      const p = player();
      c.data.armT = 5; p.dmgOut = 0.7;
    });
  }
})();
