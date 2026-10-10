// 第六至九章招式保留镰刀节拍、妖刀记招与儿童无替身的差别。
'use strict';
(function () {
  const G = window.G, M = G.MOVES, K = G.KITS, f = n => n / 60;
  const slash = (body, damage, tier = 'W1', frames = 20, guard = 'normal', accent = '#ffffff') => ({ slot: 'enemy', body,
    dur: f(frames + 28), active: [f(frames), f(frames + 6)], warn: { tier, dur: f(frames) },
    from: 'body', reach: [0, 76], depth: 14, dmg: damage, push: 12, guard, cd: 1.3, weight: 2,
    sfx: 'whoosh', sfxHit: 'slash', fxHit: 'heavy', accent });
  M.DREAM_FIST = Object.assign({}, M.SP_J1, { body: 'punch', stand: null, dmg: 0, reach: [0, 28], step: 0 });
  M.DEATH_SCYTHE = slash('swing', 18, 'W2', 98); M.DEATH_SCYTHE.sfx = 'lalala';
  M.CLAY_POUNCE = slash('attack', 10, 'W1', 20); M.JUDGEMENT_FIST = Object.assign(slash('attack', 12, 'W3', 40), {
    melee: false, hazardAt: 0, hazard(e) { const p = G.world.player; return { shape: 'ellipse', x: p.x, y: p.y,
      rx: 18, ry: 9, warn: f(40), dur: f(8), dmg: 12, once: true, guard: 'normal', parry: true, fxActive: 'clay_fist', sfx: 'clay_crumble' }; } });
  K.death13 = { hp: 1000, speed: 30, fly: {z:12,bob:8}, moves: ['DEATH_SCYTHE'], brain(e, dt, c) {
    if (!dt) return true; const p = c.player; e.x = 160 + Math.sin(c.t * .65) * 104; e.z = 12 + Math.sin(c.t * 2) * 8;
    if (e.rootT > 0) return true;
    const d = e.mem; d.beat = (d.beat || 0) + dt;
    if (d.beat >= .3556 && (d.n || 0) < 4) { d.beat -= .3556; d.n = (d.n || 0) + 1; G.S.word('LA', e); }
    if (d.n === 4) { d.after = (d.after || 0) + dt; if (d.after >= .2) {
      c.hazard({ shape: 'rect', x0: 0, x1: 320, y0: p.y - 9, y1: p.y + 9, warn: 0, dur: .1, dmg: 18, once: true,
        guard: 'normal', parry: true, fxActive: 'scythe_sweep', owner: e });
      e.play('swing'); d.n = 0; d.after = 0; d.beat = -1.3;
    } }
    return true;
  } };
  K.judgement = { hp: 1000, speed: 32, moves: ['JUDGEMENT_FIST', 'CLAY_POUNCE'] };
  K.clay = { hp: 9999, speed: 24, moves: ['CLAY_POUNCE'] };
  M.PRIESTESS_POUNCE = slash('attack', 12, 'W1', 20);
  K.highpriestess = { hp: 9999, speed: 54, moves: ['PRIESTESS_POUNCE'] };
  M.AN_SLASH = slash('slash', 12); M.AN_PIERCE = slash('slash', 18, 'W5', 36, 'none', '#b568f2');
  // combat.beginDash 用 dist / time 算速度：以前写 speed: 260、没有 time → 速度 NaN，恰卡 / 卡恩一用突进坐标就变成 NaN、从画面上消失（打不到也看不见）。
  //   line：沿 W4 预警画出来的那条红线冲；melee: false：只按冲刺路径判定，不再额外吃一次 76 px 的挥刀判定。
  M.AN_DASH = Object.assign(slash('slash', 14, 'W4', 30), { melee: false, dash: { dist: 150, time: 150 / 260, w: 8, line: true } });
  // 这两招只给被附身的波鲁纳雷夫（图集动作叫 attack，没有 slash）
  M.AN_TWIN = Object.assign(slash('attack', 10), { hits: 2, every: .14 });
  M.AN_THRUST_P = slash('attack', 18, 'W5', 24, 'parryOnly', '#b568f2');
  M.AN_THRUST_P.onParried = (enemy, player, c) => {
    if (!c || c.data.bladeBusy) return true;
    G.MID.task(c, async () => { c.data.bladeBusy = true; G.MID.drain(c, 25);
      if (player.hp <= 0) { c.fail('夹住刀耗尽了体力……再来一次。'); return; }
      await G.S.say('jotaro', '刀……已经被我的身体夹住了。');
      const win = await G.S.clash({ label: '打碎它！（连按 J）', time: 4 });
      if (win) { G.S.fx('shatter', { src: 'prop:anubis_sword', logical: 'idle', x: enemy.x, y: enemy.y - 30, pieces: 20 }); c.end(); }
      else G.S.hint('刀挣脱了。等紫色突刺，再精准格挡。', 6);
      c.data.bladeBusy = false;
    }); return true;
  };
  for (const cid of ['chaka', 'khan', 'polnareff_possessed']) K[cid] = { hp: cid === 'chaka' ? 900 : cid === 'khan' ? 1200 : 1400,
    speed: 42, moves: cid === 'polnareff_possessed' ? ['AN_TWIN', 'AN_THRUST_P'] : ['AN_SLASH', 'AN_PIERCE', 'AN_DASH'],
    onHitBy(e, att, move, info) {
      if (!att || att.team !== 'player' || move.unseen) return null;
      const c = G.world.fight; if (!c || !c.data.memory) return null;
      const type = att.mem.anubisCounterUntil >= c.t ? '格挡反击' : info.slot === 'special' ? 'U' : info.slot === 'rush' ? '连打' : info.slot;
      if (type === '格挡反击') att.mem.anubisCounterUntil = -1;
      const mem = c.data.memory;
      if (mem.includes(type)) {
        if (!e.mem.counterAt || c.t - e.mem.counterAt >= .45) { e.mem.counterAt = c.t;
          G.combat.hit(e, att, { dmg: 10, slot: 'enemy', guard: 'normal', push: 8 }); G.S.word('记住了！', e); }
        return 'parry';
      }
      mem.push(type); if (mem.length > 3) mem.shift(); return null;
    } };
  M.MARIAH_KICK = slash('kick', 12); M.ALESSI_AXE = slash('axe', 16, 'W2', 45);
  K.mariah = { hp: 1300, speed: 62, moves: ['MARIAH_KICK'], brain(e, dt, c) {
    if (Math.abs(e.x - c.player.x) < 50 && !e.atk && !e.tele && e.cool <= 0) { G.AI.tele(e, 'MARIAH_KICK'); e.cool = 1; return true; }
    if (!e.atk && !e.tele) { G.AI.approach(e, c.player, 96, dt); return true; } return false;
  } };
  K.alessi = { hp: 1300, speed: 38, moves: ['ALESSI_AXE'] };
  M.KIDPOL_AMBUSH = { slot: 'J3', body: 'punch', melee: false, dmg: 0, reach: [0, 70], depth: 24, dur: .4, active: [0, .1], guard: 'none',
    onStart(p, c) { if (c && c.data.hidden === 'aquarium' && c.boss && Math.abs(p.x - c.boss.x) <= 90 && (p.x - c.boss.x) * c.boss.facing < 0) {
      G.combat.hit(p, c.boss, { dmg: 150, slot: 'J3', push: 20 }); c.data.ambush++; c.data.hidden = null; G.S.word('反击！', p);
    } } };
  for (const [i, dmg] of [6, 6, 10].entries()) M['KID_J' + (i + 1)] = Object.assign({}, M.SP_J1, { body: 'punch', stand: null,
    dmg, slot: 'J' + (i + 1), from: 'body', reach: [0, 30], step: 2 });
  K.polnareff_kid = { hp: 100, speed: 70, combo: ['KID_J1', 'KID_J2', 'KID_J3'], chords: { 'dodge+attack': 'KIDPOL_AMBUSH' },
    special: null, dodge: {}, onHitBy: () => null };
  K.jotaro_kid = { hp: 130, speed: 64, combo: ['KID_J1', 'KID_J2', 'KID_J3'], special: null, dodge: {} };
  M.JA_MAGNET_CLAP = { slot: 'fin', body: 'cmd', stand: null, dur: .5, active: [0, .1], dmg: 0,
    onStart(p, c) { const a = G.party.get(p.cid === 'joseph' ? 'avdol' : 'joseph'), e = c && c.boss;
      if (!a || !e) return;
      if (e.hp <= e.maxHp * .5 && (p.x - e.x) * (a.x - e.x) < 0 && Math.abs(p.x - a.x) <= 120 && Math.abs((p.x + a.x) / 2 - e.x) <= 10) {
        G.S.word('合击！', e); G.S.fx('magnet_junk', { x: e.x, y: e.y - 20, n: 20 }); c.end();
      } else G.S.hint('先打到半血，再分站她的左右，J＋L 合击。', 5);
    } };
})();
