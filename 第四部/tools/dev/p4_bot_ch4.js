// 第4章自动试玩的任务单和打法（p4_play.js 自动注入；api 见 p4_bot.js 的 B.api）。
'use strict';
(() => {
  const B = window.__bot;
  if (!B) return;
  const { G, P, F, hold, tap, go, face, enemy, attackRhythm, after, toHit, note, now } = B.api;

  Object.assign(B.plan, {
    living_ch4: [
      { id: 'console', go: [296, 158], act: 'ok' },
      { id: 'tv', go: [322, 156], act: 'ok', done: () => F().tvGo },
    ],
    harbor_ch4: [
      { id: 'swap_koichi', act: 'swap', done: () => P() && P().cid === 'koichi' },
      { id: 'lamp', go: [411, 156], act: 'special', done: () => F().otoGo },
      { id: 'walk', go: [600, 158], done: () => F().otoGo },
    ],
    street_ch4: [
      { id: 'tv', act: 'swap', done: () => P() && P().cid === 'joseph_old' },
      { id: 'tv_look', go: [252, 158], act: 'special' },
      { id: 'cry', go: [440, 158], done: () => F().cry },
      { id: 'box_e', go: [470, 158], act: 'ok', done: () => F().boxSeen },
      { id: 'box_u', go: [470, 158], act: 'special', done: () => F().photo },
      { id: 'clerk', go: [578, 154], act: 'ok', done: () => F().compact },
      { id: 'box_e2', go: [470, 158], act: 'ok', done: () => F().makeup },
      { id: 'trail', go: [950, 158], done: () => F().toPond },
    ],
    pond_ch4: [
      { id: 'pond', go: [300, 158], done: () => F().splash },
      { id: 'swap_joseph', act: 'swap', done: () => P() && P().cid === 'joseph_old' },
      { id: 'edge', go: [320, 152], act: 'special', done: () => F().blood },
      { id: 'splash', go: [322, 152], act: 'ok', done: () => F().saved },
    ],
  });

  // 走到 (x, y) 停下：到了以后 14 px 内不再重新走（转身那一步会挪 1 px，不然在边界上来回晃）
  function park(fb, key, x, y) {
    const p = P();
    if (fb[key] && Math.abs(p.x - x) <= 14 && Math.abs(p.y - y) <= 4) return true;
    fb[key] = false;
    if (!go(x, y, 3)) return false;
    fb[key] = true;
    return true;
  }
  // 对着一个对手：贴到 24 px、对齐 y、出拳；它在预警就闪
  function brawl(e, fb, o = {}) {
    const p = P();
    if (!p || !e) return hold([]);
    if ((e.tele || e.atk) && toHit(e) <= (o.dodgeAt || 0.14) && fb.dodged !== e.tele && Math.abs(e.x - p.x) < 150) { fb.dodged = e.tele; hold([]); tap('dodge'); return; }
    const dx = e.x - p.x, adx = Math.abs(dx);
    if (!p.atk && !p.rush && (adx > 36 || adx < 10 || Math.abs(p.y - e.y) > 4)) { go(e.x - Math.sign(dx || 1) * 24, e.y, 4); return; }
    if (!p.atk && !p.rush && !face(Math.sign(dx || 1))) return;
    hold([]);
    attackRhythm(0.22);
  }

  // 段 A：拉近 3 次 → 打坏摩托 → J3
  B.fights.b06a_rhcp = (ctx) => {
    const d = ctx.data, p = P(), e = enemy('rhcp_bike'), fb = B.fight;
    if (!p || !e) return hold([]);
    if (d.tauntT != null) { hold([]); attackRhythm(0.24); return; }
    if ((d.pulls || 0) < 3) {
      const dx = e.x - p.x;
      if (Math.abs(dx) > 90 || Math.abs(dx) < 30 || Math.abs(e.y - p.y) > 5) { go(e.x - 60, e.y, 6); return; }
      if (!face(Math.sign(dx) || 1)) return;
      hold(['guard']);
      after('pullJ', 0.3, () => tap('attack'));
      return;
    }
    brawl(e, fb);
  };

  // 段 B：钻地的辣妹
  const GR = [[96, 158], [232, 168], [372, 154], [520, 166], [688, 156], [836, 168]];
  B.fights.b06b_rhcp = (ctx) => {
    const d = ctx.data, p = P(), e = enemy('rhcp'), fb = B.fight;
    if (!p || !e) return hold([]);
    if (d.final === 'fork' || d.final === 'closing') return hold([]);
    if (d.final === 'tyre_wait') {
      if (!park(fb, 'pkT', 590, 152)) return;
      if (!face(1)) return;
      hold([]); attackRhythm(0.24); return;
    }
    if (d.final === 'tyre_open' || d.final === 'tyre_out') {
      if (!park(fb, 'pkO', 570, 152)) return;
      if (!face(1)) return;
      if (d.final === 'tyre_out' && e.visible !== false && !e.hidden) { hold(['guard']); after('tyreJ', 0.15, () => tap('attack')); }
      else hold([]);
      return;
    }
    if (!e.hidden && e.alpha > 0.5) { fb.build = null; brawl(e, fb, { dodgeAt: 0.16 }); return; }
    // 它在地下：在离自己最近的格栅上做一块黏地，然后守在旁边
    const live = (d.stickies || []).find((s) => s.t > 1.5);
    if (live) { go(live.x - 36, live.y, 4); if (!fb.build) face(1); return; }
    const g = GR.slice().sort((a, b) => Math.abs(a[0] - p.x) - Math.abs(b[0] - p.x))[0];
    const rub = (d.rubbles || []).find((r) => Math.abs(r.x - g[0]) < 12 && Math.abs(r.y - g[1]) < 6);
    if (rub) {
      if (!park(fb, 'pkR', rub.x - 30, rub.y)) return;
      hold(['guard']); after('stickJ', 0.2, () => tap('attack'));
      return;
    }
    if (!park(fb, 'pkG', g[0] - 30, g[1])) return;
    if (!face(1)) return;
    hold([]);
    fb.build = true;
    attackRhythm(0.24);
    if ((fb.taps || 0) > 3) fb.taps = 0;
  };

  // 段 C：先盘问一个船员，再削音石明的帽子；然后打音石明
  B.fights.b06c_rhcp = (ctx) => {
    const d = ctx.data, p = P(), fb = B.fight;
    if (!p) return hold([]);
    if (d.lunging) return hold([]);
    if (!d.found) {
      const a = enemy('sh_crew_a'), o = enemy('sh_crew_oto');
      if (!fb.asked && a) {
        if (!park(fb, 'pkA', a.x - 20, a.y)) return;
        hold([]); after('ask', 0.3, () => { tap('ok'); fb.asked = true; note('c_ask'); });
        return;
      }
      if (!o) return hold([]);
      if (!park(fb, 'pkC', o.x - 20, o.y)) return;
      if (!face(1)) return;
      hold(['guard']); after('capJ', 0.3, () => tap('attack'));
      return;
    }
    brawl(enemy('otoishi'), fb);
  };
  void now;
})();
