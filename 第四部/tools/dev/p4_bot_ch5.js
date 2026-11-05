// 第5章的自动试玩：自由走动的任务单 + 三段战斗的打法（p4_play.js 自动注入；工具见 p4_bot.js 的 B.api）。
'use strict';
(() => {
  const B = window.__bot;
  if (!B) return;
  const { G, F, P, W, now, note, hold, tap, after, go, face, enemy, toHit, attackRhythm } = B.api;

  Object.assign(B.plan, {
    rohan_out_ch5: [
      { id: 'window', go: [317, 152], act: 'ok', done: () => F().window },
    ],
    rohan_in_ch5: [
      { id: 'hole', go: [398, 152], act: 'special', done: () => F().holeFixed },
      { id: 'door', go: [48, 160], done: () => F().leaveStudio },
    ],
    ditch_ch5: [
      { id: 'swap', act: 'swap', done: () => P() && P().cid === 'jotaro4' },
      { id: 'tracks', go: [300, 154], act: 'special', done: () => F().tracks },
      { id: 'right', go: [630, 160], done: () => F().toFarm },
    ],
    farm_out_ch5: [
      { id: 'laundry', go: [252, 154], act: 'ok', done: () => F().laundry },
      { id: 'door', go: [103, 152], act: 'ok', done: () => F().enterHouse },
    ],
  });

  // 第 7 战：画面是黑的，可机器人直接看露伴的位置（玩家看波纹）。预警就闪，平时贴上去三连；暴走时连按 J
  B.fights.b07_heavensdoor = (ctx) => {
    const d = ctx.data, p = P(), rh = enemy('rohan'), fb = B.fight;
    if (!p || !rh) return hold([]);
    if (d.raceOn) { hold([]); attackRhythm(0.15); return; }
    // 飞过来的天堂之门小人：离得近就闪
    for (const s of G.world.shots) {
      if (s.tag !== 'door' || s.dead) continue;
      if (Math.abs(s.x - p.x) < 34 && Math.abs(s.y - p.y) < 12 && fb.dodgedShot !== s) { fb.dodgedShot = s; hold([]); tap('dodge'); return; }
    }
    if (rh.tele && toHit(rh) <= 0.14 && fb.dodged !== rh.tele && Math.abs(rh.x - p.x) < 120) { fb.dodged = rh.tele; hold([]); tap('dodge'); return; }
    const side = p.x < rh.x ? -1 : 1;
    const tx = G.clamp(rh.x + side * 22, 50, 466);
    if (!p.atk && !p.rush && (Math.abs(p.x - tx) > 10 || Math.abs(p.y - rh.y) > 4)) { go(tx, rh.y, 6); return; }
    if (!p.atk && !p.rush && !face(-side)) return;
    hold([]);
    const n = fb.taps || 0;
    attackRhythm(0.24);
    if (n > 3 && now() - (fb.lastJ || 0) > 0.6) fb.taps = 0;
  };

  // 第 8 战段 1：先去灶台拿锅；老鼠瞄准时举锅（按住 L），它跑出来 / 探头时对齐 y 弹钢珠
  B.fights.b08a_ratt = (ctx) => {
    const d = ctx.data, p = P(), rat = enemy('rat_a');
    if (!p) return hold([]);
    if (!d.pan) {
      if (!go(171, 152, 3)) return;
      hold([]); after('pan', 0.3, () => tap('ok')); return;
    }
    if (!rat || rat.hp <= 0) return hold([]);
    const m = rat.mem || {};
    const dir = rat.x > p.x ? 1 : -1;
    if (m.mode === 'aim' && !m.fired) {
      if (p.facing !== dir) { hold([dir > 0 ? 'right' : 'left']); return; }
      hold(['guard']); return;
    }
    if (m.mode === 'hide') {
      // 躲着：站到离它 60–120 px、同一条 y 上等
      const tx = G.clamp(rat.x - dir * 90, 60, 460);
      if (Math.abs(p.x - tx) > 30 || Math.abs(p.y - rat.y) > 3) { go(tx, rat.y, 20); return; }
      hold([]); face(dir); return;
    }
    if (Math.abs(p.y - rat.y) > 4) { go(p.x, rat.y, 999); return; }
    if (!face(dir)) return;
    hold([]); attackRhythm(0.3);
  };

  // 第 8 战段 2：第一发打岩石（那是反射点），露出来以后屏住呼吸打草丛
  B.fights.b08b_hill = (ctx) => {
    const d = ctx.data;
    if (!d.scope || d.firing) return hold([]);
    const tgt = d.ammo >= 2 ? [668, 112] : [778, 85];
    if (d.ammo >= 2 && !d.decoyTold) return hold([]);            // 先等岩石闪一下
    const dx = tgt[0] - d.aimX, dy = tgt[1] - d.aimY, keys = [];
    if (Math.abs(dx) > 1.2) keys.push(dx > 0 ? 'right' : 'left');
    if (Math.abs(dy) > 1.2) keys.push(dy > 0 ? 'down' : 'up');
    if (keys.length) { hold(keys); return; }
    if (d.breathOut) { hold([]); return; }
    hold(['guard']);
    const ex = Math.hypot((d.showX || 0) - tgt[0], (d.showY || 0) - tgt[1]);
    if (ex < 3 && (d.breath || 0) < 0.9) after('fire' + d.ammo, 0.2, () => { tap('attack'); note('hill_fire', { ammo: d.ammo, ex: Math.round(ex * 10) / 10 }); });
  };
})();
