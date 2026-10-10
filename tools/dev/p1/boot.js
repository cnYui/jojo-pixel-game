// 包 1 自测页的启动：进测试场景、主循环挂起（测试用 G.dbg.tick 手动推进），标记就绪
'use strict';
(function () {
  const G = window.G;
  // ?audioinit=1：在页面载入时（没有用户手势）调 G.audio.init()——page.evaluate 带 userGesture，测不了“手势前不建 AudioContext”
  window.__p1act = !!(navigator.userActivation && navigator.userActivation.hasBeenActive);
  if (/[?&]audioinit=1/.test(location.search)) G.audio.init();
  G.setScene(G.testScene);
  G.dbg.hold = true;
  G.start();
  const l = document.getElementById('loading');
  if (l) l.remove();
  window.__p1ready = true;
})();
