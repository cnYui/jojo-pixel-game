// 包 3 自测页的脚本加载器：按 index.html 的顺序插 <script>（file:// 可用），缺的模块（别的包还没交付）跳过、由 stubs.js 补。
// 每个文件的加载结果记进 window.__load = [[文件, 'ok' | 'missing' | 'error: …'], …]，test_ui.py 读它。
'use strict';
(function () {
  const ENGINE = '../../../engine/';
  const LIST = [
    [ENGINE + 'core.js', true], [ENGINE + 'res.js', true], [ENGINE + 'input.js', true], [ENGINE + 'audio.js', false],
    [ENGINE + 'px.js', true], [ENGINE + 'fx.js', false], [ENGINE + 'post.js', false], [ENGINE + 'atlas.js', true], [ENGINE + 'bg.js', false],
    ['stubs.js', true],
    [ENGINE + 'font.js', true], [ENGINE + 'ui.js', true], [ENGINE + 'ui_cards.js', true], [ENGINE + 'hud.js', true],
    ['demo.js', true],
  ];
  window.__load = [];
  let curFile = null;
  const errs = [];
  window.addEventListener('error', (e) => { if (curFile) errs.push(curFile + ': ' + e.message); }, true);
  function load(i) {
    if (i >= LIST.length) { if (window.DEMO && window.DEMO.boot) window.DEMO.boot(); return; }
    const [src, required] = LIST[i];
    const s = document.createElement('script');
    curFile = src;
    const n0 = errs.length;
    s.src = src;
    s.onload = () => {
      window.__load.push([src, errs.length > n0 ? 'error: ' + errs.slice(n0).join(' | ') : 'ok']);
      curFile = null;
      load(i + 1);
    };
    s.onerror = () => {
      window.__load.push([src, required ? 'MISSING(required)' : 'missing']);
      curFile = null;
      load(i + 1);
    };
    document.body.appendChild(s);
  }
  load(0);
})();
