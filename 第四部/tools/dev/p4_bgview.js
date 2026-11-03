// 第四部背景的实机截图：在真游戏里摆一张背景、站两个人，镜头从左到右各截一张，有开关层（key / pick）的再开着截一遍。
//   用来核对画面比例、人站的位置、对白框盖住哪里、会动的层接得对不对（不跑剧情）。
//   用法：node 第四部/tools/dev/p4_bgview.js --out 输出目录 [--chapter ch2] hirose_living budogaoka_hall …
//   不写背景名 = 这个章节包（--chapter，默认 ch2）里的全部背景。输出 <背景>_<镜头>[_<开关>].png（640×360，2 倍）。
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { serve } = require('./serve');

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const OUT = path.resolve(opt('--out', 'p4_bgview_out'));
const CH = opt('--chapter', 'ch2');
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
  // 借第 N 章的位置跑一个只摆背景的“章节”：playFrom 会先加载 bg_common 和 bg_<章节>
  const list = await page.evaluate(async ({ CH, keys }) => {
    const idx = G.CHAPTERS.findIndex((c) => c.key === CH);
    const bg = G.D.bg;
    const want = keys.length ? keys : Object.keys(bg).filter((k) => bg[k].pack === CH);
    window.__S = null;
    G.CHAPTERS[idx].run = (S) => { window.__S = S; return new Promise(() => {}); };
    G.playFrom(idx);
    const t0 = Date.now();
    while (!window.__S && Date.now() - t0 < 20000) await new Promise((r) => setTimeout(r, 50));
    return want.map((k) => ({ key: k, w: bg[k].w, anchors: bg[k].anchors || {},
      toggles: (bg[k].layers || []).concat(bg[k].fg || []).filter((L) => L.key).map((L) => L.key) }));
  }, { CH, keys });
  for (const it of list) {
    const toggles = [...new Set(it.toggles)];
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
      G.world.stage.state = {};
    }, it);
    const cams = it.w <= 320 ? [0] : [0, Math.round((it.w - 320) / 2), it.w - 320];
    for (const cx of cams) {
      for (const tg of [null, ...toggles]) {
        await page.evaluate(({ cx, tg }) => {
          const st = G.world.stage;
          st.camTarget = cx;
          st.state = {};
          if (tg) st.state[tg] = 1;
          const p = G.world.player;
          if (p) { p.x = cx + 60; p.y = 160; }
          const ko = st.actors.find((a) => a.id === 'koichi_v');
          if (ko) { ko.x = cx + 96; ko.y = 150; }
          G.world.snapCamera();
        }, { cx, tg });
        await page.waitForTimeout(350);
        const name = `${it.key}_${cx}${tg ? '_' + tg : ''}.png`;
        await page.screenshot({ path: path.join(OUT, name) });
        console.log('截图', name);
      }
    }
  }
  console.log(errors.length ? '报错：\n' + errors.join('\n') : '无报错');
  await browser.close();
  srv.close();
})().catch((e) => { console.error(e); process.exit(1); });
