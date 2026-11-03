// 第11章　川尻家 / 败者食尘：玩法（开发脚本 第四部/docs/第11章_开发脚本.md 第 3 节）。剧情节拍在 story/p4_ch11.js。
//   插曲 爸爸不是爸爸（b11_spy，潜行录证据）、第 17 战 Cheap Trick 段 A 十字路口（b17a_street，背不能被看到）/ 段 B 幽灵小路（b17b_alley，不能回头）、
//   第 18 战 败者食尘：出门（b18_go）、躲开露伴（b18_avoid）、偷猫草（b18_cat）。最后的“拖时间”是过场里的选择，写在 p4_ch11.js。
//   这些都不是正面打架：用 S.fight 只是为了现成的“重来这一小段 / 放水再来”、HUD 的槽和计时。没有 waves，机关全在 tick 里。
//   人物 cid 用 C11.cid('hayato') 取：别章的正式图（hayato / kawajiri / rohan …）合进来了就用正式的，没有就用本章画的 ph11_* 占位。
'use strict';
(function () {
  const G = window.G;
  const P4 = () => G.P4;
  const clk = () => (G.clk ? G.clk.ui : 0);
  const UW = 640;

  // ================================================================ 人物 cid：正式的有就用正式的
  const REAL = { hayato: 'hayato', kosaku: 'kawajiri', shinobu: 'shinobu', rohan: 'rohan', okuyasu: 'okuyasu', reimi: 'reimi', killerq: 'killerqueen' };
  const HERO = { hayato: true, rohan: true };
  const C11 = (G.C11 = {});
  C11.cid = (k) => {
    const D = G.D || {}, ch = D.chars || {}, r = REAL[k];
    if (r && ch[r] && (!HERO[k] || (D.heroes && D.heroes[r]))) return r;
    return 'ph11_' + k;
  };
  C11.straycat = () => (G.D && G.D.props && G.D.props.straycat ? 'straycat' : 'ph11_straycat');
  // 早人、露伴的 kit：本章的玩法里他们不出拳（正式的 kit 由别章定义时也照样用 kitOverride 关掉招式）
  for (const c of ['hayato', 'ph11_hayato']) if (!G.KITS[c]) G.KITS[c] = { hp: 60, speed: 56, combo: [], rush: null, special: null, guard: {}, dodge: { dist: 24 }, chords: {} };
  for (const c of ['rohan', 'ph11_rohan']) if (!G.KITS[c]) G.KITS[c] = { hp: 100, speed: 60, combo: [], rush: null, special: null, guard: {}, dodge: {}, chords: {} };
  const NOMOVES = { combo: [], rush: null, special: null, chords: {} };
  const player = () => G.world.player;

  // 战斗里插一段演出（照序章 p4_pro_fights.js 的 cine）：占住 W.cine，演完还回去
  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-ch11' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  C11.cine = cine;
  // 按键：只看“这一次按下的时刻”变没变（战斗里 updatePlayer 会把缓冲吃掉，lastPress 不会）
  function pressed(d, key) {
    const lp = G.input.lastPress(key);
    const k = 'lp_' + key;
    if (d[k] === undefined) { d[k] = lp; return false; }
    if (lp !== d[k]) { d[k] = lp; return true; }
    return false;
  }

  // ================================================================ 视线扇形 + 叠加层（画在 UI 层：世界坐标 ×2）
  //   w = { a: 人, range, dy0, slope, red }：a 面朝的一侧，range 以内、上下 dy0 + dx·slope 以内算看得见
  function sees(w, p) {
    const a = w.a;
    if (!a || a.remove || !p || w.off) return false;
    const dx = (p.x - a.x) * (a.facing || 1);
    return dx > -4 && dx < w.range && Math.abs(p.y - a.y) <= w.dy0 + Math.max(0, dx) * w.slope;
  }
  C11.sees = sees;
  let coneH = null;
  function conesOverlay(getList) {
    if (coneH) coneH.close();
    coneH = P4().overlay((g) => {
      const list = getList();
      if (!list || !G.cam || !G.cam.w2u || (G.world && G.world.cine && !list.showInCine)) return;
      g.save();
      for (const w of list) {
        const a = w.a;
        if (!a || a.remove || w.off || a.visible === false) continue;
        const f = a.facing || 1;
        const p0 = G.cam.w2u(a.x, a.y - 6, 0), p1 = G.cam.w2u(a.x + f * w.range, a.y - 6, 0);
        const spread = (w.dy0 + w.range * w.slope) * 2 * 0.6;
        g.globalAlpha = w.red ? 0.30 : 0.16;
        g.fillStyle = w.red ? '#ff5040' : '#fff0a0';
        g.beginPath();
        g.moveTo(p0.x, p0.y - w.dy0 * 1.2);
        g.lineTo(p1.x, p1.y - spread);
        g.lineTo(p1.x, p1.y + spread);
        g.lineTo(p0.x, p0.y + w.dy0 * 1.2);
        g.closePath();
        g.fill();
      }
      g.restore();
    }, { z: -1 });
    return coneH;
  }
  C11.closeCones = () => { if (coneH) { coneH.close(); coneH = null; } };

  // 录像的「● REC」（画面左上）
  let recH = null;
  function recOverlay(getRec) {
    if (recH) recH.close();
    recH = P4().overlay((g, t) => {
      const r = getRec();
      if (!r) return;
      const on = Math.floor(t * 2.5) % 2 === 0;
      G.ui.box(g, 14, 110, 132, 140, { fill: 'rgba(10,8,16,0.82)' });
      if (on) { g.fillStyle = '#ff3030'; g.fillRect(24, 119, 10, 10); }
      P4().text(g, 'REC  ' + r.t.toFixed(1) + ' / 2.0', 40, 118, '#fff4d6', 12);
    }, { z: 2 });
  }
  C11.closeRec = () => { if (recH) { recH.close(); recH = null; } };

  // ================================================================ 巡逻：一张站点表，一站一站走、停、做事
  //   step = { x, y, face, wait, act, red }：走到 (x, y) → 面朝 face 停 wait 秒；停着的时候 w.act = act（证据要看这个）
  function patrolTick(w, dt) {
    const a = w.a;
    if (!a || a.remove || w.frozen) return;
    const st = w.route[w.i % w.route.length];
    if (w.waitT == null) {
      const dx = st.x - a.x, dy = (st.y == null ? a.y : st.y) - a.y;
      if (Math.abs(dx) < 1.5 && Math.abs(dy) < 1.5) {
        w.waitT = st.wait || 0; a.facing = st.face || a.facing; a.play('idle'); w.act = st.act || null; w.red = !!st.red;
      } else { G.combat.walkTo(a, st.x, st.y == null ? a.y : st.y, dt, w.speed || 40); w.act = null; w.red = false; }
      return;
    }
    w.waitT -= dt;
    if (st.turn && w.waitT < st.turn) a.facing = -(st.face || 1);
    if (w.waitT <= 0) { w.waitT = null; w.i++; w.act = null; w.red = false; }
  }
  C11.patrolTick = patrolTick;
  function spawnNpc(S, cid, id, x, y, facing) {
    let a = S.actor(id);
    if (!a || a.remove) a = S.spawn(cid, x, y, { id, facing });
    Object.assign(a, { x, y, facing, remove: false, visible: true, hold: false, alpha: 1, team: 'npc', script: null, follow: null });
    a.play('idle');
    return a;
  }
  C11.spawnNpc = spawnNpc;

  // ================================================================ 早人的潜行（插曲 b11_spy、最后一次 b18_cat 共用）
  //   o = { id, spots: [[x, y]…], start: [x, y], watchers: (S, d, assist) => [w…], evidence: [{ id, label, mark, when(d, p) }], goal(d, p) → true 赢,
  //         onTick(S, c, dt), failText, steps, mark }
  const HIDE_R = 16, HIDE_DY = 20;
  function stealthFight(S, o) {
    const hay = C11.cid('hayato');
    S.hint(null);
    return S.fight({
      id: o.id, arena: o.arena || [10, 630], lead: hay, swap: false, lockMsg: '这里只有早人一个人',
      music: 'tension', after: null, dmgScale: 1.2, losable: true, playerMinHp: 1, energy: { start: 0 }, bench: { mode: 'hide' },
      kitOverride: { [hay]: NOMOVES },
      gauge: { max: 100, value: 0, label: '被发现', color: '#ff7060', rate: () => 0 },
      steps: o.steps,
      testHint: (c) => {
        const d = c.data, p = player();
        return { sus: Math.round(d.sus || 0), hidden: !!d.hidden, ev: (d.got || []).join(','), rec: d.rec ? d.rec.ev.id : null, x: p ? Math.round(p.x) : null,
          acts: (d.ws || []).map((w) => (w.act || '') + (w.red ? '!' : '')).join('|') };
      },
      tick: (c, dt) => stealthTick(S, c, dt, o),
      endWhen: (c) => !!c.data.won,
    }).then((r) => {
      C11.closeCones(); C11.closeRec();
      const p = player();
      if (p) { p.alpha = 1; p.noGuard = false; }
      return r;
    });
  }
  C11.stealthFight = stealthFight;
  function stealthTick(S, c, dt, o) {
    const d = c.data, p = player();
    if (!p) return;
    if (!d.init) {
      d.init = true; d.sus = 0; d.got = []; d.t = 0;
      p.x = o.start[0]; p.y = o.start[1]; p.facing = o.start[2] || -1; p.noGuard = true; p.alpha = 1; p.hold = false;
      d.ws = o.watchers(S, d, c.assist || c.attempt >= 2);
      if (c.assist) for (const w of d.ws) { w.range *= 0.7; }
      conesOverlay(() => d.ws);
      recOverlay(() => d.rec);
      if (o.onInit) o.onInit(S, c);
      pressed(d, 'special'); pressed(d, 'ok');
    }
    d.t += dt;
    for (const w of d.ws) if (!w.custom) patrolTick(w, dt); else w.custom(w, dt, d);
    if (o.onTick) o.onTick(S, c, dt);
    // 躲：按住 L，离躲的地方 16 px 以内
    const spot = o.spots.find((s) => Math.abs(s[0] - p.x) <= HIDE_R && Math.abs(s[1] - p.y) <= HIDE_DY);
    const hide = G.input.isDown('guard') && !!spot;
    if (hide !== d.hidden) {
      d.hidden = hide;
      p.hold = hide || !!d.rec;
      if (hide) { p.state = 'idle'; p.play('down'); S.sfx('creak', 0.3); } else p.play('idle');
    }
    p.alpha = d.hidden ? 0.55 : 1;
    if (G.input.isDown('guard') && !spot && !d.hideTold && !d.rec) { d.hideTold = true; S.hint('要贴着家具才躲得住（鞋柜、沙发、盆栽、冰箱、房门）', 3); }
    // 视线
    const seen = !d.hidden && d.ws.some((w) => sees(w, p));
    d.sus = G.clamp((d.sus || 0) + (seen ? dt / 0.6 * 100 : -dt * 60), 0, 100);
    if (c.gauge) c.gauge.value = d.sus;
    if (seen && !d.seenSfx) { d.seenSfx = true; S.sfx('sting_shock', 0.45); }
    if (!seen) d.seenSfx = false;
    if (d.sus >= 100) { c.fail(o.failText); return; }
    // U 录像（2 s，录的时候不能动）
    if (pressed(d, 'special') && !d.rec && o.evidence) {
      const ev = o.evidence.find((e) => d.got.indexOf(e.id) < 0 && e.when(d, p));
      if (ev) { d.rec = { ev, t: 0 }; p.hold = true; p.state = 'idle'; if (!d.hidden) p.play('idle'); S.sfx('blip', 0.6); }
      else { S.sfx('menu_error', 0.5); S.emote(p, o.evidence.every((e) => d.got.indexOf(e.id) >= 0) ? '已经够了' : '……现在拍不到什么', 1); }
    }
    if (d.rec) {
      d.rec.t += dt;
      if (!d.rec.ev.when(d, p)) { S.emote(p, '没录完……', 1); d.rec = null; p.hold = d.hidden; }
      else if (d.rec.t >= 2) {
        const ev = d.rec.ev;
        d.rec = null; p.hold = d.hidden;
        d.got.push(ev.id);
        c.step(d.got.length);
        S.sfx('camera_shutter', 0.9);
        S.mark(ev.mark);
        S.hint('录到了：' + ev.label + '（' + d.got.length + ' / ' + o.evidence.length + '）', 3);
      }
    }
    if (pressed(d, 'ok') && o.onOk) o.onOk(S, c, p);
    if (o.help && d.t > 60 && !d.helped && !(d.got || []).length) { d.helped = true; S.hint(o.help, 7); }
    if (o.goal(d, p)) d.won = true;
  }

  // =====================================================================================================================
  // 插曲 爸爸不是爸爸（b11_spy）：kawajiri_ch11 夜
  // =====================================================================================================================
  const KH = { spots: [[81, 160], [247, 160], [304, 160], [397, 160], [524, 160]], start: [596, 160, -1] };
  C11.KH = KH;
  C11.spy = (S) => stealthFight(S, {
    id: 'b11_spy', spots: KH.spots, start: KH.start, steps: { n: 3, label: '证据' },
    failText: '被爸爸发现了……',
    help: '早人·旁白：躲在他看不到的那一边，等他开始做奇怪的事……',
    watchers: (S2) => {
      const ko = spawnNpc(S2, C11.cid('kosaku'), 'c11_kosaku', 300, 150, -1);
      const sh = spawnNpc(S2, C11.cid('shinobu'), 'c11_shinobu', 470, 150, -1);
      return [
        { a: ko, range: 96, dy0: 16, slope: 0.2, speed: 34, i: 0,
          route: [{ x: 236, y: 150, face: -1, wait: 7, act: 'nails' }, { x: 98, y: 150, face: -1, wait: 6, act: 'photo' },
            { x: 440, y: 150, face: 1, wait: 7, act: 'sign' }] },
        { a: sh, range: 72, dy0: 10, slope: 0.14, speed: 30, i: 0,
          route: [{ x: 470, y: 148, face: -1, wait: 4 }, { x: 400, y: 148, face: -1, wait: 3 }] },
      ];
    },
    evidence: [
      { id: 'nails', label: '剪下来的指甲，一片片收进小瓶子', mark: 'b11_ev1', when: (d, p) => evNear(d, p, 'nails', 150) },
      { id: 'photo', label: '盯着全家福里“自己”的脸', mark: 'b11_ev2', when: (d, p) => evNear(d, p, 'photo', 170) },
      { id: 'sign', label: '一遍遍练“川尻浩作”的签名', mark: 'b11_ev3', when: (d, p) => evNear(d, p, 'sign', 150) },
    ],
    onInit: (S2, c) => {
      S2.mark('b11_start');
      S2.hint('按住 L：躲在家具后面　U：用摄像机录下证据（离近一点、朝着他）', 8);
      c.data.actFx = 0;
    },
    onTick: (S2, c, dt) => {
      // 爸爸在做“那件事”的时候头上冒一个小字，玩家看得出来
      const w = c.data.ws[0];
      c.data.actFx -= dt;
      if (w.act && c.data.actFx <= 0) { c.data.actFx = 2.2; S2.emote(w.a, { nails: '咔嚓…咔嚓…', photo: '……', sign: '川尻浩作…' }[w.act], 1.6, '#e0d0ff'); }
    },
    goal: (d) => d.got.length >= 3,
  });
  function evNear(d, p, act, r) {
    const w = d.ws[0], a = w.a;
    if (w.act !== act || !a) return false;
    const dx = a.x - p.x;
    return Math.abs(dx) <= r && Math.abs(a.y - p.y) <= 30 && Math.sign(dx || 1) === (p.facing || 1);
  }

  // =====================================================================================================================
  // 第 18 战 最后一次 段 1：偷猫草（b18_cat），kawajiri_ch11 早上
  // =====================================================================================================================
  C11.cat = (S) => stealthFight(S, {
    id: 'b18_cat', spots: KH.spots, start: KH.start, steps: { n: 2, label: '猫草' },
    failText: '被爸爸看见了……',
    watchers: (S2) => {
      const ko = spawnNpc(S2, C11.cid('kosaku'), 'c11_kosaku', 440, 150, -1);
      const sh = spawnNpc(S2, C11.cid('shinobu'), 'c11_shinobu', 470, 148, -1);
      return [
        // 爸爸坐在餐桌前看报纸，面朝左；每 6 s 抬头扫客厅 2 s（扇形变红、变长）
        { a: ko, range: 60, dy0: 8, slope: 0.12, custom: (w, dt, d) => {
          w.cyc = ((w.cyc || 0) + dt) % 8;
          const look = w.cyc >= 6;
          w.red = look; w.range = look ? 150 : 60; w.dy0 = look ? 40 : 8;
          if (look && !w.told) { w.told = true; G.S.emote(w.a, '……', 1.2); }
          if (!look) w.told = false;
        } },
        { a: sh, range: 64, dy0: 10, slope: 0.14, speed: 30, i: 0,
          route: [{ x: 500, y: 148, face: 1, wait: 4 }, { x: 470, y: 148, face: -1, wait: 3 }] },
      ];
    },
    onInit: (S2, c) => { S2.hint('走到客厅的盆栽那里按 E 拿猫草，再从玄关出去。爸爸抬头的时候（扇形变红）躲好！', 8); },
    onOk: (S2, c, p) => {
      const d = c.data;
      if (!d.cat && Math.abs(p.x - 304) <= 22 && Math.abs(p.y - 156) <= 22) {
        d.cat = true; c.step(1);
        S2.sfx('pop', 0.8);
        S2.mark('b18_cat_ok');
        S2.hint('拿到猫草了！从玄关（左边）出去', 4);
      }
    },
    goal: (d, p) => d.cat && p.x <= 40,
  });

  // =====================================================================================================================
  // 第 18 战 循环 1：出门（b18_go），corner_ch11，没有输赢
  // =====================================================================================================================
  C11.go = (S, toX) => {
    const hay = C11.cid('hayato');
    return S.fight({
      id: 'b18_go', arena: [10, 630], lead: hay, swap: false, music: null, after: null, losable: false, playerMinHp: 1, energy: { start: 0 },
      bench: { mode: 'hide' }, kitOverride: { [hay]: NOMOVES },
      tick: (c, dt) => {
        const d = c.data, p = player();
        if (!d.init) { d.init = true; p.x = 40; p.y = 160; p.facing = 1; S.hint('往右走，去上学', 5); d.min = 480; }
        d.min = Math.min(500, d.min + dt * 0.6);
        S.state('clock', Math.round(d.min));
      },
      endWhen: () => player() && player().x >= toX,
    });
  };

  // =====================================================================================================================
  // 第 18 战 循环 2：躲开露伴（b18_avoid），corner_ch11，8:00 → 8:25
  // =====================================================================================================================
  const CN = { spots: [[206, 158], [270, 158], [359, 158], [589, 158], [71, 158]] };
  C11.CN = CN;
  C11.avoid = (S, hooks) => {
    const hay = C11.cid('hayato');
    S.hint(null);
    return S.fight({
      id: 'b18_avoid', arena: [10, 630], lead: hay, swap: false, music: 'tension', after: null, dmgScale: 1.2, losable: true, playerMinHp: 1,
      energy: { start: 0 }, bench: { mode: 'hide' }, kitOverride: { [hay]: NOMOVES },
      gauge: { max: 100, value: 0, label: '被发现', color: '#ff7060', rate: () => 0 },
      timer: { label: '撑到 8:25：', until: 25 },
      testHint: (c) => ({ sus: Math.round(c.data.sus || 0), hidden: !!c.data.hidden, rx: c.data.ws && c.data.ws[0].a ? Math.round(c.data.ws[0].a.x) : null }),
      tick: (c, dt) => {
        const d = c.data, p = player();
        if (!d.init) {
          d.init = true; d.sus = 0;
          p.x = 240; p.y = 164; p.facing = 1; p.noGuard = true; p.hold = false; p.alpha = 1;
          const ro = spawnNpc(S, C11.cid('rohan'), 'c11_rohan_walk', 680, 152, -1);
          ro.visible = false;
          d.ws = [{ a: ro, range: 90, dy0: 12, slope: 0.15, off: true, custom: (w, dt2) => {
            if (c.t < 5) return;
            if (w.off) { w.off = false; ro.visible = true; S.emote(ro, '那个孩子……在哪？', 1.6); }
            w.turnT = (w.turnT || 0) + dt2;
            // 每 7 s 回头看一眼（1.5 s）
            if (w.turnT % 7 > 5.5) { ro.facing = 1; ro.play('idle'); return; }
            if (ro.x > -20) G.combat.walkTo(ro, ro.x - 1, 152, dt2, 26); else w.off = true;
          } }];
          conesOverlay(() => d.ws);
          if (hooks && hooks.init) hooks.init(S, c);
          S.hint('露伴老师会从右边过来找你：贴着小路口、邮筒、反射镜、售货机按住 L 躲好', 8);
        }
        for (const w of d.ws) w.custom(w, dt);
        S.state('clock', 480 + Math.min(25, Math.floor(c.t)));
        if (hooks && hooks.tick) hooks.tick(S, c, dt);
        const spot = CN.spots.find((s) => Math.abs(s[0] - p.x) <= HIDE_R && Math.abs(s[1] - p.y) <= HIDE_DY);
        const hide = G.input.isDown('guard') && !!spot;
        if (hide !== d.hidden) { d.hidden = hide; p.hold = hide; if (hide) { p.state = 'idle'; p.play('down'); } else p.play('idle'); }
        p.alpha = d.hidden ? 0.55 : 1;
        const seen = !d.hidden && d.ws.some((w) => sees(w, p));
        d.sus = G.clamp(d.sus + (seen ? dt / 0.5 * 100 : -dt * 60), 0, 100);
        if (c.gauge) c.gauge.value = d.sus;
        if (d.sus >= 100) c.fail('被露伴老师看见了……');
      },
      endWhen: (c) => c.t >= 25,
    }).then((r) => { C11.closeCones(); const p = player(); if (p) { p.alpha = 1; p.noGuard = false; p.hold = false; } return r; });
  };

  // =====================================================================================================================
  // 第 17 战 段 A：十字路口（b17a_street），露伴，背不能被看到
  // =====================================================================================================================
  const ST = { exitX: 930, cross: [404, 576], wallY: 146 };
  const WALKERS = [
    ['thug_a', 120, 166, 1, 38, [20, 380]], ['fan_a', 300, 158, -1, 32, [60, 400]], ['flirt', 470, 168, 1, 40, [300, 700]],
    ['fan_b', 640, 156, -1, 30, [420, 860]], ['kid', 780, 172, 1, 44, [600, 940]], ['thug_b', 900, 162, -1, 34, [640, 930]],
  ];
  function hdWrite(S, c, p) {
    const d = c.data;
    if ((d.hdCd || 0) > 0) { S.emote(p, '……等一下', 0.8); return; }
    const t = d.walkers.find((w) => { const dx = (w.a.x - p.x) * p.facing; return dx >= 0 && dx <= 60 && Math.abs(w.a.y - p.y) <= 22; });
    if (!t) { S.emote(p, '……前面没人', 0.8); return; }
    d.hdCd = 4;
    t.awayT = 5; t.a.facing = t.a.x > p.x ? 1 : -1;
    S.sfx('card_flip', 0.8); S.sfx('sparkle', 0.5);
    S.sfxText('天堂之门', t.a, { dur: 0.9 });
    S.emote(t.a, '向后转，走开', 1.4, '#f0d070');
    if (!d.hdMarked) { d.hdMarked = true; S.mark('b17a_hd'); }
  }
  C11.street = (S) => {
    const ro = C11.cid('rohan');
    S.hint(null);
    return S.fight({
      id: 'b17a_street', arena: [10, 950], lead: ro, swap: false, lockMsg: '只有露伴背着 Cheap Trick', music: 'battle', after: null,
      dmgScale: 1.2, losable: true, playerMinHp: 1, energy: { start: 0 }, bench: { mode: 'stay' }, kitOverride: { [ro]: NOMOVES },
      gauge: { max: 100, value: 0, label: '背后', color: '#c8a0ff', rate: () => 0 },
      testHint: (c) => ({ back: Math.round(c.data.back || 0), x: Math.round(player().x), y: Math.round(player().y), sig: c.data.sig,
        ws: (c.data.walkers || []).map((w) => Math.round(w.a.x) + (w.a.facing > 0 ? '>' : '<') + Math.round(w.a.y)).join(' ') }),
      tick: (c, dt) => {
        const d = c.data, p = player();
        if (!d.init) {
          d.init = true; d.back = 0; d.pushT = 6; d.sigT = 0; d.sig = 0; d.hdCd = 0;
          p.x = 30; p.y = 144; p.facing = 1; p.hold = false; p.noGuard = true;
          S.state('signal', 0);
          d.walkers = WALKERS.map(([cid, x, y, f, sp, rg], i) => ({ a: spawnNpc(S, cid, 'c11_walker' + i, x, y, f), sp, rg, awayT: 0 }));
          d.ko = S.actor('koichi');
          d.cones = d.walkers.map((w) => ({ a: w.a, range: 84, dy0: 14, slope: 0 }));
          conesOverlay(() => d.cones);
          pressed(d, 'special');
          S.mark('b17a_start');
          S.hint('贴着店铺的墙走（按 ↑ 贴到最里面），别让背后的人看到你的背。U：天堂之门，让前面的人转身走开', 9);
        }
        // 红绿灯 10 s 一换（只是街景；大路上没有墙，过马路要小心）
        d.sigT += dt;
        if (d.sigT >= 10) { d.sigT = 0; d.sig = 1 - d.sig; S.state('signal', d.sig); }
        d.hdCd = Math.max(0, d.hdCd - dt);
        for (const w of d.walkers) {
          const a = w.a;
          if (w.awayT > 0) { w.awayT -= dt; G.combat.walkTo(a, a.x + a.facing * 10, a.y, dt, w.sp * 1.4); continue; }
          if (a.x <= w.rg[0]) a.facing = 1; else if (a.x >= w.rg[1]) a.facing = -1;
          G.combat.walkTo(a, a.x + a.facing * 10, a.y, dt, w.sp);
        }
        // 康一跟在后面
        if (d.ko && !d.ko.remove) {
          const tx = p.x - p.facing * 22;
          if (Math.abs(d.ko.x - tx) > 4) G.combat.walkTo(d.ko, tx, G.clamp(p.y + 10, 150, 176), dt, 64); else d.ko.play('idle');
        }
        // 背：路人在露伴背后、面朝他，露伴又没贴着墙（斑马线上没有墙）
        const onWall = p.y <= ST.wallY && !(p.x > ST.cross[0] && p.x < ST.cross[1]);
        let n = 0;
        for (const w of d.walkers) {
          const a = w.a;
          if (w.awayT > 0 || onWall) continue;
          const behind = (a.x - p.x) * p.facing < 0, toward = Math.sign(p.x - a.x) === a.facing;
          if (behind && toward && Math.abs(a.x - p.x) <= 84 && Math.abs(a.y - p.y) <= 14) n++;
        }
        d.back = G.clamp(d.back + (n ? n * 60 * dt : -30 * dt), 0, 100);
        if (c.gauge) c.gauge.value = d.back;
        if (n && !d.warned) { d.warned = true; S.sfx('sting_shock', 0.5); S.emote(p, '……背后有人', 0.9); }
        if (!n) d.warned = false;
        if (d.back >= 100) { c.fail('有人看到了露伴的背……'); return; }
        // Cheap Trick 每 9 s 推一下
        d.pushT -= dt;
        if (d.pushT <= 0) {
          d.pushT = 9;
          p.y = Math.min(176, p.y + 12);
          S.sfx('whoosh', 0.5);
          S.emote(p, ['诶～那位大姐，看看这边嘛！', '露伴老师的背，很好看哦～', '大家快看过来～'][(d.pushN = (d.pushN || 0) + 1) % 3], 1.6, '#c8c0e8');
          if (d.pushN === 1 && d.ko) S.emote(d.ko, '露伴老师，贴着墙！', 1.6, '#9be070');
        }
        if (pressed(d, 'special')) hdWrite(S, c, p);
        if (p.x >= ST.exitX && !d.won) { d.won = true; S.mark('b17a_clear'); }
      },
      endWhen: (c) => !!c.data.won,
    }).then((r) => {
      C11.closeCones();
      for (let i = 0; i < WALKERS.length; i++) { const a = S.actor('c11_walker' + i); if (a) a.remove = true; }
      const p = player(); if (p) p.noGuard = false;
      return r;
    });
  };

  // =====================================================================================================================
  // 第 17 战 段 B：幽灵小路（b17b_alley），不能回头
  // =====================================================================================================================
  const VOICES = ['露伴老师——', '掉东西了哦——', '岸边先生？', '回头看看嘛……', '你的速写本……'];
  C11.alley = (S) => {
    const ro = C11.cid('rohan');
    S.hint(null);
    return S.fight({
      id: 'b17b_alley', arena: [10, 630], lead: ro, swap: false, music: 'tension', after: null, dmgScale: 1.2, losable: true, playerMinHp: 1,
      energy: { start: 0 }, bench: { mode: 'hide' }, kitOverride: { [ro]: NOMOVES },
      steps: { n: 1, label: '走到出口，别回头' },
      testHint: (c) => ({ x: Math.round(player().x), uWin: !!c.data.uWin, pulls: c.data.pulls || 0 }),
      tick: (c, dt) => {
        const d = c.data, p = player();
        if (!d.init) {
          d.init = true; d.nextV = 110; d.pullT = 5; d.pulls = 0;
          p.x = 40; p.y = 156; p.facing = 1; p.hold = false; p.noGuard = true;
          S.state('dark', 0); S.state('hands', 0);
          pressed(d, 'special');
          S.mark('b17b_start');
          S.hint('往右走到出口。绝对不要回头（别按 ←）', 7);
        }
        if (p.facing < 0 && !d.turned) { d.turned = true; turnBack(S, c); return; }
        if (p.x >= d.nextV && p.x < 520) {
          d.nextV += 90;
          const v = VOICES[(d.vi = (d.vi || 0) + 1) % VOICES.length];
          S.sfxText(v, { wx: p.x - 70, wy: p.y - 30, wz: 0 }, { dur: 1.4 });
          S.sfx('wind', 0.4);
          S.state('dark', Math.min(1, (G.world.stage.state.dark || 0) + 0.34));
        }
        // Cheap Trick 扳头：连按 J 顶住
        d.pullT -= dt;
        if (d.pullT <= 0 && !d.uWin && !d.busy) {
          d.pullT = 7; d.busy = true;
          cine(c, async () => {
            S.emote(p, '它在扳我的头……！', 1.2);
            S.sfx('creak', 0.7);
            const ok = await S.mash({ need: c.assist ? 5 : 8, time: 1.6, label: '连按 J！顶住！' });
            d.busy = false; d.pulls++;
            if (!ok) { p.facing = -1; }
          });
        }
        if (p.x >= 520 && !d.uWin && !d.done) { d.uWin = true; d.uT = 4; S.sfx('sting_reveal', 0.6); S.emote(p, '', 0.1); S.hint('铃美：「就是现在！」　按 U！', 4); pressed(d, 'special'); }
        if (d.uWin) {
          d.uT -= dt;
          if (pressed(d, 'special')) { d.uWin = false; d.done = true; cine(c, () => C11.onAlleyU(S, c)); }
          else if (d.uT <= 0) { d.uWin = false; S.emote(p, '它又爬回肩膀上了……', 1.2); p.x = Math.max(40, p.x); d.retryX = p.x + 30; }
        }
        if (!d.uWin && !d.done && d.retryX && p.x >= d.retryX) { d.retryX = null; d.uWin = true; d.uT = 4; S.hint('按 U！', 3); }
      },
      endWhen: (c) => !!c.data.won,
    }).then((r) => { const p = player(); if (p) p.noGuard = false; S.state('hands', 0); return r; });
  };
  async function turnBack(S, c) {
    await cine(c, async () => {
      S.state('hands', 1);
      S.sfx('sting_shock', 0.8);
      S.shake(2, 0.4);
      await S.wait(0.8);
    });
    c.fail('露伴回头了……');
  }
  // 剧情那边会把 onAlleyU 换成真正的演出（Cheap Trick 回头 → 被拖走），演完设 c.data.won
  C11.onAlleyU = async (S, c) => { c.data.won = true; };
})();
