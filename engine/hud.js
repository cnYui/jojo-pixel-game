// HUD（UI 层 640×360）：队长面板（血条 + 能量条）、队伍行、探索头像条（灰 / 问号）、Boss 条（阶段刻度）、教学进度格、
// 计时、环境槽、连击数、头顶标记（表情 / 互动提示 / 小血条 / 替身调查 U）（技术约定 §4.10.3）
'use strict';
(function () {
  const G = window.G;
  const UW = 640;
  const LOW = 0.25;            // 低血线（= CFG.lowHp，规划 §3.7 第 12 条）
  const TAG_DY = 40;           // 左上 VS 小标签（高 34，画在 y 8）在时，队长面板往下让的距离（原来 26，标签压住了名字）

  const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
  const f16 = () => { if (!G.f16 && G.initFonts) G.initFonts(); return G.f16; };
  const f12 = () => { if (!G.f12 && G.initFonts) G.initFonts(); return G.f12; };
  const snd = (name, o) => (name && G.audio && G.audio.sfx ? G.audio.sfx(name, o) : null);
  const box = (g, x0, y0, x1, y1, o) => (G.ui && G.ui.box ? G.ui.box(g, x0, y0, x1, y1, o) : null);
  const W = () => G.world || null;
  const tsafe = () => { const T = G.touch; return T && T.on && T.safe ? T.safe : null; };
  function mix(a, b, k) {
    if (G.mixHex) return G.mixHex(a, b, k);
    const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
    const c = [16, 8, 0].map((s) => Math.round(((pa >> s) & 255) * (1 - k) + ((pb >> s) & 255) * k));
    return '#' + c.map((v) => v.toString(16).padStart(2, '0')).join('');
  }
  function w2u(x, y, z = 0) {
    if (G.cam && G.cam.w2u) {
      const r = G.cam.w2u(x, y, z);
      if (Array.isArray(r)) return { x: r[0], y: r[1] };
      if (r) return { x: r.x, y: r.y };
    }
    return { x: (x - ((G.cam && G.cam.x) || 0)) * 2, y: (y - z - ((G.cam && G.cam.y) || 0)) * 2 };
  }
  const headY = (a) => (typeof a.headY === 'function' ? a.headY() : a.y - (a.z || 0) - (a.top || 40) * (a.scale || 1));
  function hasHead(cid, expr) {
    const c = G.D && G.D.chars && G.D.chars[cid];
    return !!(c && c.heads && (c.heads[expr] || (c.headAlias && c.headAlias[expr] && c.heads[c.headAlias[expr]])));
  }
  function headImg(cid, expr) {
    if (!G.head || !(G.D && G.D.chars && G.D.chars[cid])) return null;
    if (expr !== 'normal' && !hasHead(cid, expr)) expr = 'normal';
    const h = G.head(cid, expr);
    const im = Array.isArray(h) ? h[0] : h;
    return im && G.ready(im) ? im : null;
  }
  function auraOf(a) {
    const D = G.D || {};
    const sid = (a && a.standId) || (a && D.heroes && D.heroes[a.cid] && D.heroes[a.cid].stand);
    return (sid && D.stands && D.stands[sid] && D.stands[sid].aura) || '#b090ff';
  }
  function nameOf(a) {
    const D = G.D || {};
    if (!a) return '';
    if (G.NAMES && G.NAMES[a.cid]) return G.NAMES[a.cid];
    if (D.heroes && D.heroes[a.cid]) return D.heroes[a.cid].short;
    return a.name || (D.chars && D.chars[a.cid] && D.chars[a.cid].name) || a.cid || '';
  }
  // 灰度 / 黑剪影头像（探索头像条的 gray / unknown），缓存
  const variants = new Map();
  function variant(im, kind) {
    const key = kind + '|' + im.src.length + '|' + im.src.slice(-32);
    let c = variants.get(key);
    if (c) return c;
    const w = im.naturalWidth, h = im.naturalHeight;
    if (kind === 'gray') {
      c = G.mkCanvas(w, h, true);
      c.g.drawImage(im, 0, 0);
      const id = c.g.getImageData(0, 0, w, h), d = id.data;
      for (let i = 0; i < d.length; i += 4) {
        const l = Math.round((d[i] * 0.3 + d[i + 1] * 0.59 + d[i + 2] * 0.11) * 0.6 + 20);
        d[i] = d[i + 1] = d[i + 2] = l;
      }
      c.g.putImageData(id, 0, 0);
    } else {
      c = G.mkCanvas(w, h);
      c.g.drawImage(im, 0, 0);
      c.g.globalCompositeOperation = 'source-in';
      c.g.fillStyle = '#0a0610'; c.g.fillRect(0, 0, w, h);
    }
    variants.set(key, c);
    return c;
  }
  // 条（带黑底框与高光）
  function bar(g, x, y, w, h, k, col, back = '#2a2030') {
    k = clamp01(k);
    g.fillStyle = '#0c0a14'; g.fillRect(x - 1, y - 1, w + 2, h + 2);
    g.fillStyle = back; g.fillRect(x, y, w, h);
    g.fillStyle = col; g.fillRect(x, y, Math.round(w * k), h);
    if (h >= 3) { g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(x, y, Math.round(w * k), 1); }
  }
  function star(g, x, y, s, col) {
    x = Math.round(x); y = Math.round(y);
    g.fillStyle = col;
    g.fillRect(x - s * 2, y, s * 4 + 2, 2); g.fillRect(x, y - s * 2, 2, s * 4 + 2);
    g.fillStyle = '#fff'; g.fillRect(x, y, 2, 2);
  }
  // 残条：掉血后白色残条停 0.12 s、再 0.4 s 缩回
  const trails = new WeakMap();
  function trailOf(obj, k, dt) {
    let s = trails.get(obj);
    if (!s) { s = { v: k, from: k, hold: 0, u: 1 }; trails.set(obj, s); }
    if (k > s.v) { s.v = k; s.u = 1; }
    else if (k < s.v - 1e-6) {
      if (s.u >= 1) { s.from = s.v; s.u = 0; s.hold = 0.12; }
      if (s.hold > 0) s.hold -= dt;
      else { s.u = Math.min(1, s.u + dt / 0.4); s.v = Math.max(k, s.from + (k - s.from) * s.u); }
    }
    return s.v;
  }

  const hud = (G.hud = {
    on: false, boss: null, timer: null, gauge: null,
    combo: { n: 0, t: 0, word: null, pop: 0 },
    steps: null,
    energyFlashT: 0, stripA: 0, lastDone: 0, stepFlashT: 0, lastWorld: 0, objHit: new WeakMap(), _dt: 0,

    reset() {
      this.on = false; this.boss = null; this.timer = null; this.gauge = null; this.steps = null;
      this.combo = { n: 0, t: 0, word: null, pop: 0 };
      this.energyFlashT = 0; this.lastDone = 0; this.stepFlashT = 0;
    },
    // 连击：combat 每次我方命中调；word = 连打拟声（ORA / HORA / MUDA），'' = 只写「×N」，不给 = 「N HIT」
    comboHit(word) {
      const c = this.combo;
      c.n++; c.t = 0; c.pop = 0.1;
      c.word = word == null ? null : word;
    },
    // 能量满的那一刻（combat 调）：meter_full 一次 + 能量条右端闪光
    flashEnergy() {
      this.energyFlashT = 0.6;
      snd('meter_full', { vol: 0.8 });
    },
    // 顶部 HUD 占到哪一行（UI y），提示框躲开它
    topBottom() {
      if (!this.on) return 0;
      let y = 60 + (G.uifx && G.uifx.tagKey ? TAG_DY : 0);
      const Wd = W();
      const n = Wd && Wd.allies ? Wd.allies().length : 0;
      if (n) y = 94 + 30 * (n - 1) + (G.uifx && G.uifx.tagKey ? TAG_DY : 0);
      return y;
    },

    update(dt) {
      this._dt = dt;
      // 连击计时按 world 时钟（顿帧期间不归零），60f 没打中归零
      const now = G.clk ? G.clk.world : 0;
      const dw = Math.max(0, Math.min(0.1, now - this.lastWorld));
      this.lastWorld = now;
      const c = this.combo;
      if (c.n > 0) { c.t += dw; if (c.t >= 1.0) { c.n = 0; c.word = null; } }
      if (c.pop > 0) c.pop = Math.max(0, c.pop - dt);
      if (this.energyFlashT > 0) this.energyFlashT = Math.max(0, this.energyFlashT - dt);
      if (this.steps) {
        if (this.steps.done > this.lastDone) this.stepFlashT = 0.3;
        this.lastDone = this.steps.done;
      } else this.lastDone = 0;
      if (this.stepFlashT > 0) this.stepFlashT = Math.max(0, this.stepFlashT - dt);
      const Wd = W();
      const party = G.party && G.party.members ? G.party.members : [];
      const want = !this.on && Wd && Wd.stage && Wd.free && !(G.S && G.S.busy) && !Wd.combat && !Wd.insert && party.length >= 2 &&
        !(G.ui && G.ui.letterbox > 1);
      this.stripA = clamp01(this.stripA + (want ? dt : -dt) * 6);
    },

    draw(g) {
      g.imageSmoothingEnabled = false;
      if (this.stripA > 0) this.drawStrip(g, this.stripA);
      if (!this.on) return;
      const Wd = W();
      const dy = G.uifx && G.uifx.tagKey ? TAG_DY : 0;
      const p = Wd && Wd.player;
      if (p) this.drawLeader(g, p, dy);
      this.drawAllies(g, dy);
      if (this.steps) this.drawSteps(g);
      else if (this.boss) this.drawBoss(g);
      this.drawTimerGauge(g);
      this.drawCombo(g);
    },

    // ------------------------------------------------------------ 队长面板
    drawLeader(g, p, dy) {
      const F = f16(), dt = this._dt;
      const y0 = 8 + dy;
      box(g, 8, y0, 256, y0 + 52);
      const k = p.maxHp ? p.hp / p.maxHp : 0;
      const im = headImg(p.cid, k < LOW && hasHead(p.cid, 'hurt') ? 'hurt' : 'normal');
      if (im) {
        g.fillStyle = '#282446'; g.fillRect(13, y0 + 5, 34, 34);
        g.save(); g.beginPath(); g.rect(14, y0 + 6, 32, 32); g.clip();
        const sh = k < LOW ? Math.round(Math.sin(G.clk.ui * 40)) : 0;
        g.drawImage(im, 0, 0, 32, 32, 14 + sh, y0 + 6, 32, 32);
        g.restore();
      }
      F.draw(g, nameOf(p), 54, y0 + 3, '#fff', { outline: '#000' });
      // HP
      const tr = trailOf(p, k, dt);
      g.fillStyle = '#0c0a14'; g.fillRect(53, y0 + 23, 194, 8);
      g.fillStyle = '#2a2030'; g.fillRect(54, y0 + 24, 192, 6);
      g.fillStyle = '#ffffff'; g.fillRect(54, y0 + 24, Math.round(192 * clamp01(tr)), 6);
      const low = k < LOW;
      const hpCol = low ? (Math.floor(G.clk.ui * 4) % 2 ? '#ff6040' : '#ff8a60') : '#e8c440';
      g.fillStyle = hpCol; g.fillRect(54, y0 + 24, Math.round(192 * clamp01(k)), 6);
      g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(54, y0 + 24, Math.round(192 * clamp01(k)), 1);
      f12().draw(g, Math.max(0, Math.ceil(p.hp)) + '/' + p.maxHp, 246, y0 + 6, low ? '#ff9a80' : '#cfc8dc', { align: 'right', outline: '#000' });
      // 能量（替身光环色；满了 2 Hz 闪 + 右端闪光 + 小星星）
      const aura = auraOf(p);
      const ek = p.energyMax ? (p.energy || 0) / p.energyMax : 0;
      const full = ek >= 1;
      const ecol = full && Math.floor(G.clk.ui * 4) % 2 ? mix(aura, '#ffffff', 0.5) : aura;
      bar(g, 54, y0 + 34, 192, 5, ek, ecol, '#1c1430');
      for (let i = 1; i < 4; i++) { g.fillStyle = 'rgba(0,0,0,0.45)'; g.fillRect(54 + i * 48, y0 + 34, 1, 5); }
      if (full) {
        const t = G.clk.ui;
        const s = Math.round(2 + Math.sin(t * 9) * 1.5);
        star(g, 246, y0 + 36, Math.max(1, s), mix(aura, '#ffffff', 0.4));
        for (let i = 0; i < 5; i++) {
          const ph = (t * 1.6 + i * 0.37) % 1;
          if (ph > 0.6) continue;
          const sx = 54 + ((i * 53 + Math.floor(t * 1.6 + i * 0.37) * 37) % 192), sy = y0 + 36 - Math.round(ph * 10);
          star(g, sx, sy, 1, '#fff');
        }
        f12().draw(g, 'U', 251, y0 + 30, Math.floor(t * 4) % 2 ? '#ffe040' : '#fff', { outline: '#3a1a60' });
      }
      if (this.energyFlashT > 0) {
        g.fillStyle = 'rgba(255,255,255,' + (this.energyFlashT / 0.6 * 0.8).toFixed(3) + ')';
        g.fillRect(53, y0 + 33, 194, 7);
      }
      // 剧情专用 U 的提示窗口开着：能量条右边写「按 U！」（f12 金字）
      const fight = W() && W().fight;
      if (fight && fight.storyU) {
        const sp = fight.spec && fight.spec.kitOverride && fight.spec.kitOverride[p.cid] && fight.spec.kitOverride[p.cid].special;
        const prompt = (sp && sp.prompt) || '按 U！';
        f12().draw(g, prompt, 262, y0 + 30, Math.floor(G.clk.ui * 4) % 2 ? '#ffd040' : '#fff4c0', { outline: '#3a1a00' });
      }
    },
    // ------------------------------------------------------------ 队伍行（战斗参战的其他人）
    drawAllies(g, dy) {
      const Wd = W();
      if (!Wd || !Wd.allies) return;
      const list = Wd.allies().filter((a) => a && a !== Wd.player);
      const swap = !!(Wd.fight && Wd.fight.swap);
      let qMarked = false;
      list.forEach((a, i) => {
        const x = 8, y = 66 + 30 * i + dy;
        box(g, x, y, x + 172, y + 28, { fill: 'rgba(14,12,30,0.82)' });
        const down = a.state === 'down';
        const im = headImg(a.cid, 'normal');
        if (im) {
          g.save(); g.beginPath(); g.rect(x + 4, y + 3, 24, 22); g.clip();
          g.drawImage(down ? variant(im, 'gray') : im, x + 4 - 4, y + 3 - 2);
          g.restore();
        }
        f12().draw(g, nameOf(a), x + 30, y + 3, down ? '#8a8498' : '#cfe8ff', { outline: '#000' });
        if (down) f12().draw(g, '倒地', x + 140, y + 3, '#ff9a8a', { outline: '#000', align: 'right' });
        else bar(g, x + 30, y + 18, 100, 3, a.maxHp ? a.hp / a.maxHp : 0, '#7ac8ff');
        if (a.energyMax && a.energy >= a.energyMax) { g.fillStyle = Math.floor(G.clk.ui * 4) % 2 ? auraOf(a) : '#fff'; g.fillRect(x + 134, y + 17, 4, 4); }
        if (swap && !down && !qMarked && a.leadable !== false) {
          qMarked = true;
          f12().draw(g, 'Q', x + 160, y + 8, '#ffe040', { outline: '#3a1a00', align: 'center' });
        }
      });
    },
    // ------------------------------------------------------------ Boss 条（阶段刻度）
    drawBoss(g) {
      const b = this.boss;
      if (!b || b.remove) return;
      const F = f16(), dt = this._dt;
      const name = b.name || (G.D && G.D.chars && G.D.chars[b.cid] && G.D.chars[b.cid].name) || b.cid || '';
      // 左上 VS 小标签（宽 220–250、画在 x 8）在时，条的左端会被标签盖住，血量低于 ~20% 就整条看不见：条改从标签右边开始，右端不动
      const vsd = G.uifx && G.uifx.tagKey && G.D && G.D.ui && G.D.ui.vs && G.D.ui.vs[G.uifx.tagKey];
      const x = vsd && vsd.tag ? Math.max(170, 8 + vsd.tag.w + 10) : 170, y = 30, w = 470 - x, h = 8;
      F.draw(g, name, x + w / 2, 8, '#ffd0d0', { align: 'center', outline: '#200810' });
      const k = b.maxHp ? clamp01(b.hp / b.maxHp) : 0;
      const tr = trailOf(b, k, dt);
      g.fillStyle = '#0c0a14'; g.fillRect(x - 2, y - 2, w + 4, h + 4);
      g.fillStyle = '#2a1018'; g.fillRect(x, y, w, h);
      g.fillStyle = '#fff'; g.fillRect(x, y, Math.round(w * tr), h);
      const broken = b.breakT > 0 || b.state === 'broken';
      g.fillStyle = broken ? (Math.floor(G.clk.ui * 8) % 2 ? '#ffd83c' : '#e83040') : '#e83040';
      g.fillRect(x, y, Math.round(w * k), h);
      g.fillStyle = 'rgba(255,255,255,0.3)'; g.fillRect(x, y, Math.round(w * k), 2);
      g.fillStyle = 'rgba(0,0,0,0.3)'; g.fillRect(x, y + h - 2, Math.round(w * k), 2);
      const phases = b.phases || [];
      for (const ph of phases) {
        if (typeof ph.at !== 'number') continue;
        const px = x + Math.round(w * ph.at);
        g.fillStyle = '#fff'; g.fillRect(px, y - 3, 1, h + 6);
        g.fillStyle = '#0c0a14'; g.fillRect(px + 1, y - 3, 1, h + 6);
      }
      if (broken) f12().draw(g, '破绽！', x + w + 6, y - 3, '#ffd83c', { outline: '#3a0a00' });
      // 韧性（有上限的 Boss）：条下一道细线
      if (b.poiseMax > 0) {
        const pk = clamp01((b.poise || 0) / b.poiseMax);
        g.fillStyle = '#0c0a14'; g.fillRect(x - 1, y + h + 2, w + 2, 3);
        g.fillStyle = '#c8b070'; g.fillRect(x, y + h + 3, Math.round(w * pk), 1);
      }
    },
    // ------------------------------------------------------------ 教学进度格（代替 Boss 条）
    drawSteps(g) {
      const s = this.steps, F = f16();
      // 队长面板占 x 8–256：格子和标题都从 264 往右放，不压面板右端的血量数字和血条
      const n = s.n || 0, cw = 24, gap = 4;
      const tw = n * cw + (n - 1) * gap, x0 = Math.max(264, Math.round((UW - tw) / 2)), y = 30;
      const lw = F.width ? F.width(s.label || '') : 0;
      F.draw(g, s.label || '', Math.max(x0 + tw / 2, 264 + lw / 2), 8, '#ffe9a8', { align: 'center', outline: '#200810' });
      for (let i = 0; i < n; i++) {
        const x = x0 + i * (cw + gap);
        g.fillStyle = '#0c0a14'; g.fillRect(x - 1, y - 1, cw + 2, 10);
        const lit = i < (s.done || 0);
        g.fillStyle = lit ? '#ffd83c' : '#2a2030'; g.fillRect(x, y, cw, 8);
        if (lit) { g.fillStyle = 'rgba(255,255,255,0.4)'; g.fillRect(x, y, cw, 2); }
        if (lit && i === s.done - 1 && this.stepFlashT > 0) { g.fillStyle = 'rgba(255,255,255,' + (this.stepFlashT / 0.3).toFixed(3) + ')'; g.fillRect(x - 1, y - 1, cw + 2, 10); }
        if (!lit && i === (s.done || 0)) { g.fillStyle = Math.floor(G.clk.ui * 3) % 2 ? 'rgba(255,216,60,0.5)' : 'rgba(255,216,60,0.2)'; g.fillRect(x, y, cw, 8); }
      }
    },
    // ------------------------------------------------------------ 计时 / 环境槽（右上）
    drawTimerGauge(g) {
      const S = tsafe();
      const oy = S && S.sys < UW - 2 ? 34 : 0;
      const Wd = W();
      if (this.timer && Wd) {
        const left = Math.max(0, Math.ceil(this.timer.until - (Wd.fightT || 0)));
        box(g, 472, 8 + oy, 632, 34 + oy);
        f16().draw(g, (this.timer.label || '') + left + ' 秒', 552, 13 + oy, left <= 5 ? '#ffd34a' : '#fff', { align: 'center', outline: '#000' });
      }
      const ga = this.gauge;
      if (ga) {
        const y = (this.timer ? 40 : 8) + oy;
        box(g, 472, y, 632, y + 26);
        f12().draw(g, ga.label || '', 482, y + 4, '#e8e0f0', { outline: '#000' });
        const gk = ga.max ? ga.value / ga.max : 0;
        f12().draw(g, Math.round(gk * 100) + '%', 622, y + 4, '#cfc8dc', { outline: '#000', align: 'right' });
        bar(g, 482, y + 18, 140, 4, gk, ga.color || '#7ac8ff');
      }
    },
    // ------------------------------------------------------------ 连击数（UI (560, 120) 右对齐；位图字 f16 ×2）
    drawCombo(g) {
      const c = this.combo;
      if (c.n < 2) return;
      const S = tsafe();
      const xr = S && S.sys ? Math.min(560, S.sys - 8) : 560;
      const y = S && S.sys < UW - 2 ? 150 : 120;
      const gold = c.n >= 20;
      const numCol = gold ? '#ffd040' : '#ffffff';
      const big = c.word != null ? (c.word ? c.word + ' ×' + c.n : '×' + c.n) : String(c.n);
      const im = f16().bake(big, numCol, { outline: gold ? '#3a1a00' : '#1a1030' });
      const sc = 2 + (c.pop > 0 ? c.pop / 0.1 * 0.6 : 0);
      const jx = c.n >= 50 ? Math.round(Math.random() * 2 - 1) : 0, jy = c.n >= 50 ? Math.round(Math.random() * 2 - 1) : 0;
      const w = Math.round(im.width * sc), h = Math.round(im.height * sc);
      const a = clamp01((1.0 - c.t) / 0.25);
      g.save();
      g.globalAlpha = a;
      g.imageSmoothingEnabled = false;
      if (c.word == null) {
        const hit = f16().bake('HIT', '#ffe9a8', { outline: '#1a1030' });
        g.drawImage(hit, xr - hit.width + jx, y + h - hit.height - 2 + jy);
        g.drawImage(im, Math.round(xr - hit.width - 4 - w) + jx, y + Math.round((im.height * 2 - h) / 2) + jy, w, h);
      } else g.drawImage(im, Math.round(xr - w) + jx, y + Math.round((im.height * 2 - h) / 2) + jy, w, h);
      // 计时细条（快断了会变红）
      g.fillStyle = c.t > 0.7 ? '#ff6040' : 'rgba(255,255,255,0.7)';
      g.fillRect(Math.round(xr - 60), y + 38, Math.round(60 * clamp01(1 - c.t)), 2);
      g.restore();
    },
    // ------------------------------------------------------------ 探索头像条（自由走动、队伍 ≥ 2 人）
    drawStrip(g, alpha) {
      const party = (G.party && G.party.members) || [];
      const Wd = W();
      const leader = Wd && Wd.player;
      g.save();
      g.globalAlpha = alpha;
      party.forEach((a, i) => {
        const x = 8 + 32 * i, y = 8;
        const isL = a === leader;
        g.fillStyle = isL ? '#ffd83c' : '#0c0a14'; g.fillRect(x - 2, y - 2, 32, 32);
        g.fillStyle = isL ? '#3a2a00' : '#3a3450'; g.fillRect(x - 1, y - 1, 30, 30);
        g.fillStyle = '#1c1830'; g.fillRect(x, y, 28, 28);
        const im = headImg(a.cid, 'normal');
        const look = a.look || (a.leadable === false ? 'gray' : null);
        if (im) {
          const src = look === 'gray' ? variant(im, 'gray') : look === 'unknown' ? variant(im, 'sil') : im;
          g.drawImage(src, 2, 2, 28, 28, x, y, 28, 28);
        }
        if (look === 'unknown') f16().draw(g, '？', x + 14, y + 6, '#fff', { align: 'center', outline: '#000' });
        if (a.mem && a.mem.bandage && a.mem.away) {
          g.fillStyle = '#eee9d9'; g.fillRect(x + 2, y + 9, 24, 6);
          g.fillStyle = '#c6bdab'; g.fillRect(x + 2, y + 11, 24, 1); g.fillRect(x + 18, y + 9, 1, 6);
        }
        if (isL) { g.fillStyle = '#ffd83c'; g.fillRect(x + 10, y + 30, 8, 2); }
      });
      if (party.length) {
        const can = !(G.party && G.party.canSwap) || G.party.canSwap();
        f12().draw(g, 'Q 换', 8 + 32 * party.length + 2, 17, can ? '#ffe9a8' : '#6a6478', { outline: '#000' });
      }
      g.restore();
    },

    // ================================================================ 头顶标记（世界坐标 → UI；插入画面时不画）
    drawMarks(g) {
      const Wd = W();
      if (!Wd || !Wd.stage || Wd.insert) return;
      const st = Wd.stage;
      const t = G.clk.ui;
      const F = f16();
      for (const a of st.actors || []) {
        if (!a || a.visible === false || a.remove) continue;
        const hp = w2u(a.x, headY(a), 0);
        // 表情（emote = { text, t, color }）
        if (a.emote && a.emote.text) {
          const bounce = Math.round(Math.abs(Math.sin(t * 9)) * 2);
          F.draw(g, a.emote.text, hp.x, hp.y - 32 - bounce, a.emote.color || '#ffe14a', { align: 'center', outline: '#1a1020' });
        }
        // 小血条：非 Boss 敌人（战斗中）；可破坏物挨打后 2 s
        const isObj = a.team === 'object';
        let show = false;
        if (a.team === 'enemy' && !a.boss && !a.dead && Wd.combat && a.maxHp) show = true;
        if (isObj && a.maxHp) {
          const rec = this.objHit.get(a);
          if (!rec) this.objHit.set(a, { hp: a.hp, t: -9 });
          else if (a.hp < rec.hp) { rec.hp = a.hp; rec.t = t; }
          if (rec && t - rec.t < 2 && a.hp > 0) show = true;
        }
        if (show) bar(g, Math.round(hp.x - 20), Math.round(hp.y - 10), 40, 4, a.hp / a.maxHp, '#ff5050');
      }
      // 互动提示（W.near：{ actor | hot, label, x, top }）
      const busy = G.S && G.S.busy;
      const lookH = !busy && Wd.free && G.party && G.party.lookReady && G.party.lookReady() && Wd.findLook ? Wd.findLook() : null;
      const n = Wd.near;
      let nearIsLook = false;
      if (n && Wd.free && !busy && !Wd.combat) {
        const label = n.label || (n.actor && (n.actor.label || n.actor.name)) || (n.hot && n.hot.label) || '';
        const nx = n.x != null ? n.x : n.actor ? n.actor.x : n.hot ? (n.hot.lx != null ? n.hot.lx : n.hot.x) : 0;
        const ny = n.top != null ? n.top : n.actor ? headY(n.actor) : n.hot ? (n.hot.ly != null ? n.hot.ly : n.hot.y - 40) : 0;
        const p = w2u(nx, ny, 0);
        const fl = Math.round(Math.abs(Math.sin(t * 4 * Math.PI)) * 2);   // 4 Hz 上下浮 2 px
        nearIsLook = !!(lookH && n.hot && n.hot === lookH);
        this.drawPrompt(g, p.x, p.y - 22 - fl, label, nearIsLook || !!(lookH && !n.hot));
      }
      if (lookH && !nearIsLook && !(n && Wd.free)) {
        const p = w2u(lookH.lx != null ? lookH.lx : lookH.x, lookH.ly != null ? lookH.ly : lookH.y - 40, 0);
        this.drawUBadge(g, p.x - 7, p.y - 30 - Math.round(Math.abs(Math.sin(t * 3)) * 3), true);
      }
    },
    drawPrompt(g, x, y, label, withU) {
      const F = f16();
      const w = F.width(label) + 26;
      const x0 = Math.round(x - w / 2), y0 = Math.round(y - 12);
      g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(x0 + 2, y0 + 2, w, 22);
      g.fillStyle = 'rgba(14,12,30,0.88)'; g.fillRect(x0, y0, w, 22);
      g.fillStyle = '#fff'; g.fillRect(x0, y0, w, 1); g.fillRect(x0, y0 + 21, w, 1); g.fillRect(x0, y0, 1, 22); g.fillRect(x0 + w - 1, y0, 1, 22);
      if (G.ui && G.ui.glyph) G.ui.glyph(g, 'down', x0 + 6, y0 + 9, '#ffd34a');
      F.draw(g, label, x0 + 18, y0 + 3, '#fff');
      if (withU) this.drawUBadge(g, x0 + w + 3, y0 + 3, false);
    },
    drawUBadge(g, x, y, big) {
      const s = big ? 16 : 14;
      const on = Math.floor(G.clk.ui * 4) % 2 === 0;
      g.fillStyle = '#0c0a14'; g.fillRect(x - 1, y - 1, s + 2, s + 2);
      g.fillStyle = on ? '#c08aff' : '#9a6ae0'; g.fillRect(x, y, s, s);
      g.fillStyle = 'rgba(255,255,255,0.4)'; g.fillRect(x, y, s, 1);
      f12().draw(g, 'U', x + s / 2, y + Math.round((s - 13) / 2) + 1, '#fff', { align: 'center', outline: '#2a0a4a' });
    },
  });
})();
