// 后段敌人的攻击仍走统一格挡、弹反和时停结算；谜题的胜利条件交给章节持有。
'use strict';
(function () {
  const G = window.G, M = G.MOVES, K = G.KITS, f = n => n / 60;
  const punch = (id, n, tier, frames, anim = 'punch', reach = 44) => {
    M[id] = { slot: 'enemy', body: 'cmd', stand: anim, dur: f(frames + 28),
      active: [f(frames), f(frames + 5)], reach: [0, reach], depth: 10, dmg: n, push: 16,
      guard: 'normal', warn: { tier, dur: f(frames) }, sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light' };
  };
  const basic = (e, dt, c) => {
    if (!dt || !c || e.atk || e.tele || e.mem.locked) return true;
    const p = c.player; e.facing = Math.sign(p.x - e.x) || 1;
    if (Math.abs(p.x - e.x) > 38 || Math.abs(p.y - e.y) > 5) G.combat.walkTo(e, p.x - e.facing * 30, p.y, dt, e.speed);
    if (e.cool <= 0) { G.AI.tele(e, e.moves[e.patternI++ % e.moves.length]); e.cool = 1.05; }
    return true;
  };
  M.HH_LATE_BULLET = { slot: 'enemy', body: 'cmd', stand: 'cast', dur: .8, active: [.4, .43],
    melee: false, fireAt: [.4], warn: { tier: 'W4', dur: .4 },
    shot: { kind: 'bullet', speed: 155, life: 3.2, homing: 2.7, dmg: 12, hitR: [3, 4, 18], colour: '#f6d552' }, sfx: 'gunshot' };
  K.e_holhorse_late = { hp: 99999, speed: 36, moves: ['HH_LATE_BULLET'], special: null,
    onHitBy: () => 'evade', brain(e, dt, c) {
      if (!dt) return true; e.facing = Math.sign(c.player.x - e.x) || 1;
      G.combat.walkTo(e, c.player.x - e.facing * 65, c.player.y, dt, e.speed);
      e.mem.fire = (e.mem.fire || 0) + dt;
      if (e.mem.fire >= 1.5) { e.mem.fire %= 1.5; G.combat.shoot(e, M.HH_LATE_BULLET.shot); G.S.sfx('gunshot'); }
      return true;
    } };
  M.PS_DIVE = { slot: 'enemy', body: 'dive', stand: null, dur: 2.5, active: [0, 2.5], melee: false,
    diveAlongPath: 180, dmg: 18, push: 8, guard: 'normal', sfx: 'bird_screech', sfxHit: 'stab',
    warn: { tier: 'W2', dur: f(40), path: e => e.mem.divePath },
    onParried(e, p, c) {
      e.atk = e.tele = e.mem.dash = null; e.z = 0; e.state = 'idle'; e.stunT = 1; e.mem.perch = false;
      if (c) c.emit('birdBite', { e, p }); return true;
    } };
  M.PS_SPEARS = { slot: 'enemy', body: 'perch', stand: null, dur: 1.1, active: [.1, .2], melee: false,
    fireAt: [.1], warn: { tier: 'W4', dur: f(30) }, sfx: 'ice',
    shot: { kind: 'ice', n: 3, spread: 11, speed: 160, dmg: 10, life: 2.2, hitR: [3, 5, 30], colour: '#d4f1ff' } };
  M.PS_BULLET = { slot: 'enemy', body: 'perch', stand: null, dur: 1, active: [.1, .2], melee: false,
    fireAt: [.1], warn: { tier: 'W4', dur: f(24) }, sfx: 'ice',
    shot: { kind: 'ice', n: 2, spread: 25, speed: 130, homing: 2.5, dmg: 8, life: 2.4, hitR: [4, 5, 28], colour: '#b7e6ff' } };
  M.PS_WALL = { slot: 'enemy', body: 'perch', stand: null, dur: .7, active: [.1, .2], melee: false,
    warn: { tier: 'W3', dur: .7 }, onStart(e, c) { if (c) c.emit('iceWall', { e }); }, sfx: 'ice' };
  K.e_petshop = { hp: 1500, speed: 115, bodyW: 5, moves: ['PS_DIVE', 'PS_SPEARS', 'PS_BULLET', 'PS_WALL'],
    onHitBy(e, a, m, info) { return e.mem.perch ? 'evade' : info.slot === 'special' ? null : 'evade'; },
    brain(e, dt, c) {
      if (!dt || e.mem.locked) return true;
      if (e.atk || e.tele) return true;
      e.mem.perch = true; e.z = 24; e.facing = Math.sign(c.player.x - e.x) || 1;
      if (e.cool > 0) return true;
      const id = e.moves[e.patternI++ % e.moves.length];
      if (id === 'PS_DIVE') {
        e.mem.perch = false; e.z = 0;
        e.mem.divePath = [[e.x, e.y], [c.player.x, c.player.y], [G.clamp(c.player.x + e.facing * 65, c.spec.arena[0] + 12, c.spec.arena[1] - 12), c.player.y]];
      }
      G.AI.tele(e, id); e.cool = 1.3; return true;
    } };
  punch('VA_KICK', 16, 'W1', 16, 'kick');
  punch('VA_STOMP', 22, 'W2', 30, 'stomp', 55);
  K.e_vanilla = { hp: 800, speed: 58, standId: 'cream', moves: ['VA_KICK', 'VA_STOMP'], brain: basic };
  punch('NK_BACK', 8, 'W1', 22, null, 34);
  K.e_nukesaku = { hp: 200, speed: 40, moves: ['NK_BACK'], brain(e, dt, c) {
    const r = basic(e, dt, c); e.facing = -(Math.sign(c.player.x - e.x) || 1); return r;
  } };
  punch('TW_PUNCH', 20, 'W1', 16);
  punch('TW_KICK', 18, 'W1', 16, 'kick');
  M.TW_RUSH = { slot: 'enemy', body: 'cmd', stand: 'rush', dur: 1.2, active: [0, 1],
    reach: [0, 55], depth: 12, dmg: 4, push: 1, every: f(4), guard: 'normal',
    warn: { tier: 'W2', dur: f(30) }, sfx: 'muda_loop', sfxHit: 'punch', fxHit: 'light' };
  M.TW_KNIFE = { slot: 'enemy', body: 'cmd', stand: 'cast', dur: .75, active: [.1, .2], melee: false,
    fireAt: [.1], warn: { tier: 'W4', dur: f(24) }, sfx: 'knife_volley',
    shot: { kind: 'knife', n: 3, spread: 13, speed: 240, dmg: 12, life: 1.5, hitR: [3, 5, 18], colour: '#e2e3ec' } };
  K.e_dio = { hp: 1500, speed: 75, standId: 'theworld', poiseMax: 0,
    moves: ['TW_PUNCH', 'TW_RUSH', 'TW_KNIFE', 'TW_KICK'], brain: basic };
})();
