// 替身子对象（包 4）：召唤 / 收回 / 站位 / 光环 / 透明 / 动作时间表；非人形替身（藤蔓 vine、沙 sand）；远程替身的触须连线（技术约定 §4.12）
'use strict';
(function () {
  const G = window.G;
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const easeOut = (u) => (G.ease ? G.ease(u, 'out') : 1 - Math.pow(1 - u, 3));
  const easeIn = (u) => (G.ease ? G.ease(u, 'in') : u * u * u);
  const lerp = (a, b, u) => a + (b - a) * u;
  const IDLE_DEF = { dx: -6, z: 6 };
  // 构建时人物 / 替身整体缩了 G.D.ck 倍：所有以像素写的“替身离本体多远 / 多高 / 藤蔓多长”都在这里统一乘回去
  const ck = () => (G.D && G.D.ck) || 1;
  const SAND = ['#f0c878', '#d8a050', '#fbe0a0'];
  const AUTO_RECALL = 2.5;          // 自由走动：亮出来以后多久没动作就收回
  const VINE_GROW = 0.1;
  const frozenOf = (a) => !!(G.time && G.time.isFrozen && G.time.isFrozen(a));
  const W = () => G.world || {};
  const sBusy = () => !!(G.S && G.S.busy);
  const light = (c, k) => (G.mixHex ? G.mixHex(c, '#ffffff', k) : c);
  const sfx = (name, o) => { if (name && G.audio && G.audio.sfx) G.audio.sfx(name, o); };
  const spawn = (name, kw, o) => (G.fx && G.fx.spawn ? G.fx.spawn(name, kw, o) : null);

  class Stand {
    constructor(owner, standId, o = {}) {
      const sd = (G.D && G.D.stands && G.D.stands[standId]) || {};
      this.owner = owner;
      this.id = standId;
      this.def = sd;
      this.kind = sd.kind || 'humanoid';
      this.atlas = this.kind === 'vine' ? null : G.atlas(standId);
      this.color = o.color || sd.aura || '#c080ff';
      this.ghost = sd.ghost || this.color;
      this.alpha = 0.92;
      this.skin = o.skin || null;
      this.mode = 'hidden';
      this.modeT = 0;
      this.pose = 'idle';
      this.poseT = 0;
      this.seq = null;
      this.frameOverride = null;
      this.x = owner.x; this.y = owner.y; this.z = 0;
      this.depth = -0.5;
      this.dx = 0;
      this.holdT = 0;
      this.idleT = 0;
      this.ghostOn = false;
      this.ghosts = [];
      this._ap = null;      // 出现：{ t, dur, rise }
      this._rc = null;      // 收回：{ t, dur, x0, z0 }
      this._act = null;     // 当前动作的参数
      this._jx = 0;
      this._clk = 0;        // 替身自己的时间（冻住 / 顿帧时不走）：藤蔓、残影用
      this._vine = null;    // 藤蔓：{ t0, len, dy, hold, out: null | t0 }
      this._gl = -1;
    }
    get visible() { return this.mode !== 'hidden'; }
    // 本体离地高度：this.z 是“替身离本体脚底多高”，画面 / 判定 / 特效要再加上本体自己的 z
    //   （序-8 石阶上人的 z = 台阶高度，最高 80；飞的敌人 z = fly.z）。以前没加，人在坡顶时替身掉在地面那一层（2026-10-10 用户截图）
    oz() { return (this.owner && this.owner.z) || 0; }
    idleSpot() {
      const sp = this.owner.standPos;
      const ip = (sp && (sp.dx != null || sp.z != null) ? sp : null) || this.def.idle || IDLE_DEF;
      return { dx: (ip.dx == null ? IDLE_DEF.dx : ip.dx) * ck(), z: (ip.z == null ? IDLE_DEF.z : ip.z) * ck() };
    }
    link() {
      const sp = this.owner.standPos;
      return sp && sp.link !== undefined ? sp.link : this.def.link || null;
    }

    // ---------------- 召唤 / 收回 / 动作
    summon(o = {}) {
      const ow = this.owner, f = ow.facing || 1;
      const dur = o.dur == null ? 0.35 : o.dur, rise = o.rise == null ? 12 : o.rise;
      const was = this.mode;
      this._rc = null;
      if (was === 'hidden' || was === 'recall') {
        const ip = this.idleSpot(), sc = ow.scale || 1;
        if (was === 'hidden') { this.x = ow.x + f * ip.dx * sc; this.z = ip.z * sc; }
        this.mode = 'summon'; this.modeT = 0;
        this.pose = 'idle'; this.poseT = 0; this.seq = null; this._act = null; this.frameOverride = null; this.depth = -0.5;
        this._ap = { t: 0, dur: Math.max(0.01, dur), rise };
        if (this.kind === 'humanoid' || this.kind === 'sand') {
          spawn('summon_lines', { x: Math.round(this.x), y: Math.round(ow.y - this.oz() - this.z), colour: this.color, aura_colour: this.color, dur },
            { by: ow, tag: 'stand' });
        }
        if (this.kind === 'sand') this._sand(ow);
        if (this.kind === 'vine') this._vine = { t0: this._clk, len: 26, dy: -10, hold: 0.25, out: null };
        if (o.sfx !== false) sfx(this.def.summonSfx, { vol: o.vol == null ? 0.9 : o.vol, x: ow.x });
        if (o.flash && G.flash) G.flash(4 / 60, 0.35, '#d8c0ff');
        if (o.card) {
          if (G.uifx && G.uifx.standCard) G.uifx.standCard(this.id, typeof o.card === 'object' ? o.card : {});
          if (G.audio && G.audio.cue) G.audio.cue('sting_reveal');
        }
      }
      this.idleT = 0;
      const Wd = W();
      if (ow === Wd.player && Wd.free && !Wd.combat && Wd.standReact) Wd.standReact(ow);
      return this;
    }
    recall(o = {}) {
      if (this.mode === 'hidden' || this.mode === 'recall') return this;
      const dur = o.dur == null ? 0.25 : o.dur;
      this.mode = 'recall'; this.modeT = 0;
      this._rc = { t: 0, dur: Math.max(0.01, dur), x0: this.x, z0: this.z };
      this._ap = null; this._act = null; this.ghostOn = false;
      if (this._vine && this._vine.out == null) this._vine.out = this._clk;
      if (o.sfx !== false) sfx('stand_recall', { vol: 0.7, x: this.owner.x });
      return this;
    }
    hide() {
      this.mode = 'hidden'; this.modeT = 0; this._ap = this._rc = this._act = this._vine = null;
      this.pose = 'idle'; this.seq = null; this.frameOverride = null; this.ghosts.length = 0; this.ghostOn = false; this.idleT = 0;
      this.x = this.owner.x; this.z = 0;
    }
    // o = { dx: 14, z: 4, dur: null, seq: null, hold: false, depth: 'front', jitter: 0 }；hidden 时自动快召（0.12 s、rise 4）
    act(pose, o = {}) {
      if (this.mode === 'hidden' || this.mode === 'recall') this.summon({ dur: 0.12, rise: 4, sfx: o.sfx });
      const base = pose === 'rush' ? { dx: 16, z: 4, jitter: 1 } : pose === 'block' ? { dx: 12, z: 3 } : {};
      const p = Object.assign({ dx: 14, z: 4, dur: null, seq: null, hold: false, depth: 'front', jitter: 0 }, base);
      // 值为 undefined 的键不覆盖默认值：combat 出招时传 { dx: m.standDx }，招式没写 standDx 就是 undefined，
      // 以前会让替身 x 变成 NaN 且再也回不来（火柱之后红色魔术师消失、法皇射出的宝石 x 为 NaN）
      for (const k in o) if (o[k] !== undefined) p[k] = o[k];
      p.dx *= ck(); p.z *= ck();
      this.mode = 'act'; this.modeT = 0;
      this.pose = pose; this.poseT = 0; this.seq = p.seq || null; this.frameOverride = null;
      this._act = p; this.dx = p.dx; this.depth = p.depth === 'back' ? -0.5 : 0.5; this.holdT = 0; this.idleT = 0;
      const ow = this.owner;
      if (this.kind === 'vine') {
        // 藤蔓长度可由招式给（p.len = 招式的 vineLen，和判定距离对齐）；p.vineHold 给了就到时自己缩回（藤鞭打完立刻收），不等动作结束
        const len = p.len != null ? p.len : pose === 'rush' ? 52 : pose === 'block' ? 18 : pose === 'punch_heavy' ? 64 : 44;
        this._vine = { t0: this._clk, len, dy: p.vineDy != null ? p.vineDy : pose === 'block' ? -14 : -2, hold: p.vineHold != null ? p.vineHold : p.dur != null ? p.dur : 0.22, out: null, act: true, snap: p.vineHold != null, thorns: pose === 'punch_heavy' };
      }
      if (this.kind === 'sand') this._sand(ow);
      return this;
    }
    idle() {
      if (this.mode === 'hidden' || this.mode === 'recall') return this;
      this.mode = 'idle'; this.modeT = 0;
      this.pose = 'idle'; this.poseT = 0; this.seq = null; this._act = null; this.frameOverride = null; this.depth = -0.5;
      if (this._vine && this._vine.act && this._vine.out == null) this._vine.out = this._clk;
      return this;
    }
    _sand(ow) {
      spawn('burst', { x: Math.round(ow.x + (ow.facing || 1) * 4), y: Math.round(ow.y - this.oz() - 2), n: 16, speed: 50, life: 0.5,
        colours: SAND, gravity: 160, spread: 140, angle: 90, seed: (this._clk * 97) | 0 }, { by: ow, tag: 'stand' });
    }

    // ---------------- 每帧（在本体之后调；本体冻住 / 局部顿帧时整个跳过）
    frame() {
      if (this.frameOverride != null) return this.frameOverride;
      if (this.seq && this.seq.length) {
        for (const [fr, until] of this.seq) if (this.poseT < until) return fr;
        return this.seq[this.seq.length - 1][0];
      }
      return this.atlas ? this.atlas.frameAt(this.pose, this.poseT, 1, this.skin) : 0;
    }
    update(dt) {
      const ow = this.owner;
      if (!ow || frozenOf(ow) || ow.stopT > 0) return;
      const k = dt * (ow.slowK || 1);
      this._clk += k;
      this.modeT += k; this.poseT += k;
      const f = ow.facing || 1;
      this.y = ow.y;
      if (this.mode === 'hidden') { this.x = ow.x; this.z = 0; this._jx = 0; this._ghostTick(); return; }
      if (this._ap) {
        this._ap.t += k;
        if (this._ap.t >= this._ap.dur) { this._ap = null; if (this.mode === 'summon') { this.mode = 'idle'; this.modeT = 0; } }
      }
      if (this.mode === 'act') {
        const a = this._act;
        let end = false;
        if (a.dur != null) end = this.poseT >= a.dur;
        else if (this.seq && this.seq.length) { const last = this.seq[this.seq.length - 1][1]; end = last < 50 && this.poseT >= last; }
        else if (this.atlas) end = this.atlas.done(this.pose, this.poseT, 1, this.skin);
        else end = this.poseT >= 0.3;
        if (end) { if (a.hold) this.holdT += k; else this.idle(); }
      }
      if (this.mode === 'recall') {
        const r = this._rc, u = Math.min(1, (r.t += k) / r.dur), e = easeIn(u);
        this.x = lerp(r.x0, ow.x, e);
        this.z = lerp(r.z0, ow.topPx() * ow.scale * 0.55, e);
        this._jx = 0;
        if (u >= 1) this.hide();
        this._ghostTick();
        return;
      }
      // 替身跟本体一起缩放（第5章脑内战本体缩到 0.5）：站位偏移、浮起高度、召唤上升量都乘本体的 scale，画的时候 draw() 也按 scale 画
      let tx, tz;
      const sc = ow.scale || 1;
      if (this.mode === 'act') { tx = ow.x + f * this._act.dx * sc; tz = this._act.z * sc; }
      else {
        const ip = this.idleSpot();
        tx = ow.x + f * ip.dx * sc;
        tz = (ip.z + Math.round(Math.sin(ow.ownT * 2.2) * 1.5)) * sc;   // 浮动用本体自己的时间
        this.depth = -0.5;
      }
      if (this._ap) tz -= this._ap.rise * sc * (1 - easeOut(Math.min(1, this._ap.t / this._ap.dur)));
      if (!(Math.abs(tx - this.x) <= 140)) this.x = tx;      // 含 this.x 为 NaN 的情况：直接归位
      else this.x += (tx - this.x) * (1 - Math.pow(2, -k / 0.012));   // 约 0.05 s 到位
      this.z = Math.round(tz);
      this._jx = this._act && this._act.jitter ? (Math.random() < 0.5 ? -1 : 1) * this._act.jitter : 0;
      // 自由走动：2.5 s 没再动作就收回
      const Wd = W();
      if (this.mode === 'idle' && Wd.free && !Wd.combat && !sBusy()) {
        this.idleT += dt;
        if (this.idleT >= AUTO_RECALL) this.recall();
      } else if (this.mode !== 'idle') this.idleT = 0;
      this._ghostTick();
    }
    _ghostTick() {
      if (this.ghostOn && this.mode !== 'hidden' && this.atlas) {
        if (this._gl < 0 || this._clk - this._gl >= 1 / 30) {
          this._gl = this._clk;
          this.ghosts.push({ x: this.x, z: this.z, oz: this.oz(), pose: this.pose, frame: this.frame(), facing: this.owner.facing, t: this._clk });
          if (this.ghosts.length > 4) this.ghosts.shift();
        }
      }
      while (this.ghosts.length && this._clk - this.ghosts[0].t >= 0.25) this.ghosts.shift();
    }
    // 判定原点（= 替身当前位置）、拳影 / 连打特效中心（世界坐标）
    origin() { return { x: this.x, y: this.owner.y, z: this.oz() + this.z }; }
    chest() { const f = this.owner.facing || 1, sc = this.owner.scale || 1; return { x: this.x + f * 8 * sc, y: this.owner.y, z: this.oz() + this.z + 30 * sc }; }

    // ---------------- 画（canvas pass；纵深排序项：owner.y ± 0.5）
    draw(g, camX, camY, o = {}) {
      const ow = this.owner;
      if (this.mode === 'hidden' || !ow.visible || !this.atlas || this.kind === 'vine') return;
      const flip = (ow.facing || 1) < 0, sy0 = ow.y - this.oz() - camY, scale = ow.scale || 1;
      if (this.ghosts.length) {
        const col = light(this.ghost || this.color, 0.3), n = this.ghosts.length;
        this.ghosts.forEach((gh, i) => {
          const age = this._clk - gh.t;
          if (age >= 0.25) return;
          const dth = (n > 1 ? 0.2 + 0.35 * (i / (n - 1)) : 0.55) * (1 - age / 0.25);
          this.atlas.draw(g, gh.pose, gh.frame, gh.x - camX, ow.y - camY - (gh.oz || 0) - gh.z, { flip: gh.facing < 0, scale, skin: this.skin, tint: { color: col, k: 0.45 }, dither: dth });
        });
      }
      let pose = this.pose;
      const fallbackBlock = pose === 'block' && !this.atlas.has('block', this.skin);
      if (fallbackBlock) pose = 'idle';
      const frame = fallbackBlock ? this.atlas.frameAt('idle', this.poseT, 1, this.skin) : this.frame();
      const sx = this.x - camX + this._jx, sy = sy0 - this.z;
      const aura = { color: this.color, alpha: 0.55, grow: 1, jitter: true, t: ow.ownT };
      let opt;
      if (this._ap) {
        const u = Math.min(1, this._ap.t / this._ap.dur);
        const vis = Math.floor(this._ap.t * 30) % 2 === 0 || u > 0.55;
        opt = { flip, scale, skin: this.skin, aura: { color: this.color, alpha: 0.7 * u, grow: 1, jitter: true, t: ow.ownT },
          tint: { color: '#ffffff', k: 1 - u }, dither: vis ? 0.92 * Math.min(1, 0.25 + u) : 0 };
      } else if (this.mode === 'recall') {
        const u = Math.min(1, this._rc.t / this._rc.dur);
        opt = { flip, scale, skin: this.skin, aura: { color: this.color, alpha: 0.55 * (1 - u), grow: 1, jitter: true, t: ow.ownT },
          tint: { color: '#ffffff', k: 0.8 * u }, dither: 0.92 * (1 - u) };
      } else opt = { flip, scale, skin: this.skin, alpha: this.alpha, aura, outline: o.outline || null };
      this.atlas.draw(g, pose, frame, sx, sy, opt);
      if (fallbackBlock && this.mode === 'act') this._blockArc(g, sx, sy, ow.facing || 1, scale);
    }
    // 没有 block 帧时：身前一道光环色半透明竖弧
    _blockArc(g, sx, sy, f, sc = 1) {
      const cx = Math.round(sx + f * 10 * sc), cy = Math.round(sy - 22 * sc), ga = g.globalAlpha;
      g.globalAlpha = ga * (0.45 + 0.15 * Math.sin((this._clk || 0) * 20));
      g.fillStyle = this.color;
      for (let a = -70; a <= 70; a += 6) {
        const r = a * Math.PI / 180;
        g.fillRect(cx + Math.round(Math.cos(r) * 5 * sc * f), cy + Math.round(Math.sin(r) * 16 * sc), 1, 2);
      }
      g.globalAlpha = ga;
    }
    // 像素层（world.drawPixel 'mid' 调）：远程替身的触须连线、隐者之紫的藤蔓
    drawPixel(P, camX, camY) {
      const ow = this.owner, f = ow.facing || 1;
      if (this.kind === 'vine') { this._drawVine(P, camX, camY); return; }
      if (this.mode === 'hidden' || this.link() !== 'tendril') return;
      const ax = Math.round(ow.x + f * 3 - camX), ay = Math.round(ow.y - ow.z - ow.topPx() * ow.scale * 0.6 - camY);
      const c = this.chest(), bx = Math.round(this.x - f * 2 * (ow.scale || 1) - camX), by = Math.round(c.y - c.z - camY);
      let grow = 1;
      if (this._ap) grow = Math.min(1, this._ap.t / this._ap.dur);
      else if (this.mode === 'recall') grow = 1 - Math.min(1, this._rc.t / this._rc.dur);
      if (grow <= 0) return;
      const t = G.clk ? G.clk.flow : 0;
      if (G.FX && G.FX.tendrils) G.FX.tendrils(P, [[ax, ay], [bx, by]], t, { colour: this.color, wiggle: 1.0, seed: ow.uid % 97, grow });
      else if (G.px && G.px.line) G.px.line(P, ax, ay, ax + (bx - ax) * grow, ay + (by - ay) * grow, this.color, 0.8);
    }
    _drawVine(P, camX, camY) {
      const v = this._vine;
      if (!v) return;
      const ow = this.owner, f = ow.facing || 1, t = this._clk;
      let u = Math.min(1, (t - v.t0) / VINE_GROW);
      if (v.out == null && !v.act && t - v.t0 >= VINE_GROW + v.hold) v.out = v.t0 + VINE_GROW + v.hold;
      if (v.out == null && v.act && (this.mode !== 'act' || v.snap) && t - v.t0 >= VINE_GROW + v.hold) v.out = t;
      if (v.out != null) {
        const r = Math.min(1, (t - v.out) / VINE_GROW);
        u = Math.min(u, 1 - r);
        if (r >= 1) { this._vine = null; return; }
      }
      if (u <= 0) return;
      // 从乔瑟夫伸出去的手上长（point 帧的手在身前 ≈ 12 px、离脚底 30 px；以前从胸口 6 px 处长）
      // 12 / 30 / len / dy 都是原尺寸的像素，人物缩了 ck 倍，手的位置和藤蔓长度一起缩
      const k = ow.scale * ck();
      const x0 = Math.round(ow.x + f * 12 * k - camX), y0 = Math.round(ow.y - ow.z - 30 * k - camY);
      const x1 = Math.round(x0 + f * v.len * k * u), y1 = Math.round(y0 + v.dy * k * u);
      if (G.FX && G.FX.vines) G.FX.vines(P, x0, y0, x1, y1, t, v.t0 - 1, v.t0 - 1, { colour: 'purple', strands: v.thorns ? 3 : 2, seed: ow.uid % 97, wiggle: 2 });
      else if (G.px && G.px.line) { G.px.line(P, x0, y0, x1, y1, '#9a4ce0', 1, 2); G.px.line(P, x0, y0 + 1, x1, y1 + 1, '#5a2a90', 1, 1); }
    }
    dispose() { this.hide(); }
  }
  G.Stand = Stand;
})();
