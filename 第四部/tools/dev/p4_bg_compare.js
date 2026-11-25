// 复用生产背景渲染器，避免在 Python 重写视差、动画条和开关的绘制规则。
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  const browser = await chromium.launch();
  const result = [];
  const errors = [];
  try {
    for (const item of input) {
      const rows = item.rows.map(row => ({ label: row.label }));
      for (const side of ['old', 'new']) {
        // 每侧独立页面，避免反射图层的内部缓存沿用上一侧贴图。
        const page = await browser.newPage();
        page.on('pageerror', e => errors.push(String(e)));
        await page.addScriptTag({ path: path.resolve(__dirname, '../../游戏/engine/core.js') });
        await page.evaluate(async images => {
          const loaded = {};
          for (const [key, uri] of Object.entries(images)) {
            const im = new Image(); im.src = uri; await im.decode(); loaded[key] = im;
          }
          Object.assign(G, { image: key => loaded[key],
            ready: im => im.complete && im.naturalWidth > 0,
            dbg: { ev: (type, data) => { throw new Error(type + JSON.stringify(data)); } } });
        }, item.images[side]);
        await page.addScriptTag({ path: path.resolve(__dirname, '../../游戏/engine/bg.js') });
        const captures = await page.evaluate(({ spec, rows }) => rows.map(row => {
          const cv = document.createElement('canvas'); cv.width = 320; cv.height = 180;
          const g = cv.getContext('2d'); g.imageSmoothingEnabled = false;
          g.fillStyle = '#000'; g.fillRect(0, 0, 320, 180);
          G.cam.y = row.y;
          const bg = new G.Background(spec), stage = { state: row.state, camY: row.y };
          bg.draw(g, row.x, 0, stage); bg.drawFg(g, row.x, 0, stage);
          return cv.toDataURL('image/png').split(',')[1];
        }), { spec: item.spec, rows: item.rows });
        captures.forEach((capture, i) => { rows[i][side] = capture; });
        await page.close();
      }
      result.push({ key: item.key, rows });
    }
    if (errors.length) throw new Error(errors.join('\n'));
    process.stdout.write(JSON.stringify(result));
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
