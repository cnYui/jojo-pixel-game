// 第4章　杜王港 / 辣妹与透明宝宝：第 6 战三段（开发脚本 第四部/docs/第4章_开发脚本.md §3）。剧情节拍在 story/p4_ch4.js。
//   段 A 空地（亿泰追电瓶摩托：按住 L 按 J 拉近 3 次 → 打坏摩托 → J3 削地面）
//   段 B 码头（仗助：辣妹在地下钻来钻去，康一报方位；J3 碎地 + 修成黏地卡住它；叉车轮胎夹住它崩进海里）
//   段 C SPW 的船（亿泰：60 s 充电槽；E 盘问船员、L+J 削掉帽子看手指；辣妹扑乔瑟夫时 QTE 拉过来；音石明 HP 300）
//   亿泰的招式组 K.okuyasu 归第2章（engine/p4_moves.js）：按住 L 按 J 拉近照用（段 A 摩托挂 onPulled 计数）；段 C 削帽子在这里自己判。
//   战斗里要停下来演的地方用 cine()（照序章 p4_pro_fights.js）。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const R = (G.P4CH4 = {});
  const player = () => G.world.player;
  const OKU = () => 'okuyasu';
  R.OKU = OKU;

  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-fight' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  // 按住 L 按 J（仗助的“修”）：上一帧以后又按了 J、而且正按着 L 在格挡
  function guardJ(d, p) {
    const lp = G.input.lastPress('attack');
    if (lp === d.lastAtkPress) return false;
    d.lastAtkPress = lp;
    return !!p && (p.state === 'guard' || (p.atk && p.atk.slot === 'guardAttack'));
  }
  // 轰炸空间削过的黑缝（第2章 engine/p4_moves.js 注册的 erase_seam；没有就退回冲击圈）
  function seam(S, x, y, h = 30) {
    if (G.FX && G.FX.erase_seam) S.fx('erase_seam', { x, y, h, dur: 0.8 }, { life: 0.8 });
    else S.fx('shockwave', { x, y: y - 16, r_max: 20, dur: 0.3, colour: '#8cb6ff' }, { life: 0.3 });
  }

  // 乔瑟夫（79 岁）：只在自由走动里当队长（U 念写）；走得慢
  K.joseph_old = K.joseph_old || Object.assign({}, K.joseph, { hp: 100, speed: 44, standId: 'hermit' });

  // ======================================================================= 辣妹的电量（头顶一条小槽）
  let chargeH = null;
  function chargeBar(getE, getV) {
    if (chargeH) chargeH.close();
    chargeH = P4().overlay((g) => {
      const e = getE();
      if (!e || e.remove || e.visible === false || (e.alpha != null && e.alpha < 0.3) || !G.cam || !G.cam.w2u || G.world.insert) return;
      const v = G.clamp(getV() || 0, 0, 100);
      const p = G.cam.w2u(e.x, e.headY() - 4, 0);
      const w = 34, x = Math.round(p.x - w / 2), y = Math.round(p.y - 14);
      g.fillStyle = '#1a1020'; g.fillRect(x - 1, y - 1, w + 2, 6);
      g.fillStyle = '#3a3428'; g.fillRect(x, y, w, 4);
      g.fillStyle = v >= 70 ? '#fff060' : v >= 40 ? '#ffd040' : '#c08a30';
      g.fillRect(x, y, Math.round(w * v / 100), 4);
      P4().text(g, '电' + Math.round(v) + '%', x + w + 4, y - 5, '#ffe070', 12, 'left');
    }, { z: 2 });
    return chargeH;
  }
  R.closeCharge = () => { if (chargeH) { chargeH.close(); chargeH = null; } };
  // 电光（辣妹身上 / 电线里）
  function zap(S, x0, y0, x1, y1, life = 0.25) {
    S.fx('lightning', { x0, y0, x1, y1, colour: '#fff8c0', glow_colour: '#ffd040', branches: 2 }, { life });
  }
  R.zap = zap;

  // ======================================================================= 辣妹的招式
  // 往后甩的小电弧（段 A）：W1 0.5 s，身前 90 px
  M.RH_ZAP = {
    slot: 'enemy', body: 'punch', stand: null, warn: { tier: 'W1', dur: 0.5 }, dur: 0.5 + 0.35, active: [0.5, 0.62], from: 'body', reach: [0, 90], depth: 14,
    dmg: 6, push: 8, guard: 'normal', sfx: 'thunder', sfxVol: 0.4, sfxHit: 'punch', fxHit: 'light', accent: '#ffe060',
    onStart: (a) => { zap(G.S, a.x, a.y - 14, a.x + a.facing * 86, a.y - 10, 0.3); },
  };
  // 钻出来直接扑（段 B）：W4 红线 0.5 s，伤害 12
  const dashPath = (e) => {
    const p = G.world.player;
    if (!p) return [[e.x, e.y], [e.x + e.facing * 120, e.y]];
    const dx = p.x - e.x, dy = p.y - e.y, d = Math.hypot(dx, dy) || 1;
    return [[e.x, e.y], [p.x + dx / d * 24, p.y + dy / d * 14]];
  };
  M.RH_DASH = {
    slot: 'enemy', body: 'dash', warn: { tier: 'W4', dur: 0.5, path: dashPath }, dur: 0.5 + 0.45, active: [0.5, 0.8], melee: false,
    dash: { dist: 150, time: 0.3, w: 8, line: true }, dmg: 12, push: 14, guard: 'normal', sfx: 'whoosh', sfxHit: 'punch_heavy', fxHit: 'heavy', accent: '#ffd040',
  };
  M.RH_DASH_FAST = Object.assign({}, M.RH_DASH, { warn: { tier: 'W4', dur: 0.4, path: dashPath }, dur: 0.4 + 0.45, active: [0.4, 0.7] });
  // 地面上的快拳：W1 0.35 s，伤害 8
  M.RH_PUNCH = {
    slot: 'enemy', body: 'punch', warn: { tier: 'W1', dur: 0.35 }, dur: 0.35 + f(20), active: [0.35, 0.35 + f(6)], from: 'body', reach: [4, 36], depth: 10,
    dmg: 8, push: 8, guard: 'normal', sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light', accent: '#ffd040',
  };
  M.RH_PUNCH_FAST = Object.assign({}, M.RH_PUNCH, { warn: { tier: 'W1', dur: 0.25 }, dur: 0.25 + f(20), active: [0.25, 0.25 + f(6)] });
  // 音石明：吉他抡砸（W1 0.45 s，10）、余电电击（W4 0.5 s，8，身前 140 px 一条线）
  M.OT_GUITAR = {
    slot: 'enemy', body: 'guitar', warn: { tier: 'W1', dur: 0.45 }, dur: 0.45 + f(22), active: [0.45, 0.45 + f(6)], from: 'body', reach: [4, 40], depth: 10,
    dmg: 10, push: 14, guard: 'normal', sfx: 'whoosh', sfxHit: 'baseball_hit', fxHit: 'heavy', accent: '#ffffff',
  };
  M.OT_SHOCK = {
    slot: 'enemy', body: 'guitar', warn: { tier: 'W4', dur: 0.5 }, dur: 0.5 + 0.35, active: [0.5, 0.65], from: 'body', reach: [0, 140], depth: 9,
    dmg: 8, push: 10, guard: 'normal', sfx: 'thunder', sfxVol: 0.5, sfxHit: 'punch', fxHit: 'light', accent: '#ffe060',
    onStart: (a) => { zap(G.S, a.x + a.facing * 6, a.y - 16, a.x + a.facing * 140, a.y - 4, 0.35); },
  };

  // ======================================================================= 段 A：空地（b06a_rhcp）
  const FA = { arena: [20, 630], oku: [200, 154], bike: [300, 152], stop: 600, box: [447, 162] };
  K.e_rhcp_bike = {
    hp: 120, speed: 30, moves: ['RH_ZAP'], koStyle: 'none', idle: 'idle', armor: true,
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player;
      if (!p || m.hold) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      e.play('idle');
      if (d.bikeDown) return true;
      if (d.pulls >= 3) { e.facing = p.x > e.x ? 1 : -1; return true; }     // 没电了：停着不动
      // 往右逃（到 600 停下挑衅）
      if (e.x < FA.stop) { G.combat.walkTo(e, FA.stop, e.y, dt, 30); e.play('idle'); }
      e.facing = -1;
      m.gap = (m.gap == null ? 2.2 : m.gap) - dt;
      if (m.gap <= 0 && Math.abs(p.x - e.x) < 100 && Math.abs(p.y - e.y) < 14) { G.AI.tele(e, 'RH_ZAP'); m.gap = 3; }
      if (e.x >= FA.stop - 1 && !m.taunted) { m.taunted = true; G.S.emote(e, '来追我呀～', 1.4, '#ffe070'); }
      return true;
    },
  };
  function bikeSetup(S, ctx) {
    const d = ctx.data, e = S.actor('rhcp_bike');
    d.pulls = 0; d.charge = 30;
    const old = S.actor('ebike_a');
    if (old) old.remove = true;
    const bike = T().prop(S, 'ebike', e.x, e.y + 0.5, { id: 'ebike_a', frame: 1 });
    d.bikeProp = bike;
    e.z = 8; e.dmgMul = () => (d.pulls >= 3 ? 1 : 0);
    T().tick(() => {
      if (!bike || bike.remove) return true;
      if (d.bikeDown) return true;
      const a = S.actor('rhcp_bike');
      if (!a) return false;
      bike.x = a.x; bike.y = a.y + 0.5; bike.facing = a.facing;
      return false;
    });
    chargeBar(() => S.actor('rhcp_bike'), () => d.charge);
    // 亿泰按住 L 按 J 拉近（第2章的 TH_PULL：面前 120 px 内最近的敌人）：拉到一次记一次
    e.onPulled = (a) => {
      const b = e;
      if (d.bikeDown || d.pulls >= 3) return;
      b.atk = null; b.tele = null;
      S.sfx('pop', 0.8);
      d.pulls++;
      ctx.step(d.pulls);
      S.sfxText(d.pulls + '/3', a, { dur: 0.7 });
      if (d.pulls >= 3) {
        S.mark('b06a_pull3');
        T().setFrame(bike, 0);
        d.charge = 5;
        S.emote(b, '啊？没电了？', 1.4, '#ffe070');
        S.hint('电瓶没电了！把摩托打坏（HP 120）', 6);
      }
    };
    d.lastAtkPress = G.input.lastPress('attack');
    S.hint('面朝摩托，按住 L 再按 J：轰炸空间削掉中间的空间，把摩托拉过来（120 px 以内）', 8);
  }
  function bikeTick(S, c, dt) {
    const d = c.data, p = player(), e = S.actor('rhcp_bike');
    if (!p || !e) return;
    if (!d.bikeDown && d.pulls >= 3 && e.hp <= 1) {
      d.bikeDown = true;
      cine(c, async () => {
        const bike = d.bikeProp;
        T().setFrame(bike, 2);
        S.sfx('metal_crunch', 0.9); S.sfx('crash', 0.6);
        S.fx('burst', { x: e.x, y: e.y - 6, n: 12, speed: 40, colours: ['#c83a3a', '#5a5e6a', '#ffe060'], gravity: 160, life: 0.7 });
        S.shake(3, 0.3);
        S.mark('b06a_bike_down');
        e.untargetable = true;
        await S.arc(e, FA.box[0], FA.box[1], 30, 0.6, { anim: 'dash' });
        e.z = 0; e.facing = p.x < e.x ? -1 : 1; e.play('idle');
        zap(S, e.x, e.y - 4, e.x, e.y - 30, 0.4);
        await S.say('rhcp', '嘿嘿……这下面是什么，你知道吗？', { expr: 'smile' });
        S.hint('J3（连按三下 J）：削掉地面！', 10);
        d.tauntT = c.t;
        d.lastJ3 = null;
      });
    }
    if (d.tauntT != null && !d.cable) {
      const a = p.atk;
      if ((a && a.slot === 'J3' && p.atkT >= a.active[0]) || c.t - d.tauntT > 10) {
        d.cable = true;
        cine(c, async () => {
          if (!(a && a.slot === 'J3')) {
            S.face(p, 1);
            await S.summon(p, { dur: 0.1, rise: 4 });
            S.standAct(p, 'punch_heavy', { dx: 22, z: 2, dur: 0.6 });
          }
          S.sfx('whoosh', 1, 0.55); S.sfx('crash', 0.7);
          seam(S, 450, 162, 20);
          S.fx('crack', { x: 450, y: 160, size: 20 }, { life: 1.2 });
          S.shake(4, 0.4);
          S.state('cable', 1);
          await S.wait(0.4);
          zap(S, 450, 160, e.x, e.y - 20, 0.6);
          S.sfx('thunder', 0.8);
          S.flash(0.12, 0.6, '#fff8c0');
          d.charge = 100;
          await S.animate(0.35, (k) => { e.alpha = 1 - k; e.z = -8 * k; });
          S.mark('b06a_cable');
          c.end();
        });
      }
    }
  }
  R.fightA = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b06a_rhcp', arena: FA.arena, lead: OKU(), swap: false, lockMsg: '这一战只能由亿泰应战',
      music: 'battle', after: null, dmgScale: 0.9, playerMinHp: 1, losable: false, energy: { start: 0 }, coverage: false,
      steps: { n: 3, label: '拉近摩托' },
      waves: [[{ kit: 'e_rhcp_bike', cid: 'rhcp', id: 'rhcp_bike', name: '电瓶摩托', x: FA.bike[0], y: FA.bike[1], boss: true, hp: 120, minHp: 1 }]],
      testHint: (ctx) => { const e = G.S.actor('rhcp_bike'); return { pulls: ctx.data.pulls || 0, bikeHp: e ? e.hp : null, down: !!ctx.data.bikeDown, cable: !!ctx.data.cable }; },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const p = player();
        p.x = FA.oku[0]; p.y = FA.oku[1]; p.facing = 1;
        S2.mark('b06a_start');
        bikeSetup(S2, ctx);
      },
      tick: (c, dt) => bikeTick(S, c, dt),
      endWhen: (c) => !!c.data.cable && !G.world.cine,
    });
    R.closeCharge();
    const e = S.actor('rhcp_bike');
    if (e) e.remove = true;
    return res;
  };

  // ======================================================================= 段 B：码头（b06b_rhcp）
  const HB = {
    arena: [24, 930],
    grates: [[96, 158], [232, 168], [372, 154], [520, 166], [688, 156], [836, 168]],
    lamps: [[151, 148], [411, 148], [701, 148], [901, 148]],
    forklift: [628, 150], tyre: [618, 150], sea: [720, 112],
  };
  K.e_rhcp = {
    hp: 900, speed: 70, moves: [], koStyle: 'none', idle: 'idle',
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player;
      if (!p || m.hold || d.final) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      const hi = (d.charge || 0) >= 70;
      m.ph = m.ph || 'under';
      m.t = (m.t == null ? 1.6 : m.t) - dt;
      if (m.ph === 'under') {
        if (!e.hidden) G.AI.hide(e, true, { alpha: 0 });
        if (m.t <= 0) { pickEmerge(e, d, p); m.ph = 'call'; m.t = 0.5; }
        return true;
      }
      if (m.ph === 'call') {
        if (m.t <= 0) {
          G.AI.hide(e, false);
          e.x = m.at[0]; e.y = m.at[1]; e.z = 0; e.alpha = 1;
          G.S.sfx('crash', 0.5);
          G.S.fx('burst', { x: e.x, y: e.y - 4, n: 8, speed: 30, colours: ['#8a8e96', '#ffe060'], gravity: 140, life: 0.5 });
          zap(G.S, e.x, e.y, e.x, e.y - 28, 0.3);
          if (m.lamp) zap(G.S, e.x, 48, e.x, e.y - 20, 0.4);
          m.ph = 'ground'; m.t = 3; m.n = 0; m.gap = 0.1;
          if (stuckAt(d, e.x, e.y)) {
            m.stuck = 2; e.dmgIn = 1.5; d.stuckN = (d.stuckN || 0) + 1;
            G.S.emote(e, '卡住了！', 1.6, '#ffe070'); G.S.sfx('slime', 0.8);
            G.S.mark('b06b_sticky');
            return true;
          }
          e.facing = p.x > e.x ? 1 : -1;
          G.AI.tele(e, hi ? 'RH_DASH_FAST' : 'RH_DASH');
        }
        return true;
      }
      // ground：卡住时不动；否则两拳，然后钻回地下
      if (m.stuck > 0) { m.stuck -= dt; e.play('hurt'); if (m.stuck <= 0) e.dmgIn = 1; return true; }
      e.play('idle');
      e.facing = p.x > e.x ? 1 : -1;
      const dx = Math.abs(p.x - e.x);
      if (dx > 30 || Math.abs(p.y - e.y) > 6) G.combat.walkTo(e, p.x - e.facing * 26, p.y, dt, e.speed * (hi ? 1.3 : 1));
      m.gap -= dt;
      if (m.gap <= 0 && m.n < 2 && dx < 44 && Math.abs(p.y - e.y) < 10) { G.AI.tele(e, hi ? 'RH_PUNCH_FAST' : 'RH_PUNCH'); m.n++; m.gap = 0.9; }
      if (m.t <= 0) {
        // 钻回最近的格栅
        G.S.fx('burst', { x: e.x, y: e.y - 4, n: 6, speed: 26, colours: ['#ffe060'], gravity: 80, life: 0.4 });
        G.AI.hide(e, true, { alpha: 0 });
        m.ph = 'under'; m.t = 1.4 + Math.random() * 0.8;
      }
      return true;
    },
  };
  function stuckAt(d, x, y) {
    return (d.stickies || []).some((s) => s.t > 0 && Math.abs(s.x - x) < 34 && Math.abs(s.y - y) < 16);
  }
  // 挑钻出来的地方：多半是离仗助最近的格栅；有时是路灯；喊方位
  function pickEmerge(e, d, p) {
    const m = e.mem;
    let at, lamp = false;
    const near = HB.grates.slice().sort((a, b) => Math.abs(a[0] - p.x) - Math.abs(b[0] - p.x));
    // 有黏地的格栅：它不知道，照样会从那里出来（离仗助最近的那个优先）
    if (Math.random() < 0.25) {
      const l = HB.lamps.slice().sort((a, b) => Math.abs(a[0] - p.x) - Math.abs(b[0] - p.x))[0];
      at = [l[0], G.clamp(p.y, 146, 174)]; lamp = true;
    } else at = Math.random() < 0.8 ? near[0] : near[1];
    if (Math.abs(at[0] - p.x) < 10 && !lamp) at = [at[0], at[1]];
    m.at = at; m.lamp = lamp;
    const ko = G.S.actor('koichi');
    const word = lamp ? '上面！' : Math.abs(at[0] - p.x) < 24 ? '脚下！' : at[0] < p.x ? '左边！' : '右边！';
    if (ko) G.S.emote(ko, word, 0.8, '#bfe8ff');
    d.call = { x: at[0], y: at[1], word, t0: G.clk.ui, lamp };
    G.S.sfx('blip', 0.5);
  }
  let callH = null;
  function callArrow() {
    if (callH) callH.close();
    callH = P4().overlay((g) => {
      const W = G.world, c = W.fight, p = W.player;
      if (!c || !c.data.call || !p || !G.cam || !G.cam.w2u || W.insert) return;
      const q = c.data.call, age = G.clk.ui - q.t0;
      if (age > 0.6) return;
      const pp = G.cam.w2u(p.x, p.headY() - 18, 0), tp = G.cam.w2u(q.x, q.lamp ? 60 : q.y - 6, 0);
      const ang = Math.atan2(tp.y - pp.y, tp.x - pp.x), L = 14;
      const x = Math.round(pp.x), y = Math.round(pp.y);
      g.save();
      g.strokeStyle = '#1a1020'; g.lineWidth = 6; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(ang) * L * 2, y + Math.sin(ang) * L * 2); g.stroke();
      g.strokeStyle = '#ffe060'; g.lineWidth = 3; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(ang) * L * 2, y + Math.sin(ang) * L * 2); g.stroke();
      const hx = x + Math.cos(ang) * L * 2, hy = y + Math.sin(ang) * L * 2;
      g.fillStyle = '#ffe060';
      g.beginPath(); g.moveTo(hx + Math.cos(ang) * 8, hy + Math.sin(ang) * 8);
      g.lineTo(hx + Math.cos(ang + 2.4) * 8, hy + Math.sin(ang + 2.4) * 8); g.lineTo(hx + Math.cos(ang - 2.4) * 8, hy + Math.sin(ang - 2.4) * 8); g.fill();
      P4().text(g, q.word, x, y - 24, '#bfe8ff', 12, 'center', '#0a2238');
      g.restore();
    }, { z: 2 });
  }
  function harborSetup(S, ctx) {
    const d = ctx.data;
    d.charge = 100; d.rubbles = []; d.stickies = []; d.lastAtkPress = G.input.lastPress('attack');
    for (const a of G.world.stage.actors) if (a.id && (a.id.indexOf('hb_rub') === 0 || a.id.indexOf('hb_stk') === 0)) a.remove = true;
    S.state('forklift', 0); S.state('tyre', 0);
    const e = S.actor('rhcp');
    if (e) { e.mem.ph = 'under'; e.mem.t = 1.6; G.AI.hide(e, true, { alpha: 0 }); }
    chargeBar(() => S.actor('rhcp'), () => d.charge);
    callArrow();
    ctx.on('hit', (ev) => {
      const r = S.actor('rhcp');
      if (r && ev.t === r && r.mem.stuck > 0) S.sfxText('×1.5', r, { dur: 0.4 });
    });
    S.hint('它在地下钻来钻去：听康一报方位！J3 打碎地面，按住 L 按 J 把碎块修成黏地，等它钻出来卡住', 9);
  }
  function harborTick(S, c, dt) {
    const d = c.data, p = player(), e = S.actor('rhcp'), ko = S.actor('koichi');
    if (!p || !e) return;
    // 电量：在地下慢慢回，地面上慢慢掉
    d.charge = G.clamp((d.charge || 0) + (e.hidden ? 4 : -6) * dt, 20, 100);
    // 康一跟在仗助后面 70 px（不参战）
    if (ko && !d.final) {
      const tx = G.clamp(p.x - (p.facing || 1) * 70, 40, 900);
      if (Math.abs(ko.x - tx) > 20) G.combat.walkTo(ko, tx, 146, dt, 70); else ko.play('idle');
      ko.facing = p.x > ko.x ? 1 : -1;
    }
    // 碎块 / 黏地计时
    for (const r of d.rubbles) { r.t -= dt; if (r.t <= 0 && r.a) { r.a.remove = true; r.a = null; } }
    d.rubbles = d.rubbles.filter((r) => r.t > 0);
    for (const s of d.stickies) { s.t -= dt; if (s.t <= 0 && s.a) { s.a.remove = true; s.a = null; } }
    d.stickies = d.stickies.filter((s) => s.t > 0);
    // J3 打地面：拳头前留一块碎混凝土（一招一次，最多 3 块）
    const a = p.atk;
    if (a && a.slot === 'J3' && a !== d.j3Atk && p.atkT >= a.active[0]) {
      d.j3Atk = a;
      if (d.final === 'tyre_wait' && Math.abs(p.x - HB.tyre[0]) < 46 && Math.abs(p.y - HB.tyre[1]) < 16) { breakTyre(S, c); return; }
      if (!d.final) {
        const rx = G.clamp(p.x + p.facing * 30, HB.arena[0] + 10, HB.arena[1] - 10), ry = p.y;
        if (d.rubbles.length >= 3) { const old = d.rubbles.shift(); if (old.a) old.a.remove = true; }
        const ra = T().prop(S, 'rubble', rx, ry + 0.5, { id: 'hb_rub' + T().count('hbr') });
        d.rubbles.push({ x: rx, y: ry, t: 4, a: ra });
        S.fx('crack', { x: rx, y: ry - 2, size: 14 }, { life: 1.0 });
        S.sfx('clay_crumble', 0.6);
        if (!d.rubTold) { d.rubTold = true; S.hint('地面碎了！站在碎块旁边按住 L 按 J：修成黏地', 5); }
      }
    }
    // 按住 L 按 J：修碎块 → 黏地；收尾时修轮胎
    if (guardJ(d, p)) {
      if (d.final === 'tyre_out' || d.final === 'tyre_open') {
        if (Math.abs(p.x - HB.tyre[0]) < 62 && Math.abs(p.y - HB.tyre[1]) < 18) {
          if (d.final === 'tyre_out') { d.final = 'closing'; cine(c, () => closeTyre(S, c)); }
          else S.emote(p, '它缩回去了……等它探出来！', 1.0);
        }
      } else if (!d.final) {
        const r = d.rubbles.find((q) => Math.abs(q.x - p.x) < 40 && Math.abs(q.y - p.y) < 16);
        if (r) {
          S.standAct(p, 'reach', { dx: 16, z: 2, dur: 0.6 });
          P4().fixGlow(S, r.x, r.y - 6);
          if (r.a) r.a.remove = true;
          r.t = 0;
          const sa = T().prop(S, 'sticky', r.x, r.y + 0.5, { id: 'hb_stk' + T().count('hbs') });
          sa.hold = false; sa.frozen = null;
          d.stickies.push({ x: r.x, y: r.y, t: 6, a: sa });
          d.stickyMade = (d.stickyMade || 0) + 1;
          if (d.stickyMade === 1) S.hint('黏地（6 s）：它从这里钻出来就会卡住 2 s，伤害 ×1.5', 5);
        }
      }
    }
    // 半血：路灯偷袭（全屏白 2 s）
    if (!d.flashDone && e.hp <= 450) {
      d.flashDone = true;
      cine(c, async () => {
        e.atk = null; e.tele = null; G.AI.hide(e, true, { alpha: 0 }); e.mem.ph = 'under'; e.mem.t = 2.5;
        S.sfx('thunder', 1);
        S.flash(2.0, 1, '#ffffff');
        await S.wait(0.5);
        await S.say('koichi', '仗助君！它从路灯——', { expr: 'shock' });
        await S.wait(0.6);
        p.x = HB.forklift[0] - 30; p.y = 160; p.facing = -1;
        p.hp = Math.max(1, p.hp - 10); p.flash = 1;
        p.state = 'hurt'; p.play('hurt');
        S.sfx('wall_slam', 0.9); S.shake(5, 0.4);
        S.mark('b06b_flash');
        await S.wait(0.6);
        p.state = 'idle'; p.play('idle');
        await S.say('josuke', '……被它扔到叉车这边来了。', { expr: 'rage' });
      });
      return;
    }
    // HP 锁在 225：钻进叉车电瓶
    if (!d.final && e.hp <= 226 && d.flashDone) {
      d.final = 'fork';
      cine(c, async () => {
        e.atk = null; e.tele = null; e.mem.hold = true;
        G.AI.hide(e, false); e.alpha = 1;
        await S.walk(e, HB.forklift[0] - 6, 150, { speed: 120, anim: 'dash' });
        zap(S, e.x, e.y - 10, HB.forklift[0] - 6, 133, 0.5);
        S.sfx('thunder', 0.9);
        G.AI.hide(e, true, { alpha: 0 });
        S.state('forklift', 1);
        d.charge = 100;
        S.sfxText('电力回满！', { wx: HB.forklift[0], wy: 150, wz: 40 }, { dur: 1.0 });
        await S.say('rhcp', '嘿嘿，这台叉车的电瓶归我了！', { expr: 'smile' });
        await S.wait(0.6);
        S.state('forklift', 0);
        await S.say('koichi', '它钻进轮胎里了！叉车的前轮……！', { expr: 'shock' });
        S.hint('J3：打爆叉车前轮！', 8);
        d.final = 'tyre_wait';
      });
    }
    // 轮胎裂口：辣妹每 2.4 s 探出来 1.4 s（离得近会被抓）
    if (d.final === 'tyre_out' || d.final === 'tyre_open') {
      d.pokeT = (d.pokeT || 0) + dt;
      const cyc = d.pokeT % 2.4;
      const out = cyc >= 1.0;
      if (out && d.final === 'tyre_open') {
        d.final = 'tyre_out'; d.grabbed = false;
        G.AI.hide(e, false); e.x = HB.tyre[0] - 10; e.y = HB.tyre[1] + 2; e.z = 4; e.alpha = 1; e.untargetable = true; e.play('hand');
        S.sfx('slime', 0.5);
        S.emote(e, '抓到你啦！', 0.8, '#ffe070');
      } else if (!out && d.final === 'tyre_out') {
        d.final = 'tyre_open';
        G.AI.hide(e, true, { alpha: 0 });
      }
      if (d.final === 'tyre_out' && !d.grabbed && cyc >= 1.6 && Math.abs(p.x - e.x) < 26 && Math.abs(p.y - e.y) < 12) {
        d.grabbed = true;
        G.combat.hit(e, p, { slot: 'enemy', dmg: 10, push: 16, guard: 'normal', sfxHit: 'punch', fxHit: 'light' });
      }
    }
  }
  function breakTyre(S, c) {
    const d = c.data;
    d.final = 'tyre_open'; d.pokeT = 0.2;
    S.state('tyre', 1);
    S.sfx('crash', 0.9); S.sfx('metal_crunch', 0.6);
    S.fx('burst', { x: HB.tyre[0], y: HB.tyre[1] - 6, n: 12, speed: 40, colours: ['#2a2a30', '#5a5e6a'], gravity: 160, life: 0.6 });
    S.shake(3, 0.3);
    S.mark('b06b_tyre');
    S.hint('它从轮胎裂口探出来的时候：按住 L 按 J，修复轮胎！', 8);
  }
  async function closeTyre(S, c) {
    const d = c.data, e = S.actor('rhcp'), p = player();
    S.standAct(p, 'reach', { dx: 16, z: 2, dur: 0.8 });
    P4().fixGlow(S, HB.tyre[0], HB.tyre[1] - 6, { n: 9, r: 14 });
    S.state('tyre', 0);
    e.untargetable = true;
    e.play('hurt');
    await S.wait(0.3);
    S.sfxText('夹住了！', { wx: HB.tyre[0], wy: HB.tyre[1], wz: 30 }, { dur: 0.8 });
    await S.say('rhcp', '什、什么？！轮胎合上了？！放开我——', { expr: 'shock' });
    for (let i = 0; i < 4; i++) { S.shake(2, 0.1); zap(S, e.x, e.y - 6, e.x + (i % 2 ? 14 : -14), e.y - 20, 0.15); await S.wait(0.18); }
    S.sfx('explosion', 0.9);
    S.sfxText('砰！', { wx: HB.tyre[0], wy: HB.tyre[1], wz: 26 }, { dur: 0.9 });
    S.state('tyre', 1);
    S.flash(0.12, 0.7);
    S.shake(5, 0.4);
    G.AI.hide(e, false); e.alpha = 1;
    await S.arc(e, HB.sea[0], HB.sea[1], 60, 0.9, { anim: 'hurt', spin: 10 });
    e.rot = 0;
    S.sfx('splash', 1);
    S.fx('water_splash', { x: HB.sea[0], y: HB.sea[1], size: 1.4 }, { life: 0.8 });
    e.visible = false;
    S.mark('b06b_sea');
    d.done = true;
  }
  R.fightB = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b06b_rhcp', arena: HB.arena, lead: 'josuke', swap: false, lockMsg: '这一战只能由仗助应战',
      music: 'battle', after: null, dmgScale: 0.9, losable: true, energy: { start: 30 },
      waves: [[{ kit: 'e_rhcp', cid: 'rhcp', id: 'rhcp', name: '辣妹', x: 500, y: 160, boss: true, hp: 900, minHp: 225 }]],
      testHint: (ctx) => { const e = G.S.actor('rhcp'), d = ctx.data; return { hp: e ? e.hp : null, ph: e ? e.mem.ph : null, final: d.final || null, stuck: d.stuckN || 0, sticky: d.stickyMade || 0, charge: Math.round(d.charge || 0) }; },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const p = player();
        p.x = 300; p.y = 160; p.facing = 1;
        S2.mark('b06b_start');
        harborSetup(S2, ctx);
      },
      onRetry: async (S2) => { S2.state('tyre', 0); S2.state('forklift', 0); },
      tick: (c, dt) => harborTick(S, c, dt),
      endWhen: (c) => !!c.data.done && !G.world.cine,
    });
    R.closeCharge();
    if (callH) { callH.close(); callH = null; }
    for (const a of G.world.stage.actors) if (a.id && (a.id.indexOf('hb_rub') === 0 || a.id.indexOf('hb_stk') === 0)) a.remove = true;
    const e = S.actor('rhcp');
    if (e) e.remove = true;
    return res;
  };

  // ======================================================================= 段 C：SPW 的船（b06c_rhcp）
  const SH = {
    arena: [30, 620], oku: [120, 156], joseph: [588, 150], gen: [190, 146], captain: [500, 150],
    crew: [['crew_a', 250, 150], ['crew_c', 310, 162], ['crew_oto', 370, 152], ['crew_b', 430, 164]],
  };
  const CREW_TALK = {
    crew_a: ['船员', ['我们一直在甲板上干活，没看见什么怪东西。', '发电机？刚才好像嗡了一下……']],
    crew_b: ['船员', ['你、你是谁？乔斯达先生的朋友？', '我在这条船上干了五年了。']],
    crew_c: ['船员', ['缆绳我刚绑好，别碰。', '……今天的海风有点电人。']],
    crew_oto: ['船员', ['……我是新来的。帽子？别管帽子。', '快、快回去守着你的老头吧。']],
    captain: ['船长', ['船上的人都是 SPW 财团挑的，不会有问题。', '……不过有一个是昨天才补上来的。']],
  };
  K.e_otoishi = {
    hp: 300, speed: 52, moves: [], koStyle: 'ko', idle: 'idle',
    brain(e, dt, ctx) {
      const m = e.mem, p = G.world.player;
      if (!p || m.hold) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      e.facing = p.x > e.x ? 1 : -1;
      const dx = Math.abs(p.x - e.x);
      if (dx > 34 || Math.abs(p.y - e.y) > 6) G.AI.approach(e, p, 32, dt); else e.play('idle');
      m.gap = (m.gap == null ? 1.2 : m.gap) - dt;
      m.shock = (m.shock == null ? 3 : m.shock) - dt;
      if (G.combat.tokens() >= 1) return true;
      if (m.shock <= 0 && dx < 150 && Math.abs(p.y - e.y) < 10) { G.AI.tele(e, 'OT_SHOCK'); m.shock = 5; m.gap = 1.2; return true; }
      if (m.gap <= 0 && dx < 46 && Math.abs(p.y - e.y) < 10) { G.AI.tele(e, 'OT_GUITAR'); m.gap = 1.6; }
      return true;
    },
  };
  function shipSetup(S, ctx) {
    const d = ctx.data;
    d.lastAtkPress = G.input.lastPress('attack');
    d.asked = {};
    for (const a of G.world.stage.actors) if (a.id && a.id.indexOf('sh_') === 0) a.remove = true;
    S.state('gen', 0);
    const jo = S.actor('joseph_old');
    if (jo) { jo.x = SH.joseph[0]; jo.y = SH.joseph[1]; jo.facing = -1; jo.visible = true; jo.play('idle'); jo.team = 'npc'; }
    for (const [cid, x, y] of SH.crew) S.spawn(cid, x, y, { id: 'sh_' + cid, facing: -1, name: '船员' });
    S.spawn('captain', SH.captain[0], SH.captain[1], { id: 'sh_captain', facing: -1, name: '船长' });
    // 辣妹：藏在发电机里（平时看不见，只在发电机上方画电量）
    const r = S.spawn('rhcp', SH.gen[0], SH.gen[1] + 4, { id: 'sh_rhcp', facing: 1 });
    r.shadow = false; r.visible = false;
    const genAt = { x: SH.gen[0], y: SH.gen[1], z: 0, visible: true, alpha: 1, headY: () => SH.gen[1] - 34 };
    chargeBar(() => { const rr = S.actor('sh_rhcp'); return rr && rr.visible ? rr : genAt; }, () => (ctx.gauge ? ctx.gauge.value : 0));
    S.hint('辣妹在船上的发电机里充电！走到船员旁边按 E 盘问，按住 L 按 J 削掉他们的帽子', 9);
  }
  async function capOff(S, c, cm) {
    const d = c.data, p = player();
    S.face(p, cm);
    const cap = T().prop(S, 'crewcap', cm.x, cm.y + 0.5, { id: 'sh_cap' + T().count('cap'), z: 30 });
    S.sfx('whoosh', 0.8, 0.55);
    seam(S, cm.x, cm.y - 20, 12);
    await S.arc(cap, p.x + p.facing * 8, p.y + 0.5, 20, 0.35, { z1: 26, spin: 6 });
    cap.rot = 0;
    S.emote(cm, '我的帽子！', 0.9);
    if (cm.cid !== 'crew_oto') {
      await S.say(OKU(), '……手上全是绳子磨出来的茧。干活的手，不是他。');
      cap.remove = true;
      d.capsWrong = (d.capsWrong || 0) + 1;
      return;
    }
    await S.say(OKU(), '……左手手指上，一排硬茧。这是弹吉他的手！', { expr: 'rage' });
    await S.say('otoishi', '……啧。被发现了啊。', { expr: 'smile', name: '音石明' });
    cap.remove = true;
    // 换成音石明本人
    const x = cm.x, y = cm.y;
    cm.remove = true;
    S.sfx('sting_reveal', 0.8);
    const e = c.spawn({ kit: 'e_otoishi', cid: 'otoishi', id: 'otoishi', name: '音石明', x, y, boss: true, hp: 300, koStyle: 'ko' });
    e.facing = p.x > x ? 1 : -1;
    S.fx('smoke', { x, y: y - 10, n: 8, rise: 10, life: 0.6 }, { life: 0.8 });
    S.mark('b06c_found');
    d.found = true;
    await S.say('otoishi', '辣妹！先把那个老头子烤熟！', { expr: 'rage' });
    if (c.gauge) c.gauge.value = Math.max(c.gauge.value, 99.5);       // 一现身就让辣妹扑乔瑟夫
  }
  async function lungeJoseph(S, c) {
    const d = c.data, jo = S.actor('joseph_old'), p = player(), r = S.actor('sh_rhcp');
    d.lunging = true;
    S.state('gen', 1);
    S.sfx('thunder', 1);
    if (r) { r.visible = true; r.alpha = 1; r.x = SH.gen[0]; r.y = SH.gen[1] + 4; r.play('dash'); }
    zap(S, SH.gen[0], SH.gen[1] - 20, SH.gen[0] + 20, SH.gen[1] - 4, 0.4);
    G.slowAll(0.35, 1.5);
    S.filter('vignette', 0.4, { colour: '#ffe060', inner: 0.6 });
    await S.say('rhcp', '电力满格！老头子，你的命归我了！', { expr: 'smile' });
    if (jo && r) S.walk(r, jo.x - 30, jo.y, { speed: 160, anim: 'dash' }).catch(G.cancelIgnore);
    const res = await S.press({ key: 'attack', window: 1.2, label: '按住 L 按 J：把乔瑟夫拉过来！' });
    S.filter('vignette', null);
    if (res === 'miss') {
      if (jo) { zap(S, jo.x - 20, jo.y - 20, jo.x, jo.y - 20, 0.5); jo.play('hurt'); }
      S.sfx('thunder', 1); S.flash(0.2, 0.8, '#fff8c0');
      await S.say('joseph_old', 'OH MY GOD——！', { expr: 'shock' });
      c.fail('乔瑟夫被辣妹电倒了……');
      return;
    }
    // 拉到了：空间削掉，乔瑟夫一下子到亿泰身边
    S.sfx('whoosh', 0.9, 0.55);
    if (jo) seam(S, jo.x, jo.y, 34);
    if (jo) { jo.x = G.clamp(p.x - p.facing * 20, SH.arena[0] + 10, SH.arena[1] - 10); jo.y = p.y + 4; jo.play('shock'); }
    if (r) { r.script = null; r.x = SH.gen[0]; r.y = SH.gen[1] + 4; }
    S.sfx('crash', 0.6);
    S.fx('burst', { x: SH.joseph[0] - 20, y: SH.joseph[1] - 10, n: 10, speed: 30, colours: ['#ffe060', '#fff8c0'], gravity: 60, life: 0.5 });
    await S.say('joseph_old', 'OH MY GOD！刚才那是什么？！', { expr: 'shock' });
    if (!d.saved) { d.saved = true; S.mark('b06c_save_joseph'); }
    if (c.gauge) c.gauge.value = 30;
    if (r) { r.visible = false; r.play('idle'); }
    S.state('gen', 0);
    if (jo) jo.play('idle');
    d.lunging = false;
    if (!d.found) S.hint('它还会再来！快找出混在船员里的本体（E 盘问，L+J 削帽子）', 7);
    else S.hint('打倒音石明！', 4);
  }
  function shipTick(S, c, dt) {
    const d = c.data, p = player();
    if (!p) return;
    // 按住 L 按 J：削掉离亿泰最近的船员的帽子（120 px 内；音石明现身以后照常是拉近）
    if (guardJ(d, p) && !d.found && !d.lunging) {
      let best = null, bd = 121;
      for (const [cid] of SH.crew) { const cm = S.actor('sh_' + cid); if (cm && !cm.mem.capOff) { const dd = Math.abs(cm.x - p.x) + Math.abs(cm.y - p.y); if (dd < bd) { bd = dd; best = cm; } } }
      if (best) { best.mem.capOff = true; cine(c, () => capOff(S, c, best)); return; }
    }
    if (c.gauge && c.gauge.value >= c.gauge.max - 0.01 && !d.lunging) { d.lunging = true; cine(c, () => lungeJoseph(S, c)); return; }
    // E 盘问
    if (!d.lunging && G.input.hit('ok')) {
      let best = null, bd = 34;
      for (const id of ['sh_crew_a', 'sh_crew_b', 'sh_crew_c', 'sh_crew_oto', 'sh_captain']) {
        const a = S.actor(id);
        if (!a) continue;
        const dd = Math.abs(a.x - p.x) + Math.abs(a.y - p.y) * 1.5;
        if (dd < bd) { bd = dd; best = a; }
      }
      if (best) {
        G.input.consume('ok');
        const key = best.id.slice(3), lines = CREW_TALK[key];
        const k = d.asked[key] = (d.asked[key] || 0) + 1;
        d.askN = (d.askN || 0) + 1;
        cine(c, async () => {
          S.face(best, p);
          await S.say(best.cid, lines[1][(k - 1) % 2], { name: lines[0], actor: best });
          if (key === 'crew_oto' && k === 1) await S.say(OKU(), '（……这家伙，帽子压得好低。）');
          if (d.askN === 2 && !d.capHint) { d.capHint = true; S.hint('问不出什么……按住 L 按 J：削掉帽子看看他们的手！', 6); }
        });
      }
    }
  }
  R.fightC = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b06c_rhcp', arena: SH.arena, lead: OKU(), swap: false, lockMsg: '这一战只能由亿泰应战',
      music: 'battle', after: null, dmgScale: 0.9, losable: true, energy: { start: 30 },
      gauge: { max: 100, value: 0, label: '辣妹充电', color: '#ffe060', rate: (c) => (c.data.lunging ? 0 : 100 / 60) },
      waves: [],
      testHint: (ctx) => { const e = G.S.actor('otoishi'), d = ctx.data; return { gauge: ctx.gauge ? Math.round(ctx.gauge.value) : null, found: !!d.found, saved: !!d.saved, otoHp: e ? e.hp : null, caps: d.capsWrong || 0 }; },
      onWave: async () => {},
      onRetry: async (S2) => { S2.state('gen', 0); },
      tick: (c, dt) => {
        if (!c.data.setup) { c.data.setup = true; const p = player(); p.x = SH.oku[0]; p.y = SH.oku[1]; p.facing = 1; G.S.mark('b06c_start'); shipSetup(S, c); }
        shipTick(S, c, dt);
      },
      endWhen: (c) => {
        const e = G.S.actor('otoishi');
        return !!c.data.found && !!e && (e.dead || e.hp <= 0) && !G.world.cine;
      },
    });
    R.closeCharge();
    S.state('gen', 0);
    return res;
  };
})();
