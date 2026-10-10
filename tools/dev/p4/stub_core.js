// 包 4 自测用桩：core.js / res.js / input.js / audio.js 的最小实现（照技术约定 §2–§4.4 的接口）。集成时换成包 1 的真文件。
'use strict';
(function () {
  const G = (window.G = window.G || {});
  G.W = 320; G.H = 180; G.UW = 640; G.UH = 360;
  G.D = window.GAME_DATA;

  // ---------------- 工具（§4.1.1）
  G.clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  G.lerp = (a, b, t) => a + (b - a) * t;
  G.mod = (a, n) => ((a % n) + n) % n;
  let seed = 12345;
  const rnd = () => { seed = (Math.imul(seed, 1103515245) + 12345) >>> 0; return seed / 4294967296; };
  G.rand = (a = 0, b = 1) => a + (b - a) * rnd();
  G.pick = (arr) => arr[Math.floor(rnd() * arr.length)];
  G.sign = (v) => (v > 0 ? 1 : v < 0 ? -1 : 0);
  G.prng = (s) => { let x = s >>> 0 || 1; return () => { x = (Math.imul(x, 1664525) + 1013904223) >>> 0; return x / 4294967296; }; };
  G.hash01 = function (...xs) {
    let h = 2166136261;
    for (const x of xs) {
      const v = Number.isInteger(x) ? x : Math.round(x * 997);
      h = (h ^ v) >>> 0; h = Math.imul(h, 16777619) >>> 0; h = (h ^ (h >>> 13)) >>> 0;
      h = Math.imul(h, 0x5BD1E995) >>> 0; h = (h ^ (h >>> 15)) >>> 0;
    }
    return h / 4294967296;
  };
  G.hrange = (a, b, ...xs) => a + (b - a) * G.hash01(...xs);
  G.ease = function (u, kind = 'io') {
    u = G.clamp(u, 0, 1);
    switch (kind) {
      case 'linear': return u;
      case 'in': return u * u;
      case 'out': return 1 - (1 - u) * (1 - u);
      case 'in3': return u * u * u;
      case 'out3': return 1 - Math.pow(1 - u, 3);
      default: return u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
    }
  };
  G.prog = (t, t0, t1) => G.clamp((t - t0) / (t1 - t0), 0, 1);
  G.tw = (t, t0, t1, a, b, kind = 'linear') => a + (b - a) * G.ease(G.prog(t, t0, t1), kind);
  G.stepped = (t, fps = 12) => Math.floor(t * fps) / fps;
  G.wobble = (t, amp = 1, freq = 1, phase = 0) => amp * Math.sin(2 * Math.PI * (freq * t + phase));
  const rgbCache = new Map();
  G.C = { white: [255, 255, 255], black: [0, 0, 0], emerald: [40, 230, 140], purple: [154, 76, 224], menace: [170, 60, 220], yellow: [255, 216, 60] };
  G.rgbOf = function (c) {
    if (Array.isArray(c)) return c;
    let v = rgbCache.get(c);
    if (v) return v;
    if (G.C[c]) v = G.C[c];
    else {
      let h = String(c).replace('#', '');
      if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
      const n = parseInt(h, 16) || 0;
      v = [(n >> 16) & 255, (n >> 8) & 255, n & 255];
    }
    rgbCache.set(c, v);
    return v;
  };
  G.mixHex = (a, b, k) => {
    const x = G.rgbOf(a), y = G.rgbOf(b);
    const h = (i) => ('0' + Math.round(x[i] + (y[i] - x[i]) * k).toString(16)).slice(-2);
    return '#' + h(0) + h(1) + h(2);
  };

  // ---------------- 调试（§4.1.7）
  G.dbg = {
    shot: null, events: [], counts: {},
    ev(type, data) { this.events.push(Object.assign({ t: G.clk.ui, type }, data || {})); if (this.events.length > 400) this.events.shift(); this.counts[type] = (this.counts[type] || 0) + 1; },
    resetCounts() { this.counts = {}; },
    animFallbacks: new Set(), missingImg: new Set(), missingSfx: new Set(), missingGlyph: new Set(), missingHead: new Set(),
    fps: { avg: 60, min: 60 },
  };

  // ---------------- 时钟、等待、场景（§2.3）
  G.clk = { ui: 0, world: 0, flow: 0 };
  G.waiters = [];
  G.wait = (sec, clock = 'world') => new Promise((res) => G.waiters.push({ clock, until: G.clk[clock] + sec, res }));
  G.until = (fn) => new Promise((res) => G.waiters.push({ fn, res }));
  G.cancelIgnore = (e) => { if (!e || e.name !== 'RunCancelled') console.error(e); };
  G.defer = (sec, fn, clock = 'world') => G.wait(sec, clock).then(fn).catch(G.cancelIgnore);
  G.scene = null;
  G.setScene = (s) => { if (G.scene && G.scene.leave) G.scene.leave(); G.scene = s; if (s.enter) s.enter(); };
  G.fadeA = 0; G.flashA = 0; G.flashColor = '#fff'; G.hitStopAll_t = 0; G.slowAllK = 1; G.slowAllT = 0;
  G.fade = (to, dur = 0.5) => { G.fadeA = to; return Promise.resolve(); };
  G.flash = (dur = 0.25, peak = 1, color = '#fff') => { G.flashA = peak; G.flashColor = color; G._flashDur = dur; };
  G.shake = (amp = 2, dur = 0.25, o = {}) => { G.cam.shakeAmp = Math.max(amp, G.cam.shakeAmp * (1 - G.cam.shakeT / Math.max(1e-6, G.cam.shakeDur))); G.cam.shakeDur = dur; G.cam.shakeT = 0; G.cam.shakeDir = o.dir || 'both'; };
  G.hitStopAll = (sec) => { G.hitStopAll_t = Math.max(G.hitStopAll_t, Math.min(sec, 0.5)); };
  G.slowAll = (k, sec) => { G.slowAllK = Math.min(G.slowAllK, k); G.slowAllT = Math.max(G.slowAllT, sec); };

  // ---------------- 画布（§2.4）
  G.mkCanvas = function (w, h, read = false) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    c.g = read ? c.getContext('2d', { willReadFrequently: true }) : c.getContext('2d');
    c.g.imageSmoothingEnabled = false;
    return c;
  };
  G.wv = document.createElement('canvas'); G.wv.width = 320; G.wv.height = 180;
  G.wg = G.wv.getContext('2d', { willReadFrequently: true }); G.wg.imageSmoothingEnabled = false;
  G.uv = document.createElement('canvas'); G.uv.width = 640; G.uv.height = 360;
  G.ug = G.uv.getContext('2d'); G.ug.imageSmoothingEnabled = false;
  G.screen = document.getElementById('screen');
  G.sctx = G.screen.getContext('2d');
  G.scale = 4;
  G.resize = function () { G.screen.width = 320 * G.scale; G.screen.height = 180 * G.scale; G.sctx.imageSmoothingEnabled = false; };
  G.resize();

  // ---------------- 镜头（§2.6）
  G.cam = {
    x: 0, y: 0, zoom: null, shakeAmp: 0, shakeDur: 0, shakeT: 0, shakeDir: 'both', bumpK: 0, bumpT: 0, bumpDur: 0,
    bump(k = 0.08, dur = 0.12) { this.bumpK = k; this.bumpT = 0; this.bumpDur = dur; },
    amp() { return this.shakeDur > 0 && this.shakeT < this.shakeDur ? this.shakeAmp * (1 - this.shakeT / this.shakeDur) : 0; },
    box() {
      const bump = this.bumpDur > 0 && this.bumpT < this.bumpDur ? this.bumpK * (1 - this.bumpT / this.bumpDur) : 0;
      let k = (this.zoom ? this.zoom.k : 1) * (1 + bump);
      const amp = this.amp();
      if (amp > 0) { const m = Math.ceil(amp) + 1; if (k < 1 + (2 * m + 2) / 180) k = 1 + (2 * m + 2) / 180; }
      const w = 320 / k, h = 180 / k;
      let cx = this.zoom ? this.zoom.x - this.x : 160, cy = this.zoom ? this.zoom.y - this.y : 90;
      const f = Math.floor(G.clk.ui * 30);
      const jx = Math.round((G.hash01(f, 7, 1) * 2 - 1) * amp), jy = this.shakeDir === 'x' ? 0 : Math.round((G.hash01(f, 7, 2) * 2 - 1) * amp);
      cx += jx; cy += jy * 0.6;
      cx = G.clamp(cx, w / 2, 320 - w / 2); cy = G.clamp(cy, h / 2, 180 - h / 2);
      return { x: cx - w / 2, y: cy - h / 2, w, h };
    },
    w2s(wx, wy, wz = 0) { return [wx - this.x, wy - wz - this.y]; },
    s2u(sx, sy) { const b = this.box(); return [(sx - b.x) * 320 / b.w * 2, (sy - b.y) * 180 / b.h * 2]; },
    w2u(wx, wy, wz = 0) { const s = this.w2s(wx, wy, wz); return this.s2u(s[0], s[1]); },
  };

  // ---------------- 设置 / 存储
  G.store = { get: (k, d) => d, set: () => {} };
  G.settings = { reduceFlash: false, musicVol: 0.8, sfxVol: 0.9, grunts: false, mashHold: false, touchSize: 1, save() {} };

  // ---------------- res（§4.2）
  const imgs = new Map(), pixes = new Map();
  G.image = function (key) {
    let im = imgs.get(key);
    if (im) return im;
    const uri = G.D.img[key];
    if (!uri) { G.dbg.missingImg.add(key); return null; }
    im = new Image(); im.src = uri; imgs.set(key, im);
    return im;
  };
  G.ready = (im) => !!(im && im.complete && im.naturalWidth > 0);
  G.pix = function (key) {
    let p = pixes.get(key);
    if (p) return p;
    const im = G.image(key);
    if (!G.ready(im)) return null;
    const c = G.mkCanvas(im.naturalWidth, im.naturalHeight, true);
    c.g.drawImage(im, 0, 0);
    const d = c.g.getImageData(0, 0, c.width, c.height);
    p = { w: c.width, h: c.height, u32: new Uint32Array(d.data.buffer.slice(0)) };
    pixes.set(key, p);
    return p;
  };
  G.res = {
    preloadPack(name) {
      const keys = G.D.packKeys[name] || [];
      return Promise.all(keys.map((k) => { const im = G.image(k); return im && im.decode ? im.decode().catch(() => G.dbg.missingImg.add(k)) : null; }));
    },
  };

  // ---------------- input（§4.3）：按键缓冲 / 日志按 world 时钟
  const KEY = {
    ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right', ArrowUp: 'up', KeyW: 'up', ArrowDown: 'down', KeyS: 'down',
    KeyJ: 'attack', KeyZ: 'attack', KeyK: 'dodge', KeyX: 'dodge', KeyL: 'guard', KeyC: 'guard', KeyU: 'special', KeyV: 'special',
    KeyQ: 'swap', Tab: 'swap', Digit1: 'lead1', Digit2: 'lead2', Digit3: 'lead3', Digit4: 'lead4', Digit5: 'lead5', Digit6: 'lead6',
    Enter: 'ok', NumpadEnter: 'ok', Space: 'ok', KeyE: 'ok', Escape: 'pause', KeyP: 'pause', Backspace: 'back',
  };
  const pending = [];
  G.input = {
    down: {}, hits: {}, tap: null, tapCanvas: null, buf: [], log: {}, okLockUntil: 0,
    isDown(a) { return !!this.down[a]; },
    hit(a) { return !!this.hits[a]; },
    consume(a) { this.hits[a] = false; },
    okHit() { return this.hit('ok') && G.clk.ui >= this.okLockUntil; },
    consumeOk() { this.hits.ok = false; },
    lockOk(sec) { this.okLockUntil = G.clk.ui + sec; },
    mashHit() { return this.hit('attack') || this.hit('ok'); },
    buffered(a, win = 0.2) { return this.buf.some((b) => b.a === a && !b.used && G.clk.world - b.t <= win); },
    take(a, win = 0.2) { const b = this.buf.find((x) => x.a === a && !x.used && G.clk.world - x.t <= win); if (b) { b.used = true; return true; } return false; },
    count(a, win) { return (this.log[a] || []).filter((t) => G.clk.world - t <= win).length; },
    lastPress(a) { const l = this.log[a]; return l && l.length ? l[l.length - 1] : -Infinity; },
    beginStep() {
      while (pending.length) {
        const [a, dn] = pending.shift();
        if (dn) {
          if (!this.down[a]) { this.hits[a] = true; this.buf.push({ a, t: G.clk.world, used: false }); (this.log[a] = this.log[a] || []).push(G.clk.world); }
          this.down[a] = true;
        } else this.down[a] = false;
      }
      this.buf = this.buf.filter((b) => G.clk.world - b.t <= 0.3);
    },
    endStep() { this.hits = {}; this.tap = null; this.tapCanvas = null; },
    clear() { this.down = {}; this.buf = []; },
    // 自测用：直接按 / 放
    press(a) { pending.push([a, true]); pending.push([a, false]); },
    hold(a, on) { pending.push([a, !!on]); },
  };
  window.addEventListener('keydown', (e) => { const a = KEY[e.code]; if (!a) return; e.preventDefault(); if (!e.repeat) pending.push([a, true]); });
  window.addEventListener('keyup', (e) => { const a = KEY[e.code]; if (!a) return; e.preventDefault(); pending.push([a, false]); });
  window.addEventListener('blur', () => G.input.clear());

  // ---------------- audio（§4.4）桩：只记调用
  const calls = [];
  G.audio = {
    calls,
    sfx(name, o) { calls.push(['sfx', name]); return null; },
    loop(name, o) { calls.push(['loop', name]); return { stop() { calls.push(['loop_stop', name]); }, setVol() {}, setRate() {} }; },
    music(name) { calls.push(['music', name]); return Promise.resolve(); },
    stopMusic() {}, cue(name) { calls.push(['cue', name]); return { hitIn: 0 }; }, duck() {}, update() {},
  };

  // ---------------- 主循环与 render（§2.3 / §2.5）。自测时 G.__auto = false，由测试脚本 G.__step(n) 推进
  function step(dt) {
    G.clk.ui += dt;
    G.input.beginStep();
    const worldAdv = G.hitStopAll_t <= 0 && !(G.scene && G.scene.frozen);
    if (G.hitStopAll_t > 0) G.hitStopAll_t -= dt;
    if (G.slowAllT > 0) { G.slowAllT -= dt; if (G.slowAllT <= 0) G.slowAllK = 1; }
    const wdt = dt * G.slowAllK;
    if (G.scene) G.scene.update(dt, worldAdv, wdt);
    if (worldAdv) { G.clk.world += wdt; G.clk.flow += wdt * (G.time ? G.time.flowScale() : 1); }
    G.cam.shakeT += dt; if (G.cam.bumpDur) G.cam.bumpT += dt;
    if (G.flashA > 0) G.flashA = Math.max(0, G.flashA - dt / Math.max(0.01, G._flashDur || 0.25));
    G.waiters = G.waiters.filter((w) => {
      if (w.fn ? w.fn() : G.clk[w.clock] >= w.until) { w.res(); return false; }
      return true;
    });
    G.input.endStep();
  }
  G.__stepOne = step;
  G.__step = (n = 1) => { for (let i = 0; i < n; i++) step(1 / 60); G.__render(); };
  let renderMs = [], canvasMs = [];
  G.__perf = { renderMs, canvasMs };
  G.__render = function () {
    const t0 = performance.now();
    const wg = G.wg, s = G.scene;
    wg.setTransform(1, 0, 0, 1, 0, 0); wg.globalAlpha = 1; wg.globalCompositeOperation = 'source-over'; wg.imageSmoothingEnabled = false;
    wg.fillStyle = '#000'; wg.fillRect(0, 0, 320, 180);
    if (s && s.drawWorld) s.drawWorld(wg);
    const t1 = performance.now();
    const needPx = (G.fx && G.fx.hasPixel('mid')) || (G.fx && G.fx.hasPixel('over')) || (G.post && G.post.active()) || (s && s.hasPixel && s.hasPixel());
    if (needPx && G.px) {
      const P = G.px.begin(wg);
      if (s.drawPixel) s.drawPixel(P, 'mid');
      if (G.fx) G.fx.drawPixel(P, 'mid');
      if (G.post) G.post.apply(P, 'mid');
      if (!(s.hasOver && s.hasOver())) { if (G.fx) G.fx.drawPixel(P, 'over'); if (G.post) G.post.apply(P, 'final'); }
      G.px.end();
    }
    if (s && s.hasOver && s.hasOver()) {
      s.drawOver(wg);
      const P = G.px.begin(wg); if (G.fx) G.fx.drawPixel(P, 'over'); if (G.post) G.post.apply(P, 'final'); G.px.end();
    }
    if (G.flashA > 0) { wg.globalAlpha = G.flashA; wg.fillStyle = G.flashColor; wg.fillRect(0, 0, 320, 180); wg.globalAlpha = 1; }
    G.ug.clearRect(0, 0, 640, 360);
    if (s && s.drawUI) s.drawUI(G.ug);
    const sc = G.sctx, W2 = 320 * G.scale, H2 = 180 * G.scale;
    sc.imageSmoothingEnabled = false;
    sc.fillStyle = '#000'; sc.fillRect(0, 0, W2, H2);
    const b = G.cam.box();
    sc.drawImage(G.wv, b.x, b.y, b.w, b.h, 0, 0, W2, H2);
    sc.drawImage(G.uv, 0, 0, 640, 360, 0, 0, W2, H2);
    const t2 = performance.now();
    canvasMs.push(t1 - t0); renderMs.push(t2 - t0);
    if (canvasMs.length > 600) { canvasMs.shift(); renderMs.shift(); }
  };
  G.__auto = /auto=1/.test(location.search);
  let last = 0, acc = 0;
  function frame(nowMs) {
    if (G.__auto) {
      const dt = Math.min(0.1, (nowMs - last) / 1000); last = nowMs; acc += dt;
      let n = 0;
      while (acc >= 1 / 60 && n < 6) { step(1 / 60); acc -= 1 / 60; n++; }
      if (n === 6) acc = 0;
      G.__render();
    } else last = nowMs;
    requestAnimationFrame(frame);
  }
  G.start = () => requestAnimationFrame(frame);
})();
