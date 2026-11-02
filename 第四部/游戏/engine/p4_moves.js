// 第四部的招式组：仗助·疯狂钻石、白衣承太郎，以及序章三个对手（承太郎的试探、水中项链、逃跑的安杰罗）的 brain。
//   仗助的数值照搬第三部承太郎（开发脚本 §0：“战斗数值全部用第三部现成的”），只换粉色和 DORA 字；走速 66（承太郎 64）。
//   敌方的大段剧情机关（水汽、钻嘴、手套、障碍物）写在 story/p4_prologue.js 的战斗 tick 里，这里只管“它自己怎么动、怎么出招”。
'use strict';
(function () {
  const G = window.G;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const CD = '#ffb0d8', CD2 = '#ff70c0';

  // ======================================================================= 东方仗助 · 疯狂钻石
  M.CD_J1 = Object.assign({}, M.SP_J1, { accent: CD });
  M.CD_J2 = Object.assign({}, M.SP_J2, { accent: CD });
  M.CD_J3 = Object.assign({}, M.SP_J3, { accent: CD, word: 'DORA!' });
  M.CD_FIN = Object.assign({}, M.SP_FIN, { accent: CD2, word: 'DORA!!' });
  M.CD_U_FIN = Object.assign({}, M.SP_U_FIN, { accent: CD2, word: 'DORA!!!' });
  K.josuke = {
    hp: 130, speed: 66, standId: 'crazyd',
    combo: ['CD_J1', 'CD_J2', 'CD_J3'],
    // 喊声（ora_voice）是承太郎的声音，仗助不配；连打的拳声循环照用
    rush: {
      tick: f(4), dmg: 4, push: 1, reach: [6, 52], depth: 10, loop: 'ora_loop', word: 'DORA',
      fx: 'fists', fist: 'crazyd', accent: '#ffc8e4', hitSfx: 'punch', finisher: 'CD_FIN',
    },
    guard: { pose: 'block' }, guardAttack: null, chords: {}, parry: { effect: 'reflect' }, dodge: {},
    special: { name: '多拉拉拉拉', title: 'josuke', bg: 'radial', colours: ['#6a1a4a', '#3a0a28', '#a8306e'], run: spJosuke, pose: 'cmd' },
    explore: { pose: 'punch' }, grunt: 'grunt_jotaro',
  };
  // 多拉拉拉拉：切入 0.92 s（combat 放）→ 冲刺 8f → 连打 60f → 终结一拳（和第三部欧拉欧拉同一节奏）
  async function spJosuke(p, C) {
    const t = C.target(180);
    C.aim(t);
    if (t) await C.dash(t.x - p.facing * 30, t.y, f(8));
    C.stand('rush', { dx: 16, jitter: 1 });
    await C.rush(f(60), { dmg: 15, tick: f(12), reach: [6, 56], depth: 12, word: 'DORA', wordEvery: f(14),
      visual: { reach: 42, spread: 34, rate: 45, scale: 1.35, big: 0.3 } });
    C.stand('punch', { dx: 20, seq: [[2, 99]] });
    const hit = C.hitArea(C.front(0, 64, 14), 'CD_U_FIN');
    if (hit.length) {
      C.fx('shockwave', { x: hit[0].x, y: hit[0].y - 24, r_max: 64, dur: 0.4, colour: '#ffd0e8' });
      C.impact(['invert', 'red'], f(2), f(12));
      C.stopAll(f(12) + 0.2);
      C.shake(6, f(30));
    }
    await C.wait(0.45);
  }

  // ======================================================================= 空条承太郎（第四部，白衣）· 白金之星
  //   拳脚和第三部一样；U 换成时停 1 s（开发脚本 §3 序2：“U 时停 1 s 照常”）。时停里敌人全停、挨的拳排队到恢复时一起算
  K.jotaro4 = Object.assign({}, K.jotaro, {
    speed: 64,
    special: { name: '白金之星·世界', title: 'jotaro_ts', bg: 'radial', colours: ['#241c6a', '#0e0a2c', '#3e32a8'], run: spJotaroTs, pose: 'cmd' },
  });
  async function spJotaroTs(p, C) {
    // 拟声字「チク…タク…」不画：第四部的字库里没有片假名大字，只留钟声
    G.time.stop(p, { tint: 'blue', sfx: 'timestop_sp', burst: 0.4, dur: 1, resume: 0.36, words: false,
      lines: { start: 'jotaro_ts', end: 'jotaro_resume' } });
    await C.wait(0.05);
  }

  // ======================================================================= 序1 承太郎的试探（开发脚本 §3 序1）
  //   承太郎不掉血：白金之星把仗助的拳全部架住（替身摆 block；伤害倍率 0.02 = 每拳只扣 1 点，血量 9999 看不出来）。
  //   不用 onHitBy 返回 'block'：格挡会把他往后推 8 px，一整段连打能把他推出半个校门
  //   出拳全部慢：预警 0.75–0.9 s（“第 ③–⑤ 步放慢出拳，给足反应时间”）。伤害照第三部 J1 的一半左右（序章 dmgScale 0.8 再乘）
  const lunge = (warn) => ({
    slot: 'enemy', body: 'cmd', stand: 'punch', standSeq: [[1, f(3)], [2, 99]], standDx: 18,
    warn: { tier: 'W1', dur: warn }, dur: warn + f(26), active: [warn, warn + f(10)],
    melee: false, dash: { dist: 58, time: f(9), w: 8 }, dmg: 6, push: 12, guard: 'normal',
    sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light', accent: '#d8c8ff', shake: [1, f(6)],
  });
  M.JT_LUNGE = lunge(0.75);
  M.JT_LUNGE_SLOW = lunge(0.9);
  // 慢速欧拉（伤害 ×0.5）：W2 0.9 s 蓄力，之后 1 s 里每 8f 一拳（2 伤），站着打，教“按住 L 挡一整串”
  M.JT_ORA = {
    slot: 'enemy', body: 'cmd', stand: 'rush', standDx: 16, warn: { tier: 'W2', dur: 0.9 },
    dur: 0.9 + 1.0 + f(16), active: [0.9, 1.9], every: f(8), from: 'body', reach: [6, 70], depth: 12,
    dmg: 2, push: 1, guard: 'normal', sfxHit: 'punch', fxHit: 'light', accent: '#d8c8ff', word: 'ORA', sfx: 'ora_rush', sfxVol: 0.6,
  };
  K.e_jotaro4_test = {
    hp: 9999, speed: 46, standId: 'starplat', moves: ['JT_LUNGE', 'JT_LUNGE_SLOW', 'JT_ORA'], koStyle: 'none', idle: 'idle', armor: true,
    dmgMul: () => 0.02,
    // 仗助的拳全被白金之星架住：替身摆一下 block（自己在出招时不摆，免得把出拳动作打断）
    onHitBy(t) {
      if (t.stand && !t.atk && !t.tele && G.clk.world - (t.mem.blockT || -9) > 0.2) { t.mem.blockT = G.clk.world; t.stand.act('block', { dur: 0.25 }); }
      return null;
    },
    // brain：按 ctx.data.step 出招（1–2 站着让仗助打；3 冲拳；4 先一串慢速欧拉再冲拳；5 慢冲拳；6 停手等 U）
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player;
      if (!p) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      e.facing = p.x > e.x ? 1 : -1;
      const step = d.step || 1;
      if (m.lastStep !== step) { m.lastStep = step; m.gap = 1.1; m.n = 0; }
      if (step <= 2 || step >= 6 || d.demoHold) { if (e.state === 'walk') { e.state = 'idle'; } e.play('idle'); return true; }
      // 保持 40 px 左右的距离（冲拳 58 px 够得着；离太近仗助来不及看预警）
      const dx = Math.abs(p.x - e.x);
      if (dx > 52 || Math.abs(p.y - e.y) > 6) G.AI.approach(e, p, 40, dt);
      else if (dx < 26) G.combat.walkTo(e, p.x + (e.x < p.x ? -40 : 40), e.y, dt, e.speed);
      else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
      m.gap -= dt;
      if (m.gap > 0 || dx > 64 || Math.abs(p.y - e.y) > 10) return true;
      if (step === 3) { G.AI.tele(e, 'JT_LUNGE'); m.gap = 2.0; }
      else if (step === 4) { G.AI.tele(e, m.n++ % 2 === 0 ? 'JT_ORA' : 'JT_LUNGE'); m.gap = 2.2; }
      else if (step === 5) { G.AI.tele(e, 'JT_LUNGE_SLOW'); m.gap = 2.3; }
      return true;
    },
  };

  // ======================================================================= 序2 段 1 水中项链（开发脚本 §3 序2）
  //   水汽突袭：脸从水汽里浮出来 0.4 s（W4 红线指着扑过来的路线）→ 沿线扑过去，10 伤；K 闪开 / L 挡住
  //   浓度越高越快：brain 每帧按 ctx.data.vapor 改速度，预警时间也跟着缩（startupMinus）
  const aquaPath = (e) => {
    const p = G.world.player;
    if (!p) return [[e.x, e.y], [e.x + e.facing * 90, e.y]];
    const dx = p.x - e.x, dy = p.y - e.y, d = Math.hypot(dx, dy) || 1;
    const over = 26;      // 扑过头一点：不是停在人身上
    return [[e.x, e.y], [p.x + dx / d * over, p.y + dy / d * over * 0.6]];
  };
  M.AQ_RUSH = {
    slot: 'enemy', body: 'lunge', stand: null, warn: { tier: 'W4', dur: 0.4, path: aquaPath },
    dur: 0.4 + 0.45, active: [0.4, 0.4 + 0.3], melee: false, dash: { dist: 150, time: 0.3, w: 8, line: true },
    dmg: 10, push: 10, guard: 'normal', sfx: 'water_jet', sfxVol: 0.7, sfxHit: 'water_splash', fxHit: 'light', accent: '#a0e0ff',
  };
  // 顺着雨丝从墙洞钻进来：预警只有 0.3 s（墙开着的代价）
  M.AQ_RUSH_FAST = Object.assign({}, M.AQ_RUSH, { warn: { tier: 'W4', dur: 0.3, path: aquaPath }, dur: 0.3 + 0.45, active: [0.3, 0.6] });
  K.e_aqua = {
    hp: 400, speed: 60, moves: ['AQ_RUSH'], koStyle: 'none', idle: 'idle', armor: true, fly: { z: 14 },
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player, st = G.world.stage;
      if (!p || !st) return true;
      // 浮在半空（头的高度）上下飘
      e.z = 12 + Math.round(Math.sin(G.clk.world * 2.4 + e.uid) * 3);
      // 剧情在演（钻嘴 / 被打散重组）、或者仗助张着嘴把它引过去（m.bait，战斗 tick 在拉它）：自己不动
      if (m.hold || (m.scatter || 0) > 0 || m.bait) return true;
      const k = 1 + (d.vapor || 0) / 100;
      e.speed = 60 * k;
      e.mem.startupMinus = Math.min(0.12, ((d.vapor || 0) / 100) * 0.12);
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      // 绕着队长飘：在他左边或右边 50 px，偶尔换边
      const side = m.side || (m.side = e.x < p.x ? -1 : 1);
      const tx = G.clamp(p.x + side * 50, st.x0 + 12, st.x1 - 12);
      const ty = G.clamp(p.y + Math.round(Math.sin(G.clk.world * 1.3) * 8), st.yMin, st.yMax);
      G.combat.walkTo(e, tx, ty, dt, e.speed * 0.8);
      e.facing = p.x > e.x ? 1 : -1;
      m.gap = (m.gap == null ? 2.2 : m.gap) - dt * k;
      m.rainCd = (m.rainCd == null ? 4 : m.rainCd) - dt;
      if (m.gap > 0 || G.combat.tokens() >= 2) return true;
      // 墙开着：先钻进墙洞外的雨里，从洞口扑出来（brain 不管洞在哪：剧情把位置写进 ctx.data.hole）
      if (d.wallOpen && d.hole && m.rainCd <= 0) {
        m.rainCd = 7;
        G.AI.blink(e, d.hole[0], G.clamp(d.hole[1], st.yMin, st.yMax), { word: null });
        if (G.fx) G.fx.spawn('water_splash', { x: d.hole[0], y: d.hole[1], size: 0.8 }, { by: e });
        G.AI.tele(e, 'AQ_RUSH_FAST');
      } else G.AI.tele(e, 'AQ_RUSH');
      m.gap = 2.4 + Math.random() * 1.2;
      if (Math.random() < 0.35) m.side = -side;
      return true;
    },
  };

  // ======================================================================= 序2 段 2 逃跑的安杰罗（不能打：untargetable，只能追上去抓）
  //   往右跑，速度比仗助慢一点；仗助追近了就踢翻路边的东西（剧情 tick 负责障碍物），跑到岩石那里没路了就缩在原地
  K.e_angelo_run = {
    hp: 999, speed: 52, moves: [], koStyle: 'none', idle: 'idle',
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem;
      if (m.hold) return true;
      const end = d.endX || 1040;
      if (e.state !== 'idle' && e.state !== 'walk' && e.state !== 'run') return true;
      if (e.x >= end - 2) { e.facing = -1; e.play('hurt'); e.state = 'idle'; return true; }   // 走投无路，缩着
      const sp = (m.boost > 0 ? 1.6 : 1) * (d.angeloSpeed || e.speed);
      m.boost = Math.max(0, (m.boost || 0) - dt);
      const ty = d.angeloY != null ? d.angeloY : e.y;
      G.combat.walkTo(e, end, ty, dt, sp);
      return true;
    },
  };
})();
