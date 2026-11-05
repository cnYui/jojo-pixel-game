// 第7章的试玩机器人：自由走动的任务单 + 第 11 战三段的打法（p4_play.js 自动注入；p4_bot.js 的 api 见那个文件末尾）。
//   约会：先和由花子说话 → 露天座 1 → 露天座 2 → 绕到由花子右边再说一次（四条线索）。
//   解谜：看 1 号、看 4 号（最后看的那张就是选项的默认值），再去和辻彩说“就是这张”。
//   追光：一路往右走到美容院门口。
'use strict';
(() => {
  const B = window.__bot;
  if (!B) return;
  const G = window.G;
  const F = () => G.flags || {};
  const P = () => G.world.player;

  Object.assign(B.plan, {
    date_ch7: [
      { id: 'yk1', go: [282, 156], act: 'ok', done: () => F().ch7c0 },
      { id: 'table1', go: [344, 154], act: 'ok', done: () => F().ch7c1 },
      { id: 'table2', go: [398, 154], act: 'ok', done: () => F().ch7c2 },
      { id: 'yk2', go: [318, 156], act: 'ok', done: () => F().ch7c3 },
      { id: 'wait', go: [320, 158] },
    ],
    salon_ch7: [
      { id: 'face1', go: [343, 146], act: 'ok' },
      { id: 'face4', go: [412, 146], act: 'ok' },
      { id: 'aya', go: [318, 160], act: 'ok' },
      { id: 'aya2', go: [318, 160], act: 'ok' },
      { id: 'wait', go: [318, 160] },
    ],
    street_ch7: [
      { id: 'trail', go: [940, 158], done: () => F().trailEnd },
    ],
  });

  // 段 A：站在坦克和康一之间；坦克靠近就打开它，每隔一阵按住 L 按 J 弹烟头
  B.fights.b11a_sha = (ctx, api) => {
    const { hold, tap, enemy, attackRhythm, after, now } = api;
    const p = P(), sha = enemy('sha');
    if (!p || !sha) return hold([]);
    const ko = G.world.stage.find && G.world.stage.find('koichi');
    const kx = ko ? ko.x : 250;
    const fb = B.fight;
    // 每 7 s 弹一次烟头（先按住格挡，再按攻击）
    if (now() - (fb.cigT || -99) > 7 && Math.abs(sha.x - p.x) > 30) {
      if (!fb.cigOn) { fb.cigOn = now(); }
      hold(['guard']);
      if (now() - fb.cigOn > 0.15) { tap('attack'); fb.cigT = now(); fb.cigOn = 0; }
      return;
    }
    // 站位：坦克那一侧、离康一 30 px
    const side = sha.x >= kx ? 1 : -1;
    const tx = kx + side * 34, ty = sha.y;
    const dx = sha.x - p.x;
    if (Math.abs(dx) < 34 && Math.abs(sha.y - p.y) < 10) {
      const dir = dx > 0 ? 1 : -1;
      if (p.facing !== dir) { hold([dir > 0 ? 'right' : 'left']); return; }
      hold([]);
      attackRhythm(0.2);
      return;
    }
    const keys = [];
    if (Math.abs(tx - p.x) > 4) keys.push(tx > p.x ? 'right' : 'left');
    if (Math.abs(ty - p.y) > 3) keys.push(ty > p.y ? 'down' : 'up');
    hold(keys);
    void after;
  };

  // 段 B：贴着坦克背后打（它追热源 / 追康一）；重量满了按 U；坦克要炸了（boom）就闪开
  B.fights.b11b_sha = (ctx, api) => {
    const { hold, tap, enemy, attackRhythm, now } = api;
    const p = P(), sha = enemy('sha');
    if (!p || !sha) return hold([]);
    const fb = B.fight;
    if (ctx.data.full && !ctx.data.uUsed) {
      hold([]);
      if (now() - (fb.uT || -9) > 0.5) { fb.uT = now(); tap('special'); }
      return;
    }
    if (sha.mem && sha.mem.armed > 0) {
      // 红圈：往远处走
      hold([p.x >= sha.x ? 'right' : 'left']);
      return;
    }
    // 贴在它“行进方向”的背后打（它去撞热源时不会回头）
    const tg = ctx.data.shaTarget, dir = tg && tg.x != null ? (tg.x >= sha.x ? 1 : -1) : (sha.facing || 1);
    const dx = sha.x - p.x, dy = sha.y - p.y;
    const behind = (p.x - sha.x) * dir < 0;
    if (Math.abs(dx) < 30 && Math.abs(dy) < 8 && behind) {
      // 太贴了拳头打不到（判定从身前 6 px 起）：先退半步
      if (Math.abs(dx) < 12) { hold([dx > 0 ? 'left' : 'right']); return; }
      const fd = dx > 0 ? 1 : -1;
      if (p.facing !== fd) { hold([fd > 0 ? 'right' : 'left']); return; }
      hold([]);
      attackRhythm(0.22);
      return;
    }
    const tx = sha.x - dir * 22;
    const keys = [];
    if (Math.abs(tx - p.x) > 4) keys.push(tx > p.x ? 'right' : 'left');
    if (Math.abs(dy) > 3) keys.push(dy > 0 ? 'down' : 'up');
    hold(keys);
    void tap;
  };

  // 段 C：站在康一和吉良之间打吉良；硬币红圈闪开；满能量放时停
  B.fights.b11c_kira = (ctx, api) => {
    const { hold, tap, enemy, attackRhythm, toHit, now } = api;
    const p = P(), k = enemy('kira');
    if (!p || !k) return hold([]);
    const fb = B.fight;
    if (p.energy >= (p.energyMax || 100) && now() - (fb.uT || -9) > 3) { fb.uT = now(); tap('special'); return; }
    // 地上的红圈（硬币）：走开
    const hz = G.world.hazards || [];
    for (const h of hz) {
      if (!h || h.side !== 'enemy' || h.dead || h.shape !== 'ellipse') continue;
      if (Math.abs(h.x - p.x) < (h.rx || 26) + 6 && Math.abs(h.y - p.y) < (h.ry || 10) + 4) {
        hold([p.y > h.y ? 'down' : 'up', h.x > p.x ? 'left' : 'right']);
        return;
      }
    }
    const th = toHit(k);
    if (th <= 0.12 && Math.abs(k.x - p.x) < 50 && fb.dodged !== k.tele) { fb.dodged = k.tele; tap('dodge'); return; }
    const dx = k.x - p.x, dy = k.y - p.y;
    if (Math.abs(dx) < 30 && Math.abs(dy) < 8) {
      const dir = dx > 0 ? 1 : -1;
      if (p.facing !== dir) { hold([dir > 0 ? 'right' : 'left']); return; }
      hold([]);
      attackRhythm(0.22);
      return;
    }
    const keys = [];
    const tx = k.x - (dx > 0 ? 24 : -24);
    if (Math.abs(tx - p.x) > 4) keys.push(tx > p.x ? 'right' : 'left');
    if (Math.abs(dy) > 3) keys.push(dy > 0 ? 'down' : 'up');
    hold(keys);
  };
})();
