// 第9章的试玩机器人：自由走动的任务单 + 骰子、第 14 战三段的打法（p4_play.js 自动注入；规矩见 第四部/docs/分章开发约定.md）。
//   全部走和键盘同一条输入路径（api.tap / hold），所以它能打通 = 玩家照提示能打通。
'use strict';
(() => {
  const B = window.__bot, G = window.G;
  if (!B) return;
  const F = () => G.flags || {};
  Object.assign(B.plan, {
    road_ch9: [
      { id: 'sky', go: [300, 156], act: 'ok', done: () => F().sky },
      { id: 'vending', go: [531, 156], act: 'ok', done: () => F().vend },
      { id: 'rohan', go: [956, 158], done: () => F().toRohan },
    ],
    corridor_ch9: [
      { id: 'd302', go: [147, 154], act: 'ok', done: () => F().seen_door_302 },
      { id: 'nurse', go: [585, 154], act: 'ok', done: () => F().nurse },
      { id: 'd304', go: [417, 154], act: 'ok', done: () => F().door304 },
    ],
    attic_ch9: [
      { id: 'bulb', go: [200, 158], act: 'ok', done: () => F().lamp },
      { id: 'cat', go: [150, 160], act: 'ok', done: () => F().catSeen },
      { id: 'wait', go: [80, 160], done: () => F().hideNow },
      { id: 'hide', go: [40, 156], act: 'ok', done: () => F().hidden },
    ],
  });

  // 骰子：选“刚好赢”的那一面（怀疑涨得最少）；赢不了就选怀疑最低的
  B.fights.b_ch9_dice = (ctx, api) => {
    const d = ctx.data, fb = B.fight;
    api.hold([]);
    if (d.phase !== 'pick' || d.t < 0.8) { fb.want = null; return; }
    if (fb.want == null || fb.round !== d.round) {
      fb.round = d.round;
      const his = G.P4CH9.hand(d.rohan).v;
      let best = null;
      for (let face = 1; face <= 6; face++) {
        const v = G.P4CH9.hand([d.mine[0], d.mine[1], face]).v, s = G.P4CH9.suspicion(d, face);
        const score = v > his ? s : 1000 + s;
        if (!best || score < best.score) best = { face, score };
      }
      fb.want = best.face;
      api.note('dice_pick', { round: d.round, rohan: d.rohan, mine: d.mine, face: fb.want });
    }
    if (d.face !== fb.want) {
      const right = (fb.want - d.face + 6) % 6 <= 3;
      api.after('diceMove', 0.14, () => api.tap(right ? 'right' : 'left'));
      return;
    }
    api.after('diceOk', 0.3, () => api.tap('attack'));
  };

  // 段 1 隧道：先去房间门口按 E（拖露伴是连打 QTE，界面那边处理），然后往右跑；公路之星贴近就回身打散，扑过来就闪
  B.fights.b14a_tunnel = (ctx, api) => {
    const d = ctx.data, p = api.P(), hs = api.enemy('highway');
    if (!p) return api.hold([]);
    if (hs && hs.tele && api.toHit(hs) <= 0.15 && B.fight.dodged !== hs.tele) { B.fight.dodged = hs.tele; api.hold([]); api.tap('dodge'); return; }
    const near = hs && hs.visible !== false && !(hs.mem && hs.mem.scatter > 0) && Math.abs(hs.x - p.x) < 34 && Math.abs(hs.y - p.y) < 8;
    if (near) {
      if (!api.face(hs.x > p.x ? 1 : -1)) return;
      api.hold([]); api.attackRhythm(0.22); return;
    }
    if (!d.rohan) {
      if (d.pulling) return api.hold([]);
      if (!api.go(494, 152, 6)) return;
      api.hold([]); api.after('room', 0.3, () => api.tap('ok')); return;
    }
    api.go(940, 158, 4);
  };

  // 段 2 追车：同车道前面 110 px 内有车就换到空的车道
  B.fights.b14b_road = (ctx, api) => {
    const d = ctx.data, p = api.P();
    api.hold([]);
    if (!p || !d.obs) return;
    const LANES = [144, 158, 172];
    const danger = (lane) => d.obs.some((o) => !o.hit && o.lane === lane && o.x - p.x > -10 && o.x - p.x < 120);
    if (!danger(d.lane)) return;
    const opts = [d.lane - 1, d.lane + 1].filter((l) => l >= 0 && l <= 2 && !danger(l));
    if (!opts.length) return;
    void LANES;
    api.after('lane', 0.05, () => api.tap(opts[0] < d.lane ? 'up' : 'down'));
  };

  // 段 3 病房：贴近三连；看见预警快到了就闪
  B.fights.b14c_ward = (ctx, api) => {
    const p = api.P(), hs = api.enemy('highway'), fb = B.fight;
    if (!p || !hs) return api.hold([]);
    if (hs.tele && api.toHit(hs) <= 0.15 && fb.dodged !== hs.tele) { fb.dodged = hs.tele; api.hold([]); api.tap('dodge'); return; }
    const dx = hs.x - p.x;
    if (!p.atk && !p.rush && (Math.abs(dx) > 36 || Math.abs(dx) < 10 || Math.abs(p.y - hs.y) > 4)) { api.go(hs.x - Math.sign(dx || 1) * 24, hs.y, 4); return; }
    if (!p.atk && !p.rush && !api.face(Math.sign(dx || 1))) return;
    api.hold([]); api.attackRhythm(0.24);
  };
})();
