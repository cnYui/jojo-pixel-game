// 成就页面 + 解锁牌的画法（成就文档 §三、实施文档 §3.4 / §3.6）。
//   页面是整个 640×360 的独立场景：进去时记住来源（标题），Esc / 返回回标题，并把标题菜单的 token（menuTask）一起作废，
//   免得标题菜单协程和成就页同时抢输入。解锁牌不暂停、不抢输入，只排在画面右上角，由 G.ui.draw 调 drawToast。
'use strict';
(function () {
  const G = window.G;
  const UW = 640, UH = 360;
  const GOLD = '#ffe9a8';
  const SEL = 'rgba(255,211,74,0.18)';
  // 等级色（成就文档 §三：铜 / 银 / 金 / 白金）；边框取深一档
  const TIER_COL = { bronze: '#b87333', silver: '#c8ccd8', gold: '#ffd040', platinum: '#d8e8ff' };
  const TIER_DARK = { bronze: '#5a3010', silver: '#585c68', gold: '#704c00', platinum: '#48587a' };
  const TIER_NAME = { bronze: '铜', silver: '银', gold: '金', platinum: '白金' };
  const TABS = [['all', '全部'], ['story', '剧情旅程'], ['trial', '星尘试炼']];
  const ROW_H = 34, ROWS = 7, LIST_Y = 64;                    // 一屏 7 条
  // ⚙ 解锁牌：宽 190 × 高 40，右上角 x 444–634 / y 8–48（战斗评价牌在 y 98–176，互不重叠）
  const TOAST = { x0: 444, x1: 634, y0: 8, y1: 48, slide: 0.25, hold: 3, out: 0.25 };
  // 滑到够远的地方再画（用平移做滑入滑出：box 是整数坐标，直接改坐标会抖）
  const SX = 210;

  const clamp01 = v => (v < 0 ? 0 : v > 1 ? 1 : v);
  const A = () => G.ach || null;
  const F16 = () => { if (!G.f16 && G.initFonts) G.initFonts(); return G.f16; };
  const F12 = () => { if (!G.f12 && G.initFonts) G.initFonts(); return G.f12; };
  const snd = (n, o) => { if (n && G.audio && G.audio.sfx) G.audio.sfx(n, o); };
  const task = fn => (G.runPromise || (f => new Promise(f)))(fn);
  const mark = id => (A() && A().at(id) > 0 ? A().dateOf(id) : 0);
  const fmtDate = ms => {
    if (!ms) return '';
    const d = new Date(ms), p = n => (n < 10 ? '0' : '') + n;
    return (d.getMonth() + 1) + '-' + p(d.getDate());
  };
  // 超出宽度截断加省略号（说明只占一行）
  function fit(F, str, maxW) {
    str = String(str);
    if (F.width(str) <= maxW) return str;
    let s = '';
    for (const ch of str) { if (F.width(s + ch + '…') > maxW) break; s += ch; }
    return s + '…';
  }
  const tierColor = t => TIER_COL[t] || TIER_COL.bronze;

  // ---------------------------------------------------------------- 勋章图标（28×28，代码画）
  // 圆角底按等级色，中间 14×14 点阵（GLYPH 在 story\achievements_def.js，规划方后补图案），未解锁换成锁
  function icon(g, d, x, y, got) {
    const base = got ? tierColor(d.tier) : '#3a3648', dark = got ? (TIER_DARK[d.tier] || '#222') : '#1c1a26';
    g.save();
    // 圆角：四角各削 2 px，中间两行收 1 px
    g.fillStyle = dark;
    g.fillRect(x + 1, y, 26, 28); g.fillRect(x, y + 1, 28, 26);
    g.fillStyle = base;
    g.fillRect(x + 1, y + 1, 26, 26); g.fillRect(x, y + 3, 28, 22);
    g.fillStyle = 'rgba(255,255,255,0.28)';
    g.fillRect(x + 2, y + 2, 24, 1);
    g.fillStyle = 'rgba(0,0,0,0.25)';
    g.fillRect(x + 2, y + 24, 24, 1);
    const glyph = (G.ACH_GLYPH || {})[got ? d.icon : 'lock'] || (G.ACH_GLYPH || {}).lock;
    if (glyph) {
      const gx = x + 7, gy = y + 7, fg = got ? '#1a1020' : '#8a8498';
      g.fillStyle = fg;
      for (let r = 0; r < 14; r++) {
        const row = glyph[r] || '';
        for (let c = 0; c < 14; c++) if (row[c] === '#') g.fillRect(gx + c, gy + r, 1, 1);
      }
      if (got) { g.fillStyle = 'rgba(255,255,255,0.5)'; for (let r = 0; r < 14; r++) if ((glyph[r] || '')[0] === '#') g.fillRect(gx, gy + r, 1, 1); }
    }
    g.restore();
  }

  // ---------------------------------------------------------------- 解锁牌（被 G.ui.draw 在最上层调）
  // 队列依次出；黑幕 G.fadeA 盖着的时候连着画也看不见，所以排队等黑幕散了再开始
  let cur = null, endedAt = 0;
  function drawToast(g) {
    const A_ = A();
    if (!A_ || !A_.toastQueue) return;
    if (G.fadeA >= 0.05) return;
    if (cur) { drawToastCard(g, cur); return; }
    if (G.clk.ui - endedAt < 0.05) return;                    // 两条之间留一帧缝，免得边框糊在一起
    const q = A_.toastQueue();
    const item = q.shift();
    if (!item) return;
    cur = { def: item.def, t0: G.clk.ui, loud: item.def.tier === 'gold' || item.def.tier === 'platinum' };
    if (cur.loud) snd('sparkle', { vol: .7 });
    snd('ding', { vol: .6, rate: cur.loud ? 1.1 : 0.95 });
  }
  function drawToastCard(g, c) {
    const t = G.clk.ui - c.t0;
    if (t < TOAST.slide) return toastAt(g, c, (1 - t / TOAST.slide) * SX);   // 滑入
    if (t < TOAST.slide + TOAST.hold) return toastAt(g, c, 0);                // 停 3 s
    const k = (t - TOAST.slide - TOAST.hold) / TOAST.out;
    if (k >= 1) { cur = null; endedAt = G.clk.ui; return; }                   // 滑出完毕，下一条
    toastAt(g, c, k * SX);
  }
  // dx = 往右挪多少（用平移画，box 的整数坐标就不用在动画里抖动）
  function toastAt(g, c, dx) {
    const F16x = F16(), F12x = F12();
    if (!F16x || !F12x) return;
    const t = G.clk.ui - c.t0;
    const x0 = TOAST.x0 + dx, y0 = TOAST.y0, x1 = TOAST.x1 + dx, y1 = TOAST.y1;
    const col = tierColor(c.def.tier);
    G.ui.box(g, x0, y0, x1, y1, { fill: 'rgba(18,14,34,0.92)', border: col });
    icon(g, c.def, Math.round(x0 + 7), y0 + 8, true);
    F12x.draw(g, '成就解锁', x0 + 41, y0 + 5, '#c8c4d8', { outline: '#140c18' });
    F16x.draw(g, fit(F16x, c.def.name, x1 - x0 - 48), x0 + 41, y0 + 20, col, { outline: '#140c18' });
    // 金 / 白金：右边飘几点星光，和别的解锁牌区分开
    if (c.loud) {
      // 偶尔超时被切到后台再回来，dt 会很大；按秒取余落到 NaN 就画不出星光，这里兜一下
      const rnd = G.hash01 || Math.random;
      if (!isFinite(t)) return;
      for (let i = 0; i < 5; i++) {
        const p = (t * 0.9 + i * 0.2) % 1, sx = Math.round(x1 - 10 - rnd(i, 3) * 120), sy = Math.round(y0 + 6 + p * 30);
        if (sy > y1 - 4) continue;
        g.fillStyle = i % 2 ? '#fff6c0' : '#fff';
        g.fillRect(sx, sy, 1, 1);
        if (i % 2) { g.fillRect(sx - 1, sy, 3, 1); g.fillRect(sx, sy - 1, 1, 3); }
      }
    }
  }

  // ---------------------------------------------------------------- 成就页面（独立场景）
  // task = 这一次进入的 Promise（null = 没开着）；holdDir / holdT = 触屏上下滑动的连走
  const page = { task: null, tab: 0, sel: 0, top: 0, t: 0, res: null, from: null, holdDir: 0, holdT: 0 };
  const listOf = () => { const a = A(); return a ? a.list(TABS[page.tab][0]) : []; };
  // 选中行跟着列表走：切页签 / 成就数量变化时不越界
  function clampSel() {
    const n = listOf().length;
    page.sel = n ? Math.max(0, Math.min(n - 1, page.sel)) : 0;
    const maxTop = Math.max(0, n - ROWS);
    if (page.sel < page.top) page.top = page.sel;
    if (page.sel >= page.top + ROWS) page.top = page.sel - ROWS + 1;
    page.top = Math.max(0, Math.min(maxTop, page.top));
  }
  function setTab(i) {
    page.tab = G.mod(i, TABS.length);
    page.sel = 0; page.top = 0;
    snd('menu_move', { vol: .5 });
  }
  // afk = 被别的场景顶掉（不是玩家按了返回）：这里不播取消音，场景切换自己有声
  function close(afk) {
    if (!page.task) return;
    page.task = null;
    if (!afk) snd('menu_cancel', { vol: .6 });
    const r = page.res; page.res = null;
    if (r) r();
  }
  function openPage() {
    if (page.task) return page.task;                          // 已经开着：复用同一次进入（不叠两层）
    page.t = 0; page.from = G.scene; page.sel = 0; page.top = 0;
    // 标题菜单协程靠 token 判断自己还在不在前台（main.js 的 menuTask）：这里把它作废，免得两套输入同时吃按键
    const token = (G.menuTask | 0) + 1;
    G.menuTask = token;
    // 先换场景再挂起调用方：setScene 是同步的，如果它同步调了上一个场景的 leave()（成就页恰好在场时会 close 掉这一次），
    //   顺序反过来会把刚挂上的 task / res 又清掉，调用方永远等下去
    G.setScene(achScene);
    const p = task(res => { page.res = res; });
    page.task = p;
    snd('menu_confirm', { vol: .5 });
    return p;
  }
  // 回标题：来源就是标题时直接恢复（不重新起标题菜单），否则走 G.goTitle
  async function back() {
    close();
    if (page.from && page.from.name === 'title') {
      G.setScene(page.from);
      snd('menu_confirm', { vol: .5 });
      return;
    }
    if (G.goTitle) await G.goTitle();
  }

  // 触屏：点页签 / 点行 / 上下滑动 / 点左上「返回」（照标题菜单那条路：只认 G.input.tap）
  // 页签宽度的算法只写一处：画的时候和点的时候用同一份，改了不会错位
  const tabWidth = (F, i) => F.width(TABS[i][1]) + 24;
  function tapAt(t) {
    if (t.x <= 96 && t.y >= 2 && t.y <= 28) { back().catch(e => { if (!G.cancelled(e)) console.error(e); }); return; }
    const tabY0 = 36, tabY1 = 56;
    if (t.y >= tabY0 - 4 && t.y <= tabY1 + 4) {
      let x = 24;
      for (let i = 0; i < TABS.length; i++) {
        const w = tabWidth(F16(), i);
        if (t.x >= x && t.x <= x + w) { setTab(i); return; }
        x += w + 8;
      }
      return;
    }
    if (t.y >= LIST_Y && t.y < LIST_Y + LIST_H()) {
      const row = Math.floor((t.y - LIST_Y) / ROW_H);
      const list = listOf(), i = page.top + row;
      if (row >= 0 && i < list.length) { page.sel = i; snd('menu_move', { vol: .5 }); }
    }
  }
  const LIST_H = () => ROWS * ROW_H;
  // 上下移一行（到头就停：成就页不像菜单那样循环，滚到底看得见）
  function moveSel(d) {
    const n = listOf().length;
    if (!n) return;
    const v = Math.max(0, Math.min(n - 1, page.sel + d));
    if (v !== page.sel) { page.sel = v; snd('menu_move', { vol: .5 }); }
    clampSel();
  }
  function update(dt) {
    if (!page.task) return;
    page.t += dt;
    const I = G.input;
    if (!I) return;
    if (I.tap) tapAt(I.tap);
    if (page.t < 0.12 && !I.tap) return;                       // 刚进来的一下确认键不当操作（和菜单一样留个延迟）
    if (I.hit('up') || I.hit('down')) moveSel(I.hit('up') ? -1 : 1);
    if (I.hit('left') || I.hit('right')) setTab(page.tab + (I.hit('left') ? -1 : 1));
    if (I.hit('swap')) setTab(page.tab + 1);                   // 说明里写的 Q / E 切页签
    if (I.hit('pause') || I.hit('back')) {
      I.consume('pause'); I.consume('back');
      back().catch(e => { if (!G.cancelled(e)) console.error(e); });
      return;
    }
    // 触屏上下滑：方向盘 / 手指按住 up、down 时先走一步，按住 0.35 s 后每 0.11 s 连着走
    const dir = I.isDown('up') && !I.isDown('down') ? -1 : I.isDown('down') && !I.isDown('up') ? 1 : 0;
    if (dir !== page.holdDir) { page.holdDir = dir; page.holdT = 0; if (dir) moveSel(dir); }
    else if (dir) {
      page.holdT += dt;
      if (page.holdT > 0.35) {
        page.holdT -= 0.11;
        moveSel(dir);
      }
    }
    clampSel();
  }

  function drawUI(g) {
    const F16 = F16(), F12 = F12();
    if (!F16 || !A()) return;
    g.imageSmoothingEnabled = false;
    // 整页底色（世界层在后面，压暗一点让字看得清）
    g.fillStyle = 'rgba(8,6,18,0.82)';
    g.fillRect(0, 0, UW, UH);
    const s = A().summary();
    F16.draw(g, '成就', 24, 8, GOLD, { outline: '#1a1020' });
    const title = '已解锁 ' + s.got + ' / ' + s.total;
    const pts = '成就点 ' + s.pts + ' / ' + s.ptsTotal;
    F12.draw(g, pts, 628, 12, '#ffd9a0', { align: 'right', outline: '#140c18' });
    F16.draw(g, title, 628 - F12.width(pts) - 18, 8, GOLD, { align: 'right', outline: '#1a1020' });
    g.fillStyle = 'rgba(255,233,168,0.3)'; g.fillRect(24, 30, 604, 1);
    // 页签
    let x = 24;
    TABS.forEach(([key, name], i) => {
      const w = tabWidth(F16, i), on = i === page.tab;
      if (on) { g.fillStyle = SEL; g.fillRect(x, 34, w, 22); }
      g.fillStyle = on ? GOLD : 'rgba(200,196,216,0.5)'; g.fillRect(x, 34, w, on ? 2 : 1);
      F16.draw(g, name, x + w / 2, 38, on ? '#fff4d6' : '#9a93a8', { align: 'center', outline: on ? '#140c18' : null });
      x += w + 8;
    });
    g.fillStyle = 'rgba(255,233,168,0.3)'; g.fillRect(24, 58, 604, 1);
    // 列表
    const list = listOf();
    clampSel();
    const H = LIST_H();
    g.save();
    g.beginPath(); g.rect(20, LIST_Y, 604, H); g.clip();
    for (let r = 0; r < ROWS; r++) {
      const i = page.top + r, d = list[i];
      if (!d) break;
      drawRow(g, d, i, LIST_Y + r * ROW_H);
    }
    g.restore();
    if (!list.length) F16.draw(g, '这里还没有成就。', UW / 2, LIST_Y + 40, '#8a8498', { align: 'center' });
    // 滚动条
    if (list.length > ROWS) {
      const barH = Math.max(16, Math.round(H * ROWS / list.length));
      const barY = LIST_Y + Math.round((H - barH) * (page.top / Math.max(1, list.length - ROWS)));
      g.fillStyle = 'rgba(255,255,255,0.08)'; g.fillRect(628, LIST_Y, 4, H);
      g.fillStyle = 'rgba(255,233,168,0.6)'; g.fillRect(628, barY, 4, barH);
    }
    // 底部操作提示
    F12.draw(g, G.touch && G.touch.on ? '点页签切换　上下滑动　左上返回' : '↑↓ 选择　←→ / Q·E 切页签　Esc 返回', 320, 342, '#9a93a8', { align: 'center' });
    // 左上「返回」（触屏按下；键鼠也能点）
    g.fillStyle = 'rgba(20,16,34,0.7)'; g.fillRect(22, 4, 74, 22);
    g.fillStyle = 'rgba(255,233,168,0.5)'; g.fillRect(22, 4, 74, 1); g.fillRect(22, 25, 74, 1);
    F12.draw(g, '← 返回', 30, 8, '#c8c4d8');
  }

  function drawRow(g, d, i, y) {
    const F16 = F16(), F12 = F12();
    const got = A().at(d.id) > 0, sel = i === page.sel;
    if (sel) { g.fillStyle = SEL; g.fillRect(22, y + 1, 600, ROW_H - 3); g.fillStyle = GOLD; g.fillRect(22, y + 1, 3, ROW_H - 3); }
    icon(g, d, 32, y + 3, got);
    const nameCol = got ? '#fff4d6' : 'rgba(200,196,216,0.55)';
    const name = !got && d.hidden ? '？？？' : d.name;
    const desc = !got && d.hidden && d.hint ? d.hint : d.desc;
    F16.draw(g, fit(F16, name, 300), 68, y + 2, nameCol, { outline: '#140c18' });
    F12.draw(g, fit(F12, desc || '', 296), 68, y + 19, got ? '#c8c4d8' : 'rgba(160,155,180,0.7)');
    // 右边：等级 / 进度 / 日期
    const tierS = TIER_NAME[d.tier] || '';
    const tc = tierColor(d.tier);
    F12.draw(g, tierS, 566, y + 6, got ? tc : 'rgba(150,146,170,0.6)', { align: 'right', outline: '#140c18' });
    if (got) F12.draw(g, '★ ' + fmtDate(A().dateOf(d.id)), 620, y + 6, '#9ad88a', { align: 'right' });
    else if (d.goal > 0) {
      const n = Math.min(d.goal, curProgress(d));
      F12.draw(g, '进度 ' + n + ' / ' + d.goal, 620, y + 20, 'rgba(200,196,216,0.75)', { align: 'right' });
      const bw = 110, bx = 620 - bw - 4;
      g.fillStyle = 'rgba(255,255,255,0.12)'; g.fillRect(bx, y + 24, bw, 3);
      g.fillStyle = tc; g.fillRect(bx, y + 24, Math.round(bw * clamp01(n / d.goal)), 3);
    } else F12.draw(g, '未解锁', 620, y + 20, 'rgba(150,146,170,0.6)', { align: 'right' });
  }

  // 有 goal 的成就现在到哪一步了：按成就自己的计数键取（没有计数的就按存档里数出来的值）
  function curProgress(d) {
    const a = A();
    switch (d.id) {
      case 'foes_5': case 'foes_15': return a.count('foes') || wonCount_();
      case 'rank_s_10': return a.count('rank_s');
      case 'special_10': return a.count('special');
      case 'sptw_30': return a.count('sptw');
      case 'souv_10': return a.count('souv') || souvCount_();
      case 'look_30': return a.count('investigate');
      case 'swap_50': return a.count('swap');
      case 'leaders_6': return a.set ? a.set('leaders').length : 0;     // 这条记的是集合不是计数
      case 'trial_fail_10': return a.count('trial_over');
      default: return 0;
    }
  }
  const wonCount_ = () => (G.EXTRA && G.EXTRA.state ? +(G.EXTRA.state().won || 0) : 0);
  const souvCount_ = () => (G.EXTRA && G.EXTRA.state ? (G.EXTRA.state().souv || []).length : 0);

  // 世界层保持黑底（成就页是菜单类页面，不需要地图）
  const achScene = {
    name: 'achievements', frozen: false,
    enter() { page.t = 0; },
    // 被别的场景顶掉（不是从返回键走的）：resolve 掉这一次进入，调用方不会永远挂着
    leave() { close(true); },
    update(dt) { update(dt); },
    drawWorld(wg) { wg.fillStyle = '#08060f'; wg.fillRect(0, 0, G.W, G.H); },
    drawUI(g) { drawUI(g); },
  };

  G.uiAch = {
    achScene,
    openPage,
    drawToast,
    icon,
    TIER_COL, TIER_DARK,
    // 调试 / 自动测试读：当前页签、选中行、一屏几条
    state() { return { open: !!page.task && G.scene === achScene, tab: TABS[page.tab][0], sel: page.sel, top: page.top, n: listOf().length }; },
  };
})();
