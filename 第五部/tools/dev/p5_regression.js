// 将仓库现有战斗夹具接到第五部复制的引擎，只在第五部_out里生成页面和报告。
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
process.env.NODE_PATH ||= 'D:/CodeWorkSpace/honglou-juan2/node_modules';
require('node:module').Module._initPaths();
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../../..');
const out = path.join(__dirname, '_out/regression');
const checks = [], errors = [];
function check(name, ok, detail) { checks.push({ name, ok: !!ok, detail }); }

const route = file => '/' + path.relative(root, file).split(path.sep).map(encodeURIComponent).join('/');
function fixture(name) {
  const source = path.join(root, 'tools/dev/p5');
  const html = fs.readFileSync(path.join(source, name + '.html'), 'utf8').replace(/src="([^"]+)"/g, (_, relative) => {
    const target = relative.startsWith('../../../engine/')
      ? path.join(root, '第五部/游戏/engine', path.basename(relative)) : path.resolve(source, relative);
    return `src="${route(target)}"`;
  });
  const target = path.join(out, name + '.html');
  fs.writeFileSync(target, html);
  return route(target);
}

async function main() {
  fs.mkdirSync(out, { recursive: true });
  // file: 在受管理 Chromium 中可能禁用；同源静态 HTTP 保留原夹具和断言。
  const server = http.createServer((req, res) => {
    const name = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname);
    if (name === '/favicon.ico') { res.writeHead(204).end(); return; }
    const file = path.resolve(root, '.' + name);
    if (!file.startsWith(root + path.sep) || !/\.(js|html)$/.test(file)) { res.writeHead(404).end(); return; }
    const open = fs.createReadStream(file);
    open.once('error', () => res.writeHead(404).end());
    open.once('open', () => {
      res.setHeader('Content-Type', file.endsWith('.js') ? 'text/javascript; charset=utf-8' : 'text/html; charset=utf-8');
      open.pipe(res);
    });
  });
  await new Promise((resolve, reject) => server.once('error', reject).listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + server.address().port;
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', msg => { if (['warning', 'error'].includes(msg.type())) errors.push(msg.text()); });
    const url = base + fixture('arena');
    await page.goto(url);
    await page.evaluate(() => P5.init());
    for (const method of ['aiRange', 'combos', 'dodge', 'guards', 'poise', 'wall', 'special', 'shots', 'timestop', 'cancellation', 'retry', 'finish', 'rushLoop']) {
      const r = await page.evaluate(async method => {
        let timer;
        try { return await Promise.race([P5[method](), new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(method + '超时')), 12000); })]); }
        finally { clearTimeout(timer); }
      }, method);
      switch (method) {
        case 'aiRange':
          check('原尺寸及缩小尺寸近战AI', r.every(v => v.damage > 0), r);
          await page.reload(); await page.evaluate(() => P5.init()); break;
        case 'combos': check('三连与连打时序', JSON.stringify(r.chain) === '["J1","J2","J3"]' && r.entered && r.frames >= 80 && r.frames <= 90 && r.end.cd > .45, r); break;
        case 'dodge': check('闪避无敌帧与擦身', r.hits.every(v => v.n === 12 ? v.dmg > 0 : v.dmg === 0) && JSON.stringify(r.hits.map(v => v.graze)) === '[1,1,0,0]' && r.persistentEnergy === 0, r); break;
        case 'guards': check('格挡与弹反', JSON.stringify(r.values.map(v => v.dmg)) === '[4,6,20,20]' && r.firstParry && r.parries === 1 && r.handled && r.eStun === 0, r); break;
        case 'poise': check('韧性与连打反冲', r.broken.state === 'broken' && Math.abs(r.broken.dur - 1.5) < 1e-6 && r.dmg === 12 && r.healed && r.capped === 6 && r.counter, r); break;
        case 'wall': check('撞墙反弹', r.wall && r.x < 314, r); break;
        case 'special': check('必杀能量门槛及剧情窗口', !r.normal.low && r.normal.done && r.normal.energy === 0 && !r.outside && r.invoked === 1, r); break;
        case 'shots': check('弹体反射与地火', JSON.stringify(r.out.map(v => v.side)) === '["player","enemy"]' && r.out[1].dead && r.out[1].root > 0 && r.ground && !r.cut && r.after < r.before, r); break;
        case 'timestop': check('时停冻结及结算', r.frozen && r.queued === 2 && r.hp - r.after === 12 && r.done && r.guardCleared && r.immune === 0, r); break;
        case 'cancellation': check('切场取消旧任务', !r.value && r.result.cancelled && r.result.name === 'RunCancelled' && r.runChanged, r); break;
        case 'retry': check('检查点重试', new Set(r.seen.map(v => v.e)).size === 1 && r.after1.attempt === 1 && r.after1.hp === 100 && r.after1.speed === 88 && r.assist && r.assistDmg === 14 && r.menus.at(-1).length === 3, r); break;
        case 'finish': check('胜负收尾', r.every(v => v.done && v.dead && v.standHidden), r); break;
        case 'rushLoop': {
          const byName = Object.fromEntries(r.map(v => [v.name, v]));
          check('七种中断均停止连打拳声', r.length === 7 && r.every(v => v.rushing && !v.live.length && !(v.liveInCine || []).length && !v.stale) && byName.swap.leader === 'kakyoin' && byName.bossKo.result === 'win' && byName.bossKo.bossDead, r); break;
        }
      }
    }
    check('战斗循环无异常', !(await page.evaluate(() => P5.diagnostics())).events.length);
    await page.goto(base + fixture('specials'));
    await page.evaluate(() => Specials.init());
    const matrix = await page.evaluate(() => Specials.matrix());
    const extras = await page.evaluate(() => Specials.extras());
    const boundaries = await page.evaluate(() => Specials.boundaries());
    for (const r of matrix) {
      const damage = r.cid === 'avdol' && r.mode === 'depth' ? r.damage === 0 : r.damage > 0;
      check(`${r.cid} ${r.side} ${r.mode}`, damage && r.done && r.result && r.energy === 0 && !r.cine && !r.liveShots && !r.fx.length && !r.errors.length, r);
    }
    check('平面最近目标', extras.pick.intended);
    check('零速度弹体原地', extras.speedZero.dx === 0 && extras.speedZero.dy === 0);
    check('剧情地火与空场恢复', extras.crossfire.cut === 4 && extras.crossfire.result && extras.crossfire.damage > 0 && !extras.crossfire.groundCut && extras.crossfire.groundDx === 0 && extras.noTargets.every(r => r.done && r.result && !r.cine && !r.liveShots && !r.errors.length));
    check('切场后弹体任务清空', extras.cancel.done && !extras.cancel.result && !extras.cancel.liveShots);
    for (const r of boundaries.walls) check(`${r.cid} 贴墙 ${r.side}`, r.lo >= 8 && r.hi <= 632 && r.lo <= r.hi && r.damage > 0 && r.done && r.result && !r.cine && !r.fx.length && !r.errors.length, r);
    for (const r of boundaries.outOfRange) check(`${r.cid} 超出射程`, r.damage === 0 && r.done && r.result && !r.cine && !r.liveShots && !r.errors.length, r);
    check('追踪、高度与Boss免伤', boundaries.locked && boundaries.retargeted && boundaries.heightHits === 0 && boundaries.immune.damage === 0);
    check('控制台无异常', errors.length === 0, errors);
    fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify({ ok: checks.every(v => v.ok), checks, errors }, null, 2));
    for (const failure of checks.filter(v => !v.ok)) console.error(failure.name, failure.detail);
    assert(checks.every(v => v.ok), '公共战斗/大招回归失败');
    console.log(`PASS：${checks.length}项公共战斗与六人大招回归（第五部复制引擎，无第五部剧情战斗）。`);
  } finally { if (browser) await browser.close(); server.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
