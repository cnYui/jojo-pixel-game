// 固定时钟和静止敌人使方向、纵深、伤害及演出回归可重复，战斗和图集均使用生产实现。
'use strict';
(function () {
  const G = window.G, W = G.world, C = G.combat;
  let current;
  const step = async (n = 1) => {
    for (let i = 0; i < n; i++) {
      G.dbg.tick(1, 1 / 60);
      await Promise.resolve();
      if (current) for (const s of W.shots) if (!current.seen.has(s)) {
        current.seen.add(s);
        current.shots.push({ kind: s.kind, vx: s.vx, vy: s.vy, x: s.x, y: s.y });
      }
      if (i % 4 === 0) G.render();
    }
    G.render();
  };
  function enemy(x, y, extra = {}) {
    const e = new G.Actor('avdol', x, y, Object.assign({
      team: 'enemy', kit: { hp: 1000, speed: 0, brain: () => true }, hp: 1000,
      boss: true, stand: 'magred', brain: () => true,
    }, extra));
    W.stage.actors.push(e);
    return e;
  }
  function reset(cid, o = {}) {
    G.cancelRun(); G.time.clear(); G.input.clear(); G.fx.clear(); G.post.clear();
    G.hitStopAll_t = 0; G.slowAllT = 0; G.slowAllK = 1;
    W.cine = null; W.slow = 1; W._combatSlowT = 0;
    W.anims = []; W.ticks = []; W.zoom = null;
    G.party.reset(); G.party.set([cid], { leader: cid });
    const p = G.party.leader(); C.resetActor(p);
    W.setStage({ id: 'specials', bg: 'hongkong_night', x0: 0, x1: 640, yMin: 100, yMax: 175 },
      { player: p, x: o.x ?? 320, y: 150 });
    const e = o.empty ? null : enemy(p.x + (o.dx ?? 80), p.y + (o.dy ?? 0), o.enemy || {});
    W.combat = true; W.free = false;
    // 和 fight.js 的 ctx 同形：带 data / on。正式入口还加载了各章的招式文件，它们的像素层（moves_ch02_05 的 J.drawPixel）
    //   每帧读 G.world.fight.data；以前这里没给 data，渲染循环每帧抛 “reading 'draw'”（正式入口画面验收 0/12 的根因）
    W.fight = { spec: { arena: [0, 640], kitOverride: {}, dmgScale: 1, playerMinHp: 0 }, data: {}, emit() {}, on() { return () => {}; } };
    p.facing = o.facing ?? 1; p.stand.summon({ instant: true });
    G.cam.x = p.x - 160; G.cam.y = 0; G.dbg.events.length = 0;
    current = { p, e, shots: [], seen: new Set(), done: false, result: null };
    return current;
  }
  function snap() {
    const { p, e, shots, done, result } = current;
    return { damage: e ? 1000 - e.hp : 0, facing: p.facing, x: p.x, y: p.y,
      done, result, energy: p.energy, cine: W.cine && W.cine.by, shots,
      liveShots: W.shots.length, fx: G.fx.list.filter(x => !G.fx.expired(x)).map(x => ({ name: x.name, life: x.life, tag: x.tag })),
      errors: G.dbg.events.filter(x => ['fx_error', 'fx_unknown', 'loop_error'].includes(x.type)) };
  }
  const S = window.Specials = {
    step, snap, reset,
    async init() {
      await G.res.preloadPack('core'); await G.res.preloadPack('bg_ch1');
      G.setScene({
        update(dt, advancing, wdt) { if (advancing) W.update(wdt); },
        drawWorld: g => W.draw(g),
        hasPixel: () => W.hasPixel(), drawPixel: (P, layer) => W.drawPixel(P, layer),
        hasOver: () => W.hasOver(), drawOver: g => W.drawOver(g),
      });
      G.start(); return true;
    },
    start(cid, o) {
      const s = reset(cid, o); s.p.energy = 100;
      C.special(s.p).then(r => { s.done = true; s.result = r; });
    },
    async matrix() {
      const out = [];
      for (const cid of ['jotaro', 'kakyoin', 'avdol', 'polnareff', 'joseph', 'iggy']) {
        for (const side of [1, -1]) for (const mode of ['front', 'back', 'depth', 'point', 'far']) {
          const dx = side * (mode === 'point' ? 8 : mode === 'far' ? (cid === 'iggy' ? 94 : 170) : 80);
          S.start(cid, { dx, dy: mode === 'depth' ? -35 : 0, facing: mode === 'back' ? -side : side });
          await step(360);
          out.push({ cid, side, mode, ...snap() });
        }
      }
      return out;
    },
    async boundaries() {
      const walls = [];
      for (const cid of ['jotaro', 'polnareff']) for (const side of [-1, 1]) {
        S.start(cid, { x: side > 0 ? 624 : 16, dx: -side * 8, facing: side });
        let lo = Infinity, hi = -Infinity;
        for (let i = 0; i < 360; i++) {
          await step(); lo = Math.min(lo, current.p.x); hi = Math.max(hi, current.p.x);
        }
        walls.push({ cid, side, lo, hi, ...snap() });
      }
      const outOfRange = [];
      for (const cid of ['jotaro', 'polnareff', 'joseph', 'iggy', 'avdol']) {
        S.start(cid, { x: 80, dx: 480 }); await step(360);
        outOfRange.push({ cid, ...snap() });
      }
      const lock = reset('avdol');
      const shot = C.shoot(lock.p, { speed: 100, homing: 3, homingTarget: lock.e, life: 5, dmg: 1 });
      enemy(lock.p.x + 6, lock.p.y - 40);
      await step();
      const locked = shot.vy === 0;
      lock.e.remove = true; await step();
      const retargeted = shot.vy < 0;
      const high = reset('iggy', { dx: 40, enemy: { z: 80 } });
      const heightHits = C.createC(high.p).hitMove('IG_U').length;
      S.start('jotaro', { enemy: { dmgMul: 0 } }); await step(360);
      const immune = snap();
      return { walls, outOfRange, locked, retargeted, heightHits, immune };
    },
    async extras() {
      const s = reset('jotaro'); s.e.x = s.p.x + 40;
      enemy(s.p.x + 5, s.p.y - 45);
      const picked = C.createC(s.p).target(180);
      const pick = { intended: picked === s.e, dx: picked && picked.x - s.p.x, dy: picked && picked.y - s.p.y };
      const noTargets = [];
      for (const cid of ['jotaro', 'kakyoin', 'avdol', 'polnareff', 'joseph', 'iggy']) {
        S.start(cid, { empty: true, facing: -1 }); await step(360);
        noTargets.push({ cid, ...snap() });
      }
      const stationary = reset('avdol');
      const shot = C.shoot(stationary.p, { speed: 0, homing: 0, dmg: 1, life: 0.5 }, { x: 180, y: 130, z: 0 });
      const x = shot.x, y = shot.y; await step(10);
      const speedZero = { dx: shot.x - x, dy: shot.y - y };
      const story = reset('avdol'); story.e.x = story.p.x + 100;
      let cut = 0, groundCut = false, groundX = null, groundStart = null;
      W.cine = { by: 'special-run', owner: story.p };
      const promise = G.KITS.avdol.crossfireSp(story.p, C.createC(story.p)).then(r => { story.done = true; story.result = r; });
      for (let i = 0; i < 240; i++) {
        for (const sh of W.shots) {
          if (sh.fromGround) {
            groundCut ||= G.AI.cut(story.e, sh);
            groundStart ??= sh.x; groundX = sh.x;
          } else if (G.AI.cut(story.e, sh)) cut++;
        }
        await step();
        const ground = W.shots.find(s => s.fromGround);
        if (ground) { groundStart ??= ground.x; groundX = ground.x; }
      }
      await promise;
      const crossfire = { ...snap(), cut, groundCut, groundDx: groundX == null ? null : groundX - groundStart };
      S.start('kakyoin', { facing: -1, dx: -80 }); await step(12);
      G.cancelRun(); W.cine = null; await step(180);
      const cancel = snap();
      return { pick, noTargets, speedZero, crossfire, cancel };
    },
  };
})();
