// 两场布加拉提战共用公共战斗判定，重试由S.fight恢复；拉链图随原判定缩放。
'use strict';
(function () {
  const G = window.G, R = G.P5CH1 = {};
  for (const slot of ['J1', 'J2', 'J3', 'FIN']) G.MOVES['P5_GE_' + slot] = Object.assign({}, G.MOVES['SP_' + slot], {
    word: slot === 'J3' || slot === 'FIN' ? 'MUDA!' : null, accent: '#edc862', push: slot === 'FIN' ? 12 : 3, launch: null,
  });
  Object.assign(G.KITS.giorno, {
    combo: ['P5_GE_J1', 'P5_GE_J2', 'P5_GE_J3'],
    rush: { tick: 4 / 60, dmg: 4, push: 0, reach: [0, 52], depth: 12, word: 'MUDA', hitSfx: 'punch', finisher: 'P5_GE_FIN' },
    guard: { pose: 'block' }, dodge: {}, parry: {},
  });
  G.MOVES.P5_SF_J = { slot: 'enemy', body: 'attack', stand: 'rush', standDx: 12,
    dur: .72, active: [.08, .48], every: .18, hits: 3, reach: [0, 48], depth: 12,
    dmg: 7, push: 2, guard: 'normal', sfx: 'whoosh', sfxHit: 'punch', warn: { tier: 'W1', dur: .35 } };
  G.KITS.p5_bucciarati = { hp: 140, speed: 54, standId: 'stickyfingers', koStyle: 'none', moves: [],
    brain(e, dt, c) {
      if (!dt || !c) return true;
      const p = c.player, d = c.data;
      if (d.hidden > 0 || d.action > 0) return true;
      e.facing = p.x >= e.x ? 1 : -1;
      // 停靠距离和拳的有效距离均按当前人物大小核对，保持近身三连能命中。
      G.AI.approach(e, p, 20, dt);
      d.jab = (d.jab || 0) - dt;
      if (d.jab <= 0 && Math.abs(e.x - p.x) < 30 && Math.abs(e.y - p.y) < 10) {
        G.AI.tele(e, 'P5_SF_J'); d.jab = 1.5; d.jabs = (d.jabs || 0) + 1;
        G.S.mark('p5_ch1_jabs');
      }
      return true;
    } };
  R.fight = async (S, phase) => {
    const second = phase === 2, id = 'b_ch1_' + phase, arena = second ? [150, 550] : [20, 300];
    let context;
    const ink = G.P5.worldInk((at, t, g) => {
      const c = context;
      if (!c || G.world.fight !== c) return;
      for (const h of G.world.hazards) {
        if (h.dead || !h.p5zip) continue;
        at((h.x0 + h.x1) / 2, (h.y0 + h.y1) / 2, q => {
          const w = (h.x1 - h.x0) / 2, active = h.phase === 'active';
          q.scale(w * 2 / 28, active && h.ankle ? 1.2 : .8);
          G.ui.sheet(q, 'zipper', 0, 0, 5, 1, { alpha: active ? 1 : .45 + Math.abs(Math.sin(t * 12)) * .35 });
        });
      }
      if (c.data.hidden > 0 && c.boss) at(c.data.doorX, c.boss.y, q => {
        q.scale(22 / 28, .7);
        G.ui.sheet(q, 'zipper', 0, 0, 5);
      });
      if (c.data.sense > 0) {
        g.fillStyle = '#fff6ed30'; g.fillRect(0, 0, 640, 360);
      }
    });
    try {
      const res = await S.fight({ id, arena, lead: 'giorno', swap: false, music: 'battle', after: null,
        losable: true, coverage: false, energy: { start: second ? 100 : 0 }, vs: id,
        waves: [[{ kit: 'p5_bucciarati', cid: 'bucciarati', actor: 'bucciarati', id: 'bucciarati', name: '布加拉提',
          x: second ? 380 : 218, y: 161, hp: 140, minHp: second ? 0 : 56, boss: true }]],
        onWave: async (S2, wave, actors, attempt, c) => {
          context = c;
          const e = actors[0];
          Object.assign(e, { visible: true, alpha: 1, hidden: false, untargetable: false, slowK: 1, hold: false, tint: null });
          Object.assign(c.player, { x: second ? 230 : 105, y: 162, facing: 1 });
          Object.assign(c.data, { next: 1, cycle: 0, hidden: 0, action: 0, sense: 0, jabs: 0, zips: 0, dives: 0, holes: 0, ankles: 0, specials: 0 });
          S2.hint(second ? 'J 连打；K 离开拉链口；L 弹反远端抓取；能量满 U：感觉失控三秒' : 'J 连打；拉链长条亮起用 K 闪避，或在命中前 L 弹反', 9);
          S2.mark('p5_ch1_' + phase + '_start');
        },
        kitOverride: second ? { giorno: { special: { need: 100, title: 'giorno', bg: 'radial', colours: ['#f7e3ae', '#b994b2'],
          prompt: 'U 黄金体验：让对手感觉失控三秒',
          run: async (S2, p, c, C) => {
            const e = c.boss;
            c.data.sense = 3; c.data.specials++; G.world.slow = .22;
            e.ghostOn = true; G.combat.ghostBurst(e, 3); C.stand('rush', { dx: 14 });
            if (G.combat.hitCheck(p, { reach: [0, 65], depth: 16 }, e))
              G.combat.hit(p, e, { slot: 'special', dmg: 14, push: 0, guard: 'none', sfxHit: 'punch_heavy' });
            S2.mark('p5_sense_overload'); await C.wait(.25);
          } } } } : {},
        tick: (c, dt) => {
          const d = c.data, e = c.boss, p = c.player;
          if (!e) return;
          if (d.sense > 0) {
            d.sense = Math.max(0, d.sense - dt); G.world.slow = d.sense > 0 ? .22 : 1; e.ghostOn = d.sense > 0;
            if (!d.sense) S.mark('p5_sense_recovered');
          }
          d.action = Math.max(0, d.action - dt * G.world.slow);
          if (d.hidden > 0) {
            d.hidden -= dt * G.world.slow;
            if (d.hidden <= 0) {
              d.hidden = 0;
              e.x = G.clamp(p.x - d.diveFromSide * 62, arena[0] + 16, arena[1] - 16);
              d.diveToSide = Math.sign(e.x - p.x);
              e.y = p.y; e.alpha = 1; e.hidden = false; e.untargetable = false;
              S.sfx('whoosh'); S.mark('p5_zip_reappear');
            }
            return;
          }
          d.next -= dt * G.world.slow;
          if (d.next > 0 || e.atk || e.tele) return;
          const kind = d.cycle++ % (second ? 4 : 2); d.next = 2.5; d.action = .9;
          if (kind === 1) {
            d.dives++; d.hidden = .8; d.doorX = e.x; d.diveFromSide = Math.sign(e.x - p.x) || e.facing;
            e.alpha = 0; e.hidden = true; e.untargetable = true;
            S.sfx('whoosh'); S.mark('p5_zip_dive'); return;
          }
          const hole = second && kind === 2, ankle = second && kind === 3;
          const x0 = hole ? p.x - 18 : Math.min(e.x, p.x) - 12;
          const x1 = hole ? p.x + 18 : Math.max(e.x, p.x) + 12;
          const h = c.hazard({ owner: e, side: 'enemy', shape: 'rect', x0, x1, y0: p.y - 6, y1: p.y + 6,
            warn: hole ? .9 : .7, dur: hole ? 1.3 : .23, dmg: hole ? 10 : ankle ? 16 : 18,
            push: 0, guard: hole ? 'none' : 'normal', parry: !hole, once: true, root: hole || ankle ? .65 : 0,
            sfx: 'whoosh', onHit: () => { d.hits = (d.hits || 0) + 1; S.mark('p5_ch1_hazard_hit'); } });
          h.p5zip = true; h.ankle = ankle;
          S.standAct(e, 'punch', { dx: 16, dur: .9 });
          if (hole) { d.holes++; S.mark('p5_zip_hole'); }
          else if (ankle) { d.ankles++; S.mark('p5_zip_ankle'); }
          else { d.zips++; S.mark('p5_zip_punch'); }
        },
        endWhen: c => !second && c.boss && c.boss.hp <= 56,
        testHint: c => ({ phase, bossHp: c.boss?.hp, bossX: c.boss?.x, bossY: c.boss?.y,
          ...c.data, hazards: G.world.hazards.filter(h => !h.dead).map(h => ({ x0: h.x0, x1: h.x1, y0: h.y0, y1: h.y1, phase: h.phase, left: h.warn - h.t })) }),
      });
      G.combat.stopRush(S.player); S.recall(S.player);
      G.flags['p5Ch1Fight' + phase] = res.attempts;
      S.mark('p5_ch1_' + phase + '_win'); await S.wait(.6);
    } finally {
      ink.close(); G.world.slow = 1;
      const e = S.actor('bucciarati');
      if (e) Object.assign(e, { alpha: 1, hidden: false, untargetable: false, ghostOn: false, slowK: 1 });
    }
  };
})();
