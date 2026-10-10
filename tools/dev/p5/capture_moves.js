// 六名主角逐帧抽帧（正式入口 index.html + 生产战斗 / 特效 / 替身代码）：J1 / J2 / J3、连打 + 终结、U、格挡、弹反、闪避、
//   guardAttack、自由走动 J / U。只搭场景、按真实按键时钟注入输入；状态快照给 capture_moves.py 画判定框和弹体位置。
'use strict';
(function () {
  const G = window.G, W = G.world, C = G.combat, f = n => n / 60;
  const step = async (n = 1) => { for (let i = 0; i < n; i++) { G.dbg.tick(1, f(1)); await Promise.resolve(); } };
  let cur = null;

  function dummy(x, y, o = {}) {
    const e = new G.Actor(o.cid || 'jgeil', x, y, {
      team: 'enemy', kit: { hp: 10000, speed: 0, brain: () => true }, hp: 10000, minHp: 1,
      boss: false, stand: null, brain: () => true, noCharge: true,
    });
    e.maxHp = 10000; e.hp = 10000; e.minHp = 1; e.facing = -1; e.brain = () => true;
    W.stage.actors.push(e);
    return e;
  }
  // mode 'combat'：战斗场景（W.fight 带 data，和 fight.js 的 ctx 同形）；'explore'：自由走动（没有 W.fight）
  function reset(cid, o = {}) {
    G.cancelRun(); G.ui.reset(); if (G.S) { G.S.busy = false; G.S.cardOn = false; }
    G.time.clear(); G.input.clear(); G.fx.clear(); G.post.clear();
    G.hitStopAll_t = 0; G.slowAllT = 0; G.slowAllK = 1; G.fadeA = 0; G.flashA = 0;
    W.cine = null; W.insert = null; W.slow = 1; W._combatSlowT = 0;
    W.anims = []; W.ticks = []; W.zoom = null; G.cam.zoom = null; G.cam.shakeDur = 0;
    G.party.reset(); G.party.set([cid], { leader: cid });
    const p = G.party.leader(); C.resetActor(p);
    W.setStage({ id: 'capture', bg: o.bg || 'hongkong_night', x0: 0, x1: 640, yMin: 120, yMax: 176 },
      { player: p, x: o.x ?? 200, y: o.y ?? 160 });
    const e = o.noEnemy ? null : dummy(p.x + (o.dx ?? 70), p.y + (o.dy ?? 0), o.enemy || {});
    if (o.mode === 'explore') { W.combat = false; W.free = true; W.fight = null; }
    else {
      W.combat = true; W.free = false;
      W.fight = { spec: { arena: [0, 640], kitOverride: {}, dmgScale: 1, playerMinHp: 0 }, data: {}, emit() {}, on() { return () => {}; } };
    }
    p.facing = o.facing ?? 1;
    if (o.mode !== 'explore' && p.stand) p.stand.summon({ instant: true, sfx: false });
    G.cam.x = Math.max(0, Math.min(320, p.x - 110)); G.cam.y = 0;
    G.dbg.events.length = 0; G.dbg.missingImg.clear && G.dbg.missingImg.clear();
    cur = { p, e, requested: new Set(), rushStart: null, pics: [], trace: [] };
    return cur;
  }
  const r1 = v => Math.round(v * 10) / 10;
  function state(i) {
    const p = cur.p, e = cur.e, s = p.stand;
    const br = p.atlasFor ? p.atlasFor(p.anim).resolve(p.anim, p.skin) : null;
    const sr = s && s.atlas ? s.atlas.resolve(s.pose, s.skin) : null;
    const m = p.atk;
    let box = null;
    if (m && m.melee !== false && !m.shot && m.reach && m.active && p.atkT >= m.active[0] && p.atkT < m.active[1]) {
      const o = m.from === 'stand' && s ? s.origin() : p, fc = p.facing || 1, bw = e ? (e.bodyW || 6) : 6;
      const a = o.x + fc * (m.reach[0] - bw), b = o.x + fc * (m.reach[1] + bw);
      box = { x0: Math.min(a, b), x1: Math.max(a, b), y: o.y, depth: m.depth || 8, zr: m.zr || 26, oz: o.z || 0, circle: m.shape && m.shape.kind === 'circle' ? m.shape.r : null };
    }
    if (p.state === 'rush') {
      const k = C.kitOf(p).rush;
      if (k && !k.shot && k.reach) { const fc = p.facing || 1, bw = e ? (e.bodyW || 6) : 6, a = p.x + fc * (k.reach[0] - bw), b = p.x + fc * (k.reach[1] + bw); box = { x0: Math.min(a, b), x1: Math.max(a, b), y: p.y, depth: k.depth || 10, zr: 26, oz: 0, rush: true }; }
    }
    const front = C.standFront ? C.standFront(p, 12) : null;
    return {
      i, state: p.state, x: r1(p.x), y: r1(p.y), z: r1(p.z || 0), facing: p.facing, anim: p.anim,
      body: br ? br.name + '[' + p.frameIndex() + ']' : p.anim, atk: p.atkId || (m && m.slot) || null, atkT: m ? r1(p.atkT * 60) : null,
      stand: s ? { mode: s.mode, pose: s.pose, act: sr ? sr.name : null, frame: s.atlas ? s.frame() : null, x: r1(s.x), z: r1(s.z), kind: s.kind, visible: s.visible, top: s.atlas ? s.atlas.topPx() : null } : null,
      front: front ? { x: r1(front.x), y: r1(front.y), z: r1(front.z) } : null, box,
      shots: W.shots.map(sh => ({ kind: sh.kind, x: r1(sh.x), y: r1(sh.y), z: r1(sh.z), hitR: sh.hitR, travel: r1(sh._travel || 0), dead: !!sh.dead, life: r1(sh.life), range: sh.range || null, slot: sh.slot })),
      hazards: W.hazards.map(h => ({ shape: h.shape, x: h.x, y: h.y, rx: h.rx, ry: h.ry, x0: h.x0, x1: h.x1, y0: h.y0, y1: h.y1, phase: h.phase })),
      enemy: e ? { x: r1(e.x), y: r1(e.y), z: r1(e.z || 0), hp: e.hp, state: e.state, bodyW: e.bodyW, top: e.topPx() } : null,
      cam: { x: G.cam.x || 0, y: G.cam.y || 0 }, cine: W.cine ? String(W.cine.by && W.cine.by.cid || W.cine.by) : null, insert: !!W.insert,
      fx: G.fx.list.filter(x => !G.fx.expired(x)).map(x => x.name), energy: p.energy, hitstop: r1(G.hitStopAll_t * 60),
    };
  }
  function snap(i, label, screen) {
    const st = state(i);
    cur.pics.push({ i, label, st, png: G.wv.toDataURL('image/png'), screen: screen ? G.screen.toDataURL('image/png') : null });
  }
  // 自动三连 / 连打的按键：按招式自己的时钟按（和 capture 排查脚本同一个思路），不按固定节奏
  function autoCombo(i, want) {
    const p = cur.p, m = p.atk;
    if (p.state === 'rush') {
      if (cur.rushStart == null) cur.rushStart = i;
      if (want.rushFrames != null && i - cur.rushStart < want.rushFrames && (i - cur.rushStart) % 6 === 0) G.input.inject('attack');
      return;
    }
    if (!m || cur.requested.has(m)) return;
    const slot = m.slot, idx = ['J1', 'J2', 'J3'].indexOf(slot);
    if (idx < 0) return;
    if (idx + 1 >= want.hits && !(slot === 'J3' && want.rushFrames != null)) return;
    const thr = slot === 'J3' ? (m.active[0] + m.active[1]) / 2 : Math.max(m.active[0] + C.CFG.comboBufFrom, (m.link || m.active[1]) - f(2));
    if (p.atkT >= thr) { G.input.inject('attack'); cur.requested.add(m); }
  }
  const CAP = window.CAP = {
    reset, state, step,
    async setup() {
      G.dbg.hold = true;
      window.__entry = G.playFrom(1);
      await G.res.loadPack('bg_common'); await G.res.loadPack('bg_ch1'); await G.res.loadPack('bg_prologue');
      G.cancelRun(); await Promise.resolve();
      G.ui.reset(); if (G.S) { G.S.busy = false; G.S.cardOn = false; if (G.S.ambient) G.S.ambient(null); if (G.S._filters) G.S._filters.clear(); }
      return { scene: G.scene && G.scene.name };
    },
    // spec: { cid, mode, dx, dy, facing, bg, frames, combo: { hits, rushFrames }, events: [[frame, kind, arg]], every, at: [..], screenAt: [..], energy }
    async run(spec) {
      const s = reset(spec.cid, spec);
      // 先走完替身召唤（0.35 s）再开始按键；探索模式替身本来就收着
      await step(spec.pre ?? (spec.mode === 'explore' ? 2 : 30));
      if (spec.energy != null) s.p.energy = spec.energy;
      G.dbg.events.length = 0;
      const ev = spec.events || [], at = new Set(spec.at || []), screenAt = new Set(spec.screenAt || []);
      for (let i = 0; i <= spec.frames; i++) {
        for (const [fr, kind, arg] of ev) if (fr === i) {
          if (kind === 'tap') G.input.inject(arg);
          else if (kind === 'down') G.input.press(arg, 'cap');
          else if (kind === 'up') G.input.release(arg, 'cap');
          else if (kind === 'poke' && s.e) C.hit(s.e, s.p, Object.assign({ dmg: 10, push: 6, slot: 'enemy', poiseDmg: 0, sfxHit: 'punch' }, arg || {}), { first: true });
          else if (kind === 'shotAt' && s.e) C.shoot(s.e, Object.assign({ kind: 'fireball', r: 5, speed: 140, dmg: 8, hitR: [7, 6, 18] }, arg || {}), { x: s.e.x - 10, y: s.e.y, z: 22 });
          else if (kind === 'js') (new Function('p', 'e', 'W', 'G', 'C', arg))(s.p, s.e, W, G, C);
        }
        if (spec.combo) autoCombo(i, spec.combo);
        if (i > 0) await step();
        const every = spec.every && i % spec.every === 0;
        if (every || at.has(i) || screenAt.has(i)) snap(i, (spec.labels && spec.labels[i]) || ('f' + i), screenAt.has(i));
        s.trace.push({ i, st: s.p.state, atk: s.p.atkId, shots: W.shots.length, hp: s.e ? s.e.hp : null, energy: s.p.energy });
        if (spec.stopWhen && (new Function('p', 'e', 'W', 'G', 'return ' + spec.stopWhen))(s.p, s.e, W, G) && i > (spec.minFrames || 0)) break;
      }
      const dmg = s.e ? 10000 - s.e.hp : 0;
      return { cid: spec.cid, name: spec.name, pics: s.pics, trace: s.trace, dmg, rushStart: s.rushStart,
        errors: G.dbg.events.filter(x => /error|unknown/.test(x.type)).map(x => ({ type: x.type, where: x.where, msg: x.msg, name: x.name })),
        missing: [...G.dbg.missingImg] };
    },
  };
})();
