// 第2章自动试玩：学校、商店街、道口的任务单，第 3 战「锁」、第 4 战「表面」段 A / 段 B 的打法，
//   以及两个战斗外的小界面（内疚的回答二选一、段 C 的「抗拒」连按）。p4_play.js 在 p4_bot.js 之后自动注入。
//   和 p4_bot.js 一样只往输入队列里塞按键（tap / hold），不直接改游戏状态：它能打通 = 玩家照着提示也能打通。
'use strict';
(() => {
  const B = window.__bot;
  if (!B || B.ch2) return;
  B.ch2 = true;
  const G = window.G, I = G.input, A = B.api;
  const { hold, tap, after, go, face, enemy, now, note, toHit, attackRhythm } = A;
  const F = () => G.flags || {};
  const P = () => G.world.player;

  // ------------------------------------------------------------------ 自由走动的任务单
  Object.assign(B.plan, {
    // 节拍 7：看告示板 → 换康一 → 对着储物柜 U 听 → E 打开间田的柜子
    school_ch2: [
      { id: 'board', go: [271, 156], act: 'ok', done: () => !!(F().checked && F().checked.board) },
      { id: 'swapK', act: 'swap', done: () => !!P() && P().cid === 'koichi' },
      { id: 'listen', go: [134, 156], act: 'special', done: () => !!F().listened },
      { id: 'locker', go: [147, 156], act: 'ok', done: () => !!F().lockerOpen },
    ],
    // 段 B 前：走到女学生跟前 → 换康一 → 对着理发店 U → 往前走到老酒铺
    arcade_ch2: [
      { id: 'girls', go: [300, 158], done: () => !!F().girlsSeen },
      { id: 'swapK', act: 'swap', done: () => !!P() && P().cid === 'koichi' },
      { id: 'barber', go: [300, 156], act: 'special', done: () => !!F().girlsGone },
      { id: 'liquor', go: [404, 158], done: () => !!F().liquor },
    ],
    // 道口：康一对着右边的警报灯 U
    crossing_ch2: [
      { id: 'lamp', go: [214, 158], act: 'special', done: () => !!F().alarm },
    ],
  });

  // ------------------------------------------------------------------ 战斗外的小界面：内疚的回答、抗拒连按
  function ch2Step() {
    const R = G.P4CH2;
    if (!R) return;
    if (R.pick && R.pick.open) {
      const st = B.ch2pick && B.ch2pick.obj === R.pick ? B.ch2pick : (B.ch2pick = { obj: R.pick, t: now(), done: false });
      if (!st.done && now() - st.t > 0.6) { st.done = true; tap(R.pick.good); note('ch2_pick', { good: R.pick.good }); }
    }
    if (R.resist && R.resist.open && B.frame % 8 === 0) tap('attack');
  }
  const orig = I.beginStep;
  I.beginStep = function () {
    try { ch2Step(); } catch (e) { if (!B.err) B.err = String((e && e.stack) || e); }
    return orig.apply(this, arguments);
  };

  // 它快打到了就闪（同一招只闪一次）
  function dodgeIf(e, fb, range = 130) {
    const p = P(), busy = e && (e.tele || e.atk);
    if (!busy) { fb.dodged = null; return false; }
    if (fb.dodged === busy || toHit(e) > 0.14 || Math.abs(e.x - p.x) > range || Math.abs(e.y - p.y) > 20) return false;
    fb.dodged = busy; hold([]); tap('dodge');
    return true;
  }
  // 贴到对手身边 tx 处、同一行，面朝它出 J（三连后停一下，免得一直按成别的东西）
  function punish(e, fb, dist = 26) {
    const p = P(), dx = e.x - p.x, dir = Math.sign(dx) || 1;
    if (!p.atk && (Math.abs(Math.abs(dx) - dist) > 8 || Math.abs(p.y - e.y) > 3)) { go(e.x - dir * dist, e.y, 4); return; }
    if (!p.atk && !face(dir)) return;
    hold([]);
    if ((fb.taps || 0) < 3) attackRhythm(0.2);
    else if (now() - (fb.lastJ || 0) > 0.7) fb.taps = 0;
  }

  // ------------------------------------------------------------------ 第 3 战：康一 vs 玉美（不打本人，用拟声字把他吵到崩溃）
  //   平时站在他左边（门那一侧）46 px，同一行连续贴字：贴中的击退把他往右推，他往门口跑的时候正好撞上来。
  //   他背过身站着不动时绕到背后 12 px 贴（耳边 +10）
  B.fights.b03_thelock = () => {
    const p = P(), e = enemy('tamami'), fb = B.fight;
    if (!p || !e) return hold([]);
    const m = e.mem || {};
    const back = !m.run && m.pause > 0.35 && m.wave;
    let tx = back ? e.x - (e.facing || 1) * 12 : e.x - 46;
    tx = Math.max(54, Math.min(310, tx));
    if (!p.atk && (Math.abs(p.x - tx) > 7 || Math.abs(p.y - e.y) > 3)) { go(tx, e.y, 5); return; }
    const dir = Math.sign(e.x - p.x) || 1;
    if (!p.atk && !face(dir)) return;
    hold([]);
    // 他捂着耳朵的时候贴了也听不见：等快松手了再贴（字飞过去要 0.3 s 左右）
    if (m.ears > 0.3) return;
    attackRhythm(0.26);
    if (!fb.told) { fb.told = true; note('b03_bot', { plan: 'left-side shots' }); }
  };

  // ------------------------------------------------------------------ 第 4 战段 A：仗助 vs 表面（学校走廊）
  //   平时和它错开一行（y 差 10 左右：视线条涨不起来，它照样会出招）；它出招就闪，出完一套露出破绽（愣住）再贴上去三连。
  //   过半以后换成康一：对准仗助手里的笔贴字
  B.fights.b04a_surface = (ctx) => {
    const d = ctx.data, p = P(), sf = enemy('surface'), fb = B.fight;
    if (!p || !sf) return hold([]);
    if (d.ctrl) return hold([]);
    if (d.penMode) {
      const pen = enemy('ch2_pen'), jo = enemy('josuke');
      if (p.cid !== 'koichi' || !pen || d.penHit) return hold([]);
      const ty = jo ? jo.y : pen.y, dir = Math.sign(pen.x - p.x) || 1;
      if (Math.abs(p.y - ty) > 3) { go(p.x, ty, 6); return; }
      if (Math.abs(pen.x - p.x) < 16) { go(pen.x - dir * 34, ty, 4); return; }
      if (!face(dir)) return;
      hold([]);
      attackRhythm(0.6);
      return;
    }
    if (p.cid !== 'josuke') return hold([]);
    if (dodgeIf(sf, fb)) return;
    // 第一次尝试先故意和它对视一次，让视线条涨满（录像里看得到“被操纵”），最多 12 s
    if (ctx.attempt === 0 && !(d.ctrlN > 0)) {
      if (!fb.demoT) fb.demoT = now();
      if (now() - fb.demoT < 12) {
        const ddx = sf.x - p.x, ddir = Math.sign(ddx) || 1;
        if (!p.atk && (Math.abs(p.y - sf.y) > 2 || Math.abs(Math.abs(ddx) - 50) > 8)) { go(sf.x - ddir * 50, sf.y, 4); return; }
        if (!p.atk && !face(ddir)) return;
        return hold([]);
      }
    }
    const open = (sf.mem && sf.mem.open > 0) || sf.stunT > 0 || sf.state === 'hurt';
    if (open && !fb.pun) { fb.pun = now(); fb.taps = 0; }
    if (fb.pun && now() - fb.pun > 1.3) fb.pun = 0;
    if (fb.pun) { punish(sf, fb); return; }
    if (p.atk) return hold([]);
    // 错开一行等它出招
    const st = G.world.stage, side = p.y >= sf.y ? 1 : -1;
    let ty = sf.y + side * 10;
    if (ty > st.yMax - 1 || ty < st.yMin + 1) ty = sf.y - side * 10;
    const dx = sf.x - p.x, dir = Math.sign(dx) || 1;
    const tx = Math.abs(dx) < 40 || Math.abs(dx) > 70 ? sf.x - dir * 54 : p.x;
    if (Math.abs(p.y - ty) > 2 || Math.abs(p.x - tx) > 6) { go(tx, ty, 5); return; }
    hold([]);
  };

  // ------------------------------------------------------------------ 第 4 战段 B：商店街（J3 打碎啤酒箱 → 按住 L 按 J 修复 → 打到它跑）
  B.fights.b04b_surface = (ctx) => {
    const d = ctx.data, p = P(), sf = enemy('surface'), fb = B.fight;
    if (!p || !sf || !sf.visible) return hold([]);
    if (p.cid !== 'josuke') { hold([]); after('swapJ', 0.4, () => tap('swap')); return; }
    if (!d.shards) {
      if (dodgeIf(sf, fb, 90)) return;
      if (!p.atk && (Math.abs(p.x - 338) > 4 || Math.abs(p.y - 150) > 3)) { go(338, 150, 3); return; }
      if (!p.atk && !face(1)) return;
      hold([]);
      if ((fb.taps || 0) < 3) attackRhythm(0.2);
      else if (now() - (fb.lastJ || 0) > 0.9) fb.taps = 0;
      return;
    }
    if (!d.trap) {
      hold(['guard']);
      after('trapJ', 0.35, () => tap('attack'));
      return;
    }
    if (dodgeIf(sf, fb)) return;
    punish(sf, fb, 24);
  };
  note('bot_ch2_on');
})();
