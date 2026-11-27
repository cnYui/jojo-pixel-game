// 标题的成就页与游戏内解锁牌共用第五部的像素字体和菜单面板。
'use strict';
(function () {
  const G = window.G;
  const W = 640, H = 360, ROWS = 6, ROW_H = 34;
  const GOLD = '#ffe9a8', DIM = '#b7a9bb';
  const tiers = { bronze: ['一星', '#dcad85'], silver: ['二星', '#d5d7e8'], gold: ['三星', '#ffd870'] };
  const tabs = [['story', '旅程'], ['battle', '战斗'], ['explore', '探索'], ['skill', '技巧']];
  const controls = {
    back: [18, 7, 96, 51],
    prev: [18, 306, 136, 350],
    next: [504, 306, 622, 350],
  };
  const tabBox = i => [18 + i * 109, 54, 116 + i * 109, 98];
  const inside = (t, [x0, y0, x1, y1]) => t.x >= x0 && t.x <= x1 && t.y >= y0 && t.y <= y1;
  const sound = key => G.audio.sfx(key, { vol: .54 });
  const label = (g, text, x, y, color = GOLD, size = 16, align = 'left') =>
    G['f' + size].draw(g, text, x, y, color, { align, outline: '#170e20' });
  const list = () => G.ach.list(tabs[tab][0]);
  const pages = () => Math.max(1, Math.ceil(list().length / ROWS));
  let tab = 0, page = 0, origin, done;
  let toast, lastDraw = 0;

  function button(g, [x0, y0, x1, y1], text, active = false, disabled = false) {
    G.ui.box(g, x0, y0, x1, y1, {
      fill: active ? '#4b332e' : '#23182e', border: active ? GOLD : '#6a5068',
    });
    label(g, text, (x0 + x1) / 2, (y0 + y1) / 2 - 8, disabled ? '#817283' : active ? GOLD : '#eee3e6', 16, 'center');
  }
  function changeTab(i) { tab = G.mod(i, tabs.length); page = 0; sound('menu_move'); }
  function changePage(step) {
    const p = G.clamp(page + step, 0, pages() - 1);
    if (p !== page) { page = p; sound('menu_move'); }
  }
  function back() { sound('menu_cancel'); G.setScene(origin); }
  function update() {
    const I = G.input, t = I.tap;
    if (I.hit('pause') || I.hit('back')) { I.consume('pause'); I.consume('back'); back(); return; }
    if (t) {
      if (inside(t, controls.back)) { back(); return; }
      const i = tabs.findIndex((_, i) => inside(t, tabBox(i)));
      if (i >= 0) { changeTab(i); return; }
      if (inside(t, controls.prev)) changePage(-1);
      if (inside(t, controls.next)) changePage(1);
      return;
    }
    if (I.hit('left') || I.hit('right')) changeTab(tab + (I.hit('left') ? -1 : 1));
    if (I.hit('up') || I.hit('down')) changePage(I.hit('up') ? -1 : 1);
  }

  const date = when => {
    const d = new Date(when);
    return (d.getMonth() + 1) + '月' + d.getDate() + '日';
  };
  function draw(g) {
    g.fillStyle = '#160f21'; g.fillRect(0, 0, W, H);
    button(g, controls.back, '返回');
    label(g, '成就', 320, 21, GOLD, 16, 'center');
    label(g, '已解锁 ' + G.ach.count() + ' / ' + G.ach.list().length, 622, 23, GOLD, 16, 'right');
    tabs.forEach(([, name], i) => button(g, tabBox(i), name, tab === i));
    if (pages() > 1) label(g, (page + 1) + ' / ' + pages(), 622, 72, DIM, 12, 'right');

    list().slice(page * ROWS, (page + 1) * ROWS).forEach((def, i) => {
      const y = 101 + i * ROW_H, got = G.ach.has(def.id), secret = def.hidden && !got;
      const [rank, color] = tiers[def.tier];
      g.fillStyle = i % 2 ? '#21172c' : '#2a1b32'; g.fillRect(18, y, 604, ROW_H - 2);
      g.fillStyle = got ? color : '#6d5770'; g.fillRect(18, y, got ? 3 : 1, ROW_H - 2);
      label(g, secret ? '隐藏成就' : def.name, 32, y + 1, got ? '#fff6e1' : DIM);
      label(g, secret ? '解锁后显示内容。' : def.desc, 32, y + 18, got ? '#ddd0d9' : DIM, 12);
      const progress = G.ach.progress(def.id), when = G.ach.date(def.id);
      const detail = got ? '已解锁' + (when ? '　' + date(when) : '') : progress ? progress.join(' / ') : '未解锁';
      label(g, rank, 610, y + 1, got ? color : DIM, 12, 'right');
      label(g, detail, 610, y + 17, got ? color : DIM, 12, 'right');
    });
    if (pages() > 1) {
      button(g, controls.prev, '上一页', false, page === 0);
      button(g, controls.next, '下一页', false, page === pages() - 1);
    }
    if (!G.touch || !G.touch.on) label(g, '左右切换分类　上下翻页　Esc 返回', 320, 321, DIM, 12, 'center');
  }
  const scene = {
    name: 'achievements',
    frozen: true,
    update,
    drawUI: draw,
    enter() { document.body.classList.add('tc-achievements'); },
    leave() {
      document.body.classList.remove('tc-achievements');
      const resolve = done; done = null;
      if (resolve) resolve();
    },
  };

  function drawToast(g) {
    const ui = G.ui;
    const dt = Math.min(.05, G.clk.ui - lastDraw);
    lastDraw = G.clk.ui;
    if (!G.ach.enabled || G.fadeA > .05 || G.S.cardOn || G.uifx.chapter ||
      ui.dlg || ui.narr || ui.qte || ui.noticeBox || ui.choiceBox || G.world.cine || G.world.combat) return;
    // 对话盖过通知时，留住剩余的显示时间。
    if (toast && (toast.elapsed += dt) >= 2.5) toast = null;
    if (!toast) {
      const def = G.ach.nextToast();
      if (!def) return;
      toast = { def, elapsed: 0 };
      sound('ding');
    }
    const { def, elapsed } = toast;
    const offset = Math.round(220 * (1 - G.clamp(Math.min(elapsed, 2.5 - elapsed) / .2, 0, 1)));
    const x = 426 + offset, color = tiers[def.tier][1];
    G.ui.box(g, x, 9, x + 204, 53, { fill: '#281b30', border: color });
    label(g, '成就解锁', x + 12, 15, color, 12);
    label(g, def.name, x + 12, 30, '#fff6e1');
  }

  G.uiAch = {
    open() {
      origin = G.scene; tab = 0; page = 0;
      return new Promise(resolve => { done = resolve; G.setScene(scene); });
    },
    drawToast,
  };
})();
