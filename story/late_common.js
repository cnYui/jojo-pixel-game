// 小游戏共享取消、输入和像素绘制；每个机关保留自己的完成条件和重试点。
'use strict';
(function () {
  const G = window.G, W = G.world, T = G.TPL;
  const hit = a => { const yes = G.input.hit(a); if (yes) G.input.consume(a); return yes; };
  const text = (g, s, x, y, colour = '#fff2d0', align = 'left') => G.f12.draw(g, s, x, y, colour, { align, outline: '#151023' });
  const label = (g, title, sub) => { g.fillStyle = '#181126'; g.fillRect(8, 8, 624, 51); text(g, title, 20, 15, '#ffe174'); if (sub) text(g, sub, 20, 36); };
  // 战斗里的机关说明：右上、Boss 条 / 计时框下面（同 mid_common 的 M.hud），不压左上的队长血条、同伴栏和 VS 小标签；
  // 小游戏（没有战斗 HUD）才用 label 的顶栏。
  const hud = (g, lines, y = 44) => lines.filter(Boolean).forEach((s, i) => text(g, s, 630, y + i * 15, i ? '#ffe3a0' : '#fff4d6', 'right'));
  const L = G.LATE = { hit, text, label, hud,
    async lines(S, rows) { for (const [who, words, expr] of rows) await S.say(who, words, expr ? { expr } : {}); },
    async game(S, state, tick, draw, drawUI) {
      const run = G.runId, oldFree = W.free, oldInsert = W.insert, oldUI = G.ui.insertUI;
      W.free = false; G.lateGame = state; state.t = 0;
      if (draw) S.insert((g, t) => draw(g, state, t));
      if (drawUI) S.insertUI(g => drawUI(g, state));
      try {
        return await G.runPromise((res, reject) => {
          const update = dt => {
            if (run !== G.runId) return true;
            try { state.t += dt; tick(state, dt); if (state.done) { G.dbg.ev('mini_result', { type: state.type, win: state.win, t: state.t }); res(state); return true; } }
            catch (e) { reject(e); return true; }
            return false;
          };
          W.ticks.push(update);
          return () => { const i = W.ticks.indexOf(update); if (i >= 0) W.ticks.splice(i, 1); };
        });
      } finally {
        if (run === G.runId) { G.lateGame = null; W.free = oldFree; W.insert = oldInsert; G.ui.insertUI = oldUI; G.input.lockOk(.5); }
      }
    },
    task(c, fn) {
      if (c.data.busy) return;
      c.data.busy = true; const run = G.runId, old = W.cine; W.cine = { by: '后段机关' };
      Promise.resolve().then(fn).catch(G.cancelIgnore).finally(() => {
        if (run === G.runId && W.fight === c) { c.data.busy = false; W.cine = old; }
      });
    },
    damage(c, n, extra = {}) { return G.combat.hit(null, c.player, Object.assign({ dmg: n, push: 0, slot: 'enemy', guard: 'none', sfxHit: 'thud' }, extra)); },
    pixel(draw) { const p = { type: 'pixel', id: 'late_' + W.stage.id, x: 0, y: 0, draw }; W.stage.props.push(p); return p; },
    async view(S, o, seconds = 1) { const v = T.show(S, o); try { await S.wait(seconds); } finally { v.close(); } },
    move(p, dt, speed = 70) {
      const dx = (G.input.isDown('right') ? 1 : 0) - (G.input.isDown('left') ? 1 : 0);
      const dy = (G.input.isDown('down') ? 1 : 0) - (G.input.isDown('up') ? 1 : 0);
      W.move(p, dx * speed * dt, dy * speed * dt * .65);
      if (dx) p.facing = Math.sign(dx); p.play(dx || dy ? 'walk' : p.idleAnim);
    },
    hot(id, x, labelText, tags, use, look) { return { id, x, y: 160, r: 26, ry: 100, label: labelText, tags, use, look }; },
    async explore(S, stage, o = {}) {
      const st = G.STAGES[stage], flag = 'exit_' + stage; G.flags[flag] = false;
      st.hotspots = o.hotspots || []; st.npcs = o.npcs || [];
      st.triggers = [{ x0: o.exitX || st.x1 - 24, x1: st.x1 + 16, y0: 0, y1: 180,
        once: true, run: async () => { G.flags[flag] = true; } }];
      st.onLook = o.onLook || (async (s, p) => s.say(p.cid, '替身的气息从前方传来。'));
      await S.setStage(stage, { x: o.x || 48, y: 160 });
      if (o.location) S.location(o.location, { y: 50 });   // 自由走动时左上是队伍头像条（UI y 8–40），地点卡放它下面（同序章）
      T.memberTalk(o.talk || {}); S.free(true); S.hint(o.hint || 'Q 切换队长，E 搭话，U 调查；沿路向右。', 8);
      await S.until(() => G.flags[flag] && !S.busy); S.free(false);
    },
    async clash(S, o = {}) {
      const ins = T.show(S, { bg: 'radial', colours: ['#231139', '#8a6829'], draw: g => {
        const q = G.ui.qte, v = q && typeof q.v === 'number' ? q.v : .5;
        const middle = 90 + v * 140, t = G.clk.ui;
        for (let n = 0; n < 14; n++) {
          const y = 46 + n * 7, jitter = Math.sin(t * 35 + n) * 6;
          g.fillStyle = '#bc9cff'; g.fillRect(24 + jitter, y, middle - 24, 4);
          g.fillStyle = '#e4bd4f'; g.fillRect(middle, y + 2, 294 - middle - jitter, 4);
        }
        T.sprite(g, o.a || 'starplat', 'idle', 0, 38, 170, { scale: 2 });
        T.sprite(g, o.b || 'theworld', 'idle', 0, 282, 170, { scale: 2, flip: true });
      } });
      try { return await S.clash(o); } finally { ins.close(); }
    },
    async runner(S, o = {}) {
      for (let attempt = 0; ; attempt++) {
        const q = { type: o.race ? 'race' : 'chase', lane: 1, hp: o.hp || 100, distance: 0,
          speed: 0, cars: [], spawn: 0, behind: 210, slow: 0, hits: 0, leading: 0, seed: 0,
          enemyLane: 1, enemyAhead: 28, blocked: 0, finalBend: false, followT: 0,
          touch: { buttons: ['pad', 'j'], captions: { j: o.race ? '加速' : '水花' } } };
        await L.game(S, q, (s, dt) => {
          // 画面是从车后看的三条车道（左 / 中 / 右）：左右键换道最直观；追车段也认上下键（规划写的“上下换道”）
          const lo = hit('left') || (!o.race && hit('up')), hi = hit('right') || (!o.race && hit('down'));
          if (lo) s.lane = Math.max(0, s.lane - 1); if (hi) s.lane = Math.min(2, s.lane + 1);
          s.speed += ((o.race ? G.input.isDown('attack') ? 120 : 30 : 90) - s.speed) * dt * 3;
          s.distance += s.speed * dt; s.slow = Math.max(0, s.slow - dt);
          if (o.race) {
            s.finalBend = s.distance >= 2160;
            if (s.enemyLane !== s.lane) { s.followT += dt; if (s.followT >= .3) { s.enemyLane = s.lane; s.followT = 0; } }
            else s.followT = 0;
            if (s.speed > 90 && s.lane !== s.enemyLane) { s.leading += dt; s.enemyAhead -= dt * 8; }
            else if (s.speed > 90) { s.blocked += dt; s.enemyAhead += dt * 3; }
            s.enemyAhead = G.clamp(s.enemyAhead, -30, 50);
            if (s.finalBend) s.enemyAhead = Math.max(16, s.enemyAhead);
          }
          s.spawn += dt;
          if (s.spawn >= (o.race ? 2.4 : 3.2)) { s.spawn = 0; s.cars.push({ x: 338, lane: (s.seed++ * 2 + 1) % 3, warn: .5 }); }
          for (const car of s.cars) { car.warn -= dt; car.x -= s.speed * dt; if (car.x < 90 && car.x > 60 && car.lane === s.lane && !car.hit) { car.hit = true; s.hp -= 10; s.hits++; S.sfx('thud'); S.shake(2, .15); } }
          s.cars = s.cars.filter(c => c.x > -30);
          if (!o.race) {
            const cycle = s.t % 8; s.behind = 35 + 150 * (1 - cycle / 8);
            if (hit('attack') && s.slow <= 0) { s.slow = 2; S.sfx('emerald_shot'); }
            if (cycle > 7.85 && s.lane === Math.floor(s.t / 8) % 3 && s.slow <= 0 && s.lastRam !== Math.floor(s.t / 8)) { s.lastRam = Math.floor(s.t / 8); s.hp -= 10; s.hits++; S.shake(3, .2); }
          }
          if (s.hp <= 0) { s.done = true; s.win = false; }
          if (o.race ? s.distance >= 2400 : s.t >= 60) { s.done = true; s.win = true; s.storyLoss = !!o.race; }
        }, (g, s) => {
          g.fillStyle = '#171328'; g.fillRect(0, 0, 320, 180);
          g.fillStyle = '#3b343e'; g.beginPath(); g.moveTo(128, 25); g.lineTo(192, 25); g.lineTo(320, 180); g.lineTo(0, 180); g.closePath(); g.fill();
          for (let n = 0; n < 9; n++) { const k = ((n * 25 + s.distance * .5) % 180) / 180, y = 25 + 150 * k * k;
            g.fillStyle = '#bea96f'; for (const side of [-1, 1]) g.fillRect(160 + side * (10 + k * 50), y, 2, 4 + k * 8); }
          for (const car of s.cars) { const x = 120 + car.lane * 40, y = 180 - car.x * .38;
            if (y > 35) { g.fillStyle = car.warn > 0 ? '#ff5749' : '#b7ae9b'; g.fillRect(x - 10, y - 14, 20, 26); g.fillStyle = '#201b29'; g.fillRect(x - 7, y - 10, 14, 6); } }
          const x = 120 + s.lane * 40; g.fillStyle = '#67aec0'; g.fillRect(x - 12, 138, 24, 34);
          g.fillStyle = '#eee0ac'; g.fillRect(x - 8, 141, 16, 8);
          if (o.race) {
            g.fillStyle = '#c45a79'; g.fillRect(109 + s.enemyLane * 40, 120 - s.enemyAhead, 22, 28); }
          else { g.fillStyle = s.slow > 0 ? '#45978b' : '#ac7b42'; g.fillRect(118 + Math.floor(s.t / 8) % 3 * 40, 170 - s.behind * .15, 24, 27); }
        }, (g, s) => { label(g, o.race ? 'F-MEGA' : '追车：坚持六十秒', o.race ? '按住 J 加速；左右换道' : '左右（或上下）换道；J 绿宝石水花让后车减速两秒'); text(g, '车况 ' + Math.max(0, s.hp), 22, 318);
          text(g, o.race ? '赛程 ' + Math.min(100, Math.floor(s.distance / 24)) + '%' : '剩余 ' + Math.ceil(Math.max(0, 60 - s.t)) + ' 秒', 610, 318, '#ffe174', 'right');
          if (o.race && s.finalBend) text(g, '最后的弯道……他提前封住了路线！', 320, 72, '#ffad94', 'center'); });
        if (q.win) return q;
        await S.say(o.race ? 'kakyoin' : 'joseph', o.race ? '这次还没有跑完。再来！' : '差一点失去控制……继续追！');
      }
    }
  };
})();
