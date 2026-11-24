// 打击感（重击闪白 / 顿帧缓出 / 击退缓出 + 压扁）验收用的页面端脚本：固定 60 Hz 逐步推进，记每一帧的画面输入。
//   同一份脚本既跑新分支，也跑基线（没有 G.HITSTOP、没有 flashNow 的旧引擎）：按能力探测，不认识的字段当旧行为。
//   页面里的战斗 / 时钟 / 输入 / 角色全是生产实现，只有声音和界面用 stubs.js 里的桩。
'use strict';
(function () {
  const G = window.G, W = G.world, C = G.combat, f = (n) => n / 60;
  const step = async (n = 1) => { for (let i = 0; i < n; i++) { G.dbg.tick(1, f(1)); await Promise.resolve(); } };
  const tap = async (a, n = 1) => { G.input.inject(a); await step(n); };
  const NEW = !!G.HITSTOP;                               // 新引擎才有顿帧曲线
  const setMode = (m) => { if (NEW) G.HITSTOP.freeze = m === 'legacy' ? 1 : 0.6; };   // legacy = freeze 100% = 旧的二值冻结

  function reset(cid, eo) {
    cid = cid || 'jotaro'; eo = eo || {};
    G.cancelRun(); G.time.clear(); G.input.clear(); G.fx.clear(); if (G.post.clear) G.post.clear();
    G.hitStopAll_t = 0; G.hitStopAll_total = 0; G.slowAllT = 0; G.slowAllK = 1;
    W.cine = null; W.slow = 1; W._combatSlowT = 0; W.anims = []; W.ticks = []; W.zoom = null;
    G.party.reset(); G.party.set([cid], { leader: cid });
    const p = G.party.leader(); C.resetActor(p);
    W.setStage({ id: 'p5', bg: 'hongkong_night', x0: 0, x1: 320, y0: 100, y1: 175 }, { player: p, x: 100, y: 160 });
    const e = new G.Actor('avdol', 240, 160, Object.assign({ team: 'enemy', kit: G.KITS.e_avdol_test, hp: 100000, boss: true, stand: 'magred', brain: () => true }, eo));
    W.stage.actors.push(e);
    W.combat = true; W.free = false;
    W.fight = { spec: { arena: [0, 320], kitOverride: {}, dmgScale: 1, playerMinHp: 0 }, data: {}, emit() {}, on() { return () => {}; } };
    p.facing = 1; e.facing = -1;
    p.stand.summon({ instant: true }); if (e.stand) e.stand.summon({ instant: true });
    G.dbg.resetCounts(); G.__audioLog.length = 0;
    return { p, e };
  }

  // 读目标这一帧真正画出去的输入（图集 draw 的参数）。图集是按角色 id 缓存共用的，只装一次钩子，当前盯谁放在 cur 里
  const cur = { target: null, atlases: [], last: null };
  function probe(t) {
    cur.target = t; cur.atlases = [t.atlas].concat(t.alt || []); cur.last = null;
    for (const at of cur.atlases) {
      if (!at || at.__hf) continue;
      const od = at.draw; at.__hf = true;
      at.draw = function (g, logical, frame, x, y, o) {
        if (cur.atlases.indexOf(this) >= 0) cur.last = { x, y, flash: (o && o.flash) || 0, onScreen: g === G.wg };
        return od.apply(this, arguments);
      };
    }
    return cur;
  }
  async function frames(t, n, pre) {
    const rec = probe(t), out = [];
    for (let i = 0; i < n; i++) {
      if (pre) pre(i);
      const w0 = G.clk.world, hs0 = G.hitStopAll_t, x0 = t.x;
      rec.last = null;
      G.dbg.tick(1, f(1)); await Promise.resolve();
      const d = rec.last;
      out.push({
        i, wmul: Math.round((G.clk.world - w0) * 60 * 1e4) / 1e4, hs: Math.round(hs0 * 60 * 1e3) / 1e3,
        x: Math.round(t.x * 1e4) / 1e4, dx: Math.round((t.x - x0) * 1e4) / 1e4, state: t.state,
        flash: d ? Math.round(d.flash * 1e3) / 1e3 : null, drawX: d ? d.x : null, squash: d ? !d.onScreen : null,
      });
    }
    return out;
  }

  const HF = window.HF = {
    NEW, reset, step, tap,
    async init() {
      await G.res.preloadPack('core'); await G.res.preloadPack('bg_fixture');
      // 和 main.js 的 gameScene 一样：世界不推进（全局顿帧冻结段）时不调 W.update，推进时用 wdt（含缓出倍率）
      G.setScene({ name: 'world', frozen: false, update(dt, adv, wdt) { if (adv) W.update(wdt); }, drawWorld: (g) => W.draw(g), drawUI() {}, drawTop() {},
        hasPixel: () => W.hasPixel(), drawPixel: (P, l) => W.drawPixel(P, l), hasOver: () => W.hasOver(), drawOver: (g) => W.drawOver(g) });
      G.start(); return true;
    },

    // ① 顿帧曲线：每个 n 帧的顿帧，逐步看世界倍率；总步数必须 = n，冻结段 0，缓出段单调上升，最后一步 < 1
    async hitstop() {
      const out = [];
      for (const n of [1, 2, 3, 4, 6, 8, 12, 18, 24, 30]) {
        for (const mode of ['legacy', 'curve']) {
          setMode(mode === 'legacy' ? 'legacy' : 'curve');
          reset();
          await step(2);
          G.hitStopAll(f(n));
          const mul = [];
          let guard = 0;
          while (G.hitStopAll_t > 0 && guard++ < 200) { const w0 = G.clk.world; await step(1); mul.push(Math.round((G.clk.world - w0) * 60 * 1e4) / 1e4); }
          const w1 = G.clk.world; await step(1);
          out.push({ n, mode, steps: mul.length, mul, frozen: mul.filter((v) => v === 0).length, sum: Math.round(mul.reduce((a, b) => a + b, 0) * 1e3) / 1e3, after: Math.round((G.clk.world - w1) * 60 * 1e4) / 1e4 });
        }
      }
      setMode('curve');
      return out;
    },

    // ② 弹反窗口：顿帧（n 帧）开始后第 a 个真实帧按 L，敌人的一击在世界时间 T0+S 帧落下，看弹没弹成。
    //    返回每个 (n, S) 的成功按键帧集合（a 的取值）和打击发生的真实帧
    async parry(mode, ns, Ss) {
      setMode(mode);
      const res = [];
      for (const n of ns) for (const S of Ss) {
        const ok = [];
        let strikeFrame = null;
        for (let a = -10; a <= 40; a++) {
          const { p, e } = reset();
          await step(2);
          let T0 = null;                                 // 顿帧开始那一刻（r = 0）的世界时钟
          let done = false, parried = false, frame = null;
          for (let r = -10; r < 80 && !done; r++) {
            if (r === 0) { T0 = G.clk.world; G.hitStopAll(f(n)); }
            if (r === a) G.input.inject('guard');
            G.dbg.tick(1, f(1)); await Promise.resolve();
            if (r >= 0 && G.clk.world >= T0 + f(S) - 1e-9) {   // 这一击按世界时间落下
              const hp0 = p.hp;
              const o = C.hit(e, p, { dmg: 20, push: 0, slot: 'enemy', poiseDmg: 0, sfxHit: null, guard: 'normal' }, { first: true });
              parried = !!o.parry; frame = r; done = true;
            }
          }
          if (parried) ok.push(a);
          if (strikeFrame == null && frame != null) strikeFrame = frame;
        }
        res.push({ n, S, ok, width: ok.length, lo: ok.length ? ok[0] : null, hi: ok.length ? ok[ok.length - 1] : null, strike: strikeFrame });
      }
      setMode('curve');
      return res;
    },

    // ③ 连打入口窗口：像人一样每 5 帧按一下 J 打出 J1 → J2 → J3；J3 出招那一帧记为 0，只在第 z 帧再按一下 J，看进没进连打
    async rushEntry(mode, zs) {
      setMode(mode);
      const ok = [], info = [];
      for (const z of zs) {
        const { p, e } = reset();
        e.x = p.x + 30; e.facing = -1; e.y = p.y;
        await step(2);
        let j3 = null, entered = false, hitAt = null;
        const hp0 = e.hp;
        for (let r = 0; r < 220 && !entered; r++) {
          if (j3 == null) { if (p.atk && p.atk.slot === 'J3') j3 = r; else if (r % 5 === 0) G.input.inject('attack'); }
          if (j3 != null && r === j3 + z) G.input.inject('attack');
          G.dbg.tick(1, f(1)); await Promise.resolve();
          if (j3 != null && hitAt == null && G.hitStopAll_t > 0) hitAt = r - j3;
          if (p.state === 'rush') entered = true;
        }
        if (entered) ok.push(z);
        info.push({ z, entered, j3, hitAt });
      }
      setMode('curve');
      return { ok, info };
    },

    // ④ 重击受击时间线：直接让 SP_J3 / SP_FIN 命中，逐帧记目标闪白 alpha、画面 x、位移、抖动、压扁
    async timeline(moveId, opts) {
      opts = opts || {};
      setMode(opts.legacy ? 'legacy' : 'curve');
      const { p, e } = reset();
      e.x = p.x + 30; e.y = p.y; e.facing = -1; e.hp = 1e6;
      G.settings.reduceFlash = !!opts.reduce;
      await step(3);
      const m = G.MOVES[moveId];
      const rec = probe(e);
      const out = [];
      const x0 = e.x;
      // 和真实战斗一样，命中发生在一个逻辑步里（ui 时钟已经走了这一步）：挂一个只跑一次的 tick
      W.ticks.push(() => { C.hit(p, e, m, { first: true, src: m }); return true; });
      for (let i = 0; i < (opts.n || 24); i++) {
        const w0 = G.clk.world, hs0 = G.hitStopAll_t, xb = e.x;
        rec.last = null;
        G.dbg.tick(1, f(1)); await Promise.resolve();
        const d = rec.last;
        out.push({
          i, wmul: Math.round((G.clk.world - w0) * 60 * 1e4) / 1e4, hs: Math.round(hs0 * 60 * 1e3) / 1e3,
          x: Math.round((e.x - x0) * 1e3) / 1e3, dx: Math.round((e.x - xb) * 1e3) / 1e3, state: e.state,
          flash: d ? Math.round(d.flash * 1e3) / 1e3 : null, shake: d && d.onScreen ? Math.round((d.x - e.x + (G.cam.x || 0)) * 1e3) / 1e3 : null, squash: d ? !d.onScreen : null,
        });
      }
      G.settings.reduceFlash = false;
      setMode('curve');
      return { move: moveId, push: m.push, stopAll: m.stopAll, flashTarget: m.flashTarget, frames: out };
    },

    // ⑤ 击退：不同 push 的总位移和时长、落点；撞墙扫描（敌人离右墙 d px，fin 的 40 px 击退，看 wall_slam 响没响）
    async push() {
      setMode('curve');
      const profile = [];
      for (const push of [4, 8, 12, 24, 30, 40, 60]) {
        const { p, e } = reset();
        e.x = 150; e.y = p.y; await step(2);
        const x0 = e.x, rows = [];
        C.hit(p, e, { dmg: 1, push, slot: 'J3', poiseDmg: 0, sfxHit: null }, { first: true });
        let steps = 0;
        for (let i = 0; i < 40; i++) { const xb = e.x; G.dbg.tick(1, f(1)); await Promise.resolve(); rows.push(Math.round((e.x - xb) * 1e3) / 1e3); if (e._push) steps = i + 1; }
        profile.push({ push, total: Math.round((e.x - x0) * 1e4) / 1e4, steps: steps + 0, rows: rows.slice(0, 14) });
      }
      const slam = [];
      for (const P of [40, 60]) for (let d = 0; d <= P + 6; d++) {
        const { p, e } = reset();
        e.y = p.y; e.x = 312 - d; p.x = e.x - 40; await step(2);
        G.__audioLog.length = 0;
        C.hit(p, e, { dmg: 1, push: P, slot: 'fin', poiseDmg: 0, sfxHit: null }, { first: true });
        await step(30);
        slam.push({ P, d, slam: G.__audioLog.some((v) => v[1] === 'wall_slam'), x: Math.round(e.x * 100) / 100 });
      }
      return { profile, slam };
    },

    // 调试：J1 → J2 → J3 → 再按 J，逐帧记出招状态
    async chainLog(near, zPress) {
      const { p, e } = reset();
      e.x = p.x + (near ? 30 : 140); e.y = p.y; e.facing = -1;
      await step(2);
      const log = [];
      const rec = (tag) => log.push([tag, p.atk ? p.atk.slot : null, p.state, Math.round(p.atkT * 60), Math.round(e.hp), Math.round(p.stopT * 60), Math.round(G.hitStopAll_t * 60)]);
      await tap('attack'); rec('J1');
      await step(7); await tap('attack', 3); rec('J2');
      await step(7); await tap('attack'); rec('J3');
      for (let r = 1; r < 60; r++) { if (r === zPress) G.input.inject('attack'); G.dbg.tick(1, f(1)); await Promise.resolve(); rec('r' + r); }
      return log;
    },

    // ⑥ 轻击不变：J1 命中，目标闪白 alpha 逐帧、画面抖动
    async light() { return HF.timeline('SP_J1', { n: 20 }); },
  };
})();
