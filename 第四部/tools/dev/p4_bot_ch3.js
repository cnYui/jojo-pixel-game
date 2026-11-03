// 第3章的试玩机器人：自由走动任务单 + 第5战三段、小游戏东尼欧的晚餐的打法（p4_play.js 自动注入，规矩见 第四部/docs/分章开发约定.md）。
//   和 p4_bot.js 一样只往输入队列里塞按键，不直接改游戏状态。
'use strict';
(() => {
  const B = window.__bot;
  if (!B) return;
  const G = window.G;
  const F3 = () => (G.P4CH3 && G.P4CH3.F) || {};

  // ------------------------------------------------------------------ 自由走动
  Object.assign(B.plan, {
    class_ch3: [
      { id: 'bento', go: [189, 156], act: 'ok', done: () => F3().bento },
      { id: 'listen', go: [262, 152], act: 'special', done: () => F3().wind },
      { id: 'door', go: [10, 158], done: () => F3().toHall },
    ],
    hall_ch3: [
      { id: 'yk1', go: [82, 155], act: 'ok', done: () => (F3().yTalk || 0) >= 1 },
      { id: 'yk2', go: [82, 155], act: 'ok', done: () => (F3().yTalk || 0) >= 2 },
      { id: 'yk3', go: [82, 155], act: 'ok', done: () => (F3().yTalk || 0) >= 3 },
    ],
    villa_out_ch3: [
      { id: 'mailbox', go: [135, 156], act: 'ok', done: () => F3().mailbox },
      { id: 'booth', go: [513, 156], act: 'ok', done: () => F3().booth },
      { id: 'wuwu', go: [103, 156], act: 'ok', done: () => F3().wuwu },
    ],
  });

  // ------------------------------------------------------------------ 第5战段 1 逃脱：门口射一个字（我讨厌你）→ 听 → 拨号 → 鞋柜 → 电椅
  const PAD = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['*', '0', '#']];
  const NUMBER = '3524189';
  function padPos(k) { for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) if (PAD[r][c] === k) return [r, c]; return [0, 0]; }
  B.fights.b05_escape = (ctx, api) => {
    const d = ctx.data, p = api.P(), fb = B.fight;
    if (!p) return api.hold([]);
    if (d.dial) {
      api.hold([]);
      const want = padPos(NUMBER[d.dial.typed.length] || '3');
      if (d.dial.r !== want[0]) { api.after('dialV', 0.14, () => api.tap(d.dial.r < want[0] ? 'down' : 'up')); return; }
      if (d.dial.c !== want[1]) { api.after('dialH', 0.14, () => api.tap(d.dial.c < want[1] ? 'right' : 'left')); return; }
      api.after('dialJ', 0.22, () => api.tap('attack'));
      return;
    }
    if (!fb.hate && !(G.P4CH3.F.hateNote)) {
      if (!api.go(116, 156, 4)) return;
      if (!api.face(-1)) return;
      api.hold([]);
      api.after('hateJ', 0.3, () => { api.tap('attack'); fb.hate = true; });
      return;
    }
    if (!d.listened) { api.hold([]); api.after('listen', 0.4, () => api.tap('special')); return; }
    if (!d.dialed) { if (!api.go(600, 156, 3)) return; api.hold([]); api.after('dialOpen', 0.3, () => api.tap('ok')); return; }
    if (!d.shoeNailed) {
      const s = api.enemy('vl_shoe');
      if (!s) return api.hold([]);
      if (!api.go(s.x + 14, 156, 3)) return;
      api.hold([]); api.after('shoe', 0.3, () => api.tap('ok')); return;
    }
    if (!d.chairNailed) {
      const s = api.enemy('vl_chair');
      if (!s) return api.hold([]);
      if (!api.go(s.x + 14, 156, 3)) return;
      api.hold([]); api.after('chair', 0.3, () => api.tap('ok')); return;
    }
    api.hold([]);
  };

  // ------------------------------------------------------------------ 第5战段 2 别墅：U 烧断发丝 → 贴字陷阱等她踩 + 尾巴抽打；她出招就按住 L 挡
  B.fights.b05_lovedeluxe = (ctx, api) => {
    const d = ctx.data, p = api.P(), yk = api.enemy('yukako'), fb = B.fight;
    if (!p || !yk) return api.hold([]);
    if (d.tether && !d.uUsed) { api.hold([]); if (ctx.storyU) api.after('burn', 0.4, () => api.tap('special')); return; }
    const th = api.toHit(yk);
    const busy = !!(yk.tele || yk.atk);
    // 她在出招：按住 L 格挡（头发抓的地面圈也能挡），不按 J（按住 L 按 J 会贴字）
    if (busy && th < 0.5) { api.hold(['guard']); fb.guardT = api.now(); return; }
    if (api.now() - (fb.guardT || -9) < 0.25) { api.hold(['guard']); return; }
    // 每隔一会儿在脚下贴一个字：按住 L、按 J
    const traps = (d.traps || []).length;
    if (traps < 2 && api.now() - (fb.trapT || -9) > 5) {
      if (fb.trapStep !== 1) { api.hold(['guard']); fb.trapStep = 1; fb.trapAt = api.now(); return; }
      if (api.now() - fb.trapAt < 0.12) { api.hold(['guard']); return; }
      api.hold(['guard']); api.tap('attack'); fb.trapStep = 0; fb.trapT = api.now(); return;
    }
    const dx = yk.x - p.x, adx = Math.abs(dx);
    if (!p.atk && (adx > 30 || adx < 10 || Math.abs(p.y - yk.y) > 4)) { api.go(yk.x - Math.sign(dx || 1) * 22, yk.y, 4); return; }
    if (!p.atk && !api.face(Math.sign(dx || 1))) return;
    api.hold([]);
    api.attackRhythm(0.24);
  };

  // ------------------------------------------------------------------ 第5战段 3 海岬：选「啪嘤」（第 3 张），U 由 QTE 那边按
  B.fights.b05_cape = (ctx, api) => {
    const d = ctx.data;
    api.hold([]);
    if (d.phase !== 'choose') return;
    if (d.sel !== 2) { api.after('capeSel', 0.18, () => api.tap('right')); return; }
    api.after('capeJ', 0.25, () => api.tap('attack'));
  };

  // ------------------------------------------------------------------ 小游戏 东尼欧的晚餐：洗手 → 东尼欧背对时溜到目标按 E；被他看着就退回门口
  B.fights.mg_tonio = (ctx, api) => {
    const d = ctx.data, p = api.P(), t = api.enemy('tonio_k'), C3 = G.P4CH3;
    if (!p || !t || d.round == null) return api.hold([]);
    if (d.wash) { api.hold([]); api.after('wash', 0.09, () => api.tap(d.wash.n % 2 ? 'right' : 'left')); return; }
    const view = d.view || C3.KT.view;
    const seenAt = (x) => !(d.cook > 0) && Math.sign(x - t.x) === t.facing && Math.abs(x - t.x) <= view + 12;
    const tg = C3.TARGETS[d.round];
    if (!d.washed) {
      // 他朝左走（快到左端）时，水槽也在视线里：等他转身
      if (seenAt(C3.KT.sink) || (t.facing < 0 && t.x < 260)) { api.go(30, 158, 4); return; }
      if (!api.go(C3.KT.sink, 158, 3)) return;
      api.hold([]); api.after('sinkE', 0.15, () => api.tap('ok')); return;
    }
    // 在视线里就往门口退
    if (seenAt(p.x)) { api.go(30, 158, 4); return; }
    const at = Math.abs(p.x - tg.x) <= 6;
    if (at) { api.hold([]); api.after('lookE', 0.12, () => api.tap('ok')); return; }
    if (tg.x < 200) {
      // 操作台在巡逻范围左边：路上和目标都不在视线里就走
      if (!seenAt(tg.x) && !seenAt((p.x + tg.x) / 2)) api.go(tg.x, 158, 4); else api.hold([]);
      return;
    }
    // 汤锅、烤箱、冰箱要从他身边过：等他在灶台前做菜（背对着）
    if (d.cook > 0) { api.go(tg.x, 158, 4); return; }
    // 他朝右走、还没到灶台：跟在他背后（他看不见背后），他一停下来做菜就从身边溜过去
    if (t.facing > 0 && t.x < C3.KT.stove && !d.pause) { api.go(Math.max(120, t.x - 40), 158, 4); return; }
    if (!seenAt(160)) api.go(160, 158, 4); else api.go(30, 158, 4);
  };
})();
