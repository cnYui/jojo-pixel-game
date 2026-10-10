// 包 2 自测用的桩：按技术约定接口写的最小 G（core / res / atlas / time / world 的一小部分），集成时换成真的
'use strict';
(function () {
  const G = window.G = {};
  G.W = 320; G.H = 180; G.UW = 640; G.UH = 360;
  G.D = window.GAME_DATA;
  G.clk = { ui: 0, world: 0, flow: 0 };
  G.cam = { x: 0, y: 0, zoom: null };
  G.settings = { reduceFlash: false };
  G.shakeLog = [];
  G.shake = (amp, dur) => { G.shakeLog.push([amp, dur]); };
  G.dbg = {
    events: [], counts: {},
    ev(type, data) { this.events.push(Object.assign({ t: G.clk.ui, type }, data || {})); this.counts[type] = (this.counts[type] || 0) + 1; },
    missingImg: new Set(), animFallbacks: new Set(),
  };
  G.mkCanvas = function (w, h, read = false) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    c.g = read ? c.getContext('2d', { willReadFrequently: true }) : c.getContext('2d');
    c.g.imageSmoothingEnabled = false;
    return c;
  };
  const imgs = {};
  G.image = function (key) {
    if (imgs[key]) return imgs[key];
    const src = G.D && G.D.img && G.D.img[key];
    if (!src) { G.dbg.missingImg.add(key); return null; }
    const im = new Image();
    im.src = src;
    imgs[key] = im;
    return im;
  };
  G.ready = im => !!(im && im.complete && im.naturalWidth > 0);
  const pixC = {};
  G.pix = function (key) {
    if (pixC[key]) return pixC[key];
    const im = G.image(key);
    if (!G.ready(im)) return null;
    const c = G.mkCanvas(im.naturalWidth, im.naturalHeight, true);
    c.g.drawImage(im, 0, 0);
    const d = c.g.getImageData(0, 0, c.width, c.height);
    return (pixC[key] = { w: c.width, h: c.height, u32: new Uint32Array(d.data.buffer) });
  };
  G.res = {
    preloadAll() {
      return Promise.all(Object.keys(G.D.img).map(k => { const im = G.image(k); return im.decode().catch(() => null); }));
    },
  };
  // 图集桩：cell / pivot / animations（技术约定 §3.3），只做 pix / has
  function cellPix(img, x0, y0, w, h, ox, oy) {
    const out = new Uint32Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const sx = x0 + x, sy = y0 + y;
      if (sx >= 0 && sy >= 0 && sx < img.w && sy < img.h) out[y * w + x] = img.u32[sy * img.w + sx];
    }
    return { u32: out, w, h, ox, oy };
  }
  const atl = {};
  G.atlas = function (cid) {
    if (atl[cid]) return atl[cid];
    const m = G.D.chars[cid];
    if (!m) { G.dbg.missingImg.add('chars/' + cid); return null; }
    const cache = {};
    const A = {
      resolve(lg) { return m.animations[lg] || m.animations[m.aliases && m.aliases[lg]] || m.animations.idle || m.animations[Object.keys(m.animations)[0]]; },
      has(lg) { return !!(m.animations[lg] || (m.aliases && m.animations[m.aliases[lg]])); },
      pix(lg, f = 0, flip = false) {
        const key = lg + '|' + f + '|' + flip;
        if (cache[key]) return cache[key];
        const p = G.pix(m.image);
        if (!p) return null;
        const a = A.resolve(lg), fr = Math.max(0, Math.min(a.frames - 1, f | 0));
        let v = cellPix(p, fr * m.cell[0], a.row * m.cell[1], m.cell[0], m.cell[1], m.pivot[0], m.pivot[1]);
        if (flip) { const u = new Uint32Array(v.w * v.h); for (let y = 0; y < v.h; y++) for (let x = 0; x < v.w; x++) u[y * v.w + v.w - 1 - x] = v.u32[y * v.w + x]; v = { u32: u, w: v.w, h: v.h, ox: v.w - v.ox, oy: v.oy }; }
        return (cache[key] = v);
      },
    };
    return (atl[cid] = A);
  };
  G.propAtlas = function (id) {
    id = String(id).replace(/^prop:/, '');
    const key0 = 'prop:' + id;
    if (atl[key0]) return atl[key0];
    const m = G.D.props[id];
    if (!m) { G.dbg.missingImg.add('props/' + id); return null; }
    const cache = {};
    const A = {
      has() { return true; },
      pix(lg, f = 0) {
        const fr = Math.max(0, Math.min(m.frames - 1, (typeof lg === 'number' ? lg : f) | 0));
        if (cache[fr]) return cache[fr];
        const p = G.pix(m.image);
        if (!p) return null;
        return (cache[fr] = cellPix(p, fr * m.size[0], 0, m.size[0], m.size[1], m.pivot[0], m.pivot[1]));
      },
    };
    return (atl[key0] = A);
  };
  // 时停桩：visual() 由测试设置 G.time._vis
  G.time = {
    _vis: null, immune: new Set(),
    visual() { return this._vis; },
    flowScale() { return this._vis && (this._vis.phase === 'burst' || this._vis.phase === 'stopped') ? 0 : 1; },
    overActive() { return !!this._vis && this._vis.phase !== 'warn' && this.immune.size > 0; },
  };
  G.world = { insert: null };
  // 测试用：推进时钟（ui 一直走；world 按 worldAdv；flow 按 flowScale）
  G.tick = function (dt, worldAdv = true) {
    G.clk.ui += dt;
    if (worldAdv) { G.clk.world += dt; G.clk.flow += dt * G.time.flowScale(); }
  };
})();
