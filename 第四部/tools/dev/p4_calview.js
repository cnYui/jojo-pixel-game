// 日历地图（杜王町地图 morioh_map）的实机截图：在真游戏里放各章开头的日历动画，按时间点截图。
//   --pins：不放动画，把各章全部图钉 + 名字一次画上去（核对重画的建筑和图钉对不对得上）
//   用法：node 第四部/tools/dev/p4_calview.js --out 输出目录 [--at 0.3,3.2] [--pins] [--root 游戏目录] [prologue ch2 ch4 …]
//   不写章节 = prologue。输出 cal_<章>_<秒>.png、pins_all.png（640×360，2 倍）。
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { serve, ROOT } = require('./serve');

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const OUT = path.resolve(opt('--out', 'p4_calview_out'));
const AT = opt('--at', '0.3,3.2').split(',').map(Number);
const PINS = argv.includes('--pins');
const ROOTDIR = path.resolve(opt('--root', ROOT));
const keys = argv.filter((a, i) => !a.startsWith('--') && !(i > 0 && argv[i - 1].startsWith('--')));
fs.mkdirSync(OUT, { recursive: true });

// 各章开章时在内存里补的锚点（剧情脚本里的默认值；背景元数据里有同名锚点时以元数据为准，和游戏里一样）
const FILL = {
  ch1: { nijimura: [70, 140] }, ch2: { hirose_home: [150, 150] }, ch5: { rohan_house: [228, 48], farm: [58, 70] },
  ch7: { ch7_salon: [214, 86], ch7_tailor: [188, 100] },
  ch11: { c11_kawajiri: [140, 100], c11_rohan: [226, 92], c11_alley: [186, 80] }, final: { fin_home: [140, 104] },
};
// 全部图钉（at = 锚点名，xy = 剧情里写死的坐标）
const ALL = [
  ['prologue', 'school', '葡萄丘高中'], ['prologue', 'home', '东方家'], ['ch1', 'nijimura', '虹村家'], ['ch2', 'hirose_home', '康一家'],
  ['ch3', 'villa', '海边别墅'], ['ch3', [146, 98], '意大利餐厅'], ['ch4', 'sea', '杜王港'],
  ['ch5', 'rohan_house', '露伴宅'], ['ch5', 'farm', '牧场'],
  ['ch6', [190, 96], '幽灵小路'], ['ch6', [222, 82], '葡萄丘银行'], ['ch6', [138, 58], '葡萄丘中学'],
  ['ch7', 'ch7_salon', '灰姑娘美容院'], ['ch7', 'ch7_tailor', '裁缝店'], ['ch8', [130, 104], '吉良家旧宅'], ['ch8', [203, 62], '杜王站'],
  ['ch10', [46, 44], '送电铁塔'], ['ch10', [140, 100], '宫本的屋子'],
  ['ch11', 'c11_kawajiri', '川尻家'], ['ch11', 'c11_rohan', '露伴宅(11)'], ['ch11', 'c11_alley', '幽灵小路(11)'], ['final', 'fin_home', '住宅区'],
];

(async () => {
  const { srv, url } = await serve(ROOTDIR);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 640, height: 360 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(url + 'index.html?autotest=1');
  await page.waitForFunction(() => window.G && G.booted && G.ui.menu, null, { timeout: 90000 });
  await page.evaluate(async (FILL) => {
    window.__S = null;
    G.CHAPTERS[0].run = (S) => { window.__S = S; return new Promise(() => {}); };
    G.playFrom(0);
    const t0 = Date.now();
    while (!window.__S && Date.now() - t0 < 30000) await new Promise((r) => setTimeout(r, 50));
    const S = window.__S;
    await S.setStage('map_pro', { x: 160, y: 165, music: null, fade: false });
    G.fadeA = 0;
    if (S.player) S.player.visible = false;
    const an = (G.D.bg.morioh_map.anchors = G.D.bg.morioh_map.anchors || {});
    for (const ch in FILL) for (const k in FILL[ch]) if (!an[k]) an[k] = FILL[ch][k];
    G.P4.CAL.ch11 = G.P4.CAL.ch11 || { pins: [{ at: 'c11_kawajiri', label: '川尻家' }, { at: 'c11_rohan', label: '露伴宅' }, { at: 'c11_alley', label: '幽灵小路' }], stamp: 'stamp' };
  }, FILL);
  await page.waitForTimeout(400);

  if (PINS) {
    await page.evaluate((ALL) => {
      const an = G.D.bg.morioh_map.anchors, m = G.D.ui.map || {}, P4 = G.P4;
      const img = (k) => { const im = k ? G.image(k) : null; return im && G.ready(im) ? im : null; };
      window.__pinsH = P4.overlay((g) => {
        const pim = img(m.pin && m.pin.image), meta = m.pin || { ax: 5, ay: 15 };
        for (const [, at, label] of ALL) {
          const xy = Array.isArray(at) ? at : an[at] || [160, 90];
          if (pim) g.drawImage(pim, Math.round(xy[0] * 2 - meta.ax * 2), Math.round(xy[1] * 2 - meta.ay * 2), pim.width * 2, pim.height * 2);
          P4.text(g, label, Math.round(xy[0] * 2 + 12), Math.round(xy[1] * 2 - 34), '#fff4d6', 12, 'left', '#2a0a1a');
        }
      }, { z: 1 });
    }, ALL);
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, 'pins_all.png') });
    console.log('截图 pins_all.png');
    await page.evaluate(() => window.__pinsH.close());
    // 不带图钉的底图（实机画面，2 倍）
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(OUT, 'map_only.png') });
    console.log('截图 map_only.png');
  }

  for (const key of (keys.length ? keys : PINS ? [] : ['prologue'])) {
    const t0 = Date.now();
    await page.evaluate((key) => {
      window.__cal = null;
      G.P4.calendar(window.__S, key, { hold: 60 }).then((h) => { window.__cal = h; });
    }, key);
    for (const at of AT) {
      const wait = at * 1000 - (Date.now() - t0);
      if (wait > 0) await page.waitForTimeout(wait);
      const name = `cal_${key}_${String(at).replace('.', 'p')}.png`;
      await page.screenshot({ path: path.join(OUT, name) });
      console.log('截图', name);
    }
    await page.evaluate(() => { G.P4.clearOverlays(); });
    await page.waitForTimeout(200);
  }
  console.log(errors.length ? '报错：\n' + errors.join('\n') : '无报错');
  await browser.close();
  srv.close();
})().catch((e) => { console.error(e); process.exit(1); });
