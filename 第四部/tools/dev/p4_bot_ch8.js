// 第8章的试玩机器人任务单和打法（p4_play.js 自动注入；公共部分在 p4_bot.js，这里只往 __bot.plan / __bot.fights 里加东西）。
//   旧宅：换承太郎看本子 → 奖状 → 相册 → 遗照（触发咔嚓）→ 第 12 战 → 换回仗助修木箱。
//   车站：长椅 → 换乔瑟夫念写 → 另一张长椅找到静 → 跟大柳说话 → 第 13 战（第一局故意输，看完“小动作”的教学再连赢三局）。
'use strict';
(() => {
  const B = window.__bot;
  if (!B) return;
  const G = window.G, F = () => G.flags || {};
  const P = () => G.world.player;
  const has = (cid) => !!(G.D && G.D.chars && G.D.chars[cid]);
  const joseph = () => (has('joseph_old') ? 'joseph_old' : 'ph8_joseph');

  B.plan.kirahouse_ch8 = [
    { id: 'swap_jotaro', act: 'swap', done: () => F().afterFight || (P() && P().cid === 'jotaro4') },
    { id: 'notebook', go: [44, 152], act: 'special', done: () => F().afterFight || F().notebook },
    { id: 'awards', go: [156, 152], act: 'ok' },
    { id: 'album', go: [331, 154], act: 'ok', done: () => F().afterFight || F().album },
    { id: 'portrait', go: [239, 152], act: 'ok', done: () => F().afterFight || F().portrait },
    { id: 'wait_fight', done: () => F().afterFight },
    { id: 'swap_josuke', act: 'swap', done: () => F().houseDone || (P() && P().cid === 'josuke') },
    { id: 'box', go: [580, 154], act: 'special', done: () => F().houseDone },
  ];
  B.plan.station_ch8 = [
    { id: 'bench1', go: [485, 160], act: 'ok', done: () => F().bench1 },
    { id: 'swap_joseph', act: 'swap', done: () => F().nensha || (P() && P().cid === joseph()) },
    { id: 'nensha', go: [485, 160], act: 'special', done: () => F().nensha || F().shizuka },
    { id: 'bench2', go: [615, 160], act: 'ok', done: () => F().shizuka },
    { id: 'oyanagi', go: [358, 160], act: 'ok', done: () => F().toJanken },
  ];

  // 第 12 战：一直用承太郎（拍立得在他手里）。他探身出手时闪开，出手后露在外面那 1.2 s 贴上去打；
  //   打出相框倒地后，站到取景框外（|dx| > 36 + 余量），确认框里没人再按 U
  B.fights.b12_atomheart = (ctx, api) => {
    const { hold, tap, go, face, enemy, toHit, attackRhythm, after, now, note } = api;
    const d = ctx.data, p = P(), e = enemy('yoshihiro'), fb = B.fight;
    if (!p || !e) return hold([]);
    if (p.cid !== 'jotaro4') { hold([]); after('swapJ', 0.4, () => tap('swap')); return; }
    const m = e.mem || {};
    if (d.downT > 0 && !d.solo) {
      const mates = (G.party.members || []).filter((a) => a !== p);
      const blocked = (x) => Math.abs(x - e.x) < 36 || mates.some((a) => Math.abs(a.x - e.x) < 36 && Math.abs(a.y - e.y) < 22);
      // 站在离他 52 px 的一侧（选离自己近、又在场地里的那边）
      const side = p.x < e.x ? -1 : 1;
      let tx = e.x + side * 52;
      if (tx < 160 || tx > 500) tx = e.x - side * 52;
      if (Math.abs(p.x - tx) > 6 || Math.abs(p.y - e.y) > 3) { go(tx, e.y, 4); return; }
      if (!face(e.x > p.x ? 1 : -1)) return;
      hold([]);
      if (ctx.storyU && !blocked(p.x)) after('snap', 0.35, () => { tap('special'); note('b12_snap', { x: Math.round(p.x), ex: Math.round(e.x) }); });
      else if (blocked(p.x)) note('b12_blocked', { mates: mates.map((a) => Math.round(a.x)) });
      return;
    }
    // 他在出手：近身那一下闪开
    if (e.tele && toHit(e) <= 0.16 && fb.dodged !== e.tele && Math.abs(e.x - p.x) < 80) { fb.dodged = e.tele; hold([]); tap('dodge'); return; }
    if (m.mode === 'out' || m.mode === 'lean' || (e.tele && !e.untargetable)) {
      const side = p.x < e.x ? -1 : 1;
      const tx = e.x + side * 22;
      if (Math.abs(p.x - tx) > 10 || Math.abs(p.y - e.y) > 4) { go(tx, e.y, 6); return; }
      if (!face(-side)) return;
      hold([]); attackRhythm(0.22); return;
    }
    // 在相框里：站在和室中间等（离当前相框 60 px，不贴脸）
    const fx = m.frame ? m.frame.x : 300;
    const tx = G.clamp(fx + (p.x < fx ? -60 : 60), 170, 490);
    if (Math.abs(p.x - tx) > 12) { go(tx, 158, 8); return; }
    hold([]);
    void now;
  };

  // 第 13 战：读“剪刀——”那一拍大柳先动的那只手（画面上看得到的小动作），在“布！”出克它的那只
  B.fights.b13_boyiiman = (ctx, api) => {
    const { hold, tap, note } = api;
    hold([]);
    const d = ctx.data, r = d.round;
    if (!r || r.t0 == null || r.pick != null || r.botDone || G.world.cine) return;
    const el = ctx.t - r.t0;
    if (el < 0.75 * 2 - 0.08) return;
    const lose = (d.lose || 0) === 0 && (d.win || 0) === 0 && (d.played || 0) === 0;   // 第一局故意输（看教学）
    const pick = lose ? (r.oy + 1) % 3 : (r.oy + 2) % 3;
    r.botDone = true;
    tap(['left', 'up', 'right'][pick]);
    note('b13_throw', { n: r.n, oy: r.oy, said: r.said, pick, el: Math.round(el * 100) / 100 });
  };
})();
