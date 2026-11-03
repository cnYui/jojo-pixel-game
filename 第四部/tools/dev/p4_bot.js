// 第四部序章自动试玩机器人（由 p4_play.js 注入页面）。
//   每一步逻辑开头（G.input.beginStep 之前）看一眼局面，往输入队列里塞按键：走的是和键盘、触屏同一条路
//   （G.input.press / release / inject），不直接改游戏状态，所以它能打通 = 玩家照着提示也能打通。
//   window.__botCfg：read 读对话的速度倍数（录视频用 1，测试用 0.2）；failChase 段 2 故意失败几次（测“放水再来”）；
//   assist 失败菜单里有「放水再来」就选它；chapter 只跑一章时由 p4_play.js 直接进章，标题菜单不选。
//   各章的任务单和打法写在 p4_bot_<章>.js（p4_play.js 自动注入）：往 window.__bot.plan 加地图任务单，往 window.__bot.fights
//   挂 战斗 id → function (ctx, api)，api 是下面这些小工具（hold / tap / pulse / after / go / face / enemy / toHit / attackRhythm …）。
//   各章不用改这个文件（第四部/docs/分章开发约定.md）。
'use strict';
(() => {
  if (window.__bot) return;
  const G = window.G, I = G.input;
  const cfg = Object.assign({ read: 1, failChase: 0, assist: true }, window.__botCfg || {});
  const B = (window.__bot = { cfg, notes: [], held: new Set(), err: null, finished: false, started: false, task: null, fight: {}, fights: {} });
  const held = B.held;
  const F = () => G.flags || {};
  const W = () => G.world;
  const P = () => G.world.player;
  const now = () => G.clk.ui;
  const note = (k, o) => { B.notes.push(Object.assign({ t: Math.round(now() * 100) / 100, k }, o || {})); if (B.notes.length > 600) B.notes.shift(); };
  B.note = note;

  function hold(keys) {
    for (const a of [...held]) if (keys.indexOf(a) < 0) { I.release(a, 'bot'); held.delete(a); }
    for (const a of keys) if (!held.has(a)) { I.press(a, 'bot'); held.add(a); }
  }
  const tap = (a) => I.inject(a);
  // 按一下再松开（格挡要真的按下去：精准格挡看的是按下的时刻，普通格挡看按着没有）
  const pulses = [];
  function pulse(a, frames = 6) { I.press(a, 'botp'); pulses.push({ a, n: frames }); }
  function tickPulses() {
    for (let i = pulses.length - 1; i >= 0; i--) if (--pulses[i].n <= 0) { I.release(pulses[i].a, 'botp'); pulses.splice(i, 1); }
  }
  // 简单的计时器：same key 的等待到点了才做
  const timers = {};
  function after(key, sec, fn) {
    const t = timers[key];
    if (!t) { timers[key] = { at: now() + sec }; return; }
    if (now() >= t.at) { delete timers[key]; fn(); }
  }
  const clearTimer = (key) => { delete timers[key]; };

  function go(x, y, tol = 4) {
    const p = P(), st = W().stage;
    if (!p || !st) return false;
    const yy = G.clamp(y, st.yMin != null ? st.yMin : y, st.yMax != null ? st.yMax : y);
    const keys = [];
    if (Math.abs(x - p.x) > tol) keys.push(x > p.x ? 'right' : 'left');
    if (Math.abs(yy - p.y) > 2) keys.push(yy > p.y ? 'down' : 'up');
    hold(keys);
    return !keys.length;
  }
  function face(dir) {
    const p = P();
    if (!p || p.facing === dir) return true;
    hold([dir > 0 ? 'right' : 'left']);
    return false;
  }

  // ------------------------------------------------------------------ 界面：菜单、QTE、提示框、对话、旁白
  function menu(m) {
    hold([]);
    const opts = m.options.map(String);
    const pick = (label) => opts.findIndex((o) => o.indexOf(label) >= 0);
    let want = -1;
    // 标题菜单没有标题：openMenu 把空串存成 null，所以这里不能写 === ''（之前一直没等就进了序章，录像开头看不到标题）
    if (!m.title && pick('从序章开始') >= 0) {
      if (B.finished) return;                       // 打完了：停在标题
      if (cfg.chapter) return;                      // 只跑一章：p4_play.js 直接 G.playFrom 进章
      if (B.titleSeen == null) B.titleSeen = now();
      if (now() - B.titleSeen < (cfg.titleWait || 0)) return;   // 录视频：先让标题画面停几秒
      want = pick('从序章开始');
    } else if (/完$/.test(m.title || '')) {
      if (!B.finished) note('chapter_end', { title: m.title });
      B.finished = true;
      // 下一章做好以后第一项是「继续下一章」：测一章就停在这一章，选「选择章节」同样回到标题
      want = pick('返回标题');
      if (want < 0) want = pick('选择章节');
    } else if (pick('再来一次') >= 0) {
      const a = pick('放水再来');
      want = cfg.assist && a >= 0 ? a : pick('再来一次');
    } else want = m.escIndex != null ? m.escIndex : 0;
    if (want < 0) want = 0;
    if (m.idx !== want) { after('menuMove', 0.12, () => tap(m.idx < want ? 'down' : 'up')); return; }
    after('menuOk', 0.35, () => { tap('ok'); if (want === pick('从序章开始')) B.started = true; note('menu', { title: m.title, pick: opts[want] }); });
  }
  function qte(q) {
    hold([]);
    if (q.result != null) return;
    if (q.type === 'press') {
      if (q.t >= q.nowT - 0.02 && !q.botDone) { q.botDone = true; tap(q.key || 'attack'); }
    } else if (q.type === 'mash' || q.type === 'clash') {
      if (B.frame % 4 === 0) tap('attack');
    } else if (q.type === 'timing') {
      if (q.m >= q.zone[0] + 0.02 && q.m <= q.zone[1] - 0.02) tap('attack');
    } else if (B.frame % 5 === 0) tap('attack');
  }
  function dialog(d) {
    hold([]);
    const total = d.pageLen[d.page];
    if (d.shown < total) return;
    const key = 'dlg';
    if (B.dlgObj !== d || B.dlgPage !== d.page) { B.dlgObj = d; B.dlgPage = d.page; clearTimer(key); }
    if (I.okLocked()) return;
    after(key, cfg.read * (0.45 + total * 0.045), () => tap('ok'));
  }
  function narr(n) {
    hold([]);
    if (n.auto) return;
    if (n.shown < n.total) return;
    if (B.narrObj !== n) { B.narrObj = n; clearTimer('narr'); }
    if (I.okLocked()) return;
    after('narr', cfg.read * (0.6 + n.total * 0.05), () => tap('ok'));
  }
  function uiStep() {
    const U = G.ui;
    if (U.menu) { menu(U.menu); return true; }
    if (U.qte && !U.qte.hold) { qte(U.qte); return true; }
    if (U.noticeBox) { hold([]); if (!I.okLocked()) after('notice', Math.max(0.8, 1.6 * cfg.read), () => tap('ok')); return true; }
    if (U.choiceBox) { hold([]); after('choice', 0.6, () => tap('ok')); return true; }
    if (U.dlg) { dialog(U.dlg); return true; }
    if (U.narr) { narr(U.narr); return true; }
    return false;
  }

  // ------------------------------------------------------------------ 自由走动：每张地图一张任务单
  const PLAN = {
    road_pro: [
      { id: 'pot_look', go: [332, 156], act: 'ok', done: () => F().potHinted || F().potFixed },
      { id: 'pot_fix', go: [332, 156], act: 'special', done: () => F().potFixed },
      { id: 'vending', go: [531, 155], act: 'ok', done: () => F().coin },
      { id: 'fans', go: [572, 154], act: 'ok', done: () => F().fans },
      { id: 'gate', go: [956, 158], done: () => F().toGate },
    ],
    market_pro: [
      { id: 'soy', go: [130, 156], act: 'ok' },
      { id: 'snack', go: [288, 156], act: 'ok' },
      { id: 'soap', go: [394, 156], act: 'ok' },
      { id: 'tofu', go: [474, 156], act: 'ok' },
      { id: 'wait', go: [500, 158] },
    ],
    house_pro: [
      { id: 'swap', act: 'swap', done: () => P() && P().cid === 'jotaro4' },
      { id: 'puddle', go: [250, 166], act: 'special', done: () => F().puddle },
    ],
  };
  B.plan = PLAN;             // 各章的 p4_bot_<章>.js 往这里加自己地图的任务单
  const progress = {};       // 地图 → 第几个任务
  function roam(dt) {
    const st = W().stage, p = P();
    if (!st || !p) { hold([]); return; }
    const list = PLAN[st.id];
    if (!list) { hold([]); return; }
    let i = progress[st.id] || 0;
    while (i < list.length && list[i].done && list[i].done()) i++;
    progress[st.id] = i;
    const t = list[i];
    if (!t) { hold([]); return; }
    if (B.task !== t) { B.task = t; t.tries = t.tries || 0; t.t0 = now(); t.acted = false; note('task', { stage: st.id, id: t.id }); }
    // 卡住保护：一个任务 25 s 还没完成就跳过（记下来，测试报告里会看到）
    if (now() - t.t0 > 25) { note('task_skip', { stage: st.id, id: t.id, x: Math.round(p.x), y: Math.round(p.y) }); progress[st.id] = i + 1; B.task = null; hold([]); return; }
    if (t.acted) {
      // 动作已经做了：等它引出的剧情演完，再看完成条件
      hold([]);
      after('acted', 0.5, () => {
        if (!t.done || t.done()) { progress[st.id] = i + 1; B.task = null; note('task_done', { id: t.id }); }
        else if (++t.tries < 4) t.acted = false;
        else { progress[st.id] = i + 1; B.task = null; note('task_fail', { id: t.id }); }
      });
      return;
    }
    if (t.go && !go(t.go[0], t.go[1])) return;
    hold([]);
    if (!t.act) { if (!t.done) { /* 只是走到这里等剧情 */ } return; }
    after('act', 0.25, () => { tap(t.act); t.acted = true; });
  }

  // ------------------------------------------------------------------ 战斗
  const enemy = (id) => (G.S && G.S.actor ? G.S.actor(id) : null);
  // 离对手这一拳打到还有多少秒（预警剩余 + 出招后到判定开始）；没在出招 → Infinity
  function toHit(e) {
    if (!e) return Infinity;
    if (e.tele) return Math.max(0, e.tele.dur - e.tele.t) + Math.max(0, (e.atk ? 0 : 0));
    if (e.atk && e.atkT != null) { const a = e.atk.active; return e.atkT < a[0] ? a[0] - e.atkT : (e.atkT <= a[1] ? 0 : Infinity); }
    return Infinity;
  }
  // 按节奏出拳：fb.taps 记这一轮按了几下（前三下是 J1→J2→J3，之后连按就是连打）
  function attackRhythm(gap = 0.22) {
    const fb = B.fight;
    if (now() - (fb.lastJ || -9) >= gap) { fb.lastJ = now(); fb.taps = (fb.taps || 0) + 1; tap('attack'); }
  }
  // 序1：照教学六步做
  function fightJotaro(ctx) {
    const d = ctx.data, p = P(), jt = enemy('jotaro4'), fb = B.fight;
    if (!p || !jt) return hold([]);
    const step = d.step || 1, dx = jt.x - p.x;
    if (fb.step !== step) { fb.step = step; fb.taps = 0; fb.lastJ = -9; fb.guardT = 0; note('t1_step', { step }); }
    if (d.ok === step) { hold([]); return; }          // 这一步过了，等台词
    if (step === 1 || step === 2) {
      // 贴近到 24 px 左右，对着他出拳（出拳会往前冲一点：8–40 px 之间都不用重新走位，免得打断连段）
      const adx = Math.abs(dx);
      if (!p.atk && !p.rush && (adx > 40 || adx < 8 || Math.abs(p.y - jt.y) > 5)) { go(jt.x - Math.sign(dx || 1) * 24, jt.y, 4); return; }
      if (!p.atk && !p.rush && !face(Math.sign(dx || 1))) return;
      hold([]);
      if (step === 1) { attackRhythm(0.24); return; }
      // 第②步：J1→J3，再连按 14 下进入连打，然后松手 1.2 s 让终结那一拳打出来（一直按着就一直是连打）
      const n = fb.taps || 0;
      if (n < 3) attackRhythm(0.22);
      else if (n < 17) attackRhythm(0.07);
      else if (now() - fb.lastJ > 1.2) fb.taps = 0;
      return;
    }
    if (step === 6) {
      hold([]);
      if (ctx.storyU || (p.energy >= (p.energyMax || 100))) after('u6', 0.6, () => tap('special'));
      return;
    }
    const th = toHit(jt);
    if (step === 3) {
      hold([]);
      if (jt.tele && th <= 0.14 && !fb.dodged) { fb.dodged = jt.tele; tap('dodge'); }
      if (!jt.tele) fb.dodged = null;
      return;
    }
    if (step === 4) {
      if (jt.tele || jt.atk) { hold(['guard']); fb.guardT = now(); }
      else if (now() - fb.guardT > 0.4) hold([]);
      return;
    }
    if (step === 5) {
      hold([]);
      if (jt.tele && th <= 0.07 && fb.parried !== jt.tele) { fb.parried = jt.tele; pulse('guard', 8); }
    }
  }
  // 序2 段 1：打碎加湿器 → 打墙放汽 → 拿手套 → 打到 30% 以下 → 修墙 → 张嘴（连打）引它钻进来
  function fightAqua(ctx) {
    const d = ctx.data, p = P(), aq = enemy('aqua'), fb = B.fight;
    if (!p) return hold([]);
    if (p.cid !== 'josuke') { hold([]); after('swapBack', 0.4, () => tap('swap')); return; }
    const low = aq && aq.hp <= aq.maxHp * 0.3;
    // 它在扑过来：先闪（不管在做哪个任务）
    if (aq && aq.tele && !d.inMouth && toHit(aq) <= 0.16 && fb.dodged !== aq.tele && Math.hypot(aq.x - p.x, aq.y - p.y) < 170) {
      fb.dodged = aq.tele; hold([]); tap('dodge'); return;
    }
    let phase = fb.phase || 'hum';
    if (phase === 'hum' && d.humBroken) phase = 'wall';
    if (phase === 'wall' && d.wallOpen) phase = 'glove';
    if (phase === 'glove' && d.glove) phase = 'fight';
    if (phase === 'fight' && low) phase = d.wallOpen ? 'fix' : 'bait';
    if (phase === 'fix' && !d.wallOpen) phase = 'bait';
    if (fb.phase !== phase) { fb.phase = phase; fb.t0 = now(); fb.lastJ = -9; note('aq_phase', { phase }); }
    // 每个阶段最多 25 s：卡住就往下走（记录）
    if (['hum', 'wall', 'glove'].indexOf(phase) >= 0 && now() - fb.t0 > 25) {
      note('aq_phase_skip', { phase }); fb.phase = { hum: 'wall', wall: 'glove', glove: 'fight' }[phase]; fb.t0 = now(); return;
    }
    if (phase === 'hum') {
      if (!go(50, 150, 3)) return;
      if (!face(-1)) return;
      hold([]); attackRhythm(0.24); return;
    }
    if (phase === 'wall') {
      if (!go(150, 148, 3)) return;
      hold([]); attackRhythm(0.24); return;
    }
    if (phase === 'glove') {
      if (!go(380, 150, 3)) return;
      hold([]); after('glove', 0.3, () => tap('ok')); return;
    }
    if (phase === 'fix') {
      if (!go(152, 150, 3)) { return; }
      hold(['guard']);
      after('fixJ', 0.3, () => tap('attack'));
      return;
    }
    if (!aq || aq.hidden || aq.visible === false || (aq.mem && aq.mem.scatter > 0)) { hold([]); return; }
    if (phase === 'fight') {
      // 贴到它侧面 22 px，对齐 y，三连
      const side = p.x < aq.x ? -1 : 1;
      const tx = G.clamp(aq.x + side * 22, 24, 456);
      if (Math.abs(p.x - tx) > 8 || Math.abs(p.y - aq.y) > 4) { go(tx, aq.y, 6); return; }
      if (!face(-side)) return;
      hold([]); attackRhythm(0.24); return;
    }
    // bait：背对它出 J1→J3（J3 打中会把它打散），接着连按进入连打：连打时嘴是张着的，它会自己凑到面前钻进来
    const dist = Math.hypot(aq.x - p.x, (aq.y - p.y) * 1.6);
    const rushing = !!p.rush || p.state === 'rush' || p.state === 'rushEnd';
    if (!fb.baiting) {
      const away = aq.x > p.x ? -1 : 1;
      // 离墙远一点再引（在墙边出 J3 会把刚修好的墙又打开）
      if (p.x < 230) { go(260, 160, 6); return; }
      if (dist < 40) { go(G.clamp(p.x + away * 40, 240, 450), p.y, 4); return; }
      if (dist > 110) { go(aq.x + (p.x < aq.x ? -70 : 70), aq.y, 8); return; }
      if (!face(away)) return;
      hold([]);
      fb.baiting = true; fb.baitT = now(); fb.taps = 0; fb.lastJ = -9; note('aq_bait');
    }
    hold([]);
    attackRhythm((fb.taps || 0) < 3 ? 0.2 : 0.07);
    // 一轮没引进来（连打停了 / 8 s 了）：重新摆位置再来
    if ((!rushing && !p.atk && (fb.taps || 0) > 6) || now() - fb.baitT > 8) { fb.baiting = false; }
  }
  // 序2 段 2：往右追；挡路的东西 J 打开；追上了连按 J（QTE 那边处理）
  function fightChase(ctx) {
    const d = ctx.data, p = P(), an = enemy('angelo'), fb = B.fight;
    if (!p || !an) return hold([]);
    if (ctx.attempt < cfg.failChase) { hold([]); return; }      // 故意站着不动，等时间到
    let ob = null;
    for (const o of d.obs || []) {
      if (o.done || !o.down) continue;
      const ddx = o.x - p.x;
      if (ddx > -6 && ddx < 44 && Math.abs(o.y - p.y) <= 12) { ob = o; break; }
    }
    if (ob) { if (!face(1)) return; hold([]); attackRhythm(0.2); return; }
    const ty = an.y;
    const keys = ['right'];
    if (Math.abs(ty - p.y) > 2) keys.push(ty > p.y ? 'down' : 'up');
    if (an.x - p.x < 16) keys.shift();
    hold(keys);
  }
  function fightStep(dt) {
    const ctx = W().fight;
    if (!ctx || !ctx.spec) { hold([]); return; }
    if (B.fight.id !== ctx.spec.id || B.fight.attempt !== ctx.attempt) {
      B.fight = { id: ctx.spec.id, attempt: ctx.attempt, t0: now() };
      note('fight', { id: ctx.spec.id, attempt: ctx.attempt });
    }
    if (W().cine) { hold([]); return; }
    const id = ctx.spec.id;
    if (id === 'b_pro1_jotaro') fightJotaro(ctx);
    else if (id === 'b_pro2_aqua') fightAqua(ctx);
    else if (id === 'b_pro2_chase') fightChase(ctx);
    else if (B.fights[id]) B.fights[id](ctx, B.api);
    else hold([]);
  }
  // 给各章打法用的小工具（p4_bot_<章>.js 里的 function (ctx, api)）
  B.api = { G, I, B, W, P, F, now, note, hold, tap, pulse, after, clearTimer, go, face, enemy, toHit, attackRhythm };

  B.frame = 0;
  function step(dt) {
    B.frame++;
    tickPulses();
    if (B.manual) { hold([]); return; }            // 测试脚本自己按键时把机器人关掉（p4_rush_loop.js）
    if (G.scene && G.scene.name === 'title' && !G.ui.menu) { hold([]); return; }
    if (uiStep()) return;
    const w = W();
    if (w.combat && w.fight) { fightStep(dt); return; }
    if (w.free && !(G.S && G.S.busy)) { roam(dt); return; }
    hold([]);
  }
  const orig = I.beginStep;
  I.beginStep = function () {
    try { step(1 / 60); } catch (e) { if (!B.err) B.err = String((e && e.stack) || e); }
    return orig.apply(this, arguments);
  };
  note('bot_on', { cfg });
})();
