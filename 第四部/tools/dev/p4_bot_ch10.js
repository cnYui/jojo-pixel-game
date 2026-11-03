// 第10章自动试玩：塔脚和夜路的任务单、第 15 战 Superfly、第 16 战 谜（前半 / 后半）的打法。
//   由 p4_play.js 在 p4_bot.js 之后注入；只用 window.__bot.api 里的按键工具（和玩家同一条输入路），不直接改游戏状态。
'use strict';
(() => {
  const B = window.__bot;
  if (!B || B.ch10) return;
  B.ch10 = true;
  const A = B.api, G = A.G, F = A.F, P = A.P;
  const isCid = (p, base) => p && (p.cid === base || p.cid === base + '_tmp');

  B.plan.tower_ch10 = [
    { id: 'sign', go: [48, 152], act: 'ok', done: () => F().sign },
    { id: 'swap_mk', act: 'swap', done: () => isCid(P(), 'mikitaka') },
    { id: 'horn', act: 'special', done: () => F().horn },
    { id: 'swap_js', act: 'swap', done: () => P() && P().cid === 'josuke' },
    { id: 'leg', go: [72, 154], act: 'ok', done: () => F().climb },
  ];
  B.plan.road_ch10 = [
    { id: 'bag', go: [200, 164], act: 'ok', done: () => F().bag },
    { id: 'swap_yu', act: 'swap', done: () => isCid(P(), 'yuya') },
    { id: 'scent0', go: [300, 162], act: 'special', done: () => F().scent0 },
    { id: 'scent1', go: [560, 156], act: 'special', done: () => F().scent1 },
    { id: 'scent2', go: [820, 160], act: 'special', done: () => F().scent2 },
    { id: 'house', go: [960, 158], done: () => F().toMiyamoto },
  ];

  // 靠近对手侧面出拳（三连 → 停一下再来）
  function brawl(e, gap = 24) {
    const p = P(), fb = B.fight;
    const side = p.x < e.x ? -1 : 1;
    const st = A.W().stage;
    const tx = G.clamp(e.x + side * gap, st.x0 + 6, st.x1 - 6);
    const adx = Math.abs(e.x - p.x);
    if (!p.atk && !p.rush && (adx > gap + 16 || adx < 3 || Math.abs(p.y - e.y) > 4)) { A.go(tx, e.y, 5); return; }
    if (!p.atk && !p.rush && !A.face(e.x > p.x ? 1 : -1)) return;
    A.hold([]);
    if ((fb.taps || 0) >= 3 && A.now() - fb.lastJ < 0.7) return;
    if ((fb.taps || 0) >= 3) fb.taps = 0;
    A.attackRhythm(0.22);
  }
  // 对手在出招、离得近：闪一下
  function dodgeIf(e, range = 120) {
    const p = P(), fb = B.fight;
    if (!e || !e.tele || fb.dodged === e.tele) return false;
    if (A.toHit(e) > 0.16 || Math.hypot(e.x - p.x, e.y - p.y) > range) return false;
    fb.dodged = e.tele; A.hold([]); A.tap('dodge'); return true;
  }

  // ---- 第 15 战：打碎铆钉 → 等他钻进铁架 → 按住 L 按 J 修回去；段 B 未起隆跑到横担右头按 U
  B.fights.b15_superfly = (ctx) => {
    const d = ctx.data, p = P(), ty = A.enemy('toyohiro'), fb = B.fight;
    if (!p || !ty) return A.hold([]);
    if (d.phase === 'B') {
      if (d.swing) return A.hold([]);
      if (!A.go(240, p.y, 3)) return;
      A.hold([]); A.after('cable', 0.3, () => A.tap('special'));
      return;
    }
    if (p.cid !== 'josuke') { A.hold([]); A.after('swapJ', 0.4, () => A.tap('swap')); return; }
    if (dodgeIf(ty)) return;
    const broken = (d.rivets || []).filter((r) => r.broken);
    if (ty.mem.merged) {
      if (broken.length) {
        A.hold(['guard']);
        A.after('fixJ', 0.35, () => A.tap('attack'));
        return;
      }
      // 打碎最近的一颗：站在它左边 22 px，J1→J3
      const r = (d.rivets || []).slice().sort((a, b) => Math.abs(a.x - p.x) - Math.abs(b.x - p.x))[0];
      if (!r) return A.hold([]);
      if (!p.atk && (Math.abs(p.x - (r.x - 22)) > 6 || Math.abs(p.y - r.y) > 3)) { A.go(r.x - 22, r.y, 3); fb.taps = 0; return; }
      if (!p.atk && !A.face(1)) return;
      A.hold([]);
      A.attackRhythm(0.22);
      if ((fb.taps || 0) > 4 && !p.atk) fb.taps = 0;
      return;
    }
    brawl(ty, 24);
  };

  // ---- 第 16 战前半：他闭眼的时候冲上去打；平时离远点、躲纸；紧张槽高了换裕也（裕也的 U 吸养分降紧张）
  B.fights.b16_enigma = (ctx) => {
    const d = ctx.data, p = P(), te = A.enemy('terunosuke'), fb = B.fight;
    if (!p || !te) return A.hold([]);
    const tension = ctx.gauge ? ctx.gauge.value : 0;
    const yuLead = isCid(p, 'yuya');
    if (!yuLead && tension > 55) { A.hold([]); A.after('swapY', 0.3, () => A.tap('swap')); return; }
    if (yuLead && p.energy >= 100) { A.hold([]); A.after('heal', 0.3, () => A.tap('special')); return; }
    if (yuLead && tension < 20) { A.hold([]); A.after('swapJ', 0.3, () => A.tap('swap')); return; }
    if (dodgeIf(te, 200)) return;
    const sniff = d.sniffT && G.clk.world - d.sniffT < 1.2;
    if (te.mem.fear || sniff) { brawl(te, 22); return; }
    fb.taps = 0;
    // 平时：站在他前面 110 px，上下错开一点躲直线的纸
    const side = p.x < te.x ? -1 : 1;
    const st = A.W().stage;
    let tx = te.x + side * 110;
    if (tx < st.x0 + 10 || tx > st.x1 - 10) tx = te.x - side * 110;
    A.go(G.clamp(tx, st.x0 + 10, st.x1 - 10), te.y + (Math.floor(A.now() / 2) % 2 ? 8 : -8), 8);
  };

  // ---- 第 16 战后半：裕也先揣两张纸，等紧张槽满；仗助出来后打到底，最后按住 L 按 J
  B.fights.b16_enigma_b = (ctx) => {
    const d = ctx.data, p = P(), te = A.enemy('terunosuke');
    if (!p || !te) return A.hold([]);
    if (d.part === 2) {
      const pp = (d.papers || []).filter((q) => !q.held).sort((a, b) => Math.abs(a.x - p.x) - Math.abs(b.x - p.x))[0];
      if (pp) {
        if (!A.go(pp.x, pp.y, 6)) return;
        A.hold([]); A.after('grab', 0.15, () => A.tap('ok'));
        return;
      }
      if (dodgeIf(te, 200)) return;
      // 纸揣好了：离他远点等（紧张槽会自己满）
      A.go(G.clamp(te.x < 200 ? 330 : 70, 30, 360), 156, 8);
      return;
    }
    if (d.part !== 3) return A.hold([]);
    if (d.needFix) { A.hold(['guard']); A.after('fixBook', 0.35, () => A.tap('attack')); return; }
    if (d.finishing) return A.hold([]);
    if (dodgeIf(te, 160)) return;
    brawl(te, 22);
  };
})();
