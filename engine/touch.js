// 触屏：方向盘、J / K / L / E / U 按钮、换人钮、暂停、全屏 → G.input（技术约定 §4.3.5；照银魂 touch.js + 报告 02 §8.3 改）
// 长相和位置在 index.html 的 #tc 一段；这里管：什么时候出现、多指同时按、方向盘滑动、按场景显隐、横屏提示、全屏、按键大小。
//   网址后面加 ?touch=1 强制显示（电脑上调试用）　?touch=0 强制不显示
// 点菜单 / 选项靠 G.input.tap（UI 坐标；ui.js / main.js 判断点中了哪一项）。
'use strict';
(function () {
  const G = window.G;
  const I = G.input;
  const root = document.getElementById('tc');
  const ua = navigator.userAgent;
  const T = (G.touch = {
    on: false,
    ctx: '',            // explore / combat / late / menu / qte / story / title / end
    haptic: true,       // 按下震一下（手机支持、且用户已经碰过页面时）
    ios: /iP(hone|ad|od)/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1),
    // 屏幕按键压在画面上的范围（UI 坐标 0..640 / 0..360）：l = 方向盘右缘；r = L 钮左缘；top = 换人钮上缘；sys = 全屏 / 暂停钮左缘。
    // 触屏关着时是 0 / 640 / 360 / 640。提示、选项、计时、HUD 靠它躲开按钮
    safe: { l: 0, r: G.UW, top: G.UH, sys: G.UW },
    toast() {}, setOn() {}, cycleSize() {}, sizeName: () => '中',
  });
  if (!root) return;
  const $ = (id) => document.getElementById(id);
  const param = new URLSearchParams(location.search).get('touch');
  const force = param === '1' ? true : param === '0' ? false : null;
  const isCoarse = () => !!(window.matchMedia && matchMedia('(pointer: coarse)').matches) || /Android|Mobile|iP(hone|ad|od)/i.test(ua);

  // ---------------------------------------------------------------- 按钮 / 方向 → 按键
  const buzz = (ms = 9) => {
    const act = navigator.userActivation;
    if (!T.haptic || !navigator.vibrate || (act && !act.hasBeenActive)) return;   // 没碰过页面时调 vibrate 浏览器会打警告
    try { navigator.vibrate(ms); } catch (e) { /* 不支持就算了 */ }
  };
  const el = {
    pad: $('tc-pad'), j: root.querySelector('.tc-j'), k: root.querySelector('.tc-k'), l: root.querySelector('.tc-l'),
    e: root.querySelector('.tc-e'), u: root.querySelector('.tc-u'), swap: $('tc-swap'), pause: $('tc-pause'), full: $('tc-full'),
  };
  const releasers = [];

  // 每个按钮自己记着哪几根手指按着它：方向盘 + 出拳 + 闪避同时按没问题
  [el.j, el.k, el.l, el.e, el.u, el.swap, el.pause].forEach((b) => {
    if (!b) return;
    const a = b.dataset.key, ids = new Set(), src = 'tc:' + a;
    b.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      try { b.setPointerCapture(e.pointerId); } catch (err) { /* 合成事件没有对应的指针 */ }
      ids.add(e.pointerId);
      b.classList.add('on');
      I.press(a, src);
      buzz();
    });
    const up = (e) => {
      if (!ids.delete(e.pointerId) || ids.size) return;
      b.classList.remove('on');
      I.release(a, src);
    };
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach((n) => b.addEventListener(n, up));
    releasers.push(() => { if (ids.size) I.release(a, src); ids.clear(); b.classList.remove('on'); });
  });

  // 方向盘：手指落在盘上、滑到哪儿朝哪儿走；8 个方向，横竖方向的范围比斜向宽
  const knob = $('tc-knob');
  const arrows = {};
  el.pad.querySelectorAll('.arr').forEach((p) => { arrows[p.dataset.d] = p; });
  const AXIS = { right: 0, down: 90, left: 180, up: -90 };
  const padKeys = { left: false, right: false, up: false, down: false };
  let padId = null;
  function padSet(dir) {
    for (const a in padKeys) {
      const on = !!dir[a];
      if (on && !padKeys[a]) I.press(a, 'tcpad');
      else if (!on && padKeys[a]) I.release(a, 'tcpad');
      padKeys[a] = on;
      if (arrows[a]) arrows[a].classList.toggle('on', on);
    }
  }
  function padMove(e) {
    const r = el.pad.getBoundingClientRect();
    const R = r.width / 2, dx = e.clientX - (r.left + R), dy = e.clientY - (r.top + R);
    const d = Math.hypot(dx, dy), lim = R * 0.45, k = d > lim ? lim / d : 1;
    knob.style.transform = `translate(${dx * k}px, ${dy * k}px)`;
    const dir = {};
    if (d >= R * 0.3) {
      const th = (Math.atan2(dy, dx) * 180) / Math.PI;
      for (const a in AXIS) {
        let diff = Math.abs(th - AXIS[a]) % 360;
        if (diff > 180) diff = 360 - diff;
        if (diff < (padKeys[a] ? 66 : 60)) dir[a] = true;     // 已经按着的方向多给 6 度，边界上不来回跳
      }
    }
    padSet(dir);
  }
  el.pad.addEventListener('pointerdown', (e) => {
    if (padId != null) return;
    e.preventDefault();
    padId = e.pointerId;
    try { el.pad.setPointerCapture(e.pointerId); } catch (err) { /* 同上 */ }
    el.pad.classList.add('on');
    padMove(e);
  });
  el.pad.addEventListener('pointermove', (e) => { if (e.pointerId === padId) padMove(e); });
  const padUp = (e) => {
    if (e && e.pointerId !== padId) return;
    padId = null;
    el.pad.classList.remove('on');
    knob.style.transform = '';
    padSet({});
  };
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach((n) => el.pad.addEventListener(n, padUp));
  releasers.push(() => padUp());

  // ---------------------------------------------------------------- 按场景显隐（1 = 亮，0.4 / 0.6 = 暗着但还能按，0 = 藏起来、手指能穿过去点到画面）
  const SHOW = {
    explore: { pad: 1, j: 0.6, k: 0, l: 0, u: 1, e: 1, swap: 1, pause: 1 },
    combat:  { pad: 1, j: 1, k: 1, l: 1, u: 1, e: 0.4, swap: 1, pause: 1 },
    late:    { pad: 1, j: 1, k: 1, l: 1, u: 1, e: 1, swap: 0, pause: 1 },
    menu:    { pad: 1, j: 0, k: 0, l: 0, u: 0, e: 1, swap: 0, pause: 1 },
    qte:     { pad: 0, j: 1, k: 0, l: 0, u: 0, e: 1, swap: 0, pause: 1 },
    story:   { pad: 0, j: 0, k: 0, l: 0, u: 0, e: 0, swap: 0, pause: 1 },
    title:   { pad: 1, j: 0, k: 0, l: 0, u: 0, e: 1, swap: 0, pause: 0 },
    end:     { pad: 0, j: 0, k: 0, l: 0, u: 0, e: 0, swap: 0, pause: 0 },
  };
  let probeErr = false;
  const probe = (fn) => {             // 读别的模块的状态：出错不往外抛（每 50 ms 一次，抛了会刷屏），只记一次
    try { return fn(); } catch (e) {
      if (!probeErr) { probeErr = true; G.dbg.ev('touch_probe_error', { msg: String(e && e.message) }); }
      return false;
    }
  };
  function context() {
    const sc = G.scene && G.scene.name, U = G.ui;
    if (sc === 'title' || sc === 'end') return sc;
    if (sc === 'video') return 'story';
    if (U) {
      if (U.menu || U.choiceBox) return 'menu';
      if (U.qte) return 'qte';
      if (typeof U.blocking === 'function' ? probe(() => U.blocking()) : U.dlg || U.narr || U.notice) return 'story';
    }
    if (G.lateGame) return 'late';
    return G.world && G.world.combat ? 'combat' : 'explore';
  }
  const CAP = {   // 各场景下按钮下面的小字
    j: { qte: '连按' },
    e: { menu: '确认', title: '确认', qte: '确认' },
    u: { explore: '替身调查' },
  };
  const caps = Object.fromEntries(['j', 'k', 'l', 'e', 'u'].map(n => [n, el[n].querySelector('i')]));
  const capDefault = Object.fromEntries(Object.entries(caps).map(([n, node]) => [n, node.textContent]));
  const shown = {};
  function apply(n, v) {
    if (shown[n] === v || !el[n]) return;
    shown[n] = v;
    el[n].classList.toggle('tc-off', v === 0);
    el[n].classList.toggle('tc-dim', v > 0 && v < 1);
  }
  let lastCtx = '';
  function refresh() {
    const c = context();
    const show = Object.assign({}, SHOW[c]);
    const lateTouch = c === 'late' && G.lateGame.touch;
    // 机关各自声明操作，避免探索层把格挡、闪避或小游戏专用 U 藏起来。
    if (lateTouch && Array.isArray(lateTouch.buttons)) {
      for (const n of ['pad', 'j', 'k', 'l', 'u', 'e', 'swap']) show[n] = lateTouch.buttons.includes(n) ? 1 : 0;
    }
    const W = G.world;
    let uReady = false, uGold = false;
    if (c === 'title' && G.scene.mode && G.scene.mode !== 'main') show.pause = 1;      // 选章节 / 说明页里，暂停钮 = 返回
    if (c === 'explore') {
      const ready = probe(() => !!(G.party && G.party.lookReady && G.party.lookReady()));
      if (!ready) show.u = 0.4;                                                    // 替身调查冷却中
      else uReady = probe(() => !!(W && W.findLook && W.findLook()));            // 附近有标签对得上的调查点：跳动
      if (!probe(() => !!(G.party && G.party.canSwap && G.party.canSwap()))) show.swap = 0;
    } else if (c === 'combat') {
      const p = W && W.player;
      const full = !!(p && p.energy >= (p.energyMax || 100));
      uGold = !!(W && W.fight && W.fight.storyU);
      uReady = full || uGold;
      if (!uReady) show.u = 0.4;
      if (!(W && W.fight && W.fight.swap)) show.swap = 0;
    }
    T.ctx = c;
    for (const n in show) apply(n, show[n]);
    if (c !== lastCtx || c === 'late') {
      lastCtx = c;
      for (const n in caps) caps[n].textContent = lateTouch && lateTouch.captions && lateTouch.captions[n] ||
        (CAP[n] && CAP[n][c]) || capDefault[n];
    }
    el.u.classList.toggle('ready', uReady && show.u > 0);
    el.u.classList.toggle('gold', uGold);
    el.e.classList.toggle('pulse', c === 'explore' && !!(W && W.near));       // 附近有人 / 东西可以调查：E 钮跳动
  }

  // 选菜单时按住上 / 下：过一会儿开始连着走
  const rep = { a: null, t0: 0, last: 0 };
  function repeat(now) {
    const menuish = T.ctx === 'menu' || T.ctx === 'title';
    const a = padKeys.up && !padKeys.down ? 'up' : padKeys.down && !padKeys.up ? 'down' : null;
    if (!menuish || !a) { rep.a = null; return; }
    if (rep.a !== a) { rep.a = a; rep.t0 = rep.last = now; return; }
    if (now - rep.t0 > 380 && now - rep.last > 110) { rep.last = now; I.inject(a); }
  }

  // ---------------------------------------------------------------- 排版：按钮大小随屏幕高度走；竖着拿就停住、提示横过来
  const SIZES = [['小', 0.82], ['中', 1], ['大', 1.22]];
  let sizeIdx = (function () {
    const v = G.store.get('touch-size', null);
    if (typeof v === 'number' && v >= 0 && v < SIZES.length) return v | 0;
    const i = SIZES.findIndex((s) => Math.abs(s[1] - G.settings.touchSize) < 0.01);
    return i >= 0 ? i : 1;
  })();
  G.settings.touchSize = SIZES[sizeIdx][1];
  T.sizeName = () => SIZES[sizeIdx][0];
  T.cycleSize = () => {
    sizeIdx = (sizeIdx + 1) % SIZES.length;
    G.store.set('touch-size', sizeIdx);
    G.settings.touchSize = SIZES[sizeIdx][1];
    G.settings.save();
    layout();
  };
  function syncSize() {               // 设置菜单直接改了 G.settings.touchSize 时跟上
    if (Math.abs(G.settings.touchSize - SIZES[sizeIdx][1]) < 0.001) return;
    let best = 1, bd = Infinity;
    SIZES.forEach((s, i) => { const d = Math.abs(s[1] - G.settings.touchSize); if (d < bd) { bd = d; best = i; } });
    sizeIdx = best;
    G.settings.touchSize = SIZES[best][1];
    G.store.set('touch-size', sizeIdx);
    layout();
  }
  function layout() {
    const w = innerWidth, h = innerHeight;
    root.style.setProperty('--b', G.clamp(Math.round(Math.min(h * 0.145, w * 0.075) * SIZES[sizeIdx][1]), 36, 96) + 'px');
    const portrait = T.on && h > w;
    document.body.classList.toggle('tc-portrait', portrait);
    G.suspended = portrait;
    measure();
  }
  function measure() {
    const S = T.safe;
    if (!T.on) { S.l = 0; S.r = G.UW; S.top = G.UH; S.sys = G.UW; return; }
    const c = G.screen.getBoundingClientRect();
    if (!(c.width > 0 && c.height > 0)) return;
    const kx = G.UW / c.width, ky = G.UH / c.height;
    const gx = (x) => G.clamp((x - c.left) * kx, 0, G.UW);
    const gy = (y) => G.clamp((y - c.top) * ky, 0, G.UH);
    S.l = gx(el.pad.getBoundingClientRect().right);
    S.r = gx(el.l.getBoundingClientRect().left);
    S.top = gy(el.swap.getBoundingClientRect().top);
    S.sys = gx((el.full.style.display === 'none' ? el.pause : el.full).getBoundingClientRect().left);
  }
  addEventListener('resize', layout);
  addEventListener('orientationchange', () => setTimeout(layout, 250));

  // ---------------------------------------------------------------- 全屏（安卓 Chrome 全屏后还能锁横屏；iPhone 的 Safari 没有网页全屏，要“添加到主屏幕”）
  const de = document.documentElement;
  const reqFs = de.requestFullscreen || de.webkitRequestFullscreen;
  const exitFs = document.exitFullscreen || document.webkitExitFullscreen;
  const inFs = () => document.fullscreenElement || document.webkitFullscreenElement;
  if (!reqFs) el.full.style.display = 'none';
  else {
    el.full.addEventListener('click', () => {      // 全屏要求“手指抬起”这种用户动作，pointerdown 不算
      try {
        if (inFs()) { exitFs.call(document); return; }
        const p = reqFs.call(de, { navigationUI: 'hide' });
        const lock = () => { try { screen.orientation.lock('landscape').catch(() => {}); } catch (err) { /* 不支持锁定方向 */ } };
        if (p && p.then) p.then(lock).catch(() => {}); else lock();
      } catch (err) { /* 浏览器不让就算了 */ }
    });
    ['fullscreenchange', 'webkitfullscreenchange'].forEach((n) => document.addEventListener(n, () => { G.resize(); layout(); }));
  }

  // ---------------------------------------------------------------- 提示
  const toastEl = $('tc-toast');
  let toastTimer = 0;
  const queue = [];
  function toast(msg, ms = 5000) {
    if (!toastEl) return;
    queue.push([msg, ms]);
    if (!toastTimer) next();
    function next() {
      const q = queue.shift();
      if (!q) { toastTimer = 0; return; }
      toastEl.textContent = q[0];
      toastEl.classList.add('show');
      toastTimer = setTimeout(() => { toastEl.classList.remove('show'); toastTimer = setTimeout(next, 400); }, q[1]);
    }
  }
  T.toast = toast;
  function whenBooted(fn) { const t = setInterval(() => { if (G.scene) { clearInterval(t); fn(); } }, 200); }
  const once = (key) => { if (G.store.get(key, null)) return false; G.store.set(key, 1); return true; };

  // 切到别的应用 / 锁屏回来：屏幕常亮（只有 https 或 localhost 才有这个接口）
  let wake = null;
  async function keepAwake() {
    try {
      if (navigator.wakeLock && !wake && !document.hidden) {
        wake = await navigator.wakeLock.request('screen');
        wake.addEventListener('release', () => { wake = null; });
      }
    } catch (e) { /* 拿不到就算了 */ }
  }
  document.addEventListener('visibilitychange', () => { if (T.on && !document.hidden) keepAwake(); });

  // 手离开屏幕一会儿，按键淡下去（少挡画面）；一碰就回来
  let lastAct = performance.now(), idle = false;
  const poke = () => { lastAct = performance.now(); };
  function fade(now) {
    const want = now - lastAct > 2500 && padId == null && !root.querySelector('.on');
    if (want !== idle) { idle = want; document.body.classList.toggle('tc-idle', want); }
  }
  ['pointerdown', 'pointermove'].forEach((n) => document.addEventListener(n, poke, true));

  // ---------------------------------------------------------------- 开关
  let timer = 0;
  function loop() { const now = performance.now(); syncSize(); refresh(); repeat(now); fade(now); }
  function setOn(v) {
    if (T.on === v) return;
    T.on = v;
    document.body.classList.toggle('tc-on', v);
    if (v) {
      layout();
      lastCtx = '';
      for (const n in shown) delete shown[n];
      lastAct = performance.now();
      refresh();
      timer = setInterval(loop, 50);
      keepAwake();
      whenBooted(() => {        // 等标题出来了再弹，载入时弹的提示没人看得见
        if (once('touch-tip')) toast('左手方向盘；右手 J 出拳（连点＝连打）/ K 闪避 / L 格挡 / U 必杀（走动时 U＝替身调查）；右边的“换”换队长', 6500);
        if (T.ios && !navigator.standalone && once('touch-ios-tip')) toast('iPhone 想全屏玩：点浏览器的“分享”→“添加到主屏幕”，再从桌面图标打开', 7000);
      });
    } else {
      clearInterval(timer);
      releasers.forEach((f) => f());
      document.body.classList.remove('tc-portrait', 'tc-idle');
      idle = false;
      G.suspended = false;
      measure();
    }
  }
  T.setOn = setOn;
  T.refresh = () => { if (T.on) refresh(); };

  // 手指点在按钮以外的地方（黑边上）：算一次“确认 / 点这里”。点在画面里 input.js 已经管了
  document.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'touch' && force !== false) setOn(true);
    if (!T.on || e.target === G.screen || (e.target.closest && e.target.closest('.tc-part'))) return;
    I.tapAt(e);
  }, true);
  // 接了实体键盘就把屏幕按键收起来（再碰屏幕会自己出现）
  const KEYS = /^(Arrow|Key[WASDJKLZXCEPUVQ]$|Enter|Space|Escape|Backspace|Numpad|Tab$|Digit[1-6]$)/;
  addEventListener('keydown', (e) => { if (force !== true && T.on && KEYS.test(e.code)) setOn(false); });
  document.addEventListener('contextmenu', (e) => { if (T.on) e.preventDefault(); });
  document.addEventListener('gesturestart', (e) => e.preventDefault());       // iOS 老版本的双指缩放

  setOn(force !== null ? force : isCoarse());
})();
