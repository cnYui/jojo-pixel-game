// 第6章机器人：自由走动的任务单 + 各段打法（p4_play.js 自动注入；工具函数见 p4_bot.js 的 B.api）
'use strict';
(() => {
  const B = window.__bot;
  if (!B) return;
  const G = window.G;
  const F = () => G.flags || {};
  const P = () => G.world.player;

  Object.assign(B.plan, {
    alley_ch6: [
      // 第一次自由走动：露伴先读（读不了），再和铃美说话
      { id: 'read_ghost', go: [282, 154], act: 'special', done: () => F().ch6ReadGhost },
      { id: 'talk_reimi', go: [282, 154], act: 'ok', done: () => F().ch6TalkReimi },
      // 「不能回头」：先往前走一段，故意回一次头（被拖回去），再一路走出去
      { id: 'walk_on', go: [470, 154], done: () => F().ch6Dragged || (P() && P().x >= 465) },
      { id: 'look_back', go: [440, 154], done: () => F().ch6Dragged },
      { id: 'exit', go: [614, 154], done: () => F().ch6AlleyOut },
    ],
    road_ch6: [
      { id: 'vending', go: [526, 156], act: 'ok', done: () => F().ch6Vending },
    ],
    bank_ch6: [
      { id: 'ticket_look', go: [236, 152], act: 'ok', done: () => F().ch6TicketHint || F().ch6Fixed },
      { id: 'ticket_fix', go: [236, 152], act: 'special', done: () => F().ch6Fixed },
    ],
  });

  // 捡硬币：挑“约 ¥”最高的安全街区（派出所 / 河边 / 工地只在别处都捡薄了才去），光标挪过去，有空队就派
  B.fights.mg_coins = (ctx, api) => {
    const d = ctx.data;
    api.hold([]);
    if (!d.blocks) return;
    const est = (b) => b.base * Math.pow(0.8, b.visits) * (b.danger ? 0.6 : 1);
    let best = d.blocks[0];
    for (const b of d.blocks) if (est(b) > est(best)) best = b;
    if (d.cur !== best.i) {
      const c0 = d.cur % 3, r0 = Math.floor(d.cur / 3), c1 = best.i % 3, r1 = Math.floor(best.i / 3);
      api.after('cur', 0.1, () => api.tap(c1 > c0 ? 'right' : c1 < c0 ? 'left' : r1 > r0 ? 'down' : 'up'));
      return;
    }
    if (d.squads.some((q) => q.st === 'home')) api.after('send', 0.2, () => api.tap('attack'));
  };

  // 外墙：两人轮流往上。队长和队友同层 → 走到 20 px 内按 J 抛；队友在上一层 → Q 换过去；队友在下一层 → 站到他头顶按住 L 按 J
  B.fights.b09a_wall = (ctx, api) => {
    const p = P(), ms = (G.party && G.party.members) || [];
    const pt = ms.find((a) => a !== p);
    if (!p || !pt || p.lvl == null || pt.lvl == null) return api.hold([]);
    const fb = api.B.fight;
    // 身前有丰收：先挥两拳
    const bug = G.world.stage.actors.find((a) => a.id && /^hb\d/.test(a.id) && !a.remove && a.lvl === p.lvl && Math.abs(a.x - p.x) < 30);
    if (bug && !fb.pulling) {
      if (!api.face(bug.x > p.x ? 1 : -1)) return;
      api.hold([]); api.attackRhythm(0.24); return;
    }
    if (pt.lvl > p.lvl) { api.hold([]); api.after('swap', 0.4, () => api.tap('swap')); return; }
    if (Math.abs(pt.x - p.x) > 18) { fb.pulling = false; api.go(pt.x + (p.x < pt.x ? -12 : 12), p.y, 3); return; }
    if (pt.lvl === p.lvl) { api.hold([]); api.after('throw', 0.4, () => api.tap('attack')); return; }
    // 队友在下一层：按住 L，再按 J
    fb.pulling = true;
    api.hold(['guard']);
    api.after('pull', 0.35, () => api.tap('attack'));
  };

  // 楼顶：仗助当队长往右走；前面断了就按住 L 按 J 修；队长被换成亿泰就换回来。醉了就站着
  B.fights.b09b_roof = (ctx, api) => {
    const d = ctx.data, p = P();
    if (!p) return api.hold([]);
    if (d.drunk) return api.hold([]);
    if (p.cid !== 'josuke') { api.hold([]); api.after('swapBack', 0.4, () => api.tap('swap')); return; }
    const bug = G.world.stage.actors.find((a) => a.id && /^hb\d/.test(a.id) && !a.remove && Math.abs(a.x - p.x) < 28);
    if (bug) { if (!api.face(bug.x > p.x ? 1 : -1)) return; api.hold([]); api.attackRhythm(0.24); return; }
    const segs = [[454, 472], [472, 490], [490, 508], [508, 526]];
    const i = (d.cut || []).findIndex((v, k) => v && !d.fixed[k]);
    if (i >= 0 && p.x >= segs[i][0] - 12) { api.hold(['guard']); api.after('fix', 0.35, () => api.tap('attack')); return; }
    const ty = p.x > 430 ? 148 : 156;
    api.go(600, ty, 2);
  };

  // 第 10 战：一直往右爬，吉良近了就派丰收
  B.fights.b10_kq = (ctx, api) => {
    const d = ctx.data, p = P(), kr = api.enemy('kira');
    if (!p) return api.hold([]);
    api.hold(['right']);
    if (kr && d.cd <= 0 && Math.abs(kr.x - p.x) < 70) api.after('send', 0.15, () => api.tap('attack'));
  };

  // 纽扣：往左跑；前面 40 px 内有学生的脚和自己在同一条线上，就换一条线（上下）；扫帚快来了就在扫帚区外面等
  B.fights.b10c_button = (ctx, api) => {
    const d = ctx.data, p = P();
    if (!p || !d.walkers) return api.hold([]);
    const lanes = [146, 158, 172];
    const danger = (y) => d.walkers.some((q) => q.a.x < p.x + 6 && q.a.x > p.x - 44 && Math.abs(q.a.y - y) < 9);
    let ty = p.y;
    if (danger(p.y)) { const ok = lanes.filter((y) => !danger(y)); if (ok.length) ty = ok.sort((a, b) => Math.abs(a - p.y) - Math.abs(b - p.y))[0]; }
    const ev = 3.2, on = 1.0, ph = d.broomT % ev;
    const nearBroom = p.x > 340 && p.x < 352;
    if (nearBroom && (ph < on || ph > ev - 1.6)) { api.go(p.x, ty, 2); return; }
    const keys = [];
    keys.push('left');
    if (Math.abs(ty - p.y) > 2) keys.push(ty > p.y ? 'down' : 'up');
    api.hold(keys);
  };
})();
