// 第7章　商店街 / 灰姑娘与枯萎穿心攻击：第 11 战三段（开发脚本 第四部/docs/第7章_开发脚本.md 第 3 节）。剧情节拍在 story/p4_ch7.js。
//   段 A 承太郎护住康一（目标段 35 s）→ 段 B 康一 + 回音 ACT3 用 3 FREEZE 压住坦克 → 段 C 承太郎（带伤）打吉良（目标段，600 HP）。
//   枯萎穿心攻击打不坏、追“热”：亮着的热源 > 刚出过拳的人 > 默认目标。坦克的“怎么动”写在 K.e_sha 的 brain，
//   “爆炸、热源、烟头、重量”这些剧情机关写在各段的战斗 tick 里（和序章一样）。
//   规矩见 第四部/docs/分章开发约定.md：招式组 K.koichi_act3 / e_sha / e_kira 只在这个文件里定义，不改公共引擎。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const R = (G.P4CH7 = {});

  // 别章画的人：正式图合进来以前用本章的占位（tools/art/p4_chars_ch7.py 的 ph7_*）
  const PH = { yukako: 'ph7_yukako', okuyasu: 'ph7_okuyasu', kira: 'ph7_kira', killerqueen: 'ph7_killerqueen' };
  R.cid = (c) => ((G.D && G.D.chars && G.D.chars[c]) || !PH[c] ? c : PH[c]);

  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-fight' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  R.cine = cine;
  const player = () => G.world.player;
  const member = (cid) => ((G.party && G.party.members) || []).find((a) => a.cid === cid) || null;
  const an = () => (G.D && G.D.bg && G.D.bg.morioh_avenue && G.D.bg.morioh_avenue.anchors) || {};
  const at = (k, d) => an()[k] || d;

  // ================================================================ 招式组
  // 回音 ACT3（康一）：近身拳三连，伤害偏低；没有连打（设计文档 3.3）。U「3 FREEZE」由段 B 用 kitOverride 按重量条开窗
  // 爆炸的击退都压在 24 以下：引擎里 push ≥ 24 会打出倒地（down），康一的图没有倒地动作
  const E3 = '#7af0b8';
  //   出拳的是 ACT3，康一本人站着指挥（body 'idle'：康一的图只有 idle / walk / bow，没有出拳的身体动作）
  M.E3_J1 = Object.assign({}, M.SP_J1, { body: 'idle', dmg: 4, accent: E3, poiseDmg: 4 });
  M.E3_J2 = Object.assign({}, M.SP_J2, { body: 'idle', dmg: 4, accent: E3, poiseDmg: 4 });
  M.E3_J3 = Object.assign({}, M.SP_J3, { body: 'idle', dmg: 6, accent: E3, word: null, launch: null, push: 10, poiseDmg: 10 });
  // 照分章约定从 ACT2（第3章）/ ACT1（第2章）派生：闪避、格挡、替身调查沿用，换掉招式和替身
  K.koichi_act3 = Object.assign({}, K.koichi_act2 || K.koichi || {}, {
    hp: 100, speed: 68, standId: 'echoes3', combo: ['E3_J1', 'E3_J2', 'E3_J3'], rush: null, special: null,
    guardAttack: null, chords: {}, grunt: null,
  });

  // 枯萎穿心攻击：打不坏（伤害倍率 0、最低血量锁死），挨打只被推开；怎么追由 ctx.data.shaTarget 决定（各段 tick 每帧算好）
  K.e_sha = {
    hp: 9999, speed: 36, moves: [], koStyle: 'none', idle: 'idle', armor: true, dmgMul: () => 0.02,   // 0 会被引擎当成“免疫”直接返回、不发 hit 事件（engine/combat.js hit）；0.02 = 每下 1 点，挨打时再补满
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, st = G.world.stage;
      if (!st) return true;
      if (m.hold || m.armed > 0 || d.frozen) { if (e.state === 'walk') e.state = 'idle'; return true; }
      const t = d.shaTarget;
      if (!t) { e.play('idle'); return true; }
      const sp = (d.shaSpeed || e.speed) * (m.cool > 0 ? 0.5 : 1);
      // 刚炸完往回退一点（cool），不然贴着人连炸
      if (m.cool > 0 && m.back) { G.combat.walkTo(e, m.back[0], m.back[1], dt, sp); e.play('walk'); return true; }
      G.combat.walkTo(e, t.x, G.clamp(t.y, st.yMin, st.yMax), dt, sp);
      e.facing = t.x > e.x ? 1 : -1;
      e.play('walk');
      return true;
    },
  };

  // 吉良吉影：杀手皇后刺拳二连；第一炸弹（硬币）和“去踢康一”由段 C 的 tick 来做（要放道具和危险区）
  const kqJab = (warn, dmg) => ({
    slot: 'enemy', body: 'punch', stand: 'punch', standSeq: [[1, f(3)], [2, 99]], standDx: 18,
    warn: { tier: 'W1', dur: warn }, dur: warn + f(24), active: [warn, warn + f(8)],
    melee: false, dash: { dist: 40, time: f(8), w: 8 }, dmg, push: 14, guard: 'normal',
    sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light', accent: '#f0a8d8', shake: [1, f(6)],
  });
  M.KQ_JAB = kqJab(0.4, 8);
  M.KQ_JAB2 = kqJab(0.3, 10);
  K.e_kira = {
    hp: 600, speed: 52, moves: ['KQ_JAB', 'KQ_JAB2'], koStyle: 'none', idle: 'idle',
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player;
      if (!p || m.hold) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      const fast = e.hp < e.maxHp / 2 ? 0.8 : 1;
      // 冲着康一去（tick 定时把 d.kiraGoKoichi 打开）：走到康一身边，tick 负责踢
      const ko = d.koichi;
      if (d.kiraGoKoichi && ko) {
        G.combat.walkTo(e, ko.x + (ko.x < e.x ? 16 : -16), ko.y, dt, e.speed * 1.1);
        e.facing = ko.x > e.x ? 1 : -1; e.play('walk');
        return true;
      }
      e.facing = p.x > e.x ? 1 : -1;
      const dx = Math.abs(p.x - e.x);
      if (dx > 44 || Math.abs(p.y - e.y) > 6) { G.AI.approach(e, p, 36, dt); e.play('walk'); }
      else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
      m.gap = (m.gap == null ? 1.2 : m.gap) - dt;
      if (m.gap > 0 || dx > 60 || Math.abs(p.y - e.y) > 10) return true;
      m.n = (m.n || 0) + 1;
      G.AI.tele(e, m.n % 2 ? 'KQ_JAB' : 'KQ_JAB2');
      m.gap = (1.6 + Math.random() * 0.6) * fast;
      return true;
    },
  };

  // ================================================================ 热源（背景开关层 + 烟头）
  const HEATS = () => [
    { key: 'heat_car', x: at('car_hood', [582])[0], y: 158, label: '轿车的引擎盖' },
    { key: 'heat_vend', x: at('vending_back', [419])[0], y: 146, label: '售货机背后' },
    { key: 'heat_truck', x: at('truck_hood', [800])[0], y: 158, label: '小货车的引擎盖' },
    { key: 'heat_butt', x: at('butt', [214])[0], y: 166, label: '马路上的烟头' },
  ];
  function heatsInit(S, c) {
    c.data.heats = HEATS().map((h) => Object.assign(h, { on: false, cd: 0, ttl: 0 }));
    for (const h of c.data.heats) S.state(h.key, 0);
  }
  function heatOn(S, c, h, ttl) {
    h.on = true; h.ttl = ttl || 0;
    if (h.key) S.state(h.key, 1);
    if (!c.data.heatTold) { c.data.heatTold = true; S.hint(h.label + '热起来了：坦克会先去撞热的东西！', 4); }
  }
  function heatOff(S, c, h) {
    h.on = false; h.cd = 30;
    if (h.key) S.state(h.key, 0);
    if (h.prop) { h.prop.remove = true; h.prop = null; }
  }
  function heatTick(S, c, dt) {
    for (const h of c.data.heats || []) {
      if (h.cd > 0) h.cd -= dt;
      if (h.on && h.ttl > 0) { h.ttl -= dt; if (h.ttl <= 0) heatOff(S, c, h); }
    }
    c.data.heats = (c.data.heats || []).filter((h) => h.key || h.on);
  }
  // 坦克挑目标：离它 280 px 以内亮着的热源（最近的）> 3 s 内出过拳的人 > 默认目标
  function pickTarget(c, sha, people, fallback, range = 280) {
    let best = null, bd = 1e9;
    for (const h of c.data.heats || []) {
      if (!h.on) continue;
      const dd = Math.abs(h.x - sha.x);
      if (dd < range && dd < bd) { bd = dd; best = h; }
    }
    if (best) return best;
    for (const a of people) if (a && c.t - (a._ch7Hot == null ? -9 : a._ch7Hot) < 3) return a;
    return fallback;
  }

  // 爆炸：坦克停 0.35 s 张嘴（地上红圈），然后白光、危险区判定。打在热源上那个热源熄掉；自己毫发无伤，退开
  function armBlast(S, c, sha, tgt) {
    const m = sha.mem;
    m.armed = 0.35;
    sha.atk = null; sha.tele = null; sha.state = 'idle'; sha.play('boom');
    S.sfx('skid', 0.5);
    S.sfxText('看这边！', sha, { dur: 0.7 });
    const x = sha.x, y = sha.y;
    G.combat.hazard({ shape: 'ellipse', x, y, rx: 30, ry: 12, warn: 0.35, dur: 0.1, dmg: 26, push: 22, owner: sha, side: 'enemy', guard: 'normal',
      onActive: () => {
        S.sfx('explosion', 0.9);
        S.fx('explosion', { x, y: y - 10, size: 1.1 }, { life: 0.6 });
        S.flash(0.1, 0.7);
        S.shake(4, 0.3);
      } });
    G.defer(0.36, () => {
      if (G.world.fight !== c) return;
      m.armed = 0; m.cool = 2; c.data.blasts = (c.data.blasts || 0) + 1;
      m.back = [G.clamp(x + (sha.x <= (tgt.x || x) ? -40 : 40), c.spec.arena[0] + 10, c.spec.arena[1] - 10), y];
      sha.play('walk');
      if (tgt && tgt.key !== undefined && tgt.on) { heatOff(S, c, tgt); m.pant = 2; S.fx('smoke', { x: tgt.x, y: tgt.y - 6, n: 6, rise: 14, life: 0.9 }, { life: 1.2 }); }
      if (tgt && tgt.cig) { tgt.on = false; if (tgt.prop) tgt.prop.remove = true; m.pant = 2; }
    }, 'world');
  }
  function shaTick(S, c, dt, people, fallback, range) {
    const sha = S.actor('sha'), d = c.data;
    if (!sha) return;
    const m = sha.mem;
    if (m.cool > 0) m.cool -= dt;
    if (m.pant > 0) m.pant -= dt;
    if (m.armed > 0 || d.frozen) return;
    const tgt = pickTarget(c, sha, people, fallback, range);
    if (tgt !== d.shaTarget) {
      if (d.shaTarget && tgt) S.emote(sha, '看这边！', 0.8, '#c8d8ff');
      d.shaTarget = tgt;
    }
    if (!tgt || m.cool > 0) return;
    if (Math.abs(tgt.x - sha.x) < 16 && Math.abs((tgt.y || sha.y) - sha.y) < 10) armBlast(S, c, sha, tgt);
  }
  // 打到坦克：不掉血，只被推开、冒火花
  function shaOnHit(S, c, e, extra) {
    const sha = S.actor('sha');
    if (!sha || e.t !== sha) return false;
    const att = e.att, dir = att ? (sha.x >= att.x ? 1 : -1) : 1;
    const push = (e.slot === 'J3' || e.slot === 'fin' || e.slot === 'special' ? 40 : 10) * (extra || 1);
    const st = G.world.stage;
    sha.x = G.clamp(sha.x + dir * push, c.spec.arena[0] + 8, c.spec.arena[1] - 8);
    sha.y = G.clamp(sha.y, st.yMin, st.yMax);
    sha.hp = sha.maxHp;
    if (att) att._ch7Hot = c.t;
    if ((c.data.clangs = (c.data.clangs || 0) + 1) % 3 === 1) { S.sfx('clang', 0.6); S.sfxText('锵！', sha, { dur: 0.5 }); }
    return true;
  }

  // =====================================================================================================================
  // 段 A　承太郎：护住康一（b11a_sha）
  // =====================================================================================================================
  const A = { arena: [140, 700], koichi: [250, 152], jotaro: [300, 160], sha: [420, 158], survive: 35 };
  function throwCig(S, c) {
    const p = player(), d = c.data;
    if (d.cigCd > 0) return;
    d.cigCd = 5;
    const st = G.world.stage;
    const x = G.clamp(p.x + p.facing * 80, c.spec.arena[0] + 10, c.spec.arena[1] - 10), y = G.clamp(p.y + 4, st.yMin, st.yMax);
    S.sfx('lighter', 0.6); S.sfx('whoosh', 0.5);
    const cig = T().prop(S, 'cig', p.x, p.y, { id: 'cig' + T().count('cig'), z: 20 });
    if (cig) S.arc(cig, x, y, 18, 0.35, { z1: 0 }).catch(G.cancelIgnore);
    const h = { key: null, cig: true, x, y, on: true, ttl: 6, cd: 0, prop: cig, label: '烟头' };
    d.heats.push(h);
    if (!d.cigMarked) { d.cigMarked = true; S.mark('b11a_cig'); }
    S.hint('坦克转头去追烟头了！', 3);
  }
  function aSetup(S, c) {
    const d = c.data, ko = member('koichi');
    heatsInit(S, c);
    d.cigCd = 0; d.timeline = [[8, 'heat_car'], [18, 'heat_vend'], [28, 'heat_truck']];
    d.lastGuardJ = G.input.lastPress('attack');
    if (ko) { ko.x = A.koichi[0]; ko.y = A.koichi[1]; ko.facing = 1; ko.hold = true; ko.state = 'idle'; ko.play('hurt'); }
    const sha = S.actor('sha');
    if (sha) { sha.mem.cool = 1.2; }
    c.on('hit', (e) => { if (shaOnHit(S, c, e)) return; });
    c.on('special', () => { G.defer(1.6, () => { if (G.world.fight === c && !d.tsTold) { d.tsTold = true; S.emote(player(), '……连时停都打不坏。', 1.6); } }, 'world'); });
    S.hint('枯萎穿心攻击冲着康一去了！J 把它打开（打不坏）　按住 L 按 J：弹烟头引开它', 8);
  }
  function aTick(S, c, dt) {
    const d = c.data, p = player(), ko = member('koichi');
    if (!p) return;
    d.cigCd = Math.max(0, (d.cigCd || 0) - dt);
    for (const [t, key] of d.timeline) {
      if (c.t >= t && !d['tl_' + key]) { d['tl_' + key] = true; const h = d.heats.find((x) => x.key === key); if (h) heatOn(S, c, h, 12); }
    }
    heatTick(S, c, dt);
    // 按住 L 按 J：弹烟头
    const lp = G.input.lastPress('attack');
    if (lp !== d.lastGuardJ) { d.lastGuardJ = lp; if (p.state === 'guard') throwCig(S, c); }
    shaTick(S, c, dt, [p], ko);
    // 坦克离康一近了：提示一次
    const sha = S.actor('sha');
    if (sha && ko && Math.abs(sha.x - ko.x) < 70 && !d.nearTold) { d.nearTold = true; S.hint('它要撞上康一了！挡在中间打开它，或者弹烟头！', 4); }
    if (ko) { ko.x = A.koichi[0]; ko.y = A.koichi[1]; }
  }
  R.fightA = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b11a_sha', arena: A.arena, lead: 'jotaro4', swap: false, lockMsg: '康一吓得动不了了', vip: 'koichi', vipHp: 60,
      music: 'battle', after: null, dmgScale: 1.0, playerMinHp: 1, losable: false, energy: { start: 40 }, coverage: false,
      timer: { label: '护住康一：', until: A.survive }, survive: A.survive,
      waves: [[{ kit: 'e_sha', cid: 'sha', id: 'sha', name: '枯萎穿心攻击', x: A.sha[0], y: A.sha[1], boss: true, hp: 9999, minHp: 9000 }]],
      testHint: (ctx) => { const sha = G.S.actor('sha'), ko = member('koichi'); return { shaX: sha ? Math.round(sha.x) : null, koHp: ko ? ko.hp : null, blasts: ctx.data.blasts || 0 }; },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const p = player();
        p.x = A.jotaro[0]; p.y = A.jotaro[1]; p.facing = 1;
        aSetup(S2, ctx);
      },
      tick: (c, dt) => aTick(S, c, dt),
    });
    for (const a of G.world.stage.actors) if (a.id && (a.id.indexOf('cig') === 0 || a.id === 'sha')) a.remove = true;
    return res;
  };

  // =====================================================================================================================
  // 段 B　康一 + 回音 ACT3：3 FREEZE（b11b_sha）
  // =====================================================================================================================
  const B = { arena: [140, 860], koichi: [520, 160], sha: [330, 156] };
  // 引擎有两种调法：剧情窗口里是 run(S, p, ctx, C)，平时是 run(p, C)（engine/combat.js special）
  async function spFreeze(...args) {
    const C = args[args.length - 1], p = args.length >= 4 ? args[1] : args[0];
    const c = G.world.fight, S = G.S, sha = S.actor('sha');
    if (!c) return;
    c.data.uUsed = true;
    S.hint(null);
    if (sha) {
      p.facing = sha.x >= p.x ? 1 : -1;
      if (Math.abs(sha.x - p.x) > 40) await C.dash(sha.x - p.facing * 26, sha.y, f(8));
    }
    C.stand('punch', { dx: 18 });
    S.sfx('punch_heavy', 1);
    await C.wait(0.15);
    if (sha) {
      c.data.frozen = true;
      sha.mem.hold = true; sha.atk = null; sha.tele = null; sha.state = 'idle';
      sha.play('stuck');
      S.fx('shockwave', { x: sha.x, y: sha.y - 4, r_max: 48, dur: 0.45, colour: '#7af0b8' }, { life: 0.6 });
      S.fx('burst', { x: sha.x, y: sha.y, n: 12, speed: 30, colours: ['#6a6a74', '#3a3a44'], gravity: 120, life: 0.7 });
      S.sfx('wall_slam', 1); S.sfx('rumble', 0.8);
      S.sfxText('咚——！', sha, { dur: 1.2 });
      S.shake(6, 0.5);
      S.mark('b11b_freeze');
    }
    await C.wait(0.9);
    c.end();
  }
  function bSetup(S, c) {
    const d = c.data, p = player(), jt = member('jotaro4');
    heatsInit(S, c);
    d.heatI = 0; d.heatT = 2;
    if (jt) { const xy = at('jotaro_down', [620, 168]); jt.x = xy[0]; jt.y = xy[1]; jt.hold = true; S.pose(jt, 'down'); }
    if (p.setStand && !p.stand) p.setStand('echoes3');
    c.on('hit', (e) => {
      const sha = S.actor('sha');
      d.hitAll = (d.hitAll || 0) + 1; d.lastT = e.t && e.t.id;
      if (!sha || e.t !== sha) return;
      shaOnHit(S, c, e, 0.4);
      if (!c.gauge || d.frozen) return;
      let add = e.slot === 'J3' ? 10 : 5;
      if (sha.mem.pant > 0) add += 5;
      if (c.attempt >= 1 || c.assist) add += 3;
      c.gauge.add(add);
      if (e.slot === 'J3') { S.sfxText('沉！', sha, { dur: 0.6 }); sha.mem.slowT = 1; }
      // 满了就锁住不再掉（不然每秒掉 3，满格只停一帧，按 U 的窗口抓不住）
      if (c.gauge.value >= 100 && !d.full) { d.full = true; S.sfx('meter_full', 0.8); S.hint('重量满了：按 U，3 FREEZE！', 30); }
    });
    S.hint('回音 ACT3：J 打它让它变重（第三下最重）。它去撞热源的时候从后面打！', 8);
  }
  function bTick(S, c, dt) {
    const d = c.data, p = player(), sha = S.actor('sha');
    if (!p || !sha) return;
    // 热源轮着亮，总有一个亮着：坦克去撞热源的时候，就是康一从背后打它的时候（上一个炸掉 1.5 s 后亮下一个）
    if (!d.heats.some((h) => h.key && h.on)) {
      d.heatT -= dt;
      if (d.heatT <= 0) {
        d.heatT = 1.5;
        const hs = d.heats.filter((h) => h.key && h.cd <= 0 && Math.abs(h.x - sha.x) > 120);
        const pool = hs.length ? hs : d.heats.filter((h) => h.key);
        const h = pool[d.heatI++ % pool.length];
        h.cd = 0;
        heatOn(S, c, h, 12);
      }
    }
    heatTick(S, c, dt);
    const w = c.gauge ? c.gauge.value : 0;
    d.shaSpeed = 40 * Math.max(0.3, 1 - w / 140) * (sha.mem.slowT > 0 ? 0.5 : 1);
    if (sha.mem.slowT > 0) sha.mem.slowT -= dt;
    shaTick(S, c, dt, [p], p, 900);
  }
  R.fightB = async function (S) {
    S.hint(null);
    const ko = member('koichi');
    const oldKit = ko ? ko.kit : null;
    if (ko) { ko.kit = K.koichi_act3; ko.maxHp = 100; if (ko.setStand) ko.setStand('echoes3'); }
    const res = await S.fight({
      id: 'b11b_sha', arena: B.arena, lead: 'koichi', swap: false, lockMsg: '承太郎倒下了……只能靠康一', allies: [],
      music: 'battle', after: null, dmgScale: 1.0, losable: true, energy: { start: 0 }, coverage: false,
      gauge: { max: 100, value: 0, label: '重量', color: '#7af0b8', rate: (c) => (c.data.full ? 0 : -3) },
      bench: { mode: 'stay', at: { jotaro4: at('jotaro_down', [620, 168]) } },
      kitOverride: { koichi: { special: { need: 0, title: 'koichi_act3', bg: 'radial', colours: ['#0e5a3a', '#06241a', '#1ec080'],
        window: (c) => !!c.data.full && !c.data.uUsed, prompt: '按 U！', run: spFreeze } } },
      waves: [[{ kit: 'e_sha', cid: 'sha', id: 'sha', name: '枯萎穿心攻击', x: B.sha[0], y: B.sha[1], boss: true, hp: 9999, minHp: 9000 }]],
      testHint: (ctx) => { const p = player(), sh = G.S.actor('sha'); return { weight: ctx.gauge ? Math.round(ctx.gauge.value) : 0, frozen: !!ctx.data.frozen, blasts: ctx.data.blasts || 0, hits: ctx.data.hitAll || 0, dx: sh ? Math.round(sh.x - p.x) : null }; },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const p = player();
        p.x = B.koichi[0]; p.y = B.koichi[1]; p.facing = -1;
        bSetup(S2, ctx);
      },
      tick: (c, dt) => bTick(S, c, dt),
    });
    if (ko) ko.kit = oldKit;
    // 打完把这一段的坦克收掉（不然下一段 S.actor('sha') 会拿到上一段留下的那只）
    for (const a of G.world.stage.actors) if (a.id === 'sha') a.remove = true;
    return res;
  };

  // =====================================================================================================================
  // 段 C　承太郎（带伤）vs 吉良吉影（b11c_kira）
  // =====================================================================================================================
  const Cc = { arena: [300, 820], jotaro: [470, 160], kira: [640, 158], koichi: [400, 168], sha: [560, 150] };
  function coinBomb(S, c, kira) {
    const p = player(), st = G.world.stage;
    const x = G.clamp(p.x + (Math.random() * 24 - 12), c.spec.arena[0] + 10, c.spec.arena[1] - 10), y = G.clamp(p.y, st.yMin, st.yMax);
    kira.play('throw');
    S.sfx('coin', 0.7);
    const coin = T().prop(S, 'coin_bomb', kira.x, kira.y, { id: 'coin' + T().count('coin'), z: 24, frame: 0 });
    if (coin) S.arc(coin, x, y, 24, 0.4, { z1: 0 }).then(() => { if (coin) { coin.frozen = null; coin.hold = false; coin.play('idle'); } }, G.cancelIgnore);
    if (!c.data.coinTold) { c.data.coinTold = true; S.hint('杀手皇后碰过的硬币就是炸弹：红圈里快闪开（K）！', 5); }
    G.combat.hazard({ shape: 'ellipse', x, y, rx: 26, ry: 10, warn: 1.0, dur: 0.1, dmg: 18, push: 22, owner: kira, side: 'enemy', guard: 'normal',
      onActive: () => {
        S.sfx('explosion', 0.8);
        S.fx('explosion', { x, y: y - 8, size: 0.9 }, { life: 0.5 });
        S.shake(3, 0.25);
        if (coin) coin.remove = true;
      } });
  }
  function cSetup(S, c) {
    const d = c.data, p = player(), ko = member('koichi');
    d.coinT = 4; d.goT = 12; d.koichi = ko;
    p.hp = Math.round(p.maxHp * 0.7);
    if (ko) { ko.x = Cc.koichi[0]; ko.y = Cc.koichi[1]; ko.hold = true; S.pose(ko, 'hurt'); }
    let sha = S.actor('sha_stuck');
    if (!sha) sha = S.spawn('sha', Cc.sha[0], Cc.sha[1], { id: 'sha_stuck', facing: -1 });
    S.pose(sha, 'stuck');
    if (!d.halfTold) c.on('hit', (e) => {
      const kira = S.actor('kira');
      if (kira && e.t === kira && kira.hp < kira.maxHp / 2 && !d.halfTold) {
        d.halfTold = true;
        cine(c, async () => { await S.say(R.cid('kira'), '这只手……好重……！那个小鬼的替身还缠着我！', { expr: 'rage', name: '吉良' }); });
      }
      if (kira && e.t === kira && d.kiraGoKoichi) { d.kiraGoKoichi = false; d.goT = 12; }
    });
    S.hint('吉良会去踢倒在地上的康一：挡在中间！　U：时停', 7);
  }
  function cTick(S, c, dt) {
    const d = c.data, kira = S.actor('kira'), ko = d.koichi;
    if (!kira) return;
    const busy = kira.state !== 'idle' && kira.state !== 'walk';
    d.coinT -= dt;
    if (d.coinT <= 0 && !busy && !d.kiraGoKoichi) { d.coinT = kira.hp < kira.maxHp / 2 ? 4.5 : 6; coinBomb(S, c, kira); }
    d.goT -= dt;
    if (d.goT <= 0 && !d.kiraGoKoichi) { d.kiraGoKoichi = true; S.emote(kira, '先收拾那个小鬼。', 1.2); }
    if (d.kiraGoKoichi && ko && Math.abs(kira.x - ko.x) < 22 && Math.abs(kira.y - ko.y) < 10) {
      d.kiraGoKoichi = false; d.goT = 12;
      ko.hp = Math.max(0, ko.hp - 10); ko.flash = 1;
      S.sfx('punch', 0.8); S.sfxText('咚', ko, { dur: 0.5 }); S.shake(2, 0.2);
      if (ko.hp > 0) S.emote(ko, '呜……！', 0.8);
    }
    if (ko) { ko.x = Cc.koichi[0]; ko.y = Cc.koichi[1]; }
  }
  R.fightC = async function (S) {
    S.hint(null);
    const kcid = R.cid('kira'), kq = R.cid('killerqueen');
    const res = await S.fight({
      id: 'b11c_kira', arena: Cc.arena, lead: 'jotaro4', swap: false, lockMsg: '康一动不了了', vip: 'koichi', vipHp: 40,
      music: 'battle', after: null, dmgScale: 1.0, losable: true, energy: { start: 50 }, coverage: false,
      steps: { n: 1, label: '打倒吉良' },
      waves: [[{ kit: 'e_kira', cid: kcid, id: 'kira', name: '吉良吉影', x: Cc.kira[0], y: Cc.kira[1], boss: true, hp: 600, minHp: 1, stand: kq }]],
      testHint: (ctx) => { const k = G.S.actor('kira'), ko = member('koichi'); return { kiraHp: k ? k.hp : null, koHp: ko ? ko.hp : null }; },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const p = player();
        p.x = Cc.jotaro[0]; p.y = Cc.jotaro[1]; p.facing = 1;
        const k = S2.actor('kira');
        if (k && !k.stand && k.setStand) k.setStand(kq);
        cSetup(S2, ctx);
      },
      tick: (c, dt) => cTick(S, c, dt),
      endWhen: (c) => { const k = G.S.actor('kira'); return !!k && k.hp <= 1; },
    });
    const k = S.actor('kira');
    if (k) {
      k.team = 'npc'; k.brain = null; k.moves = []; k.atk = null; k.tele = null; k.state = 'idle'; k.mem.hold = true;
      if (k.stand) k.stand.recall({ instant: true });
    }
    for (const a of G.world.stage.actors) if (a.id && a.id.indexOf('coin') === 0) a.remove = true;
    return res;
  };
})();
