// 包 1 自测用的桩：别的包还没写好时，按技术约定接口给的最小实现（只在 tools\dev\p1\test_page.html 里加载，集成时换成真的）
'use strict';
(function () {
  const G = window.G;

  // ---- 包 5：时停（flowScale 测试里可改）
  G.time = { active: false, k: 1, flowScale() { return this.k; }, overActive() { return false; }, isFrozen() { return false; } };

  // ---- 包 2：像素会话（真的 getImageData / putImageData：顺便验“世界层画布读像素不出 willReadFrequently 警告”）
  G.px = {
    cur: null,
    begin(ctx) {
      if (this.cur) throw new Error('像素会话不能嵌套');
      const d = ctx.getImageData(0, 0, G.W, G.H);
      this.cur = { ctx, d, u32: new Uint32Array(d.data.buffer), w: G.W, h: G.H };
      return this.cur;
    },
    end() { const c = this.cur; this.cur = null; if (c) c.ctx.putImageData(c.d, 0, 0); },
  };
  // 特效：开着时在 (2..5, 2..5) 画一个反色小方块（mid 层）
  G.fx = {
    on: false, calls: { mid: 0, over: 0 },
    hasPixel() { return this.on; },
    drawPixel(P, layer) {
      this.calls[layer]++;
      if (!this.on || layer !== 'mid') return;
      for (let y = 2; y < 6; y++) for (let x = 2; x < 6; x++) P.u32[y * P.w + x] ^= 0x00ffffff;
    },
  };
  G.post = { on: false, calls: { mid: 0, final: 0 }, active() { return this.on; }, apply(P, stage) { this.calls[stage]++; } };

  // ---- 包 3：最小对话 / QTE（只为测“点屏推进”“J 不推进”“QTE 后狂点不跳台词”，规则照 §4.10.1 / §4.3.4）
  const U = (G.ui = {
    dlg: null, qte: null, menu: null, choiceBox: null, narr: null, notice: null,
    blocking() { return !!(this.dlg || this.qte || this.menu || this.choiceBox || this.narr || this.notice); },
    say(text, o = {}) {
      return new Promise((res) => { this.dlg = { text, t: 0, shown: 0, all: false, pages: o.pages || 1, page: 0, res }; });
    },
    startQte(o) {
      return new Promise((res) => { this.qte = { type: o.type || 'mash', need: o.need || 8, m: 0, t: 0, res, state: 'run' }; });
    },
    update(dt) {
      const I = G.input;
      const q = this.qte;
      if (q) {
        q.t += dt;
        if (q.state === 'run' && I.mashHit()) { q.m++; if (q.m >= q.need) { q.state = 'done'; q.doneT = q.t; } }
        if (q.state === 'done' && q.t - q.doneT >= 0.0) {
          this.qte = null;
          I.lockOk(0.6);            // §4.3.4：每个 QTE resolve 前
          I.consumeOk();
          q.res(true);
        }
        return;
      }
      const d = this.dlg;
      if (!d) return;
      d.t += dt;
      if (!d.all) { d.shown = Math.min(d.text.length, Math.floor(d.t * 18)); if (d.shown >= d.text.length) d.all = true; }
      if (I.okHit() && d.t > 0.12) {
        I.consumeOk();
        if (!d.all) { d.all = true; d.shown = d.text.length; }
        else if (d.page + 1 < d.pages) { d.page++; d.t = 0; d.all = false; d.shown = 0; }
        else { this.dlg = null; d.res(); }
      }
    },
    draw(ug) {
      const d = this.dlg;
      if (d) { ug.fillStyle = 'rgba(16,14,40,0.88)'; ug.fillRect(20, 272, 600, 80); }
      if (this.qte) { ug.fillStyle = '#ffd34a'; ug.fillRect(120, 210, 400 * Math.min(1, this.qte.m / this.qte.need), 8); }
    },
  });

  // ---- 包 4：世界 / 队伍（触屏显隐读的那几个字段）
  G.world = { combat: false, near: null, player: { energy: 0, energyMax: 100 }, fight: null, _look: null, findLook() { return this._look; } };
  G.party = { _ready: true, _swap: true, lookReady() { return this._ready; }, canSwap() { return this._swap; } };

  // ---- 测试场景：棋盘格世界（看缩放清不清楚）+ 一个标记像素（验 w2u）+ UI
  G.testScene = {
    name: 'world',
    frozen: false,
    marker: null,          // { sx, sy }：世界画布坐标，画一个纯红像素
    updates: 0,
    probe: null,           // 测试挂的探针：每步在 UI 处理之前读一次 G.input
    update(dt, worldAdv, wdt) { this.updates++; if (this.probe) this.probe(); U.update(dt); },
    drawWorld(wg) {
      for (let y = 0; y < G.H; y += 8) for (let x = 0; x < G.W; x += 8) {
        wg.fillStyle = ((x + y) >> 3) & 1 ? '#203040' : '#304050';
        wg.fillRect(x, y, 8, 8);
      }
      if (this.marker) { wg.fillStyle = '#ff0000'; wg.fillRect(this.marker.sx, this.marker.sy, 1, 1); }
    },
    hasPixel() { return true; },
    drawUI(ug) { U.draw(ug); },
  };
})();
