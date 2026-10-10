// 背景图层（包 4）：照原工程 bg 模块的图层顺序和公式；类型表 G.BG_TYPES[type] = (g, L, camX, t, st) => {}（技术约定 §3.6）
'use strict';
(function () {
  const G = window.G;
  const W = () => G.W || 320, H = () => G.H || 180;
  const mod = (a, n) => ((a % n) + n) % n;
  // 统一偏移公式：o = floor(camX·k + t·vx) mod period（镜头往右为正，报告 06 §7.7）
  const offs = (camX, k, t, vx, period) => mod(Math.floor(camX * (k == null ? 1 : k) + t * (vx || 0)), period);
  const img = (key) => { const im = key ? G.image(key) : null; return im && G.ready(im) ? im : null; };
  const hash = (...xs) => (G.hash01 ? G.hash01(...xs) : 0.5);
  const cssCache = new Map();
  function css(c) {
    let v = cssCache.get(c);
    if (!v) {
      const a = G.rgbOf ? G.rgbOf(c) : [255, 255, 255];
      v = 'rgb(' + a[0] + ',' + a[1] + ',' + a[2] + ')';
      cssCache.set(c, v);
    }
    return v;
  }

  // 横向循环贴一条（图宽 ≥ period + 320 时一次贴完；图宽 = period 时分两段接上，同银魂 gfx.js:239-254）
  function wrapDraw(g, im, o, period, dy, sh, sy = 0) {
    const iw = im.width, w = W();
    const span = iw >= period + w ? iw : Math.min(iw, period);
    let dx = 0, sx = o, guard = 0;
    while (dx < w && guard++ < 8) {
      if (sx >= span) sx = mod(sx, span);
      const ww = Math.min(w - dx, span - sx);
      if (ww <= 0) break;
      g.drawImage(im, sx, sy, ww, sh, dx, dy, ww, sh);
      dx += ww; sx = 0;
    }
  }

  const T = {};
  G.BG_TYPES = T;

  // static：固定在屏幕
  T.static = (g, L) => { const im = img(L.image); if (im) g.drawImage(im, L.x || 0, L.y || 0); };

  // wrap：横向循环（k 视差、vx 自己按时间滚、h 只取上面 h 行）
  T.wrap = (g, L, camX, t, st) => {
    const im = img(L.image);
    if (!im) return;
    const period = L.period || im.width;
    const sp = st && st.state && st.state.speed != null ? st.state.speed : 1;
    const o = offs(camX, L.k, t * sp, L.vx, period);
    const sh = Math.min(L.h || im.height, im.height);
    wrapDraw(g, im, o, period, L.y || 0, sh);
  };

  // pano：不循环全景，画在 x − camX·k（school_gate）
  T.pano = (g, L, camX) => {
    const im = img(L.image);
    if (im) g.drawImage(im, (L.x || 0) - Math.floor(camX * (L.k == null ? 1 : L.k)), L.y || 0);
  };

  // image：单张图；screen 时固定屏幕坐标；flicker > 0 时透明度 1 − flicker·(0.5 + 0.5·sin13t·sin7.3t)
  T.image = (g, L, camX, t) => {
    const im = img(L.image);
    if (!im) return;
    const x = L.screen ? L.x || 0 : (L.x || 0) - Math.floor(camX * (L.k == null ? 1 : L.k));
    if (x > W() || x + im.width < 0) return;
    const fl = L.flicker === true ? 0.3 : L.flicker || 0;
    const ga = g.globalAlpha;
    if (fl > 0) g.globalAlpha = ga * Math.max(0, Math.min(1, 1 - fl * (0.5 + 0.5 * Math.sin(13 * t) * Math.sin(7.3 * t))));
    g.drawImage(im, x, L.y || 0);
    g.globalAlpha = ga;
  };

  // strip：烘好的循环帧条（横向），帧 floor(t·fps) mod n
  T.strip = (g, L, camX, t) => {
    const im = img(L.image);
    if (!im) return;
    const w = L.w || im.width / (L.n || 1), h = L.h || im.height, n = L.n || Math.max(1, Math.round(im.width / w));
    const f = mod(Math.floor(t * (L.fps || 0) + 1e-6), n);
    const x = L.screen ? L.x || 0 : (L.x || 0) - Math.floor(camX * (L.k == null ? 1 : L.k));
    if (x > W() || x + w < 0) return;
    g.drawImage(im, f * w, 0, w, h, x, L.y || 0, w, h);
  };

  // pick：按 stage.state[key]（0..1）选图（铁栏被掰弯）；有 values 选最接近的，否则第 round(v·(n−1)) 张
  T.pick = (g, L, camX, t, st) => {
    const ims = L.images || [];
    if (!ims.length) return;
    let v = st && st.state ? st.state[L.key] : 0;
    v = typeof v === 'number' ? v : v ? 1 : 0;
    let i = 0;
    if (L.values && L.values.length === ims.length) {
      let bd = 1e9;
      L.values.forEach((val, j) => { const d = Math.abs(val - v); if (d < bd - 1e-9) { bd = d; i = j; } });
    } else i = Math.round(Math.max(0, Math.min(1, v)) * (ims.length - 1));
    const im = img(ims[i]);
    if (im) g.drawImage(im, (L.x || 0) - Math.floor(camX * (L.k || 0)), L.y || 0);
  };

  // clouds：同银魂
  T.clouds = (g, L, camX, t) => {
    const span = L.span || W() + 200;
    for (const c of L.clouds || []) {
      const im = img(c.image);
      if (!im) continue;
      const x = mod(c.x0 + t * (c.vx || 0) - camX * (c.k || 0), span) - 100;
      g.drawImage(im, Math.floor(x), c.y || 0);
    }
  };

  // tint：整屏罩色；key 有值时：state[key] 是数字 = alpha 乘数，假 = 不画
  T.tint = (g, L, camX, t, st) => {
    let a = L.alpha == null ? 0.3 : L.alpha;
    if (L.key) {
      const v = st && st.state ? st.state[L.key] : undefined;
      if (typeof v === 'number') a *= v;
      else if (!v) return;
    }
    if (a <= 0) return;
    const ga = g.globalAlpha;
    g.globalAlpha = ga * Math.min(1, a);
    g.fillStyle = css(L.color || '#000000');
    g.fillRect(0, 0, W(), H());
    g.globalAlpha = ga;
  };

  // glow：预烘的光晕图，lighter 混合；flicker（true = 0.3）同 image 的公式
  T.glow = (g, L, camX, t) => {
    const im = img(L.image);
    if (!im) return;
    const fl = L.flicker === true ? 0.3 : L.flicker || 0;
    const a = (L.alpha == null ? 1 : L.alpha) * (fl > 0 ? 1 - fl * (0.5 + 0.5 * Math.sin(13 * t) * Math.sin(7.3 * t)) : 1);
    if (a <= 0) return;
    const x = L.screen ? L.x || 0 : (L.x || 0) - Math.floor(camX * (L.k == null ? 1 : L.k));
    const ga = g.globalAlpha, op = g.globalCompositeOperation;
    g.globalCompositeOperation = 'lighter';
    g.globalAlpha = ga * Math.min(1, a);
    g.drawImage(im, x, L.y || 0);
    g.globalAlpha = ga;
    g.globalCompositeOperation = op;
  };

  // stars：眨眼星 list:[[x, y, speed, phase, big, color]]（屏幕坐标；k 视差默认 0）
  T.stars = (g, L, camX, t) => {
    const k = L.k || 0, w = W();
    const ga = g.globalAlpha;
    for (const s of L.list || []) {
      const [x0, y, sp, ph, big, col] = s;
      const b = 0.5 + 0.5 * Math.sin(t * (sp || 1) + (ph || 0));
      if (b < 0.2) continue;
      const x = Math.round(mod(x0 - camX * k, w + 2));
      g.fillStyle = css(col || '#ffffff');
      g.globalAlpha = ga * (b > 0.75 ? 1 : b > 0.45 ? 0.75 : 0.5);
      g.fillRect(x, Math.round(y), 1, 1);
      if (big && b > 0.7) { g.globalAlpha = ga * 0.5; g.fillRect(x - 1, y, 1, 1); g.fillRect(x + 1, y, 1, 1); g.fillRect(x, y - 1, 1, 1); g.fillRect(x, y + 1, 1, 1); }
    }
    g.globalAlpha = ga;
  };

  // petals：飘落花瓣（照 school_gate：周期 4–7 s，从上往左下飘，sin(2.3t+i)·6 左右摆；vx = 一个周期横向漂多少 px，默认 −70）
  T.petals = (g, L, camX, t) => {
    const n = L.n || 26, seed = L.seed || 0, cols = L.colors || ['#ffd6e4', '#f4a0be'], w = W(), h = H();
    const y0 = L.y0 == null ? -6 : L.y0, y1 = L.y1 == null ? y0 + (L.vy || 190) : L.y1, vx = L.vx == null ? -70 : L.vx;
    const k = L.k == null ? 0.2 : L.k;
    for (let i = 0; i < n; i++) {
      const per = 4 + 3 * hash(i, 31, seed);
      const u = mod(t + hash(i, 32, seed) * per, per) / per;
      const xr = -20 + (w + 80) * hash(i, 33, seed) + u * vx + Math.sin(t * 2.3 + i) * 6 - camX * k;
      const x = Math.round(mod(xr + 20, w + 80) - 20), y = Math.round(y0 + u * (y1 - y0));
      if (x < -2 || x >= w || y < 0 || y >= h) continue;
      g.fillStyle = css(cols[i % cols.length]);
      g.fillRect(x, y, 1, 1);
      if (Math.floor(t * 6 + i) % 3 === 0) g.fillRect(x + 1, y, 1, 1);
    }
  };

  // neon：亮版招牌叠在暗底上（世界坐标，跟图层一起卷）；flick 的那几块 10 fps 判定：12% 灭一帧、15% 概率隔帧闪
  T.neon = (g, L, camX, t) => {
    const k = L.k == null ? 1 : L.k, period = L.period || 0, w = W(), kf = Math.floor(t * 10);
    (L.signs || []).forEach((s, i) => {
      const im = img(s.image);
      if (!im) return;
      let x = s.x - Math.floor(camX * k);
      if (period) { x = mod(x, period); if (x > w + 20) x -= period; }
      if (x > w || x + im.width < 0) return;
      if (s.flick) {
        const sd = s.seed == null ? i + 1 : s.seed;
        if (hash(kf, sd, 55) < 0.12 || (hash(Math.floor(kf / 6), sd, 56) < 0.15 && kf % 2)) return;
      }
      g.drawImage(im, x, s.y);
    });
  };

  // reflect：湿路面倒影（香港）：取图上 y 线以上 2n 行，2:1 压扁翻转，逐行 round(1.8·sin(r·1.3+6t)·(0.3+r/n)) 横晃，
  //          亮度减 30 后按 a0→a1 渐弱相加（原式 out = street + max(ref − 30, 0)·fade），每 4 行有一行暗 0.8
  //          有 image：用这张全景图（period / k 卷动）预先算好每一行；没有 image：直接反射画布上已经画好的东西（平滑透明，近似）
  const reflCache = new Map();
  function reflRows(L) {
    const key = L.image + '|' + L.y + '|' + L.n + '|' + L.a0 + '|' + L.a1;
    let R = reflCache.get(key);
    if (R) return R;
    const src = G.pix ? G.pix(L.image) : null;
    if (!src) return null;
    const n = L.n || 27, y = L.y == null ? 152 : L.y, w = src.w, a0 = L.a0 == null ? 0.62 : L.a0, a1 = L.a1 == null ? 0.27 : L.a1;
    const c = G.mkCanvas(w, n, true), cg = c.g || c.getContext('2d');
    const id = cg.createImageData(w, n), out = new Uint32Array(id.data.buffer), s = src.u32;
    for (let r = 0; r < n; r++) {
      const ya = y - 1 - 2 * r, yb = y - 2 - 2 * r, fade = (a0 + (a1 - a0) * (r / n)) * (r % 4 === 3 ? 0.8 : 1);
      for (let x = 0; x < w; x++) {
        const pa = ya >= 0 && ya < src.h ? s[ya * w + x] : 0, pb = yb >= 0 && yb < src.h ? s[yb * w + x] : 0;
        const rr = (((pa & 255) + (pb & 255)) >> 1) - 30, gg = ((((pa >>> 8) & 255) + ((pb >>> 8) & 255)) >> 1) - 30,
          bb = ((((pa >>> 16) & 255) + ((pb >>> 16) & 255)) >> 1) - 30;
        const R2 = Math.max(0, rr) * fade, G2 = Math.max(0, gg) * fade, B2 = Math.max(0, bb) * fade;
        out[r * w + x] = (0xff000000 | ((B2 & 255) << 16) | ((G2 & 255) << 8) | (R2 & 255)) >>> 0;
      }
    }
    cg.putImageData(id, 0, 0);
    R = { c, w, n };
    reflCache.set(key, R);
    return R;
  }
  T.reflect = (g, L, camX, t) => {
    const n = L.n || 27, y = L.y == null ? 152 : L.y, w = W();
    if (L.image) {
      const R = reflRows(L);
      if (!R) return;
      const period = L.period || R.w, o = offs(camX, L.k, 0, 0, period);
      const op = g.globalCompositeOperation;
      g.globalCompositeOperation = 'lighter';
      for (let r = 0; r < n; r++) {
        const dx = Math.round(1.8 * Math.sin(r * 1.3 + t * 6) * (0.3 + r / n));
        wrapDraw(g, R.c, mod(o - dx, period), period, y + 1 + r, 1, r);
      }
      g.globalCompositeOperation = op;
      return;
    }
    const cv = g.canvas, ga = g.globalAlpha, a0 = L.a0 == null ? 0.62 : L.a0, a1 = L.a1 == null ? 0.27 : L.a1;
    for (let r = n - 1; r >= 0; r--) {
      const dx = Math.round(1.8 * Math.sin(r * 1.3 + t * 6) * (0.3 + r / n)), sy = y - 1 - 2 * r;
      if (sy < 0) continue;
      g.globalAlpha = ga * (a0 + (a1 - a0) * (r / n)) * 0.6;
      g.drawImage(cv, 0, sy, w, 1, dx, y + 1 + r, w, 1);
    }
    g.globalAlpha = ga;
  };

  // ------------------------------------------------------------------ Background
  const badTypes = new Set();
  class Background {
    constructor(spec) {
      this.spec = spec || {};
      this.layers = this.spec.layers || [];
      this.fg = this.spec.fg || [];
    }
    draw(g, camX, t, st) { for (const L of this.layers) this.layer(g, L, camX, t, st); }
    // 前景（角色前面）：默认 alpha 1（和银魂不同）
    drawFg(g, camX, t, st) { for (const L of this.fg) this.layer(g, L, camX, t, st); }
    layer(g, L, camX, t, st) {
      if (!L) return;
      // 公共 key：stage.state[key] 为真才画（pick / tint 的 key 另有意思，它们自己处理）
      if (L.key && L.type !== 'pick' && L.type !== 'tint' && !(st && st.state && st.state[L.key])) return;
      const fn = T[L.type];
      if (!fn) {
        if (!badTypes.has(L.type)) { badTypes.add(L.type); if (G.dbg && G.dbg.ev) G.dbg.ev('bg_type_missing', { type: L.type }); }
        return;
      }
      const a = L.alpha == null ? 1 : L.alpha;
      if (a <= 0) return;
      const ga = g.globalAlpha, op = g.globalCompositeOperation;
      if (a < 1 && L.type !== 'tint' && L.type !== 'glow') g.globalAlpha = ga * a;
      if (L.blend && L.type !== 'glow') g.globalCompositeOperation = L.blend;
      fn(g, L, camX, t, st);
      g.globalAlpha = ga;
      g.globalCompositeOperation = op;
    }
  }
  G.Background = Background;
})();
