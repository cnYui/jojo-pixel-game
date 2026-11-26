// 出租车是可受击的道具；耐久、预警、闪避和失败菜单都接现成战斗上下文。
'use strict';
(function () {
  const G = window.G;
  const R = G.P5PRO = {};
  R.fightTaxi = async S => {
    const taxi = S.actor('taxi');
    const owner = { team: 'enemy', facing: -1, dmgOut: 1, name: '出租车' };
    const res = await S.fight({
      id: 'b_pro1_taxi', arena: [240, 620], lead: 'koichi', swap: false,
      lockMsg: '先追回康一的行李', music: 'battle', after: null,
      losable: true, coverage: false, energy: { start: 100 }, waves: [],
      gauge: { max: 280, value: 280, label: '出租车耐久', color: '#edc862' },
      kitOverride: { koichi: { special: {
        need: 100, title: 'koichi', bg: 'radial', colours: ['#17381d', '#659b43'],
        prompt: 'J 连打　K 闪避　U：3 FREEZE 压住四秒',
        run: async (S2, p, c, C) => {
          const d = c.data;
          d.freezes++; d.freeze = 4; d.charge = null;
          for (const h of G.world.hazards) h.dead = true;
          p.facing = taxi.x >= p.x ? 1 : -1;
          C.stand('punch', { dx: 18, z: 4 });
          G.combat.hit(p, taxi, { slot: 'special', dmg: 60, energy: 0, push: 0, guard: 'none', sfxHit: 'thud' });
          S2.sfxText('3 FREEZE', taxi, { dur: 1.2 }); S2.mark('p5_taxi_freeze');
          S2.shake(2, .25);
          await S2.animate(.25, k => { taxi.z = -4 * k; });
          await C.wait(.3);
        },
      } } },
      tick: (c, dt) => {
        const d = c.data;
        if (!d.ready) {
          Object.assign(d, { ready: true, freeze: 0, next: 1.5, charge: null, hits: 0, freezes: 0,
            warnings: 0, collisions: 0, dodges: 0 });
          G.combat.resetActor(taxi);
          Object.assign(taxi, { x: 420, y: 160, z: 0, hp: 281, maxHp: 281, minHp: 1,
            team: 'object', bodyW: 30, armor: true, visible: true, remove: false, name: '出租车' });
          taxi.atlas = G.atlas('prop:taxi');
          c.on('hit', e => { if (e.t === taxi) { d.hits++; S.mark('p5_taxi_hit'); } });
          c.on('dodge', () => { d.dodges++; });
          S.hint('别想开走！J 连打削减耐久；红线亮起用 K 闪避；U：3 FREEZE 压住四秒', 9);
          S.mark('p5_taxi_start');
        }
        c.gauge.value = taxi.hp - 1;
        taxi.atlas = G.atlas(taxi.hp < 141 ? 'prop:taxi_hit' : 'prop:taxi');
        if (d.freeze > 0) {
          d.freeze = Math.max(0, d.freeze - dt);
          taxi.z = d.freeze > 0 ? -4 : 0;
          if (!d.freeze) { d.next = 1.4; S.mark('p5_taxi_thaw'); }
          return;
        }
        if (d.charge) {
          const q = d.charge, t = q.h.t - q.h.warn;
          if (t >= 0 && t < q.h.dur) {
            taxi.x = G.lerp(q.from, q.to, t / q.h.dur);
            // 预警覆盖整条倒车路径；生效后判定跟随车身，避免车还没到就撞到人。
            q.h.x0 = taxi.x - 37; q.h.x1 = taxi.x + 37;
          }
          if (q.h.dead) {
            q.back = (q.back || 0) + dt;
            taxi.x = G.lerp(q.to, 420, Math.min(1, q.back / 1.2));
            if (q.back >= 1.2) { d.charge = null; d.next = 1.8; }
          }
          return;
        }
        d.next -= dt;
        if (d.next <= 0) {
          d.warnings++;
          const from = taxi.x, to = 278;
          const h = c.hazard({ owner, side: 'enemy', shape: 'rect', x0: to - 30, x1: from + 30,
            y0: 150, y1: 170, warn: .9, dur: .42, dmg: 25, push: 0,
            guard: 'none', once: true, sfx: 'whoosh',
            onActive: h => { h.x0 = taxi.x - 37; h.x1 = taxi.x + 37; },
            onHit: () => { d.collisions++; S.mark('p5_taxi_collision'); },
          });
          d.charge = { h, from, to };
          S.hint('倒车了！红线是冲撞范围：K 闪避，或走出车道', 2.5);
          S.mark('p5_taxi_warning');
        }
      },
      endWhen: c => !!c.data.ready && taxi.hp <= 1,
      testHint: c => ({ durability: taxi.hp - 1, ...Object.fromEntries(
        ['freeze', 'hits', 'freezes', 'warnings', 'collisions', 'dodges'].map(k => [k, c.data[k] || 0])) }),
    });
    G.combat.stopRush(S.player);
    Object.assign(taxi, { hp: 1, team: 'npc', z: 0, x: 420 });
    taxi.atlas = G.atlas('prop:taxi_hit');
    G.flags.p5TaxiWon = true; G.flags.p5TaxiAttempts = res.attempts;
    S.mark('p5_taxi_win');
    await S.wait(.6);
    return res;
  };
})();
