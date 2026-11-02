// 第四部各章共用的零件：替身调查（仗助的“修”、白衣承太郎的“看”）、UI 叠加层、仗助发型记录、日历地图、超市清单、
//   手套图标、教学自动示范的按键、追本体时的水痕指路。写法照第三部 story/common.js；第三部的 G.TPL 照用。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const clk = () => (G.clk ? G.clk : { ui: 0, world: 0 });
  const UW = 640, UH = 360;
  const P4 = (G.P4 = {});

  // ================================================================ UI 叠加层
  //   画在 HUD 之后、对话框之前（挂在 G.hud.drawMarks 后面：引擎不用改）。换章 / 回标题时 main.js 调 P4.clearOverlays()；
  //   每个叠加层记着开它时的 runId，回了标题自己失效（剧情被取消时没人来关它）
  P4.layers = [];
  P4.overlay = (fn, o = {}) => {
    const h = { fn, t0: clk().ui, run: G.runId, dead: false, z: o.z || 0, close() { this.dead = true; } };
    P4.layers.push(h);
    P4.layers.sort((a, b) => a.z - b.z);
    return h;
  };
  P4.clearOverlays = () => { P4.layers.length = 0; };
  const oldMarks = G.hud.drawMarks;
  G.hud.drawMarks = function (g) {
    if (oldMarks) oldMarks.call(this, g);
    if (!P4.layers.length) return;
    P4.layers = P4.layers.filter((h) => !h.dead && h.run === G.runId);
    for (const h of P4.layers) {
      try { h.fn(g, clk().ui - h.t0); } catch (e) { console.error(e); h.dead = true; }
    }
  };
  const img = (key) => { const im = key ? G.image(key) : null; return im && G.ready(im) ? im : null; };
  const ui = () => (G.D && G.D.ui) || {};
  const ease = (u) => 1 - Math.pow(1 - Math.max(0, Math.min(1, u)), 3);
  const text = (g, s, x, y, col = '#fff4d6', size = 12, align = 'left', outline = '#130b20') =>
    G['f' + size].draw(g, s, x, y, col, { align, outline });
  P4.text = text;

  // ================================================================ 修复的金光（疯狂钻石“一抹”）
  P4.fixGlow = (S, x, y, o = {}) => {
    S.sfx('sparkle', o.vol == null ? 0.8 : o.vol);
    S.fx('sparkles', { x, y, n: o.n || 7, radius: o.r || 12, colour: '#ffe9a8', period: 0.5, size: 3 }, { life: o.life || 0.9 });
    S.fx('glint', { x, y, size: o.size || 8 }, { life: 0.4 });
  };

  // ================================================================ 替身调查（自由走动按 U）
  const spot = (h) => (h ? { x: h.lx != null ? h.lx : h.x, y: h.ly != null ? h.ly : h.y } : null);
  // 仗助：疯狂钻石伸手一抹（tags 'fix'）。修的结果由调查点自己的 look 演；对着好好的东西按 U：「……这个本来就是好的。」
  G.LOOK.josuke = {
    tags: ['fix'], cd: 1, miss: '……这个本来就是好的。',
    run: async (S, p, h) => {
      const at = spot(h);
      if (at) S.face(p, at.x > p.x ? 1 : at.x < p.x ? -1 : p.facing);
      await S.summon(p, { dur: 0.14, rise: 4 });
      S.standAct(p, 'reach', { dx: 18, z: 4, dur: 0.7 });
      if (h) {
        const gy = h.fy != null ? h.fy : h.y - (h.fz || 14);
        P4.fixGlow(S, h.fx != null ? h.fx : h.x, gy);
        await S.wait(0.45);
      } else await S.wait(0.25);
    },
  };
  // 白衣承太郎：白金之星的眼睛（tags 'detail'），和第三部承太郎一样：眼部条带 → 推镜到调查点
  G.LOOK.jotaro4 = {
    tags: ['detail', 'grab'], cd: 1, miss: '……没什么特别的。',
    run: async (S, p, h) => {
      S.sfx('glint', 0.7);
      await S.eyeStrip('jotaro4', { dur: 0.4 });
      if (h) {
        const at = spot(h);
        await S.zoom(2.5, at.x, at.y, 0.22);
        S.fx('glint', { x: at.x, y: at.y, size: 7 }, { tag: 'look' });
        await S.wait(1.0);
        await S.zoom(1, null, null, 0.2);
      }
    },
  };

  // ================================================================ 仗助发型记录（开发脚本 §4）
  //   剧情里有人说仗助的头发 → 画面定格 0.4 s → 金色小牌从上面滑进来「东方仗助 发型记录 第 N 次」+ 盖章音，停 1.2 s。
  //   存档只记“第几次已经发生过”（数字列表）：同一条重玩不会再记一次（“读档以后不重复记”）
  const HAIR_ROWS = {
    1: { who: '不良学长', where: '上学路', said: '过时的鸡冠头', result: '鼻子修好了，脸更歪了' },
    2: { who: '空条承太郎', where: '葡萄丘高中校门', said: '“找起来倒是方便”（误会）', result: '被时停躲开' },
    3: { who: '超市劫匪', where: '超市', said: '怪头', result: '刀柄修进了额头' },
  };
  P4.hair = {
    ROWS: HAIR_ROWS,
    list() {
      const v = G.store.get('p4-hair', []);
      return Array.isArray(v) ? v.filter((n) => HAIR_ROWS[n]).sort((a, b) => a - b) : [];
    },
    add(n) {
      const l = this.list();
      if (l.indexOf(n) < 0) { l.push(n); l.sort((a, b) => a - b); G.store.set('p4-hair', l); }
      if (G.dbg && G.dbg.ev) G.dbg.ev('hair_record', { n, total: l.length });
    },
    // 暂停菜单的那一页（main.js 调）：一次一行
    pageText() {
      const l = this.list();
      if (!l.length) return '还没有记录。\n（谁敢说仗助的头发，这里就记一笔。）';
      return l.map((n) => { const r = HAIR_ROWS[n]; return '第' + n + '次　' + r.who + '（' + r.where + '）\n　说：' + r.said + '\n　下场：' + r.result; }).join('\n');
    },
    async show(S, n) {
      S.hint(null);
      G.hitStopAll(0.4);
      S.sfx('freeze', 0.5);
      await S.wait(0.4, 'ui');
      const meta = ui().hair || {};
      let stamped = -1;
      const h = P4.overlay((g, t) => drawHair(g, t, n, meta, h), { z: 5 });
      h.end = Infinity;
      S.sfx('whoosh', 0.6);
      await S.wait(0.3, 'ui');
      S.sfx('thud', 0.9); S.sfx('card_flip', 0.7); S.shake(1.5, 0.15);
      stamped = clk().ui;
      void stamped;
      await S.wait(1.2, 'ui');
      h.end = clk().ui - h.t0;
      await S.wait(0.2, 'ui');
      h.close();
      this.add(n);
    },
  };
  function drawHair(g, t, n, meta, h) {
    const pm = meta.plate, pim = pm && img(pm.image);
    const w = pm ? pm.w : 228, hh = pm ? pm.h : 44;
    const x = Math.round(UW / 2 - w / 2), y = Math.round(-hh - 6 + (hh + 6 + 30) * ease(t / 0.22));
    const a = t > h.end ? Math.max(0, 1 - (t - h.end) / 0.2) : 1;
    g.save();
    g.globalAlpha = a;
    if (pim) g.drawImage(pim, x, y);
    else { G.ui.box(g, x, y, x + w, y + hh); text(g, '东方仗助 发型记录 第' + n + '次', x + w / 2, y + 14, '#ffe070', 16, 'center'); }
    // 数字：0.3 s 时从 1.8 倍砸进小牌的空格里（盖章）
    const slot = (pm && pm.slot) || [170, 4, 27, 36];
    const dm = (meta.digits || [])[n];
    const dim = dm && img(dm.image);
    if (dim && t >= 0.3) {
      const u = Math.min(1, (t - 0.3) / 0.12), sc = 1.8 - 0.8 * ease(u);
      const cx = x + slot[0] + slot[2] / 2, cy = y + slot[1] + slot[3] / 2;
      const dw = Math.round(dm.w * sc), dh = Math.round(dm.h * sc);
      g.globalAlpha = a * Math.min(1, u * 3);
      g.drawImage(dim, Math.round(cx - dw / 2), Math.round(cy - dh / 2), dw, dh);
      if (t < 0.5) { g.globalAlpha = a * (1 - (t - 0.3) / 0.2); g.fillStyle = '#fff'; g.fillRect(x + slot[0] - 2, y + slot[1] - 2, slot[2] + 4, slot[3] + 4); }
    }
    g.restore();
  }

  // ================================================================ 日历地图（开发脚本 §4）
  //   320×180 俯视杜王町；这一章的图钉一枚枚落下来，盖红章（年月），右上小字写地点。以后的章节往 CAL 里加一行，
  //   去过的地方留灰色图钉（gray: 前面各章的图钉）
  const CAL = {
    prologue: { pins: [{ at: 'school', label: '葡萄丘高中' }, { at: 'home', label: '东方家' }], stamp: 'stamp' },
  };
  P4.CAL = CAL;
  P4.calendar = async (S, key, o = {}) => {
    const c = CAL[key];
    if (!c) return;
    const an = (G.D && G.D.bg && G.D.bg.morioh_map && G.D.bg.morioh_map.anchors) || {};
    const keys = Object.keys(CAL), gray = [];
    for (const k of keys) { if (k === key) break; for (const p of CAL[k].pins) gray.push(p); }
    const m = ui().map || {};
    const pins = c.pins.map((p, i) => ({ p, xy: an[p.at] || [160, 90], t0: 0.5 + i * 0.45 }));
    const stampAt = 0.5 + pins.length * 0.45 + 0.25;
    const h = P4.overlay((g, t) => {
      const pin = (xy, im, dy = 0) => {
        if (!im) return;
        const meta = m.pin || { ax: 5, ay: 15 };
        g.drawImage(im, Math.round(xy[0] * 2 - meta.ax * 2), Math.round(xy[1] * 2 - meta.ay * 2 + dy), im.width * 2, im.height * 2);
      };
      for (const q of gray) pin(an[q.at] || [160, 90], img(m.pin_gray && m.pin_gray.image));
      for (const q of pins) {
        const u = (t - q.t0) / 0.3;
        if (u < 0) continue;
        // 从上面掉下来，落地弹一下
        const dy = u < 1 ? -60 * (1 - ease(u)) : u < 1.4 ? -Math.round(Math.sin((u - 1) / 0.4 * Math.PI) * 6) : 0;
        pin(q.xy, img(m.pin && m.pin.image), dy);
        if (u >= 1) text(g, q.p.label, Math.round(q.xy[0] * 2 + 12), Math.round(q.xy[1] * 2 - 34), '#fff4d6', 12, 'left', '#2a0a1a');
      }
      if (t >= stampAt) {
        const sm = m.stamp, sim = sm && img(sm.image);
        if (sim) {
          const u = Math.min(1, (t - stampAt) / 0.14), sc = 1.9 - 0.9 * ease(u);
          const w = Math.round(sm.w * sc), hh = Math.round(sm.h * sc), cx = 534, cy = 262;
          g.save(); g.globalAlpha = Math.min(1, u * 2);
          g.drawImage(sim, Math.round(cx - w / 2), Math.round(cy - hh / 2), w, hh);
          g.restore();
        }
      }
      const pl = m.place, plim = pl && img(pl.image);
      if (plim) g.drawImage(plim, UW - pl.w - 14, 12);
    }, { z: 1 });
    for (const q of pins) G.defer(q.t0 + 0.3, () => { S.sfx('pop', 0.7); S.sfx('thud', 0.4); }, 'ui');
    G.defer(stampAt, () => { S.sfx('thud', 1); S.sfx('card_flip', 0.6); S.shake(2, 0.2); }, 'ui');
    await S.wait(stampAt + (o.hold || 1.6), 'ui');
    return h;
  };

  // ================================================================ 超市清单（节拍 9，画面右上）
  P4.shopList = (items) => {
    const st = { items: items.map((s) => ({ name: s, done: false })), extra: null };
    st.check = (name) => { const it = st.items.find((i) => i.name === name); if (it && !it.done) { it.done = true; return true; } return false; };
    st.all = () => st.items.every((i) => i.done);
    st.h = P4.overlay((g) => {
      const W = G.world;
      if (!W || W.insert || (G.S && G.S.cardOn)) return;
      const rows = st.items.length + (st.extra ? 1 : 0);
      const x0 = 492, y0 = 10, x1 = 630, y1 = y0 + 28 + rows * 18;
      G.ui.box(g, x0, y0, x1, y1, { fill: 'rgba(250,244,226,0.94)' });
      text(g, '妈妈的清单', x0 + 10, y0 + 7, '#5a3a20', 12, 'left', null);
      const list = st.items.slice();
      if (st.extra) list.push({ name: st.extra, done: true, extra: true });
      list.forEach((it, i) => {
        const y = y0 + 26 + i * 18;
        g.fillStyle = '#5a3a20'; g.fillRect(x0 + 10, y + 1, 10, 10);
        g.fillStyle = '#faf4e2'; g.fillRect(x0 + 11, y + 2, 8, 8);
        if (it.done) { g.fillStyle = it.extra ? '#c04030' : '#2a8a3a'; for (let k = 0; k < 4; k++) { g.fillRect(x0 + 11 + k, y + 5 + k, 2, 2); } for (let k = 0; k < 6; k++) g.fillRect(x0 + 14 + k, y + 7 - k, 2, 2); }
        text(g, it.name, x0 + 26, y, it.extra ? '#c04030' : '#3a2a1a', 12, 'left', null);
      });
    });
    return st;
  };

  // ================================================================ 手套图标（序2：拿了乳胶手套以后，队长面板右边）
  P4.gloveIcon = () => P4.overlay((g) => {
    if (!(G.hud && G.hud.on)) return;
    const pm = G.D && G.D.props && G.D.props.glove_icon;
    if (!pm) return;
    G.ui.sheet(g, pm, 0, 274, 56, 2, { anchor: 'tl' });
    text(g, '手套', 278 + pm.size[0], 60, '#ffe9a8', 12, 'left');
  });

  // ================================================================ 教学的自动示范：按键帽在仗助头顶闪（“显示按键”）
  P4.keyDemo = (getActor) => {
    const st = { label: null, on: 0, note: '自动示范' };
    st.h = P4.overlay((g, t) => {
      const a = getActor();
      if (!st.label || !a || !G.cam || !G.cam.w2u) return;
      const p = G.cam.w2u(a.x, a.headY() - 10, 0);
      const s = 28, x = Math.round(p.x - s / 2), y = Math.round(Math.max(30, p.y - 44));
      G.ui.keyCap(g, x, y, st.label, clk().ui < st.on, s);
      text(g, st.note, x + s / 2, y - 16, '#ffe9a8', 12, 'center');
      void t;
    }, { z: 3 });
    st.press = (label, dur = 0.18) => { st.label = label; st.on = clk().ui + dur; };
    return st;
  };

  // ================================================================ 水痕指路（序2 段 2：手套里的项链往本体那边挣）
  //   本体在画面外：屏幕那一边出一串往外流的水滴 + 箭头；在画面里：本体头顶一滴水上下跳
  P4.waterTrail = (getTarget) => P4.overlay((g, t) => {
    const a = getTarget();
    if (!a || a.remove || !G.cam || !G.cam.w2u || (G.world && G.world.cine)) return;
    const p = G.cam.w2u(a.x, a.y - 30, 0);
    const right = p.x > UW - 8, left = p.x < 8;
    g.save();
    if (right || left) {
      const dir = right ? 1 : -1, ex = right ? UW - 18 : 18, y = Math.round(G.clamp(p.y, 60, 300));
      for (let i = 0; i < 6; i++) {
        const u = ((t * 1.6 + i / 6) % 1), x = Math.round(ex - dir * (90 - u * 90));
        g.globalAlpha = 0.35 + 0.65 * u;
        g.fillStyle = '#7ad0ff'; g.fillRect(x - 2, y - 1 + (i % 2) * 2, 5, 3); g.fillStyle = '#e0f6ff'; g.fillRect(x - 1, y - 1 + (i % 2) * 2, 2, 1);
      }
      g.globalAlpha = 1;
      g.fillStyle = '#7ad0ff';
      for (let k = 0; k < 7; k++) g.fillRect(ex + dir * (k - 6), y - k, 2, k * 2 + 1);
      text(g, '本体', ex - dir * 16, y - 26, '#bfe8ff', 12, 'center', '#0a2238');
    } else {
      const bob = Math.round(Math.abs(Math.sin(t * 5)) * 4);
      g.fillStyle = '#7ad0ff';
      const x = Math.round(p.x), y = Math.round(p.y - 26 - bob);
      g.fillRect(x - 1, y - 6, 3, 3); g.fillRect(x - 2, y - 3, 5, 4); g.fillRect(x - 1, y + 1, 3, 1);
    }
    g.restore();
  });
})();
