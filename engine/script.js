// 剧情脚本 API：await S.say(...) / S.walk(...) 这样一句句写剧情（G.S，除 S.fight；S.fight 由 fight.js 加）、G.STORY、G.flags
//   接口见技术约定 §4.16。所有别的包的函数都在“用的那一刻”去取（载入时不碰别的模块），找不到就记 G.dbg 事件 'api_missing'、
//   照常往下走（剧情不会因为某个演出零件还没做好就卡死）。
'use strict';
(function () {
  const G = window.G;
  const task = G.runPromise || (f => new Promise(f));
  G.flags = {};
  G.STORY = {};

  // ---------------------------------------------------------------- 小工具（只在本文件里用）
  const fn = (o, k) => !!(o && typeof o[k] === 'function');
  const missing = (name) => { if (G.dbg && G.dbg.ev) G.dbg.ev('api_missing', { name }); };
  // 调别的包的函数：有就调，没有就记一笔并返回 dflt
  function call(objName, k, args, dflt) {
    const o = G[objName];
    if (!fn(o, k)) { missing(objName + '.' + k); return dflt; }
    return o[k](...args);
  }
  const P = (v) => Promise.resolve(v);
  const clk = () => (G.clk ? G.clk : { ui: 0, world: 0, flow: 0 });
  const touchOn = () => !!(G.touch && G.touch.on);

  // 这个说话人有没有头像（没有头像的 NPC 自动不画头像框，免得记进 missingHead）
  function hasHeads(cid) {
    if (typeof cid !== 'string' || cid.indexOf(':') >= 0) return false;
    const c = G.D && G.D.chars && G.D.chars[cid];
    return !!(c && c.heads && Object.keys(c.heads).length);
  }
  // 资源是否存在：cid / 'scene:xxx' / 'prop:xxx'
  function resExists(c) {
    if (typeof c !== 'string' || !G.D) return false;
    if (c.startsWith('scene:')) return !!(G.D.scene && G.D.scene[c.slice(6)]);
    if (c.startsWith('prop:')) return !!(G.D.props && G.D.props[c.slice(5)]);
    return !!(G.D.chars && G.D.chars[c]);
  }
  const ease = (u) => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2);

  const S = (G.S = {
    busy: false,
    talker: null,
    cardOn: false,        // 篇章卡显示中（快照的 chapter 字段读它）
    _filters: new Set(),  // S.filter 加过的滤镜名（S.filter(null) 一次清掉）
    _amb: null,           // 当前的环境音循环
    get flags() { return G.flags; },
    get player() { return G.world ? G.world.player : null; },

    // ================================================================ 流程
    // 跑一段剧情（同一时间只跑一段；跑的时候玩家不能动，跑完交还操作）。嵌套时直接写，别再包 S.run（无职坑 B16）
    async run(f, o = {}) {
      const runId = G.runId;
      while (this.busy) await G.wait(0.05, 'ui');
      this.busy = true;
      const W = G.world;
      W.free = false;
      let err = null;
      try { await f(this); } catch (e) {
        if (G.cancelled && G.cancelled(e)) throw e;
        if (G.dbg && G.dbg.ev) G.dbg.ev('script_error', { msg: String((e && e.message) || e) });
        console.error(e);   // 剧情代码出错是真问题：让自动测试看见
        err = e;
      }
      if (runId !== G.runId) return;
      // 出错也交还操作再抛：以前直接 throw，busy 永远是 true，玩家什么也做不了（2026-10-09 牢房抢漫画卡死）
      this.busy = false;
      if ((o.keepLocked !== true || err) && W.stage) W.free = true;
      if (err) throw err;
    },
    actor(a) {
      if (a == null) return null;
      if (typeof a !== 'string') return a;
      const W = G.world;
      if (a === 'player') return W.player;
      const st = W.stage;
      let r = st && fn(st, 'find') ? st.find(a) : null;
      if (!r && fn(G.party, 'get')) r = G.party.get(a) || null;
      return r || null;
    },
    wait: (sec, clock) => G.wait(sec, clock || 'world'),
    until: (f) => G.until(f),
    free(on = true) { G.world.free = on; },
    mark(name) { if (G.dbg) G.dbg.shot = name; },
    // 返回第一个存在的 cid（P1 / P2 资源没画好时顶上）；都没有就返回最后一个并记 missingImg
    cid(...cands) {
      for (const c of cands) if (resExists(c)) return c;
      const last = cands[cands.length - 1];
      if (G.dbg && G.dbg.missingImg) G.dbg.missingImg.add(String(last).startsWith('scene:') ? 'scene/' + String(last).slice(6) : 'chars/' + last);
      return last;
    },
    // 资源存不存在（剧情里做“有就放、没有就跳过”的判断用）
    exists(c) { return resExists(c); },

    // ================================================================ 声音
    sfx(name, vol = 1, rate = 1) {
      if (vol && typeof vol === 'object') return call('audio', 'sfx', [name, vol], null);
      return call('audio', 'sfx', [name, { vol, rate }], null);
    },
    // 播音效，在击打点 resolve（按真实时间等：全场慢放时也对得上声音）
    cue(name, o = {}) {
      const h = call('audio', 'cue', [name, o], null);
      return G.wait(h && h.hitIn > 0 ? h.hitIn : 0, 'ui');
    },
    music(name, fade) {
      if (!name) return this.stopMusic(fade);
      return call('audio', 'music', [name, { fade: fade == null ? 0.8 : fade }], P());
    },
    stopMusic(fade) { return call('audio', 'stopMusic', [fade == null ? 0.8 : fade], undefined); },
    ambient(name, vol = 0.3) {
      if (this._amb) { try { this._amb.stop(0.3); } catch (e) { /* 已经停了 */ } this._amb = null; }
      if (name) this._amb = call('audio', 'loop', [name, { vol }], null);
      return this._amb;
    },

    // ================================================================ 画面
    shake(amp = 2, dur = 0.25, o = {}) { if (fn(G, 'shake')) G.shake(amp, dur, o); else missing('G.shake'); },
    bump(k = 0.08, dur = 0.12) { if (G.cam && fn(G.cam, 'bump')) G.cam.bump(k, dur); else missing('cam.bump'); },
    flash(dur = 0.25, peak = 1, color = '#fff') { if (fn(G, 'flash')) G.flash(dur, peak, color); else missing('G.flash'); },
    // 剧情的冲击帧默认 force（不受全局 0.6 s 节流）。签名：impact(style, dur) / impact([styles], step, hold)
    impact(style = 'invert', dur = 1 / 24, hold = 0) {
      if (Array.isArray(style)) return call('post', 'impactSeq', [style, dur, hold, { force: true }], undefined);
      return call('post', 'impact', [style, dur, { force: true }], undefined);
    },
    fadeOut(dur = 0.5) { return fn(G, 'fade') ? G.fade(1, dur) : P(); },
    fadeIn(dur = 0.5) { return fn(G, 'fade') ? G.fade(0, dur) : P(); },
    letterbox(on) { if (G.ui) G.ui.letterboxTarget = on === true ? 32 : (typeof on === 'number' ? on : 0); },
    // 世界层插入画面：fn(wg, t) 或 { draw, drawPixel, clock }；null 关掉（顺手清掉 tag 'insert' 的特效）
    insert(f, o = {}) {
      const W = G.world;
      if (!f) { W.insert = null; if (G.fx && fn(G.fx, 'killTag')) G.fx.killTag('insert'); return; }
      const obj = typeof f === 'function' ? { draw: f } : Object.assign({}, f);
      obj.clock = obj.clock || o.clock || 'world';
      obj.t0 = clk()[obj.clock] || 0;
      W.insert = obj;
      return obj;
    },
    insertUI(f) { if (G.ui) G.ui.insertUI = f ? { draw: f, t0: clk().ui } : null; },
    // 常驻滤镜（= G.post.filter）；name = null 清掉这里加过的全部滤镜
    filter(name, amount = 1, o = {}) {
      if (!G.post || !fn(G.post, 'filter')) { missing('post.filter'); return; }
      if (name == null) { for (const n of this._filters) G.post.filter(n, null); this._filters.clear(); return; }
      if (amount == null) { G.post.filter(name, null); this._filters.delete(name); return; }
      G.post.filter(name, amount, o);
      this._filters.add(name);
    },
    // 镜头推近 / 拉回：k 倍，对准世界坐标 (x, y)，或角色（第三个参数是相对胸口的 dy，默认 −24）
    zoom(k, x, y, dur = 0.3) {
      const W = G.world;
      if (x != null && (typeof x === 'object' || typeof x === 'string')) {
        const a = this.actor(x);
        if (a) { const dy = typeof y === 'number' ? y : -24; x = a.x; y = a.y - (a.z || 0) + dy; } else { x = null; y = null; }
      }
      const z0 = W.zoom || { k: 1, x: x != null ? x : (G.cam ? G.cam.x + 160 : 160), y: y != null ? y : 90 };
      const to = { k, x: x != null ? x : z0.x, y: y != null ? y : z0.y };
      // 后发的推拉镜接管：没 await 的长推镜（比如 0.9 s）不能在拉回 1.0 之后再把镜头推回去
      const tok = W._zoomTok = (W._zoomTok || 0) + 1;
      if (dur <= 0) { W.zoom = k > 1.001 ? to : null; return P(); }
      const from = Object.assign({}, z0);
      return this.animate(dur, (u) => {
        if (W._zoomTok !== tok) return;
        const e = ease(u);
        W.zoom = { k: G.lerp(from.k, to.k, e), x: G.lerp(from.x, to.x, e), y: G.lerp(from.y, to.y, e) };
        if (u >= 1 && k <= 1.001) W.zoom = null;
      });
    },
    // 〔推镜冲上去〕：zoom 音效提前 0.40 s，到位那一下白闪 .35 + 暗角 0 → .55（报告 09 §2.8）
    async punchIn(a, o = {}) {
      o = Object.assign({ k: 3, dur: 0.14, dy: -30, hold: 0.6 }, o);
      this.sfx('zoom');
      await G.wait(Math.max(0, 0.40 - o.dur), 'ui');
      await this.zoom(o.k, a, o.dy, o.dur);
      this.flash(0.06, 0.35);
      this.filter('vignette', 0.55, { colour: '#000000', inner: 0.5 });
      G.defer(o.hold, () => this.filter('vignette', null), 'ui');
    },
    // 数字 = 镜头左边的世界 x；角色 = 跟着它；null = 跟队长
    camera(x) {
      const W = G.world, st = W.stage;
      if (!st) return;
      if (x == null) { st.camTarget = null; W.focus = null; }
      else if (typeof x === 'number') { st.camTarget = x; W.focus = null; }
      else { st.camTarget = null; W.focus = this.actor(x); }
    },
    // 剧情直接放特效（= G.fx.spawn）；函数还没移植时跳过
    fx(name, kw = {}, o = {}) {
      if (!G.fx || !fn(G.fx, 'spawn')) { missing('fx.spawn'); return null; }
      if (G.FX && !fn(G.FX, name)) { missing('FX.' + name); return null; }
      return G.fx.spawn(name, kw, o);
    },
    killFx(inst) { if (inst && G.fx && fn(G.fx, 'kill')) G.fx.kill(inst); },
    lightning() { this.flash(0.3, 0.85, '#e4ebff'); this.sfx('thunder', 0.8); },
    state(key, val) { const st = G.world.stage; if (st) { st.state = st.state || {}; st.state[key] = val; } },

    // ================================================================ 卡片 / 文字（= G.uifx.*）
    nameCard(cid, o = {}) { return call('uifx', 'nameCard', [cid, o], undefined); },
    standCard(id, o = {}) { return call('uifx', 'standCard', [id, o], undefined); },
    location(key, o = {}) { return call('uifx', 'location', [key, o], undefined); },
    title(key, o = {}) { return P(call('uifx', 'title', [key, o], undefined)); },
    async chapterCard(key, o = {}) {
      this.cardOn = true;
      try { await P(call('uifx', 'chapterCard', [key, o], undefined)); } finally { this.cardOn = false; }
    },
    // 拟声字：at = 角色 / 角色 id / {wx, wy, wz} / {x, y}
    sfxText(word, at, o = {}) {
      if (typeof at === 'string') at = this.actor(at);
      return call('uifx', 'sfx', [word, at, o], undefined);
    },
    word(word, at, o) { return this.sfxText(word, at, o); },
    menacing(o = {}) {
      o = Object.assign({}, o);
      if (typeof o.actor === 'string') o.actor = this.actor(o.actor);
      return call('uifx', 'menacing', [o], null) || { stop() {} };
    },
    emote(a, text, dur = 1, color) { a = this.actor(a); if (a) a.emote = { text, t: dur, color }; },
    hint(text, dur) { return call('ui', 'hint', [text, dur], undefined); },
    notice(o) { return P(call('ui', 'notice', [o], undefined)); },
    vs(o) { return P(call('uifx', 'vs', [o], undefined)); },
    cutin(o) { return P(call('uifx', 'cutin', [o], undefined)); },
    tbc(o = {}) { return P(call('uifx', 'tbc', [o], undefined)); },
    panel(id, o = {}) { return call('uifx', 'panel', [id, o], null) || { close() {} }; },
    crash(from, to, o = {}) { return P(call('uifx', 'crashRecord', [from, to, o], undefined)); },
    photo(o = {}) { return P(call('uifx', 'photo', [o], undefined)); },
    eyeStrip(cid, o = {}) { return P(call('uifx', 'eyeStrip', [cid, o], undefined)); },
    memory(o = {}) { return call('uifx', 'memoryPanel', [o], null) || { close() {} }; },
    // 旅行地图（实现在 story\common.js 的 G.TPL.route）
    route(stops, o = {}) { return G.TPL && fn(G.TPL, 'route') ? G.TPL.route(this, stops, o) : (missing('TPL.route'), P()); },

    // ================================================================ 对话
    // who = cid（取头像、名字、打字音）/ null（调查描述，无头像无名牌）；o = { expr, name, color, pos, portrait, actor }
    async say(who, text, o = {}) {
      o = Object.assign({}, o);
      const W = G.world, st = W.stage, tk = this.talker;
      let a = o.actor ? this.actor(o.actor) : null;
      if (!a && typeof who === 'string') {
        if (W.player && W.player.cid === who) a = W.player;
        else if (st && fn(st, 'find')) a = st.find(who) || null;
        if (!a && fn(G.party, 'get')) a = G.party.get(who) || null;
        if (!a && tk && tk.cid === who) a = tk;
      }
      delete o.actor;
      if (o.portrait === undefined && who && !hasHeads(who)) o.portrait = false;
      let talked = false;
      if (a && !a.hold && !a.script && !a.remove && (a.state === 'idle' || a.state == null) && a.atlas && fn(a.atlas, 'has') && a.atlas.has('talk')) {
        a.play('talk'); talked = true;
      }
      await call('ui', 'say', [who, text, o], P());
      if (talked && !a.remove && a.anim === 'talk') a.play(a.idleAnim || 'idle');
    },
    narrate(text, o = {}) {
      o = Object.assign({}, o);
      if (o.top) { o.pos = 'top'; delete o.top; }
      return P(call('ui', 'narrate', [text, o], undefined));
    },
    choice(options, title, o) { return P(call('ui', 'choice', [options, title, o], 0)); },

    // ================================================================ 角色 / 动作
    spawn(cid, x, y, o = {}) {
      o = Object.assign({}, o);
      if (typeof cid === 'string' && (cid.startsWith('prop:') || cid.startsWith('scene:')) && o.shadow === undefined) o.shadow = false;
      const a = new G.Actor(cid, x, y, o);
      if (o.shadow === false) a.shadow = false;
      if (o.z != null) a.z = o.z;
      G.world.stage.add(a);
      return a;
    },
    remove(a) { a = this.actor(a); if (a) a.remove = true; },
    face(a, dir) {
      a = this.actor(a);
      if (!a) return;
      if (typeof dir === 'number') a.facing = dir;
      else { const b = this.actor(dir); if (b) a.facing = b.x > a.x ? 1 : -1; }
    },
    // 同伴 / NPC 跟着谁走（null = 不跟了）
    follow(a, target = 'player') { a = this.actor(a); if (a) { a.follow = target ? this.actor(target) : null; a.hold = false; } },
    prop(o) {
      const p = Object.assign({ type: 'sprite', x: 0, y: 0, z: 0, rot: 0, alpha: 1, scale: 1 }, o);
      G.world.stage.props.push(p);
      return p;
    },
    unprop(p) { const st = G.world.stage; if (st && p) st.props = st.props.filter((q) => q !== p); },
    // 逐帧动画：f(k, dt)，k 从 0 走到 1，dur 秒后结束（挂在 G.world.ticks 上，世界时钟）
    animate(dur, f) {
      const d = Math.max(1e-4, dur), runId = G.runId;
      return task((res) => {
        let t = 0;
        G.world.ticks.push((dt) => {
          if (runId !== G.runId) { res(); return true; }
          t += dt;
          const k = Math.min(1, t / d);
          try { f(k, dt); } catch (e) { console.error(e); res(); return true; }
          if (k >= 1) { res(); return true; }
          return false;
        });
      });
    },
    walk(a, x, y, o = {}) {
      a = this.actor(a);
      if (!a) return P();
      a.visible = true;
      return task((res) => {
        const speed = o.speed || Math.min(a.speed || 60, 64);
        const ty = y == null ? a.y : y;
        const runId = G.runId;
        a.hold = false;
        a.state = 'idle';
        a.script = (dt) => {
          if (runId !== G.runId || a.remove) { a.script = null; res(); return; }
          const dx = x - a.x, dy = ty - a.y, d = Math.hypot(dx, dy);
          if (d < 1) {
            a.x = x; a.y = ty; a.script = null; a.state = 'idle';
            a.play(o.endAnim || a.idleAnim || 'idle');
            if (o.face) a.facing = o.face;
            res();
            return;
          }
          const step = Math.min(d, speed * dt);
          a.x += (dx / d) * step; a.y += (dy / d) * step;
          if (Math.abs(dx) > 0.5 && !o.backward) a.facing = dx > 0 ? 1 : -1;
          a.play(o.anim || 'walk', { speed: o.animSpeed || 1 });
        };
      });
    },
    // 抛物线（被打飞、跳下来、扔东西）。结束时自动 hold = false
    arc(a, x, y, height, dur, o = {}) {
      a = this.actor(a);
      if (!a) return P();
      return task((res) => {
        const x0 = a.x, y0 = a.y, z0 = a.z || 0, z1 = o.z1 || 0, r0 = a.rot || 0, runId = G.runId;
        let t = 0;
        a.hold = true;
        a.script = (dt) => {
          if (runId !== G.runId || a.remove) { a.script = null; a.hold = false; res(); return; }
          t += dt;
          const k = Math.min(1, t / Math.max(1e-4, dur));
          a.x = G.lerp(x0, x, k); a.y = G.lerp(y0, y, k);
          a.z = G.lerp(z0, z1, k) + 4 * height * k * (1 - k);
          if (o.spin) a.rot = r0 + o.spin * k;
          if (o.anim) a.play(o.anim);
          if (k >= 1) { a.script = null; a.hold = false; res(); }
        };
      });
    },
    // 摆姿势：o.freeze = 定格在第几帧；o.x / o.y 顺便挪位置
    pose(a, anim, o = {}) {
      a = this.actor(a);
      if (!a) return;
      a.hold = true; a.state = 'idle';
      a.play(anim, { restart: o.restart, speed: o.speed });
      a.frozen = o.freeze != null ? o.freeze : null;
      if (o.y != null) a.y = o.y;
      if (o.x != null) a.x = o.x;
    },
    unpose(a, o = {}) {
      a = this.actor(a);
      if (!a) return;
      a.hold = false; a.state = 'idle'; a.frozen = null; a.rot = 0;
      if (o.y != null) a.y = o.y;
      if (o.x != null) a.x = o.x;
      a.play(a.idleAnim || 'idle');
    },
    async act(a, anim, o = {}) {
      a = this.actor(a);
      if (!a) return;
      a.hold = true;
      a.play(anim, { restart: true, speed: o.speed || 1 });
      const t0 = clk().world;
      await G.until(() => a.remove || (fn(a, 'animDone') && a.animDone()) || clk().world - t0 > (o.max || 3));
      if (!o.keep && !a.remove) { a.hold = false; a.play(a.idleAnim || 'idle'); }
    },
    // 换地图：自动带上队伍（G.party.carryList()）；o = { x, y, facing, fade, music, bg（同一张地图换背景变体）, ambient }
    async setStage(id, o = {}) {
      let def = typeof id === 'string' ? G.STAGES[id] : id;
      if (!def) { missing('STAGES.' + id); return; }
      if (o.bg) def = Object.assign({}, def, { bg: o.bg });
      if (o.fade !== false) await G.fade(1, o.fadeDur || 0.35);
      // 背景按“第一次登记的章节”分包：在别的章节包里（underwater、mansion_hall、redsea_island…）就先补载，
      //   不然这张地图一片黑（从章节选择直接进、或本章用到别章背景时都会碰到）
      const bgm = def.bg && G.D && G.D.bg ? G.D.bg[def.bg] : null;
      if (bgm && bgm.pack && G.res && fn(G.res, 'loaded') && !G.res.loaded('bg_' + bgm.pack)) {
        try { await G.res.loadPack('bg_' + bgm.pack); } catch (e) { console.error(e); }
      }
      const W = G.world;
      W.zoom = null; W._zoomTok = (W._zoomTok || 0) + 1;   // 换图时还在跑的推拉镜作废
      if (W.insert) this.insert(null);
      const carry = fn(G.party, 'carryList') ? G.party.carryList() : [];
      W.setStage(def, { player: W.player, x: o.x, y: o.y, carry });
      if (fn(G.party, 'rebuildFollow')) G.party.rebuildFollow();
      if (o.facing && W.player) { W.player.facing = o.facing; carry.forEach((c) => { c.facing = o.facing; }); }
      if (fn(W, 'snapCamera')) W.snapCamera();
      const mus = o.music !== undefined ? o.music : def.music;
      if (mus) this.music(mus);
      const amb = o.ambient !== undefined ? o.ambient : def.ambient || null;
      this.ambient(amb ? amb.name : null, amb ? amb.vol : 0);
      if (o.fade !== false) await G.fade(0, 0.4);
    },
    // 自动卷轴（银魂保留；以后的追车、滑翔段用）：镜头每秒走 speed px 到 endX；障碍用 K 闪避的无敌帧穿过（不再有跳）
    //   obstacles = [{ x, y, w, h, dmg, sfx, word, prop }]；o.onTick(dt, t, obs)；输了从头再来。M1 不用
    async runner(o) {
      const W = G.world, st = W.stage, p = W.player;
      const cam0 = o.cam0 != null ? o.cam0 : st.camX;
      for (let attempt = 0; ; attempt++) {
        const obs = (o.obstacles || []).map((ob) => Object.assign({ done: false }, ob));
        const props = obs.map((ob) => (ob.prop ? this.prop(Object.assign({ x: ob.x, y: ob.y }, ob.prop)) : null));
        st.camX = cam0; st.camTarget = cam0; W.focus = null;
        p.x = cam0 + (o.rx || 110); p.y = o.y || p.y; p.z = 0; p.state = 'idle'; p.hold = false; p.hp = p.maxHp; p.invuln = 0;
        if (attempt > 0) await G.fade(0, 0.4);
        W.free = true;
        let t = 0, lost = false, finished = false;
        W.ticks.push((dt) => {
          t += dt;
          st.camTarget = Math.min(o.endX, st.camTarget + (o.speed || 90) * dt);
          if (st.camTarget >= o.endX && st.camX >= o.endX - 2) { finished = true; return true; }
          if (o.onTick) o.onTick(dt, t, obs);
          for (const ob of obs) {
            if (ob.done || p.invuln > 0 || p.iframe > 0) continue;
            if (Math.abs(p.x - ob.x) < (ob.w || 16) / 2 + 5 && Math.abs(p.y - ob.y) < (ob.h || 8)) {
              ob.done = true; p.hp -= ob.dmg || 15; p.invuln = 1.0; p.flash = 1;
              this.shake(3, 0.25); this.sfx(ob.sfx || 'thud', 0.9); this.sfxText(ob.word || '咚', p);
            }
          }
          if (p.hp <= 0) { p.hp = 0; lost = true; return true; }
          return false;
        });
        await G.until(() => lost || finished);
        W.free = false;
        props.forEach((pr) => pr && this.unprop(pr));
        if (finished) break;
        await G.wait(0.8);
        const r = await P(call('ui', 'openMenu', [`${p.name || ''}倒下了……`, ['再来一次', '回到标题'], { note: '输了就从这一段重新开始' }], 0));
        if (r === 1) { await G.goTitle(); const e = new Error('已返回标题'); e.name = 'RunCancelled'; throw e; }
        await G.fade(1, 0.3);
      }
      st.camTarget = null;
      p.hp = p.maxHp;
    },

    // ================================================================ 队伍 / 替身 / 战斗外机制
    party(ids, o = {}) { return call('party', 'set', [ids, o], undefined); },
    // 入队；o.notice 时弹「X 加入了队伍！」系统框（由这里弹，awaitable，不交给 party.add）
    async join(id, o = {}) {
      const r = call('party', 'add', [id, Object.assign({}, o, { notice: false })], null);
      if (o.notice) {
        this.sfx('power_up');
        await this.notice({ who: id, title: '', text: `${this.nameOf(id)} 加入了队伍！` });
      }
      return r;
    },
    leave(id, o = {}) { return call('party', 'remove', [id, o], undefined); },
    setLeader(id, o = {}) { return !!call('party', 'setLeader', [id, o], false); },
    lockLeader(on = true) { return call('party', 'lock', [on], undefined); },
    leadable(id, on, o = {}) { return call('party', 'setLeadable', [id, on, o], undefined); },
    nameOf(cid) {
      const c = typeof cid === 'string' ? cid : cid && cid.cid;
      const D = G.D || {};
      return (G.NAMES && G.NAMES[c]) || (D.heroes && D.heroes[c] && D.heroes[c].short) || (D.speakers && D.speakers[c] && D.speakers[c].short) ||
        (D.chars && D.chars[c] && D.chars[c].name) || c;
    },
    // 只给“另一个人短暂操作”的特殊段落（新建 Actor）；一般换人用 S.setLeader
    setPlayer(cid, o = {}) {
      const W = G.world, old = W.player;
      const p = new G.Actor(cid, o.x != null ? o.x : old ? old.x : 100, o.y != null ? o.y : old ? old.y : 160, {
        id: cid, team: 'player', hp: o.hp, speed: o.speed, facing: o.facing || (old ? old.facing : 1), kit: o.kit,
      });
      if (old && W.stage) {
        if (o.keep) { old.team = 'npc'; old.hold = false; old.state = 'idle'; } else old.visible = false;
      }
      if (W.stage) W.stage.add(p);
      W.player = p;
      return p;
    },
    // 替身召唤：o = { dur, rise, sfx, card }；o.card 时同时放替身卡 + sting_reveal
    async summon(a, o = {}) {
      a = this.actor(a);
      if (!a) return;
      if (!a.stand && fn(a, 'setStand')) {
        const sid = a.standId || (G.D.heroes && G.D.heroes[a.cid] && G.D.heroes[a.cid].stand);
        if (sid) a.setStand(sid);
      }
      if (!a.stand) { missing('stand:' + a.cid); return; }
      if (o.card) { this.standCard(a.stand.id || a.standId, typeof o.card === 'object' ? o.card : {}); this.cue('sting_reveal'); }
      a.stand.summon(o);
      await G.wait(o.dur != null ? o.dur : 0.35);
    },
    async recall(a, o = {}) {
      a = this.actor(a);
      if (!a || !a.stand) return;
      a.stand.recall(o);
      await G.wait(o.dur != null ? o.dur : 0.25);
    },
    standAct(a, pose, o = {}) {
      a = this.actor(a);
      if (!a) return;
      if (!a.stand && fn(a, 'setStand')) {
        const sid = a.standId || (G.D.heroes && G.D.heroes[a.cid] && G.D.heroes[a.cid].stand);
        if (sid) a.setStand(sid);
      }
      if (a.stand) a.stand.act(pose, o);
    },
    timestop(by, o = {}) {
      if (!G.time || !fn(G.time, 'stop')) { missing('time.stop'); return P(); }
      return G.time.stop(this.actor(by), o);
    },
    // QTE（= G.ui.startQte）；包装带默认值（技术约定 §4.10.1）。resolve 前再锁一次确认键（防手机猛点跳台词）
    async qte(o) {
      const r = await P(call('ui', 'startQte', [o], o && o.type === 'press' ? 'miss' : true));
      if (G.input) { if (fn(G.input, 'lockOk')) G.input.lockOk(0.6); if (fn(G.input, 'consumeOk')) G.input.consumeOk(); }
      return r;
    },
    mash(o) { return this.qte(Object.assign({ type: 'mash', label: '连按 J！', need: 8, time: 2, decay: 0 }, o)); },
    timing(o) { return this.qte(Object.assign({ type: 'timing', label: '看准时机按 J！', speed: 1.1, zone: [0.42, 0.58], tries: 1 }, o)); },
    rhythm(o) { return this.qte(Object.assign({ type: 'rhythm', label: '跟着节拍按 J！', window: 0.16, travel: 1.6, pass: 0.6 }, o)); },
    clash(o) { return this.qte(Object.assign({ type: 'clash', label: '连按 J！欧拉欧拉！', time: 4, push: 0.06, rate: 0.2, start: 0.5 }, o)); },
    press(o) { return this.qte(Object.assign({ type: 'press', key: 'guard', window: 0.5, failOk: true }, o)); },
    pluck(o) { return this.qte(Object.assign({ type: 'pluck' }, o)); },
    aim(o) { return this.qte(Object.assign({ type: 'aim' }, o)); },

    // ================================================================ 过场视频（op / coffin / ending，技术约定 §2.7）
    video(name, o = {}) {
      return task((res) => {
        const v = G.D && G.D.video && G.D.video[name];
        if (!v) { if (G.dbg && G.dbg.ev) G.dbg.ev('video_missing', { name }); res(); return; }
        const el = document.createElement('video');
        el.src = v.webm && el.canPlayType('video/webm; codecs="vp9, opus"') ? v.webm : v.src;
        el.playsInline = true;
        el.preload = 'auto';
        const prev = G.scene, prevFade = G.fadeA;
        let done = false, t = 0;
        const runId = G.runId;
        const finish = () => {
          if (done) return;
          done = true;
          try { el.pause(); el.removeAttribute('src'); el.load(); } catch (e) { /* 已经释放 */ }
          if (runId === G.runId) { G.fadeA = prevFade; G.setScene(prev); }
          res();
        };
        const scene = {
          name: 'video',
          get frozen() { return false; },
          enter() {}, leave() {},
          update(dt) {
            t += dt;
            if (o.skip !== false && t > 0.6 && (G.input.okHit() || G.input.hit('pause'))) {
              G.input.consumeOk(); if (fn(G.input, 'consume')) G.input.consume('pause');
              finish();
            }
          },
          drawWorld() {},
          drawScreen(sctx, w, h) { if (el.readyState >= 2) sctx.drawImage(el, 0, 0, w, h); },
          drawUI(ug) {
            if (t < 4 && G.f12) G.f12.draw(ug, touchOn() ? '点屏幕跳过' : 'Enter 跳过', 628, 342, 'rgba(255,255,255,0.6)', { align: 'right', outline: 'rgba(0,0,0,0.5)' });
          },
        };
        el.addEventListener('ended', finish, { once: true });
        el.addEventListener('error', finish, { once: true });
        this.stopMusic(0.3);
        G.fadeA = 0;      // 前面淡出留下的黑幕会整个盖住视频（银魂坑 B13），放完再还原
        G.setScene(scene);
        const pr = el.play();
        if (pr && pr.catch) pr.catch(() => { el.muted = true; const p2 = el.play(); if (p2 && p2.catch) p2.catch(finish); });
        G.defer((v.duration || 20) + 3, finish, 'ui');
        return () => { done = true; el.pause(); el.removeAttribute('src'); el.load(); };
      });
    },
  });
})();
