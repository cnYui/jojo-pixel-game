// 竖向背景（第10章送电铁塔这种图高 > 180、带 tall 图层的）的实机截图：镜头往上卷，按 stage.camY 一档一档截。
//   人站在地图元数据 anchors.beams / arms / top_deck 写的横梁上（每档挑落在画面里的那几道），用来核对能站的梁和画出来的对不对得上。
//   用法：node 第四部/tools/dev/p4_bgview_tall.js --out 输出目录 [--chapter ch10] [--step 90] transmission_tower
//   输出 <背景>_y<camY>[_<开关>].png（640×360，2 倍）。
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { serve } = require('./serve');

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const OUT = path.resolve(opt('--out', 'p4_bgview_out'));
const CH = opt('--chapter', 'ch10');
const STEP = +opt('--step', 90);
const keys = argv.filter((a, i) => !a.startsWith('--') && !(i > 0 && argv[i - 1].startsWith('--')));
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const { srv, url } = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 640, height: 360 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(url + 'index.html?autotest=1');
  await page.waitForFunction(() => window.G && G.booted && G.ui.menu, null, { timeout: 60000 });
  const list = await page.evaluate(async ({ CH, keys }) => {
    const idx = G.CHAPTERS.findIndex((c) => c.key === CH);
    const bg = G.D.bg;
    const want = keys.length ? keys : Object.keys(bg).filter((k) => bg[k].pack === CH && (bg[k].h || 180) > 180);
    window.__S = null;
    G.CHAPTERS[idx].run = (S) => { window.__S = S; return new Promise(() => {}); };
    G.playFrom(idx);
    const t0 = Date.now();
    while (!window.__S && Date.now() - t0 < 20000) await new Promise((r) => setTimeout(r, 50));
    return want.map((k) => {
      const b = bg[k], a = b.anchors || {};
      const decks = [].concat(a.beams || [], a.arms || [], a.top_deck ? [a.top_deck] : []);
      return { key: k, w: b.w, h: b.h || 180, cam: b.camY || [0, 0], decks,
        toggles: [...new Set((b.layers || []).flatMap((L) => [L].concat(L.layers || [])).filter((L) => L.key).map((L) => L.key))] };
    });
  }, { CH, keys });
  for (const it of list) {
    await page.evaluate(async (it) => {
      const S = window.__S, ST = G.STAGES, id = 'bgview_' + it.key;
      ST[id] = Object.assign({}, ST.road_pro, { id, bg: it.key, x0: 0, x1: it.w, camX: 0, obstacles: [], state: {}, music: null,
        npcs: [], props: [], hotspots: [], triggers: [] });
      S.party(['josuke'], { leader: 'josuke' });
      await S.setStage(id, { x: 60, y: 160, facing: 1, music: null, fade: false });
      G.fadeA = 0;
      if (S.player) S.player.visible = true;
      const ko = S.spawn('koichi', 92, 150, { id: 'koichi_v', facing: -1 });
      if (ko) ko.visible = true;
    }, it);
    const ys = [];
    for (let y = 0; y >= it.cam[0]; y -= STEP) ys.push(y);
    if (ys[ys.length - 1] !== it.cam[0]) ys.push(it.cam[0]);
    for (const cy of ys) {
      for (const tg of [null, ...it.toggles]) {
        await page.evaluate(({ cy, tg, decks }) => {
          const st = G.world.stage;
          st.camTarget = 0;
          st.camY = cy;
          st.state = {};
          if (tg) st.state[tg] = 1;
          // 画面里（y 在 cy+50 … cy+178）的梁：仗助站最低的那道左边，康一站最高的那道右边
          const vis = decks.filter((d) => d[2] >= cy + 50 && d[2] <= cy + 178).sort((a, b) => b[2] - a[2]);
          const p = G.world.player, ko = st.actors.find((a) => a.id === 'koichi_v');
          const lo = vis[0], hi = vis[vis.length - 1];
          if (p) { if (lo) { p.x = lo[0] + 14; p.y = lo[2]; } else { p.x = 60; p.y = 160; } }
          if (ko) { if (hi) { ko.x = hi[1] - 14; ko.y = hi[2]; } else { ko.x = 96; ko.y = 150; } }
          G.world.snapCamera();
        }, { cy, tg, decks: it.decks });
        await page.waitForTimeout(350);
        const name = `${it.key}_y${cy}${tg ? '_' + tg : ''}.png`;
        await page.screenshot({ path: path.join(OUT, name) });
        console.log('截图', name);
      }
    }
  }
  console.log(errors.length ? '报错：\n' + errors.join('\n') : '无报错');
  await browser.close();
  srv.close();
})().catch((e) => { console.error(e); process.exit(1); });
