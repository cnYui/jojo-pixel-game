// 盖布按声音而非血条追击；三个预言分别重试，保留喜剧解谜的因果。
'use strict';
(function () {
  const G = window.G, M = G.MID, T = G.TPL, W = G.world, I = G.input;
  const crew = ['jotaro', 'joseph', 'avdol', 'polnareff', 'iggy'];
  const hospitalParty = (S, leader) => {
    S.party([...crew, 'kakyoin'], { leader });
    G.party.get('kakyoin').mem.bandage = true;
    G.party.remove('kakyoin', { look: 'gray' });
  };
  const ring = (S, x, y, r) => S.fx('shockwave', { x, y, squash: .25, r_max: r, dur: .5, colour: '#b8eaff' });
  async function desert(S) {
    hospitalParty(S, 'jotaro'); await M.scene(S, 'desert_ch8', null, 48);
    S.mark('b16a_geb');
    await M.objectFight(S, { id: 'b16a_geb', lead: 'jotaro', swap: false, coverage: false,
      arena: [0, 640], bench: 'hide', music: 'battle',
      testHint: c => ({ distance: c.data.distance, pebble: c.data.pebble, ignore: c.data.ignore }),
      tick(c, dt) {
        const d = c.data, p = c.player, dx = p.x - d.lastX;
        if (dx > 0 && dx < 30) d.distance = Math.max(2000, d.distance - dx * 2);
        d.lastX = p.x; d.quiet = Math.abs(dx) > .05 ? 0 : d.quiet + dt;
        if (p.x > 580) { p.x -= 320; d.lastX = p.x; d.dog.x -= 320; }
        d.dog.x = p.x - 24; d.dog.y = p.y + 3;
        const noise = (x, y, r, delay = 20 / 60) => {
          ring(S, x, y, r);
          if (c.t < d.ignore) return;
          d.sounds.push({ x: G.clamp(x + dx / Math.max(dt, .001) * delay * .5, 8, 632), y, at: c.t + delay });
        };
        M.every(d, 'step', dt, .32, () => { if (Math.abs(dx) > .05) { noise(p.x, p.y, 24); ring(S, d.dog.x, d.dog.y, 12); } });
        if (I.hit('attack')) noise(p.x, p.y, 64);
        if (d.quiet >= 3) { d.quiet = 0; noise(p.x, p.y, 24); }
        if (I.okHit()) {
          I.consumeOk();
          if (d.pebble) { const x = G.clamp(p.x + p.facing * 64, 8, 632); d.pebble = false;
            d.ignore = c.t + 2; ring(S, x, p.y, 48); d.sounds = [{ x, y: p.y, at: c.t + 20 / 60 }]; S.sfx('pop'); }
          else if (d.stones.some(x => Math.abs(x - p.x) < 26)) { d.pebble = true; S.word('石子', p); }
        }
        for (const n of d.sounds.filter(n => n.at <= c.t)) {
          c.hazard({ shape: 'ellipse', x: n.x, y: n.y, rx: 18, ry: 10, warn: 20 / 60, dur: .18,
            dmg: 20, once: true, guard: 'none', fxActive: 'geb_claw', sfx: 'water_jet' });
        }
        d.sounds = d.sounds.filter(n => n.at > c.t);
        if (d.distance <= 2000) c.end();
      }
    }, c => {
      c.player.x = 48; c.player.y = 163;
      Object.assign(c.data, { distance: 4000, lastX: 48, quiet: 0, ignore: 0, pebble: false, sounds: [], stones: [80, 240, 400, 560] });
      c.data.dog = c.spawn({ cid: 'iggy', x: 24, y: 166, team: 'npc', hold: true, untargetable: true });
      for (const x of c.data.stones) c.spawn({ cid: 'prop:rock', x, y: 166, team: 'object', untargetable: true });
      M.ui(S, g => M.hud(g, ['恩多尔距离 ' + Math.ceil(c.data.distance) + ' 米',
        c.data.pebble ? 'E 扔出石子，水爪会去打它' : '向右走；脚步声会引来水爪，K 闪；石头旁 E 捡石子']));
    });
  }
  async function glide(S) {
    await M.scene(S, 'glide_ch8', null, 110, 'jotaro'); S.mark('b16b_geb');
    await S.say('jotaro', '愚者变成滑翔翼……走！');
    const oldHold = S.player.hold;
    try {
      await M.objectFight(S, { id: 'b16b_geb', lead: 'jotaro', swap: false, coverage: false,
        bench: 'hide', music: 'battle',
        testHint: c => ({ distance: c.data.distance, height: c.data.height, columns: c.data.columns }),
        tick(c, dt) {
          const d = c.data, p = c.player; p.hold = true; p.x = 110;
          d.height = G.clamp(d.height + ((I.isDown('down') ? 1 : 0) - (I.isDown('up') ? 1 : 0)) * 74 * dt, 50, 144);
          // float 是落水半露头的动作（只露帽子和上半张脸），滑翔时吊在愚者下面要整个人
          p.y = d.height + 18; p.z = 0; p.play('idle'); d.wing.x = p.x; d.wing.y = d.height;
          d.distance = Math.max(0, d.distance - 200 * dt); d.scroll += 200 * dt;
          // 计时键不能叫 wing：d.wing 是滑翔翼（愚者）本体，M.every 会把它累加成字符串，下一帧 d.wing.x 就抛错、整段卡死
          M.every(d, 'wingT', dt, 2, () => { ring(S, p.x, 162, 14); d.columns.push({ x: p.x + 110, at: c.t, top: d.height - 8 }); S.sfx('sand_storm'); });
          for (const col of d.columns) {
            col.x -= 180 * dt;
            if (c.t - col.at > 40 / 60 && !col.fired) { col.fired = true; S.sfx('water_jet'); }
            if (col.fired && !col.hit && Math.abs(col.x - p.x) < 13 && d.height > col.top - 10) { col.hit = true; M.damage(c, 16); }
          }
          d.columns = d.columns.filter(col => col.x > -20);
          if (d.distance <= 0) c.end();
        }
      }, c => {
        Object.assign(c.data, { distance: 2000, height: 90, scroll: 0, columns: [] }); c.player.hold = true;
        c.data.wing = c.spawn({ cid: 'fool', x: 110, y: 90, team: 'npc', hold: true, untargetable: true, idleAnim: 'glide' });
        M.pixel('glide_water', P => {
          const d = c.data;
          for (let i = 0; i < 12; i++) { const x = (i * 31 - d.scroll % 31 + 320) % 320; G.px.line(P, x, 168, x + 14, 167, '#d9b474', 1); }
          for (const col of d.columns) {
            const x = col.x - G.cam.x;
            if (!col.fired) G.px.ellipse(P, x - 12, 160, x + 12, 167, '#a4efff', null, 1, .8);
            else G.FX.geb_column(P, x, 170, G.clk.world, G.clk.world - .12, { top: col.top });
          }
        });
        M.ui(S, g => M.hud(g, ['距离 ' + Math.ceil(c.data.distance) + ' 米', '↑↓ 改变高度，飞到水柱顶上']));
      });
    } finally { S.player.hold = oldHold; }
    await S.press({ key: 'special', window: 1, label: 'U——把伊奇扔出去！', failOk: true });
    S.sfx('dog_bark'); await M.scene(S, 'desert_ch8', null, 180);
    const n = S.spawn('ndoul', 234, 164, { team: 'npc' }); n.play('idle');
    await S.walk('player', 210, 164, { speed: 260 }); G.fx.hit(231, 135, 'heavy'); S.sfx('punch_heavy'); n.play('down');
    await M.lines(S, [['ndoul', '九荣神……还有八个……'], ['jotaro', '……到此为止了。']]);
    const black = T.show(S, { bg: 'black' }); S.sfx('water_jet'); await S.wait(1.2); black.close();
    await S.say('jotaro', '……他自己选了结局。');
    const grave = T.show(S, { bg: 'desert_night', parts: [{ cid: 'prop:cane', x: 170, y: 158 }] });
    await S.wait(2); grave.close();
  }
  async function prophecy(S) {
    hospitalParty(S, 'iggy'); S.leadable('jotaro', false, { look: 'gray', msg: '承太郎去买东西了。' });
    G.party.get('jotaro').mem.away = true;
    for (const cid of ['joseph', 'avdol']) S.leadable(cid, false, { msg: '这次由伊奇和波鲁纳雷夫行动。' });
    await M.scene(S, 'aswan_ch8', st => {
      st.npcs = [M.npc('npc_merchant', 'orange_seller', 220, '小贩', '橘子！又甜又便宜！'),
        M.npc('npc_townsfolk', 'pedestrian', 410, '路人', '前面的茶摊能歇脚。'),
        M.npc('oingo', 'fake_jotaro', 660, '承太郎？', '……呀、呀嘞呀嘞。'),
        M.npc('boingo', 'boingo', 850, '看漫画的男孩', '……预、预言是绝对的。')];
      st.hotspots = [M.hot('fake_scent', 660, '奇怪的气味', ['scent', 'detail'], '他的味道不对。', null,
        async s => { s.sfx('dog_bark', { n: 3 }); await s.say(null, '（伊奇朝假承太郎狂叫。）'); }), M.exit('prophecy', 930, '茶摊', 'ch8Tea')];
    }, 60, 'iggy');
    M.prop(S, 'manga', 850); M.prop(S, 'orange', 220);
    await M.explore(S, 'ch8Tea', 'E 搭话；伊奇 U 闻出假承太郎；到最右茶摊 E。');
    for (let phase = 1; phase <= 3; phase++) {
      S.mark('b17_prophecy' + phase);
      const text = phase === 1 ? '有人喝下了下毒的茶！' : phase === 2 ? '一辆马车撞上了承太郎！' : '橘子在承太郎脸上爆炸！';
      const comic = T.show(S, { bg: 'black', parts: [{ cid: 'prop:manga', x: 160, y: 110, scale: 3 }],
        draw(g) {
          for (let i = 0; i < 3; i++) {
            const x = 52 + i * 72, y = 48;
            g.fillStyle = '#fff4ce'; g.fillRect(x, y, 68, 56);
            g.strokeStyle = '#20152b'; g.lineWidth = 2; g.strokeRect(x, y, 68, 56);
            G.atlas(i === 2 ? 'oingo' : 'jotaro').draw(g, 'idle', 0, x + 40, y + 51);
            G.propAtlas(phase === 1 ? 'tea_cup' : phase === 2 ? 'cart' : 'orange').draw(g, 'idle', 0, x + 18, y + 45);
            if (i === 2) { g.fillStyle = '#d8343e'; g.fillRect(x + 45, y + 13, 3, 15); g.fillRect(x + 45, y + 31, 3, 3); }
          }
        } });
      const priorUI = G.ui.insertUI;
      S.insertUI((g) => {
        for (let i = 0; i < 3; i++) M.text(g, ['危险靠近', '预言兑现', '命运拐弯'][i], 110 + i * 144, 105, '#20152b');
        M.text(g, text, 104, 225); M.text(g, '托特神：三个画格，三十秒改变结局。', 104, 246);
      });
      const captions = G.ui.insertUI;
      try { await S.wait(2.5); } finally { comic.close(); if (G.ui.insertUI === captions) G.ui.insertUI = priorUI; }
      await S.say('boingo', text);
      await M.objectFight(S, { id: 'b17_prophecy' + phase, lead: phase === 1 ? 'iggy' : 'polnareff', swap: true,
        allies: ['iggy', 'polnareff'], bench: 'hide', coverage: false, arena: [0, 960], music: 'daily',
        testHint: c => ({ phase, orange: c.data.orange, left: 30 - c.t, solved: c.data.solved }),
        tick(c) {
          const d = c.data, p = c.player;
          if (I.okHit()) { I.consumeOk();
            if (phase === 1 && p.cid === 'iggy' && (Math.abs(p.x - 250) < 30 || Math.abs(p.x - 410) < 30)) { d.solved = true; S.sfx('splash'); S.word('搅局成功！', p); }
            if (phase === 2 && p.cid === 'polnareff' && Math.abs(p.x - 490) < 30) { d.solved = true; S.sfx('slash'); S.word('割断缰绳！', p); }
            if (phase === 3) {
              if (!d.orange && Math.abs(p.x - 230) < 30) { d.orange = true; S.word('拿起橘子', p); }
              else if (d.orange && Math.abs(p.x - 690) < 32) { d.solved = true; S.sfx('explosion'); S.fx('explosion', { x: 690, y: 133 }); }
            }
          }
          if (d.solved) c.end();
          else if (c.t >= 30) c.fail(phase === 1 ? '毒茶喷了一脸……从这一格漫画重来。' : phase === 2 ? '马车撞飞了你……从这一格漫画重来。' : '橘子爆了！……从这一格漫画重来。');
        }
      }, c => {
        Object.assign(c.data, { orange: false, solved: false }); c.player.x = 140; c.player.y = 162;
        const fake = c.spawn({ cid: 'oingo', x: 690, y: 162, team: 'npc', hold: true, untargetable: true }); fake.play('idle');
        for (const [id, x] of phase === 1 ? [['tea_cup', 250], ['cake', 410]] : phase === 2 ? [['cart', 490]] : [['orange', 230]])
          c.spawn({ cid: 'prop:' + id, x, y: 164, team: 'object', untargetable: true });
        M.ui(S, g => {
          M.hud(g, ['托特预言：' + text + '　' + Math.ceil(Math.max(0, 30 - c.t)) + ' 秒',
            phase === 1 ? '伊奇：到茶杯 / 蛋糕旁按 E 搅局（Q 换人）' : phase === 2 ? '波鲁纳雷夫：到马车旁按 E 割缰绳' : c.data.orange ? '把橘子递给右边的假承太郎：E' : '左边拿起橘子（E），递给右边的假承太郎']);
          G.atlas('prop:manga').draw(g, 'idle', 0, 600, 120, { scale: 2 });
        });
      });
    }
    // 最后一个预言兑现：橘子在“承太郎”脸上爆炸——炸的是奥因哥自己（oingo boom）
    hospitalParty(S, 'jotaro');
    const og = S.spawn('oingo', S.player.x + 44, 162, { id: 'oingo_boom', team: 'npc', facing: -1 });
    og.play('boom'); S.sfx('explosion'); S.fx('explosion', { x: og.x, y: 136, size: 20 });
    await M.lines(S, [['oingo', '预言……为什么总是落到我头上？！'], ['boingo', '绝、绝对会应验的……'], ['jotaro', '……你们在干什么。']]);
    og.remove = true;
  }
  G.STORY.ch8 = async S => {
    await M.ensureBg('_ch8');
    S.party([...M.crew, 'avdol'], { leader: 'joseph' });
    await M.scene(S, 'coast_ch8', st => {
      st.npcs = [M.npc('npc_spw', 'pilot', 200, 'SPW 驾驶员', '这只狗……很难搞。祝你们好运。')];
      st.hotspots = [M.hot('gum', 110, '咖啡味口香糖', ['nensha', 'scent'], '伊奇爱吃这个。', async (s, h, p) => {
        if (p.cid !== 'joseph') return s.say(p.cid, '乔瑟夫拿口香糖试试。'); s.flags.ch8Gum = true;
      }), M.hot('heli', 275, '直升机', ['detail', 'nensha', 'life'], 'SPW 财团的直升机。')];
    }, 55); await S.chapterCard('ch8');
    M.prop(S, 'gum', 110); M.prop(S, 'heli', 275); const dog = S.spawn('iggy', 145, 164, { team: 'npc' });
    await S.say('polnareff', '哇！别扯我的头发！'); S.sfx('dog_bark'); dog.play('idle');
    await M.explore(S, 'ch8Gum', '乔瑟夫到口香糖旁 E 收买伊奇；Q 换队长。');
    // 入队的是队伍里的伊奇（另一个 Actor）：先撤掉海滩上那只 NPC，在它的位置入队，不然会有两只伊奇
    const dogAt = { x: dog.x, y: dog.y }; dog.remove = true;
    await S.join('iggy', { notice: true, x: dogAt.x, y: dogAt.y });
    await S.notice({ title: '埃及九荣神', text: 'DIO 最后的刺客，以埃及九位神明为名。' });
    await M.scene(S, 'desert_ch8', null, 48, 'jotaro'); S.sfx('water_jet'); S.sfx('crash'); S.shake(6, .6);
    await M.lines(S, [[null, '直升机落入沙中。……来不及了。'], ['kakyoin', '……看不见了。'], ['avdol', '水听见了手镯，却没有上当……'], ['polnareff', '腿……承太郎，小心！'], ['ndoul', '声音，已经告诉了我一切。']]);
    await desert(S); await glide(S);
    await S.say('kakyoin', '我会回来的。……在 DIO 的馆门口等我。');
    // 去科翁坡的地图放在第9章开头（第9章本来就从这段路开始，这里不重复）
    await prophecy(S); await M.end(S, 'ch8_complete');
  };
})();
