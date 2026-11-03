// 第10章　送电铁塔 / 铁塔与谜：第 15 战 Superfly（仗助 ⇄ 未起隆）、第 16 战 谜（仗助 ⇄ 裕也，分前后两场 S.fight）。
//   剧情节拍在 story/p4_ch10.js；规矩见 第四部/docs/第10章_开发脚本.md 第 3 节、第四部/docs/分章开发约定.md。
//   客串（未起隆、裕也）的招式组也写在这里：只有这一章能操作他们（设计文档 3.4）。
//   未起隆、裕也的正式图集归第9章画：G.P4CH10.cid() 先查正式 cid，没合进来就用本章的 _tmp 临时版。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const R = (G.P4CH10 = {});
  const DMG = 1.1;                       // 第8–10章伤害系数（设计文档 1.2）

  // ======================================================================= cid：正式版优先（第9章交图后自动换过去）
  const has = (cid) => !!(G.D && G.D.chars && G.D.chars[cid]);
  R.cid = {
    mikitaka: () => (has('mikitaka') ? 'mikitaka' : 'mikitaka_tmp'),
    yuya: () => (has('yuya') ? 'yuya' : 'yuya_tmp'),
  };
  // 名牌、替身卡：正式的在别章的 ui 里，没有就用本章画的 _tmp
  const ui = () => (G.D && G.D.ui) || {};
  R.nameKey = (cid) => ((ui().namecards || {})[cid] ? cid : cid + '_tmp');
  R.standKey = (id) => ((ui().standcards || {})[id] ? id : id + '_tmp');

  // 在战斗里插一段演出（和序章 p4_pro_fights.js 的 cine 一样：占住 W.cine，玩家、敌人、战斗 tick 都停）
  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    // 同一帧里接连开两段演出时，后一段不能把前一段的占位当成“原来的”记下来（否则演完以后 W.cine 永远放不开）
    const old = W.cine && W.cine.by === 'p4-ch10' ? null : W.cine;
    W.cine = { by: 'p4-ch10' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  const player = () => G.world.player;
  const member = (cid) => ((G.party && G.party.members) || []).find((a) => a.cid === cid) || null;
  const stun = (e, sec) => { e.atk = null; e.tele = null; e.stunT = sec; e._hurtDur = sec; e.state = 'hurt'; e.stateT = 0; e.play('hurt'); };
  // 一次按键只认一次（剧情自己处理的键：修复的 L+J、客串的 U）
  const pressed = (d, key, name) => {
    const lp = G.input.lastPress(name);
    if (d[key] === undefined) { d[key] = lp; return false; }
    if (lp !== d[key]) { d[key] = lp; return true; }
    return false;
  };

  // ======================================================================= 客串：支仓未起隆（地球风与火）
  //   不能出拳（J 只是比划一下，伤害 1）；U 由战斗自己处理（变磁铁 / 变电线），kit 里不挂必杀，免得走切入
  M.MK_POKE = Object.assign({}, M.SP_J1, { slot: 'J1', stand: null, standSeq: null, dmg: 1, push: 2, energy: 0, accent: '#a0e0e0', reach: [4, 26],
    sfxHit: 'blip', word: null });
  const mkKit = { hp: 100, speed: 66, standId: null, combo: ['MK_POKE', 'MK_POKE', 'MK_POKE'], rush: null,
    guard: { pose: 'guard' }, guardAttack: null, chords: {}, parry: {}, dodge: {}, special: null, explore: { pose: 'point' }, grunt: null };
  K.mikitaka = K.mikitaka || mkKit;
  K.mikitaka_tmp = mkKit;

  // ======================================================================= 客串：喷上裕也（公路之星）
  //   J 公路之星连踢（伤害低）；U 吸养分（能量 100）由战斗自己处理：自己和仗助回血、紧张槽 −40
  const HS = '#ff70a0';
  M.HS_J1 = Object.assign({}, M.SP_J1, { accent: HS, dmg: 6, word: null });
  M.HS_J2 = Object.assign({}, M.SP_J2, { accent: HS, dmg: 6 });
  M.HS_J3 = Object.assign({}, M.SP_J3, { accent: HS, dmg: 11, word: '咚！' });
  M.HS_FIN = Object.assign({}, M.SP_FIN, { accent: HS, dmg: 10, word: '咚!!' });
  const yuKit = (stand) => ({ hp: 100, speed: 70, standId: stand, combo: ['HS_J1', 'HS_J2', 'HS_J3'],
    rush: { tick: f(5), dmg: 2, push: 1, reach: [6, 50], depth: 10, loop: 'ora_loop', word: '咚', fx: 'fists', fist: stand, accent: '#ffc0d8', hitSfx: 'punch', finisher: 'HS_FIN' },
    guard: { pose: 'block' }, guardAttack: null, chords: {}, parry: { effect: 'reflect' }, dodge: {}, special: null, explore: { pose: 'point' }, grunt: null });
  K.yuya = K.yuya || yuKit('highway');
  K.yuya_tmp = yuKit('highway_tmp');

  // =====================================================================================================================
  // 第 15 战 Superfly（b15_superfly）：送电铁塔中层的梁上，仗助 ⇄ 未起隆；丰大 HP 800
  // =====================================================================================================================
  const TW = {
    mid: [83, 237, 42],            // 中层的梁（帐篷、炉子那一层）：段 A、段 C
    arm: [56, 264, -150],          // 第二道横担：段 B
    rivets: [110, 160, 210],       // 中层梁上能打碎的铆钉（x）
    wireOut: [260, -129], wireEnd: [320, -65],
  };
  R.TW = TW;
  // 站到某一道梁上：可走带收成梁上一条（y ±4），镜头竖向卷到梁上方 130 px（铁塔竖向不会自己跟人，docs/第10章_背景.md）
  R.level = (beam) => {
    const st = G.world.stage;
    st.yMin = beam[2] - 4; st.yMax = beam[2] + 4;
    st.camY = G.clamp(beam[2] - 130, -360, 0);
    st.ground = beam[2];
  };
  R.ground = () => { const st = G.world.stage; st.yMin = 142; st.yMax = 176; st.camY = 0; st.ground = 150; };

  // ---- 丰大的招
  M.TY_KICK = { slot: 'enemy', body: 'cmd', stand: null, warn: { tier: 'W1', dur: 0.45 }, dur: 0.45 + f(26), active: [0.45, 0.45 + f(6)],
    melee: true, from: 'body', reach: [0, 40], depth: 8, dmg: 10, push: 16, guard: 'normal', sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light', accent: '#8cd88c' };
  M.TY_BOLTS = { slot: 'enemy', body: 'cmd', stand: null, warn: { tier: 'W4', dur: 0.5 }, dur: 0.9, active: [0.5, 0.53], melee: false, fireAt: [0.5],
    shot: { kind: 'bullet', n: 3, spread: 10, speed: 140, dmg: 7, life: 1.8, hitR: [3, 5, 18], colour: '#c8ccd8' }, sfx: 'metal_crunch', sfxVol: 0.5 };
  // 铁架里伸出钢条横扫：W2 预警 0.6 s，够得远（90 px）
  M.TY_BAR = { slot: 'enemy', body: 'idle', stand: null, warn: { tier: 'W2', dur: 0.6 }, dur: 0.6 + f(30), active: [0.6, 0.6 + f(8)],
    melee: true, from: 'body', reach: [0, 90], depth: 10, dmg: 12, push: 22, guard: 'normal', sfx: 'metal_crunch', sfxHit: 'punch_heavy', fxHit: 'heavy',
    accent: '#c8ccd8', shake: [2, f(10)], word: '锵！' };

  K.e_toyohiro = {
    hp: 800, speed: 50, moves: ['TY_KICK', 'TY_BOLTS', 'TY_BAR'], koStyle: 'none', idle: 'idle', armor: false,
    // 在铁架里：打不动，力气从铁架弹回来（打的人自己挨）
    dmgMul: (t) => (t.mem.merged ? 0 : 1),
    onHitBy(t, att, m) {
      if (!t.mem.merged || !att || att.team === 'enemy') return null;
      const now = G.clk.world;
      if (now - (t.mem.reflT || -9) < 0.3) return null;
      t.mem.reflT = now;
      const dmg = Math.min(12, Math.max(3, Math.round((m.dmg || 4) * 0.8)));
      G.defer(0.05, () => {
        if (G.world.fight && att.hp > 0) G.combat.hit(null, att, { slot: 'enemy', dmg, push: 8, guard: 'none', sfxHit: 'metal_crunch', fxHit: 'light', accent: '#8cd88c' });
      });
      G.S.sfxText('弹回来了！', att, { dur: 0.6 });
      const c = G.world.fight;
      if (c && c.data) c.data.reflects = (c.data.reflects || 0) + 1;
      return null;
    },
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player, st = G.world.stage;
      if (!p || !st || m.hold || d.phase === 'B') return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      // 钻进铁架 / 出来：段 C 待在里面更久
      const inT = d.phase === 'C' ? 4 : 3, outT = d.phase === 'C' ? 3.5 : 6 + Math.random() * 2;
      m.mt = (m.mt || 0) + dt;
      if (!m.merged && m.mt >= (m.outFor || outT)) { R.merge(e, true); m.mt = 0; m.inFor = inT; }
      else if (m.merged && m.mt >= (m.inFor || inT)) { R.merge(e, false); m.mt = 0; m.outFor = outT; }
      e.facing = p.x > e.x ? 1 : -1;
      m.gap = (m.gap == null ? 1.6 : m.gap) - dt;
      if (m.merged) {
        // 在铁架里顺着梁慢慢挪，隔一会儿扔一把螺栓
        G.combat.walkTo(e, G.clamp(p.x + (e.x < p.x ? -70 : 70), st.x0 + 6, st.x1 - 6), e.y, dt, 30);
        if (m.gap <= 0 && G.combat.tokens() < 2) { G.AI.tele(e, 'TY_BOLTS'); m.gap = 1.6; }
        return true;
      }
      const dx = Math.abs(p.x - e.x);
      if (dx > 34 || Math.abs(p.y - e.y) > 4) G.AI.approach(e, p, 28, dt);
      else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
      if (m.gap > 0 || G.combat.tokens() >= 2) return true;
      const pick = dx < 40 ? (Math.random() < 0.6 ? 'TY_KICK' : 'TY_BAR') : dx < 90 ? 'TY_BAR' : 'TY_BOLTS';
      G.AI.tele(e, pick);
      m.gap = 1.5 + Math.random() * 0.8;
      return true;
    },
  };
  R.merge = (e, on) => {
    e.mem.merged = on;
    e.alpha = on ? 0.45 : 1;
    e.tint = on ? { color: '#8a9098', k: 0.7 } : null;
    G.S.sfx(on ? 'metal_crunch' : 'whoosh', 0.5);
    if (on) G.S.sfxText('融进铁架', e, { dur: 0.6 });
  };

  // ---- 铆钉：J3 / 终结打碎，按住 L 按 J 修回去（碎铁顺着铁架飞回原处，把铁架里的丰大撞出来）
  function rivetsSetup(S, d) {
    for (const a of G.world.stage.actors) if (a.id && a.id.indexOf('tw_rv') === 0) a.remove = true;
    d.rivets = TW.rivets.map((x, i) => ({ x, y: TW.mid[2] - 2, broken: false, a: T().prop(S, 'rivet', x, TW.mid[2] - 2, { id: 'tw_rv' + i, frame: 0 }) }));
  }
  function rivetBreak(S, c, p) {
    const d = c.data, a = p.atk, slot = a && a.slot;
    if (!a || (slot !== 'J3' && slot !== 'fin') || a === d.brkAtk || p.atkT < a.active[0] || p.atkT > a.active[1] + f(2)) return;
    for (const r of d.rivets || []) {
      const dx = (r.x - p.x) * p.facing;
      if (r.broken || dx < -4 || dx > 50 || Math.abs(r.y - p.y) > 10) continue;
      d.brkAtk = a;
      r.broken = true;
      T().setFrame(r.a, 1);
      S.sfx('metal_crunch', 0.8);
      S.fx('burst', { x: r.x, y: r.y - 4, n: 8, speed: 30, colours: ['#c8ccd8', '#6a7080'], gravity: 120, life: 0.6 });
      if (!d.rivetTold) { d.rivetTold = true; S.hint('铆钉碎了。按住 L 再按 J：把碎铁修回去，顺着铁架撞他！', 6); }
      break;
    }
  }
  async function rivetFix(S, c) {
    const d = c.data, p = player(), ty = S.actor('toyohiro');
    const broken = (d.rivets || []).filter((r) => r.broken);
    if (!broken.length) { S.emote(p, '没有碎掉的东西可修……', 1); return; }
    S.standAct(p, 'reach', { dx: 16, z: 6, dur: 0.6 });
    S.sfx('whoosh', 0.7);
    for (const r of broken) { r.broken = false; T().setFrame(r.a, 0); P4().fixGlow(S, r.x, r.y - 6, { n: 5 }); }
    if (!ty || ty.hp <= 1) return;
    // 他在铁架里：修回去的碎铁顺着铁架打到他身上；在外面：离铆钉 50 px 以内才挨得到
    const near = broken.some((r) => Math.abs(r.x - ty.x) < 50);
    if (!ty.mem.merged && !near) return;
    if (ty.mem.merged) R.merge(ty, false);
    ty.mem.mt = 0;
    const dmg = (d.phase === 'C' ? 40 : 30) * broken.length;
    G.combat.hit(p, ty, { slot: 'special', dmg: Math.min(dmg, 90), push: 18, guard: 'none', energy: 6, sfxHit: 'punch_heavy', fxHit: 'heavy', accent: '#ffb0d8', word: '锵！！' });
    stun(ty, 1.5);
    S.shake(3, 0.3);
    if (!d.fixDone) { d.fixDone = true; S.mark('ch10_rivet_fix'); }
    d.fixHits = (d.fixHits || 0) + 1;
  }

  // ---- 段 A → 段 B：仗助的腿被铁架包住，丰大顺着电线逃；强制换成未起隆
  async function toPhaseB(S, c) {
    const d = c.data, ty = S.actor('toyohiro'), js = member('josuke'), mk = member(R.cid.mikitaka());
    d.phase = 'B';
    S.hint(null);
    if (ty) { R.merge(ty, false); ty.atk = null; ty.tele = null; ty.state = 'idle'; ty.play('idle'); }
    S.sfx('metal_crunch', 1); S.shake(3, 0.5);
    if (js) { js.atk = null; js.state = 'idle'; js.play('hurt'); js.tint = { color: '#8a9098', k: 0.5 }; }
    S.sfxText('咔咔咔', js, { dur: 1 });
    await S.say('josuke', '腿……被铁架包住了！', { expr: 'shock' });
    await S.say('toyohiro', '最后一个人出不去！现在塔里有你，我就能下去了！', { expr: 'smile' });
    S.mark('ch10_josuke_stuck');
    // 镜头卷到上面的横担：未起隆追上去，丰大往电线那头爬
    c.setLead(mk.cid);
    G.party.locked = true;
    if (js) { js.team = 'npc'; js.visible = false; }
    R.level(TW.arm);
    G.world.stage.x0 = TW.arm[0] + 4; G.world.stage.x1 = TW.arm[1] - 2;
    Object.assign(mk, { x: TW.arm[0] + 20, y: TW.arm[2], facing: 1, state: 'idle', visible: true });
    if (ty) { Object.assign(ty, { x: TW.wireOut[0], y: TW.arm[2], facing: 1, untargetable: true }); ty.play('walk'); }
    G.world.snapCamera();
    await S.say(mk.cid, '仗助先生！我去把他拉回来！');
    d.slideT = 0; d.slideMax = c.assist ? 16 : 12;
    G.hud.timer = { label: '丰大逃走：', until: c.t + d.slideMax, t: c.t, left: d.slideMax };
    S.hint('跑到横担右头（电线那边），按 U：未起隆变成的东西能把他拉回来', 8);
  }
  function slideTick(S, c, dt) {
    const d = c.data, ty = S.actor('toyohiro'), p = player();
    d.slideT += dt;
    // 丰大顺着电线往右下滑：wireOut → wireEnd
    const u = Math.min(1, d.slideT / d.slideMax);
    if (ty) { ty.x = G.lerp(TW.wireOut[0], TW.wireEnd[0] - 8, u); ty.y = TW.arm[2]; ty.z = Math.round(G.lerp(21, -60, u)); }
    if (u >= 1) { c.fail('丰大顺着电线逃走了……仗助被留在了塔里。'); return; }
    if (pressed(d, 'lpU', 'special') && p && p.cid === R.cid.mikitaka()) {
      if (p.x < 232) { S.emote(p, '还够不着电线……再往右！', 1); return; }
      d.swing = true;
      cine(c, () => cableSwing(S, c));
    }
  }
  async function cableSwing(S, c) {
    const d = c.data, ty = S.actor('toyohiro'), mk = player(), js = member('josuke');
    G.hud.timer = null;
    S.hint(null);
    await S.say(mk.cid, '我刚才就已经变成这根电线了！', { expr: 'smile' });
    mk.visible = false;
    S.sfx('whoosh', 1);
    S.sfxText('嗡——', { wx: TW.wireOut[0], wy: TW.arm[2], wz: 30 }, { dur: 0.8 });
    if (ty) {
      ty.z = 0;
      await S.arc(ty, 160, TW.arm[2], 50, 0.7, { anim: 'hurt', spin: 8 });
      ty.rot = 0;
    }
    S.sfx('metal_crunch', 1); S.shake(4, 0.4);
    S.mark('ch10_cable_swing');
    await S.say('toyohiro', '电线……是你变的？！', { expr: 'shock' });
    // 丰大顺手一钉，把未起隆变的那段电线夹在铁架上（不画钉子扎进人，只有一声）
    S.sfx('guard', 1);
    S.sfxText('锵', { wx: 236, wy: TW.arm[2], wz: 20 }, { dur: 0.8 });
    await S.say(mk.cid, '……我被夹住了。仗助先生，剩下的拜托了。', { name: '未起隆（电线）' });
    // 回到中层：仗助的腿松开了
    R.level(TW.mid);
    G.world.stage.x0 = TW.mid[0] + 4; G.world.stage.x1 = TW.mid[1] - 4;
    if (js) { js.visible = true; js.tint = null; js.team = 'npc'; }
    c.setLead('josuke');
    const p = player();
    Object.assign(p, { x: 110, y: TW.mid[2], facing: 1, state: 'idle' });
    mk.team = 'npc'; mk.visible = false;
    if (ty) Object.assign(ty, { x: 200, y: TW.mid[2], z: 0, untargetable: false, facing: -1, state: 'idle' });
    if (ty) { ty.mem.mt = 0; ty.mem.gap = 1.2; }
    G.world.snapCamera();
    await S.say('josuke', '……腿松开了。轮到我了，丰大。', { expr: 'rage' });
    await S.say('toyohiro', '你打不中的！你的拳头会被铁塔弹回去！', { expr: 'rage' });
    S.hint('他躲在铁架里：J3 打碎铆钉，按住 L 按 J 修回去。被弹回去的力气会打回他身上！', 8);
    d.phase = 'C';
  }

  function superflyTick(S, c, dt) {
    const d = c.data, p = player(), ty = S.actor('toyohiro');
    if (!p || !ty) return;
    if (d.phase === 'B') { if (!d.swing) slideTick(S, c, dt); return; }
    if (p.cid === 'josuke') rivetBreak(S, c, p);
    // 按住 L 按 J：修复（只有仗助会修）
    if (pressed(d, 'lpJ', 'attack') && p.cid === 'josuke' && p.state === 'guard') { cine(c, () => rivetFix(S, c)); return; }
    // 未起隆的 U：变成磁铁，把铁架里的丰大吸出来（冷却 6 s）
    if (pressed(d, 'lpU', 'special') && p.cid === R.cid.mikitaka()) {
      if (ctxCd(d, 'mag', 6)) {
        const near = Math.abs(ty.x - p.x) < 130;
        cine(c, async () => {
          const mg = T().prop(S, 'magnet', p.x + p.facing * 10, p.y + 0.5, { id: 'mk_mag', z: 14 });
          p.visible = false;
          S.sfx('blip', 0.8); S.sfxText('磁铁！', mg, { dur: 0.7 });
          await S.wait(0.35);
          if (ty.mem.merged && near) {
            R.merge(ty, false); ty.mem.mt = 0;
            await S.animate(0.3, (k) => { ty.x = G.lerp(ty.x, p.x + p.facing * 24, k * 0.5); });
            stun(ty, 2);
            S.sfx('metal_crunch', 0.8);
            if (!d.magTold) { d.magTold = true; S.hint('丰大被吸出来了！换回仗助（Q）趁现在打！', 5); }
          } else S.emote(p, ty.mem.merged ? '太远了……' : '他没躲在铁架里。', 1);
          await S.wait(0.3);
          mg.remove = true; p.visible = true;
        });
      } else S.emote(p, '变身要歇一会儿……', 0.8);
    }
    if (d.phase === 'A' && ty.hp <= ty.maxHp * 0.4 && !d.toB) { d.toB = true; cine(c, () => toPhaseB(S, c)); return; }
    if (d.phase === 'C' && ty.hp <= 1 && !d.won) { d.won = true; S.mark('ch10_superfly_win'); }
    // 打铁塔被弹回来三次还没修过：提示一次
    if ((d.reflects || 0) >= 3 && !d.reflTold && !d.fixDone) { d.reflTold = true; S.hint('打铁塔会被弹回来！J3 先打碎梁上的铆钉，再按住 L 按 J 修复', 7); }
  }
  function ctxCd(d, k, sec) {
    const now = G.clk.world;
    if (now - (d['cd_' + k] || -99) < sec) return false;
    d['cd_' + k] = now;
    return true;
  }
  R.fightSuperfly = async function (S) {
    S.hint(null);
    const mk = R.cid.mikitaka();
    const res = await S.fight({
      id: 'b15_superfly', arena: [TW.mid[0] + 4, TW.mid[1] - 4], lead: 'josuke', swap: true, allies: [mk],
      music: 'battle', after: null, dmgScale: DMG, losable: true, energy: { start: 0 },
      waves: [[{ kit: 'e_toyohiro', actor: 'toyohiro', cid: 'toyohiro', id: 'toyohiro', name: '钢田一丰大', x: 200, y: TW.mid[2], boss: true, hp: 800, minHp: 1 }]],
      testHint: (ctx) => {
        const ty = G.S.actor('toyohiro'), d = ctx.data;
        return { phase: d.phase, hp: ty ? ty.hp : null, merged: !!(ty && ty.mem.merged), fixHits: d.fixHits || 0, reflects: d.reflects || 0, slide: d.slideT ? Math.round(d.slideT) : 0 };
      },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const d = ctx.data;
        d.phase = 'A';
        R.level(TW.mid);
        const p = player(), m2 = member(mk), js = member('josuke'), ty = S2.actor('toyohiro');
        Object.assign(p, { x: 110, y: TW.mid[2], facing: 1 });
        if (js) { js.tint = null; js.visible = true; }
        if (m2) Object.assign(m2, { x: 96, y: TW.mid[2] + 2, visible: true });
        if (ty) { ty.mem.merged = false; ty.alpha = 1; ty.tint = null; ty.mem.mt = 0; ty.z = 0; ty.rot = 0; }
        rivetsSetup(S2, d);
        G.world.snapCamera();
        S2.hint('丰大会钻进铁架：那时候打他会被弹回来。Q 换未起隆，U 变磁铁能把他吸出来', 7);
      },
      tick: (c, dt) => superflyTick(S, c, dt),
      endWhen: (c) => !!c.data.won,
    });
    for (const a of G.world.stage.actors) if (a.id && (a.id.indexOf('tw_rv') === 0 || a.id === 'mk_mag')) a.remove = true;
    const ty = S.actor('toyohiro');
    if (ty) { ty.team = 'npc'; ty.brain = null; ty.atk = null; ty.tele = null; ty.alpha = 1; ty.tint = null; ty.mem.merged = false; ty.state = 'idle'; ty.play('down'); }
    const js = member('josuke');
    if (js) js.tint = null;
    G.hud.timer = null;
    return res;
  };

  // =====================================================================================================================
  // 第 16 战 谜：前半 b16_enigma（仗助 ⇄ 裕也，紧张槽）→ 剧情：仗助变成纸 → 后半 b16_enigma_b（裕也揣纸、碎纸机；仗助出来收尾）
  // =====================================================================================================================
  const MH = { arena: [20, 378], shred: [424, 150], feed: [378, 150], bin: [424, 122], papers: [[150, 150], [300, 160]] };
  R.MH = MH;
  M.TE_SHURIKEN = { slot: 'enemy', body: 'point', stand: null, warn: { tier: 'W4', dur: 0.45 }, dur: 0.8, active: [0.45, 0.48], melee: false, fireAt: [0.45],
    shot: { kind: 'bullet', n: 3, spread: 12, speed: 170, dmg: 6, life: 1.6, hitR: [3, 5, 18], colour: '#fbf8ef' }, sfx: 'whoosh' };
  // 陷阱纸：打开往前一扔，纸上画的东西冒出来（火往前滚、纸蝎子爬、地上一道电光）
  const trap = (kind, shot) => ({ slot: 'enemy', body: 'point', stand: null, warn: { tier: 'W4', dur: 0.6 }, dur: 1.0, active: [0.6, 0.63], melee: false,
    fireAt: [0.6], shot, sfx: 'card_flip', trap: kind });
  M.TE_FIRE = trap(0, { kind: 'bullet', n: 1, speed: 90, dmg: 9, life: 2.2, hitR: [6, 6, 20], colour: '#ff9a2a' });
  M.TE_SCORP = trap(1, { kind: 'bullet', n: 3, spread: 18, speed: 60, dmg: 5, life: 3, hitR: [4, 4, 8], colour: '#5a3020' });
  M.TE_SPARK = trap(2, { kind: 'bullet', n: 1, speed: 200, dmg: 8, life: 1.4, hitR: [4, 8, 10], colour: '#fff6a0' });
  const TRAP_WORD = ['火！', '蝎子！', '电！'];
  K.e_terunosuke = {
    hp: 800, speed: 56, moves: ['TE_SHURIKEN', 'TE_FIRE', 'TE_SCORP', 'TE_SPARK'], koStyle: 'none', idle: 'idle',
    // 平时是“纸做的”：挨打只掉 20%；闭上一只眼（害怕）的时候掉全血（段 3 一直在怕）
    dmgMul: (t) => (t.mem.fear || t.mem.terrified ? 1 : 0.2),
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player, st = G.world.stage;
      if (!p || !st || m.hold) return true;
      // 恐惧的小动作：每 5–7 s 闭一次眼（2 s）；前 1 s 让裕也的鼻子先闻到
      if (!m.terrified) {
        m.fearIn = (m.fearIn == null ? 4 : m.fearIn) - dt;
        if (!m.fear && m.fearIn <= 1 && !m.sniffed) { m.sniffed = true; d.sniffT = G.clk.world; }
        if (!m.fear && m.fearIn <= 0) { m.fear = true; m.fearLeft = 2.5; e.emote = { text: '（闭上一只眼）', t: 2, color: '#ffe0f0' }; }
        if (m.fear) { m.fearLeft -= dt; if (m.fearLeft <= 0) { m.fear = false; m.sniffed = false; m.fearIn = 4 + Math.random() * 2; } }
      }
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      e.facing = p.x > e.x ? 1 : -1;
      // 闭眼的那 2.5 s 他僵在原地（怕得动不了）：这就是打他的机会
      if (m.fear && !m.terrified) { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); return true; }
      // 拉开 80 px：离太近就往后跳
      const dx = Math.abs(p.x - e.x);
      const keep = m.terrified ? 50 : 80;
      if (dx < keep - 20 || dx > keep + 30 || Math.abs(p.y - e.y) > 6) G.combat.walkTo(e, G.clamp(p.x + (e.x < p.x ? -keep : keep), st.x0 + 10, st.x1 - 10), p.y, dt, e.speed);
      else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
      m.gap = (m.gap == null ? 1.6 : m.gap) - dt;
      if (m.gap > 0 || G.combat.tokens() >= 2 || m.fear) return true;
      const r = Math.random();
      const id = r < 0.35 ? 'TE_SHURIKEN' : r < 0.6 ? 'TE_FIRE' : r < 0.8 ? 'TE_SCORP' : 'TE_SPARK';
      G.AI.tele(e, id);
      const mv = M[id];
      if (mv.trap != null) {
        // 陷阱纸打开的那一下：纸上画的东西冒出来（道具一闪），紧张 +12
        G.defer(0.55, () => {
          if (!G.world.fight) return;
          const pr = T().prop(G.S, 'paper_trap', e.x + e.facing * 14, e.y + 0.5, { id: 'te_trap', frame: mv.trap, z: 6 });
          G.S.sfxText(TRAP_WORD[mv.trap], pr, { dur: 0.6 });
          G.defer(0.6, () => { pr.remove = true; });
          const c = G.world.fight;
          if (c && c.gauge && player() && player().cid === 'josuke' && c.data.part === 1) c.gauge.add(12);
        });
      }
      m.gap = m.terrified ? 2.4 : 1.8 + Math.random() * 0.8;
      return true;
    },
  };
  // 裕也的鼻子：小动作出现前 1 s，辉之辅头顶闪一下粉色的「嗅」（裕也在场才有）
  let sniffH = null;
  function sniffOverlay() {
    if (sniffH) sniffH.close();
    sniffH = P4().overlay((g) => {
      const c = G.world.fight, te = G.S.actor('terunosuke');
      if (!c || !te || !G.cam || !G.cam.w2u || !c.data.sniffT) return;
      if (!member(R.cid.yuya()) || member(R.cid.yuya()).visible === false) return;
      const age = G.clk.world - c.data.sniffT;
      if (age < 0 || age > 1.0) return;
      const pt = G.cam.w2u(te.x, te.headY() - 14, 0);
      const on = Math.floor(age * 8) % 2 === 0;
      if (!on) return;
      g.fillStyle = '#ff70a0';
      g.fillRect(Math.round(pt.x) - 13, Math.round(pt.y) - 22, 26, 18);
      P4().text(g, '嗅', Math.round(pt.x), Math.round(pt.y) - 20, '#ffffff', 12, 'center', '#6a1a3a');
    }, { z: 2 });
  }
  R.closeSniff = () => { if (sniffH) { sniffH.close(); sniffH = null; } };

  // 裕也的 U：吸养分（能量 100）——自己和仗助各回 30，紧张 −40
  function yuyaHeal(S, c, p) {
    if (p.energy < 100) { S.emote(p, '能量还不够……', 0.8); return; }
    p.energy = 0;
    cine(c, async () => {
      const hs = p.stand;
      if (hs) S.standAct(p, 'reach', { dx: 18, z: 4, dur: 0.8 });
      S.sfx('sparkle', 0.8);
      S.sfxText('吸养分', p, { dur: 0.8 });
      for (const a of [p, member('josuke')]) if (a && a.visible !== false) { a.hp = Math.min(a.maxHp, a.hp + 30); P4().fixGlow(S, a.x, a.y - 16, { n: 4 }); }
      if (c.gauge) c.gauge.add(-40);
      await S.wait(0.6);
    });
  }
  function hitFear(S, c) {
    c.on('hit', (e) => {
      const te = S.actor('terunosuke'), p = player();
      if (!te) return;
      if (e.t === te && te.mem.fear && !te.mem.terrified) {
        if (!c.data.winkHit) { c.data.winkHit = true; S.mark('ch10_wink_hit'); S.hint('他闭眼（害怕）的时候才打得疼！裕也会先闻到', 5); }
        if (!(te.stunT > 0)) stun(te, 0.8);
      }
      if (e.t === p && c.gauge && e.dmg > 0) c.gauge.add(c.data.part === 1 ? (p.cid === 'josuke' ? 8 : 0) : 10);
    });
  }

  // ---- 前半：仗助 ⇄ 裕也，紧张槽满 = 仗助咬嘴唇变成纸 = 失败；辉之辅 HP ≤ 55% → 剧情
  R.fightEnigmaA = async function (S) {
    S.hint(null);
    const yu = R.cid.yuya();
    sniffOverlay();
    const res = await S.fight({
      id: 'b16_enigma', arena: MH.arena, lead: 'josuke', swap: true, allies: [yu],
      music: 'battle', after: null, dmgScale: DMG, losable: true, energy: { start: 0 },
      gauge: { max: 100, value: 0, label: '紧张', color: '#ff9ac0', rate: (c) => (player() && player().cid === 'josuke' ? -2 : -3),
        onFull: (c) => { c.data.bit = true; } },
      waves: [[{ kit: 'e_terunosuke', actor: 'terunosuke', cid: 'terunosuke', id: 'terunosuke', name: '宫本辉之辅', x: 260, y: 156, boss: true, hp: 800, minHp: 1 }]],
      testHint: (ctx) => {
        const te = G.S.actor('terunosuke'), d = ctx.data;
        return { hp: te ? te.hp : null, fear: !!(te && te.mem.fear), tension: ctx.gauge ? Math.round(ctx.gauge.value) : null, winkHit: !!d.winkHit };
      },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        ctx.data.part = 1;
        const te = S2.actor('terunosuke');
        if (te) { te.mem.fear = false; te.mem.fearIn = 3; te.mem.terrified = false; }
        hitFear(S2, ctx);
        S2.hint('他平时像纸一样打不疼。闭上一只眼（害怕）的时候才是机会！紧张槽满了仗助就会变成纸', 8);
      },
      tick: (c, dt) => {
        const p = player(), te = S.actor('terunosuke');
        if (!p || !te) return;
        if (pressed(c.data, 'lpU', 'special') && p.cid === yu) { yuyaHeal(S, c, p); return; }
        if (c.data.bit || (c.gauge && c.gauge.value >= c.gauge.max)) { c.data.bit = false; c.fail('仗助咬住了嘴唇——「唰」，他变成了一张纸。'); return; }
        if (te.hp <= te.maxHp * 0.55) c.data.half = true;
      },
      endWhen: (c) => !!c.data.half,
    });
    R.closeSniff();
    return res;
  };

  // ---- 后半：段 2 裕也揣纸（碎纸机开着，裕也的紧张槽涨）→ 裕也变成纸，夹着的两张纸撑开 → 段 3 仗助收尾
  function papersSetup(S, d) {
    for (const a of G.world.stage.actors) if (a.id && a.id.indexOf('mh_pp') === 0) a.remove = true;
    d.papers = MH.papers.map((xy, i) => ({ i, x: xy[0], y: xy[1], held: false, a: T().prop(S, 'paper', xy[0], xy[1], { id: 'mh_pp' + i, frame: i === 0 ? 4 : 2, z: 16 }) }));
    d.feedT = 3;
  }
  function papersTick(S, c, dt) {
    const d = c.data, p = player(), te = S.actor('terunosuke');
    // 两张纸慢慢往碎纸机那边飘（他一直在往进纸台扇风）——裕也得赶在前面揣起来
    for (const pp of d.papers || []) {
      if (pp.held) { pp.a.x = p.x - p.facing * 4; pp.a.y = p.y + 0.5; pp.a.z = 22; continue; }
      pp.x += dt * 6; pp.a.x = pp.x; pp.a.z = 14 + Math.round(Math.sin(G.clk.world * 3 + pp.i) * 4);
      if (pp.x >= MH.feed[0] - 6) { c.fail('纸被卷进了碎纸机……'); return; }
      const near = Math.abs(pp.x - p.x) < 20 && Math.abs(pp.y - p.y) < 14;
      if (near && !d.paperHint) { d.paperHint = true; S.hint('按 E：把纸揣进怀里', 3); }
      if (near && G.input.hit('ok')) {
        G.input.consume('ok');
        pp.held = true;
        S.sfx('pop', 0.8);
        if (d.papers.every((q) => q.held)) { S.mark('ch10_papers_held'); S.hint('两张纸叠在一起揣好了。……紧张槽也快满了', 5); }
      }
    }
    // 辉之辅隔一会儿往进纸台扔一张别的纸：碎纸机「咔咔」地响，紧张 +6
    d.feedT -= dt;
    if (d.feedT <= 0 && te) {
      d.feedT = 5;
      S.sfx('metal_crunch', 0.5);
      S.sfxText('咔咔咔', { wx: MH.shred[0], wy: MH.shred[1], wz: 50 }, { dur: 0.7 });
      if (c.gauge) c.gauge.add(6);
    }
  }
  async function yuyaPaper(S, c) {
    const d = c.data, p = player(), js = member('josuke'), te = S.actor('terunosuke');
    S.hint(null);
    await S.say(p.cid, '……可恶，腿在抖。我也开始怕了吗。', { expr: 'shock' });
    S.sfx('whoosh', 0.9); S.flash(0.2, 0.7);
    S.sfxText('唰', p, { dur: 0.8 });
    p.visible = false;
    const pyx = { x: p.x, y: p.y };
    const pp = T().prop(S, 'paper', pyx.x, pyx.y + 0.5, { id: 'mh_yuya', frame: 0, z: 2 });
    for (const q of d.papers || []) q.a.remove = true;
    S.mark('ch10_yuya_paper');
    await S.say('terunosuke', '哈哈，三张都到手了！', { expr: 'smile' });
    // 裕也一变成纸，揣在他怀里叠着的两张纸被撑开：仗助和康一出来了
    S.sfx('card_flip', 1); S.sfx('sparkle', 0.8);
    S.flash(0.3, 0.8, '#fff8e0');
    await S.wait(0.3);
    if (js) { Object.assign(js, { x: G.clamp(pyx.x - 20, 30, 360), y: pyx.y, visible: true, state: 'idle' }); }
    const ko = S.actor('koichi_mh') || S.spawn('koichi', G.clamp(pyx.x + 24, 30, 360), pyx.y + 4, { id: 'koichi_mh', facing: -1 });
    ko.visible = true;
    c.setLead('josuke');
    p.team = 'npc';
    G.party.locked = true;
    S.mark('ch10_papers_open');
    if (te) { te.mem.terrified = true; te.mem.fear = true; te.emote = { text: '（两只眼都闭上了）', t: 2, color: '#ffe0f0' }; }
    await S.say('terunosuke', '怎、怎么会……我明明把你们折起来了！', { expr: 'shock' });
    await S.say('josuke', '裕也把我们两张纸叠着揣在怀里。他一变，我们就被撑开了。', { expr: 'rage' });
    await S.say('koichi', '仗助君……裕也君他……', { expr: 'shock' });
    await S.say('josuke', '我会把他放出来的。先收拾你，辉之辅。', { expr: 'rage' });
    d.part = 3;
    pp.frame = 0;
    if (c.gauge) c.gauge.value = 0;
    S.hint('他吓坏了，现在打得疼！打到底，再按住 L 按 J', 6);
  }
  async function finishBook(S, c) {
    const d = c.data, p = player(), te = S.actor('terunosuke');
    S.hint(null);
    te.mem.hold = true; te.atk = null; te.tele = null;
    const ok = await S.mash({ need: 10, time: 2.4, label: '连按 J！DORARARA！' });
    void ok;
    await S.summon(p, { dur: 0.08, rise: 4 });
    S.standAct(p, 'rush', { dx: 18, z: 4, hold: true, jitter: 1 });
    for (let i = 0; i < 8; i++) G.defer(i * 0.08, () => S.sfx('punch', 0.5));
    S.sfxText('DORARARA', te, { dur: 0.8 });
    te.play('hurt');
    S.shake(3, 0.7);
    await S.wait(0.7);
    S.standAct(p, 'punch', { dx: 22, z: 4, dur: 0.5 });
    S.sfx('punch_heavy', 1);
    S.sfxText('DORA!!', te, { dur: 0.9 });
    await S.arc(te, MH.feed[0] - 4, 150, 24, 0.45, { anim: 'hurt' });
    S.pose(te, 'down');
    S.recall(p);
    S.state('shred', 1);
    await S.say('terunosuke', '碎、碎纸机还开着……！', { expr: 'shock' });
    S.hint('按住 L 按 J：把他和碎纸一起修好', 10);
    d.needFix = true;
  }
  async function bookFix(S, c) {
    const d = c.data, p = player(), te = S.actor('terunosuke');
    d.needFix = false;
    S.hint(null);
    S.face(p, 1);
    await S.summon(p, { dur: 0.1, rise: 4 });
    S.standAct(p, 'reach', { dx: 20, z: 4, dur: 1.2 });
    // 碎纸机里的纸条倒飞回来，绕着他转一圈，合成一本书
    S.sfx('whoosh', 0.9);
    for (let i = 0; i < 10; i++) {
      G.defer(i * 0.06, () => {
        const pr = T().prop(S, 'paper', MH.bin[0] - 10 + (i % 4) * 6, 150, { id: 'mh_strip' + i, frame: 0, z: 30 + (i % 3) * 8 });
        S.arc(pr, te.x, te.y, 20, 0.4, { spin: 6 }).then(() => { pr.remove = true; }, G.cancelIgnore);
      });
    }
    P4().fixGlow(S, te.x, te.y - 10, { n: 12, r: 20, life: 1.2 });
    await S.wait(0.9);
    S.flash(0.6, 1, '#ffffff');
    S.sfx('sparkle', 1);
    te.visible = false;
    T().prop(S, 'enigma_book', te.x, te.y, { id: 'mh_book', frame: 0 });
    S.recall(p);
    S.mark('ch10_book');
    await S.wait(0.6);
    d.won = true;
  }
  R.fightEnigmaB = async function (S) {
    S.hint(null);
    const yu = R.cid.yuya();
    sniffOverlay();
    const res = await S.fight({
      id: 'b16_enigma_b', arena: MH.arena, lead: yu, swap: false, lockMsg: '仗助在纸里……只能靠裕也了', allies: [],
      music: 'battle', after: null, dmgScale: DMG, losable: true, energy: { start: 0 }, bench: { mode: 'hide' },
      gauge: { max: 100, value: 20, label: '紧张', color: '#ff9ac0', rate: (c) => (c.data.part === 2 ? 4 : 0), onFull: (c) => { c.data.full = true; } },
      waves: [[{ kit: 'e_terunosuke', actor: 'terunosuke', cid: 'terunosuke', id: 'terunosuke', name: '宫本辉之辅', x: 300, y: 156, boss: true, hp: 800, minHp: 1 }]],
      testHint: (ctx) => {
        const te = G.S.actor('terunosuke'), d = ctx.data;
        return { part: d.part, hp: te ? te.hp : null, te: te ? [Math.round(te.x), Math.round(te.y), te.state, !!te.mem.hold, te.visible] : null, held: (d.papers || []).filter((q) => q.held).length, tension: ctx.gauge ? Math.round(ctx.gauge.value) : null, needFix: !!d.needFix };
      },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const d = ctx.data;
        d.part = 2;
        S2.state('shred', 1);
        const te = S2.actor('terunosuke'), js = member('josuke'), p = player();
        if (te) { te.hp = Math.round(te.maxHp * 0.55); te.mem.fear = false; te.mem.terrified = false; te.mem.fearIn = 4; te.visible = true; te.mem.hold = false; }
        if (te) S2.unpose(te);
        if (js) { js.visible = false; js.team = 'npc'; }
        const ko = S2.actor('koichi_mh');
        if (ko) ko.remove = true;
        for (const id of ['mh_yuya', 'mh_book']) { const a = S2.actor(id); if (a) a.remove = true; }
        Object.assign(p, { x: 60, y: 156, facing: 1, visible: true });
        papersSetup(S2, d);
        hitFear(S2, ctx);
        S2.hint('仗助和康一的纸往碎纸机那边飘了！走过去按 E 揣进怀里（两张）', 8);
      },
      tick: (c, dt) => {
        const d = c.data, p = player(), te = S.actor('terunosuke');
        if (!p || !te) return;
        if (d.part === 2) {
          papersTick(S, c, dt);
          if (pressed(d, 'lpU', 'special') && p.cid === yu) { yuyaHeal(S, c, p); return; }
          if (d.full || (c.gauge && c.gauge.value >= c.gauge.max)) {
            d.full = false;
            if (!(d.papers || []).every((q) => q.held)) { c.fail('裕也害怕得发抖……纸还没揣好，他就变成了纸。'); return; }
            d.part = 2.5;
            cine(c, () => yuyaPaper(S, c));
          }
          return;
        }
        if (d.part === 3) {
          if (te.hp <= 1 && !d.finishing) { d.finishing = true; cine(c, () => finishBook(S, c)); return; }
          if (d.needFix && pressed(d, 'lpJ2', 'attack') && p.state === 'guard') cine(c, () => bookFix(S, c));
          else if (d.needFix) pressed(d, 'lpJ2', 'attack');
        }
      },
      endWhen: (c) => !!c.data.won,
    });
    R.closeSniff();
    for (const a of G.world.stage.actors) if (a.id && /^(mh_pp|mh_strip|te_trap)/.test(a.id)) a.remove = true;
    return res;
  };
})();
