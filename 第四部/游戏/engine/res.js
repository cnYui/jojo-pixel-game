// 资源：图片 key → Image、像素数组、按需插入 <script> 加载数据包 / 音乐（技术约定 §4.2；取代银魂按“.png 结尾的字符串”扫描的做法）
'use strict';
(function () {
  const G = window.G;
  const imgs = Object.create(null);        // key → HTMLImageElement
  const pixc = Object.create(null);        // key → { w, h, u32 }
  const scripts = Object.create(null);     // src → Promise

  // key → Image | null。key 不在 GAME_DATA.img 里：记 missingImg、返回 null（调用方必须容忍 null，银魂坑 A4）
  G.image = function (key) {
    const hit = imgs[key];
    if (hit) return hit;
    const D = G.D, src = D && D.img ? D.img[key] : null;
    if (!src) { G.dbg.missingImg.add(String(key)); return null; }
    const im = new Image();
    im.decoding = 'async';
    im.src = src;
    imgs[key] = im;
    return im;
  };
  G.ready = (im) => !!(im && im.complete && im.naturalWidth > 0);

  // key → { w, h, u32 }（Uint32Array，0xAABBGGRR）| null（图还没解码好时返回 null，不缓存，下次再试）
  G.pix = function (key) {
    const hit = pixc[key];
    if (hit) return hit;
    const im = G.image(key);
    if (!G.ready(im)) return null;
    const w = im.naturalWidth, h = im.naturalHeight;
    const cv = G.mkCanvas(w, h, true);      // 会读像素：willReadFrequently（§0.2 第 14 条）
    cv.g.drawImage(im, 0, 0);
    const d = cv.g.getImageData(0, 0, w, h);
    cv.width = cv.height = 0;               // 临时画布用完丢掉
    const r = { w, h, u32: new Uint32Array(d.data.buffer) };
    pixc[key] = r;
    return r;
  };

  function decodeOne(key) {
    const im = G.image(key);
    if (!im) return Promise.resolve(false);
    if (G.ready(im)) return Promise.resolve(true);
    if (typeof im.decode === 'function') {
      return im.decode().then(() => true, () => { G.dbg.missingImg.add(String(key)); return false; });
    }
    return new Promise((res) => {
      im.addEventListener('load', () => res(true), { once: true });
      im.addEventListener('error', () => { G.dbg.missingImg.add(String(key)); res(false); }, { once: true });
    });
  }

  G.res = {
    // 插入 <script>：onload resolve、onerror reject；同一个 src 默认只插一次（o.again 强制再插，音乐释放后重新加载用）
    loadScript(src, o = {}) {
      if (!o.again && scripts[src]) return scripts[src];
      const p = new Promise((res, rej) => {
        const s = document.createElement('script');
        s.src = src;
        s.async = false;
        s.onload = () => { s.remove(); res(); };            // 执行完就把节点拿掉（音乐脚本几 MB 文本，不留在 DOM 里）
        s.onerror = () => { s.remove(); delete scripts[src]; rej(new Error('loadScript 失败：' + src)); };
        (document.head || document.documentElement).appendChild(s);
      });
      scripts[src] = p;
      return p;
    },
    // 一组 key 全部建 Image 并 decode()（失败的记 missingImg，不抛）
    preloadKeys(keys, onProgress) {
      const list = keys || [];
      let done = 0;
      const total = list.length;
      if (!total) { if (onProgress) onProgress(0, 0); return Promise.resolve(); }
      return Promise.all(list.map((k) => decodeOne(k).then(() => {
        done++;
        if (onProgress) onProgress(done, total);
      }))).then(() => undefined);
    },
    // 解码某个已加载的图片包里的全部图片（img_core.js 由 index.html 直接加载，启动时调这个）
    preloadPack(name, onProgress) {
      const D = G.D;
      return this.preloadKeys(D && D.packKeys ? D.packKeys[name] : null, onProgress);
    },
    // 按需加载图片包（'core' 或 'bg_<短名>'）：已加载 → 不再插脚本（只补一遍解码，已解码的图立刻过）；否则插 <script> 再解码这个包的全部图片
    loadPack(name) {
      const D = G.D;
      if (!D) return Promise.reject(new Error('GAME_DATA 没加载'));
      if (D.packsLoaded && D.packsLoaded[name]) return this.preloadKeys(D.packKeys ? D.packKeys[name] : null);
      const p = D.packs && D.packs[name];
      if (!p || !p.file) { G.dbg.ev('pack_missing', { name }); return Promise.resolve(); }
      return this.loadScript(p.file).then(() => this.preloadKeys(D.packKeys ? D.packKeys[name] : null));
    },
    loaded(name) { const D = G.D; return !!(D && D.packsLoaded && D.packsLoaded[name]); },
  };
})();
