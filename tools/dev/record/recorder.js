// 录屏（tools/dev/record/record_demo.py 注入）：画面 + 混好的声音一条，BGM、音效各单独一条，三条同一时刻开录，时间对得上。
// 照银魂 tools/recorder.js 的做法；JoJo 的声音是 WebAudio 总线（G.audio.musicOut / sfxOut → 压缩器 G.audio.master），直接从总线各接一路。
// 要用 http:// 打开游戏（file:// 下片头视频画进画布会算跨域，录不出来）。数据每 3 秒一块，交给 Python 的 window.__recSave 写盘。
// 录宣传片素材时只在画面上藏掉对话框、旁白、操作提示、互动提示、目标箭头、QTE 提示和菜单（状态不动，测试器照常读快照）。
(() => {
  if (window.__recs) return;
  const A = G.audio, ac = A.ctx;
  if (!ac) throw new Error('AudioContext 还没建（先按一个键解锁声音）');
  ac.resume().catch(() => {});
  const dMix = ac.createMediaStreamDestination(), dBgm = ac.createMediaStreamDestination(), dSfx = ac.createMediaStreamDestination();
  A.master.connect(dMix);            // 压缩器之后 = 玩家听到的
  A.musicOut.connect(dBgm);
  A.sfxOut.connect(dSfx);
  // 保活：一路听不见的直流（1e-5）接进三条轨。没声音的那条轨浏览器可能先不出数据，第一声才开始写，三条就对不齐 0 秒
  try {
    const keep = ac.createConstantSource(); keep.offset.value = 1e-5; keep.start();
    keep.connect(dMix); keep.connect(dBgm); keep.connect(dSfx);
    window.__recKeep = keep;
  } catch (e) { console.warn('rec keepalive', e); }
  // 片头 op / 序幕 coffin 是 <video> 元素直接出声，接进 BGM 轨和混音轨
  const origPlay = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () {
    if (!this.__recHooked && this.tagName === 'VIDEO') {
      this.__recHooked = true;
      try { const src = ac.createMediaElementSource(this); src.connect(dBgm); src.connect(dMix); } catch (e) { console.warn('rec video hook', e); }
    }
    return origPlay.call(this);
  };

  if (window.__recCleanUI !== false) {
    const nop = () => {};
    for (const k of ['drawHint', 'drawDialog', 'drawChoice', 'drawNarr', 'drawNotice', 'drawQte', 'drawMenu']) if (G.ui[k]) G.ui[k] = nop;
    if (G.hud && G.hud.drawPrompt) G.hud.drawPrompt = nop;
    if (G.TPL && G.TPL.goal) G.TPL.goal = () => ({ stopped: true, stop() {} });
  }

  // 不传帧率：画布每画一次就收一帧（传 60 会被限流丢帧，见银魂流程复盘第十四节）
  const vs = G.screen.captureStream();
  const streams = {
    full: new MediaStream([...vs.getVideoTracks(), ...dMix.stream.getAudioTracks()]),
    bgm: dBgm.stream,
    sfx: dSfx.stream,
  };
  window.__recs = {};
  window.__recPending = 0;
  for (const k of Object.keys(streams)) {
    const opt = k === 'full'
      ? { mimeType: 'video/webm;codecs=vp9,opus', videoBitsPerSecond: 16000000, audioBitsPerSecond: 256000 }
      : { mimeType: 'audio/webm;codecs=opus', audioBitsPerSecond: 256000 };
    const r = new MediaRecorder(streams[k], opt);
    let chain = Promise.resolve();
    r.ondataavailable = (e) => {
      if (!e.data || !e.data.size) return;
      window.__recPending++;
      chain = chain.then(async () => {
        const buf = new Uint8Array(await e.data.arrayBuffer());
        let s = '';
        for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
        await window.__recSave(k, btoa(s));
        window.__recPending--;
      });
    };
    window.__recs[k] = r;
  }
  for (const r of Object.values(window.__recs)) r.start(3000);
  window.__recStart = performance.now();
  window.__recStop = () => new Promise((res) => {
    const rs = Object.values(window.__recs);
    let n = 0;
    for (const r of rs) { r.onstop = () => { if (++n === rs.length) res(); }; r.stop(); }
  });
})();
