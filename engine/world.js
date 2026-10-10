// 世界（包 4）：Actor、Stage、G.world（更新顺序、镜头、互动 / 触发 / 替身调查入口、影子、纵深排序绘制、残影、插入画面、时停 over pass）
'use strict';
(function () {
  const G = window.G;
  G.STAGES = {};

  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const dbgSet = (name, v) => { const d = G.dbg; if (d && d[name] && d[name].add) d[name].add(v); };
  const ev = (type, data) => { if (G.dbg && G.dbg.ev) G.dbg.ev(type, data); };
  const now = () => (G.clk ? G.clk.world : 0);
  const T = () => G.time || null;
  const frozenOf = (a) => { const t = T(); return !!(t && t.isFrozen && t.isFrozen(a)); };
  const overOn = () => { const t = T(); return !!(t && t.overActive && t.overActive()); };
  const sBusy = () => !!(G.S && G.S.busy);
  const uiBlocking = () => !!(G.ui && G.ui.blocking && G.ui.blocking());
  const run = (fn) => { if (G.S && G.S.run) G.S.run(fn).catch(G.cancelIgnore); };
  const FROZEN_OUTLINE = '#f0e8c0';
  const GHOST_LIFE = 0.25;

  let uidN = 0;

  // ------------------------------------------------------------------ 角色
  class Actor {
    constructor(cid, x = 0, y = 0, o = {}) {
      const D = G.D || {};
      const isProp = typeof cid === 'string' && (cid.indexOf('scene:') === 0 || cid.indexOf('prop:') === 0);
      const m = isProp ? null : (D.chars || {})[cid];
      const kit = o.kit && typeof o.kit === 'object' ? o.kit : G.KITS ? G.KITS[o.kit || cid] || null : null;
      const option = (key, fallback) => o[key] !== undefined ? o[key] : kit && kit[key] !== undefined ? kit[key] : fallback;
      // 身份
      this.uid = ++uidN;
      this.cid = cid;
      this.id = o.id || cid;
      this.atlas = G.atlas(cid);
      this.name = o.name || (m && m.name) || (D.heroes && D.heroes[cid] && D.heroes[cid].cn) || cid;
      // alt = 候选图集 cid（数组；写成单个字符串也认——以前字符串会在这里抛错，剧情 S.run 卡死）
      this.alt = [].concat(o.alt || []).filter((id) => typeof id === 'string' && D.chars && D.chars[id]).map((id) => G.atlas(id));
      this.team = o.team || 'npc';
      this.kit = kit;
      this.boss = !!o.boss;
      this.vip = !!o.vip;
      this.mem = {};
      // 位置
      this.x = x; this.y = y; this.z = o.z || 0;
      this.vx = 0; this.vy = 0; this.vz = 0;
      this.facing = o.facing || 1;
      this.scale = o.scale || 1;
      this.bodyW = o.bodyW || (m && m.bodyW) || 6;
      this.top = o.top || (m && m.top) || null;
      this.pivotMode = o.pivot === 'center' || o.pivotMode === 'center' ? 'center' : 'foot';
      this.fly = option('fly', null);
      this.laneOff = (G.rand ? G.rand(-5, 5) : 0);
      // 动画
      this.idleAnim = option('idleAnim', option('idle', o.anim || 'idle'));
      this.anim = this.idleAnim;
      this.animT = G.rand ? G.rand(0, 2) : 0;
      this.animSpeed = 1;
      this.frozen = null;
      this.skin = o.skin || null;
      this.hold = false;
      this.script = null;
      this.rot = 0;
      this.alpha = o.alpha == null ? 1 : o.alpha;
      this.visible = o.visible !== false;
      this.shadow = o.shadow == null ? !(typeof cid === 'string' && cid.indexOf('prop:') === 0) : !!o.shadow;
      this.shadowW = o.shadowW || 14 * this.scale;
      this.flash = 0;
      this.tint = o.tint || null;
      this.outline = null;
      this.auraFlame = null;
      this.ghostOn = false;
      this.ghosts = [];
      this.ghostColor = null;
      this.ownT = 0;
      // 互动
      this.talk = o.talk || null;
      this.label = o.label || null;
      this.talkRy = o.talkRy || 22;
      this.noTurn = !!o.noTurn;
      this.emote = null;
      this.onStand = o.onStand || null;
      this.standReact = o.standReact !== false;
      // 数值
      this.maxHp = this.hp = o.hp || (kit && kit.hp) || 100;
      this.energy = 0;
      this.energyMax = 100;
      this.minHp = o.minHp || 0;
      this.dmgMul = option('dmgMul', null);
      this.dmgIn = 1;
      this.dmgOut = o.dmgOut || 1;
      this.invuln = 0;
      this.iframe = 0;
      this.stopT = 0;
      this.slowK = 1;
      this.armor = option('armor', false);
      this.poise = 0;
      this.poiseMax = o.poiseMax || (kit && kit.poiseMax) || 0;
      this.breakT = 0;
      this.poiseIdleT = 0;
      this.chainT = 0;
      this.chainGapT = 0;
      this.untargetable = !!o.untargetable;
      this.hidden = false;
      // 控制效果
      this.rootT = 0;
      this.stunT = 0;
      this.burn = null;
      this.rootImmuneT = 0;
      this.rootBy = null;
      // 状态
      this.state = 'idle';
      this.stateT = 0;
      this.atk = null;
      this.atkT = 0;
      this.combo = -1;
      this.rush = null;
      this.rushCdT = 0;
      this.dodgeCd = 0;
      this.dodgeT0 = -Infinity;
      this.grazed = false;
      this.guardT = 0;
      this.guardRelT = 0;
      this.parryUntil = -Infinity;
      this.parryLockUntil = -Infinity;
      this.lastGuardPressT = -Infinity;
      this.firstParryDone = false;
      this.nextMul = 1;
      this.nextMulT = 0;
      this.hurtEnergyT = 0;
      this.tsGuard = false;
      this.cool = G.rand ? G.rand(0.6, 1.4) : 1;
      this.focus = null;
      this.focusT = 0;
      this.tele = null;
      this.downT = 0;
      this.dead = false;
      this.remove = false;
      this.koStyle = option('koStyle', o.boss ? 'ko' : 'fly');
      // 替身
      this.stand = null;
      this.standId = null;
      this.standPos = option('standPos', null);
      // 队伍
      this.follow = null;
      this.followSlot = 0;
      this.leadable = true;
      this.look = null;
      // AI
      this.moves = o.moves || (kit && kit.moves) || [];
      this.moveCd = {};
      this.pattern = o.pattern || (kit && kit.pattern) || null;
      this.patternI = 0;
      this.brain = o.brain || (kit && kit.brain) || null;
      this.range = o.range || 25;
      this.ranged = o.ranged || 0;
      this.noCharge = !!o.noCharge;
      this.speed = o.speed || (kit && kit.speed) || 72;
      this.phases = o.phases || null;
      this.phaseI = 0;
      this.onKo = o.onKo || null;
      this.koTo = o.koTo || null;
      this.koImpact = !!o.koImpact;
      this.targetPick = option('targetPick', null);
      this.onHitBy = option('onHitBy', null);
      this.onShotNear = option('onShotNear', null);
      this.evadeWord = o.evadeWord || '它躲开了！';
      this.breakable = o.breakable || null;
      // 替身：o.stand > kit.standId > heroes[cid].stand
      const sid = o.stand !== undefined ? o.stand : (kit && kit.standId) || (D.heroes && D.heroes[cid] && D.heroes[cid].stand) || null;
      if (sid) this.setStand(sid);
    }
    play(name, o = {}) {
      if (this.anim !== name || o.restart) { this.anim = name; this.animT = 0; this.frozen = null; }
      this.animSpeed = o.speed || 1;
    }
    // 附加图集（原片场景里的特殊动作）：本体没有、附加图集有（不经通用回退）的动作到那里找
    atlasFor(name) {
      if (this.alt.length) for (const at of this.alt) if (at.has(name, this.skin)) return at;
      return this.atlas;
    }
    frameIndex() {
      const at = this.atlasFor(this.anim);
      if (this.frozen != null) return Math.max(0, Math.min(at.frames(this.anim, this.skin) - 1, this.frozen | 0));
      return at.frameAt(this.anim, this.animT, this.animSpeed, this.skin);
    }
    animDone() { return this.atlasFor(this.anim).done(this.anim, this.animT, this.animSpeed, this.skin); }
    topPx() { return this.top != null ? this.top : this.atlas.topPx(); }
    headY() { return this.y - this.z - this.topPx() * this.scale; }
    side() { return this.team === 'player' || this.team === 'ally' ? 'good' : this.team; }
    ghostCol() {
      if (this.ghostColor) return this.ghostColor;
      if (this.stand) return this.stand.color;
      const S = (G.D && G.D.stands) || {};
      const h = G.D && G.D.heroes && G.D.heroes[this.cid];
      return (h && S[h.stand] && S[h.stand].aura) || '#ffffff';
    }
    _pivotDy() { return this.pivotMode === 'center' ? -(this.atlas.ch - this.atlas.py) * this.scale : 0; }
    // 残影（旧 → 新）：tint {ghostColor, 0.45} + dither 0.2 → 0.55，每个 0.25 s 淡掉
    drawGhosts(g, camX, camY) {
      const gs = this.ghosts, n = gs.length;
      if (!n || !this.visible) return;
      const col = this.ghostCol(), dy = this._pivotDy();
      for (let i = 0; i < n; i++) {
        const gh = gs[i], age = this.ownT - gh.t;
        if (age >= GHOST_LIFE || age < 0) continue;
        const base = n > 1 ? 0.2 + (0.55 - 0.2) * (i / (n - 1)) : 0.55;
        const dth = base * (1 - age / GHOST_LIFE);
        if (dth <= 0.03) continue;
        this.atlasFor(gh.anim).draw(g, gh.anim, gh.frame, gh.x - camX, gh.y - gh.z - camY + dy, {
          flip: gh.facing < 0, scale: gh.scale, skin: gh.skin, tint: { color: col, k: 0.45 }, dither: dth,
        });
      }
    }
    draw(g, camX, camY, o = {}) {
      if (!this.visible || this.alpha <= 0) return;
      if (o.ghosts !== false) this.drawGhosts(g, camX, camY);
      const wt = now();
      let sx = this.x - camX;
      const sy = this.y - this.z - camY + this._pivotDy();
      let alpha = this.alpha;
      if (this.invuln > 0 && (this.team === 'player' || this.team === 'ally') && Math.floor(wt * 20) % 2 === 0) alpha *= 0.45;
      if (this.iframe > 0 && this.state === 'dodge' && Math.floor(wt * 30) % 2 === 1) alpha *= 0.6;
      if (this.stopT > 0 && this.state === 'hurt') sx += Math.floor(wt * 30) % 2 ? 1 : -1;
      const at = this.atlasFor(this.anim), fr = this.frameIndex(), flip = this.facing < 0;
      if (this.auraFlame && G.fx && G.fx.auraFlame) {
        const r = G.fx.auraFlame(this.cid, this.anim, fr, flip, this.scale, this.ownT, this.auraFlame);
        if (r && r.canvas) g.drawImage(r.canvas, Math.round(sx) - r.ox, Math.round(sy) - r.oy);
      }
      at.draw(g, this.anim, fr, sx, sy, {
        flip, scale: this.scale, rot: this.rot, alpha, flash: this.flash, tint: this.tint,
        outline: o.outline || this.outline, skin: this.skin, sil: o.sil, backlit: o.backlit, rim: o.rim, dither: o.dither,
      });
    }
    setStand(standId) {
      const sd = standId && G.D && G.D.stands ? G.D.stands[standId] : null;
      if (this.stand && this.stand.dispose) this.stand.dispose();
      this.stand = null;
      this.standId = standId || null;
      if (!standId || (sd && sd.kind === 'object') || !G.Stand) return null;
      this.stand = new G.Stand(this, standId);
      return this.stand;
    }
  }
  G.Actor = Actor;

  // ------------------------------------------------------------------ 地图
  class Stage {
    constructor(def) {
      this.def = def;
      this.id = def.id;
      const spec = def.bg && G.D && G.D.bg ? G.D.bg[def.bg] : null;
      if (def.bg && !spec) dbgSet('missingImg', 'bg/' + def.bg);
      this.bgSpec = spec || null;
      this.bg = new G.Background(spec || { layers: [] });
      const walk = spec && spec.walk;
      this.x0 = def.x0 == null ? 0 : def.x0;
      this.x1 = def.x1 == null ? (spec && spec.w) || G.W : def.x1;
      this.mapX0 = this.x0; this.mapX1 = this.x1;     // 地图本来的左右范围（战斗会把 x0 / x1 临时改成场地，镜头夹取要用这个）
      this.yMin = def.yMin == null ? (walk ? walk[0] : 150) : def.yMin;
      this.yMax = def.yMax == null ? (walk ? walk[1] : 176) : def.yMax;
      this.ground = def.ground == null ? (spec && spec.ground) || this.yMin : def.ground;
      this.actors = [];
      this.props = (def.props || []).filter((p) => p.type !== 'breakable').map((p) => Object.assign({}, p));
      this.hotspots = (def.hotspots || []).map((h) => Object.assign({}, h));
      this.triggers = (def.triggers || []).map((t) => Object.assign({ fired: false }, t));
      this.obstacles = (def.obstacles || []).map((ob) => Object.assign({}, ob));
      this.camX = def.camX || 0;
      this.camY = 0;
      this.camTarget = null;
      this.lock = null;
      this.t = 0;
      this.state = Object.assign({}, def.state || {});
      this.anchors = Object.assign({}, spec && spec.anchors, def.anchors);
      this.onLook = def.onLook || null;
    }
    add(a) { if (this.actors.indexOf(a) < 0) this.actors.push(a); a.remove = false; return a; }
    find(id) { return this.actors.find((a) => a.id === id && !a.remove); }
    bounds() { return this.lock ? [this.lock.x0 + 10, this.lock.x1 - 10] : [this.x0 + 8, this.x1 - 8]; }
  }
  G.Stage = Stage;

  // ------------------------------------------------------------------ 影子（fx.shadow：两级椭圆，乘法变暗；小画布预先做好，multiply 画上去）
  const shadowCache = new Map();
  function shadowCanvas(w) {
    w = Math.max(2, Math.round(w));
    let c = shadowCache.get(w);
    if (c) return c;
    const h = Math.max(2, Math.round(w * 0.28));
    c = G.mkCanvas(w, h);
    const g = c.g || c.getContext('2d');
    const id = g.createImageData(w, h), u = new Uint32Array(id.data.buffer);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const ex = (x + 0.5 - w / 2) / (w / 2), ey = (y + 0.5 - h / 2) / (h / 2), d = ex * ex + ey * ey;
      const v = d <= 0.45 ? 166 : d <= 1 ? 206 : -1;
      if (v >= 0) u[y * w + x] = (0xff000000 | (v << 16) | (v << 8) | v) >>> 0;
    }
    g.putImageData(id, 0, 0);
    shadowCache.set(w, c);
    return c;
  }

  // ------------------------------------------------------------------ 道具（地图 props）
  function drawProp(g, p, camX, camY, t) {
    const x = Math.round(p.x - camX), y = Math.round(p.y - camY);
    switch (p.type) {
      case 'image': {
        const im = G.image(p.image);
        if (!im || !G.ready(im)) break;
        if (p.screen) g.drawImage(im, p.sx || 0, p.sy || 0);
        else g.drawImage(im, x - (p.ax || 0), Math.round(y - (p.z || 0)) - (p.ay || 0));
        break;
      }
      case 'sprite': {
        const A = G.propAtlas(p.sprite || p.id);
        const f = p.frame != null ? p.frame : A.frameAt('idle', t * (p.speed || 1));
        A.draw(g, 'idle', f, x, y - (p.z || 0), { flip: !!p.flip, scale: p.scale || 1, alpha: p.alpha, rot: p.rot || 0 });
        break;
      }
      case 'rects':
        for (const [dx, dy, w, h, c] of p.rects || []) { g.fillStyle = c; g.fillRect(x + dx, Math.round(y - (p.z || 0)) + dy, w, h); }
        break;
      case 'custom': if (p.draw) p.draw(g, x, y, t); break;
      default: break;
    }
  }

  // ------------------------------------------------------------------ 世界
  const ghostLast = new WeakMap();   // 残影：上一次快照的 ownT
  const burnFx = new WeakMap();      // 着火：挂在人身上的 fire 实例
  const reactT = new WeakMap();      // NPC 的亮替身反应：上一次的 world 时刻
  const items = [];

  const W = (G.world = {
    stage: null, player: null, free: false, combat: false, focus: null, near: null, insert: null, cine: null, slow: 1,
    maxTokens: 2, anims: [], ticks: [], shots: [], hazards: [], fightT: 0, fight: null, zoom: null,
    _az: null, _ambient: null,

    // o = { player, x, y, facing, carry: [Actor], music: false, ambient: false }
    setStage(def, o = {}) {
      if (typeof def === 'string') {
        const d = G.STAGES[def];
        if (!d) { ev('stage_missing', { id: def }); def = { id: def, bg: null }; } else def = d;
      }
      const st = new Stage(def);
      this.stage = st;
      this.shots = [];
      this.hazards = [];
      if (G.fx && G.fx.clear) G.fx.clear();
      this.near = null;
      this.focus = null;
      this._az = null;
      const p = o.player || this.player;
      if (p) {
        if (o.x != null) p.x = o.x;
        p.x = clamp(p.x, st.x0 + 8, st.x1 - 8);
        p.y = clamp(o.y != null ? o.y : p.y, st.yMin, st.yMax);
        p.z = 0; p.vx = 0; p.vy = 0; p.vz = 0; p.state = 'idle'; p.follow = null;
        if (o.facing) p.facing = o.facing;
        st.add(p);
        this.player = p;
      }
      for (const n of def.npcs || []) {
        if (n.cond && !n.cond()) continue;
        const a = new Actor(n.cid, n.x, n.y, Object.assign({}, n, { team: n.team || 'npc' }));
        if (n.anim) a.play(n.anim);
        st.add(a);
      }
      for (const b of def.props || []) {
        if (b.type !== 'breakable') continue;
        const a = new Actor('prop:' + (b.sprite || b.id), b.x, b.y, {
          id: b.id, team: 'object', hp: b.hp || 30, shadow: false, breakable: b, z: b.z || 0, noTurn: true,
          standReact: false, bodyW: b.w ? b.w / 2 : 8,
        });
        a.frozen = (b.frames || [0, 1])[0];
        st.add(a);
      }
      const carry = o.carry || (G.party && G.party.carryList ? G.party.carryList() : []);
      carry.forEach((a, i) => {
        if (a === p) return;
        a.script = null; a.state = 'idle'; a.z = 0; a.vx = 0; a.vy = 0; a.remove = false; a.hold = false;
        if (p) {
          a.x = clamp(p.x - (p.facing || 1) * (22 + i * 22), st.x0 + 8, st.x1 - 8);
          a.y = clamp(p.y + [-3, 3, -5, 5, 0][i % 5], st.yMin, st.yMax);
          a.facing = p.facing;
        }
        a.play(a.idleAnim);
        st.add(a);
      });
      for (const a of st.actors) if (a.stand) a.stand.hide();
      if (G.audio) {
        if (o.music !== false && def.music && G.audio.music) G.audio.music(def.music);
        if (o.ambient !== false) {
          if (this._ambient && this._ambient.stop) { this._ambient.stop(0.3); this._ambient = null; }
          if (def.ambient && G.audio.loop) {
            const am = typeof def.ambient === 'string' ? { name: def.ambient } : def.ambient;
            this._ambient = G.audio.loop(am.name, { vol: am.vol == null ? 0.4 : am.vol });
          }
        }
      }
      if (G.party && G.party.rebuildFollow) G.party.rebuildFollow();
      this.snapCamera();
      return st;
    },
    enemies() { return this.stage ? this.stage.actors.filter((a) => a.team === 'enemy' && !a.dead && !a.remove) : []; },
    allies() { return this.stage ? this.stage.actors.filter((a) => a.team === 'ally' && !a.remove) : []; },
    npcs() { return this.stage ? this.stage.actors.filter((a) => a.team === 'npc' && !a.remove) : []; },
    objects() { return this.stage ? this.stage.actors.filter((a) => a.team === 'object' && !a.remove) : []; },
    members() {
      const st = this.stage;
      if (!st || !G.party) return [];
      return G.party.members.filter((m) => !m.remove && st.actors.indexOf(m) >= 0);
    },
    tokens() { return this.enemies().filter((e) => e.state === 'windup' || e.state === 'attack' || e.state === 'charge').length; },

    // 夹纵深带、场地边界、障碍（同银魂 world.js:192-209）；rootT > 0 的人不动
    move(a, dx, dy, free = false) {
      if (a.rootT > 0) return;
      const st = this.stage;
      if (!st) { a.x += dx; a.y += dy; return; }
      let nx = a.x + dx;
      let ny = clamp(a.y + dy, st.yMin, st.yMax);
      // 自由跟随只绕过战斗锁，仍受地图边缘约束。
      if (free) nx = clamp(nx, st.x0 + 8, st.x1 - 8);
      if (!free) {
        const [lo, hi] = st.bounds();
        if (a.x >= lo && a.x <= hi) nx = clamp(nx, lo, hi);
        else if (a.x < lo) nx = Math.max(nx, a.x);
        else nx = Math.min(nx, a.x);
      }
      for (const ob of st.obstacles) {
        if (nx > ob.x0 && nx < ob.x1 && ny > ob.y0 && ny < ob.y1) {
          const wasX = a.x > ob.x0 && a.x < ob.x1, wasY = a.y > ob.y0 && a.y < ob.y1;
          if (!wasX) nx = a.x; else if (!wasY) ny = a.y; else { nx = a.x; ny = a.y; }
        }
      }
      a.x = nx; a.y = ny;
    },

    // ---------------- 每帧（技术约定 §4.11.3 的顺序）
    update(dt) {
      const st = this.stage;
      if (!st) return;
      const tm = T();
      // 1
      st.t += dt * (tm && tm.flowScale ? tm.flowScale() : 1);
      if (this.anims.length) {
        this.anims = this.anims.filter((an) => {
          an.t += dt;
          const k = Math.min(1, an.t / an.dur);
          an.fn(k, dt);
          if (k >= 1) { if (an.res) an.res(); return false; }
          return true;
        });
      }
      if (this.combat && !this.cine) this.fightT += dt;
      if (this.ticks.length) this.ticks = this.ticks.filter((fn) => !fn(dt));
      // 2
      if (tm && tm.update) tm.update(dt);
      // 3
      if (G.party && G.party.update) G.party.update(dt);
      // 4
      const p = this.player, C = G.combat || {}, paused = new Set();
      for (const a of st.actors) {
        if (a.remove) continue;
        // 时停和局部顿帧暂停个人计时，避免恢复时无敌或控制效果已经耗尽。
        if (frozenOf(a)) { paused.add(a); continue; }
        if (a.stopT > 0) { a.stopT = Math.max(0, a.stopT - dt); paused.add(a); continue; }
        if (a.flash > 0) a.flash = Math.max(0, a.flash - dt * 7);
        if (a.invuln > 0) a.invuln = Math.max(0, a.invuln - dt);
        if (a.iframe > 0) a.iframe = Math.max(0, a.iframe - dt);
        if (a.dodgeCd > 0) a.dodgeCd = Math.max(0, a.dodgeCd - dt);
        if (a.emote && typeof a.emote.t === 'number') { a.emote.t -= dt; if (a.emote.t <= 0) a.emote = null; }
        if (a.rootT > 0) { a.rootT = Math.max(0, a.rootT - dt); if (a.rootT <= 0) a.rootBy = null; }
        if (a.stunT > 0) a.stunT = Math.max(0, a.stunT - dt);
        if (a.rootImmuneT > 0) a.rootImmuneT = Math.max(0, a.rootImmuneT - dt);
        if (a.breakT > 0) a.breakT = Math.max(0, a.breakT - dt);
        if (a.nextMulT > 0) { a.nextMulT = Math.max(0, a.nextMulT - dt); if (a.nextMulT <= 0) a.nextMul = 1; }
        this._burn(a);
        const da = dt * a.slowK * (a.team === 'enemy' ? this.slow : 1);
        a.animT += da; a.stateT += da; a.ownT += da;
        if (a.fly && a.state !== 'launched' && a.state !== 'down' && a.state !== 'dead' && !a.script) {
          a.z = a.fly.z + Math.round(Math.sin(a.ownT * 2.4) * (a.fly.bob || 0));
        }
        this._ghost(a);
        if (a.script) a.script(da);
        else if (a === p) { if (C.updatePlayer) C.updatePlayer(a, da); }
        else if (a.team === 'ally') { if (C.updateAlly) C.updateAlly(a, da); }
        else if (a.team === 'enemy') { if (C.updateEnemy) C.updateEnemy(a, da); }
        else if (a.follow) { if (G.party && G.party.updateFollow) G.party.updateFollow(a, da); }
        else if (!a.hold && a.anim !== a.idleAnim && a.animDone()) a.play(a.idleAnim);
      }
      // 5 替身（读本体这一帧的新位置）
      // stopT 归零的这一逻辑步仍被冻结，替身必须与本体同时恢复。
      for (const a of st.actors) if (a.stand && !a.remove && !paused.has(a)) a.stand.update(dt);
      // 6 敌人互相推开
      const es = this.enemies();
      for (let i = 0; i < es.length; i++) {
        for (let j = i + 1; j < es.length; j++) {
          const a = es[i], b = es[j];
          if (Math.abs(a.x - b.x) < 12 && Math.abs(a.y - b.y) < 6) {
            const s = a.x < b.x ? -1 : 1;
            // 冻结者不被碰撞挪动，仍可动的一方独自让开。
            if (!paused.has(a)) this.move(a, s * 20 * dt * (paused.has(b) ? 2 : 1), 0);
            if (!paused.has(b)) this.move(b, -s * 20 * dt * (paused.has(a) ? 2 : 1), 0);
          }
        }
      }
      if (st.actors.some((a) => a.remove)) st.actors = st.actors.filter((a) => !a.remove);
      // 7
      if (C.updateShots) C.updateShots(dt);
      if (C.updateHazards) C.updateHazards(dt);
      // 8 自由走动：触发区 → 互动（E）→ 替身调查（U）
      this.near = null;
      if (p && this.free && !sBusy() && !this.combat && p.state !== 'down' && !uiBlocking()) {
        for (const tr of st.triggers) {
          if (tr.fired) continue;
          if (tr.cond && !tr.cond()) continue;
          const inX = p.x >= tr.x0 && p.x <= tr.x1;
          const inY = tr.y0 == null || (p.y >= tr.y0 && p.y <= tr.y1);
          if (inX && inY) { if (tr.once !== false) tr.fired = true; run(tr.run); break; }
        }
        if (!sBusy()) {
          const I = G.input;
          this.near = this.findNear();
          if (this.near && I && (I.okHit ? I.okHit() : I.hit && I.hit('ok'))) {
            if (I.consumeOk) I.consumeOk();
            const n = this.near;
            if (n.actor) {
              const a = n.actor;
              p.facing = a.x > p.x ? 1 : -1;
              run(async (S) => {
                const old = a.facing;
                if (!a.noTurn) a.facing = p.x > a.x ? 1 : -1;
                S.talker = a;
                try { await a.talk(S, a); } finally { S.talker = null; }
                if (!a.noTurn && !a.remove && !a.follow) a.facing = old;
              });
            } else {
              const h = n.hot;
              run((S) => h.use(S, h, p));
            }
          } else if (I && I.take && I.take('special', 0.15)) {
            if (G.party && G.party.investigate) G.party.investigate();
          }
        }
      }
      // 9
      if (G.fx && G.fx.prune) G.fx.prune();
      this.updateCamera(dt);
    },
    _ghost(a) {
      if (a.ghostOn) {
        const last = ghostLast.get(a);
        if (last == null || a.ownT - last >= 1 / 30 || a.ownT < last) {
          ghostLast.set(a, a.ownT);
          a.ghosts.push({ x: a.x, y: a.y, z: a.z, anim: a.anim, frame: a.frameIndex(), facing: a.facing, skin: a.skin, scale: a.scale, t: a.ownT });
          if (a.ghosts.length > 4) a.ghosts.shift();
        }
      }
      if (a.ghosts.length) {
        while (a.ghosts.length && a.ownT - a.ghosts[0].t >= GHOST_LIFE) a.ghosts.shift();
      }
    },
    // 燃烧：按 world 时钟每 tick 秒掉一次（combat 有 burnTick 就交给它），身上挂一个 fire 实例
    _burn(a) {
      const b = a.burn, t = now();
      let inst = burnFx.get(a);
      if (b) {
        if (t >= (b.until == null ? Infinity : b.until)) a.burn = null;
        else {
          const tick = b.tick || 0.5;
          if (b._next == null) b._next = t + tick;
          if (t >= b._next) {
            b._next += tick;
            const dmg = Math.max(1, Math.round((b.dps || 4) * tick));
            if (G.combat && G.combat.burnTick) G.combat.burnTick(a, dmg);
            else if (!a.dead) {
              a.hp = Math.max(a.minHp || 0, a.hp - dmg);
              a.flash = Math.max(a.flash, 0.5);
              if (a.hp <= 0 && G.combat && G.combat.ko) G.combat.ko(a, null);
            }
          }
          if (!inst && G.fx && G.fx.spawn) {
            inst = G.fx.spawn('fire', { x: a.x, y: a.y, w: 8, h: 10 }, { follow: a, dy: -Math.round(a.topPx() * a.scale * 0.35), tag: 'burn' });
            if (inst) burnFx.set(a, inst);
          }
        }
      }
      if (!a.burn && inst) { if (G.fx && G.fx.kill) G.fx.kill(inst); burnFx.delete(a); }
    },

    // ---------------- 互动
    findNear() {
      const p = this.player, st = this.stage;
      if (!p || !st) return null;
      let best = null, bd = 1e9;
      for (const a of st.actors) {
        if (a === p || !a.talk || a.remove || !a.visible || a.team === 'enemy') continue;
        const dx = Math.abs(a.x - p.x), dy = Math.abs(a.y - p.y);
        if (dx < 26 && dy < a.talkRy && dx + dy * 1.5 < bd) {
          bd = dx + dy * 1.5;
          best = { actor: a, label: a.label || a.name, x: a.x, top: a.headY() };
        }
      }
      for (const h of st.hotspots) {
        if (!h.use || h.hidden || (h.cond && !h.cond())) continue;
        const dx = Math.abs(h.x - p.x), dy = Math.abs(h.y - p.y);
        if (dx < (h.r || 18) && dy < (h.ry || 22) && dx + dy * 1.5 < bd) {
          bd = dx + dy * 1.5;
          best = { hot: h, label: h.label, x: h.lx == null ? h.x : h.lx, top: h.ly == null ? h.y - 40 : h.ly };
        }
      }
      return best;
    },
    // 替身调查的目标：队长周围（半径 h.r × 1.6）最近的、tags 和 G.LOOK[队长].tags 有交集、cond 成立的调查点
    findLook() {
      const p = this.player, st = this.stage;
      if (!p || !st) return null;
      const L = G.LOOK && G.LOOK[p.cid];
      const tags = (L && L.tags) || [];
      if (!tags.length) return null;
      let best = null, bd = 1e9;
      for (const h of st.hotspots) {
        if (!h.tags || !h.tags.length || h.hidden || (h.cond && !h.cond())) continue;
        if (!h.tags.some((tg) => tags.indexOf(tg) >= 0)) continue;
        const dx = Math.abs(h.x - p.x), dy = Math.abs(h.y - p.y);
        if (dx <= (h.r || 18) * 1.6 && dy <= (h.ry || 22) * 1.6 && dx + dy * 1.5 < bd) { bd = dx + dy * 1.5; best = h; }
      }
      return best;
    },
    // 队长自由走动时亮替身：搭话范围 ×1.5 内最近的 NPC 反应（onStand → G.LOOK.onStandDefault；同一个 NPC 10 s 内只一次）
    standReact(leader) {
      const st = this.stage;
      leader = leader || this.player;
      if (!st || !leader || !this.free || this.combat || sBusy()) return false;
      const t = now();
      let best = null, bd = 1e9;
      for (const a of st.actors) {
        if (a === leader || a.team !== 'npc' || a.remove || !a.visible || a.standReact === false) continue;
        if (G.party && G.party.members.indexOf(a) >= 0) continue;
        const dx = Math.abs(a.x - leader.x), dy = Math.abs(a.y - leader.y);
        if (dx >= 26 * 1.5 || dy >= a.talkRy * 1.5) continue;
        const last = reactT.get(a);
        if (last != null && t - last < 10) continue;
        if (!a.onStand && !(G.LOOK && G.LOOK.onStandDefault)) continue;
        if (dx + dy * 1.5 < bd) { bd = dx + dy * 1.5; best = a; }
      }
      // 调查点也可以写 onStand（J 亮替身 = “恶灵”伸手去碰它）：范围同 U 调查（半径 ×1.6），比最近的 NPC 更近就选它
      let bh = null, bhd = 1e9;
      for (const h of st.hotspots) {
        if (!h.onStand || h.hidden || (h.cond && !h.cond())) continue;
        const dx = Math.abs(h.x - leader.x), dy = Math.abs(h.y - leader.y);
        if (dx > (h.r || 18) * 1.6 || dy > (h.ry || 22) * 1.6) continue;
        const last = reactT.get(h);
        if (last != null && t - last < 2) continue;
        if (dx + dy * 1.5 < bhd) { bhd = dx + dy * 1.5; bh = h; }
      }
      if (bh && (!best || bhd < bd)) {
        reactT.set(bh, t);
        ev('stand_react', { id: bh.id });
        run((S) => bh.onStand(S, bh, leader));
        return true;
      }
      if (!best) return false;
      reactT.set(best, t);
      const a = best;
      ev('stand_react', { id: a.id });
      if (a.onStand) run((S) => a.onStand(S, a, leader));
      else run((S) => G.LOOK.onStandDefault(S, a, leader));
      return true;
    },

    // ---------------- 镜头（§2.6）
    snapCamera() { this.updateCamera(1, true); },
    updateCamera(dt, snap) {
      const st = this.stage;
      if (!st) return;
      const w = G.W || 320, p = this.player;
      let lo = st.lock ? st.lock.x0 : st.x0;
      let hi = Math.max(lo, (st.lock ? st.lock.x1 : st.x1) - w);
      let target, rate = 6;
      if (st.camTarget != null) target = st.camTarget;
      else if (this.focus) target = this.focus.x - w / 2;
      else if (this.combat && p) {
        rate = 4;
        let e = null, bd = 1e9;
        for (const a of this.enemies()) {
          if (a.untargetable || !a.visible) continue;
          const d = Math.abs(a.x - p.x) + Math.abs(a.y - p.y);
          if (d < bd) { bd = d; e = a; }
        }
        target = e ? (p.x + e.x) / 2 - w / 2 : p.x - w / 2;
        target = clamp(target, p.x - 0.8 * w, p.x - 0.2 * w);   // 操作角色留在屏幕中间 60% 以内
        const ar = this.fight && this.fight.spec && this.fight.spec.arena;
        if (ar) {
          // 场地比一屏窄：镜头对准场地中心，只按地图本来的范围夹取（战斗把 st.x0 改成了 ar[0]，按它夹取镜头会被推到 ar[0]：
          //   单屏地图的背景不动、人物却整体左移 ar[0] 像素——序1 牢房里承太郎跑进墙里、阿布德尔像站在牢里）
          if (ar[1] - ar[0] <= w) {
            const c = (ar[0] + ar[1]) / 2 - w / 2, m0 = st.lock ? st.lock.x0 : st.mapX0 != null ? st.mapX0 : lo;
            const m1 = st.lock ? st.lock.x1 : st.mapX1 != null ? st.mapX1 : lo + w;
            lo = hi = clamp(c, m0, Math.max(m0, m1 - w));
          }
          else { lo = Math.max(lo, ar[0]); hi = Math.max(lo, Math.min(hi, ar[1] - w)); }
        }
      } else if (p) target = p.x - w / 2 + (p.facing || 1) * 12;
      else target = st.camX;
      target = clamp(target, lo, hi);
      st.camX = snap ? target : st.camX + (target - st.camX) * Math.min(1, dt * rate);
      // W6 招牌大招：预警开始推到 1.3（0.2 s），到这一招收招完再 0.2 s 拉回
      let want = null;
      if (this.combat) {
        for (const e of this.enemies()) {
          const tier = (e.tele && e.tele.tier) || (e.atk && e.atk.warn && e.atk.warn.tier);
          if (tier === 'W6') { want = e; break; }
        }
      }
      const az = this._az || (this._az = { k: 1, x: 160, y: 90 });
      if (want) { az.x = want.x; az.y = want.y - want.z - want.topPx() * want.scale * 0.6; }
      const kt = want ? 1.3 : 1, step = (snap ? 1 : dt) * 1.5;
      az.k += clamp(kt - az.k, -step, step);
      if (G.cam) {
        G.cam.x = Math.round(st.camX);
        G.cam.y = Math.round(st.camY || 0);
        G.cam.zoom = this.zoom ? this.zoom : az.k > 1.001 ? { k: az.k, x: az.x, y: az.y } : null;
      }
    },

    // ---------------- 画（canvas pass，§2.5 ①）
    _collect(g, camX, camY, filter, over) {
      const st = this.stage;
      items.length = 0;
      let n = 0;
      const push = (y, k, o) => { items.push({ y, k, o, n: n++ }); };
      if (!over) for (const p of st.props) if (!p.hidden && p.type !== 'pixel' && !(p.cond && !p.cond())) push(p.depth == null ? p.y : p.depth, 0, p);
      // 地图写了 fgDepth：前景（拘留所铁栏）按这条脚底线参与纵深排序，线后面（牢里）的人被挡、线前面（走廊）的人画在上面
      if (!over && st.def.fgDepth != null && st.bg.fg.length) push(st.def.fgDepth, 5, null);
      for (const a of st.actors) {
        if (a.remove || !a.visible) continue;
        if (!filter(a)) continue;
        push(a.y, 1, a);
        if (a.stand && a.stand.visible) push(a.y + a.stand.depth, 2, a.stand);
        if (a.ghosts.length) push(a.y - 0.1, 3, a);
      }
      if (!over) for (const s of this.shots) if (s && (s.kind === 'img' || (s.image && s.kind !== 'px'))) push((s.y || 0) + 0.5, 4, s);
      items.sort((a, b) => a.y - b.y || a.n - b.n);
      const tm = T();
      const stopped = !!(tm && tm.active && tm.phase === 'stopped');
      for (const it of items) {
        if (it.k === 1) {
          const a = it.o;
          a.draw(g, camX, camY, { ghosts: false, outline: stopped && frozenOf(a) ? FROZEN_OUTLINE : null });
        } else if (it.k === 2) it.o.draw(g, camX, camY, stopped && frozenOf(it.o.owner) ? { outline: FROZEN_OUTLINE } : undefined);
        else if (it.k === 3) it.o.drawGhosts(g, camX, camY);
        else if (it.k === 4) { if (G.combat && G.combat.drawShot) G.combat.drawShot(g, it.o, camX, camY); }
        else if (it.k === 5) st.bg.drawFg(g, camX, st.t, st);
        else drawProp(g, it.o, camX, camY, this.stage.t);
      }
      items.length = 0;
    },
    draw(g) {
      const ins = this.insert;
      if (ins) {
        const t = (G.clk ? G.clk[ins.clock || 'ui'] : 0) - (ins.t0 || 0);
        if (ins.draw) ins.draw(g, t);
        return;
      }
      const st = this.stage;
      if (!st) return;
      const camX = G.cam ? G.cam.x | 0 : Math.round(st.camX), camY = G.cam ? G.cam.y | 0 : 0, t = st.t;
      st.bg.draw(g, camX, t, st);
      const imm = overOn() ? G.time.immune : null;
      // 影子
      const op = g.globalCompositeOperation;
      g.globalCompositeOperation = 'multiply';
      for (const a of st.actors) {
        if (a.remove || !a.visible || !a.shadow || a.rot || a.alpha <= 0.3 || a.z >= 40) continue;
        if (imm && imm.has(a)) continue;
        const c = shadowCanvas(a.shadowW);
        g.drawImage(c, Math.round(a.x - camX - c.width / 2), Math.round(a.y - camY - c.height / 2));
      }
      g.globalCompositeOperation = op;
      // 纵深排序：道具 / 角色 / 替身 / 残影 / 贴图飞行道具
      const f = imm ? (a) => !imm.has(a) : () => true;
      this._collect(g, camX, camY, f, false);
      if (st.def.fgDepth == null) st.bg.drawFg(g, camX, t, st);
    },
    hasPixel() { return !!(this.stage || this.insert); },
    drawPixel(P, layer) {
      const ins = this.insert;
      if (ins) {
        if (ins.drawPixel) ins.drawPixel(P, layer, (G.clk ? G.clk[ins.clock || 'ui'] : 0) - (ins.t0 || 0));
        return;
      }
      const st = this.stage;
      if (!st) return;
      if (layer === 'mid') {
        const camX = G.cam ? G.cam.x | 0 : 0, camY = G.cam ? G.cam.y | 0 : 0;
        for (const p of st.props) if (p.type === 'pixel' && !p.hidden && p.draw) p.draw(P, Math.round(p.x - camX), Math.round(p.y - camY), st.t);
        for (const a of st.actors) if (a.stand && !a.remove && a.visible && a.stand.drawPixel) a.stand.drawPixel(P, camX, camY);
      }
      if (G.combat && G.combat.drawPixel) G.combat.drawPixel(P, layer);
    },
    hasOver() { return overOn(); },
    // 时停中能动的人 + 他们的替身（全彩，画在已经变色的世界上面）
    drawOver(g) {
      const st = this.stage;
      if (!st || this.insert || !overOn()) return;
      const imm = G.time.immune;
      const camX = G.cam ? G.cam.x | 0 : 0, camY = G.cam ? G.cam.y | 0 : 0;
      this._collect(g, camX, camY, (a) => imm.has(a), true);
    },
  });
})();
