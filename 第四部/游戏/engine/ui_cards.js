// UI 层的“特效”：名牌 / 替身卡 / 地点卡 / 篇章卡 / 大标题 / 拟声字 / ゴゴゴ / 换队长卡 / VS 卡 / 必杀切入 / 面板 / 坠毁章 /
// 眼部条带 / 念写照片 / 回忆小窗 / To Be Continued（技术约定 §4.10.2；动画照 源码\engine\text.py，VS 照 s10 slam，切入照 s18 portrait_cut）
'use strict';
(function () {
  const G = window.G;
  const task = G.runPromise || (f => new Promise(f));
  const UW = 640, UH = 360, WW = 320, WH = 180;

  // ---------------------------------------------------------------- 小工具
  function ez(u, k = 'io') {
    u = u < 0 ? 0 : u > 1 ? 1 : u;
    switch (k) {
      case 'linear': return u;
      case 'in': return u * u;
      case 'out': return 1 - (1 - u) * (1 - u);
      case 'in3': return u * u * u;
      case 'out3': return 1 - (1 - u) * (1 - u) * (1 - u);
      case 'back': { const s = 1.70158, v = u - 1; return v * v * ((s + 1) * v + s) + 1; }
      default: return u * u * (3 - 2 * u);
    }
  }
  const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
  const lerp = (a, b, u) => a + (b - a) * u;
  const prog = (t, t0, t1) => (t1 <= t0 ? (t >= t1 ? 1 : 0) : clamp01((t - t0) / (t1 - t0)));
  const snd = (name, o) => (name && G.audio && G.audio.sfx ? G.audio.sfx(name, o) : null);
  const UI = () => (G.D && G.D.ui) || {};
  const f16 = () => { if (!G.f16 && G.initFonts) G.initFonts(); return G.f16; };
  const f12 = () => { if (!G.f12 && G.initFonts) G.initFonts(); return G.f12; };
  function hash(...xs) {
    if (G.hash01) return G.hash01(...xs);
    let h = 2166136261;
    for (const x of xs) {
      const v = Number.isInteger(x) ? x : Math.round(x * 997);
      h = Math.imul((h ^ v) >>> 0, 16777619) >>> 0; h = (h ^ (h >>> 13)) >>> 0;
      h = Math.imul(h, 0x5BD1E995) >>> 0; h = (h ^ (h >>> 15)) >>> 0;
    }
    return h / 4294967296;
  }
  const wob = (t, amp, freq, ph = 0) => amp * Math.sin(2 * Math.PI * (freq * t + ph));
  function mix(a, b, k) {
    if (G.mixHex) return G.mixHex(a, b, k);
    const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
    const c = [16, 8, 0].map((s) => Math.round(((pa >> s) & 255) * (1 - k) + ((pb >> s) & 255) * k));
    return '#' + c.map((v) => v.toString(16).padStart(2, '0')).join('');
  }
  function imgOf(meta) {
    if (!meta) return null;
    const im = G.image(meta.image);
    return G.ready(im) ? im : null;
  }
  // 最近邻贴图：o = { alpha, scale, sx, sy（非等比）, rot（度）, anchor: 'c' | 'tl' }
  function blit(g, im, x, y, o = {}) {
    if (!im) return;
    const w = im.naturalWidth || im.width, h = im.naturalHeight || im.height;
    const sx = (o.scale != null ? o.scale : 1) * (o.sx != null ? o.sx : 1);
    const sy = (o.scale != null ? o.scale : 1) * (o.sy != null ? o.sy : 1);
    if (sx <= 0.01 || sy <= 0.01) return;
    g.save();
    g.imageSmoothingEnabled = false;
    if (o.alpha != null) g.globalAlpha *= clamp01(o.alpha);
    const dw = Math.max(1, Math.round(w * sx)), dh = Math.max(1, Math.round(h * sy));
    if (o.rot) {
      g.translate(Math.round(x), Math.round(y));
      g.rotate(o.rot * Math.PI / 180);
      g.drawImage(im, o.anchor === 'tl' ? 0 : -Math.round(dw / 2), o.anchor === 'tl' ? 0 : -Math.round(dh / 2), dw, dh);
    } else if (o.anchor === 'tl') g.drawImage(im, Math.round(x), Math.round(y), dw, dh);
    else g.drawImage(im, Math.round(x - dw / 2), Math.round(y - dh / 2), dw, dh);
    g.restore();
  }
  // 头像（三种表情写法、场景头像名都认）：→ { imgs, w, h } | null
  function headOf(cid, expr) {
    const D = G.D || {};
    if (!G.head) return null;
    if (cid && !(D.chars && D.chars[cid])) {      // 直接给了场景头像名（'s04_kak_evil'）
      for (const k in (D.chars || {})) {
        const c = D.chars[k];
        if (c.headAlias && c.headAlias[cid]) { expr = cid; cid = k; break; }
      }
    }
    if (!cid || !(D.chars && D.chars[cid])) return null;
    const ch = D.chars[cid];
    if (expr && !(ch.heads && (ch.heads[expr] || (ch.headAlias && ch.headAlias[expr])))) expr = null;
    const h = G.head(cid, expr || 'normal');
    if (!h) return null;
    const imgs = (Array.isArray(h) ? h : [h]).filter(Boolean);
    if (!imgs.length) return null;
    const sz = G.headSize ? G.headSize(cid, expr || 'normal') : null;
    return { imgs, w: sz ? sz[0] : imgs[0].naturalWidth || 32, h: sz ? sz[1] : imgs[0].naturalHeight || 32 };
  }
  function hasHead(cid, expr) {
    const c = G.D && G.D.chars && G.D.chars[cid];
    return !!(c && c.heads && (c.heads[expr] || (c.headAlias && c.headAlias[expr] && c.heads[c.headAlias[expr]])));
  }
  // 白色剪影（描边用）缓存
  const silCache = new Map();
  function silhouette(im, color) {
    const key = im.src.length + ':' + im.src.slice(-24) + color;
    let c = silCache.get(key);
    if (c) return c;
    c = G.mkCanvas(im.naturalWidth, im.naturalHeight);
    c.g.drawImage(im, 0, 0);
    c.g.globalCompositeOperation = 'source-in';
    c.g.fillStyle = color; c.g.fillRect(0, 0, c.width, c.height);
    silCache.set(key, c);
    if (silCache.size > 64) silCache.delete(silCache.keys().next().value);
    return c;
  }
  // 头像贴图（帧 f、缩放 s、可带 1 个“世界像素”的描边）
  function drawHead(g, hd, f, x, y, s, o = {}) {
    if (!hd) return;
    const im = hd.imgs[Math.min(f, hd.imgs.length - 1)] || hd.imgs[0];
    if (!G.ready(im)) return;
    g.save();
    g.imageSmoothingEnabled = false;
    if (o.alpha != null) g.globalAlpha *= o.alpha;
    const w = hd.w * s, h = hd.h * s;
    if (o.flip) { g.translate(Math.round(x) + w, Math.round(y)); g.scale(-1, 1); x = 0; y = 0; }
    if (o.outline) {
      const sil = silhouette(im, o.outline), d = o.ow || Math.max(1, Math.round(s / 3));
      for (const [dx, dy] of [[-d, 0], [d, 0], [0, -d], [0, d]]) g.drawImage(sil, 0, 0, hd.w, hd.h, Math.round(x) + dx, Math.round(y) + dy, w, h);
    }
    g.drawImage(im, 0, 0, hd.w, hd.h, Math.round(x), Math.round(y), w, h);
    g.restore();
  }
  // 世界 → UI（G.cam.w2u 返回数组或对象都认）
  function w2u(x, y, z = 0) {
    if (G.cam && G.cam.w2u) {
      const r = G.cam.w2u(x, y, z);
      if (Array.isArray(r)) return { x: r[0], y: r[1] };
      if (r) return { x: r.x, y: r.y };
    }
    const cx = (G.cam && G.cam.x) || 0, cy = (G.cam && G.cam.y) || 0;
    return { x: (x - cx) * 2, y: (y - z - cy) * 2 };
  }
  const isActor = (a) => a && (typeof a.headY === 'function' || (a.cid !== undefined && a.team !== undefined));
  function actorHead(a) {
    const hy = typeof a.headY === 'function' ? a.headY() : a.y - (a.z || 0) - (a.top || 40) * (a.scale || 1);
    return w2u(a.x, hy, 0);
  }
  function fx(name, ...args) {
    const f = G.FX && G.FX[name];
    if (typeof f !== 'function') return false;
    f(...args);
    return true;
  }
  function withPx(g, fn) {
    if (!G.px || G.px.cur) return false;
    const P = G.px.begin(g);
    try { fn(P); } finally { G.px.end(); }
    return true;
  }
  let offA = null, offB = null;
  const offCanvas = () => (offA || (offA = G.mkCanvas(WW, WH, true)));
  const offCanvas2 = () => (offB || (offB = G.mkCanvas(WW, WH, true)));
  function resetCtx(g) {
    g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.imageSmoothingEnabled = false;
  }
  // 斜切（fx.slash_wipe 的几何）：第 y 行的切口 x
  function slashEdge(y, amount, angle = 22) {
    const ta = Math.tan(angle * Math.PI / 180);
    const span = WW + WH * Math.abs(ta) + 8;
    const pos = -WH * Math.abs(ta) - 4 + span * amount;
    return pos - (WH - y) * ta;
  }
  // 插入画面里要把“下面的世界”也画出来（斜切进 / 出时）：临时摘掉 insert 调 world.draw
  function drawWorldUnder(wg) {
    const W = G.world;
    wg.fillStyle = '#000'; wg.fillRect(0, 0, WW, WH);
    if (!W || typeof W.draw !== 'function' || !W.stage) return;
    const ins = W.insert;
    W.insert = null;
    try { W.draw(wg); } finally { W.insert = ins; resetCtx(wg); }
  }
  function setInsert(obj) {
    const W = G.world;
    if (!W) return null;
    obj.prev = W.insert || null;
    obj.t0 = G.clk.ui; obj.clock = 'ui'; obj.uifx = true;
    W.insert = obj;
    return obj;
  }
  function clearInsert(obj) {
    const W = G.world;
    if (W && obj && W.insert === obj) W.insert = obj.prev && obj.prev !== obj ? obj.prev : null;
    if (G.fx && G.fx.killTag) G.fx.killTag('insert');
  }
  function standOf(cid) {
    const D = G.D || {};
    return (D.heroes && D.heroes[cid] && D.heroes[cid].stand) || null;
  }
  function standMeta(id) { return (G.D && G.D.stands && G.D.stands[id]) || null; }
  function atlasOf(cid) {
    if (!cid || !G.atlas) return null;
    if (!(G.D && G.D.chars && G.D.chars[cid])) return null;
    return G.atlas(cid);
  }
  function atlasHas(A, name) { return !!(A && (A.has ? A.has(name) : false)); }
  function atlasFrame(A, name, t) {
    if (!A) return 0;
    if (A.frameAt) return A.frameAt(name, t);
    return 0;
  }
  // 抖动的 4 角小星（UI 像素 ×2）
  function star(g, x, y, s, col) {
    x = Math.round(x); y = Math.round(y);
    g.fillStyle = col;
    g.fillRect(x - s * 2, y, s * 4 + 2, 2); g.fillRect(x, y - s * 2, 2, s * 4 + 2);
    g.fillStyle = '#fff'; g.fillRect(x, y, 2, 2);
  }

  // ================================================================ G.uifx
  const uifx = (G.uifx = {
    cards: [],       // 名牌 / 替身卡 / 地点卡 / 换队长卡
    titles: [],      // 大字
    words: [],       // 拟声字
    menaces: [],     // ゴゴゴ
    panels: [],      // 面板 / 回忆小窗
    misc: [],        // 照片 / 坠毁章 / TBC
    chapter: null,   // 篇章卡（阻塞）
    vsCur: null, cut: null, ecut: null, eye: null,
    tagKey: null, tagT: 0,

    blocking() { return !!this.chapter; },
    clear() {
      if (this.vsCur) clearInsert(this.vsCur.ins);
      if (this.cut) clearInsert(this.cut.ins);
      if (this.eye) clearInsert(this.eye.ins);
      this.cards = []; this.titles = []; this.words = []; this.menaces = []; this.panels = []; this.misc = [];
      this.chapter = null; this.vsCur = null; this.cut = null; this.ecut = null; this.eye = null;
      this.tagKey = null; this.tagT = 0;
    },

    // ------------------------------------------------------------ 名牌 / 替身卡 / 地点卡
    nameCard(cid, o = {}) {
      const m = (UI().namecards || {})[cid];
      if (!m) { if (G.dbg && G.dbg.missingImg) G.dbg.missingImg.add('ui/namecard/' + cid); return; }
      this.cards = this.cards.filter((c) => !(c.kind === 'name'));
      this.cards.push({ kind: 'name', m, t: 0, dur: o.dur || 2.6, x: o.x != null ? o.x : (m.x != null ? m.x : 24), y: o.y != null ? o.y : (m.y != null ? m.y : 264) });
    },
    standCard(id, o = {}) {
      const m = (UI().standcards || {})[id];
      if (!m) { if (G.dbg && G.dbg.missingImg) G.dbg.missingImg.add('ui/standcard/' + id); return; }
      const side = o.side || m.side || 'right';
      this.cards = this.cards.filter((c) => !(c.kind === 'stand' && c.side === side));
      const x = o.x != null ? o.x : (side === 'right' ? UW - m.w - 16 : 16);
      this.cards.push({ kind: 'stand', m, side, t: 0, dur: o.dur || 2.6, x, y: o.y != null ? o.y : (m.y != null ? m.y : 40) });
      if (o.sfx) snd(o.sfx);
    },
    location(key, o = {}) {
      const m = (UI().locations || {})[key];
      if (!m) { if (G.dbg && G.dbg.missingImg) G.dbg.missingImg.add('ui/location/' + key); return; }
      this.cards = this.cards.filter((c) => c.kind !== 'loc');
      // 队伍 ≥ 2 人时左上角有探索头像条（y 6–40）和换队长小卡（y 44–88）：默认位置挪到它们下面（y 92），不再压在头像上
      const y0 = m.y != null ? m.y : 24, crowd = !!(G.party && G.party.members && G.party.members.length >= 2);
      this.cards.push({ kind: 'loc', m, t: 0, dur: o.dur || 3.0, x: o.x != null ? o.x : (m.x != null ? m.x : 24), y: o.y != null ? o.y : (crowd ? Math.max(y0, 92) : y0) });
    },
    leaderCard(actor) {
      if (!actor) return;
      this.cards = this.cards.filter((c) => c.kind !== 'leader');
      this.cards.push({ kind: 'leader', a: actor, t: 0, dur: 0.6 });
    },

    // ------------------------------------------------------------ 篇章卡（阻塞，期间暂停键无效：G.ui.blocking() 为真）
    chapterCard(key, o = {}) {
      return task((res) => {
        const m = (UI().chapters || {})[key];
        if (!m && G.dbg && G.dbg.missingImg) G.dbg.missingImg.add('ui/chapter/' + key);
        this.chapter = { key, m, t: 0, dur: o.dur || 2.8, res };
        if (G.audio && G.audio.cue) G.audio.cue('sting_reveal'); else snd('sting_reveal');
      });
    },

    // ------------------------------------------------------------ 大字（中心对齐，back 弹出）
    title(key, o = {}) {
      return task((res) => {
        const m = (UI().titles || {})[key];
        if (!m && G.dbg && G.dbg.missingImg) G.dbg.missingImg.add('ui/title/' + key);
        const pop = o.pop != null ? o.pop : 0.25, dur = o.dur != null ? o.dur : 1.6;
        this.titles.push({ key, m, t: 0, pop, dur, total: pop + dur + 0.2, x: o.x != null ? o.x : 320, y: o.y != null ? o.y : 180, res, text: o.text || key });
        if (o.sfx) snd(o.sfx);
      });
    },

    // ------------------------------------------------------------ 拟声字：at = Actor（头顶）/ {wx, wy, wz}（世界）/ {x, y}（UI）
    sfx(word, at, o = {}) {
      const m = (UI().sfx || {})[word];
      if (!m && G.dbg && G.dbg.missingImg) G.dbg.missingImg.add('ui/sfx/' + word);
      const w = { word, m, t: 0, dur: o.dur != null ? o.dur : 0.7, pop: o.pop != null ? o.pop : 0.12,
        jitter: o.jitter != null ? o.jitter : 1.5, drift: o.drift || [0, 0], rot: o.rot || 0,
        scale: o.scale != null ? o.scale : (o.size ? o.size / ((m && m.size) || 40) : 1),
        dx: o.dx || 0, dy: o.dy || 0, seed: (this.words.length * 7 + Math.floor(G.clk.ui * 13)) % 997 };
      if (isActor(at)) {
        if (o.follow) w.actor = at;
        else {
          const hy = typeof at.headY === 'function' ? at.headY() : at.y - (at.z || 0) - (at.top || 40);
          w.wx = at.x; w.wy = hy; w.wz = 0;
        }
        w.dy -= 14;
      } else if (at && at.wx != null) { w.wx = at.wx; w.wy = at.wy; w.wz = at.wz || 0; }
      else if (at && at.x != null) { w.ux = at.x; w.uy = at.y; }
      else { w.ux = 320; w.uy = 150; }
      if (Array.isArray(w.drift) === false) w.drift = [w.drift.x || 0, w.drift.y || 0];
      this.words.push(w);
      if (this.words.length > 48) this.words.shift();
      return w;
    },

    // ------------------------------------------------------------ ゴゴゴ（text.menacing 的公式）
    menacing(o = {}) {
      const h = Object.assign({ x: 520, y: 180, char: 'ゴ', n: 4, spread: 90, seed: 0, dur: Infinity }, o, { t: 0, stopT: null });
      h.stop = () => { if (h.stopT == null) h.stopT = h.t; };
      this.menaces.push(h);
      return h;
    },

    // ------------------------------------------------------------ VS 卡（规划 §4.1 = s10 slam）
    vs(o = {}) {
      const key = o.key;
      if (o.attempt > 0 || o.skip) { this.vsTag(key); return Promise.resolve(); }
      return task((res) => {
        const meta = (UI().vs || {})[key] || {};
        const colours = o.colours || meta.colours || ['#5a6a80', '#2a3040'];
        let en = o.enemy;
        if (typeof en === 'string') en = { cid: en };
        en = Object.assign({ anim: 'idle', scale: 3, n: 1 }, en || {});
        const v = { key, meta, colours, hero: o.hero, enemy: en, t: 0, pre: 0.26, res, phase: 'pre', seed: (hash(key ? key.length : 0, 3) * 97) | 0 };
        v.hd = headOf(o.hero, hasHead(o.hero, 'angry') ? 'angry' : 'normal');
        let hit = 0.26;
        if (G.audio && G.audio.cue) { const c = G.audio.cue('sting_reveal', { vol: 0.5 }); if (c && c.hitIn != null) hit = c.hitIn; }
        else snd('sting_reveal', { vol: 0.5 });
        v.pre = Math.min(0.4, Math.max(0.05, hit));
        this.vsCur = v;
      });
    },
    vsTag(key) {
      if (!key) { this.tagKey = null; return; }
      this.tagKey = key; this.tagT = 0;
    },

    // ------------------------------------------------------------ 必杀切入（玩家 0.92 s / 敌人 W6 0.6 s）
    cutin(o = {}) {
      if (o.enemy) return this.enemyCutin(o);
      return task((res) => {
        const cid = o.cid;
        const stand = o.stand || standOf(cid);
        const sm = standMeta(stand) || {};
        const hero = (G.D && G.D.heroes && G.D.heroes[cid]) || {};
        const cols = o.colours || hero.burst || [mix(sm.aura || '#8060ff', '#000000', 0.6), mix(sm.aura || '#8060ff', '#000000', 0.25)];
        const c = { o, cid, stand, sm, cols, t: 0, dur: o.dur || 0.92, res, bg: o.bg || 'radial', title: o.title, seed: (cid || '').length + 5 };
        c.hd = o.portrait === false ? null : headOf(typeof o.portrait === 'string' ? o.portrait : cid, o.expr || (hasHead(cid, 'angry') ? 'angry' : 'normal'));
        c.A = atlasOf(stand);
        c.edge = sm.card || '#ffffff';
        c.ins = setInsert({ draw: (wg) => this.drawCutinWorld(wg, c) });
        if (G.audio && G.audio.cue) G.audio.cue('super_start'); else snd('super_start');
        if (G.audio && G.audio.duck) G.audio.duck(0.4);
        if (this.cut) this.finishCut(this.cut);
        this.cut = c;
      });
    },
    enemyCutin(o) {
      return task((res) => {
        const sm = standMeta(o.stand) || {};
        const base = sm.card || '#e04060';
        const cols = o.colours || [mix(base, '#000000', 0.35), mix(base, '#000000', 0.75)];
        const e = { o, cols, t: 0, dur: o.dur || 0.6, res, title: o.title, seed: 11 };
        e.hd = headOf(o.portrait || o.cid, o.expr);
        snd('sting_shock', { vol: 0.8 });
        if (G.shake) G.shake(3, 0.3);
        if (this.ecut) { const r = this.ecut.res; this.ecut = null; r(); }
        this.ecut = e;
      });
    },

    // ------------------------------------------------------------ 面板（纸巾特写等）
    panel(id, o = {}) {
      const m = (UI().panels || {})[id];
      if (!m && G.dbg && G.dbg.missingImg) G.dbg.missingImg.add('ui/panel/' + id);
      const p = { kind: 'panel', id, m, t: 0, dur: o.dur != null ? o.dur : Infinity, pop: o.pop != null ? o.pop : 0.2, x: o.x, y: o.y, closeT: null, fade: 0.2 };
      p.close = (fade = 0.2) => { if (p.closeT == null) { p.closeT = p.t; p.fade = Math.max(0.01, fade); } };
      this.panels.push(p);
      return p;
    },
    // 回忆小窗（s07 _memory_panel）：红色渐变 + 染黑剪影 + 雨丝 + 闪红眼
    memoryPanel(o = {}) {
      // dur：面板队列按 p.t < p.dur + 0.2 过滤，不写 dur（undefined）时第一帧就被丢掉，回忆小窗从来没显示过；直到 close() 才收
      const p = { kind: 'memory', cid: o.cid || 'jgeil', t: 0, dur: o.dur != null ? o.dur : Infinity, x: o.x != null ? o.x : 16, y: o.y != null ? o.y : 20, closeT: null, fade: 0.2, eyes: o.eyes || null };
      p.close = (fade = 0.2) => { if (p.closeT == null) { p.closeT = p.t; p.fade = Math.max(0.01, fade); } };
      p.base = this.buildMemory(p);
      this.panels.push(p);
      return p;
    },

    // ------------------------------------------------------------ 坠毁章（规划 §2.3）
    crashRecord(from, to, o = {}) {
      return task((res) => {
        this.misc.push({ kind: 'crash', from, to, t: 0, hold: o.hold != null ? o.hold : 2, res, dinged: false });
      });
    },
    // ------------------------------------------------------------ 眼部条带（s18 shot_D）
    eyeStrip(cid, o = {}) {
      return task((res) => {
        const e = { cid, t: 0, dur: o.dur != null ? o.dur : 0.4, word: o.word || null, res, worded: false };
        e.hd = headOf(cid, hasHead(cid, 'angry') ? 'angry' : 'normal');
        e.ins = setInsert({ draw: (wg) => this.drawEyeWorld(wg, e) });
        snd('glint', { vol: 0.7 });
        if (G.shake) G.shake(2, 0.15);
        if (this.eye) { clearInsert(this.eye.ins); this.eye.res(); }
        this.eye = e;
      });
    },
    // ------------------------------------------------------------ 念写照片（规划 §3.1 乔瑟夫）
    photo(o = {}) {
      return task((res) => {
        this.misc = this.misc.filter((m) => m.kind !== 'photo');
        this.misc.push({ kind: 'photo', o, t: 0, hold: o.hold != null ? o.hold : 1.2, res, frames: o.frames || [0, 1, 2] });
        snd('camera_shutter', { vol: 0.8 });
      });
    },
    // ------------------------------------------------------------ To Be Continued（褐色 + 徽章，终音 hit 时正好定格）
    tbc(o = {}) {
      return task((res) => {
        let hit = 1.607;
        if (G.audio && G.audio.cue) { const c = G.audio.cue('tbc'); if (c && c.hitIn != null) hit = c.hitIn; }
        else snd('tbc');
        this.misc = this.misc.filter((m) => m.kind !== 'tbc');
        this.misc.push({ kind: 'tbc', t: 0, hit: Math.max(0.6, hit), hold: o.hold != null ? o.hold : 2.0, res, resolved: false, sepia: -1 });
      });
    },
    tbcOff() { this.misc = this.misc.filter((m) => m.kind !== 'tbc'); },

    // ================================================================ 每帧（ui 时钟）
    update(dt) {
      for (const c of this.cards) c.t += dt;
      this.cards = this.cards.filter((c) => c.t < c.dur);
      if (this.tagKey) this.tagT += dt;
      for (const tt of this.titles) tt.t += dt;
      for (const tt of this.titles) if (tt.t >= tt.total && tt.res) { const r = tt.res; tt.res = null; r(); }
      this.titles = this.titles.filter((tt) => tt.t < tt.total);
      for (const w of this.words) w.t += dt;
      this.words = this.words.filter((w) => w.t < w.dur);
      for (const h of this.menaces) h.t += dt;
      this.menaces = this.menaces.filter((h) => (h.stopT == null || h.t - h.stopT < 0.2) && h.t < h.dur + 0.2);
      for (const p of this.panels) p.t += dt;
      this.panels = this.panels.filter((p) => (p.closeT == null || p.t - p.closeT < p.fade) && p.t < p.dur + 0.2);
      if (this.chapter) {
        const c = this.chapter;
        c.t += dt;
        if (c.t >= c.dur) { this.chapter = null; c.res(); }
      }
      this.updateVs(dt);
      if (this.cut) { this.cut.t += dt; if (this.cut.t >= this.cut.dur) this.finishCut(this.cut); }
      if (this.ecut) { const e = this.ecut; e.t += dt; if (e.t >= e.dur) { this.ecut = null; e.res(); } }
      if (this.eye) {
        const e = this.eye;
        e.t += dt;
        if (e.word && !e.worded && e.t >= 0.05) { e.worded = true; this.sfx(e.word, { x: 520, y: 176 }, { rot: -6, dur: Math.max(0.3, e.dur) }); }
        if (e.t >= e.dur) { this.eye = null; clearInsert(e.ins); e.res(); }
      }
      for (const m of this.misc) this.updateMisc(m, dt);
      this.misc = this.misc.filter((m) => !m.dead);
    },
    finishCut(c) {
      clearInsert(c.ins);
      if (this.cut === c) this.cut = null;
      c.res();
    },
    updateVs(dt) {
      const v = this.vsCur;
      if (!v) return;
      v.t += dt;
      const u = v.t - v.pre;            // 冲击开始后的秒数
      if (v.phase === 'pre') {
        if (!v.whoosh && v.t >= v.pre - 0.12) { v.whoosh = true; snd('whoosh', { vol: 0.45 }); }
        if (u >= 0) {
          v.phase = 'slam';
          v.ins = setInsert({ draw: (wg) => this.drawVsWorld(wg, v) });
          snd('punch', { vol: 0.75, seed: 0 });
          if (G.flash) G.flash(0.06, 0.5);
          if (G.shake) G.shake(4, 0.25);
        }
      } else if (v.phase === 'slam' && u >= 0.93) {
        v.phase = 'exit';
        clearInsert(v.ins);
        this.vsTag(v.key);
        const r = v.res; v.res = null; r();
      } else if (v.phase === 'exit' && u >= 0.93 + 0.12) {
        this.vsCur = null;
      }
    },
    updateMisc(m, dt) {
      m.t += dt;
      if (m.kind === 'crash') {
        if (!m.dinged && m.t >= 0.35) { m.dinged = true; snd('ding', { vol: 0.8 }); snd('pop', { vol: 0.6 }); }
        if (m.t >= 0.47 + m.hold + 0.2) { m.dead = true; m.res(); }
      } else if (m.kind === 'photo') {
        if (!m.devSnd && m.t >= 1.05) { m.devSnd = true; snd('sparkle', { vol: 0.5 }); }
        if (m.t >= 0.25 + 0.8 + m.hold + 0.2) { m.dead = true; m.res(); }
      } else if (m.kind === 'tbc') {
        const s0 = m.hit - 0.6;
        const a = clamp01((m.t - s0) / 0.2);
        if (G.post && G.post.filter && a > 0 && a !== m.sepia) { m.sepia = a; G.post.filter('sepia', a); }
        if (!m.frozen && m.t >= m.hit) { m.frozen = true; if (G.shake) G.shake(1.5, 0.12); }
        if (!m.resolved && m.t >= m.hit + m.hold) { m.resolved = true; m.res(); }
      }
    },

    // ================================================================ 画（G.ui.draw 里，HUD 之上、提示 / 对话之下）
    draw(g) {
      g.imageSmoothingEnabled = false;
      this.drawTag(g);
      for (const c of this.cards) this.drawCardItem(g, c);
      for (const h of this.menaces) this.drawMenace(g, h);
      for (const w of this.words) this.drawWord(g, w);
      for (const p of this.panels) (p.kind === 'memory' ? this.drawMemory(g, p) : this.drawPanel(g, p));
      for (const m of this.misc) this.drawMisc(g, m);
      for (const tt of this.titles) this.drawTitle(g, tt);
      if (this.ecut) this.drawEnemyCut(g, this.ecut);
      if (this.vsCur) this.drawVsUI(g, this.vsCur);
      if (this.cut) this.drawCutUI(g, this.cut);
    },
    drawCard(g) {
      const c = this.chapter;
      if (!c) return;
      const a = clamp01(Math.min(c.t / 0.35, (c.dur - c.t) / 0.35));
      g.save();
      g.globalAlpha = a;
      const im = imgOf(c.m);
      if (im) g.drawImage(im, 0, 0, UW, UH);
      else {      // 缺图兜底：黑底 + 宋体字
        g.fillStyle = '#140820'; g.fillRect(0, 0, UW, UH);
        const ch = (G.D && G.D.chapters) || null;
        f16().draw(g, c.key, UW / 2, UH / 2 - 8, '#ffe040', { align: 'center', outline: '#000' });
        void ch;
      }
      g.restore();
    },

    drawTag(g) {
      if (!this.tagKey) return;
      const v = (UI().vs || {})[this.tagKey];
      const im = v && imgOf(v.tag);
      if (!im) return;
      const k = ez(clamp01(this.tagT / 0.16), 'out3');
      g.drawImage(im, Math.round(lerp(-v.tag.w - 4, 8, k)), 8);
    },
    drawCardItem(g, c) {
      if (c.kind === 'leader') { this.drawLeader(g, c); return; }
      const im = imgOf(c.m);
      if (!im) return;
      let slide, fadeT, off;
      if (c.kind === 'loc') { slide = ez(prog(c.t, 0, 0.35), 'out3'); fadeT = 0.3; off = Math.round((1 - slide) * -300); }
      else if (c.kind === 'stand') { slide = ez(prog(c.t, 0, 0.3), 'out3'); fadeT = 0.25; off = Math.round((1 - slide) * (c.m.w + 40)) * (c.side === 'right' ? 1 : -1); }
      else { slide = ez(prog(c.t, 0, 0.3), 'out3'); fadeT = 0.25; off = Math.round((1 - slide) * -200); }
      const a = clamp01((c.dur - c.t) / fadeT);
      g.save();
      g.globalAlpha = a;
      g.drawImage(im, c.x + off, c.y);
      g.restore();
    },
    // 换队长：左上（队伍头像条下面）弹一张斜角小卡：头像 + 名字 + 『替身名』
    drawLeader(g, c) {
      const a = c.a, D = G.D || {};
      const cid = a.cid;
      const hero = (D.heroes && D.heroes[cid]) || {};
      const sid = a.standId || hero.stand;
      const sm = standMeta(sid) || {};
      const col = sm.aura || '#ffd83c';
      const name = (G.NAMES && G.NAMES[cid]) || hero.short || a.name || cid;
      const k = ez(prog(c.t, 0, 0.1), 'out3');
      const alpha = clamp01((c.dur - c.t) / 0.15);
      const x = Math.round(lerp(-240, 8, k)), y = 44;
      const F = f16(), w = Math.max(F.width(name), f12().width('『' + (sm.cn || '') + '』')) + 70;
      g.save();
      g.globalAlpha = alpha;
      g.fillStyle = 'rgba(0,0,0,0.55)';
      g.beginPath(); g.moveTo(x + 4, y + 4); g.lineTo(x + w + 4, y + 4); g.lineTo(x + w - 8, y + 44); g.lineTo(x - 8, y + 44); g.fill();
      g.fillStyle = '#140a28';
      g.beginPath(); g.moveTo(x + 10, y); g.lineTo(x + w, y); g.lineTo(x + w - 12, y + 40); g.lineTo(x - 2, y + 40); g.fill();
      g.fillStyle = col; g.fillRect(x + 6, y, w - 6, 2); g.fillRect(x - 2, y + 38, w - 10, 2);
      const hd = headOf(cid, 'normal');
      if (hd) { g.save(); g.beginPath(); g.rect(x + 8, y + 4, 32, 32); g.clip(); drawHead(g, hd, 0, x + 8, y + 4, 1); g.restore(); }
      F.draw(g, name, x + 48, y + 4, '#fff', { outline: '#000' });
      f12().draw(g, '『' + (sm.cn || '') + '』', x + 46, y + 23, col, { outline: '#000' });
      if (c.t < 0.12) { g.globalAlpha = (0.12 - c.t) / 0.12 * 0.7; g.fillStyle = '#fff'; g.fillRect(x - 2, y, w, 40); }
      g.restore();
    },
    drawMenace(g, h) {
      const m = (UI().menace || {})[h.char];
      const im = imgOf(m);
      let x0 = h.x, y0 = h.y;
      if (h.actor) { const p = actorHead(h.actor); x0 = p.x + (h.dx != null ? h.dx : 56); y0 = p.y + (h.dy != null ? h.dy : 30); }
      const t = h.t, n = h.n;
      const endA = h.stopT != null ? clamp01(1 - (t - h.stopT) / 0.2) : (h.dur !== Infinity ? clamp01((h.dur + 0.2 - t) / 0.2) : 1);
      for (let i = 0; i < n; i++) {
        const ph = hash(h.seed, i);
        const appear = i * 0.12;
        if (t < appear) continue;
        const u = ((t - appear) * 0.35 + ph) % 1;
        const xx = x0 + (i - (n - 1) / 2) * h.spread / Math.max(1, n - 1) * 1.6 + Math.sin((t + ph) * 5) * 3;
        const yy = y0 + (0.5 - u) * 60 + (i % 2) * 18;
        const a = Math.min(1, prog(t, appear, appear + 0.15)) * (1 - Math.max(0, (u - 0.8) / 0.2)) * endA;
        const sc = (1 + 0.08 * Math.sin((t + ph) * 11)) * (h.scale || 1);
        if (im) blit(g, im, xx, yy, { alpha: a, scale: sc, rot: -(-8 + 16 * ph) });
        else f16().draw(g, h.char, xx, yy - 8, '#aa3cdc', { align: 'center', outline: '#1a0022' });
      }
    },
    drawWord(g, w) {
      let p;
      if (w.actor) { p = actorHead(w.actor); }
      else if (w.wx != null) p = w2u(w.wx, w.wy, w.wz);
      else p = { x: w.ux, y: w.uy };
      const u = prog(w.t, 0, w.pop);
      const sc = (w.pop ? 1.6 - 0.6 * ez(u, 'out') : 1) * w.scale;
      const k = Math.floor(G.clk.ui * 24);
      const jx = (hash(k, w.seed, 1) * 2 - 1) * w.jitter, jy = (hash(k, w.seed, 2) * 2 - 1) * w.jitter;
      const a = clamp01((w.dur - w.t) / 0.12);
      const x = p.x + w.dx + jx + w.drift[0] * w.t, y = p.y + w.dy + jy + w.drift[1] * w.t;
      const im = imgOf(w.m);
      if (im) blit(g, im, x, y, { alpha: a, scale: sc, rot: -w.rot });
      else {
        const b = f16().bake(w.word, '#fff', { outline: '#000' });
        blit(g, b, x, y, { alpha: a, scale: 2 * sc, rot: -w.rot });
      }
    },
    drawTitle(g, tt) {
      const sc = tt.pop ? ez(prog(tt.t, 0, tt.pop), 'back') : 1;
      if (sc <= 0.02) return;
      const a = clamp01((tt.total - tt.t) / 0.2);
      const im = imgOf(tt.m);
      if (im) blit(g, im, tt.x, tt.y, { alpha: a, scale: Math.max(0.05, sc) });
      else blit(g, f16().bake(tt.text, '#ffe040', { outline: '#2a0a3a' }), tt.x, tt.y, { alpha: a, scale: 3 * Math.max(0.05, sc) });
    },
    drawPanel(g, p) {
      const im = imgOf(p.m);
      if (!im) return;
      const w = p.m.w || im.naturalWidth, h = p.m.h || im.naturalHeight;
      const x = p.x != null ? p.x : Math.round((UW - w) / 2), y = p.y != null ? p.y : Math.round((UH - h) / 2);
      const sc = p.pop ? ez(prog(p.t, 0, p.pop), 'back') : 1;
      let a = Math.min(1, p.t / 0.08);
      if (p.closeT != null) a *= clamp01(1 - (p.t - p.closeT) / p.fade);
      if (p.dur !== Infinity) a *= clamp01((p.dur + 0.2 - p.t) / 0.2);
      blit(g, im, x + w / 2, y + h / 2, { alpha: a, scale: Math.max(0.05, sc) });
    },

    // ------------------------------------------------------------ 回忆小窗
    buildMemory(p) {
      const pw = 118, ph = 84, sk = 12;
      const c = G.mkCanvas(pw, ph, true);
      const id = c.g.createImageData(pw, ph);
      const stops = [[26, 6, 16], [90, 12, 28], [160, 24, 40], [58, 6, 16]];
      const BAY = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map((v) => v / 16 + 1 / 32);
      const bands = 8;
      const mask = new Uint8Array(pw * ph);
      for (let y = 0; y < ph; y++) {
        const q = ((y + 0.5) / ph) * (bands - 1);
        const b = Math.floor(q) + ((q - Math.floor(q)) > BAY[((y & 3) << 2)] ? 1 : 0);
        const uu = Math.min(1, b / (bands - 1)) * (stops.length - 1);
        const i0 = Math.min(stops.length - 2, Math.floor(uu)), f = uu - i0;
        const col = [0, 1, 2].map((k) => Math.round(stops[i0][k] * (1 - f) + stops[i0 + 1][k] * f));
        const xl = sk * (1 - y / (ph - 1)), xr = pw - 1 - sk * (y / (ph - 1));
        for (let x = 0; x < pw; x++) {
          if (x < xl || x > xr) continue;
          const i = (y * pw + x) * 4;
          id.data[i] = col[0]; id.data[i + 1] = col[1]; id.data[i + 2] = col[2]; id.data[i + 3] = 255;
          mask[y * pw + x] = 1;
        }
      }
      // 剪影：本体 idle 第 0 帧染成 (20,4,8)，肤色（头以下）留成粉色（原片 J·凯尔举起的两只右手）
      const A = atlasOf(p.cid);
      let sp = null;
      if (A && A.pix) sp = A.pix('idle', 0, false);
      if (sp && sp.u32) {
        const ox = Math.round(pw / 2 - sp.ox + 4), oy = Math.round(ph - 2 - sp.oy);
        for (let yy = 0; yy < sp.h; yy++) {
          for (let xx = 0; xx < sp.w; xx++) {
            const v = sp.u32[yy * sp.w + xx];
            const al = v >>> 24;
            if (!al) continue;
            const X = ox + xx, Y = oy + yy;
            if (X < 0 || Y < 0 || X >= pw || Y >= ph || !mask[Y * pw + X]) continue;
            const r = v & 255, gg = (v >>> 8) & 255, b = (v >>> 16) & 255;
            const skin = yy >= 19 && r > 200 && gg > 150 && b < 170;
            const i = (Y * pw + X) * 4;
            id.data[i] = skin ? 236 : 20; id.data[i + 1] = skin ? 120 : 4; id.data[i + 2] = skin ? 132 : 8;
          }
        }
        p.eyeY = p.eyes ? null : Math.max(4, oy + Math.round(sp.oy - ((G.D.chars[p.cid] && G.D.chars[p.cid].top) || 40)) + 9);
      }
      // 白描边
      const put = (x, y) => { if (x >= 0 && y >= 0 && x < pw && y < ph) { const i = (y * pw + x) * 4; id.data[i] = id.data[i + 1] = id.data[i + 2] = id.data[i + 3] = 255; } };
      for (let x = sk; x < pw; x++) put(x, 0);
      for (let x = 0; x < pw - sk; x++) put(x, ph - 1);
      for (let y = 0; y < ph; y++) { put(Math.round(sk * (1 - y / (ph - 1))), y); put(Math.round(pw - 1 - sk * (y / (ph - 1))), y); }
      c.g.putImageData(id, 0, 0);
      p.mask = mask; p.pw = pw; p.ph = ph;
      return c;
    },
    drawMemory(g, p) {
      const u = prog(p.t, 0, 0.25);
      let a = u;
      if (p.closeT != null) a *= clamp01(1 - (p.t - p.closeT) / p.fade);
      if (a <= 0) return;
      const slide = ez(u, 'out3');
      const x = p.x - Math.round((1 - slide) * 60), y = p.y;
      g.save();
      g.globalAlpha = a;
      g.drawImage(p.base, 0, 0, p.pw, p.ph, x, y, p.pw * 2, p.ph * 2);
      // 雨丝（只画在平行四边形里）
      const k = Math.floor(p.t * 14);
      g.fillStyle = 'rgb(200,120,140)';
      for (let i = 0; i < 26; i++) {
        const rx = (hash(i, 5) * (p.pw + 30) + k * 7) % (p.pw + 30) - 15;
        const ry = (hash(i, 6) * p.ph + k * 13 * (0.8 + 0.4 * hash(i, 7))) % p.ph;
        for (let s = 0; s < 5; s++) {
          const px = Math.floor(rx - s * 0.4), py = Math.floor(ry + s);
          if (px >= 0 && py >= 0 && px < p.pw && py < p.ph && p.mask[py * p.pw + px]) g.fillRect(x + px * 2, y + py * 2, 2, 2);
        }
      }
      if (Math.floor(p.t * 5) % 3) {
        g.fillStyle = 'rgb(255,60,60)';
        const eyes = p.eyes || [[p.pw / 2 + 6, p.eyeY != null ? p.eyeY : p.ph - 44], [p.pw / 2 + 9, p.eyeY != null ? p.eyeY : p.ph - 44]];
        for (const [ex, ey] of eyes) g.fillRect(x + Math.round(ex) * 2, y + Math.round(ey) * 2, 2, 2);
      }
      g.restore();
    },

    // ------------------------------------------------------------ 坠毁章 / 照片 / TBC
    drawMisc(g, m) {
      if (m.kind === 'crash') this.drawCrash(g, m);
      else if (m.kind === 'photo') this.drawPhoto(g, m);
      else if (m.kind === 'tbc') this.drawTbc(g, m);
    },
    drawCrash(g, m) {
      const cr = UI().crash;
      if (!cr || !cr.plate) return;
      const pim = imgOf(cr.plate);
      if (!pim) return;
      const pw = cr.plate.w, ph = cr.plate.h;
      const xs = UW - pw - 18, ys = UH - ph - 18;
      const k = ez(prog(m.t, 0, 0.2), 'out3');
      const fadeA = clamp01((0.47 + m.hold + 0.2 - m.t) / 0.2);
      const x = Math.round(lerp(UW + 8, xs, k)), y = ys;
      g.save();
      g.globalAlpha = fadeA;
      g.drawImage(pim, x, y);
      const slot = cr.plate.slot || [pw - (cr.dw || 24) - 14, Math.round((ph - (cr.dh || 26)) / 2), cr.dw || 24, cr.dh || 26];
      const sx = x + slot[0], sy = y + slot[1], sw = slot[2], sh = slot[3];
      const dig = (n) => { const key = (cr.digits || [])[n]; return key ? G.image(key) : null; };
      const oldIm = dig(m.from), newIm = dig(m.to);
      if (m.t < 0.47) {
        if (oldIm && G.ready(oldIm)) g.drawImage(oldIm, sx, sy);
        if (m.t >= 0.2) {         // 红线划掉（0.15 s）
          const u = prog(m.t, 0.2, 0.35);
          g.fillStyle = '#e02030';
          const L = Math.round((sw + 6) * u);
          for (let i = 0; i < L; i++) g.fillRect(sx - 3 + i, sy + sh - 4 - Math.round(i * (sh - 8) / (sw + 6)), 2, 2);
        }
      }
      if (m.t >= 0.35 && newIm && G.ready(newIm)) {   // 新数字从 1.8 倍砸下
        const u = prog(m.t, 0.35, 0.47);
        const sc = 1.8 - 0.8 * ez(u, 'out');
        blit(g, newIm, sx + sw / 2, sy + sh / 2 + Math.round((1 - u) * -10), { scale: sc, alpha: Math.min(1, u * 3) });
        if (m.t < 0.55) { g.globalAlpha = fadeA * (1 - prog(m.t, 0.47, 0.55)); g.fillStyle = '#fff'; g.fillRect(sx - 2, sy - 2, sw + 4, sh + 4); }
      }
      g.restore();
    },
    drawPhoto(g, m) {
      const o = m.o, D = G.D || {};
      let im = null, fw = 16, fh = 20, frame = 0, nfr = 1;
      if (o.image) { im = G.image(o.image); if (G.ready(im)) { fw = im.naturalWidth; fh = im.naturalHeight; } }
      else {
        const pm = D.props && D.props.photo;
        if (pm) { im = G.image(pm.image); fw = pm.size[0]; fh = pm.size[1]; nfr = pm.frames || 1; }
      }
      const dev = m.t - 0.25;
      const fi = dev < 0.4 ? 0 : dev < 0.8 ? 1 : 2;
      frame = Math.min(nfr - 1, m.frames[Math.min(m.frames.length - 1, fi)] || 0);
      const sc = Math.max(1, Math.floor(Math.min(120 / fw, 140 / fh)));
      const pwid = fw * sc, phei = fh * sc, bx = 10, btop = 10, bbot = 30;
      const W2 = pwid + bx * 2, H2 = phei + btop + bbot;
      const k = ez(prog(m.t, 0, 0.25), 'out3');
      const fade = clamp01((0.25 + 0.8 + m.hold + 0.2 - m.t) / 0.2);
      const cx = UW / 2, cy = lerp(UH + H2, UH / 2 - 6, k);
      const rot = lerp(-14, -3, k);
      g.save();
      g.globalAlpha = fade;
      g.translate(Math.round(cx), Math.round(cy));
      g.rotate(rot * Math.PI / 180);
      g.imageSmoothingEnabled = false;
      g.fillStyle = 'rgba(0,0,0,0.45)'; g.fillRect(-W2 / 2 + 6, -H2 / 2 + 6, W2, H2);
      g.fillStyle = '#f4f0e6'; g.fillRect(-W2 / 2, -H2 / 2, W2, H2);
      g.fillStyle = '#d8d0c0'; g.fillRect(-W2 / 2, H2 / 2 - 2, W2, 2);
      const px0 = -W2 / 2 + bx, py0 = -H2 / 2 + btop;
      g.fillStyle = '#201828'; g.fillRect(px0, py0, pwid, phei);
      if (G.ready(im)) g.drawImage(im, o.image ? 0 : frame * fw, 0, fw, fh, px0, py0, pwid, phei);
      if (dev >= 0.8 && o.arrow && Math.floor(G.clk.ui * 4) % 4 !== 3) {    // 红箭头（照片像素坐标，angle 度：0 右、90 上）
        const ax = px0 + o.arrow.x * sc, ay = py0 + o.arrow.y * sc, ang = -(o.arrow.angle || 0) * Math.PI / 180;
        const L = 26, ca = Math.cos(ang), sa = Math.sin(ang);
        const tip = [ax, ay], tail = [ax - ca * L, ay - sa * L];
        for (const [col, wd] of [['#2a0008', 7], ['#ff3040', 4]]) {
          g.fillStyle = col;
          const n = 24;
          for (let i = 0; i <= n; i++) {
            const xx = lerp(tail[0], tip[0] - ca * 8, i / n), yy = lerp(tail[1], tip[1] - sa * 8, i / n);
            g.fillRect(Math.round(xx - wd / 2), Math.round(yy - wd / 2), wd, wd);
          }
          for (let r = 0; r < 12; r++) {
            const hx = tip[0] - ca * r, hy = tip[1] - sa * r, hw = r * 0.75 + wd / 2 - 2;
            g.fillRect(Math.round(hx - sa * hw - 1), Math.round(hy + ca * hw - 1), 3, 3);
            g.fillRect(Math.round(hx + sa * hw - 1), Math.round(hy - ca * hw - 1), 3, 3);
            g.fillRect(Math.round(hx - 1), Math.round(hy - 1), 3, 3);
          }
        }
      }
      if (dev >= 0.8 && dev < 0.95) { g.globalAlpha = fade * (1 - (dev - 0.8) / 0.15); g.fillStyle = '#fff'; g.fillRect(px0, py0, pwid, phei); }
      g.restore();
    },
    drawTbc(g, m) {
      const tb = UI().tbc;
      const im = imgOf(tb);
      const s0 = m.hit - 0.4;
      if (m.t < s0) return;
      const u = prog(m.t, s0, m.hit);
      const w = tb ? tb.w : 236, h = tb ? tb.h : 44;
      const fx_ = UW - w - 18, fy = UH - h - 18;
      const off = (1 - ez(u, 'back')) * (w + 30);
      if (im) g.drawImage(im, Math.round(fx_ + off), fy);
      else f16().draw(g, 'To Be Continued', fx_ + off + w / 2, fy + 14, '#d8bc5c', { align: 'center', outline: '#24160a' });
    },

    // ================================================================ VS 卡：世界层（插入画面）
    drawVsWorld(wg, v) {
      const u = Math.max(0, v.t - v.pre);
      resetCtx(wg);
      wg.fillStyle = v.colours[1] || '#000'; wg.fillRect(0, 0, WW, WH);
      withPx(wg, (P) => {
        fx('radial_burst_bg', P, u, { cx: 160, cy: 96, colours: v.colours, n: 18, spin: 0.6 });
        fx('speedlines', P, u, { cx: 160, cy: 96, style: 'radial', n: 36, colour: 'white', inner: 70, alpha: 0.4, seed: v.seed });
        if (G.px.poly) G.px.poly(P, [[0, 70], [320, 52], [320, 120], [0, 138]], [22, 10, 36]);
        if (G.px.line) { G.px.line(P, 0, 69, 320, 51, '#ffffff', 1, 2); G.px.line(P, 0, 139, 320, 121, '#ffffff', 1, 2); }
      });
      const s = ez(prog(u, 0, 0.09), 'out3');
      // 敌人（×scale，朝左，白描边）
      const en = v.enemy, A = atlasOf(en.cid);
      if (A) {
        const meta = G.D.chars[en.cid];
        const centre = meta && meta.pivot && meta.cell && meta.pivot[1] < meta.cell[1] * 0.75;
        const baseY = en.y != null ? en.y : (centre ? 96 : 176);
        const fr = en.frame != null ? en.frame : atlasFrame(A, en.anim, u);
        const gap = (meta ? meta.cell[0] : 40) * en.scale * 0.55;
        for (let i = 0; i < en.n; i++) {
          const x = lerp(350, 262, s) - (i - (en.n - 1) / 2) * gap;
          A.draw(wg, en.anim, fr, Math.round(x), baseY, { scale: en.scale, flip: true, outline: '#ffffff' });
        }
      }
      // 英雄头像 ×3（白描边，前 0.33 s 张嘴喊）
      if (v.hd) {
        const f = u < 0.33 ? Math.floor(u * 10) % 2 : 0;
        drawHead(wg, v.hd, f, Math.round(lerp(-24, 56, s) - v.hd.w * 1.5), 96 - Math.round(v.hd.h * 1.5), 3, { outline: '#ffffff', ow: 1 });
      }
    },
    // VS 卡：UI 层（VS 字 / 敌名 / 英文；预备的黑边收拢；退场斜切）
    drawVsUI(g, v) {
      const u = v.t - v.pre;
      if (v.phase === 'pre') {          // 预备：上下黑边收拢（给 sting_reveal 的 0.26 s）
        const k = ez(clamp01(v.t / v.pre), 'in');
        const h = Math.round(k * 70);
        g.fillStyle = '#000'; g.fillRect(0, 0, UW, h); g.fillRect(0, UH - h, UW, h);
        return;
      }
      const m = v.meta;
      const sh = u < 0.25 ? Math.round((hash(Math.floor(G.clk.ui * 30), 7) * 2 - 1) * (1 - u / 0.25) * 6) : 0;
      if (v.phase === 'slam') {
        const sc = ez(prog(u, 0, 0.09), 'back'), sc2 = ez(prog(u, 0.03, 0.12), 'back');
        const mark = UI().vs && UI().vs.mark;
        if (sc > 0.05 && imgOf(mark)) blit(g, imgOf(mark), 322 + sh, 142, { scale: Math.max(0.05, sc) });
        if (sc2 > 0.05) {
          if (imgOf(m.name)) blit(g, imgOf(m.name), 322 + sh, 200, { scale: Math.max(0.05, sc2) });
          if (imgOf(m.en)) blit(g, imgOf(m.en), 322 + sh, 230, { alpha: clamp01(sc2) });
        }
        if (u < 0.05) { g.fillStyle = 'rgba(255,255,255,' + (0.5 * (1 - u / 0.05)).toFixed(3) + ')'; g.fillRect(0, 0, UW, UH); }
      } else {                              // 退场：0.12 s 斜切（替身色带 + 白刃）扫过
        const k = prog(u, 0.93, 1.05);
        this.slashBandUI(g, k, v.colours[0] || '#5a6a80');
      }
    },
    // UI 层的斜切带：一条带色的斜条从左扫到右（退场转场用）
    slashBandUI(g, k, col) {
      const ta = Math.tan(22 * Math.PI / 180);
      const span = UW + UH * ta + 160;
      const pos = -UH * ta - 80 + span * k;
      for (let y = 0; y < UH; y += 2) {
        const e = pos - (UH - y) * ta;
        g.fillStyle = col; g.fillRect(Math.round(e - 70), y, 70, 2);
        g.fillStyle = '#fff'; g.fillRect(Math.round(e), y, 4, 2);
      }
    },

    // ================================================================ 必杀切入：世界层（插入画面；斜切进出时露出下面的世界）
    renderCutin(c, t) {
      const cv = offCanvas(), g = cv.g;
      resetCtx(g);
      g.fillStyle = c.cols[c.cols.length - 1] || '#000'; g.fillRect(0, 0, WW, WH);
      withPx(g, (P) => {
        if (c.bg === 'menace') fx('menace_bg', P, t, { colours: c.cols, cx: 160, cy: 90, speed: 2.4 });
        else fx('radial_burst_bg', P, t, { cx: 160, cy: 90, colours: c.cols, n: 18, spin: 0.9 });
        fx('speedlines', P, t, { cx: 160, cy: 88, style: 'radial', n: 40, inner: 62, colour: 'white', alpha: 0.55, seed: c.seed });
      });
      const jx = Math.round(wob(t, 1.4, 13)), jy = Math.round(wob(t, 1, 17, 0.3));
      // 替身 ×4（右，朝左，带光环 grow 2）
      const A = c.A, sm = c.sm || {};
      if (A && sm.kind !== 'vine') {
        const aura = { color: sm.aura || '#c080ff', alpha: 0.55, grow: 2, jitter: true, t };
        if (atlasHas(A, 'portrait')) A.draw(g, 'portrait', atlasFrame(A, 'portrait', t), 238 + jx, 182 + jy, { scale: 4, flip: true, aura });
        else {
          const name = atlasHas(A, 'idle') ? 'idle' : null;
          A.draw(g, name || 'idle', atlasFrame(A, name || 'idle', t), 244 + jx, 232 + jy, { scale: 3, flip: true, aura });
        }
      } else if (sm.kind === 'vine') {
        withPx(g, (P) => {
          for (let i = 0; i < 4; i++) fx('vines', P, 330, 30 + i * 36, 170 + i * 6, 60 + i * 24, t, 0, 0.3, { colour: 'purple', strands: 2, seed: i });
        });
      }
      // 本人头像 ×4（左）
      if (c.hd) {
        const f = c.hd.imgs.length > 1 ? 1 : 0;
        drawHead(g, c.hd, f, 20 - jx, 26 + jy, 4, { outline: '#ffffff', ow: 2 });
      }
      return cv;
    },
    drawCutinWorld(wg, c) {
      const t = c.t;
      const cv = this.renderCutin(c, t);
      const inK = clamp01(t / 0.12), outK = clamp01((t - (c.dur - 0.12)) / 0.12);
      if (inK >= 1 && outK <= 0) { wg.drawImage(cv, 0, 0); return; }
      drawWorldUnder(wg);
      const edge = c.edge || '#fff';
      for (let y = 0; y < WH; y++) {
        let xa, xb;
        if (outK <= 0) { xa = 0; xb = Math.round(slashEdge(y, inK)); }
        else { xa = Math.round(slashEdge(y, outK)); xb = WW; }
        xa = Math.max(0, xa); xb = Math.min(WW, xb);
        if (xb > xa) wg.drawImage(cv, xa, y, xb - xa, 1, xa, y, xb - xa, 1);
        const ex = outK <= 0 ? xb : xa;
        if (ex > -2 && ex < WW + 2) { wg.fillStyle = edge; wg.fillRect(ex - 1, y, 3, 1); wg.fillStyle = '#fff'; wg.fillRect(ex, y, 1, 1); }
      }
    },
    // 必杀切入：UI 层（招式名大字 + 暗色斜条）
    drawCutUI(g, c) {
      const t = c.t;
      const m = c.title ? (UI().specials || {})[c.title] : null;
      if (c.title && !m && G.dbg && G.dbg.missingImg && !c.noted) { c.noted = true; G.dbg.missingImg.add('ui/special/' + c.title); }
      const im = imgOf(m);
      if (!im || t < 0.12) return;
      const outA = clamp01((c.dur - t) / 0.12);
      const sc = ez(prog(t, 0.14, 0.32), 'back');
      const cy = 304, w = im.naturalWidth;
      g.save();
      g.globalAlpha = outA;
      g.fillStyle = 'rgba(8,4,18,0.82)';
      g.beginPath(); g.moveTo(0, cy - 30); g.lineTo(UW, cy - 44); g.lineTo(UW, cy + 22); g.lineTo(0, cy + 36); g.fill();
      g.fillStyle = c.edge || '#fff';
      for (let x = 0; x < UW; x += 2) {
        g.fillRect(x, Math.round(cy - 30 - x * 14 / UW) - 2, 2, 2);
        g.fillRect(x, Math.round(cy + 36 - x * 14 / UW), 2, 2);
      }
      g.restore();
      if (sc > 0.05) blit(g, im, 320 + Math.round(wob(t, 1.5, 13)), cy - 4, { scale: Math.max(0.05, sc), alpha: outA });
      void w;
    },

    // ================================================================ W6 敌人切入：UI 层斜带（世界照走、看得见上下）
    drawEnemyCut(g, e) {
      const t = e.t;
      const cv = offCanvas2(), cg = cv.g;
      resetCtx(cg);
      cg.fillStyle = e.cols[e.cols.length - 1]; cg.fillRect(0, 0, WW, WH);
      withPx(cg, (P) => {
        fx('radial_burst_bg', P, t, { cx: 160, cy: 90, colours: e.cols, n: 18, spin: 0.9 });
        fx('speedlines', P, t, { cx: 160, cy: 90, style: 'radial', n: 40, inner: 60, colour: 'white', alpha: 0.55, seed: e.seed });
      });
      const jx = Math.round(wob(t, 1.4, 13)), jy = Math.round(wob(t, 1, 17, 0.3));
      if (e.hd) drawHead(cg, e.hd, e.hd.imgs.length > 1 ? Math.floor(t * 8) % 2 : 0, 160 - e.hd.w * 2 + jx, 90 - e.hd.h * 2 + jy, 4, { outline: '#ffffff', ow: 2 });
      // 斜带：上沿 (0,44)→(320,30)，下沿 (0,150)→(320,136)；进出 0.08 s 斜切
      const inK = clamp01(t / 0.08), outK = clamp01((t - (e.dur - 0.08)) / 0.08);
      const top = (x) => 44 - 14 * x / WW, bot = (x) => 150 - 14 * x / WW;
      for (let y = 30; y <= 150; y++) {
        let xa = Math.max(0, Math.ceil((44 - y) * WW / 14)), xb = Math.min(WW, Math.floor((150 - y) * WW / 14) + 1);
        if (outK <= 0) xb = Math.min(xb, Math.round(slashEdge(y, inK)));
        else xa = Math.max(xa, Math.round(slashEdge(y, outK)));
        if (xb > xa) g.drawImage(cv, xa, y, xb - xa, 1, xa * 2, y * 2, (xb - xa) * 2, 2);
      }
      const xr = outK <= 0 ? WW * inK + 60 : WW;
      const xl = outK <= 0 ? 0 : WW * outK;
      g.fillStyle = '#fff';
      for (let x = Math.max(0, Math.floor(xl)); x < Math.min(WW, xr); x++) {
        g.fillRect(x * 2, Math.round(top(x)) * 2 - 2, 2, 2);
        g.fillRect(x * 2, Math.round(bot(x)) * 2 + 2, 2, 2);
      }
      const m = e.title ? (UI().titles || {})[e.title] : null;
      if (e.title && !m && G.dbg && G.dbg.missingImg && !e.noted) { e.noted = true; G.dbg.missingImg.add('ui/title/' + e.title); }
      const im = imgOf(m);
      if (im && t > 0.08) {
        const sc = ez(prog(t, 0.08, 0.22), 'back');
        blit(g, im, 320 + Math.round(wob(t, 1.5, 13)), 262, { scale: Math.max(0.05, sc), alpha: clamp01((e.dur - t) / 0.08) });
      }
    },

    // ================================================================ 眼部条带：世界层（插入画面）
    drawEyeWorld(wg, e) {
      const t = e.t;
      resetCtx(wg);
      wg.fillStyle = '#000'; wg.fillRect(0, 0, WW, WH);
      const b0 = 54, b1 = 120;
      withPx(wg, (P) => {
        const cols = [[42, 32, 64], [74, 58, 106], [42, 32, 64]];
        for (let y = b0; y < b1; y++) {
          const u = (y - b0) / (b1 - b0), k = u < 0.5 ? u * 2 : (1 - u) * 2;
          const c = [0, 1, 2].map((i) => Math.round(cols[0][i] + (cols[1][i] - cols[0][i]) * Math.round(k * 5) / 5));
          if (G.px.rect) G.px.rect(P, 0, y, WW, 1, c);
        }
        fx('speedlines', P, t, { cx: 160, cy: 86, style: 'horizontal', n: 26, inner: 0, colour: '#8a7ab0', band: [b0, b1], alpha: 0.8 });
      });
      if (e.hd) drawHead(wg, e.hd, e.hd.imgs.length > 1 ? 1 : 0, 160 - e.hd.w * 3, 87 - Math.round(e.hd.h * 13 / 32) * 6, 6);
      wg.fillStyle = '#000'; wg.fillRect(0, 0, WW, b0); wg.fillRect(0, b1 + 1, WW, WH - b1 - 1);
      wg.fillStyle = '#fff'; wg.fillRect(0, b0 - 1, WW, 1); wg.fillRect(0, b1, WW, 1);
      withPx(wg, (P) => {
        fx('glint', P, 172, 87, t, 0.05, { size: 9, dur: 0.45, accent: '#5cf0d0' });
        fx('glint', P, 212, 87, t, 0.09, { size: 7, dur: 0.4, accent: '#5cf0d0' });
      });
    },
  });
})();
