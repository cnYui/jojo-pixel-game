// 音频：WebAudio 总线（音乐 / 音效）、音效变体组与并发上限、按需解码 / LRU 释放、标题曲流式（<audio> → WebAudio）、循环音效、时停磁带拖停、压低、同步点（技术约定 §4.4、§3.10，报告 07 §5）
'use strict';
(function () {
  const G = window.G;
  const SR = 44100;
  const MAX_TRACKS = 5;                         // 同时解码着的配乐最多 5 首（LRU）
  const UI_SFX = /^(blip|menu_)/;               // UI 音：不限并发、不受时停影响
  const VOICE = /^(grunt_|ora_voice$|muda_voice$|hora_voice$)/;   // 合成人声：设置“喊声”管
  const TS_EXEMPT = /^(timestop|time_resume|clock_tick)/;         // 时停期间照原样播的
  const JA = () => (window.JOJO_AUDIO = window.JOJO_AUDIO || { music: {}, sfx: {} });
  const meta = () => (G.D && G.D.audio) || null;
  const sfxMeta = (n) => { const m = meta(); return m && m.sfx ? m.sfx[n] : null; };
  const musicMeta = (n) => { const m = meta(); return m && m.music ? m.music[n] : null; };

  let dctx = null;                 // 解码用的上下文（用户手势前是 OfflineAudioContext，之后是真的 AudioContext）
  const bufs = Object.create(null);         // 音效 → AudioBuffer
  const live = Object.create(null);         // 音效 → 正在播的 handle[]（并发上限）
  let groups = null;                        // 变体组：原名 → [名字…]
  const tracks = Object.create(null);       // 配乐 → { buf, used }
  const loading = Object.create(null);      // 配乐 → Promise<AudioBuffer>
  const streams = Object.create(null);      // 流式音乐 → { blob, url, el, node, g }
  const fading = new Set();                 // 正在淡出的音轨
  let cur = null;                           // 当前音轨 { name, kind: 'buf'|'stream', src|st, g, vol, meta, lp, pos, lastCtx }
  let pending = null;                       // 还没解锁时要放的音乐 { name, o, token, stream }
  let token = 0;
  let duckK = 1, duckT = 0, hum = null, heart = null, lpTarget = 20000;
  let volM = -1, volS = -1;
  let clockN = 0;

  // ---------------------------------------------------------------- 小工具
  function b64ToU8(s) {
    const bin = atob(s), n = bin.length, u = new Uint8Array(n);
    for (let i = 0; i < n; i++) u[i] = bin.charCodeAt(i);
    return u;
  }
  function decode(ab) {
    return new Promise((res, rej) => {
      if (!dctx) { rej(new Error('没有可用的音频上下文')); return; }
      let p;
      try { p = dctx.decodeAudioData(ab, res, rej); } catch (e) { rej(e); return; }
      if (p && typeof p.then === 'function') p.then(res, rej);
    });
  }
  function makeOffline() {
    const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (!OAC) return null;
    try { return new OAC({ numberOfChannels: 2, length: 1, sampleRate: SR }); } catch (e) { /* 老 Safari：位置参数 */ }
    try { return new OAC(2, 1, SR); } catch (e) { return null; }
  }
  // 循环点（§3.10）：解码长度明显多于原样本数 = 浏览器没认 gapless 头，开头有编码延迟 → 跳过它。
  // “明显”= 多出 encDelay 的一半以上：Chromium 实测有几个 mp3 解码出来比原长多 2–9 个样本（尾部补齐没剪干净），那不是编码延迟，不能拿来挪循环起点
  function loopPts(buf, m) {
    const samples = m && m.samples;
    if (!samples) return { s: 0, e: buf.duration };
    const k = buf.sampleRate / SR, want = Math.round(samples * k), delay = m.encDelay || 1105;
    if (buf.length - want >= (delay * k) / 2) { const s = delay / SR; return { s, e: Math.min(buf.duration, s + samples / SR) }; }
    return { s: 0, e: Math.min(buf.duration, samples / SR) };
  }
  function buildGroups() {
    groups = Object.create(null);
    const sm = meta() && meta().sfx;
    if (!sm) return;
    for (const n of Object.keys(sm)) {
      const g = sm[n].group;
      if (g) (groups[g] || (groups[g] = [])).push(n);
    }
    for (const g in groups) groups[g].sort();
  }
  function has(n) { return !!(sfxMeta(n) || bufs[n]); }
  // 名字 → 实际音效名；变体组：给了 seed 取 name + (seed mod 组大小)，没给就随机挑一个
  function resolve(name, seed) {
    if (has(name)) return name;
    if (!groups) buildGroups();
    const g = groups[name];
    if (!g || !g.length) return null;
    if (seed != null && Number.isFinite(+seed)) return g[G.mod(Math.floor(+seed), g.length)];
    return g[Math.floor(Math.random() * g.length)];
  }
  function panOf(o) {
    if (o.pan != null) return G.clamp(+o.pan || 0, -1, 1);
    if (o.x != null) return G.clamp(((o.x - G.cam.x - G.W / 2) / (G.W / 2)) * 0.6, -0.6, 0.6);
    return 0;
  }
  function chain(src, vol, pan, dest) {
    const ctx = A.ctx;
    const g = ctx.createGain();
    g.gain.value = vol;
    src.connect(g);
    let p = null;
    if (pan && typeof ctx.createStereoPanner === 'function') {
      p = ctx.createStereoPanner();
      p.pan.value = pan;
      g.connect(p);
      p.connect(dest);
    } else g.connect(dest);
    return { g, p };
  }
  const now = () => (A.ctx ? A.ctx.currentTime : 0);

  // ---------------------------------------------------------------- 上下文与总线
  function ensureCtx() {
    if (A.ctx) return A.ctx;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    let ctx = null;
    try { ctx = new AC({ sampleRate: SR }); } catch (e) {
      try { ctx = new AC(); } catch (e2) { return null; }
    }
    A.ctx = ctx;
    const comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -10;
    comp.knee.value = 6;
    comp.ratio.value = 8;
    comp.attack.value = 0.003;
    comp.release.value = 0.15;
    comp.connect(ctx.destination);
    A.master = comp;
    A.musicOut = ctx.createGain();
    A.musicOut.connect(comp);
    A.musicLP = ctx.createBiquadFilter();
    A.musicLP.type = 'lowpass';
    A.musicLP.frequency.value = lpTarget;
    A.musicLP.Q.value = 0.707;
    A.musicLP.connect(A.musicOut);
    A.tsGain = ctx.createGain();            // 时停用（和 duckGain 串着，互不打架）
    A.tsGain.connect(A.musicLP);
    A.duckGain = ctx.createGain();
    A.duckGain.connect(A.tsGain);
    A.sfxOut = ctx.createGain();
    A.sfxOut.connect(comp);
    volM = volS = -1;
    syncVolumes(true);
    dctx = ctx;
    return ctx;
  }
  function syncVolumes(snap) {
    if (!A.ctx) return;
    const S = G.settings, m = 0.62 * G.clamp(+S.musicVol || 0, 0, 1), s = 0.85 * G.clamp(+S.sfxVol || 0, 0, 1);
    if (m !== volM) { volM = m; if (snap) A.musicOut.gain.value = m; else A.musicOut.gain.setTargetAtTime(m, now(), 0.05); }
    if (s !== volS) { volS = s; if (snap) A.sfxOut.gain.value = s; else A.sfxOut.gain.setTargetAtTime(s, now(), 0.05); }
  }
  function onRunning() {
    if (!A.ctx || A.ctx.state !== 'running') return;
    A.unlocked = true;
    if (pending && pending.token === token) {
      const p = pending;
      pending = null;
      if (p.stream) { if (streams[p.name]) playStream(streams[p.name], p.name, p.o); }
      else if (tracks[p.name]) startBuf(p.name, tracks[p.name].buf, p.o);
      else loadTrack(p.name).then((buf) => { if (p.token === token && !cur) startBuf(p.name, buf, p.o); }, () => {});
    }
  }

  // ---------------------------------------------------------------- 配乐
  function touchTrack(n) { if (tracks[n]) tracks[n].used = ++clockN; }
  function isBusy(n) {
    if (cur && cur.name === n) return true;
    for (const t of fading) if (t.name === n) return true;
    return false;
  }
  function releaseTrack(n) { delete tracks[n]; }
  function enforceLRU(keep) {
    for (;;) {
      const names = Object.keys(tracks);
      if (names.length <= MAX_TRACKS) return;
      let victim = null, best = Infinity;
      for (const n of names) {
        if (n === keep || isBusy(n)) continue;
        if (tracks[n].used < best) { best = tracks[n].used; victim = n; }
      }
      if (!victim) return;
      releaseTrack(victim);
    }
  }
  // 配乐 → AudioBuffer：没加载的插 <script>（o.again），解码完立刻删 base64
  function loadTrack(name) {
    if (tracks[name]) { touchTrack(name); return Promise.resolve(tracks[name].buf); }
    if (loading[name]) return loading[name];
    const m = musicMeta(name);
    if (!m) return Promise.reject(new Error('没有这首音乐：' + name));
    const p = (async () => {
      let s = JA().music[name];
      if (!s) { await G.res.loadScript(m.file, { again: true }); s = JA().music[name]; }
      if (!s) throw new Error('音乐数据为空：' + name);
      const u8 = b64ToU8(s);
      delete JA().music[name];
      const buf = await decode(u8.buffer);
      tracks[name] = { buf, used: ++clockN };
      enforceLRU(name);
      return buf;
    })();
    loading[name] = p;
    const done = () => { delete loading[name]; };
    p.then(done, done);
    return p;
  }
  function fadeOutCurrent(fade) {
    const t = cur;
    cur = null;
    if (!t || !A.ctx) return;
    const ctx = A.ctx, n0 = ctx.currentTime, f = Math.max(0.01, fade);
    const gp = t.g.gain;
    gp.cancelScheduledValues(n0);
    gp.setValueAtTime(gp.value, n0);
    gp.linearRampToValueAtTime(0, n0 + f);
    t.fadeEnd = n0 + f;
    fading.add(t);
    if (t.kind === 'buf') {
      t.src.onended = () => {
        fading.delete(t);
        try { t.g.disconnect(); } catch (e) { /* 已断开 */ }
        if ((t.releaseOnEnd || t.releaseOnEndAlways) && !isBusy(t.name)) releaseTrack(t.name);
      };
      try { t.src.stop(n0 + f + 0.03); } catch (e) { /* 已停 */ }
    }
  }
  function startBuf(name, buf, o) {
    const ctx = A.ctx, n0 = ctx.currentTime;
    const m = musicMeta(name) || {};
    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.loop = true;
    const lp = loopPts(buf, m);
    src.loopStart = lp.s;
    src.loopEnd = lp.e;
    src.playbackRate.value = A.rate;
    const g = ctx.createGain();
    g.gain.setValueAtTime(0, n0);
    g.gain.linearRampToValueAtTime(o.vol, n0 + Math.max(0.01, o.fade));
    src.connect(g);
    g.connect(A.duckGain);
    const len = Math.max(0.01, lp.e - lp.s);
    const off = lp.s + G.mod(o.from || 0, len);
    src.start(n0, off);
    cur = { name, kind: 'buf', src, g, vol: o.vol, meta: m, lp, pos: off - lp.s, lastCtx: n0 };
    touchTrack(name);
  }
  // 流式（标题曲）：base64 → Blob('audio/mpeg') → blob: URL → <audio loop> → createMediaElementSource → duckGain
  function streamFor(name) {
    if (streams[name]) return Promise.resolve(streams[name]);
    const m = musicMeta(name);
    return (async () => {
      let s = JA().music[name];
      if (!s) { await G.res.loadScript(m.file, { again: true }); s = JA().music[name]; }
      if (streams[name]) return streams[name];
      if (!s) throw new Error('音乐数据为空：' + name);
      const blob = new Blob([b64ToU8(s)], { type: 'audio/mpeg' });
      delete JA().music[name];                 // Blob 做好就删 base64；Blob 留着（回标题再用）
      const url = URL.createObjectURL(blob);
      const el = new Audio();
      el.preload = 'auto';
      el.loop = true;
      el.src = url;
      const st = { name, blob, url, el, node: null, g: null, failed: false };
      el.addEventListener('error', () => { if (cur && cur.st === st) fallbackStream(st, name, cur.o || { fade: 0.3, vol: cur.vol, from: 0 }); });
      streams[name] = st;
      return st;
    })();
  }
  function playStream(st, name, o) {
    const ctx = A.ctx;
    if (st.failed) { fallbackStream(st, name, o); return; }
    try {
      if (!st.node) {
        st.node = ctx.createMediaElementSource(st.el);
        st.g = ctx.createGain();
        st.node.connect(st.g);
      }
    } catch (e) { fallbackStream(st, name, o); return; }
    for (const f of fading) if (f.st === st) fading.delete(f);      // 淡出还没完又重新放：别让淡出结束时把它暂停掉
    try { st.g.disconnect(); } catch (e) { /* 第一次 */ }
    st.g.connect(A.duckGain);
    const n0 = ctx.currentTime, gp = st.g.gain;
    gp.cancelScheduledValues(n0);
    gp.setValueAtTime(0, n0);
    gp.linearRampToValueAtTime(o.vol, n0 + Math.max(0.01, o.fade));
    try { if (o.from) st.el.currentTime = o.from; else if (st.el.ended) st.el.currentTime = 0; } catch (e) { /* 还没加载 */ }
    try { st.el.playbackRate = A.rate; st.el.preservesPitch = false; } catch (e) { /* 不支持 */ }
    const tk = token;
    cur = { name, kind: 'stream', st, g: st.g, vol: o.vol, o, meta: musicMeta(name) || {} };
    A.wantGesture = false;
    const p = st.el.play();
    if (p && p.catch) {
      p.catch((e) => {
        if (tk !== token || !cur || cur.st !== st) return;
        if (e && e.name === 'NotAllowedError') {          // 还要一次用户手势：等下一下按键 / 点击
          cur = null;
          pending = { name, o, token: tk, stream: true };
          A.wantGesture = true;
        } else if (e && e.name !== 'AbortError') fallbackStream(st, name, o);
      });
    }
  }
  // 流式失败（极少数浏览器）才退回解码成 AudioBuffer；淡出结束立刻释放
  function fallbackStream(st, name, o) {
    st.failed = true;
    if (cur && cur.st === st) cur = null;
    try { st.el.pause(); } catch (e) { /* 无 */ }
    const tk = token;
    st.blob.arrayBuffer().then((ab) => decode(ab)).then((buf) => {
      if (tk !== token || !A.ctx) return;
      tracks[name] = { buf, used: ++clockN };
      startBuf(name, buf, o);
      if (cur) cur.releaseOnEndAlways = true;
      G.dbg.ev('music_stream_fallback', { name });
    }, () => { G.dbg.ev('music_fail', { name }); });
  }

  // ---------------------------------------------------------------- 对外接口
  const A = (G.audio = {
    ctx: null, master: null, musicOut: null, musicLP: null, duckGain: null, tsGain: null, sfxOut: null,
    unlocked: false, wantGesture: false, inited: false, sfxReady: false,
    name: null,           // 当前音乐名
    rate: 1,              // 音乐目标速度（危机变奏 1.06）
    tsOn: false, tsMusic: 'tape',

    // 建总线。用户还没有过手势时先只建解码用的 OfflineAudioContext（免得 Chrome 报“AudioContext was not allowed to start”），
    // 真的 AudioContext 在第一次手势（unlock）时建
    init() {
      if (this.inited) return;
      this.inited = true;
      const ua = navigator.userActivation;
      if (ua && ua.hasBeenActive) ensureCtx();
      if (!dctx) dctx = makeOffline();
      buildGroups();
      document.addEventListener('visibilitychange', () => {
        if (!A.ctx) return;
        if (document.hidden) {
          try { A.ctx.suspend(); } catch (e) { /* 无 */ }
          if (cur && cur.kind === 'stream' && !cur.st.el.paused) { cur.st.el.pause(); cur.heldByHide = true; }
        } else if (A.unlocked) {
          try { A.ctx.resume(); } catch (e) { /* 无 */ }
          if (cur && cur.heldByHide) { cur.heldByHide = false; const p = cur.st.el.play(); if (p && p.catch) p.catch(() => {}); }
        }
      });
    },
    // 第一次用户手势：建 / 恢复 AudioContext；成功后补放 pendingMusic（流式的在手势里同步 play）
    unlock() {
      if (!this.inited) this.init();
      const ctx = ensureCtx();
      if (!ctx) return;
      if (pending && pending.stream && pending.token === token && streams[pending.name]) {
        const p = pending;
        pending = null;
        playStream(streams[p.name], p.name, p.o);
      }
      if (ctx.state === 'running') onRunning();
      else {
        let r;
        try { r = ctx.resume(); } catch (e) { r = null; }
        if (r && r.then) r.then(onRunning, () => {});
      }
    },
    // 解码全部音效（base64 → ArrayBuffer → decodeAudioData），解码完删掉 base64
    loadSfx(onProgress) {
      if (!this.inited) this.init();
      const src = JA().sfx;
      const names = Object.keys(src);
      const total = names.length;
      let done = 0;
      if (!dctx || !total) { this.sfxReady = true; if (onProgress) onProgress(total, total); return Promise.resolve(); }
      return Promise.all(names.map((n) => {
        let u8;
        try { u8 = b64ToU8(src[n]); } catch (e) { u8 = null; }
        delete src[n];
        const p = u8 ? decode(u8.buffer).then((b) => { bufs[n] = b; }, () => { G.dbg.ev('sfx_decode_fail', { name: n }); }) : Promise.resolve();
        return p.then(() => { done++; if (onProgress) onProgress(done, total); });
      })).then(() => { A.sfxReady = true; });
    },
    has(name) { return !!resolve(name); },

    // 音乐：同名正在放就不重开；没解码就加载 + 解码；整段循环；上一首淡出
    music(name, o = {}) {
      const fade = o.fade == null ? 0.8 : o.fade, vol = o.vol == null ? 1 : o.vol, from = o.from || 0;
      if (!name) { this.stopMusic(fade); return Promise.resolve(); }
      if (this.name === name && (cur || pending || loading[name])) {
        if (cur && A.ctx && Math.abs(cur.vol - vol) > 1e-3) {
          cur.vol = vol;
          const gp = cur.g.gain, n0 = now();
          gp.cancelScheduledValues(n0);
          gp.setValueAtTime(gp.value, n0);
          gp.linearRampToValueAtTime(vol, n0 + Math.max(0.05, fade));
        }
        return Promise.resolve();
      }
      const m = musicMeta(name);
      if (!m) { G.dbg.ev('music_missing', { name }); return Promise.resolve(); }
      fadeOutCurrent(fade);
      this.name = name;
      pending = null;
      const tk = ++token;
      const oo = { fade, vol, from };
      if (m.stream) {
        return streamFor(name).then((st) => {
          if (tk !== token) return;
          if (!A.ctx || !A.unlocked) { pending = { name, o: oo, token: tk, stream: true }; return; }
          playStream(st, name, oo);
        }, (e) => { G.dbg.ev('music_fail', { name, msg: String(e && e.message) }); });
      }
      return loadTrack(name).then((buf) => {
        if (tk !== token) return;
        if (!A.ctx || !A.unlocked) { pending = { name, o: oo, token: tk, stream: false }; return; }
        startBuf(name, buf, oo);
      }, (e) => { G.dbg.ev('music_fail', { name, msg: String(e && e.message) }); });
    },
    stopMusic(fade = 0.8) {
      token++;
      pending = null;
      fadeOutCurrent(fade);
      this.name = null;
    },
    // 预加载 + 解码（不播）；流式的不预取
    prefetch(names) {
      const list = (Array.isArray(names) ? names : [names]).filter((n) => { const m = musicMeta(n); return m && !m.stream; });
      return Promise.all(list.map((n) => loadTrack(n).catch(() => { G.dbg.ev('music_fail', { name: n }); }))).then(() => undefined);
    },
    // 释放 keep 以外、不在播放也不在淡出中的配乐；正在淡出的那首在淡出结束时释放
    releaseExcept(keep) {
      const k = new Set(Array.isArray(keep) ? keep : keep ? [keep] : []);
      for (const n of Object.keys(tracks)) {
        if (k.has(n) || (cur && cur.name === n)) continue;
        let f = null;
        for (const t of fading) if (t.name === n) f = t;
        if (f) { f.releaseOnEnd = true; continue; }
        releaseTrack(n);
      }
    },
    // 调试 / 自测：解码结果（配乐或音效）、当前音轨
    info(name) {
      const t = tracks[name], b = t ? t.buf : bufs[name];
      if (!b) return null;
      const m = t ? musicMeta(name) : sfxMeta(name), lp = loopPts(b, m);
      return { length: b.length, sampleRate: b.sampleRate, channels: b.numberOfChannels, duration: b.duration,
        loopStart: lp.s, loopEnd: lp.e, samples: m ? m.samples : null };
    },
    current() { return cur ? { name: cur.name, kind: cur.kind, vol: cur.vol } : null; },
    loopPoints: loopPts,     // (AudioBuffer, 元数据) → { s, e } 秒

    mem() {
      let bytes = 0;
      const names = [];
      for (const n of Object.keys(tracks)) {
        const b = tracks[n].buf;
        bytes += b.length * b.numberOfChannels * 4;
        names.push(n);
      }
      return { pcmMB: Math.round((bytes / 1e6) * 10) / 10, tracks: names };
    },

    // 音效：o = { vol, rate, pan, x（世界 x，自动声像）, at（延迟秒）, seed, force（喊声关着也播，试听用） }；兼容写法 sfx(name, vol, rate)
    sfx(name, o, rate) {
      if (typeof o === 'number') o = { vol: o, rate: rate == null ? 1 : rate };
      o = o || {};
      const real = resolve(name, o.seed);
      if (!real) { G.dbg.missingSfx.add(String(name)); return null; }
      if (VOICE.test(real) && !G.settings.grunts && !o.force) return null;
      const buf = bufs[real], ctx = A.ctx;
      if (!buf || !ctx) return null;
      const ui = UI_SFX.test(real);
      let r = o.rate == null ? 1 : +o.rate, v = o.vol == null ? 1 : +o.vol;
      if (A.tsOn && !ui && !TS_EXEMPT.test(real)) { r *= 0.9; v *= 0.708; }
      if (!ui) {
        const list = live[real] || (live[real] = []);
        while (list.length >= 4) list.shift().stop();           // 同名最多 4 个，掐最老的
      }
      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.playbackRate.value = r;
      const nodes = chain(src, v, panOf(o), A.sfxOut);
      const t0 = ctx.currentTime + Math.max(0, +o.at || 0);
      const h = {
        name: real, rate: r, src, ended: false,
        stop(fade = 0) {
          if (h.ended) return;
          h.ended = true;
          drop(h);
          try {
            if (fade > 0) {
              const n0 = now(), gp = nodes.g.gain;
              gp.cancelScheduledValues(n0);
              gp.setValueAtTime(gp.value, n0);
              gp.linearRampToValueAtTime(0, n0 + fade);
              src.stop(Math.max(t0, n0 + fade));
            } else src.stop();
          } catch (e) { /* 已停 */ }
        },
        setVol(x) { nodes.g.gain.setTargetAtTime(x, now(), 0.02); },
        setRate(x) { h.rate = x; src.playbackRate.setTargetAtTime(x, now(), 0.02); },
      };
      src.onended = () => {
        h.ended = true;
        drop(h);
        try { nodes.g.disconnect(); if (nodes.p) nodes.p.disconnect(); } catch (e) { /* 已断开 */ }
      };
      if (!ui) live[real].push(h);
      src.start(t0);
      return h;
    },
    // 循环音效：返回 { stop(fade = 0.1), setVol(v), setRate(r) }；o = { vol, rate, pan, x, fade（淡入秒）, seed }
    loop(name, o = {}) {
      const real = resolve(name, o.seed);
      const dummy = { name: real || name, dummy: true, stop() {}, setVol() {}, setRate() {} };
      if (!real) { G.dbg.missingSfx.add(String(name)); return dummy; }
      const buf = bufs[real], ctx = A.ctx;
      if (!buf || !ctx) return dummy;
      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.loop = true;
      const lp = loopPts(buf, sfxMeta(real));
      src.loopStart = lp.s;
      src.loopEnd = lp.e;
      src.playbackRate.value = o.rate == null ? 1 : +o.rate;
      const vol = o.vol == null ? 1 : +o.vol, n0 = ctx.currentTime;
      const nodes = chain(src, o.fade > 0 ? 0 : vol, panOf(o), A.sfxOut);
      if (o.fade > 0) { nodes.g.gain.setValueAtTime(0, n0); nodes.g.gain.linearRampToValueAtTime(vol, n0 + o.fade); }
      src.start(n0, lp.s);
      let stopped = false;
      src.onended = () => { try { nodes.g.disconnect(); if (nodes.p) nodes.p.disconnect(); } catch (e) { /* 已断开 */ } };
      return {
        name: real,
        get playing() { return !stopped; },
        stop(fade = 0.1) {
          if (stopped) return;
          stopped = true;
          const t = now(), gp = nodes.g.gain;
          try {
            gp.cancelScheduledValues(t);
            gp.setValueAtTime(gp.value, t);
            gp.linearRampToValueAtTime(0, t + Math.max(0.005, fade));
            src.stop(t + Math.max(0.005, fade) + 0.02);
          } catch (e) { /* 已停 */ }
        },
        setVol(v, ramp = 0.05) { if (!stopped) nodes.g.gain.setTargetAtTime(v, now(), Math.max(0.001, ramp / 3)); },
        setRate(r) { if (!stopped) src.playbackRate.setTargetAtTime(r, now(), 0.02); },
      };
    },
    // 立刻播，返回“击打点在多少秒后”（hit / rate）：剧情 await G.wait(h.hitIn, 'ui') 让画面落在锣声上
    cue(name, o = {}) {
      const h = this.sfx(name, o);
      const real = (h && h.name) || resolve(name, o.seed) || name;
      const m = sfxMeta(real);
      let r = h ? h.rate : o.rate == null ? 1 : +o.rate;
      if (!h && A.tsOn && !UI_SFX.test(real) && !TS_EXEMPT.test(real)) r *= 0.9;
      return { hitIn: m && m.hit ? m.hit / (r || 1) : 0, handle: h };
    },
    // 压低音乐 dur 秒（ui 时钟）后自动回来；duck(false) 立刻回来；dur 可以是 Infinity（暂停菜单）
    duck(k = 0.35, dur = 0.3) {
      if (k === false) { duckK = 1; duckT = 0; if (A.ctx) A.duckGain.gain.setTargetAtTime(1, now(), 0.06); return; }
      if (!(duckT > 0) || k < duckK) duckK = k;
      duckT = Math.max(duckT, dur);
      if (A.ctx) A.duckGain.gain.setTargetAtTime(duckK, now(), 0.015);
    },
    // 时停（报告 07 §5.3）：开 = 磁带拖停 + timestop_hum；之后所有音效 rate ×0.9、−3 dB。o.music：'tape'（默认）| 'duck' | 'none'
    timeStop(on, o = {}) {
      const ctx = A.ctx;
      if (on) {
        if (A.tsOn) return;
        A.tsOn = true;
        A.tsMusic = o.music || 'tape';
        if (ctx) {
          const t = ctx.currentTime;
          if (A.tsMusic === 'tape') {
            if (cur && cur.kind === 'buf') cur.src.playbackRate.setTargetAtTime(0.05, t, 0.25);
            A.musicLP.frequency.cancelScheduledValues(t);
            A.musicLP.frequency.setTargetAtTime(300, t, 0.3);
            A.tsGain.gain.cancelScheduledValues(t);
            A.tsGain.gain.setTargetAtTime(0, t + 0.6, 0.2);
          } else if (A.tsMusic === 'duck') {
            A.tsGain.gain.setTargetAtTime(0.3, t, 0.1);
            A.musicLP.frequency.setTargetAtTime(800, t, 0.15);
          }
        }
        if (hum) hum.stop(0.05);
        hum = this.loop('timestop_hum', { vol: o.humVol == null ? 1.6 : o.humVol, fade: 0.5 });
      } else {
        if (!A.tsOn) return;
        A.tsOn = false;
        if (hum) { hum.stop(0.1); hum = null; }
        if (ctx) {
          const t = ctx.currentTime;
          if (cur && cur.kind === 'buf') {
            const pr = cur.src.playbackRate;
            pr.cancelScheduledValues(t);
            pr.setValueAtTime(A.tsMusic === 'tape' ? 0.3 : pr.value, t);
            pr.linearRampToValueAtTime(A.rate, t + 0.4);
          }
          A.musicLP.frequency.cancelScheduledValues(t);
          A.musicLP.frequency.setTargetAtTime(lpTarget, t, 0.1);
          A.tsGain.gain.cancelScheduledValues(t);
          A.tsGain.gain.setTargetAtTime(1, t, 0.1);
        }
      }
    },
    // 音乐变速（危机变奏 1.06）
    setRate(r = 1, dur = 0.3) {
      A.rate = r;
      if (!cur || !A.ctx || A.tsOn) return;
      if (cur.kind === 'buf') {
        const pr = cur.src.playbackRate, t = now();
        pr.cancelScheduledValues(t);
        pr.setValueAtTime(pr.value, t);
        pr.linearRampToValueAtTime(r, t + Math.max(0.01, dur));
      } else { try { cur.st.el.playbackRate = r; } catch (e) { /* 不支持 */ } }
    },
    // 音乐低通（暂停菜单 800）；lowpass(null) 复原
    lowpass(hz, dur = 0.3) {
      lpTarget = hz ? G.clamp(+hz, 40, 20000) : 20000;
      if (!A.ctx || A.tsOn) return;
      const f = A.musicLP.frequency, t = now();
      f.cancelScheduledValues(t);
      f.setValueAtTime(Math.max(40, f.value), t);
      f.exponentialRampToValueAtTime(lpTarget, t + Math.max(0.01, dur));
    },
    // 低血（规划 §3.7 第 12 条）：heartbeat_loop + 音乐 1.06
    lowHp(on) {
      if (on) {
        if (heart && heart.playing) return;
        heart = this.loop('heartbeat_loop', { vol: 0.6, fade: 0.2 });
        this.setRate(1.06, 0.4);
      } else {
        if (heart) { heart.stop(0.3); heart = null; }
        this.setRate(1, 0.4);
      }
    },
    // 当前音乐播放位置换算成拍 / 小节（浮点数；卡点用 Math.floor）
    beat() {
      if (!cur) return { name: this.name, t: 0, beat: 0, bar: 0 };
      const m = cur.meta || {};
      const t = cur.kind === 'stream' ? cur.st.el.currentTime || 0 : cur.pos;
      return { name: cur.name, t, beat: m.beatSec ? t / m.beatSec : 0, bar: m.barSec ? t / m.barSec : 0 };
    },
    // 打字音 blip 的 rate = blipHz / 660
    voice(c) {
      let hz = typeof c === 'number' ? c : null;
      if (hz == null) {
        const D = G.D || {};
        const h = (D.heroes && D.heroes[c]) || (D.speakers && D.speakers[c]);
        hz = (h && h.blipHz) || 600;
      }
      return hz / 660;
    },
    // 每步调用：音量设置、压低计时（ui 时钟）、流式淡出结束、播放位置
    update(dt) {
      if (!A.ctx) return;
      syncVolumes(false);
      if (duckT > 0 && duckT !== Infinity) {
        duckT -= dt;
        if (duckT <= 0) { duckT = 0; duckK = 1; A.duckGain.gain.setTargetAtTime(1, now(), 0.06); }
      }
      const t = A.ctx.currentTime;
      for (const f of fading) {
        if (f.kind === 'stream' && t >= f.fadeEnd) {
          fading.delete(f);
          try { f.st.el.pause(); f.st.g.disconnect(); } catch (e) { /* 已断开 */ }
        }
      }
      if (cur && cur.kind === 'buf') {
        const len = cur.lp.e - cur.lp.s;
        cur.pos += (t - cur.lastCtx) * cur.src.playbackRate.value;
        cur.lastCtx = t;
        if (len > 0 && cur.pos >= len) cur.pos = G.mod(cur.pos, len);
      }
    },
  });
  function drop(h) {
    const list = live[h.name];
    if (!list) return;
    const i = list.indexOf(h);
    if (i >= 0) list.splice(i, 1);
  }
})();
