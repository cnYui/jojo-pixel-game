// 第1章的试玩机器人：两段自由走动的任务单 + 三场战斗的打法（p4_play.js 自动注入，规矩见 第四部/docs/分章开发约定.md）。
//   走的是和键盘同一条输入路径：它能打通 = 玩家照着提示也能打通。
'use strict';
(() => {
  const B = window.__bot;
  if (!B) return;
  const { G, P, F, now, note, hold, tap, after, go, face, enemy, toHit, attackRhythm } = B.api;

  Object.assign(B.plan, {
    // 自由走动 A：前院，走到大门口按 E 进屋
    yard_ch1: [{ id: 'door', go: [421, 152], act: 'ok', done: () => !!F().ch1Door }],
    // 自由走动 C：阁楼，走到木箱前按 U 修碎纸
    attic_ch1: [{ id: 'box', go: [219, 152], act: 'special', done: () => !!F().ch1Photo }],
  });

  const RACK = [264, 146];

  // 不能挡的招来了：按 K
  function dodgeIf(e, fb, win = 0.14) {
    if (e && e.tele && toHit(e) <= win && fb.dodged !== e.tele) { fb.dodged = e.tele; hold([]); tap('dodge'); return true; }
    return false;
  }

  // 第 1 战：站在花盆架右边，让亿泰在右边；他用拉近时不闪，花盆飞起来再闪；其余的招都闪；空了就去修花盆
  B.fights.b01_thehand = (ctx) => {
    const d = ctx.data, p = P(), e = enemy('okuyasu'), fb = B.fight;
    if (!p || !e) return hold([]);
    if (d.pot) {
      if (!d.pot.dodged && p.state !== 'dodge') { hold([]); after('potDodge', 0.15, () => tap('dodge')); }
      else hold([]);
      return;
    }
    if (e.tele) {
      const pull = e.tele.move === 'OK_PULL';
      if (pull && d.aligned) { hold([]); return; }       // 让他拉：花盆会一起飞过来
      if (dodgeIf(e, fb, pull ? 0.1 : 0.14)) return;
      hold([]);
      return;
    }
    const pots = 6 - ((G.world.stage.state || {}).pots_gone || 0);
    if (pots <= 0) {
      if (!go(RACK[0] + 8, RACK[1] + 4, 4)) return;
      hold(['guard']);
      after('fixPot', 0.3, () => tap('attack'));
      return;
    }
    const low = e.hp <= e.maxHp * 0.3;
    if (low || e.state === 'down') {
      // 低血：站到花盆架和亿泰中间等他拉
      if (e.x < RACK[0] + 40) { go(RACK[0] - 30, e.y, 6); return; }
      go(RACK[0] + 26, G.clamp(e.y, RACK[1], RACK[1] + 14), 4);
      return;
    }
    // 打他：贴近 24 px 出三连（站位尽量保持在花盆架右边）
    const dx = e.x - p.x, adx = Math.abs(dx);
    if (!p.atk && !p.rush && (adx > 40 || adx < 10 || Math.abs(p.y - e.y) > 5)) { go(e.x - Math.sign(dx || 1) * 24, e.y, 4); return; }
    if (!p.atk && !p.rush && !face(Math.sign(dx || 1))) return;
    hold([]);
    attackRhythm(0.24);
  };

  // 坏公司的兵：离仗助最近的一个
  function nearest(ctx, filt) {
    const p = P();
    let best = null, bd = 1e9;
    for (const a of ctx.enemies()) {
      if (a.dead || a.hp <= 0 || a.untargetable || (filt && !filt(a))) continue;
      const dd = Math.abs(a.x - p.x) + Math.abs(a.y - p.y) * 2;
      if (dd < bd) { bd = dd; best = a; }
    }
    return best;
  }
  // 走过去的时候绕开地雷
  function goSafe(d, x, y, tol) {
    const p = P();
    for (const mn of d.mines || []) {
      if (mn.gone) continue;
      const ahead = (mn.x - p.x) * Math.sign(x - p.x);
      if (ahead > 0 && ahead < 14 && Math.abs(mn.y - p.y) < 7) { y = mn.y + (p.y >= mn.y ? 10 : -10); break; }
    }
    return go(x, y, tol);
  }
  // 有导弹飞到面前：转过去打
  function swat() {
    const p = P();
    for (const s of G.world.shots) {
      if (s.dead || s.tag !== 'missile' || s.side !== 'enemy') continue;
      const dx = s.x - p.x;
      if (Math.abs(dx) < 46 && Math.abs(s.y - p.y) < 14 && s.z <= 44) {
        if (!p.atk && !face(Math.sign(dx) || 1)) return true;
        hold([]); attackRhythm(0.18); return true;
      }
    }
    return false;
  }
  function brawl(ctx, target) {
    const d = ctx.data, p = P();
    if (!target) { hold([]); return; }
    const dx = target.x - p.x, adx = Math.abs(dx);
    if (!p.atk && !p.rush && (adx > 30 || adx < 6 || Math.abs(p.y - target.y) > 5)) { goSafe(d, target.x - Math.sign(dx || 1) * 18, target.y, 4); return; }
    if (!p.atk && !p.rush && !face(Math.sign(dx || 1))) return;
    hold([]);
    attackRhythm(0.22);
  }

  // 第 2 战 段 1：先打兵（小兵一拳一个），导弹来了打下来
  B.fights.b02_badcompany_a = (ctx) => {
    if (swat()) return;
    brawl(ctx, nearest(ctx));
  };

  // 第 2 战 段 2：前两阶段清兵、躲红圈；第三阶段去修导弹碎片
  B.fights.b02_badcompany_b = (ctx) => {
    const d = ctx.data, p = P();
    if (!p) return hold([]);
    // 红圈：在圈里就往外走
    for (const rm of d.rain || []) {
      if (rm.done) continue;
      if (Math.pow((p.x - rm.x) / 24, 2) + Math.pow((p.y - rm.y) / 12, 2) <= 1) {
        go(rm.x + (p.x >= rm.x ? 34 : -34), p.y, 2);
        return;
      }
    }
    if (swat()) return;
    const db = (d.debris || []).filter((q) => !q.gone && !(d.rain || []).some((r) => !r.done && Math.hypot(r.x - q.x, r.y - q.y) < 24))
      .sort((a, b) => Math.hypot(a.x - p.x, a.y - p.y) - Math.hypot(b.x - p.x, b.y - p.y))[0];
    if ((d.ph || 1) === 3 && db) {
      if (!goSafe(d, db.x - 10, db.y, 3)) return;
      hold(['guard']);
      after('fixDb', 0.3, () => tap('attack'));
      return;
    }
    brawl(ctx, nearest(ctx));
  };
  note('bot_ch1_on');
})();
