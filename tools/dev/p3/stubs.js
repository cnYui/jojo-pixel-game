// 包 3 自测用的桩：只补“还没交付 / 自测时要能随意摆布”的模块（G.world、G.party、G.S、G.time、G.touch，post 没有时补一个简版）。
// 真引擎（core / res / input / audio / px / fx / atlas / bg）由 loader.js 先加载；这里只在缺的时候补，不覆盖真的。
'use strict';
(function () {
  const G = window.G;
  G.dbg = G.dbg || { ev() {}, missingImg: new Set(), missingGlyph: new Set(), missingHead: new Set(), missingSfx: new Set(), animFallbacks: new Set() };

  // ---------------------------------------------------------------- G.post（包 2 的 post.js 没到时：只做褐色，冲击帧等不画）
  if (!G.post) {
    const filters = {};
    G.post = {
      _stub: true,
      filter(name, amount = 1) { if (amount == null) delete filters[name]; else filters[name] = amount; },
      impact() {}, impactSeq() {}, pulse() {},
      active() { return Object.keys(filters).length > 0; },
      apply(P, stage) {
        if (stage !== 'mid') return;
        const a = filters.sepia;
        if (!a) return;
        const u = P.u32, BAY = G.px.BAY;
        const pal = [[36, 22, 10], [80, 52, 26], [128, 90, 48], [176, 132, 80], [214, 178, 122], [240, 218, 170]];
        for (let y = 0; y < P.h; y++) for (let x = 0; x < P.w; x++) {
          if (a < 1 && G.px.bay(x, y) >= a) continue;
          const i = y * P.w + x, v = u[i];
          const l = ((v & 255) * 0.3 + ((v >>> 8) & 255) * 0.59 + ((v >>> 16) & 255) * 0.11) / 255;
          const q = Math.min(5, Math.floor(l * 6 + BAY[((y & 3) << 2) | (x & 3)] - 0.5));
          const c = pal[Math.max(0, q)];
          u[i] = (0xff000000 | (c[2] << 16) | (c[1] << 8) | c[0]) >>> 0;
        }
      },
      clear() { for (const k in filters) delete filters[k]; },
    };
  }
  if (!G.fx) G.fx = { hasPixel: () => false, drawPixel() {}, killTag() {}, spawn() { return null; }, prune() {} };
  if (!G.time) G.time = { flowScale: () => 1, isFrozen: () => false, overActive: () => false, active: false };
  if (!G.touch) G.touch = { on: false, safe: { l: 0, r: 640, top: 360, sys: 640 } };

  // ---------------------------------------------------------------- 演示用 Actor
  class DemoActor {
    constructor(cid, x, y, o = {}) {
      const m = (G.D.chars && G.D.chars[cid]) || {};
      const hero = (G.D.heroes && G.D.heroes[cid]) || {};
      Object.assign(this, {
        cid, id: o.id || cid, name: o.name || m.name || cid, x, y, z: 0, facing: o.facing || 1, scale: o.scale || 1,
        team: o.team || 'npc', boss: !!o.boss, hp: o.hp != null ? o.hp : 100, maxHp: o.maxHp || o.hp || 100,
        energy: o.energy || 0, energyMax: 100, top: m.top || 40, visible: true, anim: o.anim || 'idle', emote: null,
        standId: hero.stand || o.standId || null, state: o.state || 'idle', look: o.look || null, leadable: o.leadable !== false,
        phases: o.phases || null, poise: o.poise || 0, poiseMax: o.poiseMax || 0, breakT: 0, label: o.label || null, dead: false,
      });
    }
    headY() { return this.y - this.z - this.top * this.scale; }
  }
  G.DemoActor = DemoActor;

  // ---------------------------------------------------------------- G.world（桩）
  G.world = {
    _stub: true,
    stage: null, player: null, free: true, combat: false, near: null, insert: null, cine: null, fight: null, fightT: 0, slow: 1, _look: null,
    setStage(bgKey) {
      const spec = G.D.bg[bgKey];
      this.stage = { id: 'demo_pro', bgKey, spec, bg: spec && G.Background ? new G.Background(spec) : null, actors: [], t: 0, state: {} };
      return this.stage;
    },
    add(a) { this.stage.actors.push(a); return a; },
    enemies() { return this.stage ? this.stage.actors.filter((a) => a.team === 'enemy') : []; },
    allies() { return this.stage ? this.stage.actors.filter((a) => a.team === 'ally') : []; },
    objects() { return this.stage ? this.stage.actors.filter((a) => a.team === 'object') : []; },
    members() { return G.party.members; },
    findLook() { return this._look; },
    update(dt) {
      if (this.stage) this.stage.t += dt;
      if (this.combat && !this.cine) this.fightT += dt;
      if (this.stage) for (const a of this.stage.actors) if (a.emote) { a.emote.t -= dt; if (a.emote.t <= 0) a.emote = null; }
    },
    draw(wg) {
      if (this.insert) {
        const ins = this.insert;
        ins.draw(wg, G.clk[ins.clock || 'ui'] - (ins.t0 || 0));
        return;
      }
      const st = this.stage;
      if (!st) return;
      if (st.bg) st.bg.draw(wg, G.cam.x, st.t, st);
      else if (st.spec && st.spec.layers && st.spec.layers[0]) { const im = G.image(st.spec.layers[0].image); if (G.ready(im)) wg.drawImage(im, 0, 0); }
      const list = st.actors.filter((a) => a.visible).sort((a, b) => a.y - b.y);
      for (const a of list) {
        if (!G.atlas) continue;
        const A = G.atlas(a.cid);
        if (!A) continue;
        A.draw(wg, a.anim, A.frameAt ? A.frameAt(a.anim, G.clk.world) : 0, Math.round(a.x - G.cam.x), Math.round(a.y - a.z - G.cam.y), { flip: a.facing < 0, scale: a.scale });
      }
      if (st.bg && st.bg.drawFg) st.bg.drawFg(wg, G.cam.x, st.t, st);
    },
    hasPixel() { return !!this.stage; },
  };

  G.party = {
    _stub: true, members: [], locked: false,
    leader() { return G.world.player; },
    lookReady() { return !!this._lookReady; },
    canSwap() { return !this.locked; },
  };
  G.S = G.S || { busy: false, flags: {} };
  G.NAMES = G.NAMES || {};

  // ---------------------------------------------------------------- 演示场景（照技术约定 §2.3 的场景接口）
  G.demoScene = {
    name: 'world',
    get frozen() { return !!(G.ui && G.ui.menu); },
    enter() {}, leave() {},
    update(dt, worldAdv, wdt) {
      if (!(G.ui && G.ui.menu) && worldAdv) G.world.update(wdt);
      G.ui.update(dt);
    },
    drawWorld(wg) { G.world.draw(wg); },
    hasPixel() { return G.world.hasPixel(); },
    drawPixel() {},
    drawUI(ug) { G.ui.draw(ug); },
    drawTop(ug) { G.ui.drawTop(ug); },
  };
})();
