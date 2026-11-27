// 快进验收与实时有声录像共用真实键盘机器人；输出严格限制在第五部。
// --chapter prologue|ch1；--record 第五部/tools/dev/_out/两章.webm --size 1920x1080 --read 1
'use strict';
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
process.env.NODE_PATH ||= 'D:/CodeWorkSpace/honglou-juan2/node_modules';
require('node:module').Module._initPaths();
const { chromium } = require('playwright');
const { P5Bot } = require('./p5_bot');
const argv = process.argv.slice(2), opt = (k, d) => argv.includes(k) ? argv[argv.indexOf(k) + 1] : d;
const p5root = path.resolve(__dirname, '../..');
const inside = value => {
  const full = path.resolve(value), rel = path.relative(p5root, full);
  if (rel.startsWith('..') || path.isAbsolute(rel)) throw new Error('输出只能写第五部：' + value);
  return full;
};
const record = opt('--record', null), chapter = opt('--chapter', null);
const achievements = argv.includes('--achievements');
if (chapter && !['prologue', 'ch1'].includes(chapter)) throw new Error('--chapter 只支持 prologue|ch1');
const recording = record && inside(record);
if (recording && !recording.endsWith('.webm')) throw new Error('--record 需要.webm输出路径');
const out = inside(opt('--out', path.join(__dirname, '_out', recording ? 'record_' + (chapter || 'all') : 'play' + (chapter ? '_' + chapter : ''))));
const [width, height] = opt('--size', recording ? '1920x1080' : '960x540').split('x').map(Number);
assert(width > 0 && height > 0, '--size 宽x高');
const report = { ok: false, mode: recording ? 'record' : 'fast', chapter: chapter || 'all', size: [width, height], errors: [], requests: [], marks: [], dialogs: [], fights: [], shots: [], missing: {} };
const read = () => {
  const s = G.dbg.snapshot(), c = G.world.fight, h = c?.data?.charge?.h, hint = c?.spec.testHint?.(c);
  return { ...s, clk: G.clk.ui, scene: G.scene?.name, cine: !!G.world.cine, attempt: c?.attempt,
    energy: G.world.player?.energy, facing: G.world.player?.facing, menuIdx: G.ui.menu?.idx, fightHint: hint, vs: !!G.uifx.vsCur,
    taxi: c?.id === 'b_pro1_taxi' ? { x: G.S.actor('taxi')?.x, z: G.S.actor('taxi')?.z, warnLeft: h?.phase === 'warn' ? h.warn - h.t : -1, active: h?.phase === 'active', ...hint } : null,
    marks: window.__p5marks.splice(0), tbc: G.uifx.misc.some(x => x.kind === 'tbc' && x.t >= x.hit), errors: G.dbg.events.filter(e => /error|api_missing/.test(e.type)) };
};
async function main() {
  fs.mkdirSync(out, { recursive: true });
  if (recording) fs.mkdirSync(path.dirname(recording), { recursive: true });
  const server = spawn(process.env.PYTHON || 'python', [path.join(__dirname, 'p5_serve.py'), '--port', '0'], { windowsHide: true, env: { ...process.env, PYTHONUTF8: '1', PYTHONDONTWRITEBYTECODE: '1' }, stdio: ['ignore', 'pipe', 'pipe'] });
  let browser, page, stderr = '', bot, recorderStarted = false;
  server.stderr.on('data', b => { stderr += b; });
  const ready = new Promise((resolve, reject) => {
    let text = ''; const timer = setTimeout(() => reject(new Error('服务启动超时 ' + stderr)), 15000);
    server.once('error', reject);
    server.stdout.on('data', b => { text += b; if (text.includes('\n')) { clearTimeout(timer); resolve(JSON.parse(text.split('\n')[0]).url); } });
  });
  try {
    const url = await ready;
    browser = await chromium.launch({ headless: !argv.includes('--headed'), args: ['--autoplay-policy=no-user-gesture-required'] });
    page = await browser.newPage({ viewport: { width, height } });
    page.on('pageerror', e => report.errors.push(e.stack || String(e)));
    page.on('console', m => { if (m.type() === 'error') report.errors.push(m.text()); });
    page.on('requestfailed', r => report.requests.push(r.url() + ' ' + r.failure()?.errorText));
    page.on('response', r => { if (r.status() >= 400) report.requests.push(r.status() + ' ' + r.url()); });
    if (recording) {
      report.recFiles = {};
      await page.exposeFunction('__recSave', (kind, b64) => {
        const file = kind === 'full' ? recording : recording.replace(/\.webm$/, '_' + kind + '.webm');
        report.recFiles[kind] = file; fs.appendFileSync(file, Buffer.from(b64, 'base64'));
      });
      for (const suffix of ['', '_bgm', '_sfx']) { const file = recording.replace(/\.webm$/, suffix + '.webm'); if (fs.existsSync(file)) fs.unlinkSync(file); }
    }
    if (achievements) await page.goto(url + '?touch=0');
    else await page.goto(url + '?autotest=1');
    await page.waitForFunction(() => window.G?.booted && G.ui.menu?.t > .2);
    await page.keyboard.press('Shift');
    await page.evaluate(real => {
      G.dbg.hold = !real; window.__p5marks = [];
      const old = G.S.mark;
      G.S.mark = function (mark) { window.__p5marks.push({ mark, t: G.clk.ui, bossHp: G.S.actor('bucciarati')?.hp }); return old.call(this, mark); };
      const channel = new MessageChannel();
      const yieldTask = () => new Promise(r => { channel.port1.onmessage = r; channel.port2.postMessage(0); });
      window.__p5step = async frames => {
        const n0 = window.__p5marks.length;
        for (let n = 0; n < frames; n++) { G.dbg.tick(1); await yieldTask(); if (window.__p5marks.length !== n0) break; }
      };
    }, !!recording);
    if (recording) {
      await page.evaluate(() => { window.__recCleanUI = false; });
      await page.addScriptTag({ path: path.resolve(__dirname, '../../../tools/dev/record/recorder.js') });
      recorderStarted = true;
      report.capture = await page.evaluate(() => ({ canvas: [G.screen.width, G.screen.height], streams: Object.fromEntries(Object.entries(window.__recs).map(([k, r]) => [k, r.stream.getTracks().map(t => t.kind)])) }));
      await page.waitForTimeout(2500);
    }
    bot = new P5Bot(page, { record: !!recording, chapter, read: Number(opt('--read', recording ? '1' : '.08')) });
    const seen = new Set();
    const shot = async name => {
      if (seen.has(name)) return;
      seen.add(name); if (!recording) await bot.step(/card/.test(name) ? 28 : 2);
      const file = String(report.shots.length + 1).padStart(2, '0') + '_' + name + '.png';
      await page.screenshot({ path: path.join(out, file) }); report.shots.push(file);
    };
    if (!recording) bot.options.streetLife = async (id, phase) => {
      // 让开场提示自然消退，避免底部文字框挡住花盆和贴地小道具。
      if (id === 'vine' && phase === 'before') await bot.step(720);
      await shot('life_' + id + '_' + phase);
      const state = await page.evaluate(() => ({
        gravel: G.S.actor('gravel').visible, key: G.S.actor('key').visible,
        frog: !!G.S.actor('frog')?.visible, bench: G.S.actor('bench').visible,
        benchY: G.S.actor('bench').y, playerY: G.world.player.y,
      }));
      report.life ||= {}; report.life[id + '_' + phase] = state;
      assert(state.bench && state.benchY < state.playerY, '长椅应在主角脚底纵深之后');
      if (id === 'frog') { assert.equal(state.gravel, phase === 'before'); assert.equal(state.frog, phase === 'after'); }
      if (id === 'butterfly') assert.equal(state.key, phase === 'before');
    };
    await shot('title');
    const t0 = Date.now(); let progressT = 0;
    for (let i = 0; i < 30000; i++) {
      const s = await page.evaluate(read); report.last = s;
      if (Date.now() - progressT > 10000) { progressT = Date.now(); console.log('进度', s.clk.toFixed(1), s.stage, s.hp, s.fightId, s.attempt, s.fightHint?.bossHp); fs.writeFileSync(path.join(out, 'state.json'), JSON.stringify(s, null, 2)); }
      for (const m of s.marks) { report.marks.push(m); if (!/hit$|collision$|jabs$/.test(m.mark)) { console.log(m.mark); await shot(m.mark); } }
      if (s.chapter) await shot('chapter_card_' + (s.stage || 'start'));
      if (s.vs) await shot('vs_card_' + s.fightId);
      if (s.tbc) await shot('to_be_continued_' + s.stage);
      if (s.hint?.includes('出租车在右边')) await shot('hall_45s_arrow');
      if (s.stage === 'street_ch1' && bot.streetSpot >= 5 && Math.abs(s.px - 340) < 5) await shot('bench_front_occlusion');
      if (s.dlg && !report.dialogs.some(d => d.text === s.dlg)) report.dialogs.push({ who: s.dwho, text: s.dlg, pages: s.dlen });
      if (s.fightId) {
        report.fights.push({ id: s.fightId, t: s.clk, attempt: s.attempt, hp: s.hp, ...s.taxi, ...s.fightHint });
        if (s.hp <= 0) await shot('idle_loss_' + s.fightId);
        if (s.attempt === 1 && s.combat) await shot('retry_' + s.fightId);
      }
      for (const field of ['missingImg', 'missingGlyph', 'missingHead', 'missingSfx', 'fallbacks']) if (s[field]?.length) report.missing[field] = [...new Set([...(report.missing[field] || []), ...s[field]])];
      if (s.errors.length || report.errors.length) throw new Error('游戏运行报错 ' + JSON.stringify(s.errors));
      if (await bot.act(s)) break;
      await bot.step(8);
      if (Date.now() - t0 > (recording ? 3600000 : 900000)) throw new Error('试玩超时');
    }
    await bot.keys(); const end = await page.evaluate(read);
    assert(bot.finished && end.scene === 'title', '应完成所选章节并回标题');
    const marks = new Set(report.marks.map(m => m.mark)), expected = [];
    if (chapter !== 'ch1') expected.push('p5_map_stamp', 'p5_echoes_card', 'p5_taxi_freeze', 'p5_taxi_win', 'p5_banknote', 'p5_goldexp_card', 'p5_frog_hop', 'p5_prologue_end');
    if (chapter !== 'prologue') expected.push('p5_life_unneeded', 'p5_life_vine', 'p5_life_frog', 'p5_life_butterfly', 'p5_ch1_talk_passer_m', 'p5_ch1_talk_passer_f', 'p5_luca_cry', 'p5_luca_attack', 'p5_luca_reflect', 'p5_luca_down', 'p5_funicular_station', 'p5_bucciarati_cards', 'p5_zip_punch', 'p5_zip_dive', 'p5_zip_reappear', 'p5_ch1_1_win', 'p5_tracking_fly', 'p5_zip_hole', 'p5_zip_ankle', 'p5_sense_overload', 'p5_sense_recovered', 'p5_ch1_2_win', 'p5_harbor_alliance', 'p5_ch1_end');
    for (const mark of expected) assert(marks.has(mark), '缺关键节拍 ' + mark);
    if (!recording) {
      for (const id of new Set(report.fights.map(f => f.id).filter(id => !id.startsWith('b_p5_')))) {
        assert(bot.losses.has(id), id + '不操作应该输并重试');
        const retry = report.fights.find(f => f.id === id && f.attempt === 1);
        assert(retry && retry.hp === (id === 'b_pro1_taxi' ? 100 : 120), id + '重试满血');
        if (id !== 'b_pro1_taxi') assert.equal(retry.bossHp, 140, id + '重试恢复对手血量');
      }
      if (chapter !== 'ch1') {
        assert(bot.arrowSeen, '45秒后出现出口箭头');
        for (const id of ['info', 'flight', 'passer_m', 'passer_f', 'belt']) assert(marks.has('p5_inspect_' + id), '未调查 ' + id);
        assert(report.fights.some(f => f.id === 'b_pro1_taxi' && f.attempt === 1 && f.dodges > 0 && f.freezes > 0), '出租车K闪避与U冻结');
      }
    }
    if (chapter !== 'prologue') {
      const one = report.fights.filter(f => f.id === 'b_ch1_1');
      assert(report.marks.some(m => m.mark === 'p5_ch1_1_win' && m.bossHp === 56) && one.filter(f => f.bossHp != null).every(f => f.bossHp >= 56), '车厢40%转场');
      assert(report.marks.some(m => m.mark === 'p5_ch1_2_win' && m.bossHp === 0), '广场击败布加拉提');
      const start = report.marks.find(m => m.mark === 'p5_sense_overload'), stop = report.marks.find(m => m.mark === 'p5_sense_recovered');
      assert(stop.t - start.t >= 3 && stop.t - start.t < 4, '感觉失控持续三秒');
    }
    if (!chapter) {
      const episodes = await page.evaluate(() => Object.entries(G.P5_EPISODES).map(([key, ep]) => ({
        key, battles: ep.scenes.flatMap((scene, i) => scene.fight ? ['b_p5_' + key + '_' + (i + 1)] : []),
      })));
      assert.deepEqual(episodes.map(e => e.key), ['ch2','ch3','ch4','ch5','ch6','ch7','ch8','final']);
      for (const ep of episodes) {
        assert(marks.has('p5_' + ep.key + '_clear'), '没有打完 ' + ep.key);
        for (const id of ep.battles) assert(marks.has(id + '_win'), '没打赢 ' + id);
      }
      assert(marks.has('p5_campaign_special'), '新章节必杀键未触发');
      if (!recording) assert(bot.campaignRetry, '没有重试新增战斗');
      assert.deepEqual(await page.evaluate(() => G.store.get('p5-progress', null)), { v: 1, max: 9, last: 9, clear: true });
      await shot('returned_title');
      await page.reload();
      await page.waitForFunction(() => G.booted && G.scene?.name === 'title');
      assert.deepEqual(await page.evaluate(() => ({ max: G.progress.max, clear: G.progress.clear })), { max: 9, clear: true });
    }
    if (achievements) {
      report.achievements = await page.evaluate(() => ({
        got: G.ach.list().filter(def => G.ach.has(def.id)).map(def => def.id),
        story: G.ach.list('story').map(def => def.id), battles: G.ach.list('battle').map(def => def.id),
        progress: G.store.get('p5-achievements', null), part3: G.store.get('ach', null),
      }));
      const { got, story, battles, progress, part3 } = report.achievements;
      assert.equal(part3, null, '第五部不应使用第三部存档');
      const earned = new Set(got);
      const needed = chapter === 'ch1' ? ['chapter_ch1', 'b_ch1_1', 'b_ch1_2', 'life_pair'] :
        chapter === 'prologue' ? ['chapter_prologue', 'b_pro1_taxi', 'taxi_freeze'] :
          [...story, ...battles, 'life_pair', 'three_clues', 'taxi_freeze'];
      if (!recording) needed.push('retry_win');
      for (const id of needed) assert(earned.has(id), '未解锁真实游玩成就 ' + id);
      assert(got.every(id => progress.got[id] > 0), '新成就应有真实解锁时间');
    }
    assert.deepEqual(report.missing, {}, '缺图缺字或动作回退');
    assert(report.dialogs.every(d => d.pages === 1), '对话不应拆页');
    assert.deepEqual(report.errors, []); assert.deepEqual(report.requests, []);
    report.save = await page.evaluate(() => ({ p5: G.store.get('p5-progress', null), p4: G.store.get('p4-progress', null), overlays: G.P5.layers.length }));
    assert.equal(report.save.p4, null); assert.equal(report.save.overlays, 0, '回标题清理特效');
    await shot('returned_title'); report.realSeconds = (Date.now() - t0) / 1000; report.gameSeconds = end.clk; report.ok = true;
    console.log('PASS：真实键盘通关并回标题，剧情标记齐全，控制台0错误。');
  } catch (e) {
    report.failure = e.stack || String(e);
    if (page) { report.last = await page.evaluate(() => window.G?.dbg?.snapshot()).catch(() => null); await page.screenshot({ path: path.join(out, 'failure.png') }).catch(() => {}); }
    throw e;
  } finally {
    if (page && recorderStarted) {
      await page.evaluate(() => window.__recStop()); await page.waitForFunction(() => window.__recPending === 0, null, { timeout: 120000 });
      report.recBytes = Object.fromEntries(Object.entries(report.recFiles).map(([k, f]) => [k, fs.statSync(f).size])); console.log('录像已写入', JSON.stringify(report.recBytes));
    }
    fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
    if (browser) await browser.close();
    if (server.exitCode === null) { const closed = new Promise(r => server.once('exit', r)); server.kill(); await closed; }
  }
}
main().catch(e => { console.error(e); process.exitCode = 1; });
