// 第四部的招式组：仗助·疯狂钻石、白衣承太郎、亿泰·轰炸空间、康一·回音 ACT1（第2章起），以及序章三个对手（承太郎的试探、水中项链、逃跑的安杰罗）的 brain。
//   亿泰、康一第一次能操作是第2章，后面各章都要用，所以和仗助放在一起（分章开发约定第 5 节）；回音 ACT2 / ACT3 由第一次出现的章自己派生。
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

  // ======================================================================= 削过的黑缝（轰炸空间的招都留这一道）
  //   竖着的一道黑色裂口、两边一圈淡蓝的光：先“唰”地拉开（前 12%），70% 以后变细淡出。y 是脚底，往上画 h px
  if (G.FX && G.FX._SIG) {
    G.FX.erase_seam = function (P, x, y, t, t0, kw) {
      kw = kw || {};
      const dur = kw.dur == null ? 1 : kw.dur, u = (t - t0) / dur;
      if (u < 0 || u >= 1) return;
      const px = G.px, h = kw.h || 30, open = Math.min(1, u / 0.12), w = u < 0.7 ? 2 : 1, a = u < 0.7 ? 1 : (1 - u) / 0.3;
      const X = Math.round(x), top = Math.round(y - h * open), bot = Math.round(y);
      for (let yy = top; yy <= bot; yy++) {
        const j = ((yy * 7) & 3) === 0 ? 1 : 0;           // 边上一点锯齿
        px.rect(P, X - w - 1 + j, yy, 1, 1, '#b8d4ff', a * 0.9);
        px.rect(P, X - w + j, yy, w * 2, 1, '#06060c', a);
        px.rect(P, X + w + j, yy, 1, 1, '#b8d4ff', a * 0.9);
      }
    };
    G.FX._SIG.erase_seam = ['x', 'y', 't', 't0'];
  }
  const seam = (x, y, by, o = {}) => {
    if (G.fx) G.fx.spawn('erase_seam', { x, y, h: o.h || 30, dur: o.dur || 1 }, { life: o.dur || 1, by });
  };

  // ======================================================================= 虹村亿泰 · 轰炸空间（设计文档 3.3「亿泰 · 轰炸空间」）
  //   HP 140、走速 62（第2章开发脚本 §0）。J1 / J2 右手横扫、反手（和白金之星 J1 / J2 同档）；
  //   J3「削」：右手掌一抹，伤害 22、无视格挡，削过的地方留一道黑缝 1 s；J3 后连按：左拳连打，终结是一次削；
  //   按住 L 按 J「拉近」：削掉中间的空间，把面前 120 px 内最近的敌人（或者挂了 pullable 的道具）拉到跟前、硬直 18f，接 J3 是固定连段；
  //   K「削步」：削掉面前的空间瞬移 64 px，代替普通闪避，无敌帧一样；U：切入 → 连削三次，每次先拉近再削，最后一下削掉它脚下的地面让它摔倒。
  //   各章的情境招（削地面露出电缆、削掉空气炸弹、把猫草拉开……）写在各章自己的战斗文件里（kitOverride / 道具的 onPulled）
  const TH = '#8cb6ff', TH2 = '#3462d0';
  M.TH_J1 = Object.assign({}, M.SP_J1, { accent: TH });
  M.TH_J2 = Object.assign({}, M.SP_J2, { accent: TH });
  const SEAM_FX = (dx, h) => [{ name: 'erase_seam', dx, kw: { h, dur: 1 }, life: 1 }];
  M.TH_J3 = {
    slot: 'J3', body: 'cmd', stand: 'erase', standSeq: [[0, f(8)], [1, f(16)], [2, 99]], standDx: 22, dur: f(30), active: [f(9), f(13)],
    from: 'body', reach: [6, 48], depth: 9, dmg: 22, push: 4, guard: 'none', energy: 3, poiseDmg: 30, stopAll: f(6), link: f(13), cancel: f(13),
    step: 2, sfx: 'whoosh', sfxRate: 0.7, sfxHit: 'punch_heavy', sfxVol: 0.8, fxHit: 'heavy', accent: TH, shake: [3, f(12)], bump: 0.06,
    activeFx: SEAM_FX(14, 30),
  };
  // 连打终结：一次削（6 / 4 / 24，无视格挡）
  M.TH_FIN = {
    slot: 'fin', body: 'cmd', stand: 'erase', standSeq: [[1, f(10)], [2, 99]], standDx: 24, dur: f(34), active: [f(6), f(10)],
    from: 'body', reach: [6, 54], depth: 10, dmg: 18, push: 12, guard: 'none', energy: 4, poiseDmg: 25, stopAll: f(8), link: 99, cancel: f(10),
    step: 4, sfx: 'whoosh', sfxRate: 0.65, sfxHit: 'crit', fxHit: 'finisher', accent: TH2, shake: [3, f(15)], bump: 0.08, flashTarget: f(2),
    activeFx: SEAM_FX(16, 34),
  };
  // 拉近：判定不靠近战框，onStart 里自己找人
  function pullPick(a, range) {
    const st = G.world && G.world.stage, dir = a.facing || 1;
    if (!st) return null;
    const foe = a.team === 'enemy';
    let best = null, bd = Infinity;
    for (const t of st.actors) {
      if (!t || t === a || t.remove || t.dead || t.hp <= 0 || t.untargetable || t.visible === false) continue;
      const ok = foe ? (t === G.world.player || t.team === 'ally') : (t.team === 'enemy' || (t.team === 'object' && t.pullable));
      if (!ok) continue;
      const dx = (t.x - a.x) * dir, dy = Math.abs(t.y - a.y);
      if (dx < 8 || dx > range || dy > 16) continue;
      const d = dx + dy * 2;
      if (d < bd) { bd = d; best = t; }
    }
    return best;
  }
  function pullTo(a, t, gap = 24, dur = 0.12) {
    const st = G.world.stage, dir = a.facing || 1;
    let x = a.x + dir * gap, y = a.y;
    if (st && st.bounds) { const [lo, hi] = st.bounds(); x = G.clamp(x, lo, hi); y = G.clamp(y, st.yMin, st.yMax); }
    seam(t.x, t.y, a, { h: 32 });
    if (G.combat.ghostBurst) G.combat.ghostBurst(t, 2);
    t.stunT = Math.max(t.stunT || 0, f(18));
    if (t.onPulled) t.onPulled(a);
    return G.combat.tweenTo(t, x, y, dur);
  }
  M.TH_PULL = {
    slot: 'guardAttack', body: 'cmd', stand: 'pull', standDx: 18, dur: f(20), active: [f(5), f(7)], melee: false, cd: 0.6, energy: 0,
    sfx: 'whoosh', sfxRate: 0.55, accent: TH,
    onStart(a) {
      const t = pullPick(a, 120);
      if (t) pullTo(a, t);
      else seam(a.x + (a.facing || 1) * 40, a.y, a, { h: 26, dur: 0.6 });
    },
  };
  // 削步：起点、落点各一道黑缝，不拖残影（像是空间被削掉、人直接到了那边）
  function eraseStep(a, d) {
    seam(a.x, a.y, a, { h: 30, dur: 0.6 });
    seam(a.x + d.x, a.y + d.y, a, { h: 30, dur: 0.6 });
    a.ghostOn = false;
  }
  M.TH_U_CUT = {
    slot: 'special', body: 'cmd', stand: 'erase', dur: f(20), active: [0, f(4)], from: 'body', reach: [0, 60], depth: 14,
    dmg: 25, push: 2, energy: 0, poiseDmg: 40, stopAll: 0, guard: 'none', sfxHit: 'punch_heavy', fxHit: 'heavy', accent: TH, shake: [3, f(12)],
  };
  M.TH_U_FIN = Object.assign({}, M.TH_U_CUT, {
    dmg: 40, push: 30, launch: { z: 10, t: f(36) }, poiseDmg: 999, sfxHit: 'ko_hit', fxHit: 'finisher', accent: TH2, bump: 0.2, flashTarget: f(2),
  });
  K.okuyasu = {
    hp: 140, speed: 62, standId: 'thehand',
    combo: ['TH_J1', 'TH_J2', 'TH_J3'],
    rush: {
      tick: f(4), dmg: 4, push: 1, reach: [6, 52], depth: 10, loop: 'ora_loop', word: null,
      fx: 'fists', fist: 'thehand', accent: '#a8c8ff', hitSfx: 'punch', finisher: 'TH_FIN',
    },
    guard: { pose: 'block' }, guardAttack: 'TH_PULL', chords: {}, parry: { effect: 'reflect' },
    dodge: { dist: 64, dur: f(5), iframe: f(10), cd: f(30), onStart: eraseStep },
    special: { name: '轰炸空间', title: 'okuyasu', bg: 'radial', colours: ['#1c3a8a', '#0a1430', '#3462d0'], run: spOkuyasu, pose: 'cmd' },
    explore: { pose: 'erase' }, grunt: 'grunt_jotaro',
  };
  // 连削三次：拉近 0.1 s → 削（判定在身前 0–60 px）→ 停一下；第三下削掉脚下的地面，对手摔出去
  async function spOkuyasu(p, C) {
    for (let i = 0; i < 3; i++) {
      const t = C.target(220), last = i === 2;
      if (!t) break;
      C.aim(t);
      C.stand('pull', { dx: 18 });
      C.sfx('whoosh', { rate: 0.55 });
      await pullTo(p, t, 26, 0.1);
      if (!C.valid()) return;
      C.stand('erase', { dx: 22, seq: [[1, f(6)], [2, 99]] });
      C.sfx('whoosh', { rate: 0.7 });
      seam(p.x + p.facing * 30, p.y, p, { h: 36 });
      const hit = C.hitArea(C.front(0, 64, 14), last ? 'TH_U_FIN' : 'TH_U_CUT');
      if (hit.length) {
        if (last) {
          G.combat.fxAt('crack', { x: hit[0].x, y: hit[0].y, size: 16 }, p, 1.5);     // crack 默认不会自己消失
          C.impact(['invert', 'blue'], f(2), f(12));
          C.stopAll(f(12) + 0.2);
          C.shake(6, f(30));
        } else { C.impact('invert', f(2)); C.shake(3, f(12)); }
      }
      await C.wait(last ? 0.5 : 0.3);
    }
  }

  // ======================================================================= 广濑康一 · 回音 ACT1（设计文档 3.3「康一 · 回音」；第2章第 3 战起能用）
  //   HP 90、走速 68。J：往前射一个拟声字（「咚！」「嗡——」「叮铃铃」「啪！」轮着来），伤害很低；贴中以后 3 s 内每秒被吵得顿一下（硬直 10f）。
  //   ACT1 打不出拳：没有连打。K 闪避、L 格挡照通用；U「大音量」：身边 160 px 的敌人全被吵得硬直 1.5 s（Boss 0.8 s），再吵 3 s。
  //   ACT2（尾巴抽打、声音陷阱）由第3章派生 K.koichi_act2，ACT3（近身拳、3 FREEZE）由第7章派生 K.koichi_act3
  const EC = '#7cf0b0';
  const ECHO_IMG = ['ui/sfx/echo_0', 'ui/sfx/echo_1', 'ui/sfx/echo_2', 'ui/sfx/echo_3'];
  function noisy(t, sec = 3) {
    const run = G.runId, m = t.mem || (t.mem = {});
    m.noisyUntil = G.clk.world + sec;
    if (m.noisyLoop) return;
    m.noisyLoop = true;
    (async () => {
      try {
        while (G.runId === run && !t.dead && t.hp > 0 && G.clk.world < m.noisyUntil) {
          await G.wait(1, 'world');
          if (G.runId !== run || t.dead || t.hp <= 0) break;
          t.stunT = Math.max(t.stunT || 0, f(10));
          if (G.fx) G.fx.spawn('glint', { x: t.x, y: t.y - 30, size: 5 }, { life: 0.25, by: t });
        }
      } catch (e) { if (!(G.cancelled && G.cancelled(e))) throw e; } finally { m.noisyLoop = false; }
    })();
  }
  const echoShot = (dmg, push, stop) => ({
    kind: 'img', image: ECHO_IMG[0], n: 1, speed: 230, life: 0.7, range: 150, hitR: [6, 8, 22], dmg, push, energy: 2,
    stop, slot: 'shot', reflect: false, accent: EC, onHit: (s, t, r) => { if (r && r.dmg) noisy(t); },
  });
  const nextWord = (a) => { a.mem.echoN = ((a.mem.echoN == null ? -1 : a.mem.echoN) + 1) % ECHO_IMG.length; return { image: ECHO_IMG[a.mem.echoN] }; };
  M.EC_J1 = {
    slot: 'J1', body: 'cmd', stand: 'shoot', standDx: 6, standZ: 14, dur: f(18), active: [f(6), f(8)], melee: false, from: 'stand',
    fireAt: [f(6)], link: f(10), cancel: f(10), shotAhead: 10, shotZ: 8, shot: echoShot(3, 4, f(2)), shotMod: nextWord,
    sfx: 'whoosh', sfxRate: 1.4, energy: 0, accent: EC,
  };
  M.EC_J2 = Object.assign({}, M.EC_J1, { slot: 'J2' });
  M.EC_J3 = Object.assign({}, M.EC_J1, { slot: 'J3', dur: f(24), link: f(14), cancel: f(14), shot: echoShot(5, 10, f(4)), sfxRate: 1.1 });
  M.EC_U = {
    slot: 'special', body: 'cmd', dur: f(20), active: [0, f(4)], from: 'body', reach: [0, 160], depth: 30,
    dmg: 12, push: 8, energy: 0, poiseDmg: 40, guard: 'none', sfxHit: 'punch', fxHit: 'light', accent: EC,
  };
  K.koichi = {
    hp: 90, speed: 68, standId: 'echoes1',
    combo: ['EC_J1', 'EC_J2', 'EC_J3'],
    rush: null,
    guard: { pose: 'block' }, guardAttack: null, chords: {}, parry: { effect: 'root', dur: f(24) }, dodge: {},
    special: { name: '回音', title: 'koichi', bg: 'radial', colours: ['#1c6a40', '#0a3a20', '#2a8a50'], run: spKoichi, pose: 'cmd' },
    explore: { pose: 'shoot' }, grunt: null,
    noisy,      // 各章的情境招也要“吵得顿一下”时用：G.KITS.koichi.noisy(敌人, 秒数)
  };
  async function spKoichi(p, C) {
    C.stand('shoot', { dx: 8, z: 14 });
    C.sfx('whoosh', { rate: 0.5 });
    C.fx('shockwave', { x: p.x, y: p.y - 20, r_max: 160, dur: 0.5, colour: '#9cf0c0' });
    const hit = C.hitArea({ x0: p.x - 160, x1: p.x + 160, y0: p.y - 30, y1: p.y + 30 }, 'EC_U');
    for (const t of hit) {
      t.stunT = Math.max(t.stunT || 0, t.boss ? 0.8 : 1.5);
      noisy(t, 3);
      C.word('咚！', t);
    }
    if (hit.length) C.shake(3, f(18));
    await C.wait(0.6);
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
