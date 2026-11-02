// 全屏后期（包 2）：常驻滤镜栈（褐色 / 时停色调 / 罩色 / 暗角 / 灰…）、冲击帧（0.6 s 全局节流）、冲击帧序列、时停三段画面、低血脉冲
// 技术约定 §4.7 / §2.5：apply(P, 'mid') = 滤镜（加入顺序）→ 时停画面（G.time.visual()）→ 脉冲；apply(P, 'final') = 冲击帧（永远最后）。
// 禁止 ctx.filter（§0.2 第 13 条）：全部在像素会话的 Uint32 数组上算。
'use strict';
(function () {
  const G = window.G;
  const now = () => (G.clk ? G.clk.ui || 0 : 0);
  const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
  const reduce = () => !!(G.settings && G.settings.reduceFlash);
  const MIN_FLASH = 2 / 60 - 1e-6;                          // 任何“一帧闪”不少于 2/60 s（§0.2 第 6 条）
  function dbgEv(type, data) { try { if (G.dbg && G.dbg.ev) G.dbg.ev(type, data); } catch (e) { /* 调试记录失败不影响画面 */ } }

  const KNOWN = new Set(['sepia', 'ts_gray', 'ts_grey', 'ts_yellow', 'ts_blue', 'ts_purple', 'ts_green', 'ts_red', 'tint', 'vignette', 'gray', 'grey', 'invert', 'dim', 'vision']);

  const post = {
    filters: [],          // { name, from, to, t0, dur, kill, o }
    imp: null,            // { styles, step, hold, t0, o }
    lastImpact: -Infinity,
    pulses: {},           // name → { t0 }

    // 常驻滤镜：amount = null 删掉（o.dur > 0 时先淡出再删）；name = null 清掉全部滤镜；o.dur 秒内从当前值缓到 amount（ui 时钟）
    filter(name, amount = 1, o = {}) {
      o = o || {};
      if (name == null) { this.filters.length = 0; return; }
      if (!KNOWN.has(name)) { dbgEv('post_unknown', { name }); return; }
      const t = now(), dur = Math.max(0, o.dur || 0);
      let f = null;
      for (const e of this.filters) if (e.name === name) f = e;
      if (amount == null) {
        if (!f) return;
        if (dur <= 0) { this.filters.splice(this.filters.indexOf(f), 1); return; }
        f.from = this.value(name); f.to = 0; f.t0 = t; f.dur = dur; f.kill = true;
        return;
      }
      if (!f) { f = { name, from: 0, to: 0, t0: t, dur: 0, kill: false, o: {} }; this.filters.push(f); f.from = o.from != null ? o.from : (dur > 0 ? 0 : amount); }
      else f.from = o.from != null ? o.from : this.value(name);
      f.to = amount; f.t0 = t; f.dur = dur; f.kill = false;
      Object.assign(f.o, o);
    },
    // 当前值（0 = 没有）
    value(name) {
      for (const f of this.filters) if (f.name === name) return this._val(f, now());
      return 0;
    },
    _val(f, t) {
      if (f.dur <= 0) return f.to;
      return f.from + (f.to - f.from) * clamp((t - f.t0) / f.dur);
    },

    // 冲击帧：style = invert bw bw3 red purple yellow blue green（fx.IMPACT）或 2–3 色数组；上一次开始后 0.6 s 内再调用丢掉（o.force 例外）
    // 减少闪烁：不画，改成 G.shake(2, 0.15)。返回 true = 放了
    impact(style = 'invert', dur = 1 / 24, o = {}) {
      return this.impactSeq([style], dur, 0, o);
    },
    // 冲击帧序列：例 impactSeq(['invert', 'purple'], 1/24, 0.28) = invert 1 格 → 紫色 1 格并定格 0.28 s
    impactSeq(styles, step = 1 / 24, holdLast = 0, o = {}) {
      o = o || {};
      if (!styles || !styles.length) return false;
      if (reduce()) { if (G.shake) G.shake(2, 0.15); return false; }
      const t = now();
      if (!o.force && t - this.lastImpact < 0.6) return false;
      this.lastImpact = t;
      this.imp = { styles: styles.slice(), step: Math.max(step || 1 / 24, MIN_FLASH), hold: Math.max(0, holdLast || 0), t0: t, o };
      return true;
    },
    // 脉冲：'lowhp' = vignette(0.35 + 0.15·sin(2π·1.2t), '#5a0010')
    pulse(name, on) {
      if (name !== 'lowhp') { dbgEv('post_unknown', { name }); return; }
      if (on) { if (!this.pulses[name]) this.pulses[name] = { t0: now() }; } else delete this.pulses[name];
    },
    _imp() {
      const im = this.imp;
      if (!im) return null;
      const e = now() - im.t0;
      if (e < 0 || e >= im.styles.length * im.step + im.hold) { this.imp = null; return null; }
      return im;
    },
    _ts() {
      const T = G.time;
      if (!T || typeof T.visual !== 'function') return null;
      const v = T.visual();
      return v && v.phase && v.phase !== 'warn' ? v : null;
    },
    active() {
      return this.filters.length > 0 || !!this._imp() || Object.keys(this.pulses).length > 0 || !!this._ts();
    },
    apply(P, stage) {
      const FX = G.FX;
      if (!FX || !P) return;
      if (stage === 'final') {
        const im = this._imp();
        if (!im || reduce()) return;
        const idx = Math.min(im.styles.length - 1, Math.floor((now() - im.t0) / im.step));
        FX.impact_frame(P, { style: im.styles[idx], threshold: im.o.threshold });
        return;
      }
      // 'mid'：滤镜（加入顺序）→ 时停画面 → 脉冲
      const t = now();
      for (let i = 0; i < this.filters.length; i++) {
        const f = this.filters[i], a = this._val(f, t);
        if (f.kill && f.dur > 0 && t - f.t0 >= f.dur) { this.filters.splice(i, 1); i--; continue; }
        if (a > 0) this._filter(P, f.name, a, f.o);
      }
      const v = this._ts();
      if (v) {
        const tint = v.tint || 'yellow', u = clamp(v.u || 0);
        if (v.phase === 'burst') FX.timestop(P, u, 0, v.cx, v.cy, { dur: 1, tint, soft: reduce() });
        else if (v.phase === 'stopped') FX.timestop_world(P, { amount: 1, tint });
        else if (v.phase === 'resume') FX.time_resume(P, u, 0, v.cx, v.cy, { dur: 1, tint });
      }
      if (this.pulses.lowhp) FX.vignette(P, { amount: 0.35 + 0.15 * Math.sin(2 * Math.PI * 1.2 * t), colour: '#5a0010' });
    },
    _filter(P, name, a, o) {
      const FX = G.FX, px = G.px;
      switch (name) {
        case 'sepia': FX.sepia(P, { amount: a, strength: o.strength == null ? 0.5 : o.strength }); break;
        case 'ts_gray': case 'ts_grey': case 'ts_yellow': case 'ts_blue': case 'ts_purple': case 'ts_green': case 'ts_red':
          FX.timestop_world(P, { amount: a, tint: name === 'ts_grey' ? 'ts_gray' : name }); break;
        case 'tint': px.tint(P, o.color || o.colour || '#000000', a); break;
        case 'vignette': FX.vignette(P, { amount: a, colour: o.colour || o.color || 'black', inner: o.inner == null ? 0.65 : o.inner }); break;
        case 'gray': case 'grey': px.gray(P, a, o.tint || null); break;
        case 'invert': if (a >= 0.5) px.invert(P); break;
        case 'dim': FX.dim_bg(P, a, { col: o.col || o.colour || '#140c30' }); break;
        case 'vision': this._vision(P, a, o); break;
        default: break;
      }
    },
    // 视野限制（雾、致盲：只剩 follow 周围 r px；技术约定 §4.16 末预留，先实现简单版）
    _vision(P, a, o) {
      const px = G.px, f = o.follow, cam = G.cam || { x: 0, y: 0 };
      let cx = P.w / 2, cy = P.h / 2;
      if (f && f.x != null) { cx = f.x - (cam.x || 0); cy = f.y - (f.z || 0) - (cam.y || 0) - 20; }
      const r = o.r || 48, edge = o.edge || 12, c = px.rgb(o.colour || o.color || '#000000');
      const cr = c & 255, cg = (c >>> 8) & 255, cb = (c >>> 16) & 255, d = px.dist(cx, cy, 1, P.w, P.h), u = P.u32;
      for (let y = 0; y < P.h; y++) for (let x = 0; x < P.w; x++) {
        const i = y * P.w + x, k = clamp((d[i] - r) / edge) * a;
        if (k > 0) px.qblendI(u, i, x, y, cr, cg, cb, k, 4, false);
      }
    },
    clear() {
      this.filters.length = 0;
      this.imp = null;
      this.pulses = {};
    },
  };
  G.post = post;
})();
