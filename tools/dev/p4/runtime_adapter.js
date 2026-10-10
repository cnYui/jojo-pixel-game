// 包 4 联接自测：保留真 core/res/input，仅把手动推进和耗时采样接到自测入口。
'use strict';
(function () {
  const G = window.G;
  G.dbg.hold = true;
  G.__perf = { canvasMs: [], renderMs: [] };
  const draw = G.world.draw;
  G.world.draw = function (g) {
    const t = performance.now();
    draw.call(this, g);
    G.__perf.canvasMs.push(performance.now() - t);
  };
  const tick = (n, dt = 1 / 60) => {
    const t = performance.now();
    G.dbg.tick(n, dt);
    G.__perf.renderMs.push(performance.now() - t);
  };
  G.__step = (n) => tick(n);
  G.__stepOne = (dt) => tick(1, dt);
  G.__render = () => tick(0);
  G.audio = { sfx() {}, music() { return Promise.resolve(); }, loop() { return { stop() {} }; }, update() {} };
})();
