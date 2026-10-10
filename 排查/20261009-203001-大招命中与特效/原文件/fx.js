// 原工程 源码\engine\fx.py 的像素特效移植（同名同参、纯时间函数）+ 场景辅助函数 + 特效实例系统 G.fx（包 2）
// 约定（技术约定 §4.6）：G.FX.name(P, …位置参数, kw)；P = G.px 像素会话 {u32, w, h}；坐标 = 世界画布坐标；
// Python 的关键字参数全部放进最后一个对象 kw（键名照 Python：colour、r_max、t_end …），默认值照抄原文件。
// 原片手绘感：火焰 / 光环 / 旋涡 / 速度线保留 floor(t·12) 抽帧，位置用连续时间。无血。
'use strict';
(function () {
  const G = window.G;
  const px = G.px;
  const FX = {};
  G.FX = FX;

  // =================================================================== 基础
  const TAU = Math.PI * 2;
  const RAD = Math.PI / 180;
  const BAY = px.BAY;
  const pack = px.pack;
  const bay = (x, y) => BAY[((y & 3) << 2) | (x & 3)];

  // core.hash01（FNV 变体，非整数先 round(x·997)）；本地版本不走可变参数，热循环里不分配
  function mixh(h, x) {
    const v = Number.isInteger(x) ? x : Math.round(x * 997);
    h = (h ^ v) >>> 0;
    h = Math.imul(h, 16777619) >>> 0;
    h = (h ^ (h >>> 13)) >>> 0;
    h = Math.imul(h, 0x5BD1E995) >>> 0;
    return (h ^ (h >>> 15)) >>> 0;
  }
  function H(a, b, c, d, e) {
    let h = mixh(2166136261, a);
    if (b !== undefined) {
      h = mixh(h, b);
      if (c !== undefined) {
        h = mixh(h, c);
        if (d !== undefined) {
          h = mixh(h, d);
          if (e !== undefined) h = mixh(h, e);
        }
      }
    }
    return h / 4294967296;
  }
  FX._hash01 = H;

  // core.ease
  function ease(u, kind) {
    u = u < 0 ? 0 : u > 1 ? 1 : u;
    switch (kind) {
      case 'linear': return u;
      case 'in': return u * u;
      case 'out': return 1 - (1 - u) * (1 - u);
      case 'in3': return u * u * u;
      case 'out3': { const v = 1 - u; return 1 - v * v * v; }
      case 'back': { const s = 1.70158, v = u - 1; return v * v * ((s + 1) * v + s) + 1; }
      case 'bounce': {
        const n1 = 7.5625, d1 = 2.75;
        if (u < 1 / d1) return n1 * u * u;
        if (u < 2 / d1) { u -= 1.5 / d1; return n1 * u * u + 0.75; }
        if (u < 2.5 / d1) { u -= 2.25 / d1; return n1 * u * u + 0.9375; }
        u -= 2.625 / d1; return n1 * u * u + 0.984375;
      }
      case 'elastic':
        if (u === 0 || u === 1) return u;
        return Math.pow(2, -10 * u) * Math.sin((u * 10 - 0.75) * TAU / 3) + 1;
      case 'step': return u >= 1 ? 1 : 0;
      default: return u * u * (3 - 2 * u);                  // 'io'
    }
  }
  const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
  const lerp = (a, b, u) => a + (b - a) * u;
  const prog = (t, t0, t1) => (t1 <= t0 ? (t >= t1 ? 1 : 0) : clamp((t - t0) / (t1 - t0)));
  const tr = Math.trunc;
  const rnd = Math.round;
  const fmod1 = v => v - Math.floor(v);                    // Python x % 1.0（结果非负）
  const EMPTY_SIG = [];
  // 世界路径随镜头移动时复用点容器，避免常驻弹道每帧制造临时数组。
  function offsetPoints(src, dst, cx, cy) {
    dst.length = src.length;
    for (let i = 0; i < src.length; i++) {
      const p = src[i];
      if (!Array.isArray(p)) { dst[i] = p; continue; }
      const q = Array.isArray(dst[i]) ? dst[i] : (dst[i] = []);
      if (Array.isArray(p[0])) offsetPoints(p, q, cx, cy);
      else {
        q.length = p.length;
        q[0] = p[0] - cx; q[1] = p[1] - cy;
        for (let j = 2; j < p.length; j++) q[j] = p[j];
      }
    }
    return dst;
  }
  const def = (v, d) => (v === undefined || v === null ? d : v);
  FX._ease = ease;

  // 颜色：一律转成打包整数 0xAABBGGRR
  const col = c => (typeof c === 'number' ? c >>> 0 : px.rgb(c));
  const cR = v => v & 255, cG = v => (v >>> 8) & 255, cB = v => (v >>> 16) & 255;
  const dark = (c, k = 0.5) => px.dark(c, k);
  const light = (c, k = 0.5) => px.light(c, k);
  const mix = (a, b, u) => px.mix(a, b, u);
  const WHITE = pack(255, 255, 255), BLACK = pack(0, 0, 0);

  // 调色板（暗 → 亮），同 fx.PALETTES / fx.IMPACT
  const PALETTES = {
    fire: ['#5a0c1c', '#b8182a', '#e8501a', '#ff9820', '#ffd840', '#fffbe0'],
    blue: ['#101848', '#2440b0', '#3c88f0', '#58d0f8', '#b8f4ff', '#ffffff'],
    green: ['#08381c', '#15803c', '#28c860', '#80f0a0', '#e0ffe8'],
    purple: ['#200838', '#5a2890', '#9a4ce0', '#d090ff', '#fbe8ff'],
    gold: ['#4a2a06', '#a86a10', '#e0a020', '#ffd83c', '#fff8c0'],
    ts_yellow: ['#12140a', '#343a1c', '#626a34', '#98a05a', '#cfd490', '#f6f6d0'],
    ts_blue: ['#0a0c20', '#1c2856', '#364e92', '#6484c4', '#a4c0ea', '#e6f0ff'],
    ts_gray: ['#101014', '#34343c', '#5c5c66', '#8a8a94', '#bebec6', '#f0f0f4'],
    ts_purple: ['#120a20', '#34205a', '#5e4094', '#9270c8', '#c8b0ec', '#f4ecff'],
    ts_green: ['#08140c', '#1a3a24', '#34684a', '#5e9a72', '#9cd0a8', '#e0f8e4'],
    sepia: ['#1e1208', '#42301a', '#6e5230', '#9c7a4c', '#c8a874', '#eedcae'],
  };
  const IMPACT = {
    bw: ['#000000', '#ffffff'],
    bw3: ['#000000', '#8a8a96', '#ffffff'],
    red: ['#16000a', '#d81c38', '#ffe8d8'],
    purple: ['#1c0832', '#8a34d0', '#ffe040'],
    yellow: ['#1a0c00', '#e09a18', '#fffbe0'],
    blue: ['#040a24', '#2c58e0', '#d8f4ff'],
    green: ['#021a0c', '#18b060', '#f0ffe0'],
  };
  FX.PALETTES = PALETTES;
  FX.IMPACT = IMPACT;
  const palCache = new Map();
  // 调色板名 / 颜色数组 → 打包色数组（缓存）
  function pal(p) {
    const key = typeof p === 'string' ? p : (Array.isArray(p) ? p.join(',') : String(p));
    let v = palCache.get(key);
    if (!v) {
      const src = typeof p === 'string' ? (PALETTES[p] || PALETTES.fire) : p;
      v = Uint32Array.from(src.map(col));
      palCache.set(key, v);
      if (palCache.size > 64) palCache.delete(palCache.keys().next().value);
    }
    return v;
  }
  const TS_TINT = { yellow: 'ts_yellow', blue: 'ts_blue', gray: 'ts_gray', grey: 'ts_gray', purple: 'ts_purple', green: 'ts_green' };
  const tsPal = tint => (typeof tint === 'string' ? (TS_TINT[tint] || tint) : tint);

  const rmax = (P, cx, cy) => Math.hypot(Math.max(cx, P.w - cx), Math.max(cy, P.h - cy)) + 2;
  function dbgEv(type, data) { try { if (G.dbg && G.dbg.ev) G.dbg.ev(type, data); } catch (e) { /* 调试记录失败不影响画面 */ }
  }

  // 4 角像素星（fx._star_shape）
  function star(P, x, y, r, c, thin) {
    x = rnd(x); y = rnd(y); r = rnd(r);
    if (r <= 0) { px.dot(P, x, y, c); return; }
    px.line(P, x - r, y, x + r, y, c);
    px.line(P, x, y - r, x, y + r, c);
    if (!thin && r >= 3) {
      px.line(P, x - 1, y - 1, x + 1, y + 1, c);
      px.line(P, x - 1, y + 1, x + 1, y - 1, c);
      if (r >= 5) {
        px.line(P, x - r + 1, y - 1, x + r - 1, y - 1, c);
        px.line(P, x - r + 1, y + 1, x + r - 1, y + 1, c);
        px.line(P, x - 1, y - r + 1, x - 1, y + r - 1, c);
        px.line(P, x + 1, y - r + 1, x + 1, y + r - 1, c);
      }
    }
  }
  // 单点（fx._px：round + 抖动）
  const dotA = (P, x, y, c, a) => px.plot(P, x, y, c, a);

  // =================================================================== 纹理（fxtex）
  const texCache = new Map();
  // Mulberry32：JS 里复现不了 numpy 的随机数，兜底纹理用它（视觉等价）
  function rng32(seed) {
    let s = seed >>> 0;
    return function () {
      s = (s + 0x6D2B79F5) >>> 0;
      let t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  // fx._noise_tex 的同算法版本（可平铺 value noise，[0,1]）
  function genNoise(seed, w, h, cells, octaves) {
    const rand = rng32(1000 + seed);
    const out = new Float32Array(w * h);
    let amp = 1, tot = 0, n = cells;
    for (let o = 0; o < octaves; o++) {
      const g = new Float32Array(n * n);
      for (let i = 0; i < n * n; i++) g[i] = rand();
      for (let y = 0; y < h; y++) {
        const ys = y / h * n, y0 = Math.floor(ys);
        let fy = ys - y0; fy = fy * fy * (3 - 2 * fy);
        for (let x = 0; x < w; x++) {
          const xs = x / w * n, x0 = Math.floor(xs);
          let fx_ = xs - x0; fx_ = fx_ * fx_ * (3 - 2 * fx_);
          const a = g[(y0 % n) * n + (x0 % n)], b = g[(y0 % n) * n + ((x0 + 1) % n)];
          const c = g[((y0 + 1) % n) * n + (x0 % n)], d = g[((y0 + 1) % n) * n + ((x0 + 1) % n)];
          const top = a + (b - a) * fx_, bot = c + (d - c) * fx_;
          out[y * w + x] += amp * (top + (bot - top) * fy);
        }
      }
      tot += amp; amp *= 0.5; n *= 2;
    }
    let mn = Infinity, mxv = -Infinity;
    for (let i = 0; i < out.length; i++) { out[i] /= tot; if (out[i] < mn) mn = out[i]; if (out[i] > mxv) mxv = out[i]; }
    const k = 1 / Math.max(1e-6, mxv - mn);
    for (let i = 0; i < out.length; i++) out[i] = (out[i] - mn) * k;
    return out;
  }
  function imgReady(key) {
    const D = G.D;
    return !!(key && D && D.img && D.img[key] && G.pix);
  }
  // 64×64 噪声纹理（Float32Array，[y·64 + x]）：优先用构建好的 fx/noise<seed>，没有就用 JS 兜底
  function noiseTex(seed) {
    seed = ((seed % 4) + 4) % 4;
    let v = texCache.get('n' + seed);
    if (v) return v;
    const D = G.D, keys = D && D.fxtex && D.fxtex.noise;
    const key = keys && keys[seed];
    if (imgReady(key)) {
      const p = G.pix(key);
      if (p && p.w === 64 && p.h === 64) {
        v = new Float32Array(4096);
        for (let i = 0; i < 4096; i++) v[i] = (p.u32[i] & 255) / 255;
        texCache.set('n' + seed, v);
        return v;
      }
      // 图还没解码：先用兜底，下一帧再试
    }
    v = texCache.get('nf' + seed);
    if (!v) { v = genNoise(seed, 64, 64, 4, 3); texCache.set('nf' + seed, v); if (key) dbgEv('fx_tex_fallback', { tex: 'noise' + seed }); }
    if (!key) texCache.set('n' + seed, v);
    return v;
  }
  FX._noise_tex = noiseTex;

  // fx._fog_tex 同算法（H × 512 可平铺雾纹理）
  function fogTex(seed, Hh) {
    const key = 'fog' + seed + '|' + Hh;
    let v = texCache.get(key);
    if (v) return v;
    const rand = rng32(500 + seed), W2 = 512;
    v = new Float32Array(Hh * W2);
    let amp = 1, tot = 0;
    for (const [cy, cx] of [[5, 8], [9, 16], [18, 32]]) {
      const g = new Float32Array(cy * cx);
      for (let i = 0; i < g.length; i++) g[i] = rand();
      for (let y = 0; y < Hh; y++) {
        const ys = y / Hh * cy, y0 = Math.floor(ys);
        let fy = ys - y0; fy = fy * fy * (3 - 2 * fy);
        const ya = (y0 % cy) * cx, yb = Math.min(y0 + 1, cy - 1) * cx;
        for (let x = 0; x < W2; x++) {
          const xs = x / W2 * cx, x0 = Math.floor(xs);
          let fx_ = xs - x0; fx_ = fx_ * fx_ * (3 - 2 * fx_);
          const a = g[ya + (x0 % cx)], b = g[ya + ((x0 + 1) % cx)], c = g[yb + (x0 % cx)], d = g[yb + ((x0 + 1) % cx)];
          const top = a + (b - a) * fx_, bot = c + (d - c) * fx_;
          v[y * W2 + x] += amp * (top + (bot - top) * fy);
        }
      }
      tot += amp; amp *= 0.5;
    }
    let mn = Infinity, mxv = -Infinity;
    for (let i = 0; i < v.length; i++) { v[i] /= tot; if (v[i] < mn) mn = v[i]; if (v[i] > mxv) mxv = v[i]; }
    for (let i = 0; i < v.length; i++) v[i] = (v[i] - mn) / Math.max(1e-6, mxv - mn);
    texCache.set(key, v);
    return v;
  }

  // scipy.ndimage.gaussian_filter（mode 'reflect'、truncate 4.0）的一维版，可分离
  function gaussRows(src, w, h, sigma, axis) {
    const rad = Math.trunc(4 * sigma + 0.5), k = new Float64Array(2 * rad + 1);
    let s = 0;
    for (let i = -rad; i <= rad; i++) { k[i + rad] = Math.exp(-0.5 * i * i / (sigma * sigma)); s += k[i + rad]; }
    for (let i = 0; i < k.length; i++) k[i] /= s;
    const out = new Float32Array(w * h);
    const n = axis === 0 ? h : w;
    const refl = j => {                                     // 'reflect'：d c b a | a b c d | d c b a
      const p = 2 * n;
      j = ((j % p) + p) % p;
      return j < n ? j : p - 1 - j;
    };
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        let acc = 0;
        for (let i = -rad; i <= rad; i++) {
          const v = axis === 0 ? src[refl(y + i) * w + x] : src[y * w + refl(x + i)];
          acc += v * k[i + rad];
        }
        out[y * w + x] = acc;
      }
    }
    return out;
  }
  // fx._ankh_field(S)：{ core, up, w, h, pad }；优先用构建好的 fx/ankh<S>（R = core、G = up），没有就在 JS 里算（含高斯）
  function ankhField(S) {
    S = Math.max(4, S | 0);
    const ck = 'ankh' + S;
    let v = texCache.get(ck);
    if (v) return v;
    const D = G.D, fxt = D && D.fxtex;
    const key = fxt && fxt.ankh && fxt.ankh[S];
    if (imgReady(key)) {
      const p = G.pix(key);
      if (p) {
        const k = (fxt.ankhScale && fxt.ankhScale[S]) || 1, n = p.w * p.h;
        const core = new Float32Array(n), up = new Float32Array(n);
        for (let i = 0; i < n; i++) { const c = p.u32[i]; core[i] = (c & 255) / 255 * k; up[i] = ((c >>> 8) & 255) / 255 * k; }
        const pad = fxt.ankhPad && fxt.ankhPad[S] != null ? fxt.ankhPad[S] : Math.max(6, tr(S * 0.3));
        v = { core, up, w: p.w, h: p.h, pad };
        texCache.set(ck, v);
        return v;
      }
      return computeAnkh(S, false);                         // 图还没解码：这一帧用算的，不缓存
    }
    return computeAnkh(S, true);
  }
  function computeAnkh(S, store) {
    const pad = Math.max(6, tr(S * 0.3)), w = tr(S * 0.9) + 2 * pad, h = S + 2 * pad;
    const m = new Float32Array(w * h), cx = w / 2, top = pad;
    const lx = S * 0.19, ly = S * 0.22, lcy = top + ly;
    const by0 = top + S * 0.44, by1 = top + S * 0.56, armw = S * 0.44;
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const ex = (x + 0.5 - cx) / lx, ey = (y + 0.5 - lcy) / ly;
        const dd = Math.sqrt(ex * ex + ey * ey);
        const ring = Math.abs(dd - 0.84) * Math.min(lx, ly) < S * 0.062;
        const ax = Math.abs(x + 0.5 - cx), flare = (ax / armw) * S * 0.05;
        const bar = ax < armw && y + 0.5 > by0 - flare && y + 0.5 < by1 + flare;
        const sv = (y + 0.5 - by1) / (S * 0.44);
        const stem = y + 0.5 >= by0 && sv <= 1 && ax < S * (0.075 + 0.07 * clamp(sv));
        m[y * w + x] = ring || bar || stem ? 1 : 0;
      }
    }
    const sig = S * 0.018 + 0.7;
    let core = gaussRows(gaussRows(m, w, h, sig, 0), w, h, sig, 1);
    let mx = 1e-3;
    for (let i = 0; i < core.length; i++) if (core[i] > mx) mx = core[i];
    for (let i = 0; i < core.length; i++) core[i] /= mx;
    const up = new Float32Array(w * h), K = Math.max(3, tr(S * 0.3));
    for (let k = 1; k <= K; k++) {
      const wt = Math.pow(1 - k / (K + 1), 0.8);
      for (let y = 0; y < h - k; y++) for (let x = 0; x < w; x++) {
        const v = core[(y + k) * w + x] * wt;
        if (v > up[y * w + x]) up[y * w + x] = v;
      }
    }
    const v = { core, up, w, h, pad };
    if (store) texCache.set('ankh' + S, v);
    return v;
  }
  FX._ankh_field = ankhField;

  // =================================================================== 精灵（图集 id + 逻辑动作 + 帧）
  // sprite.PAL：程序兜底图（拳头、宝石、蝙蝠、人形）用
  const SPAL = {
    k: '#1a1020', K: '#000000', w: '#ffffff', W: '#efe6d2', '1': '#c4c4d4', '2': '#7c7c90', '3': '#4a4a5c',
    s: '#f6c49a', S: '#d8946c', d: '#9a5e3a', D: '#6e3e24', r: '#e0303c', R: '#901828', o: '#f5902a', O: '#b85c1c',
    y: '#ffd83c', Y: '#c89a20', g: '#3cc060', G: '#1e7a3c', l: '#9cef6a', c: '#48d8e8', C: '#1e8a9a', b: '#3c64dc',
    B: '#1e2860', u: '#9cc8ff', U: '#5a9ae6', p: '#9a4ce0', P: '#5a2890', v: '#7a70d8', V: '#4a3a9a', m: '#f058b4',
    M: '#a02878', h: '#8a5a34', H: '#5a361e', t: '#d8b878', T: '#a8844c', z: '#d8e0ec', Z: '#8a94a8', f: '#f08888',
    e: '#20182a',
  };
  // ASCII 网格 → {u32, w, h, ox, oy}（锚点默认在中心，同 fx._grid + 调用处的 −w/2、−h/2）
  function gridImg(g, pal2) {
    const lines = g.split('\n').map(s => s.trim()).filter(s => s.length);
    const w = Math.max(...lines.map(s => s.length)), h = lines.length;
    const u = new Uint32Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < lines[y].length; x++) {
      const ch = lines[y][x];
      const v = (pal2 && pal2[ch] !== undefined) ? pal2[ch] : SPAL[ch];
      if (v) u[y * w + x] = col(v) | 0xff000000;
    }
    return { u32: u, w, h, ox: w / 2, oy: h / 2 };
  }
  function cropOpaque(p) {
    let x0 = p.w, y0 = p.h, x1 = -1, y1 = -1;
    for (let y = 0; y < p.h; y++) for (let x = 0; x < p.w; x++) if (p.u32[y * p.w + x] >>> 24) {
      if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
    }
    if (x1 < 0) return null;
    const w = x1 - x0 + 1, h = y1 - y0 + 1, u = new Uint32Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) u[y * w + x] = p.u32[(y + y0) * p.w + x + x0];
    return { u32: u, w, h, ox: w / 2, oy: h / 2, bx: x0, by: y0 };
  }
  function atlasOf(cid) {
    const D = G.D;
    if (!D || typeof cid !== 'string') return null;
    if (cid.indexOf('prop:') === 0) { const id = cid.slice(5); return D.props && D.props[id] && G.propAtlas ? G.propAtlas(id) : null; }
    if (cid.indexOf('scene:') === 0) { const id = cid.slice(6); return D.scene && D.scene[id] && G.propAtlas ? G.propAtlas(cid) : null; }
    return D.chars && D.chars[cid] && G.atlas ? G.atlas(cid) : null;
  }
  // 'starplat' + 'fist' / 'starplat.fist' / 'prop.knife' / 'prop:knife' / 'scene:s07_coin' → [cid, logical]
  function splitName(src, logical) {
    let cid = String(src), lg = logical;
    if (cid.indexOf(':') < 0) {
      const k = cid.indexOf('.');
      if (k > 0) { if (lg == null) lg = cid.slice(k + 1); cid = cid.slice(0, k); }
      if (cid === 'prop') { cid = 'prop:' + lg; lg = 'idle'; }
    }
    return [cid, lg == null ? 'idle' : lg];
  }
  const pixCache = new Map();
  // → {u32, w, h, ox, oy}（不翻转）| null。exact：要求图集里真有这个动作（不走回退）
  function sprPix(src, logical, frame, exact) {
    if (!src) return null;
    if (src.u32) return src;
    const [cid, lg] = splitName(src, logical);
    const key = cid + '|' + lg + '|' + (frame | 0) + (exact ? '|x' : '');
    const hit = pixCache.get(key);
    if (hit) return hit;
    const A = atlasOf(cid);
    if (!A || !A.pix) return null;
    if (exact && A.has && !A.has(lg)) return null;
    let p = null;
    try { p = A.pix(lg, frame | 0, false); } catch (e) { p = null; }
    if (!p || !p.u32) return null;
    const v = { u32: p.u32, w: p.w, h: p.h, ox: p.ox || 0, oy: p.oy || 0 };
    pixCache.set(key, v);
    if (pixCache.size > 400) pixCache.delete(pixCache.keys().next().value);
    return v;
  }
  FX._sprPix = sprPix;
  const exists = (src, logical) => !!sprPix(src, logical, 0);

  // 精灵变体（outline → tint → flip → scale → rotate，同 sprite._variant），锚点 = pivot
  const sv = (p, o) => px.variant(p, 0, 0, p.w, p.h, Object.assign({ ax: p.ox, ay: p.oy }, o));

  // fx._figure：程序人形剪影（精灵缺失时兜底），锚点脚底中心
  const figCache = new Map();
  function figureImg(colour, w = 26, h = 44) {
    const c0 = col(colour === undefined ? [200, 160, 255] : colour);
    const key = c0 + '|' + w + '|' + h;
    let v = figCache.get(key);
    if (v) return v;
    const B = px.buffer(w, h);
    const k = pack(26, 16, 32) | 0, c = c0 | 0xff000000, l = light(c0, 0.45) | 0xff000000, cx = w >> 1, hr = Math.max(3, Math.floor(w / 5));
    px.box(B, cx - 5, h - 16, cx - 2, h - 1, k); px.box(B, cx + 1, h - 16, cx + 4, h - 1, k);
    px.box(B, cx - 4, h - 15, cx - 3, h - 2, c); px.box(B, cx + 2, h - 15, cx + 3, h - 2, c);
    px.poly(B, [[cx - 9, 2 * hr + 3], [cx + 9, 2 * hr + 3], [cx + 5, h - 15], [cx - 6, h - 15]], k);
    px.poly(B, [[cx - 8, 2 * hr + 4], [cx + 8, 2 * hr + 4], [cx + 4, h - 16], [cx - 5, h - 16]], c);
    px.line(B, cx - 6, 2 * hr + 6, cx - 3, h - 18, l);
    px.box(B, cx - 12, 2 * hr + 4, cx - 9, 2 * hr + 16, k); px.box(B, cx + 9, 2 * hr + 4, cx + 12, 2 * hr + 16, k);
    px.box(B, cx - 11, 2 * hr + 5, cx - 10, 2 * hr + 15, c); px.box(B, cx + 10, 2 * hr + 5, cx + 11, 2 * hr + 15, c);
    px.ellipse(B, cx - hr - 1, 0, cx + hr + 1, 2 * hr + 3, k, null);
    px.ellipse(B, cx - hr, 1, cx + hr, 2 * hr + 2, c, null);
    px.dot(B, cx - 2, hr + 1, WHITE); px.dot(B, cx + 2, hr + 1, WHITE);
    v = { u32: B.u32, w, h, ox: w / 2, oy: h };
    figCache.set(key, v);
    return v;
  }
  FX._figure = figureImg;
  // 精灵或兜底人形
  const sprOrFig = (src, logical, frame, colour) => sprPix(src, logical, frame) || figureImg(colour);

  // sprite.aura：剪影 4 邻域膨胀 grow 次、涂成 colour、平滑 alpha 贴在精灵后面，±1 px 抖动（先画光环再画精灵）
  function auraDraw(P, p, x, y, flip, scale, colour, t, alpha = 0.55, grow = 1) {
    if (alpha <= 0) return;
    const base = sv(p, { flip, scale });
    const v = px.variant(base, 0, 0, base.w, base.h, { grow, sil: colour, ax: base.ax, ay: base.ay });
    px.stamp(P, v, x + rnd(Math.sin(t * 23)), y + rnd(Math.cos(t * 17)), 1, alpha);
  }
  FX.aura = function (P, src, x, y, kw) {
    kw = kw || {};
    const p = sprPix(src, kw.logical, kw.frame | 0);
    if (!p) return;
    auraDraw(P, p, x, y, !!kw.flip, def(kw.scale, 1), def(kw.colour, '#c080ff'), def(kw.t, 0), def(kw.alpha, 0.55), def(kw.grow, 1));
  };
  // 精灵直接贴（sprite.draw：平滑 alpha）
  FX.sprite = function (P, src, x, y, kw) {
    kw = kw || {};
    const p = sprPix(src, kw.logical, kw.frame | 0);
    if (!p) return false;
    const o = { flip: !!kw.flip, scale: def(kw.scale, 1) };
    if (kw.tint) o.tint = kw.tint;
    if (kw.outline) o.outline = kw.outline;
    if (kw.rot) o.rotDeg = -kw.rot;                         // 原约定逆时针为正；px 顺时针为正
    px.stamp(P, sv(p, o), x, y, def(kw.dither, 1), def(kw.alpha, 1));
    return true;
  };

  // =================================================================== 基础
  // fx.shadow：脚下两级扁椭圆，对已有像素做乘法变暗
  FX.shadow = function (P, x, y, kw) {
    kw = kw || {};
    const w = Math.max(2, rnd(def(kw.w, 14))), alpha = def(kw.alpha, 0.35);
    const h = kw.h ? tr(kw.h) : Math.max(2, rnd(w * 0.28));
    const x0 = rnd(x - w / 2), y0 = rnd(y - h / 2), u = P.u32;
    const m1 = 1 - alpha, m2 = 1 - alpha * 0.55;
    for (let yy = Math.max(0, y0); yy < Math.min(P.h, y0 + h); yy++) {
      const ey = (yy - y0 + 0.5 - h / 2) / (h / 2);
      for (let xx = Math.max(0, x0); xx < Math.min(P.w, x0 + w); xx++) {
        const ex = (xx - x0 + 0.5 - w / 2) / (w / 2), d = ex * ex + ey * ey;
        if (d > 1) continue;
        const m = d <= 0.45 ? m1 : m2, i = yy * P.w + xx, v = u[i];
        u[i] = pack((v & 255) * m, ((v >>> 8) & 255) * m, ((v >>> 16) & 255) * m);
      }
    }
  };

  // fx.speedlines：漫画速度线，每秒重随机 fps 次；alpha < 1 直接带抖动画（与“先画层再整层抖动”结果一致）
  FX.speedlines = function (P, t, kw) {
    kw = kw || {};
    const alpha = def(kw.alpha, 1);
    if (alpha <= 0) return;
    const cx = def(kw.cx, P.w / 2), cy = def(kw.cy, P.h / 2), style = kw.style || 'radial', n = def(kw.n, 48);
    const c = col(def(kw.colour, 'white')), inner = def(kw.inner, 40), seed = def(kw.seed, 0), fps = def(kw.fps, 12);
    const wd0 = kw.width ? kw.width[0] : 1, wd1 = kw.width ? kw.width[1] : 5, band = kw.band || null;
    const k = Math.floor(t * fps);
    if (style === 'radial') {
      const Rr = rmax(P, cx, cy) + 6;
      for (let i = 0; i < n; i++) {
        if (H(seed, k, i, 9) < 0.12) continue;
        const a = TAU * (i + H(seed, k, i, 1) * 0.9) / n;
        const r0 = inner * (0.75 + 0.9 * H(seed, k, i, 2));
        const h3 = H(seed, k, i, 3), wd = wd0 + (wd1 - wd0) * h3 * h3;
        const ca = Math.cos(a), sa = Math.sin(a), hw = wd / 2 * Rr / 180;
        px.tri(P, cx + ca * r0, cy + sa * r0, cx + ca * Rr - sa * hw, cy + sa * Rr + ca * hw,
          cx + ca * Rr + sa * hw, cy + sa * Rr - ca * hw, c, alpha);
      }
      return;
    }
    const horiz = style === 'horizontal', span = horiz ? P.h : P.w, along = horiz ? P.w : P.h, centre = horiz ? cy : cx;
    for (let i = 0; i < n; i++) {
      let p = -2 + (span + 4) * H(seed, k, i, 1);
      if (band) p = band[0] + (band[1] - band[0]) * H(seed, k, i, 1);
      else if (inner && Math.abs(p - centre) < inner / 2) continue;
      const L = along * 0.12 + (along * 0.6 - along * 0.12) * H(seed, k, i, 2);
      const s = -L * 0.5 + (along + L * 0.5) * H(seed, k, i, 3);
      const th = wd0 + (wd1 - wd0) * Math.pow(H(seed, k, i, 4), 1.6);
      const flipEnd = H(seed, k, i, 5) < 0.5;
      if (horiz) {
        if (flipEnd) px.tri(P, s + L, p, s, p - th / 2, s, p + th / 2, c, alpha);
        else px.tri(P, s, p, s + L, p - th / 2, s + L, p + th / 2, c, alpha);
      } else if (flipEnd) px.tri(P, p, s + L, p - th / 2, s, p + th / 2, s, c, alpha);
      else px.tri(P, p, s, p - th / 2, s + L, p + th / 2, s + L, c, alpha);
    }
  };

  // fx.impact_frame：整幅高反差冲击帧。style：'invert' | IMPACT 名 | 2–3 色数组；阈值自适应（2 色中位数，3 色 38% / 72% 分位）
  let lumBuf = null;
  const hist = new Uint32Array(256);
  function pctl(n, q) {                                    // numpy.percentile（线性插值）在直方图上的版本
    const pos = (n - 1) * q, lo = Math.floor(pos), f = pos - lo;
    let acc = 0, vlo = -1, vhi = -1;
    for (let b = 0; b < 256; b++) {
      acc += hist[b];
      if (vlo < 0 && acc > lo) vlo = b;
      if (acc > lo + 1) { vhi = b; break; }
    }
    if (vhi < 0) vhi = vlo;
    return vlo + (vhi - vlo) * f;
  }
  FX.impact_frame = function (P, kw) {
    if (typeof kw === 'string' || Array.isArray(kw)) kw = { style: kw };
    kw = kw || {};
    const style = def(kw.style, 'invert');
    if (style === 'invert') { px.invert(P); return; }
    const pl = pal(typeof style === 'string' ? (IMPACT[style] || IMPACT.bw) : style), L = pl.length;
    const u = P.u32, n = u.length;
    if (!lumBuf || lumBuf.length !== n) lumBuf = new Float32Array(n);
    let t1, t2 = Infinity;
    if (kw.threshold != null) {
      if (L === 2) t1 = kw.threshold * 255; else { t1 = kw.threshold * 255 * 0.6; t2 = kw.threshold * 255 * 1.3; }
      for (let i = 0; i < n; i++) { const v = u[i]; lumBuf[i] = (v & 255) * 0.299 + ((v >>> 8) & 255) * 0.587 + ((v >>> 16) & 255) * 0.114; }
    } else {
      hist.fill(0);
      for (let i = 0; i < n; i++) {
        const v = u[i], l = (v & 255) * 0.299 + ((v >>> 8) & 255) * 0.587 + ((v >>> 16) & 255) * 0.114;
        lumBuf[i] = l; hist[l > 255 ? 255 : l | 0]++;
      }
      if (L === 2) t1 = pctl(n, 0.5); else { t1 = pctl(n, 0.38); t2 = pctl(n, 0.72); }
    }
    const a1 = t1 + 0.01, a2 = t2 + 0.01;
    const c0 = pl[0], c1 = pl[1], c2 = pl[L > 2 ? 2 : 1];
    for (let i = 0; i < n; i++) {
      const l = lumBuf[i];
      const idx = (l > a1 ? 1 : 0) + (L > 2 && l > a2 ? 1 : 0);
      u[i] = idx === 0 ? c0 : idx === 1 ? c1 : c2;
    }
  };

  // fx.hit_spark：打击点星爆（闪光帧 → 圆环 + 长刺 → 飞散碎线）
  const _angs = new Float64Array(8), _lens = new Float64Array(8);
  function spike(P, x, y, ang, rIn, rOut, wd, c) {
    const ca = Math.cos(ang), sa = Math.sin(ang), rm = rIn + (rOut - rIn) * 0.3;
    px.quad(P, x + ca * rIn, y + sa * rIn, x + ca * rm - sa * wd, y + sa * rm + ca * wd,
      x + ca * rOut, y + sa * rOut, x + ca * rm + sa * wd, y + sa * rm - ca * wd, c);
  }
  FX.hit_spark = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 0.2), dt = t - t0;
    if (dt < 0 || dt >= dur) return;
    const u = dt / dur, S = def(kw.size, 12), c = col(def(kw.colour, 'white')), acc = col(def(kw.accent, '#ffd83c'));
    const sd = def(kw.seed, 0) * 131 + tr(t0 * 97) + tr(x) * 7 + tr(y);
    const rot = H(sd, 7) * TAU;
    for (let i = 0; i < 8; i++) {
      _angs[i] = rot + TAU * i / 8 + (H(sd, i, 1) - 0.5) * 0.35;
      _lens[i] = (i % 2 === 0 ? 1.45 : 0.9) * (0.8 + 0.4 * H(sd, i, 2));
    }
    if (u < 0.22) {
      px.disc(P, x, y, S * 0.55, acc);
      px.disc(P, x, y, S * 0.42, c);
      for (let i = 0; i < 8; i++) spike(P, x, y, _angs[i], S * 0.3, S * _lens[i], i % 2 === 0 ? 3 : 2, c);
    } else if (u < 0.5) {
      const r = S * (0.5 + 0.35 * (u - 0.22) / 0.28);
      for (let i = 0; i < 8; i++) {
        spike(P, x, y, _angs[i], S * 0.45, S * _lens[i] * 1.15, i % 2 === 0 ? 2.2 : 1.4, acc);
        const ca = Math.cos(_angs[i]), sa = Math.sin(_angs[i]);
        px.line(P, x + ca * S * 0.5, y + sa * S * 0.5, x + ca * S * _lens[i] * 0.95, y + sa * S * _lens[i] * 0.95, c);
      }
      px.ellipse(P, x - r, y - r, x + r, y + r, null, c, S >= 10 ? 2 : 1);
      px.disc(P, x, y, Math.max(1, S * 0.14), c);
    } else {
      const v = (u - 0.5) / 0.5;
      for (let i = 0; i < 8; i++) {
        const ca = Math.cos(_angs[i]), sa = Math.sin(_angs[i]);
        const r0 = S * (0.8 + 0.6 * v) * _lens[i], r1 = r0 + S * 0.35 * (1 - v);
        px.line(P, x + ca * r0, y + sa * r0, x + ca * r1, y + sa * r1, i % 2 ? acc : c);
      }
      if (v < 0.5) {
        const r = S * 0.9;
        for (let j = 0; j < 16; j++) { const a = rot + TAU * j / 16; dotA(P, x + Math.cos(a) * r, y + Math.sin(a) * r, c, 0.7); }
      }
    }
  };

  // fx.shockwave：扩散像素环（squash < 1 = 地面环，> 1 = 竖椭圆盾），变细、抖动淡出；echo 内圈细环
  FX.shockwave = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 0.4), dt = t - t0;
    if (dt < 0 || dt >= dur) return;
    const u = dt / dur, r = Math.max(1, def(kw.r_max, 60) * ease(u, 'out3'));
    const wd = Math.max(1, def(kw.width, 2) * (1 - 0.6 * u)), fade = u < 0.55 ? 1 : 1 - (u - 0.55) / 0.45;
    const c = col(def(kw.colour, 'white')), sq = def(kw.squash, 1);
    px.ring(P, x, y, r, wd, c, fade, sq);
    if (def(kw.echo, true) && r > 6) px.ring(P, x, y, r * 0.72, 0.6, c, fade * 0.5, sq);
  };

  // =================================================================== 拳头 / 连打
  const FIST_GRID = `
....kkkkk..
..kkvvvvvk.
kkkvvvvvvvk
kyYkvkvkvvk
kyYkvvvvvvk
kyYkVkVkVvk
.kkkVVVVVk.
....kkkkk..`;
  const FIST_WORLD = FIST_GRID.replace(/v/g, 'y').replace(/V/g, 'Y').replace(/yYk/g, 'gGk');
  const fistCache = new Map();
  // 'starplat' = starplat 的 fist 动作第 0 帧（裁到不透明包围盒、锚点在中心）；缺图用 _FIST_GRID
  function fistImg(fist) {
    fist = fist || 'starplat';
    let v = fistCache.get(fist);
    if (v) return v;
    const [cid, lg] = splitName(fist, fist.indexOf('.') > 0 ? null : 'fist');
    const p = sprPix(cid, lg, 0, true);
    if (p) v = cropOpaque(p);
    if (!v) v = gridImg(/world/.test(fist) ? FIST_WORLD : FIST_GRID);
    v.ox = v.w / 2; v.oy = v.h / 2;
    if (p || !atlasOf(cid)) fistCache.set(fist, v);       // 图集在但图还没好：不缓存兜底
    return v;
  }
  FX._fist = fistImg;
  function rushColour(fist) {
    const D = G.D, cid = splitName(fist || 'starplat', 'fist')[0];
    const st = D && D.stands && D.stands[cid];
    if (st && st.ghost) return st.ghost;
    return /world/.test(String(fist)) ? '#fff2a0' : '#d8d0ff';
  }
  const _ritems = [];
  // fx.rush：ORA / MUDA 连打拳影墙。(x, y) = 替身胸口；[t0, t1] 内每秒 rate 个拳头，每个活 life 秒
  // 游戏加强（规划 §3.7 第 5 条）：kw.big（默认 0）比例的“近处”拳头（depth 大、后画）×2；kw.scale 整体倍数
  FX.rush = function (P, x, y, t, t0, t1, kw) {
    kw = kw || {};
    const life = def(kw.life, 0.3);
    if (t1 == null) t1 = Infinity;
    if (t < t0 || t > t1 + life) return;
    const dir = def(kw.direction, 1) < 0 ? -1 : 1, spread = def(kw.spread, 26), rate = def(kw.rate, 30), seed = def(kw.seed, 0);
    const reach = kw.reach != null ? kw.reach : spread * 0.75, fist = def(kw.fist, 'starplat'), sparks = def(kw.sparks, true);
    const big = def(kw.big, 0), sc0 = def(kw.scale, 1);
    const im = fistImg(fist), scol = col(def(kw.colour, rushColour(fist)));
    const iMin = Math.max(0, Math.floor((t - life - t0) * rate) - 1), iMax = Math.floor((Math.min(t, t1) - t0) * rate) + 1;
    let n = 0;
    for (let i = iMin; i <= iMax; i++) {
      const ts = t0 + (i + 0.6 * H(seed, i, 0)) / rate;
      if (ts > t || ts > t1) continue;
      const u = (t - ts) / life;
      if (u >= 1) continue;
      let it = _ritems[n];
      if (!it) it = _ritems[n] = { depth: 0, i: 0, u: 0, ox: 0, oy: 0 };
      it.depth = H(seed, i, 4); it.i = i; it.u = u;
      it.ox = spread * 0.55 * H(seed, i, 1);
      it.oy = spread * ((H(seed, i, 2) + H(seed, i, 3)) / 2 - 0.5) * 1.3;
      n++;
    }
    // 按深度排序（远的先画）：插入排序，n 一般 < 20
    for (let a = 1; a < n; a++) {
      const v = _ritems[a]; let b = a - 1;
      while (b >= 0 && (_ritems[b].depth > v.depth || (_ritems[b].depth === v.depth && _ritems[b].i > v.i))) { _ritems[b + 1] = _ritems[b]; b--; }
      _ritems[b + 1] = v;
    }
    const flip = dir < 0;
    for (let a = 0; a < n; a++) {
      const { depth, i, u, ox, oy } = _ritems[a];
      const sc = sc0 * (big > 0 && depth >= 1 - big ? 2 : 1);
      const fw = im.w * sc, fh = im.h * sc;
      const ext = ease(Math.min(1, u / 0.4), 'out'), back = Math.max(0, (u - 0.75) / 0.25), e = ext * (1 - 0.5 * back);
      const fx_ = x + dir * (ox + e * reach), fy = y + oy;
      if (u < 0.7) {                                        // 拳后速度线
        const L = 6 + 14 * (1 - u) + 6 * H(seed, i, 5), xb = fx_ - dir * fw * 0.4;
        for (let j = 0; j < 2; j++) {
          const yy = rnd(fy + (j === 0 ? -fh * 0.3 : fh * 0.25));
          for (let s = 0; s < tr(L); s++) dotA(P, xb - dir * s, yy, scol, (1 - s / L) * 0.9);
        }
      }
      if (ext > 0.25 && u < 0.75) {                         // 两层残影
        const gv = px.variant(im, 0, 0, im.w, im.h, { flip, scale: sc, sil: scol, ax: im.w / 2, ay: im.h / 2 });
        for (let q = 0; q < 2; q++) {
          const gk = q === 0 ? 0.55 : 0.3, ga = q === 0 ? 0.35 : 0.6;
          const ge = e - (1 - gk) * 0.5, gx = x + dir * (ox + Math.max(0, ge) * reach);
          px.stamp(P, gv, gx, fy, ga, 1);
        }
      }
      const o = { flip, scale: sc, ax: im.w / 2, ay: im.h / 2 };
      if (depth < 0.3) o.tint = { c: 'black', k: 0.3 };
      px.stamp(P, px.variant(im, 0, 0, im.w, im.h, o), fx_, fy, 1, 1);
      if (sparks && u > 0.38 && u < 0.62 && H(seed, i, 6) < 0.55) {
        const sx = fx_ + dir * (fw / 2 + 2), r = 2 + tr(H(seed, i, 7) * 2.5) * (sc > 1 ? 2 : 1);
        star(P, sx, fy, r, WHITE, false);
        px.dot(P, rnd(sx), rnd(fy), col('#ffd83c'));
      }
    }
  };

  // fx.afterimage（软件版，剧情用）：positions 旧 → 新 [[x, y] 或 [x, y, frame]]；真身由调用方最后画
  FX.afterimage = function (P, sprite_name, positions, kw) {
    kw = kw || {};
    const n = positions ? positions.length : 0;
    if (!n) return;
    const colour = kw.colour == null ? null : kw.colour, a0 = def(kw.alpha0, 0.3), a1 = def(kw.alpha1, 0.75);
    const tint = colour != null ? colour : 'white', am = colour != null ? def(kw.amt, 0.45) : 0.3;
    const flip = !!kw.flip, frame = kw.frame | 0;
    for (let k = 0; k < n; k++) {
      const pos = positions[k], f = pos.length > 2 ? pos[2] : frame;
      const a = a0 + (a1 - a0) * (k / Math.max(1, n - 1));
      const p = sprPix(sprite_name, kw.logical, f);
      let v;
      if (p) {
        const o = { flip, tint: { c: tint, k: am } };
        if (colour != null) o.outline = dark(tint, 0.55);
        v = sv(p, o);
      } else {
        const fig = figureImg();
        v = px.variant(fig, 0, 0, fig.w, fig.h, { flip, tint: { c: tint, k: am }, ax: fig.w / 2, ay: fig.h });
      }
      px.stamp(P, v, pos[0], pos[1], a, 1);
    }
  };

  // =================================================================== 粒子
  function colsOf(c) {
    if (Array.isArray(c) && c.length && typeof c[0] !== 'number') return pal(c);
    return pal([c]);
  }
  // fx.burst：通用解析粒子（angle 90 = 上）
  FX.burst = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const life = def(kw.life, 0.6), dt = t - t0;
    if (dt < 0 || dt > life) return;
    const n = def(kw.n, 20), speed = def(kw.speed, 60), cols = colsOf(def(kw.colours, ['white'])), gravity = def(kw.gravity, 120);
    const size = def(kw.size, 1), seed = def(kw.seed, 0), spread = def(kw.spread, 360), angle = def(kw.angle, 90);
    const drag = def(kw.drag, 0), fade = def(kw.fade, true);
    const s = drag > 0 ? (1 - Math.exp(-drag * dt)) / drag : dt;
    for (let i = 0; i < n; i++) {
      const lf = life * (0.55 + 0.45 * H(seed, i, 1));
      if (dt > lf) continue;
      const a = (angle + (H(seed, i, 2) - 0.5) * spread) * RAD, v = speed * (0.35 + 0.65 * H(seed, i, 3));
      const ppx = x + Math.cos(a) * v * s, ppy = y - Math.sin(a) * v * s + 0.5 * gravity * dt * dt;
      const c = cols[tr(H(seed, i, 4) * cols.length) % cols.length];
      const u = dt / lf;
      let sz = size;
      if (size > 1 && u > 0.6) sz = Math.max(1, size - 1);
      const al = (!fade || u < 0.6) ? 1 : 1 - (u - 0.6) / 0.4;
      if (sz <= 1) dotA(P, ppx, ppy, c, al);
      else {
        if (al < 1 && !(bay(tr(ppx), tr(ppy)) < al)) continue;
        px.rect(P, rnd(ppx - sz / 2), rnd(ppy - sz / 2), sz, sz, c);
      }
    }
  };

  // fx._puff：烟团（抖动外圈 → 底色混黑 22% → 主体 → 高光）
  function puff(P, x, y, r, c, al = 1, soft = true) {
    if (r < 0.8) { dotA(P, rnd(x), rnd(y), c, al); return; }
    if (soft) px.disc(P, x, y, r + 1, c, al * 0.45);
    px.disc(P, x, y, r, mix(c, BLACK, 0.22), al);
    px.disc(P, x - r * 0.12, y - r * 0.2, r * 0.82, c, al);
    if (r >= 2.5) px.disc(P, x - r * 0.32, y - r * 0.4, r * 0.4, light(c, 0.3), al);
  }
  FX._puff = puff;

  // fx.dust：落地 / 刹车 / 脚步的地面尘
  FX.dust = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const life = def(kw.life, 0.75), dt = t - t0;
    if (dt < 0 || dt > life) return;
    const n = def(kw.n, 10), seed = def(kw.seed, 0), c = col(def(kw.colour, '#d8c8a8')), speed = def(kw.speed, 55), size = def(kw.size, 1);
    const s = (1 - Math.exp(-4.5 * dt)) / 4.5;
    for (let i = 0; i < n; i++) {
      const lf = life * (0.6 + 0.4 * H(seed, i, 1));
      if (dt > lf) continue;
      const u = dt / lf, side = i % 2 === 0 ? -1 : 1, v = speed * (0.35 + 0.65 * H(seed, i, 2)) * size;
      const ppx = x + side * (v * s + 2 * H(seed, i, 3));
      const ppy = y - 1 - (3 + 9 * H(seed, i, 4)) * size * ease(u, 'out');
      const r = (1.5 + (2.5 + 3.5 * H(seed, i, 5)) * ease(u, 'out')) * size;
      puff(P, ppx, ppy, r, c, u < 0.4 ? 1 : 1 - (u - 0.4) / 0.6);
    }
    FX.burst(P, x, y - 1, t, t0, { n: Math.max(2, n >> 1), speed: 55 * size, life: life * 0.55, colours: [dark(c, 0.6)], gravity: 280, seed: seed + 77, spread: 130, angle: 90 });
  };

  const FIREBALL = ['#ffffff', '#fff6c0', '#ffe050', '#ffa820', '#f06418', '#c8202a', '#80182a', '#5a3040', '#4a4050'];
  // fx.explosion：白闪 → 翻滚火球（白 → 黄 → 橙 → 红 → 烟）+ 上升烟团 + 碎屑火花 + 冲击环，约 2.2 s
  FX.explosion = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const dt = t - t0;
    if (dt < 0 || dt > 2.2) return;
    const S = def(kw.size, 40), seed = def(kw.seed, 0), sm = col(def(kw.smoke_colour, '#5c5666')), smb = col('#908a9a');
    for (let i = 0; i < 12; i++) {
      const ts = 0.22 + 0.3 * H(seed, i, 20), lf = 1.3 + 0.6 * H(seed, i, 21), e = dt - ts;
      if (e < 0 || e > lf) continue;
      const u = e / lf, ang = TAU * H(seed, i, 22), rr = S * 0.3 * Math.sqrt(H(seed, i, 23));
      const ppx = x + Math.cos(ang) * rr + (H(seed, i, 24) - 0.5) * S * 0.5 * u;
      const ppy = y + Math.sin(ang) * rr * 0.5 - S * (0.35 + 0.9 * H(seed, i, 25)) * ease(u, 'out');
      const r = S * (0.13 + 0.1 * H(seed, i, 26)) * (0.7 + 0.9 * ease(u, 'out'));
      puff(P, ppx, ppy, r, mix(sm, smb, 0.35 * H(seed, i, 27)), u < 0.45 ? 1 : 1 - (u - 0.45) / 0.55);
    }
    if (dt < 1) {
      const nb = 13, rise = S * 0.3 * ease(dt, 'in'), fb = pal(FIREBALL), nn = fb.length - 1;
      const ramp = k => fb[tr(clamp(k, 0, nn))];
      for (let i = 0; i < nb; i++) {
        const ang = TAU * (i / nb + 0.1 * H(seed, i, 1));
        const rr = S * 0.34 * (0.25 + 0.75 * H(seed, i, 2)) * (0.45 + 0.7 * ease(clamp(dt / 0.35), 'out'));
        const ppx = x + Math.cos(ang) * rr, ppy = y + Math.sin(ang) * rr * 0.75 - rise * (0.6 + 0.8 * H(seed, i, 5));
        const grow = ease(clamp(dt / 0.12), 'out'), shrink = 1 - clamp((dt - 0.5) / 0.5);
        const r = S * (0.19 + 0.12 * H(seed, i, 3)) * grow * (0.35 + 0.65 * shrink);
        if (r < 0.8) continue;
        const age = dt * 6 + H(seed, i, 4);
        px.disc(P, ppx, ppy, r, ramp(age + 1.5));
        px.disc(P, ppx - r * 0.1, ppy - r * 0.15, r * 0.76, ramp(age + 0.5));
        px.disc(P, ppx - r * 0.25, ppy - r * 0.3, r * 0.4, ramp(age - 0.5));
      }
    }
    if (dt < 0.09) {
      const k = dt / 0.09;
      px.disc(P, x, y, S * (0.42 + 0.4 * k), col('#ffe050'));
      px.disc(P, x, y, S * (0.34 + 0.34 * k), WHITE);
    }
    if (def(kw.ring, true)) FX.shockwave(P, x, y, t, t0, { dur: 0.38, r_max: S * 1.4, colour: '#fff4b0', width: 3 });
    if (def(kw.debris, true)) {
      FX.burst(P, x, y, t, t0 + 0.07, { n: 16, speed: S * 3.2, life: 1.1, colours: ['#2a2030', '#5a4a40'], gravity: 240, size: 2, seed: seed + 5, spread: 200, angle: 90 });
      FX.burst(P, x, y, t, t0, { n: 26, speed: S * 4.2, life: 0.65, colours: ['#ffe050', '#ffffff', '#ffa820'], gravity: 90, size: 1, seed: seed + 9, drag: 2.5 });
    }
  };

  // fx.smoke：上升、变大、抖动淡出的烟团（一次性 / loop 连续）
  FX.smoke = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const life = def(kw.life, 1.6), t1 = kw.t1 == null ? null : kw.t1;
    if (t < t0 || (t1 != null && t > t1 + life)) return;
    const n = def(kw.n, 8), seed = def(kw.seed, 0), c = col(def(kw.colour, '#8a8a98')), rise = def(kw.rise, 30);
    const spread = def(kw.spread, 10), size = def(kw.size, 5), loop = !!kw.loop, wind = def(kw.wind, 0);
    let j0 = 0, j1 = n - 1, interval = 0;
    if (loop) { interval = life / n; const jh = Math.floor((t - t0) / interval); j0 = Math.max(0, jh - n - 1); j1 = jh; }
    for (let j = j0; j <= j1; j++) {
      let ts;
      if (loop) { ts = t0 + j * interval; if (t1 != null && ts > t1) continue; } else ts = t0 + 0.3 * H(seed, j, 1);
      const e = t - ts, lf = life * (0.7 + 0.3 * H(seed, j, 2));
      if (e < 0 || e > lf) continue;
      const u = e / lf;
      const ppx = x + (H(seed, j, 3) - 0.5) * spread * (0.4 + u) + wind * e + Math.sin(e * 3 + j) * 1.5;
      const ppy = y - rise * ease(u, 'out') * (0.7 + 0.6 * H(seed, j, 4));
      const r = size * (0.35 + 0.9 * ease(u, 'out')) * (0.7 + 0.5 * H(seed, j, 5));
      puff(P, ppx, ppy, r, mix(c, WHITE, 0.12 * H(seed, j, 6)), u < 0.35 ? 1 : 1 - (u - 0.35) / 0.65);
    }
  };

  // =================================================================== 火
  // fx.fire：泪滴形火舌的并集，底部中心在 (x, y)，高约 1.35h；12 fps 抽帧
  FX.fire = function (P, x, y, t, kw) {
    kw = kw || {};
    const w = def(kw.w, 16), h = def(kw.h, 24), intensity = def(kw.intensity, 1), seed = def(kw.seed, 0);
    const pl = pal(def(kw.palette, 'fire')), L = pl.length, fps = def(kw.fps, 12);
    const ts = Math.floor(t * fps) / fps, k12 = Math.floor(t * fps), top = y - h * 1.35;
    const x0 = Math.max(0, tr(x - w * 0.7 - 1)), y0 = Math.max(0, tr(top)), x1 = Math.min(P.w, tr(x + w * 0.7 + 2)), y1 = Math.min(P.h, tr(y + 1));
    if (x1 <= x0 || y1 <= y0) return;
    const nt = w < 22 ? 3 : 5, tex = noiseTex(seed % 4), u32 = P.u32, Wd = P.w;
    // 每条火舌的常量
    const tj = fireTongues;
    for (let j = 0; j < nt; j++) {
      const c = (j - (nt - 1) / 2) / Math.max(1, (nt - 1) / 2), centre = 1 - Math.abs(c);
      const T = tj[j];
      T.hj = h * (0.55 + 0.45 * centre) * (0.82 + 0.3 * H(seed, j, k12)) * intensity;
      T.rj = w / 2 * (0.52 + 0.36 * centre);
      T.cxj = x + c * w * 0.27;
      T.sway = (Math.sin(ts * 6.1 + j * 1.7 + seed) * 0.6 + (H(seed, j, k12, 2) - 0.5) * 0.8) * T.rj * 0.9;
      T.cw = 0.8 + 0.2 * centre;
    }
    for (let yy = y0; yy < y1; yy++) {
      const ry = (Math.floor(yy * 3 + ts * 90 + seed * 11) & 63) * 64;
      const vb = (y - (yy + 0.5)) / h, base = clamp(0.18 - vb, 0, 1) * 1.2;
      const row = yy * Wd, br = (yy & 3) << 2;
      for (let j = 0; j < nt; j++) {                        // 行常量
        const T = tj[j], v = (y - (yy + 0.5)) / Math.max(1, T.hj), vc = clamp(v);
        T.v = v; T.cxv = T.cxj + T.sway * vc * vc;
        T.hw = T.rj * Math.pow(clamp(1 - v), 0.75) * Math.sqrt(clamp(v * 5 + 0.35));
        T.f2 = 1 - 0.35 * vc;
        T.ok = v >= -0.02 && v <= 1 && T.hw > 0.3;
      }
      for (let xx = x0; xx < x1; xx++) {
        let heat = -1;
        for (let j = 0; j < nt; j++) {
          const T = tj[j];
          const f = T.ok ? (1 - Math.abs(xx + 0.5 - T.cxv) / Math.max(T.hw, 0.3)) * T.f2 : -1;
          const hv = f * T.cw;
          if (hv > heat) heat = hv;
        }
        heat += (tex[ry + (Math.floor(xx * 3 + seed * 23) & 63)] - 0.5) * 0.35;
        if (heat > 0) heat += base;
        const lvl = Math.floor(heat * (L + 1) + (BAY[br | (xx & 3)] - 0.5) * 0.9);
        if (lvl >= 1) u32[row + xx] = pl[lvl - 1 > L - 1 ? L - 1 : lvl - 1];
      }
    }
    if (def(kw.embers, true)) {
      const ne = Math.max(2, tr(w / 5 * intensity));
      for (let j = 0; j < ne; j++) {
        const per = 0.8 + 0.5 * H(seed, j, 1), ph = fmod1(ts / per + H(seed, j, 2));
        const ex = x + (H(seed, j, 3) - 0.5) * w * 0.8 + Math.sin((ts + j) * 5) * 2, ey = y - h * (0.5 + 0.9 * ph);
        dotA(P, ex, ey, pl[Math.min(L - 1, ph < 0.5 ? 3 : 2)], 1 - ph);
      }
    }
  };
  const fireTongues = [0, 1, 2, 3, 4].map(() => ({ hj: 0, rj: 0, cxj: 0, sway: 0, cw: 0, v: 0, cxv: 0, hw: 0, f2: 0, ok: false }));

  // fx.fire_ankh：红色魔术师「十字火焰风暴」燃烧的安卡十字（高 size，中心 (x, y)）；grow 秒内回弹弹出
  FX.fire_ankh = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const t1 = kw.t1 == null ? null : kw.t1;
    if (t < t0 || (t1 != null && t >= t1)) return;
    const dt = t - t0, size = def(kw.size, 40), seed = def(kw.seed, 0), grow = def(kw.grow, 0.25);
    const F = ankhField(tr(size)), core = F.core, up = F.up, fw = F.w, fh = F.h;
    const ts = Math.floor(t * 12) / 12, tex = noiseTex((seed + 1) % 4);
    const s = grow > 0 ? ease(prog(dt, 0, grow), 'back') : 1;
    const pl = pal(def(kw.palette, 'fire')), L = pl.length;
    const ox = rnd(x - fw * s / 2), oy = rnd(y - fh * s / 2);
    FX.glow(P, x, y, size * 0.7 * Math.max(s, 0.3), '#ff7a20', { alpha: 0.4 });
    if (s < 0.999 && s <= 0.05) return;
    const nw = s < 0.999 ? Math.max(1, tr(fw * s)) : fw, nh = s < 0.999 ? Math.max(1, tr(fh * s)) : fh;
    const u32 = P.u32, Wd = P.w;
    for (let r = 0; r < nh; r++) {
      const Y = oy + r;
      if (Y < 0 || Y >= P.h) continue;
      const yy = s < 0.999 ? Math.min(fh - 1, tr(r / s)) : r;
      const ry = (Math.floor(yy * 2.2 + ts * 110) & 63) * 64, ry2 = (Math.floor(yy * 1.1 + ts * 40 + 13) & 63) * 64;
      const by = ((oy + yy) & 3) << 2;
      for (let q = 0; q < nw; q++) {
        const X = ox + q;
        if (X < 0 || X >= Wd) continue;
        const xx = s < 0.999 ? Math.min(fw - 1, tr(q / s)) : q;
        const rx = Math.floor(xx * 2.6 + seed * 9) & 63;
        const n1 = tex[ry + rx], n2 = tex[ry2 + rx], i = yy * fw + xx;
        const a = core[i] * (0.92 + 0.16 * (n2 - 0.5)), b = up[i] * (0.3 + 1.3 * n1) * 0.9;
        const heat = a > b ? a : b;
        const lvl = Math.floor(heat * (L + 0.5) + (BAY[by | ((ox + xx) & 3)] - 0.5) * 0.8);
        if (lvl >= 1) u32[Y * Wd + X] = pl[lvl - 1 > L - 1 ? L - 1 : lvl - 1];
      }
    }
    FX.burst(P, x, y, t, t0, { n: 24, speed: size * 2.2, life: 0.7, colours: ['#ffd83c', '#ff9820', '#ffffff'], gravity: -30, seed: seed + 3, drag: 2 });
    const cy = col('#ffd83c'), co = col('#ff9820');
    for (let j = 0; j < 6; j++) {
      const per = 0.6 + 0.4 * H(seed, j, 11), ph = fmod1(dt / per + H(seed, j, 12));
      dotA(P, x + (H(seed, j, 13) - 0.5) * size * 0.8, y - size * 0.3 - size * 0.6 * ph, ph < 0.5 ? cy : co, 1 - ph);
    }
  };

  // =================================================================== 闪光、魔法
  // fx.sparkles：一群闪烁四角星（连续）
  FX.sparkles = function (P, x, y, t, kw) {
    kw = kw || {};
    const n = def(kw.n, 6), radius = def(kw.radius, 12), c = col(def(kw.colour, 'yellow')), seed = def(kw.seed, 0);
    const period = def(kw.period, 0.8), size = def(kw.size, 3);
    for (let i = 0; i < n; i++) {
      const ph = H(seed, i, 1), per = period * (0.7 + 0.6 * H(seed, i, 2)), cyc = t / per + ph, cc = Math.floor(cyc), f = cyc - cc;
      const ang = TAU * H(seed, i, cc, 3), rr = radius * Math.sqrt(H(seed, i, cc, 4));
      const ppx = x + Math.cos(ang) * rr, ppy = y + Math.sin(ang) * rr, s = Math.sin(Math.PI * f), st = rnd(s * size);
      if (s < 0.12) continue;
      const xi = rnd(ppx), yi = rnd(ppy);
      if (st <= 0) px.dot(P, xi, yi, c);
      else {
        star(P, ppx, ppy, st + (st >= 2 ? 1 : 0), c, true);
        px.dot(P, xi, yi, WHITE);
        if (st >= 2) { px.dot(P, xi - 1, yi, WHITE); px.dot(P, xi + 1, yi, WHITE); px.dot(P, xi, yi - 1, WHITE); px.dot(P, xi, yi + 1, WHITE); }
      }
    }
  };

  // fx.glint：一次性星光（眼睛、剑尖、胎记）
  FX.glint = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 0.45), dt = t - t0;
    if (dt < 0 || dt >= dur) return;
    const u = dt / dur, s = u < 0.8 ? Math.sin(Math.PI * Math.min(1, u * 1.25)) : (1 - u) / 0.2 * 0.35;
    const r = Math.max(0, rnd(def(kw.size, 6) * s)), c = col(def(kw.colour, 'white')), acc = col(def(kw.accent, '#ffd83c'));
    x = rnd(x); y = rnd(y);
    if (r >= 1) {
      px.line(P, x - r - 1, y, x + r + 1, y, acc); px.line(P, x, y - r - 1, x, y + r + 1, acc);
      px.line(P, x - r, y, x + r, y, c); px.line(P, x, y - r, x, y + r, c);
      const q = Math.max(1, Math.floor(r / 3));
      px.line(P, x - q, y - q, x + q, y + q, c); px.line(P, x - q, y + q, x + q, y - q, c);
      if (r >= 3) px.box(P, x - 1, y - 1, x + 1, y + 1, c);
    } else px.dot(P, x, y, c);
  };

  // fx._bolt_points：中点位移折线（闪电、波纹共用）→ 扁平数组 [x0, y0, x1, y1, …]
  function boltPoints(x0, y0, x1, y1, seed, k, depth = 5, disp = 0.28) {
    let pts = [x0, y0, x1, y1];
    let amp = Math.hypot(x1 - x0, y1 - y0) * disp;
    for (let lev = 0; lev < depth; lev++) {
      const nw = [pts[0], pts[1]], m = pts.length / 2;
      for (let i = 0; i < m - 1; i++) {
        const ax = pts[2 * i], ay = pts[2 * i + 1], bx = pts[2 * i + 2], by = pts[2 * i + 3];
        const mx = (ax + bx) / 2, my = (ay + by) / 2, sl = Math.hypot(bx - ax, by - ay) || 1;
        const nx = -(by - ay) / sl, ny = (bx - ax) / sl, o = (H(seed, k, lev, i) - 0.5) * 2 * amp;
        nw.push(mx + nx * o, my + ny * o, bx, by);
      }
      pts = nw; amp *= 0.5;
    }
    return pts;
  }
  FX._bolt_points = boltPoints;

  // fx.hamon：波纹——金色电流 + 橙色抖动光晕 + 目标点同心波纹 + 星光（连续，fps 重随机）
  FX.hamon = function (P, x0, y0, x1, y1, t, kw) {
    kw = kw || {};
    const seed = def(kw.seed, 0), colour = def(kw.colour, '#ffd83c'), fps = def(kw.fps, 16), strands = def(kw.strands, 2);
    const k = tr(t * fps), gold = col(colour), lt = light(gold, 0.7), orange = col('#ff9a20');
    const L = Math.hypot(x1 - x0, y1 - y0);
    if (L >= 2) {
      const paths = [];
      for (let s = 0; s < strands; s++) {
        const pts = boltPoints(x0, y0, x1, y1, seed + 31 * s, k, 4, 0.14 + 0.06 * s);
        paths.push(pts);
        px.lines(P, pts, orange, 0.5, 3);
      }
      for (let s = 0; s < paths.length; s++) px.lines(P, paths[s], s === 0 ? lt : gold);
      for (let j = 0; j < 4; j++) {
        const q = H(seed, k, j, 1), ppx = x0 + (x1 - x0) * q, ppy = y0 + (y1 - y0) * q, a = H(seed, k, j, 2) * TAU;
        const p2x = ppx + Math.cos(a) * 4, p2y = ppy + Math.sin(a) * 4;
        px.line(P, ppx, ppy, p2x, p2y, gold);
        px.line(P, p2x, p2y, p2x + Math.cos(a + 1.2) * 3, p2y + Math.sin(a + 1.2) * 3, gold);
      }
    }
    if (def(kw.ripples, true)) {
      for (let ri = 0; ri < 3; ri++) {
        const ph = fmod1(t / 0.45 + ri / 3), r = 3 + ph * 16;
        const c = ph < 0.3 ? lt : ph < 0.65 ? gold : orange;
        if (ph > 0.85 && k % 2) continue;
        px.ellipse(P, x1 - r, y1 - r * 0.8, x1 + r, y1 + r * 0.8, null, c, 1);
      }
      FX.sparkles(P, x1, y1, t, { n: 5, radius: 12, colour, seed: seed + 1, period: 0.35, size: 2 });
    }
    FX.glint(P, x1, y1, t - Math.floor(t / 0.3) * 0.3, 0, { size: 3, dur: 0.3 });
  };

  // fx.lightning：锯齿闪电 + 分叉 + 抖动光晕（fps 0 = 静止形状）
  FX.lightning = function (P, x0, y0, x1, y1, t, kw) {
    kw = kw || {};
    const seed = def(kw.seed, 0), fps = def(kw.fps, 12), branches = def(kw.branches, 3), width = def(kw.width, 1);
    const k = fps ? tr(t * fps) : 0, gcol = col(def(kw.glow_colour, '#9cc8ff')), c = col(def(kw.colour, 'white'));
    const pts = boltPoints(x0, y0, x1, y1, seed, k);
    px.lines(P, pts, gcol, 0.55, width + 2);
    const segs = [pts], m = pts.length / 2;
    for (let b = 0; b < branches; b++) {
      const i = tr(m * (0.2 + 0.6 * H(seed, k, b, 1))), bx = pts[2 * i], by = pts[2 * i + 1];
      const L = Math.hypot(x1 - x0, y1 - y0) * (0.2 + 0.25 * H(seed, k, b, 2));
      const base = Math.atan2(y1 - y0, x1 - x0) + (H(seed, k, b, 3) - 0.5) * 1.6;
      const bp = boltPoints(bx, by, bx + Math.cos(base) * L, by + Math.sin(base) * L, seed + 7 + b, k, 4);
      px.lines(P, bp, gcol, 0.55, width + 1);
      segs.push(bp);
    }
    for (let j = 0; j < segs.length; j++) px.lines(P, segs[j], c, 1, j === 0 ? width : 1);
  };

  // =================================================================== 天气 / 氛围
  const pmod = (a, m) => ((a % m) + m) % m;                 // Python 取模（结果非负）

  // fx.rain：斜雨（每 3 根 1 根远层）；ground 给了就加 12 fps 溅点
  FX.rain = function (P, t, kw) {
    kw = kw || {};
    const n = def(kw.n, 120), angle = def(kw.angle, 12), speed = def(kw.speed, 260), seed = def(kw.seed, 0);
    const c = col(def(kw.colour, '#a8b8e8')), length = def(kw.length, 7), ground = kw.ground == null ? null : kw.ground, layers = def(kw.layers, true);
    const far = mix(c, pack(20, 24, 48), 0.5), ta = Math.tan(angle * RAD), Hh = P.h + 40;
    const sn = Math.sin(angle * RAD), cs = Math.cos(angle * RAD);
    for (let i = 0; i < n; i++) {
      const near = i % 3 !== 0 || !layers;
      const spd = speed * (near ? 1 : 0.6) * (0.85 + 0.3 * H(seed, i, 1)), ln = length * (near ? 1 : 0.6);
      const yv = pmod(H(seed, i, 2) * Hh + spd * t, Hh) - 20;
      const x0 = H(seed, i, 3) * (P.w + P.h * Math.abs(ta) + 20) - (ta > 0 ? P.h * ta : 0) - 10, xv = x0 + yv * ta;
      px.line(P, xv, yv, xv - ln * sn, yv - ln * cs, near ? c : far);
    }
    if (ground != null) {
      const k = tr(t * 12);
      for (let j = 0; j < Math.floor(n / 6); j++) {
        const sx = H(seed, k, j, 5) * P.w, gy = ground + tr(H(seed, k, j, 6) * 6);
        px.dot(P, tr(sx - 1), tr(gy - 1), c); px.dot(P, tr(sx + 1), tr(gy - 1), c); px.dot(P, tr(sx), tr(gy), far);
      }
    }
  };

  // fx.sand_wind：风沙（3 条抖动沙幕 + n 根沙粒横线）；region = [y0, y1]
  FX.sand_wind = function (P, t, kw) {
    kw = kw || {};
    const n = def(kw.n, 80), seed = def(kw.seed, 0), cols = pal(def(kw.colours, ['#f0c878', '#d8a050', '#fbe0a0'])), speed = def(kw.speed, 180);
    const dir = def(kw.direction, 1), region = kw.region || [0, P.h], y0r = region[0], y1r = region[1];
    const xr = kw.xrange || [0, P.w];                       // 扩展：只在横向一段里画（伊奇连打的“前方带”）
    if (def(kw.sheets, true)) {
      const u = P.u32;
      for (let s = 0; s < 3; s++) {
        const cy = y0r + (y1r - y0r) * (0.3 + 0.25 * s) + Math.sin(t * 0.7 + s) * 6, hh = 6 + 3 * s;
        const ya = Math.max(0, tr(cy - hh)), yb = Math.min(P.h, tr(cy + hh));
        const c = cols[s % cols.length], cr = cR(c), cg = cG(c), cb = cB(c);
        for (let yy = ya; yy < yb; yy++) {
          const v = Math.pow(clamp(1 - Math.abs(yy - cy) / hh), 0.7);
          for (let xx = Math.max(0, xr[0] | 0); xx < Math.min(P.w, xr[1] | 0); xx++) {
            const ph = (xx - dir * t * speed * (0.5 + 0.2 * s)) * 0.03 + s * 3;
            const wav = 0.5 + 0.5 * Math.sin(ph + 0.6 * Math.sin(ph * 0.37 + yy * 0.2));
            px.qblendI(u, yy * P.w + xx, xx, yy, cr, cg, cb, v * wav * 0.6, 3, false);
          }
        }
      }
    }
    const span = P.w + 60;
    for (let i = 0; i < n; i++) {
      const spd = speed * (0.6 + 0.8 * H(seed, i, 1));
      let xv = pmod(H(seed, i, 2) * span + dir * spd * t, span) - 30;
      if (dir < 0) xv = P.w - xv;
      if (xv < xr[0] - 8 || xv > xr[1] + 8) continue;
      const yv = y0r + H(seed, i, 3) * (y1r - y0r) + Math.sin(t * 4 + i) * 3, ln = 2 + tr(H(seed, i, 4) * 7);
      px.line(P, xv, yv, xv - dir * ln, yv, cols[i % cols.length]);
    }
  };

  const PETAL_SHAPES = [['.10.', '1002', '.02.'], ['..1', '.10', '102', '22.'], ['1.', '02', '.2'], ['1..', '010', '.022']];
  // fx.petals：樱花瓣（4 种翻转姿势，7 fps），斜向飘落、左右摆，循环
  FX.petals = function (P, t, kw) {
    kw = kw || {};
    const n = def(kw.n, 24), seed = def(kw.seed, 0), wind = kw.wind || [26, 20], cols = pal(def(kw.colours, ['#ffa8c8', '#ffe4ee', '#d86c98']));
    const sx = P.w + 20, sy = P.h + 20;
    for (let i = 0; i < n; i++) {
      const spx = wind[0] * (0.6 + 0.8 * H(seed, i, 1)), spy = wind[1] * (0.6 + 0.8 * H(seed, i, 2));
      const ppx = pmod(H(seed, i, 3) * sx + spx * t + Math.sin(t * 2.3 + i) * 6, sx) - 10;
      const ppy = pmod(H(seed, i, 4) * sy + spy * t, sy) - 10;
      const st = pmod(tr(t * 7 + H(seed, i, 5) * 4), 4), xi = rnd(ppx), yi = rnd(ppy), sh = PETAL_SHAPES[st];
      for (let yy = 0; yy < sh.length; yy++) for (let xx = 0; xx < sh[yy].length; xx++) {
        const ch = sh[yy][xx];
        if (ch !== '.') px.dot(P, xi + xx, yi + yy, cols[+ch]);
      }
    }
  };

  // fx.bubbles：盒内上升的气泡
  FX.bubbles = function (P, t, x0, y0, x1, y1, kw) {
    kw = kw || {};
    const n = def(kw.n, 20), seed = def(kw.seed, 0), c = col(def(kw.colour, '#b8ecff')), speed = def(kw.speed, 30), hgt = Math.max(1, y1 - y0);
    for (let i = 0; i < n; i++) {
      const spd = speed * (0.5 + H(seed, i, 1)), yv = y1 - fmod1(H(seed, i, 2) + t * spd / hgt) * hgt;
      const xv = x0 + H(seed, i, 3) * (x1 - x0) + Math.sin(t * 3 + i * 1.7) * 2, r = tr(H(seed, i, 4) * H(seed, i, 4) * 3.2);
      const xi = rnd(xv), yi = rnd(yv);
      if (r === 0) px.dot(P, xi, yi, c);
      else if (r === 1) { px.dot(P, xi - 1, yi, c); px.dot(P, xi + 1, yi, c); px.dot(P, xi, yi - 1, c); px.dot(P, xi, yi + 1, c); }
      else { px.ellipse(P, xi - r, yi - r, xi + r, yi + r, null, c, 1); px.dot(P, xi - r + 1, yi - r + 1, WHITE); }
    }
  };

  // fx.fog：漂移雾带（两层可平铺纹理不同速滚动，量化抖动半透明）
  FX.fog = function (P, t, kw) {
    kw = kw || {};
    const density = def(kw.density, 0.6), c = col(def(kw.colour, '#c8c8d8')), seed = def(kw.seed, 0), speed = def(kw.speed, 8);
    const region = kw.region || [0, P.h], levels = def(kw.levels, 3), maxA = def(kw.max_alpha, 0.85);
    const y0 = Math.max(0, tr(region[0])), y1 = Math.min(P.h, tr(region[1]));
    if (y1 <= y0 || density <= 0) return;
    const tex = fogTex(seed % 4, P.h), tex2 = fogTex((seed + 1) % 4, P.h), o1 = tr(t * speed), o2 = tr(t * speed * 1.9) + 200;
    const hh = y1 - y0, cr = cR(c), cg = cG(c), cb = cB(c), u = P.u32;
    for (let yy = y0; yy < y1; yy++) {
      const r = yy - y0, edge = clamp(Math.min(r + 1, hh - r) / Math.max(1, hh * 0.18));
      for (let xx = 0; xx < P.w; xx++) {
        const f = 0.6 * tex[yy * 512 + ((xx + o1) & 511)] + 0.4 * tex2[yy * 512 + ((xx + o2) & 511)];
        const A = clamp((f - (1 - density)) * 2.2) * edge * maxA;
        if (A > 0) px.qblendI(u, yy * P.w + xx, xx, yy, cr, cg, cb, A, levels, false);
      }
    }
  };

  // fx.stars：星空（暗点、亮点、少数眨眼十字星）
  FX.stars = function (P, t, kw) {
    kw = kw || {};
    const n = def(kw.n, 80), seed = def(kw.seed, 0), twinkle = def(kw.twinkle, true), rg = kw.region || [0, 0, P.w, P.h];
    const dim = col('#7078a8'), mid = col('#c0c8f0'), warm = col('#fff0c0'), dimd = mix(dim, BLACK, 0.5), k = tr(t * 8);
    for (let i = 0; i < n; i++) {
      const ppx = rnd(rg[0] + H(seed, i, 1) * (rg[2] - rg[0])), ppy = rnd(rg[1] + H(seed, i, 2) * (rg[3] - rg[1])), kind = H(seed, i, 3);
      let on = true;
      if (twinkle && H(seed, i, 4) < 0.35) on = H(seed, i, Math.floor(k / 2) + tr(H(seed, i, 5) * 7), 6) > 0.3;
      if (kind < 0.62) px.dot(P, ppx, ppy, on ? dim : dimd);
      else if (kind < 0.9) px.dot(P, ppx, ppy, on ? (i % 3 ? mid : warm) : dim);
      else {
        const ph = fmod1(t * 0.9 + H(seed, i, 7)), r = 1 + (twinkle && ph < 0.5 ? 1 : 0);
        px.dot(P, ppx, ppy, WHITE);
        px.dot(P, ppx - r, ppy, mid); px.dot(P, ppx + r, ppy, mid); px.dot(P, ppx, ppy - r, mid); px.dot(P, ppx, ppy + r, mid);
        if (r > 1) { px.dot(P, ppx - 1, ppy, WHITE); px.dot(P, ppx + 1, ppy, WHITE); px.dot(P, ppx, ppy - 1, WHITE); px.dot(P, ppx, ppy + 1, WHITE); }
      }
    }
  };

  // fx.shooting_star：流星 (x0, y0) → (x1, y1)，拖尾结束后留 0.2 s
  FX.shooting_star = function (P, t, t0, x0, y0, x1, y1, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 0.6), dt = t - t0;
    if (dt < 0 || dt > dur + 0.2) return;
    const u = Math.min(1, dt / dur), hx = lerp(x0, x1, u), hy = lerp(y0, y1, u), L = Math.hypot(x1 - x0, y1 - y0) || 1;
    const dx = (x1 - x0) / L, dy = (y1 - y0) / L, fade = dt <= dur ? 1 : 1 - (dt - dur) / 0.2;
    const c = col(def(kw.colour, 'white')), tc = col(def(kw.tail_colour, '#ffd870')), tail = def(kw.tail, 34), tc2 = mix(tc, '#ff7040', 0.5);
    const tl = Math.min(tail, L * u);
    for (let s = 0; s < tr(tl); s++) {
      const a = (1 - s / tail) * fade, cc = s < 4 ? c : (s < tail * 0.5 ? tc : tc2);
      dotA(P, hx - dx * s, hy - dy * s, cc, a);
      if (s < tail * 0.4) dotA(P, hx - dx * s - dy, hy - dy * s + dx, tc, a * 0.5);
    }
    if (dt <= dur) {
      star(P, hx, hy, 2 + tr(t * 24) % 2, c, true);
      px.dot(P, rnd(hx), rnd(hy), WHITE);
      for (let j = 0; j < 3; j++) {
        const s = 8 + j * 7;
        dotA(P, hx - dx * s + (H(tr(t0 * 10), j, tr(t * 12)) - 0.5) * 4, hy - dy * s + 2 + j, tc, 0.7);
      }
    }
  };

  // =================================================================== 水
  // fx.water_splash：落水（皇冠水花、水柱、压扁的水面涟漪），约 1.1 s
  FX.water_splash = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const dt = t - t0;
    if (dt < 0 || dt > 1.1) return;
    const size = def(kw.size, 1), seed = def(kw.seed, 0), cols = pal(def(kw.colours, ['#ffffff', '#b8ecff', '#5aa0e6']));
    FX.shockwave(P, x, y, t, t0 + 0.05, { dur: 0.8, r_max: 30 * size, colour: cols[1], width: 2, squash: 0.25, echo: false });
    FX.shockwave(P, x, y, t, t0 + 0.3, { dur: 0.8, r_max: 20 * size, colour: cols[0], width: 1, squash: 0.25, echo: false });
    if (dt < 0.7) {
      const u = dt / 0.7, hgt = 34 * size * Math.sin(Math.PI * Math.min(1, u * 1.2)), wdt = Math.max(1, 5 * size * (1 - 0.5 * u));
      for (let j = 0; j < tr(hgt); j++) {
        const yy = rnd(y - j), ww = wdt * (1 - 0.5 * j / Math.max(1, hgt));
        for (let xx = rnd(x - ww); xx <= rnd(x + ww); xx++) px.dot(P, xx, yy, j < hgt * 0.3 ? cols[2] : cols[1]);
        px.dot(P, rnd(x - ww * 0.3), yy, cols[0]);
      }
      px.disc(P, x, y - hgt, Math.max(1, 2 * size), cols[0]);
    }
    FX.burst(P, x, y - 2, t, t0, { n: tr(30 * size), speed: 130 * size, life: 1.0, colours: cols, gravity: 280, size: size >= 0.8 ? 2 : 1, seed, spread: 70, angle: 90 });
    FX.burst(P, x, y - 1, t, t0, { n: tr(16 * size), speed: 80 * size, life: 0.7, colours: [cols[0], cols[1]], gravity: 220, size: 1, seed: seed + 1, spread: 150, angle: 90 });
  };

  // fx.water_gush：破洞喷水（摆动的抛物线水流 + 水滴 + 落地溅点）；0.3 s 内起势，t1 停（null = 一直喷）
  FX.water_gush = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const t1 = kw.t1 == null ? null : kw.t1;
    if (t < t0 || (t1 != null && t > t1 + 0.6)) return;
    const dt = t - t0, dir = def(kw.direction, 1), strength = def(kw.strength, 1), ground = kw.ground == null ? null : kw.ground, seed = def(kw.seed, 0);
    const cols = pal(def(kw.colours, ['#ffffff', '#9ad8ff', '#3c8ad8', '#1e5aa8']));
    let ramp = ease(prog(dt, 0, 0.3), 'out');
    if (t1 != null && t > t1) ramp *= 1 - (t - t1) / 0.6;
    const v0 = 70 * strength * ramp + 10, g = 240, ts = Math.floor(t * 12) / 12;
    let land = null;
    for (let q = 0; q < 60; q++) {
      const s = q / 59, ppx = x + dir * v0 * s, ppy = y + 0.5 * g * s * s - 4 * s + Math.sin(ts * 20 - s * 18) * 1.2 * s;
      if (ground != null && ppy >= ground) { land = ppx; break; }
      if (ppx < -4 || ppx > P.w + 4 || ppy > P.h + 4) break;
      px.disc(P, ppx, ppy, 1.5 + 2 * s * strength, cols[2]);
    }
    const hk = tr(ts * 24) % 5;
    for (let q = 0; q < 60; q++) {
      const s = q / 59, ppx = x + dir * v0 * s, ppy = y + 0.5 * g * s * s - 4 * s + Math.sin(ts * 20 - s * 18) * 1.2 * s;
      if ((ground != null && ppy >= ground) || ppx < -4 || ppx > P.w + 4 || ppy > P.h + 4) break;
      px.dot(P, rnd(ppx), rnd(ppy - 1), cols[1]);
      if (tr(s * 60) % 5 === hk) px.dot(P, rnd(ppx), rnd(ppy - 1), cols[0]);
    }
    px.disc(P, x, y, 2, cols[0]);
    const rate = 40, ih = tr(dt * rate);
    for (let i = Math.max(0, ih - 40); i <= ih; i++) {
      const tsi = t0 + i / rate, e = t - tsi;
      if (e < 0 || e > 1 || (t1 != null && tsi > t1)) continue;
      const vx = dir * v0 * (0.7 + 0.6 * H(seed, i, 1)), vy = -20 - 40 * H(seed, i, 2);
      const ppx = x + vx * e, ppy = y + vy * e + 0.5 * g * e * e;
      if (ground != null && ppy > ground) continue;
      dotA(P, ppx, ppy, cols[tr(H(seed, i, 3) * 3)], 1);
    }
    if (ground != null && land != null) {
      const k = tr(t * 12);
      for (let j = 0; j < 8; j++) {
        const ang = (40 + 100 * H(seed, k, j, 1)) * RAD, rr = 2 + 6 * H(seed, k, j, 2);
        px.dot(P, rnd(land + Math.cos(ang) * rr), rnd(ground - Math.sin(ang) * rr), cols[j % 2]);
      }
    }
  };

  // =================================================================== 绿色法皇
  const GEM = {
    emerald: { k: '#0a4a2a', m: '#20d080', l: '#b8ffd8', d: '#0e9050' },
    ice: { k: '#1a3a6a', m: '#a0dcff', l: '#ffffff', d: '#5a9ae0' },
    ruby: { k: '#4a0a14', m: '#e0303c', l: '#ffc0c8', d: '#901828' },
  };
  const GEM_GRIDS = [`
.k.
kmk
.k.`, `
..k..
.klk.
kmmdk
.kdk.
..k..`, `
...k...
..klk..
.kllmk.
kmmmmdk
.kmddk.
..kdk..
...k...`];
  const gemCache = new Map();
  function gemImg(kind, sz) {
    const key = kind + sz;
    let v = gemCache.get(key);
    if (!v) { const p = GEM[kind] || GEM.emerald; v = gridImg(GEM_GRIDS[sz] || GEM_GRIDS[1], p); gemCache.set(key, v); }
    return v;
  }
  FX._gem_img = gemImg;
  // 单颗宝石（飞行道具用）：kw = { kind: 'emerald' | 'ice' | 'ruby', size: 0 | 1 | 2, vx, vy（给了速度就画一小段拖尾） }
  FX.gem = function (P, x, y, kw) {
    kw = kw || {};
    const kind = def(kw.kind, 'emerald'), p = GEM[kind] || GEM.emerald, im = gemImg(kind, def(kw.size, 1));
    const vx = kw.vx || 0, vy = kw.vy || 0, sp = Math.hypot(vx, vy);
    if (sp > 1) {
      const dx = vx / sp, dy = vy / sp, tr1 = col(p.m), tr2 = col(p.d), lt = light(tr1, 0.5);
      for (let s = 1; s < 10; s++) {
        const tx = x - dx * s * 1.6, ty = y - dy * s * 1.6;
        dotA(P, tx, ty, s < 3 ? lt : s < 6 ? tr1 : tr2, 1 - s / 10);
        if (s < 6) dotA(P, tx - dy, ty + dx, tr2, 0.8 - s / 7);
      }
    }
    px.stamp(P, px.variant(im, 0, 0, im.w, im.h, { ax: im.w / 2, ay: im.h / 2 }), x, y, def(kw.alpha, 1), 1);
  };

  // fx.emerald_splash：[t0, t1] 内从 (x0, y0) 依次射出 n 颗宝石，带弧度飞向 (x1, y1) ± spread，到达后小火花
  FX.emerald_splash = function (P, x0, y0, x1, y1, t, t0, t1, kw) {
    kw = kw || {};
    if (t < t0) return;
    const n = def(kw.n, 24), seed = def(kw.seed, 0), spread = def(kw.spread, 20), speed = def(kw.speed, 320), kind = def(kw.kind, 'emerald'), arc = def(kw.arc, 10);
    const p = GEM[kind] || GEM.emerald, trail = col(p.m), trail2 = col(p.d), lt = light(trail, 0.5);
    const L = Math.hypot(x1 - x0, y1 - y0), T = Math.max(0.12, L / speed);
    for (let i = 0; i < n; i++) {
      const ts = t0 + (t1 - t0) * (i + 0.8 * H(seed, i, 0)) / Math.max(1, n), e = t - ts;
      if (e < 0 || e > T + 0.12) continue;
      const sx = x0 + (H(seed, i, 1) - 0.5) * 6, sy = y0 + (H(seed, i, 2) - 0.5) * 6;
      const ex = x1 + (H(seed, i, 3) - 0.5) * 2 * spread, ey = y1 + (H(seed, i, 4) - 0.5) * 2 * spread;
      const u = Math.min(1, e / T), bend = (H(seed, i, 5) - 0.5) * 2 * arc, ll = Math.hypot(ex - sx, ey - sy) || 1;
      const nx = -(ey - sy) / ll, ny = (ex - sx) / ll;
      if (u < 1) {
        for (let s = 1; s < 13; s++) {
          const q = u - s * 0.015;
          if (q < 0) break;
          const b = Math.sin(Math.PI * q) * bend, tx = sx + (ex - sx) * q + nx * b, ty = sy + (ey - sy) * q + ny * b;
          dotA(P, tx, ty, s < 3 ? lt : (s < 7 ? trail : trail2), 1 - s / 13);
          if (s < 7) dotA(P, tx + ny, ty - nx, trail2, 0.8 - s / 9);
        }
        const b = Math.sin(Math.PI * u) * bend, im = gemImg(kind, H(seed, i, 6) < 0.45 ? 2 : 1);
        px.stamp(P, px.variant(im, 0, 0, im.w, im.h, { ax: im.w / 2, ay: im.h / 2 }), sx + (ex - sx) * u + nx * b, sy + (ey - sy) * u + ny * b, 1, 1);
      } else {
        FX.hit_spark(P, ex, ey, t, ts + T, { size: 5, colour: 'white', accent: p.m, seed: i, dur: 0.12 });
      }
    }
  };

  // fx._sag_curve → 采样点（整数）写进 out（Int32Array，[x0, y0, x1, y1, …]），返回点数
  let _curve = new Int32Array(2048);
  function sagCurve(ax, ay, bx, by, sag, wig, t, seed) {
    const L = Math.hypot(bx - ax, by - ay), n = Math.max(2, tr(L) + 1);
    if (_curve.length < n * 2) _curve = new Int32Array(n * 2 + 256);
    const Ln = L || 1, nx = -(by - ay) / Ln, ny = (bx - ax) / Ln;
    for (let i = 0; i < n; i++) {
      const s = i / (n - 1);
      let x = ax + (bx - ax) * s, y = ay + (by - ay) * s + sag * 4 * s * (1 - s);
      if (wig) { const ww = Math.sin(s * Math.PI * 3 + t * 4 + seed) * wig * Math.sin(Math.PI * s); x += nx * ww; y += ny * ww; }
      _curve[2 * i] = rnd(x); _curve[2 * i + 1] = rnd(y);
    }
    return n;
  }
  // fx.tendrils：法皇的发光丝线网。pts = 折线 [[x, y], …] 或线段对 [[[x0, y0], [x1, y1]], …]；grow 0..1 只画前一部分
  FX.tendrils = function (P, pts, t, kw) {
    kw = kw || {};
    const grow = def(kw.grow, 1);
    if (!pts || pts.length < 1 || grow <= 0) return;
    const pairs = Array.isArray(pts[0][0]);
    const nseg = pairs ? pts.length : pts.length - 1;
    const core = col(def(kw.colour, 'emerald')), dk = dark(core, 0.45), lt = light(core, 0.6);
    const glow = def(kw.glow, true), wiggle = def(kw.wiggle, 1), seed = def(kw.seed, 0), pulses = def(kw.pulses, true);
    for (let j = 0; j < nseg; j++) {
      const a = pairs ? pts[j][0] : pts[j], b = pairs ? pts[j][1] : pts[j + 1];
      const L = Math.hypot(b[0] - a[0], b[1] - a[1]), sg = kw.sag == null ? L * 0.06 : kw.sag;
      const n = sagCurve(a[0], a[1], b[0], b[1], sg, wiggle, t, seed + j), m = Math.max(2, tr(n * clamp(grow)));
      const C = _curve;
      if (glow) {
        for (let i = 0; i < m; i++) {
          const x = C[2 * i], y = C[2 * i + 1];
          px.plot(P, x + 1, y, dk, 0.6); px.plot(P, x - 1, y, dk, 0.6); px.plot(P, x, y + 1, dk, 0.6); px.plot(P, x, y - 1, dk, 0.6);
        }
        for (let i = 0; i < m; i++) {
          const x = C[2 * i], y = C[2 * i + 1];
          px.plot(P, x + 2, y, dk, 0.22); px.plot(P, x - 2, y, dk, 0.22); px.plot(P, x, y + 2, dk, 0.22); px.plot(P, x, y - 2, dk, 0.22);
        }
      }
      for (let i = 0; i < m; i++) px.dot(P, C[2 * i], C[2 * i + 1], core);
      if (pulses && m > 6) {
        const nq = Math.max(1, tr(L / 40));
        for (let q = 0; q < nq; q++) {
          const u = fmod1(t * 1.2 + q / nq + H(seed, j, q)), k = tr(u * (m - 1));
          for (let s = Math.max(0, k - 2); s < Math.min(m, k + 3); s++) px.dot(P, C[2 * s], C[2 * s + 1], lt);
          px.dot(P, C[2 * k], C[2 * k + 1], WHITE);
        }
      }
    }
  };

  // =================================================================== 藤蔓
  const VINE_COLS = {
    purple: ['#2a0e44', '#8a44d8', '#d0a0ff', '#5a2890'],
    green: ['#0c2c16', '#34b058', '#a0f080', '#1e7a3c'],
    holly: ['#1a1030', '#3aa860', '#a8f090', '#8a44d8'],
    dark: ['#0a0a10', '#3a3a4a', '#7a7a90', '#2a2a3a'],
    fire: ['#5a0c1c', '#e8501a', '#ffd840', '#ff9820'],     // 红色束缚的火绳（规划 §5.1.2 MR_RED_BIND）
    hamon: ['#5a2a00', '#ffb020', '#fff6b0', '#ffe060'],    // s00 HAMON_VINE（波纹贯藤）
  };
  FX.VINE_COLS = VINE_COLS;
  let _vs = [new Int32Array(1024), new Int32Array(1024), new Int32Array(1024)];
  // fx.vines：带刺双股藤蔓沿弯曲路径在 [t0, t1] 内长出（之后轻轻摆）。colour：名字或 [描边, 主色, 高光, 刺]
  FX.vines = function (P, x0, y0, x1, y1, t, t0, t1, kw) {
    kw = kw || {};
    if (t < t0) return;
    const cs = pal(typeof kw.colour === 'string' || kw.colour == null ? (VINE_COLS[def(kw.colour, 'purple')] || VINE_COLS.purple) : kw.colour);
    const ko = cs[0], cm = cs[1], cl = cs[2], ct = cs[3];
    const thorns = def(kw.thorns, true), seed = def(kw.seed, 0), wiggle = def(kw.wiggle, 2), strands = Math.min(3, def(kw.strands, 2)), sway = def(kw.sway, true);
    const g = t1 > t0 ? ease(prog(t, t0, t1), 'out') : 1, L = Math.hypot(x1 - x0, y1 - y0);
    if (L < 1) return;
    const n = tr(L * 1.5) + 2, m = Math.max(2, tr(n * g));
    const dx = (x1 - x0) / L, dy = (y1 - y0) / L, nx = -dy, ny = dx;
    const bd = kw.bend == null ? (H(seed, 1) - 0.5) * 0.5 * L : kw.bend;
    const sw = sway && g >= 1 ? Math.sin(t * 2.2 + seed) * 1.2 : 0, freq = L / 14;
    if (_vs[0].length < m * 2) _vs = [0, 1, 2].map(() => new Int32Array(m * 2 + 256));
    for (let k = 0; k < strands; k++) {
      const S = _vs[k], ph = k * Math.PI + seed;
      for (let i = 0; i < m; i++) {
        const s = i / (n - 1), bx = x0 + (x1 - x0) * s + nx * (bd * 4 * s * (1 - s) + sw * s * s);
        const by = y0 + (y1 - y0) * s + ny * (bd * 4 * s * (1 - s) + sw * s * s), off = Math.sin(s * TAU * freq / 2 + ph) * wiggle;
        S[2 * i] = rnd(bx + nx * off); S[2 * i + 1] = rnd(by + ny * off);
      }
    }
    for (let k = 0; k < strands; k++) {                     // 描边（6 邻域）
      const S = _vs[k];
      for (let i = 0; i < m; i++) {
        const x = S[2 * i], y = S[2 * i + 1];
        px.dot(P, x + 1, y, ko); px.dot(P, x - 1, y, ko); px.dot(P, x, y + 1, ko); px.dot(P, x, y - 1, ko); px.dot(P, x + 1, y + 1, ko); px.dot(P, x - 1, y - 1, ko);
      }
    }
    if (thorns) {
      for (let k = 0; k < strands; k++) {
        const S = _vs[k];
        for (let j = 3 + k * 3; j < m - 2; j += 7) {
          const side = (Math.floor(j / 7) + k) % 2 === 0 ? 1 : -1;
          const tx = S[2 * j] + rnd(nx * side * 2), ty = S[2 * j + 1] + rnd(ny * side * 2);
          const tx2 = S[2 * j] + rnd(nx * side * 3 + dx), ty2 = S[2 * j + 1] + rnd(ny * side * 3 + dy);
          px.dot(P, tx, ty, ct); px.dot(P, tx2, ty2, ct);
          px.dot(P, tx2 + rnd(nx * side), ty2 + rnd(ny * side), ko);
        }
      }
    }
    for (let k = 0; k < strands; k++) {                     // 主色 + 高光
      const S = _vs[k], ox = k % 2 === 0 ? 1 : 0, oy = -1 + (k % 2 ? 1 : 0);
      for (let i = 0; i < m; i++) px.dot(P, S[2 * i], S[2 * i + 1], cm);
      for (let i = 0; i < m; i++) if (i % 4 < 2) px.dot(P, S[2 * i] + ox, S[2 * i + 1] + oy, cl);
    }
    if (g < 1) px.disc(P, _vs[0][2 * (m - 1)], _vs[0][2 * (m - 1) + 1], 1.5, cl);
  };

  // 扩展（游戏要，原片没有）：缠住一个人——几道藤 / 火绳 / 丝线从四周收紧、绕身交叉。(x, y) = 脚点；h = 身高
  // kw = { kind: 'vine' | 'fire' | 'tendril', colour, h: 30, w: 12, n: 3, seed, grow: 0.15 }；被缠住期间常驻
  FX.wrap = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    if (t < t0) return;
    const kind = def(kw.kind, 'vine'), hh = def(kw.h, 30), w = def(kw.w, 12), n = def(kw.n, 3), seed = def(kw.seed, 0), grow = def(kw.grow, 0.15);
    const g = ease(prog(t - t0, 0, grow), 'out');
    for (let i = 0; i < n; i++) {
      const yy = y - hh * (0.25 + 0.55 * (i + 0.5) / n), side = i % 2 ? 1 : -1;
      const r0 = w * (1.8 - 0.8 * g);                      // 从外面收紧到贴身
      const ax = x - side * r0, ay = yy - 4 + 8 * H(seed, i, 1) * (1 - g), bx = x + side * w * 0.6, by = yy + 3;
      if (kind === 'tendril') FX.tendrils(P, [[ax, ay], [bx, by]], t, { colour: def(kw.colour, '#50e890'), wiggle: 0.6 + 1.4 * (1 - g), seed: seed + i });
      else {
        const colour = kw.colour || (kind === 'fire' ? 'fire' : 'purple');
        FX.vines(P, ax, ay, bx, by, t, t0, t0 + grow, { colour, thorns: kind !== 'fire', seed: seed + i * 7, wiggle: 1.2, strands: 2, bend: side * 3 });
      }
    }
    if (kind === 'fire') {                                  // 火绳上的火苗和余烬
      const ts = Math.floor(t * 12) / 12, cy = col('#ffd83c'), co = col('#ff9820');
      for (let j = 0; j < 5; j++) {
        const ph = fmod1(ts * 1.4 + H(seed, j, 3));
        dotA(P, x + (H(seed, j, 4) - 0.5) * w * 1.6, y - hh * (0.2 + 0.7 * H(seed, j, 5)) - ph * 8, ph < 0.5 ? cy : co, 1 - ph);
      }
    }
  };
  FX.firerope = (P, x, y, t, t0, kw) => FX.wrap(P, x, y, t, t0, Object.assign({ kind: 'fire', n: 4 }, kw || {}));

  // =================================================================== 奶油、飞刀
  // fx.void_sphere：虚空球（黑球 + 爬动的点状边 + 被吸进去的粒子）
  FX.void_sphere = function (P, x, y, r, t, kw) {
    kw = kw || {};
    px.disc(P, x, y, r + 1, col('#2a1a3a'));
    px.disc(P, x, y, r, BLACK);
    const ts = Math.floor(t * 12) / 12, nd = kw.dots || Math.max(8, tr(TAU * r / 3.2)), c1 = col(def(kw.rim, '#e8e0f0')), c2 = col(def(kw.rim2, '#7a6a9a'));
    const k12 = tr(ts * 12);
    for (let i = 0; i < nd; i++) {
      const ang = TAU * i / nd + ts * 1.6, rr = r + 1.5 + ((i + k12) % 3 === 0 ? 0.8 : 0);
      const ppx = x + Math.cos(ang) * rr, ppy = y + Math.sin(ang) * rr;
      if ((i + k12) % 4 === 0) px.disc(P, ppx, ppy, 1, c1); else px.dot(P, rnd(ppx), rnd(ppy), i % 2 ? c2 : c1);
    }
    const nh = Math.floor(nd / 2), k24 = tr(ts * 24), ci = col('#241a34');
    for (let i = 0; i < nh; i++) {
      const ang = -TAU * i / nh - ts * 1.1;
      if ((i + k24) % 3 === 0) px.dot(P, rnd(x + Math.cos(ang) * r * 0.8), rnd(y + Math.sin(ang) * r * 0.8), ci);
    }
    for (let j = 0; j < 6; j++) {
      const ph = fmod1(t * 1.5 + H(j, 7)), ang = TAU * H(j, 8), rr = r + 3 + (1 - ph) * r * 0.9;
      dotA(P, rnd(x + Math.cos(ang) * rr), rnd(y + Math.sin(ang) * rr), c2, 1 - ph * 0.5);
    }
  };

  // fx._knife_proc：程序飞刀（指向 ang，0 = 右、90 = 上）
  const knifeCache = new Map();
  function knifeProc(angq) {
    let v = knifeCache.get('p' + angq);
    if (v) return v;
    const size = 17, B = px.buffer(size, size), c = size >> 1, a = angq * RAD, ux = Math.cos(a), uy = -Math.sin(a);
    const Pt = s => [c + ux * s, c + uy * s], k = pack(26, 16, 32);
    let p0 = Pt(-6), p1 = Pt(7); px.line(B, p0[0], p0[1], p1[0], p1[1], k, 1, 3);
    p0 = Pt(-6); p1 = Pt(-2); px.line(B, p0[0], p0[1], p1[0], p1[1], col('#5a361e'));
    p0 = Pt(0); p1 = Pt(7); px.line(B, p0[0], p0[1], p1[0], p1[1], col('#c8d0e0'));
    p0 = Pt(8); px.dot(B, tr(p0[0]), tr(p0[1]), k);
    const gx = -uy, gy = ux;
    px.line(B, c - ux + gx * 2, c - uy + gy * 2, c - ux - gx * 2, c - uy - gy * 2, col('#c89a20'));
    p0 = Pt(3); px.dot(B, tr(p0[0]), tr(p0[1]), WHITE);
    v = { u32: B.u32, w: size, h: size };
    knifeCache.set('p' + angq, v);
    return v;
  }
  // fx.knives：items = [[x, y, 角度], …]（(x, y) = 刀中心）；飞行中刀尾 3 条速度线；frozen = 时停中静止 + 偶尔一像素闪光
  FX.knives = function (P, items, t, kw) {
    kw = kw || {};
    const frozen = !!kw.frozen, streak = def(kw.streak, 14), sc = col(def(kw.streak_colour, '#e8ecff'));
    const kp = sprPix('prop:knife', 'idle', 0);
    for (let j = 0; j < items.length; j++) {
      const x = items[j][0], y = items[j][1], ang = items[j][2], angq = pmod(rnd(ang / 5) * 5, 360);
      const a = ang * RAD, ux = Math.cos(a), uy = -Math.sin(a);
      if (!frozen && streak > 0) {
        const hl = kp ? kp.w / 2 : 7;
        for (let q = 0; q < 3; q++) {
          const off = q - 1, ln = streak * (off === 0 ? 1 : 0.6);
          for (let s = tr(hl); s < tr(hl + ln); s++) dotA(P, x - ux * s - uy * off * 1.5, y - uy * s + ux * off * 1.5, sc, 0.9 * (1 - (s - hl) / ln));
        }
      }
      if (kp) px.stamp(P, px.variant(kp, 0, 0, kp.w, kp.h, { rotDeg: -angq, ax: kp.w / 2, ay: kp.h / 2 }), x, y, 1, 1);
      else { const im = knifeProc(angq); px.stamp(P, px.variant(im, 0, 0, im.w, im.h, { ax: im.w / 2, ay: im.h / 2 }), x, y, 1, 1); }
      if (frozen && tr(t * 3 + j * 0.37) % 5 === 0) px.dot(P, rnd(x + ux * 3), rnd(y + uy * 3), WHITE);
    }
  };

  // =================================================================== 时停
  const lum8 = px.lum8;
  const stopLUT = tint => px.lumLUT(pal(tsPal(tint)), 0.5, 0.9);
  // fx.timestop_world：停止时间的画面（亮度映射到 6 色调色板 + 有序抖动）；amount < 1 抖动过渡
  FX.timestop_world = function (P, kw) {
    if (typeof kw === 'number') kw = { amount: kw };
    kw = kw || {};
    const amount = def(kw.amount, 1);
    if (amount <= 0) return;
    px.lummap(P, pal(tsPal(def(kw.tint, 'yellow'))), 0.5, 0.9, amount);
  };
  // fx._sphere_mix：d < R → inside 处理，否则 outside；模式 0 不动 / 1 反色 / 2 停止色 / 3 停止色再反色
  function sphereMix(P, R, cx, cy, inMode, outMode, rim, rimw, rim2, band, lut) {
    const d = px.dist(cx, cy, 1, P.w, P.h), u = P.u32, W = P.w, rimT = rimw / 2 + 0.2, rc = rim == null ? 0 : col(rim), r2 = rim2 == null ? 0 : col(rim2);
    for (let y = 0; y < P.h; y++) {
      const row = y * W, br = (y & 3) << 2;
      for (let x = 0; x < W; x++) {
        const i = row + x, v = u[i], dist = d[i], mode = dist < R ? inMode : outMode;
        let res = v;
        if (mode === 1) res = (v ^ 0x00ffffff) >>> 0;
        else if (mode === 2) res = lut[((br | (x & 3)) << 8) | lum8(v)];
        else if (mode === 3) res = (lut[((br | (x & 3)) << 8) | lum8(v)] ^ 0x00ffffff) >>> 0;
        if (band > 0 && dist >= R - band && dist < R) res = (v ^ 0x00ffffff) >>> 0;
        if (rim != null) {
          if (Math.abs(dist - R) < rimT) res = rc;
          if (rim2 != null && Math.abs(dist - (R + 4)) < 0.6 && BAY[br | (x & 3)] < 0.6) res = r2;
        }
        u[i] = res;
      }
    }
  }
  FX._sphere_mix = sphereMix;
  // fx.timestop：「ZA WARUDO」——反色球扩张 → 全屏反色 → 球收缩留下停止色调；返回停止程度 0..1。kw.t_end 给了就自动接 time_resume
  FX.timestop = function (P, t, t0, cx, cy, kw) {
    kw = kw || {};
    if (t < t0) return 0;
    const dur = def(kw.dur, 1), tint = def(kw.tint, 'yellow'), tEnd = kw.t_end == null ? null : kw.t_end, rd = def(kw.resume_dur, 0.6);
    if (tEnd != null && t >= tEnd) {
      FX.time_resume(P, t, tEnd, cx, cy, { dur: rd, tint });
      return 1 - prog(t, tEnd, tEnd + rd);
    }
    const u = (t - t0) / dur, pl = pal(tsPal(tint)), lightC = pl[pl.length - 2], Rm = rmax(P, cx, cy) + 4, lut = stopLUT(tint);
    if (u < 0.45) {
      if (kw.soft) sphereMix(P, Rm * ease(u / 0.45, 'out'), cx, cy, 2, 0, 'white', 2, lightC, 0, lut);   // 减少闪烁：球内直接停止色、不反色
      else sphereMix(P, Rm * ease(u / 0.45, 'out'), cx, cy, 1, 0, 'white', 2, lightC, 0, lut);
      return 0;
    }
    if (u < 0.55) { sphereMix(P, Rm + 10, cx, cy, kw.soft ? 2 : 1, 0, null, 2, null, 0, lut); return 0.2; }
    if (u < 1) { sphereMix(P, Rm * (1 - ease((u - 0.55) / 0.45, 'in')), cx, cy, kw.soft ? 2 : 3, 2, lightC, 2, null, 0, lut); return 0.5 + 0.5 * (u - 0.55) / 0.45; }
    px.lummap(P, pl, 0.5, 0.9, 1);
    return 1;
  };
  // fx.time_resume：颜色从 (cx, cy) 涟漪般恢复（球外仍是停止色，1 px 白边，边内 7 px 反色带）
  FX.time_resume = function (P, t, t0, cx, cy, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 0.6);
    if (t < t0 || t >= t0 + dur) return;
    const tint = def(kw.tint, 'yellow'), R = (rmax(P, cx, cy) + 10) * ease((t - t0) / dur, 'in');
    sphereMix(P, R, cx, cy, 0, 2, 'white', 1, null, 7, stopLUT(tint));
  };

  // fx.clock：钟面（hour:minute 指针；cracked 0..1 长裂纹）
  FX.clock = function (P, x, y, r, hour, minute, kw) {
    kw = kw || {};
    const k = col('#1a1020'), rim = def(kw.rim, '#c89a20');
    px.disc(P, x, y, r + 1, k); px.disc(P, x, y, r, col(rim));
    px.disc(P, x - 1, y - 1, Math.max(1, r - 2), light(rim, 0.3));
    px.disc(P, x, y, Math.max(1, r - 2), dark(rim, 0.7));
    px.disc(P, x, y, Math.max(1, r - 3), col(def(kw.face, '#efe6d2')));
    const xi = rnd(x), yi = rnd(y);
    if (def(kw.numerals, true)) {
      for (let i = 0; i < 12; i++) {
        const ang = TAU * i / 12 - Math.PI / 2, ppx = rnd(x + Math.cos(ang) * (r - 4.5)), ppy = rnd(y + Math.sin(ang) * (r - 4.5));
        if (i % 3 === 0 && r >= 9) { px.dot(P, ppx, ppy, k); px.dot(P, ppx + rnd(-Math.cos(ang)), ppy + rnd(-Math.sin(ang)), k); }
        else px.dot(P, ppx, ppy, col('#6a5a50'));
      }
    }
    const ha = TAU * ((hour % 12) + minute / 60) / 12 - Math.PI / 2, ma = TAU * (minute / 60) - Math.PI / 2;
    px.line(P, xi, yi, xi + Math.cos(ha) * r * 0.45, yi + Math.sin(ha) * r * 0.45, k, 1, r >= 10 ? 2 : 1);
    px.line(P, xi, yi, xi + Math.cos(ma) * r * 0.72, yi + Math.sin(ma) * r * 0.72, k);
    px.dot(P, xi, yi, col('#c83030'));
    const cracked = def(kw.cracked, 0);
    if (cracked > 0) crackDraw(P, x + r * 0.2, y - r * 0.15, clamp(cracked), r * 1.1, def(kw.seed, 0), '#1a1020', null, [x, y, r - 2]);
  };

  // =================================================================== 发光、滤镜
  // fx.glow：抖动径向光（量化，不模糊）；add = 加法提亮
  FX.glow = function (P, x, y, r, colour, kw) {
    kw = kw || {};
    const alpha = def(kw.alpha, 0.6), add = !!kw.add, levels = def(kw.levels, 3), power = def(kw.power, 1.3);
    if (r <= 0 || alpha <= 0) return;
    const x0 = Math.max(0, tr(x - r)), y0 = Math.max(0, tr(y - r)), x1 = Math.min(P.w, tr(x + r + 1)), y1 = Math.min(P.h, tr(y + r + 1));
    if (x1 <= x0 || y1 <= y0) return;
    const c = col(colour), cr = cR(c), cg = cG(c), cb = cB(c), u = P.u32, ir = 1 / r;
    for (let yy = y0; yy < y1; yy++) {
      const dy = yy - y;
      for (let xx = x0; xx < x1; xx++) {
        const dx = xx - x, d = 1 - Math.sqrt(dx * dx + dy * dy) * ir;
        if (d <= 0) continue;
        px.qblendI(u, yy * P.w + xx, xx, yy, cr, cg, cb, Math.pow(d, power) * alpha, levels, add);
      }
    }
  };

  // fx.light_beam：斜光柱 + 浮尘
  FX.light_beam = function (P, x0, x1, top, bottom, t, kw) {
    kw = kw || {};
    const c = col(def(kw.colour, '#fff4c0')), slant = def(kw.slant, 0.45), alpha = def(kw.alpha, 0.5), motes = def(kw.motes, 18), seed = def(kw.seed, 0), spread = def(kw.spread, 0.25);
    top = tr(top); bottom = tr(bottom);
    const ya = Math.max(0, top), yb = Math.min(P.h, bottom);
    if (yb <= ya) return;
    const cr = cR(c), cg = cG(c), cb = cB(c), u = P.u32;
    for (let yy = ya; yy < yb; yy++) {
      const dy = yy - top, left = x0 + dy * (slant - spread * 0.5), right = x1 + dy * (slant + spread * 0.5);
      const wdt = Math.max(1, right - left), vert = 1 - 0.75 * dy / Math.max(1, bottom - top);
      const xa = Math.max(0, Math.floor(left) - 1), xb = Math.min(P.w, Math.ceil(right) + 1);
      for (let xx = xa; xx < xb; xx++) {
        const uu = (xx - left) / wdt, edge = clamp(Math.min(uu, 1 - uu) * wdt / 5);
        if (edge <= 0) continue;
        const shim = 0.8 + 0.2 * Math.sin((xx - dy * slant) * 0.35 + t * 1.5);
        px.qblendI(u, yy * P.w + xx, xx, yy, cr, cg, cb, clamp(edge * vert * shim * alpha), 3, false);
      }
    }
    const mc = light(c, 0.5);
    for (let i = 0; i < motes; i++) {
      const v = H(seed, i, 1), yv = top + (bottom - top) * fmod1(v + t * 0.03 * (0.5 + H(seed, i, 2)));
      const dyv = yv - top, l_ = x0 + dyv * (slant - spread * 0.5), r_ = x1 + dyv * (slant + spread * 0.5);
      const xv = l_ + (r_ - l_) * (0.1 + 0.8 * H(seed, i, 3)) + Math.sin(t * 0.8 + i) * 3;
      if (Math.sin(t * 2 + i * 1.3) > -0.3) px.dot(P, rnd(xv), rnd(yv), mc);
    }
  };

  // fx.vignette：抖动暗角
  const vigCache = new Map();
  function vigField(W, Hh) {
    const key = W + 'x' + Hh;
    let f = vigCache.get(key);
    if (f) return f;
    f = new Float32Array(W * Hh);
    for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) {
      const dx = (x + 0.5 - W / 2) / (W / 2), dy = (y + 0.5 - Hh / 2) / (Hh / 2);
      f[y * W + x] = Math.sqrt(dx * dx * 0.85 + dy * dy);
    }
    vigCache.set(key, f);
    return f;
  }
  FX.vignette = function (P, kw) {
    if (typeof kw === 'number') kw = { amount: kw };
    kw = kw || {};
    const amount = def(kw.amount, 0.6);
    if (amount <= 0) return;
    const c = col(def(kw.colour, 'black')), inner = def(kw.inner, 0.65), f = vigField(P.w, P.h), u = P.u32;
    const cr = cR(c), cg = cG(c), cb = cB(c), k = 1 / (1.35 - inner);
    for (let y = 0; y < P.h; y++) for (let x = 0; x < P.w; x++) {
      const i = y * P.w + x, d = (f[i] - inner) * k;
      if (d <= 0) continue;
      px.qblendI(u, i, x, y, cr, cg, cb, Math.pow(d > 1 ? 1 : d, 1.2) * amount, 3, false);
    }
  };

  // fx._row_shift / heat_haze / underwater_wobble / caustic_light
  let _row = new Uint32Array(512);
  function rowShift(P, y0, y1, shiftOf) {
    y0 = Math.max(0, tr(y0)); y1 = Math.min(P.h, tr(y1));
    if (_row.length < P.w) _row = new Uint32Array(P.w);
    const u = P.u32, W = P.w;
    for (let y = y0; y < y1; y++) {
      const sh = shiftOf(y);
      if (!sh) continue;
      const row = y * W;
      for (let x = 0; x < W; x++) _row[x] = u[row + x];
      for (let x = 0; x < W; x++) { let sx = x - sh; sx = sx < 0 ? 0 : sx > W - 1 ? W - 1 : sx; u[row + x] = _row[sx]; }
    }
  }
  FX.heat_haze = function (P, t, y0, y1, kw) {
    kw = kw || {};
    const amp = def(kw.amp, 1), ts = Math.floor(t * def(kw.fps, 12)) / def(kw.fps, 12);
    rowShift(P, y0, y1, y => rnd(amp * Math.sin(y * 0.45 + ts * 9) * (0.6 + 0.4 * Math.sin(y * 0.13 - ts * 3))));
  };
  FX.underwater_wobble = function (P, t, kw) {
    kw = kw || {};
    const amp = def(kw.amp, 1), ts = Math.floor(t * def(kw.fps, 12)) / def(kw.fps, 12);
    rowShift(P, 0, P.h, y => rnd(amp * Math.sin(y * 0.12 + ts * 3.1) + amp * 0.6 * Math.sin(y * 0.31 - ts * 4.7)));
    if (kw.caustics) FX.caustic_light(P, t, { y0: 0, y1: P.h * 0.45, colour: def(kw.colour, '#a8f0ff') });
  };
  FX.caustic_light = function (P, t, kw) {
    kw = kw || {};
    const y0 = Math.max(0, tr(def(kw.y0, 0))), y1 = Math.min(P.h, tr(def(kw.y1, P.h / 2)));
    if (y1 <= y0) return;
    const c = col(def(kw.colour, '#a8f0ff')), alpha = def(kw.alpha, 0.55), fps = def(kw.fps, 12), ts = Math.floor(t * fps) / fps;
    const cr = cR(c), cg = cG(c), cb = cB(c), u = P.u32;
    for (let yy = y0; yy < y1; yy++) {
      const fade = 1 - (yy - y0) / Math.max(1, y1 - y0);
      for (let xx = 0; xx < P.w; xx++) {
        const wx = xx * 0.11 + Math.sin(yy * 0.19 + ts * 1.7) * 1.3, wy = yy * 0.17 + Math.sin(xx * 0.07 - ts * 1.3) * 1.3;
        const net = clamp(1 - Math.min(Math.abs(Math.sin(wx + ts * 0.9)), Math.abs(Math.sin(wy - ts * 0.7))) * 5);
        if (net > 0) px.qblendI(u, yy * P.w + xx, xx, yy, cr, cg, cb, net * fade * alpha, 2, false);
      }
    }
  };

  // =================================================================== 碎裂、裂纹
  // 精灵 → Voronoi 碎片（缓存）
  const pieceCache = new Map();
  function voronoiPieces(v, pieces, seed) {
    const xsA = [], ysA = [];
    let bx0 = v.w, bx1 = 0, by0 = v.h, by1 = 0, sx = 0, sy = 0;
    for (let y = 0; y < v.h; y++) for (let x = 0; x < v.w; x++) if (v.u32[y * v.w + x] >>> 24) {
      xsA.push(x); ysA.push(y); sx += x; sy += y;
      if (x < bx0) bx0 = x; if (x + 1 > bx1) bx1 = x + 1; if (y < by0) by0 = y; if (y + 1 > by1) by1 = y + 1;
    }
    const N = xsA.length;
    if (!N) return { ps: [], cx: v.w / 2, cy: v.h / 2 };
    const sxp = new Float64Array(pieces), syp = new Float64Array(pieces);
    for (let i = 0; i < pieces; i++) { sxp[i] = bx0 + H(seed, i, 1) * (bx1 - bx0); syp[i] = by0 + H(seed, i, 2) * (by1 - by0); }
    const lab = new Int32Array(N);
    for (let p = 0; p < N; p++) {
      let best = 0, bd = Infinity;
      for (let i = 0; i < pieces; i++) { const dx = xsA[p] - sxp[i], dy = ysA[p] - syp[i], d = dx * dx + dy * dy; if (d < bd) { bd = d; best = i; } }
      lab[p] = best;
    }
    const ps = [];
    for (let j = 0; j < pieces; j++) {
      let cnt = 0, x0 = 1e9, y0 = 1e9, mx = 0, my = 0;
      for (let p = 0; p < N; p++) if (lab[p] === j) { cnt++; mx += xsA[p]; my += ysA[p]; if (xsA[p] < x0) x0 = xsA[p]; if (ysA[p] < y0) y0 = ysA[p]; }
      if (!cnt) continue;
      const xs = new Int16Array(cnt), ys = new Int16Array(cnt), cs = new Uint32Array(cnt);
      let q = 0;
      for (let p = 0; p < N; p++) if (lab[p] === j) { xs[q] = xsA[p] - x0; ys[q] = ysA[p] - y0; cs[q] = v.u32[ysA[p] * v.w + xsA[p]]; q++; }
      ps.push({ xs, ys, cs, x0, y0, pcx: mx / cnt, pcy: my / cnt });
    }
    return { ps, cx: sx / N, cy: sy / N };
  }
  function tintCol(c, mode, k, tr_, tg, tb) {             // sprite._apply_tint 的单像素版
    let r = c & 255, g = (c >>> 8) & 255, b = (c >>> 16) & 255;
    if (mode === 1) { r += (255 - r) * k; g += (255 - g) * k; b += (255 - b) * k; }
    else if (mode === 2) { r *= 1 - k; g *= 1 - k; b *= 1 - k; }
    else { r = r * (1 - k) + tr_ * k; g = g * (1 - k) + tg * k; b = b * (1 - k) + tb * k; }
    return pack(r | 0, g | 0, b | 0);
  }
  // fx.shatter：精灵按 Voronoi 切成 pieces 块炸开、下落、抖动淡出；src = 图集 id（+ kw.logical）/ 'cid.logical' / pix 对象
  FX.shatter = function (P, src, x, y, t, t0, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 1.2), dt = t - t0;
    if (dt < 0 || dt >= dur) return;
    const pieces = def(kw.pieces, 40), seed = def(kw.seed, 0), frame = kw.frame | 0, flip = !!kw.flip, scale = def(kw.scale, 1);
    const force = def(kw.force, 1), gravity = def(kw.gravity, 150), tintTo = kw.tint_to == null ? null : kw.tint_to;
    const key = (src && src.u32 ? 'pix' + (src.w + 'x' + src.h) : String(src)) + '|' + (kw.logical || '') + '|' + frame + '|' + flip + '|' + scale + '|' + pieces + '|' + seed;
    let pc = pieceCache.get(key);
    if (!pc) {
      const p = sprOrFig(src, kw.logical, frame, kw.colour);
      const v = sv(p, { flip, scale });
      pc = voronoiPieces(v, pieces, seed);
      pc.ax = v.ax; pc.ay = v.ay;
      pieceCache.set(key, pc);
      if (pieceCache.size > 64) pieceCache.delete(pieceCache.keys().next().value);
    }
    let cxm = pc.cx, cym = pc.cy;
    if (kw.origin) { cxm = kw.origin[0]; cym = kw.origin[1]; }
    const u = dt / dur, bx = x - pc.ax, by = y - pc.ay, u32 = P.u32, W = P.w;
    let tm = 0, tk = 0, tcr = 0, tcg = 0, tcb = 0;
    if (tintTo != null) {
      tk = clamp(u * 1.6);
      if (tintTo === 'white') tm = 1; else if (tintTo === 'black' || tintTo === 'silhouette') tm = 2;
      else { tm = 3; const c = col(tintTo); tcr = cR(c); tcg = cG(c); tcb = cB(c); }
    }
    const al = u < 0.55 ? 1 : 1 - (u - 0.55) / 0.45, flash = dt < 0.07;
    for (let j = 0; j < pc.ps.length; j++) {
      const pe = pc.ps[j], delay = 0.06 * H(seed, j, 3), e = Math.max(0, dt - delay);
      let ox, oy;
      if (flash) { ox = (pe.pcx - cxm) * 0.08; oy = (pe.pcy - cym) * 0.08; }
      else {
        const vx = (pe.pcx - cxm) * 2.2 * force + (H(seed, j, 4) - 0.5) * 40 * force;
        const vy = (pe.pcy - cym) * 1.2 * force - (30 + 40 * H(seed, j, 5)) * force;
        ox = vx * e; oy = vy * e + 0.5 * gravity * e * e;
      }
      const X0 = rnd(bx + pe.x0 + ox), Y0 = rnd(by + pe.y0 + oy);
      for (let q = 0; q < pe.cs.length; q++) {
        const X = X0 + pe.xs[q], Y = Y0 + pe.ys[q];
        if (X < 0 || Y < 0 || X >= W || Y >= P.h) continue;
        if (al < 0.999 && !(BAY[((Y & 3) << 2) | (X & 3)] < al)) continue;
        let c = pe.cs[q];
        if (flash) c = tintCol(c, 1, 0.5, 0, 0, 0);
        else if (tm) c = tintCol(c, tm, tk, tcr, tcg, tcb);
        u32[Y * W + X] = c | 0xff000000;
      }
    }
  };

  // fx._crack_paths / _crack_draw / crack：锯齿主裂纹 + 分叉，dur 秒内长出，之后保持
  const crackCache = new Map();
  function crackPaths(size, seed, branches = 6) {
    const key = size.toFixed(1) + '|' + seed + '|' + branches;
    let paths = crackCache.get(key);
    if (paths) return paths;
    paths = [];
    for (let b = 0; b < branches; b++) {
      const ang = TAU * (b + 0.6 * H(seed, b, 1)) / branches, L = size * (0.55 + 0.45 * H(seed, b, 2));
      const pts = [[0, 0]];
      let ppx = 0, ppy = 0, acc = 0, q = 0;
      while (acc < L) {
        const seg = 2.5 + 3 * H(seed, b, q, 3), a = ang + (H(seed, b, q, 4) - 0.5) * 1.1;
        ppx += Math.cos(a) * seg; ppy += Math.sin(a) * seg; acc += seg; pts.push([ppx, ppy]); q++;
      }
      paths.push([pts, 0]);
      if (pts.length > 3) {
        const k = 1 + tr(H(seed, b, 5) * (pts.length - 2));
        let sx = pts[k][0], sy = pts[k][1];
        const a2 = ang + (H(seed, b, 6) < 0.5 ? 0.7 : -0.7), sub = [[sx, sy]];
        for (let q2 = 0; q2 < 2 + tr(H(seed, b, 7) * 2); q2++) {
          const seg = 2 + 2.5 * H(seed, b, q2, 8), a = a2 + (H(seed, b, q2, 9) - 0.5) * 0.9;
          sx += Math.cos(a) * seg; sy += Math.sin(a) * seg; sub.push([sx, sy]);
        }
        paths.push([sub, k / Math.max(1, pts.length - 1)]);
      }
    }
    crackCache.set(key, paths);
    if (crackCache.size > 128) crackCache.delete(crackCache.keys().next().value);
    return paths;
  }
  function crackDraw(P, x, y, g, size, seed, colour, hi, clip) {
    const paths = crackPaths(Math.round(size * 10) / 10, seed), c = col(colour), hic = hi ? col(hi) : null;
    for (let pi = 0; pi < paths.length; pi++) {
      const pts = paths[pi][0], start = paths[pi][1];
      if (g <= start) continue;
      const gg = start < 1 ? (g - start) / (1 - start) : 1, n = pts.length, m = gg * (n - 1), k = tr(m);
      let seg = [];
      for (let i = 0; i <= Math.min(k, n - 1); i++) seg.push([x + pts[i][0], y + pts[i][1]]);
      if (k < n - 1) { const f = m - k; seg.push([x + pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, y + pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f]); }
      if (clip) {
        const s2 = [];
        for (const p of seg) { if ((p[0] - clip[0]) ** 2 + (p[1] - clip[1]) ** 2 <= clip[2] * clip[2]) s2.push(p); else break; }
        seg = s2;
      }
      if (seg.length < 2) continue;
      if (hic != null) px.lines(P, seg.map(p => [p[0] + 1, p[1] + 1]), hic);
      px.lines(P, seg, c);
    }
  }
  FX.crack = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    if (t < t0) return;
    crackDraw(P, x, y, ease(prog(t, t0, t0 + def(kw.dur, 0.25)), 'out'), def(kw.size, 30), def(kw.seed, 0), def(kw.colour, '#1a1020'), kw.hi || null, null);
  };

  // =================================================================== 转场
  // fx.iris：圆形转场（0 开、1 关）
  FX.iris = function (P, amount, kw) {
    kw = kw || {};
    if (amount <= 0) return;
    const c = col(def(kw.colour, 'black'));
    if (amount >= 1) { P.u32.fill(c); return; }
    const cx = def(kw.cx, P.w / 2), cy = def(kw.cy, P.h / 2), R = rmax(P, cx, cy) * (1 - amount), d = px.dist(cx, cy, 1, P.w, P.h), u = P.u32;
    for (let i = 0; i < u.length; i++) if (d[i] > R) u[i] = c;
  };
  // fx.diamond_wipe：复古菱形扫屏（0 开、1 盖满）
  const diaCache = new Map();
  FX.diamond_wipe = function (P, amount, kw) {
    kw = kw || {};
    if (amount <= 0) return;
    const c = col(def(kw.colour, 'black'));
    if (amount >= 1) { P.u32.fill(c); return; }
    const cell = def(kw.cell, 20), key = cell + '|' + P.w + 'x' + P.h;
    let f = diaCache.get(key);
    if (!f) {
      const man = new Float32Array(P.w * P.h), diag = new Float32Array(P.w * P.h), den = Math.floor(P.w / cell) + Math.floor(P.h / cell);
      for (let y = 0; y < P.h; y++) for (let x = 0; x < P.w; x++) {
        const lx = (x % cell) + 0.5 - cell / 2, ly = (y % cell) + 0.5 - cell / 2;
        man[y * P.w + x] = (Math.abs(lx) + Math.abs(ly)) / cell;
        diag[y * P.w + x] = (Math.floor(x / cell) + Math.floor(y / cell)) / den;
      }
      f = { man, diag };
      diaCache.set(key, f);
    }
    const rev = !!kw.reverse, u = P.u32;
    for (let i = 0; i < u.length; i++) {
      const dg = rev ? 1 - f.diag[i] : f.diag[i];
      if (f.man[i] < clamp(amount * 1.7 - dg * 0.7)) u[i] = c;
    }
  };
  // fx.slash_wipe：斜切转场 + 2 px 亮边（0 开、1 盖满；reverse 从右往左）
  FX.slash_wipe = function (P, amount, kw) {
    kw = kw || {};
    if (amount <= 0) return;
    const ta = Math.tan(def(kw.angle, 20) * RAD), span = P.w + P.h * Math.abs(ta) + 8, pos = -P.h * Math.abs(ta) - 4 + span * amount;
    const c = col(def(kw.colour, 'black')), edge = kw.edge === undefined ? 'white' : kw.edge, ec = edge ? col(edge) : 0, rev = !!kw.reverse, u = P.u32;
    for (let y = 0; y < P.h; y++) {
      const off = (P.h - y) * ta, row = y * P.w;
      for (let x = 0; x < P.w; x++) {
        const val = (rev ? P.w - 1 - x : x) + off;
        if (val < pos) u[row + x] = c;
        else if (edge && val < pos + 2) u[row + x] = ec;
      }
    }
  };
  // fx.sepia：褐色定格（6 级调色板 + 抖动）
  FX.sepia = function (P, kw) {
    if (typeof kw === 'number') kw = { amount: kw };
    kw = kw || {};
    const amount = def(kw.amount, 1);
    if (amount <= 0) return;
    px.lummap(P, pal('sepia'), def(kw.strength, 0.5), 0.95, amount);
  };

  // =================================================================== 风格化背景（铺满画布）
  const menCache = [];
  // fx.menace_bg：JoJo 威压旋涡背景（2–4 色，螺旋臂慢转，12 fps）；同一个 12 fps 步内直接复用上次结果
  FX.menace_bg = function (P, t, kw) {
    kw = kw || {};
    const fps = def(kw.fps, 12), ts = Math.floor(t * fps) / fps, cs = pal(def(kw.colours, ['#402060', '#200830']));
    const cx = def(kw.cx, P.w / 2), cy = def(kw.cy, P.h / 2), arms = def(kw.arms, 3), twist = def(kw.twist, 0.09), speed = def(kw.speed, 1.6);
    const key = ts + '|' + cs.join(',') + '|' + rnd(cx) + '|' + rnd(cy) + '|' + arms + '|' + twist + '|' + speed + '|' + P.w + 'x' + P.h;
    for (let i = 0; i < menCache.length; i++) if (menCache[i].key === key) { P.u32.set(menCache[i].buf); return; }
    const ang = px.angle(cx, cy, P.w, P.h), dist = px.dist(cx, cy, 1, P.w, P.h), n = cs.length, u = P.u32;
    for (let y = 0; y < P.h; y++) {
      const br = (y & 3) << 2, row = y * P.w;
      for (let x = 0; x < P.w; x++) {
        const i = row + x;
        let v = Math.sin(ang[i] * arms + dist[i] * twist - ts * speed) * 0.5 + 0.5;
        v = 0.75 * v + 0.25 * (Math.sin(dist[i] * 0.05 - ts * 1.1) * 0.5 + 0.5);
        let q = Math.floor(v * n + (BAY[br | (x & 3)] - 0.5) * 0.35);
        u[i] = cs[q < 0 ? 0 : q > n - 1 ? n - 1 : q];
      }
    }
    let slot = menCache.find(m => m.buf.length === u.length && m.used < 0);
    if (!slot) {
      if (menCache.length < 3) { slot = { key: '', buf: new Uint32Array(u.length), used: 0 }; menCache.push(slot); }
      else { slot = menCache.reduce((a, b) => (a.used <= b.used ? a : b)); if (slot.buf.length !== u.length) slot.buf = new Uint32Array(u.length); }
    }
    slot.key = key; slot.used = performance.now(); slot.buf.set(u);
  };
  // fx.radial_burst_bg：旋转放射条纹（点名卡、VS 卡、切入）；spin = 圈 / 秒，连续时间、无抖动
  FX.radial_burst_bg = function (P, t, kw) {
    kw = kw || {};
    const cx = def(kw.cx, P.w / 2), cy = def(kw.cy, P.h / 2), cs = pal(def(kw.colours, ['#f0c040', '#e07020'])), n = def(kw.n, 16), spin = def(kw.spin, 0.2);
    const ang = px.angle(cx, cy, P.w, P.h), k = cs.length, u = P.u32, off = t * spin;
    for (let i = 0; i < u.length; i++) u[i] = cs[pmod(Math.floor((ang[i] / TAU + off) * n), k)];
  };

  // =================================================================== 替身
  // fx.stand_summon：替身从本体升起（rise px），前 55% 30 Hz 隔帧消失、白化渐回原色、上升能量线；之后照常画（alpha + 光环）
  FX.stand_summon = function (P, cid, logical, x, y, t, t0, kw) {
    kw = kw || {};
    if (t < t0) return;
    const flip = !!kw.flip, frame = kw.frame | 0, dur = def(kw.dur, 0.35), ac = def(kw.aura_colour, '#c080ff'), alpha = def(kw.alpha, 0.92);
    const rise = def(kw.rise, 12), scale = def(kw.scale, 1), u = (t - t0) / dur, p = sprPix(cid, logical, frame);
    if (u < 1) {
      const yy = y + rise * (1 - ease(u, 'out')), vis = Math.floor((t - t0) * 30) % 2 === 0 || u > 0.55;
      if (p) auraDraw(P, p, x, yy, flip, scale, ac, t, 0.7 * u);
      if (vis) {
        let v;
        if (p) v = sv(p, { flip, scale, tint: { c: 'white', k: Math.round((1 - u) * 100) / 100 } });
        else { const fg = figureImg(ac); v = px.variant(fg, 0, 0, fg.w, fg.h, { flip, tint: { c: 'white', k: Math.round((1 - u) * 100) / 100 }, ax: fg.w / 2, ay: fg.h }); }
        px.stamp(P, v, x, yy, alpha * Math.min(1, 0.25 + u), 1);
      }
      summonLines(P, x, y, u, t0, ac);
      return;
    }
    if (p) { auraDraw(P, p, x, y, flip, scale, ac, t); px.stamp(P, sv(p, { flip, scale }), x, y, 1, alpha); }
    else { const fg = figureImg(ac); px.stamp(P, px.variant(fg, 0, 0, fg.w, fg.h, { flip, ax: fg.w / 2, ay: fg.h }), x, y, 1, alpha); }
  };
  function summonLines(P, x, y, u, t0, ac) {
    const a = col(ac), l = light(a, 0.6), k = tr(t0 * 10);
    for (let j = 0; j < 8; j++) {
      const sx = x + (H(j, 3, k) - 0.5) * 30, ph = fmod1(u * 1.6 + H(j, 4)), sy = y - 4 - ph * 44, L = 4 + tr(6 * H(j, 5));
      px.line(P, sx, sy, sx, sy + L, j % 2 ? l : a);
    }
  }
  // stand_summon 里那 8 条上升能量线（拆出来单独用；stand.js 召唤时 spawn）
  FX.summon_lines = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 0.35);
    if (t < t0 || t - t0 >= dur) return;
    summonLines(P, x, y, (t - t0) / dur, t0, def(kw.colour, def(kw.aura_colour, '#c080ff')));
  };
  // s07 stand_out：替身白化 + 抖动溶解退场（替身收回、被控制的友方“胜负已分”）
  FX.stand_out = function (P, cid, logical, x, y, t, t0, kw) {
    kw = kw || {};
    const u = prog(t, t0, t0 + def(kw.dur, 0.25));
    if (u >= 1) return;
    const p = sprOrFig(cid, logical, kw.frame | 0, kw.colour);
    px.stamp(P, sv(p, { flip: !!kw.flip, scale: def(kw.scale, 1), tint: { c: 'white', k: Math.round(u * 80) / 100 } }), x, y, 0.92 * (1 - u), 1);
  };

  // fx._aura_fields：剪影膨胀 grow 次 + 向上拖尾 K 级（缓存）
  const auraFieldCache = new Map();
  function auraFields(p, cacheKey, flip, scale, grow, K) {
    const key = cacheKey + '|' + flip + '|' + scale + '|' + grow + '|' + K;
    let F = auraFieldCache.get(key);
    if (F) return F;
    const v = sv(p, { flip, scale }), pad = grow + K + 2, W2 = v.w + 2 * (grow + 2), H2 = v.h + pad + grow + 2;
    let m = new Uint8Array(W2 * H2);
    for (let y = 0; y < v.h; y++) for (let x = 0; x < v.w; x++) if (v.u32[y * v.w + x] >>> 24) m[(y + pad) * W2 + x + grow + 2] = 1;
    for (let g = 0; g < grow; g++) {
      const n = m.slice();
      for (let y = 0; y < H2; y++) for (let x = 0; x < W2; x++) {
        const i = y * W2 + x;
        if (m[i]) continue;
        if ((y > 0 && m[i - W2]) || (y < H2 - 1 && m[i + W2]) || (x > 0 && m[i - 1]) || (x < W2 - 1 && m[i + 1])) n[i] = 1;
      }
      m = n;
    }
    const mf = new Float32Array(W2 * H2), up = new Float32Array(W2 * H2);
    for (let i = 0; i < mf.length; i++) mf[i] = m[i];
    for (let k = 1; k <= K; k++) {
      const wt = 1 - k / (K + 1);
      for (let y = 0; y < H2 - k; y++) for (let x = 0; x < W2; x++) {
        const val = mf[(y + k) * W2 + x] * wt;
        if (val > up[y * W2 + x]) up[y * W2 + x] = val;
      }
    }
    F = { mf, up, w: W2, h: H2, ax: v.ax + grow + 2, ay: v.ay + pad };
    auraFieldCache.set(key, F);
    if (auraFieldCache.size > 96) auraFieldCache.delete(auraFieldCache.keys().next().value);
    return F;
  }
  // 热场 → 打包色写进 dst（dst = 像素会话 / 缓存画布的 u32）；(ox, oy) = 场左上角在 dst 里的位置；(bx, by) = Bayer 坐标原点
  function auraPaint(dst, dw, dh, F, ox, oy, bx, by, t, kw) {
    const fps = def(kw.fps, 12), ts = Math.floor(t * fps) / fps, seed = def(kw.seed, 0), intensity = def(kw.intensity, 1);
    const tex = noiseTex((seed + 2) % 4), c = col(def(kw.colour, '#c080ff'));
    const p0 = dark(c, 0.55), p1 = c, p2 = light(c, 0.55);
    for (let yy = 0; yy < F.h; yy++) {
      const Y = oy + yy;
      if (Y < 0 || Y >= dh) continue;
      const ry = (Math.floor(yy * 1.6 + ts * 70) & 63) * 64, br = ((by + yy) & 3) << 2;
      for (let xx = 0; xx < F.w; xx++) {
        const X = ox + xx;
        if (X < 0 || X >= dw) continue;
        const i = yy * F.w + xx, mf = F.mf[i], up = F.up[i];
        if (!mf && !up) continue;
        const n = tex[ry + (Math.floor(xx * 3.1 + seed * 7) & 63)];
        const a = mf * (0.55 + 0.5 * n), b = up * (0.2 + 1.2 * n), heat = (a > b ? a : b) * intensity;
        const lvl = Math.floor(heat * 3.4 + (BAY[br | ((bx + xx) & 3)] - 0.5) * 0.9);
        if (lvl >= 1) dst[Y * dw + X] = lvl === 1 ? p0 : lvl === 2 ? p1 : p2;
      }
    }
  }
  // fx.aura_flame（像素会话版，剧情插入画面用）：src = 图集 id（+ kw.logical）/ 'cid.logical'；精灵之前、同锚点调用
  FX.aura_flame = function (P, src, x, y, t, kw) {
    kw = kw || {};
    const frame = kw.frame | 0, flip = !!kw.flip, scale = def(kw.scale, 1), grow = def(kw.grow, 3) | 0, K = def(kw.height, 14) | 0;
    const p = sprOrFig(src, kw.logical, frame, null);
    const F = auraFields(p, src && src.u32 ? 'pix' + p.w + 'x' + p.h : String(src) + '|' + (kw.logical || '') + '|' + frame, flip, scale, grow, K);
    const ox = rnd(x - F.ax), oy = rnd(y - F.ay);
    auraPaint(P.u32, P.w, P.h, F, ox, oy, ox, oy, t, kw);
  };
  FX.aura_wisps = function (P, x, y, t, kw) {
    kw = kw || {};
    FX.aura_flame(P, kw.src || null, x, y, t, kw);
  };

  // =================================================================== 蝙蝠
  const BAT_UP = `
k...........k
kk.........kk
kPk.......kPk
.kPkk.k.kkPk.
..kkkkkkkkk..
....krkrk....
.....kkk.....`;
  const BAT_DN = `
.....k.k.....
....kkkkk....
..kkkrkrkkk..
.kPkkkkkkkPk.
kPk.......kPk
kk.........kk
k...........k`;
  let batImgs = null;
  FX.bats = function (P, t, t0, x, y, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 2.2), dt = t - t0;
    if (dt < 0 || dt > dur) return;
    const n = def(kw.n, 12), seed = def(kw.seed, 0), speed = def(kw.speed, 110), spread = def(kw.spread, 150), angle = def(kw.angle, 90);
    const spr = sprPix('prop:bat', 'idle', 0);
    if (!spr && !batImgs) batImgs = [gridImg(BAT_UP, { P: '#7a5a9a', r: '#ff3040' }), gridImg(BAT_DN, { P: '#7a5a9a', r: '#ff3040' })];
    for (let i = 0; i < n; i++) {
      const e = dt - 0.35 * H(seed, i, 1);
      if (e < 0) continue;
      const a = (angle + (H(seed, i, 2) - 0.5) * spread) * RAD, v = speed * (0.6 + 0.7 * H(seed, i, 3)), dist = v * e + 40 * e * e;
      const fl = Math.sin(e * 9 + i) * 5, sx = (H(seed, i, 10) - 0.5) * 12, sy = (H(seed, i, 11) - 0.5) * 6;
      const ppx = x + sx + Math.cos(a) * dist + Math.sin(a) * fl, ppy = y + sy - Math.sin(a) * dist + Math.cos(a) * fl * 0.5;
      if (ppx < -20 || ppx > P.w + 20 || ppy < -20 || ppy > P.h + 20) continue;
      const f = tr(t * 14 + H(seed, i, 4) * 2) % 2;
      const im = spr ? (sprPix('prop:bat', 'idle', f) || spr) : batImgs[f];
      const big = !spr && H(seed, i, 9) < 0.2 ? 2 : 1;
      px.stamp(P, px.variant(im, 0, 0, im.w, im.h, { flip: Math.cos(a) < 0, scale: big, ax: im.w / 2, ay: im.h / 2 }), ppx, ppy, 1, 1);
    }
  };

  // =================================================================== 场景辅助函数（原片场景文件里的，去掉下划线）
  const FIRE_COLS = [pack(150, 24, 24), pack(230, 80, 20), pack(255, 170, 40), pack(255, 240, 150), pack(255, 255, 235)];
  // s07 fireball：4 层同心椭圆（纵向 ×0.85）；heat 0..1 冷却偏红；lift > 0 每层提亮（小火块不能看着像血）
  FX.fireball = function (P, x, y, r, kw) {
    kw = kw || {};
    const heat = def(kw.heat, 1), lift = def(kw.lift, 0), a = def(kw.alpha, 1);
    x = rnd(x); y = rnd(y);
    const LV = [1, 0.72, 0.45, 0.22];
    for (let k = 0; k < 4; k++) {
      const ci = tr(clamp(k + lift - (1 - heat) * 2.5, 0, 4)), rr = r * LV[k];
      if (rr < 0.6) continue;
      px.ellipse(P, x - rr, y - rr * 0.85, x + rr, y + rr * 0.85, FIRE_COLS[ci], null, 1, a);
    }
  };
  // s07 fire_jet：从 x0 到 x1 的横向火焰洪流（每 3.5 px 一个 fireball，14 fps 抖动）；x1 < x0 时向左
  FX.fire_jet = function (P, x0, x1, y, t, kw) {
    kw = kw || {};
    const seed = def(kw.seed, 0), thick = def(kw.thick, 1), span = Math.abs(x1 - x0);
    if (span <= 1) return;
    const k = tr(t * 14), n = Math.max(2, tr(span / 3.5)), dir = x1 >= x0 ? 1 : -1, sc = pack(255, 220, 90);
    for (let i = 0; i < n; i++) {
      const u = i / (n - 1), xx = x0 + (x1 - x0) * u, wob = Math.sin(u * 9 + t * 22 + seed) * 2;
      const r = (4.5 + 2 * H(i, k, seed)) * thick * (0.75 + 0.45 * u);
      FX.fireball(P, xx, y + wob, r, { heat: 0.9 + 0.1 * H(i, k, 3) });
    }
    for (let j = 0; j < 6; j++) {
      const ph = fmod1(t * 3 + H(j, seed, 7)), sx = x0 + (x1 - x0) * H(j, seed, 8) + dir * ph * 10, sy = y - 6 - ph * 10 * (j % 2 ? 1 : -1);
      const lo = Math.min(x0, x1) - (dir < 0 ? 6 : 0), hi = Math.max(x0, x1) + (dir > 0 ? 6 : 0);
      if (sx >= lo && sx <= hi) px.dot(P, rnd(sx), rnd(sy), sc);
    }
  };
  // s07 fire_chunks：被剑切碎的火团飞散（0.55 s，保持橙黄）；kw.direction 扩展：−1 往左飘
  FX.fire_chunks = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const dt = t - t0;
    if (dt < 0 || dt > 0.55) return;
    const seed = def(kw.seed, 0), n = def(kw.n, 6), speed = def(kw.speed, 90), dir = def(kw.direction, 1);
    for (let i = 0; i < n; i++) {
      const up = i % 2 === 0 ? 1 : -1, a = (25 + 40 * H(seed, i, 1)) * RAD * up, v = speed * (0.6 + 0.6 * H(seed, i, 2));
      const ppx = x + dir * (Math.cos(a) * v * dt * 0.8 + 6 * dt), ppy = y - Math.sin(a) * v * dt + 60 * dt * dt;
      const r = (3.5 + 2 * H(seed, i, 3)) * (1 - dt / 0.55);
      if (r > 0.6) FX.fireball(P, ppx, ppy, r, { heat: 1 - 0.4 * dt / 0.55, lift: 1 });
    }
  };
  // s07 slash_arc：银色战车剑光（9 点弧线覆盖 120°，白 → #9cc8ff，前半 2 px）。flip 默认 true（原片：弧往左）；朝右出剑传 flip: false
  FX.slash_arc = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 0.1), u = prog(t, t0, t0 + dur);
    if (t < t0 || u >= 1) return;
    const size = def(kw.size, 12), seed = def(kw.seed, 0), fl = def(kw.flip, true) ? -1 : 1, ang0 = -60 + 40 * H(seed, 1);
    const pts = [];
    for (let k = 0; k < 9; k++) { const a = (ang0 + 120 * k / 8) * RAD; pts.push([x + Math.cos(a) * size * 0.45 * fl, y - Math.sin(a) * size]); }
    px.lines(P, pts, mix('white', '#9cc8ff', u), 1, u < 0.5 ? 2 : 1);
  };
  // s07 dim_bg：压暗 + 冷色（替身亮相的聚光），平滑混色，最多 0.9
  FX.dim_bg = function (P, a, kw) {
    kw = kw || {};
    if (a <= 0.01) return;
    const c = col(def(kw.col, def(kw.colour, '#140c30'))), k = Math.round(Math.min(a, 0.9) * 100) / 100, cr = cR(c), cg = cG(c), cb = cB(c), u = P.u32;
    for (let i = 0; i < u.length; i++) {
      const v = u[i], r = v & 255, g = (v >>> 8) & 255, b = (v >>> 16) & 255;
      u[i] = pack(r + k * (cr - r), g + k * (cg - g), b + k * (cb - b));
    }
  };
  // s07 blade_ext / coin_on_blade：把 chariot.thrust 帧 1（剑朝左）的剑身加长，硬币串在剑上
  const BLADE_HI = pack(255, 255, 255), BLADE_LO = pack(140, 150, 172), BLADE_OL = pack(26, 16, 32);
  FX.blade_ext = function (P, X, Y) {
    const by = Y - 35;
    px.line(P, X - 69, by - 1, X - 52, by - 1, BLADE_OL);
    px.line(P, X - 70, by, X - 52, by, BLADE_HI);
    px.line(P, X - 68, by + 1, X - 52, by + 1, BLADE_LO);
    px.dot(P, X - 71, by, BLADE_OL);
  };
  FX.coin_on_blade = function (P, X, Y, i) {
    const by = Y - 35, cx = X - 64 + 6 * i, f = i % 2 === 0 ? 1 : 3;
    if (!FX.sprite(P, 'prop:coin', cx, by, { frame: f })) { px.disc(P, cx, by, 3, col('#c89a20')); px.disc(P, cx, by, 2, col('#ffd83c')); }
    px.line(P, cx - 2, by, cx + 1, by, BLADE_HI);
  };
  // s04 _ora_bg：欧拉漫画格底（紫三色放射 n 22 spin .35 + 径向速度线 n 40 inner 34）
  FX.ora_bg = function (P, t, cx, cy) {
    FX.radial_burst_bg(P, t, { cx, cy, colours: ['#5a2aa0', '#34146a', '#46208a'], n: 22, spin: 0.35 });
    FX.speedlines(P, t, { cx, cy, style: 'radial', n: 40, colour: '#d8c8ff', inner: 34, alpha: 0.55, seed: 8, fps: 16 });
  };
  // s02 _cap_shadow：承太郎压帽——帽檐阴影把眼睛那一条（pose 帧 1 的 x 12–27、y 14–18，相对锚点 −6..9 / −38..−34）
  // 压暗到 28%，青色瞳孔 (44,196,168) 改成发光的 (140,255,235)。画在 jotaro.pose 帧 1 上，同锚点；kw = { scale: 3, amount: 1, fade: 0.1 }
  const capCache = new Map();
  FX.cap_shadow = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    if (t < t0) return;
    const scale = def(kw.scale, 3), amount = def(kw.amount, 1) * clamp((t - t0) / def(kw.fade, 0.1));
    if (amount <= 0) return;
    const p = sprPix('jotaro', 'pose', 1);
    if (!p) return;
    let ov = capCache.get(p);
    if (!ov) {
      const u = new Uint32Array(p.w * p.h), x0 = rnd(p.ox) - 6, x1 = rnd(p.ox) + 9, y0 = rnd(p.oy) - 38, y1 = rnd(p.oy) - 34;
      for (let yy = Math.max(0, y0); yy < Math.min(p.h, y1); yy++) for (let xx = Math.max(0, x0); xx < Math.min(p.w, x1); xx++) {
        const c = p.u32[yy * p.w + xx];
        if (!(c >>> 24)) continue;
        const r = c & 255, g = (c >>> 8) & 255, b = (c >>> 16) & 255;
        u[yy * p.w + xx] = (r === 44 && g === 196 && b === 168) ? pack(140, 255, 235)
          : pack(r * 0.28 + 40 * 0.25, g * 0.28 + 16 * 0.25, b * 0.28 + 70 * 0.25);
      }
      ov = { u32: u, w: p.w, h: p.h, ox: p.ox, oy: p.oy };
      capCache.set(p, ov);
    }
    px.stamp(P, sv(ov, { flip: !!kw.flip, scale }), x, y, amount, 1);
  };
  // s18 clash_sparks：对拳接触点每秒 rate 个 hit_spark（±10 / ±14，size 7–12）
  FX.clash_sparks = function (P, t, t0, t1, cx, cy, kw) {
    kw = kw || {};
    const seed = def(kw.seed, 0), rate = def(kw.rate, 11);
    if (t1 == null) t1 = Infinity;
    const k1 = tr((Math.min(t, t1) - t0) * rate);
    for (let k = Math.max(0, k1 - 3); k <= k1; k++) {
      const ts = t0 + k / rate;
      if (ts > t || ts > t1) continue;
      FX.hit_spark(P, cx - 10 + 20 * H(seed, k, 1), cy - 14 + 28 * H(seed, k, 2), t, ts, { size: 7 + tr(5 * H(seed, k, 3)), seed: k, accent: def(kw.accent, '#ffd83c') });
    }
  };

  // =================================================================== 新增（原片没有，游戏要）
  // 地面危险区预警（W3）：红框 + 抖动填充 16 Hz 明暗闪；dur 给了就从中心往外“灌满”提示命中时刻
  // kw = { colour: '#ff3048', dur, shape: 'rect' | 'ellipse', fill: true }
  FX.zone_warn = function (P, x0, y0, x1, y1, t, t0, kw) {
    kw = kw || {};
    const dt = t - t0, dur = kw.dur == null ? null : kw.dur;
    if (dt < 0 || (dur != null && dt > dur)) return;
    const c = col(def(kw.colour, '#ff3048')), lc = light(c, 0.55), on = Math.floor(dt * 16) % 2 === 0;
    const ell = kw.shape === 'ellipse', cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, rx = Math.abs(x1 - x0) / 2, ry = Math.abs(y1 - y0) / 2;
    const p = dur ? clamp(dt / dur) : 1;
    if (def(kw.fill, true)) {
      const fa = on ? 0.32 : 0.18;
      if (ell) px.ellipse(P, cx - rx, cy - ry, cx + rx, cy + ry, c, null, 1, fa);
      else px.box(P, x0, y0, x1, y1, c, fa);
      if (dur) {                                            // 灌满：内层随时间扩到整个区域，越接近越亮
        const kx = rx * p, ky = ry * p, ia = 0.25 + 0.45 * p;
        if (ell) px.ellipse(P, cx - kx, cy - ky, cx + kx, cy + ky, lc, null, 1, ia);
        else px.box(P, cx - kx, cy - ky, cx + kx, cy + ky, lc, ia);
      }
    }
    const oc = on ? lc : c;
    if (ell) px.ellipse(P, cx - rx, cy - ry, cx + rx, cy + ry, null, oc, 1);
    else {
      px.line(P, x0, y0, x1, y0, oc); px.line(P, x0, y1, x1, y1, oc); px.line(P, x0, y0, x0, y1, oc); px.line(P, x1, y0, x1, y1, oc);
      const L = Math.max(2, Math.min(5, Math.min(rx, ry)));    // 四角加亮
      for (const [ax, ay, sx, sy] of [[x0, y0, 1, 1], [x1, y0, -1, 1], [x0, y1, 1, -1], [x1, y1, -1, -1]]) {
        px.line(P, ax, ay, ax + sx * L, ay, WHITE); px.line(P, ax, ay, ax, ay + sy * L, WHITE);
      }
    }
  };
  // 弹道预警（W4）：pts = [[x0, y0], [x1, y1]] 直线或 [[x0, y0], [cx, cy], [x1, y1]] 二次贝塞尔；从起点画向终点（grow 秒内长满）
  // 2 px 红色虚线（段 4、空 3），16 Hz 明暗闪，终点 3 px 小叉；kw = { colour: '#ff3048', grow: 0.15, dur }
  let _wl = new Float64Array(1024);
  FX.warn_line = function (P, pts, t, t0, kw) {
    kw = kw || {};
    const dt = t - t0, dur = kw.dur == null ? null : kw.dur;
    if (dt < 0 || (dur != null && dt > dur) || !pts || pts.length < 2) return;
    const c = col(def(kw.colour, '#ff3048')), on = Math.floor(dt * 16) % 2 === 0, cc = on ? light(c, 0.35) : c;
    const a = pts[0], b = pts[pts.length - 1], q = pts.length > 2 ? pts[1] : null;
    const est = q ? Math.hypot(q[0] - a[0], q[1] - a[1]) + Math.hypot(b[0] - q[0], b[1] - q[1]) : Math.hypot(b[0] - a[0], b[1] - a[1]);
    const N = Math.max(2, Math.min(500, Math.ceil(est * 1.5)));
    if (_wl.length < (N + 1) * 3) _wl = new Float64Array((N + 1) * 3 + 64);
    let s = 0;
    for (let i = 0; i <= N; i++) {
      const u = i / N;
      let x, y;
      if (q) { const v = 1 - u; x = v * v * a[0] + 2 * v * u * q[0] + u * u * b[0]; y = v * v * a[1] + 2 * v * u * q[1] + u * u * b[1]; }
      else { x = a[0] + (b[0] - a[0]) * u; y = a[1] + (b[1] - a[1]) * u; }
      if (i > 0) s += Math.hypot(x - _wl[3 * i - 3], y - _wl[3 * i - 2]);
      _wl[3 * i] = x; _wl[3 * i + 1] = y; _wl[3 * i + 2] = s;
    }
    const total = s, vis = total * clamp(dt / Math.max(1e-3, def(kw.grow, 0.15)));
    for (let i = 0; i <= N; i++) {
      const si = _wl[3 * i + 2];
      if (si > vis) break;
      if (si % 7 >= 4) continue;
      px.rect(P, rnd(_wl[3 * i] - 0.5), rnd(_wl[3 * i + 1] - 0.5), 2, 2, cc);
    }
    if (vis >= total - 0.01) {
      const ex = rnd(b[0]), ey = rnd(b[1]);
      px.line(P, ex - 1, ey - 1, ex + 1, ey + 1, WHITE); px.line(P, ex - 1, ey + 1, ex + 1, ey - 1, WHITE);
      px.dot(P, ex - 2, ey - 2, cc); px.dot(P, ex + 2, ey - 2, cc); px.dot(P, ex - 2, ey + 2, cc); px.dot(P, ex + 2, ey + 2, cc);
    }
  };

  // 世界地图路线（bg_asia.draw_route 的画线部分；城市名由 UI 层画）。stops = 城市名 / [x, y]（世界地图画布坐标）
  // 城市坐标：kw.cities → G.D.bg.world_map.anchors（cities 或直接按名字）→ 原工程 CITIES。返回 { pos, u, arrived, dir }
  const CITIES = { 东京: [298, 44], 香港: [248, 86], 新加坡: [227, 152], 加尔各答: [195, 85], 瓦拉纳西: [180, 76], 卡拉奇: [138, 78], 阿拉伯沙漠: [88, 84], 红海: [56, 75], 阿斯旺: [46, 81], 卢克索: [45, 73], 开罗: [40, 61] };
  FX.CITIES = CITIES;
  const VEH = {
    plane: [`
....kk......
....kwk.....
kk..kwwk....
kwkkkwwwkkk.
kwwwwwwwwwbk
.kkkkwwwkkk.
....kwwk....
....kkk.....`, { k: [30, 24, 40], w: [246, 246, 250], b: [110, 170, 230] }],
    ship: [`
....kk......
....krk.....
..kkkkkkk...
..kwwbwwk...
kkkkkkkkkkkk
krrrrrrrrrrk
.kRRRRRRRRk.
..kkkkkkkk..`, { k: [30, 24, 40], w: [246, 246, 250], b: [110, 170, 230], r: [60, 70, 120], R: [40, 44, 80] }],
    train: [`
.kk.........
.kk..kkkkkk.
kkkkkkbbwbbk
kggggkbbwbbk
kggggggggggk
kGGGGGGGGGGk
.kkk.kk.kkk.
.kwk....kwk.`, { k: [30, 24, 40], g: [70, 150, 90], G: [40, 100, 60], b: [130, 190, 230], w: [240, 240, 240] }],
    car: [`
............
...kkkkk....
..kbbkbbk...
kkkkkkkkkkk.
kyyyyyyyyyyk
kYYYYYYYYYYk
.kkk....kkk.
.kwk....kwk.`, { k: [30, 24, 40], y: [236, 180, 60], Y: [180, 120, 40], b: [130, 190, 230], w: [200, 200, 200] }],
    sub: [`
.....kk.....
....kyyk....
..kkkyykkk..
.kyyyyyyyybk
kyyyykyykyyk
kYYYYYYYYYYk
.kkkkkkkkkk.`, { k: [30, 24, 40], y: [236, 200, 60], Y: [180, 140, 40], b: [130, 190, 230] }],
  };
  VEH.boat = VEH.ship; VEH.heli = VEH.plane;
  const vehCache = new Map();
  function vehIcon(vehicle) {
    let v = vehCache.get(vehicle);
    if (v) return v;
    v = sprPix('prop:map_' + vehicle, 'idle', 0);
    if (!v) { const d = VEH[vehicle] || VEH.plane; v = gridImg(d[0], d[1]); }
    v = { u32: v.u32, w: v.w, h: v.h, ox: v.w / 2, oy: v.h / 2 };
    vehCache.set(vehicle, v);
    return v;
  }
  function stopXY(s, kw) {
    if (Array.isArray(s)) return [+s[0], +s[1]];
    const c = kw.cities && kw.cities[s];
    if (c) return [+c[0], +c[1]];
    const an = G.D && G.D.bg && G.D.bg.world_map && G.D.bg.world_map.anchors;
    const a = an && ((an.cities && an.cities[s]) || an[s]);
    if (a && (Array.isArray(a) || a.x != null)) return Array.isArray(a) ? [+a[0], +a[1]] : [+a.x, +a.y];
    return (CITIES[s] || [160, 90]).slice();
  }
  const routeCache = new Map();
  function routePath(pts, arc) {
    const key = pts.map(p => p.join(',')).join(';') + '|' + arc;
    let r = routeCache.get(key);
    if (r) return r;
    const xs = [pts[0][0]], ys = [pts[0][1]], stopS = [0];
    for (let k = 0; k < pts.length - 1; k++) {
      const [x0, y0] = pts[k], [x1, y1] = pts[k + 1], dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy) || 1;
      let nx = -dy / L, ny = dx / L;
      if (ny > 0 || (Math.abs(ny) < 1e-6 && nx > 0)) { nx = -nx; ny = -ny; }
      const cx = (x0 + x1) / 2 + nx * arc * L, cy = (y0 + y1) / 2 + ny * arc * L, n = Math.max(4, tr(L * 3));
      let seg = 0;
      for (let i = 1; i <= n; i++) {
        const u = i / n, x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1, y = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1;
        seg += Math.hypot(x - xs[xs.length - 1], y - ys[ys.length - 1]);
        xs.push(x); ys.push(y);
      }
      stopS.push(stopS[stopS.length - 1] + seg);
    }
    const s = [0];
    for (let i = 1; i < xs.length; i++) s.push(s[i - 1] + Math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]));
    r = { xs, ys, s, stopS };
    routeCache.set(key, r);
    if (routeCache.size > 32) routeCache.delete(routeCache.keys().next().value);
    return r;
  }
  function dashPts(P, R, sMax, period, on, thick, c, dx, dy) {
    const seen = new Set();
    for (let i = 0; i < R.xs.length; i++) {
      if (R.s[i] > sMax || (R.s[i] % period) >= on) continue;
      const xi = rnd(R.xs[i] - 0.5 * (thick - 1)) + dx, yi = rnd(R.ys[i] - 0.5 * (thick - 1)) + dy;
      for (let ox = 0; ox < thick; ox++) for (let oy = 0; oy < thick; oy++) {
        const k = (xi + ox) * 4096 + yi + oy;
        if (seen.has(k)) continue;
        seen.add(k); px.dot(P, xi + ox, yi + oy, c);
      }
    }
  }
  const MINK = pack(72, 42, 24);
  function cityDot(P, x, y, c, ring, big) {
    const xi = rnd(x), yi = rnd(y);
    if (big) {
      px.box(P, xi - 2, yi - 1, xi + 2, yi + 1, MINK); px.box(P, xi - 1, yi - 2, xi + 1, yi + 2, MINK);
      px.box(P, xi - 1, yi - 1, xi + 1, yi + 1, c); px.dot(P, xi - 1, yi - 1, pack(255, 200, 190));
    } else { px.box(P, xi - 1, yi - 1, xi + 1, yi + 1, MINK); px.dot(P, xi, yi, c); }
    if (ring > 0 && ring < 0.85) { const r = 2 + ring * 7; px.ellipse(P, xi - r, yi - r, xi + r, yi + r, null, c, 1); }
  }
  function tAtS(target, t0, t1, L, kind) {                 // 缓动进度反解：路线走到弧长 target 的时刻
    if (L <= 0) return t0;
    const want = target / L;
    let lo = 0, hi = 1;
    for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; if (ease(m, kind) < want) lo = m; else hi = m; }
    return t0 + (t1 - t0) * hi;
  }
  FX.draw_route = function (P, stops, t, t0, t1, kw) {
    kw = kw || {};
    const colour = col(def(kw.colour, [204, 32, 40])), arc = def(kw.arc, 0.14), kind = def(kw.kind, 'io'), vehicle = def(kw.vehicle, 'plane');
    if (kw.history && kw.history.length) {
      const hl = Array.isArray(kw.history[0]) && typeof kw.history[0][0] !== 'number' ? kw.history : [kw.history];
      for (const hs of hl) {
        if (hs.length < 2) continue;
        const R = routePath(hs.map(s => stopXY(s, kw)), arc);
        dashPts(P, R, R.s[R.s.length - 1] + 1, 4, 2, 1, pack(150, 60, 50), 0, 0);
        for (const nm of hs) { const p = stopXY(nm, kw); cityDot(P, p[0], p[1], pack(170, 90, 70), 0, false); }
      }
    }
    const pts = stops.map(s => stopXY(s, kw));
    if (pts.length < 2) { cityDot(P, pts[0][0], pts[0][1], colour, 0, true); return { pos: pts[0], u: 1, arrived: true, dir: [1, 0] }; }
    const R = routePath(pts, arc), L = R.s[R.s.length - 1], u = ease(prog(t, t0, t1), kind), sNow = u * L;
    dashPts(P, R, sNow, 5, 3, 2, pack(110, 30, 30), 1, 1);
    dashPts(P, R, sNow, 5, 3, 2, colour, 0, 0);
    for (let i = 0; i < pts.length; i++) {
      if (i > 0 && sNow < R.stopS[i] - 0.5) continue;
      const ta = i === 0 ? t0 : tAtS(R.stopS[i], t0, t1, L, kind);
      cityDot(P, pts[i][0], pts[i][1], colour, i > 0 && t < ta + 0.5 ? prog(t, ta, ta + 0.5) : 0, true);
    }
    let j = 1;
    while (j < R.s.length - 1 && R.s[j] < sNow) j++;
    const k0 = Math.max(0, j - 3), k1 = Math.min(R.xs.length - 1, j + 3), dirx = R.xs[k1] - R.xs[k0], diry = R.ys[k1] - R.ys[k0];
    const f = R.s[j] > R.s[j - 1] ? clamp((sNow - R.s[j - 1]) / (R.s[j] - R.s[j - 1])) : 1;
    const vx = R.xs[j - 1] + (R.xs[j] - R.xs[j - 1]) * f, vy = R.ys[j - 1] + (R.ys[j] - R.ys[j - 1]) * f;
    if (def(kw.show_vehicle, true)) {
      const ic = vehIcon(vehicle), moving = u > 0 && u < 1, flip = dirx < 0;
      let bob = moving && (vehicle === 'plane' || vehicle === 'heli') ? rnd(Math.sin(t * 9)) : 0;
      if (vehicle === 'ship' || vehicle === 'boat' || vehicle === 'sub') bob = rnd(Math.sin(t * 5));
      if ((vehicle === 'plane' || vehicle === 'heli') && moving) {      // 地面投影（平滑 110/255）
        const sx = rnd(vx), sy = rnd(vy) + 5, sc = pack(60, 44, 30);
        for (let xx = sx - 3; xx <= sx + 3; xx++) if (xx >= 0 && xx < P.w && sy >= 0 && sy < P.h) px.blendI(P.u32, sy * P.w + xx, cR(sc), cG(sc), cB(sc), 110 / 255);
      }
      if (moving && (vehicle === 'ship' || vehicle === 'boat' || vehicle === 'sub')) {
        const back = flip ? 1 : -1;
        for (let q = 0; q < 3; q++) px.dot(P, rnd(vx + back * (7 + q * 3)), rnd(vy + 3 + (q % 2)), pack(246, 246, 240));
      }
      px.stamp(P, px.variant(ic, 0, 0, ic.w, ic.h, { flip, ax: ic.w / 2, ay: ic.h / 2 }), vx, vy - 2 + bob, 1, 1);
    }
    return { pos: [vx, vy], u, arrived: u >= 1, dir: [dirx, diry] };
  };

  // 替身调查（阿布德尔·生命探测）：n 团小火焰绕身一圈后排成箭头指向 angle（度，0 = 右、90 = 上），停住后熄掉
  // kw = { n: 6, angle: 0, colour: '#ff7a30', dur: 1.2, r: 14 }
  FX.flame_pointer = function (P, x, y, t, t0, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 1.2), dt = t - t0;
    if (dt < 0 || dt >= dur) return;
    const n = def(kw.n, 6), r = def(kw.r, 14), ang = def(kw.angle, 0) * RAD, u = dt / dur, seed = def(kw.seed, 0);
    const ux = Math.cos(ang), uy = -Math.sin(ang), ts = Math.floor(t * 12) / 12;
    const fade = u > 0.82 ? 1 - (u - 0.82) / 0.18 : 1, glowC = col(def(kw.colour, '#ff7a30'));
    // 箭头：杆 4 团 + 两边倒钩（照 n 往后排）
    const tgt = [[6, 0], [11, 0], [16, 0], [22, 0], [17, 5], [17, -5]];
    for (let i = 0; i < n; i++) {
      const orbitA = TAU * i / n + ease(Math.min(1, u / 0.45), 'io') * TAU;
      const ox = x + Math.cos(orbitA) * r, oy = y + Math.sin(orbitA) * r * 0.55;      // 绕身（压扁的圆，像绕着人转）
      const tg = tgt[i % tgt.length], along = tg[0] + Math.floor(i / tgt.length) * 6, side = tg[1];
      const tx = x + ux * along - uy * side, ty = y + uy * along + ux * side;
      const k = ease(clamp((u - 0.45) / 0.25), 'out3');
      const fx_ = lerp(ox, tx, k), fy = lerp(oy, ty, k);
      const flick = 2.2 + 0.7 * Math.sin(ts * 23 + i * 1.9) + (k >= 1 && i % tgt.length === 3 ? 0.8 : 0);
      FX.glow(P, fx_, fy, flick * 2.6, glowC, { alpha: 0.35 * fade });
      FX.fireball(P, fx_, fy - 1, flick, { heat: 0.95, lift: 1, alpha: fade });
      dotA(P, fx_ + (H(seed, i, tr(ts * 12)) - 0.5) * 3, fy - flick - 2 - fmod1(ts * 2 + i * 0.3) * 4, col('#ffd83c'), 0.8 * fade);
    }
  };
  // 替身调查（伊奇·嗅探）：地上一条黄色气味虚线（沿 pts 折线 0.6 s 内铺开、往前流动、最后 40% 渐隐）+ 小缕气味
  // kw = { colour: '#e8c070', dur: 3 }
  FX.scent_line = function (P, pts, t, t0, kw) {
    kw = kw || {};
    const dur = def(kw.dur, 3), dt = t - t0;
    if (dt < 0 || dt >= dur || !pts || pts.length < 2) return;
    const c = col(def(kw.colour, '#e8c070')), lc = light(c, 0.5);
    const fade = dt > dur * 0.6 ? 1 - (dt - dur * 0.6) / (dur * 0.4) : 1;
    let total = 0;
    for (let i = 0; i < pts.length - 1; i++) total += Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]);
    const vis = total * clamp(dt / 0.6), flow = t * 18;
    let s0 = 0;
    for (let i = 0; i < pts.length - 1 && s0 < vis; i++) {
      const a = pts[i], b = pts[i + 1], L = Math.hypot(b[0] - a[0], b[1] - a[1]);
      for (let s = 0; s < L && s0 + s < vis; s += 1) {
        const S = s0 + s, ph = pmod(S - flow, 5);
        if (ph >= 2) continue;
        const x = a[0] + (b[0] - a[0]) * s / L, y = a[1] + (b[1] - a[1]) * s / L;
        dotA(P, x, y, ph < 1 ? lc : c, fade);
      }
      s0 += L;
    }
    const nw = Math.max(1, Math.floor(vis / 24));
    for (let k = 0; k < nw; k++) {                           // 每 24 px 一缕往上飘的气味
      let S = (k + 0.5) * 24, i = 0;
      while (i < pts.length - 2 && S > Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])) { S -= Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]); i++; }
      const a = pts[i], b = pts[i + 1], L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, f = Math.min(1, S / L);
      const bx = a[0] + (b[0] - a[0]) * f, by = a[1] + (b[1] - a[1]) * f, ph = fmod1(t * 0.9 + H(k, 31));
      for (let j = 0; j < 4; j++) dotA(P, bx + Math.sin(ph * 6 + j * 0.9) * 1.5, by - 2 - ph * 10 - j, j < 2 ? c : lc, (1 - ph) * fade * 0.85);
    }
  };

  // 反吸沿骷髅到嘴部的路径收束雾丝，让方向和破解动作在无文字时也能看清。
  FX.inhale_stream = function(P,x,y,t,t0,kw) {
    kw=kw||{};const dt=t-t0,dur=def(kw.dur,1.2);if(dt<0||dt>=dur)return;
    const cx=def(kw.cx,x+80),cy=def(kw.cy,y-35),c=col(def(kw.colour,'#d8c8ff')),lit=light(c,.55);
    const fade=clamp(dt/.12)*clamp((dur-dt)/.2),n=def(kw.n,22),seed=def(kw.seed,0);
    for(let i=0;i<n;i++){
      const u=fmod1(dt*1.8+H(i,seed)),v=1-u;
      const spread=(H(i,seed,7)-.5)*34*v;
      const sx=cx+(x-cx)*u,sy=cy+(y-cy)*u+spread+Math.sin(u*TAU+i)*5*v;
      const tail=Math.max(0,u-.06),tx=cx+(x-cx)*tail,ty=cy+(y-cy)*tail+spread+Math.sin(tail*TAU+i)*5*(1-tail);
      px.line(P,tx,ty,sx,sy,i%3?c:lit,fade*(.35+.65*u));
      dotA(P,sx,sy,lit,fade);
    }
    const rx=3+Math.sin(dt*24);
    px.ellipse(P,x-rx,y-2,x+rx,y+2,lit,null,1,fade*.65);
  };
  // 火焰爆发保留向外扩张的热核、火舌和余烬，区别于持续火柱或普通命中粒子。
  FX.fire_burst = function(P,x,y,t,t0,kw) {
    kw=kw||{};const dt=t-t0,dur=def(kw.dur,.65);if(dt<0||dt>=dur)return;
    const u=dt/dur,size=def(kw.size,20),r=size*(.2+Math.sin(u*Math.PI)*.9),seed=def(kw.seed,0),c=col('#ff9820');
    const fade=clamp((1-u)*1.4);
    for(let i=0;i<10;i++){
      const a=i*TAU/10+H(i,seed)*.4,reach=r*(.7+H(i,seed,2)*.5),bx=x+Math.cos(a)*reach,by=y+Math.sin(a)*reach-u*size*.7;
      px.tri(P,x-Math.sin(a)*r*.3,y+Math.cos(a)*r*.3,x+Math.sin(a)*r*.3,y-Math.cos(a)*r*.3,bx,by,c,fade);
    }
    const cy=y-u*size*.3,core=col('#ffd840'),hot=col('#fffbe0'),ember=col('#ffb820');
    px.ellipse(P,x-r*.55,cy-r*.7,x+r*.55,cy+r*.7,core,null,1,fade);
    px.ellipse(P,x-r*.25,cy-r*.4,x+r*.25,cy+r*.4,hot,null,1,fade);
    for(let i=0;i<18;i++){
      const a=H(i,seed,9)*TAU,dist=size*(.2+u*(1+H(i,seed,4)));
      dotA(P,x+Math.cos(a)*dist,y+Math.sin(a)*dist-u*size,ember,fade);
    }
  };

  // =================================================================== 实例系统 G.fx（技术约定 §4.6.3）
  // 每个函数的位置参数名（不含 P、kw）。't' = 当前时刻；'t0' = 生成时刻；其余从 kw 里按名字取。
  const SIG = {
    shadow: ['x', 'y'], speedlines: ['t'], impact_frame: [], hit_spark: ['x', 'y', 't', 't0'], shockwave: ['x', 'y', 't', 't0'],
    rush: ['x', 'y', 't', 't0', 't1'], afterimage: ['sprite_name', 'positions'], burst: ['x', 'y', 't', 't0'], dust: ['x', 'y', 't', 't0'],
    explosion: ['x', 'y', 't', 't0'], smoke: ['x', 'y', 't', 't0'], fire: ['x', 'y', 't'], fire_ankh: ['x', 'y', 't', 't0'],
    sparkles: ['x', 'y', 't'], glint: ['x', 'y', 't', 't0'], hamon: ['x0', 'y0', 'x1', 'y1', 't'], lightning: ['x0', 'y0', 'x1', 'y1', 't'],
    rain: ['t'], sand_wind: ['t'], petals: ['t'], bubbles: ['t', 'x0', 'y0', 'x1', 'y1'], fog: ['t'], stars: ['t'],
    shooting_star: ['t', 't0', 'x0', 'y0', 'x1', 'y1'], water_splash: ['x', 'y', 't', 't0'], water_gush: ['x', 'y', 't', 't0'],
    emerald_splash: ['x0', 'y0', 'x1', 'y1', 't', 't0', 't1'], gem: ['x', 'y'], tendrils: ['pts', 't'],
    vines: ['x0', 'y0', 'x1', 'y1', 't', 't0', 't1'], wrap: ['x', 'y', 't', 't0'], firerope: ['x', 'y', 't', 't0'],
    void_sphere: ['x', 'y', 'r', 't'], knives: ['items', 't'], timestop_world: [], timestop: ['t', 't0', 'cx', 'cy'],
    time_resume: ['t', 't0', 'cx', 'cy'], clock: ['x', 'y', 'r', 'hour', 'minute'], glow: ['x', 'y', 'r', 'colour'],
    light_beam: ['x0', 'x1', 'top', 'bottom', 't'], vignette: [], heat_haze: ['t', 'y0', 'y1'], underwater_wobble: ['t'],
    caustic_light: ['t'], shatter: ['src', 'x', 'y', 't', 't0'], crack: ['x', 'y', 't', 't0'], iris: ['amount'],
    diamond_wipe: ['amount'], slash_wipe: ['amount'], sepia: [], menace_bg: ['t'], radial_burst_bg: ['t'],
    stand_summon: ['cid', 'logical', 'x', 'y', 't', 't0'], summon_lines: ['x', 'y', 't', 't0'], stand_out: ['cid', 'logical', 'x', 'y', 't', 't0'],
    aura: ['src', 'x', 'y'], sprite: ['src', 'x', 'y'], aura_flame: ['src', 'x', 'y', 't'], aura_wisps: ['x', 'y', 't'],
    bats: ['t', 't0', 'x', 'y'], fireball: ['x', 'y', 'r'], fire_jet: ['x0', 'x1', 'y', 't'], fire_chunks: ['x', 'y', 't', 't0'],
    slash_arc: ['x', 'y', 't', 't0'], dim_bg: ['a'], blade_ext: ['X', 'Y'], coin_on_blade: ['X', 'Y', 'i'], ora_bg: ['t', 'cx', 'cy'],
    cap_shadow: ['x', 'y', 't', 't0'], clash_sparks: ['t', 't0', 't1', 'cx', 'cy'], zone_warn: ['x0', 'y0', 'x1', 'y1', 't', 't0'],
    warn_line: ['pts', 't', 't0'], draw_route: ['stops', 't', 't0', 't1'], flame_pointer: ['x', 'y', 't', 't0'], scent_line: ['pts', 't', 't0'],
    inhale_stream: ['x','y','t','t0'], fire_burst: ['x','y','t','t0'],
  };
  FX._SIG = SIG;
  const XK = new Set(['x', 'x0', 'x1', 'cx', 'X']);           // space 'world' 时减 G.cam.x
  const YK = new Set(['y', 'y0', 'y1', 'cy', 'Y', 'top', 'bottom', 'ground']);
  const PK = new Set(['pts', 'positions', 'items']);         // 点数组：每个点的 [0] / [1] 减镜头
  // 自动寿命（报告 05 §7.4；绝对时间参数已换成相对秒数）
  function autoLife(name, kw) {
    const t1 = kw.t1 == null ? null : kw.t1;
    switch (name) {
      case 'hit_spark': return def(kw.dur, 0.2);
      case 'shockwave': return def(kw.dur, 0.4);
      case 'rush': return (t1 == null ? Infinity : t1) + def(kw.life, 0.3);
      case 'burst': return def(kw.life, 0.6);
      case 'dust': return def(kw.life, 0.75);
      case 'explosion': return 2.2;
      case 'smoke': return t1 != null ? t1 + def(kw.life, 1.6) : (kw.loop ? Infinity : 0.3 + def(kw.life, 1.6));
      case 'fire_ankh': return t1 == null ? Infinity : t1;
      case 'emerald_splash': {
        const L = Math.hypot((kw.x1 || 0) - (kw.x0 || 0), (kw.y1 || 0) - (kw.y0 || 0));
        return (t1 == null ? 0 : t1) + Math.max(0.12, L / def(kw.speed, 320)) + 0.12 + 0.02;
      }
      case 'shatter': return def(kw.dur, 1.2);
      case 'glint': return def(kw.dur, 0.45);
      case 'time_resume': return def(kw.dur, 0.6);
      case 'water_splash': return 1.1;
      case 'water_gush': return t1 == null ? Infinity : t1 + 0.6;
      case 'bats': return def(kw.dur, 2.2);
      case 'fire_chunks': return 0.55;
      case 'slash_arc': return def(kw.dur, 0.1);
      case 'stand_out': return def(kw.dur, 0.25);
      case 'summon_lines': return def(kw.dur, 0.35);
      case 'clash_sparks': return t1 == null ? Infinity : t1 + 0.25;
      case 'shooting_star': return def(kw.dur, 0.6) + 0.2;
      case 'flame_pointer': return def(kw.dur, 1.2);
      case 'scent_line': return def(kw.dur, 3);
      case 'inhale_stream': return def(kw.dur,1.2);
      case 'fire_burst': return def(kw.dur,.65);
      case 'zone_warn': case 'warn_line': return kw.dur == null ? Infinity : kw.dur;
      default: return Infinity;                              // speedlines / fire / vines / tendrils / crack / hamon / menace_bg … 由创建者 kill
    }
  }
  let seq = 0;
  const fx = {
    list: [],
    // spawn(name, kw, o)：kw 里给全部参数（含位置参数）；绝对时间参数 t1 / t_end 写相对秒数
    // o = { clock: 'flow'|'world'|'ui', layer: 'mid'|'over', space: 'world'|'canvas', follow, dx, dy, follow1, dx1, dy1, life, id, tag, by, delay }
    spawn(name, kw = {}, o = {}) {
      if (typeof FX[name] !== 'function') { dbgEv('fx_unknown', { name }); return null; }
      kw = kw || {}; o = o || {};
      let clock = o.clock, layer = o.layer;
      if (o.by && clock == null && layer == null && G.time && G.time.immune && G.time.immune.has && G.time.immune.has(o.by)) { clock = 'world'; layer = 'over'; }
      clock = clock || 'flow';
      const clk = G.clk || { ui: 0, world: 0, flow: 0 };
      const inst = {
        id: o.id != null ? o.id : 'fx' + (++seq), name, kw, o, clock, layer: layer || 'mid', space: o.space || 'world',
        follow: o.follow || null, dx: o.dx || 0, dy: o.dy || 0, follow1: o.follow1 || null, dx1: o.dx1 || 0, dy1: o.dy1 || 0,
        tag: o.tag || null, by: o.by || null, t0: (clk[clock] || 0) + (o.delay || 0), dead: false,
        life: o.life != null ? o.life : autoLife(name, kw), kv: {}, args: [], pointCache: {},
      };
      if (o.id != null) for (const e of this.list) if (e.id === o.id) e.dead = true;   // 同 id 顶替
      this.list.push(inst);
      return inst;
    },
    kill(x) {
      for (const e of this.list) if (e === x || e.id === x) e.dead = true;
    },
    killTag(tag) { for (const e of this.list) if (e.tag === tag) e.dead = true; },
    clear() { this.list.length = 0; },
    has(id) { for (const e of this.list) if (e.id === id && !e.dead) return true; return false; },
    get(id) { for (const e of this.list) if (e.id === id && !e.dead) return e; return null; },
    expired(e) {
      if (e.dead) return true;
      if (e.follow && (e.follow.remove || e.follow.dead && e.o.killWithFollow)) return true;
      const t = (G.clk && G.clk[e.clock]) || 0;
      return t - e.t0 > e.life;
    },
    hasPixel(layer) {
      for (const e of this.list) if (e.layer === layer && !this.expired(e)) return true;
      return false;
    },
    prune() {
      const L = this.list;
      let j = 0;
      for (let i = 0; i < L.length; i++) if (!this.expired(L[i])) L[j++] = L[i];
      L.length = j;
    },
    drawPixel(P, layer) {
      const W = G.world, ins = !!(W && W.insert), cam = G.cam || { x: 0, y: 0 }, L = this.list;
      for (let n = 0; n < L.length; n++) {
        const e = L[n];
        if (e.layer !== layer || this.expired(e)) continue;
        if (ins && e.space === 'world' && e.tag !== 'insert') continue;
        const t = (G.clk && G.clk[e.clock]) || 0;
        if (t < e.t0) continue;
        try { this._call(P, e, t, cam); } catch (err) {
          e.dead = true;
          dbgEv('fx_error', { name: e.name, msg: String(err && err.message || err) });
        }
      }
    },
    _call(P, e, t, cam) {
      const kv = e.kv, kw = e.kw, dt = t - e.t0;
      for (const k in kv) if (!(k in kw)) delete kv[k];
      for (const k in kw) { const v = kw[k]; kv[k] = typeof v === 'function' ? v(dt, e) : v; }
      if (kw.t1 != null && typeof kv.t1 === 'number') kv.t1 = e.t0 + kv.t1;
      if (kw.t_end != null && typeof kv.t_end === 'number') kv.t_end = e.t0 + kv.t_end;
      const sig = SIG[e.name] || EMPTY_SIG;
      if (e.follow) {                                        // 跟随：x = follow.x + dx·facing，y = follow.y − follow.z + dy
        const f = e.follow, fx_ = f.x + e.dx * (f.facing || 1), fy = f.y - (f.z || 0) + e.dy;
        if (sig.indexOf('x') >= 0) { kv.x = fx_; kv.y = fy; }
        else if (sig.indexOf('x0') >= 0) { kv.x0 = fx_; kv.y0 = fy; }
        else { kv.cx = fx_; kv.cy = fy; }
      }
      if (e.follow1) { const f = e.follow1; kv.x1 = f.x + e.dx1 * (f.facing || 1); kv.y1 = f.y - (f.z || 0) + e.dy1; }
      if (e.space === 'world' && (cam.x || cam.y)) {
        const cx = cam.x || 0, cy = cam.y || 0;
        for (const k in kv) {
          const v = kv[k];
          if (typeof v === 'number') { if (XK.has(k)) kv[k] = v - cx; else if (YK.has(k)) kv[k] = v - cy; }
          else if (PK.has(k) && Array.isArray(v)) kv[k] = offsetPoints(v, e.pointCache[k] || (e.pointCache[k] = []), cx, cy);
        }
      }
      const a = e.args;
      a.length = 0;
      a.push(P);
      for (let i = 0; i < sig.length; i++) {
        const p = sig[i];
        if (p === 't') a.push(t);
        else if (p === 't0') a.push(e.t0);
        else if (p === 't1') a.push(kv.t1 == null ? Infinity : kv.t1);
        else a.push(kv[p]);
      }
      a.push(kv);
      return FX[e.name].apply(null, a);
    },

    // 快捷包装（combat.js 用）：命中火花（规划 §3.7 第 4 条）；每击位置 ±3 随机；o.by 照时钟规则
    hit(x, y, level = 'light', o = {}) {
      o = o || {};
      const jx = x + (Math.random() * 2 - 1) * 3, jy = y + (Math.random() * 2 - 1) * 3, acc = o.accent || '#ffd83c';
      const so = { by: o.by, clock: o.clock, layer: o.layer, space: o.space, tag: o.tag };
      const seed = (Math.random() * 1000) | 0, out = [];
      const sp = (n, k) => { const r = this.spawn(n, k, so); if (r) out.push(r); };
      switch (level) {
        case 'heavy':
          sp('hit_spark', { x: jx, y: jy, size: 18, accent: acc, seed });
          sp('shockwave', { x: jx, y: jy, r_max: 40, width: 2, colour: o.ring || '#ffffff' });
          break;
        case 'finisher':
          sp('hit_spark', { x: jx, y: jy, size: 22, accent: acc, dur: 0.3, seed });
          sp('shockwave', { x: jx, y: jy, r_max: 60, width: 3, colour: o.ring || '#ffffff' });
          break;
        case 'guard':
          sp('hit_spark', { x: jx, y: jy, size: 8, colour: '#ffffff', accent: acc, seed });
          sp('shockwave', { x: jx, y: jy, r_max: 18, squash: 1.6, dur: 0.2, colour: acc, width: 2 });
          break;
        case 'parry':
          sp('hit_spark', { x: jx, y: jy, size: 14, colour: '#ffffff', accent: acc, seed });
          sp('shockwave', { x: jx, y: jy, r_max: 18, squash: 1.6, dur: 0.2, colour: '#ffffff', width: 2 });
          sp('glint', { x: jx, y: jy - 2, size: 8 });
          break;
        default:
          sp('hit_spark', { x: jx, y: jy, size: o.size || 10, accent: acc, seed });
      }
      return out;
    },
    dustAt(x, y, o = {}) {
      o = o || {};
      return this.spawn('dust', { x, y, n: 6, speed: 70, colour: o.colour, size: o.size, seed: (Math.random() * 1000) | 0 },
        { by: o.by, clock: o.clock, layer: o.layer, space: o.space, tag: o.tag });
    },

    // 画布版 aura_flame（技术约定 §4.6.2）：→ { canvas, ox, oy } | null；调用方在画精灵之前 drawImage(canvas, x − ox, y − oy)
    // 直接在 Atlas.pix 的数组上算，结果 putImageData 到 G.mkCanvas(w, h, true) 缓存画布；按 (cid, 动作, 帧, 翻转, 缩放, floor(t·12), intensity/0.1 …) 缓存，LRU 64
    // o = { colour, seed: 0, grow: 3, height: 14, intensity: 1, at: [x, y]（可选：给了就按画布坐标对齐 Bayer） }
    _auraLRU: new Map(),
    _auraPool: [],
    auraFlame(cid, logical, frame, flip, scale, t, o = {}) {
      o = o || {};
      const p = sprPix(cid, logical, frame | 0);
      if (!p || !G.mkCanvas) return null;
      const grow = def(o.grow, 3) | 0, K = def(o.height, 14) | 0, sc = scale || 1, inten = Math.round(def(o.intensity, 1) * 10) / 10;
      if (inten <= 0) return null;
      const F = auraFields(p, String(cid) + '|' + logical + '|' + (frame | 0), !!flip, sc, grow, K);
      let bx = 0, by = 0;
      if (o.at) { bx = rnd(o.at[0] - F.ax) & 3; by = rnd(o.at[1] - F.ay) & 3; }
      const key = cid + '|' + logical + '|' + (frame | 0) + '|' + (flip ? 1 : 0) + '|' + sc + '|' + Math.floor(t * def(o.fps, 12)) + '|' + inten + '|' +
        def(o.colour, '#c080ff') + '|' + def(o.seed, 0) + '|' + grow + '|' + K + '|' + bx + by;
      const lru = this._auraLRU;
      let hit = lru.get(key);
      if (hit) { lru.delete(key); lru.set(key, hit); return hit; }
      let cv = null;
      for (let i = 0; i < this._auraPool.length; i++) { const c = this._auraPool[i]; if (c.width === F.w && c.height === F.h) { cv = c; this._auraPool.splice(i, 1); break; } }
      if (!cv) cv = G.mkCanvas(F.w, F.h, true);
      const g = cv.g || cv.getContext('2d', { willReadFrequently: true });
      if (!cv._img) cv._img = g.createImageData(F.w, F.h);
      const u = new Uint32Array(cv._img.data.buffer);
      u.fill(0);
      auraPaint(u, F.w, F.h, F, 0, 0, bx, by, t, { colour: o.colour, seed: o.seed, intensity: inten, fps: o.fps });
      g.putImageData(cv._img, 0, 0);
      hit = { canvas: cv, ox: F.ax, oy: F.ay };
      lru.set(key, hit);
      if (lru.size > 64) { const k0 = lru.keys().next().value, old = lru.get(k0); lru.delete(k0); if (this._auraPool.length < 32) this._auraPool.push(old.canvas); }
      return hit;
    },
  };
  G.fx = fx;
})();
