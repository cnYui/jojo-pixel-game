// 成就系统的纯逻辑检查（没有浏览器）：node tools\dev\full\ach_logic_check.js
//   造一个最小的 window.G（存档用内存 Map，章节表取 main.js 里的 names，EXTRA / progress / TRIAL 用 stub），
//   再把 engine\achievements.js → story\achievements_def.js → engine\ui_ach.js 依次跑一遍，逐条断言。
//   ⚠ 这是"接进游戏前的自检"：判定全过不等于页面好看，页面和真实存档还要在浏览器里走一遍。
'use strict';
global.window = global;
const path = require('path');
const ROOT = path.resolve(__dirname, '../../..');

// ---------------------------------------------------------------- 最小 G
// 存档：内存 Map；get/set 走 JSON 往返，和 engine\core.js 的 G.store 行为一致（读到的是副本，不是同一个对象）
const mem = new Map();
const hooks = [];
const store = {
  get(key, def) { return mem.has(key) ? JSON.parse(mem.get(key)) : def; },
  set(key, val) { mem.set(key, JSON.stringify(val)); },
  remove(key) { mem.delete(key); },
  reload() { hooks.forEach(fn => fn()); },
  onLoad(fn) { hooks.push(fn); },
  flush() {}, status() { return { local: true, xhs: null, hasXhs: false, stamp: 0 }; },
};
// main.js 的章节表（key / title / sub 三样就够；顺序就是成就里的 idx）
const NAMES = [
  ['prologue', '序章　东京', '替身之名'], ['ch1', '第1章　香港', '灰塔与银色战车'],
  ['ch2', '第2章　南海', '南海漂流'], ['ch3', '第3章　新加坡', '新加坡的恶意'],
  ['ch4', '第4章　印度', '两只右手的男人'], ['ch5', '第5章　巴基斯坦', '公路、浓雾与卡拉奇'],
  ['ch6', '第6章　阿拉伯', '沙漠的太阳与梦'], ['ch7', '第7章　红海', '许愿与大嘴'],
  ['ch8', '第8章　埃及沙漠', '九荣神：沙与预言'], ['ch9', '第9章　尼罗河', '刀、磁铁与影子'],
  ['ch10', '第10章　开罗', '赌局与看门鸟'], ['ch11', '第11章　DIO的馆', '日落之前'],
  ['final', '终章　DIO的世界', '直到黎明'],
];
const CHAPTERS = NAMES.map(([key, title, sub]) => ({ key, title, sub }));
// 挑战登记表的 stub：id 和章 key 对应（和 story\{chNN,final}.js 里登记的一样，够反查所属章）
const CHALLENGES = [
  { id: 'b02_chariot', chapter: 'ch1' }, { id: 'b12_sun', chapter: 'ch6' }, { id: 'b18a_anubis', chapter: 'ch9' },
  { id: 'b26b_cream', chapter: 'ch11' }, { id: 'b28d3_dio', chapter: 'final' },
];
// extras 的 stub：state / has / rankOf / wonOnce 按测试里现填的数据返回
const EXT = { won: 0, ranks: {}, souv: [], HAS: {}, WONONCE: {} };
const G = global.G = {
  CHAPTERS, DEMO: null,
  store,
  dbg: { autotest: false, ev() {}, missingImg: new Set(), missingGlyph: new Set() },
  clk: { ui: 0, world: 0, flow: 0 },
  mod: (a, n) => ((a % n) + n) % n,
  clamp: (v, a, b) => (v < a ? a : v > b ? b : v),
  cancelIgnore() {},
  cancelled: e => !!(e && e.name === 'RunCancelled'),
  runPromise: ex => new Promise(ex),
  setScene(s) { G.scene = s; },
  scene: null,
  fadeA: 0,
  EXTRA: {
    CHALLENGES, SOUVENIRS: [],
    state() { return { ranks: Object.assign({}, EXT.ranks), won: EXT.won, souv: EXT.souv.slice(), challenges: CHALLENGES.map(d => d.id) }; },
    has(id) { return !!EXT.HAS[id]; },
    rankOf(id) { return EXT.ranks[id] || null; },
    wonOnce(id) { return !!EXT.WONONCE[id]; },
    challengeResult: async () => 2, challengeMenu: async () => null,
  },
  // 累计游玩秒数：play 事件里带了 sec 就按它记，没带就读这份（和 main.js 的 progress.info() 一致）
  progress: { info: () => ({ play: EXT.play || 0 }) },
  TRIAL: { CFG: { FAST: 2700, FAST2: 1800 } },
};
G.ui = { box() {}, draw() {}, drawTop() {}, update() {} };

// ---------------------------------------------------------------- 加载被测文件
require(path.join(ROOT, 'engine/achievements.js'));
require(path.join(ROOT, 'story/achievements_def.js'));
require(path.join(ROOT, 'engine/ui_ach.js'));
const A = G.ach;

// ---------------------------------------------------------------- 断言
let fails = 0, passes = 0;
// 一场新的战斗：extra 的 won 数跟着涨（战斗成就按 G.EXTRA.state().won 数不同的战斗）
function win(o) { EXT.won++; return EV.fight_won(Object.assign({ id: 'w' + EXT.won }, o)); }
function ok(cond, msg) {
  if (cond) { passes++; return true; }
  fails++;
  console.log('  ✗ ' + msg);
  return false;
}
const eq = (a, b, msg) => ok(a === b, msg + '（实际 ' + JSON.stringify(a) + '，期望 ' + JSON.stringify(b) + '）');
// 重开一份干净的存档（模拟刷新页面：存档留着，G.ach 重新建）
function reload() { A.reload(); }
// 清存档 + 把 EXTRA / DEMO / 进度这些测试数据一起复位（否则前一段的桩数据会漏到下一段）
function resetSave() {
  mem.clear();
  EXT.won = 0; EXT.ranks = {}; EXT.souv = []; EXT.HAS = {}; EXT.WONONCE = {}; EXT.play = 0; EXT.swapN = 0;
  CHALLENGES.forEach(c => delete EXT.WONONCE[c.id]);
  G.EXTRA.SOUVENIRS = [];
  G.DEMO = null;
  hooks.forEach(fn => fn());
}

// 每条成就的"喂什么事件"：从定义里找它认的事件，按 id 给最小 payload
const TIER_PTS = { bronze: 5, silver: 10, gold: 20, platinum: 40 };
const EV = {
  chapter_done: i => ({ idx: i, key: CHAPTERS[i].key }),
  fight_won: o => Object.assign({ id: 'x', chapter: 'ch1', mode: 'story', rank: 'B', score: 70, time: 60, hurt: 0, hpLeft: 1,
    parry: 0, graze: 0, rushHits: 0, special: 0, attempts: 1, assist: false, losable: true, lead: 'jotaro', trial: false }, o),
  timestop: o => Object.assign({ by: 'jotaro' }, o),
  special: () => ({}),
  // main.js 的 persist() 发的是 { sec: progress.play }：这里同时把桩里的 play 抬上去，等价于"玩够时长"
  play: o => { const sec = o && o.sec != null ? o.sec : 0; EXT.play = Math.max(EXT.play || 0, sec); return { sec }; },
  swap: o => Object.assign({ to: 'joseph' }, o),
  investigate: () => ({}),
  souvenir: () => ({}),
  trial_start: () => ({ squad: ['jotaro', 'polnareff'] }),
  trial_stage: o => Object.assign({ n: 1, id: 'b01', rank: 'A', hurt: 0, alive: 2, squad: ['jotaro', 'polnareff'],
    stages: 1, flawless: 0, sptw: 0, ranks: {} }, o),
  trial_down: () => ({ cid: 'polnareff', n: 3 }),
  trial_clear: o => Object.assign({ time: 3600, downs: 1, squad: ['jotaro', 'polnareff'], ranks: {}, flawless: 0, sptw: 0, n: 18 }, o),
  trial_over: () => ({ n: 1, id: 'b05', downs: 3 }),
  dio_growth: () => ({}),
  dio_play_dead: () => ({}),
};
// 每条成就最少喂几次（计数类要喂到阈值）
const ALL = A.list();

// ---------------------------------------------------------------- ① 总数 / 总点数
console.log('① 清单：62 条、785 点');
eq(ALL.length, 62, '总数 62');
let pts = 0;
ALL.forEach(d => { pts += TIER_PTS[d.tier] || 0; });
eq(pts, 785, '总点数 785');
eq(ALL.filter(d => d.cat === 'story').length, 45, '剧情 45');
eq(ALL.filter(d => d.cat === 'trial').length, 16, '试炼 16');
eq(ALL.filter(d => d.cat === 'meta').length, 1, '白金 1');
eq(ALL[ALL.length - 1].id, 'platinum', '白金排最后');
// 章节 13 条的 id / 名字 / 等级照成就文档 §2.1
const CH_TIER = ['bronze', 'bronze', 'bronze', 'bronze', 'bronze', 'silver', 'silver', 'silver', 'silver', 'gold', 'gold', 'gold', 'gold'];   // 序章 + 第 1–4 章铜、第 5–8 章银、第 9 章起金（成就文档 §2.1）
CHAPTERS.forEach((c, i) => {
  const cid = 'ch_' + c.key.replace(/^ch(?=\d)/, '');   // ch_prologue / ch_1 … ch_final
  const d = ALL.find(x => x.id === cid);
  ok(!!d, '章节成就存在：' + cid);
  if (!d) return;
  eq(d.name, c.sub, '章节成就名字 ' + d.id);
  eq(d.tier, CH_TIER[i], '章节成就等级 ' + d.id);
});
// id 不重复
eq(new Set(ALL.map(d => d.id)).size, ALL.length, 'id 不重复');
// 每条都有名字和说明（白金也有）
ok(ALL.every(d => d.name && d.desc), '每条都有名字和说明');

// ---------------------------------------------------------------- ② 逐条喂事件能解锁；计数类 n-1 次不解锁、第 n 次解锁
// 先把每条成就写成"怎么解锁"的步骤：{ once: [事件…] } 或 { times: [事件×n] }
function stepsFor(d) {
  switch (d.id) {
    case 'foes_5': return { times: 5, ev: () => win({}) };
    case 'foes_15': return { times: 15, ev: () => win({}) };
    case 'foes_all': return { times: 1, ev: () => win({}), prep: () => { CHALLENGES.forEach(c => { EXT.WONONCE[c.id] = true; }); } };
    case 'rank_s_1': return { times: 1, ev: () => win({ rank: 'S' }) };
    case 'rank_s_10': return { times: 10, ev: () => { const id = 's' + Object.keys(EXT.ranks).length; EXT.ranks[id] = { rank: 'S' }; return win({ id, rank: 'S' }); } };
    case 'rank_s_all': return { times: 1, ev: () => win({ id: 'b02_chariot' }), prep: () => { CHALLENGES.forEach(c => { EXT.ranks[c.id] = { rank: 'S' }; }); } };
    case 'no_hit': return { times: 1, ev: () => win({ losable: true, hurt: 0 }) };
    case 'last_stand': return { times: 1, ev: () => win({ hpLeft: 0.05 }) };
    case 'parry_8': return { times: 1, ev: () => win({ parry: 8 }) };
    case 'graze_8': return { times: 1, ev: () => win({ graze: 8 }) };
    case 'ora_100': return { times: 1, ev: () => win({ rushHits: 100 }) };
    case 'special_10': return { times: 10, ev: () => EV.special({}) };
    case 'comeback': return { times: 1, ev: () => win({ attempts: 4 }) };
    case 'sptw_first': return { times: 1, ev: () => EV.timestop({ by: 'jotaro' }) };
    case 'sptw_30': return { times: 30, ev: () => EV.timestop({ by: 'jotaro' }) };
    case 'dio_growth': return { times: 1, ev: () => EV.dio_growth({}), hook: true };
    case 'dio_play_dead': return { times: 1, ev: () => EV.dio_play_dead({}), hook: true };
    case 'souv_10': return { times: 10, ev: () => { EXT.souv.push('s' + EXT.souv.length); return EV.souvenir({ n: EXT.souv.length }); } };
    case 'souv_all': return { times: 1, ev: () => EV.souvenir({}), prep: () => {
      G.EXTRA.SOUVENIRS = [{ id: 'a1', chapter: 'ch1' }, { id: 'a2', chapter: 'ch2' }];
      G.EXTRA.SOUVENIRS.forEach(s => { EXT.HAS[s.id] = true; });
    } };
    case 'look_30': return { times: 30, ev: () => EV.investigate({}), hook: true };
    case 'swap_50': return { times: 50, ev: () => EV.swap({ to: 'joseph' }), hook: true };
    // 开场队长是承太郎，换到其余 5 个人就够了
    case 'leaders_6': { let n = 0; return { times: 5, ev: () => EV.swap({ to: ['joseph', 'avdol', 'kakyoin', 'polnareff', 'iggy'][n++ % 5] }), hook: true }; }   // 闭包计数：不依赖 prep（⑤ 会在每次循环里重复调 prep）
    case 'challenge_first': return { times: 1, ev: () => win({ mode: 'challenge' }) };
    case 'play_3h': return { times: 1, ev: () => EV.play({ sec: 10800 }) };
    case 'play_10h': return { times: 1, ev: () => EV.play({ sec: 36000 }) };
    case 'trial_start': return { times: 1, ev: () => EV.trial_start({}) };
    case 'trial_clear': return { times: 1, ev: () => EV.trial_clear({}) };
    case 'trial_5': return { times: 1, ev: () => EV.trial_stage({ n: 5 }) };
    case 'trial_10': return { times: 1, ev: () => EV.trial_stage({ n: 10 }) };
    case 'trial_15': return { times: 1, ev: () => EV.trial_stage({ n: 15 }) };
    case 'trial_no_loss': return { times: 1, ev: () => EV.trial_clear({ downs: 0, squad: ['jotaro', 'polnareff'] }) };
    case 'trial_solo': return { times: 1, ev: () => EV.trial_clear({ squad: ['jotaro'] }) };
    case 'trial_duo': return { times: 1, ev: () => EV.trial_clear({ squad: ['polnareff', 'jotaro'] }) };
    case 'trial_fast': return { times: 1, ev: () => EV.trial_clear({ time: 2700 }) };
    case 'trial_fast2': return { times: 1, ev: () => EV.trial_clear({ time: 1800 }) };
    case 'trial_s_all': return { times: 1, ev: () => {
      const ranks = {};
      for (let i = 1; i <= 18; i++) ranks['s' + i] = { rank: 'S' };
      return EV.trial_clear({ ranks, n: 18 });
    } };
    case 'trial_flawless_5': return { times: 1, ev: () => EV.trial_stage({ flawless: 5 }) };
    case 'trial_time_30': return { times: 1, ev: () => EV.trial_stage({ sptw: 30 }) };
    case 'trial_last_one': return { times: 1, ev: () => EV.trial_stage({ alive: 1, squad: ['jotaro', 'polnareff'] }) };
    case 'trial_down_first': return { times: 1, ev: () => EV.trial_down({}) };
    case 'trial_fail_10': return { times: 10, ev: () => EV.trial_over({}) };
    case 'platinum': return null;     // 单独测（⑤）
    default:
      if (d.id.indexOf('ch_') === 0) {
        const key = d.id.slice(3), i = CHAPTERS.findIndex(c => c.key === key || c.key === 'ch' + key);   // 成就 id 是 ch_prologue / ch_1 … ch_final
        return { times: 1, ev: () => EV.chapter_done(i) };
      }
      // 其余全是"打赢某一场 / 某个条件"的战斗成就
      if (d.on.fight_won) return { times: 1, ev: () => EV.fight_won({ id: d.scope || 'x' }) };
      return null;
  }
}

// 每条都在一份干净的存档里单独喂：不被别的成就顺带解开干扰，也方便断言"还差一次"
console.log('② 逐条喂事件');
A.enable(true);
for (const d of ALL) {
  if (d.id === 'platinum') continue;
  const st = stepsFor(d);
  if (!ok(st, '有喂事件的办法：' + d.id)) continue;
  resetSave();
  A.enable(true);
  const evName = Object.keys(d.on)[0];
  const fire = ev => (st.hook ? A.dbgHook(evName, ev) : A.emit(evName, ev));
  const times = st.times || 1;
  if (st.prep) st.prep();
  for (let k = 0; k < times - 1; k++) fire(st.ev());
  if (times > 1) ok(!A.has(d.id), d.id + '：喂 ' + (times - 1) + ' 次不该解锁');
  fire(st.ev());
  ok(A.has(d.id), d.id + '：第 ' + times + ' 次该解锁');
}
// 顺带：autowin 判胜的战斗不算
resetSave();
A.enable(true);
A.emit('fight_won', EV.fight_won({ autowin: true, rank: 'S' }));
ok(!A.has('first_win') && !A.has('rank_s_1'), 'autowin 判胜不算');
A.emit('timestop', EV.timestop({ by: 'dio' }));
ok(!A.has('sptw_first'), 'DIO 停时间不算承太郎的 sptw_first');

// ---------------------------------------------------------------- ③ 存档往返
console.log('③ 存档往返');
resetSave();
A.enable(true);
A.emit('fight_won', EV.fight_won({ id: 'b02_chariot' }));
ok(A.has('win_chariot'), '存档往返前：已解锁 win_chariot');
A.emit('swap', EV.swap({ to: 'joseph' }));
A.flush();
const saved = mem.get('ach');
ok(!!saved, '写了 ach 键');
ok(JSON.parse(saved).v === 1, '版本号 v:1');
// 新建一份 G.ach：读同一个 store
delete require.cache[require.resolve(path.join(ROOT, 'engine/achievements.js'))];
require(path.join(ROOT, 'engine/achievements.js'));
// 定义是 achievements_def.js 在加载时注册进当时那份 G.ach 的：换了新实例要把定义也重新载一遍
delete require.cache[require.resolve(path.join(ROOT, 'story/achievements_def.js'))];
require(path.join(ROOT, 'story/achievements_def.js'));
const A2 = G.ach;
A2.enable(true);
ok(A2.has('win_chariot'), '新建的 G.ach 读到 win_chariot');
eq(A2.count('swap'), 1, '新建的 G.ach 读到计数 swap=1');
ok(A2.at('win_chariot') > 0, '解锁时间戳 > 0');
// 坏存档：不是对象 / 版本不对，当空
mem.set('ach', JSON.stringify('坏了'));
A2.reload();
eq(A2.summary().got, 0, '坏存档（字符串）当空');
mem.set('ach', JSON.stringify({ v: 2, got: { win_chariot: 1 } }));
A2.reload();
eq(A2.summary().got, 0, 'v!==1 当空');
// 回读：容器里更新了一份，G.store.reload 之后成就跟着变
A2.enable(true);
A2.emit('fight_won', EV.fight_won({ id: 'b12_sun' }));
ok(A2.has('win_sun'), '解锁 win_sun');
mem.set('ach', JSON.stringify({ v: 1, got: {}, cnt: {}, sets: {} }));
hooks.forEach(fn => fn());
ok(!A2.has('win_sun'), 'G.store.reload 之后跟着存档重读（清空）');

// ---------------------------------------------------------------- ④ enable(false)：什么都不发生
console.log('④ enable(false)');
resetSave();
A.enable(false);
A.emit('chapter_done', EV.chapter_done(0));
A.add('swap', 5);
A.unlock('first_win');
A.dbgHook('swap', EV.swap({ to: 'joseph' }));
eq(A.summary().got, 0, '关闭时不解锁');
eq(A.count('swap'), 0, '关闭时不计数');
ok(!mem.has('ach'), '关闭时不写存档');
A.enable(true);

// ---------------------------------------------------------------- ⑤ platinum 要等其余 61 条
console.log('⑤ platinum');
resetSave();
A.enable(true);
const others = A.list().filter(d => d.id !== 'platinum');
let guard = 0;
for (const d of others) {
  const st = stepsFor(d);
  if (!st) { ok(false, '有解锁办法：' + d.id); continue; }
  if (st.prep) st.prep();
  const evName = Object.keys(d.on)[0];
  for (let k = 0; k < (st.times || 1); k++) {
    if (k && st.prep) st.prep();
    st.hook ? A.dbgHook(evName, st.ev()) : A.emit(evName, st.ev());
    if (++guard > 5000) break;
  }
}
const missing = others.filter(d => !A.has(d.id));
eq(missing.length, 0, '其余 61 条都能解锁（缺：' + missing.map(d => d.id).join(',') + '）');
ok(A.has('platinum'), '其余全解锁后 platinum 解锁');
// fork：少一条时不解锁
resetSave();
A.enable(true);
savePush({ v: 1, got: Object.fromEntries(others.filter(d => d.id !== 'trial_solo').map(d => [d.id, 1])), cnt: {}, sets: {} });
hooks.forEach(fn => fn());
A.recheck();
ok(!A.has('platinum'), '差一条（trial_solo）时 platinum 不解锁');
function savePush(o) { mem.set('ach', JSON.stringify(o)); }

// ---------------------------------------------------------------- ⑥ 体验版过滤
console.log('⑥ G.DEMO');
resetSave();
G.DEMO = { last: 1 };
const demoList = A.list();
A.list();                                     // 重建缓存后再取一次，确认缓存跟着 DEMO 走
ok(demoList.every(d => d.cat !== 'trial'), '体验版没有 trial 类');
ok(demoList.some(d => d.id === 'ch_prologue') && demoList.some(d => d.id === 'ch_1'), '体验版有 ch_prologue / ch_1');
ok(!demoList.some(d => d.id === 'ch_2'), '体验版没有 ch_2');
ok(!demoList.some(d => d.id === 'ch_final'), '体验版没有 ch_final');
ok(demoList.some(d => d.id === 'platinum'), '体验版仍有白金（条件改成"当前列表其余全解锁"）');
// 体验版里战斗成就按所属章过滤：b02_chariot 属第1章（开放），b12_sun 属第6章（不开放）
ok(demoList.some(d => d.id === 'win_chariot'), '体验版有 win_chariot（第1章）');
ok(!demoList.some(d => d.id === 'win_sun'), '体验版没有 win_sun（第6章）');
// 体验版的白金：当前列表里除自己全解锁才解锁
A.enable(true);
const dl = A.list().filter(d => d.id !== 'platinum');
savePush({ v: 1, got: Object.fromEntries(dl.map(d => [d.id, 1])), cnt: {}, sets: {} });
hooks.forEach(fn => fn());
A.recheck();
ok(A.has('platinum'), '体验版：当前列表全解锁后白金解锁');
const s = A.summary();
eq(s.total, demoList.length, '体验版 summary.total = 当前列表条数');
G.DEMO = null;
const full = A.summary();
eq(full.total, 62, '去掉 DEMO 之后回到 62 条');

// ---------------------------------------------------------------- 迁移出来的两条备用断言
console.log('⑦ 其它');
resetSave();
A.enable(true);
eq(A.summary().ptsTotal, 785, 'ptsTotal 785');
A.unlock('first_win');
A.unlock('first_win');
eq(A.summary().got, 1, 'unlock 幂等');
// 章节成就懒初始化：定义里没有 ch_ 的话 G.CHAPTERS 变了也要能补
eq(A.list().filter(d => d.id.indexOf('ch_') === 0).length, 13, '章节成就 13 条');

console.log('\n' + (fails ? '✗ ' + fails + ' 条失败' : '✓ 全部通过') + '（' + passes + ' 条断言）');
process.exit(fails ? 1 : 0);
