// 自动测试的状态快照 G.dbg.snapshot()（字段定死，技术约定 §6.2）+ 调试快捷键（只在 ?autotest=1 / ?debug=1 时）
//   每一段都包在 try 里：别的包的字段晚到 / 改名时，快照照样能拿到，只是那一段是 null（不让测试脚本因为一个字段报错停下）。
'use strict';
(function () {
  const G = window.G;
  const r1 = (v) => (typeof v === 'number' && isFinite(v) ? Math.round(v * 10) / 10 : v == null ? null : v);
  const ri = (v) => (typeof v === 'number' && isFinite(v) ? Math.round(v) : null);
  const r3 = (v) => (typeof v === 'number' && isFinite(v) ? Math.round(v * 1000) / 1000 : null);
  const arr = (s) => (s ? Array.from(s) : []);
  const safe = (f, dflt = null) => { try { const v = f(); return v === undefined ? dflt : v; } catch (e) { return dflt; } };

  const TIER_KIND = { W1: 'emote', W2: 'heavy', W3: 'zone', W4: 'line', W5: 'unblockable', W6: 'cutin' };
  const moveOf = (m) => (m && typeof m === 'object' ? m : (m && G.MOVES ? G.MOVES[m] : null));
  const moveId = (m) => {
    if (!m) return null;
    if (typeof m === 'string') return m;
    if (m.id) return m.id;
    if (G.MOVES) for (const k in G.MOVES) if (G.MOVES[k] === m) return k;
    return null;
  };
  // 预警剩余秒：combat.js 的 G.AI.tele 建 { t: 0, dur, elapsed }，每帧 tele.t += dt（已过秒数，不是开始时刻）。
  // 以前按“开始时刻”猜，clk.world 小的时候（开局几秒、夹具）会算错；tele.left 有就优先用。
  function teleLeft(tele) {
    if (!tele) return -1;
    if (typeof tele.left === 'number') return Math.max(0, tele.left);
    const dur = tele.dur || 0;
    const el = typeof tele.t === 'number' ? tele.t : 0;
    return Math.max(0, dur - el);
  }
  // 预警结束到判定帧还差多少：预警结束时 startMove 把 atkT 设成 tele.elapsed（预警已经算进前摇），
  // 所以还剩 active[0] - elapsed；elapsed 没给时按 0（整段前摇都在预警之后）。
  function teleStartupLeft(tele, m) {
    if (!m || !m.active) return 0;
    const el = typeof tele.elapsed === 'number' ? tele.elapsed : 0;
    return Math.max(0, m.active[0] - el);
  }
  function pt(v) {
    if (!v) return null;
    if (Array.isArray(v)) return [ri(v[0]), ri(v[1])];
    if (typeof v.x === 'number') return [ri(v.x), ri(v.y)];
    return null;
  }

  function enemyRow(e) {
    const tele = e.tele || null;
    const left = tele ? teleLeft(tele) : -1;
    const tier = tele ? tele.tier || (moveOf(tele.move) && moveOf(tele.move).warn && moveOf(tele.move).warn.tier) || null : null;
    let target = null;
    if (tele) {
      if (Array.isArray(tele.path) && tele.path.length) target = pt(tele.path[tele.path.length - 1]);
      else target = pt(tele.target);
    }
    let hitIn = -1;
    if (tele) {
      hitIn = left + teleStartupLeft(tele, moveOf(tele.move));
    } else if (e.atk) {
      const m = moveOf(e.atk);
      if (m && m.active && typeof e.atkT === 'number' && e.atkT < m.active[0]) hitIn = m.active[0] - e.atkT;
    }
    return [e.id, ri(e.x), ri(e.y), ri(e.z || 0), ri(e.hp), ri(e.maxHp), e.state || null, r3(left), tier,
      tier ? TIER_KIND[tier] || null : null, tele ? moveId(tele.move) : null, target, r3(hitIn),
      !!e.boss, !!e.untargetable, r3(e.rootT || 0), r3(e.breakT || 0), e.uid != null ? e.uid : null];
  }

  function warnRows(W) {
    const out = [];
    for (const e of safe(() => W.enemies(), [])) {
      const tele = e.tele;
      if (!tele) continue;
      const left = teleLeft(tele);
      const m = moveOf(tele.move);
      const tier = tele.tier || (m && m.warn && m.warn.tier) || null;
      const kind = tier ? TIER_KIND[tier] || null : null;
      if (Array.isArray(tele.path) && tele.path.length >= 2) {
        const a = tele.path[0], b = tele.path[tele.path.length - 1];
        const row = [tier, kind, ri(a[0]), ri(a[1]), ri(b[0]), ri(b[1]), r3(left)];
        if (tele.path.length === 3) row.push(ri(tele.path[1][0]), ri(tele.path[1][1]));
        out.push(row);
      } else {
        const tg = pt(tele.target) || [ri(e.x), ri(e.y)];
        out.push([tier, kind, ri(e.x), ri(e.y), tg[0], tg[1], r3(left)]);
      }
    }
    for (const h of safe(() => W.hazards, []) || []) {
      const wl = hazWarnLeft(h);
      if (wl == null || wl <= 0 || h.hidden) continue;
      const b = hazBox(h);
      out.push([h.warnTier || 'W3', 'zone', b[0], b[2], b[1], b[3], r3(wl)]);
    }
    return out;
  }
  function hazBox(h) {
    if (typeof h.x0 === 'number') return [ri(h.x0), ri(h.x1), ri(h.y0), ri(h.y1)];
    const x = h.follow ? h.follow.x : h.x, y = h.follow ? h.follow.y : h.y;
    const rx = h.rx || 10, ry = h.ry || rx / 2;
    return [ri(x - rx), ri(x + rx), ri(y - ry), ri(y + ry)];
  }
  // combat.hazard 的计时字段：h.t（已过秒数，含 delay）、h.delay、h.warn、h.dur，h.phase = 'warn' | 'active' | 'done'。
  // 以前读不存在的 h.age / h.active，预警剩余永远是 null、active 永远是 false。
  function hazWarnLeft(h) {
    if (typeof h.warnLeft === 'number') return h.warnLeft;
    const el = typeof h.t === 'number' ? h.t : typeof h.age === 'number' ? h.age : null;
    if (el == null) return null;
    return Math.max(0, (h.delay || 0) + (h.warn || 0) - el);
  }
  function hazActive(h) {
    if (typeof h.active === 'boolean') return h.active;
    if (typeof h.phase === 'string') return h.phase === 'active';
    const wl = hazWarnLeft(h);
    return wl != null ? wl <= 0 : false;
  }

  function dlgText(d) {
    if (!d) return null;
    const name = d.name || '';
    let body = '';
    if (Array.isArray(d.pages)) body = d.pages.map((p) => (Array.isArray(p) ? p.join('') : String(p))).join('');
    else if (d.text != null) body = String(d.text);
    return name ? name + '：' + body : body;
  }
  function pageLen(d) {
    if (!d) return 0;
    if (Array.isArray(d.pages)) { const p = d.pages[d.page || 0]; return Array.isArray(p) ? p.join('').length : String(p || '').length; }
    return d.text ? String(d.text).length : 0;
  }

  G.dbg.snapshot = function () {
    const W = G.world || {}, U = G.ui || {}, S = G.S || {}, st = W.stage || null, p = W.player || null;
    const f = W.fight || null;
    const out = {};
    out.scene = safe(() => (G.scene ? G.scene.name || 'other' : null));
    out.stage = st ? st.id : null;
    out.x0 = st ? ri(st.x0) : null;
    out.x1 = st ? ri(st.x1) : null;
    out.free = !!W.free; out.busy = !!S.busy; out.combat = !!W.combat; out.cine = !!W.cine;
    Object.assign(out, safe(() => ({
      leader: p ? p.cid : null, px: p ? ri(p.x) : null, py: p ? ri(p.y) : null, pz: p ? ri(p.z || 0) : 0, pfacing: p ? p.facing : 1,
      pstate: p ? p.state : null, hp: p ? ri(p.hp) : null, maxHp: p ? ri(p.maxHp) : null, energy: p ? ri(p.energy) : null,
      energyMax: p ? ri(p.energyMax || 100) : null, iframe: p ? r3(p.iframe || 0) : 0, dodgeCd: p ? r3(p.dodgeCd || 0) : 0,
      standMode: p && p.stand ? p.stand.mode : null, rootT: p ? r3(p.rootT || 0) : 0,
    }), {}));
    out.party = safe(() => (G.party.members || []).map((a) => [a.cid, ri(a.hp), ri(a.maxHp), a.state, ri(a.energy), a.team, a.leadable !== false]), []);
    out.leaderCanInvestigate = safe(() => !!G.party.lookReady(), false);
    out.fightId = f && f.spec ? f.spec.id || null : null;
    out.fightSwap = f ? !!(f.swap != null ? f.swap : f.spec && f.spec.swap) : false;
    out.fightT = r1(W.fightT || 0);
    out.fightLosable = f && f.spec ? (f.spec.losable != null ? !!f.spec.losable : !(f.spec.playerMinHp > 0)) : null;
    out.fightCoverage = f && f.spec ? f.spec.coverage !== false : null;
    out.assist = f ? !!f.assist : false;
    out.storyU = f ? !!f.storyU : false;
    out.fightHint = safe(() => (f && f.spec && typeof f.spec.testHint === 'function' ? f.spec.testHint(f) : null));
    // 调试数据只保留小游戏的值，避免 Actor / Canvas 的循环引用污染快照。
    const primitive = (v, depth = 0) => {
      if (v == null || ['string', 'number', 'boolean'].includes(typeof v)) return v;
      if (depth > 3 || typeof v !== 'object' || v.cid || v.getContext) return undefined;
      if (Array.isArray(v)) return v.map(x => primitive(x, depth + 1));
      return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, primitive(x, depth + 1)]).filter(([, x]) => x !== undefined));
    };
    out.lateGame = safe(() => primitive(G.lateGame)); out.midGame = safe(() => primitive(G.midGame));
    out.steps = safe(() => (G.hud && G.hud.steps ? { n: G.hud.steps.n, done: G.hud.steps.done, label: G.hud.steps.label } : null));
    out.enemies = safe(() => W.enemies().map(enemyRow), []);
    out.warns = safe(() => warnRows(W), []);
    out.shots = safe(() => (W.shots || []).map((s) => [ri(s.x - (p ? p.x : 0)), ri(s.y - (p ? p.y : 0)), r1(s.vx || 0), s.side || (s.owner && s.owner.side ? s.owner.side() : null),
      s.reflect !== false, !!s.cuttable]), []);
    out.hazards = safe(() => (W.hazards || []).map((h) => { const b = hazBox(h); return [b[0], b[1], b[2], b[3], r3(hazWarnLeft(h)), hazActive(h), h.side || 'enemy', h.guard || 'normal', !!h.hidden]; }), []);
    out.objects = safe(() => W.objects().map((o) => [o.id, ri(o.x), ri(o.y), ri(o.hp), ri(o.maxHp), o.state === 'broken' || o.hp <= 0]), []);
    out.boss = safe(() => (G.hud && G.hud.boss ? { name: G.hud.boss.name, hp: ri(G.hud.boss.hp), maxHp: ri(G.hud.boss.maxHp), phase: G.hud.boss.phaseI || 0 } : null));
    out.combo = safe(() => (G.hud && G.hud.combo ? G.hud.combo.n : 0), 0);
    // 快照和界面读取同一份状态，避免把方法名当状态字段。
    Object.assign(out, safe(() => U.state(), {}));
    out.chapter = !!(S.cardOn || out.chapter);
    out.insert = !!(W.insert || U.insertUI);
    out.video = out.scene === 'video';
    out.timer = safe(() => (G.hud && G.hud.timer ? Math.round(G.hud.timer.until - (W.fightT || 0)) : null));
    out.gauge = safe(() => (G.hud && G.hud.gauge ? { id: G.hud.gauge.id, value: ri(G.hud.gauge.value), max: ri(G.hud.gauge.max) } : null));
    out.near = safe(() => {
      const n = W.near;
      if (!n) return null;
      return n.label || (n.hot && n.hot.label) || (n.actor && (n.actor.label || n.actor.name)) || null;
    });
    out.npcs = safe(() => (st ? st.actors.filter((a) => a.talk && a.visible !== false && !a.remove).map((a) => [a.label || a.name || a.id, ri(a.x), ri(a.y)]) : []), []);
    out.hotspots = safe(() => (st ? (st.hotspots || []).filter((h) => !h.hidden && (!h.cond || h.cond())).map((h) => [h.label || h.id, ri(h.x), ri(h.y), h.tags || []]) : []), []);
    out.ts = safe(() => (G.time && G.time.active ? G.time.phase : null));
    out.flags = G.flags || {};
    out.fade = r3(G.fadeA || 0);
    out.okLocked = safe(() => (G.input && typeof G.input.okLockUntil === 'number' ? G.clk.ui < G.input.okLockUntil : false), false);
    out.ctitle = safe(() => (G.curChapter != null && G.CHAPTERS && G.CHAPTERS[G.curChapter] ? G.CHAPTERS[G.curChapter].title : null));
    out.dbgShot = G.dbg.shot || null;
    out.counts = Object.assign({}, G.dbg.counts || {});
    out.fallbacks = arr(G.dbg.animFallbacks);
    out.missingImg = arr(G.dbg.missingImg);
    out.missingSfx = arr(G.dbg.missingSfx);
    out.missingGlyph = arr(G.dbg.missingGlyph);
    out.missingHead = arr(G.dbg.missingHead);
    out.fps = G.dbg.fps || null;
    // 以下是快照的附加字段（§6.2 之外，测试用）：最近 400 条事件里的几类计数、替身调查统计（story\common.js 记）
    out.evTotals = safe(() => {
      const t = { look_missing: 0, script_error: 0, video_missing: 0, api_missing: [] };
      for (const e of G.dbg.events || []) {
        if (e.type === 'api_missing') { if (t.api_missing.indexOf(e.name) < 0) t.api_missing.push(e.name); } else if (e.type in t) t[e.type]++;
      }
      return t;
    }, null);
    out.lookStats = safe(() => (G.LOOK && G.LOOK.stats ? JSON.parse(JSON.stringify(G.LOOK.stats)) : null));
    return out;
  };

  // 调试快捷键（?debug=1）：F2 跳到下一个战斗结束（赢）、F4 存档跳章（只在调试时挂，正常游玩不加任何监听）
  try {
    const q = (location && location.search) || '';
    if (/[?&]debug=1/.test(q)) {
      addEventListener('keydown', (e) => {
        if (e.key === 'F2' && G.world && G.world.fight && typeof G.world.fight.end === 'function') { G.world.fight.end(); e.preventDefault(); }
        if (e.key === 'F4' && G.progress) { G.progress.reach(G.CHAPTERS.length - 1); e.preventDefault(); }
      });
    }
  } catch (e) { /* 没有 location（桩环境） */ }
})();
