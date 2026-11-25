// 对照图的旧列保留原绘制方式，仅用于验收，运行包只读取生成后的道具图。
'use strict';
const fs = require('node:fs'), path = require('node:path');
const { spawnSync } = require('node:child_process');
process.env.NODE_PATH ||= 'D:/CodeWorkSpace/honglou-juan2/node_modules';
require('node:module').Module._initPaths();
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../..'), out = path.join(__dirname, '_out');
const old = spawnSync(process.env.PYTHON || 'python', ['-c', `import sys,io,json,base64
sys.path.insert(0, sys.argv[1])
import props5
result={}
for key, draw in props5.PROPS.items():
    stream=io.BytesIO(); draw().img().save(stream, format='PNG')
    result[key]='data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()
print(json.dumps(result))`, path.join(root, 'tools/art')], { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1' }, windowsHide: true });
if (old.status !== 0) throw new Error(old.stderr);
const generated = Object.fromEntries(Object.entries(JSON.parse(fs.readFileSync(path.join(root, 'assets/_meta/props.json'), 'utf8')).props)
  .filter(([, m]) => m.source).map(([key, m]) => [key, 'data:image/png;base64,' + fs.readFileSync(path.join(root, 'assets', m.image + '.png')).toString('base64')]));
async function main() {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 1530 }, deviceScaleFactor: 1 });
    await page.setContent('<body style="margin:0"><canvas width="1280" height="1530"></canvas>');
    await page.evaluate(async ({ old, generated }) => {
      const g = document.querySelector('canvas').getContext('2d');
      g.fillStyle = '#211c2c'; g.fillRect(0, 0, 1280, 1530); g.imageSmoothingEnabled = false;
      g.font = '22px "Microsoft YaHei", sans-serif'; g.fillStyle = '#ffe29c';
      g.fillText('第五部道具 · 原代码版 / 生图版（均按游戏像素放大 4 倍）', 28, 40);
      const names = ['taxi', 'taxi_hit', 'suitcase', 'shovel', 'frog', 'frog_hop', 'ladybug', 'butterfly', 'vine', 'zipper', 'banknote', 'insect_light'];
      const labels = ['出租车', '受损出租车', '行李箱', '铲子', '青蛙', '跳跃青蛙', '瓢虫', '蝴蝶', '藤蔓与花盆', '拉链口', '纸币', '追踪虫'];
      async function image(uri, x, y) {
        const im = new Image(); im.src = uri; await im.decode();
        g.drawImage(im, x - im.width * 2, y - im.height * 4, im.width * 4, im.height * 4);
      }
      function runtime(key, x, y) {
        g.save(); g.translate(x, y); g.scale(4, 4);
        if (key === 'vine') {
          g.fillStyle = '#733c38'; g.fillRect(-5, -7, 10, 7); g.fillStyle = '#d8915b'; g.fillRect(-6, -9, 12, 3);
          g.strokeStyle = '#4d8c52'; g.lineWidth = 2; g.beginPath(); g.moveTo(0, -9);
          for (let yy = 0; yy <= 30; yy += 2) g.lineTo(Math.sin(yy / 7) * 4, -9 - yy);
          g.stroke(); g.fillStyle = '#9abf68';
          for (let yy = 5; yy < 30; yy += 7) g.fillRect(Math.sin(yy / 7) * 4 + (yy % 2 ? -5 : 1), -10 - yy, 5, 3);
        } else if (key === 'butterfly') {
          g.translate(0, -5); const w = 6;
          g.fillStyle = '#ffeaa2'; g.fillRect(-w, -3, w * 2, 5); g.fillStyle = '#bb738d'; g.fillRect(-w, -1, w * 2, 2);
          g.fillStyle = '#4b304c'; g.fillRect(0, -3, 1, 6);
        } else if (key === 'zipper') {
          g.translate(0, -5); const w = 14;
          g.fillStyle = '#140f26'; g.fillRect(-w, -3, w * 2, 6); g.strokeStyle = '#c7b4f4'; g.lineWidth = 1; g.strokeRect(-w, -4, w * 2, 8);
          for (let xx = -w; xx < w; xx += 5) { g.fillStyle = '#e1d7ed'; g.fillRect(xx, -4, 2, 2); g.fillRect(xx + 2, 2, 2, 2); }
        } else if (key === 'banknote') {
          // 原纸币在640 UI层以15×9绘制，此处折算回320世界像素。
          g.scale(.5, .5); g.translate(0, -5);
          g.fillStyle = '#1b332b'; g.fillRect(-7, -4, 15, 9); g.fillStyle = '#add59b'; g.fillRect(-6, -3, 13, 7); g.fillStyle = '#4e865b'; g.fillRect(-1, -2, 3, 5);
        } else if (key === 'insect_light') {
          g.translate(0, -2); g.fillStyle = '#f8e69c'; g.fillRect(-2, -2, 4, 4); g.fillStyle = '#fffbea'; g.fillRect(-4, -1, 2, 1); g.fillRect(2, -3, 2, 1);
        }
        g.restore();
      }
      for (let i = 0; i < names.length; i++) {
        const key = names[i], x = 20 + i % 2 * 630, y = 65 + Math.floor(i / 2) * 240;
        g.fillStyle = '#30293d'; g.fillRect(x, y, 610, 230);
        g.font = '17px "Microsoft YaHei", sans-serif'; g.fillStyle = '#efe3cb'; g.fillText(labels[i] + ' / ' + key, x + 12, y + 25);
        g.fillStyle = '#bdb3c5'; g.fillText('原代码版', x + 120, y + 53); g.fillText('生图版', x + 420, y + 53);
        const baseline = y + 222;
        if (old[key]) await image(old[key], x + 160, baseline); else runtime(key, x + 160, baseline);
        await image(generated[key], x + 460, baseline);
      }
    }, { old: JSON.parse(old.stdout), generated });
    await page.screenshot({ path: path.join(out, 'props.png') });
    console.log('道具对照图：' + path.join(out, 'props.png'));
  } finally { await browser.close(); }
}
main().catch(e => { console.error(e); process.exitCode = 1; });
