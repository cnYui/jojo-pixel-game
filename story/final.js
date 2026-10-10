// 终章保留楼梯、追车、布网和三场决战的独立检查点，时停仍使用统一的时间轴与排队结算。
'use strict';
(function () {
  const G = window.G, W = G.world, S = G.S, L = G.LATE, T = G.TPL;
  const fallen = ['avdol', 'iggy'];
  function party(active, leader, lost = fallen) { S.party([...active, ...lost], { leader }); lost.forEach(cid => S.leave(cid)); }
  async function stairs() {
    party(['jotaro', 'joseph', 'kakyoin', 'polnareff'], 'polnareff'); await S.setStage('stairs_fin');
    S.mark('final_stairs'); await S.say('dio', '波鲁纳雷夫……再上一步，就到我这边来了。');
    const q = { type: 'stairs', step: 0, resets: 0, flash: 0, acc: 0,
      touch: { buttons: ['pad'], captions: {} } };
    await L.game(S, q, (s, dt) => {
      s.flash = Math.max(0, s.flash - dt);
      if (G.input.isDown('right') || G.input.isDown('up')) s.acc += dt; else s.acc = 0;
      if (s.acc >= .18) { s.acc = 0; s.step++; S.sfx('footstep'); }
      if (s.step >= 10) { s.resets++; s.step = 0; s.flash = .1; S.sfx('timestop_hum'); if (s.resets >= 2) { s.done = true; s.win = true; } }
    }, (g, s) => {
      T.drawBg(g, 'mansion_stairs', s.t);
      T.sprite(g, 'dio', 'idle', 0, 221, 76, { alpha: .7 });
      T.sprite(g, 'polnareff', 'walk', Math.floor(s.t * 8) % 4, 40 + s.step * 12, 160 - s.step * 6);
      if (s.flash > 0) { g.fillStyle = '#9a9ca4aa'; g.fillRect(0, 0, 320, 180); }
    }, (g, s) => L.label(g, '爬上楼梯', '按 → / ↑，接近平台　' + s.step + ' / 15'));
    await S.say('polnareff', '我刚才明明在上楼梯，回过神来却在下楼……');
    await S.say('polnareff', '我的剑……不会对着我的伙伴！'); S.sfx('crash'); S.shake(4, .4);
    await S.narrate('墙壁破开，伙伴赶到。DIO 退进黑暗。众人从窗户出去，分成两路追赶。');
  }
  async function roofWeb() {
    party(['joseph', 'kakyoin'], 'kakyoin', fallen); await S.setStage('roof_fin', { x: 40, y: 159 });
    const nodes = [55, 125, 195, 265, 335, 405, 475, 550];
    for (let attempt = 0; ; attempt++) {
      S.mark('final_web');
      const q = { type: 'web', nodes: nodes.map(x => ({ x, set: false })), warn: 0, next: 5, cuts: 0, hazards: 0,
        touch: { buttons: ['pad', 'j', 'k'], captions: { j: '布网', k: '闪避' } } };
      await L.game(S, q, (s, dt) => {
        L.move(W.player, dt, 95);
        if (L.hit('attack')) { const n = s.nodes.find(n => !n.set && Math.abs(n.x - W.player.x) < 28); if (n) { n.set = true; S.sfx('hiero_tentacle'); } }
        if (s.t >= s.next && !s.warn) {
          s.kind = s.hazards++ % 2 ? 'cut' : 'knife'; s.warn = (s.kind === 'knife' ? 24 : 40) / 60;
          s.targetX = W.player.x; s.next += 5;
        }
        if (s.warn > 0) { s.warn -= dt; if (L.hit('dodge')) { W.player.x = G.clamp(W.player.x + (G.input.isDown('left') ? -1 : 1) * 42, 15, 615); s.evaded = true; }
          if (s.warn <= 0) {
            if (Math.abs(W.player.x - s.targetX) < 24 && !s.evaded) {
              if (s.kind === 'knife') { L.damage({ player: W.player }, 12); S.sfx('knife_volley'); }
              else { const n = s.nodes.find(n => n.set); if (n) { n.set = false; s.cuts++; } S.sfx('hiero_tentacle'); }
              G.dbg.ev('web_hazard_hit', { kind: s.kind });
            } else G.dbg.ev('web_hazard_evade', { kind: s.kind });
            // 归零：倒计时减完常停在一个很小的负数上，`!s.warn` 为假，之后就再也不出下一次飞刀 / 切丝了。
            s.evaded = false; s.warn = 0;
          }
        }
        if (s.nodes.every(n => n.set)) { s.done = true; s.win = true; }
        if (s.t >= 30 && !s.done) { s.done = true; s.win = false; }
      }, (g, s) => {
        T.drawBg(g, 'cairo_rooftops', s.t, G.cam.x);
        for (const n of s.nodes) {
          const x = n.x - G.cam.x; g.fillStyle = n.set ? '#50ff99' : '#bfd6c566'; g.fillRect(x - 3, 148, 6, 12);
          if (n.set) { g.strokeStyle = '#4ebc77'; g.beginPath(); g.moveTo(x, 149); g.lineTo(305 - G.cam.x, 90); g.stroke(); }
        }
        T.sprite(g, 'kakyoin', 'walk', Math.floor(s.t * 7) % 4, W.player.x - G.cam.x, W.player.y);
        T.sprite(g, 'dio', s.warn > 0 ? 'punch' : 'idle', 0, (s.targetX || 365) - G.cam.x, 87, { alpha: .8 });
        if (s.warn > 0) { g.fillStyle = '#ffde73'; g.fillRect(s.targetX - G.cam.x - 18, 161, 36, 2); }
      }, (g, s) => {
        L.label(g, '半径二十米 · 触须网', '靠近八个节点按 J；金色预警出现时 K 闪离路线');
        L.text(g, '布网 ' + s.nodes.filter(n => n.set).length + ' / 8' + ' · HP ' + Math.ceil(W.player.hp), 22, 314, '#86ffb9');
        L.text(g, '剩余 ' + Math.ceil(Math.max(0, 30 - s.t)) + ' 秒', 610, 314, '#ffe174', 'right');
      });
      if (q.win) break;
      await S.say('kakyoin', '还差一点……重新布下这张网。'); W.player.x = 40;
    }
    await S.say('kakyoin', '半径20米——绿宝石水花！');
    const dio = S.spawn('dio', 365, 158, { id: 'roof_dio' });
    G.time.stop(dio, { tint: 'yellow', burst: .4, dur: 1.2, lines: { start: 'dio_ts', end: 'dio_resume' } });
    await S.wait(2.81, 'ui'); S.sfx('punch_heavy'); S.impact('invert', 2 / 60); S.shake(5, .3);
    await S.narrate('所有的丝同时断开。时间恢复时，花京院撞进了水塔，水从裂缝涌出。');
    for (let attempt = 0; ; attempt++) {
      S.mark('final_clock');
      const q = { type: 'clock', x: 140, y: 96, tx: 232, ty: 68, wobbleX: 0, wobbleY: 0,
        touch: { buttons: ['pad', 'j'], captions: { j: '最后一发' } } };
      await L.game(S, q, (s, dt) => {
        const dx = (G.input.isDown('right') ? 1 : 0) - (G.input.isDown('left') ? 1 : 0), dy = (G.input.isDown('down') ? 1 : 0) - (G.input.isDown('up') ? 1 : 0);
        s.x = G.clamp(s.x + dx * 60 * dt, 10, 310); s.y = G.clamp(s.y + dy * 60 * dt, 10, 170);
        s.wobbleX = Math.sin(s.t * 21) * 2; s.wobbleY = Math.cos(s.t * 17) * 2;
        if (L.hit('attack')) { s.done = true; s.win = Math.hypot(s.x + s.wobbleX - s.tx, s.y + s.wobbleY - s.ty) <= 7; S.sfx('emerald_shot'); }
      }, (g, s) => {
        T.drawBg(g, 'cairo_rooftops', s.t); g.fillStyle = '#242137'; g.fillRect(217, 35, 30, 95);
        g.fillStyle = '#e8d8ab'; g.beginPath(); g.arc(s.tx, s.ty, 7, 0, Math.PI * 2); g.fill();
        g.strokeStyle = '#67ffb1'; g.strokeRect(s.x + s.wobbleX - 4, s.y + s.wobbleY - 4, 8, 8);
        T.sprite(g, 'kakyoin', 'down', 0, 90, 174, { scale: 2 });
      }, g => L.label(g, '最后一发 · 留下讯息', '方向键瞄准钟面，J 发射；失败只重试这一发'));
      if (q.win) { S.sfx('glass_break'); break; }
      await S.narrate('准星晃开了。只重试最后一发。');
    }
    S.music('sad'); await S.say('kakyoin', '乔斯达先生……他的替身的秘密……是「时间」……');
    await L.view(S, { bg: 'cairo_rooftops', parts: [{ cid: 'kakyoin', anim: 'down', x: 150, y: 175, scale: 2 }] }, 1.5); S.leave('kakyoin');
  }
  async function message() {
    S.setLeader('joseph', { force: true }); S.mark('final_message');
    await S.say('joseph', '时间……是时间！承太郎，DIO 的能力是让时间停止！');
    const q = { type: 'message', value: 0, bonus: false, touch: { buttons: ['j'], captions: { j: '传讯' } } };
    await L.game(S, q, (s, dt) => {
      s.value = Math.min(1, s.value + dt / 3 + (L.hit('attack') ? .07 : 0));
      if (s.value >= 1 && s.t < 2.8) s.bonus = true;
      if (s.t >= 3) { s.done = true; s.win = true; }
    }, (g, s) => {
      T.drawBg(g, 'cairo_rooftops', s.t);
      T.sprite(g, 'joseph', 'point', 0, 68, 174, { scale: 2 }); T.sprite(g, 'dio', 'idle', 0, 243, 172, { scale: 2 });
      g.strokeStyle = '#ab64c2'; for (let n = 0; n < 4; n++) { g.beginPath(); g.moveTo(85, 116 + n * 3); g.lineTo(240, 100 + n * 4); g.stroke(); }
    }, (g, s) => { L.label(g, '把讯息传给承太郎', '连按 J 加快藤蔓中的讯息'); g.fillStyle = '#3a294e'; g.fillRect(100, 302, 440, 8); g.fillStyle = '#d9b0f5'; g.fillRect(100, 302, 440 * s.value, 8); });
    if (q.bonus) await S.say('joseph', '……还有！他停时间的时候，自己也只能动几秒！');
    const dio = S.actor('roof_dio') || S.spawn('dio', 300, 160, { id: 'roof_dio' });
    G.time.stop(dio, { tint: 'yellow', dur: 1.2, lines: { start: 'dio_ts', end: 'dio_resume' } }); await S.wait(2.81, 'ui');
    await L.view(S, { bg: '#641e37', parts: [{ cid: 'joseph', anim: 'down', x: 155, y: 145, scale: 2, alpha: .25 }] }, 1.1);
    await S.say('joseph', '承太郎……别靠近他……'); S.leave('joseph');
  }
  function stopDio(c, phase) {
    const d = c.data, e = c.boss, p = c.player;
    d.stops++; d.stop = { x: p.x, y: p.y, attacked: false, knives: [], knifeBuilt: false, launched: false };
    d.growing = phase === 1 && d.stops >= 2 && !G.flags.dioGrowth;
    d.growthStarted = false;
    e.mem.locked = true; e.atk = e.tele = null;
    G.time.stop(e, { tint: 'yellow', prewarn: true, burst: .4, dur: phase === 3 ? 2.4 : 1.2, resume: .36,
      sfx: 'timestop', music: 'tape', lines: { start: 'dio_ts', end: 'dio_resume' },
      grant: G.flags.dioGrowth ? { actor: p, sec: .5 } : null,
      holdWhile: () => d.growing });
    G.dbg.ev('dio_stop_start', { phase, n: d.stops });
  }
  // 首次觉醒 QTE：时停时间轴由 holdWhile（d.growing）停住。收尾不往 W.ticks 里再塞回调——world.update 把 ticks
  // 过滤成新数组，回调执行中 push 进旧数组的会丢，QTE 成功后 growing 一直为真、时停永远不放。改由这场 fight 自己的
  // tick（stopTick → growthTick）每帧检查，成功那一帧直接放行并收掉结果牌；失败照常显示 0.7 秒结果牌后由 Promise 收尾。
  let growQ = null;
  function dropGrowth() { const q = growQ; growQ = null; if (q && G.ui.qte === q) G.ui.finishQte(q, true); }
  function grantGrowth(c) {
    const d = c.data, p = c.player, e = c.boss;
    if (!d.growing) return;
    d.growing = false; G.flags.dioGrowth = true;
    if (G.time.active && G.time.by === e) {
      G.time.o.grant = { actor: p, sec: G.time.phase === 'stopped' ? G.time.t + .5 : .5 };
      if (G.time.phase === 'stopped') G.time.immune.add(p);
    }
    S.hint('承太郎在停止的时间里能动半秒！', 3); G.dbg.ev('dio_growth');
  }
  function startGrowth(c) {
    const d = c.data, run = G.runId;
    d.growthStarted = true;
    const promise = S.mash({ need: 8, time: 2, decay: 0, label: '……手指动了！动起来！（连按 J）' });
    const q = growQ = G.ui.qte;
    // QTE 不占 W.cine：fight 的 tick 要继续跑 growthTick；时停中敌人和飞行道具本来就冻住。
    if (q && q.cineSet) { q.cineSet = false; if (W.cine && W.cine.by === 'qte') W.cine = null; }
    promise.then(win => {
      if (run !== G.runId || W.fight !== c || growQ !== q) return;
      growQ = null;
      if (win) grantGrowth(c); else d.growing = false;
    }).catch(G.cancelIgnore);
  }
  function growthTick(c) {
    const q = growQ;
    if (!q || G.ui.qte !== q || q.result !== true) return;
    growQ = null; grantGrowth(c); G.ui.finishQte(q);
  }
  function stopTick(c, dt, phase) {
    const d = c.data, e = c.boss, p = c.player, ts = G.time, st = d.stop;
    if (!st) return;
    if (ts.active && ts.by === e && ts.phase === 'stopped') {
      if (d.growing) { if (!d.growthStarted) startGrowth(c); else growthTick(c); return; }
      if (phase !== 2) {
        e.x += G.clamp(st.x - 22 - e.x, -160 * dt, 160 * dt); e.y += G.clamp(st.y - e.y, -70 * dt, 70 * dt);
        if (!st.attacked && Math.abs(e.x - st.x) <= 38 && Math.abs(e.y - st.y) < 8 && Math.abs(p.y - st.y) < 9 && Math.abs(p.x - st.x) < 38) {
          // 第三段的 +30% 由这一场的 dmgScale 1.3 统一乘（排队伤害结算时同样乘）；以前这里再写 39，等于 ×1.69，一拳 51
          st.attacked = true; e.stand.act('punch', { dur: .4 }); ts.queueHit(p, e, { dmg: 30, push: 24, slot: 'enemy', guard: 'normal', sfxHit: 'punch_heavy' });
        }
      } else {
        if (!st.knifeBuilt) {
          st.knifeBuilt = true;
          for (let n = 0; n < 16; n++) { const a = n * Math.PI / 8; st.knives.push({ x: st.x + Math.cos(a) * 62, y: st.y + Math.sin(a) * 13, a, dead: false }); }
          S.sfx('knife_freeze');
        }
        if (!ts.isFrozen(p) && L.hit('attack')) {
          for (const k of st.knives) if (Math.sign(k.x - p.x) === p.facing) k.dead = true;
          S.sfx('parry'); p.stand.act('rush', { dur: .2 }); G.dbg.ev('dio_knives_deflected', { count: st.knives.filter(k => k.dead).length });
        }
      }
    }
    if (phase === 2 && ts.phase === 'resume' && !st.launched) {
      st.launched = true; S.sfx('knife_volley');
      for (const k of st.knives.filter(k => !k.dead)) {
        const angle = Math.atan2(st.y - k.y, st.x - k.x);
        c.shoot(e, { kind: 'knife', ang: angle, speed: 185, dmg: 12, life: 1, hitR: [2, 4, 20], colour: '#e2e3ec', tag: 'dio_ring' }, { x: k.x, y: k.y, z: 20 });
      }
    }
    if (!ts.active) { e.mem.locked = false; d.stop = null; d.nextStop = c.t + (phase === 3 ? 7 : 8); }
  }
  // 装死的条件：玩家 HP 低于 35%，或 DIO 已经被打到 1 HP（他不会倒下，不装死这一段收不了尾）；时停中不行。
  function canPlayDead(c) {
    const d = c.data, p = c.player, e = c.boss;
    return !!(p && e && !d.playDead && !G.time.active && (p.hp / p.maxHp < .35 || e.hp <= 1));
  }
  async function playDead(c) {
    const d = c.data, p = c.player, e = c.boss; d.playDead = true; G.time.clear(); d.stop = null; e.mem.locked = true;
    p.play('down'); S.sfx('flatline');
    // G.ui.insertUI 存的是 { draw, t0 } 对象，S.insertUI 只收绘制函数：按对象身份原样放回，取消 / 重来时也要放回。
    const oldUI = G.ui.insertUI;
    S.insertUI(g => { L.hud(g, ['心跳停止……', '等待破绽']); g.strokeStyle = '#72e7a0'; g.beginPath(); g.moveTo(120, 308); g.lineTo(520, 308); g.stroke(); });
    const mine = G.ui.insertUI;
    let sign = null, v = null;
    try {
      await S.wait(.9, 'ui'); sign = T.prop(S, 'road_sign', e.x + 14, e.y - 30);
      await S.say('dio', '心跳真的停了……那就彻底结束吧。');
      v = T.show(S, { bg: 'cairo_street_night', parts: [{ cid: 'chariot', anim: 'punch', x: 140, y: 167, scale: 2 }, { cid: 'dio', anim: 'hurt', x: 193, y: 162, scale: 2 }], draw(g) { g.fillStyle = '#fff9ba'; g.fillRect(168, 72, 3, 20); } });
      S.sfx('glint'); await S.wait(.45, 'ui'); v.close(); v = null;
      await S.say('polnareff', '赶上了！'); S.sfx('punch_heavy');
      await L.view(S, { bg: 'cairo_street_night', parts: [{ cid: 'polnareff', anim: 'down', x: 270, y: 174, scale: 2 }] }, .7);
    } finally {
      if (v) v.close();
      if (sign) sign.remove = true;
      if (G.ui.insertUI === mine) G.ui.insertUI = oldUI;
    }
    p.play('idle'); p.state = 'idle'; p.dmgOut = 2; d.counterUntil = c.t + 1.5;
    e.mem.locked = false; e.stunT = 1.5; d.nextStop = c.t + 5; S.hint('白金之星反击！一秒半内伤害翻倍。', 3); G.dbg.ev('dio_play_dead');
  }
  async function roadroller(c) {
    const d = c.data, e = c.boss; d.roller = true; G.time.clear(); d.stop = null;
    await S.title('roadroller'); S.sfx('roadroller');
    const v = T.show(S, { bg: 'cairo_street_night', draw(g, t) {
      g.fillStyle = '#09060dbb'; g.fillRect(70, 145, 180, 10);
      T.sprite(g, 'prop:roadroller', 'idle', Math.min(2, Math.floor(t * 2)), 160, 72 + Math.min(60, t * 55), { scale: 2 });
      T.sprite(g, 'jotaro', 'cmd', 0, 160, 175, { scale: 2 });
    } }); await S.wait(1, 'ui');
    G.time.stop(e, { tint: 'yellow', prewarn: false, dur: 5, burst: .4, lines: { start: 'dio_ts', end: 'dio_resume' } });
    const win = await S.clash({ label: '顶回去——！（连按 J）', time: 4, id: 'roadroller' }); v.close();
    if (!win) L.damage(c, 35);
    await S.eyeStrip('jotaro', { dur: .4 });
    S.standCard('starplat_world', { y: 6 });
    G.time.stop(c.player, { tint: 'blue', prewarn: false, dur: 2, burst: .4, lines: { start: 'jotaro_ts', end: 'jotaro_resume' } });
    c.player.x = e.x + 30; c.player.facing = -1; c.player.play('kick'); e.play('hurt'); S.sfx('punch_heavy'); S.shake(5, .3);
    e.hp = Math.max(e.maxHp * .18, e.hp - 350); await S.wait(2.8, 'ui'); G.flags.starWorld = true;
    d.nextStop = c.t + 7; G.dbg.ev('dio_roadroller');
  }
  async function finalClash(c) {
    const d = c.data; d.final = true; G.time.clear(); d.stop = null;
    for (let attempt = 0; ; attempt++) {
      S.mark('final_last_clash'); const win = await L.clash(S, { label: '欧拉——！！（连按 J）', time: 5, rate: attempt ? .14 : .2, id: 'dio_final' });
      if (win) { c.end(); return; }
      const min = c.player.minHp; c.player.minHp = 1;
      G.combat.hit(c.boss, c.player, { dmg: 60, push: 0, slot: 'enemy', guard: 'none', sfxHit: 'thud' }, { queued: true }); c.player.minHp = min;
      await S.say('jotaro', '还没结束。最后这一拳，再来！');
    }
  }
  async function dioFight(phase) {
    party(['jotaro', 'polnareff'], 'jotaro', ['avdol', 'iggy', 'kakyoin', 'joseph']);
    await S.setStage('street_fin', { x: 250, y: 160 }); S.mark('final_dio_' + phase);
    const hp = [0, 1500, 1800, 2200][phase];
    await S.fight({ id: 'b28d' + phase + '_dio', lead: 'jotaro', swap: false, bench: 'hide', arena: [150, 650], finish: 'none', music: 'boss',
      vs: phase === 1 ? 'theworld' : null,
      dmgScale: phase === 3 ? 1.3 : 1,
      waves: [[{ cid: 'dio', kit: 'e_dio', boss: true, hp, minHp: 1, x: 470, y: 160 }]],
      kitOverride: phase === 2 ? { jotaro: { chords: { 'guard+dodge': { hold: 3, run(s, p, c) {
        if (canPlayDead(c)) L.task(c, () => playDead(c));
        else { const held = p._chordHold['guard+dodge']; held.t = 0; held.done = false; }
      } } } } } : phase === 3 ? { jotaro: { special: { name: '白金之星·世界', need: 100, title: 'jotaro_ts',
        // 能量满才是“窗口开着”：HUD 的「按 U！」和触屏金圈只在真能放的时候出现（窗口外按 U 也只在能量满时生效）。
        window: c => c.player.energy >= (c.player.energyMax || 100), prompt: '能量满了！按 U：白金之星·世界', run(s, p) {
        G.time.stop(p, { tint: 'blue', sfx: 'timestop_sp', burst: .4, dur: 2, resume: .36, lines: { start: 'jotaro_ts', end: 'jotaro_resume' } });
      } } } } : {},
      onWave(s, n, es, attempt, c) {
        dropGrowth();
        c.data.stops = 0; c.data.nextStop = 7; c.data.stop = null; c.data.magazines = phase === 2 ? 3 : 0; c.data.hold = 0; c.data.clashNext = 0;
        c.data.playDead = false; c.data.roller = false; c.data.final = false; c.data.growing = false; c.data.growthStarted = false;
        W.stage.props = W.stage.props.filter(p => !String(p.id || '').startsWith('late_'));
        // 杂志只挡时停后的刀阵（规划：前 3 把刀不扣血）；以前所有飞刀都算，DIO 平时的三连飞刀（TW_KNIFE）开场就把三本杂志用光
        if (phase === 2) c.player.onHitBy = (t, a, m, info) => {
          if (m.tag === 'dio_ring' && c.data.magazines > 0) { c.data.magazines--; if (info.shot) info.shot.dead = true; s.sfx('guard'); G.dbg.ev('magazine_block', { left: c.data.magazines }); return 'evade'; }
          return null;
        };
        L.pixel(P => {
          const stop = c.data.stop;
          if (stop && G.time.phase === 'warn') G.px.line(P, c.boss.x - G.cam.x, c.boss.y, stop.x - G.cam.x, stop.y, '#ffe174', .75, 2);
          if (stop && G.time.active && !stop.launched) for (const k of stop.knives) if (!k.dead) G.px.line(P, k.x - G.cam.x - 3, k.y - 20, k.x - G.cam.x + 3, k.y - 20, '#f2eefc');
        });
        s.insertUI(g => L.hud(g, phase === 1 ? ['DIO · 第1段', '黄光预警：提前按住 L 防御，或 K 闪离路线', '时停中精准格挡无效',
            G.flags.dioGrowth ? '停止的时间里，可以动半秒！' : null]
          : phase === 2 ? ['DIO · 第2段', '时停里能动的半秒：J 弹开一侧飞刀', '刀阵飞来时面朝 DIO 按住 L', 'HP 低于 35%：按住 L + K 三秒装死', '杂志挡刀 ' + c.data.magazines + ' / 3',
            canPlayDead(c) ? '停止心跳 ' + c.data.hold.toFixed(1) + ' / 3 秒' : null]
          : ['DIO · 第3段', '能量满按 U：白金之星·世界', '压路机和最后一拳：连按 J']));
      },
      tick(c, dt) {
        const d = c.data, e = c.boss, p = c.player;
        stopTick(c, dt, phase);
        if (d.counterUntil && c.t >= d.counterUntil) { p.dmgOut = 1; d.counterUntil = 0; }
        if (phase === 2 && !d.playDead) {
          const held = p._chordHold && p._chordHold['guard+dodge'];
          if (held && !canPlayDead(c)) { held.t = 0; held.done = false; }
          d.hold = held ? Math.min(3, held.t) : 0;
          // 正在“停止心跳”：承太郎倒在地上，DIO 不出新招、不发动时停，只慢慢走近确认（原著他是走过去看的）。
          //   以前他照打不误：HP 低于 35% 时还要在挨打中按住 3 秒，几乎必死（终章旧路线在这一段连输 22 次）；松手就恢复。
          if (d.hold > 0) {
            if (!d.holdLock) { d.holdLock = true; e.mem.locked = true; e.tele = null; p.play('down'); G.dbg.ev('dio_play_dead_hold'); }
            if (!e.atk && !e.mem.dash) { const side = p.x >= e.x ? -1 : 1; G.combat.walkTo(e, p.x + side * 34, p.y, dt, 24); }
          } else if (d.holdLock) { d.holdLock = false; if (!G.time.active) e.mem.locked = false; if (p.anim === 'down') p.play('idle'); }
          // DIO 只会被打到 1 HP；玩家一直没掉到 35% 以下时也要能进装死（波鲁纳雷夫的一剑是这一段的收尾），提示一次。
          if (e.hp <= 1 && !d.deadHint) { d.deadHint = true; S.hint('DIO 不会就这样倒下……停止心跳引他靠近：按住 L + K 三秒', 6); }
        }
        if (phase === 3 && !d.roller && (e.hp / e.maxHp <= .75 || c.t >= 12)) { L.task(c, () => roadroller(c)); return; }
        if (phase === 3 && d.roller && !d.final && e.hp / e.maxHp <= .15) { L.task(c, () => finalClash(c)); return; }
        if (!G.time.active && c.t >= d.nextStop && !d.busy && !d.holdLock) stopDio(c, phase);
        if (phase === 1 && !G.time.active && c.t >= d.clashNext && e.atkId === 'TW_RUSH' && e.atk && p.rush && Math.abs(e.x - p.x) < 65) {
          d.clashNext = c.t + 6;
          L.task(c, async () => { e.atk = null; const win = await L.clash(S, { label: '欧拉欧拉欧拉！（连按 J）', time: 4 }); if (win) e.stunT = 1; else L.damage(c, 60); });
        }
        // 第一段必须经历第二次时停的“手指动了”：DIO 先被打到 1 HP 时把下一次时停提前，觉醒之后才结束这一段。
        if (e.hp <= 1 && phase === 1) { if (G.flags.dioGrowth) c.end(); else if (!G.time.active && d.nextStop > c.t + 1) d.nextStop = c.t + 1; }
        if (e.hp <= 1 && phase === 2 && d.playDead && !d.busy) c.end();
      }, after(s, es, attempt, c) { dropGrowth(); s.insertUI(null); c.player.onHitBy = null; c.player.dmgOut = 1; }
    });
  }
  L.final = { stairs, roofWeb, message, dioFight };
  G.STORY.final = async function () {
    await S.chapterCard('final');
    await stairs(); await S.setStage('chase_fin');
    await L.lines(S, [['joseph', '这些够不够？不够记在 SPW 财团的账上！'], ['jotaro', '两路一起追也好。'], ['dio', '威尔逊·菲利普斯。开车，追上那辆卡车。']]);
    T.prop(S, 'truck', 170, 168); T.prop(S, 'senator_car', 270, 168);
    S.mark('final_chase'); await L.runner(S, { hp: 100 });
    S.sfx('glass_break'); await L.view(S, { bg: 'black', draw(g) { g.fillStyle = '#aaa8b1'; g.fillRect(115, 78, 90, 65); g.fillStyle = '#19121f'; g.fillRect(136, 84, 44, 43); } }, .6);
    await S.narrate('一个黑影砸碎了卡车后窗。上议员没能逃出来。卡车撞进了路边的楼。');
    G.flags.crash = 6; await S.crash(5, 6); await S.say('joseph', '……这一次，可以不算吗？');
    await roofWeb(); await message();
    await L.lines(S, [['dio', '哦？你竟然主动靠近我？'], ['jotaro', '不靠近的话，怎么揍你。']]);
    await dioFight(1); await dioFight(2);
    await L.view(S, { bg: '#641e37', parts: [{ cid: 'dio', anim: 'laugh', x: 190, y: 171, scale: 3, alpha: .3 }] }, 1.2); S.sfx('drain');
    await S.say('dio', '最高哒！'); await S.title('wryyy'); S.sfx('roar'); await dioFight(3);
    S.mark('final_finish');
    await L.view(S, { bg: 'radial', parts: [{ cid: 'theworld', anim: 'hurt', x: 190, y: 172, scale: 3 }, { cid: 'starplat', anim: 'punch', x: 90, y: 172, scale: 3 }], draw(g, t) {
      g.strokeStyle = '#ffffdb'; g.lineWidth = 2; g.beginPath(); g.moveTo(180, 43); g.lineTo(187, 77); g.lineTo(175, 112); g.lineTo(200, 154); g.stroke();
      for (let n = 0; n < 32; n++) { g.fillStyle = '#ffe89b'; g.fillRect(185 + Math.cos(n * 2.4) * t * 32, 98 + Math.sin(n * 2.4) * t * 32, 2, 2); }
    } }, 1.4); S.sfx('glass_break');
    await L.view(S, { bg: 'black', parts: [{ cid: 'dio', anim: 'hurt', x: 160, y: 172, scale: 3 }], draw(g) { g.fillStyle = '#fffac7'; g.fillRect(156, 60, 3, 96); } }, .9);
    await S.say('dio', '怎么可能……我是……DIO……');
    await L.view(S, { bg: 'cairo_street_night', parts: [{ cid: 'scene:s18_final2_jotaro_back', x: 160, y: 180, scale: 2 }] }, .8);
    await S.say('jotaro', '你的失败只有一个原因……就是你惹我生气了。'); await L.view(S, { bg: 'black' }, .6);
    await S.setStage('dawn_fin'); S.music('sad'); S.mark('final_dawn');
    await L.view(S, { bg: 'cairo_street_dawn', draw(g, t) {
      g.fillStyle = '#d1c3a1'; g.fillRect(137, 140, 42, 10);
      for (let n = 0; n < 48; n++) { g.fillStyle = '#e2d3a9'; g.fillRect(158 + Math.sin(n * 2.4) * t * 18, 142 - t * (12 + n % 20), 1, 1); }
    } }, 2); await S.narrate('SPW 的人赶到。DIO 的遗体在黎明的阳光中化灰。');
    await L.view(S, { bg: 'cairo_street_dawn', parts: [{ cid: 'joseph', anim: 'down', x: 175, y: 165, scale: 2 }, { cid: 'starplat', anim: 'punch', x: 130, y: 167, scale: 2 }] }, 1.2);
    await S.narrate('白金之星按压心脏。SPW 将 DIO 的血输回乔瑟夫体内。心跳，再次响起。'); S.sfx('heartbeat');
    await S.join('joseph'); await S.say('joseph', '你以为是乔瑟夫吗？是我 DIO 哒！'); await S.say('jotaro', '……再开这种玩笑，我真的会揍你。');
    await S.setStage('bedroom_fin'); S.mark('final_holly');
    S.location('kujo_day50'); await S.wait(1.6);
    await L.view(S, { bg: 'kujo_bedroom_morning', parts: [{ cid: 'holly', anim: 'idle', x: 160, y: 163, scale: 2 }], draw(g, t) {
      for (let n = 0; n < 24; n++) { g.fillStyle = '#ffe68c'; g.fillRect(160 + Math.cos(n * 2.4) * t * 25, 122 - t * 15 + Math.sin(n * 2.4) * t * 12, 1, 1); }
    } }, 1.5); await S.say('holly', '承太郎……');
    party(['jotaro', 'joseph', 'polnareff'], 'jotaro', ['avdol', 'iggy', 'kakyoin']); S.mark('final_airport');
    await L.explore(S, 'airport_fin', { exitX: 285, location: 'cairo_airport',
      onLook: async (s, p) => s.say(p.cid, p.cid === 'jotaro' ? '……已经感觉不到 DIO 的气息了。' : p.cid === 'joseph' ? '隐者之紫什么都没拍到。……这样就好。' : '银色战车也该休息了。'), talk: {
      joseph: 'Holly 已经醒了！我们回家！', polnareff: '我回法国了。……替我跟阿布德尔和伊奇说声谢谢。', jotaro: '……再见。保重。'
    }, hotspots: [
      L.hot('board', 130, '航班显示板', ['detail'], async s => s.narrate('东京、巴黎。两个方向，同一次告别。'), async s => s.say('jotaro', '飞往东京的航班，开始登机了。')),
      L.hot('window', 220, '停机坪', ['detail'], async s => s.narrate('跑道另一端，飞机缓缓转向。'), async s => s.say('jotaro', '太阳升起来了。'))
    ], hint: '最后一次自由走动：Q 换队长，E 与伙伴告别，U 调查；向右去登机口。' });
    S.mark('final_ending'); await S.video('ending');
    await S.notice({ text: '星尘斗士的旅途，到此结束。\n原作：荒木飞吕彦《JOJO的奇妙冒险》\n同人游戏，仅供交流。角色、故事与音乐版权归原权利人。\n制作：悠一 × AI 协作。', minT: 3, auto: false });
    G.flags.completed = true;
  };
})();
