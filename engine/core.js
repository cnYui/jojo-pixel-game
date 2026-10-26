// 底座：G 命名空间、常量、工具（源码 engine/core.py 移植）、三个时钟、主循环、场景、等待、黑幕 / 闪色 / 震屏 / 顿帧 / 慢放、两层画布与合成、镜头与坐标换算、设置与存储、G.dbg 基础（技术约定 §2、§4.1）
'use strict';
(function () {
  const G = (window.G = {});
  G.W = 320;
  G.H = 180;
  G.UW = 640;
  G.UH = 360;
  G.D = window.GAME_DATA;          // data/data_meta.js 没加载时是 undefined（main.js 的 boot 会提示先构建）

  // ================================================================ 工具（core.py 移植，技术约定 §4.1.1）
  G.clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  G.lerp = (a, b, t) => a + (b - a) * t;
  G.mod = (a, n) => ((a % n) + n) % n;
  G.rand = (a = 0, b = 1) => a + Math.random() * (b - a);
  G.pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
  G.sign = (v) => (v < 0 ? -1 : v > 0 ? 1 : 0);
  // 固定种子的随机数（mulberry32，同银魂 core.js:28-36）
  G.prng = (seed) => {
    let a = (seed * 2654435761) >>> 0 || 1;
    return () => {
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };
  // core.py hash01：FNV 变体。非整数参数先 round(x·997)（JS 分不清 3 和 3.0，只要求自身确定）
  G.hash01 = function () {
    let h = 2166136261;
    for (let i = 0; i < arguments.length; i++) {
      const x = arguments[i];
      const v = Number.isInteger(x) ? x : Math.round(x * 997);
      h = (h ^ (v >>> 0)) >>> 0;
      h = Math.imul(h, 16777619) >>> 0;
      h = (h ^ (h >>> 13)) >>> 0;
      h = Math.imul(h, 0x5bd1e995) >>> 0;
      h = (h ^ (h >>> 15)) >>> 0;
    }
    return h / 4294967296;
  };
  G.hrange = function (a, b) {
    return a + (b - a) * G.hash01.apply(null, Array.prototype.slice.call(arguments, 2));
  };
  G.noise1 = (x, seed = 0) => {
    const i = Math.floor(x), f = x - i;
    const a = G.hash01(i, seed) * 2 - 1, b = G.hash01(i + 1, seed) * 2 - 1;
    const u = f * f * (3 - 2 * f);
    return a + (b - a) * u;
  };
  // core.py ease(u, kind)：linear in out io in3 out3 back bounce elastic step
  G.ease = function (u, kind = 'io') {
    u = u < 0 ? 0 : u > 1 ? 1 : u;
    switch (kind) {
      case 'linear': return u;
      case 'in': return u * u;
      case 'out': return 1 - (1 - u) * (1 - u);
      case 'io': return u * u * (3 - 2 * u);
      case 'in3': return u * u * u;
      case 'out3': return 1 - (1 - u) * (1 - u) * (1 - u);
      case 'back': { const s = 1.70158, v = u - 1; return v * v * ((s + 1) * v + s) + 1; }
      case 'bounce': {
        const n1 = 7.5625, d1 = 2.75;
        if (u < 1 / d1) return n1 * u * u;
        if (u < 2 / d1) { u -= 1.5 / d1; return n1 * u * u + 0.75; }
        if (u < 2.5 / d1) { u -= 2.25 / d1; return n1 * u * u + 0.9375; }
        u -= 2.625 / d1;
        return n1 * u * u + 0.984375;
      }
      case 'elastic':
        if (u === 0 || u === 1) return u;
        return Math.pow(2, -10 * u) * Math.sin(((u * 10 - 0.75) * (2 * Math.PI)) / 3) + 1;
      case 'step': return u >= 1 ? 1 : 0;
      default: return u;
    }
  };
  // 银魂兼容别名（G.ease.out(t) 这种写法）：out = out3、in = in3、inOut = 三次、outBack = back
  const cl01 = (t) => (t < 0 ? 0 : t > 1 ? 1 : t);
  G.ease.out = (t) => { t = cl01(t); return 1 - (1 - t) * (1 - t) * (1 - t); };
  G.ease.in = (t) => { t = cl01(t); return t * t * t; };
  G.ease.inOut = (t) => { t = cl01(t); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  G.ease.outBack = (t) => G.ease(t, 'back');
  G.prog = (t, t0, t1) => (t1 <= t0 ? (t >= t1 ? 1 : 0) : cl01((t - t0) / (t1 - t0)));
  G.tw = (t, t0, t1, a, b, kind = 'io') => G.lerp(a, b, G.ease(G.prog(t, t0, t1), kind));
  // 关键帧：pts = [[t0, v0], [t1, v1], …]，v 可以是数组
  G.keys = (t, pts, kind = 'io') => {
    if (t <= pts[0][0]) return pts[0][1];
    for (let i = 0; i + 1 < pts.length; i++) {
      const ta = pts[i][0], va = pts[i][1], tb = pts[i + 1][0], vb = pts[i + 1][1];
      if (t <= tb) {
        const u = G.ease(G.prog(t, ta, tb), kind);
        if (Array.isArray(va)) return va.map((x, j) => G.lerp(x, vb[j], u));
        return G.lerp(va, vb, u);
      }
    }
    return pts[pts.length - 1][1];
  };
  G.stepped = (t, fps = 12) => Math.floor(t * fps) / fps;
  G.wobble = (t, amp = 1, freq = 1, phase = 0) => amp * Math.sin(2 * Math.PI * (freq * t + phase));

  // core.py 的颜色表 C
  G.C = {
    black: [0, 0, 0], ink: [26, 16, 32], white: [255, 255, 255], cream: [239, 230, 210],
    night0: [8, 6, 22], night1: [20, 16, 52], night2: [40, 30, 90], night3: [70, 50, 130],
    dusk0: [60, 20, 70], dusk1: [150, 40, 90], dusk2: [240, 110, 80], dusk3: [255, 190, 90],
    sky0: [60, 120, 220], sky1: [110, 170, 240], sky2: [180, 220, 255],
    sea0: [10, 40, 90], sea1: [20, 80, 150], sea2: [60, 140, 200],
    sand0: [180, 110, 50], sand1: [225, 160, 80], sand2: [250, 210, 130],
    grass0: [30, 90, 50], grass1: [60, 150, 70],
    stone0: [60, 55, 70], stone1: [110, 100, 115], stone2: [170, 160, 165],
    red: [224, 48, 60], dred: [144, 24, 40], orange: [245, 144, 42],
    yellow: [255, 216, 60], gold: [200, 154, 32], green: [60, 192, 96],
    dgreen: [30, 122, 60], emerald: [40, 230, 140], cyan: [72, 216, 232],
    blue: [60, 100, 220], navy: [30, 40, 96], purple: [154, 76, 224],
    dpurple: [90, 40, 144], magenta: [240, 88, 180], pink: [255, 150, 200],
    menace: [170, 60, 220],
  };
  const rgbCache = new Map();
  // '#rrggbb' | '#rgb' | [r,g,b(,a)] | C 表里的名字 → [r,g,b]
  G.rgbOf = (c) => {
    if (Array.isArray(c)) return c.length === 3 ? c : [c[0] | 0, c[1] | 0, c[2] | 0];
    if (c == null) return [0, 0, 0];
    let v = rgbCache.get(c);
    if (v) return v;
    if (G.C[c]) v = G.C[c];
    else {
      let s = String(c).replace(/^#/, '');
      if (s.length === 3) s = s[0] + s[0] + s[1] + s[1] + s[2] + s[2];
      const n = parseInt(s.slice(0, 6), 16);
      v = Number.isNaN(n) ? [0, 0, 0] : [(n >> 16) & 255, (n >> 8) & 255, n & 255];
    }
    rgbCache.set(c, v);
    return v;
  };
  const hex2 = (n) => (n < 16 ? '0' : '') + n.toString(16);
  G.mixHex = (a, b, k) => {
    const x = G.rgbOf(a), y = G.rgbOf(b), u = cl01(k);
    return '#' + hex2(Math.round(x[0] + (y[0] - x[0]) * u)) + hex2(Math.round(x[1] + (y[1] - x[1]) * u)) + hex2(Math.round(x[2] + (y[2] - x[2]) * u));
  };

  // ================================================================ 存储与设置（§4.1.6）
  // 读写都走内存镜像 mem（同步，调用方不用改）。写入时立刻落 localStorage，再异步落小红书小工具容器自带的 Storage
  // （window.xhs.miniTool.setStorage，客户端 9.46+）：容器里的 localStorage 不保证留得住，两边都写，启动时以“最后写入时间”新的那份为准。
  // 容器的 Storage 只有异步接口，所以启动时回读一次（hydrate），限时——接口卡住不能把游戏拦在载入界面；
  // 用能力检测（有没有 setStorage / getStorage），不按 UA / 机型分支。任何一边写失败都不抛错，状态给存档界面看（status）。
  const PFX = 'jojo-', STAMP_KEY = 'jojo-save-t', XHS_KEY = 'jojo-save', FLUSH_MS = 400, HYDRATE_MS = 1500, XHS_CALL_MS = 5000;
  const mem = {};                       // 键（不带前缀）→ JSON 字符串
  let stamp = 0;                        // 最后一次写入的时间（ms）；本机和容器各存一份，比大小决定谁覆盖谁
  const loadHooks = [];
  const st = { local: null, xhs: null };    // true = 最近一次写成功，false = 失败，null = 还没试过 / 没有这条通道
  const xhsApi = () => {
    const m = window.xhs && window.xhs.miniTool;
    return m && typeof m.setStorage === 'function' && typeof m.getStorage === 'function' ? m : null;
  };
  // 容器接口可能同步抛错、返回 undefined、或者永远不返回：都当成“这次失败”，不能卡住后面的写入
  const callXhs = (fn, ms) => new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('timeout')), ms);
    try { Promise.resolve(fn()).then(r => { clearTimeout(timer); resolve(r); }, e => { clearTimeout(timer); reject(e); }); }
    catch (e) { clearTimeout(timer); reject(e); }
  });
  (function loadLocal() {
    try {
      localStorage.setItem(PFX + 'probe', '1'); localStorage.removeItem(PFX + 'probe');   // 隐私模式的 Safari 读得出、写不进：先探一下
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.indexOf(PFX) === 0 && k !== STAMP_KEY && k !== XHS_KEY) mem[k.slice(PFX.length)] = localStorage.getItem(k);
      }
      stamp = +localStorage.getItem(STAMP_KEY) || 0;
      st.local = true;
    } catch (e) { st.local = false; }
  })();
  const writeLocal = (key, json) => {
    try {
      if (json == null) localStorage.removeItem(PFX + key); else localStorage.setItem(PFX + key, json);
      localStorage.setItem(STAMP_KEY, String(stamp));
      st.local = true;
    } catch (e) { st.local = false; }    // 隐私模式 / 存满了：内存里的这次有效
  };
  let flushTimer = 0, flushing = false, flushAgain = false, dirty = false;
  function flush() {
    if (flushTimer) { clearTimeout(flushTimer); flushTimer = 0; }
    const api = xhsApi();
    if (!api || !dirty) return;
    if (flushing) { flushAgain = true; return; }
    flushing = true; dirty = false;
    callXhs(() => api.setStorage({ key: XHS_KEY, data: JSON.stringify({ v: 1, t: stamp, keys: mem }) }), XHS_CALL_MS)
      .then(() => { st.xhs = true; }, () => { st.xhs = false; dirty = true; })    // 失败的留着：下一次写入或切后台时再试
      .then(() => { flushing = false; if (flushAgain) { flushAgain = false; schedule(); } });
  }
  function schedule() {
    if (!xhsApi()) return;
    dirty = true;
    if (!flushTimer) flushTimer = setTimeout(flush, FLUSH_MS);
  }
  const notify = () => loadHooks.forEach(fn => { try { fn(); } catch (e) { console.error(e); } });
  let hydrating = null;
  function hydrate() {
    const api = xhsApi();
    if (!api) return Promise.resolve();
    return callXhs(() => api.getStorage({ key: XHS_KEY }), HYDRATE_MS).then(r => r, () => null).then(r => {
      if (r) st.xhs = true;      // 能读回来就说明这条通道是通的（没写过时 data 是 null，也算）
      let o = null;
      try { o = r && r.data ? JSON.parse(r.data) : null; } catch (e) { o = null; }
      const ok = o && o.v === 1 && o.keys && typeof o.keys === 'object' && +o.t > 0;
      if (ok && +o.t > stamp) {
        // 容器里的更新（或者本机浏览器存储被清空了）：以容器为准，整份换过来再回写本机
        const old = Object.keys(mem);
        old.forEach(k => { delete mem[k]; });
        stamp = +o.t;
        Object.keys(o.keys).forEach(k => { if (typeof o.keys[k] === 'string') mem[k] = o.keys[k]; });
        Object.keys(mem).forEach(k => writeLocal(k, mem[k]));
        old.forEach(k => { if (mem[k] == null) writeLocal(k, null); });    // 容器那份里没有的键（清除存档删掉的）本机也要删
        notify();
        if (G.dbg && G.dbg.ev) G.dbg.ev('store_hydrate', { from: 'xhs', keys: Object.keys(mem).length });
      } else if (Object.keys(mem).length && (!ok || +o.t < stamp)) schedule();   // 本机的更新、或容器里还没有：补写过去
    });
  }
  G.store = {
    get(key, def) {
      try { return mem[key] == null ? def : JSON.parse(mem[key]); } catch (e) { return def; }
    },
    set(key, val) {
      let json;
      try { json = JSON.stringify(val); } catch (e) { return; }
      if (json === undefined) return;
      mem[key] = json; stamp = Date.now();
      writeLocal(key, json); schedule();
    },
    remove(key) {
      if (mem[key] == null) return;
      delete mem[key]; stamp = Date.now();
      writeLocal(key, null); schedule();
    },
    // 启动时调一次（可重复调，只回读一次）：返回的 Promise 最多等 HYDRATE_MS，超时 / 失败都照常 resolve，游戏不会被它拦住
    hydrate() {
      if (!hydrating) hydrating = hydrate().then(() => {}, () => {});
      return hydrating;
    },
    flush,                                                // 切后台 / 关页面前立刻写，不等 400 ms 的合并
    onLoad(fn) { loadHooks.push(fn); },                   // 存档被换掉（容器回读、清除存档）后各模块重新读
    reload: notify,
    // 存放状态，给存档界面看：local / xhs = 最近一次写成功 / 失败 / 没试过（null）；hasXhs = 有没有容器存储接口
    status() { return { local: st.local, xhs: st.xhs, hasXhs: !!xhsApi(), stamp }; },
  };
  const SET_DEF = { reduceFlash: false, musicVol: 0.8, sfxVol: 0.9, grunts: false, mashHold: false, touchSize: 1 };
  G.settings = Object.assign({}, SET_DEF);
  function loadSettings() {
    const s = G.store.get('settings', null);
    if (!s || typeof s !== 'object') return;
    for (const k in SET_DEF) if (typeof s[k] === typeof SET_DEF[k]) G.settings[k] = s[k];
  }
  loadSettings();
  G.store.onLoad(loadSettings);
  Object.defineProperty(G.settings, 'save', {
    enumerable: false,
    value() {
      const o = {};
      for (const k in SET_DEF) o[k] = G.settings[k];
      G.store.set('settings', o);
    },
  });

  // ================================================================ 调试基础（§4.1.7）
  G.dbg = {
    shot: null,
    events: [],
    counts: {},
    ev(type, data) {
      const e = Object.assign({ t: G.clk.ui, type }, data);
      this.events.push(e);
      if (this.events.length > 400) this.events.shift();
      this.counts[type] = (this.counts[type] || 0) + 1;
      // 成就（engine/achievements.js）只在这里借道这几种已有事件；判空 + 吞掉异常，成就出问题不能把游戏一起带走
      if (G.ach && G.ach.dbgHook) { try { G.ach.dbgHook(type, e); } catch (err) { /* 忽略：成就记不上不挡玩法 */ } }
    },
    resetCounts() { this.counts = {}; },
    animFallbacks: new Set(), missingImg: new Set(), missingSfx: new Set(), missingGlyph: new Set(), missingHead: new Set(),
    fps: { avg: 60, min: 60 },
    autotest: /[?&]autotest=1/.test(location.search),
    hold: false,                       // 测试用：true 时主循环只画不走，由 tick() 手动推进
    tick(n = 1, dt = 1 / 60) {         // 测试用：同步推进 n 个逻辑步，再画一帧
      for (let i = 0; i < n; i++) safeStep(dt);
      safeRender();
    },
  };

  // ================================================================ 时钟、等待、场景（§2.3、§4.1.2–4.1.3）
  G.clk = { ui: 0, world: 0, flow: 0 };
  const waits = { ui: [], world: [] };
  let waiters = [];
  const pending = new Set();
  G.runId = 0;
  G.cancelled = (e) => !!(e && e.name === 'RunCancelled');
  G.cancelIgnore = (e) => { if (!G.cancelled(e)) console.error(e); };
  // 所有剧情等待属于同一轮运行，换章时必须让整条 await 链退出。
  G.runPromise = (executor) => new Promise((resolve, reject) => {
    const entry = { id: G.runId, reject, cleanup: null, settled: false, cleaned: false };
    pending.add(entry);
    const clean = () => {
      if (entry.cleaned || typeof entry.cleanup !== 'function') return;
      entry.cleaned = true;
      entry.cleanup();
    };
    const finish = (fn, value) => {
      if (entry.settled) return;
      entry.settled = true;
      pending.delete(entry);
      try { clean(); } catch (e) { reject(e); return; }
      fn(value);
    };
    entry.cancel = error => finish(reject, error);
    try {
      entry.cleanup = executor(v => finish(resolve, v), e => finish(reject, e));
      // 同步完成的执行器也可能在返回时才交出资源释放函数。
      if (entry.settled) clean();
    }
    catch (e) { finish(reject, e); }
  });
  G.cancelRun = () => {
    G.runId++;
    const error = new Error('这一轮剧情已结束'); error.name = 'RunCancelled';
    for (const entry of Array.from(pending)) {
      if (entry.id === G.runId) continue;
      entry.cancel(error);
    }
    waits.ui = []; waits.world = []; waiters = [];
    fadeTw = null; flashTw = null; G.flashA = 0;
  };
  G.wait = (sec, clock = 'world') => G.runPromise((res) => {
    const c = clock === 'ui' ? 'ui' : 'world';
    waits[c].push({ at: G.clk[c] + (sec > 0 ? sec : 0), res });
  });
  G.until = (fn) => G.runPromise((res) => { waiters.push({ fn, res }); });
  G.defer = (sec, fn, clock = 'world') => G.wait(sec, clock).then(fn).catch(G.cancelIgnore);
  G.suspended = false;
  G.scene = null;
  G.setScene = (s) => {
    const old = G.scene;
    if (old && old.leave) old.leave();
    G.scene = s;
    if (s && s.enter) s.enter();
  };
  function settle(c) {
    const list = waits[c];
    if (!list.length) return;
    const now = G.clk[c] + 1e-9;
    const keep = [];
    for (const w of list) { if (now >= w.at) w.res(); else keep.push(w); }
    waits[c] = keep;
  }
  function checkWaiters() {
    if (!waiters.length) return;
    const list = waiters;
    waiters = [];
    for (const w of list) {
      let ok;
      try { ok = w.fn(); } catch (e) { report('until', e); ok = true; }
      if (ok) w.res(); else waiters.push(w);
    }
  }

  // ================================================================ 画面效果（§4.1.4）
  G.fadeA = 0;
  G.flashA = 0;
  G.flashColor = '#fff';
  G.hitStopAll_t = 0;
  G.slowAllK = 1;
  G.slowAllT = 0;
  let fadeTw = null, flashTw = null;
  G.fade = (to, dur = 0.5) => G.runPromise((res) => {
    if (fadeTw) { const old = fadeTw; fadeTw = null; old.res(); }      // 被新的黑幕顶掉：旧的照样 resolve，免得剧情卡住
    if (!(dur > 0)) { G.fadeA = to; res(); return; }
    fadeTw = { from: G.fadeA, to, t: 0, dur, res };
  });
  G.flash = (dur = 0.25, peak = 1, color = '#fff') => {
    if (G.settings.reduceFlash) peak *= 0.35;
    flashTw = { t: 0, dur: Math.max(2 / 60, dur), peak };              // 一帧闪也至少 2/60 s（§0.2 第 6 条）
    G.flashColor = color;
    G.flashA = peak;
  };
  G.shake = (amp = 2, dur = 0.25, o = {}) => {
    const c = G.cam;
    if (amp >= c.shakeNow()) {
      c.shakeAmp = amp;
      c.shakeDur = Math.max(1 / 60, dur);
      c.shakeT = 0;
      c.shakeDir = o.dir === 'x' ? 'x' : 'both';
      c.shakeDecay = o.decay !== false;
    }
  };
  G.hitStopAll = (sec) => { G.hitStopAll_t = Math.max(G.hitStopAll_t, Math.min(sec, 0.5)); };
  G.slowAll = (k, sec) => {
    G.slowAllK = Math.min(G.slowAllK, k);
    G.slowAllT = Math.max(G.slowAllT, sec);
  };
  function tickFx(dt) {
    if (fadeTw) {
      fadeTw.t += dt;
      G.fadeA = G.lerp(fadeTw.from, fadeTw.to, Math.min(1, fadeTw.t / fadeTw.dur));
      if (fadeTw.t >= fadeTw.dur - 1e-9) { const f = fadeTw; fadeTw = null; G.fadeA = f.to; f.res(); }
    }
    if (flashTw) {
      flashTw.t += dt;
      G.flashA = flashTw.peak * Math.max(0, 1 - flashTw.t / flashTw.dur);
      if (flashTw.t >= flashTw.dur) { flashTw = null; G.flashA = 0; }
    }
    const c = G.cam;
    if (c.shakeT < c.shakeDur) c.shakeT += dt;
    if (c.bumpT < c.bumpDur) c.bumpT += dt;
  }

  // ================================================================ 画布（§2.4）
  G.mkCanvas = (w, h, read = false) => {
    const c = document.createElement('canvas');
    c.width = w;
    c.height = h;
    const g = read ? c.getContext('2d', { willReadFrequently: true }) : c.getContext('2d');
    g.imageSmoothingEnabled = false;
    c.g = g;
    return c;
  };
  G.wv = G.mkCanvas(G.W, G.H, true);         // 世界层（要读像素）
  G.wg = G.wv.g;
  G.uv = G.mkCanvas(G.UW, G.UH);             // UI 层（透明底，不读像素）
  G.ug = G.uv.g;
  G.screen = document.getElementById('screen');
  if (!G.screen) {
    G.screen = document.createElement('canvas');
    G.screen.id = 'screen';
    (document.body || document.documentElement).appendChild(G.screen);
  }
  G.sctx = G.screen.getContext('2d');
  G.scale = 2;
  G.resize = function () {
    const dpr = window.devicePixelRatio || 1;
    let s = Math.floor(Math.min((innerWidth * dpr) / G.W, (innerHeight * dpr) / G.H));
    const fit = s < 2;                        // 窗口太小（物理宽 < 640）
    s = Math.max(2, s);
    G.scale = s;
    if (G.screen.width !== G.W * s) G.screen.width = G.W * s;   // 位图：严格整数倍
    if (G.screen.height !== G.H * s) G.screen.height = G.H * s;
    let cssW = (G.W * s) / dpr, cssH = (G.H * s) / dpr;
    if (fit) { const k = Math.min(innerWidth / cssW, innerHeight / cssH); cssW *= k; cssH *= k; }   // 极小窗口才非整数缩小
    G.screen.style.width = cssW + 'px';
    G.screen.style.height = cssH + 'px';
    G.sctx.imageSmoothingEnabled = false;
  };
  addEventListener('resize', G.resize);
  addEventListener('orientationchange', () => setTimeout(G.resize, 250));
  if (window.visualViewport) visualViewport.addEventListener('resize', G.resize);
  ['fullscreenchange', 'webkitfullscreenchange'].forEach((n) => document.addEventListener(n, G.resize));
  G.resize();
  // 指针事件 → UI 坐标（0..640 × 0..360）/ 世界画布坐标（0..320 × 0..180）
  G.toUI = (e) => {
    const r = G.screen.getBoundingClientRect();
    return { x: ((e.clientX - r.left) * G.UW) / r.width, y: ((e.clientY - r.top) * G.UH) / r.height };
  };
  G.toCanvas = (e) => {
    const r = G.screen.getBoundingClientRect();
    return { x: ((e.clientX - r.left) * G.W) / r.width, y: ((e.clientY - r.top) * G.H) / r.height };
  };

  // ================================================================ 镜头（§2.6）
  G.cam = {
    x: 0, y: 0, zoom: null,
    shakeAmp: 0, shakeDur: 0, shakeT: 0, shakeDir: 'both', shakeDecay: true,
    bumpK: 0, bumpT: 0, bumpDur: 0,
    shakeNow() {                            // 当前震屏幅度（线性衰减；decay false 时恒定）
      if (this.shakeT >= this.shakeDur || this.shakeAmp <= 0) return 0;
      return this.shakeDecay ? this.shakeAmp * (1 - this.shakeT / this.shakeDur) : this.shakeAmp;
    },
    bumpNow() { return this.bumpT < this.bumpDur ? this.bumpK * (1 - this.bumpT / this.bumpDur) : 0; },
    bump(k = 0.08, dur = 0.12) {
      if (k >= this.bumpNow()) { this.bumpK = k; this.bumpT = 0; this.bumpDur = Math.max(1 / 60, dur); }
    },
    // 世界画布上要显示的框 {x, y, w, h}（含推镜头与震屏；照原片 s10 camera()）
    box() {
      // 插入画面（特写 / 切入）按整张 320×180 构图：不吃剧情推镜（2026-10-09 序章小指特写被推镜 1.25 放大、切掉半个人）；震屏 / 冲击照旧
      const z = G.world && G.world.insert ? null : this.zoom;
      let k = (z ? z.k : 1) * (1 + this.bumpNow());
      const amp = this.shakeNow();
      if (amp > 0) {
        const m = Math.ceil(amp) + 1, kk = 1 + (2 * m + 2) / 180;   // 抖的时候自动微推，免得露黑边
        if (k < kk) k = kk;
      }
      const w = G.W / k, h = G.H / k;
      let cx = z ? z.x - this.x : G.W / 2, cy = z ? z.y - this.y : G.H / 2;
      if (amp > 0) {
        const f = Math.floor(G.clk.ui * 30);
        cx += Math.round((G.hash01(f, 7, 1) * 2 - 1) * amp);
        if (this.shakeDir !== 'x') cy += Math.round((G.hash01(f, 7, 2) * 2 - 1) * amp) * 0.6;
      }
      cx = w >= G.W ? G.W / 2 : G.clamp(cx, w / 2, G.W - w / 2);
      cy = h >= G.H ? G.H / 2 : G.clamp(cy, h / 2, G.H - h / 2);
      return { x: cx - w / 2, y: cy - h / 2, w, h };
    },
    w2s(wx, wy, wz = 0) { return { x: wx - this.x, y: wy - wz - this.y }; },
    s2u(sx, sy) {
      const b = this.box();
      return { x: ((sx - b.x) * G.W / b.w) * 2, y: ((sy - b.y) * G.H / b.h) * 2 };
    },
    w2u(wx, wy, wz = 0) { return this.s2u(wx - this.x, wy - wz - this.y); },
  };

  // ================================================================ 主循环（§2.3）
  const STEP = 1 / 60;
  let acc = 0, last = 0, running = false;
  const reported = new Set();
  // 主循环里的异常：记进 G.dbg，同一条只往外抛一次（浏览器照常报 Uncaught，自动测试收得到），循环本身不停（银魂坑 A4）
  function report(where, e) {
    const msg = String((e && e.message) || e);
    G.dbg.ev('loop_error', { where, msg });
    const key = where + '|' + msg;
    if (reported.has(key)) return;
    reported.add(key);
    setTimeout(() => { throw e; });
  }
  const flowScale = () => (G.time && typeof G.time.flowScale === 'function' ? G.time.flowScale() : 1);
  function step(dt) {
    G.clk.ui += dt;
    const I = G.input;
    if (I) I.beginStep();                  // 两步之间收到的 DOM 事件落到 hits / 缓冲（时间戳 = 当时的 clk.world）
    try {
      if (G.audio) G.audio.update(dt);
      const sc = G.scene;
      const worldAdv = G.hitStopAll_t <= 0 && !(sc && sc.frozen);
      if (G.hitStopAll_t > 0) { G.hitStopAll_t -= dt; if (G.hitStopAll_t < 1e-9) G.hitStopAll_t = 0; }
      if (G.slowAllT > 0) { G.slowAllT -= dt; if (G.slowAllT <= 1e-9) { G.slowAllT = 0; G.slowAllK = 1; } }   // 慢放时长按 ui 时钟
      const wdt = dt * G.slowAllK;
      if (sc && sc.update) sc.update(dt, worldAdv, wdt);
      if (worldAdv) {
        G.clk.world += wdt;
        G.clk.flow += wdt * flowScale();
        settle('world');
      }
      settle('ui');
      tickFx(dt);
      checkWaiters();
    } finally {
      if (I) I.endStep();                  // 清本步的 hits / tap；缓冲里的按键保留，所以顿帧不吞键
    }
  }
  function safeStep(dt) { try { step(dt); } catch (e) { report('step', e); } }

  function resetCtx(g) {
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.globalAlpha = 1;
    g.globalCompositeOperation = 'source-over';
    g.imageSmoothingEnabled = false;
  }
  function pixelPass(sc, wg, over) {
    const px = G.px, fx = G.fx, post = G.post;
    const P = px.begin(wg);
    try {
      if (!over) {
        if (sc && sc.drawPixel) sc.drawPixel(P, 'mid');
        if (fx && fx.drawPixel) fx.drawPixel(P, 'mid');
        if (post && post.apply) post.apply(P, 'mid');
        if (sc && sc.hasOver && sc.hasOver()) return;
      }
      if (fx && fx.drawPixel) fx.drawPixel(P, 'over');
      if (post && post.apply) post.apply(P, 'final');      // 冲击帧永远最后
    } finally {
      px.end();
    }
  }
  function render() {
    const sc = G.scene, wg = G.wg, ug = G.ug, fx = G.fx, post = G.post;
    // ① 世界层·画布绘制
    resetCtx(wg);
    wg.fillStyle = '#000';
    wg.fillRect(0, 0, G.W, G.H);
    if (sc && sc.drawWorld) { sc.drawWorld(wg); resetCtx(wg); }
    // ② 世界层·像素后期
    const need = !!G.px && ((fx && fx.hasPixel && (fx.hasPixel('mid') || fx.hasPixel('over'))) ||
      (post && post.active && post.active()) || (sc && sc.hasPixel && sc.hasPixel()));
    if (need) pixelPass(sc, wg, false);
    // ③ 时停中能动的人
    if (sc && sc.hasOver && sc.hasOver()) {
      if (sc.drawOver) { sc.drawOver(wg); resetCtx(wg); }
      if (G.px) pixelPass(sc, wg, true);
    }
    // ④ 世界层平滑闪色（只罩世界层，UI 不闪）
    if (G.flashA > 0) {
      wg.globalAlpha = Math.min(1, G.flashA);
      wg.fillStyle = G.flashColor;
      wg.fillRect(0, 0, G.W, G.H);
      wg.globalAlpha = 1;
    }
    // ⑤ UI 层
    resetCtx(ug);
    ug.clearRect(0, 0, G.UW, G.UH);
    if (sc && sc.drawUI) { sc.drawUI(ug); resetCtx(ug); }
    if (G.fadeA > 0) {
      ug.globalAlpha = Math.min(1, G.fadeA);
      ug.fillStyle = '#000';
      ug.fillRect(0, 0, G.UW, G.UH);
      ug.globalAlpha = 1;
    }
    if (sc && sc.drawTop) { sc.drawTop(ug); resetCtx(ug); }
    // ⑥ 合成到屏幕
    const s = G.sctx, SW = G.screen.width, SH = G.screen.height;
    resetCtx(s);
    s.fillStyle = '#000';
    s.fillRect(0, 0, SW, SH);
    if (sc && sc.drawScreen) { sc.drawScreen(s, SW, SH); resetCtx(s); }
    else {
      const b = G.cam.box();
      s.drawImage(G.wv, b.x, b.y, b.w, b.h, 0, 0, SW, SH);
    }
    s.drawImage(G.uv, 0, 0, G.UW, G.UH, 0, 0, SW, SH);
  }
  function safeRender() {
    try { render(); } catch (e) {
      if (G.px && G.px.cur) { try { G.px.end(); } catch (e2) { /* 会话已经坏了 */ } }
      report('render', e);
    }
  }
  G.render = safeRender;

  // 帧率统计：每秒一次（avg = 帧数 / 秒，min = 1 / 最长帧间隔）
  let fpsN = 0, fpsT = 0, fpsMax = 0;
  function fpsSample(dt) {
    if (!(dt > 0)) return;
    fpsN++;
    fpsT += dt;
    if (dt > fpsMax) fpsMax = dt;
    if (fpsT >= 1) {
      G.dbg.fps = { avg: Math.round((fpsN / fpsT) * 10) / 10, min: Math.round((1 / fpsMax) * 10) / 10 };
      fpsN = 0; fpsT = 0; fpsMax = 0;
    }
  }
  function frame(now) {
    requestAnimationFrame(frame);          // 先排下一帧：本帧出错循环也不停
    const raw = (now - last) / 1000;
    last = now;
    const dt = Math.min(0.1, Math.max(0, raw));
    fpsSample(raw > 0 && raw < 1 ? raw : 0);
    if (G.suspended || G.dbg.hold) { acc = 0; safeRender(); return; }   // 手机竖着拿时停住（touch.js 设）
    acc += dt;
    let n = 0;
    while (acc >= STEP && n < 6) { safeStep(STEP); acc -= STEP; n++; }
    if (n === 6) acc = 0;                  // 防螺旋
    safeRender();
  }
  G.start = () => {
    if (running) return;
    running = true;
    requestAnimationFrame((t) => { last = t; requestAnimationFrame(frame); });
  };
})();
