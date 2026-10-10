// 角色图集绘制（包 4）：逻辑动作名 → 图集真名（amap / 别名 / 通用回退）、翻转 / 缩放 / 旋转 / 染色 / 闪白 / 剪影 / 光环 / 描边 / 逆光 / 抖动透明、道具与场景专用图集、对话头像
'use strict';
(function () {
  const G = window.G;

  // ------------------------------------------------------------------ 通用回退表（技术约定 §3.3）
  G.FALLBACK = {
    run: ['walk'], walk: ['idle'], talk: ['idle'],
    cmd: ['point', 'cast', 'fight', 'attack', 'idle'], cmd2: ['cmd'], cmd_hold: ['cmd', 'pose'],
    guard: ['block', 'cmd', 'idle'],
    dodge: [{ a: 'run', f: 1 }, 'walk', 'idle'],
    hurt: ['shock', 'idle'], getup: ['hurt', 'idle'],
    down: [{ a: 'lie', flip: true }, { a: 'hurt', rot: -90, dy: -8 }, { a: 'idle', rot: -90, dy: -8 }],
    special: ['cast', 'pose', 'cmd'], win: ['pose', 'idle'], pose: ['idle'], shock: ['hurt', 'idle'],
    punch2: ['punch'], punch_heavy: ['upper', { a: 'punch', f: 1 }], rush: ['punch'], block: ['idle'],
    windup: ['ready', 'cmd', 'idle'], attack: ['punch', 'cast', 'thrust', 'shoot', 'cmd'], attack2: ['attack'],
    shoot: ['attack'], fly: ['hurt', 'down'],
  };

  const DEG = Math.PI / 180;
  const BAY = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map((v) => v / 16 + 1 / 32);
  const EMPTY = Object.freeze({});
  const dbgSet = (name, v) => { const d = G.dbg; if (d && d[name] && d[name].add) d[name].add(v); };

  // ------------------------------------------------------------------ 颜色
  const hexCache = new Map();
  function rgbOf(c) {
    if (G.rgbOf) return G.rgbOf(c);
    if (Array.isArray(c)) return c;
    let v = hexCache.get(c);
    if (!v) {
      let h = String(c).replace('#', '');
      if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
      const n = parseInt(h, 16) || 0;
      v = [(n >> 16) & 255, (n >> 8) & 255, n & 255];
      hexCache.set(c, v);
    }
    return v;
  }
  const css = (c) => { const v = rgbOf(c); return 'rgb(' + v[0] + ',' + v[1] + ',' + v[2] + ')'; };
  const colKey = (c) => (Array.isArray(c) ? c.join(',') : String(c));
  const q16 = (v) => Math.max(0, Math.min(16, Math.round(v * 16)));

  // ------------------------------------------------------------------ 派生贴图缓存（LRU，全部图集共用）
  // 抖动透明 / 光环 / 描边 / 逆光描边 这些都在 Atlas.pix() 给的 Uint32Array 上算好，putImageData 到小缓存画布（不“画上去再读回来”）
  const LRU_MAX = 700;
  const lru = new Map();
  const stats = { hit: 0, miss: 0, ditherHit: 0, ditherMiss: 0 };
  function cget(key, dither) {
    const v = lru.get(key);
    if (v) { lru.delete(key); lru.set(key, v); stats.hit++; if (dither) stats.ditherHit++; }
    return v;
  }
  function cput(key, v, dither) {
    stats.miss++; if (dither) stats.ditherMiss++;
    lru.set(key, v);
    if (lru.size > LRU_MAX) lru.delete(lru.keys().next().value);
    return v;
  }
  function toCanvas(u32, w, h) {
    const c = G.mkCanvas(w, h, true);
    const g = c.g || c.getContext('2d');
    const id = g.createImageData(w, h);
    new Uint32Array(id.data.buffer).set(u32);
    g.putImageData(id, 0, 0);
    return c;
  }
  const pack = (r, g, b) => ((0xff000000 | ((b & 255) << 16) | ((g & 255) << 8) | (r & 255)) >>> 0);

  // 掩码工具（m = Uint8Array，1 = 不透明）
  function maskOf(u, n) { const m = new Uint8Array(n); for (let i = 0; i < n; i++) m[i] = u[i] >>> 24 ? 1 : 0; return m; }
  function padded(p, pad) {   // cell 像素 → 四周加 pad 的数组
    const W2 = p.w + 2 * pad, H2 = p.h + 2 * pad, u = new Uint32Array(W2 * H2);
    for (let y = 0; y < p.h; y++) u.set(p.u32.subarray(y * p.w, y * p.w + p.w), (y + pad) * W2 + pad);
    return { u32: u, w: W2, h: H2, ox: p.ox + pad, oy: p.oy + pad };
  }
  function dilate(m, w, h, times) {
    for (let k = 0; k < times; k++) {
      const n = m.slice();
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const i = y * w + x;
        if (m[i]) continue;
        if ((x > 0 && m[i - 1]) || (x < w - 1 && m[i + 1]) || (y > 0 && m[i - w]) || (y < h - 1 && m[i + w])) n[i] = 1;
      }
      m = n;
    }
    return m;
  }
  // 外圈：kind 'out' = 4 邻域外描边（sprite._outline）；'rim' = 只描上、左、右（s00 _rim：右邻 / 左邻 / 下邻在里面的透明像素）
  function outerRing(m, w, h, kind) {
    const r = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = y * w + x;
      if (m[i]) continue;
      const R = x < w - 1 && m[i + 1], L = x > 0 && m[i - 1], D = y < h - 1 && m[i + w], U = y > 0 && m[i - w];
      if (R || L || D || (kind === 'out' && U)) r[i] = 1;
    }
    return r;
  }
  // 内圈：不透明、且上 / 上上 / 左 / 右有透明的像素（逆光的亮边，s18 _backlit 的做法改成照亮上沿）
  function innerRim(m, w, h) {
    const r = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = y * w + x;
      if (!m[i]) continue;
      const U = y > 0 ? m[i - w] : 0, U2 = y > 1 ? m[i - 2 * w] : 0, L = x > 0 ? m[i - 1] : 0, R = x < w - 1 ? m[i + 1] : 0;
      if (!U || !U2 || !L || !R) r[i] = 1;
    }
    return r;
  }
  function mixPx(c, rgb, k) {
    const r = c & 255, g = (c >>> 8) & 255, b = (c >>> 16) & 255;
    return ((c & 0xff000000) | (((b + (rgb[2] - b) * k + 0.5) & 255) << 16) | (((g + (rgb[1] - g) * k + 0.5) & 255) << 8) |
      ((r + (rgb[0] - r) * k + 0.5) & 255)) >>> 0;
  }

  const mk = (name, a, x) => ({
    name, a, f: x && x.f != null ? x.f : null, rot: (x && x.rot) || 0, flip: !!(x && x.flip), dy: (x && x.dy) || 0, fell: false,
  });

  // ------------------------------------------------------------------ Atlas
  class Atlas {
    // type：'char'（角色图集）| 'prop'（道具 / 场景专用的横向帧条）| 'missing'（占位）
    constructor(id, m, type) {
      this.id = id; this.m = m; this.type = type;
      if (type === 'char') {
        this.cw = m.cell[0]; this.ch = m.cell[1]; this.px = m.pivot[0]; this.py = m.pivot[1];
        this.anims = m.animations || {}; this.aliases = m.aliases || {}; this.amap = m.amap || {};
      } else if (type === 'prop') {
        this.cw = m.size[0]; this.ch = m.size[1]; this.px = m.pivot[0]; this.py = m.pivot[1];
        this.anims = { idle: { row: 0, frames: m.frames || 1, fps: m.fps || 0, kind: m.kind || 'static' } };
        this.aliases = {}; this.amap = {};
      } else {
        this.cw = 12; this.ch = 24; this.px = 6; this.py = 24;
        this.anims = { idle: { row: 0, frames: 1, fps: 0, kind: 'static' } }; this.aliases = {}; this.amap = {};
      }
      this.key = (m && m.image) || null;
      this.missing = type === 'missing';
      this._img = null; this._sheet = null; this._res = new Map(); this._cells = new Map(); this._sil = new Map(); this._top = null;
      this._first = Object.keys(this.anims)[0];
    }
    img() { if (!this._img && this.key) this._img = G.image(this.key); return this._img; }
    ready() { const im = this.img(); return !!im && G.ready(im); }

    // ---------------- 动作名解析（§3.3：amap → animations → aliases → G.FALLBACK → idle → 第一个动作）
    _real(name, extra) {
      if (name == null) return null;
      const A = this.anims;
      if (A[name]) return mk(name, A[name], extra);
      const al = this.aliases[name];
      if (al != null && A[al]) return mk(al, A[al], extra);
      return null;
    }
    _try(item) {
      let extra = null, name = item;
      if (item && typeof item === 'object') { extra = item; name = item.a; }
      if (name == null) return null;
      const am = this.amap[name];
      if (am != null) {
        let r = null;
        if (typeof am === 'object') {
          const x = Object.assign({}, am);
          if (extra) for (const k of ['f', 'rot', 'flip', 'dy']) if (extra[k] != null) x[k] = extra[k];
          r = this._real(am.a, x);
        } else r = this._real(am, extra);
        if (r) return r;
      }
      return this._real(name, extra);
    }
    _note(logical, r) {
      if (this.missing) return;
      dbgSet('animFallbacks', this.id + ':' + logical + '→' + r.name + (r.f != null ? '#' + r.f : '') + (r.rot ? '@' + r.rot : '') +
        (r.flip ? '~flip' : ''));
    }
    _resolve(logical, skin) {
      if (typeof logical === 'number' || (typeof logical === 'string' && /^\d+$/.test(logical))) {
        const a = this.anims.idle || this.anims[this._first];
        return mk(this.anims.idle ? 'idle' : this._first, a, { f: +logical });
      }
      let r = null;
      if (skin) { r = this._try(skin + '_' + logical); if (r) return r; }
      r = this._try(logical);
      if (r) return r;
      const fb = G.FALLBACK[logical];
      if (fb) for (const it of fb) { r = this._try(it); if (r) { r.fell = true; this._note(logical, r); return r; } }
      r = this._real('idle') || mk(this._first, this.anims[this._first]);
      r.fell = true;
      this._note(logical, r);
      return r;
    }
    resolve(logical, skin = null) {
      const k = skin ? skin + '\u0001' + logical : logical;
      let r = this._res.get(k);
      if (!r) { r = this._resolve(logical, skin); this._res.set(k, r); }
      return r;
    }
    has(logical, skin = null) {
      if (typeof logical === 'number' || /^\d+$/.test(String(logical))) return this.type === 'prop';
      return !!((skin && this._try(skin + '_' + logical)) || this._try(logical));
    }
    frames(logical, skin = null) { return this.resolve(logical, skin).a.frames; }
    frameAt(logical, t, speed = 1, skin = null) {
      const r = this.resolve(logical, skin), a = r.a;
      if (r.f != null) return Math.max(0, Math.min(a.frames - 1, r.f | 0));
      if (!a.fps || a.kind === 'static' || a.frames <= 1) return 0;
      const n = Math.floor(t * a.fps * speed + 1e-6);
      return a.kind === 'loop' ? ((n % a.frames) + a.frames) % a.frames : Math.max(0, Math.min(n, a.frames - 1));
    }
    done(logical, t, speed = 1, skin = null) {
      const r = this.resolve(logical, skin), a = r.a;
      if (a.kind === 'loop' && r.f == null) return false;
      if (r.f != null) return t * Math.max(1, a.fps || 1) * speed >= 1;
      return t * (a.fps || 1) * speed >= a.frames;
    }
    // idle 第 0 帧最高的不透明像素到 pivot 的距离（元数据里没给 top 时用）
    topPx() {
      if (this._top != null) return this._top;
      if (this.m && this.m.top != null) return (this._top = this.m.top);
      const p = this.pix('idle', 0);
      if (!p) return this.py - 4;
      for (let y = 0; y < p.h; y++) for (let x = 0; x < p.w; x++) if (p.u32[y * p.w + x] >>> 24) return (this._top = p.oy - y);
      return (this._top = this.py - 4);
    }

    // ---------------- 像素（软件贴图、光环 / 抖动计算用）
    sheetPix() {
      if (!this._sheet && this.key && this.ready()) this._sheet = G.pix(this.key);
      return this._sheet;
    }
    _cellPix(row, f, flip) {
      const key = row * 4096 + f * 2 + (flip ? 1 : 0);
      let p = this._cells.get(key);
      if (p) return p;
      const S = this.sheetPix();
      if (!S) return null;
      const w = this.cw, h = this.ch, u = new Uint32Array(w * h), sx = f * w, sy = row * h;
      for (let y = 0; y < h; y++) {
        const yy = sy + y;
        if (yy < 0 || yy >= S.h) continue;
        for (let x = 0; x < w; x++) {
          const xx = sx + x;
          if (xx < 0 || xx >= S.w) continue;
          u[y * w + (flip ? w - 1 - x : x)] = S.u32[yy * S.w + xx];
        }
      }
      p = { u32: u, w, h, ox: flip ? w - this.px : this.px, oy: this.py };
      this._cells.set(key, p);
      return p;
    }
    // 返回这一帧的像素 { u32, w, h, ox, oy }（ox/oy = pivot；resolve 的 flip 已经算进去，旋转不算）
    pix(logical, frame = null, flip = false) {
      if (this.missing) return null;
      const r = this.resolve(logical);
      let f = frame == null ? (r.f == null ? 0 : r.f) : frame | 0;
      f = Math.max(0, Math.min(r.a.frames - 1, f));
      return this._cellPix(r.a.row, f, !!flip !== r.flip);
    }

    // ---------------- 整张图集的纯色剪影（染色 / 闪白 / 剪影用：source-in，不读像素）
    silSheet(color) {
      const k = colKey(color);
      let c = this._sil.get(k);
      if (c) return c;
      const im = this.img();
      if (!G.ready(im)) return null;
      c = G.mkCanvas(im.width, im.height);
      const g = c.g || c.getContext('2d');
      g.drawImage(im, 0, 0);
      g.globalCompositeOperation = 'source-in';
      g.fillStyle = css(color);
      g.fillRect(0, 0, im.width, im.height);
      g.globalCompositeOperation = 'source-over';
      this._sil.set(k, c);
      if (this._sil.size > 12) this._sil.delete(this._sil.keys().next().value);
      return c;
    }

    // ---------------- 贴图辅助
    _blitSheet(g, src, row, f, flip, X, Y, rot, sc, alpha) {
      if (!src || alpha <= 0) return;
      const cw = this.cw, ch = this.ch, sx = f * cw, sy = row * ch;
      const ga = g.globalAlpha;
      g.globalAlpha = ga * Math.min(1, alpha);
      if (!rot && sc === 1 && !flip) g.drawImage(src, sx, sy, cw, ch, X - this.px, Y - this.py, cw, ch);
      else {
        g.save();
        g.translate(X, Y);
        if (rot) g.rotate(rot);
        g.scale(flip ? -sc : sc, sc);
        g.drawImage(src, sx, sy, cw, ch, -this.px, -this.py, cw, ch);
        g.restore();
      }
      g.globalAlpha = ga;
    }
    _blitCanvas(g, d, X, Y, rot, sc, alpha) {
      if (!d || alpha <= 0) return;
      const ga = g.globalAlpha;
      g.globalAlpha = ga * Math.min(1, alpha);
      if (!rot && sc === 1) g.drawImage(d.c, X - d.ox, Y - d.oy);
      else {
        g.save();
        g.translate(X, Y);
        if (rot) g.rotate(rot);
        if (sc !== 1) g.scale(sc, sc);
        g.drawImage(d.c, -d.ox, -d.oy);
        g.restore();
      }
      g.globalAlpha = ga;
    }
    // 光环剪影（sprite.aura：4 邻域膨胀 grow 像素、填光环色）
    _auraCanvas(row, f, flip, grow, color) {
      const key = 'a|' + this.id + '|' + row + ',' + f + ',' + (flip ? 1 : 0) + '|' + grow + '|' + colKey(color);
      let d = cget(key);
      if (d) return d;
      const p0 = this._cellPix(row, f, flip);
      if (!p0) return null;
      const p = padded(p0, grow);
      const m = dilate(maskOf(p.u32, p.w * p.h), p.w, p.h, grow);
      const c = rgbOf(color), col = pack(c[0], c[1], c[2]), u = new Uint32Array(p.w * p.h);
      for (let i = 0; i < u.length; i++) if (m[i]) u[i] = col;
      return cput(key, { c: toCanvas(u, p.w, p.h), ox: p.ox, oy: p.oy });
    }
    _ringCanvas(row, f, flip, color, kind) {
      const key = 'r|' + this.id + '|' + row + ',' + f + ',' + (flip ? 1 : 0) + '|' + kind + '|' + colKey(color);
      let d = cget(key);
      if (d) return d;
      const p0 = this._cellPix(row, f, flip);
      if (!p0) return null;
      const p = kind === 'inner' ? p0 : padded(p0, 1);
      const m = maskOf(p.u32, p.w * p.h);
      const r = kind === 'inner' ? innerRim(m, p.w, p.h) : outerRing(m, p.w, p.h, kind);
      const c = rgbOf(color), col = pack(c[0], c[1], c[2]), u = new Uint32Array(p.w * p.h);
      for (let i = 0; i < u.length; i++) if (r[i]) u[i] = col;
      return cput(key, { c: toCanvas(u, p.w, p.h), ox: p.ox, oy: p.oy });
    }
    // 抖动透明：本体（含染色 / 闪白 / 剪影 / 逆光 / 描边）在数组上算好，再按屏幕对齐的 Bayer 4×4 挖掉；alpha 量化 17 档
    _ditherCanvas(row, f, flip, o, q, X, Y) {
      const p0 = this._cellPix(row, f, flip);
      if (!p0) return null;
      const pad = o.outline || o.rim ? 1 : 0;
      const bx = (X - p0.ox - pad) & 3, by = (Y - p0.oy - pad) & 3;
      const tk = o.tint && o.tint.k > 0 ? colKey(o.tint.color) + '*' + q16(o.tint.k) : '';
      const fk = o.flash > 0 ? q16(o.flash) : 0;
      const bl = o.backlit;
      const blk = bl ? colKey(bl.dark || '#221830') + '*' + q16(bl.k == null ? 0.45 : bl.k) + '*' + (bl.rim ? colKey(bl.rim) : '') : '';
      const key = 'd|' + this.id + '|' + row + ',' + f + ',' + (flip ? 1 : 0) + '|' + bx + by + '|' + q + '|' + tk + '|' + fk + '|' +
        (o.sil ? colKey(o.sil) : '') + '|' + blk + '|' + (o.outline ? colKey(o.outline) : '') + '|' + (o.rim ? colKey(o.rim) : '');
      let d = cget(key, true);
      if (d) return d;
      const p = pad ? padded(p0, 1) : p0, w = p.w, h = p.h, n = w * h;
      const u = new Uint32Array(n);
      u.set(p.u32);
      const m = maskOf(u, n);
      if (o.sil) {
        const c = rgbOf(o.sil), col = pack(c[0], c[1], c[2]);
        for (let i = 0; i < n; i++) if (m[i]) u[i] = col;
      } else {
        if (bl) {
          const dk = rgbOf(bl.dark || '#221830'), k = q16(bl.k == null ? 0.45 : bl.k) / 16;
          for (let i = 0; i < n; i++) if (m[i]) u[i] = mixPx(u[i], dk, k);
          if (bl.rim) { const rr = innerRim(m, w, h), rc = rgbOf(bl.rim); for (let i = 0; i < n; i++) if (rr[i]) u[i] = mixPx(u[i], rc, 0.75); }
        }
        if (tk) { const tc = rgbOf(o.tint.color), k = q16(o.tint.k) / 16; for (let i = 0; i < n; i++) if (m[i]) u[i] = mixPx(u[i], tc, k); }
        if (fk) { const k = fk / 16, wc = [255, 255, 255]; for (let i = 0; i < n; i++) if (m[i]) u[i] = mixPx(u[i], wc, k); }
      }
      if (o.outline) { const r = outerRing(m, w, h, 'out'), c = rgbOf(o.outline), col = pack(c[0], c[1], c[2]); for (let i = 0; i < n; i++) if (r[i]) u[i] = col; }
      if (o.rim) { const r = outerRing(m, w, h, 'rim'), c = rgbOf(o.rim), col = pack(c[0], c[1], c[2]); for (let i = 0; i < n; i++) if (r[i]) u[i] = col; }
      const thr = q / 16;
      for (let y = 0; y < h; y++) {
        const br = ((by + y) & 3) << 2;
        for (let x = 0; x < w; x++) if (!(BAY[br | ((bx + x) & 3)] < thr)) u[y * w + x] = 0;
      }
      d = { c: toCanvas(u, w, h), ox: p.ox, oy: p.oy };
      return cput(key, d, true);
    }

    _drawMissing(g, x, y) {
      const X = Math.round(x), Y = Math.round(y);
      g.fillStyle = '#ff00ff';
      g.fillRect(X - 6, Y - 24, 12, 1); g.fillRect(X - 6, Y - 1, 12, 1);
      g.fillRect(X - 6, Y - 24, 1, 24); g.fillRect(X + 5, Y - 24, 1, 24);
    }

    // (x, y) = 脚点 pivot 在画布上的位置（调用方已减过镜头）；o 见技术约定 §4.8
    draw(g, logical, frame, x, y, o = EMPTY) {
      if (this.missing) { this._drawMissing(g, x, y); return; }
      if (!this.ready()) return;
      let alpha = o.alpha == null ? 1 : o.alpha;
      if (alpha <= 0) return;
      const r = this.resolve(logical, o.skin || null), a = r.a;
      let f = frame == null ? (r.f == null ? 0 : r.f) : frame | 0;
      if (f < 0) f = 0; else if (f >= a.frames) f = a.frames - 1;
      const faceL = !!o.flip, flip = faceL !== r.flip;
      const rot = (r.rot ? (faceL ? -r.rot : r.rot) * DEG : 0) + (o.rot || 0);
      const sc = o.scale || 1;
      const X = Math.round(x), Y = Math.round(y + r.dy * sc);
      const row = a.row;
      if (o.aura) {
        const au = o.aura, grow = au.grow == null ? 1 : au.grow;
        const d = this._auraCanvas(row, f, flip, grow, au.color || '#c080ff');
        let jx = 0, jy = 0;
        if (au.jitter !== false) { const t = au.t || 0; jx = Math.round(Math.sin(t * 23)); jy = Math.round(Math.cos(t * 17)); }
        this._blitCanvas(g, d, X + jx, Y + jy, rot, sc, au.alpha == null ? 0.55 : au.alpha);
      }
      const dth = o.dither;
      if (dth != null && dth < 1) {
        const q = q16(dth);
        if (q <= 0) return;
        this._blitCanvas(g, this._ditherCanvas(row, f, flip, o, q, X, Y), X, Y, rot, sc, alpha);
        return;
      }
      const im = this.img();
      if (o.sil) this._blitSheet(g, this.silSheet(o.sil), row, f, flip, X, Y, rot, sc, alpha);
      else {
        this._blitSheet(g, im, row, f, flip, X, Y, rot, sc, alpha);
        const bl = o.backlit;
        if (bl) {
          this._blitSheet(g, this.silSheet(bl.dark || '#221830'), row, f, flip, X, Y, rot, sc, alpha * (bl.k == null ? 0.45 : bl.k));
          if (bl.rim) this._blitCanvas(g, this._ringCanvas(row, f, flip, bl.rim, 'inner'), X, Y, rot, sc, alpha * 0.75);
        }
        if (o.tint && o.tint.k > 0) this._blitSheet(g, this.silSheet(o.tint.color), row, f, flip, X, Y, rot, sc, alpha * o.tint.k);
        if (o.flash > 0) this._blitSheet(g, this.silSheet('#ffffff'), row, f, flip, X, Y, rot, sc, alpha * o.flash);
      }
      if (o.outline) this._blitCanvas(g, this._ringCanvas(row, f, flip, o.outline, 'out'), X, Y, rot, sc, alpha);
      if (o.rim) this._blitCanvas(g, this._ringCanvas(row, f, flip, o.rim, 'rim'), X, Y, rot, sc, alpha);
    }

    // bg_asia.draw_reflection：只画在 box=[x0,y0,x1,y1]（画布坐标）里；vflip = 水洼倒影（脚在 y、身子往下挂，squash 时压扁到框底）
    drawReflection(g, box, logical, frame, x, y, o = EMPTY) {
      if (this.missing || !this.ready()) return;
      const [x0, y0, x1, y1] = box;
      const dopt = { flip: !!o.flip, scale: o.scale || 1, alpha: o.alpha == null ? 0.9 : o.alpha,
        tint: { color: o.tint || '#96bedc', k: o.amt == null ? 0.35 : o.amt }, skin: o.skin || null };
      g.save();
      g.beginPath();
      g.rect(Math.round(x0), Math.round(y0), Math.round(x1 - x0), Math.round(y1 - y0));
      g.clip();
      if (!o.vflip) this.draw(g, logical, frame, x, y, dopt);
      else {
        const hh = this.py * (o.scale || 1), room = Math.max(2, Math.round(y1) - Math.round(y));
        const sq = o.squash !== false && hh > room ? room / hh : 1;
        g.translate(Math.round(x), Math.round(y));
        g.scale(1, -sq);
        this.draw(g, logical, frame, 0, 0, dopt);
      }
      g.restore();
    }
  }
  Atlas.stats = stats;
  Atlas.cacheSize = () => lru.size;
  Atlas.clearCache = () => { lru.clear(); stats.hit = stats.miss = stats.ditherHit = stats.ditherMiss = 0; };
  G.Atlas = Atlas;

  // ------------------------------------------------------------------ 取图集
  const atlases = new Map();
  const props = new Map();
  let missingAtlas = null;
  const placeholder = () => missingAtlas || (missingAtlas = new Atlas('missing', null, 'missing'));

  // 道具 / 场景专用：'scene:xxx' 取场景专用；'prop:xxx' 或不带前缀取道具（道具里没有再找场景专用）
  G.propAtlas = (id) => {
    let A = props.get(id);
    if (A) return A;
    const D = G.D || {};
    let m = null, key = '';
    if (typeof id === 'string' && id.indexOf('scene:') === 0) { key = id.slice(6); m = D.scene && D.scene[key]; }
    else {
      key = typeof id === 'string' && id.indexOf('prop:') === 0 ? id.slice(5) : String(id);
      m = (D.props && D.props[key]) || (D.scene && D.scene[key]);
    }
    if (m) A = new Atlas(id, m, 'prop');
    else { dbgSet('missingImg', (String(id).indexOf('scene:') === 0 ? 'scene/' : 'props/') + key); A = placeholder(); }
    props.set(id, A);
    return A;
  };
  G.atlas = (cid) => {
    if (typeof cid === 'string' && (cid.indexOf('scene:') === 0 || cid.indexOf('prop:') === 0)) return G.propAtlas(cid);
    let A = atlases.get(cid);
    if (A) return A;
    const m = G.D && G.D.chars && G.D.chars[cid];
    if (m) A = new Atlas(cid, m, 'char');
    else { dbgSet('missingImg', 'chars/' + cid); A = placeholder(); }
    atlases.set(cid, A);
    return A;
  };

  // ------------------------------------------------------------------ 头像（表情三种写法：emotion 名 / 图集 expressions 的 id / 场景专用精灵名）
  function headMeta(cid) {
    const C = (G.D && G.D.chars) || {};
    let m = C[cid];
    if ((!m || !m.heads || !Object.keys(m.heads).length) && typeof cid === 'string' && cid.indexOf('__') > 0) m = C[cid.split('__')[0]] || m;
    return m || null;
  }
  function headEmotion(m, cid, expr) {
    const H = m.heads || {}, keys = Object.keys(H);
    if (!keys.length) return null;
    const e = expr == null ? 'normal' : expr;
    if (H[e]) return e;
    const al = m.headAlias && m.headAlias[e];
    if (al != null && H[al]) return al;
    dbgSet('missingHead', cid + ':' + e);
    return H.normal ? 'normal' : keys[0];
  }
  G.head = (cid, expr = 'normal') => {
    const m = headMeta(cid);
    if (!m) return null;
    const emo = headEmotion(m, cid, expr);
    if (!emo) return null;
    return m.heads[emo].map((k) => G.image(k));
  };
  G.headSize = (cid, expr = 'normal') => {
    const m = headMeta(cid);
    if (!m) return [32, 32];
    const emo = headEmotion(m, cid, expr);
    if (!emo) return [32, 32];
    if (m.headSize && m.headSize[emo]) return m.headSize[emo];
    const im = G.image(m.heads[emo][0]);
    return im && G.ready(im) ? [im.naturalWidth, im.naturalHeight] : [32, 32];
  };
})();
