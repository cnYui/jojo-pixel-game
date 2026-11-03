// 第11章机器人（p4_play.js 自动注入）：b11_spy / b18_cat 潜行、b18_go、b18_avoid、b17a_street、b17b_alley 的打法。
//   照 p4_bot.js 的约定：只按键，不改游戏状态。剧情里的选择题（循环 3、拖时间）由剧情把要选的序号放在 G.flags.c11pick，
//   这里把选择框的光标挪过去再按确定（玩家照着选也一样过）。
'use strict';
(() => {
  const B = window.__bot, G = window.G;
  if (!B || !B.fights) return;
  const A = B.api;
  const { hold, pulse, go, after, now, note } = A;
  const P = A.P, F = A.F;

  // 选择框：光标挪到 c11pick
  const U = G.ui, origUpd = U.updateChoice;
  U.updateChoice = function (dt) {
    const c = this.choiceBox, want = F().c11pick;
    if (c && typeof want === 'number' && c.idx !== want && !B.manual) {
      if (!c.botMove || now() - c.botMove > 0.15) { c.botMove = now(); G.input.inject(c.idx < want ? 'down' : 'up'); }
    }
    return origUpd.apply(this, arguments);
  };

  const near = (p, x, y, r = 3) => Math.abs(p.x - x) <= r && Math.abs(p.y - y) <= r;
  // 走到 (x, y)，到了就转向 face、按住 L 躲
  function hideAt(x, y, face) {
    const p = P();
    if (!near(p, x, y, 3)) { go(x, y, 2); return false; }
    if (face && p.facing !== face) { hold([face > 0 ? 'right' : 'left']); return false; }
    hold(['guard']);
    return true;
  }
  function pressU(key) { after(key, 0.3, () => pulse('special', 4)); }

  // ------------------------------------------------------------ 插曲：三段证据
  B.fights.b11_spy = (ctx) => {
    const d = ctx.data, p = P();
    if (!d.ws || !p) return hold([]);
    const ko = d.ws[0], a = ko.a, got = (d.got || []).length;
    if (d.rec) { hold(d.hidden ? ['guard'] : []); return; }
    const Y = 176;
    if (got === 0) {
      if (p.x > 320 && !near(p, 304, Y)) { go(304, Y, 2); return; }
      if (hideAt(304, Y, -1) && ko.act === 'nails') pressU('u1');
    } else if (got === 1) {
      if (hideAt(247, Y, -1) && ko.act === 'photo') pressU('u2');
    } else if (got === 2) {
      // 等他从左边走回去、过了 330 再挪到盆栽后面，转向右
      const passed = a.x > 330 && (ko.act === 'sign' || a.facing > 0);
      if (!passed) { hideAt(247, Y, 0); return; }
      if (hideAt(304, Y, 1) && ko.act === 'sign') pressU('u3');
    } else hold([]);
  };

  // ------------------------------------------------------------ 最后一次：偷猫草
  B.fights.b18_cat = (ctx) => {
    const d = ctx.data, p = P();
    if (!d.ws || !p) return hold([]);
    const w = d.ws[0], cyc = w.cyc || 0, danger = cyc >= 4.8;
    const Y = 176;
    const spots = [[397, Y], [304, Y], [247, Y], [81, Y]];
    if (!d.cat) {
      if (danger && p.x < 452) {
        // 快抬头了：去最近的躲藏点
        let best = spots[0];
        for (const s of spots) if (Math.abs(s[0] - p.x) < Math.abs(best[0] - p.x)) best = s;
        hideAt(best[0], best[1], 0);
        return;
      }
      if (!near(p, 304, Y, 4)) { go(304, Y, 2); return; }
      hold([]);
      after('catE', 0.3, () => pulse('ok', 4));
      return;
    }
    if (danger && p.x > 285) { hideAt(304, Y, 0); return; }
    go(20, Y, 2);
  };

  // ------------------------------------------------------------ 循环 1：出门
  B.fights.b18_go = () => hold(['right']);

  // ------------------------------------------------------------ 循环 2：躲在反射镜后面撑到 8:25
  B.fights.b18_avoid = () => { hideAt(270, 164, 0); };

  // ------------------------------------------------------------ 第 17 战 段 A：贴墙走，过马路挑空当
  B.fights.b17a_street = (ctx) => {
    const d = ctx.data, p = P();
    if (!d.walkers || !p) return hold([]);
    const Y = 143, cross = [404, 576];
    // 前面 60 px 有人：天堂之门让他走开（冷却好了才按）
    if ((d.hdCd || 0) <= 0 && d.walkers.some((w) => { const dx = (w.a.x - p.x) * p.facing; return w.awayT <= 0 && dx >= 0 && dx <= 56 && Math.abs(w.a.y - p.y) <= 20; })) {
      after('hd', 0.1, () => pulse('special', 4));
    }
    // 过马路这 3 s 里会跑到露伴背后、面朝他的人：高度差 14 以内、朝右走、还没过斑马线
    const threat = (x) => d.walkers.some((w) => {
      const a = w.a;
      return w.awayT <= 0 && Math.abs(a.y - Y) <= 14 && a.facing > 0 && a.x < cross[1] + 10 && a.x > x - 100;
    });
    if (p.x < cross[0] - 16) { go(cross[0] - 12, Y, 2); return; }
    if (p.x < cross[0] && (threat(p.x) || d.pushT < 4)) { go(p.x, Y, 2); return; }
    go(940, Y, 2);
  };

  // ------------------------------------------------------------ 第 17 战 段 B：只往右走，窗口开了按 U
  B.fights.b17b_alley = (ctx) => {
    const d = ctx.data, p = P();
    if (!p) return hold([]);
    if (d.uWin) { hold([]); pressU('alleyU'); return; }
    if (d.done) { hold([]); return; }
    hold(p.x < 600 ? ['right'] : []);
  };
  note('bot_ch11_on');
})();
