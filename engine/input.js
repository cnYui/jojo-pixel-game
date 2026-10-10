// 输入：键盘 / 指针 → 动作名；DOM 事件先排队、每个逻辑步开头落地；按键缓冲与按键日志按 world 时钟（顿帧不吞键）；确认键锁（技术约定 §4.3.1–4.3.4）
'use strict';
(function () {
  const G = window.G;

  // 键表（§4.3.1，和规划 §3.1 是同一张）
  const KEYMAP = {
    ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right',
    ArrowUp: 'up', KeyW: 'up', ArrowDown: 'down', KeyS: 'down',
    KeyJ: 'attack', KeyZ: 'attack',
    KeyK: 'dodge', KeyX: 'dodge',
    KeyL: 'guard', KeyC: 'guard',
    KeyU: 'special', KeyV: 'special',
    KeyQ: 'swap', Tab: 'swap',
    Digit1: 'lead1', Digit2: 'lead2', Digit3: 'lead3', Digit4: 'lead4', Digit5: 'lead5', Digit6: 'lead6',
    Enter: 'ok', NumpadEnter: 'ok', Space: 'ok', KeyE: 'ok',
    Escape: 'pause', KeyP: 'pause',
    Backspace: 'back',
  };
  const BUF_KEEP = 0.3;     // 缓冲保留 0.3 s 世界时间
  const LOG_KEEP = 1.2;     // 按键日志每个动作保留最近 1.2 s 世界时间

  const pending = [];                          // 两步之间收到的事件：{ k: 'down'|'up'|'hit'|'tap', a, src, ui, cv }
  const holders = Object.create(null);         // 动作 → Set(按着它的来源：'key:KeyJ'、'touch' …)

  const I = (G.input = {
    KEYMAP,
    down: {},
    hits: {},
    tap: null,            // 这一步里点了画面：UI 坐标 {x, y}
    tapCanvas: null,      // 同一下的世界画布坐标
    okLockUntil: 0,       // ui 时钟
    buf: [],              // [{ a, t: clk.world, used }]
    log: {},              // 动作 → [按下时刻（clk.world）…]
    last: {},             // 动作 → 最近一次按下的 clk.world

    isDown(a) { return !!this.down[a]; },
    hit(a) { return !!this.hits[a]; },
    consume(a) { this.hits[a] = false; },
    // 剧情 / 菜单的确认：只认 Enter / 空格 / E / 点击（D8：J 不推进），并受 lockOk 约束
    okHit() { return !!this.hits.ok && G.clk.ui >= this.okLockUntil; },
    consumeOk() { this.hits.ok = false; },
    lockOk(sec) { this.okLockUntil = Math.max(this.okLockUntil, G.clk.ui + sec); },
    okLocked() { return G.clk.ui < this.okLockUntil; },
    // 只给 QTE 连按 / 拳拳相对用
    mashHit() { return !!(this.hits.attack || this.hits.ok); },

    // 最近 win 秒内（world 时钟）有没有“还没被 take 的”按下
    buffered(a, win = 0.2) {
      const now = G.clk.world;
      for (const e of this.buf) if (e.a === a && !e.used && now - e.t <= win + 1e-9) return true;
      return false;
    },
    // 同上，有就消耗（最早的那一下）并返回 true
    take(a, win = 0.2) {
      const now = G.clk.world;
      for (const e of this.buf) {
        if (e.a === a && !e.used && now - e.t <= win + 1e-9) { e.used = true; return true; }
      }
      return false;
    },
    // 最近 win 秒内（world 时钟）按下的次数（按键日志，不受 take 影响；连打判定用）
    count(a, win) {
      const L = this.log[a];
      if (!L) return 0;
      const now = G.clk.world;
      let n = 0;
      for (const t of L) if (now - t <= win + 1e-9) n++;
      return n;
    },
    lastPress(a) { const v = this.last[a]; return v === undefined ? -Infinity : v; },
    // 最近一下还没被 take 的 a 是不是不到 win 秒前按的（有组合键的角色：单键先等 4/60 s 看另一个键来不来）
    fresh(a, win = 4 / 60) {
      const now = G.clk.world;
      for (let i = this.buf.length - 1; i >= 0; i--) {
        const e = this.buf[i];
        if (e.a === a && !e.used) return now - e.t < win - 1e-9;
      }
      return false;
    },
    // 组合键（§4.3.3 chords）：a、b 都有没被 take 的按下（bufWin 内），且两次按下相差 ≤ win（按 lastPress 比）→ 两个缓冲都消耗，返回 true
    chord(a, b, win = 4 / 60, bufWin = 0.2) {
      if (!this.buffered(a, bufWin) || !this.buffered(b, bufWin)) return false;
      if (Math.abs(this.lastPress(a) - this.lastPress(b)) > win + 1e-9) return false;
      this.take(a, bufWin);
      this.take(b, bufWin);
      return true;
    },

    // ---- 给 touch.js 等别的输入来源用（同样先排队，下一步开头落地）
    press(a, src = 'ext') { pending.push({ k: 'down', a, src }); },
    release(a, src = 'ext') { pending.push({ k: 'up', a, src }); },
    inject(a) { pending.push({ k: 'hit', a }); },                // 只算一次按下，不改 down（菜单长按连发用）
    tapAt(e) { pending.push({ k: 'tap', ui: G.toUI(e), cv: G.toCanvas(e) }); },

    beginStep() {
      const now = G.clk.world;
      const rec = !(G.scene && G.scene.frozen);              // 开着菜单（世界冻结）时不进战斗缓冲，免得关菜单后自己出招
      for (let i = 0; i < pending.length; i++) {
        const ev = pending[i];
        if (ev.k === 'down') {
          const set = holders[ev.a] || (holders[ev.a] = new Set());
          const was = set.size > 0;
          set.add(ev.src);
          if (!was) { this.hits[ev.a] = true; if (rec) record(ev.a, now); }
          this.down[ev.a] = true;
        } else if (ev.k === 'up') {
          const set = holders[ev.a];
          if (set) set.delete(ev.src);
          if (!set || set.size === 0) this.down[ev.a] = false;
        } else if (ev.k === 'hit') {
          this.hits[ev.a] = true;
          if (rec) record(ev.a, now);
        } else if (ev.k === 'tap') {
          this.hits.ok = true;
          this.tap = ev.ui;
          this.tapCanvas = ev.cv;
        }
      }
      pending.length = 0;
      // 过期清理（world 时钟停着时什么都不过期）
      if (this.buf.length && now - this.buf[0].t > BUF_KEEP) this.buf = this.buf.filter((e) => now - e.t <= BUF_KEEP);
      for (const a in this.log) {
        const L = this.log[a];
        if (L.length && now - L[0] > LOG_KEEP) this.log[a] = L.filter((t) => now - t <= LOG_KEEP);
      }
    },
    endStep() {
      this.hits = {};
      this.tap = null;
      this.tapCanvas = null;
    },
    clear() {
      this.down = {};
      this.hits = {};
      this.tap = this.tapCanvas = null;
      this.buf = [];
      this.log = {};
      for (const a in holders) holders[a].clear();
      pending.length = 0;
    },
  });
  function record(a, now) {
    I.buf.push({ a, t: now, used: false });
    (I.log[a] || (I.log[a] = [])).push(now);
    I.last[a] = now;
  }

  // ---------------------------------------------------------------- DOM 事件
  const unlockAudio = () => {
    const A = G.audio;
    if (A && (!A.unlocked || A.wantGesture)) A.unlock();
  };
  addEventListener('keydown', (e) => {
    unlockAudio();
    if (e.ctrlKey || e.metaKey || e.altKey) return;            // 浏览器 / 系统快捷键不抢
    const a = KEYMAP[e.code];
    if (!a) return;
    e.preventDefault();                                         // Tab 必须拦（§4.3.1）
    if (e.repeat) return;                                       // 系统按键重复不算新按下
    pending.push({ k: 'down', a, src: 'key:' + e.code });
  });
  addEventListener('keyup', (e) => {
    const a = KEYMAP[e.code];
    if (!a) return;
    e.preventDefault();
    pending.push({ k: 'up', a, src: 'key:' + e.code });
  });
  addEventListener('blur', () => I.clear());
  G.screen.addEventListener('pointerdown', (e) => {
    unlockAudio();
    pending.push({ k: 'tap', ui: G.toUI(e), cv: G.toCanvas(e) });
  });
  // 浏览器要求先有一次用户手势才能出声：五种事件都试（手机上手指抬起才算数）
  ['pointerdown', 'pointerup', 'touchend', 'click'].forEach((n) => addEventListener(n, unlockAudio, true));
})();
