// 馆内三组机关分别拥有检查点；必然牺牲只用过场，玩家的输入负责破解真实战斗。
'use strict';
(function () {
  const G = window.G, W = G.world, S = G.S, L = G.LATE, T = G.TPL;
  const all = ['jotaro', 'joseph', 'kakyoin', 'avdol', 'polnareff', 'iggy'];
  function party(ids, leader, lost = []) { S.party([...ids, ...lost], { leader }); lost.forEach(id => S.leave(id)); }
  async function lightSoul(cid, seconds = 1.6) {
    S.sfx('glass_break');
    const v = T.show(S, { bg: '#161126', draw(g, t) {
      const k = Math.min(1, t / seconds);
      T.sprite(g, cid, 'idle', 0, 160, 164 - k * 80, { scale: 2, alpha: 1 - k, tint: { color: '#ffffff', k: .85 } });
      for (let n = 0; n < 64; n++) { const a = n * 2.399, r = 8 + k * (20 + n % 15);
        g.fillStyle = n % 2 ? '#ffffff' : '#fff0b6'; g.fillRect(160 + Math.cos(a) * r, 144 - k * 65 + Math.sin(a) * r, 1, 2); }
    } }); try { await S.wait(seconds); } finally { v.close(); }
  }
  async function baseball() {
    for (let attempt = 0; ; attempt++) {
      S.mark('ch11_baseball');
      const q = { type: 'baseball', inning: 1, ball: 0, pitch: 0, side: 0, delegated: false,
        own: 0, enemy: 0, phase: 'select', reveal: 0, guess: false,
        touch: { buttons: ['pad', 'j', 'e', 'swap'], captions: { j: '投球', e: '确认', swap: '藤蔓' } } };
      await L.game(S, q, (s, dt) => {
        if (s.phase === 'result') { s.reveal -= dt; if (s.reveal > 0) return;
          s.ball++; if (s.ball % 4 === 0) s.inning++;
          if (s.ball >= 12) { s.done = true; s.win = s.own > s.enemy; return; }
          s.phase = 'select';
        }
        if (s.inning >= 3 && L.hit('swap')) { s.delegated = true; S.sfx('vine'); }
        if (!s.delegated) {
          if (L.hit('left')) s.pitch = (s.pitch + 2) % 3;
          if (L.hit('right')) s.pitch = (s.pitch + 1) % 3;
          if (L.hit('up') || L.hit('down')) s.side = 1 - s.side;
        }
        const fire = L.hit('attack') || L.hit('ok');
        if (!fire) return;
        if (s.delegated) { s.pitch = Math.floor(G.rand(0, 3)); s.side = Math.floor(G.rand(0, 2)); }
        s.guess = G.rand(0, 1) < (s.delegated ? .3 : .9);
        if (s.guess) { s.enemy++; S.sfx('baseball_hit'); } else { s.own += 3; S.sfx('tv_game'); }
        s.phase = 'result'; s.reveal = .8;
        G.dbg.ev('baseball_pitch', { inning: s.inning, pitch: s.pitch, side: s.side, delegated: s.delegated, read: s.guess });
      }, (g, s) => {
        g.fillStyle = '#12182c'; g.fillRect(0, 0, 320, 180); g.fillStyle = '#438153'; g.fillRect(12, 22, 296, 146);
        g.fillStyle = '#c6ad7b'; g.beginPath(); g.moveTo(160, 49); g.lineTo(240, 108); g.lineTo(160, 163); g.lineTo(80, 108); g.fill();
        g.fillStyle = '#fff0cb'; for (const [x, y] of [[160, 54], [226, 108], [160, 153], [94, 108]]) g.fillRect(x - 3, y - 2, 6, 4);
        T.sprite(g, 'jotaro', 'cmd', 0, 160, 124);
        T.sprite(g, 'telence', s.phase === 'result' ? 'punch' : 'idle', 0, 203, 166);
        if (s.delegated) { g.fillStyle = '#ae78c5'; for (let n = 0; n < 4; n++) g.fillRect(20 + n * 2, 138 + n * 4, 60, 2); }
        if (s.phase === 'result') { g.fillStyle = '#ffffee'; g.fillRect(160 + (s.guess ? 30 : -30), 130, 3, 3); }
        for (let y = 0; y < 180; y += 3) { g.fillStyle = '#080b162a'; g.fillRect(0, y, 320, 1); }
      }, (g, s) => {
        L.label(g, '阿图姆神 · 棒球　第' + Math.min(3, s.inning) + '局', '左右选球种，上下选内外角，J / E 投球');
        L.text(g, ['直球', '曲球', '变速'][s.pitch] + ' · ' + ['内角', '外角'][s.side], 22, 312, '#ffe174');
        L.text(g, '承太郎 ' + s.own + ' : ' + s.enemy + ' 泰伦斯', 610, 312, '#ffffff', 'right');
        if (s.phase === 'result') L.text(g, s.guess ? 'YES！我读到了你的灵魂。' : 'NO？！灵魂与输入不同……', 320, 75, s.guess ? '#ffb0a0' : '#91ffbb', 'center');
        if (s.inning >= 3) L.text(g, s.delegated ? '藤蔓操作：乔瑟夫决定输入，按确认即可。' : '第三局：按 Q，把手柄交给藤蔓！', 320, 285, '#d5a7ef', 'center');
      });
      if (q.win) { G.flags.baseballDelegated = q.delegated; return q; }
      await S.say('joseph', '他只能读取拿手柄的人。把第三局的输入交给藤蔓！这三局再来一次。');
    }
  }
  async function labyrinth() {
    party(['avdol', 'polnareff', 'iggy'], 'avdol'); await S.setStage('illusion_ch11', { x: 80, y: 160 });
    await S.vs({ key: 'tenoresax', hero: 'avdol', enemy: 'kennyg' }); G.uifx.vsTag(null);
    for (let attempt = 0; ; attempt++) {
      S.mark('ch11_labyrinth');
      const q = { type: 'labyrinth', variant: 0, found: false, hits: 0, wallX: 285, loop: 20,
        touch: { buttons: ['pad', 'j', 'u', 'swap'], captions: { j: '敲墙', u: '调查', swap: '队长' } } };
      W.stage.props = W.stage.props.filter(p => p.id !== 'late_labyrinth');
      const wall = L.pixel(P => {
        const x = q.wallX - G.cam.x, colours = ['#514066', '#3e5269', '#61513d'];
        G.px.rect(P, x - 13, 42, 26, 124, colours[q.variant]);
        for (let y = 46; y < 160; y += 12) G.px.line(P, x - 13, y, x + 12, y, '#201729');
        if (q.found) for (let n = 0; n < q.hits; n++) G.px.line(P, x - 8 + n * 6, 71, x - 5 + n * 4, 142, '#171022', 1, 2);
      }); wall.id = 'late_labyrinth';
      let enemy = null;
      await L.game(S, q, (s, dt) => {
        const p = W.player; L.move(p, dt); if (L.hit('swap')) G.party.next();
        if (p.x > 610 || p.x < 25 || s.t >= s.loop) {
          if (enemy) { enemy.remove = true; enemy = null; }
          p.x = 65; s.variant = (s.variant + 1) % 3; s.wallX = [285, 430, 180][s.variant]; s.found = false; s.hits = 0; s.loop = s.t + 20; S.sfx('sax_melody');
        }
        if (L.hit('special')) {
          if (p.cid === 'avdol' || p.cid === 'iggy') { s.found = true; S.sfx(p.cid === 'iggy' ? 'dog_bark' : 'fire_burst'); }
          else S.hint('波鲁纳雷夫：这里刚才是不是来过？换阿布德尔或伊奇调查。', 2);
        }
        if (s.found && Math.abs(p.x - s.wallX) < 35 && L.hit('attack')) {
          s.hits++; S.sfx(s.hits < 4 ? 'punch' : 'ko_hit'); S.shake(2, .12);
          if (s.hits === 3) { enemy = S.spawn('kennyg', s.wallX, 160, { id: 'late_kennyg', hold: true }); enemy.play('sax'); }
          if (s.hits >= 4) { s.done = true; s.win = true; }
        }
        if (s.t >= 60) { s.done = true; s.win = false; }
      }, null, (g, s) => {
        L.label(g, '次中音萨克斯 · 幻觉走廊', 'Q 换队长，阿布德尔 / 伊奇按 U 指向假墙；靠近 J 敲三次，再击倒本体');
        L.text(g, '剩余 ' + Math.ceil(Math.max(0, 60 - s.t)) + ' 秒', 22, 313, '#ffe174');
        if (s.found) { const p = W.player, x = (s.wallX - G.cam.x) * 2;
          g.strokeStyle = p.cid === 'iggy' ? '#e8c070' : '#ff9d40'; g.lineWidth = 2;
          g.beginPath(); g.moveTo((p.x - G.cam.x) * 2, 310); g.lineTo(x, 303); g.stroke();
          L.text(g, s.hits >= 3 ? '肯尼·G 暴露了！再按 J！' : '假墙 ' + s.hits + ' / 3', x, 250, '#ffe174', 'center'); }
        g.fillStyle = 'rgba(83,25,117,' + (.08 + .25 * s.t / 60) + ')'; g.fillRect(0, 110, 640, 180);
      });
      wall.remove = true;
      W.stage.props = W.stage.props.filter(p => p !== wall);
      if (q.win) { enemy.play('down'); await S.title('saiki'); return; }
      if (enemy) enemy.remove = true;
      await S.say('avdol', '幻觉又把我们送回了原处。只有这段走廊重来。'); W.player.x = 80;
    }
  }
  async function creamHidden() {
    S.mark('ch11_cream_hidden');
    await S.fight({ id: 'b26b_cream', lead: 'polnareff', swap: false, allies: ['iggy'], bench: 'hide', finish: 'none', arena: [12, 308], vs: 'cream',
      waves: [[{ cid: 'vanilla', kit: 'e_vanilla', boss: true, hp: 1200, minHp: 1, x: 270, y: 160 }]],
      onWave(s, n, es, attempt, c) {
        const e = c.boss; e.brain = () => true; e.onHitBy = () => c.data.phase === 'expose' ? null : 'evade'; e.dmgMul = () => 2;
        c.data.phase = 'warn'; c.data.phaseT = 0; c.data.rushes = 0; c.data.sand = 0; c.data.sandNext = 8; c.data.carves = []; c.data.hit = false;
        e.alpha = 0; e.stand.hide();
        W.stage.props = W.stage.props.filter(p => !String(p.id || '').startsWith('late_'));
        L.pixel(P => {
          for (const carve of c.data.carves) G.px.rect(P, carve.x - G.cam.x - 5, carve.y - 4, 10, 9, '#120c19');
          if (c.data.phase === 'warn') for (let i = 0; i < 9; i++) G.px.rect(P, e.x - G.cam.x + (i - 4) * 3, e.y - 2 - i % 3, 1, 1, '#bbad8e');
          if (c.data.sand > 0 || c.data.phase === 'expose') {
            const x = e.x - G.cam.x; G.px.disc(P, x, e.y - 17, 18, '#b99b5b'); G.px.disc(P, x, e.y - 17, 15, '#170e27'); }
        });
        s.insertUI(g => L.hud(g, ['奶油 · 看不见的虚空', '尘土预告冲刺：上下让开，或 K 闪避', '三次冲刺后探头，只有这时打得中',
          c.data.phase === 'expose' ? '探头！伤害 ×2' : c.data.sand > 0 ? '伊奇的沙显出了轮廓！' : '伊奇每八秒撒沙显形']));
      },
      tick(c, dt) {
        const d = c.data, e = c.boss, p = c.player; d.phaseT += dt; d.sand = Math.max(0, d.sand - dt);
        // 虚空阶段保持替身隐藏，探头的可见轮廓由这一场持有。
        e.stand.hide();
        if (c.t >= d.sandNext) { d.sandNext += 8; d.sand = 1.5; G.S.sfx('sand'); }
        if (d.phase === 'expose') { e.alpha = 1; if (d.phaseT >= 40 / 60) { d.phase = 'warn'; d.phaseT = 0; e.alpha = 0; e.stand.hide(); } }
        else if (d.phase === 'warn' && d.phaseT >= 20 / 60) {
          d.phase = 'dash'; d.phaseT = 0; d.hit = false;
          const target = d.rushes % 2 ? G.rand(20, 300) : p.x;
          d.vx = target >= e.x ? 120 : -120; d.targetY = G.clamp(p.y + G.rand(-8, 8), 148, 174);
          G.S.sfx('void_eat');
        } else if (d.phase === 'dash') {
          const x0 = e.x; e.x = G.clamp(e.x + d.vx * dt, 18, 302); e.y += G.clamp(d.targetY - e.y, -35 * dt, 35 * dt);
          if (Math.abs(e.x - (d.lastCarve || 0)) >= 8) { d.carves.push({ x: e.x, y: e.y }); d.lastCarve = e.x; if (d.carves.length > 90) d.carves.shift(); }
          if (!d.hit && p.x >= Math.min(x0, e.x) - 16 && p.x <= Math.max(x0, e.x) + 16 && Math.abs(p.y - e.y) < 13) {
            d.hit = true; L.damage(c, p.maxHp * .4); G.dbg.ev('cream_void_contact', { dmg: p.maxHp * .4 }); }
          if (e.x <= 18 || e.x >= 302 || d.phaseT >= 2.4) { d.rushes++; d.phase = d.rushes % 3 === 0 ? 'expose' : 'warn'; d.phaseT = 0; }
        }
        if (e.hp <= 1) c.end();
      // 看不见的虚空段结束：这一个瓦尼拉（alpha 0、惰性大脑、探头才吃伤害）留在地图上会和下一段新生成的瓦尼拉同时在场
      }, after(s, es) { s.insertUI(null); for (const e of es) e.remove = true; }
    });
  }
  async function creamSun() {
    S.mark('ch11_cream_sun');
    await S.fight({ id: 'b26c_sunlight', lead: 'polnareff', swap: false, allies: ['iggy'], bench: 'hide', finish: 'none', arena: [12, 308],
      waves: [[{ cid: 'vanilla', kit: 'e_vanilla', boss: true, hp: 800, minHp: 1, x: 215, y: 160 }]],
      kitOverride: { polnareff: { special: { name: '阳光飞踢', need: 0, window: c => c.data.beam && Math.abs(c.boss.x - 274) < 40,
        prompt: '他靠近阳光了！按 U 飞踢！', async run(s, p, c) { p.play('kick'); c.boss.x = 274; c.data.sunWin = true; s.sfx('punch_heavy'); s.shake(4, .25); c.end(); } } } },
      onWave(s, n, es, attempt, c) {
        c.data.beam = false; c.data.j3Until = 0; c.data.sunWin = false;
        W.stage.props = W.stage.props.filter(p => !String(p.id || '').startsWith('late_'));
        L.pixel(P => { if (c.data.beam) { G.px.rect(P, 260, 32, 30, 140, '#fff2b9', .35); G.px.rect(P, 270, 32, 8, 140, '#fffbd4', .65); } });
        c.on('hit', ({ t, slot }) => { if (t === c.boss && slot === 'J3') c.data.j3Until = c.t + .35; });
        s.insertUI(g => L.hud(g, ['瓦尼拉·艾斯', c.data.beam ? 'J3 贯穿把他击退进光柱；或靠近阳光时 U 飞踢' : '先逼出他的吸血鬼本性！']));
      },
      tick(c) {
        if (!c.data.beam && !c.data.busy && c.boss.hp <= 400) L.task(c, async () => {
          await G.S.say('polnareff', '腿又复原了……他已经是吸血鬼！');
          await lightSoul('iggy'); G.S.leave('iggy');
          await G.S.say('polnareff', '伊奇——！！'); c.data.beam = true;
          c.boss.x = 238; c.boss.atk = c.boss.tele = null; c.boss.stunT = 1; G.S.sfx('crash');
          G.dbg.ev('cream_sun_open');
        });
        if (c.data.beam && c.t <= c.data.j3Until && Math.abs(c.boss.x - 274) <= 18) { c.data.sunWin = true; c.end(); }
      }, after(s) { s.insertUI(null); }
    });
    S.leave('iggy'); await L.lines(S, [['polnareff', '你那么想变成 DIO 那样的吸血鬼？……那就好好晒晒太阳吧！']]);
    await lightSoul('vanilla'); S.music('sad');
    const v = T.show(S, { bg: 'mansion_hall', draw(g, t) {
      g.fillStyle = '#fff2b92d'; g.fillRect(130, 0, 60, 180);
      T.sprite(g, 'polnareff', 'kneel', 0, 160, 173);
      T.sprite(g, 'avdol', 'idle', 0, 135, 154 - t * 20, { alpha: Math.max(0, 1 - t / 3) });
      T.sprite(g, 'iggy', 'idle', 0, 183, 153 - t * 20, { alpha: Math.max(0, 1 - t / 3) });
    } }); await S.say('polnareff', '阿布德尔……伊奇……'); await S.wait(2); v.close();
  }
  L.ch11 = { baseball, labyrinth, creamHidden, creamSun };
  G.STORY.ch11 = async function () {
    party(all, 'jotaro'); await S.chapterCard('ch11'); await S.setStage('mansion_ext_ch11', { x: 70, y: 160 }); S.mark('ch11_return');
    S.location('dio_mansion');
    await S.narrate('第49天，下午。SPW 的车在馆门口停下。');
    await S.say('kakyoin', '我说过会在这里等你们。'); await S.notice({ who: 'kakyoin', text: '花京院归队。六人的旅途，终于来到馆门口。' });
    const v = T.show(S, { bg: 'black', parts: [{ cid: 'vanilla', anim: 'kneel', x: 160, y: 172, alpha: .25 }] });
    await S.say('vanilla', '为了 DIO 大人，我的一切都可以献出。'); v.close();
    await L.view(S, { bg: 'black' }, .5); S.sfx('drip'); await S.say('dio', '……起来吧，瓦尼拉。');
    await S.until(() => !G.uifx.cards.some(k => k.kind === 'loc')); S.nameCard('vanilla', { y: 24 }); await S.wait(1.2);
    await L.explore(S, 'mansion_ext_ch11', { exitX: 285, hotspots: [
      L.hot('windows', 205, '冰冷的馆', ['life', 'scent'], async s => s.say('jotaro', '……到了。'), async s => s.say(W.player.cid, W.player.cid === 'avdol' ? '里面有好几个生命……还有一个，很冷，像死的一样。' : '伊奇夹着尾巴。气味从门缝一直通向深处。'))
    ], hint: '阿布德尔 / 伊奇按 U 调查；向右进馆。' });
    await S.setStage('corridor_ch11'); const butler = S.spawn('telence', 250, 160, { id: 'butler' });
    S.nameCard('telence', { y: 24 });
    await S.say('telence', '欢迎光临。主人还在休息。'); await S.say('kakyoin', '……画像的眼睛在跟着我们转。');
    party(['jotaro', 'joseph', 'kakyoin'], 'kakyoin');
    await L.view(S, { bg: 'redsea_island', parts: [{ cid: 'telence', x: 240, y: 170, scale: 2 }] }, 1.4);
    S.sfx('glass_break'); S.impact('invert', 2 / 60); await S.setStage('game_ch11');
    await S.say('telence', '这里是游戏室。阿图姆神会问你们的灵魂。');
    await S.vs({ key: 'atum', hero: 'kakyoin', enemy: 'telence' }); G.uifx.vsTag(null);
    S.mark('ch11_fmega'); const race = await L.runner(S, { race: true });
    if (race.leading > .5) await S.say('telence', '……你很厉害。可惜，我看得见你的灵魂。');
    await S.say('kakyoin', '最后一个弯道……他早就知道我要去哪条车道。');
    await L.soul(S, 'kakyoin', true); S.leave('kakyoin'); S.setLeader('jotaro', { force: true });
    await baseball(); await S.say('jotaro', '读得到我的灵魂，读不到老头子的藤蔓。欧拉！');
    await L.view(S, { bg: 'game_room', parts: [{ cid: 'starplat', anim: 'punch', x: 170, y: 170, scale: 2 }, { cid: 'telence', anim: 'hurt', x: 250, y: 150, scale: 2 }] }, .7);
    S.sfx('ko_hit'); await S.title('saiki'); await S.join('kakyoin');
    await labyrinth(); await S.setStage('hall_ch11'); S.mark('ch11_cream_sacrifice');
    S.music('boss');
    const black = T.show(S, { bg: 'mansion_hall', draw(g, t) {
      const x = 30 + t * 80; g.fillStyle = '#100818'; g.beginPath(); g.arc(x, 140, 19, 0, Math.PI * 2); g.fill();
      T.sprite(g, 'avdol', 'push', 0, 195, 170); T.sprite(g, 'polnareff', 'hurt', 0, 228 + Math.min(15, t * 15), 166);
      if (t > 1) { g.fillStyle = '#140d1b'; g.fillRect(192, 50, 22, 121); }
    } }); await S.wait(3); black.close();
    await lightSoul('avdol'); S.leave('avdol'); await S.say('polnareff', '阿布德尔——！！');
    S.standCard('cream', { sfx: 'sting_reveal' }); await S.say('vanilla', '为了 DIO 大人……');
    await creamHidden(); await creamSun();
    party(['jotaro', 'joseph', 'kakyoin', 'polnareff'], 'jotaro', ['avdol', 'iggy']);
    await S.setStage('tower_ch11'); S.mark('ch11_nukesaku');
    S.spawn('nukesaku', 235, 160, { id: 'nukesaku', facing: -1 });
    await S.choice(['搭话', '动手'], '楼梯上背对着的“女人”');
    await S.say('jotaro', '你的脸和身体……是反的！');
    await S.fight({ id: 'b27_nukesaku', lead: 'jotaro', swap: false, bench: 'hide', finish: 'ko',
      waves: [[{ cid: 'nukesaku', kit: 'e_nukesaku', boss: true, hp: 200, x: 235, y: 160 }]] });
    await S.say('nukesaku', '我带路！主人就在棺材里！');
    S.mark('ch11_coffin'); T.prop(S, 'coffin', 160, 163); S.sfx('door');
    await L.view(S, { bg: 'black', draw(g) { g.fillStyle = '#d6bf6f'; g.fillRect(143, 130, 32, 4); g.fillRect(153, 121, 17, 10); } }, 1.7);
    await S.narrate('棺材里只有一顶帽子的空镜。努凯萨克的声音，突然停了。');
    await L.view(S, { bg: 'mansion_exterior', draw(g) { g.fillStyle = '#070817aa'; g.fillRect(0, 0, 320, 180); } }, .8);
    S.music('ominous'); await S.say('dio', '……醒得正好。'); S.mark('ch11_end'); await S.tbc();
  };
})();
