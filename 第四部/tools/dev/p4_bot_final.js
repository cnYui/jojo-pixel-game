// 终章自动试玩的任务单和打法（p4_play.js 自动注入；框架在 p4_bot.js）。
//   corner_fin：段 A 打完走到亿泰身边。b19_kq_a 打吉良、躲触爆；b19_kq_b 壁炉撒灰、泡泡贴上来时格挡；
//   b19_kq_c 照步骤做；b19_kq_d 亿泰回来后换他、拉开猫草、J3 破盾。段 E 的 QTE 由框架处理（press 按 q.key，mash 连按 J）。
'use strict';
(() => {
  const B = window.__bot;
  if (!B) return;
  const { G, P, now, hold, tap, pulse, after, go, face, enemy, toHit, attackRhythm, note } = B.api;
  const R = () => G.P4FIN;
  const cast = (k) => (R() ? R().cast(k) : k);

  B.plan.corner_fin = [
    { id: 'to_okuyasu', go: [() => (enemy(cast('okuyasu')) || {}).x + 30, 160] },
  ];
  // 任务单的 go 只认数字：动态目标在这里换算
  Object.defineProperty(B.plan.corner_fin[0], 'go', { get() { const o = enemy(cast('okuyasu')); return [o ? o.x + 30 : 330, o ? o.y : 160]; } });

  // 离最近的空气弹多远（世界坐标，y 乘 1.4）
  function nearestBubble(d) {
    const p = P(), list = (d.bub && d.bub.list) || [];
    let best = null, bd = Infinity;
    for (const b of list) { if (b.dead) continue; const dd = Math.hypot(b.x - p.x, (b.y - p.y) * 1.4); if (dd < bd) { bd = dd; best = b; } }
    return { b: best, d: bd };
  }
  // 贴到对手身边打三连 / 连打；对方出手前闪开
  function brawl(ctx, e, o = {}) {
    const p = P(), fb = B.fight;
    if (!p || !e || e.remove) { hold([]); return; }
    if (e.tele && toHit(e) <= 0.14 && fb.dodged !== e.tele && Math.abs(e.x - p.x) < 90) { fb.dodged = e.tele; hold([]); tap('dodge'); return; }
    const side = p.x < e.x ? -1 : 1;
    const tx = G.clamp(e.x + side * 26, 24, 936), adx = Math.abs(e.x - p.x);
    if (!p.atk && !p.rush && (adx > 42 || adx < 10 || Math.abs(p.y - e.y) > 5)) { go(tx, e.y, 6); return; }
    if (!p.atk && !p.rush && !face(-side)) return;
    hold([]);
    const n = fb.taps || 0;
    if (o.j3) { if (n < 3) attackRhythm(0.22); else if (now() - fb.lastJ > 0.7) fb.taps = 0; return; }
    if (n < 3) attackRhythm(0.22); else if (n < 14) attackRhythm(0.08); else if (now() - fb.lastJ > 1.0) fb.taps = 0;
  }

  // 段 A：打吉良；站在粉光圈里就先跑开；泡泡贴近就按住 L
  B.fights.b19_kq_a = (ctx) => {
    const d = ctx.data, p = P(), k = enemy('kira');
    if (!p) return hold([]);
    for (const b of d.bombs || []) {
      if (!b.dead && b.t > 1.1 && Math.hypot(p.x - b.x, (p.y - b.y) * 2) < 52) { go(b.x + (p.x < b.x ? -70 : 70), p.y, 4); return; }
    }
    const nb = nearestBubble(d);
    if (nb.b && nb.d < 20) { face(nb.b.x > p.x ? 1 : -1); hold(['guard']); return; }
    if (nb.b && nb.d < 48 && !p.atk && !p.rush) { const away = p.x < nb.b.x ? -1 : 1; go(G.clamp(p.x + away * 60, 30, 610), p.y < 156 ? p.y + 10 : p.y - 10, 4); return; }
    if (p.energy >= (p.energyMax || 100) && k && Math.abs(k.x - p.x) < 120) { after('aU', 0.3, () => tap('special')); }
    brawl(ctx, k);
  };
  // 段 B：先到壁炉撒灰，然后等泡泡贴上来时格挡（按住 L）
  B.fights.b19_kq_b = (ctx) => {
    const d = ctx.data, p = P();
    if (!p || !d.bub) return hold([]);
    const nb = nearestBubble(d);
    if (nb.b && nb.d < 26) { face(nb.b.x > p.x ? 1 : -1); if (nb.d < 20) hold(['guard']); return; }
    if (!go(103, 150, 3)) return;
    hold([]);
    if (!B.fight.ashed || (d.bub.revealUntil < G.clk.world && d.ash > 0 && nb.b)) { B.fight.ashed = true; after('ash', 0.3, () => tap('ok')); }
  };
  // 段 C：花瓶 J3 → E 捡碎片 → L+J 修碎片 → 早人 E → 电话响按 J
  B.fights.b19_kq_c = (ctx) => {
    const d = ctx.data, p = P(), fb = B.fight;
    if (!p || d.busy) return hold([]);
    if (fb.st !== d.st) { fb.st = d.st; fb.taps = 0; fb.lastJ = -9; note('c_step', { st: d.st }); }
    if (d.st === 0) {
      if (!p.atk && !go(339 - 22, 150, 3)) return;
      if (!p.atk && !face(1)) return;
      hold([]);
      if ((fb.taps || 0) < 3) attackRhythm(0.22); else if (now() - fb.lastJ > 0.8) fb.taps = 0;
      return;
    }
    if (d.st === 1) { if (!go(339, 150, 3)) return; hold([]); after('pick', 0.3, () => tap('ok')); return; }
    if (d.st === 2) { hold(['guard']); after('fixJ', 0.4, () => tap('attack')); return; }
    if (d.st === 3) {
      const hy = enemy(cast('hayato'));
      if (!hy) return hold([]);
      if (!go(hy.x + 16, hy.y, 4)) return;
      hold([]); after('hayatoE', 0.3, () => tap('ok')); return;
    }
    if (d.st === 4) { hold([]); after('phoneJ', 0.5, () => tap('attack')); }
  };
  // 段 D：亿泰回来之前只用仗助打；回来以后换亿泰：拉开猫草（L+J），护盾没了换着打
  B.fights.b19_kq_d = (ctx) => {
    const d = ctx.data, p = P(), k = enemy('kira'), fb = B.fight;
    if (!p || !k) return hold([]);
    const oc = cast('okuyasu');
    if (d.back && p.cid !== oc && !(d.shieldOff > 0)) { hold([]); after('swapO', 0.4, () => tap('swap')); return; }
    if (p.cid === oc) {
      const nb = nearestBubble(d);
      if (nb.b && nb.d < 40 && Math.abs(nb.b.y - p.y) < 10) { face(nb.b.x > p.x ? 1 : -1); hold([]); attackRhythm(0.25); return; }
      if (!(d.shieldOff > 0) && !(d.pullCd > 0)) {
        if (Math.abs(k.x - p.x) > 110 || Math.abs(k.y - p.y) > 12) { go(k.x + (p.x < k.x ? -80 : 80), k.y, 8); return; }
        hold(['guard']); after('pullJ', 0.3, () => tap('attack')); return;
      }
    }
    if (p.cid !== oc) {
      const nb = nearestBubble(d);
      if (nb.b && nb.d < 24) { face(nb.b.x > p.x ? 1 : -1); hold(['guard']); return; }
    }
    if (p.energy >= (p.energyMax || 100)) { after('dU', 0.3, () => tap('special')); }
    const shield = !(d.shieldOff > 0) && !(d.shieldBreak > 0);
    brawl(ctx, k, { j3: shield });
    void fb;
  };
})();
