// 包 4 自测用桩：fx.js（G.fx 实例系统 + 用到的几个 G.FX 函数的简化画法）和 post.js（只做时停的灰黄色调，方便看 over pass）。集成时换成包 2 的真文件。
'use strict';
(function () {
  const G = window.G;
  const px = () => G.px;
  const FX = (G.FX = G.FX || {});

  // summon_lines：stand_summon 里那 8 条上升能量线（fx.py:2414-2421）
  FX.summon_lines = function (P, x, y, t, t0, kw = {}) {
    const dur = kw.dur || 0.35, u = (t - t0) / dur;
    if (u < 0 || u >= 1) return;
    const ac = kw.colour || kw.aura_colour || '#c080ff', lc = G.mixHex(ac, '#ffffff', 0.6);
    for (let j = 0; j < 8; j++) {
      const sx = Math.round(x + (G.hash01(j, 3, Math.floor(t0 * 10)) - 0.5) * 30);
      const ph = (u * 1.6 + G.hash01(j, 4)) % 1, sy = Math.round(y - 4 - ph * 44), L = 4 + Math.floor(6 * G.hash01(j, 5));
      px().line(P, sx, sy, sx, sy + L, j % 2 ? lc : ac);
    }
  };
  // tendrils：触须（简化：下垂 + 轻微摆动的 1 px 线 + 抖动光晕 + 光点）
  FX.tendrils = function (P, pts, t, kw = {}) {
    const col = kw.colour || '#70ffb0', grow = kw.grow == null ? 1 : kw.grow, wig = kw.wiggle == null ? 1 : kw.wiggle;
    const segs = Array.isArray(pts[0][0]) ? pts : pts.slice(0, -1).map((p, i) => [p, pts[i + 1]]);
    const ts = Math.floor(t * 12) / 12;
    segs.forEach(([a, b], si) => {
      const n = Math.max(2, Math.round(Math.hypot(b[0] - a[0], b[1] - a[1]) / 2));
      const m = Math.max(1, Math.round(n * grow));
      let lx = a[0], ly = a[1];
      for (let i = 1; i <= m; i++) {
        const u = i / n, sag = Math.sin(Math.PI * u) * 4, w = Math.sin(ts * 6 + u * 9 + si) * wig;
        const xx = Math.round(a[0] + (b[0] - a[0]) * u), yy = Math.round(a[1] + (b[1] - a[1]) * u + sag + w);
        px().line(P, lx, ly, xx, yy, col);
        px().plot(P, xx, yy - 1, col, 0.35); px().plot(P, xx, yy + 1, col, 0.35);
        lx = xx; ly = yy;
      }
      const pu = (t * 0.8 + si * 0.3) % 1;
      if (pu < grow) px().plot(P, Math.round(a[0] + (b[0] - a[0]) * pu), Math.round(a[1] + (b[1] - a[1]) * pu + Math.sin(Math.PI * pu) * 4), '#ffffff');
    });
  };
  // vines：两股拧在一起的紫藤（简化）
  FX.vines = function (P, x0, y0, x1, y1, t, t0, t1, kw = {}) {
    const L = Math.hypot(x1 - x0, y1 - y0);
    if (L < 1) return;
    const n = Math.round(L), ts = Math.floor(t * 12) / 12;
    for (let s = 0; s < (kw.strands || 2); s++) {
      let lx = x0, ly = y0;
      for (let i = 1; i <= n; i++) {
        const u = i / n, off = Math.sin(u * 10 + s * Math.PI + ts * 3) * 1.6;
        const xx = Math.round(x0 + (x1 - x0) * u), yy = Math.round(y0 + (y1 - y0) * u + off);
        px().line(P, lx, ly, xx, yy, s ? '#b070f0' : '#7a3cc0', 1, 1);
        if (i % 6 === 3) px().plot(P, xx, yy - 2, '#e0c0ff');
        lx = xx; ly = yy;
      }
    }
  };
  FX.burst = function (P, x, y, t, t0, kw = {}) {
    const dt = t - t0, life = kw.life || 0.6, n = kw.n || 20, cols = kw.colours || ['#ffffff'];
    if (dt < 0 || dt > life) return;
    for (let i = 0; i < n; i++) {
      const a = ((kw.angle || 90) + (G.hash01(kw.seed || 0, i, 2) - 0.5) * (kw.spread || 360)) * Math.PI / 180;
      const sp = (kw.speed || 60) * (0.5 + G.hash01(kw.seed || 0, i, 3));
      const xx = x + Math.cos(a) * sp * dt, yy = y - Math.sin(a) * sp * dt + 0.5 * (kw.gravity || 120) * dt * dt;
      px().plot(P, Math.round(xx), Math.round(yy), cols[i % cols.length], 1 - dt / life);
    }
  };
  FX.fire = function (P, x, y, t, kw = {}) {
    const w = kw.w || 16, h = kw.h || 24, ts = Math.floor(t * 12);
    for (let i = 0; i < w; i++) {
      const hh = Math.round(h * (0.4 + 0.6 * G.hash01(ts, i, 9)) * Math.sin(Math.PI * (i + 0.5) / w));
      px().line(P, Math.round(x - w / 2 + i), y, Math.round(x - w / 2 + i), y - hh, '#ff7a20');
      px().line(P, Math.round(x - w / 2 + i), y, Math.round(x - w / 2 + i), y - Math.round(hh * 0.5), '#ffd040');
    }
  };

  // ---------------- 实例系统（§4.6.3 的最小子集）
  const ARGS = {
    summon_lines: (k) => [k.x, k.y], burst: (k) => [k.x, k.y], dust: (k) => [k.x, k.y], shockwave: (k) => [k.x, k.y],
  };
  const LIFE = { summon_lines: (k) => k.dur || 0.35, burst: (k) => k.life || 0.6, fire: () => Infinity };
  const list = [];
  G.fx = {
    list,
    spawn(name, kw = {}, o = {}) {
      const by = o.by, imm = by && G.time && G.time.immune && G.time.immune.has(by);
      const inst = { name, kw: Object.assign({}, kw), o, clock: o.clock || (imm ? 'world' : 'flow'), layer: o.layer || (imm ? 'over' : 'mid'), tag: o.tag || null };
      inst.t0 = G.clk[inst.clock];
      inst.life = o.life || (LIFE[name] ? LIFE[name](kw) : 1);
      list.push(inst);
      return inst;
    },
    kill(i) { const k = list.indexOf(i); if (k >= 0) list.splice(k, 1); },
    killTag(tag) { for (let k = list.length - 1; k >= 0; k--) if (list[k].tag === tag) list.splice(k, 1); },
    clear() { list.length = 0; },
    has(id) { return list.some((i) => i.o.id === id); },
    hasPixel(layer) { return list.some((i) => i.layer === layer); },
    prune() { for (let k = list.length - 1; k >= 0; k--) { const i = list[k]; if (G.clk[i.clock] - i.t0 > i.life) list.splice(k, 1); } },
    drawPixel(P, layer) {
      const W = G.world;
      for (const i of list.slice()) {
        if (i.layer !== layer) continue;
        if (W && W.insert && i.tag !== 'insert' && (i.o.space || 'world') === 'world') continue;
        const t = G.clk[i.clock];
        if (t - i.t0 > i.life) { G.fx.kill(i); continue; }
        const fn = FX[i.name];
        if (!fn) continue;
        const k = Object.assign({}, i.kw);
        if (i.o.follow) { const f = i.o.follow; k.x = f.x + (i.o.dx || 0) * (f.facing || 1); k.y = f.y - f.z + (i.o.dy || 0); }
        if ((i.o.space || 'world') === 'world') { k.x -= G.cam.x; k.y -= G.cam.y; }
        if (i.name === 'fire') fn(P, Math.round(k.x), Math.round(k.y), t, k);
        else if (ARGS[i.name]) fn(P, Math.round(k.x), Math.round(k.y), t, i.t0, k);
      }
    },
    auraFlame() { return null; },
    hit() {}, dustAt() {},
  };

  // ---------------- post 桩：时停期间把世界映射成灰黄（只为了看 over pass 的“能动的人保持彩色”）
  G.post = {
    active() { return !!(G.time && G.time.overActive && G.time.overActive()); },
    apply(P, stage) { if (stage === 'mid' && this.active() && G.px.gray) { G.px.gray(P, 1); if (G.px.tint) G.px.tint(P, '#e0c060', 0.35); } },
    filter() {}, impact() {}, impactSeq() {}, pulse() {}, clear() {},
  };
})();
