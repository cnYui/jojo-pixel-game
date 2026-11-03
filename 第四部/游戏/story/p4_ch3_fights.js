// 第3章　海边别墅 / 由花子与意大利菜：战斗和小游戏（开发脚本 第四部/docs/第3章_开发脚本.md §3）。剧情节拍在 story/p4_ch3.js。
//   第5战段 1「逃脱」b05_escape（康一 ACT1，计时）、段 2「别墅」b05_lovedeluxe（康一 ACT2 对由花子）、段 3「海岬」b05_cape（选字 + U，不会输）、
//   小游戏「东尼欧的晚餐」mg_tonio（仗助一个人，4 轮，每轮一场）。都是 S.fight：没有敌人的段落 waves 留空、自己的 tick 判定结束，
//   这样玩家的按键（E、J、方向键）在战斗状态下照常进来，机器人（tools/dev/p4_bot_ch3.js）也能照着打。
//   康一 ACT1 的招式组 G.KITS.koichi、亿泰、回音 ACT1 都是第2章的（engine/p4_moves.js、chars_ch2.json）；ACT2 在这里派生 K.koichi_act2。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const C3 = (G.P4CH3 = { F: {} });
  const W = () => G.world;
  const player = () => G.world.player;
  const S0 = () => G.S;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  C3.OKU = () => 'okuyasu';
  C3.ECH1 = () => 'echoes1';
  // 康一：换上回音（act 1 / 2）。战斗动作用第2章补的康一本体（chars/koichi_ex：cmd、hurt、down、dodge、guard）
  C3.koichiGear = (a, act) => {
    if (!a) return a;
    if (act) {
      const sid = act === 2 ? 'echoes2' : C3.ECH1();
      if (a.standId !== sid || !a.stand) a.setStand(sid);
    }
    return a;
  };

  // 在战斗里插一段演出：把 W.cine 占住（玩家、敌人、战斗 tick 都停），演完还回去（写法同序章 p4_pro_fights.js）
  async function cine(ctx, fn) {
    const Wd = G.world, run = G.runId;
    if (Wd.fight !== ctx) return;
    const old = Wd.cine;
    Wd.cine = { by: 'p4-ch3' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && Wd.fight === ctx) Wd.cine = old || null; }
  }
  C3.cine = cine;
  // 战斗专用的叠加层：战斗结束（或换了一场）就自己关
  function fightOverlay(ctx, fn, z) {
    const h = P4().overlay((g, t) => { if (G.world.fight !== ctx) { h.close(); return; } fn(g, t); }, { z: z || 0 });
    return h;
  }
  const w2u = (x, y, z) => (G.cam && G.cam.w2u ? G.cam.w2u(x, y, z || 0) : { x: (x - (G.cam ? G.cam.x : 0)) * 2, y: y * 2 });
  const txt = (g, s, x, y, col, size, align, out) => P4().text(g, s, x, y, col, size || 12, align || 'left', out === undefined ? '#130b20' : out);

  // ================================================================ 康一：段 1 用第2章的 ACT1（J 射拟声字），只给字弹加一个“飞到头冒火星”（好知道打到门口没有）；
  //   ACT2 派生 K.koichi_act2：J 尾巴抽打（前方 10–58 px，6 / 6 / 10），声音陷阱在战斗 tick 里（按住 L 再按 J）
  const fizzleShot = (m) => Object.assign({}, m, { shot: Object.assign({}, m.shot, { fizzle: { name: 'sparkles', kw: { n: 3, radius: 5, colour: '#9cf0c0', period: 0.3 }, life: 0.25 } }) });
  M.EC3_J1 = fizzleShot(M.EC_J1);
  M.EC3_J2 = fizzleShot(M.EC_J2);
  M.EC3_J3 = fizzleShot(M.EC_J3);
  const ACT1 = Object.assign({}, K.koichi, { combo: ['EC3_J1', 'EC3_J2', 'EC3_J3'], special: null });
  const tail = (slot, dmg, push, o) => Object.assign({
    slot, body: 'cmd', stand: 'punch', standDx: 10, dur: f(20), active: [f(6), f(10)], from: 'body', reach: [10, 58], depth: 9,
    dmg, push, energy: 2, link: f(10), cancel: f(10), step: 2, sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light', accent: '#d0e080', shake: [1, f(6)],
  }, o || {});
  M.EC2_T1 = tail('J1', 6, 6);
  M.EC2_T2 = tail('J2', 6, 6, { sfxRate: 1.1 });
  M.EC2_T3 = tail('J3', 10, 18, { dur: f(26), active: [f(8), f(12)], step: 3, sfxHit: 'punch_heavy', fxHit: 'heavy', word: '啪！', shake: [2, f(10)] });
  K.koichi_act2 = Object.assign({}, K.koichi, {
    standId: 'echoes2', combo: ['EC2_T1', 'EC2_T2', 'EC2_T3'], rush: null, parry: {}, special: null, explore: { pose: 'punch' },
  });

  // ================================================================ 山岸由花子 · 爱的豪华（敌人）
  //   头发鞭：竖起 0.4 s（W1）→ 往前横扫 60 px，12；头发抓：脚下冒发丝 0.6 s（W3 地面圈）→ 踩中拉到她面前撞一下，16
  M.YK_WHIP = {
    slot: 'enemy', body: 'cmd', warn: { tier: 'W1', dur: 0.4 }, dur: 0.4 + 0.4, active: [0.4, 0.52], reach: [0, 60], depth: 12,
    dmg: 12, push: 14, guard: 'normal', sfx: 'whoosh', sfxHit: 'slash', fxHit: 'light', accent: '#5a3a8a', shake: [2, f(8)],
    onStart: (a) => { if (G.fx) G.fx.spawn('slash_arc', { x: a.x + a.facing * 26, y: a.y - 18, size: 22 }, { by: a, life: 0.25 }); },
  };
  M.YK_GRAB = {
    slot: 'enemy', body: 'cmd', warn: { tier: 'W3', dur: 0.6 }, dur: 0.6 + 0.4, active: [0.6, 0.75], melee: false, hazardAt: 0,
    hazard: (a) => {
      const p = G.world.player;
      if (!p) return null;
      return {
        shape: 'ellipse', x: p.x, y: p.y, rx: 13, ry: 7, warn: 0.6, dur: 0.15, dmg: 16, push: 0, guard: 'normal', sfx: 'slime', sfxHit: 'thud',
        onActive: (h) => grabActive(h, a), onHit: (h, t) => grabPull(a, t),
      };
    },
  };
  function grabActive(h, a) {
    const d = (G.world.fight && G.world.fight.data) || {}, p = G.world.player;
    // 康一站在自己贴的「啪嘤」上：抓空，她反被弹开
    const tr = p && (d.traps || []).find((q) => q.kind === 2 && Math.abs(q.x - p.x) < 14 && Math.abs(q.y - p.y) < 8);
    if (tr) { h.x = -9999; trapFire(tr, a, true); }
  }
  function grabPull(a, t) {
    if (!t || t !== G.world.player) return;
    const tx = clamp(a.x + a.facing * 16, G.world.stage.x0 + 8, G.world.stage.x1 - 8);
    G.combat.tweenTo(t, tx, a.y, 0.2);
    if (G.uifx) G.uifx.sfx('咚', t);
    if (G.fx) G.fx.spawn('wrap', { x: t.x, y: t.y, h: 22, w: 10, n: 3, kind: 'tendril', colour: '#2a1838' }, { by: a, life: 0.5, follow: t });
  }
  K.e_yukako = {
    hp: 900, speed: 52, moves: ['YK_WHIP', 'YK_GRAB'], koStyle: 'none', idle: 'idle', poiseMax: 60,
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player;
      if (!p) return true;
      if (m.hold) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      e.facing = p.x > e.x ? 1 : -1;
      const dx = Math.abs(p.x - e.x);
      if (dx > 54 || Math.abs(p.y - e.y) > 6) G.AI.approach(e, p, 46, dt);
      else { if (e.state === 'walk') e.state = 'idle'; e.play('idle'); }
      m.gap = (m.gap == null ? 1.4 : m.gap) - dt;
      if (m.gap > 0 || G.combat.tokens() >= 1) return true;
      const near = dx <= 66 && Math.abs(p.y - e.y) <= 10;
      if ((d.yrelease || 0) > 0 || (near && Math.random() < 0.6)) G.AI.tele(e, 'YK_WHIP');
      else G.AI.tele(e, 'YK_GRAB');
      m.gap = (ctx && ctx.assist ? 2.2 : 1.6) + Math.random() * 0.8;
      return true;
    },
  };

  // =====================================================================================================================
  // 第5战段 1　逃脱（b05_escape）：60 s（第二次起 / 放水 90 s）里做完三件事：听（U）、拨号（窗边 E）、挡门（鞋柜 + 电椅 E，连按 J 钉住）
  // =====================================================================================================================
  const VL = { door: 57, shoe: 107, chair: 535, window: 607, shoeTo: 78, chairTo: 104, phoneDir: 1 };
  const NUMBER = '3524189';
  const PAD = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['*', '0', '#']];
  const PAD_RATE = { 1: 0.8, 2: 0.86, 3: 0.92, 4: 0.98, 5: 1.04, 6: 1.1, 7: 1.16, 8: 1.22, 9: 1.28, '*': 0.7, 0: 1.34, '#': 0.74 };
  function escProps(S) {
    for (const id of ['vl_shoe', 'vl_chair']) { const a = S.actor(id); if (a) a.remove = true; }
    S.state('shoebox', 0); S.state('chair', 0);
    T().prop(S, 'shoecab', VL.shoe, 139, { id: 'vl_shoe' });
    T().prop(S, 'echair', VL.chair, 141, { id: 'vl_chair' });
  }
  async function listen(S, c) {
    const d = c.data, p = player();
    C3.koichiGear(p, 1);
    await S.summon(p, { dur: 0.12, rise: 3 });
    S.standAct(p, 'cast', { dx: 8, z: 8, dur: 1.2 });
    S.sfx('blip', 0.6);
    d.listenUntil = c.t + 4.5;
    if (!d.listened) {
      d.listened = true;
      S.mark('b05a_listen');
      await S.say('koichi', '……窗外。四十多米外有个公用电话亭！', { expr: 'shock' });
      await S.say('koichi', '回音能把声音送过去……按号码的声音也行！');
      S.hint('窗边（最右边）按 E：让回音学出按键的声音拨号', 6);
    }
    S.recall(p);
  }
  async function pushToDoor(S, c, which) {
    const d = c.data, p = player(), id = which === 'shoe' ? 'vl_shoe' : 'vl_chair', pr = S.actor(id);
    if (!pr) return;
    const to = which === 'shoe' ? VL.shoeTo : VL.chairTo;
    if (!d[which + 'Moved']) {
      d[which + 'Moved'] = true;
      p.facing = to < pr.x ? -1 : 1;
      p.x = pr.x - p.facing * 16; p.y = Math.max(p.y, 150);
      S.pose(p, 'guard');
      S.sfx('metal_scrape', 0.6);
      const x0 = pr.x, px0 = p.x, dur = Math.max(0.6, Math.abs(x0 - to) / 160);
      await S.animate(dur, (k) => { pr.x = G.lerp(x0, to, k); p.x = G.lerp(px0, to - p.facing * 16, k); if (Math.random() < 0.15) S.sfx('footstep0', 0.3); });
      S.unpose(p);
      S.sfx('thud', 0.8); S.shake(2, 0.2);
    }
    const ok = await S.mash({ need: 10, time: 3, label: '连按 J！钉住它！' });
    if (ok) {
      d[which + 'Nailed'] = true;
      S.sfx('crash', 0.6);
      S.fx('sparkles', { x: pr.x, y: pr.y - 16, n: 5, radius: 10, colour: '#d8ffb0', period: 0.4 }, { life: 0.6 });
      S.sfxText('咚咚！', { wx: pr.x, wy: pr.y - 20, wz: 0 }, { dur: 0.8 });
      if (d.shoeNailed && d.chairNailed) {
        S.mark('b05a_barricade');
        await S.say('koichi', '门口堵上了……这下她进不来了吧。');
      } else await S.say('koichi', which === 'shoe' ? '还有书桌那把电椅……也推过去！' : '鞋柜也推过去堵上！');
    } else S.hint('没钉牢：站在它旁边再按 E，连按 J', 5);
  }
  // 拨号盘（窗边 E 打开）：←→↑↓ 选键，J 让回音学出那个音；K / L 收起
  function dialTick(S, c) {
    const d = c.data, dl = d.dial, I = G.input, p = player();
    if (!dl) return;
    p.hold = true;
    if (I.hit('left')) dl.c = (dl.c + 2) % 3;
    if (I.hit('right')) dl.c = (dl.c + 1) % 3;
    if (I.hit('up')) dl.r = (dl.r + 3) % 4;
    if (I.hit('down')) dl.r = (dl.r + 1) % 4;
    if (I.hit('left') || I.hit('right') || I.hit('up') || I.hit('down')) S.sfx('menu_move', 0.4);
    if (I.hit('dodge') || I.hit('guard')) { d.dial = null; p.hold = false; return; }
    if (I.hit('attack')) {
      const key = PAD[dl.r][dl.c];
      S.sfx('blip', 0.7, PAD_RATE[key] || 1);
      dl.flash = { key, t: c.t };
      if (key === NUMBER[dl.typed.length]) {
        dl.typed += key;
        if (dl.typed.length === NUMBER.length) {
          d.dial = null; p.hold = false; d.dialed = true;
          cine(c, async () => {
            S.sfx('ding', 0.6);
            await S.wait(0.4);
            S.sfxText('嘟——', { wx: VL.window - 10, wy: 100, wz: 0 }, { dur: 1.0 });
            await S.wait(0.7);
            await S.say('josuke', '喂？……康一？！你在哪儿？', { name: '电话那头（仗助）' });
            await S.say('koichi', '仗助君！我被关在一栋海边的别墅里……', { expr: 'shock' });
            S.mark('b05a_dial');
          });
        }
      } else { S.sfx('menu_error', 0.6); S.sfxText('滋', p, { dur: 0.5 }); }
    }
  }
  function drawDial(g, c) {
    const dl = c.data.dial;
    if (!dl) return;
    const x0 = 420, y0 = 96, w = 196, h = 200;
    G.ui.box(g, x0, y0, x0 + w, y0 + h, { fill: 'rgba(20,28,16,0.94)' });
    txt(g, '拨号（回音学声音）', x0 + 10, y0 + 8, '#d8ffb0', 12);
    txt(g, '纸条：352 4189', x0 + 10, y0 + 26, '#fff4d6', 12);
    const shown = (dl.typed + '_______').slice(0, 7);
    txt(g, shown.slice(0, 3) + ' ' + shown.slice(3), x0 + w / 2, y0 + 46, '#ffe070', 16, 'center');
    for (let r = 0; r < 4; r++) for (let k = 0; k < 3; k++) {
      const bx = x0 + 34 + k * 46, by = y0 + 72 + r * 28, sel = r === dl.r && k === dl.c;
      const lit = dl.flash && dl.flash.key === PAD[r][k] && c.t - dl.flash.t < 0.2;
      g.fillStyle = lit ? '#ffe070' : sel ? '#8ab050' : '#3a4a2a'; g.fillRect(bx, by, 38, 22);
      g.fillStyle = sel ? '#ffffff' : '#6a7a5a'; g.fillRect(bx, by, 38, 2);
      txt(g, PAD[r][k], bx + 19, by + 4, lit ? '#2a1a00' : '#ffffff', 12, 'center');
    }
    txt(g, '←→↑↓ 选　J 按　K 收起', x0 + w / 2, y0 + h - 18, '#c8d8b8', 12, 'center');
  }
  function drawListen(g, c) {
    const d = c.data;
    if (!(d.listenUntil > c.t)) return;
    const k = Math.floor(c.t * 6) % 3;
    for (let i = 0; i < 4; i++) {
      const x = 604 - i * 10 - (k === i % 3 ? 2 : 0);
      g.fillStyle = 'rgba(200,255,160,' + (0.8 - i * 0.18) + ')';
      g.fillRect(x, 150 - i * 8, 3, 60 + i * 16);
    }
    txt(g, '电话亭 →', 588, 128, '#d8ffb0', 12, 'right');
    const left = G.hud.timer ? G.hud.timer.left : 60;
    txt(g, left > 30 ? '脚步：还远' : '脚步：越来越近', 320, 300, left > 30 ? '#d8ffb0' : '#ff9a7a', 16, 'center');
  }
  function escSetup(S, c) {
    const d = c.data, p = player();
    d.limit = c.attempt >= 1 || c.assist ? 90 : 60;
    if (G.hud.timer) { G.hud.timer.until = d.limit; G.hud.timer.left = d.limit; }
    escProps(S);
    C3.koichiGear(p, 1);
    Object.assign(p, { x: 548, y: 156, facing: -1 });
    c.on('fizzle', (e) => {
      const s = e.shot;
      if (!s || s.owner !== player()) return;
      if (s.x < VL.door + 50 && !C3.F.hateNote) {
        C3.F.hateNote = true;
        cine(c, async () => {
          S.sfxText('我讨厌你', { wx: VL.door, wy: 100, wz: 0 }, { dur: 3 });
          S.sfx('sting_comedy', 0.7);
          await S.narrate('……她回来看到这个，大概也只会觉得我在害羞。', { pos: 'top' });
        });
      }
    });
    d.ov = fightOverlay(c, (g) => { drawListen(g, c); drawDial(g, c); }, 2);
    S.mark('b05a_start');
    S.hint('E 调查　J 回音射字　U 听声音：三件事都做完再逃！', 7);
  }
  function escTick(S, c, dt) {
    const d = c.data, p = player(), I = G.input;
    if (!p) return;
    if (G.hud.timer && G.hud.timer.until !== d.limit) G.hud.timer.until = d.limit;
    if (c.t >= d.limit) { c.fail('由花子回来了……'); return; }
    if (d.dial) { dialTick(S, c); return; }
    if (I.hit('special')) { cine(c, () => listen(S, c)); return; }
    if (I.hit('ok')) {
      const near = (x, r) => Math.abs(p.x - x) <= (r || 22);
      const shoe = S.actor('vl_shoe'), chair = S.actor('vl_chair');
      if (near(VL.window, 30)) { d.dial = { r: 0, c: 0, typed: d.dialed ? NUMBER : '' }; if (d.dialed) { d.dial = null; S.hint('电话已经打通了', 3); } else S.hint('←→↑↓ 选键，J 按：352 4189', 5); return; }
      if (shoe && near(shoe.x, 24) && !d.shoeNailed) { cine(c, () => pushToDoor(S, c, 'shoe')); return; }
      if (chair && near(chair.x, 24) && !d.chairNailed) { cine(c, () => pushToDoor(S, c, 'chair')); return; }
    }
    if (!d.started) {
      d.started = true;
      cine(c, async () => {
        await S.say('koichi', '（手机没有……门被锁上了。窗户是封死的。）');
        await S.say('koichi', '（她说一会儿就回来。得在那之前想办法！）', { expr: 'shock' });
      });
    }
  }
  C3.escape = async function (S) {
    S.hint(null);
    const kitA1 = Object.assign({}, ACT1);
    return S.fight({
      id: 'b05_escape', arena: [16, 628], lead: 'koichi', swap: false, music: 'tension', after: null, losable: true,
      playerMinHp: 1, energy: { start: 0 }, waves: [], timer: { label: '由花子回来', until: 60 },
      kitOverride: { koichi: kitA1 },
      onRetry: async (S2) => { escSetup(S2, G.world.fight); },
      tick: (c, dt) => { if (!c.data.init) { c.data.init = true; escSetup(S, c); } escTick(S, c, dt); },
      testHint: (c) => ({ listened: !!c.data.listened, dialed: !!c.data.dialed, shoe: !!c.data.shoeNailed, chair: !!c.data.chairNailed, dial: c.data.dial ? c.data.dial.typed : null }),
      endWhen: (c) => !!(c.data.listened && c.data.dialed && c.data.shoeNailed && c.data.chairNailed && !G.world.cine),
    });
  };

  // =====================================================================================================================
  // 第5战段 2　别墅（b05_lovedeluxe）：康一 ACT2 对由花子（900 血，打到 25%）
  // =====================================================================================================================
  const TRAPS = ['轰', '滋', '啪嘤'];
  const TRAP_COL = ['#ff8a4a', '#ffe070', '#ff9ad8'];
  function placeTrap(S, c) {
    const d = c.data, p = player();
    d.traps = d.traps || [];
    const kind = (d.trapN = (d.trapN || 0) + 1) % 3 === 1 ? 0 : d.trapN % 3 === 2 ? 1 : 2;
    if (d.traps.length >= 3) d.traps.shift();
    d.traps.push({ kind, x: p.x, y: p.y, t: c.t });
    S.standAct(p, 'cast', { dx: 6, z: 2, dur: 0.4 });
    S.sfx('pop', 0.7);
    S.sfxText(TRAPS[kind], { wx: p.x, wy: p.y - 4, wz: 0 }, { dur: 0.5 });
    if (!d.trapTold) { d.trapTold = true; S.hint('贴好了。把由花子引过来踩上去！（「轰」炸、「滋」烫、「啪嘤」弹开）', 6); }
  }
  function trapFire(tr, yk, onKoichi) {
    const c = G.world.fight, d = c ? c.data : null, S = S0(), p = player();
    if (!d || !yk) return;
    d.traps = (d.traps || []).filter((q) => q !== tr);
    if (!d.trapHit) { d.trapHit = true; S.mark('b05b_trap'); }
    if (tr.kind === 0) {
      S.fx('explosion', { x: tr.x, y: tr.y - 8, size: 1.1 }, { life: 0.5 });
      S.sfx('explosion', 0.8); S.shake(4, 0.3);
      G.combat.hit(p, yk, { slot: 'shot', dmg: 40, push: 22, guard: 'none', sfxHit: 'punch_heavy', fxHit: 'heavy', word: '轰！', accent: '#ff8a4a' });
    } else if (tr.kind === 1) {
      S.fx('lightning', { x0: yk.x - 8, y0: yk.y - 40, x1: yk.x + 6, y1: yk.y, colour: '#fff4a0' }, { life: 0.4 });
      S.sfx('crossfire', 0.6);
      G.combat.hit(p, yk, { slot: 'shot', dmg: 30, push: 6, guard: 'none', sfxHit: 'fire_burst', fxHit: 'light', word: '滋——', accent: '#ffe070' });
      d.yrelease = 2;
    } else {
      const dir = onKoichi ? (yk.x > p.x ? 1 : -1) : (yk.x >= tr.x ? 1 : -1);
      const st = G.world.stage, tx = clamp(yk.x + dir * 60, st.x0 + 8, st.x1 - 8);
      S.sfx('pop', 1); S.sfx('whoosh', 0.6);
      yk.atk = null; yk.tele = null; yk.state = 'hurt'; yk.stateT = 0; yk._hurtDur = 0.5; yk.play('hurt');
      S.sfxText('啪嘤！', yk, { dur: 0.7 });
      G.combat.tweenTo(yk, tx, yk.y, 0.3);
      if (onKoichi) S.emote(p, '抓空了！', 1, '#d8ffb0');
    }
  }
  async function burnTether(S, p, c) {
    const d = c.data, yk = S.actor('yukako');
    d.uUsed = true;
    S.hint(null);
    S.standAct(p, 'cast', { dx: 6, z: 10, dur: 0.6 });
    S.sfx('crossfire', 0.8);
    if (yk) S.fx('lightning', { x0: p.x, y0: p.y - 24, x1: yk.x, y1: yk.y - 26, colour: '#fff4a0' }, { life: 0.5 });
    S.sfxText('滋——', p, { dur: 0.8 });
    await S.wait(0.5);
    d.tether = false;
    S.mark('b05b_scalp');
    await S.say('koichi', '回音往发丝上贴了「滋」……烧断了！', { expr: 'shock' });
    await S.say('yukako', '……康一君，你真的变了呢。', { expr: 'rage' });
    S.hint('J 尾巴抽打　按住 L 再按 J：在脚下贴字陷阱　K 闪避', 7);
  }
  function seal(S, c, n) {
    const st = G.world.stage, key = ['hair_window', 'hair_stairs', 'hair_door'][n - 1];
    S.state(key, 1);
    S.sfx('slime', 0.8); S.shake(2, 0.3);
    if (n === 1) st.x1 -= 40;
    if (n === 2) st.x0 += 40;
    for (const a of [player(), S.actor('yukako')]) if (a) a.x = clamp(a.x, st.x0 + 6, st.x1 - 6);
    S.hint(['头发把窗户封住了……', '楼梯也被封住了！', '门口全是头发：逃不出去了！'][n - 1], 4);
  }
  function ldSetup(S, c) {
    const d = c.data, p = player(), yk = S.actor('yukako');
    C3.koichiGear(p, 2);
    Object.assign(p, { x: 170, y: 158, facing: -1 });
    if (yk) { Object.assign(yk, { x: 96, y: 156, facing: 1, skin: null }); }
    S.state('hair_window', 0); S.state('hair_stairs', 0); S.state('hair_door', 0); S.state('hair_walls', 1);
    d.tether = true; d.pullT = 0; d.sealT = 0; d.seals = 0; d.traps = []; d.lastAtk = G.input.lastPress('attack');
    d.hpMark = yk ? yk.hp : 900; d.markT = 0; d.kTold = false;
    d.ov = fightOverlay(c, (g) => drawLD(g, c), 0);
    S.mark('b05b_start');
    S.hint('头皮里连着她的头发！趁现在按 U：让回音往发丝上贴「滋」', 7);
  }
  function drawLD(g, c) {
    const d = c.data, S = S0(), p = player(), yk = S.actor('yukako');
    // 字陷阱：地上一块小牌子，快过期时闪
    for (const q of d.traps || []) {
      const left = 8 - (c.t - q.t);
      if (left < 2 && Math.floor(c.t * 8) % 2) continue;
      const u = w2u(q.x, q.y + 2, 0), w = q.kind === 2 ? 34 : 20;
      g.fillStyle = 'rgba(20,24,10,0.85)'; g.fillRect(Math.round(u.x - w / 2), Math.round(u.y - 9), w, 16);
      g.fillStyle = TRAP_COL[q.kind]; g.fillRect(Math.round(u.x - w / 2), Math.round(u.y + 6), w, 2);
      txt(g, TRAPS[q.kind], Math.round(u.x), Math.round(u.y - 8), TRAP_COL[q.kind], 12, 'center');
    }
    // 头皮里的发丝：由花子头上到康一头上，一根会抖的黑线
    if (d.tether && p && yk && !G.world.cine) {
      const a = w2u(yk.x, yk.y - 22, yk.z || 0), b = w2u(p.x, p.y - 18, p.z || 0);
      const n = 18, slack = (d.yrelease || 0) > 0 ? 18 : 6;
      g.fillStyle = '#1a1024';
      for (let i = 0; i <= n; i++) {
        const k = i / n, x = a.x + (b.x - a.x) * k, y = a.y + (b.y - a.y) * k + Math.sin(k * Math.PI) * slack + Math.sin(c.t * 9 + k * 7) * 1.5;
        g.fillRect(Math.round(x), Math.round(y), 3, 2);
      }
    }
  }
  function ldTick(S, c, dt) {
    const d = c.data, p = player(), yk = S.actor('yukako');
    if (!p || !yk) return;
    d.yrelease = Math.max(0, (d.yrelease || 0) - dt);
    // 白发：HP ≤ 66% 灰、≤ 40% 白
    const k = yk.hp / yk.maxHp;
    const skin = k <= 0.4 ? 'white' : k <= 0.66 ? 'grey' : null;
    if (yk.skin !== skin) {
      yk.skin = skin;
      S.sfx('sting_shock', 0.5);
      S.emote(yk, skin === 'white' ? '……！' : '……', 1);
      if (skin === 'white' && !d.white) { d.white = true; S.mark('b05b_white'); S.hint('她的头发全白了……再加把劲！', 4); }
    }
    // 发丝连着：K 闪不了；每 6 s 扯一下（拉近 30 px）
    if (d.tether) {
      p.dodgeCd = Math.max(p.dodgeCd || 0, 0.2);
      if (G.input.hit('dodge') && !d.kTold) { d.kTold = true; S.emote(p, '被头发扯着，闪不开！', 1.2, '#d8ffb0'); }
      d.pullT += dt;
      if (d.pullT >= 6 && !(d.yrelease > 0) && p.state !== 'hurt') {
        d.pullT = 0;
        const dir = yk.x > p.x ? 1 : -1, st = G.world.stage;
        G.combat.tweenTo(p, clamp(p.x + dir * 30, st.x0 + 6, st.x1 - 6), p.y, 0.18);
        S.sfx('whoosh', 0.7);
        S.sfxText('扯！', p, { dur: 0.5 });
      }
    }
    // 按住 L 再按 J：贴字陷阱
    const lp = G.input.lastPress('attack');
    if (lp !== d.lastAtk) {
      d.lastAtk = lp;
      if (p.state === 'guard') placeTrap(S, c);
    }
    // 陷阱过期 / 被踩
    d.traps = (d.traps || []).filter((q) => c.t - q.t < 8);
    if (!yk.hidden && yk.state !== 'hurt') {
      const tr = d.traps.find((q) => Math.abs(q.x - yk.x) < 12 && Math.abs(q.y - yk.y) < 8);
      if (tr) trapFire(tr, yk, false);
    }
    // 包屋：每 15 s 一处出口被头发封住（窗 → 楼梯 → 门），场地两边各缩 40 px（最多两次）
    d.sealT += dt;
    if (d.sealT >= 15 && d.seals < 3) { d.sealT = 0; seal(S, c, ++d.seals); }
    // 卡住：60 s 没打掉 10%
    if (yk.hp < d.hpMark - yk.maxHp * 0.1) { d.hpMark = yk.hp; d.markT = c.t; }
    else if (c.t - d.markT > 60 && !d.stuckTold) {
      d.stuckTold = true;
      cine(c, async () => { await S.narrate('……她踩到陷阱就躲不开。先贴字，再把她引过来！', { pos: 'top' }); });
    }
  }
  C3.loveDeluxe = async function (S) {
    S.hint(null);
    const yk = S.actor('yukako');
    return S.fight({
      id: 'b05_lovedeluxe', arena: [24, 600], lead: 'koichi', swap: false, music: 'battle', after: null, dmgScale: 0.7, losable: true,
      energy: { start: 0 },
      kitOverride: { koichi: Object.assign({}, K.koichi_act2, {
        special: { need: 0, window: (c) => !!c.data.tether && !c.data.uUsed, prompt: '按 U！烧断发丝', colours: ['#3a4a1a', '#1a2408', '#6a8a2a'], bg: 'radial', run: burnTether },
      }) },
      waves: [[{ kit: 'e_yukako', actor: yk || 'yukako', cid: 'yukako', id: 'yukako', name: '山岸由花子', x: 96, y: 156, boss: true, hp: 900, minHp: 225 }]],
      onWave: async (S2, wi, spawned, attempt, c) => { ldSetup(S2, c); },
      tick: (c, dt) => ldTick(S, c, dt),
      testHint: (c) => { const y = S.actor('yukako'); return { hp: y ? y.hp : null, tether: !!c.data.tether, traps: (c.data.traps || []).length, seals: c.data.seals || 0, skin: y ? y.skin : null }; },
      endWhen: (c) => { const y = S.actor('yukako'); return !!y && y.hp <= y.maxHp * 0.25 + 0.5; },
    });
  };

  // =====================================================================================================================
  // 第5战段 3　海岬（b05_cape）：切尾巴 → 选字（←→ 选、J 贴，2 s）→ 悬崖塌了 → U 1 s。不会输，错了只重来那一步
  // =====================================================================================================================
  const CP = { edge: [236, 160], koichi: [120, 160], yukako: [196, 158] };
  async function capeIntro(S, c) {
    const d = c.data, p = player(), yk = S.actor('yukako');
    S.face(p, 1); if (yk) S.face(yk, -1);
    C3.koichiGear(p, 2);
    await S.summon(p, { dur: 0.15, rise: 4 });
    p.stand.x = p.x + 30;
    await S.say('yukako', '康一君……你的替身，我收下了。', { expr: 'rage' });
    if (yk) { yk.play('cmd'); S.sfx('slime', 0.8); }
    S.fx('wrap', { x: p.x + 30, y: p.y, h: 26, w: 12, n: 4, kind: 'tendril', colour: '#d8d8e0' }, { life: 0.8 });
    await S.wait(0.6);
    S.sfx('slash', 0.9); S.flash(0.1, 0.5);
    S.sfxText('咔嚓', { wx: p.x + 34, wy: p.y - 20, wz: 0 }, { dur: 0.7 });
    const tip = T().prop(S, 'tail_tip', p.x + 34, p.y + 1, { id: 'cp_tip', z: 20 });
    await S.arc(tip, CP.edge[0], CP.edge[1], 26, 0.7, { spin: 8 });
    if (tip) tip.rot = 0;
    S.mark('b05c_tail');
    S.stand && p.stand.act('hurt', { dur: 0.6 });
    await S.say('koichi', '尾巴尖被切掉了……！', { expr: 'shock' });
    await S.say('koichi', '（可是那截尾巴还在崖边。……还能贴字！）');
    if (yk) yk.play('idle');
    choose(S, c);
  }
  function choose(S, c) {
    const d = c.data;
    d.phase = 'choose'; d.sel = 0; d.chooseT = c.t; d.limit = c.data.wrong ? 3 : 2;
    player().hold = true;
    S.hint('断尾上贴哪个字？←→ 选，J 贴', d.limit + 1);
  }
  async function chosen(S, c, ok) {
    const d = c.data, p = player(), yk = S.actor('yukako');
    if (!ok) {
      d.wrong = (d.wrong || 0) + 1;
      await S.narrate('……不对。', { pos: 'top' });
      choose(S, c);
      return;
    }
    S.sfx('pop', 0.9);
    S.sfxText('啪嘤', { wx: CP.edge[0], wy: CP.edge[1] - 6, wz: 0 }, { dur: 0.9 });
    S.mark('b05c_pop');
    await S.wait(0.4);
    S.sfx('rumble', 0.8); S.shake(2, 0.6);
    await S.say('koichi', '（脚下……地在裂开的声音！）', { expr: 'shock' });
    await fall(S, c);
  }
  async function fall(S, c) {
    const d = c.data, yk = S.actor('yukako'), p = player();
    if (!yk) return;
    // 崖边塌下去：只给剪影（压暗 + 往下掉出画面）
    S.sfx('crash', 0.9); S.shake(5, 0.6);
    S.fx('burst', { x: CP.edge[0] - 6, y: CP.edge[1], n: 16, speed: 40, colours: ['#7a6a5a', '#4a3a2a'], gravity: 160, life: 0.9 }, { life: 1 });
    yk.tint = { color: '#0a0610', k: 0.85 };
    yk.atk = null; yk.tele = null;
    S.pose(yk, 'hurt');
    await S.say('yukako', '啊——', { expr: 'wshock' });
    const r = await S.press({ key: 'special', window: 1.0, label: '按 U！' });
    if (r === 'miss') {
      await S.narrate('……不对，还来得及！', { pos: 'top' });
      yk.tint = null; S.unpose(yk);
      return fall(S, c);
    }
    await S.arc(yk, CP.edge[0] - 4, CP.edge[1] + 30, 10, 0.3, { anim: 'hurt' });
    S.sfx('pop', 1); S.sfx('whoosh', 0.8);
    S.sfxText('啪嘤！！', { wx: CP.edge[0], wy: CP.edge[1] - 10, wz: 0 }, { dur: 1.0 });
    yk.tint = null;
    await S.arc(yk, CP.yukako[0] - 20, CP.yukako[1], 40, 0.6, { anim: 'hurt' });
    S.pose(yk, 'down');
    S.sfx('thud', 0.8);
    S.mark('b05c_saved');
    await S.wait(0.6);
    d.done = true;
  }
  function capeTick(S, c) {
    const d = c.data, I = G.input, p = player();
    if (!d.init) { d.init = true; cine(c, () => capeIntro(S, c)); return; }
    if (d.phase !== 'choose') return;
    p.hold = true;
    if (I.hit('left')) { d.sel = (d.sel + 2) % 3; S.sfx('menu_move', 0.4); }
    if (I.hit('right')) { d.sel = (d.sel + 1) % 3; S.sfx('menu_move', 0.4); }
    if (I.hit('attack') || I.hit('ok')) { d.phase = 'act'; p.hold = false; S.hint(null); cine(c, () => chosen(S, c, d.sel === 2)); return; }
    if (c.t - d.chooseT > d.limit) { d.phase = 'act'; S.hint(null); cine(c, () => chosen(S, c, false)); }
  }
  function drawCape(g, c) {
    const d = c.data;
    if (d.phase !== 'choose' || G.world.cine) return;
    const left = Math.max(0, d.limit - (c.t - d.chooseT));
    for (let i = 0; i < 3; i++) {
      const x = 200 + i * 90, y = 120, sel = i === d.sel;
      G.ui.box(g, x, y - (sel ? 6 : 0), x + 70, y + 70 - (sel ? 6 : 0), { fill: sel ? 'rgba(60,80,20,0.96)' : 'rgba(20,24,10,0.9)' });
      txt(g, TRAPS[i], x + 35, y + 26 - (sel ? 6 : 0), TRAP_COL[i], 16, 'center');
    }
    g.fillStyle = '#d8ffb0'; g.fillRect(200, 206, Math.round(250 * left / d.limit), 4);
    txt(g, '←→ 选　J 贴', 320, 216, '#fff4d6', 12, 'center');
  }
  C3.cape = async function (S) {
    S.hint(null);
    return S.fight({
      id: 'b05_cape', arena: [8, 234], lead: 'koichi', swap: false, music: 'tension', after: null, losable: false, playerMinHp: 1,
      energy: { start: 0 }, waves: [],
      kitOverride: { koichi: Object.assign({}, K.koichi_act2) },
      tick: (c) => { if (!c.data.ov) c.data.ov = fightOverlay(c, (g) => drawCape(g, c), 3); capeTick(S, c); },
      testHint: (c) => ({ phase: c.data.phase || null, sel: c.data.sel, wrong: c.data.wrong || 0 }),
      endWhen: (c) => !!c.data.done,
    });
  };

  // =====================================================================================================================
  // 小游戏　东尼欧的晚餐（mg_tonio）：后厨，每轮一场。先洗手（水槽 E，←→ 交替 8 次 / 3 s），趁东尼欧背对着溜过去，看一眼目标（E）
  // =====================================================================================================================
  const KT = { door: 24, sink: 80, stove: 296, patrol: [200, 370], view: 150 };
  const TARGETS = [{ id: 'pot', x: 281, label: '汤锅' }, { id: 'oven', x: 375, label: '烤箱' }, { id: 'board', x: 148, label: '操作台' }, { id: 'fridge', x: 454, label: '冰箱' }];
  C3.TARGETS = TARGETS;
  C3.KT = KT;
  const LOOKS = [
    ['josuke', '汤锅里炖着番茄……就是普通的番茄。'],
    ['josuke', '烤箱里是一盘烤好的……布丁？他做菜还挺讲究。'],
    ['josuke', '操作台上的面条，有什么东西在动……是错觉吧。'],
  ];
  // 巡逻：200–370 来回走，两头停 1.6 s 转身；每走过一次灶台（296）停下来做菜 5 s——背对客人，这时候看不见（溜过去的机会）
  function tonioPatrol(S, c, dt) {
    const d = c.data, t = S.actor('tonio_k');
    if (!t) return;
    if (d.cook > 0) {
      d.cook -= dt; t.play('cmd');
      if (Math.floor(d.cook * 2) !== Math.floor((d.cook + dt) * 2)) S.fx('smoke', { x: KT.stove, y: 70, n: 3, rise: 14, colour: '#f0f0f4', life: 0.8 }, { life: 1 });
      if (d.cook <= 0) t.play('walk');
      return;
    }
    if (d.wait > 0) { d.wait -= dt; t.play('idle'); return; }   // 开场 / 被送回去以后：先在左边尝一会儿酱汁（朝右），给客人洗手的工夫
    if (d.pause > 0) { d.pause -= dt; t.play('idle'); if (d.pause <= 0) { t.facing = -t.facing; d.cooked = false; } return; }
    const to = t.facing > 0 ? KT.patrol[1] : KT.patrol[0];
    const step = 34 * dt;
    if (!d.cooked && Math.abs(t.x - KT.stove) <= step) { t.x = KT.stove; d.cooked = true; d.cook = 5; S.emote(t, '哼～', 4.6, '#ffe9a8'); return; }
    if (Math.abs(to - t.x) <= step) { t.x = to; d.pause = 1.6; t.play('idle'); return; }
    t.x += Math.sign(to - t.x) * step; t.play('walk');
  }
  function seenBy(c) {
    const d = c.data, t = S0().actor('tonio_k'), p = player();
    if (!t || !p) return false;
    const dx = p.x - t.x, view = d.view || KT.view;
    if (d.cook > 0) return false;
    return Math.sign(dx) === t.facing && Math.abs(dx) <= view;
  }
  async function sentBack(S, c, why) {
    const d = c.data, p = player(), t = S.actor('tonio_k');
    d.washed = false; d.seen = 0; d.wash = null; p.hold = false;
    d.catches = (d.catches || 0) + 1;
    if (d.catches >= 2 && !d.relaxed) { d.relaxed = true; d.view = 110; }
    if (t) { S.face(t, p); t.play(why === 'hands' ? 'rage' : 'shock'); }
    if (why === 'hands') {
      S.sfx('sting_shock', 0.8); S.shake(3, 0.3);
      await S.say('tonio', '先洗手！！厨房里不洗手是最不能原谅的！', { expr: 'rage' });
    } else {
      S.sfx('ding', 0.6);
      await S.say('tonio', '这位客人，后厨不对外开放。请回座位。', { expr: 'smile' });
    }
    await S.fadeOut(0.3);
    Object.assign(p, { x: KT.door + 10, y: 158, facing: 1 });
    if (t) { t.play('idle'); t.x = KT.patrol[0]; t.facing = 1; d.pause = 0; d.wait = 3; d.cook = 0; d.cooked = false; }
    G.world.snapCamera();
    await S.fadeIn(0.3);
    S.hint(why === 'hands' ? '先去水槽（门边）按 E 洗手！' : '脸朝的那边（黄色的带子）是他的视线。等他在灶台前做菜再过去', 6);
  }
  function drawTonio(g, c) {
    const d = c.data, S = S0(), t = S.actor('tonio_k'), p = player();
    if (!t || G.world.cine) return;
    if (d.cook > 0) { const u = w2u(t.x, t.y - 44, 0); txt(g, '做菜中（背对着）', Math.round(u.x), Math.round(u.y) - 16, '#ffe9a8', 12, 'center'); }
    else {
    // 视线扇形：脸朝的那一边 150 px，画成地面上的一条淡黄带子
    const view = d.view || KT.view, x0 = t.facing > 0 ? t.x : t.x - view, x1 = t.facing > 0 ? t.x + view : t.x;
    const a = w2u(x0, t.y + 4, 0), b = w2u(x1, t.y + 4, 0);
    g.fillStyle = d.seen > 0 ? 'rgba(255,120,90,0.28)' : 'rgba(255,240,150,0.18)';
    g.fillRect(Math.round(a.x), Math.round(a.y) - 10, Math.round(b.x - a.x), 20);
    }
    // 洗手
    if (d.wash) {
      const left = Math.max(0, 3 - (c.t - d.wash.t0));
      G.ui.box(g, 220, 110, 420, 170, { fill: 'rgba(16,28,40,0.94)' });
      txt(g, '洗手：←→ 交替按', 320, 118, '#bfe8ff', 12, 'center');
      txt(g, d.wash.n + ' / 8', 320, 136, '#ffffff', 16, 'center');
      g.fillStyle = '#bfe8ff'; g.fillRect(236, 160, Math.round(168 * left / 3), 4);
    }
    // 洗过手：手上一个小水滴图标
    txt(g, d.washed ? '手：洗干净了' : '手：还没洗', 14, 300, d.washed ? '#bfe8ff' : '#ffb8a0', 12, 'left');
    txt(g, '目标：' + TARGETS[d.round].label, 14, 316, '#ffe9a8', 12, 'left');
    if (d.seen > 0) { const u = w2u(t.x, t.y - 44, 0); txt(g, d.seen > 0.5 ? '！' : '？', Math.round(u.x), Math.round(u.y), '#ff6a4a', 16, 'center'); }
  }
  function tonioTick(S, c, dt) {
    const d = c.data, p = player(), I = G.input;
    if (!p) return;
    if (!d.init) {
      d.init = true;
      const tk = S.actor('tonio_k'); if (tk) { tk.x = KT.patrol[0]; tk.facing = 1; d.wait = 3; }
      d.ov = fightOverlay(c, (g) => drawTonio(g, c), 1);
      if (!C3.F.kitchenTold) { C3.F.kitchenTold = true; S.hint('先在水槽按 E 洗手。东尼欧在灶台前做菜（背对着）时溜过去，看一眼' + TARGETS[d.round].label + '（E）', 9); }
    }
    tonioPatrol(S, c, dt);
    // 洗手小游戏
    if (d.wash) {
      p.hold = true;
      const dir = I.hit('left') ? 'L' : I.hit('right') ? 'R' : null;
      if (dir && dir !== d.wash.last) { d.wash.last = dir; d.wash.n++; S.sfx('splash', 0.35, 1 + d.wash.n * 0.03); }
      if (d.wash.n >= 8) { d.wash = null; d.washed = true; p.hold = false; S.sfx('sparkle', 0.6); S.hint('手洗干净了！', 2); }
      else if (c.t - d.wash.t0 > 3) { d.wash = null; p.hold = false; S.hint('没洗完：再按一次 E', 3); }
      return;
    }
    // 视线
    if (d.round < 3 || !d.reached) {
      if (seenBy(c)) {
        d.seen += dt;
        if (d.seen >= 1) { d.seen = 0; cine(c, () => sentBack(S, c, 'seen')); return; }
      } else d.seen = Math.max(0, d.seen - dt * 2);
    }
    if (I.hit('ok')) {
      if (Math.abs(p.x - KT.sink) <= 22) { if (!d.washed) { d.wash = { n: 0, last: null, t0: c.t }; S.sfx('water_gush', 0.4); } else S.hint('手已经洗过了', 2); return; }
      const tg = TARGETS[d.round];
      if (Math.abs(p.x - tg.x) <= 24) {
        if (!d.washed) { cine(c, () => sentBack(S, c, 'hands')); return; }
        if (d.round === 3) { d.reached = true; d.done = true; return; }
        cine(c, async () => {
          const ln = LOOKS[d.round];
          await S.say(ln[0], ln[1]);
          S.mark('mg_round' + (d.round + 1));
          d.done = true;
        });
      }
    }
  }
  C3.tonio = async function (S, round) {
    S.hint(null);
    return S.fight({
      id: 'mg_tonio', arena: [12, 470], lead: 'josuke', swap: false, music: 'daily', after: null, losable: false, playerMinHp: 1,
      energy: { start: 0 }, waves: [],
      onRetry: null,
      tick: (c, dt) => { if (c.data.round == null) { c.data.round = round; c.data.seen = 0; c.data.view = KT.view; } tonioTick(S, c, dt); },
      testHint: (c) => ({ round: c.data.round, washed: !!c.data.washed, catches: c.data.catches || 0, wash: c.data.wash ? c.data.wash.n : null }),
      endWhen: (c) => !!c.data.done && !G.world.cine,
    });
  };
})();
