// 游戏内 UI（UI 层 640×360，版式照原工程 text.py）：对话 / 选项 / 旁白 / 提示 / 系统框 / 菜单 / 7 种 QTE / 插入层 / 黑边（技术约定 §4.10.1）
'use strict';
(function () {
  const G = window.G;
  const task = G.runPromise || (f => new Promise(f));
  const UW = 640, UH = 360;
  const CPS = 18;              // 对话打字速度（字 / 秒）
  const NARR_CPS = 14.4;       // 旁白打字速度
  const POP = 0.12;            // 对话框弹出 / 推进延迟
  const BOX_X0 = 20, BOX_X1 = 620, BOX_H = 80, BOX_Y_BOTTOM = 272, BOX_Y_TOP = 12;
  const SEL = 'rgba(255,211,74,0.18)';
  const GOLD = '#ffd34a';

  // ---------------------------------------------------------------- 小工具
  // 和 源码\engine\core.py ease() 同一套公式（本地一份，免得依赖别人的别名）
  function ez(u, k = 'io') {
    u = u < 0 ? 0 : u > 1 ? 1 : u;
    switch (k) {
      case 'linear': return u;
      case 'in': return u * u;
      case 'out': return 1 - (1 - u) * (1 - u);
      case 'in3': return u * u * u;
      case 'out3': return 1 - (1 - u) * (1 - u) * (1 - u);
      case 'back': { const s = 1.70158, v = u - 1; return v * v * ((s + 1) * v + s) + 1; }
      case 'step': return u >= 1 ? 1 : 0;
      default: return u * u * (3 - 2 * u);
    }
  }
  const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
  const f16 = () => { if (!G.f16 && G.initFonts) G.initFonts(); return G.f16; };
  const f12 = () => { if (!G.f12 && G.initFonts) G.initFonts(); return G.f12; };
  const snd = (name, o) => (name && G.audio && G.audio.sfx ? G.audio.sfx(name, o) : null);
  const tsafe = () => { const T = G.touch; return T && T.on && T.safe ? T.safe : null; };
  const W = () => G.world || null;
  const BAY = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map((v) => v / 16 + 1 / 32);

  function nameOf(who) {
    if (!who) return '';
    const D = G.D || {};
    if (G.NAMES && G.NAMES[who]) return G.NAMES[who];
    if (D.heroes && D.heroes[who]) return D.heroes[who].short || D.heroes[who].cn;
    if (D.speakers && D.speakers[who]) return D.speakers[who].short;
    if (D.chars && D.chars[who]) return D.chars[who].name;
    return String(who);
  }
  function colorOf(who) {
    const D = G.D || {};
    if (who && D.heroes && D.heroes[who] && D.heroes[who].nameColor) return D.heroes[who].nameColor;
    if (who && D.speakers && D.speakers[who] && D.speakers[who].nameColor) return D.speakers[who].nameColor;
    return '#555566';
  }
  // 头像：G.head 返回 [第 0 帧, 第 1 帧?]；尺寸优先 G.headSize（非 32×32 的场景头像按它排版）
  function headOf(cid, expr) {
    if (!cid || !G.head || !(G.D && G.D.chars && G.D.chars[cid])) return null;
    const h = G.head(cid, expr || 'normal');
    if (!h) return null;
    const arr = Array.isArray(h) ? h.filter(Boolean) : [h];
    if (!arr.length) return null;
    let sz = G.headSize ? G.headSize(cid, expr || 'normal') : null;
    if (!sz) { const im = arr[0]; sz = [im.naturalWidth || im.width || 32, im.naturalHeight || im.height || 32]; }
    return { imgs: arr, w: sz[0], h: sz[1] };
  }

  // 道具 / 场景专用图的帧（横向帧条），按 pivot 画到 (x, y)；meta 可以是 GAME_DATA.props / scene 里的条目
  function sheet(g, meta, frame, x, y, scale = 1, o = {}) {
    if (typeof meta === 'string') {
      const D = G.D || {};
      meta = meta.startsWith('scene:') ? (D.scene || {})[meta.slice(6)] : (D.props || {})[meta.replace(/^prop:/, '')];
    }
    if (!meta) return false;
    const im = G.image(meta.image);
    if (!G.ready(im)) return false;
    const [w, h] = meta.size || [im.naturalWidth, im.naturalHeight];
    const n = meta.frames || 1;
    const f = Math.max(0, Math.min(n - 1, frame | 0));
    const pv = o.anchor === 'tl' ? [0, 0] : (meta.pivot || [w / 2, h]);
    const flip = !!o.flip;
    const dx = Math.round(x - (flip ? w - pv[0] : pv[0]) * scale), dy = Math.round(y - pv[1] * scale);
    g.save();
    g.imageSmoothingEnabled = false;
    if (o.alpha != null) g.globalAlpha *= o.alpha;
    if (flip) { g.translate(dx + w * scale, dy); g.scale(-1, 1); g.drawImage(im, f * w, 0, w, h, 0, 0, w * scale, h * scale); }
    else g.drawImage(im, f * w, 0, w, h, dx, dy, w * scale, h * scale);
    g.restore();
    return true;
  }

  // 边缘泛红（抖动），拔肉芽钻入时用；17 档缓存，320×180 画好后 ×2 贴到 UI 层
  const edgeCache = [];
  function redEdge(g, alpha, color = [90, 0, 16]) {
    const q = Math.round(clamp01(alpha) * 16);
    if (q <= 0) return;
    let c = edgeCache[q];
    if (!c) {
      c = G.mkCanvas(320, 180);
      const id = c.g.createImageData(320, 180);
      const a = q / 16;
      for (let y = 0; y < 180; y++) {
        for (let x = 0; x < 320; x++) {
          const dx = (x - 159.5) / 160, dy = (y - 89.5) / 90;
          const d = Math.sqrt(dx * dx + dy * dy);
          const v = clamp01((d - 0.45) / 0.6) * a * 1.4;
          if (BAY[((y & 3) << 2) | (x & 3)] < v) {
            const i = (y * 320 + x) * 4;
            id.data[i] = color[0]; id.data[i + 1] = color[1]; id.data[i + 2] = color[2]; id.data[i + 3] = 255;
          }
        }
      }
      c.g.putImageData(id, 0, 0);
      edgeCache[q] = c;
    }
    g.save();
    g.imageSmoothingEnabled = false;
    g.drawImage(c, 0, 0, 320, 180, 0, 0, UW, UH);
    g.restore();
  }

  // 键帽小图标（QTE 提示）：圆角方块 + 字母
  function keyCap(g, x, y, label, on = false, size = 24) {
    const s = size;
    g.fillStyle = '#0c0a14'; g.fillRect(x - 1, y + 1, s + 2, s + 2);
    g.fillStyle = on ? '#ffe9a8' : '#e8e0f0'; g.fillRect(x, y, s, s - (on ? 0 : 2));
    g.fillStyle = on ? '#c89a20' : '#8a84a0'; g.fillRect(x, y + s - (on ? 2 : 4), s, 2);
    g.fillStyle = '#0c0a14';
    g.fillRect(x, y, 1, 1); g.fillRect(x + s - 1, y, 1, 1);
    const F = f16();
    F.draw(g, label, x + s / 2, y + (on ? 4 : 3), '#1a1020', { align: 'center' });
  }
  const KEYCAP = { attack: 'J', dodge: 'K', guard: 'L', special: 'U', ok: 'E' };

  // ---------------------------------------------------------------- QTE 默认参数（技术约定 §4.10.1）
  const QDEF = {
    mash: { label: '连按 J！', need: 8, time: 2, decay: 0 },
    timing: { label: '看准时机按 J！', speed: 1.1, zone: [0.42, 0.58], tries: 1, limit: null },
    rhythm: { label: '跟着节奏按 J！', notes: [], window: 0.16, travel: 1.6, pass: 0.6 },
    clash: { label: '连按 J！欧拉欧拉！', time: 4, push: 0.06, rate: 0.2, start: 0.5, colours: ['#b090ff', '#ffd040'] },
    press: { key: 'guard', window: 0.5, label: null, failOk: true, perfect: null },
    pluck: {
      label: '方向键对准，按住 J 拔！', speed: 60, r: 6, pullSec: 3, drillSec: 1.5, wobble: [2, 10], wobbleHz: 1.5, noise: 2,
      jump: { after: 0.5, every: 40 / 60, px: 8 }, finalMash: { need: 8, time: 1.4, decay: 0, label: '拔出来！' },
      bud: [160, 70], start: [196, 128],
    },
    aim: { label: '按住方向键稳住！', time: 6, need: 3, r: 10, drift: 18, jitter: 1 },
  };
  const PRESS_LABEL = { guard: 'L！', dodge: 'K！', attack: 'J！', special: 'U！' };

  // 注意：技术约定 §4.10.1 的字段表里同时有状态 notice 和方法 notice(o)，一个名字放不下两样——
  // 方法保留 G.ui.notice(o)（S.notice 转调它），状态放 G.ui.noticeBox；快照请用 G.ui.state()（下面）
  const ui = (G.ui = {
    dlg: null, choiceBox: null, narr: null, narrOut: null, hints: [], menu: null, noticeBox: null, qte: null,
    insertUI: null, letterbox: 0, letterboxTarget: 0,
    clashFails: {},           // clash 的 o.id → 失败次数（第 2 次起 push ×1.3）

    reset() {
      this.dlg = null; this.choiceBox = null; this.narr = null; this.narrOut = null; this.hints = []; this.menu = null;
      this.noticeBox = null; this.insertUI = null; this.letterbox = 0; this.letterboxTarget = 0;
      if (this.qte) this.endQteCleanup(this.qte);
      this.qte = null;
      if (G.uifx && G.uifx.clear) G.uifx.clear();
      if (G.hud && G.hud.reset) G.hud.reset();
    },
    blocking() {
      return !!(this.dlg || this.choiceBox || this.narr || this.menu || this.noticeBox || this.qte ||
        (G.uifx && G.uifx.chapter));
    },
    // 给 G.dbg.snapshot()（包 8）用的 UI 部分：字段名照技术约定 §6.2
    state() {
      const d = this.dlg, q = this.qte, n = this.narr;
      return {
        dlg: d ? d.text : null, dwho: d ? d.who : null, ddone: d ? d.shown >= d.pageLen[d.page] : false,
        dpage: d ? d.page : -1, dlen: d ? d.pages.length : 0,
        narr: n ? n.lines.join('') : null, nauto: n ? (n.auto || 0) : 0,
        choice: this.choiceBox ? this.choiceBox.options.slice() : null,
        notice: this.noticeBox ? [this.noticeBox.title || '', this.noticeBox.text || ''].join('') : null,
        menu: this.menu ? (this.menu.title || '') : null,
        menuItems: this.menu ? this.menu.options.map(String) : null,
        chapter: !!(G.uifx && G.uifx.chapter),
        qte: q ? {
          type: q.type, state: q.state, t: q.t, result: q.result, m: q.m, v: q.v, zone: q.zone || null,
          notes: q.notes || null, key: q.key || null, pull: q.pull || 0, drill: q.drill || 0,
          phase: q.phase || null, hold: !!q.hold,
        } : null,
        hint: this.hints.length ? this.hints[0].text : null,
      };
    },
    sheet, keyCap,

    // ============================================================ 对话
    say(who, text, o = {}) {
      return task((res) => {
        if (this.dlg && this.dlg.res) { const r = this.dlg.res; this.dlg = null; r(); }
        const d = this.makeDlg(who, text == null ? '' : String(text), o);
        d.res = res;
        this.dlg = d;
        if (o.sfx) snd(o.sfx);
      });
    },
    makeDlg(who, text, o) {
      const F = f16();
      const name = o.name != null ? o.name : nameOf(who);
      const color = o.color || colorOf(who);
      const pos = o.pos === 'top' ? 'top' : 'bottom';
      const y0 = pos === 'top' ? BOX_Y_TOP : BOX_Y_BOTTOM;
      let pcid = null;
      if (o.portrait === false || !who) pcid = null;
      else if (typeof o.portrait === 'string') pcid = o.portrait;
      else pcid = who;
      const head = pcid ? headOf(pcid, o.expr) : null;
      const sc = head ? (head.h <= 34 ? 2 : 1) : 1;
      const px = BOX_X0 + 8, py = y0 + 8;
      const tx = head ? px + head.w * sc + 14 : BOX_X0 + 16;
      const lines = F.wrap(text, BOX_X1 - tx - 16);
      const pages = [];
      for (let i = 0; i < lines.length; i += 3) pages.push(lines.slice(i, i + 3));
      if (!pages.length) pages.push(['']);
      return {
        who, text, name, color, expr: o.expr || 'normal', head, sc, px, py, tx, pos, y0, pages,
        pageLen: pages.map((p) => p.join('').length), page: 0, shown: 0, t: 0, pt: 0, actor: o.actor || null,
        voice: who && G.audio && G.audio.voice ? G.audio.voice(who) : 1,
      };
    },

    // ============================================================ 选项
    choice(options, title, o = {}) {
      return task((res) => {
        this.choiceBox = { options: options.map(String), title: title || null, idx: o.idx || 0, res, t: 0 };
        snd('pop', { vol: 0.5 });
      });
    },
    choiceLayout(c) {
      const F = f16();
      const w = Math.max(...c.options.map((s) => F.width(s))) + 44;
      const h = c.options.length * 24 + 12;
      let x = BOX_X1 - w;
      const S = tsafe();
      if (S && S.r) x = Math.min(x, S.r - w - 8);
      const y = this.dlg ? BOX_Y_BOTTOM - h - 10 : UH - h - 20;
      return { x: Math.round(x), y: Math.round(y), w, h };
    },

    // ============================================================ 旁白
    narrate(text, o = {}) {
      return task((res) => {
        const F = f16();
        const onBlack = !!o.onBlack;
        const pos = o.pos || (onBlack ? 'center' : 'top');
        const lines = F.wrap(text == null ? '' : String(text), 560);
        this.narrOut = null;
        this.narr = { lines, total: lines.join('').length, t: 0, shown: 0, res, auto: o.auto || 0, pos, onBlack };
      });
    },

    // ============================================================ 提示 / 系统框 / 菜单
    // hint(null / '') = 清掉提示（剧情里 S.hint(null) 用来收起；以前 String(null) 会显示成“null”）
    hint(text, dur = 4.5) { this.hints = text == null || text === '' ? [] : [{ text: String(text), t: 0, dur }]; },
    notice(o = {}) {
      return task((res) => {
        this.noticeBox = Object.assign({ t: 0, res }, o);
        snd('sparkle', { vol: 0.6 });
      });
    },
    showNotice(o) { return this.notice(o); },     // 银魂旧名
    openMenu(title, options, o = {}) {
      return task((res) => {
        this.menu = Object.assign({ title: title || null, options, idx: o.idx || 0, res, t: 0 }, o);
        this.menu.options = options;
      });
    },
    menuLayout(m) {
      const F = f16();
      const tw = m.title ? F.width(m.title) : 0;
      const iw = Math.max(0, ...m.options.map((s) => F.width(String(s))));
      const w = Math.max(tw, iw + 40) + 60;
      const h = (m.title ? 46 : 16) + m.options.length * 26 + (m.note ? 24 : 0) + 12;
      const x = Math.round((UW - w) / 2), y = Math.round(Math.max(4, Math.min(UH - h - 4, m.y == null ? (UH - h) / 2 : m.y)));
      return { x, y, w, h, oy: y + (m.title ? 46 : 16) };
    },

    // ============================================================ QTE
    startQte(o = {}) {
      return task((res) => {
        if (this.qte) this.finishQte(this.qte, true);
        const type = QDEF[o.type] ? o.type : 'mash';
        const q = Object.assign({}, QDEF[type], o, { type });
        if (type === 'pluck') {
          q.jump = Object.assign({}, QDEF.pluck.jump, o.jump || {});
          q.finalMash = Object.assign({}, QDEF.pluck.finalMash, o.finalMash || {});
          q.wobble = (o.wobble || QDEF.pluck.wobble).slice();
        }
        Object.assign(q, { t: 0, res, result: null, endT: 0, state: 'run', m: 0, v: 0, presses: 0, holdAcc: 0, judged: [], misses: 0, flash: 0, pull: 0, drill: 0 });
        if (type === 'clash') {
          q.v = q.start;
          if (q.id && (this.clashFails[q.id] || 0) >= 1) q.push *= 1.3;
        } else if (type === 'rhythm') {
          q.state = 'run'; q.notesState = q.notes.map(() => 0);
        } else if (type === 'press') {
          q.label = q.label || PRESS_LABEL[q.key] || '按键！';
          const p = q.perfect || 0;
          q.nowT = q.at != null ? q.at : Math.max(p, q.window - p);
          q.deadline = Math.max(q.window, q.nowT + p);
        } else if (type === 'pluck') {
          q.aim = { x: q.start[0], y: q.start[1] };
          q.budPos = { x: q.bud[0], y: q.bud[1] };
          q.jumpOff = { x: 0, y: 0 }; q.nextJump = 0; q.relaxed = false; q.wobbleK = 1; q.phase = 'pull'; q.resets = 0;
          q.m = [q.aim.x - q.budPos.x, q.aim.y - q.budPos.y];
          q.fm = null;
          const Wd = W();
          if (Wd) {
            q.prevInsert = Wd.insert || null;
            Wd.insert = { draw: (wg, t) => this.drawPluckWorld(wg, q, t), t0: G.clk.ui, clock: 'ui', qte: true };
          }
        } else if (type === 'aim') {
          q.p = { x: q.start ? q.start[0] : 0, y: q.start ? q.start[1] : 0 }; q.acc = 0; q.m = [q.p.x, q.p.y]; q.dir = Math.random() * Math.PI * 2;
        }
        const Wd = W();
        if (Wd && Wd.combat && !Wd.cine) { Wd.cine = { by: 'qte' }; q.cineSet = true; }
        this.qte = q;
        if (G.dbg && G.dbg.ev) G.dbg.ev('qte_start', { type });
      });
    },
    // 结束：显示结果后由 updateQte 调；force = 被新的 QTE 顶掉
    finishQte(q, force) {
      this.endQteCleanup(q);
      if (this.qte === q) this.qte = null;
      const I = G.input;
      if (I) { if (I.lockOk) I.lockOk(0.6); if (I.consumeOk) I.consumeOk(); }
      const out = q.result == null ? (q.type === 'press' ? 'miss' : false) : q.result;
      if (G.dbg && G.dbg.ev) G.dbg.ev('qte', { type: q.type, result: out });
      const Wd = W();
      if (Wd && Wd.fight && Wd.fight.emit) Wd.fight.emit('qte', { type: q.type, result: out });
      if (!force || q.res) q.res(out);
    },
    endQteCleanup(q) {
      const Wd = W();
      if (!Wd) return;
      if (q.cineSet && Wd.cine && Wd.cine.by === 'qte') Wd.cine = null;
      q.cineSet = false;
      if (q.type === 'pluck' && Wd.insert && Wd.insert.qte) Wd.insert = q.prevInsert || null;
    },
    qteOk(q) {
      if (q.type === 'press') return q.result === 'perfect' || q.result === 'ok';
      if (q.result && typeof q.result === 'object') return q.result.hits >= q.result.total * (q.pass || 0.6);
      return q.result === true;
    },
    // 连按输入：J / Enter / 点屏（mashHit）；设置「连打 QTE 改成按住 J」时按住 J = 每秒 6 次
    mashPresses(q, dt) {
      const I = G.input;
      let n = 0;
      if (I.mashHit && I.mashHit()) { n++; if (I.consume) I.consume('attack'); if (I.consumeOk) I.consumeOk(); }
      if (G.settings && G.settings.mashHold && I.isDown && I.isDown('attack')) {
        q.holdAcc += dt * 6;
        while (q.holdAcc >= 1) { q.holdAcc -= 1; n++; }
      } else q.holdAcc = 0;
      return n;
    },

    // ============================================================ 每帧
    update(dt) {
      const I = G.input;
      this.letterbox += (this.letterboxTarget - this.letterbox) * Math.min(1, dt * 6);
      if (this.insertUI && this.insertUI.t0 == null) this.insertUI.t0 = G.clk.ui;
      for (const h of this.hints) h.t += dt;
      this.hints = this.hints.filter((h) => h.t < h.dur);
      if (this.narrOut) { this.narrOut.out += dt; if (this.narrOut.out >= 0.25) this.narrOut = null; }
      if (G.uifx && G.uifx.update) G.uifx.update(dt);
      if (G.hud && G.hud.update) G.hud.update(dt);
      if (!I) return;
      if (this.menu) { this.updateMenu(dt); return; }
      if (G.uifx && G.uifx.chapter) return;
      if (this.noticeBox) {
        const n = this.noticeBox;
        n.t += dt;
        const ready = n.t >= Math.max(0.6, n.minT || 0);
        if (ready && (n.auto || I.okHit())) { I.consumeOk(); const r = n.res; this.noticeBox = null; snd('menu_confirm', { vol: 0.5 }); r(); }
        return;
      }
      if (this.qte && !this.qte.hold) { this.updateQte(dt); return; }
      if (this.choiceBox) { this.updateChoice(dt); return; }
      if (this.dlg) { this.updateDlg(dt); return; }
      if (this.narr) this.updateNarr(dt);
    },
    updateMenu(dt) {
      const I = G.input, m = this.menu;
      m.t += dt;
      const n = m.options.length;
      if (I.tap) {
        const L = this.menuLayout(m), t = I.tap;
        const row = Math.floor((t.y - (L.oy - 4)) / 26);
        const inBox = t.x >= L.x && t.x <= L.x + L.w && t.y >= L.y && t.y <= L.y + L.h;
        if (inBox && row >= 0 && row < n) m.idx = row;
        else {
          I.consume('ok');
          if (!inBox && m.escIndex != null) { this.closeMenu(m.escIndex, 'menu_cancel'); return; }
        }
      }
      if (I.hit('up')) { m.idx = (m.idx + n - 1) % n; snd('menu_move', { vol: 0.5 }); }
      if (I.hit('down')) { m.idx = (m.idx + 1) % n; snd('menu_move', { vol: 0.5 }); }
      if (m.onKey && (I.hit('left') || I.hit('right'))) {
        const dir = I.hit('left') ? -1 : 1;
        if (m.onKey(m.idx, dir, m) !== false) snd('menu_move', { vol: 0.5, rate: dir < 0 ? 0.9 : 1.1 });
      }
      if (I.okHit() && m.t > 0.08) { I.consumeOk(); this.closeMenu(m.idx, 'menu_confirm'); }
      else if ((I.hit('pause') || I.hit('back')) && m.escIndex != null) {
        I.consume('pause'); I.consume('back'); this.closeMenu(m.escIndex, 'menu_cancel');
      }
    },
    closeMenu(i, sound) {
      const m = this.menu;
      this.menu = null;
      snd(sound, { vol: 0.6 });
      m.res(i);
    },
    updateChoice(dt) {
      const I = G.input, c = this.choiceBox;
      c.t += dt;
      const n = c.options.length;
      if (I.tap) {
        const L = this.choiceLayout(c), t = I.tap;
        const row = Math.floor((t.y - (L.y + 6)) / 24);
        if (t.x >= L.x - 4 && t.x <= L.x + L.w + 4 && row >= 0 && row < n) c.idx = row;
        else I.consume('ok');
      }
      if (I.hit('up')) { c.idx = (c.idx + n - 1) % n; snd('menu_move', { vol: 0.5 }); }
      if (I.hit('down')) { c.idx = (c.idx + 1) % n; snd('menu_move', { vol: 0.5 }); }
      if (I.okHit() && c.t > 0.12) { I.consumeOk(); const r = c.res, i = c.idx; this.choiceBox = null; snd('menu_confirm', { vol: 0.6 }); r(i); }
    },
    updateDlg(dt) {
      const I = G.input, d = this.dlg;
      d.t += dt; d.pt += dt;
      const total = d.pageLen[d.page];
      if (d.shown < total) {
        const before = Math.floor(d.shown);
        if (d.t >= POP) d.shown = Math.min(total, d.shown + CPS * dt);
        const now = Math.floor(d.shown);
        if (d.who && now > before) {
          for (let k = before + 1; k <= now; k++) {
            if (k % 2 === 1) snd('blip', { vol: 0.32, rate: d.voice * (0.94 + Math.random() * 0.12) });
          }
        }
        if (I.okHit() && d.t > POP) { I.consumeOk(); d.shown = total; }
      } else if (I.okHit() && d.t > POP && d.pt > 0.08) {
        I.consumeOk();
        if (d.page < d.pages.length - 1) { d.page++; d.shown = 0; d.pt = 0; }
        else { const r = d.res; this.dlg = null; r(); }
      }
    },
    updateNarr(dt) {
      const I = G.input, n = this.narr;
      n.t += dt;
      if (n.t >= 0.12) n.shown = Math.min(n.total, n.shown + NARR_CPS * dt);
      const close = () => { const r = n.res; this.narrOut = { n, out: 0 }; this.narr = null; r(); };
      if (I.okHit() && n.t > 0.15) {
        I.consumeOk();
        if (n.shown < n.total) n.shown = n.total;
        else close();
      } else if (n.auto && n.t > n.auto && n.shown >= n.total) close();
    },

    // ------------------------------------------------------------ QTE 逐类型
    updateQte(dt) {
      const q = this.qte, I = G.input;
      q.t += dt;
      if (q.flash > 0) q.flash = Math.max(0, q.flash - dt);
      if (q.result != null) {
        q.endT += dt;
        if (q.endT > 0.7) this.finishQte(q);
        return;
      }
      const win = (r, s) => { q.result = r; q.state = 'done'; if (s) snd(s.n, s.o); };
      switch (q.type) {
        case 'mash': {
          q.v = Math.max(0, q.v - (q.decay || 0) * dt);
          const n = this.mashPresses(q, dt);
          if (n) { q.v += n; q.presses += n; q.flash = 0.08; snd('blip', { vol: 0.35, rate: 1 + q.v / q.need }); }
          q.m = clamp01(q.v / q.need);
          if (q.v >= q.need) win(true, { n: 'crit', o: { vol: 0.7 } });
          else if (q.t >= q.time) win(false, { n: 'menu_error', o: { vol: 0.5 } });
          break;
        }
        case 'timing': {
          const ph = (q.t * (q.speed || 1.1)) % 2;
          q.m = ph < 1 ? ph : 2 - ph;
          const press = (I.mashHit && I.mashHit()) || I.okHit();
          if (press) {
            I.consume('attack'); I.consumeOk();
            if (q.m >= q.zone[0] && q.m <= q.zone[1]) win(true, { n: 'crit', o: { vol: 0.8 } });
            else if (--q.tries <= 0) win(false, { n: 'menu_error', o: { vol: 0.5 } });
            else { q.misses++; q.flash = 0.25; snd('guard', { vol: 0.4 }); }
          }
          if (q.limit && q.t > q.limit && q.result == null) win(false, { n: 'menu_error', o: { vol: 0.5 } });
          break;
        }
        case 'rhythm': {
          const w = q.window || 0.16;
          const press = this.mashPresses(q, 0) > 0 || (I.okHit() && (I.consumeOk(), true));
          if (press) {
            let best = -1, bd = 1e9;
            q.notes.forEach((nt, i) => { if (q.notesState[i] === 0 && Math.abs(q.t - nt) < bd) { bd = Math.abs(q.t - nt); best = i; } });
            if (best >= 0 && bd <= w) { q.notesState[best] = 1; q.judged.push({ t: q.t, ok: true }); snd('pop', { vol: 0.6, rate: 1.3 }); }
            else { q.judged.push({ t: q.t, ok: false }); snd('blip', { vol: 0.3, rate: 0.6 }); }
          }
          q.notes.forEach((nt, i) => { if (q.notesState[i] === 0 && q.t - nt > w) { q.notesState[i] = -1; q.judged.push({ t: q.t, ok: false }); } });
          const last = q.notes.length ? q.notes[q.notes.length - 1] : 0;
          if (q.t > last + 0.8) {
            const hits = q.notesState.filter((s) => s === 1).length;
            const r = { hits, total: q.notes.length };
            win(r, { n: hits >= q.notes.length * (q.pass || 0.6) ? 'crit' : 'menu_error', o: { vol: 0.6 } });
          }
          break;
        }
        case 'clash': {
          const prog = clamp01(q.t / q.time);
          q.v -= q.rate * (0.6 + 0.4 * prog) * dt;
          const n = this.mashPresses(q, dt);
          if (n) {
            q.v += q.push * n; q.presses += n; q.flash = 0.06;
            snd('punch', { vol: 0.35, rate: (q.presses % 2 ? 1.0 : 1.12) * (0.96 + Math.random() * 0.08) });
          }
          q.m = clamp01(q.v);
          const lose = () => { if (q.id) this.clashFails[q.id] = (this.clashFails[q.id] || 0) + 1; win(false, { n: 'menu_error', o: { vol: 0.5 } }); };
          if (q.v >= 1) { q.v = 1; win(true, { n: 'crit', o: { vol: 0.9 } }); if (G.shake) G.shake(3, 0.25); }
          else if (q.v <= 0) { q.v = 0; lose(); }
          else if (q.t >= q.time) { if (q.v > 0.5) win(true, { n: 'crit', o: { vol: 0.8 } }); else lose(); }
          break;
        }
        case 'press': {
          if (I.hit(q.key)) {
            I.consume(q.key);
            const p = q.perfect;
            if (p && Math.abs(q.t - q.nowT) <= p) win('perfect', { n: 'dodge_perfect', o: { vol: 0.8 } });
            else win('ok', { n: 'guard', o: { vol: 0.7 } });
          } else if (q.t >= q.deadline) win('miss', { n: q.failOk ? null : 'menu_error', o: { vol: 0.5 } });
          if (q.result === 'miss' && q.failOk) q.state = 'done';
          break;
        }
        case 'pluck': this.updatePluck(q, dt); break;
        case 'aim': {
          const sp = 60;
          const f = q.drift * (0.3 + 0.7 * clamp01(q.t / q.time));
          q.dir += ((G.noise1 ? G.noise1(q.t * 0.9, 7) : Math.sin(q.t * 1.3)) * 2.2) * dt;
          q.p.x += Math.cos(q.dir) * f * dt + (Math.random() * 2 - 1) * q.jitter;
          q.p.y += Math.sin(q.dir) * f * dt * 0.7 + (Math.random() * 2 - 1) * q.jitter;
          if (I.isDown('left')) q.p.x -= sp * dt;
          if (I.isDown('right')) q.p.x += sp * dt;
          if (I.isDown('up')) q.p.y -= sp * dt;
          if (I.isDown('down')) q.p.y += sp * dt;
          q.p.x = Math.max(-80, Math.min(80, q.p.x)); q.p.y = Math.max(-50, Math.min(50, q.p.y));
          q.m = [q.p.x, q.p.y];
          if (Math.hypot(q.p.x, q.p.y) <= q.r) q.acc += dt;
          q.v = clamp01(q.acc / q.need);
          if (q.throw && I.hit('attack')) { I.consume('attack'); win(Math.hypot(q.p.x, q.p.y) <= q.r, { n: 'thud', o: { vol: .8 } }); }
          else if (!q.throw && q.acc >= q.need) win(true, { n: 'crit', o: { vol: 0.8 } });
          else if (q.t >= q.time) win(false, { n: 'menu_error', o: { vol: 0.5 } });
          break;
        }
      }
    },
    // 拔肉芽（规划 §5.1.4）：准星追肉芽，按住 J 且离中心 ≤ r 拔，否则钻入；钻满清零重来（第一次后放宽一次）；拔满接 finalMash
    updatePluck(q, dt) {
      const I = G.input;
      if (q.phase === 'final') {
        const fm = q.fm;
        fm.t += dt;
        fm.v = Math.max(0, fm.v - (fm.decay || 0) * dt);
        const n = this.mashPresses(q, dt);
        if (n) { fm.v += n; q.flash = 0.08; snd('stab', { vol: 0.5, rate: 0.7 + 0.04 * fm.v }); if (G.shake) G.shake(1.5, 0.1); }
        q.m = [0, 0];
        if (fm.v >= fm.need) { q.result = true; q.state = 'done'; q.pull = 1; snd('crit', { vol: 0.9 }); if (G.shake) G.shake(4, 0.3); }
        else if (fm.t >= fm.time) { fm.v = 0; fm.t = 0; fm.retries++; q.flash = 0.3; snd('menu_error', { vol: 0.4 }); }
        return;
      }
      const sp = q.speed;
      if (I.isDown('left')) q.aim.x -= sp * dt;
      if (I.isDown('right')) q.aim.x += sp * dt;
      if (I.isDown('up')) q.aim.y -= sp * dt;
      if (I.isDown('down')) q.aim.y += sp * dt;
      q.aim.x = Math.max(8, Math.min(312, q.aim.x)); q.aim.y = Math.max(8, Math.min(172, q.aim.y));
      // 肉芽抖动：正弦振幅随拔出进度变大 + 噪声；拔过一半后每 every 秒突然一跳
      const A = (q.wobble[0] + (q.wobble[1] - q.wobble[0]) * q.pull) * q.wobbleK;
      const w = Math.PI * 2 * q.wobbleHz;
      const nz = (s) => (G.noise1 ? G.noise1(q.t * 3.1, s) : Math.sin(q.t * 7.3 + s)) * q.noise;
      if (q.pull > q.jump.after) {
        q.nextJump -= dt;
        if (q.nextJump <= 0) {
          q.nextJump = q.jump.every;
          const a = Math.random() * Math.PI * 2;
          q.jumpOff = { x: Math.cos(a) * q.jump.px * q.wobbleK, y: Math.sin(a) * q.jump.px * 0.6 * q.wobbleK };
          snd('heartbeat', { vol: 0.35 });
        }
      } else q.jumpOff = { x: 0, y: 0 };
      q.budPos.x = q.bud[0] + A * Math.sin(w * q.t) + nz(1) + q.jumpOff.x;
      q.budPos.y = q.bud[1] + A * 0.45 * Math.sin(w * 0.7 * q.t + 1.3) + nz(2) + q.jumpOff.y;
      const dx = q.aim.x - q.budPos.x, dy = q.aim.y - q.budPos.y;
      q.m = [dx, dy];
      q.holding = !!I.isDown('attack');
      if (q.holding && Math.hypot(dx, dy) <= q.r) {
        q.pull = Math.min(1, q.pull + dt / q.pullSec);
        q.pullSfxT = (q.pullSfxT || 0) - dt;
        if (q.pullSfxT <= 0) { q.pullSfxT = 0.35; snd('stab', { vol: 0.3, rate: 0.7 }); }
      } else {
        q.drill = Math.min(1, q.drill + dt / q.drillSec);
      }
      if (q.drill >= 1) {
        q.pull = 0; q.drill = 0; q.resets++;
        if (!q.relaxed) { q.relaxed = true; q.r = 9; q.wobbleK = 0.7; }
        if (G.shake) G.shake(4, 0.3);
        snd('rumble', { vol: 0.6 });
        q.flash = 0.3;
        if (G.dbg && G.dbg.ev) G.dbg.ev('pluck_reset', { n: q.resets });
        if (q.onReset) {
          const p = q.onReset(q);
          if (p && typeof p.then === 'function') { q.hold = true; p.then(() => { q.hold = false; }, () => { q.hold = false; }); }
        }
        return;
      }
      if (q.pull >= 1) {
        q.phase = 'final';
        q.fm = Object.assign({ v: 0, t: 0, retries: 0 }, q.finalMash);
        snd('sting_shock', { vol: 0.5 });
      }
    },

    // ============================================================ 画
    draw(g) {
      g.imageSmoothingEnabled = false;
      if (this.insertUI && this.insertUI.draw) {
        const t0 = this.insertUI.t0 == null ? G.clk.ui : this.insertUI.t0;
        this.insertUI.draw(g, G.clk.ui - t0);
      }
      if (this.letterbox > 0.5) {
        const h = Math.round(this.letterbox);
        g.fillStyle = '#000'; g.fillRect(0, 0, UW, h); g.fillRect(0, UH - h, UW, h);
      }
      if (G.hud) { if (G.hud.draw) G.hud.draw(g); if (G.hud.drawMarks) G.hud.drawMarks(g); }
      if (G.uifx && G.uifx.draw) G.uifx.draw(g);
      for (const h of this.hints) this.drawHint(g, h);
      if (this.narr && !this.narr.onBlack) this.drawNarr(g, this.narr, 1);
      if (this.narrOut && !this.narrOut.n.onBlack) this.drawNarr(g, this.narrOut.n, 1 - this.narrOut.out / 0.25);
      const qHold = this.qte && this.qte.hold;      // 拔肉芽钻满后剧情在说话：QTE 画在对话下面
      if (qHold) this.drawQte(g);
      if (this.dlg) this.drawDialog(g);
      if (this.choiceBox) this.drawChoice(g);
      if (this.noticeBox) this.drawNotice(g);
      if (this.qte && !qHold) this.drawQte(g);
      if (G.uifx && G.uifx.drawCard) G.uifx.drawCard(g);
    },
    drawTop(g) {
      g.imageSmoothingEnabled = false;
      if (this.narr && this.narr.onBlack) this.drawNarr(g, this.narr, 1);
      if (this.narrOut && this.narrOut.n.onBlack) this.drawNarr(g, this.narrOut.n, 1 - this.narrOut.out / 0.25);
      if (this.menu) this.drawMenu(g);
    },

    // text.py box()：投影 (+4,+4)、底、2 px 黑边、内缩 2 的 2 px 白框、内缩 4 的 1 px 暗线（坐标含端点，和 PIL 一样）
    box(g, x0, y0, x1, y1, o = {}) {
      x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
      if (y1 - y0 < 2 || x1 - x0 < 2) return;
      const w = x1 - x0 + 1, h = y1 - y0 + 1;
      // PIL 是“替换”不是叠加：投影只画框外露出的 L 形，框内底色就是 fill 本身
      if (o.shadow !== false) {
        g.fillStyle = o.shadow || 'rgba(0,0,0,0.63)';
        g.fillRect(x1 + 1, y0 + 4, 4, h); g.fillRect(x0 + 4, y1 + 1, w - 4, 4);
      }
      g.fillStyle = '#000';
      g.fillRect(x0, y0, w, 2); g.fillRect(x0, y1 - 1, w, 2); g.fillRect(x0, y0 + 2, 2, h - 4); g.fillRect(x1 - 1, y0 + 2, 2, h - 4);
      g.fillStyle = o.fill || 'rgba(16,14,40,0.88)';
      g.fillRect(x0 + 2, y0 + 2, w - 4, h - 4);
      if (y1 - y0 >= 10) {
        const b = o.border || '#fff';
        g.fillStyle = b;
        g.fillRect(x0 + 2, y0 + 2, w - 4, 2); g.fillRect(x0 + 2, y1 - 3, w - 4, 2);
        g.fillRect(x0 + 2, y0 + 2, 2, h - 4); g.fillRect(x1 - 3, y0 + 2, 2, h - 4);
        g.fillStyle = 'rgba(0,0,0,0.47)';
        g.fillRect(x0 + 4, y0 + 4, w - 8, 1); g.fillRect(x0 + 4, y1 - 4, w - 8, 1);
        g.fillRect(x0 + 4, y0 + 5, 1, h - 10); g.fillRect(x1 - 4, y0 + 5, 1, h - 10);
      }
    },
    // 引擎自己的界面符号（不走字库，simsun 没有 ►）：'cursor' 6×9 右三角、'next' 9×5 下三角、'down' 7×4 ▼、'up' 7×4 ▲
    glyph(g, kind, x, y, color = '#fff', o = {}) {
      x = Math.round(x); y = Math.round(y);
      const rows = [];
      if (kind === 'cursor') for (let r = 0; r < 9; r++) rows.push([0, r, 6 - Math.abs(r - 4)]);
      else if (kind === 'next') for (let r = 0; r < 5; r++) rows.push([r, r, 9 - 2 * r]);
      else if (kind === 'down') for (let r = 0; r < 4; r++) rows.push([r, r, 7 - 2 * r]);
      else if (kind === 'up') for (let r = 0; r < 4; r++) rows.push([3 - r, r, 1 + 2 * r]);
      if (o.shadow) { g.fillStyle = o.shadow; for (const [dx, dy, w] of rows) g.fillRect(x + dx + 1, y + dy + 1, w, 1); }
      g.fillStyle = color;
      for (const [dx, dy, w] of rows) g.fillRect(x + dx, y + dy, w, 1);
    },

    drawDialog(g) {
      const d = this.dlg, F = f16();
      const k = ez(Math.min(1, d.t / POP), 'out');
      let y0 = d.y0, y1 = d.y0 + BOX_H;
      if (k < 1) {
        const cy = (y0 + y1) / 2, hh = Math.max(2, BOX_H * k / 2);
        y0 = Math.floor(cy - hh); y1 = Math.floor(cy + hh);
      }
      this.box(g, BOX_X0, y0, BOX_X1, y1);
      if (k < 0.95) return;
      const total = d.pageLen[d.page];
      const typing = d.shown < total;
      if (d.head) {
        const { imgs, w, h } = d.head, sc = d.sc, px = d.px, py = d.py;
        const fw = w * sc, fh = h * sc;
        g.fillStyle = '#fff'; g.fillRect(px - 2, py - 2, fw + 4, fh + 4);
        g.fillStyle = '#282446'; g.fillRect(px - 1, py - 1, fw + 2, fh + 2);
        const pf = typing && imgs.length > 1 ? Math.floor(G.clk.ui * 8) % 2 : 0;
        const im = imgs[pf] || imgs[0];
        if (G.ready(im)) g.drawImage(im, 0, 0, w, h, px, py, fw, fh);
      }
      if (d.name) {
        const tw = F.width(d.name) + 14;
        const ty = Math.max(0, y0 - 14), x = d.tx - 4;
        g.fillStyle = '#fff'; g.fillRect(x, ty, tw + 1, 21);
        g.fillStyle = d.color; g.fillRect(x + 2, ty + 2, tw - 3, 17);
        F.draw(g, d.name, d.tx + 3, ty + 2, '#fff');
      }
      let left = Math.floor(d.shown);
      let ly = y0 + (d.name ? 16 : 14);
      for (const line of d.pages[d.page]) {
        const part = line.slice(0, Math.max(0, left));
        left -= line.length;
        if (part) F.draw(g, part, d.tx, ly, '#fff', { outline: '#000' });
        ly += 22;
      }
      if (!typing && Math.floor(G.clk.ui * 3) % 2 === 0) this.glyph(g, 'next', BOX_X1 - 18, y0 + BOX_H - 16, '#fff');
    },
    drawChoice(g) {
      const c = this.choiceBox, F = f16();
      const { x, y, w, h } = this.choiceLayout(c);
      const k = ez(Math.min(1, c.t / 0.1), 'out');
      if (k < 1) { const cy = y + h / 2, hh = Math.max(2, h * k / 2); this.box(g, x, Math.floor(cy - hh), x + w, Math.floor(cy + hh)); return; }
      if (c.title) f12().draw(g, c.title, x + 4, y - 16, '#ffe9a8', { outline: '#140c18' });
      this.box(g, x, y, x + w, y + h);
      c.options.forEach((s, i) => {
        const sel = i === c.idx, ry = y + 6 + i * 24;
        if (sel) { g.fillStyle = SEL; g.fillRect(x + 5, ry, w - 9, 23); }
        if (sel) this.glyph(g, 'cursor', x + 10 + (Math.floor(G.clk.ui * 4) % 2), ry + 7, GOLD, { shadow: '#140c18' });
        F.draw(g, s, x + 26, ry + 4, sel ? '#fff' : '#bdb6c8', { outline: sel ? '#000' : null });
      });
    },
    drawNarr(g, n, alpha) {
      const F = f16();
      const a0 = Math.min(1, n.t / 0.25) * clamp01(alpha);
      if (a0 <= 0) return;
      const hh = n.lines.length * 22 + 16;
      const y0 = n.pos === 'top' ? 10 : n.pos === 'bottom' ? UH - hh - 10 : Math.round((UH - hh) / 2);
      g.save();
      g.globalAlpha = a0;
      g.fillStyle = 'rgba(0,0,0,0.67)'; g.fillRect(0, y0, UW, hh);
      let left = Math.floor(n.shown);
      n.lines.forEach((line, i) => {
        const part = line.slice(0, Math.max(0, left));
        left -= line.length;
        if (part) F.draw(g, part, Math.round(UW / 2 - F.width(line) / 2), y0 + 8 + i * 22 + 2, '#fff', { outline: '#000' });
      });
      g.restore();
    },
    drawHint(g, h) {
      const F = f16();
      const a = Math.max(0, Math.min(1, h.t * 4, (h.dur - h.t) * 3));
      if (a <= 0) return;
      const S = tsafe();
      const wrapW = S && S.sys ? Math.max(240, Math.min(520, 2 * (S.sys - 8 - UW / 2) - 20)) : 520;
      const lines = F.wrap(h.text, wrapW);
      const w = Math.max(...lines.map((l) => F.width(l))) + 20;
      const hh = lines.length * 20 + 16;
      let y;
      const hudBottom = G.hud && G.hud.on ? G.hud.topBottom() : 0;
      if (S) y = Math.max(64, hudBottom + 6);
      else if (this.dlg || this.choiceBox) y = 64;
      else y = UH - hh - 12;
      const x = Math.round((UW - w) / 2);
      g.save();
      g.globalAlpha = a;
      this.box(g, x, y, x + w, y + hh, { fill: 'rgba(20,18,30,0.88)', border: GOLD });
      lines.forEach((l, i) => F.draw(g, l, UW / 2, y + 9 + i * 20, '#fff', { align: 'center' }));
      g.restore();
    },
    drawMenu(g) {
      const m = this.menu, F = f16();
      g.fillStyle = 'rgba(0,0,0,0.55)'; g.fillRect(0, 0, UW, UH);
      const { x, y, w, h, oy } = this.menuLayout(m);
      const k = ez(Math.min(1, m.t / 0.12), 'out');
      if (k < 1) { const cy = y + h / 2, hh = Math.max(2, h * k / 2); this.box(g, x, Math.floor(cy - hh), x + w, Math.floor(cy + hh)); return; }
      this.box(g, x, y, x + w, y + h);
      if (m.title) {
        F.draw(g, m.title, UW / 2, y + 15, '#ffe9a8', { align: 'center', outline: '#1a1020' });
        g.fillStyle = 'rgba(255,233,168,0.35)'; g.fillRect(x + 16, y + 37, w - 32, 1);
      }
      m.options.forEach((o, i) => {
        const sel = i === m.idx, ry = oy + i * 26;
        if (sel) { g.fillStyle = SEL; g.fillRect(x + 10, ry - 4, w - 20, 24); }
        if (sel) this.glyph(g, 'cursor', x + 20 + (Math.floor(G.clk.ui * 4) % 2), ry + 3, GOLD, { shadow: '#140c18' });
        F.draw(g, String(o), x + 36, ry, sel ? '#fff' : '#bdb6c8', { outline: sel ? '#000' : null });
      });
      if (m.note) f12().draw(g, m.note, UW / 2, oy + m.options.length * 26 + 6, '#9a93a8', { align: 'center' });
    },
    drawNotice(g) {
      const n = this.noticeBox, F = f16();
      const k = ez(Math.min(1, n.t / 0.25), 'back');
      // 正文带换行（操作说明、体验版结束等）：标题单独一行、正文逐行，框按行数加高、放在画面中间；单行的照旧在下方一条
      const rows = n.text && String(n.text).indexOf('\n') >= 0 ? String(n.text).split('\n') : null;
      if (rows) return this.drawNoticeRows(g, n, F, k, rows);
      const bw = 440, bh = 64, x0 = Math.round(UW / 2 - bw / 2), y0 = 284 + Math.round((1 - k) * 40);
      g.save();
      g.globalAlpha = clamp01(n.t / 0.08);
      g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(x0 + 4, y0 + 4, bw, bh);
      g.fillStyle = 'rgba(12,16,48,0.92)'; g.fillRect(x0, y0, bw, bh);
      g.fillStyle = '#fff';
      g.fillRect(x0, y0, bw, 2); g.fillRect(x0, y0 + bh - 2, bw, 2); g.fillRect(x0, y0, 2, bh); g.fillRect(x0 + bw - 2, y0, 2, bh);
      g.fillStyle = '#5a6ec8';
      g.fillRect(x0 + 4, y0 + 4, bw - 8, 2); g.fillRect(x0 + 4, y0 + bh - 6, bw - 8, 2); g.fillRect(x0 + 4, y0 + 4, 2, bh - 8); g.fillRect(x0 + bw - 6, y0 + 4, 2, bh - 8);
      let tx = x0 + 18;
      const hd = n.who ? headOf(n.who, n.expr) : null;
      if (hd) {
        const s = hd.h <= 34 ? 2 : 1, cx0 = x0 + 8, cy0 = y0 + 4;
        g.save(); g.beginPath(); g.rect(cx0, cy0, 56, 56); g.clip();
        const im = hd.imgs[0];
        if (G.ready(im)) g.drawImage(im, 0, 0, hd.w, hd.h, cx0 + Math.round((56 - hd.w * s) / 2), cy0 + 56 - hd.h * s + 4, hd.w * s, hd.h * s);
        g.restore();
        tx = x0 + 74;
      }
      const tw = n.title ? F.draw(g, n.title, tx, y0 + 12, '#ffe26e', { outline: '#140c18' }) : 0;
      if (n.text) F.draw(g, n.text, tx + tw + (tw ? 6 : 0), y0 + 12, '#fff', { outline: '#140c18' });
      if (n.sub) f12().draw(g, n.sub, tx, y0 + 38, '#96dcff', { outline: '#140c18' });
      if (n.t > 0.6 && Math.floor(G.clk.ui * 3) % 2 === 0) this.glyph(g, 'next', x0 + bw - 22, y0 + bh - 15, '#fff');
      // 周围冒小星星
      const rnd = G.prng ? G.prng(31) : Math.random;
      for (let i = 0; i < 6; i++) {
        const sx = x0 + Math.floor(rnd() * (bw + 40) - 20), sy = y0 + Math.floor(rnd() * 30 - 22), t0 = 0.05 + i * 0.12;
        const kk = (n.t - t0) / 0.45;
        if (kk <= 0 || kk >= 1) continue;
        const s = Math.round(Math.sin(kk * Math.PI) * 4);
        g.fillStyle = '#fff096'; g.fillRect(sx - s, sy, 2 * s + 2, 2); g.fillRect(sx, sy - s, 2, 2 * s + 2);
      }
      g.restore();
    },
    drawNoticeRows(g, n, F, k, rows) {
      const lh = 22, head = n.title ? 30 : 0;
      const bw = 480, bh = 24 + head + rows.length * lh + (n.sub ? 18 : 0);
      const x0 = Math.round(UW / 2 - bw / 2), y0 = Math.round(UH / 2 - bh / 2) + Math.round((1 - k) * 30);
      g.save();
      g.globalAlpha = clamp01(n.t / 0.08);
      g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(x0 + 4, y0 + 4, bw, bh);
      g.fillStyle = 'rgba(12,16,48,0.94)'; g.fillRect(x0, y0, bw, bh);
      g.fillStyle = '#fff';
      g.fillRect(x0, y0, bw, 2); g.fillRect(x0, y0 + bh - 2, bw, 2); g.fillRect(x0, y0, 2, bh); g.fillRect(x0 + bw - 2, y0, 2, bh);
      g.fillStyle = '#5a6ec8';
      g.fillRect(x0 + 4, y0 + 4, bw - 8, 2); g.fillRect(x0 + 4, y0 + bh - 6, bw - 8, 2); g.fillRect(x0 + 4, y0 + 4, 2, bh - 8); g.fillRect(x0 + bw - 6, y0 + 4, 2, bh - 8);
      if (n.title) {
        F.draw(g, n.title, UW / 2, y0 + 12, '#ffe26e', { outline: '#140c18', align: 'center' });
        g.fillStyle = 'rgba(255,226,110,0.35)'; g.fillRect(x0 + 24, y0 + 34, bw - 48, 1);
      }
      rows.forEach((r, i) => F.draw(g, r, x0 + 24, y0 + 12 + head + i * lh, '#fff', { outline: '#140c18' }));
      if (n.sub) f12().draw(g, n.sub, x0 + 24, y0 + 12 + head + rows.length * lh + 2, '#96dcff', { outline: '#140c18' });
      if (n.t > 0.6 && Math.floor(G.clk.ui * 3) % 2 === 0) this.glyph(g, 'next', x0 + bw - 22, y0 + bh - 15, '#fff');
      g.restore();
    },

    // ------------------------------------------------------------ QTE 画
    drawQte(g) {
      const q = this.qte, F = f16();
      if (q.type === 'pluck') { this.drawPluckUI(g, q); return; }
      // o.y（可省）= QTE 框的上沿：剧情动作在画面中间时（保健室的钢笔）把框挪到上方，别挡住人物
      const x0 = 120, y0 = typeof q.y === 'number' ? q.y : 210, x1 = 520, y1 = y0 + 72;
      const shake = q.flash > 0 && q.type !== 'press' ? Math.round((Math.random() * 2 - 1) * 2) : 0;
      g.save();
      g.translate(shake, 0);
      this.box(g, x0, y0, x1, y1, { fill: 'rgba(14,12,30,0.92)', border: q.type === 'clash' ? '#ffe9a8' : '#fff' });
      F.draw(g, q.label || '', UW / 2, y0 + 8, '#ffe9a8', { align: 'center', outline: '#140c18' });
      const bx = x0 + 16, bw = x1 - x0 - 32;
      switch (q.type) {
        case 'mash': {
          keyCap(g, x0 + 16, y0 + 32, 'J', Math.floor(G.clk.ui * 8) % 2 === 0 || q.flash > 0);
          const bx2 = x0 + 50, bw2 = x1 - x0 - 66;
          this.bar(g, bx2, y0 + 36, bw2, 10, q.v / q.need, '#ffb03a');
          this.bar(g, bx2, y0 + 52, bw2, 2, 1 - q.t / q.time, '#8a8498');
          break;
        }
        case 'timing': {
          const by = y0 + 38;
          g.fillStyle = '#0c0a14'; g.fillRect(bx - 1, by - 1, bw + 2, 14);
          g.fillStyle = '#2a2040'; g.fillRect(bx, by, bw, 12);
          g.fillStyle = q.flash > 0 ? '#ff6040' : '#ffd34a';
          g.fillRect(bx + Math.round(q.zone[0] * bw), by, Math.round((q.zone[1] - q.zone[0]) * bw), 12);
          g.fillStyle = 'rgba(255,255,255,0.4)'; g.fillRect(bx + Math.round(q.zone[0] * bw), by, Math.round((q.zone[1] - q.zone[0]) * bw), 2);
          const mx = bx + Math.round((q.m || 0) * bw);
          g.fillStyle = '#0c0a14'; g.fillRect(mx - 3, by - 6, 7, 24);
          g.fillStyle = '#fff'; g.fillRect(mx - 2, by - 5, 5, 22);
          if (q.tries > 1 || q.misses) f12().draw(g, '剩余 ' + q.tries + ' 次', x1 - 14, y0 + 56, '#cfe8ff', { align: 'right' });
          break;
        }
        case 'rhythm': {
          const lx = x0 + 60, by = y0 + 44, travel = q.travel || 1.6;
          g.fillStyle = '#2a2040'; g.fillRect(x0 + 14, by - 8, x1 - x0 - 28, 17);
          g.fillStyle = GOLD; g.fillRect(lx, by - 11, 3, 23);
          q.notes.forEach((nt, i) => {
            if (q.notesState[i] !== 0) return;
            const x = lx + Math.round(((nt - q.t) / travel) * (x1 - x0 - 90));
            if (x < x0 + 12 || x > x1 - 16) return;
            g.fillStyle = '#ff9ec0'; g.fillRect(x - 5, by - 5, 11, 11);
            g.fillStyle = '#fff'; g.fillRect(x - 2, by - 2, 5, 5);
          });
          const last = q.judged[q.judged.length - 1];
          if (last && q.t - last.t < 0.35) f16().draw(g, last.ok ? '好！' : '……', lx + 1, y0 - 22, last.ok ? '#ffe14a' : '#9a93a8', { align: 'center', outline: '#140c18' });
          f12().draw(g, q.notesState.filter((s) => s === 1).length + ' / ' + q.notes.length, x1 - 14, y0 + 10, '#cfe8ff', { align: 'right' });
          break;
        }
        case 'clash': this.drawClash(g, q, x0, y0, x1, y1); break;
        case 'press': this.drawPress(g, q, x0, y0, x1, y1); break;
        case 'aim': this.drawAim(g, q); break;
      }
      g.restore();
      this.drawQteResult(g, q, y0);
    },
    drawQteResult(g, q, y0) {
      if (q.result == null) return;
      const ok = this.qteOk(q);
      let s = ok ? '成功！' : (q.failOk ? '……' : '失败……');
      if (q.result === 'perfect') s = '完美！';
      const k = ez(Math.min(1, q.endT / 0.12), 'back');
      const im = f16().bake(s, ok ? '#ffe14a' : '#cfc8dc', { outline: '#140c18' });
      const sc = ok ? 2 : 1;
      const w = Math.round(im.width * sc * Math.max(0.2, k)), h = Math.round(im.height * sc * Math.max(0.2, k));
      g.drawImage(im, Math.round(UW / 2 - w / 2), Math.round(y0 - 14 - h / 2), w, h);
    },
    bar(g, x, y, w, h, k, col, back = '#2a2030') {
      k = clamp01(k);
      g.fillStyle = '#0c0a14'; g.fillRect(x - 1, y - 1, w + 2, h + 2);
      g.fillStyle = back; g.fillRect(x, y, w, h);
      g.fillStyle = col; g.fillRect(x, y, Math.round(w * k), h);
      if (h >= 3) { g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(x, y, Math.round(w * k), 1); }
    },
    // 拳拳相对：左边我方色、右边敌方色，交界处火花
    drawClash(g, q, x0, y0, x1) {
      const cols = q.colours || QDEF.clash.colours;
      const bx = x0 + 14, bw = x1 - x0 - 28, by = y0 + 32, bh = 16;
      const cut = bx + Math.round(clamp01(q.v) * bw);
      g.fillStyle = '#0c0a14'; g.fillRect(bx - 2, by - 2, bw + 4, bh + 4);
      g.fillStyle = cols[0]; g.fillRect(bx, by, cut - bx, bh);
      g.fillStyle = cols[1]; g.fillRect(cut, by, bx + bw - cut, bh);
      g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(bx, by, bw, 2);
      g.fillStyle = 'rgba(0,0,0,0.3)'; g.fillRect(bx, by + bh - 3, bw, 3);
      g.fillStyle = 'rgba(255,255,255,0.6)'; g.fillRect(bx + Math.round(bw / 2), by - 4, 1, bh + 8);
      // 交界火花（12 fps 抽帧）
      const k = Math.floor(G.clk.ui * 12);
      const hs = (i, s) => (G.hash01 ? G.hash01(k, i, s) : Math.random());
      g.fillStyle = '#fff'; g.fillRect(cut - 2, by - 6, 4, bh + 12);
      for (let i = 0; i < 6; i++) {
        const a = hs(i, 1) * Math.PI * 2, L = 6 + hs(i, 2) * 14;
        const sx = cut + Math.cos(a) * L, sy = by + bh / 2 + Math.sin(a) * L * 0.7;
        g.fillStyle = i % 2 ? '#fff4a0' : '#fff';
        g.fillRect(Math.round(sx) - 1, Math.round(sy) - 1, 3, 3);
      }
      f12().draw(g, '我方', bx, by + bh + 6, cols[0], { outline: '#000' });
      f12().draw(g, '敌方', bx + bw, by + bh + 6, cols[1], { outline: '#000', align: 'right' });
      this.bar(g, bx + 60, by + bh + 11, bw - 120, 2, 1 - q.t / q.time, '#8a8498');
      keyCap(g, UW / 2 - 12, by + bh + 4, 'J', Math.floor(G.clk.ui * 10) % 2 === 0 || q.flash > 0, 18);
    },
    // 指定键：收缩的圈落在“现在！”时刻；perfect 时圈内标金
    drawPress(g, q, x0, y0, x1) {
      const cx = UW / 2, cy = y0 + 48;
      keyCap(g, cx - 14, cy - 14, KEYCAP[q.key] || '?', q.result != null, 28);
      if (q.result == null) {
        const r = Math.max(0, 16 + (q.nowT - q.t) * 90);
        const col = q.perfect && Math.abs(q.t - q.nowT) <= q.perfect ? '#ffe040' : '#fff';
        for (let a = 0; a < 48; a++) {
          const ang = a / 48 * Math.PI * 2;
          g.fillStyle = col;
          g.fillRect(Math.round(cx + Math.cos(ang) * r) - 1, Math.round(cy + Math.sin(ang) * r * 0.75) - 1, 2, 2);
        }
        if (q.perfect && Math.abs(q.t - q.nowT) <= q.perfect) f16().draw(g, '现在！', cx + 34, cy - 8, '#ffe040', { outline: '#3a0a00' });
        this.bar(g, x0 + 30, y0 + 64, x1 - x0 - 60, 2, 1 - q.t / q.deadline, '#8a8498');
      }
    },
    drawAim(g, q) {
      const cx = UW / 2, cy = 106, bw = 320, bh = 200;     // 160×100 的框 ×2
      g.fillStyle = 'rgba(10,8,20,0.6)'; g.fillRect(cx - bw / 2, cy - bh / 2, bw, bh);
      g.fillStyle = '#fff'; g.fillRect(cx - bw / 2, cy - bh / 2, bw, 1); g.fillRect(cx - bw / 2, cy + bh / 2, bw, 1);
      g.fillRect(cx - bw / 2, cy - bh / 2, 1, bh); g.fillRect(cx + bw / 2, cy - bh / 2, 1, bh + 1);
      const rr = q.r * 2;
      for (let a = 0; a < 40; a++) { const ang = a / 40 * Math.PI * 2; g.fillStyle = GOLD; g.fillRect(Math.round(cx + Math.cos(ang) * rr), Math.round(cy + Math.sin(ang) * rr), 2, 2); }
      const px = Math.round(cx + q.p.x * 2), py = Math.round(cy + q.p.y * 2);
      g.fillStyle = '#ff3048'; g.fillRect(px - 8, py - 1, 17, 2); g.fillRect(px - 1, py - 8, 2, 17);
      this.bar(g, cx - 150, 250, 300, 8, q.v, '#ffd040');
      this.bar(g, cx - 150, 264, 300, 2, 1 - q.t / q.time, '#8a8498');
    },
    // 拔肉芽的世界层画面：剧情给 o.draw(wg, q) 就用它；没给用默认（tatami_top 底 + 花京院的脸 + 肉芽 + 白金之星的手）
    drawPluckWorld(wg, q, t) {
      if (q.draw) { q.draw(wg, q, t); return; }
      wg.fillStyle = '#2a2018'; wg.fillRect(0, 0, 320, 180);
      const D = G.D || {};
      const bg = D.bg && D.bg.tatami_top;
      if (bg && bg.layers && bg.layers[0]) { const im = G.image(bg.layers[0].image); if (G.ready(im)) wg.drawImage(im, 0, 0); }
      sheet(wg, 'scene:s04_kak_face', 0, 160, 110 + 64, 4);
      const bf = Math.floor(G.clk.ui * 8) % 3;
      sheet(wg, 'prop:fleshbud', bf, q.budPos.x, q.budPos.y, 3);
      if (q.drill > 0.02) {
        wg.fillStyle = '#e070b0';
        const L = q.drill * 80;
        for (let i = 0; i < L; i += 2) {
          const x = q.aim.x + 6 + i * 0.6 + Math.sin(i * 0.3 + G.clk.ui * 10) * 2, y = q.aim.y + 10 + i * 0.75;
          wg.fillRect(Math.round(x), Math.round(y), 2, 2);
        }
      }
      sheet(wg, 'scene:s04_sphand', q.holding ? 1 : 0, q.aim.x + 2, q.aim.y + 22, 2);
    },
    drawPluckUI(g, q) {
      const F = f16();
      redEdge(g, q.drill * 0.6);
      if (q.flash > 0) { g.fillStyle = 'rgba(255,60,90,' + (q.flash * 0.6).toFixed(3) + ')'; g.fillRect(0, 0, UW, UH); }
      const label = q.phase === 'final' ? q.fm.label : q.label;
      this.box(g, 150, 10, 490, 44, { fill: 'rgba(14,12,30,0.88)' });
      F.draw(g, label, UW / 2, 19, '#ffe9a8', { align: 'center', outline: '#140c18' });
      // 准星（UI 坐标 = 世界画布 ×2；插入画面没有推镜）
      if (q.phase !== 'final') {
        const ax = Math.round(q.aim.x * 2), ay = Math.round(q.aim.y * 2);
        const near = Math.hypot(q.m[0], q.m[1]) <= q.r;
        const col = near ? '#7dff9a' : '#ffffff';
        g.fillStyle = '#000';
        g.fillRect(ax - 9, ay - 1, 6, 3); g.fillRect(ax + 4, ay - 1, 6, 3); g.fillRect(ax - 1, ay - 9, 3, 6); g.fillRect(ax - 1, ay + 4, 3, 6);
        g.fillStyle = col;
        g.fillRect(ax - 8, ay, 4, 1); g.fillRect(ax + 5, ay, 4, 1); g.fillRect(ax, ay - 8, 1, 4); g.fillRect(ax, ay + 5, 1, 4);
      }
      const bx = 170, bw = 300;
      f12().draw(g, '拔出', bx - 8, 318, '#ffd8f0', { align: 'right', outline: '#000' });
      this.bar(g, bx, 320, bw, 8, q.phase === 'final' ? 1 : q.pull, '#ff9ec0');
      f12().draw(g, '钻入', bx - 8, 336, '#ff8080', { align: 'right', outline: '#000' });
      this.bar(g, bx, 338, bw, 5, q.drill, '#e02040');
      if (q.phase === 'final') {
        keyCap(g, UW / 2 - 14, 250, 'J', Math.floor(G.clk.ui * 10) % 2 === 0 || q.flash > 0, 28);
        this.bar(g, 220, 288, 200, 10, q.fm.v / q.fm.need, '#ffb03a');
        this.bar(g, 220, 302, 200, 2, 1 - q.fm.t / q.fm.time, '#8a8498');
      } else keyCap(g, 476, 316, 'J', !!q.holding, 22);
      this.drawQteResult(g, q, 90);
    },
  });
})();
