// 233 乐园激励视频广告：G.ads.supported() / G.ads.watch(scene[, { timeoutMs }])。
// SDK 是 async 加载的，所以这里只在真正调用时看 window.MetaH5Ad，加载失败不影响游戏启动。
// showAd 同一次播放会多次回调：status=0/3 是过程态，只有 status=4 发奖，而且一次播放只能结算一次。
'use strict';
(function () {
  const G = window.G;
  const AD_TYPE = 1;
  const DEFAULT_TIMEOUT_MS = 120000;
  const SUPPORT_TIMEOUT_MS = 3000;
  const MOCK_DELAY_MS = 50;
  const LOG_NAMES = ['logBlue', 'logGreen', 'logRed', 'logYellow'];
  const MOCK_MODES = ['ok', 'closed', 'skipped', 'fail', 'timeout', 'unsupported'];
  // technical = 环境 / SDK 侧的问题；用户自己关闭、跳过、重复点击不算技术故障。
  const TECHNICAL = {
    rewarded: false, closed: false, skipped: false, busy: false,
    failed: true, timeout: true, sdk_missing: true, unsupported: true, exception: true,
  };

  const cancellations = new Set();
  let playing = false;
  let mockMode = null;

  function note(type, data) {
    try { if (G.dbg && G.dbg.ev) G.dbg.ev(type, data); } catch (e) { /* 日志不能挡住广告流程 */ }
  }

  // mock 只给自动化 / 显式调试用；正式环境无论怎么调 setMock 都不生效。
  function mockAllowed() {
    if (G.dbg && G.dbg.autotest) return true;
    try { return /[?&]debug=1(?:&|$)/.test((location && location.search) || ''); } catch (e) { return false; }
  }

  function readUrlMock() {
    if (!mockAllowed()) return null;
    try {
      const m = /[?&]adMock=([^&]*)/.exec((location && location.search) || '');
      const mode = m ? decodeURIComponent(m[1]) : null;
      return MOCK_MODES.indexOf(mode) >= 0 ? mode : null;
    } catch (e) { return null; }
  }

  function parseMaybeJson(v) {
    if (v == null) return null;
    if (typeof v === 'string') {
      try { return JSON.parse(v); } catch (e) { return null; }
    }
    return v;
  }

  // SDK 有时把结果再包一层 response / JSON 字符串，先剥掉外壳再读 status。
  function unwrap(v, depth) {
    depth = depth || 0;
    const parsed = parseMaybeJson(v);
    if (depth >= 5 || parsed === null || typeof parsed !== 'object') return parsed;
    if (Object.prototype.hasOwnProperty.call(parsed, 'response')) return unwrap(parsed.response, depth + 1);
    return parsed;
  }

  function toNumber(v) {
    if (v === null || v === undefined || v === '') return null;
    const n = Number(v);
    return isFinite(n) ? n : null;
  }

  function normalize(raw) {
    const result = unwrap(raw) || {};
    const data = unwrap(result.data);
    const dataIsObject = !!data && typeof data === 'object';
    const code = toNumber(result.code != null ? result.code : result.errCode);
    let rawStatus;
    if (dataIsObject) {
      rawStatus = data.status != null ? data.status : (data.rewardStatus != null ? data.rewardStatus : data.state);
    } else {
      rawStatus = data != null ? data : (result.status != null ? result.status : (result.rewardStatus != null ? result.rewardStatus : result.state));
    }
    const status = toNumber(rawStatus);
    const message = String(result.message != null ? result.message : (result.msg != null ? result.msg : (dataIsObject && data.message != null ? data.message : '')));
    // 奖励只能来自 status=4，兼容字段不能把关闭或未知回调误判为看完。
    return { code: code, status: status, message: message, rewarded: status === 4 };
  }

  // SDK 内部会调 logBlue 等全局函数；缺了会抛 ReferenceError，必须在 showAd 前补齐，但不能覆盖已有实现。
  function installLogFallback() {
    for (let i = 0; i < LOG_NAMES.length; i++) {
      const name = LOG_NAMES[i];
      if (typeof window[name] === 'function') continue;
      try {
        window[name] = (function (tag) {
          return function () {
            try {
              const args = Array.prototype.slice.call(arguments);
              args.unshift('[MetaH5Ad:' + tag + ']');
              console.debug.apply(console, args);
            } catch (e) { /* 没有 console.debug 也不能影响广告 */ }
          };
        })(name);
      } catch (e) { /* 宿主把 window 冻住时也不能挡住广告 */ }
    }
  }

  function makeResult(ok, reason, status, scene, raw, extra) {
    const r = {
      success: !!ok,
      status: status === null || status === undefined ? null : status,
      reason: reason,
      technical: !!TECHNICAL[reason],
      scene: scene === undefined ? null : scene,
      raw: raw,
    };
    if (extra) Object.assign(r, extra);
    return r;
  }

  function supported() {
    return new Promise(function (resolve) {
      // mock 下不碰真 SDK：unsupported 模式才返回 false。
      if (mockAllowed() && mockMode) { resolve(mockMode !== 'unsupported'); return; }
      const sdk = window.MetaH5Ad;
      if (!sdk || typeof sdk.isAdSupport !== 'function') { note('ad_support_missing'); resolve(false); return; }
      let done = false;
      let timer = null;
      const finish = function (ok, detail) {
        if (done) return;
        done = true;
        cancellations.delete(cancel);
        if (timer) { clearTimeout(timer); timer = null; }
        note('ad_support', { supported: !!ok, detail: detail });
        resolve(!!ok);
      };
      const cancel = function () { finish(false, 'cancelled'); };
      cancellations.add(cancel);
      // 3 秒竞速：SDK 不回调时不能把整个业务卡死。
      timer = setTimeout(function () { finish(false, 'timeout'); }, SUPPORT_TIMEOUT_MS);
      try {
        sdk.isAdSupport(AD_TYPE, function (raw) {
          const result = unwrap(raw) || {};
          finish(Number(result.code) === 0 && Number(result.data) === 1, raw);
        });
      } catch (e) {
        finish(false, String(e && e.message || e));
      }
    });
  }

  function setMock(mode) {
    if (!mockAllowed()) return false;
    if (MOCK_MODES.indexOf(mode) < 0) return false;
    mockMode = mode;
    note('ad_mock_set', { mode: mode });
    return true;
  }

  function watch(scene, opts) {
    const name = typeof scene === 'string' ? scene : (scene && scene.id ? String(scene.id) : null);
    if (playing) {
      note('ad_watch_busy', { scene: name });
      return Promise.resolve(makeResult(false, 'busy', null, name, null));
    }
    // 同步置 busy：两次 watch 挨着调用时第二次必须立刻看到 busy。
    playing = true;
    installLogFallback();
    const options = opts && typeof opts === 'object' ? opts : {};
    const timeoutMs = (function () {
      const n = Number(options.timeoutMs);
      return isFinite(n) && n > 0 ? n : DEFAULT_TIMEOUT_MS;
    })();
    note('ad_watch', { scene: name, timeoutMs: timeoutMs, mock: mockAllowed() && mockMode ? mockMode : null });
    // engine/audio.js 目前没有全局静音 / 主音量开关，只有会写进存档的用户音量设置；
    // 这里不自己造接口、也不改用户设置，播放期间保持原音量。

    return new Promise(function (resolve) {
      let settled = false;
      let timer = null;
      let lastStatus = null;
      let lastRaw;
      const finish = function (ok, reason, status, raw, extra) {
        if (settled) return;
        settled = true;
        cancellations.delete(cancel);
        playing = false;
        if (timer) { clearTimeout(timer); timer = null; }
        const r = makeResult(ok, reason, status, name, raw, extra);
        note('ad_settle', { scene: name, success: r.success, reason: r.reason, status: r.status, technical: r.technical });
        resolve(r);
      };

      const cancel = function () { finish(false, 'cancelled', lastStatus, lastRaw); };
      cancellations.add(cancel);
      if (mockAllowed() && mockMode) {
        const mode = mockMode;
        timer = setTimeout(function () {
          if (mode === 'ok') finish(true, 'rewarded', 4, { mock: true, status: 4 }, { mocked: true });
          else if (mode === 'closed') finish(false, 'closed', 1, { mock: true, status: 1 }, { mocked: true });
          else if (mode === 'skipped') finish(false, 'skipped', 2, { mock: true, status: 2 }, { mocked: true });
          else if (mode === 'fail') finish(false, 'failed', -1, { mock: true, status: -1 }, { mocked: true });
          else if (mode === 'timeout') finish(false, 'timeout', null, { mock: true }, { mocked: true });
          else finish(false, 'unsupported', null, { mock: true }, { mocked: true });
        }, MOCK_DELAY_MS);
        return;
      }

      const sdk = window.MetaH5Ad;
      if (!sdk || typeof sdk.showAd !== 'function') { finish(false, 'sdk_missing', null, null); return; }

      timer = setTimeout(function () {
        finish(false, 'timeout', lastStatus, lastRaw);
      }, timeoutMs);

      try {
        sdk.showAd(AD_TYPE, function (raw) {
          if (settled) return; // 同一次播放的重复回调（包括重复 status=4）在这里丢掉
          lastRaw = raw;
          const result = normalize(raw);
          lastStatus = result.status;
          note('ad_event', { scene: name, code: result.code, status: result.status, message: result.message });

          if (result.code !== null && result.code !== 0) { finish(false, 'failed', result.status === null ? -1 : result.status, raw); return; }
          if (result.rewarded) { finish(true, 'rewarded', 4, raw); return; }
          // 展示成功 / 点击广告只是过程态，继续等，不能提前判失败。
          if (result.status === 0 || result.status === 3) return;
          if (result.status === 1) { finish(false, 'closed', 1, raw); return; }
          if (result.status === 2) { finish(false, 'skipped', 2, raw); return; }
          if (result.status === -1) { finish(false, 'failed', -1, raw); return; }
          // 未知但 code 未失败：继续等，交给 timeout 兜底。
        });
      } catch (e) {
        finish(false, 'exception', lastStatus, lastRaw, { error: String(e && e.message || e) });
      }
    });
  }

  G.ads = {
    // 战斗失效时释放等待和 busy；迟到回调仍由 finish 的一次性结算挡住。
    cancel: function () { Array.from(cancellations).forEach(function (cancel) { cancel(); }); },
    supported: supported,
    watch: watch,
    setMock: setMock,
    get busy() { return playing; },
  };

  mockMode = readUrlMock();
})();
